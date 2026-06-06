# 07-第一个接口实战：博客文章 CRUD（内存版）

- 对应文档版本：首版教程
- 适用环境：Python 3.10+, FastAPI 0.100+, curl（或 PowerShell）, Windows/macOS/Linux
- 读者角色：后端初学者
- 预计耗时：新手 60 分钟 / 熟手 25 分钟
- 前置教程：[06-请求体：POST 请求](./06-请求体：POST请求/)
- 可视化：无

---

## 一、目标与完成效果

**一句话目标**：把前面学的所有知识（路由、路径参数、JSON、POST 请求体、Pydantic 模型）串起来，实现一个完整的博客文章 CRUD 接口——能创建、查看、修改、删除文章，数据存在内存里。

**完成后的可观测效果**：
- 你用 curl 创建了一篇文章，返回了文章内容，并且带有一个自动生成的 ID。
- 你再用 curl 发一个 GET 请求，拿到刚才创建的那篇文章——数据真的"存"住了。
- 你用 curl 更新文章标题，再次 GET 验证，标题变了。
- 你用 curl 删除一篇文章，再次 GET 验证，返回 404。
- 你把五个接口全部测完，发现它们像一个真正的"后台管理系统"一样工作。
- 你重启服务器，发现刚才创建的所有文章全部消失了——然后你明白为什么这只是"内存版"。

---

## 二、前置条件

| 序号 | 条件 | 验证命令 |
|------|------|----------|
| 1 | 已完成教程 06，`blog_backend/schemas.py` 和 `blog_backend/main.py` 存在 | `dir blog_backend`（Windows）或 `ls blog_backend/` |
| 2 | 服务器正在运行（`uvicorn blog_backend.main:app --reload`） | 终端里能看到 `Uvicorn running on http://127.0.0.1:8000` |
| 3 | curl 可用 | `curl --version` 能输出版本号 |
| 4 | 理解 GET/POST 的区别，知道路径参数和请求体是什么 | 能说出 `GET /posts/1` 里的 `1` 是路径参数 |

**一条命令确认前置满足**：

```powershell
curl http://127.0.0.1:8000
```

如果返回 `{"message":"Hello World"}`，前置条件满足。

---

## 三、分步操作

### 步骤 0：为什么先做"内存版"？——分两步走，不晕

在开始写代码之前，我们先花 3 分钟回答一个你可能会问的问题：

> **"为什么先做一个重启就丢数据的内存版？直接连数据库不好吗？"**

**因为直接连数据库，你会同时学到两件新东西：**
1. 接口怎么设计（路由、请求体、参数、响应、错误处理）
2. 数据库怎么操作（SQL、ORM、连接、事务）

**同时学两件新东西 = 同时踩两个坑 = 报错时你完全不知道是接口写错了还是数据库连错了。**

这就像你第一次学开车——还没学会踩油门和刹车，教练就把你扔到高速公路上。你方向盘还没握稳，就要同时应对变道、超车、看路牌。结果就是：熄火、撞车、崩溃。

**我们的策略是"分两步走"：**

| 阶段 | 做什么 | 数据存哪 | 本章对应 |
|------|--------|----------|----------|
| 第一步 | 先学会"接口长什么样" | Python 列表（内存） | **本章（07）** |
| 第二步 | 再学会"数据怎么存" | 数据库（SQLite） | 教程 13 |

**本章只关心一件事：五个接口的"长相"和"行为"。** 数据存在一个 Python 列表里，你不用管数据库、不用写 SQL、不用配连接。等接口写对了、逻辑跑通了，到了教程 13 再换数据库——那时候你只需要改"数据存储"这一个部分，接口逻辑完全不变。

**一句话**：先学会"上菜"，再学"做菜"。本章学上菜。

---

### 步骤 1：接口设计表——先画蓝图，再盖房子

在动手写代码之前，我们先把"要盖什么样的房子"画出来。下面是五个接口的完整设计表：

| 方法 | 路径 | 功能 | 请求体 | 成功响应 | 失败响应 |
|------|------|------|--------|----------|----------|
| `GET` | `/posts` | 获取全部文章 | 无 | `200` + 文章列表 | — |
| `GET` | `/posts/{id}` | 获取单篇文章 | 无 | `200` + 文章对象 | `404` 文章不存在 |
| `POST` | `/posts` | 创建文章 | `{"title": "...", "content": "..."}` | `200` + 创建的文章 | `422` 数据校验失败 |
| `PUT` | `/posts/{id}` | 更新文章 | `{"title": "...", "content": "..."}` | `200` + 更新后的文章 | `404` 文章不存在 |
| `DELETE` | `/posts/{id}` | 删除文章 | 无 | `200` + `{"message": "删除成功"}` | `404` 文章不存在 |

