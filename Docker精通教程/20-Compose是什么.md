# 20 — Compose 是什么？

> - 对应文档版本：Docker精通教程 outline v1
> - 适用环境：任何已安装 Docker 的系统
> - 读者角色：已掌握 Dockerfile 和 docker run，需要管理多容器应用的开发者
> - 预计耗时：新手 25 分钟 / 熟手 10 分钟
> - 前置教程：第 10-14 章（Dockerfile 系列）
> - 可视化：无

---

## 我在做什么？

到目前为止，你启动一个应用是这样的：

```bash
# 启动 MySQL
docker run -d --name mysql-db \
  -e MYSQL_ROOT_PASSWORD=your_password \
  -e MYSQL_DATABASE=myapp \
  -v mysql-data:/var/lib/mysql \
  --network my-net \
  mysql:8.0

# 启动 Redis
docker run -d --name redis-cache \
  --network my-net \
  redis:7-alpine

# 启动 Web 应用
docker run -d --name web-app \
  -p 8080:3000 \
  -e DB_HOST=mysql-db \
  -e REDIS_HOST=redis-cache \
  --network my-net \
  my-web-app:v1
```

每次都要记忆这些命令——参数顺序、环境变量名、网络名、卷名。重启电脑后，还得按正确顺序一条条重新执行。更糟的是，你把这些命令写给同事，同事可能漏掉 `--network` 导致容器之间互相找不到。

**Docker Compose** *此术语见附录C* 就是来解决这个问题的：把上面的三行命令，变成一个 YAML 文件，然后一条命令搞定。

学完这一章，你能：
- 理解 Docker Compose 解决什么问题
- 区分 `docker compose`（新版）和 `docker-compose`（旧版）
- 安装并验证 Compose 可用
- 写出第一个 compose.yml 文件
- 用一条命令启动多容器应用

---

## 一、问题：手动管理多容器的痛苦

### 一个真实的场景

你做了一个 Web 应用，依赖三个服务：

```
Web 应用（Node.js，端口 3000）
  ├── 需要 MySQL（数据库，端口 3306）
  ├── 需要 Redis（缓存，端口 6379）
  └── 需要 Nginx（反向代理，端口 80）
```

在没有 Compose 的情况下，你需要：

1. 创建网络：`docker network create my-net`
2. 创建数据卷：`docker volume create mysql-data`
3. 启动 MySQL：`docker run -d --name mysql ...`（记得连网络、挂卷）
4. 等 MySQL 启动完成（约 30 秒）
5. 启动 Redis：`docker run -d --name redis ...`
6. 启动 Web 应用：`docker run -d --name web ...`
7. 启动 Nginx：`docker run -d --name nginx ...`

每次要调整一个参数——比如把 MySQL 密码改成别的——你要回忆所有相关命令，找出写密码的那一条，改掉，然后重新执行整个序列。

**这就是 Compose 要解决的核心问题：把"启动一组容器"从一个手动执行的任务，变成一个可复现的声明式配置。**

---

## 二、Docker Compose 是什么？

### 一句话定义

Docker Compose 是一个工具，让你用 **YAML** *此术语见附录C* 文件定义多容器应用，然后**一条命令**启动、停止、重建所有服务。

### 类比：Compose 是"容器编排的 recipe"

想象你去餐厅点菜 vs 自己做菜：

- **手动 docker run** = 自己买菜、洗菜、切菜、炒菜、洗碗。每一步都得自己干，顺序不能错，分量不能忘。
- **Docker Compose** = 一张食谱（recipe）。上面写着：3 个鸡蛋、200g 面粉、1 勺盐、烤箱 180°C 烤 20 分钟。你照着食谱，全部材料准备好，一起推进烤箱，等 20 分钟，取出来就能吃。

compose.yml 就是这张食谱。它描述了：
- 需要哪些"材料"（服务、镜像、端口、环境变量、数据卷）
- 材料之间怎么搭配（网络、依赖关系）
- 最终怎么"烹饪"（一条 `docker compose up`）

