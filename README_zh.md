# AI Agent 项目模板

基于 Pydantic-AI + FastAPI 构建的生产就绪 AI agent 应用模板。提供结构化日志、错误处理、配置管理和 Docker 支持的清洁基础架构。

> 📖 **English Documentation**: [README.md](README.md)

## 特性

- 🤖 **AI Agent 框架**: 基于 Pydantic-AI 构建的强大 agent 开发框架
- 🚀 **FastAPI 集成**: 带自动文档的 RESTful API 端点
- ⚡ **快速依赖管理**: 使用 uv 进行闪电般快速的包管理
- 📝 **结构化日志**: 集成 Logfire 的全面日志记录
- 🔧 **配置管理**: 基于环境变量的配置，使用 Pydantic Settings
- 🐳 **Docker 支持**: 开箱即用的 Docker 配置
- 🧪 **测试框架**: 预配置的 pytest 设置，支持异步测试
- 📚 **文档**: 全面的文档和示例
- 🛠️ **开发工具**: 包含常用开发命令的 Makefile
- 🌐 **双语支持**: 英文和中文文档

## 快速开始

### 环境要求

- Python 3.11+
- [cookiecutter](https://cookiecutter.readthedocs.io/)
- [uv](https://docs.astral.sh/uv/) (推荐用于快速依赖管理)

### 安装 cookiecutter

```bash
# 使用 pip
pip install cookiecutter

# 使用 uv
uv tool install cookiecutter

# 使用 conda
conda install cookiecutter

# 使用 homebrew (macOS)
brew install cookiecutter
```

### 创建新项目

1. **从模板生成项目:**
```bash
cookiecutter gh:coco-xyz/agent-project-template
```

2. **回答提示问题:**
```
project_name [My Awesome Project]: 您的 AI Agent 项目
project_slug [your_ai_agent_project]: your-project-name
```

3. **进入新项目目录:**
```bash
cd your-project-name
```

4. **设置项目:**
```bash
# 如果还没有安装 uv
pip install uv

# 完整项目设置（安装依赖、创建 .env 等）
make setup
```

5. **开始开发:**
```bash
# CLI 模式运行
make run-cli

# 或运行 API 服务器
make run-api
```

## 模板配置

模板在 `cookiecutter.json` 中使用以下变量：

| 变量 | 描述 | 默认值 |
|------|------|--------|
| `project_name` | 人类可读的项目名称 | "My Awesome Project" |
| `project_slug` | Python 包名（snake_case） | "my_awesome_project" |

## 项目结构

生成后，您的项目将具有以下结构：

```
your-project-name/
├── src/                     # 主要源代码
│   ├── core/                # 核心模块（配置、日志、LLM 等）
│   ├── agents/              # AI Agent 实现
│   ├── api/                 # FastAPI 路由和端点
│   │   ├── errors/          # 错误处理
│   │   ├── schemas/         # API 模式定义
│   │   └── v1/              # API 版本 1 端点
│   ├── models/              # 数据模型
│   ├── services/            # 业务逻辑服务
│   ├── stores/              # 数据库和缓存存储
│   ├── prompts/             # AI 提示词和模板
│   └── utils/               # 工具函数
├── tests/                   # 测试文件
├── docs/                    # 文档
├── logs/                    # 日志文件（运行时创建）
├── migrations/              # 数据库迁移
├── initdb/                  # 数据库初始化脚本
├── main.py                  # 应用入口点
├── pyproject.toml           # 项目配置
├── uv.lock                  # 依赖锁定文件
├── env.sample               # 环境变量模板
├── docker-compose.yml       # Docker compose 配置
├── docker-compose.middleware.yml  # 仅中间件服务
├── Dockerfile               # Docker 配置
├── Makefile                 # 开发命令
├── README.md                # 英文文档
└── README_zh.md             # 中文文档
```

## 包含内容

### 核心组件

- **Agent 框架**: 构建 AI agents 的基础类
- **API 层**: 带健康检查和 agent 端点的 FastAPI 应用
- **配置**: 基于环境的设置与验证
- **日志**: 集成 Logfire 的结构化日志
- **错误处理**: 全面的错误处理和验证

### 开发工具

- **Makefile**: 常用开发命令（`make help` 查看全部）
- **测试**: 支持异步和覆盖率的 pytest
- **代码质量**: 预配置的 black、isort、flake8、mypy
- **Docker**: 用于生产部署的多阶段 Dockerfile

### 依赖项

- **pydantic-ai**: 现代 AI agent 框架
- **FastAPI**: 高性能 web 框架
- **Logfire**: 高级日志和可观测性
- **Pydantic**: 数据验证和设置管理
- **uvicorn**: 生产用 ASGI 服务器

## 使用示例

### CLI 模式
```bash
# 交互式 CLI
make run-cli

# 直接命令
uv run python main.py --mode cli
```

### API 模式
```bash
# 启动 API 服务器
make run-api

# 开发模式（热重载）
make run-api-dev

# 访问交互式文档：http://localhost:8080/docs
```

### 开发命令
```bash
# 查看所有可用命令
make help

# 运行测试
make test

# 格式化代码
make format

# 类型检查
make type-check

# 构建 Docker 镜像
make docker-build
```

## 自定义

生成项目后，您可以自定义：

1. **Agent 逻辑**: 在 `src/agents/` 中实现您的 AI agents
2. **API 端点**: 在 `src/api/` 中添加路由
3. **配置**: 修改 `src/core/config.py` 中的设置
4. **依赖**: 更新 `pyproject.toml` 并运行 `uv sync`

## 贡献

欢迎贡献来改进这个模板！请：

1. Fork 仓库
2. 创建功能分支
3. 进行更改
4. 如适用，添加测试
5. 提交 pull request

## 许可证

此模板在 MIT 许可证下发布。从此模板生成的项目可以使用您选择的任何许可证。

## 支持

- 📖 **文档**: 查看生成项目的 README 文件
- 🐛 **问题**: 在 GitHub 上报告错误或请求功能
- 💬 **讨论**: 加入社区讨论

---

**祝您编码愉快！🚀**
