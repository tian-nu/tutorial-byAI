# 第9章：JDBC数据库编程

## 本章目标

学完本章你将能够：

- 理解JDBC在Java生态系统中的位置与架构
- 熟练编写JDBC六步曲完成数据库CRUD操作
- 亲手演示SQL注入攻击，深刻理解其危害
- 掌握PreparedStatement防御SQL注入的原理
- 配置Druid连接池优化数据库连接管理
- 运用DAO模式实现分层架构
- **完成EMS v2：JDBC版员工管理系统**，将前9章的Java+SQL知识融为一个完整项目

---

## 9.1 JDBC概述

### 9.1.1 什么是JDBC？

到目前为止，你已经掌握了Java编程（第1-7章）和SQL操作（第8章）。但它们是两个**独立的世界**：

- Java程序跑在JVM里，操作对象、集合、流
- MySQL跑在数据库服务器上，等待SQL指令

**JDBC（Java Database Connectivity）就是连接这两个世界的桥梁。**

它是Java定义的一套标准接口（`java.sql`包），让Java程序可以用统一的方式访问任何关系型数据库。换个通俗的说法：JDBC是Java世界的"万能数据库遥控器"。

### 9.1.2 JDBC架构

```
┌────────────────────────────┐
│        Java 应用程序        │  ← 你写的业务代码
├────────────────────────────┤
│        JDBC API            │  ← java.sql / javax.sql（接口层）
│  Connection / Statement    │
│  PreparedStatement         │
│  ResultSet                 │
├────────────────────────────┤
│     DriverManager          │  ← 驱动管理器（找合适的驱动）
├────────────────────────────┤
│  MySQL Driver  │Oracle Drv │  ← 各厂商提供的驱动实现（.jar）
│  (mysql-       │(ojdbc)    │
│  connector-j)  │           │
├────────────────────────────┤
│   MySQL    │   Oracle ...  │  ← 数据库服务器
└────────────────────────────┘
```

JDBC的核心设计思想是**面向接口编程**：Java只定义接口（Connection、Statement、ResultSet等），具体实现由各数据库厂商提供（称为**JDBC驱动**）。你写代码时面向接口编程，换数据库只需换驱动jar包，代码几乎不用改。

### 9.1.3 为什么还要学JDBC？

你可能听说过MyBatis、Hibernate、Spring Data JPA这些框架——它们让你用一两行代码就完成数据库操作。那为什么还要学"原始"的JDBC？

答案是：**所有的ORM框架底层都是JDBC。** 当你的MyBatis突然报出 `CommunicationsException: Communications link failure`，或者JPA的懒加载导致N+1查询问题时，如果你不懂JDBC，你只能盲目地搜索报错信息。但如果你懂JDBC，你会立刻知道：这是数据库连接断了，这是ResultSet没关闭导致连接泄露。

> **类比**：Spring Boot的自动配置就像自动挡汽车，JDBC就像手动挡。学会手动挡，你才能真正理解汽车的传动原理，开自动挡时遇到问题也能更快定位。

### 9.1.4 Class.forName()还需要吗？

很多老教程会教你第一步写：

```java
Class.forName("com.mysql.cj.jdbc.Driver");
```

> 🚨 **坑点：JDBC 4.0（JDK 6起）不再需要手动加载驱动！**
> - 从JDBC 4.0开始，Java引入了**SPI（Service Provider Interface）机制**
> - 驱动jar包（如mysql-connector-j-8.x.x.jar）的`META-INF/services/java.sql.Driver`文件中已声明了驱动类
> - `DriverManager.getConnection()` 会自动扫描classpath找到合适的驱动
> - **但面试中常被问到这行代码**，你知道它现在可省略、知道它做了什么就够了

### 9.1.5 添加Maven依赖

在pom.xml中添加MySQL驱动：

```xml
<dependency>
    <groupId>com.mysql</groupId>
    <artifactId>mysql-connector-j</artifactId>
    <version>8.2.0</version>
</dependency>
```

> 注意：MySQL 8.0.31起，Maven坐标从 `mysql:mysql-connector-java` 改为了 `com.mysql:mysql-connector-j`。如果你看到老教程用旧坐标，不用担心——新坐标是官方推荐的。

---

## 9.2 JDBC编程六步曲

这是本章最核心的内容。JDBC操作数据库遵循一套固定的流程，每一步都有其目的和潜在陷阱。我们用一个完整的查询示例逐步展开。

### 准备工作：数据库与测试数据

确保第8章创建的 `ems` 数据库和 `employee` 表可用，并插入测试数据：

```sql
USE ems;

INSERT INTO employee (name, age, department, salary, email) VALUES
('张三', 28, '技术部', 18000.00, 'zhangsan@example.com'),
('李四', 32, '技术部', 20000.00, 'lisi@example.com'),
('王五', 25, '市场部', 12000.00, 'wangwu@example.com'),
('赵六', 35, '人事部', 18000.00, 'zhaoliu@example.com'),
('钱七', 29, '技术部', 16000.00, 'qianqi@example.com');
```

### 完整六步曲代码（先看全局，再逐步拆解）

```java
import java.sql.*;

public class JdbcSixSteps {
    public static void main(String[] args) {
        // 第1步：注册驱动（JDBC 4.0+可省略，但写了也无妨）
        // Class.forName("com.mysql.cj.jdbc.Driver");

        String url = "jdbc:mysql://localhost:3306/ems"
                   + "?useSSL=false"
                   + "&serverTimezone=Asia/Shanghai"
                   + "&characterEncoding=utf8mb4";
        String username = "root";
        String password = "你的密码";

        Connection conn = null;
        PreparedStatement pstmt = null;
        ResultSet rs = null;

        try {
            // 第2步：获取数据库连接
            conn = DriverManager.getConnection(url, username, password);
            System.out.println("数据库连接成功！");

            // 第3步：创建PreparedStatement（预编译SQL）
            String sql = "SELECT id, name, department, salary FROM employee WHERE department = ?";
            pstmt = conn.prepareStatement(sql);
            
            // 设置占位符参数
            pstmt.setString(1, "技术部");

            // 第4步：执行SQL查询
            rs = pstmt.executeQuery();

            // 第5步：处理结果集
            System.out.println("===== 技术部员工列表 =====");
            while (rs.next()) {
                long id = rs.getLong("id");            // 列索引从1开始！
                String name = rs.getString("name");
                String dept = rs.getString("department");
                double salary = rs.getDouble("salary");
                
                System.out.printf("ID: %d | 姓名: %s | 部门: %s | 薪资: %.2f%n",
                        id, name, dept, salary);
            }

        } catch (SQLException e) {
            System.err.println("数据库操作异常：" + e.getMessage());
            e.printStackTrace();
        } finally {
            // 第6步：释放资源（倒序关闭！）
            try { if (rs != null) rs.close(); } catch (SQLException e) { e.printStackTrace(); }
            try { if (pstmt != null) pstmt.close(); } catch (SQLException e) { e.printStackTrace(); }
            try { if (conn != null) conn.close(); } catch (SQLException e) { e.printStackTrace(); }
        }
    }
}
```

运行结果：

```
数据库连接成功！
===== 技术部员工列表 =====
ID: 1 | 姓名: 张三 | 部门: 技术部 | 薪资: 18000.00
ID: 2 | 姓名: 李四 | 部门: 技术部 | 薪资: 20000.00
ID: 5 | 姓名: 钱七 | 部门: 技术部 | 薪资: 16000.00
```

现在，让我们逐步深入理解每一步的细节。

---

### 9.2.1 第1步：注册驱动（了解即可）

```java
// 传统写法（JDBC 3.0时代需要，现在可省略）
Class.forName("com.mysql.cj.jdbc.Driver");
```

这行代码触发Driver类的静态代码块执行，将MySQL驱动注册到DriverManager中。现在驱动jar包通过SPI自动注册，这一行不需要了。

### 9.2.2 第2步：获取连接 — Connection

```java
String url = "jdbc:mysql://localhost:3306/ems"
           + "?useSSL=false"
           + "&serverTimezone=Asia/Shanghai"
           + "&characterEncoding=utf8mb4";
String username = "root";
String password = "你的密码";

Connection conn = DriverManager.getConnection(url, username, password);
```

**JDBC URL格式详解**：

```
jdbc:mysql://[主机]:[端口]/[数据库名]?参数1=值1&参数2=值2
   │    │        │       │       │
   │    │        │       │       └── 指定数据库名
   │    │        │       └── 端口，MySQL默认3306
   │    │        └── 主机，localhost表示本机
   │    └── 子协议，表示MySQL数据库
   └── 主协议，固定为jdbc
```

**常用连接参数速查**：

