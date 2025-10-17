# save as quick_openai_test.py and run with same interpreter your app uses
from openai import OpenAI
import os
print("OPENAI_API_KEY:", repr(os.getenv("OPENAI_API_KEY"))[:60])
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
models = client.models.list()
print(f"Found {len(models.data)} models")
print(f"First model: {models.data[0].id if models.data else 'None'}")
