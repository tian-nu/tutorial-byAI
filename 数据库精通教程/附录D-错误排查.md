# 附录 D — 常见错误排查指南

> 数据库的错误信息通常很"吝啬"——只给你一个错误码和一行英文。本附录按错误码索引，告诉你每个错误的**真正原因**和**具体解决步骤**。遇到错误时，先搜错误码，再按步骤排查。

---

## 错误码索引

### 1045 — Access denied for user

**错误信息：** `ERROR 1045 (28000): Access denied for user 'root'@'localhost' (using password: YES)`

**原因：** 用户名或密码错误，或该用户无权从当前主机连接。

**排查步骤：**
1. 确认用户名和密码是否正确
2. 确认 `host` 部分是否匹配：`'root'@'localhost'` ≠ `'root'@'%'` ≠ `'root'@'192.168.1.1'`
3. 检查 MySQL 是否在运行：`mysqladmin -u root -p ping`

**解决方案：**
```bash
# 方案 1：确认密码后重试
mysql -u root -p

# 方案 2：跳过权限验证启动（紧急情况，修复后必须恢复）
# 停止 MySQL 服务
sudo systemctl stop mysql
# 跳过权限表启动
sudo mysqld_safe --skip-grant-tables &
# 无密码登录
mysql -u root
# 修改密码
FLUSH PRIVILEGES;
ALTER USER 'root'@'localhost' IDENTIFIED BY 'new_password';
# 正常重启 MySQL
sudo systemctl restart mysql
```

---

### 1062 — Duplicate entry

**错误信息：** `ERROR 1062 (23000): Duplicate entry 'alice' for key 'uk_username'`

**原因：** 试图插入或更新一条违反唯一约束的数据。

**排查步骤：**
1. 确认是哪个唯一键冲突（错误信息中会显示 `uk_username`）
2. 检查数据中是否已有该值

**解决方案：**
```sql
-- 方案 1：先查是否存在
SELECT * FROM users WHERE username = 'alice';

-- 方案 2：用 INSERT ... ON DUPLICATE KEY UPDATE
INSERT INTO users (username, email) VALUES ('alice', 'new@example.com')
ON DUPLICATE KEY UPDATE email = 'new@example.com';

-- 方案 3：用 REPLACE INTO（注意：会删除旧行再插入新行）
REPLACE INTO users (username, email) VALUES ('alice', 'new@example.com');

-- 方案 4：先删除再插入
DELETE FROM users WHERE username = 'alice';
INSERT INTO users (username, email) VALUES ('alice', 'new@example.com');
```

---

### 1054 — Unknown column

**错误信息：** `ERROR 1054 (42S22): Unknown column 'user_name' in 'field list'`

**原因：** SQL 中引用了不存在的列名。

**排查步骤：**
1. 检查列名拼写
2. 确认表结构：`DESC table_name;`
3. 检查是否引用了别名而非原列名（WHERE 中不能使用 SELECT 别名）

**常见错误：**
```sql
-- ❌ 错误：列名拼写错误
SELECT user_name FROM users;  -- 应该是 username

-- ❌ 错误：WHERE 中使用了 SELECT 别名
SELECT id AS user_id FROM users WHERE user_id = 1;  -- 别名在 WHERE 阶段还未定义

-- ❌ 错误：字符串没加引号，被当成列名
SELECT * FROM users WHERE username = alice;  -- 应该是 'alice'
```

---

### 1146 — Table doesn't exist

**错误信息：** `ERROR 1146 (42S02): Table 'ecommerce.orders' doesn't exist`

**原因：** 引用了不存在的表。

**排查步骤：**
1. 确认当前数据库：`SELECT DATABASE();`
2. 确认表名拼写正确：`SHOW TABLES LIKE '%order%';`
3. 检查是否在正确的数据库中

**常见错误：**
```sql
-- ❌ USE 了错误的数据库
USE test;
SELECT * FROM orders;  -- orders 在 ecommerce 库中

-- ✅ 用完整表名
SELECT * FROM ecommerce.orders;
```

---

### 1213 — Deadlock

**错误信息：** `ERROR 1213 (40001): Deadlock found when trying to get lock; try restarting transaction`

**原因：** 两个或多个事务互相等待对方持有的锁，形成死锁。

**排查步骤：**
1. 查看最近一次死锁详情：`SHOW ENGINE INNODB STATUS\G`（搜索 "LATEST DETECTED DEADLOCK"）
2. 查看当前锁等待：`SELECT * FROM performance_schema.data_locks;`
3. 查看当前事务：`SELECT * FROM information_schema.INNODB_TRX;`