| 参数 | 推荐值 | 说明 |
|------|--------|------|
| `useSSL` | `false`（开发）/ `true`（生产） | MySQL 8默认开启SSL，本地开发建议关闭 |
| `serverTimezone` | `Asia/Shanghai` | **必须设置！** 否则时区不正确 |
| `characterEncoding` | `utf8mb4` | 字符编码，支持emoji |
| `useUnicode` | `true` | 使用Unicode字符集 |
| `allowPublicKeyRetrieval` | `true` | 允许客户端获取公钥（某些认证方式需要） |

> 🚨 **坑点：serverTimezone参数在MySQL 8驱动中非常重要**
> - 如果不设置，驱动会尝试自动检测时区，可能使用UTC（差8小时）
> - 现象：Java代码插入的DATETIME，在数据库中少了8小时（或多了8小时）
> - **解决**：明确指定 `serverTimezone=Asia/Shanghai`
> - MySQL 8.0.23+ 驱动支持简写为 `connectionTimeZone=SERVER`（让连接使用服务器时区）

> 🚨 **坑点：useSSL参数**
> - MySQL 8.0默认开启SSL/TLS，但本地开发的MySQL通常没有配置SSL证书
> - 不加 `useSSL=false` 可能报错：`javax.net.ssl.SSLHandshakeException`
> - **开发环境**加 `useSSL=false`，**生产环境**配好证书后用SSL

Connection对象代表一个与数据库的活连接，它有以下关键职责：
- 持有TCP socket连接到数据库服务器
- 管理事务（commit/rollback）
- 创建Statement/PreparedStatement对象

### 9.2.3 第3步：创建Statement / PreparedStatement

JDBC提供了三种Statement：

```java
// 1. Statement — 静态SQL，不推荐（SQL注入风险！）
Statement stmt = conn.createStatement();
stmt.executeQuery("SELECT * FROM employee WHERE name = '张三'");

// 2. PreparedStatement — 预编译SQL，推荐！
PreparedStatement pstmt = conn.prepareStatement("SELECT * FROM employee WHERE name = ?");
pstmt.setString(1, "张三");

// 3. CallableStatement — 调用存储过程
CallableStatement cstmt = conn.prepareCall("{call my_procedure(?)}");
```

| 特性 | Statement | PreparedStatement |
|------|-----------|-------------------|
| **SQL预编译** | 不预编译（每次发完整SQL） | ✅ 预编译（只编译一次） |
| **防SQL注入** | ❌ 不防 | ✅ 天然免疫（见9.3节） |
| **性能** | 每次硬解析SQL | 首次编译后缓存，后续快 |
| **代码可读性** | 拼接字符串，混乱 | 占位符`?`，清晰 |
| **适用场景** | 仅DDL语句（如建表） | **所有带参数的DML/DQL** |

**本书铁律：永远用PreparedStatement处理带参数的SQL。**

### 9.2.4 第4步：执行SQL

```java
// executeQuery() → 执行SELECT → 返回ResultSet（结果集）
ResultSet rs = pstmt.executeQuery();

// executeUpdate() → 执行INSERT/UPDATE/DELETE → 返回int（影响行数）
String insertSql = "INSERT INTO employee (name, age, department, salary, email) VALUES (?, ?, ?, ?, ?)";
PreparedStatement insertPstmt = conn.prepareStatement(insertSql);
insertPstmt.setString(1, "孙八");
insertPstmt.setInt(2, 27);
insertPstmt.setString(3, "市场部");
insertPstmt.setDouble(4, 14000.00);
insertPstmt.setString(5, "sunba@example.com");
int affectedRows = insertPstmt.executeUpdate();
System.out.println("插入了 " + affectedRows + " 行");

// execute() → 返回boolean（是否有ResultSet返回），用于不确定类型的SQL
```

PreparedStatement的参数设置方法（按数据库列类型对应）：

| setXxx方法 | 对应的SQL类型 | 示例 |
|-----------|-------------|------|
| `setInt(index, value)` | INT | `setInt(1, 28)` |
| `setLong(index, value)` | BIGINT | `setLong(1, 10001L)` |
| `setString(index, value)` | VARCHAR/CHAR/TEXT | `setString(1, "张三")` |
| `setDouble(index, value)` | DOUBLE/FLOAT | `setDouble(1, 18000.0)` |
| `setBigDecimal(index, value)` | DECIMAL | `setBigDecimal(1, new BigDecimal("18000.00"))` |
| `setDate(index, value)` | DATE | `setDate(1, Date.valueOf("2026-05-22"))` |
| `setTimestamp(index, value)` | DATETIME/TIMESTAMP | `setTimestamp(1, Timestamp.valueOf(LocalDateTime.now()))` |
| `setNull(index, Types.VARCHAR)` | NULL值 | `setNull(1, java.sql.Types.VARCHAR)` |

> 🚨 **占位符索引从1开始，不是0！** 这是Java程序员最容易犯的错误之一——因为Java数组索引从0开始，但JDBC的`?`占位符索引从1开始。

### 9.2.5 第5步：处理ResultSet

ResultSet是一个**指向结果集当前行**的游标（cursor）：

```
ResultSet对象（内存中的一张虚拟表）

游标初始位置──→  (before first)   ← 初始状态
                  ┌────┬──────┬──────────┬────────┐
                  │ id │ name │department│ salary │
游标指向第1行 →   ├────┼──────┼──────────┼────────┤
   rs.next()      │ 1  │ 张三 │  技术部   │18000.00│
                  ├────┼──────┼──────────┼────────┤
游标指向第2行 →   │ 2  │ 李四 │  技术部   │20000.00│
   rs.next()      ├────┼──────┼──────────┼────────┤
                  │... │ ...  │   ...    │  ...   │
                  └────┴──────┴──────────┴────────┘
游标指向最后一行之后 → (after last)    ← rs.next()返回false
```

```java
while (rs.next()) {                         // 游标下移一行，有数据则进入循环
    // 按列名获取（推荐：可读性好）
    long id = rs.getLong("id");
    String name = rs.getString("name");
    
    // 按列索引获取（注意：索引从1开始！）
    // String name = rs.getString(2);  ← 第2列
    
    // 判断NULL
    String email = rs.getString("email");
    if (rs.wasNull()) {                     // getXxx()后立即调用wasNull()
        System.out.println("邮箱为空");
    }
}
```

> 🚨 **坑点：列索引从1开始，不是0！**
> ```java
> // ❌ 报错：Column Index out of range, 0 < 1
> rs.getString(0);
> 
> // ✅ 正确
> rs.getString(1);  // 第1列
> ```

> 🚨 **坑点：getString()遇到NULL**
> - `rs.getString("email")` 在email为NULL时返回Java的`null`（String是引用类型，可以为null）
> - 但 `rs.getInt("age")` 在age为NULL时返回 `0`（int是基本类型，不能为null）！
> - **判断NULL的正确方式**：先调用 `rs.getXxx()`，然后立即调用 `rs.wasNull()`

### 9.2.6 第6步：释放资源

数据库连接是非常宝贵的资源，用完必须释放，否则会导致**连接泄露（Connection Leak）**——连接池耗尽，新请求无法获取连接。

**传统方式（finally + 逐层关闭）**：

```java
Connection conn = null;
PreparedStatement pstmt = null;
ResultSet rs = null;
try {
    conn = DriverManager.getConnection(url, username, password);
    pstmt = conn.prepareStatement(sql);
    rs = pstmt.executeQuery();
    // ... 处理结果
} catch (SQLException e) {
    e.printStackTrace();
} finally {
    // 倒序关闭：rs → pstmt → conn
    if (rs != null) {
        try { rs.close(); } catch (SQLException e) { e.printStackTrace(); }
    }
    if (pstmt != null) {
        try { pstmt.close(); } catch (SQLException e) { e.printStackTrace(); }
    }
    if (conn != null) {
        try { conn.close(); } catch (SQLException e) { e.printStackTrace(); }
    }
}
```

**现代方式（try-with-resources，强烈推荐！）**：

```java
String sql = "SELECT id, name, department, salary FROM employee WHERE department = ?";

try (Connection conn = DriverManager.getConnection(url, username, password);
     PreparedStatement pstmt = conn.prepareStatement(sql)) {
    
    pstmt.setString(1, "技术部");
    
    try (ResultSet rs = pstmt.executeQuery()) {
        while (rs.next()) {
            System.out.println(rs.getString("name"));
        }
    }
    
} catch (SQLException e) {
    e.printStackTrace();
}
// 无需手动close！try-with-resources自动按声明顺序的逆序关闭资源
```

> 🚨 **try-with-resources 倒序关闭的原理**：
> - 声明顺序：conn → pstmt → rs
> - 关闭顺序：rs → pstmt → conn（自动倒序）
> - 必须先关ResultSet，再关Statement，最后关Connection
> - 原因：Statement关闭时会自动关闭其关联的ResultSet，Connection关闭时会自动关闭其关联的所有Statement。但依赖自动关闭不安全——如果关闭Connection时抛出异常，Statement和ResultSet可能不会被关闭

