#!/usr/bin/env python3
"""
Test script for venue search feature
Simulates a full party planning flow with venue search and task generation
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000/api/chat"

def print_separator(title=""):
    print("\n" + "=" * 70)
    if title:
        print(f" {title} ".center(70, "="))
        print("=" * 70)
    print()

def send_message(conversation_id, content):
    """Send a message and return the response"""
    print(f"👤 USER: {content}")
    print()
    
    response = requests.post(
        f"{BASE_URL}/conversations/{conversation_id}/messages",
        json={"content": content}
    )
    
    if response.status_code != 200:
        print(f"❌ ERROR: {response.status_code}")
        print(response.text)
        return None
    
    data = response.json()
    assistant_msg = data.get("assistant_message", "")
    
    print(f"🤖 ASSISTANT:\n{assistant_msg}")
    print()
    
    return assistant_msg

def main():
    print_separator("🎉 Party Planning with Venue Search - Full Flow Test")
    
    # Step 1: Create conversation
    print("📝 Step 1: Creating conversation...")
    response = requests.post(f"{BASE_URL}/conversations/", json={})
    
    if response.status_code != 200:
        print(f"❌ Failed to create conversation: {response.status_code}")
        print(response.text)
        return
    
    data = response.json()
    conversation_id = data["conversation"]["id"]
    print(f"✅ Conversation created: {conversation_id}")
    print()
    
    # Step 2: Send party request
    print_separator("Step 2: Sending party request")
    send_message(
        conversation_id,
        "Moja dziewczyna ma pojutrze urodziny. Zorganizuj imprezę urodzinową w Warszawie, "
        "która zacznie się około godziny 16:00 i potrwa około 5 godzin."
    )
    
    time.sleep(2)
    
    # Step 3: Modify plan - add bakery
    print_separator("Step 3: Modifying plan - specialized bakery")
    send_message(
        conversation_id,
        "Chciałbym żeby tort urodzinowy zamówić z cukierni zajmującej się profesjonalnie tortami, "
        "a na torcie będzie napis: Wszystkiego najlepszego Ada."
    )
    
    time.sleep(2)
    
    # Step 4: Modify plan - Polish menu
    print_separator("Step 4: Modifying plan - Polish cuisine")
    send_message(
        conversation_id,
        "Jako menu chciałbym tradycyjną kuchnię polską"
    )
    
    time.sleep(2)
    
    # Step 5: Confirm plan
    print_separator("Step 5: Confirming plan")
    send_message(
        conversation_id,
        "Zatwierdzam"
    )
    
    time.sleep(2)
    
    # Step 6: Provide contact info - name
    print_separator("Step 6: Providing contact info - Name")
    send_message(
        conversation_id,
        "Mateusz Winiarek"
    )
    
    time.sleep(1)
    
    # Step 7: Provide contact info - phone
    print_separator("Step 7: Providing contact info - Phone")
    send_message(
        conversation_id,
        "886859039"
    )
    
    time.sleep(1)
    
    # Step 8: Confirm date
    print_separator("Step 8: Confirming date")
    send_message(
        conversation_id,
        "tak"
    )
    
    # Wait for venue search and task generation
    print_separator("⏳ Waiting for venue search and task generation...")
    time.sleep(5)
    
    print_separator("✅ TEST COMPLETE")
    print("Check the backend console for:")
    print("  - Venue search results")
    print("  - Bakery search results")
    print("  - Generated task list with formatted output")
    print("  - Saved tasks in database/tasks/")
    print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Test interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

