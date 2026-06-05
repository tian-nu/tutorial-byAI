# 20 — SQL 优化场景大全

> - 对应文档版本：database_mastery_outline.md v1, database_mastery_detailed_outline.md v2
> - 适用环境：MySQL 8.0+，已创建 my_shop 数据库
> - 读者角色：已学完第 19 章索引实战的开发者
> - 预计耗时：新手 75 分钟 / 熟手 40 分钟
> - 前置教程：第 04-19 章，尤其是第 17 章（B+树）、第 18 章（EXPLAIN）、第 19 章（索引实战）
> - 可视化：无

---

## 我在做什么？

前三章你学了原理、工具、实战。现在我们把所有知识串起来，用真实场景来练手。这一章不讲新概念，而是**用 EXPLAIN 验证每一个优化策略**，让你看到 Before/After 的量化差异。

学完这一章，你能针对常见的 SQL 性能问题（深分页、JOIN 慢、COUNT 慢、排序慢、批量操作慢），给出可量化的优化方案。

---

## 一、分页优化

### 1.1 深分页问题（回顾第 08 章）

```sql
-- 深分页：跳过 100000 行取 10 行
SELECT * FROM users ORDER BY id LIMIT 100000, 10;
```

这为什么慢？MySQL 需要：
1. 从第一行开始扫描，数到第 100000 行
2. 扔掉前 100000 行
3. 取接下来的 10 行

虽然走了主键索引（type: index），但 **rows 是 100010**，实际大量无效扫描。

```sql
EXPLAIN SELECT * FROM users ORDER BY id LIMIT 100000, 10;
-- type: index, rows: 100010
```

### 1.2 游标分页（推荐）

游标分页（Cursor Pagination）*此术语见附录E* 用上一页的最后一个 ID 作为起点：

```sql
-- ❌ 传统深分页
SELECT * FROM users ORDER BY id LIMIT 100000, 10;

-- ✅ 游标分页：记住上一页最后一条的 id
SELECT * FROM users WHERE id > 99990 ORDER BY id LIMIT 10;
```

EXPLAIN 对比：

```sql
-- 传统分页
EXPLAIN SELECT * FROM users ORDER BY id LIMIT 100000, 10;
-- type: index, rows: 100010

-- 游标分页
EXPLAIN SELECT * FROM users WHERE id > 99990 ORDER BY id LIMIT 10;
-- type: range, rows: 10  ← 只扫描 10 行！
```

**游标分页的局限**：
- 只能"上一页/下一页"，不能跳页
- 要求排序键唯一且有序（通常用自增主键）
- 不适合"第 N 页"的 UI 场景

### 1.3 延迟关联

延迟关联（Deferred Join）*此术语见附录E*：先查主键，再回表取完整数据。

```sql
-- ❌ 深分页：直接查所有列
SELECT * FROM users ORDER BY created_at LIMIT 100000, 10;

-- ✅ 延迟关联：先查主键，再关联
SELECT u.* FROM users u
INNER JOIN (
    SELECT id FROM users ORDER BY created_at LIMIT 100000, 10
) AS t ON u.id = t.id;
```

为什么快？子查询只查 `id` 列，可能走覆盖索引，不需要回表。外层再通过主键 ID 取完整行，主键查找极快。

---

## 二、JOIN 优化

### 2.1 小表驱动大表

核心原则：**让数据量小的表做驱动表（外层循环），数据量大的表做被驱动表（内层循环），且被驱动表的 JOIN 列必须有索引。**

```sql
-- 假设 users 有 1000 行，orders 有 100000 行

-- ✅ 正确：小表（users）驱动大表（orders）
SELECT * FROM users u
INNER JOIN orders o ON u.id = o.user_id;
-- 对 users 的每一行，在 orders 的 user_id 索引中查找对应订单

-- 效果：1000 次索引查找，每次 ~3 次 IO
-- 总共约 3000 次 IO
```

### 2.2 JOIN 字段加索引

