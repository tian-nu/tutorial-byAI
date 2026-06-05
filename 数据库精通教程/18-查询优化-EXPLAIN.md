# 18 — 查询优化（EXPLAIN）

> - 对应文档版本：database_mastery_outline.md v1, database_mastery_detailed_outline.md v2
> - 适用环境：MySQL 8.0+，已创建 my_shop 数据库
> - 读者角色：已学完第 17 章 B+树索引原理的开发者
> - 预计耗时：新手 60 分钟 / 熟手 30 分钟
> - 前置教程：第 04-17 章
> - 可视化：无

---

## 我在做什么？

第 17 章你理解了索引的底层原理。但"知道"和"会用"之间，还差一个关键工具：**EXPLAIN**。

EXPLAIN 是 MySQL 的"X 光机"——它能告诉你 MySQL 打算怎么执行你的 SQL，用没用索引，扫描了多少行，哪里是瓶颈。没有 EXPLAIN，优化就是瞎猜；有了 EXPLAIN，优化就是科学。

**重要提示**：本章和原细纲顺序互换——先学 EXPLAIN（第 18 章），再学索引实战（第 19 章）。原因很简单：你先学会"看 X 光片"，再学"怎么开药方"，比先背一堆禁忌再理解原理要自然得多。

学完这一章，你能读懂 EXPLAIN 的输出，根据 type、rows、Extra 字段判断查询是否高效，并给出优化建议。

---

## 一、EXPLAIN 基本用法

### 1.1 最简单的 EXPLAIN

```sql
EXPLAIN SELECT * FROM users WHERE id = 1;
```

输出大概长这样：

```
+----+-------------+-------+-------+---------------+---------+---------+-------+------+-------+
| id | select_type | table | type  | possible_keys | key     | key_len | ref   | rows | Extra |
+----+-------------+-------+-------+---------------+---------+---------+-------+------+-------+
|  1 | SIMPLE      | users | const | PRIMARY       | PRIMARY | 4       | const |    1 | NULL  |
+----+-------------+-------+-------+---------------+---------+---------+-------+------+-------+
```

这一行里有 10 个字段，但新手不需要全部理解。我们重点看 **4 个核心字段**：

| 字段 | 含义 | 重点关注 |
|------|------|---------|
| **type** | 访问类型 | 从差到好：ALL → index → range → ref → const |
| **key** | 实际使用的索引 | NULL = 没走索引！ |
| **rows** | 预估扫描行数 | 越小越好 |
| **Extra** | 额外信息 | 看有没有 Using temporary、Using filesort |

另外，**possible_keys** 是 MySQL 认为"可能"用到的索引，**key** 是"实际"用的索引。如果 possible_keys 有值而 key 是 NULL，说明 MySQL 觉得用了索引也不划算，选择了全表扫描。

### 1.2 EXPLAIN FORMAT=JSON

如果你觉得表格版不够详细，MySQL 5.6+ 支持 JSON 格式：

```sql
EXPLAIN FORMAT=JSON SELECT * FROM users WHERE id = 1\G
```

输出会包含更详细的成本估算（`query_cost`），但日常使用表格版就够了。

---

## 二、type 字段：从差到好

type 字段描述了 MySQL 访问数据的方式，是 EXPLAIN 中**最重要的字段**。从最差到最好排列：

```
ALL → index → range → ref → eq_ref → const → system
差 ←———————————————————————————————————————→ 好
```

### 2.1 ALL：全表扫描（最差！）

```sql
EXPLAIN SELECT * FROM users WHERE name = '张三';
-- 假设 name 列没有索引

-- type: ALL
-- rows: 100000  （假设 10 万行）
```

**含义**：MySQL 逐行扫描整张表，一行一行检查 `name = '张三'`。

**看到 ALL 就要警惕**：如果 rows 很大（比如 > 1000），这条查询大概率需要优化。

### 2.2 index：全索引扫描（比 ALL 略好）

```sql
EXPLAIN SELECT name FROM users ORDER BY name;
-- 假设 name 列有索引

-- type: index
```

**含义**：扫描整个索引而不是整张表。因为索引通常比表小，所以比 ALL 快一点。但仍然是全扫描，rows 很大时也慢。

**与 ALL 的区别**：ALL 扫描数据页，index 扫描索引页。索引页更小，IO 更少，但本质还是"全扫"。

### 2.3 range：范围扫描

```sql
EXPLAIN SELECT * FROM users WHERE id BETWEEN 100 AND 200;
-- 主键索引

-- type: range
```

**含义**：MySQL 用索引定位到范围的起点，然后沿着索引扫描到终点。这是 B+树叶子节点链表的优势。

