# 36 — Docker 与 CI/CD：让代码自己跑到服务器上

> - 对应文档版本：Docker精通教程 outline v1
> - 适用环境：GitHub 账号、Docker Hub 账号、一台可 SSH 访问的服务器
> - 读者角色：已掌握 Dockerfile 和 Compose，需要搭建自动化部署管道的开发者
> - 预计耗时：新手 45 分钟 / 熟手 20 分钟
> - 前置教程：第 10～14 章（Dockerfile 系列）、第 22 章（多容器编排）、第 35 章（安全基础）
> - 可视化：无

---

## 我在做什么？

你写完代码，本地测试通过，然后要部署到服务器。步骤是：手动 `docker build`，手动 `docker tag`，手动 `docker push`，SSH 到服务器，手动 `docker compose pull && docker compose up -d`。一次部署 5 分钟，一天部署 5 次，一周就花掉 2 小时。而且每次手动操作，都可能在某个步骤出错——标签打错了、忘了 push、服务器上旧的镜像没清理。

这一章教你用 CI/CD *此术语见附录C* 把整个流程自动化。你只需要 `git push`，剩下的——构建镜像、推送到仓库、部署到服务器——全部由 GitHub Actions 自动完成。代码推上去，喝杯咖啡，代码已经在服务器上跑了。

学完这一章，你能：
- 理解 CI/CD 中 Docker 的角色：构建 → 推送 → 部署
- 用 GitHub Actions 自动构建 Docker 镜像并推送到 Docker Hub
- 制定合理的镜像标签策略（git commit hash / 版本号）
- 在 CI 中使用 Docker 层缓存加速构建
- 配置服务器自动拉取最新镜像并重新部署

---

## 一、CI/CD 的基本流程

### 一张图看懂

```
你：git push
  │
  ▼
CI 服务器（GitHub Actions / GitLab CI / Jenkins）
  │
  ├── 1. 检出代码
  │     git clone
  │
  ├── 2. 运行测试
  │     npm test / pytest / go test
  │
  ├── 3. 构建 Docker 镜像
  │     docker build -t my-app:abc123 .
  │
  ├── 4. 推送到镜像仓库
  │     docker push my-app:abc123
  │
  └── 5. 触发部署
        SSH 到服务器
        docker compose pull
        docker compose up -d
  │
  ▼
服务器：新版本上线！
```

### 为什么用 Docker 做 CI/CD？

```
传统 CI/CD                            Docker CI/CD
┌──────────────────────┐             ┌──────────────────────┐
│ CI 环境要装 Node.js    │             │ CI 只需要 Docker       │
│ CI 环境要装 Python     │             │ 所有依赖在镜像里       │
│ CI 环境要装 Go         │             │ 构建产物就是镜像       │
│ 环境不一致 → 玄学问题  │             │ 环境完全一致          │
│ 部署要手动配环境       │             │ 部署只需要 docker run │
└──────────────────────┘             └──────────────────────┘
```

> **想多一点**：没有 Docker 的 CI/CD 就像一个接力赛，每个选手（CI 环境、测试环境、生产环境）用的跑道（操作系统、依赖版本、配置）都不一样。选手 A 的棒子（构建产物）递给选手 B，可能因为跑道不同而掉棒（环境不一致导致的 bug）。Docker 把跑道标准化了——每个选手跑在完全相同的跑道上，棒子（镜像）就是构建产物本身，不会因为环境不同而变形。

---

## 二、GitHub Actions 实战：自动构建 + 推送

### 准备：创建 Docker Hub Access Token

