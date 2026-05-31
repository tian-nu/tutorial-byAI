# 117-SpringBoot集成测试

> 💡 单元测试告诉你每个齿轮没问题，但组装起来的机器能转吗？Controller 收到了正确的 JSON 吗？Service 真的写了数据库吗？拦截器拦对了吗？集成测试启动完整的 Spring 上下文，模拟真实的 HTTP 请求，端到端验证你的应用。本章教你用 Spring Boot Test 写出"像真的请求一样"的测试。

---

## 本章目标
- 使用 `@SpringBootTest` 加载完整上下文
- 使用 `MockMvc` 测试 Controller 层
- 使用 `@DataJpaTest` 测试 Repository 层
- 使用 `@TestConfiguration` 替换 Bean
- 使用 Testcontainers 替代真实数据库

---

## 117.1 依赖准备

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-test</artifactId>
    <scope>test</scope>
</dependency>

<dependency>
    <groupId>com.h2database</groupId>
    <artifactId>h2</artifactId>
    <scope>test</scope>
</dependency>
```

`spring-boot-starter-test` 包含了 JUnit 5、Mockito、MockMvc、AssertJ 等。

---

## 117.2 @SpringBootTest——全量上下文

```java
@SpringBootTest
class UserServiceIntegrationTest {

    @Autowired
    private UserService userService;

    @Test
    void testCreateAndFindUser() {
        User created = userService.create("alice", "alice@example.com");
        assertNotNull(created.getId());

        User found = userService.findById(created.getId());
        assertEquals("alice", found.getUsername());
    }
}
```

### 关键配置

```java
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
class FullIntegrationTest {

    @LocalServerPort
    private int port;

    @Autowired
    private TestRestTemplate restTemplate;

    @Test
    void testHealthEndpoint() {
        ResponseEntity<String> response = restTemplate.getForEntity(
                "http://localhost:" + port + "/health", String.class);
        assertEquals(HttpStatus.OK, response.getStatusCode());
    }
}
```

| 参数 | 含义 |
|------|------|
| `RANDOM_PORT` | 随机端口启动 Web 容器 |
| `DEFINED_PORT` | 使用 `server.port` 配置的端口 |
| `MOCK`（默认） | 不启动真实 Web 容器 |
| `NONE` | 不启动 Web 环境 |

---

## 117.3 MockMvc——测试 Controller

MockMvc 不启动真实 HTTP 服务器，但能完整走 Spring MVC 的请求处理链路。

```java
@SpringBootTest
@AutoConfigureMockMvc
class UserControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @Test
    void testGetUserById() throws Exception {
        mockMvc.perform(get("/api/users/1")
                        .contentType(MediaType.APPLICATION_JSON))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.data.username").value("alice"))
                .andExpect(jsonPath("$.data.email").value("alice@example.com"));
    }

    @Test
    void testCreateUser() throws Exception {
        String json = """
                {
                    "username": "bob",
                    "email": "bob@example.com",
                    "password": "password123"
                }
                """;

        mockMvc.perform(post("/api/users")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(json))
                .andExpect(status().isCreated())
                .andExpect(jsonPath("$.data.id").isNumber());
    }

    @Test
    void testCreateUserWithInvalidEmail() throws Exception {
        String json = """
                {"username": "bob", "email": "not-an-email", "password": "123"}
                """;

        mockMvc.perform(post("/api/users")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(json))
                .andExpect(status().isBadRequest());
    }
}
```

### 常用 MockMvc 方法

```java
// 请求方法
mockMvc.perform(get("/api/users"))
mockMvc.perform(post("/api/users"))
mockMvc.perform(put("/api/users/1"))
mockMvc.perform(delete("/api/users/1"))

// 请求头与参数
.param("page", "0")
.param("size", "10")
.header("Authorization", "Bearer " + token)

// 响应断言
.andExpect(status().isOk())
.andExpect(status().isCreated())
.andExpect(status().isBadRequest())
.andExpect(jsonPath("$.message").exists())
.andExpect(content().string(containsString("success")))

// 打印请求/响应（调试用）
.andDo(print())
```

---

## 117.4 @DataJpaTest——只测数据层

```java
@DataJpaTest
class UserRepositoryTest {

    @Autowired
    private UserRepository userRepository;

    @Test
    void testFindByEmail() {
        User user = new User();
        user.setUsername("alice");
        user.setEmail("alice@example.com");
        userRepository.save(user);

        Optional<User> found = userRepository.findByEmail("alice@example.com");
        assertTrue(found.isPresent());
        assertEquals("alice", found.get().getUsername());
    }

