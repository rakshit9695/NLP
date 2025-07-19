"""
src/phase4_scoring/diversity_scorer.py

Evaluates the diversity of an itinerary in terms of activity/category variety.
Higher diversity yields a better score.
"""

from collections import Counter

def score_diversity(itinerary_info: dict) -> float:
    """
    Scores itinerary diversity [0.0, 1.0].
    Uses activities, categories, and tags found in itinerary_info.

    Args:
        itinerary_info (dict): Should include a list of visited places, each with 'category' and/or 'tags'.

    Returns:
        float: Diversity score (higher = more diverse)
    """
    # Defensive: If nothing, score is low
    visited_places = itinerary_info.get('visited_places', [])
    if not visited_places or len(visited_places) < 2:
        return 0.0

    # Extract all categories/tags
    categories = set()
    all_tags = set()
    for place in visited_places:
        if 'category' in place and place['category']:
            categories.add(place['category'].lower())
        if 'tags' in place:
            # tags could be JSON-encoded string, list, etc.
            tags = place['tags']
            if isinstance(tags, str):
                try:
                    import json
                    tags = json.loads(tags)
                except Exception:
                    tags = [tags]
            for tag in tags:
                all_tags.add(tag.lower())

    n_cat = len(categories)
    n_tag = len(all_tags)

    # Diversity heuristics: max diversity if 5+ unique categories or 8+ unique tags
    cat_score = min(n_cat / 5, 1.0)
    tag_score = min(n_tag / 8, 1.0)

    # Weight categories higher since they're broader, but sum both (can be tweaked/tuned)
    diversity_score = 0.7 * cat_score + 0.3 * tag_score

    return round(diversity_score, 3)

# --- CLI demo ---
if __name__ == "__main__":
    example_info = {
        'visited_places': [
            {'name': 'Taj Mahal', 'category': 'Historical Monument', 'tags': ['unesco', 'architecture']},
            {'name': 'Gateway of India', 'category': 'Monument', 'tags': ['waterfront', 'historical']},
            {'name': 'Hawa Mahal', 'category': 'Palace', 'tags': ['heritage', 'jaipur']},
            {'name': 'MG Road', 'category': 'Shopping Area', 'tags': ['market', 'shopping']},
            {'name': 'Bandipur National Park', 'category': 'Nature Reserve', 'tags': ['wildlife', 'nature']}
        ]
    }
    print("Diversity Score:", score_diversity(example_info))
