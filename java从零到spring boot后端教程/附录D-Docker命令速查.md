# 附录D · Docker常用命令速查

> "Docker把应用和它的所有依赖打包成一个集装箱——在任何安装了Docker的机器上都能运行，不会出现'我机器上能跑啊'的问题。本附录覆盖镜像、容器、网络、数据卷和docker-compose的常用命令。"

---

## D.1 镜像（Image）

镜像就像程序的模板——它包含了代码、运行时、系统库、环境变量等一切运行所需的东西。它是只读的，不能修改。

| 命令 | 作用 |
|------|------|
| `docker images` | 列出本地镜像 |
| `docker pull image:tag` | 从仓库拉取镜像 |
| `docker build -t name:tag .` | 从Dockerfile构建镜像 |
| `docker tag source target` | 给镜像打标签 |
| `docker push image:tag` | 推送到仓库 |
| `docker rmi image:tag` | 删除镜像 |
| `docker rmi -f image:tag` | 强制删除镜像 |
| `docker save -o file.tar image:tag` | 导出镜像为tar |
| `docker load -i file.tar` | 从tar导入镜像 |
| `docker image prune` | 清理无标签镜像 |
| `docker image prune -a` | 清理所有未使用镜像 |
| `docker history image:tag` | 查看镜像构建历史 |

### Dockerfile常用指令 — Java项目示例

```dockerfile
FROM eclipse-temurin:21-jdk-alpine AS builder
WORKDIR /app
COPY pom.xml .
COPY src ./src
RUN ./mvnw package -DskipTests

FROM eclipse-temurin:21-jre-alpine
WORKDIR /app
COPY --from=builder /app/target/*.jar app.jar
EXPOSE 8080
ENTRYPOINT ["java", "-jar", "app.jar"]
```

| 指令 | 作用 |
|------|------|
| `FROM` | 基础镜像 |
| `WORKDIR` | 工作目录 |
| `COPY src dst` | 复制文件 |
| `ADD src dst` | 复制+自动解压tar和URL |
| `RUN command` | 构建时执行命令 |
| `CMD ["exec"]` | 容器启动时的默认命令 |
| `ENTRYPOINT ["exec"]` | 容器入口点（不易被覆盖） |
| `ENV key=value` | 环境变量 |
| `EXPOSE port` | 声明端口（文档作用） |
| `VOLUME /path` | 声明挂载点 |
| `USER user` | 切换用户 |
| `ARG name` | 构建参数 |

---

## D.2 容器（Container）

容器是镜像的运行实例——就像根据模板（镜像）造出来的一个正在运行的沙盒。

### 生命周期

| 命令 | 作用 |
|------|------|
| `docker run -d --name xxx image` | 后台运行容器 |
| `docker run -it image sh` | 交互运行 |
| `docker run -p 8080:8080 image` | 端口映射（主机:容器） |
| `docker run -v /host:/container image` | 挂载数据卷 |
| `docker run -e KEY=VALUE image` | 设置环境变量 |
| `docker run --restart=always image` | 自动重启 |
| `docker run --network=net image` | 指定网络 |
| `docker start container` | 启动已停止容器 |
| `docker stop container` | 停止容器 |
| `docker restart container` | 重启容器 |
| `docker rm container` | 删除容器 |
| `docker rm -f container` | 强制删除（运行中也可删） |

### 查看与日志

| 命令 | 作用 |
|------|------|
| `docker ps` | 列出运行中的容器 |
| `docker ps -a` | 列出所有容器（含已停止） |
| `docker logs container` | 查看日志 |
| `docker logs -f container` | 实时跟踪日志 |
| `docker logs --tail 100 container` | 查看最近100行 |
| `docker inspect container` | 查看容器详细信息 |
| `docker stats` | 实时监控资源使用 |
| `docker top container` | 查看容器内进程 |
| `docker port container` | 查看端口映射 |

### 交互

| 命令 | 作用 |
|------|------|
| `docker exec -it container sh` | 进入容器执行命令 |
| `docker exec container command` | 在容器内执行命令 |
| `docker cp src dst` | 容器与主机间复制文件 |
| `docker diff container` | 查看文件变更 |

