# 24b — CORS 与同源策略——跨域排错指南

## 学习目标
- 理解同源策略（Same-Origin Policy）的"同源"怎么判断
- 掌握 CORS 机制的工作原理，尤其预检请求
- 能应对最常见的 CORS 报错，独立排查跨域问题

---

## 24b.1 浏览器有一道"围墙"

如果你在自己电脑上写前端 `localhost:5173`，调用后端 API `localhost:3000`，Chrome 直接弹红字报错。你肯定遇到过这个：

```
Access to fetch at 'http://localhost:3000/api/users'
from origin 'http://localhost:5173' has been blocked by CORS policy:
No 'Access-Control-Allow-Origin' header is present on the
requested resource.
```

为什么 `localhost:5173` 不能直接读 `localhost:3000`？明明在 **同一台电脑上**。

答案：**同源策略（Same-Origin Policy）**。这是浏览器内置的安全规则——一个页面的 JavaScript 只能读取**同源**（origin）的响应数据，不能随便跨源读。

这个限制只在**浏览器里**生效。你用 `curl` 或 Postman 调同样的 API 完全没问题——因为同源策略是浏览器保护用户的，不是保护服务器的。

---

## 24b.2 "同源"到底怎么判断？

**Origin（源）= 协议 + 域名 + 端口**，三个必须完全一样才算同源。

举例：你有个页面运行在 `http://www.example.com:80/index.html`：

| 你要访问的 URL | 是否同源？ | 哪里不一样 |
|---------------|-----------|-----------|
| `http://www.example.com/about.html` | ✅ 同源 | 只有路径不同，无所谓 |
| `https://www.example.com/about.html` | ❌ 不同 | **协议**不同（https vs http） |
| `http://api.example.com/users` | ❌ 不同 | **域名**不同（api vs www） |
| `http://www.example.com:8080/users` | ❌ 不同 | **端口**不同（80 vs 8080） |

注意：`localhost:5173` 和 `localhost:3000` ——**端口不同**，不同源！

💡 **想多一点**：IE 浏览器的判断规则和主流浏览器不一样——IE 不看端口号（`localhost:5173` 和 `localhost:3000` 也被视为同源）。但你不需要关心这个了，因为 IE 已经正式退休（2022年），除非你维护银行/政府遗留系统。

---

## 24b.3 为什么要搞这么严——两个经典攻击场景

同源策略看着像制造麻烦，但没有它，互联网早就崩溃了。两个最典型的攻击：

### （1）防 CSRF——你访问了恶意网站不会自动转账

你在浏览器已经登录了银行（`bank.com`），银行在你的 Cookie 里存了你的 `sessionId`。

假设同源策略不存在：你下次不小心点进 `evil.com`，这个恶意网站直接写 JavaScript 调用 `bank.com/transfer?to=hacker&amount=10000`。由于 Cookie 是自动带的，这个请求会用你的身份执行转账。

有了同源策略：`evil.com` 的 JS 虽然可以**发**请求（请求发送出去了，Cookie 也带了），但浏览器不会让 `evil.com` 的 JS **读** `bank.com` 的响应——看不到内容，黑客就没法把数据回传到自己的服务器。

### （2）防偷数据——不能跨域读取公司内网

如果你公司内网有个 `http://intranet.company.com/salaries`，没有同源策略的话，任何网页都可以用 JS 去请求这个 URL 然后读取工资数据。

同源策略保证：我访问的外部网站 `evil.com`，不能拿我的浏览器权限去读 `http://intranet.company.com` 的内容。

**一句话总结：同源策略防护的是"网站 A 的 JavaScript 通过你的浏览器去偷看网站 B 的数据"。**

---

## 24b.4 CORS：有规矩的"例外通道"

实际开发中，前后端分离——前端在 `myapp.com`，后端 API 在 `api.myapp.com` 或 `localhost:3000`，必须跨域。你说"我也是合法跨域，放我过去！"

CORS（**Cross-Origin Resource Sharing**，跨域资源共享）就是这个"放行机制"。它是一组 HTTP 头，让服务器告诉浏览器："以下来源可以跨域访问我"。

---

### 24b.4.1 最简单的情况（GET 请求，不涉及预检）

你的前端发了一个 `GET` 请求到 `https://api.example.com/users`：

1. 浏览器**自动**在请求头里加上 `Origin: https://myapp.com`（你前端所在页面的源）
2. 服务器收到请求，在响应里写 `Access-Control-Allow-Origin: https://myapp.com`
3. 浏览器比对 `<origin>` 和 ACAO 头的值——匹配就放行，不匹配就报错

