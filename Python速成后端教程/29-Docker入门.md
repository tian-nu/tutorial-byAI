# 29-Docker 入门

- 对应文档版本：首版教程
- 适用环境：Ubuntu 22.04 LTS 服务器，已有博客项目
- 读者角色：后端初学者
- 预计耗时：新手 45 分钟 / 熟手 25 分钟
- 前置教程：[28-Nginx + HTTPS]
- 可视化：有，`.project/docs/tutorials/python_29_docker_visual.html`

---

> 📊 可视化演示见 [python_29_docker_visual.html](../../.project/docs/tutorials/python_29_docker_visual.html)

## 一、目标与完成效果

**一句话目标**：用 Docker + Docker Compose 把你的博客项目打包，一条命令就能部署，换服务器只需 `git clone` + `docker-compose up -d`。

**完成后的可观测效果**：
- 服务器上安装了 Docker 和 Docker Compose。
- 项目根目录下有 `Dockerfile` 和 `docker-compose.yml` 两个配置文件。
- `docker-compose build` 能成功构建镜像，镜像包含整个项目代码和所有依赖。
- `docker-compose up -d` 一键启动，浏览器访问 `https://你的域名/docs` 依然正常。
- 数据库数据通过 volume 持久化，删容器不会丢数据（此术语需进附录：volume）。
- `docker-compose logs -f` 能查看实时日志，`docker-compose down` 一键停止。

---

## 二、前置条件

| 序号 | 条件 | 验证命令 |
|------|------|----------|
| 1 | 已完成教程 28，博客系统通过域名 HTTPS 访问 | 浏览器打开 `https://你的域名/docs` 能看到 Swagger UI |
| 2 | SSH 可登录服务器 | `ssh root@你的IP` 能成功登录 |
| 3 | 项目代码在 GitHub/Gitee | `git remote -v` 能看到远程地址 |
| 4 | 服务器至少 1GB 内存（Docker 运行需要一点内存） | `free -h` 能看到 1G+ 内存 |

**一条命令确认前置满足**：

```bash
# 在服务器上执行
curl https://yourdomain.com/docs
```

如果返回 HTML（Swagger UI），前置条件满足。

---

## 三、分步操作

### 步骤 1：痛点回顾——手动部署太麻烦

**我在做什么？** 理解 Docker 解决了什么问题，为什么需要它。

回顾一下你现在的部署流程：

```
买新服务器 → apt install Python Git → git clone → 创建 venv → pip install → 启动服务
```

**问题来了**：
1. **环境不一致**：我本地跑的好好的，换个服务器怎么跑不起来？（依赖版本不同、系统不同、缺少系统库...）
2. **重搭麻烦**：换服务器、重装系统，每换一次环境就要从头来一遍。
3. **依赖地狱**：项目 A 需要 Python 3.10，项目 B 需要 Python 3.11——两个都装，冲突。
4. **卸载麻烦**：删项目，得一个个删依赖，删不干净。

**比喻**：手动部署就像搬家——你得把家具一件件拆下来搬到新家，再一件件拼起来。不同的新家插座型号不一样，地板高度不一样，拼起来各种不合适。

---

### 步骤 2：Docker 比喻——集装箱

**我在做什么？** 理解 Docker 的核心思想——把应用打包成"集装箱"。

**Docker 怎么解决问题？** 你把你的应用（代码、依赖、配置、运行环境）全部打包成一个**镜像**（此术语需进附录）。镜像就像一个集装箱：

- 集装箱里面什么都有，到了新地方，开箱即用。
- 哪里有 Docker，哪里就能运行你的镜像，环境完全一致。
- 一个集装箱一个应用，互不干扰。

**比喻**：
- **镜像**（Image）：就是你打包好的"集装箱"。包含了代码、依赖、环境。
- **容器**（Container）：镜像运行起来就是容器。一个镜像可以启动多个容器。此术语需进附录。
- **Docker Hub**：免费的集装箱码头，放着成千上万个官方做好的镜像（`python:3.11`、`nginx`、`postgres` 等等）。你可以拉下来直接用。
- **Dockerfile**：写你这个集装箱怎么打包的说明书。
- **Docker Compose**：如果有多个集装箱（应用 + 数据库 + 缓存...），用它来一键启动所有集装箱。

