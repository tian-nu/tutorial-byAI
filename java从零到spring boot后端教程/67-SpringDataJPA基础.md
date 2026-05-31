# 第67章 · Spring Data JPA基础

> **📢 这章是第64-67章Java数据库访问四层递进的终点站——JPA。** 走路（JDBC第64章）→ 穿鞋（连接池第65章）→ 自行车（MyBatis第66章）→ **汽车（JPA本章）**。你定义好Java类，JPA自动建表、自动生成SQL、连级联查询都帮你搞定。这是本书后续所有项目的主力持久层技术。

> "你有两辆奔驰——一辆是MyBatis手动挡（第66章），一辆是JPA自动挡（本章）。MyBatis让你精确控制每一个换挡时机（每条SQL），JPA让你踩油门就走（定义实体就够了）。本书的选择是：主力开自动挡JPA，遇到需要精确控制的路段再切手动挡MyBatis。"

---

## 67.1 JPA是什么

**JPA**（Jakarta Persistence API，原Java Persistence API）是Java官方的持久化规范。它定义了一套接口和注解，Hibernate是它最流行的实现。Spring Data JPA在JPA之上做了进一步封装，提供了极其简洁的数据访问层。

```
你的代码（只需写接口！）
    │
    ▼
Spring Data JPA（提供JpaRepository，自动生成CRUD方法）
    │
    ▼
Hibernate（JPA的实现，ORM引擎）
    │
    ▼
JDBC（底层数据库通信）
```

> 💡 **JPA ≠ Hibernate**。JPA是规范（接口），Hibernate是实现（具体代码）。就像USB是规范，你的U盘是实现。Spring Data JPA = JPA规范 + Hibernate默认实现 + Spring的简化封装。

---

## 67.2 项目配置

### 67.2.1 Maven依赖

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-data-jpa</artifactId>
</dependency>
<dependency>
    <groupId>com.mysql</groupId>
    <artifactId>mysql-connector-j</artifactId>
    <version>8.0.33</version>
</dependency>
```

`spring-boot-starter-data-jpa` 已经包含了Hibernate、HikariCP、Spring Data JPA，不需要单独引入。

### 67.2.2 application.yml

```yaml
spring:
  datasource:
    url: jdbc:mysql://localhost:3306/my_shop?useSSL=false&serverTimezone=Asia/Shanghai
    username: root
    password: your_password_here
    driver-class-name: com.mysql.cj.jdbc.Driver

  jpa:
    hibernate:
      ddl-auto: update      # 自动更新表结构（开发用update，生产用validate）
    show-sql: true          # 打印SQL（开发环境开，生产关）
    properties:
      hibernate:
        format_sql: true    # 格式化输出的SQL
        dialect: org.hibernate.dialect.MySQLDialect
```

`ddl-auto` 的取值：

| 值 | 行为 | 使用场景 |
|----|------|---------|
| `none` | 不做任何DDL操作 | 生产环境推荐 |
| `validate` | 验证实体和表结构是否匹配，不匹配则启动报错 | 生产环境安全选项 |
| `update` | 实体变了自动ALTER TABLE（只增不改不删） | 开发环境 |
| `create` | 每次启动删表重建 | 测试环境 |
| `create-drop` | 启动建表，关闭删表 | 单元测试 |

> 🚨 生产环境严禁使用 `ddl-auto: update`！它只追加不删除，且不会帮你做数据迁移。用 `validate` 或 `none`，表结构的变更通过Flyway/Liquibase等迁移工具管理。

---

## 67.3 实体类：从Java对象到数据库表

### 67.3.1 基础实体

```java
package com.example.entity;

import jakarta.persistence.*;
import java.math.BigDecimal;
import java.time.LocalDateTime;

@Entity                     // 标识这是一个JPA实体
@Table(name = "users")      // 映射到users表（不写则默认类名小写）
public class User {

    @Id                     // 主键
    @GeneratedValue(strategy = GenerationType.IDENTITY)  // 自增策略
    private Long id;

    @Column(name = "username", nullable = false, unique = true, length = 50)
    private String username;

    @Column(nullable = false, length = 100)
    private String email;

    @Column(name = "age")
    private Integer age;

    @Column(precision = 10, scale = 2)
    private BigDecimal balance;

    @Column(name = "created_at", updatable = false)
    private LocalDateTime createdAt;

    @Column(name = "updated_at")
    private LocalDateTime updatedAt;

