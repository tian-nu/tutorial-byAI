# 05 — docker run 详解

> - 对应文档版本：Docker精通教程 outline v1
> - 适用环境：任何已安装 Docker 的系统
> - 读者角色：已完成 01-04 章的开发者，了解镜像基本概念
> - 预计耗时：新手 25 分钟 / 熟手 10 分钟
> - 前置教程：第 04 章（理解镜像与 Tag）
> - 可视化：无

---

## 我在做什么？

你已经用过 `docker run` 了——`docker run hello-world`、`docker run -it ubuntu bash`。但你有没有发现，`docker run` 后面可以跟一大堆选项，每个选项都有不同的效果？

这一章，我们把 `docker run` 彻底拆开。学完之后，你会知道什么时候该用 `-d` 后台运行，什么时候该用 `--rm` 自动清理，什么时候该用 `--restart` 让容器挂了自动重启。

学完这一章，你能：
- 写出完整语法的 `docker run` 命令，理解每个选项的含义
- 区分前台运行和后台运行，知道为什么 `-d` 这么重要
- 用 `--name` 给容器起名字，用 `--rm` 让容器退出后自动删除
- 配置 `--restart` 策略，让容器在崩溃后自动恢复
- 用 `-p` 端口映射把容器内的服务暴露到宿主机

---

## 一、`docker run` 的完整语法：一张地图

### 先把全貌看清楚

```bash
docker run [OPTIONS] IMAGE[:TAG] [COMMAND] [ARG...]
```

各部分的含义：

```
docker run -d --name my-nginx -p 8080:80 --restart always nginx:1.27.4
│      │   │   │          │           │         │                │
│      │   │   │          │           │         │                └── 镜像:标签
│      │   │   │          │           │         └── 重启策略：always
│      │   │   │          │           └── 端口映射：宿主机8080 → 容器80
│      │   │   │          └── 容器名：my-nginx
│      │   │   └── 后台运行
│      │   └── 子命令：创建并启动容器
│      └── Docker 客户端
└── 终端提示符
```

> 这个命令你现在可能觉得长，但学完本章，你会觉得它每一部分都"理所当然"。

### 选项的顺序

Docker 对选项的顺序**没有严格要求**，但有一个约定俗成的推荐顺序：

```bash
docker run [运行模式选项] [标识选项] [网络/存储选项] [资源限制选项] IMAGE [COMMAND]
```

比如：

```bash
# 推荐顺序（先运行模式，再标识，再网络/存储）
docker run -d --name my-nginx -p 8080:80 -v /data:/usr/share/nginx/html nginx:1.27.4

# 下面的写法也能跑，但读起来别扭
docker run -p 8080:80 -d -v /data:/usr/share/nginx/html --name my-nginx nginx:1.27.4
```

两者都能跑，但前者读起来更顺：先知道"后台运行"，再知道"叫 my-nginx"，然后知道"端口映射到 8080"。

---

## 二、前台 vs 后台：`-d` 选项

这是 `docker run` 最常用、也最容易犯错的选项。

### 前台运行（默认）

```bash
docker run nginx:1.27.4
```

当你执行这个命令，你的终端会被"占用"——你会看到 nginx 的日志输出滚动，**Ctrl+C 会停止容器**。

```
/docker-entrypoint.sh: /docker-entrypoint.d/ is not empty...
/docker-entrypoint.sh: Looking for shell scripts in /docker-entrypoint.d/
...
2026/01/01 12:00:00 [notice] 1#1: start worker process 30
```

此时：
- 你的终端被"卡住"了，不能输入其他命令
- 按 `Ctrl+C` → 容器收到中断信号 → 停止
- 关闭终端窗口 → 容器也会停止

> 前台模式适合调试：你想看容器启动时发生了什么，有没有报错。但生产环境这么跑就废了——你关了终端，服务就停了。

### 后台运行（`-d`，`--detach`）

```bash
docker run -d nginx:1.27.4
```

输出只有一行：**容器 ID**（长格式）。

```
a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6
```

此时：
- 终端立刻返回，你可以继续输入其他命令
- 容器在后台默默运行
- 关闭终端窗口 → 容器**继续运行**（和前台模式的关键区别）

**`-d`** *此术语见附录C* 的全称是 `--detach`，意思是"分离"——把你的终端和容器的生命周期分离。

