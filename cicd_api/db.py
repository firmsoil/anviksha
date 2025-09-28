import os
from pymongo import MongoClient
import sys # Added for graceful exit on critical error

# Use the Docker service name 'mongodb_cicd' as the hostname via an environment variable.
# Fall back to 'mongodb_cicd' if the variable is not explicitly set.
# Note: In a typical docker-compose setup, the service name resolves to the correct internal IP.
MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongodb_cicd:27017/")
DB_NAME = "cicd_db"
COLLECTION_NAME = "cdPipelineEvents"

# Initialize client and collection when the module is imported
# This block includes basic error handling to prevent hard crashes on startup
try:
    # Set a timeout for connection attempts
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    # The next line forces a connection attempt to fail fast if MongoDB is down
    client.admin.command('ping') 
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]
    print(f"Successfully connected to MongoDB at {MONGO_URI}")
except Exception as e:
    # Log the critical error and set variables to None. The app will fail gracefully 
    # when get_collection() is called.
    print(f"CRITICAL ERROR: Failed to connect to MongoDB at {MONGO_URI}. Error: {e}")
    client = None
    db = None
    collection = None

def get_collection():
    """Returns the MongoDB collection object, raising an error if the connection failed."""
    if collection is None:
        raise ConnectionError("Database connection is not initialized. Check MongoDB status and MONGO_URI environment variable.")
    return collection

def get_client():
    """Returns the MongoDB client object."""
    return client
