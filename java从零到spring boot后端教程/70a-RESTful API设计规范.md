# 第70a章 · RESTful API设计规范

> 你走进一家餐厅，不会冲进后厨自己颠勺——你坐在桌前，对服务员说"一份宫保鸡丁"。服务员把这个信息递给后厨（创建订单），过一会儿端着菜回来（返回资源）。你吃完说"买单"，服务员递上账单。整个过程中，你只需要知道**名词**（宫保鸡丁、账单）和几个**动词**（点、买单），完全不需要了解后厨怎么运作。RESTful API就是你和后端之间的"餐厅服务员"——一种约定好的请求方式。**本章内容语言无关，适用于所有后端框架（Java / Go / Python / Node.js 等）。**

---

## 本章目标
- 理解REST是什么，以及它的六大设计约束
- 掌握URL设计原则：用名词，不用动词；用层级关系表达资源归属
- 将HTTP方法与CRUD操作建立一一对应关系
- 熟记最常用的HTTP状态码及其使用场景
- 设计统一的JSON请求与响应格式
- 为Todo应用设计一套完整的RESTful API（第119章第52节项目伏笔）
- 为下一章Spring Boot中的 `@GetMapping` / `@PostMapping` 建立概念基础

---

## 70a.1 REST是什么

### 70a.1.1 自动售货机比喻

你站在一台自动售货机前。机器上有几排按钮，每个按钮对应一种饮料。

```
你按下"A3"（可口可乐）    →  机器掉出一罐可口可乐
你按下"B1"（矿泉水）      →  机器掉出一瓶矿泉水
```

你不需要知道机器内部的传送带怎么转动、冷藏系统怎么工作。你只需要知道：
- **资源（Resource）**：每瓶饮料是一个"资源"——可口可乐、矿泉水、橙汁
- **标识符（Identifier）**：A3、B1 是定位资源的"地址"
- **统一接口（Uniform Interface）**：所有操作都是"按按钮"这一个动作，区别只在于按哪个按钮

**这就是REST**。REST（Representational State Transfer，表述性状态转移）不是协议，不是框架，而是一套 **API设计风格**。它由Roy Fielding在2000年的博士论文中提出。

REST的核心思想：**把后端的一切都视为"资源"，通过URL定位资源，通过HTTP方法操作资源。** 就像自动售货机把一切商品视为"饮料"，通过按钮位置定位，通过"按"这一个动作操作。

### 70a.1.2 REST的六大约束

REST架构风格定义了六大约束。你不是去背它们，而是理解每一条在解决什么问题。

| 约束 | 一句话解释 | 你马上体会到的好处 |
|------|-----------|-------------------|
| **客户端-服务端** | 前端和后端分离，各管各的 | 前端改UI，后端不用动；后端换数据库，前端不用动 |
| **无状态** | 每个请求自带全部信息，服务端不"记"上一个请求 | 服务器重启不丢状态；水平扩展不用同步Session |
| **可缓存** | 响应可以标记"这个数据24小时内不变" | 减少不必要的网络请求；CDN可以帮你加速 |
| **统一接口** | 所有人用同一种方式和服务器对话 | 新人看API文档10分钟就能上手 |
| **分层系统** | 中间可以加负载均衡/网关/代理 | 你可以先搭Nginx在前端，后端代码一行不改 |
| **按需代码（可选）** | 服务器可以下发可执行代码（如JS） | 这个在API设计中很少用到，了解一下即可 |

> 🤔 想多一点：上面六条中，"统一接口"是REST最区别于其他风格的地方。你用 `GET /users/1` 查用户，别人也用 `GET /users/1` 查用户——URL结构和HTTP方法已经表达了意图，不需要额外文档解释"这个接口是干嘛的"。这就是RESTful API的"自描述性"。

---

## 70a.2 URL设计：用名词，不要用动词

### 70a.2.1 核心原则

**URL是资源的位置，不是动作的描述。动作由HTTP方法来表达。**

你给自动售货机的按钮编号"A3"（位置），而不是"按下去取可口可乐"（动作）。按钮位置是名词，按是动作。

❌ **错误示例——把动词塞进URL**

```
GET /getAllUsers         ← "getAll"是动词，不应该出现在URL里
POST /createUser         ← "create"是动词
POST /updateUserById/5   ← "update"是动词
GET /deleteUser?id=5     ← "delete"是动词
```

