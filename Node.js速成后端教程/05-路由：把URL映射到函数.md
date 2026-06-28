# 05-路由：把 URL 映射到函数

> "路由是后端开发的骨架——URL 长什么样，对应哪个函数，返回什么数据。这一章我们系统学习 Express 路由的全部玩法：GET/POST/PUT/DELETE 四种方法、路径参数、查询参数、路由分组，以及那些让你 debug 到凌晨三点的路由顺序陷阱。"

---

## 一、目标与完成效果

**一句话目标**：掌握 Express 路由系统的完整用法，能用 `app.get()` / `app.post()` / `app.put()` / `app.delete()` 定义四种 HTTP 方法的接口，理解路径参数和查询参数的区别，学会用 `express.Router()` 管理多组路由，避开路由顺序的经典陷阱。

**完成后的可观测效果**：
- 你的 `server.js` 里新增了直接用 `app.post()` 等定义的测试路由，并用 Thunder Client 验证了所有四种 HTTP 方法。
- 你理解了 `req.params` 和 `req.query` 的区别，能正确获取路径参数和查询参数。
- 你的 `routes/articles.js` 里新增了带查询参数的文章列表接口（支持分页）。
- 你亲手验证了路由顺序陷阱：把 `/articles/me` 放在 `/:id` 后面，`me` 被当成 id 处理。
- 你能对着 RESTful 设计规范表格，判断一个 URL 设计是否"RESTful"。

---

## 二、前置条件

| 序号 | 条件 | 验证命令 |
|------|------|----------|
| 1 | 已完成教程 04，`server.js` 和 `routes/articles.js` 存在且功能正常 | `npm run dev` 正常启动 |
| 2 | Thunder Client 插件已安装 | VS Code 左侧有闪电图标 |
| 3 | 理解 HTTP 方法的基本概念（GET/POST/PUT/DELETE） | 能说出 GET 是"获取"，POST 是"创建" |
| 4 | 理解 `require` 和 `module.exports` | 能看懂 `const router = require('./routes/articles')` |

**一条命令确认前置满足**：

```bash
npm run dev
```

终端输出 "Server is running on http://localhost:3000"，且 `GET http://localhost:3000/api/articles` 返回文章 JSON 数组，前置条件满足。

---

## 三、分步操作

### 步骤 1：路由的本质——"URL → 函数"的映射表

你已经不知不觉用了很多次路由。在 `server.js` 里：

```javascript
app.get('/', (req, res) => { res.send('你好，世界！'); });
app.get('/api/hello', (req, res) => { res.json({ message: 'Hello API' }); });
```

这两行代码就是在定义**路由**（Route）。

#### 路由的三个要素

一条完整的路由由三个部分组成：

```
app.get('/api/articles', (req, res) => { ... });
  ↑        ↑                  ↑
HTTP方法   URL路径            处理函数
```

| 要素 | 说明 | 例子 |
|------|------|------|
| **HTTP 方法** | 客人想做什么？ | `GET` 读、`POST` 创建、`PUT` 改、`DELETE` 删 |
| **URL 路径** | 客人找哪个资源？ | `/api/articles` = 文章列表，`/api/articles/3` = 第 3 号文章 |
| **处理函数** | 服务员接到这个请求后怎么处理？ | `(req, res) => { res.json(data) }` |

**比喻**：路由就是餐厅的"菜单 + 流程手册"。菜单上的每一行（URL + 方法）都对应后厨的一个标准操作流程（处理函数）。

```
菜单：
  GET  /               → "欢迎光临，请坐！"（res.send('你好，世界！'))
  GET  /api/articles   → "这是今天的菜单"（res.json(articles)）
  GET  /api/articles/3 → "第3号菜的详情"（res.json(article)）
  POST /api/articles   → "好的，帮您记下了"（添加新文章）
```

