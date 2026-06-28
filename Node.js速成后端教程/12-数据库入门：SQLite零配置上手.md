# 12-数据库入门：SQLite 零配置上手

> "第 09 章结尾你亲眼看到了——重启服务器，文章全没了。数据存在内存里就像用粉笔在黑板上记账，一擦就没了。这一章我们引入数据库，把数据真正写到硬盘上。而且我们不选需要安装服务器软件的 MySQL，选**零配置**的 SQLite——一个文件就是整个数据库。你只需要一行 `npm install`，数据库就已经就绪了。"

---

## 一、目标与完成效果

**一句话目标**：理解数据库的基本概念（数据库/表/行/列），安装 `better-sqlite3`，创建第一个数据库文件并执行插入和查询操作，将 `.db` 文件加入 `.gitignore`。

**完成后的可观测效果**：
- 你理解了"数据库 = Excel 文件夹，表 = Sheet"的对应关系。
- 你成功安装了 `better-sqlite3`（或备选方案 `sql.js`）。
- 你创建了 `database/init.js`，运行后项目根目录出现了 `blog.db` 文件。
- 你执行了 `INSERT` 和 `SELECT` 语句，看到数据被写入 `.db` 文件并成功读出。
- `blog.db` 已加入 `.gitignore`，不会被提交到 Git。
- 你理解了 `.db` 文件是二进制文件，不能用记事本打开（打开也是乱码）。

---

## 二、前置条件

| 序号 | 条件 | 验证命令 |
|------|------|----------|
| 1 | 已完成教程 09，`blog-backend/` 项目结构完整 | `ls blog-backend/routes/articles.js` 文件存在 |
| 2 | `npm run dev` 能正常启动 | `npm run dev` 终端输出 "Server is running on http://localhost:3000" |
| 3 | 理解 JavaScript 数组的基本操作 | 能看懂 `push`、`find`、`splice` |
| 4 | 已安装 Node.js 18+ | `node -v` 输出 ≥ v18.0.0 |
| 5 | 有 C++ 编译工具（仅 better-sqlite3 需要，若安装失败可用备选方案 sql.js） | Windows：`npm install -g windows-build-tools`（如失败不影响，可用备选方案） |

**一条命令确认前置满足**：

```bash
npm run dev
```

终端输出 "Server is running on http://localhost:3000"，然后 `Ctrl+C` 停止，前置条件满足。

---

## 三、分步操作

### 步骤 1：用 Excel 比喻理解数据库

如果你从未接触过数据库，先用你熟悉的 Excel 来建立一个心智模型：

| 数据库概念 | Excel 比喻 | 说明 |
|-----------|-----------|------|
| **数据库（Database）** | 一个文件夹 | 里面可以放多个 Excel 文件（表） |
| **表（Table）** | 一个 Sheet | 每张 Sheet 存一类数据（如"用户表"、"文章表"） |
| **行（Row）** | 一行数据 | 代表一条记录，如"用户 Alice 的完整信息" |
| **列（Column）** | 一列标题 | 代表一个字段，如 `username`、`email`、`age` |
| **主键（Primary Key）** | 行号 | 唯一标识每一行，绝不重复 |
| **SQL** | Excel 的公式/筛选功能 | 用命令操作数据："把年龄>18 的人找出来" |

**一个具体的对应**：

```
Excel 中的"用户 Sheet"：
┌────┬──────────┬───────────────────┬─────┐
│ id │ username │      email        │ age │
├────┼──────────┼───────────────────┼─────┤
│ 1  │  alice   │ alice@example.com │  25 │
│ 2  │   bob    │ bob@example.com   │  30 │
│ 3  │ charlie  │ charlie@test.com  │  28 │
└────┴──────────┴───────────────────┴─────┘

对应的 SQL 表：
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT,
    email TEXT,
    age INTEGER
);
```

> 和 Excel 的关键区别：数据库可以处理**百万行**数据而不会卡顿；可以同时被多个程序访问；可以做 Excel 做不到的复杂查询（如"找出写过文章数大于 5 的所有用户"）。

---

### 步骤 2：为什么选 SQLite？

市面上有很多数据库：MySQL、PostgreSQL、MongoDB、Oracle……为什么本教程选 SQLite？

