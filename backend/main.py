from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize FastAPI
app = FastAPI(title="AI Methods Explorer")

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