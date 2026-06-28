# 26-Jest + supertest：为博客 API 写测试

> "理论讲完了，动手吧。这一章你将为博客系统的全部接口写自动化测试——注册、登录、文章 CRUD、权限检查、认证拦截。安装 Jest 和 supertest，改造 server.js，创建独立测试数据库，写 18 个测试用例，最后一条 `npm test` 看到一片绿色 ✓。从今天起，你改代码不再靠猜，而是靠测试告诉你——改坏了没有。"

---

## 一、目标与完成效果

**一句话目标**：安装 Jest + supertest，改造 `server.js` 导出 `app` 对象，创建独立测试数据库，为博客系统写 18 个集成测试用例，运行 `npm test` 看到全部通过。

**完成后的可观测效果**：
- `npm install --save-dev jest supertest` 安装完成。
- `server.js` 改造完成：`app.listen` 只在直接运行时启动，`module.exports = app` 导出供测试使用。
- 新建 `tests/setup.js`——用独立 SQLite 测试数据库（`test.db`），`beforeAll` 建表，`beforeEach` 清空数据，`afterAll` 关闭连接。
- 新建 `jest.config.js`——配置 Jest 使用 Node 环境。
- 新建 `tests/auth.test.js`——5 个测试用例：注册、重复注册、登录、密码错误、用户不存在。
- 新建 `tests/articles.test.js`——13 个测试用例：获取全部、获取单篇、404、创建、缺少字段、更新、更新 404、删除、删除 404、无 token 401、无效 token 401、跨用户修改 403、跨用户删除 403。
- 运行 `npm test`，终端输出 `18 passed, 18 total`，一片绿色 ✓。
- 测试数据全部写入 `tests/test.db`，你的开发数据 `blog.db` 完全不受影响。

---

## 二、前置条件

| 序号 | 条件 | 验证命令 |
|------|------|----------|
| 1 | 已完成教程 25，理解测试的意义和策略 | 能用口述解释"测试金字塔"和"为什么需要独立测试数据库" |
| 2 | 博客系统所有接口正常运行 | `npm run dev` 正常启动，`GET /api/articles` 返回数据 |
| 3 | `server.js` 当前在第 24 章之后的最终状态 | `server.js` 包含所有路由（articles、auth、comments、upload）和中间件 |
| 4 | 项目使用 CommonJS 模块系统 | `package.json` 中没有 `"type": "module"` |

**一条命令确认前置满足**：

```bash
npm run dev
```

终端输出 "Server is running on http://localhost:3000"，且用 Thunder Client 发 `POST /api/auth/login` Body: `{"username":"alice","password":"alice123"}` 能返回 token，前置条件满足。

---

## 三、分步操作

### 步骤 1：安装 Jest 和 supertest

两个工具一把装：

```bash
npm install --save-dev jest supertest
```

**参数解释**：
- `--save-dev`：安装为开发依赖（`devDependencies`）。这意味着这些工具只在开发/测试时使用，生产环境部署时不需要。
- `jest`：测试框架。此术语需进附录。负责运行测试、断言、输出报告。
- `supertest`：HTTP 测试库。此术语需进附录。负责向 Express app 模拟 HTTP 请求。

**验证安装**：

```bash
npx jest --version
```

输出类似 `29.x.x`，安装成功。

**比喻**：Jest 是"考试系统"——负责出题、收卷、打分。supertest 是"答题笔"——负责在试卷上写字（发 HTTP 请求）。两者配合，自动化考试一条龙。

---

### 步骤 2：Jest 基础——三件套：describe、it、expect

在写测试之前，先了解 Jest 的三个核心 API。**你不需要背，写的时候对照着看就行。**

#### 2.1 `describe`——测试组

```javascript
describe('文章 CRUD 接口', () => {
    // 这一组的所有测试都跟"文章 CRUD"相关
});
```

`describe` 把一组相关的测试用例包在一起，让输出更清晰。可以嵌套：

```javascript
describe('文章 CRUD 接口', () => {
    describe('GET /api/articles', () => {
        // 测试获取文章列表
    });
    describe('POST /api/articles', () => {
        // 测试创建文章
    });
});
```

**比喻**：`describe` 就像考试的分卷——"第一卷：选择题"、"第二卷：填空题"。每个分卷里有多道题。

#### 2.2 `it`（或 `test`）——单个测试用例

```javascript
it('获取所有文章应返回 200', async () => {
    // 测试逻辑
});
```

`it` 定义一个测试用例。第一个参数是描述（用"应该 xxx"的句式），第二个参数是测试函数。`test` 和 `it` 完全等价，本教程用 `it`。

**命名规范**：`it('应该做什么', () => { ... })`。如 `it('创建文章缺少标题应返回 400', ...)`。

#### 2.3 `expect`——断言

```javascript
expect(实际值).toBe(期望值);
```

`expect` 是 Jest 的断言函数。此术语需进附录。它检查"实际值是否等于期望值"。如果不等，测试失败。

**常用断言方法**：

| 方法 | 含义 | 示例 |
|------|------|------|
| `.toBe(value)` | 严格相等（`===`） | `expect(res.status).toBe(200)` |
| `.toEqual(value)` | 深度相等（对象/数组） | `expect(res.body).toEqual({ success: true })` |
| `.toBeTruthy()` | 真值（不为 `null`/`undefined`/`false`/`0`/`""`） | `expect(res.body.data.token).toBeTruthy()` |
| `.toHaveProperty(path)` | 对象有某个属性 | `expect(res.body.data).toHaveProperty('token')` |
| `.toContain(item)` | 数组/字符串包含某元素 | `expect(res.body.data.articles).toContainEqual(expect.objectContaining({ title: '测试' }))` |

**比喻**：`expect` 就像"标准答案比对器"——你告诉它"我认为实际值应该是 X"，它检查实际值是不是 X。是 → 打勾，不是 → 打叉并告诉你差在哪里。

---

### 步骤 3：supertest 基础——不发 HTTP 请求的 HTTP 测试

supertest 的核心用法就一行：

```javascript
const request = require('supertest');
const app = require('../server');  // 导入 Express app

// 发 GET 请求，期望 200
await request(app).get('/api/articles').expect(200);
```

**关键理解**：`request(app)` 不需要服务器真正启动。supertest 在内存中直接调用 Express 的请求处理函数，模拟 HTTP 请求。**不需要 `app.listen(3000)`，不需要 `npm run dev`。**

**常用方法链**：

```javascript
await request(app)
    .get('/api/articles')                    // GET 请求
    .set('Authorization', `Bearer ${token}`) // 设置请求头
    .query({ page: 1, limit: 5 })           // 查询参数
    .expect(200);                            // 期望状态码

await request(app)
    .post('/api/auth/register')              // POST 请求
    .send({ username: 'test', password: '123456' })  // 请求体
    .expect(201);                            // 期望状态码
```

**请求方法**：`.get()` / `.post()` / `.put()` / `.delete()` 对应 HTTP 方法。
**请求头**：`.set('Header-Name', 'value')` 设置请求头。
**请求体**：`.send({ ... })` 发送 JSON 请求体。
**查询参数**：`.query({ key: 'value' })` 设置 URL 查询参数。
**期望**：`.expect(statusCode)` 断言状态码。

