# 30-Docker 容器化部署

> "你在本地跑得好好的博客，部署到服务器上却报错——`better-sqlite3` 编译失败、Node.js 版本不对、系统库缺失……这些'环境问题'占用了部署工作量的 80%。Docker 一劳永逸地解决它：把代码、依赖、运行时全都打包进一个'箱子'，在本地能跑的箱子，在服务器上也能跑。这一章，你从零创建 Dockerfile、构建镜像、运行容器，再用 docker-compose 一键编排 Node.js + PostgreSQL + Nginx 三容器——让你的部署从'手工作坊'升级为'流水线工厂'。"

---

## 一、目标与完成效果

**一句话目标**：创建 Dockerfile、`.dockerignore`、`docker-compose.yml`，把博客系统容器化，理解镜像、容器、Volume 等 Docker 核心概念，实现一键部署。

**完成后的可观测效果**：
- `Dockerfile` 创建在 `blog-backend/` 根目录——基于 `node:18-alpine`，`npm ci --production`，`CMD ["node", "server.js"]`。
- `.dockerignore` 创建在 `blog-backend/` 根目录——排除了 `node_modules/`、`.env`、`uploads/`、`tests/`、`*.db`、`.git/`。
- `docker build -t blog-backend .` 构建成功，镜像大小约 150-200MB。
- `docker run -d -p 3000:3000 --name blog --env-file .env blog-backend` 启动容器成功。
- `curl http://localhost:3000/api/articles` 返回 JSON 数据。
- `docker-compose.yml` 创建在 `blog-backend/` 根目录——编排 `app`（Node.js）+ `db`（PostgreSQL）+ `nginx` 三容器。
- `docker-compose up -d` 一键启动三个容器。
- 你能向同事解释：镜像 vs 容器、Dockerfile vs docker-compose、Volume 的作用。

---

## 二、前置条件

| 序号 | 条件 | 验证命令 |
|------|------|------|
| 1 | 已完成教程 26，博客系统全部测试通过 | `npm test` 输出 `18 passed, 18 total` |
| 2 | 本地安装了 Docker Desktop | `docker --version` 输出版本号（如 `Docker version 24.x.x`） |
| 3 | 博客系统当前使用 SQLite（`better-sqlite3`） | `ls database/blog.db` 在 `blog-backend/` 下存在（或能通过 `npm run dev` 启动后自动创建） |

**一条命令确认前置满足**：

```bash
docker --version && npm test
```

`docker --version` 有输出，`npm test` 输出 `18 passed`，前置条件满足。

**如果没装 Docker Desktop**：
- Windows/Mac：去 https://www.docker.com/products/docker-desktop/ 下载安装
- Linux 服务器：`sudo apt install docker.io docker-compose -y`

---

## 三、分步操作

### 步骤 1：Docker 是什么？

在动手之前，先理解 Docker 的核心概念。如果你需要深度学习，本教程配套了《Docker 精通教程》——本章只讲部署所需的最小知识。

#### 1.1 三个核心概念

| 概念 | 一句话解释 | 搬家比喻 |
|------|-----------|----------|
| **镜像（Image）** | 打包好的"代码 + 环境 + 依赖"的只读模板 | 打包好的搬家箱——里面装好了所有东西，封箱贴标签 |
| **容器（Container）** | 镜像的运行实例——一个隔离的轻量级进程 | 在新家打开的搬家箱——箱子里的东西在新家正常使用 |
| **Dockerfile** | 构建镜像的"配方"——描述镜像里有什么、怎么构建 | 搬家清单——"箱子 1：放锅碗瓢盆；箱子 2：放衣服" |

**关系链**：`Dockerfile` → `docker build` → 镜像（Image）→ `docker run` → 容器（Container）

**比喻**：Dockerfile 是菜谱，镜像是做好的菜（可以打包带走），容器是端上桌正在被吃的菜。一份菜谱可以做出很多份菜，一份菜可以被很多人吃——同理，一个 Dockerfile 可以构建出镜像，一个镜像可以启动多个容器。

#### 1.2 Docker 解决了什么问题？

