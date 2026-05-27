# 第20章：RESTful API设计与最佳实践

## 本章目标

学完本章你将能够：

- 理解REST架构的核心思想——资源导向设计，告别操作导向的混乱URL
- 掌握HTTP方法（GET/POST/PUT/PATCH/DELETE）的正确语义、幂等性和安全性
- 设计规范的API URL：版本管理、复数名词、层级关系、过滤排序分页参数
- 实现统一的分页响应格式，配合Spring Data的`Pageable`自动分页
- 使用springdoc-openapi（Spring Boot 3.x兼容）自动生成API文档
- 用Knife4j增强API文档界面，一键获得美观的接口调试页面
- 使用IDEA HTTP Client编写`.http`文件直接测试接口

---

> **本章定位**：前19章我们完成了EMS后端的所有核心功能——从数据库到业务逻辑到Web接口。但一个"能用"的API和一个"好用"的API之间，差距在于设计规范。本章就是补上这关键一环：让你的API遵循RESTful设计原则，拥有清晰的URL结构、正确的HTTP状态码、统一的分页格式、自动生成的接口文档。这些是前后端协作的基石——第21-22章的前端开发将完全依赖本章设计的API。

---

## 20.1 RESTful设计原则

### 20.1.1 什么是REST？

REST（Representational State Transfer，表述性状态转移）是Roy Fielding在2000年博士论文中提出的架构风格。别被名字吓到——它的核心思想极其朴素：

**用URL定位资源，用HTTP方法描述对资源的操作。**

对比一下两种风格：

```
操作导向（传统风格）                  资源导向（RESTful风格）
─────────────────────              ─────────────────────
GET /getEmployee?id=1              GET /api/v1/employees/1
POST /createEmployee               POST /api/v1/employees
POST /updateEmployee               PUT /api/v1/employees/1
POST /deleteEmployee?id=1          DELETE /api/v1/employees/1
GET /listEmployees?dept=IT         GET /api/v1/employees?department=IT
```

操作导向的URL里塞满了动词（get/create/update/delete），而且全部用GET或POST。RESTful风格则用**名词（资源）**作为URL，用**HTTP方法**表达操作意图。

为什么RESTful更好？

1. **语义清晰**：看到`DELETE /employees/1`就知道是删除，不需要看URL猜
2. **统一约定**：所有开发者遵循同一套规则，降低沟通成本
3. **工具友好**：HTTP缓存、代理、网关都能正确理解语义（GET可缓存，DELETE不应被缓存）
4. **自描述**：URL本身就能说明"我在操作什么资源"

### 20.1.2 HTTP方法语义详解

HTTP协议本身就定义了一组方法，每个方法有明确的语义。RESTful API的核心就是正确使用这些方法：

| 方法 | 语义 | 幂等 | 安全 | 典型示例 | 成功状态码 |
|------|------|------|------|---------|-----------|
| **GET** | 获取资源 | ✓ | ✓ | `GET /api/v1/employees/1` | 200 OK |
| **POST** | 创建资源 | ✗ | ✗ | `POST /api/v1/employees` | 201 Created |
| **PUT** | 全量更新资源 | ✓ | ✗ | `PUT /api/v1/employees/1` | 200 OK |
| **PATCH** | 部分更新资源 | ✗ | ✗ | `PATCH /api/v1/employees/1` | 200 OK |
| **DELETE** | 删除资源 | ✓ | ✗ | `DELETE /api/v1/employees/1` | 204 No Content |

两个关键概念需要理解：

**幂等性（Idempotent）**：同一个请求执行一次和执行多次，效果相同。

- `GET /employees/1`：查一次和查十次，数据不变 → 幂等
- `PUT /employees/1`（把薪资改为20000）：改一次和改十次，最终都是20000 → 幂等
- `DELETE /employees/1`：删一次和删十次，最终都是"不存在" → 幂等
- `POST /employees`（创建员工）：调一次创建一个，调十次创建十个 → **不幂等**

**安全性（Safe）**：请求不会修改服务器上的资源。

- GET和HEAD是仅有的安全方法——它们只读不写
- 安全方法可以被缓存、被搜索引擎爬虫自由调用，不会产生副作用

> 🚨 **坑点：用GET请求执行删除操作 → 搜索引擎爬虫可能误触发！**
>
> 有些开发者为了方便，把删除操作写成`GET /deleteEmployee?id=1`。这有两个严重后果：
>
> 1. **搜索引擎爬虫**会抓取页面中的所有链接。如果你的删除链接是`<a href="/deleteEmployee?id=1">删除</a>`，爬虫会自动"点击"这个链接，**帮你把数据删了**
> 2. **浏览器预加载**：Chrome等浏览器会预加载页面中的链接，同样可能触发删除
> 3. **浏览器缓存**：GET请求可能被缓存，导致删除操作根本没到达服务器
>
> **正确做法**：删除必须用DELETE方法。如果前端不方便发DELETE请求，至少用POST。

