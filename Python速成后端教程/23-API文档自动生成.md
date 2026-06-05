# 23-API 文档自动生成

- 对应文档版本：首版教程
- 适用环境：Python 3.10+, FastAPI 0.100+, Windows/macOS/Linux
- 读者角色：后端初学者
- 预计耗时：新手 20 分钟 / 熟手 10 分钟
- 前置教程：[13-博客接口升级：数据真正存到数据库]
- 可视化：无

---

## 一、目标与完成效果

**一句话目标**：发现 FastAPI 自带的杀手级功能——自动生成的 API 文档。你不需要额外写一行文档代码，FastAPI 已经帮你准备好了。

**完成后的可观测效果**：
- 浏览器打开 `http://127.0.0.1:8000/docs`，看到所有接口的 Swagger UI 交互式文档。
- 在 Swagger UI 里点击 "Try it out"，可以直接在浏览器里测试接口——不需要 curl，不需要 Postman。
- 打开 `http://127.0.0.1:8000/redoc`，看到另一种风格的 ReDoc 文档。
- 给每个接口加上 `summary`、`description`、`tags` 后，文档从"能用"变成"好用"——接口按分类排列，中文描述一目了然。
- 你能跟同事说："我从来不用写 API 文档，FastAPI 自动生成的。"

---

## 二、前置条件

| 序号 | 条件 | 验证命令 |
|------|------|----------|
| 1 | 博客 CRUD 接口在 `blog_backend/main.py` 中正常工作 | `curl http://127.0.0.1:8000/posts` 返回数据 |
| 2 | 服务器正在运行（`uvicorn blog_backend.main:app --reload`） | 终端能看到 `Uvicorn running on http://127.0.0.1:8000` |

**一条命令确认前置满足**：

```powershell
curl http://127.0.0.1:8000/docs
```

如果能返回 HTML 页面（而不是 404），前置条件满足。

---

## 三、分步操作

### 步骤 1：打开 Swagger UI——你的 API 文档已经在了

你的服务器已经在运行。现在打开浏览器，访问：

```
http://127.0.0.1:8000/docs
```

**你看到了什么？** 一个完整的交互式 API 文档页面，列出了你所有的接口：

- `GET /posts` —— 获取文章列表
- `POST /posts` —— 创建文章
- `GET /posts/{post_id}` —— 获取单篇文章
- `PUT /posts/{post_id}` —— 更新文章
- `DELETE /posts/{post_id}` —— 删除文章
- `POST /login` —— 登录
- `POST /users` —— 注册
- `POST /posts/upload-image` —— 上传封面图

**你写一行文档的代码了吗？没有。** FastAPI 从你的 Python 代码中自动提取了所有信息——路径、方法、参数类型、请求体结构、响应模型——生成了这份文档。

**比喻**：FastAPI 就像一个"自动记账员"——你写代码时定义了什么参数、什么返回值，它全部默默记下来（通过 Pydantic 类型注解和 `response_model`），然后自动生成一份漂亮的账本（Swagger 文档）。你不需要额外做任何事。

**这背后是什么？** FastAPI 遵循 **OpenAPI** 规范（以前叫 Swagger），这是业界标准的 API 文档格式。此术语需进附录。FastAPI 自动生成 OpenAPI JSON，Swagger UI 再把这个 JSON 渲染成漂亮的网页。

```
你的 Python 代码 → FastAPI 解析 → OpenAPI JSON → Swagger UI 渲染 → 你看到的网页
```

---

### 步骤 2：在 Swagger UI 里直接测试接口

Swagger UI 不只是"看"的文档，它还能**直接测试接口**。

**操作步骤**：

1. 在文档页面找到 `POST /login` 接口，点击展开。
2. 点击 **"Try it out"** 按钮。
3. 在 Request body 的编辑框中输入：

```json
{
  "username": "alice",
  "password": "alice123"
}
```

4. 点击 **"Execute"** 按钮。
5. 下方出现 **Response**，显示服务器返回的 JSON 和状态码。

**你刚才在浏览器里完成了一次 API 调用——不需要 curl，不需要 Postman，不需要写代码。**

**接下来测试需要认证的接口**：