**常见死锁场景：**
```sql
-- Session A                   Session B
START TRANSACTION;             START TRANSACTION;
UPDATE t SET c=1 WHERE id=1;   UPDATE t SET c=2 WHERE id=2;
UPDATE t SET c=2 WHERE id=2;   UPDATE t SET c=1 WHERE id=1;
-- 死锁！A 等 B 释放 id=2 的锁，B 等 A 释放 id=1 的锁
```

**解决方案：**
1. **应用层重试**：捕获死锁异常，重新执行事务
2. **统一加锁顺序**：所有事务按相同顺序访问资源（如都先操作 id=1 再操作 id=2）
3. **减小事务粒度**：让事务尽快提交，减少持锁时间
4. **添加合适的索引**：行锁基于索引，全表扫描会导致锁更多行

```python
# 伪代码：应用层死锁重试
import time

def execute_with_retry(cursor, max_retries=3):
    for attempt in range(max_retries):
        try:
            cursor.execute("START TRANSACTION")
            # ... 业务 SQL ...
            cursor.execute("COMMIT")
            return
        except DeadlockError:
            cursor.execute("ROLLBACK")
            if attempt == max_retries - 1:
                raise
            time.sleep(0.1 * (attempt + 1))  # 递增等待
```

---

### 1205 — Lock wait timeout exceeded

**错误信息：** `ERROR 1205 (HY000): Lock wait timeout exceeded; try restarting transaction`

**原因：** 事务等待获取锁的时间超过了 `innodb_lock_wait_timeout`（默认 50 秒）。

**和死锁的区别：**
- 死锁（1213）：两个事务**互相**等对方，InnoDB 主动检测并回滚其中一个
- 锁等待超时（1205）：一个事务在等另一个事务释放锁，InnoDB 不主动干预，等超时

**排查步骤：**
1. 找到持锁的事务：`SELECT * FROM information_schema.INNODB_TRX;`
2. 找到被锁住的事务：`SELECT * FROM performance_schema.data_lock_waits;`
3. 如果持锁事务是"睡眠连接"（忘了提交），KILL 掉：`KILL <trx_mysql_thread_id>;`

**常见原因：**
```sql
-- Session A：开启事务，改了数据，但忘了提交
START TRANSACTION;
UPDATE products SET stock = 50 WHERE id = 1;
-- 然后去开会了，没有 COMMIT

-- Session B：尝试更新同一行，等 50 秒后超时
START TRANSACTION;
UPDATE products SET stock = 40 WHERE id = 1;  -- 等 50 秒 → ERROR 1205
```

**解决方案：**
1. 检查是否有未提交的长事务
2. 调大超时时间（治标不治本）：`SET GLOBAL innodb_lock_wait_timeout = 100;`
3. 根本解决方案：减小事务粒度，尽快提交

---

### 1064 — Syntax error

**错误信息：** `ERROR 1064 (42000): You have an error in your SQL syntax...`

**原因：** SQL 语法错误。

**常见错误：**
```sql
-- ❌ 错误：关键字拼写错误
SLECT * FROM users;        -- 应该是 SELECT
UPDATA users SET ...;      -- 应该是 UPDATE

-- ❌ 错误：缺少引号
INSERT INTO users (name) VALUES (张三);  -- 字符串需要引号

-- ❌ 错误：逗号分隔符多余
SELECT id, name, FROM users;  -- name 后面多了一个逗号

-- ❌ 错误：整数溢出（也报 syntax error）
CREATE TABLE t (id TINYINT);  -- 然后 INSERT 值 > 127
```

---

### 1451 — Cannot delete or update a parent row (外键约束)

**错误信息：** `ERROR 1451 (23000): Cannot delete or update a parent row: a foreign key constraint fails`

**原因：** 试图删除或更新被外键引用的行。

**解决方案：**
```sql
-- 方案 1：先删除子表记录
DELETE FROM orders WHERE user_id = 1;
DELETE FROM users WHERE id = 1;

-- 方案 2：建表时使用 ON DELETE CASCADE（自动级联删除）
CREATE TABLE orders (
    ...
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 方案 3：临时禁用外键检查（谨慎！）
SET FOREIGN_KEY_CHECKS = 0;
DELETE FROM users WHERE id = 1;
SET FOREIGN_KEY_CHECKS = 1;
```

---

### 1452 — Cannot add or update a child row (外键约束)

