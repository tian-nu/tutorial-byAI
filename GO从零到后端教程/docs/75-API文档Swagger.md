# 第75章 · API文档Swagger

> "你辛辛苦苦写了50个API接口，然后前端同事跑来问你：'这个接口的请求参数是什么？返回的是什么格式？错误码有哪些？' 你不可能每次遇到这个问题都翻源代码回答。Swagger让你在代码里写几句注释，自动生成一份漂亮的在线API文档——可读、可搜、还能直接在浏览器里点'Try it out'测试接口。"

---

## 75.1 Swagger / OpenAPI是什么

### 一段历史

2010年，一个叫Tony Tam的人创建了Swagger项目——一个帮助开发者设计和文档化RESTful API的工具。2015年，SmartBear公司把Swagger规范捐献给了Linux基金会，改名为**OpenAPI Specification**。现在：

- **OpenAPI** = API描述规范（标准）
- **Swagger** = 实现这套规范的工具集

在日常交流中，大家仍然习惯说"Swagger文档"，但其实指的是"符合OpenAPI规范的API文档"。

### Swagger生态

| 工具 | 用途 |
|------|------|
| **Swagger Editor** | 在线编写OpenAPI规范的编辑器 |
| **Swagger UI** | 把OpenAPI规范渲染成可交互的HTML文档 |
| **Swagger Codegen** | 根据OpenAPI规范自动生成客户端SDK代码 |
| **swaggo/swag** | 从Go代码注释中自动生成OpenAPI规范 |

### 为什么需要API文档

如果没有Swagger，API文档通常长这样——一个飞书/Notion文档，里面手写了几十个接口的描述。一旦接口改了，文档忘了更新，就成了"接口文档从来对不上实际接口"的噩梦。

Swagger的解决方案是：**文档和代码同源**。你在代码的注释里描述接口，编译时自动生成文档。代码变了，重新生成文档即可——永远不会脱节。

---

## 75.2 swaggo工具：注释→文档

