#!/usr/bin/env python3

# Debug Checkpoint Script
# This script examines what's actually stored in the checkpoint collections

import asyncio
import sys
import os
import json
sys.path.append('/app')

from pymongo import MongoClient
from bson import ObjectId
import datetime

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

def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, (datetime.datetime, ObjectId)):
        return str(obj)
    raise TypeError(f"Type {type(obj)} not serializable")

async def debug_checkpoint_collections():
    """Debug what's stored in checkpoint collections"""
    print_status("Debugging checkpoint collections...")
    
    try:
        mongo_uri = os.getenv('MONGODB_URI', 'mongodb://mongo:27017')
        db_name = os.getenv('MONGODB_DB_NAME', 'seq_sonic')
        
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
        db = client[db_name]
        
        # Check all checkpoint collections
        collections = db.list_collection_names()
        checkpoint_collections = [col for col in collections if 'checkpoint' in col.lower()]
        
        for col_name in checkpoint_collections:
            print("\n" + "="*60)
            print_status(f"Collection: {col_name}")
            print("="*60)
            
            collection = db[col_name]
            count = collection.count_documents({})
            print_status(f"Total documents: {count}")
            
            if count > 0:
                # Get recent documents
                recent_docs = list(collection.find().sort("_id", -1).limit(5))
                
                for i, doc in enumerate(recent_docs):
                    print(f"\n--- Document {i+1} ---")
                    
                    # Print key fields
                    for key, value in doc.items():
                        if key == '_id':
                            print(f"{key}: {value}")
                        elif key in ['thread_id', 'checkpoint_ns', 'checkpoint_id']:
                            print(f"{key}: {value}")
                        elif key == 'checkpoint' and isinstance(value, dict):
                            print(f"{key}: (checkpoint data)")
                            if 'channel_values' in value:
                                channel_values = value['channel_values']
                                if 'messages' in channel_values:
                                    messages = channel_values['messages']
                                    print(f"  Messages count: {len(messages) if isinstance(messages, list) else 'N/A'}")
                                    if isinstance(messages, list) and messages:
                                        for j, msg in enumerate(messages[-3:]):  # Show last 3 messages
                                            if isinstance(msg, dict):
                                                msg_type = msg.get('type', 'unknown')
                                                content = msg.get('content', '')[:100] + '...' if len(msg.get('content', '')) > 100 else msg.get('content', '')
                                                print(f"    Message {j+1} ({msg_type}): {content}")
                        elif key == 'metadata':
                            print(f"{key}: {json.dumps(value, indent=2, default=json_serial)}")
                        else:
                            # Truncate long values
                            str_value = str(value)
                            if len(str_value) > 200:
                                str_value = str_value[:200] + "..."
                            print(f"{key}: {str_value}")
            else:
                print_warning("No documents found in this collection")
        
        client.close()
        return True
        
    except Exception as e:
        print_error(f"Failed to debug checkpoint collections: {e}")
        return False

async def test_checkpointer_directly():
    """Test the checkpointer directly to see if it's working"""
    print_status("Testing checkpointer directly...")
    
    try:
        from pymongo import MongoClient
        from langgraph.checkpoint.mongodb import MongoDBSaver
        
        mongo_uri = os.getenv('MONGODB_URI', 'mongodb://mongo:27017')
        db_name = os.getenv('MONGODB_DB_NAME', 'seq_sonic')
        
        client = MongoClient(mongo_uri)
        checkpointer = MongoDBSaver(client, db_name=db_name)
        
        # Test config
        config = {'configurable': {'thread_id': 'debug_thread_123', 'checkpoint_ns': 'shared_conversation'}}
        
        # Try to get state
        state = await checkpointer.aget(config)
        print_status(f"Retrieved state: {state}")
        
        # List checkpoints
        checkpoints = [cp async for cp in checkpointer.alist(config, limit=3)]
        print_status(f"Found {len(checkpoints)} checkpoints for thread")
        
        for i, cp in enumerate(checkpoints):
            print(f"  Checkpoint {i+1}: {cp}")
        
        client.close()
        return True
        
    except Exception as e:
        print_error(f"Direct checkpointer test failed: {e}")
        return False

async def main():
    """Main execution function"""
    print("🔍 Debugging Checkpoint Collections")
    print("=" * 60)
    print()

    await debug_checkpoint_collections()
    print()
    await test_checkpointer_directly()

if __name__ == "__main__":
    asyncio.run(main())
