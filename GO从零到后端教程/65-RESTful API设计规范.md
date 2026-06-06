# 第65章 · RESTful API设计规范

> "数据库学会了，现在让我们的Go程序通过HTTP接口把数据提供给外部调用。这就像你开了一家餐厅，后厨（数据库）准备好了所有食材和菜谱，现在你需要把菜单（API）递给客人，告诉他们怎么点菜、能点哪些菜。RESTful（一种用URL表示资源、用HTTP方法表示操作的API设计风格，详见附录I） API就是互联网世界最流行的'菜单设计规范'——照这个规范设计接口，全世界的前端工程师都能无缝调用。"

---

## 65.1 REST是什么

REST全称：**Representational State Transfer**，直译是"表现层状态转移"。

别被这个名字吓到。用大白话说：**把服务器上的"资源"通过HTTP协议暴露出来，客户端通过标准的HTTP方法来操作这些资源。**

### 一个比喻：自动售货机

想象一台自动售货机。它有若干行货架，每行放不同饮料：

- 你想看第3行有什么饮料 → **"查看"** 操作（对应HTTP GET）
- 你投币买了一瓶 → **"购买"** 操作（对应HTTP POST，创建订单）
- 管理员打开门把第3行的可乐全换成雪碧 → **"替换"** 操作（对应HTTP PUT）
- 管理员发现第3行有个标签写错了，只改了标签 → **"部分修改"**（对应HTTP PATCH）
- 管理员撤掉第3行，这行不卖饮料了 → **"删除"** 操作（对应HTTP DELETE）

这台售货机就是一个RESTful系统：
- **资源**（Resource）：每一行货架上的饮料（用URL表示，如 `/drinks/3`）
- **表现层**（Representation）：你用眼睛看到的饮料信息——名字、价格、库存（对应服务器返回的JSON数据）
- **状态转移**（State Transfer）：你操作了这个资源（买了一瓶，库存从10变成9），资源状态发生了改变

### REST的六大约束

REST之父Roy Fielding在2000年的博士论文中定义了REST架构的六大约束。我们不需要全背下来，但理解它们能帮你设计出更好的API：

| 约束 | 含义 | 餐厅比喻 |
|------|------|----------|
| **客户端-服务端** | 前端和后端分离，各自独立演进 | 服务员和厨师分开，换服务员不影响厨师做菜 |
| **无状态** | 每个请求独立，服务器不记住"上次是谁" | 每张点菜单都是独立的，厨师不需要记住"刚才那个客人点了什么" |
| **可缓存** | 响应可以标记为"可缓存"，减少重复请求 | "今日特价菜"贴墙上，不用每次都问服务员 |
| **统一接口** | 用标准HTTP方法操作资源 | 所有餐厅都分"点菜、催菜、买单"，顾客不用学新规则 |
| **分层系统** | 客户端不知道中间经过了代理还是负载均衡器 | 你不知道厨房有几个厨师，只管菜对不对 |
| **按需代码（可选）** | 服务器可以发送代码给客户端执行 | 服务员给你一张自助点餐的平板，上面有程序帮你点菜 |

---

## 65.2 URL设计：用名词，不要用动词

这是新手最容易犯的错。URL应该表示"**什么东西**"（名词/资源），而不是"**做什么**"（动词/操作）。

### 正确 vs 错误

```http
# ❌ 错误：用动词
GET /getUsers             获取用户列表
GET /getUserById?id=1     获取单个用户
POST /createUser          创建用户
POST /deleteUser          删除用户
POST /updateUserName      修改用户名

# ✅ 正确：用名词复数表示资源
GET /users                获取用户列表
GET /users/1              获取ID为1的用户
POST /users               创建用户
DELETE /users/1           删除ID为1的用户
PUT /users/1              完整替换ID为1的用户
PATCH /users/1            部分修改ID为1的用户
```

**为什么用名词复数？** 因为 `/users` 表示"用户集合"，`/users/1` 表示"用户集合中ID为1的那个"。这符合集合语义。

### 层级关系的URL设计

资源之间有层级关系时，用嵌套URL：

```http
GET /users/1/orders           获取用户1的所有订单
GET /users/1/orders/5         获取用户1的5号订单
POST /users/1/orders          为用户1创建新订单
GET /articles/10/comments     获取文章10的所有评论
GET /articles/10/comments/3   获取文章10的第3条评论
```

**嵌套不要太深**——URL层级越深越难维护。一般不超过 **资源/标识/子资源/标识** 四层。如果更深，考虑拆成独立的查询参数：

```http
# 太深，不推荐
GET /schools/3/classes/5/students/7/grades/1

# 更好的做法
GET /grades?student=7&class=5&school=3
```

### URL命名规范

