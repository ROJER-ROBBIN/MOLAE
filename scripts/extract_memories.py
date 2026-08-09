import sqlite3
import re

DB_PATH = "data/parsed_chat.sqlite"

# Very basic dictionary for placeholder memory extraction
NICKNAMES = ["mowne", "molae", "bro", "da", "macha", "mapla", "di"]
KEYWORDS = {
    "exam": "Study & Exams",
    "college": "Places",
    "hospital": "Places",
    "bus": "Meetings & Travel",
    "miss you": "Relationships",
    "love": "Relationships",
    "fight": "Important Moments",
    "sorry": "Important Moments"
}

def extract_memories():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Clear existing memories
    cursor.execute("DELETE FROM memories")
    
    cursor.execute("SELECT * FROM messages WHERE is_system = 0 AND conversation_id IS NOT NULL")
    messages = cursor.fetchall()
    
    memories_to_insert = []
    
    print("Running basic NLP memory extraction...")
    
    for msg in messages:
        text = msg['text'].lower()
        conv_id = msg['conversation_id']
        
        if not text:
            continue
            
        # Extract Nicknames
        for nick in NICKNAMES:
            if re.search(r'\b' + nick + r'\b', text):
                memories_to_insert.append((
                    "Nicknames",
                    f"Used nickname: {nick}",
                    conv_id
                ))
                
        # Extract Keywords
        for kw, category in KEYWORDS.items():
            if kw in text:
                memories_to_insert.append((
                    category,
                    f"Discussed: {kw}",
                    conv_id
                ))

    # De-duplicate memories per conversation to avoid spam
    unique_memories = set(memories_to_insert)

    cursor.executemany(
        "INSERT INTO memories (category, description, source_conversation_id) VALUES (?, ?, ?)",
        list(unique_memories)
    )
    
    conn.commit()
    conn.close()
    
    print(f"Extracted {len(unique_memories)} unique memories across {len(messages)} messages.")
    print("(Note: This is a basic NLP implementation. Phase 6 will upgrade this with LLM capabilities.)")

if __name__ == "__main__":
    extract_memories()