```sql
-- 假设 orders.user_id 没有索引

-- ❌ 没有索引
EXPLAIN SELECT * FROM users u
INNER JOIN orders o ON u.id = o.user_id;
-- orders 表：type: ALL, rows: 100000  ← 对每个 user 都要全表扫描 orders！

-- ✅ 加上索引
CREATE INDEX idx_user_id ON orders(user_id);

EXPLAIN SELECT * FROM users u
INNER JOIN orders o ON u.id = o.user_id;
-- orders 表：type: ref, rows: 10  ← 只扫描该用户的订单
```

**EXPLAIN 对比**：

| 场景 | users (驱动表) | orders (被驱动表) |
|------|---------------|-------------------|
| 无索引 | type: ALL, rows: 1000 | type: ALL, rows: 100000 |
| 有索引 | type: ALL, rows: 1000 | type: ref, rows: 10 |

**性能差距**：1000 × 100000 = 1 亿行扫描 → 1000 × 10 = 10000 行扫描，**差距 10000 倍**。

---

## 三、COUNT 优化

### 3.1 COUNT(*) vs COUNT(1) vs COUNT(col)

```sql
-- 三个写法的区别
SELECT COUNT(*) FROM users;     -- 统计所有行（含 NULL）
SELECT COUNT(1) FROM users;     -- 同 COUNT(*)，没有区别
SELECT COUNT(col) FROM users;   -- 统计 col 不为 NULL 的行数
```

**在 InnoDB 中，COUNT(*) 和 COUNT(1) 性能完全相同**。MySQL 优化器会把 COUNT(1) 优化为 COUNT(*)。不要被网上的"COUNT(1) 比 COUNT(*) 快"误导。

```sql
-- COUNT(col) 忽略 NULL
SELECT COUNT(email) FROM users;  -- 只统计 email 不为 NULL 的行
SELECT COUNT(*) FROM users;      -- 统计所有行

-- 如果 email 列有 NOT NULL 约束，两者结果相同
-- 如果 email 列允许 NULL，COUNT(email) 可能比 COUNT(*) 少
```

### 3.2 大表 COUNT 为什么慢？

InnoDB 不支持直接读取"表有多少行"（因为 MVCC 的原因，不同事务看到的数据不同）。所以 COUNT(*) 必须遍历索引。

```sql
-- 在没有 WHERE 条件时，MySQL 会选最小的索引来扫描
EXPLAIN SELECT COUNT(*) FROM users;
-- type: index, key: 某个二级索引（选最小的）
```

### 3.3 大表 COUNT 近似值

如果不需要精确值，可以用近似值：

```sql
-- 方法 1：SHOW TABLE STATUS
SHOW TABLE STATUS LIKE 'users';
-- 关注 Rows 列，但这是近似值，误差可能达 40-50%

-- 方法 2：information_schema
SELECT TABLE_ROWS FROM information_schema.TABLES
WHERE TABLE_SCHEMA = 'my_shop' AND TABLE_NAME = 'users';
-- 同样是近似值

-- 方法 3：使用缓存（Redis）维护一个计数器
-- 在应用层每次 INSERT 时 +1，DELETE 时 -1
```

> **想多一点**：为什么 `SHOW TABLE STATUS` 的 Rows 是近似值？因为 InnoDB 不维护精确的行数——MVCC 下不同事务看到的数据不同，维护精确行数需要加锁，代价太高。所以 InnoDB 用采样估算，误差可接受。

---

## 四、IN vs EXISTS 性能对比

### 4.1 基本差异

```sql
-- IN：先执行子查询，再匹配外层
SELECT * FROM orders WHERE user_id IN (SELECT id FROM users WHERE city = '北京');

-- EXISTS：对外层的每一行，检查子查询是否有匹配
SELECT * FROM orders o WHERE EXISTS (
    SELECT 1 FROM users u WHERE u.id = o.user_id AND u.city = '北京'
);
```

