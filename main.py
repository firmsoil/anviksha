import os
import json
import pymongo
from bson import ObjectId
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from openai import OpenAI
from typing import List, Dict, Any
from datetime import datetime, timedelta

MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "cicd_db"
COLLECTION_NAME = "cdPipelineEvents"

SCHEMA = """
Collection: cdPipelineEvents

Fields:

- event_type: string
- description: string
- source: string
"""

openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

MOCK_RESPONSES = {
    "list all event types": [
        {
            "$group": {
                "_id": None,
                "event_types": {"$addToSet": "$event_type"}
            }
        }
    ],
    "count events by source": [
        {
            "$group": {
                "_id": "$source",
                "count": {"$sum": 1}
            }
        }
    ],
    "show events with scan started": [
        {
            "$match": {
                "event_type": {"$regex": "scan started", "$options": "i"}
            }
        }
    ],
}

app = FastAPI()

def mock_llm_response(prompt: str) -> str:
    for key, pipeline in MOCK_RESPONSES.items():
        if key in prompt.lower():
            return json.dumps({"pipeline": pipeline, "explanation": f"Mock explanation for '{key}'"})
    return json.dumps({"pipeline": [], "explanation": "Mock: No matching query found."})

def generate_pipeline(query: str, history: List[Dict[str, str]]) -> tuple[List[Dict[str, Any]], str]:
    history_str = "\n".join([f"User: {msg['query']}\nAssistant: {msg.get('response', '')}" for msg in history])

    if "since two weeks ago" in query.lower():
        two_weeks_ago = datetime.utcnow() - timedelta(days=14)
        pipeline = [
            {"$match": {"event_timestamp": {"$gte": two_weeks_ago}}},
            {"$limit": 1000}
        ]
        explanation = (
            "This pipeline filters the events from the last two weeks based on the event_timestamp, "
            "ensuring only valid event documents are included and limits the results to 1000."
        )
        return pipeline, explanation

    if os.getenv("OPENAI_API_KEY"):
        system_prompt = f"""
You are a MongoDB query expert.

Translate the user's natural language query into a valid MongoDB aggregation pipeline.

Output only a JSON object: {{"pipeline": [array of stages], "explanation": "brief explanation"}}

Ensure the pipeline is safe: limit results to 1000, avoid destructive operations.

Use schema-aware logic based on the CICD event schema.

For multi-turn, refine based on history.

Schema:

{SCHEMA}

Conversation history:

{history_str}

User's natural language query: "{query}"
"""
        user_prompt = ""
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"}
        )
        result = response.choices[0].message.content
        try:
            parsed = json.loads(result)
            if not any("$limit" in stage for stage in parsed["pipeline"]):
                parsed["pipeline"].append({"$limit": 1000})
            return parsed["pipeline"], parsed["explanation"]
        except Exception as e:
            raise ValueError(f"Failed to parse LLM response: {e}")
    else:
        result = mock_llm_response(query)
        parsed = json.loads(result)
        if not any("$limit" in stage for stage in parsed["pipeline"]):
            parsed["pipeline"].append({"$limit": 1000})
        return parsed["pipeline"], parsed["explanation"]

def execute_pipeline(pipeline: List[Dict[str, Any]], db) -> List[Dict[str, Any]]:
    collection = db[COLLECTION_NAME]
    try:
        results = list(collection.aggregate(pipeline))
        json_compatible_results = jsonable_encoder(
            results,
            custom_encoder={ObjectId: str}
        )
        return json_compatible_results
    except Exception as e:
        raise RuntimeError(f"Query execution failed: {e}")

def summarize_results(results: List[Dict[str, Any]], query: str, pipeline_explanation: str) -> str:
    results_str = json.dumps(results[:10], default=str)
    if os.getenv("OPENAI_API_KEY"):
        system_prompt = """
You are a helpful summarizer.

Provide a concise, business-friendly summary and explanation.

Output only plain text.
"""
        user_prompt = f"""
Given query: "{query}"

Pipeline explanation: "{pipeline_explanation}"

Results: {results_str}

"""
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )
        return response.choices[0].message.content
    else:
        return f"Mock summary for results: {results_str}"

@app.post("/api/query")
async def api_query(request: Request):
    try:
        body = await request.json()
        query_text = body.get("query", "")
        client = pymongo.MongoClient(MONGO_URI)
        db = client[DB_NAME]
        pipeline, explanation = generate_pipeline(query_text, [])
        results = execute_pipeline(pipeline, db)
        return {"results": results, "explanation": explanation}
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

