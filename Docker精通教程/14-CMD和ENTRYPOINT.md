# 14 — CMD 和 ENTRYPOINT

> - 对应文档版本：Docker精通教程 outline v1
> - 适用环境：任何已安装 Docker 的系统
> - 读者角色：已掌握 Dockerfile 基本指令，需要理解容器启动行为的开发者
> - 预计耗时：新手 35 分钟 / 熟手 15 分钟
> - 前置教程：第 13 章（WORKDIR、ENV、EXPOSE）
> - 可视化：无

---

## 我在做什么？

你写了 Dockerfile，安装了软件，复制了代码，设置了工作目录和环境变量。现在只剩最后一步：**告诉 Docker，容器启动时到底该执行什么？**

这是 Dockerfile 里最容易搞混的两条指令——`CMD` 和 `ENTRYPOINT` *此术语见附录C*。它们的名字让人困惑，行为让人困惑，配合使用更让人困惑。但一旦你理解了"它们分别解决什么问题"，就永远不会再写错了。

学完这一章，你能：
- 用 CMD 定义容器的默认启动命令
- 用 ENTRYPOINT 定义容器的固定入口程序
- 设计 CMD + ENTRYPOINT 配合使用的镜像
- 区分 exec 形式和 shell 形式，理解为什么 exec 形式更推荐
- 理解信号传递问题，知道为什么 `docker stop` 有时要等 10 秒

---

## 一、CMD：容器的"默认动作"

### CMD 做什么？

```dockerfile
CMD ["executable", "param1", "param2"]
```

CMD 定义了容器启动时**默认执行**的命令。关键在于"默认"二字——它**可以被 `docker run` 后面的参数覆盖**。

### 最简单的例子

```dockerfile
FROM alpine:latest
CMD ["echo", "Hello from CMD"]
```

```bash
# 场景 A：不加额外参数 → CMD 生效
docker run my-cmd-image
# 输出：Hello from CMD

# 场景 B：加了额外参数 → CMD 被覆盖
docker run my-cmd-image echo "I overwrote you!"
# 输出：I overwrote you!
# CMD 被完全替换了！
```

### CMD 的三种写法

```dockerfile
# 写法 1：exec 形式（推荐）
CMD ["executable", "param1", "param2"]

# 写法 2：CMD 作为 ENTRYPOINT 的默认参数（配合 ENTRYPOINT 使用）
CMD ["param1", "param2"]

# 写法 3：shell 形式
CMD executable param1 param2
```

> 写法 2 是 CMD 和 ENTRYPOINT 配合模式，本章第四节专门讲。

### 如果 Dockerfile 里有多条 CMD？

只有**最后一条**生效。前面的都被覆盖了。

```dockerfile
CMD ["echo", "first"]    # 这条被忽略
CMD ["echo", "second"]   # 这条也忽略
CMD ["echo", "third"]    # 只有这条生效
```

### CMD 的典型用途

```
CMD ["nginx", "-g", "daemon off;"]   → 启动 nginx
CMD ["node", "server.js"]            → 启动 Node.js 应用
CMD ["python", "app.py"]             → 启动 Python 应用
CMD ["java", "-jar", "app.jar"]      → 启动 Java 应用
```

---

## 二、ENTRYPOINT：容器的"固定入口"

### ENTRYPOINT 做什么？

```dockerfile
ENTRYPOINT ["executable", "param1"]
```

ENTRYPOINT 定义了容器启动时**必须执行**的程序。它不是"默认"，而是"固定"——`docker run` 后面的参数**不会覆盖** ENTRYPOINT，而是**作为追加参数**传递给 ENTRYPOINT。

### ENTRYPOINT vs CMD：行为对比

| 场景 | CMD | ENTRYPOINT |
|------|-----|-----------|
| `docker run myimage` | 执行 CMD 定义的内容 | 执行 ENTRYPOINT 定义的内容 |
| `docker run myimage arg` | **覆盖 CMD**，执行 arg | ENTRYPOINT 依然执行，arg **作为参数追加** |
| `docker run --entrypoint` | 不受影响（CMD 本来就可以被覆盖） | **覆盖** ENTRYPOINT |

