# 10 — 第一个 Dockerfile

> - 对应文档版本：Docker精通教程 outline v1
> - 适用环境：任何已安装 Docker 的系统
> - 读者角色：已掌握 `docker run` 基础，准备自己构建镜像的开发者
> - 预计耗时：新手 35 分钟 / 熟手 15 分钟
> - 前置教程：第 03 章（`docker run` 基础）
> - 可视化：无

---

## 我在做什么？

前几章你一直在用别人做好的镜像——`docker run ubuntu`、`docker run nginx`。这些镜像是谁做的？怎么做的？

从这一章开始，你要自己动手做镜像。你会写你的第一份 **Dockerfile** *此术语见附录C*——一个纯文本文件，告诉 Docker"怎么把代码和环境打包成一个镜像"。你不再是一个只会用别人菜的食客，你要开始学做菜了。

学完这一章，你能：
- 看懂一个 Dockerfile 的基本骨架
- 用 `docker build` 把 Dockerfile 变成镜像
- 理解"构建上下文"是什么，为什么那个 `.` 很关键
- 给自己构建的镜像打标签（tag）

---

## 一、Dockerfile 是什么？

### 为什么要写 Dockerfile？—— 用 `docker commit` 不好吗？

你在第 03 章学了，`docker run -it ubuntu bash` 进入容器后可以装软件。你可能会想：那我装好软件，退出容器，能不能把这个"装好了软件的容器"保存成镜像？

能。Docker 确实提供了一个命令：

```bash
docker commit 容器名 新镜像名
```

这条命令会把容器当前的状态**拍一张快照**，存成一个新镜像。

但你最好不要用。为什么？

<div align="center">

```
docker commit 的问题：

  你：  docker run ubuntu
  你：  apt update && apt install nginx
  你：  docker commit my-container my-nginx
  同事：docker run my-nginx
  同事：nginx 怎么起不来？你上次到底改了哪些配置？
  你：  呃……我不记得了……

  docker commit 就像一道菜，"做法"丢失了，只剩"成品"。
  别人吃着觉得咸，但不知道你放了 3 勺盐还是 5 勺盐。
```

</div>

而 Dockerfile 不同：

```
Dockerfile 就像一道菜的"菜谱"：
  FROM 基础食材
  RUN  加调料、翻炒
  COPY 摆盘
  CMD  出锅上桌

任何看过菜谱的人都知道这道菜怎么做、可以调整哪里。
换到另一间厨房（另一台机器），照菜谱重做，味道一模一样。
```

### 一句话定义

> **Dockerfile 是一个纯文本文件，里面写满了"怎么构建一个镜像"的指令。每一条指令，对应镜像的一层。**

它和 `docker commit` 的核心区别：

| 维度 | `docker commit` | Dockerfile |
|------|----------------|------------|
| 可重复性 | 差。你不知道之前做了什么操作 | 好。每条指令都是明文的 |
| 版本控制 | 不能。无法纳入 Git 管理 | 能。Dockerfile 就是代码 |
| 可审查性 | 低。黑箱产物 | 高。逐行可读 |
| 团队协作 | 差。"你手动改了啥？" | 好。看 Dockerfile 就清楚了 |
| 镜像大小 | 容易膨胀（残留垃圾） | 可控（可以清理） |

> **想多一点**：你可以把 `docker commit` 想象成**拍照片**——你只能看到最终结果，看不到形成过程。Dockerfile 是**录像**——你能回放构建的每一步。在软件工程里，"可重复"比"省事"重要一百倍。一个只有你知道怎么构建的镜像，等于一个只有你能维护的系统。

---

## 二、Dockerfile 的基本结构

一个最简单的 Dockerfile 长这样：

```dockerfile
FROM alpine:latest
RUN echo "正在构建镜像..."
COPY hello.txt /hello.txt
CMD echo "容器启动了！"
```

只有四行？对，够了。这四行就是 Dockerfile 的四大支柱：

