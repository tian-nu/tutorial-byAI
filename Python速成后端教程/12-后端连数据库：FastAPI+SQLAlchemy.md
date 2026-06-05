# 12-后端连数据库：FastAPI + SQLAlchemy

- 对应文档版本：首版教程
- 适用环境：Python 3.10+, FastAPI 0.100+, SQLAlchemy 2.0+, Windows/macOS/Linux
- 读者角色：后端初学者
- 预计耗时：新手 70 分钟 / 熟手 30 分钟
- 前置教程：[07-第一个接口实战：博客文章 CRUD（内存版）](./07-第一个接口实战：博客文章CRUD内存版.md)
- 可视化：无

---

## 一、目标与完成效果

**一句话目标**：把教程 07 的"内存版"博客升级为"数据库版"——用 SQLAlchemy ORM 代替 Python 列表，让数据真正存到硬盘上，重启服务器也不会丢。

**完成后的可观测效果**：
- 你新建了 `database.py` 和 `models.py` 两个文件，代码量不超过 80 行，但你的博客从此有了"永久记忆"。
- 你启动服务器后，SQLite 数据库文件 `blog.db` 自动出现在项目目录里。
- 你用 curl 创建一篇文章，关掉服务器再启动，那篇文章还在——不丢数据了。
- 你打开 `blog.db` 文件（用 DB Browser 或命令行），能亲眼看到数据库里真的存着你创建的文章。
- 你理解了 ORM 是什么——"翻译官"比喻能让你跟完全不懂编程的朋友讲清楚。

---

## 二、前置条件

| 序号 | 条件 | 验证命令 |
|------|------|----------|
| 1 | 已完成教程 07，`blog_backend/main.py` 和 `blog_backend/schemas.py` 存在 | `dir blog_backend`（Windows）或 `ls blog_backend/` |
| 2 | Python 虚拟环境已激活 | 终端前面有 `(venv)` 字样 |
| 3 | FastAPI 已安装 | `pip show fastapi` |
| 4 | 理解 CRUD 五个接口的逻辑（教程 07 的内容） | 能说出 `GET /posts`、`POST /posts`、`GET /posts/{id}`、`PUT /posts/{id}`、`DELETE /posts/{id}` 分别做什么 |

**一条命令确认前置满足**：

```powershell
# Windows PowerShell
pip show fastapi; dir blog_backend
```

如果 `fastapi` 版本信息正常显示，且 `blog_backend/` 目录下有 `main.py` 和 `schemas.py`，前置条件满足。

---

## 三、分步操作

### 步骤 0：为什么需要数据库？——"便签纸" vs "刻石碑"

在教程 07 中，我们用 Python 列表 `posts_db = []` 来存文章。能跑，但有一个致命问题：**重启服务器，数据全丢。**

这就像你在便签纸上记账——纸在，账在；纸扔了，账没了。而数据库就像把账刻在石碑上，服务器重启了、电脑关机了，石碑还在，账就在。

**但这里有一个两难问题：直接操作数据库需要写 SQL 语句。**

比如你想查所有文章，要写：

```sql
SELECT * FROM posts;
```

创建一篇文章，要写：

```sql
INSERT INTO posts (title, content, published) VALUES ('我的文章', '正文内容', 1);
```

更新一篇文章，要写：

```sql
UPDATE posts SET title = '新标题' WHERE id = 2;
```

**SQL 是另一门语言。** 你刚学会 Python 和 FastAPI，现在又要学 SQL？这就像你刚学会骑自行车，教练就让你去开飞机——两种完全不同的操作方式，同时学会让你崩溃。

**所以我们需要一个"翻译官"——ORM。**

---

### 步骤 1：ORM 是什么？——"翻译官"比喻

**ORM** 全称 **Object-Relational Mapping**（对象关系映射），名字很唬人，但核心思想很简单：

> **你用 Python 对象说话，ORM 帮你翻译成 SQL。**

打个比方：

你是一个只说中文的老板（Python 代码），你要跟一个只说英文的供应商（数据库）做生意。你不会英文，供应商不会中文。你们需要一个翻译官——**ORM 就是这个翻译官。**

```
你（Python 代码）                  翻译官（ORM）                  供应商（数据库）
    │                                   │                            │
    │——"我要所有文章"                    │                            │
    │  (posts = session.query(Post).all())                           │
    │                                   │——"SELECT * FROM posts"     │
    │                                   │                          → │
    │                                   │                   （查表）  │
    │                                   │           ← 返回结果       │
    │                                   │                            │
    │←—— 返回 Python 对象列表            │                            │
    │     [Post(title="..."), Post(title="...")]                     │
```

**你不需要写一行 SQL。** 你只需要操作 Python 对象——创建 `Post` 对象、查询 `Post` 对象、修改 `Post` 对象的属性、删除 `Post` 对象。ORM 自动帮你把这些操作翻译成对应的 SQL 语句。

**SQLAlchemy** 就是 Python 世界里最流行的 ORM 翻译官。此术语需进附录。

---

### 步骤 2：安装依赖

打开终端，确保虚拟环境已激活（终端前面有 `(venv)` 字样），执行：

```bash
pip install sqlalchemy
```

**验证安装**：

```bash
pip show sqlalchemy
```

你应该看到类似输出：

```
Name: SQLAlchemy
Version: 2.0.x
Summary: Database Abstraction Library
```

如果看到版本号，安装成功。

> **不需要单独安装 SQLite 驱动。** SQLAlchemy 自带 SQLite 支持（Python 标准库内置了 `sqlite3` 模块），只要你用的是 Python 3.x，不需要额外安装任何数据库软件。

---

### 步骤 3：配置数据库连接——告诉翻译官"供应商"在哪

现在我们要新建一个文件，专门负责数据库的连接和配置。在 `blog_backend/` 目录下新建 `database.py`。

**我在做什么？** 创建一个"通信中心"，它负责：① 告诉 SQLAlchemy 数据库在哪；② 创建数据库连接池；③ 提供"每次请求拿一个数据库会话"的机制。

**代码**（`blog_backend/database.py` 完整版）：

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

