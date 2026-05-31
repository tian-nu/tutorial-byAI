# 第57章 · JOIN多表查询

> "你的仓库里不小心分出了很多货架——用户一个货架、订单一个货架、商品一个货架。现在老板问：'张三买了哪些商品？'这需要同时翻三个货架，把张三的ID在订单货架上找到对应的商品ID，再去商品货架上找到商品名字。JOIN就是专门干这件事的——它是连接不同货架的传送带。"

---

## 57.1 为什么需要JOIN

假设你有一个电商系统，三张表：

```
users 表：                 orders 表：               products 表：
+----+--------+         +----+---------+--------+  +----+----------+
| id | name   |         | id | user_id | prod_id |  | id | name     |
+----+--------+         +----+---------+--------+  +----+----------+
| 1  | 张三   |         | 1  | 1       | 10     |  | 10 | 机械键盘 |
| 2  | 李四   |         | 2  | 1       | 20     |  | 20 | 鼠标     |
+----+--------+         | 3  | 2       | 30     |  | 30 | 显示器   |
                        +----+---------+--------+  +----+----------+
```

老板问："张三买了什么？"你需要：
1. 在 `users` 表找到张三的 id = 1
2. 在 `orders` 表找到 user_id = 1 的记录（id=1和id=2）
3. 在 `products` 表找到 prod_id = 10 和 20 的名字

这就是JOIN要做的事——**通过公共字段把多张表连成一张虚拟大表**，然后在这张大表上查询。

---

## 57.2 INNER JOIN：取交集

### 57.2.1 基础语法

```sql
SELECT 列名列表
FROM 表A
INNER JOIN 表B ON 表A.某列 = 表B.某列;
```

**"INNER JOIN … ON …"就是"把A表和B表，按照ON后面的条件匹配，能匹配上的行拼在一起"。**

先创建演示数据：

```sql
CREATE DATABASE join_demo CHARACTER SET utf8mb4;
USE join_demo;

CREATE TABLE students (
    id   INT PRIMARY KEY,
    name VARCHAR(20)
);

CREATE TABLE scores (
    id         INT PRIMARY KEY,
    student_id INT,
    course     VARCHAR(20),
    score      INT
);

INSERT INTO students VALUES
    (1, '张三'), (2, '李四'), (3, '王五'), (4, '赵六');

INSERT INTO scores VALUES
    (1, 1, '数学', 85),
    (2, 1, '英语', 90),
    (3, 2, '数学', 78),
    (4, 3, '英语', 88);
```

现在执行INNER JOIN：

```sql
SELECT students.name, scores.course, scores.score
FROM students
INNER JOIN scores ON students.id = scores.student_id;
```

输出：

```
+--------+--------+-------+
| name   | course | score |
+--------+--------+-------+
| 张三   | 数学   |    85 |
| 张三   | 英语   |    90 |
| 李四   | 数学   |    78 |
| 王五   | 英语   |    88 |
+--------+--------+-------+
```

**注意赵六没有出现**——他在students表中存在，但没有成绩记录。INNER JOIN只返回**两表中都匹配得上**的行。

### 57.2.2 INNER JOIN的可视化理解

```
students:              scores:
┌────┬──────┐         ┌────┬────────────┬──────┬───────┐
│ id │ name │         │ id │ student_id │course│ score │
├────┼──────┤         ├────┼────────────┼──────┼───────┤
│ 1  │ 张三 │◄────────│ 1  │     1      │ 数学 │  85   │
│ 1  │ 张三 │◄────────│ 2  │     1      │ 英语 │  90   │
│ 2  │ 李四 │◄────────│ 3  │     2      │ 数学 │  78   │
│ 3  │ 王五 │◄────────│ 4  │     3      │ 英语 │  88   │
│ 4  │ 赵六 │          └────┴────────────┴──────┴───────┘
└────┴──────┘
        ▲
        └─── 赵六没有匹配到任何scores行，被排除
```

### 57.2.3 多表JOIN

```sql
-- 三表连接：查每个订单的客户名和商品名
SELECT u.name AS customer, p.name AS product, o.amount
FROM orders o
INNER JOIN users u    ON o.user_id    = u.id
INNER JOIN products p ON o.product_id = p.id;
```

> 💡 `orders o` 是表别名，`ON o.user_id = u.id` 比 `ON orders.user_id = users.id` 简洁得多。

### 57.2.4 JOIN与GROUP BY配合

```sql
-- 每个学生的平均分
SELECT s.name, AVG(sc.score) AS avg_score
FROM students s
INNER JOIN scores sc ON s.id = sc.student_id
GROUP BY s.id, s.name
ORDER BY avg_score DESC;
```

---

## 57.3 LEFT JOIN：保留左表全部

LEFT JOIN保留**左表**的所有行，右表匹配不上就填NULL。

