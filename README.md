# AI Agent Project Template

A production-ready template for building AI agent applications with Pydantic-AI + FastAPI. This template provides a clean foundation with structured logging, error handling, configuration management, and Docker support.

> 📖 **中文文档**: [README_zh.md](README_zh.md)

## Features

- 🤖 **AI Agent Framework**: Built with Pydantic-AI for robust agent development
- 🚀 **FastAPI Integration**: RESTful API endpoints with automatic documentation
- ⚡ **Fast Dependency Management**: Uses uv for lightning-fast package management
- 📝 **Structured Logging**: Comprehensive logging with Logfire integration
- 🔧 **Configuration Management**: Environment-based configuration with Pydantic Settings
- 🐳 **Docker Support**: Ready-to-use Docker configuration
- 🧪 **Testing Framework**: Pre-configured pytest setup with async support
- 📚 **Documentation**: Comprehensive documentation and examples
- 🛠️ **Development Tools**: Makefile with common development commands
- 🌐 **Dual Language**: English and Chinese documentation

## Quick Start

### Prerequisites

- Python 3.11+
- [cookiecutter](https://cookiecutter.readthedocs.io/)
- [uv](https://docs.astral.sh/uv/) (recommended for fast dependency management)

### Install cookiecutter

```bash
# Using pip
pip install cookiecutter

# Using uv
uv tool install cookiecutter

# Using conda
conda install cookiecutter

# Using homebrew (macOS)
brew install cookiecutter
```

### Create a New Project

1. **Generate project from template:**
```bash
cookiecutter gh:coco-xyz/agent-project-template
```

2. **Answer the prompts:**
```
project_name [My Awesome Project]: Your AI Agent Project
project_slug [your_ai_agent_project]: your-project-name
```

3. **Navigate to your new project:**
```bash
cd your-project-name
```

4. **Set up the project:**
```bash
# Install uv if you haven't already
pip install uv

# Complete project setup (installs dependencies, creates .env, etc.)
make setup
```

5. **Start developing:**
```bash
# Run in CLI mode
make run-cli

# Or run API server
make run-api
```

## Template Configuration

The template uses the following variables in `cookiecutter.json`:

| Variable | Description | Default |
|----------|-------------|---------|
| `project_name` | Human-readable project name | "My Awesome Project" |
| `project_slug` | Python package name (snake_case) | "my_awesome_project" |

## Project Structure

After generation, your project will have this structure:

```
your-project-name/
├── src/                     # Main source code
│   ├── core/                # Core modules (config, logging, LLM, etc.)
│   ├── agents/              # AI Agent implementations
│   ├── api/                 # FastAPI routes and endpoints
│   │   ├── errors/          # Error handling
│   │   ├── schemas/         # API schemas
│   │   └── v1/              # API version 1 endpoints
│   ├── models/              # Data models
│   ├── services/            # Business logic services
│   ├── stores/              # Database and cache stores
│   ├── prompts/             # AI prompts and templates
│   └── utils/               # Utility functions
├── tests/                   # Test files
├── docs/                    # Documentation
├── logs/                    # Log files (created at runtime)
├── migrations/              # Database migrations
├── initdb/                  # Database initialization scripts
├── main.py                  # Application entry point
├── pyproject.toml           # Project configuration
├── uv.lock                  # Dependency lock file
├── env.sample               # Environment variables template
├── docker-compose.yml       # Docker compose configuration
├── docker-compose.middleware.yml  # Middleware services only
├── Dockerfile               # Docker configuration
├── Makefile                 # Development commands
├── README.md                # English documentation
└── README_zh.md             # Chinese documentation
```

## What's Included

### Core Components

- **Agent Framework**: Base classes for building AI agents
- **API Layer**: FastAPI application with health checks and agent endpoints
- **Configuration**: Environment-based settings with validation
- **Logging**: Structured logging with Logfire integration
- **Error Handling**: Comprehensive error handling and validation

### Development Tools

- **Makefile**: Common development commands (`make help` to see all)
- **Testing**: pytest with async support and coverage
- **Code Quality**: black, isort, flake8, mypy pre-configured
- **Docker**: Multi-stage Dockerfile for production deployment

### Dependencies

- **pydantic-ai**: Modern AI agent framework
- **FastAPI**: High-performance web framework
- **Logfire**: Advanced logging and observability
- **Pydantic**: Data validation and settings management
- **uvicorn**: ASGI server for production

## Usage Examples

### CLI Mode
```bash
# Interactive CLI
make run-cli

# Direct command
uv run python main.py --mode cli
```

### API Mode
```bash
# Start API server
make run-api

# With hot reload for development
make run-api-dev

# Access interactive docs at http://localhost:8080/docs
```

### Development Commands
```bash
# View all available commands
make help

# Run tests
make test

# Format code
make format

# Type checking
make type-check

# Build Docker image
make docker-build
```

## Customization

After generating your project, you can customize:

1. **Agent Logic**: Implement your AI agents in `src/agents/`
2. **API Endpoints**: Add routes in `src/api/`
3. **Configuration**: Modify settings in `src/core/config.py`
4. **Dependencies**: Update `pyproject.toml` and run `uv sync`

## Contributing

Contributions to improve this template are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This template is released under the MIT License. Projects generated from this template can use any license you choose.

## Support

- 📖 **Documentation**: Check the generated project's README files
- 🐛 **Issues**: Report bugs or request features on GitHub
- 💬 **Discussions**: Join the community discussions

---

**Happy coding! 🚀**
