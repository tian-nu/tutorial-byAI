# 04-返回 JSON

- 对应文档版本：首版教程
- 适用环境：Python 3.10+, FastAPI 0.100+, Windows/macOS/Linux
- 读者角色：后端初学者
- 预计耗时：新手 40 分钟 / 熟手 15 分钟
- 前置教程：[03-什么是 API：请求与响应](./03-什么是API：请求与响应/)
- 可视化：无

---

## 一、目标与完成效果

**一句话目标**：学会用 FastAPI 返回 JSON 格式的数据——包括单个对象、对象列表，并用 Pydantic 模型让接口自动生成文档。

**完成后的可观测效果**：
- 你访问 `http://127.0.0.1:8000/posts/1`，浏览器返回一个包含标题、内容、作者、日期等字段的博客文章（JSON 格式）。
- 你访问 `http://127.0.0.1:8000/posts`，浏览器返回一个包含多篇文章的 JSON 数组。
- 你打开 `/docs`，在 Swagger 页面上能看到每个接口的"返回数据长什么样"——字段名、类型、是否必填，一目了然。
- 你故意返回一个 Python 的 `datetime` 对象，亲眼看到报错信息，然后学会用正确的方式修复。

---

## 二、前置条件

| 序号 | 条件 | 验证命令 |
|------|------|----------|
| 1 | 已完成教程 03，`main.py` 能跑起来 | 浏览器访问 `http://127.0.0.1:8000` 返回 JSON |
| 2 | 服务器正在运行（`uvicorn blog_backend.main:app --reload`） | 终端里能看到 `Uvicorn running on http://127.0.0.1:8000` |
| 3 | 理解 HTTP 请求和响应的基本概念（GET、状态码、响应体） | 能说出 200 和 404 的区别 |
| 4 | 知道 Python 的 `dict`（字典）和 `list`（列表）怎么用 | `{"name": "小明"}` 和 `["a", "b", "c"]` 能看懂 |

**一条命令确认前置满足**：

```powershell
curl http://127.0.0.1:8000
```

如果返回 `{"message":"Hello World"}`，前置条件满足。

---

## 三、分步操作

### 步骤 1：JSON 是什么？——从 Python 字典到"通用语言"

在上一章，你的接口返回了 `{"message": "Hello World"}`。你看到这一对花括号 `{}` 和一个冒号 `:`，第一反应可能是："这不就是 Python 字典吗？"

**长得像，但不是同一个东西。** 我们先把这事说清楚。

#### 1.1 JSON 和 Python dict 的"血缘关系"

JSON 的全称是 **JavaScript Object Notation**（JavaScript 对象表示法）。它出生在 JavaScript 的世界里，但因为长得太像各种语言里的"键值对"数据结构，后来成了所有编程语言通用的数据交换格式。

把 Python dict 和 JSON 放在一起看：

| 对比维度 | Python dict | JSON |
|----------|-------------|------|
| **样子** | `{"name": "小明", "age": 18}` | `{"name": "小明", "age": 18}` |
| **本质** | Python 内存里的一个**数据结构**，你可以对它做 `.keys()`、`.items()` 等操作 | 一个**字符串**，纯文本，可以被任何语言读取 |
| **key 的引号** | 单引号或双引号都行：`{'name': '小明'}` 也合法 | **必须用双引号**：`{"name": "小明"}` ✅，`{'name': '小明'}` ❌ |
| **值的类型** | 支持 Python 特有的类型（`datetime`、`Decimal`、自定义类等） | 只支持 6 种类型：字符串、数字、布尔值、null、数组、对象 |
| **最后一个元素后面** | 可以加逗号：`{"a": 1,}` ✅ | 不能加逗号：`{"a": 1,}` ❌ |
| **注释** | 不能有注释 | 不能有注释 |

**关键区别**：Python dict 是"活的数据结构"，你可以在 Python 代码里操作它；JSON 是"死的字符串"，它就是一串文本，需要被**解析**（parse）之后才能变成某个语言的数据结构。

> **比喻**：Python dict 是你厨房里活蹦乱跳的食材（可以切、可以炒、可以调味），JSON 是把这些食材拍成照片发到外卖平台上的菜单（任何人看到这张照片都能知道有什么食材，但照片本身不能吃）。

#### 1.2 JSON 支持的 6 种数据类型

```json
{
  "字符串": "hello world",
  "数字": 42,
  "浮点数": 3.14,
  "布尔值": true,
  "空值": null,
  "数组": ["苹果", "香蕉", "橘子"],
  "嵌套对象": {
    "内层键": "内层值"
  }
}
```

