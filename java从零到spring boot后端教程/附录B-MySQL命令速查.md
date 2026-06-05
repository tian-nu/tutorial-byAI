# 附录B · MySQL常用命令速查

> "MySQL命令千千万，但日常工作中真正高频使用的就那几十条。本附录按使用场景分类，是你日常操作数据库时的快速参考手册。"

---

## B.1 连接与基本信息

```bash
mysql -u root -p
mysql -u root -p -h 127.0.0.1 -P 3306
mysql -u root -p database_name
```

```sql
SHOW DATABASES;
USE database_name;
SELECT DATABASE();
SHOW TABLES;
DESC table_name;
SHOW CREATE TABLE table_name;
SHOW COLUMNS FROM table_name;
SHOW INDEX FROM table_name;
SHOW TABLE STATUS;
SELECT VERSION();
SHOW STATUS;
SHOW VARIABLES;
SHOW VARIABLES LIKE 'character%';
SHOW PROCESSLIST;
SHOW ENGINES;
```

---

## B.2 数据库操作

```sql
CREATE DATABASE db_name
    DEFAULT CHARACTER SET utf8mb4
    DEFAULT COLLATE utf8mb4_unicode_ci;

DROP DATABASE db_name;
ALTER DATABASE db_name CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

---

## B.3 表操作

### 创建表

```sql
CREATE TABLE users (
    id         BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    name       VARCHAR(100)    NOT NULL,
    email      VARCHAR(255)    NOT NULL,
    age        TINYINT UNSIGNED NOT NULL DEFAULT 0,
    bio        TEXT,
    salary     DECIMAL(10,2),
    is_active  TINYINT NOT NULL DEFAULT 1,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE INDEX idx_email (email),
    INDEX idx_name (name),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

### 修改表

```sql
DROP TABLE IF EXISTS users;
TRUNCATE TABLE users;

ALTER TABLE users ADD COLUMN phone VARCHAR(20) AFTER email;
ALTER TABLE users DROP COLUMN phone;
ALTER TABLE users MODIFY COLUMN name VARCHAR(200) NOT NULL;
ALTER TABLE users CHANGE COLUMN name username VARCHAR(100) NOT NULL;
ALTER TABLE users ADD INDEX idx_age (age);
ALTER TABLE users DROP INDEX idx_age;
ALTER TABLE users RENAME TO customers;
```

---

## B.4 查询（SELECT）

### 基础查询

```sql
SELECT * FROM users;
SELECT id, name, email FROM users;
SELECT DISTINCT city FROM users;
```

### 条件查询

```sql
SELECT * FROM users WHERE id = 1;
SELECT * FROM users WHERE age > 18 AND is_active = 1;
SELECT * FROM users WHERE name LIKE '%张%';
SELECT * FROM users WHERE email IS NULL;
SELECT * FROM users WHERE age BETWEEN 18 AND 30;
SELECT * FROM users WHERE id IN (1, 2, 3);
```

### 排序与分页

```sql
SELECT * FROM users ORDER BY created_at DESC;
SELECT * FROM users ORDER BY age ASC, name DESC;

SELECT * FROM users LIMIT 10;
SELECT * FROM users LIMIT 10 OFFSET 20;
```

### 聚合查询

```sql
SELECT COUNT(*) FROM users;
SELECT COUNT(*) AS total,
       AVG(age) AS avg_age,
       MAX(age) AS max_age,
       MIN(age) AS min_age,
       SUM(salary) AS total_salary
FROM users;
```

### 分组

```sql
SELECT city, COUNT(*) AS cnt FROM users
    GROUP BY city
    HAVING cnt > 5
    ORDER BY cnt DESC;
```

### 多表连接

```sql
SELECT u.name, o.order_no FROM users u
    INNER JOIN orders o ON u.id = o.user_id;

SELECT u.name, o.order_no FROM users u
    LEFT JOIN orders o ON u.id = o.user_id;

SELECT u1.name AS user1, u2.name AS user2 FROM users u1
    JOIN users u2 ON u1.manager_id = u2.id;
```

### 子查询

```sql
SELECT * FROM users WHERE id = (
    SELECT user_id FROM orders WHERE amount > 1000 LIMIT 1
);

SELECT * FROM users WHERE id IN (
    SELECT user_id FROM orders WHERE amount > 1000
);

SELECT * FROM (
    SELECT * FROM users WHERE age > 18
) AS adult_users WHERE city = '北京';
```

### 联合查询

```sql
SELECT * FROM orders WHERE user_id = 1
UNION
SELECT * FROM orders WHERE user_id = 2;

SELECT * FROM orders WHERE user_id = 1
UNION ALL
SELECT * FROM orders WHERE user_id = 1;
```

### 条件表达式

```sql
SELECT IFNULL(nickname, '匿名') AS display_name FROM users;
SELECT COALESCE(phone, email, '无联系方式') FROM users;

SELECT
    CASE
        WHEN age < 18 THEN '未成年'
        WHEN age < 60 THEN '成年'
        ELSE '老年'
    END AS age_group
FROM users;
```

---

## B.5 插入、更新、删除

```sql
INSERT INTO users (name, email, age) VALUES ('张三', 'zhang@test.com', 25);
INSERT INTO users (name, email, age) VALUES
    ('张三', 'zhang@test.com', 25),
    ('李四', 'li@test.com', 30);
INSERT INTO users SET name='张三', email='zhang@test.com';
INSERT INTO users (name, email) SELECT name, email FROM temp_users;

UPDATE users SET age = 26, updated_at = NOW() WHERE id = 1;
UPDATE users SET age = age + 1 WHERE city = '北京';
UPDATE orders o JOIN users u ON o.user_id = u.id
    SET o.status = 'VIP' WHERE u.level > 5;

DELETE FROM users WHERE id = 1;
DELETE FROM users WHERE created_at < '2020-01-01' LIMIT 1000;
```

---

## B.6 索引

```sql
CREATE INDEX idx_name ON users(name);
CREATE UNIQUE INDEX idx_email ON users(email);
CREATE INDEX idx_name_age ON users(name, age);
CREATE FULLTEXT INDEX idx_content ON articles(title, content);
ALTER TABLE users ADD INDEX idx_created (created_at);
ALTER TABLE users DROP INDEX idx_name;

SHOW INDEX FROM users;
EXPLAIN SELECT * FROM users WHERE email = 'test@test.com';
EXPLAIN FORMAT=JSON SELECT * FROM users WHERE name LIKE '%张%';
EXPLAIN ANALYZE SELECT * FROM users WHERE age > 18;
```

EXPLAIN结果关键字段：
- `type`：连接类型。`ALL`（全表扫描）→ 糟了；`index` → 还行；`ref` → 好；`const` → 完美
- `key`：实际使用的索引，NULL意味着没用到索引
- `rows`：预估扫描行数，越小越好
- `Extra`：`Using filesort` → 需要优化；`Using index` → 覆盖索引，最优

---

## B.7 事务

```sql
START TRANSACTION;
UPDATE accounts SET balance = balance - 100 WHERE id = 1;
UPDATE accounts SET balance = balance + 100 WHERE id = 2;
COMMIT;

START TRANSACTION;
UPDATE accounts SET balance = balance - 100 WHERE id = 1;
ROLLBACK;

SET autocommit = 0;
SET autocommit = 1;

SHOW ENGINE INNODB STATUS;
```

事务四大特性ACID：
- **A**tomicity：原子性——要么全做，要么全不做
- **C**onsistency：一致性——事务前后数据完整
- **I**solation：隔离性——并发事务互不干扰
- **D**urability：持久性——提交后永久保存

---

## B.8 用户与权限

```sql
CREATE USER 'username'@'localhost' IDENTIFIED BY 'password';
CREATE USER 'username'@'%' IDENTIFIED BY 'password';

GRANT ALL PRIVILEGES ON database_name.* TO 'username'@'localhost';
GRANT SELECT, INSERT, UPDATE ON database_name.* TO 'username'@'localhost';
GRANT ALL PRIVILEGES ON *.* TO 'username'@'localhost' WITH GRANT OPTION;

REVOKE DELETE ON database_name.* FROM 'username'@'localhost';
REVOKE ALL PRIVILEGES ON *.* FROM 'username'@'localhost';

DROP USER 'username'@'localhost';

SHOW GRANTS FOR 'username'@'localhost';
SELECT User, Host FROM mysql.user;

FLUSH PRIVILEGES;
ALTER USER 'root'@'localhost' IDENTIFIED BY 'new_password';
```

---

## B.9 备份与恢复

```bash
mysqldump -u root -p database_name > backup.sql
mysqldump -u root -p database_name table1 table2 > backup.sql
mysqldump -u root -p --all-databases > all_backup.sql
mysqldump -u root -p --no-data database_name > schema_only.sql
mysqldump -u root -p --no-create-info database_name > data_only.sql

mysql -u root -p database_name < backup.sql
mysql -u root -p < all_backup.sql
```

---

## B.10 常用函数速览

| 分类 | 函数 | 说明 |
|------|------|------|
| 字符串 | `CONCAT(a, b)` | 拼接 |
| 字符串 | `SUBSTRING(s, start, len)` | 截取 |
| 字符串 | `LENGTH(s)` | 字节长度 |
| 字符串 | `CHAR_LENGTH(s)` | 字符长度 |
| 字符串 | `UPPER(s)` / `LOWER(s)` | 大小写 |
| 字符串 | `TRIM(s)` | 去空格 |
| 字符串 | `REPLACE(s, old, new)` | 替换 |
| 字符串 | `LEFT(s, n)` / `RIGHT(s, n)` | 从左/右截取n个字符 |
| 数值 | `ROUND(x, d)` | 四舍五入 |
| 数值 | `CEIL(x)` / `FLOOR(x)` | 向上/向下取整 |
| 数值 | `ABS(x)` | 绝对值 |
| 数值 | `MOD(x, y)` | 取余 |
| 数值 | `RAND()` | 随机数[0,1) |
| 日期 | `NOW()` / `CURRENT_TIMESTAMP` | 当前时间 |
| 日期 | `DATE_FORMAT(d, fmt)` | 日期格式化 |
| 日期 | `DATEDIFF(d1, d2)` | 日期间隔天数 |
| 日期 | `DATE_ADD(d, INTERVAL n unit)` | 日期加法 |
| 日期 | `YEAR(d)` / `MONTH(d)` / `DAY(d)` | 取年/月/日 |
| 条件 | `IF(cond, a, b)` | 三元运算 |
| 条件 | `IFNULL(x, default)` | NULL替换 |
| 条件 | `COALESCE(a, b, c)` | 返回第一个非NULL |

---

本附录覆盖了后端开发中80%的MySQL操作场景。建议收藏，遇到不确定的语法时随时翻阅。

---

[← 上一章：附录A-Java标准库速查.md](附录A-Java标准库速查.md) | [下一章：附录C-Redis命令速查.md →](附录C-Redis命令速查.md)