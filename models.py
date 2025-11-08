from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class QueryRequest(BaseModel):
    query: str
    session_id: Optional[str] = None

class QueryResponse(BaseModel):
    pipeline: List[Dict[str, Any]]
    explanation: str
    results: List[Dict[str, Any]]
    raw_results: Optional[List[Dict[str, Any]]] = None

class EventFilter(BaseModel):
    event_type: Optional[str] = None
    source: Optional[str] = None
    start_date: Optional[str] = None  # ISO format
    end_date: Optional[str] = None
    limit: Optional[int] = 50
    skip: Optional[int] = 0

