# 附录 B — SQL 语法速查表

> 本附录按 SQL 语句的五种分类（DDL / DML / DQL / DCL / TCL）组织，给出每种语句的语法骨架和最常用示例。这不是完整语法手册，而是"我要写一条 XXX 语句，基本格式是什么"的速查。

---

## 一、DDL（Data Definition Language，数据定义语言）

DDL 操作的是**数据库对象的结构**（表、索引、视图等），而非数据本身。

### 1.1 数据库操作

| 语法 | 示例 | 说明 |
|------|------|------|
| `CREATE DATABASE [IF NOT EXISTS] db_name [CHARSET charset] [COLLATE collation];` | `CREATE DATABASE ecommerce DEFAULT CHARSET utf8mb4 COLLATE utf8mb4_unicode_ci;` | 创建数据库 |
| `DROP DATABASE [IF EXISTS] db_name;` | `DROP DATABASE IF EXISTS test_db;` | 删除数据库 |
| `ALTER DATABASE db_name CHARSET utf8mb4;` | `ALTER DATABASE ecommerce CHARSET utf8mb4;` | 修改数据库字符集 |
| `USE db_name;` | `USE ecommerce;` | 切换数据库 |

### 1.2 表操作

| 语法 | 示例 | 说明 |
|------|------|------|
| `CREATE TABLE [IF NOT EXISTS] t (col TYPE [约束], ...) [ENGINE=InnoDB] [CHARSET=utf8mb4];` | `CREATE TABLE users (id INT PRIMARY KEY AUTO_INCREMENT, name VARCHAR(50) NOT NULL);` | 创建表 |
| `DROP TABLE [IF EXISTS] t;` | `DROP TABLE IF EXISTS temp;` | 删除表 |
| `ALTER TABLE t ADD COLUMN col TYPE [约束];` | `ALTER TABLE users ADD COLUMN age INT DEFAULT 0;` | 添加列 |
| `ALTER TABLE t MODIFY COLUMN col NEW_TYPE;` | `ALTER TABLE users MODIFY COLUMN age TINYINT UNSIGNED;` | 修改列类型 |
| `ALTER TABLE t CHANGE old_name new_name TYPE;` | `ALTER TABLE users CHANGE age user_age TINYINT;` | 重命名列 |
| `ALTER TABLE t DROP COLUMN col;` | `ALTER TABLE users DROP COLUMN user_age;` | 删除列 |
| `ALTER TABLE t ADD INDEX idx_name (col);` | `ALTER TABLE users ADD INDEX idx_name (name);` | 添加索引 |
| `ALTER TABLE t ADD PRIMARY KEY (col);` | `ALTER TABLE temp ADD PRIMARY KEY (id);` | 添加主键 |
| `ALTER TABLE t ADD FOREIGN KEY (col) REFERENCES t2(col);` | `ALTER TABLE orders ADD FOREIGN KEY (user_id) REFERENCES users(id);` | 添加外键 |
| `ALTER TABLE t RENAME TO new_name;` | `ALTER TABLE orders RENAME TO orders_archive;` | 重命名表 |
| `TRUNCATE TABLE t;` | `TRUNCATE TABLE log;` | 清空表（不可回滚，比 DELETE 快） |

### 1.3 索引操作

| 语法 | 示例 | 说明 |
|------|------|------|
| `CREATE INDEX idx_name ON t (col);` | `CREATE INDEX idx_status ON orders (status);` | 创建普通索引 |
| `CREATE UNIQUE INDEX idx_name ON t (col);` | `CREATE UNIQUE INDEX uk_email ON users (email);` | 创建唯一索引 |
| `CREATE INDEX idx_name ON t (col1, col2);` | `CREATE INDEX idx_user_status ON orders (user_id, status);` | 创建联合索引 |
| `CREATE FULLTEXT INDEX idx_name ON t (col);` | `CREATE FULLTEXT INDEX ft_content ON articles (content) WITH PARSER ngram;` | 创建全文索引 |
| `DROP INDEX idx_name ON t;` | `DROP INDEX idx_status ON orders;` | 删除索引 |

