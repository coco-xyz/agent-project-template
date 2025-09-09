# Architecture Guide

This document outlines the module hierarchy, import guidelines, and architectural principles for the Agent Project Template.

## Module Hierarchy

The codebase follows a strict layered architecture to prevent circular dependencies and maintain clean separation of concerns:

```
┌─────────────────────────────────────────────────────────────┐
│                    api/cli (Top Layer)                     │
│                 User interfaces and endpoints              │
├─────────────────────────────────────────────────────────────┤
│                      services                              │
│                   Business logic                           │
├─────────────────────────────────────────────────────────────┤
│                       agents                               │
│                    AI agents                               │
├─────────────────────────────────────────────────────────────┤
│                       stores                               │
│           Database, Redis, and data persistence            │
├─────────────────────────────────────────────────────────────┤
│                       utils                                │
│           Utility functions (can depend on core)           │
├─────────────────────────────────────────────────────────────┤
│                       core                                 │
│        Configuration, logging, exceptions, error codes     │
├─────────────────────────────────────────────────────────────┤
│                      models                                │
│              Data models and schemas (Bottom Layer)        │
└─────────────────────────────────────────────────────────────┘
```

### Layer Descriptions

#### 1. **models** (Bottom Layer)
- **Purpose**: Data models, schemas, and type definitions
- **Dependencies**: None (pure data structures)
- **Examples**: Pydantic models, SQLAlchemy models, type definitions

#### 2. **core** (Foundation Layer)
- **Purpose**: Application-specific foundational components
- **Dependencies**: models only
- **Contains**:
  - Configuration management (`config.py`)
  - Logging system (`logger.py`)
  - Exception classes (`exceptions.py`)
  - Error codes (`error_codes.py`)
  - Logfire configuration (`logfire_config.py`)

#### 3. **utils** (Application Utilities)
- **Purpose**: Utility functions that may depend on application configuration
- **Dependencies**: core, models
- **Contains**:
  - Snowflake ID generator (uses core config and logging)
  - Generic helper functions
  - Third-party library wrappers that need configuration

#### 4. **stores** (Data Layer)
- **Purpose**: Data persistence and external service connections
- **Dependencies**: core, utils, models
- **Contains**:
  - Database connections and operations
  - Redis client and operations
  - File storage utilities
  - External API clients

#### 5. **agents** (AI Agent Layer)
- **Purpose**: AI agents and agent-specific logic
- **Dependencies**: stores, core, utils, models
- **Contains**:
  - AI agents and their implementations
  - Agent-specific utilities
  - Agent conversation management

#### 6. **services** (Business Logic Layer)
- **Purpose**: Business logic and application services
- **Dependencies**: agents, stores, core, utils, models
- **Contains**:
  - Business services
  - Data processing pipelines
  - Orchestration logic

#### 7. **api/cli** (Interface Layer)
- **Purpose**: User interfaces and external communication
- **Dependencies**: services, agents, stores, core, utils, models
- **Contains**:
  - REST API endpoints
  - CLI commands
  - Middleware
  - Request/response handling

## Import Guidelines

### ✅ Correct Import Patterns

```python
# Lower layers can import from even lower layers
# core can import from models
from agent_project_template.models.user import User

# utils can import from core and models
from agent_project_template.core.config import settings
from agent_project_template.core.logger import get_logger
from agent_project_template.models.user import User

# stores can import from utils, core, models
from agent_project_template.core.config import settings
from agent_project_template.core.logger import get_logger
from agent_project_template.utils.snowflake_generator import generate_snowflake_id
from agent_project_template.models.session import Session

# agents can import from stores, utils, core, models
from agent_project_template.stores.database import get_db_dependency
from agent_project_template.core.exceptions import ValidationException
from agent_project_template.utils.snowflake_generator import SnowflakeGenerator

# services can import from agents, stores, utils, core, models
from agent_project_template.agents.demo_agent import DemoAgent
from agent_project_template.stores.database import get_db_dependency
from agent_project_template.core.exceptions import ValidationException
from agent_project_template.utils.snowflake_generator import SnowflakeGenerator

# api can import from all lower layers
from agent_project_template.services.demo_service import DemoService
from agent_project_template.agents.demo_agent import DemoAgent
from agent_project_template.stores.redis_client import get_redis_client
from agent_project_template.core.logger import get_logger
```

