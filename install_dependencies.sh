#!/bin/bash

# AI Agent Services - Dependency Installation Script
# This script installs all dependencies for all microservices

echo "🚀 Starting AI Agent Services Dependency Installation"
echo "=================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# Check if Python is installed
if ! command -v python &> /dev/null; then
    print_error "Python is not installed. Please install Python 3.8+ first."
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    print_error "Node.js is not installed. Please install Node.js 16+ first."
    exit 1
fi

print_status "Python version: $(python --version)"
print_status "Node.js version: $(node --version)"

# Base directory
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
print_status "Working directory: $BASE_DIR"

# Services to install
SERVICES=(
    "main_service"
    "editor_service"
    "analyzer_service"
    "transform_service"
    "visualization_service"
    "chat_service"
    "auth_service"
)

# Install Python dependencies for each service
print_status "Installing Python dependencies for all services..."

for service in "${SERVICES[@]}"; do
    SERVICE_DIR="$BASE_DIR/services/$service"

    if [ -d "$SERVICE_DIR" ]; then
        print_status "Installing dependencies for $service..."

        # Create virtual environment if it doesn't exist
        if [ ! -d "$SERVICE_DIR/venv" ]; then
            print_status "Creating virtual environment for $service..."
            python -m venv "$SERVICE_DIR/venv"
        fi

        # Activate virtual environment and install dependencies
        source "$SERVICE_DIR/venv/bin/activate"

        if [ -f "$SERVICE_DIR/requirements.txt" ]; then
            pip install --upgrade pip
            pip install -r "$SERVICE_DIR/requirements.txt"

            if [ $? -eq 0 ]; then
                print_success "Dependencies installed for $service"
            else
                print_error "Failed to install dependencies for $service"
                deactivate
                continue
            fi
        else
            print_warning "No requirements.txt found for $service"
        fi

        deactivate
    else
        print_warning "Service directory $SERVICE_DIR not found"
    fi
done

# Install frontend dependencies
print_status "Installing frontend dependencies..."

if [ -d "$BASE_DIR/frontend" ]; then
    cd "$BASE_DIR/frontend"

    if [ -f "package.json" ]; then
        npm install

        if [ $? -eq 0 ]; then
            print_success "Frontend dependencies installed"
        else
            print_error "Failed to install frontend dependencies"
        fi
    else
        print_warning "No package.json found in frontend directory"
    fi
else
    print_warning "Frontend directory not found"
fi

# Create .env files if they don't exist
print_status "Setting up environment files..."

# Main service .env
if [ ! -f "$BASE_DIR/services/main_service/.env" ]; then
    cat > "$BASE_DIR/services/main_service/.env" << EOF
FLASK_ENV=development
FLASK_DEBUG=True
PORT=5000
JWT_SECRET_KEY=your-super-secret-jwt-key-change-in-production
MONGODB_URI=mongodb://localhost:27017/aida_db
EOF
    print_success "Created .env for main_service"
fi

# Auth service .env
if [ ! -f "$BASE_DIR/services/auth_service/.env" ]; then
    cat > "$BASE_DIR/services/auth_service/.env" << EOF
FLASK_ENV=development
FLASK_DEBUG=True
PORT=5006
JWT_SECRET_KEY=your-super-secret-jwt-key-change-in-production
MONGODB_URI=mongodb://localhost:27017/aida_db
EOF
    print_success "Created .env for auth_service"
fi

# Other services .env
for service in "${SERVICES[@]}"; do
    if [[ "$service" != "main_service" && "$service" != "auth_service" ]]; then
        SERVICE_ENV="$BASE_DIR/services/$service/.env"
        if [ ! -f "$SERVICE_ENV" ]; then
            cat > "$SERVICE_ENV" << EOF
FLASK_ENV=development
FLASK_DEBUG=True
PORT=$(echo "$service" | sed 's/_service//' | awk '{print 5000 + NR}')
EOF
            print_success "Created .env for $service"
        fi
    fi
done

# Frontend .env
if [ ! -f "$BASE_DIR/frontend/.env" ]; then
    cat > "$BASE_DIR/frontend/.env" << EOF
VITE_FLASK_API=http://localhost:5000
EOF
    print_success "Created .env for frontend"
fi

# Create uploads directories
print_status "Creating uploads directories..."
for service in "${SERVICES[@]}"; do
    UPLOAD_DIR="$BASE_DIR/services/$service/uploads"
    mkdir -p "$UPLOAD_DIR"
    print_success "Created uploads directory for $service"
done

# Create static directories for services that need them
STATIC_DIR="$BASE_DIR/services/main_service/static"
mkdir -p "$STATIC_DIR/plots"
print_success "Created static/plots directory for main_service"

# Final instructions
echo ""
echo "=================================================="
print_success "All dependencies installed successfully!"
echo ""
echo "Next steps:"
echo "1. Make sure MongoDB is running locally or update MONGODB_URI in .env files"
echo "2. Start all services: python services/start_all.py"
echo "3. Start frontend: cd frontend && npm run dev"
echo "4. Open http://localhost:5173 in your browser"
echo ""
echo "Service URLs:"
echo "- Main Service: http://localhost:5000"
echo "- Auth Service: http://localhost:5006"
echo "- Editor Service: http://localhost:5001"
echo "- Analyzer Service: http://localhost:5002"
echo "- Transform Service: http://localhost:5003"
echo "- Visualization Service: http://localhost:5004"
echo "- Chat Service: http://localhost:5005"
echo "- Frontend: http://localhost:5173"
echo ""
print_warning "Remember to change JWT_SECRET_KEY and MONGODB_URI for production!"