> 🔥 **魔鬼细节**：supertest 的 `request(app)` 不会启动 TCP 端口，不会占用 `3000`。你可以在测试运行时同时 `npm run dev` 启动开发服务器——两者互不干扰。因为 supertest 走的是"内存通道"，开发服务器走的是"网络通道"。

**比喻**：supertest 就像一个"内部测试员"——他不需要从外面打电话（HTTP 请求），而是直接走进服务器内部问："嘿，如果现在有人发一个 POST /api/articles，你会怎么回答？"服务器回答后，测试员检查答案对不对。

---

### 步骤 4：改造 server.js——分离 app 和 listen

**问题**：当前 `server.js` 在文件末尾直接 `app.listen(3000, ...)`。如果测试文件 `require('./server')`，服务器就会启动——这会导致端口冲突，而且测试结束时服务器还在运行。

**解决**：把 `app.listen` 放到一个条件判断里——只有当 `server.js` 被直接运行（`node server.js`）时才启动服务器。如果被 `require` 导入（测试中），只导出 `app` 对象。

#### 4.1 改造前（当前 server.js 末尾）

```javascript
// ... 路由和中间件 ...

// ❌ 直接启动——测试时也会启动
app.listen(PORT, () => {
    console.log(`Server is running on http://localhost:${PORT}`);
});

module.exports = app;
```

#### 4.2 改造后

```javascript
// ... 路由和中间件 ...

// ✅ 只在直接运行时启动服务器
if (require.main === module) {
    app.listen(PORT, () => {
        console.log(`Server is running on http://localhost:${PORT}`);
    });
}

module.exports = app;
```

**`require.main === module` 是什么？** 这是 Node.js 判断"当前文件是不是被直接运行"的标准方法：
- `node server.js` 运行 → `require.main === module` 为 `true` → 启动服务器。
- `require('./server')` 导入 → `require.main === module` 为 `false` → 不启动服务器。

**改造 `server.js`**：打开 `server.js`，找到 `app.listen(...)` 这一行，包裹到 `if (require.main === module)` 中。

**完整改造后的 `server.js` 末尾**：

```javascript
const PORT = process.env.PORT || 3000;

// 只在直接运行时启动服务器（测试时不启动）
if (require.main === module) {
    app.listen(PORT, () => {
        console.log(`Server is running on http://localhost:${PORT}`);
    });
}

module.exports = app;
```

**验证改造**：

```bash
# 1. 直接运行——应该启动服务器
node server.js
# → 输出 "Server is running on http://localhost:3000"
# Ctrl+C 停止

# 2. 在 Node.js 中 require——应该不启动服务器
node -e "const app = require('./server'); console.log('app 导入成功，服务器未启动');"
# → 输出 "app 导入成功，服务器未启动"
```

> 🔥 **魔鬼细节**：`require.main === module` 只在 CommonJS 中有效。如果你的项目是 ES Modules（`"type": "module"`），需要用 `import.meta.url` 判断。本教程的 `blog-backend` 使用 CommonJS，所以直接用 `require.main === module`。

**比喻**：`require.main === module` 就像"直接叫名字 vs 被点名"——你直接叫服务员的名字，他会过来服务你（启动服务器）。别人点名提到你，你只需要应一声（导出 app），不需要站起来。

---

### 步骤 5：创建测试数据库——`tests/setup.js`

测试需要一个独立的数据库。我们创建 `tests/setup.js`，它负责：
- 测试开始前：创建独立 SQLite 数据库（`tests/test.db`），建表。
- 每个测试前：清空数据，插入测试用的基础数据。
- 测试结束后：关闭数据库连接，删除测试数据库文件。

#### 5.1 创建 `tests/` 目录

```bash
mkdir tests
```

#### 5.2 创建 `tests/setup.js`

```javascript
// tests/setup.js — 测试数据库环境
const Database = require('better-sqlite3');
const path = require('path');
const fs = require('fs');

// 测试数据库文件路径（独立于开发数据库）
const TEST_DB_PATH = path.join(__dirname, 'test.db');

let db;

// ========== beforeAll：所有测试开始前执行一次 ==========
beforeAll(() => {
    // 如果上次测试残留了 test.db，先删除
    if (fs.existsSync(TEST_DB_PATH)) {
        fs.unlinkSync(TEST_DB_PATH);
    }

    // 创建新的测试数据库连接
    db = new Database(TEST_DB_PATH);

    // 开启外键约束
    db.pragma('foreign_keys = ON');

    // 建表（和 database/schema.js 一致）
    db.exec(`
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            author_id INTEGER NOT NULL,
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            updated_at TEXT NOT NULL DEFAULT (datetime('now')),
            FOREIGN KEY (author_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL,
            article_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            FOREIGN KEY (article_id) REFERENCES articles(id),
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
    `);

    console.log('✅ 测试数据库已创建');
});

// ========== beforeEach：每个测试用例前执行 ==========
beforeEach(() => {
    // 清空所有数据（按外键依赖顺序删除）
    db.exec('DELETE FROM comments');
    db.exec('DELETE FROM articles');
    db.exec('DELETE FROM users');

    // 插入测试用的基础数据
    const now = new Date().toISOString();

    // 插入两个测试用户
    db.prepare('INSERT INTO users (id, username, email, password_hash, created_at) VALUES (?, ?, ?, ?, ?)')
        .run(1, 'alice', 'alice@example.com', '$2a$10$test_hash_for_alice', now);
    db.prepare('INSERT INTO users (id, username, email, password_hash, created_at) VALUES (?, ?, ?, ?, ?)')
        .run(2, 'bob', 'bob@example.com', '$2a$10$test_hash_for_bob', now);

    // 插入两篇测试文章（分别属于 alice 和 bob）
    db.prepare('INSERT INTO articles (id, title, content, author_id, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)')
        .run(1, 'Alice 的第一篇文章', '这是 Alice 的内容', 1, now, now);
    db.prepare('INSERT INTO articles (id, title, content, author_id, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)')
        .run(2, 'Bob 的第一篇文章', '这是 Bob 的内容', 2, now, now);

    console.log('✅ 测试数据已重置');
});

// ========== afterAll：所有测试结束后执行一次 ==========
afterAll(() => {
    if (db) {
        db.close();
    }
    // 删除测试数据库文件
    if (fs.existsSync(TEST_DB_PATH)) {
        fs.unlinkSync(TEST_DB_PATH);
    }
    console.log('✅ 测试数据库已清理');
});

