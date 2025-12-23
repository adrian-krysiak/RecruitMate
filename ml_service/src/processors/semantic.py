from typing import List, Dict, Tuple, Any

from spacy.language import Language
from sentence_transformers import SentenceTransformer, util
import torch

from src.config import SECTION_WEIGHTS
from src.data_models import MatchDetail


class SemanticProcessor:
    """
    Processor responsible for Contextual Semantic Matching using SBERT.
    It compares chunks of the Job Description against CV sections, applying weights
    via efficient matrix operations.
    """

    def __init__(self, nlp: Language, sbert_model: SentenceTransformer):
        """
        Initializes the processor with pre-loaded models injected from the Orchestrator.
        """
        self.nlp = nlp
        self.model = sbert_model

    def analyze(self, job_text: str, cv_sections: Dict[str, str]
                ) -> Tuple[float, List[MatchDetail], Dict[str, float]]:
        """
        Main entry point for semantic analysis.
        Orchestrates chunking, encoding, matrix calculation, and statistics.
        """

        # 1. Prepare Job Data (Signal)
        job_chunks = self._chunk_text(job_text)
        if not job_chunks:
            return 0.0, [], {}

        job_embeddings = self.model.encode(job_chunks, convert_to_tensor=True)

        # 2. Prepare CV Data (flattened chunks with metadata)
        cv_chunks_data, cv_weights = self._prepare_cv_data(cv_sections)

        if not cv_chunks_data:
            return 0.0, [], {}

        cv_texts = [item["text"] for item in cv_chunks_data]
        cv_embeddings = self.model.encode(cv_texts, convert_to_tensor=True)

        # 3. Core Matrix Calculation (Vectorized)
        details, total_weighted_score, raw_scores_map = self._compute_weighted_matches(
            job_embeddings, cv_embeddings, job_chunks, cv_chunks_data, cv_weights
        )

        # 4. Final Aggregation
        final_score = total_weighted_score / len(job_chunks)
        section_breakdown = self._calculate_section_stats(raw_scores_map)

        return round(final_score, 4), details, section_breakdown

    def _prepare_cv_data(self, cv_sections: Dict[str, str]
                         ) -> Tuple[List[Dict[str, Any]], Any]:
        """
        Flattens CV sections into a list of chunks and a corresponding tensor of weights.
        Returns:
            (cv_chunks_data, weights_tensor)
        """
        cv_chunks_data = []
        weights_list = []

        for section, text in cv_sections.items():
            if not text.strip():
                continue

            chunks = self._chunk_text(text)
            weight = SECTION_WEIGHTS.get(section, 0.1)

            for c in chunks:
                cv_chunks_data.append({
                    "text": c,
                    "section": section
                })
                weights_list.append(weight)

        # Convert weights to a tensor for broadcasting later
        # Shape: (1, M) where M is number of CV chunks
        if weights_list:
            weights_tensor = torch.tensor(weights_list)
        else:
            weights_tensor = torch.tensor([])

        return cv_chunks_data, weights_tensor

    def _compute_weighted_matches(self,
                                  job_emb,
                                  cv_emb,
                                  job_chunks: List[str],
                                  cv_chunks_data: List[Dict],
                                  cv_weights: torch.Tensor
                                  ) -> Tuple[List[MatchDetail], float, Dict[str, List[float]]]:
        """
        Performs cosine similarity and applies weights using matrix operations.
        """
        # A. Calculate Raw Cosine Similarity
        # Shape: (N_job, M_cv)
        similarity_matrix = util.cos_sim(job_emb, cv_emb)

        # B. Apply Weights (Broadcasting)
        # We multiply every column j by the weight of CV chunk j
        # If using GPU/MPS, ensure weights are on the same device
        if job_emb.device != cv_weights.device:
            cv_weights = cv_weights.to(job_emb.device)

        weighted_matrix = similarity_matrix * cv_weights

        # C. Extract Best Matches
        details = []
        total_weighted_score = 0.0

        # Helper to collect stats per section
        # Key: section_name, Value: list of raw scores chosen as best matches
        raw_scores_map: Dict[str, List[float]] = {}

        # Iterate over job requirements (Rows)
        for i, job_req in enumerate(job_chunks):
            # Find index of the highest weighted score in this row
            best_idx = int(torch.argmax(weighted_matrix[i]))

            # Extract scores
            weighted_score = float(weighted_matrix[i][best_idx])
            raw_score = float(similarity_matrix[i][best_idx])

            # Clip weighted score to [0.0, 1.0] just in case weights > 1.0 cause overflow
            final_score = max(0.0, min(weighted_score, 1.0))

            # Get metadata
            best_match_data = cv_chunks_data[best_idx]
            section = best_match_data["section"]

            details.append(MatchDetail(
                job_requirement=job_req,
                best_cv_match=best_match_data["text"],
                cv_section=section,
                score=round(final_score, 4),
                raw_semantic_score=round(raw_score, 4)
            ))

            total_weighted_score += final_score

            # Collect stats
            if section not in raw_scores_map:
                raw_scores_map[section] = []
            raw_scores_map[section].append(raw_score)

        return details, total_weighted_score, raw_scores_map

    def _calculate_section_stats(self, raw_scores_map: Dict[str, List[float]]
                                 ) -> Dict[str, float]:
        """
        Calculates average raw similarity per section based on selected matches.
        """
        section_breakdown = {}
        for section, scores in raw_scores_map.items():
            if scores:
                avg = sum(scores) / len(scores)
                section_breakdown[section] = round(avg, 3)
            else:
                section_breakdown[section] = 0.0
        return section_breakdown

    def _chunk_text(self, text: str) -> List[str]:
        """
        Splits text into sentences using the injected Spacy NLP object.
        """
        doc = self.nlp(text)
        # Filter chunks that are too short (less than 3 words)
        chunks = [sent.text.strip()
                  for sent in doc.sents if len(sent.text.split()) > 2]
        return chunks