**错误信息：** `ERROR 1452 (23000): Cannot add or update a child row: a foreign key constraint fails`

**原因：** 试图插入的子表记录引用了不存在的父表记录。

**解决方案：**
```sql
-- 先确认父表记录存在
SELECT * FROM users WHERE id = 999;

-- 如果不存在，先插入父表记录
INSERT INTO users (id, username) VALUES (999, 'new_user');
-- 再插入子表记录
INSERT INTO orders (user_id, ...) VALUES (999, ...);
```

---

### 1364 — Field doesn't have a default value

**错误信息：** `ERROR 1364 (HY000): Field 'name' doesn't have a default value`

**原因：** 插入时未给 NOT NULL 且无 DEFAULT 值的列提供值。

**解决方案：**
```sql
-- 方案 1：插入时提供值
INSERT INTO users (name, email) VALUES ('张三', 'zhang@example.com');

-- 方案 2：修改列定义，添加默认值
ALTER TABLE users MODIFY name VARCHAR(50) NOT NULL DEFAULT '';

-- 方案 3：修改 SQL_MODE（不推荐，会隐藏问题）
SET sql_mode = '';  -- 去掉 STRICT_TRANS_TABLES
```

---

### 2013 — Lost connection to MySQL server

**错误信息：** `ERROR 2013 (HY000): Lost connection to MySQL server during query`

**原因：** 查询执行期间连接断开。

**常见原因：**
1. 查询超时（`net_read_timeout` / `net_write_timeout`）
2. 结果集太大（超过 `max_allowed_packet`）
3. MySQL 服务器重启

**解决方案：**
```sql
-- 查看当前超时设置
SHOW VARIABLES LIKE '%timeout%';

-- 调大超时时间
SET GLOBAL net_read_timeout = 60;
SET GLOBAL net_write_timeout = 60;

-- 调大最大数据包
SET GLOBAL max_allowed_packet = 256 * 1024 * 1024;  -- 256MB
```

---

### 2006 — MySQL server has gone away

**错误信息：** `ERROR 2006 (HY000): MySQL server has gone away`

**原因：** 连接已断开，无法执行查询。

**常见原因：**
1. 连接空闲超时（`wait_timeout` 默认 8 小时）
2. 发送的数据包过大
3. 服务器重启

**解决方案：**
```bash
# 重新连接
mysql -u root -p

# 或调大超时时间
SET GLOBAL wait_timeout = 28800;  -- 8 小时
SET GLOBAL interactive_timeout = 28800;

# 在应用层使用连接池 + 连接健康检查
```

---

### 1175 — Safe update mode

**错误信息：** `ERROR 1175 (HY000): You are using safe update mode and you tried to update a table without a WHERE that uses a KEY column`

**原因：** 开启了安全更新模式（`sql_safe_updates = 1`），UPDATE/DELETE 必须使用带索引的 WHERE 条件。

**解决方案：**
```sql
-- 方案 1：加索引条件
UPDATE users SET status = 0 WHERE id = 100;  -- id 是主键 ✓

-- 方案 2：临时关闭安全模式
SET sql_safe_updates = 0;
UPDATE users SET status = 0 WHERE status = 1;
SET sql_safe_updates = 1;
```

---

### 1709 — Index column size too large

**错误信息：** `ERROR 1709 (HY000): Index column size too large. The maximum column size is 767 bytes.`

**原因：** 索引列的总大小超过了限制（InnoDB 默认 767 字节，utf8mb4 下 VARCHAR(191) 已达上限）。

**解决方案：**
```sql
-- 方案 1：减小索引列长度
CREATE INDEX idx_name ON articles (title(100));  -- 只索引前 100 个字符

-- 方案 2：启用 innodb_large_prefix（MySQL 5.7）
SET GLOBAL innodb_large_prefix = ON;
SET GLOBAL innodb_file_format = Barracuda;

-- 方案 3：升级到 MySQL 8.0（默认支持 3072 字节）
```

---

## 快速排查流程

当你遇到一个数据库错误时，按以下顺序排查：

```
1. 读错误信息 → 提取错误码和关键描述
2. 查本附录 → 找到对应错误码 → 按步骤排查
3. 如果不在本附录 → 查官方文档：
   https://dev.mysql.com/doc/refman/8.0/en/error-handling.html
4. 如果还是不行 → 检查 MySQL 错误日志：
   SHOW VARIABLES LIKE 'log_error';
   tail -f /var/log/mysql/error.log
```