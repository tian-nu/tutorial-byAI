# 第12章 · HTTP协议（二）

> "上一章学了HTTP的'骨架'——请求和响应的格式。这一章学HTTP的'肌肉'——Cookie/Session让HTTP'记住'你是谁，缓存让网站更快，CORS让前端能跨域调用你的接口。"

## 12.1 Cookie与Session：解决HTTP的"脸盲症"

HTTP是无状态的——每个请求都是独立的，服务端不知道两次请求来自同一个人。你登录了淘宝，刷新一下页面，服务器怎么知道"刚才登录的那个人还是你"？

答案就是 **Cookie** 和 **Session**。

```
浏览器                                服务端
  │                                     │
  │ ──POST /login (用户名+密码)────────→  │
  │                                     │ ① 验证密码正确
  │                                     │ ② 创建Session，存入服务端内存/Redis
  │                                     │ ③ Session ID = "abc123xyz"
  │                                     │
  │ ←──Set-Cookie: JSESSIONID=abc123xyz │
  │                                     │
  │ (浏览器自动保存这个Cookie)             │
  │                                     │
  │ ──GET /api/orders─────────────────→  │
  │   Cookie: JSESSIONID=abc123xyz       │ ④ 根据Session ID找到对应用户
  │                                     │ ⑤ 返回该用户的订单数据
  │ ←──200 OK [订单数据]────────────────  │
```

### Cookie

- 存在**浏览器**端
- 大小有限（通常4KB）
- 每次请求自动携带（同域名下）
- 可以设过期时间
- 不安全——不要存敏感信息（密码、余额等）

### Session

- 存在**服务端**（内存、Redis、数据库）
- 大小无严格限制
- 通过Cookie中的Session ID来关联
- 安全——敏感数据在服务端，浏览器只拿一个ID

### Spring Boot中的Session

```java
@PostMapping("/login")
public String login(@RequestParam String username,
                    @RequestParam String password,
                    HttpSession session) {
    if (authenticate(username, password)) {
        session.setAttribute("user", username);  // 写入Session
        return "登录成功";
    }
    return "登录失败";
}

@GetMapping("/profile")
public String profile(HttpSession session) {
    String user = (String) session.getAttribute("user");  // 读取Session
    if (user == null) {
        return "请先登录";
    }
    return "当前用户: " + user;
}
```

> 🤔 想多一点：实际生产环境中，Session通常不直接存在JVM内存里——如果服务器重启，所有用户的登录状态就丢了。所以一般用 **Redis** 集中存储Session。你在第68-70章（Redis篇）会学到如何用 `spring-session-data-redis` 把Session存到Redis里。

## 12.2 HTTP缓存

浏览器每次请求都从服务器拉数据，又慢又费流量。**缓存**让浏览器把常用的数据存一份，下次直接用，不用再请求。

### 缓存的两种模式

**强缓存（不发请求）：**

```
浏览器第一次请求 GET /logo.png
  ← 200 OK
  ← Cache-Control: max-age=86400    （缓存24小时）

24小时内再请求 GET /logo.png
  → 浏览器直接从本地缓存读取，不发网络请求！
```

**协商缓存（发请求验证）：**

```
浏览器第一次请求 GET /api/data
  ← 200 OK
  ← ETag: "abc123"

第二次请求 GET /api/data
  → If-None-Match: "abc123"

服务端检查：数据没变
  ← 304 Not Modified
  ← (没有响应体，浏览器用缓存)
```

### Spring Boot中设置缓存头

```java
@GetMapping("/static-data")
public ResponseEntity<String> getStaticData() {
    return ResponseEntity.ok()
        .cacheControl(CacheControl.maxAge(1, TimeUnit.HOURS))
        .body("这是不经常变化的数据");
}
```

## 12.3 CORS：跨域资源共享

### 什么是跨域？

浏览器的**同源策略**：一个网页只能请求**同源**（相同协议+域名+端口）的API。

```
http://localhost:3000 的前端页面
    │
    │ 请求 http://localhost:8080/api/users
    │
    ↓
浏览器阻止！因为端口不同（3000 ≠ 8080）→ 跨域！
```

这在前后端分离开发中非常常见——前端跑在 `localhost:3000`（React/Vue开发服务器），后端跑在 `localhost:8080`（Spring Boot）。

### CORS解决方案

服务端在响应头里加上 `Access-Control-Allow-Origin`：

```
HTTP/1.1 200 OK
Access-Control-Allow-Origin: http://localhost:3000
Access-Control-Allow-Methods: GET, POST, PUT, DELETE
Access-Control-Allow-Headers: Content-Type, Authorization
```

### Spring Boot配置CORS

**方式一：注解（单个Controller）**

```java
@RestController
@CrossOrigin(origins = "http://localhost:3000")
public class UserController {
    // ...
}
```

**方式二：全局配置**

```java
@Configuration
public class CorsConfig implements WebMvcConfigurer {
    @Override
    public void addCorsMappings(CorsRegistry registry) {
        registry.addMapping("/api/**")            // 匹配 /api/ 开头的路径
                .allowedOrigins("http://localhost:3000")
                .allowedMethods("GET", "POST", "PUT", "DELETE")
                .allowedHeaders("*")
                .allowCredentials(true);           // 允许携带Cookie
    }
}
```

> ⚠️ 生产环境不要用 `allowedOrigins("*")`（允许所有来源），这等于把门敞开。只配置你的前端域名。

### 预检请求（Preflight）

对于非简单请求（如Content-Type为application/json的POST请求），浏览器会先发一个 **OPTIONS** 请求去"探路"：

```
浏览器 → OPTIONS /api/users              （预检请求）
  ← Access-Control-Allow-Origin: ...
  ← Access-Control-Allow-Methods: POST

浏览器 → POST /api/users                 （真正的请求）
```

这个OPTIONS请求是浏览器自动发的，你不需要手动处理。Spring Boot的CORS配置会自动响应。

---

## 本章小结

| 学了什么 | 一句话说明 |
|----------|-----------|
| Cookie | 浏览器端的小存储，解决HTTP无状态问题 |
| Session | 服务端的用户状态存储，通过Cookie中的Session ID关联 |
| 强缓存 | Cache-Control: max-age，不发请求直接用 |
| 协商缓存 | ETag/If-None-Match，发请求验证，304表示没变 |
| CORS | 跨域资源共享，前后端分离开发的必备配置 |

## 自测题

1. HTTP是无状态的。用户登录后，第二次访问页面时服务端怎么知道"这是刚才登录的那个人"？描述Cookie和Session的协作过程。

2. 你在 `localhost:3000` 的前端页面用 `fetch` 请求 `localhost:8080/api/users`，浏览器控制台报了CORS错误。应该在前端代码里解决还是在后端Spring Boot里解决？具体怎么做？

3. 浏览器缓存一张图片，设置 `Cache-Control: max-age=3600`。在1小时内，用户再次访问同一张图片时，浏览器会发网络请求吗？如果图片在服务端被更新了，用户能看到新图片吗？