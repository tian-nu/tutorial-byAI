# 13 — WORKDIR、ENV、EXPOSE

> - 对应文档版本：Docker精通教程 outline v1
> - 适用环境：任何已安装 Docker 的系统
> - 读者角色：已掌握 COPY/RUN 基础，需要配置容器运行环境的开发者
> - 预计耗时：新手 25 分钟 / 熟手 12 分钟
> - 前置教程：第 12 章（COPY 和 ADD）
> - 可视化：无

---

## 我在做什么？

你的 Dockerfile 现在能装软件（`RUN`）、能复制文件（`COPY`）。但你还需要告诉 Docker 三件事：

1. **"以后的操作在哪个目录下执行？"** → `WORKDIR`
2. **"运行时需要什么环境变量？"** → `ENV`
3. **"容器会监听哪个端口？"** → `EXPOSE`

这三条指令看似简单，但每一条背后都有"不这么写就会踩坑"的故事。比如：为什么不能用 `RUN cd /app` 代替 `WORKDIR /app`？`EXPOSE` 到底有没有实际作用？环境变量在构建时和运行时有什么不同？

学完这一章，你能：
- 正确使用 `WORKDIR` 设置工作目录
- 理解为什么 `RUN cd` 不管用
- 用 `ENV` 设置构建时可用的环境变量
- 搞清 `EXPOSE` 和 `-p` 各自做什么

---

## 一、WORKDIR：定个"老地方"

### 基本语法

```dockerfile
WORKDIR /app
```

`WORKDIR` 做了两件事：
1. 如果 `/app` 目录不存在，**创建**它。
2. 把当前的工作目录切换到 `/app`。**后续的所有指令**（`RUN`、`COPY`、`CMD`、`ENTRYPOINT`）都在这个目录下执行。

### 实战对比：有 WORKDIR vs 没有 WORKDIR

```dockerfile
# ❌ 没有 WORKDIR
FROM alpine:latest
RUN mkdir -p /app
COPY . /app
RUN cd /app && ls -la
CMD ["ls", "-la"]
# CMD 在 / 下执行 ls（因为最后一次 cd /app 在另一个 shell 里已经失效了）
```

```dockerfile
# ✅ 有 WORKDIR
FROM alpine:latest
WORKDIR /app
COPY . .
RUN ls -la
CMD ["ls", "-la"]
# 所有指令都在 /app 下执行
```

### 为什么不能用 `RUN cd /app` 代替？

这是新手最容易踩的认知坑。想象你在终端里：

```bash
cd /tmp           # 你进入了 /tmp
pwd               # 显示 /tmp

# 现在你执行：
bash -c "cd /home && pwd"   # 在一个新的 shell 里 cd /home，pwd 显示 /home
pwd                          # 你又回到原来的 shell，pwd 显示 /tmp
```

每条 `RUN` 指令在 Docker 里都是**在一个全新的 shell 里执行**，执行完毕后 shell 退出。你在那条 `RUN` 里 `cd /app` 了，但下一条 `RUN` 启动了一个全新的 shell——`cd` 的效果丢失了。

```
RUN cd /app && npm install
          │
          ▼
  ┌─────────────────────────────────┐
  │ 临时容器里的临时 shell            │
  │ $ cd /app            ← 进入 /app │
  │ $ npm install        ← 在 /app 执行│
  │ $ exit               ← shell 退出 │
  └─────────────────────────────────┘
          │
          ▼ shell 退出了，/app 的"当前目录"状态随之消失
          
下一条 RUN：
  ┌─────────────────────────────────┐
  │ 又是一个全新的 shell              │
  │ $ pwd                  ← 在 / 下 │
  │ cd 去哪了？ 丢了。               │
  └─────────────────────────────────┘
```

而 `WORKDIR` 不同——它改变了镜像的**元数据**，告诉 Docker："这个镜像的工作目录是 `/app`。"后续每个 `RUN` 启动的 shell 都会自动进入这个目录。

```dockerfile
WORKDIR /app       # 这条指令影响了镜像的元数据
RUN npm install    # 自动在 /app 下执行
RUN ls -la         # 自动在 /app 下执行
CMD ["node", "server.js"]  # 自动在 /app 下执行
```

