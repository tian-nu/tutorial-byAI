# 73-依赖注入（IoC容器）

> 💡 你买了一套精装房。开发商已经把水电、地板、墙面都弄好了，你拎包入住即可。但如果有一天你想把厨房的洗菜池换成双槽的，你不能直接砸墙——你得按规矩来：拆旧、接管、密封、验收。Spring IoC 容器就是这套"精装房"——它把对象之间的关系在"开盘"前装配好，你拎包入住；你要换零件？按规则声明即可，不用砸墙。

---

## 本章目标
- 掌握 `@Component`、`@Service`、`@Repository`、`@Controller` 四种组件注解
- 理解 `@Autowired` 构造器注入的原理与最佳实践
- 处理多实现冲突：`@Qualifier` 与 `@Primary`
- 掌握 Bean 的五个作用域及其适用场景
- 了解 Bean 生命周期：`@PostConstruct` 与 `@PreDestroy`

---

## 73.1 把类交给 Spring ——四种组件注解

在 Spring 的世界里，你写的普通 Java 类不会自动成为"被管理的 Bean"。你必须用注解**声明**："这个类请 Spring 帮我管理。"

Spring 提供了四种语义相同的注解（底层都是 `@Component`），但为不同层提供了语义区分：

| 注解 | 语义层 | 作用 |
|------|--------|------|
| `@Component` | 通用 | 任何 Spring 管理的组件 |
| `@Service` | 业务逻辑层 | 标注 Service 类，语义更清晰 |
| `@Repository` | 数据访问层 | 标注 DAO / Repository 类，自动翻译数据库异常 |
| `@Controller` | 表现层 | 标注 Spring MVC 控制器（第75章详讲） |

```java
package com.example.demo.service;

import org.springframework.stereotype.Service;

@Service  // 等价于 @Component，但阅读代码时一眼就知道这是业务层
public class UserService {

    public String getUserName(Long id) {
        return "User-" + id;
    }
}
```

> 四者本质上没有功能差异。使用 `@Service` 而不是裸 `@Component` 的唯一原因：**代码即文档**——6个月后的你看到 `@Service` 就知道这是业务逻辑。

---

## 73.2 构造器注入——推荐的依赖引入方式

上一章讲了 DI 的三种方式。这里聚焦最佳实践：**构造器注入**。

```java
package com.example.demo.service;

import com.example.demo.repository.UserRepository;
import org.springframework.stereotype.Service;

@Service
public class UserService {

    private final UserRepository userRepository;

    // Spring 4.3+ 后，如果只有一个构造器，@Autowired 可省略
    public UserService(UserRepository userRepository) {
        this.userRepository = userRepository;
    }

    public String findUserEmail(Long id) {
        return userRepository.findEmailById(id);
    }
}
```

对应的 Repository：

```java
package com.example.demo.repository;

import org.springframework.stereotype.Repository;

@Repository
public class UserRepository {

    public String findEmailById(Long id) {
        return "user" + id + "@example.com";
    }
}
```

### 为什么构造器注入最好？

用一个反例说明——字段注入的灾难：

```java
@Service
public class UserService {

    @Autowired
    private UserRepository userRepository;

    // 某天你写了一个测试：
    public static void main(String[] args) {
        UserService service = new UserService();          // 编译通过！
        service.findUserEmail(1L);                        // 💥 NullPointerException！
    }
}
```

`userRepository` 是 `null`——因为字段注入依赖 Spring 容器来设置值，`new UserService()` 不会触发注入。而构造器注入的做法：

```java
@Service
public class UserService {

    private final UserRepository userRepository;

    public UserService(UserRepository userRepository) {
        this.userRepository = userRepository;
    }

    // new UserService(null) 编译通过，但需要显式传 null
    // 正常使用时 Spring 必须提供一个 UserRepository 才能创建 UserService
}
```

> 🤔 想多一点：构造器注入的另一个优势是**不可变性**。`private final` 确保依赖在对象创建后不会被中途替换。这在多线程环境下尤其重要——你不能让一个正在处理请求的 Service 突然被换了 Repository。

