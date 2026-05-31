# 85-API文档

> 💡 你和同事合作开发前后端。你写好了一个用户管理接口，发微信告诉他："POST /api/users，body传 username、email、phone。"一周后他问："phone 是必传的吗？格式是什么？"——你开始翻代码。如果有一份自动生成的"接口说明书"，随代码更新而自动更新，前端随时可以查——这就是 API 文档工具的价值。

---

## 本章目标
- 集成 SpringDoc OpenAPI（Swagger 3）
- 使用 `@Tag`、`@Operation`、`@Schema` 美化文档
- 配置 Swagger UI 用于可视化交互
- 理解 API 文档的最佳实践与安全考量

---

## 85.1 SpringDoc OpenAPI 集成

### 添加依赖

```xml
<dependency>
    <groupId>org.springdoc</groupId>
    <artifactId>springdoc-openapi-starter-webmvc-ui</artifactId>
    <version>2.5.0</version>
</dependency>
```

### application.yml 配置

```yaml
springdoc:
  swagger-ui:
    path: /docs
    operations-sorter: method
    tags-sorter: alpha
  api-docs:
    path: /api-docs
```

浏览器访问 `http://localhost:8080/docs` 即可看到 Swagger UI。

---

## 85.2 核心注解速查

| 注解 | 位置 | 作用 |
|------|------|------|
| `@Tag` | Controller 类上 | 分组命名 |
| `@Operation` | 方法上 | 接口描述 |
| `@ApiResponses` | 方法上 | 可能的响应 |
| `@Parameter` | 参数上 | 参数描述 |
| `@Schema` | 实体类/字段上 | 模型字段描述 |

---

## 85.3 美化你的文档

### Controller

```java
@RestController
@RequestMapping("/api/users")
@Tag(name = "用户管理", description = "用户的增删改查接口")
public class UserController {

    @Operation(summary = "查询用户列表", description = "分页查询所有用户")
    @ApiResponse(responseCode = "200", description = "查询成功")
    @GetMapping
    public Result<List<User>> list() {
        return Result.success(userService.findAll());
    }

    @Operation(summary = "根据ID查询用户")
    @ApiResponses({
            @ApiResponse(responseCode = "200", description = "查询成功"),
            @ApiResponse(responseCode = "404", description = "用户不存在")
    })
    @GetMapping("/{id}")
    public Result<User> getById(
            @Parameter(description = "用户ID", example = "1", required = true)
            @PathVariable Long id) {
        return Result.success(userService.findById(id));
    }

    @Operation(summary = "创建用户")
    @ApiResponse(responseCode = "201", description = "创建成功")
    @PostMapping
    public Result<User> create(
            @Parameter(description = "用户信息", required = true)
            @Valid @RequestBody User user) {
        return Result.success(userService.create(user));
    }

    @Operation(summary = "更新用户")
    @PutMapping("/{id}")
    public Result<User> update(
            @Parameter(description = "用户ID", example = "1")
            @PathVariable Long id,
            @Valid @RequestBody User user) {
        return Result.success(userService.update(id, user));
    }

    @Operation(summary = "删除用户")
    @ApiResponse(responseCode = "204", description = "删除成功")
    @DeleteMapping("/{id}")
    public Result<Void> delete(
            @Parameter(description = "用户ID", example = "1")
            @PathVariable Long id) {
        userService.delete(id);
        return Result.success(null);
    }
}
```

### 实体类

```java
@Data
@Schema(description = "用户实体")
public class User {

    @Schema(description = "用户ID（新增时不需要传）", example = "1",
            accessMode = Schema.AccessMode.READ_ONLY)
    private Long id;

    @Schema(description = "用户名", example = "zhangsan",
            requiredMode = Schema.RequiredMode.REQUIRED)
    @NotBlank
    @Size(min = 2, max = 20)
    private String username;

    @Schema(description = "邮箱", example = "zhangsan@example.com",
            requiredMode = Schema.RequiredMode.REQUIRED)
    @NotBlank @Email
    private String email;

    @Schema(description = "手机号", example = "13800138000")
    @Pattern(regexp = "^1[3-9]\\d{9}$")
    private String phone;

    @Schema(description = "年龄", example = "25", minimum = "0", maximum = "150")
    @Min(0) @Max(150)
    private Integer age;
}
```

### 全局配置

```java
@Configuration
public class OpenApiConfig {

    @Bean
    public OpenAPI customOpenAPI() {
        return new OpenAPI()
                .info(new Info()
                        .title("Demo API 文档")
                        .version("1.0.0")
                        .description("Spring Boot 教程示例项目")
                        .contact(new Contact()
                                .name("开发团队")
                                .email("dev@example.com")));
    }
}
```

---

## 85.4 Swagger UI 交互式测试

访问 `http://localhost:8080/docs`：
1. 顶部显示项目名称和版本
2. 左侧列出 `@Tag` 分组的接口
3. 点击 **Try it out** → 填入参数 → **Execute** → 看到真实响应

---

## 85.5 生产环境的安全考量

**API 文档绝对不能在生产环境公开暴露！**

```yaml
# application-dev.yml
springdoc:
  api-docs:
    enabled: true
  swagger-ui:
    enabled: true

# application-prod.yml
springdoc:
  api-docs:
    enabled: false
  swagger-ui:
    enabled: false
```

---

## 85.6 分组——大项目的文档组织

```java
@Configuration
public class OpenApiGroupConfig {

    @Bean
    public GroupedOpenApi userApi() {
        return GroupedOpenApi.builder()
                .group("用户模块")
                .pathsToMatch("/api/users/**")
                .build();
    }

    @Bean
    public GroupedOpenApi orderApi() {
        return GroupedOpenApi.builder()
                .group("订单模块")
                .pathsToMatch("/api/orders/**")
                .build();
    }
}
```

Swagger UI 右上角出现下拉框，可在不同分组间切换。

---

## 85.7 小结

| 知识点 | 核心内容 |
|--------|----------|
| SpringDoc | Spring Boot 3.x 的 Swagger 替代方案 |
| @Tag | Controller 分组命名 |
| @Operation | 接口描述（summary + description） |
| @Schema | 实体字段描述（description + example + requiredMode） |
| Swagger UI | `/docs` 路径，交互式测试 |
| 生产环境 | 必须关闭 API 文档 |
| GroupedOpenApi | 大项目按模块分组 |

---

## 85.8 自测题

**1. 以下哪个注解用来描述字段在请求体中必传？**

A. `@Schema(description = "用户名")`  
B. `@Schema(requiredMode = Schema.RequiredMode.REQUIRED)`  
C. `@Schema(accessMode = Schema.AccessMode.READ_ONLY)`  

**2. API 文档生产环境应该打开还是关闭？为什么？**

**3. 有 80 个接口分布在 5 个 Controller 中，如何在 Swagger UI 中按模块浏览？**

---

**答案提示**：1→B。2→必须关闭——暴露接口结构增加攻击面，Try it out 可能导致误操作。3→使用 `GroupedOpenApi` 按 Controller 路径前缀分组。恭喜你完成教程系列！