# Secure Coding Reference
## Python & Go Patterns for AI Infrastructure

### Table of Contents
1. [Input Validation](#input-validation)
2. [Secrets & Configuration](#secrets)
3. [Authentication & Authorization](#auth)
4. [API Security (FastAPI)](#api-security)
5. [Injection Prevention](#injection)
6. [Dependency Management](#dependencies)
7. [Logging & Error Handling](#logging)
8. [Cryptography](#crypto)
9. [Docker & Deployment](#docker-deploy)
10. [Go-Specific Patterns](#go-patterns)

---

## Input Validation {#input-validation}

### Python: Pydantic Models (FastAPI)

Every external input must go through a Pydantic model. Never trust raw request data.

```python
from pydantic import BaseModel, Field, validator
from typing import Optional
import re

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=10000)
    session_id: str = Field(..., pattern=r"^[a-f0-9]{32}$")
    model: Optional[str] = Field(default="claude-sonnet-4-20250514")
    
    @validator("message")
    def sanitize_message(cls, v):
        # Strip null bytes and control characters
        v = v.replace("\x00", "")
        v = re.sub(r"[\x01-\x08\x0b\x0c\x0e-\x1f]", "", v)
        return v.strip()
    
    @validator("model")
    def validate_model(cls, v):
        allowed = {"claude-sonnet-4-20250514", "claude-haiku-4-5-20251001", "claude-opus-4-6"}
        if v not in allowed:
            raise ValueError(f"Model must be one of {allowed}")
        return v
```

### Path Traversal Prevention

```python
import os
from pathlib import Path

ALLOWED_BASE = Path("/opt/hydra-project/data")

def safe_file_read(user_path: str) -> str:
    """Read a file safely, preventing path traversal."""
    # Resolve to absolute, following symlinks
    resolved = (ALLOWED_BASE / user_path).resolve()
    
    # Verify it's still under the allowed base
    if not str(resolved).startswith(str(ALLOWED_BASE.resolve())):
        raise ValueError(f"Path traversal attempt: {user_path}")
    
    if not resolved.is_file():
        raise FileNotFoundError(f"Not a file: {user_path}")
    
    return resolved.read_text()
```

### Go: Input Validation

```go
import (
    "fmt"
    "regexp"
    "strings"
)

var sessionIDRegex = regexp.MustCompile(`^[a-f0-9]{32}$`)

type ChatRequest struct {
    Message   string `json:"message" validate:"required,min=1,max=10000"`
    SessionID string `json:"session_id" validate:"required"`
    Model     string `json:"model,omitempty"`
}

func (r *ChatRequest) Validate() error {
    r.Message = strings.TrimSpace(r.Message)
    if r.Message == "" {
        return fmt.Errorf("message cannot be empty")
    }
    if !sessionIDRegex.MatchString(r.SessionID) {
        return fmt.Errorf("invalid session ID format")
    }
    allowedModels := map[string]bool{
        "claude-sonnet-4-20250514": true,
        "claude-haiku-4-5-20251001":  true,
    }
    if r.Model != "" && !allowedModels[r.Model] {
        return fmt.Errorf("invalid model: %s", r.Model)
    }
    return nil
}
```

---

## Secrets & Configuration {#secrets}

### Never Hardcode Secrets

```python
# BAD — hardcoded secret
ANTHROPIC_API_KEY = "sk-ant-api03-xxxx"

# BAD — committed .env file
load_dotenv()  # .env not in .gitignore

# GOOD — environment variable with validation
import os

def get_required_env(key: str) -> str:
    """Get a required environment variable or fail fast."""
    value = os.environ.get(key)
    if not value:
        raise RuntimeError(f"Required environment variable {key} is not set")
    return value

ANTHROPIC_API_KEY = get_required_env("ANTHROPIC_API_KEY")
```

### Docker Secrets in Python

```python
from pathlib import Path

def read_docker_secret(name: str, default: str = None) -> str:
    """Read a Docker Swarm secret from /run/secrets/."""
    secret_path = Path(f"/run/secrets/{name}")
    if secret_path.is_file():
        return secret_path.read_text().strip()
    if default is not None:
        return default
    raise RuntimeError(f"Docker secret '{name}' not found and no default provided")

DB_PASSWORD = read_docker_secret("db_password")
```

### .gitignore Essentials

```gitignore
# Secrets — NEVER commit
.env
.env.*
*.pem
*.key
credentials.yaml
secrets/

# Docker
docker-compose.override.yml

# Python
__pycache__/
*.pyc
.venv/

# IDE
.vscode/
.idea/
```

### Pre-Commit Hook for Secret Detection

```bash
#!/bin/bash
# .git/hooks/pre-commit
# Prevent committing secrets

PATTERNS=(
    "sk-ant-"
    "sk-[a-zA-Z0-9]{20,}"
    "AKIA[0-9A-Z]{16}"
    "password\s*=\s*['\"]"
    "api_key\s*=\s*['\"]"
    "BEGIN RSA PRIVATE KEY"
    "BEGIN OPENSSH PRIVATE KEY"
)

for pattern in "${PATTERNS[@]}"; do
    if git diff --cached --diff-filter=ACM | grep -qiP "$pattern"; then
        echo "ERROR: Potential secret detected matching pattern: $pattern"
        echo "Use 'git diff --cached' to find and remove it."
        exit 1
    fi
done
```

---

## Authentication & Authorization {#auth}

### FastAPI JWT Authentication

```python
from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt

SECRET_KEY = read_docker_secret("jwt_secret")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE = timedelta(hours=1)

security = HTTPBearer()

def create_access_token(subject: str) -> str:
    expire = datetime.now(timezone.utc) + ACCESS_TOKEN_EXPIRE
    payload = {"sub": subject, "exp": expire, "iat": datetime.now(timezone.utc)}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    try:
        payload = jwt.decode(
            credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM]
        )
        subject = payload.get("sub")
        if subject is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return subject
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

# Usage
@app.get("/api/secure")
async def secure_endpoint(user: str = Depends(verify_token)):
    return {"user": user}
```

### Service-to-Service Auth (Internal)

For internal services (Christi → ChromaDB, Tax Prep → Milvus), use shared secrets via Docker secrets:

```python
from fastapi import Request, HTTPException

INTERNAL_API_KEY = read_docker_secret("internal_api_key")

async def verify_internal(request: Request):
    key = request.headers.get("X-Internal-Key")
    if key != INTERNAL_API_KEY:
        raise HTTPException(status_code=403, detail="Forbidden")
```

---

## API Security (FastAPI) {#api-security}

### CORS Configuration

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Restrictive CORS — only allow known origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://yourdomain.com",
        "http://127.0.0.1:3000",  # Local dev only
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type"],
    max_age=3600,
)
```

### Rate Limiting

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/api/chat")
@limiter.limit("30/minute")
async def chat(request: Request, body: ChatRequest):
    ...
```

### Request Size Limits

```python
from fastapi import FastAPI

app = FastAPI()

# Limit request body size (prevent DoS)
@app.middleware("http")
async def limit_body_size(request: Request, call_next):
    MAX_BODY = 10 * 1024 * 1024  # 10MB
    content_length = request.headers.get("content-length")
    if content_length and int(content_length) > MAX_BODY:
        raise HTTPException(status_code=413, detail="Request too large")
    return await call_next(request)
```

### Security Headers Middleware

```python
from starlette.middleware.base import BaseHTTPMiddleware

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        # Remove server header
        if "server" in response.headers:
            del response.headers["server"]
        return response

app.add_middleware(SecurityHeadersMiddleware)
```

---

## Injection Prevention {#injection}

### SQL Injection (if using raw SQL)

```python
# BAD — string concatenation
cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")

# GOOD — parameterized query
cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))

# GOOD — SQLAlchemy ORM (preferred)
user = session.query(User).filter(User.id == user_id).first()
```

### Command Injection

```python
import subprocess

# BAD — shell=True with user input
subprocess.run(f"grep {user_input} /var/log/app.log", shell=True)

# GOOD — list args, no shell
subprocess.run(["grep", user_input, "/var/log/app.log"], shell=False, check=True)

# BETTER — use Python libraries instead of shell commands
import re
with open("/var/log/app.log") as f:
    matches = [line for line in f if re.search(re.escape(user_input), line)]
```

### Template Injection (Jinja2)

```python
from jinja2 import Environment, select_autoescape

# GOOD — autoescape enabled
env = Environment(autoescape=select_autoescape(["html", "xml"]))

# BAD — rendering user input as template
template = env.from_string(user_input)  # NEVER do this
```

### SSRF Prevention

```python
import ipaddress
from urllib.parse import urlparse

BLOCKED_RANGES = [
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("169.254.0.0/16"),
]

def validate_url(url: str) -> bool:
    """Prevent SSRF by blocking internal network targets."""
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        return False
    try:
        import socket
        ip = socket.gethostbyname(parsed.hostname)
        addr = ipaddress.ip_address(ip)
        for blocked in BLOCKED_RANGES:
            if addr in blocked:
                return False
    except (socket.gaierror, ValueError):
        return False
    return True
```

---

## Dependency Management {#dependencies}

### Pin All Dependencies

```
# requirements.txt — pin exact versions
anthropic==0.49.0
fastapi==0.115.6
pydantic==2.10.4
uvicorn==0.34.0
python-jose[cryptography]==3.3.0
```

### Vulnerability Scanning

```bash
# pip-audit — check for known vulnerabilities
pip install pip-audit
pip-audit -r requirements.txt

# safety — alternative scanner
pip install safety
safety check -r requirements.txt

# Automate in CI or pre-deploy
```

### Go Module Security

```bash
# Check for vulnerabilities
govulncheck ./...

# Keep modules updated
go get -u ./...
go mod tidy
```

---

## Logging & Error Handling {#logging}

### Secure Logging (Never Log Secrets)

```python
import structlog
import re

def redact_secrets(_, __, event_dict):
    """Redact sensitive values from log output."""
    patterns = [
        (r"sk-ant-[a-zA-Z0-9-]+", "sk-ant-***REDACTED***"),
        (r"sk-[a-zA-Z0-9]{20,}", "sk-***REDACTED***"),
        (r"password['\"]?\s*[:=]\s*['\"]?[^\s,}]+", "password=***REDACTED***"),
        (r"token['\"]?\s*[:=]\s*['\"]?[^\s,}]+", "token=***REDACTED***"),
    ]
    msg = event_dict.get("event", "")
    if isinstance(msg, str):
        for pattern, replacement in patterns:
            msg = re.sub(pattern, replacement, msg, flags=re.IGNORECASE)
        event_dict["event"] = msg
    return event_dict

structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        redact_secrets,
        structlog.processors.JSONRenderer(),
    ]
)

logger = structlog.get_logger()
```

### Error Handling (Don't Leak Internals)

```python
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    # Log the full error internally
    logger.error("unhandled_exception", error=str(exc), path=request.url.path)
    
    # Return sanitized error to client
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},  # No stack traces, no internals
    )
```

---

## Cryptography {#crypto}

### Password Hashing

```python
# Use bcrypt or argon2 — NEVER MD5/SHA1/SHA256 for passwords
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

hashed = pwd_context.hash("plaintext_password")
verified = pwd_context.verify("plaintext_password", hashed)
```

### Encryption at Rest

```python
from cryptography.fernet import Fernet

# Generate key (store securely via Docker secret)
key = Fernet.generate_key()  # Store this, don't regenerate
cipher = Fernet(key)

# Encrypt
encrypted = cipher.encrypt(b"sensitive data")

# Decrypt
decrypted = cipher.decrypt(encrypted)
```

### Secure Random Generation

```python
import secrets

# Generate secure tokens
token = secrets.token_urlsafe(32)  # URL-safe base64
hex_token = secrets.token_hex(32)  # Hex string

# NEVER use random.random() for security-sensitive values
# random module is NOT cryptographically secure
```

---

## Docker & Deployment {#docker-deploy}

### Dockerfile Security

```dockerfile
# Use specific version, not :latest
FROM python:3.12-slim@sha256:<pin-digest>

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser -d /app -s /sbin/nologin appuser

# Install dependencies as root, then switch
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY --chown=appuser:appuser app/ /app/

# Switch to non-root
USER appuser

# Don't run as PID 1 without signal handling
# Use tini or exec form
ENTRYPOINT ["python", "-m", "app"]

# Health check
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health')"
```

### Docker Compose Security

```yaml
services:
  api:
    image: myapp:latest
    read_only: true
    security_opt:
      - no-new-privileges:true
    cap_drop:
      - ALL
    tmpfs:
      - /tmp
    networks:
      - backend
    # Never use host network mode
    # network_mode: host  # BAD
    secrets:
      - db_password
      - api_key

secrets:
  db_password:
    external: true
  api_key:
    external: true

networks:
  backend:
    driver: overlay
    driver_opts:
      encrypted: "true"
```

---

## Go-Specific Patterns {#go-patterns}

### HTTP Server Security

```go
import (
    "net/http"
    "time"
)

srv := &http.Server{
    Addr:              "127.0.0.1:8080",
    ReadTimeout:       10 * time.Second,
    ReadHeaderTimeout: 5 * time.Second,
    WriteTimeout:      30 * time.Second,
    IdleTimeout:       120 * time.Second,
    MaxHeaderBytes:    1 << 20, // 1MB
    Handler:           mux,
}
```

### Context-Aware Operations

```go
// Always use context for cancellation and timeouts
func processRequest(ctx context.Context, input string) (string, error) {
    ctx, cancel := context.WithTimeout(ctx, 30*time.Second)
    defer cancel()
    
    select {
    case result := <-doWork(ctx, input):
        return result, nil
    case <-ctx.Done():
        return "", ctx.Err()
    }
}
```

### Safe File Operations

```go
import (
    "fmt"
    "path/filepath"
    "strings"
)

const allowedBase = "/opt/hydra-project/data"

func safeReadFile(userPath string) ([]byte, error) {
    // Clean and resolve the path
    cleaned := filepath.Clean(userPath)
    absPath := filepath.Join(allowedBase, cleaned)
    resolved, err := filepath.EvalSymlinks(absPath)
    if err != nil {
        return nil, fmt.Errorf("invalid path: %w", err)
    }
    
    // Verify it's under the allowed base
    if !strings.HasPrefix(resolved, allowedBase) {
        return nil, fmt.Errorf("path traversal attempt: %s", userPath)
    }
    
    return os.ReadFile(resolved)
}
```