注意 JSON 的 `true`、`false`、`null` 是**全小写**，而 Python 是 `True`、`False`、`None`（首字母大写）。这是一个高频易错点。

#### 1.3 JSON 数组 = Python list

JSON 的数组用方括号 `[]`，里面放逗号分隔的值：

```json
[
  {"id": 1, "title": "第一篇文章"},
  {"id": 2, "title": "第二篇文章"},
  {"id": 3, "title": "第三篇文章"}
]
```

这在 Python 里对应 `list[dict]`——一个列表，里面每个元素是一个字典。

> **一句话总结**：把 JSON 想象成"全球通用的数据集装箱"——不管你是 Python、Java、Go 还是 JavaScript，只要你把数据装进这个集装箱，任何人都能打开它，知道里面装了什么。

---

### 🤔 想多一点：JSON 的 key 为什么必须用双引号？

你可能会想：Python 明明支持单引号 `{'name': '小明'}`，JSON 凭什么不行？

**历史原因**：JSON 脱胎于 JavaScript 的对象字面量语法。在 JavaScript 里，字符串可以用单引号也可以用双引号，但 JSON 的创造者 Douglas Crockford 在设计 JSON 时做了一个"简化决策"——**只允许双引号**。这样做的好处是：

1. **解析器更简单**：只要看到双引号就知道是字符串，不用区分单引号还是双引号。
2. **避免歧义**：英文中单引号常用作撇号（如 `can't`、`it's`），如果 JSON 允许单引号，解析器就得分清"这个单引号是字符串边界还是英文缩写"。
3. **跨语言一致**：有些语言（如 Java）的字符串只能用双引号，JSON 统一用双引号避免了语言差异。

**这就引出了 JSON 的设计哲学**：JSON 宁可功能少一点，也要保证**简单、无歧义、到处都能用**。它只支持 6 种类型，不支持注释，不允许尾随逗号——所有这些"限制"都是为了同一个目的：**让 JSON 解析器足够简单，任何语言都能在几行代码里实现它。**

---

### 步骤 2：为什么后端都用 JSON 做"通用语言"？

在 JSON 诞生之前，后端之间传数据用什么？**XML**。长这样：

```xml
<post>
  <id>1</id>
  <title>我的第一篇文章</title>
  <content>今天天气真好。</content>
</post>
```

XML 本身没问题，但它有两个致命缺点：
- **啰嗦**：每个字段都要写两遍——开始标签和结束标签。上面 4 个字段，XML 写了 8 行（包含根标签），JSON 只需要 4 行。
- **不是原生数据结构**：XML 解析出来是一个"文档树"，你还要手动把它映射成你语言里的字典或对象。JSON 解析出来直接就是字典/对象——对 JavaScript 来说甚至不需要解析，`JSON.parse()` 一行搞定。

**JSON 赢在三个字：刚刚好。** 它只有 6 种类型，但覆盖了 99% 的数据传输需求。它不啰嗦，但人类还能读。它没有 XML 的复杂（命名空间、属性、CDATA……），但表达能力足够。

| 数据格式 | 人类可读 | 解析复杂度 | 数据体积 | 跨语言 |
|----------|----------|-----------|----------|--------|
| JSON | ✅ 好 | 低 | 小 | ✅ 所有语言 |
| XML | ✅ 可以 | 中 | 大 | ✅ 所有语言 |
| Python pickle | ❌ 二进制 | 低 | 小 | ❌ 只有 Python |
| Protobuf | ❌ 二进制 | 中 | 极小 | ✅ 大部分语言 |

> **对于后端的实际意义**：你用 Python 写后端，你同事用 Java 写后端，前端同学用 JavaScript 写页面，手机 App 用 Swift/Kotlin 写——这四种语言唯一能直接沟通的数据格式就是 JSON。你返回一个 Python dict，FastAPI 自动把它变成 JSON 字符串，前端的 JavaScript 收到后自动变成 JS 对象——**整个过程你不需要写一行转换代码。**

---

### 步骤 3：FastAPI 自动序列化——你返回 dict，它帮你转 JSON

**序列化（Serialization）** 这个词听起来吓人，其实非常简单：

> **序列化 = 把内存里的数据结构，变成可以传输的字符串（JSON 字符串）。**

就像你搬家时，把衣柜（内存里的 Python dict）拆成木板（JSON 字符串），装进货车（HTTP 响应体），运到新家（浏览器），再拼回衣柜（浏览器把 JSON 解析成 JavaScript 对象）。

**FastAPI 的自动序列化意味着什么？** 你只需要在函数里 `return` 一个 Python dict，FastAPI 会自动帮你做三件事：

