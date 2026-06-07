# 27 — ARG 构建参数

> - 对应文档版本：Docker精通教程 outline v1
> - 适用环境：任何已安装 Docker 的系统
> - 读者角色：已掌握 Dockerfile 基本写法，需要构建时灵活配置的开发者
> - 预计耗时：新手 30 分钟 / 熟手 15 分钟
> - 前置教程：第 10～14 章（Dockerfile 系列）、第 24 章（环境变量）
> - 可视化：无

---

## 我在做什么？

你写了一个 Dockerfile，里面写死了 `FROM node:20`。今天 Node.js 22 发布了，你想试试新版本。你怎么办？改 Dockerfile 的 FROM 行？如果你有 10 个项目，每个项目都要改一行。如果只是临时测试，改完还要改回来。

能不能在构建时动态指定版本号？比如 `docker build --build-arg NODE_VERSION=22 .`，而不改 Dockerfile？

能。这就是 **ARG** *此术语见附录C* ——构建阶段的变量，只存在于 `docker build` 的过程中，不进最终镜像。

学完这一章，你能：
- 用 `ARG` 在 Dockerfile 里定义构建参数
- 用 `--build-arg` 在构建时传入值
- 区分 ARG 和 ENV 的使用场景
- 理解 ARG 的安全边界（哪些信息会泄露，哪些不会）

---

## 一、ARG 是什么？

### 一句话定义

> **ARG 是 Dockerfile 里的"构建时变量"。它只在 `docker build` 过程中有效，构建完成后就消失了，不进入最终镜像。**

### 基本语法

```dockerfile
# 定义 ARG，带默认值
ARG NODE_VERSION=20

# 使用 ARG（就像使用普通变量）
FROM node:${NODE_VERSION}-alpine
```

构建时：

```bash
# 用默认值（20）
docker build -t myapp .

# 指定其他版本
docker build --build-arg NODE_VERSION=22 -t myapp .
```

### ARG 的生命周期

```
docker build 开始
  │
  ├─ ARG 定义生效 ────────────────────┐
  │                                   │
  ├─ FROM ...                         │ ARG 的作用域
  ├─ RUN ...                          │ （只在构建时）
  ├─ COPY ...                         │
  ├─ CMD ...                          │
  │                                   │
  └─ 构建结束 ────────────────────────┘
       │
       ARG 消失。镜像里没有 ARG 的值。

docker run 开始
  │
  └─ 容器里没有 ARG。ARG 的值无法在运行时获取。
```

> **想多一点**：ARG 和 ENV 的区别，是 Docker 新手最容易混淆的概念之一。想象你在烤蛋糕：ARG 是"烤箱温度"——只在烤的过程中有用，蛋糕出炉后，温度这个概念不存在了。ENV 是"蛋糕里加的糖"——蛋糕烤好后，糖还在里面，吃的时候能尝到。ARG 是构建时的，ENV 是运行时的。

---

## 二、ARG vs ENV：一张表说清楚

| 维度 | ARG | ENV |
|------|-----|-----|
| **生效时机** | 仅 `docker build` 时 | `docker build` + `docker run` 时 |
| **是否进入最终镜像** | ❌ 不进入 | ✅ 进入 |
| **`docker run` 时能否访问** | ❌ 不能 | ✅ 能 |
| **`docker history` 能否看到** | ⚠️ 值在中间层可见 | ✅ 值在镜像层可见 |
| **能否在运行时覆盖** | ❌ 构建完就固定了 | ✅ `docker run -e` 可覆盖 |
| **定义方式** | `ARG VAR=value` | `ENV VAR=value` |
| **传入方式** | `docker build --build-arg VAR=value` | `docker run -e VAR=value` |
| **典型用途** | 版本号、构建选项、代理设置 | 运行环境、数据库地址、日志级别 |

### 一个对比实验

