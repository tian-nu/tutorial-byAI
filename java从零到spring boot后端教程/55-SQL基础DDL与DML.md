# 第55章 · SQL基础：DDL与DML

> "仓库建好了，现在是时候在里面搭货架、搬货、改标签了。SQL就是跟仓库管理员交流的标准语言——你说'把第三排货架上红色的箱子全搬过来'，管理员听得懂，机器也听得懂。这门语言比你想象的简单，也比你想象的强大。"

---

## 55.1 SQL是什么

SQL的全称是**Structured Query Language**（结构化查询语言）。注意，大部分中国程序员直接念"S-Q-L"三个字母，面试时两种发音都行。

SQL是你的仓库管理员指令手册。你对着MySQL输入：

```sql
SELECT name, phone FROM users WHERE age > 18;
```

翻译成管理员能懂的话就是："去users货架上，把所有age大于18的箱子打开，把里面的name和phone拿出来给我。"

**关键认知**：SQL是共通的。你学会了MySQL的SQL，去用PostgreSQL、Oracle、SQL Server时，90%的语句一模一样。就像你会开大众，去开丰田只需要适应一下方向盘手感——核心操作不变。

---

## 55.2 SQL的五大分类

SQL语句按功能分为五大类，理解这个分类会让你的知识体系非常清晰：

| 分类 | 英文 | 作用 | 比喻 | 核心动词 |
|------|------|------|------|----------|
| DDL | Data Definition Language | 定义数据结构 | 搭货架、拆货架 | CREATE / ALTER / DROP / TRUNCATE |
| DML | Data Manipulation Language | 操作数据内容 | 往箱子里放东西、改贴纸 | INSERT / UPDATE / DELETE |
| DQL | Data Query Language | 查询数据 | 在仓库里找东西 | SELECT |
| DCL | Data Control Language | 控制权限 | 给员工发钥匙、收钥匙 | GRANT / REVOKE |
| TCL | Transaction Control Language | 控制事务 | 批量操作确认/回滚按钮 | COMMIT / ROLLBACK / SAVEPOINT |

本章重点讲DDL和DML，下一章讲DQL。DCL和TCL在事务章节详细展开。

> **新手记忆法**：DDL管"货架长什么样"，DML管"货架上有什么东西"，DQL管"帮我找一下东西在哪"。

---

## 55.3 数据类型

搭建货架之前，你得先想好每个格子装什么东西。MySQL提供了丰富的"格子类型"：

### 整数类型

| 类型 | 字节数 | 有符号范围 | 无符号范围 |
|------|--------|-----------|-----------|
| TINYINT | 1 | -128 ~ 127 | 0 ~ 255 |
| SMALLINT | 2 | -32768 ~ 32767 | 0 ~ 65535 |
| MEDIUMINT | 3 | -838万 ~ 838万 | 0 ~ 1677万 |
| INT | 4 | -21亿 ~ 21亿 | 0 ~ 42亿 |
| BIGINT | 8 | -922京 ~ 922京 | 0 ~ 1844京 |

**选择原则**：用最小的够用类型。比如年龄用TINYINT（没人能活256岁以上），用户ID用INT或BIGINT（看用户量）。

### 小数类型

| 类型 | 说明 |
|------|------|
| FLOAT / DOUBLE | 近似值，有精度损失 |
| DECIMAL(M, D) | 精确值，M=总位数，D=小数位数 |

**金额永远用DECIMAL**。比如 `DECIMAL(10, 2)` 表示总共10位，其中2位小数（最大 99999999.99）。用FLOAT存钱，算着算着就会出现0.01的误差——财务对不上账你就等着被叫去喝茶。

### 字符串类型

| 类型 | 最大长度 | 存储方式 |
|------|---------|----------|
| CHAR(N) | 255字符 | 定长，不管存几个字符都占N个位置 |
| VARCHAR(N) | 65535字节 | 变长，存几个占几个+1~2字节开销 |
| TEXT | 65535字节 | 长文本，不参与排序和索引 |
| LONGTEXT | 4GB | 超长文本 |

**CHAR vs VARCHAR 比喻**：

CHAR是**固定格子**——你说"这个格子放10个字"，它就造一个10个字宽的格子。你放"你好"两个字，剩下8个空位用空格填满。好处是存取快（位置固定，不用计算），坏处是浪费空间。

VARCHAR是**弹性盒子**——你说"这个盒子最多装10个字"，它就会按你实际放了多少字来伸缩。放"你好"就占2个字的物理空间。好处是省空间，坏处是更新数据时如果从"你好"改成"你好世界你好世界"，盒子要扩容，有一定开销。

