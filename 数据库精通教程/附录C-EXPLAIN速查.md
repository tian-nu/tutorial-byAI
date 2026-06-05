# 附录 C — EXPLAIN 输出字段速查

> 本附录按 EXPLAIN 输出的每个字段，逐一解释其含义、常见值、以及对应的优化建议。当你面对一个慢查询时，EXPLAIN 就是你的 X 光机——它告诉你 MySQL 是怎么执行这个查询的。

---

## 一、EXPLAIN 基础用法

```sql
-- 基本用法
EXPLAIN SELECT * FROM orders WHERE user_id = 100;

-- JSON 格式（更详细）
EXPLAIN FORMAT=JSON SELECT * FROM orders WHERE user_id = 100;

-- 实际执行并分析（MySQL 8.0.18+，会真正执行查询！）
EXPLAIN ANALYZE SELECT * FROM orders WHERE user_id = 100;
```

---

## 二、字段详解

### 2.1 `id`

| 值 | 含义 | 说明 |
|----|------|------|
| 相同数字 | 从上到下执行 | 简单查询或 JOIN 中同时执行的表 |
| 不同数字（递增） | 数字越大越先执行 | 子查询中，最内层子查询 id 最大 |
| NULL | UNION 结果集 | 表示 UNION 的最终合并结果 |

### 2.2 `select_type`

| 值 | 含义 | 优化建议 |
|----|------|---------|
| `SIMPLE` | 简单查询（无子查询、无 UNION） | 最佳情况，无需优化 |
| `PRIMARY` | 最外层查询 | 正常 |
| `SUBQUERY` | 子查询（非相关子查询） | 子查询可能全表扫描，考虑改写为 JOIN |
| `DEPENDENT SUBQUERY` | 相关子查询（依赖外部查询） | ⚠️ 性能杀手！外层每行都执行一次子查询，务必改写 |
| `DERIVED` | 派生表（FROM 子句中的子查询） | 物化到临时表，大数据量时慢 |
| `UNION` | UNION 中的第二个及之后的 SELECT | 正常 |
| `UNION RESULT` | UNION 的结果合并 | 正常 |

### 2.3 `table`

| 值 | 含义 |
|----|------|
| 表名 | 实际表名 |
| `<derivedN>` | 派生表，N 对应某个 id |
| `<unionM,N>` | UNION 合并结果 |

### 2.4 `partitions`

| 值 | 含义 |
|----|------|
| NULL | 没有分区 |
| 分区名 | 命中的分区（如 p0, p1） |

### 2.5 `type` ⭐（最重要字段）

**type 是访问类型，从好到差排列：**

| 值 | 含义 | 示例 | 优化建议 |
|----|------|------|---------|
| `NULL` | 不需要访问表 | `SELECT 1+1` | 完美 |
| `system` | 表只有一行（系统表） | 极少见 | 完美 |
| `const` | 主键或唯一索引等值匹配，最多一行 | `WHERE id = 1` | 完美 |
| `eq_ref` | JOIN 时用主键或唯一索引匹配，一行 | `JOIN ON a.id = b.id` | 非常好 |
| `ref` | 非唯一索引等值匹配，可能多行 | `WHERE user_id = 100` | 好 |
| `fulltext` | 全文索引 | `MATCH ... AGAINST` | 全文搜索专用 |
| `ref_or_null` | ref 的变体，额外搜索 NULL | `WHERE col = 1 OR col IS NULL` | 可接受 |
| `index_merge` | 索引合并（多个索引的交集/并集） | `WHERE a=1 OR b=2` | 比单索引好，但说明索引设计可能有问题 |
| `unique_subquery` | IN 子查询中用主键 | `WHERE id IN (SELECT ...)` | 可接受 |
| `index_subquery` | IN 子查询中用非唯一索引 | `WHERE col IN (SELECT ...)` | 可接受 |
| `range` | 索引范围扫描 | `WHERE id > 100`, `BETWEEN`, `IN` | 可接受，注意范围大小 |
| `index` | 全索引扫描（扫描整个索引树） | `ORDER BY indexed_col` | ⚠️ 比 ALL 好但仍然是全扫描 |
| `ALL` | 全表扫描 | 无 WHERE 或 WHERE 条件无索引 | ❌ 数据量大时必须优化 |

**记忆口诀：** `NULL → system → const → eq_ref → ref → range → index → ALL`，从左到右越来越差。你的目标是让 type 至少达到 `range` 级别。

### 2.6 `possible_keys`

| 值 | 含义 | 优化建议 |
|----|------|---------|
| 索引名列表 | MySQL 认为可能用到的索引 | 如果为 NULL 且 WHERE 有过滤条件，说明需要加索引 |
| NULL | 没有可用索引 | 检查 WHERE 条件是否需要索引 |

### 2.7 `key` ⭐

| 值 | 含义 | 优化建议 |
|----|------|---------|
| 索引名 | 实际使用的索引 | 如果不在 possible_keys 中，说明 MySQL 做了不同选择 |
| NULL | 没有使用索引 | 如果 type 是 ALL，说明全表扫描，需要优化 |

### 2.8 `key_len`

| 值 | 含义 | 优化建议 |
|----|------|---------|
| 数字（字节数） | 使用的索引长度 | 联合索引中，越大说明用到的列越多（越接近"最左前缀"的全部列） |

**计算示例：**
- `INT` 索引列：4 字节（可 NULL 时 +1 = 5）
- `VARCHAR(50)` utf8mb4：50 × 4 + 2（变长） = 202 字节（可 NULL 时 +1 = 203）

### 2.9 `ref`

