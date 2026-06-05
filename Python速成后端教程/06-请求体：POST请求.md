# 06-请求体：POST 请求

- 对应文档版本：首版教程
- 适用环境：Python 3.10+, FastAPI 0.100+, curl（或 PowerShell）, Windows/macOS/Linux
- 读者角色：后端初学者
- 预计耗时：新手 40 分钟 / 熟手 15 分钟
- 前置教程：[03-什么是 API：请求与响应](./03-什么是API：请求与响应.md)
- 可视化：无

---

## 一、目标与完成效果

**一句话目标**：学会用 POST 请求向服务器"提交数据"（而不是像 GET 那样只管"看"），用 Pydantic 模型定义数据格式，让 FastAPI 自动帮你校验数据对不对。

**完成后的可观测效果**：
- 你能用一句话说清楚 GET 和 POST 的区别——给别人讲明白，而不是自己"大概知道"。
- 你新建了一个 `schemas.py` 文件，在里面定义了一个 `BlogCreate` 类，用 Python 类型注解声明了字段要求。
- 你用 curl 发了一条 POST 请求，创建了一篇"博客文章"，服务器返回了成功响应。
- 你故意发一条缺少 `title` 的请求，亲眼看到 FastAPI 返回 422 错误，并且错误信息详细告诉你"哪个字段少了"。
- 你故意把 `Content-Type` 设错，亲眼看到 415 错误，知道为什么会报这个错以及怎么修。

---

## 二、前置条件

| 序号 | 条件 | 验证命令 |
|------|------|----------|
| 1 | 已完成教程 03，理解 GET 请求和状态码 | 浏览器访问 `http://127.0.0.1:8000` 返回 `{"message":"Hello World"}` |
| 2 | 服务器正在运行（`uvicorn blog_backend.main:app --reload`） | 终端里能看到 `Uvicorn running on http://127.0.0.1:8000` |
| 3 | curl 可用（或 PowerShell 的 `Invoke-WebRequest`） | `curl --version` 能输出版本号 |
| 4 | 项目目录 `blog_backend/` 存在 | `dir blog_backend`（Windows）或 `ls blog_backend/` |

**一条命令确认前置满足**：

```powershell
curl http://127.0.0.1:8000
```

如果返回 `{"message":"Hello World"}`，前置条件满足。

---

## 三、分步操作

### 步骤 1：GET vs POST——"给我看"和"帮我存"

在教程 03 中，我们学了 GET 请求。你访问 `http://127.0.0.1:8000`，浏览器发了一个 GET 请求，服务器把数据返回给你。整个过程就像你去图书馆借书——你只是**看**，书不会少，书架不会变。

但现实中的后端不只是"展示数据"。用户要注册账号、要发文章、要上传头像——这些操作都会**改变服务器上的数据**。这时候 GET 就不够用了，你需要 POST。

#### 比喻：图书馆借书 vs 捐书

| | GET（借书） | POST（捐书） |
|------|------------|------------|
| 你做什么 | 从书架上拿一本书看 | 把一本新书放进书架 |
| 服务器数据变了吗 | 没变（书还在） | 变了（多了一本书） |
| 你需要带什么 | 什么都不用带，说书名就行 | 必须带一本实体书过去 |
| 能重复做吗 | 可以，借一百次书也不会多出来 | 可以，捐一百次书就多一百本 |
| 对应的 HTTP 请求 | 请求体通常为空 | 请求体里装着你要提交的数据 |

**一句话总结**：GET 是"给我看看"，POST 是"帮我存下来"。

GET 请求的数据跟在 URL 后面（比如 `http://127.0.0.1:8000/search?keyword=Python`），一眼就能看到。POST 请求的数据装在**请求体**里，URL 上看不到——就像你捐书的时候，书名不会写在图书馆门口的告示牌上，而是写在书里夹着的入库单上。

> **请求体**（Request Body）就是 POST 请求里"夹带的数据"。它是 HTTP 请求的第四个组成部分（前三个是 URL、方法、请求头，我们在教程 03 学过）。

