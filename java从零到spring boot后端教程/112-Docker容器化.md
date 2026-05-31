# 112-Docker容器化

> 💡 你开发了一个 Spring Boot 应用，在本地跑得很完美。交给同事部署，他花了半天时间装 JDK、配环境变量、调 MySQL 版本、解决"你用的 Mac 我是 Windows"的路径问题——最后应用还是报错。你如果能给他一个"集装箱"：里面装好了你的应用 + JDK + 所有配置，他只需要一条命令就能跑起来，全世界任何机器都一样——这就是 Docker。

---

## 本章目标
- 理解 Docker 的核心概念：镜像、容器、Dockerfile、docker-compose
- 安装 Docker 并跑通第一个容器
- 把 Spring Boot 应用打包成 Docker 镜像
- 用 docker-compose 一键启动应用 + MySQL + Redis
- 掌握常用 Docker 命令

---

## 112.1 Docker 是什么

### 三个核心概念

| 概念 | 一句话解释 | 类比 |
|------|-----------|------|
| **镜像（Image）** | 一个只读的"安装包"，包含应用和它的运行环境 | 你打包好的 `.iso` 安装光盘 |
| **容器（Container）** | 镜像的运行实例，轻量隔离 | 你用光盘安装好、正在运行的系统 |
| **Dockerfile** | 构建镜像的"说明书" | 光盘的制作流程文档 |

### Docker vs 虚拟机

```
虚拟机：                      Docker：
┌─────────────┐              ┌─────────────┐
│   App A      │              │   App A      │
│   Bin/Libs  │              │   Bin/Libs  │
├─────────────┤              ├─────────────┤
│ Guest OS    │              │ Container   │
├─────────────┤              ├─────────────┤
│ Hypervisor  │              │ Docker      │
├─────────────┤              ├─────────────┤
│ Host OS     │              │ Host OS     │
├─────────────┤              ├─────────────┤
│ Hardware    │              │ Hardware    │
└─────────────┘              └─────────────┘
   重（GB级）                    轻（MB级）
   启动1-2分钟                    启动秒级
   每个有完整OS                   共享Host内核
```

---

## 112.2 安装 Docker

### Windows

下载 [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop/)，安装后重启。

### Linux（Ubuntu）

```bash
sudo apt update
sudo apt install docker.io docker-compose-v2 -y
sudo systemctl enable docker --now
sudo usermod -aG docker $USER
```

注销后重新登录，然后验证：

```bash
docker --version
docker run hello-world
```

看到 "Hello from Docker!" 即安装成功。

---

## 112.3 Docker 基础命令

### 镜像操作

```bash
docker images                          # 列出本地所有镜像
docker pull openjdk:17                 # 从 Docker Hub 拉取镜像
docker rmi openjdk:17                  # 删除镜像
docker tag myapp:latest myapp:v1.0     # 打标签
```

### 容器操作

```bash
docker ps                             # 列出运行中的容器
docker ps -a                          # 列出所有容器（含已停止的）
docker run -d -p 8080:8080 myapp      # 后台运行，映射端口
docker stop <container_id>            # 停止容器
docker start <container_id>           # 启动已停止的容器
docker restart <container_id>         # 重启
docker rm <container_id>              # 删除容器
docker rm -f <container_id>           # 强制删除（先停止再删除）
docker logs -f <container_id>         # 实时查看日志
docker exec -it <container_id> bash   # 进入容器内部
```

### docker run 常用参数

```bash
docker run \
  -d \                  # 后台运行（detached）
  --name myapp \        # 给容器起个名字
  -p 8080:8080 \        # 端口映射 主机端口:容器端口
  -e DB_HOST=mysql \    # 设置环境变量
  -v /data:/app/data \  # 挂载卷 主机目录:容器目录
  --restart always \    # 容器退出时自动重启
  myapp:latest
```

### 验证方法

