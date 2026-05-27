# 第16章：Spring Boot Web开发

## 本章目标

学完本章你将能够：

- 设计并实现企业级统一返回格式`Result<T>`类，包含状态码枚举和静态工厂方法
- 使用`@RestControllerAdvice`实现三层全局异常处理（业务异常、校验异常、兜底异常）
- 掌握JSR-380参数校验注解体系，编写自定义校验注解
- 理解CORS跨域原理，用三种方式配置跨域处理
- 实现安全可靠的文件上传下载功能
- 编写登录拦截器并解决拦截器中Service为null的经典问题

---

> **本章定位**：本章专注于Spring Boot Web开发的最佳实践。第12章我们学习了Spring MVC基础（Controller、请求绑定、响应），本章将在此基础上构建一套完整、健壮、可复用的Web层基础架构。学完本章，你写的Controller会拥有统一返回格式、全局异常兜底、自动参数校验、跨域支持——这些是任何一个企业级后端项目的标配。

---

## 16.1 静态资源处理

### 16.1.1 默认静态资源路径

Spring Boot内置了静态资源处理机制，无需额外配置。以下四个classpath路径下的文件会自动作为静态资源提供：

```
1. classpath:/static/          ← 最常用
2. classpath:/public/
3. classpath:/resources/       ← 注意！不是src/main/resources，是classpath下的resources目录
4. classpath:/META-INF/resources/
```

在实际项目中，你只需把`logo.png`放到`src/main/resources/static/`目录下，启动应用后访问`http://localhost:8080/logo.png`即可。

这四个路径的优先级从高到低为：`/META-INF/resources/` > `/resources/` > `/static/` > `/public/`。如果同名文件存在于多个路径，优先级高的生效。

### 16.1.2 自定义静态资源路径

如果需要使用其他目录，在`application.yml`中配置：

```yaml
spring:
  web:
    resources:
      static-locations:
        - classpath:/custom-static/
        - file:/opt/uploads/        # 也可以指向文件系统绝对路径
```

> 🚨 **坑点：Controller路径会覆盖静态资源路径**

假设你有一个Controller：

```java
@RestController
public class PageController {
    @GetMapping("/index.html")
    public String index() {
        return "这是Controller返回的内容";
    }
}
```

同时`static/`下也有一个`index.html`。当你访问`/index.html`时，返回的是**Controller的内容，而不是静态文件**。这是因为Spring MVC的DispatcherServlet会先匹配HandlerMapping（Controller），找不到才走静态资源处理。

**这个优先级规则是：Controller > 静态资源 > 404错误页面。**

### 16.1.3 静态资源缓存配置

```yaml
spring:
  web:
    resources:
      cache:
        period: 86400              # 缓存时间（秒），24小时
      chain:
        cache: true                # 启用资源链缓存
        strategy:
          content:
            enabled: true          # 基于内容的版本策略
            paths: /js/**, /css/**
```

---

## 16.2 统一返回格式 — Result<T> 类完整设计

### 16.2.1 为什么需要统一返回格式？

想象一下，如果没有统一格式，你的API可能是这样的：

```json
// 成功时返回（接口A）
{ "id": 1, "name": "张三", "salary": 18000 }

// 成功时返回（接口B）
{ "employees": [{...}], "total": 100 }

// 失败时返回（接口A）
{ "error": "用户不存在" }

// 失败时返回（接口B）
{ "status": "error", "msg": "参数错误" }
```

前端开发者看到这些响应会崩溃——每个接口的响应结构都不一样，解析代码要写N套。统一返回格式就是为了解决这个问题：**无论成功还是失败，响应的外层结构永远一致**。

```json
// 统一后的格式：
// 成功
{ "code": 200, "message": "操作成功", "data": { "id": 1, "name": "张三" } }

// 失败
{ "code": 400, "message": "用户名不能为空", "data": null }
```

前端只需写一套解析逻辑：

```javascript
fetch('/api/user').then(res => res.json()).then(result => {
    if (result.code === 200) {
        console.log(result.data);  // 取数据
    } else {
        alert(result.message);     // 显示错误信息
    }
});
```

### 16.2.2 Result<T> 完整实现

创建`com.example.springbootdemo.common.Result`：

```java
package com.example.springbootdemo.common;

import com.fasterxml.jackson.annotation.JsonInclude;
import lombok.Data;

@Data
@JsonInclude(JsonInclude.Include.NON_NULL)  // 为null的字段不序列化
public class Result<T> {

    private int code;
    private String message;
    private T data;

    private Result(int code, String message, T data) {
        this.code = code;
        this.message = message;
        this.data = data;
    }

    public static <T> Result<T> success() {
        return new Result<>(ResultCode.SUCCESS.getCode(),
                ResultCode.SUCCESS.getMessage(), null);
    }

    public static <T> Result<T> success(T data) {
        return new Result<>(ResultCode.SUCCESS.getCode(),
                ResultCode.SUCCESS.getMessage(), data);
    }

    public static <T> Result<T> success(String message, T data) {
        return new Result<>(ResultCode.SUCCESS.getCode(), message, data);
    }

    public static <T> Result<T> error(ResultCode resultCode) {
        return new Result<>(resultCode.getCode(), resultCode.getMessage(), null);
    }

    public static <T> Result<T> error(int code, String message) {
        return new Result<>(code, message, null);
    }

    public static <T> Result<T> error(ResultCode resultCode, String message) {
        return new Result<>(resultCode.getCode(), message, null);
    }

    public boolean isSuccess() {
        return this.code == ResultCode.SUCCESS.getCode();
    }
}
```

状态码枚举`ResultCode`：

