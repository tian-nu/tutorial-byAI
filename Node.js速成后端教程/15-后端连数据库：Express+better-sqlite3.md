# 15-后端连数据库：Express+better-sqlite3

> "第 14 章的 seed 脚本是独立运行的——运行完就退出。这一章我们让数据库连接**长驻**在 Express 服务器里，像一个全天候值班的仓库保管员。创建 `database/db.js` 数据库连接模块，用单例模式确保整个应用共用一个连接；重构 `database/schema.js`，让它从 `db.js` 获取连接；最后在路由中引入数据库，把第 09 章的数组查询替换为真正的 SQL 查询。"

---

## 一、目标与完成效果

**一句话目标**：创建 `database/db.js` 数据库连接模块（单例模式），重构 `database/schema.js` 和 `server.js` 使用统一的数据库连接，在路由中引入数据库并执行 SQL 查询。

**完成后的可观测效果**：
- 你创建了 `database/db.js`，导出 `db` 对象和 `initDatabase()` 函数。
- `server.js` 不再直接 `new Database('blog.db')`，而是从 `database/db.js` 引入。
- `database/schema.js` 不再创建新连接，而是接收 `db` 参数来建表。
- 你在 `routes/articles.js` 中引入了 `db`，能执行数据库查询返回数据。
- 整个应用只创建了一个数据库连接——无论多少请求进来，都共用同一个 `db` 对象。

---

## 二、前置条件

| 序号 | 条件 | 验证命令 |
|------|------|----------|
| 1 | 已完成教程 14，`database/schema.js` 和 `database/seed.js` 存在 | `ls database/schema.js` 和 `ls database/seed.js` 文件存在 |
| 2 | 测试数据已插入 | `node database/seed.js` 能正常运行（数据可能重复，没关系） |
| 3 | 理解 `require` 的模块缓存机制 | 第 04 章：同一个模块 `require` 多次，只执行一次 |

**一条命令确认前置满足**：

```bash
node -e "const db = new (require('better-sqlite3'))('blog.db'); console.log(db.prepare('SELECT COUNT(*) AS c FROM articles').get())"
```

输出 `{ c: 5 }`（或更多，如果 seed 跑了多次），前置条件满足。

---

## 三、分步操作

### 步骤 1：为什么需要统一的数据库连接模块？

当前 `server.js` 和 `database/schema.js` 各自创建数据库连接：

```javascript
// server.js
const db = initDatabase();  // 内部 new Database('blog.db')

// 路由中需要数据库怎么办？再 new 一次？
const db = new Database('blog.db');  // ❌ 又创建了一个新连接！
```

**问题**：
1. **多次创建连接浪费资源**——每次 `new Database()` 都会打开文件、分配内存。
2. **连接不共享**——`server.js` 里的 `db` 和路由里的 `db` 不是同一个对象。
3. **重复执行 PRAGMA**——每个连接都要单独开启外键约束。

**解决方案**：单例模式（Singleton）——整个应用只创建一次数据库连接，所有模块通过 `require` 共享同一个 `db` 对象。

---

### 步骤 2：用餐厅比喻理解"单例连接"

```
❌ 多个连接（错误做法）：
  客人A来了 → 新开一个厨房 → 做好菜 → 拆掉厨房
  客人B来了 → 再新开一个厨房 → 做好菜 → 拆掉厨房
  （浪费！每次都要建厨房、拆厨房）

✅ 单例连接（正确做法）：
  餐厅开业 → 建一个厨房（initDatabase）
  客人A来了 → 用同一个厨房做菜
  客人B来了 → 用同一个厨房做菜
  餐厅打烊 → 关掉厨房
```

**Node.js 的 `require` 缓存机制天然支持单例**：当你第一次 `require('./database/db')` 时，Node.js 执行模块代码，缓存结果。后续所有 `require('./database/db')` 都返回同一个缓存对象。**这就是为什么把数据库连接放在一个独立模块里导出，就能实现单例。**

---

### 步骤 3：创建 database/db.js——数据库连接模块

创建 `database/db.js`：

