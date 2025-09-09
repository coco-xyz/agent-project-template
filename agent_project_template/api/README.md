# API Package

This package provides a complete FastAPI-based REST API for the Agent Project Template.

## Features

- **Fail-fast imports**: No graceful degradation, dependencies must be available
- **Request ID middleware**: Automatic generation and propagation of request IDs
- **Structured logging**: Request/response logging with consistent format
- **Unified error handling**: ApplicationException-based error responses
- **Schema consistency**: Centralized request/response models
- **OpenAPI documentation**: Complete error response mapping
- **SSE streaming**: Server-Sent Events for real-time communication
- **Security middleware**: CORS, GZip, TrustedHost support
- **Metrics hooks**: Basic performance monitoring

## Quick Start

### Using the API Factory

```python
from agent_project_template.api import create_api

# Create a complete API application
app = create_api(
    title="My Agent API",
    version="1.0.0",
    enable_cors=True,
    enable_compression=True,
    enable_security=True,
    enable_metrics=True
)

# Run with uvicorn
# uvicorn main:app --reload
```

### Mounting to Existing App

```python
from fastapi import FastAPI
from agent_project_template.api import mount_api

app = FastAPI()

# Mount API components
mount_api(
    app,
    prefix="/api",
    enable_cors=True,
    enable_compression=True
)
```

### Manual Router Usage

```python
from fastapi import FastAPI
from agent_project_template.api import router

app = FastAPI()
app.include_router(router, prefix="/api")
```

## Middleware Stack

The middleware is applied in this order (first added = last executed):

1. **Exception Handlers** - Global error handling
2. **Request Logging** - HTTP request/response logging
3. **Request ID** - Generate/propagate X-Request-ID headers
4. **Security** - TrustedHost (production only)
5. **CORS** - Cross-origin resource sharing
6. **Compression** - GZip response compression
7. **Metrics** - Performance monitoring hooks

## Configuration

The API factory respects these settings from `core.config`:

```python
# CORS origins (defaults to ["*"] in debug mode)
cors_origins: List[str] = ["https://myapp.com"]

# Trusted hosts for production
trusted_hosts: List[str] = ["myapp.com", "api.myapp.com"]

# Debug mode affects default CORS and security settings
debug: bool = False
```

## Error Responses

All endpoints return standardized error responses:

```json
{
  "error": {
    "type": "AgentException",
    "message": "Demo agent is not available",
    "code": "AGENT_INIT_FAILED"
  },
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "path": "/api/v1/demo/chat",
  "method": "POST"
}
```

## Streaming Endpoints

SSE endpoints follow this format:

```
data: {"id": 0, "message": "Hello", "timestamp": 1234567890}

data: {"id": 1, "message": "World", "timestamp": 1234567891}

event: complete
data: {"status": "finished"}
```

## Adding New Endpoints

1. Create request/response schemas in `v1/schemas/`
2. Define endpoints in `v1/endpoints/`
3. Add error response mappings
4. Use ApplicationException for errors
5. Register router in `v1/__init__.py`

## Testing

```python
from fastapi.testclient import TestClient
from agent_project_template.api import create_api

app = create_api()
client = TestClient(app)

def test_health():
    response = client.get("/api/v1/demo/health")
    assert response.status_code == 200
    assert "X-Request-ID" in response.headers
```
