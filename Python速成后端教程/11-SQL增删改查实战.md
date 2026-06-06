# 11-SQL 增删改查实战

- 对应文档版本：首版教程
- 适用环境：Python 3.10+（内置 sqlite3）, Windows/macOS/Linux
- 读者角色：后端初学者
- 预计耗时：新手 45 分钟 / 熟手 20 分钟
- 前置教程：[09-数据库入门：SQLite 零配置上手](./09-数据库入门：SQLite零配置上手/)、[10-建表：博客系统的表结构设计](./10-建表：博客系统的表结构设计/)
- 可视化：无

---

## 一、目标与完成效果

**一句话目标**：在 SQLite 命令行里，亲手敲完 INSERT、SELECT、UPDATE、DELETE、JOIN 五类 SQL 语句，把博客系统的 `posts` 表和 `users` 表玩透。

**完成后的可观测效果**：
- 你打开 SQLite 命令行，能独立完成一篇文章的创建、查询、修改、删除。
- 你能用一条 SQL 查出"某用户发了多少篇文章"。
- 你能用一条 SQL 查出"最新 5 篇文章的标题和作者名"。
- 你看到 `WHERE` 这个词会条件反射——"不加 WHERE 等于全表遭殃"。
- 你在教程 12 中看到 SQLAlchemy 生成的 SQL 语句时，能一眼认出它在干什么。

---

## 二、前置条件

| 序号 | 条件 | 验证命令 |
|------|------|----------|
| 1 | Python 3.10+ 已安装 | `python --version` |
| 2 | 已完成教程 10，`blog.db` 数据库文件存在，`posts` 表和 `users` 表已建好 | `python -c "import sqlite3; conn = sqlite3.connect('blog.db'); print(conn.execute(\"SELECT name FROM sqlite_master WHERE type='table'\").fetchall()); conn.close()"` |
| 3 | 数据库中有至少 2 个用户和 3 篇文章的测试数据 | 见下方验证命令 |

**一条命令确认全部前置满足**：

```powershell
python -c "import sqlite3; conn = sqlite3.connect('blog.db'); tables = conn.execute(\"SELECT name FROM sqlite_master WHERE type='table'\").fetchall(); print('Tables:', tables); print('Users:', conn.execute('SELECT COUNT(*) FROM users').fetchone()[0]); print('Posts:', conn.execute('SELECT COUNT(*) FROM posts').fetchone()[0]); conn.close()"
```

如果输出显示 `Tables: [('users',), ('posts',)]`，且 Users 和 Posts 都大于 0，前置条件满足。

如果表存在但数据为空，没关系——本章第一步就会带你插入数据。如果表不存在，请回到 [10-建表：博客系统的表结构设计](./10-建表：博客系统的表结构设计/) 先建表。

---

## 三、分步操作

### 步骤 0：SQL 是什么？——"跟数据库说话的语言"

在教程 07 中，你用 Python 列表模拟了一个"数据库"——`posts_db = []`，然后遍历列表来查找文章。**那是在跟 Python 列表说话。**

现在我们要跟**真正的数据库**说话了。数据库有自己的语言——**SQL**（Structured Query Language，结构化查询语言）。

**比喻**：Python 列表是你自己写在便签纸上的笔记，你自己翻、自己找、自己改。SQL 是你跟一个图书管理员（数据库）说："帮我找一下编号为 3 的那本书"——管理员去书库里找，然后把书递给你。你不需要知道书库里书是怎么排列的，你只需要知道**怎么跟管理员说话**。

**SQL 的四大"句式"**：

| 句式 | 英文 | 对应 CRUD 中的哪个 | 餐厅比喻 |
|------|------|-------------------|----------|
| `INSERT` | 插入 | **C**reate（增） | "把这道新菜加到菜单里" |
| `SELECT` | 查询 | **R**ead（查） | "菜单上有什么菜？" |
| `UPDATE` | 更新 | **U**pdate（改） | "把宫保鸡丁改成酱爆鸡丁" |
| `DELETE` | 删除 | **D**elete（删） | "把这道菜从菜单上划掉" |

本章我们就围绕这四大句式，一条一条在 SQLite 命令行里跑，亲眼看到每条语句的效果。

---

### 步骤 1：启动 SQLite 命令行，看看现在有什么

打开终端，进入项目目录（能看到 `blog.db` 文件的那个目录），启动 SQLite：

```bash
sqlite3 blog.db
```

