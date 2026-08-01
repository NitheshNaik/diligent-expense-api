# Smart Expense Tracker

## What I Built

A REST API for tracking personal expenses, built with Python and FastAPI. It supports creating expenses, listing them with optional category filtering, calculating totals, and deleting records. Data is stored in-memory (no database), making it easy to run locally with zero setup beyond Python dependencies.

## Install

```bash
# Create and activate a virtual environment
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS / Linux

# Install dependencies
pip install -r requirements.txt
```

## Run

```bash
uvicorn src.main:app --reload
```

The API will be available at **http://127.0.0.1:8000**.  
Interactive docs (Swagger UI) are at **http://127.0.0.1:8000/docs**.

## Test

```bash
python -m pytest tests/ -v
```