1. 把 Python dict 转成 JSON 字符串
2. 设置响应头 `Content-Type: application/json`
3. 把 JSON 字符串放进响应体，发回给客户端

**你什么都不用做。** 不需要 `import json`，不需要 `json.dumps()`，不需要手动设置响应头。这就是 FastAPI 的核心理念：**你只写业务逻辑，框架帮你处理所有"翻译"工作。**

我们来验证一下。确保你的 `main.py` 目前是教程 03 结束时的状态：

```python
from fastapi import FastAPI
from fastapi.responses import JSONResponse

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
```

用 `curl -v` 看一下响应头：

```bash
curl -v http://127.0.0.1:8000/
```

你会看到响应头里有一行：

```
< content-type: application/json
```

这一行就是你**什么都没做**，FastAPI 自动帮你加上的。它告诉客户端："我返回的是 JSON，请按 JSON 来解析。"

---

### 步骤 4：返回一个博客文章对象

现在我们终于要写点"有内容"的东西了。你的博客后端，至少得能返回一篇文章吧？

#### 4.1 定义文章数据

打开 `blog_backend/main.py`，在现有代码后面添加以下内容：

```python
# === 模拟数据：一篇文章 ===
sample_post = {
    "id": 1,
    "title": "FastAPI 入门指南",
    "content": "今天我们来学习如何使用 FastAPI 构建后端服务。FastAPI 是一个现代、高性能的 Python Web 框架……",
    "author": "小明",
    "created_at": "2026-06-01",
    "published": True,
    "tags": ["Python", "FastAPI", "后端"]
}


@app.get("/posts/1")
def get_post():
    return sample_post
```

保存文件。服务器会自动重启（因为你有 `--reload`）。

#### 4.2 验证

浏览器访问 `http://127.0.0.1:8000/posts/1`：

```json
{"id":1,"title":"FastAPI 入门指南","content":"今天我们来学习如何使用 FastAPI 构建后端服务。FastAPI 是一个现代、高性能的 Python Web 框架……","author":"小明","created_at":"2026-06-01","published":true,"tags":["Python","FastAPI","后端"]}
```

**你做了什么？** 你定义了一个 Python dict（`sample_post`），里面包含了一篇博客文章的所有字段：标题、内容、作者、日期、是否发布、标签。然后你在函数里 `return` 了这个 dict，FastAPI 自动把它转成了 JSON。

**观察几个细节**：
- `published: True`（Python 的 `True`，首字母大写）→ 到了 JSON 里变成了 `true`（全小写）。FastAPI 自动帮你做了这个转换。
- `tags` 是一个 Python list → 到了 JSON 里变成了 JSON 数组 `["Python", "FastAPI", "后端"]`。
- 中文字符正常显示，没有乱码。FastAPI 默认使用 UTF-8 编码。

> **比喻**：你（厨师）在后厨准备了一盘菜——一个 Python dict。FastAPI（服务员）接过这盘菜，把它装进一个标准外卖盒（JSON 字符串），贴上标签（`Content-Type: application/json`），然后端给客人（浏览器）。客人打开盒子，看到的就是 JSON 格式的数据。

---

### 步骤 5：返回一个博客文章列表

一篇文章不够，真实的博客需要返回多篇文章。

#### 5.1 定义文章列表

在 `main.py` 中继续添加：

```python
# === 模拟数据：多篇文章 ===
sample_posts = [
    {
        "id": 1,
        "title": "FastAPI 入门指南",
        "content": "今天我们来学习如何使用 FastAPI 构建后端服务……",
        "author": "小明",
        "created_at": "2026-06-01",
        "published": True,
        "tags": ["Python", "FastAPI", "后端"]
    },
    {
        "id": 2,
        "title": "Python 字典和 JSON 的关系",
        "content": "很多初学者搞不清 Python dict 和 JSON 的区别……",
        "author": "小红",
        "created_at": "2026-06-02",
        "published": True,
        "tags": ["Python", "JSON", "基础"]
    },
    {
        "id": 3,
        "title": "为什么选择 FastAPI？",
        "content": "在众多 Python Web 框架中，FastAPI 凭借其性能和易用性脱颖而出……",
        "author": "小明",
        "created_at": "2026-06-03",
        "published": False,
        "tags": ["FastAPI", "对比", "选型"]
    }
]


@app.get("/posts")
def get_posts():
    return sample_posts
```

保存文件。

#### 5.2 验证

浏览器访问 `http://127.0.0.1:8000/posts`：

