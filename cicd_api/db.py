import os
from pymongo import MongoClient

# Use environment variable for the connection URI, defaulting to the Docker service name.
# Inside the Docker network, 'mongodb_cicd' resolves to the MongoDB container's IP.
MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongodb_cicd:27017/")
DB_NAME = "cicd_db"
COLLECTION_NAME = "cdPipelineEvents"

# Initialize the client, database, and collection
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

def get_collection():
    """Returns the pre-initialized collection object."""
    return collection

# Test connection on module load to catch connection errors early
try:
    # The ismaster command is a lightweight way to confirm the connection
    client.admin.command('ismaster')
    print(f"Successfully connected to MongoDB at: {MONGO_URI}")
except Exception as e:
    # If this fails, the container will likely crash, but the error message will be informative
    print(f"ERROR: Failed to connect to MongoDB using URI: {MONGO_URI}. Details: {e}")
