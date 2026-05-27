# 第8章：关系型数据库与SQL必知必会

## 本章目标

学完本章你将能够：

- 独立完成MySQL 8.0的安装与基本配置
- 按照数据库设计范式规范地设计表结构
- 熟练编写DDL（建库建表）、DML（增删改）、DQL（查）三类SQL语句
- 理解并正确使用JOIN进行多表联合查询
- 理解索引的B+Tree原理，能使用EXPLAIN分析查询性能
- 理解事务的ACID特性与隔离级别
- 为后续JDBC编程和第9章的EMS v2项目打下扎实的数据库基础

---

## 8.1 MySQL安装与配置

### 8.1.1 MySQL 8.0简介

MySQL是世界上最流行的开源关系型数据库管理系统（RDBMS），由Oracle公司维护。本书选择MySQL 8.0版本，它是目前（截至2026年）最成熟稳定的版本，拥有以下突出特性：

- **窗口函数**：支持ROW_NUMBER()、RANK()等分析函数
- **CTE（公共表表达式）**：支持WITH RECURSIVE递归查询
- **更好的JSON支持**：原生JSON数据类型与丰富的JSON函数
- **原子DDL**：ALTER TABLE等操作支持原子性回滚
- **caching_sha2_password**：默认认证插件，安全性大幅提升

### 8.1.2 Windows平台安装（重点）

**步骤1：下载安装包**

访问MySQL官网 https://dev.mysql.com/downloads/mysql/ ，选择 **Windows (x86, 64-bit), MSI Installer**（约400MB）。推荐下载离线安装包而非在线安装器，避免安装过程中因网络问题失败。

> 🚨 **坑点：不要下载ZIP Archive版本**
> - ZIP解压版需要手动初始化数据目录、注册Windows服务、配置my.ini，步骤繁多容易出错
> - 初学者强烈建议使用MSI安装程序，它会自动完成上述所有步骤

**步骤2：运行安装程序**

双击msi文件，选择 **Custom（自定义）** 安装类型：

- 必选组件：MySQL Server 8.0.xx、MySQL Workbench（图形化管理工具）
- 可选组件：MySQL Shell（高级命令行工具）、Samples and Examples（示例数据库）

**步骤3：配置MySQL Server**

安装向导会自动进入配置阶段：

1. **High Availability**：选择"Standalone MySQL Server"（单机模式）
2. **Type and Networking**：
   - Config Type：选择"Development Computer"（开发机，内存占用最小）
   - Port：保持默认3306
   - 勾选"Open Windows Firewall port for network access"（允防火墙通过）
3. **Authentication Method**：选择"Use Strong Password Encryption for Authentication"（默认的caching_sha2_password）

> 🚨 **坑点：MySQL 8.0密码加密方式变了！**
> - MySQL 8.0默认认证插件是 **caching_sha2_password**，而MySQL 5.x是 **mysql_native_password**
> - **现象**：如果你用Navicat 11及以下版本、旧版DBeaver、甚至某些老旧的编程语言驱动连接MySQL 8.0，会报错"Authentication plugin 'caching_sha2_password' cannot be loaded"
> - **解决方案（三选一）**：
>   1. **升级客户端**（推荐）：升级Navicat到12+版本，或使用DBeaver（免费跨平台，天然支持MySQL 8.0）
>   2. **修改认证插件**：在安装时选择"Use Legacy Authentication Method"，或之后执行：
>      ```sql
>      ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY '你的密码';
>      FLUSH PRIVILEGES;
>      ```
>   3. **配置连接参数**：在JDBC URL中添加 `defaultAuthenticationPlugin=mysql_native_password`

4. **Accounts and Roles**：设置root密码（**务必记住！**）。可以点击"Add User"额外创建一个普通用户用于开发。
5. **Windows Service**：保持默认（服务名MySQL80，开机自启）。

**步骤4：验证安装**

打开命令提示符（Win+R → cmd），输入：

```bash
mysql -u root -p
```

输入密码后出现 `mysql>` 提示符，输入 `SELECT VERSION();` 验证：

```sql
mysql> SELECT VERSION();
+-----------+
| VERSION() |
+-----------+
| 8.0.xx    |
+-----------+
1 row in set (0.00 sec)
```

### 8.1.3 Mac与Linux安装速览

**Mac (Homebrew)**：

```bash
brew install mysql
brew services start mysql
mysql_secure_installation  # 安全配置向导（设置密码、删除匿名用户等）
```

**Ubuntu/Debian**：

```bash
sudo apt update
sudo apt install mysql-server
sudo mysql_secure_installation
```

**CentOS/RHEL**：

```bash
sudo yum install mysql-server
sudo systemctl start mysqld
sudo grep 'temporary password' /var/log/mysqld.log  # 查看临时密码
sudo mysql_secure_installation
```

### 8.1.4 客户端工具推荐

| 工具 | 类型 | 价格 | 推荐理由 |
|------|------|------|----------|
| **DBeaver** | 桌面客户端 | 免费 | 跨平台，支持几乎所有数据库，界面友好，自动识别MySQL 8.0认证方式 |
| **IDEA Database工具** | IDE内置 | Ultimate收费 | 无需切换窗口，SQL补全强大，支持直接查看ER图 |
| **MySQL Workbench** | 官方工具 | 免费 | 官方出品，ER图设计功能强大，但界面略显臃肿 |
| **Navicat** | 桌面客户端 | 收费 | 功能全面，但需12+版本才支持MySQL 8.0 |

本书推荐使用 **DBeaver** 作为日常数据库管理工具。

### 8.1.5 基本命令速查

连接到MySQL后，以下命令是你每天都会用到的：

```sql
SHOW DATABASES;                    -- 查看所有数据库
CREATE DATABASE mydb;              -- 创建数据库
USE mydb;                          -- 切换到某个数据库
SHOW TABLES;                       -- 查看当前库的所有表
DESC table_name;                   -- 查看表结构（DESCRIBE的简写）
SHOW CREATE TABLE table_name;      -- 查看建表完整DDL
SELECT DATABASE();                 -- 查看当前在哪个库
STATUS;                            -- 查看连接状态（版本、字符集等）
```

---

## 8.2 数据库设计基础

### 8.2.1 从需求到数据库表

在动手写SQL之前，我们需要先回答一个问题：**数据应该怎样组织？**

以一个简化版的"企业员工管理系统"为例，原始需求可能是这样的：

- 公司有多个部门，每个部门有多名员工
- 每位员工有姓名、年龄、邮箱、薪资、入职日期
- 一个员工只能属于一个部门

如果直接把所有信息写在一张纸上，可能是这样的：

| 姓名 | 年龄 | 部门名 | 部门地址 | 薪资 | 邮箱 |
|------|------|--------|----------|------|------|
| 张三 | 28 | 技术部 | 3号楼 | 15000 | zhang@x.com |
| 李四 | 32 | 技术部 | 3号楼 | 20000 | li@x.com |
| 王五 | 25 | 市场部 | 5号楼 | 12000 | wang@x.com |

