# 30 — PostgreSQL 对比 MySQL

> - 对应文档版本：本篇为数据库精通教程第七篇第 1 章
> - 适用环境：PostgreSQL 15+ / MySQL 8.0+，本章为概念对比章，部分命令可动手验证
> - 读者角色：已学完第 1-5 篇 MySQL 基础的开发者
> - 预计耗时：新手 90 分钟 / 熟手 45 分钟
> - 前置教程：第 1-5 篇（MySQL 基础）
> - 可视化：无

---

## 我在做什么？

你已经用了很长时间 MySQL，增删改查、索引、事务、主从复制都搞明白了。这时候你可能听说过另一个名字——**PostgreSQL**（简称 PG）。有人跟你说"PG 比 MySQL 强"，也有人说"MySQL 简单够用就行"。

这一章，我们不再争论"谁更好"，而是**把两个数据库放在一起对比**，让你清楚：
- PG 和 MySQL 在架构上有什么区别？
- 哪些场景 PG 比 MySQL 更合适？
- 从 MySQL 转到 PG，你要改哪些习惯？
- PG 有哪些 MySQL 没有的"杀手锏"功能？

学完这一章，你能说出至少 3 个"选 PG 不选 MySQL"的业务场景，并且能在 PG 里写出基本的 CRUD。

---

## 一、从 MySQL 到 PostgreSQL 的思维转换

在进入技术细节之前，先把思维方式调整过来。如果你抱着"PG 就是一个 SQL 语法不一样的 MySQL"的心态去学，你会碰很多钉子。

### 1.1 哲学差异

| 维度 | MySQL | PostgreSQL |
|------|-------|------------|
| 设计哲学 | 简单实用，"够用就行" | 标准优先，"规范和正确性比方便更重要" |
| SQL 标准 | 部分兼容，有自己的方言 | 极高标准兼容，几乎照着 SQL 标准实现的 |
| 扩展性 | 存储引擎可插拔 | 单引擎但高度可扩展（扩展、自定义类型、自定义函数） |
| 默认值 | 宽松，自动为你纠错 | 严格，你做错了就报错 |
| 社区 | Oracle 主导 + 社区 | 纯社区驱动 |

**一句话**：MySQL 像丰田——皮实耐用、简单好修；PostgreSQL 像奔驰——精密严谨、功能强大但学习曲线更陡。

### 1.2 字符串引用：你的第一个坑

这是 MySQL 转 PG 最常踩的一个坑——**双引号和单引号的语义不同**。

```sql
-- MySQL：双引号和单引号都当字符串（不推荐但能用）
SELECT "hello";      -- MySQL: 'hello'
SELECT 'hello';      -- MySQL: 'hello'

-- PostgreSQL：严格区分！
SELECT 'hello';      -- PG: 'hello' ✅ 字符串
SELECT "hello";      -- PG: 错误！"hello" 被当成列名或表名（标识符）❌
```

PG 中：
- **单引号 `'...'`**：字符串字面量
- **双引号 `"..."`**：标识符引用（列名、表名），仅当名称含大写或特殊字符时才需要

```sql
-- PostgreSQL 正确做法
SELECT 'hello';                        -- 字符串
SELECT "UserName" FROM "Users";        -- 含大写的列名和表名才用双引号
SELECT username FROM users;            -- 全小写不需要引号
```

> **记忆口诀**：PG 里单引号才是字符串，双引号是"名字"。MySQL 用户过来先把反引号 `` ` `` 换成双引号 `"`（标识符），把双引号 `"` 换成单引号 `'`（字符串）。

---

## 二、架构差异：进程 vs 线程

这是两者最根本的架构差异，决定了资源管理方式完全不同。

### 2.1 连接模型

```
MySQL 连接模型（线程）：
客户端 → 连接线程 → 共享 Buffer Pool
每个连接 = 一个线程，所有线程共享进程内存空间

PostgreSQL 连接模型（进程）：
客户端 → 连接进程（fork） → 独立内存空间
每个连接 = 一个独立的操作系统进程
```

