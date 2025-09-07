#!/usr/bin/env python3

# Test Async MongoDB Connection Script
# This script tests the AsyncMongoDB connection when running in Docker containers

import asyncio
import sys
import os
sys.path.append('/app')

from pymongo import AsyncMongoClient, MongoClient
from langgraph.checkpoint.mongodb import MongoDBSaver

# Colors for output
RED = '\033[0;31m'
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
NC = '\033[0m'  # No Color

def print_status(message):
    print(f"{BLUE}[INFO]{NC} {message}")

def print_success(message):
    print(f"{GREEN}[SUCCESS]{NC} {message}")

def print_warning(message):
    print(f"{YELLOW}[WARNING]{NC} {message}")

def print_error(message):
    print(f"{RED}[ERROR]{NC} {message}")

async def check_docker_env():
    """Check if we're running in Docker environment"""
    print_status("Checking if running in Docker environment...")

    if os.path.exists("/.dockerenv"):
        print_success("Running inside Docker container")
        return True
    else:
        print_warning("Not running inside Docker container")
        print_warning("This script is designed for Docker container testing")
        return False

async def test_async_mongo_connection():
    """Test basic AsyncMongoDB connection"""
    print_status("Testing AsyncMongoDB connection...")

    try:
        # Use environment variables or default to docker mongo
        mongo_uri = os.getenv('MONGODB_URI', 'mongodb://mongo:27017')
        db_name = os.getenv('MONGODB_DB_NAME', 'seq_sonic')

        print(f'Connecting to MongoDB: {mongo_uri}')
        print(f'Database: {db_name}')

        client = AsyncMongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
        db = client[db_name]

        # Test the connection with ping
        await client.admin.command('ping')
        print('✅ AsyncMongoDB ping successful')

        # List databases
        dbs = await client.list_database_names()
        print(f'Available databases: {dbs}')

        # Check if our database exists
        if db_name in dbs:
            print(f'✅ Database {db_name} exists')

            # List collections
            collections = await db.list_collection_names()
            print(f'Collections in {db_name}: {collections}')

            # Check checkpoint collections
            checkpoint_collections = [col for col in collections if 'checkpoint' in col]
            if checkpoint_collections:
                print(f'✅ Checkpoint collections found: {checkpoint_collections}')
            else:
                print('⚠️ No checkpoint collections found yet')

        else:
            print(f'⚠️ Database {db_name} does not exist yet (will be created on first use)')

        await client.close()
        print('✅ AsyncMongoDB connection test completed successfully')
        return True

    except Exception as e:
        print(f'❌ AsyncMongoDB connection failed: {e}')
        return False

async def test_async_langgraph_checkpoint():
    """Test Async LangGraph checkpoint functionality"""
    print_status("Testing Async LangGraph checkpoint functionality...")

    try:
        # Use environment variables or default to docker mongo
        mongo_uri = os.getenv('MONGODB_URI', 'mongodb://mongo:27017')
        db_name = os.getenv('MONGODB_DB_NAME', 'seq_sonic')

        print(f'Testing Async LangGraph MongoDBSaver with: {mongo_uri}')

        # MongoDBSaver works with both sync and async clients
        # But for async operations, we need to use a sync client
        sync_client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)

        # Test creating a checkpoint saver with sync client for async operations
        checkpointer = MongoDBSaver(sync_client, db_name=db_name)
        print('✅ MongoDBSaver created successfully with MongoClient')

        # Test basic checkpoint operations using async methods
        config = {'configurable': {'thread_id': 'test_thread', 'checkpoint_ns': 'test_namespace'}}

        # Try to get state using async method (should return empty if no state exists)
        state = await checkpointer.aget(config)
        print(f'✅ Checkpoint aget operation successful (state: {state})')

        # Test async list operation
        checkpoints = [cp async for cp in checkpointer.alist(config, limit=1)]
        print(f'✅ Checkpoint alist operation successful (found {len(checkpoints)} checkpoints)')

        sync_client.close()
        print('✅ Async LangGraph checkpoint test completed successfully')
        return True

    except Exception as e:
        print(f'❌ Async LangGraph checkpoint test failed: {e}')
        return False

async def main():
    """Main execution function"""
    print("🔍 Testing Async MongoDB Connection in Docker Environment")
    print("=" * 60)
    print()

    print_status("Starting AsyncMongoDB connection tests...")
    print()

    # Check if running in Docker
    if not await check_docker_env():
        print()
        print_warning("To test in Docker environment, run:")
        print("  docker-compose exec backend python3 /app/test-async-mongo-connection.py")
        print("  OR")
        print("  docker-compose exec backend bash -c 'cd /app && python3 test-async-mongo-connection.py'")
        return False

    print()

    # Test basic AsyncMongoDB connection
    if await test_async_mongo_connection():
        print()
        # Test Async LangGraph checkpoint
        if await test_async_langgraph_checkpoint():
            print()
            print_success("🎉 All AsyncMongoDB tests passed!")
            print_success("Async state persistence should work correctly in Docker environment")
            print()
            print_status("Environment variables:")
            for key, value in os.environ.items():
                if 'MONGO' in key.upper():
                    print(f"  {key}={value}")
            if not any('MONGO' in key.upper() for key in os.environ.keys()):
                print("  No MongoDB env vars found")
            return True
        else:
            print()
            print_error("Async LangGraph checkpoint test failed")
            return False
    else:
        print()
        print_error("AsyncMongoDB connection test failed")
        print_error("Check your MongoDB configuration and Docker network setup")
        return False

if __name__ == "__main__":
    # Run the async main function
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
