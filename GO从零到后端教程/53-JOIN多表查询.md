# 第53章 · JOIN多表查询

> "现实世界的数据库从来不会把所有数据塞进一张表。用户信息存在users表，订单存在orders表，商品存在products表——分开存放是为了避免数据冗余。但问题来了：你想查'张三的所有订单'，张三在users表里，订单在orders表里，你需要把两张表'连'起来查。JOIN就是这门连接的艺术。"

---

## 53.1 为什么需要多张表

假设你设计一个电商系统，如果只用一张表存所有东西：

```
orders_big_table:
id | username | email           | phone      | product_name | price | order_time
1  | zhangsan | zs@test.com     | 13800001111 | iPhone 15    | 6999  | 2024-01-01
2  | zhangsan | zs@test.com     | 13800001111 | AirPods      | 1299  | 2024-01-03
3  | lisi     | lisi@test.com   | 13900002222 | iPhone 15    | 6999  | 2024-01-05
4  | zhangsan | zs@test.com     | 13800001111 | MacBook      | 9999  | 2024-01-08
```

看到问题了吗？张三的信息（username、email、phone）重复了三次。这会导致：

1. **存储浪费**：同一份信息存三遍。
2. **更新噩梦**：张三换了手机号，你要在三条记录里都改——稍微漏一条就数据不一致。
3. **删除异常**：把第三条记录删了（李四的订单），李四这个用户的信息就彻底消失了。

**正确做法**：拆成两张表：

**users表**：
```
id | username | email          | phone
1  | zhangsan | zs@test.com    | 13800001111
2  | lisi     | lisi@test.com  | 13900002222
```

**orders表**：
```
id | user_id | product_name | price | order_time
1  | 1       | iPhone 15    | 6999  | 2024-01-01
2  | 1       | AirPods      | 1299  | 2024-01-03
3  | 2       | iPhone 15    | 6999  | 2024-01-05
4  | 1       | MacBook      | 9999  | 2024-01-08
```

现在用户信息只存一份。要查"张三的所有订单"，通过 `users.id = orders.user_id` 把两张表"连"起来——这就是JOIN。

---

## 53.2 外键：表与表之间的桥梁

`orders.user_id` 就是外键——它指向 `users.id`，在两张表之间建立关联。

### 外键约束

建表时可以声明外键关系：

```sql
CREATE TABLE orders (
    id         BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    user_id    BIGINT UNSIGNED NOT NULL,
    product_name VARCHAR(200)  NOT NULL,
    price      DECIMAL(10, 2)  NOT NULL,
    order_time DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    INDEX idx_user_id (user_id),
    CONSTRAINT fk_orders_user
        FOREIGN KEY (user_id) REFERENCES users(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

`FOREIGN KEY (user_id) REFERENCES users(id)` 告诉MySQL：orders表的user_id必须能在users表的id中找到。如果你试图插入 `user_id = 999`（一个不存在的用户），MySQL会直接拒绝。

- `ON DELETE CASCADE`：删除用户时，自动删除该用户的所有订单。
- `ON UPDATE CASCADE`：修改用户id时，自动更新订单中的user_id。
- `ON DELETE SET NULL`：删除用户时，订单的user_id设为NULL（订单保留）。
- `ON DELETE RESTRICT`：如果有订单引用该用户，拒绝删除用户。

**行业争议**：有些公司禁止使用数据库外键约束——认为它把业务逻辑绑在了数据库层，不利于分库分表和大规模扩展。他们选择在应用层保证数据一致性。但对于初学者和大多数中小型项目，外键约束是**防数据错乱的最后一道防线**——保留比较好。

---

## 53.3 INNER JOIN：取交集

INNER JOIN只返回**两张表中都匹配的行**。

想象两个圆的交集——只取重叠的部分。

```sql
SELECT
    u.username,
    u.email,
    o.product_name,
    o.price,
    o.order_time
FROM users AS u
INNER JOIN orders AS o ON u.id = o.user_id;
```

**逐词解释**：
- `FROM users AS u`：以users表为主，起别名为u
- `INNER JOIN orders AS o`：连接orders表，起别名为o
- `ON u.id = o.user_id`：连接条件是users的id等于orders的user_id
- SELECT的是想要的字段，来自两张表

**结果**：

```
+----------+---------------+--------------+-------+---------------------+
| username | email         | product_name | price | order_time          |
+----------+---------------+--------------+-------+---------------------+
| zhangsan | zs@test.com   | iPhone 15    | 6999  | 2024-01-01 00:00:00 |
| zhangsan | zs@test.com   | AirPods      | 1299  | 2024-01-03 00:00:00 |
| lisi     | lisi@test.com | iPhone 15    | 6999  | 2024-01-05 00:00:00 |
| zhangsan | zs@test.com   | MacBook      | 9999  | 2024-01-08 00:00:00 |
+----------+---------------+--------------+-------+---------------------+
```

**注意**：如果users表里有用户 `wangwu`，但他没有任何订单——wangwu不会出现在INNER JOIN的结果中。因为INNER JOIN只返回两边都能匹配上的行。

**INNER JOIN 可以简写为 JOIN**（等价）：

```sql
SELECT u.username, o.product_name
FROM users u
JOIN orders o ON u.id = o.user_id;
```

### 多个表INNER JOIN

```sql
SELECT
    u.username,
    o.product_name,
    o.price,
    p.category
