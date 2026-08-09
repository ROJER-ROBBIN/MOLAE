from backend.ai.prompt_builder import build_system_prompt, format_historical_memories, format_recent_conversation, build_full_context
from backend.ai.validator import ResponseValidator

def test_prompt_builder():
    instructions = "Be short and casual."
    sys_prompt = build_system_prompt(instructions)
    assert "Digital Memory" in sys_prompt
    assert "Be short and casual." in sys_prompt

def test_format_historical_memories():
    memories = [
        {"source": "test_src", "distance": 0.5, "document": "hello there"}
    ]
    formatted = format_historical_memories(memories)
    assert "HISTORICAL MEMORY 1" in formatted
    assert "hello there" in formatted

def test_format_recent_conversation():
    history = [{"role": "user", "content": "hi"}, {"role": "assistant", "content": "hello"}]
    formatted = format_recent_conversation(history)
    assert "User: hi" in formatted
    assert "AI: hello" in formatted

def test_validator_pass():
    val = ResponseValidator()
    # No claims
    is_valid, fb = val.validate_response("hey what's up?", [])
    assert is_valid is True

def test_validator_rejects_unsupported_claim():
    val = ResponseValidator()
    # Makes a claim, but no memories to support it
    is_valid, fb = val.validate_response("I remember we went to the beach", [])
    assert is_valid is False
    assert fb == "I don't have a saved memory of that."

def test_validator_accepts_supported_claim():
    val = ResponseValidator()
    memories = [{"document": "went to the beach last week"}]
    is_valid, fb = val.validate_response("I remember we went to the beach", memories)
    assert is_valid is True