```java
package com.example.springbootdemo.common;

import lombok.Getter;

@Getter
public enum ResultCode {

    SUCCESS(200, "操作成功"),

    BAD_REQUEST(400, "请求参数有误"),
    UNAUTHORIZED(401, "未认证，请先登录"),
    FORBIDDEN(403, "无权限访问"),
    NOT_FOUND(404, "请求的资源不存在"),
    METHOD_NOT_ALLOWED(405, "请求方法不允许"),

    INTERNAL_ERROR(500, "服务器内部错误"),
    SERVICE_UNAVAILABLE(503, "服务暂不可用"),

    PARAM_ERROR(1001, "参数校验失败"),
    USER_NOT_FOUND(1002, "用户不存在"),
    USERNAME_OR_PASSWORD_ERROR(1003, "用户名或密码错误"),
    TOKEN_EXPIRED(1004, "Token已过期"),
    TOKEN_INVALID(1005, "Token无效"),
    DUPLICATE_KEY(1006, "数据重复"),
    DATA_NOT_FOUND(1007, "数据不存在"),
    BUSINESS_ERROR(1008, "业务处理异常");

    private final int code;
    private final String message;

    ResultCode(int code, String message) {
        this.code = code;
        this.message = message;
    }
}
```

**设计要点解读**：

1. **泛型`<T>`**：让data可以承载任意类型的返回数据——`Result<User>`、`Result<List<Employee>>`、`Result<PageInfo<Employee>>`等。

2. **`@JsonInclude(JsonInclude.Include.NON_NULL)`**：当data为null时不序列化该字段，这样成功时返回`{"code":200,"message":"操作成功","data":{...}}`，失败时返回`{"code":400,"message":"参数错误"}`——不会出现`"data":null`这种冗余字段。

3. **构造方法私有**：强制使用静态工厂方法创建，避免`new Result(200, "ok", null)`这种不符合语义的创建方式。

4. **状态码分层**：
   - 2xx：HTTP标准成功码
   - 4xx：HTTP标准客户端错误码
   - 5xx：HTTP标准服务端错误码
   - 1xxx：自定义业务错误码（更精细的错误分类）

### 16.2.3 Controller中使用Result

```java
@RestController
@RequestMapping("/api/employees")
public class EmployeeController {

    @Autowired
    private EmployeeService employeeService;

    @GetMapping("/{id}")
    public Result<Employee> getById(@PathVariable Long id) {
        Employee employee = employeeService.findById(id);
        if (employee == null) {
            return Result.error(ResultCode.USER_NOT_FOUND);
        }
        return Result.success(employee);
    }

    @GetMapping
    public Result<List<Employee>> list() {
        List<Employee> list = employeeService.findAll();
        return Result.success(list);
    }

    @PostMapping
    public Result<Void> add(@RequestBody @Valid EmployeeSaveDTO dto) {
        employeeService.save(dto);
        return Result.success();
    }

    @DeleteMapping("/{id}")
    public Result<Void> delete(@PathVariable Long id) {
        employeeService.deleteById(id);
        return Result.success();
    }
}
```

> 🚨 **坑点：返回类型不一致**
> - 如果你的Controller有的方法返回`Result<User>`，有的返回`User`，有的返回`String`，前端就要写多套解析逻辑
> - **铁律：所有Controller方法必须返回`Result<T>`或其子类型**
> - 全局异常处理返回的也是`Result`（见下一节），保证任何情况下前端都能按统一结构解析

---

## 16.3 全局异常处理 — @RestControllerAdvice

### 16.3.1 为什么需要全局异常处理？

没有全局异常处理时，你的Controller代码可能是这样的：

```java
@GetMapping("/{id}")
public Result<Employee> getById(@PathVariable Long id) {
    try {
        Employee emp = employeeService.findById(id);
        if (emp == null) {
            return Result.error(404, "员工不存在");
        }
        return Result.success(emp);
    } catch (Exception e) {
        log.error("查询员工失败", e);
        return Result.error(500, "服务器内部错误");
    }
}

@PostMapping
public Result<Void> add(@RequestBody Employee employee) {
    try {
        if (employee.getName() == null || employee.getName().isBlank()) {
            return Result.error(400, "姓名不能为空");
        }
        employeeService.save(employee);
        return Result.success();
    } catch (Exception e) {
        log.error("新增员工失败", e);
        return Result.error(500, "服务器内部错误");
    }
}
```

每个方法都要写`try-catch`，充斥着重复的错误处理代码。更糟糕的是：
- 有些异常可能根本不会被catch（比如Spring MVC在请求参数绑定时抛出的异常）
- 如果某个接口忘了try-catch，异常就会直接暴露给前端（带上完整的异常栈信息——**安全风险！**）
- 当需求变化时（比如想在异常时记录日志），需要修改N个Controller中的N个catch块

**全局异常处理的核心思想**：将所有Controller中的异常处理逻辑**抽取到一个地方**，让Controller方法只关注正常流程。

### 16.3.2 三层异常处理架构

这是企业级项目中经过验证的异常处理分层设计：

```
┌─────────────────────────────────────────────┐
│              @RestControllerAdvice           │
│                                              │
│  ┌───────────────────────────────────────┐  │
│  │ 第一层：业务异常 BusinessException      │  │
│  │ → 返回对应的业务错误码和消息            │  │
│  └───────────────────────────────────────┘  │
│  ┌───────────────────────────────────────┐  │
│  │ 第二层：参数校验异常                    │  │
│  │ MethodArgumentNotValidException       │  │
│  │ → 提取字段错误信息，友好提示            │  │
│  └───────────────────────────────────────┘  │
│  ┌───────────────────────────────────────┐  │
│  │ 第三层：兜底异常 Exception              │  │
│  │ → 记录日志，返回统一500错误             │  │
│  │ → 绝不返异常栈给前端！               │  │
│  └───────────────────────────────────────┘  │
└─────────────────────────────────────────────┘
```

### 16.3.3 完整实现

