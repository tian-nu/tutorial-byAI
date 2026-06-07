# 30 — 项目二：Python 应用容器化

> - 对应文档版本：Docker精通教程 outline v1
> - 适用环境：任何已安装 Docker 的系统
> - 读者角色：已掌握 Dockerfile 基础，准备容器化 Python 应用的开发者
> - 预计耗时：新手 35 分钟 / 熟手 15 分钟
> - 前置教程：第 10 章（Dockerfile）、第 29 章（Node.js 容器化）
> - 可视化：无

---

## 我在做什么？

上一章你容器化了一个 Node.js 应用。这一章换 Python——用 FastAPI 写一个 REST API，同样走一遍容器化流程。Node.js 和 Python 的容器化套路非常相似，但 Python 有几个专属的"坑"和"为什么"——比如**容器里不需要虚拟环境**、**开发模式和生产模式应该用不同的启动方式**。

你读完这一章会发现：容器化不同语言的应用，90% 的套路是一样的，只有 10% 是语言特有的。掌握这 10%，你就真正掌握了容器化的"通用心法"。

学完这一章，你能：
- 写一个 Python 应用的 Dockerfile（FastAPI / Flask 通用）
- 理解为什么容器里不需要 `python -m venv`
- 区分开发模式（`uvicorn --reload`）和生产模式（`gunicorn` 或 `uvicorn` 无 `--reload`）
- 正确配置 `.dockerignore` 忽略 `__pycache__`、`.venv`
- 用 `curl` 验证 API 端点

---

## 一、项目代码：一个 FastAPI 应用

### 项目结构

```
python-app/
├── app.py
├── requirements.txt
├── Dockerfile
└── .dockerignore
```

### requirements.txt

```
fastapi==0.104.1
uvicorn[standard]==0.24.0
```

就两行。`fastapi` 是 Web 框架，`uvicorn` 是 ASGI 服务器（跑 FastAPI 的东西）。

### app.py

```python
import os
from fastapi import FastAPI

app = FastAPI()

# 根路径
@app.get("/")
def root():
    return {
        "message": "Hello from FastAPI in Docker!",
        "env": os.getenv("APP_ENV", "development")
    }

# 健康检查
@app.get("/health")
def health():
    return {"status": "OK"}
```

这个应用做的事和上一章 Node.js 的几乎一模一样：一个根路径、一个健康检查端点。这是故意的——让你看到，不同语言的应用，容器化套路是相通的。

---

## 二、为什么容器里不需要虚拟环境？

这是 Python 开发者容器化时最常问的问题。

### 虚拟环境是干什么的？

在传统开发中，`python -m venv .venv` 创建虚拟环境是为了**隔离不同项目的 Python 依赖**。你的项目 A 需要 `fastapi==0.104.1`，项目 B 需要 `fastapi==0.95.0`，如果装在同一个系统 Python 里，冲突。所以用虚拟环境各玩各的。

### 容器本身就是隔离的

Docker 容器**本身就是最高级别的隔离**。一个容器只有一个应用、一套 Python 解释器、一套依赖。项目 A 的容器和项目 B 的容器完全不共享任何东西。你在容器里 `pip install` 直接装到系统 Python 里，没有任何冲突风险。

**比喻**：

```
虚拟环境 = 合租公寓里隔出的一个小房间（跟别人共享厨房和厕所）
容器     = 你自己的独栋别墅（所有东西都是你的，不跟任何人共享）
```

在独栋别墅里，你不需要再隔一个小房间——整栋别墅都是你的。

### 那为什么很多 Dockerfile 教程里还有 venv？

两种原因：
1. 教程作者习惯使然，没想明白
2. 为了兼容某些特殊场景（比如一个容器里同时跑多个 Python 版本——但这不是推荐做法）

对于 99% 的 Python 容器化场景：**不需要虚拟环境**。直接 `pip install` 到系统 Python 就行了。

---

## 三、Dockerfile：两个版本

### 开发模式 Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# 先拷 requirements.txt，再装依赖（利用层缓存）
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# 再拷源代码
COPY app.py .

EXPOSE 8000

# 开发模式：uvicorn 带 --reload 热重载
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```

逐行解读：

```
FROM python:3.11-slim
    ↓ slim 版本比完整版小很多（~150MB vs ~900MB），推荐日常使用
    ↓ 如果项目需要编译 C 扩展（如 psycopg2），用 python:3.11 完整版
WORKDIR /app
    ↓ 创建并进入 /app
COPY requirements.txt .
    ↓ 先拷依赖清单（变化频率低）
RUN pip install --no-cache-dir -r requirements.txt
    ↓ --no-cache-dir：不缓存 pip 下载的包（减小镜像体积）