---

### 步骤 2：用 Pydantic 定义请求体模型

现在我们要实现一个功能：**用户可以提交一篇博客文章**。文章必须包含标题（`title`）和内容（`content`），还可以选择是否立即发布（`published`）。

在 FastAPI 中，定义"提交的数据长什么样"的最佳工具是 **Pydantic**。

> **Pydantic 是什么？** Pydantic 是一个 Python 库，专门用来定义数据模型和校验数据。你告诉它"这个字段必须是字符串，那个字段必须是整数"，它就在数据进来的时候自动帮你检查——不符合要求的直接拒绝，附上详细的错误原因。FastAPI 内置了 Pydantic 支持，不需要额外安装。

#### 2.1 新建 `schemas.py`

在 `blog_backend/` 目录下新建一个文件，命名为 `schemas.py`：

```python
from pydantic import BaseModel


class BlogCreate(BaseModel):
    title: str
    content: str
    published: bool = False
```

**逐行解释**：

- `from pydantic import BaseModel`：从 Pydantic 工具箱里拿出 `BaseModel` 这个"模板"。所有你定义的数据模型都要继承它。
- `class BlogCreate(BaseModel):`：定义一个叫 `BlogCreate` 的类，它**继承**了 `BaseModel`。继承的意思是：`BlogCreate` 自动拥有了 `BaseModel` 的所有能力（数据校验、类型转换、序列化等），同时你可以在里面添加自己的字段。
- `title: str`：声明 `title` 字段，类型是 `str`（字符串）。**这个字段是必填的**——如果请求里没有它，Pydantic 会报错。
- `content: str`：声明 `content` 字段，类型也是 `str`，同样是必填的。
- `published: bool = False`：声明 `published` 字段，类型是 `bool`（布尔值），**默认值是 `False`**。因为有默认值，这个字段是**可选**的——如果请求里没传它，Pydantic 会自动填上 `False`。

**比喻**：`BlogCreate` 就像一张"博客文章入库单"。入库单上印好了三个格子——标题、内容、是否发布。`title` 和 `content` 格子上盖了"必填"的红章，`published` 格子旁边用小字写着"不填默认 false"。

> **为什么叫 `BlogCreate` 而不是 `Blog`？** 命名约定：`BlogCreate` 表示"创建博客时用的数据结构"。等后续我们做数据库时，还会有 `BlogRead`（读取时返回的数据结构）、`BlogUpdate`（更新时用的数据结构）。不同的场景可能需要不同的字段组合，用名字区分清楚。

---

### 步骤 3：字段类型——告诉 Pydantic 你要什么

Pydantic 的核心能力是**类型校验**。你声明 `title: str`，Pydantic 就会确保收到的 `title` 真的是字符串。如果请求里传了 `"title": 123`（一个数字），Pydantic 会自动尝试转成字符串 `"123"`——转不了就报错。

常用的字段类型：

| 类型注解 | 含义 | 示例值 |
|----------|------|--------|
| `str` | 字符串 | `"Hello"` |
| `int` | 整数 | `42` |
| `float` | 浮点数 | `3.14` |
| `bool` | 布尔值 | `True` / `False` |
| `list[str]` | 字符串列表 | `["a", "b"]` |
| `str \| None` | 字符串或 `None`（可选） | `"Hello"` 或 `None` |

> `str | None` 是 Python 3.10+ 的新语法，等价于旧写法 `Optional[str]`。如果你用的是 Python 3.9 或更早，需要用 `from typing import Optional` 然后写 `Optional[str]`。本项目要求 Python 3.10+，所以直接用 `str | None` 就行。

---

### 步骤 4：可选字段与默认值

在 `BlogCreate` 中，`title` 和 `content` 是必填的，`published` 有默认值所以是可选的。但有时候你需要一个**真正的可选字段**——可以不传，传了就是字符串，不传就是 `None`。

```python
from pydantic import BaseModel


class BlogCreate(BaseModel):
    title: str
    content: str
    published: bool = False
    summary: str | None = None  # 真正的可选字段
```