### 日期时间类型

| 类型 | 格式 | 范围 |
|------|------|------|
| DATE | YYYY-MM-DD | 1000-01-01 ~ 9999-12-31 |
| TIME | HH:MM:SS | -838:59:59 ~ 838:59:59 |
| DATETIME | YYYY-MM-DD HH:MM:SS | 1000-01-01 00:00:00 ~ 9999-12-31 23:59:59 |
| TIMESTAMP | YYYY-MM-DD HH:MM:SS | 1970-01-01 00:00:01 ~ 2038-01-19 03:14:07 |

**DATETIME vs TIMESTAMP**：TIMESTAMP会随服务器时区自动转换，适合记录"这条数据什么时候被修改的"，但范围受限于2038年。DATETIME存什么就是什么，适合生日、会议时间等固定时刻。

---

## 55.4 DDL：定义数据结构

DDL是"建筑师的工作"——决定仓库是什么结构、每排货架长什么样。

### 55.4.1 创建数据库

```sql
-- 创建一个数据库
CREATE DATABASE my_shop;

-- 创建数据库时指定字符集（强烈推荐）
CREATE DATABASE my_shop
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;
```

| 参数 | 含义 |
|------|------|
| `CHARACTER SET utf8mb4` | 字符集为utf8mb4，支持emoji表情（`utf8` 是阉割版，不支持emoji） |
| `COLLATE utf8mb4_unicode_ci` | 排序规则，`ci` = Case Insensitive（不区分大小写） |

> ⚠️ **必须用 `utf8mb4` 而不是 `utf8`**！MySQL的 `utf8` 是历史遗留的阉割版，最多只支持3字节，存不了emoji（4字节）。用 `utf8mb4`（Most Bytes 4）才是真正的UTF-8。

**查看所有数据库**：

```sql
SHOW DATABASES;
```

**使用（切换）数据库**：

```sql
USE my_shop;
```

**删除数据库**：

```sql
DROP DATABASE my_shop;
```

> ⚠️ `DROP DATABASE` 会删除数据库内**所有表和数据**，且不可恢复。生产环境执行前务必确认两遍。

### 55.4.2 创建表

现在搭第一个货架——用户表：

```sql
CREATE TABLE users (
    id         INT AUTO_INCREMENT PRIMARY KEY COMMENT '用户ID，主键自增',
    username   VARCHAR(50)  NOT NULL UNIQUE COMMENT '用户名，唯一',
    password   VARCHAR(255) NOT NULL COMMENT '加密后的密码，255位是为了容纳BCrypt哈希',
    email      VARCHAR(100) NOT NULL COMMENT '邮箱',
    age        TINYINT UNSIGNED COMMENT '年龄，无符号0-255',
    balance    DECIMAL(10, 2) DEFAULT 0.00 COMMENT '账户余额，默认0',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';
```

逐行解读：

| 语句片段 | 含义 |
|----------|------|
| `INT AUTO_INCREMENT` | 整数类型，每次插入自动+1 |
| `PRIMARY KEY` | 主键，唯一标识一行，不允许NULL |
| `NOT NULL` | 不允许为空 |
| `UNIQUE` | 值必须唯一，不能重复 |
| `TINYINT UNSIGNED` | 无符号TINYINT，范围0~255 |
| `DEFAULT 0.00` | 不指定值时默认为0 |
| `DEFAULT CURRENT_TIMESTAMP` | 默认值为当前时间 |
| `ON UPDATE CURRENT_TIMESTAMP` | 行被修改时自动更新为当前时间 |
| `COMMENT '...'` | 注释，给列和表加说明 |
| `ENGINE=InnoDB` | 存储引擎，InnoDB支持事务和行级锁 |
| `CHARSET=utf8mb4` | 表级别字符集 |

**查看表结构**：

```sql
DESC users;
-- 或者
SHOW CREATE TABLE users;
```

DESC输出示例：

```
+------------+------------------+------+-----+-------------------+-------------------+
| Field      | Type             | Null | Key | Default           | Extra             |
+------------+------------------+------+-----+-------------------+-------------------+
| id         | int              | NO   | PRI | NULL              | auto_increment    |
| username   | varchar(50)      | NO   | UNI | NULL              |                   |
| password   | varchar(255)     | NO   |     | NULL              |                   |
| email      | varchar(100)     | NO   |     | NULL              |                   |
| age        | tinyint unsigned | YES  |     | NULL              |                   |
| balance    | decimal(10,2)    | YES  |     | 0.00              |                   |
| created_at | datetime         | YES  |     | CURRENT_TIMESTAMP |                   |
| updated_at | datetime         | YES  |     | CURRENT_TIMESTAMP | on update         |
+------------+------------------+------+-----+-------------------+-------------------+
```