FROM users u
JOIN orders o    ON u.id = o.user_id
JOIN products p  ON o.product_name = p.name;
```

链式连接三张表：用户→订单→商品分类。

### JOIN 结合 WHERE / GROUP BY / ORDER BY

```sql
SELECT
    u.username,
    COUNT(o.id) AS order_count,
    SUM(o.price) AS total_spent
FROM users u
JOIN orders o ON u.id = o.user_id
WHERE o.order_time >= '2024-01-01'
GROUP BY u.id, u.username
HAVING total_spent > 5000
ORDER BY total_spent DESC;
```

这个查询做了：多表连接→时间过滤→按用户分组→统计订单数和总金额→只保留消费大于5000的→按消费额排序。

---

## 53.4 LEFT JOIN：左表全保留

LEFT JOIN（也称LEFT OUTER JOIN）：**左表的所有行都返回**，右表匹配不上就填NULL。

```sql
SELECT
    u.username,
    u.email,
    o.product_name,
    o.price
FROM users u
LEFT JOIN orders o ON u.id = o.user_id;
```

如果user表中有三个用户：zhangsan（有3个订单）、lisi（有1个订单）、wangwu（0个订单）：

```
+----------+---------------+--------------+-------+
| username | email         | product_name | price |
+----------+---------------+--------------+-------+
| zhangsan | zs@test.com   | iPhone 15    | 6999  |
| zhangsan | zs@test.com   | AirPods      | 1299  |
| zhangsan | zs@test.com   | MacBook      | 9999  |
| lisi     | lisi@test.com | iPhone 15    | 6999  |
| wangwu   | ww@test.com   | NULL         | NULL  |
+----------+---------------+--------------+-------+
```

wangwu没有订单，但依然出现在结果中——订单相关字段全是NULL。

### LEFT JOIN 排除交集（查"没订单的用户"）

```sql
SELECT u.username
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
WHERE o.id IS NULL;
```

先LEFT JOIN确保所有用户都出现，然后用 `WHERE o.id IS NULL` 过滤出那些右表匹配不上的行——即没有订单的用户。

### LEFT JOIN 常见误区

**误区一：把条件写在ON还是WHERE？**

```sql
SELECT u.username, o.product_name
FROM users u
LEFT JOIN orders o ON u.id = o.user_id AND o.price > 5000;
```

vs

```sql
SELECT u.username, o.product_name
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
WHERE o.price > 5000;
```

第一个查询：LEFT JOIN时只连接price>5000的订单，没满足条件的行依然返回（NULL）。wangwu仍然会出现。

第二个查询：WHERE在JOIN之后执行。`o.price > 5000` 会把NULL也过滤掉（NULL > 5000 = NULL，不是TRUE）——wangwu消失了。

**规则**：LEFT JOIN中，ON中的条件影响"和哪些行连接"，WHERE中的条件影响"最终结果保留哪些行"。

---

## 53.5 RIGHT JOIN：右表全保留

RIGHT JOIN是LEFT JOIN的镜像——右表的所有行都返回：

```sql
SELECT u.username, o.product_name
FROM users u
RIGHT JOIN orders o ON u.id = o.user_id;
```

orders表的所有行都返回，users表匹配不上就填NULL。这在有订单但用户被删了的情况下才会出现。

**实际上，大多数开发者从来不用RIGHT JOIN**——把表顺序换一下，用LEFT JOIN就能完成RIGHT JOIN的工作：

```sql
SELECT u.username, o.product_name
FROM orders o
LEFT JOIN users u ON u.id = o.user_id;
```

效果和上面RIGHT JOIN完全一样，但可读性更好。团队代码规范通常会禁用RIGHT JOIN。

---

## 53.6 自连接：自己连自己

自连接就是一张表自己和自己JOIN——用于表中行与行之间的比较。

**场景**：找出同一个部门的同事配对。

有一张 `employees` 表：

```
id | name   | department
1  | 张三   | 技术部
2  | 李四   | 技术部
3  | 王五   | 市场部
4  | 赵六   | 技术部
```

要找出"技术部中所有的同事配对关系"：

```sql
SELECT
    e1.name AS employee,
    e2.name AS colleague