| 规范 | 示例 | 说明 |
|------|------|------|
| 全小写 | `/users` 不是 `/Users` | URL区分大小写，惯例全小写 |
| 用连字符 | `/user-profiles` 不是 `/user_profiles` | 连字符比下划线更易读 |
| 不用文件扩展名 | `/users/1` 不是 `/users/1.json` | 用Accept头协商格式 |
| 集合用复数 | `/orders` 哪个用户都一样 | 英语习惯 |
| 结尾不加斜杠 | `/users` 不是 `/users/` | 统一习惯 |

---

## 65.3 HTTP方法对应CRUD

CRUD是数据操作的四个基本动作：Create（增）、Read（查）、Update（改）、Delete（删）。RESTful API用HTTP方法对应它们：

| 操作 | HTTP方法 | URL示例 | 请求体 | 安全 | 幂等 |
|------|---------|---------|--------|------|------|
| 查列表 | GET | `/users` | 无 | ✅ | ✅ |
| 查单个 | GET | `/users/1` | 无 | ✅ | ✅ |
| 新增 | POST | `/users` | 有 | ❌ | ❌ |
| 全量替换 | PUT | `/users/1` | 有 | ❌ | ✅ |
| 部分修改 | PATCH | `/users/1` | 有 | ❌ | ❌ |
| 删除 | DELETE | `/users/1` | 通常无 | ❌ | ✅ |

### 两个重要概念：安全性与幂等性

**安全性（Safe）**：这个请求**不会改变服务器上的资源**。只读操作。

- GET是安全的——你查10次用户列表，用户数据不会变。
- POST/PUT/PATCH/DELETE是不安全的——它们会改变数据。

**幂等性（Idempotent）**：同一个请求，执行1次和100次，效果一样。

- GET是幂等的——查1次和查100次返回同样的结果。
- PUT是幂等的——把用户1的名字设成"张三"，做1次和100次结果都是"张三"。
- DELETE是幂等的——删1次删除成功，删100次也是"已删除"状态。
- **POST不是幂等的**——每次POST `/users` 都会创建一条新数据，执行100次就多了100条记录。
- **PATCH通常也不是幂等的**——比如 `{"age": +1}` 这种相对修改。

### 各方法的详细说明

#### GET —— 查询

```http
GET /users?page=1&size=20&sort=created_at:desc
```

- 请求体为空（虽然HTTP协议允许GET带请求体，但强烈不建议）
- 参数通过**查询字符串**（Query String）传递
- 永远不应该改变服务器状态

#### POST —— 新增

```http
POST /users
Content-Type: application/json

{
  "name": "张三",
  "email": "zhangsan@example.com",
  "age": 25
}
```

- 向集合中新增一个资源
- 服务器自动分配ID并返回
- 成功返回 **201 Created**，响应头 `Location` 指向新资源URL

#### PUT —— 全量替换

```http
PUT /users/1
Content-Type: application/json

{
  "name": "李四",
  "email": "lisi@example.com",
  "age": 30
}
```

- 必须提供**所有字段**，缺失的字段会被设为默认值/空值
- "把这个资源整体换成我给你这版"

#### PATCH —— 部分修改

```http
PATCH /users/1
Content-Type: application/json

{
  "age": 31
}
```

- 只传**要修改的字段**，其他字段保持不变
- 在Go中实现时需要注意：如何区分"没传"和"传了空值"

#### DELETE —— 删除

```http
DELETE /users/1
```

- 通常无请求体
- 成功返回 204 No Content 或 200

---

## 65.4 状态码的正确使用

HTTP状态码是服务器告诉客户端"结果如何"的简短数字。正确使用状态码，让调用方一眼看懂发生了什么。

### 状态码分类

| 范围 | 类别 | 含义 | 餐厅比喻 |
|------|------|------|----------|
| 1xx | 信息 | 收到请求，继续处理 | "稍等，我在查" |
| 2xx | 成功 | 请求成功处理 | "您的菜好了" |
| 3xx | 重定向 | 需要进一步操作 | "宫保鸡丁卖完了，但我们有辣子鸡" |
| 4xx | 客户端错误 | 你的请求有问题 | "您点的菜不在菜单上" |
| 5xx | 服务端错误 | 服务器内部出问题了 | "厨师切到手了，今天做不了" |

### 常用状态码详解

#### 2xx 成功系列

```http
200 OK
```

一切正常。GET请求成功，PUT/PATCH修改成功，DELETE删除成功时都用这个。

```http
201 Created
```

资源创建成功。**仅用于POST成功时。** 通常响应头里会带 `Location: /users/128` 告诉你新资源的URL。

```http
204 No Content
```

请求成功，但没有内容返回。常用于DELETE成功时——删除完了，没什么好给你看的。也用于PATCH成功但不返回数据时。

#### 3xx 重定向系列