### 55.4.3 修改表结构

```sql
-- 添加列
ALTER TABLE users ADD COLUMN phone VARCHAR(20) COMMENT '手机号';

-- 修改列类型
ALTER TABLE users MODIFY COLUMN phone VARCHAR(30);

-- 重命名列（同时可能改类型）
ALTER TABLE users CHANGE COLUMN phone mobile VARCHAR(30);

-- 删除列（危险操作）
ALTER TABLE users DROP COLUMN mobile;

-- 添加索引
ALTER TABLE users ADD INDEX idx_username (username);

-- 重命名表
ALTER TABLE users RENAME TO app_users;
```

### 55.4.4 删除表

```sql
-- 删除表结构+所有数据
DROP TABLE users;

-- 清空表数据但保留表结构
TRUNCATE TABLE users;
```

`DROP TABLE` = 把整个货架拆了扔掉。`TRUNCATE TABLE` = 把货架上的箱子全清空，货架还在。

> ⚠️ `TRUNCATE` 比 `DELETE` 快（它不走事务日志），但不可回滚。除非你明确知道自己在做什么，否则用 `DELETE FROM users;`（不带WHERE会删所有数据，但可回滚）。

---

## 55.5 DML：操作数据内容

DML是"仓库工人的工作"——往货架上放东西、搬东西、改标签、扔东西。

### 55.5.1 插入数据：INSERT

**单行插入**：

```sql
INSERT INTO users (username, password, email, age, balance)
VALUES ('zhangsan', 'hashed_password_here', 'zhangsan@example.com', 25, 1000.00);
```

**多行插入**（批量插入效率远高于多次单行插入）：

```sql
INSERT INTO users (username, password, email, age)
VALUES
    ('lisi',   'pass_lisi',   'lisi@example.com',   30),
    ('wangwu', 'pass_wangwu', 'wangwu@example.com', 28),
    ('zhaoliu','pass_zhaoliu','zhaoliu@example.com',22);
```

**省略列名**（不推荐，列顺序变了就出错）：

```sql
INSERT INTO users VALUES (NULL, 'sunqi', 'pass_sunqi', 'sunqi@example.com', 35, 500.00, NOW(), NOW());
```

> 💡 自增主键那列写 `NULL` 或 `DEFAULT`，MySQL会自动生成下一个值。或者直接省略该列。

### 55.5.2 查询数据：SELECT

这是数据库最高频的操作，第56章会深入展开。这里只给最基础的形式：

```sql
-- 查全部
SELECT * FROM users;

-- 指定列
SELECT id, username, email FROM users;

-- 条件筛选
SELECT * FROM users WHERE age > 25;

-- 排序
SELECT * FROM users ORDER BY age DESC;

-- 限制数量
SELECT * FROM users LIMIT 10;
```

### 55.5.3 更新数据：UPDATE

```sql
-- 更新单列
UPDATE users SET age = 26 WHERE id = 1;

-- 更新多列
UPDATE users SET age = 27, balance = balance + 100 WHERE id = 1;

-- 不加WHERE会更新所有行！！！
UPDATE users SET balance = 0;
-- 上面这行会把你所有用户的余额清零——这就是为什么MySQL默认开启了safe update mode
```

### 55.5.4 删除数据：DELETE

```sql
-- 删除指定行
DELETE FROM users WHERE id = 3;

-- 删除所有行（危险！但可回滚）
DELETE FROM users;

-- 批量条件删除
DELETE FROM users WHERE age < 18;
```

---

## 55.6 WHERE条件详解

WHERE子句支持丰富的条件组合：

| 操作符 | 含义 | 示例 |
|--------|------|------|
| `=` | 等于 | `WHERE age = 25` |
| `!=` 或 `<>` | 不等于 | `WHERE age != 25` |
| `>` `<` `>=` `<=` | 大于、小于等 | `WHERE balance >= 1000` |
| `BETWEEN a AND b` | 在a~b之间（含两端） | `WHERE age BETWEEN 20 AND 30` |
| `IN (a, b, c)` | 在给定的集合中 | `WHERE age IN (18, 25, 30)` |
| `IS NULL` | 是空值 | `WHERE phone IS NULL` |
| `IS NOT NULL` | 不是空值 | `WHERE phone IS NOT NULL` |
| `AND` | 同时满足 | `WHERE age > 20 AND balance > 500` |
| `OR` | 满足任一 | `WHERE age < 20 OR age > 60` |
| `NOT` | 取反 | `WHERE NOT (age < 18)` |
| `LIKE` | 模糊匹配 | `WHERE username LIKE 'zhang%'` |