---

## 9.3 SQL注入深度演示（核心安全章节）

这是全书最重要的安全章节。**SQL注入是OWASP Top 10中最常见的Web安全漏洞之一**，理解它不仅能保护你的代码，也是面试高频考点。

### 9.3.1 场景设定

假设我们正在开发一个登录功能。用户输入用户名和密码，后端验证是否匹配。

**数据库中的user表**：

```sql
CREATE TABLE user (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(50) NOT NULL
);

INSERT INTO user (username, password) VALUES
('admin', '123456'),
('zhangsan', 'abc123');
```

user表当前数据：

| id | username | password |
|----|----------|----------|
| 1 | admin | 123456 |
| 2 | zhangsan | abc123 |

### 9.3.2 危险的拼接SQL方式（Statement）

```java
// ❌ 危险方式：用Statement拼接SQL
public boolean login(String inputUsername, String inputPassword) {
    String sql = "SELECT * FROM user WHERE username = '" 
               + inputUsername + "' AND password = '" 
               + inputPassword + "'";
    
    try (Connection conn = DriverManager.getConnection(url, username, password);
         Statement stmt = conn.createStatement();
         ResultSet rs = stmt.executeQuery(sql)) {
        
        return rs.next();  // 有结果 → 登录成功
    } catch (SQLException e) {
        e.printStackTrace();
        return false;
    }
}
```

### 9.3.3 正常登录

用户输入：`username = "admin"`, `password = "123456"`

```java
login("admin", "123456");
```

拼接出的SQL（正常）：

```sql
SELECT * FROM user WHERE username = 'admin' AND password = '123456'
```

数据库中有 `(admin, 123456)` 这条记录 → `rs.next()` 返回 `true` → **登录成功** ✅

---

### 9.3.4 攻击演示1：注释绕过密码

攻击者输入：

```
用户名: admin' -- 
密码:   （任意，甚至留空）
```

> `-- ` 是SQL中的注释符号（注意`--`后面必须有一个空格），它会注释掉后面的所有内容。

```java
login("admin' -- ", "任意");
```

拼接出的SQL（被篡改）：

```sql
SELECT * FROM user 
WHERE username = 'admin' -- ' AND password = '任意'
                         ↑
                   从这开始全是注释，被数据库忽略！
```

数据库实际执行的SQL相当于：

```sql
SELECT * FROM user WHERE username = 'admin'
```

只要`admin`用户存在，就返回一行 → `rs.next()` 返回 `true` → **登录成功！攻击者不知道密码也成功登录了！** ❌🔓

```
攻击流程图示：

用户输入: admin' -- 
         ┌──────┬──┬──┐
         │admin  │' │--│
         └──────┴──┴──┘
           用户名  闭合单引号  注释掉后续SQL

SQL模板: SELECT * FROM user WHERE username='[输入]' AND password='[输入]'

拼接结果: SELECT * FROM user WHERE username='admin' -- ' AND password='任意'
         ┌─────────────────────────────────────────┐ ┌──────────────┐
         │              有效SQL                      │   注释部分     │
         │  SELECT * FROM user WHERE username='admin'│   （被忽略）    │
         └─────────────────────────────────────────┘ └──────────────┘

结果: 绕过了密码验证！
```

### 9.3.5 攻击演示2：万能密码（OR永真式）

攻击者输入：

```
用户名: （任意，或者留空）
密码: ' OR '1'='1
```

```java
login("anything", "' OR '1'='1");
```

拼接出的SQL：

```sql
SELECT * FROM user 
WHERE username = 'anything' AND password = '' OR '1'='1'
                                           └──────────────┘
                                             永远为TRUE！
```

由于`OR`的存在，整个WHERE条件变为：

```
(username='anything' AND password='')  OR  '1'='1'
                 ↑ FALSE                       ↑ TRUE
                       └────── OR ──────────┘
                                 ↓
                              TRUE！
```

最终SQL等价于：

```sql
SELECT * FROM user WHERE TRUE
```

**返回用户表的所有行** → `rs.next()` 返回 `true` → **登录成功！甚至拿到了所有用户的数据！** ❌🔓🔓

```
攻击流程图示：

输入密码: ' OR '1'='1

SQL模板: SELECT * FROM user WHERE username='[输入]' AND password='[输入]'

拼接过程:
  username='anything' AND password='' OR '1'='1'
  └───────────────────┘         └──────────────┘
       原条件                      攻击注入的永真条件

布尔逻辑:
  (FALSE) OR (TRUE) = TRUE  →  绕过所有验证！

结果: 返回所有用户 → 登录成功 + 数据泄露
```

### 9.3.6 攻击演示3：删库跑路

攻击者输入：

```
用户名: （任意）
密码: '; DROP TABLE user; --
```

```java
login("anything", "'; DROP TABLE user; -- ");
```

拼接出的SQL（多条语句）：

```sql
SELECT * FROM user WHERE username = 'anything' AND password = '';
DROP TABLE user; -- '
```

MySQL默认不允许一次执行多条SQL（需要`allowMultiQueries=true`），但如果配置不当或使用其他数据库（如PostgreSQL支持多语句），这条攻击会成功——**整张user表被删除！**

```
拼接结果:
  SELECT * FROM user WHERE username = 'anything' AND password = '';
  DROP TABLE user; -- '

  └──第1条SQL：查询，返回空────┘ └──第2条SQL：删表！──┘
```

> 🚨 **严重警告：拼接SQL的用户输入永远不可信！**
> - 任何来自用户输入的数据（表单、URL参数、HTTP Header、文件上传内容）都可能包含恶意SQL代码
> - SQL注入不仅危害当前用户，还可能导致整库数据泄露、删除、篡改
> - 历史上最大的数据泄露事件中，很多都是SQL注入导致的

### 9.3.7 PreparedStatement防御原理

PreparedStatement是如何防住这些攻击的？关键在于**SQL模板与参数分离**：

```
传统Statement方式（拼接）：
┌──────────────────────────────────────────────────┐
│  SELECT * FROM user WHERE username='admin' -- ' AND password=''  │
│  └──────────────── 一条完整的SQL字符串 ──────────┘                │
│  数据库收到后：重新解析整个字符串（无法区分"代码"和"数据"）        │
└──────────────────────────────────────────────────┘

PreparedStatement方式（预编译）：
┌─────────────┐     ┌───────────────────┐
│  SQL模板     │     │  参数（单独发送）  │
│ SELECT *     │     │  param1: admin' --│
│ FROM user    │     │  param2: 任意     │
│ WHERE        │     └───────────────────┘
│ username = ? │             │
│ AND          │             ▼
│ password = ? │     参数被当作"纯数据"
└─────────────┘     单引号被自动转义为 \'
      │             分号被当作普通字符
      ▼             SQL关键字被当作字符串值
┌──────────────────────────────────────┐
│  数据库内部执行：                     │
│  (1) 先编译SQL模板（确定执行计划）     │
│  (2) 再将参数作为"值"填入             │
│  → 参数永远不可能改变SQL的语法结构！   │
└──────────────────────────────────────┘
```

用代码对比：

```java
// ❌ Statement拼接：admin' -- 中的单引号改变了SQL语法结构
String sql = "SELECT * FROM user WHERE username = 'admin' -- ' AND password = ''";

// ✅ PreparedStatement：admin' -- 整个被当作username的值
String template = "SELECT * FROM user WHERE username = ? AND password = ?";
pstmt.setString(1, "admin' -- ");  // 数据库将其处理为：username = 'admin\' -- '
pstmt.setString(2, "任意");
// 数据库实际执行的等价SQL：
// SELECT * FROM user WHERE username = 'admin\' -- ' AND password = '任意'
//                                    ↑ 这个单引号被转义了！
// 它查找 username 等于 "admin' -- " 的用户（不存在，所以登录失败）
```

**PreparedStatement的防御流程分步详解**：

```
第1步：Java程序发送SQL模板到数据库
  ┌─────────┐                    ┌──────────┐
  │  Java   │ ── ① 发送模板 ──→ │  MySQL   │
  │         │  SELECT ... WHERE  │          │
  │         │  username=? AND    │          │
  │         │  password=?         │          │
  └─────────┘                    └──────────┘
                                       │
                                 ② 解析+编译+优化
                                 生成执行计划（缓存起来）
                                       │
  ┌─────────┐                    ┌──────────┐
  │  Java   │ ── ③ 发送参数 ──→ │  MySQL   │
  │         │  param[0]="admin'--"│        │
  │         │  param[1]="123"    │          │
  └─────────┘                    └──────────┘
                                       │
                                 ④ 将参数填入已编译的模板
                                 单引号 → 转义为 \'
                                 分号 → 当作普通字符
                                       │
                                 ⑤ 执行（参数不会改变SQL结构）
```

