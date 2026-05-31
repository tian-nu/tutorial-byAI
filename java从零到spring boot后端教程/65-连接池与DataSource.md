# 第65章 · 连接池与DataSource

> **📢 第64章用DriverManager每次新建连接太浪费了。** 建立一条数据库连接需要TCP三次握手、MySQL认证、分配线程——至少30-100ms。高并发下每秒几百个请求，光建立连接就耗掉几秒钟。连接池就是预先把连接建好放池子里，用的时候借一个，用完还回去。就像共享单车——你不用自己造一辆车，路边扫一辆就骑走。

---

## 65.1 为什么需要连接池

### 没有连接池（DriverManager方式）

```
请求1 → 建立连接(50ms) → 执行SQL(10ms) → 关闭连接(5ms) → 总耗时 65ms
请求2 → 建立连接(50ms) → 执行SQL(10ms) → 关闭连接(5ms) → 总耗时 65ms
请求3 → 建立连接(50ms) → 执行SQL(10ms) → 关闭连接(5ms) → 总耗时 65ms
```

执行SQL只花了10ms，建立和销毁连接却花了55ms——**85%的时间浪费在连接管理上**。

### 有连接池

```
启动时：预先创建10个连接放入池中
请求1 → 从池中借连接(0.1ms) → 执行SQL(10ms) → 归还连接(0.1ms) → 总耗时 10.2ms
请求2 → 从池中借连接(0.1ms) → 执行SQL(10ms) → 归还连接(0.1ms) → 总耗时 10.2ms
请求3 → 从池中借连接(0.1ms) → 执行SQL(10ms) → 归还连接(0.1ms) → 总耗时 10.2ms
```

性能提升约**6倍**。

---

## 65.2 连接池的工作原理

```
                    ┌──────────────────┐
                    │   连接池(Pool)     │
                    │                  │
应用请求连接 ──────→ │  [conn1] ←空闲    │──────→ 返回可用连接
                    │  [conn2] ←空闲    │
                    │  [conn3] ←占用    │
                    │  [conn4] ←占用    │
                    │  [conn5] ←空闲    │
                    │  ...             │
                    └──────────────────┘
```

基本流程：
1. **启动初始化**：池启动时创建 `minimumIdle` 个连接
2. **借出（borrow）**：有请求时，从空闲连接队列取出一个，标记为占用
3. **归还（return）**：请求处理完，连接不关闭，重新放入空闲队列
4. **扩容**：所有连接都被占用且未到 `maximumPoolSize`，创建新连接
5. **缩容**：空闲连接超过 `minimumIdle` 且闲置超过 `idleTimeout`，关闭多余连接
6. **验活**：借出前发送一条测试SQL（如 `SELECT 1`）确认连接仍然有效

---

## 65.3 DataSource接口

JDBC定义了 `javax.sql.DataSource` 接口，它是连接池的标准抽象：

```java
public interface DataSource {
    Connection getConnection() throws SQLException;
    Connection getConnection(String username, String password) throws SQLException;
}
```

任何连接池（HikariCP、Druid、Tomcat JDBC Pool、C3P0）都实现这个接口。你的代码只依赖DataSource接口，换连接池只需换依赖和配置，不用改代码。

```java
// 你的代码只依赖 DataSource 接口
DataSource dataSource = ...; // 由Spring注入具体实现
try (Connection conn = dataSource.getConnection()) {
    // 执行SQL
}
```

---

## 65.4 HikariCP：Spring Boot默认连接池

Spring Boot 2.x+ 默认使用 **HikariCP**（日语"光"，读作hi-ka-ri），是目前Java生态中**最快**的连接池。

### 65.4.1 Maven依赖

```xml
<dependency>
    <groupId>com.zaxxer</groupId>
    <artifactId>HikariCP</artifactId>
    <version>5.0.1</version>
</dependency>
```

如果用的是 `spring-boot-starter-data-jpa` 或 `spring-boot-starter-jdbc`，HikariCP已经自动包含在内，不需要额外添加。

### 65.4.2 Spring Boot中配置

在 `application.yml` 中：

