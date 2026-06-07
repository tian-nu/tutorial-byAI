# 23 — Compose 常用命令

> - 对应文档版本：Docker精通教程 outline v1
> - 适用环境：任何已安装 Docker + Docker Compose 的系统
> - 读者角色：已掌握 compose.yml 编写，需要熟悉 Compose 命令行操作的开发者
> - 预计耗时：新手 25 分钟 / 熟手 12 分钟
> - 前置教程：第 22 章（多容器编排实战）
> - 可视化：无

---

## 我在做什么？

前几章你在写 compose.yml，在跑 `docker compose up -d`，在 `docker compose down`。但 Compose 的命令远不止这三个——它有一整套命令来管理多容器应用的生命周期：启动、停止、重启、查看日志、进入容器、重新构建、拉取镜像。

这一章是一个"命令手册"，但不止是手册——每个命令后面都跟着"什么时候用"和"容易踩什么坑"。

学完这一章，你能：
- 用 Compose 命令管理应用的全生命周期
- 区分 `stop` vs `down`、`start` vs `up`、`restart` vs `down && up`
- 看懂 `docker compose` 命令和 `docker` 命令的对应关系
- 避免最常见的命令误用（特别是 `down` 忘 `-v`）

---

## 一、`docker compose up`：启动一切

### 基本用法

```bash
docker compose up
```

这是你用得最多的 Compose 命令。它做了以下事情：
1. 读取 compose.yml
2. 创建必要的网络和数据卷
3. 构建或拉取镜像
4. 创建并启动所有服务容器

### 常用选项

```bash
docker compose up -d        # 后台运行（detached mode）
docker compose up --build   # 启动前重新构建镜像
docker compose up --no-deps # 不启动依赖的服务（只启动指定服务）
docker compose up web       # 只启动 web 服务（及其依赖）
docker compose up --force-recreate  # 强制重新创建容器（即使配置没变）
docker compose up --remove-orphans  # 删除 compose.yml 里已不存在的服务容器
```

### 什么时候用哪个？

| 场景 | 命令 |
|------|------|
| 正常启动 | `docker compose up -d` |
| 改了 Dockerfile 后启动 | `docker compose up -d --build` |
| 只重启某个服务 | `docker compose up -d web` |
| 改了 compose.yml 后启动 | `docker compose up -d`（Compose 会自动检测变化并重建容器） |
| 调试，想看日志 | `docker compose up`（不要 `-d`，前台跑） |

### `-d` 要不要加？

- **开发时调试**：不加 `-d`，前台运行。所有日志直接输出到终端，`Ctrl+C` 就能停止。方便快速排错。
- **确认一切正常后**：加 `-d`，后台运行。终端可以继续做其他事情。

### 和 `docker run` 的对应关系

```
docker compose up -d
  ≈ docker network create → docker volume create → docker build → docker run -d（对每个服务）
```

但 `docker compose up` 更聪明——它只重建有变化的服务，没变化的直接用缓存。

---

## 二、`docker compose down`：停止并清理

### 基本用法

```bash
docker compose down
```

做的事情：
1. 停止所有服务容器
2. 删除所有服务容器
3. 删除默认网络（和 compose.yml 里声明的网络）

**不删除**：
- 数据卷（除非加 `-v`）
- 构建的镜像（除非加 `--rmi`）

### 常用选项

```bash
docker compose down -v        # 同时删除数据卷（⚠️ 数据会丢失！）
docker compose down --rmi all # 同时删除所有镜像
docker compose down --rmi local # 只删除本地构建的镜像
docker compose down --volumes # -v 的长格式写法
docker compose down -t 30     # 等 30 秒再强制杀死（默认 10 秒）
```

### ⚠️ `-v` 的风险

```bash
# ❌ 危险操作——如果你还需要数据库里的数据
docker compose down -v
# MySQL 的数据卷被删了，所有数据都没了！

# ✅ 安全操作——数据保留，下次 docker compose up 数据还在
docker compose down
```

