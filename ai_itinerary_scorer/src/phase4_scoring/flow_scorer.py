"""
src/phase4_scoring/flow_scorer.py

Scores the logical/route flow of an itinerary:
- Penalizes unnecessary geographic backtracking and zig-zags.
- Rewards itineraries that minimize cross-country hops or unnecessary repetition.
- Best flow = sequential/geographic efficiency (e.g. Delhi → Agra → Jaipur, not Delhi → Jaipur → Delhi → Agra).

Assumes 'itinerary_info["visited_places"]' is a list of DB place dicts in visit order, each with at least 'city' and 'state'.
"""

from typing import Dict, List

def _geo_tuple(place):
    """Returns (city, state) tuple for uniqueness checks and scoring."""
    return (place.get('city', '').strip().lower(), place.get('state', '').strip().lower())

def score_flow(itinerary_info: Dict) -> float:
    """
    Scores the logical flow of an itinerary based on ordered locations.

    Args:
        itinerary_info (dict): Must contain 'visited_places', in visit order.

    Returns:
        float: Flow score [0.0, 1.0]
    """
    visited_places: List[Dict] = itinerary_info.get('visited_places', [])
    if not visited_places or len(visited_places) == 1:
        return 1.0 if visited_places else 0.0 # Trivial case
    
    geo_sequence = [_geo_tuple(p) for p in visited_places]
    n_places = len(geo_sequence)

    # 1. Count back-and-forth movements ("return to previous city after visiting a different one")
    hops = 0
    last = geo_sequence[0]
    seen = [last]
    for g in geo_sequence[1:]:
        if g != last:
            hops += 1
            last = g
        seen.append(g)
    
    # 2. Penalize revisits (looping back to a city already visited), except for the first instance
    unique_cities = set()
    repeat_penalty = 0.0
    for i, g in enumerate(geo_sequence[1:], 1):
        if g in geo_sequence[:i] and g not in unique_cities:
            repeat_penalty += 0.15
            unique_cities.add(g)

    # 3. Normalize hops (ideally, n-places - 1 hops in a straight line)
    min_hops = n_places - 1
    penalty = max((hops - min_hops) * 0.12, 0.0)  # Each extra movement penalizes a bit

    # 4. Total penalty for bad flow (with revisits penalty weighted in)
    total_penalty = min(0.2 + repeat_penalty + penalty, 0.8) if hops > min_hops else min(repeat_penalty, 0.8)

    flow_score = round(1.0 - total_penalty, 3)
    return flow_score

# --- CLI demo ---
if __name__ == "__main__":
    itinerary1 = { # Good flow
        "visited_places": [
            {"name": "Qutub Minar", "city": "Delhi", "state": "Delhi"},
            {"name": "Taj Mahal", "city": "Agra", "state": "Uttar Pradesh"},
            {"name": "Hawa Mahal", "city": "Jaipur", "state": "Rajasthan"},
        ]
    }
    itinerary2 = { # "Bad" flow: backtrack to Delhi in the middle
        "visited_places": [
            {"name": "Qutub Minar", "city": "Delhi", "state": "Delhi"},
            {"name": "Hawa Mahal", "city": "Jaipur", "state": "Rajasthan"},
            {"name": "Red Fort", "city": "Delhi", "state": "Delhi"},
            {"name": "Taj Mahal", "city": "Agra", "state": "Uttar Pradesh"},
        ]
    }
    print("Flow Score (Good Flow):", score_flow(itinerary1))
    print("Flow Score (Bad Flow):", score_flow(itinerary2))
