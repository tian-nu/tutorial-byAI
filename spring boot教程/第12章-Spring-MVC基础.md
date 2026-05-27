# 第12章：Spring MVC基础

## 本章目标

学完本章你将能够：

- 回顾MVC架构三层职责，理解数据在Model/View/Controller之间的流转
- 画出DispatcherServlet处理请求的完整流程，理解Spring MVC的核心组件分工
- 区分@Controller与@RestController，掌握请求映射注解体系
- 熟练使用@RequestParam/@PathVariable/@RequestBody完成请求参数绑定
- 设计统一返回格式Result类，让前端对接更轻松
- 对比拦截器与过滤器的区别，实现登录拦截器实战
- 解决中文乱码问题，理解Spring Boot的默认编码配置
- **完成EMS v3：Spring版员工CRUD**，用IoC管理依赖 + AOP日志 + MVC分层重构

---

## 12.1 MVC架构回顾

### 12.1.1 什么是MVC？

你在第9章已经接触过DAO模式的分层思想：Controller → Service → DAO → DB。那是一个纵向的分层，解决的是"职责分离"的问题。MVC是另一种分层思想，解决的是"用户界面与业务逻辑分离"的问题。

MVC是**Model-View-Controller**的缩写，它把一个应用分成三个核心部分：

```text
┌─────────────────────────────────────────────────────────────┐
│                       MVC 三层职责                           │
├───────────────┬───────────────────┬─────────────────────────┤
│               │                   │                         │
│   Controller  │      Model        │        View             │
│   (调度员)     │    (数据+逻辑)     │      (展示层)            │
│               │                   │                         │
│  接收请求      │  业务数据          │  展示数据                │
│  调用业务      │  业务逻辑          │  用户交互                │
│  选择视图      │  数据验证          │  不含业务逻辑            │
│               │                   │                         │
├───────────────┼───────────────────┼─────────────────────────┤
│  "该找谁处理"  │  "怎么处理"        │  "怎么展示"              │
└───────────────┴───────────────────┴─────────────────────────┘
```

用一个餐厅来类比：

- **Controller = 前台服务员**：接待客人，记录点单，把需求转达后厨，最后把菜品端给客人。服务员不炒菜也不吃菜，只负责"调度"。
- **Model = 后厨**：根据点单炒菜，处理食材（数据），执行烹饪逻辑（业务规则）。后厨不直接面对客人。
- **View = 菜品摆盘**：把后厨做好的菜用好看的方式呈现给客人。摆盘不改变菜的味道，只改变呈现方式。

### 12.1.2 MVC数据流

一个完整的请求在MVC中的流转过程：

```text
用户操作(点击按钮/输入URL)
        │
        ▼
  ┌─────────────┐
  │ Controller  │  ① 接收请求，提取参数
  └──────┬──────┘
         │ ② 调用Model处理业务
         ▼
  ┌─────────────┐
  │   Model     │  ③ 执行业务逻辑，返回数据
  └──────┬──────┘
         │ ④ 返回处理结果
         ▼
  ┌─────────────┐
  │    View     │  ⑤ 用数据渲染视图
  └──────┬──────┘
         │ ⑥ 返回响应
         ▼
    用户看到页面
```

### 12.1.3 为什么前后端分离时代还要学MVC？

你可能会问：现在都是前后端分离了，前端用Vue/React，后端只返回JSON，还需要MVC吗？

答案是：**需要，但View的角色变了。**

- **传统MVC**：View是服务器渲染的HTML页面（JSP、Thymeleaf）
- **前后端分离MVC**：View是前端框架（Vue/React），Controller返回JSON数据而非HTML页面

Spring MVC完美支持这两种模式：用`@Controller`返回视图名，用`@RestController`返回JSON数据。本章重点讲解后者——因为这是现代开发的主流。

---

## 12.2 Spring MVC请求流程

### 12.2.1 DispatcherServlet — 万物入口

Spring MVC的核心是一个Servlet：**DispatcherServlet**。它是整个请求处理链的"总指挥"，所有HTTP请求都必须经过它。

你不需要自己配置DispatcherServlet——Spring Boot已经自动帮你配好了。但理解它的工作流程，是排查Web问题的基本功。

用一个类比来理解DispatcherServlet：

> 想象一个大型医院的导诊台。每个病人进来后，导诊台不治病，但负责：挂号→分诊到对应科室→安排医生→把处方和诊断结果整理好→告诉病人去哪取药。DispatcherServlet就是这个导诊台。

### 12.2.2 完整请求流程（分步ASCII图）

下面是一个HTTP请求从进入到响应的完整流程，每一步都标注了参与的核心组件：

```text
                    HTTP请求: GET /api/employees/1
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│  Step 1: DispatcherServlet 接收请求                               │
│  "我是总指挥，所有请求先到我这里"                                    │
└──────────────────────────┬───────────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────────┐
│  Step 2: HandlerMapping 查找处理器                                 │
│  "根据URL /api/employees/1，找到 EmployeeController.findById()"   │
│  返回: HandlerExecutionChain = Handler + Interceptors             │
└──────────────────────────┬───────────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────────┐
│  Step 3: HandlerAdapter 适配执行                                   │
│  "用反射调用 Controller 方法，处理参数绑定"                          │
│  执行拦截器 preHandle() ──→ 返回true才继续                         │
└──────────────────────────┬───────────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────────┐
│  Step 4: Controller 执行业务逻辑                                   │
│  EmployeeController.findById(1)                                   │
│    → 调用 EmployeeService.findById(1)                             │
│      → 调用 EmployeeDao.findById(1)                               │
│    → 返回 Result<Employee>                                        │
└──────────────────────────┬───────────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────────┐
│  Step 5: ViewResolver 或 直接返回JSON                              │
│  如果是 @Controller  → ViewResolver找视图模板 → 渲染HTML           │
│  如果是 @RestController → 跳过ViewResolver → Jackson序列化JSON     │
└──────────────────────────┬───────────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────────┐
│  Step 6: 执行拦截器 postHandle() 和 afterCompletion()             │
│  DispatcherServlet 返回HTTP响应                                    │
└──────────────────────────────────────────────────────────────────┘
                           │
                           ▼
                    HTTP响应: 200 OK
                    { "code":200, "data":{...} }
```

### 12.2.3 核心组件逐一解释

| 组件 | 职责 | 类比 |
|------|------|------|
| **DispatcherServlet** | 前端控制器，统一接收请求，协调各组件 | 医院导诊台 |
| **HandlerMapping** | 根据URL找到对应的Controller方法 | 医院挂号系统（查哪个科室） |
| **HandlerAdapter** | 适配执行Controller方法，处理参数绑定 | 叫号系统（安排具体医生） |
| **Controller** | 业务处理入口，调用Service层 | 医生（诊断+开处方） |
| **ViewResolver** | 根据视图名找到具体模板页面 | 药房（按处方拿药） |
| **Interceptor** | 在Controller前后执行拦截逻辑 | 分诊台（量体温、查预约） |

> 🚨 **坑：DispatcherServlet配置错误 → 404**
>
> 在纯Spring Framework项目中（非Spring Boot），你需要手动在`web.xml`中配置DispatcherServlet的URL映射。如果配置的`<url-pattern>`不对（比如只配了`/api/*`），那么`/api`之外的请求就不会被DispatcherServlet处理，直接返回404。
>
> Spring Boot已经自动配置了DispatcherServlet映射`/`（拦截所有请求），所以你不会遇到这个问题。但如果你手动覆盖了`server.servlet.context-path`或其他配置，就要注意路径匹配了。

### 12.2.4 Spring Boot自动配置了什么？

Spring Boot通过`DispatcherServletAutoConfiguration`自动注册了DispatcherServlet，你不需要写任何XML或Java Config。默认配置如下：

