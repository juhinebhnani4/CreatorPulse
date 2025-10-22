#!/usr/bin/env python3
"""
Restart the backend server by killing existing processes and starting a new one.
"""

import subprocess
import time
import sys
import os

def kill_processes_on_port(port=8000):
    """Kill all processes listening on the given port."""
    print(f"Looking for processes on port {port}...")

    try:
        # Find PIDs listening on port 8000
        result = subprocess.run(
            ['netstat', '-ano'],
            capture_output=True,
            text=True,
            shell=True
        )

        pids = set()
        for line in result.stdout.split('\n'):
            if f':{port}' in line and 'LISTENING' in line:
                parts = line.split()
                if parts:
                    pid = parts[-1]
                    if pid.isdigit():
                        pids.add(pid)

        if not pids:
            print(f"No processes found on port {port}")
            return True

        print(f"Found {len(pids)} process(es) on port {port}: {pids}")

        # Kill each process
        for pid in pids:
            print(f"Killing process {pid}...")
            try:
                subprocess.run(['taskkill', '/F', '/PID', pid], shell=True, check=False)
            except Exception as e:
                print(f"  Warning: Could not kill {pid}: {e}")

        time.sleep(2)
        print("Processes killed.")
        return True

    except Exception as e:
        print(f"Error killing processes: {e}")
        return False

def start_backend():
    """Start the backend server."""
    print("\nStarting backend server...")

    # Change to script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)

    venv_python = os.path.join(script_dir, '.venv', 'Scripts', 'python.exe')

    if not os.path.exists(venv_python):
        print(f"ERROR: Virtual environment not found at {venv_python}")
        return False

    print(f"Using Python: {venv_python}")
    print(f"Working directory: {os.getcwd()}")
    print("\nStarting uvicorn...")
    print("="*60)

    try:
        # Start uvicorn with reload
        subprocess.Popen(
            [venv_python, '-m', 'uvicorn', 'backend.main:app', '--reload', '--port', '8000'],
            shell=True
        )

        print("\nBackend server started!")
        print("Check for startup messages above.")
        print("The server will auto-reload when you make code changes.")
        print("\nPress Ctrl+C in the server window to stop it.")

        return True

    except Exception as e:
        print(f"ERROR starting backend: {e}")
        return False

if __name__ == "__main__":
    print("="*60)
    print("Backend Server Restart Script")
    print("="*60 + "\n")

    # Kill existing processes
    if not kill_processes_on_port(8000):
        print("\nWARNING: Could not kill all processes. Continue anyway? (y/n)")
        if input().lower() != 'y':
            sys.exit(1)

    # Wait a moment
    time.sleep(1)

    # Start new server
    if start_backend():
        print("\n" + "="*60)
        print("SUCCESS: Backend server restarted")
        print("="*60)
        sys.exit(0)
    else:
        print("\n" + "="*60)
        print("FAILED: Could not start backend server")
        print("="*60)
        sys.exit(1)