**`summary: str | None = None` 拆开看**：

- `str | None`：这个字段可以是 `str` 类型，也可以是 `None`。
- `= None`：默认值是 `None`。请求里不传这个字段，Pydantic 就自动填 `None`。

**两种"可选"的区别**：

| 写法 | 含义 | 不传时的值 |
|------|------|-----------|
| `published: bool = False` | 可选，但有具体默认值 | `False` |
| `summary: str \| None = None` | 可选，没有就为空 | `None` |

> **什么时候用哪种？** 如果这个字段在业务上有一个合理的默认值（比如文章默认不发布），用 `= False`。如果这个字段"本来就可以没有"（比如摘要可以不写），用 `= None`。

---

### 步骤 5：在 `main.py` 中接入 POST 接口

模型定义好了，现在把它接到路由上。

#### 5.1 修改 `main.py`

打开 `blog_backend/main.py`，在原有代码基础上追加以下内容：

```python
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from blog_backend.schemas import BlogCreate  # 新增：导入刚刚定义的模型

app = FastAPI()


@app.get("/")
def read_root():
    return {"message": "Hello World"}


@app.get("/secret")
def secret_page():
    return JSONResponse(
        status_code=404,
        content={"error": "你找的秘密页面不存在！", "hint": "试试别的路径，比如 /"}
    )


# === 新增：POST 接口，用于创建博客文章 ===
@app.post("/blogs")
def create_blog(blog: BlogCreate):
    return {
        "message": "博客创建成功！",
        "title": blog.title,
        "content": blog.content,
        "published": blog.published,
    }
```

**逐行解释新增部分**：

- `from blog_backend.schemas import BlogCreate`：从你刚建的 `schemas.py` 中导入 `BlogCreate` 类。
- `@app.post("/blogs")`：和 `@app.get("/")` 是同一类东西，但这次是 **POST** 路由。意思是：当有人用 POST 方法访问 `/blogs` 时，调用下面这个函数。
- `def create_blog(blog: BlogCreate):`：注意参数 `blog: BlogCreate`——这是 FastAPI 的魔法所在。你告诉 FastAPI"这个参数的类型是 `BlogCreate`"，FastAPI 就会自动：
  1. 从请求体中读取 JSON 数据
  2. 用 Pydantic 校验数据是否符合 `BlogCreate` 的定义
  3. 校验通过后，把数据转换成一个 `BlogCreate` 实例，传给你的函数
  4. 校验不通过，自动返回 422 错误，附带详细原因

保存文件。因为开启了 `--reload`，服务器会自动重启。

---

### 步骤 6：用 curl 发 POST 请求

现在来实际测试。打开一个新终端（服务器终端不要关），输入：

```bash
curl -X POST http://127.0.0.1:8000/blogs \
  -H "Content-Type: application/json" \
  -d '{"title": "我的第一篇文章", "content": "这是正文内容。", "published": true}'
```

**逐行解释这条命令**：

- `curl -X POST`：`-X` 指定请求方法。默认是 GET，这里显式指定 POST。
- `http://127.0.0.1:8000/blogs`：请求的目标 URL。
- `-H "Content-Type: application/json"`：`-H` 是设置请求头。`Content-Type: application/json` 告诉服务器："我发的数据是 JSON 格式的，请按 JSON 来解析。"
- `-d '{"title": "我的第一篇文章", "content": "这是正文内容。", "published": true}'`：`-d` 是请求体（data）。这里放的就是 JSON 数据——三个字段：`title`、`content`、`published`。

**预期输出**：

```json
{"message":"博客创建成功！","title":"我的第一篇文章","content":"这是正文内容。","published":true}
```

**成功了！** 你发了一条 POST 请求，服务器收到了你的数据，解析、校验、返回了确认信息。

---

#### 6.1 测试可选字段：不传 `published`

```bash
curl -X POST http://127.0.0.1:8000/blogs \
  -H "Content-Type: application/json" \
  -d '{"title": "第二篇文章", "content": "没有 published 字段。"}'
```

