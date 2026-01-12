# RecruitMate ML Service

The RecruitMate ML Service is a **Hybrid CV-to-Job Match Engine** that evaluates the compatibility between candidate resumes and job offers using a sophisticated multi-layered approach. It combines semantic analysis (SBERT), keyword extraction (Named Entity Recognition with ESCO skills dataset), fallback TF-IDF matching, and writing style analysis to provide comprehensive match scoring.

## Project Structure

```
ml_service/
├── data/                          # Data-related files
│   ├── raw/                       # Raw datasets
│   │   ├── skills_en.csv         # ESCO European Skills dataset
│   │   └── skills_en_addons.csv  # Custom supplementary skills
│   └── processed/                 # Processed/cached data
│       └── skills_en.pkl         # Preprocessed ESCO patterns
├── models_cache/                  # Cached ML models
│   ├── models--sentence-transformers--all-MiniLM-L6-v2/
│   └── models--sentence-transformers--all-mpnet-base-v2/
├── notebooks/                     # Jupyter notebooks for analysis
│   └── similarity_check.ipynb
├── scripts/                       # Utility scripts
│   └── benchmark.py
├── src/                           # Source code for the matching engine
│   ├── __init__.py
│   ├── config.py                 # Configuration settings
│   ├── data_models.py            # Pydantic models for I/O
│   ├── orchestrator.py           # Main matching pipeline
│   ├── parsers.py                # CV and job description parsers
│   ├── utils.py                  # Utility functions
│   └── processors/               # Processing modules
│       ├── __init__.py
│       ├── semantic.py           # Semantic similarity (SBERT)
│       ├── ner.py                # Named Entity Recognition (ESCO skills)
│       └── fallback_tfidf.py     # Fallback TF-IDF matching
├── tests/                         # Comprehensive test suite
│   ├── __init__.py
│   ├── conftest.py               # Test fixtures
│   ├── test_api.py               # API endpoint tests
│   ├── test_engine.py            # Core engine tests
│   ├── test_integration.py       # End-to-end integration tests
│   ├── test_data.py              # Data processing tests
│   └── test_parsers.py           # Parser tests
├── main.py                        # FastAPI application entry point
├── requirements.txt               # Python dependencies
├── Dockerfile                     # Docker containerization
├── pytest.ini                     # Pytest configuration
└── README.md                      # Project documentation
```

## Installation

### Prerequisites
- Python 3.11+
- pip or conda

### Step-by-Step Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-repo/RecruitMate.git
   cd RecruitMate/ml_service
   ```

2. **Create a virtual environment and activate it**:
   ```bash
   python -m venv venv
   .\venv\Scripts\activate  # Windows
   # or
   source venv/bin/activate  # macOS/Linux
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Download required NLP models**:
   
   spaCy NLP model:
   ```bash
   python -m spacy download en_core_web_sm
   ```
   
   SBERT embeddings model (`all-MiniLM-L6-v2`):
   - The model will be automatically downloaded on first service startup and cached in `models_cache/`
   - Alternatively, pre-download it:
   ```bash
   python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"
   ```

5. **Start the service**:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 5001 --reload
   ```

   The API will be available at `http://localhost:5001`
   - Interactive API docs: `http://localhost:5001/docs`
   - Alternative API docs: `http://localhost:5001/redoc`

## Usage

### API Endpoints

#### 1. **Health Check**
Check if the service and models are loaded and ready.

```bash
GET /health
```

**Response:**
```json
{
  "status": "ok",
  "models_loaded": true
}
```

#### 2. **Match CV to Job Offer** (Main Endpoint)
Evaluate the compatibility between a CV and a job offer.

```bash
POST /match
Content-Type: application/json
```

