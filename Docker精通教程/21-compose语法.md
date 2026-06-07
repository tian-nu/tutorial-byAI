# 21 — compose.yml 语法

> - 对应文档版本：Docker精通教程 outline v1
> - 适用环境：任何已安装 Docker + Docker Compose 的系统
> - 读者角色：已理解 Compose 基本概念，需要掌握 compose.yml 完整语法的开发者
> - 预计耗时：新手 35 分钟 / 熟手 15 分钟
> - 前置教程：第 20 章（Compose 是什么）
> - 可视化：无

---

## 我在做什么？

上一章你写了一个 5 行的 compose.yml，启动了一个 Nginx 容器。但真实项目不可能这么简单——你需要定义数据库、缓存、Web 应用，它们之间需要网络互通、数据持久化、环境变量配置、启动顺序控制。

这一章，我们逐字段拆解 compose.yml 的完整结构。学完之后，你拿到任何一个 compose.yml 文件，都能看懂它在做什么；你也能从零写一个完整的 compose.yml。

学完这一章，你能：
- 理解 compose.yml 的顶层结构：`services`、`volumes`、`networks`
- 掌握每个核心字段的用法和注意事项
- 写出包含 Web + MySQL + Redis 的完整 compose.yml
- 用 `docker compose config` 验证语法

---

## 一、compose.yml 的顶层结构

一个完整的 compose.yml 由三个顶层区块组成：

```yaml
# 顶层结构
services:    # 定义应用的服务（容器）
volumes:     # 定义具名数据卷
networks:    # 定义自定义网络
```

> `services` 是必须的，`volumes` 和 `networks` 是可选的。但实际项目中你几乎总会用到它们。

### 类比：compose.yml 是一栋公寓楼的建筑设计图

- **services** = 每个房间（房间里有谁、做什么工作、用什么家具）
- **networks** = 走廊和楼梯（房间之间怎么互相通行）
- **volumes** = 储藏室（东西放哪，搬家时哪些东西留下）

---

## 二、services 区块详解

`services` 是 compose.yml 的核心。每个服务定义了一个容器（或一组容器）。

### 2.1 `image`：指定镜像

```yaml
services:
  web:
    image: nginx:alpine      # 从 Docker Hub 拉取 nginx:alpine 镜像
  db:
    image: mysql:8.0          # 从 Docker Hub 拉取 mysql:8.0 镜像
  custom:
    image: my-registry.com/my-app:v1.2.3  # 从私有仓库拉取
```

`image` 的格式和 `docker pull` 一样：`[仓库地址/]镜像名[:标签]`。

### 2.2 `build`：从 Dockerfile 构建

如果你不想用现成的镜像，而是从 Dockerfile 构建：

```yaml
services:
  web:
    build: .                  # 用当前目录的 Dockerfile 构建
    # 等价于：docker build -t web .
```

更完整的写法：

```yaml
services:
  web:
    build:
      context: ./app          # Dockerfile 所在的目录（构建上下文）
      dockerfile: Dockerfile.prod  # 指定 Dockerfile 文件名（默认是 Dockerfile）
      args:                   # 构建参数（对应 Dockerfile 里的 ARG）
        NODE_ENV: production
        APP_VERSION: "1.2.3"
```

`image` 和 `build` 可以同时出现：

```yaml
services:
  web:
    build: .
    image: myapp:v1           # 构建后给镜像打上这个标签
```

> 如果只写 `build` 不写 `image`，Compose 会自动生成一个镜像名（格式：`项目名-服务名`）。

### 2.3 `ports`：端口映射

```yaml
services:
  web:
    image: nginx:alpine
    ports:
      - "8080:80"             # 宿主机 8080 → 容器 80
      - "443:443"             # 可以映射多个端口
```

三种写法：

```yaml
# 写法 1：字符串（推荐，最直观）
ports:
  - "8080:80"

# 写法 2：对象（需要指定协议时）
ports:
  - target: 80                # 容器端口
    published: 8080           # 宿主机端口
    protocol: tcp             # 默认 tcp，可选 udp

# 写法 3：只写容器端口（宿主机随机分配端口）
ports:
  - "3000"                    # 等价于 docker run -P
```

> **注意**：`ports` 的值格式是 `"宿主机端口:容器端口"`，不是 `"容器端口:宿主机端口"`。这和 `docker run -p` 的格式一致——先写外面，再写里面。记住口诀：**"外面→里面"**。

