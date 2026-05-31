# 90-RBAC权限控制

> 💡 一家公司有 CEO、部门经理、普通员工、实习生。CEO 能进所有办公室，实习生只能进自己的工位。公司不是给每个人单独配钥匙，而是定义角色——"经理钥匙"能开经理办公室，"员工钥匙"能开大办公区。RBAC（基于角色的访问控制）就是这种"不给人配权限，给角色配权限"的管理方式。

---

## 本章目标
- 理解 RBAC 的核心概念：用户、角色、权限
- 设计 RBAC 五张数据库表
- 在 Spring Security 中实现动态权限校验
- 区分角色（Role）和权限（Permission）的粒度差异

---

## 90.1 为什么需要 RBAC？

想象一个后台管理系统，有 1000 个用户，100 个功能点。如果不使用角色：

- 每新增一个用户，管理员要从 100 个功能点里勾选他该有的权限
- 公司新来一批实习生，管理员要给 30 个人每人勾一遍"只能看、不能改"
- 一个人升职了，管理员要逐项调整他的权限

有了 RBAC：

1. 定义角色：`ADMIN`、`EDITOR`、`VIEWER`
2. 给角色配权限：
   - `VIEWER` → 只能读文章
   - `EDITOR` → 读写文章
   - `ADMIN` → 读写文章 + 管理用户
3. 给用户分配角色：张三 = `EDITOR`

新人入职 → 赋一个角色，搞定。

---

## 90.2 RBAC 五张核心表

```
┌──────────┐     ┌──────────────┐     ┌──────────┐
│  user    │     │  user_role   │     │   role   │
├──────────┤     ├──────────────┤     ├──────────┤
│ id (PK)  │────→│ user_id (FK) │     │ id (PK)  │
│ username │     │ role_id (FK) │←────│ name     │
│ password │     └──────────────┘     │ code     │
└──────────┘                          └────┬─────┘
                                           │
                                    ┌──────┴──────────┐
                                    │ role_permission │
                                    ├─────────────────┤
                                    │ role_id (FK)    │
                                    │ permission_id (FK)│
                                    └────────┬────────┘
                                             │
                                    ┌────────┴────────┐
                                    │   permission    │
                                    ├─────────────────┤
                                    │ id (PK)         │
                                    │ name            │
                                    │ code            │
                                    │ url             │
                                    └─────────────────┘
```

---

## 90.3 建表 SQL

```sql
CREATE TABLE `user` (
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
    `username` VARCHAR(50) NOT NULL UNIQUE,
    `password` VARCHAR(255) NOT NULL,
    `email` VARCHAR(100),
    `enabled` TINYINT(1) DEFAULT 1,
    `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE `role` (
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(50) NOT NULL COMMENT '角色名（中文显示用）',
    `code` VARCHAR(50) NOT NULL UNIQUE COMMENT '角色编码（程序用，如 ROLE_ADMIN）',
    `description` VARCHAR(255)
);

CREATE TABLE `permission` (
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(50) NOT NULL COMMENT '权限名',
    `code` VARCHAR(100) NOT NULL UNIQUE COMMENT '权限编码（如 user:delete）',
    `url` VARCHAR(255) COMMENT '对应的接口路径',
    `method` VARCHAR(10) COMMENT 'HTTP方法'
);

CREATE TABLE `user_role` (
    `user_id` BIGINT NOT NULL,
    `role_id` BIGINT NOT NULL,
    PRIMARY KEY (`user_id`, `role_id`),
    FOREIGN KEY (`user_id`) REFERENCES `user`(`id`),
    FOREIGN KEY (`role_id`) REFERENCES `role`(`id`)
);

CREATE TABLE `role_permission` (
    `role_id` BIGINT NOT NULL,
    `permission_id` BIGINT NOT NULL,
    PRIMARY KEY (`role_id`, `permission_id`),
    FOREIGN KEY (`role_id`) REFERENCES `role`(`id`),
    FOREIGN KEY (`permission_id`) REFERENCES `permission`(`id`)
);
```

### 初始数据

```sql
INSERT INTO `role` (`name`, `code`) VALUES ('管理员', 'ROLE_ADMIN'), ('编辑', 'ROLE_EDITOR'), ('访客', 'ROLE_VISITOR');

INSERT INTO `permission` (`name`, `code`, `url`, `method`) VALUES
('查看文章', 'article:read', '/api/articles/**', 'GET'),
('创建文章', 'article:create', '/api/articles', 'POST'),
('修改文章', 'article:update', '/api/articles/**', 'PUT'),
('删除文章', 'article:delete', '/api/articles/**', 'DELETE'),
('管理用户', 'user:manage', '/api/admin/users/**', 'ALL');

INSERT INTO `role_permission` (`role_id`, `permission_id`) VALUES
(1, 1), (1, 2), (1, 3), (1, 4), (1, 5),  -- ADMIN: 全部权限
(2, 1), (2, 2), (2, 3),                    -- EDITOR: 读+写+改
(3, 1);                                    -- VISITOR: 只读
```

> 🤔 想多一点：为什么权限表要有 `url` 和 `method` 字段？因为有了这两个字段，你可以在数据库层面配置"哪个接口需要哪个权限"，而不需要每次新增接口都改 Java 代码。启动时从数据库加载权限表到内存，过滤器根据请求的 URL + Method 匹配权限。

---

## 90.4 Java 实体类

```java
@Entity
@Table(name = "role")
@Data
public class Role {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    private String name;
    private String code;

    @ManyToMany(fetch = FetchType.EAGER)
    @JoinTable(name = "role_permission",
        joinColumns = @JoinColumn(name = "role_id"),
        inverseJoinColumns = @JoinColumn(name = "permission_id"))
    private Set<Permission> permissions = new HashSet<>();
}