```text
Spring Boot 自动配置清单：
├── DispatcherServlet 映射 "/"（拦截所有请求）
├── 内嵌Tomcat（默认8080端口）
├── Jackson JSON序列化（自动将对象转JSON）
├── CharacterEncodingFilter（UTF-8编码）
├── 静态资源路径（classpath:/static/ 等）
└── 错误处理（/error 默认错误页面）
```

你只需要引入`spring-boot-starter-web`依赖，以上全部自动生效。

---

## 12.3 Controller开发

### 12.3.1 @Controller vs @RestController

这是初学者最容易混淆的一对注解。先看结论：

```text
@RestController = @Controller + @ResponseBody
```

| 注解 | 返回值含义 | 适用场景 |
|------|-----------|---------|
| `@Controller` | 返回**视图名**（HTML页面名） | 传统服务端渲染（JSP/Thymeleaf） |
| `@RestController` | 返回**数据**（JSON/XML） | 前后端分离API |
| `@Controller` + 方法上`@ResponseBody` | 该方法返回数据 | 混合场景（部分页面+部分API） |

用代码对比：

```java
// 方式一：@Controller — 返回视图名
@Controller
public class PageController {

    @GetMapping("/index")
    public String index(Model model) {
        model.addAttribute("name", "张三");
        return "index";  // → ViewResolver找index.html/index.jsp渲染
    }
}

// 方式二：@RestController — 返回JSON数据
@RestController
public class ApiController {

    @GetMapping("/api/user")
    public User getUser() {
        return new User("张三", 25);  // → Jackson自动序列化为JSON
    }
}

// 方式三：@Controller + @ResponseBody — 混合
@Controller
public class MixedController {

    @GetMapping("/index")
    public String index() {
        return "index";  // 返回视图
    }

    @GetMapping("/api/user")
    @ResponseBody       // 这个方法返回JSON而非视图
    public User getUser() {
        return new User("张三", 25);
    }
}
```

> 🚨 **坑：用了@Controller但忘了@ResponseBody → 报404或视图解析错误**
>
> 如果你写的是API接口，返回的是对象，但用了`@Controller`而不是`@RestController`，Spring MVC会尝试把返回值当作视图名去找模板页面。找不到就报404或`CircularViewPathException`。
>
> **简单规则**：写API就用`@RestController`，写页面就用`@Controller`。不要混用。

### 12.3.2 请求映射注解

Spring MVC提供了丰富的请求映射注解，从粗粒度到细粒度：

```java
@RestController
@RequestMapping("/api/employees")  // 类级别：公共路径前缀
public class EmployeeController {

    // 方法级别：完整路径 = /api/employees + "" = /api/employees
    @GetMapping
    public Result<List<Employee>> list() { ... }

    // 完整路径 = /api/employees/{id}
    @GetMapping("/{id}")
    public Result<Employee> findById(@PathVariable Long id) { ... }

    // 完整路径 = /api/employees
    @PostMapping
    public Result<Void> create(@RequestBody Employee employee) { ... }

    // 完整路径 = /api/employees/{id}
    @PutMapping("/{id}")
    public Result<Void> update(@PathVariable Long id,
                               @RequestBody Employee employee) { ... }

    // 完整路径 = /api/employees/{id}
    @DeleteMapping("/{id}")
    public Result<Void> delete(@PathVariable Long id) { ... }
}
```

快捷注解对照表：

| 快捷注解 | 等价于 | HTTP方法 |
|---------|--------|---------|
| `@GetMapping` | `@RequestMapping(method = GET)` | GET |
| `@PostMapping` | `@RequestMapping(method = POST)` | POST |
| `@PutMapping` | `@RequestMapping(method = PUT)` | PUT |
| `@DeleteMapping` | `@RequestMapping(method = DELETE)` | DELETE |
| `@PatchMapping` | `@RequestMapping(method = PATCH)` | PATCH |

> 🚨 **坑：RESTful中GET请求不应该有请求体**
>
> HTTP规范中GET请求是"获取资源"，应该是幂等且安全的。请求体（Request Body）在GET请求中的行为是不确定的——有些HTTP客户端会忽略GET请求的body，有些代理服务器会直接丢弃它。
>
> 如果你需要传复杂查询条件，应该用查询参数（`?name=张三&age=25`）或者改用POST + `@RequestBody`。

> 🚨 **坑：POST和PUT的语义区别**
>
> 按RESTful规范：
> - **POST**：创建资源（非幂等，调两次创建两条）
> - **PUT**：全量更新资源（幂等，调多次结果一样）
>
> 但在实际开发中，很多团队统一用POST处理所有写操作。这不违反什么硬性规则，但**团队内必须统一约定**，否则有人用POST创建、有人用PUT创建，接口风格混乱。

> 🚨 **坑：URL路径的末尾斜杠**
>
> `/api/employees/` 和 `/api/employees` 在Spring MVC中是两个不同的映射。如果你在`@GetMapping`中写了末尾`/`，那么不带`/`的请求会404，反之亦然。
>
> **建议**：统一不加末尾斜杠，在代码规范中明确约定。

---

## 12.4 请求参数绑定

Spring MVC提供了多种注解，将HTTP请求中的数据自动绑定到Java方法的参数上。这是Spring MVC最强大的功能之一——你不需要手动从`HttpServletRequest`中取参数了。

### 12.4.1 @RequestParam — URL查询参数

`@RequestParam`用于绑定URL中`?`后面的查询参数：

```java
@GetMapping("/search")
public Result<List<Employee>> search(
        @RequestParam String name,                          // 必传
        @RequestParam(required = false) String department,  // 可选
        @RequestParam(defaultValue = "1") int page          // 默认值
) {
    // 请求: GET /api/employees/search?name=张三&page=2
    // name="张三", department=null, page=2
    return Result.success(employeeService.search(name, department, page));
}
```

`@RequestParam`三个关键属性：

| 属性 | 默认值 | 说明 |
|------|--------|------|
| `required` | `true` | 是否必传。为true时未传参会抛400 |
| `defaultValue` | 无 | 默认值。设置了defaultValue后required自动变false |
| `name` / `value` | 参数名 | 指定URL参数名（当方法参数名与URL参数名不同时使用） |

> 🚨 **坑：required=true但未传参 → 400 Bad Request**
>
> ```java
> // 请求: GET /api/employees/search  （没传name参数）
> @GetMapping("/search")
> public Result<List<Employee>> search(@RequestParam String name) {
>     // 报错！HTTP 400 Bad Request:
>     // Required request parameter 'name' is not present
> }
> ```
>
> 解决方案：
> - 设为可选：`@RequestParam(required = false)`
> - 给默认值：`@RequestParam(defaultValue = "")`
> - 如果参数确实必传，就让前端修Bug——这个400是正确行为

### 12.4.2 @PathVariable — RESTful路径变量

`@PathVariable`用于绑定URL路径中的变量部分，这是RESTful风格的核心：

```java
// 请求: GET /api/employees/42
@GetMapping("/{id}")
public Result<Employee> findById(@PathVariable Long id) {
    // id = 42
    return Result.success(employeeService.findById(id));
}

// 多个路径变量
// 请求: GET /api/departments/3/employees/42
@GetMapping("/departments/{deptId}/employees/{empId}")
public Result<Employee> findInDepartment(
        @PathVariable Long deptId,
        @PathVariable Long empId
) {
    // deptId=3, empId=42
    return Result.success(employeeService.findInDepartment(deptId, empId));
}

// 路径变量名与方法参数名不同时，需要显式指定
@GetMapping("/{employeeId}")
public Result<Employee> findById(@PathVariable("employeeId") Long id) {
    return Result.success(employeeService.findById(id));
}
```

`@RequestParam` vs `@PathVariable` 对比：

| 对比维度 | @RequestParam | @PathVariable |
|---------|---------------|---------------|
| 数据位置 | URL的`?`后面 | URL路径的一部分 |
| 示例 | `/employees?name=张三` | `/employees/42` |
| RESTful风格 | 非RESTful | RESTful |
| 适用场景 | 过滤、排序、分页 | 标识具体资源 |