### 典型错误：忘记 `-d`

❌ 新手最常犯的错误：

```bash
# 想启动 nginx 后台运行，但忘了加 -d
docker run nginx:1.27.4
# 终端被卡住，不知所措，按 Ctrl+C，容器停了
```

✅ 正确做法：

```bash
docker run -d nginx:1.27.4
# 终端立刻返回，容器在后台运行
```

### 前台 vs 后台对比

| 特性 | 前台（默认） | 后台（`-d`） |
|------|------------|------------|
| 终端是否被占用 | 是 | 否 |
| 能看到日志吗 | 实时看到 | 需要用 `docker logs` 查看 |
| Ctrl+C 会停止容器吗 | 会 | 不会（Ctrl+C 只影响终端） |
| 关闭终端会停止容器吗 | 会 | 不会 |
| 适合场景 | 调试、临时测试 | 生产环境、长期运行的服务 |

---

## 三、容器命名：`--name`

### 为什么需要命名？

如果你不指定 `--name`，Docker 会给容器随机分配一个名字，比如：

```
quirky_bose
funny_volhard
admiring_curie
```

这些名字是 Docker 随机组合形容词 + 科学家名字生成的。**很可爱，但完全不可控。**

```bash
# 不指定名字
docker run -d nginx:1.27.4
# 名字：quirky_bose（每次都不一样）

# 指定名字
docker run -d --name my-nginx nginx:1.27.4
# 名字：my-nginx（你指定的）
```

**`--name`** *此术语见附录C* 让你能用人能读懂的标识符来操作容器，而不是靠记忆 `a1b2c3d4e5f6` 这种 ID。

```bash
# 有名字之后，一切操作都方便了
docker logs my-nginx      # 查看日志
docker stop my-nginx      # 停止
docker start my-nginx     # 启动
docker rm my-nginx        # 删除
```

### 命名规则

- 只能包含字母、数字、下划线、连字符、点号
- 不能和已有的容器重名（包括已停止的）
- 最大 128 个字符

```bash
# ❌ 重复名字会报错
docker run -d --name my-nginx nginx:1.27.4
docker run -d --name my-nginx nginx:1.27.4
# Error: Conflict. The container name "/my-nginx" is already in use by container "abc123"

# 解决方法：先删除旧容器，或换一个名字
docker rm my-nginx
docker run -d --name my-nginx nginx:1.27.4
```

---

## 四、退出自动删除：`--rm`

### 这个选项解决什么问题？

默认情况下，容器停止后**不会自动删除**。也就是说，每次你 `docker run` 一个临时容器，它就留在那，占用空间。几天下来，`docker ps -a` 能看到几十个已停止的容器。

```bash
# 每次测试都留下一个已停止的容器
docker run alpine echo "test 1"
docker run alpine echo "test 2"
docker run alpine echo "test 3"
docker ps -a
# 看到三个 Exited 容器，占着位置
```

**`--rm`** *此术语见附录C* 让容器在**退出后自动删除**，不留痕迹。

```bash
# 容器退出后自动删除
docker run --rm alpine echo "test 1"
docker run --rm alpine echo "test 2"
docker run --rm alpine echo "test 3"
docker ps -a
# 干干净净，没有一个 Exited 容器
```

### 什么时候用 `--rm`？

| 场景 | 用 `--rm` 吗？ | 理由 |
|------|-------------|------|
| 临时测试一个命令 | ✅ 用 | 用完就丢，没必要留着 |
| 一次性任务（数据迁移、备份） | ✅ 用 | 任务完成容器就没用了 |
| 长期运行的 Web 服务 | ❌ 不用 | 你需要容器停了之后还能 `docker start` 重新启动 |
| 调试容器，想保留现场 | ❌ 不用 | 容器出错后你想进去看日志或文件 |

### `--rm` 和 `-d` 可以一起用吗？

可以。容器在后台运行，当你用 `docker stop` 停止它时，它会自动删除。

```bash
docker run -d --rm --name temp-nginx nginx:1.27.4
docker stop temp-nginx
# 容器停止后自动删除
docker ps -a | grep temp-nginx
# 没有输出，容器已删除
```

> **想多一点**：`--rm` 在 CI/CD 流水线中极其有用。流水线里跑的容器（比如运行测试、构建代码）都是一次性的，任务完成就删。不清理的话，CI 服务器几周就被死容器塞满了。

