from fastapi import APIRouter, Query, HTTPException
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
import sqlite3
import json
import os
from backend.ai.retrieval import retrieval_engine
from backend.database import get_db_connection

router = APIRouter()

@router.get("/stats")
async def get_memories_stats():
    profile_path = os.path.join("data", "memories", "persona_profile.json")
    stats = {
        "total_memories": 0,
        "important_conversations": 0,
        "frequently_discussed_topics": ["Relationship", "College", "Family", "Funny moments"],
        "recent_memories_count": 0
    }
    
    try:
        # Get memories count from sqlite
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM memories")
        stats["total_memories"] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM conversations")
        stats["important_conversations"] = cursor.fetchone()[0]
        
        conn.close()
    except Exception as e:
        print(f"Error getting stats: {e}")
        
    return stats

@router.get("/category/{category_name}")
async def get_category_memories(category_name: str, top_k: int = 20):
    category_map = {
        "Relationship": "love, romantic, feelings, couple, relationship, miss you",
        "College": "college, university, exams, study, campus, friends, degree",
        "Family": "family, parents, amma, appa, home, house, mom, dad",
        "Funny moments": "haha, funny, joke, laughing, lol, comedy, humor",
        "Emotional moments": "sad, crying, emotional, feelings, deep talk, missing you",
        "Special days": "birthday, anniversary, celebration, party, special day, congrats",
        "Everyday conversations": "good morning, good night, ate, sleep, what doing, breakfast"
    }
    
    query = category_map.get(category_name, category_name)
    try:
        results = retrieval_engine.semantic_search(query, top_k=top_k)
        
        memories = []
        for res in results:
            start_time = res['metadata'].get('start_time', 'Unknown Date')
            if 'T' in start_time:
                date = start_time.split('T')[0]
            else:
                date = start_time
                
            snippet = res['document']
            if len(snippet) > 150:
                snippet = snippet[:150] + "..."
                
            memories.append({
                "id": str(res['chunk_id']),
                "date": date,
                "title": f"{category_name} Memory",
                "description": f"Conversation about {category_name.lower()}",
                "snippet": snippet,
                "category": category_name,
                "importance": round(max(0, 1.0 - res['distance']), 2)
            })
        return memories
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search")
async def search_memories(q: str, top_k: int = 20):
    try:
        results = retrieval_engine.semantic_search(q, top_k=top_k)
        
        memories = []
        for res in results:
            start_time = res['metadata'].get('start_time', 'Unknown Date')
            if 'T' in start_time:
                date = start_time.split('T')[0]
            else:
                date = start_time
                
            snippet = res['document']
            if len(snippet) > 150:
                snippet = snippet[:150] + "..."
                
            memories.append({
                "id": str(res['chunk_id']),
                "date": date,
                "title": "Search Result",
                "description": f"Found matching memory for '{q}'",
                "snippet": snippet,
                "category": "Search",
                "importance": round(max(0, 1.0 - res['distance']), 2)
            })
        return memories
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/context/{chunk_id}")
async def get_memory_context(chunk_id: str):
    # Fetch the chunk from chroma to get its start_time
    try:
        res = retrieval_engine.collection.get(ids=[chunk_id])
        if not res['ids']:
            raise HTTPException(status_code=404, detail="Memory chunk not found")
        
        metadata = res['metadatas'][0]
        start_time = metadata.get('start_time')
        if not start_time:
            raise HTTPException(status_code=404, detail="No start_time found for memory chunk")
        
        # Query messages around start_time
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get messages starting a bit before and ending a bit after (just fetch by time limit)
        # We will fetch up to 100 messages starting from this timestamp
        cursor.execute(
            "SELECT * FROM messages WHERE datetime_iso >= ? ORDER BY datetime_iso ASC LIMIT 50",
            (start_time,)
        )
        
        rows = cursor.fetchall()
        messages = [dict(row) for row in rows]
        
        conn.close()
        
        date = start_time.split('T')[0] if 'T' in start_time else start_time
        
        return {
            "id": chunk_id,
            "date": date,
            "messages": messages,
            "source_conversation_id": metadata.get('conversation_id', 'Unknown')
        }
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
