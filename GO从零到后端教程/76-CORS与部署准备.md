# 第76章 · CORS与部署准备

> "API写完了，文档也有了，本地测试一切正常。但当前端同事从浏览器里调用你的接口时——报错了。浏览器的控制台里赫然写着：'has been blocked by CORS（跨域资源共享，浏览器安全机制，详见附录I） policy'。别慌，这不是你的程序出了bug，这是浏览器的安全机制在保护用户。这一章我们解决跨域（浏览器禁止一个域名的页面请求另一个域名的数据，详见附录I）问题，然后给服务加上安全头、优雅关闭、最后用压测工具踩一脚'油门'，看看你的服务到底能抗多少流量。"

---

## 76.1 同源策略

### 什么是同源

浏览器有一个铁律：**两个URL只有协议、域名、端口号完全相同，才算"同源"**。

| URL A | URL B | 是否同源 | 原因 |
|-------|-------|---------|------|
| `http://example.com` | `http://example.com/users` | ✅ | 同协议、同域名、同端口 |
| `http://example.com` | `https://example.com` | ❌ | 协议不同（http vs https） |
| `http://example.com` | `http://api.example.com` | ❌ | 域名不同（子域名也不行） |
| `http://example.com:80` | `http://example.com:8080` | ❌ | 端口不同 |

### 同源策略保护什么

假设你登录了网银 `www.bank.com`，浏览器里存着你的登录Cookie。此时你又打开了一个恶意网站 `www.evil.com`。如果没有同源策略，`www.evil.com` 的JavaScript可以向 `www.bank.com` 发请求，读取你的账户余额、发起转账——因为浏览器会自动带上你的Cookie。

**同源策略就是浏览器的一道防火墙**：默认情况下，一个源的JavaScript不能访问另一个源的资源。

### 跨域问题的本质

前后端分离是现代Web开发的标配：
- 前端：`http://localhost:3000`（Vue/React开发服务器）
- 后端：`http://localhost:8080`（Gin服务）

端口不同 → 不同源 → 浏览器拦截前端请求 → CORS错误。

**解决方案不是关闭浏览器的安全策略**（用户不会这么做），而是让后端在响应头中告诉浏览器："我允许来自 `localhost:3000` 的请求"。

---

## 76.2 Gin CORS中间件

### 安装

```bash
go get github.com/gin-contrib/cors
```

### 基础配置

```go
import (
    "time"

    "github.com/gin-contrib/cors"
    "github.com/gin-gonic/gin"
)

func main() {
    r := gin.Default()

    r.Use(cors.New(cors.Config{
        AllowOrigins:     []string{"http://localhost:3000", "https://myapp.com"},
        AllowMethods:     []string{"GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"},
        AllowHeaders:     []string{"Origin", "Content-Type", "Authorization"},
        ExposeHeaders:    []string{"Content-Length", "X-Request-ID"},
        AllowCredentials: true,
        MaxAge:           12 * time.Hour,
    }))

    r.Run()
}
```

### 配置参数详解

| 参数 | 含义 | 示例 |
|------|------|------|
| `AllowOrigins` | 允许哪些域名跨域 | `[]string{"http://localhost:3000"}` |
| `AllowMethods` | 允许哪些HTTP方法 | `[]string{"GET", "POST"}` |
| `AllowHeaders` | 允许哪些请求头 | `[]string{"Authorization", "Content-Type"}` |
| `ExposeHeaders` | 允许JS读取哪些响应头 | `[]string{"X-Request-ID"}` |
| `AllowCredentials` | 是否允许携带Cookie/Authorization | `true` |
| `MaxAge` | 预检请求缓存时间 | `12 * time.Hour` |

### AllowOrigins vs AllowOriginFunc

`AllowOrigins` 是静态白名单，写死了允许的域名。如果允许多个子域名（`*.myapp.com`），用 `AllowOriginFunc`：

```go
r.Use(cors.New(cors.Config{
    AllowOriginFunc: func(origin string) bool {
        return strings.HasSuffix(origin, ".myapp.com") || origin == "http://localhost:3000"
    },
    AllowMethods: []string{"GET", "POST", "PUT", "DELETE"},
}))
```

### 允许所有源（仅限开发环境）