```dockerfile
FROM alpine:latest        # 1. 基于哪个镜像开始
RUN echo "正在构建..."     # 2. 构建时执行什么命令
COPY hello.txt /hello.txt  # 3. 把什么文件复制进镜像
CMD echo "容器启动了！"     # 4. 容器启动时执行什么命令
```

| 指令 | 作用 | 执行时机 | 类比 |
|------|------|---------|------|
| `FROM` | 指定基础镜像 | 构建开始时 | "用什么面粉做面包" |
| `RUN` | 在镜像里执行命令 | **构建时**（`docker build`） | "和面、发酵" |
| `COPY` | 从宿主机复制文件到镜像 | **构建时**（`docker build`） | "往里加馅料" |
| `CMD` | 容器启动时的默认命令 | **运行时**（`docker run`） | "面包出炉后怎么切" |

> **关键区分**：`RUN` 和 `CMD` 的执行时机完全不同。`RUN` 是**做面包的过程**（构建时），`CMD` 是**面包拿来怎么吃**（运行时）。如果你想把软件装进镜像，用 `RUN`；如果你想定义容器启动后干什么，用 `CMD`。

---

## 三、`docker build` 流程：从 Dockerfile 到镜像

### 命令格式

```bash
docker build -t 镜像名:标签 构建上下文路径
```

比如：

```bash
docker build -t myapp:v1 .
```

### 背后发生了什么？

当你敲下 `docker build -t myapp:v1 .`，Docker 做的事情：

```
你敲下 docker build -t myapp:v1 .
           │
           ▼
┌─────────────────────────────────────────────────┐
│ 步骤 1：打包构建上下文                           │
│         把 "." (当前目录) 下的所有文件打包，      │
│         发给 Docker 守护进程                     │
│         （.dockerignore 里的文件除外，第 12 章讲）│
└──────────────────────┬──────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────┐
│ 步骤 2：逐条执行 Dockerfile 指令                 │
│         FROM alpine → 拉取 alpine 镜像（如无本地）│
│         RUN echo ... → 启动临时容器，执行命令，    │
│                         保存为新层                │
│         COPY ...     → 把文件写入镜像层           │
│         CMD ...      → 记录启动命令（不执行）      │
└──────────────────────┬──────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────┐
│ 步骤 3：所有指令执行完毕，生成一个镜像            │
│         给它打上标签 myapp:v1                     │
│         存到本地镜像仓库                          │
└─────────────────────────────────────────────────┘
```

> 每一行 Dockerfile 指令 = 一个**镜像层** *此术语见附录C*。`FROM` 是一层，`RUN` 是一层，`COPY` 是一层。最终镜像 = 所有层叠在一起。你在下一章会学到层缓存是什么、怎么利用它加速构建。

---

## 四、构建上下文：那个 `.` 到底是什么？

### 别小看这个点

```bash
docker build -t myapp:v1 .
#                         ↑
#                    这个点是什么？
```

这个 `.` 不是"当前目录"的字面意思，而是告诉 Docker：**"把当前目录下的所有文件，打包发给 Docker 守护进程，作为构建上下文。"**

### 我做得对不对？—— 一个小实验

在你的终端里执行：

```bash
# 创建一个临时目录
mkdir docker-test && cd docker-test

# 创建一个巨大的无意义文件
dd if=/dev/zero of=huge_file bs=1M count=500 2>/dev/null || fsutil file createnew huge_file 1000000
# （上面两条命令选一条能用的，目的只是造一个大文件）

# 创建一个 Dockerfile
echo "FROM alpine:latest" > Dockerfile
echo 'CMD echo "hello"' >> Dockerfile

# 执行构建，注意发送给守护进程的数据量
docker build -t test-context .
```

你会看到输出开头类似：

```
Sending build context to Docker daemon  525.3MB
```

Docker **把当前目录下所有文件（包括你那个 500MB 的大文件）打包发给守护进程了**。

### 这意味着什么？