**这就是 CRUD。** 每个字母对应一个操作：

| 字母 | 全称 | 中文 | 对应 HTTP 方法 | 比喻 |
|------|------|------|---------------|------|
| **C** | Create | 创建 | `POST` | 往书架上放一本新书 |
| **R** | Read | 读取 | `GET` | 从书架上拿一本书看 |
| **U** | Update | 更新 | `PUT` | 把书架上某本书换成新版本 |
| **D** | Delete | 删除 | `DELETE` | 从书架上拿走一本书 |

**CRUD 是后端开发中最基础的模式。** 无论你做什么系统——博客、电商、聊天、任务管理——本质上都是对某种"资源"做增删改查。你学会了博客文章的 CRUD，换个"商品"或"订单"你也一样会写。

> **RESTful 风格**：你可能听说过"RESTful API"这个词。我们这套接口设计（`GET /posts`、`POST /posts`、`GET /posts/{id}`、`PUT /posts/{id}`、`DELETE /posts/{id}`）就是典型的 RESTful 风格。它的核心思想是：**用 URL 表示"资源"（posts），用 HTTP 方法表示"操作"（GET/POST/PUT/DELETE）**。URL 里不出现动词（比如不用 `/createPost`、`/deletePost` 这种写法），动词由 HTTP 方法来表达。此术语需进附录。

---

### 步骤 2：用 Python 列表模拟数据库

先打开 `blog_backend/main.py`。在文件开头（`app = FastAPI()` 之后），加一行：

```python
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from blog_backend.schemas import BlogCreate

app = FastAPI()

# === 用列表模拟数据库 ===
posts_db: list[dict] = []  # 这篇文章的"数据库"
```

**这一行在干什么？**

`posts_db` 是一个空列表，类型注解 `list[dict]` 表示"这是一个列表，里面每个元素是一个字典"。每个字典代表一篇文章，比如：

```python
{
    "id": 1,
    "title": "我的第一篇文章",
    "content": "这是正文内容。",
    "published": True
}
```

**比喻**：`posts_db` 就像你书桌上的一叠便签纸。每张便签纸上记着一篇文章的信息。你可以在上面加新便签（创建文章）、翻看某张便签（读取文章）、修改便签上的内容（更新文章）、把便签撕掉扔掉（删除文章）。

**为什么叫"内存版"？** 因为这个列表存在 Python 程序的内存里。程序在跑，列表就在；程序停了，列表就没了。就像你写在便签纸上的东西——便签纸在桌上就在，你把便签纸全扔了（重启服务器），就什么都没了。

---

### 步骤 3：逐个实现五个接口

现在开始一个接口一个接口地写。每个接口都遵循"三步走"：**代码 → curl 测试 → 验证返回**。

---

#### 接口 1：`GET /posts` —— 获取全部文章

**我在做什么？** 写一个接口，当用户访问 `/posts` 时，把 `posts_db` 里所有的文章一次性返回。

**代码**（追加到 `main.py` 末尾）：

```python
# === 获取全部文章 ===
@app.get("/posts")
def get_all_posts():
    return posts_db
```

**解释**：就这么简单。`posts_db` 是一个列表，FastAPI 自动把它转成 JSON 数组返回。如果列表是空的，就返回 `[]`（空数组）。

**curl 测试**：

```bash
curl http://127.0.0.1:8000/posts
```

**预期输出**：

```json
[]
```

空的。因为还没创建任何文章。别急，下一个接口就来创建。

---

#### 接口 2：`POST /posts` —— 创建文章

**我在做什么？** 写一个接口，当用户用 POST 方法访问 `/posts` 并带上文章的标题和内容时，把文章存进 `posts_db`，然后返回创建好的文章。

**代码**（追加到 `main.py` 末尾）：

```python
# === 创建文章 ===
@app.post("/posts")
def create_post(blog: BlogCreate):
    # 生成自增 ID
    new_id = len(posts_db) + 1

    # 构建新文章
    new_post = {
        "id": new_id,
        "title": blog.title,
        "content": blog.content,
        "published": blog.published,
    }

    # 存入"数据库"
    posts_db.append(new_post)

    return new_post
```

**逐行解释**：