```http
# 请求（浏览器自动加）
GET /users HTTP/1.1
Host: api.example.com
Origin: https://myapp.com

# 响应（服务器必须写）
HTTP/1.1 200 OK
Access-Control-Allow-Origin: https://myapp.com
Content-Type: application/json
```

如果你的前端跑在 `https://myapp.com`，后端返回 `Access-Control-Allow-Origin: https://other.com`→不匹配→被CORS拦截。

❌ **常见误解**：
- 以为前端代码里要做什么特殊处理 → 不用，浏览器自动加 `Origin` 头，你什么都不要动
- 以为服务器返回了数据但浏览器故意不给 JS → 不完全对。实际上浏览器已经拿到了响应（网络也是通的），但**把响应内容"没收"了**，JS 读到的是空或报错

---

### 24b.4.2 预检请求（Preflight Request）——复杂的跨域要先"问路"

如果请求不是简单的 `GET`，而是 `POST` 带了 JSON 或者 `PUT`/`DELETE`/`PATCH`，浏览器不会直接发请求，而是**先发一个 OPTIONS 请求探路**，问清楚服务器允不允许。

哪些算"简单请求"不需要预检：
- 方法只限 `GET`、`HEAD`、`POST`
- Headers 只限浏览器自动设的基本头（Accept、Content-Language 等）
- Content-Type 只限 `text/plain`、`application/x-www-form-urlencoded`、`multipart/form-data`

只要不满足这些条件，浏览器就会先发 OPTIONS：

```
客户端                        服务器
  │                             │
  │─ OPTIONS /users ──────────→│  "我能用 PUT 调你吗？"
  │  Origin: myapp.com         │
  │  Access-Control-Request-   │
  │    Method: PUT             │
  │                             │
  │←────── 204 No Content ──── │  "可以，PUT 允许"
  │  Access-Control-Allow-     │
  │    Origin: myapp.com       │
  │  Access-Control-Allow-     │
  │    Methods: GET,PUT,POST   │
  │                             │
  │─ PUT /users ──────────────→│  "好，正式发送"
  │  (带 body)                 │
  │                             │
  │←────── 200 OK ──────────── │  "收到"
```

注意：**OPTIONS 是浏览器自动发的，前端代码看不出来**。你在 Network 面板看到 OPTIONS 请求突然冒出来，不是后端的 bug。

💡 **想多一点**：预检请求可以缓存。服务器返回 `Access-Control-Max-Age: 86400`（单位秒），告诉浏览器："24小时内不用再预检了"。减少 OPTIONS 请求的数量也是性能优化的一环。

---

## 24b.5 真实排错指南——看到这个错误怎么一步步排查

我们回到开头那张最经典的 CORS 报错：

```
Access to fetch at 'https://api.example.com/users'
from origin 'https://myapp.com' has been blocked by CORS policy:
No 'Access-Control-Allow-Origin' header is present on the
requested resource.
```

别慌。这个错误告诉你三件事：
1. 前端来自 `https://myapp.com`
2. 试着调用 `https://api.example.com/users`
3. 响应里没有 `Access-Control-Allow-Origin` 头

### 排错步骤

#### 第 1 步：打开 DevTools Network 面板，找到失败的请求

F12 → Network，找到那个标记为红色的请求（通常是一行红字），点进去看 Headers。

#### 第 2 步：检查 Request Headers 的 Origin

在 Request Headers 里找 `Origin`，确认前端是从哪个域发的。比如：

```
Origin: https://myapp.com
```

#### 第 3 步：检查 Response Headers

看 Response Headers 里有没有 `Access-Control-Allow-Origin`。如果没有——这就是问题所在，**后端根本没配 CORS**。

如果有，检查它的值是不是匹配你的前端 Origin。比如后端配了 `Access-Control-Allow-Origin: https://other.com`，而你的前端是 `https://myapp.com`——不匹配。

#### 第 4 步：看请求方法——是不是触发了预检

如果你发的是 `POST`（JSON）、`PUT`、`DELETE`，Network 面板应该能在失败请求之前看到一条 **OPTIONS** 请求。

- OPTIONS 返回了 **403/404/500** 等非成功状态 → 预检失败。后端框架没有正确配置 OPTIONS 对应的处理。
- OPTIONS 返回了 **204**，但实际请求还是报 CORS → 预检通过了，实际请求的响应缺了 ACAO 头。检查后面的 `PUT`/`DELETE` 响应。

#### 第 5 步：检查后端 CORS 配置

最常见的几种后端 CORS 问题：

| 问题 | 后端代码里的问题 |
|------|----------------|
| 没有 CORS 配置 | 你在 `npm init` 裸跑了一个 Express，没装任何 CORS 中间件 |
| 只配了 GET，没配 OPTIONS | CORS 中间件没覆盖所有路由，预检被路由逻辑挡了 |
| 跨域 Cookie 忘配 | 你需要 `Access-Control-Allow-Credentials: true`，而且 ACAO 不能用 `*` |
| 前端 header 加了自定义头 | 需要 `Access-Control-Allow-Headers: X-Custom-Token` |

