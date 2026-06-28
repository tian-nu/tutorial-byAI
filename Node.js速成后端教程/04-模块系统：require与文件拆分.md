# 04-模块系统：require 与文件拆分

> "所有代码塞一个文件 = 所有衣服塞一个箱子。这一章我们学会 Node.js 的模块系统——用 `require` 和 `module.exports` 把代码拆成多个文件，让项目结构清晰起来。"

---

## 一、目标与完成效果

**一句话目标**：理解 Node.js 的 CommonJS 模块系统，学会用 `require` 引入模块、用 `module.exports` 导出模块，把路由从 `server.js` 拆分到独立的 `routes/` 文件夹中。

**完成后的可观测效果**：
- 你的 `blog-backend/` 目录下多了一个 `routes/` 文件夹，里面有 `articles.js`。
- `server.js` 从 15 行瘦身到了 10 行左右，路由逻辑搬到了 `routes/articles.js`。
- 访问 `http://localhost:3000/api/articles` 返回 JSON 数据——功能完全不变，但代码结构清晰了 10 倍。

---

## 二、前置条件

| 序号 | 条件 | 验证命令 |
|------|------|----------|
| 1 | 已完成教程 03，`server.js` 能跑起来 | `npm run dev` 能正常启动 |
| 2 | 理解 `require('express')` 的基本含义 | 知道它在加载 Express 包 |
| 3 | 理解 JavaScript 对象和函数的基本概念 | 能看懂 `{ key: 'value' }` 和 `function() {}` |

**一条命令确认前置满足**：

```bash
npm run dev
```

终端输出 "Server is running on http://localhost:3000"，且浏览器访问 `http://localhost:3000/api/hello` 返回 `{"message":"Hello API"}`，前置条件满足。

---

## 三、分步操作

### 步骤 1：为什么需要模块——"所有代码写一个文件 = 所有衣服塞一个箱子"

先看看你现在的 `server.js`：

```javascript
const express = require('express');
const app = express();

app.get('/', (req, res) => {
    res.send('你好，世界！');
});

app.get('/api/hello', (req, res) => {
    res.json({ message: 'Hello API' });
});

app.listen(3000, () => {
    console.log('Server is running on http://localhost:3000');
});
```

现在只有 2 个路由，看起来还行。但想象一下 30 个路由之后：

```javascript
// 噩梦版 server.js（不需要真的写，感受一下）
app.get('/api/articles', ...);
app.get('/api/articles/:id', ...);
app.post('/api/articles', ...);
app.put('/api/articles/:id', ...);
app.delete('/api/articles/:id', ...);
app.post('/api/auth/register', ...);
app.post('/api/auth/login', ...);
app.get('/api/comments', ...);
app.post('/api/comments', ...);
// ... 还有 20 个路由
```

**一个文件几百行，翻来翻去找不到，改一个地方影响全局，多人协作天天冲突。**

这就是我们需要"模块系统"的原因。Node.js 的模块系统让你能把代码拆成多个文件，每个文件负责一个独立的功能。

**比喻**：把代码拆分 = 把衣服分类放到不同的抽屉里。内衣一个抽屉、T恤一个抽屉、裤子一个抽屉——找起来方便，洗的时候也不会搞混。

---

### 步骤 2：`require('./xxx')` vs `require('express')`——自己写的 vs npm 下载的

在 Node.js 中，`require()` 是加载模块的唯一方式。但 `require()` 根据参数的不同，有两种完全不同的行为：

| 写法 | 含义 | 去哪找 |
|------|------|--------|
| `require('express')` | 加载 npm 下载的包 | `node_modules/express/` |
| `require('./routes/articles')` | 加载你自己写的文件 | 当前目录下的 `routes/articles.js` |
| `require('../utils')` | 加载上级目录的文件 | 上级目录下的 `utils.js` |

**判断规则**：
- 以 `./` 或 `../` 开头 → 你**自己写的文件**（相对路径）
- 不以 `./` 或 `../` 开头 → **npm 包**（从 `node_modules/` 里找）或 **Node.js 内置模块**（如 `fs`、`path`、`http`）

> 🔥 **魔鬼细节**：`require('./xxx')` 前面的 `./` **不能省略**。如果写成 `require('routes/articles')`，Node.js 会去 `node_modules/` 里找，找不到就报错。`./` 的意思是"从当前目录开始找"。

