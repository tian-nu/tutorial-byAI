# 第102章 · Docker容器化

> "你在本地跑得好好的Go程序，到了服务器上就不行了——Go版本不对、缺少系统库、配置文件路径不一样……这种'环境不一致'问题是软件工程领域的古老噩梦。Docker（应用容器引擎，详见附录I）用一个天才的思路解决了它：把代码和它依赖的一切（操作系统、运行时、库、配置）全部打包成一个标准化的'集装箱'，在任何地方都能以完全相同的方式运行。"

---

## 102.1 为什么需要Docker

### 古老的环境不一致问题

没有Docker时，部署一个Go应用的典型灾难流程：

1. 开发说"我本地跑得好好的啊"
2. 运维说"你服务器不是Ubuntu 22.04，是CentOS 7"
3. 开发说"那装Go 1.22啊"
4. 运维说"CentOS 7仓库里的Go版本太老了，只能手动装"
5. 装了Go 1.22，又缺 `libc` 的某个版本
6. 搞了三个小时终于跑起来了，结果下个应用又需要Go 1.20
7. ……（此处省略一万句脏话）

### Docker的解决方案

Docker说：开发把**整个运行环境**（不只是代码）打包发给我。运维只需要运行这个包，什么都不用装。

就像一个**搬家**的比喻：
- 传统方式：你告诉搬家公司"把我的家具搬过去"，但新房子格局不一样，有些家具塞不进去
- Docker方式：你把整套房子（包括里面的所有东西）打包成一个**集装箱**，搬到任何地方原样放下来就能住

---

## 102.2 核心比喻：集装箱系统

### 镜像 = 集装箱

**镜像（Image，打包应用和环境的只读模板，详见附录I）**是一个只读模板，包含了运行应用所需的一切：操作系统文件、依赖库、你的代码、配置文件。它就像一个装满了东西的密封集装箱——你可以在任何码头装卸它。

### 容器 = 装着集装箱正在运行的船

**容器（Container，镜像的运行实例，详见附录I）**是镜像的**运行实例**。一个镜像可以启动多个容器，就像同一个集装箱模板可以装到很多条船上。

容器运行时，Docker引擎在宿主机上加了一层薄薄的隔离（namespace/cgroups），让每个容器以为自己独占一台机器——但实际上所有容器共享同一个Linux内核。

### 仓库 = 集装箱码头

**仓库（Registry）**是存放和分发镜像的地方。Docker Hub是最大的公共码头，你的私有码头可以是阿里云容器镜像服务、AWS ECR等。

```
你的电脑                  服务器
    │                       │
    │ docker build          │ docker pull
    ▼                       ▼
 镜像(tag)  ──docker push──> Docker Hub ──docker pull──> 镜像(tag)
    │                                                       │
    │ docker run                                            │ docker run
    ▼                                                       ▼
 容器A                      容器B                   容器C
 (开发环境)                (测试环境)               (生产环境)
```

### 🤔 想多一点：Docker和虚拟机的区别

| | Docker容器 | 虚拟机(VM) |
|---|---|---|
| 虚拟化层级 | 操作系统层 | 硬件层 |
| 启动速度 | 秒级 | 分钟级 |
| 占用空间 | MB级 | GB级 |
| 性能损耗 | 几乎无（~2%） | 较高（~10-15%） |
| 隔离性 | 较弱（共享内核） | 强（完全隔离） |
| 每个实例含OS | 否（共享宿主机内核） | 是（完整Guest OS） |

一句话：VM是**给每个应用单独盖一栋楼**，每栋楼有自己的水电系统。Docker是**在同一个大仓库里用隔板分出不同区域**，水电共用。

---

## 102.3 镜像 vs 容器

### 镜像：只读模板

镜像是分层的。每条Dockerfile指令创建一个新的层（layer）：