- `new_id = len(posts_db) + 1`：**自增 ID** 的实现。`len(posts_db)` 是当前列表里有多少篇文章。如果是空的（0 篇），`0 + 1 = 1`，第一篇就是 ID 1。如果已有 3 篇，`3 + 1 = 4`，新文章就是 ID 4。此术语需进附录。

- `new_post = {...}`：把 `BlogCreate` 里的字段拿出来，加上一个 `id` 字段，拼成完整的文章字典。

- `posts_db.append(new_post)`：把新文章加到列表末尾。`append` 是 Python 列表的方法，意思是"在末尾追加一个元素"。

- `return new_post`：返回创建好的文章，FastAPI 自动转成 JSON。

> **这里用到了教程 06 学的 `BlogCreate` 模型**。`blog.title`、`blog.content`、`blog.published` 都是 Pydantic 校验通过后才传进来的，你可以放心使用。

**curl 测试**：

```bash
curl -X POST http://127.0.0.1:8000/posts ^
  -H "Content-Type: application/json" ^
  -d "{\"title\": \"我的第一篇文章\", \"content\": \"这是正文内容。\", \"published\": true}"
```

> **PowerShell 用户注意**：PowerShell 中 `^` 是续行符（不是 `\`）。如果不想换行，就把整条命令写成一行。另外，JSON 里的双引号在 PowerShell 中需要用 `\"` 转义。如果嫌麻烦，可以用单引号括 JSON，但 `true` 必须写成 `$true`。**更简单的方法**：把整条命令写成一行，用双引号括 JSON 外部，内部双引号用 `\"` 转义，就像上面那样。

> **如果上面这条命令在 PowerShell 中报错**，试试这个简化版（一行，不换行，JSON 用单引号包，把 `true` 换成字符串 `"true"` 暂时不纠结类型）：
>
> ```powershell
> curl -X POST http://127.0.0.1:8000/posts -H "Content-Type: application/json" -d '{"title": "我的第一篇文章", "content": "这是正文内容。", "published": true}'
> ```
>
> 如果单引号版本也不行，就把 `true` 改成 `"yes"` 字符串，FastAPI 的 Pydantic 会自动转换：
>
> ```powershell
> curl -X POST http://127.0.0.1:8000/posts -H "Content-Type: application/json" -d '{"title": "我的第一篇文章", "content": "这是正文内容。", "published": "yes"}'
> ```

**预期输出**：

```json
{"id":1,"title":"我的第一篇文章","content":"这是正文内容。","published":true}
```

**验证**：再发一条 GET 请求，确认文章真的存进去了：

```bash
curl http://127.0.0.1:8000/posts
```

**预期输出**：

```json
[{"id":1,"title":"我的第一篇文章","content":"这是正文内容。","published":true}]
```

列表里有一篇文章了！ID 是 1，标题、内容、发布状态都对。

**多创建几篇，方便后面测试**：

```bash
# 创建第二篇
curl -X POST http://127.0.0.1:8000/posts -H "Content-Type: application/json" -d '{"title": "第二篇文章", "content": "第二篇的正文。", "published": false}'

# 创建第三篇
curl -X POST http://127.0.0.1:8000/posts -H "Content-Type: application/json" -d '{"title": "第三篇文章", "content": "第三篇的正文。", "published": true}'
```

现在 `GET /posts` 应该返回三篇文章了：

```bash
curl http://127.0.0.1:8000/posts
```

**预期输出**：

```json
[{"id":1,"title":"我的第一篇文章","content":"这是正文内容。","published":true},{"id":2,"title":"第二篇文章","content":"第二篇的正文。","published":false},{"id":3,"title":"第三篇文章","content":"第三篇的正文。","published":true}]
```

---

#### 接口 3：`GET /posts/{id}` —— 获取单篇文章

**我在做什么？** 写一个接口，当用户访问 `/posts/1` 时返回第 1 篇文章，访问 `/posts/2` 时返回第 2 篇。如果文章不存在，返回 404。

**代码**（追加到 `main.py` 末尾）：

```python
# === 获取单篇文章 ===
@app.get("/posts/{post_id}")
def get_post(post_id: int):
    # 遍历列表，找到 id 匹配的文章
    for post in posts_db:
        if post["id"] == post_id:
            return post

    # 没找到 → 返回 404
    return JSONResponse(
        status_code=404,
        content={"error": f"文章 #{post_id} 不存在"}
    )
```

**逐行解释**：