```dockerfile
FROM alpine:latest
ARG BUILD_TIME=unknown
ENV APP_NAME=myapp
RUN echo "Build time: $BUILD_TIME" > /build-info.txt
RUN echo "App name: $APP_NAME" >> /build-info.txt
CMD ["cat", "/build-info.txt"]
```

```bash
docker build --build-arg BUILD_TIME="2026-06-06" -t arg-test .
docker run --rm arg-test
# 输出：
# Build time: 2026-06-06
# App name: myapp
```

两个值都打出来了，看起来一样？再试：

```bash
# 运行时查看环境变量
docker run --rm arg-test env
# PATH=/usr/local/sbin:...
# APP_NAME=myapp
# （没有 BUILD_TIME！）

# 运行时覆盖 ENV
docker run --rm -e APP_NAME=production arg-test env
# APP_NAME=production   ← ENV 被覆盖了

# 试试覆盖 ARG（没用）
docker run --rm -e BUILD_TIME=now arg-test env
# （BUILD_TIME 不存在，ARG 在运行时无法访问）
```

---

## 三、ARG 的默认值

### 不给默认值

```dockerfile
ARG VERSION
FROM alpine:${VERSION}
```

```bash
docker build -t test .
# 报错：failed to process "${VERSION}": missing ':' in substitution
# 或者 VERSION 为空，导致 FROM alpine: 语法错误
```

如果 ARG 没有默认值，`--build-arg` 又不传，这个变量就是空的。**建议总是给 ARG 一个默认值**，除非你明确希望"不传就报错"。

### 给默认值

```dockerfile
ARG VERSION=latest
FROM alpine:${VERSION}
```

```bash
docker build -t test .                  # 用默认值 latest
docker build --build-arg VERSION=3.19 -t test .  # 用 3.19
```

### 默认值的妙用：开箱即用，但可定制

```dockerfile
ARG NODE_VERSION=20
ARG ALPINE_VERSION=3.20
FROM node:${NODE_VERSION}-alpine${ALPINE_VERSION}
```

新同事 clone 项目后直接 `docker build`，用默认值就能跑。需要定制时，加 `--build-arg`。这和第 24 章学的 `${VAR:-默认值}` 思路一致：**默认值让配置"可选的"。**

---

## 四、预定义 ARG：Docker 自带的内置变量

Docker 提供了一些预定义的 ARG，你不需要在 Dockerfile 里声明就能用：

| 预定义 ARG | 含义 | 示例值 |
|-----------|------|--------|
| `HTTP_PROXY` | HTTP 代理地址 | `http://proxy.example.com:8080` |
| `HTTPS_PROXY` | HTTPS 代理地址 | `http://proxy.example.com:8080` |
| `NO_PROXY` | 不走代理的地址 | `localhost,127.0.0.1,.internal` |
| `FTP_PROXY` | FTP 代理地址 | `http://proxy.example.com:8080` |

这些预定义 ARG 主要用于**构建时走代理**。比如公司网络需要通过代理访问外网，构建时 Docker 要拉取基础镜像、`apt-get` 要下载包，都需要走代理：

```bash
docker build \
  --build-arg HTTP_PROXY=http://proxy.company.com:8080 \
  --build-arg HTTPS_PROXY=http://proxy.company.com:8080 \
  -t myapp .
```

> **注意**：预定义 ARG 不需要在 Dockerfile 里显式声明 `ARG HTTP_PROXY`。但如果你在 Dockerfile 里写了 `ARG HTTP_PROXY`，你就覆盖了它的自动传递行为——Docker 不会再自动把宿主机的代理环境变量传进去。所以**一般不要手动声明这些预定义 ARG**，让 Docker 自动处理。

### 多平台构建的预定义 ARG

如果你用 `docker buildx` 做多平台构建（比如同时构建 x86 和 ARM 的镜像），还有这些预定义 ARG：

| 预定义 ARG | 含义 |
|-----------|------|
| `TARGETPLATFORM` | 目标平台，如 `linux/arm64` |
| `BUILDPLATFORM` | 构建平台，如 `linux/amd64` |
| `TARGETOS` | 目标操作系统，如 `linux` |
| `TARGETARCH` | 目标架构，如 `arm64` |