1. 在 `POST /users` 或 `POST /posts` 等需要认证的接口上，点击右上角的 **🔒 Authorize** 按钮（或页面顶部的小锁图标）。
2. 在弹窗中输入你的 token（从登录接口的响应中复制 `access_token` 的值）。
3. 格式：直接粘贴 token 字符串，不需要加 `Bearer` 前缀（Swagger UI 会自动加）。
4. 点击 **Authorize**，然后 **Close**。
5. 现在所有需要认证的接口都会自动带上这个 token。

**比喻**：Swagger UI 的 "Try it out" 就像一个"接口遥控器"——你不需要记住 curl 的各种参数和格式，在网页上填好参数，点按钮，结果就出来了。调试接口从未如此轻松。

---

### 步骤 3：给接口加描述——从"能用"到"好用"

当前的文档虽然列出了所有接口，但描述很简陋——接口名称是函数名或路径，参数说明是字段名，看不出接口的用途。

我们可以通过装饰器参数给接口加上中文描述，让文档变得"一看就懂"。

打开 `blog_backend/main.py`，逐个给接口加上 `summary` 和 `description`：

```python
# === 获取文章列表（分页 + 搜索） ===
@app.get(
    "/posts",
    response_model=PaginatedResponse[BlogResponse],
    summary="获取文章列表",
    description="支持分页（page、size）和关键词搜索（keyword）。不传参数时默认返回第 1 页，每页 10 条。",
    tags=["文章管理"],
)
def get_all_posts(
    page: int = 1,
    size: int = 10,
    keyword: str = "",
    db: Session = Depends(get_db),
):
    # ... 函数体不变 ...


# === 获取单篇文章 ===
@app.get(
    "/posts/{post_id}",
    summary="获取单篇文章",
    description="根据文章 ID 获取文章详情。如果文章不存在，返回 404。",
    tags=["文章管理"],
)
def get_post(post_id: int, db: Session = Depends(get_db)):
    # ... 函数体不变 ...


# === 创建文章 ===
@app.post(
    "/posts",
    summary="创建文章",
    description="创建一篇新文章。需要登录。创建成功后返回完整的文章对象。",
    tags=["文章管理"],
)
def create_post(
    blog: BlogCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # ... 函数体不变 ...


# === 更新文章 ===
@app.put(
    "/posts/{post_id}",
    summary="更新文章",
    description="更新指定文章的内容。只有文章作者本人可以更新。不是作者返回 403。",
    tags=["文章管理"],
)
def update_post(
    post_id: int,
    blog: BlogCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # ... 函数体不变 ...


# === 删除文章 ===
@app.delete(
    "/posts/{post_id}",
    summary="删除文章",
    description="删除指定文章。只有文章作者本人可以删除。不是作者返回 403。",
    tags=["文章管理"],
)
def delete_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # ... 函数体不变 ...


# === 上传封面图 ===
@app.post(
    "/posts/upload-image",
    summary="上传文章封面图",
    description="上传图片文件作为文章封面。支持 JPEG、PNG、GIF、WebP 格式，最大 5MB。返回可访问的图片 URL。",
    tags=["文章管理"],
)
async def upload_image(file: UploadFile = File(...)):
    # ... 函数体不变 ...


# === 用户注册 ===
@app.post(
    "/users",
    summary="用户注册",
    description="注册新用户。用户名必须唯一，密码长度至少 6 位。",
    tags=["用户管理"],
)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    # ... 函数体不变 ...


# === 用户登录 ===
@app.post(
    "/login",
    summary="用户登录",
    description="使用用户名和密码登录，成功后返回 JWT access token。token 有效期 30 分钟。",
    tags=["用户管理"],
)
def login(user: UserLogin, db: Session = Depends(get_db)):
    # ... 函数体不变 ...
```

**逐行解释**：

- `summary="获取文章列表"`：接口的简短描述，显示在 Swagger UI 的接口列表里。
- `description="支持分页..."`：接口的详细描述，展开接口后显示。可以写多行，支持 Markdown 格式。
- `tags=["文章管理"]`：给接口分组。Swagger UI 会把相同 `tags` 的接口归到一组，折叠显示。`tags` 可以同时属于多个组（如 `tags=["文章管理", "公开接口"]`）。

**比喻**：`summary` 是书的标题，`description` 是封底介绍，`tags` 是书架的分类标签。加上这些，你的文档从"一堆函数列表"变成了"一本有目录、有章节的说明书"。

---

