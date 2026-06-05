# 附录 A — MySQL 常用命令速查

> 本附录汇总了 MySQL 日常开发和管理中最常用的命令。按"搜到什么就能解决什么问题"组织，每个命令给出用途和示例。不追求全面，追求实用。

---

## 一、服务器管理

| 命令 | 用途 | 示例 |
|------|------|------|
| `mysql -u root -p` | 登录 MySQL | `mysql -u root -p` |
| `mysql -h 192.168.1.1 -P 3306 -u root -p` | 远程登录 | `mysql -h 192.168.1.1 -P 3306 -u root -p` |
| `SHOW PROCESSLIST;` | 查看当前连接 | `SHOW PROCESSLIST;` |
| `SHOW FULL PROCESSLIST;` | 查看完整 SQL（不截断） | `SHOW FULL PROCESSLIST;` |
| `KILL 123;` | 杀掉连接 ID 为 123 的连接 | `KILL 123;` |
| `SHOW STATUS;` | 查看服务器状态变量 | `SHOW STATUS LIKE '%Threads%';` |
| `SHOW VARIABLES;` | 查看服务器配置变量 | `SHOW VARIABLES LIKE '%buffer_pool%';` |
| `SHOW ENGINES;` | 查看支持的存储引擎 | `SHOW ENGINES;` |
| `SHOW MASTER STATUS;` | 查看主库 binlog 位置 | `SHOW MASTER STATUS;` |
| `SHOW SLAVE STATUS\G` | 查看从库复制状态 | `SHOW SLAVE STATUS\G` |
| `FLUSH LOGS;` | 刷新日志（切割 binlog） | `FLUSH LOGS;` |
| `SET GLOBAL slow_query_log = ON;` | 开启慢查询日志 | `SET GLOBAL slow_query_log = ON;` |
| `SET GLOBAL long_query_time = 0.5;` | 设置慢查询阈值（秒） | `SET GLOBAL long_query_time = 0.5;` |
| `SELECT @@datadir;` | 查看数据目录路径 | `SELECT @@datadir;` |
| `SELECT VERSION();` | 查看 MySQL 版本 | `SELECT VERSION();` |

---

## 二、用户与权限管理

| 命令 | 用途 | 示例 |
|------|------|------|
| `CREATE USER 'user'@'host' IDENTIFIED BY 'password';` | 创建用户 | `CREATE USER 'app'@'%' IDENTIFIED BY 'your_password_here';` |
| `DROP USER 'user'@'host';` | 删除用户 | `DROP USER 'app'@'%';` |
| `ALTER USER 'user'@'host' IDENTIFIED BY 'new_password';` | 修改密码 | `ALTER USER 'root'@'localhost' IDENTIFIED BY 'new_password';` |
| `GRANT ALL ON db.* TO 'user'@'host';` | 授予某库所有权限 | `GRANT ALL ON ecommerce.* TO 'app'@'%';` |
| `GRANT SELECT, INSERT, UPDATE ON db.* TO 'user'@'host';` | 授予特定权限 | `GRANT SELECT, INSERT, UPDATE ON ecommerce.* TO 'app'@'%';` |
| `REVOKE ALL ON db.* FROM 'user'@'host';` | 撤销权限 | `REVOKE ALL ON ecommerce.* FROM 'app'@'%';` |
| `SHOW GRANTS FOR 'user'@'host';` | 查看用户权限 | `SHOW GRANTS FOR 'app'@'%';` |
| `FLUSH PRIVILEGES;` | 刷新权限表 | `FLUSH PRIVILEGES;` |
| `SELECT user, host FROM mysql.user;` | 查看所有用户 | `SELECT user, host FROM mysql.user;` |

---

## 三、库操作

| 命令 | 用途 | 示例 |
|------|------|------|
| `SHOW DATABASES;` | 列出所有数据库 | `SHOW DATABASES;` |
| `CREATE DATABASE db_name;` | 创建数据库 | `CREATE DATABASE ecommerce DEFAULT CHARSET utf8mb4;` |
| `DROP DATABASE db_name;` | 删除数据库（危险！） | `DROP DATABASE test_db;` |
| `USE db_name;` | 切换数据库 | `USE ecommerce;` |
| `SELECT DATABASE();` | 查看当前数据库 | `SELECT DATABASE();` |
| `ALTER DATABASE db_name DEFAULT CHARSET utf8mb4;` | 修改数据库字符集 | `ALTER DATABASE ecommerce DEFAULT CHARSET utf8mb4;` |
| `SHOW CREATE DATABASE db_name;` | 查看建库语句 | `SHOW CREATE DATABASE ecommerce;` |