**Request Body:**
```json
{
  "cv": "AI & Data Engineering Specialist. AI-focused Data Engineer with professional experience in Python, SQL, and cloud ecosystems. Expert in transforming complex datasets into actionable insights, developing machine learning models, and architecting Generative AI solutions (including LangChain agents with RAG). Data Engineer | Global Professional Services Firm Feb 2024 – Feb 2025. Architected ETL processes for large-scale datasets on Azure using Python, SQL, and PySpark. Implemented predictive models (Random Forest, Logistic Regression) to enhance analytical accuracy and business decision-making. Developed AI agents using LangChain (RAG, custom tool integration) to automate internal workflows and optimize LLM-driven document querying.",
  "job_offer": "AI Transformation Consultant. We are a consulting–technology company specializing in process automation and transformations based on Agentic AI and RAG systems. Organizations around the world – from the USA, through Europe, to the Middle East – rely on our expertise to move from AI experimentation to real implementations that deliver measurable business results. In this role you will: Participate in early conversations with clients to uncover real needs and transformation directions. Lead advisory and strategic discussions, co-creating the vision for AI-based solutions. We'll be excited to talk to you if: You are able to conduct conversations with decision-makers and understand the broader business context. You communicate fluently in English (C1+) – daily work with international clients is natural for you.",
  "alpha": 0.7
}
```

**Parameters:**
- `cv` (string, required): The candidate's CV/resume text (minimum 50 characters)
- `job_offer` (string, required): The job description text (minimum 50 characters)
- `alpha` (float, optional, default: 0.7): Balance between semantic matching (0.7) and keyword matching (0.3)
  - Values: 0.0–1.0
  - 1.0 = 100% semantic similarity, 0% keyword matching
  - 0.0 = 0% semantic similarity, 100% keyword matching
  - 0.7 = Default: 70% semantic, 30% keyword-based

**Response:**
```json
{
  "match_score": 0.407,
  "semantic_score": 0.427,
  "keyword_score": 0.329,
  "action_verb_score": 0.591,
  "common_keywords": [
    "artificial intelligence",
    "english",
    "machine learning",
    "make decisions",
    "rag"
  ],
  "missing_keywords": [
    "adaptability",
    "advise others",
    "apply strategic thinking",
    "aws",
    "business processes",
    "communication",
    "lead others",
    "project management",
    "show initiative",
    "teamwork"
  ],
  "section_scores": {
    "experience": 0.374,
    "summary": 0.431,
    "skills": 0.358,
    "education": 0.374,
    "projects": 0.172
  },
  "details": [
    {
      "job_requirement": "We are a consulting–technology company specializing in process automation and transformations based on Agentic AI and RAG systems.",
      "best_cv_match": "Developed AI agents using LangChain (RAG, custom tool integration) to automate internal workflows and optimize LLM-driven document querying.",
      "cv_section": "experience",
      "score": 0.75,
      "raw_semantic_score": 0.577
    },
    {
      "job_requirement": "You communicate fluently in English (C1+) – daily work with international clients is natural for you.",
      "best_cv_match": "Languages: Polish (Native), English (C1/Advanced), German (Intermediate/B1+).",
      "cv_section": "skills",
      "score": 0.462,
      "raw_semantic_score": 0.44
    }
  ]
}
```

**Response Fields:**

- `match_score`: Overall match percentage (0.0–1.0)
- `semantic_score`: Semantic similarity based on SBERT embeddings
- `keyword_score`: Skills gap analysis using ESCO dataset
- `action_verb_score`: Writing quality bonus based on action verbs
- `common_keywords`: Skills found in both CV and job offer
- `missing_keywords`: Required skills absent from CV
- `section_scores`: Match scores per CV section
- `details`: Job requirement to CV match pairs with similarity scores

### Python Client Example

```python
import requests

API_URL = "http://localhost:5001"

response = requests.post(
    f"{API_URL}/match",
    json={
        "cv": "AI & Data Engineering Specialist with experience in Python, SQL, Azure, and machine learning...",
        "job_offer": "AI Transformation Consultant required. Experience with Agentic AI, RAG systems...",
        "alpha": 0.7
    }
)

result = response.json()
print(f"Overall Match: {result['match_score']:.1%}")
print(f"Semantic Score: {result['semantic_score']:.1%}")
print(f"Missing Skills: {', '.join(result['missing_keywords'][:5])}")
```

## Methodology

The RecruitMate ML Service employs a sophisticated 4-step pipeline to evaluate CV-to-job compatibility:

### Step 1: Parsing & Extraction

**CV Parser** extracts:
- Skills section
- Work experience
- Education
- Projects
- Summary/objective
- Other sections

**Job Offer Parser** extracts:
- Requirements
- Responsibilities
- Education requirements
- Other relevant sections (filters out boilerplate like "About Company")

