# 附录C：Express 常用模式速查

> 本附录汇总教程中出现的所有 Express 代码模式，每个模式给出可直接复制使用的完整代码块。所有模式基于 Express 4.x + Node.js 18+。

---

## 1. 创建 Express 应用

```javascript
const express = require('express');
const app = express();

// 中间件和路由配置...

// 导出 app（供测试使用）
module.exports = app;

// 只在直接运行时启动服务器
if (require.main === module) {
    const PORT = process.env.PORT || 3000;
    app.listen(PORT, () => {
        console.log(`Server is running on http://localhost:${PORT}`);
    });
}
```

> 对应章节：02, 26

---

## 2. 定义路由（GET / POST / PUT / DELETE）

```javascript
const express = require('express');
const router = express.Router();

// GET — 获取资源列表
router.get('/', (req, res) => {
    res.json({ success: true, data: { items: [] } });
});

// GET — 获取单个资源
router.get('/:id', (req, res) => {
    const { id } = req.params;
    // 查找资源...
    res.json({ success: true, data: { id } });
});

// POST — 创建资源
router.post('/', (req, res) => {
    const { title, content } = req.body;
    // 创建资源...
    res.status(201).json({ success: true, data: { title, content } });
});

// PUT — 更新资源
router.put('/:id', (req, res) => {
    const { id } = req.params;
    const { title, content } = req.body;
    // 更新资源...
    res.json({ success: true, data: { id, title, content } });
});

// DELETE — 删除资源
router.delete('/:id', (req, res) => {
    const { id } = req.params;
    // 删除资源...
    res.status(204).send();
});

module.exports = router;
```

> 对应章节：05, 09

---

## 3. 路径参数和查询参数

```javascript
// 路径参数 — 通过 req.params 获取
// GET /api/articles/42
router.get('/:id', (req, res) => {
    const articleId = req.params.id;  // "42"
    // ...
});

// 查询参数 — 通过 req.query 获取
// GET /api/articles?page=2&limit=10&search=Node
router.get('/', (req, res) => {
    const page = parseInt(req.query.page) || 1;
    const limit = parseInt(req.query.limit) || 10;
    const search = req.query.search || '';
    // ...
});
```

> 对应章节：06, 22, 23

---

## 4. 路由分组（express.Router）

```javascript
// server.js — 主入口
const express = require('express');
const app = express();

const articlesRouter = require('./routes/articles');
const authRouter = require('./routes/auth');
const commentsRouter = require('./routes/comments');
const uploadRouter = require('./routes/upload');

app.use('/api/articles', articlesRouter);
app.use('/api/auth', authRouter);
app.use('/api', commentsRouter);        // 注意：评论路由嵌套在文章路由下
app.use('/api', uploadRouter);

// routes/articles.js — 路由文件
const express = require('express');
const router = express.Router();

router.get('/', (req, res) => { /* ... */ });
router.get('/:id', (req, res) => { /* ... */ });
router.post('/', (req, res) => { /* ... */ });

module.exports = router;
```

> 对应章节：05, 15

---

## 5. 中间件模式

### 5.1 全局中间件（对所有请求生效）

```javascript
// 内置中间件
app.use(express.json());       // 解析 JSON 请求体
app.use(express.urlencoded({ extended: true }));  // 解析 URL 编码请求体

// 第三方中间件
app.use(require('morgan')('dev'));    // HTTP 请求日志
app.use(require('cors')());           // 跨域支持

// 自定义中间件
app.use((req, res, next) => {
    console.log(`${req.method} ${req.url}`);
    next();
});
```

> 对应章节：06, 07

### 5.2 路由级中间件（只对特定路由生效）

```javascript
const { authenticate } = require('../middleware/auth');

// 单个路由
router.post('/', authenticate, (req, res) => {
    // 只有认证通过的用户才能执行到这里
});

router.put('/:id', authenticate, (req, res) => {
    // ...
});

router.delete('/:id', authenticate, (req, res) => {
    // ...
});
```

> 对应章节：19

### 5.3 自定义中间件文件

```javascript
// middleware/logger.js
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

```javascript
// middleware/auth.js
const jwt = require('jsonwebtoken');
const AppError = require('../utils/AppError');

function authenticate(req, res, next) {
    const authHeader = req.headers.authorization;
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
        throw new AppError('未提供认证令牌', 401);
    }

    const token = authHeader.split(' ')[1];
    try {
        const decoded = jwt.verify(token, process.env.JWT_SECRET);
        req.user = decoded;
        next();
    } catch (err) {
        if (err.name === 'TokenExpiredError') {
            throw new AppError('认证令牌已过期，请重新登录', 401);
        }
        throw new AppError('认证令牌无效', 401);
    }
}

module.exports = { authenticate };
```

> 对应章节：06, 19

---

## 6. 解析 JSON 请求体

```javascript
// server.js 中，在路由之前
app.use(express.json());

// 路由中即可通过 req.body 获取数据
router.post('/', (req, res) => {
    const { title, content } = req.body;  // req.body 是解析后的对象
    // ...
});
```

> 对应章节：07

---

## 7. 静态文件服务

```javascript
const path = require('path');

// 让浏览器能直接访问 uploads/ 目录中的文件
// GET /uploads/abc123.jpg → 返回文件内容
app.use('/uploads', express.static(path.join(__dirname, 'uploads')));
```

> 对应章节：24

---

