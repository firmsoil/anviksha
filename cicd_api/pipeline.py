from bson import ObjectId
from datetime import datetime
import dateparser
import re
from typing import List, Dict, Any, Tuple, Optional
import logging


def extract_event_type(query: str) -> Optional[str]:
    """Extracts event type from query for patterns like: 'pipeline events for XYZ'."""
    match = re.search(r'pipeline events for ([\w\s\-]+)', query, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return None

def extract_object_id(query: str) -> Optional[ObjectId]:
    """Extracts an ObjectId from query for 'ObjectId(\"...\")' or 'ObjectId(...)'."""
    match = re.search(r'ObjectId\([\'"]?([a-fA-F0-9]{24})[\'"]?\)', query)
    if match:
        try:
            return ObjectId(match.group(1))
        except Exception:
            return None
    return None

def extract_nlp_date(query: str) -> Optional[datetime]:
    """Extracts date phrase from query like 'since two weeks ago' and parses it."""
    match = re.search(r'\b(since|after|from)\s+([a-zA-Z0-9\s,.\-]+)', query, re.IGNORECASE)
    if match:
        human_date = match.group(2).strip()
        dt = dateparser.parse(human_date)
        return dt
    return None

def generate_pipeline(query: str, history: List[Dict[str, str]]) -> Tuple[List[Dict[str, Any]], str]:
    """
    Generates a MongoDB aggregation pipeline from a natural language query.
    Supports event type, ObjectId, and natural language date filters.
    """
    pipeline = []
    explanation = "No recognized pattern in query."

    # 1. Check ObjectId
    obj_id = extract_object_id(query)
    if obj_id:
        pipeline = [{"$match": {"_id": obj_id}}, {"$limit": 1000}]
        explanation = f"Matches document with ObjectId {str(obj_id)}"
        return pipeline, explanation

    # 2. Check for event_type and date filters
    event_type = extract_event_type(query)
    date_filter = extract_nlp_date(query)
    match_filter = {}

    if event_type:
        match_filter["event_type"] = event_type

    if date_filter:
        match_filter["event_timestamp"] = {"$gte": date_filter}

    if match_filter:
        pipeline = [{"$match": match_filter}, {"$limit": 1000}]
        parts = []
        if event_type:
            parts.append(f"event_type='{event_type}'")
        if date_filter:
            parts.append(f"event_timestamp>={date_filter.isoformat()}")
        explanation = f"Filters applied: {', '.join(parts)}"  # Fixed unterminated string
        return pipeline, explanation

    # 3. Default fallback: limit documents
    pipeline = [{"$limit": 1000}]
    explanation = "No filters detected, returning up to 1000 documents."
    return pipeline, explanation


def execute_pipeline(pipeline: List[Dict[str, Any]], database) -> List[Dict[str, Any]]:
    """
    Executes the given aggregation pipeline on the specified database using the collection name.
    Assumes the collection is 'cdPipelineEvents' as per your context.
    """
    try:
        collection = database["cdPipelineEvents"]
        cursor = collection.aggregate(pipeline)
        results = list(cursor)
        return results
    except Exception as e:
        logging.error(f"Failed to execute pipeline: {e}")
        return []


def summarize_results(results: List[Dict[str, Any]], query: str, explanation: str) -> Dict[str, Any]:
    """
    Creates a summary combining the query, explanation and number of results.
    You can extend this with more intelligent summarization if desired.
    """
    summary = {
        "query": query,
        "explanation": explanation,
        "result_count": len(results),
        "sample_results": results[:3] if results else []
    }
    return summary

