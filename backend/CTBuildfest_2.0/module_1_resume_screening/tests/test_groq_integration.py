import pytest
from app.ai.groq_client import groq_client
from app.config import settings

@pytest.mark.integration
def test_live_groq_connectivity():
    """Integration test verifying real Groq API connectivity using configured key."""
    if not groq_client.is_available():
        pytest.skip("GROQ_API_KEY not configured or offline")

    result = groq_client.call_structured(
        system_prompt="You are a JSON assistant. Respond with JSON containing status 'ok'.",
        user_prompt="Ping",
        temperature=0.1
    )
    assert isinstance(result, dict)
    assert len(result) > 0
