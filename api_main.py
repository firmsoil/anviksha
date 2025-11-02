import os
import sys
import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pymongo.errors import ConnectionFailure
from datetime import datetime
from bson import ObjectId

# Add current directory to path for imports
sys.path.insert(0, '/app')

# Import our modules
import pipeline
import mcp_client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# MongoDB Setup
MONGO_HOST = os.getenv("MONGO_HOST", "mongo")
MONGO_PORT = os.getenv("MONGO_PORT", "27017")
MONGO_URI = f"mongodb://{MONGO_HOST}:{MONGO_PORT}/"
DATABASE_NAME = "cicd_db"

db_client = None
database = None

def get_db():
    global db_client, database
    if database is None:
        try:
            from pymongo import MongoClient
            db_client = MongoClient(MONGO_URI)
            db_client.admin.command('ismaster')
            database = db_client[DATABASE_NAME]
            logger.info("✅ Connected to MongoDB")
        except ConnectionFailure as e:
            logger.error(f"❌ MongoDB connection failed: {e}")
            raise RuntimeError(f"Failed to connect to MongoDB at {MONGO_URI}")
    return database

# FastAPI App
app = FastAPI(
    title="CICD Conversational Analytics API",
    description="Natural language CI/CD data analysis with MCP",
    version="2.0.0",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
)

# Pydantic Models
class QueryRequest(BaseModel):
    query: str
    session_id: str = "default_session"
    history: list = []

class QueryResponse(BaseModel):
    query_text: str
    summary: str
    pipeline_explanation: str
    mongodb_pipeline: list
    results: list
    mcp_enabled: bool
    schema_source: str

class MCPStatusResponse(BaseModel):
    enabled: bool
    server_url: str
    cache_ttl: int
    collections: list = []
    error: str = None

@app.on_event("startup")
def startup_initialization():
    try:
        get_db()
        logger.info("Database initialized")
        
        mcp = mcp_client.get_mcp_client()
        if mcp.enabled:
            logger.info("✅ MCP Client enabled")
            try:
                mcp.build_enriched_schema_context("cdPipelineEvents")
                logger.info("✅ MCP schema cache warmed")
            except Exception as e:
                logger.warning(f"⚠️  MCP cache warm failed: {e}")
        else:
            logger.warning("⚠️  MCP disabled - using static schema")
    except Exception as e:
        logger.error(f"❌ Startup failed: {e}")

@app.get("/")
def root():
    return {"message": "Anviksha API", "docs": "/api/docs", "health": "/api/health"}

@app.get("/api/health")
def health_check():
    try:
        db = get_db()
        db_client.admin.command('ping')
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    mcp = mcp_client.get_mcp_client()
    mcp_status = {
        "enabled": mcp.enabled,
        "server_url": mcp.mcp_url if mcp.enabled else None
    }
    
    return {
        "status": "ok" if db_status == "connected" else "degraded",
        "db_status": db_status,
        "mcp_status": mcp_status,
        "version": "2.0.0"
    }

@app.get("/api/mcp/status", response_model=MCPStatusResponse)
def mcp_status():
    mcp = mcp_client.get_mcp_client()
    
    if not mcp.enabled:
        return MCPStatusResponse(
            enabled=False,
            server_url=mcp.mcp_url,
            cache_ttl=mcp.cache_ttl,
            error="MCP disabled or unreachable"
        )
    
    try:
        collections = mcp.list_collections(DATABASE_NAME)
        return MCPStatusResponse(
            enabled=True,
            server_url=mcp.mcp_url,
            cache_ttl=mcp.cache_ttl,
            collections=collections
        )
    except Exception as e:
        return MCPStatusResponse(
            enabled=False,
            server_url=mcp.mcp_url,
            cache_ttl=mcp.cache_ttl,
            error=str(e)
        )

@app.post("/api/mcp/clear-cache")
def clear_mcp_cache():
    try:
        mcp = mcp_client.get_mcp_client()
        mcp.clear_cache()
        return {"status": "success", "message": "MCP cache cleared"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/schema")
def get_schema_info():
    try:
        mcp = mcp_client.get_mcp_client()
        
        if mcp.enabled:
            schema_context = mcp.build_enriched_schema_context("cdPipelineEvents")
            return {
                "source": "mcp",
                "collection": "cdPipelineEvents",
                "context": schema_context,
                "fields": mcp.get_schema("cdPipelineEvents")
            }
        else:
            return {
                "source": "static",
                "collection": "cdPipelineEvents",
                "context": mcp._get_fallback_schema_text(),
                "warning": "MCP disabled"
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/query", response_model=QueryResponse)
def handle_query(request: QueryRequest):
    try:
        db = get_db()
        mcp = mcp_client.get_mcp_client()

        logger.info(f"Query: '{request.query}'")

        gen_pipeline, explanation = pipeline.generate_pipeline(request.query, request.history)
        results = pipeline.execute_pipeline(gen_pipeline, db)
        summary = pipeline.summarize_results(results, request.query, explanation)

        return QueryResponse(
            query_text=request.query,
            summary=summary,
            pipeline_explanation=explanation,
            mongodb_pipeline=gen_pipeline,
            results=results,
            mcp_enabled=mcp.enabled,
            schema_source="mcp" if mcp.enabled else "static"
        )
    except Exception as e:
        logger.error(f"Query failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/collections/{collection_name}/distinct/{field_name}")
def get_distinct_field_values(collection_name: str, field_name: str, limit: int = 100):
    try:
        mcp = mcp_client.get_mcp_client()
        
        if not mcp.enabled:
            raise HTTPException(status_code=503, detail="MCP disabled")
        
        values = mcp.get_distinct_values(collection_name, field_name, DATABASE_NAME, limit)
        
        return {
            "collection": collection_name,
            "field": field_name,
            "distinct_values": values,
            "count": len(values),
            "limit": limit
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/collections/{collection_name}/sample")
def get_sample_documents(collection_name: str, limit: int = 10):
    try:
        mcp = mcp_client.get_mcp_client()
        
        if not mcp.enabled:
            raise HTTPException(status_code=503, detail="MCP disabled")
        
        samples = mcp.sample_documents(collection_name, DATABASE_NAME, min(limit, 50))
        
        return {
            "collection": collection_name,
            "samples": samples,
            "count": len(samples),
            "limit": limit
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
