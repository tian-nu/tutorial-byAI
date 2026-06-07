# 12 — COPY 和 ADD

> - 对应文档版本：Docker精通教程 outline v1
> - 适用环境：任何已安装 Docker 的系统
> - 读者角色：已理解 Dockerfile 基本结构，需要把代码和文件打包进镜像的开发者
> - 预计耗时：新手 25 分钟 / 熟手 12 分钟
> - 前置教程：第 10 章（第一个 Dockerfile）、第 11 章（FROM 和 RUN）
> - 可视化：无

---

## 我在做什么？

你的 Dockerfile 现在能装软件了（`RUN apt install nginx`），但 nginx 只是一个空壳——它没有你的网页文件、没有你的配置文件、没有你的应用代码。

这一章学 `COPY` 和 `ADD`——两条负责"把文件搬进镜像"的指令。你不要小看"复制文件"这件事——复制哪些、不复制哪些、从哪复制到哪，每一个细节都可能成为坑。你还会学到 `.dockerignore`，一个能让你构建速度快 10 倍的隐藏武器。

学完这一章，你能：
- 用 `COPY` 把代码和配置打包进镜像
- 理解构建上下文和 COPY 路径之间的关系
- 配置 `.dockerignore` 排除不需要的文件
- 知道 `ADD` 是什么、为什么一般不用它

---

## 一、COPY：把文件搬进镜像

### 基本语法

```dockerfile
COPY 源路径 目标路径
```

- **源路径**：相对于**构建上下文**的路径（就是 `docker build` 后面那个 `.` 代表的目录）
- **目标路径**：镜像里的绝对路径（或相对于 WORKDIR 的相对路径，第 13 章会讲）

### 最简单的例子

假设你的项目目录长这样：

```
my-project/
├── Dockerfile
└── index.html
```

Dockerfile：

```dockerfile
FROM nginx:alpine
COPY index.html /usr/share/nginx/html/index.html
```

构建：

```bash
cd my-project
docker build -t my-nginx:v1 .
```

发生了什么？

```
构建上下文 = my-project/ 目录
COPY index.html → 从 my-project/index.html 复制文件
→ 放到镜像的 /usr/share/nginx/html/index.html
```

运行：

```bash
docker run -d -p 8080:80 my-nginx:v1
curl http://localhost:8080
# 输出你的 index.html 内容
```

### 源路径的规则

#### 规则 1：相对于构建上下文

```dockerfile
# 构建上下文是 /home/user/my-project/
COPY index.html /app/index.html
# 源 = /home/user/my-project/index.html  ✅

# ❌ 这是死路一条
COPY /etc/hosts /app/hosts
# 源 = /home/user/my-project/etc/hosts  ← 不存在！
```

为什么？因为 Docker 只认构建上下文里的文件。`COPY` 不能访问宿主机上构建上下文之外的任何路径。这是个安全设计——否则一个恶意的 Dockerfile 可以把你的 `/etc/shadow` 打包进镜像。

#### 规则 2：不能 `..` 到上级目录

```dockerfile
# ❌ 错误
COPY ../other-project/config.yml /app/
# 构建上下文往上走，不行
```

COPY 的源路径**必须在构建上下文之内**。`..` 会跳出构建上下文，Docker 会直接报错。

#### 规则 3：源路径是目录时，复制目录内容

```dockerfile
# 假设构建上下文里有 ./src/ 目录
COPY src /app/
# 镜像里：/app/ 下面会有 src 目录里的所有内容

# 注意：复制的是 src 的**内容**，不是 src 目录本身
# 如果你想要 /app/src/，目标路径要写成 /app/src/
COPY src /app/src/
```

#### 规则 4：目标路径不存在时，自动创建

```dockerfile
COPY config/app.yml /etc/myapp/config.yml
# 如果 /etc/myapp/ 目录不存在，Docker 会自动创建
```

---

## 二、.dockerignore：别把垃圾桶也打包进去

### 问题场景

你有一个 Node.js 项目：

```
my-project/
├── Dockerfile
├── src/
├── package.json
├── node_modules/          ← 300 MB！
├── .git/                  ← 100 MB！
├── .env                   ← 里面有密码！
├── tests/
├── README.md
└── docker-compose.yml
```

你的 Dockerfile：

