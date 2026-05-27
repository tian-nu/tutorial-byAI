# 第12章 · HTTP协议（二）

> "你第一次去超市，收银员不认识你。第二次去，她竟然说：'老规矩，不要袋子是吧？'——她怎么记住的？因为这个超市有一套'会员系统'。HTTP也一样，Cookie和Session就是它的'记人系统'。"

> **重要提示**：本章代码示例中出现的 `http.HandleFunc`、`http.SetCookie` 等函数来自 Go 的 `net/http` 标准库。如果你看到不认识的函数不要慌，只是还没有学到——本章重点理解概念和流程，代码是为了让你看到"实际是怎么写的"。

---

## 12.1 Cookie

### 超市会员卡的比喻

你第一次去一家连锁超市，结账时收银员递给你一张**会员卡**，上面写着你的会员编号。

第二次你去另一家分店，一刷卡，收银员立刻说："哦，张先生，您上次买的酱油我们新到了一批，要不要看看？"

**会员卡 = Cookie**

Cookie是服务器"塞"给浏览器的一张**小纸条**，浏览器把它保存在本地。之后每次访问同一个网站时，浏览器自动把这张小纸条带回去。服务器一看纸条上的信息就知道"哦，这是张先生"。

### Cookie的工作流程

```
第1次访问：
浏览器 ──→ GET / ──→ 服务器
浏览器 ←── 200 OK ←── 服务器
         + Set-Cookie: user_id=abc123

第2次访问：
浏览器 ──→ GET / ──→ 服务器
         + Cookie: user_id=abc123
浏览器 ←── 200 OK ←── 服务器
         "哦，你是abc123！欢迎回来，张先生！"
```

### Cookie的属性

服务器在 `Set-Cookie` 响应头里不但可以设置Cookie的值，还可以设置一堆属性来控制它的行为：

```http
Set-Cookie: session_id=abc123; Domain=.example.com; Path=/; Expires=Wed, 21 Oct 2026 07:28:00 GMT; HttpOnly; Secure; SameSite=Lax
```

| 属性 | 作用 | 通俗比喻 |
|------|------|----------|
| **Name=Value** | Cookie的名字和值 | 会员卡编号 |
| **Domain** | 哪些域名能收到这个Cookie | "这张卡只在华东区的门店能用" |
| **Path** | 哪些路径能收到这个Cookie | "这张卡只能买食品区的东西，不适用于电器区" |
| **Expires / Max-Age** | Cookie何时过期 | "这张卡的有效期到2026年10月21日" |
| **HttpOnly** | 禁止JavaScript读取 | "这张卡店员能看，你不能自己涂改"（防XSS攻击） |
| **Secure** | 只在HTTPS连接中发送 | "这张卡只在VIP通道传输，不在普通通道传" |
| **SameSite** | 控制跨站请求是否发送Cookie | "这张卡只能在本店里用，不能拿到隔壁店用"（防CSRF攻击） |

### SameSite详解

SameSite是近年来最重要的Cookie安全属性，有三个取值：

| 值 | 行为 | 使用场景 |
|----|------|----------|
| **Strict** | 只有同站请求才发Cookie，跨站一律不发 | 最安全，网银/支付系统 |
| **Lax**（默认） | 大部分跨站请求不发，但"顶级导航"（如从外部点链接打开你的网站）会发 | 大多数场景的平衡选择 |
| **None** | 跨站请求也发Cookie（必须同时设 `Secure`） | 需要被嵌入iframe或跨站调用的服务 |

> 🤔 想多一点：你有没有遇到过这种情况——你在微信里点了一个淘宝链接，打开后是未登录状态，但你在浏览器里直接打开淘宝明明是登录的？这很可能是因为淘宝的Cookie设置了 `SameSite=Lax`，微信里跳转算是跨站请求，Cookie没发过去。

### 用Go设置和读取Cookie