| 传统部署的问题 | Docker 的解决方案 |
|---------------|------------------|
| "在我电脑上能跑啊" | Docker 镜像包含完整环境——任何地方运行都一样 |
| Node.js 版本不一致 | 镜像中固定了 Node.js 版本（如 `node:18-alpine`） |
| 系统库缺失（如 `better-sqlite3` 编译失败） | 镜像中包含了所有系统依赖 |
| 多个应用抢占端口 | 每个容器是隔离的，各自有独立的端口空间 |
| 部署步骤多、容易出错 | `docker-compose up -d` 一条命令搞定 |

> 搬家比喻：传统部署 = 把家具拆成零件，搬到新家再组装（容易丢零件、装错）。Docker 部署 = 把整个房间打包成集装箱，搬到新家直接打开（一模一样，不会出错）。

---

### 步骤 2：安装 Docker（服务器上）

如果你之前在服务器上部署了博客（第 28 章），现在在服务器上安装 Docker：

```bash
sudo apt update
sudo apt install docker.io docker-compose -y
```

**让 deploy 用户不用 sudo 也能用 docker**：

```bash
sudo usermod -aG docker $USER
```

**退出重新登录**使权限生效：

```bash
exit
ssh deploy@your_server_ip
```

**验证**：

```bash
docker --version
# → Docker version 24.x.x
docker-compose --version
# → docker-compose version 1.29.x
```

> 🔥 **魔鬼细节**：`usermod -aG docker $USER` 中的 `-a` 是"追加"（append）——不加 `-a` 会把用户从其他组中移除（包括 `sudo` 组），导致你失去 sudo 权限。这是个常见悲剧。

---

### 步骤 3：创建 Dockerfile

在 `blog-backend/` 根目录下创建 `Dockerfile`：

```dockerfile
# 1. 基础镜像：Node.js 18 + Alpine Linux（超轻量）
FROM node:18-alpine

# 2. 设置工作目录（容器内的路径）
WORKDIR /app

# 3. 先复制 package.json 和 package-lock.json
#    （先复制这两个文件，可以利用 Docker 的层缓存）
COPY package*.json ./

# 4. 安装生产依赖（跳过 devDependencies）
#    npm ci 比 npm install 更快更严格，适合 CI/CD 环境
RUN npm ci --production

# 5. 复制所有源代码
COPY . .

# 6. 声明容器运行时监听的端口（仅文档作用）
EXPOSE 3000

# 7. 启动命令（exec 形式，不要用 shell 形式）
CMD ["node", "server.js"]
```

#### 3.1 逐行解释

| 行 | 指令 | 含义 | 为什么要这样写 |
|----|------|------|---------------|
| 1 | `FROM node:18-alpine` | 以 `node:18-alpine` 为基础镜像 | Alpine Linux 超轻量（~5MB），基于它的 Node.js 镜像只有 ~120MB，而 `node:18`（基于 Debian）有 ~350MB |
| 2 | `WORKDIR /app` | 设置工作目录 | 后续的 `COPY`、`RUN`、`CMD` 都在 `/app` 下执行——相当于 `cd /app` |
| 3-4 | `COPY package*.json ./` | 只复制 `package.json` 和 `package-lock.json` | Docker 构建有层缓存——如果 `package.json` 没变，这层直接用缓存，跳过 `npm ci`，构建速度极快 |
| 5 | `RUN npm ci --production` | 安装生产依赖 | `npm ci` 严格按 `package-lock.json` 安装，适合 CI/CD（此术语需进附录）；`--production` 跳过 devDependencies |
| 6 | `COPY . .` | 复制所有源代码 | 把 `server.js`、`routes/`、`middleware/`、`database/` 等全部复制到容器的 `/app/` |
| 7 | `EXPOSE 3000` | 声明容器监听 3000 端口 | 这只是文档——告诉使用者"这个容器在 3000 端口提供服务"。实际的端口映射靠 `docker run -p` |
| 8 | `CMD ["node", "server.js"]` | 容器启动时执行的命令 | 用 exec 形式（JSON 数组），不要用 shell 形式（`CMD node server.js`）——exec 形式能正确接收 Unix 信号（如 SIGTERM），实现优雅关闭 |