- `@app.get("/posts/{post_id}")`：`{post_id}` 是**路径参数**（教程 05 学过）。URL 里写了什么，`post_id` 就是什么。
- `def get_post(post_id: int)`：`int` 类型注解告诉 FastAPI 把路径参数转成整数。如果用户访问 `/posts/abc`，FastAPI 会自动返回 422 错误（因为 `"abc"` 不是整数）。
- `for post in posts_db:`：遍历列表，一篇一篇找。这是最朴素的查找方式——就像你在一叠便签纸里一张一张翻，找到编号对上的那张。
- `if post["id"] == post_id:`：找到了！直接返回这篇文章。
- `return JSONResponse(status_code=404, ...)`：循环结束都没找到，说明文章不存在，返回 404。这是教程 04 学过的 `JSONResponse` 用法。

**curl 测试**：

```bash
# 获取存在的文章（ID 1）
curl http://127.0.0.1:8000/posts/1

# 获取不存在的文章（ID 999）
curl http://127.0.0.1:8000/posts/999
```

**预期输出（ID 1）**：

```json
{"id":1,"title":"我的第一篇文章","content":"这是正文内容。","published":true}
```

**预期输出（ID 999）**：

```json
{"error":"文章 #999 不存在"}
```

同时 HTTP 状态码是 404。用 `curl -v` 可以看到：

```bash
curl -v http://127.0.0.1:8000/posts/999
```

响应头第一行会显示 `< HTTP/1.1 404 Not Found`。

---

#### 接口 4：`PUT /posts/{id}` —— 更新文章

**我在做什么？** 写一个接口，当用户用 PUT 方法访问 `/posts/1` 并带上新的标题和内容时，更新第 1 篇文章的数据。如果文章不存在，返回 404。

**代码**（追加到 `main.py` 末尾）：

```python
# === 更新文章 ===
@app.put("/posts/{post_id}")
def update_post(post_id: int, blog: BlogCreate):
    # 先找到这篇文章的索引
    for i, post in enumerate(posts_db):
        if post["id"] == post_id:
            # 找到了！更新数据
            posts_db[i] = {
                "id": post_id,  # id 不变
                "title": blog.title,
                "content": blog.content,
                "published": blog.published,
            }
            return posts_db[i]

    # 没找到 → 返回 404
    return JSONResponse(
        status_code=404,
        content={"error": f"文章 #{post_id} 不存在，无法更新"}
    )
```

**逐行解释**：

- `for i, post in enumerate(posts_db):`：`enumerate()` 是 Python 内置函数，它同时给你**索引**（`i`）和**元素**（`post`）。比如第一篇：`i=0, post={"id": 1, ...}`。我们需要索引，因为后面要用 `posts_db[i] = ...` 来替换这一项。
- `if post["id"] == post_id:`：找到了目标文章。
- `posts_db[i] = {...}`：**用新字典替换旧字典**。注意 `"id": post_id` 保持不变——更新文章不改 ID。`title`、`content`、`published` 用请求体中的新值。
- `return posts_db[i]`：返回更新后的文章。
- 如果循环结束都没找到，返回 404。

**curl 测试**：

```bash
# 更新文章 1 的标题
curl -X PUT http://127.0.0.1:8000/posts/1 -H "Content-Type: application/json" -d '{"title": "更新后的标题", "content": "更新后的正文。", "published": true}'

# 验证更新是否生效
curl http://127.0.0.1:8000/posts/1

# 尝试更新不存在的文章
curl -X PUT http://127.0.0.1:8000/posts/999 -H "Content-Type: application/json" -d '{"title": "不存在", "content": "不存在。"}'
```

**预期输出（更新成功）**：

```json
{"id":1,"title":"更新后的标题","content":"更新后的正文。","published":true}
```

**预期输出（文章不存在）**：

```json
{"error":"文章 #999 不存在，无法更新"}
```

---

#### 接口 5：`DELETE /posts/{id}` —— 删除文章

**我在做什么？** 写一个接口，当用户用 DELETE 方法访问 `/posts/1` 时，删除第 1 篇文章。如果文章不存在，返回 404。

**代码**（追加到 `main.py` 末尾）：

```python
# === 删除文章 ===
@app.delete("/posts/{post_id}")
def delete_post(post_id: int):
    # 找到这篇文章的索引
    for i, post in enumerate(posts_db):
        if post["id"] == post_id:
            # 找到了！删除它
            deleted = posts_db.pop(i)
            return {"message": f"文章 #{post_id}「{deleted['title']}」已删除"}

    # 没找到 → 返回 404
    return JSONResponse(
        status_code=404,
        content={"error": f"文章 #{post_id} 不存在，无法删除"}
    )
```

**逐行解释**：