> 🚨 **坑点：PreparedStatement不能防御表名/列名/ORDER BY注入**
> 
> ```java
> // ❌ 占位符只能替代"值"（WHERE条件的值、INSERT的字段值），不能替代以下内容：
> String sql = "SELECT * FROM ? WHERE ? = ?";     // ?不能替代表名
> String sql = "SELECT * FROM user ORDER BY ?";    // ?不能替代ORDER BY字段
> String sql = "SELECT * FROM user WHERE name LIKE '%?%'";  // ?在字符串中无效
> ```
> 
> **如果需要动态表名或列名**，必须使用**白名单校验**：
> ```java
> private static final Set<String> ALLOWED_TABLES = Set.of("employee", "user", "department");
> private static final Set<String> ALLOWED_COLUMNS = Set.of("id", "name", "salary", "department");
> 
> public void dynamicQuery(String tableName, String orderColumn) {
>     if (!ALLOWED_TABLES.contains(tableName)) {
>         throw new IllegalArgumentException("非法的表名: " + tableName);
>     }
>     if (!ALLOWED_COLUMNS.contains(orderColumn)) {
>         throw new IllegalArgumentException("非法的排序列: " + orderColumn);
>     }
>     // 此时可以安全地拼接到SQL中（因为值来自白名单，不是用户任意输入）
>     String sql = "SELECT * FROM " + tableName + " ORDER BY " + orderColumn;
> }
> ```

---

## 9.4 JDBC事务控制

在第8章我们学习了手动SQL事务（START TRANSACTION / COMMIT / ROLLBACK），在JDBC中同样可以控制事务。

### 9.4.1 默认行为：自动提交

JDBC连接创建后，默认是**自动提交（auto-commit）**模式：

```java
Connection conn = DriverManager.getConnection(url, username, password);
// 此时 conn.getAutoCommit() 返回 true
// 每条 executeUpdate() 都是一个独立的事务，执行完自动提交
```

这会导致什么后果？以转账为例：

```java
// ❌ 危险：默认自动提交
String deduct = "UPDATE account SET balance = balance - 5000 WHERE name = '张三'";
String add = "UPDATE account SET balance = balance + 5000 WHERE name = '李四'";

stmt.executeUpdate(deduct);  // ← 这条执行完立刻提交了！
// 如果这里程序崩溃……
stmt.executeUpdate(add);     // ← 这条永远执行不到
// 结果：张三的钱扣了，李四的钱没加！5000元凭空消失！
```

> 🚨 **坑点：忘记关闭自动提交 = 失去事务保护**
> - 任何需要多条SQL构成一个原子操作的场景（转账、下单减库存、创建订单+订单明细），都必须关闭自动提交
> - 这是个非常隐蔽的bug：平时测试可能没问题（程序不崩溃），一旦出现异常就数据不一致

### 9.4.2 手动事务控制

```java
Connection conn = null;
try {
    conn = DriverManager.getConnection(url, username, password);
    conn.setAutoCommit(false);  // ← 关闭自动提交，开启手动事务
    
    // 第1步：张三减5000
    try (PreparedStatement pstmt1 = conn.prepareStatement(
            "UPDATE account SET balance = balance - 5000 WHERE name = ?")) {
        pstmt1.setString(1, "张三");
        int rows1 = pstmt1.executeUpdate();
        if (rows1 != 1) {
            throw new RuntimeException("张三扣款失败（可能余额不足或用户不存在）");
        }
    }
    
    // 第2步：李四加5000
    try (PreparedStatement pstmt2 = conn.prepareStatement(
            "UPDATE account SET balance = balance + 5000 WHERE name = ?")) {
        pstmt2.setString(1, "李四");
        int rows2 = pstmt2.executeUpdate();
        if (rows2 != 1) {
            throw new RuntimeException("李四加款失败（用户不存在）");
        }
    }
    
    // 两步都成功 → 提交
    conn.commit();
    System.out.println("转账成功！");
    
} catch (Exception e) {
    // 任何一步失败 → 回滚！
    if (conn != null) {
        try {
            conn.rollback();
            System.out.println("转账失败，已回滚：" + e.getMessage());
        } catch (SQLException ex) {
            ex.printStackTrace();
        }
    }
} finally {
    if (conn != null) {
        try {
            conn.setAutoCommit(true);  // 恢复自动提交（好习惯）
            conn.close();
        } catch (SQLException e) {
            e.printStackTrace();
        }
    }
}
```

事务控制的关键API：

| 方法 | 作用 |
|------|------|
| `conn.setAutoCommit(false)` | 关闭自动提交，开始事务 |
| `conn.commit()` | 提交事务（所有操作生效） |
| `conn.rollback()` | 回滚事务（所有操作撤销） |
| `conn.setAutoCommit(true)` | 恢复自动提交 |

> 🚨 **关键习惯**：`rollback()` 必须写在catch块中，`commit()` 必须写在所有操作成功之后。这是"要么全成功，要么全失败"的代码保障。

---

## 9.5 连接池

### 9.5.1 为什么需要连接池？

回顾9.2节——每一次数据库操作都要经历：

```
① 建立TCP连接（三次握手）
② MySQL认证（用户名密码验证）
③ 执行SQL
④ 关闭TCP连接（四次挥手）
```

如果每个HTTP请求都要经历①②④这三个步骤，想象一个场景：

- 你的API每秒处理1000个请求
- 每个请求执行1次数据库查询
- TCP建立耗时约10ms，认证耗时约5ms

那么每秒花在"建立连接"上的时间就是：**1000 × (10 + 5) = 15000ms = 15秒**——你每秒只有1秒的"有效工作时间"，其他15秒全在建立和关闭连接！

**连接池的解决方案**：

```
不使用连接池（每次新建-销毁）：
  请求1 → CREATE → 执行SQL → DESTROY
  请求2 → CREATE → 执行SQL → DESTROY
  请求3 → CREATE → 执行SQL → DESTROY
  每次都要 CREATE + DESTROY（昂贵！）

使用连接池（借用-归还）：
  启动时预创建：  [conn1] [conn2] [conn3] ... [conn10]  ← 池中有10个连接
  
  请求1 → BORROW(conn1) → 执行SQL → RETURN(conn1)
  请求2 → BORROW(conn2) → 执行SQL → RETURN(conn2)
  请求3 → BORROW(conn1) → 执行SQL → RETURN(conn1)  ← conn1已归还，可以复用！
  ...
  连接用完归还池中，下个请求直接借用，无需重新建立
```

**类比**：不用连接池就像每次出门都买一辆新车，用完就扔；用连接池就像共享单车——需要时扫码骑走，用完锁车归还。

### 9.5.2 Druid连接池

Alibaba Druid是阿里巴巴开源的高性能数据库连接池，它不仅是连接池，还提供了强大的监控功能。

**添加Maven依赖**：

```xml
<dependency>
    <groupId>com.alibaba</groupId>
    <artifactId>druid</artifactId>
    <version>1.2.20</version>
</dependency>
```

**druid.properties配置文件**：

```properties
# 数据库连接信息
url=jdbc:mysql://localhost:3306/ems?useSSL=false&serverTimezone=Asia/Shanghai&characterEncoding=utf8mb4
username=root
password=你的密码
driverClassName=com.mysql.cj.jdbc.Driver

# 连接池核心参数
initialSize=5                      # 启动时初始连接数
minIdle=5                          # 最小空闲连接数（池中至少保留这么多连接）
maxActive=20                       # 最大活动连接数（同时最多20个连接）
maxWait=3000                       # 获取连接最大等待时间(ms)，超时抛异常
# ↑ 重要！不设置maxWait，获取不到连接会无限等待

# 连接健康检查
validationQuery=SELECT 1           # 验证连接是否有效的测试SQL
testWhileIdle=true                 # 空闲时检测（推荐开启）
testOnBorrow=false                 # 借出时检测（影响性能，不推荐）
testOnReturn=false                 # 归还时检测（不推荐）
timeBetweenEvictionRunsMillis=60000 # 检测间隔（60秒检查一次空闲连接）

# 连接超时与回收
minEvictableIdleTimeMillis=300000  # 连接最小空闲时间（5分钟后可回收）
removeAbandoned=true               # 回收泄露的连接
removeAbandonedTimeout=300         # 泄露的连接超过300秒回收
logAbandoned=true                  # 记录泄露连接的日志

# 监控统计
filters=stat,wall,log4j            # 统计、SQL防火墙、日志
```

**Druid连接池使用示例**：

