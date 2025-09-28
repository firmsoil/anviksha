# Anviksha - Conversational Software Delivery Analytics

![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)
![MongoDB](https://img.shields.io/badge/database-MongoDB-brightgreen)
![OpenAI](https://img.shields.io/badge/AI-OpenAI%20GPT--4o-orange)
![License](https://img.shields.io/badge/license-Apache%202.0-lightgrey)

Transform your software delivery data/events into actionable business insights with natural language queries, powered by OpenAI LLMs and MongoDB aggregation frameworks.

---

## Table of Contents
- [Overview](#overview)
- [Key Features](#key-features)
- [Installation & Local Setup (macOS)](#installation--local-setup-macos)
- [Example Use Cases](#example-use-cases)
  - [CI/CD Pipeline Success Rates](#query-1-cicd-pipeline-success-rates)
  - [Build Durations for Failed Builds](#query-2-build-durations-for-failed-builds)
- [Project Structure](#project-structure)
- [Technology Stack](#technology-stack)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

This system provides a conversational AI interface that enables users to query MongoDB enterprise datasets—such as software delivery pipelines, order databases, and customer information—using natural business language. Queries are translated into MongoDB aggregation pipelines dynamically, executed safely, and the results summarized in clear, business-friendly explanations.

---

## Key Features
- Natural language query processing with multi-turn conversational refinement  
- Dynamic translation to MongoDB aggregation pipelines with schema awareness  
- Secure query execution with performance and safety guards (result limits, validation)  
- Support for analytics on CI/CD pipeline events and operational software delivery metrics  
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

### Query 1: CI/CD Pipeline Success Rates

    Input: Show successful builds in last 7 days by branch

    Generated Pipeline: Filters build events, groups by branch, counts successes
    
    Output: Summary of build counts per branch with insights for software delivery

### Query 2: Build Durations for Failed Builds

    Input: Average build duration for failed builds triggered by user jdoe last month
    
    Generated Pipeline: Filters by status, user, and timeframe, averages duration
    
    Output: Concise statistic highlighting bottlenecks or performance issues

---

## Project Structure
```bash
/
├── main.py                 # Core conversational agent and query processing logic
├── load_data.py            # Sample data insertion scripts for MongoDB
├── setup.sh                # Automated environment setup bash script
├── cicd_api/               # Modular CI/CD analytics package
│   ├── __init__.py
│   ├── api.py              # API interfaces for CI/CD analytics
│   ├── events_handler.py   # Event processing for pipeline event documents
│   ├── pipeline_generator.py # MongoDB pipeline builders for CI/CD queries
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