---

## 五、实战：通过 ARG 控制安装的软件版本

### 场景：一个 Dockerfile 支持多个 Python 版本

```dockerfile
# Dockerfile
ARG PYTHON_VERSION=3.12
FROM python:${PYTHON_VERSION}-slim

WORKDIR /app
COPY requirements.txt .

# 通过 ARG 控制是否安装开发依赖
ARG INSTALL_DEV=false
RUN if [ "$INSTALL_DEV" = "true" ]; then \
      pip install --no-cache-dir -r requirements.txt && \
      pip install --no-cache-dir pytest pylint; \
    else \
      pip install --no-cache-dir -r requirements.txt; \
    fi

COPY . .
CMD ["python", "app.py"]
```

使用：

```bash
# 生产构建（默认：Python 3.12，不装开发依赖）
docker build -t myapp:prod .

# 开发构建（Python 3.11，装开发依赖）
docker build \
  --build-arg PYTHON_VERSION=3.11 \
  --build-arg INSTALL_DEV=true \
  -t myapp:dev .

# 试试 Python 3.13
docker build --build-arg PYTHON_VERSION=3.13 -t myapp:py313 .
```

一个 Dockerfile，三个不同的镜像。**不用改 Dockerfile，不用创建分支，不用维护多个 Dockerfile。**

### 场景：控制多阶段构建的目标阶段

结合第 25 章的多阶段构建，ARG 可以控制使用哪个阶段：

```dockerfile
# Dockerfile
ARG NODE_VERSION=20

# ===== 第一阶段：构建 =====
FROM node:${NODE_VERSION}-alpine AS builder
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npm run build

# ===== 第二阶段：Nginx（生产） =====
FROM nginx:alpine AS production
COPY --from=builder /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]

# ===== 第三阶段：Node 开发服务器（开发） =====
FROM node:${NODE_VERSION}-alpine AS development
WORKDIR /app
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app .
EXPOSE 3000
CMD ["npm", "run", "dev"]
```

```bash
# 生产构建（默认）
docker build -t myapp:prod .

# 开发构建（指定 target 阶段）
docker build --target development -t myapp:dev .
```

---

## 六、ARG 的安全问题：什么能看见，什么不能

### ARG 值在 `docker history` 中可见

这是一个重要的安全考量：

```bash
docker build --build-arg SECRET_TOKEN=abc123 -t myapp .
docker history myapp
```

输出中可能包含：

```
IMAGE          CREATED BY
abc123         RUN echo "Token: abc123" > /token.txt
```

如果你在 `RUN` 中使用了 ARG 值，**这个值会出现在 `docker history` 里**。任何能拉取这个镜像的人都能看到它。

### 因此：ARG 不能传密钥

```dockerfile
# ❌ 危险！API 密钥通过 ARG 传入
ARG API_KEY=your_key_here
RUN echo "API_KEY=$API_KEY" > /config
# docker history 会显示这一行的完整内容，包括密钥
```

✅ 正确做法：密钥在运行时传入，用 ENV 或 Docker secrets：

```bash
# 运行时传入密钥
docker run -e API_KEY=your_key_here myapp
```

或者用 Docker Swarm / Kubernetes 的 secrets 机制。

### ARG 值和 ENV 值的可见性对比

```dockerfile
ARG SECRET_ARG=arg_secret
ENV PUBLIC_ENV=env_public
RUN echo "ARG: $SECRET_ARG" > /arg.txt
RUN echo "ENV: $PUBLIC_ENV" > /env.txt
```

```bash
docker history myapp
# 能看到：
#   RUN echo "ARG: arg_secret" > /arg.txt    ← ARG 值可见
#   ENV PUBLIC_ENV=env_public                ← ENV 值可见
#   RUN echo "ENV: env_public" > /env.txt    ← 同上

docker run --rm myapp env
# 能看到：
#   PUBLIC_ENV=env_public
#   （SECRET_ARG 不存在）
```

