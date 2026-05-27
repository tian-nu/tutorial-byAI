# 第11章 · HTTP协议（一）

> "你在浏览器地址栏敲下回车的那一刻，浏览器的背后发生了什么？——它向服务器发了一封'请求信'。这封信的语言，就叫HTTP。"

---

## 11.1 HTTP是什么

HTTP = **HyperText Transfer Protocol** = 超文本传输协议

你可以把HTTP理解为**浏览器和服务器之间对话的语言**。

浏览器说："麻烦给我 `/images/logo.png` 这个文件。"（发送HTTP请求）
服务器说："好的，这是你要的文件，它的类型是PNG图片。"（返回HTTP响应）

```
浏览器（客户端）                          服务器
     │                                      │
     │  ──── HTTP请求 ────────────────→     │
     │   GET /images/logo.png HTTP/1.1      │
     │   Host: www.example.com              │
     │                                      │
     │  ←─── HTTP响应 ─────────────────     │
     │   HTTP/1.1 200 OK                    │
     │   Content-Type: image/png            │
     │   [图片的二进制数据]                   │
```

HTTP是**无状态**的：服务器不记得你上一次请求了什么。每一次请求都是独立的——服务器不认识你，不记得你。你第一次访问淘宝和第二次访问淘宝，对HTTP协议来说是完全独立的两个请求。（至于淘宝为什么能记住你——那是Cookie和Session的功劳，下一章讲。）

> 🤔 想多一点：HTTP协议是**明文**的——这意味着如果你在HTTP网站上输入密码，任何能截获你网络数据的人都能看到你的密码原文。这就像在大街上用明信片写银行卡密码——不是不能寄，但非常不安全。所以后来才有了HTTPS（HTTP + 加密），我们在第13章详细讲。

---

## 11.2 URL结构拆解

URL = **Uniform Resource Locator** = 统一资源定位符

你每天看到的 `https://www.example.com:8080/search?q=hello&page=2#results`，它到底是什么？

把它拆开来看：

```
https://www.example.com:8080/search?q=hello&page=2#results
└─┬──┘ └─────┬──────┘ └┬┘ └──┬──┘ └───┬────────┘ └──┬──┘
  │          │         │     │         │             │
Scheme     Host      Port  Path     Query       Fragment
(协议)    (主机名)  (端口) (路径)  (查询参数)   (片段/锚点)
```

### 逐部分解释

| 部分 | 示例值 | 解释 |
|------|--------|------|
| **Scheme** | `https` | 用什么协议访问。常见的有 `http`、`https`、`ftp`、`ws` |
| **Host** | `www.example.com` | 服务器的地址，IP或域名 |
| **Port** | `8080` | 端口号。省略时默认：http默认80，https默认443 |
| **Path** | `/search` | 资源在服务器上的路径。类比文件系统中的路径 |
| **Query** | `?q=hello&page=2` | 查询参数，`?`开头，`&`分隔多个键值对 |
| **Fragment** | `#results` | 锚点/片段标识符，指向页面内的某个位置。这个部分**不会发送到服务器**，只在浏览器端使用 |

### 举个例子

```
https://music.163.com/song?id=186016
```

- `https` → 用加密的HTTP协议
- `music.163.com` → 网易云音乐的服务器
- `443` → 省略了，https默认443端口
- `/song` → 请求歌曲相关的资源
- `?id=186016` → 具体要哪首歌？id为186016的那首

换成"去餐厅点菜"的比喻：

```
菜单上写着 "主食/面条?口味=辣&大小=大碗"

Scheme  → 用中文点（不是英文）
Host    → 对着服务员说（不是对着厨师直接喊）
Path    → "主食/面条"（我要吃主食里面的面条）
Query   → 口味=辣，大小=大碗（具体要什么样的）
```

---

## 11.3 HTTP请求结构

一个HTTP请求看起来是这样的：

```http
POST /api/users HTTP/1.1
Host: api.example.com
Content-Type: application/json
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64)
Accept: application/json

{"name": "张三", "email": "zhangsan@example.com"}
```

结构分三部分：

