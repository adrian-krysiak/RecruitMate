import csv
from pathlib import Path
import pickle
from typing import List, Set, Dict, Tuple

import spacy
from spacy.language import Language
from spacy.tokens import Doc

from src.config import SECTION_WEIGHTS, NER_SKILLS_DATA_PATH


class NERProcessor:
    """
    Processor responsible for Named Entity Recognition and Gap Analysis.
    """

    def __init__(self, nlp: Language):
        self.nlp = nlp
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

            section_weight = SECTION_WEIGHTS.get(section, 0.1)
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
        print('common_keywords:', common_keywords)
        print('missing_keywords:', missing_keywords)
        print('final_score:', final_score)

        return round(final_score, 4), common_keywords, missing_keywords

    def _extract_skills(self, doc: Doc) -> List[str]:
        """
        Returns unique SKILL entities (lowercase).
        """
        if not doc.text.strip():
            return []

        skills = {ent.text.lower() for ent in doc.ents if ent.label_ == "SKILL"}
        return list(skills)

    def _get_mvp_patterns(self) -> List[Dict]:
        """
        Load patterns from processed file or create from raw CSVs.
        """
        processed_path = Path(NER_SKILLS_DATA_PATH['processed'])

        if processed_path.exists():
            with processed_path.open('rb') as f:
                return pickle.load(f)

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
                    pickle.dump(patterns, f)
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

                alt_text = row.get('altLabels', '')
                if alt_text:
                    labels.update(label.strip() for label in alt_text.split('\n') if label.strip())

                hid_text = row.get('hiddenLabels', '')
                if hid_text:
                    labels.update(label.strip() for label in hid_text.split('\n') if label.strip())

                if uri not in skill_labels:
                    skill_labels[uri] = set()
                skill_labels[uri].update(labels)

        seen_patterns = set()

        for uri, labels in skill_labels.items():
            for label in labels:
                normalized = ' '.join(label.lower().split())

                if not normalized or normalized in seen_patterns:
                    continue

                seen_patterns.add(normalized)

                # ✅ FIX: Use spaCy tokenization instead of .split()
                doc = self.nlp.make_doc(normalized)
                token_pattern = [{"LOWER": token.text} for token in doc]

                patterns.append({
                    "label": "SKILL",
                    "pattern": token_pattern,
                    "id": uri
                })

        return patterns
