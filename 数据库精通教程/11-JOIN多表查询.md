# 11 — JOIN 多表查询

> - 对应文档版本：database_mastery_outline.md v1, database_mastery_detailed_outline.md v2
> - 适用环境：MySQL 8.0+，已创建 my_shop 数据库（含 users, orders, order_items, products 四表）
> - 读者角色：已学完第 10b 章子查询的开发者
> - 预计耗时：新手 60 分钟
> - 前置教程：第 04-10b 章
> - 可视化：有，[11-JOIN图解_visual.html](11-JOIN图解_visual.html)

---

## 我在做什么？

到目前为止，你的查询都只涉及一张表。但现实世界的数据分散在多张表中——用户信息在 `users` 表，订单在 `orders` 表，订单明细在 `order_items` 表，商品在 `products` 表。

你想查"Alice 买了哪些商品，每个多少钱"，需要把 4 张表的数据串起来。这就是 **JOIN**（连接查询）*此术语见附录E* 要做的事：**把多张表的数据，按照某种关联条件，拼成一张大表**。

学完这一章，你能写出 4 表联查，理解 JOIN ON 和 WHERE 的本质区别，并用文氏图辅助判断 JOIN 结果。

> 📊 可视化演示见 [11-JOIN图解_visual.html](11-JOIN图解_visual.html) — 通过文氏图和实际数据，逐步展示每种 JOIN 的结果集。

---

## 一、一个比喻：拼图游戏

把多表 JOIN 想象成**拼图**：

- 你有两张表：`users`（用户）和 `orders`（订单）
- 两张表中都有一列 `user_id`（在 users 中是 `id`，在 orders 中是 `user_id`）
- `users.id = orders.user_id` 就是拼图的"接口"——把用户和他们的订单配对

```
users 表：                     orders 表：
┌────┬──────────┐            ┌────┬─────────┬──────────┐
│ id │ username │            │ id │ user_id │ product  │
├────┼──────────┤            ├────┼─────────┼──────────┤
│ 1  │ alice    │            │ 1  │    1    │ iPhone   │
│ 2  │ bob      │            │ 2  │    1    │ iPad     │
│ 3  │ charlie  │            │ 3  │    2    │ MacBook  │
└────┴──────────┘            └────┴─────────┴──────────┘

JOIN 后（INNER JOIN ON users.id = orders.user_id）：
┌────┬──────────┬──────────┐
│ id │ username │ product  │
├────┼──────────┼──────────┤
│ 1  │ alice    │ iPhone   │  ← users.id=1 匹配 orders.user_id=1
│ 1  │ alice    │ iPad     │  ← users.id=1 匹配 orders.user_id=1
│ 2  │ bob      │ MacBook  │  ← users.id=2 匹配 orders.user_id=2
└────┴──────────┴──────────┘
```

注意 **charlie（id=3）没有出现在结果中**，因为 orders 表里没有 `user_id=3` 的订单。这就是 INNER JOIN 的特性——只返回匹配的行。

---

## 二、INNER JOIN：只返回匹配行

**INNER JOIN** *此术语见附录E*（内连接）是最常用的 JOIN 类型。它返回两张表中**同时满足 ON 条件**的行。

### 2.1 基本语法

```sql
SELECT 列名列表
FROM 表A
INNER JOIN 表B ON 表A.某列 = 表B.某列;
```

### 2.2 实战：用户 + 订单

```sql
-- 查"每个订单的编号、用户名、商品名"
SELECT o.id AS order_id, u.username, o.product
FROM orders o
INNER JOIN users u ON o.user_id = u.id;
```

结果：
```
+----------+----------+----------+
| order_id | username | product  |
+----------+----------+----------+
|        1 | alice    | iPhone   |
|        2 | alice    | iPad     |
|        3 | bob      | MacBook  |
+----------+----------+----------+
```

### 2.3 INNER JOIN 的"文氏图"理解

如果把两张表看作两个集合，INNER JOIN 就是**交集**：

