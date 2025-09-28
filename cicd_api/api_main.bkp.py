from fastapi import FastAPI, HTTPException, Body
from typing import List, Dict, Any, Optional

# Use explicit relative imports inside the package
from .models import QueryRequest, QueryResponse, EventFilter
from .db import get_collection

app = FastAPI(title="CICD Conversational Analytics API")

# In-memory session storage, replace with persistent store in prod
session_history = {}

EVENT_SCHEMA = {
    "event_type": "string",
    "description": "string",
    "source": "string"
}

@app.post("/api/query", response_model=QueryResponse)
async def api_query(query_request: QueryRequest):
    coll = get_collection()
    history = session_history.get(query_request.session_id, []) if query_request.session_id else []

    try:
        pipeline, explanation = generate_pipeline(query_request.query, history)
        results = execute_pipeline(pipeline, coll.database)
        summary = summarize_results(results, query_request.query, explanation)

        if query_request.session_id:
            history.append({"query": query_request.query, "response": summary})
            session_history[query_request.session_id] = history

        return QueryResponse(
            pipeline=pipeline,
            explanation=explanation,
            results=results,
            raw_results=None
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/schema")
async def api_schema():
    return {"schema": EVENT_SCHEMA}


@app.post("/api/history")
async def api_history(session_id: str):
    return {"history": session_history.get(session_id, [])}


@app.post("/api/events", response_model=List[Dict[str, Any]])
async def api_events(filters: EventFilter = Body(...)):
    coll = get_collection()
    query = {}
    if filters.event_type:
        query["event_type"] = {"$regex": filters.event_type, "$options": "i"}
    if filters.source:
        query["source"] = {"$regex": filters.source, "$options": "i"}

    # Adjust date filtering here if your documents have date stored

    cursor = coll.find(query).skip(filters.skip).limit(filters.limit)
    results = []
    for doc in cursor:
        doc["_id"] = str(doc["_id"])
        results.append(doc)
    return results


# Note: The functions generate_pipeline, execute_pipeline, summarize_results
# should be defined in this module or imported if defined elsewhere in this package.
# For example:
from .pipeline import generate_pipeline, execute_pipeline, summarize_results