```
基础层: ubuntu:22.04 (80MB)
  └─ 层1: RUN apt-get install ca-certificates (2MB)
      └─ 层2: COPY myapp /app/myapp (15MB)
          └─ 层3: CMD ["/app/myapp"] (0B)
```

镜像分层的好处：如果两个镜像都基于 `ubuntu:22.04`，Docker只需要下载一次基础层。如果只是代码变了，重新构建时只需要重建最上面的层——下面的层都在缓存里。

### 容器：运行实例 = 镜像 + 可写层

启动容器时，Docker在镜像的只读层上面加了一层**可写层**（container layer）。容器中对文件的所有修改只发生在这层可写层上——镜像本身不变。

这就是为什么：
- 容器删了，里面的所有修改都没了（可写层被销毁）
- 从同一个镜像启动的容器，初始状态完全一样
- 如果要在多个容器间共享数据，需要**卷（Volume）**——把宿主机的某个目录挂载到容器里

---

## 102.4 基本命令

### 镜像操作

```bash
docker images                        # 列出本地所有镜像
docker pull golang:1.22-alpine       # 从仓库拉取镜像
docker rmi golang:1.22-alpine        # 删除镜像
docker tag myapp:latest myapp:v1.0   # 给镜像打标签
docker build -t myapp:latest .       # 从Dockerfile构建镜像
```

### 容器操作

```bash
docker run -d -p 8080:8080 --name myapp myapp:latest
docker ps                            # 查看正在运行的容器
docker ps -a                         # 查看所有容器（含已停止的）
docker stop myapp                    # 停止容器
docker start myapp                   # 启动已停止的容器
docker restart myapp                 # 重启容器
docker rm myapp                      # 删除容器
docker rm -f myapp                   # 强制删除（即使正在运行）
docker exec -it myapp /bin/sh        # 进入容器内部执行命令
docker logs myapp                    # 查看容器日志
docker logs -f myapp                 # 实时跟踪日志
docker logs --tail 100 myapp         # 查看最近100行
docker cp myapp:/app/config.yaml .   # 从容器复制文件出来
```

### docker run 参数详解

```bash
docker run \
  -d \                    # 后台运行（detached mode）
  -p 8080:8080 \          # 端口映射：宿主机端口:容器端口
  -p 9090:9090 \          # 可以映射多个端口
  --name myapp \          # 容器名称
  --restart always \      # 自动重启策略
  -e DB_HOST=mysql \      # 设置环境变量
  -e DB_PASSWORD=secret \
  -v /data:/app/data \    # 挂载卷：宿主机路径:容器路径
  --memory 512m \         # 限制内存使用
  --cpus 1.0 \            # 限制CPU使用
  myapp:latest            # 使用的镜像及其标签
```

`-d` vs 不加 `-d`：不加 `-d` 时，容器的输出会直接打印在你的终端上，Ctrl+C会停止容器。加 `-d` 后容器在后台默默运行。

---

## 102.5 Dockerfile编写

Dockerfile是一个文本文件，描述如何构建镜像。每一条指令创建一个新的层。

### 所有指令详解

**FROM**：指定基础镜像。每个Dockerfile必须以FROM开头。

```dockerfile
FROM golang:1.22-alpine
```

**WORKDIR**：设置工作目录。之后所有的 `RUN`、`COPY`、`CMD` 都相对于这个目录。

```dockerfile
WORKDIR /app
```

**COPY**：从宿主机（构建上下文）复制文件到镜像中。

```dockerfile
COPY go.mod go.sum ./
COPY . .
```

**ADD**：和COPY类似，但有额外功能：自动解压tar文件、支持URL下载。一般推荐用COPY（更透明），除非你需要自动解压功能。

```dockerfile
ADD config.tar.gz /app/config/
```

**RUN**：在镜像构建时执行命令。常用来安装依赖、编译代码。

```dockerfile
RUN go mod download
RUN go build -o myapp ./cmd/api/
```