```java
import com.alibaba.druid.pool.DruidDataSourceFactory;
import javax.sql.DataSource;
import java.io.InputStream;
import java.sql.*;
import java.util.Properties;

public class DruidDemo {
    private static DataSource dataSource;
    
    static {
        try (InputStream is = DruidDemo.class.getClassLoader()
                .getResourceAsStream("druid.properties")) {
            Properties props = new Properties();
            props.load(is);
            dataSource = DruidDataSourceFactory.createDataSource(props);
            System.out.println("Druid连接池初始化成功！");
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
    
    public static Connection getConnection() throws SQLException {
        return dataSource.getConnection();  // 从池中借一个连接
    }
    
    public static void main(String[] args) {
        String sql = "SELECT * FROM employee WHERE salary > ?";
        
        try (Connection conn = getConnection();   // ← 从连接池借
             PreparedStatement pstmt = conn.prepareStatement(sql)) {
            
            pstmt.setDouble(1, 15000);
            
            try (ResultSet rs = pstmt.executeQuery()) {
                while (rs.next()) {
                    System.out.println(rs.getString("name") 
                            + " - " + rs.getDouble("salary"));
                }
            }
            // try-with-resources结束 → conn.close() → 归还到连接池（非真正关闭）
            
        } catch (SQLException e) {
            e.printStackTrace();
        }
    }
}
```

> 🚨 **坑点：maxActive设置太小 → 并发时获取连接超时**
> - 当并发请求数超过maxActive时，新请求会在maxWait时间内等待
> - 如果maxWait到期仍没有可用连接 → 抛出 `GetConnectionTimeoutException`
> - **经验值**：maxActive = (CPU核心数 × 2) + 有效磁盘数，一般业务20-50足够

> 🚨 **坑点：不配置maxWait → 无限等待**
> - 如果不设置maxWait，Druid默认会无限等待直到获取连接
> - 在高并发时，大量线程阻塞在获取连接上 → 线程池耗尽 → 系统雪崩
> - **必须设置maxWait，通常3000ms（3秒）较为合理**

### 9.5.3 HikariCP — Spring Boot的默认连接池

如果你将来使用Spring Boot，它会自动使用 **HikariCP**（日语"光"，意为"快如光速"），是公认的最快JDBC连接池：

```yaml
# Spring Boot中只需在application.yml配置
spring:
  datasource:
    url: jdbc:mysql://localhost:3306/ems?useSSL=false&serverTimezone=Asia/Shanghai
    username: root
    password: 你的密码
    hikari:
      maximum-pool-size: 20
      minimum-idle: 5
      connection-timeout: 3000
```

HikariCP没有Druid的SQL监控和防火墙功能，但在纯粹的性能上略胜一筹。实际项目中，两者都非常流行。

---

## 9.6 DAO模式

### 9.6.1 为什么需要分层？

如果直接在main方法里写JDBC代码（像前面所有示例那样），时间久了会变成这样：

```java
// ❌ 混乱：业务逻辑和数据库操作搅在一起
public static void main(String[] args) {
    // 连接数据库
    // 验证输入
    // 查询员工
    // 计算涨薪幅度
    // 更新数据库
    // 打印结果
    // 关闭连接
    // ... 300行代码全混在一个方法里！
}
```

**DAO（Data Access Object）模式**就是为了解决这个问题。它将数据库操作封装在专门的类中，实现关注点分离：

```
┌──────────────────────────────────────────┐
│              表示层 (Controller)          │  ← 处理用户输入/输出
│            参数校验、数据格式化            │
├──────────────────────────────────────────┤
│              业务层 (Service)             │  ← 处理业务逻辑
│          事务管理、业务规则验证            │
├──────────────────────────────────────────┤
│              数据访问层 (DAO)              │  ← 只负责数据库操作
│       CRUD SQL、连接管理、结果封装         │
├──────────────────────────────────────────┤
│               数据库 (MySQL)              │
└──────────────────────────────────────────┘
```

### 9.6.2 DAO模式实现

**Employee实体类**：

```java
public class Employee {
    private Long id;
    private String name;
    private Integer age;
    private String department;
    private Double salary;
    private String email;
    private String hireDate;
    
    // 无参构造 + 全参构造 + getter/setter 省略
}
```

**DAO接口（定义契约）**：

```java
import java.util.List;

public interface EmployeeDao {
    List<Employee> findAll() throws SQLException;
    Employee findById(Long id) throws SQLException;
    List<Employee> findByDepartment(String department) throws SQLException;
    int insert(Employee emp) throws SQLException;
    int update(Employee emp) throws SQLException;
    int deleteById(Long id) throws SQLException;
}
```

**DAO实现类**：

```java
import com.alibaba.druid.pool.DruidDataSourceFactory;
import javax.sql.DataSource;
import java.io.InputStream;
import java.sql.*;
import java.util.ArrayList;
import java.util.List;
import java.util.Properties;

public class EmployeeDaoImpl implements EmployeeDao {
    
    private static DataSource dataSource;
    
    static {
        try (InputStream is = EmployeeDaoImpl.class.getClassLoader()
                .getResourceAsStream("druid.properties")) {
            Properties props = new Properties();
            props.load(is);
            dataSource = DruidDataSourceFactory.createDataSource(props);
        } catch (Exception e) {
            throw new RuntimeException("Druid连接池初始化失败", e);
        }
    }
    
    @Override
    public List<Employee> findAll() throws SQLException {
        String sql = "SELECT id, name, age, department, salary, email, hire_date FROM employee";
        List<Employee> list = new ArrayList<>();
        
        try (Connection conn = dataSource.getConnection();
             PreparedStatement pstmt = conn.prepareStatement(sql);
             ResultSet rs = pstmt.executeQuery()) {
            
            while (rs.next()) {
                list.add(rowToEmployee(rs));
            }
        }
        return list;
    }
    
    @Override
    public Employee findById(Long id) throws SQLException {
        String sql = "SELECT id, name, age, department, salary, email, hire_date FROM employee WHERE id = ?";
        
        try (Connection conn = dataSource.getConnection();
             PreparedStatement pstmt = conn.prepareStatement(sql)) {
            
            pstmt.setLong(1, id);
            
            try (ResultSet rs = pstmt.executeQuery()) {
                if (rs.next()) {
                    return rowToEmployee(rs);
                }
            }
        }
        return null;
    }
    
    @Override
    public List<Employee> findByDepartment(String department) throws SQLException {
        String sql = "SELECT id, name, age, department, salary, email, hire_date FROM employee WHERE department = ?";
        List<Employee> list = new ArrayList<>();
        
        try (Connection conn = dataSource.getConnection();
             PreparedStatement pstmt = conn.prepareStatement(sql)) {
            
            pstmt.setString(1, department);
            
            try (ResultSet rs = pstmt.executeQuery()) {
                while (rs.next()) {
                    list.add(rowToEmployee(rs));
                }
            }
        }
        return list;
    }
    
    @Override
    public int insert(Employee emp) throws SQLException {
        String sql = "INSERT INTO employee (name, age, department, salary, email) VALUES (?, ?, ?, ?, ?)";
        
        try (Connection conn = dataSource.getConnection();
             PreparedStatement pstmt = conn.prepareStatement(sql)) {
            
            pstmt.setString(1, emp.getName());
            pstmt.setInt(2, emp.getAge());
            pstmt.setString(3, emp.getDepartment());
            pstmt.setDouble(4, emp.getSalary());
            pstmt.setString(5, emp.getEmail());
            
            return pstmt.executeUpdate();
        }
    }
    
    @Override
    public int update(Employee emp) throws SQLException {
        String sql = "UPDATE employee SET name=?, age=?, department=?, salary=?, email=? WHERE id=?";
        
        try (Connection conn = dataSource.getConnection();
             PreparedStatement pstmt = conn.prepareStatement(sql)) {
            
            pstmt.setString(1, emp.getName());
            pstmt.setInt(2, emp.getAge());
            pstmt.setString(3, emp.getDepartment());
            pstmt.setDouble(4, emp.getSalary());
            pstmt.setString(5, emp.getEmail());
            pstmt.setLong(6, emp.getId());
            
            return pstmt.executeUpdate();
        }
    }
    
    @Override
    public int deleteById(Long id) throws SQLException {
        String sql = "DELETE FROM employee WHERE id = ?";
        
        try (Connection conn = dataSource.getConnection();
             PreparedStatement pstmt = conn.prepareStatement(sql)) {
            
            pstmt.setLong(1, id);
            return pstmt.executeUpdate();
        }
    }
    
    // 辅助方法：将ResultSet当前行转换为Employee对象
    private Employee rowToEmployee(ResultSet rs) throws SQLException {
        Employee emp = new Employee();
        emp.setId(rs.getLong("id"));
        emp.setName(rs.getString("name"));
        emp.setAge(rs.getInt("age"));
        emp.setDepartment(rs.getString("department"));
        emp.setSalary(rs.getDouble("salary"));
        emp.setEmail(rs.getString("email"));
        emp.setHireDate(rs.getString("hire_date"));
        return emp;
    }
}
```

> **预告**：到了Spring Boot + MyBatis章节（第13章），你会发现MyBatis本质上就是自动帮你做了上面这些事情——它通过XML或注解定义SQL和对象映射，底层依然是JDBC（PreparedStatement + ResultSet封装）。

### 9.6.3 分层职责对比