**触发条件**：`=`、`>`、`<`、`>=`、`<=`、`BETWEEN`、`IN`、`LIKE 'xxx%'`（注意是前匹配，不是前导模糊）。

### 2.4 ref：非唯一索引查找

```sql
EXPLAIN SELECT * FROM users WHERE age = 25;
-- 假设 age 列有索引（非唯一，多个人可能同岁）

-- type: ref
```

**含义**：使用非唯一索引查找，可能返回多行。这是很常见的访问类型，能走到 ref 就算不错了。

### 2.5 eq_ref：唯一索引关联查找

```sql
EXPLAIN SELECT * FROM orders o
JOIN users u ON o.user_id = u.id;
-- users.id 是主键（唯一索引）

-- 在 orders 的每一行中，type 可能是：ALL
-- 在 users 中，type 是：eq_ref
```

**含义**：使用唯一索引（主键或 UNIQUE 索引）做等值查找，最多返回一行。这是 JOIN 中最理想的访问类型。

### 2.6 const：主键等值查找（最好！）

```sql
EXPLAIN SELECT * FROM users WHERE id = 1;
-- 主键索引

-- type: const
```

**含义**：用主键等值查找，最多返回一行。MySQL 把它当作常量处理，极快。

### 2.7 system：系统表（极少见）

只有一行数据的系统表。日常开发几乎遇不到，知道就行。

### type 字段速查表

| type | 含义 | 严重程度 | 触发条件 |
|------|------|---------|---------|
| ALL | 全表扫描 | 🔴 必须优化（大表） | 没走索引 |
| index | 全索引扫描 | 🟠 尽量优化 | 扫描整个索引 |
| range | 范围扫描 | 🟡 可以接受 | BETWEEN、>、<、IN |
| ref | 非唯一索引查找 | 🟢 不错 | 普通索引等值查找 |
| eq_ref | 唯一索引查找 | 🟢 好 | JOIN 时唯一索引关联 |
| const | 主键等值查找 | 🟢 最好 | WHERE id = 具体值 |

---

## 三、key 字段：实际使用的索引

```sql
EXPLAIN SELECT * FROM users WHERE name = '张三';
-- 假设 name 列有索引 idx_name

-- key: idx_name  ← 好！走了索引

EXPLAIN SELECT * FROM users WHERE city = '北京';
-- 假设 city 列没有索引

-- key: NULL       ← 坏！没走索引
```

**key 字段显示 NULL 时，说明 MySQL 选择了全表扫描**。这可能是因为：
- 该列没有索引
- 有索引但 MySQL 优化器认为全表扫描更快（比如小表）
- 索引失效了（第 19 章讲）

---

## 四、rows 字段：预估扫描行数

rows 是 MySQL 优化器**预估**的需要扫描的行数，不是精确值，但足够用于判断。

```sql
EXPLAIN SELECT * FROM users WHERE age > 30;
-- rows: 50000  ← 预估扫描 5 万行

EXPLAIN SELECT * FROM users WHERE id = 1;
-- rows: 1      ← 预估扫描 1 行
```

**rows 的指导意义**：
- rows = 1 → 极好，主键或唯一索引等值查找
- rows < 100 → 不错
- rows < 1000 → 可以接受
- rows > 10000 → 需要关注，尤其当实际返回行数很少时
- rows 接近表总行数 → 全表扫描，必须优化

> **想多一点**：rows 是"预估"值，不是"实际"值。MySQL 基于统计信息（`innodb_stats_persistent`）估算。如果统计信息过时，rows 可能严重偏离实际。可以用 `ANALYZE TABLE table_name;` 更新统计信息。

---

## 五、Extra 字段：额外信息

Extra 字段包含关于查询执行的额外信息，是 EXPLAIN 的"备注栏"。

### 5.1 Using index（覆盖索引）

```sql
EXPLAIN SELECT id, age FROM users WHERE age = 25;
-- 假设 age 列有索引

-- Extra: Using index
```

**含义**：查询的所有列都在索引中，不需要回表。这是**最好的情况**，第 19 章会详细讲覆盖索引。

### 5.2 Using where

```sql
EXPLAIN SELECT * FROM users WHERE age = 25 AND city = '北京';
-- 假设只有 age 列有索引

-- Extra: Using where
```

**含义**：MySQL 在存储引擎返回行之后，在 Server 层做了额外的 WHERE 过滤。如果 age 索引返回了 100 行，MySQL 还需要检查这 100 行的 city 是否等于 '北京'。

### 5.3 Using index condition（索引下推，ICP）

```sql
EXPLAIN SELECT * FROM users WHERE name LIKE '张%' AND age = 25;
-- 假设有联合索引 idx_name_age(name, age)

-- Extra: Using index condition
```

