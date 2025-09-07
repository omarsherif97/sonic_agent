#!/bin/bash

# Test MongoDB Connection Script
# This script tests the MongoDB connection when running in Docker containers

set -e  # Exit on any error

echo "🔍 Testing MongoDB Connection in Docker Environment"
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

# Check if we're in Docker environment
check_docker_env() {
    print_status "Checking if running in Docker environment..."

    if [ -f "/.dockerenv" ]; then
        print_success "Running inside Docker container"
        return 0
    else
        print_warning "Not running inside Docker container"
        print_warning "This script is designed for Docker container testing"
        return 1
    fi
}

# Test basic MongoDB connection
test_mongo_connection() {
    print_status "Testing MongoDB connection..."

    # Try to connect to MongoDB
    if python3 -c "
import sys
sys.path.append('/app')
from pymongo import MongoClient
import os

try:
    # Use environment variables or default to docker mongo
    mongo_uri = os.getenv('MONGODB_URI', 'mongodb://mongo:27017')
    db_name = os.getenv('MONGODB_DB_NAME', 'seq_sonic')

    print(f'Connecting to MongoDB: {mongo_uri}')
    print(f'Database: {db_name}')

    client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
    db = client[db_name]

    # Test the connection
    client.admin.command('ping')
    print('✅ MongoDB ping successful')

    # List databases
    dbs = client.list_database_names()
    print(f'Available databases: {dbs}')

    # Check if our database exists
    if db_name in dbs:
        print(f'✅ Database {db_name} exists')

        # List collections
        collections = db.list_collection_names()
        print(f'Collections in {db_name}: {collections}')

        # Check checkpoint collections
        checkpoint_collections = [col for col in collections if 'checkpoint' in col]
        if checkpoint_collections:
            print(f'✅ Checkpoint collections found: {checkpoint_collections}')
        else:
            print('⚠️ No checkpoint collections found yet')

    else:
        print(f'⚠️ Database {db_name} does not exist yet (will be created on first use)')

    client.close()
    print('✅ MongoDB connection test completed successfully')

except Exception as e:
    print(f'❌ MongoDB connection failed: {e}')
    sys.exit(1)
"; then
        print_success "MongoDB connection test passed"
        return 0
    else
        print_error "MongoDB connection test failed"
        return 1
    fi
}

# Test LangGraph checkpoint functionality
test_langgraph_checkpoint() {
    print_status "Testing LangGraph checkpoint functionality..."

    if python3 -c "
import sys
sys.path.append('/app')
from langgraph.checkpoint.mongodb import MongoDBSaver
from pymongo import MongoClient
import os

try:
    # Use environment variables or default to docker mongo
    mongo_uri = os.getenv('MONGODB_URI', 'mongodb://mongo:27017')
    db_name = os.getenv('MONGODB_DB_NAME', 'seq_sonic')

    print(f'Testing LangGraph MongoDBSaver with: {mongo_uri}')

    client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)

    # Test creating a checkpoint saver
    checkpointer = MongoDBSaver(client, db_name=db_name)
    print('✅ MongoDBSaver created successfully')

    # Test basic checkpoint operations
    config = {'configurable': {'thread_id': 'test_thread', 'checkpoint_ns': 'test_namespace'}}

    # Try to get state (should return empty if no state exists)
    state = checkpointer.get(config)
    print(f'✅ Checkpoint get operation successful (state: {state})')

    client.close()
    print('✅ LangGraph checkpoint test completed successfully')

except Exception as e:
    print(f'❌ LangGraph checkpoint test failed: {e}')
    sys.exit(1)
"; then
        print_success "LangGraph checkpoint test passed"
        return 0
    else
        print_error "LangGraph checkpoint test failed"
        return 1
    fi
}

# Main execution
main() {
    echo ""
    print_status "Starting MongoDB connection tests..."
    echo ""

    # Check if running in Docker
    if ! check_docker_env; then
        echo ""
        print_warning "To test in Docker environment, run:"
        echo "  docker-compose exec backend bash /app/test-mongo-connection.sh"
        echo "  OR"
        echo "  docker-compose exec backend /app/test-mongo-connection.sh"
        exit 1
    fi

    echo ""

    # Test basic MongoDB connection
    if test_mongo_connection; then
        echo ""
        # Test LangGraph checkpoint
        if test_langgraph_checkpoint; then
            echo ""
            print_success "🎉 All MongoDB tests passed!"
            print_success "State persistence should work correctly in Docker environment"
            echo ""
            print_status "Environment variables:"
            env | grep -E "(MONGO|MONGODB)" || echo "No MongoDB env vars found"
        else
            echo ""
            print_error "LangGraph checkpoint test failed"
            exit 1
        fi
    else
        echo ""
        print_error "MongoDB connection test failed"
        print_error "Check your MongoDB configuration and Docker network setup"
        exit 1
    fi
}

# Run main function
main "$@"