### 步骤 4：给参数加描述——让每个字段都说话

目前 Swagger UI 里的参数名是 `page`、`size`、`keyword`，但没有任何说明。我们可以用 `Query()` 给查询参数加上描述。

打开 `blog_backend/main.py`，改造 `get_all_posts` 的参数：

```python
from fastapi import Query


@app.get(
    "/posts",
    response_model=PaginatedResponse[BlogResponse],
    summary="获取文章列表",
    description="支持分页（page、size）和关键词搜索（keyword）。不传参数时默认返回第 1 页，每页 10 条。",
    tags=["文章管理"],
)
def get_all_posts(
    page: int = Query(1, ge=1, description="页码，从 1 开始"),
    size: int = Query(10, ge=1, le=100, description="每页条数，范围 1~100"),
    keyword: str = Query("", description="搜索关键词，匹配标题和内容"),
    db: Session = Depends(get_db),
):
    # ... 函数体不变（边界保护可以简化或去掉，因为 Query 的 ge/le 已经做了限制） ...
```

**逐行解释**：

- `Query(1, ge=1, description="页码，从 1 开始")`：`Query` 的第一个参数是默认值，`ge=1` 表示 "greater than or equal to 1"（最小值 1），`description` 是参数说明。此术语需进附录：Query。
- `Query(10, ge=1, le=100, description="...")`：`le=100` 表示 "less than or equal to 100"（最大值 100）。
- `Query("", description="...")`：默认值为空字符串，无额外校验。

**用 `Query` 的好处**：
1. **文档里显示参数描述**——Swagger UI 会在每个参数旁显示说明文字。
2. **自动校验**——`ge=1` 意味着如果用户传 `page=0`，FastAPI 会自动返回 422 验证错误，不需要你手动写 `if page < 1:`。
3. **代码更简洁**——之前的手动边界检查（`if page < 1: page = 1`）可以删掉了。

**注意**：如果你用了 `Query(ge=1)`，FastAPI 会在参数非法时返回 422 状态码（而不是静默修正为 1）。这是更标准的做法——告诉客户端"你传的参数不对"，而不是悄悄改掉。

---

### 步骤 5：给模型加示例数据，文档更直观

在 Swagger UI 里，请求体的 Schema 显示了每个字段的类型和是否必填。但如果你能给每个字段加一个**示例值**，文档会直观得多。

打开 `blog_backend/schemas.py`，给 `BlogCreate` 加示例数据：

```python
class BlogCreate(BaseModel):
    title: str
    content: str
    published: bool = False
    summary: str | None = None
    cover_image: str | None = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "title": "Python 入门教程",
                    "content": "从零开始学 Python，适合初学者。",
                    "published": True,
                    "summary": "一篇面向初学者的 Python 教程",
                    "cover_image": "/static/abc123.jpg",
                }
            ]
        }
    }
```

**逐行解释**：

- `model_config`：Pydantic v2 的配置方式（旧版是 `class Config:`），用于设置模型的各种元信息。
- `"json_schema_extra"`：往生成的 JSON Schema 中追加额外信息。Swagger UI 读取这些信息来展示示例。
- `"examples": [...]`：示例数据列表。Swagger UI 会显示第一个示例，并在 "Example" 下拉框中展示。

**效果**：在 Swagger UI 里展开 `POST /posts`，点击 "Try it out"，请求体编辑框里会自动填充示例数据——用户不需要从零开始写 JSON，改几个字段就能测试。

**比喻**：`model_config` 里的 examples 就像快递单上的"填写示例"——"收件人：张三，地址：XX 省 XX 市"，你照着填就行，不用自己想格式。

---

### 步骤 6：ReDoc——另一种风格的文档

FastAPI 除了 Swagger UI，还提供了另一种文档风格：**ReDoc**。

打开浏览器，访问：

```
http://127.0.0.1:8000/redoc
```

**ReDoc 的特点**：
- 三栏布局：左侧导航，中间文档，右侧示例。
- 更适合"阅读"而不是"交互测试"。
- 没有 "Try it out" 功能，但排版更清晰，适合打印或导出。

**Swagger UI vs ReDoc**：

| 特性 | Swagger UI | ReDoc |
|------|------------|-------|
| 交互式测试 | ✅ Try it out | ❌ 只读 |
| 排版 | 紧凑，折叠式 | 三栏，适合阅读 |
| 适合场景 | 开发调试 | 对外发布、打印 |
| 路径 | `/docs` | `/redoc` |

