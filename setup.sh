#!/bin/bash

# setup.sh
# Shell script to set up the Agentic AI Conversational Analytics System on macOS.
# This automates:
# - Installing Homebrew (if not present)
# - Installing MongoDB Community Edition
# - Starting MongoDB service
# - Installing Python dependencies (pymongo, openai)
# - Creating and loading sample data via load_data.py
# - Creating main.py (with updated generate_pipeline and summarize_results functions)
# - Optional: Setting OpenAI API key
# - Running the system

# Check for Homebrew and install if not present
if ! command -v brew &> /dev/null; then
    echo "Homebrew not found. Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
else
    echo "Homebrew is already installed."
fi

# Update Homebrew
brew update

# Install MongoDB
echo "Installing MongoDB Community Edition..."
brew tap mongodb/brew
brew install mongodb-community@7.0

# Start MongoDB service
echo "Starting MongoDB service..."
brew services start mongodb/brew/mongodb-community@7.0

# Verify MongoDB is running
if mongosh --eval "db.runCommand({ ping: 1 })" &> /dev/null; then
    echo "MongoDB is running."
else
    echo "Failed to start MongoDB. Please check manually."
    exit 1
fi

# Install Python dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install pymongo openai

# Prompt for OpenAI API key (optional)
read -p "Enter your OpenAI API key (optional, press Enter to skip): " OPENAI_KEY
if [ ! -z "$OPENAI_KEY" ]; then
    export OPENAI_API_KEY="$OPENAI_KEY"
    echo "export OPENAI_API_KEY='$OPENAI_KEY'" >> ~/.bash_profile
    source ~/.bash_profile
    echo "OpenAI API key set."
else
    echo "Skipping OpenAI API key setup. System will use mock mode."
fi

# Create load_data.py
echo "Creating load_data.py..."
cat > load_data.py << EOL
# load_data.py
# Script to load sample data into MongoDB.

import pymongo
from datetime import datetime

MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "sales_db"
COLLECTION_NAME = "orders"

# Sample data
SAMPLE_ORDERS = [
    {
        "order_id": "ord001",
        "customer_id": "cust001",
        "product_id": "prod001",
        "quantity": 2,
        "price": 50.0,
        "order_date": datetime(2023, 1, 15),
        "status": "completed"
    },
    {
        "order_id": "ord002",
        "customer_id": "cust001",
        "product_id": "prod002",
        "quantity": 1,
        "price": 100.0,
        "order_date": datetime(2023, 2, 20),
        "status": "pending"
    },
    {
        "order_id": "ord003",
        "customer_id": "cust002",
        "product_id": "prod001",
        "quantity": 3,
        "price": 50.0,
        "order_date": datetime(2023, 3, 10),
        "status": "completed"
    },
]

SAMPLE_CUSTOMERS = [
    {"customer_id": "cust001", "name": "Alice", "email": "alice@example.com", "join_date": datetime(2022, 1, 1)},
    {"customer_id": "cust002", "name": "Bob", "email": "bob@example.com", "join_date": datetime(2022, 2, 1)},
]

SAMPLE_PRODUCTS = [
    {"product_id": "prod001", "name": "Widget A", "category": "Electronics", "stock": 100, "unit_price": 50.0},
    {"product_id": "prod002", "name": "Widget B", "category": "Electronics", "stock": 50, "unit_price": 100.0},
]

def load_data():
    client = pymongo.MongoClient(MONGO_URI)
    db = client[DB_NAME]
    
    db.orders.insert_many(SAMPLE_ORDERS)
    db.customers.insert_many(SAMPLE_CUSTOMERS)
    db.products.insert_many(SAMPLE_PRODUCTS)
    
    print("Sample data loaded.")

if __name__ == "__main__":
    load_data()
EOL

# Load sample data
echo "Loading sample data..."
python load_data.py

# Create main.py with updates
echo "Creating main.py..."
cat > main.py << EOL
# main.py
# This is the main script for the Agentic AI Conversational Analytics System.

import os
import json
import pymongo
from openai import OpenAI
from typing import List, Dict, Any

MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "sales_db"
COLLECTION_NAME = "orders"

