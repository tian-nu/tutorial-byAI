# 88-JWT认证实战

> 💡 你去银行办业务。第一次：填表、排队、柜员核对你身份、拍照、给个排队号。之后每次来，你只掏排队号——柜员扫一下，所有信息全出来了，不需要再填表。JWT 就是这个"排队号"——一个自包含的、自带防伪水印的凭证，服务器看一眼就认识你。

---

## 本章目标
- 理解 JWT 的三段结构：Header、Payload、Signature
- 用 jjwt 库完整实现：注册 → 登录 → 签发 token → 前端存 token → 每次请求带 token → 后端验证 → 放行
- 实现 token 刷新机制
- 知道 JWT 的风险与最佳实践

---

## 88.1 JWT 是什么——拆解一个 token

```
eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMDAxIiwibmFtZSI6IuW8oOS4iSIsInJvbGUiOiJVU0VSIiwiZXhwIjoxNzE2MDAwMDAwfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
```

用 `.` 分割成三部分：

```
Header    (红): eyJhbGciOiJIUzI1NiJ9
Payload   (蓝): eyJzdWIiOiIxMDAxIiwibmFtZSI6IuW8oOS4iSIsInJvbGUiOiJVU0VSIiwiZXhwIjoxNzE2MDAwMDAwfQ
Signature (绿): SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
```

### Header — 算法声明

Base64 解码后：
```json
{"alg": "HS256", "typ": "JWT"}
```

### Payload — 存放数据（不要放密码！）

Base64 解码后：
```json
{
  "sub": "1001",
  "name": "张三",
  "role": "USER",
  "exp": 1716000000
}
```

| 标准字段 | 含义 |
|----------|------|
| `sub` | Subject，通常是用户 ID |
| `iss` | Issuer，签发者 |
| `iat` | Issued At，签发时间 |
| `exp` | Expiration，过期时间 |

### Signature — 防伪水印

```
HMACSHA256(
    base64UrlEncode(header) + "." + base64UrlEncode(payload),
    secret_key
)
```

任何人改 Payload，签名就对不上了——服务器验签直接拒绝。

> 🤔 想多一点：JWT 的 Payload 是 Base64 编码，不是加密！任何人拿到 token 都能解码出用户名、用户 ID。所以**绝对不要把密码、身份证号等敏感信息放进 JWT Payload**。

---

## 88.2 依赖准备

```xml
<dependency>
    <groupId>io.jsonwebtoken</groupId>
    <artifactId>jjwt-api</artifactId>
    <version>0.12.5</version>
</dependency>
<dependency>
    <groupId>io.jsonwebtoken</groupId>
    <artifactId>jjwt-impl</artifactId>
    <version>0.12.5</version>
    <scope>runtime</scope>
</dependency>
<dependency>
    <groupId>io.jsonwebtoken</groupId>
    <artifactId>jjwt-jackson</artifactId>
    <version>0.12.5</version>
    <scope>runtime</scope>
</dependency>
```

`application.yml` 中配置密钥和过期时间：

```yaml
jwt:
  secret: your-256-bit-secret-key-must-be-at-least-32-characters-long
  expiration: 86400000  # 24小时，单位毫秒
```

---

## 88.3 JWT 工具类