**含义**：MySQL 使用了索引下推（Index Condition Pushdown，ICP）*此术语见附录E*。简单说，MySQL 把 `age = 25` 这个过滤条件"下推"到存储引擎层，在索引中直接过滤，而不是回表后再过滤。第 19 章会详细讲。

### 5.4 Using temporary（⚠️ 需要关注）

```sql
EXPLAIN SELECT DISTINCT city FROM users ORDER BY created_at;
-- 如果 city 和 created_at 没有联合索引

-- Extra: Using temporary
```

**含义**：MySQL 需要创建临时表来完成查询。这通常发生在 GROUP BY、DISTINCT、ORDER BY 同时使用时。临时表可能写磁盘，性能差。

### 5.5 Using filesort（⚠️ 需要关注）

```sql
EXPLAIN SELECT * FROM users ORDER BY created_at;
-- 如果 created_at 没有索引

-- Extra: Using filesort
```

**含义**：MySQL 需要额外的排序操作。"filesort" 这个名字有误导性——它不一定写文件，可能只在内存中排序。但无论如何，**额外排序就是额外开销**。

**注意**：Using filesort 不一定严重。如果排序数据量很小（几百行），在内存中排序很快。但如果 rows 很大（几万行），filesort 就可能是瓶颈。

### 5.6 Extra 字段速查表

| Extra 值 | 含义 | 严重程度 |
|----------|------|---------|
| Using index | 覆盖索引，无需回表 | 🟢 最好 |
| Using index condition | 索引下推，减少回表 | 🟢 好 |
| Using where | Server 层额外过滤 | 🟡 正常 |
| Using temporary | 需要临时表 | 🟠 需要关注 |
| Using filesort | 需要额外排序 | 🟠 需要关注 |
| NULL | 无额外信息 | 🟡 正常 |

---

## 六、EXPLAIN ANALYZE（MySQL 8.0.18+）

**要求 MySQL 8.0.18 及以上版本**。

`EXPLAIN ANALYZE` 不只是预估，而是**实际执行**查询并测量每步的耗时：

```sql
EXPLAIN ANALYZE SELECT * FROM users WHERE age = 25;
```

输出示例（简化）：

```
-> Filter: (users.age = 25)  (cost=... rows=10) (actual time=0.123..0.456 rows=10 loops=1)
    -> Index lookup on users using idx_age (age=25)  (cost=... rows=10) (actual time=0.100..0.200 rows=10 loops=1)
```

**关键区别**：
- `EXPLAIN`：预估，不执行查询
- `EXPLAIN ANALYZE`：实际执行，返回真实耗时和行数

**使用场景**：当你觉得 EXPLAIN 的预估和实际不符时，用 EXPLAIN ANALYZE 看真实数据。

---

## 七、慢查询日志

慢查询日志（Slow Query Log）*此术语见附录E* 是 MySQL 记录执行时间超过阈值的查询的日志。

### 7.1 开启慢查询日志

```sql
-- 查看当前状态
SHOW VARIABLES LIKE 'slow_query_log%';
SHOW VARIABLES LIKE 'long_query_time';

-- 开启慢查询日志
SET GLOBAL slow_query_log = ON;

-- 设置阈值（超过 2 秒的查询被记录）
SET GLOBAL long_query_time = 2;

-- 记录不走索引的查询（可选）
SET GLOBAL log_queries_not_using_indexes = ON;
```

### 7.2 查看慢查询日志

```bash
# 找到慢查询日志文件路径
mysql -u root -p -e "SHOW VARIABLES LIKE 'slow_query_log_file';"

# 用 mysqldumpslow 分析
mysqldumpslow -s t -t 10 /path/to/slow-query.log
# -s t：按时间排序
# -t 10：显示前 10 条
```

### 7.3 慢查询日志的局限性

- 只记录超过阈值的查询，不记录"快但执行次数多"的查询
- 生产环境开启有性能开销（约 1-3%）
- 需要定期清理，否则日志文件会越来越大

---

## 八、实战：EXPLAIN 对比分析

我们来做一个完整的对比实验。先用 my_shop 的 users 表：