---

## 四、表操作

| 命令 | 用途 | 示例 |
|------|------|------|
| `SHOW TABLES;` | 列出当前库所有表 | `SHOW TABLES;` |
| `SHOW TABLES LIKE '%user%';` | 模糊查找表 | `SHOW TABLES LIKE '%order%';` |
| `DESC table_name;` | 查看表结构 | `DESC orders;` |
| `SHOW CREATE TABLE table_name;` | 查看建表语句 | `SHOW CREATE TABLE orders\G` |
| `SHOW TABLE STATUS;` | 查看表状态（引擎、行数等） | `SHOW TABLE STATUS LIKE 'orders';` |
| `ALTER TABLE t ADD COLUMN col INT;` | 添加列 | `ALTER TABLE orders ADD COLUMN remark VARCHAR(255);` |
| `ALTER TABLE t MODIFY col VARCHAR(100);` | 修改列定义 | `ALTER TABLE orders MODIFY remark TEXT;` |
| `ALTER TABLE t CHANGE old new VARCHAR(100);` | 重命名列 | `ALTER TABLE orders CHANGE remark notes TEXT;` |
| `ALTER TABLE t DROP COLUMN col;` | 删除列 | `ALTER TABLE orders DROP COLUMN notes;` |
| `ALTER TABLE t ADD INDEX idx_name (col);` | 添加索引 | `ALTER TABLE orders ADD INDEX idx_status (status);` |
| `ALTER TABLE t DROP INDEX idx_name;` | 删除索引 | `ALTER TABLE orders DROP INDEX idx_status;` |
| `ALTER TABLE t ADD PRIMARY KEY (col);` | 添加主键 | `ALTER TABLE temp ADD PRIMARY KEY (id);` |
| `ALTER TABLE t ADD FOREIGN KEY (col) REFERENCES t2(col);` | 添加外键 | `ALTER TABLE orders ADD FOREIGN KEY (user_id) REFERENCES users(id);` |
| `RENAME TABLE old TO new;` | 重命名表 | `RENAME TABLE orders TO orders_archive;` |
| `DROP TABLE table_name;` | 删除表（危险！） | `DROP TABLE temp;` |
| `TRUNCATE TABLE table_name;` | 清空表（不可回滚） | `TRUNCATE TABLE temp;` |
| `OPTIMIZE TABLE table_name;` | 优化表（整理碎片） | `OPTIMIZE TABLE orders;` |
| `ANALYZE TABLE table_name;` | 分析表（更新索引统计） | `ANALYZE TABLE orders;` |

---

## 五、数据操作

| 命令 | 用途 | 示例 |
|------|------|------|
| `SELECT * FROM t WHERE ...;` | 查询数据 | `SELECT * FROM orders WHERE user_id = 100;` |
| `INSERT INTO t (col1, col2) VALUES (v1, v2);` | 插入单行 | `INSERT INTO users (name, email) VALUES ('张三', 'zhang@example.com');` |
| `INSERT INTO t (...) VALUES (...), (...), (...);` | 批量插入 | `INSERT INTO users (name, email) VALUES ('A','a@x.com'), ('B','b@x.com');` |
| `INSERT INTO t SELECT ... FROM t2;` | 从查询结果插入 | `INSERT INTO archive SELECT * FROM orders WHERE created_at < '2020-01-01';` |
| `UPDATE t SET col = val WHERE ...;` | 更新数据 | `UPDATE products SET price = 199 WHERE id = 1;` |
| `DELETE FROM t WHERE ...;` | 删除数据 | `DELETE FROM cart_items WHERE user_id = 100;` |
| `REPLACE INTO t (...) VALUES (...);` | 插入或替换 | `REPLACE INTO config (key, value) VALUES ('version', '2.0');` |
| `INSERT ... ON DUPLICATE KEY UPDATE ...;` | 插入或更新 | `INSERT INTO stats (date, count) VALUES ('2024-01-01', 1) ON DUPLICATE KEY UPDATE count = count + 1;` |
| `SELECT SQL_CALC_FOUND_ROWS * FROM t LIMIT 10;` | 查询并计算总数 | `SELECT SQL_CALC_FOUND_ROWS * FROM orders LIMIT 10; SELECT FOUND_ROWS();` |

