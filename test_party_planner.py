#!/usr/bin/env python3
"""
Test Party Planner Feature
Quick interactive test of the party planning flow
"""

import asyncio
import sys
sys.path.append('backend')

from party_planner import PartyPlanner

async def test_party_planner():
    print("🎉 Party Planner Test")
    print("=" * 50)
    print()
    
    planner = PartyPlanner()
    
    # Test 1: Initial Request
    print("TEST 1: Initial party request")
    print("-" * 50)
    user_input = "Zorganizuj imprezę urodzinową na 10 osób pojutrze"
    print(f"User: {user_input}")
    print()
    
    response = await planner.process_request(user_input)
    print(f"Assistant:\n{response}")
    print()
    print(f"State: {planner.state}")
    print("=" * 50)
    print()
    
    # Test 2: Modification
    print("TEST 2: Plan modification")
    print("-" * 50)
    user_input = "Dodaj balony i zmień tort na większy"
    print(f"User: {user_input}")
    print()
    
    response = await planner.process_request(user_input)
    print(f"Assistant:\n{response}")
    print()
    print(f"State: {planner.state}")
    print("=" * 50)
    print()
    
    # Test 3: Confirmation
    print("TEST 3: Plan confirmation")
    print("-" * 50)
    user_input = "Potwierdzam"
    print(f"User: {user_input}")
    print()
    
    response = await planner.process_request(user_input)
    print(f"Assistant:\n{response}")
    print()
    print(f"State: {planner.state}")
    print("=" * 50)
    print()
    
    # Test 4: Information gathering
    print("TEST 4: Providing information")
    print("-" * 50)
    
    # Simulate gathering multiple pieces of info
    info_inputs = [
        "Jan Kowalski",
        "+48 123 456 789",
        "15 grudnia 2024",
        "18:00"
    ]
    
    for info in info_inputs:
        print(f"User: {info}")
        response = await planner.process_request(info)
        print(f"Assistant: {response[:100]}...")
        print()
        
        if planner.state == "complete":
            print("✅ Planning complete!")
            print(f"Gathered info: {planner.gathered_info}")
            break
    
    print()
    print("=" * 50)
    print("Test completed!")

if __name__ == "__main__":
    asyncio.run(test_party_planner())