```go
package main

import (
    "fmt"
    "net/http"
    "time"
)

func main() {
    http.HandleFunc("/login", func(w http.ResponseWriter, r *http.Request) {
        http.SetCookie(w, &http.Cookie{
            Name:     "session_id",
            Value:    "abc123",
            Path:     "/",
            Domain:   "localhost",
            Expires:  time.Now().Add(24 * time.Hour),
            HttpOnly: true,
            Secure:   false,
            SameSite: http.SameSiteLaxMode,
        })
        fmt.Fprint(w, "登录成功！Cookie已设置。")
    })

    http.HandleFunc("/profile", func(w http.ResponseWriter, r *http.Request) {
        cookie, err := r.Cookie("session_id")
        if err != nil {
            http.Error(w, "未登录", http.StatusUnauthorized)
            return
        }
        fmt.Fprintf(w, "欢迎回来！你的session_id是: %s", cookie.Value)
    })

    http.ListenAndServe(":3000", nil)
}
```

---

## 12.2 Session

### 超市后台的会员档案

Cookie"只是一个编号"，真正重要的数据存在服务器。

会员卡上只有一个编号（比如"202600001"），而你的姓名、手机号、积分余额、消费记录——全存在超市**后台的会员系统**里。

**会员卡编号 = Cookie中的SessionID**
**后台会员系统 = 服务器端的Session**

```
Cookie（浏览器端）              Session（服务器端）
┌──────────────┐          ┌──────────────────────┐
│ session_id=   │          │ abc123 → {            │
│   abc123      │          │   "user_id": 42,      │
│               │          │   "username": "张三",  │
│               │          │   "role": "admin",     │
│               │          │   "login_time": "..."  │
│               │          │ }                     │
└──────────────┘          └──────────────────────┘
```

### 为什么需要Session？

**安全。** 如果Cookie里直接存 `{"username": "张三", "role": "admin"}`，任何懂点技术的人都能打开浏览器开发者工具，把 `"role"` 改成 `"admin"`——然后他就变成管理员了。

但Cookie里只存一个**随机生成的、不可猜测的**SessionID，攻击者就算看到了也没用——他不知道这个ID对应什么数据，也猜不出别人的SessionID。

### 完整的登录流程

```
1. 用户提交登录表单（用户名+密码）
2. 服务器验证用户名密码正确
3. 服务器创建一个Session（比如存Redis里），得到SessionID
4. 服务器通过 Set-Cookie 把 SessionID 发给浏览器
5. 浏览器存下Cookie，之后每次请求自动带上
6. 服务器收到请求，从Cookie中取出SessionID
7. 服务器用SessionID去查Session数据（去Redis/数据库查）
8. 得到用户信息，处理请求，返回响应
```

### Go中使用Session

Go标准库没有内置Session支持，实际开发中通常用第三方库（如 `gorilla/sessions`）或直接用Redis存储：

```
流程简化版：
登录  → 生成随机token → 存Redis(user_token → user_info)
返回  → Set-Cookie(token)
请求  → 读Cookie中的token → 查Redis → 取出user_info
```

> 🤔 想多一点：Session到底存在哪里？常见方案有三种：① 内存（最简单，但重启丢失，多台服务器不共享）；② 数据库（持久化，但慢）；③ Redis（又快又持久化，多台服务器共享，**生产环境最常用**）。如果你用Redis存Session，用户的每次请求都要查一次Redis——但Redis快到微秒级，完全不是瓶颈。

---

## 12.3 HTTP缓存

缓存的核心思想就一句：**已经拿过的东西，不用再拿一遍**。

### 缓存在哪里？

```
浏览器 ────→ CDN节点 ────→ 反向代理(Nginx) ────→ 应用服务器
  ↑             ↑               ↑                  ↑
浏览器缓存    CDN缓存         代理缓存           应用缓存
```

后端开发主要关注两头的缓存：**浏览器缓存**（你通过HTTP头控制）和**CDN/代理缓存**。

### 强缓存 vs 协商缓存

| 类型 | 策略 | 比喻 |
|------|------|------|
| **强缓存** | "在过期之前，别来问我，直接用缓存。" | 超市收银员："会员卡在有效期内，直接放行。" |
| **协商缓存** | "过期了，但别急着重新下载，先问问服务器有没有变化。" | "卡过期了，但我打个电话问问总部，你还能不能用。" |

### 强缓存：Cache-Control

服务器通过 `Cache-Control` 响应头告诉浏览器"这个资源你可以缓存多久"：

```http
Cache-Control: max-age=3600, public
```