---

## 六、索引

| 命令 | 用途 | 示例 |
|------|------|------|
| `SHOW INDEX FROM table_name;` | 查看表的索引 | `SHOW INDEX FROM orders;` |
| `CREATE INDEX idx_name ON t (col);` | 创建普通索引 | `CREATE INDEX idx_status ON orders (status);` |
| `CREATE UNIQUE INDEX idx_name ON t (col);` | 创建唯一索引 | `CREATE UNIQUE INDEX uk_email ON users (email);` |
| `CREATE INDEX idx_name ON t (col1, col2);` | 创建联合索引 | `CREATE INDEX idx_user_status ON orders (user_id, status);` |
| `CREATE FULLTEXT INDEX idx_name ON t (col);` | 创建全文索引 | `CREATE FULLTEXT INDEX ft_content ON articles (content) WITH PARSER ngram;` |
| `DROP INDEX idx_name ON table_name;` | 删除索引 | `DROP INDEX idx_status ON orders;` |
| `SELECT * FROM sys.schema_unused_indexes;` | 查看未使用的索引 | `SELECT * FROM sys.schema_unused_indexes WHERE object_schema = 'ecommerce';` |
| `SELECT * FROM sys.schema_redundant_indexes;` | 查看冗余索引 | `SELECT * FROM sys.schema_redundant_indexes WHERE table_schema = 'ecommerce';` |

---

## 七、查询分析

| 命令 | 用途 | 示例 |
|------|------|------|
| `EXPLAIN SELECT ...;` | 查看执行计划 | `EXPLAIN SELECT * FROM orders WHERE user_id = 100;` |
| `EXPLAIN FORMAT=JSON SELECT ...;` | JSON 格式执行计划 | `EXPLAIN FORMAT=JSON SELECT * FROM orders WHERE user_id = 100;` |
| `EXPLAIN ANALYZE SELECT ...;` | 实际执行并分析（MySQL 8.0.18+） | `EXPLAIN ANALYZE SELECT * FROM orders WHERE user_id = 100;` |
| `SHOW PROFILE;` | 查看查询各阶段耗时 | `SET profiling = 1; SELECT ...; SHOW PROFILE;` |
| `SHOW PROFILE CPU FOR QUERY 1;` | 查看特定查询的 CPU 耗时 | `SHOW PROFILE CPU FOR QUERY 1;` |

---

## 八、事务与锁

| 命令 | 用途 | 示例 |
|------|------|------|
| `START TRANSACTION;` | 开始事务 | `START TRANSACTION;` |
| `BEGIN;` | 开始事务（简写） | `BEGIN;` |
| `COMMIT;` | 提交事务 | `COMMIT;` |
| `ROLLBACK;` | 回滚事务 | `ROLLBACK;` |
| `SAVEPOINT sp1;` | 创建保存点 | `SAVEPOINT sp1;` |
| `ROLLBACK TO SAVEPOINT sp1;` | 回滚到保存点 | `ROLLBACK TO SAVEPOINT sp1;` |
| `SET AUTOCOMMIT = 0;` | 关闭自动提交 | `SET AUTOCOMMIT = 0;` |
| `SELECT @@tx_isolation;` | 查看事务隔离级别 | `SELECT @@transaction_isolation;` |
| `SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED;` | 设置隔离级别 | `SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED;` |
| `SELECT ... FOR UPDATE;` | 加排他锁 | `SELECT * FROM products WHERE id = 1 FOR UPDATE;` |
| `SELECT ... LOCK IN SHARE MODE;` | 加共享锁（MySQL 8.0 用 `FOR SHARE`） | `SELECT * FROM products WHERE id = 1 FOR SHARE;` |
| `SHOW ENGINE INNODB STATUS\G` | 查看 InnoDB 状态（含死锁信息） | `SHOW ENGINE INNODB STATUS\G` |
| `SELECT * FROM information_schema.INNODB_TRX;` | 查看当前事务 | `SELECT * FROM information_schema.INNODB_TRX;` |
| `SELECT * FROM information_schema.INNODB_LOCKS;` | 查看当前锁（MySQL 8.0 用 `performance_schema.data_locks`） | `SELECT * FROM performance_schema.data_locks;` |

