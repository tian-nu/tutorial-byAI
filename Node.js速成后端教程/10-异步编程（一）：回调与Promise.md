# 10-异步编程（一）：回调与 Promise

> "异步编程是 Node.js 的灵魂。如果你不理解异步，你就永远无法真正理解 Node.js。这一章，我们用打电话 vs 发短信的比喻入门，用餐厅服务员的故事理解事件循环，用回调地狱的惨状让你心甘情愿拥抱 Promise。学完这一章，你会知道——为什么 Node.js 能同时处理成千上万个请求，而 Python 的多线程却那么费劲。"

---

## 一、目标与完成效果

**一句话目标**：理解同步与异步的本质区别，掌握 Node.js 的回调函数模式与 err 优先约定，亲眼见证回调地狱的可怕，学会用 Promise 链式调用改写嵌套回调，并理解事件循环的直观原理。

**完成后的可观测效果**：
- 你能用自己的话解释"同步 = 打电话、异步 = 发短信"的比喻。
- 你能写出 `fs.readFile` 的回调版代码，并理解 `(err, data) => { ... }` 的参数约定。
- 你亲手写出了三层嵌套的回调地狱代码，理解了为什么需要 Promise。
- 你能用 `new Promise((resolve, reject) => { ... })` 创建 Promise，用 `.then().catch()` 链式调用。
- 你能用 `Promise.all()` 并行读取三个文件。
- 你理解了事件循环的一句话解释 + ASCII 图。
- 你的 `blog-backend/sandbox/` 目录下有可运行的演示文件。

---

## 二、前置条件

| 序号 | 条件 | 验证命令 |
|------|------|----------|
| 1 | 已完成教程 09，`blog-backend/` 项目结构完整，CRUD 接口可正常运行 | `npm run dev` 正常启动 |
| 2 | 理解 JavaScript 函数的基本概念（能定义函数、把函数作为参数传递） | 能看懂 `function doSomething(callback) { callback(); }` |
| 3 | 理解 `try/catch` 的基本用法 | 能看懂 `try { ... } catch (err) { ... }` |
| 4 | 会用终端 `cd` 和 `node` 命令 | 能 `node sandbox/01-callback.js` 运行文件 |

**一条命令确认前置满足**：

```bash
npm run dev
```

终端输出 "Server is running on http://localhost:3000"，`Ctrl+C` 退出，前置条件满足。

---

## 三、分步操作

### 步骤 1：打电话 vs 发短信——理解同步与异步

这是理解异步编程最关键的一步。请先放下代码，想象两个场景。

#### 同步 = 打电话

```
你拨号 → 等待对方接听 → 对方接了 → 你们聊天 → 挂断
         ↑ 这段时间你什么也做不了，只能等着
```

- 你只能做一件事：打电话。
- 电话没接通之前，你不能发邮件、不能写代码、不能做任何其他事。
- **一个人在同一时间只能做一件事**。

#### 异步 = 发短信

```
你发短信 → 放下手机 → 写代码 → 吃饭 → 手机响了 → 看回复
           ↑ 发完就放下了，不等着
```

- 发完短信后，你可以做任何其他事情。
- 对方回复时，你收到通知，再处理回复。
- **一个人可以同时"进行"多件事**。

#### 对应到代码

| 现实 | 同步代码 | 异步代码 |
|------|----------|----------|
| 打电话 | `const data = fs.readFileSync('file.txt')` — 读文件时，整个程序等着 | `fs.readFile('file.txt', (err, data) => { ... })` — 读文件时，程序继续干别的 |
| 效果 | 一行一行执行，上一行没完成，下一行绝不开始 | 发起操作后立刻继续执行，操作完成时通过回调通知你 |

**餐厅比喻**：同步就像服务员只服务一桌客人——点菜、等菜、上菜、结账，全部完成才去下一桌。异步就像服务员同时服务多桌——点完 1 号桌的菜就去 2 号桌，1 号桌的菜做好了（回调）再端上去。

---

### 步骤 2：Node.js 为什么是异步的——单线程 + 事件循环

你可能听说过 Python 用多线程、Java 用多线程来处理并发。但 Node.js 只有一个主线程，为什么也能同时处理成千上万个请求？

#### 一句话答案

**Node.js 只有一个主线程，但通过"事件循环"在后台排队处理耗时操作，主线程不会被阻塞。**

#### 餐厅比喻（彻底理解）

想象一个餐厅，只有一个服务员（单线程），但能同时服务 20 桌客人：

```
1. 服务员走到 1 号桌 → 记录点菜（发起异步操作）→ 把菜单交给厨房
2. 服务员不等菜做好，立刻走到 2 号桌 → 记录点菜 → 交给厨房
3. 服务员走到 3 号桌 → 记录点菜 → 交给厨房
4. ...
5. 厨房喊："1 号桌的菜好了！"（回调触发）
6. 服务员端菜上 1 号桌
7. 继续服务其他桌...
```

**关键点**：
- 服务员（主线程）只做"记录点菜"和"端菜"这种**快速操作**。
- 做菜（耗时操作）交给了厨房（操作系统/线程池），服务员不等。
- 菜好了（回调），服务员再回来处理。

**和 Python/Java 多线程的区别**：

| | Node.js | Python/Java 多线程 |
|------|---------|---------------------|
| 线程数 | 1 个主线程 | 每个请求一个线程 |
| 并发方式 | 事件循环（异步非阻塞） | 多线程同时执行 |
| 服务员比喻 | 1 个服务员服务 20 桌 | 20 个服务员各服务 1 桌 |
| 内存开销 | 低（只有一个线程） | 高（每个线程都有独立内存） |
| 适合场景 | I/O 密集型（读写文件、网络请求） | CPU 密集型（计算、加密） |

> 🔥 **魔鬼细节**：异步 ≠ 多线程。Node.js 是单线程的。你写的 JavaScript 代码永远只在一个线程上运行。但 Node.js 底层调用的 C++ 库（libuv）会使用线程池来处理文件读写等操作——这些线程不在你的 JavaScript 代码中，你感受不到它们。