COPY app.py .
    ↓ 再拷代码（变化频率高）
EXPOSE 8000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
    ↓ app:app = 文件名:FastAPI 实例变量名
    ↓ --host 0.0.0.0：必须写，不写的话容器内服务只监听 127.0.0.1，外部访问不到
    ↓ --reload：文件变化时自动重启（开发用，生产不要）
```

### ❌ 常见错误：`--host` 没写或写成 `127.0.0.1`

```bash
# ❌ uvicorn 默认只监听 127.0.0.1
CMD ["uvicorn", "app:app", "--port", "8000"]

# 结果：容器内 curl localhost:8000 能通，但宿主机访问不到
```

为什么会这样？`127.0.0.1` 是"只接受本机的连接"。在容器里，来自宿主机的请求是"外部连接"——`127.0.0.1` 会拒绝它。`0.0.0.0` 表示"接受来自任何网络接口的连接"。

```bash
# ✅ 必须写 --host 0.0.0.0
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

这不仅是 uvicorn 的问题，Flask 的 `flask run --host 0.0.0.0`、Django 的 `python manage.py runserver 0.0.0.0:8000` 同理。

### 生产模式 Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

EXPOSE 8000

ENV APP_ENV=production

# 生产模式：不用 --reload，不用开发服务器
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

和生产模式的区别只有两处：
1. 去掉了 `--reload`（生产环境不需要热重载，反而消耗资源）
2. 加了 `ENV APP_ENV=production`

### 如果项目更大？用 Gunicorn

对于生产环境，很多团队用 **Gunicorn** *此术语见附录C*（一个更成熟的 Python WSGI/ASGI 服务器）而不是直接跑 uvicorn。Gunicorn 管理多个 worker 进程，能更好地利用多核 CPU。

用 Gunicorn 的生产 Dockerfile：

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

EXPOSE 8000

ENV APP_ENV=production

# Gunicorn 管理 4 个 uvicorn worker
CMD ["gunicorn", "app:app", \
     "--workers", "4", \
     "--worker-class", "uvicorn.workers.UvicornWorker", \
     "--bind", "0.0.0.0:8000"]
```

对应的 `requirements.txt` 需要加一行：

```
fastapi==0.104.1
uvicorn[standard]==0.24.0
gunicorn==21.2.0
```

### 深入想一下：为什么生产不能用 `flask run` 或 `uvicorn --reload`？

Flask 自带的 `flask run` 和 Django 的 `runserver` 在启动时都会打印一段警告：

```
WARNING: This is a development server. Do not use it in a production deployment.
```

这不是客气话。开发服务器的设计目标是"方便调试"，不是"高性能处理请求"。它：
- 单线程处理请求（一次只能处理一个）
- 不做安全加固
- `--reload` 会持续监控文件系统，消耗 CPU

生产服务器（Gunicorn、uWSGI、直接 uvicorn 无 `--reload`）：
- 多 worker 并行处理
- 经过安全实践考验
- 不监控文件变化

**把开发服务器用在生产环境，就像开着一辆驾校教练车去跑 F1 比赛——它能跑，但不对。**

---

## 四、.dockerignore

```
__pycache__
*.pyc
*.pyo
.pytest_cache
.venv
venv
.env
.git
.gitignore
.DS_Store
```

和 Node.js 的 `node_modules` 一样，Python 的 `__pycache__` 和 `.venv` **绝对不能打包进镜像**：

- `__pycache__`：Python 编译后的字节码缓存，不同 Python 版本不兼容
- `.venv`：宿主机的虚拟环境，里面的包是宿主机的操作系统和 Python 版本编译的，容器里不能用

---

## 五、构建与运行

### 构建

```bash
docker build -t my-python-app .
```

### 开发模式运行

```bash
docker run -d \
  -p 8000:8000 \
  --name python-demo-dev \
  -v "$(pwd)/app.py:/app/app.py" \
  -e APP_ENV=development \
  my-python-app
```

注意：我们只 bind mount 了 `app.py`，不是整个目录。原因和 Node.js 一样——容器里 `pip install` 装的包在 `/usr/local/lib/python3.11/site-packages/`，bind mount 整个目录会把它们覆盖掉。

### 验证

```bash
# 1. 确认容器在跑
docker ps --filter name=python-demo-dev

# 2. 测试根路径
curl http://localhost:8000/
# 预期：{"message":"Hello from FastAPI in Docker!","env":"development"}

# 3. 测试健康检查
curl http://localhost:8000/health
# 预期：{"status":"OK"}