| 维度 | MySQL（线程模型） | PostgreSQL（进程模型） |
|------|-------------------|----------------------|
| 每个连接的开销 | 小（线程共享内存） | 大（每个进程独立内存，约 5-10MB） |
| 上下文切换 | 线程切换（轻量） | 进程切换（较重） |
| 内存管理 | 共享 Buffer Pool | 每个进程有自己的 work_mem + 共享 shared_buffers |
| 连接数上限 | 通常数千 | 通常数百（每个进程开销大） |
| 崩溃隔离 | 线程崩溃可能影响整个进程 | 单个进程崩溃不影响其他连接 |
| 连接池需求 | 不那么迫切 | **强烈建议使用连接池**（PgBouncer 或 Pgpool-II） |

**想多一点**：PG 的进程模型导致每个连接都 `fork()` 一个新进程，创建连接的代价比 MySQL 大得多。这就是为什么 PG 社区非常强调"必须用连接池"。如果你从 MySQL 转 PG，最常见的性能问题就是"没用连接池，直接开了 500 个直连"。

```bash
# PG 强烈推荐的架构
app → PgBouncer（连接池，比如 50 个实际连接）→ PostgreSQL

# 而不是
app → 直接 500 个 PostgreSQL 连接
```

### 2.2 内存结构对比

| 组件 | MySQL（InnoDB） | PostgreSQL |
|------|----------------|------------|
| 共享数据缓存 | Buffer Pool（innodb_buffer_pool_size） | shared_buffers |
| 每连接工作内存 | sort_buffer_size, join_buffer_size | work_mem |
| WAL 日志 | redo log | WAL（Write-Ahead Log） |
| 后台刷盘 | InnoDB 后台线程 | Checkpointer + Background Writer |

---

## 三、MVCC 实现差异：PG 的"无 undo log"设计

这是 MySQL 和 PG 最值得深入理解的差异之一。两者都实现了 MVCC *此术语见附录E*，但实现方式天差地别。

### 3.1 MySQL（InnoDB）的 MVCC

回顾第 22 章：InnoDB 的 MVCC 通过 **undo log** 实现。
- 每行数据有一个隐藏的 `DB_TRX_ID`（创建或修改该行的事务 ID）和 `DB_ROLL_PTR`（指向 undo log 的回滚指针）
- 修改一行：原数据拷到 undo log，新数据写入数据页，回滚指针指向 undo log
- 读取时：通过 undo log 构建版本链，找到"当前事务可见的版本"
- undo log 膨胀需要后台 purge 线程清理

### 3.2 PostgreSQL 的 MVCC

PG 的 MVCC 完全不需要 undo log。它直接在**数据表（堆表）中保留所有版本**。

```
PostgreSQL 的 MVCC 核心机制：
  - 每行数据有两个系统字段：xmin（创建此版本的事务 ID）和 xmax（删除此版本的事务 ID）
  - UPDATE 操作 = 在表中 INSERT 一个新版本 + 把旧版本的 xmax 标记为当前事务 ID
  - DELETE 操作 = 把该行的 xmax 标记为当前事务 ID（不是真正删除）
  - SELECT 查询 = 找到 "xmin 已提交 且 xmax 未提交或未设置" 的版本
```

**对比表格**：

| 维度 | MySQL（InnoDB） | PostgreSQL |
|------|----------------|------------|
| 旧版本存储位置 | undo log（独立的回滚段） | 就在数据表（堆表）中 |
| UPDATE 实现 | 原行 → undo log，新行 → 数据页 | 原行标记失效 + 新行插入表中 |
| DELETE 实现 | 标记删除 + undo log 记录旧值 | 标记 xmax（逻辑删除） |
| 回滚 | 通过 undo log 恢复 | 标记事务为 aborted，死行保留 |
| 旧版本清理 | 后台 purge 线程清理 undo log | **VACUUM 命令**清理表中死行 |
| 空间膨胀 | undo log 膨胀 | 表本身膨胀（死行占空间） |
| 回滚段问题 | 长事务可能撑爆 undo log | 长事务阻止 VACUUM 清理，导致表膨胀 |

### 3.3 VACUUM：PG 的"垃圾回收"

因为旧版本直接存在表中，时间久了，表里面可能 90% 都是"死行"（dead tuples）——已经不被任何事务需要的旧版本。这些死行必须清理，否则：
- 表越变越大（空间浪费）
- 查询越来越慢（扫描大量死行）
- 事务 ID 回卷风险

**VACUUM** *此术语见附录E* 就是 PG 的垃圾回收机制：

