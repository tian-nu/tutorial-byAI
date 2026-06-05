# 第66章 · Gin框架入门

> "你当然可以用Go标准库的 `net/http` 来写Web服务——就像你可以用锤子和锯子徒手造家具。但当你需要造一个衣柜、一张床、一套沙发时，用电动工具更好。Gin框架（一套帮你省去重复劳动、快速搭建Web服务的代码库，详见附录I）就是Go Web开发中的'电动工具'：更快、更省力、更不容易出错。"

---

## 66.1 Gin是什么

Gin是一个用Go语言编写的**高性能HTTP Web框架**。它最大的卖点是**快**——官方benchmark显示它比标准库 `net/http` 快40倍。

### 为什么Gin这么快？

不是因为标准库写得烂，而是因为Gin用了一个**HTTP路由器**（router）——`httprouter`。这个路由器内部使用了一种叫 **Radix Tree**（基数树）的数据结构来存储和匹配路由。

**比喻：文件夹系统 vs 搜索引擎**

标准库的 `http.HandleFunc` 有点像在一个文件夹里顺序翻文件，每个请求来了都要逐一比对路径是否匹配。Gin的Radix Tree则像一个索引——URL的每一段（用 `/` 分隔）都是树的层级节点，匹配时可以跳过不相关的分支。

```
标准库：逐个比对
  ↓ "是 / 开头吗？"→"是 /users 吗？"→"是 /users/123 吗？"→...
  
Gin的Radix Tree：
    /
   └─ users
       ├─ /:id
       │   └─ orders  → 匹配 /users/123/orders
       └─ /search     → 匹配 /users/search
```

Trie树的匹配复杂度是 **O(URL长度)**，与注册的路由数量无关——你注册100条路由和100万条路由，匹配速度几乎一样。

### Gin的定位

| 特性 | 说明 |
|------|------|
| 极简核心 | 只做路由、中间件、请求/响应处理 |
| 无ORM | 不内置数据库操作，你自由选择GORM/sqlx |
| 无模板强制 | 可以用Go原生模板，也可以纯API返回JSON |
| 无脚手架 | 不像Ruby on Rails有各种generator |
| 中间件生态 | Logger、Recovery、CORS、Gzip、限流等开箱即用 |

Gin的设计哲学是"**给你最快的核心，其他你自己选**"。它不强迫你用什么数据库、什么模板引擎、什么项目结构——这既是自由，也是需要你在后续章节中学好怎么组织代码的原因。

---

## 66.2 安装Gin

安装Gin之前，确保你已经初始化了Go模块：

```bash
mkdir myweb
cd myweb
go mod init myweb
```

然后安装Gin：

```bash
go get -u github.com/gin-gonic/gin
```

这条命令会把Gin的源码下载到 `$GOPATH/pkg/mod/` 目录下，并在 `go.mod` 中添加依赖记录：

```
module myweb

go 1.21

require github.com/gin-gonic/gin v1.9.1
```

`go.sum` 文件也会自动生成，记录每个依赖包的校验和，防止被篡改。

**确认安装成功**：在你的代码里写 `import "github.com/gin-gonic/gin"`，IDE没有报红就说明装好了。

---

## 66.3 Hello World完整示例

创建一个 `main.go` 文件：

```go
package main

import (
	"net/http"

	"github.com/gin-gonic/gin"
)

func main() {
	r := gin.Default()

	r.GET("/hello", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{
			"message": "Hello, 世界!",
		})
	})

	r.Run()
}
```

运行：

```bash
go run main.go
```

终端输出：

```
[GIN-debug] [WARNING] Creating an Engine instance with the Logger and Recovery middleware already attached.

[GIN-debug] [WARNING] Running in "debug" mode. Switch to "release" mode in production.
 - using env:   export GIN_MODE=release
 - using code:  gin.SetMode(gin.ReleaseMode)

[GIN-debug] GET    /hello                    --> main.main.func1 (3 handlers)
[GIN-debug] [WARNING] You trusted all proxies, this is NOT safe. We recommend you to set a value.
Please check https://pkg.go.dev/github.com/gin-gonic/gin#readme-don-t-trust-all-proxies for details.
[GIN-debug] Environment variable PORT is undefined. Using port :8080 by default
[GIN-debug] Listening and serving HTTP on :8080
```