# === 1. 数据库地址 ===
DATABASE_URL = "sqlite:///./blog.db"

# === 2. 创建引擎 ===
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # SQLite 专用配置
    echo=True,  # 开发时打开 SQL 日志，上线后关掉
)

# === 3. 创建会话工厂 ===
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# === 4. 创建基类 ===
class Base(DeclarativeBase):
    pass
```

**逐行解释**：

**1. `DATABASE_URL = "sqlite:///./blog.db"`**

这是数据库的"地址"。拆开看：

| 部分 | 值 | 含义 |
|------|-----|------|
| `sqlite` | 数据库类型 | 用 SQLite（一个零配置的轻量数据库，数据存在一个文件里） |
| `///` | 分隔符 | SQLite 专用格式，表示"本地文件" |
| `./blog.db` | 文件路径 | 在当前目录下创建 `blog.db` 文件来存数据 |

**比喻**：`DATABASE_URL` 就是供应商的地址。`sqlite:///./blog.db` 的意思是："供应商在本地，他的仓库是一个叫 `blog.db` 的文件。"

> ⚠️ **SQLite 的 URL 格式有三个斜杠**（`///`）。这是最容易写错的地方——多一个少一个都会报错。MySQL 和 PostgreSQL 用的是 `://`（两个斜杠），但 SQLite 是 `:///`（三个斜杠）。这个坑我们后面会专门讲。

**2. `engine = create_engine(...)`**

**engine**（引擎）是 SQLAlchemy 的核心——它负责跟数据库建立连接、执行 SQL、管理连接池。此术语需进附录。

**比喻**：engine 就是翻译官手里的"电话"。翻译官通过这通电话联系供应商。没有电话，翻译官就没法工作。

参数说明：
- `connect_args={"check_same_thread": False}`：这是 SQLite 特有的配置。默认情况下 SQLite 不允许跨线程使用同一个连接，但 FastAPI 的请求处理可能涉及多个线程，所以需要关掉这个检查。**如果你用的是 MySQL 或 PostgreSQL，这行不需要。**
- `echo=True`：打开 SQL 日志。开发时这个非常重要——你会看到每一句实际执行的 SQL 语句，方便调试。**上线后必须关掉**（改成 `echo=False`），否则日志会爆。

**3. `SessionLocal = sessionmaker(...)`**

**Session**（会话）是 SQLAlchemy 中和数据库交互的"工作单元"。你每次要查数据、存数据、改数据，都需要通过一个 Session 来进行。此术语需进附录。

**比喻**：Session 就是翻译官每次"出任务"时的临时工位。每次有客户（HTTP 请求）来访，翻译官就开一个临时工位（Session），在这个工位上完成所有翻译工作，任务结束后工位就撤了。

参数说明：
- `autocommit=False`：不自动提交事务。需要你手动调用 `session.commit()` 才会真正写入数据库。这给了你"后悔"的机会——如果中间出错了，可以回滚。
- `autoflush=False`：不自动刷新。`flush` 是把 pending 的 SQL 语句发到数据库但不提交。我们手动控制。
- `bind=engine`：把会话工厂绑定到我们创建的引擎上——告诉它"你的电话就是这一部"。

**4. `class Base(DeclarativeBase): pass`**

`Base` 是所有 ORM 模型的"基类"（父类）。你后面定义的每个数据库表模型（比如 `Post`、`User`）都要继承自它。

**比喻**：`Base` 就像翻译官手里的一叠空白表格模板。每种表格（`Post` 表、`User` 表）都从这叠模板里拿一张空白的，然后填上自己的字段。

---

### 步骤 4：理解 `get_db` 依赖注入——每次请求一个"临时工位"

在 `database.py` 末尾，我们需要再加一个函数——`get_db`。它是 FastAPI 的**依赖注入**机制的核心组件。

**追加到 `blog_backend/database.py` 末尾**：