```sql
-- 手动 VACUUM（不锁表，标记死行可重用但不归还磁盘空间）
VACUUM users;

-- VACUUM FULL（锁表，重写整个表，归还磁盘空间给操作系统）
VACUUM FULL users;

-- 查看表膨胀情况
SELECT schemaname, relname, 
       n_dead_tup, n_live_tup,
       round(n_dead_tup * 100.0 / NULLIF(n_live_tup + n_dead_tup, 0), 2) AS dead_ratio
FROM pg_stat_user_tables
ORDER BY n_dead_tup DESC;
```

**PG 有 autovacuum 守护进程**，自动在后台 VACUUM。通常不需要手动操作，但你需要知道它存在。

> **MySQL 用户的理解桥梁**：VACUUM 类似于 MySQL 的 purge 线程 + OPTIMIZE TABLE 的合体。但 PG 里 VACUUM 是核心机制，不是可选优化。

---

## 四、数据类型：PG 的丰富武器库

如果说 MySQL 的数据类型是"瑞士军刀"（基本够用），那 PG 的数据类型就是"专业工具箱"。

### 4.1 原生支持的 MySQL 没有的类型

```sql
-- === 数组类型 ===
CREATE TABLE products (
    id SERIAL PRIMARY KEY,     -- SERIAL = 自增整数，PG 不用 AUTO_INCREMENT
    name TEXT,
    tags TEXT[]                -- 字符串数组！
);

INSERT INTO products (name, tags) 
VALUES ('PG 教程', ARRAY['数据库', 'PostgreSQL', '教程']);

-- 数组查询：找包含"PostgreSQL"标签的商品
SELECT * FROM products WHERE 'PostgreSQL' = ANY(tags);
-- 数组索引（GIN）
CREATE INDEX idx_tags ON products USING GIN(tags);

-- === JSONB 类型 ===
CREATE TABLE user_profiles (
    user_id INT PRIMARY KEY,
    profile JSONB               -- 二进制 JSON，支持索引
);

INSERT INTO user_profiles VALUES (1, '{"name": "张三", "skills": ["SQL", "Python"], "address": {"city": "北京"}}');

-- JSONB 查询：找 city 是北京的
SELECT * FROM user_profiles WHERE profile @> '{"address": {"city": "北京"}}';
-- 提取字段
SELECT profile->>'name' FROM user_profiles;
-- JSONB 索引
CREATE INDEX idx_profile ON user_profiles USING GIN(profile);
-- 更新 JSONB 内部字段
UPDATE user_profiles 
SET profile = jsonb_set(profile, '{skills,0}', '"Go"') 
WHERE user_id = 1;

-- === UUID 类型 ===
CREATE TABLE api_keys (
    id UUID DEFAULT gen_random_uuid(),
    user_id INT
);

-- === 网络地址类型 ===
SELECT '192.168.1.0/24'::CIDR;        -- IP 地址段
SELECT '192.168.1.1'::INET;           -- IP 地址
SELECT '08:00:2b:01:02:03'::MACADDR;  -- MAC 地址

-- 判断 IP 是否在网段内
SELECT '192.168.1.5'::INET << '192.168.1.0/24'::INET;  -- true
```

### 4.2 类型对比速查

| 需求 | MySQL 怎么做 | PostgreSQL 怎么做 |
|------|-------------|------------------|
| 自增主键 | `INT AUTO_INCREMENT` | `SERIAL` 或 `BIGINT GENERATED ALWAYS AS IDENTITY` |
| 布尔值 | `TINYINT(1)`（假装是 bool） | `BOOLEAN`（真正的 true/false） |
| 长文本 | `TEXT` | `TEXT` |
| 数组 | ❌ 不支持，用 JSON 或逗号分隔字符串凑合 | `INT[]` `TEXT[]` 原生支持 |
| JSON | `JSON` 类型（MySQL 5.7+） | `JSONB`（二进制）+ `JSON`（文本），JSONB 更强 |
| UUID | `CHAR(36)` 或 `BINARY(16)` | `UUID` 原生类型 + `gen_random_uuid()` 函数 |
| 时间戳 | `TIMESTAMP` | `TIMESTAMP WITH TIME ZONE` / `TIMESTAMP WITHOUT TIME ZONE` |
| IP 地址 | `VARCHAR(15)` | `INET` 原生类型，支持网段运算 |
| 枚举 | `ENUM('a','b','c')` | `CREATE TYPE xxx AS ENUM (...)` 或直接用 `TEXT` + CHECK |