> **想多一点**：`RUN cd` 是一个"运行时"操作（只在那个临时 shell 里有效），`WORKDIR` 是一个"声明式"配置（写入镜像元数据，持久生效）。这是 Dockerfile 设计哲学的一部分：能用声明式指令解决的，不要用命令式技巧绕过。声明式意味着"意图明确、行为稳定、可预测"。

### 多次使用 WORKDIR

```dockerfile
WORKDIR /app
WORKDIR src
# 最终工作目录 = /app/src

# 等价于：
WORKDIR /app/src
```

每次用相对路径，就会叠加到上一个 WORKDIR 后面。这和 `cd app && cd src` 的效果一样。

### 最佳实践：永远用绝对路径的 WORKDIR

```dockerfile
# ✅ 推荐
WORKDIR /app

# ⚠️ 可用但要小心——路径取决于上一条 WORKDIR
WORKDIR src
```

---

## 二、ENV：设置环境变量

### 基本语法

```dockerfile
ENV NODE_ENV=production
ENV APP_HOME=/app
```

`ENV` 设置的环境变量在**两个阶段**都生效：
1. **构建时**：后续的 `RUN`、`COPY` 等指令可以读取这个变量。
2. **运行时**：容器启动后，容器内的进程可以读取这个变量。

### 构建时使用环境变量

```dockerfile
FROM node:20-alpine

ENV NODE_ENV=production

# RUN 可以读取 ENV 设的变量
RUN echo "当前环境：${NODE_ENV}" && \
    if [ "$NODE_ENV" = "production" ]; then \
        echo "生产模式，跳过 devDependencies"; \
    fi

# npm 会根据 NODE_ENV 决定是否安装 devDependencies
COPY package*.json ./
RUN npm ci --only=production
```

### 运行时使用（也能被 `-e` 覆盖）

```bash
# 使用 Dockerfile 里的默认值
docker run my-node-app
# NODE_ENV=production（Dockerfile 里设的）

# 运行时覆盖
docker run -e NODE_ENV=development my-node-app
# NODE_ENV=development（被 docker run -e 覆盖了）
```

### ENV 可以一次设多个

```dockerfile
ENV APP_HOME=/app \
    NODE_ENV=production \
    PORT=3000
```

### 环境变量的"坑"：构建时 vs 运行时

```dockerfile
FROM alpine:latest

# 构建时：$NAME 是 "builder"
ENV NAME=builder
RUN echo "构建时的 NAME 是：${NAME}"   # 输出 builder

# 覆盖
ENV NAME=runner
```

```bash
# 运行容器
docker run myapp
# NAME=runner

# docker run -e 可以在运行时再次覆盖
docker run -e NAME=custom myapp
# NAME=custom
```

**优先级**：`docker run -e` > Dockerfile 的最后一个 `ENV` > 之前的 `ENV`

> **想多一点**：`ENV` 最容易被低估的价值不是"设个变量"，而是"让镜像的行为可以通过环境变量配置"。比如你的应用代码可以通过 `process.env.DATABASE_URL` 读数据库连接串。你把默认值写在 Dockerfile 里，但允许 `docker run -e DATABASE_URL=xxx` 覆盖。这样同一个镜像，在开发环境连开发库，在生产环境连生产库——**镜像本身不需要重新构建**。

### `ENV` vs `ARG`：一个容易混淆的对比

| 维度 | `ENV` | `ARG` |
|------|-------|-------|
| 生效范围 | **构建时 + 运行时** | **仅构建时** |
| 运行时能读到吗？ | 能 | **不能** |
| `docker run -e` 能覆盖吗？ | 能 | 不能（运行时 ARG 不存在） |
| 典型用途 | 运行时环境配置（NODE_ENV、数据库 URL） | 构建参数（版本号、构建时间） |

```dockerfile
# ENV：运行时也需要
ENV NODE_ENV=production

# ARG：只在构建时用
ARG VERSION=1.0.0
RUN echo "构建版本：${VERSION}"
# 容器启动后，$VERSION 不存在
```

---

## 三、EXPOSE：声明端口（但这只是一个"便签"）

### 基本语法

