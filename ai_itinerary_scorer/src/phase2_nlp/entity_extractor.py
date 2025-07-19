"""
src/phase2_nlp/entity_extractor.py

Extracts named entities from itinerary text using a custom spaCy NER model.
Returns a structured list of entities including text, label, and character offsets.
"""

from .custom_ner import load_ner
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

# Load the NER model once at import time for efficiency.
nlp = load_ner()

def extract_entities(text: str) -> List[Dict]:
    """
    Extracts entities from the provided text using the loaded NER model.

    Args:
        text (str): Input itinerary or natural language document.

    Returns:
        List[Dict]: List of dictionaries with 'text', 'label', 'start', 'end'.
    """
    doc = nlp(text)
    entities = []
    for ent in doc.ents:
        entities.append({
            'text': ent.text,
            'label': ent.label_,
            'start': ent.start_char,
            'end': ent.end_char
        })
    logger.debug(f"Extracted {len(entities)} entities from text")
    return entities

# Simple CLI for quick testing
if __name__ == "__main__":
    sample_text = "Dinner at Le Jules Verne in the evening, visit Louvre Museum on Day 2."
    print(extract_entities(sample_text))
