# 25-为博客 API 写测试

- 对应文档版本：首版教程
- 适用环境：Python 3.10+, pytest 7+, httpx 0.24+, pytest-cov, Windows/macOS/Linux
- 读者角色：后端初学者
- 预计耗时：新手 50 分钟 / 熟手 25 分钟
- 前置教程：[24-为什么要写测试]
- 可视化：无

---

## 一、目标与完成效果

**一句话目标**：为博客系统的全部接口编写自动化测试——注册、登录、文章 CRUD、评论、分页、搜索——运行 `pytest -v` 看到一片绿色 ✓，并用 `pytest-cov` 查看代码覆盖率。

**完成后的可观测效果**：
- 新建 `blog_backend/conftest.py`，用 pytest fixture 自动创建测试数据库和测试客户端。
- `blog_backend/test_main.py` 包含 10+ 个测试函数，覆盖所有核心接口。
- 运行 `pytest -v`，所有测试通过，终端一片绿色 ✓。
- 运行 `pytest --cov=blog_backend`，看到覆盖率报告——哪些代码被测试到了，哪些没覆盖。
- 测试数据全部写入 `test_blog.db`，你的开发数据 `blog.db` 完全不受影响。
- 你能说出 fixture 的作用，以及为什么测试需要独立的数据库。

---

## 二、前置条件

| 序号 | 条件 | 验证命令 |
|------|------|----------|
| 1 | 已完成教程 24，pytest 和 httpx 已安装 | `pytest --version` 能输出版本号 |
| 2 | `blog_backend/main.py` 包含所有接口（注册、登录、文章 CRUD、评论、分页、搜索） | `curl http://127.0.0.1:8000/posts` 返回数据 |
| 3 | 项目结构完整：`blog_backend/database.py`、`blog_backend/models.py`、`blog_backend/auth.py` | `dir blog_backend\` 确认文件存在 |

**一条命令确认前置满足**：

```powershell
python -c "from blog_backend.main import app; from blog_backend.database import Base, get_db; print('所有模块导入成功')"
```

如果输出 `所有模块导入成功`，前置条件满足。

---

## 三、分步操作

### 步骤 1：测试数据库——创建独立的 `test_blog.db`

**问题**：教程 24 的测试直接用 `TestClient` 发请求，它连的是你开发用的 `blog.db`。这意味着：
- 测试创建的"alice"用户会出现在你的真实数据库中。
- 测试删除的文章会真的从你的数据库中消失。
- 你的开发数据被测试污染了。

**解决**：创建独立的测试数据库。测试时用 `test_blog.db`，开发时用 `blog.db`，互不干扰。

**比喻**：测试数据库就像"实验田"——你在实验田里随便种、随便拔，不影响真正的农田（开发数据库）。试验做完，实验田清空，农田完好如初。

我们要在 `conftest.py` 中实现这个逻辑。但在写代码之前，先理解 **pytest fixture**。

---

### 步骤 2：pytest fixture——每次测试前自动准备环境

**fixture** 是 pytest 最核心的概念之一。此术语需进附录。

**什么是 fixture？** 一个装饰了 `@pytest.fixture` 的函数，它会在测试函数运行之前自动执行，准备好测试需要的"环境"（数据库、客户端、测试数据等）。

**为什么需要 fixture？** 假设你有 10 个测试函数，每个都需要"先创建数据库表、再创建测试客户端"。没有 fixture 的话，你要在每个测试函数里写一遍创建数据库的代码——10 次重复。有了 fixture，你写一次，pytest 在每个测试前自动注入。

**比喻**：fixture 就像"每次考试前自动发一张空白试卷"。你不用自己准备试卷（数据库），不用自己削铅笔（客户端），pytest 在每次考试前自动帮你准备好一切。考完试，pytest 还帮你收走试卷（清理数据库）。

**fixture 的两个核心能力**：

| 能力 | 说明 | 比喻 |
|------|------|------|
| **setup**（准备） | 在测试前自动执行，准备好环境 | 考试前发空白试卷 |
| **teardown**（清理） | 在测试后自动执行，清理环境 | 考试后收走试卷 |

**setup 和 teardown 在代码中怎么写？** 用 `yield` 关键字——`yield` 之前是 setup，`yield` 之后是 teardown：

```python
@pytest.fixture
def example():
    print("setup: 测试前准备")    # ← 测试前执行
    yield "数据"                  # ← 把数据传给测试函数
    print("teardown: 测试后清理") # ← 测试后执行
```

现在动手写 `conftest.py`。

**注意**：`conftest.py` 是 pytest 的特殊文件名，放在测试目录下，pytest 会自动加载其中的 fixture，供同目录的测试文件使用。你不需要手动导入。

新建 `blog_backend/conftest.py`：

```python
# blog_backend/conftest.py —— 测试配置与 fixture

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from blog_backend.database import Base, get_db
from blog_backend.main import app

# ============================================================
# 1. 创建独立的测试数据库
# ============================================================
# 使用 test_blog.db，而不是 blog.db
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test_blog.db"

test_engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},  # SQLite 需要这个参数
)

TestSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine,
)

