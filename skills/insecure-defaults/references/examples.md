# Insecure Defaults — Examples and Counter-Examples

## Hardcoded Secret Fallbacks

### Insecure (REPORT)
```python
# JWT secret with hardcoded fallback
SECRET_KEY = os.environ.get("JWT_SECRET", "change-me-in-production")
token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

# Database password with default
DB_PASSWORD = os.getenv("DB_PASS") or "postgres"
```

### Secure (SKIP)
```python
# Crash on missing secret — fail-closed
SECRET_KEY = os.environ["JWT_SECRET"]  # KeyError if missing

# Explicit validation
secret = os.getenv("JWT_SECRET")
if not secret:
    raise RuntimeError("JWT_SECRET environment variable is required")
```

## Default Credentials

### Insecure (REPORT)
```python
# Admin account with known password
ADMIN_USER = "admin"
ADMIN_PASS = "admin123"

# API key fallback
API_KEY = config.get("api_key", "sk-test-key-12345")
```

### Secure (SKIP)
```python
# Test fixture credentials (clearly scoped)
@pytest.fixture
def test_admin():
    return {"user": "test_admin", "pass": "test_pass"}

# Example in documentation
# Example: API_KEY=sk-your-key-here
```

## Fail-Open Security Controls

### Insecure (REPORT)
```python
# Auth disabled by default
AUTH_REQUIRED = os.getenv("AUTH_REQUIRED", "false").lower() == "true"

# CORS wildcard
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*")

# Debug mode on by default
DEBUG = os.getenv("DEBUG", "true").lower() == "true"
```

### Secure (SKIP)
```python
# Auth enabled by default (fail-closed)
AUTH_REQUIRED = os.getenv("AUTH_REQUIRED", "true").lower() != "false"

# Restrictive CORS default
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "").split(",")

# Debug off by default
DEBUG = os.getenv("DEBUG", "false").lower() == "true"
```

## Weak Cryptography

### Insecure (REPORT)
```python
# MD5 for password hashing
password_hash = hashlib.md5(password.encode()).hexdigest()

# ECB mode encryption
cipher = AES.new(key, AES.MODE_ECB)

# SHA1 for HMAC
hmac.new(secret, msg, hashlib.sha1)
```

### Secure (SKIP)
```python
# bcrypt for passwords
password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

# MD5 for non-security checksum
file_hash = hashlib.md5(data).hexdigest()  # integrity check only
```

## Permissive File/Network Access

### Insecure (REPORT)
```python
# World-writable permissions
os.chmod(config_file, 0o777)

# Binding to all interfaces by default
app.run(host="0.0.0.0", port=8080)  # in production config

# Public S3 bucket
bucket_acl = os.getenv("S3_ACL", "public-read")
```

### Secure (SKIP)
```python
# Restrictive permissions
os.chmod(config_file, 0o600)

# Localhost binding
app.run(host="127.0.0.1", port=8080)

# Private by default
bucket_acl = os.getenv("S3_ACL", "private")
```

## Debug/Verbose Error Exposure

### Insecure (REPORT)
```python
# Stack trace in API response
@app.exception_handler(Exception)
async def handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"error": str(exc), "traceback": traceback.format_exc()}
    )

# SQL query in error message
except sqlite3.Error as e:
    return {"error": f"Query failed: {query} — {e}"}
```

### Secure (SKIP)
```python
# Generic error to client, detailed log server-side
@app.exception_handler(Exception)
async def handler(request, exc):
    logger.exception("Unhandled error")
    return JSONResponse(status_code=500, content={"error": "Internal server error"})
```

## Environment Variable Patterns

### Red Flags (Always Investigate)
```
SECRET = env.get("X") or "fallback"     # Fallback secret
KEY = env.get("X", "default-key")        # Default API key
PASSWORD = env.get("X", "password")      # Default password
ENABLED = env.get("X", "false")          # Security feature off by default
```

### Safe Patterns
```
SECRET = env["X"]                         # Crash if missing (fail-closed)
KEY = env.get("X")                        # None if missing (no fallback)
if not key: raise ValueError("X required") # Explicit validation
ENABLED = env.get("X", "true")            # Security feature on by default
```