```sql
-- 1. 查看表中有哪些索引
SHOW INDEX FROM users;

-- 2. 没有索引的情况
EXPLAIN SELECT * FROM users WHERE email = 'alice@example.com';
-- type: ALL, rows: 很多, key: NULL
-- 结论：全表扫描，需要优化！

-- 3. 创建索引
CREATE INDEX idx_email ON users(email);

-- 4. 再次 EXPLAIN
EXPLAIN SELECT * FROM users WHERE email = 'alice@example.com';
-- type: ref, rows: 1, key: idx_email
-- 结论：走索引了，效率大幅提升！

-- 5. 验证覆盖索引
EXPLAIN SELECT id, email FROM users WHERE email = 'alice@example.com';
-- Extra: Using index
-- 结论：不需要回表，最快！

-- 6. 验证索引失效
EXPLAIN SELECT * FROM users WHERE UPPER(email) = 'ALICE@EXAMPLE.COM';
-- type: ALL, key: NULL
-- 结论：函数包裹索引列 → 索引失效！第 19 章详解
```

---

## 我做得对不对？

### 验证方法

用以下 SQL 自测，能解释每个 EXPLAIN 输出就算合格：

```sql
-- 测试 1：主键等值查找
EXPLAIN SELECT * FROM users WHERE id = 1;
-- 预期：type=const, key=PRIMARY, rows=1

-- 测试 2：无索引列查询
EXPLAIN SELECT * FROM users WHERE city = '北京';
-- 预期：type=ALL, key=NULL

-- 测试 3：索引列等值查找
EXPLAIN SELECT * FROM users WHERE email = 'alice@example.com';
-- 预期：type=ref, key=idx_email（需先创建）

-- 测试 4：范围查询
EXPLAIN SELECT * FROM users WHERE id BETWEEN 10 AND 20;
-- 预期：type=range, key=PRIMARY
```

---

## 不对怎么办？

### 常见错误 1：只看 type 不看 rows

```sql
-- 查询 A
EXPLAIN SELECT * FROM users WHERE id = 1;
-- type: const, rows: 1 ✅

-- 查询 B
EXPLAIN SELECT * FROM users WHERE age > 30;
-- type: range, rows: 50000  ← 虽然 type 是 range，但 rows 很大！
```

range 不一定比 ref 差，ref 不一定比 range 好。**type + rows 一起看**才有意义。

### 常见错误 2：看到 Using filesort 就恐慌

```sql
EXPLAIN SELECT * FROM users WHERE id = 1 ORDER BY name;
-- Extra: Using filesort
-- rows: 1
```

rows=1 时，filesort 排序 1 行数据，几乎零开销。只有当 rows 很大时，filesort 才需要关注。

### 常见错误 3：Using temporary 就必须优化

```sql
EXPLAIN SELECT DISTINCT status FROM orders;
-- Extra: Using temporary
```

如果 `status` 的值只有几种（如 'pending', 'shipped', 'done'），临时表非常小，可以忽略。但当 `status` 可能有很多不同值且数据量大时才需要关注。

### 常见错误 4：EXPLAIN 结果和实际差别大

EXPLAIN 是预估，不是实际执行。如果 rows 预估是 100 但实际返回 10000 行，可能是统计信息过时了：

```sql
-- 更新统计信息
ANALYZE TABLE users;
```

---

## 本章小结

| 本章学了什么 | 对应命令/概念 | 注意事项 |
|-------------|-------------|---------|
| EXPLAIN 基本用法 | `EXPLAIN SELECT ...;` | 核心关注 type、key、rows、Extra |
| type: ALL | 全表扫描 | 大表时必须优化 |
| type: index | 全索引扫描 | 比 ALL 略好，但仍需关注 |
| type: range | 范围扫描 | 使用 >、<、BETWEEN、IN 等 |
| type: ref | 非唯一索引等值查找 | 常见且不错的访问类型 |
| type: eq_ref | 唯一索引等值查找 | JOIN 时最理想 |
| type: const | 主键等值查找 | 最快，只有一行 |
| key 字段 | 实际使用的索引 | NULL = 没走索引，需要排查 |
| rows 字段 | 预估扫描行数 | 结合 type 一起看，不是精确值 |
| Extra: Using index | 覆盖索引 | 最好，无需回表 |
| Extra: Using index condition | 索引下推（ICP） | 好，减少回表 |
| Extra: Using temporary | 需要临时表 | 大表时需关注 |
| Extra: Using filesort | 需要额外排序 | rows 大时需关注 |
| EXPLAIN ANALYZE | 实际执行并测量 | MySQL 8.0.18+，真实耗时 |
| 慢查询日志 | `SET GLOBAL slow_query_log = ON;` | 生产环境记录慢 SQL |
| mysqldumpslow | 分析慢查询日志 | `-s t` 按时间排序 |

---

> **[可暂停点 — 本章结束]**：你已经掌握了 EXPLAIN 这个"X 光机"。下一章我们学索引实战，亲手创建索引并用 EXPLAIN 验证效果。重启命令：`mysql -u root -p`，`USE my_shop;`，`EXPLAIN SELECT * FROM users WHERE id = 1;`。