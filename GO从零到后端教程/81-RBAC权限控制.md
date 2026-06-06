# 第81章 · RBAC权限控制

> "用户登录了，Token也验证通过了——但每个登录用户都能做所有操作吗？当然不能。张三只能看和改自己的文章，李四作为管理员可以删任何人的文章，王五（实习生）只能看不能改。怎么管住这些'谁能干什么'？这就是权限控制。RBAC（Role-Based Access Control，基于角色的访问控制，详见附录I）是其中最经典、应用最广的模型。本章教你从零设计一套完整的权限系统。"

---

## 81.1 RBAC的核心思想

### 公司岗位的比喻

想象你刚入职一家公司：

```
你（User）→ 被分配岗位"会计"（Role）→ 会计能做"记账、出报表"（Permissions）
```

你之所以能做记账，不是因为你叫张三，而是因为你的岗位是会计。如果明天你调岗到开发部，你的权限自动切换——**权限跟着角色走，不跟人走**。

这就是RBAC的三层模型：

```
User（用户）──多对多──> Role（角色）──多对多──> Permission（权限）
```

### 为什么不能直接把权限挂在用户身上？

假设你有一百个"内容编辑"：
- 如果权限挂在人身上：每个编辑入职时，你都要手动给他分配"写文章、改文章、删自己的文章"等5个权限。编辑离职时要一个一个撤掉。新增一个权限（如"置顶文章"），要给一百个人逐个加上
- 如果权限挂在角色上：每个编辑入职时分配一个"编辑"角色。权限变更时，改一次角色就行——所有编辑自动获得新权限

**RBAC的核心价值：权限变更的维护成本从O(n)降到O(1)。**

### 一个内容管理系统的权限设计

| 角色 | 权限 |
|------|------|
| 游客 | 查看文章列表、查看单篇文章 |
| 作者 | 游客权限 + 写文章、改自己的文章、删自己的文章 |
| 编辑 | 作者权限 + 改任何人的文章、文章置顶 |
| 管理员 | 编辑权限 + 删任何人的文章、管理用户、系统配置 |

如果直接用 `if userID == ...` 判断权限会怎样？

```go
if user.ID == 1 || user.ID == 3 || user.ID == 7 || user.ID == 12 || user.ID == 15 {
    // 允许删除文章
}
```

这就是权限管理的噩梦：权限散落在代码各处，每增加一个管理员就要改代码、重新部署。而RBAC把权限关系移到数据库里，代码不变，改数据库就行。

---

## 81.2 数据库设计

### 五张核心表

```sql
CREATE TABLE users (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(64) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    status TINYINT NOT NULL DEFAULT 1,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE roles (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(64) NOT NULL UNIQUE,
    description VARCHAR(255) NOT NULL DEFAULT '',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE permissions (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    code VARCHAR(128) NOT NULL UNIQUE,
    name VARCHAR(128) NOT NULL,
    description VARCHAR(255) NOT NULL DEFAULT '',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE user_roles (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    role_id BIGINT NOT NULL,
    UNIQUE KEY uk_user_role (user_id, role_id),
    INDEX idx_user_id (user_id),
    INDEX idx_role_id (role_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE role_permissions (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    role_id BIGINT NOT NULL,
    permission_id BIGINT NOT NULL,
    UNIQUE KEY uk_role_perm (role_id, permission_id),
    INDEX idx_role_id (role_id),
    INDEX idx_permission_id (permission_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

五张表之间的关系：

```
users ──< user_roles >── roles ──< role_permissions >── permissions
```

- `users` 和 `roles` 是多对多（一个用户可以有多个角色，一个角色可以分配给多个用户）
- `roles` 和 `permissions` 也是多对多（一个角色有多个权限，一个权限可以属于多个角色）

### 初始化数据

```sql
INSERT INTO permissions (code, name, description) VALUES
('article:read',    '查看文章', '查看公开文章'),
('article:create',  '创建文章', '写新文章'),
('article:update',  '编辑文章', '修改已有文章'),
('article:delete',  '删除文章', '删除文章'),
('article:publish', '发布文章', '将草稿发布'),
('user:manage',     '管理用户', '查看和管理用户账号'),
('system:config',   '系统配置', '修改系统配置');