> **如果提示 `'sqlite3' 不是内部或外部命令`**：用 Python 内置的方式打开：
>
> ```bash
> python -c "import sqlite3; conn = sqlite3.connect('blog.db'); conn.close()"
> ```
>
> 然后使用 Python 交互模式来执行 SQL。不过更推荐的方法是用 DB Browser for SQLite 这个免费图形化工具（https://sqlitebrowser.org/），它的"执行 SQL"标签页能让你直接输入 SQL 并看到表格形式的输出。
>
> 如果 `sqlite3` 命令可用，本章后续示例均以 `sqlite3` 命令行界面为准。

进入 SQLite 后，你会看到提示符变成了：

```
sqlite>
```

先看看有哪些表：

```sql
.tables
```

**预期输出**：

```
posts   users
```

两个表都在。再看看表结构：

```sql
.schema posts
```

**预期输出**（取决于教程 10 的具体建表语句，大致类似）：

```sql
CREATE TABLE posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    author_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (author_id) REFERENCES users(id)
);
```

> **`.schema` 和 `.tables` 是什么？** 它们是 SQLite 自带的**点命令**（以 `.` 开头），不是标准 SQL。它们只在 SQLite 命令行里有效，用来查看数据库的元信息。`.tables` 列出所有表，`.schema 表名` 显示建表语句。

再看看现在有什么数据：

```sql
SELECT * FROM users;
SELECT * FROM posts;
```

如果教程 10 结束时已经插入了一些测试数据，你会看到它们。如果为空也不要紧，下一步我们就来插入。

---

### 步骤 2：INSERT —— 往表里插入数据

**我在做什么？** 往 `posts` 表里插入一篇文章。

**语法**：

```sql
INSERT INTO 表名 (列1, 列2, ...) VALUES (值1, 值2, ...);
```

现在执行第一条 INSERT：

```sql
INSERT INTO posts (title, content, author_id) VALUES ('我的第一篇 SQL 文章', '用 SQL 插入数据真简单！', 1);
```

> **⚠️ 注意**：`author_id = 1` 假设你的 `users` 表里已经有一个 ID 为 1 的用户。如果教程 10 没有插入用户数据，先插入一个用户：
>
> ```sql
> INSERT INTO users (username, email, password_hash) VALUES ('alice', 'alice@example.com', 'hashed_password_123');
> ```

**预期输出**：

```
(无报错就是成功)
```

SQLite 在执行 INSERT 后不会自动显示结果。要验证是否插入成功，用 SELECT：

```sql
SELECT * FROM posts;
```

**预期输出**：

```
1|我的第一篇 SQL 文章|用 SQL 插入数据真简单！|1|2026-06-05 10:00:00
```

注意看：虽然你只指定了 `title`、`content`、`author_id` 三列，但 `id` 和 `created_at` 也自动填上了。这是因为建表时定义了：
- `id INTEGER PRIMARY KEY AUTOINCREMENT`——ID 自动生成，每插入一条就加 1
- `created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP`——自动填入当前时间

**再插入两篇文章，方便后面练习**：

```sql
INSERT INTO posts (title, content, author_id) VALUES ('Python 装饰器入门', '装饰器其实很简单...', 1);
INSERT INTO posts (title, content, author_id) VALUES ('Docker 部署笔记', '记录一次 Docker 部署过程...', 2);
```

> **如果 `author_id = 2` 的用户不存在**：先插入第二个用户：
>
> ```sql
> INSERT INTO users (username, email, password_hash) VALUES ('bob', 'bob@example.com', 'hashed_password_456');
> ```

验证全部插入：

```sql
SELECT * FROM posts;
```

**预期输出**（3 行数据，ID 分别为 1、2、3）：

```
1|我的第一篇 SQL 文章|用 SQL 插入数据真简单！|1|2026-06-05 10:00:00
2|Python 装饰器入门|装饰器其实很简单...|1|2026-06-05 10:01:00
3|Docker 部署笔记|记录一次 Docker 部署过程...|2|2026-06-05 10:02:00
```

---

#### ❌ 常见错误 → ✅ 正确示例

> **错误 1：字符串值忘记加引号**

❌ 错误示例：

```sql
INSERT INTO posts (title, content, author_id) VALUES (我的文章, 内容, 1);
```

SQLite 会报错：

```
Parse error: no such column: 我的文章
```

SQLite 把 `我的文章` 当成**列名**了，而不是字符串值。不加引号的东西，SQLite 先去找列名，找不到就报错。

✅ 正确示例：

```sql
INSERT INTO posts (title, content, author_id) VALUES ('我的文章', '内容', 1);
```

字符串值必须用**单引号**括起来。SQL 中单引号表示字符串，双引号在某些数据库中也行，但单引号是标准写法。

---

> **错误 2：SQL 语句末尾忘记分号**

❌ 错误示例：

```sql
INSERT INTO posts (title, content, author_id) VALUES ('我的文章', '内容', 1)
```

在 SQLite 命令行中，如果不加分号就回车，提示符会变成：

