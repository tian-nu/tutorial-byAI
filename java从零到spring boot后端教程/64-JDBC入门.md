# 第64章 · JDBC入门

> **📢 本章学的是Java连接数据库最底层的方式。** 就像学开车要先了解发动机怎么工作一样——后面第66章MyBatis和第67章JPA都是对JDBC的封装。走路（JDBC）→ 自行车（MyBatis）→ 汽车（JPA）。三层都要学，但主力是JPA。你不需要用JDBC写生产代码，但你必须理解它，因为MyBatis和JPA的底层都是它。

> "从这一章开始，我们用Java代码操作数据库。前10章你在MySQL命令行里写SQL，现在你要让Java程序替你写SQL、发SQL、收结果。JDBC就是Java和数据库之间的翻译官——你用Java说一句'查所有用户'，JDBC翻译成MySQL能懂的SQL发过去，再把返回的表格翻译成Java对象还给你。"

---

## 64.1 JDBC是什么

**JDBC**（Java Database Connectivity）是Java标准库中操作数据库的API。它定义了一组接口（`java.sql` 和 `javax.sql` 包），数据库厂商实现这些接口，提供驱动。

```
你的Java代码
    │
    ▼
JDBC接口（java.sql.Connection, Statement, ResultSet等）
    │
    ▼
MySQL驱动（mysql-connector-java.jar，实现JDBC接口）
    │
    ▼
MySQL数据库
```

JDBC不需要额外安装——它是JDK的一部分。你只需要引入对应数据库的驱动jar包。

---

## 64.2 第一个JDBC程序

### 64.2.1 添加依赖

Maven项目在 `pom.xml` 中添加：

```xml
<dependency>
    <groupId>com.mysql</groupId>
    <artifactId>mysql-connector-j</artifactId>
    <version>8.0.33</version>
</dependency>
```

### 64.2.2 六步操作法

```java
import java.sql.*;

public class JdbcDemo {
    public static void main(String[] args) {
        // 1. 数据库连接信息
        String url = "jdbc:mysql://localhost:3306/my_shop?useSSL=false&serverTimezone=Asia/Shanghai";
        String username = "root";
        String password = "your_password_here";

        // 2. 声明资源（finally中关闭用）
        Connection conn = null;
        Statement stmt = null;
        ResultSet rs = null;

        try {
            // 3. 获取连接
            conn = DriverManager.getConnection(url, username, password);

            // 4. 创建Statement
            stmt = conn.createStatement();

            // 5. 执行SQL并获取结果
            String sql = "SELECT id, username, email, age FROM users";
            rs = stmt.executeQuery(sql);

            // 6. 处理结果集
            while (rs.next()) {
                int id = rs.getInt("id");
                String name = rs.getString("username");
                String email = rs.getString("email");
                int age = rs.getInt("age");
                System.out.printf("ID: %d, Name: %s, Email: %s, Age: %d%n",
                        id, name, email, age);
            }

        } catch (SQLException e) {
            e.printStackTrace();
        } finally {
            // 7. 释放资源（顺序：倒着关）
            try { if (rs != null) rs.close(); } catch (SQLException e) { e.printStackTrace(); }
            try { if (stmt != null) stmt.close(); } catch (SQLException e) { e.printStackTrace(); }
            try { if (conn != null) conn.close(); } catch (SQLException e) { e.printStackTrace(); }
        }
    }
}
```

### 64.2.3 URL格式详解

```
jdbc:mysql://[主机]:[端口]/[数据库名]?参数1=值1&参数2=值2
```

| 参数 | 推荐值 | 说明 |
|------|--------|------|
| `useSSL` | `false`（开发环境） | 是否使用SSL连接 |
| `serverTimezone` | `Asia/Shanghai` | 服务器时区 |
| `characterEncoding` | `utf8` | 字符编码 |
| `useUnicode` | `true` | 使用Unicode |

完整URL示例：
```
jdbc:mysql://localhost:3306/my_shop?useSSL=false&serverTimezone=Asia/Shanghai&characterEncoding=utf8&useUnicode=true
```

---

## 64.3 DriverManager → Connection → Statement → ResultSet

这是JDBC的四大核心接口，一条流水线：

```
DriverManager ──→ Connection ──→ Statement ──→ ResultSet
 (创建连接)        (一条连接)     (发送SQL)     (接收结果)
```

### Connection（连接）

```java
Connection conn = DriverManager.getConnection(url, username, password);
```

Connection代表一条到数据库的TCP连接。连接很昂贵——建立连接需要TCP三次握手、MySQL认证、分配线程。这就是为什么第65章要讲连接池。

### Statement（语句）

```java
Statement stmt = conn.createStatement();
ResultSet rs = stmt.executeQuery("SELECT ...");       // 查询
int rows = stmt.executeUpdate("INSERT/UPDATE/DELETE"); // 增删改
boolean isResultSet = stmt.execute("SQL");             // 任意SQL
```