### 12.4.3 @RequestBody — JSON请求体

`@RequestBody`用于将请求体中的JSON数据自动反序列化为Java对象。这是前后端分离开发中**最常用**的参数绑定方式：

```java
// 请求: POST /api/employees
// Body: {"name":"张三","age":25,"department":"技术部","salary":15000}
@PostMapping
public Result<Void> create(@RequestBody Employee employee) {
    // Spring MVC自动将JSON转为Employee对象
    // employee.getName() = "张三"
    // employee.getAge() = 25
    employeeService.create(employee);
    return Result.success();
}
```

> 🚨 **坑：POST请求用@RequestParam收不到JSON body → 必须用@RequestBody**
>
> 这是初学者最常犯的错误：
>
> ```java
> // ❌ 错误：@RequestParam只能取URL参数，取不到JSON body
> @PostMapping
> public Result<Void> create(@RequestParam String name,
>                            @RequestParam int age) {
>     // 前端发了JSON body，这里name和age都是null → 400
> }
>
> // ✅ 正确：用@RequestBody接收JSON
> @PostMapping
> public Result<Void> create(@RequestBody Employee employee) {
>     // JSON自动映射到Employee对象
> }
> ```
>
> 记住这个规则：
> - **URL上的参数**（`?key=value`）→ `@RequestParam`
> - **路径中的变量**（`/users/42`）→ `@PathVariable`
> - **请求体中的JSON** → `@RequestBody`

`@RequestBody`依赖Jackson库进行JSON序列化/反序列化。Spring Boot的`spring-boot-starter-web`已经自动引入了Jackson，你不需要额外配置。

### 12.4.4 @RequestHeader — 获取请求头

```java
@GetMapping("/info")
public Result<Map<String, String>> info(
        @RequestHeader("User-Agent") String userAgent,
        @RequestHeader(value = "X-Token", required = false) String token
) {
    Map<String, String> info = new HashMap<>();
    info.put("userAgent", userAgent);
    info.put("token", token);
    return Result.success(info);
}
```

### 12.4.5 @DateTimeFormat — 日期参数

当前端传日期字符串时，Spring MVC默认不知道怎么解析，需要你告诉它格式：

```java
@GetMapping("/by-date")
public Result<List<Employee>> findByHireDate(
        @RequestParam @DateTimeFormat(pattern = "yyyy-MM-dd") LocalDate hireDate
) {
    // 请求: GET /api/employees/by-date?hireDate=2024-01-15
    // hireDate = LocalDate.of(2024, 1, 15)
    return Result.success(employeeService.findByHireDate(hireDate));
}
```

如果前端传的是JSON body中的日期字段，则需要在实体类字段上用`@JsonFormat`：

```java
public class Employee {
    @JsonFormat(pattern = "yyyy-MM-dd")
    private LocalDate hireDate;
}
```

> 🚨 **坑：@DateTimeFormat和@JsonFormat不要搞混**
>
> - `@DateTimeFormat`：用于`@RequestParam`/`@PathVariable`等非JSON参数的日期解析
> - `@JsonFormat`：用于`@RequestBody` JSON反序列化时的日期解析
>
> 两者作用场景不同，用错了日期就解析不了。

### 12.4.6 参数绑定全景图

```text
┌──────────────────────────────────────────────────────────────┐
│                    HTTP请求参数绑定全景                        │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  GET /api/employees?page=1&size=10                           │
│                      │      │                                │
│               @RequestParam @RequestParam                    │
│                                                              │
│  GET /api/employees/42                                       │
│                      │                                       │
│                @PathVariable                                  │
│                                                              │
│  POST /api/employees                                         │
│  Body: {"name":"张三","age":25}                               │
│         │                                                    │
│    @RequestBody → Jackson反序列化 → Employee对象              │
│                                                              │
│  GET /api/employees                                          │
│  Header: X-Token: abc123                                     │
│           │                                                  │
│     @RequestHeader                                           │
│                                                              │
│  GET /api/employees?hireDate=2024-01-15                      │
│                      │                                       │
│        @RequestParam + @DateTimeFormat                       │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

## 12.5 响应处理

### 12.5.1 @ResponseBody与JSON序列化

在`@RestController`中，所有方法的返回值都会经过Jackson自动序列化为JSON。这个过程是：

```text
Java对象 → Jackson ObjectMapper → JSON字符串 → HTTP响应体
```

```java
@RestController
@RequestMapping("/api/employees")
public class EmployeeController {

    @GetMapping("/{id}")
    public Employee findById(@PathVariable Long id) {
        Employee emp = employeeService.findById(id);
        // Jackson自动将emp转为:
        // {"id":1,"name":"张三","age":25,"department":"技术部","salary":15000}
        return emp;
    }
}
```

Jackson常见序列化注解：

```java
public class Employee {
    @JsonProperty("emp_name")       // JSON中字段名为emp_name而非name
    private String name;

    @JsonIgnore                     // 序列化时忽略此字段
    private String password;

    @JsonFormat(pattern = "yyyy-MM-dd")
    private LocalDate hireDate;

    @JsonInclude(JsonInclude.Include.NON_NULL)  // 值为null时不输出此字段
    private String email;
}
```

### 12.5.2 ResponseEntity — 完全控制HTTP响应

当你需要精确控制HTTP状态码、响应头时，用`ResponseEntity<T>`：

```java
@PostMapping
public ResponseEntity<Result<Employee>> create(@RequestBody Employee employee) {
    Employee created = employeeService.create(employee);

    // 设置201 Created状态码 + Location响应头
    URI location = URI.create("/api/employees/" + created.getId());
    return ResponseEntity
            .created(location)                   // 201 Created
            .body(Result.success(created));
}

@PutMapping("/{id}")
public ResponseEntity<Result<Employee>> update(
        @PathVariable Long id,
        @RequestBody Employee employee) {
    Employee updated = employeeService.update(id, employee);
    return ResponseEntity.ok(Result.success(updated));  // 200 OK
}

@DeleteMapping("/{id}")
public ResponseEntity<Void> delete(@PathVariable Long id) {
    employeeService.delete(id);
    return ResponseEntity.noContent().build();  // 204 No Content
}
```

常用HTTP状态码速查：

| 状态码 | 含义 | 使用场景 |
|--------|------|---------|
| 200 OK | 成功 | GET查询、PUT更新 |
| 201 Created | 已创建 | POST新建资源 |
| 204 No Content | 成功但无返回体 | DELETE删除 |
| 400 Bad Request | 请求参数错误 | 参数校验失败 |
| 404 Not Found | 资源不存在 | 查询的ID不存在 |
| 500 Internal Server Error | 服务器内部错误 | 未捕获的异常 |

### 12.5.3 统一返回格式Result类设计

在实际项目中，如果Controller有时返回`Employee`，有时返回`String`，有时返回`Map`，前端开发者会崩溃——他不知道每个接口返回的数据结构是什么。

**最佳实践**：所有接口统一返回同一个包装格式。

```text
标准响应格式：
{
    "code": 200,           // 业务状态码（不是HTTP状态码）
    "message": "success",  // 提示信息
    "data": { ... }        // 实际数据（泛型）
}
```

完整代码实现：

```java
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
        return new Result<>(200, "success", null);
    }

    public static <T> Result<T> success(T data) {
        return new Result<>(200, "success", data);
    }

    public static <T> Result<T> success(String message, T data) {
        return new Result<>(200, message, data);
    }

    public static <T> Result<T> error(int code, String message) {
        return new Result<>(code, message, null);
    }

    public static <T> Result<T> error(String message) {
        return new Result<>(500, message, null);
    }

    public int getCode() { return code; }
    public String getMessage() { return message; }
    public T getData() { return data; }
}
```

配合业务状态码枚举更规范：

```java
public enum ResultCode {

