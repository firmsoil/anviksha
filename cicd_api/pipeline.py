import os
import json
import re
import dateparser
from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime
from bson import ObjectId
# NOTE: The openai library is used here, assuming you have set OPENAI_API_KEY in your docker-compose.yml
# If you prefer Gemini, replace this with the appropriate Gemini API client/requests logic.
from openai import OpenAI
import logging
from pymongo.errors import OperationFailure 

# Initialize the OpenAI client (will read key from environment)
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Define a basic schema for the LLM to understand the data
# The LLM uses this information to build the pipeline.
SCHEMA = """
Collection: cdPipelineEvents

Fields:
- event_type: string (e.g., 'Build Stage Started', 'SAST Security Scan Started')
- user: string (e.g., 'Jane Doe', 'John Smith')
- source: string (e.g., 'GitLab', 'Harness', 'Security Tool')
- event_timestamp: datetime (ISO format)
- duration_seconds: numeric (used for calculating averages and timing)
"""

# --- LLM Functions (Core Logic) ---

def generate_pipeline(query: str, history: List[Dict[str, str]]) -> Tuple[List[Dict[str, Any]], str]:
    """
    Calls the LLM to generate a MongoDB aggregation pipeline from the user query.
    """
    full_prompt = (
        f"You are a MongoDB pipeline generator. Convert the following user query "
        f"into a valid MongoDB aggregation pipeline that can be executed on the '{SCHEMA}' collection. "
        f"The query is: '{query}'. "
        f"Ensure all aggregation operations (like $avg, $sum) use the correct field names and types, especially 'duration_seconds' for time calculations."
        f"Return the response as a JSON object with two keys: 'pipeline' (List[Dict]) and 'explanation' (str)."
    )

    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a professional JSON-generating MongoDB expert. Respond only with the requested JSON object."},
                {"role": "user", "content": full_prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        response_json = json.loads(response.choices[0].message.content)
        pipeline = response_json.get("pipeline", [{"$limit": 100}])
        explanation = response_json.get("explanation", "LLM provided no explanation.")
        return pipeline, explanation

    except Exception as e:
        # Fallback if LLM call fails (e.g., bad key, network error)
        logging.error(f"LLM call failed in generate_pipeline: {e}. Falling back to default pipeline.")
        pipeline = [{"$limit": 100}]
        explanation = "LLM failed to generate pipeline. Returning 100 sample documents."
        return pipeline, explanation


def execute_pipeline(pipeline: List[Dict[str, Any]], database) -> List[Dict[str, Any]]:
    """
    Executes the given aggregation pipeline on the specified database.
    """
    try:
        collection = database["cdPipelineEvents"]
        cursor = collection.aggregate(pipeline)
        results = list(cursor)
        
        # Convert ObjectId to str for JSON compatibility
        json_compatible_results = json.loads(json.dumps(results, default=str))
        return json_compatible_results
    except OperationFailure as e:
        # Raise a clear error that includes the failing pipeline for debugging
        failing_pipeline_str = json.dumps(pipeline, indent=2, default=str)
        logging.error(f"MongoDB OperationFailure occurred. Pipeline attempted: {failing_pipeline_str}. Error: {e}")
        # Re-raise the error with context
        raise RuntimeError(
            f"MongoDB query failed (OperationFailure). "
            f"The LLM-generated pipeline was invalid or referenced missing data. "
            f"Attempted Pipeline: {failing_pipeline_str}. MongoDB Error: {e.details.get('errmsg', 'No message')}"
        )
    except Exception as e:
        logging.error(f"Query execution failed: {e}")
        # Raise a concise error for the caller
        raise RuntimeError(f"MongoDB pipeline execution failed. Check if data is loaded.")


def summarize_results(results: List[Dict[str, Any]], query: str, pipeline_explanation: str) -> str:
    """
    Summarizes the query results using the LLM.
    """
    if os.getenv("OPENAI_API_KEY"):
        results_str = json.dumps(results[:10], default=str)
        system_prompt = "You are a helpful summarizer. Provide a concise, business-friendly summary and explanation. Output only plain text."
        user_prompt = f"Given query: \"{query}\"\nPipeline explanation: \"{pipeline_explanation}\"\nResults: {results_str}\n"

        try:
            response = openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            logging.error(f"LLM summarization failed: {e}")
            return f"Error: LLM summarization failed ({str(e)}). Raw count: {len(results)}"
    else:
        return f"Mock summary (OpenAI Key Missing). Raw result count: {len(results)}"

# --- Utility functions (Fixed) ---

def extract_event_type(query: str) -> Optional[str]:
    match = re.search(r'pipeline events for ([\w\s\-]+)', query, re.IGNORECASE)
    if match: return match.group(1).strip()
    return None

def extract_object_id(query: str) -> Optional[ObjectId]:
    # FIXED: Using a cleaner raw string regex to avoid Python SyntaxError on startup
    # This matches ObjectId(24charhex), ObjectId('24charhex'), or just the 24-char hex string
    match = re.search(r'([a-fA-F0-9]{24})', query)
    if match:
        try: return ObjectId(match.group(1))
        except Exception: return None
    return None

def extract_nlp_date(query: str) -> Optional[datetime]:
    match = re.search(r'\b(since|after|from)\s+([a-zA-Z0-9\s,.-]+)', query, re.IGNORECASE)
    if match:
        human_date = match.group(2).strip()
        dt = dateparser.parse(human_date)
        return dt
    return None