```yaml
spring:
  datasource:
    url: jdbc:mysql://localhost:3306/my_shop?useSSL=false&serverTimezone=Asia/Shanghai&characterEncoding=utf8
    username: root
    password: your_password_here
    driver-class-name: com.mysql.cj.jdbc.Driver
    hikari:
      minimum-idle: 5              # 最小空闲连接数
      maximum-pool-size: 20        # 最大连接数
      idle-timeout: 300000         # 空闲超时时间（毫秒），默认10分钟
      max-lifetime: 1800000        # 连接最大存活时间（毫秒），默认30分钟
      connection-timeout: 30000    # 等待连接的超时时间（毫秒），默认30秒
      connection-test-query: SELECT 1  # 连接测试SQL
```

在 `application.properties` 中等价配置：

```properties
spring.datasource.url=jdbc:mysql://localhost:3306/my_shop?useSSL=false&serverTimezone=Asia/Shanghai
spring.datasource.username=root
spring.datasource.password=your_password_here
spring.datasource.driver-class-name=com.mysql.cj.jdbc.Driver
spring.datasource.hikari.minimum-idle=5
spring.datasource.hikari.maximum-pool-size=20
spring.datasource.hikari.idle-timeout=300000
spring.datasource.hikari.max-lifetime=1800000
spring.datasource.hikari.connection-timeout=30000
```

### 65.4.3 参数详解

| 参数 | 默认值 | 说明 | 调优建议 |
|------|--------|------|---------|
| `minimum-idle` | 同maximum-pool-size | 池中保持的最小空闲连接数 | 建议等于maximum-pool-size，避免突发流量时的扩容延迟 |
| `maximum-pool-size` | 10 | 池中最大连接数（包含空闲+占用） | 公式：`((CPU核心数 * 2) + 硬盘数)`，通常20~50 |
| `idle-timeout` | 600000（10分钟） | 空闲连接超过此时间被回收 | 保持默认 |
| `max-lifetime` | 1800000（30分钟） | 连接的最大存活时间 | 应比数据库的 `wait_timeout` 小几分钟 |
| `connection-timeout` | 30000（30秒） | 等待可用连接的最大时间 | 超过抛SQLException |
| `connection-test-query` | 无 | 验证连接有效性的SQL | MySQL用 `SELECT 1`，执行极快 |
| `pool-name` | 自动生成 | 连接池名称 | 设置一个有意义的名字，便于日志排查 |

> ⚠️ `max-lifetime` 必须比MySQL的 `wait_timeout` 少。如果MySQL先断开了闲置连接而HikariCP还不知道，取出来用就会报错。MySQL默认 `wait_timeout = 28800`（8小时），所以默认30分钟的max-lifetime是安全的。

### 65.4.4 连接数计算公式

```
最佳连接池大小 = ((CPU核心数 * 2) + 有效硬盘数)
```

例如：4核CPU + 1个SSD = (4*2)+1 = 9个连接。

这只是起点，实际应根据压测结果调整。如果 `maximum-pool-size` 设得太大（如1000），每个连接在MySQL端都是一个线程，线程上下文切换反而拖垮性能。

---

## 65.5 纯Java代码创建HikariCP（不使用Spring）

在非Spring环境中直接使用HikariCP：

```java
import com.zaxxer.hikari.HikariConfig;
import com.zaxxer.hikari.HikariDataSource;
import javax.sql.DataSource;
import java.sql.*;

public class HikariDemo {
    public static void main(String[] args) {
        HikariConfig config = new HikariConfig();
        config.setJdbcUrl("jdbc:mysql://localhost:3306/my_shop?useSSL=false&serverTimezone=Asia/Shanghai");
        config.setUsername("root");
        config.setPassword("your_password_here");
        config.setMinimumIdle(5);
        config.setMaximumPoolSize(20);
        config.setConnectionTestQuery("SELECT 1");

        DataSource dataSource = new HikariDataSource(config);

        // 使用方式和DriverManager完全一样，只是getConnection()从池中取
        try (Connection conn = dataSource.getConnection();
             PreparedStatement pstmt = conn.prepareStatement("SELECT id, username FROM users WHERE age > ?")) {

            pstmt.setInt(1, 18);

            try (ResultSet rs = pstmt.executeQuery()) {
                while (rs.next()) {
                    System.out.println(rs.getString("username"));
                }
            }

        } catch (SQLException e) {
            e.printStackTrace();
        }
    }
}
```

---

## 65.6 常见连接池对比