**两个都免费，两个都自动生成。** 你不需要选——FastAPI 两个都给你了。

---

### 步骤 7：🤔 想多一点——为什么自动文档这么重要？

你可能会想：不就是个文档页面吗？我写好接口，用 curl 测试一下不就行了？

**自动文档的价值在于消除"沟通成本"**：

| 场景 | 没有文档 | 有自动文档 |
|------|----------|-----------|
| 前端问"这个接口要传什么参数？" | 你在 Slack 里打字解释，或者截图代码 | 前端自己打开 `/docs`，一目了然 |
| 新同事入职，想了解有哪些 API | 你给他讲一遍，或者他翻代码 | 打开 `/docs`，所有接口按分类排列 |
| 你用 Postman 手动测试 | 手动填 URL、Header、Body | 在 Swagger UI 里点 "Try it out" |
| 接口改了参数，忘记通知前端 | 前端调用报错，过来找你 | 改了代码，文档自动更新，前端看到的变化就是实时的 |
| 写接口文档给甲方验收 | 花半天写 Word 文档 | 发一个 `/docs` 链接 |

**核心原则：文档和代码是一体的。** 代码改了，文档自动跟着变——不存在"文档过时了"的问题。你不需要在"写代码"和"写文档"之间同步，因为它们是同一件事。

**比喻**：传统开发 = 你做饭，然后手写一份菜单。菜单和菜可能对不上（你换了菜，忘记更新菜单）。FastAPI = 你做饭，菜单自动根据你做的菜生成——你换了菜，菜单自动更新。

---

## 四、完整代码清单

### `blog_backend/schemas.py`（本教程新增/修改部分）

<details>
<summary>点击展开完整代码</summary>

```python
from pydantic import BaseModel


class BlogCreate(BaseModel):
    title: str
    content: str
    published: bool = False
    summary: str | None = None
    cover_image: str | None = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "title": "Python 入门教程",
                    "content": "从零开始学 Python，适合初学者。",
                    "published": True,
                    "summary": "一篇面向初学者的 Python 教程",
                    "cover_image": "/static/abc123.jpg",
                }
            ]
        }
    }


# ... 其他 Schema 保持不变 ...
```

</details>

### `blog_backend/main.py`（本教程新增/修改部分）

<details>
<summary>点击展开完整代码</summary>

