# 100-设计模式（Java实现）

> 💡 你去宜家买家具。宜家不告诉你"怎么造一把椅子"，它给你一张图纸——上面画好了椅子由椅腿、椅面、螺丝组成，以及怎么组装。设计模式就是软件工程中的"宜家图纸"——不是代码，而是被无数人验证过的可复用解决方案。本章精选 5 种在 Java 和 Spring 中最常见的模式，每种都回答三个问题：什么场景、怎么实现、Spring 里怎么用。

---

## 本章目标
- 掌握 5 种关键设计模式：单例、工厂、策略、观察者、依赖注入
- 每种能写出 Java 实现
- 知道每种模式在 Spring 框架中的应用位置
- 面试时能讲清模式意图与场景

---

## 100.1 单例模式（Singleton）

### 意图

确保一个类只有一个实例，并提供全局访问点。

### 场景

- 数据库连接池
- 配置管理器
- 日志工厂

### Java 实现（饿汉式 — 最简单可靠）

```java
public class DatabasePool {
    private static final DatabasePool INSTANCE = new DatabasePool();

    private DatabasePool() {}  // 私有构造器，外部不能 new

    public static DatabasePool getInstance() {
        return INSTANCE;
    }

    public void connect() {
        System.out.println("连接数据库");
    }
}
```

### 懒汉式（线程安全，双重检查锁）

```java
public class DatabasePool {
    private static volatile DatabasePool instance;

    private DatabasePool() {}

    public static DatabasePool getInstance() {
        if (instance == null) {
            synchronized (DatabasePool.class) {
                if (instance == null) {
                    instance = new DatabasePool();
                }
            }
        }
        return instance;
    }
}
```

### 枚举单例（最安全，防止反射破坏）

```java
public enum DatabasePool {
    INSTANCE;

    public void connect() {
        System.out.println("连接数据库");
    }
}
```

### Spring 中的应用

Spring 容器管理的 Bean **默认就是单例**（`@Scope("singleton")`）。你在任何地方 `@Autowired` 获取的都是同一个实例。

```java
@Service  // 默认单例
public class UserService { }

@Scope("prototype")  // 每次获取都是新实例
public class ShoppingCart { }
```

---

## 100.2 工厂模式（Factory Pattern）

### 意图

不直接 `new`，而是通过工厂方法创建对象。让调用方和具体实现类解耦。

### 场景

- 支付方式选择（支付宝 / 微信 / 银行卡）
- 数据库驱动加载
- 日志框架适配

### Java 实现

```java
// 产品接口
public interface PaymentService {
    void pay(BigDecimal amount);
}

// 具体产品
public class AlipayService implements PaymentService {
    @Override
    public void pay(BigDecimal amount) {
        System.out.println("支付宝支付: " + amount);
    }
}

public class WechatPayService implements PaymentService {
    @Override
    public void pay(BigDecimal amount) {
        System.out.println("微信支付: " + amount);
    }
}

// 工厂
public class PaymentFactory {
    public static PaymentService create(String type) {
        return switch (type) {
            case "alipay" -> new AlipayService();
            case "wechat" -> new WechatPayService();
            default -> throw new IllegalArgumentException("不支持的支付方式: " + type);
        };
    }
}

// 使用
PaymentService payment = PaymentFactory.create("alipay");
payment.pay(new BigDecimal("100.00"));
```

> 🤔 想多一点：上面的工厂每次调用都 new 一个新对象。如果支付服务是无状态的，可以把实例缓存起来——这就是"工厂 + 单例"的组合，也是 Spring 容器干的事。

### Spring 中的应用

- `BeanFactory` 和 `ApplicationContext` 本质上就是超级工厂
- Spring AOP 的 `ProxyFactory`
- Jackson 的 `ObjectMapper`（工厂方法创建 JsonParser / JsonGenerator）

---

## 100.3 策略模式（Strategy Pattern）

### 意图

定义一组算法，将它们封装起来，让它们可以互相替换。策略模式让算法的变化独立于使用算法的客户端。

### 场景

- 不同等级的折扣策略
- 不同文件格式的导出（PDF / Excel / Word）
- 不同消息通知渠道（短信 / 邮件 / 推送）

### 类图