ARG 和 ENV 的值在 `docker history` 中**都可见**。区别在于：
- ARG 在镜像的环境变量中**不可见**（`docker run ... env` 里没有）
- ENV 在镜像的环境变量中**可见**

> **想多一点**：很多人以为 ARG "不进镜像"所以"安全"。这是一个危险的误解。ARG 确实不进入最终镜像的**环境变量**，但如果你在 `RUN` 指令里使用了 ARG 的值，这个值就嵌入了那一层镜像的**命令历史**中。任何能访问镜像的人都能用 `docker history` 看到。所以规则很简单：**ARG 不传密钥，ENV 也不传密钥。密钥永远在运行时注入。** 如果你必须在构建时访问密钥（比如 `git clone` 私有仓库），用 `--secret` 特性（`docker build --secret`），但这超出了本章范围。

---

## 七、ARG 作用域：在哪里定义，在哪里生效

### 规则 1：ARG 在 FROM 之前定义，对整个 Dockerfile 有效

```dockerfile
ARG NODE_VERSION=20
FROM node:${NODE_VERSION}-alpine
# NODE_VERSION 在这里可用
RUN echo "Node version: ${NODE_VERSION}"
```

### 规则 2：ARG 在 FROM 之后定义，只对当前阶段有效

```dockerfile
FROM alpine:latest
ARG MY_VAR=hello
RUN echo $MY_VAR   # ✅ 可用

FROM alpine:latest
RUN echo $MY_VAR   # ❌ 不可用！新阶段，ARG 需要重新声明
```

### 规则 3：多阶段构建中，每个阶段需要重新声明 ARG

```dockerfile
ARG NODE_VERSION=20          # 全局 ARG

FROM node:${NODE_VERSION}-alpine AS builder
ARG NODE_VERSION             # 必须重新声明才能用
RUN echo "Building with Node ${NODE_VERSION}"

FROM alpine:latest
ARG NODE_VERSION             # 也必须重新声明
RUN echo "Running, built with Node ${NODE_VERSION}"
```

注意：重新声明时**不需要写默认值**（默认值在全局声明里已经有了），但也可以覆盖：

```dockerfile
ARG NODE_VERSION=20

FROM node:${NODE_VERSION}-alpine AS builder
ARG NODE_VERSION=18          # 可以覆盖全局默认值
RUN echo "Building with Node ${NODE_VERSION}"   # 输出 18
```

### 规则 4：`--build-arg` 的值覆盖默认值

```bash
docker build --build-arg NODE_VERSION=22 -t myapp .
# 无论 ARG 默认值是什么，这里都用 22
```

---

## 八、我做得对不对？

### 验证方法

```bash
# 1. 创建测试 Dockerfile
cat > Dockerfile << 'EOF'
ARG VERSION=3.19
FROM alpine:${VERSION}
ARG BUILD_DATE=unknown
RUN echo "Build date: $BUILD_DATE" > /build-info.txt
CMD ["cat", "/build-info.txt"]
EOF

# 2. 用默认值构建
docker build -t arg-test-default .
docker run --rm arg-test-default
# 预期：Build date: unknown

# 3. 用 --build-arg 构建
docker build --build-arg BUILD_DATE="2026-06-06" -t arg-test-custom .
docker run --rm arg-test-custom
# 预期：Build date: 2026-06-06

# 4. 验证 ARG 不在运行时环境变量中
docker run --rm arg-test-custom env
# 预期：看不到 BUILD_DATE

# 5. 验证 docker history 中能看到 ARG 值
docker history arg-test-custom
# 在输出中应该能看到 "Build date: 2026-06-06"

# 6. 验证 ARG 不传时用默认值
docker build -t arg-test-default2 .
docker run --rm arg-test-default2
# 预期：Build date: unknown
```

