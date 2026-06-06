# 第51章 · SQL基础：DDL与DML

> "仓库建好了，现在是时候在里面搭货架、搬货、改标签了。SQL就是跟仓库管理员交流的标准语言——你说'把第三排货架上红色的箱子全搬过来'，管理员听得懂，机器也听得懂。这门语言比你想象的简单，也比你想象的强大。"

---

## 51.1 SQL是什么

SQL的全称是**Structured Query Language**（结构化查询语言）。注意官方发音：不是"S-Q-L"三个字母念，而是读作"sequel"。但大部分中国程序员直接念"S-Q-L"，面试时两种发音都行。

SQL是你的仓库管理员指令手册。你对着MySQL输入：

```sql
SELECT name, phone FROM users WHERE age > 18;
```

翻译成管理员能懂的话就是："去users货架上，把所有age大于18的箱子打开，把里面的name和phone拿出来给我。"

**关键认知**：SQL是共通的。你学会了MySQL的SQL，去用PostgreSQL、Oracle、SQL Server时，90%的语句一模一样。就像你会开大众，去开丰田只需要适应一下方向盘手感——核心操作不变。

---

## 51.2 SQL的五大分类

SQL语句按功能分为五大类，理解这个分类会让你的知识体系非常清晰：

| 分类 | 英文 | 作用 | 比喻 | 核心动词 |
|------|------|------|------|----------|
| DDL | Data Definition Language | 定义数据结构 | 搭货架、拆货架 | CREATE / ALTER / DROP / TRUNCATE |
| DML | Data Manipulation Language | 操作数据内容 | 往箱子里放东西、改贴纸 | INSERT / UPDATE / DELETE |
| DQL | Data Query Language | 查询数据 | 在仓库里找东西 | SELECT |
| DCL | Data Control Language | 控制权限 | 给员工发钥匙、收钥匙 | GRANT / REVOKE |
| TCL | Transaction Control Language | 控制事务 | 批量操作确认/回滚按钮 | COMMIT / ROLLBACK / SAVEPOINT |

本章重点讲DDL和DML，下一章讲DQL。DCL和TCL在后面事务章节详细展开。

> **新手记忆法**：DDL管"货架长什么样"，DML管"货架上有什么东西"，DQL管"帮我找一下东西在哪"。

---

## 51.3 数据类型

搭建货架之前，你得先想好每个格子装什么东西。MySQL提供了丰富的"格子类型"：

### 整数类型

| 类型 | 字节数 | 有符号范围 | 无符号范围 |
|------|--------|-----------|-----------|
| TINYINT | 1 | -128 ~ 127 | 0 ~ 255 |
| SMALLINT | 2 | -32768 ~ 32767 | 0 ~ 65535 |
| MEDIUMINT | 3 | -838万 ~ 838万 | 0 ~ 1677万 |
| INT | 4 | -21亿 ~ 21亿 | 0 ~ 42亿 |
| BIGINT | 8 | -922京 ~ 922京 | 0 ~ 1844京 |

**选择原则**：用最小的够用类型。比如年龄用TINYINT（没人能活256岁以上），用户ID用INT或BIGINT（看用户量）。

### 小数类型

| 类型 | 说明 |
|------|------|
| FLOAT / DOUBLE | 近似值，有精度损失 |
| DECIMAL(M, D) | 精确值，M=总位数，D=小数位数 |

**金额永远用DECIMAL**。比如 `DECIMAL(10, 2)` 表示总共10位，其中2位小数（最大 99999999.99）。用FLOAT存钱，算着算着就会出现0.01的误差——财务对不上账你就等着被叫去喝茶。

### 字符串类型

| 类型 | 最大长度 | 存储方式 |
|------|---------|----------|
| CHAR(N) | 255字符 | 定长，不管存几个字符都占N个位置 |
| VARCHAR(N) | 65535字节 | 变长，存几个占几个+1~2字节开销 |
| TEXT | 65535字节 | 长文本，不参与排序和索引 |
| LONGTEXT | 4GB | 超长文本 |

**CHAR vs VARCHAR 比喻**：

CHAR是**固定格子**——你说"这个格子放10个字"，它就造一个10个字宽的格子。你放"你好"两个字，剩下8个空位用空格填满。好处是存取快（位置固定，不用计算），坏处是浪费空间。

VARCHAR是**弹性盒子**——你说"这个盒子最多装10个字"，它就会按你实际放了多少字来伸缩。放"你好"就占2个字的物理空间。好处是省空间，坏处是更新数据时如果从"你好"改成"你好世界你好世界"，盒子要扩容，有一定开销。