- `@app.delete("/posts/{post_id}")`：`@app.delete` 表示这是一个 DELETE 路由。这是你第一次用 `@app.delete` 装饰器，用法和 `@app.get`、`@app.post` 完全一样。
- `posts_db.pop(i)`：`pop()` 是 Python 列表的方法，它做两件事：① 删除指定索引的元素；② 返回被删除的那个元素。这里我们用 `deleted` 变量接收返回值，方便在响应消息里引用被删文章的标题。
- 返回 `{"message": "..."}` 而不是被删的文章——这是常见做法，告诉用户"删成功了"。你也可以返回被删的文章，两种都可以，但返回消息更清晰。

**curl 测试**：

```bash
# 删除文章 2
curl -X DELETE http://127.0.0.1:8000/posts/2

# 验证删除是否生效
curl http://127.0.0.1:8000/posts/2

# 尝试删除不存在的文章
curl -X DELETE http://127.0.0.1:8000/posts/999
```

**预期输出（删除成功）**：

```json
{"message":"文章 #2「第二篇文章」已删除"}
```

**预期输出（验证删除）**：

```json
{"error":"文章 #2 不存在"}
```

**预期输出（文章不存在）**：

```json
{"error":"文章 #999 不存在，无法删除"}
```

---

### 步骤 4：自增 ID 的细节——为什么删除后 ID 不连续？

你已经创建了 3 篇文章，然后删了第 2 篇。现在 `posts_db` 里有 2 篇文章（ID 1 和 ID 3）。再创建一篇新文章，它的 ID 会是多少？

```bash
curl -X POST http://127.0.0.1:8000/posts -H "Content-Type: application/json" -d '{"title": "新文章", "content": "新内容。"}'
```

**预期输出**：

```json
{"id":3,"title":"新文章","content":"新内容。","published":false}
```

咦？ID 是 3？但列表里已经有 ID 3 的文章了！

**这就是 `len(posts_db) + 1` 的局限性。** 删除 ID 2 后，列表里还有 2 篇文章（ID 1 和 ID 3），`len(posts_db)` 是 2，`2 + 1 = 3`，但 ID 3 已经被占用了。

> **🤔 想多一点：自增 ID 为什么这么"笨"？**

你用 `len(posts_db) + 1` 生成 ID，删掉中间的文章后，`len()` 变小了，新 ID 就会和已有的重复。这个问题在真实数据库里不会出现——数据库的自增 ID 是独立维护的计数器，它只增不减，删了文章计数器也不会倒退。

**那为什么我们不用更"聪明"的方法？** 比如遍历列表找最大 ID 再加 1？

**因为本章的目标不是"做一个完美的 ID 生成器"，而是"理解接口逻辑"。** 在教程 13 换成数据库后，ID 生成由数据库自动处理，你根本不需要写 `len(posts_db) + 1` 这行代码。现在花时间优化一个会被丢掉的方案，不值得。

**现阶段的生命周期**：创建 3 篇 → 删 1 篇 → 再创建会产生 ID 冲突。**没关系，教程 13 换数据库后这个问题就消失了。** 现在你只需要知道：自增 ID 在真实数据库中由数据库自动维护，不会重复也不会倒退。

---

### ❌ 常见错误 → ✅ 正确示例

> **错误 1：PUT 请求找不到文章，但代码没有处理 404**

❌ 错误示例：

```python
@app.put("/posts/{post_id}")
def update_post(post_id: int, blog: BlogCreate):
    for i, post in enumerate(posts_db):
        if post["id"] == post_id:
            posts_db[i] = {"id": post_id, "title": blog.title, "content": blog.content, "published": blog.published}
            return posts_db[i]
    # 循环结束，什么都没返回 → FastAPI 返回 null（200 状态码！）
```

如果 `post_id` 不存在，`for` 循环结束后函数没有 `return` 任何东西，Python 函数默认返回 `None`。FastAPI 会把 `None` 转成 JSON 的 `null`，并且 HTTP 状态码是 **200**（成功！）。这就有问题了——客户端以为更新成功了，但实际上什么都没发生。

✅ 正确示例：

```python
@app.put("/posts/{post_id}")
def update_post(post_id: int, blog: BlogCreate):
    for i, post in enumerate(posts_db):
        if post["id"] == post_id:
            posts_db[i] = {"id": post_id, "title": blog.title, "content": blog.content, "published": blog.published}
            return posts_db[i]

    # 必须显式返回 404
    return JSONResponse(
        status_code=404,
        content={"error": f"文章 #{post_id} 不存在，无法更新"}
    )
```

---