**预期输出**：

```json
{"message":"博客创建成功！","title":"第二篇文章","content":"没有 published 字段。","published":false}
```

注意 `published` 自动变成了 `false`——这就是默认值在起作用。

#### 6.2 测试可选字段：不传 `summary`

因为我们还没有在接口中使用 `summary` 字段，先不测试。这部分留给你自己实验——在 `create_blog` 函数中加入 `"summary": blog.summary`，然后试试传和不传 `summary` 的区别。

---

### 步骤 7：FastAPI 自动校验——422 错误登场

Pydantic 最强大的地方不是"定义字段"，而是**自动校验**。我们来故意发一个错误请求，看看 FastAPI 怎么处理。

#### 7.1 故意缺少必填字段 `title`

```bash
curl -X POST http://127.0.0.1:8000/blogs \
  -H "Content-Type: application/json" \
  -d '{"content": "我忘了写标题！"}'
```

**预期输出**：

```json
{"detail":[{"type":"missing","loc":["body","title"],"msg":"Field required","input":{"content":"我忘了写标题！"}}]}
```

**逐行解读这个错误**：

- `"detail"`：错误详情，是一个数组（因为可能同时有多个错误）。
- `"type": "missing"`：错误类型是"缺少字段"。
- `"loc": ["body", "title"]`：出错位置——`body`（请求体）里的 `title` 字段。
- `"msg": "Field required"`：错误信息——这个字段是必填的。
- `"input": {"content": "我忘了写标题！"}`：显示你**实际传了什么**，方便你对比检查。

HTTP 状态码是 **422 Unprocessable Entity**（无法处理的实体）。用 `-v` 就能看到：

```bash
curl -v -X POST http://127.0.0.1:8000/blogs \
  -H "Content-Type: application/json" \
  -d '{"content": "我忘了写标题！"}'
```

输出中第一行响应：

```
< HTTP/1.1 422 Unprocessable Entity
```

> **422 是什么？** 422 属于 4xx 系列（客户端错误），意思是"我收到了你的请求，格式也对了，但数据本身有问题——比如缺少必填字段、字段类型不对"。和 400（Bad Request，请求格式就有问题）的区别在于：400 是"你的 JSON 我根本看不懂"，422 是"JSON 我看懂了，但里面的数据不符合要求"。

#### 7.2 故意传错字段类型

```bash
curl -X POST http://127.0.0.1:8000/blogs \
  -H "Content-Type: application/json" \
  -d '{"title": "类型错误测试", "content": 12345}'
```

注意 `content` 传了一个数字 `12345`，而不是字符串。

**预期输出**：Pydantic 会尝试将 `12345` 转成字符串 `"12345"`——对于 `int` → `str`，Pydantic 默认可以自动转换。所以这条请求**不会报错**，返回的 `content` 会是 `"12345"`（字符串）。

> 如果你传的是 `{"title": "测试", "content": [1, 2, 3]}`（一个列表），Pydantic 就转不了了，会返回 422 错误。

#### 7.3 故意传一个不存在的字段

```bash
curl -X POST http://127.0.0.1:8000/blogs \
  -H "Content-Type: application/json" \
  -d '{"title": "多了个字段", "content": "正文", "author": "张三"}'
```

注意 `author` 字段在 `BlogCreate` 里不存在。

**预期输出**：**默认情况下，请求会成功，多余的 `author` 字段会被忽略。** 这是 FastAPI/Pydantic 的默认行为——它只处理你声明过的字段，多余的不报错、不处理、直接丢掉。

> 如果你希望多余的字段也报错，可以在 `BlogCreate` 类上加上配置。这不是本章重点，但你可以记住：`class BlogCreate(BaseModel):` 后面加 `model_config = {"extra": "forbid"}` 就能禁止多余字段。

---

### ❌ 常见错误 → ✅ 正确示例

> **错误 1：Content-Type 没设或设错**

❌ 错误示例：

