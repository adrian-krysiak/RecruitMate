import re

import spacy
from typing import List
from spacy.tokens import Doc

from src.config import CHUNK_WINDOW_SIZE, CHUNK_OVERLAP_SIZE


def lemmatize_text(text: str, nlp: spacy.Language) -> str:
    """Cleans text and converts words to their base form (lemma)
    using spaCy."""
    # Ensure text is lowercase for consistency
    doc: Doc = nlp(text.lower())
    # Filter for only alphabetical tokens and join their lemmas
    return " ".join([token.lemma_ for token in doc if token.is_alpha])


def chunk_text(text: str, nlp: spacy.Language,
               window_size: int = CHUNK_WINDOW_SIZE,
               overlap: int = CHUNK_OVERLAP_SIZE) -> List[str]:
    """Splits a long text into overlapping chunks based on sentences
    (Sliding Window)."""

    if not isinstance(text, str):
        return []

    flat_text = re.sub(r'\s+', ' ', text).strip()
    if not flat_text: return []
    doc: Doc = nlp(flat_text)
    sentences = [sent.text.strip() for sent in doc.sents]

    # If text is very short, return it as a single chunk
    if len(sentences) <= window_size:
        return [flat_text]

    chunks = []
    # Calculate step size (must be at least 1)
    step = max(1, window_size - overlap)

    # Create chunks
    for i in range(0, len(sentences), step):
        group = sentences[i:i + window_size]
        chunks.append(' '.join(group))

    return chunks