```
...>
```

这表示 SQLite 认为你还没说完，在等你继续输入。因为 SQL 语句可以跨多行，分号才是"一句话结束"的标志。

✅ 正确示例：

```sql
INSERT INTO posts (title, content, author_id) VALUES ('我的文章', '内容', 1);
```

**如果在 `...>` 提示符下卡住了怎么办？** 输入一个分号 `;` 然后回车，SQLite 会尝试执行你之前输入的内容（大概率报错），然后回到 `sqlite>` 提示符。

---

### 步骤 3：SELECT 基础 —— 查看表中的数据

**我在做什么？** 用 SELECT 查询 `posts` 表中的数据。

#### 3.1 查全部列：`SELECT *`

```sql
SELECT * FROM posts;
```

**预期输出**：3 行数据，每行包含所有列（id, title, content, author_id, created_at）。

**`*` 是什么？** 星号 = "所有列"（读作 star）。`SELECT * FROM posts` = "从 posts 表里，把每一行的所有列都拿出来"。

**比喻**：`*` 就像你去图书馆，跟管理员说"把书架上所有的书都拿来"——不挑，全要。

#### 3.2 只查特定列：`SELECT 列名, 列名`

```sql
SELECT title, author_id FROM posts;
```

**预期输出**：

```
我的第一篇 SQL 文章|1
Python 装饰器入门|1
Docker 部署笔记|2
```

只有两列——`title` 和 `author_id`。`content`、`id`、`created_at` 都没有出现。

**为什么只查特定列？** 想象你的 `posts` 表里有一万篇文章，每篇的 `content` 字段有几千字。如果你只想要标题列表，`SELECT *` 会把一万篇文章的正文也全拉出来——浪费网络带宽、浪费内存、浪费时间。**只拿你需要的列，是 SQL 性能优化的第一条原则。**

---

### 🤔 想多一点：`SELECT *` 是坏习惯吗？

你在网上搜索"SQL 最佳实践"时，会看到很多人说"**永远不要用 `SELECT *`**"。这个说法有道理，但需要理解背后的原因，而不是死记硬背。

**`SELECT *` 的问题**：
1. **性能**：拿了你不需要的数据，浪费传输和内存。
2. **脆弱性**：如果以后有人给表加了新列，`SELECT *` 的结果变了，你的代码可能因此崩溃（比如你按列索引取值，新列插入中间导致索引错位）。
3. **可读性**：别人读你的代码，看到 `SELECT *` 不知道你到底要哪些列。

**但在什么情况下 `SELECT *` 没问题？**
- 在命令行里**临时查看数据**（就像你现在做的）——因为你确实想看所有列。
- 表只有 3-5 列，且你确实需要全部。
- 写的是管理脚本，不是核心业务代码。

**结论**：在练习和临时探索时用 `SELECT *` 完全没问题。但在代码里写 SQL 时（比如教程 12 的 SQLAlchemy 部分），明确列出需要的列名。**这就像平时穿拖鞋出门没问题，但正式场合得穿鞋——知道什么时候该穿什么就行。**

---

### 步骤 4：SELECT + WHERE —— 按条件过滤

**我在做什么？** 只查 `author_id = 1` 的文章（即 alice 写的文章）。

```sql
SELECT * FROM posts WHERE author_id = 1;
```

**预期输出**：

```
1|我的第一篇 SQL 文章|用 SQL 插入数据真简单！|1|2026-06-05 10:00:00
2|Python 装饰器入门|装饰器其实很简单...|1|2026-06-05 10:01:00
```

只有两行——`author_id = 1` 的文章。`author_id = 2` 的那篇（Docker 部署笔记）被过滤掉了。

**WHERE 就是"筛选器"**。你可以把它想象成图书馆管理员问你："你要找什么书？"然后你回答："作者是 alice 的。"管理员就只给你 alice 写的书，其他人的不拿。

**常见的 WHERE 比较运算符**：

| 运算符 | 含义 | 示例 |
|--------|------|------|
| `=` | 等于 | `WHERE author_id = 1` |
| `!=` 或 `<>` | 不等于 | `WHERE author_id != 1` |
| `>` | 大于 | `WHERE id > 2` |
| `<` | 小于 | `WHERE id < 3` |
| `>=` | 大于等于 | `WHERE id >= 2` |
| `<=` | 小于等于 | `WHERE id <= 2` |

> **⚠️ 注意**：SQL 里的等号是 `=`，不是 `==`。Python 里用 `==` 判断相等，SQL 里用 `=`。这是初学者最容易串的地方。

试试其他条件：

```sql
-- 查询 id 大于 1 的文章
SELECT * FROM posts WHERE id > 1;

-- 查询 author_id 不等于 1 的文章
SELECT * FROM posts WHERE author_id != 1;
```