```dockerfile
FROM node:20
COPY . /app      # 把所有东西都复制进去了！
RUN npm install  # 又装了一遍依赖（明明 node_modules 已经有了）
```

这就好比你要搬家，把垃圾桶、废纸篓、旧报纸全塞进搬家箱——不是不行，但你浪费了时间、空间，甚至可能把碎纸机里的保密文件也搬走了。

### .dockerignore 是什么？

`.dockerignore` 是一个放在构建上下文根目录的文本文件，告诉 Docker：**"打包构建上下文时，忽略这些文件。"**

```
# .dockerignore
node_modules
.git
.env
*.log
.DS_Store
```

把它放在 `Dockerfile` 旁边：

```
my-project/
├── .dockerignore    ← 放这里
├── Dockerfile
├── src/
├── package.json
├── node_modules/    ← 不会被发给 Docker
└── ...
```

### 效果对比

```bash
# 没有 .dockerignore
docker build -t myapp .
# Sending build context to Docker daemon  532.4MB
# （node_modules 300MB + .git 100MB + 别的）

# 有 .dockerignore
docker build -t myapp .
# Sending build context to Docker daemon  2.3MB
# （只发了 src/ + package.json + Dockerfile）
```

**差别：200 倍。** 不是夸张，是你真实会遇到的数据。

### .dockerignore 的写法

```
# 注释用 #
# 每行一个模式

# 忽略具体文件
.env
Dockerfile
docker-compose.yml

# 忽略整个目录
node_modules/
.git/
.idea/
.vscode/

# 忽略所有 .log 文件
*.log

# 忽略所有以 . 开头的隐藏文件
.*

# 但保留某个特定文件（用 ! 排除异常）
!.gitkeep

# 忽略所有 markdown 文件
*.md
# 但保留 README.md
!README.md
```

> 规则和 `.gitignore` 基本一样。如果你会用 `.gitignore`，那你已经会用 `.dockerignore` 了。

### 一个 Node.js 项目的实战 .dockerignore

```
node_modules
npm-debug.log*
.git
.gitignore
.env
.env.*
.DS_Store
*.md
!README.md
coverage
.nyc_output
dist
.cache
```

> **想多一点**：很多人觉得 `.dockerignore` 是"锦上添花"的东西，不重要。错了。它能做三件关键的事：(1) 排除 `node_modules`，让 `COPY . /app` 不会把本地依赖拖进镜像；(2) 排除 `.git`，减少构建上下文几百 MB；(3) 排除 `.env`，**防止密钥泄露到镜像里**。第三条尤其致命——一旦 `.env` 进了镜像，你推送到 Docker Hub 的那一刻，密码就全网公开了。

---

## 三、ADD：COPY 的"高级版"，但一般别用

### ADD 做什么？

```dockerfile
ADD 源 目标
```

`ADD` 和 `COPY` 功能几乎一样——从构建上下文复制文件到镜像。但 `ADD` 多了两个能力：

1. **自动解压**：如果源是 `.tar`、`.tar.gz`、`.tgz`、`.bz2` 等压缩包，ADD 会自动解压到目标路径。
2. **URL 下载**：源可以是一个 URL，ADD 会从那个 URL 下载文件到镜像里。

### 自动解压：ADD 唯一合理的用法

```dockerfile
# 假设构建上下文里有个 app.tar.gz
ADD app.tar.gz /app/
# Docker 自动把 app.tar.gz 解压到 /app/ 下面
# 等价于你先 COPY app.tar.gz /app/ 再 RUN tar -xzf /app/app.tar.gz
```

如果你确实需要解压一个压缩包到镜像里，`ADD` 能帮你省掉一条 `RUN tar` 指令。

### URL 下载：为什么不推荐

```dockerfile
# ❌ 不推荐
ADD https://example.com/some-binary /usr/local/bin/some-binary
```

为什么不推荐？

1. **无法缓存**：ADD 的 URL 下载每次构建都重新下载，不受层缓存机制保护。即使 URL 指向的文件没变，Docker 也不知道。
2. **不可验证**：ADD 不会校验下载文件的完整性（没有 checksum 验证）。你无法确定下载到的是不是正确的文件。
3. **不可重复**：如果你要用 ADD 下载文件，每次 `docker build` 的结果取决于远程服务器当时返回什么。远程文件变了，你的构建静默变化，而 Dockerfile 一个字没改——这是排查噩梦。