> 🔥 **魔鬼细节**：`COPY package*.json ./` 放在 `COPY . .` 之前，是 Docker 构建优化的关键技巧。Docker 的每一行指令生成一个"层"，如果某层的输入没变，Docker 会使用缓存。把不常变的 `package.json` 放在前面——每次改代码时，`package.json` 没变，`npm ci` 这层直接用缓存，构建从 60 秒降到 2 秒。

#### 3.2 为什么用 `node:18-alpine` 而不是 `node:18`？

| 镜像 | 大小 | 基础系统 | 适用场景 |
|------|------|----------|----------|
| `node:18` | ~350MB | Debian（完整 Linux） | 需要系统级工具（如编译 C++ 扩展） |
| `node:18-alpine` | ~120MB | Alpine Linux（超轻量） | 生产环境部署——小、快、安全 |
| `node:18-slim` | ~200MB | Debian（精简版） | 折中选择 |

`better-sqlite3` 需要编译 C++ 代码——`node:18-alpine` 预装了编译工具，所以没问题。如果你的项目依赖了更多需要编译的原生模块，可能需要 `node:18` 或加装 `build-base`。

#### 3.3 `npm ci` vs `npm install`

| 特性 | `npm install` | `npm ci` |
|------|-------------|---------|
| 速度 | 较慢 | 更快（跳过依赖解析，严格按 lock 文件） |
| 行为 | 可能会修改 `package-lock.json` | 如果 `package-lock.json` 和 `package.json` 不一致，直接报错 |
| 清理 | 不清理 `node_modules/` | 先删除 `node_modules/`，再全新安装 |
| 适用场景 | 日常开发 | CI/CD 构建（Docker 构建属于 CI/CD） |

> 🔥 **魔鬼细节**：`npm ci` 中的 `ci` 不是 "Continuous Integration" 的缩写，而是 "Clean Install" 的缩写。但它在 CI/CD 环境中确实是最佳选择——因为 CI 环境需要可重复的构建，`npm ci` 严格按 lock 文件安装，保证每次构建结果一致。

---

### 步骤 4：创建 `.dockerignore`

在 `blog-backend/` 根目录下创建 `.dockerignore`：

```
node_modules/
.env
uploads/
tests/
*.db
.git/
.gitignore
Dockerfile
.dockerignore
docker-compose.yml
```

**逐行解释**：

| 排除项 | 为什么排除 |
|--------|-----------|
| `node_modules/` | 不要在本地 `node_modules/` 打包进镜像——容器内会 `npm ci` 重新安装，而且本地的是 Windows/Mac 版本，Linux 容器用不了 |
| `.env` | 不要把本地密钥打包进镜像！镜像可能被上传到 Docker Hub（公开），密钥泄露后果严重 |
| `uploads/` | 上传的文件不应该打包进镜像——应该用 Volume 持久化存储。镜像里打包 `uploads/` 会导致每次构建镜像时上传的文件被打包进去，镜像越来越大 |
| `tests/` | 测试文件不需要在生产镜像中 |
| `*.db` | SQLite 数据库文件不应该打包进镜像——容器重启后数据会丢失，应该用 Volume |
| `.git/` | Git 历史记录不需要在生产镜像中（会显著增大镜像体积） |
| `.gitignore` | 不需要 |
| `Dockerfile` | 不需要 |
| `.dockerignore` | 不需要 |
| `docker-compose.yml` | 不需要 |

> 🔥 **魔鬼细节**：**创建 `.dockerignore` 必须在 `docker build` 之前！** 如果你忘了创建 `.dockerignore`，`COPY . .` 会把 `node_modules/`（几百 MB）打包进镜像，构建极慢，镜像巨大。而且 `.env` 中的密钥会被永久记录在镜像层中——即使你后来删了 `.env`，之前的镜像层仍然包含它。

**比喻**：`.dockerignore` 就像搬家时的"不带清单"——"锅碗瓢盆带，但冰箱里的剩菜不带。衣服带，但旧报纸不带。"不是所有东西都值得搬进新家。

---

### 步骤 5：构建镜像

```bash
cd blog-backend
docker build -t blog-backend .
```

- `-t blog-backend`：给镜像起一个名字（tag）（此术语需进附录）
- `.`：构建上下文（当前目录）——Docker 会把当前目录下的文件发给 Docker 引擎

