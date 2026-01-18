## 2024-05-22 - Information Leakage & DoS Protection
**Vulnerability:** The `/upload` endpoint returned raw exception messages (potentially including secrets/stack traces) and had no file size limit.
**Learning:** Default exception handlers often leak internal state. `file.read()` on upload endpoints can lead to OOM without limits.
**Prevention:** Implement global or endpoint-specific exception handlers that log the error but return generic messages to clients. Set explicit content length limits.