// 导出 db 供测试文件使用
module.exports = { getDb: () => db };
```

**逐行解释**：

- `beforeAll`：所有测试开始前执行**一次**。这里创建数据库连接、建表。此术语需进附录。
- `beforeEach`：**每个**测试用例前执行一次。这里清空所有数据并重新插入测试数据——确保每个测试都从一个干净的、已知的状态开始。此术语需进附录。
- `afterAll`：所有测试结束后执行**一次**。关闭数据库连接、删除测试数据库文件。此术语需进附录。
- `DELETE FROM comments` → `DELETE FROM articles` → `DELETE FROM users`：按外键依赖的倒序删除——先删子表（comments），再删父表（articles、users），否则外键约束会阻止删除。
- `getDb` 函数：导出数据库连接，供测试文件使用。用函数而不是直接导出 `db`，是因为 `db` 在 `beforeAll` 中才创建——如果直接导出，`require` 时 `db` 还是 `undefined`。

> 🔥 **魔鬼细节**：`beforeAll` 和 `beforeEach` 的区别是关键——`beforeAll` 在整个测试文件的生命周期中只执行一次，`beforeEach` 在每个 `it()` 测试用例前都执行一次。如果你把建表放在 `beforeEach` 中，每个测试都要重建表，慢且没必要。如果你把清空数据放在 `beforeAll` 中，测试用例之间会互相影响（测试 A 创建的数据可能影响测试 B 的结果）。

**比喻**：`beforeAll` = 考试前布置考场（摆桌子、开灯）。`beforeEach` = 每场考试前发空白试卷。`afterAll` = 所有考试结束后收拾考场（关灯、锁门）。你不会每场考试都重新布置考场，但你需要每场考试都发新试卷。

---

### 步骤 6：创建 `jest.config.js`

在项目根目录（`blog-backend/`）下创建 `jest.config.js`：

```javascript
// jest.config.js — Jest 配置文件
module.exports = {
    testEnvironment: 'node',         // 测试环境：Node.js
    testMatch: [
        '**/tests/**/*.test.js'      // 测试文件匹配模式
    ],
    verbose: true,                    // 显示每个测试的详细信息
};
```

**参数解释**：
- `testEnvironment: 'node'`：告诉 Jest 在 Node.js 环境中运行测试（不是浏览器 jsdom 环境）。
- `testMatch`：告诉 Jest 去哪里找测试文件。`**/tests/**/*.test.js` 匹配 `tests/` 目录下所有 `.test.js` 文件。
- `verbose: true`：显示每个测试用例的名称和结果（PASSED / FAILED）。

> 🔥 **魔鬼细节**：Jest 默认不支持 ES Modules（`import`/`export`）。本教程使用 CommonJS（`require`/`module.exports`），所以不需要额外配置。如果你的项目用了 `"type": "module"`，需要配置 `transform` 或使用 `babel-jest`。这不是本教程的范围。

---

### 步骤 7：测试用户认证——`tests/auth.test.js`

现在写第一个测试文件。新建 `tests/auth.test.js`：

```javascript
// tests/auth.test.js — 用户认证接口测试
const request = require('supertest');
const app = require('../server');
const { getDb } = require('./setup');
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');

// JWT 密钥（和 server.js 中保持一致）
const JWT_SECRET = process.env.JWT_SECRET || 'your_jwt_secret_here';

describe('用户认证接口', () => {
    describe('POST /api/auth/register — 注册', () => {
        it('注册新用户应返回 201', async () => {
            const res = await request(app)
                .post('/api/auth/register')
                .send({ username: 'newuser', email: 'newuser@example.com', password: 'password123' });

            expect(res.status).toBe(201);
            expect(res.body.success).toBe(true);
            expect(res.body.data).toHaveProperty('id');
            expect(res.body.data.username).toBe('newuser');
        });

        it('注册重复用户名应返回 409', async () => {
            // 先注册一个用户
            await request(app)
                .post('/api/auth/register')
                .send({ username: 'alice', email: 'alice@example.com', password: 'password123' });

            // 再次注册同名用户——应失败
            const res = await request(app)
                .post('/api/auth/register')
                .send({ username: 'alice', email: 'alice@example.com', password: 'password123' });

            expect(res.status).toBe(409);
            expect(res.body.success).toBe(false);
        });

        it('注册缺少密码应返回 400', async () => {
            const res = await request(app)
                .post('/api/auth/register')
                .send({ username: 'nopassword' });

            expect(res.status).toBe(400);
            expect(res.body.success).toBe(false);
        });
    });

    describe('POST /api/auth/login — 登录', () => {
        // 在测试登录前，先注册一个已知密码的测试用户
        beforeEach(async () => {
            const db = getDb();
            const hashedPassword = bcrypt.hashSync('testpassword', 10);
            db.prepare('INSERT OR REPLACE INTO users (id, username, email, password_hash, created_at) VALUES (?, ?, ?, ?, ?)')
                .run(99, 'testuser', 'testuser@example.com', hashedPassword, new Date().toISOString());
        });

        it('登录成功应返回 token', async () => {
            const res = await request(app)
                .post('/api/auth/login')
                .send({ email: 'testuser@example.com', password: 'testpassword' });

            expect(res.status).toBe(200);
            expect(res.body.success).toBe(true);
            expect(res.body.data).toHaveProperty('token');
            expect(res.body.data.token).toBeTruthy();

            // 验证 token 是否有效
            const decoded = jwt.verify(res.body.data.token, JWT_SECRET);
            expect(decoded.username).toBe('testuser');
        });

        it('密码错误应返回 401', async () => {
            const res = await request(app)
                .post('/api/auth/login')
                .send({ email: 'testuser@example.com', password: 'wrongpassword' });

            expect(res.status).toBe(401);
            expect(res.body.success).toBe(false);
        });

        it('登录不存在的用户应返回 401', async () => {
            const res = await request(app)
                .post('/api/auth/login')
                .send({ email: 'nonexistent@example.com', password: 'password123' });

            expect(res.status).toBe(401);
            expect(res.body.success).toBe(false);
        });
    });
});
```

**逐行解释**：

- `const { getDb } = require('./setup')`：导入 `setup.js` 的 `getDb` 函数。因为 `setup.js` 在顶层执行了 `beforeAll`/`beforeEach`/`afterAll`，Jest 会自动收集这些钩子。
- `describe('用户认证接口', ...)`：顶层测试组，包含所有认证相关测试。
- 嵌套 `describe('POST /api/auth/register', ...)`：按接口分组。
- `it('注册新用户应返回 201', async () => { ... })`：单个测试用例。`async` 是因为 `supertest` 的调用返回 Promise。
- `await request(app).post('/api/auth/register').send({ ... })`：发送 POST 请求。
- `expect(res.status).toBe(201)`：断言状态码。
- `expect(res.body.data).toHaveProperty('id')`：断言响应体中有 `id` 字段。
- 登录测试中的 `beforeEach`：因为 `setup.js` 的 `beforeEach` 会清空所有数据，所以需要在每个登录测试前重新插入一个有已知密码的测试用户。`bcrypt.hashSync` 直接用 `bcrypt` 库计算哈希（和 `routes/auth.js` 中的注册逻辑一致）。

> 🔥 **魔鬼细节**：登录测试需要一个"已知密码的用户"——`setup.js` 中插入的 `alice` 和 `bob` 的密码是假哈希，无法用来登录。所以要单独用 `bcrypt.hashSync` 创建真实哈希。`INSERT OR REPLACE` 确保即使 `testuser` 已存在也能正确插入。

---

### 步骤 8：测试文章 CRUD——`tests/articles.test.js`（上）

新建 `tests/articles.test.js`。先写获取文章和创建文章的部分：

```javascript
// tests/articles.test.js — 文章 CRUD 接口测试
const request = require('supertest');
const app = require('../server');
const { getDb } = require('./setup');
const bcrypt = require('bcryptjs');

// JWT 密钥（和 server.js 中保持一致）
const JWT_SECRET = process.env.JWT_SECRET || 'your_jwt_secret_here';

