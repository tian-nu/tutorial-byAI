# 09-数据库入门：SQLite 零配置上手

- 对应文档版本：首版教程
- 适用环境：Python 3.10+, Windows/macOS/Linux（SQLite 为 Python 内置模块，无需额外安装）
- 读者角色：后端初学者
- 预计耗时：新手 30 分钟 / 熟手 10 分钟
- 前置教程：[08-中间件：窥探每个请求](./08-中间件：窥探每个请求.md)
- 可视化：无

---

## 一、目标与完成效果

**一句话目标**：理解数据库是什么，用 SQLite 在硬盘上创建一个真实的数据库文件，亲手执行建表、插入、查询操作，为下一章"把博客文章存到数据库"打好基础。

**完成后的可观测效果**：
- 你的项目目录里多了一个 `blog.db` 文件（大小虽然只有几 KB，但它是一个货真价实的数据库）。
- 你在终端里敲 `sqlite3 blog.db`，进入一个交互式命令行，能查看表结构、插入数据、查询数据。
- 你能用"Excel 表格"这个比喻，给不懂编程的朋友解释清楚数据库、表、行、列分别是什么。
- 你打开 `blog.db` 文件，之前插入的数据不会消失——它真的写到了硬盘上，不像上一章的内存版 CRUD，服务器重启数据就没了。

---

## 二、前置条件

| 序号 | 条件 | 验证命令 |
|------|------|----------|
| 1 | Python 3.10+ 已安装 | `python --version` |
| 2 | 虚拟环境已激活（本教程只用 Python 内置模块，但保持习惯） | `venv\Scripts\activate`（Windows）或 `source venv/bin/activate`（macOS/Linux） |

**一条命令确认前置满足**：

```powershell
python --version
```

如果输出类似 `Python 3.12.x`，前置条件满足。SQLite 是 Python 3 的自带模块，**不需要 `pip install` 任何东西**。

---

## 三、分步操作

### 步骤 1：数据库是什么？——用 Excel 来理解

在之前几章，你写的博客文章 CRUD 用的是一个 Python 列表：`blogs = []`。这有一个致命问题——**服务器重启，数据全没**。就像你在纸上记了笔记，一阵风把纸吹走了。

我们需要一个能把数据**持久化**到硬盘上的东西。这个东西就是**数据库（Database）**。

#### 比喻：数据库 = 一个 Excel 文件

如果你用过 Excel，恭喜你——你已经理解了数据库 80% 的核心概念。我们来一一对应：

| 数据库概念 | Excel 类比 | 通俗解释 |
|-----------|-----------|----------|
| **数据库（Database）** | 一个 `.xlsx` 文件 | 一个独立的数据容器，所有数据都在这个文件里 |
| **表（Table）** | 一个 Sheet（工作表） | 一类数据的集合。比如一个 Sheet 叫"博客文章"，一个叫"用户" |
| **行（Row）/ 记录（Record）** | 一行数据 | 一条具体的数据。比如一行就是"第 3 号文章：标题是《Python 真好学》" |
| **列（Column）/ 字段（Field）** | 一列 | 数据的某个属性。比如 A 列是"标题"，B 列是"作者"，C 列是"发布时间" |

画成表格就是这样：

```
表名：blogs（博客文章）
┌────┬──────────────────┬──────────┬─────────────────────┐
│ id │     title        │  author  │     created_at      │
├────┼──────────────────┼──────────┼─────────────────────┤
│ 1  │ Python 真好学    │  小明    │ 2026-06-01 10:00:00 │
│ 2  │ FastAPI 入门     │  小红    │ 2026-06-02 14:30:00 │
│ 3  │ 数据库原来这么简单│  小明    │ 2026-06-03 09:15:00 │
└────┴──────────────────┴──────────┴─────────────────────┘
        ↑                    ↑              ↑
      列（字段）          行（记录）     行（记录）
```

**数据库就是 Excel 文件，表就是 Sheet，行就是一行数据，列就是一类属性。** 这个比喻贯穿全章，后面你每次看到"表"、"行"、"列"，脑子里就浮现 Excel 的画面。

> **为什么不用真正的 Excel 存数据？** 因为 Excel 不是为"程序读写"设计的——你不能在 Python 代码里写 `excel_file.get_row(5)` 然后瞬间拿到数据。数据库就是专门干这个的：它能让你用代码（而不是鼠标）精确、快速、安全地读写数据。

---

### 步骤 2：SQLite 是什么？——数据库界的"瑞士军刀"