```python
from fastapi import FastAPI, Depends, Query, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
# ... 其他导入不变 ...

app = FastAPI()

# ... 中间件、静态文件等不变 ...


# === 获取文章列表（分页 + 搜索） ===
@app.get(
    "/posts",
    response_model=PaginatedResponse[BlogResponse],
    summary="获取文章列表",
    description="支持分页（page、size）和关键词搜索（keyword）。不传参数时默认返回第 1 页，每页 10 条。",
    tags=["文章管理"],
)
def get_all_posts(
    page: int = Query(1, ge=1, description="页码，从 1 开始"),
    size: int = Query(10, ge=1, le=100, description="每页条数，范围 1~100"),
    keyword: str = Query("", description="搜索关键词，匹配标题和内容"),
    db: Session = Depends(get_db),
):
    query = db.query(Post)
    if keyword:
        query = query.filter(
            or_(
                Post.title.contains(keyword),
                Post.content.contains(keyword),
            )
        )
    total = query.count()
    skip = (page - 1) * size
    posts = query.offset(skip).limit(size).all()
    pages = math.ceil(total / size) if total > 0 else 0
    return {
        "items": posts,
        "total": total,
        "page": page,
        "size": size,
        "pages": pages,
    }


# === 获取单篇文章 ===
@app.get(
    "/posts/{post_id}",
    summary="获取单篇文章",
    description="根据文章 ID 获取文章详情。如果文章不存在，返回 404。",
    tags=["文章管理"],
)
def get_post(post_id: int, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if post is None:
        return JSONResponse(
            status_code=404,
            content={"error": f"文章 #{post_id} 不存在"}
        )
    return post


# === 创建文章 ===
@app.post(
    "/posts",
    summary="创建文章",
    description="创建一篇新文章。需要登录。创建成功后返回完整的文章对象。",
    tags=["文章管理"],
)
def create_post(
    blog: BlogCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    new_post = Post(
        title=blog.title,
        content=blog.content,
        published=blog.published,
        summary=blog.summary,
        cover_image=blog.cover_image,
        author_id=current_user.id,
    )
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post


# === 更新文章 ===
@app.put(
    "/posts/{post_id}",
    summary="更新文章",
    description="更新指定文章的内容。只有文章作者本人可以更新。不是作者返回 403。",
    tags=["文章管理"],
)
def update_post(
    post_id: int,
    blog: BlogCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    post = db.query(Post).filter(Post.id == post_id).first()
    if post is None:
        return JSONResponse(
            status_code=404,
            content={"error": f"文章 #{post_id} 不存在，无法更新"}
        )
    check_owner(post, current_user)
    post.title = blog.title
    post.content = blog.content
    post.published = blog.published
    post.summary = blog.summary
    db.commit()
    return post


# === 删除文章 ===
@app.delete(
    "/posts/{post_id}",
    summary="删除文章",
    description="删除指定文章。只有文章作者本人可以删除。不是作者返回 403。",
    tags=["文章管理"],
)
def delete_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    post = db.query(Post).filter(Post.id == post_id).first()
    if post is None:
        return JSONResponse(
            status_code=404,
            content={"error": f"文章 #{post_id} 不存在，无法删除"}
        )
    check_owner(post, current_user)
    db.delete(post)
    db.commit()
    return {"message": f"文章 #{post_id}「{post.title}」已删除"}


# === 上传封面图 ===
@app.post(
    "/posts/upload-image",
    summary="上传文章封面图",
    description="上传图片文件作为文章封面。支持 JPEG、PNG、GIF、WebP 格式，最大 5MB。返回可访问的图片 URL。",
    tags=["文章管理"],
)
async def upload_image(file: UploadFile = File(...)):
    allowed_types = ["image/jpeg", "image/png", "image/gif", "image/webp"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的文件类型：{file.content_type}。仅支持 JPEG、PNG、GIF、WebP。"
        )
    contents = await file.read()
    max_size = 5 * 1024 * 1024
    if len(contents) > max_size:
        raise HTTPException(
            status_code=413,
            detail=f"文件过大：{len(contents) / 1024 / 1024:.1f}MB。最大允许 5MB。"
        )
    ext = os.path.splitext(file.filename)[1]
    unique_name = f"{uuid.uuid4()}{ext}"
    file_path = os.path.join(UPLOAD_DIR, unique_name)
    with open(file_path, "wb") as f:
        f.write(contents)
    return {
        "url": f"/static/{unique_name}",
        "filename": unique_name,
    }


# === 用户注册 ===
@app.post(
    "/users",
    summary="用户注册",
    description="注册新用户。用户名必须唯一，密码长度至少 6 位。",
    tags=["用户管理"],
)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    # ... 函数体不变 ...


# === 用户登录 ===
@app.post(
    "/login",
    summary="用户登录",
    description="使用用户名和密码登录，成功后返回 JWT access token。token 有效期 30 分钟。",
    tags=["用户管理"],
)
def login(user: UserLogin, db: Session = Depends(get_db)):
    # ... 函数体不变 ...
```

</details>

---

## 五、验证方法

```bash
# 1. 打开 Swagger UI
# 浏览器访问 http://127.0.0.1:8000/docs
# → 所有接口按 tags 分组显示，每个接口有中文 summary

# 2. 在 Swagger UI 里测试登录
# 展开 POST /login → Try it out → 输入用户名密码 → Execute
# → 返回 token

# 3. 填入认证信息
# 点击页面顶部的 Authorize 按钮 → 粘贴 token → Authorize
# → 所有需要认证的接口自动带上 token

# 4. 在 Swagger UI 里测试创建文章
# 展开 POST /posts → Try it out → 编辑请求体 → Execute
# → 返回创建的文章

# 5. 打开 ReDoc
# 浏览器访问 http://127.0.0.1:8000/redoc
# → 看到另一种风格的文档，三栏布局
```

---

## 六、术语附录