```
❌ 错误做法：
   cd /home/user
   docker build -t myapp:v1 .
   # 把 /home/user 下所有东西（几十 GB）
   # 打包发给 Docker 守护进程 → 巨慢无比

✅ 正确做法：
   cd /home/user/my-docker-project   # 只包含 Dockerfile 和必要文件
   docker build -t myapp:v1 .
   # 只打包这个项目目录 → 快
```

> **想多一点**："构建上下文"这个概念，很多 Docker 教程一笔带过，但这恰恰是新手最容易踩的坑之一。你的家目录里可能有几十 GB 的视频、代码仓库、node_modules。一句 `docker build .` 把它们全打包发给 Docker，就像你要寄一封信，却把整个房间里的东西都塞进了信封。更糟的是，docker build 默认从 Dockerfile 所在的目录打包上下文——你这个 `.` 指哪个目录，上下文就是哪个目录。

### COPY 指令和构建上下文的关系

`COPY` 只能复制**构建上下文之内的文件**。你不能 COPY 构建上下文之外的文件：

```dockerfile
# ❌ 错误：/etc/passwd 不在构建上下文里
COPY /etc/passwd /passwd

# ❌ 错误：../other-project 在上级目录，不在构建上下文里
COPY ../other-project /app
```

Docker 这样做是出于**安全考虑**。如果可以 COPY 任意路径，一个恶意的 Dockerfile 就能把宿主机的敏感文件打包进镜像。

---

## 五、`-t` 打标签：给你的镜像起名字

### 标签的格式

```bash
docker build -t 镜像名:版本号 .
#             ───┬─── ─┬──
#            名称    标签(tag)
```

示例：

```bash
docker build -t myapp:v1 .
docker build -t myapp:latest .
docker build -t myapp:v1.0.0 .
```

### 不写标签会怎样？

```bash
docker build .
# 构建成功，但镜像没有名字
```

```bash
docker images
# REPOSITORY   TAG       IMAGE ID       CREATED         SIZE
# <none>       <none>    a1b2c3d4e5f6   10 seconds ago  7.5MB
```

一个没有名字和标签的镜像，被称为**悬空镜像（dangling image）**。你只能靠 IMAGE ID 引用它——多不方便。

### 一次构建，多个标签

```bash
docker build -t myapp:v1 -t myapp:latest .
```

这会给同一个镜像打两个标签。就像一个人可以同时有"张三"和"阿三"两个称呼，指的是同一个人。

---

## 六、实战：写你的第一个 Dockerfile

### 准备工作

打开终端，找一个干净的目录：

```bash
mkdir my-first-dockerfile && cd my-first-dockerfile
```

### 步骤 1：创建 Dockerfile

用任意文本编辑器创建文件 `Dockerfile`（注意：**没有后缀名**，就叫 `Dockerfile`，不是 `Dockerfile.txt`）：

```dockerfile
# 基于 Alpine Linux——一个只有 ~5MB 的超精简 Linux
FROM alpine:latest

# 构建时打印一句话
RUN echo "镜像正在构建中..."

# 构建时创建一个小文件
RUN echo "这条信息是在构建时写入的" > /build-info.txt

# 容器启动时执行的默认命令
CMD echo "容器启动了！构建信息如下：" && cat /build-info.txt
```

### 步骤 2：构建镜像

```bash
docker build -t myfirst:v1 .
```

你会看到类似这样的输出：

```
[+] Building 1.5s (7/7) FINISHED
 => [1/3] FROM docker.io/library/alpine:latest
 => [2/3] RUN echo "镜像正在构建中..."
 => [3/3] RUN echo "这条信息是在构建时写入的" > /build-info.txt
 => exporting to image
 => => naming to docker.io/library/myfirst:v1
```

每一行 `=>` 是一条 Dockerfile 指令的执行结果。注意看：`RUN echo "镜像正在构建中..."` 输出了你的那行字，说明它真的在构建时执行了。

### 步骤 3：运行你的镜像

```bash
docker run myfirst:v1
```

预期输出：

```
容器启动了！构建信息如下：
这条信息是在构建时写入的
```

### 步骤 4：检查你有什么