### 清理

| 命令 | 作用 |
|------|------|
| `docker container prune` | 清理已停止容器 |
| `docker system prune -a` | 清理所有未使用资源 |

---

## D.3 网络（Network）

| 命令 | 作用 |
|------|------|
| `docker network ls` | 列出网络 |
| `docker network create name` | 创建网络 |
| `docker network rm name` | 删除网络 |
| `docker network connect net container` | 容器接入网络 |
| `docker network disconnect net container` | 容器断开网络 |
| `docker network inspect name` | 查看网络详情 |

### 网络模式

| 模式 | 说明 |
|------|------|
| `bridge` | 默认模式，容器间通过docker0网桥通信 |
| `host` | 与宿主机共享网络栈 |
| `none` | 无网络 |
| `overlay` | 跨主机网络（Swarm模式） |

---

## D.4 数据卷（Volume）

数据卷是容器间共享和持久化数据的方式——容器删了数据还在。

| 命令 | 作用 |
|------|------|
| `docker volume ls` | 列出数据卷 |
| `docker volume create name` | 创建数据卷 |
| `docker volume rm name` | 删除数据卷 |
| `docker volume inspect name` | 查看数据卷详情 |
| `docker volume prune` | 清理未使用数据卷 |

### 挂载类型

```bash
docker run -v named_volume:/data image
docker run -v /host/path:/container/path image
docker run --mount type=bind,src=/host,dst=/container image
```

---

## D.5 Docker Compose

Docker Compose用YAML文件定义和管理多容器应用。

### docker-compose.yml 模板 — Java项目

```yaml
services:
  app:
    build: .
    ports:
      - "8080:8080"
    depends_on:
      - db
      - redis
    environment:
      SPRING_DATASOURCE_URL: jdbc:mysql://db:3306/mydb
      SPRING_REDIS_HOST: redis
    volumes:
      - ./uploads:/app/uploads

  db:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: your_password_here
      MYSQL_DATABASE: mydb
    ports:
      - "3306:3306"
    volumes:
      - db_data:/var/lib/mysql

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

volumes:
  db_data:
```

### Compose命令

| 命令 | 作用 |
|------|------|
| `docker-compose up` | 启动所有服务 |
| `docker-compose up -d` | 后台启动 |
| `docker-compose up --build` | 重新构建并启动 |
| `docker-compose down` | 停止并删除容器 |
| `docker-compose down -v` | 同时删除数据卷 |
| `docker-compose ps` | 查看服务状态 |
| `docker-compose logs -f service` | 查看服务日志 |
| `docker-compose exec service sh` | 进入容器 |
| `docker-compose restart service` | 重启单个服务 |
| `docker-compose stop service` | 停止单个服务 |
| `docker-compose rm service` | 删除已停止服务 |
| `docker-compose build` | 构建镜像 |
| `docker-compose pull` | 拉取最新镜像 |

> **注意**：Docker Compose V2中改为 `docker compose`（无连字符），如 `docker-compose` 报错请用 `docker compose`。

---

## D.6 多阶段构建示例 — Java应用

```dockerfile
FROM eclipse-temurin:21-jdk-alpine AS builder
WORKDIR /app
COPY pom.xml .
COPY src ./src
RUN ./mvnw package -DskipTests

FROM eclipse-temurin:21-jre-alpine
RUN apk add --no-cache curl
WORKDIR /app
COPY --from=builder /app/target/*.jar app.jar
HEALTHCHECK --interval=30s --timeout=3s --retries=3 \
  CMD curl -f http://localhost:8080/actuator/health || exit 1
EXPOSE 8080
ENTRYPOINT ["java", "-Xmx256m", "-jar", "app.jar"]
```

---

Docker是现代后端开发的标配技能。掌握镜像构建、容器管理、Compose编排这三块，就能应对日常开发中的所有容器化需求。

---

[← 上一章：附录C-Redis命令速查.md](附录C-Redis命令速查/) | [下一章：附录E-Git命令速查.md →](附录E-Git命令速查/)