回顾目前在DAO层看到的所有操作，它们的职责非常纯粹——**只管数据库**。而业务逻辑（如"新员工入职需要发送邮件通知"、"涨薪幅度不能超过20%"）应该放在Service层。

| 层 | 职责 | 不应做的事 |
|----|------|-----------|
| **DAO** | CRUD SQL、连接获取归还 | 业务规则判断、发送邮件、事务控制（复杂场景事务在Service层） |
| **Service** | 业务规则、事务控制、调用DAO | 写SQL、手动管理Connection |
| **Controller** | 参数校验、调用Service、响应格式化 | 直接调用DAO、处理SQL异常 |

---

## EMS v2：JDBC版员工管理系统

终于到了动手实践的环节！我们将在第7章EMS v1（纯Java命令行版）的基础上，用JDBC+MySQL替换原来的List内存存储，实现**持久化的员工管理**。

### v2 vs v1对比

| 对比维度 | EMS v1（第7章） | EMS v2（本章） |
|----------|---------------|---------------|
| 存储方式 | `List<Employee>` 内存存储 | MySQL数据库持久化 |
| 数据持久性 | 程序退出即丢失 | 永久保存 |
| 多实例共享 | ❌ 不共享 | ✅ 共用同一数据库 |
| 技术栈 | Java SE | Java SE + JDBC + Druid + MySQL |
| SQL注入防护 | 不涉及 | PreparedStatement全覆盖 |

### 项目结构

```
ems-jdbc/
├── pom.xml
├── src/main/resources/
│   └── druid.properties              ← 连接池配置
└── src/main/java/com/ems/
    ├── Main.java                     ← 程序入口（命令行菜单）
    ├── entity/
    │   └── Employee.java             ← 实体类
    ├── dao/
    │   ├── EmployeeDao.java          ← DAO接口
    │   └── EmployeeDaoImpl.java      ← DAO实现（Druid+PreparedStatement）
    └── service/
        └── EmployeeService.java       ← 业务层（事务控制）
```

### 代码实现

**pom.xml**：

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0
         http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <groupId>com.ems</groupId>
    <artifactId>ems-jdbc</artifactId>
    <version>2.0</version>

    <properties>
        <maven.compiler.source>17</maven.compiler.source>
        <maven.compiler.target>17</maven.compiler.target>
        <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
    </properties>

    <dependencies>
        <!-- MySQL驱动 -->
        <dependency>
            <groupId>com.mysql</groupId>
            <artifactId>mysql-connector-j</artifactId>
            <version>8.2.0</version>
        </dependency>
        <!-- Druid连接池 -->
        <dependency>
            <groupId>com.alibaba</groupId>
            <artifactId>druid</artifactId>
            <version>1.2.20</version>
        </dependency>
    </dependencies>
</project>
```

**druid.properties**（注意替换数据库密码）：

```properties
url=jdbc:mysql://localhost:3306/ems?useSSL=false&serverTimezone=Asia/Shanghai&characterEncoding=utf8mb4
username=root
password=你的密码
driverClassName=com.mysql.cj.jdbc.Driver
initialSize=5
minIdle=5
maxActive=20
maxWait=3000
```

**Employee.java**：

```java
package com.ems.entity;

public class Employee {
    private Long id;
    private String name;
    private Integer age;
    private String department;
    private Double salary;
    private String email;
    private String hireDate;

    public Employee() {}

    public Employee(String name, Integer age, String department, Double salary, String email) {
        this.name = name;
        this.age = age;
        this.department = department;
        this.salary = salary;
        this.email = email;
    }

    // ===== getter/setter =====
    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }

    public String getName() { return name; }
    public void setName(String name) { this.name = name; }

    public Integer getAge() { return age; }
    public void setAge(Integer age) { this.age = age; }

    public String getDepartment() { return department; }
    public void setDepartment(String department) { this.department = department; }

    public Double getSalary() { return salary; }
    public void setSalary(Double salary) { this.salary = salary; }

    public String getEmail() { return email; }
    public void setEmail(String email) { this.email = email; }

    public String getHireDate() { return hireDate; }
    public void setHireDate(String hireDate) { this.hireDate = hireDate; }

    @Override
    public String toString() {
        return String.format(
            "ID: %d | 姓名: %s | 年龄: %d | 部门: %s | 薪资: %.2f | 邮箱: %s | 入职: %s",
            id, name, age, department, salary, email, hireDate
        );
    }
}
```

**EmployeeDao.java**：

```java
package com.ems.dao;

import com.ems.entity.Employee;
import java.sql.SQLException;
import java.util.List;

public interface EmployeeDao {
    List<Employee> findAll() throws SQLException;
    Employee findById(Long id) throws SQLException;
    List<Employee> findByDepartment(String department) throws SQLException;
    List<Employee> findBySalaryRange(Double min, Double max) throws SQLException;
    int insert(Employee emp) throws SQLException;
    int update(Employee emp) throws SQLException;
    int deleteById(Long id) throws SQLException;
}
```

**EmployeeDaoImpl.java**：

```java
package com.ems.dao;

import com.alibaba.druid.pool.DruidDataSourceFactory;
import com.ems.entity.Employee;

import javax.sql.DataSource;
import java.io.InputStream;
import java.sql.*;
import java.util.ArrayList;
import java.util.List;
import java.util.Properties;

public class EmployeeDaoImpl implements EmployeeDao {

    private static DataSource dataSource;

    static {
        try (InputStream is = EmployeeDaoImpl.class.getClassLoader()
                .getResourceAsStream("druid.properties")) {
            Properties props = new Properties();
            props.load(is);
            dataSource = DruidDataSourceFactory.createDataSource(props);
        } catch (Exception e) {
            System.err.println("Druid连接池初始化失败, 请检查 druid.properties 配置！");
            throw new RuntimeException(e);
        }
    }

    @Override
    public List<Employee> findAll() throws SQLException {
        String sql = "SELECT id, name, age, department, salary, email, hire_date FROM employee ORDER BY id";
        List<Employee> list = new ArrayList<>();
        try (Connection conn = dataSource.getConnection();
             PreparedStatement pstmt = conn.prepareStatement(sql);
             ResultSet rs = pstmt.executeQuery()) {
            while (rs.next()) {
                list.add(buildEmployee(rs));
            }
        }
        return list;
    }

    @Override
    public Employee findById(Long id) throws SQLException {
        String sql = "SELECT id, name, age, department, salary, email, hire_date FROM employee WHERE id = ?";
        try (Connection conn = dataSource.getConnection();
             PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setLong(1, id);
            try (ResultSet rs = pstmt.executeQuery()) {
                if (rs.next()) {
                    return buildEmployee(rs);
                }
            }
        }
        return null;
    }

    @Override
    public List<Employee> findByDepartment(String department) throws SQLException {
        String sql = "SELECT id, name, age, department, salary, email, hire_date FROM employee WHERE department = ? ORDER BY id";
        List<Employee> list = new ArrayList<>();
        try (Connection conn = dataSource.getConnection();
             PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setString(1, department);
            try (ResultSet rs = pstmt.executeQuery()) {
                while (rs.next()) {
                    list.add(buildEmployee(rs));
                }
            }
        }
        return list;
    }

    @Override
    public List<Employee> findBySalaryRange(Double min, Double max) throws SQLException {
        String sql = "SELECT id, name, age, department, salary, email, hire_date FROM employee WHERE salary BETWEEN ? AND ? ORDER BY salary DESC";
        List<Employee> list = new ArrayList<>();
        try (Connection conn = dataSource.getConnection();
             PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setDouble(1, min);
            pstmt.setDouble(2, max);
            try (ResultSet rs = pstmt.executeQuery()) {
                while (rs.next()) {
                    list.add(buildEmployee(rs));
                }
            }
        }
        return list;
    }

    @Override
    public int insert(Employee emp) throws SQLException {
        String sql = "INSERT INTO employee (name, age, department, salary, email) VALUES (?, ?, ?, ?, ?)";
        try (Connection conn = dataSource.getConnection();
             PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setString(1, emp.getName());
            pstmt.setInt(2, emp.getAge());
            pstmt.setString(3, emp.getDepartment());
            pstmt.setDouble(4, emp.getSalary());
            pstmt.setString(5, emp.getEmail());
            return pstmt.executeUpdate();
        }
    }

    @Override
    public int update(Employee emp) throws SQLException {
        String sql = "UPDATE employee SET name=?, age=?, department=?, salary=?, email=? WHERE id=?";
        try (Connection conn = dataSource.getConnection();
             PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setString(1, emp.getName());
            pstmt.setInt(2, emp.getAge());
            pstmt.setString(3, emp.getDepartment());
            pstmt.setDouble(4, emp.getSalary());
            pstmt.setString(5, emp.getEmail());
            pstmt.setLong(6, emp.getId());
            return pstmt.executeUpdate();
        }
    }

