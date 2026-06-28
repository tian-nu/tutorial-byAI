# 09-第一个接口实战：博客文章 CRUD 内存版

> "终于到了实战环节！这一章我们把前面学到的所有知识——路由、中间件、请求解析、统一响应格式、错误处理——全部用上，完成一个完整的博客文章 CRUD 接口。创建、读取、更新、删除，一个不落。同时，你也会亲身体会'内存存储'的致命缺陷——为下一阶段数据库做好铺垫。"

---

## 一、目标与完成效果

**一句话目标**：完整实现博客文章的 CRUD（Create/Read/Update/Delete）接口，用数组存储数据，用 `crypto.randomUUID()` 生成 ID，所有接口返回统一的 JSON 格式，并用 Thunder Client 逐一验证。

**完成后的可观测效果**：
- `GET /api/articles` — 返回所有文章（统一格式）。
- `GET /api/articles/:id` — 返回单篇文章，不存在返回 404。
- `POST /api/articles` — 创建新文章，返回 201，必填字段校验。
- `PUT /api/articles/:id` — 更新文章，不存在返回 404。
- `DELETE /api/articles/:id` — 删除文章，不存在返回 404，成功返回 204。
- 你用 Thunder Client 测试了所有 5 个接口，每个接口都能正常工作。
- 你重启服务器后，所有创建的文章都消失了——深刻理解了"内存存储"的致命缺陷。

---

## 二、前置条件

| 序号 | 条件 | 验证命令 |
|------|------|----------|
| 1 | 已完成教程 08，`AppError` 和 `errorHandler` 已配置 | `npm run dev` 正常启动 |
| 2 | 统一响应格式已应用（`{ success: true, data: ... }`） | `GET /api/articles` 返回统一格式 |
| 3 | `express.json()` 已配置 | `POST /api/echo` 能正常接收 `req.body` |
| 4 | Thunder Client 会用 | 能发 GET/POST/PUT/DELETE 请求 |

**一条命令确认前置满足**：

```bash
npm run dev
```

终端输出 "Server is running on http://localhost:3000"，且 `GET /api/articles` 返回 `{ success: true, data: {...} }` 格式，前置条件满足。

---

## 三、分步操作

### 步骤 1：CRUD 是什么？

CRUD 是后端开发中最常见的四个操作的首字母缩写：

| 字母 | 操作 | HTTP 方法 | 含义 | 餐厅比喻 |
|------|------|-----------|------|----------|
| **C** | Create | POST | 创建新资源 | 客人点了一道新菜，厨师做好加入菜单 |
| **R** | Read | GET | 读取资源 | 客人看菜单（列表）或看某道菜的详情 |
| **U** | Update | PUT | 更新资源 | 客人说"这道菜换一种做法" |
| **D** | Delete | DELETE | 删除资源 | 客人说"这道菜不要了" |

**每一套 CRUD 接口 = 一个"资源"的完整管理功能。** 你今天要写的就是"文章"这个资源的 CRUD。

---

### 步骤 2：重写 `routes/articles.js`——完整 CRUD

现在打开 `routes/articles.js`，把它**完全重写**为以下内容。每一个改动都有注释说明。