> 🚨 **坑点：POST用于更新、PUT用于创建 → 语义混乱**
>
> 有些团队习惯所有写操作都用POST：`POST /updateEmployee`、`POST /createEmployee`。这虽然能工作，但完全浪费了HTTP协议的语义。更严重的是：
>
> - HTTP缓存无法正确处理（POST响应不应被缓存，PUT可以）
> - API网关/负载均衡器无法根据方法做智能路由
> - 自动化工具（如Swagger）无法正确生成客户端代码
>
> **正确做法**：创建用POST，全量更新用PUT，部分更新用PATCH，删除用DELETE。

### 20.1.3 PUT vs PATCH — 容易混淆的两种更新

PUT是全量更新——客户端必须发送资源的**所有字段**，未发送的字段会被设为null：

```json
// PUT /api/v1/employees/1  — 全量更新
// 当前数据：{ "name": "张三", "age": 25, "department": "技术部", "salary": 15000 }
{
    "name": "张三",
    "age": 26,              // 只想改age
    "department": "技术部",
    "salary": 15000
}
// 结果：age变为26，其他字段不变

// 但如果只发送了部分字段：
{
    "age": 26
}
// 结果：name/department/salary全部变为null！因为PUT是"替换"，不是"合并"
```

PATCH是部分更新——只发送需要修改的字段：

```json
// PATCH /api/v1/employees/1  — 部分更新
{
    "age": 26               // 只发需要改的字段
}
// 结果：只有age变为26，其他字段完全不变
```

在实际项目中，**PATCH更常用**，因为前端表单往往只修改部分字段。但如果你能保证前端总是发送完整对象，PUT的语义更清晰。

> 🚨 **坑点：所有请求都返回200，在body中放错误码 → 违反HTTP语义**
>
> 有些团队的设计是这样的：
>
> ```json
> // 删除成功
> HTTP 200
> { "code": 200, "message": "删除成功" }
>
> // 删除失败（员工不存在）
> HTTP 200
> { "code": 404, "message": "员工不存在" }
>
> // 删除失败（无权限）
> HTTP 200
> { "code": 403, "message": "无权限" }
> ```
>
> 这种做法的问题：
>
> 1. **HTTP状态码和业务状态码重复**，容易混乱
> 2. **中间件/网关/缓存无法正确处理**：它们只看HTTP状态码，看到200就认为成功
> 3. **监控告警失效**：你的监控系统看到全是200，以为一切正常，实际业务可能大量失败
> 4. **前端处理复杂**：每个请求都要先解析body再判断成功失败，无法用`response.ok`快速判断
>
> **正确做法**：HTTP状态码表达"这次HTTP请求本身是否成功"，业务状态码（如第16章的Result.code）表达"业务逻辑是否成功"。两者配合使用：
>
> ```json
> // 删除成功
> HTTP 204 No Content
> (无body)
>
> // 员工不存在
> HTTP 404 Not Found
> { "code": 404, "message": "员工不存在" }
>
> // 无权限
> HTTP 403 Forbidden
> { "code": 403, "message": "无权限" }
> ```

### 20.1.4 HTTP状态码速查

HTTP状态码分为五类，记住每类的含义就能快速判断：

| 类别 | 含义 | 常用状态码 | 说明 |
|------|------|-----------|------|
| **1xx** | 信息 | 100 Continue | 继续发送请求体（少见） |
| **2xx** | 成功 | 200 OK | 请求成功（GET/PUT/PATCH通用） |
| | | 201 Created | 资源创建成功（POST） |
| | | 204 No Content | 成功但无返回内容（DELETE） |
| **3xx** | 重定向 | 301 Moved Permanently | 永久重定向 |
| | | 302 Found | 临时重定向 |
| **4xx** | 客户端错误 | 400 Bad Request | 请求参数错误/格式不对 |
| | | 401 Unauthorized | 未认证（没登录/Token无效） |
| | | 403 Forbidden | 已认证但无权限 |
| | | 404 Not Found | 资源不存在 |
| | | 409 Conflict | 资源冲突（如重复创建） |
| **5xx** | 服务器错误 | 500 Internal Server Error | 服务器内部异常 |
| | | 502 Bad Gateway | 网关/代理收到无效响应 |
| | | 503 Service Unavailable | 服务暂时不可用 |

**选择原则**：

- 成功时：GET→200，POST→201，PUT/PATCH→200，DELETE→204
- 客户端错误：优先用最具体的4xx（401≠403，400≠422）
- 服务端错误：统一500，不要暴露内部异常细节