> 📊 可视化演示见 [python_29_docker_visual.html](../../.project/docs/tutorials/python_29_docker_visual.html)

**类比表格**：

| 概念 | 类比 | 解释 |
|------|------|------|
| 镜像 | 程序安装包 | 打包好的所有文件，只读，不能改 |
| 容器 | 运行中的程序 | 镜像运行起来就是容器，一个镜像可以多个容器 |
| Dockerfile | 打包说明书 | 一步步告诉 Docker 怎么构建你的镜像 |
| Docker Compose | 多集装箱说明书 | 定义多个容器怎么一起启动 |
| Volume | 集装箱外的储物箱 | 容器删了，数据还在 |
| Docker Hub | 公共仓库 | 别人做好的镜像放在这里，直接拉下来用 |

---

> 🤔 想多一点：Docker 和虚拟机有什么区别？

| 对比项 | Docker | 虚拟机 |
|--------|--------|--------|
| 启动时间 | 秒级 | 分钟级 |
| 资源占用 | 共享主机内核，占用少 | 每个虚拟机都跑完整 OS，占用大 |
| 磁盘占用 | 几 MB 到几百 MB | 几 GB |
| 隔离性 | 进程级隔离 | 完整系统级隔离 |
| 适合场景 | 单个应用容器化 | 跑多个不同 OS |

**简单说**：Docker 更轻量，启动更快，占资源更少，适合部署后端应用。

---

### 步骤 3：安装 Docker + Docker Compose

**我在做什么？** 在服务器上安装 Docker 和 Docker Compose。

```bash
# SSH 登录服务器
ssh root@你的IP

# 安装 Docker 和 Docker Compose（Ubuntu 22.04 直接预装）
apt install docker.io docker-compose -y
```

**验证安装**：

```bash
docker --version
# 预期输出：Docker version 20.10.x or newer

docker-compose --version
# 预期输出：docker-compose version 1.29.x or newer
```

**如果需要安装最新版 Docker**，可以用官方脚本：

```bash
# 可选：官方脚本安装最新版
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
```

**启动 Docker 服务**：

```bash
systemctl start docker
systemctl enable docker    # 开机自启
```

**验证**：拉一个测试镜像运行：

```bash
docker run hello-world
```

**预期输出**：

```
Hello from Docker!
This message shows that your installation appears to be working correctly.
```

**我做得对不对？** `docker run hello-world` 能正常输出，说明 Docker 安装成功。

---

### 步骤 4：写 Dockerfile——告诉 Docker 怎么打包你的项目

**我在做什么？** 在项目根目录创建 `Dockerfile`，一步步定义怎么打包。此术语需进附录：Dockerfile。

```bash
cd ~/blog_backend
vim Dockerfile
```

**内容如下**：

