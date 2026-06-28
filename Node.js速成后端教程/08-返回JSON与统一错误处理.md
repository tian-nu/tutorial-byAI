# 08-返回JSON与统一错误处理

> "前端同学最怕的就是'接口返回格式不统一'——有的接口返回 `{ data: ... }`，有的返回 `{ result: ... }`，错误时有的返回字符串，有的返回 HTML。这一章我们制定统一的响应格式，创建自定义错误类，让每一个接口的返回都有章可循。"

---

## 一、目标与完成效果

**一句话目标**：制定统一的 JSON 响应格式（成功 `{ success: true, data: ... }`，失败 `{ success: false, error: { message, code } }`），创建 `AppError` 自定义错误类，升级全局错误处理中间件，添加 404 兜底路由，让整个项目的 API 响应风格统一。

**完成后的可观测效果**：
- 所有成功接口返回 `{ success: true, data: ... }` 格式。
- 所有错误接口返回 `{ success: false, error: { message: '...', code: '...' } }` 格式。
- 你创建了 `utils/AppError.js`，可以在路由中用 `throw new AppError('文章不存在', 404)` 抛出自定义错误。
- 404 兜底路由返回统一的 JSON 格式，而不是 Express 默认的 HTML 页面。
- 错误处理中间件能区分开发环境和生产环境，生产环境不暴露 `err.stack`。

---

## 二、前置条件

| 序号 | 条件 | 验证命令 |
|------|------|----------|
| 1 | 已完成教程 07，`express.json()` 已配置，Echo 接口可用 | `npm run dev` 正常启动 |
| 2 | `middleware/errorHandler.js` 已创建并挂载 | `ls middleware/errorHandler.js` 文件存在 |
| 3 | 理解 `try/catch` 和 `throw` 的基本概念 | 能看懂 `try { throw new Error('xxx') } catch (err) { ... }` |

**一条命令确认前置满足**：

```bash
npm run dev
```

终端输出 "Server is running on http://localhost:3000"，前置条件满足。

---

## 三、分步操作

### 步骤 1：为什么需要统一响应格式——"前端同学不用猜你返回的结构"

先看看你现在的接口返回格式：

| 接口 | 返回格式 |
|------|----------|
| `GET /api/articles` | `{ page, limit, total, data: [...] }` |
| `GET /api/articles/:id` | `{ id, title, author }`（直接返回文章对象） |
| `GET /api/articles/me` | `{ message: '...' }` |
| `POST /api/auth/register` | `{ message: '...', user: {...} }` |
| 404 错误 | `{ error: '文章不存在' }` |

**问题很明显**：
- 有的返回格式有 `data` 包裹，有的直接返回对象。
- 成功时没有统一的"成功标识"。
- 错误时只有 `error` 字段，没有标识这是"失败"响应。

**前端同学拿到这些响应后，需要针对每个接口写不同的解析逻辑。** 如果前端同学说："能不能统一一下？"——这就是我们要解决的问题。

**统一之后的格式**：

```json
// 成功
{ "success": true, "data": { ... } }

// 失败
{ "success": false, "error": { "message": "文章不存在", "code": "NOT_FOUND" } }
```

**好处**：
- 前端只需要检查 `success` 字段，就能判断请求是否成功。
- 成功时，`data` 里一定有数据。
- 失败时，`error` 里一定有 `message` 和 `code`，可以做精确的错误提示。

---

### 步骤 2：成功响应格式——`{ success: true, data: ... }`

规定：所有成功的 API 响应，包裹在 `{ success: true, data: ... }` 中。

#### 2.1 修改 `routes/articles.js`

把原来的直接返回改成统一格式：

