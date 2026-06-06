# 第52章 · SQL进阶：查询与聚合

> "数据存进去了，早晚要拿出来看。SELECT是SQL中使用频率最高、花样最多的命令——没有之一。你可以把它想象成一个超级搜索引擎，输入条件，它就能从几百万条数据里精准捞出你想要的结果。后端工程师60%的工作本质上就是写SELECT。"

---

## 52.1 SELECT基础

### 查所有字段

```sql
SELECT * FROM users;
```

`*` 表示所有列。这条语句会返回users表的所有行、所有列。

**面试陷阱**：生产代码中**不要用 `SELECT *`**，原因有三：
1. 你不知道表未来会不会加新字段，返回的数据量可能暴涨。
2. 数据库需要去元数据表查有哪些字段，多一步开销。
3. 你拿到的字段顺序依赖于建表顺序，代码解耦性差。

**正确做法**：明确列出需要的字段。

```sql
SELECT id, username, email, created_at FROM users;
```

### 别名（AS）

```sql
SELECT
    id       AS 用户ID,
    username AS 用户名,
    email    AS 邮箱
FROM users;
```

`AS` 给字段起别名，让查询结果更可读。AS可以省略，但不建议——可读性差：

```sql
SELECT id user_id, username name FROM users;
```

虽然能跑，但读代码的人分不清 `id` 和 `user_id` 的关系。

### 计算字段

SELECT不仅可以查已有字段，还能做计算：

```sql
SELECT
    username,
    balance,
    balance * 0.01 AS points
FROM users;
```

假设每1元余额兑1积分，直接算出来。

### 函数处理字段

```sql
SELECT
    username,
    UPPER(email)    AS email_upper,
    CHAR_LENGTH(username) AS name_len,
    DATE(created_at) AS register_date
FROM users;
```

常用函数：
- `UPPER()` / `LOWER()`：转大小写
- `CHAR_LENGTH()`：字符数（中文一个字算1）
- `LENGTH()`：字节数（中文一个字通常3字节）
- `CONCAT()`：拼接字符串
- `DATE()`：提取日期部分
- `YEAR()` / `MONTH()` / `DAY()`：提取年月日
- `NOW()`：当前时间

---

## 52.2 WHERE：条件筛选

WHERE是SELECT的灵魂。不加WHERE的SELECT等于说"全给我拿出来"——这在生产环境中很危险，可能把全表几十万行全拉出来，内存直接爆。

### 比较运算符

```sql
SELECT * FROM users WHERE age > 18;
SELECT * FROM users WHERE age >= 30;
SELECT * FROM users WHERE age = 25;
SELECT * FROM users WHERE age <> 25;
SELECT * FROM users WHERE username = 'zhangsan';
```

**注意**：MySQL中 `<>` 和 `!=` 都表示"不等于"，但 `<>` 是SQL标准写法，考试和面试时写 `<>`。

### BETWEEN ... AND ...

```sql
SELECT * FROM users WHERE age BETWEEN 20 AND 30;
```

等价于 `age >= 20 AND age <= 30`。**注意BETWEEN是闭区间**，包含边界值。

### IN

```sql
SELECT * FROM users WHERE id IN (1, 3, 5, 7, 9);
```

等价于 `id = 1 OR id = 3 OR id = 5 OR ...`，但更简洁且优化器能更好地处理。

### IS NULL / IS NOT NULL

```sql
SELECT * FROM users WHERE phone IS NULL;
SELECT * FROM users WHERE phone IS NOT NULL;
```

**面试重点**：判断NULL不能写 `phone = NULL`！因为NULL表示"未知"，两个未知值无法比较。`NULL = NULL` 的结果不是TRUE，而是NULL（未知）。这是SQL新手最容易踩的坑。

### LIKE：模糊匹配

```sql
SELECT * FROM users WHERE username LIKE 'zhang%';
```

`%` 匹配任意多个字符（包括0个）。`zhang%` 表示以"zhang"开头的所有值。