---

## 20.2 API URL设计规范

### 20.2.1 版本管理

API一旦发布，就会有外部消费者（前端、移动端、第三方）依赖。后续修改API时，不能破坏已有的消费者。版本管理就是解决这个问题的：

```
/api/v1/employees          ← 第1版API
/api/v2/employees          ← 第2版API（可能改变了响应格式）
```

Spring Boot中的实现：

```java
@RestController
@RequestMapping("/api/v1/employees")
@Tag(name = "员工管理", description = "员工CRUD接口")
public class EmployeeController {

    @GetMapping
    public Result<PageResult<EmployeeVO>> list(
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "20") int size) {
        // ...
    }
}
```

当需要v2时，创建新的Controller：

```java
@RestController
@RequestMapping("/api/v2/employees")
@Tag(name = "员工管理V2", description = "员工CRUD接口（V2版）")
public class EmployeeV2Controller {
    // v2版本的实现，可能与v1有不同的响应格式
}
```

**版本策略建议**：

| 策略 | 示例 | 优点 | 缺点 |
|------|------|------|------|
| URL路径（推荐） | `/api/v1/employees` | 直观、易理解 | URL变长 |
| 请求头 | `Accept: application/vnd.myapi.v1+json` | URL干净 | 不直观、调试麻烦 |
| 查询参数 | `/api/employees?version=1` | 简单 | 容易遗忘、缓存问题 |

本书采用URL路径方式，这也是业界最主流的做法。

### 20.2.2 资源命名规范

**规则1：用复数名词**

```
✗  GET /api/v1/employee/1        ← 单数
✓  GET /api/v1/employees/1       ← 复数
```

为什么用复数？因为`/employees`代表的是"员工集合"这个资源，从中取一个就是`/employees/1`。整个URL读起来像自然语言："employees中的第1号"。

**规则2：避免动词**

```
✗  GET /api/v1/getEmployee?id=1
✗  POST /api/v1/createEmployee
✗  PUT /api/v1/updateEmployee/1
✗  DELETE /api/v1/deleteEmployee/1

✓  GET /api/v1/employees/1
✓  POST /api/v1/employees
✓  PUT /api/v1/employees/1
✓  DELETE /api/v1/employees/1
```

动词由HTTP方法承担，URL只负责定位资源。

**规则3：层级关系用路径表达**

```
✓  GET /api/v1/departments/3/employees      ← 部门3下的所有员工
✓  GET /api/v1/departments/3/employees/5    ← 部门3下的5号员工
```

但层级不要超过两层，否则URL过长且难以维护：

```
✗  GET /api/v1/companies/1/departments/3/employees/5/projects/2
```

超过两层时，改用查询参数：

```
✓  GET /api/v1/employees/5/projects?companyId=1&departmentId=3
```

**规则4：用小写字母和连字符**

```
✗  GET /api/v1/EmployeeInfo/1
✗  GET /api/v1/employee_info/1

✓  GET /api/v1/employee-info/1
```

### 20.2.3 过滤、排序、分页参数

查询资源时，经常需要筛选条件。这些参数不应出现在路径中，而应作为查询参数：

```
GET /api/v1/employees?page=0&size=20&sort=name,asc&department=IT&salaryMin=10000
```

| 参数 | 作用 | 示例 |
|------|------|------|
| `page` | 页码（从0开始） | `page=0` |
| `size` | 每页条数 | `size=20` |
| `sort` | 排序字段和方向 | `sort=name,asc` 或 `sort=salary,desc` |
| `department` | 按部门过滤 | `department=IT` |
| `salaryMin` | 最低薪资 | `salaryMin=10000` |

**过滤参数命名建议**：

- 精确匹配：直接用字段名（`department=IT`）
- 范围查询：加后缀（`salaryMin=10000&salaryMax=30000`）
- 模糊查询：加后缀（`nameLike=张`）
- 日期范围：`hireDateFrom=2024-01-01&hireDateTo=2024-12-31`

---

## 20.3 统一分页设计

### 20.3.1 分页请求参数

在第16章我们设计了统一返回格式`Result<T>`，现在来设计统一的分页格式。

Spring Data已经提供了`Pageable`接口，我们可以直接利用：

```java
@GetMapping
public Result<PageResult<EmployeeVO>> list(
        @RequestParam(defaultValue = "0") int page,
        @RequestParam(defaultValue = "20") int size,
        @RequestParam(required = false) String sort,
        @RequestParam(required = false) String department) {
    // page从0开始，前端传1的话需要减1
    Pageable pageable = PageRequest.of(page, size,
        sort != null ? Sort.by(sort.split(",")) : Sort.unsorted());
    PageResult<EmployeeVO> result = employeeService.findByPage(department, pageable);
    return Result.success(result);
}
```