```javascript
// GET /api/articles — 获取所有文章（支持分页）
router.get('/', (req, res) => {
    const page = parseInt(req.query.page) || 1;
    const limit = parseInt(req.query.limit) || 10;

    const startIndex = (page - 1) * limit;
    const endIndex = startIndex + limit;

    const paginatedArticles = articles.slice(startIndex, endIndex);

    res.json({
        success: true,
        data: {
            page: page,
            limit: limit,
            total: articles.length,
            articles: paginatedArticles
        }
    });
});

// GET /api/articles/:id — 获取单篇文章
router.get('/:id', (req, res) => {
    const article = articles.find(a => a.id === parseInt(req.params.id));
    if (!article) {
        return res.status(404).json({
            success: false,
            error: {
                message: '文章不存在',
                code: 'ARTICLE_NOT_FOUND'
            }
        });
    }
    res.json({
        success: true,
        data: article
    });
});
```

#### 2.2 修改 `routes/auth.js`

```javascript
// 用户注册
router.post('/register', (req, res) => {
    res.status(201).json({
        success: true,
        data: {
            message: '注册成功',
            user: { id: 1, username: 'newuser' }
        }
    });
});

// 用户登录
router.post('/login', (req, res) => {
    res.json({
        success: true,
        data: {
            message: '登录成功',
            token: 'fake-jwt-token-xxxxx'
        }
    });
});
```

> `auth.js` 中的接口第 09 章会重写为真正的逻辑，现在先统一格式。

---

### 步骤 3：失败响应格式——`{ success: false, error: { message, code } }`

规定：所有失败的 API 响应，包裹在 `{ success: false, error: { message, code } }` 中。

| 字段 | 类型 | 说明 | 示例 |
|------|------|------|------|
| `success` | boolean | 固定 `false` | `false` |
| `error.message` | string | 人类可读的错误描述 | `"文章不存在"` |
| `error.code` | string | 机器可读的错误码（便于前端做精确判断） | `"ARTICLE_NOT_FOUND"` |

**错误码命名规范**：大写字母 + 下划线，如 `ARTICLE_NOT_FOUND`、`VALIDATION_ERROR`、`UNAUTHORIZED`。

> `error.code` 的好处：前端可以根据 `code` 做精确的错误处理——比如 `code === 'UNAUTHORIZED'` 时跳转登录页，`code === 'ARTICLE_NOT_FOUND'` 时显示 404 页面。而不是靠解析 `message` 字符串（中文、英文、多语言？非常不可靠）。

---

### 步骤 4：创建自定义错误类 `AppError`

如果每次返回错误都要手动写 `res.status(404).json({ success: false, error: { message: '...', code: '...' } })`，代码会很冗长。我们需要一个更优雅的方式——**抛出一个错误，让全局错误处理中间件统一处理**。

#### 4.1 创建 `utils/AppError.js`

在 `blog-backend/` 下创建 `utils/` 文件夹，然后在里面新建 `AppError.js`：

```javascript
// utils/AppError.js — 自定义错误类
class AppError extends Error {
    constructor(message, statusCode) {
        super(message);            // 调用父类 Error 的构造函数
        this.statusCode = statusCode; // HTTP 状态码，如 404、400、500
        this.isOperational = true;    // 标记为"可预期的错误"（而非程序 bug）

        // 捕获堆栈信息，但排除构造函数本身
        Error.captureStackTrace(this, this.constructor);
    }
}

module.exports = AppError;
```

#### 逐行解释

```javascript
class AppError extends Error {
```

`AppError` 继承自 JavaScript 内置的 `Error` 类。这意味着 `AppError` 是一个"加强版"的错误——除了 `message`，还带了 `statusCode` 和 `isOperational`。

```javascript
super(message);
```

调用父类（`Error`）的构造函数，设置 `this.message = message`。这是必需的，否则 `err.message` 会是空的。

```javascript
this.isOperational = true;
```

**区分"预期错误"和"程序 bug"**：
- `isOperational = true`：预期内的错误（如文章不存在、参数校验失败）——返回对应的 HTTP 状态码。
- `isOperational = false`：程序 bug（如 `undefined.something`）——返回 500。

这个标记在第 8.5 节错误处理中间件中会用到。