    // 🚨 必须有无参构造器（JPA要求）
    public User() {}

    // 方便的构造器（业务用，不是JPA要求的）
    public User(String username, String email) {
        this.username = username;
        this.email = email;
    }

    // getter / setter ...
    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }
    public String getUsername() { return username; }
    public void setUsername(String username) { this.username = username; }
    // ... 其余getter/setter省略
}
```

### 67.3.2 核心注解速查

| 注解 | 作用 | 常用属性 |
|------|------|---------|
| `@Entity` | 标识JPA实体 | name（实体名，默认类名） |
| `@Table` | 映射表名 | name, indexes, uniqueConstraints |
| `@Id` | 标识主键 | - |
| `@GeneratedValue` | 主键生成策略 | strategy: IDENTITY/AUTO/SEQUENCE/TABLE/UUID |
| `@Column` | 映射列 | name, nullable, unique, length, precision, scale, columnDefinition |
| `@Enumerated` | 枚举映射 | EnumType.ORDINAL(存序号)/STRING(存字符串，推荐) |
| `@Transient` | 该字段不映射到数据库 | - |
| `@CreatedDate` | 创建时自动填时间（需配合 `@EntityListeners`） | - |
| `@LastModifiedDate` | 更新时自动填时间 | - |

---

## 67.4 JpaRepository：免费CRUD

这是Spring Data JPA最强大的特性——你只需要写一个接口继承 `JpaRepository`，增删改查分页排序全都有了，**不需要写任何实现代码**。

```java
package com.example.repository;

import com.example.entity.User;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface UserRepository extends JpaRepository<User, Long> {
    //                                  ↑ 实体类型  ↑ 主键类型
    // 这里什么都不用写！以下方法全部免费：
}
```

JpaRepository自带的方法：

```java
// 保存（新增或更新）
userRepository.save(user);               // 如果user.id=null则INSERT，否则UPDATE

// 批量保存
userRepository.saveAll(userList);

// 按ID查询
Optional<User> user = userRepository.findById(1L);

// 查询全部
List<User> allUsers = userRepository.findAll();

// 按ID批量查询
List<User> users = userRepository.findAllById(List.of(1L, 2L, 3L));

// 统计
long count = userRepository.count();

// 按ID删除
userRepository.deleteById(1L);

// 删除实体
userRepository.delete(user);

// 判断是否存在
boolean exists = userRepository.existsById(1L);
```

全部是免费的，一行实现代码都不用写。

---

## 67.5 查询方法命名：按规则起名，自动生成SQL

Spring Data JPA能**根据方法名自动生成SQL**。规则是 `findBy + 属性名 + 条件`：

```java
public interface UserRepository extends JpaRepository<User, Long> {

    // 精确查询
    Optional<User> findByUsername(String username);

    // 模糊查询
    List<User> findByUsernameContaining(String keyword);

    // 多条件
    List<User> findByAgeGreaterThanAndEmailContaining(Integer age, String email);

    // OR条件
    List<User> findByUsernameOrEmail(String username, String email);

    // 范围查询
    List<User> findByAgeBetween(Integer minAge, Integer maxAge);

    // IN查询
    List<User> findByAgeIn(List<Integer> ages);

    // 排序
    List<User> findByAgeGreaterThanOrderByCreatedAtDesc(Integer age);

    // 限制结果
    Optional<User> findTopByOrderByCreatedAtDesc();
    List<User> findTop10ByOrderByIdDesc();

    // 判断
    boolean existsByUsername(String username);
}
```

### 命名规则关键词表

| 关键词 | SQL等价 | 示例 |
|--------|---------|------|
| `findBy` / `getBy` / `readBy` / `queryBy` | `SELECT ... WHERE` | `findByUsername` |
| `Containing` | `LIKE %xxx%` | `findByUsernameContaining` |
| `And` | `AND` | `findByAgeAndEmail` |
| `Or` | `OR` | `findByUsernameOrEmail` |
| `Between` | `BETWEEN` | `findByAgeBetween` |
| `LessThan` / `GreaterThan` | `<` / `>` | `findByAgeGreaterThan` |
| `Before` / `After` | `<` / `>` (日期) | `findByCreatedAtAfter` |
| `IsNull` / `IsNotNull` | `IS NULL` / `IS NOT NULL` | `findByEmailIsNull` |
| `Like` | `LIKE` | `findByUsernameLike` |
| `StartingWith` | `LIKE 'xxx%'` | `findByUsernameStartingWith` |
| `In` | `IN (...)` | `findByAgeIn` |
| `OrderBy...Asc/Desc` | `ORDER BY` | `findByAgeOrderByCreatedAtDesc` |
| `True` / `False` | `= TRUE` / `= FALSE` | `findByActiveTrue` |
| `IgnoreCase` | 忽略大小写 | `findByUsernameIgnoreCase` |
| `Top` / `First` | `LIMIT` | `findTop5ByOrderByIdDesc` |

---

## 67.6 @Query：自定义查询

当方法名太长或查询太复杂时，用 `@Query` 直接写JPQL（面向实体的SQL）：

```java
public interface UserRepository extends JpaRepository<User, Long> {