### 20.3.2 分页响应格式

设计一个通用的分页响应类：

```java
package com.example.springbootdemo.common;

import lombok.Data;
import java.util.List;

@Data
public class PageResult<T> {

    private List<T> content;
    private int page;
    private int size;
    private long totalElements;
    private int totalPages;

    public PageResult(List<T> content, int page, int size, long totalElements) {
        this.content = content;
        this.page = page;
        this.size = size;
        this.totalElements = totalElements;
        this.totalPages = (int) Math.ceil((double) totalElements / size);
    }
}
```

响应JSON示例：

```json
{
    "code": 200,
    "message": "操作成功",
    "data": {
        "content": [
            { "id": 1, "name": "张三", "age": 25, "department": "技术部", "salary": 15000 },
            { "id": 2, "name": "李四", "age": 30, "department": "技术部", "salary": 18000 }
        ],
        "page": 0,
        "size": 20,
        "totalElements": 56,
        "totalPages": 3
    }
}
```

### 20.3.3 Service层分页实现

```java
@Service
@Slf4j
public class EmployeeServiceImpl implements EmployeeService {

    private final EmployeeRepository employeeRepository;

    public EmployeeServiceImpl(EmployeeRepository employeeRepository) {
        this.employeeRepository = employeeRepository;
    }

    @Override
    public PageResult<EmployeeVO> findByPage(String department, Pageable pageable) {
        Page<Employee> page;
        if (department != null && !department.isEmpty()) {
            page = employeeRepository.findByDepartment(department, pageable);
        } else {
            page = employeeRepository.findAll(pageable);
        }

        List<EmployeeVO> voList = page.getContent().stream()
                .map(this::toVO)
                .toList();

        return new PageResult<>(voList, pageable.getPageNumber(),
                pageable.getPageSize(), page.getTotalElements());
    }

    private EmployeeVO toVO(Employee entity) {
        EmployeeVO vo = new EmployeeVO();
        vo.setId(entity.getId());
        vo.setName(entity.getName());
        vo.setAge(entity.getAge());
        vo.setDepartment(entity.getDepartment());
        vo.setSalary(entity.getSalary());
        vo.setEmail(entity.getEmail());
        vo.setHireDate(entity.getHireDate());
        return vo;
    }
}
```

> 🚨 **坑点：Spring Data的Pageable页码从0开始！**
>
> 前端通常习惯页码从1开始，但Spring Data的`PageRequest.of(page, size)`中page从0开始。如果你的前端传`page=1`，后端需要`PageRequest.of(page - 1, size)`或者约定前端也传0-based。建议在API文档中明确说明页码规则，避免前后端不一致导致数据错位。

---

## 20.4 API文档 — springdoc-openapi + Knife4j

### 20.4.1 为什么需要API文档？

前后端分离开发中，API文档是前后端之间的"契约"。没有文档，前端开发者只能：
- 看后端代码猜接口（效率极低）
- 口头问后端同事（信息容易遗漏）
- 用抓包工具看请求（只能看到已有的）

好的API文档应该包含：
- 每个接口的URL、HTTP方法、请求参数、响应格式
- 参数的类型、是否必填、默认值、取值范围
- 响应示例
- 错误码说明

手动写文档的问题：**代码改了文档忘了改** → 文档和代码不一致 → 比没有文档更可怕。

解决方案：**从代码自动生成文档**。

### 20.4.2 springdoc-openapi — Spring Boot 3.x的API文档方案

在Spring Boot 2.x时代，最流行的API文档工具是Springfox（Swagger2）。但Springfox从2020年起就停止维护了，**不支持Spring Boot 3.x**。现在必须使用springdoc-openapi。

> 🚨 **坑点：springfox已死，不要在Spring Boot 3.x项目中使用**
>
> Springfox最后的版本是3.0.0（2020年发布），不支持Spring Boot 3.x。如果你在网上搜到`@Api`、`@ApiOperation`这些注解，那是Springfox的——**已经过时了**。springdoc-openapi使用的是OpenAPI 3.0规范的注解：`@Tag`、`@Operation`、`@Parameter`、`@Schema`。

**第一步：添加依赖**

```xml
<dependency>
    <groupId>org.springdoc</groupId>
    <artifactId>springdoc-openapi-starter-webmvc-ui</artifactId>
    <version>2.3.0</version>
</dependency>
```

这个依赖同时包含了：
- `springdoc-openapi-starter-webmvc-api`：核心功能，自动扫描Controller生成OpenAPI规范
- `swagger-ui`：内置的Swagger UI界面