**LIKE通配符**：

| 通配符 | 含义 | 示例 |
|--------|------|------|
| `%` | 匹配任意多个字符 | `'zhang%'` → zhang开头 |
| `_` | 匹配单个字符 | `'zhang_'` → zhang后面只有一个字符 |

```sql
-- 名字以 'zhang' 开头
SELECT * FROM users WHERE username LIKE 'zhang%';

-- 邮箱包含 @qq.com
SELECT * FROM users WHERE email LIKE '%@qq.com';

-- 名字是三个字，以 '三' 结尾
SELECT * FROM users WHERE username LIKE '__三';
```

> ⚠️ `LIKE '%xxx%'` 开头带 `%` 会导致全表扫描，无法使用索引。大数据量下非常慢。

---

## 55.7 完整练习：从创建到删除

在MySQL命令行或DBeaver中依次执行以下SQL，跟着走一遍：

```sql
-- 1. 创建数据库
CREATE DATABASE sql_practice CHARACTER SET utf8mb4;
USE sql_practice;

-- 2. 创建学生表
CREATE TABLE students (
    id      INT AUTO_INCREMENT PRIMARY KEY,
    name    VARCHAR(50) NOT NULL,
    gender  ENUM('男', '女') NOT NULL,
    score   TINYINT UNSIGNED NOT NULL,
    class   VARCHAR(20)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 3. 插入数据
INSERT INTO students (name, gender, score, class) VALUES
    ('张三', '男', 88, '一班'),
    ('李四', '女', 92, '一班'),
    ('王五', '男', 75, '二班'),
    ('赵六', '女', 95, '二班'),
    ('孙七', '男', 60, '一班');

-- 4. 查询验证
SELECT * FROM students;

-- 5. 修改数据
UPDATE students SET score = score + 5 WHERE name = '孙七';

-- 6. 删除数据
DELETE FROM students WHERE score < 70 AND class = '二班';

-- 7. 查看最终结果
SELECT * FROM students ORDER BY score DESC;

-- 8. 练习结束，删除表
DROP TABLE students;
DROP DATABASE sql_practice;
```

---

## 本章小结

| 概念 | 要点 |
|------|------|
| SQL | 结构化查询语言，操作关系型数据库的标准语言 |
| DDL | 定义数据结构：CREATE/ALTER/DROP DATABASE/TABLE |
| DML | 操作数据：INSERT/UPDATE/DELETE |
| 数据类型 | 整数(INT系列)、精确小数(DECIMAL)、字符串(VARCHAR>CHAR)、日期(DATETIME) |
| utf8mb4 | 必须用的字符集，utf8是阉割版不支持emoji |
| WHERE | 条件筛选，支持=, !=, >, <, BETWEEN, IN, LIKE, AND, OR |
| 安全提醒 | UPDATE和DELETE不加WHERE会操作全表 |

---

## 自测题

1. **写出创建商品表的SQL：表名 `products`，包含 `id`（自增主键）、`name`（VARCHAR 100，不为空）、`price`（DECIMAL 8,2，不为空）、`stock`（INT，不为空，默认0）、`created_at`（DATETIME，默认当前时间）。使用InnoDB引擎和utf8mb4字符集。**

2. **表中已有10条数据，执行 `DELETE FROM users;` 和 `TRUNCATE TABLE users;` 有什么区别？**

3. **VARCHAR(50) 和 CHAR(50) 的区别是什么？什么场景用哪个？**

<details>
<summary>参考答案（做完再看）</summary>

1. ```sql
CREATE TABLE products (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    name       VARCHAR(100) NOT NULL,
    price      DECIMAL(8, 2) NOT NULL,
    stock      INT NOT NULL DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

2. `DELETE FROM users;` 逐行删除，走事务日志，可以回滚（如果开启了事务）。`TRUNCATE TABLE users;` 直接释放数据页，不走逐行删除，不可回滚，速度更快，还会重置自增计数器。开发时除非明确需要重置表，否则用DELETE。

3. CHAR(50)固定占50个字符的存储空间，存取快但浪费空间，适合存固定长度的数据（如手机号、身份证号、MD5哈希）。VARCHAR(50)按实际字符数+1~2字节存储，省空间但更新长文本时有扩容开销，适合存长度不固定的数据（如用户名、邮箱、地址）。日常开发中VARCHAR的使用频率远高于CHAR。
</details>