**使用建议**：固定长度的用CHAR（手机号、身份证、MD5值），长度差异大的用VARCHAR（用户名、邮箱、地址），文章内容用TEXT。

### 日期时间类型

| 类型 | 格式 | 范围 | 说明 |
|------|------|------|------|
| DATE | YYYY-MM-DD | 1000-01-01 ~ 9999-12-31 | 生日、日期 |
| TIME | HH:MM:SS | -838:59:59 ~ 838:59:59 | 时长、时刻 |
| DATETIME | YYYY-MM-DD HH:MM:SS | 1000-01-01 ~ 9999-12-31 | 最常用，创建时间/更新时间 |
| TIMESTAMP | YYYY-MM-DD HH:MM:SS | 1970-01-01 ~ 2038-01-19 | 自动时区转换 |
| YEAR | YYYY | 1901 ~ 2155 | 年份 |

**DATETIME vs TIMESTAMP**：TIMESTAMP会跟着服务器时区自动转换——中国服务器存的 `2024-01-01 12:00:00`，美国服务器读出来变成前一天。DATETIME则忠实记录，不受时区影响。如果用TIMESTAMP，注意**2038年溢出问题**——到了2038年1月19日，TIMESTAMP存不下更大的时间了。新的应用建议用DATETIME。

🤔 **想多一点**：很多老系统用户表的生日字段用TIMESTAMP——这些系统将在2038年"翻车"。如果你的面试官问"TIMESTAMP和DATETIME的区别"，把时区转换和2038问题说出来，他会觉得你真的懂。

---

## 51.4 CREATE TABLE：建造货架

建表是使用数据库的第一步。以下是一个完整的用户表建表语句：

```sql
CREATE TABLE users (
    id         BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    username   VARCHAR(50)     NOT NULL,
    email      VARCHAR(100)    NOT NULL,
    password   VARCHAR(255)    NOT NULL,
    phone      CHAR(11)        NOT NULL DEFAULT '',
    age        TINYINT UNSIGNED         DEFAULT 0,
    balance    DECIMAL(12, 2)  NOT NULL DEFAULT 0.00,
    is_active  TINYINT(1)      NOT NULL DEFAULT 1,
    created_at DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uk_email (email),
    UNIQUE KEY uk_username (username),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

我们逐字段拆解：

### 字段定义

**`id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT`**

| 修饰符 | 含义 |
|--------|------|
| BIGINT | 8字节大整数 |
| UNSIGNED | 无符号（没有负数），范围翻倍到 0~1844京 |
| NOT NULL | 不允许为空 |
| AUTO_INCREMENT | 自动递增——每插入一行，id自动+1 |

`id` 是主键（唯一标识表中每一行记录的字段，详见附录I），作为每条记录的唯一标识。就像每个公民有唯一的身份证号一样。

**`username VARCHAR(50) NOT NULL`**

用户名，最长50个字符。`NOT NULL` 表示这个格子里必须放东西，不能空着。

**`phone CHAR(11) NOT NULL DEFAULT ''`**

手机号是固定11位的，用CHAR比VARCHAR更合适。`DEFAULT ''` 表示如果插入时没填，默认为空字符串。

**`age TINYINT UNSIGNED DEFAULT 0`**

年龄：范围 0~255。没有 `NOT NULL`，因为用户可以选不填年龄——此时值为NULL。

**`balance DECIMAL(12, 2) NOT NULL DEFAULT 0.00`**

账户余额：精确存储，总共12位，2位小数。

**`is_active TINYINT(1) NOT NULL DEFAULT 1`**

是否激活：用1字节存布尔值（0=冻结，1=正常）。MySQL没有真正的BOOLEAN类型，`TINYINT(1)` 是惯例。

**`created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP`**

创建时间：如果不手动指定，自动填当前时间。

**`updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP`**

更新时间：创建时自动填当前时间，**每次修改本行数据时自动更新**。这是写代码时最容易忘、但最实用的字段——你每次排查数据问题都要看"这个记录是什么时候改的"。

### 约束

```sql
PRIMARY KEY (id)
```
主键约束。唯一标识每一行，自动创建聚簇索引。一个表只能有一个主键。

```sql
UNIQUE KEY uk_email (email)
```
唯一约束。email字段的值在整张表中不能重复。`uk_email` 是这个约束的名称（`uk` = unique key），起个好名字方便后续排查。

```sql
UNIQUE KEY uk_username (username)
```
同样，用户名也不能重复。

```sql
INDEX idx_created_at (created_at)
```
普通索引。给 `created_at` 字段加索引，查询"最近注册的用户"时会快很多。`idx_` 前缀表示索引。

### 建表语句尾部

```sql
ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