---

### 步骤 5：SELECT + ORDER BY —— 按某列排序

**我在做什么？** 按创建时间倒序排列文章（最新的在前）。

```sql
SELECT * FROM posts ORDER BY created_at DESC;
```

**预期输出**：

```
3|Docker 部署笔记|记录一次 Docker 部署过程...|2|2026-06-05 10:02:00
2|Python 装饰器入门|装饰器其实很简单...|1|2026-06-05 10:01:00
1|我的第一篇 SQL 文章|用 SQL 插入数据真简单！|1|2026-06-05 10:00:00
```

最新创建的文章（ID 3）排在了最前面。

**ORDER BY 的语法**：

```sql
SELECT 列名 FROM 表名 ORDER BY 列名 ASC|DESC;
```

- `ASC`（ascending，升序）：从小到大，默认值，可以省略不写
- `DESC`（descending，降序）：从大到小

试试升序排列：

```sql
SELECT * FROM posts ORDER BY created_at ASC;
```

再试试按标题的字母顺序排列：

```sql
SELECT * FROM posts ORDER BY title ASC;
```

**预期输出**：

```
3|Docker 部署笔记|...           （D 开头，排第一）
2|Python 装饰器入门|...         （P 开头，排第二）
1|我的第一篇 SQL 文章|...       （中文排最后）
```

---

### 🤔 想多一点：排序到底发生在哪里？

你可能会想："数据库里数据本来就是按插入顺序存的，为什么要排序？"

**因为数据库不保证数据的物理存储顺序。** 你今天插入的数据，明天可能被数据库引擎内部重组了（比如为了优化查询速度）。你永远不能假设 `SELECT * FROM posts` 返回的顺序就是"插入顺序"。

**排序是数据库引擎在"查询时"临时做的，不改变数据的物理存储。** 这就像图书馆管理员帮你把书按出版日期排好递给你，但书架上书的位置没变——下次你不说排序，他还是一本一本按原位置给你拿。

> **ORDER BY 可以配合 WHERE 一起用**：
>
> ```sql
> SELECT * FROM posts WHERE author_id = 1 ORDER BY created_at DESC;
> ```
>
> 先按 `author_id = 1` 过滤，再按 `created_at DESC` 排序。两条子句的执行顺序是：WHERE 先筛 → ORDER BY 后排。

---

### 步骤 6：UPDATE —— 修改已有数据

**我在做什么？** 把 ID 为 1 的文章标题改成 `'新标题：SQL 真好玩'`。

```sql
UPDATE posts SET title = '新标题：SQL 真好玩' WHERE id = 1;
```

验证：

```sql
SELECT * FROM posts WHERE id = 1;
```

**预期输出**：

```
1|新标题：SQL 真好玩|用 SQL 插入数据真简单！|1|2026-06-05 10:00:00
```

标题变了，但 `content`、`author_id` 等列不变。

**UPDATE 的语法**：

```sql
UPDATE 表名 SET 列名1 = 新值1, 列名2 = 新值2, ... WHERE 条件;
```

**可以一次更新多列**：

```sql
UPDATE posts SET title = '新标题', content = '新正文' WHERE id = 1;
```

**比喻**：UPDATE 就像你拿出一张便签纸，在原来的内容上划掉旧的字，写上新的。`SET` 是"改成什么"，`WHERE` 是"改哪张便签纸"。

---

### 步骤 7：DELETE —— 删除数据

**我在做什么？** 删除 ID 为 3 的文章。

```sql
DELETE FROM posts WHERE id = 3;
```

验证：

```sql
SELECT * FROM posts;
```

**预期输出**：只有 ID 1 和 ID 2 两篇文章了。ID 3 的那篇（Docker 部署笔记）被删掉了。

**DELETE 的语法**：

```sql
DELETE FROM 表名 WHERE 条件;
```

**比喻**：DELETE 就像你把一张便签纸揉成团扔进垃圾桶。`WHERE` 是"扔哪张"。

---

### ⚠️ 步骤 8：WHERE 忘记写的灾难 —— 这是本章最重要的一节

现在，请你**想象**下面这条命令的效果：

```sql
DELETE FROM posts;
```

**没错——没有 WHERE。** 这意味着什么？

**"DELETE FROM posts" = "把 posts 表里所有行都删掉"**。

如果你是博客系统的管理员，这个系统已经运行了三年，积累了 5000 篇文章。某个周一的早上，你迷迷糊糊地敲了 `DELETE FROM posts;` 然后回车——

**0.1 秒后，5000 篇文章全部消失。没有确认弹窗，没有"你确定吗？"，没有回收站。就像你对着一个装满文件的文件夹按了 Shift+Delete。**