> 🔥 **魔鬼细节**：Express 内部有一个**路由表**（Route Table），它本质是一个**数组**。每当你调用 `app.get('/xxx', handler)`，Express 就往这个数组里追加一条记录。当请求进来时，Express 从数组的**第一条开始往后找**，找到第一个匹配的就停。这个"顺序匹配"机制，会导致步骤 6 的经典陷阱。

---

### 步骤 2：app.get() / app.post() / app.put() / app.delete()——四种方法实战

到目前为止你只用了 `app.get()`。现在把四种方法都试一遍。

在 `server.js` 中现有路由的下方，添加以下四个测试路由：

```javascript
// 测试 POST 请求
app.post('/api/test', (req, res) => {
    res.json({ message: 'POST 请求成功！' });
});

// 测试 PUT 请求
app.put('/api/test', (req, res) => {
    res.json({ message: 'PUT 请求成功！' });
});

// 测试 DELETE 请求
app.delete('/api/test', (req, res) => {
    res.json({ message: 'DELETE 请求成功！' });
});
```

> 注意：`app.get('/api/test')` 我们没有加——等一下你可以试试用 Thunder Client 发 GET 请求到 `/api/test`，看看 Express 返回什么。

保存文件，nodemon 自动重启。

#### 用 Thunder Client 验证四种方法

打开 Thunder Client，分别发送以下四个请求：

| 方法 | URL | 预期 Status | 预期 Response |
|------|-----|-------------|---------------|
| `GET` | `http://localhost:3000/api/test` | **404** 或 `Cannot GET /api/test` | 我们没有定义 GET 对应的路由 |
| `POST` | `http://localhost:3000/api/test` | 200 | `{"message":"POST 请求成功！"}` |
| `PUT` | `http://localhost:3000/api/test` | 200 | `{"message":"PUT 请求成功！"}` |
| `DELETE` | `http://localhost:3000/api/test` | 200 | `{"message":"DELETE 请求成功！"}` |

> 🔥 **重要发现**：同一个 URL `/api/test`，用不同的 HTTP 方法访问，会触发**不同的处理函数**。这就是 RESTful 设计的核心思想——**URL 表示"资源"，HTTP 方法表示"操作"**。

#### 为什么 GET 返回 404？

因为虽然 URL 匹配（`/api/test`），但 HTTP 方法不匹配。Express 找的是 `GET /api/test` 对应的处理函数——你没定义，所以 404。

**比喻**：你走进餐厅说"我要删掉宫保鸡丁"（`DELETE /api/test`），服务员查菜单，找到 `DELETE /api/test` 这条规则，执行了删除操作。但如果你说"给我看看宫保鸡丁"（`GET /api/test`），服务员翻遍菜单找不到对应规则——这道菜没有"只看不买"的选项（你没定义 GET 路由），于是回复"404，没有这个服务"。

---

### 步骤 3：express.Router() 路由分组——多组路由管理

在教程 04 中你已经创建了 `routes/articles.js` 并在 `server.js` 中挂载。现在让我们深入理解这个模式，并再创建一个路由分组。

#### 3.1 创建第二组路由：`routes/auth.js`

在 `routes/` 目录下新建 `auth.js`：

```javascript
const express = require('express');
const router = express.Router();

// 用户注册（暂时只返回模拟数据）
router.post('/register', (req, res) => {
    res.json({ message: '注册成功', user: { id: 1, username: 'newuser' } });
});

// 用户登录（暂时只返回模拟数据）
router.post('/login', (req, res) => {
    res.json({ message: '登录成功', token: 'fake-jwt-token-xxxxx' });
});

module.exports = router;
```

#### 3.2 在 server.js 中挂载第二组路由

在 `server.js` 中，在 `articlesRouter` 的引入和挂载下方，添加：

```javascript
// 引入认证路由
const authRouter = require('./routes/auth');

// 挂载认证路由
app.use('/api/auth', authRouter);
```

现在 `server.js` 的完整路由部分应该是：