### 1.4 视图操作

| 语法 | 示例 | 说明 |
|------|------|------|
| `CREATE VIEW v AS SELECT ...;` | `CREATE VIEW active_users AS SELECT * FROM users WHERE status = 1;` | 创建视图 |
| `DROP VIEW v;` | `DROP VIEW active_users;` | 删除视图 |

---

## 二、DML（Data Manipulation Language，数据操作语言）

DML 操作的是**表中的数据**。

### 2.1 INSERT

```sql
-- 基本语法
INSERT INTO table_name (col1, col2, ...) VALUES (val1, val2, ...);

-- 插入单行
INSERT INTO users (username, email) VALUES ('张三', 'zhang@example.com');

-- 批量插入
INSERT INTO users (username, email) VALUES
    ('张三', 'zhang@example.com'),
    ('李四', 'li@example.com'),
    ('王五', 'wang@example.com');

-- 从查询结果插入
INSERT INTO archive_users SELECT * FROM users WHERE created_at < '2023-01-01';

-- 插入或替换（如果主键冲突则删除旧行插入新行）
REPLACE INTO config (key, value) VALUES ('version', '2.0');

-- 插入或更新（如果主键冲突则更新指定列）
INSERT INTO stats (date, count) VALUES ('2024-01-01', 1)
ON DUPLICATE KEY UPDATE count = count + 1;
```

### 2.2 UPDATE

```sql
-- 基本语法
UPDATE table_name SET col1 = val1, col2 = val2 WHERE condition;

-- 更新单行
UPDATE users SET email = 'new@example.com' WHERE id = 1;

-- 批量更新
UPDATE products SET price = price * 1.1 WHERE category_id = 5;

-- 多表更新
UPDATE orders o
JOIN users u ON o.user_id = u.id
SET o.status = 5
WHERE u.status = 0;
```

### 2.3 DELETE

```sql
-- 基本语法
DELETE FROM table_name WHERE condition;

-- 删除指定行
DELETE FROM cart_items WHERE user_id = 100 AND product_id = 1;

-- 多表删除
DELETE o, oi
FROM orders o
JOIN order_items oi ON o.id = oi.order_id
WHERE o.created_at < '2020-01-01';

-- 删除 vs TRUNCATE
-- DELETE: 逐行删除，可回滚，触发触发器，慢
-- TRUNCATE: 直接释放数据页，不可回滚，不触发触发器，快
```

---

## 三、DQL（Data Query Language，数据查询语言）

DQL 的核心是 `SELECT` 语句，是 SQL 中使用频率最高的部分。

### 3.1 SELECT 完整语法骨架

```sql
SELECT [DISTINCT] select_list
FROM table_reference
  [JOIN table_reference ON condition]
  [LEFT/RIGHT JOIN table_reference ON condition]
[WHERE condition]
[GROUP BY col_list]
[HAVING aggregate_condition]
[ORDER BY col_list [ASC|DESC]]
[LIMIT offset, count];
```

### 3.2 基本查询

```sql
-- 查询所有列
SELECT * FROM users;

-- 查询指定列
SELECT id, username, email FROM users;

-- 别名
SELECT u.id AS user_id, u.username AS name FROM users u;

-- DISTINCT 去重
SELECT DISTINCT category_id FROM products;

-- 表达式计算
SELECT id, price, price * 0.9 AS discounted_price FROM products;
```

### 3.3 WHERE 条件

