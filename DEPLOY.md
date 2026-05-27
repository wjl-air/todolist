# Todolist 项目上线方案

> Vue3 + FastAPI + MySQL | Docker 容器化部署 | GitHub Actions CI/CD

---

## 一、项目概述

| 层级 | 技术栈 | 开发端口 | 生产运行方式 |
|------|--------|----------|-------------|
| 前端 | Vue 3 + Vite 5 | 5173 | nginx:alpine 静态服务 |
| 后端 | FastAPI + uvicorn | 8000 | python:3.12-slim 容器 |
| 数据库 | MySQL 8.0 | 3306 | mysql:8.0 容器 + 持久化卷 |

生产环境通过 **nginx 反向代理**统一入口，用户在浏览器访问 `http://<服务器IP>` 即可，前端 `/api/*` 请求由 nginx 转发到后端，无需跨域处理。

---

## 二、生产架构

```
┌───────────────────────────────────────────────────────┐
│                    Ubuntu Server                       │
│                                                       │
│  ┌─────────────────────────────────────────────────┐  │
│  │  nginx (frontend 容器)                  端口:80  │  │
│  │  ├─ /          → 前端静态文件                   │  │
│  │  └─ /api/*     → proxy_pass 后端:8000           │  │
│  └───────────────┬─────────────────────────────────┘  │
│                  │                                     │
│  ┌───────────────▼─────────────────────────────────┐  │
│  │  backend 容器                             :8000  │  │
│  │  FastAPI + uvicorn                              │  │
│  │  DB_HOST → mysql                                │  │
│  └───────────────┬─────────────────────────────────┘  │
│                  │                                     │
│  ┌───────────────▼─────────────────────────────────┐  │
│  │  mysql 容器                               :3306  │  │
│  │  数据库: 1111                                   │  │
│  │  数据卷: mysql_data (持久化)                    │  │
│  └─────────────────────────────────────────────────┘  │
│                                                       │
└───────────────────────────────────────────────────────┘
```

---

## 三、代码改造清单

### 3.1 前端 `src/App.vue`

将硬编码的 API 地址改为相对路径，生产环境由 nginx 代理：

```diff
- const API = 'http://localhost:8000/api/todos'
+ const API = '/api/todos'
```

### 3.2 后端 `backend/main.py`

数据库配置改为读取环境变量，CORS 可移除（nginx 同源代理）：

```diff
- DB_CONFIG = {
-     'host': 'localhost',
-     'user': 'root',
-     'password': 'root',
-     'database': '1111',
-     ...
- }
+ DB_CONFIG = {
+     'host': os.environ.get('DB_HOST', 'localhost'),
+     'user': os.environ.get('DB_USER', 'root'),
+     'password': os.environ.get('DB_PASSWORD', 'root'),
+     'database': os.environ.get('DB_NAME', '1111'),
+     ...
+ }
```

### 3.3 新建 `backend/requirements.txt`

```
fastapi>=0.100.0
uvicorn>=0.23.0
pymysql>=1.1.0
pydantic>=2.0.0
```

---

## 四、新增部署文件

### 4.1 文件清单

```
D:\fast api\
├── Dockerfile.backend           # 后端镜像构建文件
├── Dockerfile.frontend          # 前端多阶段构建文件
├── docker-compose.yml           # 服务编排
├── .env.example                 # 环境变量模板
├── docker/
│   ├── nginx/
│   │   └── default.conf         # nginx 配置
│   └── mysql/
│       └── init.sql             # 数据库建表脚本
└── .github/
    └── workflows/
        └── deploy.yml           # CI/CD 流水线
```

### 4.2 `Dockerfile.backend`

```dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ .

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 4.3 `Dockerfile.frontend`

多阶段构建：第一阶段用 Node 编译 Vue 项目，第二阶段用 nginx 提供服务。

```dockerfile
# 阶段一：构建
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# 阶段二：运行
FROM nginx:alpine
COPY docker/nginx/default.conf /etc/nginx/conf.d/default.conf
COPY --from=builder /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### 4.4 `docker/nginx/default.conf`

```nginx
server {
    listen 80;
    server_name _;

    root /usr/share/nginx/html;
    index index.html;

    # 前端 SPA 路由回退
    location / {
        try_files $uri $uri/ /index.html;
    }

    # API 反向代理到后端
    location /api/ {
        proxy_pass http://backend:8000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 4.5 `docker/mysql/init.sql`

MySQL 容器启动时自动执行建表：

```sql
CREATE DATABASE IF NOT EXISTS `1111` DEFAULT CHARACTER SET utf8mb4;

USE `1111`;

CREATE TABLE IF NOT EXISTS todos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    completed TINYINT(1) DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### 4.6 `docker-compose.yml`

```yaml
version: "3.8"

services:
  mysql:
    image: mysql:8.0
    container_name: todolist-mysql
    restart: always
    environment:
      MYSQL_ROOT_PASSWORD: ${DB_ROOT_PASSWORD}
      MYSQL_DATABASE: "1111"
    volumes:
      - ./docker/mysql/init.sql:/docker-entrypoint-initdb.d/init.sql
      - mysql_data:/var/lib/mysql
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
      interval: 10s
      timeout: 5s
      retries: 5

  backend:
    image: ghcr.io/<你的GitHub用户名>/todolist-backend:latest
    container_name: todolist-backend
    restart: always
    depends_on:
      mysql:
        condition: service_healthy
    environment:
      DB_HOST: mysql
      DB_USER: root
      DB_PASSWORD: ${DB_ROOT_PASSWORD}
      DB_NAME: "1111"
    ports:
      - "127.0.0.1:8000:8000"

  frontend:
    image: ghcr.io/<你的GitHub用户名>/todolist-frontend:latest
    container_name: todolist-frontend
    restart: always
    depends_on:
      - backend
    ports:
      - "80:80"

volumes:
  mysql_data:
```