```javascript
const express = require('express');
const crypto = require('crypto');
const router = express.Router();
const AppError = require('../utils/AppError');

// ========== 模拟数据库：用数组存储文章 ==========
// 初始数据：3 篇示例文章
let articles = [
    {
        id: 'a1b2c3d4-e5f6-7890-abcd-ef1234567890',
        title: 'Node.js 入门指南',
        content: 'Node.js 是一个基于 Chrome V8 引擎的 JavaScript 运行时...',
        author: '小明',
        createdAt: '2026-06-01T08:00:00.000Z',
        updatedAt: '2026-06-01T08:00:00.000Z'
    },
    {
        id: 'b2c3d4e5-f6a7-8901-bcde-f12345678901',
        title: 'Express 框架详解',
        content: 'Express 是 Node.js 最流行的 Web 框架...',
        author: '小红',
        createdAt: '2026-06-02T08:00:00.000Z',
        updatedAt: '2026-06-02T08:00:00.000Z'
    },
    {
        id: 'c3d4e5f6-a7b8-9012-cdef-123456789012',
        title: 'RESTful API 设计',
        content: 'RESTful 是一种 API 设计风格...',
        author: '小刚',
        createdAt: '2026-06-03T08:00:00.000Z',
        updatedAt: '2026-06-03T08:00:00.000Z'
    }
];

// ========== R — Read：获取文章列表 ==========
// GET /api/articles
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

// ========== R — Read：获取单篇文章 ==========
// GET /api/articles/:id
router.get('/:id', (req, res) => {
    const article = articles.find(a => a.id === req.params.id);
    if (!article) {
        throw new AppError('文章不存在', 404);
    }
    res.json({
        success: true,
        data: article
    });
});

// ========== C — Create：创建文章 ==========
// POST /api/articles
router.post('/', (req, res) => {
    const { title, content, author } = req.body;

    // 验证必填字段
    if (!title || !content) {
        throw new AppError('标题和内容为必填字段', 400);
    }

    // 创建新文章
    const newArticle = {
        id: crypto.randomUUID(),           // 用 UUID 生成唯一 ID
        title: title,
        content: content,
        author: author || '匿名',           // 作者可选，默认"匿名"
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString()
    };

    // 存入数组（模拟数据库插入）
    articles.push(newArticle);

    // 返回 201 Created + 新创建的文章
    res.status(201).json({
        success: true,
        data: newArticle
    });
});

// ========== U — Update：更新文章 ==========
// PUT /api/articles/:id
router.put('/:id', (req, res) => {
    const { title, content, author } = req.body;

    // 查找文章
    const index = articles.findIndex(a => a.id === req.params.id);
    if (index === -1) {
        throw new AppError('文章不存在', 404);
    }

    // 验证必填字段
    if (!title || !content) {
        throw new AppError('标题和内容为必填字段', 400);
    }

    // 全量替换（PUT 的语义）
    articles[index] = {
        ...articles[index],       // 保留 id 和 createdAt
        title: title,
        content: content,
        author: author || articles[index].author,
        updatedAt: new Date().toISOString()
    };

    res.json({
        success: true,
        data: articles[index]
    });
});

// ========== D — Delete：删除文章 ==========
// DELETE /api/articles/:id
router.delete('/:id', (req, res) => {
    const index = articles.findIndex(a => a.id === req.params.id);
    if (index === -1) {
        throw new AppError('文章不存在', 404);
    }

    // 从数组中删除
    articles.splice(index, 1);

    // 返回 204 No Content（成功但无内容）
    res.status(204).send();
});

module.exports = router;
```

---

### 步骤 3：逐行解释——每个接口的要点

#### 3.1 为什么用 `let` 而不是 `const` 声明数组？

```javascript
let articles = [ ... ];
```

因为我们要对数组进行增删改操作（`push`、`splice`、索引赋值），所以用 `let` 声明。`const` 声明只是不能重新赋值（`articles = []`），但 `push` 和 `splice` 是可以的——不过用 `let` 语义更清楚："这个数组的内容会变"。

#### 3.2 为什么用 UUID 而不是自增数字？

```javascript
id: crypto.randomUUID()
```

`crypto.randomUUID()` 生成一个全局唯一的字符串 ID，如 `"a1b2c3d4-e5f6-7890-abcd-ef1234567890"`。

| 对比 | 自增数字（1, 2, 3...） | UUID |
|------|----------------------|------|
| 唯一性 | 单机唯一，多机可能冲突 | 全球唯一 |
| 实现 | 简单，`articles.length + 1` | 需要 `crypto.randomUUID()` |
| 安全性 | 容易被猜测（知道 5 号就能猜到 6 号） | 无法猜测 |
| 分布式友好 | ❌ 两台服务器可能生成相同的 ID | ✅ 生成相同 UUID 的概率接近于零 |

> 🔥 **魔鬼细节**：`crypto.randomUUID()` 是 Node.js 19+ 才内置的。如果你用的是 Node.js 18，可以用 `require('crypto').randomUUID()`（同样可用）。如果你的 Node.js 版本低于 14.17，需要安装 `uuid` 包：`npm install uuid`。

#### 3.3 创建文章——必填字段验证

```javascript
if (!title || !content) {
    throw new AppError('标题和内容为必填字段', 400);
}
```

`!title` 会在 `title` 为 `undefined`、`null`、`''`（空字符串）时都为 `true`。这就是最简单的"必填字段验证"。