---

## 73.3 当多个实现冲突时——@Qualifier 与 @Primary

一个接口有两个实现类，Spring 该注入哪一个？

```java
public interface PaymentService {
    void pay(int amount);
}

@Service
public class AlipayService implements PaymentService {
    @Override
    public void pay(int amount) {
        System.out.println("支付宝支付：" + amount);
    }
}

@Service
public class WechatPayService implements PaymentService {
    @Override
    public void pay(int amount) {
        System.out.println("微信支付：" + amount);
    }
}
```

如果 OrderService 直接注入 `PaymentService`：

```java
@Service
public class OrderService {

    private final PaymentService paymentService;

    public OrderService(PaymentService paymentService) {
        this.paymentService = paymentService;
    }
}
```

**启动报错**：

```
Field paymentService in OrderService required a single bean, but 2 were found:
  - alipayService
  - wechatPayService
```

### 解决方法一：@Qualifier（精确指定）

```java
@Service
public class OrderService {

    private final PaymentService paymentService;

    public OrderService(@Qualifier("alipayService") PaymentService paymentService) {
        this.paymentService = paymentService;
    }
}
```

`@Qualifier("alipayService")` 中的名字是**类名首字母小写**（Bean 的默认名称）。也可以自定义：

```java
@Service("aliPay")
public class AlipayService implements PaymentService { }

// 使用时
public OrderService(@Qualifier("aliPay") PaymentService paymentService) { }
```

### 解决方法二：@Primary（默认首选）

在某个实现上加 `@Primary`，Spring 在没有 `@Qualifier` 时优先选它：

```java
@Service
@Primary
public class AlipayService implements PaymentService { }
```

优先级：`@Qualifier` > `@Primary` > 按类型匹配。

> 🤔 想多一点：`@Primary` 适合"大多数情况下用这个"的场景。如果你的系统 90% 的地方用支付宝、10% 的地方用微信，给支付宝加 `@Primary`，10% 的地方加 `@Qualifier("wechatPayService")` 即可。

---

## 73.4 Bean 的作用域——何时创建、何时销毁

Spring 默认是**单例（Singleton）**——整个容器中只有一个实例。但有时候你需要不同生命周期的 Bean。

| 作用域 | 说明 | 比喻 |
|--------|------|------|
| `singleton`（默认） | 整个容器只一个实例 | 全公司的饮水机→大家都用一个 |
| `prototype` | 每次注入/获取都创建新实例 | 一次性纸杯→每人拿到的都是新的 |
| `request` | 每个 HTTP 请求一个实例 | 挂号单→每次看病一张新单子 |
| `session` | 每个 HTTP 会话一个实例 | 购物车→同一人多次购物共用一个 |
| `application` | ServletContext 级别，全局唯一 | 公司大门→所有人都过同一扇门 |

```java
import org.springframework.context.annotation.Scope;
import org.springframework.stereotype.Component;

@Component
@Scope("prototype")
public class ShoppingCart {
    private List<String> items = new ArrayList<>();

    public void addItem(String item) {
        items.add(item);
    }
}
```

### Singleton 与 Prototype 的陷阱

```java
@Service
public class OrderService {

    @Autowired
    private ShoppingCart cart;  // 每次注入的 cart 是同一个吗？
}
```

- 如果 `ShoppingCart` 是 **singleton**（默认）：所有请求共享同一个 cart——购物车会乱套。
- 如果 `ShoppingCart` 是 **prototype**：每次注入都是新实例——但注意：**单例 Bean 中的 prototype Bean 只在创建时注入一次**，之后不会重新创建。

> 这是 Spring 新手最常踩的坑之一。一个 `@Scope("prototype")` 的 Bean 被注入到 `@Scope("singleton")` 的 Bean 中，这个 prototype Bean 只会被创建一次（单例 Bean 创建时）并始终使用同一个引用。解决方法：使用 `ObjectFactory` 或 `@Lookup`。