✅ **正确示例——用名词定位资源，用HTTP方法表达动作**

```
GET    /users            ← 获取所有用户
POST   /users            ← 创建用户
PUT    /users/5          ← 更新用户5
DELETE /users/5          ← 删除用户5
```

URL只回答两个问题：
1. **操作什么资源？** → `/users`（用户资源）
2. **操作哪个具体资源？** → `/users/5`（id为5的用户资源）

**怎么操作这个资源？** → 这个问题由HTTP方法（GET/POST/PUT/DELETE）回答，URL不负责。

### 70a.2.2 层级关系URL设计

资源之间常有归属关系——"张三的订单"中，"订单"归属于"用户"。用URL的层级路径来表达这种归属：

```
/users              ← 所有用户
/users/42           ← id为42的用户
/users/42/orders    ← 用户42的所有订单
/users/42/orders/7  ← 用户42的订单7
/users/42/orders/7/items   ← 用户42的订单7中的订单项
```

层级设计的规则：
- 每个 `/` 后面的部分是一个**子资源**
- 层级不要太深——超过3层就很难读了。比如 `/users/42/orders/7/items/3/comments/12` 就太深了
- 如果层级太深，拆成两个短URL。例如订单项评论可以独立为 `/orders/7/items/3/comments` 而不是挂在 `/users/42/` 下面

### 70a.2.3 常见URL风格约定

| 约定 | 示例 | 说明 |
|------|------|------|
| 全部小写 | `/users` 而非 `/Users` | URL区分大小写，约定用小写避免混淆 |
| 单词间用连字符 | `/user-profiles` 而非 `/user_profiles` 或 `/userProfiles` | 连字符比下划线更易读 |
| 集合用复数 | `/users` 而非 `/user` | 因为 `/users` 表示"用户们的集合" |
| 不用文件扩展名 | `/users` 而非 `/users.json` | 响应格式由 `Accept` 头决定，不是URL |
| 查询参数用于过滤 | `/users?role=admin&status=active` | 跟在 `?` 后面，多个参数用 `&` 连接 |

### 70a.2.4 什么情况下URL里可以出现"动词"

有极少情况确实难以用标准CRUD表达，此时可以接受动词——但放在URL**末尾**，且保持为少数例外：

```
POST /users/42/send-verification-email    ← "发送验证邮件"无法映射为资源操作
POST /orders/7/cancel                      ← "取消订单"是一种状态变更，可以接受
POST /reports/generate                     ← "生成报告"触发一个后台任务
```

> ⚠️ 注意：即使出现动词，HTTP方法仍然是POST（触发一个动作），URL末尾的动词只描述动作名称。URL的主体部分（`/users/42/`）依然是名词性资源路径。

---

## 70a.3 HTTP方法与资源操作映射

这一节你可能在第11章见过。但那里是"HTTP协议本身的方法定义"，这里从**API设计者**的角度重新看一遍：每种方法对应什么操作、请求体和响应体长什么样、成功时返回什么状态码。

### 70a.3.1 GET — 获取资源

**语义**：从服务器读取资源，**不改变**服务器上的任何数据。

**安全与幂等**：GET是安全的（不修改数据）和幂等的（发10次结果一样）。

```
请求：
GET /users HTTP/1.1
Host: api.example.com
Accept: application/json

响应：
HTTP/1.1 200 OK
Content-Type: application/json

{
  "code": 200,
  "message": "ok",
  "data": [
    {"id": 1, "name": "张三", "email": "zhang@example.com"},
    {"id": 2, "name": "李四", "email": "li@example.com"}
  ]
}
```

```
请求（获取单个）：
GET /users/1 HTTP/1.1
Host: api.example.com
Accept: application/json

响应（找到）：
HTTP/1.1 200 OK
Content-Type: application/json

{
  "code": 200,
  "message": "ok",
  "data": {"id": 1, "name": "张三", "email": "zhang@example.com"}
}

响应（未找到）：
HTTP/1.1 404 Not Found
Content-Type: application/json

{
  "code": 404,
  "message": "用户不存在",
  "data": null
}
```

### 70a.3.2 POST — 创建资源

**语义**：在服务器上创建一个新的资源。

**非幂等**：POST不是幂等的——连续发两次POST `/users` 会创建两个用户，而不是一个。

