# 14-SQL增删改查实战

> "第 13 章建好了三张空表，就像盖好了房子但没放家具。这一章我们把 SQL 四大操作——INSERT 插入、SELECT 查询、UPDATE 更新、DELETE 删除——全部拿下。还会学到 JOIN 关联查询，把文章和作者名一起查出来；学到参数化查询，防止 SQL 注入；最后写一个 seed 脚本，一键插入测试数据，让空荡荡的数据库热闹起来。"

---

## 一、目标与完成效果

**一句话目标**：掌握 SQL 的 INSERT/SELECT/UPDATE/DELETE 四种核心操作，理解 JOIN 关联查询，学会参数化查询防止 SQL 注入，创建 `database/seed.js` 插入测试数据。

**完成后的可观测效果**：
- 你创建了 `database/seed.js`，运行后向三张表插入了 2 个用户、5 篇文章、多条评论。
- 你理解了 `db.prepare().run()` / `.get()` / `.all()` 三种方法的使用场景和返回值。
- 你亲眼看到了 SQL 注入攻击的效果，并学会了用参数化查询防御。
- 你理解了 JOIN 的两种类型（INNER JOIN 和 LEFT JOIN），能写出"查询文章并带出作者名"的 SQL。
- 你学会了事务（Transaction）——批量插入时，要么全成功，要么全失败。

---

## 二、前置条件

| 序号 | 条件 | 验证命令 |
|------|------|----------|
| 1 | 已完成教程 13，`database/schema.js` 创建完毕 | `npm run dev` 输出 "✅ 数据库表结构已就绪" |
| 2 | `better-sqlite3`（或 `sql.js`）已安装 | `ls node_modules/better-sqlite3` 文件夹存在 |
| 3 | 理解 `db.prepare()` 和 `?` 占位符的基本用法 | 第 12 章步骤 5 |

**一条命令确认前置满足**：

```bash
npm run dev
```

输出 "✅ 数据库表结构已就绪（users, articles, comments）"，然后 `Ctrl+C` 停止，前置条件满足。

---

## 三、分步操作

### 步骤 1：INSERT——插入数据

INSERT 是 SQL 中用得最多的操作之一。它有三种常见写法：

#### 1.1 单条插入

```javascript
const Database = require('better-sqlite3');
const db = new Database('blog.db');

// 预编译 INSERT 语句
const insertUser = db.prepare(
    'INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)'
);

// 执行插入
const result = insertUser.run('alice', 'alice@example.com', 'hashed_password_placeholder');
console.log(`新用户 ID: ${result.lastInsertRowid}`);  // 输出 1
console.log(`影响行数: ${result.changes}`);            // 输出 1
```

**INSERT 语法结构**：

```sql
INSERT INTO 表名 (列1, 列2, ...) VALUES (值1, 值2, ...)
```

- 列名和值一一对应，顺序要一致。
- 如果某列有 `DEFAULT` 值（如 `created_at`），可以不写——数据库会自动填充。
- 自增主键（`id`）不需要手动指定。

#### 1.2 多条插入——用事务

如果要插入 100 条数据，一条一条 `run()` 会很慢（每次都要写磁盘）。更好的做法是**批量插入 + 事务**：

```javascript
// 准备数据
const users = [
    ['alice', 'alice@example.com', 'hash_placeholder'],
    ['bob', 'bob@example.com', 'hash_placeholder'],
    ['charlie', 'charlie@example.com', 'hash_placeholder']
];

// 开启事务 → 批量插入 → 提交事务
const insertMany = db.transaction((users) => {
    const stmt = db.prepare(
        'INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)'
    );
    for (const user of users) {
        stmt.run(...user);  // ...user 展开数组为三个参数
    }
});

insertMany(users);
console.log('✅ 批量插入完成');
```

#### 事务（Transaction）是什么？

**比喻**：你把一笔钱从 A 账户转到 B 账户，需要两步——A 扣钱，B 加钱。如果第一步成功了但第二步失败了，钱就凭空消失了。事务保证这两步**要么全部成功，要么全部失败**（回滚）。

```
事务 = 一个"原子操作包"
  ├── 操作1
  ├── 操作2
  └── 操作3
→ 全部成功 → 提交（COMMIT）
→ 任意一步失败 → 回滚（ROLLBACK），所有操作撤销
```