```json
[{"id":1,"title":"FastAPI 入门指南","content":"今天我们来学习如何使用 FastAPI 构建后端服务……","author":"小明","created_at":"2026-06-01","published":true,"tags":["Python","FastAPI","后端"]},{"id":2,"title":"Python 字典和 JSON 的关系","content":"很多初学者搞不清 Python dict 和 JSON 的区别……","author":"小红","created_at":"2026-06-02","published":true,"tags":["Python","JSON","基础"]},{"id":3,"title":"为什么选择 FastAPI？","content":"在众多 Python Web 框架中，FastAPI 凭借其性能和易用性脱颖而出……","author":"小明","created_at":"2026-06-03","published":false,"tags":["FastAPI","对比","选型"]}]
```

你这次 `return` 的是一个 `list[dict]`（Python 列表，里面是字典）。FastAPI 自动把它转成了 JSON 数组。

**对比两个接口**：

| 接口 | 路径 | 返回类型 | Python 类型 | JSON 类型 |
|------|------|----------|-------------|-----------|
| 单篇文章 | `/posts/1` | 一个文章对象 | `dict` | JSON 对象 `{}` |
| 文章列表 | `/posts` | 多个文章对象 | `list[dict]` | JSON 数组 `[{}, {}, {}]` |

> **注意路径设计**：`/posts/1` 和 `/posts` 是两个不同的路径，对应两个不同的接口。`/posts` 返回全部文章，`/posts/1` 返回 id 为 1 的那篇文章。这是一种常见的 RESTful API 设计惯例。

---

### 步骤 6：用 `response_model` 让 Swagger 自动生成文档

到目前为止，你的接口返回了数据，但 Swagger 文档（`/docs`）里看不到这些数据"长什么样"——它只显示返回类型是"unknown"。

要让 Swagger 知道你返回的数据结构，你需要用 **Pydantic 模型** 配合 `response_model`。

#### 6.1 什么是 Pydantic？

**Pydantic** 是一个 Python 库，专门用来**定义数据模型**。你定义一个类，继承自 `pydantic.BaseModel`，在里面声明字段和类型——Pydantic 就能自动做数据校验、类型转换、生成文档。

> **比喻**：Pydantic 模型就像你餐厅的"标准菜谱"。菜谱上写了每道菜的名字、食材、分量——厨师（你的代码）必须按菜谱做菜，服务员（FastAPI）会按菜谱给客人介绍菜品。如果厨师做出来的菜不符合菜谱，服务员会拒绝上菜。

#### 6.2 定义 Pydantic 模型

在 `main.py` 最上面的 import 区域，添加 `pydantic` 的导入，然后定义模型：

```python
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional

app = FastAPI()


# === Pydantic 模型：定义文章数据结构 ===
class Post(BaseModel):
    id: int
    title: str
    content: str
    author: str
    created_at: str
    published: bool
    tags: list[str]
```

**逐行解释**：

- `class Post(BaseModel):`——定义一个叫 `Post` 的类，继承自 `BaseModel`。`BaseModel` 是 Pydantic 提供的"菜谱模板"，继承它之后，这个类就自动获得了数据校验和文档生成的能力。
- `id: int`——声明 `id` 字段，类型是 `int`（整数）。如果传进来的数据里 `id` 是字符串 `"1"`，Pydantic 在大多数情况下会自动转成整数 `1`。
- `title: str`——声明 `title` 字段，类型是 `str`（字符串）。
- `tags: list[str]`——声明 `tags` 字段，类型是"字符串列表"。`list[str]` 是 Python 3.9+ 的写法，表示"列表里的每个元素都是字符串"。

> ⚠️ **`list[str]` 需要 Python 3.9+**。如果你用的是 Python 3.8 或更早版本，需要写成 `from typing import List` 然后 `tags: List[str]`。本教程假定 Python 3.10+，所以直接用 `list[str]`。

#### 6.3 在接口上使用 `response_model`

修改你的两个接口，加上 `response_model` 参数：

```python
@app.get("/posts/1", response_model=Post)
def get_post():
    return sample_post


@app.get("/posts", response_model=list[Post])
def get_posts():
    return sample_posts
```

**关键点**：
- 单篇文章：`response_model=Post`——告诉 FastAPI "这个接口返回的数据符合 `Post` 模型的结构"。
- 文章列表：`response_model=list[Post]`——告诉 FastAPI "这个接口返回一个列表，列表里的每个元素都符合 `Post` 模型的结构"。

#### 6.4 见证奇迹：打开 Swagger 文档

保存文件，等服务器重启，然后访问 `http://127.0.0.1:8000/docs`。

展开 `GET /posts/1`，你会看到 **Response** 区域现在显示了一个完整的 Schema（数据模式）：