```http
301 Moved Permanently
```

资源永久搬家了。比如 `/v1/users` 迁移到了 `/v2/users`。浏览器会自动跳转，搜索引擎也会更新索引。

```http
302 Found / 307 Temporary Redirect
```

临时搬家。请求临时被重定向到另一个URL，但下次还是访问原地址。

#### 4xx 客户端错误系列

```http
400 Bad Request
```

你的请求格式不对。JSON格式错误、参数缺失、字段类型不对——这些都应该返回400。

```http
401 Unauthorized
```

你没登录，或者你的登录凭证已过期。这里的"Unauthorized"其实应该叫"Unauthenticated"（未认证），历史命名问题。

```http
403 Forbidden
```

你登录了，但你没有权限。比如普通用户试图访问管理员页面——你身份没问题，但权限不够。

```http
404 Not Found
```

你要找的资源不存在。用户ID=99999不存在、URL路径不存在——都用404。

#### 5xx 服务端错误系列

```http
500 Internal Server Error
```

服务器内部炸了。程序抛出未捕获的异常/panic、数据库连接断开、磁盘满了——凡是服务器自己的锅，都用500。

**重要原则：5xx错误不要把详细的错误堆栈暴露给客户端。** 攻击者能从堆栈信息中获取敏感信息。客户端只需要知道"服务器出错了"，具体的日志记录在服务器端即可。

```http
502 Bad Gateway
```

服务器是网关/代理，从上游服务收到了无效响应。比如Nginx转发请求给Go应用，但Go应用挂了没响应。

```http
503 Service Unavailable
```

服务暂时不可用。可能是维护中、过载、限流。通常带 `Retry-After` 头告诉客户端多久后重试。

```http
504 Gateway Timeout
```

网关超时。Nginx等代理在规定时间内没等到上游服务的响应。

### 状态码决策流程图

```
收到请求 → 参数格式对了吗？
              ↓ 没对 → 400 Bad Request
              ↓ 对了
          → 用户登录了吗？
              ↓ 没登录 → 401 Unauthorized
              ↓ 登录了
          → 用户有权限吗？
              ↓ 没权限 → 403 Forbidden
              ↓ 有权限
          → 资源存在吗？（对GET/PUT/DELETE/PATCH特定资源）
              ↓ 不存在 → 404 Not Found
              ↓ 存在
          → 业务逻辑正确吗？
              ↓ 有问题 → 根据具体情况返回对应状态码
              ↓ 没问题
          → 是POST创建吗？
              ↓ 是 → 201 Created
              ↓ 不是 → 200 OK（或204 No Content）
```

---

## 65.5 统一响应格式设计实战

如果你的API有时返回 `{"user": ...}`，有时返回 `"deleted"`，有时直接返回一个数字——调用方会疯掉。你必须设计一个**统一的响应信封**，包裹所有响应数据。

### 标准三段式响应格式

```json
{
  "code": 0,
  "msg": "success",
  "data": {
    "id": 1,
    "name": "张三",
    "email": "zhangsan@example.com"
  }
}
```

- **code**：业务状态码。`0` 表示成功，非0表示失败（具体数字区分错误类型）
- **msg**：给开发者看的提示信息。成功时 `"success"` 或 `"ok"`，失败时给具体原因
- **data**：实际的业务数据。成功时放数据，失败时通常为 `null`

### Go代码实现

（以下用Gin框架示范，Gin语法的详细讲解从下一章开始，这里先感受一下代码风格）

```go
package main

import (
	"net/http"

	"github.com/gin-gonic/gin"
)

type Response struct {
	Code int         `json:"code"`
	Msg  string      `json:"msg"`
	Data interface{} `json:"data"`
}

func Success(c *gin.Context, data interface{}) {
	c.JSON(http.StatusOK, Response{
		Code: 0,
		Msg:  "success",
		Data: data,
	})
}

func Error(c *gin.Context, code int, msg string) {
	c.JSON(http.StatusOK, Response{
		Code: code,
		Msg:  msg,
		Data: nil,
	})
}
```

注意：`Error` 函数里，HTTP状态码仍然是 `200`（`http.StatusOK`），而业务错误码通过响应体里的 `code` 字段区分。这是一个常见做法——让HTTP层面只关注协议是否正常完成，业务层面的错误由响应体中的业务码表达。

### 分页列表的响应格式

查询列表不能一股脑把几十万条数据全返回。必须分页：

```json
{
  "code": 0,
  "msg": "success",
  "data": {
    "items": [
      { "id": 1, "name": "张三" },
      { "id": 2, "name": "李四" }
    ],
    "total": 1523,
    "page": 1,
    "page_size": 20
  }
}
```

```go
type PageData struct {
	Items    interface{} `json:"items"`
	Total    int64       `json:"total"`
	Page     int         `json:"page"`
	PageSize int         `json:"page_size"`
}
```