数据库有很多种。MySQL、PostgreSQL、MongoDB……这些名字你可能听过。但它们都有一个共同点：**需要安装、配置、启动服务**。就像你要开一家大餐厅，得先租店面、装修、办执照、招员工。

SQLite 不一样。它有三个特点，每一个都很"离谱"：

#### 特点一：零配置

**不用安装任何东西。** Python 3 自带 `sqlite3` 模块，你不需要 `pip install`，不需要配置用户名密码，不需要启动一个"数据库服务"。打开就能用，就像打开记事本写字一样简单。

#### 特点二：一个文件就是整个数据库

你创建一个数据库，硬盘上就多一个文件。比如 `blog.db`。这个文件里装着你的所有表、所有数据。备份数据库 = 复制这个文件。删除数据库 = 删掉这个文件。迁移数据库 = 把这个文件复制到另一台电脑。

对比一下 MySQL：备份 MySQL 数据库你需要 `mysqldump` 导出 SQL 文件，迁移时还要在新服务器上重新导入。SQLite 直接复制粘贴就行。

#### 特点三：轻量但五脏俱全

SQLite 支持标准的 SQL 语法（`CREATE TABLE`、`INSERT`、`SELECT`、`UPDATE`、`DELETE`），支持事务（保证数据一致性），支持索引（加速查询）。别看它小，该有的功能一个不少。

**SQLite 的定位**：它不是 MySQL 的"替代品"，而是"小型应用的最佳选择"。你的个人博客、手机 App 的本地存储、浏览器的书签和历史记录——这些场景用 SQLite 绰绰有余。全球有超过一万亿（1 trillion）个 SQLite 数据库在运行——你没看错，是一万亿。你手机上的每个 App 几乎都在用 SQLite。

#### SQLite 不适合什么？

- 高并发写入（几百个人同时发文章）——MySQL / PostgreSQL 更适合
- 需要网络访问（多个服务器共享数据库）——MySQL / PostgreSQL 更适合
- 数据量巨大（几百 GB）——专业数据库更适合

**但你要做的个人博客，用户只有你自己，SQLite 完美够用。**

---

### 步骤 3：打开 SQLite 命令行——三种方式任选其一

现在我们来真正操作 SQLite。你有三种方式，选一种你方便的就行。

#### 方式一：Python 交互环境（推荐——零安装，所有系统通用）

这是最"零配置"的方式。打开终端，输入：

```bash
python
```

进入 Python 交互环境（你会看到 `>>>` 提示符），然后输入：

```python
import sqlite3
conn = sqlite3.connect("blog.db")
```

> **这一行做了什么？** `sqlite3.connect("blog.db")` 的意思是："连接（或创建）当前目录下名为 `blog.db` 的数据库文件"。如果文件不存在，SQLite 会自动创建它。如果存在，就打开它。

然后我们用 Python 执行 SQL 语句。先创建一个"游标"（cursor）——你可以把它理解成"数据库里的光标"，用来执行 SQL 命令：

```python
cursor = conn.cursor()
```

现在 `cursor` 就绪了，你可以通过它执行 SQL。不过我们先不急着写 SQL，先看看方式二——如果你更喜欢直接用 SQLite 的命令行工具。

#### 方式二：SQLite 命令行工具（`.db` 文件直接打开）

如果你安装了独立的 SQLite 命令行工具，可以直接：

```bash
sqlite3 blog.db
```

**如何检查你有没有安装？**

```bash
sqlite3 --version
```

- **macOS / Linux**：通常自带，直接能用。
- **Windows**：通常没有自带。

**Windows 用户安装 SQLite 命令行工具**：

1. 打开 https://www.sqlite.org/download.html
2. 找到 "Precompiled Binaries for Windows" 区域
3. 下载 `sqlite-tools-win-x64-XXXXXXX.zip`（选 `sqlite-tools`，不是 `sqlite-dll`）
4. 解压后，把 `sqlite3.exe` 所在的文件夹路径加入系统 PATH 环境变量
5. 重新打开终端，输入 `sqlite3 --version` 验证

> **如果不想折腾 PATH**：把解压出来的 `sqlite3.exe` 直接复制到你的项目根目录（能看到 `blog_backend/` 文件夹的那一层），然后在那个目录下打开终端，输入 `.\sqlite3.exe blog.db` 即可。

#### 方式三：VS Code 插件（图形化界面，所见即所得）

如果你更喜欢图形界面，VS Code 有一个叫 **SQLite Viewer** 的插件：

