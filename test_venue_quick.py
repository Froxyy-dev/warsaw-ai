#!/usr/bin/env python3
"""Quick test for venue search with fixed parser"""
import requests
import time

BASE_URL = "http://localhost:8000/api/chat"

def send_msg(conv_id, msg):
    print(f"👤 {msg[:80]}...")
    r = requests.post(f"{BASE_URL}/conversations/{conv_id}/messages", json={"content": msg})
    resp = r.json().get("assistant_message", "")
    print(f"🤖 {resp[:150]}...")
    print()
    return resp

# Create conversation
print("Creating conversation...")
r = requests.post(f"{BASE_URL}/conversations/", json={})
conv_id = r.json()["conversation"]["id"]
print(f"✅ ID: {conv_id}\n")

# Party request
send_msg(conv_id, "Moja dziewczyna ma pojutrze urodziny. Zorganizuj imprezę urodzinową na 10 osób w Warszawie, która zacznie się około godziny 16:00 i potrwa około 5 godzin.")
time.sleep(1)

# Modify - bakery
send_msg(conv_id, "Chciałbym żeby tort urodzinowy zamówić z cukierni zajmującej się profesjonalnie tortami, a na torcie będzie napis: Wszystkiego najlepszego Ada.")
time.sleep(1)

# Modify - menu
send_msg(conv_id, "Chciałbym żeby była tradycyjna kuchnia polska.")
time.sleep(1)

# Confirm
send_msg(conv_id, "Potwierdzam")
time.sleep(1)

# Name
send_msg(conv_id, "Mateusz Winiarek")
time.sleep(1)

# Phone
resp = send_msg(conv_id, "886859039")

# Wait for search
print("⏳ Waiting for venue search (15s)...")
time.sleep(15)

# Check response
if "Nie znalazłem" in resp:
    print("❌ STILL FAILING - Check backend logs")
elif "Znalazłem" in resp or "🏢" in resp or "🍰" in resp:
    print("✅ SUCCESS - Venues found!")
else:
    print("⚠️  Check response above")

print("\n📋 Check backend console for task list!")

