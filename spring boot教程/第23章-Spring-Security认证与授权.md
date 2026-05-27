# 第23章：Spring Security认证与授权

## 本章目标

学完本章你将能够：

- 理解Spring Security的过滤器链架构，画出核心过滤器的执行顺序图
- 掌握SecurityContextHolder、Authentication、UserDetailsService等核心组件的协作关系
- 使用Spring Security 6.x Lambda DSL配置安全规则（不再使用已弃用的WebSecurityConfigurerAdapter）
- 实现基于数据库的用户认证，自定义UserDetailsService加载用户信息
- 使用BCryptPasswordEncoder安全地存储和校验密码（绝不使用MD5/SHA）
- 设计RBAC五表权限模型，编写完整的建表SQL
- 配置URL级别的权限控制和自定义登录成功/失败处理器
- 使用@EnableMethodSecurity和@PreAuthorize实现方法级安全控制
- 自定义401/403响应，适配前后端分离架构

---

## 23.1 Spring Security架构

### 23.1.1 为什么需要安全框架

假设你写了一个员工管理系统的API，任何知道URL的人都能直接调用删除员工的接口——这显然不行。Web应用面临的安全威胁包括：

- **未认证访问**：匿名用户访问受保护资源
- **越权操作**：普通用户执行管理员操作
- **会话劫持**：攻击者盗取用户会话
- **CSRF攻击**：跨站请求伪造
- **暴力破解**：自动尝试大量密码

Spring Security是Spring生态中的安全框架，提供了认证（Authentication，你是谁）和授权（Authorization，你能做什么）的完整解决方案。

### 23.1.2 过滤器链 — Spring Security的核心执行模型

Spring Security的底层实现是一组Servlet Filter的链式调用。每个HTTP请求都会经过这条过滤器链，每个过滤器负责一个安全检查环节。

```
HTTP请求
  │
  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      SecurityFilterChain                            │
│                                                                     │
│  ┌──────────────────────────┐                                       │
│  │ 1. DisableEncodeUrlFilter│  → 移除URL中的Session ID              │
│  └────────────┬─────────────┘                                       │
│               ▼                                                     │
│  ┌──────────────────────────┐                                       │
│  │ 2. WebAsyncManagerFilter │  → 异步请求安全集成                    │
│  └────────────┬─────────────┘                                       │
│               ▼                                                     │
│  ┌──────────────────────────┐                                       │
│  │ 3. SecurityContextFilter │  → 加载/保存SecurityContext            │
│  │    (核心！)              │     (包含认证信息)                      │
│  └────────────┬─────────────┘                                       │
│               ▼                                                     │
│  ┌──────────────────────────┐                                       │
│  │ 4. HeaderWriterFilter    │  → 写入安全响应头                      │
│  └────────────┬─────────────┘                                       │
│               ▼                                                     │
│  ┌──────────────────────────┐                                       │
│  │ 5. CorsFilter            │  → 跨域处理                           │
│  └────────────┬─────────────┘                                       │
│               ▼                                                     │
│  ┌──────────────────────────┐                                       │
│  │ 6. CsrfFilter            │  → CSRF令牌校验                       │
│  └────────────┬─────────────┘                                       │
│               ▼                                                     │
│  ┌──────────────────────────┐                                       │
│  │ 7. LogoutFilter          │  → 注销请求处理                       │
│  └────────────┬─────────────┘                                       │
│               ▼                                                     │
│  ┌──────────────────────────────────┐                               │
│  │ 8. UsernamePasswordAuthentication│  → 表单登录认证               │
│  │    Filter                        │     (用户名+密码)              │
│  └────────────┬─────────────────────┘                               │
│               ▼                                                     │
│  ┌──────────────────────────┐                                       │
│  │ 9. DefaultLoginPageFilter│  → 生成默认登录页                      │
│  └────────────┬─────────────┘                                       │
│               ▼                                                     │
│  ┌──────────────────────────┐                                       │
│  │10. RequestCacheAwareFilter│  → 登录后恢复原始请求                 │
│  └────────────┬─────────────┘                                       │
│               ▼                                                     │
│  ┌──────────────────────────┐                                       │
│  │11. SecurityContextHolder │  → 异步安全上下文传播                  │
│  │    Filter (异步)         │                                       │
│  └────────────┬─────────────┘                                       │
│               ▼                                                     │
│  ┌──────────────────────────┐                                       │
│  │12. SessionManagementFilter│ → Session固定保护/并发控制            │
│  └────────────┬─────────────┘                                       │
│               ▼                                                     │
│  ┌──────────────────────────┐                                       │
│  │13. ExceptionTranslation  │  → 将安全异常转为HTTP响应              │
│  │    Filter (核心！)       │     (401/403)                         │
│  └────────────┬─────────────┘                                       │
│               ▼                                                     │
│  ┌──────────────────────────┐                                       │
│  │14. AuthorizationFilter   │  → 最终授权决策                       │
│  │    (核心！)              │     (检查是否有权限访问)               │
│  └────────────┬─────────────┘                                       │
│               ▼                                                     │
│         你的Controller                                              │
└─────────────────────────────────────────────────────────────────────┘
```

**关键理解**：

1. **过滤器链是可配置的**——你可以添加、移除、替换过滤器，也可以配置多条过滤器链（不同URL路径使用不同的安全策略）
2. **SecurityContextFilter**负责在请求开始时从Session（或Redis）加载认证信息到SecurityContextHolder，请求结束时清除
3. **ExceptionTranslationFilter**是安全异常的"翻译官"——它捕获Spring Security内部抛出的异常，转为对应的HTTP 401/403响应
4. **AuthorizationFilter**是最后一道关卡，检查当前认证用户是否有权访问目标URL