```
┌──────────────┐         ┌──────────────────┐
│  Calculator  │────────→│  DiscountStrategy │ (接口)
│              │         ├──────────────────┤
│ calc(price)  │         │ discount(price)   │
└──────────────┘         └───────┬──────────┘
                                 │
                    ┌────────────┼────────────┐
                    ▼            ▼            ▼
             ┌──────────┐ ┌──────────┐ ┌──────────┐
             │ NoDiscount│ │VIPDiscount│ │SVIPDiscount│
             │  无折扣   │ │  9折     │ │  8折     │
             └──────────┘ └──────────┘ └──────────┘
```

### Java 实现

```java
// 策略接口
public interface DiscountStrategy {
    BigDecimal discount(BigDecimal price);
}

// 具体策略
@Component("vip")
public class VipDiscount implements DiscountStrategy {
    @Override
    public BigDecimal discount(BigDecimal price) {
        return price.multiply(new BigDecimal("0.9"));
    }
}

@Component("svip")
public class SvipDiscount implements DiscountStrategy {
    @Override
    public BigDecimal discount(BigDecimal price) {
        return price.multiply(new BigDecimal("0.8"));
    }
}

// 上下文
@Service
@RequiredArgsConstructor
public class PriceCalculator {

    private final Map<String, DiscountStrategy> strategyMap;

    @Autowired
    public PriceCalculator(List<DiscountStrategy> strategies) {
        this.strategyMap = new HashMap<>();
        for (DiscountStrategy s : strategies) {
            if (s instanceof VipDiscount) strategyMap.put("vip", s);
            else if (s instanceof SvipDiscount) strategyMap.put("svip", s);
        }
    }

    public BigDecimal calculate(String userLevel, BigDecimal price) {
        DiscountStrategy strategy = strategyMap.getOrDefault(userLevel,
                p -> p);  // 默认原价
        return strategy.discount(price);
    }
}
```

### 优化：用 Bean 名称作为策略 Key

```java
@Service
@RequiredArgsConstructor
public class PriceCalculator {

    private final Map<String, DiscountStrategy> strategyMap;

    public BigDecimal calculate(String userLevel, BigDecimal price) {
        DiscountStrategy strategy = strategyMap.getOrDefault(userLevel, p -> p);
        return strategy.discount(price);
    }
}
```

当策略类用 `@Component("vip")` 注册时，Spring 自动把 Bean 名称作为 Map 的 key。

### Spring 中的应用

- `SimpleMimeMessagePreparator` — 不同的邮件生成策略
- `PlatformTransactionManager` — 不同的事务管理策略
- Spring Security 的 `AuthenticationProvider` — 不同的认证策略

---

## 100.4 观察者模式（Observer Pattern）

### 意图

定义一对多依赖，当一个对象状态改变时，所有依赖者自动收到通知。

### 场景

- 用户注册后发短信 + 发邮件 + 送优惠券
- 订单状态变更通知
- Spring Event（本章重点）

### Java 实现（传统方式）

```java
// 观察者接口
public interface Observer {
    void update(String message);
}

// 主题（被观察者）
public class Subject {
    private final List<Observer> observers = new ArrayList<>();

    public void attach(Observer o) { observers.add(o); }
    public void detach(Observer o) { observers.remove(o); }

    public void notifyAll(String message) {
        for (Observer o : observers) {
            o.update(message);
        }
    }
}

// 具体观察者
public class SmsObserver implements Observer {
    @Override
    public void update(String message) {
        System.out.println("发短信: " + message);
    }
}
```

### Spring 中的实现：ApplicationEvent

```java
// 事件类
@Getter
public class UserRegisteredEvent extends ApplicationEvent {
    private final Long userId;
    private final String username;

    public UserRegisteredEvent(Object source, Long userId, String username) {
        super(source);
        this.userId = userId;
        this.username = username;
    }
}

// 发布事件
@Service
@RequiredArgsConstructor
public class UserService {
    private final ApplicationEventPublisher publisher;

    public void register(User user) {
        // ... 注册逻辑
        publisher.publishEvent(new UserRegisteredEvent(this, user.getId(), user.getUsername()));
    }
}

// 监听者 1
@Component
public class SmsListener {
    @EventListener
    public void handleUserRegistered(UserRegisteredEvent event) {
        System.out.println("发短信给: " + event.getUsername());
    }
}

// 监听者 2
@Component
public class EmailListener {
    @EventListener
    @Async  // 异步执行
    public void handleUserRegistered(UserRegisteredEvent event) {
        System.out.println("发邮件给: " + event.getUsername());
    }
}
```