# 4. FastAPI 自带交互式文档
# 浏览器访问：http://localhost:8000/docs
# 预期：看到 Swagger UI 页面，可以直接测试 API
```

### 验证热重载（开发模式）

```bash
# 1. 修改 app.py 里的 message
# 把 "Hello from FastAPI in Docker!" 改成 "Hello from FastAPI! Updated!"

# 2. 保存文件

# 3. 看 uvicorn 日志
docker logs python-demo-dev --tail 3
# 预期看到：WARNING:  WatchFiles detected changes in 'app.py'. Reloading...

# 4. 再次测试
curl http://localhost:8000/
# {"message":"Hello from FastAPI! Updated!","env":"development"}
```

---

## 六、我做得对不对？

### 完整验证流程

```bash
# === 生产模式验证 ===

# 1. 构建镜像
docker build -t my-python-app .
# 检查：无报错

# 2. 运行容器
docker run -d -p 8000:8000 --name python-demo my-python-app
# 检查：返回容器 ID

# 3. 确认容器状态
docker ps --filter name=python-demo
# 检查：STATUS 列显示 "Up"

# 4. 测试健康检查
curl http://localhost:8000/health
# 预期：{"status":"OK"}

# 5. 测试根路径
curl http://localhost:8000/
# 预期：{"message":"Hello from FastAPI in Docker!","env":"production"}

# 6. 停掉生产容器
docker stop python-demo && docker rm python-demo

# === 开发模式验证 ===

# 7. 启动开发模式
docker run -d -p 8000:8000 --name python-demo-dev \
  -v "${PWD}/app.py:/app/app.py" \
  -e APP_ENV=development \
  my-python-app

# 8. 确认开发模式
curl http://localhost:8000/
# 预期：{"message":"Hello from FastAPI in Docker!","env":"development"}

