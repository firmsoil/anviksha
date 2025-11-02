import os
import random
from datetime import datetime, timedelta
from pymongo import MongoClient

# --- Configuration ---
MONGO_HOST = os.getenv("MONGO_HOST", "mongodb_cicd")
MONGO_PORT = os.getenv("MONGO_PORT", "27017")
MONGO_URI = f"mongodb://{MONGO_HOST}:{MONGO_PORT}/"
DATABASE_NAME = "cicd_db"
COLLECTION_NAME = "cdPipelineEvents"

# --- Enhanced Data Generation for Demo ---

def generate_events(start_date: datetime, count: int) -> list:
    """Generates realistic CI/CD events optimized for demo queries."""
    events = []
    
    # Enhanced event types with realistic durations
    # Format: (event_type, base_duration_seconds)
    event_types = [
        # Build and Test Events (high frequency)
        ("Pull Request Created", 0),
        ("Code Review / Approval", 3600),  # 1 hour
        ("Build Stage Started", 0),
        ("Build Stage Completed", 180),  # 3 minutes
        ("Unit Tests Started", 0),
        ("Unit Tests Completed", 60),  # 1 minute
        ("Integration Tests Started", 0),
        ("Integration Tests Completed", 300),  # 5 minutes
        
        # Security Events (critical for demo)
        ("SAST Security Scan Started", 0),
        ("SAST Security Scan Completed", 900),  # 15 minutes
        ("Vulnerability Scan Started", 0),
        ("Vulnerability Scan Completed", 600),  # 10 minutes
        ("Vulnerability Scan Failed", 0),
        ("Security Approval Required", 0),
        ("Security Approval Granted", 1800),  # 30 minutes
        
        # Code Quality
        ("SonarQube Code Quality Scan Started", 0),
        ("SonarQube Code Quality Scan Completed", 120),  # 2 minutes
        
        # Deployment Events
        ("Artifact Published (Container)", 30),  # 30 seconds
        ("Pre-Prod Deployment Started", 0),
        ("Pre-Prod Deployment Finished", 240),  # 4 minutes
        ("Production Deployment Started", 0),
        ("Production Deployment Finished", 180),  # 3 minutes
        
        # Approval and Monitoring
        ("Manual Approval Required", 0),
        ("Manual Approval Granted", 7200),  # 2 hours
        ("Manual Approval Denied", 0),
        ("Service Monitoring Started", 0),
        ("Health Check Passed", 5),  # 5 seconds
        
        # Rollback Events
        ("Rollback Initiated", 0),
        ("Rollback Finished", 150),  # 2.5 minutes
    ]
    
    # More realistic users with varied activity
    users = [
        "John Smith",      # Primary user for demo query
        "John Smith",      # Duplicate to increase frequency
        "Jane Doe",
        "Alice Johnson",
        "Bob Wilson",
        "SystemUser-CI",
        "DeveloperX"
    ]
    
    # Varied sources
    sources = [
        "GitLab",
        "GitLab",  # Most common
        "Jenkins",
        "Security Tool",
        "Harness",
        "SonarQube"
    ]
    
    # Pipeline IDs for realistic grouping
    pipeline_ids = [f"pipeline-{i}" for i in range(100, 110)]
    
    current_date = start_date
    
    for i in range(count):
        event_type, base_duration = random.choice(event_types)
        
        # Calculate duration with variation
        duration = 0
        if base_duration > 0:
            # Add/subtract up to 30% for realistic variation
            variation = random.randint(-int(base_duration * 0.3), int(base_duration * 0.3))
            duration = max(1, base_duration + variation)
        
        # Space events realistically
        current_date += timedelta(minutes=random.randint(2, 30))
        
        # Determine environment based on event type
        is_prod_event = "Production" in event_type or "Rollback" in event_type
        environment = "prod" if is_prod_event else random.choice(["dev", "staging", "dev", "dev"])
        branch = "main" if is_prod_event else random.choice(["main", "feature-branch", "feature-auth", "bugfix-123"])
        
        event = {
            "event_type": event_type,
            "event_timestamp": current_date,
            "user": random.choice(users),
            "source": random.choice(sources),
            "duration_seconds": duration,
            "pipeline_id": random.choice(pipeline_ids),
            "metadata": {
                "branch": branch,
                "environment": environment,
                "commit_sha": f"abc{random.randint(1000, 9999)}",
                "build_number": random.randint(1, 500)
            }
        }
        events.append(event)
    
    return events

# --- Main Execution ---

def load_data():
    """Initializes MongoDB connection and loads enhanced sample data."""
    try:
        # Connect to MongoDB
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        client.admin.command('ping') 
        db = client[DATABASE_NAME]
        collection = db[COLLECTION_NAME]

        # 1. Drop the existing collection (for clean reload)
        collection.drop()
        print(f"Dropped existing collection: {COLLECTION_NAME}")

        # 2. Generate and insert enhanced data (increased to 200 for better demo)
        start_time = datetime.now() - timedelta(days=14)  # 2 weeks of data
        new_events = generate_events(start_time, 200)
        
        insert_result = collection.insert_many(new_events)
        print(f"Successfully inserted {len(insert_result.inserted_ids)} new documents into {COLLECTION_NAME}.")
        
        # 3. Create indices for better performance
        collection.create_index("event_type")
        collection.create_index("event_timestamp")
        collection.create_index("user")
        collection.create_index("source")
        collection.create_index("duration_seconds")
        print("Created performance indices")
        
        # 4. Display statistics for verification
        print("\n=== Data Statistics ===")
        print(f"Total events: {collection.count_documents({})}")
        print(f"Events by John Smith: {collection.count_documents({'user': 'John Smith'})}")
        print(f"Security scan events: {collection.count_documents({'event_type': {'$regex': 'Security', '$options': 'i'}})}")
        print(f"Events with duration > 0: {collection.count_documents({'duration_seconds': {'$gt': 0}})}")
        print(f"Distinct event types: {len(collection.distinct('event_type'))}")
        print(f"Distinct sources: {len(collection.distinct('source'))}")
        
        client.close()
        print("\n✅ Data loading completed successfully!")

    except Exception as e:
        print(f"❌ Error loading data into MongoDB: {e}")

if __name__ == "__main__":
    load_data()
