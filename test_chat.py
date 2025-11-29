#!/usr/bin/env python3
"""Quick test script to verify chat endpoints"""

import requests
import json

BASE_URL = "http://localhost:8000/api/chat"

def test_chat():
    print("🧪 Testing Chat API\n")
    
    # Test 1: Create conversation
    print("1️⃣ Creating conversation...")
    try:
        response = requests.post(f"{BASE_URL}/conversations/", json={})
        print(f"Status code: {response.status_code}")
        response.raise_for_status()
        data = response.json()
        conv_id = data['conversation']['id']
        print(f"✅ Created conversation: {conv_id}\n")
    except Exception as e:
        print(f"❌ Failed to create conversation: {e}")
        if 'response' in locals():
            print(f"Response status: {response.status_code}")
            print(f"Response body: {response.text}")
        return
    
    # Test 2: Send message
    print("2️⃣ Sending message...")
    try:
        response = requests.post(
            f"{BASE_URL}/conversations/{conv_id}/messages",
            json={"content": "Cześć, jak się masz?"}
        )
        response.raise_for_status()
        assistant_msg = response.json()
        print(f"✅ Got response: {assistant_msg['content'][:100]}...\n")
    except Exception as e:
        print(f"❌ Failed to send message: {e}")
        print(f"Response: {response.text if 'response' in locals() else 'No response'}")
        return
    
    # Test 3: Get conversation
    print("3️⃣ Getting conversation...")
    try:
        response = requests.get(f"{BASE_URL}/conversations/{conv_id}")
        response.raise_for_status()
        conv = response.json()
        print(f"✅ Conversation has {len(conv['messages'])} messages")
        for i, msg in enumerate(conv['messages'], 1):
            print(f"   {i}. [{msg['role']}]: {msg['content'][:50]}...")
    except Exception as e:
        print(f"❌ Failed to get conversation: {e}")
        return
    
    print("\n✅ All tests passed!")

if __name__ == "__main__":
    test_chat()