```dockerfile
EXPOSE 80
EXPOSE 443
EXPOSE 3000/tcp
```

### EXPOSE 到底做什么？

很多新手以为 `EXPOSE` 会自动把端口映射出来。**不会。**

`EXPOSE` 的作用**仅仅是文档**：它告诉读 Dockerfile 的人（和某些 Docker 工具）："这个镜像里的应用会监听 80 端口。"

```
EXPOSE 80  →  "嘿，我里面有个东西在监听 80 端口"
              （信息性的，不产生实际网络效果）

docker run -p 8080:80 →  实际把宿主机的 8080 映射到容器的 80
                          （这才是真正的端口映射）
```

### 一张表说明白

```dockerfile
# Dockerfile
EXPOSE 80
```

```bash
# 场景 1：不加 -p
docker run my-web-app
# 容器里 nginx 在 80 端口跑着，但宿主机访问不到
# curl http://localhost:80  → 连接被拒绝

# 场景 2：加了 -p
docker run -p 8080:80 my-web-app
# curl http://localhost:8080  → 成功！
# -p 8080:80 的意思是：把宿主机的 8080 映射到容器的 80
```

### 那 EXPOSE 有什么用？

1. **给人看**：读 Dockerfile 的人一眼就知道这个容器用什么端口。
2. **给 `-P` 用**：`docker run -P`（大写 P）会自动把 EXPOSE 声明的端口映射到宿主机的一个随机端口。

```bash
docker run -d -P my-web-app
# Docker 自动把容器 80 映射到宿主机的某个随机端口（比如 32768）

docker ps
# PORTS 列会显示：0.0.0.0:32768->80/tcp
```

> `-p`（小写）= 手动指定映射；`-P`（大写）= 自动映射所有 EXPOSE 端口到随机宿主机端口。

### 实战示例

```dockerfile
FROM nginx:alpine

# 声明：这个容器会监听 80 端口（HTTP）和 443 端口（HTTPS）
EXPOSE 80
EXPOSE 443

COPY html/ /usr/share/nginx/html/
```

```bash
# 手动映射
docker run -d -p 8080:80 my-web

# 自动映射（让 Docker 选端口）
docker run -d -P --name auto-web my-web
docker port auto-web
# 输出：
# 80/tcp -> 0.0.0.0:32768
# 443/tcp -> 0.0.0.0:32769
```

---

## 四、实战：构建一个带环境变量和明确工作目录的应用镜像

我们要做一个微型的 Node.js 应用，展示 `WORKDIR`、`ENV`、`EXPOSE` 的配合使用。

### 项目结构

```
my-node-app/
├── Dockerfile
├── .dockerignore
├── package.json
└── server.js
```

### 步骤 1：创建应用文件

**package.json**：

```json
{
  "name": "docker-env-demo",
  "version": "1.0.0",
  "main": "server.js"
}
```

**server.js**：

```javascript
const http = require('http');

const PORT = process.env.PORT || 3000;
const APP_NAME = process.env.APP_NAME || 'Unknown App';
const NODE_ENV = process.env.NODE_ENV || 'development';

const server = http.createServer((req, res) => {
  res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' });
  res.end(`
    <h1>${APP_NAME}</h1>
    <p>环境：${NODE_ENV}</p>
    <p>端口：${PORT}</p>
    <p>时间：${new Date().toISOString()}</p>
  `);
});

server.listen(PORT, () => {
  console.log(`${APP_NAME} 运行在端口 ${PORT}，环境：${NODE_ENV}`);
});
```

**.dockerignore**：

```
node_modules
.git
.env
*.md
```

### 步骤 2：写 Dockerfile

```dockerfile
FROM node:20-alpine

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV NODE_ENV=production \
    APP_NAME=MyDockerApp \
    PORT=3000

# 复制依赖清单并安装
COPY package*.json ./
RUN npm ci --only=production && npm cache clean --force

# 复制应用代码
COPY server.js ./

# 声明端口（文档作用）
EXPOSE 3000

# 启动命令
CMD ["node", "server.js"]
```

注意指令的顺序：