| 值 | 含义 |
|----|------|
| `const` | 与常量比较，如 `WHERE col = 100` |
| 数据库名.表名.列名 | 与另一个表的列比较（JOIN 条件） |
| `func` | 与函数结果比较 |

### 2.10 `rows` ⭐

| 值 | 含义 | 优化建议 |
|----|------|---------|
| 数字 | MySQL **估算**需要扫描的行数 | 越小越好。如果 rows 很大但实际结果很少，说明索引选择性差 |

**注意：** rows 是估算值，不是精确值。InnoDB 的统计信息可能不准确，可以用 `ANALYZE TABLE` 更新。

### 2.11 `filtered`

| 值 | 含义 | 优化建议 |
|----|------|---------|
| 百分比（0-100） | 满足 WHERE 条件的行数占比 | 越低说明过滤效果越好，但 rows × filtered% 才是最终有效行数 |

### 2.12 `Extra` ⭐

| 值 | 含义 | 优化建议 |
|----|------|---------|
| `Using index` | 覆盖索引，不需要回表 | ✅ 最佳情况 |
| `Using where` | 用 WHERE 条件过滤 | 正常 |
| `Using index condition` | 索引下推（ICP） | ✅ 好，减少了回表 |
| `Using temporary` | 使用临时表 | ⚠️ 常见于 GROUP BY、DISTINCT、ORDER BY，考虑优化 |
| `Using filesort` | 额外排序（未用索引排序） | ⚠️ 检查 ORDER BY 列是否有索引 |
| `Using join buffer` | JOIN 用了缓冲 | ⚠️ JOIN 列没有索引 |
| `Impossible WHERE` | WHERE 条件永远为假 | 检查逻辑 |
| `No tables used` | 没有 FROM 子句 | 正常（如 `SELECT 1+1`） |
| `Select tables optimized away` | 优化器直接算出结果 | ✅ 最佳（如 `SELECT MAX(id) FROM t`） |
| `Using MRR` | 多范围读取优化 | ✅ 好 |
| `Using index for group-by` | 松散索引扫描 | ✅ 好 |

---

## 三、常见优化场景速查

### 3.1 type = ALL（全表扫描）

```
问题：WHERE 条件列没有索引
解决：CREATE INDEX idx_name ON table (col);
```

### 3.2 type = index（全索引扫描）

```
问题：扫描了整个索引，但不如 const/ref 高效
解决：添加更精确的 WHERE 条件，或考虑是否需要优化
```

### 3.3 Extra = Using filesort

```
问题：ORDER BY 列没有索引，需要额外排序
解决：CREATE INDEX idx_name ON table (order_col);
```

### 3.4 Extra = Using temporary

```
问题：GROUP BY 或 DISTINCT 导致临时表
解决：CREATE INDEX idx_name ON table (group_col);
```

### 3.5 Extra = Using join buffer

```
问题：JOIN 条件列没有索引
解决：在 JOIN 的关联列上创建索引
```

### 3.6 key_len 小于预期

```
问题：联合索引没有用到所有列
解决：检查 WHERE 条件是否满足"最左前缀"原则
```

### 3.7 select_type = DEPENDENT SUBQUERY

```
问题：相关子查询，外层每行执行一次
解决：改写为 JOIN
```

---

## 四、EXPLAIN 输出示例解读

### 示例 1：好查询

```sql
EXPLAIN SELECT * FROM orders WHERE user_id = 100;
```

```
id: 1
select_type: SIMPLE
table: orders
type: ref          ← 非唯一索引等值匹配，好
possible_keys: idx_user_id
key: idx_user_id   ← 用到了索引
key_len: 8
ref: const
rows: 5            ← 只扫描 5 行
Extra: NULL
```

**结论：** 查询质量好，无需优化。

### 示例 2：需要优化的查询

```sql
EXPLAIN SELECT * FROM orders WHERE total_amount > 100 ORDER BY created_at DESC;
```

```
id: 1
select_type: SIMPLE
table: orders
type: ALL          ← ❌ 全表扫描
possible_keys: NULL
key: NULL          ← ❌ 没有索引
rows: 100000       ← 扫描 10 万行
Extra: Using where; Using filesort  ← ❌ 额外排序
```

**优化方案：**
```sql
-- 1. 为 total_amount 加索引（解决全表扫描）
CREATE INDEX idx_total ON orders (total_amount);

-- 2. 如果经常按 total_amount 过滤 + 按 created_at 排序，建联合索引
CREATE INDEX idx_total_created ON orders (total_amount, created_at);
```

### 示例 3：覆盖索引（最佳）

```sql
EXPLAIN SELECT id, user_id FROM orders WHERE user_id = 100;
```

```
id: 1
select_type: SIMPLE
table: orders
type: ref
possible_keys: idx_user_id
key: idx_user_id
rows: 5
Extra: Using index  ← ✅ 覆盖索引，不需要回表
```

---

## 五、MySQL 8.0 EXPLAIN ANALYZE

MySQL 8.0.18 引入了 `EXPLAIN ANALYZE`，它会**真正执行查询**并给出实际耗时：

```sql
EXPLAIN ANALYZE SELECT * FROM orders WHERE user_id = 100;
```

输出示例：
```
-> Index lookup on orders using idx_user_id (user_id=100)
   (cost=0.35 rows=5) (actual time=0.015..0.018 rows=5 loops=1)
```

**关键字段：**
- `actual time`：实际执行时间（毫秒）
- `rows`：实际返回行数
- `loops`：循环次数（嵌套循环 JOIN 时很有用）

**注意：** `EXPLAIN ANALYZE` 会真正执行查询，所以对 UPDATE/DELETE 要特别小心，建议在事务中执行并回滚。