## 8. 统一响应格式

```javascript
// 成功响应
res.json({
    success: true,
    data: {
        // 业务数据...
    }
});

// 创建成功（201）
res.status(201).json({
    success: true,
    data: {
        // 新创建的资源...
    }
});

// 删除成功（204，无响应体）
res.status(204).send();

// 错误响应（通过 AppError + 全局错误处理中间件自动生成）
// { success: false, error: { message: '...', code: '...' } }
```

> 对应章节：08

---

## 9. 自定义错误类

```javascript
// utils/AppError.js
class AppError extends Error {
    /**
     * @param {string} message — 错误信息
     * @param {number} statusCode — HTTP 状态码
     */
    constructor(message, statusCode) {
        super(message);
        this.statusCode = statusCode;
        this.isOperational = true;  // 标记为可预期的错误
        Error.captureStackTrace(this, this.constructor);
    }
}

module.exports = AppError;
```

使用方式：

```javascript
const AppError = require('../utils/AppError');

// 在路由中抛出
throw new AppError('文章不存在', 404);
throw new AppError('用户名已被注册', 409);
throw new AppError('未提供认证令牌', 401);
```

> 对应章节：08

---

## 10. 404 兜底

```javascript
// 放在所有路由之后，错误处理中间件之前
app.use((req, res) => {
    res.status(404).json({
        success: false,
        error: {
            message: `接口不存在：${req.method} ${req.originalUrl}`,
            code: 'NOT_FOUND'
        }
    });
});
```

> 对应章节：08

---

## 11. 全局错误处理中间件

```javascript
// middleware/errorHandler.js
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

挂载（放在所有路由和 404 兜底之后）：

```javascript
app.use(errorHandler);
```

> 对应章节：08

---

## 12. CORS 配置

```javascript
const cors = require('cors');

// 简单配置：允许所有来源
app.use(cors());

// 详细配置：只允许特定来源
app.use(cors({
    origin: ['http://localhost:5173', 'https://your-frontend.com'],
    methods: ['GET', 'POST', 'PUT', 'DELETE'],
    allowedHeaders: ['Content-Type', 'Authorization'],
    credentials: true
}));
```

> 对应章节：06

---

## 13. multer 文件上传

### 13.1 配置 multer

```javascript
// middleware/upload.js
const multer = require('multer');
const path = require('path');
const crypto = require('crypto');

const storage = multer.diskStorage({
    destination: function (req, file, cb) {
        cb(null, 'uploads/');
    },
    filename: function (req, file, cb) {
        const uniqueSuffix = Date.now() + '-' + crypto.randomUUID();
        const ext = path.extname(file.originalname);
        cb(null, uniqueSuffix + ext);
    }
});

const fileFilter = (req, file, cb) => {
    const allowedTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp'];
    if (allowedTypes.includes(file.mimetype)) {
        cb(null, true);
    } else {
        cb(new Error('只允许上传 JPG、PNG、GIF、WebP 格式的图片'), false);
    }
};

const upload = multer({
    storage: storage,
    fileFilter: fileFilter,
    limits: {
        fileSize: 5 * 1024 * 1024  // 5MB
    }
});

module.exports = upload;
```

### 13.2 上传接口

```javascript
// routes/upload.js
const express = require('express');
const router = express.Router();
const upload = require('../middleware/upload');
const { authenticate } = require('../middleware/auth');
const AppError = require('../utils/AppError');

router.post('/upload', authenticate, (req, res, next) => {
    upload.single('image')(req, res, function (err) {
        if (err) {
            if (err.code === 'LIMIT_FILE_SIZE') {
                return next(new AppError('文件大小不能超过 5MB', 413));
            }
            if (err.message.includes('只允许上传')) {
                return next(new AppError(err.message, 400));
            }
            return next(new AppError('文件上传失败', 500));
        }

        if (!req.file) {
            return next(new AppError('请选择要上传的图片', 400));
        }

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

> 对应章节：24

---

## 14. JWT 认证中间件

```javascript
// middleware/auth.js
const jwt = require('jsonwebtoken');
const AppError = require('../utils/AppError');

function authenticate(req, res, next) {
    const authHeader = req.headers.authorization;

    if (!authHeader || !authHeader.startsWith('Bearer ')) {
        throw new AppError('未提供认证令牌', 401);
    }

    const token = authHeader.split(' ')[1];

    try {
        const decoded = jwt.verify(token, process.env.JWT_SECRET);
        req.user = decoded;  // { userId, username, iat, exp }
        next();
    } catch (err) {
        if (err.name === 'TokenExpiredError') {
            throw new AppError('认证令牌已过期，请重新登录', 401);
        }
        throw new AppError('认证令牌无效', 401);
    }
}

module.exports = { authenticate };
```

使用：

```javascript
const { authenticate } = require('../middleware/auth');

// 保护单个路由
router.post('/', authenticate, (req, res) => {
    const authorId = req.user.userId;  // 从 JWT 获取当前用户
    // ...
});
```

> 对应章节：19

---

## 15. 完整 server.js 骨架

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

// 导出 & 启动
module.exports = app;

if (require.main === module) {
    app.listen(PORT, () => {
        console.log(`Server is running on http://localhost:${PORT}`);
    });
}
```

> 对应章节：08, 15, 26

---

> **更新记录**：2026-06-12 初始版本，覆盖教程第 02-26 章所有 Express 代码模式。