```
FROM → WORKDIR → ENV → COPY package*.json → RUN npm ci → COPY server.js → EXPOSE → CMD
        │                  │                           │
        │                  └── 这一步利用缓存：        └── 代码经常变，放最后
        │                      package.json 不怎么变
        └── WORKDIR 放在 COPY 之前，
            后面的 COPY 和 CMD 都在 /app 下
```

> `npm cache clean --force` 清理 npm 缓存，减小镜像体积。每一条 RUN 都应该是"做了事并清理干净"。

### 步骤 3：构建和运行

```bash
# 构建
docker build -t node-env-demo:v1 .

# 用默认环境变量运行
docker run -d -p 3000:3000 --name demo1 node-env-demo:v1

# 测试
curl http://localhost:3000
# 输出包含：MyDockerApp / production / 3000

# 用自定义环境变量运行另一个实例
docker run -d -p 3001:3000 \
  -e APP_NAME=StagingApp \
  -e NODE_ENV=staging \
  --name demo2 node-env-demo:v1

# 测试第二个实例
curl http://localhost:3001
# APP_NAME 变成了 StagingApp，NODE_ENV 变成了 staging
# 但你用的是同一个镜像！
```

### 步骤 4：进入容器验证 WORKDIR

```bash
docker exec -it demo1 sh
# 进入容器后：
pwd
# 输出：/app          ← 这就是 WORKDIR 的效果

echo $NODE_ENV
# 输出：production    ← ENV 的效果

echo $APP_NAME
# 输出：MyDockerApp   ← ENV 的效果

exit
```

> 注意：`docker exec` 进入容器时，默认就在 WORKDIR 指定的目录。这就是为什么你不需要先 `cd /app`。

---

## 五、我做得对不对？

### 验证方法

```bash
# 1. 构建镜像
docker build -t node-env-demo:v1 .

# 2. 查看镜像信息
docker inspect node-env-demo:v1 | grep -A5 "WorkingDir"
# 应该看到 "WorkingDir": "/app"

docker inspect node-env-demo:v1 | grep -A5 "ExposedPorts"
# 应该看到 "3000/tcp"

# 3. 运行容器
docker run -d -p 3000:3000 --name env-test node-env-demo:v1

# 4. 验证应用有响应
curl http://localhost:3000
# 应该看到 HTML 内容

# 5. 进入容器，验证工作目录和环境变量
docker exec env-test pwd
# 输出：/app

docker exec env-test printenv NODE_ENV
# 输出：production

docker exec env-test printenv APP_NAME
# 输出：MyDockerApp

# 6. 验证运行时可以用 -e 覆盖
docker run -d -p 3001:3000 -e APP_NAME=CustomApp --name env-test2 node-env-demo:v1
curl http://localhost:3001
# 应该看到 APP_NAME 变成了 CustomApp

# 7. 清理
docker stop env-test env-test2 && docker rm env-test env-test2
```

---

## 六、不对怎么办？

### 常见错误 1：用 `RUN cd /app` 代替 `WORKDIR /app`

```dockerfile
# ❌ 错误
FROM alpine:latest
RUN mkdir -p /app
RUN cd /app
COPY server.js .    # 这会把文件复制到 / 下面，不是 /app 下面！
```

❌ 原因：如前面解释的，`RUN cd` 只在那一条 RUN 的 shell 里有效，下一条指令回到了 `/`。

✅ 正确：

```dockerfile
FROM alpine:latest
WORKDIR /app     # 环境永久切换
COPY server.js . # 文件复制到 /app/server.js
```

### 常见错误 2：WORKDIR 指定的路径在后续指令里不存在

```dockerfile
FROM alpine:latest
WORKDIR /app/subdir/deep
# WORKDIR 会自动创建 /app/subdir/deep，所以不会出错
```

这条其实不会出错——`WORKDIR` 会自动创建不存在的目录。但如果你后续操作依赖"目录里有某些文件"，而这些文件不存在，问题才暴露。排查方向：

```bash
docker run -it --rm my-image sh
# 手动探查目录结构
ls -la /app/subdir/deep
```

### 常见错误 3：以为 `EXPOSE` 能替代 `-p`

```bash
# Dockerfile 里有：EXPOSE 3000

# ❌ 你这样做：
docker run myapp
curl http://localhost:3000
# 连接被拒绝 —— 因为你没做端口映射！
```