    SUCCESS(200, "操作成功"),
    CREATED(201, "创建成功"),
    BAD_REQUEST(400, "请求参数错误"),
    UNAUTHORIZED(401, "未登录"),
    FORBIDDEN(403, "无权限"),
    NOT_FOUND(404, "资源不存在"),
    INTERNAL_ERROR(500, "服务器内部错误");

    private final int code;
    private final String message;

    ResultCode(int code, String message) {
        this.code = code;
        this.message = message;
    }

    public int getCode() { return code; }
    public String getMessage() { return message; }
}
```

Controller中使用：

```java
@RestController
@RequestMapping("/api/employees")
public class EmployeeController {

    @GetMapping("/{id}")
    public Result<Employee> findById(@PathVariable Long id) {
        Employee emp = employeeService.findById(id);
        if (emp == null) {
            return Result.error(ResultCode.NOT_FOUND.getCode(),
                                ResultCode.NOT_FOUND.getMessage());
        }
        return Result.success(emp);
    }

    @PostMapping
    public Result<Employee> create(@RequestBody Employee employee) {
        Employee created = employeeService.create(employee);
        return Result.success(ResultCode.CREATED.getMessage(), created);
    }
}
```

前端拿到的响应永远是统一格式：

```json
{
    "code": 200,
    "message": "操作成功",
    "data": {
        "id": 1,
        "name": "张三",
        "age": 25,
        "department": "技术部",
        "salary": 15000
    }
}
```

> 🚨 **坑：@RestController中返回null → 响应体为空**
>
> ```java
> @GetMapping("/{id}")
> public Result<Employee> findById(@PathVariable Long id) {
>     return null;  // ❌ HTTP响应体为空字符串，前端JSON.parse报错
> }
> ```
>
> 永远不要在`@RestController`中返回`null`。即使没有数据，也要返回`Result.success()`或`Result.error()`，让前端能正常解析JSON。

---

## 12.6 拦截器与过滤器

### 12.6.1 Filter — Servlet规范层面的拦截

Filter（过滤器）是Servlet规范定义的组件，它在**DispatcherServlet之前**执行，可以修改请求和响应对象。

```text
请求 → Filter链 → DispatcherServlet → Interceptor链 → Controller
响应 ← Filter链 ← DispatcherServlet ← Interceptor链 ← Controller
```

Filter的核心接口是`jakarta.servlet.Filter`（Spring Boot 3.x使用Jakarta EE命名空间）：

```java
@Component
public class LogFilter implements Filter {

    @Override
    public void doFilter(ServletRequest request, ServletResponse response,
                         FilterChain chain) throws IOException, ServletException {
        HttpServletRequest req = (HttpServletRequest) request;
        long start = System.currentTimeMillis();

        System.out.println("[Filter] 请求开始: " + req.getMethod() + " " + req.getRequestURI());

        chain.doFilter(request, response);  // 放行，继续执行后续Filter和Servlet

        long elapsed = System.currentTimeMillis() - start;
        System.out.println("[Filter] 请求结束: 耗时" + elapsed + "ms");
    }
}
```

Filter的特点：
- 可以修改请求参数、请求头、请求体
- 可以修改响应内容
- 可以直接中断请求（不调用`chain.doFilter()`）
- 无法获取具体是哪个Controller方法在处理

### 12.6.2 Interceptor — Spring MVC层面的拦截

Interceptor（拦截器）是Spring MVC定义的组件，它在**DispatcherServlet之后、Controller之前**执行，可以获取Handler的具体信息。

```java
@Component
public class LoginInterceptor implements HandlerInterceptor {

    @Override
    public boolean preHandle(HttpServletRequest request, HttpServletResponse response,
                             Object handler) throws Exception {
        // handler就是具体的Controller方法
        if (handler instanceof HandlerMethod handlerMethod) {
            String methodName = handlerMethod.getMethod().getName();
            System.out.println("[Interceptor] 访问方法: " + methodName);
        }

        // 检查是否登录
        String token = request.getHeader("X-Token");
        if (token == null || token.isEmpty()) {
            response.setStatus(401);
            response.setContentType("application/json;charset=UTF-8");
            response.getWriter().write("{\"code\":401,\"message\":\"请先登录\"}");
            return false;  // 不放行，直接返回
        }

        return true;  // 放行
    }

    @Override
    public void postHandle(HttpServletRequest request, HttpServletResponse response,
                           Object handler, ModelAndView modelAndView) throws Exception {
        // Controller方法执行后、视图渲染前调用
        System.out.println("[Interceptor] postHandle执行");
    }

    @Override
    public void afterCompletion(HttpServletRequest request, HttpServletResponse response,
                                Object handler, Exception ex) throws Exception {
        // 请求完成后调用（无论是否异常），用于资源清理
        if (ex != null) {
            System.out.println("[Interceptor] 请求异常: " + ex.getMessage());
        }
        System.out.println("[Interceptor] afterCompletion执行");
    }
}
```

注册拦截器：

```java
@Configuration
public class WebConfig implements WebMvcConfigurer {

    @Autowired
    private LoginInterceptor loginInterceptor;

    @Override
    public void addInterceptors(InterceptorRegistry registry) {
        registry.addInterceptor(loginInterceptor)
                .addPathPatterns("/api/**")              // 拦截所有/api路径
                .excludePathPatterns("/api/login",       // 放行登录接口
                                     "/api/register");  // 放行注册接口
    }
}
```

### 12.6.3 Filter vs Interceptor 完整对比

```text
┌──────────────────────────────────────────────────────────────────┐
│              请求处理链路中的位置                                   │
│                                                                  │
│  请求 ─→ Filter ─→ Filter ─→ DispatcherServlet                  │
│                                       │                          │
│                                       ├→ Interceptor.preHandle  │
│                                       ├→ Controller方法          │
│                                       ├→ Interceptor.postHandle │
│                                       └→ Interceptor.afterCompletion│
│                                                                  │
│  响应 ←─ Filter ←─ Filter ←─ DispatcherServlet                  │
└──────────────────────────────────────────────────────────────────┘
```

| 对比维度 | Filter | Interceptor |
|---------|--------|-------------|
| **规范** | Servlet规范（Jakarta EE） | Spring MVC规范 |
| **作用范围** | 所有请求（包括静态资源） | 只拦截DispatcherServlet处理的请求 |
| **能否获取Handler信息** | ❌ 不能 | ✅ 能（`HandlerMethod`） |
| **能否修改请求/响应** | ✅ 可以 | ❌ 不方便 |
| **执行时机** | DispatcherServlet之前 | DispatcherServlet之后 |
| **Spring Bean注入** | ✅ 可以（`@Component`） | ✅ 可以（`@Component`） |
| **典型用途** | 编码处理、跨域、压缩 | 登录校验、权限检查、日志记录 |

**选择原则**：
- 需要在Servlet层面操作（编码、CORS、压缩）→ 用Filter
- 需要知道具体Controller方法信息 → 用Interceptor
- 大部分业务拦截场景 → 用Interceptor

> 🚨 **坑：Filter抛异常，Interceptor的afterCompletion也可能不执行**
>
> 执行顺序是`Filter → DispatcherServlet → Interceptor → Controller`。如果Filter中抛出了异常，请求根本不会到达DispatcherServlet，自然也不会触发Interceptor的`afterCompletion()`。
>
> 所以如果你在`afterCompletion()`中做了资源清理（如关闭数据库连接），要确保Filter不会吞掉异常或提前中断请求链。

### 12.6.4 实战：登录拦截器

下面是一个完整的登录拦截器实现，包含Token校验和路径放行：

```java
@Component
public class AuthInterceptor implements HandlerInterceptor {

    @Override
    public boolean preHandle(HttpServletRequest request,
                             HttpServletResponse response,
                             Object handler) throws Exception {
        if (!(handler instanceof HandlerMethod)) {
            return true;
        }

        HandlerMethod handlerMethod = (HandlerMethod) handler;

        SkipAuth skipAuth = handlerMethod.getMethodAnnotation(SkipAuth.class);
        if (skipAuth != null) {
            return true;
        }

        String token = request.getHeader("Authorization");
        if (token == null || !token.startsWith("Bearer ")) {
            sendError(response, 401, "未登录或Token已过期");
            return false;
        }

        String actualToken = token.substring(7);
        if (!validateToken(actualToken)) {
            sendError(response, 401, "Token无效");
            return false;
        }

        return true;
    }