---

### 步骤 3：回调函数——"事办完了再叫我"

回调函数（Callback）是 JavaScript 中最基础的异步处理方式。它的核心思想很简单：

**把一个函数传给另一个函数，当操作完成时，用这个函数通知你。**

#### 3.1 最基础的回调：setTimeout

```javascript
console.log('1. 开始');

setTimeout(() => {
    console.log('3. 3 秒后执行');
}, 3000);

console.log('2. 结束');
```

**输出顺序**：

```
1. 开始
2. 结束
3. 3 秒后执行
```

注意：`2. 结束` 在 `3. 3秒后执行` 之前！这就是异步—— `setTimeout` 不会阻塞后面的代码。

#### 3.2 在 `blog-backend/sandbox/` 中创建演示文件

首先创建 sandbox 目录：

```bash
mkdir blog-backend/sandbox
```

然后在 `blog-backend/sandbox/01-callback.js` 中创建：

```javascript
// sandbox/01-callback.js — 回调函数基础演示

// 示例 1：setTimeout — 最基础的回调
console.log('=== 示例 1：setTimeout ===');
console.log('A: 开始');

setTimeout(() => {
    console.log('B: 2 秒后执行（异步回调）');
}, 2000);

console.log('C: setTimeout 之后的代码，不会等 B');
console.log('');

// 示例 2：自定义回调函数
console.log('=== 示例 2：自定义回调 ===');

function 做菜(菜名, 做好了叫我) {
    console.log(`  厨师开始做 ${菜名}...`);
    setTimeout(() => {
        console.log(`  厨师：${菜名} 做好了！`);
        做好了叫我(null, `${菜名}（热腾腾）`);
    }, 1000);
}

console.log('  客人点菜：宫保鸡丁');
做菜('宫保鸡丁', (err, 菜) => {
    if (err) {
        console.log('  出错了：', err);
    } else {
        console.log(`  服务员端上：${菜}`);
    }
});
console.log('  客人继续看手机（没被阻塞）');
```

运行：

```bash
node sandbox/01-callback.js
```

**预期输出**：

```
=== 示例 1：setTimeout ===
A: 开始
C: setTimeout 之后的代码，不会等 B

=== 示例 2：自定义回调 ===
  客人点菜：宫保鸡丁
  厨师开始做 宫保鸡丁...
  客人继续看手机（没被阻塞）
  厨师：宫保鸡丁 做好了！
  服务员端上：宫保鸡丁（热腾腾）
```

观察 `C` 在 `B` 之前输出，以及 `客人继续看手机` 在 `服务员端上` 之前输出——这就是异步。

---

### 步骤 4：Node.js 的 err 优先回调约定

Node.js 几乎所有内置异步 API 都遵循一个约定：**回调函数的第一个参数是错误对象，第二个才是结果**。

```javascript
(err, result) => {
    if (err) {
        // 处理错误
    } else {
        // 使用 result
    }
}
```

#### 4.1 用 fs.readFile 演示

创建 `blog-backend/sandbox/02-err-first.js`：

```javascript
// sandbox/02-err-first.js — err 优先回调约定演示
const fs = require('fs');

console.log('=== 示例 1：读取存在的文件 ===');
fs.readFile('sandbox/01-callback.js', 'utf8', (err, data) => {
    if (err) {
        console.log('❌ 读取失败：', err.message);
        return;
    }
    console.log('✅ 读取成功，文件前 50 个字符：');
    console.log(data.substring(0, 50));
    console.log('...');
});

console.log('=== 示例 2：读取不存在的文件 ===');
fs.readFile('sandbox/不存在.txt', 'utf8', (err, data) => {
    if (err) {
        console.log('❌ 读取失败：', err.message);
        console.log('   错误码：', err.code);  // ENOENT = 文件不存在
        return;
    }
    console.log('✅ 读取成功：', data);
});

console.log('（这条消息在文件读取结果之前打印，证明是异步的）');
```

运行：

```bash
node sandbox/02-err-first.js
```

**预期输出**：

```
=== 示例 1：读取存在的文件 ===
=== 示例 2：读取不存在的文件 ===
（这条消息在文件读取结果之前打印，证明是异步的）
✅ 读取成功，文件前 50 个字符：
// sandbox/01-callback.js — 回调函数基础演示
...
❌ 读取失败： ENOENT: no such file or directory, open 'sandbox/不存在.txt'
   错误码： ENOENT
```

#### 4.2 err 优先约定的好处

| 好处 | 说明 |
|------|------|
| 统一风格 | 不用猜哪个参数是错误、哪个是结果——永远是 `(err, result)` |
| 强制错误处理 | 你不检查 `err` 就用 `data`，ESLint 会警告你，团队 Code Review 也会发现 |
| 不会漏掉错误 | 同步代码可以用 `try/catch`，异步代码只能用回调的第一个参数传错误 |

> 🔥 **魔鬼细节**：回调函数不是一定会被调用！比如 `fs.readFile` 读取一个不存在的文件时，回调**一定会被调用**（只是 `err` 不为 `null`）。但有些第三方库的回调可能因为 bug 永远不被调用——这就是为什么 Promise 更安全：Promise 一定会 resolve 或 reject。

---

### 步骤 5：回调地狱——三层嵌套读文件

现在我们来做一个真实的场景：**读文件 A → 用 A 的内容构造文件名 → 读文件 B → 用 B 的内容构造文件名 → 读文件 C**。

#### 5.1 先创建测试用的文件

```bash
mkdir blog-backend/sandbox/data
```

创建 `blog-backend/sandbox/data/file-a.txt`：

```
file-b.txt
```

创建 `blog-backend/sandbox/data/file-b.txt`：

```
file-c.txt
```

创建 `blog-backend/sandbox/data/file-c.txt`：

```
Hello World! 这是第三层文件的内容。
```

#### 5.2 写回调地狱代码

创建 `blog-backend/sandbox/03-callback-hell.js`：

