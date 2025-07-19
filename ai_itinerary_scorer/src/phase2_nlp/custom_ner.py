"""
src/phase2_nlp/custom_ner.py

Handles loading (and optionally training) a custom spaCy NER model.
Falls back to default English NER if no custom model is present.
"""

import spacy
from pathlib import Path
from config.settings import NER_MODEL_PATH, SPACY_MODEL

def load_ner():
    """
    Returns a spaCy Language model for NER.
    Tries to load your custom model first,
    otherwise falls back to the standard spaCy pipeline.
    """
    custom_model_path = Path(NER_MODEL_PATH)
    if custom_model_path.is_dir():
        try:
            nlp = spacy.load(str(custom_model_path))
            print(f"Loaded custom NER model from '{custom_model_path}'.")
            return nlp
        except Exception as e:
            print(f"Could not load custom model at {custom_model_path}: {e}")

    # Fallback to stock spaCy model (English)
    print(f"Falling back to spaCy model '{SPACY_MODEL}'.")
    return spacy.load(SPACY_MODEL)

def train_custom_ner(training_data, output_dir):
    """
    Fine-tune a spaCy NER model for travel itineraries.

    Args:
        training_data: List of (text, {"entities": [(start, end, label), ...]}) pairs.
        output_dir: Path to save the trained model.

    Example:
        training_data = [
            ("Day 1: Visit Eiffel Tower.", {"entities": [(12, 25, "LOCATION")]}),
            ...
        ]
    
    To actually train, use spaCy CLI/tools or see spaCy docs for scripts:
    https://spacy.io/usage/training
    """
    # This is a placeholder stub.
    # Add CLI wrappers, integration with prodigy, or manual code as needed.
    raise NotImplementedError("Custom NER training should be implemented in scripts/train_model.py or a separate pipeline.")

# CLI/test mode: Try loading to validate that config/settings path works.
if __name__ == "__main__":
    nlp = load_ner()
    sample = "Arrive at Rome airport on July 10th. Visit the Vatican in afternoon."
    doc = nlp(sample)
    print("Entities:", [(ent.text, ent.label_) for ent in doc.ents])
