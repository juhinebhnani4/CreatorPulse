#!/usr/bin/env python3
"""
Test the newsletter generation API endpoint directly to see the error.
"""

import requests
import json

# API endpoint
url = "http://localhost:8000/api/v1/newsletters/generate"

# Get a workspace ID first
workspaces_url = "http://localhost:8000/api/v1/workspaces"

# Note: You'll need a valid auth token. For testing, we'll try without auth first
headers = {
    "Content-Type": "application/json"
}

# First, let's try to get workspace info (this might fail without auth)
print("Testing newsletter generation endpoint...\n")

# Test data
payload = {
    "workspace_id": "a378d938-c330-4060-82a4-17579dc8bb3f",  # Replace with your workspace ID
    "title": "Test Newsletter",
    "max_items": 5,
    "days_back": 7,
    "tone": "professional",
    "language": "en",
    "temperature": 0.7
}

print(f"Sending POST to: {url}")
print(f"Payload: {json.dumps(payload, indent=2)}\n")

try:
    response = requests.post(url, json=payload, headers=headers)

    print(f"Status Code: {response.status_code}")
    print(f"Status Text: {response.reason}")
    print(f"\nResponse Headers:")
    for key, value in response.headers.items():
        print(f"  {key}: {value}")

    print(f"\nResponse Body:")
    try:
        response_json = response.json()
        print(json.dumps(response_json, indent=2))
    except:
        print(response.text)

except Exception as e:
    print(f"Error making request: {e}")
    import traceback
    traceback.print_exc()