```javascript
Error.captureStackTrace(this, this.constructor);
```

捕获调用栈（stack trace），但排除 `AppError` 构造函数本身——这样错误堆栈的第一行会直接指向你 `throw new AppError(...)` 的地方，而不是指向 `AppError.js` 内部。

#### 4.2 使用 AppError

在路由中，原来你要写：

```javascript
// ❌ 旧方式——冗长
if (!article) {
    return res.status(404).json({
        success: false,
        error: { message: '文章不存在', code: 'ARTICLE_NOT_FOUND' }
    });
}
```

现在可以简化为：

```javascript
// ✅ 新方式——简洁
const AppError = require('../utils/AppError');

if (!article) {
    throw new AppError('文章不存在', 404);
}
```

> 注意：`throw` 后面不需要 `return`——`throw` 会中断当前函数执行，把控制权交给错误处理中间件。

---

### 步骤 5：升级全局错误处理中间件

现在 `AppError` 抛出的错误会到达 `middleware/errorHandler.js`。我们需要升级它，让它能正确处理 `AppError`。

#### 5.1 重写 `middleware/errorHandler.js`

```javascript
// middleware/errorHandler.js — 全局错误处理中间件（升级版）
const AppError = require('../utils/AppError');

function errorHandler(err, req, res, next) {
    // 打印错误到控制台（方便调试）
    console.error('❌ 错误:', err.message);
    if (process.env.NODE_ENV === 'development') {
        console.error(err.stack);
    }

    // 默认值
    let statusCode = 500;
    let message = '服务器内部错误';
    let errorCode = 'INTERNAL_ERROR';

    // 如果是 AppError（已知错误），使用它携带的状态码和消息
    if (err instanceof AppError) {
        statusCode = err.statusCode;
        message = err.message;
        // 根据状态码生成错误码
        errorCode = getErrorCode(statusCode);
    }

    // 返回统一格式的错误响应
    res.status(statusCode).json({
        success: false,
        error: {
            message: message,
            code: errorCode,
            // 开发环境返回错误堆栈，生产环境不返回
            ...(process.env.NODE_ENV === 'development' && { stack: err.stack.split('\n') })
        }
    });
}

// 根据 HTTP 状态码生成对应的错误码
function getErrorCode(statusCode) {
    const codeMap = {
        400: 'BAD_REQUEST',
        401: 'UNAUTHORIZED',
        403: 'FORBIDDEN',
        404: 'NOT_FOUND',
        409: 'CONFLICT',
        422: 'VALIDATION_ERROR',
        429: 'TOO_MANY_REQUESTS',
        500: 'INTERNAL_ERROR'
    };
    return codeMap[statusCode] || 'INTERNAL_ERROR';
}

module.exports = errorHandler;
```

#### 逐行解释

```javascript
if (err instanceof AppError) {
```

`instanceof` 检查错误是否是 `AppError` 的实例。如果是，说明这是"已知错误"，使用它携带的状态码和消息；如果不是，说明是"未知错误"（程序 bug），返回 500。

```javascript
...(process.env.NODE_ENV === 'development' && { stack: err.stack.split('\n') })
```

`err.stack.split('\n')` 把堆栈字符串按行分割成数组，方便前端展示。`process.env.NODE_ENV` 是 Node.js 的环境变量——开发时通常是 `'development'`，生产部署时是 `'production'`。

> 🔥 **魔鬼细节**：生产环境**绝对不要返回 `err.stack`**。堆栈信息包含了你的服务器文件路径、代码行号、甚至可能泄露敏感信息。攻击者可以通过堆栈信息推断你的项目结构和依赖版本。

#### 5.2 在路由中使用 AppError

修改 `routes/articles.js` 的 `GET /:id` 路由：

```javascript
const AppError = require('../utils/AppError');

// GET /api/articles/:id — 获取单篇文章
router.get('/:id', (req, res) => {
    const article = articles.find(a => a.id === parseInt(req.params.id));
    if (!article) {
        throw new AppError('文章不存在', 404);
    }
    res.json({
        success: true,
        data: article
    });
});
```