**第二步：配置application.yml**

```yaml
springdoc:
  api-docs:
    enabled: true
    path: /v3/api-docs              # OpenAPI JSON的路径（默认就是/v3/api-docs）
  swagger-ui:
    enabled: true
    path: /swagger-ui.html          # Swagger UI的路径
    tags-sorter: alpha              # 按字母排序标签
    operations-sorter: method       # 按HTTP方法排序接口
  packages-to-scan: com.example.springbootdemo.controller
  default-flat-param-object: true   # 参数平铺展示
```

启动应用后访问：
- Swagger UI：`http://localhost:8080/swagger-ui.html`
- OpenAPI JSON：`http://localhost:8080/v3/api-docs`

**第三步：OpenAPI配置类**

```java
package com.example.springbootdemo.config;

import io.swagger.v3.oas.models.OpenAPI;
import io.swagger.v3.oas.models.info.Contact;
import io.swagger.v3.oas.models.info.Info;
import io.swagger.v3.oas.models.info.License;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class OpenApiConfig {

    @Bean
    public OpenAPI customOpenAPI() {
        return new OpenAPI()
                .info(new Info()
                        .title("EMS员工管理系统 API")
                        .version("1.0.0")
                        .description("EMS员工管理系统RESTful API文档，包含员工CRUD、部门管理等功能")
                        .contact(new Contact()
                                .name("开发团队")
                                .email("dev@example.com"))
                        .license(new License()
                                .name("Apache 2.0")
                                .url("https://www.apache.org/licenses/LICENSE-2.0")));
    }
}
```

### 20.4.3 常用注解详解

**@Tag — Controller分组**

```java
@RestController
@RequestMapping("/api/v1/employees")
@Tag(name = "员工管理", description = "员工的增删改查接口")
public class EmployeeController {
    // ...
}
```

Swagger UI中会按Tag分组展示接口，一个Tag对应一个折叠面板。

**@Operation — 接口描述**

```java
@GetMapping("/{id}")
@Operation(summary = "根据ID查询员工", description = "返回指定ID的员工详细信息，不存在时返回404")
public Result<EmployeeVO> findById(
        @Parameter(description = "员工ID", required = true, example = "1")
        @PathVariable Long id) {
    return Result.success(employeeService.findById(id));
}
```

**@Parameter — 参数说明**

```java
@GetMapping
@Operation(summary = "分页查询员工列表")
public Result<PageResult<EmployeeVO>> list(
        @Parameter(description = "页码（从0开始）", example = "0")
        @RequestParam(defaultValue = "0") int page,
        @Parameter(description = "每页条数", example = "20")
        @RequestParam(defaultValue = "20") int size,
        @Parameter(description = "排序，格式：字段,方向", example = "name,asc")
        @RequestParam(required = false) String sort,
        @Parameter(description = "部门名称过滤", example = "技术部")
        @RequestParam(required = false) String department) {
    // ...
}
```

**@Schema — 模型说明**

```java
@Data
@Schema(description = "员工信息")
public class EmployeeVO {

    @Schema(description = "员工ID", example = "1")
    private Long id;

    @Schema(description = "姓名", example = "张三", requiredMode = Schema.RequiredMode.REQUIRED)
    private String name;

    @Schema(description = "年龄", example = "25", minimum = "18", maximum = "65")
    private Integer age;

    @Schema(description = "部门", example = "技术部")
    private String department;

    @Schema(description = "月薪", example = "15000.00")
    private Double salary;

    @Schema(description = "邮箱", example = "zhangsan@example.com")
    private String email;

    @Schema(description = "入职日期", example = "2024-01-15")
    private LocalDate hireDate;
}
```

**@Operation + 请求体示例**

```java
@PostMapping
@Operation(summary = "创建员工")
public Result<EmployeeVO> create(
        @Parameter(description = "员工信息", required = true)
        @RequestBody @Valid EmployeeCreateDTO dto) {
    return Result.success(employeeService.create(dto));
}
```

### 20.4.4 完整的RESTful CRUD Controller示例

结合前面所有知识，写一个规范的RESTful Controller：