发现问题了吗？"技术部"的地址"3号楼"重复出现了两次。如果技术部搬到了6号楼，你需要修改所有属于技术部的员工记录——这就是**数据冗余**。

**数据库设计的核心目标就是：减少冗余、保证一致性、方便查询。**

### 8.2.2 数据库设计四步骤

数据库设计通常遵循以下流程：

```
需求分析 → 概念设计(ER图) → 逻辑设计(范式化) → 物理设计(建表SQL)
```

**Step 1 - 需求分析**：找出系统中的"实体"和它们之间的关系

从上面的需求中，我们能识别出：
- **实体**：员工（Employee）、部门（Department）
- **关系**：员工"属于"部门（一个部门有多个员工，一个员工只属于一个部门）→ **1:N关系**

**Step 2 - 概念设计（ER图）**：

ER图（Entity-Relationship Diagram）是数据库设计的"蓝图"，包含三个核心要素：

- **实体（Entity）**：用矩形表示，代表一个数据对象（如"员工"、"部门"）
- **属性（Attribute）**：用椭圆表示，代表实体的特征（如"姓名"、"薪资"）
- **关系（Relationship）**：用菱形表示，代表实体之间的联系

```
      姓名                      部门名
        ↙                         ↙
      ┌──────┐    属于    ┌──────┐
      │ 员工 │──────────→│ 部门 │
      └──────┘  1:N      └──────┘
      ↗     ↘            ↗     ↘
   年龄   薪资         地址   成立日期
```

- **1:N**（一对多）：一个部门有多个员工，一个员工只属于一个部门，这是最常见的关系类型
- **1:1**（一对一）：一个员工只有一个工位，一个工位只属于一个员工（比较少见，通常可以合并为一张表）
- **M:N**（多对多）：一个学生选多门课，一门课被多个学生选（需要中间表来实现，如"选课表"）

**Step 3 - 逻辑设计（三范式）**：

范式（Normal Form）是一套用来消除数据冗余的规则，共有6个范式，日常开发中掌握前三个就足够了。

---

**第一范式（1NF — 列原子性）**

定义：表中的每一列都是不可再拆分的最小数据单元。

> 🚨 **反例（违反1NF）**：
>
> | id | name | address |
> |----|------|---------|
> | 1 | 张三 | 北京市朝阳区XX路100号 |
>
> 地址列包含了省、市、区、路等多个信息，不满足原子性。

**正例**：将地址拆分为多列

| id | name | province | city | district | street |
|----|------|----------|------|----------|--------|
| 1 | 张三 | 北京市 | 朝阳区 | - | XX路100号 |

> 实际开发中，是否拆分取决于业务需求。如果系统从不按省/市筛选，保持为一个"地址"列也可以——过度拆分和过度合并都是问题。

---

**第二范式（2NF — 消除部分依赖）**

定义：在满足1NF的基础上，非主键列必须**完全依赖**于主键的全部字段（而非部分字段）。

> 🚨 **反例（违反2NF）**：假设选课表用（学号, 课程号）作为联合主键
>
> | 学号(PK) | 课程号(PK) | 学生姓名 | 课程名 | 成绩 |
> |----------|-----------|----------|--------|------|
> | 001 | C01 | 张三 | 数学 | 90 |
> | 001 | C02 | 张三 | 英语 | 85 |
>
> "学生姓名"只依赖于"学号"（主键的一部分），这就是**部分依赖**。

**正例**：将学生信息拆分到独立的"学生表"

| 学号(PK) | 姓名 |
|----------|------|
| 001 | 张三 |

| 学号(PK) | 课程号(PK) | 成绩 |
|----------|-----------|------|
| 001 | C01 | 90 |
| 001 | C02 | 85 |

---

**第三范式（3NF — 消除传递依赖）**

定义：在满足2NF的基础上，非主键列不能**传递依赖**于主键（即非主键列之间不能有依赖关系）。

> 🚨 **反例（违反3NF）**：
>
> | 学号(PK) | 姓名 | 班级 | 班主任 |
> |----------|------|------|--------|
> | 001 | 张三 | 一班 | 王老师 |
> | 002 | 李四 | 一班 | 王老师 |
>
> 学号 → 班级 → 班主任，"班主任"传递依赖于"学号"（通过"班级"这个中间列）

**正例**：班级信息独立为一张表

| 学号(PK) | 姓名 | 班级ID |
|----------|------|--------|
| 001 | 张三 | 1 |
| 002 | 李四 | 1 |

| 班级ID(PK) | 班级名 | 班主任 |
|------------|--------|--------|
| 1 | 一班 | 王老师 |

---

> 🚨 **坑点：过度范式化**
> - 范式化可以减少冗余，但也会导致查询时需要JOIN大量表，性能严重下降
> - **适当反范式化**（冗余换性能）：比如订单表中直接存"商品名"和"商品单价"，就算商品表中的名称和价格改了，已生成的订单数据也不应该变（这是业务快照的真实需求）
> - 记住一条经验法则：**OLTP（在线事务处理）系统范式化为主，OLAP（在线分析处理）系统适当反范式化**

**Step 4 - 物理设计**：将逻辑设计转化为具体数据库的建表语句（详见8.3节）。

### 8.2.3 EMS项目的数据库设计

回到我们的EMS员工管理系统，按照上述设计过程：

**需求分析**：
- 管理员工信息（姓名、年龄、部门、薪资、邮箱、入职日期）
- 员工必须属于一个部门

**ER图**：

```
    name──→  ┌──────────┐
    age ──→  │ Employee │──→ department
   email──→ │          │──→ salary
hire_date─→└──────────┘──→ hire_date
```

**表结构设计**：

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | BIGINT | PRIMARY KEY, AUTO_INCREMENT | 主键自增 |
| name | VARCHAR(50) | NOT NULL | 员工姓名 |
| age | INT | CHECK(age>=18 AND age<=65) | 年龄 |
| department | VARCHAR(50) | - | 所属部门 |
| salary | DECIMAL(10,2) | NOT NULL DEFAULT 0.00 | 薪资（精确到分） |
| email | VARCHAR(100) | UNIQUE | 邮箱（唯一） |
| hire_date | DATETIME | DEFAULT CURRENT_TIMESTAMP | 入职日期 |

---

## 8.3 DDL — 数据定义语言

DDL（Data Definition Language）是用于定义数据库结构的SQL语句，主要包括 `CREATE`、`ALTER`、`DROP`。

### 8.3.1 创建数据库

```sql
CREATE DATABASE ems
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_general_ci;
```

> 🚨 **坑点：utf8 还是 utf8mb4？**
> - MySQL中 `utf8` 是**阉割版**的UTF-8，最多只支持3个字节，无法存储emoji表情（😀=4字节）和部分生僻汉字（如"𠮷"）
> - `utf8mb4` 才是真正的UTF-8实现，支持1-4字节的完整Unicode字符
> - **永远使用 `utf8mb4`**，这是MySQL官方从8.0开始逐步废弃utf8别名的重要原因
> - 验证差异：尝试在utf8表中插入emoji → `ERROR 1366: Incorrect string value`