    private boolean validateToken(String token) {
        return token != null && token.length() > 10;
    }

    private void sendError(HttpServletResponse response, int status,
                           String message) throws IOException {
        response.setStatus(status);
        response.setContentType("application/json;charset=UTF-8");
        response.getWriter().write(
            "{\"code\":" + status + ",\"message\":\"" + message + "\"}"
        );
    }
}

@Target(ElementType.METHOD)
@Retention(RetentionPolicy.RUNTIME)
public @interface SkipAuth {
}
```

在Controller中使用`@SkipAuth`放行不需要登录的接口：

```java
@RestController
@RequestMapping("/api")
public class AuthController {

    @PostMapping("/login")
    @SkipAuth
    public Result<String> login(@RequestBody LoginRequest request) {
        String token = authService.login(request.getUsername(), request.getPassword());
        return Result.success(token);
    }
}
```

---

## 12.7 中文乱码问题

中文乱码是Java Web开发的"传统艺能"，几乎每个初学者都会遇到。乱码的根本原因只有一个：**编码和解码使用了不同的字符集**。

### 12.7.1 乱码产生的三种场景

```text
┌─────────────────────────────────────────────────────────────┐
│                    中文乱码三场景                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ① GET请求参数乱码                                          │
│     浏览器编码: UTF-8 → Tomcat解码: ISO-8859-1 → 乱码       │
│     解决: Tomcat URIEncoding="UTF-8"                        │
│                                                             │
│  ② POST请求体乱码                                           │
│     浏览器编码: UTF-8 → Servlet解码: ISO-8859-1 → 乱码      │
│     解决: request.setCharacterEncoding("UTF-8")             │
│           或 CharacterEncodingFilter                        │
│                                                             │
│  ③ 响应乱码                                                 │
│     服务端编码: ISO-8859-1 → 浏览器解码: UTF-8 → 乱码        │
│     解决: response.setContentType("text/html;charset=UTF-8")│
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 12.7.2 Spring Boot的默认UTF-8配置

好消息是：**Spring Boot已经帮你解决了大部分乱码问题。**

Spring Boot自动注册了`CharacterEncodingFilter`，默认编码为UTF-8：

```text
Spring Boot 自动配置:
├── CharacterEncodingFilter（encoding=UTF-8, force=true）
├── Tomcat URIEncoding=UTF-8（内嵌Tomcat默认）
└── Jackson JSON编码=UTF-8
```

所以如果你用的是Spring Boot，通常不会遇到乱码问题。

> 🚨 **坑：GET请求中文乱码 → 检查Tomcat配置**
>
> 如果你没有用Spring Boot的内嵌Tomcat，而是将WAR包部署到外部Tomcat，需要在Tomcat的`server.xml`中配置：
>
> ```xml
> <Connector port="8080" protocol="HTTP/1.1"
>            URIEncoding="UTF-8"        <!-- 加上这行 -->
>            connectionTimeout="20000" />
> ```
>
> Spring Boot内嵌Tomcat默认就是UTF-8，不需要额外配置。

> 🚨 **坑：POST请求中文乱码 → CharacterEncodingFilter**
>
> 在纯Spring Framework项目中（非Spring Boot），你需要在`web.xml`中配置：
>
> ```xml
> <filter>
>     <filter-name>encodingFilter</filter-name>
>     <filter-class>org.springframework.web.filter.CharacterEncodingFilter</filter-class>
>     <init-param>
>         <param-name>encoding</param-name>
>         <param-value>UTF-8</param-value>
>     </init-param>
>     <init-param>
>         <param-name>forceEncoding</param-name>
>         <param-value>true</param-value>
>     </init-param>
> </filter>
> ```
>
> Spring Boot已经自动配置了，你什么都不用做。

### 12.7.3 如果Spring Boot中仍然乱码

如果你在Spring Boot中仍然遇到乱码，检查以下几点：

1. **数据库编码**：确保MySQL数据库、表、列的字符集都是`utf8mb4`（第8章讲过）
2. **数据库连接编码**：JDBC URL中加`characterEncoding=utf8mb4`
3. **IDEA编码**：File → Settings → Editor → File Encodings → 全部设为UTF-8
4. **响应Content-Type**：确保`response.setContentType("application/json;charset=UTF-8")`

```yaml
spring:
  datasource:
    url: jdbc:mysql://localhost:3306/ems?characterEncoding=utf8mb4&serverTimezone=Asia/Shanghai
```

---

## 本章小结

本章我们学习了Spring MVC的核心知识：

1. **MVC架构**：Model负责数据和业务逻辑，View负责展示，Controller负责调度。前后端分离时代View的角色由前端框架承担。

2. **DispatcherServlet请求流程**：所有请求经过DispatcherServlet → HandlerMapping找Controller → HandlerAdapter执行方法 → 返回结果。理解这个流程是排查Web问题的基础。

3. **Controller开发**：`@RestController = @Controller + @ResponseBody`，写API用`@RestController`，写页面用`@Controller`。

4. **请求参数绑定**：URL参数用`@RequestParam`，路径变量用`@PathVariable`，JSON请求体用`@RequestBody`，请求头用`@RequestHeader`，日期用`@DateTimeFormat`/`@JsonFormat`。

5. **统一返回格式**：设计`Result<T>`类，所有接口返回统一格式`{code, message, data}`，前端对接更轻松。

6. **拦截器与过滤器**：Filter在Servlet层面拦截（DispatcherServlet之前），Interceptor在Spring MVC层面拦截（Controller前后）。业务拦截用Interceptor，底层处理用Filter。

7. **中文乱码**：Spring Boot默认UTF-8编码，通常不需要额外配置。如果仍乱码，检查数据库编码、JDBC连接编码、IDE编码。

```text
本章知识脉络：
MVC思想 → DispatcherServlet流程 → Controller注解体系
       → 参数绑定五件套 → 统一返回格式Result
       → 拦截器vs过滤器 → 中文乱码解决
```

---

## 思考题

**1.** `@RestController`和`@Controller`有什么区别？如果一个类标注了`@Controller`但所有方法都标注了`@ResponseBody`，效果等同于`@RestController`吗？

**2.** 以下请求分别应该用哪个注解接收参数？
- `GET /api/employees?name=张三&age=25`
- `GET /api/employees/42`
- `POST /api/employees`，Body为`{"name":"张三","age":25}`

**3.** Filter和Interceptor的执行顺序是什么？如果Filter中抛出异常，Interceptor的`afterCompletion()`还会执行吗？

**4.** 为什么建议所有API接口统一返回`Result<T>`格式？如果某个接口直接返回实体对象，会有什么问题？

**5.** Spring Boot中为什么通常不会遇到中文乱码问题？它自动做了哪些配置？

**6.** 以下代码有什么问题？如何修复？

```java
@RestController
@RequestMapping("/api/employees")
public class EmployeeController {

    @PostMapping
    public Result<Void> create(@RequestParam String name,
                               @RequestParam int age) {
        Employee emp = new Employee(name, age);
        employeeService.create(emp);
        return Result.success();
    }
}
```

---

### 思考题答案

<details>
<summary>点击展开答案</summary>

**第1题**：

`@RestController` = `@Controller` + `@ResponseBody`。`@Controller`标注的类，方法返回值默认被ViewResolver解析为视图名；`@RestController`标注的类，方法返回值直接被Jackson序列化为JSON。

如果一个类标注了`@Controller`但所有方法都标注了`@ResponseBody`，效果**等同于**`@RestController`。`@RestController`本身就是一个组合注解，源码如下：

