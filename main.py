"""
FastAPI app that serves your existing static site (./web) and exposes
a data API at /api/insights.

Folder layout expected (matches what you already have):

    main.py
    requirements.txt
    web/
        index.html
        style.css
        script.js
    data/
        insights.json      <- optional, only needed if you use /api/insights

Run:
    pip install -r requirements.txt
    uvicorn main:app --reload

Then open http://127.0.0.1:8000
"""

import json
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles

BASE_DIR = Path(__file__).resolve().parent
WEB_DIR = BASE_DIR / "web"
DATA_FILE = BASE_DIR / "data" / "insights.json"

app = FastAPI(title="My Site API")

# ---------------------------------------------------------------------------
# Define API routes BEFORE mounting the static site, since the static mount
# at "/" acts as a catch-all and would otherwise shadow anything below it.
# ---------------------------------------------------------------------------


@app.get("/api/insights")
def get_insights():
    """Return JSON data for the frontend to fetch (e.g. via fetch('/api/insights'))."""
    if not DATA_FILE.exists():
        raise HTTPException(status_code=404, detail="insights.json not found")
    with open(DATA_FILE, "r") as f:
        return json.load(f)


@app.get("/api/health")
def health():
    return {"status": "ok"}


# ---------------------------------------------------------------------------
# Serve the existing web/ folder as-is: index.html at "/", and style.css,
# script.js, and anything else in that folder at their own paths
# (e.g. /style.css, /script.js) — no code changes needed in your HTML.
# This must be mounted LAST.
# ---------------------------------------------------------------------------
app.mount("/", StaticFiles(directory=WEB_DIR, html=True), name="web")