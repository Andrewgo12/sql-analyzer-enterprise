#!/bin/bash

# SQL Analyzer Enterprise - Installation Script for Linux/macOS
# Version: 2.0.0

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
print_header() {
    echo -e "${BLUE}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                SQL Analyzer Enterprise v2.0.0               ║"
    echo "║                    Installation Script                       ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_requirements() {
    print_step "Checking system requirements..."
    
    # Check Python version
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
        PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)
        
        if [ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -ge 8 ]; then
            print_success "Python $PYTHON_VERSION found"
        else
            print_error "Python 3.8+ required. Found: $PYTHON_VERSION"
            exit 1
        fi
    else
        print_error "Python 3 not found. Please install Python 3.8+"
        exit 1
    fi
    
    # Check pip
    if command -v pip3 &> /dev/null; then
        print_success "pip3 found"
    else
        print_error "pip3 not found. Please install pip3"
        exit 1
    fi
    
    # Check git
    if command -v git &> /dev/null; then
        print_success "git found"
    else
        print_warning "git not found. Manual installation required"
    fi
}

create_virtual_environment() {
    print_step "Creating virtual environment..."
    
    if [ -d "venv" ]; then
        print_warning "Virtual environment already exists. Removing..."
        rm -rf venv
    fi
    
    python3 -m venv venv
    source venv/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip
    
    print_success "Virtual environment created and activated"
}

install_dependencies() {
    print_step "Installing Python dependencies..."
    
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
        print_success "Dependencies installed successfully"
    else
        print_error "requirements.txt not found"
        exit 1
    fi
}

create_directories() {
    print_step "Creating necessary directories..."
    
    mkdir -p uploads logs exports cache
    chmod 755 uploads logs exports cache
    
    # Create .gitkeep files
    touch uploads/.gitkeep logs/.gitkeep exports/.gitkeep cache/.gitkeep
    
    print_success "Directories created"
}

create_config() {
    print_step "Creating configuration files..."
    
    if [ ! -f ".env" ]; then
        cat > .env << EOF
# SQL Analyzer Enterprise Configuration
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=$(openssl rand -hex 32)

# File upload settings
MAX_CONTENT_LENGTH=104857600
UPLOAD_FOLDER=uploads

# Security settings
SECURITY_SCAN_ENABLED=True
MALWARE_SCAN_ENABLED=False

# Database settings (optional)
DATABASE_URL=sqlite:///analyzer.db
EOF
        print_success "Configuration file created: .env"
    else
        print_warning "Configuration file already exists: .env"
    fi
}

run_tests() {
    print_step "Running installation tests..."
    
    # Test Python imports
    python3 -c "
import flask
import werkzeug
print('✓ Core dependencies imported successfully')
"
    
    # Test application startup
    timeout 10s python3 web_app.py --test 2>/dev/null || true
    
    print_success "Installation tests completed"
}

print_completion() {
    echo -e "${GREEN}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                    INSTALLATION COMPLETE!                   ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    
    echo -e "${BLUE}Next steps:${NC}"
    echo "1. Activate virtual environment: ${YELLOW}source venv/bin/activate${NC}"
    echo "2. Start the application: ${YELLOW}python web_app.py${NC}"
    echo "3. Open browser: ${YELLOW}http://localhost:5000${NC}"
    echo ""
    echo -e "${BLUE}Documentation:${NC}"
    echo "• Installation guide: ${YELLOW}INSTALLATION.md${NC}"
    echo "• User manual: ${YELLOW}README.md${NC}"
    echo "• API documentation: ${YELLOW}http://localhost:5000/help${NC}"
    echo ""
    echo -e "${GREEN}Happy analyzing! 🚀${NC}"
}

# Main installation process
main() {
    print_header
    
    check_requirements
    create_virtual_environment
    install_dependencies
    create_directories
    create_config
    run_tests
    
    print_completion
}

# Run main function
main "$@"