### 4.2 什么时候用 IN，什么时候用 EXISTS？

**原则：小表驱动大表。**

```sql
-- 场景 1：子查询结果小（users 中北京用户少），外层表大（orders 多）
-- → 用 IN（子查询先执行，结果集小）
SELECT * FROM orders WHERE user_id IN (
    SELECT id FROM users WHERE city = '北京'
);

-- 场景 2：外层表小（orders 少），子查询结果大（users 中活跃用户多）
-- → 用 EXISTS（外层先执行，每行检查一次）
SELECT * FROM orders o WHERE EXISTS (
    SELECT 1 FROM users u WHERE u.id = o.user_id AND u.status = 'active'
);
```

### 4.3 EXPLAIN 验证

```sql
-- 创建测试索引
CREATE INDEX idx_user_id ON orders(user_id);
CREATE INDEX idx_city ON users(city);

-- IN 的 EXPLAIN
EXPLAIN SELECT * FROM orders WHERE user_id IN (
    SELECT id FROM users WHERE city = '北京'
);
-- 子查询先执行，结果集作为常量列表

-- EXISTS 的 EXPLAIN
EXPLAIN SELECT * FROM orders o WHERE EXISTS (
    SELECT 1 FROM users u WHERE u.id = o.user_id AND u.city = '北京'
);
-- 外层 orders 驱动，每行检查 users
```

### 4.4 MySQL 8.0 的改进

MySQL 8.0 对 IN 子查询做了大量优化，很多场景下 IN 和 EXISTS 性能差别不大。**不要凭直觉选择，用 EXPLAIN 验证。**

---

## 五、ORDER BY 优化

### 5.1 利用索引排序

索引本身是有序的（B+树叶子节点有序链表）。如果 ORDER BY 的列有索引，MySQL 可以直接用索引排序，不需要额外排序。

```sql
-- 假设 created_at 有索引

-- ✅ 利用索引排序
EXPLAIN SELECT * FROM users ORDER BY created_at;
-- Extra: NULL（没有 Using filesort！）

-- ❌ 需要额外排序
EXPLAIN SELECT * FROM users ORDER BY city;
-- Extra: Using filesort
```

### 5.2 ORDER BY + WHERE 的索引利用

```sql
-- 假设有联合索引 idx_status_created(status, created_at)

-- ✅ 利用索引排序：WHERE 和 ORDER BY 都是索引的最左前缀
SELECT * FROM orders WHERE status = 'pending' ORDER BY created_at;
-- Extra: NULL（没有 Using filesort，因为索引已经按 status + created_at 排序）

-- ❌ 需要额外排序：虽然走了索引，但 WHERE 条件过滤后，索引顺序被破坏
SELECT * FROM orders WHERE status = 'pending' ORDER BY amount;
-- Extra: Using filesort（amount 不在索引中，按 amount 排序需要额外排序）
```

**规则**：ORDER BY 能利用索引排序的条件是——索引的最左前缀列在 WHERE 中用等值条件，且 ORDER BY 的列是索引的后续列。

---

## 六、批量操作优化

### 6.1 批量 INSERT

```sql
-- ❌ 逐条 INSERT：每条都是一个事务
INSERT INTO users (name, email) VALUES ('user1', 'u1@example.com');
INSERT INTO users (name, email) VALUES ('user2', 'u2@example.com');
INSERT INTO users (name, email) VALUES ('user3', 'u3@example.com');
-- 1000 条 = 1000 次事务提交 = 1000 次磁盘 IO

-- ✅ 批量 INSERT：一条 SQL 搞定
INSERT INTO users (name, email) VALUES
('user1', 'u1@example.com'),
('user2', 'u2@example.com'),
('user3', 'u3@example.com'),
-- ... 一次最多几百到几千条
('user1000', 'u1000@example.com');
```

**为什么快？**
- 一次 SQL 解析
- 一次事务提交
- 一次磁盘 IO（写 redo log）