**预期输出**（首次构建）：

```
[+] Building 45.2s (10/10) FINISHED
 => [1/5] FROM node:18-alpine
 => [2/5] WORKDIR /app
 => [3/5] COPY package*.json ./
 => [4/5] RUN npm ci --production
 => [5/5] COPY . .
 => exporting to image
 => => naming to docker.io/library/blog-backend
```

**验证镜像**：

```bash
docker images | grep blog-backend
```

**预期输出**：

```
blog-backend   latest   abc123def456   2 minutes ago   150MB
```

---

### 步骤 6：运行容器

```bash
# 确保 .env 文件存在
# 如果不存在，参考第 28 章步骤 9 创建

docker run -d -p 3000:3000 --name blog --env-file .env blog-backend
```

**参数解释**：

| 参数 | 含义 |
|------|------|
| `-d` | 后台运行（detached mode）——容器在后台运行，不占用终端 |
| `-p 3000:3000` | 端口映射——`主机端口:容器端口`。把主机的 3000 端口映射到容器的 3000 端口 |
| `--name blog` | 给容器起一个名字（方便后续操作） |
| `--env-file .env` | 从 `.env` 文件加载环境变量（JWT_SECRET、NODE_ENV 等） |
| `blog-backend` | 使用的镜像名 |

**验证容器运行**：

```bash
docker ps
```

**预期输出**：

```
CONTAINER ID   IMAGE           COMMAND                CREATED         STATUS         PORTS                    NAMES
abc123def456   blog-backend    "node server.js"       5 seconds ago   Up 5 seconds   0.0.0.0:3000->3000/tcp   blog
```

**验证服务**：

```bash
curl http://localhost:3000/api/articles
# → 返回 JSON 数据
```

> 🔥 **魔鬼细节**：`EXPOSE 3000` 在 Dockerfile 中只是文档——它**不会实际开放端口**。你必须用 `-p 3000:3000`（或 `-P` 随机映射）才能让外部访问容器内的端口。如果你忘了 `-p`，容器在运行，但外部无法访问。

---

### 步骤 7：docker-compose.yml——进阶：Node.js + PostgreSQL + Nginx 三容器编排

#### 7.1 为什么需要 docker-compose？

你的博客系统有三个组件：
- **Node.js 应用**（Express）
- **数据库**（目前是 SQLite，但 Docker 中 SQLite 有问题——见下文）
- **Nginx**（反向代理 + HTTPS）

docker-compose 让你用**一个 YAML 文件**定义这三个容器的关系，然后**一条命令**全部启动。此术语需进附录。

#### 7.2 Docker 中 SQLite 的问题

SQLite 把数据存到一个文件中（`blog.db`）。在 Docker 中：
- 容器重启后，**容器内的文件会丢失**（除非你用了 Volume）。
- 你可以用 Volume 解决——把 `blog.db` 映射到宿主机。但 SQLite 不支持并发写入——多个容器实例同时写入会出问题。

**所以生产环境应该用 PostgreSQL（或 MySQL）替代 SQLite。** 在本章的 docker-compose 方案中，我们引入 PostgreSQL 容器。这是一个"进阶"方案——你可以选择继续用 SQLite + Volume（简单），也可以切换到 PostgreSQL（更专业）。

> **本教程不强制你切换数据库**——SQLite + Volume 对个人博客完全够用。但 docker-compose.yml 示例中会展示 PostgreSQL 方案，让你知道"专业团队怎么做"。

#### 7.3 创建 `docker-compose.yml`

在 `blog-backend/` 根目录下创建 `docker-compose.yml`：

```yaml
version: '3.8'

services:
  # ========== Node.js 应用 ==========
  app:
    build: .
    container_name: blog-app
    ports:
      - "3000:3000"
    env_file:
      - .env
    environment:
      - NODE_ENV=production
      - DB_HOST=db
      - DB_PORT=5432
      - DB_USER=blog
      - DB_PASSWORD=your_db_password_here
      - DB_NAME=blog
    depends_on:
      - db
    restart: unless-stopped

  # ========== PostgreSQL 数据库 ==========
  db:
    image: postgres:16-alpine
    container_name: blog-db
    environment:
      POSTGRES_USER: blog
      POSTGRES_PASSWORD: your_db_password_here
      POSTGRES_DB: blog
    volumes:
      - pgdata:/var/lib/postgresql/data
    restart: unless-stopped

  # ========== Nginx 反向代理 ==========
  nginx:
    image: nginx:alpine
    container_name: blog-nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/conf.d/default.conf:ro
    depends_on:
      - app
    restart: unless-stopped

# ========== 数据卷 ==========
volumes:
  pgdata:
```

