# 11-异步编程（二）：async/await 与文件操作

> "Promise 链已经比回调地狱好多了，但每个 `.then()` 还是要写一个函数。有没有办法让异步代码看起来像同步代码一样干净？有——`async/await`。这一章，我们用 `async/await` 把 Promise 链进一步简化，用 `fs.promises` 替代回调版的文件操作，搞清楚什么时候用同步、什么时候用异步，最后把 Express 路由升级为 async。"

---

## 一、目标与完成效果

**一句话目标**：掌握 `async/await` 语法，用 `try/catch` 处理异步错误，用 `fs.promises` 进行文件操作，理解同步 vs 异步的适用场景，并将 Express 路由升级为 async 函数。

**完成后的可观测效果**：
- 你能把第 10 章的 Promise 链改写为 `async/await` 版本，代码量减少一半。
- 你知道 `await` 只能在 `async` 函数中使用，以及 CommonJS 中如何绕过顶层 `await` 的限制。
- 你能用 `try/catch` 包裹 `await`，正确处理异步错误。
- 你亲眼看到了忘记 `try/catch` 时 Node.js 的 `UnhandledPromiseRejectionWarning` 警告。
- 你能用 `fs.promises.readFile` 替代回调版的 `fs.readFile`，代码更简洁。
- 你安装并配置了 `express-async-errors`，Express 路由可以安全地使用 `async/await`。
- 你改写了 `routes/articles.js` 中的一个路由为 async 函数。

---

## 二、前置条件

| 序号 | 条件 | 验证命令 |
|------|------|----------|
| 1 | 已完成教程 10，理解 Promise 和 `.then().catch()` 链式调用 | `node sandbox/05-promise-chain.js` 正常运行 |
| 2 | 理解 `try/catch` 的基本用法 | 能看懂 `try { throw new Error('xxx') } catch (err) { console.log(err.message) }` |
| 3 | `blog-backend/` 项目结构完整，CRUD 接口可正常运行 | `npm run dev` 正常启动 |
| 4 | `blog-backend/sandbox/` 目录已存在，里面有教程 10 的演示文件 | `ls sandbox/` 能看到 6 个 `.js` 文件 |

**一条命令确认前置满足**：

```bash
node sandbox/05-promise-chain.js
```

终端输出 `✅ 三层链式调用全部完成！`，前置条件满足。

---

## 三、分步操作

### 步骤 1：async/await——让异步代码看起来像同步

在第 10 章中，我们用 Promise 链把回调地狱变成了扁平的链条：

```javascript
readFilePromise('file-a.txt')
    .then(dataA => {
        return readFilePromise('file-b.txt');
    })
    .then(dataB => {
        return readFilePromise('file-c.txt');
    })
    .then(dataC => {
        console.log(dataC);
    })
    .catch(err => {
        console.log('出错了：', err);
    });
```

虽然比回调地狱好，但每个 `.then()` 还是要写一个函数。有没有办法让它看起来像普通的同步代码？

**有——`async/await`。**

#### 1.1 同样的逻辑，用 async/await 写

```javascript
async function readFileChain() {
    try {
        const dataA = await readFilePromise('file-a.txt');
        const dataB = await readFilePromise('file-b.txt');
        const dataC = await readFilePromise('file-c.txt');
        console.log(dataC);
    } catch (err) {
        console.log('出错了：', err);
    }
}
```

**对比一眼可见**：

| | Promise 链 | async/await |
|------|-----------|-------------|
| 代码行数 | ~10 行 | ~6 行 |
| 嵌套层级 | 链式调用，每个 `.then()` 是新函数 | 完全平铺，像同步代码 |
| 错误处理 | `.catch()` | `try/catch` |
| 变量作用域 | 每个 `.then()` 有独立作用域 | 所有 `await` 结果在同一个作用域 |
| 可读性 | 需要理解 Promise 链 | 看起来就是普通的赋值语句 |

> **关键理解**：`async/await` 不是新东西。它只是 Promise 的"语法糖"——底层还是 Promise，只是写法更友好。`await` 就是"等这个 Promise 完成，把结果给我"。

#### 1.2 语法规则

```javascript
// 规则 1：async 关键字放在 function 前面
async function myFunction() {
    // 规则 2：await 只能在 async 函数中使用
    const result = await somePromise;
    return result;
}

// 规则 3：async 函数自动返回 Promise
myFunction().then(result => {
    console.log(result);
});
```

**餐厅比喻**：`async/await` 就像服务员用了对讲机——不用跑来跑去（`.then()` 链），直接站在岗位上等厨房通知（`await`），但等的时候不影响其他服务员（async 函数不会阻塞事件循环）。

---

### 步骤 2：await 只能在 async 函数里用——新手最常踩的坑

这是每个 Node.js 新手都会遇到的错误。试试看：

#### 2.1 错误示范

创建 `blog-backend/sandbox/07-top-level-await-error.js`：

```javascript
// sandbox/07-top-level-await-error.js — ❌ 顶层 await 错误示范
const fs = require('fs');

// ❌ 错误！await 不能在最外层使用（CommonJS 中）
const data = await fs.promises.readFile('sandbox/01-callback.js', 'utf8');
console.log(data);
```

