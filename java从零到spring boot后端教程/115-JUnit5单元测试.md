# 115-JUnit5单元测试

> 💡 你改了一个 Service 方法，觉得"应该没问题"，就提交了。上线后凌晨3点报警——某个边界条件你没考虑。如果有单元测试，你在本地跑一次 `mvn test` 就能发现。JUnit 5 是 Java 标准测试框架，本章让你从"手动验证"切换到"自动化测试"。

---

## 本章目标
- 使用 JUnit 5 编写单元测试
- 掌握常用断言：assertEquals、assertThrows、assertAll
- 使用 `@BeforeEach` / `@AfterEach` 管理测试状态
- 使用 `@ParameterizedTest` 进行参数化测试
- 理解测试覆盖率的概念

---

## 115.1 第一个测试

### 待测试的代码

```java
public class Calculator {
    public int add(int a, int b) {
        return a + b;
    }

    public int divide(int a, int b) {
        if (b == 0) {
            throw new IllegalArgumentException("Divisor cannot be zero");
        }
        return a / b;
    }
}
```

### 测试类

```java
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

class CalculatorTest {

    private final Calculator calculator = new Calculator();

    @Test
    void testAdd() {
        int result = calculator.add(2, 3);
        assertEquals(5, result);
    }

    @Test
    void testDivide() {
        int result = calculator.divide(10, 2);
        assertEquals(5, result);
    }

    @Test
    void testDivideByZero() {
        assertThrows(IllegalArgumentException.class,
                () -> calculator.divide(10, 0));
    }
}
```

### 运行

```bash
mvn test
```

或在 IDE 中右键测试类 → Run。

### 关键点

| 元素 | 含义 |
|------|------|
| `@Test` | 标记这是一个测试方法 |
| `assertEquals(expected, actual)` | 断言两个值相等 |
| `assertThrows(异常.class, lambda)` | 断言 lambda 抛出了指定异常 |
| 方法名 `void` | 测试方法必须是 public void（JUnit 5 可以是 package-private） |

---

## 115.2 常用断言

```java
import static org.junit.jupiter.api.Assertions.*;

// 相等性
assertEquals(5, result);
assertEquals(3.14, pi, 0.001);        // 浮点数，第三个参数是允许误差
assertNotEquals(0, result);

// 真假
assertTrue(list.isEmpty());
assertFalse(user.isActive());

// 空值
assertNull(result);
assertNotNull(result);

// 引用
assertSame(expected, actual);          // 同一个对象
assertNotSame(obj1, obj2);

// 数组
assertArrayEquals(new int[]{1, 2, 3}, array);

// 超时
assertTimeout(Duration.ofSeconds(1), () -> slowOperation());

// 批量断言（全部执行，不会因第一个失败就停止）
assertAll(
    () -> assertEquals("john", user.getUsername()),
    () -> assertEquals("john@example.com", user.getEmail()),
    () -> assertTrue(user.isActive())
);
```

---

## 115.3 生命周期

```java
import org.junit.jupiter.api.*;

class LifecycleTest {

    @BeforeAll
    static void initAll() {
        System.out.println("在所有测试之前执行一次（必须是 static）");
    }

    @BeforeEach
    void init() {
        System.out.println("在每个测试之前执行");
    }

    @Test
    void test1() {
        System.out.println("test1");
    }

    @Test
    void test2() {
        System.out.println("test2");
    }

    @AfterEach
    void tearDown() {
        System.out.println("在每个测试之后执行");
    }

    @AfterAll
    static void tearDownAll() {
        System.out.println("在所有测试之后执行一次（必须是 static）");
    }
}
```

### 输出顺序

```
initAll
  init → test1 → tearDown
  init → test2 → tearDown
tearDownAll
```

### 典型用途

| 注解 | 用途 |
|------|------|
| `@BeforeAll` | 启动嵌入式数据库、创建共享资源 |
| `@BeforeEach` | 初始化测试数据、重置状态 |
| `@AfterEach` | 清理测试数据 |
| `@AfterAll` | 关闭数据库连接、释放资源 |

---

## 115.4 参数化测试

当需要对多组数据测试同一个逻辑时：

