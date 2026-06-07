# 29 — 项目一：Node.js 应用容器化

> - 对应文档版本：Docker精通教程 outline v1
> - 适用环境：任何已安装 Docker 的系统
> - 读者角色：已掌握 Dockerfile 与 `docker run`，准备实战的开发者
> - 预计耗时：新手 40 分钟 / 熟手 20 分钟
> - 前置教程：第 10 章（Dockerfile）、第 14 章（CMD / ENTRYPOINT）
> - 可视化：无

---

## 我在做什么？

前面十几章你学了 Docker 的各种命令和概念。现在，是时候把知识用在**一个真实的项目**上了。

我们拿一个 Express.js（Node.js 最流行的 Web 框架）写的小应用，从头到尾走一遍容器化流程：看代码、写 Dockerfile、构建镜像、运行容器、在浏览器里看到它真的在跑。你还会学到**开发模式**——在容器里改代码立刻生效，不用每次重新构建。

这个流程是普适的。你今天学会容器化一个 Express 应用，明天就能容器化 Koa、Fastify、Nest.js 等任何 Node.js 应用——套路完全一样。

学完这一章，你能：
- 看懂一个 Node.js 项目的 `package.json`，知道该装什么依赖
- 写出一个**可用的** Node.js Dockerfile，包括多层构建优化
- 用 `docker build -t` 构建镜像，`docker run` 启动容器
- 用 bind mount 实现开发模式热重载
- 用 `curl` 验证接口是否正常

---

## 一、项目代码：一个极简 Express 应用

### 项目结构

```
node-app/
├── package.json
├── src/
│   └── index.js
├── Dockerfile
└── .dockerignore
```

### package.json

```json
{
  "name": "node-docker-demo",
  "version": "1.0.0",
  "description": "A demo Express app for Docker tutorial",
  "main": "src/index.js",
  "scripts": {
    "start": "node src/index.js",
    "dev": "nodemon src/index.js"
  },
  "dependencies": {
    "express": "^4.18.2"
  },
  "devDependencies": {
    "nodemon": "^3.0.1"
  }
}
```

注意 `package.json` 里的关键信息：
- `"main": "src/index.js"` — 入口文件在哪
- `"start": "node src/index.js"` — 怎么启动
- `"dependencies"` — 生产环境需要 `express`
- `"devDependencies"` — 开发环境需要 `nodemon`（文件变化自动重启的工具）

### src/index.js

```javascript
const express = require('express');
const app = express();
const PORT = process.env.PORT || 3000;

// 根路径
app.get('/', (req, res) => {
  res.json({ message: 'Hello from Docker!', env: process.env.NODE_ENV || 'development' });
});

// 健康检查端点
app.get('/health', (req, res) => {
  res.json({ status: 'OK', uptime: process.uptime() });
});

app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
```

这个应用有三件事：
1. `GET /` — 返回一段 JSON，附带当前环境变量
2. `GET /health` — 返回 `{"status":"OK"}`，供外部检测服务是否存活
3. 端口从环境变量 `PORT` 读取，默认 3000。这个设计非常"容器友好"——我们后面会通过 `docker run -e` 或 `environment` 来覆盖它

---

## 二、.dockerignore：别把垃圾打包进去

在写 Dockerfile 之前，先建 `.dockerignore`。它的作用和 `.gitignore` 一毛一样——告诉 Docker"这些东西别打包进构建上下文"。

```
node_modules
npm-debug.log
.git
.gitignore
.env
.DS_Store
```

为什么要把 `node_modules` 写进去？

因为在你的宿主机上，`node_modules` 是根据你的操作系统和 Node 版本编译的。比如你在 Windows 上 `npm install`，装出来的 native 模块（如 `bcrypt`）是 Windows 的二进制。但容器里跑的是 Linux（Alpine），这些二进制根本不能执行。

**一句话**：`node_modules` 必须在容器里重新装，打包宿主机的 `node_modules` 进去除了让镜像变大、让构建变慢、还可能引入不可执行的二进制——百害无一利。

---