---

## 五、端口映射：`-p`

### 容器和宿主机之间的"墙"

默认情况下，容器内的网络是**隔离的**。你在容器里跑了一个 Nginx，它监听了 80 端口，但只有容器内部能访问。从你的浏览器访问 `localhost:80`，你访问的是**宿主机的 80 端口**，不是容器的 80 端口。

```
┌─────────────────────────────────────────┐
│  宿主机                                  │
│                                          │
│  localhost:80 → 宿主机自己的 80 端口      │
│                                          │
│  ┌────────────────────────────┐          │
│  │  Nginx 容器                 │          │
│  │  容器内 80 端口 ← 只有容器内部能访问  │
│  └────────────────────────────┘          │
└─────────────────────────────────────────┘
```

`-p`（`--publish`）就是在这堵墙上**开一扇门**，让宿主机的某个端口"转发"到容器的端口。

### 基本语法

```bash
docker run -d -p 宿主机端口:容器端口 镜像
```

```bash
# 把宿主机的 8080 端口映射到容器的 80 端口
docker run -d --name my-nginx -p 8080:80 nginx:1.27.4
```

现在，访问 `http://localhost:8080`，请求会被转发到容器内的 80 端口——你就能看到 Nginx 的欢迎页了。

```
┌─────────────────────────────────────────┐
│  宿主机                                  │
│                                          │
│  localhost:8080 ──映射──> 容器内 80 端口  │
│                                          │
│  ┌────────────────────────────┐          │
│  │  Nginx 容器                 │          │
│  │  监听 0.0.0.0:80            │          │
│  └────────────────────────────┘          │
└─────────────────────────────────────────┘
```

### 端口映射的几种写法

```bash
# 写法 1：指定宿主机端口
docker run -d -p 8080:80 nginx:1.27.4
# 访问 localhost:8080 → 容器内 80

# 写法 2：让 Docker 随机分配一个宿主机端口
docker run -d -P nginx:1.27.4
# 大写的 -P 会随机分配端口，用 docker port 查看实际端口

# 写法 3：只指定容器端口，宿主机端口随机
docker run -d -p 80 nginx:1.27.4
# 用 docker port 容器名 查看实际映射的端口

# 写法 4：指定 IP 和端口（绑定到特定网络接口）
docker run -d -p 127.0.0.1:8080:80 nginx:1.27.4
# 只有 localhost 能访问，局域网其他机器不能访问
```

### 查看端口映射

```bash
# 查看容器的端口映射
docker port my-nginx

# 输出：
# 80/tcp -> 0.0.0.0:8080
# 80/tcp -> [::]:8080
```

---

## 六、重启策略：`--restart`

### 容器挂了怎么办？

在生产环境中，容器可能因为各种原因崩溃：内存不足、程序 bug、宿主机重启……你不希望半夜三点爬起来手动重启容器。

**`--restart`** *此术语见附录C* 让 Docker 在容器退出时**自动重启**它。

### 四种重启策略

| 策略 | 行为 | 适用场景 |
|------|------|---------|
| `no` | 不自动重启（默认值） | 临时容器、测试容器 |
| `always` | 无论什么原因退出，都自动重启 | 必须有 7×24 小时运行的生产服务 |
| `on-failure[:次数]` | 只在非正常退出（退出码 ≠ 0）时重启 | 希望程序崩溃时自动恢复，但手动停止就停 |
| `unless-stopped` | 除非手动 `docker stop`，否则一直重启 | 和 always 类似，但手动停止后不会自动重启 |

### 每种策略的详细说明

**`no`（默认）**

```bash
docker run -d --name test-nginx --restart no nginx:1.27.4
# 容器退出后，Docker 不会重启它
# 和没写 --restart 一样
```

**`always`**

```bash
docker run -d --name prod-nginx --restart always nginx:1.27.4
```

- 容器退出后，Docker 立刻重启它。
- **即使你用 `docker stop` 手动停止，重启 Docker 守护进程后它也会自动启动。**
- 适合：数据库、Web 服务器等需要一直运行的服务。

> 注意：`always` 意味着即使你手动 `docker stop`，下次 Docker 守护进程重启时，这个容器也会自动启动。如果你真的想永久停止这个容器，需要先 `docker update --restart no prod-nginx`，再 `docker stop`。

