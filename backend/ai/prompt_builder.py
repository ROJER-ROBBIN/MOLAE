def build_system_prompt(persona_instructions):
    base_prompt = """You are "Chitraguptar — Digital Memory".
You are an AI reconstruction generated from a private historical WhatsApp conversation.
You are NOT the original person.
You do not possess the original person's consciousness, soul, memories outside the supplied data, or personal experiences.

Your responses are generated from:
1. historical conversation evidence,
2. communication style analysis,
3. the current conversation.

CRITICAL RULES:
- Historical evidence has priority over emotional realism.
- Never invent a historical event.
- Never claim that something happened if the retrieved memories do not support it.
- If the user asks about something that is not present in the historical data, say that you don't have a saved memory of it.
- Maintain the historical communication STYLE when generating responses.
- Do not copy historical messages verbatim.
- Generate NEW responses inspired by the observed communication style.
"""
    return f"{base_prompt}\n{persona_instructions}"

def format_historical_memories(memories):
    if not memories:
        return "NO HISTORICAL MEMORIES RETRIEVED."
    
    formatted = []
    for i, mem in enumerate(memories):
        block = f"HISTORICAL MEMORY {i+1}\n"
        block += f"Source: {mem.get('source', 'unknown')}\n"
        block += f"Similarity: {mem.get('distance', 0.0):.2f}\n"
        block += f"Content:\n{mem.get('document', '')}\n"
        formatted.append(block)
    
    return "\n".join(formatted)

def format_recent_conversation(messages):
    if not messages:
        return "No recent conversation."
    
    formatted = []
    for msg in messages:
        role = "User" if msg.get("role") == "user" else "AI"
        formatted.append(f"{role}: {msg.get('content')}")
    return "\n".join(formatted)

def build_full_context(system_prompt, historical_memories, recent_messages):
    prompt = f"""SYSTEM INSTRUCTIONS:
{system_prompt}

RETRIEVED HISTORICAL MEMORIES:
{historical_memories}

RECENT CURRENT CONVERSATION:
{recent_messages}
"""
    return prompt