## 三、Dockerfile：多层构建优化

### 第一版：能跑的 Dockerfile

先从最简单的开始——能跑就行：

```dockerfile
FROM node:18-alpine

WORKDIR /app

COPY package.json .

RUN npm install --production

COPY src/ ./src/

EXPOSE 3000

CMD ["node", "src/index.js"]
```

这个 Dockerfile 做了什么？

```
FROM node:18-alpine
    ↓ Alpine 版 Node.js，整个基础镜像只有 ~120MB，比 node:18（~950MB）小很多
WORKDIR /app
    ↓ 创建 /app 目录并进去，后面所有命令都在 /app 下执行
COPY package.json .
    ↓ 先把 package.json 拷进来
RUN npm install --production
    ↓ 只装生产依赖（dependencies），跳过 devDependencies
COPY src/ ./src/
    ↓ 再把源代码拷进来
EXPOSE 3000
    ↓ 声明"我监听 3000 端口"（文档作用，不实际开端口）
CMD ["node", "src/index.js"]
    ↓ 容器启动时执行：node src/index.js
```

### ❌ 第一版的问题

问题不在"不能跑"，而在"每次改一行代码都要重装依赖"。

为什么？Docker 的层缓存*此术语见附录C*机制：每条指令生成一个层，如果某层没变，Docker 就用缓存跳过它；但如果某层变了，它**和它之后的所有层**都要重新执行。

```dockerfile
COPY package.json .       # ← 层 3：package.json 没变 → 用缓存
RUN npm install --production  # ← 层 4：用缓存 ✅
COPY src/ ./src/          # ← 层 5：src/ 里有文件改了 → 缓存失效
                           # 层 5 之后的所有层…
```

第一版的 `COPY src/` 在 `RUN npm install` **之后**，所以改代码不会触发重新装依赖——这是对的。

但等一下——如果 `package.json` 里加了新依赖呢？那 `COPY package.json .` 会变，`RUN npm install` 重新跑——这也是对的。

实际上第一版的层顺序已经是"正确"的了。我们接下来只是让它更好。

### 第二版：加上 devDependencies 的支持和多层构建

```dockerfile
# ===== 阶段 1：构建阶段 =====
FROM node:18-alpine AS builder

WORKDIR /app

COPY package.json .

# 装全部依赖（包括 devDependencies）
RUN npm install

COPY src/ ./src/

# ===== 阶段 2：运行阶段 =====
FROM node:18-alpine AS runner

WORKDIR /app

# 从构建阶段拷贝 node_modules（已包含生产依赖）
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json .
COPY --from=builder /app/src ./src

EXPOSE 3000

ENV NODE_ENV=production

CMD ["node", "src/index.js"]
```

这个版本用了**多阶段构建（multi-stage build）** *此术语见附录C*：

```
阶段1 (builder)                    阶段2 (runner)
┌─────────────────┐                ┌─────────────────┐
│ npm install     │                │                 │
│ （含 dev 依赖）  │ ──拷贝──→     │ 只拿最终需要的  │
│ 编译/测试代码   │                │ node_modules    │
└─────────────────┘                │ package.json    │
       最终丢弃 ↑                  │ src/            │
                                   └─────────────────┘
                                       最终镜像 ↑
```

**这个 Dockerfile 的实际好处**：
1. Builder 阶段装了全部依赖（包括 devDependencies），如果你有 TypeScript 需要编译，可以在 builder 里 `RUN npm run build`
2. Runner 阶段只从 builder 拿最终需要的文件，不包含 npm 缓存、devDependencies
3. 最终镜像更小

### ❌ 常见错误：COPY 顺序错了 — 先拷 src 再拷 package.json

```dockerfile
# ❌ 错误顺序
FROM node:18-alpine
WORKDIR /app
COPY . .                    # 把所有东西拷进来
RUN npm install --production
CMD ["node", "src/index.js"]
```

**为什么这是错的？**

因为 `COPY . .` 之后，**任何文件改动**都会让缓存失效。你改一行注释，`COPY . .` 变了 → `RUN npm install` 重跑 → 每次构建都等几十秒装依赖。