```
{
  "id": 0,
  "title": "string",
  "content": "string",
  "author": "string",
  "created_at": "string",
  "published": true,
  "tags": ["string"]
}
```

**你什么都没写，Swagger 自动生成了返回数据的结构文档。** 这就是 `response_model` 的魔力——你在 Pydantic 模型里声明了字段和类型，FastAPI 自动把它们转成 Swagger 文档。

> **对比没有 `response_model` 的时候**：Swagger 只显示返回类型是"unknown"，前端同学不知道你会返回什么字段、每个字段是什么类型。他们只能"猜"或者翻你的代码。有了 `response_model`，文档就是"活"的——你改模型，文档自动更新，永远不会过期。

---

### 🤔 想多一点：`response_model` 的两个隐藏功能

你可能觉得 `response_model` 就是用来生成文档的。实际上它做了两件更重要的事：

**1. 数据过滤**

假设你的 `sample_post` 里有一个"内部备注"字段 `internal_note`，你不想暴露给前端。只要你的 `Post` 模型里不声明 `internal_note` 字段，FastAPI 就会**自动过滤掉它**——返回的 JSON 里不会包含这个字段。

```python
# 模拟数据里有额外字段
sample_post = {
    "id": 1,
    "title": "FastAPI 入门指南",
    "internal_note": "这篇需要审核"  # 不想暴露给前端
}

# 但 Post 模型里没有 internal_note
class Post(BaseModel):
    id: int
    title: str
    # ... 其他字段，没有 internal_note

# 返回时，internal_note 会被自动过滤掉
```

**2. 数据校验**

如果你 `return` 的数据里，某个字段的类型和模型声明不一致，FastAPI 会报错。比如 `id` 声明为 `int`，但你返回了 `"不是数字"`——FastAPI 在返回数据之前会先校验，发现问题就报错。这确保了你的 API 不会"不小心"返回格式错误的数据。

> **这两个功能合在一起，让 `response_model` 成为了一道"出站防火墙"**——所有从你后端出去的数据，都会被这道防火墙检查一遍：格式对不对、有没有不该暴露的字段。相当于你餐厅的"出菜口"——不符合标准的菜，端不出去。

---

### 步骤 7：❌ 常见错误 —— 返回 Python 对象导致序列化失败

这是一个**新手必踩的坑**，我们先踩为敬。

#### 7.1 制造错误

在 `main.py` 中添加以下代码（**不要保存运行**，先看）：

```python
from datetime import datetime


@app.get("/server-time")
def get_server_time():
    return {"current_time": datetime.now()}
```

保存文件，访问 `http://127.0.0.1:8000/server-time`。

你会看到类似这样的错误信息（在浏览器或终端里）：

```
TypeError: Object of type datetime is not JSON serializable
```

或者 FastAPI 返回一个 500 错误，终端里打印出详细的 traceback。

#### 7.2 为什么会报错？

回到步骤 1 的表格：JSON 只支持 6 种数据类型——字符串、数字、布尔值、null、数组、对象。

`datetime` 是 Python 特有的类型，JSON 不认识它。FastAPI 的序列化器（底层是 `json.dumps()`）在尝试把 `datetime` 转成 JSON 时，发现不认识这个类型，于是抛出了异常。

**这不只是 `datetime` 的问题**。以下 Python 类型也没法直接塞进 JSON：

| Python 类型 | 示例 | 为什么不行 |
|-------------|------|-----------|
| `datetime` | `datetime.now()` | JSON 没有"日期时间"类型 |
| `Decimal` | `Decimal("3.14")` | JSON 没有"精确小数"类型 |
| `set` | `{1, 2, 3}` | JSON 没有"集合"类型 |
| 自定义类实例 | `MyClass()` | JSON 不认识你的自定义类 |
| `bytes` | `b"hello"` | JSON 不能直接放二进制数据 |

#### 7.3 ✅ 正确做法一：用 `str()` 转换

最简单的修复——把 `datetime` 转成字符串：

```python
from datetime import datetime


@app.get("/server-time")
def get_server_time():
    return {"current_time": str(datetime.now())}
```

保存，访问 `http://127.0.0.1:8000/server-time`：

```json
{"current_time": "2026-06-05 14:30:22.123456"}
```

不报错了！但字符串格式不太好看，而且前端拿到之后还得自己解析。我们可以用 `isoformat()` 输出标准格式：

```python
@app.get("/server-time")
def get_server_time():
    return {"current_time": datetime.now().isoformat()}
```

```json
{"current_time": "2026-06-05T14:30:22.123456"}
```

ISO 8601 格式（`YYYY-MM-DDTHH:MM:SS`）是国际标准，前端、数据库、其他语言都能识别。