> **想多一点**：`docker compose down -v` 是一个"干净的重置"——所有持久化数据都没了。这在开发环境有时是好事（"从头开始"），但如果在生产环境，这就是灾难。我见过有人写了个脚本定时 `docker compose down -v && docker compose up -d` 来"重启服务"，结果每次重启数据库都被清空。**永远要知道你在删什么。**

### `docker compose down` vs `docker compose stop`

| | `docker compose stop` | `docker compose down` |
|---|---|---|
| 停止容器 | ✅ | ✅ |
| 删除容器 | ❌ | ✅ |
| 删除网络 | ❌ | ✅ |
| 删除数据卷 | ❌ | ❌（除非 `-v`） |
| 容器重启后还在吗 | 在（`docker compose start` 恢复） | 不在（重新创建） |

> 类比：`stop` = 关机（数据、配置都在，重新开机就行）。`down` = 拆机（零件都拆了，下次要重新组装）。

---

## 三、`docker compose start / stop / restart`：不删除容器

### 基本用法

```bash
docker compose stop          # 停止所有服务（保留容器）
docker compose start         # 启动已停止的容器
docker compose restart       # 重启所有服务
docker compose restart web   # 只重启 web 服务
```

### 什么时候用 stop/start 而不是 down/up？

- **stop/start**：只是暂停/恢复。容器不重建，配置不重新读取，数据卷不变。适合临时停一下（比如要释放内存），再恢复。
- **down/up**：完全重建。容器、网络都重新创建。适合改了 compose.yml 或 Dockerfile 后需要生效。

```bash
# 场景：临时停一下，马上恢复
docker compose stop
# 做一些事情（比如备份数据卷）
docker compose start    # 容器恢复，IP 可能变了但数据还在

# 场景：改了配置，需要重建
docker compose down
docker compose up -d   # 重新创建容器，新配置生效
```

### 易混淆点

```bash
# ❌ 你以为改了 compose.yml 后 stop/start 能生效
docker compose stop
# 修改 compose.yml 的端口映射
docker compose start
# 端口映射没变！因为容器没重建，旧的端口映射还在

# ✅ 正确做法
docker compose down
docker compose up -d
# 容器重建，新的端口映射生效
```

---

## 四、`docker compose logs`：查看日志

### 基本用法

```bash
docker compose logs           # 查看所有服务的日志
docker compose logs web       # 只查看 web 服务的日志
docker compose logs -f        # 实时跟踪（follow，类似 tail -f）
docker compose logs --tail 50 # 只看最后 50 行
docker compose logs --since 10m  # 只看最近 10 分钟的日志
docker compose logs -f web db # 同时跟踪两个服务的日志
```

### 和 `docker logs` 的对比

```bash
# 不用 Compose：你需要知道容器名
docker ps                            # 找到容器名
docker logs my-app-web-1            # 看 web 日志
docker logs my-app-db-1             # 看 db 日志

# 用 Compose：一条命令搞定
docker compose logs                  # 所有服务日志，按服务名自动标注
docker compose logs -f               # 实时跟踪所有服务
```

> Compose 的 `logs` 命令会把不同服务的日志用不同颜色标注（在支持颜色的终端里），一眼就能看出哪条日志来自哪个服务。

---

## 五、`docker compose exec`：进入容器

### 基本用法

```bash
docker compose exec web bash       # 进入 web 服务的容器，执行 bash
docker compose exec db mysql -u root -p  # 在 db 容器里执行 mysql 命令
docker compose exec -T web cat /etc/hostname  # 不分配 TTY（适合脚本）
docker compose exec -u root web bash  # 以 root 用户进入
```

### 和 `docker exec` 的对比