`COLLATE utf8mb4_general_ci` 指定排序规则：
- `utf8mb4_general_ci`：通用规则，不区分大小写（`ci` = case insensitive），性能较好
- `utf8mb4_unicode_ci`：基于Unicode标准，排序更准确但稍慢

### 8.3.2 数据类型选择指南

MySQL支持丰富的数据类型，以下是你需要掌握的核心类型：

**数值类型**：

| 类型 | 大小 | 范围 | 使用场景 |
|------|------|------|----------|
| **TINYINT** | 1字节 | -128~127 | 年龄、状态码 |
| **INT** | 4字节 | -21亿~21亿 | 一般整数、ID |
| **BIGINT** | 8字节 | 极大 | 大数据量的主键 |
| **DECIMAL(M,D)** | 可变 | 精确小数 | **金额！** |
| **FLOAT/DOUBLE** | 4/8字节 | 近似值 | 科学计算 |

> 🚨 **坑点：金额绝对不能用FLOAT或DOUBLE！**
> - FLOAT和DOUBLE是近似值类型，会有精度丢失
> - 例如：0.1+0.2 在DOUBLE中可能等于 0.30000000000000004
> - 存储薪资、价格等任何与钱有关的数值，必须使用 `DECIMAL(10,2)`（总共10位，小数点后2位）

**字符串类型**：

| 类型 | 特点 | 使用场景 |
|------|------|----------|
| **CHAR(N)** | 定长，最多255字符 | 身份证号、手机号（长度固定） |
| **VARCHAR(N)** | 变长，最多65535字节 | 姓名、邮箱、地址（长度不定） |
| **TEXT** | 长文本，最多65535字符 | 文章内容、简介 |
| **LONGTEXT** | 超大文本，4GB | 富文本、日志 |

> 🚨 **坑点：VARCHAR(255)**
> - 很多老代码习惯写 `VARCHAR(255)`，因为历史上VARCHAR最大长度的索引限制
> - 实际上按需设定即可：姓名用 `VARCHAR(50)`，邮箱用 `VARCHAR(100)`
> - 255不是魔法数字，按业务需求来

**日期时间类型**：

| 类型 | 范围 | 精度 | 注意 |
|------|------|------|------|
| **DATE** | 1000-01-01 ~ 9999-12-31 | 天 | 生日、日期 |
| **DATETIME** | 1000-01-01 00:00:00 ~ 9999-12-31 23:59:59 | 秒（可到微秒） | **推荐** |
| **TIMESTAMP** | 1970-01-01 ~ 2038-01-19 | 秒 | 受时区影响 |

> 🚨 **坑点：DATETIME vs TIMESTAMP**
> - TIMESTAMP存的是UTC时间戳（1970-01-01起的秒数），读取时按当前时区转换
> - TIMESTAMP有**2038年问题**（32位整数溢出），不适用于未来日期
> - **建议：统一使用DATETIME**，它不受时区影响，范围也更大
> - 如果你在2026年存储了一个合同到期日为2040年的数据到TIMESTAMP列 → 报错！

### 8.3.3 约束详解

约束（Constraint）保证数据的完整性和准确性：

```sql
-- 主键约束：唯一标识一行，自动创建索引
PRIMARY KEY (id)

-- 外键约束：保证引用的数据存在
FOREIGN KEY (dept_id) REFERENCES department(id)

-- 唯一约束：不允许重复值（NULL可以重复）
UNIQUE (email)

-- 非空约束：不允许NULL值
NOT NULL

-- 默认值：插入时不指定则使用默认值
DEFAULT 0.00

-- 检查约束（MySQL 8.0.16+支持）：自定义校验规则
CHECK (age >= 18 AND age <= 65)
```

### 8.3.4 创建employee表

将前面所有的知识整合起来，这是EMS项目的核心表DDL：

```sql
USE ems;

CREATE TABLE employee (
    id          BIGINT          PRIMARY KEY AUTO_INCREMENT  COMMENT '员工ID',
    name        VARCHAR(50)     NOT NULL                    COMMENT '姓名',
    age         INT             CHECK (age >= 18 AND age <= 65) COMMENT '年龄',
    department  VARCHAR(50)                                 COMMENT '所属部门',
    salary      DECIMAL(10,2)   NOT NULL DEFAULT 0.00       COMMENT '月薪',
    email       VARCHAR(100)    UNIQUE                      COMMENT '邮箱（唯一）',
    hire_date   DATETIME        DEFAULT CURRENT_TIMESTAMP   COMMENT '入职日期',
    
    INDEX idx_department (department),
    INDEX idx_salary (salary),
    INDEX idx_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='员工信息表';
```

逐行解释关键设计决策：
- **`id BIGINT PRIMARY KEY AUTO_INCREMENT`**：自增主键，BIGINT是为了未来可能的海量数据
- **`salary DECIMAL(10,2)`**：10位总长度、2位小数（最大99999999.99，对于薪资足够）
- **`email UNIQUE`**：邮箱全局唯一，防止重复录入
- **`hire_date DEFAULT CURRENT_TIMESTAMP`**：不填入职时间则自动取当前时间
- **`ENGINE=InnoDB`**：InnoDB支持事务、行级锁、外键，是MySQL 8.0的默认引擎
- **`INDEX idx_department`**：为主管按部门查人的高频查询加索引

### 8.3.5 修改与删除表

```sql
-- 添加列
ALTER TABLE employee ADD COLUMN phone VARCHAR(20);

-- 修改列类型（慎用！可能丢失数据）
ALTER TABLE employee MODIFY COLUMN name VARCHAR(100);

-- 删除列（慎用！不可恢复）
ALTER TABLE employee DROP COLUMN phone;

-- 删除整个表
DROP TABLE IF EXISTS employee_backup;
```

---

## 8.4 DML — 数据操作语言

DML（Data Manipulation Language）用于对表中的数据行进行增删改操作。

### 8.4.1 INSERT — 插入数据

```sql
-- 单行插入（最常用）
INSERT INTO employee (name, age, department, salary, email) 
VALUES ('张三', 28, '技术部', 15000.00, 'zhangsan@example.com');

-- 多行插入（批量效率更高）
INSERT INTO employee (name, age, department, salary, email) VALUES
('李四', 32, '技术部', 20000.00, 'lisi@example.com'),
('王五', 25, '市场部', 12000.00, 'wangwu@example.com'),
('赵六', 35, '人事部', 18000.00, 'zhaoliu@example.com'),
('钱七', 29, '技术部', 16000.00, 'qianqi@example.com');
```

插入后的employee表状态：