#### 7.4 ✅ 正确做法二：用 Pydantic 模型（推荐）

Pydantic 模型天然支持 `datetime` 类型，它会自动帮你序列化：

```python
from datetime import datetime
from pydantic import BaseModel


class TimeResponse(BaseModel):
    current_time: datetime


@app.get("/server-time", response_model=TimeResponse)
def get_server_time():
    return TimeResponse(current_time=datetime.now())
    # 或者更简单：
    # return {"current_time": datetime.now()}
```

Pydantic 会自动把 `datetime` 转成 ISO 8601 字符串，不需要你手动 `str()` 或 `isoformat()`。

> **原则**：只要你的接口返回的是 Pydantic 模型（通过 `response_model` 指定），Pydantic 支持的类型（`datetime`、`UUID`、`Decimal` 等）都能自动序列化。如果你返回的是裸 dict（没有 `response_model`），那就只能用 JSON 原生支持的 6 种类型。

---

### 步骤 8：最终代码 vs 你的代码

至此，你的 `main.py` 应该包含以下所有内容。我们按功能分块展示：

**（1）导入和初始化**

```python
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from datetime import datetime

app = FastAPI()
```

**（2）Pydantic 模型**

```python
class Post(BaseModel):
    id: int
    title: str
    content: str
    author: str
    created_at: str
    published: bool
    tags: list[str]


class TimeResponse(BaseModel):
    current_time: datetime
```

**（3）模拟数据**

```python
sample_post = {
    "id": 1,
    "title": "FastAPI 入门指南",
    "content": "今天我们来学习如何使用 FastAPI 构建后端服务。FastAPI 是一个现代、高性能的 Python Web 框架……",
    "author": "小明",
    "created_at": "2026-06-01",
    "published": True,
    "tags": ["Python", "FastAPI", "后端"]
}

sample_posts = [
    {
        "id": 1,
        "title": "FastAPI 入门指南",
        "content": "今天我们来学习如何使用 FastAPI 构建后端服务……",
        "author": "小明",
        "created_at": "2026-06-01",
        "published": True,
        "tags": ["Python", "FastAPI", "后端"]
    },
    {
        "id": 2,
        "title": "Python 字典和 JSON 的关系",
        "content": "很多初学者搞不清 Python dict 和 JSON 的区别……",
        "author": "小红",
        "created_at": "2026-06-02",
        "published": True,
        "tags": ["Python", "JSON", "基础"]
    },
    {
        "id": 3,
        "title": "为什么选择 FastAPI？",
        "content": "在众多 Python Web 框架中，FastAPI 凭借其性能和易用性脱颖而出……",
        "author": "小明",
        "created_at": "2026-06-03",
        "published": False,
        "tags": ["FastAPI", "对比", "选型"]
    }
]
```

**（4）接口**

```python
# 教程 02 的接口
@app.get("/")
def read_root():
    return {"message": "Hello World"}


# 教程 03 的接口
@app.get("/secret")
def secret_page():
    return JSONResponse(
        status_code=404,
        content={"error": "你找的秘密页面不存在！", "hint": "试试别的路径，比如 /"}
    )


# 本章新增：单篇文章
@app.get("/posts/1", response_model=Post)
def get_post():
    return sample_post


# 本章新增：文章列表
@app.get("/posts", response_model=list[Post])
def get_posts():
    return sample_posts


# 本章新增：服务器时间
@app.get("/server-time", response_model=TimeResponse)
def get_server_time():
    return {"current_time": datetime.now()}
```

---

## 四、完整代码清单

### `blog_backend/main.py`（本教程最终版本）