### 4.3 JSONB vs MySQL JSON：实战区别

PG 的 JSONB 是 PG 的一大杀器。它和 MySQL 的 JSON 有一个关键区别：

| 特性 | MySQL JSON | PostgreSQL JSONB |
|------|-----------|-----------------|
| 存储格式 | 文本（解析慢，查询慢） | 二进制（解析快，查询快） |
| 索引 | 虚拟列 + 普通索引 | GIN 倒排索引（原生支持） |
| 查询操作符 | `JSON_EXTRACT(col, '$.key')` | `col->>'key'`（更简洁） |
| 包含查询 | ❌ 不原生支持 | `col @> '{"key": "val"}'` |
| 字段更新 | 较复杂 | `jsonb_set()` 函数 |

---

## 五、窗口函数：PG 更丰富

MySQL 8.0 开始支持窗口函数，但 PG 的窗口函数更丰富、更灵活。

```sql
-- 准备工作：销售数据
CREATE TABLE sales (
    sale_date DATE,
    region TEXT,
    amount NUMERIC
);

INSERT INTO sales VALUES
('2026-01-01', '华北', 1000),
('2026-01-02', '华北', 1200),
('2026-01-03', '华北', 900),
('2026-01-01', '华南', 800),
('2026-01-02', '华南', 1100);

-- === 基础窗口函数（MySQL 8.0 也支持） ===
SELECT region, sale_date, amount,
       ROW_NUMBER() OVER (PARTITION BY region ORDER BY sale_date) AS row_num,
       SUM(amount) OVER (PARTITION BY region ORDER BY sale_date) AS running_total
FROM sales;

-- === PG 特有的窗口函数 ===

-- 1. range/rows 模式更灵活
-- RANGE BETWEEN：按值范围，ROWS BETWEEN：按行数
SELECT sale_date, amount,
       -- 包括当前行及前后 1 天的行
       AVG(amount) OVER (ORDER BY sale_date RANGE BETWEEN INTERVAL '1 day' PRECEDING 
                         AND INTERVAL '1 day' FOLLOWING) AS moving_avg
FROM sales;

-- 2. FILTER 子句在窗口函数中
SELECT region, 
       SUM(amount) FILTER (WHERE amount > 900) OVER (PARTITION BY region) AS high_value_total
FROM sales;

-- 3. 命名窗口（WINDOW 子句复用定义）
SELECT region, sale_date, amount,
       ROW_NUMBER() OVER w AS row_num,
       SUM(amount) OVER w AS total
FROM sales
WINDOW w AS (PARTITION BY region ORDER BY sale_date);
```

---

## 六、CTE（WITH 子句）：PG 的树形数据利器

**CTE（Common Table Expression，公共表表达式）** *此术语见附录E* 可以理解为"在查询内部定义临时视图"，让复杂查询变得可读。

MySQL 8.0 也支持 CTE，但 PG 的 CTE 支持更早、更成熟，特别是**递归 CTE** 处理树形数据。

```sql
-- === 非递归 CTE（MySQL 和 PG 都支持） ===
WITH recent_orders AS (
    SELECT * FROM orders WHERE created_at > CURRENT_DATE - INTERVAL '7 days'
),
order_summary AS (
    SELECT customer_id, SUM(amount) AS total_amount
    FROM recent_orders
    GROUP BY customer_id
)
SELECT c.name, os.total_amount
FROM customers c
JOIN order_summary os ON c.id = os.customer_id
ORDER BY os.total_amount DESC;

-- === 递归 CTE：处理树形数据（PG 更流畅） ===
-- 场景：组织架构 — 找到某个员工的所有下属（直接+间接）
CREATE TABLE employees (
    id INT PRIMARY KEY,
    name TEXT,
    manager_id INT  -- 上级的 id
);

INSERT INTO employees VALUES
(1, 'CEO', NULL),
(2, 'CTO', 1),
(3, 'CFO', 1),
(4, '开发经理', 2),
(5, '开发工程师A', 4),
(6, '开发工程师B', 4),
(7, '会计', 3);

-- 递归查询：找到 CTO（id=2）的所有下属
WITH RECURSIVE subordinates AS (
    -- 基础情况：CTO 的直接下属
    SELECT id, name, manager_id, 1 AS level
    FROM employees
    WHERE manager_id = 2
    
    UNION ALL
    
    -- 递归：下属的下属
    SELECT e.id, e.name, e.manager_id, s.level + 1
    FROM employees e
    JOIN subordinates s ON e.manager_id = s.id
)
SELECT id, name, level, 
       REPEAT('  ', level - 1) || name AS tree_view
FROM subordinates
ORDER BY level, id;
```