**`on-failure[:次数]`**

```bash
# 崩溃时自动重启，最多重启 5 次
docker run -d --name app-server --restart on-failure:5 nginx:1.27.4

# 不限制次数
docker run -d --name app-server --restart on-failure nginx:1.27.4
```

- 只在容器**非正常退出**（退出码 ≠ 0）时重启。
- 如果你手动 `docker stop`（退出码 0），不会重启。
- 适合：程序可能偶尔崩溃，但手动停止就应该停。

**`unless-stopped`**

```bash
docker run -d --name my-app --restart unless-stopped nginx:1.27.4
```

- 和 `always` 几乎一样，但有一个关键区别：**如果你手动 `docker stop`，容器不会自动重启，即使 Docker 守护进程重启后也不会。**
- 适合：和 `always` 一样需要高可用，但你能手动停止而不用担心它"诈尸"。

### 四种策略行为对比

| 场景 | `no` | `always` | `on-failure` | `unless-stopped` |
|------|------|---------|-------------|-----------------|
| 容器内程序崩溃（退出码 ≠ 0） | 不重启 | 重启 | 重启 | 重启 |
| 容器正常退出（退出码 = 0） | 不重启 | 重启 | 不重启 | 重启 |
| 手动 `docker stop` | 不重启 | 重启 | 不重启 | 不重启 |
| 宿主机重启后 | 不重启 | 重启 | 不重启 | 重启 |

> 生产环境推荐 `unless-stopped`。理由：高可用 + 你能控制何时真正停止。

### 修改运行中容器的重启策略

```bash
# 不用重建容器，直接修改
docker update --restart always my-nginx
```

---

## 七、实战：启动一个完整的 Nginx 服务

把本章学到的选项组合起来，启动一个完整的 Nginx 服务：

```bash
# 拉取镜像（指定精确版本）
docker pull nginx:1.27.4

# 启动容器
docker run -d \
  --name my-nginx \
  -p 8080:80 \
  --restart unless-stopped \
  nginx:1.27.4
```

逐行解释：

```
-d                       → 后台运行，不占用终端
--name my-nginx          → 命名为 my-nginx，方便后续操作
-p 8080:80               → 宿主机 8080 端口映射到容器 80 端口
--restart unless-stopped → 崩溃自动重启，手动停止不重启
nginx:1.27.4             → 使用精确版本，不是 latest
```

---

## 我做得对不对？

### 验证方法

请按顺序执行以下操作，**全部成功**才算通过：

```bash
# 1. 启动 Nginx 容器
docker run -d --name my-nginx -p 8080:80 --restart unless-stopped nginx:1.27.4

# 2. 确认容器正在运行
docker ps
# 应该看到 my-nginx，STATUS 是 Up

# 3. 浏览器访问 http://localhost:8080
# 应该看到 Nginx 的欢迎页："Welcome to nginx!"

# 4. 查看容器日志，确认 Nginx 正常启动
docker logs my-nginx

# 5. 查看端口映射
docker port my-nginx
# 输出：80/tcp -> 0.0.0.0:8080

# 6. 停止并删除容器
docker stop my-nginx
docker rm my-nginx
```

**预期结果**：
- 步骤 2：`docker ps` 列表中有 `my-nginx`，STATUS 显示 `Up X seconds`
- 步骤 3：浏览器显示 "Welcome to nginx!" 页面
- 步骤 4：日志中看到 `nginx: configuration file ... test is successful`
- 步骤 5：确认端口映射正确

---

## 不对怎么办？

### 常见错误 1：忘记 `-d`，前台卡住

❌ 错误做法：

```bash
docker run --name my-nginx -p 8080:80 nginx:1.27.4
# 终端被占用，日志疯狂滚动，不知所措
```

✅ 正确做法：

```bash
docker run -d --name my-nginx -p 8080:80 nginx:1.27.4
# 终端立刻返回，只输出容器 ID
```

### 常见错误 2：端口被占用

```bash
docker run -d --name my-nginx -p 8080:80 nginx:1.27.4
# Error: port is already allocated
```

**原因**：宿主机的 8080 端口已经被其他程序占用（可能是另一个容器，也可能是宿主机的程序）。

**排查**：

