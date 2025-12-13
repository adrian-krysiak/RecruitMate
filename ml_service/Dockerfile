FROM python:3.13-slim

WORKDIR /app

# Set environment variables
# OMP/MKL/OPENBLAS set to 1 to prevent CPU oversubscription
# when using ThreadPoolExecutor with many workers.
# Code is left commented, because benchamrks showed better performance without limits
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    SENTENCE_TRANSFORMERS_HOME=/app/models_cache
    # OMP_NUM_THREADS=1 \
    # MKL_NUM_THREADS=1 \
    # OPENBLAS_NUM_THREADS=1 \
    # VECLIB_MAXIMUM_THREADS=1 \
    # NUMEXPR_NUM_THREADS=1 \
    # TORCH_NUM_THREADS=1

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install PyTorch CPU version explicitly to save ~6GB
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy only config files first to allow caching of model downloads
COPY src/__init__.py src/config.py ./src/

# Download models dynamically using variables from config.py
RUN python -c "from src.config import SPACY_MODEL_NAME, SBERT_MODEL_NAME; \
    import spacy.cli; spacy.cli.download(SPACY_MODEL_NAME); \
    from sentence_transformers import SentenceTransformer; SentenceTransformer(SBERT_MODEL_NAME)"

COPY src/ ./src/
COPY main.py .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5001", "--reload"]