> 注意：这里用 `throw` 而不是 `return res.status(404).json(...)`。`throw` 会中断当前函数，Express 会自动把错误传给全局错误处理中间件。

---

### 步骤 6：404 兜底路由

当用户访问一个不存在的接口时，Express 默认返回的是 HTML 格式的 `Cannot GET /xxx`。对于 API 来说，应该返回统一的 JSON 格式。

在 `server.js` 中，在所有路由**之后**、错误处理中间件**之前**，添加：

```javascript
// ========== 404 兜底路由（所有未匹配的路由都会到这里） ==========
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

> 🔥 **位置极其重要**：404 兜底路由必须放在所有正常路由**之后**、错误处理中间件**之前**。因为它是靠"前面的路由都没匹配，才落到这里"来工作的。如果放在路由之前，所有请求都会返回 404。

#### 验证

用 Thunder Client 发 `GET http://localhost:3000/api/xyz`。你应该看到：

```json
{
    "success": false,
    "error": {
        "message": "接口不存在：GET /api/xyz",
        "code": "NOT_FOUND"
    }
}
```

而不是 Express 默认的 `Cannot GET /api/xyz` 纯文本。

---

### 步骤 7：在路由中使用错误处理——完整示例

现在我们有了完整的错误处理体系。在路由中，你应该这样写：

```javascript
// ✅ 推荐写法——用 throw + AppError
router.get('/:id', (req, res) => {
    const article = articles.find(a => a.id === parseInt(req.params.id));
    if (!article) {
        throw new AppError('文章不存在', 404);
    }
    res.json({ success: true, data: article });
});
```

```javascript
// ✅ 也可以——用 return（适合在中间件中提前返回）
router.get('/:id', (req, res) => {
    const article = articles.find(a => a.id === parseInt(req.params.id));
    if (!article) {
        return res.status(404).json({
            success: false,
            error: { message: '文章不存在', code: 'NOT_FOUND' }
        });
    }
    res.json({ success: true, data: article });
});
```

两种方式都可以。`throw new AppError(...)` 更简洁，`return res.status(...).json(...)` 更直观。**本教程推荐用 `throw new AppError(...)`**——因为它把错误处理逻辑集中到了错误处理中间件里，路由代码更干净。

---

### 🤔 想多一点：async 路由中的错误处理——Express 5 之前的坑

**一个重要的坑**：如果你在路由中使用了 `async` 函数（比如后面连接数据库时），Express 4 默认**不会捕获 async 函数中抛出的错误**。

```javascript
// ❌ Express 4 中，这个错误不会被 errorHandler 捕获！
router.get('/:id', async (req, res) => {
    const article = await someAsyncOperation();
    // 如果这里 throw，Express 4 不会捕获，请求会一直挂起直到超时
    throw new AppError('文章不存在', 404);
});
```

**解决方案（二选一）**：

**方案一**：手动 `try/catch` + `next(err)`：

```javascript
router.get('/:id', async (req, res, next) => {
    try {
        const article = await someAsyncOperation();
        if (!article) {
            throw new AppError('文章不存在', 404);
        }
        res.json({ success: true, data: article });
    } catch (err) {
        next(err); // 手动传给错误处理中间件
    }
});
```

**方案二**：安装 `express-async-errors` 包（推荐）：

```bash
npm install express-async-errors
```

然后在 `server.js` 最顶部引入：

```javascript
require('express-async-errors');
// 然后才是
const express = require('express');
```

> `express-async-errors` 会自动给所有 async 路由处理函数加上错误捕获，你不需要手动 `try/catch`。**本教程后续章节会采用方案二。** 现在你的路由都是同步的，暂时不需要担心这个问题。

---

### ❌ 常见错误 → ✅ 解决方案

