# <ins>Anviksha</ins> - Conversational Software Delivery Analytics

![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)
![MongoDB](https://img.shields.io/badge/database-MongoDB-brightgreen)
![OpenAI](https://img.shields.io/badge/AI-OpenAI%20GPT--4o-orange)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Transform your software delivery data/events into actionable business insights with natural language queries powered by Agentic AI LLMs and MongoDB aggregation frameworks.

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

This system provides a conversational AI interface that enables users to query MongoDB enterprise datasets — such as software delivery pipeline events — using natural language. User's NLP queries are translated into MongoDB aggregation pipelines dynamically, executed safely, and the results summarized in clear, user-friendly natural-language-explanations.

---

## Key Features
- **Natural Language Processing**: Convert plain English queries into MongoDB aggregation pipelines
- **AI-Powered Analytics**: OpenAI GPT-4o integration for intelligent query understanding and result summarization
- **Real-time Query Execution**: Dynamic pipeline generation with secure MongoDB execution
- **Interactive Demos**: Pretty-printed output with `quick_demo.sh` for showcasing capabilities
- **Automated Testing**: Comprehensive test suite with `test_prototype.sh` for validation
- **RESTful API**: FastAPI-based endpoints with interactive documentation at `/api/docs`
- **Dockerized Deployment**: Complete containerized stack with MongoDB and FastAPI services
- **Sample Data**: Pre-loaded CI/CD pipeline events for immediate testing and demonstration
- **Modular Architecture**: Extensible design for enterprise-grade deployment and customization  

---

## Installation & Local Setup (macOS)


### Step 1: Install Prerequisites
```bash
    Ensure you have the following software installed on your system:
    Ensure Docker Desktop is running before proceeding.
    Ensure Python3 is installed.
    Ensure MongoDB is installed and running
```

### Step 2: Clone the Repository
```bash
    git clone https://github.com/your-org/anviksha-analytics.git
    # Navigate into the project directory
    cd anviksha
```
## Step 3: Configure Environment Variables

The application requires the OPENAI_API_KEY to be passed to the Docker container. We recommend using a .env file or exporting the variable in your terminal session.

```bash
    # .env
    OPENAI_API_KEY="sk-..."
```
⚠️ IMPORTANT: Replace "sk-..." with your actual OpenAI API Key. The other variables are defaults for the Docker network and should match your docker-compose.yml.

## Step 4: Build and Start the Application Stack

```bash
    # With Docker Desktop running and the .env file configured, launch the entire stack
    docker-compose up --build -d
```

## Step 5: Load Initial Sample Data
    
The load_data.py script needs to run once to seed your MongoDB instance with sample CI/CD events.

```bash
    # Execute the load_data.py script inside the FastAPI container
    docker-compose exec app python load_data.py
```

## Step 6: Verification

Your system should now be fully operational. Check Container Status:

```bash    
    docker-compose ps
```
Both the `mongodb_cicd` and `fastapi_analytics` services should show their status as Up.

## Step 7: Test the Application

### Quick Demo (Interactive)
```bash
    # Run the interactive demo with pretty-printed output
    ./quick_demo.sh
```

### Automated Tests
```bash
    # Run the automated test suite
    ./test_prototype.sh
```

### Manual API Testing
```bash
    # Health check
    curl http://localhost:8080/api/health
    
    # Sample query
    curl http://localhost:8080/api/query -X POST -H "Content-Type: application/json" \
      -d '{"query": "Count all events by event type", "session_id": "test_session"}'
```

### API Documentation
Visit `http://localhost:8080/api/docs` for interactive API documentation.

---

## Current Capabilities & Demo Scripts

### 🚀 Quick Start Demo
The `quick_demo.sh` script provides an interactive demonstration of the conversational analytics capabilities:

- **Analytical Queries**: Count events by type, duration analysis, user activity patterns
- **Semantic Queries**: Find events by user, filter by event characteristics  
- **Hybrid Queries**: Complex analytics combining multiple data dimensions
- **Pretty-Printed Output**: Formatted results with clear summaries and data highlights

### 🧪 Automated Testing
The `test_prototype.sh` script runs comprehensive tests to validate:

- API endpoint functionality
- MongoDB connectivity
- Query processing accuracy
- Result formatting and summarization

### 📊 Sample Data
The system comes pre-loaded with 100 sample CI/CD pipeline events including:

- **Event Types**: Build stages, security scans, deployments, approvals
- **Users**: John Smith, Jane Doe, DeveloperX, SystemUser-CI
- **Sources**: GitLab, Jenkins, Security Tool, Harness
- **Metrics**: Duration tracking, pipeline IDs, environment metadata

---

## Project Structure
```bash
/
├── main.py                 # Legacy main entry point (deprecated)
├── load_data.py            # Sample data insertion scripts for MongoDB
├── setup.sh                # Automated environment setup bash script
├── quick_demo.sh           # Interactive demo script with pretty-printed output
├── test_prototype.sh       # Automated test suite for API endpoints
├── cicd_api/               # FastAPI-based CICD analytics package
│   ├── __init__.py
│   ├── api_main.py         # FastAPI application with conversational query endpoints
│   ├── db.py               # Database connection and management
│   ├── models.py           # Pydantic models for request/response schemas
│   └── pipeline.py          # LLM-powered pipeline generation and execution
├── docker-compose.yml      # Docker orchestration configuration
├── Dockerfile             # FastAPI application container definition
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (API keys, etc.)
├── images/                # Project assets and screenshots
│   └── Anviksha.png
├── README.md              # This documentation file
└── LICENSE                # MIT License
```
---

## Technology Stack

This stack is designed for modern conversational analytics, combining AI-powered natural language processing with robust data management and containerized deployment.

| Category      | Core Technologies      | Function / Purpose |
|---------------|------------------------|--------------------|
| **AI & NLP**  | OpenAI GPT-4o Mini     | Primary LLM for natural language query understanding, MongoDB pipeline generation, and intelligent result summarization. |
|               | LangChain              | Framework for building LLM applications with chain-of-thought reasoning and prompt management. |
|               | LangGraph              | Advanced workflow orchestration for complex multi-step AI reasoning and data processing. |
| **Backend**   | FastAPI                | Modern, fast web framework for building RESTful APIs with automatic OpenAPI documentation. |
|               | Uvicorn                | High-performance ASGI server for running FastAPI applications in production. |
|               | Pydantic               | Data validation and serialization using Python type annotations for request/response models. |
| **Database**  | MongoDB 8.0+          | Document database for storing CI/CD pipeline events with flexible schema and rich querying. |
|               | PyMongo                | Official Python driver for MongoDB connectivity and aggregation pipeline execution. |
|               | Aggregation Framework  | Server-side data processing for complex analytics and real-time pipeline generation. |
| **Programming** | Python 3.11+         | Core language for backend application, AI integration, and data processing logic. |
|               | Python-multipart       | Support for file uploads and form data processing in FastAPI endpoints. |
|               | Python-dateutil        | Advanced date and time parsing for handling temporal data in CI/CD events. |
|               | Dateparser             | Natural language date parsing for user-friendly temporal query processing. |
| **Deployment** | Docker                | Containerization for consistent deployment across development and production environments. |
|               | Docker Compose         | Multi-container orchestration for MongoDB and FastAPI services with networking. |
|               | Python 3.11-slim       | Lightweight base image for optimized container size and security. |
| **Utilities** | Requests               | HTTP client library for external API integrations and service communication. |


---

## References 

### Core Framework & Architecture
- **FastAPI. (2024). FastAPI Documentation.**  
  Foundation for the RESTful API architecture, providing automatic OpenAPI documentation and request/response validation.

- **Pydantic. (2024). Pydantic Documentation.**  
  Data validation and serialization framework for type-safe request/response schemas and MongoDB ObjectId handling.

- **Uvicorn. (2024). Uvicorn ASGI Server.**  
  High-performance ASGI server for running FastAPI applications in production environments.

### AI & Natural Language Processing
- **OpenAI. (2024). OpenAI API Documentation.**  
  Core LLM integration for natural language query understanding, MongoDB pipeline generation, and intelligent result summarization.

- **LangChain. (2024). LangChain Documentation.**  
  Framework for building LLM applications with chain-of-thought reasoning and conversational query processing.

- **LangGraph. (2024). LangGraph Documentation.**  
  Advanced workflow orchestration for complex multi-step AI reasoning and data processing in analytics pipelines.

### Database & Data Processing
- **MongoDB, Inc. (2025). Simplify AI-Driven Data Connectivity With MongoDB and MCP Toolbox.**  
  [MongoDB MCP Toolbox Blog](https://www.mongodb.com/company/blog/innovation/simplify-ai-driven-data-connectivity-mcp-toolbox) - Provides reference architecture for AI-driven data connectivity using Model Context Protocol (MCP) servers, directly influencing conversational query processing and MongoDB integration patterns.

- **MongoDB, Inc. (2024). MongoDB Aggregation Framework.**  
  Directly informs the pipeline generation and execution logic for dynamic query processing and data transformation.

- **PyMongo. (2024). PyMongo Documentation.**  
  Official Python driver for MongoDB connectivity, connection management, and aggregation pipeline execution.

- **MongoDB, Inc. (2024). MongoDB Query for Date Range.**  
  Influences correct BSON date filtering and temporal query processing in pipeline generation.

### Containerization & Deployment
- **Docker, Inc. (2024). Docker Documentation.**  
  Containerization strategy for consistent deployment across development and production environments.

- **Docker Compose. (2024). Docker Compose Documentation.**  
  Multi-container orchestration for MongoDB and FastAPI services with networking configuration.

### Data Processing & Utilities
- **Python-dateutil. (2024). Python-dateutil Documentation.**  
  Advanced date and time parsing for handling temporal data in CI/CD events and sample data generation.

- **Dateparser. (2024). Dateparser Documentation.**  
  Natural language date parsing for user-friendly temporal query processing in conversational analytics.

- **Requests. (2024). Requests Documentation.**  
  HTTP client library for external API integrations and service communication in FastAPI applications.

### Sample Data & Testing
- **MongoDB, Inc. (2024). MongoDB Sample Data Patterns.**  
  Influences the sample CI/CD event data structure and generation patterns for realistic testing scenarios.

- **FastAPI. (2024). FastAPI Testing Documentation.**  
  Testing patterns and validation approaches for API endpoint functionality verification.

### Academic & Research Foundations
- **ACL Anthology. (2021). Hybrid NLP: Combining Rule-based and Machine Learning.**  
  Academic grounding for the hybrid pipeline generation approach combining LLM reasoning with structured MongoDB queries.

- **OpenAI. (2024). OpenAI Summarization Best Practices.**  
  Supports the intelligent summarization feature for post-pipeline execution result interpretation.

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
