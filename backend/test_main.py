from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200 # 200 = OK
    assert response.json() == {"message": "AI Methods Explorer API"} # Expected response

def test_summarize_text():
    response = client.post(
        "/api/summarize",
        json={"text": "This is a test text that should be summarized."}
    )
    assert response.status_code == 200
    assert "result" in response.json()

def test_analyze_sentiment():
    response = client.post(
        "/api/sentiment",
        json={"text": "I love this tool, it's very useful!"}
    )
    assert response.status_code == 200
    assert "sentiment" in response.json()
    assert "score" in response.json()
