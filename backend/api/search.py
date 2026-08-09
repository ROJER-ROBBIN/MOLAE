from fastapi import APIRouter, Query, HTTPException
from typing import List, Optional
from pydantic import BaseModel
from backend.ai.retrieval import retrieval_engine

router = APIRouter()

class SearchResult(BaseModel):
    chunk_id: int
    start_time: Optional[str]
    participants: Optional[str]
    document: str
    distance: float

@router.get("/search", response_model=List[SearchResult])
async def semantic_search(
    q: str = Query(..., description="The query string to search for semantically"),
    top_k: int = Query(5, description="Number of results to return")
):
    try:
        results = retrieval_engine.semantic_search(q, top_k=top_k)
        
        response = []
        for res in results:
            response.append(SearchResult(
                chunk_id=int(res['chunk_id']),
                start_time=res['metadata'].get('start_time'),
                participants=res['metadata'].get('participants'),
                document=res['document'],
                distance=res['distance']
            ))
            
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
