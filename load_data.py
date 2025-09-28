import pymongo
from datetime import datetime
import os # <-- Need to import os to read environment variables

# Read MONGO_URI from the environment, defaulting to the service name 'mongo'
# which is accessible via the Docker network.
MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongo:27017/")
DB_NAME = os.getenv("DB_NAME", "cicd_db")
COLLECTION_NAME = "cdPipelineEvents"

EVENT_RECORDS = [
    {"event_type": "Pull Request Created", "description": "Developer raises a pull request (merge request) for code review.", "source": "GitLab"},
    {"event_type": "Code Review / Approval", "description": "Pull request undergoes code review and approval process including security and policy checks.", "source": "GitLab"},
    {"event_type": "Pipeline Created", "description": "Pipeline triggered on pull request creation/update to run CI jobs.", "source": "GitLab"},
    {"event_type": "Pipeline Started", "description": "CI pipeline execution starts with build and test jobs.", "source": "GitLab"},
    {"event_type": "Build Stage Started", "description": "Build jobs compiling code and creating artifacts begin.", "source": "GitLab"},
    {"event_type": "SonarQube Code Quality Scan Started", "description": "Automated SonarQube scan analyzes code quality as a gate in CI pipeline.", "source": "SonarQube/GitLab"},
    {"event_type": "SonarQube Code Quality Scan Completed", "description": "SonarQube analysis completes; quality gate passed/failed determines pipeline continuation.", "source": "SonarQube/GitLab"},
    {"event_type": "SAST Security Scan Started", "description": "Static Application Security Testing scan to detect code vulnerabilities begins.", "source": "Security Tool"},
    {"event_type": "SAST Security Scan Completed", "description": "SAST scan finishes; pipeline proceeds if security gates are passed.", "source": "Security Tool"},
    {"event_type": "Vulnerability Report Generated", "description": "Detailed vulnerability report produced by the security scanning tool.", "source": "Security Tool"},
    {"event_type": "Deployment Stage Started", "description": "CD deployment stage starts, targeting staging or pre-production environment.", "source": "Harness"},
    {"event_type": "Manual Approval Required", "description": "Pipeline pauses awaiting manual sign-off for deployment to production.", "source": "Harness"},
    {"event_type": "Manual Approval Granted", "description": "Manual approval is granted; pipeline execution continues.", "source": "Harness"},
    {"event_type": "Manual Approval Denied", "description": "Manual approval denied; pipeline paused or aborted due to security concerns.", "source": "Harness"},
    {"event_type": "Production Deployment Started", "description": "Production deployment begins after passing all security and quality gates.", "source": "Harness"},
    {"event_type": "Production Deployment Finished", "description": "Production deployment completes successfully or rollback initiated on failure.", "source": "Harness"},
    {"event_type": "Rollback Initiated", "description": "Rollback initiated due to failed deployment or security incidents detected post-deployment.", "source": "Harness"},
    {"event_type": "Rollback Finished", "description": "Rollback completes to last known good state.", "source": "Harness"},
    {"event_type": "Service Monitoring Started", "description": "Monitoring of deployed app instances for security incidents, anomalies, and performance starts.", "source": "Harness"},
]

def load_data():
    client = pymongo.MongoClient(MONGO_URI)
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]
    
    # Clear old data if any
    collection.delete_many({})
    
    # Add event_timestamp field with current timestamp to all events
    for event in EVENT_RECORDS:
        event["event_timestamp"] = datetime.now()
        
    collection.insert_many(EVENT_RECORDS)
    print(f"Loaded {len(EVENT_RECORDS)} CICD event records into {DB_NAME}.{COLLECTION_NAME} with event_timestamp")

if __name__ == "__main__":
    load_data()