// 辅助函数：生成有效的 JWT token
function generateToken(userId, username) {
    const jwt = require('jsonwebtoken');
    return jwt.sign({ userId: userId, username: username }, JWT_SECRET, { expiresIn: '1h' });
}

describe('文章 CRUD 接口', () => {
    // ========== 获取文章 ==========
    describe('GET /api/articles — 获取文章列表', () => {
        it('获取所有文章应返回 200 和文章列表', async () => {
            const res = await request(app)
                .get('/api/articles');

            expect(res.status).toBe(200);
            expect(res.body.success).toBe(true);
            expect(res.body.data).toHaveProperty('articles');
            expect(res.body.data).toHaveProperty('total');
            expect(Array.isArray(res.body.data.articles)).toBe(true);
            expect(res.body.data.total).toBeGreaterThanOrEqual(2);
        });
    });

    describe('GET /api/articles/:id — 获取单篇文章', () => {
        it('获取存在的文章应返回 200', async () => {
            const res = await request(app)
                .get('/api/articles/1');

            expect(res.status).toBe(200);
            expect(res.body.success).toBe(true);
            expect(res.body.data).toHaveProperty('title');
            expect(res.body.data.id).toBe(1);
        });

        it('获取不存在的文章应返回 404', async () => {
            const res = await request(app)
                .get('/api/articles/999');

            expect(res.status).toBe(404);
            expect(res.body.success).toBe(false);
        });
    });

    // ========== 创建文章 ==========
    describe('POST /api/articles — 创建文章', () => {
        let token;

        // 每个测试前生成 alice 的 token
        beforeEach(() => {
            token = generateToken(1, 'alice');
        });

        it('创建文章成功应返回 201', async () => {
            const res = await request(app)
                .post('/api/articles')
                .set('Authorization', `Bearer ${token}`)
                .send({ title: '新文章标题', content: '新文章内容' });

            expect(res.status).toBe(201);
            expect(res.body.success).toBe(true);
            expect(res.body.data).toHaveProperty('id');
            expect(res.body.data.title).toBe('新文章标题');
            expect(res.body.data.content).toBe('新文章内容');
            expect(res.body.data.author).toBe('alice');
        });

        it('创建文章缺少标题应返回 400', async () => {
            const res = await request(app)
                .post('/api/articles')
                .set('Authorization', `Bearer ${token}`)
                .send({ content: '只有内容没有标题' });

            expect(res.status).toBe(400);
            expect(res.body.success).toBe(false);
        });

        it('创建文章缺少内容应返回 400', async () => {
            const res = await request(app)
                .post('/api/articles')
                .set('Authorization', `Bearer ${token}`)
                .send({ title: '只有标题没有内容' });

            expect(res.status).toBe(400);
            expect(res.body.success).toBe(false);
        });
    });
});
```

**关键点**：
- `generateToken` 辅助函数：用 `jsonwebtoken` 生成有效 token，模拟登录后的状态。避免了每次测试都要先注册再登录的繁琐。
- `.set('Authorization', `Bearer ${token}`)`：设置认证头。注意格式是 `Bearer ` + 空格 + token。
- 每个测试用例**独立**——`beforeEach` 重置 token，`setup.js` 的 `beforeEach` 重置数据库，确保测试之间互不干扰。

---

### 步骤 9：测试文章 CRUD——`tests/articles.test.js`（中）

继续在 `tests/articles.test.js` 中添加更新和删除的测试：

```javascript
    // ========== 更新文章 ==========
    describe('PUT /api/articles/:id — 更新文章', () => {
        let token;

        beforeEach(() => {
            token = generateToken(1, 'alice');
        });

        it('更新自己的文章应返回 200', async () => {
            const res = await request(app)
                .put('/api/articles/1')
                .set('Authorization', `Bearer ${token}`)
                .send({ title: '修改后的标题', content: '修改后的内容' });

            expect(res.status).toBe(200);
            expect(res.body.success).toBe(true);
            expect(res.body.data.title).toBe('修改后的标题');
            expect(res.body.data.content).toBe('修改后的内容');
        });

        it('更新不存在的文章应返回 404', async () => {
            const res = await request(app)
                .put('/api/articles/999')
                .set('Authorization', `Bearer ${token}`)
                .send({ title: '修改', content: '修改' });

            expect(res.status).toBe(404);
            expect(res.body.success).toBe(false);
        });

        it('更新缺少标题应返回 400', async () => {
            const res = await request(app)
                .put('/api/articles/1')
                .set('Authorization', `Bearer ${token}`)
                .send({ content: '只有内容' });

            expect(res.status).toBe(400);
            expect(res.body.success).toBe(false);
        });
    });

    // ========== 删除文章 ==========
    describe('DELETE /api/articles/:id — 删除文章', () => {
        let token;

        beforeEach(() => {
            token = generateToken(1, 'alice');
        });

        it('删除自己的文章应返回 204', async () => {
            const res = await request(app)
                .delete('/api/articles/1')
                .set('Authorization', `Bearer ${token}`);

            expect(res.status).toBe(204);
        });

        it('删除不存在的文章应返回 404', async () => {
            const res = await request(app)
                .delete('/api/articles/999')
                .set('Authorization', `Bearer ${token}`);

            expect(res.status).toBe(404);
            expect(res.body.success).toBe(false);
        });
    });