# ============================================================
# 2. 覆盖 get_db 依赖——让所有接口用测试数据库
# ============================================================
def override_get_db():
    """替换原来的 get_db，改为使用测试数据库的会话"""
    try:
        db = TestSessionLocal()
        yield db
    finally:
        db.close()


# 把 FastAPI 的 get_db 依赖替换成我们的测试版本
app.dependency_overrides[get_db] = override_get_db


# ============================================================
# 3. fixture：自动创建和清理数据库表
# ============================================================
@pytest.fixture(autouse=True)
def setup_database():
    """
    每个测试函数执行前：自动创建所有数据库表
    每个测试函数执行后：自动删除所有数据库表
    autouse=True 表示这个 fixture 自动应用到所有测试，不需要手动声明
    """
    # ===== setup 阶段 =====
    Base.metadata.create_all(bind=test_engine)
    yield  # ← 测试函数在这里执行
    # ===== teardown 阶段 =====
    Base.metadata.drop_all(bind=test_engine)


# ============================================================
# 4. fixture：提供测试客户端
# ============================================================
@pytest.fixture
def client():
    """返回一个 TestClient 实例，用于发送 HTTP 请求"""
    return TestClient(app)


# ============================================================
# 5. fixture：提供已认证的 token
# ============================================================
@pytest.fixture
def auth_token(client):
    """
    自动注册一个测试用户并登录，返回 JWT token
    依赖 client fixture（pytest 自动注入）
    """
    # 注册测试用户
    client.post(
        "/users",
        json={"username": "testuser", "password": "test123456"},
    )
    # 登录获取 token
    response = client.post(
        "/login",
        json={"username": "testuser", "password": "test123456"},
    )
    data = response.json()
    return data["access_token"]
```

**逐行解释**：

- `conftest.py`：pytest 的特殊文件名。放在 `blog_backend/` 目录下，pytest 会自动加载其中的 fixture，所有同目录下的测试文件都可以直接使用。
- 第一部分：`test_engine` 和 `TestSessionLocal`——创建指向 `test_blog.db` 的数据库连接。和 `database.py` 中的代码几乎一样，唯一区别是数据库文件名。
- 第二部分：`app.dependency_overrides[get_db] = override_get_db`——**关键操作**。FastAPI 的依赖注入系统允许你在测试时替换依赖。`get_db` 本来指向 `blog.db`，我们把它替换成指向 `test_blog.db`。从此，所有接口在测试中都用测试数据库。此术语需进附录：dependency_overrides。
- 第三部分：`setup_database` fixture——`autouse=True` 表示这个 fixture 自动应用到每个测试函数，不需要在测试函数参数中声明。`yield` 之前：创建所有表（`create_all`）。`yield` 之后：删除所有表（`drop_all`）。每个测试函数都从一个干净的数据库开始。
- 第四部分：`client` fixture——返回 `TestClient(app)`。测试函数需要发请求时，直接在参数中声明 `client` 即可。
- 第五部分：`auth_token` fixture——依赖于 `client` fixture（pytest 会自动先执行 `client`，再执行 `auth_token`）。自动注册用户 + 登录，返回 token。测试需要认证的接口时，直接声明 `auth_token` 即可。

**比喻**：`dependency_overrides` 就像"换水管"——原本 `get_db` 这根水管接到 `blog.db` 水箱，你在测试时把它拧下来，接到 `test_blog.db` 水箱。所有接口的水龙头（数据库操作）自动流向新水箱，你不需要改任何接口代码。

❌ 常见错误 → ✅ 正确示例：

❌ 错误：在测试中手动管理数据库

```python
# 错误：在每个测试函数里手动创建和删除数据库
def test_register_user():
    Base.metadata.create_all(bind=engine)  # 手动创建
    # ... 测试逻辑 ...
    Base.metadata.drop_all(bind=engine)    # 手动删除
```

✅ 正确：用 fixture 自动管理

```python
# conftest.py 中定义一次 fixture
@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)

# 测试函数中不需要写任何数据库管理代码
def test_register_user(client):
    response = client.post("/users", json={...})
    assert response.status_code == 201
```

---

### 步骤 3：测试用户注册——`test_register_user`

现在在 `blog_backend/test_main.py` 中添加测试。先清空教程 24 的代码（那个 `test_create_post` 是教学用的，现在重写完整的）。

**完全重写** `blog_backend/test_main.py`：

```python
# blog_backend/test_main.py —— 博客 API 完整测试

from fastapi.testclient import TestClient
from blog_backend.main import app


# ============================================================
# 一、用户注册测试
# ============================================================

def test_register_user(client):
    """
    测试：注册新用户
    预期：返回 201，数据库中有该用户记录
    """
    response = client.post(
        "/users",
        json={"username": "alice", "password": "alice123"},
    )

    # 断言：状态码 201
    assert response.status_code == 201

    # 断言：返回值包含用户名
    data = response.json()
    assert data["username"] == "alice"
    # 断言：密码不应该出现在返回结果中
    assert "password" not in data