输出示例：
```
id | name       | level | tree_view
---+------------+-------+------------------
2  | CTO        | 1     | CTO
4  | 开发经理    | 2     |   开发经理
5  | 开发工程师A | 3     |     开发工程师A
6  | 开发工程师B | 3     |     开发工程师B
```

**想多一点**：MySQL 8.0 也支持递归 CTE 了，语法几乎一样。但 PG 的递归 CTE 有更多优化，而且在 PG 社区里递归 CTE 是处理树形数据的"标准做法"。在 MySQL 社区，你更常看到"闭包表"（closure table）的方案。

---

## 七、全文搜索：PG 内置即用

MySQL 的全文搜索（MyISAM 或 InnoDB 5.6+）功能有限，中文支持尤其弱。PG 的全文搜索内置且功能完整。

```sql
-- === PG 全文搜索 ===

-- 1. 创建全文搜索索引（GIN）
CREATE TABLE articles (
    id SERIAL PRIMARY KEY,
    title TEXT,
    body TEXT,
    -- tsvector 是全文搜索的预处理结果列
    search_vector TSVECTOR GENERATED ALWAYS AS (
        setweight(to_tsvector('english', coalesce(title, '')), 'A') ||
        setweight(to_tsvector('english', coalesce(body, '')), 'B')
    ) STORED
);

CREATE INDEX idx_search ON articles USING GIN(search_vector);

-- 2. 全文搜索
SELECT title, 
       ts_rank(search_vector, query) AS rank
FROM articles, 
     plainto_tsquery('english', 'database performance') AS query
WHERE search_vector @@ query
ORDER BY rank DESC;

-- 3. 中文支持（需要安装 zhparser 扩展）
-- CREATE EXTENSION zhparser;
-- CREATE TEXT SEARCH CONFIGURATION chinese (PARSER = zhparser);
-- ALTER TEXT SEARCH CONFIGURATION chinese ADD MAPPING FOR n,v,a,i,e WITH simple;
```

| 特性 | MySQL 全文搜索 | PostgreSQL 全文搜索 |
|------|---------------|-------------------|
| 内置支持 | InnoDB 5.6+ / MyISAM | 所有版本内置 |
| 索引类型 | FULLTEXT 索引 | GIN 倒排索引 |
| 排名 | 有限 | `ts_rank` 支持权重设置 |
| 词典/分词 | 有限 | 可配置词典、同义词、停用词 |
| 中文 | 需要 NGRAM 解析器 | zhparser 扩展或 jieba |
| 多语言混合 | 困难 | 每条记录可指定不同语言配置 |

---

## 八、索引类型：PG 的 GIN、GiST、BRIN

MySQL 的主流索引类型是 B+Tree 和 FULLTEXT。PG 除此之外还有三种"特种部队"级别的索引。

### 8.1 GIN 索引（倒排索引）

**GIN（Generalized Inverted Index）** *此术语见附录E* 适用于"一个键对应多个值"的场景。

```sql
-- GIN 适用场景
-- 1. JSONB 字段查询
CREATE INDEX idx_profile ON user_profiles USING GIN(profile);

-- 2. 全文搜索
CREATE INDEX idx_search ON articles USING GIN(search_vector);

-- 3. 数组查询
CREATE INDEX idx_tags ON products USING GIN(tags);

-- 4. 查询 JSON 中是否包含某键值
SELECT * FROM user_profiles WHERE profile @> '{"role": "admin"}';
```

### 8.2 GiST 索引（通用搜索树）

**GiST（Generalized Search Tree）** *此术语见附录E* 是一种平衡树结构的"框架"，可以定制用于不同场景。

```sql
-- 1. 地理位置查询（PostGIS 扩展的基础）
CREATE EXTENSION postgis;
CREATE INDEX idx_location ON locations USING GIST(geom);

-- 2. 全文搜索（另一种选择）
CREATE INDEX idx_title_gist ON articles USING GIST(to_tsvector('english', title));

-- 3. 范围类型查询（时间范围、数值范围等）
CREATE TABLE room_bookings (
    room_id INT,
    during DATERANGE  -- PG 的范围类型
);
CREATE INDEX idx_booking ON room_bookings USING GIST(during);

-- 查询某段时间内的预订
SELECT * FROM room_bookings 
WHERE during && '[2026-01-01, 2026-01-07)'::DATERANGE;
```