> **错误 2：DELETE 时用 `del` 而不是 `pop()`**

❌ 错误示例：

```python
del posts_db[i]
return {"message": "删除成功"}
```

`del` 只删除，不返回被删除的元素。如果你想在响应消息里引用被删文章的标题，拿不到。

✅ 正确示例：

```python
deleted = posts_db.pop(i)
return {"message": f"文章 #{post_id}「{deleted['title']}」已删除"}
```

用 `pop()` 既能删除又能拿到被删的数据，一举两得。

---

> **错误 3：curl 命令中 JSON 的引号在 PowerShell 中转义不正确**

❌ 错误示例（PowerShell 中用 `\` 续行，JSON 内双引号不转义）：

```powershell
curl -X POST http://127.0.0.1:8000/posts \
  -H "Content-Type: application/json" \
  -d '{"title": "我的文章", "content": "正文"}'
```

PowerShell 中 `\` 不是续行符。如果这条命令恰好能跑，是因为 curl 把它当成了一个参数。但如果 JSON 里有 `true` 之类的布尔值，单引号内的 `true` 会被当成字符串。

✅ 正确示例（PowerShell 一行版）：

```powershell
curl -X POST http://127.0.0.1:8000/posts -H "Content-Type: application/json" -d '{"title": "我的文章", "content": "正文"}'
```

或者用双引号 + 转义：

```powershell
curl -X POST http://127.0.0.1:8000/posts -H "Content-Type: application/json" -d "{\"title\": \"我的文章\", \"content\": \"正文\"}"
```

**最简单的办法**：安装 Git Bash 或在 WSL 中运行 curl，这样就能用标准的 bash 语法（`\` 续行，单引号内正常写 JSON）。

---

### 步骤 5：阶段性验证——用 curl 把五个接口全部跑一遍

现在你的 `main.py` 应该包含了全部五个接口。让我们从头到尾走一遍完整流程，观察数据变化。

> **建议**：在开始之前，先重启一下服务器（在终端按 `Ctrl+C` 停止，然后重新执行 `uvicorn blog_backend.main:app --reload`），清空内存中的数据，从零开始验证。

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

应该看到 3 篇文章，ID 分别是 1、2、3。

**第 3 步：获取单篇文章**

```bash
curl http://127.0.0.1:8000/posts/2
```

应该看到第 2 篇文章（`"Python 技巧"`）。

**第 4 步：更新文章 2**

```bash
curl -X PUT http://127.0.0.1:8000/posts/2 -H "Content-Type: application/json" -d '{"title": "Python 进阶技巧", "content": "列表推导式、生成器、装饰器。", "published": true}'
```

**第 5 步：验证更新**

```bash
curl http://127.0.0.1:8000/posts/2
```

应该看到标题变成了 `"Python 进阶技巧"`，`published` 变成了 `true`。

**第 6 步：删除文章 3**

```bash
curl -X DELETE http://127.0.0.1:8000/posts/3
```

**第 7 步：验证删除**

```bash
curl http://127.0.0.1:8000/posts/3
```

应该返回 `{"error":"文章 #3 不存在"}`。

**第 8 步：获取全部文章，确认只剩 2 篇**

```bash
curl http://127.0.0.1:8000/posts
```

应该看到 ID 1 和 ID 2 两篇文章，ID 3 没有了。

**第 9 步：测试 404 错误**

```bash
curl http://127.0.0.1:8000/posts/999
curl -X PUT http://127.0.0.1:8000/posts/999 -H "Content-Type: application/json" -d '{"title": "不存在", "content": "不存在。"}'
curl -X DELETE http://127.0.0.1:8000/posts/999
```

三条命令都应该返回 404 错误。

全部通过？**恭喜，你的第一个 CRUD 接口完成！** 🎉

---

### 步骤 6：内存版的致命缺陷——重启即失忆

现在来做最后一个实验——也是本章最重要的一个实验。

**第 1 步**：确认当前有数据：

```bash
curl http://127.0.0.1:8000/posts
```

你应该看到 2 篇文章（ID 1 和 ID 2）。

**第 2 步**：重启服务器。在终端按 `Ctrl+C` 停止 uvicorn，然后重新启动：

```bash
uvicorn blog_backend.main:app --reload
```

**第 3 步**：再次获取全部文章：

```bash
curl http://127.0.0.1:8000/posts
```

**预期输出**：

```json
[]
```

**空的。刚才那两篇文章全没了。**

**为什么？** 因为 `posts_db = []` 这行代码在服务器启动时执行。每次启动，Python 都会重新执行一遍 `main.py`，`posts_db` 被重新赋值为一个空列表。你之前创建的所有文章，只存在于上一次进程的内存里——进程一死，数据就跟着死了。

**这就像你在沙滩上写字。** 水一冲，什么都没了。沙子（内存）只是临时载体，要永久保存，你需要刻在石头上（数据库）。

**这就是为什么我们需要阶段三——数据库。** 数据库把数据写在硬盘上，服务器重启了数据还在。在教程 13 中，我们会把 `posts_db` 这个列表替换成数据库表，五个接口的代码**几乎不需要改动**，只需要把"操作列表"换成"操作数据库"。

> **🤔 想多一点：内存版真的没用吗？**

**不，内存版非常有用，它有两个不可替代的价值：**

1. **降低了学习坡度**：你在本章只学了"接口逻辑"，没有同时被数据库连接、SQL 语句、ORM 配置轰炸。等接口逻辑烂熟于心后，再学数据库，你只需要关注"数据怎么存"这一个新东西。

2. **它是测试的绝佳工具**：在教程 24-25 中写测试时，你会发现内存版非常方便——不需要启动数据库、不需要清理数据，每次测试都是全新的环境，跑完就扔。很多专业项目的单元测试也是用内存数据来模拟数据库的。

**所以内存版不是"将就"，是"策略"。** 你先把接口的形状和逻辑刻在脑子里，下一阶段再给它们装上"持久化引擎"。

---

## 四、完整代码清单

### `blog_backend/schemas.py`（沿用教程 06 的版本，无需修改）

```python
from pydantic import BaseModel