运行：

```bash
node sandbox/07-top-level-await-error.js
```

**报错**：

```
SyntaxError: await is only valid in async functions
```

> `await` 只能放在 `async function` 内部。在 CommonJS 模块（`require`）的顶层，不能直接使用 `await`。

#### 2.2 解决方案：立即执行异步函数（IIFE）

创建 `blog-backend/sandbox/08-iife-async.js`：

```javascript
// sandbox/08-iife-async.js — ✅ 用立即执行函数包裹 async/await
const fs = require('fs');

// 方法：用立即执行异步函数表达式（IIFE）包裹
(async () => {
    try {
        const data = await fs.promises.readFile('sandbox/01-callback.js', 'utf8');
        console.log('✅ 读取成功，文件前 50 个字符：');
        console.log(data.substring(0, 50));
    } catch (err) {
        console.log('❌ 读取失败：', err.message);
    }
})();

console.log('（这条消息先打印）');
```

运行：

```bash
node sandbox/08-iife-async.js
```

**写法拆解**：

```javascript
(async () => {   // ← 定义一个 async 箭头函数
    // 这里可以用 await
})();            // ← 立即调用它
```

这就是 **IIFE（Immediately Invoked Function Expression，立即执行函数表达式）**。在 CommonJS 中，这是使用顶层 `await` 的标准方式。

> 🔥 **魔鬼细节**：顶层 `await` 在 ES Modules（`.mjs` 文件或 `"type": "module"`）中是可用的。但本教程使用 CommonJS（`require`），所以必须用 IIFE 包裹。如果你看到别人在 `.mjs` 文件中直接写顶层 `await`，不要惊讶——那是 ES Modules 的特性。

---

### 步骤 3：错误处理——try/catch 包裹 await

在第 10 章中，Promise 的错误处理用 `.catch()`。在 `async/await` 中，错误处理用 `try/catch`。

#### 3.1 对比

```javascript
// Promise 风格：.catch()
readFilePromise('file.txt')
    .then(data => console.log(data))
    .catch(err => console.log('出错了：', err));

// async/await 风格：try/catch
async function readFile() {
    try {
        const data = await readFilePromise('file.txt');
        console.log(data);
    } catch (err) {
        console.log('出错了：', err);
    }
}
```

#### 3.2 完整演示

创建 `blog-backend/sandbox/09-try-catch-async.js`：

```javascript
// sandbox/09-try-catch-async.js — async/await 错误处理演示
const fs = require('fs');

async function readFileSafe(filePath) {
    try {
        console.log(`  正在读取：${filePath}`);
        const data = await fs.promises.readFile(filePath, 'utf8');
        console.log(`  ✅ 成功，内容：${data.trim()}`);
        return data;
    } catch (err) {
        console.log(`  ❌ 失败：${err.message}`);
        return null; // 返回 null 表示失败，不中断程序
    }
}

(async () => {
    console.log('=== 示例 1：读取存在的文件 ===');
    await readFileSafe('sandbox/01-callback.js');
    console.log('');

    console.log('=== 示例 2：读取不存在的文件 ===');
    await readFileSafe('sandbox/不存在.txt');
    console.log('');

    console.log('=== 示例 3：读取存在的文件（继续正常执行） ===');
    await readFileSafe('sandbox/02-err-first.js');
    console.log('');

    console.log('✅ 所有操作完成（即使中间有失败，程序也没有崩溃）');
})();
```

运行：

```bash
node sandbox/09-try-catch-async.js
```

**关键点**：即使示例 2 的 `readFileSafe` 失败了，程序继续执行示例 3——因为 `try/catch` 捕获了错误，没有让它冒泡到顶层。

---

### 步骤 4：忘记 try/catch 的后果——UnhandledPromiseRejection

如果不写 `try/catch`，`await` 失败时会怎样？

#### 4.1 演示：忘记 try/catch

创建 `blog-backend/sandbox/10-unhandled-rejection.js`：

```javascript
// sandbox/10-unhandled-rejection.js — ❌ 忘记 try/catch 的后果
const fs = require('fs');

async function readFileNoCatch(filePath) {
    // ❌ 没有 try/catch！
    const data = await fs.promises.readFile(filePath, 'utf8');
    console.log('读取成功：', data);
    return data;
}

(async () => {
    console.log('开始读取（没有 try/catch）...');
    await readFileNoCatch('sandbox/不存在.txt');
    console.log('这行不会执行！');
})();
```

运行：

```bash
node sandbox/10-unhandled-rejection.js
```

**终端输出**：

```
开始读取（没有 try/catch）...
node:internal/process/promises:289
            triggerUncaughtException(err, true /* fromPromise */);
            ^

[Error: ENOENT: no such file or directory, open 'sandbox/不存在.txt'] {
  ...
}

Node.js v20.x.x
```

注意：
1. `这行不会执行！` 确实没有打印——程序崩溃了。
2. 在 Node.js 15+ 中，未捕获的 Promise rejection 会直接导致进程退出（以前只会打印警告）。

