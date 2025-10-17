#!/bin/bash

# Test script for Smart City Data Generator
# This script tests all major functionality

echo "========================================"
echo "Smart City Data Generator - Test Suite"
echo "========================================"
echo ""

# Function to check exit status
check_status() {
    if [ $? -eq 0 ]; then
        echo "✓ $1 passed"
    else
        echo "✗ $1 failed"
        exit 1
    fi
}

# Test 1: Help command
echo "Test 1: Testing help command..."
python main.py help > /dev/null 2>&1
check_status "Help command"
echo ""

# Test 2: List poles
echo "Test 2: Listing smart poles..."
python main.py list > /dev/null 2>&1
check_status "List poles"
echo ""

# Test 3: Generate single cycle
echo "Test 3: Generating single data cycle..."
python main.py generate > /dev/null 2>&1
check_status "Generate data"
echo ""

# Test 4: View latest data
echo "Test 4: Viewing latest data..."
python main.py view > /dev/null 2>&1
check_status "View data"
echo ""

# Test 5: Turn on a pole
echo "Test 5: Turning on SP005..."
python main.py control SP005 on > /dev/null 2>&1
check_status "Turn on pole"
echo ""

# Test 6: Turn off a pole
echo "Test 6: Turning off SP005..."
python main.py control SP005 off > /dev/null 2>&1
check_status "Turn off pole"
echo ""

# Test 7: Toggle a pole
echo "Test 7: Toggling SP005..."
python main.py control SP005 toggle > /dev/null 2>&1
check_status "Toggle pole"
echo ""

# Test 8: Generate data again
echo "Test 8: Generating data after control changes..."
python main.py generate > /dev/null 2>&1
check_status "Generate after control"
echo ""

# Test 9: Database query
echo "Test 9: Querying database directly..."
docker compose exec -T postgres psql -U admin -d smart_city -c "SELECT COUNT(*) FROM smart_pole_energy;" > /dev/null 2>&1
check_status "Database query"
echo ""

echo "========================================"
echo "All tests passed! ✓"
echo "========================================"