**推荐替代方案**：

```dockerfile
# ✅ 用 RUN + curl/wget 代替，更可控
FROM alpine:latest
RUN apk add --no-cache curl \
    && curl -fsSL https://example.com/some-binary -o /usr/local/bin/some-binary \
    && chmod +x /usr/local/bin/some-binary \
    && apk del curl
#    ──────┬──────
#    用完就卸载 curl，减小镜像体积！
```

### 为什么推荐用 COPY 而非 ADD？

| 维度 | COPY | ADD |
|------|------|-----|
| 行为 | 只做复制 | 复制 + 自动解压 + URL 下载 |
| 可预测性 | 高。COPY 就只做字面意思的"复制" | 低。源路径如果是 tar，行为会"意外地"变成解压 |
| 安全性 | 高。只能访问构建上下文 | 中。URL 下载来源不可控 |
| 推荐程度 | ✅ 首选 | ⚠️ 仅在需要解压 tar 文件时使用 |

> Docker 官方文档也说："For most use cases, `COPY` is preferred." 记住一条口诀：**能用 COPY 就用 COPY，ADD 只在你明确需要自动解压时登场。**

---

## 四、实战：给 nginx 镜像加静态网页

### 项目结构

```
my-web/
├── Dockerfile
├── .dockerignore
├── html/
│   └── index.html
└── config/
    └── nginx.conf
```

### 步骤 1：创建文件

**index.html** (`html/index.html`)：

```html
<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><title>Docker Nginx Demo</title></head>
<body>
  <h1>🎉 这页来自 Docker 容器！</h1>
  <p>如果你能看到这行字，说明 COPY 指令成功把 HTML 文件放进了镜像。</p>
</body>
</html>
```

**nginx.conf** (`config/nginx.conf`)：

```nginx
server {
    listen 80;
    server_name localhost;
    location / {
        root   /usr/share/nginx/html;
        index  index.html;
    }
}
```

**.dockerignore**：

```
.git
README.md
.vscode
```

**Dockerfile**：

```dockerfile
FROM nginx:alpine

# 把自定义 nginx 配置复制进去
COPY config/nginx.conf /etc/nginx/conf.d/default.conf

# 把 HTML 文件复制进去
COPY html/ /usr/share/nginx/html/

# 验证配置文件语法（构建时检查，有问题立刻报错）
RUN nginx -t
```

### 步骤 2：构建

```bash
cd my-web
docker build -t my-nginx-web:v1 .
```

预期输出：

```
[+] Building 2.1s (8/8) FINISHED
 => [1/3] FROM docker.io/library/nginx:alpine
 => [2/3] COPY config/nginx.conf /etc/nginx/conf.d/default.conf
 => [3/3] COPY html/ /usr/share/nginx/html/
 => [3/3] RUN nginx -t
 => exporting to image
 => => naming to docker.io/library/my-nginx-web:v1
nginx: the configuration file /etc/nginx/conf.d/default.conf syntax is ok
nginx: configuration file /etc/nginx/conf.d/default.conf test is successful
```

> `nginx -t` 是 nginx 的配置语法检查命令。把它放在 Dockerfile 里，构建时就能发现配置错误，而不是运行时才发现。这叫"左移"（shift left）——把检查提前到尽可能早的阶段。

### 步骤 3：运行并验证

```bash
docker run -d -p 8080:80 --name web-demo my-nginx-web:v1
curl http://localhost:8080
# 输出：
# <!DOCTYPE html>
# <html>
# ...
# <h1>🎉 这页来自 Docker 容器！</h1>
```

浏览器打开 `http://localhost:8080`，你应该看到你自己写的 HTML 页面。

### 步骤 4：验证 .dockerignore 生效

```bash
# 故意创建一个不该进镜像的大文件
dd if=/dev/zero of=bigfile.bin bs=1M count=100 2>/dev/null || fsutil file createnew bigfile.bin 104857600

# 不加 .dockerignore 时构建（会慢）
# Sending build context to Docker daemon  105MB

# 在 .dockerignore 里加一行 bigfile.bin
echo "bigfile.bin" >> .dockerignore

# 重新构建
docker build -t my-nginx-web:v1 .
# Sending build context to Docker daemon  5.2kB  ← 少了几万倍！
```

---