```bash
curl -X POST http://127.0.0.1:8000/blogs \
  -d '{"title": "测试", "content": "正文"}'
```

忘了加 `-H "Content-Type: application/json"`。

**服务器返回**：

```
{"detail":[{"type":"model_attributes_type","loc":["body"],"msg":"Input should be a valid dictionary or object to extract fields from","input":"{\"title\": \"测试\", \"content\": \"正文\"}"}]}
```

状态码是 **422**（不是 415！）。这是因为 FastAPI 默认期望 JSON 格式的请求体，但你没有声明 `Content-Type`，它可能把整个请求体当成一个字符串来解析，导致 Pydantic 校验失败。

> **注意**：有些版本的 curl 在不指定 `Content-Type` 时会自动设置 `Content-Type: application/x-www-form-urlencoded`，这会导致 FastAPI 返回 **415 Unsupported Media Type**。两种情况本质上都是同一个问题：服务器不知道你发的是 JSON。

✅ 正确示例：

```bash
curl -X POST http://127.0.0.1:8000/blogs \
  -H "Content-Type: application/json" \
  -d '{"title": "测试", "content": "正文"}'
```

---

> **错误 2：JSON 里的 key 名和 Pydantic 字段名不匹配**

❌ 错误示例：

```bash
curl -X POST http://127.0.0.1:8000/blogs \
  -H "Content-Type: application/json" \
  -d '{"Title": "标题", "Content": "正文"}'
```

注意：`Title` 和 `Content` 首字母大写了，但 `BlogCreate` 里定义的是小写的 `title` 和 `content`。

**服务器返回**：422 错误，提示 `title` 字段缺失（因为 `Title` 不等于 `title`）。

✅ 正确示例：

```bash
curl -X POST http://127.0.0.1:8000/blogs \
  -H "Content-Type: application/json" \
  -d '{"title": "标题", "content": "正文"}'
```

**JSON 的 key 名必须和 Pydantic 字段名完全一致（大小写敏感）。**

---

> **错误 3：忘记 import BaseModel**

❌ 错误示例：

```python
# schemas.py —— 报错！
class BlogCreate(BaseModel):  # NameError: name 'BaseModel' is not defined
    title: str
    content: str
```

✅ 正确示例：

```python
from pydantic import BaseModel  # 这一行必须有！


class BlogCreate(BaseModel):
    title: str
    content: str
    published: bool = False
```

---

### 🤔 想多一点：Pydantic 的校验发生在哪一步？

你发了一个 POST 请求，请求到达服务器后，FastAPI 内部经历了以下流程：

```
请求进来（POST /blogs，JSON body）
    │
    ▼
1. 路由匹配
   FastAPI 查路由表，找到匹配的路径 `/blogs` 和方法 POST
   如果找不到 → 404
    │
    ▼
2. 请求体解析
   FastAPI 读取请求头里的 Content-Type，确定数据格式（JSON）
   如果 Content-Type 不对 → 415
    │
    ▼
3. Pydantic 校验 ← 这就是我们本章学的部分！
   FastAPI 看你的函数签名：create_blog(blog: BlogCreate)
   它知道："哦，我需要把请求体转成 BlogCreate 类型"
   于是调用 Pydantic 的校验逻辑：
     - 字段 title 存在吗？类型是 str 吗？→ 不存在就报 422
     - 字段 content 存在吗？类型是 str 吗？→ 不存在就报 422
     - 字段 published 呢？→ 没传就用默认值 False
     - 有多余字段吗？→ 忽略
   如果任何校验失败 → 422，附带详细错误信息
    │
    ▼
4. 进入函数
   校验全部通过，Pydantic 把 JSON 转成一个 BlogCreate 实例
   比如：blog = BlogCreate(title="我的第一篇文章", content="...", published=True)
   这个实例被传入你的 create_blog 函数
    │
    ▼
5. 函数执行
   你的代码逻辑跑起来，返回结果
    │
    ▼
6. 返回响应
   FastAPI 把你的 return 值转成 JSON，返回给客户端
```