```sql
SELECT * FROM users WHERE username LIKE '%san';
```

以"san"结尾。

```sql
SELECT * FROM users WHERE username LIKE '%zhang%';
```

包含"zhang"（不推荐——没法用索引，后面会讲）。

**`_` 匹配单个字符**：

```sql
SELECT * FROM users WHERE phone LIKE '138________';
```

11位手机号中，138开头、后面8位任意的。`_` 占一个字符的位置。

### AND / OR 组合条件

```sql
SELECT * FROM users
WHERE age >= 18
  AND is_active = 1
  AND (email LIKE '%@gmail.com' OR email LIKE '%@qq.com');
```

**注意括号**：AND的优先级高于OR。不加括号的话 `a AND b OR c` 等于 `(a AND b) OR c`，通常不是你想要的。

---

## 52.3 ORDER BY：排序

```sql
SELECT * FROM users ORDER BY age ASC;
```

- `ASC`（ascending）：升序，从小到大。**默认值**，可以不写。
- `DESC`（descending）：降序，从大到小。

```sql
SELECT * FROM users ORDER BY balance DESC;
```

按余额从高到低。

### 多字段排序

```sql
SELECT * FROM users ORDER BY age DESC, balance ASC;
```

先按年龄降序，年龄相同的再按余额升序。**排前面的是主排序，后面的是"平局决胜"条件**。

### 按别名排序

```sql
SELECT
    balance * 0.01 AS points
FROM users
ORDER BY points DESC;
```

可以用别名排序——这在MySQL中合法（但ANSI SQL标准不允许，Oracle就不支持）。

---

## 52.4 LIMIT：分页

```sql
SELECT * FROM users ORDER BY id LIMIT 10;
```

只返回前10行。

```sql
SELECT * FROM users ORDER BY id LIMIT 10 OFFSET 20;
```

跳过前20行，取接下来的10行——即第21~30行。

**分页公式**：
- 第N页：`LIMIT page_size OFFSET (N - 1) * page_size`
- 第1页：`LIMIT 10 OFFSET 0`
- 第2页：`LIMIT 10 OFFSET 10`
- 第3页：`LIMIT 10 OFFSET 20`

### MySQL特有写法

```sql
SELECT * FROM users ORDER BY id LIMIT 20, 10;
```

等同于 `LIMIT 10 OFFSET 20`。注意参数顺序是反的——最迷惑的地方。推荐用标准写法 LIMIT ... OFFSET ...，更清晰。

### 深分页问题

```sql
SELECT * FROM users ORDER BY id LIMIT 10 OFFSET 1000000;
```

这条SQL要扫描前100万行再丢弃，才能给你10行——非常慢！解决方案在第58章详细讲。

🤔 **想多一点**：很多APP的"上拉加载更多"做到第几十页就很卡了，就是因为OFFSET太大。优化方案通常是**游标分页**（记录最后一行的id，下次用 `WHERE id > last_id LIMIT 10`），或者限制最大翻页数。

---

## 52.5 DISTINCT：去重

```sql
SELECT DISTINCT age FROM users;
```

返回所有不重复的年龄值。比如users表中有3个25岁、5个30岁，结果只返回25和30各一行。

```sql
SELECT DISTINCT age, city FROM users;
```

返回所有不重复的(年龄, 城市)组合。DISTINCT作用于所有选中的列。

---

## 52.6 聚合函数

聚合函数对一组值进行计算，返回单个值。

### COUNT：计数

```sql
SELECT COUNT(*) FROM users;
```

返回总行数。**注意**：`COUNT(*)` 统计所有行（包括NULL），`COUNT(字段名)` 只统计该字段不为NULL的行。

```sql
SELECT COUNT(phone) FROM users;
```

只统计phone不为NULL的行数。如果10个用户中有3个没填手机号，结果就是7。

```sql
SELECT COUNT(DISTINCT age) FROM users;
```

统计不重复的年龄有多少种。

### SUM：求和

```sql
SELECT SUM(balance) FROM users;
```