class BlogCreate(BaseModel):
    title: str
    content: str
    published: bool = False
    summary: str | None = None
```

### `blog_backend/main.py`（本教程最终版本）

```python
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from blog_backend.schemas import BlogCreate

app = FastAPI()

# === 用列表模拟数据库 ===
posts_db: list[dict] = []


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
def get_all_posts():
    return posts_db


# === 创建文章 ===
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


# === 获取单篇文章 ===
@app.get("/posts/{post_id}")
def get_post(post_id: int):
    for post in posts_db:
        if post["id"] == post_id:
            return post
    return JSONResponse(
        status_code=404,
        content={"error": f"文章 #{post_id} 不存在"}
    )


# === 更新文章 ===
@app.put("/posts/{post_id}")
def update_post(post_id: int, blog: BlogCreate):
    for i, post in enumerate(posts_db):
        if post["id"] == post_id:
            posts_db[i] = {
                "id": post_id,
                "title": blog.title,
                "content": blog.content,
                "published": blog.published,
            }
            return posts_db[i]
    return JSONResponse(
        status_code=404,
        content={"error": f"文章 #{post_id} 不存在，无法更新"}
    )


# === 删除文章 ===
@app.delete("/posts/{post_id}")
def delete_post(post_id: int):
    for i, post in enumerate(posts_db):
        if post["id"] == post_id:
            deleted = posts_db.pop(i)
            return {"message": f"文章 #{post_id}「{deleted['title']}」已删除"}
    return JSONResponse(
        status_code=404,
        content={"error": f"文章 #{post_id} 不存在，无法删除"}
    )
```

---

## 五、验证方法

在终端中依次执行以下命令，确认全部通过：

```bash
# 1. 创建三篇文章
curl -X POST http://127.0.0.1:8000/posts -H "Content-Type: application/json" -d '{"title": "验证1", "content": "内容1"}'
curl -X POST http://127.0.0.1:8000/posts -H "Content-Type: application/json" -d '{"title": "验证2", "content": "内容2"}'
curl -X POST http://127.0.0.1:8000/posts -H "Content-Type: application/json" -d '{"title": "验证3", "content": "内容3"}'

# 2. 获取全部 → 应返回 3 篇
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

