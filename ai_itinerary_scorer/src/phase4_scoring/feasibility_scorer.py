"""
src/phase4_scoring/feasibility_scorer.py

Scores the feasibility of an itinerary:
- Are time/location jumps reasonable?
- Do activities fit within typical durations and place opening hours?
- Is the pacing realistic?

Assumes 'itinerary_info["visited_places"]' is a list of DB place dicts in order of visit, with optional time info.
"""

from datetime import datetime
from typing import Dict

def score_feasibility(itinerary_info: Dict) -> float:
    """
    Analyzes the plausibility of the itinerary flow (travel time, durations, operating hours).
    For now, uses heuristic rules; ready to integrate with real-world APIs (Google Maps, etc.).

    Args:
        itinerary_info (dict): Should contain 'visited_places', in visit order.
            Each 'visited_place' can have:
                - 'city', 'state'
                - 'typical_duration_hours'
                - 'opening_hours' (e.g. "09:00-17:00")
                - 'planned_time' and/or 'planned_day' (optional, from NLP)
            
    Returns:
        float: Feasibility score [0.0, 1.0]
    """
    visited_places = itinerary_info.get('visited_places', [])
    if not visited_places or len(visited_places) < 2:
        return 1.0 if visited_places else 0.0 # Trivial case

    # Heuristics for common issues:
    max_travel_penalty = 0.2
    max_opening_penalty = 0.2
    max_duration_penalty = 0.2
    max_pacing_penalty = 0.2   # Too much per day

    penalties = 0.0

    # 1. Excessive city/state hops? (crude: if city/state changes > number of days)
    last_city = visited_places[0].get('city')
    last_state = visited_places[0].get('state')
    city_hops = sum(1 for p in visited_places if p.get('city') != last_city)
    state_hops = sum(1 for p in visited_places if p.get('state') != last_state)
    if city_hops + state_hops > max(1, len(visited_places) // 2):
        penalties += max_travel_penalty
    
    # 2. Operating hours: planned_time (if present) within opening_hours? (stub)
    for place in visited_places:
        planned_time = place.get('planned_time')  # e.g., "14:30"
        opening_hours = place.get('opening_hours')
        if planned_time and opening_hours:
            try:
                open_str, close_str = opening_hours.split('-')
                open_dt = datetime.strptime(open_str.strip(), "%H:%M")
                close_dt = datetime.strptime(close_str.strip(), "%H:%M")
                plan_dt = datetime.strptime(planned_time.strip(), "%H:%M")
                if not (open_dt <= plan_dt <= close_dt):
                    penalties += max_opening_penalty / len(visited_places)
            except Exception:
                pass  # ignore malformed data
    
    # 3. Activity duration: can planned/typical durations fit together? (stub, more places in a small number of hours = lower score)
    total_duration = sum(float(p.get('typical_duration_hours') or 0.0) for p in visited_places)
    planned_total_hours = itinerary_info.get('planned_total_hours')  # e.g., parsed from input
    if planned_total_hours and total_duration > planned_total_hours:
        penalties += max_duration_penalty
    elif total_duration > 10 * len(set(p.get('planned_day', 1) for p in visited_places)):
        penalties += max_duration_penalty

    # 4. Pacing: Too many items in one day (say, more than 5 per day)
    days = [p.get('planned_day', 1) for p in visited_places]
    from collections import Counter
    place_per_day = Counter(days)
    if any(v > 5 for v in place_per_day.values()):
        penalties += max_pacing_penalty

    # Clamp penalties to [0, 0.8]; 0 = perfect, 0.8 or more = almost infeasible
    penalties = min(penalties, 0.8)
    final_score = round(1.0 - penalties, 3)
    return final_score

# --- CLI demo ---
if __name__ == "__main__":
    test_info = {
        "visited_places": [
            {'name': 'Taj Mahal', 'city': 'Agra', 'state': 'Uttar Pradesh', 'typical_duration_hours': 2, 'opening_hours': '06:00-19:00', 'planned_time': '12:00', 'planned_day': 1},
            {'name': 'Gateway of India', 'city': 'Mumbai', 'state': 'Maharashtra', 'typical_duration_hours': 1, 'opening_hours': '24 hours', 'planned_time': '15:00', 'planned_day': 1},
            {'name': 'Hawa Mahal', 'city': 'Jaipur', 'state': 'Rajasthan', 'typical_duration_hours': 1.5, 'opening_hours': '09:00-17:00', 'planned_time': '16:00', 'planned_day': 1},
        ],
        "planned_total_hours": 5
    }
    print("Feasibility Score:", score_feasibility(test_info))