---

## 九、不对怎么办？

### 常见错误 1：ARG 和 ENV 混淆

```dockerfile
# ❌ 想用 ARG 做运行时配置
ARG LOG_LEVEL=info
CMD ["node", "server.js"]
# 运行时 LOG_LEVEL 不存在，server.js 读不到
```

✅ 修正：

```dockerfile
# 运行时配置用 ENV
ENV LOG_LEVEL=info
CMD ["node", "server.js"]
```

**判断标准**：问自己"这个值在容器运行时还需要吗？"如果需要（比如日志级别、数据库地址），用 ENV。如果只在构建时需要（比如版本号、安装选项），用 ARG。

### 常见错误 2：ARG 传了敏感信息

```dockerfile
# ❌ 密钥通过 ARG 传入
ARG NPM_TOKEN=your_token_here
RUN echo "//registry.npmjs.org/:_authToken=$NPM_TOKEN" > ~/.npmrc
RUN npm ci
```

`docker history` 会让所有人看到你的 npm token。

✅ 修正：用 Docker BuildKit 的 `--secret` 特性：

```bash
# Dockerfile
RUN --mount=type=secret,id=npm_token \
    NPM_TOKEN=$(cat /run/secrets/npm_token) \
    echo "//registry.npmjs.org/:_authToken=$NPM_TOKEN" > ~/.npmrc && \
    npm ci

# 构建
docker build --secret id=npm_token,src=./npm_token.txt -t myapp .
```

### 常见错误 3：多阶段构建中 ARG 只在第一阶段声明

```dockerfile
ARG NODE_VERSION=20

FROM node:${NODE_VERSION}-alpine AS builder
ARG NODE_VERSION        # ✅ 声明了
RUN echo $NODE_VERSION

FROM alpine:latest
# ❌ 忘了重新声明 ARG NODE_VERSION
RUN echo $NODE_VERSION  # 输出为空！
```

✅ 修正：每个阶段需要 ARG 时，都要重新声明（不带默认值即可）：

```dockerfile
FROM alpine:latest
ARG NODE_VERSION        # 重新声明
RUN echo $NODE_VERSION  # ✅ 输出 20
```

### 常见错误 4：`--build-arg` 变量名拼写错误

```bash
docker build --build-arg NODE_VRESION=22 -t myapp .
#                        拼写错误：VRESION 而不是 VERSION
```

Docker 不会报错——它只是把 `NODE_VERSION` 当作一个未传入的变量，用默认值（如果有的话）。你以为是 Node 22，实际上是 Node 20。

✅ 排查：

```dockerfile
# 在 Dockerfile 里加一个验证层
ARG NODE_VERSION=20
RUN echo "Actual Node version: ${NODE_VERSION}"
# 构建时看输出，确认值是你期望的
```

### 常见错误 5：在运行时尝试用 `-e` 覆盖 ARG

```bash
docker run -e VERSION=3.19 myapp
# VERSION 是 ARG 不是 ENV，-e 覆盖不了
```

✅ 如果需要在运行时覆盖，用 ENV：

```dockerfile
ARG VERSION=3.19
ENV APP_VERSION=$VERSION
# 现在 APP_VERSION 是 ENV，运行时可以用 -e 覆盖
```

---

## 十、术语解释

| 术语 | 解释 |
|------|------|
| **ARG** *此术语见附录C* | Dockerfile 的构建时变量，用 `ARG VAR=value` 定义，`--build-arg VAR=value` 传入。只在 `docker build` 过程中有效，不进最终镜像 |
| **`--build-arg`** *此术语见附录C* | `docker build` 的参数，用于向 Dockerfile 传递 ARG 变量的值 |
| **ENV** *此术语见附录C* | Dockerfile 的运行时环境变量，在构建和运行阶段都有效，会进入最终镜像 |
| **预定义 ARG** | Docker 内置的 ARG 变量，如 `HTTP_PROXY`、`HTTPS_PROXY`，不需要手动声明 |