`EXPOSE` 不创建端口映射。它只是一张便签。真正让端口通的，是 `-p` 或 `-P`。

### 常见错误 4：`ENV` 里写了敏感信息

```dockerfile
# ❌ 危险！
ENV DATABASE_PASSWORD=MySecretPass123
```

环境变量可以随时被 `docker inspect` 看到：

```bash
docker inspect myapp
# 输出里明晃晃地显示 ENV DATABASE_PASSWORD=MySecretPass123
```

敏感配置不要在 Dockerfile 里用 `ENV` 写死。正确做法：

```bash
# 运行时传入，不进镜像
docker run -e DATABASE_PASSWORD=your_password myapp
```

### 常见错误 5：`WORKDIR` 不管用，因为用 `RUN cd` 习惯了

这是认知惯性。你终端里切换目录都是 `cd`，所以写 Dockerfile 时也顺手写了 `RUN cd`。改掉这个习惯——在 Dockerfile 里，**目录切换 = `WORKDIR`**。

---

## 本章小结

| 本章学了什么 | 对应命令/概念 | 注意事项 |
|-------------|-------------|---------|
| WORKDIR | `WORKDIR /app` | 自动创建目录；影响后续所有指令；别用 `RUN cd` 替代 |
| `RUN cd` 为什么不管用 | 每条 RUN 是独立 shell，cd 效果不传递 | 很常见的认知坑，记住 shell 退出状态丢失 |
| ENV | `ENV NODE_ENV=production` | 构建时 + 运行时都生效；`docker run -e` 可覆盖 |
| ENV vs ARG | ENV 在运行时保留；ARG 只在构建时可用 | 需要运行时读取的用 ENV；只构建时需要的用 ARG |
| ENV 安全性 | 敏感信息不要写进 ENV | `docker inspect` 能看到所有 ENV 值 |
| EXPOSE | `EXPOSE 3000` | **不创建端口映射**；纯文档作用；配合 `-P` 自动映射 |
| `-p` vs `-P` | `-p 8080:80` 手动指定；`-P` 自动映射 EXPOSE 端口 | `-P` 映射到随机端口，`docker port` 查看 |
| 指令顺序 | WORKDIR、ENV 在最前面 | 设置环境的指令放前面，代码 COPY 放后面（利用缓存） |

---

## 本篇最可能出错的地方及原因

### 1. `RUN cd /app` 以为能持久切换目录（最高频的认知坑）

**原因**：终端使用者习惯了 `cd`，不知道 `RUN` 是在独立 shell 里执行的。

**排查**：你发现 `COPY . .` 没有复制到 `/app`，而是复制到了 `/`。`docker run -it --rm myimage sh`，进去 `ls`，文件在根目录。

**解决**：永远用 `WORKDIR /app`，永远不要用 `RUN cd`。

### 2. 以为 `EXPOSE` 会自动暴露端口

**原因**：`EXPOSE` 这名字确实误导人——"暴露端口"，听起来像"我已经把端口映射好了"。

**真相**：`EXPOSE` = 贴便签。"容器里有个东西在监听 3000 端口哦"——这句话对 Docker 的网络栈没有任何影响。

**验证**：不传 `-p` 或 `-P`，从宿主机上 `curl http://localhost:暴露的端口`，你会发现连接被拒绝。

### 3. 敏感信息写在 `ENV` 里

**原因**：`ENV` 看起来方便——"构建时能用，运行时也能用，一举两得。"

**后果**：`docker inspect` 可以把镜像的所有 ENV 值明文打印出来。推送镜像到仓库 ≈ 把密钥公开。

**检查**：`docker inspect 你的镜像名 | grep -i password`——如果有输出，你中招了。

### 4. 把 `--only=production` 写成了 `--production`（npm ci 相关）

```dockerfile
# ❌ 错误
RUN npm ci --production

# ✅ 正确
RUN npm ci --only=production
```

`--production` 是旧版 npm 的选项，新版用 `--only=production` 或 `--omit=dev`。写错了构建不会报错，但 devDependencies 没被省略，镜像体积凭空大了几十 MB。