**BusinessException业务异常类**：

```java
package com.example.springbootdemo.common.exception;

import com.example.springbootdemo.common.ResultCode;
import lombok.Getter;

@Getter
public class BusinessException extends RuntimeException {

    private final int code;

    public BusinessException(ResultCode resultCode) {
        super(resultCode.getMessage());
        this.code = resultCode.getCode();
    }

    public BusinessException(ResultCode resultCode, String message) {
        super(message);
        this.code = resultCode.getCode();
    }

    public BusinessException(int code, String message) {
        super(message);
        this.code = code;
    }
}
```

**全局异常处理器**：

```java
package com.example.springbootdemo.common.exception;

import com.example.springbootdemo.common.Result;
import com.example.springbootdemo.common.ResultCode;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.validation.FieldError;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.ResponseStatus;
import org.springframework.web.bind.annotation.RestControllerAdvice;

import java.util.stream.Collectors;

@Slf4j
@RestControllerAdvice
public class GlobalExceptionHandler {

    // ===== 第一层：业务异常 =====
    @ExceptionHandler(BusinessException.class)
    @ResponseStatus(HttpStatus.OK)  // 业务异常状态码用200，错误信息在body里
    public Result<Void> handleBusinessException(BusinessException e) {
        log.warn("业务异常: code={}, message={}", e.getCode(), e.getMessage());
        return Result.error(e.getCode(), e.getMessage());
    }

    // ===== 第二层：参数校验异常 =====
    @ExceptionHandler(MethodArgumentNotValidException.class)
    @ResponseStatus(HttpStatus.BAD_REQUEST)
    public Result<Void> handleValidationException(MethodArgumentNotValidException e) {
        String errorMessage = e.getBindingResult()
                .getFieldErrors()
                .stream()
                .map(fieldError -> fieldError.getField() + ": " + fieldError.getDefaultMessage())
                .collect(Collectors.joining("; "));
        log.warn("参数校验失败: {}", errorMessage);
        return Result.error(ResultCode.PARAM_ERROR.getCode(), errorMessage);
    }

    // ===== 第三层：兜底异常 =====
    @ExceptionHandler(Exception.class)
    @ResponseStatus(HttpStatus.INTERNAL_SERVER_ERROR)
    public Result<Void> handleException(Exception e) {
        log.error("系统异常: ", e);  // 记录完整异常栈到日志
        return Result.error(ResultCode.INTERNAL_ERROR);
    }
}
```

### 16.3.4 关键设计解读

**为什么@ResponseStatus不统一用500？**

- **业务异常**（BusinessException）：这是预期内的错误（用户不存在、余额不足等），程序逻辑是正常的，只是业务规则不满足。HTTP状态码200，具体错误通过body中的code区分。
- **参数校验异常**：客户端传了非法参数，HTTP 400 Bad Request。
- **兜底异常**：意料之外的错误（NPE、数据库连接断开等），HTTP 500 Internal Server Error。

> 🚨 **致命坑点：不要将异常栈返回给前端！**
> 
> ```java
> // ❌ 绝对禁止！异常栈暴露给前端 = 安全漏洞！
> @ExceptionHandler(Exception.class)
> public Result<String> handleException(Exception e) {
>     StringWriter sw = new StringWriter();
>     e.printStackTrace(new PrintWriter(sw));
>     return Result.error(500, sw.toString());
>     // 前端会看到：java.lang.NullPointerException
>     //     at com.example.service.EmployeeService.findById(EmployeeService.java:42)
>     //     ...
>     // 黑客能从中推断出你的代码结构、包名、甚至数据库表名！
> }
> ```
> 
> **正确做法**：异常栈只记录到日志（`log.error("系统异常: ", e)`），返回给前端的是统一友好的提示信息"服务器内部错误"。

> 🚨 **坑点：ExceptionHandler优先级 — 具体异常 > 父类异常**
> 
> ```java
> @ExceptionHandler(RuntimeException.class)
> public Result<Void> handleRuntime(RuntimeException e) { ... }
> 
> @ExceptionHandler(Exception.class)
> public Result<Void> handleException(Exception e) { ... }
> ```
> 
> 当抛出一个`NullPointerException`（继承自`RuntimeException`，再继承自`Exception`）时：
> - Spring会匹配**最具体的**处理器：`handleRuntime`（因为`NullPointerException`是`RuntimeException`的子类）
> - 如果只有`handleException`，才会走它
> - **两个处理器都匹配时，Spring选择更具体的那个（子类优先于父类）**

### 16.3.5 异常信息国际化简介

当你的系统需要支持多语言时，错误信息不能硬编码中文。Spring提供了`MessageSource`机制：

```java
@Slf4j
@RestControllerAdvice
public class GlobalExceptionHandler {

    @Autowired
    private MessageSource messageSource;

    @ExceptionHandler(BusinessException.class)
    public Result<Void> handleBusinessException(BusinessException e, Locale locale) {
        // 根据code和locale从messages_zh_CN.properties获取对应语言的错误信息
        String message = messageSource.getMessage("error." + e.getCode(),
                null, e.getMessage(), locale);
        return Result.error(e.getCode(), message);
    }
}
```

`src/main/resources/messages_zh_CN.properties`：

```properties
error.1002=用户不存在
error.1003=用户名或密码错误
error.1004=Token已过期，请重新登录
```

`src/main/resources/messages_en_US.properties`：

```properties
error.1002=User not found
error.1003=Invalid username or password
error.1004=Token expired, please login again
```

`application.yml`配置basename：

```yaml
spring:
  messages:
    basename: messages
    encoding: UTF-8
```

### 16.3.6 Service层如何使用

