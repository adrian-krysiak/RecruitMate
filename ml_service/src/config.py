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
    # Boost the core signals above the neutral baseline (1.0)
    'experience': 1.3,
    'projects': 1.15,
    'education': 1.1,
    'skills': 1.05,

    # Neutral baseline for generic/intro content
    'summary': 1.0,
    'uncategorized': 1.0,

    # Keep low for noisy/unmapped content
    'other': 0.5
}

NER_SKILLS_DATA_PATH = {
    'raw_eu': 'data/raw/skills_en.csv',
    'raw_add': 'data/raw/skills_en_addons.csv',
    'processed': 'data/processed/skills_en.pkl',
}

STRONG_ROOTS = {
            # --- Leadership & Management ---
            "lead", "manage", "spearhead", "orchestrate", "direct", "supervise", "oversee",
            "guide", "mentor", "coach", "train", "recruit", "hire", "onboard",
            "delegate", "chair", "govern", "administer", "steer", "captain", "mobilize",
            "empower", "champion", "authorize", "cultivate",

            # --- Creation, Development & Architecture ---
            "create", "develop", "design", "build", "architect", "engineer", "construct",
            "fabricate", "formulate", "invent", "originate", "establish", "found",
            "institute", "implement", "launch", "deploy", "ship", "pioneer", "initiate",
            "compose", "conceive", "craft", "forge", "generate",

            # --- Technical, Data & Operations ---
            "program", "code", "script", "configure", "install", "integrate", "migrate",
            "upgrade", "maintain", "repair", "troubleshoot", "debug", "refactor",
            "automate", "virtualize", "containerize", "scale", "digitize", "compute",
            "process", "extract", "transform", "load", "mine", "query", "index",

            # --- Analysis, Problem Solving & Strategy ---
            "analyze", "evaluate", "assess", "audit", "investigate", "research",
            "examine", "explore", "survey", "quantify", "measure", "calculate",
            "model", "simulate", "forecast", "predict", "identify", "detect",
            "diagnose", "solve", "resolve", "tackle", "strategize", "conceptualize",
            "vision", "plan", "map", "chart", "benchmark", "deduce", "infer",

            # --- Optimization & Improvement ---
            "optimize", "improve", "enhance", "maximize", "minimize", "reduce",
            "streamline", "accelerate", "boost", "amplify", "refine", "polish",
            "modernize", "revamp", "overhaul", "transform", "standardize", "restructure",
            "strengthen", "vitalize", "augment", "elevate",

            # --- Execution, Delivery & Achievement ---
            "execute", "deliver", "perform", "achieve", "attain", "accomplish",
            "complete", "finalize", "produce", "yield", "win", "secure", "exceed",
            "outperform", "succeed", "realize", "obtain", "fulfill",

            # --- Communication, Negotiation & Collaboration ---
            "communicate", "articulate", "present", "speak", "lecture", "negotiate",
            "persuade", "convince", "influence", "market", "sell", "promote",
            "advocate", "liaise", "collaborate", "partner", "cooperate", "coordinate",
            "facilitate", "moderate", "unify", "reconcile", "mediate", "arbitrate",
            "clarify", "define", "illustrate",

            # --- Documentation & Compliance ---
            "document", "report", "author", "write", "publish", "draft", "edit",
            "review", "summarize", "outline", "verify", "validate", "certify",
            "ensure", "guarantee", "monitor", "track", "log", "record"
        }