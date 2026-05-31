# 第56章 · SQL进阶：查询与聚合

> "你已经会在仓库里搭货架和搬箱子了。但一个合格的仓库管理员，光会搬箱子还不够。老板问'上个月销量最高的前十个商品是什么？''每个部门的平均销售额是多少？'——你不能一个个箱子打开数。你需要更强大的搜索和统计能力。SELECT不只是一个'找东西'的工具，它是你手中的数据显微镜和计算器。"

---

## 56.1 回顾SELECT基础

```sql
SELECT 列名1, 列名2, ...
FROM 表名
WHERE 条件
ORDER BY 排序列
LIMIT 数量;
```

这就是SELECT的完整执行骨架。本章将在这副骨架上填肉，让它从"查找"升级为"分析和聚合"。

> **执行顺序很重要**。虽然你写的是 `SELECT → FROM → WHERE → ORDER BY`，但MySQL实际执行的顺序是：
> ```
> FROM → WHERE → SELECT → ORDER BY → LIMIT
> ```
> 记住这个顺序，后面的聚合函数和HAVING才不会搞混。

---

## 56.2 ORDER BY：排序

```sql
-- 按分数升序（默认）
SELECT name, score FROM students ORDER BY score;

-- 按分数降序
SELECT name, score FROM students ORDER BY score DESC;

-- 多字段排序：先按班级升序，同班级内按分数降序
SELECT name, class, score FROM students ORDER BY class ASC, score DESC;
```

> 📊 字符列的排序规则由 COLLATE（排序规则）决定。`utf8mb4_general_ci` 中的 `ci` 表示 Case Insensitive，即 'a' 和 'A' 视为相同。如果要用 `_bin`（二进制排序），则会区分大小写。

---

## 56.3 LIMIT与OFFSET：分页

```sql
-- 取前5条
SELECT * FROM users LIMIT 5;

-- 跳过前10条，取5条（第11~15条）
SELECT * FROM users LIMIT 5 OFFSET 10;

-- 等价写法
SELECT * FROM users LIMIT 10, 5;
```

分页的通用公式：

```sql
-- 第 N 页，每页 M 条
SELECT * FROM table LIMIT M OFFSET (N - 1) * M;
```

```sql
-- 第1页，每页10条
SELECT * FROM users LIMIT 10 OFFSET 0;

-- 第2页，每页10条
SELECT * FROM users LIMIT 10 OFFSET 10;

-- 第3页，每页10条
SELECT * FROM users LIMIT 10 OFFSET 20;
```

> 🤔 **想多一点**：OFFSET翻到第1000页会很慢，因为MySQL需要数出前10000条然后丢掉。大表分页建议用"游标分页"（记住上一页最后一条的ID，`WHERE id > last_id LIMIT 10`），第63章优化章节会细讲。

---

## 56.4 DISTINCT：去重

```sql
-- 查所有不重复的班级名
SELECT DISTINCT class FROM students;

-- 查不重复的班级+性别组合
SELECT DISTINCT class, gender FROM students;
```

---

## 56.5 聚合函数

聚合函数把多行数据"压缩"成一个值。像榨汁机——塞进去一把橙子，出来一杯橙汁。

### 56.5.1 COUNT：计数

```sql
-- 总行数（包含NULL）
SELECT COUNT(*) FROM students;

-- 指定列的非NULL行数
SELECT COUNT(phone) FROM users;

-- 条件计数
SELECT COUNT(*) FROM students WHERE score >= 90;
```

> `COUNT(*)` 和 `COUNT(列名)` 的区别：`COUNT(*)` 统计所有行（包括全NULL的行），`COUNT(列名)` 只统计该列不为NULL的行。`COUNT(1)` 和 `COUNT(*)` 在InnoDB中性能一样，推荐用 `COUNT(*)`。

### 56.5.2 SUM：求和

```sql
-- 所有学生总分
SELECT SUM(score) FROM students;

-- 一班总分
SELECT SUM(score) FROM students WHERE class = '一班';

-- 所有用户余额总和
SELECT SUM(balance) FROM users;
```

### 56.5.3 AVG：平均值

```sql
-- 平均分
SELECT AVG(score) FROM students;

-- 精确到两位小数
SELECT ROUND(AVG(score), 2) FROM students;
```

> ⚠️ AVG忽略NULL行。如果数据中有NULL，AVG会除以非NULL的行数而不是总行数，这可能不是你想要的。

### 56.5.4 MAX / MIN：最大/最小值