```

---

### 步骤 10：测试认证中间件和文章归属——`tests/articles.test.js`（下）

继续在 `tests/articles.test.js` 中添加认证中间件和权限检查的测试：

```javascript
    // ========== 认证中间件测试 ==========
    describe('认证中间件 — 未登录无法操作', () => {
        it('不带 token 创建文章应返回 401', async () => {
            const res = await request(app)
                .post('/api/articles')
                .send({ title: '无 token 创建', content: '这条请求没有 token' });

            expect(res.status).toBe(401);
            expect(res.body.success).toBe(false);
        });

        it('带无效 token 创建文章应返回 401', async () => {
            const res = await request(app)
                .post('/api/articles')
                .set('Authorization', 'Bearer invalid_token_here')
                .send({ title: '无效 token', content: '这个 token 是假的' });

            expect(res.status).toBe(401);
            expect(res.body.success).toBe(false);
        });

        it('不带 token 更新文章应返回 401', async () => {
            const res = await request(app)
                .put('/api/articles/1')
                .send({ title: '无 token 更新', content: '没有 token' });

            expect(res.status).toBe(401);
            expect(res.body.success).toBe(false);
        });

        it('不带 token 删除文章应返回 401', async () => {
            const res = await request(app)
                .delete('/api/articles/1');

            expect(res.status).toBe(401);
            expect(res.body.success).toBe(false);
        });
    });

    // ========== 文章归属（权限）测试 ==========
    describe('文章归属 — 只能操作自己的文章', () => {
        it('用户 A 不能修改用户 B 的文章（403）', async () => {
            // bob 的 token
            const bobToken = generateToken(2, 'bob');

            // bob 尝试修改 alice 的文章（id=1）
            const res = await request(app)
                .put('/api/articles/1')
                .set('Authorization', `Bearer ${bobToken}`)
                .send({ title: 'Bob 想改 Alice 的文章', content: '这应该被拒绝' });

            expect(res.status).toBe(403);
            expect(res.body.success).toBe(false);
        });

        it('用户 A 不能删除用户 B 的文章（403）', async () => {
            // bob 的 token
            const bobToken = generateToken(2, 'bob');

            // bob 尝试删除 alice 的文章（id=1）
            const res = await request(app)
                .delete('/api/articles/1')
                .set('Authorization', `Bearer ${bobToken}`);

            expect(res.status).toBe(403);
            expect(res.body.success).toBe(false);
        });
    });
});
```

**关键点**：
- `generateToken(2, 'bob')`：生成 bob 的 token，模拟"另一个用户"。
- 用 bob 的 token 操作 alice 的文章（id=1）——预期返回 403。
- 认证中间件测试：不带 token 或带无效 token——预期返回 401。

> 🔥 **魔鬼细节**：测试中生成 token 需要知道 `JWT_SECRET`。必须和 `server.js` 中使用的是同一个密钥。如果密钥不一致，测试中生成的 token 会被中间件判定为无效，导致测试失败。本教程中 `JWT_SECRET` 默认值为 `'your_jwt_secret_here'`，测试文件中保持一致。

---

### 步骤 11：配置 `npm test` 脚本

打开 `package.json`，在 `"scripts"` 中添加 `"test"` 命令：

```json
{
    "scripts": {
        "start": "node server.js",
        "dev": "node --watch server.js",
        "test": "jest --runInBand"
    }
}
```

**`--runInBand` 是什么？** 此术语需进附录。默认情况下，Jest 会并行运行多个测试文件以加速。但我们的测试文件共享同一个测试数据库（`test.db`），并行运行会导致数据竞争（文件 A 在清空数据时，文件 B 正在读数据）。`--runInBand` 强制 Jest 串行运行所有测试文件——一个跑完再跑下一个。

**比喻**：`--runInBand` 就像"单行道"——一次只让一辆车通过。并行是"多车道"——速度快，但车多了容易撞（数据竞争）。因为我们只有一个测试数据库，必须用单行道。

> 🔥 **魔鬼细节**：如果你用 `:memory:` 内存数据库，每个测试文件会创建各自独立的数据库连接——内存数据库是连接级别的，不同连接看到的是不同的数据。这种情况下可以不用 `--runInBand`。但本教程用文件数据库（`test.db`），更直观——你可以用 SQLite 工具打开查看测试数据。

---

### 步骤 12：运行测试——看到绿色 ✓

所有代码写完了。运行测试：

```bash
npm test
```

**预期输出**：

```
 PASS  tests/auth.test.js
  用户认证接口
    POST /api/auth/register — 注册
      √ 注册新用户应返回 201 (xx ms)
      √ 注册重复用户名应返回 409 (xx ms)
      √ 注册缺少密码应返回 400 (xx ms)
    POST /api/auth/login — 登录
      √ 登录成功应返回 token (xx ms)
      √ 密码错误应返回 401 (xx ms)
      √ 登录不存在的用户应返回 401 (xx ms)

 PASS  tests/articles.test.js
  文章 CRUD 接口
    GET /api/articles — 获取文章列表
      √ 获取所有文章应返回 200 和文章列表 (xx ms)
    GET /api/articles/:id — 获取单篇文章
      √ 获取存在的文章应返回 200 (xx ms)
      √ 获取不存在的文章应返回 404 (xx ms)
    POST /api/articles — 创建文章
      √ 创建文章成功应返回 201 (xx ms)
      √ 创建文章缺少标题应返回 400 (xx ms)
      √ 创建文章缺少内容应返回 400 (xx ms)
    PUT /api/articles/:id — 更新文章
      √ 更新自己的文章应返回 200 (xx ms)
      √ 更新不存在的文章应返回 404 (xx ms)
      √ 更新缺少标题应返回 400 (xx ms)
    DELETE /api/articles/:id — 删除文章
      √ 删除自己的文章应返回 204 (xx ms)
      √ 删除不存在的文章应返回 404 (xx ms)
    认证中间件 — 未登录无法操作
      √ 不带 token 创建文章应返回 401 (xx ms)
      √ 带无效 token 创建文章应返回 401 (xx ms)
      √ 不带 token 更新文章应返回 401 (xx ms)
      √ 不带 token 删除文章应返回 401 (xx ms)
    文章归属 — 只能操作自己的文章
      √ 用户 A 不能修改用户 B 的文章（403） (xx ms)
      √ 用户 A 不能删除用户 B 的文章（403） (xx ms)

Test Suites: 2 passed, 2 total
Tests:       18 passed, 18 total
Snapshots:   0 total
Time:        x.xxx s
Ran all test suites.
```

**你看到了什么？** 18 个测试全部通过，一片绿色 ✓。从今天起，你改代码不再靠猜，而是靠测试告诉你——改坏了没有。

---

### 🤔 想多一点：测试失败时怎么办？

假设你不小心改坏了代码——比如把 `routes/articles.js` 中的 `if (!title || !content)` 验证删掉了。运行 `npm test`：

```
 FAIL  tests/articles.test.js
  文章 CRUD 接口
    POST /api/articles — 创建文章
      √ 创建文章成功应返回 201
      × 创建文章缺少标题应返回 400 (xx ms)
      √ 创建文章缺少内容应返回 400

  ● 文章 CRUD 接口 › POST /api/articles — 创建文章 › 创建文章缺少标题应返回 400

    expect(received).toBe(expected) // Object.is equality

    Expected: 400
    Received: 201

      56 |                 .send({ content: '只有内容没有标题' });
      57 |
    > 58 |             expect(res.status).toBe(400);
         |                                ^
      59 |             expect(res.body.success).toBe(false);
      60 |         });
```

**解读**：
- `Expected: 400`（你期望的）
- `Received: 201`（实际返回的）
- 箭头指向失败的那一行（`expect(res.status).toBe(400)`）

**排查思路**：
1. 看哪个测试失败了：`创建文章缺少标题应返回 400`
2. 看实际返回了什么：201（创建成功）——说明必填字段验证被绕过了
3. 去 `routes/articles.js` 检查 `if (!title || !content)` 是否还在

**这就是测试的价值**——它在你上线之前就发现了 bug。

---

## 四、完整代码清单

### `blog-backend/server.js`（改造后的末尾）

```javascript
// ... 前面的路由和中间件代码不变 ...

const PORT = process.env.PORT || 3000;

// 只在直接运行时启动服务器（测试时不启动）
if (require.main === module) {
    app.listen(PORT, () => {
        console.log(`Server is running on http://localhost:${PORT}`);
    });
}

module.exports = app;
```

### `blog-backend/jest.config.js`（本章新建）

```javascript
// jest.config.js — Jest 配置文件
module.exports = {
    testEnvironment: 'node',
    testMatch: [
        '**/tests/**/*.test.js'
    ],
    verbose: true,
};
```

### `blog-backend/tests/setup.js`（本章新建）

```javascript
// tests/setup.js — 测试数据库环境
const Database = require('better-sqlite3');
const path = require('path');
const fs = require('fs');

const TEST_DB_PATH = path.join(__dirname, 'test.db');

let db;

