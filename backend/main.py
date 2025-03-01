import json
import traceback
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import os
from dotenv import load_dotenv
import sqlite3
from contextlib import asynccontextmanager, contextmanager
from typing import Optional

# Load environment variables
load_dotenv()

# Configures database path - allow customization via environment variable
# Helps in testing where file paths might be restricted
DATABASE_URL = os.environ.get('DATABASE_URL', 'ai-explorer.db')

def init_db():
    # Make sure the directory exists if using a path with directories
    if DATABASE_URL != ':memory:' and '/' in DATABASE_URL:
        os.makedirs(os.path.dirname(DATABASE_URL), exist_ok=True)

    try:
        with sqlite3.connect(DATABASE_URL) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS requests (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    endpoint TEXT NOT NULL,
                    input_text TEXT NOT NULL,
                    result TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
        print(f"Database successfully initialized at {DATABASE_URL}")
    except Exception as e:
        print(f"Error initializing database: {str(e)}")
        print(traceback.format_exc())
        # Continue without failing - if database is not critical

@contextmanager
def get_db():
    """Context manager for db connections."""
    try:
        conn = sqlite3.connect(DATABASE_URL)
        yield conn
    except Exception as e:
        print(f"Database connection error: {str(e)}")
        print(traceback.format_exc())
        raise
    finally:
        if 'conn' in locals() and conn:
            conn.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    init_db()
    yield
    # Shutdown, cleanup if needed

# Initialize FastAPI with lifespan function
app = FastAPI(title="AI Methods Explorer", lifespan=lifespan)

# Configure CORS, allowing requests from the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define data models
class TextInput(BaseModel):
    text: str

class AIResponse(BaseModel):
    endpoint: str
    input_text: str
    result: str

def log_request(db, endpoint: str, input_text: str, result: str):
    try:
        cursor = db.cursor()
        cursor.execute("""
            INSERT INTO requests (endpoint, input_text, result)
            VALUES (?, ?, ?)
        """, (endpoint, input_text, result)
        )
        db.commit()
    except Exception as e:
        print(f"Error logging request: {str(e)}")

# Root endpoint
@app.get("/")
def read_root():
    return {"message": "AI Methods Explorer API"}

# AI Methods
# Text Summarization
@app.post("/api/summarize")
async def summarize_text(input_data: TextInput):
    # Simple integration with Hugging Face Inference API
    API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
    headers = {"Authorization": f"Bearer {os.getenv('HF_API_KEY', '')}"}
    
    try:
        response = requests.post(
            API_URL,
            headers=headers,
            json={"inputs": input_data.text, "parameters": {"max_length": 100}}
        )
        response.raise_for_status()  # This will raise an exception for HTTP errors
        result = response.json()
        if not result or not isinstance(result, list) or len(result) == 0:
            raise ValueError("Invalid response format from API")
        # TODO: Log request to db
        with get_db() as db:
            log_request(db, "summarize", input_data.text, result[0]["summary_text"])
        return {"result": result[0]["summary_text"]}
    
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"API request failed: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")
    
# Sentiment Analysis
@app.post("/api/sentiment")
async def analyze_sentiment(input_data: TextInput):
    #API_URL = "https://api-inference.huggingface.co/models/nlp-architect/sentiment-en"
    API_URL = "https://api-inference.huggingface.co/models/distilbert-base-uncased-finetuned-sst-2-english"
    headers = {"Authorization": f"Bearer {os.getenv('HF_API_KEY', '')}"}
    
    try:
        # Truncate text to 512 tokens
        input_data.text = input_data.text[:512]
        response = requests.post(
            API_URL,
            headers=headers,
            json={"inputs": input_data.text}
        )
        response.raise_for_status()
        sentiment_data = response.json()[0]
        if not sentiment_data:
            raise ValueError("No sentiment data returned from API.")

        # Extract sentiment with highest score
        if isinstance(sentiment_data, list):
            # Sort by score
            sentiment_data = sorted(sentiment_data, key=lambda x: x["score"], reverse=True)[0]
        
        result = {
            "sentiment": sentiment_data["label"],
            "score": sentiment_data["score"]
        }
        # TODO: Log request to db
        with get_db() as db:
            log_request(db, "sentiment", input_data.text, json.dumps(result))
        return result
    except requests.exceptions.RequestException as e:   # Catch all requests exceptions
        if "413" in str(e):  # Payload Too Large
            raise HTTPException(status_code=400, detail="Text is too long. Please use a shorter text (maximum 500 words).")
        raise HTTPException(status_code=500, detail=f"API request failed: {str(e)}")
    except Exception as e:  # Catch all other exceptions
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")
    
# Get available AI methods
@app.get("/api/methods")
async def get_available_methods():
    return {
        "methods": [
            {
                "id": "summarize",
                "name": "Text Summarization",
                "description": "Condenses long text into a shorter summary while preserving key information.",
                "model": "facebook/bart-large-cnn",
                "endpoint": "/api/summarize"
            },
            {
                "id": "sentiment",
                "name": "Sentiment Analysis",
                "description": "Analyzes the sentiment, emotional tone of a text (positive/negative) and returns a score.",
                "model": "distilbert-base-uncased-finetuned-sst-2-english",
                "endpoint": "/api/sentiment"}
        ]
    }

# TODO: Recent API usage history
@app.get("/api/history")
async def get_request_history(limit: int = 10):
    with get_db() as db:
        cursor = db.cursor()
        cursor.execute(
            "SELECT endpoint, input_text, result, timestamp FROM requests ORDER BY timestamp DESC LIMIT ?",
            (limit,)
        )
        records = cursor.fetchall()
        
        return {
            "history": [
                {
                    "endpoint": record[0],
                    "input_text": record[1],
                    "result": record[2],
                    "timestamp": record[3]
                }
                for record in records
            ]
        }