> 🤔 想多一点：用 Spring Event 实现观察者模式，发布者和监听者完全解耦——发布者不知道谁在监听，监听者不知道谁发布的。新增监听者只需加一个类 + `@EventListener`，不需要改任何已有代码。这就是开闭原则（对扩展开放，对修改关闭）的完美实践。

---

## 100.5 依赖注入（Dependency Injection）

### 意图

类的依赖不是自己创建，而是由外部注入。这是 Spring 框架的基石。

### 场景

- 任何需要"组装"多个组件的场景
- Spring 中几乎到处都是

### Java 实现（手动 DI）

```java
// 传统方式：自己 new
public class OrderService {
    private UserRepository userRepo = new UserRepository();
    private PaymentService paymentService = new AlipayService();
}

// 依赖注入：通过构造器注入
public class OrderService {
    private final UserRepository userRepo;
    private final PaymentService paymentService;

    public OrderService(UserRepository userRepo, PaymentService paymentService) {
        this.userRepo = userRepo;
        this.paymentService = paymentService;
    }
}

// 组装由外部（Spring 容器）完成
OrderService service = new OrderService(
    new UserRepository(),
    new AlipayService()
);
```

### Spring 中的三种注入方式

```java
// ① 构造器注入（推荐！）— 不可变 + 强制依赖
@Service
public class OrderService {
    private final UserRepository userRepo;

    public OrderService(UserRepository userRepo) {
        this.userRepo = userRepo;
    }
}

// ② Setter 注入 — 可选依赖
@Service
public class OrderService {
    private UserRepository userRepo;

    @Autowired
    public void setUserRepo(UserRepository userRepo) {
        this.userRepo = userRepo;
    }
}

// ③ 字段注入（不推荐！）— 方便但难以测试
@Service
public class OrderService {
    @Autowired
    private UserRepository userRepo;
}
```

> ⚠️ 为什么不用字段注入？当你想单元测试 `OrderService` 时，你无法传入一个 Mock 的 `UserRepository`——因为它是 `private` 字段，只能通过反射注入。构造器注入允许你在测试中 `new OrderService(mockRepo)`。

---

## 100.6 五种模式速查

| 模式 | 核心思想 | 一句话 | Spring 中的应用 |
|------|------|------|------|
| 单例 | 全局唯一实例 | "有且只有一个" | `@Scope("singleton")`（默认） |
| 工厂 | 不直接 new，通过工厂创建 | "给我一个产品" | `BeanFactory` / `ApplicationContext` |
| 策略 | 可互换的算法族 | "换个玩法" | `AuthenticationProvider` / 事务管理器 |
| 观察者 | 一对多通知 | "有消息通知大家" | `ApplicationEvent` / `@EventListener` |
| 依赖注入 | 外部注入依赖 | "别自己找，我给你" | Spring 核心：构造器注入 |

---

## 100.7 小结

| 知识点 | 核心内容 |
|--------|----------|
| 单例 | 饿汉式 / 双重检查锁 / 枚举 — Spring Bean 默认单例 |
| 工厂 | 解耦创建逻辑 — `BeanFactory` 就是超级工厂 |
| 策略 | 可替换算法族 — Spring 中用 Map<String, Strategy> 自动注入 |
| 观察者 | 一对多通知 — Spring Event + `@EventListener` |
| 依赖注入 | 构造器注入 > Setter 注入 > 字段注入 |

---

## 100.8 自测题

**1. Spring Bean 默认的作用域是什么？如果你想让每次 `@Autowired` 获取的都是新实例，该用什么注解？**

**2. 以下代码使用了哪种设计模式？它有什么好处？**

```java
@Service
@RequiredArgsConstructor
public class ReportExporter {
    private final Map<String, ReportStrategy> strategies;

    public void export(String format, Report report) {
        strategies.get(format).export(report);
    }
}
```

**3. Spring Event 的 `@EventListener` 和传统的 Observer 模式有什么关系？为什么说 Spring Event 更强大？**

---

**答案提示**：1→默认单例（singleton）。需要新实例用 `@Scope("prototype")`。2→策略模式。好处：新增导出格式（PDF/Excel/Word）只需新增一个 `@Component` 类，不需要修改 `ReportExporter`。3→Spring Event 是观察者模式的现代化实现。更强大在于：① 支持 `@Async` 异步通知；② 支持 `@TransactionalEventListener` 事务提交后才通知；③ 事件类可以继承，监听者可以按父类监听。下一章——SOLID 原则。