| 指令 | 含义 |
|------|------|
| `max-age=3600` | 缓存3600秒（1小时），1小时内直接用缓存，不请求服务器 |
| `public` | 可以被任何中间节点缓存（CDN、代理等） |
| `private` | 只能被浏览器缓存，CDN不能缓存（因为涉及用户隐私） |
| `no-cache` | 别直接用缓存，每次都要向服务器验证一下（走协商缓存） |
| `no-store` | 完全不缓存（银行交易数据等敏感内容） |
| `must-revalidate` | 过期后必须重新验证，不能用过期缓存 |

还有一个老朋友 `Expires`（HTTP/1.0时代的产物）：

```http
Expires: Wed, 21 Oct 2026 07:28:00 GMT
```

如果同时出现 `Cache-Control: max-age` 和 `Expires`，`max-age` 优先级更高。

### 协商缓存：ETag 和 Last-Modified

当强缓存过期（或设置了 `no-cache`），浏览器会带上验证信息去问服务器："这东西变过吗？"

#### 方案A：Last-Modified / If-Modified-Since

```
服务器第一次响应：
HTTP/1.1 200 OK
Last-Modified: Mon, 18 May 2026 08:00:00 GMT

浏览器下次请求：
GET /logo.png HTTP/1.1
If-Modified-Since: Mon, 18 May 2026 08:00:00 GMT

服务器判断：
- 没变 → 304 Not Modified（没有响应体，省流量！）
- 变了 → 200 OK + 新内容
```

#### 方案B：ETag / If-None-Match

ETag是**文件内容的哈希值**（如MD5），比时间戳更精确：

```
服务器第一次响应：
HTTP/1.1 200 OK
ETag: "abc123def456"

浏览器下次请求：
GET /logo.png HTTP/1.1
If-None-Match: "abc123def456"

服务器判断：
- 哈希相同 → 304 Not Modified
- 哈希不同 → 200 OK + 新内容
```

> 🤔 想多一点：为什么有了Last-Modified还需要ETag？因为Last-Modified只能精确到秒，如果一个文件在1秒内被修改了两次，Last-Modified根本看不出变化。另外，有时文件内容没变但修改时间变了（比如被压缩工具重新保存了一次），Last-Modified会导致无意义的重新下载。ETag基于内容哈希，完美解决了这些问题。生产环境中两者通常一起用。

### 缓存策略总结

```
请求一个资源
    │
    ├── 有强缓存且未过期？
    │       └── 是 → 直接用缓存（状态码: 200 from disk cache）
    │
    └── 强缓存过期 or no-cache？
            └── 发请求问服务器，带上 ETag / Last-Modified
                    │
                    ├── 服务器说 304 → 继续用缓存，更新过期时间
                    │
                    └── 服务器说 200 → 下载新内容，更新缓存
```

---

## 12.4 CORS跨域

### 同源策略：浏览器的安全门禁

浏览器有一个铁律：**一个网站不能随意读取另一个网站的数据**。

这就是**同源策略**（Same-Origin Policy）。"同源"指三个东西完全一样：

```
协议 + 域名 + 端口 → 三者完全相同，才算"同源"
```

| 页面 | 请求目标 | 是否同源？ |
|------|---------|-----------|
| `https://app.com` | `https://app.com/api/users` | ✅ 同源 |
| `https://app.com` | `http://app.com/api/users` | ❌ 协议不同（https vs http） |
| `https://app.com` | `https://api.com` | ❌ 域名不同 |
| `https://app.com` | `https://app.com:8080` | ❌ 端口不同 |

### 为什么要有同源策略？

假设没有同源策略：

```
1. 你登录了网上银行 → 银行在你的浏览器里设置了Cookie
2. 你被诱导打开了一个恶意网站 evil.com
3. evil.com 的JavaScript悄悄向 bank.com/api/transfer 发请求
4. 浏览器自动带上了你的银行Cookie
5. 你的存款被转走了 😱
```

同源策略阻止了evil.com读取bank.com的响应——请求可能发出去了（这就是CSRF攻击，需要额外防御），但evil.com拿不到响应数据。

### 但实际开发中确实需要跨域

现实场景：前端跑在 `http://localhost:5173`（Vite开发服务器），后端API跑在 `http://localhost:8080`。端口不同，不同源，浏览器直接拦截！

这就是**CORS**（Cross-Origin Resource Sharing，跨域资源共享）要解决的问题。

### CORS的解决方案

