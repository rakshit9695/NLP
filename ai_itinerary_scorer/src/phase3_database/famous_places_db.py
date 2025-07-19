"""
src/phase3_database/famous_places_db.py

SQLite Database management for famous places in India, including embeddings.
Optimized for itinerary matching and scoring.
"""

import sqlite3
import json
import logging
from typing import List, Dict, Optional, Tuple
import numpy as np
import pickle
from pathlib import Path
from config.settings import DB_PATH

logger = logging.getLogger(__name__)

class FamousPlacesDB:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self.conn = None
        self.embeddings_generator = None
        self._initialize_database()

    def _initialize_database(self):
        """Initialize DB with places table and embeddings table (India-only data)."""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row

        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS places (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                description TEXT,
                category TEXT,
                location TEXT,
                city TEXT,
                state TEXT,
                popularity_score REAL DEFAULT 0.0,
                average_rating REAL DEFAULT 0.0,
                num_reviews INTEGER DEFAULT 0,
                typical_duration_hours REAL,
                opening_hours TEXT,
                peak_hours TEXT,
                crowd_level TEXT,
                price_range TEXT,
                features TEXT,
                tags TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS embeddings (
                place_id INTEGER PRIMARY KEY,
                embedding BLOB,
                dimension INTEGER,
                model_name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(place_id) REFERENCES places(id)
            )
        ''')
        self.conn.commit()
        logger.info("Database initialized (India-only places schema).")

    def set_embeddings_generator(self, generator):
        self.embeddings_generator = generator

    def add_place(self, place_data: Dict) -> int:
        """Add a place to DB and compute/store its embedding if description is available."""
        features_json = json.dumps(place_data.get('features', []))
        tags_json = json.dumps(place_data.get('tags', []))

        cursor = self.conn.execute('''
            INSERT OR IGNORE INTO places (
                name, description, category, location, city, state,
                popularity_score, average_rating, num_reviews, typical_duration_hours,
                opening_hours, peak_hours, crowd_level, price_range, features, tags
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            place_data.get('name'), place_data.get('description'), place_data.get('category'),
            place_data.get('location'), place_data.get('city'), place_data.get('state'),
            place_data.get('popularity_score', 0.0), place_data.get('average_rating', 0.0),
            place_data.get('num_reviews', 0), place_data.get('typical_duration_hours'),
            place_data.get('opening_hours'), place_data.get('peak_hours'),
            place_data.get('crowd_level'), place_data.get('price_range'),
            features_json, tags_json
        ))
        place_id = cursor.lastrowid
        self.conn.commit()

        # Store embedding if generator and description are set
        if self.embeddings_generator and place_data.get('description'):
            self._add_embedding(place_id, place_data['description'])

        return place_id

    def _add_embedding(self, place_id: int, description: str):
        embedding = self.embeddings_generator.generate_embeddings(description)
        if len(embedding) > 0:
            vec = embedding[0]
            blob = pickle.dumps(vec)
            self.conn.execute('''
                INSERT OR REPLACE INTO embeddings (place_id, embedding, dimension, model_name)
                VALUES (?, ?, ?, ?)
            ''', (place_id, blob, len(vec), self.embeddings_generator.model_name))
            self.conn.commit()
            logger.info(f"Stored embedding for place ID {place_id}.")

    def get_place_by_id(self, place_id: int) -> Optional[Dict]:
        cursor = self.conn.execute('SELECT * FROM places WHERE id = ?', (place_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def get_all_embeddings(self) -> Tuple[np.ndarray, List[int]]:
        cursor = self.conn.execute('SELECT place_id, embedding FROM embeddings ORDER BY place_id')
        embeddings = []
        place_ids = []
        for place_id, blob in cursor.fetchall():
            vec = pickle.loads(blob)
            embeddings.append(vec)
            place_ids.append(place_id)
        if embeddings:
            return np.array(embeddings), place_ids
        return np.array([]), []

    def load_sample_data(self):
        """
        Load sample famous places from India into the database.
        Extend or replace with a real CSV/JSON load for production.
        """
        sample_places = [
            {
                'name': 'Taj Mahal',
                'description': 'Iconic mausoleum in Agra, India, and major historic monument.',
                'category': 'Historical Monument',
                'location': 'Agra, Uttar Pradesh',
                'city': 'Agra',
                'state': 'Uttar Pradesh',
                'popularity_score': 9.7,
                'average_rating': 4.7,
                'num_reviews': 105000,
                'typical_duration_hours': 2.0,
                'opening_hours': '06:00-19:00',
                'peak_hours': '09:00-12:00',
                'crowd_level': 'High',
                'price_range': '₹50-250',
                'features': ['guided tours', 'garden', 'photography'],
                'tags': ['architecture', 'mausoleum', 'unesco']
            },
            {
                'name': 'Gateway of India',
                'description': 'Monument built during the British Raj in Mumbai.',
                'category': 'Monument',
                'location': 'Mumbai, Maharashtra',
                'city': 'Mumbai',
                'state': 'Maharashtra',
                'popularity_score': 8.9,
                'average_rating': 4.5,
                'num_reviews': 78000,
                'typical_duration_hours': 1.0,
                'opening_hours': '24 hours',
                'peak_hours': '10:00-17:00',
                'crowd_level': 'High',
                'price_range': 'Free',
                'features': ['sea view', 'historic site'],
                'tags': ['gateway', 'waterfront', 'historical']
            },
            {
                'name': 'Hawa Mahal',
                'description': 'Palace in Jaipur known as the Palace of Winds.',
                'category': 'Palace',
                'location': 'Jaipur, Rajasthan',
                'city': 'Jaipur',
                'state': 'Rajasthan',
                'popularity_score': 8.5,
                'average_rating': 4.3,
                'num_reviews': 64000,
                'typical_duration_hours': 1.5,
                'opening_hours': '09:00-17:00',
                'peak_hours': '11:00-14:00',
                'crowd_level': 'Medium',
                'price_range': '₹50-100',
                'features': ['historic architecture', 'photography'],
                'tags': ['palace', 'jaipur', 'heritage']
            }
        ]

        for place in sample_places:
            self.add_place(place)
        logger.info("Sample Indian famous places loaded into DB.")

    def close(self):
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed.")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