### 实战示例：CMD vs ENTRYPOINT

```dockerfile
# 镜像 A：用 CMD
FROM alpine:latest
CMD ["echo", "hello"]
```

```bash
docker run cmd-test
# 输出：hello

docker run cmd-test world
# 输出：world
# （"echo hello" 被完全替换成 "world"）
```

```dockerfile
# 镜像 B：用 ENTRYPOINT
FROM alpine:latest
ENTRYPOINT ["echo", "hello"]
```

```bash
docker run entry-test
# 输出：hello

docker run entry-test world
# 输出：hello world
# （"echo hello" 是固定的，"world" 被追加在 hello 后面）
```

看到了吗？CMD 被**替换**了；ENTRYPOINT 被**追加**了。这就是它们最核心的行为差异。

### ENTRYPOINT 的典型用途

```
# 把镜像变成一个"可执行程序"
ENTRYPOINT ["curl"]
# docker run myimage https://example.com
# → curl https://example.com

ENTRYPOINT ["python"]
# docker run myimage script.py
# → python script.py
```

> 用 `ENTRYPOINT` 的镜像，更像一个**命令行工具**——镜像名就是命令名，后面跟的参数就是命令参数。

---

## 三、exec 形式 vs shell 形式

### 两种形式的写法

```dockerfile
# exec 形式（推荐）
CMD ["executable", "param1", "param2"]
ENTRYPOINT ["executable", "param1"]

# shell 形式（不推荐）
CMD executable param1 param2
ENTRYPOINT executable param1
```

### 背后发生了什么？

**exec 形式**：Docker 直接执行你指定的程序。容器的 PID 1 就是你的程序。

```
docker run myimage
    │
    ▼
PID 1: nginx -g "daemon off;"    ← 直接启动 nginx，PID 1 就是 nginx
```

**shell 形式**：Docker 先启动 `/bin/sh -c`，然后在 shell 里执行你的命令。容器的 PID 1 是 `/bin/sh`，不是你的程序。

```
docker run myimage
    │
    ▼
PID 1: /bin/sh -c "nginx -g 'daemon off;'"
           │
           ▼
        nginx（子进程，不是 PID 1）
```

### 为什么这很重要？—— 信号传递问题

在 Linux 中，当你 `docker stop` 一个容器时，Docker 向容器的 **PID 1** 发送 `SIGTERM` 信号，给它 10 秒时间优雅退出。如果 10 秒后还没退出，Docker 发 `SIGKILL` 强制杀死。

问题出在哪？

```
shell 形式的 CMD：
  PID 1 = /bin/sh
    └── PID 7 = nginx（子进程）

  docker stop → SIGTERM → /bin/sh
  /bin/sh 收到 SIGTERM，但它**不会**把这个信号转发给 nginx。
  nginx 不知道自己该停了，继续运行。
  10 秒后 → SIGKILL → /bin/sh（死了）→ nginx 变孤儿被强制杀死。
  优雅退出失败！nginx 没有机会清理连接、刷新缓冲区。
```

```
exec 形式的 CMD：
  PID 1 = nginx

  docker stop → SIGTERM → nginx（直接收到）
  nginx 优雅地关闭连接、保存状态、退出。
  docker stop 在 2 秒内完成。
```

**结论**：用 shell 形式，你的程序不是 PID 1，收不到 Docker 的信号。`docker stop` 每次都等到超时（10 秒）才强制杀死。**永远用 exec 形式。**

### 但 shell 形式有一个好处：可以使用 shell 特性

```dockerfile
# shell 形式可以利用管道、变量展开等 shell 特性
CMD echo "当前时间：$(date)"

# exec 形式做不到，因为 exec 形式不启动 shell
CMD ["echo", "当前时间：$(date)"]
# 输出：当前时间：$(date)（变量没被展开！）
```

如果你确实需要 shell 特性（比如管道），可以这样做：