```javascript
const express = require('express');
const app = express();

// 引入路由模块
const articlesRouter = require('./routes/articles');
const authRouter = require('./routes/auth');

// 挂载路由
app.use('/api/articles', articlesRouter);
app.use('/api/auth', authRouter);

// 首页路由
app.get('/', (req, res) => {
    res.send('你好，世界！');
});

// API 测试路由
app.get('/api/hello', (req, res) => {
    res.json({ message: 'Hello API' });
});

// 测试路由（四种 HTTP 方法）
app.post('/api/test', (req, res) => {
    res.json({ message: 'POST 请求成功！' });
});
app.put('/api/test', (req, res) => {
    res.json({ message: 'PUT 请求成功！' });
});
app.delete('/api/test', (req, res) => {
    res.json({ message: 'DELETE 请求成功！' });
});

app.listen(3000, () => {
    console.log('Server is running on http://localhost:3000');
});
```

#### 3.3 验证

| 请求 | 预期结果 |
|------|----------|
| `POST http://localhost:3000/api/auth/register` | `{"message":"注册成功","user":{"id":1,"username":"newuser"}}` |
| `POST http://localhost:3000/api/auth/login` | `{"message":"登录成功","token":"fake-jwt-token-xxxxx"}` |

#### 3.4 路由分组的好处

| 单文件写所有路由 | 路由分组 |
|------------------|----------|
| `server.js` 几百行 | `server.js` 只负责挂载，10 行左右 |
| 改文章路由要翻整个文件 | 直接打开 `routes/articles.js` |
| 多人协作容易冲突 | 每人负责一个路由文件，互不影响 |
| 路由命名混乱 | 每个文件内部路径是相对的，命名自然分层 |

**比喻**：`server.js` 是商场入口的导览牌（"川菜区 → 3楼A区，粤菜区 → 3楼B区"）。每个 `routes/xxx.js` 是一个独立的后厨专区。`app.use('/api/articles', articlesRouter)` 就是在入口挂一个"文章服务 → 请走这边"的指示牌。

---

### 步骤 4：路径参数——`/articles/:id` → `req.params.id`

在前面的教程中你已经在用了：

```javascript
// routes/articles.js 中
router.get('/:id', (req, res) => {
    const article = articles.find(a => a.id === parseInt(req.params.id));
    // ...
});
```

现在来彻底搞懂它。

#### 4.1 什么是路径参数

路径参数是**嵌在 URL 路径里面**的变量。Express 用冒号 `:` 标记：

```
GET /api/articles/3
                  ↑
              路径参数（id = 3）
```

定义路由时：`'/api/articles/:id'`
请求到来时：Express 把 `3` 提取出来，放到 `req.params.id` 里。

#### 4.2 多个路径参数

一个路由可以有多个路径参数：

```javascript
// 在 routes/articles.js 中添加（演示用）
router.get('/:category/:id', (req, res) => {
    res.json({
        category: req.params.category,
        id: parseInt(req.params.id)
    });
});
```

访问 `GET /api/articles/tech/5`，返回：

```json
{ "category": "tech", "id": 5 }
```

> 🔥 **魔鬼细节**：`req.params.id` 的值**永远是字符串**。`parseInt(req.params.id)` 是必须的，否则 `a.id === req.params.id` 的比较中，`1 === "1"` 用 `===` 会返回 `false`（类型不同）。

#### 4.3 路径参数 vs 查询参数

很多初学者搞不清什么时候用路径参数，什么时候用查询参数。先看表格，再看实战：