| 对比维度 | SQLite | MySQL / PostgreSQL |
|---------|--------|-------------------|
| 安装 | **零**，一个 npm install 搞定 | 需要下载安装服务器软件，配置端口、用户名、密码 |
| 运行方式 | 嵌入在你的 Node.js 进程里 | 独立运行的服务器进程，需要 `mysql.server start` |
| 数据存储 | **一个文件**（`blog.db`），拷贝即备份 | 一堆系统文件，不能直接拷贝 |
| 并发能力 | 适合单机、少量并发（学习/小型项目足够） | 适合高并发、多服务器 |
| 配置 | 无需配置 | 需要配置连接字符串、端口、权限 |
| 适用场景 | 学习、移动 App、桌面软件、小型网站 | 大型网站、微服务、需要多用户并发写入 |

**一句话总结**：SQLite 是你学数据库的"自行车"——简单、够用、不摔跤。MySQL/PostgreSQL 是"汽车"——功能更强，但需要考驾照（安装配置）。等你学会了骑自行车，以后开汽车只是操作方式不同，原理完全相通。

> 🔥 **魔鬼细节**：SQLite 是"嵌入式数据库"（Embedded Database）——它不是一个独立的服务器程序，而是以**库**的形式嵌入在你的 Node.js 进程里。这意味着你不需要像 MySQL 那样先 `mysql.server start`，再在代码里 `mysql.connect('localhost:3306')`。SQLite 直接读写文件，你的 Node.js 进程就是数据库服务器。

---

### 步骤 3：安装 better-sqlite3

打开终端，确保在 `blog-backend/` 目录下：

```bash
cd blog-backend
npm install better-sqlite3
```

#### 为什么选 better-sqlite3？

Node.js 中有多个 SQLite 驱动可选。我们选 `better-sqlite3` 有一个关键原因：

**它是同步的。**

```javascript
// better-sqlite3：同步 API，直接拿到结果
const rows = db.prepare('SELECT * FROM users').all();
console.log(rows); // 立即输出，不需要 await

// 其他库：异步 API，需要 async/await 或回调
const rows = await db.all('SELECT * FROM users'); // 需要 async 函数
```

**这对学习阶段极其重要**：你刚学完异步编程（如果有的话），如果现在连数据库操作也要 `async/await`，那就是"两个难点一起打"。`better-sqlite3` 的同步 API 让你专注于学习 SQL 本身，不被异步干扰。

> 🔥 **魔鬼细节**：同步 API 在 Node.js 中通常被视为"阻塞"——会卡住事件循环。但对于 SQLite 来说这不是问题，因为 SQLite 本身是嵌入式的、速度极快（微秒级），而且 SQLite 同一时间只允许一个写入。`better-sqlite3` 的同步设计恰恰是最适合 SQLite 的方式。这也是它名字里 "better" 的由来。

#### 备选方案：如果安装失败

`better-sqlite3` 依赖 node-gyp 编译 C++ 代码。在 Windows 上，如果缺少 C++ 编译工具，安装会失败。错误信息类似：

```
Error: node-gyp rebuild failed
gyp ERR! stack Error: Can't find Python executable "python"
```

**如果遇到这个问题，不要折腾环境——用备选方案 `sql.js`**：

```bash
npm uninstall better-sqlite3      # 如果已经安装失败
npm install sql.js
```

`sql.js` 是纯 JavaScript 实现的 SQLite，不需要任何编译工具。用法略有不同（异步 API），但 SQL 语法完全相同。在后文涉及 `sql.js` 的地方会用 `🔄 备选方案` 标注。

> 以下教程默认用 `better-sqlite3`。如果你用的是 `sql.js`，请参照对应的备选代码块。两种方案学到的 SQL 知识完全一样。

---

### 步骤 4：创建 database/init.js——连接数据库

在 `blog-backend/` 下创建 `database/` 文件夹，然后新建 `init.js`：

```bash
mkdir database
```

```javascript
// database/init.js — 数据库初始化脚本（第一步：连接 + 建测试表）
const Database = require('better-sqlite3');
const path = require('path');

// 创建数据库连接，如果文件不存在会自动创建
// blog.db 文件会出现在 blog-backend/ 目录下（即 process.cwd()）
const db = new Database('blog.db');

console.log('✅ 数据库已连接，blog.db 文件已创建（或打开）');

// 创建一张测试表
db.exec(`
    CREATE TABLE IF NOT EXISTS test (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL
    )