```python
# === 5. 依赖注入：每次请求创建一个新的数据库会话 ===
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

**逐行解释**：

- `db = SessionLocal()`：创建一个新的数据库会话（翻译官开了一个临时工位）。
- `yield db`：把会话交给 FastAPI 的接口函数使用。`yield` 是 Python 的生成器语法——你可以暂时理解为"把 `db` 交出去，等接口函数用完再收回来"。
- `finally: db.close()`：**无论接口函数执行成功还是失败**，最终都会关闭这个会话（翻译官收拾工位，把电话挂断）。

**比喻**：`get_db` 就像一个"工位管理员"。每次有客人来（HTTP 请求），管理员说："翻译官，第 3 号工位给你用。"翻译官干完活后，管理员把工位收拾干净，准备迎接下一个客人。

**为什么每次请求都要新建一个会话？** 因为在多用户环境下，多个请求同时进来，如果大家共享一个会话，数据会互相干扰。就像多个客人同时找同一个翻译官，翻译官会搞混谁是谁的。每个请求一个独立的会话，互不干扰。

> **依赖注入**（Dependency Injection）是 FastAPI 的一个核心特性。此术语需进附录。简单说就是：接口函数声明"我需要一个数据库会话"，FastAPI 自动把 `get_db()` 产出的会话传进去。我们在教程 08 中已经学过这个概念，这里第一次实际应用。

---

### 步骤 5：定义 ORM 模型——"刻石碑"的模板

现在我们要定义数据库表的结构。在 `blog_backend/` 目录下新建 `models.py`。

**我在做什么？** 用 Python 类来定义数据库表——每个类对应一张表，每个属性对应一个列。这就像你画了一张"石碑雕刻模板"，SQLAlchemy 按这个模板去刻真正的石碑（在数据库里建表）。

**代码**（`blog_backend/models.py` 完整版）：

```python
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from blog_backend.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # 关系：一个用户有多篇文章
    posts = relationship("Post", back_populates="author")


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    content = Column(String, nullable=False)
    published = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 外键：每篇文章属于一个用户
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # 关系：文章属于一个用户
    author = relationship("User", back_populates="posts")


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(String(500), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # 外键：每条评论属于一篇文章，属于一个用户
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # 关系
    post = relationship("Post", backref="comments")
    author = relationship("User", backref="comments")
```

**逐行解释**：

---

#### 5.1 `__tablename__` —— 你给表起的名字

```python
class Post(Base):
    __tablename__ = "posts"
```

`__tablename__` 告诉 SQLAlchemy："这个 Python 类对应的数据库表名叫 `posts`。"类名是 `Post`（单数，首字母大写），表名是 `posts`（复数，全小写）。这是约定俗成的命名习惯。

**比喻**：`Post` 类是你画的"石碑模板"，`__tablename__ = "posts"` 是你给石碑起的标题——"这块石碑叫'文章表'"。

---

#### 5.2 `Column` —— 表里的每一列

```python
id = Column(Integer, primary_key=True, index=True)
```

| 参数 | 含义 | 比喻 |
|------|------|------|
| `Integer` | 这一列存整数 | 石碑上刻数字的格子 |
| `primary_key=True` | 这是主键（唯一标识每一行） | 每块石碑的唯一编号，绝不重复 |
| `index=True` | 给这一列建索引（加速查询） | 给石碑编号做目录，翻找更快 |

```python
title = Column(String(200), nullable=False)
```

| 参数 | 含义 | 比喻 |
|------|------|------|
| `String(200)` | 这一列存字符串，最多 200 个字符 | 石碑上刻文字的格子，最长 200 字 |
| `nullable=False` | 不允许为空（必填） | 这块格子必须刻字，不能空着 |

```python
created_at = Column(DateTime, default=datetime.utcnow)
```

| 参数 | 含义 | 比喻 |
|------|------|------|
| `DateTime` | 这一列存日期时间 | 石碑上刻日期的格子 |
| `default=datetime.utcnow` | 默认值是当前时间 | 如果你不写日期，自动刻上今天的日期 |

**`Column` 常用类型速查表**：

| SQLAlchemy 类型 | Python 对应类型 | 数据库存储 |
|-----------------|----------------|-----------|
| `Integer` | `int` | 整数 |
| `String(n)` | `str` | 字符串，最多 n 个字符 |
| `Boolean` | `bool` | 布尔值（True/False） |
| `DateTime` | `datetime` | 日期时间 |
| `Text` | `str` | 长文本（不限长度） |
| `Float` | `float` | 浮点数 |
| `ForeignKey("表名.列名")` | — | 外键，指向另一张表的主键 |

---

#### 5.3 `ForeignKey` —— 表和表之间的"关联线"

```python
user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
```

**外键**（Foreign Key）是数据库里连接两张表的"纽带"。这行代码的意思是："`posts` 表的 `user_id` 列，指向 `users` 表的 `id` 列。"

**比喻**：一张文章石碑上刻着"作者编号：3"，你要查作者是谁，就拿着"3"去 `users` 表翻编号为 3 的那条记录。这个"作者编号"就是外键——它建立了文章和作者之间的关联。

此术语需进附录。

---

#### 5.4 `relationship` —— 让 Python 对象之间也能"导航"

```python
# 在 Post 类中
author = relationship("User", back_populates="posts")
```

这行代码不改变数据库表结构（不会在 `posts` 表里加列），它只影响 Python 对象的行为。它的作用是：**当你拿到一个 `Post` 对象时，可以通过 `.author` 直接拿到对应的 `User` 对象。**

**比喻**：`ForeignKey` 是石碑上刻的"作者编号：3"，`relationship` 是翻译官的一个"自动导航"功能——你只需要问"这篇文章的作者是谁？"，翻译官就自动拿着编号 3 去 `users` 表把作者找出来，塞到你手里。

**`back_populates` 是什么？** 此术语需进附录。

```python
# 在 User 类中
posts = relationship("Post", back_populates="author")
```

`back_populates="author"` 的意思是："对方（User 类）的 `posts` 属性和我方（Post 类）的 `author` 属性是一对，互相呼应。"

**效果**：建立双向导航。

```python
# 正向：从文章找到作者
post = session.query(Post).first()
print(post.author.username)  # 输出：文章作者的用户名

# 反向：从作者找到他的所有文章
user = session.query(User).first()
print(user.posts)  # 输出：[Post(title="文章1"), Post(title="文章2"), ...]
```

**`back_populates` 写错是初学者最容易犯的错误之一。** 两个类里的字符串必须**互相匹配**，就像两个对讲机的频道，必须调到同一个频率才能通话。

---

### 步骤 6：自动建表——一键把"模板"刻成"石碑"

现在模板画好了，我们要让 SQLAlchemy 按模板在数据库里建表。

**修改 `blog_backend/main.py`**，在文件开头（`app = FastAPI()` 之后，路由定义之前）加入自动建表逻辑：

```python
from fastapi import FastAPI, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from blog_backend.schemas import BlogCreate
from blog_backend.database import engine, get_db, Base
from blog_backend import models  # 导入 models 以注册所有 ORM 模型

app = FastAPI()

# === 自动建表 ===
Base.metadata.create_all(bind=engine)
```

**逐行解释**：

- `from blog_backend import models`：导入 `models.py`。看起来好像没用到，但这一步**必须做**——因为只有导入 `models` 模块后，SQLAlchemy 才知道 `Post`、`User`、`Comment` 这些类存在。如果不导入，`create_all` 会创建零张表。
- `Base.metadata.create_all(bind=engine)`：`Base.metadata` 是所有注册过的 ORM 模型的"元数据集合"（可以理解为"所有模板的目录"）。`create_all(bind=engine)` 的意思是："按目录上列出的所有模板，在 `engine` 连接的数据库里建表。"

**比喻**：`Base.metadata` = 翻译官手里的一叠设计图纸（所有表模板），`create_all(bind=engine)` = 翻译官对供应商说："按图纸，把这些石碑都刻出来。"

**关键行为**：
- 如果表不存在 → 创建表。
- 如果表已存在 → **什么都不做**（不会删表重建，不会丢数据）。
- 也就是说，第一次启动服务器时建表，之后每次启动都是"检查过了，表在，跳过"。

---

### 步骤 7：启动服务器，验证建表

**我在做什么？** 启动服务器，观察 `create_all` 是否自动建表，以及 SQL 日志输出。

**第 1 步**：启动服务器：

```bash
uvicorn blog_backend.main:app --reload
```

**第 2 步**：观察终端输出。因为我们在 `database.py` 里设置了 `echo=True`，你会看到类似这样的 SQL 日志：

```
CREATE TABLE users (
    id INTEGER NOT NULL,
    username VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL,
    created_at DATETIME,
    PRIMARY KEY (id),
    UNIQUE (username),
    UNIQUE (email)
)

CREATE TABLE posts (
    id INTEGER NOT NULL,
    title VARCHAR(200) NOT NULL,
    content VARCHAR NOT NULL,
    published BOOLEAN,
    created_at DATETIME,
    updated_at DATETIME,
    user_id INTEGER NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY(user_id) REFERENCES users (id)
)

CREATE TABLE comments (
    ...
)
```

**这些就是 ORM 帮你翻译出来的 SQL 语句！** 你写了 Python 类，ORM 帮你翻译成了 `CREATE TABLE` 语句，发给数据库执行。

**第 3 步**：检查项目目录。在 `blog_backend/` 同级目录下，应该出现了一个 `blog.db` 文件：

```powershell
dir blog.db
```

这就是 SQLite 数据库文件——你的数据就存在这个文件里。把它复制到另一台电脑上，数据就跟着过去了。

**第 4 步**：再次重启服务器，观察差异。按 `Ctrl+C` 停止，再启动：

```bash
uvicorn blog_backend.main:app --reload
```

这次终端**不会再有 `CREATE TABLE` 的日志**——因为表已经存在了，`create_all` 自动跳过。

---

### 步骤 8：改造接口——从"操作列表"到"操作数据库"

现在我们有了数据库，要把教程 07 里的五个接口从"操作 Python 列表"改成"操作数据库"。所有改动都在 `blog_backend/main.py` 里。

**关键变化一览**：

| 教程 07（内存版） | 本章（数据库版） |
|-------------------|-----------------|
| `posts_db: list[dict] = []` | 通过 `get_db` 获取 `Session` |
| `posts_db.append(new_post)` | `db.add(new_post)` + `db.commit()` |
| `for post in posts_db:` | `db.query(Post).all()` 或 `db.query(Post).filter(...)` |
| `posts_db[i] = {...}` | 修改对象属性 + `db.commit()` |
| `posts_db.pop(i)` | `db.delete(post)` + `db.commit()` |

下面逐个改造。

---

#### 接口 1：`GET /posts` —— 获取全部文章

**内存版（旧）**：

```python
@app.get("/posts")
def get_all_posts():
    return posts_db
```

**数据库版（新）**：

```python
@app.get("/posts")
def get_all_posts(db: Session = Depends(get_db)):
    posts = db.query(models.Post).all()
    return posts
```

**逐行解释**：

- `db: Session = Depends(get_db)`：**依赖注入**。FastAPI 看到这个参数声明，就会自动调用 `get_db()` 函数，把产出的数据库会话传进来。你在接口函数里直接用 `db` 就行。
- `db.query(models.Post)`：告诉数据库"我要查询 `posts` 表"。`models.Post` 是我们刚才定义的 ORM 模型类。
- `.all()`：获取所有结果，返回一个 Python 列表，里面是 `Post` 对象。

**比喻**：`db.query(models.Post).all()` = 翻译官对供应商说："把 `posts` 石碑上所有记录都给我抄一份。"供应商抄完，翻译官把抄件（Python 对象列表）交给你。

---

#### 接口 2：`POST /posts` —— 创建文章

**内存版（旧）**：

```python
@app.post("/posts")
def create_post(blog: BlogCreate):
    new_id = len(posts_db) + 1
    new_post = {
        "id": new_id,
        "title": blog.title,
        "content": blog.content,
        "published": blog.published,
    }
    posts_db.append(new_post)
    return new_post
```

**数据库版（新）**：

```python
@app.post("/posts", status_code=201)
def create_post(blog: BlogCreate, db: Session = Depends(get_db)):
    # 创建 ORM 对象（不是字典！）
    new_post = models.Post(
        title=blog.title,
        content=blog.content,
        published=blog.published,
        user_id=1,  # 暂时硬编码为 user_id=1，后续教程会处理用户认证
    )
    db.add(new_post)      # 加入待办清单
    db.commit()           # 真正写入数据库
    db.refresh(new_post)  # 刷新以获取数据库生成的 id
    return new_post
```

**逐行解释**：

- `new_post = models.Post(...)`：创建一个 `Post` 类的实例（Python 对象），而不是字典。这是 ORM 和内存版最本质的区别——你操作的是**对象**，不是**字典**。
- `user_id=1`：暂时硬编码。因为我们现在还没有用户登录功能，先假设所有文章都属于 ID 为 1 的用户。后续教程会处理用户认证后，这个值会从当前登录用户获取。
- `db.add(new_post)`：把新文章对象加入"待办清单"（pending）。此时 SQL 还没发出去。
- `db.commit()`：**把待办清单上的所有操作一次性发送到数据库并永久保存。** 这是最关键的一行——忘了它，数据不会写入数据库。此术语需进附录。
- `db.refresh(new_post)`：刷新对象，获取数据库自动生成的字段（比如 `id`、`created_at`）。因为 `id` 是数据库自动生成的，`commit()` 之前 `new_post.id` 是 `None`，`refresh()` 之后就有了。

**比喻**：
- `db.add(new_post)` = 翻译官在便签纸上写"待办：把这块新石碑放进仓库"。
- `db.commit()` = 翻译官真的搬起石碑放进仓库，归档。
- `db.refresh(new_post)` = 翻译官查一下仓库管理系统，确认石碑编号、入库时间，回来告诉你。

---

#### 接口 3：`GET /posts/{post_id}` —— 获取单篇文章

**数据库版**：

```python
@app.get("/posts/{post_id}")
def get_post(post_id: int, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if post is None:
        return JSONResponse(
            status_code=404,
            content={"error": f"文章 #{post_id} 不存在"}
        )
    return post
```

**逐行解释**：

- `db.query(models.Post)`：查询 `posts` 表。
- `.filter(models.Post.id == post_id)`：筛选条件——"id 等于 `post_id` 的行"。注意这里用的是 `==`（Python 比较运算符），不是 `=`（SQL 赋值），ORM 会帮你翻译成 SQL 的 `WHERE id = ?`。
- `.first()`：返回第一条匹配结果。如果没有匹配的，返回 `None`。
- `if post is None:`：没找到就返回 404。

**对比内存版**：内存版用 `for` 循环遍历列表找文章，数据库版用 `.filter(...).first()` 一条语句搞定。数据库有索引，即使有百万篇文章也能瞬间找到。

---

#### 接口 4：`PUT /posts/{post_id}` —— 更新文章

**数据库版**：

```python
@app.put("/posts/{post_id}")
def update_post(post_id: int, blog: BlogCreate, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if post is None:
        return JSONResponse(
            status_code=404,
            content={"error": f"文章 #{post_id} 不存在，无法更新"}
        )

    # 修改对象属性
    post.title = blog.title
    post.content = blog.content
    post.published = blog.published

    db.commit()      # 提交修改
    db.refresh(post) # 刷新以获取 updated_at
    return post
```

**注意**：这里**没有** `db.add(post)`。因为 `post` 是从数据库查出来的，它已经在 SQLAlchemy 的"追踪范围"内。你修改它的属性，SQLAlchemy 自动检测到变化，`commit()` 时自动生成 `UPDATE` 语句。

**比喻**：翻译官从仓库里搬出一块石碑（`query`），你用粉笔在上面改了几个字，翻译官看到变化了，`commit()` 时就把石碑搬回去，旧石碑替换成新的。

---

#### 接口 5：`DELETE /posts/{post_id}` —— 删除文章

**数据库版**：

```python
@app.delete("/posts/{post_id}")
def delete_post(post_id: int, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if post is None:
        return JSONResponse(
            status_code=404,
            content={"error": f"文章 #{post_id} 不存在，无法删除"}
        )

    title = post.title  # 删除前先保存标题，用于响应消息
    db.delete(post)
    db.commit()
    return {"message": f"文章 #{post_id}「{title}」已删除"}
```

**逐行解释**：

- `title = post.title`：在删除前保存标题，因为 `db.delete(post)` 之后，对象的属性可能不可用。
- `db.delete(post)`：标记这个对象为"待删除"。
- `db.commit()`：真正执行删除。

---

### 步骤 9：阶段性验证——用 curl 把五个接口全部跑一遍

现在你的 `main.py` 应该已经改造完成。让我们从头到尾走一遍完整流程，验证数据真的存到了数据库里。

> **建议**：在开始之前，先重启服务器（`Ctrl+C` 停止，重新 `uvicorn blog_backend.main:app --reload`），清空之前的测试数据。

**第 1 步：创建三篇文章**

```bash
curl -X POST http://127.0.0.1:8000/posts -H "Content-Type: application/json" -d '{"title": "FastAPI 入门", "content": "今天开始学 FastAPI。", "published": true}'
curl -X POST http://127.0.0.1:8000/posts -H "Content-Type: application/json" -d '{"title": "Python 技巧", "content": "列表推导式真好用。", "published": false}'
curl -X POST http://127.0.0.1:8000/posts -H "Content-Type: application/json" -d '{"title": "部署笔记", "content": "Docker 部署步骤记录。", "published": false}'
```

**第 2 步：获取全部文章，确认三篇都在**

```bash
curl http://127.0.0.1:8000/posts
```

你应该看到 3 篇文章，每篇都有 `id`、`created_at` 等数据库自动生成的字段。

**第 3 步：获取单篇文章**

```bash
curl http://127.0.0.1:8000/posts/2
```

**第 4 步：更新文章 2**

```bash
curl -X PUT http://127.0.0.1:8000/posts/2 -H "Content-Type: application/json" -d '{"title": "Python 进阶技巧", "content": "列表推导式、生成器、装饰器。", "published": true}'
```

**第 5 步：验证更新**

```bash
curl http://127.0.0.1:8000/posts/2
```

标题应该变成 `"Python 进阶技巧"`。

**第 6 步：删除文章 3**

```bash
curl -X DELETE http://127.0.0.1:8000/posts/3
```

**第 7 步：验证删除**

```bash
curl http://127.0.0.1:8000/posts/3
```

应该返回 404。

**第 8 步：重启服务器**

`Ctrl+C` 停止，重新启动：

```bash
uvicorn blog_backend.main:app --reload
```

**第 9 步：再次获取全部文章**

```bash
curl http://127.0.0.1:8000/posts
```

**你应该看到 ID 1 和 ID 2 两篇文章还在！** 这就是数据库版和内存版最本质的区别——数据持久化了，重启不会丢。

---

### 🤔 想多一点：为什么教程 07 和教程 12 的接口代码结构几乎一样？

你可能会注意到，改造后的接口代码和内存版非常相似：

| 操作 | 内存版 | 数据库版 |
|------|--------|----------|
| 创建 | 构造字典 → `posts_db.append()` | 构造对象 → `db.add()` → `db.commit()` |
| 查询全部 | `return posts_db` | `db.query(Post).all()` → `return` |
| 查询单个 | `for` 循环遍历 | `.filter(...).first()` |
| 更新 | 修改字典 → `posts_db[i] = ...` | 修改对象属性 → `db.commit()` |
| 删除 | `posts_db.pop(i)` | `db.delete(post)` → `db.commit()` |

**这不是巧合，这正是教程 07 设计的初衷。** 我们在教程 07 中说过：

> "先学会'接口长什么样'，再学会'数据怎么存'。等接口逻辑烂熟于心后，再学数据库，你只需要关注'数据怎么存'这一个新东西。"

**现在你看到了这个策略的成果：** 五个接口的"形状"（路由、参数、响应格式）完全没变，你只需要把"数据操作"部分从列表操作换成数据库操作。如果你一开始就学数据库，你会同时面对"接口怎么设计"和"数据库怎么操作"两个新问题，报错时完全不知道是哪边出了问题。

**这就是"分两步走"的力量。** 你不是在学两件东西，而是在一件已学会的东西上"加装"一个新能力。

---

### 步骤 10：SQLAlchemy vs 原生 SQL —— 同一操作，两套写法

为了让你更直观地感受 ORM 的价值，我们来做一个对比——同样的操作，用 SQLAlchemy（ORM）和原生 SQL 分别怎么写。

> **原生 SQL 的意思**：直接写 SQL 字符串发给数据库，不经过 ORM 翻译。Python 标准库 `sqlite3` 就支持这种写法。

| 操作 | SQLAlchemy（ORM） | 原生 SQL |
|------|-------------------|----------|
| 查询全部文章 | `db.query(Post).all()` | `SELECT * FROM posts` |
| 按 ID 查询 | `db.query(Post).filter(Post.id == 1).first()` | `SELECT * FROM posts WHERE id = 1` |
| 创建文章 | `db.add(Post(title="..."))` → `db.commit()` | `INSERT INTO posts (title, content) VALUES ('...', '...')` |
| 更新文章 | `post.title = "新标题"` → `db.commit()` | `UPDATE posts SET title = '新标题' WHERE id = 1` |
| 删除文章 | `db.delete(post)` → `db.commit()` | `DELETE FROM posts WHERE id = 1` |

**ORM 的三个核心优势**：

1. **不用写 SQL 字符串。** SQL 字符串很容易出错——少一个引号、多一个逗号，整个语句就炸了。ORM 用 Python 方法调用代替字符串拼接，IDE 可以帮你自动补全和检查语法。

2. **防 SQL 注入。** 如果你用字符串拼接 SQL（比如 `f"SELECT * FROM posts WHERE title = '{user_input}'"`），恶意用户可以在输入里塞 SQL 代码来攻击你的数据库。ORM 自动使用参数化查询，从根本上杜绝了这个问题。

3. **数据库无关性。** 如果你以后想把数据库从 SQLite 换成 MySQL 或 PostgreSQL，用 ORM 只需要改一行 `DATABASE_URL`，代码不用动。如果用原生 SQL，SQLite 和 MySQL 的 SQL 语法有差异，你需要改很多地方。

---

### ❌ 常见错误 → ✅ 正确示例

> **错误 1：忘记 `session.commit()` —— 数据没存进去**

这是初学者最容易犯的错误，没有之一。

❌ 错误示例：

```python
@app.post("/posts")
def create_post(blog: BlogCreate, db: Session = Depends(get_db)):
    new_post = models.Post(title=blog.title, content=blog.content, user_id=1)
    db.add(new_post)
    # 忘了 db.commit()！
    return new_post
```

**现象**：curl 返回了创建的文章（看起来成功了），但 `GET /posts` 查不到，重启服务器后更不可能有。

**为什么？** `db.add()` 只是把操作加入"待办清单"，`db.commit()` 才真正写入数据库。没有 `commit()`，待办清单在请求结束后就扔了，数据根本没进数据库。

**怎么发现？** 观察终端日志。如果没有 `commit()`，你看不到 `INSERT INTO posts ...` 的 SQL 日志输出。

✅ 正确示例：

```python
@app.post("/posts")
def create_post(blog: BlogCreate, db: Session = Depends(get_db)):
    new_post = models.Post(title=blog.title, content=blog.content, user_id=1)
    db.add(new_post)
    db.commit()      # ← 必须 commit
    db.refresh(new_post)
    return new_post
```

**记忆口诀**：`add` 是"说要写"，`commit` 是"真的写"。说一百遍不如做一遍。

---

> **错误 2：session 在多线程中共享 —— 数据错乱**

❌ 错误示例：

```python
# 在模块级别创建全局 session
db = SessionLocal()

@app.get("/posts")
def get_all_posts():
    return db.query(models.Post).all()  # 所有请求共享同一个 session！
```

**现象**：偶尔数据错乱、偶尔报错、偶尔正常——非常诡异的间歇性 bug。

**为什么？** FastAPI 是异步框架，多个请求可能同时处理。如果它们共享一个 session，当一个请求在修改数据时，另一个请求也在修改，两个操作互相干扰。就像两个人同时在一张纸上写字，最后谁也看不清写了什么。

✅ 正确示例：

```python
# 用 get_db 依赖注入，每次请求创建一个新 session
@app.get("/posts")
def get_all_posts(db: Session = Depends(get_db)):
    return db.query(models.Post).all()
```

**每一个请求一个独立的 session，互不干扰。** 这就是 `get_db` 依赖注入存在的全部意义。

---

> **错误 3：`back_populates` 写错 —— 双向导航失效**

❌ 错误示例：

```python
# Post 类中
author = relationship("User", back_populates="articles")  # articles?

# User 类中
posts = relationship("Post", back_populates="author")
```

`back_populates` 的值 `"articles"` 和 `User` 类中实际的属性名 `"posts"` 不匹配。

**现象**：不会报错，但 `user.posts` 拿不到文章，`post.author` 也拿不到作者。两个方向都静默失败。

✅ 正确示例：

```python
# Post 类中
author = relationship("User", back_populates="posts")

# User 类中
posts = relationship("Post", back_populates="author")
```

**`back_populates` 的值必须是对方类中 `relationship` 的属性名。** 两个字符串要互相呼应——就像两个对讲机，必须调到同一个频道。

---

> **错误 4：`DATABASE_URL` 格式错误**

❌ 错误示例：

```python
DATABASE_URL = "sqlite://blog.db"       # 少了一个斜杠
DATABASE_URL = "sqlite:///blog.db"      # 路径不对（没有 ./）
DATABASE_URL = "sqlite://localhost/blog.db"  # SQLite 不支持 localhost
```

**现象**：启动时报错，提示无法连接数据库或数据库文件创建失败。

✅ 正确示例：

```python
DATABASE_URL = "sqlite:///./blog.db"
```

**三个斜杠**，`./` 表示当前目录。

---

### 步骤 11：用 DB Browser 亲眼看看数据库里的数据

我们的数据现在存在 `blog.db` 文件里。虽然用 curl 能验证接口，但有时候你想**直接**看看数据库里到底存了什么。这时候可以用 **DB Browser for SQLite**——一个免费的 SQLite 可视化工具。

**第 1 步：下载安装**

去 https://sqlitebrowser.org/dl/ 下载适合你操作系统的版本，安装。

**第 2 步：打开 `blog.db`**

1. 打开 DB Browser for SQLite
2. 点击"打开数据库"（Open Database）
3. 选择你项目目录下的 `blog.db` 文件
4. 点击"浏览数据"（Browse Data）标签

**第 3 步：查看数据**

- 在"表"（Table）下拉框中选择 `posts`
- 你会看到你创建的所有文章，每一行一条记录，每一列一个字段
- `id`、`title`、`content`、`published`、`created_at` 全部清晰可见

**这就是你的数据在硬盘上的真实样子。** 不是你想象中的 JSON 格式，而是一张规整的表格——就像 Excel 表格一样。

---

## 四、完整代码清单

### `blog_backend/database.py`（本章新建）

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

# === 1. 数据库地址 ===
DATABASE_URL = "sqlite:///./blog.db"

# === 2. 创建引擎 ===
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=True,
)

# === 3. 创建会话工厂 ===
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# === 4. 创建基类 ===
class Base(DeclarativeBase):
    pass

# === 5. 依赖注入 ===
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### `blog_backend/models.py`（本章新建）

```python
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from blog_backend.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    posts = relationship("Post", back_populates="author")


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    content = Column(String, nullable=False)
    published = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    author = relationship("User", back_populates="posts")


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(String(500), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    post = relationship("Post", backref="comments")
    author = relationship("User", backref="comments")
```

### `blog_backend/main.py`（本教程最终版本）

```python
from fastapi import FastAPI, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from blog_backend.schemas import BlogCreate
from blog_backend.database import engine, get_db, Base
from blog_backend import models

app = FastAPI()

# === 自动建表 ===
Base.metadata.create_all(bind=engine)


@app.get("/")
def read_root():
    return {"message": "Hello World"}


@app.get("/secret")
def secret_page():
    return JSONResponse(
        status_code=404,
        content={"error": "你找的秘密页面不存在！", "hint": "试试别的路径，比如 /"}
    )


# === 获取全部文章 ===
@app.get("/posts")
def get_all_posts(db: Session = Depends(get_db)):
    posts = db.query(models.Post).all()
    return posts


# === 创建文章 ===
@app.post("/posts", status_code=201)
def create_post(blog: BlogCreate, db: Session = Depends(get_db)):
    new_post = models.Post(
        title=blog.title,
        content=blog.content,
        published=blog.published,
        user_id=1,
    )
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post


# === 获取单篇文章 ===
@app.get("/posts/{post_id}")
def get_post(post_id: int, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if post is None:
        return JSONResponse(
            status_code=404,
            content={"error": f"文章 #{post_id} 不存在"}
        )
    return post


# === 更新文章 ===
@app.put("/posts/{post_id}")
def update_post(post_id: int, blog: BlogCreate, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if post is None:
        return JSONResponse(
            status_code=404,
            content={"error": f"文章 #{post_id} 不存在，无法更新"}
        )

    post.title = blog.title
    post.content = blog.content
    post.published = blog.published

    db.commit()
    db.refresh(post)
    return post


# === 删除文章 ===
@app.delete("/posts/{post_id}")
def delete_post(post_id: int, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if post is None:
        return JSONResponse(
            status_code=404,
            content={"error": f"文章 #{post_id} 不存在，无法删除"}
        )

    title = post.title
    db.delete(post)
    db.commit()
    return {"message": f"文章 #{post_id}「{title}」已删除"}
```

### `blog_backend/schemas.py`（沿用教程 06 的版本，无需修改）

```python
from pydantic import BaseModel


class BlogCreate(BaseModel):
    title: str
    content: str
    published: bool = False
    summary: str | None = None
```

---

## 五、验证方法

在终端中依次执行以下命令，确认全部通过：

```bash
# 1. 创建三篇文章
curl -X POST http://127.0.0.1:8000/posts -H "Content-Type: application/json" -d '{"title": "验证1", "content": "内容1"}'
curl -X POST http://127.0.0.1:8000/posts -H "Content-Type: application/json" -d '{"title": "验证2", "content": "内容2"}'
curl -X POST http://127.0.0.1:8000/posts -H "Content-Type: application/json" -d '{"title": "验证3", "content": "内容3"}'

# 2. 获取全部 → 应返回 3 篇，每篇都有 id 和 created_at
curl http://127.0.0.1:8000/posts

# 3. 获取单篇 → 应返回文章 2
curl http://127.0.0.1:8000/posts/2

# 4. 更新文章 2 → 应返回更新后的文章
curl -X PUT http://127.0.0.1:8000/posts/2 -H "Content-Type: application/json" -d '{"title": "验证2-改", "content": "内容2-改"}'

# 5. 删除文章 3 → 应返回删除成功消息
curl -X DELETE http://127.0.0.1:8000/posts/3

# 6. 获取全部 → 应返回 2 篇（ID 1 和 ID 2）
curl http://127.0.0.1:8000/posts

# 7. 获取已删除的文章 3 → 应返回 404
curl http://127.0.0.1:8000/posts/3

# 8. 重启服务器（Ctrl+C 停止，重新启动）
# uvicorn blog_backend.main:app --reload

# 9. 再次获取全部 → 应返回 2 篇，数据没丢！
curl http://127.0.0.1:8000/posts
```

全部通过，本章完成。

---

## 六、小结表格

| 你学到了什么 | 一句话总结 |
|--------------|-----------|
| ORM（对象关系映射） | 一个"翻译官"——你用 Python 对象说话，它帮你翻译成 SQL 发给数据库 |
| SQLAlchemy | Python 最流行的 ORM 库，本章的核心工具 |
| `engine` | SQLAlchemy 的"电话"——负责跟数据库建立连接 |
| `Session` | SQLAlchemy 的"临时工位"——每次数据库操作都在一个会话中进行 |
| `Base` | 所有 ORM 模型的"基类"——继承它，你的类才能被映射到数据库表 |
| `Column` | 定义表里的列——`Integer`、`String`、`DateTime`、`Boolean` 等 |
| `ForeignKey` | 外键——连接两张表的"纽带"，指向另一张表的主键 |
| `relationship` | 让 Python 对象之间可以互相导航——`post.author`、`user.posts` |
| `back_populates` | 双向关系的"对讲机频道"——两个类里的字符串必须互相匹配 |
| `create_all` | 一键按 ORM 模型在数据库里建表——表存在则跳过，不丢数据 |
| `db.add()` + `db.commit()` | 创建数据：先加入待办，再真正写入。**忘了 commit 数据就丢了！** |
| `db.query().filter().first()` | 按条件查询单条数据 |
| `db.query().all()` | 查询所有数据 |
| `db.delete()` + `db.commit()` | 删除数据 |
| 依赖注入（`Depends`） | 接口函数声明"我需要什么"，FastAPI 自动传入——`get_db` 是本章的典型应用 |
| 持久化 | 数据存到硬盘上，重启服务器不丢——本章用 `blog.db` 文件实现 |

---

## 七、术语附录

| 术语 | 英文 | 通俗解释 | 本章出现位置 |
|------|------|----------|-------------|
| ORM | Object-Relational Mapping | 对象关系映射。"翻译官"——你用 Python 对象操作数据，它帮你翻译成 SQL。**字面陷阱**：三个词都很抽象，但核心就一句"用 Python 对象代替 SQL 语句"。 | 步骤 1 |
| SQLAlchemy | — | Python 最流行的 ORM 库。名字来源于"SQL" + "Alchemy"（炼金术），意思是"把 SQL 变成金子的魔法"。 | 步骤 1 |
| engine | — | SQLAlchemy 的核心组件，负责与数据库建立连接、管理连接池。比喻为翻译官手里的"电话"。 | 步骤 3 |
| Session | — | SQLAlchemy 中和数据库交互的"工作单元"。每次查询、增删改都在一个 Session 中进行。比喻为翻译官的"临时工位"。 | 步骤 3 |
| 依赖注入 | Dependency Injection | 一种设计模式：函数声明自己需要什么，框架自动传入。FastAPI 中通过 `Depends()` 实现。本章 `get_db` 就是典型应用。 | 步骤 4 |
| `commit` | — | 提交事务——把待办清单上的所有操作真正写入数据库。**不 commit 数据就丢了，这是初学者最容易忘的。** | 步骤 8（接口 2） |
| `relationship` | — | SQLAlchemy 中定义 Python 对象之间关联的方法。不改变数据库结构，只影响 Python 对象的行为。 | 步骤 5.4 |
| `back_populates` | — | `relationship` 的参数，用于建立双向导航。两个关联类的 `back_populates` 值必须互相匹配。**字面陷阱**：`back_populates` 不是"回填数据"，而是"建立双向引用"。 | 步骤 5.4 |
| 外键 | Foreign Key | 数据库概念：一张表的某个列指向另一张表的主键，用来建立表之间的关联。 | 步骤 5.3 |
| SQLite | — | 一个零配置的轻量数据库。数据存在一个 `.db` 文件里，不需要安装数据库服务器。适合开发和小型项目。 | 步骤 3 |
| 持久化 | Persistence | 把数据存到硬盘（或 SSD）上，程序重启后数据还在。对应"内存"存储（重启即丢）。 | 步骤 0 |

---

## 八、已知坑点与禁止事项

| 坑点 | 现象 | 原因 | 解决 |
|------|------|------|------|
| 忘记 `session.commit()` | 创建/更新/删除操作看起来成功，但数据没存进去，重启后消失 | `add()`/`delete()` 只是标记，`commit()` 才真正写入 | 每个写操作后都要 `db.commit()` |
| 全局 session 共享 | 偶发数据错乱、莫名其妙报错 | 多个请求共享同一个 session，操作互相干扰 | 用 `get_db` 依赖注入，每次请求新建 session |
| `back_populates` 写错 | `user.posts` 返回空，`post.author` 返回空，但不报错 | 两个 `relationship` 的 `back_populates` 值不匹配 | 确保两个字符串互相呼应，如图 `"author"` ↔ `"posts"` |
| `DATABASE_URL` 格式错误 | 启动报错，无法连接数据库 | SQLite URL 是三个斜杠 `:///`，不是两个 `://` | 写成 `sqlite:///./blog.db` |
| 忘记导入 `models` 模块 | `create_all` 不报错，但一张表也没创建 | SQLAlchemy 需要导入模型类才能"发现"它们 | 在 `main.py` 中加 `from blog_backend import models` |
| `echo=True` 带到生产环境 | 日志文件暴增，磁盘占满 | 每个 SQL 语句都打印日志，生产环境请求量大 | 上线前改成 `echo=False` 或从环境变量读取 |
| 往 `models.py` 里加 `api` 相关代码 | 循环导入报错 | `models.py` 被 `main.py` 导入，`main.py` 又被 `models.py` 导入，形成死循环 | `models.py` 只放 ORM 模型定义，不导入任何 FastAPI 相关模块 |

---

## 九、下一步建议

你已经完成了从"内存版"到"数据库版"的升级！现在你的博客有了真正的"持久记忆"——重启服务器、关机、换电脑，数据都在。

- **延伸阅读**：想了解 SQLAlchemy 的更多查询能力？去查 `filter` 的高级用法（`like`、`in_`、`and_`、`or_`），以及排序（`order_by`）、分页（`limit`、`offset`）。
- **后续教程**：后续教程将处理用户认证——注册、登录、JWT Token，让 `user_id` 不再硬编码为 1，而是从当前登录用户获取。
- **进阶提醒**：本章的 `user_id=1` 硬编码只是临时方案。后续教程会教你如何从 JWT Token 中解析出当前用户，自动注入到接口中。

---

> **本章编辑记录**：2026-06-05 初始版本。