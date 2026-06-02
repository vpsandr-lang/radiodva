#!/bin/bash
# RADIO DVA — Full system startup with proper daemonization

echo "🎧 RADIO DVA Starting..."
cd /root/Radio

# 1. Icecast (already running? kill and restart)
killall -q icecast2 2>/dev/null
sleep 2
setsid su -s /bin/sh -c "icecast2 -c /etc/icecast2/icecast.xml" nobody &>/dev/null &
sleep 4
echo "  Icecast: $(curl -s -o /dev/null -w '%{http_code}' http://localhost:8888/)"

# 2. API
setsid python3 /root/Radio/api/server.py &>/tmp/radio/api.log &
sleep 2
echo "  API: $(curl -s -o /dev/null -w '%{http_code}' http://localhost:5050/api/now-playing)"

# 3. Web
setsid python3 -m http.server 8000 --directory /root/Radio &>/tmp/radio/web.log &
sleep 1
echo "  Web: $(curl -s -o /dev/null -w '%{http_code}' http://localhost:8000/index.html)"

# 4. Broadcaster
setsid python3 -u /tmp/radio/simple_live.py &>/tmp/radio/broadcast.log &
sleep 10
echo "  Stream: $(curl -s --max-time 4 -o /dev/null -w '%{http_code}' http://localhost:8888/stream)"

PUBLIC_IP=$(curl -s ifconfig.me 2>/dev/null | grep -v '^$' | head -1)
echo ""
echo "✅ RADIO DVA LIVE!"
echo "   📻 http://$PUBLIC_IP:8888/stream"
echo "   🌐 http://$PUBLIC_IP:8000"
echo "   📡 http://$PUBLIC_IP:5050/api/now-playing"