**建议**：每次批量 500-2000 条，不要一次插太多（可能导致锁表时间过长）。

### 6.2 批量 UPDATE

```sql
-- ❌ 逐条 UPDATE
UPDATE users SET status = 'active' WHERE id = 1;
UPDATE users SET status = 'active' WHERE id = 2;
-- ...

-- ✅ 用 IN 批量
UPDATE users SET status = 'active' WHERE id IN (1, 2, 3, ..., 100);

-- ✅ 用 CASE WHEN（更新不同值）
UPDATE users SET status = CASE id
    WHEN 1 THEN 'active'
    WHEN 2 THEN 'inactive'
    WHEN 3 THEN 'banned'
END
WHERE id IN (1, 2, 3);
```

---

## 七、实际案例

### 案例 1：电商订单查询优化

**场景**：查询"某用户最近 30 天的已完成订单，按创建时间倒序"

```sql
-- ❌ 优化前：没有索引，全表扫描
SELECT * FROM orders
WHERE user_id = 42 AND status = 'completed'
AND created_at >= '2024-01-01'
ORDER BY created_at DESC
LIMIT 20;

-- EXPLAIN: type: ALL, rows: 1000000, Extra: Using where; Using filesort
```

**优化**：

```sql
-- 创建联合索引
CREATE INDEX idx_user_status_time ON orders(user_id, status, created_at);

-- ✅ 优化后
EXPLAIN SELECT * FROM orders
WHERE user_id = 42 AND status = 'completed'
AND created_at >= '2024-01-01'
ORDER BY created_at DESC
LIMIT 20;
-- type: range, rows: 15, Extra: Using index condition
```

**效果**：rows 从 1000000 → 15，性能提升约 60000 倍。

### 案例 2：用户标签筛选优化

**场景**：多条件标签筛选（用户可能有多个标签）

```sql
-- ❌ 优化前：每个标签条件单独查
SELECT * FROM users
WHERE tag1 = 'VIP' AND tag2 = 'active' AND tag3 = 'verified';

-- 问题：多个单独索引，MySQL 通常只用一个
```

**优化**：

```sql
-- 创建联合索引覆盖所有标签
CREATE INDEX idx_tags ON users(tag1, tag2, tag3);

-- ✅ 优化后
EXPLAIN SELECT * FROM users
WHERE tag1 = 'VIP' AND tag2 = 'active' AND tag3 = 'verified';
-- 走了联合索引
```

### 案例 3：日志表统计优化

**场景**：统计每天的错误日志数

```sql
-- ❌ 优化前：全表扫描
SELECT DATE(created_at) AS day, COUNT(*) AS errors
FROM logs
WHERE level = 'ERROR'
GROUP BY DATE(created_at);
-- 问题：DATE() 函数导致索引失效
```

**优化**：

```sql
-- 创建联合索引
CREATE INDEX idx_level_time ON logs(level, created_at);

-- ✅ 优化后：避免函数包裹索引列
SELECT DATE(created_at) AS day, COUNT(*) AS errors
FROM logs
WHERE level = 'ERROR'
AND created_at >= '2024-01-01'
GROUP BY DATE(created_at);
-- 带了范围条件，走了 range 扫描
```

---

## 八、大表 DDL 概述

> **本节标注"进阶运维内容，详见第 25 章"**。这里只给你一个概念，让你知道存在这样的工具。

对千万级大表执行 `ALTER TABLE ... ADD INDEX` 会锁表很长时间（可能几小时），导致业务中断。

解决方案：
- **pt-online-schema-change（pt-osc）**：Percona 工具，创建新表 → 复制数据 → 切换
- **gh-ost**：GitHub 开源，用 binlog 同步增量数据，更安全

这两个工具可以在不锁表的情况下完成 DDL 操作。第 25 章讲备份与恢复时会详细介绍。

---

## 我做得对不对？

### 验证方法

针对每个优化场景，用 EXPLAIN 对比前后差异：

