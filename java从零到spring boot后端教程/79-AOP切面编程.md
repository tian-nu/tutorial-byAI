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

## 77.5 完整 CRUD Controller（使用 Result + ResponseEntity）

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

**答案提示**：1→B。2→推荐 204 No Content，或约定统一返回 200 + `{code:200, data:null}`。3→`public static Result<Void> error(int code, String message) { return new Result<>(code, message, null); }`。下一章——Filter 和 Interceptor。</think>

<｜DSML｜tool_calls>
<｜DSML｜invoke name="Write">
<｜DSML｜parameter name="content" string="true"># 79-AOP切面编程

> 💡 古代皇帝的"太监"制度——皇帝批奏折时，太监递笔研墨，但从不参与核心决策。笔墨纸砚的准备、奏折的归档，这些"横切关注点"由太监完成，皇帝只管决策。AOP 就是你的太监总管——在你的业务方法执行前后自动完成日志、事务、权限校验等杂活，而你的业务代码干干净净，一行杂活代码都不留。

---

## 本章目标
- 理解 AOP 的核心概念：Aspect、Pointcut、Advice
- 掌握五种通知类型
- 写出可用的切点表达式（execution 语法）
- 实战：日志切面记录方法执行时间
- 彻底分清 Filter / Interceptor / AOP 三者的界限

---

## 79.1 AOP 依赖与启用

Spring Boot 中 AOP 已集成在 `spring-boot-starter-aop` 中：

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-aop</artifactId>
</dependency>
```

Spring Boot 自动配置默认启用 AOP，无需手动加 `@EnableAspectJAutoProxy`。

---

## 79.2 五种 Advice（通知）类型

| Advice 类型 | 注解 | 执行时机 | 典型用途 |
|-------------|------|----------|----------|
| 前置通知 | `@Before` | 目标方法执行前 | 权限校验、参数日志 |
| 后置通知 | `@After` | 目标方法执行后（无论成功或异常） | 资源释放 |
| 返回通知 | `@AfterReturning` | 目标方法正常返回后 | 缓存结果、返回值日志 |
| 异常通知 | `@AfterThrowing` | 目标方法抛出异常后 | 异常告警、错误日志 |
| 环绕通知 | `@Around` | 包围目标方法，最强大 | 性能计时、事务、重试 |

执行顺序：

```
@Around（前半段）→ @Before → 目标方法执行
→ @AfterReturning（正常）或 @AfterThrowing（异常）
→ @After（无论如何）→ @Around（后半段）
```

---

## 79.3 切点表达式——execution 语法

最常用的 `execution` 表达式：

```
execution(修饰符? 返回类型 包名.类名.方法名(参数列表))
```

```java
// 切入 com.example.demo.service 包下所有类的所有方法
@Pointcut("execution(* com.example.demo.service.*.*(..))")
public void serviceLayer() {}

// 切入所有 find 开头的方法
@Pointcut("execution(* com.example.demo..*.find*(..))")
public void findMethods() {}

// 组合多个切点
@Pointcut("serviceLayer() && !findMethods()")
public void serviceButNotFind() {}
```

`..` 的含义：
- 在包路径中：`com.example..service.*` = "com.example 及其所有子包下的 service 包"
- 在参数列表中：`(..)` = "任意参数"

---

## 79.4 实战：日志切面——记录方法执行时间

### 自定义注解

```java
@Target(ElementType.METHOD)
@Retention(RetentionPolicy.RUNTIME)
public @interface LogExecutionTime {
}
```

### 切面类

```java
@Slf4j
@Aspect
@Component
public class LoggingAspect {

    @Pointcut("@annotation(com.example.demo.annotation.LogExecutionTime)")
    public void logExecutionTimeAnnotation() {}

    @Pointcut("execution(* com.example.demo.service.*.*(..))")
    public void serviceLayer() {}