### 23.1.3 核心组件关系图

```
┌──────────────────────────────────────────────────────────────────┐
│                        认证流程                                   │
│                                                                  │
│  HTTP请求(用户名+密码)                                            │
│       │                                                          │
│       ▼                                                          │
│  UsernamePasswordAuthenticationFilter                            │
│       │  创建 UsernamePasswordAuthenticationToken(未认证)         │
│       ▼                                                          │
│  AuthenticationManager (接口)                                    │
│       │                                                          │
│       ▼                                                          │
│  ProviderManager (AuthenticationManager的默认实现)                │
│       │  遍历所有AuthenticationProvider                           │
│       ▼                                                          │
│  DaoAuthenticationProvider (最常用的Provider)                     │
│       │                                                          │
│       ├──► UserDetailsService.loadUserByUsername(username)       │
│       │         │                                                │
│       │         ▼                                                │
│       │    返回 UserDetails (用户信息+权限)                        │
│       │                                                          │
│       ├──► PasswordEncoder.matches(rawPassword, encodedPassword) │
│       │         │                                                │
│       │         ▼                                                │
│       │    密码匹配？                                             │
│       │         │                                                │
│       │    ┌────┴────┐                                           │
│       │    ▼         ▼                                           │
│       │   是        否                                            │
│       │    │         │                                            │
│       │    ▼         ▼                                            │
│       │  认证成功  抛出BadCredentialsException                    │
│       │    │                                                      │
│       │    ▼                                                      │
│       │  创建 UsernamePasswordAuthenticationToken(已认证)         │
│       │    │                                                      │
│       │    ▼                                                      │
│       │  SecurityContextHolder.getContext()                       │
│       │      .setAuthentication(authentication)                   │
│       │    │                                                      │
│       │    ▼                                                      │
│       │  SecurityContextPersistenceFilter保存到Session             │
│       └────┘                                                      │
└──────────────────────────────────────────────────────────────────┘
```

**核心组件逐个解释**：

| 组件 | 职责 | 类比 |
|------|------|------|
| **SecurityContextHolder** | 存储当前线程的安全上下文 | 门卫的登记本 |
| **SecurityContext** | 持有Authentication对象 | 一条登记记录 |
| **Authentication** | 认证信息载体（用户身份+权限+凭证） | 工牌 |
| **AuthenticationManager** | 认证管理入口 | 安检总台 |
| **ProviderManager** | AuthenticationManager的默认实现 | 安检总台的调度员 |
| **AuthenticationProvider** | 执行具体的认证逻辑 | 某个安检员 |
| **UserDetailsService** | 根据用户名加载用户信息 | 人事档案室 |
| **UserDetails** | 用户详情（用户名、密码、权限） | 档案内容 |
| **PasswordEncoder** | 密码编码/匹配 | 密码保险箱 |

### 23.1.4 🚨 配置方式巨变：Lambda DSL替代WebSecurityConfigurerAdapter

Spring Security 5.7开始，`WebSecurityConfigurerAdapter`被标记为`@Deprecated`，Spring Security 6.x中已**完全移除**。网上大量教程还在用旧写法，如果你照抄会直接编译报错。

**旧写法（已弃用！不要用！）**：

```java
// ❌ Spring Security 6.x 中已移除，编译报错！
@Configuration
@EnableWebSecurity
public class SecurityConfig extends WebSecurityConfigurerAdapter {

    @Override
    protected void configure(HttpSecurity http) throws Exception {
        http.csrf().disable()
            .authorizeRequests()
            .antMatchers("/api/auth/**").permitAll()
            .anyRequest().authenticated();
    }

    @Override
    protected void configure(AuthenticationManagerBuilder auth) throws Exception {
        auth.userDetailsService(userDetailsService)
            .passwordEncoder(passwordEncoder());
    }

    @Bean
    @Override
    public AuthenticationManager authenticationManagerBean() throws Exception {
        return super.authenticationManagerBean();
    }
}
```

**新写法（Spring Security 6.x Lambda DSL，必须用！）**：

```java
@Configuration
@EnableWebSecurity
public class SecurityConfig {

    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
            .csrf(csrf -> csrf.disable())
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/api/auth/**").permitAll()
                .anyRequest().authenticated()
            );
        return http.build();
    }

    @Bean
    public AuthenticationManager authenticationManager(
            AuthenticationConfiguration authenticationConfiguration) throws Exception {
        return authenticationConfiguration.getAuthenticationManager();
    }

    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder();
    }
}
```

**新旧写法关键差异**：

| 旧写法 | 新写法 | 说明 |
|--------|--------|------|
| `extends WebSecurityConfigurerAdapter` | 不继承任何类 | 继承已移除 |
| `configure(HttpSecurity http)` | `@Bean SecurityFilterChain` | 组件化配置 |
| `.csrf().disable()` | `.csrf(csrf -> csrf.disable())` | Lambda DSL |
| `.authorizeRequests()` | `.authorizeHttpRequests()` | 新API名称 |
| `.antMatchers()` | `.requestMatchers()` | 新匹配方法 |
| `.access()` | `.access()` | 保留不变 |

Lambda DSL的好处：**IDE自动补全支持更好、配置项更清晰、不会因为链式调用顺序错误导致运行时异常**。

---

## 23.2 基于数据库的认证

### 23.2.1 引入Spring Security依赖

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-security</artifactId>
</dependency>
```

引入这个依赖后，Spring Security自动配置立即生效——**所有接口默认需要认证**。此时启动项目访问任何接口，会自动跳转到一个默认登录页。这是Spring Security的"安全默认值"设计哲学：默认最安全，你需要显式放行。

### 23.2.2 自定义UserDetails

Spring Security通过`UserDetails`接口获取用户信息。我们需要让自己的实体类实现这个接口：

```java
public class SecurityUser implements UserDetails {