| 维度 | 路径参数 (`:id`) | 查询参数 (`?key=value`) |
|------|-----------------|------------------------|
| 在 URL 中的位置 | 路径的一部分 | `?` 后面 |
| 语法 | `/articles/:id` | `/articles?page=1&limit=10` |
| 在 Express 中读取 | `req.params.id` | `req.query.page` |
| 语义 | **"哪个资源"**（身份标识） | **"怎么展示"**（排序、过滤、分页） |
| 必填/可选 | 通常必填（缺少路径不匹配） | 通常可选（不传就用默认值） |
| 例子 | `GET /articles/5` → "第 5 号文章" | `GET /articles?page=3&limit=10` → "文章列表第 3 页，每页 10 条" |

**一句话判断**：如果这个参数用来回答"**哪一个**"（which one），用路径参数。如果用来回答"**怎么排列/过滤**"（how to display），用查询参数。

---

### 步骤 5：查询参数——`/articles?page=1&limit=10` → `req.query.page`

查询参数是 URL 中 `?` 后面的键值对。现在给文章列表加上分页功能。

#### 5.1 修改 `routes/articles.js` 的列表接口

打开 `routes/articles.js`，把原来的 `router.get('/')` 改成：

```javascript
// GET /api/articles — 获取所有文章（支持分页）
router.get('/', (req, res) => {
    // 从查询参数中获取 page 和 limit，设置默认值
    const page = parseInt(req.query.page) || 1;
    const limit = parseInt(req.query.limit) || 10;

    // 计算分页起始和结束位置
    const startIndex = (page - 1) * limit;
    const endIndex = startIndex + limit;

    // 分页切片
    const paginatedArticles = articles.slice(startIndex, endIndex);

    // 返回数据 + 分页信息
    res.json({
        page: page,
        limit: limit,
        total: articles.length,
        data: paginatedArticles
    });
});
```

#### 逐行解释

```javascript
const page = parseInt(req.query.page) || 1;
```

`req.query` 是一个对象，包含 URL 中所有查询参数。如果 URL 是 `/api/articles?page=2&limit=5`，那么 `req.query` 就是 `{ page: '2', limit: '5' }`。

> 🔥 **魔鬼细节**：`req.query` 里的值也全是**字符串**！`req.query.page` 是 `'2'` 而不是 `2`。所以用 `parseInt()` 转换。`|| 1` 是 JavaScript 的"默认值"技巧——如果 `parseInt(undefined)` 返回 `NaN`（falsy），就取 `1`。

```javascript
const paginatedArticles = articles.slice(startIndex, endIndex);
```

`Array.slice()` 是 JavaScript 内置的数组切片方法。`articles.slice(0, 3)` 返回第 0、1、2 个元素（不包括索引 3）。

#### 5.2 验证

用 Thunder Client 发送以下请求：

| URL | 预期效果 |
|-----|----------|
| `GET /api/articles` | 返回全部 3 篇文章，`page:1, limit:10, total:3` |
| `GET /api/articles?page=1&limit=2` | 返回前 2 篇（id=1 和 id=2），`total:3` |
| `GET /api/articles?page=2&limit=2` | 返回第 3 篇（id=3），`total:3` |
| `GET /api/articles?page=99&limit=10` | 返回空数组 `[]`，`total:3` |

> 注意：`req.query` 里的参数名大小写敏感——`?Page=1` 不会匹配到 `req.query.page`。

---

### 🤔 想多一点：为什么参数值总是字符串？

你可能会觉得烦——每次都要 `parseInt(req.query.page)`。为什么 Express 不自动帮你转成数字？

**原因**：HTTP 协议中，URL 是一个纯文本字符串。`?id=5` 中的 `5` 到底是数字、字符串、还是布尔值？Express 没办法替你做这个判断——因为 `5` 理论上也可以是一个字符串 ID（比如 PostgreSQL 的 UUID 是字符串格式）。

**所以 Express 的哲学是：原样给你，你自己转换。** 这在所有 Web 框架中都是相同的——Django、Spring、Flask 中的查询参数也都是字符串。

---

### 步骤 6：路由顺序陷阱——`/articles/me` 必须放在 `/:id` 前面

这是让无数初学者 debug 到凌晨三点的经典陷阱。现在我们亲手复现它。

