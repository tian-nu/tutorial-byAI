# 11 — FROM 和 RUN

> - 对应文档版本：Docker精通教程 outline v1
> - 适用环境：任何已安装 Docker 的系统
> - 读者角色：已了解 Dockerfile 基本结构，需要深入理解基础镜像选择和层缓存的开发者
> - 预计耗时：新手 30 分钟 / 熟手 15 分钟
> - 前置教程：第 10 章（第一个 Dockerfile）
> - 可视化：无

---

## 我在做什么？

上一章你写了第一个 Dockerfile，用了 `FROM alpine`。但为什么是 alpine？能不能用 ubuntu？能不能用 debian？它们有什么区别？

这一章我们聚焦 Dockerfile 的前两条指令：`FROM` 和 `RUN`。你会理解怎么选基础镜像、怎么写出能利用缓存的 RUN 指令，以及——最重要的——为什么每一条指令都是一层，而层是 Docker 速度的秘密。

学完这一章，你能：
- 根据场景选择合适的基础镜像（alpine / slim / 完整版）
- 区分 `RUN` 的两种写法（shell 形式 vs exec 形式）
- 利用层缓存加速构建，知道什么时候缓存会失效
- 读懂 `docker history` 的输出，看到每一层的大小

---

## 一、FROM：你站在谁的肩上？

### FROM 的作用

```dockerfile
FROM 基础镜像:版本号
```

`FROM` 是 Dockerfile 的**第一条指令**（注释除外）。它告诉 Docker："不要从零开始，从我指定的这个镜像开始构建。"

> 如果 Docker 是盖房子，`FROM` 就是选择"用什么地基"。你可以选平地（`FROM scratch`，从零开始），也可以选已经打好地基、铺好水电的房子（`FROM ubuntu:22.04`）。

### 基础镜像的三大流派

想象你要开一家餐厅。你有三种选址方案：

| 方案 | 对应基础镜像 | 特点 |
|------|------------|------|
| 租毛坯房，自己装修 | `alpine` | 极简，什么都没有，但你要什么就装什么 |
| 租简装房，拎包入住 | `debian:stable-slim` | 有基本设施，不算大，够用 |
| 租精装豪宅，拎包入住 | `ubuntu:22.04` | 什么都有，但也最大最重 |

#### Alpine：极简主义者的最爱

```dockerfile
FROM alpine:latest
```

Alpine Linux 是专门为容器设计的超精简 Linux 发行版。它的特点：

- 镜像大小：**~5 MB**（对比 Ubuntu ~77 MB）
- 包管理器：`apk`（**不是 `apt`！**）
- C 标准库：`musl libc`（不是常见的 `glibc`）
- 内核：和所有 Linux 一样用 Linux 内核（容器共享宿主机内核）

```bash
# 安装软件包
apk add --no-cache nginx
#              ───┬───
#        Alpine 特有：--no-cache 不保留安装缓存（省空间）
```

> **想多一点**：Alpine 只有 ~5 MB，意味着什么？意味着你从 Docker Hub 拉取镜像只需零点几秒。意味着你的 CI/CD 流水线构建速度飞快。意味着你的私有仓库硬盘占用小。但代价是：musl libc 不同于 glibc，某些编译型语言（如 Python 的 C 扩展、Node.js 的 native addon）可能出兼容性问题。Alpine 适合**"我知道我的依赖没问题"**的场景，不适合"装上再说"的场景。

#### Debian Slim：中庸之道

```dockerfile
FROM debian:stable-slim
```

`slim` 版本是砍掉了文档、手册页和其他非必要文件的 Debian。大小约 **~25 MB**（对比完整 Debian ~120 MB）。

- 包管理器：`apt`，和 Ubuntu 一样
- C 标准库：`glibc`，兼容性好
- 适合场景：需要 `glibc` 但对镜像大小有要求

#### Ubuntu / Debian 完整版：一条龙服务

```dockerfile
FROM ubuntu:22.04
```