```bash
# 不用 Compose：需要找到容器名
docker ps                           # 找到 web 服务的容器名
docker exec -it my-app-web-1 bash  # 进入

# 用 Compose：直接用服务名
docker compose exec web bash       # 不用记容器名
```

### 常见场景

```bash
# 进入 web 容器排查问题
docker compose exec web bash

# 在 db 容器里执行 SQL
docker compose exec db mysql -u wordpress -p

# 在 web 容器里运行一次性命令
docker compose exec web npm run migrate

# 查看 web 容器的环境变量
docker compose exec web env
```

---

## 六、`docker compose build`：重新构建镜像

### 基本用法

```bash
docker compose build           # 构建所有有 build 配置的服务
docker compose build web       # 只构建 web 服务
docker compose build --no-cache  # 不用缓存，完全重新构建
docker compose build --pull    # 构建前先拉取基础镜像的最新版本
```

### 什么时候用？

```bash
# 场景 1：改了 Dockerfile，需要重新构建
docker compose build
docker compose up -d

# 场景 2：只构建不启动
docker compose build

# 场景 3：构建并启动（一步到位）
docker compose up -d --build

# 场景 4：完全重新构建（排查缓存问题）
docker compose build --no-cache
```

---

## 七、`docker compose pull`：拉取最新镜像

### 基本用法

```bash
docker compose pull            # 拉取所有服务的镜像
docker compose pull web        # 只拉取 web 服务的镜像
docker compose pull --ignore-buildable  # 跳过有 build 配置的服务
```

### 什么时候用？

```bash
# 场景：你用的是 wordpress:latest，想更新到最新版
docker compose pull
docker compose up -d
# 如果镜像有更新，Compose 会重建容器
```

---

## 八、其他常用命令

```bash
# 查看当前项目的服务列表
docker compose ps
docker compose ps -a            # 包括停止的容器

# 查看服务使用的镜像
docker compose images

# 查看 compose.yml 解析后的完整配置
docker compose config
docker compose config --services  # 只看服务名列表

# 查看端口映射
docker compose port web 80       # 查看 web 服务的 80 端口映射到宿主机的哪个端口

# 在运行中的容器上执行命令
docker compose run web npm test  # 用 web 服务的配置启动一个新容器执行 npm test
# 注意：run 和 exec 不同！run 启动新容器，exec 进入已有容器

# 暂停/恢复容器（不停止进程，只是 freeze）
docker compose pause
docker compose unpause

# 查看资源使用
docker compose top               # 查看所有服务的进程
docker compose stats             # 实时查看 CPU、内存使用（类似 htop）
```

---

## 九、命令对比总表：docker compose vs docker

| 操作 | docker compose 命令 | 等价 docker 命令（手动） |
|------|-------------------|----------------------|
| 启动服务 | `docker compose up -d` | `docker network create` + `docker volume create` + `docker run -d` × N |
| 停止+删除 | `docker compose down` | `docker stop` × N + `docker rm` × N + `docker network rm` |
| 停止（保留容器） | `docker compose stop` | `docker stop` × N |
| 启动已停止的容器 | `docker compose start` | `docker start` × N |
| 重启 | `docker compose restart` | `docker restart` × N |
| 查看日志 | `docker compose logs` | `docker logs` × N（每个容器一条） |
| 进入容器 | `docker compose exec web bash` | `docker exec -it 容器名 bash` |
| 查看状态 | `docker compose ps` | `docker ps --filter="label=com.docker.compose.project"` |
| 构建镜像 | `docker compose build` | `docker build -t xxx .` × N |
| 拉取镜像 | `docker compose pull` | `docker pull` × N |
| 查看配置 | `docker compose config` | 无直接等价命令 |

---

## 十、我做得对不对？

### 验证方法