```java
package com.example.demo.util;

import io.jsonwebtoken.*;
import io.jsonwebtoken.security.Keys;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

import javax.crypto.SecretKey;
import java.nio.charset.StandardCharsets;
import java.util.Date;

@Component
public class JwtUtil {

    private final SecretKey key;
    private final long expiration;

    public JwtUtil(@Value("${jwt.secret}") String secret,
                   @Value("${jwt.expiration}") long expiration) {
        this.key = Keys.hmacShaKeyFor(secret.getBytes(StandardCharsets.UTF_8));
        this.expiration = expiration;
    }

    public String generateToken(Long userId, String username, String role) {
        Date now = new Date();
        Date expiryDate = new Date(now.getTime() + expiration);

        return Jwts.builder()
                .subject(userId.toString())
                .claim("username", username)
                .claim("role", role)
                .issuedAt(now)
                .expiration(expiryDate)
                .signWith(key)
                .compact();
    }

    public Long getUserIdFromToken(String token) {
        Claims claims = parseToken(token);
        return Long.parseLong(claims.getSubject());
    }

    public String getUsernameFromToken(String token) {
        return (String) parseToken(token).get("username");
    }

    public boolean validateToken(String token) {
        try {
            parseToken(token);
            return true;
        } catch (JwtException | IllegalArgumentException e) {
            return false;
        }
    }

    private Claims parseToken(String token) {
        return Jwts.parser()
                .verifyWith(key)
                .build()
                .parseSignedClaims(token)
                .getPayload();
    }
}
```

---

## 88.4 用户实体与 DTO

```java
package com.example.demo.entity;

import jakarta.persistence.*;
import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;

@Entity
@Table(name = "users")
@Data
@NoArgsConstructor
@AllArgsConstructor
public class User {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(unique = true, nullable = false)
    private String username;

    @Column(nullable = false)
    private String password;  // BCrypt 加密后的

    @Column(unique = true, nullable = false)
    private String email;

    private String role = "USER";  // USER / ADMIN
}
```

```java
package com.example.demo.dto;

import jakarta.validation.constraints.NotBlank;
import lombok.Data;

@Data
public class RegisterRequest {
    @NotBlank private String username;
    @NotBlank private String password;
    @NotBlank private String email;
}

@Data
public class LoginRequest {
    @NotBlank private String username;
    @NotBlank private String password;
}

@Data
public class LoginResponse {
    private String token;
    private String refreshToken;
    private String username;
    private String role;

    public LoginResponse(String token, String refreshToken, String username, String role) {
        this.token = token;
        this.refreshToken = refreshToken;
        this.username = username;
        this.role = role;
    }
}
```

---

## 88.5 UserRepository

```java
package com.example.demo.repository;

import com.example.demo.entity.User;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.Optional;

public interface UserRepository extends JpaRepository<User, Long> {
    Optional<User> findByUsername(String username);
    boolean existsByUsername(String username);
    boolean existsByEmail(String email);
}
```

---

## 88.6 UserService

```java
package com.example.demo.service;

import com.example.demo.dto.*;
import com.example.demo.entity.User;
import com.example.demo.repository.UserRepository;
import com.example.demo.util.JwtUtil;
import lombok.RequiredArgsConstructor;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

@Service
@RequiredArgsConstructor
public class UserService {

    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;
    private final JwtUtil jwtUtil;

    public void register(RegisterRequest request) {
        if (userRepository.existsByUsername(request.getUsername())) {
            throw new RuntimeException("用户名已存在");
        }
        if (userRepository.existsByEmail(request.getEmail())) {
            throw new RuntimeException("邮箱已被注册");
        }

        User user = new User();
        user.setUsername(request.getUsername());
        user.setPassword(passwordEncoder.encode(request.getPassword()));
        user.setEmail(request.getEmail());
        user.setRole("USER");
        userRepository.save(user);
    }

    public LoginResponse login(LoginRequest request) {
        User user = userRepository.findByUsername(request.getUsername())
                .orElseThrow(() -> new RuntimeException("用户名或密码错误"));

        if (!passwordEncoder.matches(request.getPassword(), user.getPassword())) {
            throw new RuntimeException("用户名或密码错误");
        }

        String token = jwtUtil.generateToken(user.getId(), user.getUsername(), user.getRole());
        String refreshToken = jwtUtil.generateRefreshToken(user.getId());

        return new LoginResponse(token, refreshToken, user.getUsername(), user.getRole());
    }

    public LoginResponse refreshToken(String refreshToken) {
        if (!jwtUtil.validateToken(refreshToken)) {
            throw new RuntimeException("refresh token 无效或已过期");
        }
        Long userId = jwtUtil.getUserIdFromToken(refreshToken);
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new RuntimeException("用户不存在"));

        String newToken = jwtUtil.generateToken(user.getId(), user.getUsername(), user.getRole());
        String newRefreshToken = jwtUtil.generateRefreshToken(user.getId());

        return new LoginResponse(newToken, newRefreshToken, user.getUsername(), user.getRole());
    }
}
```