## 五、COPY 的最佳实践

### 1. 复制整个目录时，末尾加 `/`

```dockerfile
# ✅ 清晰：复制目录内容到目标
COPY src/ /app/src/

# ⚠️ 容易混淆：有时候行为和你预期不同
COPY src /app/
# 如果 src 是目录，/app/ 下会有 src 的所有内容，不是 /app/src/
```

末尾加 `/` 明确告诉 Docker（和读代码的人）：目标是一个目录。

### 2. 分层复制，利用缓存

```dockerfile
# ✅ 好的做法
COPY package.json package-lock.json /app/
RUN npm ci --production
COPY src/ /app/src/
# 依赖清单很少变 → 缓存；代码经常变 → 只重建最后一层

# ❌ 不好的做法
COPY . /app/
RUN npm ci --production
# 任何文件改动都导致 COPY 层和 RUN 层全部重建
```

### 3. 用 `--chown` 指定文件所有者

```dockerfile
# 在需要非 root 用户时（安全性）
COPY --chown=node:node src/ /app/src/
```

默认情况下，COPY 进去的文件所有者是 root。如果你的应用以非 root 用户运行，用 `--chown` 指定所有者和组。

---

## 六、我做得对不对？

### 验证方法

```bash
# 1. 确认项目结构
ls -R
# 应该看到 Dockerfile、.dockerignore、html/、config/

# 2. 构建
docker build -t my-nginx-web:v1 .

# 3. 检查构建上下文的发送大小
# 注意构建输出第一行 "Sending build context to Docker daemon"
# 应该很小（< 1MB）

# 4. 运行
docker run -d -p 8080:80 --name web-test my-nginx-web:v1

# 5. 验证页面
curl http://localhost:8080
# 应该看到你的 HTML 内容

# 6. 验证 nginx 配置被正确替换
docker exec web-test cat /etc/nginx/conf.d/default.conf
# 应该看到你自定义的配置，不是 nginx 默认配置

# 7. 清理
docker stop web-test && docker rm web-test
```

---

## 七、不对怎么办？

### 常见错误 1：`COPY` 源文件不在构建上下文里

```bash
docker build -t myapp .
# => ERROR [2/3] COPY failed: file not found in build context
```

❌ 原因：源路径不在构建上下文中。比如 `COPY /home/user/config.yml /app/`——但你的构建上下文是 `my-project/`。

✅ 解决：

```bash
# 检查你的 docker build 在哪个目录执行的
pwd   # 确认当前位置

# COPY 的源路径 = pwd 的路径 + 源路径
# 如果你的文件在上级目录，把它复制到当前目录，或者
# 更改构建上下文路径：
docker build -t myapp -f myapp/Dockerfile .
# 用 .（项目根目录）作为构建上下文，
# Dockerfile 在 myapp/ 子目录里
```

### 常见错误 2：`.dockerignore` 忽略得太狠，把需要的文件也排除了

```
# .dockerignore
*
```

（把所有文件排除了，Dockerfile 都读不到。）

✅ 最小化的 `.dockerignore`：

```
node_modules
.git
.env
```

加一条测试一条：`docker build` 看看构建上下文发送大小是否合理。

### 常见错误 3：把 `.env` 打包进了镜像（安全问题）

```bash
# Dockerfile 里写了
COPY . /app/

# .dockerignore 里忘了写 .env
# → .env 被打包进镜像！
```

`.env` 文件通常包含数据库密码、API 密钥等敏感信息。如果它进了镜像：

1. 任何能拉取镜像的人都能提取出 `.env`。
2. 你把镜像推送到 Docker Hub……密码就上公网了。

**解决**：

1. `.dockerignore` 里必须有 `.env`。
2. 敏感配置用环境变量（`ENV` 指令或 `docker run -e`），不要写进镜像。
3. 永远用 `your_password_here` 占位，真实密钥用 Docker Secret 或外部配置管理工具。

### 常见错误 4：误用 `ADD` 下载文件，发现每次构建都不一样

```dockerfile
ADD https://github.com/some/release/download/v1.0/binary /usr/local/bin/
```

❌ 问题：没有版本校验，下载的可能是任何东西。而且 ADD 不支持在构建时做 checksum 验证。

✅ 替代：

