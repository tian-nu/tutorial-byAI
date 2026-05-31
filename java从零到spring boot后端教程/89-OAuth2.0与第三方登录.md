# 89-OAuth2.0与第三方登录

> 💡 你到一个新小区拜访朋友。门禁系统给你两个选择：① 打电话让朋友下来接你；② 朋友用手机 App 给你生成一个"临时通行码"，你扫码进入。方案②不用朋友下楼，也不用给你配永久门禁卡——这就是 OAuth2.0 的思路：让第三方应用能**临时、受限地**访问你的资源，而不是直接把密码给它。

---

## 本章目标
- 理解 OAuth2.0 四种授权模式
- 搞懂"授权码模式"的完整交互流程
- 用 Spring Security OAuth2 Client 接入 GitHub 登录
- 理解 access token 和 refresh token 的分工

---

## 89.1 为什么需要 OAuth2.0？

场景：你想做一个"照片冲印"网站，用户授权后，你帮他去 Google Photos 拉取照片。

**没有 OAuth2.0 的解法**：
- 用户把 Google 密码告诉你
- 你用他的密码登录 Google Photos
- 问题：用户凭什么信你？你拿到了他 Google 的全部权限（Gmail、Drive、支付……）

**OAuth2.0 的解法**：
- 用户在你网站点"用 Google 登录"
- 跳到 Google 授权页："照片冲印网站请求访问你的 Google Photos，是否同意？"
- 用户点"同意"
- Google 给你一个**临时通行证**（access token）
- 你凭 token 只能访问 Photos，不能访问 Gmail

---

## 89.2 OAuth2.0 四个角色

| 角色 | 说明 | 对应例子 |
|------|------|----------|
| **Resource Owner** | 资源拥有者 | 用户本人 |
| **Client** | 第三方应用 | 你的"照片冲印"网站 |
| **Authorization Server** | 授权服务器 | Google 的授权服务 |
| **Resource Server** | 资源服务器 | Google Photos API |

---

## 89.3 四种授权模式

| 模式 | 适用场景 | 安全性 |
|------|----------|--------|
| **授权码模式（Authorization Code）** | 有后端的 Web 应用 | ⭐⭐⭐ 最高 |
| **简化模式（Implicit）** | 纯前端 SPA（已废弃，不推荐） | ⭐ 低 |
| **密码模式（Resource Owner Password）** | 自家 App 用自家后端（已废弃） | ⭐⭐ 中 |
| **客户端凭证模式（Client Credentials）** | 服务器之间的通信 | ⭐⭐⭐ |

> ⚠️ OAuth 2.1 草案已废弃 Implicit 和 Password 模式。新项目只推荐授权码模式 + PKCE。

---

## 89.4 授权码模式——完整流程图解

```
用户想要用 GitHub 登录你的网站（客户端）

┌──────────┐                         ┌─────────────┐                    ┌──────────┐
│  浏览器   │                         │  你的后端     │                    │  GitHub   │
└────┬─────┘                         └──────┬──────┘                    └────┬─────┘
     │                                       │                                │
     │ ① 点击"用 GitHub 登录"                 │                                │
     │──────────────────────────────────────→│                                │
     │                                       │                                │
     │ ② 302 重定向到 GitHub 授权页           │                                │
     │←──────────────────────────────────────│                                │
     │                                       │                                │
     │ ③ GET /authorize?client_id=xxx&redirect_uri=xxx                        │
     │───────────────────────────────────────────────────────────────────────→│
     │                                                                        │
     │ ④ GitHub 展示授权页面："xxx 应用请求访问你的公开资料"                      │
     │←───────────────────────────────────────────────────────────────────────│
     │                                                                        │
     │ ⑤ 用户点击"同意"                                                        │
     │───────────────────────────────────────────────────────────────────────→│
     │                                                                        │
     │ ⑥ 302 重定向到你指定的 redirect_uri，带 code 参数                          │
     │←───────────────────────────────────────────────────────────────────────│
     │                                                                        │
     │ ⑦ GET /login/oauth2/code/github?code=abc123                            │
     │─────────────────────────────────→│                                     │
     │                                  │                                     │
     │                                  │ ⑧ 用 code 换 token                     │
     │                                  │ POST /login/oauth/access_token      │
     │                                  │────────────────────────────────────→│
     │                                  │                                     │
     │                                  │ ⑨ 返回 access_token                    │
     │                                  │←────────────────────────────────────│
     │                                  │                                     │
     │                                  │ ⑩ 用 access_token 获取用户信息          │
     │                                  │ GET /user                           │
     │                                  │────────────────────────────────────→│
     │                                  │                                     │
     │                                  │ ⑪ 返回用户信息 {id, name, email}       │
     │                                  │←────────────────────────────────────│
     │                                  │                                     │
     │ ⑫ 登录成功，返回你的应用 token         │                                     │
     │←─────────────────────────────────│                                     │
```

