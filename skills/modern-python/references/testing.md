# pytest and Coverage Reference

## pyproject.toml Configuration

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"              # pytest-asyncio: auto-detect async tests
addopts = [
    "-v",
    "--tb=short",
    "--strict-markers",            # fail on unknown markers
    "--cov=src",
    "--cov-report=term-missing",
    "--cov-report=html:htmlcov",
    "--cov-fail-under=80",
]
markers = [
    "slow: marks tests as slow (deselect with -m 'not slow')",
    "integration: marks integration tests",
    "unit: marks unit tests",
]
filterwarnings = [
    "error",                       # treat warnings as errors
    "ignore::DeprecationWarning",
]

[tool.coverage.run]
source = ["src"]
omit = [
    "tests/*",
    "**/__init__.py",
    "**/migrations/*",
]
branch = true                      # measure branch coverage

[tool.coverage.report]
show_missing = true
skip_covered = false
fail_under = 80
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "if TYPE_CHECKING:",
    "raise NotImplementedError",
    "if __name__ == .__main__.:",
]
```

## Common Fixtures

```python
# tests/conftest.py
import pytest
import httpx
from typing import AsyncGenerator
from my_service.main import app
from my_service.db import get_db, Base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture
def sample_data() -> dict:
    return {"id": 1, "name": "test", "value": 42}


@pytest.fixture(scope="module")
async def db_engine():
    """In-memory SQLite for tests."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest.fixture
async def db_session(db_engine) -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSession(db_engine) as session:
        yield session
        await session.rollback()


@pytest.fixture
async def client(db_session) -> AsyncGenerator[httpx.AsyncClient, None]:
    """Test client with overridden DB dependency."""
    app.dependency_overrides[get_db] = lambda: db_session
    try:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as c:
            yield c
    finally:
        app.dependency_overrides.clear()


@pytest.fixture(autouse=True)
def reset_env(monkeypatch):
    """Clear any env vars that might bleed between tests."""
    monkeypatch.delenv("MY_SERVICE_DEBUG", raising=False)
```

## Parametrize Patterns

```python
import pytest


# Basic parametrize
@pytest.mark.parametrize("input,expected", [
    (1, 2),
    (0, 1),
    (-1, 0),
])
def test_increment(input, expected):
    assert increment(input) == expected


# Parametrize with IDs
@pytest.mark.parametrize("value,error_type", [
    pytest.param("", ValueError, id="empty-string"),
    pytest.param(None, TypeError, id="none-value"),
    pytest.param(-1, ValueError, id="negative"),
])
def test_validate_raises(value, error_type):
    with pytest.raises(error_type):
        validate(value)


# Nested parametrize (cartesian product)
@pytest.mark.parametrize("fmt", ["json", "csv"])
@pytest.mark.parametrize("size", [10, 100, 1000])
def test_export(fmt, size):
    result = export(data=list(range(size)), format=fmt)
    assert result is not None


# Indirect parametrize (calls fixture with param)
@pytest.fixture
def user(request):
    return create_user(role=request.param)

@pytest.mark.parametrize("user", ["admin", "viewer", "editor"], indirect=True)
def test_user_access(user):
    assert user.can_login()
```

## Async Test Setup with pytest-asyncio

```bash
uv add --dev pytest-asyncio anyio
```

```python
# pytest-asyncio modes:
# "auto"   — all async test functions are async by default (recommended)
# "strict" — must use @pytest.mark.asyncio explicitly
# "loose"  — deprecated

# With asyncio_mode = "auto" in pyproject.toml, just write:
async def test_fetch():
    result = await fetch_data()
    assert result["status"] == "ok"


# Async fixtures work the same way
@pytest.fixture
async def connected_client():
    client = await MyClient.connect("127.0.0.1", 8080)
    yield client
    await client.close()


# Test with async fixture
async def test_client_request(connected_client):
    response = await connected_client.get("/health")
    assert response.status_code == 200


# Timeout for async tests
@pytest.mark.timeout(5)
async def test_does_not_hang():
    result = await operation_that_should_be_fast()
    assert result is not None
```

## Useful CLI Flags

```bash
# Run only fast tests
pytest -m "not slow"

# Run with coverage, stop after first failure
pytest --cov=src -x

# Re-run only failed tests
pytest --lf

# Run tests matching a name pattern
pytest -k "test_user or test_auth"

# Show slowest 10 tests
pytest --durations=10

# Run in parallel (install pytest-xdist)
pytest -n auto           # uses all CPUs
pytest -n 4              # use 4 workers

# Verbose output with captured stdout
pytest -v -s

# Generate HTML coverage report
pytest --cov=src --cov-report=html
open htmlcov/index.html
```
