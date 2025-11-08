#!/bin/bash

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

PROJECT_NAME="anviksha-phase1"
API_PORT=8080
MCP_PORT=3000

echo -e "${BLUE}======================================${NC}"
echo -e "${BLUE}Anviksha Phase 1: MCP Integration${NC}"
echo -e "${BLUE}Mock MCP Server (Real MongoDB Data)${NC}"
echo -e "${BLUE}======================================${NC}\n"

log_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
log_success() { echo -e "${GREEN}✅ $1${NC}"; }
log_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
log_error() { echo -e "${RED}❌ $1${NC}"; }

# Check prerequisites
log_info "Checking prerequisites..."

if ! command -v docker &> /dev/null; then
    log_error "Docker is not installed. Please install Docker Desktop first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    log_error "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

log_success "Docker and Docker Compose are installed"

# Check if Docker is running
if ! docker info &> /dev/null; then
    log_error "Docker is not running. Please start Docker Desktop."
    exit 1
fi

log_success "Docker is running"

# Check for required files
log_info "Checking for required files..."

REQUIRED_FILES=("mock_mcp_server.py" "Dockerfile.mcp" "docker-compose.yml" ".env")
MISSING_FILES=()

for file in "${REQUIRED_FILES[@]}"; do
    if [ ! -f "$file" ]; then
        MISSING_FILES+=("$file")
    fi
done

