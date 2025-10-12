#!/bin/bash
# Debug script to test all iteration 3 endpoints

echo "🔍 Testing Iteration 3 Endpoints"
echo "================================"

BASE_URL="http://localhost:8000/api/v1"

echo ""
echo "1. Health Check (should be at root /api/v1/):"
curl -s "$BASE_URL/" | jq . || echo "FAILED"

echo ""
echo "2. Plant Tracking - Start (POST):"
echo "Testing if endpoint exists..."
curl -s -X POST "$BASE_URL/tracking/start" \
  -H "Content-Type: application/json" \
  -d '{"user_data":{"email":"test@example.com"},"plant_id":1,"plant_nickname":"test","start_date":"2025-01-01"}' \
  | jq . 2>/dev/null || echo "Endpoint exists but may have validation errors"

echo ""
echo "3. Plant Tracking - Get user plants (GET):"
curl -s "$BASE_URL/tracking/user/test@example.com" | jq . 2>/dev/null || echo "FAILED"

echo ""
echo "4. Plant Tracking - Get instance details (GET):"
curl -s "$BASE_URL/tracking/instance/1" | jq . 2>/dev/null || echo "FAILED (expected, no instance)"

echo ""
echo "5. Chat - Start general chat (POST):"
curl -s -X POST "$BASE_URL/chat/general/start" \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com"}' \
  | jq . 2>/dev/null || echo "FAILED"

echo ""
echo "6. Guides - Categories (GET):"
curl -s "$BASE_URL/guides/categories" | jq . || echo "FAILED"

echo ""
echo "7. Favorites - Get favorites (GET):"
curl -s "$BASE_URL/favorites?email=test@example.com" | jq . 2>/dev/null || echo "FAILED"

echo ""
echo "================================"
echo "✅ Endpoint discovery complete"
echo ""
echo "📋 Expected endpoints:"
echo "  - /api/v1/tracking/start"
echo "  - /api/v1/tracking/user/{email}"
echo "  - /api/v1/chat/general/start"
echo "  - /api/v1/guides/categories"
echo "  - /api/v1/favorites"