```sql
-- 最高分
SELECT MAX(score) FROM students;

-- 最低余额
SELECT MIN(balance) FROM users;

-- 最新的注册时间
SELECT MAX(created_at) FROM users;
```

### 56.5.5 聚合函数组合使用

```sql
SELECT
    COUNT(*)   AS total_students,
    AVG(score) AS avg_score,
    MAX(score) AS max_score,
    MIN(score) AS min_score,
    SUM(score) AS total_score
FROM students;
```

输出：

```
+----------------+-----------+-----------+-----------+-------------+
| total_students | avg_score | max_score | min_score | total_score |
+----------------+-----------+-----------+-----------+-------------+
|              5 |   82.0000 |        95 |        60 |         410 |
+----------------+-----------+-----------+-----------+-------------+
```

> 💡 `AS` 给列起别名。聚合后的列名默认是函数名，用AS起个可读的名字，Java代码里取值也方便。

---

## 56.6 GROUP BY：分组聚合

聚合函数榨的是**整个表**的汁。但如果你想要**每个班分别**的汁呢？这时就需要GROUP BY。

### 56.6.1 基础分组

```sql
-- 每个班的平均分
SELECT class, AVG(score) AS avg_score
FROM students
GROUP BY class;
```

输出：

```
+--------+-----------+
| class  | avg_score |
+--------+-----------+
| 一班   |   81.6667 |
| 二班   |   82.5000 |
+--------+-----------+
```

### 56.6.2 多列分组

```sql
-- 每个班男生女生的平均分
SELECT class, gender, AVG(score) AS avg_score
FROM students
GROUP BY class, gender;
```

### 56.6.3 GROUP BY规则

GROUP BY有一条铁律：**SELECT中出现的列，要么在GROUP BY中，要么被聚合函数包裹**。违反这条规则在MySQL中会得到随机值（其他数据库直接报错）：

```sql
-- ❌ 错误：name不在GROUP BY中，也不是聚合函数
SELECT name, class, AVG(score) FROM students GROUP BY class;

-- ✅ 正确
SELECT class, AVG(score) FROM students GROUP BY class;
```

> 为什么？GROUP BY把相同class的行"压成"了一行。那name呢？同班有张三李四，压成一行后选谁的name？MySQL不知道，所以它随机选一个——这几乎肯定不是你想要的。

---

## 56.7 HAVING：分组后过滤

WHERE过滤的是**分组前**的行，HAVING过滤的是**分组后**的组。

```sql
-- 查平均分大于80的班级
SELECT class, AVG(score) AS avg_score
FROM students
GROUP BY class
HAVING avg_score > 80;
```

WHERE和HAVING可以同时出现：

```sql
-- 先剔除非正常分数，再按班级分组，最后只保留高分班级
SELECT class, AVG(score) AS avg_score, COUNT(*) AS student_count
FROM students
WHERE score BETWEEN 0 AND 100
GROUP BY class
HAVING avg_score >= 80 AND student_count >= 2
ORDER BY avg_score DESC;
```

| 子句 | 过滤目标 | 执行时机 |
|------|---------|---------|
| WHERE | 原始行 | GROUP BY之前 |
| HAVING | 分组后的组 | GROUP BY之后 |
| ORDER BY | 最终结果集 | 最后 |
| LIMIT | 最终结果集 | 最后 |

完整执行顺序：
```
FROM → WHERE → GROUP BY → HAVING → SELECT → ORDER BY → LIMIT
```

---

## 56.8 条件表达式：CASE WHEN

CASE WHEN让你在SQL中实现if-else逻辑：

```sql
SELECT
    name,
    score,
    CASE
        WHEN score >= 90 THEN '优秀'
        WHEN score >= 80 THEN '良好'
        WHEN score >= 70 THEN '中等'
        WHEN score >= 60 THEN '及格'
        ELSE '不及格'
    END AS grade
FROM students
ORDER BY score DESC;
```

配合聚合函数使用：

```sql
-- 统计每个等级的人数
SELECT
    CASE
        WHEN score >= 90 THEN '优秀'
        WHEN score >= 80 THEN '良好'
        WHEN score >= 70 THEN '中等'
        WHEN score >= 60 THEN '及格'
        ELSE '不及格'
    END AS grade,
    COUNT(*) AS count
FROM students
GROUP BY grade
ORDER BY count DESC;
```

---

## 56.9 NULL处理

NULL是SQL中最容易引起Bug的东西之一。它不是0，不是空字符串，不是false——NULL就是"未知"。