```java
@Service
public class EmployeeService {

    @Autowired
    private EmployeeMapper employeeMapper;

    public Employee findById(Long id) {
        return employeeMapper.selectById(id);
    }

    public void validateAndSave(EmployeeSaveDTO dto) {
        // 业务校验：用户名不能重复
        Employee exist = employeeMapper.selectByName(dto.getName());
        if (exist != null) {
            throw new BusinessException(ResultCode.DUPLICATE_KEY, "员工姓名[" + dto.getName() + "]已存在");
        }
        // ... 保存逻辑
    }

    public void deleteById(Long id) {
        Employee employee = employeeMapper.selectById(id);
        if (employee == null) {
            throw new BusinessException(ResultCode.DATA_NOT_FOUND, "员工不存在，ID: " + id);
        }
        employeeMapper.deleteById(id);
    }
}
```

**体会**：Service层遇到业务不满足条件时，直接`throw new BusinessException(...)`，不用返回错误码或null。Controller也不用try-catch——全局异常处理器会自动捕获并返回规范的Result。

---

## 16.4 参数校验 — JSR-380 Bean Validation

### 16.4.1 校验注解速查

Spring Boot 3.x内置了`spring-boot-starter-validation`中的Hibernate Validator（JSR-380的实现）。核心注解：

| 注解 | 适用类型 | 说明 | 示例 |
|------|---------|------|------|
| `@NotNull` | 任意类型 | 不能为null（但可以是空字符串） | `@NotNull String name` — `""` 可以通过 |
| `@NotEmpty` | String/Collection/Map/Array | 不能为null且不能为空（size>0） | `@NotEmpty String name` — `""` 不通过 |
| `@NotBlank` | String | 不能为null且trim后长度>0 | `@NotBlank String name` — `" "` 不通过 |
| `@Size(min,max)` | String/Collection/Map/Array | 长度/大小范围 | `@Size(min=2, max=20) String name` |
| `@Min(value)` | 数值 | 最小值（含） | `@Min(18) Integer age` |
| `@Max(value)` | 数值 | 最大值（含） | `@Max(65) Integer age` |
| `@Email` | String | 邮箱格式 | `@Email String email` |
| `@Pattern(regexp)` | String | 正则匹配 | `@Pattern(regexp="^1[3-9]\\d{9}$") String phone` |
| `@Positive` | 数值 | 正数（>0） | `@Positive BigDecimal salary` |
| `@PositiveOrZero` | 数值 | 非负数（>=0） | `@PositiveOrZero int count` |
| `@Negative` | 数值 | 负数（<0） | `@Negative int delta` |
| `@Past` | 日期 | 过去的日期 | `@Past LocalDate birthday` |
| `@Future` | 日期 | 将来的日期 | `@Future LocalDate deadline` |
| `@Digits(integer,fraction)` | 数值 | 整数位和小数位 | `@Digits(integer=10, fraction=2) BigDecimal amount` |
| `@Valid` | 对象引用 | 级联校验嵌套对象 | 见16.4.5 |

**@NotNull / @NotEmpty / @NotBlank 的区别**（这是面试高频问题）：

```
值          @NotNull    @NotEmpty   @NotBlank
null          ❌          ❌           ❌
""            ✅          ❌           ❌
"   "         ✅          ✅           ❌
"abc"         ✅          ✅           ✅
```

直观记忆：
- `@NotNull`：只要不是`null`就行
- `@NotEmpty`：不能是null，而且长度不能为0
- `@NotBlank`：不能是null，而且去掉首尾空格后长度不能为0

### 16.4.2 基本校验示例

创建DTO类封装请求参数：

```java
package com.example.springbootdemo.dto;

import jakarta.validation.constraints.*;
import lombok.Data;
import java.math.BigDecimal;
import java.time.LocalDate;

@Data
public class EmployeeSaveDTO {

    @NotBlank(message = "姓名不能为空")
    @Size(min = 2, max = 20, message = "姓名长度必须在2-20之间")
    private String name;

    @NotNull(message = "年龄不能为空")
    @Min(value = 18, message = "年龄不能小于18岁")
    @Max(value = 65, message = "年龄不能大于65岁")
    private Integer age;

    @NotBlank(message = "部门不能为空")
    private String department;

    @NotNull(message = "薪资不能为空")
    @Positive(message = "薪资必须大于0")
    @Digits(integer = 8, fraction = 2, message = "薪资格式不正确（整数最多8位，小数最多2位）")
    private BigDecimal salary;

    @NotBlank(message = "邮箱不能为空")
    @Email(message = "邮箱格式不正确")
    private String email;

    @Past(message = "入职日期必须是过去的日期")
    private LocalDate hireDate;
}
```

**Controller中启用校验**：

```java
@PostMapping
public Result<Void> add(@RequestBody @Valid EmployeeSaveDTO dto) {
    employeeService.save(dto);
    return Result.success();
}
```

> 🚨 **致命坑点：忘了`@Valid`注解 → 校验全部无效！**
> 
> ```java
> // ❌ 少了@Valid：即使DTO上写了@NotBlank等注解，全部不生效！
> @PostMapping
> public Result<Void> add(@RequestBody EmployeeSaveDTO dto) {
>     // dto.getName() 可能是 "" 或 null，不会触发校验！
> }
> ```
> 
> `@Valid`是校验的触发器——它告诉Spring MVC"请在绑定参数之后校验这个对象"。没有它，DTO上的所有校验注解只是"装饰品"。

### 16.4.3 校验失败的处理方式

**方式1：BindingResult手动处理**（繁琐，不推荐）

```java
@PostMapping
public Result<Void> add(@RequestBody @Valid EmployeeSaveDTO dto, BindingResult bindingResult) {
    if (bindingResult.hasErrors()) {
        List<String> errors = bindingResult.getFieldErrors()
                .stream()
                .map(e -> e.getField() + ": " + e.getDefaultMessage())
                .collect(Collectors.toList());
        return Result.error(400, String.join("; ", errors));
    }
    employeeService.save(dto);
    return Result.success();
}
```

