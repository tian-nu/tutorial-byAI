# 28 — HEALTHCHECK 健康检查

> - 对应文档版本：Docker精通教程 outline v1
> - 适用环境：任何已安装 Docker 的系统
> - 读者角色：已掌握 Dockerfile 基本写法和 `docker run`，需要确保服务可用性的开发者
> - 预计耗时：新手 35 分钟 / 熟手 15 分钟
> - 前置教程：第 14 章（CMD 和 ENTRYPOINT）、第 22 章（多容器编排）
> - 可视化：无

---

## 我在做什么？

你启动了一个 MySQL 容器，`docker ps` 显示 STATUS 是 `Up`。你以为数据库已经就绪，开始跑业务代码。结果报错 "Connection refused"——MySQL 进程起来了，但还在初始化数据库，需要几十秒才能接受连接。

Docker 只看"进程是否在运行"，不管"服务是否可用"。**容器起来了 ≠ 服务可用。**

这一章教你 **HEALTHCHECK** *此术语见附录C* ——让 Docker 主动探测你的服务是否真正在"工作"，而不是只看进程是否存活。学完这章，你能在 `docker ps` 里直接看到 `(healthy)` 或 `(unhealthy)` 标记，还能在 Compose 里用 `depends_on` + `condition: service_healthy` 确保依赖服务就绪后才启动下游服务。

学完这一章，你能：
- 理解"容器运行"和"服务健康"的区别
- 为 Nginx、MySQL、自定义应用添加健康检查
- 看懂 `docker ps` 中的 `(healthy)` / `(unhealthy)` 状态
- 在 Compose 中用 `condition: service_healthy` 控制启动顺序
- 配合 `--restart` 策略，让不健康的容器自动恢复

---

## 一、问题：容器 Running ≠ 服务 Ready

### 一个真实的场景

```bash
docker run -d --name db mysql:8.0
docker ps
# CONTAINER ID   STATUS         PORTS     NAMES
# abc123         Up 3 seconds             db

# 看起来 MySQL 启动了，马上连接
mysql -h 127.0.0.1 -P 3306 -u root -p
# ERROR 2003 (HY000): Can't connect to MySQL server
```

`docker ps` 说 `Up`，但连不上。为什么？

MySQL 的启动过程大致是：

```
1. 启动 mysqld 进程           ← 进程起来了，docker ps 显示 Up
2. 初始化数据目录            ← 如果首次启动，需要几十秒
3. 创建系统表                ← 继续等
4. 开始监听 3306 端口         ← 现在才能接受连接！
```

Docker 默认只检查**容器内的 PID 1 进程是否在运行**。只要 mysqld 进程没死，Docker 就认为容器是"Up"的。但进程可能在"初始化"、"等待依赖"、"加载配置"——这些都不是"健康"状态。

> **想多一点**：你可以把 Docker 的默认检测想象成"呼吸检测"——人还有呼吸（进程在跑），就是活的。但一个昏迷的人（服务在初始化）和醒着的人（服务可用）是不一样的。HEALTHCHECK 是"意识检测"——它在问"你好吗？"并期待一个有意义的回答。在生产环境中，这个区别至关重要：负载均衡器需要知道哪些实例是健康的才能转发流量；编排系统（如 Kubernetes）需要知道容器是否健康才能决定是否重启它。

---

## 二、HEALTHCHECK 指令语法

### 基本格式

```dockerfile
HEALTHCHECK [选项] CMD 健康检查命令
```

### 完整参数

```dockerfile
HEALTHCHECK --interval=30s --timeout=3s --retries=3 --start-period=10s \
  CMD curl -f http://localhost/health || exit 1
```

| 参数 | 含义 | 默认值 | 说明 |
|------|------|--------|------|
| `--interval` | 检查间隔 | 30s | 每 30 秒执行一次检查命令 |
| `--timeout` | 单次检查超时 | 30s | 检查命令超过 30 秒没返回就视为失败 |
| `--retries` | 重试次数 | 3 | 连续失败 N 次后标记为 `unhealthy` |
| `--start-period` | 启动缓冲期 | 0s | 容器启动后前 N 秒只记录失败，不标记 unhealthy |

### 健康状态流转