#### 4.2 为什么 async 函数中不写 try/catch 会崩溃？

```javascript
async function readFileNoCatch(filePath) {
    const data = await fs.promises.readFile(filePath, 'utf8');
    // 如果上面的 await 失败了（reject），
    // 这个 async 函数会返回一个 rejected 的 Promise
    // 如果没有 .catch() 或 try/catch 处理它，就会变成 UnhandledPromiseRejection
    return data;
}
```

**餐厅比喻**：`async` 函数就像服务员拿了一个托盘——如果菜做好了（resolve），托盘上放着菜；如果菜卖完了（reject），托盘上是一个"出错了"的纸条。如果服务员不检查这个纸条（没有 try/catch），就直接把空托盘端给客人，客人会投诉（进程崩溃）。

> 🔥 **魔鬼细节**：在 Node.js 14 及之前，未捕获的 Promise rejection 只会打印一个 `UnhandledPromiseRejectionWarning` 警告，进程不会退出。从 Node.js 15 开始，未捕获的 rejection 会直接导致进程退出（`exit code 1`）。**所以永远不要忘记 try/catch。**

---

### 步骤 5：文件操作实战——fs.promises 替代回调版 fs

在第 10 章中，我们手动包装了 `fs.readFile` 为 Promise：

```javascript
function readFilePromise(filePath) {
    return new Promise((resolve, reject) => {
        fs.readFile(filePath, 'utf8', (err, data) => {
            if (err) reject(err);
            else resolve(data);
        });
    });
}
```

其实 Node.js 10+ 已经内置了 `fs.promises`——一个返回 Promise 的 fs 版本。你不需要手动包装。

#### 5.1 同步 vs 异步 vs Promise 版——三路对比

创建 `blog-backend/sandbox/11-fs-promises.js`：

```javascript
// sandbox/11-fs-promises.js — fs 三种读取方式对比
const fs = require('fs');

(async () => {
    const filePath = 'sandbox/01-callback.js';

    // ====== 方式一：同步读取（阻塞） ======
    console.log('=== 方式一：fs.readFileSync（同步） ===');
    console.log('A: 开始同步读取');
    const dataSync = fs.readFileSync(filePath, 'utf8');
    console.log('B: 同步读取完成，前 30 个字符：', dataSync.substring(0, 30));
    console.log('C: 注意——A 和 B 之间程序是卡住的\n');

    // ====== 方式二：回调版异步读取 ======
    console.log('=== 方式二：fs.readFile（回调版） ===');
    console.log('A: 开始回调版读取');
    fs.readFile(filePath, 'utf8', (err, data) => {
        if (err) {
            console.log('B: 回调版失败：', err.message);
        } else {
            console.log('B: 回调版完成，前 30 个字符：', data.substring(0, 30));
        }
    });
    console.log('C: 回调版不阻塞，这行在 B 之前打印\n');

    // ====== 方式三：fs.promises（Promise 版） ======
    console.log('=== 方式三：fs.promises.readFile（Promise 版） ===');
    console.log('A: 开始 Promise 版读取');
    try {
        const dataPromise = await fs.promises.readFile(filePath, 'utf8');
        console.log('B: Promise 版完成，前 30 个字符：', dataPromise.substring(0, 30));
    } catch (err) {
        console.log('B: Promise 版失败：', err.message);
    }
    console.log('C: await 之后的代码（等 B 完成才执行）\n');

    console.log('=== 总结 ===');
    console.log('fs.readFileSync  → 同步，阻塞，简单但危险');
    console.log('fs.readFile       → 异步回调，不阻塞，但容易回调地狱');
    console.log('fs.promises.readFile → 异步 Promise，不阻塞，配合 async/await 最优雅');
})();
```

运行：

```bash
node sandbox/11-fs-promises.js
```

#### 5.2 读取配置文件实战

一个真实场景：写一个函数读取 JSON 配置文件，并解析它。

创建 `blog-backend/sandbox/config.json`：

```json
{
    "appName": "博客系统",
    "port": 3000,
    "database": {
        "host": "localhost",
        "name": "blog"
    }
}
```

创建 `blog-backend/sandbox/12-config-reader.js`：

```javascript
// sandbox/12-config-reader.js — 读取配置文件实战
const fs = require('fs');
const path = require('path');

async function loadConfig(configPath) {
    try {
        // 读取文件
        const raw = await fs.promises.readFile(configPath, 'utf8');

        // 解析 JSON
        const config = JSON.parse(raw);

        console.log('✅ 配置加载成功：');
        console.log(`   应用名：${config.appName}`);
        console.log(`   端口：${config.port}`);
        console.log(`   数据库主机：${config.database.host}`);
        console.log(`   数据库名：${config.database.name}`);

        return config;
    } catch (err) {
        if (err.code === 'ENOENT') {
            console.log(`❌ 配置文件不存在：${configPath}`);
        } else if (err instanceof SyntaxError) {
            console.log(`❌ 配置文件 JSON 格式错误：${err.message}`);
        } else {
            console.log(`❌ 读取配置文件失败：${err.message}`);
        }
        return null;
    }
}

(async () => {
    // 读取存在的配置
    const config1 = await loadConfig(path.join(__dirname, 'config.json'));
    console.log('');

    // 读取不存在的配置
    const config2 = await loadConfig(path.join(__dirname, '不存在的配置.json'));
    console.log('');

    // 读取格式错误的 JSON（如果存在）
    console.log('（可以尝试修改 config.json 使其 JSON 格式错误，看 catch 分支如何区分不同错误）');
})();
```