```javascript
// sandbox/03-callback-hell.js — 回调地狱演示
const fs = require('fs');
const path = require('path');

const dataDir = path.join(__dirname, 'data');

console.log('开始读取文件链...\n');

// 第一层：读 file-a.txt
fs.readFile(path.join(dataDir, 'file-a.txt'), 'utf8', (err, dataA) => {
    if (err) {
        console.log('读 file-a.txt 失败：', err.message);
        return;
    }
    const fileNameB = dataA.trim();
    console.log(`1. 从 file-a.txt 读到下一文件名：${fileNameB}`);

    // 第二层：读 file-b.txt
    fs.readFile(path.join(dataDir, fileNameB), 'utf8', (err, dataB) => {
        if (err) {
            console.log('读 file-b.txt 失败：', err.message);
            return;
        }
        const fileNameC = dataB.trim();
        console.log(`2. 从 file-b.txt 读到下一文件名：${fileNameC}`);

        // 第三层：读 file-c.txt
        fs.readFile(path.join(dataDir, fileNameC), 'utf8', (err, dataC) => {
            if (err) {
                console.log('读 file-c.txt 失败：', err.message);
                return;
            }
            console.log(`3. 从 file-c.txt 读到最终内容：${dataC.trim()}`);
            console.log('\n✅ 三层嵌套全部完成！');
        }); // 第三层结束
    }); // 第二层结束
}); // 第一层结束

console.log('（这条消息会先打印，因为读文件是异步的）');
```

运行：

```bash
node sandbox/03-callback-hell.js
```

#### 5.3 这段代码有什么问题？

看这段代码的形状：

```
fs.readFile(..., (err, dataA) => {
    fs.readFile(..., (err, dataB) => {
        fs.readFile(..., (err, dataC) => {
            // 越来越深...
        });
    });
});
```

这就是著名的**回调地狱（Callback Hell）**，也叫"金字塔代码"（Pyramid of Doom）。每多一层嵌套，代码就向右缩进一层，最终变成：

```
                    });
                });
            });
        });
    });
});
```

**回调地狱的三大问题**：

| 问题 | 具体表现 |
|------|----------|
| 可读性差 | 代码向右越缩越多，逻辑像瀑布一样往下掉 |
| 错误处理重复 | 每一层都要写 `if (err) { ... return; }`，完全一样的代码写三遍 |
| 难以维护 | 想在第三层和第二层之间加一个步骤？你把整个金字塔拆了重搭 |

> 真实的项目中，回调地狱可能嵌套 5-10 层。想象一下：读配置文件 → 连接数据库 → 查询用户 → 查询订单 → 查询商品 → 发送通知...每一层都依赖上一层的结果，每一层都是异步的。这就是为什么我们需要 Promise。

---

### 步骤 6：Promise 拯救世界——把嵌套变链式

Promise 是 JavaScript 在 ES6（2015 年）引入的异步处理方案。它的核心思想很简单：

**Promise 是一个"承诺"——承诺在未来某个时刻给你一个结果（成功或失败）。**

#### 6.1 Promise 的三种状态

```
        ┌─────────┐
        │ pending │  ← 初始状态：进行中
        └────┬────┘
         ┌───┴───┐
    ┌────▼──┐ ┌──▼──────┐
    │fulfilled│ │rejected │
    │（成功）  │ │（失败）  │
    └────────┘ └─────────┘
```

- **pending**（进行中）：操作还没完成，结果未知。
- **fulfilled**（成功）：操作成功完成，有结果值。
- **rejected**（失败）：操作失败，有错误原因。

**一旦从 pending 变成 fulfilled 或 rejected，状态就永久固定，不会再变。**

**餐厅比喻**：Promise 就像你点菜后拿到的小票——
- 你拿到小票时，菜还没好（pending）。
- 菜好了，服务员端上来（fulfilled）。
- 厨房说"这道菜卖完了"（rejected）。
- 菜一旦端上来（或确认卖完了），这个小票就"完成使命"了，不会再变。

#### 6.2 创建 Promise

创建 `blog-backend/sandbox/04-promise-basic.js`：

```javascript
// sandbox/04-promise-basic.js — Promise 基础演示

// 示例 1：手动创建 Promise
console.log('=== 示例 1：创建 Promise ===');

function 做菜(菜名, 能做吗) {
    return new Promise((resolve, reject) => {
        console.log(`  厨师开始做 ${菜名}...`);
        setTimeout(() => {
            if (能做吗) {
                resolve(`${菜名}（热腾腾）`);  // 成功！
            } else {
                reject(`${菜名} 卖完了`);       // 失败！
            }
        }, 1000);
    });
}

// 使用 Promise
做菜('宫保鸡丁', true)
    .then((菜) => {
        console.log(`✅ 服务员端上：${菜}`);
    })
    .catch((原因) => {
        console.log(`❌ 抱歉：${原因}`);
    });

console.log('  客人继续看手机（没被阻塞）');
console.log('');

// 示例 2：Promise 链式调用
console.log('=== 示例 2：链式调用 ===');

const 买菜 = () => {
    return new Promise((resolve) => {
        setTimeout(() => resolve('🥬 青菜'), 500);
    });
};

const 洗菜 = (食材) => {
    return new Promise((resolve) => {
        console.log(`  洗菜中：${食材}`);
        setTimeout(() => resolve(`${食材}（已洗净）`), 500);
    });
};

const 炒菜 = (食材) => {
    return new Promise((resolve) => {
        console.log(`  炒菜中：${食材}`);
        setTimeout(() => resolve(`${食材} → 🍳 炒青菜`), 500);
    });
};

买菜()
    .then(食材 => 洗菜(食材))
    .then(食材 => 炒菜(食材))
    .then(成品 => {
        console.log(`✅ 完成：${成品}`);
    })
    .catch(err => {
        console.log('❌ 出错了：', err);
    });

console.log('  （这条消息先打印）');
```

运行：

```bash
node sandbox/04-promise-basic.js
```

#### 6.3 Promise 链式调用的核心规则