```
容器启动
  │
  ▼
starting ──────────────────────────────────────────┐
  │  （启动缓冲期或初始检查中）                       │
  │                                                │
  │  检查通过 ──────────────────┐                   │
  ▼                             │                  │
healthy ────────────────────────┼───────────────────┤
  │  持续通过检查                │                  │
  │                             │                  │
  │  检查失败                   │                  │
  ▼                             │                  │
(一次失败) ── 累计失败 < retries ─┘                  │
  │                                                │
  │  连续失败 >= retries                            │
  ▼                                                │
unhealthy ─────────────────────────────────────────┘
  │  连续失败
  │
  │  检查恢复通过
  ▼
healthy ── 重新变为健康
```

一次检查失败不会立即标记 `unhealthy`。只有**连续失败**达到 `--retries` 次后，才标记为 `unhealthy`。同样，从 `unhealthy` 恢复也需要连续成功。

> **想多一点**：这个设计很有道理。如果一次检查失败就标记 unhealthy，那网络抖动、瞬间高负载都可能触发误判。`--retries=3` 的意思是"给我三次机会，三次都失败才说明真的有问题"。这就像你叫朋友：叫一声没回，可能是没听到；叫两声没回，可能在忙；叫三声还没回，你才确定他真的不在。

---

## 三、实战：给 Nginx 加健康检查

### 最简单的 Dockerfile with HEALTHCHECK

```dockerfile
FROM nginx:alpine

# 健康检查：每 30 秒对 localhost 发一个 HTTP 请求
# 如果返回 200（curl 返回 0），检查通过
# 如果连接失败（curl 返回非 0），检查失败
HEALTHCHECK --interval=30s --timeout=3s --retries=3 \
  CMD curl -f http://localhost/ || exit 1
```

注意：`nginx:alpine` 镜像自带 `curl`。如果基础镜像没有 `curl`，你需要先安装它，或者用 `wget`：

```dockerfile
FROM nginx:alpine
# alpine 版 nginx 自带 curl，如果用的是 debian 版，需要安装：
# RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

HEALTHCHECK --interval=30s --timeout=3s --retries=3 \
  CMD curl -f http://localhost/ || exit 1
```

### 构建并观察

```bash
# 创建目录和 Dockerfile
mkdir health-demo && cd health-demo

# 构建
docker build -t nginx-health .

# 启动
docker run -d --name nginx-health -p 8080:80 nginx-health

# 观察健康状态
docker ps
# CONTAINER ID   STATUS                    PORTS
# abc123         Up 30 seconds (healthy)   0.0.0.0:8080->80/tcp
#                              ↑
#                         有这个标记了！
```

`docker ps` 的 STATUS 列现在显示 `(healthy)`。如果健康检查还没完成第一次，你会看到 `(health: starting)`。

### 实时查看健康检查日志

```bash
docker inspect --format='{{json .State.Health}}' nginx-health | python -m json.tool
```

输出类似：

```json
{
    "Status": "healthy",
    "FailingStreak": 0,
    "Log": [
        {
            "Start": "2026-06-06T10:00:00.123456Z",
            "End": "2026-06-06T10:00:00.234567Z",
            "ExitCode": 0,
            "Output": "  % Total    % Received ...\n<html>...</html>"
        },
        {
            "Start": "2026-06-06T10:00:30.123456Z",
            "End": "2026-06-06T10:00:30.234567Z",
            "ExitCode": 0,
            "Output": "  % Total    % Received ...\n<html>...</html>"
        }
    ]
}
```

- `Status`：当前状态（`healthy` / `unhealthy` / `starting`）
- `FailingStreak`：当前连续失败次数（0 表示健康）
- `Log`：最近的 5 次检查记录（Docker 只保留最近 5 条）

---

## 四、实战：给 MySQL 加健康检查

MySQL 的健康检查不能用 `curl`，因为 MySQL 不是 HTTP 服务。可以用 `mysqladmin ping`：

```dockerfile
FROM mysql:8.0

# MySQL 的健康检查：用 mysqladmin ping 检测
HEALTHCHECK --interval=10s --timeout=5s --retries=5 --start-period=60s \
  CMD mysqladmin ping -h localhost -u root -p${MYSQL_ROOT_PASSWORD} || exit 1
```

几个关键参数：
- `--start-period=60s`：MySQL 首次启动可能需要 30～60 秒初始化，这期间不标记 unhealthy
- `--retries=5`：MySQL 的重试次数放高一点，因为初始化时间长
- `--interval=10s`：比默认 30s 更频繁，MySQL 的健康检查本身很快