同样的灾难也适用于 UPDATE：

```sql
UPDATE posts SET title = '被覆盖了';
```

**没有 WHERE 的 UPDATE = 把全表所有行的 title 都改成 `'被覆盖了'`**。5000 篇文章的标题一瞬间全部变成了同一个字符串。

---

#### ❌ UPDATE 忘记 WHERE → 全表遭殃

❌ 错误示例：

```sql
-- 你本来想改第 1 篇文章
UPDATE posts SET title = '新标题';
-- 结果：所有文章的标题都变成了 '新标题'
```

✅ 正确示例：

```sql
-- 必须加 WHERE 来限定范围
UPDATE posts SET title = '新标题' WHERE id = 1;
```

---

#### ❌ DELETE 忘记 WHERE → 全表清空

❌ 错误示例：

```sql
-- 你本来想删第 3 篇文章
DELETE FROM posts;
-- 结果：整张表被清空
```

✅ 正确示例：

```sql
DELETE FROM posts WHERE id = 3;
```

---

> **🤔 想多一点：为什么数据库不设计成"默认安全"？**

你可能会问："为什么数据库不强制要求 UPDATE 和 DELETE 必须带 WHERE？不带就报错？"

**因为有些场景下，你确实需要更新或删除全表。** 比如：
- 把所有文章的 `published` 状态从 `false` 改成 `true`（批量发布）
- 清空一张临时表（`DELETE FROM temp_logs`）
- 把所有用户的某个字段重置

**数据库设计的原则是"给你最大的灵活性，但你自己负责安全"。** 这就像菜刀——切菜很方便，切手指也很方便。你不能怪菜刀没设计成"切到手指自动变钝"，你只能自己小心。

**防御措施**：
1. **写 UPDATE 和 DELETE 时，先写 WHERE 再写前面的部分**。养成肌肉记忆：手指先敲 `WHERE id = ?`，再回头补 `DELETE FROM` 和 `SET`。
2. **生产环境用事务（TRANSACTION）**。先 `BEGIN TRANSACTION`，执行完检查结果，确认无误再 `COMMIT`。如果手滑了，`ROLLBACK` 就能撤销。教程 12 会讲事务。
3. **在 SQLite 命令行中，开启安全模式**：执行 `.echo on` 会让 SQLite 回显每一条 SQL，这样你至少能看到自己执行了什么。更好的习惯是**先用 SELECT 确认你要操作的数据范围**，再换成 UPDATE/DELETE。

---

### 步骤 9：JOIN 联表查询 —— 把两张表的数据拼在一起看

**我在做什么？** 查出每篇文章的标题 + 作者的用户名，但作者名在 `users` 表里，文章标题在 `posts` 表里。我需要把两张表"拼"在一起。

```sql
SELECT posts.title, users.username
FROM posts
JOIN users ON posts.author_id = users.id;
```

**预期输出**：

```
新标题：SQL 真好玩|alice
Python 装饰器入门|alice
```

每行：左边是文章标题（来自 `posts` 表），右边是作者用户名（来自 `users` 表）。

**JOIN 的语法拆解**：

```sql
SELECT 表1.列, 表2.列
FROM 表1
JOIN 表2 ON 表1.外键 = 表2.主键;
```

逐部分解释：

| 部分 | 含义 | 本例 |
|------|------|------|
| `SELECT posts.title, users.username` | 我要看文章的标题和用户的用户名 | `posts.title` 和 `users.username` |
| `FROM posts` | 主表是 posts | 从文章表出发 |
| `JOIN users` | 把 users 表也拉进来 | 联表查询：两张表一起查 |
| `ON posts.author_id = users.id` | 拼接条件：文章的 `author_id` 等于用户的 `id` | 文章的作者 ID 对应用户的 ID |

**比喻**：JOIN 就像你手里有两张表格——一张是"文章表"（每篇文章有个作者编号），一张是"用户表"（每个用户有名有姓）。你现在想把两张表拼成一张大表，拼接的规则是：文章表的 `author_id` 这一列 = 用户表的 `id` 这一列。拼接完后，你就能在同一行里看到"文章标题"和"作者名"。

**用图来理解 JOIN 的过程**：

```
posts 表                          users 表
┌────┬──────────┬───────────┐    ┌────┬──────────┐
│ id │ title    │ author_id │    │ id │ username │
├────┼──────────┼───────────┤    ├────┼──────────┤
│ 1  │ 新标题   │ 1         │    │ 1  │ alice    │
│ 2  │ Python.. │ 1         │    │ 2  │ bob      │
└────┴──────────┴───────────┘    └────┴──────────┘

        JOIN ON posts.author_id = users.id
                    ↓
┌────────────────────────┬──────────┐
│ posts.title            │ username │
├────────────────────────┼──────────┤
│ 新标题：SQL 真好玩     │ alice    │
│ Python 装饰器入门      │ alice    │
└────────────────────────┴──────────┘
```