```
┌──────────────────────────┐
│  请求行（Request Line）    │  ← POST /api/users HTTP/1.1
├──────────────────────────┤
│  请求头（Headers）         │  ← Host, Content-Type, Authorization...
│  （键值对，每行一个）       │
├──────────────────────────┤
│  空行                     │  ← 必选！用于分隔头部和体
├──────────────────────────┤
│  请求体（Body）            │  ← 可选，JSON/表单/文件
└──────────────────────────┘
```

### 请求行

```
POST /api/users HTTP/1.1
└┬─┘ └───┬────┘ └──┬──┘
  │       │         │
方法     路径     HTTP版本
```

### 用Go发出一个HTTP请求

```go
package main

import (
    "bytes"
    "fmt"
    "net/http"
)

func main() {
    url := "https://jsonplaceholder.typicode.com/posts"
    body := []byte(`{"title": "foo", "body": "bar", "userId": 1}`)

    resp, err := http.Post(url, "application/json", bytes.NewReader(body))
    if err != nil {
        fmt.Println("请求失败:", err)
        return
    }
    defer resp.Body.Close()

    fmt.Printf("状态码: %d\n", resp.StatusCode)

    buf := make([]byte, 1024)
    n, _ := resp.Body.Read(buf)
    fmt.Printf("响应体: %s\n", string(buf[:n]))
}
```

---

## 11.4 请求方法

HTTP方法告诉服务器"你想对这个资源做什么"。

### 常用方法一览

| 方法 | 含义 | 通俗比喻 | 是否有请求体 | 幂等性 |
|------|------|----------|:-----------:|:------:|
| **GET** | 获取资源 | "把那个东西给我看看" | ❌ | ✅ 幂等 |
| **POST** | 创建资源 | "把这个新东西放进去" | ✅ | ❌ 不幂等 |
| **PUT** | 完整替换资源 | "不管原来有什么，全换成这个" | ✅ | ✅ 幂等 |
| **PATCH** | 部分更新资源 | "只改其中的这几项" | ✅ | ❌ 不幂等 |
| **DELETE** | 删除资源 | "把这个删了" | ❌ | ✅ 幂等 |
| **HEAD** | 只拿响应头 | "这东西存在吗？别给我内容，给个信就行" | ❌ | ✅ 幂等 |
| **OPTIONS** | 查询支持的方法 | "你能接受哪些请求方式？" | ❌ | ✅ 幂等 |

> 🤔 想多一点：幂等是什么意思？**幂等 = 做一次和做多次，结果一样。** GET是幂等的——你查询100次用户信息，结果都一样（假设没其他人改数据）。POST不是幂等的——你连续发5次POST创建用户，会创建5个不同的用户。PUT是幂等的——无论第几次提交同样的数据，资源都是那个状态。PATCH不一定是幂等的——比如你说的"给余额+10块"，调5次就是加50块。

### 重点：GET vs POST（面试必问）

这是面试中最高频的问题之一。很多人能说出"GET把参数放URL里，POST放请求体里"，但远不止这些：

| 维度 | GET | POST |
|------|-----|------|
| **参数位置** | URL的Query中（`?key=value`） | 请求体中 |
| **长度限制** | URL长度有限制（浏览器通常限制2KB~8KB，但HTTP本身无限制） | 请求体理论上无限制 |
| **安全性** | 参数暴露在URL中，会被浏览器历史记录、服务器日志记录 | 参数在请求体中，不会出现在URL里（但依然是明文！除非是HTTPS） |
| **缓存** | 可以被浏览器缓存、CDN缓存 | 默认不被缓存 |
| **书签** | 可以收藏为书签 | 不能收藏 |
| **语义** | 获取数据，不应产生副作用 | 提交数据，通常会产生副作用 |
| **幂等性** | 幂等 | 不幂等 |

关键区分：
- **GET**：用来**读**数据。你刷新页面10次，应该看到同样的内容，不应该发生意外操作。
- **POST**：用来**写**数据。你刷新页面10次，可能会创建10条重复记录——所以浏览器会提示你"是否确认重新提交表单？"