```javascript
// database/db.js — 数据库连接模块（单例）
const Database = require('better-sqlite3');
const path = require('path');

// 数据库文件路径：blog-backend/blog.db
const dbPath = path.join(__dirname, '..', 'blog.db');

// 创建数据库连接（整个应用共用一个）
const db = new Database(dbPath);

// 开启外键约束
db.pragma('foreign_keys = ON');

console.log('✅ 数据库连接已建立（单例模式）');

/**
 * 初始化数据库表结构
 * 与 schema.js 解耦——schema.js 只负责建表语句
 */
function initDatabase() {
    // 建表语句移到了 schema.js 中，这里只做基础初始化
    // 但 PRAGMA 和连接创建已经在上面的代码中完成
    console.log('✅ 数据库基础初始化完成');
}

module.exports = { db, initDatabase };
```

<details>
<summary>🔄 sql.js 备选方案：database/db.js</summary>

```javascript
// database/db.js — sql.js 备选方案
const initSqlJs = require('sql.js');
const fs = require('fs');
const path = require('path');

// 单例引用
let db = null;
let SQL = null;

const dbPath = path.join(__dirname, '..', 'blog.db');

async function initDatabase() {
    SQL = await initSqlJs();

    if (fs.existsSync(dbPath)) {
        const fileBuffer = fs.readFileSync(dbPath);
        db = new SQL.Database(fileBuffer);
    } else {
        db = new SQL.Database();
    }

    db.run('PRAGMA foreign_keys = ON');
    console.log('✅ 数据库连接已建立（单例模式）');
    return { db };
}

function saveDatabase() {
    if (db) {
        const data = db.export();
        fs.writeFileSync(dbPath, Buffer.from(data));
    }
}

function getDb() {
    if (!db) {
        throw new Error('数据库未初始化！请先调用 initDatabase()');
    }
    return db;
}

module.exports = { initDatabase, getDb, saveDatabase };
```

</details>

#### 逐行解释

```javascript
const dbPath = path.join(__dirname, '..', 'blog.db');
```

用 `path.join(__dirname, '..', 'blog.db')` 而不是 `'blog.db'`。`__dirname` 是 `database/db.js` 所在的目录（`blog-backend/database/`），`..` 回退到 `blog-backend/`，所以 `blog.db` 始终在项目根目录下——**无论从哪个目录执行 `node server.js`，都不会找错位置。**

```javascript
const db = new Database(dbPath);
```

这一行在模块加载时执行（`require` 的时候）。因为 `require` 有缓存，这一行只执行一次——整个应用共用一个 `db` 对象。

```javascript
module.exports = { db, initDatabase };
```

导出 `db` 对象（路由中使用）和 `initDatabase` 函数（`server.js` 中调用）。

---

### 步骤 4：重构 database/schema.js——接收 db 参数

现在 `schema.js` 不再自己创建连接，而是接收 `db` 参数来建表：

```javascript
// database/schema.js — 数据库表结构定义（重构版）
// 不再自己创建连接，而是接收 db 参数

/**
 * 创建所有表（幂等）
 * @param {Database} db 数据库连接对象
 */
function createTables(db) {
    db.exec(`
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            created_at TEXT DEFAULT (datetime('now'))
        )
    `);

    db.exec(`
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            author_id INTEGER NOT NULL,
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (author_id) REFERENCES users(id)
        )
    `);

    db.exec(`
        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL,
            article_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (article_id) REFERENCES articles(id),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    `);

    console.log('✅ 数据库表结构已就绪（users, articles, comments）');
}

module.exports = { createTables };
```

<details>
<summary>🔄 sql.js 备选方案：database/schema.js</summary>

```javascript
// database/schema.js — sql.js 备选方案（重构版）
function createTables(db) {
    db.run(`CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        email TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        created_at TEXT DEFAULT (datetime('now'))
    )`);

    db.run(`CREATE TABLE IF NOT EXISTS articles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        author_id INTEGER NOT NULL,
        created_at TEXT DEFAULT (datetime('now')),
        updated_at TEXT DEFAULT (datetime('now')),
        FOREIGN KEY (author_id) REFERENCES users(id)
    )`);

    db.run(`CREATE TABLE IF NOT EXISTS comments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        content TEXT NOT NULL,
        article_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        created_at TEXT DEFAULT (datetime('now')),
        FOREIGN KEY (article_id) REFERENCES articles(id),
        FOREIGN KEY (user_id) REFERENCES users(id)
    )`);

    console.log('✅ 数据库表结构已就绪（users, articles, comments）');
}

module.exports = { createTables };
```

</details>

---