> **为什么 `posts.title` 要写表名前缀？** 因为两张表可能都有同名的列。比如 `posts` 有 `id`，`users` 也有 `id`——如果你只写 `SELECT id FROM posts JOIN users ...`，数据库不知道你要的是 `posts.id` 还是 `users.id`。加上表名前缀 `posts.id` 就清楚了。

---

#### ❌ 常见错误 → ✅ 正确示例

> **错误：JOIN 的 ON 条件写错了**

❌ 错误示例：

```sql
SELECT posts.title, users.username
FROM posts
JOIN users ON posts.id = users.id;
```

这样 JOIN 的意思是："文章的 ID 等于用户的 ID 才拼接"。但文章 ID 1 和用户 ID 1 之间没有逻辑关系——文章 ID 1 可能属于用户 ID 2。**ON 条件应该用外键列（`posts.author_id`）对应主表的主键列（`users.id`）。**

✅ 正确示例：

```sql
SELECT posts.title, users.username
FROM posts
JOIN users ON posts.author_id = users.id;
```

**记住**：`ON` 后面跟的是"两表之间的关联条件"，通常就是"外键 = 主键"。

---

### 步骤 10：练习 —— 巩固你今天学到的所有 SQL

现在关掉教程，自己动手完成以下练习。**遇到不会的，先自己想 30 秒，再看答案。**

---

#### 基础档（必做）

**练习 1：插入一篇文章**

自己写一条 INSERT，插入一篇标题为 `'SQL 练习文章'`、内容为 `'熟能生巧'`、作者 ID 为 1 的文章。

<details>
<summary>点击查看答案</summary>

```sql
INSERT INTO posts (title, content, author_id) VALUES ('SQL 练习文章', '熟能生巧', 1);
```

验证：

```sql
SELECT * FROM posts WHERE title = 'SQL 练习文章';
```

</details>

---

**练习 2：查询所有作者 ID 为 1 的文章**

<details>
<summary>点击查看答案</summary>

```sql
SELECT * FROM posts WHERE author_id = 1;
```

</details>

---

**练习 3：把刚才插入的那篇文章的标题改成 `'SQL 练习完成'`**

<details>
<summary>点击查看答案</summary>

```sql
-- 先查出你的文章 ID
SELECT id FROM posts WHERE title = 'SQL 练习文章';

-- 假设 ID 是 4，执行更新
UPDATE posts SET title = 'SQL 练习完成' WHERE id = 4;
```

</details>

---

**练习 4：删除刚才那篇文章**

<details>
<summary>点击查看答案</summary>

```sql
DELETE FROM posts WHERE title = 'SQL 练习完成';
```

</details>

---

#### 进阶档（挑战题，可选）

**练习 5：统计某用户发了多少篇文章**

提示：`COUNT(*)` 统计行数。

```sql
-- 查询 author_id = 1 的用户发了多少篇文章
SELECT COUNT(*) FROM posts WHERE author_id = 1;
```

<details>
<summary>点击查看答案</summary>

```sql
SELECT COUNT(*) FROM posts WHERE author_id = 1;
```

**预期输出**：

```
2
```

`COUNT(*)` 是一个**聚合函数**——它把多行数据"聚合"成一个数字。`COUNT(*)` 统计行数，`COUNT(列名)` 统计该列非 NULL 的行数。

**让输出更友好**：

```sql
SELECT author_id, COUNT(*) AS 文章数量 FROM posts WHERE author_id = 1;
```

`AS` 是**别名**（alias）——给计算结果起一个名字，方便阅读。

</details>

---

**练习 6：查询最新 5 篇文章**

提示：`LIMIT` 限制返回行数。

```sql
SELECT * FROM posts ORDER BY created_at DESC LIMIT 5;
```

<details>
<summary>点击查看答案</summary>

```sql
SELECT * FROM posts ORDER BY created_at DESC LIMIT 5;
```

**`LIMIT` 的语法**：`LIMIT N` 表示"只返回前 N 行"。通常配合 `ORDER BY` 一起使用：
- `ORDER BY created_at DESC LIMIT 5` = 按时间倒序，取前 5 条 = 最新 5 篇文章
- `ORDER BY created_at ASC LIMIT 5` = 按时间正序，取前 5 条 = 最早 5 篇文章

</details>

---

**练习 7：查出每篇文章的标题和作者邮箱**

提示：`posts` 表有 `author_id`，`users` 表有 `email`。需要 JOIN。