**CMD**：容器启动时默认执行的命令。如果 `docker run` 后面指定了命令，CMD会被覆盖。一个Dockerfile只有一个CMD生效。

```dockerfile
CMD ["./myapp"]
```

**ENTRYPOINT**：容器启动时的入口命令。和CMD的区别：ENTRYPOINT不会被 `docker run` 后的参数覆盖，那些参数会作为ENTRYPOINT的追加参数。

```dockerfile
ENTRYPOINT ["./myapp"]
CMD ["--port=8080"]          # CMD作为ENTRYPOINT的默认参数
```

此时 `docker run myapp --port=9090` 会执行 `./myapp --port=9090`。

**ENV**：设置环境变量。在构建和运行时都可用。

```dockerfile
ENV APP_ENV=production
ENV DB_HOST=mysql
```

**EXPOSE**：声明容器运行时监听的端口。这只是一个注释（文档作用），并不实际发布端口。真正发布端口靠 `docker run -p`。

```dockerfile
EXPOSE 8080
```

**ARG**：构建时参数。只在构建阶段有效，不会进入最终镜像。

```dockerfile
ARG VERSION=1.0.0
RUN echo "Building version ${VERSION}"
```

构建时传入：`docker build --build-arg VERSION=2.0.0 -t myapp .`

**VOLUME**：创建挂载点。声明容器中的某个目录应该作为卷。

```dockerfile
VOLUME ["/app/data"]
```

---

## 102.6 多阶段构建

Go编译出的二进制文件是**静态链接**的，不依赖系统库。这意味着：编译需要Go SDK（几百MB），但运行只需要那个十几MB的二进制文件。

多阶段构建（Multi-stage Build）利用这一点：**在一个阶段编译，在另一个阶段运行**，最终镜像只包含运行阶段的内容——体积极小。

### 为什么多阶段构建能减小镜像

```
单阶段构建:
  基础镜像(golang:1.22)  800MB
  + 源代码                50MB
  + 编译产物(myapp)       15MB
  = 最终镜像              865MB ← 包含整个Go工具链，浪费！

多阶段构建:
  构建阶段:
    基础镜像(golang:1.22) 800MB（仅构建时用）
    + 编译产物(myapp)      15MB
  运行阶段:
    基础镜像(alpine:3.19)  7MB
    + 编译产物(myapp)      15MB ← 从构建阶段复制过来
  = 最终镜像               22MB ← 只含二进制+最轻量的OS
```

865MB → 22MB，缩减了97%！这不仅是节省磁盘空间——更快的下载速度、更快的启动速度、更小的攻击面。

### 多阶段Dockerfile示例

```dockerfile
FROM golang:1.22-alpine AS builder

WORKDIR /app

RUN apk add --no-cache git ca-certificates

COPY go.mod go.sum ./
RUN go mod download

COPY . .

RUN CGO_ENABLED=0 GOOS=linux go build -ldflags="-s -w" -o myapp ./cmd/api/

FROM alpine:3.19

RUN apk add --no-cache ca-certificates tzdata

WORKDIR /app

COPY --from=builder /app/myapp .
COPY --from=builder /app/config.yaml .

RUN adduser -D -H -s /sbin/nologin appuser
USER appuser

EXPOSE 8080

CMD ["./myapp"]
```

**逐行解释：**

1. `FROM golang:1.22-alpine AS builder`：构建阶段，使用Go的官方Alpine镜像，命名为 `builder`
2. `RUN apk add --no-cache git ca-certificates`：Alpine用 `apk` 作为包管理器，安装Git和CA证书
3. 先复制 `go.mod` 和 `go.sum`，再 `go mod download`——利用Docker层缓存，只要依赖不变就不用重新下载
4. `CGO_ENABLED=0`：禁用CGO，生成纯静态二进制
5. `-ldflags="-s -w"`：去除调试信息，减小二进制文件大小
6. `FROM alpine:3.19`：运行阶段，用最轻量的Linux发行版（只有约7MB）
7. `COPY --from=builder /app/myapp .`：从构建阶段的镜像中复制编译产物
8. `adduser`：创建非root用户，安全最佳实践
9. `USER appuser`：切换到非root用户运行