```bash
# 运行一个 nginx
docker run -d --name test-nginx -p 8080:80 nginx:alpine

# 浏览器访问 http://localhost:8080，应看到 nginx 欢迎页

# 验证完后清理
docker rm -f test-nginx
```

---

## 112.4 Dockerfile——把你的应用做成镜像

### 你在做什么？
你要把 Spring Boot 的 jar 包打包成一个 Docker 镜像。

### 完整 Dockerfile

在项目根目录创建 `Dockerfile`：

```dockerfile
FROM eclipse-temurin:21-jre-alpine

WORKDIR /app

COPY target/*.jar app.jar

EXPOSE 8080

ENV JAVA_OPTS="-Xms256m -Xmx512m"

ENTRYPOINT ["sh", "-c", "java $JAVA_OPTS -jar app.jar"]
```

### 逐行解释

| 行 | 含义 |
|----|------|
| `FROM` | 基础镜像——在这个镜像之上构建。`eclipse-temurin:21-jre-alpine` 是精简版 JDK 21 运行时 |
| `WORKDIR` | 设置容器内的工作目录，后面的命令都在这个目录下执行 |
| `COPY` | 把本地的 jar 文件复制到容器内的 `/app/app.jar` |
| `EXPOSE` | 声明容器会监听 8080 端口（仅文档作用，真正映射靠 `-p`） |
| `ENV` | 设置环境变量，可在 `docker run -e` 覆盖 |
| `ENTRYPOINT` | 容器启动时执行的命令 |

### 构建与运行

```bash
mvn clean package -DskipTests               # 先打包 jar
docker build -t myapp:1.0 .                 # 构建镜像
docker run -d -p 8080:8080 --name myapp myapp:1.0  # 运行容器
```

### 验证方法

```bash
docker logs myapp
# 应看到 Spring Boot 启动日志

curl http://localhost:8080/health
# 如果你的应用有 health 端点

docker ps | grep myapp
# 应看到容器在运行
```

---

## 112.5 Docker 分层构建——加速构建

Docker 镜像由多层组成，每一条指令（FROM、COPY、RUN 等）创建一层。层会被缓存：如果某一层没变，后续构建直接复用。

### 优化版 Dockerfile

```dockerfile
FROM eclipse-temurin:21-jre-alpine

WORKDIR /app

# 先复制 pom.xml 和源码，在容器内编译
# 方案一：多阶段构建（推荐）
FROM eclipse-temurin:21-jdk-alpine AS builder
WORKDIR /workspace
COPY pom.xml .
COPY src src
RUN ./mvnw package -DskipTests

FROM eclipse-temurin:21-jre-alpine
WORKDIR /app
COPY --from=builder /workspace/target/*.jar app.jar
EXPOSE 8080
ENTRYPOINT ["java", "-jar", "app.jar"]
```

> 💡 Maven Wrapper（`mvnw`）让你不安装 Maven 也能构建项目。如果项目里没有，执行 `mvn wrapper:wrapper` 生成。

### 实用版（构建+小镜像）

```dockerfile
FROM eclipse-temurin:21-jdk-alpine AS builder
WORKDIR /app
COPY . .
RUN ./mvnw clean package -DskipTests

FROM eclipse-temurin:21-jre-alpine
WORKDIR /app
COPY --from=builder /app/target/*.jar app.jar
RUN addgroup -S appgroup && adduser -S appuser -G appgroup
USER appuser
EXPOSE 8080
ENTRYPOINT ["java", "-jar", "app.jar"]
```

> 🔒 `USER appuser` 确保容器内的进程不以 root 运行，这是安全最佳实践。

---

## 112.6 docker-compose——一键启动全家桶

### 你在做什么？
你的 Spring Boot 应用依赖 MySQL 和 Redis。你要一条命令同时启动这三个服务。

### docker-compose.yml

在项目根目录创建：

