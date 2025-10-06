#!/bin/bash

echo "=== Vector Search Prototype Tests ==="
echo ""

# Test 1: Analytical
echo "TEST 1: Analytical Query"
curl -s -X POST http://localhost:8080/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "How many deployment events in production?", "session_id": "test1"}' \
  | python3 -c "import sys, json; d=json.load(sys.stdin); print(f\"Type: {d.get('query_type', 'N/A')}\nSummary: {d.get('summary', 'N/A')[:200]}...\")"

echo -e "\n---\n"

# Test 2: Semantic
echo "TEST 2: Semantic Query"
curl -s -X POST http://localhost:8080/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Find events similar to security scan failures", "session_id": "test2"}' \
  | python3 -c "import sys, json; d=json.load(sys.stdin); print(f\"Type: {d.get('query_type', 'N/A')}\nPipeline: {d.get('mongodb_pipeline', [{}])[0].keys()}\nSummary: {d.get('summary', 'N/A')[:200]}...\")"

echo -e "\n---\n"

# Test 3: Hybrid
echo "TEST 3: Hybrid Query"
curl -s -X POST http://localhost:8080/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Average duration of events similar to production deployments", "session_id": "test3"}' \
  | python3 -c "import sys, json; d=json.load(sys.stdin); print(f\"Type: {d.get('query_type', 'N/A')}\nSummary: {d.get('summary', 'N/A')[:200]}...\")"

echo -e "\n=== Tests Complete ==="