> 未来你可以用专业的验证库（如 `joi`、`express-validator`），但基本原理就是检查 `req.body` 里有没有需要的字段。

#### 3.4 更新文章——PUT 全量替换

```javascript
articles[index] = {
    ...articles[index],       // 保留 id 和 createdAt
    title: title,
    content: content,
    author: author || articles[index].author,
    updatedAt: new Date().toISOString()
};
```

`...articles[index]` 是 JavaScript 的展开运算符（spread），把旧文章的所有字段先展开，然后用新值覆盖 `title`、`content` 等字段。这样可以保留 `id` 和 `createdAt`（创建时间不应该被修改）。

#### 3.5 删除文章——返回 204

```javascript
res.status(204).send();
```

204 No Content 表示"操作成功，但没有返回内容"。这是 HTTP 标准中 DELETE 操作的推荐做法——删除成功，不需要返回数据。

> `res.send()` 不传参数，等价于发送一个空响应体。`res.status(204).json()` 也可以，但 Express 在 204 时会自动忽略响应体。

#### 3.6 删除不存在的文章——返回 404 还是 204？

**答案：404。**

- **204** 暗示"操作成功了，只是没有内容返回"。如果文章不存在，删除操作没有成功。
- **404** 明确表示"你要操作的资源不存在"。

所以，删除不存在的文章 = 返回 404，而不是 204。

---

### 步骤 4：用 Thunder Client 测试所有接口

现在服务器跑起来，用 Thunder Client 逐一测试 5 个接口。

#### 测试 1：GET /api/articles — 获取文章列表

| 项目 | 值 |
|------|-----|
| 方法 | GET |
| URL | `http://localhost:3000/api/articles` |
| 预期 Status | 200 |
| 预期 Body | `{ success: true, data: { page: 1, limit: 10, total: 3, articles: [...] } }` |

#### 测试 2：GET /api/articles/:id — 获取单篇文章

| 项目 | 值 |
|------|-----|
| 方法 | GET |
| URL | `http://localhost:3000/api/articles/a1b2c3d4-e5f6-7890-abcd-ef1234567890` |
| 预期 Status | 200 |
| 预期 Body | `{ success: true, data: { id: "a1b2c3d4-...", title: "Node.js 入门指南", ... } }` |

> 测试不存在的 ID：`GET /api/articles/nonexistent-id` → 404，`{ success: false, error: { message: "文章不存在", code: "NOT_FOUND" } }`

#### 测试 3：POST /api/articles — 创建文章

| 项目 | 值 |
|------|-----|
| 方法 | POST |
| URL | `http://localhost:3000/api/articles` |
| Body → JSON | `{ "title": "我的第一篇文章", "content": "这是通过 API 创建的文章内容", "author": "测试用户" }` |
| 预期 Status | 201 |
| 预期 Body | `{ success: true, data: { id: "（UUID）", title: "我的第一篇文章", ... } }` |

> 测试必填字段校验：只发 `{ "title": "测试" }`（缺少 content） → 400，`{ success: false, error: { message: "标题和内容为必填字段" } }`

#### 测试 4：PUT /api/articles/:id — 更新文章

| 项目 | 值 |
|------|-----|
| 方法 | PUT |
| URL | 用上面创建返回的 UUID（如 `http://localhost:3000/api/articles/xxx-xxx-xxx`） |
| Body → JSON | `{ "title": "修改后的标题", "content": "修改后的内容", "author": "新作者" }` |
| 预期 Status | 200 |
| 预期 Body | `{ success: true, data: { id: "xxx-xxx", title: "修改后的标题", ... } }` |

> 测试更新不存在的文章 → 404。

#### 测试 5：DELETE /api/articles/:id — 删除文章

| 项目 | 值 |
|------|-----|
| 方法 | DELETE |
| URL | 用上面创建返回的 UUID |
| 预期 Status | 204 |
| 预期 Body | 空（无内容） |

> 再次访问同一个 ID → 404（已经被删了）。

---

### 步骤 5：PUT 和 PATCH 的区别

你可能会在其他资料里看到 `PATCH` 方法。这里简单对比一下：

| 方法 | 语义 | 请求体 | 示例 |
|------|------|--------|------|
| **PUT** | 全量替换 | 必须传所有字段 | `{ "title": "新标题", "content": "新内容", "author": "新作者" }` |
| **PATCH** | 部分更新 | 只传要改的字段 | `{ "title": "只改标题" }` |

