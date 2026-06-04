#!/usr/bin/env python3
"""RADIO DVA — Entry point with watchdog memory monitoring."""
import sys, os, time, threading
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from api.file_broadcaster import start_broadcaster
from api.server import run_server

# Start broadcaster in background
broadcaster = start_broadcaster()

# Memory watchdog thread
def memory_watchdog():
    """Monitor memory usage and restart if too high."""
    while True:
        time.sleep(60)
        try:
            with open('/proc/self/status') as f:
                for line in f:
                    if line.startswith('VmRSS:'):
                        mem_mb = int(line.split()[1]) // 1024
                        if mem_mb > 700:
                            print(f"⚠️ Memory critical: {mem_mb}MB, restarting...", flush=True)
                            os._exit(1)
                        break
        except:
            pass

t = threading.Thread(target=memory_watchdog, daemon=True)
t.start()

# Start HTTP server (blocking)
run_server()
