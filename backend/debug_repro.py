import sys
import os
from pathlib import Path

# Setup path
sys.path.append(os.getcwd())
os.environ["TEST_MODE"] = "true"
if "INVITE_CODE" in os.environ:
    del os.environ["INVITE_CODE"]

from fastapi.testclient import TestClient
from main import app

if "INVITE_CODE" in os.environ:
    del os.environ["INVITE_CODE"]

client = TestClient(app)

print("Attempting register...")
response = client.post("/register", json={"name": "DebugUser123", "password": "StrongPass1!"})
print(f"Status: {response.status_code}")
print(f"Headers: {response.headers}")
print(f"Body: {response.text}")