### 2.4 `volumes`：数据卷

在 services 里，`volumes` 有两种用途：

**用途 A：挂载具名卷（数据持久化）**

```yaml
services:
  db:
    image: mysql:8.0
    volumes:
      - mysql-data:/var/lib/mysql   # 具名卷:容器路径
```

**用途 B：挂载主机目录（开发时热更新）**

```yaml
services:
  web:
    build: .
    volumes:
      - ./src:/app/src          # 主机目录:容器路径（开发时用）
      - ./config:/app/config:ro # :ro 表示只读
```

> 用途 A 对标 `docker volume create` + `docker run -v`。用途 B 对标 `docker run -v $(pwd)/src:/app/src`。

**长格式写法**（需要更多控制时）：

```yaml
volumes:
  - type: volume               # 类型：volume（具名卷）或 bind（主机目录）
    source: mysql-data         # 卷名或主机路径
    target: /var/lib/mysql     # 容器内路径
  - type: bind
    source: ./logs
    target: /var/log/app
    read_only: true
```

### 2.5 `environment`：环境变量

```yaml
services:
  web:
    image: myapp:v1
    environment:
      NODE_ENV: production
      DATABASE_URL: mysql://db:3306/myapp
      REDIS_URL: redis://cache:6379
```

两种写法：

```yaml
# 写法 1：字典（推荐，最直观）
environment:
  NODE_ENV: production
  PORT: "3000"

# 写法 2：数组（和 docker run -e 类似）
environment:
  - NODE_ENV=production
  - PORT=3000
```

> **安全提醒**：不要在 compose.yml 里硬编码密码。用 `.env` 文件 + 变量替换（第 24 章会讲）。

### 2.6 `depends_on`：服务依赖

```yaml
services:
  web:
    build: .
    depends_on:
      - db
      - cache

  db:
    image: mysql:8.0

  cache:
    image: redis:7-alpine
```

`depends_on` 只做一件事：**控制启动顺序**。上面这个配置保证：`docker compose up` 时，先启动 `db` 和 `cache`，再启动 `web`。

**但！`depends_on` 不等服务就绪！**

这是 Docker Compose 最大的坑之一。`depends_on` 只是"等容器启动了"，不是"等容器里的服务可用了"。MySQL 容器启动了，但 MySQL 数据库还在初始化（可能需要 10-30 秒），你的 Web 应用就已经尝试连接了——结果连接失败。

```
时间线：
  T0: db 容器启动 ✓
  T1: cache 容器启动 ✓
  T2: web 容器启动 ✓（depends_on 满足了，三个容器都启动了）
  T3: db 容器里的 MySQL 还在初始化...（innodb 日志、用户表、数据库...）
  T4: web 应用尝试连接 MySQL → 失败！MySQL 还没准备好！
```

**解决方案：`healthcheck` + `depends_on` 的 `condition`**

```yaml
services:
  web:
    build: .
    depends_on:
      db:
        condition: service_healthy   # 等 db 的 healthcheck 通过才启动 web
      cache:
        condition: service_started   # 等 cache 容器启动即可（Redis 启动快）

  db:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: your_password
      MYSQL_DATABASE: myapp
    healthcheck:                     # 健康检查
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
      interval: 10s
      timeout: 5s
      retries: 5

  cache:
    image: redis:7-alpine
```

`condition` 有三种：
- `service_started`：容器启动了就行（默认行为）
- `service_healthy`：容器的 healthcheck 通过了才算
- `service_completed_successfully`：容器执行完毕且退出码为 0（适合一次性任务）

> `condition: service_healthy` 需要 Compose v2.1+ 版本。旧版 `docker-compose`（独立 Python 包）不支持。

### 2.7 `restart`：重启策略

```yaml
services:
  web:
    image: nginx:alpine
    restart: unless-stopped    # 除非手动 stop，否则总是重启
```

可选值：

| 值 | 行为 |
|----|------|
| `no` | 不自动重启（默认） |
| `always` | 无论什么原因退出，都重启 |
| `on-failure` | 仅当退出码非 0 时重启 |
| `unless-stopped` | 除非手动 `docker stop`，否则重启（推荐） |

> `unless-stopped` 是最常用的生产环境配置：容器崩溃了自动重启，但如果你手动停了它，它就不重启了——这很合理，因为手动停止意味着"我知道我为什么停它"。

### 2.8 `networks`：自定义网络