`);

console.log('✅ 测试表 test 已就绪（CREATE TABLE IF NOT EXISTS）');

// 每次脚本运行完关闭连接（脚本模式）
db.close();
console.log('✅ 数据库连接已关闭');
```

<details>
<summary>🔄 sql.js 备选方案：database/init.js</summary>

```javascript
// database/init.js — sql.js 备选方案
const initSqlJs = require('sql.js');
const fs = require('fs');
const path = require('path');

async function main() {
    // 初始化 sql.js
    const SQL = await initSqlJs();

    // 如果 blog.db 文件存在就读取，否则创建空数据库
    let db;
    const dbPath = path.join(__dirname, '..', 'blog.db');
    if (fs.existsSync(dbPath)) {
        const fileBuffer = fs.readFileSync(dbPath);
        db = new SQL.Database(fileBuffer);
    } else {
        db = new SQL.Database();
    }

    console.log('✅ 数据库已连接');

    // 创建测试表
    db.run(`CREATE TABLE IF NOT EXISTS test (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL
    )`);

    console.log('✅ 测试表 test 已就绪');

    // 保存到文件
    const data = db.export();
    const buffer = Buffer.from(data);
    fs.writeFileSync(dbPath, buffer);
    console.log('✅ 数据已保存到 blog.db');
}

main().catch(err => console.error('❌ 错误:', err));
```

</details>

#### 逐行解释

```javascript
const db = new Database('blog.db');
```

这一行做了两件事：
1. 如果 `blog.db` 文件**不存在**——SQLite 自动创建它（空的数据库文件）。
2. 如果 `blog.db` 文件**已存在**——打开它，读取里面的数据。

**blog.db 文件在哪？** 在当前工作目录（`process.cwd()`），也就是你执行 `node` 命令时所在的目录。如果你在 `blog-backend/` 下运行 `node database/init.js`，文件就在 `blog-backend/blog.db`。

> 🔥 **魔鬼细节**：`process.cwd()` 和 `__dirname` 的区别会影响 `.db` 文件的路径：
> - `process.cwd()`：你在**哪个目录下执行的命令**。如果在 `blog-backend/` 下执行 `node database/init.js`，`cwd` = `blog-backend/`。
> - `__dirname`：**当前 JS 文件**所在的目录。`database/init.js` 中，`__dirname` = `blog-backend/database/`。
> - 所以 `new Database('blog.db')` 创建的文件在 `cwd` 下，`new Database(path.join(__dirname, '..', 'blog.db'))` 无论在哪个目录执行，都在 `blog-backend/` 下。**本教程用相对路径 `'blog.db'`，因为所有脚本都约定在 `blog-backend/` 根目录执行。**

```javascript
db.exec(`CREATE TABLE IF NOT EXISTS test (...)`)
```

- `CREATE TABLE`：SQL 语句，创建一张表。
- `IF NOT EXISTS`：如果表已经存在，什么都不做（不会报错）。这叫**幂等性**——重复执行不会出错。
- `db.exec()`：执行一条 SQL 语句，适合建表等不需要参数的操作。

```javascript
db.close();
```

关闭数据库连接。在脚本模式下（运行完就退出的脚本），关闭连接释放资源。后面我们会把连接保持打开，供 Express 服务器持续使用。

#### 运行验证

```bash
node database/init.js
```

预期输出：

```
✅ 数据库已连接，blog.db 文件已创建（或打开）
✅ 测试表 test 已就绪（CREATE TABLE IF NOT EXISTS）
✅ 数据库连接已关闭
```

然后检查文件：

```bash
ls blog.db
```

你会看到项目根目录下出现了一个 `blog.db` 文件（大小约几 KB）。

> 🚫 **不要用记事本打开 `.db` 文件！** 它是二进制文件，打开只会看到乱码。要用 SQL 命令查看内容（下一步就教你）。

---

### 步骤 5：插入第一条数据 + 查询验证

在 `database/init.js` 中，在 `db.close()` 之前添加插入和查询的代码。更新后的完整文件：

```javascript
// database/init.js — 数据库初始化脚本（完整版：连接 → 建表 → 插入 → 查询）
const Database = require('better-sqlite3');

const db = new Database('blog.db');

console.log('✅ 数据库已连接');

// 1. 建表
db.exec(`
    CREATE TABLE IF NOT EXISTS test (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL
    )