# 8. 获取不存在的文章 999 → 应返回 404
curl http://127.0.0.1:8000/posts/999
```

全部通过，本章完成。

---

## 六、小结

| 你学到了什么 | 一句话总结 |
|--------------|-----------|
| CRUD | 后端开发最基础的模式：Create（增）、Read（查）、Update（改）、Delete（删） |
| RESTful 风格 | 用 URL 表示资源（`/posts`），用 HTTP 方法表示操作（GET/POST/PUT/DELETE） |
| 自增 ID | 用 `len(posts_db) + 1` 生成新文章 ID，真实项目中由数据库自动维护 |
| `enumerate()` | Python 内置函数，遍历列表时同时拿到索引和元素，更新和删除时必备 |
| `list.pop(i)` | 删除指定索引的元素并返回它，比 `del` 多一个"返回被删数据"的能力 |
| 404 错误处理 | 遍历列表没找到目标 → 返回 `JSONResponse(status_code=404, ...)` |
| 内存版 vs 数据库版 | 内存版 = 数据在列表里，重启就丢；数据库版 = 数据在硬盘上，重启还在 |
| 学习策略 | 先学会"接口长什么样"（本章），再学会"数据怎么存"（教程 13） |

---

## 七、术语附录

| 术语 | 英文 | 通俗解释 | 本章出现位置 |
|------|------|----------|-------------|
| CRUD | Create, Read, Update, Delete | 数据库操作的四个基本动作：增、查、改、删。几乎所有后端系统本质上都是对某些资源做 CRUD。**字面陷阱**：CRUD 和 "crude"（粗糙的）发音一样，但意思完全不同。 | 步骤 1 |
| 自增 ID | Auto-increment ID | 一种自动生成唯一编号的机制。每新增一条记录，ID 自动加 1。真实数据库中由数据库引擎维护，不会重复。本章用 `len(posts_db) + 1` 模拟。 | 步骤 3（接口 2）、步骤 4 |
| RESTful | Representational State Transfer | 一种 API 设计风格，核心理念：URL 只表示"资源"（名词），HTTP 方法表示"操作"（动词）。比如 `/posts`（资源）+ `GET`（读取）而不是 `/getPosts`（动词混在 URL 里）。**字面陷阱**：REST 不是 "rest"（休息），是几个单词的缩写。 | 步骤 1 |
| 内存 | Memory（RAM） | 计算机的"临时工作台"——程序运行时数据存在这里，断电或重启就消失。硬盘（磁盘）是"永久仓库"，数据写进去就一直在。本章的数据存在内存中，教程 13 会存到硬盘（数据库）。 | 步骤 2、步骤 6 |
| `enumerate()` | — | Python 内置函数，遍历列表时同时返回 `(索引, 元素)`。比如 `for i, x in enumerate(["a", "b"])` 第一次得到 `(0, "a")`，第二次得到 `(1, "b")`。 | 步骤 3（接口 4） |
| `pop()` | — | Python 列表的方法，删除指定位置的元素，并返回被删除的元素。`list.pop(0)` 删除第一个，`list.pop()` 删除最后一个。 | 步骤 3（接口 5） |

---

## 八、已知坑点与禁止事项

| 坑点 | 现象 | 原因 | 解决 |
|------|------|------|------|
| 找不到文章时忘记返回 404 | 更新/删除不存在的文章，返回 `null` 且状态码 200 | 函数没有显式 `return`，Python 默认返回 `None` | 在循环结束后加 `return JSONResponse(status_code=404, ...)` |
| 删除后用 `len(posts_db) + 1` 生成 ID 可能重复 | 新文章的 ID 和已存在的文章 ID 冲突 | 删除后列表长度变小，但"自增"没有记录历史最大值 | 教程 13 换数据库后自动解决，现阶段不用管 |
| PowerShell 中 curl 的 JSON 引号问题 | 命令报错或 JSON 解析失败 | PowerShell 对单引号和双引号的处理与 bash 不同，`\` 也不是续行符 | 把命令写成一行；或用 Git Bash/WSL 运行 curl |
| 重启服务器后数据丢失 | 之前创建的文章全没了 | 数据存在内存（Python 列表）中，进程结束内存释放 | 这是预期行为，教程 13 换数据库后解决 |

---

## 九、下一步建议

你已经完成了第一个完整的 CRUD 接口！虽然数据还只是存在内存里，但五个接口的"形状"和"逻辑"你已经掌握了。接下来：

- **下一章**：[08-中间件：窥探每个请求](./08-中间件：窥探每个请求/)——学习中间件，看看每个请求进来时服务器到底发生了什么。
- **阶段二终点**：完成教程 08 后，阶段二（数据来去）结束。你可以在那时停下来，回顾一下自己从"只会 Hello World"到"能写完整 CRUD 接口"的进步。
- **阶段三预告**：教程 09-13 将进入数据库世界。你会学到 SQLite、SQL 语句、SQLAlchemy ORM，最后把本章的五个接口升级为"数据库版"——数据再也不会丢了。

---

> [可暂停点 4/9]：阶段二即将结束。你已经能写完整的 CRUD 接口了（虽然数据还存在内存里）。下次从 [08-中间件：窥探每个请求](./08-中间件：窥探每个请求/) 继续。