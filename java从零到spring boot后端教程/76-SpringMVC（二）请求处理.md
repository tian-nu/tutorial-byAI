# 76-SpringMVC（二）请求处理

> 💡 你打开快递柜取包裹。系统要求你输入取件码——6位数字，不能多不能少，不能有字母。你输错了？弹窗告诉你"取件码格式错误"。这套"前端给你参数，后端检查合不合法"的流程，就是本章要讲的内容——如何优雅地接收参数、校验参数、处理校验失败的情况。

---

## 本章目标
- 用 `@RequestParam` 接收查询参数
- 用 `@RequestBody` 接收 JSON 请求体
- 使用 Jakarta Validation 进行参数校验
- 理解 `BindingResult` 处理校验错误

---

## 76.1 @RequestParam——接收查询参数和表单参数

URL 中 `?` 后面的键值对就是查询参数。例如：

```
GET /api/users?page=1&size=10&keyword=zhang
```

```java
@GetMapping
public List<User> list(
        @RequestParam(defaultValue = "1") int page,
        @RequestParam(defaultValue = "10") int size,
        @RequestParam(required = false) String keyword) {

    System.out.println("page=" + page + ", size=" + size + ", keyword=" + keyword);
    return userService.findByPage(page, size, keyword);
}
```

### @RequestParam 参数详解

| 属性 | 说明 | 示例 |
|------|------|------|
| `value` / `name` | 绑定的参数名 | `@RequestParam("page")` |
| `required` | 是否必传，默认 `true` | `@RequestParam(required = false)` |
| `defaultValue` | 默认值（设置后 required 自动为 false） | `@RequestParam(defaultValue = "1")` |

### 常见错误

```java
// 客户端不传 page，启动时不会报错，但请求时报 400
@GetMapping
public List<User> list(@RequestParam int page) { }

// 请求：GET /api/users （没传 page）→ 400 Bad Request
// 解决：给默认值
@GetMapping
public List<User> list(@RequestParam(defaultValue = "1") int page) { }
```

### 接收数组

```java
// GET /api/users?ids=1&ids=2&ids=3
@GetMapping
public List<User> getByIds(@RequestParam List<Long> ids) {
    return userService.findByIds(ids);
}
```

---

## 76.2 @RequestBody——接收 JSON 请求体

POST / PUT 请求通常携带 JSON 格式的请求体：

```json
{
    "username": "zhangsan",
    "email": "zhangsan@example.com",
    "age": 25
}
```

```java
@PostMapping
public User create(@RequestBody User user) {
    return userService.create(user);
}
```

Spring Boot 自动用 **Jackson** 将 JSON 字符串反序列化为 `User` 对象。

### 排查方法

```java
@PostMapping
public User create(@RequestBody User user) {
    System.out.println("收到的用户：" + user);  // 调试
    return userService.create(user);
}
```

---

## 76.3 Jakarta Validation——让参数校验像填表格一样清晰

没有校验的世界：每个字段都得在方法里写 `if null`。Jakarta Validation 用注解声明约束规则：

```java
package com.example.demo.model;

import jakarta.validation.constraints.*;
import lombok.Data;

@Data
public class User {

    private Long id;

    @NotBlank(message = "用户名不能为空")
    @Size(min = 2, max = 20, message = "用户名长度必须在2-20之间")
    private String username;

    @NotBlank(message = "邮箱不能为空")
    @Email(message = "邮箱格式不正确")
    private String email;

    @NotNull(message = "年龄不能为空")
    @Min(value = 0, message = "年龄不能小于0")
    @Max(value = 150, message = "年龄不能大于150")
    private Integer age;

    @Pattern(regexp = "^1[3-9]\\d{9}$", message = "手机号格式不正确")
    private String phone;
}
```

Controller 中加 `@Valid` 注解启用校验：

```java
@PostMapping
public User create(@Valid @RequestBody User user) {
    return userService.create(user);
}
```

### 常用校验注解速查表

| 注解 | 适用类型 | 说明 |
|------|----------|------|
| `@NotNull` | 任何类型 | 值不能为 null |
| `@NotBlank` | String | 不能为 null、不能为空字符串、不能全空白 |
| `@NotEmpty` | String / Collection / Map | 不能为 null、不能为空（size=0） |
| `@Size(min, max)` | String / Collection / Map | 长度/大小范围 |
| `@Min(value)` | 数字类型 | 最小值（含） |
| `@Max(value)` | 数字类型 | 最大值（含） |
| `@Email` | String | 邮箱格式 |
| `@Pattern(regexp)` | String | 正则表达式匹配 |
| `@Positive` | 数字类型 | 必须为正数（>0） |
| `@PositiveOrZero` | 数字类型 | 必须为非负数（>=0） |