```yaml
version: '3.8'

services:
  mysql:
    image: mysql:8.0
    container_name: app-mysql
    restart: always
    environment:
      MYSQL_ROOT_PASSWORD: your_root_password_here
      MYSQL_DATABASE: myapp
      MYSQL_USER: appuser
      MYSQL_PASSWORD: your_app_password_here
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql
      - ./sql/init.sql:/docker-entrypoint-initdb.d/init.sql
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    container_name: app-redis
    restart: always
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  app:
    build: .
    container_name: app-server
    restart: always
    ports:
      - "8080:8080"
    environment:
      SPRING_DATASOURCE_URL: jdbc:mysql://mysql:3306/myapp?useSSL=false&allowPublicKeyRetrieval=true
      SPRING_DATASOURCE_USERNAME: appuser
      SPRING_DATASOURCE_PASSWORD: your_app_password_here
      SPRING_DATA_REDIS_HOST: redis
    depends_on:
      mysql:
        condition: service_healthy
      redis:
        condition: service_healthy

volumes:
  mysql_data:
  redis_data:
```

### 操作

```bash
docker compose up -d             # 启动所有服务（后台）
docker compose ps                # 查看各服务状态
docker compose logs -f app       # 查看 app 服务日志
docker compose down              # 停止并删除所有服务
docker compose down -v           # 同时删除数据卷（数据会丢失！）
docker compose restart app       # 只重启 app 服务
```

### 验证方法

```bash
docker compose up -d
# 等待所有服务启动（第一次可能较慢，因为要下载镜像）
docker compose ps
# 所有服务 State 应为 "Up" 或 "healthy"

curl http://localhost:8080/health
# 应返回健康检查结果
```

---

## 112.7 常用 Docker 调试技巧

```bash
# 查看容器日志（最近100行）
docker logs --tail 100 app-server

# 进入运行中的容器
docker exec -it app-server sh

# 查看容器资源使用
docker stats

# 清理无用的镜像和容器
docker system prune -a

# 查看镜像的层
docker history myapp:1.0

# 从容器创建镜像（调试用）
docker commit <container_id> debug-image:latest
```

---

## 112.8 完成效果

学完本章，你应该能：
1. 用自己的 Spring Boot 项目写出 Dockerfile 并构建镜像
2. 用 `docker run` 启动和管理容器
3. 用 docker-compose 编排 Spring Boot + MySQL + Redis 全家桶
4. 进入容器内部排查问题

---

## 小结

| 知识点 | 核心命令/文件 |
|--------|---------------|
| Docker 安装 | `docker run hello-world` 验证 |
| 镜像管理 | `docker pull`, `docker images`, `docker rmi` |
| 容器生命周期 | `docker run`, `docker stop/start/restart/rm` |
| 日志与调试 | `docker logs -f`, `docker exec -it` |
| 构建镜像 | `docker build -t name:tag .` |
| 镜像描述文件 | `Dockerfile`（FROM → WORKDIR → COPY → ENTRYPOINT） |
| 多阶段构建 | `FROM ... AS builder` + `COPY --from=builder` |
| 服务编排 | `docker-compose.yml` + `docker compose up -d` |

---

## 自测题

1. Dockerfile 中 `ENTRYPOINT` 和 `CMD` 的区别是什么？
2. 你用 `docker run -d -p 9090:8080 myapp` 启动了容器，在宿主机浏览器访问哪个端口？
3. docker-compose.yml 中 `depends_on` 能保证 MySQL 准备好接受连接吗？如果不能，怎么解决？

<details>
<summary>点击查看答案</summary>

1. `ENTRYPOINT` 定义容器的主命令（不可被 `docker run` 后面的参数覆盖）；`CMD` 提供默认参数，可以被覆盖。两者配合时，CMD 作为 ENTRYPOINT 的默认参数。
2. 访问 `http://localhost:9090`。`-p 9090:8080` 表示宿主机 9090 映射到容器内 8080。
3. `depends_on` 只保证容器启动顺序，不保证内部服务就绪。解决方案：使用 `healthcheck` + `condition: service_healthy`（如本章示例），或在应用启动脚本中加入重试逻辑。
</details>