| id | name | age | department | salary | email | hire_date |
|----|------|-----|------------|--------|-------|-----------|
| 1 | 张三 | 28 | 技术部 | 15000.00 | zhangsan@example.com | 2026-05-22 xx:xx:xx |
| 2 | 李四 | 32 | 技术部 | 20000.00 | lisi@example.com | 2026-05-22 xx:xx:xx |
| 3 | 王五 | 25 | 市场部 | 12000.00 | wangwu@example.com | 2026-05-22 xx:xx:xx |
| 4 | 赵六 | 35 | 人事部 | 18000.00 | zhaoliu@example.com | 2026-05-22 xx:xx:xx |
| 5 | 钱七 | 29 | 技术部 | 16000.00 | qianqi@example.com | 2026-05-22 xx:xx:xx |

### 8.4.2 UPDATE — 更新数据

```sql
-- 张三涨薪到18000
UPDATE employee SET salary = 18000.00 WHERE name = '张三';
```

> 🚨 **坑点：UPDATE不带WHERE = 灾难！**
>
> ```sql
> -- 这个操作会把全公司的薪资都改成99999！！
> UPDATE employee SET salary = 99999.00;
> ```
>
> **保护自己的好习惯**：
> 1. 先写 `SELECT * FROM employee WHERE 条件`，确认要修改的行
> 2. 把SELECT改成UPDATE
> 3. 在测试库先执行，确认无误再到生产库执行
> 4. **在生产库执行前，必须确认当前不在生产环境**（很多IDE有颜色区分，测试库绿色，生产库红色）

### 8.4.3 DELETE vs TRUNCATE

```sql
-- 删除特定行（可回滚，可带WHERE）
DELETE FROM employee WHERE id = 5;

-- 清空整张表（不可回滚！）
TRUNCATE TABLE employee_log;
```

DELETE 与 TRUNCATE 的详细对比：

| 对比维度 | DELETE | TRUNCATE |
|----------|--------|----------|
| **能否带WHERE** | 支持 | **不支持**（删全表） |
| **事务回滚** | 可以回滚（逐行记录日志） | **不可回滚**（直接删除表再重建） |
| **删除方式** | 逐行删除（慢） | 删表重建（快） |
| **自增ID** | 保留（不会重置） | **重置为1** |
| **触发器** | 会触发 | 不会触发 |
| **返回值** | 影响行数 | 影响0行（实际整表清空） |

> 🚨 **关键记忆：DELETE可后悔（回滚），TRUNCATE不可后悔！**

---

## 8.5 DQL — 数据查询（本章核心）

DQL（Data Query Language）主要就是 `SELECT` 语句。在真实工作中，**查询占了90%以上的SQL编写量**，本节需要你重点掌握。

### 8.5.1 SELECT执行顺序

一条完整的SELECT语句，MySQL引擎按以下顺序执行（**不是**书写顺序）：

```
FROM → WHERE → GROUP BY → HAVING → SELECT → ORDER BY → LIMIT
```

理解这个顺序非常重要！比如：

```sql
SELECT department, AVG(salary) AS avg_salary  -- ⑤ 最后选列
FROM employee                                  -- ① 先确定表
WHERE age >= 25                                -- ② 过滤原始行
GROUP BY department                            -- ③ 分组
HAVING AVG(salary) > 15000                     -- ④ 过滤分组
ORDER BY avg_salary DESC                       -- ⑥ 排序
LIMIT 3;                                       -- ⑦ 取前3行
```

> 🚨 **关键推论**：
> - SELECT中定义的**别名**（如avg_salary），不能在WHERE中使用（因为WHERE在第②步，SELECT在第⑤步），但可以在ORDER BY中使用（在第⑥步）
> - 这就是为什么上面用 `HAVING AVG(salary) > 15000` 而不是 `HAVING avg_salary > 15000`（虽然MySQL对此比较宽容，但标准SQL要求不能引用别名）

### 8.5.2 基础查询

```sql
-- 查所有列（生产环境慎用！）
SELECT * FROM employee;

-- 查指定列（推荐）
SELECT name, department, salary FROM employee;

-- 查指定列，并从低到高排序
SELECT name, department, salary 
FROM employee 
ORDER BY salary ASC;

-- 别名（AS可省略）
SELECT 
    name AS 姓名, 
    department AS 部门, 
    salary AS 月薪
FROM employee;
```

查询结果：

| name | department | salary |
|------|------------|--------|
| 王五 | 市场部 | 12000.00 |
| 张三 | 技术部 | 18000.00 |
| 钱七 | 技术部 | 16000.00 |
| 赵六 | 人事部 | 18000.00 |
| 李四 | 技术部 | 20000.00 |

### 8.5.3 WHERE条件大全

```sql
-- 1. 比较运算符：=  !=  >  <  >=  <=
SELECT * FROM employee WHERE salary > 15000;

-- 2. 范围查询：BETWEEN ... AND ...（包含边界）
SELECT * FROM employee WHERE age BETWEEN 25 AND 35;

-- 3. 列表查询：IN (...)
SELECT * FROM employee WHERE department IN ('技术部', '市场部');

-- 4. 模糊查询：LIKE
SELECT * FROM employee WHERE name LIKE '张%';  -- 张开头
SELECT * FROM employee WHERE name LIKE '张_';  -- 张开头+1个字符（张三√，张三丰×）

-- 5. 空值判断
SELECT * FROM employee WHERE email IS NULL;      -- 邮箱为空
SELECT * FROM employee WHERE email IS NOT NULL;  -- 邮箱不为空
```

> 🚨 **坑点：NULL不能用=判断！**
>
> ```sql
> -- ❌ 错误：以下SQL永远查不出结果
> SELECT * FROM employee WHERE email = NULL;  -- 结果永远是空！
>
> -- ✅ 正确
> SELECT * FROM employee WHERE email IS NULL;
> ```
>
> 原因：在SQL的三值逻辑（TRUE / FALSE / UNKNOWN）中，**任何值与NULL的比较结果都是UNKNOWN**（不是TRUE也不是FALSE），所以 `email = NULL` 永远不会选出任何行。
>
> ```
> NULL = 'abc'  →  UNKNOWN（不是FALSE！）
> NULL != 'abc' →  UNKNOWN（不是TRUE！）
> NULL = NULL   →  UNKNOWN（两个NULL互不相等！）
> ```
>
> 同理：`NULL + 100` 的结果也是NULL。NULL参与的任何运算结果都是NULL，这个特性会影响聚合函数的计算（见下一小节）。

- **LIKE**中，`%` 匹配任意多个字符（包括0个），`_` 匹配恰好一个字符
- `'张%'` 匹配"张三"、"张三丰"、"张"；`'张_'` 只匹配"张三"但不匹配"张三丰"

### 8.5.4 聚合函数

聚合函数用于对一组值进行计算并返回单个值：

| 函数 | 含义 | 示例 |
|------|------|------|
| **COUNT(*)** | 统计行数（含NULL行） | 总人数 |
| **COUNT(列名)** | 统计该列非NULL的行数 | 有邮箱的人数 |
| **SUM(列)** | 求和 | 总薪资 |
| **AVG(列)** | 平均值 | 平均薪资 |
| **MAX(列)** | 最大值 | 最高薪资 |
| **MIN(列)** | 最小值 | 最低薪资 |

