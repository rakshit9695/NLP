"""
src/phase2_nlp/embeddings_generator.py

Generates semantic embeddings using Sentence-BERT (SBERT).
Optimized for CPU usage with lightweight SBERT models like "all-MiniLM-L6-v2".
"""

from sentence_transformers import SentenceTransformer
import logging
from config.settings import EMBEDDING_MODEL_NAME

logger = logging.getLogger(__name__)

class EmbeddingsGenerator:
    def __init__(self, model_name: str = EMBEDDING_MODEL_NAME):
        self.model_name = model_name
        self.model = None
        self.load_model()

    def load_model(self):
        try:
            logger.info(f"Loading SentenceTransformer model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
            logger.info("SentenceTransformer model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load SBERT model: {e}")
            raise

    def generate_embeddings(self, texts, batch_size=32):
        """
        Generate embeddings for a list of texts or a single text string.

        Args:
            texts (List[str] or str): Text(s) to embed.
            batch_size (int): Batch size for model inference.

        Returns:
            List or numpy.ndarray: Embeddings vectors.
        """

        # Normalize input
        if isinstance(texts, str):
            texts = [texts]

        if not texts:
            return []

        embeddings = self.model.encode(texts, batch_size=batch_size, show_progress_bar=False, convert_to_numpy=True)
        return embeddings

# Simple usage example / CLI
if __name__ == "__main__":
    texts = ["Visit the Eiffel Tower in Paris", "Dinner at Le Jules Verne"]
    eg = EmbeddingsGenerator()
    vectors = eg.generate_embeddings(texts)
    for i, vec in enumerate(vectors):
        print(f"Text {i}: {texts[i]}\nEmbedding shape: {vec.shape}\n")