#### 7.4 逐段解释

**`app` 服务（Node.js）**：
- `build: .`：使用当前目录的 Dockerfile 构建镜像
- `ports: "3000:3000"`：端口映射
- `env_file: .env`：加载 `.env` 文件
- `environment`：额外环境变量（数据库连接信息）
- `depends_on: db`：等 `db` 容器启动后再启动 `app`（但不等 PostgreSQL 就绪——见魔鬼细节）
- `restart: unless-stopped`：容器崩溃时自动重启

**`db` 服务（PostgreSQL）**：
- `image: postgres:16-alpine`：使用官方 PostgreSQL 16 Alpine 镜像（轻量）
- `environment`：设置数据库用户名、密码、数据库名
- `volumes: pgdata:/var/lib/postgresql/data`：把 PostgreSQL 数据目录映射到 Volume（持久化——容器删了数据还在）

**`nginx` 服务**：
- `image: nginx:alpine`：使用官方 Nginx Alpine 镜像
- `ports: "80:80"`、`"443:443"`：Nginx 对外暴露 80 和 443
- `volumes: ./nginx.conf:/etc/nginx/conf.d/default.conf:ro`：把本地的 `nginx.conf` 挂载到容器内（`:ro` 表示只读）

**`volumes`（顶级）**：
- `pgdata`：Docker Volume。此术语需进附录。数据持久化——即使容器被删除，Volume 中的数据还在。下次启动新容器，挂载同一个 Volume，数据恢复。

#### 7.5 关于 `depends_on` 的魔鬼细节

> 🔥 **魔鬼细节**：`depends_on: db` 只保证 `db` **容器**先启动，但不保证 PostgreSQL **服务**已就绪（PostgreSQL 启动需要几秒钟）。如果 `app` 在 PostgreSQL 就绪之前就尝试连接数据库，会报错。解决方案：
> - 简单方案：在 `app` 的启动脚本中添加重试逻辑（连接失败等 3 秒重试）
> - 专业方案：使用 `wait-for-it.sh` 或 Docker 的 `healthcheck`
> - 本教程方案：`restart: unless-stopped`——app 启动失败会自动重启，第二次启动时 PostgreSQL 已就绪

**比喻**：`depends_on` 就像"你先出门，我跟上"——但你先出门不代表你已经到了目的地。`restart: unless-stopped` 是"如果你没跟上，就再跟一次"。

---

### 步骤 8：docker-compose 常用命令

| 命令 | 用途 |
|------|------|
| `docker-compose up -d` | 启动所有服务（`-d` 后台运行） |
| `docker-compose down` | 停止并删除所有容器（Volume 保留） |
| `docker-compose down -v` | 停止并删除所有容器 + Volume（⚠️ 数据会丢失！） |
| `docker-compose ps` | 查看所有服务状态 |
| `docker-compose logs app` | 查看 `app` 服务的日志 |
| `docker-compose restart app` | 重启 `app` 服务 |
| `docker-compose build` | 重新构建镜像（代码更新后） |
| `docker-compose up -d --build` | 重新构建并启动（代码更新后一条命令搞定） |

#### 8.1 启动所有服务

```bash
docker-compose up -d
```

**预期输出**：

```
Creating network "blog-backend_default" with the default driver
Creating volume "blog-backend_pgdata" with default driver
Creating blog-db ... done
Creating blog-app ... done
Creating blog-nginx ... done
```

#### 8.2 更新代码后重新部署

```bash
git pull
docker-compose up -d --build
```

这一条命令会：重新构建镜像 → 停止旧容器 → 启动新容器。比之前的 `git pull` + `npm install` + `pm2 restart` 更简洁。