### ❌ Incorrect Import Patterns

```python
# NEVER: Higher layers importing from lower layers
# core importing from utils (WRONG)
from agent_project_template.utils.snowflake_generator import generate_snowflake_id  # ❌

# NEVER: core importing from stores (WRONG)
from agent_project_template.stores.database import get_db_dependency  # ❌

# NEVER: agents importing from services (WRONG)
from agent_project_template.services.demo_service import DemoService  # ❌

# NEVER: stores importing from agents (WRONG)
from agent_project_template.agents.demo_agent import DemoAgent  # ❌

# NEVER: models importing from any other layer
# models importing from core (WRONG)
from agent_project_template.core.logger import get_logger  # ❌

# NEVER: Circular dependencies
# If A imports B, then B should never import A
```

## Dependency Rules

### 1. **Unidirectional Dependencies**
- Dependencies flow **downward only** in the hierarchy
- Higher layers depend on lower layers, never the reverse
- Each layer can only import from layers below it

### 2. **No Circular Dependencies**
- If module A imports module B, then B must never import A (directly or indirectly)
- Use dependency injection or event systems to break circular dependencies

### 3. **Layer Isolation**
- **utils** can depend on core for configuration and logging but should not contain business logic
- **models** should contain only data structures, no business logic
- **core** contains application-specific foundations but no business logic

### 4. **Interface Segregation**
- Each layer should expose clean, minimal interfaces to upper layers
- Avoid exposing internal implementation details

## Migration Notes

### Logger Module Migration
The logging functionality has been moved from `utils` to `core` to establish proper hierarchy:

```python
# OLD (no longer available)
from agent_project_template.utils.logger import get_logger  # ❌ ImportError

# NEW (required)
from agent_project_template.core.logger import get_logger  # ✅
```

**Rationale**: Logging configuration depends on application settings, making it application-specific rather than a pure utility. The deprecated compatibility wrapper has been removed to enforce clean imports.

## Best Practices

### 1. **When Adding New Modules**
1. Identify which layer the module belongs to
2. Ensure it only imports from lower layers
3. Update this documentation if adding new patterns

### 2. **Dependency Injection**
Use dependency injection to avoid tight coupling:

```python
# Good: Inject dependencies
def process_data(db_client, logger, config):
    # Implementation

# Better: Use dependency injection framework or factory pattern
class DataProcessor:
    def __init__(self, db_client: DatabaseClient, logger: Logger):
        self.db_client = db_client
        self.logger = logger
```

### 3. **Configuration Management**
- All configuration should flow from `core.config`
- Utils can import configuration directly from core when needed
- Higher layers (stores, services, api) should receive configuration as parameters when possible
- Use environment variables and `.env` files for external configuration

### 4. **Error Handling**
- Use standardized exceptions from `core.exceptions`
- Use error codes from `core.error_codes`
- Maintain consistent error handling patterns across layers

## Validation Tools

### Checking Dependencies
You can validate the dependency structure using tools like:

```bash
# Check for circular imports
python -m py_compile agent_project_template/

# Use dependency analysis tools
pip install pydeps
pydeps agent_project_template --show-deps
```

### Import Linting
Configure your IDE or CI/CD to detect violations:

```python
# Example: Custom import checker
def check_imports(file_path):
    # Implement logic to validate import patterns
    # Flag violations of the hierarchy rules
    pass
```

## Future Considerations

### Microservices Migration
This architecture supports future microservice extraction:
- Each layer can potentially become a separate service
- Clean interfaces make service boundaries clear
- Dependency injection facilitates service communication

### Plugin Architecture
The layered structure supports plugin development:
- Plugins can extend specific layers
- Core functionality remains stable
- New features can be added without modifying existing layers

---

**Remember**: This architecture is designed to scale with your project. Start simple, but maintain the principles to avoid technical debt as your codebase grows.