**方式2：全局异常处理器统一处理**（推荐！）

校验失败时Spring MVC会抛出`MethodArgumentNotValidException`，我们已经在16.3.3节的全局异常处理器中处理了它——提取字段错误信息，返回友好的提示。**Controller无需任何额外的异常处理代码。**

### 16.4.4 @RequestParam / @PathVariable 的校验

> 🚨 **坑点：`@RequestParam`参数的校验需要在类上加`@Validated`**

```java
@RestController
@RequestMapping("/api/employees")
@Validated  // ← 类上必须加这个！
public class EmployeeController {

    @GetMapping("/{id}")
    public Result<Employee> getById(
            @PathVariable @Min(value = 1, message = "ID必须大于0") Long id) {
        // ...
    }

    @GetMapping("/search")
    public Result<List<Employee>> search(
            @RequestParam @NotBlank(message = "关键字不能为空") String keyword) {
        // ...
    }
}
```

**为什么**？`@Valid`用于校验方法参数中的**对象**（如`@RequestBody`中的DTO），而`@Validated`用于校验**方法参数本身**（如`@RequestParam`、`@PathVariable`）。`@Validated`是Spring提供的增强版校验注解，需要在类上加才能激活方法级的参数校验。

> 校验`@RequestParam`失败时抛出的异常是`ConstraintViolationException`，不是`MethodArgumentNotValidException`。所以你还需要在全局异常处理器中添加对它的处理：
> 
> ```java
> @ExceptionHandler(ConstraintViolationException.class)
> @ResponseStatus(HttpStatus.BAD_REQUEST)
> public Result<Void> handleConstraintViolation(ConstraintViolationException e) {
>     String message = e.getConstraintViolations().stream()
>             .map(v -> v.getPropertyPath() + ": " + v.getMessage())
>             .collect(Collectors.joining("; "));
>     return Result.error(ResultCode.PARAM_ERROR.getCode(), message);
> }
> ```

### 16.4.5 嵌套校验 — @Valid级联

当DTO中包含另一个需要校验的对象时：

```java
@Data
public class DepartmentSaveDTO {
    @NotBlank(message = "部门名称不能为空")
    private String name;

    @NotNull(message = "部门负责人不能为空")
    @Valid  // ← 必须加 @Valid 才能触发嵌套校验！
    private ManagerInfo manager;
}

@Data
public class ManagerInfo {
    @NotBlank(message = "负责人姓名不能为空")
    private String name;

    @NotBlank(message = "负责人电话不能为空")
    @Pattern(regexp = "^1[3-9]\\d{9}$", message = "手机号格式不正确")
    private String phone;
}
```

没有`@Valid`时，只会检查`manager`是否为null，不会校验`ManagerInfo`内部的字段。

### 16.4.6 分组校验

当同一个DTO在不同场景需要不同的校验规则时（如新增时需要ID为空，更新时需要ID不为空）：

```java
// 定义分组接口
public interface AddGroup {}
public interface UpdateGroup {}

@Data
public class EmployeeSaveDTO {
    @Null(groups = AddGroup.class, message = "新增时ID必须为空")
    @NotNull(groups = UpdateGroup.class, message = "更新时ID不能为空")
    private Long id;

    @NotBlank(groups = {AddGroup.class, UpdateGroup.class})
    private String name;

    // ...其他字段
}
```

Controller中使用（注意这里用`@Validated`而不是`@Valid`，因为`@Valid`不支持分组）：

```java
@PostMapping
public Result<Void> add(@RequestBody @Validated(AddGroup.class) EmployeeSaveDTO dto) {
    // ...
}

@PutMapping
public Result<Void> update(@RequestBody @Validated(UpdateGroup.class) EmployeeSaveDTO dto) {
    // ...
}
```

### 16.4.7 自定义校验注解（三步走）

当内置注解不满足需求时，比如校验"电话号码"（支持座机和手机）：

**第1步：定义注解**

```java
package com.example.springbootdemo.common.validation;

import jakarta.validation.Constraint;
import jakarta.validation.Payload;
import java.lang.annotation.*;

@Documented
@Constraint(validatedBy = {PhoneValidator.class})  // 指定校验器
@Target({ElementType.FIELD})
@Retention(RetentionPolicy.RUNTIME)
public @interface Phone {

    String message() default "电话号码格式不正确";

    Class<?>[] groups() default {};

    Class<? extends Payload>[] payload() default {};
}
```

**第2步：编写校验器**

```java
package com.example.springbootdemo.common.validation;

import jakarta.validation.ConstraintValidator;
import jakarta.validation.ConstraintValidatorContext;

public class PhoneValidator implements ConstraintValidator<Phone, String> {

    private static final String PHONE_PATTERN = "^(1[3-9]\\d{9})|(0\\d{2,3}-?\\d{7,8})$";

    @Override
    public boolean isValid(String value, ConstraintValidatorContext context) {
        if (value == null || value.isBlank()) {
            return true;  // null/空字符串由@NotBlank处理，此处不校验
        }
        return value.matches(PHONE_PATTERN);
    }
}
```

**第3步：使用**

```java
@Data
public class EmployeeSaveDTO {
    @Phone(message = "联系电话格式不正确")
    private String phone;
}
```

---

## 16.5 跨域CORS

### 16.5.1 什么是同源策略？

浏览器的**同源策略（Same-Origin Policy）**规定：当前页面的JavaScript只能访问**同源**的资源。

"同源"必须同时满足三个条件，任何一个不同就算"跨域"：

