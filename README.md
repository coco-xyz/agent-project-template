# Agent Project Template

A production-ready template for building AI agent applications using pydantic-ai and FastAPI. This template provides a solid foundation with best practices, comprehensive configuration management, and flexible deployment options.

## ✨ Features

- **🤖 Agent Framework**: Built on [pydantic-ai](https://github.com/pydantic/pydantic-ai) for type-safe AI agent development
- **🚀 Dual Mode Support**: Run as CLI application or FastAPI web service
- **🔧 Comprehensive Configuration**: Environment-based configuration with validation
- **📊 Multiple LLM Support**: OpenAI, Anthropic, Google, OpenRouter, and more
- **🗄️ Database Integration**: PostgreSQL with SQLAlchemy ORM
- **⚡ Redis Support**: Caching and distributed locking
- **📝 Structured Logging**: Integrated with Pydantic Logfire
- **🛡️ Error Handling**: Comprehensive exception handling and error codes
- **🔒 Type Safety**: Full type safety with Pydantic models
- **🐳 Container Ready**: Docker support for easy deployment

## 🏗️ Technology Stack

- **Core Framework**: [pydantic-ai](https://github.com/pydantic/pydantic-ai) 0.8.1
- **Web Framework**: FastAPI 0.115.12
- **Python**: 3.11 (fixed version)
- **ASGI Server**: uvicorn 0.35.0
- **Database**: PostgreSQL with SQLAlchemy
- **Cache**: Redis
- **Monitoring**: Pydantic Logfire
- **Package Manager**: uv

## 🚀 Quick Start

### Prerequisites

- Python 3.11 (exact version required)
- uv package manager
- PostgreSQL (optional, for database features)
- Redis (optional, for caching and locking)

### Installation

1. **Clone and setup**:
```bash
git clone <your-repo-url>
cd agent-project-template
```

2. **Install uv** (if not already installed):
```bash
pip install uv
```

3. **Create virtual environment** (optional but recommended):
```bash
uv venv .venv
source .venv/bin/activate  # Linux/macOS
# or
.venv\Scripts\activate     # Windows
```

4. **Install dependencies**:
```bash
uv sync
```

5. **Configure environment**:
```bash
cp env.sample .env
# Edit .env with your API keys and configuration
```

### Running the Application

#### CLI Mode (Default)
```bash
python main.py --mode cli
# or simply
python main.py
```

#### API Mode
```bash
python main.py --mode api
```

The API will be available at `http://localhost:8080` with interactive docs at `/docs`.

## 🏗️ Project Structure

```
agent_project_template/
├── agents/                 # AI agent definitions
│   ├── __init__.py
│   └── demo_agent.py      # Example agent implementation
├── api/                   # FastAPI application
│   ├── v1/               # API version 1
│   │   ├── endpoints/    # API endpoints
│   │   └── schemas/      # Request/response models
│   └── middleware.py     # Custom middleware
├── core/                 # Core functionality
│   ├── config.py         # Configuration management
│   ├── exceptions.py     # Custom exceptions
│   ├── llm_factory.py    # LLM model factory
│   └── database.py       # Database connection
├── services/             # Business logic layer
├── stores/               # Data persistence layer
├── utils/                # Utility functions
└── prompts/              # Prompt templates
```

## 🔧 Configuration

The template uses environment-based configuration. Key settings include:

- **LLM Configuration**: API keys and model settings for various providers
- **Database**: PostgreSQL connection settings
- **Redis**: Cache and locking configuration
- **API**: FastAPI server settings
- **Logging**: Logfire integration settings

See `env.sample` for all available configuration options.

## 🤖 Creating Your First Agent

1. **Define your agent** in `agents/your_agent.py`:
```python
from pydantic_ai import Agent
from agent_project_template.core.llm_registry import get_default_model

# Create your agent
your_agent = Agent(
    model=get_default_model(),
    system_prompt="You are a helpful assistant..."
)

async def handle_your_agent(user_input: str) -> str:
    result = await your_agent.run(user_input)
    return result.data
```

2. **Register your agent** in `agents/__init__.py`

3. **Add API endpoints** in `api/v1/endpoints/` (optional)

4. **Update main.py** to include your agent in CLI mode

## 📚 Documentation

- [Template Usage Guide](docs/TEMPLATE_GUIDE.md) - Detailed guide for using this template
- [Architecture Guide](docs/ARCHITECTURE.md) - Module hierarchy and import guidelines
- [API Documentation](http://localhost:8080/docs) - Interactive API docs (when running in API mode)

## 🚀 Deployment

### Docker
```bash
docker build -t your-agent-app .
docker run -p 8080:8080 your-agent-app
```

### Environment Variables
Set these in production:
- `AI__OPENAI_API_KEY`: OpenAI API key
- `AI__ANTHROPIC_API_KEY`: Anthropic API key
- `DATABASE__URL`: PostgreSQL connection string
- `REDIS__URL`: Redis connection string

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details.

## 🆘 Support

- Check the [Template Usage Guide](docs/TEMPLATE_GUIDE.md)
- Review the example demo agent implementation
- Open an issue for bugs or feature requests

---

**Ready to build your AI agent?** Start by exploring the demo agent and customizing it for your use case!