    private Long id;
    private String username;
    private String password;
    private Boolean enabled;
    private List<GrantedAuthority> authorities;

    public SecurityUser(Long id, String username, String password,
                        Boolean enabled, List<GrantedAuthority> authorities) {
        this.id = id;
        this.username = username;
        this.password = password;
        this.enabled = enabled;
        this.authorities = authorities;
    }

    public Long getId() {
        return id;
    }

    @Override
    public Collection<? extends GrantedAuthority> getAuthorities() {
        return authorities;
    }

    @Override
    public String getPassword() {
        return password;
    }

    @Override
    public String getUsername() {
        return username;
    }

    @Override
    public boolean isAccountNonExpired() {
        return true;
    }

    @Override
    public boolean isAccountNonLocked() {
        return true;
    }

    @Override
    public boolean isCredentialsNonExpired() {
        return true;
    }

    @Override
    public boolean isEnabled() {
        return enabled;
    }
}
```

**接口方法说明**：

| 方法 | 含义 | 返回true的场景 |
|------|------|----------------|
| `getAuthorities()` | 用户权限列表 | 返回角色和权限 |
| `getPassword()` | 加密后的密码 | 数据库中存储的BCrypt密文 |
| `getUsername()` | 用户名 | 用于登录标识 |
| `isAccountNonExpired()` | 账号是否未过期 | 未过期返回true |
| `isAccountNonLocked()` | 账号是否未锁定 | 未锁定返回true |
| `isCredentialsNonExpired()` | 凭证是否未过期 | 密码未过期返回true |
| `isEnabled()` | 账号是否启用 | 正常状态返回true |

四个布尔方法只要有一个返回`false`，用户就无法登录。如果暂时不需要这些控制，全部返回`true`即可。

### 23.2.3 实现UserDetailsService

`UserDetailsService`是Spring Security加载用户信息的核心接口，只有一个方法：

```java
@Service
public class CustomUserDetailsService implements UserDetailsService {

    private final UserMapper userMapper;
    private final RoleMapper roleMapper;
    private final PermissionMapper permissionMapper;

    public CustomUserDetailsService(UserMapper userMapper,
                                    RoleMapper roleMapper,
                                    PermissionMapper permissionMapper) {
        this.userMapper = userMapper;
        this.roleMapper = roleMapper;
        this.permissionMapper = permissionMapper;
    }

    @Override
    public UserDetails loadUserByUsername(String username)
            throws UsernameNotFoundException {

        User user = userMapper.findByUsername(username);
        if (user == null) {
            throw new UsernameNotFoundException(
                "用户不存在: " + username);
        }

        List<String> roleCodes = roleMapper.findRoleCodesByUserId(user.getId());

        List<String> permissionCodes = permissionMapper
            .findPermissionCodesByUserId(user.getId());

        List<GrantedAuthority> authorities = new ArrayList<>();
        for (String role : roleCodes) {
            authorities.add(new SimpleGrantedAuthority("ROLE_" + role));
        }
        for (String perm : permissionCodes) {
            authorities.add(new SimpleGrantedAuthority(perm));
        }

        return new SecurityUser(
            user.getId(),
            user.getUsername(),
            user.getPassword(),
            user.getEnabled(),
            authorities
        );
    }
}
```

**关键细节**：

1. `loadUserByUsername`只接收用户名，返回`UserDetails`——Spring Security会自动调用`PasswordEncoder`比对密码
2. 角色需要加`ROLE_`前缀——Spring Security的`hasRole('ADMIN')`内部会自动补`ROLE_`前缀，所以你存入时必须带前缀
3. 权限不需要前缀——`hasAuthority('user:delete')`直接匹配你存入的字符串
4. 如果用户不存在，必须抛`UsernameNotFoundException`——Spring Security会将其转换为认证失败

### 23.2.4 BCryptPasswordEncoder — 密码存储的唯一正确选择

#### 为什么BCrypt

密码存储的核心原则：**即使数据库泄露，攻击者也无法还原出明文密码**。这要求密码哈希必须满足：

1. **加盐（Salt）**：相同密码的哈希值不同，防止彩虹表攻击
2. **慢哈希（Slow Hash）**：计算速度刻意变慢，增加暴力破解成本
3. **不可逆**：无法从哈希值反推明文

| 算法 | 加盐 | 速度 | 安全性 | 结论 |
|------|------|------|--------|------|
| MD5 | ❌ 不自带 | 极快 | 🔴 秒破 | **绝对不要用** |
| SHA-256 | ❌ 不自带 | 快 | 🟡 可破 | 不推荐 |
| MD5+盐 | ⚠️ 需手动 | 极快 | 🟡 彩虹表不行但可暴力 | 不推荐 |
| BCrypt | ✅ 自动内嵌 | 慢（可调） | 🟢 安全 | **推荐** |
| Argon2 | ✅ 自动内嵌 | 慢（可调） | 🟢 最安全 | 推荐（需额外依赖） |

> 🚨 **坑：绝对不要用MD5/SHA存储密码！** MD5和SHA是消息摘要算法，设计目标是"快"——计算速度越快越好。但密码哈希恰恰需要"慢"——越慢，暴力破解的成本越高。现代GPU每秒可计算数十亿次MD5，一个8位纯数字密码的MD5在1秒内即可暴力破解。

> 🚨 **坑：不要自己写加密算法！** 密码学是极其专业的领域，自己写的算法几乎必然有漏洞。即使是专业密码学家设计的算法，也需要经过数年的同行评审。使用业界公认的BCrypt即可。

#### BCryptPasswordEncoder使用

```java
@Configuration
public class SecurityConfig {

    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder();
    }
}
```

注册用户时加密密码：

```java
@Service
public class UserService {

