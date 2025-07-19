"""
src/phase3_database/similarity_search.py

Builds/queries a FAISS index of SBERT embeddings for India's famous places.
Returns most similar DB entry for a given query text (entity/activity).
"""

import numpy as np
import faiss
from typing import List, Tuple

from .famous_places_db import FamousPlacesDB
from src.phase2_nlp.embeddings_generator import EmbeddingsGenerator

class PlaceSimilaritySearch:
    """
    Handles semantic similarity search via SBERT embeddings + FAISS for Indian famous places.
    """
    def __init__(self, db: FamousPlacesDB, embedding_generator: EmbeddingsGenerator = None):
        self.db = db
        self.embedding_generator = embedding_generator or EmbeddingsGenerator()
        self._index = None
        self._place_ids = None
        self._build_index()

    def _build_index(self):
        """
        Builds/rebuilds the FAISS index from all stored DB embeddings.
        """
        embeddings, place_ids = self.db.get_all_embeddings()
        if embeddings.shape[0] == 0:
            raise RuntimeError("Famous places DB contains no embeddings.")
        d = embeddings.shape[1]
        self._index = faiss.IndexFlatL2(d)
        self._index.add(embeddings.astype('float32'))
        self._place_ids = place_ids

    def query_top_k(self, text: str, k: int = 1) -> List[Tuple[int, float]]:
        """
        Search for the k nearest DB places to the query text.
        Returns a list of tuples: (place_id, distance)
        """
        vec = self.embedding_generator.generate_embeddings([text])[0]
        vec = np.array([vec]).astype('float32')
        D, I = self._index.search(vec, k)
        results = []
        for rank in range(k):
            idx = int(I[0][rank])
            if 0 <= idx < len(self._place_ids):
                results.append((self._place_ids[idx], float(D[0][rank])))
        return results

# --- CLI/test/demo ---
if __name__ == "__main__":
    db = FamousPlacesDB()
    db.load_sample_data()  # loads Indian sample data
    searcher = PlaceSimilaritySearch(db)
    queries = [
        "Taj Mahal",
        "Palace of Winds Jaipur",
        "Mumbai historic waterfront",
        "ancient monument in Agra"
    ]
    for q in queries:
        print(f"\nQuery: {q}")
        for place_id, dist in searcher.query_top_k(q, k=2):
            place = db.get_place_by_id(place_id)
            print(f"  -> Match: {place['name']} (Dist={dist:.3f})")
