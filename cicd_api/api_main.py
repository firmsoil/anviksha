import os
import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pymongo.errors import ConnectionFailure, OperationFailure
from datetime import datetime
from bson import ObjectId

# Corrected Import: Import the new LLM functions
from .pipeline import generate_pipeline, execute_pipeline, summarize_results

# Setup logging
logging.basicConfig(level=logging.INFO)

# --- MongoDB Setup ---

# Use the service name defined in docker-compose for the host
MONGO_HOST = os.getenv("MONGO_HOST", "mongodb_cicd")
MONGO_PORT = os.getenv("MONGO_PORT", "27017")
MONGO_URI = f"mongodb://{MONGO_HOST}:{MONGO_PORT}/"
DATABASE_NAME = "cicd_db"

# Lazy-loaded database connection
db_client = None
database = None

def get_db():
    global db_client, database
    if database is None:
        try:
            from pymongo import MongoClient
            db_client = MongoClient(MONGO_URI)
            # The ismaster command is a lightweight way to check a connection.
            db_client.admin.command('ismaster')
            database = db_client[DATABASE_NAME]
            logging.info("Successfully connected to MongoDB.")
        except ConnectionFailure as e:
            logging.error(f"MongoDB connection failed: {e}")
            # Re-raise to halt the application startup if database is essential
            raise RuntimeError(f"Failed to connect to MongoDB at {MONGO_URI}. Check Docker network.")
    return database

# --- FastAPI App Initialization ---

# Fix: Added json_encoders to handle MongoDB ObjectId and datetime automatically
app = FastAPI(
    title="CICD Conversational Analytics API",
    description="A service to convert natural language into MongoDB aggregation pipelines for CI/CD data analysis.",
    version="1.0.1",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
    json_encoders={
        ObjectId: str,
        datetime: lambda dt: dt.isoformat(),
    }
)

# --- Pydantic Models ---

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

# --- Application Startup Event ---

@app.on_event("startup")
def startup_db_client():
    # Attempt connection on startup
    try:
        get_db()
    except RuntimeError:
        # If connection fails, allow app to start, but requests will fail until DB is available
        pass

# --- API Routes ---

@app.get("/api/health")
def health_check():
    """Simple health check."""
    try:
        db = get_db()
        # Ping the database
        db_client.admin.command('ping')
        return {"status": "ok", "db_status": "connected"}
    except Exception as e:
        # Return HTTP 500 if DB is down
        raise HTTPException(status_code=500, detail=f"Database connection failed: {e}")


@app.post("/api/query", response_model=QueryResponse)
def handle_query(request: QueryRequest):
    """
    Converts a natural language query into a MongoDB aggregation pipeline
    and returns the results.
    """
    try:
        db = get_db()

        # Step 1: LLM converts NL query to MongoDB Pipeline
        # NEW: Using generate_pipeline
        pipeline, explanation = generate_pipeline(request.query, request.history)
        
        # Step 2: Execute the Pipeline against MongoDB
        # NEW: Using execute_pipeline
        results = execute_pipeline(pipeline, db)
        
        # Step 3: LLM summarizes the results
        # NEW: Using summarize_results
        summary = summarize_results(results, request.query, explanation)

        # Step 4: Return structured response
        return QueryResponse(
            query_text=request.query,
            summary=summary,
            pipeline_explanation=explanation,
            mongodb_pipeline=pipeline,
            results=results
        )

    except RuntimeError as e:
        # Handles errors raised from execute_pipeline (like OperationFailure)
        logging.error(f"Query processing failed: {e}")
        # Return a custom error message to the client
        raise HTTPException(status_code=500, detail=f"Internal Server Error processing query. Details: {e}")
    
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