1. 打开 VS Code，点击左侧扩展图标（或按 `Ctrl+Shift+X`）
2. 搜索 `SQLite Viewer`（作者：Florian Klampfer）
3. 安装后，直接在 VS Code 里右键 `blog.db` 文件 → "Open Database"

这个插件让你在 VS Code 里就能看到表结构、浏览数据，不用离开编辑器。

> **本章后续演示以方式一（Python 交互环境）和方式二（SQLite 命令行）为主，选一种你舒服的方式跟着做就行。**

---

### 步骤 4：创建数据库文件

不管你用方式一还是方式二，现在你的项目目录里应该有了一个 `blog.db` 文件。

#### 用方式一（Python 交互环境）

```python
import sqlite3
conn = sqlite3.connect("blog.db")
cursor = conn.cursor()
```

注意：此时 `blog.db` 文件可能已经出现在你的项目目录里了。用 `dir`（Windows）或 `ls`（macOS/Linux）确认一下：

```powershell
# Windows PowerShell
dir blog.db
```

```bash
# macOS / Linux
ls -l blog.db
```

如果看到 `blog.db` 文件，说明数据库创建成功。文件大小可能显示为 0 字节——这是正常的，因为里面还没有任何表和数据。

#### 用方式二（SQLite 命令行）

```bash
sqlite3 blog.db
```

你会看到类似这样的输出：

```
SQLite version 3.45.0 2024-01-15 12:00:00
Enter ".help" for usage hints.
Connected to a transient in-memory database.
Use ".open FILENAME" to reopen on a persistent database.
sqlite>
```

`sqlite>` 就是 SQLite 的命令行提示符，跟 Python 的 `>>>` 一样——等着你输入命令。

> **如果没看到 `sqlite>` 提示符？** 可能是 `sqlite3` 命令不存在。回到步骤 3，用方式一（Python 交互环境）代替，或者安装 SQLite 命令行工具。

**现在，你硬盘上有了一个真正的数据库文件。** 虽然它现在是空的，但它已经是一个完整的 SQLite 数据库了。

---

### 步骤 5：认识 SQLite 的常用命令（`.help` 系列）

在 SQLite 命令行中，有一些以 `.`（点号）开头的特殊命令，它们是 SQLite 自己的管理命令，**不是 SQL 语句**。但在 Python 交互环境中，你不能直接用这些 `.` 命令——必须用对应的 Python 代码来替代。我们两边都讲。

#### 在 SQLite 命令行中

| 命令 | 作用 | 类比 |
|------|------|------|
| `.tables` | 列出所有表名 | 看 Excel 文件里有哪些 Sheet |
| `.schema 表名` | 查看某张表的建表语句（结构） | 看 Sheet 的表头（有哪些列、每列什么类型） |
| `.mode column` | 查询结果以对齐的列格式显示 | 让输出像 Excel 表格一样整齐，而不是乱糟糟的 |
| `.headers on` | 查询结果显示列名（表头） | 输出第一行显示列名，不然你不知道每列是什么 |
| `.quit` | 退出 SQLite 命令行 | 关掉 Excel 文件 |

#### 在 Python 交互环境中

Python 没有 `.` 命令，但你可以用 Python 代码实现同样的功能：

| SQLite 命令 | Python 等价代码 |
|------------|----------------|
| `.tables` | `cursor.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()` |
| `.schema 表名` | `cursor.execute("SELECT sql FROM sqlite_master WHERE name='表名';").fetchone()` |
| `.mode column` + `.headers on` | 不需要，Python 输出是原始数据，你可以用 `print` 自己格式化 |
| `.quit` | `conn.close()` 然后 `exit()` |

> **本章后续步骤**：我们先在 SQLite 命令行模式下演示（因为更直观），每条命令后面同时标注 Python 交互环境的等价写法。如果你全程用 Python 交互环境，跟着"Python 等价写法"走就行。

---

### 步骤 6：创建第一张表——`CREATE TABLE`

现在我们来创建一张测试表，感受一下 SQL 语句长什么样。

#### 在 SQLite 命令行中

确保你已经进入了 `sqlite>` 提示符。先设置显示格式，让后续查询结果好看一点：

```sql
.mode column
.headers on
```

然后创建表：

```sql
CREATE TABLE test (id INTEGER, name TEXT);
```

**回车后，如果什么都没发生——恭喜，成功了！** SQLite 的特点是：成功时不说话，只有出错时才报错。如果你看到 `sqlite>` 提示符又回来了，说明表创建成功。

