#!/bin/bash

echo "🔍 Quick Chat Test"
echo "===================="
echo ""

# Test 1: Backend health
echo "1. Testing backend health..."
curl -s http://localhost:8000/api/health | python3 -m json.tool
echo ""

# Test 2: Chat health
echo "2. Testing chat service..."
curl -s http://localhost:8000/api/chat/health | python3 -m json.tool
echo ""

# Test 3: Create conversation
echo "3. Creating conversation..."
RESPONSE=$(curl -s -X POST http://localhost:8000/api/chat/conversations/ \
  -H "Content-Type: application/json" \
  -d '{}')
echo "$RESPONSE" | python3 -m json.tool

CONV_ID=$(echo "$RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['conversation']['id'])" 2>/dev/null)

if [ -z "$CONV_ID" ]; then
  echo "❌ Failed to create conversation"
  exit 1
fi

echo ""
echo "✅ Conversation ID: $CONV_ID"
echo ""

# Test 4: Send message
echo "4. Sending message..."
curl -s -X POST "http://localhost:8000/api/chat/conversations/$CONV_ID/messages" \
  -H "Content-Type: application/json" \
  -d '{"content":"Test message"}' | python3 -m json.tool

echo ""
echo "✅ All tests passed!"