服务器在响应里加上几个特殊的头，告诉浏览器"我允许这个来源访问我"：

```http
Access-Control-Allow-Origin: http://localhost:5173
Access-Control-Allow-Methods: GET, POST, PUT, DELETE
Access-Control-Allow-Headers: Content-Type, Authorization
Access-Control-Allow-Credentials: true
Access-Control-Max-Age: 86400
```

| 响应头 | 含义 |
|--------|------|
| `Access-Control-Allow-Origin` | 允许哪个源访问（设为 `*` 表示允许所有源，但不能和凭证一起用） |
| `Access-Control-Allow-Methods` | 允许哪些HTTP方法 |
| `Access-Control-Allow-Headers` | 允许哪些自定义请求头 |
| `Access-Control-Allow-Credentials` | 是否允许携带Cookie |
| `Access-Control-Max-Age` | 预检请求的缓存时间（秒） |

### 简单请求 vs 预检请求

有些请求是"简单"的，浏览器直接发出；有些是"复杂"的，浏览器先发一个**预检请求（Preflight）**探探路：

**简单请求**（不需要预检）：
- 方法是 GET、HEAD、POST 中的一个
- 请求头只含"安全的"头（如 Content-Type 为 `text/plain`、`application/x-www-form-urlencoded`、`multipart/form-data` 之一）

**复杂请求**（需要预检）：
- 用了 PUT、PATCH、DELETE
- 请求头含 `Authorization` 或自定义头
- Content-Type 是 `application/json`

预检请求用 **OPTIONS** 方法，浏览器先问服务器："允许来自 `http://localhost:5173` 的 PUT 请求吗？"

```
浏览器 ──→ OPTIONS /api/users ──→ 服务器
         Headers: Origin, Access-Control-Request-Method

浏览器 ←── 204 No Content ←── 服务器
         Access-Control-Allow-Origin: http://localhost:5173
         Access-Control-Allow-Methods: GET, POST, PUT

浏览器 ──→ PUT /api/users ──→ 服务器   ← 真正的请求
```

### Go中处理CORS

```go
package main

import (
    "net/http"
)

func corsMiddleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        w.Header().Set("Access-Control-Allow-Origin", "http://localhost:5173")
        w.Header().Set("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        w.Header().Set("Access-Control-Allow-Headers", "Content-Type, Authorization")
        w.Header().Set("Access-Control-Allow-Credentials", "true")

        if r.Method == http.MethodOptions {
            w.WriteHeader(http.StatusNoContent)
            return
        }

        next.ServeHTTP(w, r)
    })
}

func main() {
    mux := http.NewServeMux()
    mux.HandleFunc("/api/users", func(w http.ResponseWriter, r *http.Request) {
        w.Header().Set("Content-Type", "application/json")
        w.Write([]byte(`{"users": ["张三", "李四"]}`))
    })

    http.ListenAndServe(":8080", corsMiddleware(mux))
}
```

> 🤔 想多一点：很多初学者在开发时为了"方便"，直接把 `Access-Control-Allow-Origin` 设成 `*`（允许所有源）。这在开发环境无所谓，但在生产环境这么做等于**把你API的大门敞开了**——任何网站都可以用JavaScript调用你的API。如果你的API涉及用户数据，生产环境一定要把 `Origin` 限制为你的前端域名。

---

## 本章小结

| 知识点 | 一句话概括 |
|--------|------------|
| Cookie | 服务器塞给浏览器的小纸条，浏览器每次请求自动带回去 |
| Cookie属性 | Domain/Path控制范围，HttpOnly/Secure/SameSite控制安全性 |
| Session | 服务器端存储的用户数据，Cookie里只存一个SessionID |
| 强缓存 | Cache-Control/Expires 控制"在过期前直接用本地缓存" |
| 协商缓存 | ETag/Last-Modified 实现"过期后问服务器有没有变，没变就继续用" |
| 同源策略 | 浏览器禁止不同源的页面互相读取数据 |
| CORS | 服务器通过响应头告诉浏览器"我允许这个来源跨域访问我" |
| 预检请求 | 复杂请求前浏览器先发OPTIONS探路 |

> 🚀 下一章：HTTP是明文的，等于在大街上裸奔传密码——那怎么加密？HTTPS如何用"锁"和"钥匙"保护你的数据？