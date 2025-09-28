import pymongo
from datetime import datetime, timedelta
import os
import random
from typing import List, Dict, Any

# Use environment variable for MongoDB connection string,
# defaulting to the Docker service name 'mongodb_cicd' for inter-container communication.
MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongodb_cicd:27017/")
DB_NAME = "cicd_db"
COLLECTION_NAME = "cdPipelineEvents"

# Sample data generation
EVENT_RECORDS: List[Dict[str, Any]] = [
    {"event_type": "Pull Request Created", "description": "Developer raises a pull request (merge request) for code review.", "source": "GitLab"},
    {"event_type": "Code Review / Approval", "description": "Pull request undergoes code review and approval process including security and policy checks.", "source": "GitLab"},
    {"event_type": "Pipeline Created", "description": "Pipeline triggered on pull request creation/update to run CI jobs.", "source": "GitLab"},
    {"event_type": "Pipeline Started", "description": "CI pipeline execution starts with build and test jobs.", "source": "GitLab"},
    {"event_type": "Build Stage Started", "description": "Build jobs compiling code and creating artifacts begin.", "source": "GitLab"},
    {"event_type": "SAST Security Scan Started", "description": "Static Application Security Testing scan to detect code vulnerabilities begins.", "source": "Security Tool"},
    {"event_type": "SAST Security Scan Completed", "description": "SAST scan finishes, policy check passed.", "source": "Security Tool"},
    {"event_type": "Manual Approval Denied", "description": "Manual approval denied; pipeline paused or aborted due to security concerns.", "source": "Harness"},
    {"event_type": "Production Deployment Started", "description": "Production deployment begins after passing all security and quality gates.", "source": "Harness"},
    {"event_type": "Production Deployment Finished", "description": "Production deployment completes successfully.", "source": "Harness"},
    {"event_type": "Service Monitoring Started", "description": "Monitoring of deployed app instances for security incidents, anomalies, and performance starts.", "source": "Harness"},
]


def load_data():
    """Connects to MongoDB and loads sample data."""
    if not MONGO_URI:
        print("ERROR: MONGO_URI is not set. Cannot connect to database.")
        return

    try:
        # Use a timeout for connection
        client = pymongo.MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        # Force connection attempt
        client.admin.command('ping')
        
        db = client[DB_NAME]
        collection = db[COLLECTION_NAME]
        
        # Clear old data
        collection.delete_many({})
        
        # Prepare data with staggered timestamps for more realistic analytics
        records_to_insert = []
        base_time = datetime.now()
        for i, event in enumerate(EVENT_RECORDS):
            event_copy = event.copy()
            # Stagger timestamps, making the last event the most recent
            time_offset = timedelta(minutes=(len(EVENT_RECORDS) - 1 - i) * random.randint(1, 3))
            event_copy["event_timestamp"] = base_time - time_offset
            records_to_insert.append(event_copy) 
            
        collection.insert_many(records_to_insert)
        
        print(f"Loaded {len(records_to_insert)} CICD event records into {DB_NAME}.{COLLECTION_NAME} at {MONGO_URI}")
        
    except pymongo.errors.ConnectionFailure as e:
        print(f"ERROR: Could not connect to MongoDB at {MONGO_URI}. Is the 'mongodb_cicd' service running? Details: {e}")
    except Exception as e:
        print(f"An unexpected error occurred during data loading: {e}")

if __name__ == "__main__":
    load_data()