Go生态中使用 [swaggo/swag](https://github.com/swaggo/swag) 来生成Swagger文档。

### 安装

```bash
go install github.com/swaggo/swag/cmd/swag@latest
```

确认安装成功：

```bash
swag --version
```

### 安装Gin的Swagger集成

```bash
go get github.com/swaggo/gin-swagger
go get github.com/swaggo/files
```

---

## 75.3 主要注解

Swagger通过在Go代码的注释中写特殊注解（Annotation）来描述API。

### 全局注解（写在main.go顶部）

```go
package main

import (
    "github.com/gin-gonic/gin"
    swaggerFiles "github.com/swaggo/files"
    ginSwagger "github.com/swaggo/gin-swagger"

    _ "myweb/docs"
)

// @title           用户管理系统 API
// @version         1.0
// @description     用户管理系统的接口文档，包含用户注册、登录、信息管理等接口
// @termsOfService  https://example.com/terms/

// @contact.name   API支持团队
// @contact.url    https://example.com/support
// @contact.email  support@example.com

// @license.name  MIT
// @license.url   https://opensource.org/licenses/MIT

// @host      localhost:8080
// @BasePath  /api/v1

func main() {
    r := gin.Default()

    r.GET("/swagger/*any", ginSwagger.WrapHandler(swaggerFiles.Handler))

    api := r.Group("/api/v1")
    {
        RegisterUserRoutes(api)
    }

    r.Run()
}
```

关键点：
- `_ "myweb/docs"` — 导入swag生成的docs包（即使代码中没直接引用，也需要导入来初始化）
- `@host` — API服务器的地址
- `@BasePath` — 所有接口的公共路径前缀

### 接口注解（写在Handler函数上方）

```go
// @Summary      创建用户
// @Description  根据提供的信息创建一个新用户
// @Tags         用户管理
// @Accept       json
// @Produce      json
// @Param        request body CreateUserRequest true "创建用户请求体"
// @Success      201 {object} Response{data=model.User} "创建成功"
// @Failure      400 {object} Response "参数错误"
// @Failure      409 {object} Response "用户名已存在"
// @Router       /users [post]
func CreateUser(c *gin.Context) {
    var req CreateUserRequest
    if err := c.ShouldBindJSON(&req); err != nil {
        response.Error(c, ecode.ErrInvalidParams, "参数错误")
        return
    }

    user, err := userService.Create(&req)
    if err != nil {
        response.HandleServiceError(c, err, logger)
        return
    }

    response.Success(c, user)
}
```

### 常用注解速查

| 注解 | 含义 | 示例 |
|------|------|------|
| `@Summary` | 接口简短描述 | `"创建用户"` |
| `@Description` | 接口详细描述 | `"根据提供的信息创建新用户"` |
| `@Tags` | 分组标签 | `"用户管理"` |
| `@Accept` | 接受的请求格式 | `json` |
| `@Produce` | 返回的响应格式 | `json` |
| `@Param` | 请求参数 | `path id int true "用户ID"` |
| `@Success` | 成功响应 | `200 {object} Response` |
| `@Failure` | 失败响应 | `400 {object} Response` |
| `@Router` | 路由 | `/users [post]` |
| `@Security` | 认证方式 | `ApiKeyAuth` |

### @Param详解

```go
// @Param   name  位置   类型      是否必填  "描述"       附加属性
// @Param   id    path   int       true     "用户ID"
// @Param   page  query  int       false    "页码"        default(1)
// @Param   request body  CreateUserRequest true "请求体"
```

位置参数可选值：
- `path` — 路径参数 `/users/:id`
- `query` — 查询参数 `?page=1`
- `header` — 请求头
- `body` — 请求体
- `formData` — 表单数据

### @Success/@Failure详解

```go
// @Success  状态码  {类型}    数据类型               "描述"
// @Success  200     {object}  Response{data=User}    "查询成功"
// @Success  200     {array}   model.User             "用户列表"
// @Failure  400     {object}  Response               "参数错误"
```

---

## 75.4 Gin集成Swagger

### 生成文档

在项目根目录执行：

```bash
swag init
```

这会扫描你的代码，生成 `docs/` 目录，包含：
- `docs/docs.go` — Go代码，包含API描述信息
- `docs/swagger.json` — JSON格式的OpenAPI规范
- `docs/swagger.yaml` — YAML格式的OpenAPI规范

### 完整项目结构示例

```
myweb/
├── docs/
│   ├── docs.go           # swag生成
│   ├── swagger.json      # swag生成
│   └── swagger.yaml      # swag生成
├── internal/
│   ├── handler/
│   │   └── user_handler.go   # 带Swagger注解
│   ├── model/
│   │   └── user.go
│   └── service/
│       └── user_service.go
├── main.go               # @title, @host等全局注解
└── go.mod
```

### 注意事项

1. **`swag init` 必须在包含全局注解的 `main.go` 所在目录执行**（或指定 `-g` 参数）
2. **每次修改了注解后都要重新运行 `swag init`**
3. **`docs/` 目录应该加入 `.gitignore`？** — 看团队情况。如果团队成员都有swag，可以不提交；但为了方便CI/CD构建，通常提交。

---

## 75.5 在线文档界面

启动服务后，访问：

```
http://localhost:8080/swagger/index.html
```

你会看到一个漂亮的Swagger UI界面：

- 左侧是按Tags分组的接口列表
- 点击展开可以看到每个接口的详细信息（参数、响应格式、状态码）
- 点击 **"Try it out"** 按钮，直接在浏览器里输入参数并发起请求
- 响应结果实时显示在下方

### Swagger UI的功能

| 功能 | 说明 |
|------|------|
| 接口列表 | 按Tag分组，可折叠/展开 |
| 参数填写 | 支持path/query/body参数，有格式校验 |
| 在线测试 | 点击Execute直接发HTTP请求 |
| 响应展示 | 显示状态码、响应头、格式化后的响应体 |
| 模型展示 | 展开Schemas可以看到每个数据结构的字段定义 |
| JSON下载 | 可以下载 `swagger.json` 导入Postman/Apifox |

**这就是Swagger最大的价值——它不仅是文档，还是一个可交互的API测试工具。** 前端同事不需要装Postman，打开你的Swagger页面就能直接调用你的接口，看到真实的返回数据格式。

---

## 🤔 想多一点：Swagger的局限

### 1. 注解让代码变得臃肿

一个简单的handler函数可能只有10行，但上面的Swagger注解可能超过20行。这在一定程度上降低了代码的可读性。

**缓解方案**：
- 把handler的Swagger注解单独提取到文件头
- 只用最关键的注解（`@Summary`, `@Param`, `@Success`, `@Router`），其他的省略
- 使用Apifox或Postman等外部工具管理API文档，只在代码里维护最小化的注释

### 2. Swagger不是API设计工具

Swagger擅长"为已有接口生成文档"，但不擅长"先设计接口再写代码"。如果你做的是API First开发（先设计接口规范，前后端并行开发），应该用专门的API设计工具如Stoplight、Apicurio，或者直接写OpenAPI YAML规范，再通过Codegen生成骨架代码。

### 3. 生产环境隐藏Swagger

```go
if config.AppConfig.Server.Mode == "debug" {
    r.GET("/swagger/*any", ginSwagger.WrapHandler(swaggerFiles.Handler))
}
```

Swagger页面会暴露你所有的API路由和参数格式。在生产环境中，应该关闭Swagger或加IP白名单——不要让攻击者通过Swagger页面完整了解你的API结构。

---

## 本章小结

| 知识点 | 要点 |
|--------|------|
| OpenAPI / Swagger | API描述规范（OpenAPI）+ 工具生态（Swagger） |
| swaggo/swag | Go代码注释 → OpenAPI规范 + Swagger UI |
| 安装 | `go install github.com/swaggo/swag/cmd/swag@latest` |
| 全局注解 | `@title` / `@version` / `@host` / `@BasePath` 写在main.go |
| 接口注解 | `@Summary` / `@Param` / `@Success` / `@Failure` / `@Router` |
| @Param | `位置 参数名 类型 必填 "描述"`，位置=path/query/body/header |
| @Success | `状态码 {类型} 数据结构 "描述"` |
| swag init | 扫描代码生成 `docs/swagger.json` |
| gin-swagger | `ginSwagger.WrapHandler(swaggerFiles.Handler)` 挂载UI |
| 访问地址 | `http://host:port/swagger/index.html` |
| 安全 | 生产环境关闭Swagger或加IP白名单 |

> 🚀 下一章：第76章 · CORS与部署准备——API开发完成了，文档也有了，接下来要让前端能跨域调用、用安全头加固防护、优雅关闭服务、最后用压测工具验证你的服务能抗多少并发。

---
[← 上一章：74-错误码与统一异常处理](74-错误码与统一异常处理.md) | [下一章：76-CORS与部署准备 →](76-CORS与部署准备.md)