**关键洞察**：Pydantic 校验发生在**你的函数被调用之前**。这意味着你的函数永远收不到"脏数据"——当你写 `blog.title` 时，你可以百分之百确定它是一个字符串，不需要在函数里再写 `if not isinstance(blog.title, str)` 这种防御代码。

**这不是"安全网"，而是"安检门"**——不合格的数据根本进不了你的函数。网是兜住掉下来的人，安检门是直接不让人进。Pydantic 是安检门。

---

### 步骤 8：在 Swagger 文档中测试 POST 接口

打开浏览器，访问 `http://127.0.0.1:8000/docs`。

你会看到 Swagger 页面上多了一个新的接口：**`POST /blogs Create Blog`**。

1. 点击展开这个接口
2. 点击 **"Try it out"** 按钮
3. 在 Request body 区域，把示例 JSON 改成你自己的数据：

```json
{
  "title": "Swagger 测试文章",
  "content": "这是通过 Swagger 创建的。",
  "published": false
}
```

4. 点击 **"Execute"** 按钮

你会看到和 curl 一样的结果——返回 200，`message` 显示"博客创建成功！"。Swagger 不仅是一个文档查看器，更是一个**可以直接调用接口的测试工具**。这也是为什么 FastAPI 被称为"自带交互式文档"的框架。

---

## 四、完整代码清单

### `blog_backend/schemas.py`（新建文件）

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


@app.get("/")
def read_root():
    return {"message": "Hello World"}


@app.get("/secret")
def secret_page():
    return JSONResponse(
        status_code=404,
        content={"error": "你找的秘密页面不存在！", "hint": "试试别的路径，比如 /"}
    )


@app.post("/blogs")
def create_blog(blog: BlogCreate):
    return {
        "message": "博客创建成功！",
        "title": blog.title,
        "content": blog.content,
        "published": blog.published,
    }
```

---

## 五、验证方法

在终端中依次执行以下命令，确认一切正常：

```bash
# 1. 正常 POST 请求（三个字段都传）
curl -X POST http://127.0.0.1:8000/blogs \
  -H "Content-Type: application/json" \
  -d '{"title": "验证测试", "content": "测试正文", "published": true}'

# 2. 缺少必填字段 title → 应返回 422
curl -X POST http://127.0.0.1:8000/blogs \
  -H "Content-Type: application/json" \
  -d '{"content": "没有标题"}' -w "\nHTTP Status: %{http_code}\n"

# 3. 不传可选字段 published → 应返回 published: false
curl -X POST http://127.0.0.1:8000/blogs \
  -H "Content-Type: application/json" \
  -d '{"title": "可选字段测试", "content": "不传 published"}'

# 4. 请求一个不存在的路径 → 应返回 404
curl -X POST http://127.0.0.1:8000/nonexistent \
  -H "Content-Type: application/json" \
  -d '{"title": "测试"}'