```java
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.*;

class CalculatorTest {

    @ParameterizedTest
    @CsvSource({
        "2, 3, 5",
        "0, 0, 0",
        "-1, 1, 0",
        "100, 200, 300"
    })
    void testAdd(int a, int b, int expected) {
        assertEquals(expected, calculator.add(a, b));
    }

    @ParameterizedTest
    @ValueSource(strings = {"", "  ", "\t", "\n"})
    void testIsBlank(String input) {
        assertTrue(input.isBlank());
    }

    @ParameterizedTest
    @MethodSource("provideTestData")
    void testWithMethod(int input, boolean expected) {
        assertEquals(expected, input > 0);
    }

    static Stream<Arguments> provideTestData() {
        return Stream.of(
            Arguments.of(1, true),
            Arguments.of(-1, false),
            Arguments.of(0, false)
        );
    }
}
```

---

## 115.5 测试命名与组织

### 命名约定

推荐格式：`方法名_条件_期望`

```java
@Test
void findById_WhenIdExists_ShouldReturnUser() { }

@Test
void findById_WhenIdNotExists_ShouldThrowException() { }
```

或者用 `@DisplayName`：

```java
@Test
@DisplayName("根据ID查找用户，ID存在时应返回用户对象")
void findByIdShouldReturnUserWhenIdExists() { }
```

### 使用 @Nested 组织测试

```java
@DisplayName("用户服务测试")
class UserServiceTest {

    @Nested
    @DisplayName("创建用户")
    class CreateUser {
        @Test
        void shouldCreateUserWithValidData() { }

        @Test
        void shouldRejectDuplicateEmail() { }
    }

    @Nested
    @DisplayName("查询用户")
    class FindUser {
        @Test
        void shouldFindUserById() { }

        @Test
        void shouldReturnEmptyWhenNotFound() { }
    }
}
```

---

## 115.6 Spring Boot 中使用 JUnit 5

```java
@SpringBootTest
class UserServiceTest {

    @Autowired
    private UserService userService;

    @Test
    void testCreateUser() {
        User user = userService.create("john", "john@example.com");
        assertNotNull(user.getId());
        assertEquals("john", user.getUsername());
    }
}
```

> ⚠️ `@SpringBootTest` 会启动完整的 Spring 上下文，速度较慢。本章聚焦纯 JUnit 5，第117章详解 Spring Boot 集成测试。

---

## 115.7 测试覆盖率

### 查看覆盖率

```bash
mvn clean test jacoco:report
```

需要添加 JaCoCo 插件：

```xml
<plugin>
    <groupId>org.jacoco</groupId>
    <artifactId>jacoco-maven-plugin</artifactId>
    <version>0.8.11</version>
    <executions>
        <execution>
            <goals>
                <goal>prepare-agent</goal>
            </goals>
        </execution>
    </executions>
</plugin>
```

报告位置：`target/site/jacoco/index.html`，用浏览器打开。

> 💡 覆盖率是参考指标，不是目标。100% 覆盖率不等于零 Bug。关注核心业务逻辑的覆盖率，而非 getter/setter。

---

## 115.8 完成效果

学完本章，你应该能：
1. 为任意 Java 类编写 JUnit 5 单元测试
2. 使用多种断言验证不同情况
3. 用参数化测试减少重复代码
4. 用 IDE 或 Maven 查看测试覆盖率

---

## 小结

| 知识点 | 核心注解/方法 |
|--------|-------------|
| 测试方法 | `@Test` |
| 断言 | `assertEquals`, `assertTrue`, `assertThrows`, `assertAll` |
| 生命周期 | `@BeforeAll`, `@BeforeEach`, `@AfterEach`, `@AfterAll` |
| 参数化测试 | `@ParameterizedTest`, `@CsvSource`, `@ValueSource`, `@MethodSource` |
| 组织测试 | `@Nested`, `@DisplayName` |
| 覆盖率 | JaCoCo 插件 → `mvn jacoco:report` |

---

## 自测题

1. `@BeforeEach` 和 `@BeforeAll` 有什么区别？各自适用于什么场景？
2. 你想测试一个方法在传入负数时抛 `IllegalArgumentException`，怎么写？
3. 参数化测试中 `@CsvSource` 和 `@MethodSource` 的使用场景有何不同？

<details>
<summary>点击查看答案</summary>

1. `@BeforeEach` 在每个 `@Test` 方法前都执行一次，适合初始化测试数据；`@BeforeAll` 在所有测试前只执行一次（必须是 static），适合启动数据库等重量级操作。
2. 
```java
assertThrows(IllegalArgumentException.class,
    () -> myService.process(-1));
```
3. `@CsvSource` 适合简单的几组参数直接写在注解里；`@MethodSource` 适合参数多、数据量大、或数据需要动态生成的场景。
</details>