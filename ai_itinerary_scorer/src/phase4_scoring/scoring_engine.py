"""
src/phase4_scoring/scoring_engine.py

Combines sub-scores into a final itinerary score using configurable weights.
Provides modular scoring suitable for end-to-end API calls.
"""

from .feasibility_scorer import score_feasibility
from .popularity_scorer import score_popularity
from .diversity_scorer import score_diversity
from .flow_scorer import score_flow
from config.settings import SCORING_WEIGHTS

def score_itinerary(itinerary_info: dict) -> dict:
    """
    Computes the overall and component scores for the entire itinerary.

    Args:
        itinerary_info (dict): Contains at least 'visited_places' and other info as needed by sub-scorers.

    Returns:
        dict: {
            "overall_score": float,
            "scores": {subcomponent: float, ...},
            "grade": str,
            "recommendations": [str, ...]
        }
    """
    # Compute all component scores
    feasibility = score_feasibility(itinerary_info)
    popularity = score_popularity(itinerary_info)
    diversity = score_diversity(itinerary_info)
    flow = score_flow(itinerary_info)
    preference_alignment = itinerary_info.get("preference_alignment", 0.7)  # If not available, set to 0.7 neutral

    # Weighted sum (weights in config)
    overall = (
        feasibility * SCORING_WEIGHTS["feasibility"]
        + popularity * SCORING_WEIGHTS["popularity"]
        + diversity * SCORING_WEIGHTS["diversity"]
        + flow * SCORING_WEIGHTS["flow"]
        + preference_alignment * SCORING_WEIGHTS["preference_alignment"]
    )
    overall = round(overall, 3)

    # Simple grading logic (for user feedback)
    if overall >= 0.85:
        grade = 'Excellent'
    elif overall >= 0.7:
        grade = 'Good'
    elif overall >= 0.5:
        grade = 'Decent'
    else:
        grade = 'Needs Improvement'

    # Generate recommendations (toy/demo, customize as needed)
    recs = []
    if feasibility < 0.7:
        recs.append("Consider adjusting pacing or reducing city hops for better feasibility.")
    if popularity < 0.6:
        recs.append("Include more nationally renowned sights for a higher-impact trip.")
    if diversity < 0.5:
        recs.append("Blend different types of activities (nature, shopping, history) for richer experiences.")
    if flow < 0.5:
        recs.append("Optimize your route to avoid unnecessary backtracking.")

    return {
        "overall_score": overall,
        "scores": {
            "feasibility": feasibility,
            "popularity": popularity,
            "diversity": diversity,
            "flow": flow,
            "preference_alignment": preference_alignment
        },
        "grade": grade,
        "recommendations": recs
    }

# --- Test/CLI ---
if __name__ == "__main__":
    test_itinerary = {
        "visited_places": [
            {'name': 'Taj Mahal', 'category': 'Historical Monument', 'tags': ['unesco'], 'city': 'Agra', 'state': 'Uttar Pradesh', 'popularity_score': 9.7, 'average_rating': 4.7, 'typical_duration_hours': 2, 'planned_day': 1, 'planned_time': '12:00', 'opening_hours': '06:00-19:00'},
            {'name': 'Gateway of India', 'category': 'Monument', 'tags': ['waterfront'], 'city': 'Mumbai', 'state': 'Maharashtra', 'popularity_score': 8.9, 'average_rating': 4.5, 'typical_duration_hours': 1, 'planned_day': 1, 'planned_time': '15:00', 'opening_hours': '24 hours'},
            {'name': 'Hawa Mahal', 'category': 'Palace', 'tags': ['jaipur'], 'city': 'Jaipur', 'state': 'Rajasthan', 'popularity_score': 8.5, 'average_rating': 4.3, 'typical_duration_hours': 1.5, 'planned_day': 1, 'planned_time': '16:00', 'opening_hours': '09:00-17:00'},
        ],
        "planned_total_hours": 5,
        "preference_alignment": 0.8
    }
    from pprint import pprint
    pprint(score_itinerary(test_itinerary))
