from fastapi.testclient import TestClient
import pytest
import os
import sqlite3
from unittest.mock import patch
from main import app

# Patch sqlite3.connect to use an in-memory database before importing main
# This ensures all database operations use the in-memory database
with patch('sqlite3.connect', return_value=sqlite3.connect(':memory:')):
    from main import app, init_db

client = TestClient(app)

init_db()

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200 # 200 = OK
    assert response.json() == {"message": "AI Methods Explorer API"} # Expected response

def test_summarize_text():

    if not os.environ.get("HF_API_KEY"):
        pytest.skip("No HF_API_KEY environment variable set")

    response = client.post(
        "/api/summarize",
        json={"text": "This is a test text that should be summarized."}
    )
    assert response.status_code == 200
    assert "result" in response.json()

def test_analyze_sentiment():
    if not os.environ.get("HF_API_KEY"):
        pytest.skip("No HF_API_KEY environment variable set")

    test_text = "I love this tool, it's very useful!"
    response = client.post(
        "/api/sentiment",
        json={"text": test_text}
    )
    
    if response.status_code != 200:
        print(f"Response content: {response.content}")  # Debug output
        
    assert response.status_code == 200
    data = response.json()
    assert "sentiment" in data
    assert "score" in data


def test_get_methods():
    """Test getting available methods."""
    response = client.get("/api/methods")
    assert response.status_code == 200
    assert "methods" in response.json()
    methods = response.json()["methods"]
    assert len(methods) >= 2
    
    # Check for required fields in each method
    required_fields = ["id", "name", "description", "model", "endpoint"]
    for method in methods:
        for field in required_fields:
            assert field in method