```go
r.Use(cors.Default())
```

`cors.Default()` 等于 `AllowAllOrigins: true`——允许任何来源跨域请求。**绝不要在生产环境使用**，这等于关掉了同源策略保护。

### 开发环境 vs 生产环境

```go
if config.AppConfig.Server.Mode == "debug" {
    r.Use(cors.Default())
} else {
    r.Use(cors.New(cors.Config{
        AllowOrigins: config.AppConfig.CORS.AllowedOrigins,
        AllowMethods: []string{"GET", "POST", "PUT", "DELETE"},
        AllowHeaders: []string{"Authorization", "Content-Type"},
        MaxAge:       12 * time.Hour,
    }))
}
```

---

## 76.3 预检请求（Preflight）

### 什么是预检请求

当你发起一个"非简单请求"时，浏览器会先自动发一个 `OPTIONS` 请求去问服务器："我可以用PUT方法吗？可以带Authorization头吗？" ——这就是预检请求。

### 简单请求 vs 非简单请求

**简单请求**（不发OPTIONS预检）同时满足三个条件：

1. 方法只能是 `GET`、`HEAD`、`POST`
2. 只能带这些请求头：`Accept`、`Accept-Language`、`Content-Language`、`Content-Type`（且`Content-Type` 只能为 `application/x-www-form-urlencoded`、`multipart/form-data`、`text/plain` 三者之一）
3. 没有 `ReadableStream`

**只要有一条不满足，浏览器就发OPTIONS预检**：

```
客户端                                      服务器
  │                                          │
  │── OPTIONS /api/users ─────────────────→  │  "我能用PUT吗？"
  │   Origin: http://localhost:3000           │
  │   Access-Control-Request-Method: PUT      │
  │                                          │
  │←─ 204 No Content ──────────────────────  │  "可以"
  │   Access-Control-Allow-Origin: ...        │
  │   Access-Control-Allow-Methods: PUT       │
  │                                          │
  │── PUT /api/users/1 ───────────────────→  │  真正的请求
  │   Content-Type: application/json          │
  │   {"name":"新名字"}                       │
  │                                          │
  │←─ 200 OK ────────────────────────────── │
```

### MaxAge的作用

每次跨域请求都发一次OPTIONS预检，会对性能有影响。`MaxAge` 告诉浏览器："这个预检结果有效12小时，这段时间内不用再问了"。

```go
MaxAge: 12 * time.Hour,
```

对应的响应头：

```http
Access-Control-Max-Age: 43200
```

---

## 76.4 安全头

安全响应头是后端可以主动设置的HTTP头，告诉浏览器启用额外的安全保护。

### X-Content-Type-Options

```go
r.Use(func(c *gin.Context) {
    c.Header("X-Content-Type-Options", "nosniff")
    c.Next()
})
```

禁止浏览器"猜测"资源的MIME类型。如果服务器声明这是 `text/plain`，即使内容看起来像HTML，浏览器也不会把它当HTML执行——防止MIME类型嗅探攻击。

### X-Frame-Options

```go
r.Use(func(c *gin.Context) {
    c.Header("X-Frame-Options", "DENY")
    c.Next()
})
```

禁止其他网站用 `<iframe>` 嵌入你的页面。防止**点击劫持**攻击——攻击者在透明iframe中叠放你的页面，用户以为在点正常按钮，实际在点iframe中的恶意操作。

取值：
- `DENY` — 完全禁止被iframe嵌入
- `SAMEORIGIN` — 只允许被同源页面嵌入
- `ALLOW-FROM uri` — 只允许被指定URI嵌入（已废弃）

### X-XSS-Protection

```go
c.Header("X-XSS-Protection", "1; mode=block")
```

启用浏览器的XSS过滤器（跨站脚本攻击防护）。当浏览器检测到XSS攻击时，阻止页面加载。

### Strict-Transport-Security（HSTS）

```go
c.Header("Strict-Transport-Security", "max-age=63072000; includeSubDomains; preload")
```

强制浏览器在指定时间内只能用HTTPS访问你的网站，拒绝HTTP连接。`max-age` 单位是秒，`63072000` = 2年。

**注意**：HSTS只在HTTPS环境下有效。如果你的服务还在HTTP阶段，不要设置这个头。