```dockerfile
# ✅ 正确顺序
FROM node:18-alpine
WORKDIR /app
COPY package.json .
RUN npm install --production   # ← 这层只在 package.json 变化时重跑
COPY src/ ./src/               # ← 改代码只让这层重跑
CMD ["node", "src/index.js"]
```

**核心原则**：把变化频率最低的文件放最前面（`package.json`），变化最频繁的文件放最后面（源代码）。这样缓存命中率最高。

---

## 四、构建与运行

### 构建镜像

在 `node-app/` 目录下：

```bash
docker build -t my-node-app .
```

预期输出（第二版多阶段构建）：

```
[+] Building 15.2s (12/12) FINISHED
 => [builder 1/4] FROM docker.io/library/node:18-alpine
 => [builder 2/4] WORKDIR /app
 => [builder 3/4] COPY package.json .
 => [builder 4/4] RUN npm install
 => [runner 1/4] FROM docker.io/library/node:18-alpine
 => [runner 2/4] WORKDIR /app
 => [runner 3/4] COPY --from=builder /app/node_modules ./node_modules
 => [runner 4/4] COPY --from=builder /app/package.json .
 => [runner 5/5] COPY --from=builder /app/src ./src
 => exporting to image
 => => naming to docker.io/library/my-node-app
```

验证镜像存在：

```bash
docker images my-node-app
# REPOSITORY    TAG       IMAGE ID       CREATED          SIZE
# my-node-app   latest    a1b2c3d4e5f6   10 seconds ago   180MB
```

### 运行容器

```bash
docker run -d -p 3000:3000 --name node-demo my-node-app
```

分解这条命令：

```
docker run -d            ← 后台运行 (detach)
  -p 3000:3000           ← 把宿主机 3000 端口映射到容器 3000 端口
  --name node-demo       ← 给容器起个名字，方便管理
  my-node-app            ← 用我们刚构建的镜像
```

### 验证

```bash
# 1. 确认容器在跑
docker ps --filter name=node-demo
# 预期：STATUS 列显示 Up

# 2. 测试根路径
curl http://localhost:3000/
# 预期输出：{"message":"Hello from Docker!","env":"production"}

# 3. 测试健康检查
curl http://localhost:3000/health
# 预期输出：{"status":"OK","uptime":12.345}

# 4. 查看日志
docker logs node-demo
# 预期：看到 "Server running on port 3000"
```

如果上面的 4 步全部通过——恭喜，你成功容器化了一个 Node.js 应用。

---

## 五、开发模式：不用反复构建

刚才的运行方式有个致命问题：**每次改代码都要重新 build 镜像**。

开发的时候我们需要的是：改代码 → 自动重启服务 → 浏览器刷新。这就是所谓的**热重载（hot reload）**。

Docker 怎么做到？答案是 **bind mount** *此术语见附录C*——把宿主机上的源代码目录"挂"到容器里，覆盖容器里的对应目录。

### Bind mount 的工作原理

```
你的宿主机                        Docker 容器
┌──────────────────┐             ┌──────────────────┐
│ D:\project\src\  │──映射到──→  │ /app/src/        │
│   index.js  ←改它 │             │   index.js  ←立刻同步│
└──────────────────┘             └──────────────────┘
   你在 VS Code 里改一行          容器里看到的文件马上变
```

### 开发模式命令

```bash
# 先停掉之前的生产模式容器
docker stop node-demo && docker rm node-demo

# 以开发模式启动
docker run -d \
  -p 3000:3000 \
  --name node-demo-dev \
  -v "$(pwd)/src:/app/src" \
  -e NODE_ENV=development \
  my-node-app \
  npx nodemon src/index.js
```

分解：