```
      ┌───────────────────────────────┐
      │          users                │
      │  ┌─────────┐                 │
      │  │ 匹配的  │                 │
      │  │ 行      │  orders         │
      │  └─────────┘                 │
      │                               │
      └───────────────────────────────┘
      charlie(id=3) 被排除            没有 user_id=3 的订单不受影响
```

> 📊 更直观的文氏图 + 数据示例见 [11-JOIN图解_visual.html](11-JOIN图解_visual.html)

---

## 三、LEFT JOIN：左表全保留

**LEFT JOIN** *此术语见附录E*（左连接）：**左表的所有行都保留**，右表没有匹配的列填 NULL。

### 3.1 基本语法

```sql
SELECT 列名列表
FROM 表A
LEFT JOIN 表B ON 表A.某列 = 表B.某列;
```

### 3.2 实战：查所有用户及其订单

```sql
SELECT u.id, u.username, o.product
FROM users u
LEFT JOIN orders o ON u.id = o.user_id;
```

结果：
```
+----+----------+----------+
| id | username | product  |
+----+----------+----------+
| 1  | alice    | iPhone   |
| 1  | alice    | iPad     |
| 2  | bob      | MacBook  |
| 3  | charlie  | NULL     |  ← charlie 没有订单，product 填 NULL
+----+----------+----------+
```

**关键区别**：`INNER JOIN` 中 charlie 消失了，`LEFT JOIN` 中 charlie 保留了（product 为 NULL）。

### 3.3 利用 LEFT JOIN 找"没有关联"的行

```sql
-- 查"从未下过单的用户"
SELECT u.id, u.username
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
WHERE o.user_id IS NULL;
```

这个写法等价于 `NOT EXISTS`，但有些人觉得 LEFT JOIN + IS NULL 更直观。

---

## 四、RIGHT JOIN：可改写为 LEFT JOIN

**RIGHT JOIN** *此术语见附录E*（右连接）与 LEFT JOIN 相反：**右表全保留**，左表没有匹配的填 NULL。

```sql
-- RIGHT JOIN 写法
SELECT u.username, o.product
FROM users u
RIGHT JOIN orders o ON u.id = o.user_id;

-- 等价于 LEFT JOIN（交换表顺序）
SELECT u.username, o.product
FROM orders o
LEFT JOIN users u ON o.user_id = u.id;
```

**为什么不推荐 RIGHT JOIN？**

- 所有 RIGHT JOIN 都可以用 LEFT JOIN 改写（交换表顺序即可）
- 阅读习惯：人从左往右读，LEFT JOIN 的"主表"在左边，直觉上更自然
- 多表 JOIN 时，LEFT JOIN 和 RIGHT JOIN 混用会让代码难以理解

**我的建议**：统一用 LEFT JOIN，需要 RIGHT JOIN 时交换表顺序。

---

## 五、CROSS JOIN：笛卡尔积（慎用！）

**CROSS JOIN** *此术语见附录E*（交叉连接）：返回两张表的**笛卡尔积**（Cartesian Product）*此术语见附录E*——左表的每一行 × 右表的每一行。

```sql
-- 假设 users 有 3 行，products 有 4 行
SELECT u.username, p.name
FROM users u
CROSS JOIN products p;
-- 结果：3 × 4 = 12 行
```

**笛卡尔积示意**：

```
users: {alice, bob, charlie}
products: {iPhone, iPad, MacBook, AirPods}

CROSS JOIN 结果：
alice  × iPhone
alice  × iPad
alice  × MacBook
alice  × AirPods
bob    × iPhone
bob    × iPad
...    × ...
charlie × AirPods
总共 3 × 4 = 12 行
```

### 什么时候用 CROSS JOIN？

1. **生成测试数据**：需要所有组合（比如"所有用户 × 所有优惠券"）
2. **生成数字序列**：与辅助表配合
3. **意外**：忘记写 ON 条件，INNER JOIN 会退化为 CROSS JOIN！