> 🔥 **魔鬼细节**：`docker-compose down` 不会删除 Volume（数据卷）。这意味着 `docker-compose down && docker-compose up -d` 后，PostgreSQL 的数据还在。如果你要彻底清空数据库，用 `docker-compose down -v`（`-v` 删除 Volume）。

---

### 🤔 想多一点：Docker 中的 SQLite vs PostgreSQL

| 维度 | SQLite + Volume | PostgreSQL |
|------|----------------|------------|
| 配置复杂度 | 低——不需要额外容器 | 中——需要单独容器 + 环境变量 |
| 并发支持 | 差——不支持并发写入 | 好——支持高并发 |
| 数据持久化 | 通过 Volume 映射 `blog.db` | 通过 Volume 映射 PostgreSQL 数据目录 |
| 适合场景 | 个人博客、小项目、原型 | 多用户、高并发、团队项目 |
| 本教程当前状态 | ✅ 正在使用 | 下一阶段可选升级 |

**如果你现在不想切换数据库**：继续用 SQLite。在 Dockerfile 中保留 `COPY . .`（会包含 `database/` 目录），在 `docker-compose.yml` 中去掉 `db` 服务和 `depends_on`，用 Volume 映射 `blog.db`：

```yaml
app:
  volumes:
    - ./data:/app/data  # 映射 SQLite 数据库目录
```

> 本教程建议：先用 SQLite + Volume 方案跑起来，以后需要更高并发时再迁移到 PostgreSQL。迁移数据库是后端工程师的必修课——但不是今天。

---

## 四、完整代码清单

### `blog-backend/Dockerfile`（本章新建）

```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --production
COPY . .
EXPOSE 3000
CMD ["node", "server.js"]
```

### `blog-backend/.dockerignore`（本章新建）

```
node_modules/
.env
uploads/
tests/
*.db
.git/
.gitignore
Dockerfile
.dockerignore
docker-compose.yml
```

### `blog-backend/docker-compose.yml`（本章新建）

```yaml
version: '3.8'

services:
  app:
    build: .
    container_name: blog-app
    ports:
      - "3000:3000"
    env_file:
      - .env
    environment:
      - NODE_ENV=production
      - DB_HOST=db
      - DB_PORT=5432
      - DB_USER=blog
      - DB_PASSWORD=your_db_password_here
      - DB_NAME=blog
    depends_on:
      - db
    restart: unless-stopped

  db:
    image: postgres:16-alpine
    container_name: blog-db
    environment:
      POSTGRES_USER: blog
      POSTGRES_PASSWORD: your_db_password_here
      POSTGRES_DB: blog
    volumes:
      - pgdata:/var/lib/postgresql/data
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    container_name: blog-nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/conf.d/default.conf:ro
    depends_on:
      - app
    restart: unless-stopped

volumes:
  pgdata:
```

### `blog-backend/` 目录结构（本章最终状态）

```
blog-backend/
├── server.js
├── package.json
├── package-lock.json
├── Dockerfile              ← 本章新建
├── .dockerignore           ← 本章新建
├── docker-compose.yml      ← 本章新建
├── .gitignore
├── .env
├── jest.config.js
├── node_modules/
├── database/
│   ├── db.js
│   └── schema.js
├── routes/
│   ├── articles.js
│   ├── auth.js
│   ├── comments.js
│   └── upload.js
├── middleware/
│   ├── auth.js
│   ├── logger.js
│   └── errorHandler.js
├── utils/
│   └── AppError.js
├── tests/
│   ├── setup.js
│   ├── auth.test.js
│   └── articles.test.js
└── uploads/
```

---

## 五、验证方法

```bash
# 在 blog-backend/ 目录下执行

# 1. 构建镜像
docker build -t blog-backend .
# → 构建成功，无报错

# 2. 查看镜像
docker images | grep blog-backend
# → blog-backend  latest  xxx  150MB

# 3. 运行容器
docker run -d -p 3000:3000 --name blog-test --env-file .env blog-backend

# 4. 验证服务
curl http://localhost:3000/api/articles
# → 返回 JSON 数据

# 5. 查看容器日志
docker logs blog-test
# → 能看到 "Server is running" 或请求日志

# 6. 停止并删除测试容器
docker stop blog-test && docker rm blog-test

# 7. docker-compose 启动（如果在本地测试）
docker-compose up -d
# → 三个服务都启动成功

# 8. 查看服务状态
docker-compose ps
# → 三个服务状态都是 Up

# 9. 停止 docker-compose
docker-compose down
# → 所有容器停止并删除
```