```
-v "$(pwd)/src:/app/src"
    ↓ 把当前目录下的 src/ 映射到容器内 /app/src/
    ↓ 你在宿主机改代码 → 容器内文件同步变化
    ↓ Windows PowerShell 用户注意：用 ${PWD}/src:/app/src

-e NODE_ENV=development
    ↓ 覆盖 Dockerfile 里的 NODE_ENV=production
    ↓ Express 和一些中间件会根据这个值调整行为（如显示详细错误）

npx nodemon src/index.js
    ↓ 覆盖 Dockerfile 里的 CMD ["node", "src/index.js"]
    ↓ nodemon 会监听文件变化，自动重启 Node 进程
```

> ⚠️ **Windows 用户特别注意**：`$(pwd)` 在 PowerShell 里不能直接用。换成：
> ```powershell
> docker run -d -p 3000:3000 --name node-demo-dev -v "${PWD}/src:/app/src" -e NODE_ENV=development my-node-app npx nodemon src/index.js
> ```

### 验证热重载

```bash
# 1. 确认容器在跑
docker ps --filter name=node-demo-dev

# 2. 测试接口
curl http://localhost:3000/
# {"message":"Hello from Docker!","env":"development"}

# 3. 在宿主机上修改 src/index.js
# 把 "Hello from Docker!" 改成 "Hello from Docker! Updated!"
# 保存文件

# 4. 看容器日志确认 nodemon 检测到变化
docker logs node-demo-dev --tail 5
# 预期看到：[nodemon] restarting due to changes...

# 5. 再次测试
curl http://localhost:3000/
# {"message":"Hello from Docker! Updated!","env":"development"}
```

你在宿主机改了代码，nodemon 在容器里检测到文件变化、自动重启服务——全程没有 `docker build`、没有 `docker restart`。

这就是容器化开发的核心优势：**环境在容器里（一致），代码在宿主机上（方便编辑）**。

### 开发模式有一个坑：node_modules

如果你这样写 bind mount：

```bash
# ❌ 整项目挂载——这会把宿主机的 node_modules 覆盖掉容器里的
docker run -v "$(pwd):/app" ...
```

会把宿主机上的 `node_modules`（可能是空的，或者 Windows 版本的）覆盖到容器里，覆盖掉容器里 `npm install` 装好的 Linux 版 `node_modules`。结果就是：`express` 找不到，启动报错。

```bash
# ✅ 只挂源代码目录
docker run -v "$(pwd)/src:/app/src" ...
```

这样容器里的 `/app/node_modules` 保持原样，只有 `src/` 被 mount 覆盖。

---

## 六、我做得对不对？

### 完整验证流程

在 `node-app/` 目录下依次执行以下命令，全部通过才算成功：

```bash
# === 生产模式验证 ===

# 1. 构建镜像
docker build -t my-node-app .
# 检查：无报错，看到 "naming to docker.io/library/my-node-app"

# 2. 运行容器
docker run -d -p 3000:3000 --name node-demo my-node-app
# 检查：返回一长串容器 ID

# 3. 确认容器状态
docker ps --filter name=node-demo
# 检查：STATUS 列显示 "Up"

# 4. 测试健康检查
curl http://localhost:3000/health
# 预期：{"status":"OK","uptime":...}

# 5. 测试根路径
curl http://localhost:3000/
# 预期：{"message":"Hello from Docker!","env":"production"}

# 6. 停掉生产模式容器
docker stop node-demo && docker rm node-demo

# === 开发模式验证 ===

# 7. 启动开发模式
docker run -d -p 3000:3000 --name node-demo-dev \
  -v "${PWD}/src:/app/src" \
  -e NODE_ENV=development \
  my-node-app \
  npx nodemon src/index.js

# 8. 确认开发模式
curl http://localhost:3000/
# 预期：{"message":"Hello from Docker!","env":"development"}

# 9. 检查日志看到 nodemon 在运行
docker logs node-demo-dev --tail 3
# 预期看到：[nodemon] ...

# 10. 清理
docker stop node-demo-dev && docker rm node-demo-dev
```

---

## 七、不对怎么办？

### 常见错误 1：忘记暴露端口

```bash
docker run -d --name node-demo my-node-app
# 没有 -p 3000:3000

curl http://localhost:3000/
# curl: (7) Failed to connect to localhost port 3000
```