> 🔥 **魔鬼细节**：`better-sqlite3` 的 `db.transaction()` 返回一个函数。这个函数内部的代码要么全部成功，要么全部回滚。如果中间抛出异常，事务自动回滚。这是 `better-sqlite3` 比其他库强的地方——事务管理非常简单。

#### 1.3 返回 lastInsertRowid

```javascript
const result = insertUser.run('alice', 'alice@example.com', 'hash');
console.log(result.lastInsertRowid);  // 1
```

`lastInsertRowid` 是刚插入那一行的主键值。在博客系统中，创建文章后需要返回文章的 ID——这个值就派上用场了。

---

### 步骤 2：SELECT——查询数据

SELECT 是使用频率最高的 SQL 语句。它有多种变体：

#### 2.1 全表查询 → .all()

```javascript
const selectAll = db.prepare('SELECT * FROM users');
const users = selectAll.all();
console.log(users);
// [
//   { id: 1, username: 'alice', email: 'alice@example.com', ... },
//   { id: 2, username: 'bob', email: 'bob@example.com', ... }
// ]
```

`.all()` 返回**所有匹配的行**，结果是一个数组。如果表是空的，返回 `[]`（空数组，不是 `null` 或 `undefined`）。

#### 2.2 条件查询 → .get()

```javascript
const selectById = db.prepare('SELECT * FROM users WHERE id = ?');
const user = selectById.get(1);
console.log(user);
// { id: 1, username: 'alice', email: 'alice@example.com', ... }

// 找不到时返回 undefined
const notFound = selectById.get(999);
console.log(notFound);  // undefined
```

`.get()` 返回**第一行**。如果查询结果只有一行（如按主键查询），用 `.get()` 直接拿到对象。找不到时返回 `undefined`。

> 🔥 **魔鬼细节**：`.get()` 返回 `undefined`（找不到）或一个对象（找到了）。`.all()` 返回 `[]`（找不到）或一个数组（找到了）。**永远不要假设 `.get()` 一定返回对象**——找不到时返回 `undefined`，如果你直接 `user.username` 会报 `TypeError: Cannot read properties of undefined`。

#### 2.3 排序 → ORDER BY

```javascript
// 按创建时间倒序（最新的在前面）
const selectLatest = db.prepare(
    'SELECT * FROM articles ORDER BY created_at DESC'
);
const latestArticles = selectLatest.all();
```

| 排序关键字 | 含义 |
|-----------|------|
| `ASC` | 升序（Ascending）——从小到大，旧的在前 |
| `DESC` | 降序（Descending）——从大到小，新的在前 |

#### 2.4 限制数量 → LIMIT

```javascript
// 只取前 10 条
const selectTop10 = db.prepare(
    'SELECT * FROM articles ORDER BY created_at DESC LIMIT 10'
);
```

#### 2.5 .get() / .all() / .run() 对比

| 方法 | 用途 | 返回值 | 找不到时 |
|------|------|--------|----------|
| `.run()` | INSERT / UPDATE / DELETE | `{ changes, lastInsertRowid }` | `changes = 0` |
| `.get()` | SELECT 单行 | 对象 或 `undefined` | `undefined` |
| `.all()` | SELECT 多行 | 数组（每行是一个对象） | `[]` |

---

### 步骤 3：UPDATE——更新数据

```javascript
const updateEmail = db.prepare(
    'UPDATE users SET email = ? WHERE id = ?'
);

const result = updateEmail.run('new-email@example.com', 1);
console.log(`更新了 ${result.changes} 行`);  // 1
```

**UPDATE 语法结构**：

```sql
UPDATE 表名 SET 列1 = 值1, 列2 = 值2 WHERE 条件
```

> ⚠️ **致命警告：UPDATE 不加 WHERE 会更新所有行！**

```javascript
// ❌ 危险！这会把所有用户的 email 都改成同一个值
db.prepare('UPDATE users SET email = ?').run('same@example.com');

// ✅ 正确：始终带 WHERE
db.prepare('UPDATE users SET email = ? WHERE id = ?').run('new@example.com', 1);
```

**`result.changes`**：返回受影响的行数。如果 `changes = 0`，说明没有行被更新——可能是 `WHERE` 条件不匹配（ID 不存在）。

---

### 步骤 4：DELETE——删除数据

```javascript
const deleteUser = db.prepare('DELETE FROM users WHERE id = ?');
const result = deleteUser.run(1);
console.log(`删除了 ${result.changes} 行`);  // 1
```

**DELETE 语法结构**：

```sql
DELETE FROM 表名 WHERE 条件
```

> ⚠️ **致命警告：DELETE 不加 WHERE 会删除所有行！**

```javascript
// ❌ 灾难！这会清空整个 users 表
db.prepare('DELETE FROM users').run();

// ✅ 正确：始终带 WHERE
db.prepare('DELETE FROM users WHERE id = ?').run(1);
```

**安全建议：先 SELECT 确认再 DELETE**：

```javascript
// 1. 先查一下，确认是否是要删的那条
const target = db.prepare('SELECT * FROM users WHERE id = ?').get(1);
console.log('将要删除:', target);

// 2. 确认无误后再删
if (target) {
    db.prepare('DELETE FROM users WHERE id = ?').run(1);
    console.log('✅ 已删除');
}
```

---

### 步骤 5：JOIN——把两张表的数据连起来

你的 `articles` 表里只有 `author_id`（一个数字），没有作者名。如果要显示"文章标题 + 作者名"，就需要 JOIN。

#### 5.1 INNER JOIN——只返回匹配的行

```sql
SELECT articles.title, users.username
FROM articles
INNER JOIN users ON articles.author_id = users.id;
```

**比喻**：INNER JOIN 就像"门当户对的配对"——只有双方都有匹配的才出现。如果某篇文章的 `author_id` 在 `users` 表中不存在，这篇文章就不会出现在结果中。

**用 JavaScript 来理解**：

```javascript
// INNER JOIN 的等价 JavaScript 逻辑
const result = articles
    .filter(article => users.find(u => u.id === article.author_id))  // 双方都有
    .map(article => {
        const user = users.find(u => u.id === article.author_id);
        return { title: article.title, username: user.username };
    });
```

#### 5.2 LEFT JOIN——返回左表所有行

```sql
SELECT articles.title, users.username
FROM articles
LEFT JOIN users ON articles.author_id = users.id;
```

**比喻**：LEFT JOIN 就像"点名"——左表（articles）的所有行都出现，右表（users）能匹配上的就填，匹配不上的填 NULL。

**用 JavaScript 来理解**：

```javascript
// LEFT JOIN 的等价 JavaScript 逻辑
const result = articles.map(article => {
    const user = users.find(u => u.id === article.author_id);
    return {
        title: article.title,
        username: user ? user.username : null  // 没匹配到就填 null
    };
});
```

#### 5.3 实战：查询文章同时带出作者名

```javascript
const selectArticlesWithAuthor = db.prepare(`
    SELECT 
        articles.id,
        articles.title,
        articles.content,
        articles.created_at,
        users.username AS author_name
    FROM articles
    INNER JOIN users ON articles.author_id = users.id
    ORDER BY articles.created_at DESC
`);

const articles = selectArticlesWithAuthor.all();
console.log(articles);
// [
//   { id: 1, title: '...', content: '...', created_at: '...', author_name: 'alice' },
//   ...
// ]
```

#### 5.4 JOIN 不止两张表——三表 JOIN

查询"某篇文章下的所有评论，带出评论者用户名"：

```sql
SELECT 
    comments.id,
    comments.content,
    comments.created_at,
    users.username AS commenter
FROM comments
INNER JOIN users ON comments.user_id = users.id
WHERE comments.article_id = ?
ORDER BY comments.created_at DESC;
```

---

### 步骤 6：参数化查询 vs SQL 注入

#### 6.1 什么是 SQL 注入？

假设你有一个登录接口，用户输入用户名和密码。如果你用字符串拼接来构造 SQL：

```javascript
// ❌ 危险！字符串拼接
const username = req.body.username;  // 用户输入：' OR '1'='1
const password = req.body.password;  // 随便输

const sql = `SELECT * FROM users WHERE username = '${username}' AND password = '${password}'`;
// 拼接后的 SQL：
// SELECT * FROM users WHERE username = '' OR '1'='1' AND password = 'whatever'
//                                ↑ 这里永远为 true！↑
// 结果：返回所有用户！第一个用户被当作"登录成功"的用户。
```

这就是**SQL 注入**——攻击者通过在输入中注入 SQL 代码，改变你的 SQL 语句的语义。

#### 6.2 参数化查询——终极防御

```javascript
// ✅ 安全：参数化查询
const stmt = db.prepare('SELECT * FROM users WHERE username = ? AND password_hash = ?');
const user = stmt.get(username, password_hash);
```

`?` 占位符的参数**永远不会被当作 SQL 代码执行**。即使用户输入 `' OR '1'='1`，它也只是被当作普通字符串 `"' OR '1'='1"` 来匹配——不会改变 SQL 语句的结构。

#### 6.3 SQLite 的 ? 占位符 vs 其他数据库

| 数据库 | 占位符 | 示例 |
|--------|--------|------|
| SQLite | `?` | `WHERE id = ?` |
| MySQL | `?` | `WHERE id = ?` |
| PostgreSQL | `$1, $2, ...` | `WHERE id = $1` |
| 所有数据库通用 | 命名参数（`better-sqlite3` 支持） | `WHERE id = @id` |

> `better-sqlite3` 也支持命名参数：`db.prepare('... WHERE id = @id').get({ id: 1 })`。本教程用 `?` 因为最简单。

---

### 步骤 7：创建 database/seed.js——插入测试数据

现在把前面学的 INSERT、事务、参数化查询全部用上，写一个种子脚本，一键填充测试数据。

创建 `database/seed.js`：

```javascript
// database/seed.js — 插入测试数据
const Database = require('better-sqlite3');

const db = new Database('blog.db');
db.pragma('foreign_keys = ON');

console.log('🌱 开始插入测试数据...\n');

// ========== 1. 插入用户 ==========
const insertUser = db.prepare(
    'INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)'
);

// 用事务批量插入用户
const seedUsers = db.transaction(() => {
    insertUser.run('alice', 'alice@example.com', 'hash_alice_placeholder');
    insertUser.run('bob', 'bob@example.com', 'hash_bob_placeholder');
    insertUser.run('charlie', 'charlie@example.com', 'hash_charlie_placeholder');
});

seedUsers();
console.log('✅ 插入了 3 个用户');

// ========== 2. 插入文章 ==========
const insertArticle = db.prepare(
    'INSERT INTO articles (title, content, author_id) VALUES (?, ?, ?)'
);

const seedArticles = db.transaction(() => {
    insertArticle.run('Node.js 入门指南', 'Node.js 是一个基于 Chrome V8 引擎的 JavaScript 运行时环境，让 JavaScript 可以在服务器端运行。它的特点是事件驱动、非阻塞 I/O，非常适合构建高并发的网络应用。', 1);
    insertArticle.run('Express 框架详解', 'Express 是 Node.js 最流行的 Web 开发框架。它提供了简洁的路由系统、中间件机制和模板引擎支持，让开发者可以快速构建 Web 应用和 API。', 1);
    insertArticle.run('RESTful API 设计最佳实践', 'RESTful 是一种 API 设计风格，核心思想是用 URL 表示资源，用 HTTP 方法表示操作。好的 API 设计应该遵循统一接口、无状态、可缓存等原则。', 2);
    insertArticle.run('SQLite 入门教程', 'SQLite 是一个轻量级的嵌入式关系型数据库。它不需要安装服务器，一个文件就是一个数据库，非常适合学习和小型项目使用。', 2);
    insertArticle.run('为什么需要参数化查询', 'SQL 注入是最常见的 Web 安全漏洞之一。攻击者通过在输入中注入恶意 SQL 代码，可以绕过认证、窃取数据甚至删除整个数据库。参数化查询是防御 SQL 注入的最有效手段。', 3);
});

seedArticles();
console.log('✅ 插入了 5 篇文章');

// ========== 3. 插入评论 ==========
const insertComment = db.prepare(
    'INSERT INTO comments (content, article_id, user_id) VALUES (?, ?, ?)'
);

const seedComments = db.transaction(() => {
    // alice 的文章（id=1,2）下的评论
    insertComment.run('写得很好，深入浅出！', 1, 2);
    insertComment.run('Node.js 入门必读，推荐！', 1, 3);
    insertComment.run('Express 的部分讲得很清楚', 2, 2);
    // bob 的文章（id=3,4）下的评论
    insertComment.run('RESTful 设计原则总结得很到位', 3, 1);
    insertComment.run('SQLite 确实好用，零配置太方便了', 4, 1);
    insertComment.run('学到了很多，感谢分享', 4, 3);
    // charlie 的文章（id=5）下的评论
    insertComment.run('SQL 注入的例子很直观，一下子就懂了', 5, 1);
    insertComment.run('安全是每个开发者都应该重视的', 5, 2);
});

seedComments();
console.log('✅ 插入了 8 条评论');

// ========== 4. 验证：查询统计 ==========
const userCount = db.prepare('SELECT COUNT(*) AS count FROM users').get();
const articleCount = db.prepare('SELECT COUNT(*) AS count FROM articles').get();
const commentCount = db.prepare('SELECT COUNT(*) AS count FROM comments').get();

console.log(`\n📊 数据统计：`);
console.log(`  用户：${userCount.count} 人`);
console.log(`  文章：${articleCount.count} 篇`);
console.log(`  评论：${commentCount.count} 条`);
console.log(`\n🌱 测试数据插入完成！`);

db.close();
```

<details>
<summary>🔄 sql.js 备选方案：database/seed.js</summary>

```javascript
// database/seed.js — sql.js 备选方案
const initSqlJs = require('sql.js');
const fs = require('fs');
const path = require('path');

async function main() {
    const SQL = await initSqlJs();

    const dbPath = path.join(__dirname, '..', 'blog.db');
    let db;
    if (fs.existsSync(dbPath)) {
        const fileBuffer = fs.readFileSync(dbPath);
        db = new SQL.Database(fileBuffer);
    } else {
        db = new SQL.Database();
    }

    db.run('PRAGMA foreign_keys = ON');

    console.log('🌱 开始插入测试数据...\n');

    // 插入用户
    db.run("INSERT INTO users (username, email, password_hash) VALUES ('alice', 'alice@example.com', 'hash_alice_placeholder')");
    db.run("INSERT INTO users (username, email, password_hash) VALUES ('bob', 'bob@example.com', 'hash_bob_placeholder')");
    db.run("INSERT INTO users (username, email, password_hash) VALUES ('charlie', 'charlie@example.com', 'hash_charlie_placeholder')");
    console.log('✅ 插入了 3 个用户');

    // 插入文章
    db.run("INSERT INTO articles (title, content, author_id) VALUES ('Node.js 入门指南', 'Node.js 是一个基于 Chrome V8 引擎的 JavaScript 运行时...', 1)");
    db.run("INSERT INTO articles (title, content, author_id) VALUES ('Express 框架详解', 'Express 是 Node.js 最流行的 Web 开发框架...', 1)");
    db.run("INSERT INTO articles (title, content, author_id) VALUES ('RESTful API 设计最佳实践', 'RESTful 是一种 API 设计风格...', 2)");
    db.run("INSERT INTO articles (title, content, author_id) VALUES ('SQLite 入门教程', 'SQLite 是一个轻量级的嵌入式关系型数据库...', 2)");
    db.run("INSERT INTO articles (title, content, author_id) VALUES ('为什么需要参数化查询', 'SQL 注入是最常见的 Web 安全漏洞之一...', 3)");
    console.log('✅ 插入了 5 篇文章');

    // 插入评论
    db.run("INSERT INTO comments (content, article_id, user_id) VALUES ('写得很好，深入浅出！', 1, 2)");
    db.run("INSERT INTO comments (content, article_id, user_id) VALUES ('Node.js 入门必读，推荐！', 1, 3)");
    db.run("INSERT INTO comments (content, article_id, user_id) VALUES ('Express 的部分讲得很清楚', 2, 2)");
    db.run("INSERT INTO comments (content, article_id, user_id) VALUES ('RESTful 设计原则总结得很到位', 3, 1)");
    db.run("INSERT INTO comments (content, article_id, user_id) VALUES ('SQLite 确实好用，零配置太方便了', 4, 1)");
    db.run("INSERT INTO comments (content, article_id, user_id) VALUES ('学到了很多，感谢分享', 4, 3)");
    db.run("INSERT INTO comments (content, article_id, user_id) VALUES ('SQL 注入的例子很直观，一下子就懂了', 5, 1)");
    db.run("INSERT INTO comments (content, article_id, user_id) VALUES ('安全是每个开发者都应该重视的', 5, 2)");
    console.log('✅ 插入了 8 条评论');

    // 保存到文件
    const data = db.export();
    fs.writeFileSync(dbPath, Buffer.from(data));
    console.log('\n🌱 测试数据已保存到 blog.db');
}

main().catch(err => console.error('❌ 错误:', err));
```

</details>

#### 运行验证

```bash
node database/seed.js
```

预期输出：

```
🌱 开始插入测试数据...

✅ 插入了 3 个用户
✅ 插入了 5 篇文章
✅ 插入了 8 条评论

📊 数据统计：
  用户：3 人
  文章：5 篇
  评论：8 条

🌱 测试数据插入完成！
```

> 如果 `blog.db` 已经存在（之前 `npm run dev` 创建了），seed 脚本会追加数据。如果数据重复了，删掉 `blog.db` 再运行：`rm blog.db && npm run dev`（这会重建表结构），然后 `node database/seed.js`（插入测试数据）。

---

### 🤔 想多一点：为什么外键约束让 INSERT 有顺序要求？

因为 `articles.author_id` 引用 `users.id`，你必须先插入 `users`，再插入 `articles`。如果反过来，先插入文章，`author_id = 1` 但 `users` 表里还没有 `id = 1` 的用户——外键约束会拒绝插入。

**这就是"外键约束"对操作顺序的要求**。在 seed 脚本中，我们严格按照 users → articles → comments 的顺序插入，确保数据引用的完整性。

---

### ❌ 常见错误 → ✅ 解决方案

| 错误信息 / 现象 | 原因 | 解决 |
|-----------------|------|------|
| `FOREIGN KEY constraint failed` | 插入的数据引用了不存在的外键值 | 先插入被引用的数据（如 users），再插入引用它的数据（如 articles） |
| `UNIQUE constraint failed: users.username` | 插入的用户名已存在 | 换一个不重复的用户名，或先删掉旧数据 |
| `NOT NULL constraint failed: articles.title` | 插入时没提供必填字段的值 | 确认 INSERT 语句包含了所有 NOT NULL 的列 |
| `UPDATE` 后所有行的值都变了 | 忘了加 `WHERE` 条件 | 始终在 UPDATE 和 DELETE 后加 `WHERE` |
| `DELETE` 后整个表空了 | 忘了加 `WHERE` 条件 | 同上——先 `SELECT` 确认再 `DELETE` |
| `db.prepare().get()` 返回 `undefined` 导致 `user.username` 报错 | 查询结果不存在 | 每次 `.get()` 后先判断 `if (user)` 再使用 |
| `result.changes` 为 0 | WHERE 条件没有匹配到任何行 | 检查 `WHERE` 条件是否正确，ID 是否存在 |
| 种子脚本运行两次后数据翻倍 | INSERT 是追加操作 | 删除 `blog.db` 后重新运行 `npm run dev && node database/seed.js` |

---

## 四、完整代码清单

### `blog-backend/database/seed.js`（本章新建）

```javascript
// database/seed.js — 插入测试数据
const Database = require('better-sqlite3');

const db = new Database('blog.db');
db.pragma('foreign_keys = ON');

console.log('🌱 开始插入测试数据...\n');

// ========== 1. 插入用户 ==========
const insertUser = db.prepare(
    'INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)'
);

const seedUsers = db.transaction(() => {
    insertUser.run('alice', 'alice@example.com', 'hash_alice_placeholder');
    insertUser.run('bob', 'bob@example.com', 'hash_bob_placeholder');
    insertUser.run('charlie', 'charlie@example.com', 'hash_charlie_placeholder');
});

seedUsers();
console.log('✅ 插入了 3 个用户');

// ========== 2. 插入文章 ==========
const insertArticle = db.prepare(
    'INSERT INTO articles (title, content, author_id) VALUES (?, ?, ?)'
);

const seedArticles = db.transaction(() => {
    insertArticle.run('Node.js 入门指南', 'Node.js 是一个基于 Chrome V8 引擎的 JavaScript 运行时环境，让 JavaScript 可以在服务器端运行。它的特点是事件驱动、非阻塞 I/O，非常适合构建高并发的网络应用。', 1);
    insertArticle.run('Express 框架详解', 'Express 是 Node.js 最流行的 Web 开发框架。它提供了简洁的路由系统、中间件机制和模板引擎支持，让开发者可以快速构建 Web 应用和 API。', 1);
    insertArticle.run('RESTful API 设计最佳实践', 'RESTful 是一种 API 设计风格，核心思想是用 URL 表示资源，用 HTTP 方法表示操作。好的 API 设计应该遵循统一接口、无状态、可缓存等原则。', 2);
    insertArticle.run('SQLite 入门教程', 'SQLite 是一个轻量级的嵌入式关系型数据库。它不需要安装服务器，一个文件就是一个数据库，非常适合学习和小型项目使用。', 2);
    insertArticle.run('为什么需要参数化查询', 'SQL 注入是最常见的 Web 安全漏洞之一。攻击者通过在输入中注入恶意 SQL 代码，可以绕过认证、窃取数据甚至删除整个数据库。参数化查询是防御 SQL 注入的最有效手段。', 3);
});

seedArticles();
console.log('✅ 插入了 5 篇文章');

// ========== 3. 插入评论 ==========
const insertComment = db.prepare(
    'INSERT INTO comments (content, article_id, user_id) VALUES (?, ?, ?)'
);

const seedComments = db.transaction(() => {
    insertComment.run('写得很好，深入浅出！', 1, 2);
    insertComment.run('Node.js 入门必读，推荐！', 1, 3);
    insertComment.run('Express 的部分讲得很清楚', 2, 2);
    insertComment.run('RESTful 设计原则总结得很到位', 3, 1);
    insertComment.run('SQLite 确实好用，零配置太方便了', 4, 1);
    insertComment.run('学到了很多，感谢分享', 4, 3);
    insertComment.run('SQL 注入的例子很直观，一下子就懂了', 5, 1);
    insertComment.run('安全是每个开发者都应该重视的', 5, 2);
});

seedComments();
console.log('✅ 插入了 8 条评论');

// ========== 4. 验证：查询统计 ==========
const userCount = db.prepare('SELECT COUNT(*) AS count FROM users').get();
const articleCount = db.prepare('SELECT COUNT(*) AS count FROM articles').get();
const commentCount = db.prepare('SELECT COUNT(*) AS count FROM comments').get();

console.log(`\n📊 数据统计：`);
console.log(`  用户：${userCount.count} 人`);
console.log(`  文章：${articleCount.count} 篇`);
console.log(`  评论：${commentCount.count} 条`);
console.log(`\n🌱 测试数据插入完成！`);

db.close();
```

### `blog-backend/` 目录结构（本章最终状态）

```
blog-backend/
├── server.js
├── package.json
├── package-lock.json
├── .gitignore
├── blog.db
├── node_modules/
├── database/
│   ├── init.js            ← 第 12 章遗留
│   ├── schema.js          ← 第 13 章：建表
│   └── seed.js            ← 本章新建：测试数据
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
| 1 | 删除 `blog.db`，`npm run dev`（Ctrl+C 停止），`node database/seed.js` | 输出 "✅ 插入了 3 个用户"，"✅ 插入了 5 篇文章"，"✅ 插入了 8 条评论" |
| 2 | `node -e "const db = new (require('better-sqlite3'))('blog.db'); console.log(db.prepare('SELECT * FROM users').all())"` | 输出 3 个用户对象 |
| 3 | 同上，把 `users` 换成 `articles` | 输出 5 篇文章对象 |
| 4 | 同上，把 `users` 换成 `comments` | 输出 8 条评论对象 |
| 5 | `node -e "const db = new (require('better-sqlite3'))('blog.db'); const r = db.prepare('SELECT articles.title, users.username AS author FROM articles INNER JOIN users ON articles.author_id = users.id').all(); console.log(r)"` | 输出 5 篇文章，每篇带 `author` 字段 |

全部通过？SQL 的增删改查你已经掌握了。下一步，把这些操作集成到 Express 路由中。

---

## 六、小结表格

| 学到的东西 | 一句话解释 |
|-----------|-----------|
| INSERT | `INSERT INTO 表名 (列) VALUES (值)`——插入数据，返回 `lastInsertRowid` |
| SELECT | `SELECT 列 FROM 表 WHERE 条件`——查询数据，`.all()` 返回数组，`.get()` 返回单行 |
| UPDATE | `UPDATE 表 SET 列 = 值 WHERE 条件`——更新数据，⚠️ 不加 WHERE 更新所有行 |
| DELETE | `DELETE FROM 表 WHERE 条件`——删除数据，⚠️ 不加 WHERE 删除所有行 |
| ORDER BY / LIMIT | 排序和限制数量：`ORDER BY created_at DESC LIMIT 10` |
| JOIN | 关联查询：INNER JOIN（只返回匹配的），LEFT JOIN（左表全返回） |
| 参数化查询 | 用 `?` 占位符代替字符串拼接，天然防 SQL 注入 |
| 事务（Transaction） | 批量操作打包——要么全成功，要么全失败 |
| `.get()` vs `.all()` | `.get()` 返回单行或 `undefined`，`.all()` 返回数组或 `[]` |

---

## 七、术语附录

| 术语 | 英文 | 通俗解释 | 本章出现位置 | 字面陷阱 |
|------|------|----------|-------------|----------|
| INSERT | — | SQL 中用于插入新数据的语句。 | 步骤 1 | 不是"插入"= 覆盖——INSERT 是追加新行，不会覆盖已有数据。 |
| SELECT | — | SQL 中用于查询数据的语句。 | 步骤 2 | 不是"选择"= 选一行——SELECT 可以返回多行（`.all()`）或单行（`.get()`）。 |
| UPDATE | — | SQL 中用于修改已有数据的语句。 | 步骤 3 | 不是"更新"= 总是安全的——不加 WHERE 会更新所有行。 |
| DELETE | — | SQL 中用于删除数据的语句。 | 步骤 4 | 不是"删除"= 总是安全的——不加 WHERE 会删除所有行。 |
| WHERE | — | SQL 中的条件子句，用于过滤数据。 | 步骤 2 | 不是"哪里"——是"满足这个条件的数据"。 |
| ORDER BY | — | SQL 中用于排序的子句。 | 步骤 2.3 | 不是"按顺序"——必须指定 ASC（升序）或 DESC（降序）。 |
| LIMIT | — | SQL 中用于限制返回行数的子句。 | 步骤 2.4 | 不是"限制"= 限制数据库大小——只限制查询结果的行数。 |
| JOIN | — | SQL 中用于关联查询多张表的子句。 | 步骤 5 | 不是"连接"——是"关联"，把两张表的数据按共同字段拼在一起。 |
| 参数化查询 | Parameterized Query | 用 `?` 占位符代替直接拼接用户输入到 SQL 中的方式。防止 SQL 注入。 | 步骤 6 | 不是"参数化"= 给查询加参数——是"预编译 + 参数绑定"，数据库把 SQL 结构和参数分开处理。 |
| SQL 注入 | SQL Injection | 攻击者在输入中插入恶意 SQL 代码，改变 SQL 语句的语义，从而绕过认证或窃取数据。 | 步骤 6 | 不是"注入 SQL"——是"把 SQL 代码注入到你的查询中"，利用字符串拼接的漏洞。 |
| 事务 | Transaction | 一组 SQL 操作打包成一个"原子单元"——要么全部成功，要么全部失败（回滚）。 | 步骤 1.2 | 不是"事情"——事务的 ACID 特性（原子性、一致性、隔离性、持久性）是数据库的核心概念。 |

---

## 八、已知坑点与禁止事项

1. **UPDATE 不加 WHERE 会更新所有行**：这是最常见也最危险的错误。在写 UPDATE 时，先把 `WHERE` 条件写好，再写 `SET` 部分。

2. **DELETE 不加 WHERE 会删除所有行**：同上。建议先 `SELECT` 确认要删的数据，再 `DELETE`。

3. **SQLite 的 `?` 占位符 vs PostgreSQL 的 `$1`**：不同数据库的占位符语法不同。如果你将来换数据库，要改占位符。`better-sqlite3` 也支持命名参数（`@name`），但 `?` 最通用。

4. **`db.prepare()` 是核心 API**：`db.prepare()` 预编译 SQL，比 `db.exec()` 更安全高效。`db.exec()` 每次执行都要重新解析 SQL 字符串，`db.prepare()` 只需要编译一次。

5. **`.get()` 返回 `undefined` 时不要直接访问属性**：`const user = stmt.get(id); console.log(user.username)`——如果 `user` 是 `undefined`，会报 `TypeError`。始终先判断 `if (user)`。

6. **事务的性能优势**：逐条插入 1000 条数据，每条都触发一次磁盘写入，非常慢。用事务包裹后，只在提交时写入一次磁盘，速度提升 10-100 倍。

---

## 九、下一步建议

你已经掌握了 SQL 的增删改查。但现在的操作都是在独立脚本中——接下来把这些操作集成到 Express 路由中，让 HTTP 请求触发数据库操作：

- **下一章**：[15-后端连数据库：Express+better-sqlite3](15-后端连数据库：Express+better-sqlite3.md)——创建 `database/db.js` 数据库连接模块（单例模式），在 `server.js` 中引入，在路由中使用数据库，把数组查询替换为数据库查询。
- **延伸思考**：你现在在 seed 脚本中手动写死了 `author_id`（1, 2, 3）。在真正的应用中，`author_id` 应该来自当前登录用户——这就是下一阶段（认证）要解决的问题。

---

> 📊 本教程无可视化
>
> 本教程编辑记录：2026-06-12 初始版本。