```sql
-- 比较运算符: =, !=, <>, >, <, >=, <=
SELECT * FROM products WHERE price > 100;

-- 逻辑运算符: AND, OR, NOT
SELECT * FROM products WHERE price > 100 AND status = 1;

-- BETWEEN
SELECT * FROM products WHERE price BETWEEN 100 AND 500;

-- IN
SELECT * FROM orders WHERE status IN (1, 2, 3);

-- LIKE（% 任意字符，_ 单个字符）
SELECT * FROM users WHERE username LIKE '张%';
SELECT * FROM users WHERE phone LIKE '138________';

-- IS NULL / IS NOT NULL
SELECT * FROM users WHERE email IS NULL;

-- REGEXP（正则表达式）
SELECT * FROM users WHERE email REGEXP '^[a-z]+@gmail\\.com$';
```

### 3.4 JOIN 多表查询

```sql
-- INNER JOIN（取交集）
SELECT u.username, o.order_no
FROM users u
INNER JOIN orders o ON u.id = o.user_id;

-- LEFT JOIN（左表全保留，右表无匹配填 NULL）
SELECT u.username, o.order_no
FROM users u
LEFT JOIN orders o ON u.id = o.user_id;

-- RIGHT JOIN（右表全保留，等价于交换位置后的 LEFT JOIN）
SELECT u.username, o.order_no
FROM users u
RIGHT JOIN orders o ON u.id = o.user_id;

-- CROSS JOIN（笛卡尔积，慎用）
SELECT * FROM colors CROSS JOIN sizes;

-- 自连接（表和自己 JOIN）
SELECT e1.name AS employee, e2.name AS manager
FROM employees e1
LEFT JOIN employees e2 ON e1.manager_id = e2.id;
```

### 3.5 GROUP BY 与聚合函数

```sql
-- 聚合函数: COUNT, SUM, AVG, MAX, MIN
SELECT category_id, COUNT(*) AS cnt, AVG(price) AS avg_price
FROM products
WHERE status = 1
GROUP BY category_id;

-- HAVING（过滤聚合结果，WHERE 不能过滤聚合结果）
SELECT category_id, COUNT(*) AS cnt
FROM products
GROUP BY category_id
HAVING cnt > 10;

-- GROUP BY 多列
SELECT DATE_FORMAT(created_at, '%Y-%m') AS month, status, COUNT(*)
FROM orders
GROUP BY month, status;
```

### 3.6 ORDER BY 与 LIMIT

```sql
-- 排序（ASC 升序默认，DESC 降序）
SELECT * FROM orders ORDER BY created_at DESC;

-- 多列排序
SELECT * FROM orders ORDER BY status ASC, created_at DESC;

-- 分页（跳过 10 条，取 10 条）
SELECT * FROM orders ORDER BY id DESC LIMIT 10, 10;

-- 游标分页（比 LIMIT offset 高效）
SELECT * FROM orders WHERE id > 99990 ORDER BY id LIMIT 10;
```

### 3.7 子查询

```sql
-- 标量子查询（返回单个值）
SELECT * FROM products WHERE price > (SELECT AVG(price) FROM products);

-- 行子查询
SELECT * FROM orders WHERE (user_id, status) = (SELECT id, 1 FROM users LIMIT 1);

-- IN 子查询
SELECT * FROM products WHERE category_id IN (SELECT id FROM categories WHERE name LIKE '%电子%');

-- EXISTS 子查询
SELECT * FROM users u WHERE EXISTS (SELECT 1 FROM orders o WHERE o.user_id = u.id);

-- 相关子查询（子查询引用外部列）
SELECT * FROM products p WHERE price > (SELECT AVG(price) FROM products WHERE category_id = p.category_id);
```

### 3.8 UNION

```sql
-- UNION（合并结果集，去重）
SELECT name FROM users
UNION
SELECT receiver_name FROM orders;

-- UNION ALL（合并结果集，不去重，更快）
SELECT name FROM users
UNION ALL
SELECT receiver_name FROM orders;
```

### 3.9 窗口函数（MySQL 8.0+）

