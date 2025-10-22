#!/usr/bin/env python3
"""Kill ALL backend server processes."""

import subprocess
import time

print("Killing ALL Python processes on port 8000...")

# Find all PIDs on port 8000
result = subprocess.run(['netstat', '-ano'], capture_output=True, text=True, shell=True)

pids = set()
for line in result.stdout.split('\n'):
    if ':8000' in line and 'LISTENING' in line:
        parts = line.split()
        if parts:
            pid = parts[-1]
            if pid.isdigit():
                pids.add(pid)

print(f"Found {len(pids)} processes: {pids}")

for pid in pids:
    print(f"Killing PID {pid}...")
    subprocess.run(['taskkill', '/F', '/PID', pid], shell=True)

time.sleep(2)
print("\nAll processes killed!")
print("\nNow please run:")
print(".venv\\Scripts\\python.exe -m uvicorn backend.main:app --reload --port 8000")
