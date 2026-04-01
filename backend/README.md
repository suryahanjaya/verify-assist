# VerifyAssist Backend

Real-time LLM-powered verification of static analysis warnings.

## Quick Start

### 1. Install dependencies

```bash
cd backend
python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
# source venv/bin/activate

pip install -r requirements.txt
```

### 2. Configure environment

```bash
copy .env.example .env
# Edit .env and set your OpenAI API key:
# OPENAI_API_KEY=sk-...
# OPENAI_MODEL=gpt-4o        (optional, defaults to gpt-4o)
```

### 3. Run the server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Server starts at **http://localhost:8000**

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## API Reference

### `POST /verify`

Verify a static analysis warning.

**Request body:**

```json
{
  "warning_message": "Potential null pointer dereference at line 42",
  "category": "NULL_POINTER_DEREFERENCE",
  "code_snippet": "public void processUser(User user) {\n    if (user != null) {\n        logger.info(\"Processing: \" + user.getName());\n    }\n    user.updateLastAccess(); // line 42\n}",
  "optional_context": "user parameter comes from HTTP request and may be null"
}
```

**Response:**

```json
{
  "classification": "TRUE_POSITIVE",
  "confidence": 0.92,
  "explanation": "The null check at line 2 only guards the logger statement. Line 42 calls user.updateLastAccess() outside the null-check block, so a NullPointerException will occur when user is null.",
  "evidence": "Line 5: user.updateLastAccess() is outside the if (user != null) block that ends at line 4.",
  "cached": false
}
```

### `GET /`

Health check — returns service status and cache size.

### `DELETE /cache`

Clear all cached verification results.

---

## Example curl Requests

### Verify a warning (null pointer)

```bash
curl -X POST http://localhost:8000/verify \
  -H "Content-Type: application/json" \
  -d "{\"warning_message\": \"Potential null pointer dereference at line 42\", \"category\": \"NULL_POINTER_DEREFERENCE\", \"code_snippet\": \"public void processUser(User user) {\\n    if (user != null) {\\n        logger.info(\\\"Processing: \\\" + user.getName());\\n    }\\n    user.updateLastAccess(); // line 42\\n}\", \"optional_context\": \"user parameter comes from HTTP request and may be null\"}"
```

### Verify a warning (resource leak)

```bash
curl -X POST http://localhost:8000/verify \
  -H "Content-Type: application/json" \
  -d "{\"warning_message\": \"Resource leak: stream is never closed\", \"category\": \"RESOURCE_LEAK\", \"code_snippet\": \"public String readFile(String path) throws IOException {\\n    FileInputStream stream = new FileInputStream(path);\\n    byte[] data = stream.readAllBytes();\\n    return new String(data);\\n}\", \"optional_context\": \"Called frequently in a long-running server process\"}"
```

### Verify a warning (unused variable — likely false positive)

```bash
curl -X POST http://localhost:8000/verify \
  -H "Content-Type: application/json" \
  -d "{\"warning_message\": \"Unused variable: serialVersionUID\", \"category\": \"UNUSED_VARIABLE\", \"code_snippet\": \"public class User implements Serializable {\\n    private static final long serialVersionUID = 1L;\\n    private String name;\\n}\", \"optional_context\": \"Standard Java serialization pattern\"}"
```

### Health check

```bash
curl http://localhost:8000/
```

### Clear cache

```bash
curl -X DELETE http://localhost:8000/cache
```

---

## PowerShell Examples (Windows)

```powershell
# Health check
Invoke-RestMethod -Uri http://localhost:8000/

# Verify a warning
$body = @{
    warning_message = "Potential null pointer dereference at line 42"
    category = "NULL_POINTER_DEREFERENCE"
    code_snippet = @"
public void processUser(User user) {
    if (user != null) {
        logger.info("Processing: " + user.getName());
    }
    user.updateLastAccess(); // line 42
}
"@
    optional_context = "user parameter may be null"
} | ConvertTo-Json

Invoke-RestMethod -Uri http://localhost:8000/verify -Method Post -Body $body -ContentType "application/json"
```

---

## Project Structure

```
backend/
├── app/
│   ├── __init__.py          # Package marker
│   ├── main.py              # FastAPI entry point + /verify endpoint
│   ├── models.py            # Pydantic request/response models
│   ├── prompt_builder.py    # Builds system + user prompts for the LLM
│   ├── response_parser.py   # Regex parser for LLM text → VerifyResponse
│   ├── llm_client.py        # Async OpenAI API wrapper
│   └── cache.py             # In-memory SHA-256 keyed cache
├── .env.example             # Environment template
├── requirements.txt         # Python dependencies
└── README.md                # This file
```