```sql
-- 1. 分页优化
EXPLAIN SELECT * FROM users ORDER BY id LIMIT 100000, 10;
EXPLAIN SELECT * FROM users WHERE id > 99990 ORDER BY id LIMIT 10;

-- 2. JOIN 优化
EXPLAIN SELECT * FROM users u INNER JOIN orders o ON u.id = o.user_id;
-- 检查 orders 表的 type 是否为 ref（不是 ALL）

-- 3. COUNT 优化
SELECT COUNT(*) FROM orders;
SHOW TABLE STATUS LIKE 'orders';

-- 4. ORDER BY 优化
EXPLAIN SELECT * FROM orders ORDER BY created_at DESC;
-- 检查 Extra 是否有 Using filesort

-- 5. 批量 INSERT
-- 用应用代码或存储过程测试，或直接在 MySQL 中测
INSERT INTO users (name, email) VALUES
('a', 'a@test.com'), ('b', 'b@test.com'), ('c', 'c@test.com');
```

---

## 不对怎么办？

### 常见错误 1：盲目优化

在不知道慢在哪里的时候就开始优化，比如：

```sql
-- 不知道查询慢在哪里，就乱加索引
CREATE INDEX idx_a ON table(a);
CREATE INDEX idx_b ON table(b);
CREATE INDEX idx_c ON table(c);
-- 结果：索引太多，写入变慢，优化器选错索引
```

**正确做法**：先用 EXPLAIN 看执行计划，再用慢查询日志定位瓶颈，最后针对性优化。

### 常见错误 2：不测量就优化

```sql
-- 凭感觉认为"加个索引就好了"
CREATE INDEX idx_xxx ON table(xxx);
-- 但 EXPLAIN 发现优化器还是不用这个索引
```

**正确做法**：每次优化后，用 EXPLAIN 验证效果，比较 rows 的变化。

### 常见错误 3：IN 子查询过大

```sql
-- ❌ IN 子查询返回 100 万行
SELECT * FROM orders WHERE user_id IN (
    SELECT id FROM users  -- 100 万行！
);

-- ✅ 用 JOIN 替代
SELECT o.* FROM orders o
INNER JOIN users u ON o.user_id = u.id;
```

大 IN 子查询会导致 MySQL 在内存中创建巨大的临时表，甚至写磁盘。

---

## 本章小结

| 本章学了什么 | 对应命令/概念 | 注意事项 |
|-------------|-------------|---------|
| 深分页优化 | 游标分页 `WHERE id > last_id` | 不能跳页，要求排序键有序 |
| 延迟关联 | 子查询先查主键再回表 | 适用于 ORDER BY 非主键列的深分页 |
| JOIN 优化 | 小表驱动大表 + JOIN 列加索引 | 被驱动表的 JOIN 列必须有索引 |
| COUNT 优化 | COUNT(*) = COUNT(1) | 大表用近似值或缓存计数 |
| IN vs EXISTS | 小表驱动大表原则 | MySQL 8.0 已优化，用 EXPLAIN 验证 |
| ORDER BY 优化 | 利用索引有序性 | 索引最左前缀列等值 + ORDER BY 后续列 |
| 批量 INSERT | 一条 SQL 插入多行 | 每次 500-2000 条，避免事务过长 |
| 批量 UPDATE | 用 IN 或 CASE WHEN 批量 | 减少 SQL 解析和事务提交次数 |
| 大表 DDL | pt-osc / gh-ost | 不锁表修改表结构，详见第 25 章 |
| 优化原则 | 先 EXPLAIN → 再优化 → 再验证 | 不盲目优化，不凭感觉优化 |

---

> **[可暂停点 4/7]**：第四篇结束。你已学完索引原理、EXPLAIN 分析、索引实战和 SQL 优化场景四章。下一篇我们将进入事务与并发控制的世界。重启命令：`mysql -u root -p`，`USE my_shop;`，`EXPLAIN SELECT * FROM users WHERE id = 1;` 验证索引环境。