---

### 步骤 3：`module.exports`——把函数/对象"导出"给其他文件用

在 Node.js 中，每个文件都是一个**独立的模块**。模块内部的变量和函数默认是**私有的**——其他文件看不见。

那怎么让其他文件能用呢？用 `module.exports`。

#### 最简单的例子

创建两个文件来理解 `module.exports` 和 `require` 的关系：

**`math.js`**（导出模块）：

```javascript
// 定义一个加法函数
function add(a, b) {
    return a + b;
}

// 定义一个乘法函数
function multiply(a, b) {
    return a * b;
}

// 导出：告诉 Node.js "这两个函数可以被其他文件使用"
module.exports = {
    add: add,
    multiply: multiply
};
```

**`app.js`**（导入模块）：

```javascript
// 引入 math.js 导出的内容
const math = require('./math');

console.log(math.add(2, 3));       // 输出：5
console.log(math.multiply(2, 3));  // 输出：6
```

#### 比喻：`module.exports` = 餐厅的"对外菜单"

你在厨房（`math.js`）里可能做了很多菜，但只有写在菜单（`module.exports`）上的菜，客人（其他文件）才能点。厨房里的私房菜（没导出的函数），客人看不到也点不了。

#### 三种导出方式

```javascript
// 方式一：导出一个对象（最常用）
module.exports = {
    add,
    multiply
};

// 方式二：逐个挂载属性
module.exports.add = add;
module.exports.multiply = multiply;

// 方式三：直接导出一个函数
module.exports = function() {
    console.log('hello');
};
```

> **方式一和方式二的区别**：方式一**替换**了整个 `module.exports`，方式二是在已有的 `module.exports` 对象上**添加属性**。两种方式不能混用——如果你先用了方式二，又用方式一覆盖，之前添加的属性就丢了。

---

### 步骤 4：实战——创建 `routes/articles.js`，把文章路由拆分出去

现在我们来真正动手。把 `server.js` 里的路由拆到独立文件里。

#### 4.1 创建 `routes/` 文件夹和 `articles.js`

在 `blog-backend/` 目录下创建 `routes/` 文件夹，然后在里面新建 `articles.js`：

```javascript
const express = require('express');
const router = express.Router();

// 模拟文章数据
const articles = [
    { id: 1, title: 'Node.js 入门指南', author: '小明' },
    { id: 2, title: 'Express 框架详解', author: '小红' },
    { id: 3, title: 'RESTful API 设计', author: '小刚' }
];

// GET /api/articles — 获取所有文章
router.get('/', (req, res) => {
    res.json(articles);
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

#### 逐行解释

```javascript
const express = require('express');
```

在这个文件里也要引入 Express——因为我们要用 `express.Router()`。

```javascript
const router = express.Router();
```

**`express.Router()`** 创建了一个"迷你 Express 应用"。它和 `app` 一样可以定义路由（`.get()`、`.post()` 等），但它**不是一个完整的服务器**——它只是一个"路由组"，可以挂载到主应用上。

**比喻**：`app` 是整个餐厅，`router` 是餐厅里的一个"专区"（比如"川菜区"）。`router` 有自己的菜单（路由），但营业还需要挂在整个餐厅下面。

```javascript
router.get('/', (req, res) => {
    res.json(articles);
});
```

在 `router` 上定义路由时，路径是**相对于挂载点的**。如果后面在 `server.js` 里挂载为 `/api/articles`，那么这里的 `'/'` 实际对应的是 `/api/articles`，`'/:id'` 实际对应的是 `/api/articles/:id`。

```javascript
module.exports = router;
```

把 `router` 导出，让 `server.js` 能用 `require()` 引入它。

#### 4.2 修改 `server.js`——挂载路由

现在修改 `server.js`，把原来的路由删掉，改成挂载 `routes/articles.js`：

```javascript
const express = require('express');
const app = express();

// 引入路由模块
const articlesRouter = require('./routes/articles');

// 挂载路由：所有 /api/articles 开头的请求都交给 articlesRouter 处理
app.use('/api/articles', articlesRouter);

// 保留首页路由
app.get('/', (req, res) => {
    res.send('你好，世界！');
});

// 保留 API hello 路由
app.get('/api/hello', (req, res) => {
    res.json({ message: 'Hello API' });
});