### 你能用 Compose 做什么？

```
docker compose up       → 启动所有服务
docker compose down     → 停止并清理所有服务
docker compose ps       → 查看所有服务的状态
docker compose logs     → 查看所有服务的日志（一站式）
docker compose exec     → 进入某个服务的容器
```

> 对比一下：不用 Compose，你需要 `docker ps` 找到容器名，再 `docker logs 容器名` 看日志。用 Compose，你只需要 `docker compose logs`——所有服务的日志全部输出，按服务名自动标注。

---

## 三、安装 Docker Compose

### Docker Desktop 用户（Windows / macOS）

**已经自带，不需要单独安装。**

Docker Desktop 安装时就包含了 Compose 插件。你打开终端，直接就能用：

```bash
docker compose version
```

### Linux 用户

Linux 需要单独安装 `docker-compose-plugin` 包：

```bash
# Ubuntu / Debian
sudo apt-get update
sudo apt-get install docker-compose-plugin

# CentOS / RHEL / Fedora
sudo yum install docker-compose-plugin
# 或
sudo dnf install docker-compose-plugin
```

安装后验证：

```bash
docker compose version
# 预期输出类似：
# Docker Compose version v2.24.0
```

### 如果你还在用旧版 `docker-compose`（独立 Python 包）

旧版 `docker-compose` 是一个独立的 Python 程序，命令是 `docker-compose`（中间有连字符）。新版是 Docker 的**插件**，命令是 `docker compose`（中间是空格）。

```bash
# 旧版（独立 Python 包，不推荐）
docker-compose up

# 新版（Docker 插件，推荐）
docker compose up
```

怎么知道你在用哪个？

```bash
# 旧版
docker-compose version
# 输出：docker-compose version 1.29.2, build 5becea4c

# 新版
docker compose version
# 输出：Docker Compose version v2.24.0
```

> **关键区别**：新版的 `docker compose` 是 Docker CLI 的子命令（`docker` 后面跟 `compose`），旧版 `docker-compose` 是一个独立的可执行文件。新版功能更全、性能更好、兼容性更强。如果你系统里两个都有，**优先用新版 `docker compose`（空格）**。

---

## 四、最小示例：一个 Nginx 容器的 compose.yml

我们不急着上多容器。先用 Compose 启动一个 Nginx 容器，感受一下 compose.yml 长什么样。

### 步骤 1：创建项目目录

```bash
mkdir my-first-compose
cd my-first-compose
```

### 步骤 2：写 compose.yml

```yaml
# compose.yml
services:
  web:
    image: nginx:alpine
    ports:
      - "8080:80"
```

这个文件只有 5 行，但它相当于：

```bash
docker run -d --name web -p 8080:80 nginx:alpine
```

逐行解释：

| 行 | 含义 |
|----|------|
| `services:` | 定义一个或多个服务 *此术语见附录C* |
| `web:` | 这个服务的名字叫 `web`（你可以随便起名） |
| `image: nginx:alpine` | 使用 `nginx:alpine` 镜像 |
| `ports: - "8080:80"` | 把宿主机的 8080 端口映射到容器的 80 端口 |

### 步骤 3：启动

```bash
docker compose up -d
```

输出：

```
[+] Running 2/2
 ✔ Network my-first-compose_default  Created
 ✔ Container my-first-compose-web-1  Started
```

Docker Compose 自动做了两件事：
1. 创建了一个网络 `my-first-compose_default`（Compose 默认创建一个以项目名命名的网络）
2. 创建并启动了容器

### 步骤 4：验证

```bash
# 浏览器打开 http://localhost:8080
# 或者在终端：
curl http://localhost:8080
# 预期：看到 Nginx 欢迎页面的 HTML
```

```bash
# 查看容器
docker compose ps
# 输出：
# NAME                     IMAGE          COMMAND                  SERVICE   CREATED         STATUS         PORTS
# my-first-compose-web-1   nginx:alpine   "/docker-entrypoint.…"   web       2 minutes ago   Up 2 minutes   0.0.0.0:8080->80/tcp
```

