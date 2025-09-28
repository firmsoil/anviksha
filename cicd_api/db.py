import os
from pymongo import MongoClient

# Read MONGO_URI from the environment variable (crucial for Docker Compose)
# Defaulting to localhost is fine for local/legacy execution, but 'mongo:27017' is used inside the container.
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
DB_NAME = os.getenv("DB_NAME", "cicd_db")
COLLECTION_NAME = "cdPipelineEvents"

# Initialize client, database, and collection globally
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

def get_collection():
    """Returns the pre-initialized MongoDB collection object."""
    return collection