#### 6.1 先创建陷阱

在 `routes/articles.js` 中，添加一个特殊路由 `/me`（返回"我的文章"），**但故意放在 `/:id` 后面**：

```javascript
// ❌ 错误示范：/me 放在 /:id 后面
router.get('/:id', (req, res) => {
    const article = articles.find(a => a.id === parseInt(req.params.id));
    if (!article) {
        return res.status(404).json({ error: '文章不存在' });
    }
    res.json(article);
});

// 获取"我的文章"——这个路由会永不被触发！
router.get('/me', (req, res) => {
    res.json({ message: '这是我的文章列表' });
});
```

现在用 Thunder Client 发送 `GET http://localhost:3000/api/articles/me`。

**结果**：返回 `{"error":"文章不存在"}`，而不是 `{"message":"这是我的文章列表"}`。

#### 6.2 为什么？

Express 的路由匹配是**从上到下、顺序执行**的。当请求 `GET /api/articles/me` 进来时：

1. Express 看第一条路由：`router.get('/:id', ...)` → `me` 匹配 `:id` → **匹配成功！**
2. Express 执行处理函数：`articles.find(a => a.id === parseInt('me'))` → `parseInt('me')` 返回 `NaN` → `find` 找不到 → 返回 404。
3. Express **不会继续往下看**。第二条路由 `router.get('/me', ...)` 永远没机会执行。

**比喻**：你来到餐厅前台，第一块牌子上写着"所有号码牌都可以点菜"。你拿的是 "me" 号牌，服务员说"me 不是数字号码，不能点"——然后就不理你了。后面那块"me 号专窗"的牌子，你根本没机会看到。

#### 6.3 解决方案

**固定路径放在动态路径前面**。修改变成：

```javascript
// ✅ 正确顺序：固定路径在前，动态路径在后
router.get('/me', (req, res) => {
    res.json({ message: '这是我的文章列表' });
});

router.get('/:id', (req, res) => {
    const article = articles.find(a => a.id === parseInt(req.params.id));
    if (!article) {
        return res.status(404).json({ error: '文章不存在' });
    }
    res.json(article);
});
```

> 🔥 **金科玉律**：**Express 路由中，固定路径永远放在动态路径（带 `:` 的）之前。** 这条规则记住，能省你无数 debug 时间。

#### 6.4 验证修复

再次发送 `GET http://localhost:3000/api/articles/me`，应该返回 `{"message":"这是我的文章列表"}`。

发送 `GET http://localhost:3000/api/articles/1`，应该正常返回 id=1 的文章。

---

### 步骤 7：RESTful 设计规范

你已经学会了路由的技术实现。现在来了解**怎么设计 URL 才算"好"**。

#### 7.1 RESTful 是什么？

RESTful 是一种 API 设计风格，核心原则两条：

1. **URL 表示资源**（名词），不表示动作（动词）。
2. **HTTP 方法表示操作**（动词）。

```
❌ 不 RESTful：
GET  /api/getArticles        ← URL 里带了动词 get
POST /api/createArticle      ← URL 里带了动词 create
GET  /api/deleteArticle?id=5 ← 用 GET 做删除操作（危险！）

✅ RESTful：
GET    /api/articles         ← 获取文章列表
POST   /api/articles         ← 创建文章
GET    /api/articles/5       ← 获取第 5 号文章
PUT    /api/articles/5       ← 替换第 5 号文章
DELETE /api/articles/5       ← 删除第 5 号文章
```

**比喻**：URL 是"菜名"（名词），HTTP 方法是"动作"（点/退/换）。你不会跟服务员说"我要一份删除宫保鸡丁"——你会说"宫保鸡丁，退掉"（`DELETE /menu/gongbao`）。

#### 7.2 RESTful 设计规范表格