```dockerfile
RUN curl -fsSL https://github.com/some/release/download/v1.0/binary \
    -o /usr/local/bin/binary \
    && echo "expected_sha256_here /usr/local/bin/binary" | sha256sum -c \
    && chmod +x /usr/local/bin/binary
```

手动校验 SHA256，确保下载的是正确的文件。

### 常见错误 5：`COPY dir /app` 和 `COPY dir/ /app/` 行为的细微差异

```dockerfile
COPY src /app
# 如果 src 是目录：把 src 目录的**内容**放到 /app 下
# 如果 src 是文件：把 src 文件放到 /app

COPY src/ /app/
# 明确告诉 Docker：src 是目录，把它的内容放到 /app/
```

末尾的 `/` 在可读性上很重要。帮未来的你和你的同事少一个困惑。

---

## 本章小结

| 本章学了什么 | 对应命令/概念 | 注意事项 |
|-------------|-------------|---------|
| COPY 基本用法 | `COPY 源 目标` | 源路径相对于构建上下文；目标路径绝对路径或相对 WORKDIR |
| 源路径规则 | 不能访问构建上下文之外；不能用 `..` | Docker 的安全设计，不是 bug |
| `.dockerignore` | 排除文件，类似 `.gitignore` | 必须配！不然 node_modules、.git、.env 全打包 |
| ADD 的作用 | 自动解压 tar、URL 下载 | 一般只用在需要解压 tar 的场景 |
| 为什么推荐 COPY | 行为可预测、安全、官方推荐 | ADD 做太多事，反而不可控 |
| 分层 COPY | 先 COPY 依赖清单，RUN 安装，再 COPY 代码 | 利用缓存，代码改动后只重建最后一层 |
| `--chown` | `COPY --chown=user:group` | 非 root 运行的应用需要 |
| 构建时验证 | `RUN nginx -t` 等 | 把检查"左移"到构建阶段 |

---

## 本篇最可能出错的地方及原因

### 1. `.dockerignore` 从头到尾没创建

**现象**：`docker build` 发送了几百 MB 的构建上下文；镜像里有 node_modules、.git、.env。

**原因**：Dockerfile 项目自带了 `.dockerignore` 模板，但开发者不知道这东西存在，也没人提醒。`COPY . /app` 把一切全拖进镜像。

**解决**：每个 Docker 项目必须配 `.dockerignore`。最低要求——排除 `node_modules`、`.git`、`.env`。

### 2. `.env` 被打包进镜像（最危险的错误）

**原因**：`.dockerignore` 里忘了 `.env`，`COPY . /app` 把它带进了镜像。

**后果**：数据库密码、API 密钥在镜像层里明文存储。镜像推送到 Docker Hub → 密钥公开。而且**即使后面的层"删除"了 `.env`，它仍然存在于下层**，有镜像访问权限的人能提取出来。

**预防**：`.dockerignore` 的第一条就写 `.env`。敏感配置永远不要进镜像，用 `docker run -e` 或 Docker Secret 注入。

### 3. COPY 路径写的是宿主机绝对路径，不是相对于构建上下文

```dockerfile
# ❌ 错误认知
COPY /home/user/my-code/src/ /app/
# Docker 理解：
# 源 = 构建上下文 + /home/user/my-code/src/  ← 不存在！

# ✅ 正确
COPY ./src/ /app/
```

**原因**：新手把 COPY 的源路径理解成了"宿主机上的任意路径"。

**口诀**：COPY 的源路径 = 构建上下文内的相对路径。你的 `docker build` 在哪个目录下执行的，COPY 的源就是从那个目录出发。

### 4. 在 alpine 里用 `apt`，在 ubuntu 里用 `apk`（延续第 11 章的坑）

在写 COPY + RUN 的组合时，RUN 里忘了不同基础镜像用不同包管理器。Alpine = `apk`，Ubuntu/Debian = `apt`。

### 5. ADD 自动解压的"惊喜"——以为是普通文件复制，结果被解压了

```dockerfile
ADD myapp.tar.gz /app/
# 你以为只是复制了一个压缩包到 /app/myapp.tar.gz
# 实际上 Docker 把它解压了，/app/ 下是解压后的内容！
```

这是 ADD 最容易造成困惑的地方。同样是"把东西搬进去"，COPY 和 ADD 的行为可能不一样。所以记住：**能用 COPY 就用 COPY。**