- `ENGINE=InnoDB`：存储引擎用InnoDB（支持事务和行锁）。
- `DEFAULT CHARSET=utf8mb4`：默认字符集用utf8mb4。
- `COLLATE=utf8mb4_unicode_ci`：排序规则，不区分大小写。

**创建一个表后，用以下命令查看结构：**

```sql
DESC users;
```

```
+------------+---------------------+------+-----+-------------------+-------------------+
| Field      | Type                | Null | Key | Default           | Extra             |
+------------+---------------------+------+-----+-------------------+-------------------+
| id         | bigint unsigned     | NO   | PRI | NULL              | auto_increment    |
| username   | varchar(50)         | NO   | UNI | NULL              |                   |
| email      | varchar(100)        | NO   | UNI | NULL              |                   |
...
```

---

## 51.5 ALTER TABLE：仓库装修

货架搭好后，发现漏了个字段？或者某个字段太小了？ALTER TABLE就是让你改货架规格的。

### 新增字段

```sql
ALTER TABLE users ADD COLUMN avatar VARCHAR(255) DEFAULT '' AFTER email;
```

在email字段后面新增一个 `avatar`（头像URL）字段。

**`AFTER email`** 指定位置。如果不写，默认加到最后一列。

### 修改字段

```sql
ALTER TABLE users MODIFY COLUMN username VARCHAR(100) NOT NULL;
```

把用户名最大长度从50改成100。

### 重命名字段

```sql
ALTER TABLE users CHANGE COLUMN username user_name VARCHAR(100) NOT NULL;
```

`CHANGE` 可以同时改名和改类型。`MODIFY` 只能改类型。

### 删除字段

```sql
ALTER TABLE users DROP COLUMN avatar;
```

**危险操作**：这个列的数据全部丢失，不可恢复！

### 新增索引

```sql
ALTER TABLE users ADD INDEX idx_age (age);
```

### 删除索引

```sql
ALTER TABLE users DROP INDEX idx_age;
```

🤔 **想多一点**：在百万级数据量的表上执行ALTER TABLE要谨慎——有些操作会**锁表**，期间所有读写都被阻塞，你的网站直接挂掉。大型系统通常用 `pt-online-schema-change` 这样的工具在线修改表结构。但在学习阶段，想怎么改就怎么改。

---

## 51.6 DROP / TRUNCATE / DELETE：三种删除的区别

这三种操作都能"删除"东西，但后果完全不同：

| 操作 | 删除对象 | 比喻 | 能否回滚 | 是否保留表结构 | 速度 |
|------|---------|------|----------|---------------|------|
| DROP TABLE | 整个表 | 把整个货架拆掉扔了 | 否 | 否 | 快 |
| TRUNCATE TABLE | 表中所有行 | 把货架上所有箱子倒掉 | 否 | 是 | 极快 |
| DELETE FROM | 指定行或所有行 | 一个一个箱子搬走 | 是（InnoDB） | 是 | 慢 |

```sql
DROP TABLE users;
```

整个users表从数据库中消失，货架没了，数据也没了。重新创建表的话，AUTO_INCREMENT的计数器从头开始。

```sql
TRUNCATE TABLE users;
```

货架还在，但上面所有的箱子清空了。AUTO_INCREMENT计数器**重置为1**。因为是DDL操作，不可回滚。

```sql
DELETE FROM users WHERE id = 3;
```

只删除id=3这一行。可以回滚（在事务中）。AUTO_INCREMENT计数器**不重置**。

**关键区别**：TRUNCATE本质上是"删掉旧文件，新建一个空文件"——所以极快。DELETE是一行一行删（要走事务日志），所以数据量大时很慢。

---

## 51.7 INSERT：往货架上放东西

### 插入单行

```sql
INSERT INTO users (username, email, password, phone, age, balance)
VALUES ('zhangsan', 'zhangsan@example.com', 'hashed_pwd', '13800001111', 25, 100.00);
```

**注意字段列表和值的顺序必须一一对应**。id不用填——AUTO_INCREMENT会自动生成。created_at也不用填——有DEFAULT CURRENT_TIMESTAMP。

如果所有字段（除了id）都要填值，而且顺序和建表顺序一致，可以省略字段列表：

```sql
INSERT INTO users
VALUES (NULL, 'lisi', 'lisi@example.com', 'hashed_pwd', '13900002222', 28, 200.00, 1, NOW(), NOW());
```

**不推荐省略字段列表**——以后有人加了个字段（比如加在中间），你的INSERT顺序就对不上了。

### 插入多行

```sql
INSERT INTO users (username, email, password, phone)
VALUES
    ('user1', 'user1@test.com', 'pwd1', '13800000001'),
    ('user2', 'user2@test.com', 'pwd2', '13800000002'),
    ('user3', 'user3@test.com', 'pwd3', '13800000003');
```