    @Override
    public int deleteById(Long id) throws SQLException {
        String sql = "DELETE FROM employee WHERE id = ?";
        try (Connection conn = dataSource.getConnection();
             PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setLong(1, id);
            return pstmt.executeUpdate();
        }
    }

    private Employee buildEmployee(ResultSet rs) throws SQLException {
        Employee emp = new Employee();
        emp.setId(rs.getLong("id"));
        emp.setName(rs.getString("name"));
        // age可能为数据库NULL，getInt返回0
        int age = rs.getInt("age");
        emp.setAge(rs.wasNull() ? null : age);
        emp.setDepartment(rs.getString("department"));
        emp.setSalary(rs.getDouble("salary"));
        emp.setEmail(rs.getString("email"));
        emp.setHireDate(rs.getString("hire_date"));
        return emp;
    }
}
```

**EmployeeService.java（业务层 + 事务控制）**：

```java
package com.ems.service;

import com.ems.dao.EmployeeDao;
import com.ems.dao.EmployeeDaoImpl;
import com.ems.entity.Employee;

import javax.sql.DataSource;
import java.sql.Connection;
import java.sql.SQLException;
import java.util.List;

public class EmployeeService {

    private final EmployeeDao employeeDao = new EmployeeDaoImpl();

    // ============ 查询操作（无需事务）============

    public List<Employee> listAll() {
        try {
            return employeeDao.findAll();
        } catch (SQLException e) {
            throw new RuntimeException("查询所有员工失败", e);
        }
    }

    public Employee getById(Long id) {
        try {
            return employeeDao.findById(id);
        } catch (SQLException e) {
            throw new RuntimeException("查询员工失败, id=" + id, e);
        }
    }

    public List<Employee> searchByDepartment(String department) {
        try {
            return employeeDao.findByDepartment(department);
        } catch (SQLException e) {
            throw new RuntimeException("按部门查询失败", e);
        }
    }

    public List<Employee> searchBySalaryRange(Double min, Double max) {
        try {
            return employeeDao.findBySalaryRange(min, max);
        } catch (SQLException e) {
            throw new RuntimeException("按薪资范围查询失败", e);
        }
    }

    // ============ 写操作（简单操作，DaoImpl内部try-with-resources自动管理）============

    public void addEmployee(Employee emp) {
        try {
            int rows = employeeDao.insert(emp);
            if (rows > 0) {
                System.out.println("✅ 员工添加成功: " + emp.getName());
            } else {
                System.out.println("❌ 添加失败");
            }
        } catch (SQLException e) {
            throw new RuntimeException("添加员工失败", e);
        }
    }

    public void updateEmployee(Employee emp) {
        try {
            int rows = employeeDao.update(emp);
            if (rows > 0) {
                System.out.println("✅ 员工信息更新成功: ID=" + emp.getId());
            } else {
                System.out.println("❌ 更新失败: 员工不存在");
            }
        } catch (SQLException e) {
            throw new RuntimeException("更新员工失败", e);
        }
    }

    public void deleteEmployee(Long id) {
        try {
            int rows = employeeDao.deleteById(id);
            if (rows > 0) {
                System.out.println("✅ 员工删除成功: ID=" + id);
            } else {
                System.out.println("❌ 删除失败: 员工不存在");
            }
        } catch (SQLException e) {
            throw new RuntimeException("删除员工失败", e);
        }
    }

    public void displayAll() {
        List<Employee> list = listAll();
        if (list.isEmpty()) {
            System.out.println("📭 暂无员工数据");
        } else {
            System.out.println("========== 员工列表 (共" + list.size() + "人) ==========");
            for (Employee emp : list) {
                System.out.println(emp);
            }
            System.out.println("===============================================");
        }
    }
}
```

**Main.java（命令行交互）**：

```java
package com.ems;

import com.ems.entity.Employee;
import com.ems.service.EmployeeService;

import java.util.List;
import java.util.Scanner;

public class Main {

    private static final EmployeeService service = new EmployeeService();
    private static final Scanner scanner = new Scanner(System.in);

    public static void main(String[] args) {
        System.out.println("========================================");
        System.out.println("   EMS v2 — JDBC版员工管理系统");
        System.out.println("   数据库: MySQL 8.0 + Druid连接池");
        System.out.println("========================================");
        
        while (true) {
            printMenu();
            String choice = scanner.nextLine().trim();
            
            switch (choice) {
                case "1" -> service.displayAll();
                case "2" -> searchByDepartment();
                case "3" -> searchBySalaryRange();
                case "4" -> viewById();
                case "5" -> addEmployee();
                case "6" -> updateEmployee();
                case "7" -> deleteEmployee();
                case "0" -> {
                    System.out.println("👋 再见！");
                    return;
                }
                default -> System.out.println("⚠ 无效选项，请重新输入");
            }
        }
    }

    private static void printMenu() {
        System.out.println("\n===== 功能菜单 =====");
        System.out.println("1. 查看所有员工");
        System.out.println("2. 按部门查询");
        System.out.println("3. 按薪资范围查询");
        System.out.println("4. 按ID查看详情");
        System.out.println("5. 添加新员工");
        System.out.println("6. 修改员工信息");
        System.out.println("7. 删除员工");
        System.out.println("0. 退出系统");
        System.out.print("请选择: ");
    }

    private static void searchByDepartment() {
        System.out.print("输入部门名称: ");
        String dept = scanner.nextLine().trim();
        List<Employee> list = service.searchByDepartment(dept);
        printList(list, "【" + dept + "】员工列表");
    }

    private static void searchBySalaryRange() {
        System.out.print("最低薪资: ");
        double min = Double.parseDouble(scanner.nextLine().trim());
        System.out.print("最高薪资: ");
        double max = Double.parseDouble(scanner.nextLine().trim());
        List<Employee> list = service.searchBySalaryRange(min, max);
        printList(list, "薪资范围 [" + min + " - " + max + "] 员工");
    }

    private static void viewById() {
        System.out.print("输入员工ID: ");
        Long id = Long.parseLong(scanner.nextLine().trim());
        Employee emp = service.getById(id);
        if (emp != null) {
            System.out.println("========== 员工详情 ==========");
            System.out.println(emp);
            System.out.println("===============================");
        } else {
            System.out.println("❌ 未找到ID为 " + id + " 的员工");
        }
    }

    private static void addEmployee() {
        System.out.println("===== 添加新员工 =====");
        System.out.print("姓名: ");
        String name = scanner.nextLine().trim();
        System.out.print("年龄: ");
        int age = Integer.parseInt(scanner.nextLine().trim());
        System.out.print("部门: ");
        String dept = scanner.nextLine().trim();
        System.out.print("薪资: ");
        double salary = Double.parseDouble(scanner.nextLine().trim());
        System.out.print("邮箱: ");
        String email = scanner.nextLine().trim();

        Employee emp = new Employee(name, age, dept, salary, email);
        service.addEmployee(emp);
    }

    private static void updateEmployee() {
        System.out.print("输入要修改的员工ID: ");
        Long id = Long.parseLong(scanner.nextLine().trim());
        Employee emp = service.getById(id);
        if (emp == null) {
            System.out.println("❌ 员工不存在！");
            return;
        }
        System.out.println("当前信息: " + emp);
        System.out.println("（直接回车保留原值）");
        
        System.out.print("新姓名 [" + emp.getName() + "]: ");
        String name = scanner.nextLine().trim();
        if (!name.isEmpty()) emp.setName(name);

        System.out.print("新年龄 [" + emp.getAge() + "]: ");
        String ageStr = scanner.nextLine().trim();
        if (!ageStr.isEmpty()) emp.setAge(Integer.parseInt(ageStr));

        System.out.print("新部门 [" + emp.getDepartment() + "]: ");
        String dept = scanner.nextLine().trim();
        if (!dept.isEmpty()) emp.setDepartment(dept);

        System.out.print("新薪资 [" + emp.getSalary() + "]: ");
        String salaryStr = scanner.nextLine().trim();
        if (!salaryStr.isEmpty()) emp.setSalary(Double.parseDouble(salaryStr));

        System.out.print("新邮箱 [" + emp.getEmail() + "]: ");
        String email = scanner.nextLine().trim();
        if (!email.isEmpty()) emp.setEmail(email);

        service.updateEmployee(emp);
    }

    private static void deleteEmployee() {
        System.out.print("输入要删除的员工ID: ");
        Long id = Long.parseLong(scanner.nextLine().trim());
        service.deleteEmployee(id);
    }

    private static void printList(List<Employee> list, String title) {
        if (list.isEmpty()) {
            System.out.println("📭 " + title + ": 无数据");
        } else {
            System.out.println("========== " + title + " (共" + list.size() + "人) ==========");
            for (Employee emp : list) {
                System.out.println(emp);
            }
            System.out.println("===============================================");
        }
    }
}
```

### 运行演示

```
========================================
   EMS v2 — JDBC版员工管理系统
   数据库: MySQL 8.0 + Druid连接池
