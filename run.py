#!/usr/bin/env python3
"""RADIO DVA — Entry point.
Starts file broadcaster + API server.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Start file broadcaster (background thread)
from api.file_broadcaster import start_broadcaster
broadcaster = start_broadcaster()

# Start API server (blocking)
from api.server import run_server
run_server()