---

## 65.6 API版本管理

你的API上线后有几百个客户端在调用。某天你要改一个接口的返回格式——怎么改才不让已有的客户端挂掉？答案：**版本管理**。

### 三种常见方式

#### 方案一：URL路径（最常用，推荐）

```http
GET /api/v1/users
GET /api/v2/users
```

优点：一眼看出API版本，调试友好，浏览器直接能访问。
缺点：每个版本都是完整的独立路由组。

（以下用Gin框架示范，Gin语法的详细讲解从下一章开始，这里先感受一下代码风格）

```go
v1 := r.Group("/api/v1")
{
    v1.GET("/users", handleV1Users)
}

v2 := r.Group("/api/v2")
{
    v2.GET("/users", handleV2Users)
}
```

#### 方案二：请求头

```http
GET /api/users
Accept: application/vnd.myapp.v2+json
```

或自定义头：

```http
GET /api/users
API-Version: 2
```

优点：URL简洁。
缺点：调试不便（浏览器的地址栏里看不到版本），缓存策略复杂。

#### 方案三：查询参数

```http
GET /api/users?version=2
```

优点：极简实现。
缺点："污染"了查询参数，违反了URL表示"资源"的原则，不推荐用于生产。

### 版本号策略

| 策略 | 示例 | 说明 |
|------|------|------|
| 大版本号 | v1, v2, v3 | 不兼容的变更用新版本 |
| 日期 | 2024-01-01 | AWS风格，表示截至该日期的API规范 |
| 语义化 | v1.2 | 很少用于URL版本 |

**黄金法则：永远不要修改已发布API的行为。** 需要改就发布新版本，给老版本留足够的废弃过渡期。

---

## 🤔 想多一点：RESTful真的完美吗？

RESTful设计规范很美，但它不是万能的。实际开发中你会遇到这些困境：

### 1. 有些操作很难映射到CRUD

"用户重置密码" —— 是PUT？PATCH？POST？

常见的做法是定义一个"动作端点"：

```http
POST /users/1/reset-password
```

这打破了"只用名词"的规则，但这是务实的妥协。关键是**团队内部统一这种例外做法**。

### 2. 嵌套资源的REST诅咒

数据之间有复杂关系时，URL可能会变得很长且歧义：

```http
GET /departments/5/employees/12/projects/3/tasks/7/comments
```

这种URL应该拆成多个独立请求，或者用GraphQL。

### 3. REST vs GraphQL vs gRPC

| 维度 | REST | GraphQL | gRPC |
|------|------|---------|------|
| 设计理念 | 资源导向 | 查询导向 | 服务/方法导向 |
| 数据格式 | JSON/XML | JSON | Protobuf（二进制） |
| 学习曲线 | 低 | 中 | 中高 |
| 性能 | 好 | 可能有N+1问题 | 极高 |
| 浏览器友好 | ✅ | ✅ | ❌（需要grpc-web） |
| 前后端耦合 | 低 | 中 | 高 |
| 适合场景 | 通用API | 复杂数据查询 | 微服务内部调用 |

**作为新手，先扎扎实实掌握RESTful。** 它是基础中的基础，理解了REST，再学GraphQL和gRPC就轻松很多。

---

## 本章小结

| 知识点 | 要点 |
|--------|------|
| REST | Representational State Transfer，用HTTP方法操作资源 |
| URL设计 | 名词复数 `/users`，层级关系 `/users/1/orders`，不用动词 `/getUsers` |
| HTTP方法 | GET查 / POST增 / PUT全量替 / PATCH部分改 / DELETE删 |
| 安全性 | 请求不改变服务器状态（GET是安全的） |
| 幂等性 | 执行1次和100次效果相同（GET/PUT/DELETE幂等，POST不幂等） |
| 状态码 | 2xx成功 / 3xx重定向 / 4xx客户端错 / 5xx服务端错 |
| 201 Created | 资源创建成功专用，带Location头 |
| 204 No Content | 成功但不返回内容，常用于DELETE |
| 401/403 | 401未认证（没登录），403没权限（登录了但不让看） |
| 统一响应 | `{code, msg, data}` 三段式，业务错和HTTP状态码分离 |
| 分页响应 | `{items, total, page, page_size}` 封装在data中 |
| 版本管理 | URL路径 `/v1/users` 最常用最推荐 |

> 🚀 下一章：第66章 · Gin框架入门——Go语言最快最流行的Web框架。我们将用10分钟写出人生第一个HTTP服务器，并且理解Gin比标准库快40倍的秘密。

---
[← 上一章：64-数据库篇总结](64-数据库篇总结/) | [下一章：66-Gin框架入门 →](66-Gin框架入门/)
