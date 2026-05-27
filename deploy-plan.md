# 部署方案：Docker + GitHub Actions → Ubuntu 服务器

## Context

项目当前只能在本地运行（硬编码 localhost），需要实现 DEPLOY.md 中描述的完整部署方案：代码改造 + Docker 容器化 + GitHub Actions CI/CD 自动部署到 Ubuntu 服务器。

---

## Step 1: 代码改造（让代码能在容器中运行）

### 1.1 前端 API 地址改相对路径
- 文件：`src/App.vue:31`
- 改：`const API = 'http://localhost:8000/api/todos'` → `const API = '/api/todos'`
- 生产环境由 nginx 同源代理，开发环境 Vite dev server 可配 proxy（如果需要）

### 1.2 后端数据库配置读环境变量
- 文件：`backend/main.py:18-25` 和 `backend/database.py:3-10`
- 添加 `import os`，将硬编码的 DB_CONFIG 改为 `os.environ.get(...)` 读取环境变量
- 保留本地默认值，确保本地开发不受影响

### 1.3 新建 `backend/requirements.txt`
```
fastapi>=0.100.0
uvicorn>=0.23.0
pymysql>=1.1.0
pydantic>=2.0.0
```

---

## Step 2: Docker 容器化文件

### 2.1 `Dockerfile.backend`
- 基于 `python:3.12-slim`
- 安装 requirements.txt，复制 backend 代码
- CMD 启动 uvicorn

### 2.2 `Dockerfile.frontend`（多阶段构建）
- 阶段一：`node:20-alpine` 构建 Vue 项目 → `npm run build`
- 阶段二：`nginx:alpine` 提供静态文件服务

### 2.3 `docker/nginx/default.conf`
- `/` → 前端静态文件（含 SPA fallback）
- `/api/` → proxy_pass 到 `http://backend:8000`

### 2.4 `docker/mysql/init.sql`
- 自动创建数据库 `1111` 和 `todos` 表（与 init_db.py 逻辑一致）

### 2.5 `docker-compose.yml`
- 三个服务：mysql、backend、frontend
- mysql 使用命名卷持久化数据
- backend 等待 mysql healthy 后启动
- frontend 暴露 80 端口

### 2.6 `.env.example`
- 模板：`DB_ROOT_PASSWORD=your_secure_password_here`

---

## Step 3: GitHub Actions CI/CD

### 3.1 `.github/workflows/deploy.yml`
- 触发条件：push 到 main 分支
- 步骤：Checkout → GHCR 登录 → 构建并推送前后端镜像 → SSH 到服务器执行 `docker compose pull && up -d`
- 镜像托管：GitHub Container Registry (ghcr.io)

---

## Step 4: 本地验证

1. `docker compose build` 确认镜像能构建
2. `docker compose up -d` 启动三个容器
3. 浏览器访问 `http://localhost` 验证完整 CRUD 功能

---

## Step 5: Git 初始化 + GitHub 推送

1. `git init` + `.gitignore`（排除 node_modules、.env、dist、__pycache__）
2. 在 GitHub 创建仓库
3. 添加 remote + push 到 main

---

## Step 6: 服务器部署配置

1. Ubuntu 服务器安装 Docker + Docker Compose（如未安装）
2. 创建 `/opt/todolist` 目录，上传 `docker-compose.yml` + `.env`
3. 上传 `docker/mysql/init.sql`（首次启动建表用）
4. 配置 GitHub Secrets：`SSH_HOST`、`SSH_USER`、`SSH_PRIVATE_KEY`、`DB_ROOT_PASSWORD`
5. Push 代码触发自动部署

---

## 涉及的文件清单

| 操作 | 文件 |
|------|------|
| 修改 | `src/App.vue` (API 地址) |
| 修改 | `backend/main.py` (DB 配置) |
| 修改 | `backend/database.py` (DB 配置) |
| 新建 | `backend/requirements.txt` |
| 新建 | `Dockerfile.backend` |
| 新建 | `Dockerfile.frontend` |
| 新建 | `docker/nginx/default.conf` |
| 新建 | `docker/mysql/init.sql` |
| 新建 | `docker-compose.yml` |
| 新建 | `.env.example` |
| 新建 | `.gitignore` |
| 新建 | `.github/workflows/deploy.yml` |

## 验证方式

1. 本地 `docker compose up -d` 后访问 `http://localhost`，测试增删改查 + 切换完成状态
2. 检查 `docker compose ps` 三个容器均 healthy
3. Push 到 GitHub 后确认 Actions workflow 运行成功（构建 + 推送镜像）
4. 服务器上确认服务正常运行