INSERT INTO roles (name, description) VALUES
('admin',     '系统管理员'),
('editor',    '内容编辑'),
('author',    '作者'),
('viewer',    '只读用户');

INSERT INTO role_permissions (role_id, permission_id) VALUES
(1, 1), (1, 2), (1, 3), (1, 4), (1, 5), (1, 6), (1, 7),
(2, 1), (2, 2), (2, 3), (2, 4), (2, 5),
(3, 1), (3, 2), (3, 3),
(4, 1);

INSERT INTO user_roles (user_id, role_id) VALUES
(1, 1),
(2, 2),
(3, 3),
(4, 4);
```

permission的 `code` 命名惯例：`资源:操作`（如 `article:delete`、`user:manage`）。这种命名既直观又可程序化处理。

---

## 81.3 Gin权限中间件

### 从数据库加载用户权限

```go
func GetUserPermissions(userID int64) ([]string, error) {
	query := `
		SELECT DISTINCT p.code
		FROM permissions p
		JOIN role_permissions rp ON p.id = rp.permission_id
		JOIN user_roles ur ON rp.role_id = ur.role_id
		WHERE ur.user_id = ?
	`

	rows, err := database.DB.Query(query, userID)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var permissions []string
	for rows.Next() {
		var code string
		rows.Scan(&code)
		permissions = append(permissions, code)
	}
	return permissions, nil
}
```

这个查询通过两次JOIN把用户→角色→权限串起来。每一步都清晰可读。

### 权限中间件

```go
func RequirePermission(permissionCode string) gin.HandlerFunc {
	return func(c *gin.Context) {
		userID, exists := c.Get("user_id")
		if !exists {
			c.JSON(http.StatusUnauthorized, gin.H{"code": 401, "msg": "请先登录"})
			c.Abort()
			return
		}

		permissions, err := GetUserPermissions(userID.(int64))
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"code": 500, "msg": "权限查询失败"})
			c.Abort()
			return
		}

		hasPermission := false
		for _, p := range permissions {
			if p == permissionCode || p == "system:config" {
				hasPermission = true
				break
			}
		}

		if !hasPermission {
			c.JSON(http.StatusForbidden, gin.H{"code": 403, "msg": "没有权限执行此操作"})
			c.Abort()
			return
		}

		c.Next()
	}
}
```

注意这里有一段特殊逻辑：`p == "system:config"`——管理员角色拥有 `system:config` 权限，自动通过所有权限检查。这是一种常见的"超级管理员"处理方式。

### 路由中使用

```go
func SetupRoutes(r *gin.Engine) {
	api := r.Group("/api/v1")
	api.Use(middleware.JWTAuth(jwtSecret))

	articles := api.Group("/articles")
	{
		articles.GET("", RequirePermission("article:read"), handler.ListArticles)
		articles.POST("", RequirePermission("article:create"), handler.CreateArticle)
		articles.PUT("/:id", RequirePermission("article:update"), handler.UpdateArticle)
		articles.DELETE("/:id", RequirePermission("article:delete"), handler.DeleteArticle)
	}

	admin := api.Group("/admin")
	admin.Use(RequirePermission("user:manage"))
	{
		admin.GET("/users", handler.ListUsers)
		admin.PUT("/users/:id/roles", handler.UpdateUserRoles)
	}
}
```

### 每次请求都查数据库会不会太慢？

这是个很好的问题。对于一个权限系统，每次API调用都做一次多表JOIN查询确实有开销。

**优化方案一：权限缓存**。用户登录时，把权限列表放到内存（如 `map[int64][]string`）或Redis里，中间件读缓存而不查数据库。但权限变更后（比如管理员修改了某人的角色），需要清理缓存。

**优化方案二：JWT里带权限**。签发JWT时，把用户的权限列表写到Payload里。验证JWT时直接读取权限，不需要任何数据库查询。代价是：权限变更后旧Token仍然有效（回到JWT章节讨论的问题），直到Token过期。

**方案选择**：
- 小型系统：每次查数据库足够（一次JOIN查询通常不到5ms）
- 中型系统：Redis缓存权限，权限变更时清理相关缓存
- 大型/高安全系统：权限放JWT + 短有效期 + 关键操作实时校验

---

## 81.4 Casbin：专业权限管理库

手写RBAC能帮你理解原理，但生产环境中有更成熟的解决方案。Casbin是Go生态中最强大的权限管理库——支持ACL、RBAC、ABAC等多种模型。

### Casbin的核心概念

Casbin用一个**模型文件**定义权限模型，用一个**策略文件**存储权限数据。代码里只做一件事：`enforcer.Enforce(user, resource, action)` —— 返回 `true/false`。

```
model.conf  (定义权限模型：比如用的是RBAC)
policy.csv  (定义具体规则：张三→编辑→能写文章)
```

### 安装

```bash
go get github.com/casbin/casbin/v2
go get github.com/casbin/gorm-adapter/v3
```

### model.conf

```ini
[request_definition]
r = sub, obj, act