| 规则 | 说明 | 示例 |
|------|------|------|
| `.then()` 返回新的 Promise | 所以可以链式调用 | `.then(a).then(b).then(c)` |
| `.then()` 中可以 return 一个值 | 这个值会被下一个 `.then()` 接收 | `.then(() => 'hello').then(msg => ...)` |
| `.then()` 中可以 return 一个 Promise | 下一个 `.then()` 会等这个 Promise 完成 | `.then(() => fetchUser()).then(user => ...)` |
| `.catch()` 捕获前面所有 `.then()` 的错误 | 一个 `.catch()` 就够了，不需要每层都写 | `.then(a).then(b).then(c).catch(err => ...)` |

> 🔥 **魔鬼细节**：`.catch()` 会捕获它前面**所有** `.then()` 中抛出的错误。如果你在链的开头写 `.catch()`，它只会捕获它前面的 `.then()` 的错误，后面的不会捕获。所以 `.catch()` 通常放在链的最后。

---

### 步骤 7：用 Promise 改写回调地狱

创建 `blog-backend/sandbox/05-promise-chain.js`：

```javascript
// sandbox/05-promise-chain.js — 用 Promise 改写回调地狱
const fs = require('fs');
const path = require('path');

const dataDir = path.join(__dirname, 'data');

// 把 fs.readFile 包装成返回 Promise 的函数
function readFilePromise(filePath) {
    return new Promise((resolve, reject) => {
        fs.readFile(filePath, 'utf8', (err, data) => {
            if (err) {
                reject(err);
            } else {
                resolve(data);
            }
        });
    });
}

// 用 Promise 链式调用改写三层嵌套
console.log('开始读取文件链（Promise 版）...\n');

readFilePromise(path.join(dataDir, 'file-a.txt'))
    .then(dataA => {
        const fileNameB = dataA.trim();
        console.log(`1. 从 file-a.txt 读到下一文件名：${fileNameB}`);
        return readFilePromise(path.join(dataDir, fileNameB));
    })
    .then(dataB => {
        const fileNameC = dataB.trim();
        console.log(`2. 从 file-b.txt 读到下一文件名：${fileNameC}`);
        return readFilePromise(path.join(dataDir, fileNameC));
    })
    .then(dataC => {
        console.log(`3. 从 file-c.txt 读到最终内容：${dataC.trim()}`);
        console.log('\n✅ 三层链式调用全部完成！');
    })
    .catch(err => {
        console.log('❌ 读取过程中出错：', err.message);
    });

console.log('（这条消息先打印）');
```

#### 对比：回调地狱 vs Promise 链

| 对比维度 | 回调地狱 | Promise 链 |
|----------|----------|-----------|
| 缩进层次 | 越嵌套越深（3 层就是 3 个 tab） | 始终在同一层（平铺） |
| 错误处理 | 每层都要写 `if (err) { ... }` | 一个 `.catch()` 处理所有错误 |
| 加步骤 | 要从最内层拆开重写 | 在链中间插入一个 `.then()` 即可 |
| 可读性 | 从左到右越来越窄 | 从上到下，逻辑清晰 |

> 这就是 Promise 的核心价值：**把嵌套的"金字塔"变成扁平的"链条"**。

---

### 步骤 8：Promise.all()——并行执行多个异步操作

上面的例子中，`file-a → file-b → file-c` 是**依赖关系**——必须顺序执行。但如果三个操作之间没有依赖关系呢？比如同时读三个独立的文件——我们可以**并行**执行，节省时间。

#### 8.1 顺序执行 vs 并行执行

创建 `blog-backend/sandbox/06-promise-all.js`：

```javascript
// sandbox/06-promise-all.js — Promise.all 并行执行演示
const fs = require('fs');
const path = require('path');

const dataDir = path.join(__dirname, 'data');

function readFilePromise(filePath) {
    return new Promise((resolve, reject) => {
        fs.readFile(filePath, 'utf8', (err, data) => {
            if (err) reject(err);
            else resolve(data);
        });
    });
}

// ====== 方式一：顺序执行（一个接一个） ======
console.log('=== 方式一：顺序执行 ===');
const start1 = Date.now();

readFilePromise(path.join(dataDir, 'file-a.txt'))
    .then(dataA => {
        console.log(`  读完 file-a.txt，耗时 ${Date.now() - start1}ms`);
        return readFilePromise(path.join(dataDir, 'file-b.txt'));
    })
    .then(dataB => {
        console.log(`  读完 file-b.txt，耗时 ${Date.now() - start1}ms`);
        return readFilePromise(path.join(dataDir, 'file-c.txt'));
    })
    .then(dataC => {
        console.log(`  读完 file-c.txt，耗时 ${Date.now() - start1}ms`);
        console.log(`  顺序执行总耗时：${Date.now() - start1}ms\n`);
        runParallel();
    });

// ====== 方式二：并行执行（同时开始） ======
function runParallel() {
    console.log('=== 方式二：并行执行（Promise.all） ===');
    const start2 = Date.now();

    Promise.all([
        readFilePromise(path.join(dataDir, 'file-a.txt')),
        readFilePromise(path.join(dataDir, 'file-b.txt')),
        readFilePromise(path.join(dataDir, 'file-c.txt'))
    ])
        .then(([dataA, dataB, dataC]) => {
            console.log(`  file-a.txt: ${dataA.trim()}`);
            console.log(`  file-b.txt: ${dataB.trim()}`);
            console.log(`  file-c.txt: ${dataC.trim()}`);
            console.log(`  并行执行总耗时：${Date.now() - start2}ms`);
        })
        .catch(err => {
            console.log('  ❌ 至少一个文件读取失败：', err.message);
        });
}
```

运行：

```bash
node sandbox/06-promise-all.js
```

#### 8.2 Promise.all 的关键规则

| 规则 | 说明 |
|------|------|
| 参数是数组 | `Promise.all([promise1, promise2, promise3])` |
| 全部成功才成功 | 所有 Promise 都 fulfilled，`.then()` 才执行 |
| 一个失败全失败 | 只要有一个 reject，整个 `Promise.all` 就 reject |
| 结果顺序对应 | `.then([result1, result2, result3])` 的顺序和传入数组顺序一致 |
| 并行不分先后 | 三个 Promise 同时开始，谁先完成不确定，但 `.then()` 的结果顺序是固定的 |