```sql
SELECT 
    COUNT(*)            AS 总人数,
    COUNT(email)        AS 有邮箱人数,
    AVG(salary)         AS 平均薪资,
    SUM(salary)         AS 月工资总额,
    MAX(salary)         AS 最高薪资,
    MIN(salary)         AS 最低薪资
FROM employee;
```

结果：

| 总人数 | 有邮箱人数 | 平均薪资 | 月工资总额 | 最高薪资 | 最低薪资 |
|--------|-----------|----------|-----------|----------|----------|
| 5 | 5 | 17400.00 | 87000.00 | 20000.00 | 12000.00 |

> 🚨 **坑点：COUNT(*) vs COUNT(列名)**
>
> ```sql
> -- 假设employee表有100行，其中email列有5行为NULL
> SELECT COUNT(*) FROM employee;      -- → 100
> SELECT COUNT(email) FROM employee;  -- → 95
> ```
>
> - `COUNT(*)`：统计**所有行**（最常用）
> - `COUNT(列名)`：只统计该列**非NULL**的行数
> - 注意区分：`COUNT(DISTINCT department)` — 去重后统计（公司有多少个不重复的部门）

### 8.5.5 GROUP BY + HAVING

分组查询是日常报表中最常用的SQL模式：

```sql
-- 每个部门的平均薪资
SELECT 
    department,
    COUNT(*) AS 人数,
    AVG(salary) AS 平均薪资
FROM employee
GROUP BY department;
```

结果：

| department | 人数 | 平均薪资 |
|------------|------|----------|
| 技术部 | 3 | 18000.00 |
| 市场部 | 1 | 12000.00 |
| 人事部 | 1 | 18000.00 |

加上过滤条件——只显示平均薪资大于15000的部门：

```sql
SELECT 
    department,
    COUNT(*) AS 人数,
    AVG(salary) AS 平均薪资
FROM employee
GROUP BY department
HAVING AVG(salary) > 15000;
```

结果：

| department | 人数 | 平均薪资 |
|------------|------|----------|
| 技术部 | 3 | 18000.00 |
| 人事部 | 1 | 18000.00 |

> 🚨 **坑点：WHERE vs HAVING — 分清"行过滤"和"组过滤"！**
>
> |  | WHERE | HAVING |
> |--|-------|--------|
> | **过滤对象** | 原始行（分组前） | 分组结果（分组后） |
> | **能否用聚合函数** | ❌ 不能 | ✅ 可以 |
> | **执行时机** | 第②步 | 第④步 |
>
> ```sql
> -- ✅ 正确：WHERE过滤原始行，HAVING过滤分组
> SELECT department, AVG(salary)
> FROM employee
> WHERE age >= 25          -- 先筛掉年龄<25的行
> GROUP BY department
> HAVING AVG(salary) > 15000;  -- 再筛掉平均薪资不达标的分组
>
> -- ❌ 错误：WHERE中用了聚合函数
> SELECT department, AVG(salary)
> FROM employee
> WHERE AVG(salary) > 15000  -- ❌ 报错！WHERE阶段还没分组，哪来的AVG？
> GROUP BY department;
> ```

> 🚨 **坑点：GROUP BY 中SELECT的非聚合列必须出现在GROUP BY中**
>
> ```sql
> -- ❌ 报错：name既不在GROUP BY中，也不是聚合函数
> SELECT name, department, AVG(salary)
> FROM employee
> GROUP BY department;
>
> -- ✅ 正确
> SELECT department, AVG(salary)
> FROM employee
> GROUP BY department;
> ```
>
> MySQL 8.0默认sql_mode包含`ONLY_FULL_GROUP_BY`，会严格检查此规则。不要试图关闭它——这条规则帮你避免写出逻辑错误的SQL。

### 8.5.6 ORDER BY多列排序

```sql
-- 按部门升序，同部门按薪资降序
SELECT name, department, salary
FROM employee
ORDER BY department ASC, salary DESC;
```

结果：

| name | department | salary |
|------|------------|--------|
| 李四 | 技术部 | 20000.00 |
| 钱七 | 技术部 | 16000.00 |
| 张三 | 技术部 | 18000.00 |
| 赵六 | 人事部 | 18000.00 |
| 王五 | 市场部 | 12000.00 |

（注意：张三salary=18000、李四=20000，降序后李四在张三前面）

### 8.5.7 LIMIT分页

```sql
-- 第1页：每页2条
SELECT * FROM employee LIMIT 0, 2;   -- offset=0, count=2 → 第1-2条
-- 第2页
SELECT * FROM employee LIMIT 2, 2;   -- offset=2, count=2 → 第3-4条
-- 第3页
SELECT * FROM employee LIMIT 4, 2;   -- offset=4, count=2 → 第5条
```

写法：`LIMIT offset, count`，其中 `offset = (页码 - 1) * 每页条数`。

> 🚨 **坑点：大偏移量分页 = 性能灾难！**
>
> ```sql
> -- 查询第100001页，每页20条
> SELECT * FROM employee ORDER BY id LIMIT 2000000, 20;
> ```
>
> 这条SQL的实际执行过程是：MySQL逐行扫描前2000020行，丢掉前2000000行，只返回最后20行！**扫描了200万行只为了拿20行**。
>
> **优化方案（延迟关联/子查询优化）**：
> ```sql
> -- 先在索引上快速定位ID，再回表取数据
> SELECT * FROM employee 
> WHERE id >= (
>     SELECT id FROM employee ORDER BY id LIMIT 2000000, 1
> )
> ORDER BY id LIMIT 20;
> ```
>
> 原理：先用覆盖索引（只在索引B+Tree上遍历）快速找到第2000001行的id值，然后直接从这个id开始取20行。时间复杂度从 O(200万) 降到 O(1)。

---

## 8.6 多表查询

真实应用中，数据分散在多张表中，需要通过JOIN将它们关联起来。

### 8.6.1 准备关联数据

我们先创建一个部门表，并修改employee表：

```sql
-- 创建部门表
CREATE TABLE department (
    id      BIGINT PRIMARY KEY AUTO_INCREMENT,
    name    VARCHAR(50) NOT NULL UNIQUE COMMENT '部门名称',
    address VARCHAR(200) COMMENT '办公地址'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 插入部门数据
INSERT INTO department (name, address) VALUES
('技术部', '3号楼'),
('市场部', '5号楼'),
('人事部', '2号楼'),
('财务部', '1号楼');

-- 添加外键列
ALTER TABLE employee ADD COLUMN dept_id BIGINT;
ALTER TABLE employee ADD CONSTRAINT fk_dept 
    FOREIGN KEY (dept_id) REFERENCES department(id);

-- 更新员工部门关联
UPDATE employee SET dept_id = 1 WHERE department = '技术部';
UPDATE employee SET dept_id = 2 WHERE department = '市场部';
UPDATE employee SET dept_id = 3 WHERE department = '人事部';
```

当前数据状态：

**department表**：

| id | name | address |
|----|------|---------|
| 1 | 技术部 | 3号楼 |
| 2 | 市场部 | 5号楼 |
| 3 | 人事部 | 2号楼 |
| 4 | 财务部 | 1号楼 |