在 services 里指定网络：

```yaml
services:
  web:
    build: .
    networks:
      - frontend
      - backend

  db:
    image: mysql:8.0
    networks:
      - backend    # db 只在 backend 网络上，外部无法直接访问
```

这个配置的效果是：`web` 可以同时访问 `frontend` 和 `backend` 两个网络，`db` 只在 `backend` 网络上。前端请求通过 `web` 访问 `db`，外部无法直接连 `db`——这就实现了网络隔离。

> 如果你不在 services 里指定 `networks`，Compose 会自动把所有服务放进一个默认网络（`项目名_default`）。在这个默认网络里，所有服务可以通过服务名互相访问。

---

## 三、volumes 顶层区块（声明具名卷）

在 services 里用了 `- mysql-data:/var/lib/mysql`，就**必须**在顶层 `volumes` 里声明 `mysql-data`：

```yaml
services:
  db:
    image: mysql:8.0
    volumes:
      - mysql-data:/var/lib/mysql

volumes:
  mysql-data:           # 声明具名卷（必须和 services 里引用的名字一致）
    # driver: local     # 默认就是 local，可以不写
```

如果你在 services 里引用了一个未声明的卷，Compose 会自动创建它（不会报错）。但显式声明的好处是：你可以配置卷的驱动、标签、外部来源等。而且同行读你的 compose.yml 时，一眼就知道有哪些持久化数据。

---

## 四、networks 顶层区块（声明自定义网络）

```yaml
services:
  web:
    networks:
      - frontend
      - backend

networks:
  frontend:
    driver: bridge        # 默认就是 bridge，可以不写
  backend:
    driver: bridge
```

如果不声明，Compose 会自动创建一个默认网络。**显式声明的好处**：你可以控制网络驱动、子网、网关等。

一个更完整的网络配置：

```yaml
networks:
  backend:
    driver: bridge
    ipam:
      config:
        - subnet: 172.28.0.0/16
          gateway: 172.28.0.1
```

> 大多数场景你不需要这么细粒度的网络配置。Compose 的默认网络配置已经够用了。除非你有特殊的网络隔离需求（比如某些服务必须用特定子网），否则声明空网络块就够了。

---

## 五、实战：写一个完整的 compose.yml（Web + MySQL + Redis）

现在我们把所有知识点串起来，写一个真实项目可用的 compose.yml。

### 项目结构

```
my-app/
├── compose.yml
├── Dockerfile           # Web 应用的 Dockerfile
├── package.json
├── server.js
└── .dockerignore
```

### compose.yml（完整版）

```yaml
# compose.yml — Web + MySQL + Redis 完整配置
services:
  # ===== Web 应用 =====
  web:
    build:
      context: .
      dockerfile: Dockerfile
    image: myapp:latest
    ports:
      - "3000:3000"
    environment:
      NODE_ENV: production
      DB_HOST: db
      DB_PORT: "3306"
      DB_USER: myapp
      DB_PASSWORD: your_db_password_here
      DB_NAME: myapp
      REDIS_URL: redis://cache:6379
    depends_on:
      db:
        condition: service_healthy
      cache:
        condition: service_started
    restart: unless-stopped
    networks:
      - backend

  # ===== MySQL 数据库 =====
  db:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: your_root_password_here
      MYSQL_DATABASE: myapp
      MYSQL_USER: myapp
      MYSQL_PASSWORD: your_db_password_here
    volumes:
      - mysql-data:/var/lib/mysql
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost", "-u", "root", "-p$$MYSQL_ROOT_PASSWORD"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 30s
    restart: unless-stopped
    networks:
      - backend

  # ===== Redis 缓存 =====
  cache:
    image: redis:7-alpine
    volumes:
      - redis-data:/data
    restart: unless-stopped
    networks:
      - backend

# ===== 数据卷 =====
volumes:
  mysql-data:
  redis-data:

# ===== 网络 =====
networks:
  backend:
    driver: bridge
```

### 逐段讲解

**`web` 服务**：
- `build`：从当前目录的 Dockerfile 构建
- `ports`：宿主机 3000 → 容器 3000
- `environment`：数据库连接信息通过环境变量传入
- `depends_on`：等 `db` 健康检查通过 + `cache` 容器启动后才启动
- `restart: unless-stopped`：崩溃自动重启