SCHEMA = """
Collection: orders
Fields:
- order_id: string
- customer_id: string
- product_id: string
- quantity: integer
- price: number (double)
- order_date: date (ISODate)
- status: string (e.g., 'completed', 'pending', 'cancelled')

Collection: customers
Fields:
- customer_id: string
- name: string
- email: string
- join_date: date

Collection: products
Fields:
- product_id: string
- name: string
- category: string
- stock: integer
- unit_price: number
"""

openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

MOCK_RESPONSES = {
    "what is the total sales revenue?": [
        {"\$group": {"_id": None, "total_revenue": {"\$sum": {"\$multiply": ["\$quantity", "\$price"]}}}}
    ],
    "how many orders per customer?": [
        {"\$group": {"_id": "\$customer_id", "order_count": {"\$sum": 1}}}
    ],
}

def mock_llm_response(prompt: str) -> str:
    for key, pipeline in MOCK_RESPONSES.items():
        if key in prompt.lower():
            return json.dumps({"pipeline": pipeline, "explanation": f"Mock explanation for '{key}'"})
    return json.dumps({"pipeline": [], "explanation": "Mock: No matching query found."})

def generate_pipeline(query: str, history: List[Dict[str, str]]) -> tuple[List[Dict[str, Any]], str]:
    history_str = "\\n".join([f"User: {msg['query']}\\nAssistant: {msg.get('response', '')}" for msg in history])
    
    if os.getenv("OPENAI_API_KEY"):
        system_prompt = """
        You are a MongoDB query expert.
        Translate the user's natural language query into a valid MongoDB aggregation pipeline.
        Output only a JSON object: {"pipeline": [array of stages], "explanation": "brief explanation"}
        Ensure the pipeline is safe: limit results to 1000, avoid destructive operations.
        Use schema-aware logic: map terms like 'sales' to quantity*price, 'revenue' to sum of that, etc.
        For multi-turn, refine based on history (e.g., 'now filter by completed' refers to previous).
        """
        user_prompt = f"""
        Given the following schema:
        {SCHEMA}

        And the conversation history:
        {history_str}

        User's natural language query: "{query}"
        """
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"}
        )
        result = response.choices[0].message.content
    else:
        print("Warning: Using mock LLM response.")
        result = mock_llm_response(query)  # Changed to pass query instead of prompt for mock
    
    try:
        parsed = json.loads(result)
        return parsed["pipeline"], parsed["explanation"]
    except Exception as e:
        raise ValueError(f"Failed to parse LLM response: {e}")

def execute_pipeline(pipeline: List[Dict[str, Any]], db) -> List[Dict[str, Any]]:
    collection = db[COLLECTION_NAME]
    if not any("\$limit" in stage for stage in pipeline):
        pipeline.append({"\$limit": 1000})
    try:
        results = list(collection.aggregate(pipeline))
        return results
    except Exception as e:
        raise RuntimeError(f"Query execution failed: {e}")

def summarize_results(results: List[Dict[str, Any]], query: str, pipeline_explanation: str) -> str:
    results_str = json.dumps(results[:10])
    
    if os.getenv("OPENAI_API_KEY"):
        system_prompt = """
        You are a helpful summarizer.
        Provide a concise, business-friendly summary and explanation.
        Output only plain text.
        """
        user_prompt = f"""
        Given query: "{query}"
        Pipeline explanation: "{pipeline_explanation}"
        Results: {results_str}
        """
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )
        return response.choices[0].message.content
    else:
        return f"Mock summary for results: {json.dumps(results[:5], default=str)}"

def main():
    client = pymongo.MongoClient(MONGO_URI)
    db = client[DB_NAME]
    
    history: List[Dict[str, str]] = []
    print("Welcome to MongoDB Conversational Analytics System. Type 'exit' to quit.")
    
    while True:
        query = input("User query: ").strip()
        if query.lower() == 'exit':
            break
        
        try:
            pipeline, explanation = generate_pipeline(query, history)
            print(f"Generated Pipeline: {json.dumps(pipeline, indent=2)}")
            print(f"Query Explanation: {explanation}")
            
            results = execute_pipeline(pipeline, db)
            summary = summarize_results(results, query, explanation)
            print(f"Summary: {summary}")
            
            history.append({"query": query, "response": summary})
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()
EOL

# Run the system
echo "Setup complete. Starting the system..."
python main.py