| 规范 | ✅ 正确示例 | ❌ 错误示例 | 说明 |
|------|------------|------------|------|
| URL 用名词复数 | `/api/articles` | `/api/article` | 表示"文章集合" |
| 用 HTTP 方法表示操作 | `DELETE /api/articles/5` | `GET /api/articles/5/delete` | 操作在方法里，不在 URL 里 |
| 层级关系用嵌套 URL | `/api/articles/5/comments` | `/api/comments?articleId=5` | 评论属于文章 |
| 查询参数用于过滤/排序 | `/api/articles?status=published` | `/api/articles/published` | `published` 是过滤条件，不是子资源 |
| 用小写字母 + 连字符 | `/api/blog-posts` | `/api/blogPosts` 或 `/api/BlogPosts` | 避免大小写混乱和驼峰 |
| 不在 URL 末尾加斜杠 | `/api/articles` | `/api/articles/` | 一致性 |
| 用 HTTP 状态码表示结果 | `201 Created` | `200 OK` + `{"created": true}` | 状态码本身就是"结果报告" |

#### 7.3 本教程的 URL 设计

| 功能 | 方法 | URL |
|------|------|-----|
| 文章列表 | `GET` | `/api/articles` |
| 文章详情 | `GET` | `/api/articles/:id` |
| 创建文章 | `POST` | `/api/articles` |
| 更新文章 | `PUT` | `/api/articles/:id` |
| 删除文章 | `DELETE` | `/api/articles/:id` |
| 用户注册 | `POST` | `/api/auth/register` |
| 用户登录 | `POST` | `/api/auth/login` |

> 注册和登录是"动作"而非"资源"，用动词路径是一个常见的务实妥协——纯 RESTful 主义者可能会用 `POST /api/auth/sessions`（创建会话），但 `register` 和 `login` 更直观易懂。

---

### ❌ 常见错误 → ✅ 解决方案

| 错误信息 / 现象 | 原因 | 解决 |
|-----------------|------|------|
| `Cannot GET /api/articles/me` | 固定路径 `me` 放在了 `:id` 后面，被 `:id` 匹配走了，且 `parseInt('me')` 为 `NaN` | 把 `router.get('/me', ...)` 放到 `router.get('/:id', ...)` **前面** |
| `req.params.id` 是字符串导致 `===` 比较失败 | `req.params.id` **永远是字符串** | 用 `parseInt(req.params.id)` 或 `Number(req.params.id)` 转换 |
| 查询参数 `?page=1` 读出来是 `'1'` 而不是 `1` | `req.query` 的值也**全是字符串** | 同样用 `parseInt()` 转换 |
| `POST /api/articles` 返回 404 | 只定义了 `router.get()`，没定义 `router.post()` | 方法必须全部显式定义：`router.post('/', ...)` |
| `Cannot GET /api/auth/register` | `register` 路由用的是 `router.post()`，你发的是 GET 请求 | 检查 Thunder Client 里选的方法是否是 POST |
| `app.use('/api/articles', router)` 前缀拼接错误 | `app.use` 前缀会**自动**加到 router 内部路径前面 | `router.get('/:id')` + `app.use('/api/articles')` = 实际路径 `/api/articles/:id`，不能重复写 `/api/articles` |

---

## 四、完整代码清单

### `blog-backend/server.js`（本章最终状态）

```javascript
const express = require('express');
const app = express();

// 引入路由模块
const articlesRouter = require('./routes/articles');
const authRouter = require('./routes/auth');

// 挂载路由
app.use('/api/articles', articlesRouter);
app.use('/api/auth', authRouter);

// 首页路由
app.get('/', (req, res) => {
    res.send('你好，世界！');
});

// API 测试路由
app.get('/api/hello', (req, res) => {
    res.json({ message: 'Hello API' });
});

// 测试四种 HTTP 方法
app.post('/api/test', (req, res) => {
    res.json({ message: 'POST 请求成功！' });
});

app.put('/api/test', (req, res) => {
    res.json({ message: 'PUT 请求成功！' });
});

app.delete('/api/test', (req, res) => {
    res.json({ message: 'DELETE 请求成功！' });
});

app.listen(3000, () => {
    console.log('Server is running on http://localhost:3000');
});
```