def test_register_duplicate_user(client):
    """
    测试：重复注册相同的用户名
    预期：第二次注册返回 400
    """
    # 第一次注册：成功
    client.post("/users", json={"username": "bob", "password": "bob123456"})

    # 第二次注册：重复用户名
    response = client.post(
        "/users",
        json={"username": "bob", "password": "bob123456"},
    )

    # 断言：返回 400
    assert response.status_code == 400
```

**逐行解释**：

- `def test_register_user(client):`：参数 `client` 是 conftest.py 中定义的 fixture。pytest 看到参数名 `client`，自动去 conftest.py 中找同名 fixture，执行它，把返回值（`TestClient` 实例）传进来。
- `assert "password" not in data`：安全断言——注册接口不应该把密码明文返回给客户端。
- `test_register_duplicate_user`：先注册一次（成功），再注册一次相同用户名，断言第二次返回 400（Bad Request）。

**验证**：

```bash
pytest -v -k "register"
```

`-k "register"` 表示只运行名称中包含 "register" 的测试。

**预期输出**：两个测试都 PASSED。

---

### 步骤 4：测试用户登录——`test_login`

```python
# ============================================================
# 二、用户登录测试
# ============================================================

def test_login_success(client):
    """
    测试：用正确的用户名和密码登录
    预期：返回 200，响应中包含 access_token
    """
    # 先注册用户
    client.post("/users", json={"username": "charlie", "password": "charlie123"})

    # 登录
    response = client.post(
        "/login",
        json={"username": "charlie", "password": "charlie123"},
    )

    # 断言：状态码 200
    assert response.status_code == 200

    # 断言：响应中包含 token
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client):
    """
    测试：用错误的密码登录
    预期：返回 401
    """
    # 先注册用户
    client.post("/users", json={"username": "dave", "password": "dave123456"})

    # 用错误密码登录
    response = client.post(
        "/login",
        json={"username": "dave", "password": "wrong_password"},
    )

    # 断言：返回 401
    assert response.status_code == 401
```

**逐行解释**：

- `assert data["token_type"] == "bearer"`：JWT 登录成功后，`token_type` 字段通常是 `"bearer"`。
- `test_login_wrong_password`：测试密码错误的情况——返回 401（Unauthorized）。

---

### 步骤 5：测试创建文章（需认证）——`test_create_post`

```python
# ============================================================
# 三、文章创建测试
# ============================================================