| 错误信息 / 现象 | 原因 | 解决 |
|-----------------|------|------|
| 404 兜底路由不生效 | 放在了正常路由**前面** | 把 404 兜底路由移到所有路由的**最后面** |
| `throw new AppError(...)` 后返回 HTML 错误页 | 错误处理中间件没有正确挂载或参数个数不对 | 检查 `errorHandler` 是否四个参数，且 `app.use(errorHandler)` 放在最后 |
| `err instanceof AppError` 永远是 `false` | `require` 路径错误，导致 `AppError` 不是同一个类 | 确保 `require('../utils/AppError')` 路径正确，且只在一处 `require` |
| 生产环境返回了 `err.stack` | 没有判断 `NODE_ENV` | 在错误处理中间件中加 `process.env.NODE_ENV === 'development'` 判断 |
| `AppError` 没有 `isOperational` 属性 | 忘记在构造函数中设置 | 在 `AppError` 的 `constructor` 中加 `this.isOperational = true` |

---

## 四、完整代码清单

### `blog-backend/utils/AppError.js`（本章新建）

```javascript
// utils/AppError.js — 自定义错误类
class AppError extends Error {
    constructor(message, statusCode) {
        super(message);
        this.statusCode = statusCode;
        this.isOperational = true;
        Error.captureStackTrace(this, this.constructor);
    }
}

module.exports = AppError;
```

### `blog-backend/middleware/errorHandler.js`（本章升级）

```javascript
// middleware/errorHandler.js — 全局错误处理中间件（升级版）
const AppError = require('../utils/AppError');

function errorHandler(err, req, res, next) {
    console.error('❌ 错误:', err.message);
    if (process.env.NODE_ENV === 'development') {
        console.error(err.stack);
    }

    let statusCode = 500;
    let message = '服务器内部错误';
    let errorCode = 'INTERNAL_ERROR';

    if (err instanceof AppError) {
        statusCode = err.statusCode;
        message = err.message;
        errorCode = getErrorCode(statusCode);
    }

    res.status(statusCode).json({
        success: false,
        error: {
            message: message,
            code: errorCode,
            ...(process.env.NODE_ENV === 'development' && { stack: err.stack.split('\n') })
        }
    });
}

function getErrorCode(statusCode) {
    const codeMap = {
        400: 'BAD_REQUEST',
        401: 'UNAUTHORIZED',
        403: 'FORBIDDEN',
        404: 'NOT_FOUND',
        409: 'CONFLICT',
        422: 'VALIDATION_ERROR',
        429: 'TOO_MANY_REQUESTS',
        500: 'INTERNAL_ERROR'
    };
    return codeMap[statusCode] || 'INTERNAL_ERROR';
}

module.exports = errorHandler;
```

### `blog-backend/routes/articles.js`（本章升级——统一格式）

```javascript
const express = require('express');
const router = express.Router();
const AppError = require('../utils/AppError');

// 模拟文章数据
const articles = [
    { id: 1, title: 'Node.js 入门指南', author: '小明' },
    { id: 2, title: 'Express 框架详解', author: '小红' },
    { id: 3, title: 'RESTful API 设计', author: '小刚' }
];

// GET /api/articles — 获取所有文章（支持分页）
router.get('/', (req, res) => {
    const page = parseInt(req.query.page) || 1;
    const limit = parseInt(req.query.limit) || 10;

    const startIndex = (page - 1) * limit;
    const endIndex = startIndex + limit;

    const paginatedArticles = articles.slice(startIndex, endIndex);

    res.json({
        success: true,
        data: {
            page: page,
            limit: limit,
            total: articles.length,
            articles: paginatedArticles
        }
    });
});

// GET /api/articles/me — 固定路径必须放在动态路径前面
router.get('/me', (req, res) => {
    res.json({
        success: true,
        data: { message: '这是我的文章列表' }
    });
});

// GET /api/articles/:id — 获取单篇文章
router.get('/:id', (req, res) => {
    const article = articles.find(a => a.id === parseInt(req.params.id));
    if (!article) {
        throw new AppError('文章不存在', 404);
    }
    res.json({
        success: true,
        data: article
    });
});

module.exports = router;
```