### `blog-backend/routes/articles.js`（本章最终状态）

```javascript
const express = require('express');
const router = express.Router();

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
        page: page,
        limit: limit,
        total: articles.length,
        data: paginatedArticles
    });
});

// GET /api/articles/me — 固定路径必须在动态路径前面
router.get('/me', (req, res) => {
    res.json({ message: '这是我的文章列表' });
});

// GET /api/articles/:id — 获取单篇文章
router.get('/:id', (req, res) => {
    const article = articles.find(a => a.id === parseInt(req.params.id));
    if (!article) {
        return res.status(404).json({ error: '文章不存在' });
    }
    res.json(article);
});

module.exports = router;
```

### `blog-backend/routes/auth.js`（本章新建）

```javascript
const express = require('express');
const router = express.Router();

// 用户注册
router.post('/register', (req, res) => {
    res.json({ message: '注册成功', user: { id: 1, username: 'newuser' } });
});

// 用户登录
router.post('/login', (req, res) => {
    res.json({ message: '登录成功', token: 'fake-jwt-token-xxxxx' });
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
└── routes/
    ├── articles.js
    └── auth.js
```

---

## 五、验证方法

| 序号 | 操作 | 预期结果 |
|------|------|----------|
| 1 | `npm run dev` | 服务器正常启动，无报错 |
| 2 | `POST http://localhost:3000/api/test` | 200，`{"message":"POST 请求成功！"}` |
| 3 | `PUT http://localhost:3000/api/test` | 200，`{"message":"PUT 请求成功！"}` |
| 4 | `DELETE http://localhost:3000/api/test` | 200，`{"message":"DELETE 请求成功！"}` |
| 5 | `GET http://localhost:3000/api/test` | 404（未定义 GET 路由） |
| 6 | `GET http://localhost:3000/api/articles?page=1&limit=2` | 返回 `{page:1, limit:2, total:3, data:[前2篇]}` |
| 7 | `GET http://localhost:3000/api/articles?page=2&limit=2` | 返回 `{total:3, data:[第3篇]}` |
| 8 | `GET http://localhost:3000/api/articles/me` | 200，`{"message":"这是我的文章列表"}`（不是 404） |
| 9 | `GET http://localhost:3000/api/articles/1` | 200，返回 id=1 的文章 |
| 10 | `POST http://localhost:3000/api/auth/register` | 200，`{"message":"注册成功",...}` |
| 11 | `POST http://localhost:3000/api/auth/login` | 200，`{"message":"登录成功",...}` |

全部通过？你已经是路由系统的主人了。

---

## 六、小结表格

| 学到的东西 | 一句话解释 |
|-----------|-----------|
| 路由的三要素 | HTTP 方法 + URL 路径 + 处理函数 |
| `app.get/post/put/delete()` | 四种 HTTP 方法对应四种路由定义方式 |
| `express.Router()` | 创建路由组，每个文件管理一组相关路由 |
| `app.use('/prefix', router)` | 把路由组挂载到主应用，所有内部路径自动加前缀 |
| 路径参数 `:id` | 嵌在 URL 中的变量，Express 提取到 `req.params.id`——**永远是字符串** |
| 查询参数 `?key=value` | URL 中 `?` 后面的键值对，Express 提取到 `req.query.key`——**也永远是字符串** |
| 路由匹配顺序 | Express 从上到下匹配，找到第一个就停——固定路径必须放在动态路径前面 |
| RESTful 设计 | URL = 名词（资源），HTTP 方法 = 动词（操作） |

---

## 七、术语附录

