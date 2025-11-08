import os
import json
import re
import dateparser
from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime
from bson import ObjectId
from openai import OpenAI
import logging
from pymongo.errors import OperationFailure

# FIXED: Import without relative path (works in Docker container)
import mcp_client

# Initialize the OpenAI client
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- LLM Functions (Enhanced with MCP) ---

def generate_pipeline(query: str, history: List[Dict[str, str]]) -> Tuple[List[Dict[str, Any]], str]:
    """
    Calls the LLM to generate a MongoDB aggregation pipeline from the user query.
    NOW ENHANCED: Uses MCP Toolbox to provide rich, dynamic schema context.
    
    Args:
        query: User's natural language query
        history: Conversation history for context
        
    Returns:
        Tuple of (pipeline, explanation)
    """
    
    # PHASE 1 ENHANCEMENT: Get dynamic schema context from MCP
    mcp = mcp_client.get_mcp_client()
    
    try:
        # Build enriched schema context using real database metadata
        enriched_schema = mcp.build_enriched_schema_context("cdPipelineEvents")
        
        logger.info("Using MCP-enriched schema context for pipeline generation")
        
        # Build conversation history string
        history_str = "\n".join([
            f"User: {msg['query']}\nAssistant: {msg.get('response', '')}" 
            for msg in history
        ])
        
        # NEW: Enhanced system prompt with dynamic context
        system_prompt = f"""
You are a MongoDB query expert with access to real-time database schema information.

Your task: Translate the user's natural language query into a valid MongoDB aggregation pipeline.

CRITICAL RULES:
1. Output ONLY a JSON object with this structure: {{"pipeline": [array of stages], "explanation": "brief explanation"}}
2. Use the ACTUAL field names and values from the schema below - do NOT guess or make up field names
3. When filtering by specific values (e.g., event types), use EXACT matches from the "Available Event Types" list
4. Always limit results to 1000 documents maximum for safety
5. For duration calculations, filter out events where duration_seconds = 0 first
6. Use the indexes listed below to optimize query performance

=== DYNAMIC DATABASE CONTEXT (Real-Time) ===
{enriched_schema}

=== CONVERSATION HISTORY ===
{history_str}

=== USER'S QUERY ===
"{query}"

IMPORTANT: Base your pipeline on the ACTUAL data shown above, not assumptions.
"""

        # Call OpenAI with enriched context
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Generate MongoDB pipeline for: {query}"}
            ],
            response_format={"type": "json_object"},
            temperature=0.1
        )
        
        result = response.choices[0].message.content
        parsed = json.loads(result)
        
        pipeline = parsed.get("pipeline", [])
        explanation = parsed.get("explanation", "No explanation provided")
        
        # Safety check: ensure $limit exists
        if not any("$limit" in stage for stage in pipeline):
            pipeline.append({"$limit": 1000})
            explanation += " (Added safety limit of 1000 documents)"
        
        logger.info(f"Generated pipeline with {len(pipeline)} stages using MCP context")
        return pipeline, explanation
        
    except Exception as e:
        logger.error(f"Pipeline generation failed: {e}. Attempting fallback.")
        
        # Fallback: Try with static schema if MCP fails
        try:
            return _generate_pipeline_fallback(query, history)
        except Exception as fallback_error:
            logger.error(f"Fallback pipeline generation also failed: {fallback_error}")
            # Last resort: return safe default
            return [{"$limit": 100}], f"Error generating pipeline: {str(e)}. Returning sample data."


def _generate_pipeline_fallback(query: str, history: List[Dict[str, str]]) -> Tuple[List[Dict[str, Any]], str]:
    """Fallback pipeline generation using minimal static schema."""
    static_schema = """
Collection: cdPipelineEvents
Fields: event_type (string), event_timestamp (date), user (string), 
        source (string), duration_seconds (number), pipeline_id (string)
"""
    
    history_str = "\n".join([f"User: {msg['query']}\nAssistant: {msg.get('response', '')}" for msg in history])
    
    system_prompt = f"""
You are a MongoDB query expert.
Translate the query into a MongoDB aggregation pipeline.
Output JSON: {{"pipeline": [...], "explanation": "..."}}

Schema: {static_schema}
History: {history_str}
Query: "{query}"
"""
    
    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query}
        ],
        response_format={"type": "json_object"}
    )
    
    parsed = json.loads(response.choices[0].message.content)
    pipeline = parsed.get("pipeline", [{"$limit": 100}])
    
    if not any("$limit" in stage for stage in pipeline):
        pipeline.append({"$limit": 1000})
    
    return pipeline, parsed.get("explanation", "Fallback pipeline (MCP unavailable)")