**本教程用 PUT 简化**：如果想用 PATCH，需要额外处理"哪些字段没传就保留原值"的逻辑。PUT 要求传所有字段，逻辑更简单。等你对 CRUD 更熟悉了，可以自己改成 PATCH。

> 实际项目中，PUT 和 PATCH 经常混用。REST 纯正主义者会坚持 PATCH 用于部分更新，但很多团队直接用 PUT 处理所有更新——只要团队内部统一就行。

---

### 步骤 6：内存版的致命缺陷——重启服务器数据全丢

现在做最后一个实验：

1. 用 POST 创建一篇文章
2. 确认 GET 列表里能看到它
3. 在终端按 `Ctrl+C` 停止服务器
4. 重新 `npm run dev` 启动服务器
5. 再次 GET 列表

**你刚刚创建的文章消失了！**

**原因**：文章数据存储在 `articles` 数组里，而数组在 Node.js 进程的**内存**中。进程一旦停止，内存就被操作系统回收，所有数据都没了。

**比喻**：你在一张餐巾纸上记账。餐巾纸丢了（服务器重启），账目全没了。你需要一本真正的账本（数据库）——即使你下班了（服务器关了），账本还在，第二天还能接着用。

**这就是为什么需要数据库。** 下一阶段（教程 10-14 章）将引入 SQLite 数据库，把数据真正存到硬盘上。

---

### 🤔 想多一点：为什么 `crypto.randomUUID()` 是内置的，不用装 `uuid` 包？

在 Node.js 早期版本中，生成 UUID 需要安装第三方 `uuid` 包（`npm install uuid`）。从 Node.js 14.17 开始，`crypto.randomUUID()` 被内置了。

**你应该用哪个？**
- Node.js ≥ 14.17：用 `crypto.randomUUID()`（无需安装任何东西）。
- 老项目还在用 `uuid` 包：继续用，不要为了"升级"而改已有代码。

**本教程要求 Node.js 18+**，所以直接用 `crypto.randomUUID()`。

---

### ❌ 常见错误 → ✅ 解决方案

| 错误信息 / 现象 | 原因 | 解决 |
|-----------------|------|------|
| `POST /api/articles` 返回 400 "标题和内容为必填字段" | 请求体中没有 `title` 或 `content` 字段 | 在 Thunder Client 的 Body 中确保 JSON 包含这两个字段 |
| `POST /api/articles` 返回 `req.body` 为 `undefined` | `express.json()` 中间件没配置或顺序错误 | 确保 `app.use(express.json())` 在路由之前 |
| `PUT /api/articles/:id` 返回 404 | ID 不存在或 ID 格式不对 | 先从 GET 列表里复制一个真实 ID |
| `DELETE /api/articles/:id` 返回 404 | 同样的问题 | 同样从 GET 列表里复制 ID |
| `crypto.randomUUID is not a function` | Node.js 版本太低（< 14.17） | 升级到 Node.js 18+，或用 `npm install uuid` |
| 删除后立刻创建，新文章的 ID 和旧文章不同 | UUID 是随机生成的，不会重复利用旧 ID | 这是正常行为——UUID 的唯一性保证新 ID 不会和旧 ID 冲突 |
| 数据在重启后消失 | 数据存储在内存中，进程停止内存释放 | 正常现象——下一阶段引入数据库解决 |

---

## 四、完整代码清单

### `blog-backend/routes/articles.js`（本章完全重写）

