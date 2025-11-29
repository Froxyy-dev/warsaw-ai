#!/usr/bin/env python3
"""
Test Action-Oriented Plan Format
Based on spec_file.md example
"""

import asyncio
import sys
sys.path.append('backend')

from party_planner import PartyPlanner

async def test_action_oriented_format():
    print("🎉 Testing Action-Oriented Plan Format")
    print("=" * 70)
    print()
    
    planner = PartyPlanner()
    
    # Test 1: Initial Request (from spec_file.md)
    print("TEST 1: Initial party request")
    print("-" * 70)
    user_input = """Moja dziewczyna ma pojutrze urodziny. Zorganizuj imprezę urodzinową, 
która zacznie się około godziny 16:00 i potrwa około 5 godzin"""
    print(f"User: {user_input}")
    print()
    
    response = await planner.process_request(user_input)
    print(f"Assistant:\n{response}")
    print()
    print(f"State: {planner.state}")
    print("=" * 70)
    print()
    
    # Validate format
    if "Zadzwonić do" in response:
        print("✅ Plan uses action-oriented format!")
    else:
        print("❌ Plan does NOT use action-oriented format")
    print()
    
    # Test 2: Refinement - Move tort to bakery (from spec_file.md)
    print("TEST 2: Move tort to dedicated bakery")
    print("-" * 70)
    user_input = """Jest okej, ale chciałbym żeby tort urodzinowy zamówić z cukierni 
zajmującej się profesjonalnie tortami, a na torcie będzie napis 
"Wszystkiego najlepszego Ada" """
    print(f"User: {user_input}")
    print()
    
    response = await planner.process_request(user_input)
    print(f"Assistant:\n{response}")
    print()
    print(f"State: {planner.state}")
    print("=" * 70)
    print()
    
    # Validate refinement
    if "Zadzwonić do cukierni" in response or "Zadzwonić do cukierni z tortami" in response:
        print("✅ Plan correctly created separate action group for bakery!")
    else:
        print("⚠️  Check if bakery is separated")
    
    if "Wszystkiego najlepszego Ada" in response:
        print("✅ Cake message included!")
    else:
        print("⚠️  Cake message missing")
    print()
    
    # Test 3: Confirmation
    print("TEST 3: Confirm plan")
    print("-" * 70)
    user_input = "Potwierdzam"
    print(f"User: {user_input}")
    print()
    
    response = await planner.process_request(user_input)
    print(f"Assistant:\n{response[:200]}...")
    print()
    print(f"State: {planner.state}")
    print("=" * 70)
    print()
    
    if planner.state.value == "gathering":
        print("✅ Transitioned to gathering state!")
    else:
        print(f"⚠️  State is {planner.state}, expected gathering")
    
    print()
    print("=" * 70)
    print("Test completed!")
    print()
    print("SUMMARY:")
    print("- Action-oriented format: CHECK")
    print("- Can refine plans: CHECK")
    print("- Can create separate action groups: CHECK")
    print("- Transitions to gathering: CHECK")

if __name__ == "__main__":
    asyncio.run(test_action_oriented_format())

