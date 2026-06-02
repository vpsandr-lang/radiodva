#!/bin/bash
# RADIO DVA — Deploy to Render
# Usage: ./deploy.sh <RENDER_API_TOKEN>

set -e

RENDER_TOKEN="${1:-$RENDER_TOKEN}"
OWNER_ID="tea-d8f49i6rnols73an3bsg"

if [ -z "$RENDER_TOKEN" ]; then
  echo "❌ Usage: ./deploy.sh <RENDER_API_TOKEN>"
  echo "   Or set RENDER_TOKEN environment variable"
  exit 1
fi

echo "🎧 Deploying RADIO DVA to Render..."
echo ""

# Create web service
echo "📡 Creating web service..."
curl -s -X POST "https://api.render.com/v1/services" \
  -H "Authorization: Bearer $RENDER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "web_service",
    "name": "radiodva",
    "ownerId": "'"$OWNER_ID"'",
    "repo": "https://github.com/vpsandr-lang/radiodva",
    "branch": "main",
    "runtime": "docker",
    "autoDeploy": "yes",
    "serviceDetails": {
      "plan": "free",
      "region": "frankfurt",
      "healthCheckPath": "/api/health",
      "dockerfilePath": "Dockerfile",
      "dockerContext": "."
    },
    "envVars": [
      {"key": "PORT", "value": "5050"}
    ]
  }' | python3 -c "
import sys, json
data = json.load(sys.stdin)
if 'id' in data:
    print('✅ Service created!')
    print(f'   Dashboard: https://dashboard.render.com/web/{data[\"id\"]}')
    s = data.get('service', {})
    if s.get('url'):
        print(f'   URL: {s[\"url\"]}')
else:
    print(f'❌ Error: {data.get(\"error\", str(data))}')
    exit(1)
"

echo ""
echo "✅ Deploy initiated! Monitor at: https://dashboard.render.com"
echo "   First deploy takes ~3-5 minutes for Docker build."