所有用户余额的总和。

### AVG：平均值

```sql
SELECT AVG(age) FROM users;
```

所有用户的平均年龄。

### MAX / MIN：最大值 / 最小值

```sql
SELECT MAX(balance) FROM users;
SELECT MIN(age) FROM users;
```

```sql
SELECT username, MAX(balance) FROM users;
```

**警告**：这条SQL在大多数数据库中是**非法的**。username返回哪一行是不确定的——MySQL可能返回任意一行，PostgreSQL直接报错。聚合查询中SELECT的字段要么在GROUP BY中，要么被聚合函数包裹。

---

## 52.7 GROUP BY：分组

GROUP BY把数据按某一列分成多组，然后每组独立计算聚合值。

```sql
SELECT
    age,
    COUNT(*) AS user_count
FROM users
GROUP BY age;
```

按年龄分组，统计每个年龄段有多少用户。结果：

```
+-----+------------+
| age | user_count |
+-----+------------+
|  18 |          5 |
|  20 |         12 |
|  25 |         20 |
|  30 |          8 |
+-----+------------+
```

### 多字段分组

```sql
SELECT
    age,
    city,
    COUNT(*) AS cnt
FROM users
GROUP BY age, city;
```

按年龄和城市联合分组。25岁北京的和25岁上海的是两个不同的组。

### HAVING：过滤分组

WHERE过滤的是**行**（在分组前进行），HAVING过滤的是**分组**（在分组后进行）。

```sql
SELECT
    age,
    COUNT(*) AS cnt
FROM users
GROUP BY age
HAVING cnt > 10;
```

只返回用户数大于10的年龄段。

WHERE和HAVING配合使用：

```sql
SELECT
    age,
    COUNT(*) AS cnt,
    AVG(balance) AS avg_balance
FROM users
WHERE is_active = 1
GROUP BY age
HAVING cnt > 10 AND avg_balance > 100;
```

执行顺序：先WHERE筛选激活用户→再GROUP BY分组→再HAVING过滤分组→最后SELECT输出。

**WHERE vs HAVING 对比**：

| | WHERE | HAVING |
|---|-------|--------|
| 过滤阶段 | 分组前 | 分组后 |
| 能引用聚合函数 | 不能 | 能 |
| 性能 | 优（先过滤减少数据量） | 相对差（全量数据已分组） |
| 能用索引 | 能 | 不能 |

> **法则**：能用WHERE过滤的坚决不用HAVING。WHERE在读到数据时就过滤了，HAVING是分组完再过滤，多做了无用功。

🤔 **想多一点**：面试中经常有人混淆WHERE和HAVING。一个简单口诀：WHERE管每一行长什么样，HAVING管每一组最终算出来是多少。

---

## 52.8 子查询

子查询就是SELECT里面套SELECT——先用内层查询的结果作为外层查询的条件。

### WHERE中的子查询

```sql
SELECT username, balance
FROM users
WHERE balance > (SELECT AVG(balance) FROM users);
```

找出余额高于平均值的用户。内层查询先算出平均余额，外层再用这个值做比较。

```sql
SELECT username
FROM users
WHERE id IN (SELECT user_id FROM orders WHERE amount > 1000);
```

找到下单金额超过1000的用户。子查询先找出所有符合条件的user_id，外层再查这些用户的用户名。

### FROM中的子查询（派生表）

```sql
SELECT avg_age
FROM (
    SELECT age, COUNT(*) AS cnt
    FROM users
    GROUP BY age
) AS age_stats
WHERE cnt > 5;
```

先将分组统计结果作为一张虚拟表（派生表），再在它上面查询。**派生表必须有别名**（`AS age_stats`），否则MySQL报错。

### SELECT中的标量子查询

```sql
SELECT
    username,
    balance,
    (SELECT AVG(balance) FROM users) AS avg_all,
    balance - (SELECT AVG(balance) FROM users) AS diff
FROM users;
```

每一行都附带全局平均余额和差值。但这样写两个子查询要执行两次——可以用变量或CTE优化。

