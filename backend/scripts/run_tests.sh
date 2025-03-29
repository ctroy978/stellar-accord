#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Starting Stellar Accord Tests${NC}"

# Set the path to docker-compose.yml explicitly
COMPOSE_FILE="/home/tcoop/game-project/stellar-accord/docker-compose.yml"

# Check if Docker is running and accessible
if ! docker info >/dev/null 2>&1; then
    echo -e "${RED}Error: Cannot connect to Docker daemon. Make sure Docker is running and you have permission to access it.${NC}"
    exit 1
fi

# Check if the backend container is running
if ! docker ps | grep -E "stellar-accord-backend-1" > /dev/null; then
    echo -e "${RED}Error: Backend container is not running. Starting it now...${NC}"
    docker-compose -f "$COMPOSE_FILE" up -d backend
    sleep 5  # Give it a moment to start
    if ! docker ps | grep -E "stellar-accord-backend-1" > /dev/null; then
        echo -e "${RED}Error: Backend container still not running. Check 'docker-compose logs backend'.${NC}"
        exit 1
    fi
fi

# Check if specific test module was requested
if [ $# -eq 1 ]; then
    TEST_PATH=$1
    echo -e "${YELLOW}Running specific test: ${TEST_PATH}${NC}"
    docker-compose -f "$COMPOSE_FILE" exec -T backend pytest "$TEST_PATH" -v
else
    # Run all tests
    echo -e "${YELLOW}Running all tests...${NC}"
    
    # Model tests
    echo -e "\n${GREEN}Running model tests...${NC}"
    docker-compose -f "$COMPOSE_FILE" exec -T backend pytest tests/models/ -v || echo -e "${RED}Model tests failed${NC}"
    
    # CRUD tests
    echo -e "\n${GREEN}Running CRUD operation tests...${NC}"
    docker-compose -f "$COMPOSE_FILE" exec -T backend pytest tests/crud/ -v || echo -e "${RED}CRUD tests failed${NC}"
    
    # API tests
    echo -e "\n${GREEN}Running API endpoint tests...${NC}"
    docker-compose -f "$COMPOSE_FILE" exec -T backend pytest tests/api/ -v || echo -e "${RED}API tests failed${NC}"
    
    # Integration tests
    echo -e "\n${GREEN}Running integration tests...${NC}"
    docker-compose -f "$COMPOSE_FILE" exec -T backend pytest tests/integration/ -v || echo -e "${RED}Integration tests failed${NC}"
fi

echo -e "\n${YELLOW}Tests completed!${NC}"