```bash
docker images
# REPOSITORY   TAG       IMAGE ID       CREATED         SIZE
# myfirst      v1        abc123def456   1 minute ago    7.8MB
```

你刚刚从零构建了一个 Docker 镜像。它虽然简单，但它**是真正的镜像**——有名称、有标签、可以运行、可以分享。

---

## 七、我做得对不对？

### 验证方法

按顺序执行以下操作，全部成功才算通过：

```bash
# 1. 确认 Dockerfile 存在且内容正确
cat Dockerfile
# 应该看到 FROM、RUN、CMD 等指令

# 2. 构建镜像
docker build -t myfirst:v1 .
# 应该看到 "Successfully tagged myfirst:v1" 或类似信息

# 3. 运行镜像
docker run myfirst:v1
# 应该看到你的 CMD 输出

# 4. 查看镜像列表
docker images myfirst:v1
# 应该看到 REPOSITORY=myfirst, TAG=v1

# 5. 查看镜像的层历史
docker history myfirst:v1
# 应该看到每一层对应你的每条指令
```

**预期结果**：
- 步骤 2：无报错，构建成功
- 步骤 3：输出 `容器启动了！构建信息如下：` 和 `/build-info.txt` 的内容
- 步骤 5：能看到 `FROM`、`RUN`、`CMD` 对应的层

---

## 八、不对怎么办？

### 常见错误 1：文件名叫 `Dockerfile.txt` 或 `dockerfile`

```bash
docker build -t myapp:v1 .
# unable to prepare context: unable to evaluate symlinks
# in Dockerfile path: lstat Dockerfile: no such file or directory
```

❌ 你做错了什么：把文件命名成了 `Dockerfile.txt`（Windows 记事本默认行为），或者 `dockerfile`（小写 d）。

✅ 正确做法：文件名叫 `Dockerfile`，大小写完全一致，无后缀名。

```bash
# 在 Windows 上，用 VS Code 或 Notepad++ 创建，不要用记事本
# 在记事本里"另存为"时，文件名写 "Dockerfile"（带引号），编码选 UTF-8

# 确认文件名正确
ls -la   # Linux/Mac
dir      # Windows
# 看到 Dockerfile，不是 Dockerfile.txt
```

> Docker 默认只找当前目录下名为 `Dockerfile` 的文件。如果你非要用别的文件名（比如 `Dockerfile.dev`），需要用 `-f` 指定：`docker build -f Dockerfile.dev -t myapp:v1 .`

### 常见错误 2：`.dockerignore` 没配，构建上下文太大

```bash
docker build -t myapp:v1 .
# Sending build context to Docker daemon  2.146GB
# （然后卡住很久）
```

❌ 你做错了什么：在当前目录或其子目录下有巨大的文件（node_modules、视频、数据文件等）。

✅ 正确做法：要么换到一个干净的目录，要么创建 `.dockerignore` 文件（第 12 章详细讲）。

```bash
# 快速检查：当前目录有多大？
du -sh .                   # Linux/Mac

# 如果太大，新建一个干净目录专门放 Dockerfile
mkdir ~/docker-tutorial && cd ~/docker-tutorial
```

### 常见错误 3：忘了 `-t`，镜像没名字

```bash
docker build .
# 构建成功，但 docker images 显示 <none>:<none>
```

❌ 你做错了什么：没有用 `-t` 给镜像起名字。

✅ 正确做法：

```bash
docker build -t myapp:v1 .
```

以后每次 `docker build` 记得带 `-t 名字:标签`。名字是你的，标签是你的，忘了打标签的镜像是"流浪镜像"——你知道它在，但你叫不出它的名字。

### 常见错误 4：构建上下文路径写成了 Dockerfile 路径

```bash
# ❌ 错误
docker build -t myapp:v1 /path/to/Dockerfile
# Docker 会试图把 /path/to/Dockerfile 当成目录打包，而不是找 Dockerfile
```

✅ 正确做法：

```bash
cd /path/to/project
docker build -t myapp:v1 .
```