| 特性 | HikariCP | Druid | Tomcat JDBC Pool | DBCP2 |
|------|----------|-------|------------------|-------|
| 性能 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |
| 监控 | 基础 | 强大（内置SQL监控、Web界面） | 基础 | 基础 |
| 扩展性 | 良好 | 强大（过滤器链） | 一般 | 一般 |
| Spring Boot默认 | ✅ | ❌ | ❌ | ❌ |
| 生产推荐 | ✅ 高性能场景 | ✅ 需要监控的场景 | 不推荐 | 不推荐 |

> 💡 HikariCP适合绝大多数场景。Druid（阿里巴巴开源）提供强大的SQL监控和防火墙功能，如果团队需要可视化SQL执行统计，可以切换到Druid。

---

## 65.7 连接池常见问题

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| `Connection is not available, request timed out after 30000ms` | 所有连接被占用且达到上限 | 增大 `maximum-pool-size` 或检查是否有连接泄漏 |
| 连接池耗尽 | 有代码拿了连接没关闭（连接泄漏） | 确保所有连接在finally或try-with-resources中关闭 |
| `Communications link failure` | 连接被MySQL服务端断开 | 确保 `max-lifetime` < MySQL的 `wait_timeout` |
| 新请求等了很久才拿到连接 | 连接都在执行慢SQL | 优化慢SQL或增大连接池 |

### 检查连接泄漏

连接泄漏的典型症状：连接池连接数持续上升直到达到上限，然后所有请求超时。

```java
// ❌ 连接泄漏！conn在try块中没有关闭
public void leak() throws SQLException {
    Connection conn = dataSource.getConnection();
    PreparedStatement pstmt = conn.prepareStatement("SELECT ...");
    // 忘了关conn！这个连接永远不会归还池中
}

// ✅ 正确写法
public void noLeak() throws SQLException {
    try (Connection conn = dataSource.getConnection();
         PreparedStatement pstmt = conn.prepareStatement("SELECT ...")) {
        // try-with-resources 自动关闭
    }
}
```

---

## 本章小结

| 概念 | 要点 |
|------|------|
| 连接池 | 预先创建并管理数据库连接，避免频繁创建/销毁 |
| DataSource | JDBC定义的连接池标准接口，所有连接池都实现它 |
| HikariCP | Spring Boot默认连接池，Java生态最快 |
| minimum-idle | 最小空闲连接数，建议等于maximum-pool-size |
| maximum-pool-size | 最大连接数，公式：((CPU核数*2)+硬盘数) |
| max-lifetime | 连接最大存活时间，必须<MySQL的wait_timeout |
| 连接泄漏 | 拿了连接不归还，try-with-resources可彻底避免 |

---

## 自测题

1. **没有连接池时，为什么频繁创建和关闭连接会很慢？连接池解决了什么问题？**

2. **HikariCP的 `maximum-pool-size` 设为500有什么问题？合理的值应该怎么计算？**

3. **生产环境中连接池频繁报 `Connection is not available`，可能是什么原因？怎么排查？**

<details>
<summary>参考答案（做完再看）</summary>

1. 创建数据库连接需要TCP三次握手、MySQL认证和授权、分配线程资源，耗时30-100ms。频繁创建和关闭连接，这些开销比执行SQL本身还大。连接池在启动时预创建一批连接放着，请求来了直接取，用完归还——省去了创建/销毁的开销。同时连接池还管理连接的生命周期（验证有效性、回收长时间空闲的连接）。

2. 设500连接是过度的。每个数据库连接在MySQL端对应一个线程，500个线程的上下文切换开销非常大，反而拖慢整体性能。而且数据库能同时处理的有效并发有限，多余的连接只是在排队。合理值通常是 `((CPU核数*2) + 有效硬盘数)`，具体值需要根据实际压测确定。一般中小应用10-30即可。

3. 两个可能原因：1) 连接泄漏——代码中拿了连接没有在finally中关闭。排查：检查代码中所有 `getConnection()` 是否都有关闭逻辑，或使用try-with-resources。可以通过HikariCP的日志看到活跃连接数是否持续增长。2) 连接池太小——并发量超过了 `maximum-pool-size`。排查：监控连接池的活跃连接数和等待队列，适当调大连接池。如果调大后还是不够，说明数据库本身是瓶颈，需要SQL优化或读写分离。
</details>