```java
@Target(ElementType.TYPE)
@Retention(RetentionPolicy.RUNTIME)
@Controller
@ResponseBody
public @interface RestController { ... }
```

所以两者效果完全相同，但`@RestController`写起来更简洁。

**第2题**：

- `GET /api/employees?name=张三&age=25` → `@RequestParam String name, @RequestParam int age`
- `GET /api/employees/42` → `@PathVariable Long id`（路径中的42是路径变量）
- `POST /api/employees`，Body为JSON → `@RequestBody Employee employee`（JSON请求体必须用`@RequestBody`）

**第3题**：

执行顺序：`Filter → DispatcherServlet → Interceptor.preHandle() → Controller → Interceptor.postHandle() → Interceptor.afterCompletion() → DispatcherServlet → Filter`。

如果Filter中抛出异常，请求不会到达DispatcherServlet，因此Interceptor的`afterCompletion()`**不会执行**。这也是为什么资源清理不应该完全依赖`afterCompletion()`——Filter层面的异常会导致它被跳过。

**第4题**：

统一返回`Result<T>`格式的好处：
1. **前端解析一致**：所有接口都是`{code, message, data}`结构，前端只需一套解析逻辑
2. **错误处理统一**：业务错误和系统错误都通过`code`和`message`返回，前端统一拦截处理
3. **接口文档清晰**：响应格式固定，API文档更规范

如果直接返回实体对象，问题包括：
- 成功时返回`Employee`对象，失败时可能返回`String`或`Map`，前端无法统一处理
- 没有业务状态码，前端只能靠HTTP状态码判断成功/失败，不够灵活
- 接口返回null时响应体为空，前端`JSON.parse()`报错

**第5题**：

Spring Boot自动做了以下UTF-8配置：
1. **CharacterEncodingFilter**：自动注册，设置`encoding=UTF-8, forceEncoding=true`，确保请求和响应都使用UTF-8编码
2. **内嵌Tomcat URIEncoding**：默认UTF-8，GET请求的URL参数不会乱码
3. **Jackson JSON编码**：默认UTF-8，JSON序列化不会乱码
4. **响应Content-Type**：自动添加`charset=UTF-8`

这些配置在`spring-boot-autoconfigure`中的`HttpEncodingAutoConfiguration`自动完成。

**第6题**：

问题在于`@PostMapping`方法使用了`@RequestParam`接收参数，但前端发送POST请求时通常会把数据放在请求体（Body）中，而不是URL参数中。

- 如果前端发送的是`application/x-www-form-urlencoded`格式（表单提交），`@RequestParam`可以正常工作
- 如果前端发送的是JSON格式（`application/json`），`@RequestParam`收不到参数，name和age会是null/0

修复方式取决于前端发送的格式：

```java
// 方式一：前端发JSON → 用@RequestBody
@PostMapping
public Result<Void> create(@RequestBody Employee employee) {
    employeeService.create(employee);
    return Result.success();
}

// 方式二：前端发表单格式 → @RequestParam可以，但推荐用对象接收
@PostMapping
public Result<Void> create(Employee employee) {  // 不加注解，Spring MVC自动绑定表单参数
    employeeService.create(employee);
    return Result.success();
}
```

前后端分离项目中，推荐方式一（`@RequestBody`接收JSON）。

</details>

---

## EMS v3：Spring版员工CRUD

经过第10-12章的学习，我们终于可以把Spring的三大核心武器——**IoC（依赖管理）+ AOP（日志切面）+ MVC（Web分层）**——整合起来，重构EMS员工管理系统。

### v2 → v3 升级对比

| 对比维度 | EMS v2（第9章） | EMS v3（本章） |
|---------|----------------|----------------|
| 依赖管理 | 手动new对象 | Spring IoC容器管理 |
| 日志记录 | System.out.println散落各处 | AOP切面统一记录 |
| 架构模式 | DAO模式（命令行） | MVC三层架构（Web API） |
| 数据访问 | JDBC + Druid | JDBC + Druid（暂不变，第13章升级MyBatis） |
| 交互方式 | 命令行Scanner | HTTP RESTful API |
| 配置方式 | 硬编码/properties文件 | Spring Boot自动配置 |

### 项目结构

```text
ems-v3/
├── pom.xml
└── src/main/java/com/example/ems/
    ├── EmsApplication.java                 # Spring Boot启动类
    ├── config/
    │   └── WebConfig.java                  # MVC配置
    ├── entity/
    │   └── Employee.java                   # 员工实体类
    ├── dao/
    │   ├── EmployeeDao.java                # DAO接口
    │   └── EmployeeDaoImpl.java            # DAO实现
    ├── service/
    │   ├── EmployeeService.java            # Service接口
    │   └── EmployeeServiceImpl.java        # Service实现
    ├── controller/
    │   └── EmployeeController.java         # RESTful Controller
    ├── interceptor/
    │   └── LogInterceptor.java             # 日志拦截器
    ├── aspect/
    │   └── ServiceLogAspect.java           # AOP日志切面
    └── common/
        └── Result.java                     # 统一返回格式
```

### 第一步：pom.xml

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0
         https://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <parent>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-parent</artifactId>
        <version>3.2.5</version>
    </parent>

    <groupId>com.example</groupId>
    <artifactId>ems-v3</artifactId>
    <version>1.0.0</version>

    <properties>
        <java.version>17</java.version>
    </properties>

    <dependencies>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
        </dependency>
        <dependency>
            <groupId>com.mysql</groupId>
            <artifactId>mysql-connector-j</artifactId>
            <scope>runtime</scope>
        </dependency>
        <dependency>
            <groupId>com.alibaba</groupId>
            <artifactId>druid</artifactId>
            <version>1.2.21</version>
        </dependency>
    </dependencies>
</project>
```

### 第二步：application.yml

```yaml
server:
  port: 8080
  servlet:
    context-path: /ems

spring:
  datasource:
    driver-class-name: com.mysql.cj.jdbc.Driver
    url: jdbc:mysql://localhost:3306/ems?characterEncoding=utf8mb4&serverTimezone=Asia/Shanghai
    username: root
    password: 123456
    type: com.alibaba.druid.pool.DruidDataSource
    druid:
      initial-size: 5
      min-idle: 5
      max-active: 20
```

### 第三步：启动类

```java
package com.example.ems;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class EmsApplication {
    public static void main(String[] args) {
        SpringApplication.run(EmsApplication.class, args);
    }
}
```

### 第四步：实体类

```java
package com.example.ems.entity;

import java.math.BigDecimal;
import java.time.LocalDate;

public class Employee {

    private Long id;
    private String name;
    private Integer age;
    private String department;
    private BigDecimal salary;
    private String email;
    private LocalDate hireDate;

    public Employee() {}

    public Employee(String name, Integer age, String department,
                    BigDecimal salary, String email, LocalDate hireDate) {
        this.name = name;
        this.age = age;
        this.department = department;
        this.salary = salary;
        this.email = email;
        this.hireDate = hireDate;
    }

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }
    public String getName() { return name; }
    public void setName(String name) { this.name = name; }
    public Integer getAge() { return age; }
    public void setAge(Integer age) { this.age = age; }
    public String getDepartment() { return department; }
    public void setDepartment(String department) { this.department = department; }
    public BigDecimal getSalary() { return salary; }
    public void setSalary(BigDecimal salary) { this.salary = salary; }
    public String getEmail() { return email; }
    public void setEmail(String email) { this.email = email; }
    public LocalDate getHireDate() { return hireDate; }
    public void setHireDate(LocalDate hireDate) { this.hireDate = hireDate; }

    @Override
    public String toString() {
        return "Employee{id=" + id + ", name='" + name + "', age=" + age +
               ", department='" + department + "', salary=" + salary +
               ", email='" + email + "', hireDate=" + hireDate + "}";
    }
}
```

### 第五步：DAO层（IoC管理 + JDBC）

```java
package com.example.ems.dao;

import com.example.ems.entity.Employee;
import java.util.List;

