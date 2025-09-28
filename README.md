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
- [Installation & Local Setup (macOS)](#Installation-&-Local-Setup-(macOS))
- [Example Use Cases](#Example-Use-Cases)
- [Project Structure (uses sample cicd mongodb)](#Project-Structure-(uses-sample-cicd-mongodb))
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
