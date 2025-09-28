import pymongo
from datetime import datetime

MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "cicd_db"
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
    {"event_type": "SAST Security Scan Completed", "description": "SAST scan completes; security gate validation results impact progression.", "source": "Security Tool"},
    {"event_type": "SCA Security Scan Started", "description": "Software Composition Analysis begins to look for insecure dependencies and license risks.", "source": "Security Tool"},
    {"event_type": "SCA Security Scan Completed", "description": "SCA scan completes; security gate validation results impact progression.", "source": "Security Tool"},
    {"event_type": "Security & Risk Control Gate Check Started", "description": "Automated or manual security and compliance gate checks start (e.g., secrets scanning, threat modeling).", "source": "Security Tools/Policies"},
    {"event_type": "Security & Risk Control Gate Passed", "description": "Security and compliance gates passed; pipeline allowed to continue.", "source": "Security Tools"},
    {"event_type": "Security & Risk Control Gate Failed", "description": "A gate failure triggers pipeline halt, manual review, or remediation steps.", "source": "Security Tools"},
    {"event_type": "Artifact Validation Started", "description": "Validation of artifact signatures, integrity, and compliance begins as a gate before deployment.", "source": "CI/CD system"},
    {"event_type": "Artifact Validation Passed", "description": "Validation successful; artifact cleared for deployment.", "source": "CI/CD system"},
    {"event_type": "Artifact Validation Failed", "description": "Validation failure blocks progression to deployment.", "source": "CI/CD system"},
    {"event_type": "Pipeline Finished", "description": "CI pipeline completes successfully or fails on pull request.", "source": "GitLab"},
    {"event_type": "Merge Completed", "description": "Pull request merged into main branch after passing all CI and security gates.", "source": "GitLab"},
    {"event_type": "CD Pipeline Started", "description": "Harness CD pipeline starts deployment process to non-prod environment.", "source": "Harness"},
    {"event_type": "Deployment Stage Started", "description": "Deployment stage to staging, QA, or testing environment begins.", "source": "Harness"},
    {"event_type": "Deployment Stage Finished", "description": "Deployment stage completes successfully or fails.", "source": "Harness"},
    {"event_type": "Manual Approval Requested", "description": "Manual approval for production deployment triggered as security control.", "source": "Harness"},
    {"event_type": "Manual Approval Given", "description": "Manual approval granted after review of security/risk posture.", "source": "Harness"},
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

