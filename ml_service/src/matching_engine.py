import numpy as np
import spacy
from typing import List, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer

from src.config import SBERT_MODEL_NAME, SPACY_MODEL_NAME
from src.data_models import MatchResponse, MatchDetail, MatchRequest
from src.utils import chunk_text, lemmatize_text, get_match_status


class HybridMatchEngine:
    """
    Core engine for the hybrid CV-Job Offer matching system.
    It encapsulates the SBERT and TF-IDF logic,
    maintaining loaded models in memory.
    """

    def __init__(self):
        print("Initializing the Hybrid Match Engine")

        try:
            self.nlp = spacy.load(SPACY_MODEL_NAME)
        except OSError:
            raise RuntimeError(
                f"Could not find the spaCy model named {SPACY_MODEL_NAME}")

        try:
            self.sbert = SentenceTransformer(SBERT_MODEL_NAME)
        except Exception:
            raise RuntimeError(
                f"Could not load the SBERT model named {SBERT_MODEL_NAME}")

        try:
            self.tfidf = TfidfVectorizer(stop_words='english')
        except Exception:
            raise RuntimeError("Could not initialize the TF-IDF Vectorizer")

        print("The engine is initialized and ready to use")

    def calculate_match(self, request: MatchRequest) -> MatchResponse:
        """
        Calculates the hybrid match score between a job offer and a CV
        by orchestrating semantic (SBERT) and keyword (TF-IDF) matching.
        """

        job = request.job_description
        cv = request.cv_text
        alpha = request.alpha

        # 1. Pre-processing and Guard Clause
        job_chunks = chunk_text(job, self.nlp)
        cv_chunks = chunk_text(cv, self.nlp)

        if not job_chunks or not cv_chunks:
            return MatchResponse(
                final_score=0.0, sbert_score=0.0, tfidf_score=0.0,
                common_keywords=[], details=[]
            )

        # 2. Get Scores from Helper Methods
        sbert_score, details = self._get_semantic_match(job_chunks, cv_chunks)
        tfidf_score, common_keywords = self._get_keyword_match(job, cv)

        # 3. Calculate Final Weighted Score
        final_score = (alpha * sbert_score) + ((1 - alpha) * tfidf_score)

        return MatchResponse(
            final_score=round(final_score, 4),
            sbert_score=round(sbert_score, 4),
            tfidf_score=round(tfidf_score, 4),
            common_keywords=common_keywords,
            details=details
        )

    def _get_semantic_match(self, job_chunks: List[str], cv_chunks: List[str]
                            ) -> Tuple[float, List[MatchDetail]]:
        """
        Helper: Uses SBERT to find the best semantic match
        for each job requirement.
        """

        job_emb = self.sbert.encode(job_chunks)
        cv_emb = self.sbert.encode(cv_chunks)

        sim_matrix = cosine_similarity(job_emb, cv_emb)

        details = []
        max_scores = []

        for i, req in enumerate(job_chunks):
            # Find the best matching CV chunk for this specific job requirement
            row = sim_matrix[i]
            best_idx = np.argmax(row)
            max_score = float(row[best_idx])

            max_scores.append(max_score)
            details.append(MatchDetail(
                requirement_chunk=req,
                best_match_cv_chunk=cv_chunks[best_idx],
                score=round(max_score, 4),
                status=get_match_status(max_score)
            ))

        sbert_score = float(np.mean(max_scores)) if max_scores else 0.0
        return sbert_score, details

    def _get_keyword_match(self, job: str, cv: str) -> Tuple[float, List[str]]:
        """
        Helper: Uses TF-IDF to calculate overall keyword similarity and extract
        common terms.
        """

        clean_job = lemmatize_text(job, self.nlp)
        clean_cv = lemmatize_text(cv, self.nlp)

        try:
            tfidf_matrix = self.tfidf.fit_transform([clean_job, clean_cv])
            # Calculate cosine similarity between the two documents
            score = float(cosine_similarity(tfidf_matrix[0:1],
                                            tfidf_matrix[1:2])[0][0])

            # Extract common keywords
            feature_names = np.array(self.tfidf.get_feature_names_out())
            # Multiply vectors to find non-zero overlapping terms
            job_vec = np.array(tfidf_matrix[0].todense()).flatten()
            cv_vec = np.array(tfidf_matrix[1].todense()).flatten()

            common_mask = job_vec * cv_vec
            sorted_indices = common_mask.argsort()[::-1]

            # Select top 10 keywords where overlap > 0
            top_indices = [idx for idx in sorted_indices
                           if common_mask[idx] > 0][:10]
            common_keywords = feature_names[top_indices].tolist()

            return score, common_keywords

        except ValueError:
            # Handle cases where documents might be empty after cleaning
            return 0.0, []