---

## 73.5 Bean 生命周期——创建到销毁的全流程

Spring 中的 Bean 从"出生"到"死亡"经历以下阶段：

```
实例化 → 属性填充 → BeanNameAware → BeanFactoryAware
→ @PostConstruct → InitializingBean.afterPropertiesSet()
→ init-method → Bean 就绪
   ...（Bean 在工作）...
→ @PreDestroy → DisposableBean.destroy()
→ destroy-method → Bean 销毁
```

你只需要关心两个最常用的：

```java
import jakarta.annotation.PostConstruct;
import jakarta.annotation.PreDestroy;
import org.springframework.stereotype.Component;

@Component
public class DatabaseConnectionPool {

    @PostConstruct
    public void init() {
        System.out.println("连接池初始化：建立 10 条数据库连接");
    }

    @PreDestroy
    public void cleanup() {
        System.out.println("连接池销毁：关闭所有数据库连接");
    }
}
```

### 启动时验证

```java
@SpringBootApplication
public class DemoApplication {
    public static void main(String[] args) {
        ConfigurableApplicationContext context =
            SpringApplication.run(DemoApplication.class, args);
        // 运行一段时间后手动关闭
        context.close();  // 触发所有 @PreDestroy 方法
    }
}
```

### 实用案例：项目启动时预加载数据

```java
@Component
public class DataInitializer {

    private final UserRepository userRepository;

    public DataInitializer(UserRepository userRepository) {
        this.userRepository = userRepository;
    }

    @PostConstruct
    public void init() {
        if (userRepository.count() == 0) {
            // 数据库为空，插入默认管理员
            System.out.println("初始化默认数据...");
        }
    }
}
```

> 🤔 想多一点：`@PostConstruct` 和构造器的区别——构造器执行时，Spring 还**没有**完成依赖注入。字段可能还是 null。`@PostConstruct` 执行时，所有依赖注入已完毕，依赖可用。所以**初始化逻辑放在 @PostConstruct** 而不是构造器。

---

## 73.6 小结

| 知识点 | 核心内容 |
|--------|----------|
| 四种组件注解 | @Component / @Service / @Repository / @Controller——功能等价，语义不同 |
| 构造器注入 | 推荐方式：依赖不可变、编译期检查、无 NPE 隐患 |
| @Qualifier | 多实现时精确指定注入哪个 Bean |
| @Primary | 多实现时标记默认首选 |
| Singleton 作用域 | 默认：全容器唯一实例 |
| Prototype 作用域 | 每次获取新实例，但注意单例内注入的问题 |
| @PostConstruct | 依赖注入完成后执行初始化 |
| @PreDestroy | 容器销毁前执行清理 |

---

## 73.7 自测题

**1. 以下哪个注解在功能上与 @Component 完全不同？**

A. @Service  
B. @Repository  
C. @Controller  
D. 以上三者功能与 @Component 完全相同  

**2. 一个接口 `PaymentService` 有 `AlipayService` 和 `WechatPayService` 两个实现。启动时 Spring 报错 `required a single bean, but 2 were found`。列举两种解决方法。**

**3. 以下代码有什么问题？**

```java
@Service
public class ReportService {

    @Autowired
    private DataSource dataSource;  // @Scope("prototype")

    public Report generate() {
        // 每次调用 generate() 期望拿到一个新的 DataSource
        Connection conn = dataSource.getConnection();
        // ...
    }
}
```

---

**答案提示**：1→D（四者功能完全相同，仅语义不同）。2→方法一：注入处加 `@Qualifier("alipayService")`；方法二：给首选实现加 `@Primary`。3→DataSource 是 prototype 作用域，但 ReportService 是 singleton，DataSource 只会在 ReportService 创建时注入一次。后续 generate() 调用始终使用同一个 DataSource。解决方法：使用 `ObjectFactory<DataSource>` 或 `@Lookup` 方法。下一章——配置管理。