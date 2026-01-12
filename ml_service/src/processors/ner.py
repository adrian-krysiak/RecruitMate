import csv
from pathlib import Path
import pickle
from typing import List, Set, Dict, Tuple

from spacy.language import Language
from spacy.tokens import Doc
from spacy.symbols import ORTH

from src.config import SECTION_WEIGHTS, NER_SKILLS_DATA_PATH


class NERProcessor:
    """
    Processor responsible for Named Entity Recognition and Gap Analysis.
    """

    def __init__(self, nlp: Language):
        self.nlp = nlp
        self.uri_to_canonical: Dict[str, str] = {}
        self.label_to_canonical: Dict[str, str] = {}
        self._setup_entity_ruler()

    def _setup_entity_ruler(self):
        """
        Configures the EntityRuler with patterns.
        """
        if "entity_ruler" not in self.nlp.pipe_names:
            ruler = self.nlp.add_pipe("entity_ruler", before="parser")
        else:
            ruler = self.nlp.get_pipe("entity_ruler")
            ruler.clear()

        patterns = self._get_mvp_patterns()
        ruler.add_patterns(patterns)

    def analyze(self, job_doc: Doc, cv_sec_docs: Dict[str, Doc]
                ) -> Tuple[float, List[str], List[str]]:
        """
        Performs the Gap Analysis and calculates the Weighted Keyword Score.
        """
        job_skills = self._extract_skills(job_doc)

        if not job_skills:
            return 0.0, [], []

        cv_skill_weights: Dict[str, float] = {}

        for section, doc in cv_sec_docs.items():
            if not doc or not doc.text.strip():
                continue

            section_weight = SECTION_WEIGHTS.get(section, 0.5)
            skills_in_section = self._extract_skills(doc)
            for skill in skills_in_section:
                current_max = cv_skill_weights.get(skill, 0.0)
                cv_skill_weights[skill] = max(current_max, section_weight)

        common_keywords = []
        missing_keywords = []
        total_score = 0.0

        for required_skill in job_skills:
            if required_skill in cv_skill_weights:
                total_score += cv_skill_weights[required_skill]
                common_keywords.append(required_skill)
            else:
                missing_keywords.append(required_skill)

        final_score = total_score / len(job_skills)
        return round(final_score, 4), common_keywords, missing_keywords

    def _extract_skills(self, doc: Doc) -> List[str]:
        """
        Returns unique SKILL entities (lowercase).
        """
        if not doc.text.strip():
            return []

        skills: Set[str] = set()
        uri_to_canonical = self.uri_to_canonical
        label_to_canonical = self.label_to_canonical

        for ent in doc.ents:
            if ent.label_ != "SKILL":
                continue
            lower_text = ent.text.lower()
            skill_id = ent.ent_id_ or lower_text
            canonical = (
                uri_to_canonical.get(skill_id)
                or label_to_canonical.get(lower_text)
                or lower_text
            )
            skills.add(canonical)

        return sorted(skills)

    def _get_mvp_patterns(self) -> List[Dict]:
        """
        Load patterns from processed file or create from raw CSVs.
        """
        processed_path = Path(NER_SKILLS_DATA_PATH['processed'])

        if processed_path.exists():
            with processed_path.open('rb') as f:
                stored = pickle.load(f)

            if isinstance(stored, dict):
                self.uri_to_canonical = stored.get('canonical', {})
                self.label_to_canonical = stored.get('label_to_canonical', {})
                patterns = stored.get('patterns', [])
            else:
                # backward compatibility with old pickle storing only patterns list
                self.uri_to_canonical = {}
                self.label_to_canonical = {}
                patterns = stored

            # ensure tokenizer special-cases are always added, even when loading from cache
            self._add_special_cases_for_patterns(patterns)
            return patterns

        raw_eu_path = Path(NER_SKILLS_DATA_PATH['raw_eu'])
        raw_addon_path = Path(NER_SKILLS_DATA_PATH['raw_add'])

        patterns = []

        if raw_eu_path.exists():
            patterns.extend(self._load_patterns_from_csv(raw_eu_path))

        if raw_addon_path.exists():
            patterns.extend(self._load_patterns_from_csv(raw_addon_path))

        if patterns:
            try:
                processed_path.parent.mkdir(parents=True, exist_ok=True)
                with processed_path.open('wb') as f:
                    pickle.dump({
                        "patterns": patterns,
                        "canonical": self.uri_to_canonical,
                        "label_to_canonical": self.label_to_canonical
                    }, f)
            except Exception as e:
                print(f"Warning: Could not save processed patterns: {e}")

        return patterns

    def _load_patterns_from_csv(self, csv_path: Path) -> List[Dict]:
        """
        Load and deduplicate patterns from a single CSV file.
        Uses spaCy tokenization for pattern creation (fixes c++, .NET, etc.)
        """
        patterns = []
        skill_labels: Dict[str, Set[str]] = {}

        with csv_path.open(newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)

            for row in reader:
                uri = row.get('conceptUri', '').strip()
                if not uri:
                    continue

                labels = set()

                pref = row.get('preferredLabel', '').strip()
                if pref:
                    labels.add(pref)
                    # track canonical preferred label per concept
                    self.uri_to_canonical.setdefault(uri, pref.lower())

                alt_text = row.get('altLabels', '')
                if alt_text:
                    labels.update(label.strip()
                                  for label in alt_text.split('\n') if label.strip())

                hid_text = row.get('hiddenLabels', '')
                if hid_text:
                    labels.update(label.strip()
                                  for label in hid_text.split('\n') if label.strip())

                if uri not in skill_labels:
                    skill_labels[uri] = set()
                skill_labels[uri].update(labels)

        seen_patterns = set()

        for uri, labels in skill_labels.items():
            for label in labels:
                normalized = ' '.join(label.lower().split())
                if uri in self.uri_to_canonical and normalized:
                    self.label_to_canonical.setdefault(
                        normalized, self.uri_to_canonical[uri])

                if not normalized or normalized in seen_patterns:
                    continue

                seen_patterns.add(normalized)

                doc = self.nlp.make_doc(normalized)
                token_pattern = [{"LOWER": token.text} for token in doc]

                patterns.append({
                    "label": "SKILL",
                    "pattern": token_pattern,
                    "id": uri
                })

        return patterns

    def _add_special_cases_for_patterns(self, patterns: List[Dict]) -> None:
        """Ensure tokenizer keeps special-token skills
        (c++, .net, node.js, etc.) as single tokens."""
        for pat in patterns:
            # each token in pattern has LOWER;
            # reconstruct raw by joining with spaces
            raw_label = " ".join(tok.get("LOWER", "")
                                 for tok in pat.get("pattern", []))
            if any(ch in raw_label for ch in ['+', '.', '#', '/']):
                if raw_label:
                    self.nlp.tokenizer.add_special_case(
                        raw_label, [{ORTH: raw_label}])
