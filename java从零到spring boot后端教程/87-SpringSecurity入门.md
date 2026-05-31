# 87-SpringSecurity入门

> 💡 你开了一家银行。你可以自己雇保安、装监控、设密码门、写来访登记表——或者租一家专业安保公司，他们给你配齐全部安保方案，你只需要说一句"保护这扇门"。Spring Security 就是这家安保公司。本章**先从"10行代码让所有接口被保护"开始**，再深入理解它背后那条"安检传送带"——过滤器链。

> 📊 可视化演示见 [java_87_security_filter_visual.html](java_87_security_filter_visual.html)

---

## 本章目标
- 用最少的配置启动 Spring Security
- 理解过滤器链的执行顺序
- 掌握 `SecurityFilterChain` 的定制方法
- 实现基于内存的用户认证
- 看懂 Spring Security 默认生成的登录页面从哪来

---

## 87.1 最小可用配置——10行之内的 Spring Security

### 第一步：添加依赖

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-security</artifactId>
</dependency>
```

### 第二步：启动应用——什么都没写，保护已经开始了

你不需要写任何 Java 代码。启动 Spring Boot 应用，访问任意接口（比如你之前写的 `GET /api/users`），浏览器不会返回 JSON——而是**自动跳转到 `/login` 登录页面**。

控制台会打印一行：

```
Using generated security password: 8f2a3b1c-4d5e-6f7a-8b9c-0d1e2f3a4b5c
```

这个随机密码就是你的临时"钥匙"。用户名固定为 `user`。

### 第三步（可选）：把密码写死在配置文件里（仅开发环境！）

```yaml
spring:
  security:
    user:
      name: admin
      password: 123456
```

> 🤔 **等等，我密码写了明文，不是说要用BCrypt加密吗？** 是的，用 `spring.security.user.password` 配置时，Spring Boot 的自动配置会**自动帮你用 DelegatingPasswordEncoder 处理**——Spring 底层识别到这是配置文件的密码后，会把它哈希后存到内存里。你写的是 `123456`，但实际校验时走的是加密流程。这就是为什么这行配置后面强调"仅开发环境"——生产环境应该用更安全的方式注入密码（环境变量/配置中心/Vault）。

### 这三步加起来多少行？

依赖 4 行 + 配置 4 行 = **8 行**。你的所有 API 已经被保护，未登录请求会被拦截。

> ⚠️ **重要警告**：写死密码仅用于本地开发/学习。生产环境绝不允许！生产密码必须走环境变量或配置中心。

---

## 87.2 发生了什么？Spring Security 替你做了哪些事

你只加了依赖，Spring Boot 自动配置模块检测到 `spring-boot-starter-security` 在 classpath 上，自动注册了：

| 组件 | 作用 |
|------|------|
| `SecurityFilterChain` | 一组过滤器，拦截所有请求 |
| `DaoAuthenticationProvider` | 默认的认证方式（用户名+密码） |
| `UserDetailsService` | 从内存或数据库加载用户信息 |
| `PasswordEncoder` | 默认 BCrypt，密码不能明文存 |
| 登录页面 `/login` | 自动生成的 HTML 表单 |
| 登出 `/logout` | 退出登录的端点 |
| CSRF 保护 | 跨站请求伪造防御（默认开启） |

---

## 87.3 过滤器链——请求要过的"安检关"

每个 HTTP 请求进入 Spring 应用后，不会直接到达 Controller。它会穿过一条"安检传送带"——**SecurityFilterChain**：

```
HTTP 请求
  │
  ▼
┌─────────────────────────┐
│ 1. SecurityContextPersistenceFilter  │  ← 恢复上一次请求的 SecurityContext（从 Session）
├─────────────────────────┤
│ 2. HeaderWriterFilter               │  ← 添加安全响应头（X-Frame-Options 等）
├─────────────────────────┤
│ 3. CsrfFilter                        │  ← 检查 CSRF token（POST/PUT/DELETE 必须带）
├─────────────────────────┤
│ 4. LogoutFilter                      │  ← 拦截 /logout，清除认证信息
├─────────────────────────┤
│ 5. UsernamePasswordAuthenticationFilter │ ← ⭐ 核心：处理登录表单
├─────────────────────────┤
│ 6. ExceptionTranslationFilter       │  ← 把异常翻译为 HTTP 响应（403/302）
├─────────────────────────┤
│ 7. FilterSecurityInterceptor        │  ← ⭐ 最终守门员："这个请求，你有权访问吗？"
└─────────────────────────┘
  │
  ▼
