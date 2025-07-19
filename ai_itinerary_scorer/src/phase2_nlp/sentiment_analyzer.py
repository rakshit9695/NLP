"""
src/phase2_nlp/sentiment_analyzer.py

Performs sentiment analysis and infers preferences from itinerary text.
Uses Hugging Face transformers pipeline optimized for CPU usage.
"""
import logging
from transformers import pipeline

logger = logging.getLogger(__name__)

class SentimentAnalyzer:
    def __init__(self, model_name: str = "cardiffnlp/twitter-roberta-base-sentiment-latest"):
        try:
            logger.info(f"Loading sentiment analysis model: {model_name}")
            self.sentiment_pipeline = pipeline(
                "sentiment-analysis",
                model=model_name,
                device=-1,  # CPU only
                return_all_scores=True
            )
            logger.info("Sentiment model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading sentiment model: {e}")
            raise

    def analyze_sentiment(self, text: str):
        if not text or not text.strip():
            return {'label': 'neutral', 'score': 0.0}
        try:
            results = self.sentiment_pipeline(text)
            if isinstance(results[0], list):
                scores = {r['label'].lower(): r['score'] for r in results[0]}
            else:
                scores = {results[0]['label'].lower(): results[0]['score']}

            # Return the label with highest score
            top_label = max(scores, key=scores.get)
            return {'label': top_label, 'score': scores[top_label]}
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {e}")
            return {'label': 'neutral', 'score': 0.0}

    def infer_preferences(self, text: str):
        """Analyze user preferences or sentiments implied in the itinerary text"""
        # Placeholder: customize preference inferencing logic here
        sentiment = self.analyze_sentiment(text)
        preferences = {}
        if sentiment['label'] == 'positive' and sentiment['score'] > 0.8:
            preferences['likes_adventure'] = 'hiking' in text.lower()
        else:
            preferences['likes_adventure'] = False
        return preferences

# Simple CLI
if __name__ == "__main__":
    sa = SentimentAnalyzer()
    test_text = "I love visiting the Eiffel Tower. Beautiful experience!"
    print(sa.analyze_sentiment(test_text))