### ResultSet（结果集）

```java
while (rs.next()) {
    String name = rs.getString("username");   // 按列名取
    int age = rs.getInt(3);                   // 按列序号取（从1开始）
}
```

ResultSet就像一个在数据行上移动的游标，初始位置在**第一行之前**，每次 `next()` 移动到下一行，没数据了返回false。

---

## 64.4 SQL注入演示（本章重点）

### 64.4.1 什么是SQL注入

假设有一个登录功能：

```java
// ❌ 极危险的写法
public boolean login(String username, String password) {
    String sql = "SELECT * FROM users WHERE username = '"
               + username + "' AND password = '" + password + "'";
    ResultSet rs = stmt.executeQuery(sql);
    return rs.next(); // 有结果=登录成功
}
```

正常调用：
```java
login("zhangsan", "123456");
// SQL: SELECT * FROM users WHERE username = 'zhangsan' AND password = '123456'
// ✅ 正常
```

恶意调用：
```java
login("admin' -- ", "anything");
// 拼接后的SQL：
// SELECT * FROM users WHERE username = 'admin' -- ' AND password = 'anything'
//                                                ↑ -- 是SQL注释符，后面的都被注释掉了！
// 实际执行：SELECT * FROM users WHERE username = 'admin'
// 🚨 不需要密码就能以admin身份登录！
```

更可怕的：
```java
login("'; DROP TABLE users; -- ", "anything");
// 拼接后的SQL：
// SELECT * FROM users WHERE username = ''; DROP TABLE users; -- ' AND password = 'anything'
// 🚨 整张users表被删除！
```

### 64.4.2 PreparedStatement：防SQL注入

```java
// ✅ 安全的写法
public boolean login(String username, String password) {
    String sql = "SELECT * FROM users WHERE username = ? AND password = ?";
    PreparedStatement pstmt = conn.prepareStatement(sql);
    pstmt.setString(1, username);  // 第1个?填username
    pstmt.setString(2, password);  // 第2个?填password
    ResultSet rs = pstmt.executeQuery();
    return rs.next();
}
```

即使传入 `"admin' -- "`，PreparedStatement也会把它当做**普通的字符串值**处理，对特殊字符（如 `'`）进行转义，不会让它们破坏SQL结构。

**完整对比**：

| | Statement | PreparedStatement |
|--|-----------|-------------------|
| SQL拼接方式 | 字符串拼接 | `?` 占位符 |
| SQL注入风险 | 🚨 高危 | ✅ 安全 |
| 预编译 | 每次发送完整SQL | 编译一次，复用执行计划 |
| 性能 | 差 | 好（批量操作时尤其明显） |
| 代码可读性 | 差 | 好 |

> 🚨 **铁律：永远不要用Statement拼接用户输入来构造SQL。永远用PreparedStatement。** 这是写进每条coding guideline的底线规则，违反它意味着安全漏洞。

---

## 64.5 PreparedStatement的增删改查

```java
// ========== 查询 ==========
String sql = "SELECT id, username, email FROM users WHERE age > ?";
PreparedStatement pstmt = conn.prepareStatement(sql);
pstmt.setInt(1, 18);
ResultSet rs = pstmt.executeQuery();
while (rs.next()) {
    System.out.println(rs.getString("username"));
}

// ========== 插入 ==========
String insertSql = "INSERT INTO users (username, password, email, age) VALUES (?, ?, ?, ?)";
PreparedStatement insertStmt = conn.prepareStatement(insertSql);
insertStmt.setString(1, "newuser");
insertStmt.setString(2, "hashed_password");
insertStmt.setString(3, "newuser@example.com");
insertStmt.setInt(4, 22);
int rowsInserted = insertStmt.executeUpdate();
System.out.println("插入了 " + rowsInserted + " 行");

// ========== 更新 ==========
String updateSql = "UPDATE users SET age = ? WHERE id = ?";
PreparedStatement updateStmt = conn.prepareStatement(updateSql);
updateStmt.setInt(1, 30);
updateStmt.setInt(2, 1);
int rowsUpdated = updateStmt.executeUpdate();

// ========== 删除 ==========
String deleteSql = "DELETE FROM users WHERE id = ?";
PreparedStatement deleteStmt = conn.prepareStatement(deleteSql);
deleteStmt.setInt(1, 5);
int rowsDeleted = deleteStmt.executeUpdate();
```

### setXxx方法速查

| 方法 | SQL类型 |
|------|---------|
| `setInt(index, value)` | INT |
| `setLong(index, value)` | BIGINT |
| `setString(index, value)` | VARCHAR/CHAR/TEXT |
| `setDouble(index, value)` | DOUBLE |
| `setBigDecimal(index, value)` | DECIMAL |
| `setDate(index, value)` | DATE |
| `setTimestamp(index, value)` | DATETIME/TIMESTAMP |
| `setNull(index, Types.INTEGER)` | NULL |
| `setBoolean(index, value)` | TINYINT(1) |

