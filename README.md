# Agent Project Template

A clean and practical AI Agent project template built with Pydantic-AI + FastAPI. Ready-to-use configuration, structured logging, error handling, and Docker support for quickly building production-ready Agent services or CLI tools.

## Prerequisites (Environment Setup)
- Operating System: macOS / Linux / Windows (with make installed)
- Python: 3.11 (recommended fixed version)
- Package Manager: uv (recommended)
- Optional Dependencies: Docker, PostgreSQL, Redis

> If using uv: `pip install uv`, then run `uv sync` once in the project root to install dependencies.

## Quick Start
1) Clone the repository and enter the directory
```bash
git clone <your-repo-url>
cd agent-project-template
```
2) Initialize the project (creates .env, basic directories, and test skeleton)
```bash
make setup
```
3) Start running
- CLI mode:
```bash
make run-cli
```
- API mode:
```bash
make run-api
```
In API mode, the service runs on `http://localhost:8080` by default, with interactive documentation at `/docs`.

> For development with hot reload: `make run-api-dev`

## Configuration
- Copy `env.sample` to `.env` and fill in API keys, database, cache, and other configurations as needed.
- Validate configuration:
```bash
make config-check
```

## Common Commands (via Makefile)
- View all commands and categorized help: `make help`
- Run CLI: `make run-cli`
- Run API: `make run-api` (or hot reload `make run-api-dev`)
- Run tests: `make test` (or verbose mode `make test-verbose`)
- Code quality: `make format`, `make lint`, `make type-check`
- Docker: `make docker-build`, `make docker-run`
- Others: `make clean`, `make clean-logs`, `make version`

## Documentation
- Architecture & Conventions: `docs/ARCHITECTURE.md`
- See `docs/` directory for more documentation (can be supplemented with project-specific guides)

## Docker Quick Usage (Optional)
```bash
make docker-build
make docker-run
```

## Contributing & License
- Welcome to submit Issues / PRs to improve the template together
- License: MIT (see LICENSE file in repository)