### 🤔 想多一点：为什么不用scratch？

`scratch` 是Docker的空镜像——里面什么都没有，连 `/bin/sh` 都没有。一个纯静态的Go二进制可以用 `FROM scratch`，最终镜像只有二进制的大小（约5-15MB）。

为什么不推荐给新手？
1. 没有shell，无法 `docker exec` 进去排查
2. 没有CA证书，HTTPS请求会失败
3. 没有时区数据，时间显示UTC而非本地时区

所以推荐用 `alpine`：7MB的代价换来一个完整的Linux基本环境，排查问题方便得多。等你对整个部署流程烂熟于心后，再考虑 `scratch`。

---

## 102.7 Go项目Docker化完整示例

### Step 1：创建.dockerignore

`.dockerignore` 告诉Docker在构建时忽略哪些文件（减少构建上下文大小，提高构建速度）：

```
.git
.gitignore
README.md
*.md
.idea/
.vscode/
docker-compose.yml
**/*_test.go
```

### Step 2：编写Dockerfile

使用上面的多阶段构建Dockerfile。

### Step 3：构建镜像

```bash
docker build -t myapp:latest .
docker build -t myapp:v1.0.0 .
docker build -t myapp:latest --no-cache .   # 不使用缓存，完全重新构建
```

### Step 4：本地运行测试

```bash
docker run -d -p 8080:8080 --name myapp-dev \
  -e DB_HOST=host.docker.internal \
  myapp:latest
```

`host.docker.internal` 是Docker提供的特殊DNS名，指向宿主机。如果你的数据库跑在宿主机上而不是容器里，就用这个连接。

### Step 5：推送到镜像仓库

```bash
docker tag myapp:latest username/myapp:latest
docker push username/myapp:latest
```

---

## 102.8 docker-compose：编排多容器应用

真实应用不是孤立的——一个Go服务通常需要MySQL、Redis、可能还有Nginx。docker-compose让你在一个文件中定义所有这些服务，一条命令全部启动。

### docker-compose.yml完整示例

```yaml
version: "3.8"

services:
  api:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: myapp_api
    ports:
      - "8080:8080"
    environment:
      APP_ENV: production
      DB_HOST: mysql
      DB_PORT: "3306"
      DB_USER: myapp
      DB_PASSWORD: secret123
      DB_NAME: myapp
      REDIS_ADDR: redis:6379
    depends_on:
      mysql:
        condition: service_healthy
      redis:
        condition: service_started
    restart: unless-stopped
    volumes:
      - ./uploads:/app/uploads
    networks:
      - app_network

  mysql:
    image: mysql:8.0
    container_name: myapp_mysql
    environment:
      MYSQL_ROOT_PASSWORD: rootsecret
      MYSQL_DATABASE: myapp
      MYSQL_USER: myapp
      MYSQL_PASSWORD: secret123
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - app_network

  redis:
    image: redis:7-alpine
    container_name: myapp_redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes
    networks:
      - app_network

volumes:
  mysql_data:
  redis_data:

networks:
  app_network:
    driver: bridge
```

**关键配置解释：**

- `depends_on` + `condition: service_healthy`：api服务会等MySQL的健康检查通过后才启动。没有这个的话，api可能在数据库还没就绪时就尝试连接，导致启动失败。
- `healthcheck`：MySQL的 `mysqladmin ping` 确认数据库真正可用了（不只是进程启动了）。
- `volumes: mysql_data:/var/lib/mysql`：命名卷持久化MySQL数据。即使容器被删除，数据还在。
- `networks: app_network`：自定义网络，容器间可以用服务名（如 `mysql`、`redis`）互相访问——Docker内置了DNS解析。
- `restart: unless-stopped`：容器意外退出时自动重启，只有手动 `docker stop` 后才不重启。