app.listen(3000, () => {
    console.log('Server is running on http://localhost:3000');
});
```

#### 逐行解释

```javascript
const articlesRouter = require('./routes/articles');
```

这行代码做了三件事：
1. 找到 `routes/articles.js` 文件
2. 执行这个文件（定义 `router`、添加路由）
3. 把 `module.exports` 导出的内容（即 `router`）赋给 `articlesRouter`

```javascript
app.use('/api/articles', articlesRouter);
```

**`app.use()` 是 Express 中最强大的方法之一。** 这里的意思是："把所有以 `/api/articles` 开头的请求，都转发给 `articlesRouter` 去处理。"

具体来说：
- 请求 `GET /api/articles` → `articlesRouter` 里的 `router.get('/')` 处理
- 请求 `GET /api/articles/1` → `articlesRouter` 里的 `router.get('/:id')` 处理
- 请求 `GET /api/articles/999` → `articlesRouter` 里的 `router.get('/:id')` 处理，返回 404

**比喻**：`app.use('/api/articles', articlesRouter)` 相当于在餐厅里挂了一个指示牌："川菜区请往这边走 →"。客人走到 `/api/articles` 这个入口，后面的路由就都由川菜区（`articlesRouter`）来接待了。

---

### 步骤 5：验证功能

保存所有文件，确认 nodemon 自动重启了服务器。然后测试：

#### 用 Thunder Client 测试

| 请求 | 预期结果 |
|------|----------|
| `GET http://localhost:3000/` | "你好，世界！" |
| `GET http://localhost:3000/api/hello` | `{"message":"Hello API"}` |
| `GET http://localhost:3000/api/articles` | 返回 3 篇文章的 JSON 数组 |
| `GET http://localhost:3000/api/articles/1` | 返回 id=1 的文章 |
| `GET http://localhost:3000/api/articles/999` | 返回 404，`{"error":"文章不存在"}` |

全部通过？恭喜——你刚刚完成了人生中第一次代码拆分！

---

### 🤔 想多一点：`require` 有缓存——同一个模块 require 多次只执行一次

这是一个重要的"魔鬼细节"，理解它对你以后 debug 非常有帮助。

```javascript
// a.js
console.log('a.js 被执行了！');
module.exports = { name: 'a' };
```

```javascript
// b.js
const a1 = require('./a');  // 输出："a.js 被执行了！"
const a2 = require('./a');  // 不输出任何东西
const a3 = require('./a');  // 不输出任何东西

console.log(a1 === a2);  // true —— 是同一个对象！
```

**Node.js 在第一次 `require` 时执行模块代码，把结果缓存起来。后续的 `require` 直接返回缓存的结果，不会重新执行。**

**这意味着什么？**
- ✅ 好处：性能好，不会重复加载同一个模块。
- ⚠️ 注意：如果你修改了模块导出的对象（比如 `a1.name = 'b'`），所有引用这个模块的地方都会看到这个修改——因为大家用的是同一个对象。

**这对你的项目意味着什么？** 你在 `server.js` 里 `require('./routes/articles')` 之后，`articles.js` 里的代码只执行一次。`articles` 数组也是只创建一次。所以所有请求看到的都是同一个 `articles` 数组——这正是我们想要的（模拟数据共享）。

---

### 步骤 6：CommonJS vs ES Modules 简短对比

你可能在别的地方见过 `import` 和 `export` 语法。那是 **ES Modules**（ESM），JavaScript 官方的模块系统。本教程用的是 **CommonJS**（CJS），Node.js 传统的模块系统。

| 对比维度 | CommonJS（本教程用） | ES Modules（ESM） |
|----------|---------------------|-------------------|
| **导入** | `const x = require('./x')` | `import x from './x.js'` |
| **导出** | `module.exports = x` | `export default x` 或 `export { x }` |
| **加载时机** | 运行时同步加载 | 编译时静态分析 |
| **文件后缀** | `.js`（默认） | `.mjs` 或在 `package.json` 中设 `"type": "module"` |
| **Node.js 支持** | 从 Node.js 诞生就支持 | Node.js 12+ 开始稳定支持 |

> **为什么本教程用 CommonJS？** 因为绝大多数现有的 Node.js 教程、示例代码、Stack Overflow 答案都是用 CommonJS 写的。你学会了 CommonJS，看这些资料毫无障碍。而且 Express 的官方文档示例也是 CommonJS。等你熟悉了 Node.js 之后再学 ESM 很容易——核心概念是一样的，只是语法不同。

