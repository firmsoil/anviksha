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
- [Project Structure (uses sample cicd mongodb)](#project-structure-uses-sample-cicd-mongodb)
- [Technology Stack](#Technology-Stack)
- [Architecture](#Architecture)
- [References](#References)
- [Contributing](#Contributing)
- [License](#License)

---

## 🚀 Overview

Anviksha Analytics provides a conversational AI interface that enables users to query MongoDB enterprise datasets — such as software delivery pipelines — using natural language. User's NLP queries are translated into MongoDB aggregation pipelines dynamically, executed safely, and the results summarized in clear, user-friendly natural-language-explanations. The core purpose of Anviksha Analytics is to bridge the gap between business questions and technical data retrieval. Instead of writing complex MongoDB queries to calculate averages, filter events, or count occurrences, users simply ask a question via the web interface.

**Example Query:** *"Which event type takes the longest on average?"*

The system then automatically generates the correct MongoDB pipeline, executes it against the event database, and returns a summarized answer.

---

## ✨ Key Features

* **Natural Language to Query (NL2Q):** Utilizes the Gemini LLM to convert complex natural language into precise MongoDB Aggregation Pipelines (JSON).

* **Dynamic Translation:** MongoDB aggregation pipelines with schema awareness.

* **Secure Query:** Wuery execution with performance and safety guards (result limits, validation) 

* **End-to-End Dockerization:** All services (API, Database) are containerized for easy deployment and local development using Docker Compose.

* **Robust Data Modeling:** The data loader (`load_data.py`) ensures clean data with necessary numerical fields (e.g., `duration_seconds`) for accurate aggregation and analysis.

* **Interactive Web Dashboard:** A single-file HTML/JavaScript frontend provides a user-friendly interface to submit queries and view summarized, detailed, and raw JSON results.

* **Enhanced Stability:** Implements robust error handling and proper dependency management, ensuring the FastAPI container remains stable under load.

* **Modular Architecture:** Designed for extensibility and enterprise-grade deployment (e.g. Vertex AI on Google Cloud).

---

## 🛠️ Installation & Local Setup (macOS)

Follow these steps to get **Anviksha Analytics** fully operational on your machine.

### Prerequisites

* Docker and Docker Compose installed.

* A valid **Gemini API Key** (or an equivalent LLM API Key, depending on the implementation in `pipeline.py`).

### 1. Build and Run Containers

This command builds the application image, installing all required Python dependencies (including the `requests` library for the LLM API calls), and starts both the FastAPI and MongoDB containers in the background.

### 2. Execute NLP Query API request
```bash
curl http://localhost:8080/api/query -X POST -H "Content-Type: application/json" -d '{"query": "Which event type takes the longest on average?", "session_id": "llm_test_session"}'
```
to get the JSON response like
```bash
{"query_text":"Which event type takes the longest on average?","summary":"The aggregation pipeline analysis reveals that the \"Code Review / Approval\" event type has the longest average duration, recorded at 3,482.5 seconds. This was determined by grouping event types, calculating their average durations, sorting them in descending order, and selecting the top result.","pipeline_explanation":"This aggregation pipeline groups the events by 'event_type' to calculate the average duration (in seconds) for each event type using $avg. It then sorts the results in descending order based on the average duration and limits the output to the top result, which indicates the event type that takes the longest on average.","mongodb_pipeline":[{"$group":{"_id":"$event_type","average_duration":{"$avg":"$duration_seconds"}}},{"$sort":{"average_duration":-1}},{"$limit":1}],"results":[{"_id":"Code Review / Approval","average_duration":3482.5}]}%
```
---

## Project Structure (uses sample cicd mongodb)
```bash
/
├── Dockerfile                  # Defines the Python environment and application container build
├── docker-compose.yml          # Defines the 'app' and 'mongo' services, volumes, and ports
├── requirements.txt            # Python dependencies (fastapi, pymongo, requests, etc.)
├── load_data.py                # Script to populate the MongoDB with sample CI/CD data
├── README.md                   # Project documentation (Anviksha Analytics)
├── index.html                  # Single-file web dashboard (Frontend UI)
└── cicd_api/                   # FastAPI application package
    ├── __init__.py
    ├── main.py                 # Core API setup and routing (FastAPI entry point)
    └── pipeline.py             # LLM logic for converting Natural Language to MongoDB pipeline
```
---

## Technology Stack

* **AI & NLP:** **Google Gemini** (Large Language Model for Natural Language to Query translation).
* **Backend API:** **Python** (FastAPI) and **Uvicorn** (ASGI server).
* **Database:** **MongoDB** (Containerized) leveraging the **MongoDB Aggregation Framework**.
* **Frontend UI:** **HTML**, **JavaScript**, and **Tailwind CSS** for a responsive web dashboard.
* **Containerization:** **Docker** and **Docker Compose** for local deployment and service orchestration.

---

## 🧱 Architecture

The system is built on a containerized microservices architecture:

| Component | Technology | Role | 
 | ----- | ----- | ----- | 
| **Frontend** | HTML/Tailwind CSS/JS | Simple, responsive web dashboard for query input and result display. | 
| **API (`app` service)** | Python, FastAPI | Serves the `/api/query` endpoint, handles the LLM translation, and connects to MongoDB. | 
| **LLM** | Google Gemini (via API) | Converts user text into MongoDB Aggregation Pipeline JSON. | 
| **Database (`mongo` service)** | MongoDB | Stores the raw CI/CD event data. | 

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