运行：

```bash
node sandbox/12-config-reader.js
```

**关键技巧**：在 `catch` 中通过 `err.code === 'ENOENT'` 区分"文件不存在"和"其他 I/O 错误"，通过 `err instanceof SyntaxError` 区分"JSON 解析失败"和"其他错误"。这就是**精确的错误分类处理**。

---

### 步骤 6：什么时候用同步，什么时候用异步

不是所有情况都必须用异步。有些场景用同步更合适。关键规则：

#### 简单规则

| 场景 | 用同步还是异步 | 原因 |
|------|---------------|------|
| **启动时读配置文件** | ✅ 同步 OK | 只执行一次，阻塞几十毫秒无所谓 |
| **处理用户请求时读文件** | ❌ 必须异步 | 如果同步，所有用户都会被阻塞 |
| **循环中读很多文件** | ❌ 必须异步 | 同步读 1000 个文件，阻塞时间累加 |
| **写日志** | ✅ 异步（推荐） | 日志不应该阻塞业务逻辑 |
| **CLI 工具（一次性脚本）** | ✅ 同步 OK | 脚本运行完就退出，阻塞不影响并发 |

#### 直观对比

```javascript
// ✅ 启动时读配置——同步 OK
const config = JSON.parse(fs.readFileSync('config.json', 'utf8'));
// 服务器启动只需要 50ms，阻塞 5ms 读配置完全没问题

// ❌ 请求处理中读文件——必须异步
app.get('/api/report', async (req, res) => {
    // 如果这里用 readFileSync，读一个 100MB 的文件需要 3 秒
    // 这 3 秒内，所有其他用户的请求都会被阻塞！
    const data = await fs.promises.readFile('report.csv', 'utf8');
    res.json({ data });
});
```

**餐厅比喻**：厨师在开门前准备食材（启动时读配置）——慢慢来，不着急，客人还没来。但客人点菜后（请求处理中），厨师必须用高压锅快速做菜——不能慢，因为客人在等。

> 🔥 **魔鬼细节**：`fs.existsSync` vs `fs.exists`——检查文件是否存在也有同步/异步之分。`fs.existsSync(path)` 是同步的，`fs.exists(path, callback)` 是异步的（但已被废弃，推荐用 `fs.access` 替代）。最简单的方法：直接用 `try { await fs.promises.access(path) } catch { /* 不存在 */ }`。

---

### 步骤 7：把 Express 路由改为 async

现在把你学到的 `async/await` 应用到博客项目中。目前你的路由都是同步的（没有真正访问数据库或文件），但下一阶段引入数据库后，所有操作都将是异步的。**现在先学会怎么把路由改为 async。**

#### 7.1 Express 4 的 async 陷阱

Express 4 **不会自动捕获** async 路由处理函数中抛出的错误。来看一个例子：

```javascript
// ❌ Express 4 中，这个错误不会被 errorHandler 捕获！
router.get('/:id', async (req, res) => {
    const article = await someAsyncOperation();
    if (!article) {
        throw new AppError('文章不存在', 404);  // 这个错误会丢失！
    }
    res.json({ success: true, data: article });
});
```

如果 `throw new AppError(...)` 被执行，Express 4 不会把这个错误传给 `errorHandler`，请求会一直挂起直到超时。

#### 7.2 解决方案：express-async-errors

安装：

```bash
npm install express-async-errors
```

然后在 `server.js` 的最顶部引入（**必须在 `express` 之前**）：

```javascript
require('express-async-errors');  // ← 必须在第一行
const express = require('express');
// ...
```

**这个包做了什么？** 它给 Express 的所有路由处理函数自动包裹了一层 `try/catch`，所以你在 async 路由中 `throw` 的错误会被自动传给 `errorHandler`。你不需要手动写 `try/catch` 了。

#### 7.3 修改 server.js

打开 `server.js`，在最顶部添加 `require('express-async-errors')`：

```javascript
// server.js
require('express-async-errors');  // ← 新增：必须在 express 之前！

const express = require('express');
const app = express();

// ... 中间件配置 ...
// ... 路由挂载 ...
// ... 404 兜底 ...
// ... errorHandler ...

app.listen(3000, () => {
    console.log('Server is running on http://localhost:3000');
});
```

#### 7.4 把 routes/articles.js 中的一个路由改为 async

我们以 `GET /api/articles/:id` 为例，把它改为 async 函数。现在虽然它还是同步的，但改成 async 后，为下一阶段引入数据库做好准备。

打开 `routes/articles.js`，找到 `GET /:id` 路由，改为：