Controller（你的业务代码）
```

> 🤔 想多一点：过滤器链的顺序是写死的。你把自定义过滤器放错位置可能导致认证失败——比如放在 `SecurityContextPersistenceFilter` 之前，此时 SecurityContext 还没恢复，你读不到当前登录用户。

> 📊 上述流程的可视化动画演示见 [java_87_security_filter_visual.html](java_87_security_filter_visual.html)，那里你可以逐步播放每个过滤器的执行过程。

---

## 87.4 定制自己的 SecurityFilterChain（Spring Security 6+ 写法）

Spring Security 6 之后，推荐用 Lambda DSL 写法：

```java
@Configuration
@EnableWebSecurity
public class SecurityConfig {

    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/api/public/**").permitAll()   // 公开接口
                .requestMatchers("/api/admin/**").hasRole("ADMIN") // 需要 ADMIN 角色
                .anyRequest().authenticated()                    // 其余都要登录
            )
            .formLogin(form -> form
                .loginPage("/login")          // 自定义登录页（不设置则用默认）
                .loginProcessingUrl("/login") // 处理登录的 URL
                .defaultSuccessUrl("/home")    // 登录成功后跳转
                .permitAll()
            )
            .logout(logout -> logout
                .logoutUrl("/logout")
                .logoutSuccessUrl("/login?logout")
                .permitAll()
            )
            .csrf(csrf -> csrf.disable());  // 前后端分离时可关闭（但要知道风险）

        return http.build();
    }
}
```

### 几个关键选择

| 配置项 | 何时使用 |
|--------|----------|
| `.permitAll()` | 登录页、注册页、静态资源、公开 API |
| `.authenticated()` | 需要登录即可，不限角色 |
| `.hasRole("ADMIN")` | 需要特定角色 |
| `.hasAuthority("DELETE_USER")` | 需要特定权限（比角色更细粒度） |
| `csrf.disable()` | 前后端分离 REST API（无 Cookie）时可关 |

---

## 87.5 基于内存的用户认证（开发测试用）

```java
@Bean
public UserDetailsService userDetailsService() {
    UserDetails admin = User.builder()
            .username("admin")
            .password(passwordEncoder().encode("admin123"))
            .roles("ADMIN", "USER")
            .build();

    UserDetails user = User.builder()
            .username("user")
            .password(passwordEncoder().encode("user123"))
            .roles("USER")
            .build();

    return new InMemoryUserDetailsManager(admin, user);
}

@Bean
public PasswordEncoder passwordEncoder() {
    return new BCryptPasswordEncoder();
}
```

> ⚠️ 密码绝不能明文存储。`BCryptPasswordEncoder` 是 Spring Security 的默认选择，它会自动加盐（salt），每次 `encode("admin123")` 结果都不同。

---

## 87.6 Spring Security 架构速览

```
┌──────────────┐     ┌─────────────────┐     ┌──────────────┐
│  Security    │────→│ Authentication   │────→│  Security    │
│  Filter      │     │ Manager          │     │  Context     │
│  Chain       │     │  ┌─────────────┐ │     │  Holder      │
│              │     │  │ Provider 1   │ │     │              │
│              │     │  │ Provider 2   │ │     │              │
│              │     │  │ Provider 3   │ │     │              │
│              │     │  └─────────────┘ │     │              │
└──────────────┘     └─────────────────┘     └──────────────┘
                            ↓
                    认证成功 → 存到 SecurityContextHolder
                    认证失败 → 抛 AuthenticationException
```

你只需要记住三个核心接口：

| 接口 | 职责 | 你需要做的事 |
|------|------|-------------|
| `UserDetailsService` | 根据用户名加载用户信息 | `loadUserByUsername(String)` |
| `PasswordEncoder` | 密码加密与比对 | 通常用 `BCryptPasswordEncoder` |
| `SecurityFilterChain` | 定义哪些 URL 需要什么权限 | Lambda DSL 配置 |

---

## 87.7 常见错误

### 错误一：密码没有加密

```java
// ❌ 错误：明文存密码
UserDetails user = User.builder()
    .username("admin")
    .password("123456")   // 明文！Spring 启动时会报错
    .roles("ADMIN")
    .build();
```

Spring Security 看到密码不以 `{bcrypt}`、`{noop}` 等前缀开头，会抛 `IllegalArgumentException: There is no PasswordEncoder mapped for the id "null"`。

```java
// ✅ 正确
.password(passwordEncoder().encode("123456"))

// 或者测试时临时用（生产禁止！）
.password("{noop}123456")  // noop = No Operation，明文
```

### 错误二：关闭 CSRF 导致登录失败

前后端不分离的项目中，Spring Security 默认登录表单需要 CSRF token。如果你没关 CSRF 但登录表单少了一个 hidden input：

```html
<!-- 必须包含这个，否则 POST /login 被 CSRF 拦截 -->
<input type="hidden" th:name="${_csrf.parameterName}" th:value="${_csrf.token}"/>
```

REST API 项目可以直接关：`.csrf(csrf -> csrf.disable())`。

---

## 87.8 小结

| 知识点 | 核心内容 |
|--------|----------|
| 最小可用配置 | 加一个依赖就保护所有接口 |
| SecurityFilterChain | 一组过滤器链条，顺序固定 |
| 核心接口 | `UserDetailsService`、`PasswordEncoder`、`SecurityFilterChain` |
| authorizeHttpRequests | 用 Lambda DSL 配置 URL 权限 |
| BCryptPasswordEncoder | 默认加密器，自动加盐 |
| CSRF | 前后端分离 REST API 可关闭 |

---

## 87.9 自测题

**1. 你在 `pom.xml` 中加了 `spring-boot-starter-security`，没有写任何配置类。启动后访问 `GET /api/hello`，会发生什么？**

**2. 下面这个 Security 配置有什么问题？**

```java
http
    .authorizeHttpRequests(auth -> auth
        .anyRequest().authenticated()
        .requestMatchers("/api/public/**").permitAll()
    );
```

**3. CSRF 保护到底在防御什么？前后端分离项目为什么可以关？**

---

**答案提示**：1→不会返回 API 数据，而是跳转到 `/login` 默认登录页面。2→顺序错误：`anyRequest().authenticated()` 放在前面会拦截所有请求，`/api/public/**` 的 `permitAll()` 永远不会被执行。Spring Security 按声明顺序匹配，第一个匹配的规则生效。应该把 `requestMatchers` 放在 `anyRequest()` 前面。3→CSRF 防御的是"你在 A 网站登录后，访问恶意 B 网站，B 网站偷偷向 A 发请求"——这种攻击依赖浏览器自动带 Cookie。前后端分离项目 token 放在 Header 里而非 Cookie，浏览器不会自动带，所以可以不防。下一章——JWT 认证实战。