### 验证

```bash
docker build -t mysql-health .
docker run -d --name mysql-health \
  -e MYSQL_ROOT_PASSWORD=your_password_here \
  mysql-health

# 刚启动时
docker ps
# STATUS: Up 5 seconds (health: starting)

# 等 60 秒后
docker ps
# STATUS: Up 65 seconds (healthy)
```

---

## 五、实战：给自定义应用加健康检查

### 如果你的应用有 `/health` 端点

```dockerfile
FROM node:20-alpine
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
EXPOSE 3000
HEALTHCHECK --interval=15s --timeout=3s --retries=3 \
  CMD curl -f http://localhost:3000/health || exit 1
CMD ["node", "server.js"]
```

前提是你的应用有一个 `/health` 路由，返回 200：

```javascript
app.get('/health', (req, res) => {
  res.status(200).json({ status: 'ok' });
});
```

### 如果你的应用没有 HTTP 端点

不一定要用 HTTP。任何能判断"服务是否正常"的命令都可以：

```dockerfile
# 检查某个进程是否存在
HEALTHCHECK CMD pgrep -f "my-app" || exit 1

# 检查某个文件是否存在
HEALTHCHECK CMD test -f /tmp/app-ready || exit 1

# 检查 TCP 端口是否监听
HEALTHCHECK CMD nc -z localhost 3000 || exit 1
```

### 健康检查命令的黄金法则

> **健康检查命令必须：**
> 1. 轻量（不要做复杂计算，不要下载文件）
> 2. 快速（`--timeout` 内必须完成）
> 3. 确定性（同样的输入永远返回同样的结果）
> 4. 代表真实可用性（不能只检查进程存在，要检查服务能响应）

---

## 六、在 Compose 中用健康检查控制启动顺序

第 22 章学了 `depends_on`，但 `depends_on` 默认只等容器启动，不等服务就绪。加上 `condition: service_healthy` 才能真正等：

```yaml
# compose.yml
services:
  db:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: your_password_here
      MYSQL_DATABASE: myapp
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost", "-u", "root", "-p${MYSQL_ROOT_PASSWORD}"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 60s

  app:
    build: .
    ports:
      - "3000:3000"
    environment:
      DB_HOST: db
      DB_PASSWORD: ${MYSQL_ROOT_PASSWORD}
    depends_on:
      db:
        condition: service_healthy    # 等 db 变成 healthy 才启动 app
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/health"]
      interval: 15s
      timeout: 3s
      retries: 3
```

关键行：

```yaml
depends_on:
  db:
    condition: service_healthy
```

**没有 `condition: service_healthy`**：`app` 在 `db` 容器启动（`Up`）后立刻启动，但 `db` 可能还在初始化，`app` 连不上数据库。

**有 `condition: service_healthy`**：`app` 等到 `db` 的 STATUS 变为 `(healthy)` 后才启动。确保数据库完全就绪。

### Compose 中 healthcheck 的写法

在 Compose 里，`HEALTHCHECK` 指令有两种写法：

```yaml
# 写法 1：shell 形式（和 Dockerfile 一样）
healthcheck:
  test: curl -f http://localhost/ || exit 1
  interval: 30s
  timeout: 3s
  retries: 3

# 写法 2：exec 形式（推荐，避免 shell 解析问题）
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost/"]
  interval: 30s
  timeout: 3s
  retries: 3
```

> **推荐用 exec 形式**。shell 形式里的管道符 `||` 和特殊字符在 YAML 解析时可能出问题。exec 形式每个参数都是一个数组元素，不会发生解析歧义。

---

## 七、HEALTHCHECK + `--restart`：自动恢复

健康检查不仅告诉你问题，还可以配合 `--restart` 策略自动处理：

```bash
docker run -d \
  --name myapp \
  --restart unless-stopped \
  --health-interval=30s \
  --health-timeout=3s \
  --health-retries=3 \
  nginx-health
```

注意：**`--restart` 只在容器退出（进程退出）时触发，不会因为 `unhealthy` 而重启容器。**

Docker 的 `--restart` 策略监听的是容器的**退出事件**，而不是健康状态变化。如果一个容器变成 `unhealthy`，但进程还在运行，`--restart` 不会自动重启它。

