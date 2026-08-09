from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict
import uuid
import os

from backend.ai.retrieval import retrieval_engine
from backend.ai.persona import load_persona, get_style_instructions
from backend.ai.prompt_builder import build_system_prompt, format_historical_memories, format_recent_conversation, build_full_context
from backend.ai.llm import get_llm_provider
from backend.ai.validator import ResponseValidator

router = APIRouter()

# Simple in-memory session storage for Phase 6
# Format: { session_id: [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}] }
sessions: Dict[str, List[Dict[str, str]]] = {}

# Load reusable models/resources once
persona_profile = load_persona()
persona_instructions = get_style_instructions(persona_profile)
system_prompt = build_system_prompt(persona_instructions)
validator = ResponseValidator()

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    session_id: str
    response: str
    mode: str
    source: str
    retrieved_memories: Optional[List[dict]] = None

@router.post("", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest):
    if not req.message or not req.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty.")
        
    session_id = req.session_id or str(uuid.uuid4())
    if session_id not in sessions:
        sessions[session_id] = []
        
    # Get recent conversation (limit to last 10 messages to avoid context bloat)
    recent_history = sessions[session_id][-10:]
    
    # 1. Retrieve Historical Memories
    top_k = int(os.getenv("MEMORY_TOP_K", 5))
    try:
        memories = retrieval_engine.semantic_search(req.message, top_k=top_k)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Memory Retrieval Error: {str(e)}")
        
    formatted_memories = format_historical_memories(memories)
    formatted_history = format_recent_conversation(recent_history)
    
    # 2. Build Context
    # Add current message to context
    current_prompt = build_full_context(system_prompt, formatted_memories, formatted_history)
    
    # 3. Call LLM
    try:
        llm = get_llm_provider()
        raw_response = llm.generate_response(current_prompt, f"User: {req.message}")
    except ValueError as ve:
        # e.g., missing API key
        raise HTTPException(status_code=503, detail=str(ve))
    except RuntimeError as re:
        err_msg = str(re).lower()
        print(f"--- GEMINI UPSTREAM ERROR ---\n{str(re)}\n-----------------------------")
        if "api_key" in err_msg or "unauthenticated" in err_msg or "invalid" in err_msg:
            raise HTTPException(status_code=502, detail="Upstream Authentication Error: Invalid GEMINI_API_KEY.")
        if "429" in err_msg or "resource_exhausted" in err_msg or "quota" in err_msg:
            raise HTTPException(status_code=429, detail="Upstream Quota Error: Gemini Rate Limit Exceeded (429).")
        raise HTTPException(status_code=502, detail=str(re))
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred during generation.")
        
    # 4. Validate Response
    is_valid, fallback = validator.validate_response(raw_response, memories)
    final_response = raw_response if is_valid else fallback
    
    # 5. Update Memory
    sessions[session_id].append({"role": "user", "content": req.message})
    sessions[session_id].append({"role": "assistant", "content": final_response})
    
    return ChatResponse(
        session_id=session_id,
        response=final_response,
        mode="digital_reconstruction",
        source="ai_reconstruction",
        retrieved_memories=memories # Included for development/debugging as specified
    )
