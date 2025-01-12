

import pytest
from code_assist.providers import call_openai, call_anthropic, call_gemini

def test_openai():
    prompt = "How do I reverse a string in Python?"
    response = call_openai(prompt)
    assert response is not None
    assert "reverse" in response.lower()

def test_anthropic():
    prompt = "How do I reverse a string in Python?"
    response = call_anthropic(prompt)
    assert response is not None
    assert "reverse" in response.lower()

def test_gemini():
    prompt = "How do I reverse a string in Python?"
    response = call_gemini(prompt)
    assert response is not None
    assert "reverse" in response.lower()

# Test model loading (ensure models are available in the provided paths)
def test_model_loading():
    model_path = "path_to_local_model"
    assert load_model(model_path)