> 🤔 想多一点：很多人问我"GET请求URL最大多长？"——HTTP协议本身没规定上限，但浏览器和服务器各有各的限制。Chrome限制约2KB，IE限制约2KB，Nginx默认限制8KB。超过这些限制，GET请求会被截断。所以长参数请用POST。

---

## 11.5 请求头和请求体

### 请求头（Headers）

请求头是一组键值对，用来传递**元信息**——关于请求本身的信息。

```http
GET /api/articles HTTP/1.1
Host: blog.example.com
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64)
Accept: application/json
Accept-Language: zh-CN,zh;q=0.9
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
Cookie: session_id=abc123; theme=dark
Content-Type: application/json
Cache-Control: no-cache
```

最常见的请求头：

| 请求头 | 作用 | 示例 |
|--------|------|------|
| **Host** | 指定请求的目标主机和端口 | `www.example.com` |
| **User-Agent** | 标识客户端类型 | `Mozilla/5.0 ...` |
| **Content-Type** | 请求体的数据类型 | `application/json`, `application/x-www-form-urlencoded`, `multipart/form-data` |
| **Accept** | 客户端能接受的响应类型 | `text/html`, `application/json` |
| **Authorization** | 身份认证信息 | `Bearer eyJhbG...`, `Basic dXNlcjpwYXNz` |
| **Cookie** | 发送之前服务器设置的Cookie | `session_id=abc123` |
| **Referer** | 从哪个页面跳转过来的 | `https://www.baidu.com/s?wd=xxx` |
| **Cache-Control** | 缓存控制指令 | `no-cache`, `max-age=3600` |

### Content-Type：告诉服务器"我发的是什么格式"

这个头非常重要，服务器靠它来解析请求体：

| Content-Type | 用途 | 示例 |
|--------------|------|------|
| `application/json` | JSON数据 | REST API最常见格式 |
| `application/x-www-form-urlencoded` | 表单数据（键值对） | `<form>`提交时的默认格式 |
| `multipart/form-data` | 文件上传 | 上传头像、附件 |
| `text/plain` | 纯文本 | 原始文本数据 |
| `application/xml` | XML数据 | 老式API可能用 |

---

## 11.6 HTTP响应结构

服务器收到请求后，返回HTTP响应，结构类似：

```http
HTTP/1.1 200 OK
Content-Type: application/json
Content-Length: 85
Date: Mon, 18 May 2026 10:30:00 GMT
Server: nginx/1.24.0

{"id": 1, "name": "张三", "email": "zhangsan@example.com"}
```

```
┌──────────────────────────┐
│  状态行（Status Line）     │  ← HTTP/1.1 200 OK
├──────────────────────────┤
│  响应头（Headers）         │  ← Content-Type, Content-Length...
├──────────────────────────┤
│  空行                     │
├──────────────────────────┤
│  响应体（Body）            │  ← JSON、HTML、图片二进制...
└──────────────────────────┘
```

### Go中接收HTTP响应

```go
package main

import (
    "fmt"
    "io"
    "net/http"
)

func main() {
    resp, err := http.Get("https://jsonplaceholder.typicode.com/posts/1")
    if err != nil {
        fmt.Println("请求失败:", err)
        return
    }
    defer resp.Body.Close()

    fmt.Printf("状态码: %d %s\n", resp.StatusCode, resp.Status)
    fmt.Printf("Content-Type: %s\n", resp.Header.Get("Content-Type"))
    fmt.Printf("Content-Length: %s\n", resp.Header.Get("Content-Length"))

    body, _ := io.ReadAll(resp.Body)
    fmt.Printf("\n响应体:\n%s\n", string(body))
}
```

---

## 11.7 状态码大全

状态码是三位数字，告诉你"请求结果怎么样"。

### 状态码分类

| 范围 | 类别 | 含义 |
|------|------|------|
| **1xx** | 信息性 | "收到了，正在处理中..." |
| **2xx** | 成功 | "搞定了！" |
| **3xx** | 重定向 | "去别的地方找" |
| **4xx** | 客户端错误 | "你搞错了" |
| **5xx** | 服务器错误 | "我搞错了" |

记忆技巧：**2成3跳4你错5我错**

### 常用状态码详解

#### 2xx - 成功