```java
package com.example.springbootdemo.controller;

import com.example.springbootdemo.common.PageResult;
import com.example.springbootdemo.common.Result;
import com.example.springbootdemo.dto.EmployeeCreateDTO;
import com.example.springbootdemo.dto.EmployeeUpdateDTO;
import com.example.springbootdemo.vo.EmployeeVO;
import com.example.springbootdemo.service.EmployeeService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.tags.Tag;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.responses.ApiResponses;
import jakarta.validation.Valid;
import org.springframework.data.domain.Pageable;
import org.springframework.data.domain.Sort;
import org.springframework.data.web.PageableDefault;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/v1/employees")
@Tag(name = "员工管理", description = "员工CRUD接口")
public class EmployeeController {

    private final EmployeeService employeeService;

    public EmployeeController(EmployeeService employeeService) {
        this.employeeService = employeeService;
    }

    @GetMapping
    @Operation(summary = "分页查询员工列表")
    @ApiResponses({
        @ApiResponse(responseCode = "200", description = "查询成功")
    })
    public Result<PageResult<EmployeeVO>> list(
            @PageableDefault(size = 20, sort = "id", direction = Sort.Direction.ASC)
            Pageable pageable,
            @Parameter(description = "部门名称过滤")
            @RequestParam(required = false) String department) {
        return Result.success(employeeService.findByPage(department, pageable));
    }

    @GetMapping("/{id}")
    @Operation(summary = "根据ID查询员工")
    @ApiResponses({
        @ApiResponse(responseCode = "200", description = "查询成功"),
        @ApiResponse(responseCode = "404", description = "员工不存在")
    })
    public Result<EmployeeVO> findById(
            @Parameter(description = "员工ID") @PathVariable Long id) {
        return Result.success(employeeService.findById(id));
    }

    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    @Operation(summary = "创建员工")
    @ApiResponses({
        @ApiResponse(responseCode = "201", description = "创建成功"),
        @ApiResponse(responseCode = "400", description = "参数校验失败")
    })
    public Result<EmployeeVO> create(
            @RequestBody @Valid EmployeeCreateDTO dto) {
        return Result.success(employeeService.create(dto));
    }

    @PutMapping("/{id}")
    @Operation(summary = "全量更新员工")
    @ApiResponses({
        @ApiResponse(responseCode = "200", description = "更新成功"),
        @ApiResponse(responseCode = "404", description = "员工不存在")
    })
    public Result<EmployeeVO> update(
            @Parameter(description = "员工ID") @PathVariable Long id,
            @RequestBody @Valid EmployeeUpdateDTO dto) {
        return Result.success(employeeService.update(id, dto));
    }

    @PatchMapping("/{id}")
    @Operation(summary = "部分更新员工")
    public Result<EmployeeVO> patchUpdate(
            @Parameter(description = "员工ID") @PathVariable Long id,
            @RequestBody java.util.Map<String, Object> updates) {
        return Result.success(employeeService.patchUpdate(id, updates));
    }

    @DeleteMapping("/{id}")
    @ResponseStatus(HttpStatus.NO_CONTENT)
    @Operation(summary = "删除员工")
    @ApiResponses({
        @ApiResponse(responseCode = "204", description = "删除成功"),
        @ApiResponse(responseCode = "404", description = "员工不存在")
    })
    public void delete(
            @Parameter(description = "员工ID") @PathVariable Long id) {
        employeeService.delete(id);
    }
}
```

注意几个关键点：
- `@ResponseStatus(HttpStatus.CREATED)`：POST创建成功返回201
- `@ResponseStatus(HttpStatus.NO_CONTENT)`：DELETE成功返回204
- `@PageableDefault`：设置分页默认值
- `@ApiResponses`：明确列出可能的响应码和含义

### 20.4.5 Knife4j — 增强Swagger UI

Swagger UI虽然功能完整，但界面比较简陋。Knife4j是一个增强的Swagger UI，提供了更美观的界面和更多功能。

**添加依赖**：

```xml
<dependency>
    <groupId>com.github.xiaoymin</groupId>
    <artifactId>knife4j-openapi3-jakarta-spring-boot-starter</artifactId>
    <version>4.4.0</version>
</dependency>
```

> 注意：Spring Boot 3.x必须用`knife4j-openapi3-jakarta-spring-boot-starter`，不要用`knife4j-openapi3-spring-boot-starter`（那是Spring Boot 2.x的）。Jakarta是Java EE移交给Eclipse基金会后的命名空间（`jakarta.servlet`替代了`javax.servlet`），Spring Boot 3.x全面使用Jakarta命名空间。

添加依赖后无需额外配置，启动应用后访问：

```
http://localhost:8080/doc.html
```

Knife4j相比原生Swagger UI的增强：
- 更美观的界面，支持中文
- 离线文档导出（Markdown/Word/HTML）
- 请求参数缓存
- 全局参数配置（方便设置Token）
- 接口排序

**Knife4j增强配置**（application.yml）：

```yaml
springdoc:
  api-docs:
    enabled: true
  swagger-ui:
    enabled: true

knife4j:
  enable: true
  setting:
    language: zh_cn                # 中文界面
    enable-version: true           # 显示版本号
    enable-reload-cache-parameter: true  # 参数缓存
  openapi:
    title: EMS员工管理系统 API
    description: RESTful API文档
    version: 1.0.0
```