### 整合为一个中间件

```go
func SecurityHeaders(c *gin.Context) {
    c.Header("X-Content-Type-Options", "nosniff")
    c.Header("X-Frame-Options", "DENY")
    c.Header("X-XSS-Protection", "1; mode=block")

    if c.Request.TLS != nil {
        c.Header("Strict-Transport-Security", "max-age=63072000; includeSubDomains; preload")
    }

    c.Next()
}
```

---

## 76.5 优雅关闭

### 为什么需要优雅关闭

当你按 `Ctrl+C` 或执行 `kill` 命令时，Go程序默认会立即终止——不管当时有多少请求还在处理中。正在支付中的用户、正在上传文件的操作，都会戛然而止。

**优雅关闭**就是：收到关闭信号后，不再接受新请求，等当前正在处理的请求全部完成，再退出程序。

以下优雅关闭代码综合运用了goroutine+channel+signal+context（第34-37章），初学者可先跳过，需要时再回来。

### 实现

```go
package main

import (
    "context"
    "net/http"
    "os"
    "os/signal"
    "syscall"
    "time"

    "github.com/gin-gonic/gin"
    "go.uber.org/zap"
)

func main() {
    logger, _ := zap.NewProduction()
    defer logger.Sync()

    r := gin.New()
    r.Use(gin.Recovery())

    r.GET("/hello", func(c *gin.Context) {
        c.JSON(200, gin.H{"msg": "hello"})
    })

    srv := &http.Server{
        Addr:    ":8080",
        Handler: r,
    }

    go func() {
        logger.Info("服务启动", zap.String("addr", ":8080"))
        if err := srv.ListenAndServe(); err != nil && err != http.ErrServerClosed {
            logger.Fatal("服务启动失败", zap.Error(err))
        }
    }()

    quit := make(chan os.Signal, 1)
    signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
    <-quit

    logger.Info("正在关闭服务...")

    ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
    defer cancel()

    if err := srv.Shutdown(ctx); err != nil {
        logger.Fatal("服务关闭异常", zap.Error(err))
    }

    logger.Info("服务已安全退出")
}
```

### 流程解析

```
服务启动（goroutine中运行）
  ↓
信号监听（阻塞等待）
  ↓
收到 SIGINT（Ctrl+C）或 SIGTERM（kill）
  ↓
通知 srv.Shutdown：
  - 关闭监听端口（不再接受新请求）
  - 等待已有请求完成
  - 最多等待30秒超时
  ↓
所有请求处理完或超时
  ↓
程序退出
```

### 测试优雅关闭

启动服务后，打开浏览器访问 `http://localhost:8080/hello`，同时按 `Ctrl+C`。如果你在handler里加了 `time.Sleep(5 * time.Second)` 模拟慢请求，你会看到程序并不会立即退出，而是等5秒处理完后才退出。

---

## 76.6 压测起步：wrk

你的API开发完了，但你能保证1000人同时访问时不崩吗？需要压测来验证。

### wrk安装

wrk是一个高性能HTTP压测工具，用C语言编写：

- **macOS**：`brew install wrk`
- **Ubuntu/Debian**：`sudo apt install wrk`
- **Windows**：从GitHub下载编译好的 `.exe`，或使用WSL（Windows Subsystem for Linux，WSL是Windows内置的Linux子系统）

### 基本用法

```bash
wrk -t4 -c100 -d30s http://localhost:8080/hello
```

| 参数 | 含义 |
|------|------|
| `-t4` | 使用4个线程 |
| `-c100` | 保持100个并发连接 |
| `-d30s` | 持续压测30秒 |

### 输出解读

```
Running 30s test @ http://localhost:8080/hello
  4 threads and 100 connections
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency     2.34ms    1.23ms  15.67ms   78.50%
    Req/Sec    10.23k     1.45k   15.32k    72.00%
  1224567 requests in 30.00s, 147.08MB read
Requests/sec:  40818.87
Transfer/sec:      4.90MB
```