**全部通过？** 你的博客系统已经容器化了。从今以后，部署只需要两条命令：`git pull` + `docker-compose up -d --build`。

---

## 六、小结表格

| 学到的东西 | 一句话解释 |
|-----------|-----------|
| Docker 镜像 | 打包好的"代码 + 环境 + 依赖"的只读模板——搬家箱 |
| Docker 容器 | 镜像的运行实例——在新家打开的搬家箱 |
| Dockerfile | 构建镜像的配方——搬家清单 |
| `FROM node:18-alpine` | 使用 Node.js 18 + Alpine Linux 超轻量基础镜像 |
| `WORKDIR /app` | 设置容器内工作目录 |
| `COPY package*.json ./` | 先复制 package.json（利用层缓存加速构建） |
| `RUN npm ci --production` | 严格按 lock 文件安装生产依赖 |
| `COPY . .` | 复制所有源代码 |
| `EXPOSE 3000` | 声明端口（仅文档，实际映射靠 `-p`） |
| `CMD ["node", "server.js"]` | exec 形式启动命令（能接收 Unix 信号） |
| `.dockerignore` | 排除 `node_modules/`、`.env`、`tests/` 等——构建前必须创建 |
| `docker build -t blog-backend .` | 构建镜像 |
| `docker run -d -p 3000:3000 --name blog --env-file .env blog-backend` | 运行容器 |
| docker-compose | 用 YAML 文件定义多容器应用，一条命令启动全部 |
| Volume | Docker 数据卷——容器删了数据还在，用于持久化 |
| `docker-compose up -d` | 一键启动所有服务 |
| `docker-compose up -d --build` | 更新代码后重新构建并启动 |
| `node:18-alpine` | 约 120MB，比 `node:18`（350MB）小很多 |
| `npm ci` | 严格按 lock 文件安装，比 `npm install` 更快更严格 |

---

## 七、术语附录

| 术语 | 英文 | 通俗解释 | 本章出现位置 | 字面陷阱 |
|------|------|----------|-------------|----------|
| Docker | — | 容器化平台。把应用及其依赖打包成镜像，在任何地方运行。解决"在我电脑上能跑"问题。 | 步骤 1 | 不是"码头工人"——虽然名字来源于 docker（码头工人），但在技术领域是容器平台。 |
| 镜像 | Image | 打包好的"代码 + 环境 + 依赖"的只读模板。由 Dockerfile 构建而来。镜像可以上传到 Docker Hub 分享。 | 步骤 1 | 不是"照片"——镜像包含了完整的文件系统和运行环境，不只是"外观"。 |
| 容器 | Container | 镜像的运行实例。一个隔离的轻量级进程，有自己的文件系统、网络、进程空间。一个镜像可以启动多个容器。 | 步骤 1 | 不是"箱子"——容器是运行的进程，不是静态的存储。 |
| Dockerfile | — | 构建镜像的文本文件。每一行是一个指令（FROM、COPY、RUN、CMD 等），逐层构建。 | 步骤 3 | 不是"Docker 文件"——它是"Docker 构建脚本"，不是配置文件。 |
| docker-compose | — | Docker 官方工具。用 YAML 文件定义多容器应用（如 Node.js + PostgreSQL + Nginx），一条命令启动全部。 | 步骤 7 | 不是"编写 Docker"——compose 是"编排"（orchestration）的意思，管多个容器的协作。 |
| .dockerignore | — | 类似 `.gitignore`。告诉 Docker 构建时哪些文件不要复制到镜像中。**必须在 `docker build` 之前创建。** | 步骤 4 | 不是"忽略 Docker"——它是"Docker 构建时忽略的文件列表"。 |
| Volume | — | Docker 数据卷。用于持久化存储——容器删除后数据保留。数据库文件、上传文件、日志等应放在 Volume 中。 | 步骤 7.4 | 不是"音量"——Volume 在这里是"卷"（存储卷）的意思。 |
| alpine | Alpine Linux | 超轻量 Linux 发行版（~5MB）。Docker 官方镜像很多都有 alpine 版本（如 `node:18-alpine`、`postgres:16-alpine`），体积极小，适合生产环境。 | 步骤 3.2 | 不是"阿尔卑斯山"——名字确实来源于 Alpine（阿尔卑斯），但指的是"轻量、简洁"的哲学。 |
| `npm ci` | Clean Install | npm 的严格安装模式。先删除 `node_modules/`，再严格按照 `package-lock.json` 安装。如果 lock 文件与 `package.json` 不一致，直接报错。适合 CI/CD。 | 步骤 3.3 | 不是"持续集成"——"ci"是"Clean Install"的缩写，不是"Continuous Integration"。 |