现在用 `.tables` 验证：

```sql
.tables
```

输出：

```
test
```

你的表已经在了！用 `.schema` 看看它的结构：

```sql
.schema test
```

输出：

```
CREATE TABLE test (id INTEGER, name TEXT);
```

这就是你刚才输入的建表语句——SQLite 原样保存了它。

#### 在 Python 交互环境中

```python
import sqlite3
conn = sqlite3.connect("blog.db")
cursor = conn.cursor()

# 创建表
cursor.execute("CREATE TABLE test (id INTEGER, name TEXT);")

# 提交（保存到硬盘）
conn.commit()

# 验证：查看所有表
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
print(cursor.fetchall())
# 输出：[('test',)]

# 查看表结构
cursor.execute("SELECT sql FROM sqlite_master WHERE name='test';")
print(cursor.fetchone())
# 输出：('CREATE TABLE test (id INTEGER, name TEXT);',)
```

> **`conn.commit()` 是什么？** SQLite 的操作默认在"草稿"模式下——你做了修改，但还没保存到硬盘。`commit()` 就是"确认保存"——相当于 Word 里按 `Ctrl+S`。如果不执行 `commit()`，关闭 Python 后你的修改就丢了。`SELECT` 查询不需要 `commit()`，因为它只是读取，没有修改数据。

#### 逐行拆解 `CREATE TABLE` 语句

```sql
CREATE TABLE test (id INTEGER, name TEXT);
```

拆开看：

| 部分 | 含义 | 大白话 |
|------|------|--------|
| `CREATE TABLE` | 创建一个新表 | "我要新建一个 Sheet" |
| `test` | 表名 | "这个 Sheet 叫 test" |
| `(id INTEGER,` | 第一个列叫 `id`，类型是整数 | "A 列叫 id，只能填整数" |
| `name TEXT)` | 第二个列叫 `name`，类型是文本 | "B 列叫 name，填文字" |
| `;` | SQL 语句结束 | "我说完了，执行吧" |

**SQL 的数据类型**：SQLite 只有 5 种基本类型，你目前只需要记住两个：

| 类型 | 含义 | 例子 |
|------|------|------|
| `INTEGER` | 整数 | `1`, `42`, `999` |
| `TEXT` | 文本 | `'hello'`, `'Python 真好学'` |

> **SQL 语句不区分大小写**，但**约定俗成**：SQL 关键字（`CREATE`、`TABLE`、`INTEGER`、`TEXT`）用大写，你自己起的名字（`test`、`id`、`name`）用小写。这不是语法要求，而是让代码更易读的行业习惯。

---

### 🤔 想多一点：为什么需要"类型"？

你可能会想：Python 里变量不需要声明类型，`x = 1` 和 `x = "hello"` 随便写。为什么数据库要规定每列的类型？

**打个比方**：你有一个 Excel 表格，B 列是"年龄"。如果你在 B 列里填了一个"蓝色"，这个表格就失去了意义——"年龄"不可能是"蓝色"。数据库的类型约束就是防止这种"脏数据"进入系统。

更深一层：规定了类型，数据库就能**优化存储和查询**。整数列用整数专用的存储方式，比文本快得多。如果数据库知道 B 列全是整数，它就能用整数比较算法来排序和搜索，而不需要逐字比较字符串。

**Python 是"动态类型"（运行时才确定类型），SQL 是"静态类型"（建表时就确定类型）。** 两种设计哲学各有优劣：Python 写起来快，SQL 查起来快。你不需要在代码里"二选一"——你写 Python 代码，用 SQL 存数据，各取所长。

---

### 步骤 7：插入数据——`INSERT INTO`

表建好了，现在往里面放数据。

#### 在 SQLite 命令行中

```sql
INSERT INTO test VALUES (1, 'hello');
```

回车后，如果什么都没发生——又成功了。

让我们再插入两条，方便后续查询时看到多条数据：

```sql
INSERT INTO test VALUES (2, 'world');
INSERT INTO test VALUES (3, 'sqlite');
```

#### 逐行拆解 `INSERT INTO` 语句

```sql
INSERT INTO test VALUES (1, 'hello');
```

| 部分 | 含义 | 大白话 |
|------|------|--------|
| `INSERT INTO test` | 往 `test` 表里插入数据 | "在 test 这个 Sheet 里新增一行" |
| `VALUES (1, 'hello')` | 值：第一列 = `1`，第二列 = `'hello'` | "A 列填 1，B 列填 hello" |
| `;` | 语句结束 | "执行" |