### 那 unhealthy 有什么用？

1. **告知**：`docker ps` 直接显示状态，运维人员一眼就能看到
2. **编排**：Compose 和 Swarm 的 `condition: service_healthy` 依赖它
3. **监控**：外部监控系统可以通过 `docker inspect` 获取健康状态
4. **负载均衡**：Swarm 和 Kubernetes 会把流量从 unhealthy 实例上摘掉

如果你需要"unhealthy 自动重启"的能力，在 Docker Compose 中，从 v2.1 开始，`depends_on` 不会因为 unhealthy 重启容器，但你可以用 `restart: always` 配合外部监控。在 Kubernetes 中，liveness probe 会直接重启 unhealthy 的 Pod。

---

## 八、故意破坏健康检查，观察行为

### 实验：让 Nginx 健康检查失败

```bash
# 启动带健康检查的 nginx
docker run -d --name nginx-health-test nginx-health

# 等待几秒，确认 healthy
docker ps --filter name=nginx-health-test
# STATUS: Up 10 seconds (healthy)

# 进入容器，停掉 nginx（但容器还在运行）
docker exec nginx-health-test nginx -s stop
# nginx 停了，但 bash 这个 exec 进程退出后容器还在

# 等 30 秒（interval），再检查
docker ps --filter name=nginx-health-test
# STATUS: Up 60 seconds (unhealthy)
#                         ↑
#                   变成 unhealthy 了！
```

### 查看健康检查日志

```bash
docker inspect --format='{{json .State.Health}}' nginx-health-test | python -m json.tool
```

你会看到 `FailingStreak` 从 0 开始增加，`Status` 从 `healthy` 变成 `unhealthy`。

### 恢复健康

```bash
docker exec nginx-health-test nginx
# 重新启动 nginx

# 等几个 interval 后
docker ps --filter name=nginx-health-test
# STATUS: Up 120 seconds (healthy)
#                         ↑
#                   恢复了！
```

---

## 九、我做得对不对？

### 验证清单

```bash
# 1. 创建带 HEALTHCHECK 的 Dockerfile
cat > Dockerfile << 'EOF'
FROM nginx:alpine
HEALTHCHECK --interval=10s --timeout=3s --retries=3 \
  CMD curl -f http://localhost/ || exit 1
EOF

# 2. 构建
docker build -t health-test .

# 3. 启动容器
docker run -d --name health-test health-test

# 4. 等待 10 秒，检查状态
sleep 12
docker ps --filter name=health-test
# 预期：STATUS 列显示 (healthy)

# 5. 查看健康检查详情
docker inspect --format='{{json .State.Health}}' health-test | python -m json.tool
# 预期：Status 为 "healthy"，FailingStreak 为 0

# 6. 破坏健康检查
docker exec health-test nginx -s stop
# 等 30 秒（3 次 retries × 10s interval）
sleep 35
docker ps --filter name=health-test
# 预期：STATUS 列显示 (unhealthy)

# 7. 恢复
docker exec health-test nginx
sleep 35
docker ps --filter name=health-test
# 预期：STATUS 列恢复为 (healthy)

# 8. 清理
docker stop health-test && docker rm health-test
```

---

## 十、不对怎么办？

### 常见错误 1：健康检查命令本身消耗资源太多

```dockerfile
# ❌ 错误：健康检查做了一个复杂的数据库查询
HEALTHCHECK --interval=5s \
  CMD curl -f http://localhost:3000/api/heavy-computation || exit 1
# 每 5 秒触发一次重计算，拖垮应用
```

**症状**：应用越来越慢，但健康检查本身也消耗了大量 CPU。

✅ 修正：健康检查应该是最轻量的端点：

```dockerfile
HEALTHCHECK --interval=30s \
  CMD curl -f http://localhost:3000/health || exit 1
```

`/health` 端点只检查关键依赖（数据库连接、缓存连接），返回 `{"status": "ok"}` 或 `{"status": "degraded"}`。不做计算、不写数据库、不下载文件。

### 常见错误 2：interval 太短导致误判

```dockerfile
# ❌ 错误：每 2 秒检查一次，3 次失败就标记 unhealthy
HEALTHCHECK --interval=2s --timeout=1s --retries=3 \
  CMD curl -f http://localhost/ || exit 1
# 6 秒内 3 次失败就 unhealthy，一次网络抖动就触发
```

