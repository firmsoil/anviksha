# <ins>Anviksha</ins> - Conversational Software Delivery Analytics

![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)
![MongoDB](https://img.shields.io/badge/database-MongoDB-brightgreen)
![OpenAI](https://img.shields.io/badge/AI-OpenAI%20GPT--4o-orange)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Transform your software delivery data/events into actionable business insights with natural language queries, powered by OpenAI LLMs and MongoDB aggregation frameworks.

---

![Screenshot](images/Anviksha.png)

---

## Table of Contents
- [Overview](#Overview)
- [Key Features](#Key-Features)
- [Installation & Local Setup (macOS)](#installation--local-setup-macos)
- [Example Use Cases](#Example-Use-Cases)
- [Project Structure (uses sample cicd mongodb)](#project-structure-uses-sample-cicd-mongodb)
- [Technology Stack](#Technology-Stack)
- [References](#References)
- [Contributing](#Contributing)
- [License](#License)

---

## Overview

This system provides a conversational AI interface that enables users to query MongoDB enterprise datasets — such as software delivery pipelines — using natural language. User's NLP queries are translated into MongoDB aggregation pipelines dynamically, executed safely, and the results summarized in clear, user-friendly natural-language-explanations.

---

## Key Features
- Natural language query processing with multi-turn conversational refinement  
- Dynamic translation to MongoDB aggregation pipelines with schema awareness  
- Secure query execution with performance and safety guards (result limits, validation)  
- Support for analytics on CICD pipeline events and operational software delivery metrics  
- Integration with OpenAI GPT-4o models for language understanding and summarization  
- Sample datasets and scripts provided for quick startup on local or cloud environments  
- Modular architecture designed for extensibility and enterprise-grade deployment  

---

## Installation & Local Setup (macOS)

### 1. Install MongoDB Community Edition
```bash
brew tap mongodb/brew
brew install mongodb-community@7.0
brew services start mongodb-community@7.0
```
### 2. Set up Python Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
```
### 3. Install Python Dependencies
```bash
pip install pymongo openai langchain
```
### 4. Load Sample Data
```bash
python load_data.py
```
### 5. Set OpenAI API Key Environment Variable
```bash
export OPENAI_API_KEY="your_openai_api_key_here"
```
### 6. Run the Conversational Analytics System
```bash
python main.py
```
### 7. Execute sample Query API request
```bash
curl -X POST "http://localhost:8000/api/query" \
-H "Content-Type: application/json" \
-d '{
  "query": "Show me all pipeline events since two weeks ago"
}'
```
to get the JSON response like
```bash
{"results":[{"_id":"68d896045fb8dcac2fb48c6d","event_type":"Pull Request Created","description":"Developer raises a pull request (merge request) for code review.","source":"GitLab","event_timestamp":"2025-09-27T18:57:24.978000"},{"_id":"68d896045fb8dcac2fb48c6e","event_type":"Code Review / Approval","description":"Pull request undergoes code review and approval process including security and policy checks.","source":"GitLab","event_timestamp":"2025-09-27T18:57:24.978000"},{"_id":"68d896045fb8dcac2fb48c6f","event_type":"Pipeline Created","description":"Pipeline triggered on pull request creation/update to run CI jobs.","source":"GitLab","event_timestamp":"2025-09-27T18:57:24.978000"},{"_id":"68d896045fb8dcac2fb48c70","event_type":"Pipeline Started","description":"CI pipeline execution starts with build and test jobs.","source":"GitLab","event_timestamp":"2025-09-27T18:57:24.978000"},{"_id":"68d896045fb8dcac2fb48c71","event_type":"Build Stage Started","description":"Build jobs compiling code and creating artifacts begin.","source":"GitLab","event_timestamp":"2025-09-27T18:57:24.978000"},{"_id":"68d896045fb8dcac2fb48c72","event_type":"SonarQube Code Quality Scan Started","description":"Automated SonarQube scan analyzes code quality as a gate in CI pipeline.","source":"SonarQube/GitLab","event_timestamp":"2025-09-27T18:57:24.978000"},{"_id":"68d896045fb8dcac2fb48c73","event_type":"SonarQube Code Quality Scan Completed","description":"SonarQube analysis completes; quality gate passed/failed determines pipeline continuation.","source":"SonarQube/GitLab","event_timestamp":"2025-09-27T18:57:24.978000"},{"_id":"68d896045fb8dcac2fb48c74","event_type":"SAST Security Scan Started","description":"Static Application Security Testing scan to detect code vulnerabilities begins.","source":"Security Tool","event_timestamp":"2025-09-27T18:57:24.978000"},{"_id":"68d896045fb8dcac2fb48c75","event_type":"SAST Security Scan Completed","description":"SAST scan completes; security gate validation results impact progression.","source":"Security Tool","event_timestamp":"2025-09-27T18:57:24.978000"},{"_id":"68d896045fb8dcac2fb48c76","event_type":"SCA Security Scan Started","description":"Software Composition Analysis begins to look for insecure dependencies and license risks.","source":"Security Tool","event_timestamp":"2025-09-27T18:57:24.978000"},{"_id":"68d896045fb8dcac2fb48c77","event_type":"SCA Security Scan Completed","description":"SCA scan completes; security gate validation results impact progression.","source":"Security Tool","event_timestamp":"2025-09-27T18:57:24.978000"},{"_id":"68d896045fb8dcac2fb48c78","event_type":"Security & Risk Control Gate Check Started","description":"Automated or manual security and compliance gate checks start (e.g., secrets scanning, threat modeling).","source":"Security Tools/Policies","event_timestamp":"2025-09-27T18:57:24.978000"},{"_id":"68d896045fb8dcac2fb48c79","event_type":"Security & Risk Control Gate Passed","description":"Security and compliance gates passed; pipeline allowed to continue.","source":"Security Tools","event_timestamp":"2025-09-27T18:57:24.978000"},{"_id":"68d896045fb8dcac2fb48c7a","event_type":"Security & Risk Control Gate Failed","description":"A gate failure triggers pipeline halt, manual review, or remediation steps.","source":"Security Tools","event_timestamp":"2025-09-27T18:57:24.978000"},{"_id":"68d896045fb8dcac2fb48c7b","event_type":"Artifact Validation Started","description":"Validation of artifact signatures, integrity, and compliance begins as a gate before deployment.","source":"CI/CD system","event_timestamp":"2025-09-27T18:57:24.978000"},{"_id":"68d896045fb8dcac2fb48c7c","event_type":"Artifact Validation Passed","description":"Validation successful; artifact cleared for deployment.","source":"CI/CD system","event_timestamp":"2025-09-27T18:57:24.978000"},{"_id":"68d896045fb8dcac2fb48c7d","event_type":"Artifact Validation Failed","description":"Validation failure blocks progression to deployment.","source":"CI/CD system","event_timestamp":"2025-09-27T18:57:24.978000"},{"_id":"68d896045fb8dcac2fb48c7e","event_type":"Pipeline Finished","description":"CI pipeline completes successfully or fails on pull request.","source":"GitLab","event_timestamp":"2025-09-27T18:57:24.978000"},{"_id":"68d896045fb8dcac2fb48c7f","event_type":"Merge Completed","description":"Pull request merged into main branch after passing all CI and security gates.","source":"GitLab","event_timestamp":"2025-09-27T18:57:24.978000"},{"_id":"68d896045fb8dcac2fb48c80","event_type":"CD Pipeline Started","description":"Harness CD pipeline starts deployment process to non-prod environment.","source":"Harness","event_timestamp":"2025-09-27T18:57:24.978000"},{"_id":"68d896045fb8dcac2fb48c81","event_type":"Deployment Stage Started","description":"Deployment stage to staging, QA, or testing environment begins.","source":"Harness","event_timestamp":"2025-09-27T18:57:24.978000"},{"_id":"68d896045fb8dcac2fb48c82","event_type":"Deployment Stage Finished","description":"Deployment stage completes successfully or fails.","source":"Harness","event_timestamp":"2025-09-27T18:57:24.978000"},{"_id":"68d896045fb8dcac2fb48c83","event_type":"Manual Approval Requested","description":"Manual approval for production deployment triggered as security control.","source":"Harness","event_timestamp":"2025-09-27T18:57:24.978000"},{"_id":"68d896045fb8dcac2fb48c84","event_type":"Manual Approval Given","description":"Manual approval granted after review of security/risk posture.","source":"Harness","event_timestamp":"2025-09-27T18:57:24.978000"},{"_id":"68d896045fb8dcac2fb48c85","event_type":"Manual Approval Denied","description":"Manual approval denied; pipeline paused or aborted due to security concerns.","source":"Harness","event_timestamp":"2025-09-27T18:57:24.978000"},{"_id":"68d896045fb8dcac2fb48c86","event_type":"Production Deployment Started","description":"Production deployment begins after passing all security and quality gates.","source":"Harness","event_timestamp":"2025-09-27T18:57:24.978000"},{"_id":"68d896045fb8dcac2fb48c87","event_type":"Production Deployment Finished","description":"Production deployment completes successfully or rollback initiated on failure.","source":"Harness","event_timestamp":"2025-09-27T18:57:24.978000"},{"_id":"68d896045fb8dcac2fb48c88","event_type":"Rollback Initiated","description":"Rollback initiated due to failed deployment or security incidents detected post-deployment.","source":"Harness","event_timestamp":"2025-09-27T18:57:24.978000"},{"_id":"68d896045fb8dcac2fb48c89","event_type":"Rollback Finished","description":"Rollback completes to last known good state.","source":"Harness","event_timestamp":"2025-09-27T18:57:24.978000"},{"_id":"68d896045fb8dcac2fb48c8a","event_type":"Service Monitoring Started","description":"Monitoring of deployed app instances for security incidents, anomalies, and performance starts.","source":"Harness","event_timestamp":"2025-09-27T18:57:24.978000"}],"explanation":"This pipeline filters the events from the last two weeks based on the event_timestamp, ensuring only valid event documents are included and limits the results to 1000."}%
```

---

## Example Use Cases

### Query 1: CICD Pipeline Success Rates

    Query: "Show successful builds in last 7 days by branch"

    Generated Pipeline: Filters build events, groups by branch, counts successes
  ```bash
  Pipeline: { "$match": { "eventType": "build-completed", "status": "success" } } { "$group": { "_id": "$branch", "count": { "$sum": 1 } } }
  ```
    Output: main branch → 25 builds | develop → 15 builds

### Query 2: Build Durations for Failed Builds

    Input: Average build duration for failed builds triggered by user jdoe last month
    
    Generated Pipeline: Filters by status, user, and timeframe, averages duration
    
    Output: Concise statistic highlighting bottlenecks or performance issues

---

## Project Structure (uses sample cicd mongodb)
```bash
/
├── main.py                 # Core conversational agent and query processing logic
├── load_data.py            # Sample data insertion scripts for MongoDB
├── setup.sh                # Automated environment setup bash script
├── cicd_api/               # Modular CICD analytics package
│   ├── __init__.py
│   ├── api.py              # API interfaces for CICD analytics
│   ├── events_handler.py   # Event processing for pipeline event documents
│   ├── pipeline_generator.py # MongoDB pipeline builders for CICD queries
│   ├── summaries.py        # Business summary and explanation generation
│   └── utils.py            # Helper utilities and validation functions
├── README.md               # This documentation file
```
---

## Technology Stack

* AI & NLP: OpenAI GPT-4o Mini, MCP Toolbox concepts
* Database: MongoDB Atlas & Aggregation Framework
* Programming Language: Python 3.10+ with PyMongo and OpenAI SDK
* Deployment: Kubernetes, Istio mTLS, HashiCorp Vault for security
* Observability: OpenTelemetry, Prometheus, Grafana

---

## References 

- **MongoDB, Inc. (2025). MongoDB Atlas Architecture Center.**  
  Correlates to data layer setup, Atlas cluster provisioning, and resilient storage accessed by the pipeline executor service in `main.py`.

- **MongoDB, Inc. (2024). MongoDB Architecture Guide.**  
  Foundational for schema design and indexing decisions impacting query performance in aggregation pipeline generation functions in `main.py`.

- **Google Cloud. (2022). Reference Architectures for MongoDB Atlas on Google Cloud.**  
  Underpins deployment design using Kubernetes/OpenShift referenced in `setup.sh` and microservice orchestration around the conversational API.

- **MongoDB, Inc. (2025). MongoDB Aggregation Framework.**  
  Directly informs pipeline generation and execution logic in `main.py`’s `generate_pipeline()` and `execute_pipeline()` functions.

- **MongoDB, Inc. (2025). MongoDB Change Streams.**  
  Relevant for real-time update handling and event-driven analytics components implied in the architecture appendix.

- **OpenAI. (2025). OpenAI API Documentation.**  
  Integral to the AI orchestration logic invoking LLM completions within `main.py`, facilitating natural language to pipeline translation.

- **Google Cloud. (2025). Google Vertex AI Documentation.**  
  Supports the AI model serving and orchestration infrastructure described in the architecture.

- **HashiCorp. (n.d.). Vault Kubernetes Integration.**  
  Security reference for secret management and vault integration operations mentioned in the security appendix.

- **Istio. (n.d.). Mutual TLS (mTLS) Overview.**  
  Basis for securing service mesh communication, referenced in setup scripts and deployment practices (`setup.sh`).

- **MongoDB, Inc. (2025). MongoDB Security Documentation.**  
  Guides security best practices for API and database level controls seen in authentication and RBAC implementation context.

- **Prometheus. (n.d.). Prometheus Monitoring System.**  
  Used in observability for monitoring microservices and API telemetry as noted in system monitoring descriptions.

- **ACL Anthology. (2021). Hybrid NLP: Combining Rule-based and Machine Learning.**  
  Academic grounding for the hybrid pipeline generation approach in `main.py`.

- **MongoDB, Inc. (2025). MongoDB Query for Date Range.**  
  Influences correct BSON date filtering implemented in the pipeline generation function.

- **OpenAI. (2025). OpenAI Summarization Example.**  
  Supports the summarization feature post pipeline execution in `main.py`.

- **MongoDB, Inc. (2025). Simplify AI-Driven Data Connectivity With MongoDB and MCP Toolbox.**  
  Provides reference architecture and real-world use cases guiding integration design; relevant to system modularity and data source abstraction patterns.

- **MongoDB, Inc. (2025). Announcing the MongoDB MCP Server.**  
  Key reference for multi-data source support and AI agent interaction capability, reflected in modular tool loading and extensibility in codebase.

- **Google. (2025). MongoDB | MCP Toolbox for Databases.**  
  Documentation outlines connector schema and integration points mirrored in `main.py` tool and pipeline generation logic.

- **FlowHunt. (2025). MongoDB MCP Server - FlowHunt.**  
  Example implementation of MCP server that inspired design of the backend microservices.

- **Glama.ai. (2025). MongoDB MCP Server.**  
  Demonstrates operational MCP MongoDB tooling pattern influencing our API endpoint and query executor logic.

- **Google Cloud. (2025). MongoDB Connector for Google Cloud Integration.**  
  Correlates with infrastructure provisioning and integration validation activities covered in `setup.sh` and deployment configurations.

---

## Contributing

We warmly welcome contributions from the community!

- Please open issues to report bugs or suggest new features.
- Submit pull requests with your proposed improvements.
- We encourage collaborative discussions around architectural enhancements and best practices.
- Before contributing, please review the existing issues and pull requests to avoid duplication.

Thank you for helping to make this project better together!

---
## License

This project is licensed under the MIT License.

---
