from typing import List, Dict, Tuple, Any

from spacy.language import Language
from spacy.tokens import Doc
from sentence_transformers import SentenceTransformer, util
import torch

from src.config import SECTION_WEIGHTS
from src.data_models import MatchDetail

NOISE_PHRASES = {
    'nice to have', 'good to have', 'optional', 'benefits', 'what we offer'
    }
TRANS_TABLE = str.maketrans('', '', '():')


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

    def analyze(self, job_doc: Doc, cv_sec_docs: Dict[str, Doc]
                ) -> Tuple[float, List[MatchDetail], Dict[str, float]]:
        """
        Main entry point for semantic analysis.
        Orchestrates chunking, encoding, matrix calculation, and statistics.
        """

        # 1. Prepare Job Data (Signal)
        job_chunks = self._chunk_text(job_doc)
        if not job_chunks:
            return 0.0, [], {}

        job_embeddings = self.model.encode(job_chunks, convert_to_tensor=True)

        # 2. Prepare CV Data (flattened chunks with metadata)
        cv_chunks_data, cv_weights = self._prepare_cv_data(cv_sec_docs)

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
        # Clamp to keep semantic_score within [0,1]
        final_score = max(0.0, min(final_score, 1.0))
        section_breakdown = self._calculate_section_stats(raw_scores_map)

        return round(final_score, 4), details, section_breakdown

    def _prepare_cv_data(self, cv_sec_docs: Dict[str, Doc]
                         ) -> Tuple[List[Dict[str, Any]], Any]:
        """
        Flattens CV sections into a list of chunks and a corresponding tensor of weights.
        Returns:
            (cv_chunks_data, weights_tensor)
        """
        cv_chunks_data = []
        weights_list = []

        for section, doc in cv_sec_docs.items():
            if not doc or not doc.text.strip():
                continue

            chunks = self._chunk_text(doc)
            weight = SECTION_WEIGHTS.get(section, 0.5)

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
        # Ensure weights are on the same device
        if job_emb.device != cv_weights.device:
            cv_weights = cv_weights.to(job_emb.device)

        # C. Extract Best Matches (choose by raw similarity, then apply weight)
        details = []
        total_weighted_score = 0.0

        # Helper to collect stats per section
        # Key: section_name, Value: list of raw scores chosen as best matches
        raw_scores_map: Dict[str, List[float]] = {}

        # Iterate over job requirements (Rows)
        for i, job_req in enumerate(job_chunks):
            # 1) Select the best raw semantic match (no weights) to avoid overweighting sections
            best_idx = int(torch.argmax(similarity_matrix[i]))

            # Extract raw score and weight for that chunk
            raw_score = float(similarity_matrix[i][best_idx])
            weight = float(cv_weights[best_idx]) if len(cv_weights) > best_idx else 1.0

            # Apply section weight after selecting the best semantic match
            weighted_score = raw_score * weight

            # Clip weighted score to [0.0, 1.0]
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

    def _chunk_text(self, doc: Doc) -> List[str]:
        """
        Chunk text by newlines first, then refine with spaCy sentencizer per line.
        This avoids collapsing header-ish lines and keeps real sentences.
        """
        chunks = []
        noise_phrases = NOISE_PHRASES
        trans_table = TRANS_TABLE

        for line in doc.text.split('\n'):
            line = line.strip()
            if not line:
                continue

            # Quick header / metadata filters
            word_count = len(line.split())
            if word_count < 4:  # drop very short items like "Offer.", "AWS.", "B2B"
                continue
            if line.endswith(':'):
                continue
            # if ':' in line:
            #     before_colon = line.split(':')[0]
            #     # allow language lines like "Languages: Polish, English (C1)"
            #     lang_hint = 'language' in before_colon.lower() or 'languages' in before_colon.lower()
            #     if len(before_colon.split()) <= 3 and not lang_hint:
            #         continue

            # Split the remaining line into sentences using spaCy to avoid long run-ons
            for sent in self.nlp(line).sents:
                sent_text = sent.text.strip()
                if not sent_text:
                    continue

                # Re-run minimal length / noise checks on the sentence
                if len(sent_text.split()) < 4:
                    continue
                clean_text = sent_text.lower().translate(trans_table).strip()
                if clean_text in noise_phrases:
                    continue

                chunks.append(sent_text)

        return chunks