### 步骤 5：重构 server.js——使用统一的数据库连接

```javascript
// server.js（重构版）
const express = require('express');
const { db, initDatabase } = require('./database/db');      // ← 引入 db 模块
const { createTables } = require('./database/schema');       // ← 引入建表函数

const articlesRouter = require('./routes/articles');
const authRouter = require('./routes/auth');
const errorHandler = require('./middleware/errorHandler');

const app = express();

// 初始化数据库
initDatabase();                           // 基础初始化（实际上 db.js 加载时已完成）
createTables(db);                         // 建表
console.log('✅ 数据库初始化完成');

// 中间件
app.use(express.json());

// 路由
app.use('/api/articles', articlesRouter);
app.use('/api/auth', authRouter);

// 404 兜底
app.use((req, res) => {
    res.status(404).json({
        success: false,
        error: {
            message: `接口不存在：${req.method} ${req.originalUrl}`,
            code: 'NOT_FOUND'
        }
    });
});

// 错误处理中间件
app.use(errorHandler);

app.listen(3000, () => {
    console.log('Server is running on http://localhost:3000');
});
```

<details>
<summary>🔄 sql.js 备选方案：server.js</summary>

```javascript
// server.js — sql.js 备选方案
const express = require('express');
const { initDatabase, getDb, saveDatabase } = require('./database/db');
const { createTables } = require('./database/schema');

const articlesRouter = require('./routes/articles');
const authRouter = require('./routes/auth');
const errorHandler = require('./middleware/errorHandler');

const app = express();

// 异步初始化数据库
(async () => {
    await initDatabase();
    const db = getDb();
    createTables(db);
    saveDatabase();
    console.log('✅ 数据库初始化完成');

    // 中间件
    app.use(express.json());

    // 路由
    app.use('/api/articles', articlesRouter);
    app.use('/api/auth', authRouter);

    // 404 兜底 + 错误处理
    app.use((req, res) => {
        res.status(404).json({
            success: false,
            error: {
                message: `接口不存在：${req.method} ${req.originalUrl}`,
                code: 'NOT_FOUND'
            }
        });
    });
    app.use(errorHandler);

    app.listen(3000, () => {
        console.log('Server is running on http://localhost:3000');
    });
})();
```

</details>

---

### 步骤 6：在路由中使用数据库——GET /api/articles

打开 `routes/articles.js`，在顶部引入 `db`：

```javascript
const express = require('express');
const router = express.Router();
const { db } = require('../database/db');     // ← 引入数据库连接
const AppError = require('../utils/AppError');
```

然后把 `GET /api/articles` 从数组查询改为数据库查询：

```javascript
// GET /api/articles — 获取所有文章（数据库版）
router.get('/', (req, res) => {
    const page = parseInt(req.query.page) || 1;
    const limit = parseInt(req.query.limit) || 10;
    const offset = (page - 1) * limit;

    // 查询文章列表（带作者名）
    const selectArticles = db.prepare(`
        SELECT 
            articles.id,
            articles.title,
            articles.content,
            articles.created_at,
            articles.updated_at,
            users.username AS author
        FROM articles
        INNER JOIN users ON articles.author_id = users.id
        ORDER BY articles.created_at DESC
        LIMIT ? OFFSET ?
    `);

    const articles = selectArticles.all(limit, offset);

    // 查询总数
    const countResult = db.prepare('SELECT COUNT(*) AS total FROM articles').get();

    res.json({
        success: true,
        data: {
            page: page,
            limit: limit,
            total: countResult.total,
            articles: articles
        }
    });
});
```

<details>
<summary>🔄 sql.js 备选方案：在路由中使用数据库</summary>

```javascript
const { getDb, saveDatabase } = require('../database/db');

// GET /api/articles — 获取所有文章
router.get('/', (req, res) => {
    const db = getDb();
    const page = parseInt(req.query.page) || 1;
    const limit = parseInt(req.query.limit) || 10;
    const offset = (page - 1) * limit;

    const results = db.exec(`
        SELECT 
            articles.id,
            articles.title,
            articles.content,
            articles.created_at,
            articles.updated_at,
            users.username AS author
        FROM articles
        INNER JOIN users ON articles.author_id = users.id
        ORDER BY articles.created_at DESC
        LIMIT ${limit} OFFSET ${offset}
    `);

    // sql.js 的 exec() 返回格式不同，需要手动转换
    let articles = [];
    if (results.length > 0) {
        const cols = results[0].columns;
        articles = results[0].values.map(row => {
            const obj = {};
            cols.forEach((col, i) => { obj[col] = row[i]; });
            return obj;
        });
    }

    const countResult = db.exec('SELECT COUNT(*) AS total FROM articles');
    const total = countResult[0].values[0][0];

    res.json({
        success: true,
        data: {
            page: page,
            limit: limit,
            total: total,
            articles: articles
        }
    });
});
```