`);
console.log('✅ 测试表 test 已就绪');

// 2. 插入数据——用 db.prepare().run()
const insert = db.prepare('INSERT INTO test (name) VALUES (?)');

// 插入多条数据
const result1 = insert.run('Hello, SQLite!');
console.log(`✅ 插入了第 1 条数据，id = ${result1.lastInsertRowid}`);

const result2 = insert.run('Node.js 数据库实战');
console.log(`✅ 插入了第 2 条数据，id = ${result2.lastInsertRowid}`);

const result3 = insert.run('数据持久化测试');
console.log(`✅ 插入了第 3 条数据，id = ${result3.lastInsertRowid}`);

// 3. 查询数据——用 db.prepare().all()
const selectAll = db.prepare('SELECT * FROM test');
const rows = selectAll.all();

console.log('\n📋 test 表中的所有数据：');
rows.forEach(row => {
    console.log(`  id: ${row.id}, name: "${row.name}"`);
});

console.log(`\n共 ${rows.length} 条记录`);

db.close();
console.log('✅ 数据库连接已关闭');
```

<details>
<summary>🔄 sql.js 备选方案：插入和查询</summary>

```javascript
// 在 main() 函数中，建表之后添加：

// 插入数据
db.run("INSERT INTO test (name) VALUES ('Hello, SQLite!')");
db.run("INSERT INTO test (name) VALUES ('Node.js 数据库实战')");
db.run("INSERT INTO test (name) VALUES ('数据持久化测试')");
console.log('✅ 插入了 3 条测试数据');

// 查询数据
const results = db.exec('SELECT * FROM test');
console.log('\n📋 test 表中的所有数据：');
if (results.length > 0) {
    const columns = results[0].columns;
    const values = results[0].values;
    values.forEach(row => {
        console.log(`  id: ${row[0]}, name: "${row[1]}"`);
    });
    console.log(`\n共 ${values.length} 条记录`);
}

// 保存到文件
const data = db.export();
const buffer = Buffer.from(data);
fs.writeFileSync(dbPath, buffer);
```

</details>

#### 逐行解释

```javascript
const insert = db.prepare('INSERT INTO test (name) VALUES (?)');
```

`db.prepare()` 是 `better-sqlite3` 的核心 API。它把一条 SQL 语句**预编译**成一个"语句对象"，之后可以反复调用。

- `?` 是**占位符**（Placeholder），执行时用实际值替换。
- 预编译的好处：如果同一条 SQL 要执行 100 次（如插入 100 条数据），只需要编译一次，然后每次执行时传入不同参数——比每次都重新解析 SQL 高效得多。

> 🔥 **魔鬼细节**：`db.prepare()` 是 `better-sqlite3` 的核心 API，比 `db.exec()` 更安全高效。`db.exec()` 每次执行都要重新解析 SQL 字符串。`db.prepare()` 预编译一次，重复执行——而且它天然防 SQL 注入（因为 `?` 占位符的参数不会被当作 SQL 代码执行）。后面的教程几乎只用 `db.prepare()`。

```javascript
const result = insert.run('Hello, SQLite!');
console.log(result.lastInsertRowid);
```

`.run()` 执行预编译的语句，传入参数替换 `?`。返回值 `result` 有两个关键属性：

| 属性 | 含义 | 示例值 |
|------|------|--------|
| `result.changes` | 受影响的行数（INSERT 时为 1） | `1` |
| `result.lastInsertRowid` | 新插入行的 ID（自增主键的值） | `1`, `2`, `3` |

```javascript
const rows = selectAll.all();
```

`.all()` 执行 SELECT 查询，返回**所有**匹配的行，结果是一个**数组**，每行是一个对象。

```javascript
// 输出示例：
// [
//   { id: 1, name: 'Hello, SQLite!' },
//   { id: 2, name: 'Node.js 数据库实战' },
//   { id: 3, name: '数据持久化测试' }
// ]
```

#### 运行验证

```bash
node database/init.js
```

预期完整输出：

```
✅ 数据库已连接
✅ 测试表 test 已就绪
✅ 插入了第 1 条数据，id = 1
✅ 插入了第 2 条数据，id = 2
✅ 插入了第 3 条数据，id = 3

📋 test 表中的所有数据：
  id: 1, name: "Hello, SQLite!"
  id: 2, name: "Node.js 数据库实战"
  id: 3, name: "数据持久化测试"

共 3 条记录
✅ 数据库连接已关闭
```