| 术语 | 英文 | 通俗解释 | 本章出现位置 | 字面陷阱 |
|------|------|----------|-------------|----------|
| 路由（Route） | Route | URL 路径 + HTTP 方法 + 处理函数的组合。Express 收到请求后，按路由表找到对应的处理函数并执行。 | 步骤 1 | 不是网络里的"路由器"（Router 硬件）——Web 开发中的 Router = "请求分发器"。 |
| 路径参数 | Path Parameter / URL Parameter | 嵌在 URL 路径中的变量，用 `:` 标记。如 `/articles/:id` 中的 `:id`，值通过 `req.params.id` 获取。 | 步骤 4 | 不是"函数的参数"——它是 URL 的一部分，但被 Express 提取出来变成了变量。 |
| 查询参数 | Query Parameter / Query String | URL 中 `?` 后面的键值对，用于过滤、排序、分页等。如 `?page=1&limit=10`，值通过 `req.query.page` 获取。 | 步骤 5 | 名字里带"查询"但不是数据库的 SELECT 查询——只是 URL 中 `?` 后面的参数。 |
| RESTful | Representational State Transfer | 一种 API 设计风格：URL 表示资源（名词），HTTP 方法表示操作（动词）。是约定而非技术标准。 | 步骤 7 | 不是"安心的"（restful 的字面意思），也不是某公司的专利——是一种架构风格（architectural style）。 |
| 路由组（Router） | Express.Router | Express 提供的"迷你应用"，可以定义一组路由然后挂载到主应用上。让代码分文件管理。 | 步骤 3 | 不是网络路由器——是 Express 框架中的一个类（class），用于组织路由。 |
| 路由匹配顺序 | Route Matching Order | Express 从上到下匹配路由，找到第一个匹配的就停止。固定路径必须放在动态路径（带 `:`）前面。 | 步骤 6 | 不是按照"最佳匹配"而是"最先匹配"——第一个匹配到的就赢，不管后面有没有更精确的。 |

---

## 八、已知坑点与禁止事项

1. **路由顺序陷阱**：`/:id` 会匹配任何单段路径，包括 `me`、`new`、`search` 等。所有固定路径必须放在 `/:id` 前面。这条规则在 Express 官方文档中是明确写明的，但几乎每个初学者都会踩一次。

2. **`req.params` 和 `req.query` 的值全是字符串**：永远记得用 `parseInt()`、`Number()` 或 `parseFloat()` 转换。`'3' === 3` 是 `false`。

3. **`app.use()` 前缀拼接**：`app.use('/api/articles', router)` 会自动把 `/api/articles` 作为前缀加到 `router` 内部的所有路径前面。`router` 里不要重复写 `/api/articles`，只写相对路径即可。

4. **同一个 URL 不同方法 = 不同路由**：`GET /api/test` 和 `POST /api/test` 是完全独立的两条路由，需要分别定义。没定义的方法会返回 404。

5. **URL 大小写**：`/api/Articles` 和 `/api/articles` 是**不同的路径**。保持全小写，避免混乱。

6. **不要在 URL 中使用动词**：`/api/getArticles` 是错误的 RESTful 设计。动词应体现在 HTTP 方法中，而不是 URL 中。

---

## 九、下一步建议

路由系统你已经完全掌握了。但有一个问题你肯定发现了——POST 和 PUT 请求还没有真正接收用户传过来的数据。接下来：

- **下一章**：[06-中间件：流水线上的工人](06-中间件：流水线上的工人.md)——学习 Express 中间件机制，用 `express.json()` 解析请求体，用自定义中间件记录日志，用第三方中间件 morgan 和 cors 给项目加装专业装备。
- **延伸思考**：你现在的 `GET /api/articles` 返回了 `{page, limit, total, data}` 格式，`GET /api/articles/:id` 却只返回文章对象。这种格式不统一的问题，会在第 08 章统一解决。

---

> 📊 本教程无可视化
>
> 本教程编辑记录：2026-06-12 初始版本。