现在打开浏览器访问 `http://localhost:8080/hello`，你会看到：

```json
{"message":"Hello, 世界!"}
```

### 逐行拆解

```go
r := gin.Default()
```

`gin.Default()` 创建了一个Gin引擎（Engine）实例，**同时自动挂载了Logger和Recovery两个中间件**。Logger会打印每个请求的耗时和状态码；Recovery会在你的代码panic时自动捕获，防止整个进程挂掉。

```go
r.GET("/hello", func(c *gin.Context) {
    ...
})
```

`r.GET` 注册了一个路由：当收到对 `/hello` 的GET请求时，执行这个匿名函数。函数接收一个 `*gin.Context` 类型的参数。

```go
c.JSON(http.StatusOK, gin.H{
    "message": "Hello, 世界!",
})
```

`c.JSON` 把Go的map序列化成JSON返回给客户端。`http.StatusOK` 是常量 `200`。`gin.H` 是 `map[string]interface{}` 的快捷别名。

```go
r.Run()
```

启动HTTP服务器，默认监听 `0.0.0.0:8080`。

---

## 66.4 启动方式

### 默认端口

```go
r.Run()
```

监听 `127.0.0.1:8080`（或 `0.0.0.0:8080`，取决于Gin版本和操作系统）。

### 自定义端口

```go
r.Run(":9090")
```

监听 `0.0.0.0:9090`。

### 指定IP和端口

```go
r.Run("127.0.0.1:3000")
```

只监听本机回环地址（只有本机能访问，外部无法连接）。

### 只监听不启动（用于测试）

```go
r.Run(":8080")
```

Gin 1.x 的 `Run` 内部调用了 `http.ListenAndServe`。如果你想手动控制 `http.Server`（比如为了优雅关闭），可以：

```go
srv := &http.Server{
    Addr:    ":8080",
    Handler: r,
}
srv.ListenAndServe()
```

### 生产模式 vs 调试模式

Gin默认运行在 **debug** 模式，会打印大量路由注册信息和请求日志。上线时切换到 **release** 模式：

```go
gin.SetMode(gin.ReleaseMode)
r := gin.New()
```

Release模式下不再打印debug信息，性能也有微小提升。

---

## 66.5 Gin的核心设计：Context

每收到一个HTTP请求，Gin都会创建一个 `*gin.Context` 对象。这个对象贯穿整个请求处理生命周期——从第一个中间件到最后返回响应。你可以把它理解为"**本次请求的临时工作台**"，上面放着本次请求的所有信息。

### Context是什么

用餐厅比喻：每个客人进餐厅时，服务员拿一个空托盘（Context）。他在托盘上放：点菜单（请求体）、客人备注（请求头）、忌口信息（查询参数）。厨师（handler）从托盘上取需要的东西，做好菜（响应数据）放回托盘，服务员端走（返回给客户端）。客人走了，托盘清空，下一个客人用新托盘。

### Context包含什么

| 类别 | 内容 | 获取方式 |
|------|------|---------|
| 请求信息 | URL路径、查询参数、请求体、请求头 | `c.Request` |
| 路径参数 | `/users/:id` 中的 `id` | `c.Param("id")` |
| 查询参数 | `/users?page=1` 中的 `page` | `c.Query("page")` |
| 表单数据 | POST表单提交的字段 | `c.PostForm("name")` |
| 上传文件 | multipart/form-data中的文件 | `c.FormFile("avatar")` |
| 响应工具 | 返回JSON/XML/字符串/HTML | `c.JSON()`, `c.XML()`, `c.String()` |
| 键值存储 | 在中间件和handler间传递数据 | `c.Set("key", value)`, `c.Get("key")` |
| 错误管理 | 收集处理过程中的错误 | `c.Error(err)` |
| 请求上下文 | 标准库的 `context.Context` | `c.Request.Context()` |

