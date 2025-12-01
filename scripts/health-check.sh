#!/bin/bash
URL="${1:-http://localhost:5000/health}"
echo "🏥 Health Check: $URL"
RESPONSE=$(curl -s -w "\n%{http_code}" "$URL")
HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | head -n-1)
[ "$HTTP_CODE" -eq 200 ] && echo "✅ HEALTHY" || echo "❌ UNHEALTHY"
echo "$BODY" | jq . 2>/dev/null || echo "$BODY"
[ "$HTTP_CODE" -eq 200 ] && exit 0 || exit 1