- 镜像大小：**~77 MB**
- 包里什么都有，适合"快速上手，不想折腾"
- 适合场景：本地开发、学习、需要大量系统工具的场景

### 版本号：永远不要只写 `latest`

```dockerfile
# ❌ 不推荐
FROM ubuntu:latest
# 今天 "latest" 是 24.04，三个月后可能是 26.04
# 你的镜像行为可能悄悄变了

# ✅ 推荐
FROM ubuntu:22.04
# 明确版本，行为可预测
```

如果你写 `FROM ubuntu:latest`，三个月后重新 `docker build`，Ubuntu 的 `latest` 标签可能已经指向了新版本。你的构建结果可能不一样——库版本变了、API 变了、行为变了。这叫"漂移"（drift），是生产环境的大忌。

### Docker Hub 官方镜像 vs 社区镜像

```bash
# 官方镜像（推荐）
FROM nginx:1.25
FROM python:3.12
FROM node:20

# 社区镜像（谨慎使用）
FROM someuser/someimage:v1
```

怎么判断是不是官方镜像？去 [hub.docker.com](https://hub.docker.com) 搜索，官方镜像会标 **"Docker Official Image"**。

> 官方镜像由 Docker 公司和软件官方维护，有安全更新、有文档、经过审查。社区镜像质量参差不齐——有的比官方还好，有的里面藏着挖矿脚本。**除非你很清楚镜像的维护者是谁，否则优先用官方镜像。**

---

## 二、RUN：在镜像里执行命令

### RUN 做什么？

```dockerfile
RUN 命令
```

每一条 `RUN` 都在**构建过程中**执行一个命令，然后把执行结果（产生的文件变化）保存为镜像的一个新层。

举个简单例子：

```dockerfile
FROM alpine:latest
RUN echo "hello" > /message.txt
```

执行 `docker build` 时，Docker 做的是：

```
1. 基于 alpine 镜像启动一个临时容器
2. 在这个容器里执行 echo "hello" > /message.txt
3. 把容器的文件系统变化保存为一个新的镜像层
4. 删除临时容器
```

### RUN 的两种写法

Docker 支持两种 RUN 格式：

```dockerfile
# 方式 1：shell 形式
RUN apt update && apt install -y nginx

# 方式 2：exec 形式
RUN ["apt", "update"]
RUN ["apt", "install", "-y", "nginx"]
```

| 维度 | shell 形式 | exec 形式 |
|------|-----------|----------|
| 写法 | `RUN command arg1 arg2` | `RUN ["command", "arg1", "arg2"]` |
| 背后启动什么 | `/bin/sh -c "command arg1 arg2"` | 直接执行 `command` |
| 能用 shell 特性吗？ | 能用（管道、变量、`&&`） | 不能用 |
| 需要 shell 吗？ | 需要（镜像里必须有 `/bin/sh`） | 不需要 |

> **什么时候用 exec 形式？** 当你的基础镜像没有 shell 时（比如 `FROM scratch`），只能用 exec 形式。但绝大多数情况用 shell 形式就够了，因为 alpine、debian、ubuntu 都有 `/bin/sh`。

### 实战对比

```dockerfile
# ✅ shell 形式 —— 推荐日常使用
FROM ubuntu:22.04
RUN apt update && apt install -y nginx
#  && 是 shell 特性，exec 形式做不到
```

```dockerfile
# ✅ exec 形式 —— 在没有 shell 的场景下使用
FROM scratch
COPY mybinary /mybinary
RUN ["/mybinary", "--init"]
```

> **选择建议**：shell 形式日常用，功能多、写法自然；exec 形式在处理信号（第 14 章会讲）和"没有 shell 的镜像"时用。本章后面全部用 shell 形式。

---

## 三、层缓存机制：Docker 为什么这么快？

### 什么是层？

每一条 Dockerfile 指令（`FROM`、`RUN`、`COPY` 等）都生成一个**镜像层**。最终的镜像 = 所有层的叠加。

```
镜像 myapp:v1
┌─────────────────────────────┐
│ 第 4 层  CMD echo "hello"   │  ← 运行时配置层（很小）
├─────────────────────────────┤
│ 第 3 层  COPY . /app        │  ← 你的代码
├─────────────────────────────┤
│ 第 2 层  RUN apt install    │  ← 安装的软件
├─────────────────────────────┤
│ 第 1 层  FROM ubuntu:22.04  │  ← 基础镜像
└─────────────────────────────┘
```

### 缓存怎么工作？

当你第二次 `docker build` 时，Docker 不会重新执行没变过的指令。它会检查：**这条指令和上次构建时一样吗？** 如果一样，直接用缓存；如果不一样，重新执行。

```
第一次构建：
  FROM ubuntu:22.04     → 执行（拉取基础镜像）
  RUN apt update        → 执行（耗时 30 秒）
  RUN apt install nginx → 执行（耗时 20 秒）
  COPY . /app           → 执行（耗时 1 秒）

第二次构建（什么都没改）：
  FROM ubuntu:22.04     → 使用缓存 ✓
  RUN apt update        → 使用缓存 ✓
  RUN apt install nginx → 使用缓存 ✓
  COPY . /app           → 使用缓存 ✓
  总耗时：< 1 秒！（第一次 51 秒）
```

### 缓存什么时候会失效？

**规则：某一条指令变了，它和它后面的所有层缓存全部失效。**

```
如果只改了 COPY . /app（你的代码变了）：
  FROM ubuntu:22.04     → 使用缓存 ✓ （没变）
  RUN apt update        → 使用缓存 ✓ （没变）
  RUN apt install nginx → 使用缓存 ✓ （没变）
  COPY . /app           → 重新执行 ✗ （代码变了）
  CMD echo "hello"      → 重新执行 ✗ （因为上一条变了）

总耗时：~2 秒（只重新 COPY）
```

这就是 Dockerfile **指令顺序**的重要性：**把最不容易变的指令放前面，最容易变的放后面。** 这样前面的指令缓存住了，只有最后几层重新构建。

```dockerfile
# ❌ 糟糕的顺序：每次代码改动，整个构建从头来过
COPY . /app              # 代码经常变
RUN apt update           # 缓存失效！重装系统包！
RUN apt install -y nginx # 缓存失效！

# ✅ 正确的顺序：不变的先做
RUN apt update
RUN apt install -y nginx # 装完软件后，这层就缓存住了
COPY . /app              # 只这层重新构建
```

### `--no-cache`：强制从头构建

```bash
docker build --no-cache -t myapp:v1 .
```

加 `--no-cache`，Docker 忽略所有缓存，每条指令都重新执行。什么时候用？

- 你想确保拉取最新的软件包（`apt update` 虽然指令没变，但软件源的内容变了）
- 你怀疑缓存出了问题（应该用缓存但没用；不应该用缓存但用了）
- 你的 CI/CD 流程每天定时全量构建一次

---

## 四、实战：构建一个安装了 nginx 的 Alpine 镜像

### 步骤 1：写 Dockerfile

创建新目录并新建 `Dockerfile`：

```dockerfile
FROM alpine:3.19

# 安装 nginx
RUN apk add --no-cache nginx

# 创建 nginx 需要的目录
RUN mkdir -p /run/nginx

# 创建一个简单的首页
RUN echo "<h1>Hello from Alpine Nginx!</h1>" > /usr/share/nginx/html/index.html

CMD ["nginx", "-g", "daemon off;"]
```

> `nginx -g "daemon off;"` 是让 nginx 在前台运行。默认的 nginx 会退到后台（daemon 模式），然后容器的 PID 1 进程退出，容器就停了。`daemon off` 确保 nginx 一直占着前台，容器不会退出。

### 步骤 2：构建

```bash
docker build -t alpine-nginx:v1 .
```

预期输出：

```
[+] Building 3.2s (8/8) FINISHED
 => [1/4] FROM docker.io/library/alpine:3.19
 => [2/4] RUN apk add --no-cache nginx
 => [3/4] RUN mkdir -p /run/nginx
 => [4/4] RUN echo "<h1>Hello from Alpine Nginx!</h1>" > /usr/share/nginx/html/index.html
 => exporting to image
 => => naming to docker.io/library/alpine-nginx:v1
```

### 步骤 3：运行

```bash
docker run -d -p 8080:80 --name my-nginx alpine-nginx:v1
```

- `-d`：后台运行
- `-p 8080:80`：把宿主机的 8080 端口映射到容器的 80 端口
- `--name my-nginx`：给容器起个名字

### 步骤 4：验证

```bash
# 在浏览器打开 http://localhost:8080
# 应该看到 "Hello from Alpine Nginx!"

# 或者用 curl
curl http://localhost:8080
# 输出：<h1>Hello from Alpine Nginx!</h1>

# 查看容器日志
docker logs my-nginx
# 应该看到 nginx 的访问日志
```

### 步骤 5：查看层历史

```bash
docker history alpine-nginx:v1
```

输出类似：

```
IMAGE          CREATED          CREATED BY                                      SIZE
abc123def456   2 minutes ago    CMD ["nginx" "-g" "daemon off;"]                0B
789012abc345   2 minutes ago    RUN /bin/sh -c echo "<h1>Hello..." > ...       26B
456789def012   2 minutes ago    RUN /bin/sh -c mkdir -p /run/nginx              0B
345678cde901   2 minutes ago    RUN /bin/sh -c apk add --no-cache nginx        4.5MB
012345bcd678   3 days ago       /bin/sh -c #(nop)  CMD ["/bin/sh"]             0B
<missing>      3 days ago       /bin/sh -c #(nop) ADD file:abc123... in /      7.4MB
```

每一行对应一条指令。最下面的是基础镜像层，往上依次是每条 RUN。`SIZE` 列告诉你每层加了多少数据。

> **想多一点**：注意 `CMD` 和基础镜像的 `ADD` 层 SIZE 都是 0B 或很小——它们不是真的"空"，而是 Docker 把 CMD 这类元数据存在了镜像配置里，不算在层的文件系统大小里。真正占空间的是 `RUN apk add --no-cache nginx` 这种装了软件的层。

---

## 五、常见错误与最佳实践

### Alpine 用 `apt`（应该用 `apk`）

```dockerfile
# ❌ 错误
FROM alpine:latest
RUN apt update && apt install -y nginx
# alpine 没有 apt！

# ✅ 正确
FROM alpine:latest
RUN apk add --no-cache nginx
```

| 系统 | 包管理器 | 安装命令 |
|------|---------|---------|
| Alpine | apk | `apk add --no-cache 包名` |
| Ubuntu/Debian | apt | `apt update && apt install -y 包名` |
| CentOS/RHEL | yum/dnf | `yum install -y 包名` |

### 每次 RUN 后不清理缓存

```dockerfile
# ❌ 错误：apt 缓存留在镜像里，白白占空间
FROM ubuntu:22.04
RUN apt update
RUN apt install -y nginx

# ✅ 正确：安装完就清理
FROM ubuntu:22.04
RUN apt update && apt install -y nginx \
    && rm -rf /var/lib/apt/lists/*
#                          ─────┬─────
#                     apt 的软件包列表缓存
#                     不清的话大约多出 50-100MB
```

`&&` 是关键：如果你写两个独立的 RUN，清理操作在另一层，被"删除"的文件其实还在下层里（镜像层是叠加的，下层文件不会被真正删除，只是被上层"遮住"了）。

```dockerfile
# ❌ 错误：两层 RUN，清理无效（下层文件还在）
RUN apt update && apt install -y nginx
RUN rm -rf /var/lib/apt/lists/*
# 镜像大小 = 安装的软件 + apt 缓存（没有被真正删除，只是被遮住了）

# ✅ 正确：同一条 RUN，文件根本没进镜像层
RUN apt update && apt install -y nginx && rm -rf /var/lib/apt/lists/*
# 镜像大小 = 安装的软件（apt 缓存在同一层里被删除了，没有进入最终镜像）
```

### `apt update` 和 `apt install` 分开写，缓存不更新

```dockerfile
# ❌ 可能出问题
RUN apt update
RUN apt install -y nginx
# 第一次构建：apt update 执行，缓存住
# 第二次构建：apt update 用缓存，不重新拉取软件源
# 三个月后镜像源里的 nginx 版本变了，但你装到的还是旧版本

# ✅ 推荐
RUN apt update && apt install -y nginx
# 写成一行，如果 nginx 版本要更新，用 --no-cache 整体重建
```

---

## 六、我做得对不对？

### 验证方法

```bash
# 1. 确认 Dockerfile 存在
cat Dockerfile

# 2. 构建镜像
docker build -t alpine-nginx:v1 .

# 3. 运行容器
docker run -d -p 8080:80 --name test-nginx alpine-nginx:v1

# 4. 验证 nginx 有响应
curl http://localhost:8080
# 预期输出：<h1>Hello from Alpine Nginx!</h1>

# 5. 查看镜像大小
docker images alpine-nginx:v1
# 记录 SIZE，应该比 ubuntu 版本小很多

# 6. 查看层历史
docker history alpine-nginx:v1
# 每一行对应一条指令

# 7. 第二次构建（不改任何东西），确认使用缓存
docker build -t alpine-nginx:v1 .
# 所有步骤都应该显示 CACHED

# 8. 清理
docker stop test-nginx && docker rm test-nginx
```

---

## 七、不对怎么办？

### 常见错误 1：alpine 镜像里 `apt` 命令不存在

```
/bin/sh: apt: not found
```

❌ 原因：在 Alpine 镜像里用了 Debian/Ubuntu 的命令。

✅ 解决：把 `apt` 换成 `apk`，把 `apt install -y 包名` 换成 `apk add --no-cache 包名`。

### 常见错误 2：`--no-cache` 不是 docker build 的那个

新手容易混淆两个 `--no-cache`：

```bash
# 这个 --no-cache 是 docker build 的选项：忽略构建缓存
docker build --no-cache -t myapp .

# 这个 --no-cache 是 apk 的选项：不保留下载的安装包缓存
RUN apk add --no-cache nginx
```

两个是完全不同的东西。`apk add --no-cache` 是 Alpine 包管理器的行为，让它在安装后不保留 `.apk` 安装包文件，减小镜像体积。

### 常见错误 3：`apt update` 缓存不刷新，装的还是旧包

```
# 你的 Dockerfile:
RUN apt update && apt install -y nginx

# 三个月后，软件源里的 nginx 版本升级了，
# 但 docker build 用了缓存，装的还是旧版。
```

这不是 bug，是缓存机制的特性。解决办法：

```bash
# 方法 1：强制重建
docker build --no-cache -t myapp:v2 .

# 方法 2：在 Dockerfile 里"破坏"那个 RUN 的缓存
# 加一句无害的 echo 改变指令内容
RUN echo "cache-bust: $(date)" && apt update && apt install -y nginx
# 👆 不推荐生产使用，但适合快速调试
```

### 常见错误 4：nginx 容器启动了但 `docker ps` 看不到

```
docker run -d -p 8080:80 alpine-nginx:v1
docker ps
# 看不到容器！
```

原因：nginx 启动后立即退出了。检查你的 CMD：

```dockerfile
# ❌ 错误：nginx 默认后台运行，前台没进程，容器退出
CMD ["nginx"]

# ✅ 正确：nginx 必须在前台运行
CMD ["nginx", "-g", "daemon off;"]
```

### 常见错误 5：COPY 放在 RUN 前面，修改代码后所有缓存失效

```dockerfile
# ❌ 错误的指令顺序
FROM node:20
COPY . /app          # 代码一改 → 这层重建
RUN npm install      # 缓存失效 → 重装依赖（很慢！）

# ✅ 正确的指令顺序
FROM node:20
COPY package*.json /app/  # 先只复制依赖清单
RUN npm install           # 依赖清单没变 → 用缓存
COPY . /app               # 最后复制代码
```

---

## 本章小结

| 本章学了什么 | 对应命令/概念 | 注意事项 |
|-------------|-------------|---------|
| FROM 选型 | Alpine (~5MB) / Debian Slim (~25MB) / Ubuntu (~77MB) | Alpine 用 `apk` 不是 `apt`，musl libc 可能不兼容某些应用 |
| 版本号固定 | `FROM ubuntu:22.04` 而非 `:latest` | `latest` 标签会漂移，生产环境必须固定版本 |
| 官方 vs 社区镜像 | Docker Official Image 标识 | 优先用官方镜像，社区镜像需审查来源 |
| RUN 两种形式 | shell 形式 / exec 形式 | 日常用 shell 形式，无 shell 镜像用 exec 形式 |
| 镜像层 | 每条指令 = 一层 | 层是只读的，最终镜像 = 所有层的叠加 |
| 层缓存 | 指令没变 → 用缓存；变了 → 该层及后面全部重建 | 不变指令放前面，多变指令放后面 |
| `--no-cache` | `docker build --no-cache` | 强制从头构建，确保拉取最新依赖 |
| 单层清理 | `apt install && rm -rf /var/lib/apt/lists/*` | 必须在同一条 RUN 里清理，跨 RUN 清理无效 |
| `docker history` | 查看镜像层历史和每层大小 | 调试镜像体积和缓存问题的利器 |
| Alpine 包管理 | `apk add --no-cache nginx` | `--no-cache` 是 apk 的选项，不是 docker build 的 |

---

## 本篇最可能出错的地方及原因

### 1. Alpine 和 Ubuntu 的命令搞混（高频错误）

**原因**：很多开发者只用过 Ubuntu，习惯性敲 `apt`。进了 Alpine 镜像，`apt` 不存在。反过来，用惯了 Alpine，到 Ubuntu 里敲 `apk`，也不存在。

**口诀**：Alpine = `apk`，Ubuntu/Debian = `apt`。A 对 A，U 对 U。

### 2. 清理缓存在另一个 RUN 里做（镜像体积没变小）

**原因**：以为"放在另一个 RUN 里删除一样能省空间"，不理解镜像层的叠加机制。

```
RUN apt install -y nginx     → 这一层包含了 nginx + apt 缓存（100MB）
RUN rm -rf /var/lib/apt/lists/*  → 这一层标记"缓存被删了"（但上层的缓存文件还在）
最终镜像：100MB + 标记文件 ≈ 还是 100MB
```

**正确**：同一条 RUN 里完成安装和清理。

### 3. 不理解"某条指令变了，后面的全部重建"

**现象**：就改了一行代码，构建却重新下载了所有依赖，耗时几分钟。

**原因**：`COPY . /app` 放在 Dockerfile 前面，代码一改，它后面的 `RUN npm install` 等全失效。

**解决**：把依赖安装指令放在代码复制指令之前。利用"只复制依赖清单 → 安装依赖 → 再复制代码"的方式。

### 4. nginx 用 `CMD ["nginx"]` 导致容器秒退

**原因**：nginx 默认行为是后台运行（daemonize），启动后主进程退出，剩下的 worker 进程变成孤儿。容器只看 PID 1——PID 1 退出 = 容器停止。

**解决**：`CMD ["nginx", "-g", "daemon off;"]` 让 nginx 在前台运行。几乎所有传统的后台服务（nginx、apache、mysql）在容器里都需要前台化。