**做一个小实验**：再运行一次 `node database/init.js`。你会看到这次输出 `id = 4, 5, 6`——因为 `INSERT` 每次都会追加新行，不会覆盖旧数据。

> 数据现在是存在 `blog.db` 文件里的了——就算你关掉终端、重启电脑，数据都还在。你已经完成了"从内存到硬盘"的关键跨越。

---

### 步骤 6：.db 文件：二进制文件，加入 .gitignore

#### 6.1 .db 文件是什么？

`blog.db` 是一个**二进制文件**（Binary File），不是文本文件。SQLite 用它自己的格式存储数据——包含表结构、索引、数据行等。你不能用记事本或 VS Code 直接打开它来查看数据（打开会是乱码）。

> 要查看 `.db` 文件的内容，你需要通过 SQL 语句（就像步骤 5 做的）或者专门的数据库管理工具（如 DB Browser for SQLite）。

#### 6.2 将 .db 文件加入 .gitignore

`blog.db` 不应该被提交到 Git 仓库，原因有三：
1. **包含实际数据**：可能包含测试时输入的敏感信息。
2. **二进制文件**：Git 对二进制文件的 diff 和合并支持很差。
3. **可由代码生成**：建表脚本（schema.js）可以随时重建数据库结构，测试数据用 seed 脚本生成。

打开 `blog-backend/.gitignore`，添加：

```gitignore
# 数据库文件
*.db
```

如果 `.gitignore` 文件不存在，创建它：

```bash
echo "*.db" > .gitignore
echo "node_modules/" >> .gitignore
```

> 📦 `.gitignore` 的 `*.db` 通配符会忽略所有以 `.db` 结尾的文件，无论它们在哪。如果你将来有特殊需要保留某个 `.db` 文件，可以在 `.gitignore` 中用 `!` 排除：`!important.db`。

---

### 🤔 想多一点：SQLite 真的不需要"启动服务器"吗？

是的。当你写 `new Database('blog.db')` 时，你的 Node.js 进程**就是**数据库服务器。SQLite 以库的形式链接在你的程序里，所有 SQL 操作都发生在你的进程内部。

**对比 MySQL 的工作方式**：

```
MySQL 方式：
  你的代码 → TCP 网络 → MySQL 服务器进程 → 数据文件
  
SQLite 方式：
  你的代码 → better-sqlite3 库 → 数据文件（直接读写）
```

SQLite 省掉了"网络通信"和"独立服务器进程"两层，所以在本地单机场景下反而更快。缺点是同一时间只能有一个进程写入（SQLite 用文件锁保证数据一致性）。

**什么时候 SQLite 不够用？**
- 你的网站同时有几千人在写入（高并发写入）。
- 你需要多台服务器共享同一个数据库。
- 你需要复杂的用户权限管理（谁可以读、谁可以写）。

这些情况下你应该换 MySQL 或 PostgreSQL。但本教程的博客系统——几百个用户、几十篇文章——SQLite 绰绰有余。

---

### ❌ 常见错误 → ✅ 解决方案

| 错误信息 / 现象 | 原因 | 解决 |
|-----------------|------|------|
| `npm install better-sqlite3` 报 `node-gyp rebuild` 错误 | Windows 缺少 C++ 编译工具（Python、Visual Studio Build Tools） | 改用 `sql.js`：`npm install sql.js`（纯 JS，无需编译） |
| `node database/init.js` 报 `Cannot find module 'better-sqlite3'` | 没安装或安装到了错误的目录 | 确认在 `blog-backend/` 下执行 `npm install better-sqlite3` |
| 运行 `init.js` 后没有出现 `blog.db` 文件 | `db.close()` 前程序崩溃了，数据没写入磁盘 | 检查代码是否有语法错误，确保 `db.close()` 被调用 |
| 第二次运行 `init.js` 数据翻倍而不是覆盖 | `INSERT INTO` 是追加操作，不是替换 | 正常现象——数据会持续累积。需要清空数据时删掉 `blog.db` 重新运行 |
| 用记事本打开 `.db` 文件看到乱码 | `.db` 是二进制文件，不是文本 | 用 SQL 语句查询数据，或安装 DB Browser for SQLite 查看 |
| `db.prepare is not a function` | `better-sqlite3` 版本太旧或没正确 `require` | 确认 `const Database = require('better-sqlite3')` 且 `const db = new Database('blog.db')` |
| Git 提交时 `blog.db` 被提交了 | `.gitignore` 写错了或放错了位置 | 确认 `.gitignore` 在 `blog-backend/` 根目录，内容包含 `*.db` |