    // JPQL：操作的是Java对象，不是数据库表
    @Query("SELECT u FROM User u WHERE u.email LIKE %:domain%")
    List<User> findByEmailDomain(@Param("domain") String domain);

    // 更新操作需要加 @Modifying
    @Modifying
    @Transactional
    @Query("UPDATE User u SET u.age = :age WHERE u.id = :id")
    int updateAgeById(@Param("id") Long id, @Param("age") Integer age);

    // 原生SQL（nativeQuery=true）
    @Query(value = "SELECT * FROM users WHERE age > ?1 ORDER BY created_at DESC LIMIT ?2",
           nativeQuery = true)
    List<User> findTopByAgeNative(int age, int limit);

    // 统计查询
    @Query("SELECT COUNT(u) FROM User u WHERE u.age > :age")
    long countByAgeGreaterThan(@Param("age") int age);
}
```

> 💡 JPQL和SQL的区别：JPQL操作的是实体类和属性名（`User`、`u.age`），SQL操作的是表和列名（`users`、`age`）。JPQL的好处是你改了表名只需要改实体类上的 `@Table` 注解，不用改所有SQL。

---

## 67.7 关联关系：@OneToMany、@ManyToOne

### 67.7.1 一对多（用户 → 订单）

```java
// User.java —— 一方
@Entity
@Table(name = "users")
public class User {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String username;

    // mappedBy = "user" 表示由另一方（Order）的user字段维护关联
    // cascade = ALL 表示增删改User时级联操作其订单
    // fetch = LAZY 表示默认不加载订单，用到时才查（懒加载）
    @OneToMany(mappedBy = "user", cascade = CascadeType.ALL, fetch = FetchType.LAZY)
    private List<Order> orders = new ArrayList<>();

    // getter/setter ...
}

// Order.java —— 多方
@Entity
@Table(name = "orders")
public class Order {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private BigDecimal amount;

    // 多方持有外键
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "user_id")  // 外键列名
    private User user;

    // getter/setter ...
}
```

### 67.7.2 多对多（学生 ↔ 课程）

```java
// Student.java
@Entity
public class Student {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    private String name;

    @ManyToMany
    @JoinTable(
        name = "student_courses",                           // 中间表名
        joinColumns = @JoinColumn(name = "student_id"),     // 本实体在中间表的外键
        inverseJoinColumns = @JoinColumn(name = "course_id") // 对方实体在中间表的外键
    )
    private Set<Course> courses = new HashSet<>();
}

// Course.java
@Entity
public class Course {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    private String title;

    @ManyToMany(mappedBy = "courses")  // 由Student.courses维护关联
    private Set<Student> students = new HashSet<>();
}
```

### 67.7.3 级联操作

| CascadeType | 含义 |
|-------------|------|
| `ALL` | 所有操作都级联（增删改查） |
| `PERSIST` | 保存时级联 |
| `MERGE` | 更新时级联 |
| `REMOVE` | 删除时级联 |
| `REFRESH` | 刷新时级联 |
| `DETACH` | 脱管时级联 |

### 67.7.4 懒加载陷阱

```java
// ❌ 事务外访问懒加载集合会抛 LazyInitializationException
User user = userRepository.findById(1L).orElseThrow();
List<Order> orders = user.getOrders();  // 🚨 异常！事务已结束

// ✅ 方案一：在事务内访问
@Transactional
public User getUserWithOrders(Long id) {
    User user = userRepository.findById(id).orElseThrow();
    user.getOrders().size();  // 触发懒加载
    return user;
}