@Entity
@Table(name = "permission")
@Data
public class Permission {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    private String name;
    private String code;
    private String url;
    private String method;
}
```

User 实体增加角色关联：

```java
@ManyToMany(fetch = FetchType.EAGER)
@JoinTable(name = "user_role",
    joinColumns = @JoinColumn(name = "user_id"),
    inverseJoinColumns = @JoinColumn(name = "role_id"))
private Set<Role> roles = new HashSet<>();
```

---

## 90.5 动态权限过滤器

```java
@Component
@RequiredArgsConstructor
public class DynamicPermissionFilter extends OncePerRequestFilter {

    private final PermissionRepository permissionRepository;

    @Override
    protected void doFilterInternal(HttpServletRequest request,
                                    HttpServletResponse response,
                                    FilterChain chain)
            throws ServletException, IOException {

        String path = request.getRequestURI();
        String method = request.getMethod();

        Optional<Permission> requiredPermission =
                permissionRepository.findByUrlAndMethod(path, method);

        if (requiredPermission.isEmpty()) {
            chain.doFilter(request, response);  // 不需要权限的接口，放行
            return;
        }

        Authentication auth = SecurityContextHolder.getContext().getAuthentication();
        if (auth == null || !auth.isAuthenticated()) {
            response.sendError(401, "未登录");
            return;
        }

        boolean hasPermission = auth.getAuthorities().stream()
                .anyMatch(a -> a.getAuthority().equals(requiredPermission.get().getCode()));

        if (hasPermission) {
            chain.doFilter(request, response);
        } else {
            response.sendError(403, "权限不足");
        }
    }
}
```

---

## 90.6 优化——从数据库加载权限到内存

每次都查数据库效率低。改为启动时加载，放入 Map：

```java
@Component
public class PermissionRegistry {

    private final Map<String, Permission> permissionMap = new ConcurrentHashMap<>();

    public PermissionRegistry(PermissionRepository repository) {
        repository.findAll().forEach(p ->
            permissionMap.put(p.getUrl() + ":" + p.getMethod(), p));
    }

    public Optional<Permission> match(String url, String method) {
        // 先精确匹配，再模糊匹配（如 /api/articles/5 匹配 /api/articles/**）
        String key = url + ":" + method;
        if (permissionMap.containsKey(key)) {
            return Optional.of(permissionMap.get(key));
        }
        // AntPathMatcher 模糊匹配
        AntPathMatcher matcher = new AntPathMatcher();
        return permissionMap.entrySet().stream()
                .filter(e -> {
                    String[] parts = e.getKey().split(":");
                    return matcher.match(parts[0], url) && parts[1].equals(method);
                })
                .map(Map.Entry::getValue)
                .findFirst();
    }
}
```

---

## 90.7 Spring Security 方法级权限注解

除了 URL 级别的过滤器，你还可以在 Service 层方法上加注解：

```java
@RestController
@RequestMapping("/api/articles")
public class ArticleController {

    @GetMapping
    @PreAuthorize("hasAuthority('article:read')")
    public List<Article> list() { ... }

    @PostMapping
    @PreAuthorize("hasAuthority('article:create')")
    public Article create(@RequestBody Article article) { ... }

    @DeleteMapping("/{id}")
    @PreAuthorize("hasAuthority('article:delete')")
    public void delete(@PathVariable Long id) { ... }
}
```

别忘了启用方法级安全：

```java
@Configuration
@EnableMethodSecurity  // Spring Security 6 新写法
public class MethodSecurityConfig {
}
```

---

## 90.8 Role vs Permission —— 什么时候用哪个

| | Role（角色） | Permission（权限） |
|------|------|------|
| 粒度 | 粗 | 细 |
| 示例 | `ROLE_ADMIN` | `article:delete`、`user:create` |
| 适合场景 | 简单系统（3-5种角色） | 复杂系统（角色可能随时增删） |
| 优点 | 简单直观 | 灵活，新增权限不改代码 |
| Spring 注解 | `@PreAuthorize("hasRole('ADMIN')")` | `@PreAuthorize("hasAuthority('article:delete')")` |

最佳实践：**用户 → 角色 → 权限**。无论系统多大，加角色层，管理复杂度是 O(角色数) 而非 O(用户数 × 功能数)。

---

## 90.9 小结

| 知识点 | 核心内容 |
|--------|----------|
| RBAC | 用户 → 角色 → 权限，三层解耦 |
| 五张表 | user、role、permission、user_role、role_permission |
| 动态权限 | 数据库存 URL + Method，启动时加载，请求时匹配 |
| @PreAuthorize | 方法级权限控制 |
| 权限编码规范 | `资源:操作` 如 `article:delete` |

---

## 90.10 自测题

**1. RBAC 中"用户-角色-权限"三层各自解决了什么问题？如果去掉"角色"层直接"用户-权限"，会带来什么问题？**

**2. 以下 Java 代码中，哪个注解可以实现"只有拥有 `user:delete` 权限的用户才能调用"？**

```java
@???
public void deleteUser(Long id) { ... }
```

**3. 你有 100 个接口，需要在启动时从数据库加载对应的权限规则到内存。为什么不能每次请求都查数据库？**

---

**答案提示**：1→角色层解决了"权限组合复用"的问题。去掉角色直接用户-权限，1000 个用户 × 100 个功能 = 最大 100000 条关联记录，且每调整一组权限都要批量操作。2→`@PreAuthorize("hasAuthority('user:delete')")`。3→每次请求都查数据库 = 每次请求都多一次 I/O，1000 QPS 就是每秒 1000 次额外查询，数据库压力巨大。内存加载一次，请求时 O(1) 查 Map。下一章——常见 Web 攻击防御。