from pymongo import MongoClient

MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "cicd_db"
COLLECTION_NAME = "cdPipelineEvents"

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

def get_collection():
    return collection