```sql
SELECT s.name, sc.course, sc.score
FROM students s
LEFT JOIN scores sc ON s.id = sc.student_id;
```

输出：

```
+--------+--------+-------+
| name   | course | score |
+--------+--------+-------+
| 张三   | 数学   |    85 |
| 张三   | 英语   |    90 |
| 李四   | 数学   |    78 |
| 王五   | 英语   |    88 |
| 赵六   | NULL   |  NULL |  ← 赵六保留，成绩列为NULL
+--------+--------+-------+
```

**图解**：

```
students (LEFT):       scores (RIGHT):
┌────┬──────┐         ┌────┬────────────┬──────┬───────┐
│ id │ name │         │ id │ student_id │course│ score │
├────┼──────┤         ├────┼────────────┼──────┼───────┤
│ 1  │ 张三 │─────────│ 1  │     1      │ 数学 │  85   │
│ 1  │ 张三 │─────────│ 2  │     1      │ 英语 │  90   │
│ 2  │ 李四 │─────────│ 3  │     2      │ 数学 │  78   │
│ 3  │ 王五 │─────────│ 4  │     3      │ 英语 │  88   │
│ 4  │ 赵六 │- - - - - - - 没有匹配 → NULL  │
└────┴──────┘         └────┴────────────┴──────┴───────┘
```

### 典型场景：查没有成绩的学生

```sql
-- 查出所有没有参加考试的学生
SELECT s.id, s.name
FROM students s
LEFT JOIN scores sc ON s.id = sc.student_id
WHERE sc.id IS NULL;
```

> 注意：`WHERE sc.id IS NULL` 不是 `WHERE sc.student_id IS NULL`。选scores表中**不会为NULL的列**（如主键）来判断。

### LEFT JOIN与聚合的坑

```sql
-- 这种写法COUNT会计入NULL行，赵六被算作"考试1次，0分"：
SELECT s.name, COUNT(sc.id) AS exam_count, AVG(sc.score) AS avg_score
FROM students s
LEFT JOIN scores sc ON s.id = sc.student_id
GROUP BY s.id, s.name;
```

输出：

```
+--------+------------+-----------+
| name   | exam_count | avg_score |
+--------+------------+-----------+
| 张三   |          2 |   87.5000 |
| 李四   |          1 |   78.0000 |
| 王五   |          1 |   88.0000 |
| 赵六   |          0 |     NULL  |  ← 0次考试，平均分NULL
+--------+------------+-----------+
```

`COUNT(sc.id)` 不统计NULL，所以赵六是0。`AVG(sc.score)` 在赵六那里是NULL（因为没有非NULL值可平均），逻辑正确。

---

## 57.4 RIGHT JOIN：保留右表全部

RIGHT JOIN和LEFT JOIN是对称的，只是把"右表"作为保留方。**实际开发中几乎没人用RIGHT JOIN**——把表顺序颠倒一下，RIGHT JOIN就成了LEFT JOIN。

```sql
-- 这两条SQL结果完全相同
SELECT * FROM A RIGHT JOIN B ON A.id = B.a_id;
SELECT * FROM B LEFT JOIN A ON B.a_id = A.id;
```

> 📌 规范：团队内统一只用LEFT JOIN，可读性和可维护性最好。

---

## 57.5 自连接（SELF JOIN）

一张表自己和自己JOIN。

**场景：员工表中有 `manager_id` 列指向自己的上级。**

```sql
CREATE TABLE employees (
    id         INT PRIMARY KEY,
    name       VARCHAR(20),
    manager_id INT
);

INSERT INTO employees VALUES
    (1, '张老板', NULL),
    (2, '李经理', 1),
    (3, '王组长', 2),
    (4, '赵员工', 3),
    (5, '孙员工', 3);

-- 自连接：查每个员工和其上级的名字
SELECT
    e.name AS employee,
    m.name AS manager
FROM employees e
LEFT JOIN employees m ON e.manager_id = m.id;
```

输出：

```
+----------+-----------+
| employee | manager   |
+----------+-----------+
| 张老板   | NULL      |
| 李经理   | 张老板    |
| 王组长   | 李经理    |
| 赵员工   | 王组长    |
| 孙员工   | 王组长    |
+----------+-----------+
```

**关键点**：同一张表起了两个别名 `e` 和 `m`，MySQL把它当成两张独立的"虚拟表"来JOIN。`e.manager_id = m.id` 即"把员工行中的manager_id和另一行（上级行）的id匹配"。

---

## 57.6 UNION与UNION ALL

JOIN是**横向拼接**（加列），UNION是**纵向拼接**（加行）。

```sql
-- 查所有打过90分以上或不及格学生的名字
SELECT s.name, '高分' AS type
FROM students s
INNER JOIN scores sc ON s.id = sc.student_id
WHERE sc.score >= 90

UNION

SELECT s.name, '低分' AS type
FROM students s
INNER JOIN scores sc ON s.id = sc.student_id
WHERE sc.score < 60;
```