```javascript
// GET /api/articles/:id — 获取单篇文章（async 版）
router.get('/:id', async (req, res) => {    // ← 加 async
    const article = articles.find(a => a.id === req.params.id);
    // 注意：req.params.id 现在是 UUID 字符串，不需要 parseInt
    if (!article) {
        throw new AppError('文章不存在', 404);
        // ↑ 因为 express-async-errors，这个 throw 会被 errorHandler 捕获
    }
    res.json({
        success: true,
        data: article
    });
});
```

**变化**：
- `(req, res) => {` → `async (req, res) => {`
- 其他代码完全不变——因为 `throw new AppError(...)` 在 async 函数中也能正常工作（有 `express-async-errors` 加持）。

#### 7.5 验证

1. 启动服务器：`npm run dev`
2. 用 Thunder Client 发 `GET /api/articles/a1b2c3d4-e5f6-7890-abcd-ef1234567890`（一个存在的 ID）
3. 预期：返回 200，文章数据正常
4. 发 `GET /api/articles/nonexistent-id`
5. 预期：返回 404，`{ success: false, error: { message: "文章不存在", code: "NOT_FOUND" } }`

> 如果第 5 步返回的是 HTML 而不是 JSON，说明 `express-async-errors` 没有正确配置。检查 `server.js` 第一行是否 `require('express-async-errors')`，且是否在 `const express = require('express')` 之前。

---

### 🤔 想多一点：async 函数自动返回 Promise——这意味着什么？

```javascript
async function getValue() {
    return 42;
}

// 等价于：
function getValue() {
    return Promise.resolve(42);
}
```

**这意味着**：
- 你可以对 `async` 函数使用 `.then()` 和 `.catch()`。
- 如果你在 Express 路由中返回了一个值，Express 不会把它当响应——因为 `async` 函数返回的是 Promise，Express 会忽略 Promise 的返回值。
- 所以，在 Express 路由中，你仍然需要显式调用 `res.json()` 或 `res.send()`。

```javascript
// ❌ 错误示范——返回了 Promise，Express 不会把它当响应
router.get('/data', async (req, res) => {
    return { hello: 'world' };  // 客户端什么也收不到
});

// ✅ 正确写法——显式调用 res.json()
router.get('/data', async (req, res) => {
    res.json({ hello: 'world' });
});
```

---

### ❌ 常见错误 → ✅ 解决方案

| 错误信息 / 现象 | 原因 | 解决 |
|-----------------|------|------|
| `SyntaxError: await is only valid in async functions` | 在非 async 函数中使用了 `await` | 给函数加 `async` 关键字，或用 IIFE 包裹 |
| `UnhandledPromiseRejectionWarning` | async 函数中 `await` 失败了但没有 `try/catch` | 给 `await` 加 `try/catch`，或确保最外层有 `.catch()` |
| async 路由中 `throw` 错误，客户端一直转圈 | Express 4 不自动捕获 async 错误 | 安装 `express-async-errors` 并在 `server.js` 顶部引入 |
| `fs.promises` 是 `undefined` | Node.js 版本太低（< 10） | 升级到 Node.js 18+，或手动用 `require('fs').promises` |
| `fs.promises.readFile` 返回 Buffer 而不是字符串 | 忘记传 `'utf8'` 编码参数 | `fs.promises.readFile(path, 'utf8')` |
| `JSON.parse` 报错导致整个程序崩溃 | 文件内容不是合法 JSON | 用 `try/catch` 包裹 `JSON.parse`，区分 `SyntaxError` |
| async 函数中 `return` 了一个值，但客户端收不到 | Express 不会处理 async 函数的返回值 | 始终用 `res.json()` 或 `res.send()` 发送响应 |
| `express-async-errors` 装了但没生效 | 放在了 `const express = require('express')` 之后 | 必须在 `require('express')` 之前引入 |

---

## 四、完整代码清单

### `blog-backend/sandbox/07-top-level-await-error.js`（本章新建，仅演示错误）

```javascript
// sandbox/07-top-level-await-error.js — ❌ 顶层 await 错误示范
const fs = require('fs');

// ❌ 错误！await 不能在最外层使用（CommonJS 中）
const data = await fs.promises.readFile('sandbox/01-callback.js', 'utf8');
console.log(data);
```

> 这个文件运行会报错，目的是让读者亲眼看到错误信息。

### `blog-backend/sandbox/08-iife-async.js`（本章新建）

```javascript
// sandbox/08-iife-async.js — ✅ 用立即执行函数包裹 async/await
const fs = require('fs');

// 方法：用立即执行异步函数表达式（IIFE）包裹
(async () => {
    try {
        const data = await fs.promises.readFile('sandbox/01-callback.js', 'utf8');
        console.log('✅ 读取成功，文件前 50 个字符：');
        console.log(data.substring(0, 50));
    } catch (err) {
        console.log('❌ 读取失败：', err.message);
    }
})();

console.log('（这条消息先打印）');
```

### `blog-backend/sandbox/09-try-catch-async.js`（本章新建）

