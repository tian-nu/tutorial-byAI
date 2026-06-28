# 附录F：完整代码清单

> 本附录列出 `blog-backend/` 项目所有文件的最终完整代码。每个文件标注"截至第X章最终状态"。代码可通过折叠块展开查看。

---

## 目录

- [server.js](#serverjs) — 截至第 26 章
- [package.json](#packagejson) — 截至第 26 章
- [.gitignore](#gitignore) — 截至第 18 章
- [.env.example](#envexample) — 截至第 18 章
- [routes/articles.js](#routesarticlesjs) — 截至第 24 章
- [routes/auth.js](#routesauthjs) — 截至第 18 章
- [routes/comments.js](#routescommentsjs) — 截至第 21 章
- [routes/upload.js](#routesuploadjs) — 截至第 24 章
- [middleware/auth.js](#middlewareauthjs) — 截至第 19 章
- [middleware/logger.js](#middlewareloggerjs) — 截至第 06 章
- [middleware/errorHandler.js](#middlewareerrorhandlerjs) — 截至第 08 章
- [middleware/upload.js](#middlewareuploadjs) — 截至第 24 章
- [database/db.js](#databasedbjs) — 截至第 15 章
- [database/schema.js](#databaseschemajs) — 截至第 24 章
- [database/seed.js](#databaseseedjs) — 截至第 14 章
- [utils/AppError.js](#utilsapperrorjs) — 截至第 08 章
- [tests/setup.js](#testssetupjs) — 截至第 26 章
- [tests/auth.test.js](#testsauthtestjs) — 截至第 26 章
- [tests/articles.test.js](#testsarticlestestjs) — 截至第 26 章
- [jest.config.js](#jestconfigjs) — 截至第 26 章
- [Dockerfile](#dockerfile) — 截至第 29 章
- [docker-compose.yml](#docker-composeyml) — 截至第 30 章
- [.dockerignore](#dockerignore) — 截至第 29 章
- [ecosystem.config.js](#ecosystemconfigjs) — 截至第 27 章

---

## server.js

> 截至第 26 章最终状态（支持测试的 `module.exports` 导出）

<details>
<summary>展开代码</summary>

```javascript
require('dotenv').config();

const express = require('express');
const path = require('path');
const morgan = require('morgan');
const cors = require('cors');
const { db, initDatabase } = require('./database/db');
const { createTables } = require('./database/schema');

const articlesRouter = require('./routes/articles');
const authRouter = require('./routes/auth');
const commentsRouter = require('./routes/comments');
const uploadRouter = require('./routes/upload');
const errorHandler = require('./middleware/errorHandler');

const app = express();
const PORT = process.env.PORT || 3000;

// 数据库初始化
initDatabase();
createTables(db);
console.log('✅ 数据库初始化完成');

// 全局中间件
app.use(cors());
app.use(morgan('dev'));
app.use(express.json());
app.use('/uploads', express.static(path.join(__dirname, 'uploads')));

// 路由
app.use('/api/articles', articlesRouter);
app.use('/api/auth', authRouter);
app.use('/api', commentsRouter);
app.use('/api', uploadRouter);

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

// 全局错误处理
app.use(errorHandler);

// 导出 app（供测试使用）
module.exports = app;

// 只在直接运行时启动服务器
if (require.main === module) {
    app.listen(PORT, () => {
        console.log(`Server is running on http://localhost:${PORT}`);
    });
}
```

</details>

---

## package.json

> 截至第 26 章最终状态

<details>
<summary>展开代码</summary>

```json
{
  "name": "blog-backend",
  "version": "1.0.0",
  "description": "博客系统后端 — Node.js速成教程贯穿项目",
  "main": "server.js",
  "scripts": {
    "start": "node server.js",
    "dev": "nodemon server.js",
    "test": "jest --runInBand",
    "test:watch": "jest --watch",
    "test:coverage": "jest --coverage"
  },
  "keywords": [],
  "author": "",
  "license": "ISC",
  "dependencies": {
    "bcryptjs": "^2.4.3",
    "better-sqlite3": "^11.0.0",
    "cors": "^2.8.5",
    "dotenv": "^16.4.0",
    "express": "^4.18.2",
    "jsonwebtoken": "^9.0.2",
    "morgan": "^1.10.0",
    "multer": "^1.4.5-lts.1"
  },
  "devDependencies": {
    "jest": "^29.7.0",
    "nodemon": "^3.1.0",
    "supertest": "^6.3.4"
  }
}
```

</details>

---

## .gitignore

> 截至第 18 章最终状态

<details>
<summary>展开代码</summary>

```gitignore
node_modules/
blog.db
test.db
.env
uploads/
```

</details>

---

## .env.example

> 截至第 18 章最终状态（示例环境变量文件，不含真实密钥）

<details>
<summary>展开代码</summary>

```bash
# .env.example — 环境变量示例文件
# 复制此文件为 .env 并填入真实值
# 注意：.env 文件不应提交到 Git！

# JWT 签名密钥（至少 32 字符随机字符串）
# 生成命令：node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"
JWT_SECRET=your_super_secret_jwt_key_change_in_production_min_32_chars

# 服务器端口（可选，默认 3000）
PORT=3000

# 运行环境（development / production）
NODE_ENV=development
```

</details>

---

## routes/articles.js

> 截至第 24 章最终状态（完整 CRUD + 分页 + 搜索 + 评论数 + 封面图 + 权限保护）

<details>
<summary>展开代码</summary>

```javascript
const express = require('express');
const router = express.Router();
const { db } = require('../database/db');
const { authenticate } = require('../middleware/auth');
const AppError = require('../utils/AppError');

// ========== 文章接口 ==========

// GET /api/articles — 获取所有文章（支持分页 + 搜索 + 评论数）
router.get('/', (req, res) => {
    // 1. 解析查询参数
    let page = parseInt(req.query.page) || 1;
    let limit = parseInt(req.query.limit) || 10;
    const search = req.query.search ? req.query.search.trim() : '';

    // 2. 参数校验
    if (page < 1) page = 1;
    if (limit < 1) limit = 1;
    if (limit > 100) limit = 100;

    const offset = (page - 1) * limit;

    // 3. 动态构建 SQL
    let whereClause = '';
    const params = [];

    if (search) {
        whereClause = 'WHERE (articles.title LIKE ? OR articles.content LIKE ?)';
        params.push(`%${search}%`, `%${search}%`);
    }

    // 4. 查询总数
    const countSql = `SELECT COUNT(*) AS total FROM articles ${whereClause}`;
    const { total } = db.prepare(countSql).get(...params);

    // 5. 查询数据
    const dataSql = `
        SELECT
            articles.id,
            articles.title,
            articles.content,
            articles.cover_image,
            articles.author_id,
            articles.created_at,
            articles.updated_at,
            users.username AS author,
            (SELECT COUNT(*) FROM comments WHERE comments.article_id = articles.id) AS comment_count
        FROM articles
        INNER JOIN users ON articles.author_id = users.id
        ${whereClause}
        ORDER BY articles.created_at DESC
        LIMIT ? OFFSET ?
    `;

    const articles = db.prepare(dataSql).all(...params, limit, offset);

    // 6. 返回结果
    res.json({
        success: true,
        data: {
            articles,
            pagination: {
                page,
                limit,
                total,
                totalPages: Math.ceil(total / limit)
            }
        }
    });
});

// GET /api/articles/:id — 获取单篇文章
router.get('/:id', (req, res) => {
    const id = parseInt(req.params.id);

    const article = db.prepare(`
        SELECT
            articles.id,
            articles.title,
            articles.content,
            articles.cover_image,
            articles.author_id,
            articles.created_at,
            articles.updated_at,
            users.username AS author
        FROM articles
        INNER JOIN users ON articles.author_id = users.id
        WHERE articles.id = ?
    `).get(id);

    if (!article) {
        throw new AppError('文章不存在', 404);
    }

    res.json({
        success: true,
        data: article
    });
});

// POST /api/articles — 创建文章（需登录）
router.post('/', authenticate, (req, res) => {
    const { title, content, cover_image } = req.body;

    if (!title || !content) {
        throw new AppError('标题和内容为必填字段', 400);
    }

    const author_id = req.user.userId;
    const now = new Date().toISOString();

    const result = db.prepare(`
        INSERT INTO articles (title, content, cover_image, author_id, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?)
    `).run(title, content, cover_image || null, author_id, now, now);

    const newArticle = db.prepare(`
        SELECT
            articles.id,
            articles.title,
            articles.content,
            articles.cover_image,
            articles.author_id,
            articles.created_at,
            articles.updated_at,
            users.username AS author
        FROM articles
        INNER JOIN users ON articles.author_id = users.id
        WHERE articles.id = ?
    `).get(result.lastInsertRowid);

    res.status(201).json({
        success: true,
        data: newArticle
    });
});

// PUT /api/articles/:id — 更新文章（需登录 + 只能改自己的）
router.put('/:id', authenticate, (req, res) => {
    const id = parseInt(req.params.id);
    const { title, content, cover_image } = req.body;

    if (!title || !content) {
        throw new AppError('标题和内容为必填字段', 400);
    }

    // 检查文章是否存在
    const article = db.prepare('SELECT * FROM articles WHERE id = ?').get(id);
    if (!article) {
        throw new AppError('文章不存在', 404);
    }

    // 检查归属：只能改自己的文章
    if (article.author_id !== req.user.userId) {
        throw new AppError('无权修改此文章', 403);
    }

    const now = new Date().toISOString();

    db.prepare(`
        UPDATE articles
        SET title = ?, content = ?, cover_image = ?, updated_at = ?
        WHERE id = ?
    `).run(title, content, cover_image || null, now, id);

    const updatedArticle = db.prepare(`
        SELECT
            articles.id,
            articles.title,
            articles.content,
            articles.cover_image,
            articles.author_id,
            articles.created_at,
            articles.updated_at,
            users.username AS author
        FROM articles
        INNER JOIN users ON articles.author_id = users.id
        WHERE articles.id = ?
    `).get(id);

    res.json({
        success: true,
        data: updatedArticle
    });
});

// DELETE /api/articles/:id — 删除文章（需登录 + 只能删自己的）
router.delete('/:id', authenticate, (req, res) => {
    const id = parseInt(req.params.id);

    const article = db.prepare('SELECT * FROM articles WHERE id = ?').get(id);
    if (!article) {
        throw new AppError('文章不存在', 404);
    }

    if (article.author_id !== req.user.userId) {
        throw new AppError('无权删除此文章', 403);
    }

    // 先删除关联的评论
    db.prepare('DELETE FROM comments WHERE article_id = ?').run(id);
    // 再删除文章
    db.prepare('DELETE FROM articles WHERE id = ?').run(id);

    res.status(204).send();
});

module.exports = router;
```

</details>

---

## routes/auth.js

> 截至第 18 章最终状态（注册 + 登录）

<details>
<summary>展开代码</summary>

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

    // 1. 验证必填字段
    if (!username || !email || !password) {
        throw new AppError('用户名、邮箱和密码为必填字段', 400);
    }

    // 2. 验证密码长度
    if (password.length < 6) {
        throw new AppError('密码至少需要 6 位', 400);
    }

    // 3. 验证邮箱格式
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
        throw new AppError('邮箱格式不正确', 400);
    }

    // 4. 检查用户名是否已存在
    const existingUser = db.prepare('SELECT id FROM users WHERE username = ?').get(username);
    if (existingUser) {
        throw new AppError('用户名已被注册', 409);
    }

    // 5. 检查邮箱是否已存在
    const existingEmail = db.prepare('SELECT id FROM users WHERE email = ?').get(email);
    if (existingEmail) {
        throw new AppError('邮箱已被注册', 409);
    }

    // 6. 哈希密码
    const saltRounds = 10;
    const password_hash = await bcrypt.hash(password, saltRounds);

    // 7. 插入数据库
    const now = new Date().toISOString();
    const result = db.prepare(`
        INSERT INTO users (username, email, password_hash, created_at)
        VALUES (?, ?, ?, ?)
    `).run(username, email, password_hash, now);

    // 8. 返回新用户信息（不返回 password_hash）
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

    // 1. 验证必填字段
    if (!email || !password) {
        throw new AppError('邮箱和密码为必填字段', 400);
    }

    // 2. 查找用户
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
        { userId: user.id, username: user.username },
        process.env.JWT_SECRET,
        { expiresIn: '7d' }
    );

    // 5. 返回 token 和用户信息
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

</details>

---

## routes/comments.js

> 截至第 21 章最终状态

<details>
<summary>展开代码</summary>

```javascript
const express = require('express');
const router = express.Router();
const { db } = require('../database/db');
const { authenticate } = require('../middleware/auth');
const AppError = require('../utils/AppError');

// ========== 评论接口 ==========

// POST /api/articles/:id/comments — 创建评论（需登录）
router.post('/articles/:id/comments', authenticate, (req, res) => {
    const articleId = parseInt(req.params.id);
    const { content } = req.body;

    if (!content) {
        throw new AppError('评论内容不能为空', 400);
    }

    // 检查文章是否存在
    const article = db.prepare('SELECT id FROM articles WHERE id = ?').get(articleId);
    if (!article) {
        throw new AppError('文章不存在', 404);
    }

    const now = new Date().toISOString();
    const result = db.prepare(`
        INSERT INTO comments (content, article_id, user_id, created_at)
        VALUES (?, ?, ?, ?)
    `).run(content, articleId, req.user.userId, now);

    const newComment = db.prepare(`
        SELECT
            comments.id,
            comments.content,
            comments.article_id,
            comments.user_id,
            comments.created_at,
            users.username AS author
        FROM comments
        INNER JOIN users ON comments.user_id = users.id
        WHERE comments.id = ?
    `).get(result.lastInsertRowid);

    res.status(201).json({
        success: true,
        data: newComment
    });
});

// GET /api/articles/:id/comments — 获取文章的所有评论
router.get('/articles/:id/comments', (req, res) => {
    const articleId = parseInt(req.params.id);

    // 检查文章是否存在
    const article = db.prepare('SELECT id FROM articles WHERE id = ?').get(articleId);
    if (!article) {
        throw new AppError('文章不存在', 404);
    }

    const comments = db.prepare(`
        SELECT
            comments.id,
            comments.content,
            comments.article_id,
            comments.user_id,
            comments.created_at,
            users.username AS author
        FROM comments
        INNER JOIN users ON comments.user_id = users.id
        WHERE comments.article_id = ?
        ORDER BY comments.created_at DESC
    `).all(articleId);

    res.json({
        success: true,
        data: comments
    });
});

// DELETE /api/comments/:id — 删除评论（需登录，只能删自己的）
router.delete('/comments/:id', authenticate, (req, res) => {
    const id = parseInt(req.params.id);

    const comment = db.prepare('SELECT * FROM comments WHERE id = ?').get(id);
    if (!comment) {
        throw new AppError('评论不存在', 404);
    }

    if (comment.user_id !== req.user.userId) {
        throw new AppError('无权删除此评论', 403);
    }

    db.prepare('DELETE FROM comments WHERE id = ?').run(id);

    res.status(204).send();
});

module.exports = router;
```

</details>

---

## routes/upload.js

> 截至第 24 章最终状态

<details>
<summary>展开代码</summary>

```javascript
const express = require('express');
const router = express.Router();
const upload = require('../middleware/upload');
const { authenticate } = require('../middleware/auth');
const AppError = require('../utils/AppError');

// ========== 文件上传接口 ==========

// POST /api/upload — 上传单张图片（需登录）
router.post('/upload', authenticate, (req, res, next) => {
    upload.single('image')(req, res, function (err) {
        // multer 的错误处理
        if (err) {
            if (err.code === 'LIMIT_FILE_SIZE') {
                return next(new AppError('文件大小不能超过 5MB', 413));
            }
            if (err.message.includes('只允许上传')) {
                return next(new AppError(err.message, 400));
            }
            return next(new AppError('文件上传失败', 500));
        }

        // 没有上传文件
        if (!req.file) {
            return next(new AppError('请选择要上传的图片', 400));
        }

        // 返回图片 URL
        const imageUrl = `/uploads/${req.file.filename}`;

        res.status(201).json({
            success: true,
            data: {
                url: imageUrl,
                filename: req.file.filename,
                size: req.file.size,
                mimetype: req.file.mimetype
            }
        });
    });
});

module.exports = router;
```

</details>

---

## middleware/auth.js

> 截至第 19 章最终状态

<details>
<summary>展开代码</summary>

```javascript
const jwt = require('jsonwebtoken');
const AppError = require('../utils/AppError');

/**
 * 认证中间件
 * 从请求头 Authorization: Bearer <token> 中提取 JWT，
 * 验证签名，将用户信息挂到 req.user。
 */
function authenticate(req, res, next) {
    // 1. 从请求头提取 Authorization
    const authHeader = req.headers.authorization;

    // 2. 检查是否存在且格式正确
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
        throw new AppError('未提供认证令牌', 401);
    }

    // 3. 提取 token
    const token = authHeader.split(' ')[1];

    // 4. 验证 JWT
    try {
        const decoded = jwt.verify(token, process.env.JWT_SECRET);
        // 5. 把解码后的用户信息挂到 req.user
        req.user = decoded;
        next();
    } catch (err) {
        // 区分 token 过期和其他错误
        if (err.name === 'TokenExpiredError') {
            throw new AppError('认证令牌已过期，请重新登录', 401);
        }
        throw new AppError('认证令牌无效', 401);
    }
}

module.exports = { authenticate };
```

</details>

---

## middleware/logger.js

> 截至第 06 章最终状态

<details>
<summary>展开代码</summary>

```javascript
/**
 * 日志中间件
 * 记录每个请求的方法、路径、状态码和耗时
 */
function logger(req, res, next) {
    const start = Date.now();

    res.on('finish', () => {
        const duration = Date.now() - start;
        console.log(`${req.method} ${req.originalUrl} ${res.statusCode} — ${duration}ms`);
    });

    next();
}

module.exports = logger;
```

</details>

---

## middleware/errorHandler.js

> 截至第 08 章最终状态

<details>
<summary>展开代码</summary>

```javascript
/**
 * 全局错误处理中间件
 * Express 通过 4 个参数自动识别为错误处理中间件
 */
const errorHandler = (err, req, res, next) => {
    // 如果错误没有状态码，默认 500
    const statusCode = err.statusCode || 500;
    const message = err.message || '服务器内部错误';

    // 开发环境：返回详细错误信息（含堆栈）
    if (process.env.NODE_ENV === 'development') {
        console.error('❌ 错误详情：', err);
        return res.status(statusCode).json({
            success: false,
            error: {
                message,
                code: err.code || 'INTERNAL_ERROR',
                stack: err.stack
            }
        });
    }

    // 生产环境：只返回简洁信息，不暴露堆栈
    console.error('❌ 错误：', message);
    res.status(statusCode).json({
        success: false,
        error: {
            message: statusCode === 500 ? '服务器内部错误' : message,
            code: err.code || 'INTERNAL_ERROR'
        }
    });
};

module.exports = errorHandler;
```

</details>

---

## middleware/upload.js

> 截至第 24 章最终状态

<details>
<summary>展开代码</summary>

```javascript
const multer = require('multer');
const path = require('path');
const crypto = require('crypto');

// ========== 1. 配置存储位置和文件名 ==========
const storage = multer.diskStorage({
    // 存储目录
    destination: function (req, file, cb) {
        cb(null, 'uploads/');
    },
    // 文件名规则：时间戳 + UUID + 原始扩展名（防止冲突）
    filename: function (req, file, cb) {
        const uniqueSuffix = Date.now() + '-' + crypto.randomUUID();
        const ext = path.extname(file.originalname);
        cb(null, uniqueSuffix + ext);
    }
});

// ========== 2. 文件类型过滤器（白名单） ==========
const fileFilter = (req, file, cb) => {
    const allowedTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp'];

    if (allowedTypes.includes(file.mimetype)) {
        cb(null, true);   // 接受文件
    } else {
        cb(new Error('只允许上传 JPG、PNG、GIF、WebP 格式的图片'), false);
    }
};

// ========== 3. 创建 multer 实例 ==========
const upload = multer({
    storage: storage,
    fileFilter: fileFilter,
    limits: {
        fileSize: 5 * 1024 * 1024   // 限制 5MB
    }
});

module.exports = upload;
```

</details>

---

## database/db.js

> 截至第 15 章最终状态

<details>
<summary>展开代码</summary>

```javascript
// database/db.js — 数据库连接模块（单例）
const Database = require('better-sqlite3');
const path = require('path');

// 数据库文件路径：blog-backend/blog.db
const dbPath = path.join(__dirname, '..', 'blog.db');

// 创建数据库连接（整个应用共用一个）
const db = new Database(dbPath);

// 开启外键约束（SQLite 默认不开启）
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

</details>

---

## database/schema.js

> 截至第 24 章最终状态（articles 表含 cover_image 列）

<details>
<summary>展开代码</summary>

```javascript
// database/schema.js — 数据库表结构定义

/**
 * 创建所有表（幂等 — 使用 IF NOT EXISTS）
 * @param {Database} db 数据库连接对象
 */
function createTables(db) {
    // 用户表
    db.exec(`
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            created_at TEXT DEFAULT (datetime('now'))
        )
    `);

    // 文章表
    db.exec(`
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            cover_image TEXT,
            author_id INTEGER NOT NULL,
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (author_id) REFERENCES users(id)
        )
    `);

    // 评论表
    db.exec(`
        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL,
            article_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (article_id) REFERENCES articles(id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    `);

    console.log('✅ 数据库表结构已就绪（users, articles, comments）');
}

module.exports = { createTables };
```

</details>

---

## database/seed.js

> 截至第 14 章最终状态

<details>
<summary>展开代码</summary>

```javascript
// database/seed.js — 测试数据插入脚本
const Database = require('better-sqlite3');
const path = require('path');

const dbPath = path.join(__dirname, '..', 'blog.db');
const db = new Database(dbPath);
db.pragma('foreign_keys = ON');

// 插入测试用户（注意：password_hash 是占位符，这些用户无法登录）
const insertUsers = db.transaction(() => {
    const stmt = db.prepare(`
        INSERT OR IGNORE INTO users (username, email, password_hash, created_at)
        VALUES (?, ?, ?, datetime('now'))
    `);

    stmt.run('alice', 'alice@example.com', 'hash_placeholder');
    stmt.run('bob', 'bob@example.com', 'hash_placeholder');
    stmt.run('charlie', 'charlie@example.com', 'hash_placeholder');
});

// 插入测试文章
const insertArticles = db.transaction(() => {
    const stmt = db.prepare(`
        INSERT INTO articles (title, content, author_id, created_at, updated_at)
        VALUES (?, ?, ?, datetime('now'), datetime('now'))
    `);

    stmt.run('Node.js 入门指南', 'Node.js 是一个基于 Chrome V8 引擎的 JavaScript 运行时...', 1);
    stmt.run('Express 框架详解', 'Express 是 Node.js 最流行的 Web 框架...', 1);
    stmt.run('RESTful API 设计', 'RESTful 是一种 API 设计风格...', 2);
    stmt.run('SQLite 入门', 'SQLite 是一个零配置的嵌入式数据库...', 2);
    stmt.run('为什么需要参数化查询', 'SQL 注入是最常见的 Web 安全漏洞之一...', 3);
});

// 插入测试评论
const insertComments = db.transaction(() => {
    const stmt = db.prepare(`
        INSERT INTO comments (content, article_id, user_id, created_at)
        VALUES (?, ?, ?, datetime('now'))
    `);

    stmt.run('写得很清楚，对我帮助很大！', 1, 2);
    stmt.run('请问 Express 5 有什么新特性？', 2, 3);
    stmt.run('RESTful 这个概念终于理解了', 3, 1);
});

console.log('🌱 开始插入测试数据...');
insertUsers();
insertArticles();
insertComments();
console.log('✅ 测试数据插入完成！');
console.log('   - 用户：alice, bob, charlie（密码哈希为占位符，无法登录）');
console.log('   - 文章：5 篇');
console.log('   - 评论：3 条');

db.close();
```

</details>

---

## utils/AppError.js

> 截至第 08 章最终状态

<details>
<summary>展开代码</summary>

```javascript
/**
 * 自定义应用错误类
 * 用于在路由中抛出可预期的错误，由全局错误处理中间件统一处理
 */
class AppError extends Error {
    /**
     * @param {string} message — 错误信息
     * @param {number} statusCode — HTTP 状态码
     */
    constructor(message, statusCode) {
        super(message);
        this.statusCode = statusCode;
        this.isOperational = true;  // 标记为可预期的操作错误
        Error.captureStackTrace(this, this.constructor);
    }
}

module.exports = AppError;
```

</details>

---

## tests/setup.js

> 截至第 26 章最终状态

<details>
<summary>展开代码</summary>

```javascript
// tests/setup.js — 测试环境配置
const Database = require('better-sqlite3');
const path = require('path');

// 使用独立的测试数据库（不影响开发数据）
const testDbPath = path.join(__dirname, '..', 'test.db');
const testDb = new Database(testDbPath);
testDb.pragma('foreign_keys = ON');

// 导出测试数据库连接
module.exports = { testDb };
```

</details>

---

## tests/auth.test.js

> 截至第 26 章最终状态

<details>
<summary>展开代码</summary>

```javascript
const request = require('supertest');
const app = require('../server');
const { testDb } = require('./setup');

// 在每个测试用例之前清空数据库
beforeEach(() => {
    testDb.exec('DELETE FROM comments');
    testDb.exec('DELETE FROM articles');
    testDb.exec('DELETE FROM users');
});

describe('认证接口', () => {
    describe('POST /api/auth/register', () => {
        it('应该成功注册新用户', async () => {
            const res = await request(app)
                .post('/api/auth/register')
                .send({
                    username: 'testuser',
                    email: 'test@example.com',
                    password: 'test123456'
                })
                .expect(201);

            expect(res.body.success).toBe(true);
            expect(res.body.data).toHaveProperty('id');
            expect(res.body.data.username).toBe('testuser');
            expect(res.body.data.email).toBe('test@example.com');
            expect(res.body.data).not.toHaveProperty('password_hash');
        });

        it('重复注册应该返回 409', async () => {
            // 先注册一次
            await request(app)
                .post('/api/auth/register')
                .send({
                    username: 'testuser',
                    email: 'test@example.com',
                    password: 'test123456'
                });

            // 再注册一次
            const res = await request(app)
                .post('/api/auth/register')
                .send({
                    username: 'testuser',
                    email: 'test@example.com',
                    password: 'test123456'
                })
                .expect(409);

            expect(res.body.success).toBe(false);
            expect(res.body.error.message).toBe('用户名已被注册');
        });

        it('缺少必填字段应该返回 400', async () => {
            const res = await request(app)
                .post('/api/auth/register')
                .send({ username: 'test' })
                .expect(400);

            expect(res.body.success).toBe(false);
            expect(res.body.error.message).toContain('必填');
        });

        it('密码太短应该返回 400', async () => {
            const res = await request(app)
                .post('/api/auth/register')
                .send({
                    username: 'testuser',
                    email: 'test@example.com',
                    password: '123'
                })
                .expect(400);

            expect(res.body.error.message).toContain('至少需要 6 位');
        });
    });

    describe('POST /api/auth/login', () => {
        // 先注册一个用户用于登录测试
        beforeEach(async () => {
            await request(app)
                .post('/api/auth/register')
                .send({
                    username: 'logintest',
                    email: 'login@example.com',
                    password: 'test123456'
                });
        });

        it('应该成功登录并返回 token', async () => {
            const res = await request(app)
                .post('/api/auth/login')
                .send({
                    email: 'login@example.com',
                    password: 'test123456'
                })
                .expect(200);

            expect(res.body.success).toBe(true);
            expect(res.body.data).toHaveProperty('token');
            expect(res.body.data.user).toHaveProperty('id');
            expect(res.body.data.user.email).toBe('login@example.com');
        });

        it('密码错误应该返回 401', async () => {
            const res = await request(app)
                .post('/api/auth/login')
                .send({
                    email: 'login@example.com',
                    password: 'wrongpassword'
                })
                .expect(401);

            expect(res.body.error.message).toBe('邮箱或密码错误');
        });

        it('用户不存在应该返回 401', async () => {
            const res = await request(app)
                .post('/api/auth/login')
                .send({
                    email: 'nobody@example.com',
                    password: 'test123456'
                })
                .expect(401);

            expect(res.body.error.message).toBe('邮箱或密码错误');
        });
    });
});
```

</details>

---

## tests/articles.test.js

> 截至第 26 章最终状态

<details>
<summary>展开代码</summary>

```javascript
const request = require('supertest');
const app = require('../server');
const { testDb } = require('./setup');

let token;
let articleId;

// 每个测试用例之前：清空数据库 + 注册登录用户
beforeEach(async () => {
    testDb.exec('DELETE FROM comments');
    testDb.exec('DELETE FROM articles');
    testDb.exec('DELETE FROM users');

    // 注册用户
    await request(app)
        .post('/api/auth/register')
        .send({
            username: 'testauthor',
            email: 'author@example.com',
            password: 'test123456'
        });

    // 登录获取 token
    const loginRes = await request(app)
        .post('/api/auth/login')
        .send({
            email: 'author@example.com',
            password: 'test123456'
        });

    token = loginRes.body.data.token;
});

describe('文章 CRUD 接口', () => {
    describe('GET /api/articles', () => {
        it('应该返回空文章列表', async () => {
            const res = await request(app)
                .get('/api/articles')
                .expect(200);

            expect(res.body.success).toBe(true);
            expect(res.body.data.articles).toEqual([]);
            expect(res.body.data.pagination.total).toBe(0);
        });

        it('应该返回创建的文章', async () => {
            // 先创建一篇文章
            await request(app)
                .post('/api/articles')
                .set('Authorization', `Bearer ${token}`)
                .send({ title: '测试文章', content: '测试内容' });

            const res = await request(app)
                .get('/api/articles')
                .expect(200);

            expect(res.body.data.articles.length).toBe(1);
            expect(res.body.data.articles[0].title).toBe('测试文章');
        });
    });

    describe('GET /api/articles/:id', () => {
        it('应该返回指定文章', async () => {
            const createRes = await request(app)
                .post('/api/articles')
                .set('Authorization', `Bearer ${token}`)
                .send({ title: '测试文章', content: '测试内容' });

            const id = createRes.body.data.id;

            const res = await request(app)
                .get(`/api/articles/${id}`)
                .expect(200);

            expect(res.body.data.title).toBe('测试文章');
        });

        it('不存在的文章应该返回 404', async () => {
            const res = await request(app)
                .get('/api/articles/99999')
                .expect(404);

            expect(res.body.error.message).toBe('文章不存在');
        });
    });

    describe('POST /api/articles', () => {
        it('应该成功创建文章', async () => {
            const res = await request(app)
                .post('/api/articles')
                .set('Authorization', `Bearer ${token}`)
                .send({ title: '新文章', content: '新内容' })
                .expect(201);

            expect(res.body.success).toBe(true);
            expect(res.body.data.title).toBe('新文章');
            expect(res.body.data).toHaveProperty('author');
            articleId = res.body.data.id;
        });

        it('缺少标题应该返回 400', async () => {
            const res = await request(app)
                .post('/api/articles')
                .set('Authorization', `Bearer ${token}`)
                .send({ content: '只有内容' })
                .expect(400);

            expect(res.body.error.message).toContain('标题');
        });

        it('未登录应该返回 401', async () => {
            const res = await request(app)
                .post('/api/articles')
                .send({ title: '测试', content: '测试' })
                .expect(401);

            expect(res.body.error.message).toContain('认证');
        });
    });

    describe('PUT /api/articles/:id', () => {
        it('应该成功更新自己的文章', async () => {
            const createRes = await request(app)
                .post('/api/articles')
                .set('Authorization', `Bearer ${token}`)
                .send({ title: '原标题', content: '原内容' });

            const id = createRes.body.data.id;

            const res = await request(app)
                .put(`/api/articles/${id}`)
                .set('Authorization', `Bearer ${token}`)
                .send({ title: '新标题', content: '新内容' })
                .expect(200);

            expect(res.body.data.title).toBe('新标题');
        });

        it('更新不存在的文章应该返回 404', async () => {
            const res = await request(app)
                .put('/api/articles/99999')
                .set('Authorization', `Bearer ${token}`)
                .send({ title: '测试', content: '测试' })
                .expect(404);
        });
    });

    describe('DELETE /api/articles/:id', () => {
        it('应该成功删除自己的文章', async () => {
            const createRes = await request(app)
                .post('/api/articles')
                .set('Authorization', `Bearer ${token}`)
                .send({ title: '待删除', content: '待删除' });

            const id = createRes.body.data.id;

            await request(app)
                .delete(`/api/articles/${id}`)
                .set('Authorization', `Bearer ${token}`)
                .expect(204);
        });

        it('删除不存在的文章应该返回 404', async () => {
            const res = await request(app)
                .delete('/api/articles/99999')
                .set('Authorization', `Bearer ${token}`)
                .expect(404);
        });
    });

    describe('权限检查', () => {
        it('无 token 访问受保护接口应该返回 401', async () => {
            const res = await request(app)
                .post('/api/articles')
                .send({ title: '测试', content: '测试' })
                .expect(401);
        });

        it('无效 token 应该返回 401', async () => {
            const res = await request(app)
                .post('/api/articles')
                .set('Authorization', 'Bearer invalidtoken')
                .send({ title: '测试', content: '测试' })
                .expect(401);
        });

        it('跨用户修改文章应该返回 403', async () => {
            // 用户 A 创建文章
            const createRes = await request(app)
                .post('/api/articles')
                .set('Authorization', `Bearer ${token}`)
                .send({ title: 'A的文章', content: 'A的内容' });

            const id = createRes.body.data.id;

            // 注册用户 B
            await request(app)
                .post('/api/auth/register')
                .send({
                    username: 'userB',
                    email: 'userB@example.com',
                    password: 'test123456'
                });

            const loginBRes = await request(app)
                .post('/api/auth/login')
                .send({
                    email: 'userB@example.com',
                    password: 'test123456'
                });

            const tokenB = loginBRes.body.data.token;

            // 用户 B 尝试修改用户 A 的文章
            const res = await request(app)
                .put(`/api/articles/${id}`)
                .set('Authorization', `Bearer ${tokenB}`)
                .send({ title: 'B改了A的文章', content: '...' })
                .expect(403);
        });

        it('跨用户删除文章应该返回 403', async () => {
            const createRes = await request(app)
                .post('/api/articles')
                .set('Authorization', `Bearer ${token}`)
                .send({ title: 'A的文章', content: 'A的内容' });

            const id = createRes.body.data.id;

            await request(app)
                .post('/api/auth/register')
                .send({
                    username: 'userC',
                    email: 'userC@example.com',
                    password: 'test123456'
                });

            const loginCRes = await request(app)
                .post('/api/auth/login')
                .send({
                    email: 'userC@example.com',
                    password: 'test123456'
                });

            const tokenC = loginCRes.body.data.token;

            const res = await request(app)
                .delete(`/api/articles/${id}`)
                .set('Authorization', `Bearer ${tokenC}`)
                .expect(403);
        });
    });
});
```

</details>

---

## jest.config.js

> 截至第 26 章最终状态

<details>
<summary>展开代码</summary>

```javascript
module.exports = {
    testEnvironment: 'node',
    testMatch: ['**/tests/**/*.test.js'],
    setupFilesAfterSetup: [],
    verbose: true
};
```

</details>

---

## Dockerfile

> 截至第 29 章最终状态

<details>
<summary>展开代码</summary>

```dockerfile
# 使用 Node.js 18 Alpine 镜像（轻量）
FROM node:18-alpine

# 设置工作目录
WORKDIR /app

# 复制 package.json 和 package-lock.json
COPY package*.json ./

# 安装生产依赖
RUN npm ci --only=production

# 复制源代码
COPY . .

# 创建 uploads 目录
RUN mkdir -p uploads

# 暴露端口
EXPOSE 3000

# 启动应用
CMD ["node", "server.js"]
```

</details>

---

## docker-compose.yml

> 截至第 30 章最终状态

<details>
<summary>展开代码</summary>

```yaml
version: '3.8'

services:
  app:
    build: .
    container_name: blog-backend
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
      - PORT=3000
      - JWT_SECRET=${JWT_SECRET}
    volumes:
      - ./blog.db:/app/blog.db
      - ./uploads:/app/uploads
    restart: unless-stopped
```

</details>

---

## .dockerignore

> 截至第 29 章最终状态

<details>
<summary>展开代码</summary>

```
node_modules/
npm-debug.log
.git
.gitignore
.env
test.db
tests/
```

</details>

---

## ecosystem.config.js

> 截至第 27 章最终状态

<details>
<summary>展开代码</summary>

```javascript
module.exports = {
    apps: [
        {
            name: 'blog-backend',
            script: './server.js',
            instances: 2,
            exec_mode: 'cluster',
            env: {
                NODE_ENV: 'production',
                PORT: 3000
            },
            env_file: '.env',
            log_date_format: 'YYYY-MM-DD HH:mm:ss',
            max_memory_restart: '500M'
        }
    ]
};
```

</details>

---

> **更新记录**：2026-06-12 初始版本，收录 24 个文件，覆盖 blog-backend 项目全部代码。