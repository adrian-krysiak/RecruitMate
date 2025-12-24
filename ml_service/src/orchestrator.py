from typing import Dict, List

import spacy
from spacy.tokens import Doc
from sentence_transformers import SentenceTransformer

from src.config import SPACY_MODEL_NAME, SBERT_MODEL_NAME
from src.data_models import MatchRequest, MatchResponse
from src.parsers import CVParser, JobOfferParser

# Import our specialized processors
from src.processors.ner import NERProcessor
from src.processors.semantic import SemanticProcessor
from src.processors.fallback_tfidf import FallbackProcessor


class HybridMatchEngine:
    """
    The Orchestrator.
    It manages the lifecycle of heavy AI models and coordinates the data flow
    between Parsers, Processors, and the final Scoring Logic.
    """

    def __init__(self):
        print("🚀 Initializing Hybrid Match Engine...")

        # 1. Load Shared Models
        # Load Spacy once and pass it to all processors to save RAM
        print(f"⏳ Loading Spacy ({SPACY_MODEL_NAME})...")
        try:
            # Explicitly disable 'ner' here because we will inject our own EntityRuler
            # in the NERProcessor. Tagger/parser are needed for Action Verbs & Chunking.
            self.nlp = spacy.load(SPACY_MODEL_NAME, disable=["ner"])
        except OSError:
            print(
                f"❌ Spacy model '{SPACY_MODEL_NAME}' not found. Downloading...")
            from spacy.cli import download
            download(SPACY_MODEL_NAME)
            self.nlp = spacy.load(SPACY_MODEL_NAME, disable=["ner"])

        print(f"⏳ Loading SBERT ({SBERT_MODEL_NAME})...")
        self.sbert = SentenceTransformer(SBERT_MODEL_NAME)

        # 2. Initialize Parsers
        self.cv_parser = CVParser()
        self.job_parser = JobOfferParser()

        # 3. Initialize Processors (Dependency Injection)
        print("⚙️  Configuring Processors...")
        self.ner_processor = NERProcessor(self.nlp)
        self.semantic_processor = SemanticProcessor(self.nlp, self.sbert)
        self.fallback_processor = FallbackProcessor(self.nlp)

        print("✅ Engine Ready.")

    def calculate_match(self, request: MatchRequest) -> MatchResponse:
        """
        Main pipeline execution:
        Raw Text -> Parsed Sections -> AI Analysis -> Weighted Scoring -> Response
        """
        # --- STEP 1: PARSING ---
        cv_sections = self.cv_parser.parse(request.cv_text)
        job_data = self.job_parser.parse(request.job_description)

        # Prepare text representations
        # CV: Join valuable sections for NER
        cv_full_text = " ".join(
            [txt for sec, txt in cv_sections.items()])

        # Job: Use extracted "Signal" (Requirements + Responsibilities + Education + Uncategorized)
        job_signal_text = " ".join(
            [txt for sec, txt in job_data.items()])

        if not job_signal_text:
            # Fallback if parser found nothing (e.g. very unstructured text)
            job_signal_text = request.job_description

        # --- STEP 2: PROCESSORS EXECUTION ---

        # A. PRE-PROCESSING
        job_doc = self.nlp(job_signal_text)
        cv_sec_docs: Dict[str, Doc] = {sec: self.nlp(txt) for sec, txt in cv_sections.items()}

        # B. NER & Gap Analysis (Keywords)
        keyword_score, common_keywords, missing_keywords = self.ner_processor.analyze(
            job_doc, cv_sec_docs
        )

        # C. Semantic Analysis (SBERT + Weighted Sections)
        semantic_score, details, section_breakdown = self.semantic_processor.analyze(
            job_doc, cv_sec_docs
        )

        # D. Action Verbs (Style/Tone)
        # Analyze only narrative sections (Experience, Projects)
        narrative_docs = [cv_sec_docs.get('experience'), cv_sec_docs.get('projects')]
        narrative_docs = [d for d in narrative_docs if d is not None]
        action_verb_score = self._analyze_action_verbs(narrative_docs)

        # --- STEP 3: FALLBACK MECHANISM ---
        # If the main models failed to find ANY signal (e.g. language mismatch, empty intersection),
        # we calculate TF-IDF to avoid returning a flat 0.0 which frustrates users.

        if keyword_score == 0.0 and not missing_keywords:
            # Run fallback only when necessary to save compute time,
            # OR run always if need to log it. Here we use it to boost score.
            fallback_score, fallback_keywords = self.fallback_processor.analyze(
                job_doc, self.nlp(cv_full_text)
            )
            # Boost keywords score slightly using statistical similarity
            keyword_score = max(keyword_score, fallback_score)

            # If NER failed completely but TF-IDF found common words, grab top 5
            if not common_keywords and fallback_keywords:
                common_keywords = fallback_keywords[:5]

        # --- STEP 4: FINAL SCORING CALCULATION ---

        # 1. Base Score: Weighted average of Semantic (Context) and Keyword (Hard Skills)
        # Alpha determines the balance (default 0.7 = 70% Semantic)
        base_score = (request.alpha * semantic_score) + \
            ((1.0 - request.alpha) * keyword_score)

        # 2. Style Bonus: Action Verbs
        # We allow a small bonus (max +5%) for good writing style, but we don't penalize heavily.
        # We treat action_verb_score (0.0-1.0) as a factor.
        style_bonus = action_verb_score * 0.05

        final_score = base_score * 0.95 + style_bonus

        # Clamp final result to 0.0 - 1.0
        final_score = max(0.0, min(final_score, 1.0))

        return MatchResponse(
            final_score=round(final_score, 4),

            # Sub-scores
            semantic_score=round(semantic_score, 4),
            keyword_score=round(keyword_score, 4),
            action_verb_score=round(action_verb_score, 4),

            # Insights
            common_keywords=common_keywords,
            missing_keywords=missing_keywords,

            # Breakdown
            section_scores=section_breakdown,
            details=details
        )

    def _analyze_action_verbs(self, docs: List[Doc]) -> float:
        """
        Calculates the ratio of 'strong action verbs' to total verbs.
        Uses the shared NLP pipeline (tagger).
        """
        if not docs:
            return 0.0

        total_verbs = 0
        action_verbs = 0

        # A small list of strong action roots (could be moved to config/utils)
        strong_roots = {
            "lead", "manage", "create", "develop", "design", "implement",
            "optimize", "build", "achieve", "solve", "launch", "orchestrate",
            "spearhead", "drive", "deliver", "execute"
        }
        for doc in docs:
            if not doc or not doc.text.strip():
                continue
            for token in doc:
                if token.pos_ == "VERB":
                    total_verbs += 1
                    # Check for strong lemma OR active dependency roles (nsubj)
                    # 'nsubj' implies the candidate is the doer of the action.
                    if token.lemma_.lower() in strong_roots:
                        action_verbs += 1
                    elif any(child.dep_ == "nsubj" for child in token.children):
                        # Simple heuristic: if the verb has a subject, it's likely active voice
                        action_verbs += 1

        if total_verbs == 0:
            return 0.0

        return action_verbs / total_verbs
