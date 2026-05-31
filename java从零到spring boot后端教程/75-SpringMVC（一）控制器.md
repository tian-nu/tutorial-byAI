# 75-SpringMVC（一）控制器

> 💡 你走进一家餐厅，桌上没有菜单，但你很熟练："服务员，一份宫保鸡丁，少辣。"服务员记下，传给后厨，后厨做好，服务员端回来。这个过程四要素：你（客户端）、点菜（HTTP 请求）、服务员+后厨（控制器+服务层）、上菜（HTTP 响应）。Spring MVC 就是这套"餐厅流程"的数字化。控制器是"服务员"——它不炒菜，但它知道每道菜找哪个厨师。

---

## 本章目标
- 理解 MVC 分层架构的意义
- 掌握 `@RestController`、`@RequestMapping`、`@GetMapping`、`@PostMapping`、`@PutMapping`、`@DeleteMapping`
- 写出第一个完整的 RESTful CRUD 控制器
- 理解 `@PathVariable` 和 `@RequestBody` 的用法

---

## 75.1 MVC 是什么——一分钱一块钱的道理

MVC 是 Model-View-Controller 的缩写。但在 REST API 的世界里，View 通常不存在（返回的是 JSON 数据），所以我们实际用的是 **MC 模式**：

```
HTTP 请求 → Controller（服务员）
                ↓ 调用
           Service（厨师长：编排逻辑）
                ↓ 调用
          Repository（备菜员：操作数据库）
                ↓ 返回
           Service
                ↓ 返回
          Controller → HTTP 响应（JSON）
```

**为什么要分层？** 假设你把所有逻辑都塞在 Controller 里：

```java
@RestController
public class OrderController {

    @PostMapping("/orders")
    public String createOrder(@RequestBody Order order) {
        // 1. 校验库存（10行）
        // 2. 计算价格（20行）
        // 3. 保存订单（5行）
        // 4. 发送通知（10行）
        // 5. 更新库存（10行）
        // 怎么办？一个方法 55 行，越来越肥
    }
}
```

分层之后，Controller 只做三件事：
1. **接收请求**（拿参数）
2. **调用服务**（委托业务逻辑）
3. **返回响应**（把结果打包成 JSON）

---

## 75.2 注解速查表

| 注解 | 作用 | 位置 |
|------|------|------|
| `@RestController` | 标记为 REST 控制器，返回值自动序列化为 JSON | 类上 |
| `@RequestMapping("/api/users")` | 定义 URL 前缀 | 类上或方法上 |
| `@GetMapping` | 处理 GET 请求（查询） | 方法上 |
| `@PostMapping` | 处理 POST 请求（新增） | 方法上 |
| `@PutMapping("/{id}")` | 处理 PUT 请求（全量更新） | 方法上 |
| `@PatchMapping("/{id}")` | 处理 PATCH 请求（部分更新） | 方法上 |
| `@DeleteMapping("/{id}")` | 处理 DELETE 请求（删除） | 方法上 |
| `@PathVariable` | 从 URL 路径中提取变量 | 参数上 |
| `@RequestBody` | 从 HTTP 请求体中提取 JSON→对象 | 参数上 |

---

## 75.3 第一个 CRUD Controller——用户管理

完整的增删改查控制器，对照 RESTful 规范：

| 操作 | HTTP 方法 | URL | 含义 |
|------|----------|-----|------|
| 查询全部 | GET | `/api/users` | 获取用户列表 |
| 查询单个 | GET | `/api/users/{id}` | 获取指定用户 |
| 新增 | POST | `/api/users` | 创建用户 |
| 更新 | PUT | `/api/users/{id}` | 全量更新用户 |
| 删除 | DELETE | `/api/users/{id}` | 删除用户 |

```java
package com.example.demo.controller;

import com.example.demo.model.User;
import com.example.demo.service.UserService;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/users")
public class UserController {

    private final UserService userService;

    public UserController(UserService userService) {
        this.userService = userService;
    }

    @GetMapping
    public List<User> list() {
        return userService.findAll();
    }

    @GetMapping("/{id}")
    public User getById(@PathVariable Long id) {
        return userService.findById(id);
    }

    @PostMapping
    public User create(@RequestBody User user) {
        return userService.create(user);
    }

    @PutMapping("/{id}")
    public User update(@PathVariable Long id, @RequestBody User user) {
        return userService.update(id, user);
    }

    @DeleteMapping("/{id}")
    public void delete(@PathVariable Long id) {
        userService.delete(id);
    }
}
```

### 实体类（Model）

```java
package com.example.demo.model;

import lombok.Data;
import java.time.LocalDateTime;

@Data
public class User {
    private Long id;
    private String username;
    private String email;
    private LocalDateTime createdAt;
}
```

### 服务层（Service）