FROM employees e1
JOIN employees e2
    ON e1.department = e2.department
    AND e1.id < e2.id
WHERE e1.department = '技术部';
```

```
+----------+-----------+
| employee | colleague |
+----------+-----------+
| 张三     | 李四      |
| 张三     | 赵六      |
| 李四     | 赵六      |
+----------+-----------+
```

关键点：`e1.id < e2.id` 避免出现"张三-张三"（自己和自己配对）和"张三-李四" / "李四-张三"（重复配对）。

**另一个场景**：查找"下属和上级"。假设表中有一个 `manager_id` 字段：

```sql
SELECT
    e.name AS employee_name,
    m.name AS manager_name
FROM employees e
LEFT JOIN employees m ON e.manager_id = m.id;
```

同样是自连接——一张表从两个角度看。

---

## 53.7 JOIN的底层原理

理解JOIN是怎么执行的，才能写出高性能的查询。

### Nested Loop Join（嵌套循环连接）

这是最基本的JOIN算法。原理和嵌套for循环一模一样：

```go
for _, u := range users {
    for _, o := range orders {
        if u.ID == o.UserID {
        }
    }
}
```

**复杂度**：O(N × M)。如果users有1万行，orders有10万行，最坏情况要比较10亿次。

**MySQL的实现**：MySQL会用索引优化。如果 `orders.user_id` 有索引，内层循环不需要遍历全部10万行——通过B+树定位到user_id=对应值的行，只需几次磁盘IO。复杂度降为 O(N × log M)。

这是**小表驱动大表**原则的根源——外层循环用小表，内层用索引在大表中快速查找。

### Hash Join（哈希连接）

MySQL 8.0.18引入：

1. 把较小的表（build表）的所有JOIN键构造一个哈希表，放入内存。
2. 遍历大表（probe表）的每一行，用JOIN键在哈希表中 O(1) 查找。

**复杂度**：O(N + M)。比Nested Loop快得多，但需要足够的内存装哈希表。

**适用场景**：两张表都没有索引，或等值JOIN（`=`）。

### 如何选择

MySQL优化器会根据索引情况、表大小自动选择JOIN算法。你要做的是确保JOIN键上**有索引**，剩下交给优化器。

---

## 53.8 JOIN性能优化原则

### 1. 小表驱动大表

```sql
SELECT * FROM small_table s
JOIN big_table b ON s.id = b.small_id;
```

让行数少的表做驱动表（外层循环），行数多的做被驱动表（内层通过索引查找）。

### 2. JOIN字段必须加索引

```sql
CREATE INDEX idx_user_id ON orders(user_id);
```

没有索引时，MySQL只能用Nested Loop Join做全表扫描——非常慢。

### 3. 只SELECT需要的字段

```sql
SELECT u.username, o.product_name
FROM users u
JOIN orders o ON u.id = o.user_id;
```

而不是 `SELECT *`——减少传输量和内存占用。

### 4. 控制JOIN的表数量

一条SQL JOIN了五六张表——不仅慢，而且难以维护。单条查询JOIN不要超过3~4张表。更复杂的逻辑拆成多条简单查询。

### 5. 给表起短别名

`users AS u`、`orders AS o`、`products AS p`——别名约定：首字母。所有人一看就懂，不用每个字段前都写完整的表名。

---

## 本章小结

| 知识点 | 要点 |
|--------|------|
| 多表原因 | 避免数据冗余、更新异常、删除异常 |
| 外键 | 建立表间关联，CONSTRAINT声明，CASCADE/SET NULL/RESTRICT |
| INNER JOIN | 只返回匹配行（交集），最常用 |
| LEFT JOIN | 左表全保留，右表无匹配填NULL，排除交集用 `WHERE right.id IS NULL` |
| RIGHT JOIN | 右表全保留，可用LEFT JOIN替代，实际很少用 |
| 自连接 | 同一张表自己连自己，查同事/上下级配对 |
| Nested Loop Join | 嵌套循环，O(N×M)，依赖索引优化 |
| Hash Join | 哈希表匹配，O(N+M)，MySQL 8.0.18+，需要等值JOIN |
| 优化原则 | 小表驱动大表、JOIN字段加索引、只SELECT必要字段、控制JOIN数量 |

> 🚀 下一章：第54章 · 表设计与范式。JOIN写得顺手了，但你的表结构设计得合理吗？为什么有些表查起来特别慢、改起来特别容易出错？数据库设计有一整套科学的方法论——范式，它告诉我们什么样的表结构是优雅的、没有冗余的。

---
[← 上一章：52-SQL进阶：查询与聚合](52-SQL进阶：查询与聚合.md) | [下一章：54-表设计与范式 →](54-表设计与范式.md)