---

## 88.7 AuthController

```java
package com.example.demo.controller;

import com.example.demo.dto.*;
import com.example.demo.service.UserService;
import com.example.demo.common.Result;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/auth")
@RequiredArgsConstructor
public class AuthController {

    private final UserService userService;

    @PostMapping("/register")
    public Result<String> register(@Valid @RequestBody RegisterRequest request) {
        userService.register(request);
        return Result.success("注册成功");
    }

    @PostMapping("/login")
    public Result<LoginResponse> login(@Valid @RequestBody LoginRequest request) {
        LoginResponse response = userService.login(request);
        return Result.success("登录成功", response);
    }

    @PostMapping("/refresh")
    public Result<LoginResponse> refresh(@RequestBody RefreshRequest request) {
        LoginResponse response = userService.refreshToken(request.getRefreshToken());
        return Result.success("token 已刷新", response);
    }
}
```

---

## 88.8 JWT 认证过滤器

```java
package com.example.demo.security;

import com.example.demo.util.JwtUtil;
import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import lombok.RequiredArgsConstructor;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Component;
import org.springframework.web.filter.OncePerRequestFilter;

import java.io.IOException;
import java.util.List;

@Component
@RequiredArgsConstructor
public class JwtAuthenticationFilter extends OncePerRequestFilter {

    private final JwtUtil jwtUtil;

    @Override
    protected void doFilterInternal(HttpServletRequest request,
                                    HttpServletResponse response,
                                    FilterChain chain) throws ServletException, IOException {

        String authHeader = request.getHeader("Authorization");

        if (authHeader == null || !authHeader.startsWith("Bearer ")) {
            chain.doFilter(request, response);
            return;
        }

        String token = authHeader.substring(7);

        if (jwtUtil.validateToken(token)) {
            Long userId = jwtUtil.getUserIdFromToken(token);
            String username = jwtUtil.getUsernameFromToken(token);
            String role = jwtUtil.getRoleFromToken(token);

            UsernamePasswordAuthenticationToken authentication =
                    new UsernamePasswordAuthenticationToken(
                            userId,
                            null,
                            List.of(new SimpleGrantedAuthority("ROLE_" + role))
                    );
            SecurityContextHolder.getContext().setAuthentication(authentication);
        }

        chain.doFilter(request, response);
    }
}
```

> ⚠️ `OncePerRequestFilter` 保证每个请求这个过滤器只执行一次。即便请求被 forward 或 include 到其他 Servlet，也不会重复执行。

---

## 88.9 整合到 SecurityFilterChain

```java
@Configuration
@EnableWebSecurity
@RequiredArgsConstructor
public class SecurityConfig {

    private final JwtAuthenticationFilter jwtAuthenticationFilter;

    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
            .csrf(csrf -> csrf.disable())
            .sessionManagement(session ->
                session.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/api/auth/**").permitAll()
                .requestMatchers("/api/public/**").permitAll()
                .requestMatchers("/api/admin/**").hasRole("ADMIN")
                .anyRequest().authenticated()
            )
            .addFilterBefore(jwtAuthenticationFilter,
                             UsernamePasswordAuthenticationFilter.class);

        return http.build();
    }

    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder();
    }
}
```

**关键点**：
- `SessionCreationPolicy.STATELESS` — 不创建 session，纯 JWT 无状态
- `addFilterBefore(jwtAuthenticationFilter, UsernamePasswordAuthenticationFilter.class)` — JWT 过滤器插在表单登录过滤器之前执行

---

## 88.10 完整请求流程演示