// ✅ 方案二：用JOIN FETCH
@Query("SELECT u FROM User u JOIN FETCH u.orders WHERE u.id = :id")
Optional<User> findByIdWithOrders(@Param("id") Long id);
```

---

## 67.8 分页与排序

```java
// 分页查询
Page<User> page = userRepository.findAll(
    PageRequest.of(0, 10, Sort.by(Sort.Direction.DESC, "createdAt"))
);
// Page对象包含：
page.getContent();          // 当前页数据（List<User>）
page.getTotalPages();       // 总页数
page.getTotalElements();    // 总记录数
page.getNumber();           // 当前页码（从0开始）
page.getSize();             // 每页大小
page.hasNext();             // 是否有下一页

// 自定义方法也支持分页
Page<User> findByAgeGreaterThan(int age, Pageable pageable);
```

---

## 67.9 四层递进总结

现在回顾第64-67章的四层关系：

```
┌─────────────────────────────────────────────────────┐
│                     JPA（第67章）                     │
│  你写：接口继承JpaRepository                          │
│  得到：免费CRUD + 方法名生成SQL + 关联映射              │
│  类比：开自动挡汽车，踩油门就走                         │
│  主力：✅ 本书唯一主力持久层                           │
├─────────────────────────────────────────────────────┤
│                   MyBatis（第66章）                   │
│  你写：接口方法 + XML/注解中的SQL                      │
│  得到：精确控制每条SQL + 动态SQL                       │
│  类比：骑自行车，你得蹬，但比走路快                      │
│  定位：复杂SQL、遗留系统、报表                         │
├─────────────────────────────────────────────────────┤
│                连接池（第65章）                        │
│  解决：不用每次新建/销毁连接                           │
│  类比：穿鞋，不赤脚走路                               │
│  底层依赖：JPA和MyBatis都自动集成了连接池               │
├─────────────────────────────────────────────────────┤
│                  JDBC（第64章）                       │
│  你写：所有东西——连接、SQL、参数、遍历结果集、关闭...     │
│  类比：走路，一步一步自己走                             │
│  底层依赖：JPA和MyBatis的底层都是它                     │
└─────────────────────────────────────────────────────┘
```

**本书后续的所有Spring Boot项目，主力使用JPA，需要复杂SQL时切到MyBatis的Mapper。**

---

## 本章小结

| 概念 | 要点 |
|------|------|
| JPA | Java官方持久化规范，Hibernate是最流行的实现 |
| @Entity | 标识JPA实体类，映射数据库表 |
| @Id + @GeneratedValue | 主键+自增策略 |
| JpaRepository | 继承即免费获得所有CRUD方法 |
| 查询方法命名 | findBy + 属性 + 条件，框架自动生成SQL |
| @Query | 自定义JPQL或原生SQL |
| @OneToMany / @ManyToOne | 实体关联映射 |
| fetch = LAZY | 懒加载，用时才查（默认推荐） |
| 级联 | CascadeType.ALL/PERSIST/REMOVE/MERGE |

---

## 自测题

1. **有一个 `Product` 实体，包含 `id`（Long，自增主键）、`name`（String）、`price`（BigDecimal）、`category`（String）字段。写出实体类和对应的Repository接口，包含：按分类查询、价格区间查询、按价格降序取前5个的方法。**

2. **`JpaRepository` 提供了哪些免费方法？你继承它后不需要写哪些SQL？**

3. **JPA中 `fetch = FetchType.LAZY` 什么意思？使用时有什么坑？**

<details>
<summary>参考答案（做完再看）</summary>

1. 实体类略（参考67.3.1的模式）。Repository：
```java
public interface ProductRepository extends JpaRepository<Product, Long> {
    List<Product> findByCategory(String category);
    List<Product> findByPriceBetween(BigDecimal min, BigDecimal max);
    List<Product> findTop5ByOrderByPriceDesc();
}
```

2. JpaRepository免费提供：save(增+改)、saveAll(批量保存)、findById、findAll、findAllById、count、deleteById、delete、deleteAll、existsById。继承后不需要写INSERT、简单SELECT、UPDATE、DELETE的SQL，以及简单的数量统计和存在性判断。

3. LAZY（懒加载）表示关联数据不立即加载，只有当你真正访问它时才去数据库查询。这能避免加载不必要的数据，提高性能。坑：如果代码在事务外访问懒加载的集合（如controller返回给前端时），会抛出 `LazyInitializationException`。解决方案：1) 在事务内访问；2) 用 `JOIN FETCH` 一次性加载；3) 用 `@EntityGraph` 指定加载策略。
</details>