```javascript
const express = require('express');
const crypto = require('crypto');
const router = express.Router();
const AppError = require('../utils/AppError');

// ========== 模拟数据库：用数组存储文章 ==========
let articles = [
    {
        id: 'a1b2c3d4-e5f6-7890-abcd-ef1234567890',
        title: 'Node.js 入门指南',
        content: 'Node.js 是一个基于 Chrome V8 引擎的 JavaScript 运行时...',
        author: '小明',
        createdAt: '2026-06-01T08:00:00.000Z',
        updatedAt: '2026-06-01T08:00:00.000Z'
    },
    {
        id: 'b2c3d4e5-f6a7-8901-bcde-f12345678901',
        title: 'Express 框架详解',
        content: 'Express 是 Node.js 最流行的 Web 框架...',
        author: '小红',
        createdAt: '2026-06-02T08:00:00.000Z',
        updatedAt: '2026-06-02T08:00:00.000Z'
    },
    {
        id: 'c3d4e5f6-a7b8-9012-cdef-123456789012',
        title: 'RESTful API 设计',
        content: 'RESTful 是一种 API 设计风格...',
        author: '小刚',
        createdAt: '2026-06-03T08:00:00.000Z',
        updatedAt: '2026-06-03T08:00:00.000Z'
    }
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

// GET /api/articles/:id — 获取单篇文章
router.get('/:id', (req, res) => {
    const article = articles.find(a => a.id === req.params.id);
    if (!article) {
        throw new AppError('文章不存在', 404);
    }
    res.json({
        success: true,
        data: article
    });
});

// POST /api/articles — 创建文章
router.post('/', (req, res) => {
    const { title, content, author } = req.body;

    if (!title || !content) {
        throw new AppError('标题和内容为必填字段', 400);
    }

    const newArticle = {
        id: crypto.randomUUID(),
        title: title,
        content: content,
        author: author || '匿名',
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString()
    };

    articles.push(newArticle);

    res.status(201).json({
        success: true,
        data: newArticle
    });
});

// PUT /api/articles/:id — 更新文章
router.put('/:id', (req, res) => {
    const { title, content, author } = req.body;

    const index = articles.findIndex(a => a.id === req.params.id);
    if (index === -1) {
        throw new AppError('文章不存在', 404);
    }

    if (!title || !content) {
        throw new AppError('标题和内容为必填字段', 400);
    }

    articles[index] = {
        ...articles[index],
        title: title,
        content: content,
        author: author || articles[index].author,
        updatedAt: new Date().toISOString()
    };

    res.json({
        success: true,
        data: articles[index]
    });
});

// DELETE /api/articles/:id — 删除文章
router.delete('/:id', (req, res) => {
    const index = articles.findIndex(a => a.id === req.params.id);
    if (index === -1) {
        throw new AppError('文章不存在', 404);
    }

    articles.splice(index, 1);

    res.status(204).send();
});

module.exports = router;
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
│   ├── articles.js     ← 本章完全重写
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
| 2 | `GET /api/articles` | 200，`{ success: true, data: { articles: [3篇] } }` |
| 3 | `GET /api/articles/<uuid>` | 200，返回对应文章 |
| 4 | `GET /api/articles/nonexistent` | 404，`{ success: false, error: { message: "文章不存在" } }` |
| 5 | `POST /api/articles`，Body: `{"title":"测试","content":"内容"}` | 201，返回新文章（含 UUID） |
| 6 | `POST /api/articles`，Body: `{"title":"缺内容"}`（缺少 content） | 400，`{ success: false, error: { message: "标题和内容为必填字段" } }` |
| 7 | `PUT /api/articles/<uuid>`，Body: `{"title":"改","content":"改"}` | 200，更新时间已改变 |
| 8 | `PUT /api/articles/nonexistent`，Body: `{"title":"改","content":"改"}` | 404 |
| 9 | `DELETE /api/articles/<uuid>` | 204（空响应） |
| 10 | 再次 `DELETE /api/articles/<同上uuid>` | 404（已删除） |
| 11 | 重启服务器后 `GET /api/articles` | 回到初始 3 篇——你创建的文章消失了 |

全部通过？恭喜！你已经完成了人生中第一个完整的 CRUD 接口。

---

## 六、小结表格

| 学到的东西 | 一句话解释 |
|-----------|-----------|
| CRUD 完整实现 | Create(POST) + Read(GET) + Update(PUT) + Delete(DELETE) = 一个资源的完整管理 |
| 数组模拟数据库 | `let articles = []`，用 `push`、`find`、`findIndex`、`splice` 操作 |
| UUID 生成 ID | `crypto.randomUUID()` 生成全球唯一 ID，比自增数字更适合分布式 |
| 必填字段验证 | `if (!title \|\| !content)` 检查请求体，不通过返回 400 |
| PUT 全量替换 | 用 `...articles[index]` 保留旧字段，再覆盖新值 |
| 204 No Content | DELETE 成功后返回 204，表示"操作成功但无内容" |
| 内存存储的致命缺陷 | 数据在进程内存中，重启服务器数据全丢——必须引入数据库 |
| PUT vs PATCH | PUT 全量替换，PATCH 部分更新；本教程用 PUT 简化 |

---

## 七、术语附录

| 术语 | 英文 | 通俗解释 | 本章出现位置 | 字面陷阱 |
|------|------|----------|-------------|----------|
| CRUD | Create, Read, Update, Delete | 对数据最基本的四种操作：创建、读取、更新、删除。是后端开发中最常见的模式。 | 步骤 1 | 不是"粗鲁"（crude）——是四个单词的首字母缩写。 |
| UUID | Universally Unique Identifier | 一种 128 位的全局唯一标识符，格式为 `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`。`crypto.randomUUID()` 生成的是 UUID v4（随机生成）。 | 步骤 3.2 | 不是"你的 ID"——是"通用唯一标识符"。UUID 不会重复，所以即使两台服务器同时生成，也不会冲突。 |
| 幂等性 | Idempotency | 同一个操作执行一次和执行多次，结果相同。PUT 和 DELETE 是幂等的，POST 不是。 | 步骤 3.5 | 05 章已出现过。本章再强调：DELETE 不存在的文章返回 404 而非 204，因为 204 暗示操作成功。 |
| PUT vs PATCH | — | PUT 全量替换（传所有字段），PATCH 部分更新（只传要改的字段）。本教程用 PUT 简化。 | 步骤 5 | 不是"PUT 就是改"——PUT 的语义是"把这个 URL 对应的资源替换成我传给你的内容"。 |
| 204 No Content | — | HTTP 状态码，表示操作成功但响应体为空。DELETE 成功后的标准响应。 | 步骤 3.5 | 不是"204 没有内容"= 失败——204 的 2xx 开头意味着**成功**，只是没有返回数据。 |
| 内存存储 | In-Memory Storage | 数据存储在程序运行时的内存中，程序关闭后数据丢失。与"持久化存储"（数据库、文件）相对。 | 步骤 6 | 不是"存在脑子里"——是"存在计算机的 RAM 里"，断电或进程退出就没了。 |

---

## 八、已知坑点与禁止事项

1. **内存存储重启即丢**：本章的 `articles` 数组存在 Node.js 进程内存中。`Ctrl+C` 停止服务器后，你创建的所有文章都会消失。**这是有意为之——下一阶段引入数据库解决。**

2. **UUID 不会重复，但也不是"绝对不可能"**：UUID v4 的碰撞概率约为 2^122 分之一，比被陨石砸中的概率还低。在单个项目中，你永远不需要担心 UUID 冲突。

3. **PUT 要求传所有字段**：如果你只传了 `{ "title": "新标题" }` 而没有 `content`，`content` 会变成 `undefined`——因为必填字段校验不通过，会返回 400。

4. **`crypto.randomUUID()` 需要 Node.js ≥ 14.17**：本教程要求 Node.js 18+，所以没问题。如果你在更老的 Node.js 版本上运行，需要 `npm install uuid` 然后 `const { v4: uuidv4 } = require('uuid')`。

5. **删除不存在的文章返回 404，不是 204**：204 暗示操作成功了。删除不存在的文章 = 操作失败 = 404。

6. **`id` 现在是字符串（UUID），不是数字**：`req.params.id` 本身就是字符串，所以不需要 `parseInt()`。但 `===` 比较仍然有效——因为两个都是字符串。

---

## 九、下一步建议

你已经完成了第一个完整的 CRUD 接口！但数据存在内存里，重启就没了。接下来：

- **下一阶段（教程 10-14）**：引入 SQLite 数据库，把数据真正存到硬盘上。学 SQL 语句、建表、在 Node.js 中连接数据库、把 CRUD 接口从内存版升级到数据库版。
- **延伸思考**：你现在有 5 个接口，但没有任何"认证"——任何人都可以随意创建、修改、删除文章。后面会学 JWT 认证，让用户必须登录才能操作。

---

> [可暂停点 2/9]：阶段二（API 基本功）已完成。你学到了路由方法、参数处理、中间件、请求/响应、统一错误处理、CRUD 实战。下次从第 10 章（数据库入门）继续。
>
> 📊 本教程无可视化
>
> 本教程编辑记录：2026-06-12 初始版本。