```
请求：
POST /users HTTP/1.1
Host: api.example.com
Content-Type: application/json

{
  "name": "王五",
  "email": "wang@example.com"
}

响应（创建成功）：
HTTP/1.1 201 Created
Content-Type: application/json
Location: /users/3

{
  "code": 201,
  "message": "创建成功",
  "data": {"id": 3, "name": "王五", "email": "wang@example.com"}
}
```

> 💡 注意状态码：GET成功返回 `200`，但POST成功返回 `201 Created`。这是RESTful规范中对创建操作的约定。`Location` 头给出了新资源的URL，客户端可以立刻跳转。

### 70a.3.3 PUT — 全量更新资源

**语义**：用请求体中的数据**完整替换**指定资源。即使你只想改名字，也必须把email、年龄等所有字段一并发送。

**幂等**：PUT是幂等的——发10次同样的PUT请求，结果都一样。

```
请求：
PUT /users/1 HTTP/1.1
Host: api.example.com
Content-Type: application/json

{
  "name": "张三丰",
  "email": "zhang@example.com",
  "age": 108
}

响应：
HTTP/1.1 200 OK
Content-Type: application/json

{
  "code": 200,
  "message": "更新成功",
  "data": {"id": 1, "name": "张三丰", "email": "zhang@example.com", "age": 108}
}
```

### 70a.3.4 PATCH — 部分更新资源

**语义**：只修改请求体中指定的字段，未指定的字段保持不变。

**不一定幂等**：取决于具体实现。对普通字段的PATCH是幂等的，但像 `PATCH /users/1 { "loginCount": "+1" }` 这样的增量操作则不幂等。

```
请求：
PATCH /users/1 HTTP/1.1
Host: api.example.com
Content-Type: application/json

{
  "name": "张三丰"
}

响应：
HTTP/1.1 200 OK
Content-Type: application/json

{
  "code": 200,
  "message": "更新成功",
  "data": {"id": 1, "name": "张三丰", "email": "zhang@example.com", "age": 25}
}
```

> 💡 注意：只发了 `name`，`email` 和 `age` 保持原值不变。这就是PATCH和PUT的本质区别。

### 70a.3.5 DELETE — 删除资源

**语义**：删除指定资源。

**幂等**：DELETE是幂等的——删一次和删十次的结果都是"该资源不存在了"。

```
请求：
DELETE /users/1 HTTP/1.1
Host: api.example.com

响应（删除成功）：
HTTP/1.1 204 No Content

（没有响应体）

响应（资源不存在）：
HTTP/1.1 404 Not Found
Content-Type: application/json

{
  "code": 404,
  "message": "用户不存在",
  "data": null
}
```

> 💡 `204 No Content` 是DELETE成功的标准状态码。没有响应体——因为东西已经删了，没什么好返回的。但很多团队习惯返回一个 `{ "code": 200, "message": "删除成功" }`，这也OK——关键是团队内部统一。

### 70a.3.6 五方法速查表

| HTTP方法 | CRUD对应 | 请求体 | 响应体 | 成功状态码 | 幂等 |
|----------|---------|--------|--------|-----------|------|
| GET | Read（读） | 无 | 有（资源数据） | 200 OK | ✅ |
| POST | Create（增） | 有（新资源数据） | 有（创建后的资源） | 201 Created | ❌ |
| PUT | Update（全量改） | 有（完整资源数据） | 有（更新后的资源） | 200 OK | ✅ |
| PATCH | Update（部分改） | 有（要改的字段） | 有（更新后的资源） | 200 OK | 视情况 |
| DELETE | Delete（删） | 无 | 通常无 | 204 No Content | ✅ |

---

## 70a.4 HTTP状态码速查表

状态码有5大类，你不需要全背下来。以下是后端开发中最常用的——每个你都会在后续章节反复遇到。

### 70a.4.1 常用状态码一览

