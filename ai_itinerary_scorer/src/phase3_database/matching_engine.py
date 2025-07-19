"""
src/phase3_database/matching_engine.py

Matches extracted itinerary entities (LOCATION/ACTIVITY) to famous Indian places in the DB
using semantic similarity (embeddings + FAISS).
"""

import numpy as np
import faiss
from typing import List, Dict, Tuple, Optional

from .famous_places_db import FamousPlacesDB
from src.phase2_nlp.embeddings_generator import EmbeddingsGenerator

class PlaceMatcher:
    """
    Efficiently match user-extracted entities to their most likely famous place from the India DB.
    """
    def __init__(self, db: FamousPlacesDB, embeddings_generator: Optional[EmbeddingsGenerator] = None):
        self.db = db
        if embeddings_generator is None:
            self.embeddings_generator = EmbeddingsGenerator()
        else:
            self.embeddings_generator = embeddings_generator
        self._faiss_index = None
        self._place_ids = None
        self._build_index()  # Build on init, or when database changes

    def _build_index(self):
        """
        Loads all Indian famous places embeddings and builds or rebuilds a FAISS index.
        """
        embeddings, place_ids = self.db.get_all_embeddings()
        if embeddings.shape[0] == 0:
            raise RuntimeError("No place embeddings in the database. Did you forget to load data?")
        
        dim = embeddings.shape[1]
        self._faiss_index = faiss.IndexFlatL2(dim)   # use L2 distance; can use cosine for normalized vectors
        self._faiss_index.add(embeddings.astype('float32'))
        self._place_ids = place_ids

    def match_entity_to_place(self, entity_text: str, top_k=1) -> List[Tuple[int, float]]:
        """
        Given an entity text, finds the top_k most similar famous places in the DB.

        Returns: List of (place_id, similarity_score) tuples, sorted most-similar-first.
        """
        query_vec = self.embeddings_generator.generate_embeddings(entity_text)
        if isinstance(query_vec, list) or query_vec.ndim == 1:
            query_vec = np.array([query_vec[0] if isinstance(query_vec, list) else query_vec])
        # FAISS search
        D, I = self._faiss_index.search(query_vec.astype('float32'), top_k)
        # Lower D means more similar (it's L2 distance)
        results = []
        for rank in range(top_k):
            place_idx = I[0][rank]
            sim_score = float(D[0][rank])
            if 0 <= place_idx < len(self._place_ids):
                results.append((self._place_ids[place_idx], sim_score))
        return results

    def get_place_info(self, place_id) -> Dict:
        """
        Fetches a place's full record by its ID
        """
        return self.db.get_place_by_id(place_id)

# --- CLI/demo usage ---
if __name__ == "__main__":
    # Example usage: Try matching 'Taj Mahal', 'Qutub Minar', etc.
    db = FamousPlacesDB()
    db.load_sample_data()  # only for demo; in prod, DB is loaded during setup

    matcher = PlaceMatcher(db)
    sample_queries = [
        "Visit Taj Mahal",
        "Boat ride at Gateway of India",
        "Tour Hawa Mahal in Jaipur",
        "See the great fort"
    ]

    for query in sample_queries:
        print(f"\nQuery: {query}")
        matches = matcher.match_entity_to_place(query, top_k=2)
        for place_id, score in matches:
            info = matcher.get_place_info(place_id)
            print(f"  Matched to: {info['name']} (Score {score:.3f})")
