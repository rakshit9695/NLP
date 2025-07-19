"""
scripts/deploy_model.py

Launches the AI Itinerary Scorer FastAPI server.
Optionally initializes the DB or loads places CSV before launch.
"""

import argparse
import os
import sys
import subprocess

def main():
    parser = argparse.ArgumentParser(description="Deploy and run the AI Itinerary Scorer API server.")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host for API server (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=8000, help="Port for API server (default: 8000)")
    parser.add_argument("--reload", action="store_true", help="Enable autoreload for development.")
    parser.add_argument("--csv", type=str, help="Optionally load a CSV of places before starting the API.")

    args = parser.parse_args()

    # Optionally load CSV data before server start
    if args.csv:
        print(f"Importing places from CSV: {args.csv}")
        from train_model import load_indian_places_from_csv
        load_indian_places_from_csv(args.csv)
        print("CSV import complete.")

    # Show helpful info
    print("Launching AI Itinerary Scorer API server...")
    print(f"Host: {args.host} | Port: {args.port} | Reload: {args.reload}\n")
    print("API Docs: http://{}:{}/docs\n".format(args.host, args.port))

    # Actually launch the FastAPI/Uvicorn server
    module_path = "src.phase6_deployment.api_server:app"
    uvicorn_cmd = [
        sys.executable, "-m", "uvicorn", module_path,
        "--host", args.host,
        "--port", str(args.port)
    ]
    if args.reload:
        uvicorn_cmd.append("--reload")

    subprocess.run(uvicorn_cmd)

if __name__ == "__main__":
    main()
