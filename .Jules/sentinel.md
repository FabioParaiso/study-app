## 2024-10-24 - Integration Tests Side Effects
**Vulnerability:** Integration tests using `TestClient` write to production data file `current_study_data.json`.
**Learning:** `backend/storage.py` writes to a hardcoded filename in the current directory. Running tests executes this code, overwriting sample data.
**Prevention:** Future tests should mock `backend.storage` or use a temporary directory/file for `DATA_FILE`. Tests should be isolated from production artifacts.

## 2024-10-24 - Prompt Injection via Topic List
**Vulnerability:** User-controlled input (`topics` list) was injected directly into the LLM system prompt without sanitization. An attacker could inject newlines and instructions to override the system prompt.
**Learning:** Even structured inputs like lists can be vectors for Prompt Injection if they are concatenated into a prompt string.
**Prevention:** Implemented strict Pydantic validation on the `QuizRequest` model to whitelist allowed characters (alphanumeric, punctuation) and block control characters (newlines) and length abuse.

## 2025-02-18 - Overly Permissive CORS Configuration
**Vulnerability:** The backend was configured with `allow_origins=["*"]` and `allow_credentials=True`. This configuration is insecure and allows any website to make requests to the API.
**Learning:** Hardcoding development configurations (like wildcard CORS) in the main application entry point risks exposing them in production.
**Prevention:** Use environment variables (e.g., `ALLOWED_ORIGINS`) to strictly define allowed origins, defaulting to safe localhost ports for development, and ensure production deployments override this with specific domains.
