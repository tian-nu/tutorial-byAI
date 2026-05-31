# 81-数据访问SpringDataJPA深入

> 💡 你有一台智能冰箱。以前你要自己记住每样食物放哪层、什么日期买的、还剩多少。有了智能冰箱，你只需对着屏幕说"苹果还有几个"，冰箱自动回答。JPA 就是你数据库的"智能冰箱"——你只需要声明"我要查什么"，JPA 自动生成 SQL、执行、把结果映射成对象。本章是第67章 JPA 基础的深化，聚焦查询方法论。

---

## 本章目标
- 精通 Spring Data JPA 的查询方法命名规则
- 使用 `@Query` 编写自定义 JPQL / 原生 SQL
- 掌握分页 `Pageable` 和排序 `Sort`
- 使用 JPA 审计自动记录创建时间和修改时间
- 理解懒加载与 N+1 问题

---

## 81.1 查询方法命名规则——方法名即 SQL

| 关键字 | 方法名示例 | 生成的 SQL 条件 |
|--------|------------|-----------------|
| `findBy` | `findByUsername` | `WHERE username = ?` |
| `Containing` | `findByUsernameContaining` | `WHERE username LIKE %?%` |
| `StartingWith` | `findByUsernameStartingWith` | `WHERE username LIKE ?%` |
| `Between` | `findByAgeBetween` | `WHERE age BETWEEN ? AND ?` |
| `GreaterThan` | `findByAgeGreaterThan` | `WHERE age > ?` |
| `Before` / `After` | `findByCreatedAtAfter` | `WHERE created_at > ?` |
| `IsNull` | `findByEmailIsNull` | `WHERE email IS NULL` |
| `In` | `findByAgeIn` | `WHERE age IN (?,?,?)` |
| `And` / `Or` | `findByUsernameAndEmail` | `WHERE username=? AND email=?` |
| `OrderBy` | `findByAgeOrderByCreatedAtDesc` | `WHERE age=? ORDER BY created_at DESC` |
| `IgnoreCase` | `findByUsernameIgnoreCase` | `WHERE UPPER(username) = UPPER(?)` |
| `Top` / `First` | `findTop5ByOrderByAgeDesc` | `LIMIT 5` |

### 实例

```java
public interface UserRepository extends JpaRepository<User, Long> {

    Optional<User> findByUsername(String username);

    List<User> findByUsernameContaining(String keyword);

    List<User> findByAgeBetweenAndEmailEndingWith(
            Integer minAge, Integer maxAge, String emailSuffix);

    List<User> findTop10ByOrderByCreatedAtDesc();

    long countByAgeGreaterThan(Integer age);

    boolean existsByEmail(String email);
}
```

> 🤔 想多一点：方法名超过 3 个条件时改用 `@Query`。`findByAgeBetweenAndEmailEndingWithAndUsernameContainingOrderByCreatedAtDesc` 是反模式。

---

## 81.2 @Query——当方法名不够用时

### JPQL（面向对象查询）

```java
public interface UserRepository extends JpaRepository<User, Long> {

    @Query("SELECT u FROM User u WHERE u.email LIKE %:domain%")
    List<User> findByEmailDomain(@Param("domain") String domain);

    @Query("SELECT u FROM User u WHERE u.age > :age ORDER BY u.createdAt DESC")
    List<User> findAdultsByAge(@Param("age") Integer age);

    @Query("UPDATE User u SET u.age = :age WHERE u.id = :id")
    @Modifying
    @Transactional
    int updateAgeById(@Param("id") Long id, @Param("age") Integer age);
}
```

### 原生 SQL

```java
@Query(value = "SELECT * FROM users WHERE age > :age",
       nativeQuery = true)
List<User> findByAgeNative(@Param("age") Integer age);
```

---

## 81.3 分页与排序

```java
public interface UserRepository extends JpaRepository<User, Long> {
    Page<User> findByAgeGreaterThan(Integer age, Pageable pageable);
}
```

Controller：

```java
@GetMapping
public Result<Page<User>> list(
        @RequestParam(defaultValue = "0") int page,
        @RequestParam(defaultValue = "10") int size,
        @RequestParam(defaultValue = "createdAt") String sortBy,
        @RequestParam(defaultValue = "desc") String direction) {

    Sort sort = direction.equalsIgnoreCase("asc")
            ? Sort.by(sortBy).ascending()
            : Sort.by(sortBy).descending();

    Pageable pageable = PageRequest.of(page, size, sort);
    Page<User> userPage = userRepository.findAll(pageable);

    return Result.success(userPage);
}
```

Page 返回结构：

```json
{
    "content": [{...}, {...}],
    "totalElements": 100,
    "totalPages": 10,
    "number": 0,
    "size": 10
}
```

---

## 81.4 JPA 审计——自动记录创建时间和修改时间

```java
@Data
@Entity
@EntityListeners(AuditingEntityListener.class)
public class User {

    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @CreatedDate
    @Column(updatable = false)
    private LocalDateTime createdAt;

    @LastModifiedDate
    private LocalDateTime updatedAt;
}
```

启动类上加 `@EnableJpaAuditing`：

```java
@SpringBootApplication
@EnableJpaAuditing
public class DemoApplication {
    public static void main(String[] args) {
        SpringApplication.run(DemoApplication.class, args);
    }
}
```

---

## 81.5 懒加载与 N+1 问题

```java
@Entity
public class Order {
    @ManyToOne(fetch = FetchType.LAZY)
    private User user;
}
```

遍历订单时访问 user 会额外发 SQL：

```java
List<Order> orders = orderRepository.findAll();  // 1 条 SQL
for (Order order : orders) {
    System.out.println(order.getUser().getUsername());  // 每个订单 +1 条 SQL
}
// N+1 问题：总共 N+1 条 SQL
```

### 解决方案：JOIN FETCH

```java
@Query("SELECT o FROM Order o JOIN FETCH o.user")
List<Order> findAllWithUser();
```

一条 SQL 同时查出订单和用户数据。

---

## 81.6 小结

| 知识点 | 核心内容 |
|--------|----------|
| 查询方法命名 | findBy / Like / Between / And / Or / OrderBy 等 |
| @Query | 自定义 JPQL 或原生 SQL |
| @Modifying | UPDATE / DELETE 必须加 |
| Page / Pageable | 分页查询，返回 totalElements、totalPages |
| @CreatedDate / @LastModifiedDate | 审计自动填充时间 |
| N+1 问题 | 用 JOIN FETCH 解决 |

---

## 81.7 自测题

**1. `findTop5ByAgeBetweenOrderByCreatedAtDesc` 的含义是什么？**

**2. @Query 的 JPQL 和原生 SQL 的本质区别是什么？**

**3. 什么是 N+1 问题？如何解决？**

---

**答案提示**：1→查询年龄在范围内前5条，按创建时间降序。2→JPQL 操作实体和属性名；原生 SQL 操作表和列名。3→查询主表1条SQL + 每条记录关联查询N条SQL；解决：JOIN FETCH。下一章——事务管理。