> 🚨 **坑点：生产环境暴露API文档 → 攻击者可借此了解所有API！**
>
> API文档在开发阶段极其有用，但在生产环境中是严重的安全风险。攻击者可以通过API文档了解：
> - 所有接口的URL和参数
> - 数据模型的结构
> - 认证方式
> - 业务逻辑
>
> **解决方案：按环境条件启用文档**
>
> ```yaml
> # application-dev.yml（开发环境）
> springdoc:
>   api-docs:
>     enabled: true
>   swagger-ui:
>     enabled: true
> knife4j:
>   enable: true
>
> # application-prod.yml（生产环境）
> springdoc:
>   api-docs:
>     enabled: false
>   swagger-ui:
>     enabled: false
> knife4j:
>   enable: false
> ```
>
> 或者用Spring Profile条件控制：
>
> ```java
> @Configuration
> @Profile("dev")  // 只在dev环境生效
> public class OpenApiConfig {
>     @Bean
>     public OpenAPI customOpenAPI() {
>         return new OpenAPI().info(new Info()
>                 .title("EMS API").version("1.0"));
>     }
> }
> ```

### 20.4.6 IDEA HTTP Client — 不用离开IDE的接口测试

除了Swagger UI和Postman，IntelliJ IDEA自带了一个轻量级的HTTP Client，可以直接在IDE中测试API。

在`src/test/http/`目录下创建`.http`文件：

```http
### 查询员工列表
GET http://localhost:8080/api/v1/employees?page=0&size=10&department=技术部
Accept: application/json

### 根据ID查询员工
GET http://localhost:8080/api/v1/employees/1
Accept: application/json

### 创建员工
POST http://localhost:8080/api/v1/employees
Content-Type: application/json

{
  "name": "赵六",
  "age": 28,
  "department": "产品部",
  "salary": 16000,
  "email": "zhaoliu@example.com",
  "hireDate": "2024-06-01"
}

### 全量更新员工
PUT http://localhost:8080/api/v1/employees/1
Content-Type: application/json

{
  "name": "张三",
  "age": 26,
  "department": "技术部",
  "salary": 18000,
  "email": "zhangsan@example.com",
  "hireDate": "2024-01-15"
}

### 部分更新员工
PATCH http://localhost:8080/api/v1/employees/1
Content-Type: application/json

{
  "salary": 20000
}

### 删除员工
DELETE http://localhost:8080/api/v1/employees/1

### 使用环境变量
GET http://{{host}}:{{port}}/api/v1/employees
Accept: application/json
```

在`.http`文件同目录下创建`http-client.env.json`：

```json
{
  "dev": {
    "host": "localhost",
    "port": 8080
  },
  "test": {
    "host": "test-api.example.com",
    "port": 443
  }
}
```

使用方式：在IDEA中打开`.http`文件，每个请求旁边会出现一个绿色运行按钮，点击即可发送请求。响应会直接显示在IDEA的Run面板中。

IDEA HTTP Client的优势：
- 不用离开IDE
- `.http`文件可以纳入Git版本管理，团队共享
- 支持环境变量切换
- 支持响应断言和脚本

---

## 20.5 本章小结

本章从"能用"到"好用"，系统讲解了RESTful API的设计规范：

1. **RESTful核心思想**：资源导向设计——URL定位资源，HTTP方法描述操作。告别`/getEmployee`、`/createEmployee`这种操作导向的混乱URL
2. **HTTP方法语义**：GET获取、POST创建、PUT全量更新、PATCH部分更新、DELETE删除。理解幂等性和安全性，避免用GET执行删除等危险操作
3. **状态码正确使用**：成功时用具体的状态码（200/201/204），失败时用对应的4xx/5xx，不要所有请求都返回200然后在body中放错误码
4. **URL设计规范**：版本管理（`/api/v1/`）、复数名词（`/employees`）、层级关系（`/departments/{id}/employees`）、过滤排序分页参数
5. **统一分页格式**：`PageResult<T>`封装分页数据，配合Spring Data的`Pageable`自动分页
6. **API文档自动化**：springdoc-openapi（Spring Boot 3.x兼容）+ `@Tag`/`@Operation`/`@Parameter`/`@Schema`注解 + Knife4j增强界面
7. **IDEA HTTP Client**：用`.http`文件在IDE内直接测试接口，方便团队共享

---

## 思考题

1. 以下API设计有哪些违反RESTful原则的地方？请逐一指出并修正：
   ```
   GET /api/getEmployeeList?dept=IT
   POST /api/employee/update
   GET /api/deleteEmployee?id=5
   POST /api/employee/create
   ```