</details>

#### 逐行解释

```javascript
const { db } = require('../database/db');
```

从 `database/db.js` 引入 `db` 对象。因为 `require` 有缓存，这个 `db` 和 `server.js` 里的是同一个对象——**整个应用只有一个数据库连接。**

```javascript
LIMIT ? OFFSET ?
```

`LIMIT` 限制返回的行数，`OFFSET` 跳过前面的行。`LIMIT 10 OFFSET 20` = 跳过前 20 行，取接下来的 10 行（第 3 页，每页 10 条）。

```javascript
INNER JOIN users ON articles.author_id = users.id
```

关联 `users` 表，把 `articles.author_id` 对应的用户名取出来，用 `AS author` 重命名为 `author` 字段。

> 🔥 **魔鬼细节**：`better-sqlite3` 的 `.run()` 返回 `{ changes, lastInsertRowid }`，`.get()` 返回单行对象或 `undefined`，`.all()` 返回数组。**这三个方法都是同步的**——不需要 `await`，不需要 `async` 函数。这是 `better-sqlite3` 对比其他数据库驱动最大的优势。

---

### 步骤 7：验证——整个流程跑通

```bash
npm run dev
```

预期输出：

```
✅ 数据库连接已建立（单例模式）
✅ 数据库基础初始化完成
✅ 数据库表结构已就绪（users, articles, comments）
✅ 数据库初始化完成
Server is running on http://localhost:3000
```

然后用 Thunder Client 测试 `GET http://localhost:3000/api/articles`：

```json
{
    "success": true,
    "data": {
        "page": 1,
        "limit": 10,
        "total": 5,
        "articles": [
            {
                "id": 5,
                "title": "为什么需要参数化查询",
                "content": "SQL 注入是最常见的 Web 安全漏洞之一...",
                "created_at": "...",
                "updated_at": "...",
                "author": "charlie"
            },
            // ... 更多文章
        ]
    }
}
```

> 如果你看到 `total: 0`，说明测试数据还没插入。运行 `node database/seed.js` 后再试。

---

### 🤔 想多一点：为什么 `require` 缓存 = 天然单例？

Node.js 的模块加载机制：第一次 `require('./database/db')` 时：
1. 读取 `db.js` 文件内容。
2. 执行代码（`const db = new Database(...)`）。
3. 把 `module.exports` 的结果缓存起来。
4. 返回缓存结果。

第二次 `require('./database/db')` 时：
1. 发现缓存里已经有了。
2. **直接返回缓存结果，不再执行代码。**

所以 `new Database(dbPath)` 只执行了一次——整个应用共享一个 `db` 对象。这就是"单例模式"在 Node.js 中最自然的实现方式。

---

### ❌ 常见错误 → ✅ 解决方案

| 错误信息 / 现象 | 原因 | 解决 |
|-----------------|------|------|
| `Cannot find module '../database/db'` | 文件路径拼写错误或文件不存在 | 确认 `database/db.js` 已创建，`require` 路径正确 |
| 路由中 `db` 是 `undefined` | `database/db.js` 中 `module.exports` 没导出 `db` | 确认 `module.exports = { db, initDatabase }` |
| `npm run dev` 启动后 GET /api/articles 返回空数组 | 测试数据未插入 | 运行 `node database/seed.js` |
| 多次 `require` 后 `db` 不是同一个对象 | 不同路径 `require` 导致缓存 key 不同 | 确保所有地方都用相同的路径 `require('../database/db')` |
| `db.prepare is not a function` | `better-sqlite3` 版本问题或 `require` 路径错误 | 确认 `const { db } = require('../database/db')`，`db` 是 `Database` 实例 |

---

## 四、完整代码清单

### `blog-backend/database/db.js`（本章新建）