---

## 四、完整代码清单

### `blog-backend/database/init.js`（本章新建）

```javascript
// database/init.js — 数据库初始化脚本（完整版）
const Database = require('better-sqlite3');

const db = new Database('blog.db');

console.log('✅ 数据库已连接');

// 1. 建表
db.exec(`
    CREATE TABLE IF NOT EXISTS test (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL
    )
`);
console.log('✅ 测试表 test 已就绪');

// 2. 插入数据
const insert = db.prepare('INSERT INTO test (name) VALUES (?)');

const result1 = insert.run('Hello, SQLite!');
console.log(`✅ 插入了第 1 条数据，id = ${result1.lastInsertRowid}`);

const result2 = insert.run('Node.js 数据库实战');
console.log(`✅ 插入了第 2 条数据，id = ${result2.lastInsertRowid}`);

const result3 = insert.run('数据持久化测试');
console.log(`✅ 插入了第 3 条数据，id = ${result3.lastInsertRowid}`);

// 3. 查询数据
const selectAll = db.prepare('SELECT * FROM test');
const rows = selectAll.all();

console.log('\n📋 test 表中的所有数据：');
rows.forEach(row => {
    console.log(`  id: ${row.id}, name: "${row.name}"`);
});

console.log(`\n共 ${rows.length} 条记录`);

db.close();
console.log('✅ 数据库连接已关闭');
```

### `blog-backend/.gitignore`（本章更新）

```gitignore
node_modules/
*.db
```

### `blog-backend/` 目录结构（本章最终状态）

