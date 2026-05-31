# 77-SpringMVC（三）响应处理

> 💡 你去不同的公司面试。A公司面试完发微信："过了，下周一入职。" B公司发来一封正式邮件：主题、称呼、正文、薪资、入职日期、HR联系方式——整整一页。哪种体验更好？B公司。你的 API 也一样——返回 `"ok"` 两个字母和返回结构化的 `{code:200, message:"操作成功", data:{...}}`，后者让前端开发省心百倍。

---

## 本章目标
- 设计统一响应格式 `{code, message, data}`
- 掌握 Jackson 注解控制 JSON 序列化
- 理解 `ResponseEntity` 的灵活用法
- 编写通用的 `Result<T>` 工具类

---

## 77.1 统一响应格式——让前端不再猜

没有统一格式的 API：

```json
// 成功时返回
{"id":1, "username":"zhangsan"}

// 失败时返回
"用户不存在"

// 另一种失败
{"error":"用户名已存在"}
```

前端要写 3 套解析逻辑。统一格式后：

```json
{
    "code": 200,
    "message": "操作成功",
    "data": {"id": 1, "username": "zhangsan", "email": "zhangsan@example.com"}
}
```

---

## 77.2 Result 工具类

```java
package com.example.demo.common;

import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class Result<T> {
    private int code;
    private String message;
    private T data;

    public static <T> Result<T> success(T data) {
        return new Result<>(200, "操作成功", data);
    }

    public static <T> Result<T> success(String message, T data) {
        return new Result<>(200, message, data);
    }

    public static <T> Result<T> error(int code, String message) {
        return new Result<>(code, message, null);
    }

    public static <T> Result<T> error(String message) {
        return new Result<>(400, message, null);
    }
}
```

Controller 中使用：

```java
@GetMapping
public Result<List<User>> list() {
    List<User> users = userService.findAll();
    return Result.success(users);
}

@PostMapping
public Result<User> create(@Valid @RequestBody User user) {
    User created = userService.create(user);
    return Result.success("用户创建成功", created);
}
```

---

## 77.3 Jackson 注解——控制 JSON 的每一个细节

| 注解 | 作用 |
|------|------|
| `@JsonProperty("user_id")` | 字段重命名输出 |
| `@JsonIgnore` | 隐藏字段（如密码），永不返回给前端 |
| `@JsonInclude(JsonInclude.Include.NON_NULL)` | null 字段不输出 |
| `@JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss", timezone = "GMT+8")` | 日期格式化 |
| `@JsonIgnoreProperties({"password", "salt"})` | 类级别忽略多个字段 |

### 全局配置（推荐）

```yaml
spring:
  jackson:
    date-format: yyyy-MM-dd HH:mm:ss
    time-zone: GMT+8
    default-property-inclusion: non_null
```

---

## 77.4 ResponseEntity——完全掌控 HTTP 响应

```java
@PostMapping
public ResponseEntity<Result<User>> create(@Valid @RequestBody User user) {
    User created = userService.create(user);
    return ResponseEntity
            .status(HttpStatus.CREATED)          // 201 而非 200
            .header("X-Custom-Header", "value")
            .body(Result.success("用户创建成功", created));
}

@DeleteMapping("/{id}")
public ResponseEntity<Result<Void>> delete(@PathVariable Long id) {
    userService.delete(id);
    return ResponseEntity.noContent().build();  // 204 No Content
}
```

### 常用 HTTP 状态码

| 状态码 | 常量 | 含义 |
|--------|------|------|
| 200 | `HttpStatus.OK` | 请求成功 |
| 201 | `HttpStatus.CREATED` | 创建成功 |
| 204 | `HttpStatus.NO_CONTENT` | 删除成功，无响应体 |
| 400 | `HttpStatus.BAD_REQUEST` | 请求参数错误 |
| 404 | `HttpStatus.NOT_FOUND` | 资源不存在 |
| 500 | `HttpStatus.INTERNAL_SERVER_ERROR` | 服务器内部错误 |

---

## 77.5 完整 CRUD Controller

```java
@RestController
@RequestMapping("/api/users")
public class UserController {

    private final UserService userService;

    public UserController(UserService userService) {
        this.userService = userService;
    }

    @GetMapping
    public ResponseEntity<Result<List<User>>> list() {
        return ResponseEntity.ok(Result.success(userService.findAll()));
    }

    @GetMapping("/{id}")
    public ResponseEntity<Result<User>> getById(@PathVariable Long id) {
        return ResponseEntity.ok(Result.success(userService.findById(id)));
    }

    @PostMapping
    public ResponseEntity<Result<User>> create(@Valid @RequestBody User user) {
        User created = userService.create(user);
        return ResponseEntity.status(HttpStatus.CREATED)
                .body(Result.success("用户创建成功", created));
    }

    @PutMapping("/{id}")
    public ResponseEntity<Result<User>> update(
            @PathVariable Long id, @Valid @RequestBody User user) {
        return ResponseEntity.ok(Result.success(userService.update(id, user)));
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Result<Void>> delete(@PathVariable Long id) {
        userService.delete(id);
        return ResponseEntity.noContent().build();
    }
}
```

---

## 77.6 小结

| 知识点 | 核心内容 |
|--------|----------|
| Result 统一响应 | `{code, message, data}` 泛型包装类 |
| @JsonProperty | 字段重命名输出 |
| @JsonIgnore | 隐藏字段（密码等） |
| @JsonInclude(NON_NULL) | null 字段不输出 |
| @JsonFormat | 日期格式化 |
| ResponseEntity | 完全控制 HTTP 状态码、响应头、响应体 |

---

## 77.7 自测题

**1. 以下关于 `@JsonIgnore` 的描述，哪一项是正确的？**

A. 被标记的字段不会被存入数据库  
B. 被标记的字段在序列化为 JSON 时不会被输出  
C. 被标记的字段不能从 JSON 请求体反序列化  
D. B 和 C 都正确  

**2. 你的 API 在删除用户时，应该返回什么 HTTP 状态码？**

**3. 编写一个 `Result` 的 `error` 方法，接受错误码和错误信息，返回一个 `Result<Void>`。**

---

**答案提示**：1→B。2→推荐 204 No Content，或约定统一返回 200 + `{code:200, data:null}`。3→`public static Result<Void> error(int code, String message) { return new Result<>(code, message, null); }`。下一章——Filter 和 Interceptor。