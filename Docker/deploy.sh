#!/bin/bash

# SEQ_SONIC Docker Deployment Script
# This script deploys the SEQ_SONIC application using Docker Compose

set -e

echo "🚀 SEQ_SONIC Docker Deployment Script"
echo "====================================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Check if .env file exists
if [ ! -f "../.env" ]; then
    echo "⚠️  .env file not found. Creating template..."
    cat > ../.env << EOF
# SEQ_SONIC Environment Variables
# Replace with your actual API keys

GROQ_API_KEY=your_groq_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here

# Optional: Override default models
GROQ_MODEL=llama-3.3-70b-versatile
OPENAI_MODEL=gpt-4o-mini
EOF
    echo "📝 Created .env template. Please edit it with your actual API keys."
    echo "🔑 You can edit the .env file and then run this script again."
    exit 1
fi

# Function to check if ports are available
check_ports() {
    local ports=("8000" "8001" "80")
    for port in "${ports[@]}"; do
        if netstat -tuln | grep -q ":$port "; then
            echo "❌ Port $port is already in use. Please free it up first."
            exit 1
        fi
    done
}

# Check ports availability
echo "🔍 Checking port availability..."
check_ports

# Build and start services
echo "🏗️  Building Docker images..."
docker-compose build

echo "🚀 Starting services..."
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check service status
echo "📊 Service Status:"
docker-compose ps

# Show access information
echo ""
echo "✅ SEQ_SONIC is now running!"
echo ""
echo "🌐 Access URLs:"
echo "   Backend API:     http://localhost:8000"
echo "   Frontend Chat:   http://localhost:8001"
echo "   API Docs:        http://localhost:8000/docs"
echo "   Health Check:    http://localhost:8000/health"
echo ""
echo "🔧 Management Commands:"
echo "   View logs:       docker-compose logs -f"
echo "   Stop services:   docker-compose down"
echo "   Restart:         docker-compose restart"
echo "   Update:          docker-compose pull && docker-compose up -d"
echo ""

# Check if nginx profile is available
if docker-compose --profile production config &> /dev/null; then
    echo "🌍 To enable Nginx reverse proxy (port 80):"
    echo "   docker-compose --profile production up -d"
fi