❌ 原因：你没有用 `-p` 把容器端口映射到宿主机。容器内部确实在监听 3000，但那只在容器内部能访问。宿主机和容器之间隔着一道"墙"——`-p` 就是在墙上开一扇门。

✅ 解决：

```bash
docker run -d -p 3000:3000 --name node-demo my-node-app
```

**记忆**：Dockerfile 里的 `EXPOSE` 只是"声明"，不会自动映射端口。实际映射必须靠 `docker run -p`。

### 常见错误 2：node_modules 没装，容器里找不到 express

```bash
docker logs node-demo
# Error: Cannot find module 'express'
```

❌ 原因 1：`COPY . .` 把宿主机空的或缺少 `node_modules` 的目录拷进容器，覆盖了容器里 `npm install` 的结果。

```dockerfile
# ❌ 错误做法
FROM node:18-alpine
WORKDIR /app
COPY . .
RUN npm install        # COPY . . 之后才装——但这个错误是宿主机的 node_modules 问题
```

实际上，`COPY . .` 之后 `RUN npm install` 会**重新在容器里装**，所以这个具体错误通常不是这个原因。更常见的原因是：

❌ 原因 2（更常见）：`.dockerignore` 没写 `node_modules`，并且构建顺序混乱。

❌ 原因 3（开发模式常见）：bind mount 了整个项目目录，把宿主机的空 `node_modules` 覆盖到了容器里。

✅ 解决：

```bash
# 检查 Dockerfile 的 COPY 顺序是否正确
# package.json 应该先于 src/ 被 COPY
# 然后 RUN npm install 在 COPY package.json 之后、COPY src 之前

# 开发模式：只挂 src/，别挂整个项目
docker run -v "$(pwd)/src:/app/src" ...   # ✅
docker run -v "$(pwd):/app" ...           # ❌
```

### 常见错误 3：nodemon 没装，开发模式启动失败

```bash
docker logs node-demo-dev
# sh: nodemon: not found
```

❌ 原因：镜像是用 `npm install --production` 构建的，跳过了 `devDependencies`，而 `nodemon` 在 `devDependencies` 里。开发模式需要 nodemon，但镜像里没有。

✅ 解决：用多阶段构建的第二版 Dockerfile，builder 阶段装全部依赖（不含 `--production`），nodemon 就在里面了。

### 常见错误 4：Windows 路径问题

```powershell
# PowerShell
docker run -v "$(pwd)/src:/app/src" ...
# 或者
docker run -v "${PWD}/src:/app/src" ...
```

如果路径里有空格：

```powershell
# ❌ 路径有空格可能出错
docker run -v "D:\My Projects\src:/app/src" ...

# ✅ 用双引号包裹整个参数
docker run -v "D:\My Projects\src:/app/src" ...
```

### 常见错误 5：端口被占用

```bash
docker run -d -p 3000:3000 --name node-demo my-node-app
# Error: port is already allocated
```

✅ 换一个宿主机端口：

```bash
docker run -d -p 3001:3000 --name node-demo my-node-app
# 宿主机 3001 → 容器 3000

curl http://localhost:3001/health
```

---

## 八、完整代码清单

### package.json

```json
{
  "name": "node-docker-demo",
  "version": "1.0.0",
  "description": "A demo Express app for Docker tutorial",
  "main": "src/index.js",
  "scripts": {
    "start": "node src/index.js",
    "dev": "nodemon src/index.js"
  },
  "dependencies": {
    "express": "^4.18.2"
  },
  "devDependencies": {
    "nodemon": "^3.0.1"
  }
}
```

### src/index.js

```javascript
const express = require('express');
const app = express();
const PORT = process.env.PORT || 3000;

app.get('/', (req, res) => {
  res.json({ message: 'Hello from Docker!', env: process.env.NODE_ENV || 'development' });
});

app.get('/health', (req, res) => {
  res.json({ status: 'OK', uptime: process.uptime() });
});

app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
```

### Dockerfile（多阶段构建版）