**餐厅比喻**：`Promise.all` 就是一下子点了三桌的菜，厨房同时做。三桌菜都做好了，服务员一起端上去。如果有一桌的菜卖完了（reject），整个"三桌订单"就失败了——你需要重新处理。

> 🔥 **魔鬼细节**：`Promise.all` 中如果一个失败，**全部失败**。即使其他两个已经成功了，`.then()` 也不会被调用，而是直接进入 `.catch()`。如果你需要"部分成功也接受"，可以用 `Promise.allSettled()`（Node.js 12.9+）。

#### 8.3 顺序 vs 并行——时间差异

虽然因为文件很小，你可能看不出明显的时间差异。但想象一下：如果每个操作需要 1 秒：
- **顺序执行**：1 + 1 + 1 = **3 秒**
- **并行执行**：max(1, 1, 1) = **1 秒**

这就是为什么在不需要依赖关系时，用 `Promise.all` 能大幅提升性能。

---

### 步骤 9：事件循环——一句话 + 一张 ASCII 图

事件循环（Event Loop）是 Node.js 异步机制的核心，但它的完整原理非常复杂。对于初学者，只需要理解最直观的部分。

#### 一句话解释

**事件循环就是一个不断检查"有没有异步操作完成了"的循环——完成了就把对应的回调函数拿出来执行，没完成就继续检查。**

#### ASCII 图

```
┌─────────────────────────────────────────────────┐
│                  事件循环（Event Loop）            │
│                                                 │
│    ┌──────────┐    ┌──────────────────┐         │
│    │ 你的代码  │───▶│  发起异步操作       │         │
│    │（单线程） │    │  fs.readFile()    │         │
│    └──────────┘    │  setTimeout()     │         │
│         │          │  fetch()          │         │
│         │          └────────┬─────────┘         │
│         │                   │                   │
│         │          ┌────────▼─────────┐         │
│         │          │   操作系统/线程池  │         │
│         │          │  （后台处理）     │         │
│         │          └────────┬─────────┘         │
│         │                   │ 操作完成           │
│         │          ┌────────▼─────────┐         │
│         └─────────▶│   回调队列        │         │
│  继续执行其他代码    │  callback1       │         │
│                    │  callback2       │         │
│                    └────────┬─────────┘         │
│                             │                   │
│                    ┌────────▼─────────┐         │
│                    │   事件循环取出回调  │         │
│                    │   并执行它         │         │
│                    └──────────────────┘         │
│                                                 │
│  关键：你的代码运行在"主线程"上，永远不会中断。     │
│  异步回调只是"排队"等到主线程空闲时再执行。          │
└─────────────────────────────────────────────────┘
```

**餐厅比喻**：事件循环就是那个服务员的大脑——不断在想"厨房有没有菜好了？1 号桌要不要加水？2 号桌要结账吗？"——快速扫描所有待处理的事情，一件一件处理。

> 这里我们不深入讲解宏任务（macro-task）和微任务（micro-task）的区别。对于你现在的阶段，记住"事件循环就是排队执行回调"就够了。等你遇到了 `setTimeout(fn, 0)` 和 `Promise.resolve().then(fn)` 谁先执行的问题时，再深入学习。

---

### 🤔 想多一点：为什么 Node.js 选择了单线程 + 异步，而不是多线程？

**历史原因**：Node.js 的创造者 Ryan Dahl 在 2009 年发现，大多数 Web 服务器的瓶颈不是 CPU 计算，而是 **I/O 等待**（读文件、查数据库、调外部 API）。这些操作中，CPU 大部分时间在"等待"——啥也不干。

**多线程的问题**：每个线程都有自己的内存空间（栈），切换线程有开销，线程多了内存占用大，而且多线程编程容易出 bug（死锁、竞态条件）。

**Node.js 的答案**：一个线程就够了。CPU 只做"快速的事"（解析请求、组织响应），慢的事（读文件、查数据库）交给操作系统后台处理，处理完了通知我。这就是"非阻塞 I/O"。

**总结**：Node.js 不是万能的。它擅长 I/O 密集型（Web 服务器、API 网关、实时聊天），但不擅长 CPU 密集型（视频编码、大量数学计算、机器学习推理）。选对工具，比选"最好的工具"更重要。

---

### ❌ 常见错误 → ✅ 解决方案

| 错误信息 / 现象 | 原因 | 解决 |
|-----------------|------|------|
| 回调函数中 `err` 为 `null` 但你用了 `err.message` | `null` 没有 `.message` 属性 | 先检查 `if (err)` 再使用 `err.message` |
| `fs.readFile` 回调中 `data` 是 `undefined` | 文件读取失败，`err` 不为 `null`，但你没检查 `err` 就直接用了 `data` | 始终先检查 `if (err) { ... return; }` |
| Promise 的 `.then()` 中返回 `undefined` | 忘记 `return` 了 | `.then(data => { return doSomething(data); })` 或简写 `.then(data => doSomething(data))` |
| `Promise.all` 中一个失败，全部失败 | 这是设计行为 | 如果需要部分成功，用 `Promise.allSettled()` |
| `new Promise(...)` 中的 `resolve` 被多次调用 | 只有第一次生效，后面的被忽略 | Promise 状态一旦确定就不会改变，不用担心 |
| `setTimeout(fn, 0)` 不是立即执行 | 0 毫秒不是真的 0 毫秒，最小延迟约 1-4ms | 不要用 `setTimeout(fn, 0)` 来做"立即执行"，用 `Promise.resolve().then(fn)` |
| 回调地狱中错误处理重复 | 每层都写 `if (err) return` | 用 Promise 链，一个 `.catch()` 搞定 |
| 异步操作的结果在回调外面拿不到 | 异步操作还没完成，你就想用结果 | 只能在回调函数内或 `.then()` 内使用异步结果 |

---

## 四、完整代码清单

### `blog-backend/sandbox/01-callback.js`（本章新建）