---

## 76.4 BindingResult——拿到校验失败的具体信息

当 `@Valid` 校验失败时，Spring 默认返回 400 Bad Request，但错误信息不友好。使用 `BindingResult` 可以拿到详细校验错误：

```java
@PostMapping
public ResponseEntity<?> create(@Valid @RequestBody User user, BindingResult bindingResult) {
    if (bindingResult.hasErrors()) {
        List<String> errors = bindingResult.getFieldErrors().stream()
                .map(e -> e.getField() + ": " + e.getDefaultMessage())
                .toList();
        return ResponseEntity.badRequest().body(errors);
    }
    return ResponseEntity.ok(userService.create(user));
}
```

---

## 76.5 自定义校验注解

当内置注解不够用时（比如"用户名不能包含敏感词"），可以自定义：

```java
@Documented
@Constraint(validatedBy = NoSensitiveWordsValidator.class)
@Target({ElementType.FIELD})
@Retention(RetentionPolicy.RUNTIME)
public @interface NoSensitiveWords {
    String message() default "包含敏感词";
    Class<?>[] groups() default {};
    Class<? extends Payload>[] payload() default {};
}
```

```java
public class NoSensitiveWordsValidator
        implements ConstraintValidator<NoSensitiveWords, String> {

    private static final Set<String> SENSITIVE_WORDS = Set.of("admin", "root", "system");

    @Override
    public boolean isValid(String value, ConstraintValidatorContext context) {
        if (value == null) return true;
        return SENSITIVE_WORDS.stream().noneMatch(value.toLowerCase()::contains);
    }
}
```

---

## 76.6 分组校验——不同场景不同规则

```java
// 定义标记接口
public interface OnCreate {}
public interface OnUpdate {}
```

```java
@Data
public class User {

    @NotNull(groups = OnUpdate.class, message = "更新时ID不能为空")
    private Long id;

    @NotBlank(groups = OnCreate.class, message = "创建时用户名不能为空")
    private String username;

    @Email(message = "邮箱格式不正确")
    private String email;
}
```

```java
// 创建时校验 OnCreate 组
@PostMapping
public User create(@Validated(OnCreate.class) @RequestBody User user) {
    return userService.create(user);
}

// 更新时校验 OnUpdate 组
@PutMapping("/{id}")
public User update(@PathVariable Long id, @Validated(OnUpdate.class) @RequestBody User user) {
    return userService.update(id, user);
}
```

---

## 76.7 小结

| 知识点 | 核心内容 |
|--------|----------|
| @RequestParam | 接收查询参数，支持默认值、必选/可选、数组 |
| @RequestBody | 将 JSON 请求体反序列化为 Java 对象 |
| @Valid / @Validated | 触发 Jakarta Validation 校验 |
| @NotBlank / @NotNull / @NotEmpty | 三者的区别要分清 |
| BindingResult | 获取校验失败的详细错误列表 |
| 自定义校验 | 实现 ConstraintValidator 接口 + @Constraint 注解 |
| 分组校验 | 通过 groups 标记接口区分创建/更新场景 |

---

## 76.8 自测题

**1. 以下代码中，客户端不传 `page` 参数会怎样？**

```java
@GetMapping("/users")
public List<User> list(@RequestParam int page) { }
```

A. page 的值是 0  
B. page 的值是 null  
C. 返回 400 Bad Request  
D. 启动时报错  

**2. @NotBlank、@NotEmpty、@NotNull 的区别是什么？**

**3. 你有一个新建订单的接口，需要校验"订单金额必须为正数"。请写出 DTO 类的相关字段注解和 Controller 方法签名。**

---

**答案提示**：1→C。2→@NotNull: null 不通过；@NotEmpty: null 和空字符串不通过；@NotBlank: null、空字符串、全空白都不通过。3→`@NotNull @Positive private BigDecimal amount;` + `public Result<Order> create(@Valid @RequestBody CreateOrderDto dto)`。下一章——响应处理。