```
blog-backend/
├── server.js
├── package.json
├── package-lock.json
├── .gitignore           ← 本章更新：添加 *.db
├── blog.db              ← 本章新建：数据库文件（已被 .gitignore 忽略）
├── node_modules/
├── database/            ← 本章新建
│   └── init.js          ← 本章新建：初始化脚本
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
| 1 | `npm install better-sqlite3` | 安装成功，`package.json` 中 `dependencies` 出现 `better-sqlite3` |
| 2 | `node database/init.js` | 输出 "✅ 数据库已连接"，"✅ 测试表 test 已就绪"，插入 3 条数据，查询出 3 条 |
| 3 | `ls blog.db`（或 `dir blog.db`） | `blog.db` 文件存在 |
| 4 | 再次运行 `node database/init.js` | 输出 id = 4, 5, 6，总共 6 条数据（第二次运行追加了 3 条） |
| 5 | 删除 `blog.db`，再运行 `node database/init.js` | 输出 id = 1, 2, 3，总共 3 条数据（重新开始） |
| 6 | 检查 `node_modules/better-sqlite3/` | 文件夹存在，库已安装 |
| 7 | 如果用的是 `sql.js`：检查 `node_modules/sql.js/` | 文件夹存在，无需编译 |

全部通过？你已经从"内存存储"迈入了"数据库时代"。`.db` 文件就是你数据的永久家。

---

## 六、小结表格

| 学到的东西 | 一句话解释 |
|-----------|-----------|
| 数据库基本概念 | 数据库 = 文件夹，表 = Sheet，行 = 一条记录，列 = 一个字段 |
| 为什么选 SQLite | 零配置、一个文件、嵌入式、不需要安装服务器 |
| 为什么选 better-sqlite3 | 同步 API，学习阶段不用和异步打架；预编译语句，安全高效 |
| `new Database('blog.db')` | 创建/打开数据库文件，不存在则自动创建 |
| `db.prepare().run()` | 执行 INSERT/UPDATE/DELETE，返回 `{ changes, lastInsertRowid }` |
| `db.prepare().all()` | 执行 SELECT 查询，返回所有行（数组） |
| `?` 占位符 | 防 SQL 注入的参数替换方式 |
| `.db` 文件 | SQLite 的二进制数据文件，不能直接打开，应加入 `.gitignore` |
| `CREATE TABLE IF NOT EXISTS` | 幂等建表——重复执行不报错 |

---

## 七、术语附录

| 术语 | 英文 | 通俗解释 | 本章出现位置 | 字面陷阱 |
|------|------|----------|-------------|----------|
| 数据库（Database） | Database | 有组织的数据集合，存于硬盘上。可以理解为"一个包含多张表的容器"。 | 步骤 1 | 不是"数据仓库"——数据库不只是存数据，还包含数据之间的关系和操作规则。 |
| SQLite | — | 一种轻量级的嵌入式关系型数据库。数据存在一个 `.db` 文件里，不需要安装服务器软件。 | 步骤 2 | "Lite" 不是"功能弱"——SQLite 支持完整的 SQL 标准，只是架构上更轻量（无服务器进程）。 |
| 关系型数据库 | Relational Database | 用表（Table）存储数据，通过外键表示表与表之间关系的数据库。SQLite、MySQL、PostgreSQL 都是关系型数据库。 | 步骤 1 | 不是"有关系"——"关系"指表与表之间通过共同字段（如 id）建立的关联。 |
| 表（Table） | Table | 数据库中按行和列组织的数据集合。一张表存一类数据（如 users 表、articles 表）。 | 步骤 1 | 不是 HTML 的 `<table>`——虽然长得像二维表格，但它是存在硬盘上的结构化数据。 |
| 行（Row） | Row | 表中的一条记录。一行代表一个实体（如一个用户、一篇文章）。 | 步骤 1 | 不是"一排"——在数据库中"行"= "一条记录"。 |
| 列（Column） | Column | 表中的一个字段。一列代表一类属性（如 username、email、age）。 | 步骤 1 | 不是"竖着的一条线"——列定义了表中每条记录可以有哪些属性。 |
| 主键（Primary Key） | Primary Key | 表中唯一标识每一行的字段。通常是 `id` 列，自动递增。一个表只能有一个主键。 | 步骤 1 | 不是"主要的键"——是"唯一的身份标识"，就像身份证号。 |
| better-sqlite3 | — | Node.js 的 SQLite 驱动库，同步 API，高性能。名字暗示它比同类库更好。 | 步骤 3 | 不是"更好的 SQLite 3"——它是 SQLite 3 的**驱动**（让 Node.js 能操作 SQLite），不是 SQLite 本身的改进版。 |

---

## 八、已知坑点与禁止事项

1. **`better-sqlite3` 在 Windows 上可能安装失败**：因为需要 C++ 编译工具。如果失败，不要折腾环境——直接用 `sql.js`（纯 JS 实现）。两种方案学到的 SQL 知识完全一样。

2. **`.db` 文件不要用记事本打开**：二进制文件，打开只能看到乱码。用 SQL 语句或 DB Browser for SQLite 查看。

3. **`.db` 文件必须加入 `.gitignore`**：包含实际数据，不应提交到版本控制。用 `*.db` 通配符忽略所有数据库文件。

4. **`process.cwd()` 和 `__dirname` 的路径差异**：`new Database('blog.db')` 用相对路径，文件创建在当前工作目录。如果用绝对路径（`path.join(__dirname, '..', 'blog.db')`），无论在哪里执行 `node` 命令，文件都在 `blog-backend/` 下。

5. **`INSERT` 是追加，不是覆盖**：多次运行同一个 INSERT 脚本，数据会一直累积，不会自动清空。如果要重新开始，删除 `blog.db` 文件即可。

6. **`db.prepare()` 的 SQL 字符串中不要用模板字符串拼接参数**：
   ```javascript
   // ❌ 危险：SQL 注入
   db.prepare(`SELECT * FROM users WHERE name = '${username}'`).all();
   
   // ✅ 正确：用 ? 占位符
   db.prepare('SELECT * FROM users WHERE name = ?').all(username);
   ```

---

## 九、下一步建议

你已经创建了数据库、学会了建表和基本的插入查询。但这些还是"裸"的 SQL——接下来我们要为博客系统设计真正的表结构：

- **下一章**：[13-建表：博客系统的表结构设计](13-建表：博客系统的表结构设计.md)——设计 users、articles、comments 三张表，定义字段类型、约束、外键关系，创建 `database/schema.js`，在 `server.js` 启动时自动初始化数据库。
- **延伸思考**：你现在每次插入数据都要写完整的 INSERT 语句。后面你会把这些操作封装在 Express 路由里——用户发一个 POST 请求，路由里执行一条 INSERT，数据就存进去了。

---

> 📊 本教程无可视化
>
> 本教程编辑记录：2026-06-12 初始版本。