public interface EmployeeDao {
    List<Employee> findAll();
    Employee findById(Long id);
    int insert(Employee employee);
    int update(Employee employee);
    int deleteById(Long id);
    List<Employee> findByName(String name);
}
```

```java
package com.example.ems.dao;

import com.example.ems.entity.Employee;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Repository;

import javax.sql.DataSource;
import java.math.BigDecimal;
import java.sql.*;
import java.util.ArrayList;
import java.util.List;

@Repository
public class EmployeeDaoImpl implements EmployeeDao {

    private final DataSource dataSource;

    @Autowired
    public EmployeeDaoImpl(DataSource dataSource) {
        this.dataSource = dataSource;
    }

    @Override
    public List<Employee> findAll() {
        String sql = "SELECT * FROM employee ORDER BY id";
        List<Employee> list = new ArrayList<>();
        try (Connection conn = dataSource.getConnection();
             PreparedStatement ps = conn.prepareStatement(sql);
             ResultSet rs = ps.executeQuery()) {
            while (rs.next()) {
                list.add(mapRow(rs));
            }
        } catch (SQLException e) {
            throw new RuntimeException("查询所有员工失败", e);
        }
        return list;
    }

    @Override
    public Employee findById(Long id) {
        String sql = "SELECT * FROM employee WHERE id = ?";
        try (Connection conn = dataSource.getConnection();
             PreparedStatement ps = conn.prepareStatement(sql)) {
            ps.setLong(1, id);
            try (ResultSet rs = ps.executeQuery()) {
                if (rs.next()) {
                    return mapRow(rs);
                }
            }
        } catch (SQLException e) {
            throw new RuntimeException("查询员工失败: id=" + id, e);
        }
        return null;
    }

    @Override
    public int insert(Employee employee) {
        String sql = "INSERT INTO employee(name, age, department, salary, email, hire_date) " +
                     "VALUES(?, ?, ?, ?, ?, ?)";
        try (Connection conn = dataSource.getConnection();
             PreparedStatement ps = conn.prepareStatement(sql, Statement.RETURN_GENERATED_KEYS)) {
            ps.setString(1, employee.getName());
            ps.setInt(2, employee.getAge());
            ps.setString(3, employee.getDepartment());
            ps.setBigDecimal(4, employee.getSalary());
            ps.setString(5, employee.getEmail());
            ps.setDate(6, Date.valueOf(employee.getHireDate()));
            int rows = ps.executeUpdate();
            try (ResultSet keys = ps.getGeneratedKeys()) {
                if (keys.next()) {
                    employee.setId(keys.getLong(1));
                }
            }
            return rows;
        } catch (SQLException e) {
            throw new RuntimeException("新增员工失败", e);
        }
    }

    @Override
    public int update(Employee employee) {
        String sql = "UPDATE employee SET name=?, age=?, department=?, " +
                     "salary=?, email=?, hire_date=? WHERE id=?";
        try (Connection conn = dataSource.getConnection();
             PreparedStatement ps = conn.prepareStatement(sql)) {
            ps.setString(1, employee.getName());
            ps.setInt(2, employee.getAge());
            ps.setString(3, employee.getDepartment());
            ps.setBigDecimal(4, employee.getSalary());
            ps.setString(5, employee.getEmail());
            ps.setDate(6, Date.valueOf(employee.getHireDate()));
            ps.setLong(7, employee.getId());
            return ps.executeUpdate();
        } catch (SQLException e) {
            throw new RuntimeException("更新员工失败: id=" + employee.getId(), e);
        }
    }

    @Override
    public int deleteById(Long id) {
        String sql = "DELETE FROM employee WHERE id = ?";
        try (Connection conn = dataSource.getConnection();
             PreparedStatement ps = conn.prepareStatement(sql)) {
            ps.setLong(1, id);
            return ps.executeUpdate();
        } catch (SQLException e) {
            throw new RuntimeException("删除员工失败: id=" + id, e);
        }
    }

    @Override
    public List<Employee> findByName(String name) {
        String sql = "SELECT * FROM employee WHERE name LIKE ? ORDER BY id";
        List<Employee> list = new ArrayList<>();
        try (Connection conn = dataSource.getConnection();
             PreparedStatement ps = conn.prepareStatement(sql)) {
            ps.setString(1, "%" + name + "%");
            try (ResultSet rs = ps.executeQuery()) {
                while (rs.next()) {
                    list.add(mapRow(rs));
                }
            }
        } catch (SQLException e) {
            throw new RuntimeException("按姓名查询员工失败: name=" + name, e);
        }
        return list;
    }

    private Employee mapRow(ResultSet rs) throws SQLException {
        Employee emp = new Employee();
        emp.setId(rs.getLong("id"));
        emp.setName(rs.getString("name"));
        emp.setAge(rs.getInt("age"));
        emp.setDepartment(rs.getString("department"));
        emp.setSalary(rs.getBigDecimal("salary"));
        emp.setEmail(rs.getString("email"));
        Date hireDate = rs.getDate("hire_date");
        if (hireDate != null) {
            emp.setHireDate(hireDate.toLocalDate());
        }
        return emp;
    }
}
```

注意这里的关键变化：
- `@Repository`标注，Spring IoC容器自动管理
- `DataSource`通过构造器注入（第10章推荐的方式），不再手动创建Druid连接池
- 异常直接抛出RuntimeException，由上层统一处理

### 第六步：Service层

```java
package com.example.ems.service;

import com.example.ems.entity.Employee;
import java.util.List;

public interface EmployeeService {
    List<Employee> findAll();
    Employee findById(Long id);
    Employee create(Employee employee);
    Employee update(Long id, Employee employee);
    void deleteById(Long id);
    List<Employee> findByName(String name);
}
```

```java
package com.example.ems.service;

import com.example.ems.dao.EmployeeDao;
import com.example.ems.entity.Employee;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class EmployeeServiceImpl implements EmployeeService {

    private final EmployeeDao employeeDao;

    @Autowired
    public EmployeeServiceImpl(EmployeeDao employeeDao) {
        this.employeeDao = employeeDao;
    }

    @Override
    public List<Employee> findAll() {
        return employeeDao.findAll();
    }

    @Override
    public Employee findById(Long id) {
        Employee emp = employeeDao.findById(id);
        if (emp == null) {
            throw new RuntimeException("员工不存在: id=" + id);
        }
        return emp;
    }

    @Override
    public Employee create(Employee employee) {
        employeeDao.insert(employee);
        return employee;
    }

    @Override
    public Employee update(Long id, Employee employee) {
        Employee existing = findById(id);
        employee.setId(id);
        employeeDao.update(employee);
        return employee;
    }

    @Override
    public void deleteById(Long id) {
        findById(id);
        employeeDao.deleteById(id);
    }

    @Override
    public List<Employee> findByName(String name) {
        return employeeDao.findByName(name);
    }
}
```

### 第七步：统一返回格式

```java
package com.example.ems.common;

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
        return new Result<>(200, "success", null);
    }

    public static <T> Result<T> success(T data) {
        return new Result<>(200, "success", data);
    }

    public static <T> Result<T> error(int code, String message) {
        return new Result<>(code, message, null);
    }

    public static <T> Result<T> error(String message) {
        return new Result<>(500, message, null);
    }

    public int getCode() { return code; }
    public String getMessage() { return message; }
    public T getData() { return data; }
}
```

### 第八步：Controller层（Spring MVC）

```java
package com.example.ems.controller;

import com.example.ems.common.Result;
import com.example.ems.entity.Employee;
import com.example.ems.service.EmployeeService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/employees")
public class EmployeeController {

    private final EmployeeService employeeService;

    @Autowired
    public EmployeeController(EmployeeService employeeService) {
        this.employeeService = employeeService;
    }

    @GetMapping
    public Result<List<Employee>> list() {
        return Result.success(employeeService.findAll());
    }

    @GetMapping("/{id}")
    public Result<Employee> findById(@PathVariable Long id) {
        return Result.success(employeeService.findById(id));
    }

