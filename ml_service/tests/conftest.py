import pytest
from unittest.mock import MagicMock, patch
import numpy as np
import torch

from src.orchestrator import HybridMatchEngine


@pytest.fixture
def mock_engine():
    """
    Creates an instance of HybridMatchEngine with mocked internal models.
    """
    with patch("src.orchestrator.spacy.load") as mock_spacy_load, \
            patch("src.orchestrator.SentenceTransformer") as mock_sbert_cls, \
            patch("src.processors.fallback_tfidf.TfidfVectorizer") as mock_tfidf_cls, \
            patch("src.processors.semantic.util.cos_sim") as mock_cos_sim:

        # 1. Mocking NLP (spaCy)
        nlp_mock = MagicMock()
        nlp_mock.pipe_names = []

        def simple_pipeline(text, disable=None):
            doc_mock = MagicMock()

            # Mock sentences
            if not text or not text.strip():
                doc_mock.sents = []
                doc_mock.ents = []
            else:
                sentences = [MagicMock(text=t.strip())
                             for t in text.split('.') if t.strip()]
                if not sentences:
                    sentences = [MagicMock(text=text)]
                doc_mock.sents = sentences

            # Mock Entities (Simple heuristic for testing)
            ents = []
            for word in text.split():
                if word.lower() in ["python", "sql", "java"]:
                    ent = MagicMock()
                    ent.text = word
                    ent.label_ = "SKILL"
                    ents.append(ent)
            doc_mock.ents = ents

            # Mock Tokens
            tokens = []
            for word in text.split():
                token = MagicMock()
                token.lemma_ = word.lower()
                token.text = word
                token.is_alpha = word.isalpha()
                token.is_stop = False
                token.pos_ = "VERB" if word.lower(
                ) in ["manage", "lead"] else "NOUN"
                token.dep_ = "ROOT"
                token.children = []
                tokens.append(token)

            doc_mock.__iter__.return_value = tokens
            return doc_mock

        nlp_mock.side_effect = simple_pipeline
        mock_spacy_load.return_value = nlp_mock

        # 2. Mocking SBERT
        mock_sbert_instance = MagicMock()
        mock_sbert_instance.encode.side_effect = lambda sentences, convert_to_tensor=True: torch.rand(
            len(sentences), 384)
        mock_sbert_cls.return_value = mock_sbert_instance

        # 3. Mocking TF-IDF
        mock_tfidf_instance = MagicMock()
        mock_matrix = MagicMock()
        mock_matrix.todense.return_value = np.random.rand(2, 10)
        mock_matrix.__getitem__.return_value = mock_matrix

        mock_tfidf_instance.fit_transform.return_value = mock_matrix
        mock_tfidf_instance.get_feature_names_out.return_value = [
            f"word_{i}" for i in range(10)]
        mock_tfidf_cls.return_value = mock_tfidf_instance

        # 4. Mocking Cosine Similarity
        def mock_cos_sim_side_effect(a, b):
            return torch.rand(a.shape[0], b.shape[0])

        mock_cos_sim.side_effect = mock_cos_sim_side_effect

        yield HybridMatchEngine()