```dockerfile
# ✅ 手动启动 shell，用 exec 形式传递命令
CMD ["/bin/sh", "-c", "echo \"当前时间：$(date)\""]
```

这样 PID 1 是 `/bin/sh`，信号问题依旧存在。但至少你**明确知道**自己在用 shell，这是有意为之。

---

## 四、CMD + ENTRYPOINT 配合使用

这是 Dockerfile 最强大的组合模式，也是最容易写错的模式。

### 黄金搭档模式

```dockerfile
ENTRYPOINT ["executable", "fixed_param"]
CMD ["default_param1", "default_param2"]
```

规则：
- ENTRYPOINT 定义**执行什么程序**（固定的）
- CMD 定义**程序的默认参数**（可被 `docker run` 后的参数覆盖）

### 实战：做一个 curl 工具镜像

```dockerfile
FROM alpine:latest

# 安装 curl
RUN apk add --no-cache curl

# ENTRYPOINT：固定执行 curl
ENTRYPOINT ["curl"]

# CMD：默认参数（如果不传参数，就 curl 百度）
CMD ["--help"]
```

```bash
# 场景 A：不加参数 → CMD 生效
docker run my-curl
# 等价于：curl --help
# 输出：curl 的帮助信息

# 场景 B：传入 URL → CMD 被覆盖
docker run my-curl https://www.example.com
# 等价于：curl https://www.example.com
# 输出：example.com 的 HTML 内容

# 场景 C：传入 curl 完整参数
docker run my-curl -s -o /dev/null -w "%{http_code}" https://www.example.com
# 等价于：curl -s -o /dev/null -w "%{http_code}" https://www.example.com
# 输出：200

# 镜像名 = curl 命令名！行云流水！
```

> 这就是 ENTRYPOINT + CMD 的魔力：**镜像变成了一个可执行程序。** `docker run my-curl 参数` 等同于 `curl 参数`。你的镜像是"用法自然"的——用户用它的方式，和用命令行工具一模一样。

### 实战：做一个带默认配置的应用镜像

```dockerfile
FROM node:20-alpine

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .

# ENTRYPOINT：固定执行 node
ENTRYPOINT ["node"]

# CMD：默认执行的文件
CMD ["server.js"]
```

```bash
# 场景：正常运行
docker run my-node-app
# 等价于：node server.js

# 场景：运行其他脚本
docker run my-node-app debug.js
# 等价于：node debug.js

# 场景：交互模式（进入 REPL）
docker run -it my-node-app
# 等价于：node（不加参数，进入 REPL）
```

### 全表总结：CMD / ENTRYPOINT / docker run 参数的组合行为

| Dockerfile | `docker run myimage` | `docker run myimage arg` |
|-----------|---------------------|-------------------------|
| `CMD ["a", "b"]` | 执行 `a b` | 执行 `arg`（CMD 被覆盖） |
| `ENTRYPOINT ["x", "y"]` | 执行 `x y` | 执行 `x y arg`（arg 追加） |
| `ENTRYPOINT ["x"]` + `CMD ["y"]` | 执行 `x y` | 执行 `x arg`（CMD 被覆盖） |
| 都没有 | 报错 | 报错 |

记住这张表，CMD 和 ENTRYPOINT 的所有困惑都能解开。

---

## 五、实战：制作一个 ENTRYPOINT + CMD 配合的完整镜像

我们将做一个"文件信息查看器"镜像——默认显示镜像里的文件信息，但允许用户传自定义参数。

### 步骤 1：写 Dockerfile

```dockerfile
FROM alpine:latest

# 创建一个测试文件
RUN echo "Hello from Docker entrypoint demo!" > /data.txt && \
    echo "This file was created at build time." >> /data.txt && \
    echo "You can override the default behavior." >> /data.txt

# ENTRYPOINT：固定执行 cat（显示文件内容）
ENTRYPOINT ["cat"]

# CMD：默认显示 /data.txt
CMD ["/data.txt"]
```

### 步骤 2：构建

```bash
docker build -t file-viewer:v1 .
```

### 步骤 3：运行并验证三种场景