| 操作 | 行为 | 性能 |
|------|------|------|
| UNION | 合并 + **去重** | 慢（需要排序去重） |
| UNION ALL | 合并，**不去重** | 快（直接拼接） |

> **除非你明确需要去重，否则用 UNION ALL。** 大部分场景下你知道两个结果集不会有重复行，没必要让MySQL多跑一遍去重。

**UNION使用规则**：
1. 两边的SELECT列数必须相同
2. 对应列的数据类型必须兼容
3. 最终列名以第一个SELECT为准

---

## 57.7 JOIN查询优化提示

1. **小表驱动大表**：把数据量小的表放前面（MySQL优化器会自动处理，但了解原理有助于理解EXPLAIN结果）
2. **JOIN的ON条件列必须有索引**：否则扫描行数=两表行数的笛卡尔积
3. **避免SELECT ***：只取需要的列，减少网络传输和内存占用
4. **多表JOIN不超过3个**：超过3个需要考虑表设计是否合理

```sql
-- 在JOIN的关联列上创建索引
CREATE INDEX idx_user_id ON orders(user_id);
CREATE INDEX idx_product_id ON orders(product_id);
```

---

## 57.8 JOIN类型总结

```
INNER JOIN:              LEFT JOIN:
┌──────┐ ┌──────┐       ┌──────────┐ ┌──────┐
│  A   │ │  B   │       │    A     │ │  B   │
│  ┌─┐ │ │ ┌─┐  │       │  ┌─────┐ │ │ ┌─┐  │
│  │■│ │ │ │■│  │       │  │  ■  │ │ │ │■│  │
│  └─┘ │ │ └─┘  │       │  └─────┘ │ │ └─┘  │
│      │ │       │       │    ▲    │ │       │
└──────┘ └──────┘       │  NULL  │ │       │
   交集    交集           └──────────┘ └──────┘
                          左表全留  右表匹配
```

| JOIN类型 | 返回 | 未匹配时的处理 |
|----------|------|---------------|
| INNER JOIN | 两表都匹配的行 | 丢弃不匹配的行 |
| LEFT JOIN | 左表所有行 | 右表列填NULL |
| RIGHT JOIN | 右表所有行 | 左表列填NULL |
| CROSS JOIN | 笛卡尔积（每行×每行） | 无匹配概念 |

> 💡 MySQL不直接支持FULL OUTER JOIN（两表所有行都保留）。需要用 `LEFT JOIN UNION RIGHT JOIN` 模拟，但极少用到。

---

## 本章小结

| 概念 | 要点 |
|------|------|
| INNER JOIN | 只返回两表都匹配的行，最常用 |
| LEFT JOIN | 左表全保留，右表匹配不上填NULL |
| RIGHT JOIN | 右表全保留，统一用LEFT JOIN替代 |
| 自连接 | 同一张表起两个别名自己连自己，用于树形结构 |
| UNION | 纵向拼接，去重（`UNION ALL` 不去重，更快） |
| JOIN优化 | ON条件的列建索引，小表驱动大表，避免SELECT * |
| 三表JOIN | 多次INNER JOIN串联，用别名简化 |

---

## 自测题

1. **`students` 表有 id 和 name，`scores` 表有 student_id 和 score。写出SQL：列出所有学生的姓名和最高分（没成绩的学生也要列出，最高分显示0）。**

2. **INNER JOIN 和 LEFT JOIN 的核心区别是什么？举一个必须用 LEFT JOIN 的场景。**

3. **`UNION` 和 `UNION ALL` 的区别是什么？为什么说"除非需要去重，否则用 UNION ALL"？**

<details>
<summary>参考答案（做完再看）</summary>

1. ```sql
SELECT s.name, IFNULL(MAX(sc.score), 0) AS max_score
FROM students s
LEFT JOIN scores sc ON s.id = sc.student_id
GROUP BY s.id, s.name;
```
LEFT JOIN保证没成绩的学生也出现。IFNULL把NULL转为0。注意 GROUP BY 用 s.id 而不是 s.name，因为name可能重名而id是唯一的。

2. INNER JOIN只返回两表都匹配的行，LEFT JOIN保留左表全部行（右表不匹配则NULL）。必须用LEFT JOIN的场景：查所有学生，包括没有选课的学生；查所有商品及其销量（没有销量的商品也要列出）；报表中"全量+关联"的场景。

3. UNION合并两个结果集并去重，UNION ALL合并但不去重。UNION ALL更快是因为省去了去重的排序和比较开销。在大多数业务场景中，两个查询的结果集不会重叠（比如"高分学生"和"低分学生"），去重是多余的。
</details>