# 9. 清理
docker stop python-demo-dev && docker rm python-demo-dev
```

---

## 七、不对怎么办？

### 常见错误 1：还在容器里 `python -m venv`

```dockerfile
# ❌ 多余操作
FROM python:3.11-slim
WORKDIR /app
RUN python -m venv /opt/venv        # 创建虚拟环境
ENV PATH="/opt/venv/bin:$PATH"      # 激活虚拟环境
COPY requirements.txt .
RUN pip install -r requirements.txt
```

这会多占一层镜像空间（虚拟环境本身要复制一份 Python 标准库），而且没有任何好处。

```dockerfile
# ✅ 直接装到系统 Python
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
```

只有一种情况你需要 venv：你的容器里同时跑多个 Python 应用，且它们需要不同版本的同一个包。但这本身就是反模式——一个容器应该只跑一个应用。

### 常见错误 2：生产用 `flask run` 或 `--reload`

```dockerfile
# ❌ 生产环境
CMD ["flask", "run", "--host", "0.0.0.0"]
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```

`flask run` 是 Flask 内置的开发服务器，单线程、低性能。`--reload` 会持续监控文件系统，白白消耗 CPU。

```dockerfile
# ✅ 生产环境
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
# 或
CMD ["gunicorn", "app:app", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
```

### 常见错误 3：`--host` 没写 —— 容器外访问不到

```bash
docker run -d -p 8000:8000 --name python-demo my-python-app
curl http://localhost:8000/
# curl: (52) Empty reply from server
# 或直接超时
```

❌ 原因：uvicorn 默认只监听 `127.0.0.1`，不接受外部连接。容器的"外部"包括宿主机。

✅ 解决：Dockerfile 的 CMD 里必须写 `--host 0.0.0.0`。

### 常见错误 4：`pip install` 没加 `--no-cache-dir`

```dockerfile
# ❌ 镜像偏大
RUN pip install -r requirements.txt
```

pip 默认会缓存下载的包到 `~/.cache/pip/`。这在容器里是浪费——镜像构建完缓存也不会被清理。

```dockerfile
# ✅ 不缓存，镜像更小
RUN pip install --no-cache-dir -r requirements.txt
```

### 常见错误 5：bind mount 了整个项目，覆盖了 pip 安装的包

```bash
# ❌ 挂载整个目录
docker run -v "$(pwd):/app" ...
```

和 Node.js 的 `node_modules` 问题一模一样。宿主机的目录覆盖了容器里 pip 安装的包。

```bash
# ✅ 只挂载需要热重载的文件
docker run -v "$(pwd)/app.py:/app/app.py" ...
```

如果项目文件多，可以挂载源码目录，但确保不包含虚拟环境目录：

```bash
docker run -v "$(pwd)/src:/app/src" ...
```

---

## 八、完整代码清单

### app.py

```python
import os
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {
        "message": "Hello from FastAPI in Docker!",
        "env": os.getenv("APP_ENV", "development")
    }

@app.get("/health")
def health():
    return {"status": "OK"}
```

### requirements.txt

```
fastapi==0.104.1
uvicorn[standard]==0.24.0
```

### Dockerfile（开发 / 生产双模式注释版）

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# 先拷依赖清单（变化少 → 缓存友好）
COPY requirements.txt .

# 安装依赖（不缓存 pip 下载的包以减小镜像）
RUN pip install --no-cache-dir -r requirements.txt

# 再拷代码（变化频繁）
COPY app.py .

EXPOSE 8000

ENV APP_ENV=production

# 生产模式：uvicorn 不带 --reload
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]

# 开发模式（覆盖 CMD）：
# docker run ... my-python-app uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

### .dockerignore

```
__pycache__
*.pyc
*.pyo
.pytest_cache
.venv
venv
.env
.git
.gitignore
.DS_Store
```

---

## 本章小结

| 本章学了什么 | 对应命令/概念 | 注意事项 |
|-------------|-------------|---------|
| Python 应用容器化完整流程 | `docker build -t my-python-app .` | 流程和 Node.js 几乎一样，语言特定细节不同 |
| 容器里不需要虚拟环境 | 直接 `pip install` 到系统 Python | 容器本身就是隔离的，venv 是多余的 |
| `--host 0.0.0.0` | uvicorn / gunicorn / flask run 都要加 | 不加的话容器外访问不到 |
| 开发 vs 生产服务器 | dev: `--reload` 热重载；prod: 无 `--reload` 或用 Gunicorn | 开发服务器不能用于生产 |
| `.dockerignore` | 忽略 `__pycache__`、`.venv`、`*.pyc` | 编译产物和虚拟环境不能打包进镜像 |
| 层缓存优化 | `COPY requirements.txt` → `RUN pip install` → `COPY app.py` | 依赖清单变化少，放前面 |
| `--no-cache-dir` | `pip install --no-cache-dir` | 减小镜像体积 |
| Bind mount 开发模式 | `-v "$(pwd)/app.py:/app/app.py"` | 只挂代码文件，不覆盖 pip 安装的包 |

---

## 本篇最可能出错的地方及原因

### 1. `--host 0.0.0.0` 忘写，容器外访问不到（最高频）

**这是 Python 容器化最经典的错误。** 在宿主机上开发时，你跑 `uvicorn app:app --port 8000`，然后 `curl localhost:8000` 能通——因为服务器和客户端在同一台机器上。但到了容器里，宿主机对容器来说是"外部机器"，`127.0.0.1` 的监听范围到不了外部。

**所有 Python Web 框架都有这个问题**：FastAPI 的 uvicorn、Flask 的 `flask run`、Django 的 `runserver`，默认都只监听 `127.0.0.1`。必须显式加 `--host 0.0.0.0`。

**排查**：`docker exec python-demo curl localhost:8000/health`——如果容器内能通，容器外不通，99% 是 `--host` 的问题。

### 2. 在容器里创建虚拟环境

这是一个"惯性思维"导致的错误。很多 Python 开发者学了 venv 后，写 Dockerfile 时条件反射地加 `python -m venv`。这不会导致功能出错，但会让镜像多一层、多几十 MB，而且让 Dockerfile 看起来复杂。

**要纠正的观念**：虚拟环境是"多项目共享一个 Python 解释器"时的解决方案。容器里只有一个项目，所以不需要。确实有些公司（如 Google 的某些 Python 容器实践）仍然在容器里用 venv，但那是因为他们有一套统一的 venv 路径约定，方便 CI/CD 工具链集成。对个人项目和小团队来说，不需要。

### 3. 生产环境用 `flask run` 或 `--reload`

Flask 的 `flask run` 和 uvicorn 的 `--reload` 都是开发工具。`flask run` 启动时甚至会打印警告："WARNING: This is a development server." 但很多人选择性忽略。

**后果**：`flask run` 是单线程的，同时只能处理一个请求。如果两个用户同时访问，第二个要排队等第一个处理完。并发一上去，服务就崩溃。

**正确做法**：生产用 Gunicorn + UvicornWorker（生产环境标准配置），或者至少用 uvicorn 但不带 `--reload`。

### 4. Bind mount 覆盖了 pip 安装的包

和 Node.js 的 `node_modules` 问题同源。`-v $(pwd):/app` 把宿主机目录挂到容器 `/app`，pip 装在 `/usr/local/lib/python3.11/site-packages/` 里的包不受影响，但如果你用 `RUN pip install --target /app/deps` 或用了虚拟环境，就可能被覆盖。

**安全做法**：只挂载需要热重载的源码文件/目录，不挂整个项目根目录。