**employee表**：

| id | name | dept_id | salary |
|----|------|---------|--------|
| 1 | 张三 | 1 | 18000 |
| 2 | 李四 | 1 | 20000 |
| 3 | 王五 | 2 | 12000 |
| 4 | 赵六 | 3 | 18000 |
| 5 | 钱七 | 1 | 16000 |

### 8.6.2 INNER JOIN — 内连接

内连接返回**两张表中都匹配的行**（取交集），可以用Venn图理解：

```
  ┌──────────┐     ┌──────────┐
  │ employee │     │department│
  │  dept_id │     │    id    │
  │ 1,1,1,2,3│     │ 1,2,3,4  │
  └──────────┘     └──────────┘
       │                │
       └───────┬────────┘
               │
        ┌──────┴──────┐
        │   交集部分   │  ← INNER JOIN返回的部分
        │  dept 1,2,3 │    (dept_id=4的财务部没有员工，不出现在结果中)
        └─────────────┘
```

```sql
SELECT 
    e.name AS 姓名,
    d.name AS 部门,
    d.address AS 办公地址
FROM employee e
INNER JOIN department d ON e.dept_id = d.id;
```

结果：

| 姓名 | 部门 | 办公地址 |
|------|------|----------|
| 张三 | 技术部 | 3号楼 |
| 李四 | 技术部 | 3号楼 |
| 钱七 | 技术部 | 3号楼 |
| 王五 | 市场部 | 5号楼 |
| 赵六 | 人事部 | 2号楼 |

注意：财务部（id=4）没有员工，所以不出现在结果中——INNER JOIN只取交集。

### 8.6.3 LEFT JOIN — 左连接

左连接返回**左表所有行 + 右表匹配行**（不匹配处填NULL）：

```
  ┌──────────┐         ┌──────────┐
  │ 左表全部  │  ──→   │ 右表匹配  │
  │ employee │         │department│
  │(全部5行) │         │(匹配填)  │
  └──────────┘         └──────────┘
```

```sql
-- 以employee为主：所有员工都要，不管有没有对应部门
SELECT 
    e.name AS 姓名,
    d.name AS 部门,
    d.address AS 办公地址
FROM employee e
LEFT JOIN department d ON e.dept_id = d.id;
```

结果同上表（因为每个员工的dept_id都在department中存在）。

反过来，以department为主——**所有部门都显示，没有员工的部门显示NULL**：

```sql
SELECT 
    d.name AS 部门,
    e.name AS 员工
FROM department d
LEFT JOIN employee e ON d.id = e.dept_id
ORDER BY d.id, e.id;
```

结果：

| 部门 | 员工 |
|------|------|
| 技术部 | 张三 |
| 技术部 | 李四 |
| 技术部 | 钱七 |
| 市场部 | 王五 |
| 人事部 | 赵六 |
| 财务部 | NULL |

> 🚨 **坑点：LEFT JOIN后WHERE条件的位置至关重要！**
>
> ```sql
> -- 场景：找出"没有员工的部门"（部门有，但无人归属）
>
> -- ❌ 错误写法（WHERE放在后面过滤了整个结果集）：
> SELECT d.name
> FROM department d
> LEFT JOIN employee e ON d.id = e.dept_id
> WHERE e.name IS NULL;
> -- 结果：财务部 ✅ 正好是我们想要的
>
> -- 👆 上面这个是正确场景，但换一个条件就出问题了：
>
> -- ❌ 问题写法：想保留所有部门，只展示技术部的员工
> SELECT d.name, e.name
> FROM department d
> LEFT JOIN employee e ON d.id = e.dept_id
> WHERE d.name = '技术部';
> -- 结果：只有技术部的3条（因为WHERE过滤了整个左连接结果）
>
> -- ✅ 正确写法：条件放ON里
> -- 但注意：ON中过滤右表不改变"左表全保留"的行为！
> -- 如果需求是"只要技术部"，应该把条件放在ON而不是WHERE
> ```
>
> **核心规则**：
> - `ON` 后面的条件：决定**连接时**哪些行匹配，不匹配的右表列填NULL
> - `WHERE` 后面的条件：在**连接完成后**对整个结果集过滤
> - 如果WHERE过滤了左表的NULL行（比如 `WHERE e.name IS NOT NULL`），左连接实际上退化为内连接！

### 8.6.4 子查询

子查询是嵌套在另一个SQL中的SELECT语句：

```sql
-- 查询薪资高于平均水平的员工（子查询在WHERE中）
SELECT name, salary 
FROM employee 
WHERE salary > (SELECT AVG(salary) FROM employee);
```

| name | salary |
|------|--------|
| 张三 | 18000.00 |
| 李四 | 20000.00 |
| 赵六 | 18000.00 |

```sql
-- 子查询作为虚拟表（在FROM中）
SELECT dept_avg.department, dept_avg.avg_salary
FROM (
    SELECT department, AVG(salary) AS avg_salary
    FROM employee
    GROUP BY department
) AS dept_avg
WHERE dept_avg.avg_salary > 15000;
```

### 8.6.5 UNION合并

```sql
-- UNION：去重合并
SELECT name FROM employee WHERE department = '技术部'
UNION
SELECT name FROM employee WHERE salary > 17000;

-- UNION ALL：不去重合并（性能更好，如果你确定无重复）
SELECT name FROM employee WHERE department = '技术部'
UNION ALL
SELECT name FROM employee WHERE salary > 17000;
```

| 对比 | UNION | UNION ALL |
|------|-------|-----------|
| 去重 | ✅ 去重 | ❌ 不去重 |
| 性能 | 较慢（需排序去重） | 较快 |
| 适用 | 需要去重时 | 确定无重复或允许重复时 |

---

## 8.7 索引基础

### 8.7.1 什么是索引？

把数据表想象成一本600页的书：
- **没有索引**：要找"Spring Boot自动配置原理"这个词，你需要从第1页翻到第600页，一页页找
- **有索引**：翻到书末尾的索引页，按拼音找到 S → Spring Boot → 自动配置原理 → 第412页，直接翻过去

数据库索引的作用完全一样——**加速查询，但有维护成本（增删改时需要同时更新索引）**。

### 8.7.2 B+Tree索引原理简述

MySQL InnoDB的索引底层使用 **B+Tree**（一种自平衡的多路搜索树）数据结构：

```
                     [50 | 100]              ← 非叶子节点（只存索引键+指针）
                    /    |     \
               [10|30] [60|80] [110|150]     ← 非叶子节点
              /  |  \    ...      ...
             ↗   ↗   ↗
          [1][10][20] ...                    ← 叶子节点（存完整数据行）
          ←──── 双向链表 ────→
```

B+Tree的关键特性：
- **所有数据都存在叶子节点**（最底层），非叶子节点只存"路标"
- **叶子节点之间用双向链表连接**，所以范围查询（`BETWEEN`、`>`、`<`）非常高效
- 一个节点通常存储在一个磁盘页（16KB），因此树的高度通常只有2-4层，查找任何一行只需2-4次磁盘IO