```sql
-- ❌ 危险！忘记 ON 条件 → 笛卡尔积
SELECT u.username, o.product
FROM users u
INNER JOIN orders o;
-- 如果 users 有 1000 行，orders 有 10000 行 → 1000 万行！

-- ✅ 正确：必须写 ON
SELECT u.username, o.product
FROM users u
INNER JOIN orders o ON u.id = o.user_id;
```

---

## 六、自连接（SELF JOIN）：自己 JOIN 自己

有时候，一张表里的数据需要和自己关联。比如员工表有"上级"字段：

```sql
-- 员工表
CREATE TABLE employees (
    id INT PRIMARY KEY,
    name VARCHAR(50),
    manager_id INT  -- 指向自己的 id（上级是谁）
);

INSERT INTO employees VALUES
(1, '张总',  NULL),    -- 老板，没有上级
(2, '李经理', 1),      -- 上级是张总
(3, '王组长', 2),      -- 上级是李经理
(4, '赵员工', 3);      -- 上级是王组长
```

要查"每个员工和他的上级名字"，需要**自连接**（Self Join）*此术语见附录E*：

```sql
SELECT
    e.name AS employee,
    m.name AS manager
FROM employees e
LEFT JOIN employees m ON e.manager_id = m.id;
```

结果：
```
+----------+----------+
| employee | manager  |
+----------+----------+
| 张总     | NULL     |
| 李经理   | 张总     |
| 王组长   | 李经理   |
| 赵员工   | 王组长   |
+----------+----------+
```

**关键点**：虽然用的是同一张表，但给它起了两个不同的别名（`e` 和 `m`），MySQL 把它当作两张不同的表来处理。

---

## 七、多表 JOIN：3 张以上

现实中的查询往往涉及 3 张以上的表。比如电商场景：

```sql
-- 需求：查"Alice 买了哪些商品，每个多少钱，什么时候买的"
-- 涉及：users → orders → order_items → products（4 张表）

SELECT
    u.username,
    p.name AS product_name,
    oi.quantity,
    oi.price,
    o.created_at
FROM users u
INNER JOIN orders o ON u.id = o.user_id
INNER JOIN order_items oi ON o.id = oi.order_id
INNER JOIN products p ON oi.product_id = p.id
WHERE u.username = 'alice';
```

**执行顺序**：
1. `users INNER JOIN orders` → 得到用户和订单的组合
2. 再 `INNER JOIN order_items` → 加上订单明细
3. 再 `INNER JOIN products` → 加上商品名
4. 最后 WHERE 过滤

就像串联：表A → 表B → 表C → 表D，一步一步把数据拼起来。

---

## 八、JOIN ON vs WHERE 的本质区别（重点！）

这是 JOIN 中最容易踩的坑，也是面试高频考点。

### 8.1 对 INNER JOIN 来说，ON 和 WHERE 效果相同

```sql
-- 写法 A：条件放 ON
SELECT u.username, o.product
FROM users u
INNER JOIN orders o ON u.id = o.user_id AND o.amount > 100;

-- 写法 B：条件放 WHERE
SELECT u.username, o.product
FROM users u
INNER JOIN orders o ON u.id = o.user_id
WHERE o.amount > 100;

-- 两种写法结果相同
```

### 8.2 对 LEFT JOIN 来说，ON 和 WHERE 天差地别！

**ON 中的条件**：影响"哪些行能匹配上"，不匹配的右表列填 NULL。

**WHERE 中的条件**：在 JOIN 完成后，过滤最终结果行。

```sql
-- 假设 users 表有 3 人：alice(有2单), bob(有1单), charlie(0单)
-- orders 表：alice 的订单中有一单 amount=50

-- 写法 A：条件放 ON
SELECT u.username, o.product, o.amount
FROM users u
LEFT JOIN orders o ON u.id = o.user_id AND o.amount > 100;
```