```python
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from datetime import datetime

app = FastAPI()


# ==================== Pydantic 模型 ====================

class Post(BaseModel):
    id: int
    title: str
    content: str
    author: str
    created_at: str
    published: bool
    tags: list[str]


class TimeResponse(BaseModel):
    current_time: datetime


# ==================== 模拟数据 ====================

sample_post = {
    "id": 1,
    "title": "FastAPI 入门指南",
    "content": "今天我们来学习如何使用 FastAPI 构建后端服务。FastAPI 是一个现代、高性能的 Python Web 框架……",
    "author": "小明",
    "created_at": "2026-06-01",
    "published": True,
    "tags": ["Python", "FastAPI", "后端"]
}

sample_posts = [
    {
        "id": 1,
        "title": "FastAPI 入门指南",
        "content": "今天我们来学习如何使用 FastAPI 构建后端服务……",
        "author": "小明",
        "created_at": "2026-06-01",
        "published": True,
        "tags": ["Python", "FastAPI", "后端"]
    },
    {
        "id": 2,
        "title": "Python 字典和 JSON 的关系",
        "content": "很多初学者搞不清 Python dict 和 JSON 的区别……",
        "author": "小红",
        "created_at": "2026-06-02",
        "published": True,
        "tags": ["Python", "JSON", "基础"]
    },
    {
        "id": 3,
        "title": "为什么选择 FastAPI？",
        "content": "在众多 Python Web 框架中，FastAPI 凭借其性能和易用性脱颖而出……",
        "author": "小明",
        "created_at": "2026-06-03",
        "published": False,
        "tags": ["FastAPI", "对比", "选型"]
    }
]


# ==================== 接口 ====================

@app.get("/")
def read_root():
    return {"message": "Hello World"}


@app.get("/secret")
def secret_page():
    return JSONResponse(
        status_code=404,
        content={"error": "你找的秘密页面不存在！", "hint": "试试别的路径，比如 /"}
    )


@app.get("/posts/1", response_model=Post)
def get_post():
    return sample_post


@app.get("/posts", response_model=list[Post])
def get_posts():
    return sample_posts


@app.get("/server-time", response_model=TimeResponse)
def get_server_time():
    return {"current_time": datetime.now()}
```

---

## 五、验证方法

在终端中依次执行以下命令，确认一切正常。确保服务器正在运行（`uvicorn blog_backend.main:app --reload`）。

```bash
# 1. 确认首页正常
curl http://127.0.0.1:8000/

# 2. 确认单篇文章返回了 JSON 对象
curl http://127.0.0.1:8000/posts/1

# 3. 确认文章列表返回了 JSON 数组
curl http://127.0.0.1:8000/posts

# 4. 确认服务器时间返回正常（不报错）
curl http://127.0.0.1:8000/server-time

# 5. 确认 Swagger 文档显示了 Post 和 TimeResponse 模型
# 浏览器打开 http://127.0.0.1:8000/docs
# 展开 GET /posts，查看 Response 区域是否显示了完整的字段结构
```

预期结果：
- 第一条：`{"message":"Hello World"}`
- 第二条：一个 JSON 对象，包含 `id`、`title`、`content`、`author`、`created_at`、`published`、`tags` 七个字段
- 第三条：一个 JSON 数组，包含 3 个元素，每个元素的字段和第二条一致
- 第四条：`{"current_time":"2026-06-05T..."}`（ISO 8601 格式的时间字符串），**不报错**
- 第五条：Swagger 页面上能看到 `Post` 和 `TimeResponse` 的 Schema

---

## 六、已知坑点与禁止事项

| 坑点 | 现象 | 原因 | 解决 |
|------|------|------|------|
| 返回 `datetime` 对象报错 | `TypeError: Object of type datetime is not JSON serializable` | JSON 不支持 Python 的 `datetime` 类型 | 用 `str()` 或 `.isoformat()` 转成字符串，或用 Pydantic 模型（推荐） |
| JSON 的 key 用了单引号 | 你以为写的是 JSON，但 Python 里 `{'key': 'value'}` 只是 dict | JSON 的 key 必须用双引号 | 放心用 Python dict 的语法写，FastAPI 会自动帮你转成合法的 JSON（双引号） |
| 搞混 JSON 字符串和 Python dict | `'{"a": 1}'` 是字符串，`{"a": 1}` 是 dict | 它们长得像但本质不同：字符串是文本，dict 是数据结构 | 记住：JSON 永远是字符串（可以保存到文件、通过网络传输）；Python dict 是内存里的数据结构 |
| `response_model` 拼写错误 | `response_model=Post` 没生效，文档里还是 "unknown" | 写成了 `response_model` 或 `response_modal` | 检查拼写：`response_model`，不是 `response_model`（没有 `r` 在末尾），也不是 `response_modal` |
| `list[Post]` 报错 | `TypeError: 'type' object is not subscriptable` | Python 版本低于 3.9，不支持 `list[Post]` 语法 | 改用 `from typing import List`，写成 `response_model=List[Post]` |
| `tags: list[str]` 报错 | 同上 | 同上 | 改用 `from typing import List`，写成 `tags: List[str]` |
| 在 Pydantic 模型里用了 `datetime` 但没有 `response_model` | 返回 dict 时 `datetime` 字段仍然报序列化错误 | `response_model` 的自动序列化只在返回数据通过 Pydantic 模型时才生效 | 加上 `response_model=TimeResponse`，或者返回 Pydantic 模型实例而不是裸 dict |

---

## 七、小结

