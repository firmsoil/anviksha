from pymongo import MongoClient

# CRITICAL FIX: Changed 'localhost' to 'mongo' to connect within the Docker network
# 'mongo' is the service name defined in your docker-compose file.
MONGO_URI = "mongodb://mongo:27017/"
DB_NAME = "cicd_db"
COLLECTION_NAME = "cdPipelineEvents"

# Initial connection setup (this will now try to connect to the 'mongo' service)
try:
    client = MongoClient(MONGO_URI)
    # Ping the server to ensure a connection can be established immediately
    client.admin.command('ping')
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]
    print("Successfully connected to MongoDB.")
except Exception as e:
    # Log the error, but the app should still start. The get_collection function handles the retry logic if needed.
    print(f"Initial MongoDB connection failed: {e}")
    # Initialize placeholders if connection fails
    db = None
    collection = None


def get_collection():
    """Returns the MongoDB collection object, ensuring a connection is attempted if not already established."""
    global collection, db, client

    # Lazy initialization/reconnection check
    if collection is None:
        try:
            client = MongoClient(MONGO_URI)
            client.admin.command('ping') # Verify connection
            db = client[DB_NAME]
            collection = db[COLLECTION_NAME]
            print("Reconnected to MongoDB successfully.")
        except Exception as e:
            # Re-raise an error that will be caught by the FastAPI endpoint's HTTPException 500
            raise RuntimeError(f"Database connection failed during request: {e}")

    return collection

