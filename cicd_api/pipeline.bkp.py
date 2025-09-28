import os
import json
from typing import List, Dict, Any

from openai import OpenAI

MONGO_URI = "mongodb://localhost:27017/"

# Initialize OpenAI client once if API key available
openai_client = None
if os.getenv("OPENAI_API_KEY"):
    openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

MOCK_RESPONSES = {
    "list all event types": [
        {"$group": {"_id": None, "event_types": {"$addToSet": "$event_type"}}}
    ],
    "count events by source": [
        {"$group": {"_id": "$source", "count": {"$sum": 1}}}
    ],
    # Add more mock mappings for quick demo/testing here
}

def mock_llm_response(prompt: str) -> str:
    for key, pipeline in MOCK_RESPONSES.items():
        if key in prompt.lower():
            return json.dumps({"pipeline": pipeline, "explanation": f"Mock explanation for '{key}'"})
    return json.dumps({"pipeline": [], "explanation": "Mock: No matching query found."})

def generate_pipeline(query: str, history: List[Dict[str, str]]) -> tuple[List[Dict[str, Any]], str]:
    history_str = "\n".join([f"User: {msg['query']}\nAssistant: {msg.get('response', '')}" for msg in history])

    if openai_client:
        system_prompt = """
You are a MongoDB query expert.
Translate the user's natural language query into a valid MongoDB aggregation pipeline.
Output only a JSON object: {"pipeline": [array of stages], "explanation": "brief explanation"}.
Ensure the pipeline is safe: limit results to 1000, avoid destructive operations.
Use schema-aware logic based on the CICD event schema.
For multi-turn, refine based on history.
"""
        user_prompt = f"""
Given the following schema:
Collection: cdPelineEvents

Fields:

- event_type: string
- description: string
- source: string

And the conversation history:

{history_str}

User's natural language query: "{query}"
"""
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"}
        )
        result = response.choices[0].message.content
    else:
        print("Warning: Using mock LLM response.")
        result = mock_llm_response(query)

    try:
        parsed = json.loads(result)
        if not any("$limit" in stage for stage in parsed["pipeline"]):
            parsed["pipeline"].append({"$limit": 1000})
        return parsed["pipeline"], parsed["explanation"]
    except Exception as e:
        raise ValueError(f"Failed to parse LLM response: {e}")

def execute_pipeline(pipeline: List[Dict[str, Any]], db) -> List[Dict[str, Any]]:
    collection = db["cdPelineEvents"]
    try:
        results = list(collection.aggregate(pipeline))
        return results
    except Exception as e:
        raise RuntimeError(f"Query execution failed: {e}")

def summarize_results(results: List[Dict[str, Any]], query: str, pipeline_explanation: str) -> str:
    results_str = json.dumps(results[:10], default=str)

    if openai_client:
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