```bash
# 前提：有一个 compose.yml 在手的项目（比如第 22 章的 WordPress 项目）

# 1. 启动
docker compose up -d
docker compose ps
# 预期：所有服务 Up

# 2. 查看日志
docker compose logs --tail 20
# 预期：看到各服务的日志，按服务名标注

# 3. 停止（保留容器）
docker compose stop
docker compose ps -a
# 预期：服务 Exited，但容器还在

# 4. 重新启动
docker compose start
docker compose ps
# 预期：服务恢复 Up

# 5. 重启
docker compose restart
# 预期：容器重启，服务恢复

# 6. 进入容器
docker compose exec web bash
# 在容器里执行几条命令，exit 退出

# 7. 查看配置
docker compose config --services
# 预期：列出所有服务名

# 8. 彻底清理
docker compose down -v
# 预期：容器、网络、数据卷全部删除
```

---

## 十一、不对怎么办？

### 常见错误 1：`docker compose down` 忘记 `-v`，volume 残留

```bash
# 你执行了
docker compose down
docker compose up -d
# 咦？数据库里还是旧数据？MySQL 密码改了没生效？
```

❌ 原因：`docker compose down` 不删数据卷。MySQL 的数据卷还在，新容器挂载了旧的数据卷，用旧的密码和数据库。

✅ 解决：

```bash
# 如果需要彻底重置
docker compose down -v
docker compose up -d
```

或者手动删除残留的卷：

```bash
docker volume ls | grep 项目名
docker volume rm 项目名_mysql-data
```

### 常见错误 2：`docker compose stop` vs `docker compose down` 混淆

```bash
# 你改了 compose.yml，然后：
docker compose stop
docker compose start
# 配置没生效！
```

❌ 原因：`stop/start` 不重建容器，用旧的容器配置。改 compose.yml 后需要 `down/up`。

✅ 口诀：**改配置 = down/up，临时停 = stop/start。**

### 常见错误 3：`docker compose up` 没加 `-d`，终端被日志淹没

```bash
docker compose up
# 日志刷屏，Ctrl+C 停了。想后台运行，又跑了一遍：
docker compose up -d
# 报错：端口冲突
```

❌ 原因：第一遍 `docker compose up`（前台）已经创建了容器。Ctrl+C 虽然停止了容器，但容器还在。第二遍 `docker compose up -d` 尝试创建容器，发现端口已经被占用。

✅ 解决：

```bash
# 先清理
docker compose down
# 再后台启动
docker compose up -d

# 或者一步到位
docker compose up -d   # 直接后台启动
```

### 常见错误 4：`docker compose exec` 服务名写错

```bash
docker compose exec nginx bash
# service "nginx" is not running
```

❌ 原因：服务名是 compose.yml 里定义的，不是镜像名。如果 compose.yml 里服务叫 `web`，你用 `nginx` 去找就会报错。

✅ 解决：

```bash
# 先看有哪些服务
docker compose config --services
# 输出：web db

# 再用正确的服务名
docker compose exec web bash
```

### 常见错误 5：`docker compose run` 和 `docker compose exec` 搞混

```bash
# 你想在已有容器里执行命令
docker compose run web ls -la
# 启动了一个新容器！不是进已有容器！
```

❌ `docker compose run` 启动一个**新容器**（用服务的配置），执行完命令后容器退出。
✅ `docker compose exec` 进入**已有容器**执行命令。

```bash
# 进入已有容器执行命令
docker compose exec web ls -la

# 启动临时容器执行一次性任务（比如数据库迁移）
docker compose run --rm web npm run migrate
```

---

## 十二、术语解释

| 术语 | 解释 |
|------|------|
| **`docker compose up`** *此术语见附录C* | 启动 compose.yml 定义的所有服务。`-d` 后台运行 |
| **`docker compose down`** *此术语见附录C* | 停止并删除所有服务容器、网络。`-v` 同时删除数据卷 |
| **`docker compose stop`** *此术语见附录C* | 停止服务但不删除容器，`start` 可恢复 |
| **`docker compose start`** *此术语见附录C* | 启动被 `stop` 停止的容器 |
| **`docker compose logs`** *此术语见附录C* | 查看服务日志。`-f` 实时跟踪 |
| **`docker compose exec`** *此术语见附录C* | 在运行中的服务容器里执行命令。对比 `run`：后者启动新容器 |
| **`docker compose restart`** | 重启服务容器 |