### 子查询的性能注意

子查询不是万能的。`WHERE id IN (SELECT ...)` 在MySQL 5.6之前性能极差（因为优化器不会自动优化成JOIN）。MySQL 8.0改善了很多，但复杂的嵌套子查询建议用JOIN或CTE（WITH表达式）替代。第53章会深入讲。

---

## 52.9 UNION：合并结果集

UNION把多个SELECT的结果纵向合并（堆叠行）：

```sql
SELECT username, email FROM users WHERE age < 20
UNION
SELECT username, email FROM users WHERE balance > 10000;
```

把"年龄小于20"和"余额大于10000"的用户合并起来。**UNION会自动去重**——如果同一个用户在两个条件中都出现，只保留一行。

如果不需要去重（性能更好），用 `UNION ALL`：

```sql
SELECT username FROM users WHERE age < 20
UNION ALL
SELECT username FROM users WHERE balance > 10000;
```

### UNION的两个规则

1. 每个SELECT的**列数必须相同**。
2. 对应列的**数据类型必须兼容**。

列的别名以第一个SELECT的为准：

```sql
SELECT username AS name FROM users WHERE age < 20
UNION
SELECT email FROM users WHERE balance > 10000;
```

第二列显示的表头是 `name`（第一个SELECT的别名）。

---

## SQL执行顺序总结

这是一个面试高频考点。下面这条SQL的书写顺序和实际执行顺序是**完全不同的**：

```sql
SELECT age, COUNT(*) AS cnt                -- 5. 选择输出
FROM users                                  -- 1. 确定数据来源
WHERE is_active = 1                         -- 2. 过滤行
GROUP BY age                                -- 3. 分组
HAVING cnt > 10                             -- 4. 过滤分组
ORDER BY cnt DESC                           -- 6. 排序
LIMIT 5;                                    -- 7. 限制行数
```

**实际执行顺序**：FROM → WHERE → GROUP BY → HAVING → SELECT → ORDER BY → LIMIT

这个顺序意味着：你在SELECT中定义的别名（如 `cnt`），不能在WHERE中使用（WHERE先于SELECT执行），但可以在HAVING、ORDER BY中使用（它们在SELECT之后执行）。

---

## 本章小结

| 知识点 | 要点 |
|--------|------|
| SELECT基础 | 明确列出字段不用 `*`，用AS起别名，可做计算和函数处理 |
| WHERE | `=`/`<>`/`BETWEEN`/`IN`/`IS NULL`/`LIKE`(`%`和`_`)/`AND`/`OR` |
| ORDER BY | ASC升序（默认）/DESC降序，多字段按优先级排序 |
| LIMIT | 分页公式：`LIMIT N OFFSET (page-1)*N`，深分页用游标替代 |
| DISTINCT | 对选中列去重，作用在所有列的组合上 |
| 聚合函数 | COUNT/SUM/AVG/MAX/MIN，`COUNT(*)`含NULL，`COUNT(字段)`不含 |
| GROUP BY | 按列分组，每个组独立聚合。多字段分组形成组合键 |
| HAVING | 过滤分组（WHERE过滤行），能引用聚合函数，性能不如WHERE |
| 子查询 | SELECT中套SELECT，三位置：WHERE/FROM/SELECT |
| UNION | 纵向合并结果集，UNION去重、UNION ALL不去重；列数必须相同 |
| 执行顺序 | FROM→WHERE→GROUP BY→HAVING→SELECT→ORDER BY→LIMIT |

> 🚀 下一章：第53章 · JOIN多表查询。数据不可能全挤在一张表里——用户表、订单表、商品表各自独立。JOIN就是这些表之间的"桥梁"，让你能在一句SQL里同时查到"张三"和"张三的所有订单"。这是SQL中最烧脑、也最精彩的部分。

---
[← 上一章：51-SQL基础：DDL与DML](51-SQL基础：DDL与DML/) | [下一章：53-JOIN多表查询 →](53-JOIN多表查询/)
