"""
Test script for Scheduler API endpoints.

Prerequisites:
1. Backend running on http://localhost:8000
2. Database migration executed in Supabase (005_create_scheduler_tables.sql)

Usage:
    python test_scheduler_api.py
"""

import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://127.0.0.1:8000/api/v1"
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5M2UwMGZiMC03MjRkLTRkZDQtYmQ3NC0zYWEwYjZlZDk0ZDkiLCJleHAiOjE3NjA1OTMwNjR9.0gDHV65m1DtDDZHmvCaGfzCLen5MdmCGBml9yo2B1nc"
WORKSPACE_ID = "bf404df2-3c2d-4284-aa32-de19fd308fbd"

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {TOKEN}"
}

def print_section(title):
    """Print section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def print_test(name, passed, details=""):
    """Print test result."""
    status = "[PASS]" if passed else "[FAIL]"
    print(f"\n{status}: {name}")
    if details:
        print(f"  {details}")

def test_create_job():
    """Test POST /api/v1/scheduler - Create a scheduled job."""
    print_section("Test 1: Create Scheduled Job")

    # Use timestamp for unique job name
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    payload = {
        "workspace_id": WORKSPACE_ID,
        "name": f"Test Daily Newsletter {timestamp}",
        "description": "Automated daily newsletter generation",
        "schedule_type": "daily",
        "schedule_time": "09:00",
        "timezone": "America/New_York",
        "actions": ["scrape", "generate", "send"],
        "config": {
            "max_items": 10,
            "days_back": 1,
            "sources": ["reddit"],
            "test_mode": True
        },
        "is_enabled": True
    }

    print(f"\nRequest: POST {BASE_URL}/scheduler")
    print(f"Payload: {json.dumps(payload, indent=2)}")

    try:
        response = requests.post(
            f"{BASE_URL}/scheduler",
            headers=headers,
            json=payload
        )

        print(f"\nStatus Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")

        if response.status_code == 201:
            data = response.json()
            if data.get("success") and "id" in data.get("data", {}):
                job_id = data["data"]["id"]
                print_test("Create Job", True, f"Job ID: {job_id}")
                return job_id
            else:
                print_test("Create Job", False, "Success but missing job ID")
                return None
        else:
            print_test("Create Job", False, f"Expected 201, got {response.status_code}")
            return None

    except Exception as e:
        print_test("Create Job", False, str(e))
        return None

def test_list_jobs(workspace_id):
    """Test GET /api/v1/scheduler/workspaces/{workspace_id} - List jobs."""
    print_section("Test 2: List Scheduled Jobs")

    print(f"\nRequest: GET {BASE_URL}/scheduler/workspaces/{workspace_id}")

    try:
        response = requests.get(
            f"{BASE_URL}/scheduler/workspaces/{workspace_id}",
            headers=headers
        )

        print(f"\nStatus Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")

        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                job_count = data["data"].get("count", 0)
                print_test("List Jobs", True, f"Found {job_count} job(s)")
                return True
            else:
                print_test("List Jobs", False, "Success=false in response")
                return False
        else:
            print_test("List Jobs", False, f"Expected 200, got {response.status_code}")
            return False

    except Exception as e:
        print_test("List Jobs", False, str(e))
        return False

def test_get_job(job_id):
    """Test GET /api/v1/scheduler/{job_id} - Get job details."""
    print_section("Test 3: Get Job Details")

    print(f"\nRequest: GET {BASE_URL}/scheduler/{job_id}")

    try:
        response = requests.get(
            f"{BASE_URL}/scheduler/{job_id}",
            headers=headers
        )

        print(f"\nStatus Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")

        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print_test("Get Job", True, f"Retrieved job: {data['data'].get('name')}")
                return True
            else:
                print_test("Get Job", False, "Success=false in response")
                return False
        else:
            print_test("Get Job", False, f"Expected 200, got {response.status_code}")
            return False

    except Exception as e:
        print_test("Get Job", False, str(e))
        return False

def test_update_job(job_id):
    """Test PUT /api/v1/scheduler/{job_id} - Update job."""
    print_section("Test 4: Update Job")

    payload = {
        "schedule_time": "10:00",
        "description": "Updated: Test newsletter at 10 AM",
        "config": {
            "max_items": 15,
            "days_back": 1,
            "sources": ["reddit", "rss"],
            "test_mode": True
        }
    }

    print(f"\nRequest: PUT {BASE_URL}/scheduler/{job_id}")
    print(f"Payload: {json.dumps(payload, indent=2)}")

    try:
        response = requests.put(
            f"{BASE_URL}/scheduler/{job_id}",
            headers=headers,
            json=payload
        )

        print(f"\nStatus Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")

        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print_test("Update Job", True, "Job updated successfully")
                return True
            else:
                print_test("Update Job", False, "Success=false in response")
                return False
        else:
            print_test("Update Job", False, f"Expected 200, got {response.status_code}")
            return False

    except Exception as e:
        print_test("Update Job", False, str(e))
        return False

def test_pause_job(job_id):
    """Test POST /api/v1/scheduler/{job_id}/pause - Pause job."""
    print_section("Test 5: Pause Job")

    print(f"\nRequest: POST {BASE_URL}/scheduler/{job_id}/pause")

    try:
        response = requests.post(
            f"{BASE_URL}/scheduler/{job_id}/pause",
            headers=headers
        )

        print(f"\nStatus Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")

        if response.status_code == 200:
            data = response.json()
            if data.get("success") and data["data"].get("status") == "paused":
                print_test("Pause Job", True, "Job paused successfully")
                return True
            else:
                print_test("Pause Job", False, "Job not paused")
                return False
        else:
            print_test("Pause Job", False, f"Expected 200, got {response.status_code}")
            return False

    except Exception as e:
        print_test("Pause Job", False, str(e))
        return False

def test_resume_job(job_id):
    """Test POST /api/v1/scheduler/{job_id}/resume - Resume job."""
    print_section("Test 6: Resume Job")

    print(f"\nRequest: POST {BASE_URL}/scheduler/{job_id}/resume")

    try:
        response = requests.post(
            f"{BASE_URL}/scheduler/{job_id}/resume",
            headers=headers
        )

        print(f"\nStatus Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")

        if response.status_code == 200:
            data = response.json()
            if data.get("success") and data["data"].get("status") == "active":
                print_test("Resume Job", True, "Job resumed successfully")
                return True
            else:
                print_test("Resume Job", False, "Job not resumed")
                return False
        else:
            print_test("Resume Job", False, f"Expected 200, got {response.status_code}")
            return False

    except Exception as e:
        print_test("Resume Job", False, str(e))
        return False

def test_run_job_now(job_id):
    """Test POST /api/v1/scheduler/{job_id}/run-now - Trigger immediate execution."""
    print_section("Test 7: Run Job Now")

    payload = {
        "test_mode": True
    }

    print(f"\nRequest: POST {BASE_URL}/scheduler/{job_id}/run-now")
    print(f"Payload: {json.dumps(payload, indent=2)}")

    try:
        response = requests.post(
            f"{BASE_URL}/scheduler/{job_id}/run-now",
            headers=headers,
            json=payload
        )

        print(f"\nStatus Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")

        if response.status_code == 200:
            data = response.json()
            if data.get("success") and "execution_id" in data.get("data", {}):
                execution_id = data["data"]["execution_id"]
                print_test("Run Job Now", True, f"Execution ID: {execution_id}")
                return execution_id
            else:
                print_test("Run Job Now", False, "Success but missing execution_id")
                return None
        else:
            print_test("Run Job Now", False, f"Expected 200, got {response.status_code}")
            return None

    except Exception as e:
        print_test("Run Job Now", False, str(e))
        return None

def test_get_history(job_id):
    """Test GET /api/v1/scheduler/{job_id}/history - Get execution history."""
    print_section("Test 8: Get Execution History")

    print(f"\nRequest: GET {BASE_URL}/scheduler/{job_id}/history?limit=10")

    try:
        response = requests.get(
            f"{BASE_URL}/scheduler/{job_id}/history",
            headers=headers,
            params={"limit": 10}
        )

        print(f"\nStatus Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")

        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                count = data["data"].get("count", 0)
                print_test("Get History", True, f"Found {count} execution(s)")
                return True
            else:
                print_test("Get History", False, "Success=false in response")
                return False
        else:
            print_test("Get History", False, f"Expected 200, got {response.status_code}")
            return False

    except Exception as e:
        print_test("Get History", False, str(e))
        return False

def test_get_stats(job_id):
    """Test GET /api/v1/scheduler/{job_id}/stats - Get execution statistics."""
    print_section("Test 9: Get Execution Statistics")

    print(f"\nRequest: GET {BASE_URL}/scheduler/{job_id}/stats")

    try:
        response = requests.get(
            f"{BASE_URL}/scheduler/{job_id}/stats",
            headers=headers
        )

        print(f"\nStatus Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")

        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                stats = data["data"]
                print_test("Get Stats", True, f"Success rate: {stats.get('success_rate', 0)}%")
                return True
            else:
                print_test("Get Stats", False, "Success=false in response")
                return False
        else:
            print_test("Get Stats", False, f"Expected 200, got {response.status_code}")
            return False

    except Exception as e:
        print_test("Get Stats", False, str(e))
        return False

def test_delete_job(job_id):
    """Test DELETE /api/v1/scheduler/{job_id} - Delete job."""
    print_section("Test 10: Delete Job")

    print(f"\nRequest: DELETE {BASE_URL}/scheduler/{job_id}")

    try:
        response = requests.delete(
            f"{BASE_URL}/scheduler/{job_id}",
            headers=headers
        )

        print(f"\nStatus Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")

        if response.status_code == 200:
            data = response.json()
            if data.get("success") and data["data"].get("deleted"):
                print_test("Delete Job", True, "Job deleted successfully")
                return True
            else:
                print_test("Delete Job", False, "Success but not deleted")
                return False
        else:
            print_test("Delete Job", False, f"Expected 200, got {response.status_code}")
            return False

    except Exception as e:
        print_test("Delete Job", False, str(e))
        return False

def main():
    """Run all tests."""
    print("\n" + "=" * 70)
    print(" " * 15 + "SCHEDULER API TEST SUITE")
    print("=" * 70)
    print(f"\nBackend: {BASE_URL}")
    print(f"Workspace: {WORKSPACE_ID}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Track results
    results = {
        "passed": 0,
        "failed": 0
    }

    # Test 1: Create job
    job_id = test_create_job()
    if job_id:
        results["passed"] += 1

        # Test 2: List jobs
        if test_list_jobs(WORKSPACE_ID):
            results["passed"] += 1
        else:
            results["failed"] += 1

        # Test 3: Get job
        if test_get_job(job_id):
            results["passed"] += 1
        else:
            results["failed"] += 1

        # Test 4: Update job
        if test_update_job(job_id):
            results["passed"] += 1
        else:
            results["failed"] += 1

        # Test 5: Pause job
        if test_pause_job(job_id):
            results["passed"] += 1
        else:
            results["failed"] += 1

        # Test 6: Resume job
        if test_resume_job(job_id):
            results["passed"] += 1
        else:
            results["failed"] += 1

        # Test 7: Run job now
        execution_id = test_run_job_now(job_id)
        if execution_id:
            results["passed"] += 1
        else:
            results["failed"] += 1

        # Test 8: Get history
        if test_get_history(job_id):
            results["passed"] += 1
        else:
            results["failed"] += 1

        # Test 9: Get stats
        if test_get_stats(job_id):
            results["passed"] += 1
        else:
            results["failed"] += 1

        # Test 10: Delete job
        if test_delete_job(job_id):
            results["passed"] += 1
        else:
            results["failed"] += 1

    else:
        results["failed"] += 1
        print("\n[WARNING] Skipping remaining tests due to job creation failure")
        print("\nPossible causes:")
        print("  1. Database migration not run (005_create_scheduler_tables.sql)")
        print("  2. Backend not running")
        print("  3. Authentication token expired")

    # Print summary
    print_section("TEST SUMMARY")
    total = results["passed"] + results["failed"]
    print(f"\nTotal Tests: {total}")
    print(f"[+] Passed: {results['passed']}")
    print(f"[-] Failed: {results['failed']}")

    if results["failed"] == 0:
        print("\n[SUCCESS] All tests passed! Scheduler API is working correctly.")
    else:
        print(f"\n[WARNING] {results['failed']} test(s) failed. Please review the output above.")

    print("\n" + "=" * 70 + "\n")

if __name__ == "__main__":
    main()