#### 第 6 步：最容易被忽略的坑——`*` 和 `credentials` 不能共存

如果你要跨域带 Cookie（比如 `fetch` 里写了 `credentials: 'include'`），服务器两端必须设：

```http
# 服务器响应头
Access-Control-Allow-Origin: https://myapp.com   ← 不能是 *，必须写具体的
Access-Control-Allow-Credentials: true
```

❌ **这三个组合都会挂**：

| 服务器配的 ACAO | 服务器配的  credentials | 前端带 Cookie | 结果 |
|----------------|------------------------|--------------|------|
| `*` | 没写或 true | 带了 | ❌ 报错 |
| `*.mysite.com` | true | 带了 | ❌ 报错（不能用通配符） |
| `https://myapp.com` | true | 带了 | ✅ 通过 |

---

## 24b.6 CORS 相关头速览

| 响应头 | 作用 |
|--------|------|
| `Access-Control-Allow-Origin` | 允许哪些 Origin 跨域访问 |
| `Access-Control-Allow-Methods` | 预检响应中，允许哪些 HTTP 方法 |
| `Access-Control-Allow-Headers` | 预检响应中，允许哪些请求头 |
| `Access-Control-Allow-Credentials` | 是否允许携带 Cookie/Authorization |
| `Access-Control-Max-Age` | 预检缓存的有效期（秒） |

---

## 24b.7 小结

| 概念 | 要点 |
|------|------|
| **同源策略** | 协议 + 域名 + 端口三者一致才算同源，浏览器安全机制 |
| **CORS** | 一套 HTTP 头，让服务器声明哪些源可以跨域访问我 |
| **Origin 请求头** | 浏览器自动添加，前端不用管，标识请求来自哪个源 |
| **预检请求** | OPTIONS 方法，非简单请求必须先探路 |
| **ACAO 不能用 `*` + credentials** | 带 Cookie 跨域必须用具体域名，不能用通配符 |
| **CORS 是浏览器限制** | curl/Postman 没有问题，同源策略只影响浏览器 JS |

---

## 术语表

| 术语 | 解释 |
|------|------|
| **同源策略 (Same-Origin Policy)**（此术语需进附录） | 浏览器的安全规则：JS 只能读同源资源，防止恶意网站偷窃数据 |
| **CORS (Cross-Origin Resource Sharing)**（此术语需进附录） | 跨域资源共享，一套 HTTP 头允许服务器声明哪些源可以跨域访问 |
| **预检请求 (Preflight Request)**（此术语需进附录） | 跨域复杂请求前，浏览器发 OPTIONS 确认服务器是否允许 |
| **Origin（源）** | 协议 + 域名 + 端口 的组合，不含路径 |
| **Access-Control-Allow-Origin（ACAO）** | CORS 响应头，声明允许哪个源的请求 |
| **CSRF (Cross-Site Request Forgery)** | 跨站请求伪造，利用已登录态冒用用户身份攻击 |

---

## 验证方法

1. 打开 DevTools → Console，手动发一个跨域 `fetch`：
   ```javascript
   fetch('https://api.github.com/users/octocat')
     .then(r => r.json())
     .then(console.log)
   ```
   GitHub API 允许 CORS，所以应该能拿到数据。

2. 再手动发一个**不**允许 CORS 的请求：
   ```javascript
   fetch('https://www.baidu.com/')
     .then(r => r.text())
     .then(console.log)
   ```
   百度的响应没有 ACAO 头，你应该能看到 CORS 报错。

3. Network 面板观察这两次请求的 Headers 区别——前一个有 `Access-Control-Allow-Origin: *`，后一个没有。

---

## 最可能出错的地方及原因

1. **OPTIONS 返回 403，不知道是 CORS 问题**：很多新手看到 OPTIONS 403 就以为是权限问题，其实 OPTIONS 是浏览器发的预检请求，后端没有配置 CORS 中间件自然就 403 了。排错先看 Network 面板有没有 OPTIONS。

2. **以为服务端不需要处理 CORS**：CORS 是浏览器强制执行的安全策略，服务端不加 CORS 头就一定被浏览器拦截。但要注意——**请求其实发出去了**（你可以看到的服务端日志），只是浏览器"没收"了响应。

3. **`*` 和 `credentials` 同时用**：这两种配置互斥。如果前端需要带 Cookie，后端必须用具体域名，不能用 `*`。Chrome 在这个问题上控制得很严格，不会悄悄降级。