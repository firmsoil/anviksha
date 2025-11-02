"""
Mock MCP Server - Provides real MongoDB integration
This server connects to actual MongoDB and provides MCP-like API
"""
import os
import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pymongo import MongoClient
from typing import Dict, Any, List
import uvicorn

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Mock MCP Server")

# MongoDB connection
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://mongo:27017/")
MONGODB_DATABASE = os.getenv("MONGODB_DATABASE", "cicd_db")

mongo_client = None
db = None

def get_db():
    """Get MongoDB connection"""
    global mongo_client, db
    if db is None:
        try:
            mongo_client = MongoClient(MONGODB_URI)
            mongo_client.admin.command('ping')
            db = mongo_client[MONGODB_DATABASE]
            logger.info(f"✅ Connected to MongoDB at {MONGODB_URI}")
            logger.info(f"✅ Using database: {MONGODB_DATABASE}")
        except Exception as e:
            logger.error(f"❌ Failed to connect to MongoDB: {e}")
    return db

@app.get("/health")
def health():
    """Health check endpoint"""
    try:
        database = get_db()
        if database is not None:
            mongo_client.admin.command('ping')
            
            # Check if we have data
            try:
                collection = database["cdPipelineEvents"]
                doc_count = collection.count_documents({})
                logger.info(f"Database has {doc_count} documents in cdPipelineEvents")
            except Exception as e:
                logger.warning(f"Could not count documents: {e}")
                doc_count = -1
            
            return {
                "status": "healthy",
                "version": "1.0.0-mock",
                "database": "connected",
                "type": "mock-mcp-server",
                "mongodb_uri": MONGODB_URI,
                "database_name": MONGODB_DATABASE,
                "document_count": doc_count
            }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
    
    return JSONResponse(
        status_code=503,
        content={"status": "unhealthy", "database": "disconnected"}
    )

@app.post("/mcp/tools/listCollections")
async def list_collections(request: Request):
    """List all collections in the database"""
    try:
        body = await request.json()
        database_name = body.get("database", MONGODB_DATABASE)
        
        logger.info(f"Listing collections for database: {database_name}")
        
        database = get_db()
        if database is None:
            logger.error("Database connection is None")
            return {"collections": []}
        
        collections = database.list_collection_names()
        logger.info(f"Found collections: {collections}")
        
        return {"collections": collections}
    except Exception as e:
        logger.error(f"Error listing collections: {e}")
        return {"collections": [], "error": str(e)}

@app.post("/mcp/tools/getSchema")
async def get_schema(request: Request):
    """Get schema for a collection"""
    try:
        body = await request.json()
        collection_name = body.get("collection", "cdPipelineEvents")
        
        logger.info(f"Getting schema for collection: {collection_name}")
        
        database = get_db()
        if database is None:
            return {"schema": {}}
        
        collection = database[collection_name]
        
        # Check collection exists and has data
        doc_count = collection.count_documents({})
        logger.info(f"Collection {collection_name} has {doc_count} documents")
        
        if doc_count == 0:
            logger.warning(f"Collection {collection_name} is empty!")
            return {"schema": {}}
        
        # Sample a document to infer schema
        sample = collection.find_one()
        if not sample:
            return {"schema": {}}
        
        # Build schema from sample
        schema = {}
        for field, value in sample.items():
            if field == "_id":
                continue
            
            field_type = type(value).__name__
            if field_type == "str":
                field_type = "string"
            elif field_type == "int" or field_type == "float":
                field_type = "number"
            elif field_type == "datetime":
                field_type = "date"
            elif field_type == "dict":
                field_type = "object"
            elif field_type == "list":
                field_type = "array"
            
            schema[field] = {"type": field_type}
        
        logger.info(f"Generated schema with {len(schema)} fields: {list(schema.keys())}")
        return {"schema": schema}
        
    except Exception as e:
        logger.error(f"Error getting schema: {e}")
        return {"schema": {}, "error": str(e)}