```javascript
// sandbox/09-try-catch-async.js — async/await 错误处理演示
const fs = require('fs');

async function readFileSafe(filePath) {
    try {
        console.log(`  正在读取：${filePath}`);
        const data = await fs.promises.readFile(filePath, 'utf8');
        console.log(`  ✅ 成功，内容：${data.trim()}`);
        return data;
    } catch (err) {
        console.log(`  ❌ 失败：${err.message}`);
        return null;
    }
}

(async () => {
    console.log('=== 示例 1：读取存在的文件 ===');
    await readFileSafe('sandbox/01-callback.js');
    console.log('');

    console.log('=== 示例 2：读取不存在的文件 ===');
    await readFileSafe('sandbox/不存在.txt');
    console.log('');

    console.log('=== 示例 3：读取存在的文件（继续正常执行） ===');
    await readFileSafe('sandbox/02-err-first.js');
    console.log('');

    console.log('✅ 所有操作完成（即使中间有失败，程序也没有崩溃）');
})();
```

### `blog-backend/sandbox/10-unhandled-rejection.js`（本章新建）

```javascript
// sandbox/10-unhandled-rejection.js — ❌ 忘记 try/catch 的后果
const fs = require('fs');

async function readFileNoCatch(filePath) {
    // ❌ 没有 try/catch！
    const data = await fs.promises.readFile(filePath, 'utf8');
    console.log('读取成功：', data);
    return data;
}

(async () => {
    console.log('开始读取（没有 try/catch）...');
    await readFileNoCatch('sandbox/不存在.txt');
    console.log('这行不会执行！');
})();
```

> 这个文件运行会崩溃，目的是让读者亲眼看到未捕获 rejection 的后果。

### `blog-backend/sandbox/11-fs-promises.js`（本章新建）

```javascript
// sandbox/11-fs-promises.js — fs 三种读取方式对比
const fs = require('fs');

(async () => {
    const filePath = 'sandbox/01-callback.js';

    // ====== 方式一：同步读取（阻塞） ======
    console.log('=== 方式一：fs.readFileSync（同步） ===');
    console.log('A: 开始同步读取');
    const dataSync = fs.readFileSync(filePath, 'utf8');
    console.log('B: 同步读取完成，前 30 个字符：', dataSync.substring(0, 30));
    console.log('C: 注意——A 和 B 之间程序是卡住的\n');

    // ====== 方式二：回调版异步读取 ======
    console.log('=== 方式二：fs.readFile（回调版） ===');
    console.log('A: 开始回调版读取');
    fs.readFile(filePath, 'utf8', (err, data) => {
        if (err) {
            console.log('B: 回调版失败：', err.message);
        } else {
            console.log('B: 回调版完成，前 30 个字符：', data.substring(0, 30));
        }
    });
    console.log('C: 回调版不阻塞，这行在 B 之前打印\n');

    // ====== 方式三：fs.promises（Promise 版） ======
    console.log('=== 方式三：fs.promises.readFile（Promise 版） ===');
    console.log('A: 开始 Promise 版读取');
    try {
        const dataPromise = await fs.promises.readFile(filePath, 'utf8');
        console.log('B: Promise 版完成，前 30 个字符：', dataPromise.substring(0, 30));
    } catch (err) {
        console.log('B: Promise 版失败：', err.message);
    }
    console.log('C: await 之后的代码（等 B 完成才执行）\n');

    console.log('=== 总结 ===');
    console.log('fs.readFileSync  → 同步，阻塞，简单但危险');
    console.log('fs.readFile       → 异步回调，不阻塞，但容易回调地狱');
    console.log('fs.promises.readFile → 异步 Promise，不阻塞，配合 async/await 最优雅');
})();
```

### `blog-backend/sandbox/config.json`（本章新建）

```json
{
    "appName": "博客系统",
    "port": 3000,
    "database": {
        "host": "localhost",
        "name": "blog"
    }
}
```

### `blog-backend/sandbox/12-config-reader.js`（本章新建）

```javascript
// sandbox/12-config-reader.js — 读取配置文件实战
const fs = require('fs');
const path = require('path');

async function loadConfig(configPath) {
    try {
        const raw = await fs.promises.readFile(configPath, 'utf8');
        const config = JSON.parse(raw);

        console.log('✅ 配置加载成功：');
        console.log(`   应用名：${config.appName}`);
        console.log(`   端口：${config.port}`);
        console.log(`   数据库主机：${config.database.host}`);
        console.log(`   数据库名：${config.database.name}`);

        return config;
    } catch (err) {
        if (err.code === 'ENOENT') {
            console.log(`❌ 配置文件不存在：${configPath}`);
        } else if (err instanceof SyntaxError) {
            console.log(`❌ 配置文件 JSON 格式错误：${err.message}`);
        } else {
            console.log(`❌ 读取配置文件失败：${err.message}`);
        }
        return null;
    }
}

(async () => {
    const config1 = await loadConfig(path.join(__dirname, 'config.json'));
    console.log('');

    const config2 = await loadConfig(path.join(__dirname, '不存在的配置.json'));
    console.log('');

    console.log('（可以尝试修改 config.json 使其 JSON 格式错误，看 catch 分支如何区分不同错误）');
})();
```

### `blog-backend/server.js` 改动（本章更新）