```bash
# 场景 1：默认行为 —— 显示 /data.txt
docker run file-viewer:v1
# 输出 /data.txt 的内容

# 场景 2：显示其他文件 —— CMD 被覆盖
docker run file-viewer:v1 /etc/hostname
# 输出容器的主机名

# 场景 3：强制覆盖 ENTRYPOINT（罕见场景，用于调试）
docker run --entrypoint /bin/sh file-viewer:v1
# 进入 shell 而不是执行 cat
# 等价于：/bin/sh（cat 完全不走）
```

> `--entrypoint` 只在调试或特殊需求时使用。正常使用不要改它。

---

## 六、为什么推荐 exec 形式？——深度解析

### 信号传递问题的实操演示

先做一个 shell 形式的镜像：

```dockerfile
# shell 形式
FROM alpine:latest
CMD sleep 1000
```

构建并运行：

```bash
docker build -t shell-test .
docker run -d --name shell-demo shell-test
```

查看进程树：

```bash
docker exec shell-demo ps aux
# PID   USER     TIME  COMMAND
#     1 root      0:00 /bin/sh -c sleep 1000    ← PID 1 是 /bin/sh！
#     7 root      0:00 sleep 1000                ← sleep 是子进程
```

现在 `docker stop`：

```bash
time docker stop shell-demo
# 等待……等待……等待……
# docker stop shell-demo  0.05s user 0.02s system 0% cpu 10.253s total
#                                                     ──┬───
#                                              等了 10 秒！
```

为什么等了 10 秒？因为 `docker stop` 发了 SIGTERM 给 PID 1 (`/bin/sh`)，但 `/bin/sh` **不转发信号**给 `sleep`。Docker 等了 10 秒，没收到响应，发了 SIGKILL 强制杀死。

现在对比 exec 形式：

```dockerfile
# exec 形式
FROM alpine:latest
CMD ["sleep", "1000"]
```

```bash
docker build -t exec-test .
docker run -d --name exec-demo exec-test

docker exec exec-demo ps aux
# PID   USER     TIME  COMMAND
#     1 root      0:00 sleep 1000    ← PID 1 是 sleep！

time docker stop exec-demo
# docker stop exec-demo  0.02s user 0.01s system 2% cpu 1.214s total
#                                                     ──┬──
#                                              不到 2 秒！
```

### 什么时候可以用 shell 形式？

只有两种场景：

1. **你真的需要 shell 特性**（管道、变量展开、重定向），并且你清楚信号传递问题的代价。
2. **基础镜像没有你需要的可执行文件**，你需要 shell 来组合多个命令（但这种情况应该写一个启动脚本，而不是在 CMD 里硬塞）。

---

## 七、我做得对不对？

### 验证方法

```bash
# 1. 构建 file-viewer 镜像
docker build -t file-viewer:v1 .

# 2. 默认运行（CMD 生效）
docker run file-viewer:v1
# 预期：显示 /data.txt 的内容

# 3. 传入自定义参数（CMD 被覆盖）
docker run file-viewer:v1 /etc/alpine-release
# 预期：显示 alpine 的版本号（不是 /data.txt 的内容）

# 4. 验证 exec 形式 —— 进入容器看 PID 1
docker run -d --name fv-test file-viewer:v1
docker exec fv-test ps aux
# 预期：PID 1 是 cat（不是 /bin/sh）

# 5. 验证 docker stop 的速度
time docker stop fv-test
# 预期：应该在 2 秒内完成（不是 10 秒）

# 6. 验证 --entrypoint 能覆盖 ENTRYPOINT
docker run --entrypoint echo file-viewer:v1 "entrypoint was overridden"
# 预期：输出 "entrypoint was overridden"
```

---

## 八、不对怎么办？

### 常见错误 1：CMD 和 ENTRYPOINT 都用了 shell 形式

```dockerfile
# ❌ 错误
CMD nginx -g "daemon off;"
ENTRYPOINT node
```

❌ 原因：shell 形式导致 `/bin/sh` 成为 PID 1，信号传递出问题，容器优雅退出失败。

✅ 正确：