    private final UserMapper userMapper;
    private final PasswordEncoder passwordEncoder;

    public UserService(UserMapper userMapper, PasswordEncoder passwordEncoder) {
        this.userMapper = userMapper;
        this.passwordEncoder = passwordEncoder;
    }

    public void register(String username, String rawPassword) {
        String encodedPassword = passwordEncoder.encode(rawPassword);
        User user = new User();
        user.setUsername(username);
        user.setPassword(encodedPassword);
        user.setEnabled(true);
        userMapper.insert(user);
    }
}
```

验证密码（Spring Security自动完成，但了解原理很重要）：

```java
boolean matches = passwordEncoder.matches(
    "用户输入的明文密码",
    "数据库中的BCrypt密文"
);
```

BCrypt密文长这样：

```
$2a$10$N9qo8uLOickgx2ZMRZoMyeIjZAgcfl7p92ldGxad68LJZdL17lhWy
│  │  │                      │
│  │  │                      └── 哈希值（31字符）
│  │  └── 盐值（22字符，每次不同）
│  └── cost因子（10 = 2^10轮，越大越慢）
└── 算法版本
```

**同一个明文密码，每次`encode()`的结果都不同**——因为盐值是随机生成的。但`matches()`依然能正确验证，因为盐值已经内嵌在密文中了。

### 23.2.5 登录认证完整流程走读

让我们把整个认证流程串起来，看看一个登录请求经历了什么：

```
1. 用户提交 POST /api/auth/login  {username: "admin", password: "123456"}

2. UsernamePasswordAuthenticationFilter 拦截请求
   → 创建 UsernamePasswordAuthenticationToken(未认证，包含用户名和密码)
   → 交给 AuthenticationManager

3. AuthenticationManager (实际是 ProviderManager)
   → 遍历注册的 AuthenticationProvider
   → 找到支持 UsernamePasswordAuthenticationToken 的 DaoAuthenticationProvider

4. DaoAuthenticationProvider 执行认证
   → 调用 UserDetailsService.loadUserByUsername("admin")
   → 得到 SecurityUser (包含数据库中的BCrypt密码和权限列表)
   → 调用 PasswordEncoder.matches("123456", "$2a$10$xxx...")
   → 密码匹配成功

5. 认证成功
   → 创建 UsernamePasswordAuthenticationToken(已认证，包含用户信息和权限)
   → 存入 SecurityContextHolder.getContext().setAuthentication(...)
   → 调用 AuthenticationSuccessHandler

6. 如果密码不匹配
   → 抛出 BadCredentialsException
   → 调用 AuthenticationFailureHandler
```

---

## 23.3 安全配置

### 23.3.1 SecurityFilterChain完整配置

这是前后端分离项目中最常用的完整配置：

```java
@Configuration
@EnableWebSecurity
public class SecurityConfig {

    private final CustomUserDetailsService userDetailsService;
    private final AuthenticationSuccessHandler successHandler;
    private final AuthenticationFailureHandler failureHandler;
    private final AuthenticationEntryPoint entryPoint;
    private final AccessDeniedHandler deniedHandler;

    public SecurityConfig(CustomUserDetailsService userDetailsService,
                          AuthenticationSuccessHandler successHandler,
                          AuthenticationFailureHandler failureHandler,
                          AuthenticationEntryPoint entryPoint,
                          AccessDeniedHandler deniedHandler) {
        this.userDetailsService = userDetailsService;
        this.successHandler = successHandler;
        this.failureHandler = failureHandler;
        this.entryPoint = entryPoint;
        this.deniedHandler = deniedHandler;
    }

    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
            .csrf(csrf -> csrf.disable())
            .cors(cors -> cors.configurationSource(corsConfigurationSource()))
            .sessionManagement(session -> session
                .sessionCreationPolicy(SessionCreationPolicy.STATELESS)
            )
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/api/auth/login", "/api/auth/register")
                    .permitAll()
                .requestMatchers("/api/auth/captcha").permitAll()
                .requestMatchers("/swagger-ui/**", "/v3/api-docs/**")
                    .permitAll()
                .requestMatchers("/api/admin/**").hasRole("ADMIN")
                .requestMatchers("/api/employee/**")
                    .hasAnyRole("ADMIN", "USER")
                .anyRequest().authenticated()
            )
            .formLogin(form -> form
                .loginProcessingUrl("/api/auth/login")
                .successHandler(successHandler)
                .failureHandler(failureHandler)
            )
            .logout(logout -> logout
                .logoutUrl("/api/auth/logout")
                .logoutSuccessHandler(new HttpStatusReturningLogoutSuccessHandler(
                    HttpStatus.OK))
            )
            .exceptionHandling(ex -> ex
                .authenticationEntryPoint(entryPoint)
                .accessDeniedHandler(deniedHandler)
            )
            .userDetailsService(userDetailsService);

        return http.build();
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

> 🚨 **坑：`csrf().disable()`必须配！** REST API是无状态的，不使用Session，CSRF攻击的前提（浏览器自动携带Session Cookie）不成立。如果不禁用CSRF，所有POST/PUT/DELETE请求都会返回403。

> 🚨 **坑：`requestMatchers`的顺序非常重要！** 规则从上到下匹配，第一个匹配的规则生效。如果先写`.anyRequest().authenticated()`，后面所有的`permitAll()`都不会被匹配到。**原则：先具体后宽泛。**

> 🚨 **坑：静态资源也需要放行！** 特别是Swagger文档路径`/swagger-ui/**`和`/v3/api-docs/**`，否则开发时无法访问API文档。

### 23.3.2 自定义登录成功/失败处理器