> **注意**：`VALUES` 里的顺序必须和建表时列的顺序一致。`CREATE TABLE test (id INTEGER, name TEXT)` 先 `id` 后 `name`，所以 `VALUES` 里也先 `1`（id）后 `'hello'`（name）。

#### 在 Python 交互环境中

```python
# 插入三条数据
cursor.execute("INSERT INTO test VALUES (1, 'hello');")
cursor.execute("INSERT INTO test VALUES (2, 'world');")
cursor.execute("INSERT INTO test VALUES (3, 'sqlite');")

# 记得提交！
conn.commit()
```

> **又忘了 `commit()`？** 如果你插入数据后，关掉 Python 再打开，发现数据没了——十有八九是忘了 `conn.commit()`。养成习惯：每次修改数据（`INSERT`、`UPDATE`、`DELETE`）之后，立刻执行 `conn.commit()`。

---

### 步骤 8：查询数据——`SELECT`

现在来验证数据是不是真的在表里了。

#### 在 SQLite 命令行中

```sql
SELECT * FROM test;
```

输出：

```
id  name
--  ------
1   hello
2   world
3   sqlite
```

你的数据在！而且因为步骤 5 设置了 `.mode column` 和 `.headers on`，输出整整齐齐，像 Excel 表格一样。

#### 逐行拆解 `SELECT` 语句

```sql
SELECT * FROM test;
```

| 部分 | 含义 | 大白话 |
|------|------|--------|
| `SELECT` | 查询数据 | "我要看数据" |
| `*` | 所有列 | "所有列都要" |
| `FROM test` | 从 `test` 这张表里查 | "从 test 这个 Sheet 里找" |
| `;` | 语句结束 | "执行" |

**`*` 是通配符，代表"所有列"。** 如果你只想看 `name` 列，可以写：

```sql
SELECT name FROM test;
```

输出：

```
name
------
hello
world
sqlite
```

如果你只想看 `id` 为 2 的那一行，可以加条件：

```sql
SELECT * FROM test WHERE id = 2;
```

输出：

```
id  name
--  ------
2   world
```

`WHERE` 就是筛选条件——"只看 id 等于 2 的那一行"。这就像 Excel 里的筛选功能，只不过你用文字而不是鼠标来操作。

#### 在 Python 交互环境中

```python
# 查询所有数据
cursor.execute("SELECT * FROM test;")
rows = cursor.fetchall()
for row in rows:
    print(row)

# 输出：
# (1, 'hello')
# (2, 'world')
# (3, 'sqlite')
```

`fetchall()` 返回一个列表，里面每个元素是一个元组（tuple），对应一行数据。元组里的顺序和建表时的列顺序一致。

---

### ❌ 常见错误 → ✅ 正确示例

#### 错误 1：忘记分号

❌ 错误：

```sql
CREATE TABLE test (id INTEGER, name TEXT)
```

在 SQLite 命令行中，你没打 `;` 就按了回车，结果出现了 `...>` 提示符。SQLite 在等你继续输入——它以为你的 SQL 语句还没写完。

✅ 正确：

```sql
CREATE TABLE test (id INTEGER, name TEXT);
```

**在 SQL 中，分号是语句结束的标志。** 每一条 SQL 语句必须以分号结尾。如果你忘了，SQLite 会一直等着你输入更多内容。

**已经卡在 `...>` 了怎么办？** 输入一个分号 `;` 然后回车，SQLite 会尝试执行你输入的内容（大概率报错），然后回到正常的 `sqlite>` 提示符。如果还不行，按 `Ctrl+C` 退出，重新连接。

---

#### 错误 2：字符串没加引号

❌ 错误：

```sql
INSERT INTO test VALUES (4, hello);
```

`hello` 没加引号，SQLite 以为它是一个列名（或关键字），然后报错：`Error: no such column: hello`。

✅ 正确：

```sql
INSERT INTO test VALUES (4, 'hello');
```

**SQL 中，文本值必须用单引号 `'` 包裹。** 双引号在 SQLite 中通常也有效，但标准 SQL 认为双引号是"标识符引用"（比如表名中有空格），所以用单引号更安全。

---

#### 错误 3：Windows 路径中有中文或空格

❌ 错误：

```powershell
sqlite3 "D:\我的项目\blog.db"
```

路径中有中文或空格，可能导致 SQLite 找不到文件或创建失败。

✅ 正确：把项目放在纯英文路径下，不要有空格和中文。

