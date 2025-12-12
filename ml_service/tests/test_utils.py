from unittest.mock import MagicMock

from src.utils import get_match_status, chunk_text, lemmatize_text
from src.data_models import MatchStatus


def test_get_match_status_boundaries():
    """Verify that scores map to the correct status Enum."""
    assert get_match_status(0.80) == MatchStatus.GOOD
    assert get_match_status(0.751) == MatchStatus.GOOD
    assert get_match_status(0.60) == MatchStatus.MEDIUM
    assert get_match_status(0.40) == MatchStatus.WEAK
    assert get_match_status(float('-inf')) == MatchStatus.NONE


def test_chunk_text_logic():
    """Test the sliding window chunking logic."""
    mock_nlp = MagicMock()

    # Create fake sentences
    s1, s2, s3, s4 = MagicMock(), MagicMock(), MagicMock(), MagicMock()
    s1.text = "Sentence one."
    s2.text = "Sentence two."
    s3.text = "Sentence three."
    s4.text = "Sentence four."

    mock_doc = MagicMock()
    mock_doc.sents = [s1, s2, s3, s4]
    mock_nlp.return_value = mock_doc

    # Window size 3, Overlap 1 -> Step = 2
    # Chunk 1: [s1, s2, s3]
    # Chunk 2: [s3, s4]
    chunks = chunk_text("dummy text", mock_nlp, window_size=3, overlap=1)

    assert len(chunks) == 2
    assert "Sentence one." in chunks[0]
    assert "Sentence three." in chunks[0]
    assert "Sentence three." in chunks[1]


def test_lemmatize_text_cleaning():
    """Test that text is cleaned and lemmatized."""
    # Mocking nlp is safer for unit tests

    mock_nlp = MagicMock()
    token1 = MagicMock(lemma_="code", is_alpha=True)
    token2 = MagicMock(lemma_="python", is_alpha=True)
    token3 = MagicMock(lemma_="123", is_alpha=False)  # Should be ignored

    mock_doc = MagicMock()
    mock_doc.__iter__.return_value = [token1, token2, token3]
    mock_nlp.return_value = mock_doc

    result = lemmatize_text("Coding in Python 123", mock_nlp)
    assert result == "code python"