    @GetMapping("/search")
    public Result<List<Employee>> search(@RequestParam String name) {
        return Result.success(employeeService.findByName(name));
    }

    @PostMapping
    public Result<Employee> create(@RequestBody Employee employee) {
        return Result.success(employeeService.create(employee));
    }

    @PutMapping("/{id}")
    public Result<Employee> update(@PathVariable Long id,
                                   @RequestBody Employee employee) {
        return Result.success(employeeService.update(id, employee));
    }

    @DeleteMapping("/{id}")
    public Result<Void> delete(@PathVariable Long id) {
        employeeService.deleteById(id);
        return Result.success();
    }
}
```

### 第九步：AOP日志切面

```java
package com.example.ems.aspect;

import org.aspectj.lang.ProceedingJoinPoint;
import org.aspectj.lang.annotation.Around;
import org.aspectj.lang.annotation.Aspect;
import org.springframework.stereotype.Component;

@Aspect
@Component
public class ServiceLogAspect {

    @Around("execution(* com.example.ems.service..*.*(..))")
    public Object logServiceMethod(ProceedingJoinPoint joinPoint) throws Throwable {
        String className = joinPoint.getTarget().getClass().getSimpleName();
        String methodName = joinPoint.getSignature().getName();
        long start = System.currentTimeMillis();

        System.out.println("[EMS-AOP] >>> " + className + "." + methodName + " 开始执行");

        try {
            Object result = joinPoint.proceed();
            long elapsed = System.currentTimeMillis() - start;
            System.out.println("[EMS-AOP] <<< " + className + "." + methodName +
                               " 执行成功, 耗时: " + elapsed + "ms");
            return result;
        } catch (Throwable e) {
            long elapsed = System.currentTimeMillis() - start;
            System.out.println("[EMS-AOP] !!! " + className + "." + methodName +
                               " 执行异常, 耗时: " + elapsed + "ms, 异常: " + e.getMessage());
            throw e;
        }
    }
}
```

### 第十步：MVC拦截器

```java
package com.example.ems.interceptor;

import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.stereotype.Component;
import org.springframework.web.servlet.HandlerInterceptor;

@Component
public class LogInterceptor implements HandlerInterceptor {

    @Override
    public boolean preHandle(HttpServletRequest request,
                             HttpServletResponse response,
                             Object handler) {
        long start = System.currentTimeMillis();
        request.setAttribute("startTime", start);
        System.out.println("[EMS-MVC] >>> " + request.getMethod() + " " +
                           request.getRequestURI());
        return true;
    }

    @Override
    public void afterCompletion(HttpServletRequest request,
                                HttpServletResponse response,
                                Object handler, Exception ex) {
        long start = (Long) request.getAttribute("startTime");
        long elapsed = System.currentTimeMillis() - start;
        System.out.println("[EMS-MVC] <<< " + request.getMethod() + " " +
                           request.getRequestURI() + " 完成, 耗时: " + elapsed + "ms" +
                           (ex != null ? ", 异常: " + ex.getMessage() : ""));
    }
}
```

注册拦截器：

```java
package com.example.ems.config;

import com.example.ems.interceptor.LogInterceptor;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.servlet.config.annotation.InterceptorRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

@Configuration
public class WebConfig implements WebMvcConfigurer {

    @Autowired
    private LogInterceptor logInterceptor;

    @Override
    public void addInterceptors(InterceptorRegistry registry) {
        registry.addInterceptor(logInterceptor)
                .addPathPatterns("/api/**");
    }
}
```

### 运行与测试

启动`EmsApplication`后，控制台输出：

```text
  .   ____          _            __ _ _
 /\\ / ___'_ __ _ _(_)_ __  __ _ \ \ \ \
( ( )\___ | '_ | '_| | '_ \/ _` | \ \ \ \
 \\/  ___)| |_)| | | | | || (_| |  ) ) ) )
  '  |____| .__|_| |_|_| |_\__, | / / / /
 =========|_|==============|___/=/_/_/_/

 :: Spring Boot ::                (v3.2.5)

[EMS-AOP] >>> EmployeeServiceImpl.findAll 开始执行
[EMS-AOP] <<< EmployeeServiceImpl.findAll 执行成功, 耗时: 45ms
```

用curl或Postman测试API：

```bash
# 查询所有员工
curl http://localhost:8080/ems/api/employees

# 查询单个员工
curl http://localhost:8080/ems/api/employees/1

# 按姓名搜索
curl "http://localhost:8080/ems/api/employees/search?name=张"

# 新增员工
curl -X POST http://localhost:8080/ems/api/employees \
  -H "Content-Type: application/json" \
  -d '{"name":"王五","age":28,"department":"市场部","salary":12000,"email":"wangwu@example.com","hireDate":"2024-03-01"}'

# 更新员工
curl -X PUT http://localhost:8080/ems/api/employees/1 \
  -H "Content-Type: application/json" \
  -d '{"name":"张三","age":26,"department":"技术部","salary":18000,"email":"zhangsan@example.com","hireDate":"2023-06-15"}'

# 删除员工
curl -X DELETE http://localhost:8080/ems/api/employees/1
```

所有接口返回统一格式：

```json
{
    "code": 200,
    "message": "success",
    "data": [
        {
            "id": 1,
            "name": "张三",
            "age": 26,
            "department": "技术部",
            "salary": 18000.00,
            "email": "zhangsan@example.com",
            "hireDate": "2023-06-15"
        }
    ]
}
```

### v2 → v3 核心变化总结

```text
┌──────────────────────────────────────────────────────────────────┐
│                    EMS v2 → v3 核心变化                           │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ① IoC管理依赖（第10章）                                         │
│     v2: EmployeeDao dao = new EmployeeDaoImpl(dataSource);       │
│     v3: @Repository + @Autowired → 容器自动注入                   │
│                                                                  │
│  ② AOP日志切面（第11章）                                         │
│     v2: System.out.println散落在每个方法中                        │
│     v3: @Around切面统一记录Service方法执行时间                     │
│                                                                  │
│  ③ MVC分层架构（第12章）                                         │
│     v2: 命令行Scanner交互                                        │
│     v3: @RestController + RESTful API                            │
│                                                                  │
│  ④ 统一返回格式                                                  │
│     v2: void方法直接打印到控制台                                   │
│     v3: Result<T>统一包装，前端友好                                │
│                                                                  │
│  ⑤ 拦截器日志                                                    │
│     v2: 无                                                       │
│     v3: HandlerInterceptor记录每个HTTP请求耗时                     │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

### EMS版本演进路线

| 版本 | 章节 | 技术栈 | 交互方式 |
|------|------|--------|---------|
| EMS v1 | 第1-7章 | Java SE + ArrayList | 命令行 |
| EMS v2 | 第8-9章 | JDBC + Druid + MySQL | 命令行 |
| **EMS v3** | **第10-12章** | **Spring IoC + AOP + MVC + JDBC** | **RESTful API** |
| EMS v4 | 第13-14章 | MyBatis/JPA替代JDBC | RESTful API |
| EMS v5 | 第15-19章 | Spring Boot全栈 | RESTful API |

> **下一篇预告**：第13章我们将学习MyBatis——SQL掌控者。EMS v3中的JDBC代码依然繁琐（手动设参、手动映射结果集），MyBatis将用XML或注解的方式大幅简化数据访问层的开发。同时你将掌握动态SQL这一强大武器，让复杂查询条件的拼接变得优雅而安全。
>
> **知识串联提醒**：
> - 本章的`@Repository`标注DAO层，第13章MyBatis的`@Mapper`也是类似的语义
> - 本章的`Result<T>`统一返回格式，第16章会配合`@RestControllerAdvice`实现全局异常处理
> - 本章的拦截器，第23章Spring Security会用过滤器链替代，实现更强大的认证授权
> - DispatcherServlet的请求流程理解了，后面学Spring Security的过滤器链就不会懵