> 🤔 想多一点：为什么 step ⑥ 返回的是 code 而不是直接给 access token？因为 step ⑥ 是通过浏览器重定向（前端），如果直接返回 access token，token 会暴露在 URL 中。code 是临时的、只能用一次，拿到 code 后由后端去换 token——token 永远不出现在浏览器地址栏。

---

## 89.5 实战：接入 GitHub 登录

### 第一步：在 GitHub 注册 OAuth App

1. 登录 GitHub → Settings → Developer settings → OAuth Apps → New OAuth App
2. 填写：
   - Application name: `my-java-app`
   - Homepage URL: `http://localhost:8080`
   - Authorization callback URL: `http://localhost:8080/login/oauth2/code/github`
3. 注册后会得到 `Client ID` 和 `Client Secret`

### 第二步：添加依赖

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-oauth2-client</artifactId>
</dependency>
```

### 第三步：application.yml

```yaml
spring:
  security:
    oauth2:
      client:
        registration:
          github:
            client-id: your_github_client_id
            client-secret: your_github_client_secret
            scope: read:user,user:email
        provider:
          github:
            authorization-uri: https://github.com/login/oauth/authorize
            token-uri: https://github.com/login/oauth/access_token
            user-info-uri: https://api.github.com/user
            user-name-attribute: login
```

### 第四步：SecurityConfig

```java
@Configuration
@EnableWebSecurity
public class SecurityConfig {

    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/", "/login").permitAll()
                .anyRequest().authenticated()
            )
            .oauth2Login(oauth2 -> oauth2
                .loginPage("/login")
                .defaultSuccessUrl("/home", true)
            );
        return http.build();
    }
}
```

### 第五步：创建首页

```html
<!-- src/main/resources/templates/index.html -->
<!DOCTYPE html>
<html>
<head><title>首页</title></head>
<body>
    <h1>欢迎</h1>
    <a href="/oauth2/authorization/github">用 GitHub 登录</a>
</body>
</html>
```

你需要 Thymeleaf 依赖：

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-thymeleaf</artifactId>
</dependency>
```

### 第六步：获取 OAuth2 用户信息

```java
@RestController
@RequestMapping("/api/user")
public class UserController {

    @GetMapping("/me")
    public Map<String, Object> currentUser(
            @AuthenticationPrincipal OAuth2User principal) {
        return principal.getAttributes();
    }
}
```

响应示例：

```json
{
    "login": "zhangsan",
    "id": 123456,
    "avatar_url": "https://avatars.githubusercontent.com/u/123456",
    "email": "zhangsan@example.com",
    "name": "Zhang San"
}
```

---

## 89.6 Access Token vs Refresh Token

| | Access Token | Refresh Token |
|------|------|------|
| 有效期 | 短（分钟级） | 长（天/周级） |
| 用途 | 访问 API | 换新的 Access Token |
| 传输频率 | 每个请求都带 | 只在续期时使用 |
| 存储位置 | 内存（前端）/ 不存（后端 JWT） | 数据库或 Redis |

**为什么要两个 token？** 如果只有一个长有效期的 token，一旦泄露，攻击者可以长期使用。有了短 access token + 长 refresh token，即使 access token 泄露，影响窗口也只有几分钟。而 refresh token 只在续期时才传输一次，泄露概率大大降低。

---

## 89.7 小结

| 知识点 | 核心内容 |
|--------|----------|
| OAuth2.0 四个角色 | Resource Owner / Client / Auth Server / Resource Server |
| 四种模式 | 授权码（最安全）、Implicit、Password、Client Credentials |
| 授权码流程 | 浏览器拿 code → 后端用 code 换 token → 用 token 调 API |
| Spring Security 集成 | `oauth2Login()` 一行配置搞定 |
| Access Token + Refresh Token | 短+长组合，兼顾安全与体验 |

---

## 89.8 自测题

**1. OAuth2.0 授权码模式中，`code`（授权码）是给谁的？token 是给谁的？为什么这样设计？**

**2. 你的应用接入了微信登录。用户在微信授权页点了"拒绝"，你的后端会收到什么？**

**3. Access Token 过期了怎么办？Refresh Token 也过期了呢？**

---

**答案提示**：1→code 给浏览器（前端），token 给后端（服务端）。这样 token 不出现在浏览器地址栏，避免泄露。2→GitHub 会 302 重定向到 redirect_uri 并带上 `error=access_denied` 参数。你的应用应捕获并提示用户。3→Access Token 过期 → 用 Refresh Token 换新 Access Token。Refresh Token 也过期 → 用户需要重新登录（再次走 OAuth2.0 授权流程）。下一章——RBAC 权限控制。