```sql
-- 查询没有填手机号的用户
SELECT * FROM users WHERE phone IS NULL;

-- ⚠️ 下面这样是查不到的！
SELECT * FROM users WHERE phone = NULL;
-- 因为 NULL = NULL 的结果是 NULL（未知），不是TRUE
```

| 函数 | 作用 | 示例 |
|------|------|------|
| `IS NULL` / `IS NOT NULL` | 判断是否为NULL | `WHERE phone IS NULL` |
| `IFNULL(expr, default)` | 如果expr为NULL则返回default | `SELECT IFNULL(phone, '未填写')` |
| `COALESCE(a, b, c)` | 返回第一个非NULL值 | `SELECT COALESCE(phone, email, '无联系方式')` |

```sql
-- 余额为NULL时按0计算
SELECT name, IFNULL(balance, 0) + 100 AS new_balance FROM users;

-- 优先用phone，没有的话用email
SELECT name, COALESCE(phone, email, '无') AS contact FROM users;
```

> 🐞 **最常见的NULL Bug**：AVG(score)在score有NULL时，分母是非NULL行数而不是总行数。如果你想把NULL当成0来算平均，用 `AVG(IFNULL(score, 0))`。

---

## 56.10 字符串函数

| 函数 | 作用 | 示例 |
|------|------|------|
| `CONCAT(a, b, c)` | 拼接字符串 | `CONCAT(first_name, ' ', last_name)` |
| `LENGTH(str)` | 字节长度 | `LENGTH('你好')` → 6（utf8mb4下） |
| `CHAR_LENGTH(str)` | 字符长度 | `CHAR_LENGTH('你好')` → 2 |
| `UPPER(str)` / `LOWER(str)` | 大小写 | `UPPER('hello')` → 'HELLO' |
| `TRIM(str)` | 去首尾空格 | `TRIM(' hello ')` → 'hello' |
| `SUBSTRING(str, start, len)` | 截取子串 | `SUBSTRING('hello', 1, 2)` → 'he' |
| `REPLACE(str, from, to)` | 替换 | `REPLACE('hello world', 'world', 'mysql')` |

```sql
-- 取出邮箱的域名部分
SELECT
    email,
    SUBSTRING(email, INSTR(email, '@') + 1) AS domain
FROM users;
```

---

## 56.11 日期函数

| 函数 | 作用 | 示例 |
|------|------|------|
| `NOW()` | 当前日期时间 | `2026-05-29 14:30:00` |
| `CURDATE()` | 当前日期 | `2026-05-29` |
| `DATE(expr)` | 提取日期部分 | `DATE('2026-05-29 14:30:00')` → `2026-05-29` |
| `YEAR(expr)` / `MONTH(expr)` / `DAY(expr)` | 提取年月日 | `YEAR(NOW())` → `2026` |
| `DATEDIFF(a, b)` | 日期差（天数） | `DATEDIFF('2026-06-01', '2026-05-29')` → 3 |
| `DATE_ADD(date, INTERVAL n unit)` | 日期加减 | `DATE_ADD(NOW(), INTERVAL 7 DAY)` |
| `DATE_FORMAT(date, fmt)` | 格式化 | `DATE_FORMAT(NOW(), '%Y年%m月%d日')` |

```sql
-- 本周注册的用户
SELECT * FROM users
WHERE created_at >= DATE_ADD(CURDATE(), INTERVAL -WEEKDAY(CURDATE()) DAY);

-- 按月统计注册人数
SELECT
    DATE_FORMAT(created_at, '%Y-%m') AS month,
    COUNT(*) AS reg_count
FROM users
GROUP BY month
ORDER BY month;
```

---

## 56.12 子查询

子查询是把一个SELECT的结果作为另一个SELECT的输入。

```sql
-- 查分数高于平均分的学生
SELECT name, score
FROM students
WHERE score > (SELECT AVG(score) FROM students);

-- 查在"一班"存在的学生（用IN）
SELECT * FROM students
WHERE class IN (SELECT DISTINCT class FROM students WHERE score > 90);

-- 用EXISTS：比IN效率高（找到就停）
SELECT * FROM students s
WHERE EXISTS (
    SELECT 1 FROM students
    WHERE class = s.class AND score = 100
);
```

> IN vs EXISTS：IN先执行子查询生成结果集，然后逐行比对，适合子查询结果集小的场景。EXISTS对外层每一行执行子查询，找到一条就停，适合子查询结果集大但外层表小的场景。

---

## 56.13 综合练习

已知以下订单表：