```
1. POST /api/auth/register  {"username":"zhangsan","password":"123456","email":"z@e.com"}
   ← {"code":200,"message":"注册成功","data":null}

2. POST /api/auth/login     {"username":"zhangsan","password":"123456"}
   ← {"code":200,"data":{"token":"eyJhbG...","refreshToken":"eyJhbG...","username":"zhangsan","role":"USER"}}

3. GET /api/users           Header: Authorization: Bearer eyJhbG...
   ← {"code":200,"data":[...]}  ← 正常返回

4. GET /api/users           (无Authorization Header)
   ← 401 Unauthorized

5. POST /api/auth/refresh   {"refreshToken":"eyJhbG..."}
   ← {"code":200,"data":{"token":"eyJhbG...新token...","refreshToken":"eyJhbG...新refresh..."}}
```

---

## 88.11 前端如何存 token

| 存储方式 | 安全性 | 说明 |
|----------|--------|------|
| `localStorage` | ⚠️ 偏低 | 最简单，但 XSS 攻击可读取 |
| `sessionStorage` | ⚠️ 偏低 | 关闭标签页即清除 |
| `httpOnly Cookie` | ✅ 较好 | JS 不可读，防 XSS |
| 内存变量 | ✅ 最好 | 刷新页面丢失 |

前端请求示例：

```javascript
fetch('/api/users', {
    headers: {
        'Authorization': 'Bearer ' + localStorage.getItem('token')
    }
})
```

---

## 88.12 JWT 风险与最佳实践

| 风险 | 对策 |
|------|------|
| token 被盗用 | 设置短过期时间（15分钟）+ refresh token |
| 无法主动踢人 | 用 Redis 黑名单存储已失效的 token |
| Payload 膨胀 | 只放最小必要信息（userId + role） |
| 密钥泄露 | 密钥放环境变量，定期轮换 |
| 未验证签名 | 永远先验签再读 Payload |

---

## 88.13 补充：JwtUtil 中 generateRefreshToken

```java
public String generateRefreshToken(Long userId) {
    Date now = new Date();
    Date expiryDate = new Date(now.getTime() + 7 * 24 * 60 * 60 * 1000L); // 7天

    return Jwts.builder()
            .subject(userId.toString())
            .claim("type", "refresh")
            .issuedAt(now)
            .expiration(expiryDate)
            .signWith(key)
            .compact();
}
```

---

## 88.14 JwtUtil 中 role 提取补充

```java
public String getRoleFromToken(String token) {
    return (String) parseToken(token).get("role");
}
```

`RefreshRequest` DTO：

```java
package com.example.demo.dto;

import lombok.Data;

@Data
public class RefreshRequest {
    private String refreshToken;
}
```

---

## 88.15 小结

| 知识点 | 核心内容 |
|--------|----------|
| JWT 三段结构 | Header(算法) + Payload(数据) + Signature(防伪) |
| jjwt 库 | `Jwts.builder()` 生成，`Jwts.parser()` 解析 |
| 注册 → 登录 → token → 请求带 token → 过滤器验证 | 完整闭环 |
| 过滤器 | `OncePerRequestFilter` + `SecurityContextHolder` |
| 无状态 | `SessionCreationPolicy.STATELESS` |
| Refresh Token | 长有效期的 token 用于换新 access token |

---

## 88.16 自测题

**1. JWT 的三部分分别是什么？其中哪一部分是"防伪"的关键？**

**2. 如果你的 JWT access token 有效期设为 15 分钟，用户一直在操作网页，15 分钟后会发生什么？如何让用户体验不中断？**

**3. 为什么不要把密码放进 JWT Payload？**

---

**答案提示**：1→Header（算法声明）+ Payload（数据）+ Signature（签名 = HMACSHA256(header + "." + payload, secret)），Signature 是防伪关键。2→15 分钟后 access token 过期，后端返回 401。用户体验不中断的方案：前端拦截 401，用 refresh token 换取新 access token，重试原请求。3→JWT Payload 是 Base64 编码而非加密，任何人都能解码看到内容。下一章——OAuth2.0 与第三方登录。