@app.post("/mcp/tools/sampleDocuments")
async def sample_documents(request: Request):
    """Get sample documents from a collection"""
    try:
        body = await request.json()
        collection_name = body.get("collection", "cdPipelineEvents")
        limit = min(body.get("limit", 10), 50)
        filter_query = body.get("filter", {})
        
        logger.info(f"Sampling {limit} documents from {collection_name}")
        
        database = get_db()
        if database is None:
            return {"documents": []}
        
        collection = database[collection_name]
        
        # Get sample documents
        cursor = collection.find(filter_query).limit(limit)
        documents = []
        
        for doc in cursor:
            # Convert ObjectId to string
            if "_id" in doc:
                doc["_id"] = str(doc["_id"])
            documents.append(doc)
        
        logger.info(f"Sampled {len(documents)} documents from {collection_name}")
        return {"documents": documents}
        
    except Exception as e:
        logger.error(f"Error sampling documents: {e}")
        return {"documents": [], "error": str(e)}

@app.post("/mcp/tools/getDistinctValues")
async def get_distinct_values(request: Request):
    """Get distinct values for a field"""
    try:
        body = await request.json()
        collection_name = body.get("collection", "cdPipelineEvents")
        field = body.get("field", "event_type")
        limit = body.get("limit", 100)
        
        logger.info(f"Getting distinct values for field '{field}' in collection '{collection_name}'")
        
        database = get_db()
        if database is None:
            logger.error("Database is None")
            return {"values": []}
        
        collection = database[collection_name]
        
        # Check collection has data
        doc_count = collection.count_documents({})
        logger.info(f"Collection has {doc_count} documents")
        
        if doc_count == 0:
            logger.warning(f"Collection {collection_name} is empty!")
            return {"values": []}
        
        # Get distinct values
        values = collection.distinct(field)
        logger.info(f"Found {len(values)} distinct values for {field}: {values[:5]}...")
        
        # Limit results
        if len(values) > limit:
            values = values[:limit]
        
        return {"values": values}
        
    except Exception as e:
        logger.error(f"Error getting distinct values: {e}", exc_info=True)
        return {"values": [], "error": str(e)}

@app.post("/mcp/tools/getFieldStatistics")
async def get_field_statistics(request: Request):
    """Get statistics for a field"""
    try:
        body = await request.json()
        collection_name = body.get("collection", "cdPipelineEvents")
        field = body.get("field", "duration_seconds")
        
        database = get_db()
        if database is None:
            return {"statistics": {}}
        
        collection = database[collection_name]
        
        # Get basic statistics using aggregation
        pipeline = [
            {
                "$group": {
                    "_id": None,
                    "count": {"$sum": 1},
                    "min": {"$min": f"${field}"},
                    "max": {"$max": f"${field}"},
                    "avg": {"$avg": f"${field}"}
                }
            }
        ]
        
        result = list(collection.aggregate(pipeline))
        
        if result:
            stats = result[0]
            stats.pop("_id", None)
            logger.info(f"Statistics for {field}: {stats}")
            return {"statistics": stats}
        
        return {"statistics": {}}
        
    except Exception as e:
        logger.error(f"Error getting field statistics: {e}")
        return {"statistics": {}, "error": str(e)}

@app.post("/mcp/tools/getIndexes")
async def get_indexes(request: Request):
    """Get indexes for a collection"""
    try:
        body = await request.json()
        collection_name = body.get("collection", "cdPipelineEvents")
        
        database = get_db()
        if database is None:
            return {"indexes": []}
        
        collection = database[collection_name]
        
        # Get index information
        indexes = list(collection.list_indexes())
        
        # Clean up index info
        for idx in indexes:
            if "_id" in idx:
                idx["_id"] = str(idx["_id"])
        
        logger.info(f"Found {len(indexes)} indexes for {collection_name}")
        return {"indexes": indexes}
        
    except Exception as e:
        logger.error(f"Error getting indexes: {e}")
        return {"indexes": [], "error": str(e)}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 3000))
    logger.info(f"🚀 Starting Mock MCP Server on port {port}")
    logger.info(f"📊 MongoDB URI: {MONGODB_URI}")
    logger.info(f"💾 Database: {MONGODB_DATABASE}")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )
