# 附录D：SQL 命令速查

> 本附录收录教程中使用的所有 SQL 命令，基于 SQLite 语法（通过 better-sqlite3 执行）。每个命令给出语法、本教程实际使用的示例、以及对应章节。

---

## 1. CREATE TABLE — 建表

### 语法

```sql
CREATE TABLE IF NOT EXISTS 表名 (
    列名 数据类型 约束,
    ...
    FOREIGN KEY (外键列) REFERENCES 父表(主键)
);
```

### 示例（本教程 users 表）

```sql
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    created_at TEXT DEFAULT (datetime('now'))
);
```

### 示例（本教程 articles 表）

```sql
CREATE TABLE IF NOT EXISTS articles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    author_id INTEGER NOT NULL,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (author_id) REFERENCES users(id)
);
```

### 示例（本教程 comments 表）

```sql
CREATE TABLE IF NOT EXISTS comments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content TEXT NOT NULL,
    article_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (article_id) REFERENCES articles(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

> 对应章节：13

---

## 2. INSERT — 插入数据

### 语法

```sql
INSERT INTO 表名 (列1, 列2, ...) VALUES (值1, 值2, ...);
```

### 单条插入

```sql
INSERT INTO users (username, email, password_hash, created_at)
VALUES ('alice', 'alice@example.com', '$2b$10$...', '2026-06-12T08:00:00.000Z');
```

### 多条插入

```sql
INSERT INTO articles (title, content, author_id) VALUES
    ('第一篇文章', '内容...', 1),
    ('第二篇文章', '内容...', 1),
    ('第三篇文章', '内容...', 2);
```

### 事务中的多条插入（better-sqlite3）

```javascript
const insertMany = db.transaction((items) => {
    const stmt = db.prepare('INSERT INTO articles (title, content, author_id) VALUES (?, ?, ?)');
    for (const item of items) {
        stmt.run(item.title, item.content, item.author_id);
    }
});

insertMany([
    { title: 'A', content: '...', author_id: 1 },
    { title: 'B', content: '...', author_id: 2 }
]);
```

> 对应章节：14

---

## 3. SELECT — 查询数据

### 全表查询

```sql
SELECT * FROM articles;
```

```sql
SELECT id, title, created_at FROM articles;
```

### 条件查询（WHERE）

```sql
SELECT * FROM articles WHERE id = 5;
```

```sql
SELECT * FROM articles WHERE author_id = 1 AND title LIKE '%Node%';
```

### 排序（ORDER BY）

```sql
-- 按创建时间降序（最新的在前）
SELECT * FROM articles ORDER BY created_at DESC;

-- 按创建时间升序（最旧的在前）
SELECT * FROM articles ORDER BY created_at ASC;
```

### 限制数量（LIMIT）

```sql
-- 只取前 10 条
SELECT * FROM articles LIMIT 10;
```

### 分页（LIMIT + OFFSET）

```sql
-- 第 3 页，每页 10 条 — 跳过前 20 条，取 10 条
SELECT * FROM articles ORDER BY created_at DESC LIMIT 10 OFFSET 20;
```

```javascript
// 在代码中计算 OFFSET
const page = 3;
const limit = 10;
const offset = (page - 1) * limit;  // 20
```

### 去重（DISTINCT）

```sql
-- 查询所有不重复的作者 ID
SELECT DISTINCT author_id FROM articles;
```

### 模糊搜索（LIKE）

```sql
-- 标题包含 "Node" 的文章
SELECT * FROM articles WHERE title LIKE '%Node%';

-- 标题或内容包含 "Node"
SELECT * FROM articles WHERE title LIKE '%Node%' OR content LIKE '%Node%';
```

> 对应章节：14, 22, 23

---

## 4. UPDATE — 更新数据

### 语法

```sql
UPDATE 表名 SET 列1 = 值1, 列2 = 值2 WHERE 条件;
```

### 示例

```sql
UPDATE articles
SET title = '新标题', content = '新内容', updated_at = datetime('now')
WHERE id = 5;
```

> ⚠️ **关键警告**：**永远不要忘记 `WHERE` 子句！** 没有 `WHERE` 的 `UPDATE` 会更新**所有行**！

```sql
-- ❌ 危险！会把所有文章标题都改成 "新标题"
UPDATE articles SET title = '新标题';

-- ✅ 正确：只更新指定文章
UPDATE articles SET title = '新标题' WHERE id = 5;
```

> 对应章节：14

---

## 5. DELETE — 删除数据

### 语法

```sql
DELETE FROM 表名 WHERE 条件;
```

### 示例

```sql
DELETE FROM articles WHERE id = 5;
```

```sql
-- 删除某用户的所有文章
DELETE FROM articles WHERE author_id = 3;
```

> ⚠️ **关键警告**：**永远不要忘记 `WHERE` 子句！** 没有 `WHERE` 的 `DELETE` 会删除**所有行**！

```sql
-- ❌ 危险！会删除所有文章
DELETE FROM articles;

-- ✅ 正确：只删除指定文章
DELETE FROM articles WHERE id = 5;
```

> 对应章节：14

---

## 6. JOIN — 关联查询

### INNER JOIN（取交集）

```sql
-- 查询文章 + 作者名
SELECT
    articles.id,
    articles.title,
    articles.content,
    articles.created_at,
    users.username AS author
FROM articles
INNER JOIN users ON articles.author_id = users.id
ORDER BY articles.created_at DESC;
```

**行为**：只返回 `articles` 和 `users` 都有匹配的行。如果某篇文章的 `author_id` 在 `users` 表中不存在，该文章不会出现在结果中。

### LEFT JOIN（以左表为准）

```sql
-- 查询文章 + 评论数（含没有评论的文章）
SELECT
    articles.id,
    articles.title,
    COUNT(comments.id) AS comment_count
FROM articles
LEFT JOIN comments ON articles.id = comments.article_id
GROUP BY articles.id;
```

**行为**：返回左表（`articles`）的所有行。如果某篇文章没有评论，`comment_count` 为 0。

### 多表 JOIN

```sql
-- 查询评论 + 评论者用户名 + 文章标题
SELECT
    comments.id,
    comments.content,
    comments.created_at,
    users.username AS commenter,
    articles.title AS article_title
FROM comments
INNER JOIN users ON comments.user_id = users.id
INNER JOIN articles ON comments.article_id = articles.id
WHERE comments.article_id = 5
ORDER BY comments.created_at DESC;
```

> 对应章节：15, 21

---

## 7. 聚合函数

| 函数 | 作用 | 示例 |
|------|------|------|
| `COUNT` | 统计行数 | `SELECT COUNT(*) AS total FROM articles` |
| `SUM` | 求和 | `SELECT SUM(views) FROM articles` |
| `AVG` | 平均值 | `SELECT AVG(rating) FROM comments` |
| `MAX` | 最大值 | `SELECT MAX(created_at) FROM articles` |
| `MIN` | 最小值 | `SELECT MIN(created_at) FROM articles` |

### 本教程示例

```sql
-- 统计文章总数
SELECT COUNT(*) AS total FROM articles;

-- 统计搜索结果总数
SELECT COUNT(*) AS total FROM articles WHERE title LIKE '%Node%' OR content LIKE '%Node%';

-- 统计每篇文章的评论数
SELECT article_id, COUNT(*) AS comment_count
FROM comments
GROUP BY article_id;
```

> 对应章节：22

---

## 8. 子查询

```sql
-- 查询评论数最多的文章
SELECT * FROM articles
WHERE id = (SELECT article_id FROM comments GROUP BY article_id ORDER BY COUNT(*) DESC LIMIT 1);
```

```sql
-- 查询有评论的文章
SELECT * FROM articles
WHERE id IN (SELECT DISTINCT article_id FROM comments);
```

> 对应章节：21

---

## 9. ALTER TABLE — 修改表结构

```sql
-- 添加新列
ALTER TABLE articles ADD COLUMN cover_image TEXT;

-- SQLite 不支持删除列和修改列（需要重建表）
-- 如需删除列，需要：
-- 1. 创建新表（不含要删除的列）
-- 2. 从旧表复制数据到新表
-- 3. 删除旧表
-- 4. 重命名新表
```

> 对应章节：24

---

## 10. DROP TABLE — 删除表

```sql
-- 删除表（危险！）
DROP TABLE IF EXISTS articles;
```

> ⚠️ **危险操作**：删除表会同时删除表中的所有数据，不可恢复。

---

## 11. 外键约束（PRAGMA foreign_keys）

```sql
-- SQLite 默认不开启外键约束！必须手动开启
PRAGMA foreign_keys = ON;
```

在 better-sqlite3 中：

```javascript
const db = new Database('blog.db');
db.pragma('foreign_keys = ON');  // 每次连接都要开启
```

**外键约束的作用**：
- 插入评论时，`article_id` 必须是 `articles` 表中存在的 ID。
- 删除用户时，如果该用户有文章，删除会失败（保护数据完整性）。
- 删除文章时，该文章的评论也会被自动删除（级联删除）。

> 对应章节：13, 15

---

## 12. 参数化查询（防 SQL 注入）

### ❌ 错误做法：字符串拼接

```javascript
// 危险！用户输入 `' OR 1=1 --` 会绕过所有条件
const sql = `SELECT * FROM users WHERE username = '${username}'`;
db.prepare(sql).get();  // SQL 注入漏洞！
```

### ✅ 正确做法：参数化查询

```javascript
// 用 ? 占位符，值作为参数传入
const user = db.prepare('SELECT * FROM users WHERE username = ?').get(username);
```

```javascript
// 多个参数按顺序传入
const article = db.prepare(
    'SELECT * FROM articles WHERE id = ? AND author_id = ?'
).get(articleId, authorId);
```

```javascript
// INSERT 也使用参数化
const result = db.prepare(
    'INSERT INTO articles (title, content, author_id) VALUES (?, ?, ?)'
).run(title, content, author_id);
```

> 对应章节：14

---

## 13. better-sqlite3 常用方法

| 方法 | 用途 | 返回值 | 示例 |
|------|------|--------|------|
| `db.prepare(sql)` | 预编译 SQL 语句 | Statement 对象 | `const stmt = db.prepare('SELECT * FROM users')` |
| `stmt.get(...)` | 执行查询，取一行 | 对象 或 `undefined` | `stmt.get(id)` |
| `stmt.all(...)` | 执行查询，取所有行 | 数组 | `stmt.all()` |
| `stmt.run(...)` | 执行写操作 | `{ changes, lastInsertRowid }` | `stmt.run(title, content)` |
| `db.exec(sql)` | 执行多条 SQL 语句 | `undefined` | `db.exec('CREATE TABLE ...; CREATE TABLE ...')` |
| `db.transaction(fn)` | 创建事务 | 函数 | `const batch = db.transaction((items) => { ... })` |
| `db.pragma(key)` | 读取/设置 pragma | 值 | `db.pragma('foreign_keys = ON')` |
| `db.close()` | 关闭数据库连接 | `undefined` | `db.close()` |

> 对应章节：14, 15

---

> **更新记录**：2026-06-12 初始版本，覆盖教程第 12-24 章所有 SQL 命令。