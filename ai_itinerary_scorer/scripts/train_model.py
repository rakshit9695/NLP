"""
scripts/train_model.py

Utility for setting up the AI Itinerary Scorer project:
- (Re)initialize the DB,
- Load Indian places from a CSV,
- Train custom NER if you wish (stub provided).
"""

import argparse
import sys

from src.phase3_database.famous_places_db import FamousPlacesDB
from src.phase2_nlp.custom_ner import train_custom_ner

#############################
# CSV loader function
#############################

import csv
def load_indian_places_from_csv(csv_file_path: str):
    db = FamousPlacesDB()
    count = 0
    with open(csv_file_path, encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            # Map CSV fields to DB structure
            place_data = {
                'name': row.get('place', '').strip(),
                'description': row.get('description', '').strip(),
                'category': row.get('category', '').strip(),
                'location': row.get('address', '').strip() or row.get('landmark', '').strip(),
                'city': row.get('city', '').strip(),
                'state': '',  # You may extract state from address if desired
                'popularity_score': float(row.get('popularPlace', 0) or 0),
                'average_rating': 0.0,  # Not available
                'num_reviews': 0,       # Not available
                'typical_duration_hours': None,  # Not available
                'opening_hours': row.get('timming', '').strip() or row.get('timing', '').strip(),
                'peak_hours': '',  # Not available
                'crowd_level': '', # Not available
                'price_range': '', # Not available
                'features': row.get('special_tip', '').strip(),
                'tags': row.get('category', '').strip(),
                'phone': row.get('phone', '').strip(),
                'website': row.get('website', '').strip(),
                'latitude': row.get('latitude', '').strip(),
                'longitude': row.get('longitude', '').strip(),
            }
            db.add_place(place_data)
            count += 1
        print(f"Successfully loaded {count} places from CSV to DB.")

#############################
# Sample NER training stub
#############################

def train_ner_model():
    # This is a stub. Replace with your spaCy NER training code, e.g.:
    # train_custom_ner(training_data, output_dir)
    print("Custom NER training is not implemented. Use spaCy CLI, Prodigy, or a labeled data pipeline.")

#############################
# Main CLI
#############################

def main():
    parser = argparse.ArgumentParser(description="Setup/training utility for AI Itinerary Scorer")
    parser.add_argument("--reset-db", action="store_true", help="Reset and reinitialize the famous places DB (drops all data!)")
    parser.add_argument("--sample-db", action="store_true", help="Load the hardcoded Indian sample places (for test/demo)")
    parser.add_argument("--csv", type=str, help="CSV file to bulk-load famous Indian places.")
    parser.add_argument("--train-ner", action="store_true", help="Train (or retrain) custom NER model.")
    parser.add_argument("--all", action="store_true", help="Run --reset-db, --sample-db (and --train-ner if desired).")

    args = parser.parse_args()

    if args.all:
        print("Resetting DB, loading sample data...")
        db = FamousPlacesDB()
        if args.reset_db or args.all:
            db._initialize_database()
        db.load_sample_data()
        print("Sample data loaded.")

    if args.csv:
        print(f"Loading Indian places from: {args.csv}")
        load_indian_places_from_csv(args.csv)

    if args.train_ner:
        print("NER training requested.")
        train_ner_model()

    if args.reset_db and not args.all:
        print("Resetting (re-initializing) DB.")
        db = FamousPlacesDB()
        db._initialize_database()
        print("DB reset complete.")

    if args.sample_db and not args.all:
        db = FamousPlacesDB()
        db.load_sample_data()
        print("Sample data loaded.")

    if not (args.csv or args.train_ner or args.reset_db or args.sample_db or args.all):
        parser.print_help()

if __name__ == "__main__":
    main()