| 状态码 | 名称 | 含义 | 你什么时候用它 |
|--------|------|------|---------------|
| **200** | OK | 请求成功 | GET/PUT/PATCH 成功时 |
| **201** | Created | 资源已创建 | POST 创建资源成功时 |
| **204** | No Content | 成功但无返回内容 | DELETE 成功时 |
| **301** | Moved Permanently | 资源永久迁移 | 域名换了，旧URL永久指向新URL |
| **302** | Found | 临时重定向 | 用户未登录，临时跳转到登录页 |
| **304** | Not Modified | 内容未变，用缓存 | 协商缓存命中时（第12章第2节讲过） |
| **400** | Bad Request | 请求格式错误 | 参数校验不通过，如"email字段不是合法邮箱" |
| **401** | Unauthorized | 未认证 | 用户没登录就想访问需要登录的接口 |
| **403** | Forbidden | 无权访问 | 用户登录了，但不是管理员却想删别人的数据 |
| **404** | Not Found | 资源不存在 | 查询一个不存在的用户ID |
| **405** | Method Not Allowed | 方法不允许 | 对只支持GET的URL发了POST请求 |
| **409** | Conflict | 资源冲突 | 创建用户时用户名已存在 |
| **422** | Unprocessable Entity | 语义错误 | 请求格式正确但内容不合理，如"年龄为-5" |
| **429** | Too Many Requests | 请求太频繁 | 限流——你1秒发了1000次请求 |
| **500** | Internal Server Error | 服务器内部错误 | 代码抛了未捕获的异常，看日志去！ |
| **502** | Bad Gateway | 网关错误 | Nginx后面的应用服务器挂了 |
| **503** | Service Unavailable | 服务不可用 | 服务器正在重启、维护中 |

### 70a.4.2 状态码选择的常见错误

❌ **错误：POST创建成功返回200**

```
HTTP/1.1 200 OK
{"code": 200, "message": "创建成功", "data": {...}}
```

✅ **正确：POST创建成功返回201**

```
HTTP/1.1 201 Created
Location: /users/3
{"code": 201, "message": "创建成功", "data": {...}}
```

❌ **错误：参数校验失败返回200**

```
HTTP/1.1 200 OK
{"code": 200, "message": "用户名不能为空"}
```

✅ **正确：参数校验失败返回400**

```
HTTP/1.1 400 Bad Request
{"code": 400, "message": "用户名不能为空"}
```

> 💡 核心原则：**状态码由HTTP层表达请求的"结果类别"，响应的 `code` 字段可以携带更细粒度的业务错误码，但HTTP状态码必须正确反映整体结果。** 不能用 `200 OK` 包一个错误消息——这样客户端（浏览器、CDN、网关）无法通过状态码做缓存、重试、监控。

---

## 70a.5 请求与响应格式约定

### 70a.5.1 统一响应格式

团队中如果每个人返回的JSON格式都不一样，前端同学会疯掉。约定一套统一的响应格式是团队协作的基础。

```json
{
  "code": 200,
  "message": "ok",
  "data": {
    "id": 1,
    "name": "张三"
  }
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `code` | int | 业务状态码。`200` 表示成功，其他值表示具体错误类型 |
| `message` | string | 人类可读的提示信息。成功时简单写 `"ok"`，失败时写原因如 `"用户名已存在"` |
| `data` | any | 实际返回的数据。可以是对象、数组、或 `null`（错误时通常为 `null`） |

**各种场景的返回示例：**

```json
// 成功——返回单个对象
{
  "code": 200,
  "message": "ok",
  "data": {"id": 1, "name": "张三", "email": "zhang@example.com"}
}

// 成功——返回列表
{
  "code": 200,
  "message": "ok",
  "data": [
    {"id": 1, "name": "张三"},
    {"id": 2, "name": "李四"}
  ]
}

// 成功——无数据返回（如DELETE）
{
  "code": 200,
  "message": "删除成功",
  "data": null
}

// 失败——参数校验不通过
{
  "code": 400,
  "message": "用户名不能为空",
  "data": null
}