```sql
CREATE TABLE orders (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    customer    VARCHAR(50)  NOT NULL,
    product     VARCHAR(100) NOT NULL,
    amount      DECIMAL(10,2) NOT NULL,
    status      ENUM('待支付','已支付','已发货','已完成','已取消') NOT NULL DEFAULT '待支付',
    order_date  DATE NOT NULL
);

INSERT INTO orders (customer, product, amount, status, order_date) VALUES
    ('张三', '机械键盘',  599.00, '已完成', '2026-05-01'),
    ('李四', '显示器',   1299.00, '已完成', '2026-05-02'),
    ('张三', '鼠标',      199.00, '已发货', '2026-05-10'),
    ('王五', '机械键盘',  599.00, '已完成', '2026-05-12'),
    ('李四', '耳机',      349.00, '已支付', '2026-05-15'),
    ('赵六', '显示器',   1299.00, '待支付', '2026-05-18'),
    ('张三', '鼠标垫',     49.00, '已完成', '2026-05-20'),
    ('李四', '充电器',     89.00, '已取消', '2026-05-22');
```

请尝试写出以下SQL：

```sql
-- 1. 每个客户的订单数和总消费金额，按总金额降序
SELECT
    customer,
    COUNT(*) AS order_count,
    SUM(amount) AS total_spent
FROM orders
GROUP BY customer
ORDER BY total_spent DESC;

-- 2. 消费超过500元的客户
SELECT
    customer,
    SUM(amount) AS total_spent
FROM orders
GROUP BY customer
HAVING total_spent > 500;

-- 3. 5月份每天的订单金额统计
SELECT
    order_date,
    COUNT(*) AS order_count,
    SUM(amount) AS daily_total
FROM orders
GROUP BY order_date
ORDER BY order_date;

-- 4. 各状态订单的占比
SELECT
    status,
    COUNT(*) AS count,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM orders), 2) AS percentage
FROM orders
GROUP BY status
ORDER BY count DESC;

-- 5. 消费最高的客户（子查询方式）
SELECT customer, SUM(amount) AS total_spent
FROM orders
GROUP BY customer
ORDER BY total_spent DESC
LIMIT 1;
```

---

## 本章小结

| 概念 | 要点 |
|------|------|
| ORDER BY | 排序，ASC升序（默认），DESC降序，支持多字段 |
| LIMIT OFFSET | 分页：`LIMIT M OFFSET (N-1)*M` |
| DISTINCT | 去重，作用于所有SELECT列的组合 |
| 聚合函数 | COUNT/SUM/AVG/MAX/MIN，将多行压缩为一行 |
| GROUP BY | 分组聚合，SELECT中非聚合列必须在GROUP BY中 |
| HAVING | 分组后过滤，作用于聚合结果 |
| CASE WHEN | SQL中的if-else，可配合GROUP BY做条件分组 |
| NULL处理 | IS NULL判断，IFNULL/COALESCE给默认值 |
| 子查询 | 查询嵌套查询，IN/EXISTS两种主要写法 |
| 执行顺序 | FROM → WHERE → GROUP BY → HAVING → SELECT → ORDER BY → LIMIT |

---

## 自测题

1. **一个 `employees` 表有 `department`（部门）和 `salary`（薪资）列。写出SQL：按部门统计人数和平均薪资，只显示平均薪资超过10000的部门，按平均薪资降序排列。**

2. **下面这条SQL有什么问题？**
   ```sql
   SELECT department, name, AVG(salary)
   FROM employees
   GROUP BY department;
   ```

3. **`WHERE` 和 `HAVING` 的区别是什么？什么时候必须用 HAVING？**

<details>
<summary>参考答案（做完再看）</summary>

1. ```sql
SELECT
    department,
    COUNT(*) AS emp_count,
    AVG(salary) AS avg_salary
FROM employees
GROUP BY department
HAVING avg_salary > 10000
ORDER BY avg_salary DESC;
```

2. `name` 不在 GROUP BY 中，也不是聚合函数。GROUP BY department 后每个部门只剩一行，但name有多个值（每个员工一个名字），MySQL不知道该选哪个，这种行为是不确定的（其他数据库会直接报错）。正确的做法是去掉name列，或者把name也加入GROUP BY。

3. WHERE在分组前过滤原始行，HAVING在分组后过滤聚合结果。当筛选条件依赖聚合函数（如AVG、SUM、COUNT的结果）时，必须用HAVING。例如"平均薪资大于10000的部门"——平均薪资是聚合计算出来的，在分组完成前不存在，所以WHERE做不到，只能用HAVING。
</details>