### 8.3 BRIN 索引（块范围索引）

**BRIN（Block Range Index）** *此术语见附录E* 是 PG 特有的一种"极轻量"索引，适合**超大表且数据物理有序**的场景。

```sql
-- 非常适合作审计日志、IoT 时间序列数据
CREATE TABLE iot_readings (
    device_id INT,
    recorded_at TIMESTAMP,
    temperature NUMERIC
);

-- BRIN 索引：极小（传统 B+Tree 索引的 1/1000 大小）
CREATE INDEX idx_time ON iot_readings USING BRIN(recorded_at);

-- 查询：扫描范围极小
SELECT * FROM iot_readings 
WHERE recorded_at BETWEEN '2026-01-01' AND '2026-01-02';
```

| 索引类型 | 原理 | 适合场景 | 索引大小 | PG 独有 |
|---------|------|---------|---------|--------|
| B+Tree | 经典平衡树 | 等值、范围查询 | 中等 | 否，MySQL 也有 |
| Hash | 哈希表 | 等值查询 | 小 | MySQL MEMORY 引擎有 |
| GIN | 倒排索引 | JSONB、数组、全文搜索 | 大 | **是** |
| GiST | 通用搜索树 | 地理位置、范围类型 | 中等 | **是** |
| BRIN | 块范围摘要 | 超大表、物理有序的数据 | 极小 | **是** |
| 部分索引 | WHERE 条件过滤 | 只索引部分数据 | 小 | MySQL 不支持 |

---

## 九、选型建议速查表

### 9.1 选 PG 不选 MySQL 的场景

| 场景 | 为什么选 PG | PG 的哪个特性决定的 |
|------|-----------|-------------------|
| 需要复杂 JSON 查询和更新 | JSONB + GIN 索引比 MySQL JSON 强太多 | JSONB 类型 + GIN 索引 |
| 地理信息系统（GIS） | PostGIS 扩展是事实标准 | GiST 索引 + PostGIS |
| 需要数组、UUID、IP 等特殊类型 | 原生支持，不需要"凑合" | 丰富的数据类型 |
| 严格的数据完整性要求 | CHECK 约束更强大、类型更严格 | 严格类型系统 |
| 复杂分析查询 | 窗口函数更丰富、CTE 更成熟 | 窗口函数 + 递归 CTE |
| 全文搜索需求 | 内置全文搜索质量高 | 全文搜索 + GIN 索引 |
| 时序数据（海量、有序写入） | BRIN 索引极省空间 | BRIN 索引 |
| 对 SQL 标准合规要求高 | PG 极高标准兼容 | 设计哲学 |

### 9.2 选 MySQL 不选 PG 的场景

| 场景 | 为什么选 MySQL | MySQL 的哪个特性决定的 |
|------|--------------|---------------------|
| 简单 CRUD 为主的 Web 应用 | MySQL 更简单、资源更少 | 线程模型连接开销小 |
| 团队主要熟悉 MySQL | 学习成本考虑 | 社区生态 |
| 需要成熟的云服务支持 | AWS RDS/Aurora、阿里云 RDS 对 MySQL 支持更好 | 云生态 |
| 读多写少的简单场景 | MyISAM 引擎的读性能 | 存储引擎可插拔 |
| 需要大量物理机部署 | MySQL 运维人力更充足 | 社区生态和人才市场 |
| 中小团队快速开发 | 上手快，坑少 | 设计哲学 |

---

## 十、快速上手：PG 安装 + 前 10 条 SQL

### 10.1 安装 PostgreSQL

```bash
# Windows（下载安装器或 Docker）
docker run --name pg-local -e POSTGRES_PASSWORD=your_password_here -p 5432:5432 -d postgres:16

# macOS
brew install postgresql@16
brew services start postgresql@16

# Linux (Ubuntu/Debian)
sudo apt update && sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
```

连接：
```bash
# 默认用户 postgres 没有密码（本地信任认证）
psql -U postgres

# 或通过 Docker
docker exec -it pg-local psql -U postgres
```

### 10.2 前 10 条 SQL：与 MySQL 对照