// 失败——资源不存在
{
  "code": 404,
  "message": "用户不存在",
  "data": null
}
```

> 💡 有些团队把 `code` 和HTTP状态码保持一致（如上），有些团队用自定义业务错误码（如 `10001` 表示"用户名已存在"）。两种都行，关键是**全团队统一**。本教程采用 `code` 与HTTP状态码一致的方案。

### 70a.5.2 分页响应格式

当返回列表数据时，前端需要知道"一共有多少条""现在在第几页"。约定分页响应格式：

**请求：**

```
GET /users?page=2&size=10 HTTP/1.1
Host: api.example.com
```

| 查询参数 | 含义 | 示例值 |
|---------|------|--------|
| `page` | 第几页（从1开始） | 2 |
| `size` | 每页多少条 | 10 |

**响应：**

```json
{
  "code": 200,
  "message": "ok",
  "data": {
    "items": [
      {"id": 11, "name": "用户11"},
      {"id": 12, "name": "用户12"}
    ],
    "page": 2,
    "size": 10,
    "total": 95,
    "totalPages": 10
  }
}
```

| 分页字段 | 含义 |
|---------|------|
| `items` | 当前页的数据列表 |
| `page` | 当前页码 |
| `size` | 每页条数 |
| `total` | 总记录数 |
| `totalPages` | 总页数 |

> 💡 分页格式也有其他变体（如 `cursor` 游标分页、`offset`/`limit` 格式），上面这种 `page`/`size` 格式适用于绝大多数中小项目。你在第63章（数据库优化）和第106章（高并发）会学到什么时候需要用游标分页代替页码分页。

### 70a.5.3 Content-Type约定

| 场景 | Content-Type |
|------|-------------|
| JSON请求/响应（最常用） | `application/json; charset=utf-8` |
| 表单提交 | `application/x-www-form-urlencoded` |
| 文件上传 | `multipart/form-data` |

**前后端一致**：请求和响应都用JSON（`application/json`）。除非是文件上传等特殊场景。

---

## 70a.6 RESTful API实战：设计Todo应用

这一节你用刚学的RESTful设计原则，为Todo任务管理应用设计一套完整的API。这套API将直接作为第119章项目的接口规范。

### 70a.6.1 资源分析

Todo应用的核心资源只有两个：

- **任务（Todo）**：一条待办事项，包含标题、描述、是否完成、优先级等
- **统计（Stats）**：任务的整体统计信息（各有多少已完成/未完成）

### 70a.6.2 API设计表

| 功能 | HTTP方法 | URL | 请求体 | 成功状态码 |
|------|---------|-----|--------|-----------|
| 获取任务列表 | GET | `/api/todos?completed=false&keyword=学习` | 无 | 200 |
| 创建任务 | POST | `/api/todos` | `{"title":"学RESTful","description":"...","priority":"HIGH"}` | 201 |
| 查看任务详情 | GET | `/api/todos/5` | 无 | 200 |
| 更新任务（全量） | PUT | `/api/todos/5` | `{"title":"新标题","description":"新描述","completed":true,"priority":"LOW"}` | 200 |
| 更新任务（部分） | PATCH | `/api/todos/5` | `{"completed": true}` | 200 |
| 删除任务 | DELETE | `/api/todos/5` | 无 | 204 |
| 获取统计数据 | GET | `/api/todos/stats` | 无 | 200 |

### 70a.6.3 各接口的请求/响应示例

**1) 获取任务列表 — `GET /api/todos?completed=false&keyword=学习`**

```
请求：
GET /api/todos?completed=false&keyword=学习 HTTP/1.1
Host: api.example.com

响应：
HTTP/1.1 200 OK
Content-Type: application/json

{
  "code": 200,
  "message": "ok",
  "data": {
    "items": [
      {
        "id": 1,
        "title": "学习RESTful API",
        "description": "理解REST六大约束",
        "completed": false,
        "priority": "HIGH",
        "createdAt": "2026-06-01T10:00:00",
        "updatedAt": "2026-06-01T10:00:00"
      },
      {
        "id": 3,
        "title": "学习Spring Boot",
        "description": "从第72章开始",
        "completed": false,
        "priority": "MEDIUM",
        "createdAt": "2026-05-30T08:00:00",
        "updatedAt": "2026-05-30T08:00:00"
      }
    ],
    "page": 1,
    "size": 10,
    "total": 2,
    "totalPages": 1
  }
}
```

**2) 创建任务 — `POST /api/todos`**

```
请求：
POST /api/todos HTTP/1.1
Host: api.example.com
Content-Type: application/json

{
  "title": "学习RESTful API",
  "description": "理解REST六大约束与URL设计",
  "priority": "HIGH"
}

响应（成功）：
HTTP/1.1 201 Created
Location: /api/todos/10
Content-Type: application/json

{
  "code": 201,
  "message": "创建成功",
  "data": {
    "id": 10,
    "title": "学习RESTful API",
    "description": "理解REST六大约束与URL设计",
    "completed": false,
    "priority": "HIGH",
    "createdAt": "2026-06-01T10:05:00",
    "updatedAt": "2026-06-01T10:05:00"
  }
}

