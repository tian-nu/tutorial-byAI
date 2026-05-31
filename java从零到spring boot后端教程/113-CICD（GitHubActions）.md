# 113-CICD（GitHub Actions）

> 💡 每次改完代码，你手动执行：`mvn clean package` → `docker build` → `docker tag` → `docker push` → SSH 到服务器 → `docker pull` → `docker compose up -d`。人不是机器，总会漏步骤。GitHub Actions 能让你 `git push` 之后，以上操作全自动执行——这就是 CI/CD（持续集成/持续部署）。

---

## 本章目标
- 理解 CI/CD 的概念
- 创建一个 GitHub Actions 工作流
- 实现 push 代码后自动测试和构建 Docker 镜像
- 推送到 Docker Hub 并自动部署到服务器

---

## 113.1 CI/CD 是什么

| 缩写 | 全称 | 含义 |
|------|------|------|
| CI | Continuous Integration（持续集成） | 代码合并后自动构建、测试 |
| CD | Continuous Delivery/Deployment（持续交付/部署） | 测试通过后自动发布/部署 |

### 一个完整的 CI/CD 流水线

```
你 push 代码
    ↓
GitHub Actions 触发
    ↓
1. 拉取代码
2. 设置 JDK 21
3. mvn test（单元测试）
4. mvn package（打包）
5. docker build（构建镜像）
6. docker push（推送到镜像仓库）
7. SSH 到服务器 → docker pull → docker compose up -d（部署）
```

---

## 113.2 第一个 GitHub Actions 工作流

### 创建文件

在项目根目录创建 `.github/workflows/ci.yml`：

```yaml
name: Java CI with Maven

on:
  push:
    branches: [ main, dev ]
  pull_request:
    branches: [ main ]

jobs:
  build-and-test:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up JDK 21
        uses: actions/setup-java@v4
        with:
          java-version: '21'
          distribution: 'temurin'
          cache: maven

      - name: Run tests
        run: mvn test --no-transfer-progress

      - name: Build package
        run: mvn package -DskipTests --no-transfer-progress

      - name: Upload artifact
        uses: actions/upload-artifact@v4
        with:
          name: app-jar
          path: target/*.jar
```

### 工作流解释

| 字段 | 含义 |
|------|------|
| `name` | 工作流名称，显示在 GitHub Actions 页面 |
| `on.push.branches` | 当 push 到 main/dev 分支时触发 |
| `on.pull_request` | 当创建 PR 到 main 时触发 |
| `runs-on` | 运行环境（GitHub 提供的虚拟机） |
| `steps` | 要执行的步骤列表 |
| `uses` | 使用别人写好的 Action（复用逻辑） |
| `--no-transfer-progress` | 减少 Maven 的日志输出 |

### 验证方法

1. 把 `.github/workflows/ci.yml` 提交并 push 到 GitHub
2. 打开 GitHub 仓库页面 → Actions 标签
3. 应该看到工作流正在运行
4. 全部绿色 ✅ 即成功

---

## 113.3 构建并推送 Docker 镜像

### 准备工作：Docker Hub Access Token