Uses regex patterns and header heuristics to automatically detect and categorize content.

### Step 2: Multi-Modal Processing

Three parallel processors analyze the parsed content:

#### A. Named Entity Recognition (NER) - Keyword Matching
- **Tool**: ESCO dataset with 104,082+ European skills
- **Process**:
  - Loads skill patterns from `data/processed/skills_en.pkl`
  - Uses spaCy's EntityRuler with special tokenization for multi-token skills (e.g., "C++", ".NET", "Node.js")
  - Performs gap analysis: compares job-required skills against CV sections
  - Applies section weights to penalize/reward matches by importance:
    - Experience: 1.3 (most important)
    - Projects: 1.15
    - Education: 1.1
    - Skills section: 1.05
    - Summary: 1.0
- **Output**: `keyword_score` (0.0–1.0), `common_keywords`, `missing_keywords`

#### B. Semantic Similarity - SBERT Embeddings
- **Tool**: Sentence-BERT (`all-MiniLM-L6-v2` by default)
- **Process**:
  1. Chunks text by newlines, then by sentences (minimum 4 words per chunk)
  2. Generates embeddings for all job offer chunks and CV chunks
  3. Calculates cosine similarity matrix (vectorized with NumPy)
  4. Selects best matching pairs and applies section weights
  5. Averages to produce section-level and overall scores
- **Output**: `semantic_score` (0.0–1.0), `section_breakdown`, `detailed_matches`

#### C. Action Verb Analysis - Writing Quality
- **Process**:
  - Analyzes narrative sections (experience, projects) for strong action verbs
  - Compares against 100+ power verbs (lead, architect, orchestrate, innovate, etc.)
  - Calculates verb quality ratio: strong verbs / total verbs
- **Output**: `action_verb_score` (0.0–1.0, converted to 0–5% bonus)

### Step 3: Fallback Mechanism

**TF-IDF Fallback** activates when:
- NER finds no skill matches (`keyword_score == 0.0`)
- Provides safety net for niche skills not in ESCO dataset

**Process**:
1. Lemmatizes both CV and job text using spaCy
2. Applies TF-IDF vectorization with English stop word removal
3. Extracts top 10 common keywords by combined weight
4. Boosts keyword score with fallback results

### Step 4: Final Score Calculation

```
base_score = (alpha × semantic_score) + ((1.0 - alpha) × keyword_score)
style_bonus = action_verb_score × 0.05
final_score = (base_score × 0.95) + style_bonus
final_score = clamp(final_score, 0.0, 1.0)
```

**Example** (with alpha=0.7):
- Semantic: 0.80, Keyword: 0.75, Action Verb: 0.90
- Base: (0.7 × 0.80) + (0.3 × 0.75) = 0.56 + 0.225 = 0.785
- Bonus: 0.90 × 0.05 = 0.045
- Final: (0.785 × 0.95) + 0.045 = 0.746 + 0.045 = **0.791**

## Data Sources & Licensing

### ESCO Dataset (Primary)

The project utilizes the **ESCO (European Skills, Competences, Qualifications and Occupations)** dataset to power its Named Entity Recognition (NER) engine.

