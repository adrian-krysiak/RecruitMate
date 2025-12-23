# Sentence Transformer Model (for semantic search)
SBERT_MODEL_NAME = 'all-MiniLM-L6-v2'  # faster than 'all-mpnet-base-v2'

# SpaCy Model (for sentence splitting and lemmatization)
SPACY_MODEL_NAME = 'en_core_web_sm'

# Default Algorithm Settings
DEFAULT_ALPHA = 0.7  # 70% Semantics, 30% Keywords

# Default values for chunking strategy (how many sentences per window/overlap)
CHUNK_WINDOW_SIZE = 1
CHUNK_OVERLAP_SIZE = 0

# Weights assigned to different sections during matching
SECTION_WEIGHTS = {
    'experience': 1.0,
    'projects': 0.75,
    'education': 0.7,
    'skills': 0.65,
    'summary': 0.5,  # fallback for CV + intro
    'uncategorized': 0.5,  # fallback for Job Offer
    'other': 0.1          # ignored or low priority sections
}
