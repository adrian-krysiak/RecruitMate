# Sentence Transformer Model (for semantic search)
SBERT_MODEL_NAME = 'all-mpnet-base-v2'

# SpaCy Model (for sentence splitting and lemmatization)
SPACY_MODEL_NAME = 'en_core_web_sm'

# Default weight for the SBERT component in the hybrid score
DEFAULT_ALPHA = 0.7

# Default values for chunking strategy (how many sentences per window/overlap)
CHUNK_WINDOW_SIZE = 3
CHUNK_OVERLAP_SIZE = 1