```sql
-- ROW_NUMBER：行号
SELECT id, name, price,
       ROW_NUMBER() OVER (ORDER BY price DESC) AS rank
FROM products;

-- RANK：排名（有间隔）
SELECT id, name, price,
       RANK() OVER (ORDER BY price DESC) AS rank
FROM products;

-- 分区内排名
SELECT id, name, category_id, price,
       ROW_NUMBER() OVER (PARTITION BY category_id ORDER BY price DESC) AS category_rank
FROM products;

-- 累计求和
SELECT DATE_FORMAT(created_at, '%Y-%m') AS month,
       SUM(total_amount) AS monthly_revenue,
       SUM(SUM(total_amount)) OVER (ORDER BY DATE_FORMAT(created_at, '%Y-%m')) AS cumulative_revenue
FROM orders
GROUP BY month;
```

---

## 四、DCL（Data Control Language，数据控制语言）

DCL 管理**数据库的访问权限**。

```sql
-- 创建用户
CREATE USER 'app'@'%' IDENTIFIED BY 'your_password_here';

-- 授予权限
GRANT SELECT, INSERT, UPDATE ON ecommerce.* TO 'app'@'%';

-- 授予所有权限
GRANT ALL PRIVILEGES ON ecommerce.* TO 'app'@'%';

-- 撤销权限
REVOKE INSERT ON ecommerce.* FROM 'app'@'%';

-- 查看用户权限
SHOW GRANTS FOR 'app'@'%';

-- 删除用户
DROP USER 'app'@'%';

-- 刷新权限（修改权限后执行）
FLUSH PRIVILEGES;
```

---

## 五、TCL（Transaction Control Language，事务控制语言）

TCL 管理**事务的开始、提交、回滚**。

```sql
-- 开始事务
START TRANSACTION;
-- 或
BEGIN;

-- 提交事务
COMMIT;

-- 回滚事务
ROLLBACK;

-- 创建保存点
SAVEPOINT sp1;

-- 回滚到保存点
ROLLBACK TO SAVEPOINT sp1;

-- 释放保存点
RELEASE SAVEPOINT sp1;

-- 设置自动提交
SET AUTOCOMMIT = 0;  -- 关闭（每条语句不再自动提交）
SET AUTOCOMMIT = 1;  -- 开启（默认）

-- 查看隔离级别
SELECT @@transaction_isolation;

-- 设置隔离级别
SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED;
SET SESSION TRANSACTION ISOLATION LEVEL REPEATABLE READ;

-- 加锁读
SELECT * FROM products WHERE id = 1 FOR UPDATE;    -- 排他锁
SELECT * FROM products WHERE id = 1 FOR SHARE;      -- 共享锁（MySQL 8.0+）
```

---

## 六、SQL 执行顺序

虽然你写 SQL 的顺序是 `SELECT → FROM → WHERE → GROUP BY → HAVING → ORDER BY → LIMIT`，但 MySQL 实际执行的顺序是：

```
① FROM        -- 确定数据来源（含 JOIN）
② WHERE       -- 过滤行
③ GROUP BY    -- 分组
④ HAVING      -- 过滤分组
⑤ SELECT      -- 选择列（含聚合计算）
⑥ ORDER BY    -- 排序
⑦ LIMIT       -- 限制行数
```

理解这个顺序很重要——比如你无法在 WHERE 中使用 SELECT 中定义的别名，因为 WHERE 在 SELECT 之前执行。但你可以用 HAVING 过滤聚合结果，因为 HAVING 在 GROUP BY 之后。

```sql
-- ❌ 错误：WHERE 中不能使用别名（别名在 SELECT 阶段才定义）
SELECT price * 0.9 AS discounted_price
FROM products
WHERE discounted_price > 100;

-- ✅ 正确：重复表达式或用 HAVING（MySQL 扩展允许 HAVING 用别名）
SELECT price * 0.9 AS discounted_price
FROM products
HAVING discounted_price > 100;
```