前后端分离架构下，登录成功/失败不能重定向到页面，必须返回JSON：

```java
@Component
public class JsonAuthenticationSuccessHandler
        implements AuthenticationSuccessHandler {

    private final ObjectMapper objectMapper;

    public JsonAuthenticationSuccessHandler(ObjectMapper objectMapper) {
        this.objectMapper = objectMapper;
    }

    @Override
    public void onAuthenticationSuccess(HttpServletRequest request,
                                        HttpServletResponse response,
                                        Authentication authentication)
            throws IOException {

        SecurityUser user = (SecurityUser) authentication.getPrincipal();

        Map<String, Object> data = new HashMap<>();
        data.put("id", user.getId());
        data.put("username", user.getUsername());
        data.put("authorities", authentication.getAuthorities().stream()
            .map(GrantedAuthority::getAuthority)
            .collect(Collectors.toList()));

        Result<Map<String, Object>> result = Result.success(data);

        response.setContentType("application/json;charset=UTF-8");
        response.setStatus(HttpStatus.OK.value());
        response.getWriter().write(objectMapper.writeValueAsString(result));
    }
}
```

```java
@Component
public class JsonAuthenticationFailureHandler
        implements AuthenticationFailureHandler {

    private final ObjectMapper objectMapper;

    public JsonAuthenticationFailureHandler(ObjectMapper objectMapper) {
        this.objectMapper = objectMapper;
    }

    @Override
    public void onAuthenticationFailure(HttpServletRequest request,
                                        HttpServletResponse response,
                                        AuthenticationException exception)
            throws IOException {

        String message;
        if (exception instanceof BadCredentialsException) {
            message = "用户名或密码错误";
        } else if (exception instanceof DisabledException) {
            message = "账号已被禁用";
        } else if (exception instanceof AccountExpiredException) {
            message = "账号已过期";
        } else if (exception instanceof LockedException) {
            message = "账号已被锁定";
        } else {
            message = "登录失败";
        }

        Result<Void> result = Result.error(401, message);

        response.setContentType("application/json;charset=UTF-8");
        response.setStatus(HttpStatus.UNAUTHORIZED.value());
        response.getWriter().write(objectMapper.writeValueAsString(result));
    }
}
```

> 🚨 **坑：前后端分离项目，登录成功不能重定向！** Spring Security默认的登录成功行为是重定向到首页（302重定向），但前端期望的是JSON响应。必须自定义`AuthenticationSuccessHandler`返回JSON。

### 23.3.3 自定义401和403处理器

未认证访问受保护资源返回401，已认证但权限不足返回403：

```java
@Component
public class JsonAuthenticationEntryPoint implements AuthenticationEntryPoint {

    private final ObjectMapper objectMapper;

    public JsonAuthenticationEntryPoint(ObjectMapper objectMapper) {
        this.objectMapper = objectMapper;
    }

    @Override
    public void commence(HttpServletRequest request,
                         HttpServletResponse response,
                         AuthenticationException authException)
            throws IOException {

        Result<Void> result = Result.error(401, "未登录，请先登录");

        response.setContentType("application/json;charset=UTF-8");
        response.setStatus(HttpStatus.UNAUTHORIZED.value());
        response.getWriter().write(objectMapper.writeValueAsString(result));
    }
}
```

```java
@Component
public class JsonAccessDeniedHandler implements AccessDeniedHandler {

    private final ObjectMapper objectMapper;

    public JsonAccessDeniedHandler(ObjectMapper objectMapper) {
        this.objectMapper = objectMapper;
    }

    @Override
    public void handle(HttpServletRequest request,
                       HttpServletResponse response,
                       AccessDeniedException accessDeniedException)
            throws IOException {

        Result<Void> result = Result.error(403, "权限不足，拒绝访问");

        response.setContentType("application/json;charset=UTF-8");
        response.setStatus(HttpStatus.FORBIDDEN.value());
        response.getWriter().write(objectMapper.writeValueAsString(result));
    }
}
```

---

## 23.4 RBAC权限模型

### 23.4.1 为什么需要RBAC

最简单的权限控制是在代码里写死`if (user.getRole().equals("ADMIN"))`，但这有几个问题：

- 新增角色需要改代码
- 角色权限变化需要改代码
- 权限粒度无法动态调整

RBAC（Role-Based Access Control，基于角色的访问控制）将权限与角色解耦，通过角色作为中间层连接用户和权限。这是企业级应用中最主流的权限模型。

### 23.4.2 五表设计

```
┌──────────────┐       ┌──────────────┐       ┌──────────────┐
│    user      │       │    role      │       │  permission  │
├──────────────┤       ├──────────────┤       ├──────────────┤
│ id (PK)      │       │ id (PK)      │       │ id (PK)      │
│ username     │       │ role_code    │       │ perm_code    │
│ password     │       │ role_name    │       │ perm_name    │
│ email        │       │ description  │       │ resource     │
│ enabled      │       │ enabled      │       │ description  │
│ create_time  │       │ create_time  │       │ create_time  │
│ update_time  │       │ update_time  │       │ update_time  │
└──────┬───────┘       └──────┬───────┘       └──────┬───────┘
       │                      │                      │
       │  ┌──────────────┐   │  ┌──────────────┐   │
       │  │  user_role   │   │  │role_permission│   │
       │  ├──────────────┤   │  ├──────────────┤   │
       └──┤ user_id (FK) │   └──┤ role_id (FK) │   │
          │ role_id (FK) │      │ perm_id (FK) │   │
          └──────────────┘      └──────────────┘   │
              M:N 关系              M:N 关系         │
                                                    │
          用户 ──M:N──▶ 角色 ──M:N──▶ 权限          │
```

