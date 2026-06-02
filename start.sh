#!/bin/bash
# RADIO DVA — Start all services

cd /root/Radio

echo "🎧 RADIO DVA Starting..."
echo "========================="

# 1. Generate initial playlist if needed
if [ ! -f /tmp/radio/current_broadcast.mp3 ]; then
    echo "📀 Generating initial audio..."
    mkdir -p /tmp/radio
fi

# 2. Start API server (with built-in AI DJ broadcaster)
echo "🚀 Starting API server on :5050..."
setsid python3 -u api/server.py &>/tmp/radio/api.log &
API_PID=$!
sleep 3

# 3. Start web server for static files
echo "🌐 Starting web server on :8000..."
setsid python3 -m http.server 8000 --directory /root/Radio &>/tmp/radio/web.log &
WEB_PID=$!
sleep 1

echo ""
echo "✅ RADIO DVA LIVE!"
echo "   📡 API:      http://localhost:5050"
echo "   🎵 Stream:   http://localhost:5050/api/stream"
echo "   🌐 Website:  http://localhost:8000"
echo "   📊 Status:   http://localhost:5050/api/health"
echo ""

# Wait
wait $API_PID