beforeAll(() => {
    if (fs.existsSync(TEST_DB_PATH)) {
        fs.unlinkSync(TEST_DB_PATH);
    }

    db = new Database(TEST_DB_PATH);
    db.pragma('foreign_keys = ON');

    db.exec(`
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            author_id INTEGER NOT NULL,
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            updated_at TEXT NOT NULL DEFAULT (datetime('now')),
            FOREIGN KEY (author_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL,
            article_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            FOREIGN KEY (article_id) REFERENCES articles(id),
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
    `);

    console.log('✅ 测试数据库已创建');
});

beforeEach(() => {
    db.exec('DELETE FROM comments');
    db.exec('DELETE FROM articles');
    db.exec('DELETE FROM users');

    const now = new Date().toISOString();

    db.prepare('INSERT INTO users (id, username, email, password_hash, created_at) VALUES (?, ?, ?, ?, ?)')
        .run(1, 'alice', 'alice@example.com', '$2a$10$test_hash_for_alice', now);
    db.prepare('INSERT INTO users (id, username, email, password_hash, created_at) VALUES (?, ?, ?, ?, ?)')
        .run(2, 'bob', 'bob@example.com', '$2a$10$test_hash_for_bob', now);

    db.prepare('INSERT INTO articles (id, title, content, author_id, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)')
        .run(1, 'Alice 的第一篇文章', '这是 Alice 的内容', 1, now, now);
    db.prepare('INSERT INTO articles (id, title, content, author_id, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)')
        .run(2, 'Bob 的第一篇文章', '这是 Bob 的内容', 2, now, now);

    console.log('✅ 测试数据已重置');
});

afterAll(() => {
    if (db) {
        db.close();
    }
    if (fs.existsSync(TEST_DB_PATH)) {
        fs.unlinkSync(TEST_DB_PATH);
    }
    console.log('✅ 测试数据库已清理');
});

module.exports = { getDb: () => db };
```

### `blog-backend/tests/auth.test.js`（本章新建）

```javascript
// tests/auth.test.js — 用户认证接口测试
const request = require('supertest');
const app = require('../server');
const { getDb } = require('./setup');
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');

const JWT_SECRET = process.env.JWT_SECRET || 'your_jwt_secret_here';

describe('用户认证接口', () => {
    describe('POST /api/auth/register — 注册', () => {
        it('注册新用户应返回 201', async () => {
            const res = await request(app)
                .post('/api/auth/register')
                .send({ username: 'newuser', email: 'newuser@example.com', password: 'password123' });

            expect(res.status).toBe(201);
            expect(res.body.success).toBe(true);
            expect(res.body.data).toHaveProperty('id');
            expect(res.body.data.username).toBe('newuser');
        });

        it('注册重复用户名应返回 409', async () => {
            await request(app)
                .post('/api/auth/register')
                .send({ username: 'alice', email: 'alice@example.com', password: 'password123' });

            const res = await request(app)
                .post('/api/auth/register')
                .send({ username: 'alice', email: 'alice@example.com', password: 'password123' });

            expect(res.status).toBe(409);
            expect(res.body.success).toBe(false);
        });

        it('注册缺少密码应返回 400', async () => {
            const res = await request(app)
                .post('/api/auth/register')
                .send({ username: 'nopassword' });

            expect(res.status).toBe(400);
            expect(res.body.success).toBe(false);
        });
    });

    describe('POST /api/auth/login — 登录', () => {
        beforeEach(async () => {
            const db = getDb();
            const hashedPassword = bcrypt.hashSync('testpassword', 10);
            db.prepare('INSERT OR REPLACE INTO users (id, username, email, password_hash, created_at) VALUES (?, ?, ?, ?, ?)')
                .run(99, 'testuser', 'testuser@example.com', hashedPassword, new Date().toISOString());
        });

        it('登录成功应返回 token', async () => {
            const res = await request(app)
                .post('/api/auth/login')
                .send({ email: 'testuser@example.com', password: 'testpassword' });

            expect(res.status).toBe(200);
            expect(res.body.success).toBe(true);
            expect(res.body.data).toHaveProperty('token');
            expect(res.body.data.token).toBeTruthy();

            const decoded = jwt.verify(res.body.data.token, JWT_SECRET);
            expect(decoded.username).toBe('testuser');
        });

        it('密码错误应返回 401', async () => {
            const res = await request(app)
                .post('/api/auth/login')
                .send({ email: 'testuser@example.com', password: 'wrongpassword' });

            expect(res.status).toBe(401);
            expect(res.body.success).toBe(false);
        });

        it('登录不存在的用户应返回 401', async () => {
            const res = await request(app)
                .post('/api/auth/login')
                .send({ email: 'nonexistent@example.com', password: 'password123' });

            expect(res.status).toBe(401);
            expect(res.body.success).toBe(false);
        });
    });
});
```

### `blog-backend/tests/articles.test.js`（本章新建）

```javascript
// tests/articles.test.js — 文章 CRUD 接口测试
const request = require('supertest');
const app = require('../server');
const { getDb } = require('./setup');

const JWT_SECRET = process.env.JWT_SECRET || 'your_jwt_secret_here';

function generateToken(userId, username) {
    const jwt = require('jsonwebtoken');
    return jwt.sign({ userId: userId, username: username }, JWT_SECRET, { expiresIn: '1h' });
}

