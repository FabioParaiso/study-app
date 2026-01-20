## 2024-10-24 - Integration Tests Side Effects
**Vulnerability:** Integration tests using `TestClient` write to production data file `current_study_data.json`.
**Learning:** `backend/storage.py` writes to a hardcoded filename in the current directory. Running tests executes this code, overwriting sample data.
**Prevention:** Future tests should mock `backend.storage` or use a temporary directory/file for `DATA_FILE`. Tests should be isolated from production artifacts.

## 2024-10-24 - Prompt Injection via Topic List
**Vulnerability:** User-controlled input (`topics` list) was injected directly into the LLM system prompt without sanitization. An attacker could inject newlines and instructions to override the system prompt.
**Learning:** Even structured inputs like lists can be vectors for Prompt Injection if they are concatenated into a prompt string.
**Prevention:** Implemented strict Pydantic validation on the `QuizRequest` model to whitelist allowed characters (alphanumeric, punctuation) and block control characters (newlines) and length abuse.