def execute_pipeline(pipeline: List[Dict[str, Any]], database) -> List[Dict[str, Any]]:
    """Executes the given aggregation pipeline on the specified database."""
    try:
        collection = database["cdPipelineEvents"]
        cursor = collection.aggregate(pipeline)
        results = list(cursor)
        
        # Convert ObjectId to str for JSON compatibility
        json_compatible_results = json.loads(json.dumps(results, default=str))
        
        logger.info(f"Pipeline executed successfully. Returned {len(results)} documents.")
        return json_compatible_results
        
    except OperationFailure as e:
        # Enhanced error handling with MCP context
        failing_pipeline_str = json.dumps(pipeline, indent=2, default=str)
        logger.error(f"MongoDB OperationFailure. Pipeline: {failing_pipeline_str}. Error: {e}")
        
        # Try to provide helpful diagnostics using MCP
        mcp = mcp_client.get_mcp_client()
        if mcp.enabled:
            try:
                schema = mcp.get_schema("cdPipelineEvents")
                logger.info(f"Current schema fields: {list(schema.keys())}")
            except:
                pass
        
        raise RuntimeError(
            f"MongoDB query failed. The pipeline may reference non-existent fields or use invalid operators. "
            f"Pipeline attempted: {failing_pipeline_str}. "
            f"MongoDB error: {e.details.get('errmsg', str(e))}"
        )
        
    except Exception as e:
        logger.error(f"Query execution failed: {e}")
        raise RuntimeError(f"MongoDB pipeline execution failed: {str(e)}")


def summarize_results(results: List[Dict[str, Any]], query: str, pipeline_explanation: str) -> str:
    """Summarizes the query results using the LLM."""
    if not os.getenv("OPENAI_API_KEY"):
        return f"Query returned {len(results)} results. (OpenAI API key not configured for summarization)"
    
    try:
        results_preview = results[:10]
        results_str = json.dumps(results_preview, default=str, indent=2)
        
        metadata = f"\nTotal results: {len(results)}"
        if len(results) > 10:
            metadata += f" (showing first 10 for summary)"
        
        system_prompt = """
You are a helpful data analyst assistant.

Provide a concise, business-friendly summary of the query results.

GUIDELINES:
- Start with the key finding (e.g., "Found 15 security scan events...")
- Highlight important patterns or anomalies
- Use business-friendly language (avoid technical jargon)
- Keep the summary under 150 words
- If showing aggregated data, explain what the numbers mean

Output only plain text (no markdown, no formatting).
"""
        
        user_prompt = f"""
User asked: "{query}"

Pipeline explanation: "{pipeline_explanation}"

Results:{metadata}
{results_str}

Provide a clear summary of what was found.
"""
        
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,
            max_tokens=300
        )
        
        summary = response.choices[0].message.content
        logger.info("Results summarized successfully")
        return summary
        
    except Exception as e:
        logger.error(f"LLM summarization failed: {e}")
        return f"Query returned {len(results)} results. Error generating summary: {str(e)}"


# --- Utility functions ---

def extract_event_type(query: str) -> Optional[str]:
    """Extract event type from query string"""
    match = re.search(r'pipeline events for ([\w\s\-]+)', query, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return None


def extract_object_id(query: str) -> Optional[ObjectId]:
    """Extract MongoDB ObjectId from query string"""
    match = re.search(r'([a-fA-F0-9]{24})', query)
    if match:
        try:
            return ObjectId(match.group(1))
        except Exception:
            return None
    return None


def extract_nlp_date(query: str) -> Optional[datetime]:
    """Extract date from natural language query"""
    match = re.search(r'\b(since|after|from)\s+([a-zA-Z0-9\s,.-]+)', query, re.IGNORECASE)
    if match:
        human_date = match.group(2).strip()
        dt = dateparser.parse(human_date)
        return dt
    return None