---

## 本章小结

| 本章学了什么 | 对应命令/概念 | 注意事项 |
|-------------|-------------|---------|
| ARG 是什么 | 构建时变量，只在 `docker build` 时有效 | 不在最终镜像的环境变量中 |
| ARG vs ENV | ARG 构建时，ENV 运行时也保留 | 运行时要用的用 ENV，只在构建时用的用 ARG |
| 默认值 | `ARG VERSION=latest` | 建议总是给默认值，让 Dockerfile 开箱即用 |
| `--build-arg` 传入 | `docker build --build-arg VERSION=22 .` | 变量名拼写错误不会报错，注意检查 |
| 预定义 ARG | `HTTP_PROXY`、`HTTPS_PROXY` 等 | 不需要手动声明，Docker 自动从宿主机环境继承 |
| 安全考量 | ARG 值在 `docker history` 中可见 | 永远不要通过 ARG 传密钥 |
| 多阶段中的作用域 | 每个阶段需要重新声明 ARG | 不重新声明的话，ARG 为空 |
| 控制版本号 | `ARG NODE_VERSION=20` → `FROM node:${NODE_VERSION}` | 一个 Dockerfile 支持多个版本 |
| 验证 | `docker history` 查看、`docker run env` 对比 | ARG 在 history 中可见，在 env 中不可见 |

---

## 本篇最可能出错的地方及原因

### 1. ARG 和 ENV 混淆

**这是最高频的错误。** 把运行时需要的配置（数据库地址、日志级别）写成 ARG，结果容器启动后读不到配置。或者把构建时需要的配置（版本号）写成 ENV，结果镜像里多了一堆不必要的环境变量，还可能和运行时环境变量冲突。

**判断口诀**：这个值在容器运行后还需要吗？需要 → ENV；不需要 → ARG。

### 2. ARG 传密钥

**这是安全层面最高频的错误。** 以为 ARG "不进镜像"所以安全，但 ARG 值在 `docker history` 的 `RUN` 行中完整可见。任何能拉取镜像的人都能看到这些值。

**铁律**：密钥永远不在构建时传入。无论 ARG 还是 ENV，都不要传密钥。构建时需要密钥（如 npm token、git credentials）用 BuildKit 的 `--secret` 特性。

### 3. 多阶段构建中 ARG 作用域

**原因**：在 Dockerfile 开头定义了 `ARG NODE_VERSION=20`，以为整个 Dockerfile 都能用。但每个 `FROM` 开始一个新阶段，ARG 也需要重新声明。

**最佳实践**：每个阶段开头都显式声明需要的 ARG：

```dockerfile
ARG NODE_VERSION=20

FROM node:${NODE_VERSION}-alpine AS builder
ARG NODE_VERSION
# ... 使用 NODE_VERSION

FROM alpine:latest
ARG NODE_VERSION
# ... 使用 NODE_VERSION
```

即使不写默认值，重新声明时 `ARG NODE_VERSION`（不带等号）就够了，它会继承全局声明或 `--build-arg` 传入的值。

### 4. `--build-arg` 拼写错误，静默失败

**原因**：`docker build --build-arg NODE_VRESION=22 .`（拼写错误），Docker 不会报错，只是用默认值。你以为是 Node 22，实际是 Node 20。

**排查**：在 Dockerfile 里加 `RUN echo "NODE_VERSION=${NODE_VERSION}"`，构建时确认日志输出和你期望的一致。

### 5. ARG 在 ENV 之后定义，但 ENV 引用了 ARG

```dockerfile
ENV APP_VERSION=$VERSION    # ❌ VERSION 还没定义
ARG VERSION=1.0
```

✅ 修正：

```dockerfile
ARG VERSION=1.0
ENV APP_VERSION=$VERSION    # ✅ ARG 先定义，ENV 引用它
```

Dockerfile 是顺序执行的，ENV 引用 ARG 时，ARG 必须已经定义。