### 8.7.3 创建索引

```sql
-- 普通索引（最常用）
CREATE INDEX idx_employee_name ON employee(name);

-- 唯一索引（加速+约束唯一）
CREATE UNIQUE INDEX idx_employee_email ON employee(email);

-- 联合索引（多列组合）
CREATE INDEX idx_employee_dept_salary ON employee(department, salary);

-- 在CREATE TABLE中直接定义（见8.3.4节的employee表DDL）
```

### 8.7.4 最左前缀原则

联合索引 `(department, salary)` 相当于创建了：
- ✅ `WHERE department = '技术部'` （用到索引）
- ✅ `WHERE department = '技术部' AND salary > 15000` （用到索引）
- ❌ `WHERE salary > 15000` （**用不到索引**！因为联合索引从department开始排序）

这就像一本先按"省"再按"市"排序的电话簿：
- 你可以快速找到"浙江省杭州市"（先定省，再定市）
- 但你无法快速找到"所有姓张的人"（因为电话簿不按姓氏排序）

> 🚨 **联合索引的核心规则：查询条件必须从最左列开始，且中间不能断**。

### 8.7.5 索引失效的经典场景

> 🚨 **场景1：前置模糊查询**
>
> ```sql
> -- ❌ 索引失效（LIKE '%%' 前置模糊无法使用B+Tree的有序性）
> EXPLAIN SELECT * FROM employee WHERE name LIKE '%三';
>
> -- ✅ 索引生效（后置模糊可以）
> EXPLAIN SELECT * FROM employee WHERE name LIKE '张%';
> ```
>
> 原因：B+Tree按列的**前缀**排序，`LIKE '张%'` 可以定位到"张"开头的节点，`LIKE '%三'` 无法利用有序性。

> 🚨 **场景2：索引列上做运算**
>
> ```sql
> -- ❌ 索引失效
> SELECT * FROM employee WHERE salary + 1000 = 20000;
>
> -- ✅ 索引生效（把运算移到等号右边）
> SELECT * FROM employee WHERE salary = 19000;
> ```

> 🚨 **场景3：隐式类型转换**
>
> ```sql
> -- name是VARCHAR类型，但查询条件给的是数字
> -- ❌ 索引失效：MySQL会将name列的值隐式转换为数字再比较
> SELECT * FROM employee WHERE name = 123;
>
> -- ✅ 索引生效：给字符串值
> SELECT * FROM employee WHERE name = '123';
> ```

> 🚨 **场景4：OR条件中有非索引列**
>
> ```sql
> -- name有索引，但age没有
> -- ❌ 整个查询可能不走索引
> SELECT * FROM employee WHERE name = '张三' OR age = 28;
>
> -- ✅ 改用UNION（分而治之）
> SELECT * FROM employee WHERE name = '张三'
> UNION
> SELECT * FROM employee WHERE age = 28;
> ```

### 8.7.6 EXPLAIN — 查看查询计划

`EXPLAIN` 是SQL优化的第一工具。在SQL前面加上 `EXPLAIN`，MySQL会告诉你它打算怎样执行：

```sql
EXPLAIN SELECT * FROM employee WHERE name = '张三';
```

关键字段速查：

| 字段 | 值 | 含义 |
|------|-----|------|
| **type** | `ALL` | 全表扫描（最差！） |
| | `index` | 全索引扫描 |
| | `range` | 索引范围扫描（不错） |
| | `ref` | 非唯一索引查找（好） |
| | `const` | 主键/唯一索引常量查找（最好！） |
| **possible_keys** | 列名列表 | MySQL**认为可能**用到哪些索引 |
| **key** | 列名 | MySQL**实际**用到哪个索引 |
| **rows** | 数字 | MySQL**预估**需要扫描多少行 |
| **Extra** | `Using index` | 覆盖索引（最好的情况，只读索引不读表） |
| | `Using filesort` | 需要额外排序（不好！考虑加索引） |
| | `Using temporary` | 需要临时表（不好！考虑优化SQL） |

> 一个简单的优化目标：让 `type` 从 `ALL` 变成 `ref` 或 `range`，`rows` 从几万变成几十。

---

## 8.8 事务入门

### 8.8.1 什么是事务？

**事务（Transaction）是把一组SQL操作打包成一个"不可分割"的逻辑单元。**

最经典的例子：银行转账。

```
A账户减1000元  ─┐
                ├── 这两个操作要么都成功，要么都失败！
B账户加1000元  ─┘
```

如果A减钱后系统崩溃了，B还没加钱——1000元凭空消失了！事务就是为了防止这种情况。

### 8.8.2 ACID四大特性

| 特性 | 全称 | 通俗解释 |
|------|------|----------|
| **A - 原子性** | Atomicity | 一组操作要么全成功，要么全失败（不可分割） |
| **C - 一致性** | Consistency | 事务前后数据都是合法的（如总金额不变） |
| **I - 隔离性** | Isolation | 多个事务并发执行时互不干扰 |
| **D - 持久性** | Durability | 事务提交后，数据永久保存（即使断电） |

### 8.8.3 手动事务操作

```sql
-- 开始事务（也可用 BEGIN;）
START TRANSACTION;

-- 张三转5000元给李四
UPDATE employee SET salary = salary - 5000 WHERE name = '张三';
UPDATE employee SET salary = salary + 5000 WHERE name = '李四';

-- 检查结果：张三13000，李四25000
SELECT name, salary FROM employee WHERE name IN ('张三', '李四');

-- 确认无误，提交
COMMIT;

-- 如果发现问题，回滚
-- ROLLBACK;  ← 取消所有操作，数据回到事务开始前的状态
```

### 8.8.4 并发问题

当多个事务同时操作同一数据时，会出现以下问题：

| 问题 | 描述 | 类比 |
|------|------|------|
| **脏读** | T1读到T2**未提交**的修改，T2回滚后T1读到的是"脏数据" | 看到别人编辑到一半的文档，但别人后来撤销了 |
| **不可重复读** | T1两次读取同一行，中间T2修改了该行并提交，T1**两次结果不同** | 同一份文档，第一次看是v1，第二次看变成了v2 |
| **幻读** | T1两次查询同一范围，中间T2**插入**了新行并提交，T1第二次多出几行 | 查班级名单，第一次10人，刷新后多了1人（有人转班进来） |

### 8.8.5 隔离级别

数据库提供了四种隔离级别来应对并发问题：

| 隔离级别 | 脏读 | 不可重复读 | 幻读 | 性能 |
|----------|------|-----------|------|------|
| **READ UNCOMMITTED** | ❌ | ❌ | ❌ | 最快 |
| **READ COMMITTED** | ✅ | ❌ | ❌ | 较快 |
| **REPEATABLE READ**（MySQL默认） | ✅ | ✅ | ✅（部分） | 中等 |
| **SERIALIZABLE** | ✅ | ✅ | ✅ | 最慢 |