**Details:**
- **Source**: [European Commission - ESCO](https://esco.ec.europa.eu/)
- **Version**: Full 2024 English dataset (`skills_en.csv`)
- **Records**: 104,082+ European skills and competencies
- **License**: CC-BY (reuse authorized under [Commission Decision 2011/833/EU](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=celex%3A32011D0833))
- **Attribution**: "This service uses the ESCO classification of the European Commission."
- **Download**: Available at [ESCO portal](https://esco.ec.europa.eu/en/download)

**Modifications:**
- Filtered for IT, software development, and engineering skills
- Processed to extract preferred labels and create tokenizer special-cases for multi-token skills (e.g., "C++", ".NET", "Node.js")
- Cached as pickle format (`data/processed/skills_en.pkl`) for faster loading

### Skills Addons Dataset (Secondary)

**File**: `data/raw/skills_en_addons.csv`

**Details:**
- **Source**: Custom-generated supplementary skills dataset
- **Purpose**: Extends ESCO coverage for emerging technologies and industry-specific skills not yet in the official ESCO dataset
- **Generated with**: Assistance from Google Gemini API to ensure quality and relevance
- **Coverage**: Modern frameworks, tools, and specializations (e.g., newer versions of frameworks, emerging cloud tools)
- **Integration**: Merged with ESCO dataset during preprocessing for comprehensive skill coverage

**Note**: The combined dataset is processed and cached; modifications preserve both source datasets' integrity.

### Data Processing Pipeline

1. **ESCO Skills Loading**: Extracts `preferredLabel` and `altLabels` from `skills_en.csv`
2. **Addon Integration**: Merges custom skills from `skills_en_addons.csv`
3. **Preprocessing**: Creates spaCy EntityRuler patterns with special tokenization rules
4. **Caching**: Serializes to `data/processed/skills_en.pkl` for performance
5. **On-Load**: Deserializes cached patterns for NER processing

## Dependencies

The project uses the following Python libraries:

| Package | Version | Purpose |
|---------|---------|---------|
| `fastapi` | 0.124.4 | Web framework for API endpoints |
| `uvicorn` | 0.38.0 | ASGI server for running the application |
| `sentence-transformers` | 5.2.0 | SBERT models for semantic embeddings |
| `spacy` | 3.8.11 | NLP pipeline (tokenization, POS tagging, lemmatization) |
| `scikit-learn` | 1.8.0 | TF-IDF vectorization for fallback matching |
| `pandas` | 2.3.3 | Data manipulation and CSV handling |
| `numpy` | 2.4.0rc1 | Numerical operations and matrix calculations |
| `pydantic` | 2.12.5 | Input/output validation with type hints |
| `pytest` | 9.0.2 | Testing framework |
| `httpx` | 0.28.1 | HTTP client for API testing |
| `pytest-asyncio` | 1.3.0 | Async test support for FastAPI |

**Python Version**: 3.11+

Refer to [requirements.txt](requirements.txt) for the complete list with exact versions.

## Testing

The project includes a comprehensive test suite covering unit, integration, and end-to-end scenarios.

### Test Files

- [tests/test_parsers.py](tests/test_parsers.py) - CV and job offer parsing
- [tests/test_data.py](tests/test_data.py) - Data models and validation
- [tests/test_engine.py](tests/test_engine.py) - Core matching engine logic
- [tests/test_api.py](tests/test_api.py) - FastAPI endpoint validation
- [tests/test_integration.py](tests/test_integration.py) - End-to-end matching scenarios
- [tests/conftest.py](tests/conftest.py) - Shared fixtures and mocks

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test file
pytest tests/test_engine.py

# Run with verbose output
pytest -v

# Run integration tests only
pytest tests/test_integration.py -v
```

### Test Fixtures

The test suite includes:
- Mocked ML models (spaCy, SBERT, TF-IDF) for fast unit tests
- Real model integration tests for validation
- Sample CVs and job offers covering diverse scenarios
- Edge case handling (empty sections, niche skills, etc.)

## Docker Deployment

The service can be containerized and deployed using Docker.

### Building and Running

```bash
# Build the image
docker build -t recruitmate-ml:latest .

# Run the container
docker run -p 5001:5001 recruitmate-ml:latest

# Or use docker-compose from the root directory
docker compose up ml_service
```

### Environment Configuration

The service reads configuration from:
1. [src/config.py](src/config.py) - Default settings
2. Environment variables (optional overrides)

Key configurable items:
- SBERT model name
- spaCy model name
- Semantic/keyword balance defaults
- Section weights for gap analysis

See [src/config.py](src/config.py) for all available settings.

## License

This project is licensed under the MIT License. See the [LICENSE](../LICENSE) file for details.

## Acknowledgments

- **ESCO Dataset**: This project uses the ESCO classification of the European Commission under the CC-BY license
- **Sentence Transformers**: Built upon the excellent [sentence-transformers](https://www.sbert.net/) library by UKPLab
- **spaCy**: NLP processing powered by [spaCy](https://spacy.io/)
- **Gemini API**: Used to generate supplementary skills dataset ([skills_en_addons.csv](data/raw/skills_en_addons.csv)) to extend ESCO coverage
- **Community**: Thanks to the open-source ML and NLP communities