如果 Dockerfile 不在当前目录，用 `-f` 指定 Dockerfile 路径：

```bash
docker build -f /path/to/Dockerfile -t myapp:v1 /path/to/context
#            ───────┬──────────────        ────────┬────────
#            Dockerfile 文件路径            构建上下文目录
```

### 常见错误 5：CMD 在 `docker run` 后被覆盖了，觉得"CMD 没生效"

```bash
docker run myfirst:v1 echo "我覆盖了 CMD"
# 输出：我覆盖了 CMD
# 原先 CMD 里的 echo "容器启动了！..." 没有执行
```

这不是错误，这是 CMD 的特性。`docker run` 后面跟的命令会**覆盖** CMD。如果你想保留 CMD 行为，就不要在 `docker run` 后面加额外命令。第 14 章会详细讲 CMD 和 ENTRYPOINT 的区别。

---

## 本章小结

| 本章学了什么 | 对应命令/概念 | 注意事项 |
|-------------|-------------|---------|
| Dockerfile 是什么 | 文本文件，定义镜像构建步骤 | 比 `docker commit` 更可重复、可版本控制、可审查 |
| 四大支柱指令 | `FROM`、`RUN`、`COPY`、`CMD` | `RUN` 在构建时执行，`CMD` 在运行时执行，不要搞混 |
| `docker build` 流程 | 打包上下文 → 逐层执行 → 生成镜像 | 每一步都是独立的"层" |
| 构建上下文 | `docker build -t myapp .` 中的 `.` | 别在包含大文件的目录下执行 `docker build` |
| `-t` 打标签 | `-t 镜像名:版本号` | 不写 `-t` 会产生 `<none>:<none>` 的悬空镜像 |
| 文件名 | 必须叫 `Dockerfile` | 大小写严格一致，无后缀名，记事本保存时注意 |
| COPY 的安全约束 | 只能复制构建上下文之内的文件 | Docker 有意为之，防止敏感文件泄露 |

---

## 本篇最可能出错的地方及原因

### 1. 文件名大小写或后缀错误（Windows 用户最高发）

**原因**：Windows 记事本的默认保存行为会加 `.txt` 后缀，且用户不容易看到。你建的是 `Dockerfile.txt`，不是 `Dockerfile`。

**排查**：在终端里 `ls` 或 `dir`，看清楚完整文件名。如果显示 `Dockerfile.txt`，重命名删掉 `.txt`。

**预防**：用 VS Code、Notepad++ 等编辑器创建文件，或者终端里直接 `echo "FROM alpine" > Dockerfile` 创建。

### 2. 构建上下文路径选错，"Sending build context" 几百 MB

**原因**：在不该执行 `docker build` 的目录下执行了 `docker build`。比如在家目录下，或者在包含 `node_modules` 的项目根目录下。

**排查**：看 `docker build` 输出的第一行：`Sending build context to Docker daemon XXXMB`。如果 XXX 很大，说明上下文选错了。

**解决**：换到一个只包含 Dockerfile 和必要文件的干净目录。

### 3. RUN 和 CMD 搞混——在 RUN 里写启动命令

**原因**：以为 `RUN` 就是"让容器运行的命令"——名字确实误导人。

❌ 典型错误：

```dockerfile
FROM alpine
RUN echo "服务启动中..."   # 这是在构建时执行的，不是运行时！
```

✅ 正确：

```dockerfile
FROM alpine
CMD echo "服务启动中..."   # 这才是容器启动时执行的
```

**记忆口诀**：RUN = build time（构建时做的事），CMD = run time（运行时做的事）。RUN 是给镜像"预备食材"，CMD 是给容器"下锅"。

### 4. 每次 `docker run` 后面跟命令，发现 CMD 不生效

**原因**：`docker run 镜像 命令` 中的"命令"会覆盖 Dockerfile 里的 CMD。这是 CMD 的设计特性，不是 bug。

**解决**：测试 CMD 时不要加额外参数：`docker run myapp:v1` 就够了。CMD 和 ENTRYPOINT 的配合使用见第 14 章。