---

## 九、备份与恢复

| 命令 | 用途 | 示例 |
|------|------|------|
| `mysqldump -u root -p db > backup.sql` | 备份单个数据库 | `mysqldump -u root -p ecommerce > ecommerce_backup.sql` |
| `mysqldump -u root -p db table > backup.sql` | 备份单个表 | `mysqldump -u root -p ecommerce orders > orders_backup.sql` |
| `mysqldump -u root -p --all-databases > all.sql` | 备份所有数据库 | `mysqldump -u root -p --all-databases > all_backup.sql` |
| `mysqldump -u root -p --no-data db > schema.sql` | 只备份结构 | `mysqldump -u root -p --no-data ecommerce > schema.sql` |
| `mysqldump -u root -p --no-create-info db > data.sql` | 只备份数据 | `mysqldump -u root -p --no-create-info ecommerce > data.sql` |
| `mysqldump -u root -p --where="id>1000" db t > subset.sql` | 备份部分数据 | `mysqldump -u root -p --where="created_at>'2024-01-01'" ecommerce orders > recent.sql` |
| `mysql -u root -p db < backup.sql` | 恢复数据库 | `mysql -u root -p ecommerce < ecommerce_backup.sql` |
| `mysqlbinlog binlog.000001` | 查看 binlog 内容 | `mysqlbinlog binlog.000001` |
| `mysqlbinlog --start-datetime="2024-01-01 00:00:00" binlog.000001 \| mysql -u root -p` | 按时间点恢复 | `mysqlbinlog --start-datetime="2024-06-01 08:00:00" binlog.000001 \| mysql -u root -p` |

---

## 十、性能监控

| 命令 | 用途 | 示例 |
|------|------|------|
| `SHOW GLOBAL STATUS LIKE 'Questions';` | 总查询数 | `SHOW GLOBAL STATUS LIKE 'Questions';` |
| `SHOW GLOBAL STATUS LIKE 'Com_select';` | SELECT 次数 | `SHOW GLOBAL STATUS LIKE 'Com_%';` |
| `SHOW GLOBAL STATUS LIKE 'Threads_connected';` | 当前连接数 | `SHOW GLOBAL STATUS LIKE 'Threads_%';` |
| `SHOW GLOBAL STATUS LIKE 'Innodb_rows_read';` | InnoDB 行读取数 | `SHOW GLOBAL STATUS LIKE 'Innodb_rows_%';` |
| `SHOW GLOBAL STATUS LIKE 'Innodb_buffer_pool_read_requests';` | Buffer Pool 读请求 | `SHOW GLOBAL STATUS LIKE 'Innodb_buffer_pool_%';` |
| `SELECT * FROM sys.host_summary;` | 按主机统计 | `SELECT * FROM sys.host_summary;` |
| `SELECT * FROM sys.statement_analysis LIMIT 10;` | 最耗资源的 SQL | `SELECT * FROM sys.statement_analysis LIMIT 10;` |
| `SELECT * FROM sys.io_global_by_file_by_bytes;` | IO 最多的文件 | `SELECT * FROM sys.io_global_by_file_by_bytes;` |

---

## 十一、常用系统变量速查

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `max_connections` | 151 | 最大连接数 |
| `innodb_buffer_pool_size` | 128M | Buffer Pool 大小（建议设为物理内存 60-80%） |
| `innodb_log_file_size` | 48M | redo log 文件大小 |
| `innodb_flush_log_at_trx_commit` | 1 | 事务日志刷新策略（1=最安全 2=性能好） |
| `sync_binlog` | 1 | binlog 同步策略 |
| `long_query_time` | 10 | 慢查询阈值（秒） |
| `max_allowed_packet` | 64M | 最大数据包大小 |
| `wait_timeout` | 28800 | 非交互连接超时（秒） |
| `innodb_lock_wait_timeout` | 50 | 行锁等待超时（秒） |
| `character_set_server` | utf8mb4 | 服务器字符集 |
| `collation_server` | utf8mb4_0900_ai_ci | 服务器排序规则 |