```powershell
# 比如
cd D:\Project\blog
sqlite3 blog.db
```

如果你已经在中文路径下了，最简单的办法是**直接用 Python 交互环境**（方式一），因为 Python 对中文路径的兼容性比 SQLite 命令行工具好：

```python
import sqlite3
conn = sqlite3.connect("blog.db")  # Python 能正确处理中文路径
```

---

#### 错误 4：`CREATE TABLE` 后忘记 `conn.commit()`

这只影响 Python 交互环境。SQLite 命令行工具默认自动提交。

❌ 错误：

```python
import sqlite3
conn = sqlite3.connect("blog.db")
cursor = conn.cursor()
cursor.execute("CREATE TABLE test (id INTEGER, name TEXT);")
conn.close()  # 没调 commit()！表没保存！
```

关掉 Python 再打开，表不存在。

✅ 正确：

```python
import sqlite3
conn = sqlite3.connect("blog.db")
cursor = conn.cursor()
cursor.execute("CREATE TABLE test (id INTEGER, name TEXT);")
conn.commit()  # 别忘了保存！
```

---

### 步骤 9：退出——优雅地关闭数据库

操作完了，怎么退出？

#### 在 SQLite 命令行中

```sql
.quit
```

回车后，你回到普通的终端提示符。`blog.db` 文件已经保存在硬盘上了。

#### 在 Python 交互环境中

```python
conn.close()
exit()
```

`conn.close()` 关闭数据库连接（释放资源），`exit()` 退出 Python 交互环境。

> **如果你忘了 `conn.close()`**：关掉终端窗口也能自动关闭连接，但养成主动关闭的习惯更好——就像你离开房间时关灯一样，虽然不关也不会着火烧房子，但关了更省电（释放资源）。

---

### 步骤 10：验证数据持久化——关了再打开，数据还在

这是 SQLite 最让人安心的特性：**数据写到硬盘上了，关掉再打开也不会丢。**

#### 在 SQLite 命令行中

```bash
# 如果还在 sqlite 里，先退出
.quit

# 重新打开同一个文件
sqlite3 blog.db

# 设置显示格式
.mode column
.headers on

# 查询
SELECT * FROM test;
```

输出：

```
id  name
--  ------
1   hello
2   world
3   sqlite
```

**数据还在！** 不管你的电脑重启多少次，这些数据都不会消失——除非你手动删掉 `blog.db` 文件。

#### 在 Python 交互环境中

```python
import sqlite3
conn = sqlite3.connect("blog.db")
cursor = conn.cursor()
cursor.execute("SELECT * FROM test;")
for row in cursor.fetchall():
    print(row)
conn.close()

# 输出：
# (1, 'hello')
# (2, 'world')
# (3, 'sqlite')
```

**对比一下第 07 章的内存版 CRUD**：那时候你的博客文章存在 `blogs = []` 这个 Python 列表里，服务器重启，列表重新初始化为空，数据全没了。现在有了 `blog.db`，数据持久化到了硬盘上。这就是从"草稿纸"到"笔记本"的升级。

---

### 🤔 想多一点：为什么 SQLite 用 `sqlite3` 而不是 `sqlite`？

你可能会注意到：Python 的模块叫 `sqlite3`，SQLite 的版本号也是 `3.x.x`。那 `sqlite1` 和 `sqlite2` 去哪了？

SQLite 从 2000 年诞生，经历了两个大版本迭代。SQLite 3 是 2004 年发布的，完全重写了文件格式，与 SQLite 2 不兼容。**从那以后，SQLite 3 就是这个项目的唯一版本，已经持续了 20 多年。** 作者 D. Richard Hipp 承诺：SQLite 3 的文件格式**直到 2050 年都不会改变**。你今天创建的 `blog.db`，在 2050 年的 SQLite 中依然能打开。

这个承诺背后是一个深刻的设计哲学：**向后兼容比新功能更重要。** 全世界有一万亿个 SQLite 数据库在运行，如果文件格式改了，所有这些数据库都需要迁移——这是不可接受的。所以 SQLite 选择了一条"保守"的路：不轻易改底层，只在现有基础上优化。

**这跟很多技术项目形成了鲜明对比**——有些项目每两年就大改一次 API，让开发者疲于奔命。SQLite 的"稳定到无聊"反而成了它最大的竞争力。

---

## 四、完整代码清单

本章不涉及项目代码文件，所有操作在终端或 Python 交互环境中完成。以下是你执行过的所有命令的汇总：

### SQLite 命令行模式（完整操作序列）