1. 登录 [hub.docker.com](https://hub.docker.com) → Account Settings → Security
2. 点击 **New Access Token**，起名 `github-actions`，复制 token
3. 在 GitHub 仓库 → Settings → Secrets and variables → Actions → **New repository secret**：
   - `DOCKER_USERNAME` = 你的 Docker Hub 用户名
   - `DOCKER_PASSWORD` = 刚才复制的 token

### 完整工作流

`.github/workflows/docker-build-push.yml`：

```yaml
name: Docker Build and Push

on:
  push:
    tags:
      - 'v*'

jobs:
  docker:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up JDK 21
        uses: actions/setup-java@v4
        with:
          java-version: '21'
          distribution: 'temurin'
          cache: maven

      - name: Build JAR
        run: mvn clean package -DskipTests --no-transfer-progress

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Login to Docker Hub
        uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKER_USERNAME }}
          password: ${{ secrets.DOCKER_PASSWORD }}

      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ${{ secrets.DOCKER_USERNAME }}/myapp
          tags: |
            type=semver,pattern={{version}}
            type=sha

      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
```

> 💡 这个工作流只在 push `v*` 标签（如 `v1.0.0`）时触发，日常开发 push 不会构建 Docker 镜像。

---

## 113.4 自动部署到服务器

### 准备工作

在 GitHub Secrets 中添加：
- `SERVER_HOST` = 你的服务器 IP
- `SERVER_USER` = SSH 用户名
- `SERVER_SSH_KEY` = 你的 SSH 私钥（**不是公钥**，完整内容含 `-----BEGIN...`）

### 部署工作流

`.github/workflows/deploy.yml`：

```yaml
name: Deploy to Server

on:
  workflow_run:
    workflows: ["Docker Build and Push"]
    types:
      - completed

jobs:
  deploy:
    if: ${{ github.event.workflow_run.conclusion == 'success' }}
    runs-on: ubuntu-latest

    steps:
      - name: Deploy via SSH
        uses: appleboy/ssh-action@v1.0.3
        with:
          host: ${{ secrets.SERVER_HOST }}
          username: ${{ secrets.SERVER_USER }}
          key: ${{ secrets.SERVER_SSH_KEY }}
          script: |
            cd /opt/myapp
            docker compose pull
            docker compose up -d --remove-orphans
            docker image prune -f
```

### 解释

| 步骤 | 含义 |
|------|------|
| `workflow_run` | 等 Docker Build and Push 完成后再执行 |
| `if: success()` | 只有 upstream 工作流成功才执行 |
| `docker compose pull` | 拉取最新的镜像 |
| `docker compose up -d` | 重新创建容器（用新镜像） |
| `--remove-orphans` | 删除 compose 文件中不再存在的服务容器 |
| `docker image prune -f` | 清理无用的旧镜像 |

---

## 113.5 完整流水线总览

```
┌─────────────────────────────────────────────────────┐
│ 你执行：git tag v1.0.0 && git push --tags            │
└────────────────────┬────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────┐
│ Job 1: Docker Build and Push                        │
│   ├── Checkout code                                 │
│   ├── Set up JDK 21                                 │
│   ├── mvn package                                   │
│   ├── docker build                                  │
│   └── docker push → Docker Hub                      │
└────────────────────┬────────────────────────────────┘
                     ↓ (success)
┌─────────────────────────────────────────────────────┐
│ Job 2: Deploy to Server                             │
│   ├── SSH 连接服务器                                 │
│   ├── docker compose pull                           │
│   ├── docker compose up -d                          │
│   └── 清理旧镜像                                     │
└─────────────────────────────────────────────────────┘
```

---

## 113.6 常见问题排查

### 工作流失败了，怎么看日志？

GitHub 仓库 → Actions → 点击失败的工作流 → 点击失败的 job → 展开失败的 step。

### Maven 构建太慢

在工作流中使用缓存：

```yaml
- name: Cache Maven packages
  uses: actions/cache@v4
  with:
    path: ~/.m2/repository
    key: ${{ runner.os }}-maven-${{ hashFiles('**/pom.xml') }}
```

或者用 `actions/setup-java@v4` 自带的 `cache: maven`（推荐）。

### SSH 连接失败

- 确认 `SERVER_SSH_KEY` 是私钥的完整内容（包括换行符）
- 确认服务器上 `~/.ssh/authorized_keys` 包含对应的公钥
- 服务器的 22 端口是否被防火墙屏蔽

---

## 113.7 完成效果

学完本章，你应该能：
1. 为你的 GitHub 仓库创建 CI 工作流（自动测试 + 打包）
2. 配置 Docker Hub Token 作为 GitHub Secret
3. 实现 tag push 自动构建并推送 Docker 镜像
4. 实现新镜像自动部署到服务器

---

## 小结

| 知识点 | 核心内容 |
|--------|----------|
| CI/CD 概念 | CI=自动构建测试，CD=自动发布部署 |
| 工作流文件 | `.github/workflows/xxx.yml` |
| 触发条件 | `on: push/pull_request/workflow_run` |
| 运行环境 | `runs-on: ubuntu-latest` |
| 敏感信息 | GitHub Secrets（`${{ secrets.XXX }}`） |
| Java 环境 | `actions/setup-java@v4` |
| Docker 构建 | `docker/build-push-action@v5` |
| SSH 部署 | `appleboy/ssh-action` |

---

## 自测题

1. 你想让工作流在 push 到任意分支时都触发，`on` 字段怎么写？
2. GitHub Secrets 中的值在工作流日志中会被打印出来吗？为什么？
3. `workflow_run` 和 `workflow_dispatch` 有什么区别？

<details>
<summary>点击查看答案</summary>

1. 
```yaml
on:
  push:
    branches: [ '*' ]
```
或者直接用 `on: push`（不限制分支）。

2. 不会。GitHub 自动屏蔽 Secrets 的值，即使 `echo ${{ secrets.XXX }}` 在日志中也显示为 `***`。

3. `workflow_run` 是当另一个工作流完成时自动触发；`workflow_dispatch` 是手动在 GitHub 页面上点击按钮触发。
</details>