| 你学到了什么 | 一句话总结 |
|--------------|-----------|
| JSON 是什么 | 一种"数据集装箱"式的文本格式，6 种数据类型，所有语言都能读，key 必须用双引号 |
| JSON vs Python dict | dict 是内存里的"活数据"，JSON 是传输用的"死字符串"——长得像，本质不同 |
| 为什么后端都用 JSON | 语言无关、人类可读、JavaScript 原生支持、比 XML 更简洁 |
| FastAPI 自动序列化 | 你 `return` 一个 dict，FastAPI 自动转成 JSON 字符串，设置 `Content-Type`，不需要你写一行转换代码 |
| 返回单个对象 | 定义 Python dict → `return` 它 → FastAPI 转成 JSON 对象 `{}` |
| 返回对象列表 | 定义 Python `list[dict]` → `return` 它 → FastAPI 转成 JSON 数组 `[{}, {}, {}]` |
| Pydantic 模型 | 继承 `BaseModel`，声明字段和类型，Pydantic 自动做数据校验、类型转换、生成文档 |
| `response_model` | 告诉 FastAPI 返回数据的结构——让 Swagger 自动生成文档，同时过滤多余字段、校验数据类型 |
| 序列化错误 | 返回 `datetime`、`Decimal`、`set` 等 Python 特有类型会报错，必须转成 JSON 支持的 6 种类型之一或用 Pydantic 模型 |
| 正确的日期时间处理 | 用 `.isoformat()` 转成 ISO 8601 字符串，或直接用 Pydantic 模型（`datetime` 类型会自动序列化） |

---

## 八、术语附录

| 术语 | 英文 | 通俗解释 | 本章出现位置 |
|------|------|----------|-------------|
| JSON | JavaScript Object Notation | 一种用纯文本表示数据结构的格式，花括号 `{}` 包对象，方括号 `[]` 包数组。所有编程语言都能读写，是前后端通信的"通用语言"。**字面陷阱**：名字里有 "JavaScript"，但它跟 JavaScript 语言本身没有绑定关系——任何语言都能用 JSON。 | 步骤 1 |
| 序列化 | Serialization | 把内存里的数据结构（如 Python dict）变成可以传输或存储的字符串（如 JSON 字符串）的过程。反序列化（Deserialization）就是反过来——把字符串变回数据结构。**比喻**：搬家时把衣柜拆成木板（序列化），到了新家再拼回去（反序列化）。 | 步骤 3 |
| Pydantic | — | 一个 Python 数据校验库，FastAPI 的核心依赖之一。你定义一个继承自 `BaseModel` 的类，Pydantic 就能自动做数据校验、类型转换和文档生成。**字面陷阱**：名字和 "pedantic"（迂腐的、学究气的）同音——它确实很"迂腐"，会严格检查你的数据格式，不放过任何错误。 | 步骤 6 |
| `response_model` | — | FastAPI 路径操作装饰器（如 `@app.get`）的一个参数，用来声明接口返回数据的结构（Pydantic 模型）。作用是：① 生成 Swagger 文档 ② 过滤多余字段 ③ 校验返回数据的类型。 | 步骤 6 |
| BaseModel | — | Pydantic 提供的基类，你定义的模型类必须继承它才能获得数据校验和序列化能力。可以理解为"标准菜谱模板"——继承它之后，你的类就变成了一张"菜谱"。 | 步骤 6 |
| ISO 8601 | — | 国际标准日期时间格式，如 `2026-06-05T14:30:22`。`T` 分隔日期和时间，前端和数据库都能直接识别。 | 步骤 7 |
| RESTful API | Representational State Transfer | 一种 API 设计风格，核心思想是用 URL 路径表示"资源"（如 `/posts` 表示文章资源），用 HTTP 方法表示"操作"（GET 获取、POST 创建、PUT 修改、DELETE 删除）。本章的 `/posts` 和 `/posts/1` 就遵循了这种设计惯例。 | 步骤 5 |

---

## 九、下一步建议

你已经能让后端返回有意义的数据了——单篇文章、文章列表、被 Pydantic 模型保护的数据。但现在的文章都是写死在代码里的"模拟数据"。接下来：

- **下一章**：[05-路径参数](./05-路径参数/)——学习如何让 `/posts/1` 中的 `1` 变成动态的，用户访问 `/posts/2` 就返回第 2 篇文章，访问 `/posts/999` 就返回第 999 篇。
- **延伸思考**：你现在的 `sample_posts` 是用 Python 的 `list[dict]` 定义的，有没有办法把它存到数据库里，让数据持久化？我们会在后续章节讲 SQLite 数据库操作。

---

> **本章编辑记录**：2026-06-05 初始版本。