```dockerfile
CMD ["nginx", "-g", "daemon off;"]
ENTRYPOINT ["node"]
```

### 常见错误 2：`docker run` 后跟了参数，CMD 消失

```bash
# 你以为在追加参数？
docker run myimage --port 8080
# 实际上：CMD 被 --port 8080 完全替换了
```

❌ 原因：CMD 的行为是"覆盖"，不是"追加"。如果你想要"追加"语义，用 ENTRYPOINT。

✅ 正确做法：

```dockerfile
# 如果参数应该追加而不是替换
ENTRYPOINT ["node", "server.js"]
CMD ["--port", "3000"]
```

```bash
docker run myimage
# → node server.js --port 3000

docker run myimage --port 8080
# → node server.js --port 8080（CMD 的默认值被替换，参数追加到 ENTRYPOINT）
```

### 常见错误 3：exec 形式的 JSON 数组语法错误

```dockerfile
# ❌ 错误：不是合法的 JSON 数组
CMD ["nginx" "-g" "daemon off;"]
#     少了逗号！

# ❌ 错误：用了单引号
CMD ['nginx', '-g', 'daemon off;']
# JSON 要求双引号

# ❌ 错误：末尾多了逗号
CMD ["nginx", "-g", "daemon off;",]

# ✅ 正确
CMD ["nginx", "-g", "daemon off;"]
```

exec 形式是一个 **JSON 数组**，语法必须是合法的 JSON。逗号分隔，双引号包裹字符串。一个逗号的错误，Docker 会直接报错。

### 常见错误 4：CMD 和 ENTRYPOINT 同时用 shell 形式，行为诡异

```dockerfile
ENTRYPOINT echo "hello"
CMD echo "world"
```

❌ 原因：两条都用 shell 形式时，CMD 完全失效。ENTRYPOINT 不会把 CMD 作为默认参数。

✅ 正确：

```dockerfile
ENTRYPOINT ["echo", "hello"]
CMD ["world"]
# docker run myimage → hello world
```

### 常见错误 5：`--entrypoint` 覆盖后不知道怎么恢复

```bash
# 调试时覆盖了 ENTRYPOINT
docker run --entrypoint /bin/sh -it myimage
# 在里面操作完，exit 退出

# 但下次 docker run myimage 还是用原来的 ENTRYPOINT
# --entrypoint 只影响那一次 docker run，不修改镜像本身
```

`--entrypoint` 和 `-e`、`-p` 一样，是运行时选项，只影响当次运行，不会改变镜像。

---

## 本章小结

| 本章学了什么 | 对应命令/概念 | 注意事项 |
|-------------|-------------|---------|
| CMD | `CMD ["executable", "arg"]` | 默认启动命令；可被 `docker run` 参数覆盖 |
| ENTRYPOINT | `ENTRYPOINT ["executable"]` | 固定入口程序；`docker run` 参数作为追加参数 |
| CMD 被覆盖 | `docker run myimage arg` → CMD 没了 | CMD 是"替换"，不是"追加" |
| ENTRYPOINT 追加 | `docker run myimage arg` → 追加到 ENTRYPOINT | ENTRYPOINT 是固定的，"追加"语义 |
| exec 形式 | `CMD ["a", "b"]` | **推荐**：程序直接成为 PID 1，信号正常传递 |
| shell 形式 | `CMD a b` | **不推荐**：/bin/sh 成为 PID 1，信号传不到程序 |
| 信号传递 | SIGTERM → PID 1 → 程序 | shell 形式下 /bin/sh 不转发信号 → `docker stop` 等 10 秒 |
| CMD + ENTRYPOINT 配合 | ENTRYPOINT = 程序，CMD = 默认参数 | 黄金搭档模式，镜像变成"命令行工具" |
| `--entrypoint` | 运行时覆盖 ENTRYPOINT | 只影响当次运行，不改镜像 |
| exec 形式 JSON 语法 | 双引号、逗号分隔 | 语法错误直接报错，写时仔细检查 |