### `blog-backend/routes/auth.js`（本章升级——统一格式）

```javascript
const express = require('express');
const router = express.Router();

// 用户注册
router.post('/register', (req, res) => {
    res.status(201).json({
        success: true,
        data: {
            message: '注册成功',
            user: { id: 1, username: 'newuser' }
        }
    });
});

// 用户登录
router.post('/login', (req, res) => {
    res.json({
        success: true,
        data: {
            message: '登录成功',
            token: 'fake-jwt-token-xxxxx'
        }
    });
});

module.exports = router;
```

### `blog-backend/server.js` 新增的 404 兜底路由（在 `app.use(errorHandler)` 之前添加）

```javascript
// ... 所有路由定义 ...

// ========== 404 兜底路由（所有未匹配的路由都会到这里） ==========
app.use((req, res) => {
    res.status(404).json({
        success: false,
        error: {
            message: `接口不存在：${req.method} ${req.originalUrl}`,
            code: 'NOT_FOUND'
        }
    });
});

// ========== 错误处理中间件（必须放在最后） ==========
app.use(errorHandler);

app.listen(3000, () => {
    console.log('Server is running on http://localhost:3000');
});
```

### `blog-backend/` 目录结构（本章最终状态）

```
blog-backend/
├── server.js
├── package.json
├── package-lock.json
├── .gitignore
├── node_modules/
├── routes/
│   ├── articles.js
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
| 1 | `npm run dev` | 服务器正常启动 |
| 2 | `GET /api/articles` | 返回 `{ success: true, data: { page:1, limit:10, total:3, articles:[...] } }` |
| 3 | `GET /api/articles/1` | 返回 `{ success: true, data: { id:1, title:..., author:... } }` |
| 4 | `GET /api/articles/999` | 返回 404，`{ success: false, error: { message: "文章不存在", code: "NOT_FOUND" } }` |
| 5 | `GET /api/xyz`（不存在的路径） | 返回 404，`{ success: false, error: { message: "接口不存在：GET /api/xyz", code: "NOT_FOUND" } }` |
| 6 | `POST /api/auth/register` | 返回 201，`{ success: true, data: { message: "注册成功", ... } }` |
| 7 | 在 `server.js` 中临时添加 `throw new Error('测试')`，访问 | 返回 500，`{ success: false, error: { message: "服务器内部错误", code: "INTERNAL_ERROR" } }` |

全部通过？你的 API 响应格式已经统一，前端同学会感谢你的。

---

## 六、小结表格

| 学到的东西 | 一句话解释 |
|-----------|-----------|
| 统一响应格式 | 成功：`{ success: true, data: ... }`；失败：`{ success: false, error: { message, code } }` |
| `AppError` 自定义错误类 | 继承 `Error`，携带 `statusCode` 和 `message`，在路由中 `throw new AppError('...', 404)` |
| 全局错误处理中间件 | 四个参数 `(err, req, res, next)`，捕获所有错误，根据 `AppError` 或未知错误返回不同状态码 |
| 404 兜底路由 | 放在所有路由**之后**，返回统一 JSON 格式的 404 错误 |
| `NODE_ENV` 环境变量 | 开发环境返回 `err.stack` 方便调试，生产环境不返回防止泄露信息 |
| `err.stack` | 错误堆栈信息，包含文件路径和行号，**生产环境绝不能暴露** |
| async 路由错误处理 | Express 4 不自动捕获 async 错误，需要 `try/catch` 或 `express-async-errors` 包 |

---

## 七、术语附录

| 术语 | 英文 | 通俗解释 | 本章出现位置 | 字面陷阱 |
|------|------|----------|-------------|----------|
| 统一响应格式 | Unified Response Format | 所有 API 接口返回相同结构的数据——成功用 `{ success, data }`，失败用 `{ success, error }`。 | 步骤 1 | 不是"统一格式"= 所有接口返回相同内容——而是**结构相同**，内容不同。 |
| `AppError` | Application Error | 自定义错误类，继承自 JavaScript 的 `Error`。携带 HTTP 状态码和错误消息，用于区分"预期错误"和"程序 bug"。 | 步骤 4 | 不是 `App` 的"应用"——这里的 `App` 是 Application 的缩写，表示"应用层面的错误"。 |
| 全局错误处理（Global Error Handler） | Global Error Handler | 一个放在所有路由之后的中间件，捕获所有未处理的错误，统一返回 JSON 格式的错误响应。 | 步骤 5 | 不是"全局"= 所有错误都能处理——它只能捕获**同步**抛出的错误，async 错误需要额外处理。 |
| 404 兜底（Catch-all 404） | Catch-all 404 Route | 放在所有路由之后的中间件，匹配所有未被前面路由匹配的请求，返回 404。 | 步骤 6 | 不是"404 兜底"= 解决所有 404 问题——它只是兜住"接口不存在"的情况，你的业务逻辑中还有"资源不存在"的 404。 |
| `NODE_ENV` | Node Environment | Node.js 的环境变量，标识当前运行环境。常用值：`development`（开发）、`production`（生产）、`test`（测试）。 | 步骤 5 | 不是"Node 的 ENV"——是 `NODE_ENV`，大小写敏感，必须全大写。 |
| `err.stack` | Error Stack Trace | 错误对象的堆栈跟踪信息，记录了错误发生时的函数调用链，包含文件路径和行号。 | 步骤 5 | 不是"错误堆"——是"调用栈"（Call Stack），从错误发生位置一直追溯到最初的调用者。 |

---

## 八、已知坑点与禁止事项

1. **404 兜底路由必须放在所有正常路由之后**：如果放在前面，所有请求都会返回 404。它依赖"前面的路由都没匹配"来工作。

2. **生产环境不要返回 `err.stack`**：堆栈信息包含文件路径和行号，可能泄露服务器架构信息。用 `process.env.NODE_ENV` 判断环境。

3. **Express 4 不自动捕获 async 路由中的错误**：如果你在路由中用了 `async`，必须手动 `try/catch` 并 `next(err)`，或者安装 `express-async-errors`。

4. **`AppError` 的 `require` 路径要一致**：如果 `errorHandler.js` 和 `routes/articles.js` 中 `require` 的 `AppError` 路径指向了不同的文件，`instanceof` 检查会失败。确保只在一个地方创建 `AppError`，其他地方都是用 `require` 引入。

5. **不要混用 `throw` 和 `return` 两种错误处理方式**：在一个项目中统一用一种方式。本教程推荐 `throw new AppError(...)` + 全局错误处理中间件。

6. **`error.code` 错误码要保持一致**：不要有的地方用 `"NOT_FOUND"`，有的地方用 `"ARTICLE_NOT_FOUND"`。统一用 HTTP 状态码对应的错误码（如 `getErrorCode` 函数的映射），或者单独定义语义化错误码。

---

## 九、下一步建议

统一响应格式、错误处理体系已经就绪。接下来，终于到了实战环节——用这些知识完成第一个完整的接口：

- **下一章**：[09-第一个接口实战：博客文章CRUD内存版](09-第一个接口实战：博客文章CRUD内存版.md)——完整实现文章的创建、读取、更新、删除，用 Thunder Client 测试所有接口，用 UUID 生成 ID，了解内存存储的致命缺陷。
- **延伸思考**：你现在的 `AppError` 只有 `statusCode` 和 `message`。后面可以扩展它——加上 `errorCode`（语义化错误码）、`details`（详细错误信息，如哪个字段校验失败），让错误信息更丰富。

---

> 📊 本教程无可视化
>
> 本教程编辑记录：2026-06-12 初始版本。