describe('文章 CRUD 接口', () => {
    // ========== 获取文章 ==========
    describe('GET /api/articles — 获取文章列表', () => {
        it('获取所有文章应返回 200 和文章列表', async () => {
            const res = await request(app)
                .get('/api/articles');

            expect(res.status).toBe(200);
            expect(res.body.success).toBe(true);
            expect(res.body.data).toHaveProperty('articles');
            expect(res.body.data).toHaveProperty('total');
            expect(Array.isArray(res.body.data.articles)).toBe(true);
            expect(res.body.data.total).toBeGreaterThanOrEqual(2);
        });
    });

    describe('GET /api/articles/:id — 获取单篇文章', () => {
        it('获取存在的文章应返回 200', async () => {
            const res = await request(app)
                .get('/api/articles/1');

            expect(res.status).toBe(200);
            expect(res.body.success).toBe(true);
            expect(res.body.data).toHaveProperty('title');
            expect(res.body.data.id).toBe(1);
        });

        it('获取不存在的文章应返回 404', async () => {
            const res = await request(app)
                .get('/api/articles/999');

            expect(res.status).toBe(404);
            expect(res.body.success).toBe(false);
        });
    });

    // ========== 创建文章 ==========
    describe('POST /api/articles — 创建文章', () => {
        let token;

        beforeEach(() => {
            token = generateToken(1, 'alice');
        });

        it('创建文章成功应返回 201', async () => {
            const res = await request(app)
                .post('/api/articles')
                .set('Authorization', `Bearer ${token}`)
                .send({ title: '新文章标题', content: '新文章内容' });

            expect(res.status).toBe(201);
            expect(res.body.success).toBe(true);
            expect(res.body.data).toHaveProperty('id');
            expect(res.body.data.title).toBe('新文章标题');
            expect(res.body.data.content).toBe('新文章内容');
            expect(res.body.data.author).toBe('alice');
        });

        it('创建文章缺少标题应返回 400', async () => {
            const res = await request(app)
                .post('/api/articles')
                .set('Authorization', `Bearer ${token}`)
                .send({ content: '只有内容没有标题' });

            expect(res.status).toBe(400);
            expect(res.body.success).toBe(false);
        });

        it('创建文章缺少内容应返回 400', async () => {
            const res = await request(app)
                .post('/api/articles')
                .set('Authorization', `Bearer ${token}`)
                .send({ title: '只有标题没有内容' });

            expect(res.status).toBe(400);
            expect(res.body.success).toBe(false);
        });
    });

    // ========== 更新文章 ==========
    describe('PUT /api/articles/:id — 更新文章', () => {
        let token;

        beforeEach(() => {
            token = generateToken(1, 'alice');
        });

        it('更新自己的文章应返回 200', async () => {
            const res = await request(app)
                .put('/api/articles/1')
                .set('Authorization', `Bearer ${token}`)
                .send({ title: '修改后的标题', content: '修改后的内容' });

            expect(res.status).toBe(200);
            expect(res.body.success).toBe(true);
            expect(res.body.data.title).toBe('修改后的标题');
            expect(res.body.data.content).toBe('修改后的内容');
        });

        it('更新不存在的文章应返回 404', async () => {
            const res = await request(app)
                .put('/api/articles/999')
                .set('Authorization', `Bearer ${token}`)
                .send({ title: '修改', content: '修改' });

            expect(res.status).toBe(404);
            expect(res.body.success).toBe(false);
        });

        it('更新缺少标题应返回 400', async () => {
            const res = await request(app)
                .put('/api/articles/1')
                .set('Authorization', `Bearer ${token}`)
                .send({ content: '只有内容' });

            expect(res.status).toBe(400);
            expect(res.body.success).toBe(false);
        });
    });

    // ========== 删除文章 ==========
    describe('DELETE /api/articles/:id — 删除文章', () => {
        let token;

        beforeEach(() => {
            token = generateToken(1, 'alice');
        });

        it('删除自己的文章应返回 204', async () => {
            const res = await request(app)
                .delete('/api/articles/1')
                .set('Authorization', `Bearer ${token}`);

            expect(res.status).toBe(204);
        });

        it('删除不存在的文章应返回 404', async () => {
            const res = await request(app)
                .delete('/api/articles/999')
                .set('Authorization', `Bearer ${token}`);

            expect(res.status).toBe(404);
            expect(res.body.success).toBe(false);
        });
    });

    // ========== 认证中间件测试 ==========
    describe('认证中间件 — 未登录无法操作', () => {
        it('不带 token 创建文章应返回 401', async () => {
            const res = await request(app)
                .post('/api/articles')
                .send({ title: '无 token 创建', content: '这条请求没有 token' });

            expect(res.status).toBe(401);
            expect(res.body.success).toBe(false);
        });

        it('带无效 token 创建文章应返回 401', async () => {
            const res = await request(app)
                .post('/api/articles')
                .set('Authorization', 'Bearer invalid_token_here')
                .send({ title: '无效 token', content: '这个 token 是假的' });

            expect(res.status).toBe(401);
            expect(res.body.success).toBe(false);
        });

        it('不带 token 更新文章应返回 401', async () => {
            const res = await request(app)
                .put('/api/articles/1')
                .send({ title: '无 token 更新', content: '没有 token' });

            expect(res.status).toBe(401);
            expect(res.body.success).toBe(false);
        });

        it('不带 token 删除文章应返回 401', async () => {
            const res = await request(app)
                .delete('/api/articles/1');

            expect(res.status).toBe(401);
            expect(res.body.success).toBe(false);
        });
    });

    // ========== 文章归属（权限）测试 ==========
    describe('文章归属 — 只能操作自己的文章', () => {
        it('用户 A 不能修改用户 B 的文章（403）', async () => {
            const bobToken = generateToken(2, 'bob');

            const res = await request(app)
                .put('/api/articles/1')
                .set('Authorization', `Bearer ${bobToken}`)
                .send({ title: 'Bob 想改 Alice 的文章', content: '这应该被拒绝' });

            expect(res.status).toBe(403);
            expect(res.body.success).toBe(false);
        });

        it('用户 A 不能删除用户 B 的文章（403）', async () => {
            const bobToken = generateToken(2, 'bob');

            const res = await request(app)
                .delete('/api/articles/1')
                .set('Authorization', `Bearer ${bobToken}`);

            expect(res.status).toBe(403);
            expect(res.body.success).toBe(false);
        });
    });
});
```

### `blog-backend/package.json`（scripts 部分新增）

```json
{
    "scripts": {
        "start": "node server.js",
        "dev": "node --watch server.js",
        "test": "jest --runInBand"
    }
}
```

### `blog-backend/` 目录结构（本章最终状态）

```
blog-backend/
├── server.js                  ← 本章改造：app.listen 分离
├── package.json               ← 本章新增：test 脚本 + devDependencies
├── package-lock.json
├── jest.config.js             ← 本章新建
├── .gitignore
├── blog.db                    ← 开发数据库（不受测试影响）
├── node_modules/
├── database/
│   ├── db.js
│   └── schema.js
├── routes/
│   ├── articles.js
│   ├── auth.js
│   ├── comments.js
│   └── upload.js
├── middleware/
│   ├── auth.js
│   ├── logger.js
│   └── errorHandler.js
├── utils/
│   └── AppError.js
├── tests/                     ← 本章新建
│   ├── setup.js               ← 测试数据库环境
│   ├── auth.test.js           ← 认证测试（6 个用例）
│   └── articles.test.js       ← 文章 CRUD 测试（18 个用例）
└── uploads/
```

---

## 五、验证方法

```bash
# 1. 运行全部测试
npm test
# → 2 passed, 18 total, 一片绿色 ✓

# 2. 只运行认证测试
npx jest tests/auth.test.js --verbose
# → 1 passed, 6 total

# 3. 只运行文章测试
npx jest tests/articles.test.js --verbose
# → 1 passed, 12 total... wait 应该是 18?

# 4. 验证开发服务器不受影响
npm run dev
# → Server is running on http://localhost:3000
# 用 Thunder Client 发 GET /api/articles → 返回开发数据
# 确认 blog.db 没有被测试数据污染