| 指标 | 含义 | 这个结果的含义 |
|------|------|---------------|
| Latency Avg | 平均响应延迟 | 每个请求平均2.34ms完成 |
| Latency Stdev | 延迟标准差 | 大部分请求延迟在1.23ms范围内波动 |
| Latency Max | 最大延迟 | 最慢的一个请求用了15.67ms |
| Req/Sec | 每秒完成请求数 | 每秒处理约40818个请求 |
| Requests/sec | 总QPS | 40818 QPS |
| Transfer/sec | 总吞吐量 | 每秒传输4.9MB数据 |

**40818 QPS** 对于Gin来说是非常典型的数值——这就是为什么第66章说Gin比标准库快40倍。

### 带请求体压测（POST）

wrk本身不支持POST带JSON请求体。用 `wrk` 的Lua脚本扩展：

`post.lua`：

```lua
wrk.method = "POST"
wrk.body   = '{"name":"张三","email":"zhangsan@example.com"}'
wrk.headers["Content-Type"] = "application/json"
```

执行：

```bash
wrk -t4 -c100 -d30s -s post.lua http://localhost:8080/users
```

### 进阶：hey

如果wrk在Windows上安装困难，可以用Go写的 [hey](https://github.com/rakyll/hey)：

```bash
go install github.com/rakyll/hey@latest

hey -n 10000 -c 100 -m POST -H "Content-Type: application/json" -d '{"name":"test"}' http://localhost:8080/users
```

### 压测经验法则

| QPS级别 | 含义 | 建议 |
|---------|------|------|
| < 1000 | 性能瓶颈明显 | 检查数据库查询是否有N+1问题、是否缺索引 |
| 1000-5000 | 常规水平 | 中小业务够用，检查Redis缓存覆盖率 |
| 5000-20000 | 良好 | 大部分创业公司够用 |
| > 20000 | 优秀 | 注意GC停顿优化、连接池配置 |

---

## 🤔 想多一点：生产环境checklist

在服务正式上线前，确认以下事项：

| 检查项 | 状态 |
|--------|------|
| GIN_MODE=release | ☐ |
| CORS配置了生产域名白名单 | ☐ |
| Swagger页面已关闭或加了IP白名单 | ☐ |
| 日志等级设置为Info及以上 | ☐ |
| Recovery中间件捕获panic | ☐ |
| 优雅关闭已实现 | ☐ |
| 安全头已设置（nosniff/frame/xss） | ☐ |
| 数据库密码、API密钥不在代码中（用环境变量） | ☐ |
| 健康检查端点 `/health` 可用 | ☐ |
| 压测通过，QPS满足预期 | ☐ |
| HTTP→HTTPS重定向（如适用） | ☐ |

---

## 本章小结

| 知识点 | 要点 |
|--------|------|
| 同源策略 | 协议+域名+端口完全相同才算同源，浏览器拦截跨域请求 |
| CORS | 服务器在响应头声明允许哪些源跨域访问 |
| gin-contrib/cors | `cors.New(cors.Config{...})` 配置CORS策略 |
| AllowOrigins | 静态白名单，`AllowOriginFunc` 动态校验 |
| 预检请求 | 浏览器对非简单请求先发OPTIONS询问服务器 |
| MaxAge | 预检结果缓存时间，减少重复的OPTIONS请求 |
| 安全头 | nosniff(禁MIME嗅探) / DENY(禁iframe嵌入) / XSS防护 / HSTS |
| 优雅关闭 | `signal.NotifyContext` + `srv.Shutdown`，30秒超时等请求完成 |
| wrk压测 | `-t` 线程数 / `-c` 并发数 / `-d` 持续时间 |
| QPS解读 | Latency平均延迟 / Req/Sec每秒请求数 / Transfer每秒吞吐量 |
| 上线checklist | release模式、CORS白名单、关闭Swagger、安全头、环境变量管理 |

> 🚀 恭喜你完成了第四篇——Web框架与API开发的全部12章！从RESTful设计规范到Gin框架全家桶，再到CORS、安全加固和压测，你现在已经有能力独立开发生产级的Go Web服务了。第五篇将带你进入"用户认证与鉴权"的世界——JWT、OAuth2.0、SSO单点登录、CAS……敬请期待！

---
[← 上一章：75-API文档Swagger](75-API文档Swagger/) | [下一章：77-认证基础 →](77-认证基础/)