结果（写法 A）：
```
+----------+----------+--------+
| username | product  | amount |
+----------+----------+--------+
| alice    | iPhone   | 300    |  ← amount=300 满足 ON 条件，匹配成功
| alice    | NULL     | NULL   |  ← amount=50 不满足 ON 条件，没匹配上，填 NULL
| bob      | MacBook  | 500    |  ← 满足 ON 条件
| charlie  | NULL     | NULL   |  ← charlie 本来就没订单，填 NULL
+----------+----------+--------+
```

```sql
-- 写法 B：条件放 WHERE
SELECT u.username, o.product, o.amount
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
WHERE o.amount > 100;
```

结果（写法 B）：
```
+----------+----------+--------+
| username | product  | amount |
+----------+----------+--------+
| alice    | iPhone   | 300    |
| bob      | MacBook  | 500    |
+----------+----------+--------+
```

**charlie 消失了！** 因为：
1. LEFT JOIN 后 charlie 的 `o.amount` 是 NULL
2. `WHERE o.amount > 100` → `NULL > 100` → 不是 TRUE → 被过滤掉

**关键结论**：
- **ON 是"匹配规则"**：决定哪些行能配对
- **WHERE 是"过滤规则"**：在最终结果上过滤
- 在 LEFT JOIN 中，对右表的过滤条件放 ON 还是 WHERE，结果完全不同

### 8.3 实战案例：统计"每个用户的高额订单数"

```sql
-- 需求：统计每个用户的总订单数，以及其中"金额 > 500"的订单数

-- ✅ 正确写法：高额订单条件放 ON（保证 LEFT JOIN 保留所有用户）
SELECT
    u.username,
    COUNT(o.id) AS total_orders,
    COUNT(o2.id) AS high_value_orders
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
LEFT JOIN orders o2 ON u.id = o2.user_id AND o2.amount > 500
GROUP BY u.id, u.username;
```

> **想多一点**：ON 和 WHERE 的区别，本质上是 **SQL 执行顺序**的问题。回顾第 09 章的执行顺序图：`FROM → ON → JOIN → WHERE → GROUP BY → HAVING → SELECT → ORDER BY → LIMIT`。ON 在 JOIN 阶段起作用，WHERE 在 JOIN 之后起作用。这个顺序图是理解 JOIN 所有行为的总钥匙。

---

## 我做得对不对？

### 验证方法

请在你的 `my_shop` 数据库中执行以下验证。**在纸上画好各表的数据，手动计算 JOIN 后应该有多少行，再和 SQL 结果对比**。

```sql
-- 1. 确认环境
USE my_shop;
SELECT COUNT(*) FROM users;      -- 记下：N 行
SELECT COUNT(*) FROM orders;     -- 记下：M 行
SELECT COUNT(*) FROM order_items; -- 记下：P 行
SELECT COUNT(*) FROM products;   -- 记下：Q 行

-- 2. INNER JOIN：users + orders
-- 手动计算：orders 表中有多少行 user_id 在 users 表中存在？
SELECT COUNT(*) FROM users u
INNER JOIN orders o ON u.id = o.user_id;
-- 预期：= orders 表中 user_id 不为 NULL 且存在于 users 中的行数

-- 3. LEFT JOIN：users + orders
SELECT COUNT(*) FROM users u
LEFT JOIN orders o ON u.id = o.user_id;
-- 预期：≥ orders 表的行数（每个用户至少一条，有订单的用户可能多行）

-- 4. LEFT JOIN 找没有订单的用户
SELECT u.id, u.username FROM users u
LEFT JOIN orders o ON u.id = o.user_id
WHERE o.id IS NULL;
-- 预期：返回那些 id 在 users 中但不在 orders.user_id 中的用户

-- 5. 验证 ON vs WHERE 的区别
-- 先看所有用户和订单
SELECT u.username, o.amount FROM users u
LEFT JOIN orders o ON u.id = o.user_id;
-- 观察：没有订单的用户，amount 是 NULL

-- 然后看加上 WHERE 过滤的效果
SELECT u.username, o.amount FROM users u
LEFT JOIN orders o ON u.id = o.user_id
WHERE o.amount > 200;
-- 观察：没有订单的用户（amount=NULL）消失了！

-- 6. 多表 JOIN：4 表联查
SELECT
    u.username,
    p.name AS product_name,
    oi.quantity,
    oi.price,
    o.created_at
FROM users u
INNER JOIN orders o ON u.id = o.user_id
INNER JOIN order_items oi ON o.id = oi.order_id
INNER JOIN products p ON oi.product_id = p.id
LIMIT 10;
-- 验证：每行的 username、product_name 都能在原表中找到对应
```