<details>
<summary>点击查看答案</summary>

```sql
SELECT posts.title, users.email
FROM posts
JOIN users ON posts.author_id = users.id;
```

</details>

---

## 四、完整 SQL 语句清单

以下是本章涉及的所有 SQL 语句（按类别整理）：

### 插入

```sql
INSERT INTO posts (title, content, author_id) VALUES ('我的第一篇 SQL 文章', '用 SQL 插入数据真简单！', 1);
INSERT INTO users (username, email, password_hash) VALUES ('alice', 'alice@example.com', 'hashed_password_123');
```

### 查询

```sql
-- 查全部
SELECT * FROM posts;

-- 查特定列
SELECT title, author_id FROM posts;

-- 条件过滤
SELECT * FROM posts WHERE author_id = 1;
SELECT * FROM posts WHERE id > 1;

-- 排序
SELECT * FROM posts ORDER BY created_at DESC;
SELECT * FROM posts ORDER BY created_at ASC;

-- 组合使用
SELECT * FROM posts WHERE author_id = 1 ORDER BY created_at DESC;

-- 限制行数
SELECT * FROM posts ORDER BY created_at DESC LIMIT 5;

-- 聚合统计
SELECT COUNT(*) FROM posts WHERE author_id = 1;
```

### 更新

```sql
UPDATE posts SET title = '新标题：SQL 真好玩' WHERE id = 1;
UPDATE posts SET title = '新标题', content = '新正文' WHERE id = 1;
```

### 删除

```sql
DELETE FROM posts WHERE id = 3;
```

### 联表查询

```sql
SELECT posts.title, users.username
FROM posts
JOIN users ON posts.author_id = users.id;
```

---

## 五、验证方法

在 SQLite 命令行中，依次执行以下验证，全部通过则本章完成：

```sql
-- 1. 确认有三篇文章（如果之前删过，重新插入）
SELECT COUNT(*) FROM posts;
-- 预期：≥ 2

-- 2. INSERT 测试
INSERT INTO posts (title, content, author_id) VALUES ('验证文章', '验证内容', 1);
-- 预期：无报错

-- 3. SELECT + WHERE 测试
SELECT * FROM posts WHERE title = '验证文章';
-- 预期：能看到刚才插入的文章，id 是新生成的

-- 4. UPDATE 测试
UPDATE posts SET title = '验证文章-已更新' WHERE title = '验证文章';
SELECT * FROM posts WHERE title = '验证文章-已更新';
-- 预期：标题已变

-- 5. DELETE 测试
DELETE FROM posts WHERE title = '验证文章-已更新';
SELECT * FROM posts WHERE title = '验证文章-已更新';
-- 预期：返回空

-- 6. JOIN 测试
SELECT posts.title, users.username FROM posts JOIN users ON posts.author_id = users.id;
-- 预期：每篇文章后面跟着作者的用户名
```

---

## 六、小结

| 你学到了什么 | 一句话总结 |
|--------------|-----------|
| SQL 是什么 | 跟数据库"说话"的语言，四大句式：INSERT、SELECT、UPDATE、DELETE |
| `INSERT INTO 表名 (列) VALUES (值)` | 往表里插入一行新数据 |
| `SELECT 列 FROM 表名` | 从表里查询数据，`*` 查全部列，指定列名只查那些列 |
| `WHERE` | 筛选条件，只返回满足条件的行。`=` 是等号，不是 `==` |
| `ORDER BY 列名 DESC` | 按某列排序，`DESC` 降序（大到小），`ASC` 升序（默认） |
| `LIMIT N` | 只返回前 N 行，常配合 `ORDER BY` 做"最新 N 条" |
| `UPDATE 表名 SET 列=值 WHERE 条件` | 修改满足条件的行，**不加 WHERE 等于全表修改** |
| `DELETE FROM 表名 WHERE 条件` | 删除满足条件的行，**不加 WHERE 等于全表清空** |
| `JOIN 表 ON 条件` | 把两张表按关联条件"拼"在一起，一次查出跨表的数据 |
| `COUNT(*)` | 聚合函数，统计行数 |
| `AS` | 给列或计算结果起别名 |

---

## 七、术语附录