# 5. 验证测试数据库独立
# 运行测试后，检查 tests/test.db 存在
# 再次运行测试 → tests/test.db 被删除后重新创建
```

**全部通过？** 恭喜！你的博客系统现在有了完整的自动化测试覆盖。从今天起，`npm test` 就是你改代码后的"安全检查"。

---

## 六、小结表格

| 学到的东西 | 一句话解释 |
|-----------|-----------|
| Jest 安装 | `npm install --save-dev jest supertest`，开发依赖 |
| `describe` | 测试组——把相关测试用例包在一起 |
| `it` | 单个测试用例——"应该做什么" |
| `expect` | 断言——检查实际值是否等于期望值 |
| `supertest` | HTTP 测试库——`request(app).get('/api/xxx').expect(200)` |
| server.js 改造 | `require.main === module` 判断是否直接运行，分离 app 和 listen |
| `tests/setup.js` | 测试数据库环境：`beforeAll` 建表，`beforeEach` 重置数据，`afterAll` 清理 |
| 独立测试数据库 | 测试用 `tests/test.db`，开发用 `blog.db`，互不干扰 |
| `jest.config.js` | 配置 Jest：`testEnvironment: 'node'`，`testMatch` 匹配测试文件 |
| `generateToken` | 辅助函数：用 `jsonwebtoken` 生成有效 token，避免每次测试前登录 |
| 认证中间件测试 | 无 token → 401，无效 token → 401 |
| 文章归属测试 | 用户 A 不能修改/删除用户 B 的文章 → 403 |
| `--runInBand` | 串行运行测试，避免共享数据库的竞争 |
| 测试失败排查 | Jest 输出：哪个文件、哪一行、实际值、期望值——直接定位 |

---

## 七、术语附录

| 术语 | 英文 | 通俗解释 | 本章出现位置 | 字面陷阱 |
|------|------|----------|-------------|----------|
| Jest | — | Facebook 开源的 JavaScript 测试框架。零配置开箱即用，内置断言、mock、覆盖率等功能。Node.js 项目最常用的测试框架。 | 步骤 1-2 | 不是"玩笑"——名字来源于"Jest"（玩笑），但功能非常严肃。 |
| supertest | — | HTTP 断言库。用于向 Express/Koa 等 Node.js HTTP 服务器发模拟请求，验证响应。不需要启动 TCP 端口。 | 步骤 1、3 | 不是"超级测试"——"super"在这里是"superagent"（底层 HTTP 库）的缩写。 |
| `describe` | — | Jest 中用于定义一个测试组（suite）的函数。将相关测试用例组织在一起，可嵌套。 | 步骤 2 | 不是"描述"——它是"定义一个测试套件"，不仅仅是"描述"。 |
| `it` / `test` | — | Jest 中定义单个测试用例的函数。`it` 和 `test` 完全等价。 | 步骤 2 | 不是"它"——来自 BDD（行为驱动开发）风格："it should do something"。 |
| `expect` | — | Jest 的断言函数。`expect(实际值).toBe(期望值)` 检查两者是否相等。 | 步骤 2 | 不是"期望"——它是"我要断言这件事为真"，如果为假则测试失败。 |
| `beforeAll` | — | Jest 钩子：在所有测试用例开始前执行一次。常用于建表、创建连接等一次性操作。 | 步骤 5 | 不是"在所有之前"——是"在所有测试用例之前"，但 `describe` 外面的代码可能更早执行。 |
| `beforeEach` | — | Jest 钩子：在每个测试用例执行前执行一次。常用于重置数据、清空状态。 | 步骤 5 | 不是"在每个之前"——是"在每个测试用例之前"，不包括 `beforeAll`。 |
| `afterAll` | — | Jest 钩子：在所有测试用例结束后执行一次。常用于关闭连接、清理文件。 | 步骤 5 | 不是"在所有之后"——是"在所有测试用例之后"，但如果在 `beforeAll` 中出错，`afterAll` 可能不会执行。 |
| mock | — | 测试中的"替身"。用假的函数/模块替换真实的，避免依赖外部服务（如发邮件、调支付接口）。 | 步骤 4（概念） | 不是"嘲笑"——mock 是"模拟、仿制品"的意思。 |
| 测试数据库 | Test Database | 独立于开发数据库的数据库实例。测试前创建，测试后清理，确保测试可重复。 | 步骤 5 | 不是"测试用的数据库"——它是"与开发数据库物理隔离的独立数据库"。 |
| `--runInBand` | — | Jest 命令行参数。强制所有测试文件串行执行（一个跑完再跑下一个），避免并行测试间的数据竞争。 | 步骤 11 | 不是"在乐队中运行"——run in band 是"排队运行"的意思，一次一个。 |
| `require.main === module` | — | Node.js 判断当前文件是否被直接运行的标准方法。为 `true` 表示 `node xxx.js` 运行，为 `false` 表示被 `require` 导入。 | 步骤 4 | 不是"主模块"——"main"在这里指"入口模块"，即 Node.js 命令行直接指定的那个文件。 |

---

## 八、已知坑点与禁止事项

| 坑点 | 现象 | 原因 | 解决 |
|------|------|------|------|
| 测试时 `app.listen` 被调用 | 端口 3000 被占用，测试挂起不退出 | `require('./server')` 时 `app.listen` 被执行了 | 用 `if (require.main === module)` 包裹 `app.listen` |
| 测试和开发用同一个数据库 | 测试数据污染了 `blog.db`，或测试删除了开发数据 | 测试数据库没有隔离 | 用 `tests/test.db` 独立文件，`beforeAll` 创建，`afterAll` 删除 |
| `JWT_SECRET` 不一致 | 测试中生成的 token 被中间件拒绝，返回 401 | 测试文件中的 `JWT_SECRET` 和 `server.js` 中的不一致 | 测试文件中使用相同的默认值 `'your_jwt_secret_here'`，或从环境变量读取 |
| 并行测试导致数据竞争 | 测试随机失败，有时绿有时红 | 多个测试文件同时操作同一个 `test.db` | 用 `--runInBand` 串行运行 |
| `beforeEach` 中数据没清干净 | 测试 A 的数据影响了测试 B 的结果 | 外键约束导致删除顺序错误 | 按外键依赖倒序删除：`DELETE FROM comments` → `articles` → `users` |
| supertest 返回的 `res.body` 是空对象 | 断言 `res.body.token` 失败 | 忘记在 `server.js` 中配置 `app.use(express.json())` | 确保 `express.json()` 中间件在路由之前加载 |
| 测试登录失败——密码哈希不匹配 | `bcrypt.compareSync` 返回 `false` | `tests/setup.js` 中插入的密码是假哈希，不是真实 `bcrypt` 哈希 | 在登录测试的 `beforeEach` 中用 `bcrypt.hashSync` 生成真实哈希后插入 |
| `getDb()` 返回 `undefined` | 测试中 `getDb()` 拿到的是 `undefined` | `setup.js` 中的 `db` 在 `beforeAll` 中才创建，但 `require` 时还没执行 | 用函数 `getDb()` 而不是直接导出 `db` 变量 |
| 测试文件找不到 `server` 模块 | `Cannot find module '../server'` | 测试文件路径问题 | 确保 `tests/` 目录在 `blog-backend/` 下，`require('../server')` 能正确找到 `server.js` |

---

## 九、下一步建议

你的博客系统现在有了 18 个自动化测试用例，覆盖了核心的认证和文章 CRUD 功能。但这只是开始——你还可以扩展：

- **扩展测试**：为评论接口、分页、搜索、文件上传写测试。模式一样——`request(app).get(...)` / `.post(...)`，`expect(...)`。
- **覆盖率报告**：`npx jest --coverage` 查看哪些代码被测试覆盖了，哪些还没覆盖。
- **CI/CD 集成**：在 GitHub Actions 中配置 `npm test`，每次提交代码自动跑测试——不通过则不允许合并。
- **测试驱动开发**：下次写新功能时，试试先写测试，再写代码（红 → 绿 → 重构）。

**下一阶段（教程 27-31，部署）**，你将把博客系统部署到真实的 Linux 服务器上，让全世界都能访问。

---

> [可暂停点 6/9]：阶段七（测试）全部完成。你安装了 Jest + supertest，改造了 server.js，创建了独立测试数据库，写了 18 个测试用例，一条 `npm test` 全绿。下次从第 27 章（Linux 生存指南）继续。
>
> 📊 本教程无可视化
>
> 本教程编辑记录：2026-06-12 初始版本（第 6 批：25-26 章）。