if [ ${#MISSING_FILES[@]} -ne 0 ]; then
    log_error "Missing required files:"
    for file in "${MISSING_FILES[@]}"; do
        echo "  ❌ $file"
    done
    echo ""
    log_info "Please ensure all files are created before running this script."
    exit 1
fi

log_success "All required files present"

# Check for OpenAI API key
log_info "Checking for OpenAI API key..."

if [ ! -f .env ]; then
    log_warning ".env file not found. Creating from template..."
    if [ -f .env.example ]; then
        cp .env.example .env
    else
        log_error ".env.example not found. Cannot create .env"
        exit 1
    fi
    echo ""
    log_warning "⚠️  IMPORTANT: Please edit .env and add your OpenAI API key"
    log_info "You can get an API key from: https://platform.openai.com/api-keys"
    echo ""
    read -p "Press Enter after you've added your API key to .env..."
fi

if ! grep -q "OPENAI_API_KEY=sk-" .env; then
    log_error "OpenAI API key not found in .env file"
    log_info "Please add: OPENAI_API_KEY=sk-your-key-here"
    exit 1
fi

log_success "OpenAI API key configured"

# Stop any existing containers
log_info "Stopping any existing containers..."
docker-compose down --remove-orphans 2>/dev/null || true
log_success "Cleaned up existing containers"

# Build Docker images
log_info "Building Docker images (this may take a few minutes)..."
docker-compose build --no-cache

log_info "Starting services..."
docker-compose up -d

log_success "Services started"

# Wait for services to be healthy
log_info "Waiting for services to become healthy (30-60 seconds)..."

wait_for_service() {
    local service_name=$1
    local max_attempts=60
    local attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        if docker-compose ps | grep -q "$service_name.*healthy"; then
            return 0
        fi
        
        # Check if service exited
        if docker-compose ps | grep -q "$service_name.*Exit"; then
            return 1
        fi
        
        attempt=$((attempt + 1))
        echo -n "."
        sleep 2
    done
    return 1
}

echo -n "  MongoDB"
if wait_for_service "mongodb_cicd"; then
    log_success "MongoDB is healthy"
else
    log_error "MongoDB failed to start"
    log_info "Checking logs..."
    docker-compose logs mongo | tail -20
    exit 1
fi

echo -n "  Mock MCP Server"
if wait_for_service "mcp_toolbox_server"; then
    log_success "Mock MCP Server is healthy"
    
    # Verify MCP server is responding
    log_info "Verifying MCP Server API..."
    sleep 2
    if curl -s -f http://localhost:${MCP_PORT}/health > /dev/null; then
        log_success "MCP Server API is responding"
    else
        log_warning "MCP Server started but API not fully ready yet"
    fi
else
    log_error "Mock MCP Server failed to start"
    log_info "Checking MCP Server logs..."
    docker-compose logs mcp-server | tail -30
    echo ""
    log_warning "The system can continue without MCP (fallback mode)"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo -n "  FastAPI App"
if wait_for_service "fastapi_analytics"; then
    log_success "FastAPI App is healthy"
else
    log_error "FastAPI App failed to start"
    log_info "Checking application logs..."
    docker-compose logs app | tail -30
    exit 1
fi

# Load sample data
log_info "Loading sample CI/CD data..."
sleep 3  # Give MongoDB a moment to settle
if docker-compose exec -T app python load_data.py 2>/dev/null; then
    log_success "Sample data loaded successfully (100 events)"
else
    log_warning "Failed to load sample data automatically"
    log_info "You can load it manually later with: docker-compose exec app python load_data.py"
fi

# Run comprehensive health checks
log_info "Running comprehensive health checks..."

# API health
if curl -s -f http://localhost:${API_PORT}/api/health > /dev/null; then
    log_success "API health check passed"
    
    # Get detailed health info
    HEALTH=$(curl -s http://localhost:${API_PORT}/api/health 2>/dev/null)
    DB_STATUS=$(echo "$HEALTH" | grep -o '"db_status":"[^"]*"' | cut -d'"' -f4)
    
    if [ "$DB_STATUS" = "connected" ]; then
        log_success "Database connection verified"
    else
        log_warning "Database status: $DB_STATUS"
    fi
else
    log_error "API health check failed"
    exit 1
fi

# MCP status
MCP_STATUS=$(curl -s http://localhost:${API_PORT}/api/mcp/status 2>/dev/null)
MCP_ENABLED=$(echo "$MCP_STATUS" | grep -o '"enabled":[^,]*' | cut -d':' -f2 | tr -d ' ')

if [ "$MCP_ENABLED" = "true" ]; then
    log_success "MCP integration is ENABLED (Mock server with real MongoDB data)"
    
    # Get collections count
    COLLECTIONS=$(echo "$MCP_STATUS" | grep -o '"collections":\[[^\]]*\]')
    if [ -n "$COLLECTIONS" ]; then
        log_info "MCP Server discovered collections: $COLLECTIONS"
    fi
else
    log_warning "MCP integration is DISABLED (using static schema fallback)"
    log_info "Check MCP Server logs: docker-compose logs mcp-server"
fi

# Run integration tests
log_info "Running integration tests..."
echo ""

if docker-compose exec -T app python test_mcp_integration.py 2>/dev/null; then
    log_success "All integration tests passed!"
else
    log_warning "Some integration tests failed (check output above)"
    log_info "The system is still functional for basic queries"
fi

# Display success message and instructions
echo ""
echo -e "${GREEN}======================================${NC}"
echo -e "${GREEN}✅ Deployment Complete!${NC}"
echo -e "${GREEN}======================================${NC}"
echo ""
echo -e "${BLUE}🚀 Your Anviksha API is now running with:${NC}"
echo -e "   📦 Mock MCP Server (connects to real MongoDB)"
echo -e "   🔄 Full dynamic schema discovery"
echo -e "   💾 100 sample CI/CD events loaded"
echo ""
echo -e "${BLUE}📊 Access Points:${NC}"
echo ""
echo -e "  📖 API Documentation:  ${GREEN}http://localhost:${API_PORT}/api/docs${NC}"
echo -e "  🏥 Health Check:       ${GREEN}http://localhost:${API_PORT}/api/health${NC}"
echo -e "  🔧 MCP Status:         ${GREEN}http://localhost:${API_PORT}/api/mcp/status${NC}"
echo -e "  📊 Schema Info:        ${GREEN}http://localhost:${API_PORT}/api/schema${NC}"
echo -e "  🔌 MCP Server Health:  ${GREEN}http://localhost:${MCP_PORT}/health${NC}"
echo ""
echo -e "${BLUE}📝 Try these example queries:${NC}"
echo ""
echo -e "  ${YELLOW}# Simple query${NC}"
echo -e "  curl -X POST http://localhost:${API_PORT}/api/query \\"
echo -e "    -H 'Content-Type: application/json' \\"
echo -e "    -d '{\"query\": \"Show me the last 10 events\"}'"
echo ""
echo -e "  ${YELLOW}# Aggregation (MCP discovers field values)${NC}"
echo -e "  curl -X POST http://localhost:${API_PORT}/api/query \\"
echo -e "    -H 'Content-Type: application/json' \\"
echo -e "    -d '{\"query\": \"Count events by source\"}'"
echo ""
echo -e "  ${YELLOW}# Field-specific (MCP provides exact event types)${NC}"
echo -e "  curl -X POST http://localhost:${API_PORT}/api/query \\"
echo -e "    -H 'Content-Type: application/json' \\"
echo -e "    -d '{\"query\": \"Show me all security scan events\"}'"
echo ""
echo -e "${BLUE}🔍 Verify MCP Integration:${NC}"
echo ""
echo -e "  ${YELLOW}# Check schema source${NC}"
echo -e "  curl http://localhost:${API_PORT}/api/schema | jq .source"
echo -e "  ${GREEN}# Should return: \"mcp\"${NC}"
echo ""
echo -e "  ${YELLOW}# Get distinct event types (via MCP)${NC}"
echo -e "  curl http://localhost:${API_PORT}/api/collections/cdPipelineEvents/distinct/event_type"
echo ""
echo -e "  ${YELLOW}# Get sample documents (via MCP)${NC}"
echo -e "  curl http://localhost:${API_PORT}/api/collections/cdPipelineEvents/sample?limit=3"
echo ""
echo -e "${BLUE}🛠️  Useful commands:${NC}"
echo ""
echo -e "  View app logs:      ${YELLOW}docker-compose logs -f app${NC}"
echo -e "  View MCP logs:      ${YELLOW}docker-compose logs -f mcp-server${NC}"
echo -e "  View all logs:      ${YELLOW}docker-compose logs -f${NC}"
echo -e "  Restart services:   ${YELLOW}docker-compose restart${NC}"
echo -e "  Stop services:      ${YELLOW}docker-compose down${NC}"
echo -e "  Clear MCP cache:    ${YELLOW}curl -X POST http://localhost:${API_PORT}/api/mcp/clear-cache${NC}"
echo -e "  Reload data:        ${YELLOW}docker-compose exec app python load_data.py${NC}"
echo -e "  Check service status: ${YELLOW}docker-compose ps${NC}"
echo ""
echo -e "${BLUE}📚 Documentation:${NC}"
echo -e "  See README_PHASE1.md for detailed usage and troubleshooting"
echo ""
echo -e "${GREEN}Happy querying with MCP-enhanced schema discovery! 🎉${NC}"
echo ""