> **[可暂停点 3/8]**：第三篇结束。重启验证命令：
>
> ```bash
> docker images
> # 查看你目前为止构建的所有镜像
>
> docker build --help
> # 回顾 docker build 的可用选项
>
> # 运行你之前构建的镜像，确认它们都还能跑：
> docker run --rm myfirst:v1
> docker run --rm alpine-nginx:v1
> docker run --rm my-nginx-web:v1
> docker run --rm node-env-demo:v1
> docker run --rm file-viewer:v1
> ```
>
> 如果所有镜像都能成功运行，说明第三篇的所有操作都是正确且可重复的。

---

## 本篇最可能出错的地方及原因

### 1. shell 形式写惯了，所有 CMD/ENTRYPOINT 都用 shell 形式

**原因**：shell 形式写法自然（`CMD echo hello`），和终端命令一样，新手上手就用。很多人学了 Dockerfile 半年都不知道还有一种"exec 形式"。

**后果**：`docker stop` 每次都超时 10 秒。生产环境中，优雅退出的逻辑全废——连接没关、缓存没刷、日志没写完，容器就被 SIGKILL 强杀了。

**排查**：`docker exec 容器名 ps aux`。如果 PID 1 是 `/bin/sh` 而不是你的程序，你就踩了这个坑。

**口诀**：**CMD/ENTRYPOINT 永远用 JSON 数组（exec 形式）。** 需要 shell 特性时，手动 `CMD ["/bin/sh", "-c", "你的命令"]`。

### 2. 以为 CMD 是"追加参数"，写了 `CMD ["--port", "3000"]` 发现完全没用

```dockerfile
ENTRYPOINT ["node"]
CMD ["server.js", "--port", "3000"]
```

然后你 `docker run myimage --port 8080`，预期 `node server.js --port 8080`，实际是 `node --port 8080`——`server.js` 丢了！

**原因**：`docker run` 后面的参数**完全替换 CMD**，不是追加到 CMD 后面。只有 `ENTRYPOINT` 的参数不会被替换。

**正确设计**：把必需的参数放进 ENTRYPOINT，可选的默认参数放进 CMD。

```dockerfile
# ✅ 正确
ENTRYPOINT ["node", "server.js"]
CMD ["--port", "3000"]
# docker run myimage → node server.js --port 3000
# docker run myimage --port 8080 → node server.js --port 8080
```

### 3. CMD 和 ENTRYPOINT 都写，混淆谁的参数被谁追加

记住口诀："你 ENTRY 他 CMD"——

- **ENTRY**POINT 是**入口**（entry），固定不变。
- **CMD** 提供默认参数，可以被**命令行**（command line）覆盖。

用例子记：
```dockerfile
ENTRYPOINT ["curl"]
CMD ["--help"]
```

```bash
docker run mycurl                  # curl --help
docker run mycurl example.com      # curl example.com       ← CMD 被覆盖
docker run mycurl -I example.com   # curl -I example.com    ← CMD 被覆盖
```

### 4. exec 形式的 JSON 数组写错（少了逗号，用了单引号）

```dockerfile
# ❌ 少了逗号
CMD ["nginx" "-g" "daemon off;"]

# ❌ 用了单引号
CMD ['nginx', '-g', 'daemon off;']
```

Docker 对 JSON 格式很严格。写了第一条的人，通常是复制粘贴了文档但漏了逗号。排查：`docker build` 会直接报错，错误信息里会提示 JSON parsing error。

### 5. Alpine 的 `/bin/sh` 是 BusyBox，行为和 bash 不一样

Alpine 用的是 BusyBox 的 `sh`，不是 `bash`。某些 shell 特性（如 `source`、`[[ ]]`）在 Alpine 的 `sh` 里不可用。

```dockerfile
# ❌ 在 Alpine 里用 bash 语法
CMD source /app/env.sh && node server.js
# source 在 BusyBox sh 里行为可能不同

# ✅ 应对
CMD ["/bin/sh", "-c", ". /app/env.sh && node server.js"]
# 或者改基础镜像
FROM ubuntu:22.04  # Ubuntu 里 /bin/sh → dash，或装 bash
```