```javascript
// sandbox/01-callback.js — 回调函数基础演示

// 示例 1：setTimeout — 最基础的回调
console.log('=== 示例 1：setTimeout ===');
console.log('A: 开始');

setTimeout(() => {
    console.log('B: 2 秒后执行（异步回调）');
}, 2000);

console.log('C: setTimeout 之后的代码，不会等 B');
console.log('');

// 示例 2：自定义回调函数
console.log('=== 示例 2：自定义回调 ===');

function 做菜(菜名, 做好了叫我) {
    console.log(`  厨师开始做 ${菜名}...`);
    setTimeout(() => {
        console.log(`  厨师：${菜名} 做好了！`);
        做好了叫我(null, `${菜名}（热腾腾）`);
    }, 1000);
}

console.log('  客人点菜：宫保鸡丁');
做菜('宫保鸡丁', (err, 菜) => {
    if (err) {
        console.log('  出错了：', err);
    } else {
        console.log(`  服务员端上：${菜}`);
    }
});
console.log('  客人继续看手机（没被阻塞）');
```

### `blog-backend/sandbox/02-err-first.js`（本章新建）

```javascript
// sandbox/02-err-first.js — err 优先回调约定演示
const fs = require('fs');

console.log('=== 示例 1：读取存在的文件 ===');
fs.readFile('sandbox/01-callback.js', 'utf8', (err, data) => {
    if (err) {
        console.log('❌ 读取失败：', err.message);
        return;
    }
    console.log('✅ 读取成功，文件前 50 个字符：');
    console.log(data.substring(0, 50));
    console.log('...');
});

console.log('=== 示例 2：读取不存在的文件 ===');
fs.readFile('sandbox/不存在.txt', 'utf8', (err, data) => {
    if (err) {
        console.log('❌ 读取失败：', err.message);
        console.log('   错误码：', err.code);
        return;
    }
    console.log('✅ 读取成功：', data);
});

console.log('（这条消息在文件读取结果之前打印，证明是异步的）');
```

### `blog-backend/sandbox/03-callback-hell.js`（本章新建）

```javascript
// sandbox/03-callback-hell.js — 回调地狱演示
const fs = require('fs');
const path = require('path');

const dataDir = path.join(__dirname, 'data');

console.log('开始读取文件链...\n');

// 第一层：读 file-a.txt
fs.readFile(path.join(dataDir, 'file-a.txt'), 'utf8', (err, dataA) => {
    if (err) {
        console.log('读 file-a.txt 失败：', err.message);
        return;
    }
    const fileNameB = dataA.trim();
    console.log(`1. 从 file-a.txt 读到下一文件名：${fileNameB}`);

    // 第二层：读 file-b.txt
    fs.readFile(path.join(dataDir, fileNameB), 'utf8', (err, dataB) => {
        if (err) {
            console.log('读 file-b.txt 失败：', err.message);
            return;
        }
        const fileNameC = dataB.trim();
        console.log(`2. 从 file-b.txt 读到下一文件名：${fileNameC}`);

        // 第三层：读 file-c.txt
        fs.readFile(path.join(dataDir, fileNameC), 'utf8', (err, dataC) => {
            if (err) {
                console.log('读 file-c.txt 失败：', err.message);
                return;
            }
            console.log(`3. 从 file-c.txt 读到最终内容：${dataC.trim()}`);
            console.log('\n✅ 三层嵌套全部完成！');
        }); // 第三层结束
    }); // 第二层结束
}); // 第一层结束

console.log('（这条消息会先打印，因为读文件是异步的）');
```

### `blog-backend/sandbox/04-promise-basic.js`（本章新建）

```javascript
// sandbox/04-promise-basic.js — Promise 基础演示

// 示例 1：手动创建 Promise
console.log('=== 示例 1：创建 Promise ===');

function 做菜(菜名, 能做吗) {
    return new Promise((resolve, reject) => {
        console.log(`  厨师开始做 ${菜名}...`);
        setTimeout(() => {
            if (能做吗) {
                resolve(`${菜名}（热腾腾）`);
            } else {
                reject(`${菜名} 卖完了`);
            }
        }, 1000);
    });
}

// 使用 Promise
做菜('宫保鸡丁', true)
    .then((菜) => {
        console.log(`✅ 服务员端上：${菜}`);
    })
    .catch((原因) => {
        console.log(`❌ 抱歉：${原因}`);
    });

console.log('  客人继续看手机（没被阻塞）');
console.log('');

// 示例 2：Promise 链式调用
console.log('=== 示例 2：链式调用 ===');

const 买菜 = () => {
    return new Promise((resolve) => {
        setTimeout(() => resolve('🥬 青菜'), 500);
    });
};

const 洗菜 = (食材) => {
    return new Promise((resolve) => {
        console.log(`  洗菜中：${食材}`);
        setTimeout(() => resolve(`${食材}（已洗净）`), 500);
    });
};

const 炒菜 = (食材) => {
    return new Promise((resolve) => {
        console.log(`  炒菜中：${食材}`);
        setTimeout(() => resolve(`${食材} → 🍳 炒青菜`), 500);
    });
};

买菜()
    .then(食材 => 洗菜(食材))
    .then(食材 => 炒菜(食材))
    .then(成品 => {
        console.log(`✅ 完成：${成品}`);
    })
    .catch(err => {
        console.log('❌ 出错了：', err);
    });

console.log('  （这条消息先打印）');
```

### `blog-backend/sandbox/05-promise-chain.js`（本章新建）