2. PUT和PATCH都可以用来更新资源，请解释它们的区别。如果一个前端表单只修改了员工的薪资字段，应该用PUT还是PATCH？为什么？

3. 你的团队决定API文档在生产环境关闭。但运维人员反映，生产环境出了问题时，没有API文档很难排查。请设计一个方案，既保证安全性，又能在需要时查看文档。

4. Spring Data的`Pageable`页码从0开始，但前端分页组件通常从1开始。请设计一个方案，让前后端都不需要做额外的页码转换。

5. 以下代码有什么问题？如何改进？
   ```java
   @GetMapping("/search")
   public Result<List<EmployeeVO>> search(String name, String dept,
       Integer ageMin, Integer ageMax, Double salaryMin, Double salaryMax,
       String hireDateFrom, String hireDateTo, String sort, String direction) {
       // ...
   }
   ```

---

<details>
<summary>思考题参考答案（点击展开）</summary>

**第1题**：

- `GET /api/getEmployeeList?dept=IT` → URL中包含动词get，应改为 `GET /api/v1/employees?department=IT`
- `POST /api/employee/update` → 更新应使用PUT或PATCH，且资源名应为复数，改为 `PUT /api/v1/employees/{id}`
- `GET /api/deleteEmployee?id=5` → 删除应使用DELETE方法，且URL不应包含动词，改为 `DELETE /api/v1/employees/5`
- `POST /api/employee/create` → 创建用POST没问题，但资源名应为复数且不含动词，改为 `POST /api/v1/employees`

**第2题**：

PUT是全量更新，客户端必须发送资源的所有字段，未发送的字段会被设为null。PATCH是部分更新，只发送需要修改的字段。

只修改薪资字段时应该用PATCH：`PATCH /api/v1/employees/{id}`，body为`{"salary": 20000}`。如果用PUT，要么发送完整对象（前端需要先查询再修改再提交），要么只发薪资字段导致其他字段被清空。

**第3题**：

方案：
1. API文档服务部署在内网管理端口（如8081），与业务端口（8080）隔离
2. 通过Spring Profile控制：生产环境默认关闭，需要时通过Actuator的`/actuator/env`端点动态修改`springdoc.api-docs.enabled`为true（需配合安全认证）
3. 更安全的做法：API文档只在内网可访问，通过Nginx配置IP白名单限制访问

```yaml
# application-prod.yml
springdoc:
  api-docs:
    enabled: false
  swagger-ui:
    enabled: false
management:
  server:
    port: 8081  # 管理端口独立
  endpoints:
    web:
      exposure:
        include: health,info,env
```

**第4题**：

方案1（推荐）：在Controller层做转换，对外暴露1-based页码：

```java
@GetMapping
public Result<PageResult<EmployeeVO>> list(
        @RequestParam(defaultValue = "1") int page,  // 前端传1
        @RequestParam(defaultValue = "20") int size) {
    // 内部转为0-based
    Pageable pageable = PageRequest.of(page - 1, size);
    PageResult<EmployeeVO> result = employeeService.findByPage(null, pageable);
    // 响应中的page也转为1-based
    result.setPage(result.getPage() + 1);
    return Result.success(result);
}
```

方案2：自定义`PageableArgumentResolver`，全局自动转换。

**第5题**：

问题：参数太多，方法签名臃肿，难以维护。随着筛选条件增加，参数会越来越多。

改进：封装为查询DTO对象：

```java
@Data
@Schema(description = "员工查询条件")
public class EmployeeQueryDTO {
    @Schema(description = "姓名模糊查询")
    private String name;

    @Schema(description = "部门")
    private String department;

    @Schema(description = "最小年龄")
    private Integer ageMin;

    @Schema(description = "最大年龄")
    private Integer ageMax;

    @Schema(description = "最低薪资")
    private Double salaryMin;

    @Schema(description = "最高薪资")
    private Double salaryMax;

    @Schema(description = "入职日期起")
    private LocalDate hireDateFrom;

    @Schema(description = "入职日期止")
    private LocalDate hireDateTo;
}

@GetMapping
public Result<PageResult<EmployeeVO>> list(
        EmployeeQueryDTO query,  // Spring MVC自动绑定查询参数到DTO
        Pageable pageable) {
    return Result.success(employeeService.search(query, pageable));
}
```

</details>

---

> **下一篇预告**：本章我们设计了规范的RESTful API，有了文档和测试工具。但后端开发者迟早要面对前端——至少要能看懂前端代码、能写简单的页面来验证后端接口。第21章将从后端开发者的视角，快速速览HTML/CSS/JavaScript的核心知识，重点讲解Flexbox布局和async/await异步编程，为第22章的Vue 3前端开发打下基础。