响应（校验失败——标题为空）：
HTTP/1.1 400 Bad Request
Content-Type: application/json

{
  "code": 400,
  "message": "标题不能为空",
  "data": null
}
```

**3) 查看任务详情 — `GET /api/todos/5`**

```
请求：
GET /api/todos/5 HTTP/1.1
Host: api.example.com

响应（找到）：
HTTP/1.1 200 OK
Content-Type: application/json

{
  "code": 200,
  "message": "ok",
  "data": {
    "id": 5,
    "title": "完成Redis实战",
    "description": "Jedis + Spring Data Redis",
    "completed": true,
    "priority": "MEDIUM",
    "createdAt": "2026-05-28T14:00:00",
    "updatedAt": "2026-05-29T09:00:00"
  }
}

响应（未找到）：
HTTP/1.1 404 Not Found
Content-Type: application/json

{
  "code": 404,
  "message": "任务不存在",
  "data": null
}
```

**4) 更新任务 — `PUT /api/todos/5`**

```
请求：
PUT /api/todos/5 HTTP/1.1
Host: api.example.com
Content-Type: application/json

{
  "title": "完成Redis实战与缓存设计",
  "description": "包括缓存击穿防护",
  "completed": true,
  "priority": "HIGH"
}

响应：
HTTP/1.1 200 OK
Content-Type: application/json

{
  "code": 200,
  "message": "更新成功",
  "data": {
    "id": 5,
    "title": "完成Redis实战与缓存设计",
    "description": "包括缓存击穿防护",
    "completed": true,
    "priority": "HIGH",
    "createdAt": "2026-05-28T14:00:00",
    "updatedAt": "2026-06-01T10:10:00"
  }
}
```

**5) 标记任务为已完成（部分更新）— `PATCH /api/todos/5`**

```
请求：
PATCH /api/todos/5 HTTP/1.1
Host: api.example.com
Content-Type: application/json

{
  "completed": true
}

响应：
HTTP/1.1 200 OK
Content-Type: application/json

{
  "code": 200,
  "message": "更新成功",
  "data": {
    "id": 5,
    "title": "完成Redis实战与缓存设计",
    "description": "包括缓存击穿防护",
    "completed": true,
    "priority": "HIGH",
    "createdAt": "2026-05-28T14:00:00",
    "updatedAt": "2026-06-01T10:11:00"
  }
}
```

**6) 删除任务 — `DELETE /api/todos/5`**

```
请求：
DELETE /api/todos/5 HTTP/1.1
Host: api.example.com

响应（删除成功）：
HTTP/1.1 204 No Content

响应（任务不存在）：
HTTP/1.1 404 Not Found
Content-Type: application/json

{
  "code": 404,
  "message": "任务不存在",
  "data": null
}
```

**7) 获取统计数据 — `GET /api/todos/stats`**

```
请求：
GET /api/todos/stats HTTP/1.1
Host: api.example.com

响应：
HTTP/1.1 200 OK
Content-Type: application/json

