## 2024-10-24 - Integration Tests Side Effects
**Vulnerability:** Integration tests using `TestClient` write to production data file `current_study_data.json`.
**Learning:** `backend/storage.py` writes to a hardcoded filename in the current directory. Running tests executes this code, overwriting sample data.
**Prevention:** Future tests should mock `backend.storage` or use a temporary directory/file for `DATA_FILE`. Tests should be isolated from production artifacts.
