#!/bin/bash

# Conversor HEIC + PDF a JPG - Robust Startup Script
# This script ensures reliable application startup with proper error handling

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$PROJECT_DIR/.venv"
REQUIREMENTS_FILE="$PROJECT_DIR/requirements.txt"
PYTHON_CMD=""

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
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

# Function to find Python command
find_python() {
    if command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
    elif command -v python &> /dev/null; then
        PYTHON_CMD="python"
    else
        print_error "Python not found! Please install Python 3.8 or higher."
        exit 1
    fi
    
    # Verify Python version
    PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | grep -oE '[0-9]+\.[0-9]+' | head -1)
    MAJOR_VERSION=$(echo $PYTHON_VERSION | cut -d. -f1)
    MINOR_VERSION=$(echo $PYTHON_VERSION | cut -d. -f2)
    
    if [ "$MAJOR_VERSION" -lt 3 ] || ([ "$MAJOR_VERSION" -eq 3 ] && [ "$MINOR_VERSION" -lt 8 ]); then
        print_error "Python 3.8 or higher is required. Found: $($PYTHON_CMD --version)"
        exit 1
    fi
    
    print_success "Python found: $($PYTHON_CMD --version)"
}

# Function to setup virtual environment
setup_venv() {
    print_status "Setting up virtual environment..."
    
    if [ ! -d "$VENV_DIR" ]; then
        print_status "Creating virtual environment..."
        $PYTHON_CMD -m venv "$VENV_DIR"
        print_success "Virtual environment created"
    else
        print_success "Virtual environment already exists"
    fi
}

# Function to activate virtual environment
activate_venv() {
    print_status "Activating virtual environment..."
    source "$VENV_DIR/bin/activate"
    
    # Verify activation
    if [ "$VIRTUAL_ENV" != "$VENV_DIR" ]; then
        print_error "Failed to activate virtual environment"
        exit 1
    fi
    
    print_success "Virtual environment activated: $VIRTUAL_ENV"
}

# Function to install dependencies
install_dependencies() {
    print_status "Installing dependencies..."
    
    # Upgrade pip first
    pip install --upgrade pip --quiet
    
    # Install requirements
    if [ -f "$REQUIREMENTS_FILE" ]; then
        pip install -r "$REQUIREMENTS_FILE" --quiet
        print_success "Dependencies installed successfully"
    else
        print_error "Requirements file not found: $REQUIREMENTS_FILE"
        exit 1
    fi
}

# Function to verify installation
verify_installation() {
    print_status "Verifying installation..."
    
    # Test critical imports
    python -c "
import sys
import traceback

critical_packages = [
    'fastapi', 'uvicorn', 'pillow_heif', 'fitz', 'PIL', 'psutil', 
    'pydantic', 'aiofiles'
]

failed_imports = []

for package in critical_packages:
    try:
        __import__(package)
        print(f'✅ {package}')
    except ImportError as e:
        failed_imports.append((package, str(e)))
        print(f'❌ {package}: {e}')

if failed_imports:
    print(f'\n❌ {len(failed_imports)} package(s) failed to import')
    sys.exit(1)
else:
    print(f'\n✅ All {len(critical_packages)} critical packages imported successfully')
"

    if [ $? -eq 0 ]; then
        print_success "Installation verification passed"
    else
        print_error "Installation verification failed"
        exit 1
    fi
}

# Function to start the application
start_application() {
    print_status "Starting Conversor HEIC + PDF a JPG..."
    echo "=================================="
    
    cd "$PROJECT_DIR"
    
    # Check if main.py exists
    if [ ! -f "app/main.py" ]; then
        print_error "Application main file not found: app/main.py"
        exit 1
    fi
    
    # Start the application
    python -m app.main
}

# Function to handle cleanup on exit
cleanup() {
    print_status "Cleaning up..."
    
    # Kill any remaining processes
    if [ -f "temp/server.pid" ]; then
        PID=$(cat temp/server.pid 2>/dev/null || echo "")
        if [ ! -z "$PID" ] && kill -0 "$PID" 2>/dev/null; then
            print_status "Stopping server process (PID: $PID)..."
            kill "$PID" 2>/dev/null || true
        fi
        rm -f temp/server.pid
    fi
    
    print_success "Cleanup completed"
}

# Trap signals for cleanup
trap cleanup EXIT INT TERM

# Main execution
main() {
    echo "🚀 Conversor HEIC + PDF a JPG - Robust Startup"
    echo "=============================================="
    
    # Navigate to project directory
    cd "$PROJECT_DIR"
    print_success "Working directory: $PROJECT_DIR"
    
    # Step 1: Find Python
    find_python
    
    # Step 2: Setup virtual environment
    setup_venv
    
    # Step 3: Activate virtual environment
    activate_venv
    
    # Step 4: Install dependencies
    install_dependencies
    
    # Step 5: Verify installation
    verify_installation
    
    # Step 6: Start application
    start_application
}

# Run main function
main "$@"