| 术语 | 英文 | 通俗解释 | 本章出现位置 |
|------|------|----------|-------------|
| INSERT | — | SQL 中用来"插入新数据"的语句。对应 CRUD 中的 C（Create）。 | 步骤 2 |
| SELECT | — | SQL 中用来"查询数据"的语句。对应 CRUD 中的 R（Read）。**字面陷阱**：SELECT 在英文里是"选择"，但 SQL 里它不"选择"行（那是 WHERE 的事），只是"列出"列。 | 步骤 3 |
| UPDATE | — | SQL 中用来"修改已有数据"的语句。对应 CRUD 中的 U（Update）。**最大危险**：不加 WHERE 会修改全表。 | 步骤 6 |
| DELETE | — | SQL 中用来"删除数据"的语句。对应 CRUD 中的 D（Delete）。**最大危险**：不加 WHERE 会清空整张表，且无法撤销（除非用了事务）。 | 步骤 7 |
| WHERE | — | SQL 中的条件过滤子句。跟在 SELECT/UPDATE/DELETE 后面，用来指定"哪些行"。**生命线**：UDPATE 和 DELETE 中不加 WHERE 等于全表操作。 | 步骤 4 |
| ORDER BY | — | SQL 中的排序子句。`ASC` 升序，`DESC` 降序。排序是查询时临时进行的，不改变数据物理存储。 | 步骤 5 |
| JOIN | — | SQL 中的联表查询。把两张表按某种关联条件（ON）拼接在一起，让你能在一行里看到来自不同表的数据。 | 步骤 9 |
| 联表查询 | JOIN | JOIN 的中文翻译。把多张表的数据按关联条件合并成一张大的结果集来查询。 | 步骤 9 |
| 聚合函数 | Aggregate Function | 把多行数据"压缩"成一个值的函数。`COUNT(*)` 统计行数，`SUM()` 求和，`AVG()` 求平均，`MAX()`/`MIN()` 取最大/最小。 | 步骤 10 |
| LIMIT | — | SQL 中限制返回行数的子句。`LIMIT 5` 表示只返回前 5 行。通常配合 `ORDER BY` 做"Top N"查询。 | 步骤 10 |
| 外键 | Foreign Key | 一张表中的列，指向另一张表的主键。如 `posts.author_id` 指向 `users.id`。用来建立表与表之间的关联。 | 步骤 9 |
| 主键 | Primary Key | 表中唯一标识每一行的列。如 `posts.id`、`users.id`。值不能重复，不能为空。 | 步骤 2 |

---

## 八、已知坑点与禁止事项

| 坑点 | 现象 | 原因 | 解决 |
|------|------|------|------|
| UPDATE/DELETE 忘记 WHERE | 全表数据被修改或清空 | 没有 WHERE 时，数据库认为你要操作所有行 | 养成先写 WHERE 再写前面的习惯；生产环境用事务 |
| SQL 等号是 `=` 不是 `==` | `WHERE id == 1` 报语法错误 | SQL 和 Python 的语法不同，等号只有一个 `=` | 记住：SQL 用 `=`，Python 用 `==` |
| 字符串值忘记加引号 | `WHERE title = 我的文章` 报 "no such column" | 不加引号的值被当成列名 | 字符串必须用单引号 `'...'` 括起来 |
| SQL 语句末尾忘记分号 | 命令行卡在 `...>` 提示符 | SQLite 认为你还没说完 | 输入 `;` 回车，然后重新输入正确的语句 |
| JOIN 的 ON 条件写错 | 联表结果不对或为空 | 用错了关联列（比如用了 `posts.id = users.id` 而不是 `posts.author_id = users.id`） | 检查：ON 后面应该是"外键列 = 主键列" |
| 在 `...>` 提示符下不知道怎么办 | 无法回到正常提示符 | 忘记加分号，SQLite 在等你继续输入 | 输入 `;` 回车，SQLite 会尝试执行（大概率报错），然后回到 `sqlite>` |

---

## 九、下一步建议

你已经掌握了 SQL 的四大基本句式。现在你可以在命令行里独立操作数据库了。但真正的后端开发中，你不会在命令行里手动敲 SQL——你会用 Python 代码来操作数据库。

- **下一章**：[12-后端连数据库：FastAPI + SQLAlchemy](./12-后端连数据库：FastAPI+SQLAlchemy/)——学习如何用 Python 代码执行 SQL，以及 ORM（对象关系映射）是什么。
- **延伸练习**：回到 [10-建表](./10-建表：博客系统的表结构设计/)，看看你建的 `comments` 表（如果有的话），试着对它做 INSERT、SELECT、JOIN 操作。
- **阶段三终点预告**：完成教程 13 后，你教程 07 写的"内存版 CRUD"将升级为"数据库版"——数据再也不会因为重启服务器而丢失了。

---

> [可暂停点 5/9]：你已经会写 SQL 了。下次从 [12-后端连数据库：FastAPI + SQLAlchemy](./12-后端连数据库：FastAPI+SQLAlchemy/) 继续。
>
> 本章新增术语：INSERT、SELECT、UPDATE、DELETE、WHERE、ORDER BY、JOIN、联表查询、聚合函数、LIMIT、外键、主键。已同步至全局术语索引。