---

### 步骤 7：`__dirname` 和 `process.cwd()` 的区别

这是两个容易搞混的概念，借这个机会一次讲清楚。

```javascript
console.log(__dirname);       // 当前文件所在的目录（绝对路径）
console.log(process.cwd());   // 你执行 node 命令时所在的目录（当前工作目录）
```

| 属性 | 含义 | 示例 |
|------|------|------|
| `__dirname` | **文件**在哪个目录 | 你在 `d:/project/blog-backend/routes/articles.js` 里写 `__dirname`，永远是 `d:/project/blog-backend/routes` |
| `process.cwd()` | 你从**哪个目录**执行的 `node` | 你在 `d:/project/` 下执行 `node blog-backend/server.js`，`process.cwd()` 就是 `d:/project/` |

**什么时候用哪个？**
- 读取**相对于当前代码文件**的路径（如配置文件、模板文件）→ 用 `__dirname`
- 读取**相对于用户执行命令位置的路径**（如用户指定的输出目录）→ 用 `process.cwd()`

> **本教程中**：暂时不需要直接用到这两个。但后面学文件上传时会用到 `__dirname` 来构建上传目录的绝对路径，先记住这个概念。

---

## 四、完整代码清单

### `blog-backend/server.js`（本章最终状态）

```javascript
const express = require('express');
const app = express();

// 引入路由模块
const articlesRouter = require('./routes/articles');

// 挂载路由
app.use('/api/articles', articlesRouter);

// 首页路由
app.get('/', (req, res) => {
    res.send('你好，世界！');
});

// API 测试路由
app.get('/api/hello', (req, res) => {
    res.json({ message: 'Hello API' });
});

app.listen(3000, () => {
    console.log('Server is running on http://localhost:3000');
});
```

### `blog-backend/routes/articles.js`（本章新建）

```javascript
const express = require('express');
const router = express.Router();

// 模拟文章数据
const articles = [
    { id: 1, title: 'Node.js 入门指南', author: '小明' },
    { id: 2, title: 'Express 框架详解', author: '小红' },
    { id: 3, title: 'RESTful API 设计', author: '小刚' }
];

// GET /api/articles — 获取所有文章
router.get('/', (req, res) => {
    res.json(articles);
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

### `blog-backend/` 目录结构（本章最终状态）

```
blog-backend/
├── server.js
├── package.json
├── package-lock.json
├── .gitignore
├── node_modules/
└── routes/
    └── articles.js
```

---

## 五、验证方法

| 序号 | 操作 | 预期结果 |
|------|------|----------|
| 1 | `npm run dev` | 服务器正常启动，无报错 |
| 2 | `GET http://localhost:3000/` | 返回 "你好，世界！" |
| 3 | `GET http://localhost:3000/api/hello` | 返回 `{"message":"Hello API"}` |
| 4 | `GET http://localhost:3000/api/articles` | 返回 3 篇文章的 JSON 数组 |
| 5 | `GET http://localhost:3000/api/articles/1` | 返回 id=1 的文章 `{"id":1,"title":"Node.js 入门指南","author":"小明"}` |
| 6 | `GET http://localhost:3000/api/articles/999` | 返回 404，`{"error":"文章不存在"}` |

全部通过？代码拆分成功！

---

## 六、小结表格

| 学到的东西 | 一句话解释 |
|-----------|-----------|
| 为什么需要模块 | 一个文件几百行 → 找代码难、改代码怕、协作冲突多 |
| `require('./xxx')` | 加载你自己写的文件，`./` 不能省略 |
| `require('express')` | 加载 npm 下载的包（从 `node_modules/` 里找） |
| `module.exports` | 把文件里的函数/对象"导出"，让其他文件能 `require` 进来用 |
| `express.Router()` | 创建一个"迷你 Express 应用"，负责一组相关路由 |
| `app.use('/path', router)` | 把路由组挂载到主应用上，以 `/path` 为前缀 |
| `require` 缓存机制 | 同一个模块 `require` 多次，只执行一次，返回同一个对象 |
| CommonJS vs ES Modules | 本教程用 CommonJS（`require`/`module.exports`），这是 Node.js 传统模块系统 |
| `__dirname` | 当前代码文件所在的目录路径（绝对路径） |
| `process.cwd()` | 你执行 `node` 命令时所在的目录路径 |