✅ 修正：

```dockerfile
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD curl -f http://localhost/ || exit 1
```

生产环境的建议值：
- `--interval=30s`（不要太频繁）
- `--timeout=5s`（给网络留点余量）
- `--retries=3`（连续 3 次失败，约 90 秒后才标记 unhealthy）

### 常见错误 3：忘了 `--start-period`，刚启动就被标记 unhealthy

```dockerfile
# ❌ 错误：MySQL 需要 60 秒初始化，但 30 秒后就开始检查
HEALTHCHECK --interval=30s --retries=3 \
  CMD mysqladmin ping -h localhost || exit 1
```

**症状**：容器启动后，前 30 秒健康检查失败，90 秒后（3 次失败）被标记为 `unhealthy`，但 MySQL 可能在第 45 秒就初始化好了。

✅ 修正：

```dockerfile
HEALTHCHECK --interval=30s --timeout=5s --retries=3 --start-period=90s \
  CMD mysqladmin ping -h localhost || exit 1
```

`--start-period=90s` 给 MySQL 90 秒的充裕初始化时间，期间只记录失败，不标记 unhealthy。

### 常见错误 4：健康检查命令语法错误，永远失败

```dockerfile
# ❌ 错误：CMD 写成了 RUN 的格式
HEALTHCHECK --interval=30s \
  CMD ["curl", "-f", "http://localhost/"] || exit 1
# CMD 的 exec 形式不支持 || 和 exit 1
```

✅ 两种修正方式：

```dockerfile
# 方式一：shell 形式（支持 ||）
HEALTHCHECK --interval=30s \
  CMD curl -f http://localhost/ || exit 1

# 方式二：exec 形式（curl 非 0 返回码本身就是失败）
HEALTHCHECK --interval=30s \
  CMD ["curl", "-f", "http://localhost/"]
```

在 exec 形式中，`curl -f` 失败时会返回非 0 退出码，Docker 本身就会认为健康检查失败——不需要 `|| exit 1`。

### 常见错误 5：基础镜像里没有 `curl`

```dockerfile
FROM debian:bookworm-slim
HEALTHCHECK CMD curl -f http://localhost/ || exit 1
# 构建报错：curl: command not found
```

✅ 修正：

```dockerfile
FROM debian:bookworm-slim
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*
HEALTHCHECK CMD curl -f http://localhost/ || exit 1
```

或者用 `wget`（debian 系统通常自带）：

```dockerfile
HEALTHCHECK CMD wget --no-verbose --tries=1 --spider http://localhost/ || exit 1
```

---

## 十一、术语解释

| 术语 | 解释 |
|------|------|
| **HEALTHCHECK** *此术语见附录C* | Dockerfile 指令，定义容器健康检查的规则。Docker 根据检查结果标记容器为 healthy 或 unhealthy |
| **interval** *此术语见附录C* | 健康检查的间隔时间，如 `--interval=30s` 表示每 30 秒检查一次 |
| **timeout** *此术语见附录C* | 单次健康检查的超时时间，超过这个时间没返回就视为失败 |
| **retries** *此术语见附录C* | 连续失败的重试次数，达到这个次数后标记为 unhealthy |
| **healthy** *此术语见附录C* | 健康状态，表示健康检查命令返回成功（退出码 0） |
| **unhealthy** *此术语见附录C* | 不健康状态，表示健康检查命令连续失败达到 retries 次数 |
| **start-period** | 容器启动后的缓冲期，这个期间内健康检查失败不会导致 unhealthy |
| **`condition: service_healthy`** | Compose 中 `depends_on` 的条件，等待依赖服务变为 healthy 后才启动 |

---

## 本章小结