    @Around("logExecutionTimeAnnotation() || serviceLayer()")
    public Object logAround(ProceedingJoinPoint joinPoint) throws Throwable {
        String className = joinPoint.getSignature().getDeclaringTypeName();
        String methodName = joinPoint.getSignature().getName();

        log.info("→ 调用 {}.{}()", className, methodName);
        long start = System.currentTimeMillis();

        Object result = joinPoint.proceed();  // 执行目标方法

        long elapsed = System.currentTimeMillis() - start;
        log.info("← 返回 {}.{}() 耗时: {}ms", className, methodName, elapsed);
        return result;
    }
}
```

---

## 79.5 Filter / Interceptor / AOP —— 终极对比

| 维度 | Filter | Interceptor | AOP |
|------|--------|-------------|-----|
| **所处层级** | Servlet 容器层 | Spring MVC 层 | Spring 业务方法层 |
| **拦截对象** | HTTP 请求 | Controller 方法 | 任意 Spring Bean 的方法 |
| **能否拿到 HTTP 请求/响应** | ✅ 原生 | ✅ 原生 | ❌（需手动从 RequestContextHolder 获取） |
| **能否拿到方法参数** | ❌ | ✅ | ✅（JoinPoint.getArgs()） |
| **能否修改方法参数/返回值** | ❌ | ❌ | ✅（@Around 可修改） |
| **能否注入 Spring Bean** | 需 DelegatingFilterProxy | ✅ 直接注入 | ✅ 直接注入 |
| **精细控制粒度** | 粗（URL 级别） | 中（Controller 方法级） | 细（任意方法级，支持参数类型过滤） |
| **典型用途** | 编码设置、CORS、XSS 防御 | 认证鉴权、操作日志 | 缓存、事务、性能监控、重试 |

> 🤔 想多一点：Filter 运作在"酒店大堂"——你还没进门，只查身份证（request）。Interceptor 运作在"客房走廊"——知道你去哪个房间（Controller），但不能进房间改东西。AOP 运作在"房间里面"——可以帮你倒水递毛巾（改参数/返回值），也可以让你换房间（改执行路径）。

---

## 79.6 AOP 的底层原理——JDK 动态代理 vs CGLIB

Spring AOP 通过**代理模式**实现：

| | JDK 动态代理 | CGLIB 代理 |
|------|------|------|
| 条件 | 目标类必须实现接口 | 目标类可以没有接口 |
| 代理的是 | 接口 | 子类 |
| 限制 | 只能调用接口中定义的方法 | final 类和方法不能被代理 |
| Spring Boot 默认 | 有接口时优先 | 2.x+ 默认 CGLIB |

---

## 79.7 AOP 的陷阱——同类内部方法调用

```java
@Service
public class UserService {

    @LogExecutionTime
    public void methodA() {
        System.out.println("A 执行");
        this.methodB();  // ← 直接调用，不经过代理！
    }

    @LogExecutionTime
    public void methodB() {
        System.out.println("B 执行");
    }
}
```

`methodB` 的 `@LogExecutionTime` **不生效**！因为 `this.methodB()` 是 Java 普通调用，绕过了 Spring 代理。

**解决方案一：注入自己**

```java
@Service
public class UserService {
    @Autowired
    private UserService self;

    public void methodA() {
        self.methodB();  // 通过代理调用
    }
}
```

**解决方案二：拆分到不同的 Bean**

```java
@Service
public class UserServiceA {
    @Autowired
    private UserServiceB userServiceB;

    public void methodA() {
        userServiceB.methodB();  // 跨 Bean 调用，走代理
    }
}
```

---

## 79.8 小结

| 知识点 | 核心内容 |
|--------|----------|
| @Aspect | 声明切面类 |
| @Pointcut | 定义切点，execution 表达式 |
| @Around | 环绕通知，最强大 |
| Filter 层面 | Servlet 容器层，处理 HTTP 请求/响应 |
| Interceptor 层面 | Spring MVC 层，处理 Controller 方法 |
| AOP 层面 | 业务方法层，处理任意 Bean 方法 |
| 同类内部调用 | 绕过代理，AOP 失效的经典陷阱 |

---

## 79.9 自测题

**1. 在以下场景中选择合适的工具（Filter / Interceptor / AOP）：**

A. 记录所有 `/api/*` 请求的响应时间  
B. 对所有 Service 层方法做权限校验  
C. 给所有入参实现自动 trim() 去除前后空格  
D. 设置所有请求的 UTF-8 编码  

**2. 阅读以下代码，`methodB` 上的 `@Transactional` 会生效吗？为什么？**

```java
@Service
public class OrderService {
    @Transactional
    public void methodA() {
        this.methodB();
    }
    @Transactional(propagation = Propagation.REQUIRES_NEW)
    public void methodB() { }
}
```

**3. `execution(* com.example..service.*.save*(..))` 的含义是什么？**

---

**答案提示**：1→A: Filter/Interceptor 均可；B: AOP；C: AOP（@Around）；D: Filter。2→不会，同类内部调用绕过代理。3→匹配 com.example 及其任意子包下 service 包中任意类，所有以 save 开头的方法。下一章——全局异常处理。