> 🚨 **坑点：不同数据库默认隔离级别不同！**
> - **MySQL（InnoDB）**：默认 `REPEATABLE READ`
> - **Oracle / PostgreSQL**：默认 `READ COMMITTED`
> - 这导致同一套SQL在MySQL和Oracle下行为可能不同！迁移数据库时必须注意隔离级别的差异

> 🚨 **坑点：MySQL InnoDB在REPEATABLE READ下通过间隙锁（Gap Lock）部分解决了幻读**
> - 间隙锁会锁住索引记录之间的"间隙"，防止其他事务插入新数据
> - 但这并不意味着完全解决了幻读（某些边缘场景仍可能出现）
> - 在Oracle的`READ COMMITTED`下没有任何间隙锁保护，幻读更容易出现

查看和设置隔离级别：

```sql
-- 查看当前隔离级别
SELECT @@transaction_isolation;  -- MySQL 8.0+
-- SELECT @@tx_isolation;         -- MySQL 5.x（已废弃）

-- 设置会话隔离级别
SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED;
```

---

## 8.9 本章小结

恭喜你学完了本章！现在回顾一下你掌握的技能：

1. **MySQL安装与配置**：在Windows/Mac/Linux上完成MySQL 8.0安装，理解caching_sha2_password认证方式
2. **数据库设计**：遵循需求→ER图→范式化→建表的完整设计流程，理解1NF/2NF/3NF的每层要求
3. **DDL**：创建数据库（永远用utf8mb4）、选择正确的数据类型（金额用DECIMAL）、添加约束（PK/FK/UNIQUE/NOT NULL/DEFAULT/CHECK）
4. **DML**：INSERT批量插入、UPDATE（必须带WHERE！）、DELETE vs TRUNCATE对比
5. **DQL**：掌握SELECT执行顺序（FROM→WHERE→GROUP BY→HAVING→SELECT→ORDER BY→LIMIT）、聚合函数、GROUP BY+HAVING分组、LIMIT分页（大偏移量性能优化）
6. **多表查询**：INNER JOIN取交集、LEFT JOIN左全右匹配、子查询、UNION
7. **索引**：B+Tree结构、联合索引最左前缀原则、五类索引失效场景、EXPLAIN分析
8. **事务**：ACID特性、脏读/不可重复读/幻读、四种隔离级别、MySQL vs Oracle默认隔离级别差异

---

## 思考题

1. 为什么在MySQL中 `NULL = NULL` 的结果是NULL（即UNKNOWN）？这会导致哪些实际问题？（提示：结合JOIN和聚合函数思考）

2. 设计一个"学生选课系统"的数据库。需求：学生（学号、姓名、年级）、课程（课程号、课程名、学分）。一个学生可以选多门课，一门课可以被多个学生选。请写出完整的建表SQL（3张表，含约束）。

3. 以下SQL语句中，索引 `idx_employee_name` 和 `idx_employee_salary` 分别在什么情况下失效？为什么？

   ```sql
   -- ①
   SELECT * FROM employee WHERE UPPER(name) = 'ZHANGSAN';
   -- ②
   SELECT * FROM employee WHERE salary + 1000 > 20000;
   -- ③
   SELECT * FROM employee WHERE name LIKE '%张%';
   -- ④
   SELECT * FROM employee WHERE name = 123;
   -- ⑤
   SELECT * FROM employee WHERE name = '张三' OR salary > 20000;
   ```

4. 为什么MySQL 8.0默认的认证方式变成了caching_sha2_password？这带来了什么好处和兼容性问题？

5. 假设你设计了5张表，分别有员工基本信息、薪资记录、考勤记录、项目分配、培训记录。现在要做一个"本月员工综合报表"，需要JOIN这5张表。你会选择范式化的设计（表多但冗余少）还是反范式化的设计（表少但冗余多）？为什么？

---

<details>
<summary>思考题参考答案（点击展开）</summary>

**第1题**：
NULL表示"未知值"，两个未知值之间无法比较是否相等，因此三值逻辑下=NULL返回UNKNOWN。实际问题：
- `WHERE col = NULL` 永远得不到结果（因为UNKNOWN不被当作TRUE）
- LEFT JOIN中，如果没有匹配行，右表所有列为NULL。如果WHERE条件写`WHERE right.col = 'xxx'`，就会排除掉所有无匹配的左表行（等于把LEFT JOIN变成了INNER JOIN）
- COUNT(NULL)返回0，因此`COUNT(列)`和`COUNT(*)`结果可能不同

**第2题**：
```sql
CREATE TABLE student (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    sno VARCHAR(20) NOT NULL UNIQUE,
    name VARCHAR(50) NOT NULL,
    grade VARCHAR(10)
);

CREATE TABLE course (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    cno VARCHAR(20) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    credit DECIMAL(3,1) NOT NULL
);

CREATE TABLE student_course (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    student_id BIGINT NOT NULL,
    course_id BIGINT NOT NULL,
    score DECIMAL(4,1),
    FOREIGN KEY (student_id) REFERENCES student(id),
    FOREIGN KEY (course_id) REFERENCES course(id),
    UNIQUE KEY uk_student_course (student_id, course_id)  -- 同一学生不能重复选同一门课
);
```

**第3题**：
- ①：索引列上用了函数UPPER()，失效。改为存的时候就统一存大写。
- ②：索引列上做了运算salary+1000，失效。改为WHERE salary > 19000。
- ③：LIKE '%张%'前后都是模糊，失效。因为B+Tree按前缀排序，前置%无法定位。
- ④：隐式类型转换（VARCHAR vs INT），失效。改为WHERE name='123'。
- ⑤：OR两边必须都有索引才走索引查询；salary列如果没建索引，整个OR查询会退化为全表扫描。改用UNION。

**第4题**：
caching_sha2_password相比mysql_native_password的优势：
- SHA-256比SHA-1更安全（抗碰撞性更强）
- 支持缓存（首次认证后缓存结果，减少服务器RSA/SSL开销）
- 符合现代密码学标准

兼容性问题：旧客户端（Navicat 11-、旧JDBC驱动、旧PHP mysqli扩展）不支持此插件，需要升级客户端或降级认证方式。

**第5题**：
取决于系统类型：
- **OLTP（实时事务系统，如员工打卡）**：倾向于范式化，减少冗余意味着每次修改只需改一处，数据一致性高。JOIN多但单次查询数据量小。
- **OLAP（报表分析系统，如月报）**：倾向于反范式化（星型模型/宽表），冗余换查询速度。一次月报要JOIN 5张表不如直接建一张"月报汇总表"。
- 实际工程中可以采用 **CQRS（读写分离模型）**：写操作用范式化的表保证一致性，读操作用定期同步的宽表/缓存保证速度。

</details>

---

> **下一章预告**：第9章将教你用Java代码连接MySQL数据库——JDBC编程。你将学会JDBC六步曲、PreparedStatement防SQL注入、Druid连接池配置，并在章末完成 **EMS v2**（JDBC版员工管理系统），用一个完整的命令行CRUD项目将前8章的Java+SQL知识融会贯通。
</parameter>