def test_create_post(auth_token, client):
    """
    测试：带 token 创建文章
    预期：返回 201，文章数据正确
    """
    response = client.post(
        "/posts",
        json={
            "title": "我的第一篇文章",
            "content": "这是文章内容。",
            "published": True,
        },
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    # 断言：状态码 201
    assert response.status_code == 201

    # 断言：返回的文章数据正确
    data = response.json()
    assert data["title"] == "我的第一篇文章"
    assert data["content"] == "这是文章内容。"
    assert data["published"] is True
    # 断言：文章 ID 应该被自动生成了
    assert "id" in data


def test_create_post_without_auth(client):
    """
    测试：不带 token 创建文章
    预期：返回 401
    """
    response = client.post(
        "/posts",
        json={
            "title": "未登录创建",
            "content": "应该被拒绝。",
        },
        # 注意：没有 Authorization header
    )

    # 断言：返回 401
    assert response.status_code == 401
```

**逐行解释**：

- `def test_create_post(auth_token, client):`：这个测试函数声明了两个 fixture 参数。pytest 会先执行 `client`，再执行 `auth_token`（因为 `auth_token` 依赖 `client`），然后把两个值都传给测试函数。
- `headers={"Authorization": f"Bearer {auth_token}"}`：在请求头中携带 JWT token。格式是 `Bearer <token>`。
- `test_create_post_without_auth`：不传 `Authorization` 头，断言返回 401（未授权）。

---

### 步骤 6：测试越权修改文章——`test_update_post_cross_owner`

```python
# ============================================================
# 四、权限测试
# ============================================================

def test_update_post_own_article(auth_token, client):
    """
    测试：作者修改自己的文章
    预期：返回 200
    """
    # 创建文章
    create_response = client.post(
        "/posts",
        json={"title": "我的文章", "content": "原始内容"},
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    post_id = create_response.json()["id"]

    # 修改文章
    response = client.put(
        f"/posts/{post_id}",
        json={"title": "修改后的标题", "content": "修改后的内容"},
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    assert response.status_code == 200
    assert response.json()["title"] == "修改后的标题"


def test_update_post_cross_owner(client):
    """
    测试：alice 的文章 → bob 的 token 尝试修改
    预期：返回 403
    """
    # alice 注册并创建文章
    client.post("/users", json={"username": "alice", "password": "alice123"})
    alice_login = client.post(
        "/login", json={"username": "alice", "password": "alice123"}
    )
    alice_token = alice_login.json()["access_token"]

    create_response = client.post(
        "/posts",
        json={"title": "alice 的文章", "content": "alice 的内容"},
        headers={"Authorization": f"Bearer {alice_token}"},
    )
    post_id = create_response.json()["id"]

    # bob 注册并登录
    client.post("/users", json={"username": "bob", "password": "bob123456"})
    bob_login = client.post(
        "/login", json={"username": "bob", "password": "bob123456"}
    )
    bob_token = bob_login.json()["access_token"]

    # bob 尝试修改 alice 的文章
    response = client.put(
        f"/posts/{post_id}",
        json={"title": "bob 想偷改", "content": "bob 的内容"},
        headers={"Authorization": f"Bearer {bob_token}"},
    )

    # 断言：返回 403（禁止）
    assert response.status_code == 403
```

**逐行解释**：

- `test_update_post_own_article`：测试作者修改自己的文章应该成功。先从创建文章的响应中拿到 `post_id`，再用这个 ID 去修改。
- `test_update_post_cross_owner`：测试越权操作——alice 创建文章，bob 尝试修改。`check_owner` 检查 `author_id` 不匹配，返回 403。这个测试验证了教程 17 的权限保护逻辑。

**比喻**：这个测试就像"门禁系统测试"——alice 的房间，bob 拿着自己的钥匙（token）去开门，门禁系统（`check_owner`）说："你不是这间房的主人，不能进。"

---

### 步骤 7：测试评论 CRUD

```python
# ============================================================
# 五、评论测试
# ============================================================

def test_create_comment(auth_token, client):
    """
    测试：给文章添加评论
    预期：返回 201，评论数据正确
    """
    # 先创建一篇文章
    create_response = client.post(
        "/posts",
        json={"title": "可评论的文章", "content": "文章内容"},
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    post_id = create_response.json()["id"]

    # 添加评论
    response = client.post(
        f"/posts/{post_id}/comments",
        json={"content": "写得真好！"},
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    assert response.status_code == 201
    data = response.json()
    assert data["content"] == "写得真好！"
    assert data["post_id"] == post_id


def test_get_comments(auth_token, client):
    """
    测试：获取文章的评论列表
    预期：返回 200，包含之前添加的评论
    """
    # 创建文章
    create_response = client.post(
        "/posts",
        json={"title": "评论测试文章", "content": "内容"},
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    post_id = create_response.json()["id"]

    # 添加两条评论
    client.post(
        f"/posts/{post_id}/comments",
        json={"content": "第一条评论"},
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    client.post(
        f"/posts/{post_id}/comments",
        json={"content": "第二条评论"},
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    # 获取评论列表
    response = client.get(f"/posts/{post_id}/comments")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["content"] == "第一条评论"
    assert data[1]["content"] == "第二条评论"
```

---

### 步骤 8：测试分页——`test_pagination`

```python
# ============================================================
# 六、分页测试
# ============================================================

def test_pagination(client):
    """
    测试：分页返回正确数量的文章
    预期：page=1&size=2 返回 2 条，page=2&size=2 返回剩余文章
    """
    # 先注册并登录
    client.post("/users", json={"username": "pager", "password": "pager123"})
    login_resp = client.post(
        "/login", json={"username": "pager", "password": "pager123"}
    )
    token = login_resp.json()["access_token"]

    # 创建 5 篇文章
    for i in range(1, 6):
        client.post(
            "/posts",
            json={"title": f"文章{i}", "content": f"内容{i}"},
            headers={"Authorization": f"Bearer {token}"},
        )

    # 第 1 页，每页 2 条
    response = client.get("/posts?page=1&size=2")
    data = response.json()

    assert response.status_code == 200
    assert len(data["items"]) == 2
    assert data["total"] == 5
    assert data["page"] == 1
    assert data["pages"] == 3  # 5 条 / 每页 2 条 → 向上取整 = 3 页

    # 第 3 页，只剩 1 条
    response = client.get("/posts?page=3&size=2")
    data = response.json()
    assert len(data["items"]) == 1
```

**逐行解释**：

- 创建 5 篇文章，然后分页查询。`page=1&size=2` 应该返回 2 条，`total=5`，`pages=3`。
- 第 3 页只剩 1 条文章（因为 5 条 / 每页 2 条 = 3 页，前 2 页各 2 条，第 3 页 1 条）。

---

### 步骤 9：测试搜索——`test_search`

```python
# ============================================================
# 七、搜索测试
# ============================================================

def test_search(client):
    """
    测试：关键词搜索
    预期：只返回标题或内容中包含关键词的文章
    """
    # 注册并登录
    client.post("/users", json={"username": "searcher", "password": "search123"})
    login_resp = client.post(
        "/login", json={"username": "searcher", "password": "search123"}
    )
    token = login_resp.json()["access_token"]

    # 创建几篇不同内容的文章
    client.post(
        "/posts",
        json={"title": "Python 入门教程", "content": "从零开始学 Python"},
        headers={"Authorization": f"Bearer {token}"},
    )
    client.post(
        "/posts",
        json={"title": "Java 入门教程", "content": "从零开始学 Java"},
        headers={"Authorization": f"Bearer {token}"},
    )
    client.post(
        "/posts",
        json={"title": "Python 进阶", "content": "深入理解 Python 特性"},
        headers={"Authorization": f"Bearer {token}"},
    )

    # 搜索 "Python"
    response = client.get("/posts?keyword=Python")
    data = response.json()

    assert response.status_code == 200
    # 应该只返回 2 篇包含 "Python" 的文章
    assert len(data["items"]) == 2
    # 确认每篇都包含 "Python"
    for item in data["items"]:
        assert "Python" in item["title"] or "Python" in item["content"]


def test_search_no_result(client):
    """
    测试：搜索不存在的关键词
    预期：返回空列表，total 为 0
    """
    response = client.get("/posts?keyword=不存在的关键词XYZ")
    data = response.json()

    assert response.status_code == 200
    assert len(data["items"]) == 0
    assert data["total"] == 0
```

---

### 步骤 10：运行全部测试——看到一片绿色 ✓

现在所有测试都写好了，运行全部测试：

```bash
pytest -v
```

**预期输出**：

```
============================= test session starts =============================
platform win32 -- Python 3.10.x, pytest-7.x.x, pluggy-1.x.x
rootdir: D:\Project\...
collected 11 items

blog_backend\test_main.py::test_register_user PASSED                    [  9%]
blog_backend\test_main.py::test_register_duplicate_user PASSED          [ 18%]
blog_backend\test_main.py::test_login_success PASSED                    [ 27%]
blog_backend\test_main.py::test_login_wrong_password PASSED             [ 36%]
blog_backend\test_main.py::test_create_post PASSED                      [ 45%]
blog_backend\test_main.py::test_create_post_without_auth PASSED         [ 54%]
blog_backend\test_main.py::test_update_post_own_article PASSED          [ 63%]
blog_backend\test_main.py::test_update_post_cross_owner PASSED          [ 72%]
blog_backend\test_main.py::test_create_comment PASSED                   [ 81%]
blog_backend\test_main.py::test_get_comments PASSED                     [ 90%]
blog_backend\test_main.py::test_pagination PASSED                       [100%]

============================== 11 passed in 1.xxs ==============================
```

**一片绿色！** 11 个测试全部通过。从现在开始，你每次改代码后，只需要跑一条命令，就知道有没有搞坏已有的功能。

**如果某个测试失败了怎么办？** 回顾教程 24 的步骤 7——pytest 的输出会告诉你：
1. 哪个测试失败了
2. 哪一行失败了
3. 实际值是什么
4. 期望值是什么
根据这些信息，定位问题，修复代码，再跑 `pytest -v`。

---

### 步骤 11：🤔 想多一点——什么时候一个测试就够了？

你可能会想："我只测了 `page=1&size=2`，要不要把所有分页组合都测一遍？"

**测试的原则：代表性覆盖，不是穷举。**

| 应该测的 | 不应该测的 |
|----------|-----------|
| 正常路径（分页返回正确数量） | 所有可能的 page/size 组合（没必要） |
| 边界条件（第 3 页只剩 1 条） | 每个接口的每种 JSON 字段组合 |
| 错误路径（未登录 401、越权 403） | 每种可能的错误密码组合 |
| 核心功能（注册、登录、CRUD、评论） | 内部辅助函数（除非是纯逻辑函数） |

**关键问题**：如果你改了代码，哪个场景最可能出问题？把那个场景写成测试，而不是把所有场景都测一遍。

---

### 步骤 12：测试覆盖率——pytest-cov

测试通过了，但你不知道"哪些代码被测试覆盖了，哪些代码没被测试到"。这时候就需要**覆盖率**工具。此术语需进附录。

安装 `pytest-cov`：

```powershell
pip install pytest-cov
```

运行覆盖率测试：

```bash
pytest --cov=blog_backend --cov-report=term-missing
```

**参数解释**：
- `--cov=blog_backend`：统计 `blog_backend` 包的覆盖率。
- `--cov-report=term-missing`：在终端输出报告，显示**哪些行没有被测试覆盖**。

**预期输出**：

```
Name                          Stmts   Miss  Cover   Missing
-----------------------------------------------------------
blog_backend\__init__.py          0      0   100%
blog_backend\auth.py             20      2    90%   45-46
blog_backend\database.py         10      0   100%
blog_backend\main.py             85     15    82%   120-125, 200-210
blog_backend\models.py           15      0   100%
blog_backend\schemas.py          12      0   100%
blog_backend\test_main.py        80      0   100%
-----------------------------------------------------------
TOTAL                           222     17    92%
```

**逐行解读**：

- `Stmts`：该文件的代码语句数（statements）。
- `Miss`：没有被测试覆盖的语句数。
- `Cover`：覆盖率百分比。
- `Missing`：**具体哪些行没有被覆盖**——比如 `auth.py` 的 45-46 行。你可以打开文件看那两行是什么，然后决定是否需要补充测试。

**比喻**：覆盖率报告就像"体检报告"——告诉你身体的哪些部位（代码的哪些行）被检查过了，哪些部位还没检查。92% 覆盖 = 92% 的代码被测试跑过，8% 的代码（如某些异常处理分支）还没被触发。

**覆盖率多少算好？** 没有绝对标准，但一般参考：
- 80%+：及格。
- 90%+：良好。
- 95%+：优秀。
- 100%：不必要追求——有些代码（如 `if __name__ == "__main__"`）很难测试，且不需要测试。

---

### 步骤 13：🤔 想多一点——如果我改了接口，测试也要改吗？

**是的。** 这就是测试的"维护成本"——代码变了，测试也要跟着变。

但这恰恰是测试的价值所在：

| 场景 | 没有测试 | 有测试 |
|------|----------|--------|
| 你改了接口的返回值格式 | 前端挂了，你才知道 | 测试失败，你第一时间知道 |
| 你删了一个接口 | 没人知道，直到有人调用报错 | 测试失败，CI 拦截 |
| 你加的接口有 bug | 上线后才发现 | 写测试时就能发现 |

**测试不是"写了就不管了"，而是"代码的一部分"。** 改了代码，同步更新测试，就像你改了函数签名，同步更新调用方一样。

**比喻**：测试是代码的"影子"——代码变，影子跟着变。如果你只改代码不改测试，影子就歪了，pytest 会告诉你"影子歪了"。

---

## 四、完整代码清单

### `blog_backend/conftest.py`（本章新建）

<details>
<summary>点击展开完整代码</summary>

```python
# blog_backend/conftest.py —— 测试配置与 fixture

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from blog_backend.database import Base, get_db
from blog_backend.main import app

# ============================================================
# 1. 创建独立的测试数据库
# ============================================================
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test_blog.db"

test_engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

TestSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine,
)

# ============================================================
# 2. 覆盖 get_db 依赖——让所有接口用测试数据库
# ============================================================
def override_get_db():
    try:
        db = TestSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


# ============================================================
# 3. fixture：自动创建和清理数据库表
# ============================================================
@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


# ============================================================
# 4. fixture：提供测试客户端
# ============================================================
@pytest.fixture
def client():
    return TestClient(app)


# ============================================================
# 5. fixture：提供已认证的 token
# ============================================================
@pytest.fixture
def auth_token(client):
    client.post(
        "/users",
        json={"username": "testuser", "password": "test123456"},
    )
    response = client.post(
        "/login",
        json={"username": "testuser", "password": "test123456"},
    )
    data = response.json()
    return data["access_token"]
```

</details>

### `blog_backend/test_main.py`（本章完整版）

<details>
<summary>点击展开完整代码</summary>

```python
# blog_backend/test_main.py —— 博客 API 完整测试


# ============================================================
# 一、用户注册测试
# ============================================================

def test_register_user(client):
    response = client.post(
        "/users",
        json={"username": "alice", "password": "alice123"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "alice"
    assert "password" not in data


def test_register_duplicate_user(client):
    client.post("/users", json={"username": "bob", "password": "bob123456"})
    response = client.post(
        "/users",
        json={"username": "bob", "password": "bob123456"},
    )
    assert response.status_code == 400


# ============================================================
# 二、用户登录测试
# ============================================================

def test_login_success(client):
    client.post("/users", json={"username": "charlie", "password": "charlie123"})
    response = client.post(
        "/login",
        json={"username": "charlie", "password": "charlie123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client):
    client.post("/users", json={"username": "dave", "password": "dave123456"})
    response = client.post(
        "/login",
        json={"username": "dave", "password": "wrong_password"},
    )
    assert response.status_code == 401


# ============================================================
# 三、文章创建测试
# ============================================================

def test_create_post(auth_token, client):
    response = client.post(
        "/posts",
        json={
            "title": "我的第一篇文章",
            "content": "这是文章内容。",
            "published": True,
        },
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "我的第一篇文章"
    assert data["content"] == "这是文章内容。"
    assert data["published"] is True
    assert "id" in data


def test_create_post_without_auth(client):
    response = client.post(
        "/posts",
        json={"title": "未登录创建", "content": "应该被拒绝。"},
    )
    assert response.status_code == 401


# ============================================================
# 四、权限测试
# ============================================================

def test_update_post_own_article(auth_token, client):
    create_response = client.post(
        "/posts",
        json={"title": "我的文章", "content": "原始内容"},
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    post_id = create_response.json()["id"]

    response = client.put(
        f"/posts/{post_id}",
        json={"title": "修改后的标题", "content": "修改后的内容"},
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == 200
    assert response.json()["title"] == "修改后的标题"


def test_update_post_cross_owner(client):
    # alice 注册并创建文章
    client.post("/users", json={"username": "alice", "password": "alice123"})
    alice_login = client.post(
        "/login", json={"username": "alice", "password": "alice123"}
    )
    alice_token = alice_login.json()["access_token"]

    create_response = client.post(
        "/posts",
        json={"title": "alice 的文章", "content": "alice 的内容"},
        headers={"Authorization": f"Bearer {alice_token}"},
    )
    post_id = create_response.json()["id"]

    # bob 注册并登录
    client.post("/users", json={"username": "bob", "password": "bob123456"})
    bob_login = client.post(
        "/login", json={"username": "bob", "password": "bob123456"}
    )
    bob_token = bob_login.json()["access_token"]

    # bob 尝试修改 alice 的文章
    response = client.put(
        f"/posts/{post_id}",
        json={"title": "bob 想偷改", "content": "bob 的内容"},
        headers={"Authorization": f"Bearer {bob_token}"},
    )
    assert response.status_code == 403


# ============================================================
# 五、评论测试
# ============================================================

def test_create_comment(auth_token, client):
    create_response = client.post(
        "/posts",
        json={"title": "可评论的文章", "content": "文章内容"},
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    post_id = create_response.json()["id"]

    response = client.post(
        f"/posts/{post_id}/comments",
        json={"content": "写得真好！"},
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["content"] == "写得真好！"
    assert data["post_id"] == post_id


def test_get_comments(auth_token, client):
    create_response = client.post(
        "/posts",
        json={"title": "评论测试文章", "content": "内容"},
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    post_id = create_response.json()["id"]

    client.post(
        f"/posts/{post_id}/comments",
        json={"content": "第一条评论"},
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    client.post(
        f"/posts/{post_id}/comments",
        json={"content": "第二条评论"},
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    response = client.get(f"/posts/{post_id}/comments")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["content"] == "第一条评论"
    assert data[1]["content"] == "第二条评论"


# ============================================================
# 六、分页测试
# ============================================================

def test_pagination(client):
    client.post("/users", json={"username": "pager", "password": "pager123"})
    login_resp = client.post(
        "/login", json={"username": "pager", "password": "pager123"}
    )
    token = login_resp.json()["access_token"]

    for i in range(1, 6):
        client.post(
            "/posts",
            json={"title": f"文章{i}", "content": f"内容{i}"},
            headers={"Authorization": f"Bearer {token}"},
        )

    response = client.get("/posts?page=1&size=2")
    data = response.json()
    assert response.status_code == 200
    assert len(data["items"]) == 2
    assert data["total"] == 5
    assert data["page"] == 1
    assert data["pages"] == 3

    response = client.get("/posts?page=3&size=2")
    data = response.json()
    assert len(data["items"]) == 1


# ============================================================
# 七、搜索测试
# ============================================================

def test_search(client):
    client.post("/users", json={"username": "searcher", "password": "search123"})
    login_resp = client.post(
        "/login", json={"username": "searcher", "password": "search123"}
    )
    token = login_resp.json()["access_token"]

    client.post(
        "/posts",
        json={"title": "Python 入门教程", "content": "从零开始学 Python"},
        headers={"Authorization": f"Bearer {token}"},
    )
    client.post(
        "/posts",
        json={"title": "Java 入门教程", "content": "从零开始学 Java"},
        headers={"Authorization": f"Bearer {token}"},
    )
    client.post(
        "/posts",
        json={"title": "Python 进阶", "content": "深入理解 Python 特性"},
        headers={"Authorization": f"Bearer {token}"},
    )

    response = client.get("/posts?keyword=Python")
    data = response.json()
    assert response.status_code == 200
    assert len(data["items"]) == 2
    for item in data["items"]:
        assert "Python" in item["title"] or "Python" in item["content"]


def test_search_no_result(client):
    response = client.get("/posts?keyword=不存在的关键词XYZ")
    data = response.json()
    assert response.status_code == 200
    assert len(data["items"]) == 0
    assert data["total"] == 0
```

</details>

---

## 五、验证方法

```bash
# 1. 运行全部测试 → 看到一片绿色 ✓
pytest -v
# → 11 个测试全部 PASSED

# 2. 运行覆盖率测试 → 看到覆盖率报告
pytest --cov=blog_backend --cov-report=term-missing
# → 看到每个文件的覆盖率百分比和未覆盖行号

# 3. 确认测试数据库已创建
dir *.db
# → 应该能看到 test_blog.db

# 4. 确认开发数据库没有被污染
# 打开 blog.db 检查，不应该有测试中创建的 "alice"、"bob" 等用户
```

---

## 六、术语附录

| 术语 | 英文 | 通俗解释 | 本章出现位置 |
|------|------|----------|-------------|
| fixture | pytest fixture | pytest 的核心机制，用 `@pytest.fixture` 装饰的函数。在测试前自动准备环境（setup），测试后自动清理（teardown）。比喻：每次考试前自动发空白试卷。 | 步骤 2 |
| `conftest.py` | — | pytest 的特殊文件名，放在测试目录下。pytest 自动加载其中的 fixture，同目录的所有测试文件共享。不需要手动导入。 | 步骤 2 |
| `autouse=True` | — | fixture 参数，设为 `True` 后，该 fixture 自动应用到所有测试函数，不需要在测试函数参数中声明。 | 步骤 2 |
| `yield` | — | Python 关键字。在 fixture 中，`yield` 之前是 setup 代码（测试前执行），`yield` 之后是 teardown 代码（测试后执行）。 | 步骤 2 |
| `dependency_overrides` | — | FastAPI 的依赖替换机制。`app.dependency_overrides[原依赖] = 新依赖`，在测试中把数据库连接替换为测试数据库，所有接口自动使用测试数据库。 | 步骤 2 |
| 测试数据库 | Test Database | 独立于开发数据库的数据库文件（如 `test_blog.db`）。测试数据写入这里，不影响开发数据。测试结束后可以清空或删除。 | 步骤 1 |
| 覆盖率 | Code Coverage | 衡量"测试代码执行了多少行业务代码"的指标。`pytest-cov` 可以统计覆盖率，显示哪些行被测试到了，哪些行没有被覆盖。 | 步骤 12 |
| pytest-cov | — | pytest 的覆盖率插件。`pip install pytest-cov` 安装后，用 `--cov=包名` 参数运行，自动统计代码覆盖率。 | 步骤 12 |
| setup / teardown | — | 测试术语。setup = 测试前的准备工作（创建数据库、准备数据），teardown = 测试后的清理工作（删除数据、关闭连接）。 | 步骤 2 |

---

## 七、小结

| 你学到了什么 | 一句话总结 |
|--------------|-----------|
| 测试数据库 | `test_blog.db` 独立于 `blog.db`，测试数据不污染开发数据 |
| pytest fixture | `@pytest.fixture` 自动准备和清理环境，比喻：每次考试前自动发空白试卷 |
| `conftest.py` | pytest 特殊文件，放 fixture 定义，同目录测试文件自动共享 |
| `dependency_overrides` | 替换 FastAPI 的数据库依赖，所有接口自动使用测试数据库 |
| `autouse=True` | fixture 自动应用到所有测试，不需要手动声明 |
| 用户注册测试 | 测试注册成功（201）和重复注册（400） |
| 用户登录测试 | 测试登录成功（200 + token）和密码错误（401） |
| 文章创建测试 | 测试带 token 创建（201）和不带 token 创建（401） |
| 越权修改测试 | alice 的文章 → bob 的 token → 403（权限保护生效） |
| 评论测试 | 测试创建评论（201）和获取评论列表（200） |
| 分页测试 | 测试分页返回正确数量和 total/pages 计算 |
| 搜索测试 | 测试关键词搜索返回匹配文章，无匹配返回空列表 |
| `pytest -v` | 一条命令跑完所有测试，全绿 = 放心 |
| `pytest-cov` | `--cov=blog_backend` 查看覆盖率，知道哪些代码没被测试 |

---

## 八、已知坑点与禁止事项

| 坑点 | 现象 | 原因 | 解决 |
|------|------|------|------|
| 测试用了开发数据库 | 测试创建的用户出现在 `blog.db` 中 | 没有覆盖 `get_db` 依赖，测试直接用了 `blog.db` | 在 `conftest.py` 中用 `app.dependency_overrides[get_db] = override_get_db` 指向测试数据库 |
| `conftest.py` 放在错误位置 | fixture 找不到，测试报 `fixture 'client' not found` | `conftest.py` 必须在测试文件所在目录或其父目录 | 放在 `blog_backend/conftest.py`（和 `test_main.py` 同目录） |
| 忘记 `connect_args={"check_same_thread": False}` | SQLite 报错 `threading` 相关错误 | SQLite 默认不允许跨线程使用同一个连接，FastAPI 的依赖注入可能在多个线程中调用 | 在 `create_engine` 中加上 `connect_args={"check_same_thread": False}` |
| fixture 中没有 `yield` | 数据库表在测试间没有被清理，数据残留 | 只写了 `create_all`，没写 `drop_all`，或者 `yield` 位置不对 | 确保 `yield` 之前是 `create_all`，`yield` 之后是 `drop_all` |
| 测试依赖顺序不对 | `auth_token` fixture 报错 | `auth_token` 依赖 `client`，但它声明了 `client` 参数，pytest 不知道该先创建哪个 | `auth_token` 的参数中声明 `client`，pytest 会自动按依赖顺序执行 |
| 测试数据库中重复注册用户 | `test_register_duplicate_user` 第一次注册失败 | 上一个测试的数据库清理不彻底，用户已存在 | 检查 `setup_database` fixture 的 `autouse=True` 和 `drop_all` 是否正确执行 |
| `pytest-cov` 未安装 | `pytest: error: unrecognized arguments: --cov` | 没装 `pytest-cov` 插件 | `pip install pytest-cov` |
| 覆盖率报告显示 0% | 所有文件覆盖率都是 0% | `--cov` 参数指定的包名不对，或者测试没运行到任何业务代码 | 确认 `--cov=blog_backend` 的包名与项目结构一致 |

---

## 九、下一步建议

阶段七（测试）全部完成！你的博客系统现在有了完整的自动化测试——11 个测试覆盖了注册、登录、文章 CRUD、评论、分页、搜索。从此改代码不再提心吊胆——跑一遍 `pytest -v`，全绿就放心。

**接下来**：阶段八（部署上线）——教程 26~29。你将学习 Linux 基础、购买云服务器、配置 Nginx + HTTPS、用 Docker 容器化部署。你的博客系统将真正"上线"，让全世界的人都能访问。

**试试看**：
- 给测试增加更多边界情况：密码太短（`test_register_short_password`）、文章标题为空（`test_create_post_empty_title`）。
- 运行 `pytest --cov=blog_backend --cov-report=html`，生成 HTML 格式的覆盖率报告，在浏览器中查看。
- 故意在 `main.py` 中改错一个接口（比如把 201 改成 200），运行 `pytest -v`，看哪个测试失败了。

---

> [可暂停点 8/9]：阶段七（测试）全部完成。你的博客系统有了完整的自动化测试——11 个测试，一条命令全跑完。接下来进入最后阶段：部署上线，让全世界看到你的作品。