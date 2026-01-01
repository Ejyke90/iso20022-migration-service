#!/bin/bash

# Quick test script to verify CORS configuration

BACKEND_URL="${1:-https://doc-to-pdf-convertor-production.up.railway.app}"
FRONTEND_URL="${2:-https://word-to-pdf-agent.vercel.app}"

echo "🧪 Testing CORS Configuration"
echo "=============================="
echo "Backend:  $BACKEND_URL"
echo "Frontend: $FRONTEND_URL"
echo ""

# Test 1: Health Check
echo "Test 1: Health Check"
echo "--------------------"
HEALTH_RESPONSE=$(curl -s "$BACKEND_URL/api/health")
if echo "$HEALTH_RESPONSE" | grep -q "healthy"; then
    echo "✅ Backend is healthy"
    echo "   Response: $HEALTH_RESPONSE"
else
    echo "❌ Backend health check failed"
    echo "   Response: $HEALTH_RESPONSE"
    exit 1
fi

echo ""

# Test 2: CORS Preflight
echo "Test 2: CORS Preflight (OPTIONS request)"
echo "-----------------------------------------"
CORS_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" \
    -X OPTIONS "$BACKEND_URL/api/convert" \
    -H "Origin: $FRONTEND_URL" \
    -H "Access-Control-Request-Method: POST" \
    -H "Access-Control-Request-Headers: Content-Type")

if [ "$CORS_RESPONSE" = "204" ] || [ "$CORS_RESPONSE" = "200" ]; then
    echo "✅ CORS preflight successful (HTTP $CORS_RESPONSE)"
else
    echo "❌ CORS preflight failed (HTTP $CORS_RESPONSE)"
fi

echo ""

# Test 3: CORS Headers
echo "Test 3: Checking CORS Headers"
echo "------------------------------"
curl -s -I -X OPTIONS "$BACKEND_URL/api/convert" \
    -H "Origin: $FRONTEND_URL" \
    -H "Access-Control-Request-Method: POST" | grep -i "access-control"

echo ""

# Test 4: Health endpoint with CORS
echo "Test 4: Health Endpoint CORS Headers"
echo "-------------------------------------"
curl -s -I "$BACKEND_URL/api/health" \
    -H "Origin: $FRONTEND_URL" | grep -i "access-control"

echo ""
echo "✅ Testing complete!"
echo ""
echo "If you see 'Access-Control-Allow-Origin' headers above, CORS is working!"
echo "If not, you may need to redeploy the backend to Railway."