| 本章学了什么 | 对应命令/概念 | 注意事项 |
|-------------|-------------|---------|
| 容器 Running ≠ 服务 Ready | 进程在跑 ≠ 服务可用 | MySQL 初始化需要几十秒，期间连不上 |
| HEALTHCHECK 语法 | `HEALTHCHECK --interval=30s --timeout=3s --retries=3 CMD ...` | 命令必须轻量、快速、确定性 |
| 健康状态流转 | `starting → healthy → unhealthy` | 连续失败 retries 次才标记 unhealthy |
| Nginx 健康检查 | `CMD curl -f http://localhost/ \|\| exit 1` | 确保 curl 可用，或换 wget |
| MySQL 健康检查 | `CMD mysqladmin ping -h localhost` | 需要 start-period 给初始化留时间 |
| 自定义应用 | 提供 `/health` 端点，返回 200 | 端点只检查关键依赖，不做计算 |
| Compose 集成 | `depends_on: service: condition: service_healthy` | 比默认的 depends_on 更可靠 |
| 查看状态 | `docker ps` 的 STATUS 列 | 显示 `(healthy)` / `(unhealthy)` / `(health: starting)` |
| 查看日志 | `docker inspect` 的 `.State.Health` | 保留最近 5 条检查记录 |
| `--restart` 和 HEALTHCHECK 的关系 | `--restart` 不响应 unhealthy | 只有进程退出才触发重启 |

---

> **[可暂停点 6/8]**：第六篇结束。重启验证命令：
>
> ```bash
> docker images | head -5
> # 查看本地已构建的镜像及其大小
>
> docker ps
> # 查看正在运行的容器，检查是否有 (healthy) 标记
> ```

---

## 本篇最可能出错的地方及原因

### 1. 健康检查命令太重，拖垮应用

**这是生产环境最高频的错误。** 健康检查端点和业务逻辑混在一起。比如健康检查 `/health` 端点实际执行了一个数据库聚合查询，每 30 秒触发一次，在流量高峰期雪上加霜。

**正确做法**：健康检查端点只做"是否能连通"的检查，不做计算。如果数据库连接池满了，健康检查端点只返回当前的连接数，不尝试发起新查询。

### 2. `--start-period` 忘了设，慢启动的服务被误判 unhealthy

**原因**：MySQL、PostgreSQL、Elasticsearch 等服务首次启动需要几十秒甚至几分钟。没有 `--start-period`，Docker 在启动后立即开始检查，很快就标记 unhealthy。

**排查**：`docker inspect` 看 `FailingStreak` 和 `Log`。如果前几次检查都失败了，但后面成功了，说明 `--start-period` 不够长。

**建议值**：`--start-period` 设为你服务的最大启动时间 × 1.5。比如 MySQL 通常 60 秒启动完，设 `--start-period=90s`。

### 3. 健康检查命令里用了 `localhost`，但服务监听在 `0.0.0.0`

```dockerfile
# ❌ 如果服务只监听 127.0.0.1，localhost 能通
# ❌ 如果服务监听 0.0.0.0，localhost 也能通（容器内 localhost 就是容器自己）
# ✅ 在容器内，localhost 总是指向容器自己，不会有问题
```

实际上在容器内用 `localhost` 总是安全的，因为容器内的 `localhost` 就是容器自己。但你需要注意服务是否真的在监听指定端口。

### 4. Compose 中 `condition: service_healthy` 但目标服务没有 HEALTHCHECK

```yaml
services:
  app:
    depends_on:
      db:
        condition: service_healthy    # ❌ db 没有定义 healthcheck！
```

**症状**：`docker compose up` 报错：`service "db" has no healthcheck configured`。

✅ 修正：给 `db` 服务加上 `healthcheck` 配置。

### 5. 健康检查命令的退出码理解错误

Docker 的判断标准：**退出码 0 = 健康，非 0 = 不健康。**

```dockerfile
# ❌ 错误：curl 返回 200 时退出码是 0，不写 || exit 1 也是对的
# ✅ 正确但多余的写法：
CMD curl -f http://localhost/ || exit 1
# 这里 curl -f 失败时返回非 0，|| exit 1 把非 0 转成 1，其实一样
```

`curl -f`（`--fail`）在 HTTP 返回非 2xx 状态码时返回退出码 22。Docker 看到非 0 退出码就认为失败。所以 `|| exit 1` 在 shell 形式中不是必须的，但写了更明确。

**注意**：exec 形式中不能写 `|| exit 1`：

```dockerfile
# ❌ 错误：exec 形式不支持 shell 语法
HEALTHCHECK CMD ["curl", "-f", "http://localhost/", "||", "exit", "1"]

# ✅ 正确：exec 形式，curl 非 0 退出码就是失败
HEALTHCHECK CMD ["curl", "-f", "http://localhost/"]
```