### 4.7 `.env.example`

```env
DB_ROOT_PASSWORD=your_secure_password_here
```

服务器上复制为 `.env` 并填入实际密码：

```bash
cp .env.example .env
# 编辑 .env 填入真实密码
```

---

## 五、GitHub Actions CI/CD

### 5.1 流水线文件 `.github/workflows/deploy.yml`

```yaml
name: Deploy to Ubuntu

on:
  push:
    branches: [main]

env:
  REGISTRY: ghcr.io
  BACKEND_IMAGE: ghcr.io/${{ github.repository_owner }}/todolist-backend
  FRONTEND_IMAGE: ghcr.io/${{ github.repository_owner }}/todolist-frontend

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Log in to GitHub Container Registry
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Build & Push Backend
        uses: docker/build-push-action@v5
        with:
          context: .
          file: Dockerfile.backend
          push: true
          tags: ${{ env.BACKEND_IMAGE }}:latest

      - name: Build & Push Frontend
        uses: docker/build-push-action@v5
        with:
          context: .
          file: Dockerfile.frontend
          push: true
          tags: ${{ env.FRONTEND_IMAGE }}:latest

      - name: Deploy to Server
        uses: appleboy/ssh-action@v1
        with:
          host: ${{ secrets.SSH_HOST }}
          username: ${{ secrets.SSH_USER }}
          key: ${{ secrets.SSH_PRIVATE_KEY }}
          script: |
            cd /opt/todolist
            docker compose pull
            docker compose up -d --remove-orphans
            docker image prune -f
```

### 5.2 流水线执行流程

```
Git Push (main)
    │
    ▼
GitHub Actions 触发
    │
    ├─ ① Checkout 代码
    ├─ ② 登录 GHCR (GitHub Container Registry)
    ├─ ③ Docker Build → 后端镜像 → Push to GHCR
    ├─ ④ Docker Build → 前端镜像 → Push to GHCR
    └─ ⑤ SSH 到 Ubuntu 服务器
         ├─ docker compose pull        # 拉取新镜像
         ├─ docker compose up -d       # 重启服务
         └─ docker image prune -f      # 清理旧镜像
```

---

## 六、GitHub Secrets 配置

在 GitHub 仓库 `Settings → Secrets and variables → Actions` 中添加：

| Secret Name | 值 | 说明 |
|-------------|-----|------|
| `SSH_HOST` | `123.45.67.89` | Ubuntu 服务器公网 IP |
| `SSH_USER` | `root` | SSH 登录用户名 |
| `SSH_PRIVATE_KEY` | `-----BEGIN OPENSSH PRIVATE KEY-----...` | SSH 私钥（完整内容） |
| `DB_ROOT_PASSWORD` | 你的密码 | MySQL root 密码（与服务器 `.env` 一致） |

> **注意**：`GITHUB_TOKEN` 是 GitHub Actions 自动提供的，无需手动配置。

---

## 七、服务器初始化（首次部署前手动执行一次）

```bash
# 1. 创建项目目录
mkdir -p /opt/todolist
cd /opt/todolist

# 2. 上传 docker-compose.yml 和 .env 文件
#    可以通过 scp 或 git clone 上传
scp docker-compose.yml root@<服务器IP>:/opt/todolist/
scp .env root@<服务器IP>:/opt/todolist/

# 3. 创建 SQL 初始化目录并上传
mkdir -p docker/mysql
scp docker/mysql/init.sql root@<服务器IP>:/opt/todolist/docker/mysql/

# 4. 确保 GHCR 登录权限（如果是私有仓库）
docker login ghcr.io -u <GitHub用户名> -p <Personal Access Token>

# 5. 首次启动（会拉取镜像并创建容器）
docker compose up -d

# 6. 检查状态
docker compose ps
```

---

## 八、常用运维命令

```bash
cd /opt/todolist

# 查看所有容器状态
docker compose ps

# 查看日志
docker compose logs -f backend
docker compose logs -f frontend

# 重启服务
docker compose restart

# 停止所有服务
docker compose down

# 重新构建并启动（本地调试用）
docker compose up -d --build

# 进入后端容器
docker exec -it todolist-backend bash
```

---

## 九、部署检查清单

- [ ] 代码改造完成（API 路径、环境变量）
- [ ] `Dockerfile.backend` 和 `Dockerfile.frontend` 已创建
- [ ] `docker-compose.yml` 中替换了实际的 GitHub 用户名
- [ ] `.env` 文件已配置密码（服务器上）
- [ ] GitHub 仓库已设置 4 个 Secrets
- [ ] GitHub Actions 权限中 `Packages` 为 `Write`
- [ ] Ubuntu 服务器已安装 Docker + Docker Compose
- [ ] 服务器防火墙开放端口 80（HTTP）
- [ ] 首次手动部署验证通过
- [ ] Push 代码到 main 分支触发自动部署成功

---

## 十、技术要点说明

| 问题 | 方案 |
|------|------|
| 前端如何访问后端？ | nginx 代理 `/api/*` 到 `http://backend:8000`，同源无跨域 |
| 数据库密码如何管理？ | 不提交到 Git，通过 `.env` + Docker Secrets 注入 |
| 数据库数据如何持久化？ | `mysql_data` 命名卷挂载 `/var/lib/mysql` |
| 前端 SPA 路由怎么办？ | nginx `try_files $uri /index.html` 回退到入口 |
| 如何回滚？ | GitHub 上 revert commit，Actions 自动重新部署 |
| 镜像拉取失败？ | 私有仓库需配置 `docker login ghcr.io`，或仓库设为公开 |
