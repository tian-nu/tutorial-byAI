# 18-用户登录与JWT认证

> "第 17 章用户能注册了，密码是哈希存的——但还不能登录。这一章实现登录接口：用邮箱和密码验证身份，验证通过后签发 JWT 令牌。你会理解 JWT 的三个部分（Header + Payload + Signature），明白为什么 JWT 不是加密而是签名，学会用 dotenv 管理敏感配置。做完之后，前端拿到 token 就能告诉后端 '我是谁'——这是认证系统的最后一块拼图。"

---

## 一、目标与完成效果

**一句话目标**：安装 `jsonwebtoken` 和 `dotenv`，创建登录接口 `POST /api/auth/login`，用 `bcrypt.compare()` 验证密码，签发 JWT 令牌，配置 `.env` 环境变量管理 `JWT_SECRET`。

**完成后的可观测效果**：
- 你安装了 `jsonwebtoken` 和 `dotenv`。
- 你创建了 `.env` 文件，包含 `JWT_SECRET` 环境变量，并加入 `.gitignore`。
- 你在 `server.js` 顶部添加了 `require('dotenv').config()`。
- 你在 `routes/auth.js` 中添加了 `POST /api/auth/login` 接口。
- 登录接口接收 `{ email, password }`，验证后返回 `{ success: true, data: { token, user: { id, username, email } } }`。
- 你用 Thunder Client 先注册再登录，拿到了 token。
- 你去 [jwt.io](https://jwt.io) 粘贴 token，能看到解码后的 Payload（证明 JWT 不是加密）。

---

## 二、前置条件

| 序号 | 条件 | 验证命令 |
|------|------|----------|
| 1 | 已完成教程 17，`POST /api/auth/register` 可用 | 用 Thunder Client 注册一个用户，返回 201 |
| 2 | `bcryptjs`（或 `bcrypt`）已安装 | `ls node_modules/bcryptjs` 文件夹存在 |
| 3 | 数据库中至少有一个通过注册接口创建的用户（密码是真正的 bcrypt 哈希） | `node -e "const {db}=require('./database/db');console.log(db.prepare('SELECT id,username,password_hash FROM users').all())"` 中至少有一个用户的 `password_hash` 以 `$2b$` 开头 |
| 4 | `utils/AppError.js` 已创建 | `ls utils/AppError.js` 文件存在 |

**一条命令确认前置满足**：

```bash
npm run dev
```

然后用 Thunder Client 发 `POST /api/auth/register` 注册一个新用户（如 `username: "logintest", email: "logintest@example.com", password: "test123456"`），返回 201，前置条件满足。

> ⚠️ **重要**：seed 脚本创建的 alice 和 bob 的 `password_hash` 是 `'hash_placeholder'`（不是真正的 bcrypt 哈希），**无法用于登录**。你必须通过注册接口创建一个新用户来测试登录。

---

## 三、分步操作

### 步骤 1：安装依赖

```bash
npm install jsonwebtoken dotenv
```

- `jsonwebtoken`：签发和验证 JWT 令牌。
- `dotenv`：从 `.env` 文件加载环境变量到 `process.env`。

---

### 步骤 2：JWT 是什么——"三个部分的令牌"

JWT（JSON Web Token）是一个**自包含的令牌**，由三个部分组成，用 `.` 分隔：

```
eyJhbGciOiJIUzI1NiJ9.eyJ1c2VySWQiOjN9.4a7d8f9g...
^^^^^^^ HEADER ^^^^^^^  ^^^ PAYLOAD ^^^  ^^ SIGNATURE ^^
```

#### 2.1 Header（头部）

```json
{
  "alg": "HS256",
  "typ": "JWT"
}
```

用 Base64 编码后变成第一部分。它告诉服务器："我用的是 HS256 算法签名的 JWT。"

#### 2.2 Payload（负载）

```json
{
  "userId": 3,
  "username": "charlie",
  "iat": 1718200000,
  "exp": 1718804800
}
```

用 Base64 编码后变成第二部分。**这是 JWT 携带的数据**——用户 ID、用户名、签发时间、过期时间等。

#### 2.3 Signature（签名）

```
HMACSHA256(
  base64UrlEncode(header) + "." + base64UrlEncode(payload),
  JWT_SECRET
)
```

用服务器持有的密钥（`JWT_SECRET`）对前两部分签名，生成第三部分。**签名保证了前两部分没有被篡改**——如果有人改了 Payload（比如把 `userId` 从 3 改成 1），签名就对不上了，服务器会拒绝。

> **信封比喻**：
> - **Header** = 信封（告诉你怎么拆）
> - **Payload** = 信纸内容（写着你是谁）
> - **Signature** = 蜡封（证明这封信没被拆过、没被篡改）

#### 2.4 重点：JWT 不是加密，是签名

**Payload 里的内容任何人都能 Base64 解码看！** Base64 不是加密，只是"编码"——就像把中文翻译成摩斯密码，任何人都能翻译回来。

```
演示：去 jwt.io 粘贴一个 token，右边的 Payload 部分直接显示解码后的内容。
```

**所以绝对不要在 JWT 的 Payload 里放敏感信息**（如密码、信用卡号、身份证号）。Payload 只放"不敏感但需要验证完整性"的信息（如用户 ID、用户名、过期时间）。

---

### 步骤 3：创建 .env 文件——JWT_SECRET 环境变量

在 `blog-backend/` 根目录创建 `.env` 文件：

```bash
# .env — 环境变量（绝对不要提交到 Git！）
JWT_SECRET=your_super_secret_jwt_key_change_in_production_min_32_chars
```

> 🔥 **魔鬼细节**：`JWT_SECRET` 不能写死在代码里。如果写死在代码里，一旦代码泄露（比如开源到 GitHub），攻击者就能伪造任意用户的 JWT——他们可以自己签发 `{ userId: 1, username: "admin" }` 的令牌，以管理员身份登录。

**确保 `.gitignore` 包含 `.env`**：

```bash
# .gitignore
node_modules/
blog.db
.env            # ← 确保这一行存在
```

如果 `.gitignore` 中没有 `.env`，现在加上：

```bash
echo ".env" >> .gitignore
```

> 🔥 **魔鬼细节**：生产环境 `JWT_SECRET` 应该是一个**至少 32 字符的随机字符串**。你可以用以下命令生成：`node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"`。本教程用占位符 `your_super_secret_jwt_key_change_in_production_min_32_chars`，实际部署前务必替换。

---

### 步骤 4：在 server.js 顶部加载 dotenv

在 `server.js` 的**最顶部**（在所有 `require` 之前）添加：

```javascript
require('dotenv').config();   // ← 必须在所有代码之前加载环境变量

const express = require('express');
const AppError = require('./utils/AppError');
// ... 其余代码
```

> 🔥 **魔鬼细节**：`require('dotenv').config()` 必须在**文件最顶部**——在所有其他 `require` 之前。如果放在后面，有些模块在加载时可能已经读取了 `process.env`，此时环境变量还没加载进去，导致 `undefined`。

---

### 步骤 5：添加登录接口到 routes/auth.js

打开 `routes/auth.js`，在 `module.exports = router;` 之前添加登录接口：

```javascript
const jwt = require('jsonwebtoken');    // ← 新增：在文件顶部引入

// ... 注册接口保持不变 ...

// POST /api/auth/login — 用户登录
router.post('/login', async (req, res) => {
    const { email, password } = req.body;

    // 1. 验证必填字段
    if (!email || !password) {
        throw new AppError('邮箱和密码为必填字段', 400);
    }

    // 2. 查找用户（通过 email）
    const user = db.prepare(
        'SELECT id, username, email, password_hash FROM users WHERE email = ?'
    ).get(email);

    if (!user) {
        throw new AppError('邮箱或密码错误', 401);
    }

    // 3. 验证密码
    const isPasswordValid = await bcrypt.compare(password, user.password_hash);
    if (!isPasswordValid) {
        throw new AppError('邮箱或密码错误', 401);
    }

    // 4. 签发 JWT
    const token = jwt.sign(
        { userId: user.id, username: user.username },  // Payload
        process.env.JWT_SECRET,                         // 密钥
        { expiresIn: '7d' }                              // 过期时间
    );

    // 5. 返回 token 和用户信息（不返回 password_hash！）
    res.json({
        success: true,
        data: {
            token: token,
            user: {
                id: user.id,
                username: user.username,
                email: user.email
            }
        }
    });
});
```

**关键点解析**：

| 步骤 | 做什么 | 为什么 |
|------|--------|--------|
| 1 | 验证输入 | 邮箱和密码都是必填 |
| 2 | `SELECT ... WHERE email = ?` | 通过邮箱查找用户——邮箱是唯一的登录凭证 |
| 3 | `bcrypt.compare(password, hash)` | 把用户输入的密码哈希后，与数据库中的哈希值比对 |
| 4 | `jwt.sign(payload, secret, options)` | 签发 JWT——Payload 放用户信息，`expiresIn` 控制有效期 |
| 5 | 返回 token + 用户信息 | 不返回 `password_hash`，和注册接口保持一致 |

> 🔥 **魔鬼细节**：登录失败时**不要区分"邮箱不存在"和"密码错误"**。如果返回 `"邮箱不存在"`，攻击者可以枚举哪些邮箱已注册（用户枚举攻击）。始终返回统一的 `"邮箱或密码错误"`（401），不给攻击者任何线索。

> 🔥 **魔鬼细节**：`bcrypt.compare()` 也是异步的，必须用 `await`。处理函数要加 `async`。

> 🔥 **魔鬼细节**：Token 过期时间 `expiresIn: '7d'` 表示 7 天。太短（如 1 小时）用户体验差——频繁重新登录；太长（如 1 年）安全风险高——token 泄露后攻击者有很长时间可以利用。7 天是常见选择，配合 Refresh Token 机制可以做到"短期 token + 长期刷新"。

---

### 步骤 6：完整 routes/auth.js 一览

```javascript
const express = require('express');
const router = express.Router();
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');          // ← 新增
const { db } = require('../database/db');
const AppError = require('../utils/AppError');

// ========== 认证接口 ==========

// POST /api/auth/register — 用户注册
router.post('/register', async (req, res) => {
    const { username, email, password } = req.body;

    if (!username || !email || !password) {
        throw new AppError('用户名、邮箱和密码为必填字段', 400);
    }

    if (password.length < 6) {
        throw new AppError('密码至少需要 6 位', 400);
    }

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
        throw new AppError('邮箱格式不正确', 400);
    }

    const existingUser = db.prepare('SELECT id FROM users WHERE username = ?').get(username);
    if (existingUser) {
        throw new AppError('用户名已被注册', 409);
    }

    const existingEmail = db.prepare('SELECT id FROM users WHERE email = ?').get(email);
    if (existingEmail) {
        throw new AppError('邮箱已被注册', 409);
    }

    const saltRounds = 10;
    const password_hash = await bcrypt.hash(password, saltRounds);

    const now = new Date().toISOString();
    const insertUser = db.prepare(`
        INSERT INTO users (username, email, password_hash, created_at)
        VALUES (?, ?, ?, ?)
    `);

    const result = insertUser.run(username, email, password_hash, now);

    const newUser = db.prepare(
        'SELECT id, username, email, created_at FROM users WHERE id = ?'
    ).get(result.lastInsertRowid);

    res.status(201).json({
        success: true,
        data: newUser
    });
});

// POST /api/auth/login — 用户登录（本章新增）
router.post('/login', async (req, res) => {
    const { email, password } = req.body;

    if (!email || !password) {
        throw new AppError('邮箱和密码为必填字段', 400);
    }

    const user = db.prepare(
        'SELECT id, username, email, password_hash FROM users WHERE email = ?'
    ).get(email);

    if (!user) {
        throw new AppError('邮箱或密码错误', 401);
    }

    const isPasswordValid = await bcrypt.compare(password, user.password_hash);
    if (!isPasswordValid) {
        throw new AppError('邮箱或密码错误', 401);
    }

    const token = jwt.sign(
        { userId: user.id, username: user.username },
        process.env.JWT_SECRET,
        { expiresIn: '7d' }
    );

    res.json({
        success: true,
        data: {
            token: token,
            user: {
                id: user.id,
                username: user.username,
                email: user.email
            }
        }
    });
});

module.exports = router;
```

---

### 步骤 7：用 Thunder Client 测试登录

#### 7.1 先注册一个用户

如果你还没有可用的用户，先注册：

| 设置项 | 值 |
|--------|-----|
| Method | `POST` |
| URL | `http://localhost:3000/api/auth/register` |
| Body (JSON) | `{"username": "testuser", "email": "test@example.com", "password": "test123456"}` |

预期：201，返回用户信息。

#### 7.2 登录

| 设置项 | 值 |
|--------|-----|
| Method | `POST` |
| URL | `http://localhost:3000/api/auth/login` |
| Body (JSON) | `{"email": "test@example.com", "password": "test123456"}` |

**预期响应**（200）：

```json
{
  "success": true,
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOjMsInVzZXJuYW1lIjoidGVzdHVzZXIiLCJpYXQiOjE3MTgyMDAwMDAsImV4cCI6MTcxODgwNDgwMH0.xyz...",
    "user": {
      "id": 3,
      "username": "testuser",
      "email": "test@example.com"
    }
  }
}
```

**复制这个 token！** 下一章会用到。

#### 7.3 去 jwt.io 验证 token

1. 打开 [jwt.io](https://jwt.io)。
2. 把 token 粘贴到左侧的 "Encoded" 框里。
3. 右侧 "Decoded" 区域会显示 Payload 的内容：

```json
{
  "userId": 3,
  "username": "testuser",
  "iat": 1718200000,
  "exp": 1718804800
}
```

**你看到了吗？** Payload 的内容是明文可见的——任何人都能解码。这就是为什么我们说"JWT 不是加密，是签名"。

#### 7.4 测试各种错误场景

| 测试 | Body | 预期状态码 | 预期错误信息 |
|------|------|-----------|-------------|
| 缺少密码 | `{"email":"test@example.com"}` | 400 | 邮箱和密码为必填字段 |
| 邮箱不存在 | `{"email":"nobody@test.com","password":"123456"}` | 401 | 邮箱或密码错误 |
| 密码错误 | `{"email":"test@example.com","password":"wrongpassword"}` | 401 | 邮箱或密码错误 |
| 用 seed 用户登录 | `{"email":"alice@example.com","password":"anything"}` | 401 | 邮箱或密码错误（因为 `password_hash` 是 `hash_placeholder`，不是真正的 bcrypt 哈希） |

> 注意：邮箱不存在和密码错误返回**完全相同的错误信息**（"邮箱或密码错误"）——这是安全设计，防止用户枚举攻击。

---

### 🤔 想多一点：Token 过期后怎么办？

JWT 的 `expiresIn` 到期后，`jwt.verify()` 会抛出 `TokenExpiredError`。此时前端应该：

1. 检测到 401 响应（token 过期）。
2. 引导用户重新登录。
3. 或者用 Refresh Token 机制自动刷新——但这需要额外的 Refresh Token 接口，不在本教程范围内。

**Refresh Token 的简单原理**：登录时签发两个 token——`accessToken`（短期，如 15 分钟）和 `refreshToken`（长期，如 30 天）。`accessToken` 过期后，前端用 `refreshToken` 去换一个新的 `accessToken`。这样即使 `accessToken` 泄露，攻击者也只用 15 分钟的窗口。

---

### ❌ 常见错误 → ✅ 解决方案

| 错误信息 / 现象 | 原因 | 解决 |
|-----------------|------|------|
| `Cannot find module 'jsonwebtoken'` | 没安装 `jsonwebtoken` | `npm install jsonwebtoken` |
| `JWT_SECRET is not defined` / `secretOrPrivateKey must have a value` | 没创建 `.env` 文件，或 `dotenv` 没加载 | 创建 `.env` 文件，确保 `server.js` 顶部有 `require('dotenv').config()` |
| `secretOrPrivateKey must have a value` | `.env` 文件存在，但 `dotenv` 加载顺序错误 | 把 `require('dotenv').config()` 移到 `server.js` 最顶部 |
| 登录始终返回 401 "邮箱或密码错误" | 用户是 seed 脚本创建的，`password_hash` 是 `'hash_placeholder'` | 通过注册接口创建新用户再登录 |
| 登录成功但没有 token 返回 | 忘了 `jwt.sign()` 或拼写错误 | 确认代码中有 `const token = jwt.sign(...)` |
| `bcrypt.compare is not a function` | 忘了 `require('bcryptjs')` 或拼写错误 | 确认文件顶部有 `const bcrypt = require('bcryptjs')` |
| 登录时 `bcrypt.compare` 报错 `data and hash arguments required` | `user.password_hash` 是 `undefined`——用户不存在或 SELECT 没查 `password_hash` | 确认 SELECT 语句包含 `password_hash` 列 |
| `.env` 文件被提交到 Git | 忘了在 `.gitignore` 中加 `.env` | 立即 `git rm --cached .env`，添加 `.env` 到 `.gitignore`，重新提交 |

---

## 四、完整代码清单

### `blog-backend/routes/auth.js`（本章新增登录接口）

```javascript
const express = require('express');
const router = express.Router();
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const { db } = require('../database/db');
const AppError = require('../utils/AppError');

// ========== 认证接口 ==========

// POST /api/auth/register — 用户注册
router.post('/register', async (req, res) => {
    const { username, email, password } = req.body;

    if (!username || !email || !password) {
        throw new AppError('用户名、邮箱和密码为必填字段', 400);
    }

    if (password.length < 6) {
        throw new AppError('密码至少需要 6 位', 400);
    }

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
        throw new AppError('邮箱格式不正确', 400);
    }

    const existingUser = db.prepare('SELECT id FROM users WHERE username = ?').get(username);
    if (existingUser) {
        throw new AppError('用户名已被注册', 409);
    }

    const existingEmail = db.prepare('SELECT id FROM users WHERE email = ?').get(email);
    if (existingEmail) {
        throw new AppError('邮箱已被注册', 409);
    }

    const saltRounds = 10;
    const password_hash = await bcrypt.hash(password, saltRounds);

    const now = new Date().toISOString();
    const insertUser = db.prepare(`
        INSERT INTO users (username, email, password_hash, created_at)
        VALUES (?, ?, ?, ?)
    `);

    const result = insertUser.run(username, email, password_hash, now);

    const newUser = db.prepare(
        'SELECT id, username, email, created_at FROM users WHERE id = ?'
    ).get(result.lastInsertRowid);

    res.status(201).json({
        success: true,
        data: newUser
    });
});

// POST /api/auth/login — 用户登录
router.post('/login', async (req, res) => {
    const { email, password } = req.body;

    if (!email || !password) {
        throw new AppError('邮箱和密码为必填字段', 400);
    }

    const user = db.prepare(
        'SELECT id, username, email, password_hash FROM users WHERE email = ?'
    ).get(email);

    if (!user) {
        throw new AppError('邮箱或密码错误', 401);
    }

    const isPasswordValid = await bcrypt.compare(password, user.password_hash);
    if (!isPasswordValid) {
        throw new AppError('邮箱或密码错误', 401);
    }

    const token = jwt.sign(
        { userId: user.id, username: user.username },
        process.env.JWT_SECRET,
        { expiresIn: '7d' }
    );

    res.json({
        success: true,
        data: {
            token: token,
            user: {
                id: user.id,
                username: user.username,
                email: user.email
            }
        }
    });
});

module.exports = router;
```

### `blog-backend/server.js` 变更（顶部新增 dotenv 加载）

```javascript
require('dotenv').config();   // ← 新增：必须在最顶部

const express = require('express');
// ... 其余代码不变 ...
```

### `blog-backend/.env`（本章新建）

```bash
JWT_SECRET=your_super_secret_jwt_key_change_in_production_min_32_chars
```

### `blog-backend/` 目录结构（本章最终状态）

```
blog-backend/
├── server.js                  ← 顶部新增 dotenv 加载
├── package.json               ← 新增 jsonwebtoken、dotenv 依赖
├── package-lock.json
├── .gitignore                 ← 确保包含 .env
├── .env                       ← 本章新建（不提交到 Git！）
├── blog.db
├── node_modules/
├── database/
│   ├── db.js
│   ├── schema.js
│   └── seed.js
├── routes/
│   ├── articles.js
│   └── auth.js                ← 本章新增登录接口
├── middleware/
│   ├── logger.js
│   └── errorHandler.js
└── utils/
    └── AppError.js
```

---

## 五、验证方法

| 序号 | 操作 | 预期结果 |
|------|------|----------|
| 1 | `npm run dev` | 正常启动，无报错 |
| 2 | `POST /api/auth/register`，注册新用户 `{"username":"logintest","email":"logintest@test.com","password":"test123456"}` | 201 |
| 3 | `POST /api/auth/login`，Body: `{"email":"logintest@test.com","password":"test123456"}` | 200，返回 `{ token: "eyJ...", user: {...} }` |
| 4 | `POST /api/auth/login`，Body: `{"email":"logintest@test.com","password":"wrong"}` | 401，`邮箱或密码错误` |
| 5 | `POST /api/auth/login`，Body: `{"email":"nobody@test.com","password":"test123456"}` | 401，`邮箱或密码错误`（和密码错误返回相同信息） |
| 6 | 去 [jwt.io](https://jwt.io) 粘贴 token | 能看到解码后的 Payload（`userId`, `username`, `iat`, `exp`） |
| 7 | `POST /api/auth/login`，Body: `{"email":"alice@example.com","password":"anything"}` | 401（seed 用户无法登录，因为 `password_hash` 是占位符） |

全部通过？你的博客系统现在有了完整的注册和登录功能——用户注册后密码哈希存储，登录后获得 JWT 令牌。

---

## 六、小结表格

| 学到的东西 | 一句话解释 |
|-----------|-----------|
| JWT 三个部分 | Header（算法）+ Payload（数据）+ Signature（签名） |
| JWT 是签名不是加密 | Payload 任何人都能 Base64 解码——不要放敏感信息 |
| `jwt.sign(payload, secret, options)` | 用密钥签发 JWT，`expiresIn` 控制有效期 |
| `bcrypt.compare(password, hash)` | 把用户输入的密码哈希后，与数据库中的哈希值比对 |
| 登录失败统一错误信息 | 不区分"邮箱不存在"和"密码错误"，防止用户枚举 |
| `dotenv` | 从 `.env` 文件加载环境变量到 `process.env` |
| `.env` 不入库 | JWT_SECRET 等敏感信息通过 `.env` 管理，`.gitignore` 排除 |
| 401 Unauthorized | "你没有提供有效的凭证"——未登录或 token 无效 |

---

## 七、术语附录

| 术语 | 英文 | 通俗解释 | 本章出现位置 | 字面陷阱 |
|------|------|----------|-------------|----------|
| JWT | JSON Web Token | 一种自包含的令牌，由 Header + Payload + Signature 三部分组成。用于在前后端之间安全地传递用户身份信息。 | 步骤 2 | 不是"加密"——JWT 是签名的，Payload 是 Base64 编码（可解码），不是加密（不可解） |
| Header | — | JWT 的第一部分，声明签名算法（如 HS256）和令牌类型。 | 步骤 2.1 | 不是 HTTP 请求头——虽然都有"Header"这个词，但 JWT Header 是令牌内部的第一部分 |
| Payload | — | JWT 的第二部分，存放实际数据（如 userId、username、过期时间）。 | 步骤 2.2 | 不是"负载"= 服务器压力——是"载荷"，指令牌携带的数据 |
| Signature | — | JWT 的第三部分，用密钥对前两部分签名，防止篡改。 | 步骤 2.3 | 不是"签名"= 手写签字——是加密学中的"数字签名"，用密钥生成的校验码 |
| Bearer Token | — | 放在 HTTP 请求头 `Authorization: Bearer <token>` 中的令牌。谁持有这个 token，谁就被认为是该用户。 | 步骤 7 | 不是"熊"——Bearer 意为"持有者"，"持有令牌的人" |
| Token 过期 | Token Expiration | JWT 的 `exp` 字段标识的过期时间。过期后 `jwt.verify()` 会拒绝该 token。 | 步骤 5 | 不是"过期"= token 失效就没了——token 本身还在，只是服务器不再接受 |
| dotenv | — | Node.js 库，把 `.env` 文件中的键值对加载到 `process.env`。 | 步骤 3 | 不是"dot" = 点号——是 "dot" + "env"，".env 文件"的意思 |
| 环境变量 | Environment Variable | 操作系统级别的键值对配置，在 Node.js 中通过 `process.env` 访问。 | 步骤 3-4 | 不是"环境"= 自然环境——是"程序运行环境"的配置参数 |
| 用户枚举攻击 | User Enumeration | 攻击者通过不同的错误信息判断哪些邮箱/用户名已注册。 | 步骤 5 | 不是"枚举"= 一一列举——是"逐个试探"，通过系统反馈确认有效账号 |

---

## 八、已知坑点与禁止事项

1. **JWT 不是加密**：Payload 是 Base64 编码，任何人都能解码。**绝对不要在 Payload 里放密码、信用卡号等敏感信息。**

2. **`JWT_SECRET` 必须用环境变量**：不能写死在代码里。一旦代码泄露，攻击者可以伪造任意用户的 JWT。

3. **`.env` 必须加入 `.gitignore`**：永远不要把 `.env` 提交到 Git。如果已经提交了，立即 `git rm --cached .env` 并轮换密钥。

4. **生产环境 `JWT_SECRET` 必须是强随机字符串**：至少 32 字符。用 `node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"` 生成。

5. **登录失败不区分"邮箱不存在"和"密码错误"**：统一返回 `"邮箱或密码错误"`，防止用户枚举攻击。

6. **`bcrypt.compare()` 是异步的**：必须用 `await`，处理函数加 `async`。

7. **seed 脚本的用户不能登录**：`password_hash` 是 `'hash_placeholder'`，不是真正的 bcrypt 哈希。必须通过注册接口创建新用户来测试登录。

8. **`require('dotenv').config()` 必须在 `server.js` 最顶部**：放在所有其他 `require` 之前，否则某些模块可能读取不到环境变量。

---

## 九、下一步建议

登录接口已经完成。用户能拿到 token 了——但后端还没用 token 保护接口。任何人都还能随意创建、修改、删除文章。下一章创建认证中间件：

- **下一章**：[19-权限保护：认证中间件](19-权限保护：认证中间件.md) —— 创建认证中间件，从请求头提取 JWT 并验证，把用户信息挂到 `req.user`，让受保护的接口知道"当前是谁在操作"。
- **延伸思考**：Token 过期后怎么办？生产环境通常用"Access Token + Refresh Token"双令牌模式。Access Token 短期（15 分钟），Refresh Token 长期（30 天）。你可以研究一下如何实现。

---

> 📊 本教程无可视化
>
> 本教程编辑记录：2026-06-12 初始版本。