1. 登录 [Docker Hub](https://hub.docker.com/)
2. 右上角头像 → Account Settings → Security → New Access Token
3. 给 Token 起个名字（如 `github-actions`），权限选 "Read & Write"
4. 复制 Token 值（只显示一次！）

在 GitHub 仓库里添加 Secrets：

1. 仓库页面 → Settings → Secrets and variables → Actions → New repository secret
2. 添加两个 secret：
   - `DOCKERHUB_USERNAME`：你的 Docker Hub 用户名
   - `DOCKERHUB_TOKEN`：刚才复制的 Token

### 创建 GitHub Actions 工作流

在项目根目录创建 `.github/workflows/docker-build.yml`：

```yaml
# .github/workflows/docker-build.yml
name: Docker Build and Push

# 触发条件：推送到 main 分支时
on:
  push:
    branches:
      - main

# 环境变量
env:
  DOCKERHUB_USERNAME: ${{ secrets.DOCKERHUB_USERNAME }}
  IMAGE_NAME: my-app

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
      # 1. 检出代码
      - name: Checkout code
        uses: actions/checkout@v4

      # 2. 登录 Docker Hub
      - name: Log in to Docker Hub
        uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKERHUB_USERNAME }}
          password: ${{ secrets.DOCKERHUB_TOKEN }}

      # 3. 设置 Docker Buildx（用于构建和缓存）
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      # 4. 构建并推送镜像
      - name: Build and push
        uses: docker/build-push-action@v6
        with:
          context: .
          file: ./Dockerfile
          push: true
          # 标签策略：git commit hash + latest
          tags: |
            ${{ env.DOCKERHUB_USERNAME }}/${{ env.IMAGE_NAME }}:${{ github.sha }}
            ${{ env.DOCKERHUB_USERNAME }}/${{ env.IMAGE_NAME }}:latest
          # 缓存策略：利用 GitHub Actions 缓存
          cache-from: type=gha
          cache-to: type=gha,mode=max
```

### 逐段解释

```yaml
on:
  push:
    branches:
      - main
```
- 当有代码推送到 `main` 分支时自动触发

```yaml
docker/login-action@v3
  with:
    username: ${{ secrets.DOCKERHUB_USERNAME }}
    password: ${{ secrets.DOCKERHUB_TOKEN }}
```
- 用 GitHub Secrets 中存储的 Docker Hub 凭证登录。**永远不要把 Token 明文写在 YAML 里。**

```yaml
tags: |
  ${{ env.DOCKERHUB_USERNAME }}/${{ env.IMAGE_NAME }}:${{ github.sha }}
  ${{ env.DOCKERHUB_USERNAME }}/${{ env.IMAGE_NAME }}:latest
```
- 打两个标签：`<git commit hash>` 和 `latest`
- `github.sha` 是 GitHub Actions 的内置变量，等于当前 commit 的 SHA 值

```yaml
cache-from: type=gha
cache-to: type=gha,mode=max
```
- 用 GitHub Actions 自带的缓存机制，缓存 Docker 层。下次构建时，没变的层直接复用，构建速度大幅提升。

### 验证

```bash
# 推送代码到 main 分支
git add .
git commit -m "feat: add CI/CD pipeline"
git push origin main

# 去 GitHub 仓库的 Actions 页面
# 看到 workflow 正在运行或已完成
# 去 Docker Hub 查看，新镜像已经在上面了
```

---

## 三、标签策略：给镜像一个好名字

### 常见标签策略对比

| 策略 | 标签示例 | 优点 | 缺点 |
|------|---------|------|------|
| `latest` 只打一个 | `my-app:latest` | 简单 | 不知道是哪个版本，回滚困难 |
| git commit hash | `my-app:abc1234` | 精确对应代码，可回滚 | 不直观，不知道是哪个功能版本 |
| 语义化版本 | `my-app:1.2.3` | 可读，有版本语义 | 需要手动或自动打 tag |
| 分支名 | `my-app:main`、`my-app:dev` | 知道环境 | 同一分支多次构建相互覆盖 |
| 组合策略 | `my-app:1.2.3` + `my-app:abc1234` + `my-app:latest` | 信息完整 | 标签多，镜像仓库存储压力大 |

### 推荐的组合策略

```yaml
# 推送 git tag 时，用语义化版本
tags: |
  ${{ env.DOCKERHUB_USERNAME }}/${{ env.IMAGE_NAME }}:${{ github.ref_name }}
  ${{ env.DOCKERHUB_USERNAME }}/${{ env.IMAGE_NAME }}:${{ github.sha }}
  ${{ env.DOCKERHUB_USERNAME }}/${{ env.IMAGE_NAME }}:latest
```

触发条件：

```yaml
on:
  push:
    tags:
      - 'v*'    # 推送 v1.0.0、v2.1.3 等标签时触发
```

这样：
- `v1.2.3`：语义化版本，人能看懂
- `abc1234`：精确对应 git commit，万一出问题可以精确回滚
- `latest`：始终指向最新版本，方便快速部署

---

## 四、缓存优化：让 CI 构建飞起来

### 不用缓存的痛苦

```yaml
# ❌ 每次构建都从头开始，没有缓存
- name: Build
  run: docker build -t my-app .
```

每次 CI 构建，Docker 从零开始——下载基础镜像、`npm install`、`pip install`……即使只改了一行注释，也要等 5 分钟。

### 用 Buildx 缓存

```yaml
- name: Set up Docker Buildx
  uses: docker/setup-buildx-action@v3

- name: Build and push
  uses: docker/build-push-action@v6
  with:
    context: .
    push: true
    tags: |
      ${{ env.DOCKERHUB_USERNAME }}/${{ env.IMAGE_NAME }}:latest
    cache-from: type=gha           # 从 GitHub Actions 缓存读取
    cache-to: type=gha,mode=max    # 写入 GitHub Actions 缓存
```

缓存效果：

```
首次构建：5 分钟
  ├── 下载基础镜像：1 分钟
  ├── npm install：2 分钟
  └── 其他：2 分钟

第二次构建（只改了一行代码）：30 秒
  ├── 下载基础镜像：0 秒（缓存命中）
  ├── npm install：0 秒（缓存命中，package.json 没变）
  └── 其他：30 秒
```

### 缓存原理

```
Dockerfile 的每一层（RUN、COPY）都会生成一个缓存层。
如果这一层的输入（指令 + 文件）没变，Docker 直接复用缓存。

FROM node:20-alpine         ← 缓存：基础镜像层
WORKDIR /app                ← 缓存：指令没变
COPY package.json .         ← 缓存：package.json 没变
RUN npm ci                  ← 缓存：依赖没变
COPY . .                    ← ❌ 缓存失效：代码变了
RUN npm run build           ← ❌ 重新构建
CMD ["node", "server.js"]   ← 缓存：指令没变
```

所以要把**不常变的内容放在前面**：

```dockerfile
# ✅ 正确顺序：不变的放前面，常变的放后面
COPY package.json package-lock.json ./   # 依赖不常变
RUN npm ci                               # 不常变
COPY . .                                 # 常变，放最后
```

---

## 五、部署：让服务器自动拉取最新镜像

### 方案一：GitHub Actions SSH 部署

```yaml
# 在 build job 后面加 deploy job
jobs:
  build:
    # ... 构建和推送 ...

  deploy:
    needs: build          # 等 build 完成后再执行
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to server
        uses: appleboy/ssh-action@v1
        with:
          host: ${{ secrets.SERVER_HOST }}
          username: ${{ secrets.SERVER_USER }}
          key: ${{ secrets.SERVER_SSH_KEY }}
          script: |
            cd /opt/my-app
            docker compose pull
            docker compose up -d --remove-orphans
            docker image prune -f
```

需要添加 3 个 GitHub Secrets：
- `SERVER_HOST`：服务器 IP 或域名
- `SERVER_USER`：SSH 用户名
- `SERVER_SSH_KEY`：SSH 私钥（不要用密码登录）

### 方案二：Watchtower 自动更新

Watchtower 是一个容器，它监控镜像仓库，发现新版本后自动更新容器：

```yaml
# compose.yml
services:
  watchtower:
    image: containrrr/watchtower
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
    command: --interval 60 --cleanup my-app
    restart: always
```

```bash
# 每 60 秒检查一次，发现新镜像就自动更新 my-app 容器
docker compose up -d watchtower
```

**适合场景**：小型项目、个人服务器，不需要复杂的部署策略。

**不适合场景**：生产环境、需要蓝绿部署或金丝雀发布的大型项目。

### 方案三：Webhook 触发

在服务器上跑一个简单的 webhook 服务，CI 构建完成后 HTTP POST 通知服务器：

```bash
# 服务器上的 webhook 处理脚本
#!/bin/bash
# /opt/webhook/deploy.sh
cd /opt/my-app
docker compose pull
docker compose up -d --remove-orphans
echo "Deployed at $(date)"
```

```yaml
# GitHub Actions 中
- name: Notify webhook
  run: |
    curl -X POST ${{ secrets.WEBHOOK_URL }}
```

---

## 六、完整 CI/CD 工作流示例

```yaml
# .github/workflows/deploy.yml
name: Build and Deploy

on:
  push:
    branches:
      - main
    tags:
      - 'v*'

env:
  REGISTRY: docker.io
  IMAGE_NAME: ${{ secrets.DOCKERHUB_USERNAME }}/my-app

jobs:
  # ===== 第一步：测试 =====
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run tests
        run: |
          docker compose -f docker-compose.test.yml up --abort-on-container-exit --exit-code-from test

  # ===== 第二步：构建并推送 =====
  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Log in to Docker Hub
        uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKERHUB_USERNAME }}
          password: ${{ secrets.DOCKERHUB_TOKEN }}

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Build and push
        uses: docker/build-push-action@v6
        with:
          context: .
          push: true
          tags: |
            ${{ env.IMAGE_NAME }}:${{ github.sha }}
            ${{ env.IMAGE_NAME }}:latest
          cache-from: type=gha
          cache-to: type=gha,mode=max

      # 可选：扫描镜像漏洞
      - name: Scan image
        run: docker scout cves ${{ env.IMAGE_NAME }}:latest --only-severity critical,high

  # ===== 第三步：部署 =====
  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'   # 只在 main 分支部署
    steps:
      - name: Deploy via SSH
        uses: appleboy/ssh-action@v1
        with:
          host: ${{ secrets.SERVER_HOST }}
          username: ${{ secrets.SERVER_USER }}
          key: ${{ secrets.SERVER_SSH_KEY }}
          script: |
            cd /opt/my-app
            docker compose pull
            docker compose up -d --remove-orphans
            # 清理 24 小时前的旧镜像
            docker image prune -a --filter "until=24h" -f
```

### 工作流可视化

```
git push main
  │
  ▼
test ──────────────→ 失败 → 停止，不构建
  │
  │ 通过
  ▼
build ─────────────→ 失败 → 停止，不部署
  │
  │ 通过
  ▼
deploy ────────────→ 成功！
  │
  ▼
✅ 新版本在服务器上运行
```

---

## 七、服务器上的 compose.yml

```yaml
# /opt/my-app/compose.yml
services:
  app:
    image: your-username/my-app:latest
    # 注意：不要加 build，直接用镜像
    # build: .  ← 在服务器上不需要构建
    ports:
      - "3000:3000"
    environment:
      NODE_ENV: production
      DB_PASSWORD: ${DB_PASSWORD}
    restart: always
    logging:
      driver: json-file
      options:
        max-size: "10m"
        max-file: "3"
```

### 部署命令

```bash
# 首次部署
cd /opt/my-app
echo "DB_PASSWORD=your_db_password" > .env
docker compose up -d

# 后续更新（CI 自动执行）
docker compose pull       # 拉取最新镜像
docker compose up -d      # 重新创建容器（用新镜像）
docker image prune -f     # 清理旧镜像
```

---

## 八、我做得对不对？

### 验证清单

```bash
# 1. 确认 GitHub Actions workflow 文件存在
ls .github/workflows/
# 预期：看到 deploy.yml 或类似文件

# 2. 推送代码，触发 workflow
git push origin main
# 去 GitHub → Actions 页面，看到 workflow 正在运行

# 3. 确认镜像推送到 Docker Hub
# 去 Docker Hub 查看，有新镜像标签

# 4. 确认服务器上部署成功
ssh your-server
docker ps
# 预期：看到你的应用容器正在运行

# 5. 确认版本正确
docker inspect your-app --format='{{.Config.Image}}'
# 预期：看到 your-username/my-app:latest 或带有 commit hash 的标签

# 6. 验证缓存生效
# 在 GitHub Actions 的 build 日志中搜索 "CACHED"
# 预期：部分层显示 CACHED
```

---

## 九、不对怎么办？

### 常见错误 1：Docker Hub Token 泄露

```yaml
# ❌ Token 写在 YAML 里，提交到 Git
- name: Login
  run: docker login -u myuser -p dckr_pat_abc123...
```

GitHub 会扫描公开仓库中的 Secret，一旦发现就会自动撤销 Token 并通知你。

✅ 修正：永远用 GitHub Secrets：

```yaml
- name: Login
  run: |
    echo "${{ secrets.DOCKERHUB_TOKEN }}" | docker login -u "${{ secrets.DOCKERHUB_USERNAME }}" --password-stdin
```

### 常见错误 2：CI 中每次都 `--no-cache` 构建

```yaml
# ❌ 每次都从头构建，太慢
- name: Build
  run: docker build --no-cache -t my-app .
```

✅ 修正：用 Buildx 的 GitHub Actions 缓存：

```yaml
- uses: docker/build-push-action@v6
  with:
    cache-from: type=gha
    cache-to: type=gha,mode=max
```

### 常见错误 3：`docker compose pull` 不更新镜像

```bash
# ❌ 如果 compose 里写了 build，pull 不会拉取新镜像
```

```yaml
# ❌ 服务器上的 compose.yml
services:
  app:
    build: .          # 这是本地构建，不是拉取镜像
    ports:
      - "3000:3000"
```

```bash
docker compose pull
# 提示：app Skipped - No image tag specified, pull skipped
```

✅ 修正：服务器上不要用 `build`，直接用 `image`：

```yaml
services:
  app:
    image: your-username/my-app:latest   # 用镜像，不要 build
    ports:
      - "3000:3000"
```

### 常见错误 4：SSH 部署失败，权限不够

```bash
# 症状：CI 日志显示 SSH 连接成功，但 docker 命令报 Permission denied
```

❌ 原因：SSH 登录的用户不在 `docker` 组里。

✅ 修正：把用户加入 `docker` 组：

```bash
sudo usermod -aG docker $USER
# 然后重新登录 SSH 生效
```

### 常见错误 5：标签策略混乱，不知道部署的是哪个版本

```bash
# ❌ 只打 latest 标签
docker push my-app:latest
# 两周后出 bug，想回滚，但不知道之前部署的是哪个版本
```

✅ 修正：同时打 `latest` 和 `github.sha`：

```yaml
tags: |
  ${{ env.IMAGE_NAME }}:${{ github.sha }}
  ${{ env.IMAGE_NAME }}:latest
```

回滚时：

```bash
# 在服务器上
docker compose down
# 编辑 compose.yml，把 image 标签改为具体 commit hash
# image: my-app:abc1234
docker compose up -d
```

---

## 十、术语解释

| 术语 | 解释 |
|------|------|
| **CI/CD** *此术语见附录C* | Continuous Integration / Continuous Delivery（或 Deployment）。持续集成：代码合并时自动构建和测试。持续交付：自动部署到生产环境 |
| **GitHub Actions** *此术语见附录C* | GitHub 内置的 CI/CD 平台，通过 `.github/workflows/` 下的 YAML 文件定义工作流。每次 git push 自动触发 |
| **Buildx** *此术语见附录C* | Docker 的增强构建工具，支持多平台构建、构建缓存、并行构建。在 CI/CD 中主要通过 `docker/setup-buildx-action` 使用 |
| **Docker Hub** *此术语见附录C* | Docker 官方的镜像仓库（Registry），存放和分发 Docker 镜像。类似 GitHub 存代码，Docker Hub 存镜像 |
| **镜像标签（Image Tag）** *此术语见附录C* | 镜像的版本标识，如 `my-app:v1.2.3`。同一个镜像可以有多个标签。`latest` 是默认标签 |
| **Watchtower** | 开源工具，自动监控并更新 Docker 容器。发现镜像仓库有新版本时，自动拉取并重启容器 |

---

## 本章小结

| 本章学了什么 | 对应命令/概念 | 注意事项 |
|-------------|-------------|---------|
| CI/CD 基本流程 | 检出 → 测试 → 构建 → 推送 → 部署 | 每一步都是上一步的"门禁" |
| GitHub Actions 工作流 | `.github/workflows/deploy.yml` | 用 GitHub Secrets 存敏感信息 |
| Docker 登录 | `docker/login-action@v3` | 用 `--password-stdin`，永远不要命令行传密码 |
| 构建 + 推送 | `docker/build-push-action@v6` | 同时打 `github.sha` 和 `latest` 标签 |
| 标签策略 | `:abc1234` + `:latest` | `latest` 方便部署，`sha` 方便回滚 |
| 缓存优化 | `cache-from: type=gha` | 不改的层复用缓存，构建从 5 分钟降到 30 秒 |
| 部署方式 | SSH 部署 / Watchtower / Webhook | 小型项目用 Watchtower，生产环境用 SSH 或 Webhook |
| 服务器 compose | 用 `image:` 不用 `build:` | `pull` 只拉镜像，不构建 |
| 回滚 | 改 `image` 标签为旧版本 → `docker compose up -d` | 前提是保留了旧镜像的标签 |

---

> **[可暂停点 8/8]**：第八篇结束，全教程完成！重启验证命令：
>
> ```bash
> docker version && docker compose version
> # 确认 Docker 和 Compose 环境正常，可以随时开始实践
> ```

---

## 本篇最可能出错的地方及原因

### 1. Docker Hub Token 泄露（最高风险）

**这是 CI/CD 安全中最严重也最常见的问题。** 开发者把 Token 硬编码在 YAML 里，提交到 Git 仓库。GitHub 会扫描公开仓库中的 Secret，一旦发现就自动撤销 Token——但如果是私有仓库，可能很长时间没人发现。

**预防**：在 CI/CD 工作流中，所有敏感信息（Docker Hub Token、SSH 密钥、服务器密码）**必须通过 GitHub Secrets 或等价机制注入**。永远不要在工作流 YAML 中写明文密钥。

**如果已经泄露**：立即在 Docker Hub 上撤销旧 Token，生成新 Token，更新 GitHub Secrets，检查是否有恶意镜像被推送。

### 2. `docker compose pull` 不更新，因为 compose 里写了 `build`

**原因**：`docker compose pull` 只拉取 `image:` 字段指定的镜像。如果 `compose.yml` 里用的是 `build:`，`docker compose pull` 会跳过该服务，提示 "No image tag specified, pull skipped"。CI 部署脚本执行了 `pull`，但服务器上跑的仍然是旧镜像。

**排查**：检查服务器上的 `compose.yml`，确认所有服务用的是 `image:` 而不是 `build:`。如果本地开发需要 `build`，用 `docker-compose.override.yml` 覆盖。

### 3. CI 缓存不生效，每次都从头构建

**原因**：Docker 层缓存依赖文件内容的哈希值。如果 `COPY . .` 在 `COPY package.json` 之前，每次代码变更都会导致所有后续层缓存失效。或者 CI 环境之间不共享缓存（如每次新开一个 runner）。

**解决**：① 把 `COPY . .` 放到 Dockerfile 最后；② 用 `cache-from` 和 `cache-to` 配置 GitHub Actions 缓存；③ 确保 `mode=max` 让所有中间层都参与缓存。

### 4. SSH 部署失败因为服务器上的 Docker 版本太旧

**原因**：CI 构建的镜像可能用了新版 Dockerfile 语法，但服务器上的 Docker 版本太旧不支持。比如 `docker compose` 命令需要 Docker Compose v2，而旧服务器上只有 `docker-compose`（v1）。

**排查**：在 CI 的部署脚本中加一行 `docker version && docker compose version`，确认服务器 Docker 版本。

### 5. git push 后部署了，但线上还是旧版本

**原因**：`docker compose up -d` 只有在容器配置变了或镜像更新了才会重建容器。如果 `pull` 拉到了新镜像但容器已经在运行，`up -d` 可能认为"不需要重建"。

**解决**：用 `docker compose up -d --force-recreate` 强制重建，或者先 `docker compose down` 再 `docker compose up -d`。