| 状态码 | 含义 | 通俗解释 |
|--------|------|----------|
| **200 OK** | 成功 | "这是你要的东西。" |
| **201 Created** | 已创建 | "你POST的新资源我已经创建好了。"（常见于POST请求的响应） |
| **204 No Content** | 无内容 | "我做完了，但没什么可返回给你的。"（删除成功后常用） |

#### 3xx - 重定向

| 状态码 | 含义 | 通俗解释 |
|--------|------|----------|
| **301 Moved Permanently** | 永久重定向 | "我搬家了，以后都去这个新地址找我。"（搜索引擎会更新索引） |
| **302 Found** | 临时重定向 | "暂时搬家了，但以后可能回来。" |
| **304 Not Modified** | 未修改 | "你没看过的版本，直接从缓存拿吧。" |
| **307 Temporary Redirect** | 临时重定向（保持方法不变） | 类似302，但POST转GET的问题被修复了 |
| **308 Permanent Redirect** | 永久重定向（保持方法不变） | 类似301，但方法不会改变 |

> 🤔 想多一点：301和302在HTTP/1.0时代就存在了，它们有一个历史遗留问题：浏览器收到301/302后，可能把POST请求自动改成GET请求再重定向——这可能导致POST请求体丢失。307和308就是为了解决这个问题而生的——它们保证重定向时HTTP方法不会变。

#### 4xx - 客户端错误

| 状态码 | 含义 | 通俗解释 |
|--------|------|----------|
| **400 Bad Request** | 请求有误 | "你说的啥？格式不对，我看不懂。" |
| **401 Unauthorized** | 未认证 | "你是谁？让我先看看你的证件。"（没登录/没token） |
| **403 Forbidden** | 禁止访问 | "我认识你，但这个房间你不能进。"（登录了但没权限） |
| **404 Not Found** | 资源不存在 | "你要找的东西不存在。" |
| **405 Method Not Allowed** | 方法不允许 | "这个资源不能用POST访问，只能用GET。" |
| **409 Conflict** | 冲突 | "你要创建的ID已经被人占用了。" |
| **422 Unprocessable Entity** | 参数错误 | "格式没错，但数据不合规。"（如邮箱格式不对） |
| **429 Too Many Requests** | 请求过多 | "你太快了，慢点。"（限流/频率限制） |

#### 5xx - 服务器错误

| 状态码 | 含义 | 通俗解释 |
|--------|------|----------|
| **500 Internal Server Error** | 服务器内部错误 | "我这边崩了，不知道发生了什么。"（代码bug、配置错误） |
| **502 Bad Gateway** | 网关错误 | "我问了后面的服务器，它给了我一个莫名其妙的回复。" |
| **503 Service Unavailable** | 服务不可用 | "我现在太忙了/在维护，过会儿再来。" |
| **504 Gateway Timeout** | 网关超时 | "我等了很久，后面的服务器一直不回我。" |

### 状态码速记

```
2xx  一切正常
3xx  别来我这，去那边
4xx  你搞错了（URL写错了吧？没登录吧？没权限吧？）
5xx  我搞错了（代码崩了！数据库挂了！等我修！）
```

---

## 本章小结

| 知识点 | 一句话概括 |
|--------|------------|
| HTTP是什么 | 浏览器和服务器之间"对话"的协议，无状态，基于请求-响应模型 |
| URL结构 | scheme://host:port/path?query#fragment |
| GET vs POST | GET读数据（参数在URL，幂等），POST写数据（参数在请求体，非幂等） |
| 请求头 | 传递元信息：Host、Content-Type、Authorization、Cookie等 |
| 状态码1xx~5xx | 1信息/2成功/3重定向/4客户端错/5服务器错 |
| Content-Type | 告诉服务器请求体是什么格式（JSON/表单/文件） |
| 幂等性 | 操作一次和多次结果相同：GET/PUT/DELETE是，POST/PATCH不一定是 |

> 🚀 下一章：HTTP协议本身不记人——那淘宝怎么知道你是谁？为什么你登录一次就不用再登录了？Cookie、Session、缓存、跨域——HTTP的进阶机制来了。