```javascript
// database/db.js — 数据库连接模块（单例）
const Database = require('better-sqlite3');
const path = require('path');

// 数据库文件路径：blog-backend/blog.db
const dbPath = path.join(__dirname, '..', 'blog.db');

// 创建数据库连接（整个应用共用一个）
const db = new Database(dbPath);

// 开启外键约束
db.pragma('foreign_keys = ON');

console.log('✅ 数据库连接已建立（单例模式）');

/**
 * 初始化数据库表结构
 */
function initDatabase() {
    console.log('✅ 数据库基础初始化完成');
}

module.exports = { db, initDatabase };
```

### `blog-backend/database/schema.js`（本章重构）

```javascript
// database/schema.js — 数据库表结构定义（重构版）

/**
 * 创建所有表（幂等）
 * @param {Database} db 数据库连接对象
 */
function createTables(db) {
    db.exec(`
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            created_at TEXT DEFAULT (datetime('now'))
        )
    `);

    db.exec(`
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            author_id INTEGER NOT NULL,
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (author_id) REFERENCES users(id)
        )
    `);

    db.exec(`
        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL,
            article_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (article_id) REFERENCES articles(id),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    `);

    console.log('✅ 数据库表结构已就绪（users, articles, comments）');
}

module.exports = { createTables };
```

### `blog-backend/server.js`（本章重构）

```javascript
const express = require('express');
const { db, initDatabase } = require('./database/db');
const { createTables } = require('./database/schema');

const articlesRouter = require('./routes/articles');
const authRouter = require('./routes/auth');
const errorHandler = require('./middleware/errorHandler');

const app = express();

// 初始化数据库
initDatabase();
createTables(db);
console.log('✅ 数据库初始化完成');

// 中间件
app.use(express.json());

// 路由
app.use('/api/articles', articlesRouter);
app.use('/api/auth', authRouter);

// 404 兜底
app.use((req, res) => {
    res.status(404).json({
        success: false,
        error: {
            message: `接口不存在：${req.method} ${req.originalUrl}`,
            code: 'NOT_FOUND'
        }
    });
});

// 错误处理中间件
app.use(errorHandler);

app.listen(3000, () => {
    console.log('Server is running on http://localhost:3000');
});
```

### `blog-backend/routes/articles.js`（本章修改——引入 db）

```javascript
const express = require('express');
const router = express.Router();
const { db } = require('../database/db');     // ← 新增
const AppError = require('../utils/AppError');

// ========== 模拟数据库：用数组存储文章（保留旧代码，下章完全替换） ==========
let articles = [
    // ... 旧数据（略）
];

// GET /api/articles — 数据库版（新增）
router.get('/', (req, res) => {
    const page = parseInt(req.query.page) || 1;
    const limit = parseInt(req.query.limit) || 10;
    const offset = (page - 1) * limit;

    const selectArticles = db.prepare(`
        SELECT 
            articles.id,
            articles.title,
            articles.content,
            articles.created_at,
            articles.updated_at,
            users.username AS author
        FROM articles
        INNER JOIN users ON articles.author_id = users.id
        ORDER BY articles.created_at DESC
        LIMIT ? OFFSET ?
    `);

    const articles = selectArticles.all(limit, offset);

    const countResult = db.prepare('SELECT COUNT(*) AS total FROM articles').get();

    res.json({
        success: true,
        data: {
            page: page,
            limit: limit,
            total: countResult.total,
            articles: articles
        }
    });
});

// ... 其他路由暂时保留旧代码（下章替换）

module.exports = router;
```

### `blog-backend/` 目录结构（本章最终状态）