一次插入多行比多次插入单行效率高很多——省去了多次网络往返和事务开销。

### INSERT ... ON DUPLICATE KEY UPDATE

如果插入的username或email重复了怎么办？默认报错。但你可以让它自动变成更新操作：

```sql
INSERT INTO users (username, email, password, phone)
VALUES ('zhangsan', 'zhangsan_new@example.com', 'newpwd', '13800001111')
ON DUPLICATE KEY UPDATE
    email = VALUES(email),
    password = VALUES(password);
```

如果 `zhangsan` 这个用户名已经存在（触发了UNIQUE约束），就更新email和password字段；如果不存在，就正常插入。这在"插入或更新"场景非常实用。

---

## 51.8 UPDATE：修改货架上的标签

```sql
UPDATE users SET age = 26, balance = 150.00 WHERE id = 1;
```

把id=1的用户年龄改成26，余额改成150。

**红色警报：写UPDATE时第一个想到的必须是WHERE！**

如果你忘了WHERE：

```sql
UPDATE users SET is_active = 0;
```

**全表所有用户的is_active都会被改成0**——你的所有用户瞬间被"冻结"了。这个错误在真实生产环境中发生过无数次，有些甚至上了新闻（程序员删表跑路、误操作冻结全站用户）。

**安全做法**：

1. 写UPDATE时先写WHERE再写SET。
2. 在WHERE中用主键或唯一索引定位（`WHERE id = 1`），确保只影响一行。
3. 如果担心误操作，先用SELECT验证WHERE条件的结果：

```sql
SELECT id, username FROM users WHERE id = 1;
```

确认返回的是你想改的那一行，再执行UPDATE。

### 用表达式更新

```sql
UPDATE users SET balance = balance + 100.00 WHERE id = 1;
```

直接在当前余额上加100。这比先SELECT查出余额、在代码里加、再UPDATE回去安全得多——因为不存在并发问题。

---

## 51.9 DELETE：移走箱子

```sql
DELETE FROM users WHERE id = 100;
```

**和UPDATE一样，DELETE也必须加WHERE！**

```sql
DELETE FROM users;
```

这一句会清空users表的所有数据。如果不加WHERE，30万用户数据一秒消失。

### 软删除 vs 硬删除

**硬删除**（DELETE）直接物理删除数据，不可恢复。用户误删了文章，你只能从备份里找。

**软删除**是行业最佳实践——不真删数据，只标记"已删除"：

建表时加一个字段：

```sql
ALTER TABLE users ADD COLUMN deleted_at DATETIME DEFAULT NULL;
```

"删除"时不执行DELETE，而是：

```sql
UPDATE users SET deleted_at = NOW() WHERE id = 100;
```

查询时自动过滤掉已删除的：

```sql
SELECT * FROM users WHERE deleted_at IS NULL;
```

软删除的好处：
- 数据可恢复（把 `deleted_at` 设为NULL就行）
- 误删时保留了"案发现场"
- 满足合规需求（某些行业要求数据不可物理删除）
- 用户可以进"回收站"

唯一缺点：数据量持续增长，需要定期清理真正无用的软删除数据。

---

## 本章小结

| 知识点 | 要点 |
|--------|------|
| SQL五大分类 | DDL（结构）/ DML（数据）/ DQL（查询）/ DCL（权限）/ TCL（事务） |
| 数据类型 | 整数用最小够用型、金额必用DECIMAL、CHAR定长VARCHAR变长、DATETIME推荐 |
| CREATE TABLE | 逐字段定义类型+约束，指定ENGINE和CHARSET |
| ALTER TABLE | 改结构：ADD/MODIFY/CHANGE/DROP COLUMN |
| DROP vs TRUNCATE vs DELETE | DROP拆货架、TRUNCATE倒箱子不可回滚、DELETE逐行删可回滚 |
| INSERT | 单行/多行/ON DUPLICATE KEY UPDATE（插入或更新） |
| UPDATE | **必须先写WHERE！** 用表达式比先查再改更安全 |
| DELETE | **必须先写WHERE！** 推荐软删除（deleted_at字段标记） |

> 🚀 下一章：第52章 · SQL进阶：查询与聚合。货架有了，东西也放进去了——现在到了数据库最核心的环节：怎么用SELECT语句在几十万条数据里精准地找到你想要的东西。

---
[← 上一章：50-数据库基础与MySQL](50-数据库基础与MySQL/) | [下一章：52-SQL进阶：查询与聚合 →](52-SQL进阶：查询与聚合/)