```sql
-- 打开数据库文件
sqlite3 blog.db

-- 设置显示格式
.mode column
.headers on

-- 创建表
CREATE TABLE test (id INTEGER, name TEXT);

-- 查看所有表
.tables

-- 查看表结构
.schema test

-- 插入数据
INSERT INTO test VALUES (1, 'hello');
INSERT INTO test VALUES (2, 'world');
INSERT INTO test VALUES (3, 'sqlite');

-- 查询所有数据
SELECT * FROM test;

-- 按条件查询
SELECT * FROM test WHERE id = 2;

-- 只查特定列
SELECT name FROM test;

-- 退出
.quit
```

### Python 交互环境模式（完整操作序列）

```python
import sqlite3

# 连接数据库（不存在则自动创建）
conn = sqlite3.connect("blog.db")
cursor = conn.cursor()

# 创建表
cursor.execute("CREATE TABLE test (id INTEGER, name TEXT);")
conn.commit()

# 查看所有表
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
print(cursor.fetchall())

# 查看表结构
cursor.execute("SELECT sql FROM sqlite_master WHERE name='test';")
print(cursor.fetchone())

# 插入数据
cursor.execute("INSERT INTO test VALUES (1, 'hello');")
cursor.execute("INSERT INTO test VALUES (2, 'world');")
cursor.execute("INSERT INTO test VALUES (3, 'sqlite');")
conn.commit()

# 查询所有数据
cursor.execute("SELECT * FROM test;")
for row in cursor.fetchall():
    print(row)

# 按条件查询
cursor.execute("SELECT * FROM test WHERE id = 2;")
print(cursor.fetchone())

# 关闭连接
conn.close()
```

---

## 五、验证方法

在终端中依次执行以下操作，确认一切正常：

### 1. 确认数据库文件存在

```powershell
# Windows PowerShell
dir blog.db
```

```bash
# macOS / Linux
ls -l blog.db
```

应该能看到 `blog.db` 文件。

### 2. 确认数据持久化

```bash
# 打开数据库
sqlite3 blog.db

# 设置格式
.mode column
.headers on

# 查询
SELECT * FROM test;
```

预期输出：

```
id  name
--  ------
1   hello
2   world
3   sqlite
```

### 3. 确认 Python 也能读取

```python
import sqlite3
conn = sqlite3.connect("blog.db")
cursor = conn.cursor()
cursor.execute("SELECT * FROM test;")
rows = cursor.fetchall()
assert len(rows) == 3  # 应该有 3 行数据
print("验证通过！共", len(rows), "行数据")
conn.close()
```

三条全部通过，本章完成。

---

## 六、小结

| 你学到了什么 | 一句话总结 |
|-------------|-----------|
| 数据库是什么 | 硬盘上的"Excel 文件"，存数据用的，程序重启数据不丢 |
| 表（Table） | Excel 里的一个 Sheet，一类数据的集合 |
| 行（Row）/ 记录 | 一行数据，比如"第 3 号文章" |
| 列（Column）/ 字段 | 一列属性，比如"标题"、"作者" |
| SQLite 的特点 | 零配置、一个文件就是数据库、Python 自带支持 |
| `CREATE TABLE` | 建表语句，定义表名、列名和每列的类型 |
| `INSERT INTO` | 插入数据，往表里新增一行 |
| `SELECT` | 查询数据，`*` 表示所有列，`WHERE` 加筛选条件 |
| `INTEGER` / `TEXT` | SQLite 的两种基本数据类型：整数和文本 |
| `conn.commit()` | 在 Python 中，修改数据后必须提交（保存到硬盘） |
| `.tables` / `.schema` / `.quit` | SQLite 命令行的管理命令，查看表、查看结构、退出 |
| 数据持久化 | 关掉程序再打开，数据还在硬盘上——跟内存版 CRUD 的最大区别 |

---

## 七、术语附录

