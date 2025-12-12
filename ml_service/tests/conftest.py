import pytest
from unittest.mock import MagicMock, patch
import numpy as np

from src.matching_engine import HybridMatchEngine


@pytest.fixture
def mock_engine():
    """
    Creates an instance of HybridMatchEngine with mocked internal models.
    """
    # Added patch for cosine_similarity to control matrix dimensions
    with patch("src.matching_engine.spacy.load") as mock_spacy_load, \
            patch("src.matching_engine.SentenceTransformer") as mock_sbert_cls, \
            patch("src.matching_engine.TfidfVectorizer") as mock_tfidf_cls, \
            patch("src.matching_engine.cosine_similarity") as mock_cosine_sim:

        # 1. Mocking NLP (spaCy)
        nlp_mock = MagicMock()

        def simple_tokenizer(text):
            # FIX: Return empty list if text is empty/whitespace
            # This ensures the engine's guard clause works correctly
            if not text or not text.strip():
                doc_mock = MagicMock()
                doc_mock.sents = []
                return doc_mock

            sentences = [MagicMock(text=t.strip()) for t in text.split('.') if t.strip()]
            if not sentences:
                sentences = [MagicMock(text=text)]

            doc_mock = MagicMock()
            doc_mock.sents = sentences

            # Mock token iteration for lemmatization
            tokens = [MagicMock(lemma_=word.lower(), is_alpha=True) for word in text.split()]
            doc_mock.__iter__.return_value = tokens
            return doc_mock

        nlp_mock.side_effect = simple_tokenizer
        mock_spacy_load.return_value = nlp_mock

        # 2. Mocking SBERT (Semantic Model)
        mock_sbert_instance = MagicMock()

        # FIX: Ensure encoded matrix matches the number of input sentences
        def mock_encode(sentences):
            return np.random.rand(len(sentences), 384)

        mock_sbert_instance.encode.side_effect = mock_encode
        mock_sbert_cls.return_value = mock_sbert_instance

        # 3. Mocking TF-IDF (Keyword Model)
        mock_tfidf_instance = MagicMock()
        mock_matrix = MagicMock()

        # Mocking slicing behavior [0:1]
        mock_slice = MagicMock()
        mock_slice.todense.return_value = np.random.rand(1, 10)
        mock_matrix.__getitem__.return_value = mock_slice

        # Mocking full matrix todense()
        mock_matrix.todense.return_value = np.random.rand(2, 10)

        mock_tfidf_instance.fit_transform.return_value = mock_matrix
        mock_tfidf_instance.get_feature_names_out.return_value = [f"word_{i}" for i in range(10)]
        mock_tfidf_cls.return_value = mock_tfidf_instance

        # 4. Mocking Cosine Similarity (CRITICAL FIX)
        # Instead of a fixed value, we dynamically generate a matrix
        # based on the input shapes to avoid IndexError.
        def mock_cosine_side_effect(a, b):
            # a shape: (num_job_chunks, embedding_dim)
            # b shape: (num_cv_chunks, embedding_dim)
            rows = a.shape[0]
            cols = b.shape[0]
            # Return matrix of shape (rows, cols) filled with 0.8
            return np.full((rows, cols), 0.8)

        mock_cosine_sim.side_effect = mock_cosine_side_effect

        # Initialize the engine
        engine = HybridMatchEngine()

        yield engine
