"""
src/phase6_deployment/api_server.py

FastAPI app for AI-powered itinerary scoring.
Supports text and file (PDF/DOCX) ingestion.
"""

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from typing import List

import os
import tempfile

# PHASE 1: File handling & extraction
from src.phase1_preprocessing.document_parser import parse_document

# PHASE 2: NLP/NER/relations (entities for now)
from src.phase2_nlp.entity_extractor import extract_entities
from src.phase2_nlp.relation_extractor import extract_relations
from src.phase2_nlp.sentiment_analyzer import SentimentAnalyzer

# PHASE 3: DB and semantic matching
from src.phase3_database.famous_places_db import FamousPlacesDB
from src.phase3_database.matching_engine import PlaceMatcher

# PHASE 4: Scoring
from src.phase4_scoring.scoring_engine import score_itinerary

app = FastAPI(
    title="AI Itinerary Scorer (India)",
    description="Uploads itineraries in PDF/DOCX or text, returns actionable AI scoring & feedback",
    version="0.1"
)

# --- Required singletons ---
db_singleton = FamousPlacesDB()
db_singleton.load_sample_data()
matcher = PlaceMatcher(db_singleton)
sentiment_analyzer = SentimentAnalyzer()

# --- Utility for end-to-end itinerary info aggregation ---
def itinerary_info_from_entities(text: str, entities: List[dict]) -> dict:
    """
    Given extracted entities, use semantic matcher to fetch full place info.
    Returns info dict for scoring.
    """
    visited_places = []
    for ent in entities:
        if ent['label'] == "LOCATION":
            matches = matcher.match_entity_to_place(ent['text'], top_k=1)
            if matches:
                place_id, sim_score = matches[0]
                place_info = matcher.get_place_info(place_id)
                if place_info:
                    place_info = dict(place_info)  # SQLite Row -> dict
                    # Place sim_score in for debugging/metrics (optional)
                    place_info['semantic_match_score'] = sim_score
                    visited_places.append(place_info)
    # Sentiment/Preferences placeholder
    sentiment = sentiment_analyzer.analyze_sentiment(text)
    preference_alignment = 0.8 if sentiment['label'] == 'positive' else 0.6 if sentiment['label'] == 'neutral' else 0.3

    return {
        "visited_places": visited_places,
        "preference_alignment": preference_alignment,
    }

# --- API Endpoints ---

@app.post("/score")
def score_text_itinerary(request: dict):
    """
    Score plain text itinerary. Returns all scoring subcomponents and suggestions.
    """
    text = request.get("text")
    if not text:
        raise HTTPException(status_code=400, detail="Missing 'text' in request")
    entities = extract_entities(text)
    itinerary_info = itinerary_info_from_entities(text, entities)
    result = score_itinerary(itinerary_info)
    return JSONResponse(content=result)

@app.post("/upload")
async def upload_and_score(file: UploadFile = File(...)):
    """
    Upload a document (PDF/DOCX), auto-extract, parse, score and get feedback.
    """
    # Save to temporary file on disk
    ext = os.path.splitext(file.filename)[-1].lower()
    if ext not in [".pdf", ".docx"]:
        raise HTTPException(status_code=400, detail="Unsupported file type")
    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmpf:
        tmpf.write(await file.read())
        tmp_path = tmpf.name

    try:
        text = parse_document(tmp_path)
        entities = extract_entities(text)
        itinerary_info = itinerary_info_from_entities(text, entities)
        result = score_itinerary(itinerary_info)
    finally:
        os.unlink(tmp_path)  # Clean up

    return JSONResponse(content=result)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/docs_link")
def docs_redirect():
    return {"docs": "/docs"}

# --- Main block for Uvicorn ---
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
