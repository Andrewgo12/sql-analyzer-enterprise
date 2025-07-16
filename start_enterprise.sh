#!/bin/bash
# SQL Analyzer Enterprise - Unix/Linux Startup Script
# Launches the enterprise system with automatic backend startup

set -e

echo ""
echo "========================================"
echo "SQL Analyzer Enterprise - Startup"
echo "========================================"
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed or not in PATH"
    echo "Please install Python 3.8+ and try again"
    exit 1
fi

# Check if Node.js is available
if ! command -v node &> /dev/null; then
    echo "ERROR: Node.js is not installed or not in PATH"
    echo "Please install Node.js and try again"
    exit 1
fi

# Check if npm is available
if ! command -v npm &> /dev/null; then
    echo "ERROR: npm is not available"
    echo "Please install Node.js with npm and try again"
    exit 1
fi

echo "Starting SQL Analyzer Enterprise..."
echo ""

# Make sure the startup script is executable
chmod +x start_enterprise.py

# Run the Python startup manager
python3 start_enterprise.py

# If we get here, the system has shut down
echo ""
echo "System has shut down."