注意容器名：`my-first-compose-web-1`。命名规则：`项目名-服务名-序号`。项目名默认是 compose.yml 所在目录的名字。

### 步骤 5：停止

```bash
docker compose down
# 输出：
# [+] Running 2/2
#  ✔ Container my-first-compose-web-1  Removed
#  ✔ Network my-first-compose_default  Removed
```

一个命令，容器和网络全清理了。对比不用 Compose 的清理：

```bash
docker stop web && docker rm web && docker network rm my-net
# 三条命令，还得回忆名字，还得按顺序
```

---

## 五、我做得对不对？

### 验证方法

```bash
# 1. 确认 Compose 已安装
docker compose version
# 预期：输出 Docker Compose version v2.x.x

# 2. 创建测试目录
mkdir ~/compose-test && cd ~/compose-test

# 3. 创建 compose.yml（内容如上）
cat > compose.yml << 'EOF'
services:
  web:
    image: nginx:alpine
    ports:
      - "8080:80"
EOF

# 4. 启动
docker compose up -d

# 5. 查看状态
docker compose ps
# 预期：web 服务状态为 Up

# 6. 访问
curl http://localhost:8080
# 预期：看到 Nginx 欢迎页 HTML（包含 "Welcome to nginx!"）

# 7. 查看日志
docker compose logs
# 预期：看到 Nginx 的启动日志

# 8. 清理
docker compose down
# 预期：容器和网络被删除
```

---

## 六、不对怎么办？

### 常见错误 1：`docker compose` 命令找不到

```bash
docker compose up
# docker: 'compose' is not a docker command.
```

❌ 原因：Compose 插件没安装，或者你用的是旧版 Docker Engine（不带插件支持）。

✅ 解决：

```bash
# 先检查 Docker 版本
docker --version
# Docker version 20.10.0 以上才支持 compose 子命令

# 如果版本够新但 compose 子命令不存在，可能是插件没装
# Linux 手动安装：
sudo apt-get install docker-compose-plugin
# 或
sudo yum install docker-compose-plugin

# 如果实在装不了新版，可以用旧版 docker-compose（独立包）
docker-compose --version
```

### 常见错误 2：`docker compose` 和 `docker-compose` 混用

```bash
# ❌ 你写了：
docker-compose up
# 但 compose.yml 里用了新版才有的语法

# ✅ 统一用新版
docker compose up
```

新版和旧版基本兼容，但新版支持更多特性（如 `profiles`、`depends_on` 的 `condition` 等）。如果你拿不准，就统一用 `docker compose`（空格）。

### 常见错误 3：YAML 格式错误

```yaml
# ❌ 错误：缩进用了 tab 而不是空格
services:
	web:          # ← 这行前面是 tab
		image: nginx:alpine   # ← 这行也是 tab
```

```yaml
# ✅ 正确：用空格缩进（2 个或 4 个都行，但要统一）
services:
  web:           # ← 2 个空格
    image: nginx:alpine  # ← 4 个空格
```

YAML 对缩进极其敏感。**必须用空格，不能用 Tab。** 如果你的编辑器把 Tab 自动转成了空格，你不会遇到这个问题；如果没转，`docker compose up` 会报类似 `mapping values are not allowed here` 的错误。

### 常见错误 4：端口被占用

```bash
docker compose up -d
# Error: port 8080 is already allocated
```

❌ 原因：宿主机的 8080 端口已经被其他程序（或另一个容器）占用了。

✅ 解决：

```yaml
# 改成其他端口
services:
  web:
    image: nginx:alpine
    ports:
      - "9090:80"   # 用 9090 代替 8080
```

或者先找出谁占了 8080：

```bash
# Windows
netstat -ano | findstr :8080

# Linux / macOS
lsof -i :8080
```

---

## 七、术语解释

本节出现的术语，汇总放在这里：