---

## 本章小结

| 本章学了什么 | 对应命令/概念 | 注意事项 |
|-------------|-------------|---------|
| 启动服务 | `docker compose up -d` | `-d` 后台；`--build` 重新构建 |
| 停止并清理 | `docker compose down` | 不删数据卷（除非 `-v`）；`-v` 有风险 |
| 停止/启动（保留容器） | `docker compose stop/start` | 改配置不生效，需要 down/up |
| 重启 | `docker compose restart` | 重启所有或指定服务 |
| 查看日志 | `docker compose logs -f` | 支持 `--tail`、`--since`、多服务同时跟踪 |
| 进入容器 | `docker compose exec web bash` | 用服务名不是容器名；`run` 是启动新容器 |
| 构建镜像 | `docker compose build` | `--no-cache` 不用缓存；`--pull` 拉最新基础镜像 |
| 拉取镜像 | `docker compose pull` | 更新到最新版 |
| 查看配置 | `docker compose config` | 检查语法，输出完整配置 |
| 停止 vs 关闭 | `stop` = 关机，`down` = 拆机 | 改配置必须 down/up |

---

## 本篇最可能出错的地方及原因

### 1. `docker compose down` 不加 `-v`，数据卷残留

**这是最高频的坑。** 很多人以为 `docker compose down` 是"彻底清理"，但实际上数据卷会保留。下次 `docker compose up` 时，MySQL 会挂载旧的数据卷，导致：
- 旧的密码还在（你改了环境变量也没用，因为 MySQL 数据目录已经初始化过了）
- 旧的数据库还在（你以为删了重新创建，但其实没删）
- 如果之前 MySQL 初始化失败，数据目录损坏，下次启动会继续失败

**排查**：`docker volume ls | grep 项目名`。如果看到残留的卷，手动 `docker volume rm` 删除。

### 2. `stop/start` 和 `down/up` 搞混

改完 compose.yml 后执行 `docker compose stop && docker compose start`，发现配置没生效。

**原因**：`stop/start` 操作的是**已有的容器**，容器创建时的配置（端口映射、环境变量、数据卷挂载）是固定的。`down/up` 会**重新创建容器**，新配置才会生效。

**口诀**：改代码（Dockerfile）→ `build` + `up`；改配置（compose.yml）→ `down` + `up`；临时停 → `stop` + `start`。

### 3. `docker compose run` 当成 `docker compose exec` 用

`run` 和 `exec` 的区别：
- `run`：启动一个**新容器**（基于服务的配置），执行命令，然后退出
- `exec`：在**已有的运行中的容器**里执行命令

如果你 `docker compose run web bash`，你进入的是一个全新的容器，看不到已有容器的文件变化、进程、网络连接。如果你想排查正在运行的容器，应该用 `exec`。

### 4. `docker compose up` 前后台混用

先 `docker compose up`（前台），Ctrl+C 停止，再 `docker compose up -d`（后台），报端口冲突。

**原因**：前台运行 Ctrl+C 停止了容器进程，但容器没有被删除。`docker compose ps -a` 可以看到它还在。后台运行 `up -d` 尝试创建新容器，端口已经被占用。

**解决**：先 `docker compose down` 清理，再 `docker compose up -d`。

### 5. 在生产环境执行 `docker compose down -v`

永远不要在生产环境跑 `docker compose down -v`，除非你明确知道自己在做什么。`-v` 会删除数据卷，所有数据库数据、用户上传的文件都会消失。生产环境的数据卷管理应该用专门的备份策略，不要依赖 Compose 的 `-v` 来清理。