========================================

===== 功能菜单 =====
1. 查看所有员工
5. 添加新员工
0. 退出系统
请选择: 5

===== 添加新员工 =====
姓名: 孙八
年龄: 27
部门: 市场部
薪资: 14000
邮箱: sunba@example.com
✅ 员工添加成功: 孙八

===== 功能菜单 =====
请选择: 1

========== 员工列表 (共6人) ==========
ID: 1 | 姓名: 张三 | 年龄: 28 | 部门: 技术部 | 薪资: 18000.00 | 邮箱: zhangsan@example.com | 入职: 2026-05-22
ID: 2 | 姓名: 李四 | 年龄: 32 | 部门: 技术部 | 薪资: 20000.00 | 邮箱: lisi@example.com | 入职: 2026-05-22
ID: 3 | 姓名: 王五 | 年龄: 25 | 部门: 市场部 | 薪资: 12000.00 | 邮箱: wangwu@example.com | 入职: 2026-05-22
ID: 4 | 姓名: 赵六 | 年龄: 35 | 部门: 人事部 | 薪资: 18000.00 | 邮箱: zhaoliu@example.com | 入职: 2026-05-22
ID: 5 | 姓名: 钱七 | 年龄: 29 | 部门: 技术部 | 薪资: 16000.00 | 邮箱: qianqi@example.com | 入职: 2026-05-22
ID: 7 | 姓名: 孙八 | 年龄: 27 | 部门: 市场部 | 薪资: 14000.00 | 邮箱: sunba@example.com | 入职: 2026-05-22
===============================================

（关闭程序，重新启动 → 数据依然存在！因为已持久化到MySQL数据库）
```

---

## 9.7 本章小结

恭喜你！第九章是本书第一篇（Java基础）和第二篇（数据库与持久化）之间的桥梁。回顾本章的收获：

1. **JDBC架构理解**：Java → JDBC API → DriverManager → 厂商驱动 → 数据库，理解面向接口编程在JDBC中的体现
2. **JDBC六步曲**：注册驱动→获取连接→创建Statement→执行SQL→处理ResultSet→释放资源（try-with-resources倒序关闭）
3. **SQL注入深度理解**：
   - 亲手演示了三种攻击方式（注释绕过、万能密码、删库）
   - 理解了PreparedStatement的防御原理（SQL模板预编译 + 参数分离发送）
   - 知道PreparedStatement的局限性（不能防表名/列名注入，需白名单）
4. **JDBC事务控制**：`setAutoCommit(false)` → 多条SQL → `commit()` 或 `rollback()`
5. **Druid连接池**：initSize/minIdle/maxActive/maxWait核心参数配置
6. **DAO分层模式**：Controller→Service→DAO→DB，每层职责清晰
7. **EMS v2完整项目**：从零实现了JDBC+Druid+PreparedStatement的命令行员工管理系统，数据持久化到MySQL

---

## 思考题

1. 以下代码存在严重安全问题，请指出并给出修正方案：

   ```java
   String name = request.getParameter("name");
   String sql = "SELECT * FROM employee WHERE name = '" + name + "'";
   Statement stmt = conn.createStatement();
   ResultSet rs = stmt.executeQuery(sql);
   ```

2. PreparedStatement的防注入原理是什么？为什么它不能防止表名注入？

3. try-with-resources中声明资源的顺序是 `conn → pstmt → rs`，为什么实际关闭顺序是 `rs → pstmt → conn`？如果不按倒序关闭会有什么问题？

4. Druid连接池的 `maxActive` 和 `maxWait` 分别控制什么？如果 `maxActive=10, maxWait=3000`，当第11个并发请求到来时会发生什么？

5. 在EMS v2的EmployeeDaoImpl中，用户输入 `"' OR '1'='1"` 作为部门名称进行查询，会发生SQL注入吗？为什么？（结合PreparedStatement的防御原理回答）

6. 对比你在第7章实现的EMS v1（内存List存储）和本章的EMS v2（MySQL存储），从数据持久性、并发安全性、代码复杂度三个维度分析两者的优缺点。

---

<details>
<summary>思考题参考答案（点击展开）</summary>

**第1题**：
问题：使用Statement拼接SQL，存在SQL注入漏洞。攻击者输入 `name=' OR '1'='1' -- ` 可查出所有员工数据。

修正方案：
```java
String name = request.getParameter("name");
String sql = "SELECT * FROM employee WHERE name = ?";
PreparedStatement pstmt = conn.prepareStatement(sql);
pstmt.setString(1, name);
ResultSet rs = pstmt.executeQuery();
```

**第2题**：
PreparedStatement的防注入原理：
1. SQL模板（含占位符`?`）先发送给数据库进行**预编译**，数据库解析SQL语法结构并生成执行计划
2. 参数值**单独发送**给数据库，数据库将参数值严格当作"纯数据"处理
3. 参数值中的特殊字符（单引号`'`、分号`;`、注释符`--`）会被**转义**（如`'`转义为`\'`），不会改变已编译的SQL语法结构

不能防表名注入的原因：占位符`?`在设计上只能替代SQL语句中的"值"位置（WHERE条件值、INSERT字段值），不能替代数据库对象的标识符（表名、列名、ORDER BY、GROUP BY等）。语法层面，`FROM ?` 本身就是非法SQL。因此如果必须动态表名，只能用白名单+字符串拼接。

**第3题**：
- Java的try-with-resources机制**保证资源按声明顺序的逆序关闭**（后声明的先关闭）
- 声明顺序是 conn → pstmt → rs（因为要先有conn才能创建pstmt，先有pstmt才能创建rs），关闭则是 rs → pstmt → conn
- 为什么必须倒序：如果先关conn，conn关闭时会连带关闭其下所有pstmt和rs。但如果conn.close()抛出异常，pstmt和rs的close()就不会执行，可能导致资源泄露。倒序关闭确保每个资源单独关闭，异常隔离。

**第4题**：
- **maxActive=10**：连接池中最多同时存在10个活跃连接
- **maxWait=3000**：当池中没有可用连接时，新请求最多等待3000毫秒
- **第11个并发请求到来时**：前10个请求各占1个连接，第11个请求调用`dataSource.getConnection()`会阻塞等待。如果3秒内（maxWait=3000）有连接归还（某个请求处理完close了连接），第11个请求就能获取到；如果3秒后仍无可用连接 → 抛出 `GetConnectionTimeoutException`。

**第5题**：
不会发生SQL注入。用户输入 `"' OR '1'='1"` 被 `pstmt.setString(1, "' OR '1'='1")` 设置后，数据库实际执行的SQL等价于：
```sql
SELECT * FROM employee WHERE department = '\' OR \'1\'=\'1'
```
注意所有单引号都被转义了，数据库将其作为**department字段的值**进行精确匹配。除非数据库里真有一条记录的department列值为 `' OR '1'='1`，否则查不到任何结果。SQL注入被彻底防住了。

**第6题**：

| 维度 | EMS v1（内存List） | EMS v2（JDBC+MySQL） |
|------|-------------------|---------------------|
| **数据持久性** | ❌ 程序退出数据丢失 | ✅ 数据永久保存在磁盘 |
| **并发安全性** | ❌ 多线程同时修改List会出错 | ✅ MySQL锁机制保证并发安全 |
| **多实例共享** | ❌ 两个程序各自独立的数据 | ✅ 共用同一个数据库 |
| **代码复杂度** | ⭐ 简单（约200行） | ⭐⭐⭐ 中等（约500行，需配置连接池/DAO层/SQL） |
| **部署复杂度** | ⭐ 只需JRE | ⭐⭐⭐ 需要MySQL服务器+表初始化 |
| **查询能力** | ❌ 只能遍历List手动过滤 | ✅ SQL查询灵活强大（聚合、排序、JOIN） |

总结：EMS v1适合快速原型和学习基础语法；EMS v2是真实项目的雏形，数据持久化和SQL查询能力是生产级应用的基本要求。后续章节的Spring Boot版本将大幅简化v2中繁琐的JDBC配置。

</details>

---

> **下一篇预告**：恭喜你完成了Java基础和数据库编程的学习！从第10章开始，我们将正式踏入Spring生态的大门——首先学习Spring Framework的核心：IoC容器和依赖注入。你会发现，之前手动new对象、手动管理连接池的"苦力活"，Spring会帮你优雅地解决。
>
> **学习路线回顾**：
> - 第1-7章：Java基础 → 你可以写出功能完整的Java程序
> - 第8-9章：数据库+JDBC → 你的程序可以持久化数据了
> - 第10-20章：Spring全家桶 → 你将学会企业级开发的真功夫
>
> 你已经走完了全栈路线的"地基"部分，接下来的每一章都会让你更接近一个真正的全栈开发者。继续前进！
</parameter>