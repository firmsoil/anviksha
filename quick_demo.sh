#!/bin/bash

echo "============================================="
echo "Anviksha Conversational Query Demo Started"
echo "============================================="
echo ""

echo "[ANALYTICAL QUERY] Count all events by event type"
echo "Query: Count all events by event type"
echo "----------------------------------------"
curl -s -X POST http://localhost:8080/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Count all events by event type"}' \
  | jq -r '
    "Result Count: " + (.results | length | tostring),
    "",
    "Summary:",
    .summary,
    "",
    "Top 5 Event Types:",
    (.results[0:5] | .[] | "• " + .event_type + ": " + (.count | tostring) + " events"),
    ""
  '

echo ""
read -p "Press Enter for semantic query..."
echo ""

echo "[SEMANTIC QUERY] Find events by user John Smith"
echo "Query: Find all events by user John Smith"
echo "----------------------------------------"
curl -s -X POST http://localhost:8080/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Find all events by user John Smith"}' \
  | jq -r '
    "Result Count: " + (.results | length | tostring),
    "",
    "Summary:",
    .summary,
    "",
    "John Smith Events by Type:",
    (.results[0:5] | .[] | "• " + ._id + ": " + (.count | tostring) + " events (avg: " + (.avg_duration | tostring) + "s)"),
    ""
  '

echo ""
read -p "Press Enter for hybrid query..."
echo ""

echo "[HYBRID QUERY] Show all events with duration greater than 0"
echo "Query: Show all events with duration greater than 0 seconds"
echo "----------------------------------------"
curl -s -X POST http://localhost:8080/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Show all events with duration greater than 0 seconds"}' \
  | jq -r '
    "Result Count: " + (.results | length | tostring),
    "",
    "Summary:",
    .summary,
    "",
    "Sample Events with Duration:",
    (.results[0:5] | .[] | "• " + .event_type + " by " + .user + " (" + (.duration_seconds | tostring) + "s)"),
    ""
  '

echo ""
echo "=============================================="
echo "Anviksha Conversational Query Demo Completed"
echo "=============================================="