### 23.4.3 完整建表SQL

```sql
CREATE DATABASE IF NOT EXISTS ems_security
    DEFAULT CHARACTER SET utf8mb4
    DEFAULT COLLATE utf8mb4_unicode_ci;

USE ems_security;

-- 用户表
CREATE TABLE `sys_user` (
    `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '用户ID',
    `username` VARCHAR(50) NOT NULL COMMENT '用户名',
    `password` VARCHAR(100) NOT NULL COMMENT '密码(BCrypt)',
    `email` VARCHAR(100) DEFAULT NULL COMMENT '邮箱',
    `enabled` TINYINT(1) NOT NULL DEFAULT 1 COMMENT '是否启用',
    `create_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `update_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_username` (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';

-- 角色表
CREATE TABLE `sys_role` (
    `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '角色ID',
    `role_code` VARCHAR(50) NOT NULL COMMENT '角色编码(如ADMIN)',
    `role_name` VARCHAR(100) NOT NULL COMMENT '角色名称(如系统管理员)',
    `description` VARCHAR(200) DEFAULT NULL COMMENT '描述',
    `enabled` TINYINT(1) NOT NULL DEFAULT 1 COMMENT '是否启用',
    `create_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `update_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_role_code` (`role_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='角色表';

-- 权限表
CREATE TABLE `sys_permission` (
    `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '权限ID',
    `perm_code` VARCHAR(100) NOT NULL COMMENT '权限编码(如user:delete)',
    `perm_name` VARCHAR(100) NOT NULL COMMENT '权限名称(如删除用户)',
    `resource` VARCHAR(200) DEFAULT NULL COMMENT '资源标识(如/api/users)',
    `description` VARCHAR(200) DEFAULT NULL COMMENT '描述',
    `create_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `update_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_perm_code` (`perm_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='权限表';

-- 用户-角色关联表
CREATE TABLE `sys_user_role` (
    `user_id` BIGINT NOT NULL COMMENT '用户ID',
    `role_id` BIGINT NOT NULL COMMENT '角色ID',
    PRIMARY KEY (`user_id`, `role_id`),
    KEY `idx_role_id` (`role_id`),
    CONSTRAINT `fk_user_role_user`
        FOREIGN KEY (`user_id`) REFERENCES `sys_user`(`id`)
        ON DELETE CASCADE,
    CONSTRAINT `fk_user_role_role`
        FOREIGN KEY (`role_id`) REFERENCES `sys_role`(`id`)
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户角色关联表';

-- 角色-权限关联表
CREATE TABLE `sys_role_permission` (
    `role_id` BIGINT NOT NULL COMMENT '角色ID',
    `perm_id` BIGINT NOT NULL COMMENT '权限ID',
    PRIMARY KEY (`role_id`, `perm_id`),
    KEY `idx_perm_id` (`perm_id`),
    CONSTRAINT `fk_role_perm_role`
        FOREIGN KEY (`role_id`) REFERENCES `sys_role`(`id`)
        ON DELETE CASCADE,
    CONSTRAINT `fk_role_perm_perm`
        FOREIGN KEY (`perm_id`) REFERENCES `sys_permission`(`id`)
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='角色权限关联表';

-- 初始化数据
INSERT INTO `sys_user` (`username`, `password`, `email`, `enabled`)
VALUES ('admin', '$2a$10$N9qo8uLOickgx2ZMRZoMyeIjZAgcfl7p92ldGxad68LJZdL17lhWy',
        'admin@ems.com', 1),
       ('zhangsan', '$2a$10$N9qo8uLOickgx2ZMRZoMyeIjZAgcfl7p92ldGxad68LJZdL17lhWy',
        'zhangsan@ems.com', 1);

INSERT INTO `sys_role` (`role_code`, `role_name`, `description`)
VALUES ('ADMIN', '系统管理员', '拥有所有权限'),
       ('USER', '普通用户', '基本操作权限');

INSERT INTO `sys_permission` (`perm_code`, `perm_name`, `resource`)
VALUES ('employee:list',   '查看员工列表', '/api/employee/list'),
       ('employee:detail', '查看员工详情', '/api/employee/{id}'),
       ('employee:add',    '新增员工',     '/api/employee'),
       ('employee:update', '编辑员工',     '/api/employee/{id}'),
       ('employee:delete', '删除员工',     '/api/employee/{id}'),
       ('user:manage',     '用户管理',     '/api/admin/user/**');

INSERT INTO `sys_user_role` (`user_id`, `role_id`)
VALUES (1, 1), (2, 2);

INSERT INTO `sys_role_permission` (`role_id`, `perm_id`)
VALUES
    (1, 1), (1, 2), (1, 3), (1, 4), (1, 5), (1, 6),
    (2, 1), (2, 2);
```

> 🚨 **坑：权限粒度设计要适度！** 太细（如每个按钮一个权限）→ 权限数据爆炸，维护困难；太粗（如只有"管理员"和"用户"两个角色）→ 控制不够灵活。**建议：资源级别控制**（如`user:read`/`user:write`），而非页面或按钮级别。

> 🚨 **坑：只控制前端路由不控制后端API是最致命的安全漏洞！** 前端隐藏了"删除"按钮，但攻击者可以直接用Postman调用`DELETE /api/employee/1`——API没有任何校验。**任何前端校验都是不可信的！后端必须独立做权限校验。**

### 23.4.4 权限查询SQL

```sql
SELECT DISTINCT r.role_code
FROM sys_role r
INNER JOIN sys_user_role ur ON r.id = ur.role_id
WHERE ur.user_id = #{userId} AND r.enabled = 1;

SELECT DISTINCT p.perm_code
FROM sys_permission p
INNER JOIN sys_role_permission rp ON p.id = rp.perm_id
INNER JOIN sys_role r ON r.id = rp.role_id
INNER JOIN sys_user_role ur ON r.id = ur.role_id
WHERE ur.user_id = #{userId} AND r.enabled = 1;
```

---

## 23.5 方法级安全

### 23.5.1 @EnableMethodSecurity

URL级别的权限控制（`requestMatchers`）只能控制到接口路径，但有时候同一个接口需要根据业务参数做更细粒度的权限判断。Spring Security 6.x提供了方法级安全：

```java
@Configuration
@EnableMethodSecurity
public class SecurityConfig {
}
```

> 注意：Spring Security 5.x用的是`@EnableGlobalMethodSecurity(prePostEnabled = true)`，6.x中已弃用，替换为`@EnableMethodSecurity`。

### 23.5.2 @PreAuthorize — 方法执行前检查

```java
@RestController
@RequestMapping("/api/employee")
public class EmployeeController {

    @GetMapping("/list")
    @PreAuthorize("hasAuthority('employee:list')")
    public Result<PageResult<EmployeeVO>> list(PageRequest pageRequest) {
        return Result.success(employeeService.list(pageRequest));
    }

    @DeleteMapping("/{id}")
    @PreAuthorize("hasRole('ADMIN')")
    public Result<Void> delete(@PathVariable Long id) {
        employeeService.deleteById(id);
        return Result.success();
    }

    @PutMapping("/{id}")
    @PreAuthorize("hasAuthority('employee:update')")
    public Result<Void> update(@PathVariable Long id,
                               @RequestBody EmployeeDTO dto) {
        employeeService.update(id, dto);
        return Result.success();
    }
}
```

**`hasRole` vs `hasAuthority`的区别**：

| 表达式 | 检查内容 | 数据库中存储 | 说明 |
|--------|---------|-------------|------|
| `hasRole('ADMIN')` | `ROLE_ADMIN` | `ADMIN` | 自动补`ROLE_`前缀 |
| `hasAuthority('employee:delete')` | `employee:delete` | `employee:delete` | 精确匹配 |

### 23.5.3 @PostAuthorize — 方法执行后检查

```java
@GetMapping("/{id}")
@PostAuthorize("returnObject.data.userId == authentication.principal.id "
             + "or hasRole('ADMIN')")
public Result<EmployeeVO> detail(@PathVariable Long id) {
    return Result.success(employeeService.getById(id));
}
```

`@PostAuthorize`在方法执行**之后**检查，可以访问返回值（`returnObject`）和当前认证信息（`authentication`）。上面的例子表示：普通用户只能查看自己的信息，管理员可以查看所有人的信息。

> ⚠️ 注意：`@PostAuthorize`是先执行方法再检查，如果方法有副作用（如修改数据），即使检查不通过，数据已经被修改了。所以它只适合只读操作。

### 23.5.4 SpEL表达式常用写法

| 表达式 | 含义 |
|--------|------|
| `hasRole('ADMIN')` | 拥有ADMIN角色 |
| `hasAnyRole('ADMIN', 'USER')` | 拥有任一角色 |
| `hasAuthority('user:delete')` | 拥有user:delete权限 |
| `hasAnyAuthority('user:read', 'user:write')` | 拥有任一权限 |
| `isAuthenticated()` | 已认证（非匿名） |
| `isAnonymous()` | 匿名用户 |
| `principal` | 当前认证用户对象 |
| `authentication` | 当前Authentication对象 |
| `permitAll` | 允许所有 |
| `denyAll` | 拒绝所有 |

### 23.5.5 自定义PermissionEvaluator

`hasPermission`是SpEL中更灵活的权限表达式，可以结合业务对象做权限判断：

```java
@Component
public class CustomPermissionEvaluator implements PermissionEvaluator {

    private final PermissionService permissionService;

    public CustomPermissionEvaluator(PermissionService permissionService) {
        this.permissionService = permissionService;
    }

    @Override
    public boolean hasPermission(Authentication authentication,
                                 Object targetDomainObject,
                                 Object permission) {
        SecurityUser user = (SecurityUser) authentication.getPrincipal();
        return permissionService.hasPermission(
            user.getId(), targetDomainObject, permission);
    }

    @Override
    public boolean hasPermission(Authentication authentication,
                                 Serializable targetId,
                                 String targetType,
                                 Object permission) {
        SecurityUser user = (SecurityUser) authentication.getPrincipal();
        return permissionService.hasPermission(
            user.getId(), targetId, targetType, permission);
    }
}
```

使用：

```java
@DeleteMapping("/{id}")
@PreAuthorize("hasPermission(#id, 'employee', 'delete')")
public Result<Void> delete(@PathVariable Long id) {
    employeeService.deleteById(id);
    return Result.success();
}
```

> 🚨 **坑：`@PreAuthorize`加在非public方法上不生效！** Spring Security方法级安全基于AOP代理，而Spring AOP默认只代理public方法。如果加在private/protected方法上，注解会被静默忽略——不会报错，但权限检查不生效。

---

## 23.6 常见问题与自定义

### 23.6.1 Spring Security 6.x迁移注意事项

从Spring Security 5.x迁移到6.x，除了前面提到的配置方式变化，还有以下注意点：

| 变更项 | 5.x | 6.x |
|--------|-----|-----|
| 配置方式 | `WebSecurityConfigurerAdapter` | `@Bean SecurityFilterChain` |
| 请求匹配 | `antMatchers()` | `requestMatchers()` |
| 授权API | `authorizeRequests()` | `authorizeHttpRequests()` |
| 方法安全 | `@EnableGlobalMethodSecurity` | `@EnableMethodSecurity` |
| CSRF默认 | 默认启用但可配置 | 默认启用，需显式禁用 |
| Session | 默认IF_REQUIRED | 默认IF_REQUIRED |

### 23.6.2 SameSite Cookie问题

> 🚨 **坑：SameSite Cookie属性导致跨站请求Cookie丢失！**

现代浏览器默认将Cookie的`SameSite`属性设为`Lax`，这意味着跨站的POST请求不会携带Cookie。如果你的前端和后端不在同一个域下，Session Cookie可能丢失。

解决方案：
1. 前后端同域部署（Nginx反向代理）
2. 使用JWT（不依赖Cookie，下一章详解）
3. 配置Cookie的SameSite为None（必须同时设置Secure，仅HTTPS可用）

### 23.6.3 CORS + Security配置

> 🚨 **坑：CORS预检请求被Security拦截！** 浏览器在跨域请求前会先发一个OPTIONS预检请求，如果Security拦截了OPTIONS请求，前端会收到403，导致跨域失败。

解决方法是在Security配置中**先于授权规则处理CORS**：

```java
@Bean
public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
    http
        .cors(cors -> cors.configurationSource(corsConfigurationSource()))
        .csrf(csrf -> csrf.disable())
        .authorizeHttpRequests(auth -> auth
            .requestMatchers(CorsUtils::isPreFlightRequest).permitAll()
            .requestMatchers("/api/auth/**").permitAll()
            .anyRequest().authenticated()
        );
    return http.build();
}
```

`CorsUtils::isPreFlightRequest`会匹配所有OPTIONS预检请求并放行。

### 23.6.4 自定义AuthenticationProvider

如果需要支持非标准的认证方式（如短信验证码登录），可以实现自定义`AuthenticationProvider`：

```java
public class SmsAuthenticationProvider implements AuthenticationProvider {

    private final UserDetailsService userDetailsService;

    public SmsAuthenticationProvider(UserDetailsService userDetailsService) {
        this.userDetailsService = userDetailsService;
    }

    @Override
    public Authentication authenticate(Authentication authentication)
            throws AuthenticationException {

        SmsAuthenticationToken smsToken = (SmsAuthenticationToken) authentication;
        String phone = (String) smsToken.getPrincipal();
        String code = (String) smsToken.getCredentials();

        if (!SmsCodeValidator.isValid(phone, code)) {
            throw new BadCredentialsException("验证码错误");
        }

        UserDetails userDetails =
            userDetailsService.loadUserByUsername(phone);

        SmsAuthenticationToken result = new SmsAuthenticationToken(
            userDetails, null, userDetails.getAuthorities());
        result.setDetails(smsToken.getDetails());
        return result;
    }

    @Override
    public boolean supports(Class<?> authentication) {
        return SmsAuthenticationToken.class.isAssignableFrom(authentication);
    }
}
```

### 23.6.5 获取当前登录用户信息

在业务代码中，经常需要获取当前登录用户的信息：

```java
@Service
public class EmployeeService {

    public void addEmployee(EmployeeDTO dto) {
        SecurityUser currentUser = (SecurityUser) SecurityContextHolder
            .getContext()
            .getAuthentication()
            .getPrincipal();

        Long currentUserId = currentUser.getId();
        String currentUsername = currentUser.getUsername();

        dto.setCreatedBy(currentUserId);
        employeeMapper.insert(dto);
    }
}
```

也可以在Controller中通过`@AuthenticationPrincipal`注解直接注入：

```java
@GetMapping("/profile")
public Result<UserProfileVO> getProfile(
        @AuthenticationPrincipal SecurityUser currentUser) {
    return Result.success(userService.getProfile(currentUser.getId()));
}
```

---

## 本章小结

本章我们学习了Spring Security的核心架构和使用方法：

1. **架构层面**：Spring Security基于Servlet过滤器链，每个请求经过多个安全过滤器的检查。核心组件包括SecurityContextHolder（存储认证信息）、AuthenticationManager（认证管理）、UserDetailsService（加载用户）、PasswordEncoder（密码编码）。

2. **配置方式**：Spring Security 6.x使用Lambda DSL配置，通过`@Bean SecurityFilterChain`替代了已弃用的`WebSecurityConfigurerAdapter`。配置时注意规则顺序（先具体后宽泛）、CSRF禁用（REST API场景）、静态资源放行。

3. **数据库认证**：自定义`UserDetailsService`从数据库加载用户，使用BCryptPasswordEncoder加密密码。BCrypt自动加盐、慢哈希，是目前最推荐的密码存储方案。

4. **RBAC权限模型**：五表设计（user/role/permission/user_role/role_permission）实现了用户-角色-权限的灵活关联。权限粒度建议控制在资源级别。

5. **方法级安全**：`@EnableMethodSecurity` + `@PreAuthorize`/`@PostAuthorize`实现了更细粒度的权限控制。注意只能用在public方法上。

6. **前后端分离适配**：自定义成功/失败处理器返回JSON，自定义401/403处理器，禁用CSRF，配置CORS。

---

## 思考题

1. Spring Security的过滤器链中，如果自定义一个JWT验证过滤器，应该放在哪个位置？为什么？

2. 为什么BCrypt每次加密同一个密码结果都不同，但`matches()`方法仍然能正确验证？请从BCrypt密文结构的角度解释。

3. 在RBAC模型中，如果需要实现"数据权限"（如用户只能看到自己部门的员工），仅靠五表设计够不够？你会怎么扩展？

4. `hasRole('ADMIN')`和`hasAuthority('ROLE_ADMIN')`效果是否相同？为什么Spring Security要设计`ROLE_`前缀的机制？

5. 如果你的系统需要同时支持"用户名密码登录"和"手机验证码登录"，Spring Security的架构如何优雅地支持这两种认证方式？