```
blog-backend/
├── server.js              ← 本章重构：使用 db.js 统一连接
├── package.json
├── package-lock.json
├── .gitignore
├── blog.db
├── node_modules/
├── database/
│   ├── init.js            ← 第 12 章遗留（可保留）
│   ├── db.js              ← 本章新建：单例连接模块
│   ├── schema.js          ← 本章重构：接收 db 参数
│   └── seed.js            ← 第 14 章：测试数据
├── routes/
│   ├── articles.js        ← 本章修改：引入 db，GET / 改为数据库查询
│   └── auth.js
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
| 1 | `npm run dev` | 输出 "✅ 数据库连接已建立"，"✅ 数据库表结构已就绪"，"Server is running..." |
| 2 | `GET /api/articles` | 返回 `{ success: true, data: { total: 5, articles: [...] } }`（每篇文章带 `author` 字段） |
| 3 | `Ctrl+C` 停止，再 `npm run dev` | 同样正常启动，数据还在 |
| 4 | 在 `server.js` 中临时在两个地方 `require('./database/db')`，比较 `===` | 返回 `true`（同一个引用） |
| 5 | 故意在 `database/db.js` 中把 `module.exports` 改成 `module.exports = { db: null }` | 启动后访问 `/api/articles` 报错——验证了路由确实在使用 db 模块 |

全部通过？数据库已经成功集成到 Express 中。下一章，把剩下的 4 个接口也全部升级为数据库版。

---

## 六、小结表格

| 学到的东西 | 一句话解释 |
|-----------|-----------|
| 单例模式（Singleton） | 整个应用只创建一个数据库连接，所有模块共享 |
| `require` 缓存 = 天然单例 | Node.js 第一次 `require` 后缓存结果，后续直接返回缓存 |
| `database/db.js` | 数据库连接模块——创建 `db` 对象，导出供所有模块使用 |
| `schema.js` 重构 | 不再自己创建连接，接收 `db` 参数来建表 |
| 路由中使用 `db` | `const { db } = require('../database/db')`，然后用 `db.prepare()` 执行 SQL |
| `LIMIT ? OFFSET ?` | 分页查询的标准 SQL 写法 |
| `INNER JOIN` 带出作者名 | `JOIN users ON articles.author_id = users.id` |

---

## 七、术语附录

| 术语 | 英文 | 通俗解释 | 本章出现位置 | 字面陷阱 |
|------|------|----------|-------------|----------|
| 数据库连接模块 | Database Connection Module | 专门管理数据库连接的文件，导出 `db` 对象供其他模块使用。 | 步骤 3 | 不是"连接数据库的模块"——它不仅连接，还负责维护连接的生命周期。 |
| 单例模式 | Singleton Pattern | 设计模式：保证一个类只有一个实例，并提供全局访问点。在 Node.js 中，`require` 缓存天然实现单例。 | 步骤 2 | 不是"只有一个例子"——是"只有一个实例"，整个应用共享同一个对象。 |
| 连接生命周期 | Connection Lifecycle | 数据库连接从创建到关闭的整个过程。在 Express 中，连接在服务器启动时创建，在服务器关闭时释放。 | 步骤 3 | 不是"生命"——是从"new Database()"到"db.close()"的整个时间段。 |
| `OFFSET` | — | SQL 中分页查询的关键字，跳过前 N 行。`LIMIT 10 OFFSET 20` = 跳过前 20 行，取 10 行。 | 步骤 6 | 不是"偏移"——是"跳过"，OFFSET 的值 = (页码 - 1) × 每页条数。 |

---

## 八、已知坑点与禁止事项

1. **不要在路由中 `new Database()`**：每次请求都创建新连接是巨大的资源浪费。始终从 `database/db.js` 引入单例 `db` 对象。

2. **`require` 路径必须一致**：如果一处用 `require('../database/db')`，另一处用 `require('./database/db')`（相对路径不同），Node.js 会认为这是两个不同的模块，缓存 key 不同，导致创建两个连接。确保所有地方的使用相同的相对路径。

3. **`better-sqlite3` 的 `db` 对象是同步的**：可以直接用，不需要 `await`。这是它最大的优势——学习阶段不用和异步打架。

4. **`db.prepare()` 返回的语句对象可以复用**：如果你在路由中多次执行相同的 SQL（只是参数不同），把 `db.prepare()` 放在路由外面，避免每次请求都重新编译。

5. **`sql.js` 用户注意**：每次写操作后需要调用 `saveDatabase()` 将数据持久化到磁盘。`better-sqlite3` 自动处理这一点。

---

## 九、下一步建议

数据库连接已就绪，`GET /api/articles` 已经改为数据库版本。接下来，把剩下的 4 个接口也全部升级：

- **下一章**：[16-博客接口升级：数据真正存到数据库](16-博客接口升级：数据真正存到数据库.md)——重写 `routes/articles.js` 的全部 5 个接口为数据库操作，处理边界情况（文章不存在、changes 为 0），用 `db.prepare().run()` 的返回值判断操作是否成功，验证重启后数据不丢失。

---

> 📊 本教程无可视化
>
> 本教程编辑记录：2026-06-12 初始版本。