{
  "code": 200,
  "message": "ok",
  "data": {
    "total": 15,
    "completed": 9,
    "pending": 6
  }
}
```

### 70a.6.4 API设计自查清单

设计完一套API后，用这个清单逐条检查你是否能通过读者最常问的三个问题：

| # | 问题 | 检查点 |
|---|------|--------|
| 1 | **我在做什么？** | URL一眼看出操作的是哪个资源（`/api/todos` → 任务资源） |
| 2 | **我做得对不对？** | HTTP状态码明确告知结果（201创建成功 / 400参数错误 / 404不存在） |
| 3 | **不对怎么办？** | 响应体中的 `message` 字段给出人类可读的错误原因 |

---

## 70a.7 与Java/Spring Boot的关系

恭喜你学完了RESTful API的设计原则。你现在可能在想："道理都懂了，但怎么用Java写出来？"

下一章第71章你将先理解Spring框架的核心思想（IoC、DI、AOP），然后从第72章开始，你会学到Spring Boot如何将RESTful设计变为现实：

| 本章你学到的 | Spring Boot中的对应 |
|-------------|-------------------|
| `GET /users` | `@GetMapping("/users")` |
| `POST /users` | `@PostMapping("/users")` |
| `PUT /users/{id}` | `@PutMapping("/users/{id}")` |
| `PATCH /users/{id}` | `@PatchMapping("/users/{id}")` |
| `DELETE /users/{id}` | `@DeleteMapping("/users/{id}")` |
| 返回JSON `{code, message, data}` | `@RestController` + 返回Java对象，自动序列化为JSON |
| HTTP状态码 | `@ResponseStatus(HttpStatus.CREATED)` 或 `ResponseEntity<>` |
| 路径参数 `/users/{id}` | `@PathVariable Long id` |
| 查询参数 `?page=1&size=10` | `@RequestParam int page` |
| 请求体JSON | `@RequestBody UserCreateRequest request` |

**你现在已经知道了"API应该长什么样"，接下来就是学"怎么用Spring Boot把它造出来"。** 带着本章的知识进入第71章，你会发现Spring MVC的注解不是死记硬背——每个注解背后都有一个RESTful设计原则。

---

## 本章小结

| 概念 | 要点 |
|------|------|
| REST | 一种API设计风格，把一切视为"资源"，通过URL定位，通过HTTP方法操作 |
| REST六大约束 | 客户端-服务端、无状态、可缓存、统一接口、分层系统、按需代码 |
| URL设计 | 用名词（/users），不用动词（/getUsers）；层级关系表达资源归属（/users/42/orders） |
| GET | 获取资源 → `200 OK` |
| POST | 创建资源 → `201 Created` |
| PUT | 全量更新 → `200 OK` |
| PATCH | 部分更新 → `200 OK` |
| DELETE | 删除资源 → `204 No Content` |
| 统一响应格式 | `{ "code": 200, "message": "ok", "data": {...} }` |
| 状态码原则 | HTTP状态码反映结果类别；业务code可以做更细粒度区分，但不能用200包错误 |

---

## 自测题

**1. 以下URL中，哪些符合RESTful设计规范？哪些不符合？说明理由。**

A. `GET /api/getAllProducts`
B. `POST /api/products`
C. `GET /api/products/42`
D. `GET /api/products/delete/42`
E. `PUT /api/products/42`
F. `GET /api/Products`

**2. 以下场景应该返回什么HTTP状态码？**

A. 用户注册成功
B. 用户查询一个不存在的订单
C. 用户提交的注册表单中邮箱格式不正确
D. 用户删除了自己的一条评论
E. 用户没有登录就访问个人资料页
F. 服务端代码抛出了一个 `NullPointerException`

**3. 你是一个博客系统的后端开发者，需要设计"文章"和"评论"的RESTful API。请写出以下操作的URL + HTTP方法（不需要写请求/响应体）：**

A. 获取所有文章
B. 获取id为5的文章
C. 创建一篇新文章
D. 更新id为5的文章
E. 删除id为5的文章
F. 获取id为5的文章的所有评论
G. 为id为5的文章添加一条评论
H. 删除id为5的文章下的id为3的评论

<details>
<summary>参考答案（做完再看）</summary>

**1.**
- A. ❌ `/api/getAllProducts` — URL不能包含动词 `getAll`，应该用 `GET /api/products`
- B. ✅ `POST /api/products` — 正确
- C. ✅ `GET /api/products/42` — 正确，获取id为42的产品
- D. ❌ `/api/products/delete/42` — URL不能包含动词 `delete`，应该用 `DELETE /api/products/42`
- E. ✅ `PUT /api/products/42` — 正确
- F. ❌ `/api/Products` — URL应全小写，`Products` 中的大写 `P` 不规范。虽然HTTP标准中URL路径区分大小写这事取决于服务器实现，但约定是小写

**2.**
- A. `201 Created`
- B. `404 Not Found`
- C. `400 Bad Request`（或 `422 Unprocessable Entity`）
- D. `204 No Content`
- E. `401 Unauthorized`
- F. `500 Internal Server Error`

**3.**

| 功能 | 方法 | URL |
|------|------|-----|
| A. 获取所有文章 | GET | `/api/articles` |
| B. 获取id为5的文章 | GET | `/api/articles/5` |
| C. 创建一篇新文章 | POST | `/api/articles` |
| D. 更新id为5的文章 | PUT | `/api/articles/5` |
| E. 删除id为5的文章 | DELETE | `/api/articles/5` |
| F. 获取文章5的所有评论 | GET | `/api/articles/5/comments` |
| G. 为文章5添加评论 | POST | `/api/articles/5/comments` |
| H. 删除文章5下的评论3 | DELETE | `/api/articles/5/comments/3` |

</details>