```dockerfile
# 1. 基础镜像：从 Docker Hub 拉取 Python 3.11 镜像
FROM python:3.11-slim

# 2. 设置工作目录（容器内的 /app 目录）
WORKDIR /app

# 3. 把当前目录的 requirements.txt 复制到容器里
COPY requirements.txt .

# 4. 安装依赖
RUN pip install --no-cache-dir -r requirements.txt

# 5. 把整个项目复制到容器里
COPY . .

# 6. 暴露端口（告诉别人容器用了哪个端口，只是文档说明）
EXPOSE 8000

# 7. 启动命令（容器启动时运行的命令）
CMD ["uvicorn", "blog_backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**逐行解释**：

| 指令 | 作用 |
|------|------|
| `FROM python:3.11-slim` | 基于官方 Python 3.11 镜像构建。`slim` 版很小（只有几十 MB），够用。 |
| `WORKDIR /app` | 容器中所有后续命令都在 `/app` 目录执行。相当于 `cd /app`。 |
| `COPY requirements.txt .` | 把你电脑（服务器）上的 `requirements.txt` 复制到容器的当前工作目录（`/app`）。 `.` 表示"当前目录"。 |
| `RUN pip install ...` | 在构建镜像时执行这条命令——安装 Python 依赖。 |
| `COPY . .` | 把你电脑上的所有文件复制到容器里。第一个 `.` = 你电脑当前目录，第二个 `.` = 容器当前目录。 |
| `EXPOSE 8000` | 只是文档说明，告诉别人这个容器监听 8000 端口。不代表自动开放端口。 |
| `CMD [...]` | 容器启动时默认执行的命令。这是数组格式，每个参数一个字符串。 |

**❌ 常见错误**：

```dockerfile
# ❌ 命令格式错误，CMD 不能用空格分隔成一个字符串（推荐数组格式）
CMD "uvicorn blog_backend.main:app --host 0.0.0.0 --port 8000"