    @Test
    void testFindByEmailNotFound() {
        Optional<User> found = userRepository.findByEmail("nonexistent@example.com");
        assertTrue(found.isEmpty());
    }
}
```

### @DataJpaTest 的特点

| 特性 | 说明 |
|------|------|
| 只加载 Repository | 不加载 Service、Controller |
| 自动配置 H2 | 用内存数据库替代 MySQL |
| 自动事务回滚 | 每个测试结束后数据自动清空 |
| 快 | 比 `@SpringBootTest` 快很多 |

---

## 117.5 @TestConfiguration——替换 Bean

有时你需要用 Mock 替换某个 Bean：

```java
@SpringBootTest
class UserServiceWithMockTest {

    @Autowired
    private UserService userService;

    @TestConfiguration
    static class MockConfig {
        @Bean
        @Primary
        public EmailService emailService() {
            return Mockito.mock(EmailService.class);
        }
    }

    @Autowired
    private EmailService emailService;

    @Test
    void testCreateUserSendsEmail() {
        userService.create("alice", "alice@example.com");
        verify(emailService, times(1)).sendWelcomeEmail(any(User.class));
    }
}
```

---

## 117.6 Testcontainers——用真实数据库测试

H2 虽然快，但和 MySQL 语法有差异。

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-testcontainers</artifactId>
    <scope>test</scope>
</dependency>
<dependency>
    <groupId>org.testcontainers</groupId>
    <artifactId>mysql</artifactId>
    <scope>test</scope>
</dependency>
```

### 配置

```java
@SpringBootTest
@Testcontainers
class UserRepositoryMySQLTest {

    @Container
    static MySQLContainer<?> mysql = new MySQLContainer<>("mysql:8.0")
            .withDatabaseName("testdb")
            .withUsername("test")
            .withPassword("test");

    @DynamicPropertySource
    static void configureProperties(DynamicPropertyRegistry registry) {
        registry.add("spring.datasource.url", mysql::getJdbcUrl);
        registry.add("spring.datasource.username", mysql::getUsername);
        registry.add("spring.datasource.password", mysql::getPassword);
    }

    @Autowired
    private UserRepository userRepository;

    @Test
    void testSaveAndFind() {
        // 和真实 MySQL 完全一致的行为
        User user = new User();
        user.setUsername("alice");
        userRepository.save(user);

        assertNotNull(user.getId());
    }
}
```

> ⚠️ 首次运行会下载 MySQL 镜像，需要一点时间。Testcontainers 需要 Docker 运行。

---

## 117.7 测试环境的 application.yml

`src/test/resources/application.yml`：

```yaml
spring:
  datasource:
    url: jdbc:h2:mem:testdb;MODE=MySQL
    driver-class-name: org.h2.Driver
    username: sa
    password:
  jpa:
    hibernate:
      ddl-auto: create-drop
    show-sql: true

logging:
  level:
    root: WARN
```

---

## 117.8 完成效果

学完本章，你应该能：
1. 用 `@SpringBootTest` + `TestRestTemplate` 做端到端测试
2. 用 `MockMvc` 测试 Controller 层的请求/响应
3. 用 `@DataJpaTest` 专注测试数据访问层
4. 用 Testcontainers 运行真实数据库的集成测试

---

## 小结

| 测试层级 | 注解 | 速度 | 覆盖范围 |
|----------|------|------|----------|
| 单元测试 | `@ExtendWith(MockitoExtension.class)` | 极快 | Service 逻辑 |
| Repository | `@DataJpaTest` | 快 | 数据访问层 |
| Controller | `@WebMvcTest` | 快 | 单层 Web |
| 集成测试 | `@SpringBootTest` | 慢 | 全链路 |
| 真实 DB | `@SpringBootTest` + Testcontainers | 慢 | 全链路 + 真实数据库 |

---

## 自测题

1. `@WebMvcTest(UserController.class)` 和 `@SpringBootTest` + `@AutoConfigureMockMvc` 的区别是什么？
2. `@DataJpaTest` 的默认事务行为是什么？如何关闭自动回滚？
3. H2 数据库的 `MODE=MySQL` 配置是干什么的？

<details>
<summary>点击查看答案</summary>

1. `@WebMvcTest` 只加载 Controller 层和相关配置，需要 Mock Service；`@SpringBootTest` 加载完整上下文，Service 是真实对象。前者更快但覆盖率低。
2. 默认每个 `@Test` 方法的事务会自动回滚（不提交到数据库），保证测试数据隔离。要关闭：在方法上加 `@Rollback(false)` 或类上加 `@Transactional(propagation = Propagation.NOT_SUPPORTED)`。
3. 让 H2 尽量模拟 MySQL 的 SQL 语法和行为，减少因语法差异导致的测试通过而生产失败的假阳性问题。
</details>