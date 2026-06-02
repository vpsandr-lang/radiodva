#!/usr/bin/env python3
"""RADIO DVA — Entry point for Render deployment.

Starts the API server with built-in AI DJ broadcaster.
"""
import sys
import os

# Ensure we can import modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Start AI DJ broadcaster (background thread)
from api.broadcaster import start_broadcaster
broadcaster = start_broadcaster()
print("🎧 AI DJ Broadcaster started in background", flush=True)

# Start API server (blocking)
from api.server import run_server
run_server()