```dockerfile
# ===== 阶段 1：构建阶段 =====
FROM node:18-alpine AS builder

WORKDIR /app

COPY package.json .

RUN npm install

COPY src/ ./src/

# ===== 阶段 2：运行阶段 =====
FROM node:18-alpine AS runner

WORKDIR /app

COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json .
COPY --from=builder /app/src ./src

EXPOSE 3000

ENV NODE_ENV=production

CMD ["node", "src/index.js"]
```

### .dockerignore

```
node_modules
npm-debug.log
.git
.gitignore
.env
.DS_Store
```

---

## 本章小结

| 本章学了什么 | 对应命令/概念 | 注意事项 |
|-------------|-------------|---------|
| Node.js 应用容器化完整流程 | `docker build -t my-node-app .` | 先看懂 `package.json` 再写 Dockerfile |
| `.dockerignore` | 忽略 `node_modules`、`.git` 等 | `node_modules` 必须在容器里重新装，不能从宿主机打包 |
| Dockerfile 层顺序优化 | `COPY package.json` → `RUN npm install` → `COPY src` | 变化频率低的文件放前面，提高缓存命中率 |
| 多阶段构建 | `FROM ... AS builder` / `COPY --from=builder` | builder 装全部依赖，runner 只拿结果 |
| 生产模式运行 | `docker run -d -p 3000:3000` | `-p` 不能忘，`EXPOSE` 只是文档 |
| 开发模式热重载 | `-v "$(pwd)/src:/app/src"` + `nodemon` | 只挂 `src/`，别挂整个项目（会覆盖 `node_modules`） |
| 验证 | `curl localhost:3000/health` 返回 `{"status":"OK"}` | 健康检查端点是容器化应用的标准实践 |
| `EXPOSE` vs `-p` | `EXPOSE` 声明 + `-p` 实际映射 | `EXPOSE` 不会自动映射端口 |

---

## 本篇最可能出错的地方及原因

### 1. `COPY . .` 导致每次都重新 `npm install`（最高频）

**这是 Node.js 容器化最经典的错误。** 开发者想省事，一行 `COPY . .` 把整个项目拷进去。结果就是：每次改一行代码，`COPY . .` 缓存失效 → `RUN npm install` 重跑 → 构建时间从 2 秒变成 30 秒。

**根因**：Docker 的层缓存机制只看文件内容哈希，不看文件名。`COPY . .` 意味着"项目中任何文件变化都触发这一层重建"。而 `COPY package.json .` 后面单独 `RUN npm install`，只有 `package.json` 变化时才重新装依赖。

**记忆口诀**：package.json 是"老板"（不常变），src/ 是"员工"（天天变）。先处理老板，再处理员工。

### 2. bind mount 整项目覆盖了容器里的 `node_modules`

开发模式时用 `-v $(pwd):/app` 把整个项目目录挂进去。如果宿主机上没有 `node_modules`（你没在宿主机上 `npm install`），容器里的 `/app/node_modules` 就没了。结果：`Cannot find module 'express'`。

**解决**：只挂 `src/` 目录。容器里的 `node_modules` 保持原样。

### 3. `nodemon` 找不到 — `npm install --production` 的副作用

如果你用的是第一版 Dockerfile（`RUN npm install --production`），镜像里没有 `nodemon`（因为它在 `devDependencies` 里）。开发模式需要修改 Dockerfile 或用多阶段构建。

**解决**：builder 阶段用 `npm install`（不带 `--production`），nodemon 就有了。

### 4. PowerShell 里 `$(pwd)` 不识别

Windows PowerShell 里 `$(pwd)` 是 Linux shell 语法。在 PowerShell 中需要用 `${PWD}` 或绝对路径。

```powershell
# ✅ PowerShell 中
docker run -v "${PWD}/src:/app/src" ...
```

### 5. 忘记 `docker stop` 就 `docker rm`，报错

```bash
docker rm node-demo
# Error: You cannot remove a running container
```

`docker rm` 只能删除已停止的容器。先 `docker stop node-demo`，或直接用 `docker rm -f node-demo` 强制删除。