```bash
# 查看什么程序占用了 8080 端口
# Windows（PowerShell）：
netstat -ano | findstr :8080

# macOS / Linux：
lsof -i :8080

# 查看 Docker 中哪些容器用了 8080
docker ps --filter "publish=8080"
```

**解决**：

```bash
# 方案 1：换个端口
docker run -d --name my-nginx -p 8081:80 nginx:1.27.4

# 方案 2：停掉占用端口的容器
docker stop 占用8080的容器名
docker run -d --name my-nginx -p 8080:80 nginx:1.27.4
```

### 常见错误 3：容器名重复

```bash
docker run -d --name my-nginx nginx:1.27.4
# Error: Conflict. The container name "/my-nginx" is already in use
```

**原因**：之前已经有一个叫 `my-nginx` 的容器（包括已停止的）。

**解决**：

```bash
# 查看是否已有同名容器
docker ps -a --filter "name=my-nginx"

# 删除旧容器，或换一个名字
docker rm my-nginx
docker run -d --name my-nginx nginx:1.27.4
```

### 常见错误 4：`--restart always` 导致容器"阴魂不散"

```bash
docker run -d --name my-nginx --restart always nginx:1.27.4
docker stop my-nginx
# 容器停了
sudo systemctl restart docker   # 重启 Docker 服务
docker ps
# my-nginx 又活过来了！
```

**原因**：`--restart always` 的语义是"无论如何都要保持运行"，包括 Docker 守护进程重启后。

**解决**：如果你真的想永久停止：

```bash
docker update --restart no my-nginx
docker stop my-nginx
```

或者用 `unless-stopped` 替代 `always`。

### 常见错误 5：`-p` 写反了

❌ 错误做法：

```bash
docker run -d -p 80:8080 nginx:1.27.4
# 想访问 localhost:8080，但映射的是 80:8080
# 容器内 Nginx 监听的是 80，不是 8080，所以连不上
```

✅ 正确做法：

```bash
docker run -d -p 8080:80 nginx:1.27.4
# 格式：-p 宿主机端口:容器端口
# 宿主机 8080 → 容器内 80
```

---

## 本章小结

| 本章学了什么 | 对应命令/概念 | 注意事项 |
|-------------|-------------|---------|
| `docker run` 完整语法 | `docker run [OPTIONS] IMAGE[:TAG] [COMMAND]` | 选项顺序无强制要求，但推荐按"运行模式 → 标识 → 网络 → 资源"排列 |
| 后台运行 | `-d`（`--detach`） | 生产环境必备选项；忘记 `-d` 终端会卡住 |
| 容器命名 | `--name my-nginx` | 不指定则随机生成名字；名字不能重复（包括已停止的容器） |
| 端口映射 | `-p 宿主机端口:容器端口` | 格式容易写反，宿主机在前、容器在后；端口被占用时报错 |
| 退出自动删除 | `--rm` | 适合临时测试容器；长期运行的服务不要用 |
| 重启策略 | `--restart no/always/on-failure/unless-stopped` | 生产环境推荐 `unless-stopped`；`always` 会导致手动停止后"诈尸" |
| 随机端口 | `-P`（大写） | 自动映射容器暴露的端口到宿主机随机端口 |
| 修改运行中容器的重启策略 | `docker update --restart` | 不需要重建容器 |

---

## 本篇最可能出错的地方及原因

### 1. 忘记 `-d`（最常见）

**原因**：新手习惯了 `docker run -it ubuntu bash` 这种交互模式，启动服务时忘了加 `-d`。终端被卡住后不知所措，按 Ctrl+C 直接把容器停了。

**排查**：终端是否被占用，是否在疯狂输出日志。

**解决**：服务类容器永远加 `-d`。如果已经卡住了，按 `Ctrl+C` 停止，然后重新加 `-d` 启动。

### 2. 端口映射写反了

**原因**：`-p 宿主机:容器` 这个顺序不直观，新手容易把容器端口写前面。

**记忆口诀**：`-p 外面:里面`。"外面"是宿主机，"里面"是容器。你从外面访问，所以外面在前。

### 3. `--restart always` 和 `unless-stopped` 搞混

**原因**：两者行为非常相似，只在"手动停止"这个场景有区别。`always` 会在 Docker 守护进程重启后复活手动停止的容器，`unless-stopped` 不会。

**生产环境建议**：用 `unless-stopped`。你能控制何时真正停止，同时保留崩溃自动重启的能力。