```sql
-- 1. 查看所有数据库
-- MySQL: SHOW DATABASES;
SELECT datname FROM pg_database;
-- 或者 PG 的快捷命令：\l

-- 2. 创建数据库
-- MySQL: CREATE DATABASE mydb;
CREATE DATABASE mydb;
-- 切换数据库：\c mydb

-- 3. 查看所有表
-- MySQL: SHOW TABLES;
SELECT tablename FROM pg_tables WHERE schemaname = 'public';
-- 或者：\dt

-- 4. 创建表
-- MySQL: CREATE TABLE users (id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(100));
CREATE TABLE users (
    id SERIAL PRIMARY KEY,      -- SERIAL = 自增
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 5. 插入数据
-- MySQL: INSERT INTO users (name, email) VALUES ('alice', 'alice@example.com');
INSERT INTO users (name, email) VALUES ('alice', 'alice@example.com');

-- 6. 查询
-- MySQL: SELECT * FROM users;
SELECT * FROM users;

-- 7. 更新
-- MySQL: UPDATE users SET name = 'Alice Smith' WHERE id = 1;
UPDATE users SET name = 'Alice Smith' WHERE id = 1;

-- 8. 删除
-- MySQL: DELETE FROM users WHERE id = 1;
DELETE FROM users WHERE id = 1;

-- 9. 创建索引
-- MySQL: CREATE INDEX idx_name ON users (name);
CREATE INDEX idx_name ON users (name);

-- 10. 查看表结构
-- MySQL: DESCRIBE users; 或 SHOW CREATE TABLE users;
\d users
```

### 10.3 语法差异速查：MySQL → PG

| 操作 | MySQL 写法 | PostgreSQL 写法 |
|------|-----------|----------------|
| 自增主键 | `INT AUTO_INCREMENT` | `SERIAL` 或 `GENERATED ALWAYS AS IDENTITY` |
| 字符串引用 | 单双引号都行，反引号标识符 | 单引号字符串，双引号标识符 |
| 分页 | `LIMIT 10 OFFSET 0` | `LIMIT 10 OFFSET 0`（相同） |
| 获取当前时间 | `NOW()` | `NOW()` 或 `CURRENT_TIMESTAMP` |
| 字符串拼接 | `CONCAT(a, b)` | `CONCAT(a, b)` 或 `a \|\| b` |
| 正则匹配 | `REGEXP` | `~` （如 `WHERE name ~ '^A'`） |
| 布尔值 | `TINYINT(1)` | `BOOLEAN`（直接 `WHERE is_active`） |
| 注释 | `-- comment` 或 `/* */` | 相同 |
| 修改表 | `ALTER TABLE t MODIFY COLUMN c TYPE` | `ALTER TABLE t ALTER COLUMN c TYPE ...` |

---

## 十一、验证方法

### 验证 1：说出 3 个选 PG 不选 MySQL 的场景

不需要翻书，凭自己的理解说出：
1. 第一个场景：____（提示：JSON）
2. 第二个场景：____（提示：地理位置）
3. 第三个场景：____（提示：数据一致性）

如果能说出来且理由正确，本章的核心目标就达到了。

### 验证 2：在 PG 中完成一次递归 CTE

使用上面的 employee 表数据，写出"找到 CEO 的所有直接和间接下属，按层级排序"的 SQL。

### 验证 3：区分引号

能回答：PG 中 `'hello'` 和 `"hello"` 的区别是什么？

---

## 十二、常见错误

### 错误 1：以为 PG 和 MySQL 语法完全一样

**现象**：把 MySQL 的 SQL 直接搬到 PG 执行，各种报错。

❌ **示例**：
```sql
-- 这条 MySQL SQL 在 PG 里全错
CREATE TABLE users (
    id INT AUTO_INCREMENT,    -- PG 不支持 AUTO_INCREMENT
    name VARCHAR(100),
    `desc` TEXT               -- PG 不支持反引号
) ENGINE=InnoDB;              -- PG 没有 ENGINE 概念
```

