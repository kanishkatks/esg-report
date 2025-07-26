#!/bin/bash

# RAG Chatbot Test Script

set -e

echo "🧪 Testing RAG Chatbot..."

BACKEND_URL="http://localhost:8000"
FRONTEND_URL="http://localhost:8501"
WEAVIATE_URL="http://localhost:8080"

# Function to check if a service is running
check_service() {
    local url=$1
    local name=$2

    if curl -f "$url" &> /dev/null; then
        echo "✅ $name is running"
        return 0
    else
        echo "❌ $name is not running"
        return 1
    fi
}

# Function to test API endpoint
test_api() {
    local endpoint=$1
    local name=$2
    local expected_status=${3:-200}

    echo "Testing $name..."
    response=$(curl -s -w "%{http_code}" "$BACKEND_URL$endpoint")
    status_code="${response: -3}"

    if [ "$status_code" -eq "$expected_status" ]; then
        echo "✅ $name test passed (HTTP $status_code)"
        return 0
    else
        echo "❌ $name test failed (HTTP $status_code)"
        return 1
    fi
}

# Check if services are running
echo "🔍 Checking services..."
check_service "$WEAVIATE_URL/v1/.well-known/ready" "Weaviate"
check_service "$BACKEND_URL/health/" "Backend API"
check_service "$FRONTEND_URL/_stcore/health" "Frontend"

echo ""
echo "🧪 Running API tests..."

# Test health endpoint
test_api "/health/" "Health Check"

# Test root endpoint
test_api "/" "Root Endpoint"

# Test document stats
test_api "/documents/stats" "Document Stats"

# Test supported formats
test_api "/documents/supported-formats" "Supported Formats"

# Test search endpoint (should work even with no documents)
echo "Testing Search endpoint..."
search_response=$(curl -s -w "%{http_code}" "$BACKEND_URL/search/?q=test&limit=5")
search_status="${search_response: -3}"

if [ "$search_status" -eq 200 ]; then
    echo "✅ Search test passed (HTTP $search_status)"
else
    echo "❌ Search test failed (HTTP $search_status)"
fi

# Test chat endpoint with a simple message
echo "Testing Chat endpoint..."
chat_payload='{"message": "Hello, this is a test message", "use_history": false}'
chat_response=$(curl -s -w "%{http_code}" -X POST \
    -H "Content-Type: application/json" \
    -d "$chat_payload" \
    "$BACKEND_URL/chat/")
chat_status="${chat_response: -3}"

if [ "$chat_status" -eq 200 ]; then
    echo "✅ Chat test passed (HTTP $chat_status)"
else
    echo "❌ Chat test failed (HTTP $chat_status)"
    echo "Response: ${chat_response%???}"  # Remove status code from response
fi

echo ""
echo "📊 Service Status Summary:"
docker-compose ps

echo ""
echo "📋 Recent logs (last 20 lines):"
echo "--- Backend logs ---"
docker-compose logs --tail=10 backend

echo ""
echo "--- Frontend logs ---"
docker-compose logs --tail=10 frontend

echo ""
echo "🎯 Test complete!"
echo ""
echo "💡 Tips:"
echo "   - If tests fail, check the logs: docker-compose logs -f"
echo "   - Ensure your .env file has the correct MISTRAL_API_KEY"
echo "   - Try restarting services: docker-compose restart"
echo ""