---

## 64.6 try-with-resources 简化资源管理

Java 7+的try-with-resources可以自动关闭资源，不用写臃肿的finally块：

```java
String sql = "SELECT id, username, email FROM users WHERE age > ?";

try (Connection conn = DriverManager.getConnection(url, username, password);
     PreparedStatement pstmt = conn.prepareStatement(sql)) {

    pstmt.setInt(1, 18);

    try (ResultSet rs = pstmt.executeQuery()) {
        while (rs.next()) {
            System.out.println(rs.getString("username"));
        }
    }

} catch (SQLException e) {
    e.printStackTrace();
}
// conn, pstmt, rs 都会自动关闭，不用手动写close()
```

> `try()` 括号内的对象必须实现 `AutoCloseable` 接口。Connection、PreparedStatement、ResultSet都实现了该接口。

---

## 64.7 事务控制

```java
Connection conn = DriverManager.getConnection(url, username, password);
try {
    conn.setAutoCommit(false);  // 关闭自动提交

    PreparedStatement pstmt1 = conn.prepareStatement(
        "UPDATE accounts SET balance = balance - 500 WHERE id = 1");
    pstmt1.executeUpdate();

    PreparedStatement pstmt2 = conn.prepareStatement(
        "UPDATE accounts SET balance = balance + 500 WHERE id = 2");
    pstmt2.executeUpdate();

    conn.commit();  // 提交事务
    System.out.println("转账成功");

} catch (SQLException e) {
    conn.rollback();  // 回滚
    System.out.println("转账失败，已回滚");
    e.printStackTrace();
} finally {
    conn.setAutoCommit(true);  // 恢复自动提交
    conn.close();
}
```

---

## 64.8 JDBC的繁琐——引出MyBatis和JPA

看完上面的所有代码，你可能会想——"查一条用户要写30行代码？"是的，这就是JDBC的缺点：

- 样板代码多（打开连接→创建Statement→执行→遍历ResultSet→关闭）
- SQL和Java代码混在一起
- 手动处理类型转换（`rs.getInt()`、`rs.getString()`）
- 手动管理资源（try-catch-finally地狱）

**接下来的三章就是解决这些问题的：**

```
第64章  JDBC        ← 走路：一步一步，每一步都要自己走
第65章  连接池       ← 穿鞋：不用每次出门都找鞋（不用每次新建连接）
第66章  MyBatis     ← 自行车：比走路快，但还得自己蹬（写SQL）
第67章  JPA         ← 汽车：踩油门就走，不用管发动机（自动生成SQL）
```

---

## 本章小结

| 概念 | 要点 |
|------|------|
| JDBC | Java标准库中操作数据库的API，定义了Connection/Statement/ResultSet等接口 |
| 六步操作 | 加载驱动→获取连接→创建Statement→执行SQL→处理ResultSet→关闭资源 |
| SQL注入 | 恶意拼接SQL字符串的攻击方式，可以用PreparedStatement彻底防御 |
| PreparedStatement | 预编译SQL，用`?`占位符，防注入+性能好 |
| try-with-resources | 自动关闭实现了AutoCloseable的资源 |
| JDBC定位 | 最底层，是MyBatis和JPA的基础 |

---

## 自测题

1. **对比 Statement 和 PreparedStatement，写出两者的核心区别（至少三点）。**

2. **以下代码有什么安全问题？如何修复？**
   ```java
   String name = request.getParameter("name");
   String sql = "SELECT * FROM users WHERE username = '" + name + "'";
   ResultSet rs = stmt.executeQuery(sql);
   ```

3. **JDBC操作数据库的六个步骤是什么？**

<details>
<summary>参考答案（做完再看）</summary>

1. 1) Statement用字符串拼接构造SQL，存在SQL注入风险；PreparedStatement用`?`占位符，安全。2) Statement每次发送完整SQL到数据库；PreparedStatement预编译一次，可重复执行，性能更好。3) Statement的SQL和参数混在一起，代码可读性差；PreparedStatement的SQL结构清晰，参数用setXxx()方法设置。

2. 严重的安全问题：SQL注入。攻击者可以通过name参数注入恶意SQL。修复：使用PreparedStatement：
```java
String name = request.getParameter("name");
String sql = "SELECT * FROM users WHERE username = ?";
PreparedStatement pstmt = conn.prepareStatement(sql);
pstmt.setString(1, name);
ResultSet rs = pstmt.executeQuery();
```

3. 1) 加载数据库驱动（MySQL 8.0+自动加载，可省略）；2) 通过DriverManager获取Connection连接；3) 创建Statement或PreparedStatement；4) 执行SQL（executeQuery查询/executeUpdate增删改）；5) 处理ResultSet结果集；6) 关闭资源（ResultSet → Statement → Connection，倒序关闭）。
</details>