[policy_definition]
p = sub, obj, act

[role_definition]
g = _, _

[policy_effect]
e = some(where (p.eft == allow))

[matchers]
m = g(r.sub, p.sub) && keyMatch(r.obj, p.obj) && regexMatch(r.act, p.act)
```

逐行解释：
- `r = sub, obj, act`：每次权限检查的输入是 `(用户, 资源, 操作)`
- `p = sub, obj, act`：每条策略规则也是 `(角色/用户, 资源, 操作)`
- `g = _, _`：定义一个角色继承关系 `g(张三, 作者)` 表示张三有"作者"角色
- `e = some(where (p.eft == allow))`：只要有一条策略匹配就通过
- `m = ...`：匹配逻辑——先检查用户是否属于策略中的角色（`g(r.sub, p.sub)`），再匹配资源（`keyMatch`支持通配符），再匹配操作

### policy.csv

```csv
p, admin, /*, *
p, editor, /articles/*, (GET)|(POST)|(PUT)|(DELETE)
p, author, /articles/*, (GET)|(POST)
p, author, /articles/:id, (PUT)|(DELETE)
p, viewer, /articles/*, (GET)

g, alice, admin
g, bob, editor
g, charlie, author
g, david, viewer
```

`p` 行定义策略：`p, 角色, 资源路径, 允许的操作`。
`g` 行定义角色分配：`g, 用户, 角色`。

`/*` 是通配符——admin可以访问所有资源。`/articles/:id` 匹配 `/articles/123` 这种有ID的路径。

### Go中使用Casbin

```go
package main

import (
	"github.com/casbin/casbin/v2"
	gormadapter "github.com/casbin/gorm-adapter/v3"
	"github.com/gin-gonic/gin"
	"gorm.io/driver/mysql"
	"gorm.io/gorm"
)

func main() {
	db, _ := gorm.Open(mysql.Open("user:password@tcp(localhost:3306)/myapp?charset=utf8mb4"), &gorm.Config{})

	adapter, _ := gormadapter.NewAdapterByDB(db)
	enforcer, _ := casbin.NewEnforcer("model.conf", adapter)

	r := gin.Default()

	r.Use(func(c *gin.Context) {
		username := c.GetString("username")
		if username == "" {
			c.JSON(401, gin.H{"msg": "未登录"})
			c.Abort()
			return
		}

		ok, _ := enforcer.Enforce(username, c.Request.URL.Path, c.Request.Method)
		if !ok {
			c.JSON(403, gin.H{"msg": "没有权限"})
			c.Abort()
			return
		}

		c.Next()
	})

	r.GET("/articles", func(c *gin.Context) {
		c.JSON(200, gin.H{"msg": "文章列表"})
	})

	r.Run(":8080")
}
```

只用一行 `enforcer.Enforce(username, path, method)` 就完成了权限校验。

### Casbin的模型类型

| 模型 | 配置文件 | 适用场景 |
|------|---------|---------|
| ACL | `model.conf` 基础版 | 直接指定 用户-资源-操作 |
| RBAC | 加入 `[role_definition]` | 用户→角色→权限 |
| RBAC with Domains | 加入 `dom` 参数 | 多租户系统（不同公司不同权限） |
| ABAC | 加入自定义匹配函数 | 基于属性的权限（如"只有工作时间能访问"） |
| RESTful | 加入 `keyMatch` | 匹配URL路径和HTTP方法 |

### Casbin策略的存储方式

Casbin的"适配器"机制让它可以把策略存在任何地方：

- `file-adapter`：.csv文件（开发环境）
- `gorm-adapter`：MySQL/PostgreSQL/SQLite
- `redis-adapter`：Redis
- 自己写adapter实现接口即可

生产环境推荐用 `gorm-adapter` 存数据库——可以在管理后台动态增删策略，不需要重启服务。

### 🤔 想多一点

自己写RBAC还是用Casbin？

**自己写**：代码量不大（中间件几十行、数据库5张表），理解每一行的逻辑，调试方便，性能可控。适合标准RBAC、不需要太多花样的场景。

**Casbin**：支持复杂的策略组合、角色继承、域隔离、ABAC、表达式匹配……但需要学习其模型语言，出问题时排查困难。适合权限模型复杂或需要多模型并存的场景。

一个务实的选择：先手写简单的RBAC。当发现权限需求越来越复杂（比如多租户、资源级别的权限、动态ABAC）时再引入Casbin。

---

## 81.5 前端按钮级权限控制思路

后端控制接口权限是底线——即使前端界面显示了不该显示的按钮，点了也不生效。但从用户体验角度，不该让用户看到他不能操作的按钮。

### 基本思路

后端在用户信息接口里返回权限列表：

```json
{
  "user_id": 42,
  "username": "张三",
  "permissions": ["article:read", "article:create", "article:update"]
}
```

前端根据权限列表控制UI：

```javascript
const permissions = user.permissions;

if (permissions.includes("article:delete")) {
    showDeleteButton();
}

if (permissions.includes("article:create")) {
    showCreateButton();
}
```

### 强调

**前端权限控制只是UI优化，不是安全保障。** 用户可以在浏览器里改JS、直接发HTTP请求绕过前端限制。真正的安全保障只在后端——即使前端没显示删除按钮，后端也必须验证用户有没有 `article:delete` 权限。

---

## 本章小结

| 知识点 | 要点 |
|--------|------|
| RBAC核心 | User → Role → Permission，权限跟角色不跟人 |
| 为什么用角色 | 权限变更O(n)→O(1)，管理成本大幅降低 |
| 五张表 | users / roles / permissions / user_roles / role_permissions |
| permission code | `资源:操作`命名，如 `article:delete` |
| 权限查询 | 两次JOIN，一次查询拿到所有权限 |
| 权限中间件 | 从JWT取userID→查权限→判断→放行/403 |
| 权限缓存 | Redis缓存（中型）或放JWT（大型） |
| Casbin | 专业权限库，一行 `Enforce()` 完成校验 |
| model.conf | 定义权限模型（RBAC/ACL/ABAC） |
| policy.csv | 定义具体规则（谁→什么→能干嘛） |
| 前端按钮权限 | UI优化，非安全保障，后端才是底线 |

> 🚀 下一章：第82章 · Web安全：常见攻击。现在你的系统有了认证、授权、权限控制——但这些都有一个前提：你的服务器本身是安全的。如果黑客通过SQL注入拿到了整个数据库，前面的一切都白费了。本章我们学习最常见的四种Web攻击（SQL注入、XSS、CSRF、SSRF）以及如何在Go中防护它们。

---
[鈫?涓婁竴绔狅細81-OAuth 2.0.md](80-OAuth 2.0/) | [涓嬩竴绔狅細83-Web瀹夊叏锛氬父瑙佹敾鍑?md 鈫抅(83-Web瀹夊叏锛氬父瑙佹敾鍑?md)


---
[← 上一章：80-OAuth 2.0.md](80-OAuth 2.0/) | [下一章：82-Web安全：常见攻击.md →](82-Web安全：常见攻击/)
