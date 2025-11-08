#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

API_URL="http://localhost:8080"

echo -e "${GREEN}=============================================${NC}"
echo -e "${GREEN}Anviksha Conversational Query Demo${NC}"
echo -e "${GREEN}=============================================${NC}"
echo ""
echo -e "${CYAN}Key Features to be Demonstrated:${NC}"
echo -e "  1. Natural language queries converted to MongoDB pipelines ${YELLOW}(All Queries)${NC}"
echo -e "  2. Real-time schema discovery via MCP integration ${YELLOW}(Analytical, Security, Aggregation Queries)${NC}"
echo -e "  3. Complex aggregations (grouping, counting, averaging) ${YELLOW}(Analytical, Semantic, Aggregation Queries)${NC}"
echo -e "  4. Intelligent filtering by user, type, and attributes ${YELLOW}(Semantic, Hybrid, Security Queries)${NC}"
echo -e "  5. Multi-condition queries with combined filters ${YELLOW}(Hybrid) Query${NC}"
echo -e "  6. AI-generated summaries of query results ${YELLOW}(All Queries)${NC}"
echo ""

# Function to check if API is running
check_api() {
    if ! curl -s -f "${API_URL}/api/health" > /dev/null 2>&1; then
        echo -e "${RED}❌ Error: API is not running at ${API_URL}${NC}"
        echo -e "${YELLOW}Please start the services first with: ./quickstart.sh${NC}"
        exit 1
    fi
}

# Function to display a query section
display_query() {
    local title=$1
    local query=$2
    local description=$3
    
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}[$title]${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    if [ -n "$description" ]; then
        echo -e "${YELLOW}Description: ${description}${NC}"
    fi
    echo -e "\033[1;37mQuery: \"${query}\"${NC}"
    echo -e "${CYAN}----------------------------------------${NC}"
}

# Function to execute query and display results
execute_query() {
    local query=$1
    
    # Execute the query
    response=$(curl -s -X POST "${API_URL}/api/query" \
        -H "Content-Type: application/json" \
        -d "{\"query\": \"${query}\"}")
    
    # Check if curl failed
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ Failed to execute query${NC}"
        return 1
    fi
    
    # Check if response is valid JSON
    if ! echo "$response" | jq empty 2>/dev/null; then
        echo -e "${RED}❌ Invalid JSON response${NC}"
        echo -e "${RED}Response: ${response}${NC}"
        return 1
    fi
    
    # Extract fields
    result_count=$(echo "$response" | jq -r '.results | length')
    summary=$(echo "$response" | jq -r '.summary')
    mcp_enabled=$(echo "$response" | jq -r '.mcp_enabled')
    schema_source=$(echo "$response" | jq -r '.schema_source')
    
    # Display metadata
    echo -e "${GREEN}✓ Result Count: ${result_count}${NC}"
    echo -e "${GREEN}✓ MCP Enabled: ${mcp_enabled}${NC}"
    echo -e "${GREEN}✓ Schema Source: ${schema_source}${NC}"
    echo ""
    
    # Display summary
    echo -e "${YELLOW}📊 Summary:${NC}"
    echo -e "${summary}"
    echo ""
    
    # Display sample results
    echo -e "${YELLOW}📋 Sample Results (first 5):${NC}"
    echo "$response" | jq -r '
        .results[0:5] | 
        to_entries | 
        .[] | 
        "  " + (.key + 1 | tostring) + ". " + (
            if .value.event_type then 
                # Direct event_type field (for filtered results)
                .value.event_type + 
                (if .value.count then " (" + (.value.count | tostring) + " events)" else "" end) +
                (if .value.user then " by " + .value.user else "" end) +
                (if .value.duration_seconds then " - " + (.value.duration_seconds | tostring) + "s" else "" end) +
                (if .value.avg_duration then " (avg: " + (.value.avg_duration | tostring) + "s)" else "" end)
            elif .value._id then
                # _id field contains the grouped value (for aggregations)
                (if (.value._id | type) == "string" then .value._id else (.value._id | tostring) end) + 
                (if .value.count then ": " + (.value.count | tostring) + " events" else "" end) +
                (if .value.avg_duration then " (avg: " + (.value.avg_duration | tostring) + "s)" else "" end)
            else
                # Fallback for other structures
                (. | tostring)
            end
        )
    '
    echo ""
}

# Check if API is running
check_api

echo -e "${GREEN}✓ API is running${NC}"
echo ""

read -p "Press Enter to start the demo..."
echo ""

# Demo 1: Analytical Query - Count by event type
display_query "ANALYTICAL QUERY" \
    "Count all events by event type" \
    "Aggregation query to group and count events"

execute_query "Count all events by event type"

read -p "Press Enter to continue to semantic query..."
echo ""

# Demo 2: Semantic Query - Find by user
display_query "SEMANTIC QUERY" \
    "Find all events by user John Smith" \
    "Natural language query to filter by specific user"

execute_query "Find all events by user John Smith"

read -p "Press Enter to continue to hybrid query..."
echo ""

# Demo 3: Hybrid Query - Duration filter
display_query "HYBRID QUERY" \
    "Show all events with duration greater than 0 seconds" \
    "Combining semantic understanding with numeric filtering"

execute_query "Show all events with duration greater than 0 seconds"

read -p "Press Enter to continue to additional examples..."
echo ""

# Demo 4: Security-related query
display_query "SECURITY QUERY" \
    "Show me all security scan events" \
    "MCP-enhanced query using discovered event types"

execute_query "Show me all security scan events"

read -p "Press Enter to continue to aggregation query..."
echo ""

# Demo 5: Source aggregation
display_query "AGGREGATION QUERY" \
    "Count events by source" \
    "Group events by source system and count"

execute_query "Count events by source"

read -p "Press Enter to continue to time-based query..."
echo ""

# Demo 6: Recent events
display_query "TIME-BASED QUERY" \
    "Show me the last 10 events" \
    "Retrieve most recent pipeline events"

execute_query "Show me the last 10 events"

echo ""
echo -e "${GREEN}=============================================${NC}"
echo -e "${GREEN}Demo Completed Successfully! 🎉${NC}"
echo -e "${GREEN}=============================================${NC}"
echo ""
echo -e "${YELLOW}Try your own queries:${NC}"
echo -e "  curl -X POST ${API_URL}/api/query \\"
echo -e "    -H 'Content-Type: application/json' \\"
echo -e "    -d '{\"query\": \"YOUR QUERY HERE\"}'"
echo ""
echo -e "${CYAN}Full API documentation: ${API_URL}/api/docs${NC}"
echo ""
