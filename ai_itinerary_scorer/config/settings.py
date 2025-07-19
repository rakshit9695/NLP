# config/settings.py

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()

# === Paths ===
ROOT_DIR = Path(__file__).resolve().parent.parent
NER_MODEL_PATH = os.getenv("NER_MODEL_PATH", str(ROOT_DIR / "data/models/ner"))
EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME", "all-MiniLM-L6-v2")
DB_PATH = os.getenv("DB_PATH", str(ROOT_DIR / "data/processed/famous_places.db"))

# === Scoring weights (default, can override via ENV) ===
def parse_float(name, default):
    try:
        return float(os.getenv(name, default))
    except Exception:
        return default

SCORING_WEIGHTS = {
    "feasibility": parse_float("WEIGHT_FEASIBILITY", 0.3),
    "popularity": parse_float("WEIGHT_POPULARITY", 0.25),
    "diversity": parse_float("WEIGHT_DIVERSITY", 0.2),
    "flow": parse_float("WEIGHT_FLOW", 0.15),
    "preference_alignment": parse_float("WEIGHT_PREFERENCE", 0.1),
}

# === NLP Settings ===
SPACY_MODEL = os.getenv("SPACY_MODEL", "en_core_web_sm")

# SBERT SentenceTransformer pooling/quantization options can go here in the future

# === Other constants ===
MAX_UPLOAD_SIZE_MB = int(os.getenv("MAX_UPLOAD_SIZE_MB", 5))
SUPPORTED_FILETYPES = (".pdf", ".docx")

# Example of optional API keys (not used for open-source, but shown for expansion)
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

# === Utility ===
def print_config():
    print("NER_MODEL_PATH =", NER_MODEL_PATH)
    print("EMBEDDING_MODEL_NAME =", EMBEDDING_MODEL_NAME)
    print("DB_PATH =", DB_PATH)
    print("SCORING_WEIGHTS =", SCORING_WEIGHTS)
    print("SPACY_MODEL =", SPACY_MODEL)
    print("MAX_UPLOAD_SIZE_MB =", MAX_UPLOAD_SIZE_MB)
    print("SUPPORTED_FILETYPES =", SUPPORTED_FILETYPES)

if __name__ == "__main__":
    print("---- AI Itinerary Scorer Configuration ----")
    print_config()