---

## 八、已知坑点与禁止事项

| 坑点 | 现象 | 原因 | 解决 |
|------|------|------|------|
| 忘了创建 `.dockerignore` | `docker build` 极慢，镜像巨大（>500MB），且 `.env` 泄露 | `COPY . .` 把 `node_modules/`（几百 MB）和 `.env`（密钥）都打包了 | 在 `docker build` 之前创建 `.dockerignore`，排除 `node_modules/`、`.env`、`tests/` 等 |
| `CMD node server.js` 而不是 `CMD ["node", "server.js"]` | 容器无法优雅关闭——`docker stop` 等 10 秒后强制 kill | Shell 形式（`CMD node server.js`）启动的子进程不接收 Unix 信号 | 用 exec 形式：`CMD ["node", "server.js"]` |
| `EXPOSE 3000` 但没 `-p 3000:3000` | 容器在运行，但外部无法访问 | `EXPOSE` 只是文档，不实际开放端口 | `docker run -p 3000:3000` 或 `docker-compose` 中配置 `ports` |
| Docker 中 SQLite 数据丢失 | 容器重启后 `blog.db` 没了 | 容器内的文件系统是临时的——容器删除后文件丢失 | 用 Volume 映射数据库文件：`docker run -v ./data:/app/data` |
| `depends_on` 不保证服务就绪 | `app` 启动时连不上 `db`，报错退出 | `depends_on` 只等容器启动，不等服务就绪 | 用 `restart: unless-stopped`（崩溃自动重启），或添加连接重试逻辑 |
| 在 Windows 上构建的镜像在 Linux 上跑不了 | `exec format error` | 构建时指定了平台（如 `--platform linux/amd64`），但实际构建的是 Windows 镜像 | Docker Desktop 默认构建 Linux 镜像，通常没问题。如果手动指定平台，确保是 `linux/amd64` |
| `docker-compose down -v` 误删数据 | 数据库数据全部丢失 | `-v` 参数删除 Volume | 生产环境不要用 `-v`，除非你确定要清空所有数据 |
| `.env` 被打包进镜像 | 密钥泄露——镜像被推送到 Docker Hub 后任何人都能看到 | 忘了在 `.dockerignore` 中排除 `.env` | 在 `.dockerignore` 中添加 `.env`；用 `--env-file` 或 `environment` 在运行时注入环境变量 |

---

## 九、下一步建议

你的博客系统已经容器化了。从本地开发到服务器部署，整个流程现在是：`git push` → 服务器 `git pull` → `docker-compose up -d --build`。但这是最后一章技术教程了——下一章是终点，也是起点。

**下一章（教程 31：你学到了什么 + 下一步去哪）**，你将：
- 回顾 31 章的全部收获——从"Hello World"到"容器化部署"
- 看到一张能力地图——你掌握的技能树
- 了解与 Vue 前端教程的对接方式
- 获得下一步推荐：TypeScript、NestJS、Prisma、GraphQL、微服务、Serverless
- 收到本教程的毕业致辞

---

> [可暂停点 9/9]：阶段八（部署）全部完成。你创建了 Dockerfile、.dockerignore、docker-compose.yml，构建了镜像，运行了容器，理解了 Docker 的核心概念。下一章是毕业回顾——31 章，我们终点见。
>
> 📊 本教程无可视化
>
> 本教程编辑记录：2026-06-12 初始版本（第 7 批：27-31 章）。