| 条件 | 页面A | 页面B | 同源？ |
|------|-------|-------|--------|
| 协议 | `http://` | `https://` | ❌ 协议不同 |
| 域名 | `www.a.com` | `api.a.com` | ❌ 域名不同（子域名也不行） |
| 端口 | `localhost:3000` | `localhost:8080` | ❌ 端口不同 |

前后端分离项目中，前端跑在`localhost:5173`（Vite默认），后端跑在`localhost:8080`——**端口不同，属于跨域！**

### 16.5.2 CORS（跨域资源共享）原理

CORS通过服务器在HTTP响应中加入特殊的头，告诉浏览器"允许来自某某域名的请求"。

**简单请求**（GET、POST且Content-Type为表单/纯文本）：浏览器直接发送请求，服务器在响应中加入`Access-Control-Allow-Origin`头。

**非简单请求**（PUT、DELETE、Content-Type为JSON等）：浏览器先发送一个**预检请求（Preflight）**：

```
浏览器: OPTIONS /api/employees HTTP/1.1          ← 预检请求
         Origin: http://localhost:5173
         Access-Control-Request-Method: POST
         Access-Control-Request-Headers: Content-Type

服务器: HTTP/1.1 200 OK                  ← 服务器回应
         Access-Control-Allow-Origin: http://localhost:5173
         Access-Control-Allow-Methods: GET, POST, PUT, DELETE
         Access-Control-Allow-Headers: Content-Type, Authorization
         Access-Control-Max-Age: 3600    ← 预检结果缓存1小时

浏览器: POST /api/employees HTTP/1.1      ← 预检通过后才发正式请求
         实际请求体...
```

**核心响应头**：

| 响应头 | 说明 |
|--------|------|
| `Access-Control-Allow-Origin` | 允许的源（域名） |
| `Access-Control-Allow-Methods` | 允许的HTTP方法 |
| `Access-Control-Allow-Headers` | 允许的请求头 |
| `Access-Control-Allow-Credentials` | 是否允许携带Cookie |
| `Access-Control-Max-Age` | 预检请求缓存时间（秒） |

### 16.5.3 Spring Boot配置CORS的三种方式

**方式1：@CrossOrigin（方法级/类级）**

```java
@RestController
@RequestMapping("/api/employees")
@CrossOrigin(origins = "http://localhost:5173", maxAge = 3600)
public class EmployeeController {
    // 所有方法都允许 http://localhost:5173 跨域访问
}
```

最简单，但不适合全局大量Controller的场景。

**方式2：WebMvcConfigurer全局配置（推荐）**

```java
package com.example.springbootdemo.config;

import org.springframework.context.annotation.Configuration;
import org.springframework.web.servlet.config.annotation.CorsRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

@Configuration
public class WebMvcConfig implements WebMvcConfigurer {

    @Override
    public void addCorsMappings(CorsRegistry registry) {
        registry.addMapping("/api/**")                      // 匹配哪些路径
                .allowedOriginPatterns("*")                 // 允许哪些源
                .allowedMethods("GET", "POST", "PUT", "DELETE", "OPTIONS")
                .allowedHeaders("*")                        // 允许哪些请求头
                .allowCredentials(true)                     // 允许携带Cookie
                .maxAge(3600);                              // 预检缓存时间
    }
}
```

> 🚨 **终极坑点：`allowCredentials(true)` 和 `allowedOrigins("*")` 不能同时使用！**
> 
> 这是CORS规范的规定：如果服务器允许携带凭证（Cookie、Authorization头），就不能用通配符`*`作为允许的源。
> 
> ```java
> // ❌ 启动报错：When allowCredentials is true, allowedOrigins cannot contain "*"
> .allowedOrigins("*")
> .allowCredentials(true)
> 
> // ✅ 解决方案：用 allowedOriginPatterns 替代 allowedOrigins
> .allowedOriginPatterns("*")   // 支持通配符模式匹配
> .allowCredentials(true)
> ```
> 
> `allowedOriginPatterns`是Spring 5.3+提供的方法，它使用通配符**模式**（比如`http://*.example.com`），可以与`allowCredentials(true)`共存。

**方式3：CorsFilter Bean（最灵活，配合Spring Security使用）**

当项目集成了Spring Security时，方式2的`WebMvcConfigurer`配置可能在Security过滤器链之前不生效（Security拦截了OPTIONS请求）。此时需要`CorsFilter`：

```java
@Configuration
public class CorsConfig {

    @Bean
    public CorsFilter corsFilter() {
        CorsConfiguration config = new CorsConfiguration();
        config.addAllowedOriginPattern("*");
        config.addAllowedMethod("*");
        config.addAllowedHeader("*");
        config.setAllowCredentials(true);
        config.setMaxAge(3600L);

        UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
        source.registerCorsConfiguration("/api/**", config);
        return new CorsFilter(source);
    }
}
```

> 🚨 **坑点：OPTIONS预检被Spring Security拦截 → 返回403**
> 
> 如果你集成了Spring Security，默认它会拦截所有请求包括OPTIONS。在Security配置中必须显式放行OPTIONS：
> 
> ```java
> @Bean
> public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
>     http
>         .cors(cors -> cors.configurationSource(corsConfigurationSource()))  // 使用CorsFilter
>         .authorizeHttpRequests(auth -> auth
>             .requestMatchers(HttpMethod.OPTIONS, "/**").permitAll()  // 放行OPTIONS
>             .anyRequest().authenticated()
>         );
>     return http.build();
> }
> ```

---

## 16.6 文件上传下载

### 16.6.1 文件上传

**application.yml配置上传限制**：

```yaml
spring:
  servlet:
    multipart:
      max-file-size: 10MB        # 单个文件最大大小
      max-request-size: 50MB     # 整个请求最大大小（多个文件时）
```

**Controller实现**：

