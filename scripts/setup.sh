#!/bin/bash

# RAG Chatbot Setup Script

set -e

echo "🚀 Setting up RAG Chatbot..."

# Check if Docker and Docker Compose are installed
if ! docker info &> /dev/null; then
    echo "❌ Docker is not running. Please start Docker Desktop first."
    exit 1
fi

if ! docker compose version &> /dev/null && ! docker-compose --version &> /dev/null; then
    echo "❌ Docker Compose is not available. Please install Docker Compose first."
    exit 1
fi

echo "✅ Docker is running"

# Check if .env file exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env file and add your Mistral API key before running the application."
    echo "   You can get your API key from: https://console.mistral.ai/"
    echo ""
    echo "   Required configuration:"
    echo "   - MISTRAL_API_KEY=your_api_key_here"
    echo ""
    read -p "Press Enter to continue after updating .env file..."
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p documents/uploads
mkdir -p logs

# Build and start services
echo "🔨 Building Docker images..."
docker-compose build

echo "🚀 Starting services..."
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 10

# Check service health
echo "🔍 Checking service health..."

# Check Weaviate
if curl -f http://localhost:8080/v1/.well-known/ready &> /dev/null; then
    echo "✅ Weaviate is ready"
else
    echo "❌ Weaviate is not ready"
fi

# Check Backend
if curl -f http://localhost:8000/health/ &> /dev/null; then
    echo "✅ Backend is ready"
else
    echo "❌ Backend is not ready"
fi

# Check Frontend
if curl -f http://localhost:8501/_stcore/health &> /dev/null; then
    echo "✅ Frontend is ready"
else
    echo "❌ Frontend is not ready"
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "📱 Access the application:"
echo "   Frontend: http://localhost:8501"
echo "   Backend API: http://localhost:8000"
echo "   API Documentation: http://localhost:8000/docs"
echo "   Weaviate Console: http://localhost:8080"
echo ""
echo "📋 Useful commands:"
echo "   View logs: docker-compose logs -f"
echo "   Stop services: docker-compose down"
echo "   Restart services: docker-compose restart"
echo ""
