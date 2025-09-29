import pymongo
from datetime import datetime, timedelta
import os
from typing import List, Dict, Any

# Use environment variable for the connection URI, defaulting to the Docker service name
# This allows the script to connect to the MongoDB container when run via docker exec.
MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongodb_cicd:27017/")
DB_NAME = "cicd_db"
COLLECTION_NAME = "cdPipelineEvents"

# Define the set of distinct events, split across two projects
EVENT_RECORDS_BASE = [
    # Project Alpha Events
    {"event_type": "Pull Request Created", "description": "Developer raises a pull request for code review.", "source": "GitLab", "project": "Project Alpha"},
    {"event_type": "Code Review / Approval", "description": "Pull request undergoes code review and approval process.", "source": "GitLab", "project": "Project Alpha"},
    {"event_type": "Pipeline Started", "description": "CI pipeline execution starts with build and test jobs.", "source": "GitLab", "project": "Project Alpha"},
    {"event_type": "SonarQube Scan Completed", "description": "SonarQube analysis completes; quality gate passed.", "source": "SonarQube", "project": "Project Alpha"},
    {"event_type": "Production Deployment Started", "description": "Deployment begins after passing all gates.", "source": "Harness", "project": "Project Alpha"},
    {"event_type": "Production Deployment Finished", "description": "Production deployment completes successfully.", "source": "Harness", "project": "Project Alpha"},
    
    # Project Beta Events (focused on stability/rollbacks)
    {"event_type": "Pull Request Created", "description": "Developer raises a pull request for code review.", "source": "GitLab", "project": "Project Beta"},
    {"event_type": "Pipeline Started", "description": "CI pipeline execution starts with build and test jobs.", "source": "GitLab", "project": "Project Beta"},
    {"event_type": "Production Deployment Started", "description": "Deployment begins after passing all gates.", "source": "Harness", "project": "Project Beta"},
    {"event_type": "Rollback Initiated", "description": "Rollback initiated due to a failed deployment.", "source": "Harness", "project": "Project Beta"},
    {"event_type": "Rollback Finished", "description": "Rollback completes to last known good state.", "source": "Harness", "project": "Project Beta"},
]


def generate_time_series_data() -> List[Dict[str, Any]]:
    """Generates 10 full cycles of data with realistic, staggered timestamps."""
    full_data = []
    
    # Start the first pipeline cycle 10 hours ago
    start_time = datetime.now() - timedelta(hours=10)
    
    # Create 10 full pipeline cycles (5 for Alpha, 5 for Beta, interleaved)
    for i in range(10): 
        # Determine the project for this cycle
        project_name = "Project Alpha" if i % 2 == 0 else "Project Beta"
        
        # Determine the base events for this project
        project_events = [e for e in EVENT_RECORDS_BASE if e["project"] == project_name]

        # 1 hour between each full cycle
        current_time = start_time + timedelta(minutes=i*60) 
        
        # Simulate an event sequence over 10-20 minutes
        for j, base_event in enumerate(project_events):
            event = base_event.copy()
            
            # Stagger time between events within a cycle (1.5 to 3 minutes)
            time_offset = timedelta(seconds=(j * 90) + (i % 5) * 20) 
            event_time = current_time + time_offset
            
            event["event_timestamp"] = event_time
            
            # Add a unique 'pipeline_run_id' for each cycle
            event["pipeline_run_id"] = f"{project_name.replace(' ', '')}_RUN_{i+1:02d}"
            
            full_data.append(event)
            
    return full_data


def load_data():
    """Connects to Mongo and loads the generated data."""
    print(f"Attempting to connect to MongoDB at: {MONGO_URI}")
    
    try:
        client = pymongo.MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        
        # The ismaster command is a lightweight way to confirm the connection (within the timeout)
        client.admin.command('ismaster')
        print("MongoDB connection verified.")
        
        db = client[DB_NAME]
        collection = db[COLLECTION_NAME]
        
        # Clear old data
        collection.delete_many({})
        
        # Generate and insert new data
        event_records = generate_time_series_data()
        collection.insert_many(event_records)
        
        print(f"SUCCESS: Loaded {len(event_records)} CICD event records into {DB_NAME}.{COLLECTION_NAME}")
        
    except Exception as e:
        print(f"ERROR: Failed to load data. Ensure MongoDB is running and accessible via URI: {MONGO_URI}. Details: {e}")

if __name__ == "__main__":
    load_data()