# ✅ 正确格式
CMD ["uvicorn", "blog_backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**为什么先复制 `requirements.txt` 再复制整个项目？** 这是 Docker 构建缓存技巧：

- 如果 `requirements.txt` 没变，下次构建直接用缓存的 `pip install` 层，不用重新装一遍依赖，构建快很多。
- 如果 `requirements.txt` 变了，才重新装依赖。

---

### 步骤 5：写 docker-compose.yml——定义服务

**我在做什么？** 创建 `docker-compose.yml`，用 Docker Compose 定义并管理你的服务。此术语需进附录：docker-compose。

```bash
vim docker-compose.yml
```

**内容如下**：

```yaml
services:
  app:
    build: .                    # 从当前目录的 Dockerfile 构建镜像
    ports:
      - "8000:8000"            # 主机端口:容器端口
    restart: always            # 容器挂了自动重启
    volumes:
      - ./:/app               # 把当前目录挂载到容器（开发用，改代码不需要重新构建）
    environment:
      - DATABASE_URL=sqlite:///app/data.db

# 如果用 PostgreSQL，可以在这里加一个 db 服务：
# volumes:
#   postgres_data:              # 数据持久化
```

**逐行解释**：

| 配置 | 含义 |
|------|------|
| `services:` | 定义所有服务（容器），这里我们只有一个服务叫 `app` |
| `build: .` | Docker Compose 会自动找到当前目录的 `Dockerfile`，帮你构建镜像 |
| `ports: "8000:8000"` | 把主机的 8000 端口映射到容器的 8000 端口。格式：`主机端口:容器端口`。 |
| `restart: always` | Docker 守护进程会自动监控容器，如果你容器挂了，自动重启。非常实用。 |
| `volumes: ./:/app` | 把主机当前目录（项目代码）挂载到容器的 `/app`。好处：改了代码，容器里也会变，开发时不用重新构建镜像。如果你用 SQLite，数据库文件也在里面，数据不会丢。 |
| `environment:` | 设置环境变量。你的代码可以通过 `os.getenv("DATABASE_URL")` 读取。 |

**如果后续要加 PostgreSQL**，完整的 `docker-compose.yml` 长这样（供参考）：

```yaml
services:
  app:
    build: .
    ports:
      - "8000:8000"
    restart: always
    depends_on:
      - db
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/blog

  db:
    image: postgres:16-alpine
    restart: always
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=blog
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

**比喻**：`docker-compose.yml` 就像一份"集装箱船队说明书"——上面写着：船队里有几个集装箱（`app`、`db`），每个集装箱从哪来、暴露哪个端口、数据存在哪里、启动顺序是什么。一键就能把整个船队开起来。

---

### 步骤 6：构建镜像

**我在做什么？** 用 Docker Compose 构建你的镜像。

```bash
# 确保在项目根目录（有 docker-compose.yml）
cd ~/blog_backend

# 构建镜像
docker-compose build
```

**这一步需要几分钟**，取决于网络速度：
1. 拉取 `python:3.11-slim` 基础镜像
2. 复制 `requirements.txt`
3. `pip install` 安装依赖
4. 复制整个项目
5. 完成构建

**成功后输出**：`Successfully built xxxxxxxx`。

**我做得对不对？** `docker-compose images` 能看到你的镜像：

```bash
docker-compose images
```

输出应该包含 `blog_backend_app` 镜像。

---

### 步骤 7：一键启动

**我在做什么？** 用 Docker Compose 在后台启动服务。

```bash
# 后台启动（-d = detached，后台运行）
docker-compose up -d
```

**预期输出**：

```
Creating blog_backend_app_1 ... done
```

**查看容器状态**：

```bash
docker-compose ps
```

`State` 应该显示 `Up`。

**查看日志**（实时输出）：

```bash
docker-compose logs -f
```

按 `Ctrl+C` 退出日志查看，容器继续运行。

**现在测试**：浏览器打开 `https://你的域名/docs`，应该正常访问！

**因为 Nginx 已经配置好了反向代理，把请求转发给 `127.0.0.1:8000`，Docker 暴露了 8000 端口，Nginx 能直接访问，不需要改 Nginx 配置。**

---

### 步骤 8：查看日志、停止、重启

**我在做什么？** 学会日常管理 Docker Compose 服务的基本命令。

**常用命令速查**：

| 命令 | 作用 |
|------|------|
| `docker-compose up -d` | 构建并后台启动服务 |
| `docker-compose ps` | 查看所有容器状态 |
| `docker-compose logs -f` | 实时查看日志（按 Ctrl+C 退出） |
| `docker-compose logs -f app` | 只看 app 服务的日志 |
| `docker-compose restart` | 重启服务 |
| `docker-compose stop` | 停止服务（容器还在） |
| `docker-compose down` | 停止并删除容器（镜像还在，数据如果在 volume 也还在） |
| `docker-compose build --no-cache` | 强制重新构建，不用缓存（依赖版本更新时用） |

**示例**：

```bash
# 修改了代码，重新构建并重启：
docker-compose build
docker-compose up -d

# 看日志：
docker-compose logs -f

# 停止服务：
docker-compose down
```

---

### 步骤 9：数据库持久化——数据不丢

**我在做什么？** 理解 volume 是怎么让数据不丢的。此术语需进附录：持久化。

**如果用 SQLite**：

我们在 `docker-compose.yml` 里写了：

```yaml
volumes:
  - ./:/app
```

意思是：把主机的 `./`（当前目录）挂载到容器的 `/app`。你的 SQLite 数据库文件 `data.db` 就在主机当前目录，所以：
- 删掉容器 → 文件还在主机
- 重新 `up` → 数据还在

**如果用 PostgreSQL 或 MySQL**：

我们定义了一个 volume：

```yaml
volumes:
  postgres_data:
```

然后挂载到容器：

```yaml
volumes:
  - postgres_data:/var/lib/postgresql/data
```

Docker 会把数据库数据存在 Docker 管理的 volume 里，放在 Docker 的数据目录。即使你删掉容器、删掉服务，volume 还在，数据不会丢。下次 `docker-compose up -d`，数据自动回来。

**比喻**：volume 就像"集装箱外的保险柜"。集装箱扔了，保险柜还在，里面的东西（数据）不会丢。换个新集装箱，把保险柜挂上去，东西直接用。

---

### 步骤 10：一键部署——以后换服务器只需两步

**我在做什么？** 现在你换一台新服务器，部署只需两条命令。

```bash
# 1. 克隆项目
git clone https://github.com/你的用户名/blog_backend.git
cd blog_backend

# 2. 一键启动
docker-compose up -d
```

**完了？完了！**

**因为**：
- Docker 已经在服务器上装好了（如果没装，`apt install docker.io docker-compose -y` 一条命令）。
- `docker-compose up -d` 自动构建镜像 → 创建容器 → 启动服务。
- 依赖都在镜像里，不需要 `pip install`，不需要创建 `venv`。
- 环境完全一致，不会出现"本地跑的好好的服务器跑不起来"。

---

## 四、完整代码清单

### `blog_backend/Dockerfile`

<details>
<summary>点击展开完整代码</summary>

```dockerfile
# 基础镜像：Python 3.11 slim 版（小巧够用）
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 复制依赖清单
COPY requirements.txt .

# 安装依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制整个项目
COPY . .

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uvicorn", "blog_backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

</details>

---

### `blog_backend/docker-compose.yml`

<details>
<summary>点击展开完整代码（SQLite 版）</summary>

```yaml
services:
  app:
    build: .
    ports:
      - "8000:8000"
    restart: always
    volumes:
      - ./:/app
    environment:
      - DATABASE_URL=sqlite:///app/data.db
```

</details>

<details>
<summary>点击展开完整代码（PostgreSQL 版，含数据库服务）</summary>

```yaml
services:
  app:
    build: .
    ports:
      - "8000:8000"
    restart: always
    depends_on:
      - db
    environment:
      - DATABASE_URL=postgresql://blog_user:blog_password@db:5432/blog_db

  db:
    image: postgres:16-alpine
    restart: always
    environment:
      POSTGRES_USER: blog_user
      POSTGRES_PASSWORD: blog_password
      POSTGRES_DB: blog_db
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

</details>

---

## 五、验证方法

```bash
# 在服务器上执行：

# 1. Docker 安装验证
docker --version && docker-compose --version
# → 显示版本号，安装正常

# 2. 构建镜像
docker-compose build
# → 最后输出 Successfully built xxxxxxxx

# 3. 启动服务
docker-compose up -d
# → Creating blog_backend_app_1 ... done

# 4. 查看状态
docker-compose ps
# → State 显示 Up

# 5. 查看日志
docker-compose logs -f
# → 最后能看到 "Uvicorn running on http://0.0.0.0:8000"

# 6. 浏览器验证
# 打开 https://你的域名/docs
# → 能看到 Swagger UI，接口能正常调用

# 7. 持久化验证
# 创建一篇文章，然后：
docker-compose down
docker-compose up -d
# 查看文章还在 → 数据持久化成功
```

---

## 六、术语附录

| 术语 | 英文 | 通俗解释 | 本章出现位置 |
|------|------|----------|-------------|
| Docker | — | 容器化平台，把应用和依赖打包成镜像，随处运行。解决"环境不一致"问题。 | 步骤 2 |
| 镜像 | Image | 只读的模板，打包了应用代码、依赖、运行环境。就像"安装包"。 | 步骤 2 |
| 容器 | Container | 镜像运行起来的实例。一个镜像可以启动多个容器。容器之间互相隔离。 | 步骤 2 |
| Docker Hub | — | Docker 官方公共镜像仓库，存放了成千上万官方镜像（`python`、`nginx`、`postgres` 等）。 | 步骤 2 |
| Dockerfile | — | 文本文件，定义镜像构建步骤：用什么基础镜像、复制什么文件、安装什么依赖、启动命令是什么。 | 步骤 4 |
| docker-compose | Docker Compose | 工具，用于定义和运行多容器 Docker 应用。用一个 YAML 文件定义所有服务，一键启动。 | 步骤 5 |
| volume | Volume | Docker 持久化数据的机制。数据存在主机文件系统，容器删了数据还在。 | 步骤 9 |
| 持久化 | Persistence | 把数据保存到硬盘，程序/容器关闭后数据不丢失。 | 步骤 9 |
| 构建缓存 | Build Cache | Docker 分层构建镜像，如果某一层没变，直接用缓存，不用重新构建，加快构建速度。 | 步骤 4 |
| 端口映射 | Port Mapping | `主机端口:容器端口`，把容器端口暴露到主机，让外面能访问。 | 步骤 5 |
| `restart: always` | — | Docker 自动重启策略。容器退出或服务器重启后，Docker 自动把容器拉起来。 | 步骤 5 |
| 环境变量 | Environment Variables | 在容器中设置环境变量，应用通过 `os.getenv()` 读取，方便配置不同环境（开发/生产）。 | 步骤 5 |

---

## 七、小结

| 你学到了什么 | 一句话总结 |
|--------------|-----------|
| Docker 解决什么问题 | 环境不一致，手动部署麻烦，换服务器重复劳动 |
| Docker 核心比喻 | 集装箱——把应用和依赖打包，哪里有 Docker 哪里就能跑 |
| 镜像 vs 容器 | 镜像是安装包（只读），容器是运行中的程序 |
| Dockerfile 是什么 | 构建镜像的说明书，每一行对应一个构建步骤 |
| docker-compose.yml 是什么 | 多服务定义文件，一键启动所有容器 |
| volume 作用 | 持久化数据，容器删除数据不丢 |
| 一键部署 | 换服务器只需 `git clone` + `docker-compose up -d`，两分钟搞定 |
| 常用命令 | `build` → `up -d` → `ps` → `logs -f` → `down` |

---

## 八、已知坑点与禁止事项

| 坑点 | 现象 | 原因 | 解决 |
|------|------|------|------|
| `CMD` 格式错误 | 容器启动失败 | 字符串格式 `CMD "uvicorn ..."` 会把整个命令当成一个可执行文件找不到 | 必须用数组格式：`CMD ["uvicorn", "blog_backend.main:app", ...]` |
| 端口映射写反 | `8000:8000` → 正确；`8000 8000` → 错误；`容器端口:主机端口` → 错误 | 格式是 `主机端口:容器端口` | 记住：先主机后容器。`"8000:8000"` 表示主机 8000 映射到容器 8000。 |
| 忘记 `--host 0.0.0.0` | 容器内启动了，但 Nginx 访问不到 | uvicorn 默认监听 127.0.0.1，只能容器内访问 | `CMD` 里必须加 `--host 0.0.0.0`，才能让主机（Nginx）访问 |
| 数据存在容器里，删容器数据丢了 | 容器删了，数据库数据没了 | 没有用 volume 挂载数据目录，数据存在容器层，删容器就没了 | 一定要用 volume 挂载数据目录（SQLite 挂载项目目录，PostgreSQL 用 named volume） |
| 每次改代码都要重新构建 | 慢 | 开发时用 `volumes: ./:/app` 挂载主机目录，改代码容器里自动变，不用重新构建 | 生产环境可以直接用镜像，不用挂载 |
| 构建慢，每次都重新装依赖 | 构建慢 | 把 `COPY . .` 放在 `RUN pip install` 前面了，每次代码变都重新装依赖 | 先复制 `requirements.txt`，装完依赖再复制整个项目，利用缓存 |
| 用了 `ubuntu` 基础镜像，镜像很大 | 镜像几百 MB 甚至几个 GB | `ubuntu` 是完整系统镜像，包含很多你不需要的东西 | Python 用 `python:3.11-slim` 或 `python:3.11-alpine`，只有几十 MB |
| 容器启动后立刻退出 | `docker ps` 看不到容器，Exited | 容器里的主进程退出了，容器就退出了。查看日志 `docker-compose logs` 找原因。 | `docker-compose logs` 看错误信息，解决错误后 `docker-compose up -d` |

---

## 九、下一步建议

Docker 入门到此结束！你现在已经掌握了 Docker 最核心的用法：`Dockerfile` 定义镜像、`docker-compose.yml` 定义服务、`docker-compose up -d` 一键部署。这足够你 90% 的日常开发和部署使用了。

Docker 还有很多进阶玩法：多阶段构建、Docker Hub 推送镜像、Kubernetes 编排容器... 这些留给进阶教程。对于个人博客项目，你现在学到的已经完全够用了。

---

> [可暂停点 8/9]：阶段八（部署上线）第四部分完成。你现在能用 Docker 一键部署你的项目，换服务器只需两分钟。接下来进入最后一章：回顾与总结。