```

你应该看到：
- 第一条返回 `200` + `{"message":"博客创建成功！","title":"验证测试",...}`
- 第二条返回 `422` + 错误详情，指出 `title` 字段缺失
- 第三条返回 `200` + `"published": false`（默认值生效）
- 第四条返回 `404` + `{"detail":"Not Found"}`

四条全部通过，本章完成。

---

## 六、小结

| 你学到了什么 | 一句话总结 |
|--------------|-----------|
| GET vs POST | GET 是"给我看看"（数据不变），POST 是"帮我存下来"（数据会变） |
| 请求体（Request Body） | POST 请求里夹带的数据，装在请求体里，URL 上看不到 |
| Pydantic BaseModel | 定义数据模型的模板，继承它就能自动获得校验能力 |
| 字段类型声明 | `title: str` 和 `content: str` 是必填字段，`published: bool = False` 有默认值所以可选 |
| `str \| None = None` | 真正的可选字段——不传就是 `None`，传了必须是字符串 |
| 422 错误 | "数据我看懂了，但不符合要求"——缺少必填字段、类型不对等 |
| Content-Type 请求头 | 告诉服务器"我发的是 JSON 格式"，不设会导致解析失败 |
| Pydantic 校验时机 | 发生在函数被调用之前——"安检门"不是"安全网" |
| Swagger 测试 POST | 在 `/docs` 页面可以直接填 JSON 测试 POST 接口 |

---

## 七、术语附录

| 术语 | 英文 | 通俗解释 | 本章出现位置 |
|------|------|----------|-------------|
| 请求体 | Request Body | HTTP 请求的第四部分（前三部分是 URL、方法、请求头），装着 POST/PUT 请求要提交的数据。GET 请求通常没有请求体。**字面陷阱**：它不是"请求的身体"——"body"在这里是"主体内容"的意思。 | 步骤 1 |
| Pydantic | — | 一个 Python 数据校验库，FastAPI 内置支持。你定义数据模型（字段名 + 类型），它自动校验收到的数据是否符合要求。名字来源于"pedantic"（学究气的、一丝不苟的），暗示它"对数据格式非常较真"。 | 步骤 2 |
| BaseModel | — | Pydantic 提供的基础类，所有你定义的数据模型都要继承它。继承之后，你的类就自动拥有了数据校验、类型转换、序列化等能力。 | 步骤 2 |
| 422 错误 | 422 Unprocessable Entity | HTTP 状态码，属于 4xx（客户端错误）。意思是"请求格式没问题，但数据内容不符合要求"——比如缺少必填字段、字段类型不对。 | 步骤 7 |
| Content-Type | — | 一个 HTTP 请求头，用来告诉服务器"我发的数据是什么格式"。发 JSON 数据时必须设为 `application/json`，否则服务器不知道怎么解析。 | 步骤 6 |
| 数据校验 | Data Validation | 检查输入数据是否符合预期规则的过程。比如：必填字段有没有填？字符串字段是不是真的字符串？Pydantic 帮你自动完成这个检查，不需要你手动写 `if` 判断。 | 步骤 7 |

---

## 八、已知坑点与禁止事项

| 坑点 | 现象 | 原因 | 解决 |
|------|------|------|------|
| 忘设 `Content-Type` | 返回 422 或 415 错误 | 服务器不知道你发的是 JSON，无法正确解析 | 加上 `-H "Content-Type: application/json"` |
| JSON key 和字段名大小写不一致 | 返回 422，提示字段缺失 | JSON 的 key 是大小写敏感的，`Title` ≠ `title` | 确保 JSON key 名和 Pydantic 字段名完全一致（包括大小写） |
| 忘记 `from pydantic import BaseModel` | `NameError: name 'BaseModel' is not defined` | 用了 `BaseModel` 但没导入 | 在 `schemas.py` 顶部加上 `from pydantic import BaseModel` |
| `curl` 里换行符导致命令中断 | Windows PowerShell 中 `\` 续行符可能不生效 | PowerShell 的续行符是 `` ` ``（反引号），不是 `\` | 把整条命令写成一行，或用 PowerShell 的 `` ` `` 续行 |
| 在函数里又手动校验了一遍数据 | 代码里出现 `if blog.title is None` 之类的检查 | 不信任 Pydantic 的校验能力，写重复代码 | Pydantic 校验通过后才进入函数，函数里不需要再校验 |

---

## 九、下一步建议

你已经掌握了 FastAPI 最核心的两个能力：**GET 读取数据**和**POST 提交数据**。接下来：

- **下一章**：[07-路径参数与查询参数](07-路径参数与查询参数.md)——学习如何让 URL 更灵活，比如 `/blogs/5` 获取第 5 篇文章、`/blogs?page=2` 分页查询。
- **延伸实验**：试试在 `BlogCreate` 中加更多字段类型（`int`、`list[str]`、嵌套的 Pydantic 模型），用 curl 测试各种正确和错误的输入，观察 Pydantic 的校验反馈。

---

> [可暂停点 3/9]：POST 请求基础已完成。你已经能提交数据到服务器了。下次从 [07-路径参数与查询参数](07-路径参数与查询参数.md) 继续。