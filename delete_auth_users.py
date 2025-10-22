"""
Script to delete all Supabase Auth users
"""
import requests
import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

# List of user IDs to delete
user_ids = [
    "b01ca18a-05bc-407b-a230-f0a2dc9df274",  # amit.d789@gmail.com
    "e64a9795-5397-4984-80c8-ea9016edef0f",  # nebhnanijuhi@gmail.com
    "a6e20c20-734e-4c21-910e-a932fc2fbd4b",  # helper-test-1760673303383-8yr0ei@example.com
    "88b3f687-e5e6-46bf-b1b1-a21f9cf88483",  # helper-test-1760672831421-s0x4w4@example.com
    "1f8cd2f1-3aac-4073-8005-034addb9f353",  # charlie@example.com
    "9d0fe23a-9a67-4422-b7a8-8afb603e1d3a",  # bob@example.com
    "8a760f4f-bb74-47bf-b963-aebe7f9c6873",  # alice@example.com
    "4d2130a3-6a4a-4185-bff1-5c95fb48eead",  # newsletter-1760672769625-mb20yh@example.com
    "db861f1f-0508-4dca-8677-a0191d9bdd77",  # helper-test-1760672712970-us0rp4@example.com
    "83cfdc84-f1bc-48eb-a1c9-e95bf3f98263",  # helper-test-1760671496522-pi58sk@example.com
    "ddf7720b-1725-40ed-b4b2-01209e66b96a",  # configfix@test.com
    "21866e79-3137-4ef5-95a8-f7b7867b26a9",  # finaltest99@example.com
    "f89ef4f0-faca-4382-8c75-1c2be701d0d2",  # reloadtest@example.com
    "3762ea8f-cc71-4981-b98a-a45e4b6c2feb",  # fixedtest@example.com
    "29f5e1ea-e4c7-45d2-a056-fd06d87e9cd5",  # verify@test.com
    "abe6608b-4961-4e07-b62a-eccda278375c",  # debug@test.com
    "967f58b9-c136-427b-97f7-211abf34e2d5",  # user-1760649952-4482@example.com
    "37cfff25-b701-419d-b3fb-09e91bb51255",  # user-1760643407-3623@example.com
    "c085d55c-61bd-43d9-a351-517ab6edb6bc",  # user-1760642563-8805@example.com
    "187e58c0-bb25-4e13-a14d-905079487680",  # test-1760640743684-1666@example.com
    "356c7c69-113a-4916-bcdd-21f67de5af66",  # test-1760640702994-169@example.com
    "e0881a87-20d9-4d79-ba95-e44d749f705b",  # test-api-123@example.com
    "b164cd12-4f09-4af2-a52d-efc2ce772230",  # ssbrightaccessories@gmail.com
    "20563347-edc9-4c3f-b484-95f8dc5b8950",  # jyoti_nebhnani@yahoo.co.in
    "b8b30a2e-5fff-4553-8e38-fc7c1cb974f7",  # juhinebhnani4@gmail.com
]

def delete_user(user_id):
    """Delete a single user from Supabase Auth"""
    url = f"{SUPABASE_URL}/auth/v1/admin/users/{user_id}"
    headers = {
        "apikey": SUPABASE_SERVICE_KEY,
        "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
        "Content-Type": "application/json"
    }

    response = requests.delete(url, headers=headers)
    return response.status_code, response.text

def main():
    print(f"Starting deletion of {len(user_ids)} users...")

    deleted = 0
    failed = 0

    for user_id in user_ids:
        status_code, response_text = delete_user(user_id)

        if status_code in [200, 204]:
            deleted += 1
            print(f"[OK] Deleted user: {user_id}")
        else:
            failed += 1
            print(f"[FAIL] Failed to delete user {user_id}: {status_code} - {response_text}")

    print(f"\n--- Summary ---")
    print(f"Successfully deleted: {deleted}")
    print(f"Failed: {failed}")
    print(f"Total: {len(user_ids)}")

if __name__ == "__main__":
    main()