| 术语 | 解释 |
|------|------|
| **Docker Compose** | Docker 官方提供的多容器编排工具，通过 YAML 文件定义应用，一条命令启动所有服务 |
| **YAML** | 一种人类可读的数据序列化格式。用缩进表示层级，用冒号分隔键值。Docker Compose 用 YAML 写配置文件 |
| **编排** *此术语见附录C* | 把多个容器作为一个整体来管理：定义它们之间的关系、启动顺序、网络、存储等 |
| **compose.yml** | Docker Compose 的默认配置文件名。放在项目根目录，`docker compose` 命令自动读取 |
| **服务** *此术语见附录C* | Compose 里的"服务"对应一个容器（或一组相同容器）。每个服务运行一个镜像，有独立的端口、环境变量、数据卷等配置 |

---

## 本章小结

| 本章学了什么 | 对应命令/概念 | 注意事项 |
|-------------|-------------|---------|
| Docker Compose 的作用 | 用 YAML 文件定义多容器应用，一条命令启动 | 解决手动 docker run 的参数记忆和顺序问题 |
| Compose 的类比 | 容器编排的 recipe | 声明式配置 vs 命令式执行 |
| 安装 Compose | Docker Desktop 自带；Linux 需装 `docker-compose-plugin` | 先 `docker compose version` 确认可用 |
| 新版 vs 旧版 | `docker compose`（空格，插件）vs `docker-compose`（连字符，独立 Python 包） | 优先用新版，功能更全 |
| 最小 compose.yml | `services: web: image: nginx:alpine ports: - "8080:80"` | 5 行配置 = 一条 docker run 命令 |
| 启动 | `docker compose up -d` | `-d` 后台运行；自动创建网络 |
| 查看状态 | `docker compose ps` | 容器名格式：`项目名-服务名-序号` |
| 停止并清理 | `docker compose down` | 一条命令删除容器和网络 |
| YAML 格式 | 用空格缩进，不能用 Tab | 最常见的初学者错误 |

---

## 本篇最可能出错的地方及原因

### 1. `docker compose` 和 `docker-compose` 搞混

**原因**：网上教程新旧混杂。有的教程写 `docker-compose up`，有的写 `docker compose up`。新手不知道区别，看到一个命令就复制。

**区别**：`docker-compose`（连字符）是旧版独立 Python 包，`docker compose`（空格）是新版 Docker CLI 插件。新版功能更全（如 `docker compose watch`、`depends_on` 的 `condition: service_healthy`），旧版可能不支持某些语法。

**排查**：`docker compose version` 看版本。如果输出 `unknown command`，说明你系统里没装插件。可以用 `docker-compose version` 看旧版是否可用。

**口诀**：**有空格的是新版，没空格的是旧版。优先用有空格的那个。**

### 2. YAML 缩进用 Tab 而不用空格

**原因**：很多编辑器默认缩进是 Tab，写 YAML 时没注意，`docker compose up` 直接报错。

**现象**：`yaml: line X: found character that cannot start any token` 或 `mapping values are not allowed here`。

**解决**：检查编辑器设置，把 YAML 文件的缩进模式改成"空格"。VS Code 右下角点 `Spaces: 2` 或 `Spaces: 4`。

### 3. 以为 `docker compose down` 会自动删除数据卷

**默认不会删除 volume。** `docker compose down` 只删除容器和网络，数据卷保留。如果你想把数据卷也删了：

```bash
docker compose down -v
```

`-v` 参数会删除 compose.yml 里定义的匿名卷和具名卷。如果你忘了 `-v`，volume 会残留，下次 `docker compose up` 时数据还在——这可能是你想要的（保留数据），也可能是你不想要的（想从头开始）。**关键是要知道这个默认行为。**

### 4. 端口冲突：多个 compose 项目用了同一个宿主机端口

如果你有两个 compose 项目，都用了 `"8080:80"`，第二个项目启动时会报端口冲突。因为宿主机的 8080 只能被一个进程监听。

**解决**：不同项目用不同的宿主机端口。