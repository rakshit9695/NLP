"""
src/phase2_nlp/relation_extractor.py

Extracts relationships between entities in itinerary text.
Simple rule-based examples provided (can be extended to dependency parsing or ML).
"""

import re
from typing import List, Dict

def extract_relations(text: str, entities: List[Dict]) -> List[Dict]:
    """
    Basic pattern/rule-based relation extraction for itineraries.
    
    Args:
        text (str): The original itinerary segment text.
        entities (List[Dict]): Entity dicts as output from entity_extractor.py
    
    Returns:
        List[Dict]: Each dict has {"from", "relation", "to"} keys.
    """
    relations = []
    # Index by label for convenience
    by_label = {}
    for ent in entities:
        by_label.setdefault(ent['label'], []).append(ent)
    
    # Example 1: Activity at Location ("Dinner at Le Jules Verne")
    # For each ACTIVITY, look for the pattern "ACTIVITY at LOCATION"
    activity_ents = by_label.get('ACTIVITY', [])
    location_ents = by_label.get('LOCATION', [])
    if activity_ents and location_ents:
        for act in activity_ents:
            for loc in location_ents:
                span_text = text[act['end']:loc['start']]
                if "at" in span_text or "in" in span_text:  # Possible link
                    relations.append({
                        "from": act['text'],
                        "relation": "AT_LOCATION",
                        "to": loc['text']
                    })

    # Example 2: Activity on Date ("Tour on Day 1", "Lunch July 10th")
    date_ents = by_label.get('DATE', [])
    if activity_ents and date_ents:
        for act in activity_ents:
            for date in date_ents:
                # Check if entity spans are close for "on"/"for"/etc.
                between = text[act['end']:date['start']]
                if re.search(r"\bon\b|\bfor\b|\b,\b", between):
                    relations.append({
                        "from": act['text'],
                        "relation": "ON_DATE",
                        "to": date['text']
                    })

    # Example 3: Activity at Time ("Dinner at 8 PM")
    time_ents = by_label.get('TIME', [])
    if activity_ents and time_ents:
        for act in activity_ents:
            for tim in time_ents:
                between = text[act['end']:tim['start']]
                if re.search(r"\bat\b|\bin\b|\b,\b", between):
                    relations.append({
                        "from": act['text'],
                        "relation": "AT_TIME",
                        "to": tim['text']
                    })

    # More sophisticated approaches (dependency parsing, ML) can be added here.

    return relations

# CLI for quick testing
if __name__ == "__main__":
    sample_text = "Dinner at Le Jules Verne in the evening, visit Louvre Museum on Day 2."
    entities = [
        {'text': 'Dinner', 'label': 'ACTIVITY', 'start': 0, 'end': 6},
        {'text': 'Le Jules Verne', 'label': 'LOCATION', 'start': 10, 'end': 24},
        {'text': 'evening', 'label': 'TIME', 'start': 32, 'end': 39},
        {'text': 'Louvre Museum', 'label': 'LOCATION', 'start': 48, 'end': 62},
        {'text': 'Day 2', 'label': 'DATE', 'start': 66, 'end': 72}
    ]
    print(extract_relations(sample_text, entities))