```java
package com.example.demo.service;

import com.example.demo.model.User;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicLong;

@Service
public class UserService {

    private final Map<Long, User> userStore = new ConcurrentHashMap<>();
    private final AtomicLong idGenerator = new AtomicLong(1);

    public List<User> findAll() {
        return new ArrayList<>(userStore.values());
    }

    public User findById(Long id) {
        User user = userStore.get(id);
        if (user == null) {
            throw new RuntimeException("用户不存在：" + id);
        }
        return user;
    }

    public User create(User user) {
        user.setId(idGenerator.getAndIncrement());
        user.setCreatedAt(LocalDateTime.now());
        userStore.put(user.getId(), user);
        return user;
    }

    public User update(Long id, User updated) {
        User existing = findById(id);
        existing.setUsername(updated.getUsername());
        existing.setEmail(updated.getEmail());
        return existing;
    }

    public void delete(Long id) {
        if (userStore.remove(id) == null) {
            throw new RuntimeException("用户不存在：" + id);
        }
    }
}
```

> ⚠️ 以上 Service 用内存 Map 模拟数据库。第61-70章已学过 JDBC/JPA，第81章将用真实数据库替代这个内存实现。

### 测试接口

```bash
# 创建用户
curl -X POST http://localhost:8080/api/users \
  -H "Content-Type: application/json" \
  -d '{"username":"zhangsan","email":"zhangsan@example.com"}'

# 查询全部
curl http://localhost:8080/api/users

# 查询单个
curl http://localhost:8080/api/users/1

# 更新
curl -X PUT http://localhost:8080/api/users/1 \
  -H "Content-Type: application/json" \
  -d '{"username":"zhangsan_new","email":"new@example.com"}'

# 删除
curl -X DELETE http://localhost:8080/api/users/1
```

---

## 75.4 @RequestMapping 的细节

### 限制请求方式

```java
// 只接受 GET 和 POST
@RequestMapping(value = "/users", method = {RequestMethod.GET, RequestMethod.POST})
```

等价于分别写 `@GetMapping` 和 `@PostMapping`。

### 限制 Content-Type

```java
@PostMapping(value = "/users", consumes = "application/json")   // 只接受 JSON 请求体
@GetMapping(value = "/users", produces = "application/json")     // 只返回 JSON 响应
```

### 路径变量的另一种写法

```java
// 两种写法等价
@GetMapping("/{id}")
public User getById(@PathVariable Long id) { }

@GetMapping("/{userId}")
public User getById(@PathVariable("userId") Long id) { }  // 显式指定变量名
```

---

## 75.5 RESTful URL 设计原则

| 原则 | 正确示例 | 错误示例 |
|------|----------|----------|
| 资源用名词复数 | `/api/users` | `/api/getUsers` |
| 层级关系用路径 | `/api/users/{id}/orders` | `/api/getUserOrders?id=1` |
| 动作用 HTTP 方法表达 | `DELETE /api/users/1` | `POST /api/users/delete/1` |
| 过滤用查询参数 | `/api/users?status=active` | `/api/users/active` |

> 🤔 想多一点：RESTful 不是法律，是约定。如果你的业务有"批量删除"这种操作，`DELETE /api/users` 不直观，用 `POST /api/users/batch-delete` 也完全可以。关键是团队统一、文档清晰。

---

## 75.6 小结

| 知识点 | 核心内容 |
|--------|----------|
| MVC 分层 | Controller（接收+响应）→ Service（业务逻辑）→ Repository（数据） |
| @RestController | 类级注解，所有方法返回值自动 JSON 序列化 |
| @RequestMapping | 定义 URL 前缀或映射 |
| @GetMapping/@PostMapping/@PutMapping/@DeleteMapping | HTTP 方法映射 |
| @PathVariable | 提取 URL 路径变量 |
| @RequestBody | 将 JSON 请求体反序列化为 Java 对象 |
| RESTful 规范 | 名词复数 + HTTP 方法表达动作 |

---

## 75.7 自测题

**1. 以下 URL 设计，哪一个不符合 RESTful 规范？**

A. `GET /api/users/1`  
B. `POST /api/users`  
C. `GET /api/getUsers`  
D. `DELETE /api/users/1`  

**2. @RestController 和 @Controller 的区别是什么？**

**3. 写一个 Controller 方法：根据用户 ID 和订单状态查询该用户的订单列表。URL 应该怎么设计？**

---

**答案提示**：1→C（动词 getUsers 应改为名词 users）。2→`@RestController` = `@Controller` + `@ResponseBody`，所有方法返回值自动写入响应体（JSON 序列化）；`@Controller` 默认返回视图名，需配合 `@ResponseBody` 才能返回 JSON。3→`GET /api/users/{userId}/orders?status={status}`，用 `@PathVariable Long userId` 获取用户 ID，用 `@RequestParam String status` 获取订单状态。下一章——深入请求处理的细节。