```javascript
// server.js — 在文件最顶部添加
require('express-async-errors');

const express = require('express');
// ... 其余代码不变
```

### `blog-backend/routes/articles.js` 改动（本章更新——仅 `GET /:id` 路由）

```javascript
// GET /api/articles/:id — 获取单篇文章（async 版）
router.get('/:id', async (req, res) => {
    const article = articles.find(a => a.id === req.params.id);
    if (!article) {
        throw new AppError('文章不存在', 404);
    }
    res.json({
        success: true,
        data: article
    });
});
```

### `blog-backend/` 目录结构（本章新增）

```
blog-backend/
├── server.js                        ← 本章修改：顶部添加 require('express-async-errors')
├── package.json                     ← 本章修改：新增 express-async-errors 依赖
├── ...
├── sandbox/
│   ├── 01-callback.js               ← 第 10 章
│   ├── 02-err-first.js              ← 第 10 章
│   ├── 03-callback-hell.js          ← 第 10 章
│   ├── 04-promise-basic.js          ← 第 10 章
│   ├── 05-promise-chain.js          ← 第 10 章
│   ├── 06-promise-all.js            ← 第 10 章
│   ├── 07-top-level-await-error.js  ← 本章新建（演示错误）
│   ├── 08-iife-async.js             ← 本章新建
│   ├── 09-try-catch-async.js        ← 本章新建
│   ├── 10-unhandled-rejection.js    ← 本章新建（演示崩溃）
│   ├── 11-fs-promises.js            ← 本章新建
│   ├── 12-config-reader.js          ← 本章新建
│   ├── config.json                  ← 本章新建
│   └── data/
│       ├── file-a.txt
│       ├── file-b.txt
│       └── file-c.txt
```

---

## 五、验证方法

| 序号 | 操作 | 预期结果 |
|------|------|----------|
| 1 | `node sandbox/07-top-level-await-error.js` | 报错 `SyntaxError: await is only valid in async functions` |
| 2 | `node sandbox/08-iife-async.js` | `✅ 读取成功` + 文件前 50 个字符；`（这条消息先打印）` 先输出 |
| 3 | `node sandbox/09-try-catch-async.js` | 示例 1 成功，示例 2 显示 `❌ 失败`，示例 3 成功，最终 `✅ 所有操作完成` |
| 4 | `node sandbox/10-unhandled-rejection.js` | 程序崩溃，`这行不会执行！` 没有打印 |
| 5 | `node sandbox/11-fs-promises.js` | 三种方式都输出，`C` 在 `B` 之前（回调版），`await` 版 `C` 在 `B` 之后 |
| 6 | `node sandbox/12-config-reader.js` | 示例 1 显示配置信息，示例 2 显示 `❌ 配置文件不存在` |
| 7 | `npm install express-async-errors` | 安装成功，`package.json` 中新增依赖 |
| 8 | `npm run dev` 启动后，`GET /api/articles/nonexistent-id` | 返回 404 JSON 格式（不是 HTML），证明 `express-async-errors` 生效 |

全部通过？你已经掌握了 async/await 和文件操作。

---

## 六、小结表格

| 学到的东西 | 一句话解释 |
|-----------|-----------|
| `async/await` | Promise 的语法糖——让异步代码看起来像同步代码，底层还是 Promise |
| `async` 关键字 | 放在 `function` 前面，函数自动返回 Promise |
| `await` 关键字 | 等一个 Promise 完成，把结果取出来；只能在 `async` 函数中使用 |
| 顶层 `await` 限制 | CommonJS 中不能在最外层用 `await`，用 IIFE（立即执行异步函数）包裹 |
| `try/catch` 包裹 `await` | async/await 的错误处理方式，等价于 Promise 的 `.catch()` |
| `UnhandledPromiseRejection` | 忘记 `try/catch` 时，Node.js 15+ 会直接崩溃（以前只警告） |
| `fs.promises` | Node.js 10+ 内置的 Promise 版 fs，不需要手动包装回调 |
| `fs.promises.readFile(path, 'utf8')` | 异步读取文件并返回 Promise，配合 `await` 使用最优雅 |
| 同步 vs 异步选择 | 启动时读配置 → 同步 OK；请求处理中 → 必须异步 |
| `express-async-errors` | 让 Express 4 自动捕获 async 路由中的错误，不需要手动 `try/catch` |
| async 路由 | 路由处理函数加 `async`，配合 `express-async-errors`，`throw` 的错误会被 `errorHandler` 捕获 |
| 错误分类处理 | `err.code === 'ENOENT'` 区分文件不存在，`err instanceof SyntaxError` 区分 JSON 格式错误 |

---

## 七、术语附录

