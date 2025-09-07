#!/usr/bin/env python3

# Test State Persistence Script
# This script tests if conversation state persists across multiple turns using the sonic agent

import asyncio
import sys
import os
import json
import requests
import time
sys.path.append('/app')

# Colors for output
RED = '\033[0;31m'
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
PURPLE = '\033[0;35m'
CYAN = '\033[0;36m'
NC = '\033[0m'  # No Color

def print_status(message):
    print(f"{BLUE}[INFO]{NC} {message}")

def print_success(message):
    print(f"{GREEN}[SUCCESS]{NC} {message}")

def print_warning(message):
    print(f"{YELLOW}[WARNING]{NC} {message}")

def print_error(message):
    print(f"{RED}[ERROR]{NC} {message}")

def print_agent(message):
    print(f"{PURPLE}[AGENT]{NC} {message}")

def print_user(message):
    print(f"{CYAN}[USER]{NC} {message}")

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

async def test_backend_health():
    """Test if the backend is running and healthy"""
    print_status("Testing backend health...")
    
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print_success("Backend is healthy and running")
            return True
        else:
            print_error(f"Backend health check failed with status: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Backend health check failed: {e}")
        return False

async def invoke_sonic_agent(message: str, thread_id: str = "test_persistence_thread"):
    """Invoke the sonic agent with a message"""
    url = "http://localhost:8000/agent/invoke"
    
    payload = {
        "agent_name": "sonic",
        "thread_id": thread_id,
        "agent_input": {
            "messages": [
                {
                    "type": "human",
                    "content": message
                }
            ]
        }
    }
    
    try:
        print_user(f"Sending message: '{message}'")
        response = requests.post(url, json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            ai_response = result.get("AI_Response", "")
            print_agent(f"Response: {ai_response}")
            return ai_response
        else:
            print_error(f"Agent invocation failed with status: {response.status_code}")
            print_error(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print_error(f"Agent invocation failed: {e}")
        return None

async def test_state_persistence():
    """Test if conversation state persists across multiple turns"""
    print_status("Testing state persistence across conversation turns...")
    
    thread_id = "test_persistence_thread_" + str(int(time.time()))
    print_status(f"Using thread ID: {thread_id}")
    
    # Test 1: Introduce yourself
    print("\n" + "="*60)
    print_status("Test 1: Introducing name to the agent")
    print("="*60)
    
    response1 = await invoke_sonic_agent(
        "Hello! My name is Omar and I'm testing state persistence. Please remember my name.",
        thread_id
    )
    
    if not response1:
        print_error("Failed to get response from agent in Test 1")
        return False
    
    # Wait a moment
    await asyncio.sleep(2)
    
    # Test 2: Ask if agent remembers the name
    print("\n" + "="*60)
    print_status("Test 2: Asking agent to recall the name")
    print("="*60)
    
    response2 = await invoke_sonic_agent(
        "What is my name? Do you remember what I told you earlier?",
        thread_id
    )
    
    if not response2:
        print_error("Failed to get response from agent in Test 2")
        return False
    
    # Check if the agent remembered the name
    name_remembered = "omar" in response2.lower()
    
    if name_remembered:
        print_success("✅ Agent remembered the name! State persistence is working.")
    else:
        print_warning("⚠️ Agent did not remember the name. Checking response...")
        print_warning(f"Response content: {response2}")
    
    # Test 3: Continue conversation to further test persistence
    print("\n" + "="*60)
    print_status("Test 3: Continuing conversation with context")
    print("="*60)
    
    response3 = await invoke_sonic_agent(
        "Can you tell me a fun fact about my name or ask me something about myself?",
        thread_id
    )
    
    if not response3:
        print_error("Failed to get response from agent in Test 3")
        return False
    
    # Test 4: Test with different thread ID (should NOT remember)
    print("\n" + "="*60)
    print_status("Test 4: Testing with different thread ID (should NOT remember)")
    print("="*60)
    
    different_thread_id = "different_thread_" + str(int(time.time()))
    print_status(f"Using different thread ID: {different_thread_id}")
    
    response4 = await invoke_sonic_agent(
        "What is my name?",
        different_thread_id
    )
    
    if not response4:
        print_error("Failed to get response from agent in Test 4")
        return False
    
    name_in_different_thread = "omar" in response4.lower()
    
    if not name_in_different_thread:
        print_success("✅ Agent correctly doesn't remember name in different thread!")
    else:
        print_warning("⚠️ Agent incorrectly remembered name across different threads")
        print_warning("This might indicate thread isolation issues")
    
    return name_remembered and not name_in_different_thread

async def test_checkpoint_collections():
    """Test that checkpoint collections are being used"""
    print_status("Testing checkpoint collections...")
    
    try:
        from pymongo import MongoClient
        
        mongo_uri = os.getenv('MONGODB_URI', 'mongodb://mongo:27017')
        db_name = os.getenv('MONGODB_DB_NAME', 'seq_sonic')
        
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
        db = client[db_name]
        
        # Check checkpoint collections
        collections = db.list_collection_names()
        checkpoint_collections = [col for col in collections if 'checkpoint' in col.lower()]
        
        if checkpoint_collections:
            print_success(f"✅ Checkpoint collections found: {checkpoint_collections}")
            
            # Count documents in checkpoint collections
            for col_name in checkpoint_collections:
                count = db[col_name].count_documents({})
                print_status(f"Collection '{col_name}' has {count} documents")
        else:
            print_warning("⚠️ No checkpoint collections found")
            
        client.close()
        return len(checkpoint_collections) > 0
        
    except Exception as e:
        print_error(f"Failed to check checkpoint collections: {e}")
        return False

async def main():
    """Main execution function"""
    print("🧠 Testing State Persistence in SEQ_SONIC")
    print("=" * 60)
    print()

    print_status("Starting state persistence tests...")
    print()

    # Check if running in Docker
    if not await check_docker_env():
        print()
        print_warning("To test in Docker environment, run:")
        print("  docker-compose exec backend python3 /app/test-state-persistence.py")
        return False

    print()

    # Test backend health
    if not await test_backend_health():
        print()
        print_error("Backend is not healthy. Make sure the backend service is running.")
        print_error("Try: docker-compose up -d backend")
        return False

    print()

    # Test checkpoint collections
    checkpoint_test = await test_checkpoint_collections()
    print()

    # Test state persistence
    persistence_test = await test_state_persistence()
    
    print()
    print("=" * 60)
    print_status("TEST SUMMARY")
    print("=" * 60)
    
    if checkpoint_test:
        print_success("✅ Checkpoint collections are present")
    else:
        print_error("❌ Checkpoint collections test failed")
    
    if persistence_test:
        print_success("✅ State persistence is working correctly")
        print_success("✅ Thread isolation is working correctly")
    else:
        print_error("❌ State persistence test failed")
    
    overall_success = checkpoint_test and persistence_test
    
    if overall_success:
        print()
        print_success("🎉 All state persistence tests passed!")
        print_success("Your SEQ_SONIC agents can maintain conversation context!")
    else:
        print()
        print_error("❌ Some tests failed. Check the logs above for details.")
    
    return overall_success

if __name__ == "__main__":
    # Run the async main function
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