**`db` 服务**：
- `healthcheck`：用 `mysqladmin ping` 检查 MySQL 是否真正可用
- `$$MYSQL_ROOT_PASSWORD`：注意是两个 `$` 符号。YAML 里 `$` 是变量替换符号，`$$` 表示字面量 `$`，这样 `$MYSQL_ROOT_PASSWORD` 才会被传递给 shell 去展开
- `start_period: 30s`：MySQL 启动慢，前 30 秒不检查，给初始化时间

**`cache` 服务**：
- Redis 启动极快（通常 1-2 秒），不需要 healthcheck
- `redis-data:/data`：Redis 的 RDB/AOF 持久化文件存在 `/data` 下

---

## 六、我做得对不对？

### 验证方法

```bash
# 1. 检查 YAML 语法
docker compose config
# 如果语法正确，会输出解析后的完整配置（包括默认值）
# 如果语法错误，会报错并指出第几行有问题

# 2. 只检查语法，不输出完整配置
docker compose config -q
# 安静模式：语法正确则无输出，有错误则报错

# 3. 启动（先不 -d，前台看日志）
docker compose up
# 观察各服务的启动日志，确认没有连接错误

# 4. 查看服务状态
docker compose ps
# 预期：三个服务都是 Up 状态

# 5. 检查 db 的健康状态
docker compose ps db
# 预期：STATUS 列显示 "Up (healthy)"

# 6. 查看网络
docker network ls
# 预期：看到 my-app_backend 网络

# 7. 查看数据卷
docker volume ls
# 预期：看到 my-app_mysql-data 和 my-app_redis-data

# 8. 验证 web 可以访问 db
docker compose exec web sh -c "nc -zv db 3306"
# 预期：db (172.x.x.x:3306) open
```

---

## 七、不对怎么办？

### 常见错误 1：YAML 缩进用 Tab

```yaml
# ❌ 错误
services:
	web:           # ← tab 缩进
		image: nginx:alpine
```

```bash
docker compose config
# yaml: line 2: found character that cannot start any token
```

✅ 解决：编辑器设置 YAML 文件用空格缩进。VS Code 右下角点 `Indent Using Spaces`。

### 常见错误 2：`depends_on` 不等服务就绪

```yaml
# ❌ 只写了 depends_on，没写 healthcheck
services:
  web:
    depends_on:
      - db       # 只保证 db 容器先启动，不保证 MySQL 可用
```

现象：`docker compose up` 后，web 容器报 `Connection refused` 或 `Unknown database`。

✅ 解决：

```yaml
services:
  web:
    depends_on:
      db:
        condition: service_healthy

  db:
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
      interval: 10s
      timeout: 5s
      retries: 5
```

### 常见错误 3：healthcheck 里的 `$$` 写成 `$`

```yaml
# ❌ 错误：$MYSQL_ROOT_PASSWORD 被 YAML 当作变量展开
healthcheck:
  test: ["CMD", "mysqladmin", "ping", "-h", "localhost", "-p$MYSQL_ROOT_PASSWORD"]

# ✅ 正确：$$ 转义为字面量 $
healthcheck:
  test: ["CMD", "mysqladmin", "ping", "-h", "localhost", "-p$$MYSQL_ROOT_PASSWORD"]
```

YAML 里 `$VAR` 是变量替换语法。如果你的字符串里包含 `$` 字面量（比如 shell 变量），需要用 `$$` 转义。否则 Compose 会尝试用环境变量替换它——如果环境里没有这个变量，`$MYSQL_ROOT_PASSWORD` 就变成了空字符串，`mysqladmin ping` 的密码就是空的，healthcheck 永远失败。

### 常见错误 4：`volumes` 顶层声明漏了

```yaml
# ❌ 错误：services 里引用了 mysql-data，但顶层没声明
services:
  db:
    volumes:
      - mysql-data:/var/lib/mysql

# 没有 volumes 顶层区块
```

这个错误**不会报错**——Compose 会自动创建未声明的卷。但坏处是：你不知道这个卷的存在，`docker compose down` 时不会自动删除它（即使加了 `-v`），数据残留在你的系统里，一天天积累，最后 `docker volume ls` 一堆无名卷。

✅ 正确：显式声明所有卷。

```yaml
volumes:
  mysql-data:
```

### 常见错误 5：`ports` 的格式写反

```yaml
# ❌ 错误：把容器端口写前面了
ports:
  - "80:8080"     # 你以为是"容器 80 → 宿主机 8080"
                  # 实际是"宿主机 80 → 容器 8080"
```