---

## 七、术语附录

| 术语 | 英文 | 通俗解释 | 本章出现位置 | 字面陷阱 |
|------|------|----------|-------------|----------|
| CommonJS | — | Node.js 传统的模块系统规范。用 `require()` 加载模块，用 `module.exports` 导出模块。 | 步骤 6 | 名字里有 "Common"，但不是"通用"的意思——它是"CommonJS 规范"的名称，ES Modules 是另一个规范。 |
| `require` | — | Node.js 中加载模块的函数。可以加载 npm 包、内置模块、或自己写的文件。 | 步骤 2 | 不是"请求"的意思（虽然 HTTP 里也有 request），这里就是"加载/引入模块"。 |
| `module.exports` | — | 每个 Node.js 文件都有的一个特殊对象，你往上面放东西，其他文件 `require` 时就能拿到。 | 步骤 3 | 不是"模块的导出"，而是"模块这个对象上的 exports 属性"。 |
| ES Modules（ESM） | ECMAScript Modules | JavaScript 官方的模块系统，用 `import` 和 `export` 语法。浏览器原生支持，Node.js 12+ 也支持。 | 步骤 6 | 和 CommonJS 是两套不同的系统，语法不兼容。（`.mjs` 文件强制使用 ESM） |
| 作用域（Scope） | Scope | 一个变量或函数"在哪些地方能被访问到"。Node.js 中每个文件是一个独立的作用域——文件内部定义的变量，其他文件看不到。 | 步骤 3 | 不是"作用区域"，是"可见范围"——变量在哪个范围内有效。 |
| `express.Router()` | Router | 创建一个"迷你 Express 应用"，专门用来定义一组路由。可以挂载到主应用上。 | 步骤 4 | 不是网络里的"路由器"硬件，而是一个软件对象，负责"把请求分发到对应的处理函数"。 |
| `__dirname` | — | Node.js 的全局变量，表示当前文件所在的目录的绝对路径。前后各有两个下划线。 | 步骤 7 | 不是 `_dirname`（一个下划线），也不是 `__dirName`（大小写敏感）。 |

---

## 八、已知坑点与禁止事项

1. **`require('./xxx')` 前面的 `./` 不能省略**：这是最高频的错误。`require('routes/articles')` 会被当作 npm 包名，去 `node_modules/` 里找，找不到就报 `Cannot find module`。**必须是 `require('./routes/articles')`。**

2. **文件后缀 `.js` 可以省略，但建议保留**：`require('./routes/articles')` 和 `require('./routes/articles.js')` 都行。但保留 `.js` 后缀更清晰——明确告诉读代码的人"这是一个 JavaScript 文件"，而不是其他类型的文件。

3. **`module.exports` 和 `exports` 的区别**：`exports` 是 `module.exports` 的引用。如果你直接给 `exports` 赋值（`exports = {...}`），不会影响 `module.exports`。所以**永远用 `module.exports`**，不要用 `exports`。

4. **`require` 的缓存可能让你困惑**：如果你修改了 `articles.js` 里的数据，`server.js` 里引用的 `articlesRouter` 不会自动更新——因为 `require` 有缓存。要看到新数据，需要重启服务器。nodemon 在检测到文件变化时会自动重启，所以这个问题通常不会困扰你。

5. **循环引用（A require B，B require A）会导致 bug**：Node.js 会返回一个"不完整"的对象。避免两个文件互相 `require`。如果确实需要共享逻辑，把共享部分抽到第三个文件里。

---

## 九、下一步建议

你的项目结构已经清晰起来了！接下来：

- **下一章**：05-路由进阶：GET/POST/PUT/DELETE 实战（待后续更新）——学习完整的 CRUD 操作，给文章接口加上创建、修改、删除功能。
- **延伸思考**：你现在只有 `routes/articles.js`。如果后面还有 `routes/auth.js`（认证）、`routes/comments.js`（评论），`server.js` 里会变成 3 行 `app.use()`。想想看，能否进一步优化？——答案是：后面会学的"自动路由挂载"模式。

---

> 📊 本教程无可视化
>
> [可暂停点 1/9]：阶段一（上路准备）已完成。你学到了 Node.js 环境搭建、Express 基础、HTTP 请求-响应、模块拆分。下次从第 05 章继续。
>
> 本教程编辑记录：2026-06-12 初始版本。