# {{cookiecutter.project_name}}

基于 Pydantic-AI + FastAPI 构建的简洁实用的 AI Agent 项目。提供开箱即用的配置、结构化日志、错误处理和 Docker 支持，帮助您快速构建生产就绪的 Agent 服务或 CLI 工具。

> 📖 **English Documentation**: [README.md](README.md)

## 环境要求

- 操作系统：macOS / Linux / Windows（需安装 make）
- Python：3.11（必需 - 本项目使用固定的 Python 版本）
- **包管理器：uv（必需）** - 本项目使用 uv 进行快速依赖管理
- 可选依赖：Docker、PostgreSQL、Redis

### 安装 uv（必需）

本项目使用 uv 作为包管理器，请先安装：

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# 备选方案：通过 pip 安装
pip install uv
```

## 快速开始

1) 克隆仓库并进入目录
```bash
git clone <your-repo-url>
cd {{cookiecutter.project_slug}}
```

2) 完整项目设置（安装依赖、创建 .env 文件、目录和测试框架）
```bash
make setup
```

3) 开始运行
- CLI 模式：
```bash
make run-cli
```
- API 模式：
```bash
make run-api
```
API 模式下，服务默认运行在 `http://localhost:8080`，交互式文档位于 `/docs`。

> 开发模式（热重载）：`make run-api-dev`

## 配置

- 将 `env.sample` 复制为 `.env` 并根据需要填写 API 密钥、数据库、缓存等配置
- 验证配置：
```bash
make config-check
```

## 常用命令（通过 Makefile）

- 查看所有命令和分类帮助：`make help`
- 项目设置：`make setup`（使用 uv 安装依赖，创建 .env 文件和目录）
- 运行 CLI：`make run-cli`
- 运行 API：`make run-api`（或热重载模式 `make run-api-dev`）
- 运行测试：`make test`（或详细模式 `make test-verbose`）
- 代码质量：`make format`、`make lint`、`make type-check`
- Docker：`make docker-build`、`make docker-run`
- 其他：`make clean`、`make clean-logs`、`make version`

> **注意**：所有 Python 命令在 uv 可用时会自动使用 `uv run`，确保依赖管理的一致性。

## 项目结构

```
{{cookiecutter.project_slug}}/
├── src/                     # 主要源代码目录
│   ├── core/                # 核心模块（配置、日志等）
│   ├── agents/              # AI Agent 实现
│   ├── api/                 # FastAPI 路由和端点
│   ├── models/              # 数据模型
│   └── utils/               # 工具函数
├── tests/                   # 测试文件
├── docs/                    # 项目文档
├── logs/                    # 日志文件目录
├── main.py                  # 应用入口点
├── pyproject.toml           # 项目配置和依赖
├── uv.lock                  # uv 锁定文件
├── env.sample               # 环境变量模板
└── Makefile                 # 开发命令
```

## 文档

- 架构与约定：`docs/ARCHITECTURE.md`
- 更多文档请查看 `docs/` 目录（可根据项目需要补充特定指南）

## Docker 使用

### 开发环境（推荐）
仅启动中间件服务（PostgreSQL、Redis），在本地运行应用程序：
```bash
# 启动开发环境
make dev-start

# 在本地运行应用程序
make run-api
# 或者
make run-cli

# 停止开发环境
make dev-stop
```

### 生产环境模式
启动完整的应用程序栈，包括容器化的应用程序：
```bash
# 启动完整栈
make prod-start

# 停止完整栈
make prod-stop
```

### 单独的 Docker Compose 命令
```bash
# 启动/停止仅中间件（postgres、redis）
make compose-up-middleware
make compose-down-middleware

# 启动/停止完整应用程序栈
make compose-up
make compose-down

# 查看日志
make compose-logs
make compose-logs-middleware

# 检查服务状态
make compose-ps

# 构建应用程序镜像
make compose-build

# 清理所有资源
make compose-clean
```

### 传统 Docker 命令
```bash
make docker-build
make docker-run
```

## 贡献与许可证

- 欢迎提交 Issues / PRs 来共同改进这个模板
- 许可证：MIT（详见仓库中的 LICENSE 文件）