| 术语 | 英文 | 通俗解释 | 本章出现位置 |
|------|------|----------|-------------|
| 数据库 | Database | 一个持久化存储数据的容器，类比一个 Excel 文件。程序重启后数据依然存在，不像 Python 变量那样消失。 | 步骤 1 |
| SQLite | — | 一种轻量级嵌入式数据库。零配置，一个文件就是整个数据库，Python 自带支持。全球有一万亿个实例在运行。**字面陷阱**：名字里有 "Lite"（轻量），但不代表它功能弱——它支持完整的 SQL 标准，只是"轻量"在部署和使用上。 | 步骤 2 |
| 表 | Table | 数据库中一类数据的集合，类比 Excel 的一个 Sheet。一张表包含若干行（记录）。 | 步骤 1 |
| 行 | Row / Record | 表中的一条记录，类比 Excel 的一行。比如"第 3 号文章"就是一行。 | 步骤 1 |
| 列 | Column / Field | 表中的一个属性字段，类比 Excel 的一列。比如"标题"列、"作者"列。 | 步骤 1 |
| CREATE TABLE | — | SQL 建表语句，定义表的结构（有哪些列、每列什么类型）。 | 步骤 6 |
| INSERT INTO | — | SQL 插入语句，向表中新增一行数据。 | 步骤 7 |
| SELECT | — | SQL 查询语句，从表中读取数据。`*` 表示"所有列"，`WHERE` 后接筛选条件。 | 步骤 8 |
| 游标 | Cursor | Python 中执行 SQL 语句的"光标"。通过 `conn.cursor()` 创建，用 `cursor.execute()` 执行 SQL，用 `cursor.fetchall()` 获取结果。 | 步骤 3 |
| 提交 | Commit | 将修改保存到硬盘的操作。在 Python 中 SQLite 默认不自动提交，必须手动调用 `conn.commit()`。SQLite 命令行工具默认自动提交。 | 步骤 6 |
| 持久化 | Persistence | 数据保存到硬盘（或其他非易失性存储）上，程序关闭后数据不丢失。与"内存存储"（程序关闭数据消失）相对。 | 步骤 10 |

---

## 八、已知坑点与禁止事项

| 坑点 | 现象 | 原因 | 解决 |
|------|------|------|------|
| SQL 语句忘记分号 | 输入 `CREATE TABLE ...` 后出现 `...>` 提示符 | SQLite 在等语句结束 | 输入 `;` 回车，或按 `Ctrl+C` 退出后重新连接 |
| 字符串没加引号 | `INSERT INTO test VALUES (1, hello)` 报错 `no such column: hello` | SQL 中文本值必须用单引号 `'` 包裹 | 改为 `INSERT INTO test VALUES (1, 'hello');` |
| 路径中有中文或空格 | `sqlite3 blog.db` 报错"无法打开文件" | SQLite 命令行工具对中文路径兼容性较差 | 将项目放在纯英文路径下，或用 Python 交互环境代替 |
| Windows 没有 `sqlite3` 命令 | `'sqlite3' 不是内部或外部命令` | Windows 未预装 SQLite 命令行工具 | 用 Python 交互环境（`import sqlite3`），或下载 SQLite 命令行工具 |
| Python 中忘了 `conn.commit()` | 插入数据后关掉 Python，再打开数据没了 | SQLite 的 Python 模块默认不自动提交 | 每次 `INSERT`、`UPDATE`、`DELETE` 后执行 `conn.commit()` |
| 用双引号代替单引号 | `INSERT INTO test VALUES (1, "hello")` 在 SQLite 中可能有效，但在其他数据库（如 MySQL 严格模式）中报错 | 标准 SQL 中双引号用于标识符引用，不是字符串引用 | 始终用单引号 `'` 包裹字符串值 |
| `CREATE TABLE` 表名和关键字冲突 | 创建名为 `table` 或 `select` 的表 | 这些是 SQL 保留字，不能用做表名 | 避免用 SQL 关键字做表名，如果必须用，加双引号（如 `CREATE TABLE "table" (...)`） |

---

## 九、下一步建议

你已经掌握了数据库的基本操作——建表、插入、查询。但本章的 `test` 表只是一个热身。接下来：

- **下一章**：[10-用 SQLite 重构博客 CRUD](./10-用SQLite重构博客CRUD.md)（规划中）——把你第 07 章写的内存版博客 CRUD 改造成数据库版，文章真正存到硬盘上，服务器重启也不丢。
- **延伸实验**：
  - 试着用 `DROP TABLE test;` 删除 `test` 表（注意：数据和表结构一起删除，不可恢复）。
  - 试着用 `UPDATE test SET name = '你好' WHERE id = 1;` 修改第 1 行的数据。
  - 试着用 `DELETE FROM test WHERE id = 3;` 删除第 3 行数据。
  - 在 Python 中用 `sqlite3` 模块写一个完整的"创建表 → 插入数据 → 查询 → 关闭"脚本，保存为 `.project/_sandbox/test_sqlite.py`，跑一遍。

---

> **本章编辑记录**：2026-06-05 初始版本。