```java
@RestController
@RequestMapping("/api/files")
@Slf4j
public class FileController {

    private static final String UPLOAD_DIR = "uploads/";

    @PostMapping("/upload")
    public Result<String> upload(@RequestParam("file") MultipartFile file) {
        if (file.isEmpty()) {
            return Result.error(400, "文件不能为空");
        }

        // 获取原始文件名
        String originalFilename = file.getOriginalFilename();
        // 获取文件后缀
        String suffix = originalFilename != null
                ? originalFilename.substring(originalFilename.lastIndexOf("."))
                : "";

        // UUID重命名 → 防止文件覆盖
        String newFilename = UUID.randomUUID().toString() + suffix;

        // 确保上传目录存在
        Path uploadPath = Paths.get(UPLOAD_DIR);
        if (!Files.exists(uploadPath)) {
            Files.createDirectories(uploadPath);
        }

        // 保存文件
        Path filePath = uploadPath.resolve(newFilename);
        file.transferTo(filePath.toFile());

        log.info("文件上传成功: {} -> {}", originalFilename, newFilename);
        return Result.success("文件上传成功", "/files/" + newFilename);
    }
}
```

> 🚨 **致命坑点：文件重名覆盖**
> 
> 如果你直接用原始文件名存储，用户A上传`头像.png`，用户B也上传`头像.png`——B的文件会覆盖A的文件！
> 
> **解决方案**：UUID重命名，如`a1b2c3d4-....png`，保证文件名全局唯一。也可以结合业务ID命名：`userId_timestamp.png`。

> 🚨 **安全坑点：上传路径不可放在Web可访问目录**
> 
> ```java
> // ❌ 危险：保存在 static/ 下 → 任何人可通过URL直接访问！
> Path uploadPath = Paths.get("src/main/resources/static/uploads/");
> 
> // ✅ 安全：保存在项目外部的独立目录
> Path uploadPath = Paths.get("/opt/app/uploads/");
> ```
> 
> 如果上传目录在`static/`下，攻击者上传一个JSP文件，然后通过URL访问，它可能被Tomcat当作JSP执行（如果Tomcat配置了JSP支持）——**这是严重的安全漏洞！**

### 16.6.2 文件下载

```java
@GetMapping("/download/{filename}")
public ResponseEntity<InputStreamResource> download(@PathVariable String filename) {
    Path filePath = Paths.get(UPLOAD_DIR).resolve(filename).normalize();

    if (!Files.exists(filePath)) {
        return ResponseEntity.notFound().build();
    }

    try {
        // 设置响应头
        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_OCTET_STREAM);
        headers.setContentDisposition(ContentDisposition.attachment()
                .filename(filename, StandardCharsets.UTF_8)
                .build());

        InputStreamResource resource = new InputStreamResource(
                new FileInputStream(filePath.toFile()));

        return ResponseEntity.ok()
                .headers(headers)
                .contentLength(Files.size(filePath))
                .body(resource);

    } catch (IOException e) {
        log.error("文件下载失败: {}", filename, e);
        return ResponseEntity.internalServerError().build();
    }
}
```

> **`Path.normalize()`的安全作用**：防止路径遍历攻击。比如用户传`../../../etc/passwd`，`normalize()`会将其规范化为安全路径。

---

## 16.7 拦截器（Interceptor）实战

### 16.7.1 三步编写拦截器

**第1步：定义拦截器类**

```java
package com.example.springbootdemo.interceptor;

import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;
import org.springframework.web.servlet.HandlerInterceptor;

@Slf4j
public class LoginInterceptor implements HandlerInterceptor {

    @Override
    public boolean preHandle(HttpServletRequest request, HttpServletResponse response,
                             Object handler) throws Exception {
        String token = request.getHeader("Authorization");

        if (token == null || token.isBlank()) {
            log.warn("未携带Token，拦截请求: {} {}", request.getMethod(), request.getRequestURI());

            response.setContentType("application/json;charset=UTF-8");
            response.setStatus(401);
            response.getWriter().write("{\"code\":401,\"message\":\"未登录，请先登录\"}");
            return false;  // 不放行
        }

        // 实际项目中在此验证Token（JWT解析等）
        if (!token.startsWith("Bearer ")) {
            response.setContentType("application/json;charset=UTF-8");
            response.setStatus(401);
            response.getWriter().write("{\"code\":401,\"message\":\"Token格式不正确\"}");
            return false;
        }

        log.info("Token验证通过: {}", request.getRequestURI());
        return true;  // 放行
    }
}
```

**第2步：注册拦截器**

```java
package com.example.springbootdemo.config;

import com.example.springbootdemo.interceptor.LoginInterceptor;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.servlet.config.annotation.InterceptorRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

@Configuration
public class WebMvcConfig implements WebMvcConfigurer {

    @Autowired
    private LoginInterceptor loginInterceptor;  // ★ 通过@Autowired注入

    @Override
    public void addInterceptors(InterceptorRegistry registry) {
        registry.addInterceptor(loginInterceptor)
                .addPathPatterns("/api/**")                    // 拦截哪些路径
                .excludePathPatterns(                          // 排除哪些路径
                        "/api/auth/login",
                        "/api/auth/register",
                        "/files/**",
                        "/error"
                )
                .order(1);  // 多个拦截器时的执行顺序
    }
}
```

**第3步：让拦截器成为Spring Bean**

注意`WebMvcConfig`中通过`@Autowired`注入了`LoginInterceptor`，因此`LoginInterceptor`必须是Spring Bean：

```java
@Configuration
public class InterceptorConfig {

    @Bean
    public LoginInterceptor loginInterceptor() {
        return new LoginInterceptor();
    }
}
```

或者直接在`LoginInterceptor`类上加`@Component`。

### 16.7.2 拦截器中注入Service的坑

> 🚨 **经典坑点：拦截器中注入的@Service可能为null**