✅ 口诀：**"外面→里面"**，和 `docker run -p` 一样。

```yaml
# ✅ 正确
ports:
  - "8080:80"     # 宿主机 8080 → 容器 80
```

---

## 八、术语解释

| 术语 | 解释 |
|------|------|
| **services** | Compose 配置的核心区块，每个 service 定义一个容器（或一组容器） |
| **depends_on** *此术语见附录C* | 声明服务之间的启动依赖关系。默认只保证启动顺序，不保证服务就绪 |
| **healthcheck** | 健康检查——定期执行命令，确认容器内的服务是否正常运行。配合 `depends_on` 的 `condition: service_healthy` 实现真正的"等服务就绪" |
| **YAML** | 一种人类可读的数据序列化格式。Compose 用 YAML 写配置文件。对缩进要求极其严格，必须用空格不能用 Tab |
| **`docker compose config`** | 验证 compose.yml 语法并输出解析后的完整配置 |

---

## 本章小结

| 本章学了什么 | 对应命令/概念 | 注意事项 |
|-------------|-------------|---------|
| 顶层结构 | `services`、`volumes`、`networks` | services 必须，volumes/networks 可选但推荐显式声明 |
| `image` | `image: nginx:alpine` | 格式同 `docker pull` |
| `build` | `build: .` 或 `build: context: ./app` | 可同时指定 `image` 给构建产物打标签 |
| `ports` | `"宿主机:容器"` | 口诀"外面→里面"；和 `docker run -p` 格式一致 |
| `volumes`（services 内） | `- 卷名:容器路径` 或 `- ./host:容器路径` | 具名卷需在顶层声明；bind mount 用于开发 |
| `environment` | `NODE_ENV: production` | 两种写法：字典或数组；不要硬编码密码 |
| `depends_on` | `depends_on: - db` | 默认只等容器启动，不等服务就绪！ |
| `depends_on` + healthcheck | `condition: service_healthy` | 需要 Compose v2.1+；MySQL 必须配这个 |
| `restart` | `unless-stopped` | 推荐生产环境用 `unless-stopped` |
| `healthcheck` | `test: ["CMD", ...]` | `$$` 转义 YAML 的 `$` 变量替换 |
| 语法检查 | `docker compose config` | 每次改完 compose.yml 先跑这个 |

---

## 本篇最可能出错的地方及原因

### 1. `depends_on` 不管服务就绪——这是 Compose 新手必踩的坑

**原因**：`depends_on` 这个名字太误导了。"depend on" 听起来像"依赖它、它好了我才行"。但实际上 `depends_on` 只管容器启动顺序，不管容器里的服务是否就绪。

**真实场景**：MySQL 容器启动了，但 `mysqld` 进程还在初始化 InnoDB 日志。你的 Web 应用收到 `depends_on` 放行信号，冲进去连接 MySQL——`Connection refused`。

**正确的做法**：配上 `healthcheck` + `condition: service_healthy`。这是写 Compose 配 MySQL 的标配操作。

### 2. healthcheck 里的 `$$` 转义

在 YAML 文件里写 shell 命令，`$` 是 YAML 的特殊字符。如果你写了 `$MYSQL_ROOT_PASSWORD`，YAML 解释器会尝试用环境变量替换它——但 build 时环境里没有这个变量，它就变成了空字符串。你的 healthcheck 命令变成了 `mysqladmin ping -p`（密码为空），永远失败。

**排查**：`docker compose ps` 看 `db` 服务的 STATUS，如果显示 `(health: starting)` 一直不变成 `(healthy)`，检查 healthcheck 命令里的 `$` 是否写成了 `$$`。

### 3. 端口映射方向写反

`docker run -p` 的格式是 `宿主机:容器`，`docker compose ports` 的格式也是 `"宿主机:容器"`。但有些人会直觉地写成 `"80:8080"`——"容器里跑 80，对外暴露 8080"——这是错的。

**口诀**：想想 `docker run -p 8080:80 nginx`——先写宿主机，再写容器。Compose 完全一样。

### 4. 顶层 volumes/networks 忘记声明

不声明不会报错，Compose 会自动创建。但自动创建的东西（尤其是 volume）在你 `docker compose down` 时不会被清理（即使加了 `-v` 也只清理声明过的卷）。久而久之，你的系统里会积累大量无名卷。

**最佳实践**：所有用到的卷和网络，都在顶层显式声明。