### Context的键值存储

Gin的Context有一个内置的 **Keys** map，可以在中间件里存数据，在后续的handler里取出来：

```go
func AuthMiddleware(c *gin.Context) {
    user := GetUserFromToken(c.GetHeader("Authorization"))
    c.Set("user", user)
    c.Next()
}

func ProfileHandler(c *gin.Context) {
    user, exists := c.Get("user")
    if !exists {
        c.JSON(401, gin.H{"msg": "未登录"})
        return
    }
    c.JSON(200, user)
}
```

这是**在同一个请求内**的各处理函数间传递数据的最常见方式。

### Context的生命周期

```
客户端发起请求
  ↓
Gin创建Context对象
  ↓
Logger中间件（记录开始时间）
  ↓
你的中间件1 → c.Next() → 
  ↓
你的中间件2 → c.Next() →
  ↓
Handler处理函数（读请求、写响应）
  ↓
← 回到中间件2（c.Next()之后的代码执行）
  ↓
← 回到中间件1（c.Next()之后的代码执行）
  ↓
← Logger中间件（计算耗时、打印日志）
  ↓
Gin把Response写入网络连接
  ↓
Context对象被回收（可被GC）
```

**关键理解**：一个 `*gin.Context` 只服务于一个请求。请求结束，Context也随之失效。不要在请求之外（比如存到全局变量、在goroutine中异步使用）引用它——会导致竞态条件和数据错乱。（Goroutine详见第34章）

---

## 🤔 想多一点：`gin.Default()` vs `gin.New()`

Gin提供了两个创建引擎的函数：

```go
r := gin.Default()   // 带有Logger和Recovery中间件
r := gin.New()       // 纯裸引擎，零中间件
```

什么时候用哪个？

| 场景 | 推荐 |
|------|------|
| 学习、开发调试 | `gin.Default()` |
| 自定义中间件组合 | `gin.New()` + 手动添加 |
| 只需要Recovery不需要Logger | `gin.New()` + `r.Use(gin.Recovery())` |
| 单元测试 | `gin.New()`（不需要日志干扰测试输出） |

`gin.Default()` 的源码其实就两行：

```go
func Default() *Engine {
    engine := New()
    engine.Use(Logger(), Recovery())
    return engine
}
```

所以它不是什么"特殊版"，就是 `New()` + 两个最常用的中间件。

---

## 本章小结

| 知识点 | 要点 |
|--------|------|
| Gin | Go的高性能Web框架，基于 `httprouter`（Radix Tree路由） |
| 速度 | 比 `net/http` 快40倍，路由匹配复杂度 O(URL长度) |
| 安装 | `go get -u github.com/gin-gonic/gin` |
| gin.Default() | 创建引擎 + 自动挂载Logger和Recovery中间件 |
| gin.New() | 创建裸引擎，无中间件 |
| r.GET(path, handler) | 注册GET路由，handler接收 `*gin.Context` |
| c.JSON(code, data) | 返回JSON响应，`gin.H` = `map[string]interface{}` |
| r.Run() | 启动服务器，默认 `:8080`，可指定 `:9090` |
| Release模式 | `gin.SetMode(gin.ReleaseMode)`，生产环境必用 |
| Context | 每个请求独立的"临时工作台"，贯穿全部中间件→handler |
| c.Set/c.Get | 在同一请求的中间件和handler间传递数据 |

> 🚀 下一章：第67章 · 路由与路由组——Gin的"交通管制系统"。你会学到如何优雅地组织几十上百条路由，怎么用路由组给接口分版本、怎么接收路径中的动态参数 `/users/:id`。

---
[← 上一章：65-RESTful API设计规范](65-RESTful API设计规范.md) | [下一章：67-路由与路由组 →](67-路由与路由组.md)
