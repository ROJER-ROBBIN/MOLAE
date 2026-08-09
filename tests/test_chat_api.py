import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from backend.main import app
from backend.api.chat import sessions

client = TestClient(app)

def test_chat_empty_message():
    response = client.post("/api/chat", json={"message": ""})
    assert response.status_code == 400
    assert "Message cannot be empty" in response.json()["detail"]

def test_missing_api_key_error():
    # If GEMINI_API_KEY is not in env (which it isn't in test context without .env loaded with a real key), 
    # it should return 503 Configuration Error.
    # We will explicitly mock os.getenv to return None for GEMINI_API_KEY
    with patch("os.getenv", side_effect=lambda k, d=None: None if k == "GEMINI_API_KEY" else d):
        response = client.post("/api/chat", json={"message": "Hello"})
        assert response.status_code == 503
        assert "Configuration Error" in response.json()["detail"]

@patch("backend.api.chat.get_llm_provider")
@patch("backend.ai.retrieval.MemoryRetrievalEngine.semantic_search")
def test_chat_mocked_responses(mock_search, mock_get_llm):
    # Setup mock LLM
    mock_llm = MagicMock()
    mock_get_llm.return_value = mock_llm
    mock_search.return_value = [{"document": "studied physics exam together group study"}]
    
    # A. Short casual message
    mock_llm.generate_response.return_value = "Enna da"
    res = client.post("/api/chat", json={"message": "Hi"})
    assert res.status_code == 200
    assert res.json()["response"] == "Enna da"
    
    # B. Complex question
    complex_response = "I remember we studied for the physics exam together. It was really hard but we managed to pass by doing group study every night."
    mock_llm.generate_response.return_value = complex_response
    res = client.post("/api/chat", json={"message": "Do you remember how we passed physics?"})
    assert res.status_code == 200
    assert res.json()["response"] == complex_response
    
    # C. Emotional/serious message
    emotional_response = "I miss you too da. Please take care of yourself and don't worry too much about the past."
    mock_llm.generate_response.return_value = emotional_response
    res = client.post("/api/chat", json={"message": "I really miss you these days."})
    assert res.status_code == 200
    assert res.json()["response"] == emotional_response
    
    # D. Unsupported historical memory (Validator should catch it)
    # Give a response that claims an unsupported memory
    mock_llm.generate_response.return_value = "I remember going to Japan with you in 2019."
    # We also need to mock the semantic search to return nothing, or just let it return real db results which won't contain "Japan"
    res = client.post("/api/chat", json={"message": "Did we go to Japan?"})
    assert res.status_code == 200
    # The validator should fallback because it claims a memory not in the DB
    assert res.json()["response"] == "I don't have a saved memory of that."

@patch("backend.api.chat.get_llm_provider")
def test_invalid_api_key_error(mock_get_llm):
    mock_llm = MagicMock()
    # Simulate the upstream error when key is invalid
    mock_llm.generate_response.side_effect = RuntimeError("API_KEY_INVALID")
    mock_get_llm.return_value = mock_llm
    
    res = client.post("/api/chat", json={"message": "Hello"})
    assert res.status_code == 502
    assert "Upstream Authentication Error" in res.json()["detail"]