### docker-compose常用命令

```bash
docker-compose up -d               # 后台启动所有服务
docker-compose up -d --build       # 重新构建镜像并启动
docker-compose down                # 停止并删除所有容器
docker-compose down -v             # 同时删除卷（数据会丢！）
docker-compose ps                  # 查看所有服务状态
docker-compose logs -f api         # 实时查看api服务的日志
docker-compose restart api         # 重启单个服务
docker-compose exec api /bin/sh    # 进入api服务的容器
docker-compose build               # 只构建不启动
```

---

## 102.9 常用命令速查表

### 镜像

| 命令 | 说明 |
|------|------|
| `docker images` | 列出本地镜像 |
| `docker pull image:tag` | 拉取镜像 |
| `docker build -t name:tag .` | 构建镜像 |
| `docker tag src dst` | 重命名标签 |
| `docker rmi image` | 删除镜像 |

### 容器

| 命令 | 说明 |
|------|------|
| `docker run -d -p 80:80 --name c image` | 启动容器 |
| `docker ps` | 运行中的容器 |
| `docker ps -a` | 所有容器 |
| `docker stop/start/restart name` | 停止/启动/重启 |
| `docker rm name` | 删除容器 |
| `docker rm -f name` | 强制删除 |
| `docker exec -it name sh` | 进入容器 |
| `docker logs -f name` | 实时日志 |

### Dockerfile指令

| 指令 | 说明 |
|------|------|
| `FROM image` | 基础镜像 |
| `WORKDIR /path` | 工作目录 |
| `COPY src dst` | 复制文件 |
| `RUN cmd` | 构建时执行命令 |
| `CMD ["cmd"]` | 默认启动命令 |
| `ENV KEY=val` | 环境变量 |
| `EXPOSE port` | 声明端口 |
| `USER user` | 切换用户 |

### 最佳实践

| 实践 | 说明 |
|------|------|
| 多阶段构建 | 分离构建和运行，减小镜像 |
| `.dockerignore` | 排除不需要的文件 |
| 非root用户 | 安全：`USER appuser` |
| 层缓存优化 | 先COPY依赖文件，再COPY源码 |
| 健康检查 | 确保依赖服务就绪后再启动 |

---

## 本章小结

| 知识点 | 要点 |
|--------|------|
| Docker本质 | 把代码+环境打包成标准化集装箱，解决环境不一致 |
| 镜像 | 只读模板，分层存储，层间共享 |
| 容器 | 镜像的运行实例 = 只读层 + 可写层 |
| 仓库 | 镜像的存储和分发中心（Docker Hub等） |
| Docker vs VM | Docker共享宿主机内核，启动快、体积小 |
| 基本命令 | run/ps/stop/rm/exec/logs/pull/push/build |
| Dockerfile | FROM/WORKDIR/COPY/RUN/CMD/ENV/EXPOSE |
| CMD vs ENTRYPOINT | CMD可被docker run覆盖，ENTRYPOINT不可 |
| 多阶段构建 | 编译阶段→运行阶段，最终镜像只含二进制 |
| .dockerignore | 减少构建上下文，加速构建 |
| docker-compose | 一条命令管理多容器应用 |
| depends_on + healthcheck | 确保依赖服务就绪后才启动 |
| 命名卷 | 持久化容器数据 |

> 🚀 下一章：第103章 · CI/CD持续集成部署。Docker让部署变得可靠，但每次改代码都要手动 `docker build`、`docker push`、`docker run` 还是太慢了。如果能做到：代码推到GitHub → 自动构建 → 自动测试 → 自动部署到服务器，你只需要 `git push` 一下就行——这就是CI/CD。

---
[← 上一章：101-Git版本控制.md](101-Git版本控制.md) | [下一章：103-CI-CD持续集成部署.md →](103-CI-CD持续集成部署.md)