| 术语 | 英文 | 通俗解释 | 本章出现位置 | 字面陷阱 |
|------|------|----------|-------------|----------|
| `async` | Asynchronous（关键字） | JavaScript 关键字，放在函数前面，让函数自动返回 Promise。`async function f() { return 1 }` 等价于 `function f() { return Promise.resolve(1) }`。 | 步骤 1 | 不是"异步"本身——它是一个关键字，标记函数可以使用 `await`。 |
| `await` | Await（关键字） | JavaScript 关键字，等一个 Promise 完成，把结果取出来。`const data = await promise` 就是"等 promise 完成，把结果赋给 data"。 | 步骤 1 | 不是"等待"——虽然英文是"等待"，但它不会阻塞事件循环，只是暂停当前 async 函数的执行。 |
| `try/catch` | Try/Catch | JavaScript 的错误处理语句。`try { ... } catch (err) { ... }`——尝试执行 try 中的代码，如果出错就跳到 catch 中处理。 | 步骤 3 | 不是"尝试抓住"——是"尝试执行，捕获错误"。 |
| fs 模块 | File System | Node.js 的内置模块，提供文件操作功能。`require('fs')` 即可使用。 | 步骤 5 | 不是"fs" = "发送"——是 File System 的缩写。 |
| `fs.promises` | File System Promises | fs 模块的 Promise 版本，所有方法返回 Promise 而不是用回调。Node.js 10+ 内置。 | 步骤 5 | 不是"fs 的承诺"——是 fs 模块的一个子对象，包含返回 Promise 的方法。 |
| Promise rejection | — | Promise 的失败状态（rejected）。当 `reject()` 被调用或 `throw` 发生在 Promise 中时，Promise 进入 rejected 状态。 | 步骤 4 | 不是"拒绝"——是"操作失败"的意思。 |
| `UnhandledPromiseRejection` | — | 未处理的 Promise rejection——Promise 失败了，但没有 `.catch()` 或 `try/catch` 处理它。Node.js 15+ 会直接导致进程退出。 | 步骤 4 | 不是"没处理"——是"没有处理程序（handler）"。加上 `.catch()` 或 `try/catch` 就变成 "handled" 了。 |
| IIFE | Immediately Invoked Function Expression | "立即执行函数表达式"——定义一个函数并立刻调用它。`(function() { ... })()`。在 CommonJS 中用来绕过顶层 `await` 限制。 | 步骤 2 | 不是"IIFE 是什么新东西"——就是"定义并立刻执行"的函数，JavaScript 的老模式。 |
| `express-async-errors` | — | 一个 npm 包，让 Express 4 自动捕获 async 路由中抛出的错误。只需在 `server.js` 顶部 `require` 一次。 | 步骤 7 | 不是"Express 的异步错误"——是"让 Express 能处理异步错误"的包。 |
| `ENOENT` | Error NO ENTry | 文件系统的错误码，表示"文件或目录不存在"。第 10 章已出现过，本章在错误分类中再次使用。 | 步骤 5 | 第 10 章已解释。本章强调：可以在 `catch` 中通过 `err.code === 'ENOENT'` 精确判断。 |

---

## 八、已知坑点与禁止事项

1. **`await` 只能在 `async` 函数中使用**：CommonJS 中顶层不能直接写 `await`。用 IIFE 包裹：`(async () => { ... })()`。

2. **Express 4 不自动捕获 async 路由中的错误**：必须安装 `express-async-errors`，且在 `server.js` 最顶部（`require('express')` 之前）引入。

3. **`async` 函数自动返回 Promise**：在 Express 路由中，`return` 一个值不会发送给客户端。必须显式调用 `res.json()` 或 `res.send()`。

4. **忘记 `try/catch` 会导致进程崩溃**：Node.js 15+ 中，未捕获的 Promise rejection 直接导致进程退出。永远给 `await` 加 `try/catch`，或确保有 `express-async-errors` 兜底。

5. **`fs.promises.readFile` 不传编码返回 Buffer**：如果不传 `'utf8'`，返回的是 `Buffer` 对象（二进制数据），不是字符串。始终传 `'utf8'` 除非你需要二进制数据。

6. **`fs.existsSync` 是同步的，`fs.exists` 已被废弃**：检查文件是否存在，用 `try { await fs.promises.access(path) } catch { /* 不存在 */ }`，或者用 `fs.existsSync`（仅限启动时）。

7. **不要在请求处理函数中使用同步文件操作**：`fs.readFileSync` 会阻塞整个 Node.js 进程。在请求处理中只用 `fs.promises.readFile` 或其他异步 API。

8. **`express-async-errors` 不是万能的**：它只给 Express 的路由处理函数加 `try/catch`。如果你在中间件或定时器中用了 async 函数，仍然需要手动 `try/catch`。

---

## 九、下一步建议

你已经掌握了 Node.js 异步编程的全部核心知识——回调、Promise、async/await、文件操作。下一阶段，我们将进入数据库的世界：

- **下一阶段（教程 12-16）**：引入 SQLite 数据库——学 SQL 语句、建表、在 Node.js 中连接数据库、把 CRUD 接口从内存版升级到数据库版。你之前写的所有异步知识，都会在数据库操作中大量使用。
- **延伸思考**：你现在可以把 `routes/articles.js` 中所有路由都改为 async 函数。虽然现在它们还是同步的，但改完后，下一阶段引入数据库时只需要改数据操作部分，路由结构不用动。

---

> 📊 本教程无可视化
>
> 本教程编辑记录：2026-06-12 初始版本。