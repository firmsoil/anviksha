import os
import random
from datetime import datetime, timedelta
from pymongo import MongoClient

# --- Configuration ---
# Use the service name defined in docker-compose for the host
MONGO_HOST = os.getenv("MONGO_HOST", "mongodb_cicd")
MONGO_PORT = os.getenv("MONGO_PORT", "27017")
MONGO_URI = f"mongodb://{MONGO_HOST}:{MONGO_PORT}/"
DATABASE_NAME = "cicd_db"
COLLECTION_NAME = "cdPipelineEvents"

# --- Data Generation Helper ---

def generate_events(start_date: datetime, count: int) -> list:
    """Generates a list of realistic CI/CD events with numerical durations."""
    events = []
    
    # Events that should have a duration (simulated seconds)
    # Events with 0 duration will have their 'duration_seconds' field set to 0.
    event_types = [
        ("Pull Request Created", 0),
        ("Code Review / Approval", 3600), # 1 hour
        ("SonarQube Code Quality Scan Started", 0),
        ("SonarQube Code Quality Scan Completed", 120), # 2 mins
        ("Build Stage Started", 0),
        ("Unit Tests Completed", 60), # 1 min
        ("Integration Tests Completed", 300), # 5 mins
        ("Vulnerability Scan Started", 0),
        ("Vulnerability Scan Failed", 0),
        ("SAST Security Scan Started", 0),
        ("SAST Security Scan Completed", 900), # 15 mins (Longest event)
        ("Artifact Published (Container)", 30), # 30 seconds
        ("Pre-Prod Deployment Started", 0),
        ("Manual Approval Required", 0),
        ("Manual Approval Denied", 0),
        ("Production Deployment Started", 0),
        ("Production Deployment Finished", 180), # 3 mins
        ("Service Monitoring Started", 0),
        ("Rollback Initiated", 0),
        ("Rollback Finished", 150), # 2.5 mins
    ]
    
    users = ["John Smith", "Jane Doe", "SystemUser-CI", "DeveloperX"]
    sources = ["GitLab", "Jenkins", "Security Tool", "Harness"]

    current_date = start_date
    for _ in range(count):
        event_type, base_duration = random.choice(event_types)
        
        # Determine the duration, adding some random noise
        duration = 0 # Default to 0 seconds (FIXED: was None)
        if base_duration > 0:
            # Add/subtract up to 50% of the base duration for variation
            variation = random.randint(-int(base_duration * 0.5), int(base_duration * 0.5))
            duration = max(1, base_duration + variation)
        
        current_date += timedelta(minutes=random.randint(5, 60)) # Space events out

        event = {
            "event_type": event_type,
            "event_timestamp": current_date,
            "user": random.choice(users),
            "source": random.choice(sources),
            "duration_seconds": duration, # Now guaranteed to be a number (0 or positive)
            "pipeline_id": f"pipeline-{random.randint(100, 105)}",
            "metadata": {
                "branch": "main" if "Prod" in event_type else "feature-branch",
                "environment": "prod" if "Prod" in event_type else "dev",
            }
        }
        events.append(event)
        
    return events

# --- Main Execution ---

def load_data():
    """Initializes MongoDB connection and loads sample data."""
    try:
        # Connect to MongoDB
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        client.admin.command('ping') 
        db = client[DATABASE_NAME]
        collection = db[COLLECTION_NAME]

        # 1. Drop the existing collection (for clean reload)
        collection.drop()
        print(f"Dropped existing collection: {COLLECTION_NAME}")

        # 2. Generate and insert new data
        start_time = datetime.now() - timedelta(days=7)
        new_events = generate_events(start_time, 100)
        
        insert_result = collection.insert_many(new_events)
        print(f"Successfully inserted {len(insert_result.inserted_ids)} new documents into {COLLECTION_NAME}.")
        
        # 3. Create indices for better performance on common query fields
        collection.create_index("event_type")
        collection.create_index("event_timestamp")
        collection.create_index("user")
        
        client.close()

    except Exception as e:
        print(f"Error loading data into MongoDB: {e}")

if __name__ == "__main__":
    # Ensure the script runs when executed directly by docker-compose run
    load_data()