✅ **正确**：
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    "desc" TEXT               -- 双引号标识符（如果真要用 desc 这个保留字名）
);
```

### 错误 2：PG 里用反引号

**现象**：MySQL 习惯带到 PG。

❌ **错误**：`SELECT `name` FROM `users`;`
✅ **正确**：`SELECT name FROM users;` 或 `SELECT "name" FROM "users";`

### 错误 3：忘了 VACUUM

**现象**：PG 表越来越大，查询越来越慢，磁盘快满了。

**原因**：长期没有 VACUUM，死行堆积。虽然 autovacuum 自动运行，但在大批量 DELETE/UPDATE 后，或长事务阻塞 autovacuum 时，需要关注。

```sql
-- 检查死行比例
SELECT relname, n_dead_tup, n_live_tup,
       round(n_dead_tup * 100.0 / NULLIF(n_live_tup + n_dead_tup, 0), 2) AS dead_pct
FROM pg_stat_user_tables
ORDER BY n_dead_tup DESC;

-- 手动 VACUUM
VACUUM VERBOSE tablename;
```

### 错误 4：不用连接池直连 PG

**现象**：应用直连 300 个 PG 连接，每个连接 fork 一个进程，内存爆炸，性能下降。

✅ **解决**：在应用和 PG 之间放 PgBouncer（轻量连接池），把 300 个应用连接收敛到 30-50 个实际 PG 连接。

```ini
# pgbouncer.ini 示例
[databases]
mydb = host=localhost port=5432 dbname=mydb

[pgbouncer]
pool_mode = transaction   # 推荐：事务级连接复用
max_client_conn = 500     # 允许 500 个应用连接
default_pool_size = 30    # 30 个实际 PG 连接
```

---

## 本章小结

| 本章学了什么 | 对应命令/概念 | 注意事项 |
|-------------|-------------|---------|
| 思维转换 | PG 严格区分单引号（字符串）和双引号（标识符） | 别再写反引号了 |
| 进程 vs 线程 | PG fork 进程，MySQL 线程 | PG 必须用连接池 |
| MVCC 差异 | PG 无 undo log，死行在表中，VACUUM 清理 | 注意长事务阻塞 VACUUM |
| VACUUM | `VACUUM tablename;` | autovacuum 自动运行但需关注 |
| 数组 | `TEXT[]`, `INT[]` | MySQL 不支持原生数组 |
| JSONB | `@>` 包含查询，`->>'key'` 提取字段 | 比 MySQL JSON 强 |
| UUID | `UUID` 类型 + `gen_random_uuid()` | 不用 CHAR(36) 凑合了 |
| 窗口函数 | `FILTER` 子句、命名窗口 | PG 比 MySQL 8.0 更丰富 |
| 递归 CTE | `WITH RECURSIVE ... UNION ALL ...` | 树形数据首选方案 |
| 全文搜索 | `tsvector` + GIN 索引 | 比 MySQL 全文搜索强 |
| GIN 索引 | `USING GIN(...)` | JSONB、数组、全文搜索 |
| GiST 索引 | `USING GIST(...)` | 地理位置、范围类型 |
| BRIN 索引 | `USING BRIN(...)` | 超大表、时序数据 |
| SQL 语法差异 | 见 10.3 速查表 | AUTO_INCREMENT → SERIAL，MODIFY → ALTER COLUMN TYPE |
| 连接池 | PgBouncer | PG 部署必须带连接池 |
| 选型建议 | 看场景选数据库，不是看谁火 | MySQL 适合简单 CRUD，PG 适合复杂查询 |

---

## 最可能出错的地方及原因

1. **反引号和双引号**：MySQL 用户习惯反引号 `` ` `` 引用标识符，转到 PG 后反引号报错，原因是 PG 不使用反引号语法。
2. **忘了连接池**：从 MySQL 转 PG 最常见的性能问题——直连 500 个连接，每个 fork 进程占 5-10MB，内存直接爆炸，原因是 MySQL 的线程模型没有这个痛点，转 PG 后没想到连接开销这么大。
3. **JSONB 查询语法记不住**：PG 的 `->`, `->>`, `@>`, `?` 操作符和 MySQL 的 `JSON_EXTRACT()` 完全不同，原因是 PG 用操作符代替函数。
4. **VACUUM 概念缺失**：MySQL 没有 VACUUM 概念，转到 PG 后不理解为什么表膨胀，原因是 MySQL 的 purge 线程是后台自动的，PG 也有 autovacuum 但需要知道它存在。
5. **AUTO_INCREMENT → SERIAL**：建表语句失效，原因是两个数据库对自增列的实现语法不同，PG 的 SERIAL 本质上是通过序列（SEQUENCE）实现的。