```javascript
// sandbox/05-promise-chain.js — 用 Promise 改写回调地狱
const fs = require('fs');
const path = require('path');

const dataDir = path.join(__dirname, 'data');

// 把 fs.readFile 包装成返回 Promise 的函数
function readFilePromise(filePath) {
    return new Promise((resolve, reject) => {
        fs.readFile(filePath, 'utf8', (err, data) => {
            if (err) {
                reject(err);
            } else {
                resolve(data);
            }
        });
    });
}

// 用 Promise 链式调用改写三层嵌套
console.log('开始读取文件链（Promise 版）...\n');

readFilePromise(path.join(dataDir, 'file-a.txt'))
    .then(dataA => {
        const fileNameB = dataA.trim();
        console.log(`1. 从 file-a.txt 读到下一文件名：${fileNameB}`);
        return readFilePromise(path.join(dataDir, fileNameB));
    })
    .then(dataB => {
        const fileNameC = dataB.trim();
        console.log(`2. 从 file-b.txt 读到下一文件名：${fileNameC}`);
        return readFilePromise(path.join(dataDir, fileNameC));
    })
    .then(dataC => {
        console.log(`3. 从 file-c.txt 读到最终内容：${dataC.trim()}`);
        console.log('\n✅ 三层链式调用全部完成！');
    })
    .catch(err => {
        console.log('❌ 读取过程中出错：', err.message);
    });

console.log('（这条消息先打印）');
```

### `blog-backend/sandbox/06-promise-all.js`（本章新建）

```javascript
// sandbox/06-promise-all.js — Promise.all 并行执行演示
const fs = require('fs');
const path = require('path');

const dataDir = path.join(__dirname, 'data');

function readFilePromise(filePath) {
    return new Promise((resolve, reject) => {
        fs.readFile(filePath, 'utf8', (err, data) => {
            if (err) reject(err);
            else resolve(data);
        });
    });
}

// ====== 方式一：顺序执行（一个接一个） ======
console.log('=== 方式一：顺序执行 ===');
const start1 = Date.now();

readFilePromise(path.join(dataDir, 'file-a.txt'))
    .then(dataA => {
        console.log(`  读完 file-a.txt，耗时 ${Date.now() - start1}ms`);
        return readFilePromise(path.join(dataDir, 'file-b.txt'));
    })
    .then(dataB => {
        console.log(`  读完 file-b.txt，耗时 ${Date.now() - start1}ms`);
        return readFilePromise(path.join(dataDir, 'file-c.txt'));
    })
    .then(dataC => {
        console.log(`  读完 file-c.txt，耗时 ${Date.now() - start1}ms`);
        console.log(`  顺序执行总耗时：${Date.now() - start1}ms\n`);
        runParallel();
    });

// ====== 方式二：并行执行（同时开始） ======
function runParallel() {
    console.log('=== 方式二：并行执行（Promise.all） ===');
    const start2 = Date.now();

    Promise.all([
        readFilePromise(path.join(dataDir, 'file-a.txt')),
        readFilePromise(path.join(dataDir, 'file-b.txt')),
        readFilePromise(path.join(dataDir, 'file-c.txt'))
    ])
        .then(([dataA, dataB, dataC]) => {
            console.log(`  file-a.txt: ${dataA.trim()}`);
            console.log(`  file-b.txt: ${dataB.trim()}`);
            console.log(`  file-c.txt: ${dataC.trim()}`);
            console.log(`  并行执行总耗时：${Date.now() - start2}ms`);
        })
        .catch(err => {
            console.log('  ❌ 至少一个文件读取失败：', err.message);
        });
}
```

### `blog-backend/sandbox/data/file-a.txt`（本章新建）

```
file-b.txt
```

### `blog-backend/sandbox/data/file-b.txt`（本章新建）

```
file-c.txt
```

### `blog-backend/sandbox/data/file-c.txt`（本章新建）

```
Hello World! 这是第三层文件的内容。
```

### `blog-backend/` 目录结构（本章新增）

```
blog-backend/
├── server.js
├── package.json
├── ...
├── sandbox/                        ← 本章新建
│   ├── 01-callback.js              ← 回调基础演示
│   ├── 02-err-first.js             ← err 优先回调演示
│   ├── 03-callback-hell.js         ← 回调地狱演示
│   ├── 04-promise-basic.js         ← Promise 基础演示
│   ├── 05-promise-chain.js         ← Promise 链改写回调地狱
│   ├── 06-promise-all.js           ← Promise.all 并行演示
│   └── data/                       ← 本章新建
│       ├── file-a.txt
│       ├── file-b.txt
│       └── file-c.txt
```

---

## 五、验证方法

| 序号 | 操作 | 预期结果 |
|------|------|----------|
| 1 | `node sandbox/01-callback.js` | `C` 在 `B` 之前输出；`客人继续看手机` 在 `服务员端上` 之前输出 |
| 2 | `node sandbox/02-err-first.js` | 文件存在 → `✅ 读取成功`；文件不存在 → `❌ 读取失败` + `ENOENT` |
| 3 | `node sandbox/03-callback-hell.js` | 三层嵌套依次输出，最终显示 `✅ 三层嵌套全部完成！` |
| 4 | `node sandbox/04-promise-basic.js` | 示例 1：`✅ 服务员端上：宫保鸡丁（热腾腾）`；示例 2：`✅ 完成：🥬 青菜（已洗净）→ 🍳 炒青菜` |
| 5 | `node sandbox/05-promise-chain.js` | 三层链式依次输出，最终显示 `✅ 三层链式调用全部完成！`，且没有嵌套缩进 |
| 6 | `node sandbox/06-promise-all.js` | 顺序执行和并行执行都完成，并行执行总耗时更短 |

全部通过？你已经掌握了回调与 Promise 的核心知识。

---

## 六、小结表格

| 学到的东西 | 一句话解释 |
|-----------|-----------|
| 同步 vs 异步 | 同步 = 打电话（等着），异步 = 发短信（发完干别的，回复了再处理） |
| Node.js 单线程 + 事件循环 | 一个服务员（单线程）服务多桌，点完菜（异步）就去下一桌，菜好了（回调）再端上去 |
| 回调函数 | 把一个函数传给另一个函数，操作完成后调用它——"事办完了再叫我" |
| err 优先回调 | 回调的第一个参数是错误对象（没错就是 `null`），第二个才是结果 |
| 回调地狱 | 多层嵌套的回调代码，像金字塔一样向右缩进，难以阅读和维护 |
| Promise 三种状态 | pending（进行中）→ fulfilled（成功）/ rejected（失败），状态一旦确定就不会改变 |
| `new Promise((resolve, reject) => {...})` | 创建 Promise：成功调 `resolve()`，失败调 `reject()` |
| `.then().catch()` | `.then()` 处理成功，`.catch()` 处理失败，链式调用消除嵌套 |
| `Promise.all()` | 并行执行多个 Promise，全部成功才成功，一个失败全失败 |
| 事件循环 | 不断检查"有没有异步操作完成了"，完成了就把回调拿出来执行 |
| 异步 ≠ 多线程 | Node.js 是单线程的，异步靠事件循环和操作系统后台处理实现 |