---

## 不对怎么办？

### 常见错误 1：LEFT JOIN 时把右表过滤条件写在了 WHERE

```sql
-- ❌ 错误：WHERE 过滤掉了没有订单的用户
SELECT u.username, o.product
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
WHERE o.amount > 100;
-- 没有订单的用户（amount=NULL）被过滤掉了

-- ✅ 正确：右表过滤条件放 ON
SELECT u.username, o.product
FROM users u
LEFT JOIN orders o ON u.id = o.user_id AND o.amount > 100;
-- 没有订单的用户保留，product 为 NULL
```

### 常见错误 2：忘记 ON 条件，导致笛卡尔积

```sql
-- ❌ 错误：INNER JOIN 没写 ON
SELECT u.username, o.product
FROM users u
INNER JOIN orders o;
-- 结果：users行数 × orders行数，可能几百万行，数据库卡死

-- ✅ 正确：必须写 ON
SELECT u.username, o.product
FROM users u
INNER JOIN orders o ON u.id = o.user_id;
```

### 常见错误 3：多表 JOIN 时列名歧义

```sql
-- ❌ 错误：id 列在两张表中都存在，MySQL 不知道用哪个
SELECT id, username, product
FROM users u
INNER JOIN orders o ON u.id = o.user_id;
-- ERROR 1052 (23000): Column 'id' in field list is ambiguous

-- ✅ 正确：用表别名显式指定
SELECT u.id, u.username, o.product
FROM users u
INNER JOIN orders o ON u.id = o.user_id;
```

### 常见错误 4：LEFT JOIN 后用 INNER JOIN 可能导致数据丢失

```sql
-- ❌ 注意：LEFT JOIN 后再 INNER JOIN，可能丢失左表的 NULL 行
SELECT u.username, p.name
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
INNER JOIN products p ON o.product_id = p.id;
-- 如果 charlie 没有订单，orders 行全是 NULL
-- INNER JOIN products 时 NULL 无法匹配 → charlie 消失

-- ✅ 如果想保留所有用户，后续 JOIN 也要用 LEFT JOIN
SELECT u.username, p.name
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
LEFT JOIN products p ON o.product_id = p.id;
```

---

## 本章小结

| 本章学了什么 | 对应命令/概念 | 注意事项 |
|-------------|-------------|---------|
| INNER JOIN | `FROM A INNER JOIN B ON A.x = B.y` | 只返回匹配行；不匹配的双方都丢弃 |
| LEFT JOIN | `FROM A LEFT JOIN B ON A.x = B.y` | 左表全保留；右表无匹配填 NULL |
| RIGHT JOIN | `FROM A RIGHT JOIN B ON ...` | 不推荐，交换表顺序改用 LEFT JOIN |
| CROSS JOIN | `FROM A CROSS JOIN B` | 笛卡尔积，慎用！忘记 ON 时 INNER JOIN 会退化为 CROSS JOIN |
| 自连接（SELF JOIN） | 同一张表用两个别名 JOIN 自己 | 典型场景：员工表找上级、分类找父分类 |
| 多表 JOIN | 3+ 表串联 JOIN | 列名歧义用表别名（`u.id`）；注意 JOIN 顺序 |
| JOIN ON vs WHERE | ON 是匹配规则，WHERE 是过滤规则 | LEFT JOIN 中二者区别巨大：ON 影响匹配，WHERE 过滤最终结果 |
| LEFT JOIN 找"无关联"行 | `LEFT JOIN ... WHERE right_table.id IS NULL` | 替代 NOT EXISTS 的另一种写法 |