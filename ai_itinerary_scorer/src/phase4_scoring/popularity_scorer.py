"""
src/phase4_scoring/popularity_scorer.py

Scores an itinerary based on the popularity and average ratings of the included places.
Averages the 'popularity_score' and 'average_rating' fields from DB for all visited places.
"""

from typing import Dict

def score_popularity(itinerary_info: Dict) -> float:
    """
    Scores popularity for an itinerary [0,1] (higher = more popular/famous places).

    Args:
        itinerary_info (dict): Should include 'visited_places', a list of DB place dicts,
                               each with 'popularity_score' [0-10] and 'average_rating' [0-5].

    Returns:
        float: Popularity score [0.0, 1.0]
    """
    visited_places = itinerary_info.get('visited_places', [])
    if not visited_places:
        return 0.0

    popularity_scores = []
    rating_scores = []
    for place in visited_places:
        pop = float(place.get('popularity_score', 0.0))
        rating = float(place.get('average_rating', 0.0))
        popularity_scores.append(pop)
        rating_scores.append(rating)

    # Normalize popularity (assume 10 is max in DB)
    avg_pop = sum(popularity_scores) / len(popularity_scores) / 10.0 if popularity_scores else 0.0
    # Normalize rating (5 is max typical rating)
    avg_rating = sum(rating_scores) / len(rating_scores) / 5.0 if rating_scores else 0.0

    # Weighted mean: put slightly more emphasis on normalized popularity field from DB
    final_popularity = 0.6 * avg_pop + 0.4 * avg_rating

    # Clamp to [0.0, 1.0]
    final_popularity = max(0.0, min(final_popularity, 1.0))

    return round(final_popularity, 3)

# --- CLI/test ---
if __name__ == "__main__":
    test_info = {
        "visited_places": [
            {'name': 'Taj Mahal', 'popularity_score': 9.7, 'average_rating': 4.7},
            {'name': 'Hawa Mahal', 'popularity_score': 8.5, 'average_rating': 4.3},
            {'name': 'Gateway of India', 'popularity_score': 8.9, 'average_rating': 4.5},
        ]
    }
    print("Popularity Score:", score_popularity(test_info))