如果你的拦截器需要在验证Token时查询数据库（比如根据Token获取用户信息），你可能会这样写：

```java
// ❌ Bug：userService始终为null！
@Component
public class LoginInterceptor implements HandlerInterceptor {
    @Autowired
    private UserService userService;  // null！

    @Override
    public boolean preHandle(...) {
        userService.findByToken(token);  // NullPointerException!
        // ...
    }
}
```

**问题出在哪里？**

```java
// 如果WebMvcConfig是这样写的：
@Configuration
public class WebMvcConfig implements WebMvcConfigurer {
    @Override
    public void addInterceptors(InterceptorRegistry registry) {
        registry.addInterceptor(new LoginInterceptor());  // ← new出来的！
        // 这个new出来的对象不是Spring管理的Bean
        // 所以@Autowired不会生效！
    }
}
```

`new LoginInterceptor()`创建的对象不受Spring管理，`@Autowired`不会被执行。

**解决方案：用@Bean注册拦截器，构造器注入Service**

```java
@Component  // 或 @Configuration 中的 @Bean
public class LoginInterceptor implements HandlerInterceptor {

    private final UserService userService;

    // 构造器注入（确保依赖不为null）
    public LoginInterceptor(UserService userService) {
        this.userService = userService;
    }

    @Override
    public boolean preHandle(...) {
        // userService已经由Spring通过构造器注入了
        User user = userService.findByToken(token);
        // ...
    }
}
```

```java
@Configuration
public class WebMvcConfig implements WebMvcConfigurer {

    @Autowired
    private LoginInterceptor loginInterceptor;  // 从容器中获取（不是new的！）

    @Override
    public void addInterceptors(InterceptorRegistry registry) {
        registry.addInterceptor(loginInterceptor)  // 注入Spring管理的Bean
                .addPathPatterns("/api/**");
    }
}
```

**核心原则**：拦截器必须作为Spring Bean注册（`@Component`或`@Bean`），通过`@Autowired`注入到`WebMvcConfigurer`中使用——永远不要`new LoginInterceptor()`！

### 16.7.3 拦截器 vs 过滤器

| 对比维度 | 拦截器（Interceptor） | 过滤器（Filter） |
|---------|----------------------|-----------------|
| 规范 | Spring MVC | Servlet |
| 执行节点 | DispatcherServlet之后，Controller之前 | DispatcherServlet之前 |
| 能获取Handler | ✅ 可以拿到HandlerMethod | ❌ 不行 |
| 能注入Spring Bean | ✅ 可以（通过@Bean注册） | ✅ 可以（通过@Bean注册） |
| 能控制Controller是否执行 | ✅ `preHandle`返回false | ❌ 只能控制链的传递 |
| 适用场景 | 登录验证、权限检查、日志 | 编码处理、XSS防护、请求包装 |

> **执行顺序**：Filter → DispatcherServlet → Interceptor.preHandle → Controller → Interceptor.afterCompletion

---

## 本章小结

1. **静态资源处理**：Spring Boot内置四个默认静态资源路径，`Controller > 静态资源 > 404`的优先级规则需要牢记。

2. **统一返回格式Result<T>**：通过泛型Result类 + 状态码枚举 + 静态工厂方法，实现前端统一解析。`@JsonInclude(NON_NULL)`避免冗余字段。

3. **三层全局异常处理**：`@RestControllerAdvice` + `@ExceptionHandler`实现业务异常（BusinessException）、参数校验异常（MethodArgumentNotValidException）、兜底异常（Exception）的分层处理。**绝对不要将异常栈返回给前端**。

4. **参数校验**：JSR-380校验注解体系，`@NotNull`/`@NotEmpty`/`@NotBlank`三者的区别是关键。`@Valid`触发校验、`@Validated`支持分组和方法级校验。校验失败由全局异常处理器统一捕获返回。

5. **CORS跨域**：`allowCredentials(true)`与`allowedOrigins("*")`不能同时使用的坑；三种配置方式中`CorsFilter`最灵活（配合Spring Security）。

6. **文件上传下载**：UUID重命名防止文件覆盖；上传路径必须放在Web不可访问的目录外；`Path.normalize()`防路径遍历攻击。

7. **拦截器**：三步走（定义→注册→使用），**拦截器必须作为Spring Bean注册，构造器注入依赖，绝不能`new`出来**——这是初学者最常犯的错误。

> **下一章预告**：第17章将进入数据访问层实战——MyBatis/MyBatis Plus/JPA三种框架与Spring Boot的整合，**事务管理的7种失效场景（每种附可复现代码）**，多数据源配置，Flyway数据库版本管理。并在章末完成**EMS v5：Spring Boot版员工管理系统**——完整的三层架构RESTful API后端。

---

## 思考题

1. 在全局异常处理器中，为什么业务异常（BusinessException）使用HTTP 200而不是HTTP 500？如果改为500会有什么影响？

2. 以下校验规则有什么问题？如果有，请修正：
   ```java
   @NotNull(message = "姓名不能为空")
   @Size(min = 2, max = 20, message = "姓名长度2-20")
   private String name;
   ```

3. 你的拦截器中需要调用Service查询数据库，但是Service始终为null。请分析两种可能的错误原因，并给出修复方案。

4. `@RestControllerAdvice`和`@ControllerAdvice`有什么区别？如果在一个返回页面的项目中（使用Thymeleaf），应该用哪个？

5. 当前端域名有多个（如`http://admin.example.com`和`http://app.example.com`），如何在CORS配置中同时允许所有子域名？（提示：用`allowedOriginPatterns`）

6. 设计一个自定义校验注解`@EnumValue`，用于校验请求参数必须是某个枚举的合法值。比如`@EnumValue(enumClass = GenderEnum.class, message = "性别取值不正确") private String gender;`。请给出注解定义、校验器实现和使用示例。