---

## 七、术语附录

| 术语 | 英文 | 通俗解释 | 本章出现位置 | 字面陷阱 |
|------|------|----------|-------------|----------|
| 同步（Synchronous） | Synchronous | 代码一行一行执行，上一行没完成，下一行绝不开始。就像打电话——对方不接，你只能等着。 | 步骤 1 | 不是"同时进行"——恰恰相反，同步意味着**一次只能做一件事**。 |
| 异步（Asynchronous） | Asynchronous | 发起一个操作后，不等待它完成，继续执行后面的代码。操作完成时通过回调或 Promise 通知你。就像发短信——发完就放下手机做别的事。 | 步骤 1 | 不是"不同步"——而是"不需要同步等待"。 |
| 回调（Callback） | Callback | 把一个函数作为参数传给另一个函数，当操作完成时调用这个函数。`(err, result) => { ... }`。 | 步骤 3 | 不是"往回调用"——而是"回头再调用你"。 |
| 回调地狱（Callback Hell） | Callback Hell | 多层嵌套的回调函数，代码形状像金字塔，难以阅读和维护。 | 步骤 5 | 不是真的"地狱"——是程序员对多层嵌套代码的幽默描述。 |
| Promise | Promise | 一个"承诺"——承诺在未来某个时刻给你一个结果（成功或失败）。提供 `.then()` 和 `.catch()` 方法处理结果。 | 步骤 6 | 不是"答应"的意思——是 JavaScript 中的一个内置对象类型。 |
| `.then()` | — | Promise 的方法，用于处理 Promise 成功（fulfilled）时的结果。返回新的 Promise，所以可以链式调用。 | 步骤 6 | 不是"然后"——虽然英文是"然后"，但它是 Promise 的专用方法。 |
| `.catch()` | — | Promise 的方法，用于处理 Promise 失败（rejected）时的错误。捕获前面所有 `.then()` 中抛出的错误。 | 步骤 6 | 不是"抓住"——是"捕获错误"。 |
| 事件循环（Event Loop） | Event Loop | Node.js 的核心机制：一个不断检查"有没有异步操作完成"的循环，完成了就把回调取出来执行。 | 步骤 9 | 不是"事件的循环"——是"循环检查事件"。 |
| 非阻塞 I/O | Non-blocking I/O | I/O 操作（读写文件、网络请求）不会阻塞主线程。发起操作后立刻返回，操作完成时通过回调通知。 | 步骤 2 | 不是"I/O 不阻塞"——而是"不阻塞主线程"。I/O 操作本身在后台仍然需要时间。 |
| `ENOENT` | Error NO ENTry | Node.js 文件操作的错误码，表示"文件或目录不存在"。完整拼写：Error NO ENTry。 | 步骤 4 | 不是"E-NO-ENT"——是 UNIX 系统的错误码缩写，源于 C 语言的 `errno`。 |

---

## 八、已知坑点与禁止事项

1. **异步 ≠ 多线程**：Node.js 是单线程的。你写的所有 JavaScript 代码都在同一个线程上运行。异步只是"不等待 I/O 操作"，不是"同时运行多个 JavaScript 代码"。

2. **回调函数不是一定会被调用**：虽然 Node.js 内置 API 的回调基本都会调用，但第三方库的回调可能因为 bug 永远不被调用。Promise 更安全——它一定会 resolve 或 reject。

3. **`setTimeout(fn, 0)` 不是真的 0 毫秒**：浏览器和 Node.js 都有最小延迟（约 1-4ms）。`setTimeout(fn, 0)` 的真实含义是"尽快执行，但不早于当前代码执行完毕"。

4. **Promise 的 `.catch()` 只能捕获它前面的 `.then()` 的错误**：如果你在链中间写 `.catch()`，它后面的 `.then()` 中的错误不会被这个 `.catch()` 捕获。所以 `.catch()` 通常放在链的最后。

5. **`Promise.all` 中一个失败，全部失败**：即使其他 Promise 已经成功了，只要有一个 reject，`.then()` 就不会被调用。如果需要部分成功，用 `Promise.allSettled()`。

6. **`new Promise` 的 `resolve` 只能调用一次**：Promise 的状态一旦从 pending 变成 fulfilled 或 rejected，就永久固定了。第二次调用 `resolve` 或 `reject` 会被忽略。

7. **不要在 Promise 构造函数外使用 `resolve` 和 `reject`**：`resolve` 和 `reject` 只在 `new Promise((resolve, reject) => { ... })` 的作用域内有效。把它们存到外部变量中再调用是一种反模式，容易导致难以调试的 bug。

8. **异步操作的结果只能在回调或 `.then()` 中使用**：你不能在异步操作的外面直接拿到结果。这不是 bug，而是异步的本质——操作还没完成，结果当然还没出来。

---

## 九、下一步建议

你已经掌握了回调函数和 Promise。但 Promise 链虽然比回调地狱好，写法还是有点啰嗦——每个 `.then()` 都要写一个函数。接下来：

- **下一章**：[11-异步编程（二）：async/await与文件操作](11-异步编程（二）：asyncawait与文件操作.md)——用 `async/await` 让异步代码看起来像同步代码，一行抵十行。同时实战文件操作，对比同步和异步的适用场景，最后把 Express 路由改为 async。
- **延伸思考**：你现在写的 `readFilePromise` 函数，其实就是 `fs.promises.readFile` 的雏形。Node.js 10+ 已经内置了 `fs.promises`，不需要手动包装。下一章会讲到。

---

> 📊 本教程无可视化
>
> 本教程编辑记录：2026-06-12 初始版本。