| 术语 | 英文 | 通俗解释 | 本章出现位置 |
|------|------|----------|-------------|
| Swagger UI | — | 交互式 API 文档页面，从 OpenAPI JSON 自动生成。支持 "Try it out" 在线测试接口。 | 步骤 1、2 |
| OpenAPI | OpenAPI Specification | 业界标准的 API 描述规范（以前叫 Swagger）。用 JSON 格式描述 API 的路径、参数、响应等。FastAPI 自动生成 OpenAPI JSON。 | 步骤 1 |
| ReDoc | — | 另一种 API 文档渲染工具，三栏布局，适合阅读和打印，但无交互测试功能。 | 步骤 6 |
| `summary` | — | 装饰器参数，接口的简短描述，显示在 Swagger UI 的接口列表中。 | 步骤 3 |
| `description` | — | 装饰器参数，接口的详细描述，展开后显示。支持 Markdown 格式。 | 步骤 3 |
| `tags` | — | 装饰器参数，接口分组标签。Swagger UI 会把相同 tags 的接口归到一组折叠显示。 | 步骤 3 |
| `Query` | — | FastAPI 的查询参数定义函数。`Query(default, ge=1, description="...")` 可以设默认值、校验规则和参数说明。 | 步骤 4 |
| `model_config` | — | Pydantic v2 的模型配置方式，用于设置 `from_attributes`、`json_schema_extra` 等元信息。替代旧版 `class Config`。 | 步骤 5 |
| 422 状态码 | 422 Unprocessable Entity | HTTP 状态码，表示请求格式正确但参数校验失败（如 `page=0` 而要求 `ge=1`）。 | 步骤 4 |

---

## 七、小结

| 你学到了什么 | 一句话总结 |
|--------------|-----------|
| Swagger UI 自动文档 | 打开 `/docs`，所有接口自动列出，不需要写一行文档代码 |
| Try it out 在线测试 | 在浏览器里直接调接口，不需要 curl 或 Postman |
| `summary` 和 `description` | 给接口加中文描述，文档从"能用"变"好用" |
| `tags` 分组 | 把接口按业务分类（文章管理、用户管理），一目了然 |
| `Query` 参数描述 | `Query(1, ge=1, description="...")` 给参数加说明和校验 |
| `model_config` 示例 | `json_schema_extra` 提供示例数据，Swagger UI 自动填充 |
| ReDoc 替代视图 | `/redoc` 提供另一种文档风格，适合阅读和打印 |
| 文档代码一体 | 代码改了，文档自动更新——不存在文档过时问题 |

---

## 八、已知坑点与禁止事项

| 坑点 | 现象 | 原因 | 解决 |
|------|------|------|------|
| `model_config` 格式写错 | Swagger UI 不显示示例数据 | Pydantic v2 用 `model_config = {...}`，不是 `class Config:` | 确认 `model_config` 是类属性赋值，不是嵌套类 |
| 用 `Query` 后删了手动边界检查 | 传 `page=0` 返回 422 而不是静默修正 | `Query(ge=1)` 会触发 FastAPI 自动校验，非法参数直接返回 422 | 这是正确行为——告诉客户端参数不对。如果希望静默修正，就不要用 `ge/le`，保留手动 `if` |
| `tags` 写成 `tag` | 接口没有分组 | 参数名是 `tags`（复数），不是 `tag` | 改成 `tags=["文章管理"]` |
| `description` 里写 Markdown 但没渲染 | 在 Swagger UI 里描述是纯文本 | Swagger UI 对 `description` 支持部分 Markdown，但 `summary` 不支持 | `description` 可以用 Markdown，`summary` 保持纯文本 |
| 忘记 `response_model` 没影响文档 | 文档里还是能看到接口 | 即使没写 `response_model`，FastAPI 也能从返回值推断出基本类型，但不精确 | 始终加上 `response_model`，文档会更准确 |

---

## 九、下一步建议

阶段六（进阶功能）全部完成！你的博客系统现在有了分页、搜索、文件上传、自动文档——已经是一个功能齐全的后端了。

**接下来**：阶段七（测试）——教程 24~25。你将学习如何给这些接口写自动化测试，确保改了代码不会搞坏已有功能。

**试试看**：在 `UserCreate` 和 `UserLogin` 的 Schema 里也加上 `model_config` 示例数据，让注册和登录的 Swagger 文档更直观。

---

> [可暂停点 5/9]：阶段六（进阶功能）全部完成。你的博客系统功能齐全：分页、搜索、文件上传、自动文档。打开 `/docs` 向朋友炫耀一下——你的 API 文档是自动生成的。