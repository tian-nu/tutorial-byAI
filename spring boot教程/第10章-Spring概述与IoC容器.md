# 第10章：Spring概述与IoC容器

## 本章目标

学完本章你将能够：

- 勾勒Spring生态全景图，理解Spring Framework、Spring Boot、Spring Cloud等组件的关系
- 深刻理解IoC（控制反转）的设计哲学，从"自己new对象"到"容器管理一切"完成思维转变
- 对比三种DI（依赖注入）方式，掌握构造器注入的基本实践
- 理解Spring容器的层级结构（BeanFactory → ApplicationContext）
- 熟练运用注解式Bean管理（@Component/@Service/@Repository/@Controller）
- 处理同类型多Bean的歧义、解决循环依赖、理解Bean生命周期
- **完成EMS v3的依赖管理部分**：用Spring IoC取代手动new对象

---

## 10.1 Spring生态全景

### 10.1.1 Spring是什么？

如果你问一个Java开发者"Spring是什么"，你可能会得到十种不同的答案。这是因为**Spring已经从最初一个轻量级IoC容器，发展成了覆盖Java开发全领域的庞大生态系统**。

但无论生态多庞大，一切都始于一个核心：**Spring Framework**。本章要学的IoC和AOP，就是这个核心最基础的两个支柱。花时间理解它们，后面所有的Spring产品（Spring Boot、Spring Cloud、Spring Security……）你都会觉得"原来如此"。

```text
                        ┌─────────────────────────────────────┐
                        │         Spring 生态系统              │
                        │    (Java企业级开发事实标准)           │
                        └─────────────────────────────────────┘
                                        │
          ┌──────────┬────────┬─────────┼─────────┬──────────┬──────────┐
          │          │        │         │         │          │          │
          ▼          ▼        ▼         ▼         ▼          ▼          ▼
    ┌──────────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────────┐ ┌──────────┐
    │  Spring  │ │Spring│ │Spring│ │Spring│ │Spring│ │ Spring   │ │ Spring   │
    │Framework │ │ Boot │ │Cloud │ │Security│ │Data │ │ Session  │ │  Batch   │
    │  (核心)   │ │(脚手架)│ │(微服务)│ │(安全) │ │(数据)│ │(分布式会话)│ │ (批处理)  │
    └──────────┘ └──────┘ └──────┘ └──────┘ └──────┘ └──────────┘ └──────────┘
          │                                                                    
    ┌─────┴────────────────────────────────────────────┐
    │    Spring Framework 核心模块                      │
    │  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌───────┐  │
    │  │ IoC  │ │ AOP  │ │ MVC  │ │ JDBC │ │  TX   │  │
    │  │ 容器  │ │ 切面  │ │ Web  │ │ 数据  │ │ 事务  │  │
    │  └──────┘ └──────┘ └──────┘ └──────┘ └───────┘  │
    └──────────────────────────────────────────────────┘
```

### 10.1.2 Spring Framework vs Spring Boot — 你必须先搞清楚的关系

很多初学者会困惑："我应该学Spring Framework还是Spring Boot？" 答案是：**先学Spring Framework（就是本章和第11-12章），再学Spring Boot（第15章起）。**

用一句话说清楚它们的关系：

> **Spring Framework是地基和框架结构，Spring Boot是精装修拎包入住。**

| 对比维度 | Spring Framework | Spring Boot |
|----------|-----------------|-------------|
| **定位** | 底层框架，提供IoC/AOP/MVC等基础能力 | 脚手架，对Spring Framework进行封装和自动化配置 |
| **配置方式** | 需手动编写大量配置（XML或Java Config） | 约定优于配置，零XML，自动配置 |
| **启动方式** | 需部署到外部Tomcat等Servlet容器 | 内嵌Tomcat/Jetty/Undertow，java -jar直接启动 |
| **依赖管理** | 手动引入每个依赖，版本需自行管理 | Starter起步依赖，版本由spring-boot-dependencies统一管控 |
| **类比** | 发动机和变速箱（核心动力总成） | 整车（拧钥匙就走） |

**正确的学习路径**：先理解Spring Framework的IoC和AOP（第10-12章），搞清楚"轮子"怎么转的，到第15章再让Spring Boot帮你"自动挂挡"。否则出了问题你都不知道是引擎坏了还是变速箱坏了。

### 10.1.3 Spring生态各组件速览

| 组件 | 一句话描述 | 你将在本书何处学习 |
|------|-----------|-------------------|
| **Spring Framework** | IoC + AOP + MVC + 数据访问 + 事务管理的基石 | 第10-12章（就是本章到12章！） |
| **Spring Boot** | 自动配置 + 起步依赖 + 内嵌服务器，让Spring开发快10倍 | 第15-20章 |
| **Spring MVC** | 基于Servlet的Web框架，DispatcherServlet统一调度 | 第12章（Spring Framework模块之一） |
| **Spring Data** | 统一数据访问抽象，包含JPA/MongoDB/Redis/Elasticsearch等 | 第13章(MyBatis)/第14章(JPA)/第25章(Redis) |
| **Spring Security** | 认证与授权框架，拦截请求、验证身份、控制权限 | 第23-24章 |
| **Spring Cloud** | 微服务全家桶（服务发现、配置中心、网关、负载均衡） | 第27章入门 |
| **Spring Batch** | 批处理框架，处理大量数据的批量任务 | 不在本书范围（但掌握前27章后自学会很快） |

---

## 10.2 IoC核心思想 — 本章的灵魂

IoC（Inversion of Control，控制反转）是Spring Framework的**第一性原理**。如果你只能从这一章带走一件事，那就是这个。

### 10.2.1 从一碗泡面理解IoC

想象两种吃泡面的方式：

- **方式一（自己控制一切）**：你去超市买面饼、调料包、蔬菜包 → 回家烧水 → 撕包装 → 泡三分钟 → 吃。你控制了整个过程的每一个步骤。
- **方式二（反转控制）**：你去便利店，对店员说"来碗泡面" → 店员帮你泡好递给你 → 吃。你把"如何泡面"的控制权交给了店员。

**IoC就是"方式二"**：你不再自己创建和管理依赖对象，而是告诉容器"我需要什么"，容器帮你准备好并注入给你。控制权从"你"反转到了"容器"。

### 10.2.2 代码三阶段演进：从地狱到天堂

这是理解IoC最重要的部分。我们用同一个需求（UserService调用UserDao保存用户）来展示三种写法的演进。

#### 阶段一：自己new对象 — 硬编码地狱

```java
// ========== UserDao接口 ==========
public interface UserDao {
    void save(String username);
}

// ========== UserDao实现（MySQL版）==========
public class UserDaoImpl implements UserDao {
    @Override
    public void save(String username) {
        System.out.println("MySQL: 保存用户 " + username);
    }
}

// ========== UserService（问题所在）==========
public class UserService {
    // 问题：UserService直接把实现类写死了！
    private UserDao userDao = new UserDaoImpl();

    public void register(String username) {
        System.out.println("开始注册用户: " + username);
        userDao.save(username);
        System.out.println("注册完成");
    }
}

// ========== 主程序 ==========
public class Main {
    public static void main(String[] args) {
        UserService userService = new UserService();
        userService.register("张三");
    }
}
```

**这段代码有什么问题？**

1. **强耦合**：UserService直接依赖了`new UserDaoImpl()`。如果将来要换成Oracle数据库实现（`UserDaoOracleImpl`），必须修改UserService的源代码。
2. **难以测试**：写单元测试时，你无法用Mock对象替代`UserDaoImpl`，因为它在构造函数里直接被new出来了。
3. **不可配置**：想切换实现只能改代码、重新编译、重新部署。

> 这就是**"面向实现编程"**的典型症状。在第4章我们学过多态——你应该"面向接口编程"，但这里虽然定义了接口UserDao，实际上还是被`new UserDaoImpl()`锁死了。

#### 阶段二：工厂模式 — 部分解耦但工厂自身膨胀

很多人会想到用工厂模式来解决：

```java
// ========== 工厂类 ==========
public class BeanFactory {
    public static UserDao getUserDao() {
        // 可以通过配置文件来动态决定返回哪个实现
        String implClass = readConfig("dao.impl.class");
        if ("oracle".equals(implClass)) {
            return new UserDaoOracleImpl();
        }
        return new UserDaoImpl();  // 默认返回MySQL版
    }

    public static UserService getUserService() {
        UserService service = new UserService();
        service.setUserDao(getUserDao());  // 工厂负责"装配"
        return service;
    }

    private static String readConfig(String key) {
        // 从配置文件读取（简化演示）
        return System.getProperty(key, "mysql");
    }
}

// ========== UserService（改进版）==========
public class UserService {
    private UserDao userDao;  // 不再写死！

    public void setUserDao(UserDao userDao) {
        this.userDao = userDao;
    }

    public void register(String username) {
        System.out.println("开始注册用户: " + username);
        userDao.save(username);
        System.out.println("注册完成");
    }
}

// ========== 主程序 ==========
public class Main {
    public static void main(String[] args) {
        // UserService不再自己new UserDao，而是从工厂拿！
        UserService userService = BeanFactory.getUserService();
        userService.register("张三");
    }
}
```

**进步在哪？**
- UserService不再依赖具体实现类，只依赖接口UserDao
- 可以通过配置切换不同的实现（`-Ddao.impl.class=oracle`）

**但工厂模式仍然不够完美：**
1. 随着项目变大，工厂类会膨胀成"超级工厂"——你需要为每个Bean写一对get方法
2. 工厂类本身变成了**新的耦合点**（所有类都依赖工厂）
3. 工厂不管理Bean的生命周期、作用域

#### 阶段三：Spring IoC — 优雅的解耦

```java
// ========== UserDao实现（加@Component注解）==========
import org.springframework.stereotype.Repository;

@Repository  // 告诉Spring："我是一个DAO组件，请管理我"
public class UserDaoImpl implements UserDao {
    @Override
    public void save(String username) {
        System.out.println("MySQL: 保存用户 " + username);
    }
}

// ========== UserService（加@Service + @Autowired）==========
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

@Service  // 告诉Spring："我是一个Service组件，请管理我"
public class UserService {
    
    @Autowired  // 告诉Spring："我需要一个UserDao，请帮我注入"
    private UserDao userDao;

    public void register(String username) {
        System.out.println("开始注册用户: " + username);
        userDao.save(username);
        System.out.println("注册完成");
    }
}

// ========== Spring配置类 ==========
import org.springframework.context.annotation.ComponentScan;
import org.springframework.context.annotation.Configuration;

@Configuration
@ComponentScan("com.example")  // 扫描com.example包下的所有组件
public class AppConfig {
}

// ========== 主程序 ==========
import org.springframework.context.ApplicationContext;
import org.springframework.context.annotation.AnnotationConfigApplicationContext;

public class Main {
    public static void main(String[] args) {
        // 创建Spring容器（IoC容器）
        ApplicationContext context = 
            new AnnotationConfigApplicationContext(AppConfig.class);

        // 从容器中"拿"Bean，而不是"new"
        UserService userService = context.getBean(UserService.class);
        userService.register("张三");
    }
}
```

**Spring IoC做了什么？**
1. 我们不再`new`任何对象了——只通过注解告诉Spring需要什么
2. Spring扫描`@ComponentScan`指定的包，发现所有`@Component/@Service/@Repository`类
3. Spring创建这些类的实例并放入IoC容器
4. Spring发现有`@Autowired`注解的地方，自动从容器中找到匹配的Bean注入进去
5. UserService根本不知道`UserDao`的实现类是谁——只有容器知道

> 这就是IoC的核心：**对象的创建、装配、生命周期的控制权，从程序员反转给了Spring容器。**

### 10.2.3 IoC三大终极问题

面试官喜欢问三个问题来检验你是否真懂了IoC：

**Q1：谁控制谁？**

> **Spring IoC容器**控制了**业务对象**。传统方式是你写`new UserDaoImpl()`直接创建，现在是Spring容器创建和管理所有Bean。

**Q2：反转了什么？**

> 反转了**获取依赖的方式**。传统方式是你主动去获取（"我去超市买面饼"），IoC是容器主动注入给你（"店员递给你泡好的面"）。具体来说：原来`userDao = new UserDaoImpl()`是主动创建，现在是`@Autowired UserDao userDao`等待注入。

**Q3：为什么要反转？**

> **解耦、解耦、还是解耦。** UserService从依赖于具体实现`UserDaoImpl`变成依赖于接口`UserDao`，两者之间唯一的连接点是容器。换实现类只需要换一个注解，UserService的代码纹丝不动。

### 10.2.4 DI（依赖注入）是IoC的实现方式

**IoC和DI不是同一个概念。** 它们的关系是：

> **IoC（控制反转）是一种设计思想，DI（依赖注入）是IoC的一种具体实现方式。**

IoC还可以通过其他方式实现：
- **依赖查找（Dependency Lookup）**：主动向容器索要（`context.getBean(UserDao.class)`），老式EJB用的是这种方式
- **依赖注入（Dependency Injection）**：被动接收容器推送的依赖（`@Autowired UserDao userDao`），Spring主要用它

Spring中DI有三种具体注入方式，这是下一节的重点。

> 🚨 **坑点：IoC不是银弹！简单对象直接new就好。**
>
> ```java
> // ✅ 合理：转移给Spring管理
> @Service
> public class OrderService {
>     @Autowired
>     private OrderDao orderDao;     // Dao需要Spring管理
>     @Autowired
>     private PaymentService paySvc;  // 业务依赖需要Spring管理
> }
>
> // ✅ 合理：简单数据对象自己new
> public Order createOrder() {
>     Order order = new Order();      // Order是简单的POJO，new就好
>     order.setOrderNo(generateNo()); // 不要也交给Spring管理！
>     return order;
> }
>
> // ❌ 过度：把一切交给Spring
> @Component
> public class Order {  // 实体类也交给Spring？完全没必要！
>     private String orderNo;
>     // ...
> }
> ```
>
> **原则**：有业务行为的类（Service、Dao、Controller）交给Spring，纯数据对象（Entity、DTO、VO）直接new。

---

## 10.3 三种DI注入方式

Spring提供了三种依赖注入方式，各有优劣。

### 10.3.1 构造器注入（⭐⭐⭐ 强烈推荐）

```java
@Service
public class OrderService {
    
    private final OrderDao orderDao;        // final：一旦注入，不可变
    private final PaymentService paymentService;

    // 构造器注入：依赖通过构造函数传入
    public OrderService(OrderDao orderDao, PaymentService paymentService) {
        this.orderDao = orderDao;
        this.paymentService = paymentService;
    }

    public void createOrder(Order order) {
        orderDao.insert(order);
        paymentService.pay(order);
    }
}
```

**为什么推荐构造器注入？**

1. **依赖不可变**：字段声明为`final`，一旦通过构造函数赋值后绝对不会变。这消除了运行时依赖被意外修改的风险。
2. **保证不为null**：构造函数执行时Spring必须提供所有参数，否则容器启动就报错。杜绝了NPE隐患。
3. **完全初始化**：对象创建完毕时所有依赖已经就位，不会出现"对象已经可以用但某个依赖还是null"的半初始化状态。
4. **测试友好**：单元测试时直接new并传入Mock对象即可，无需Spring容器。
5. **Spring官方推荐**：从Spring Framework 4.3开始，如果只有一个构造器，`@Autowired`都可以省略。

```java
// 测试时不需要启动Spring，直接new传Mock
@Test
void testCreateOrder() {
    OrderDao mockDao = mock(OrderDao.class);
    PaymentService mockPay = mock(PaymentService.class);
    
    OrderService service = new OrderService(mockDao, mockPay);  // 干净！
    service.createOrder(new Order());
    
    verify(mockDao).insert(any());
}
```

> **注意**：从Spring 4.3开始，如果一个类只有一个构造器，即使不写`@Autowired`，Spring也会自动使用这个构造器注入。当然，为了代码可读性，建议还是加上。

### 10.3.2 Setter注入（⭐⭐ 次选）

```java
@Service
public class OrderService {
    
    private OrderDao orderDao;        // 不能声明为final
    private PaymentService paymentService;

    @Autowired
    public void setOrderDao(OrderDao orderDao) {
        this.orderDao = orderDao;
    }

    @Autowired
    public void setPaymentService(PaymentService paymentService) {
        this.paymentService = paymentService;
    }
}
```

**适用场景**：
- 依赖是**可选的**（没有这个依赖对象也能工作）
- 需要在运行时重新配置依赖（极少见）

**缺点**：
- 依赖不能声明为`final`，可能被意外修改
- 对象创建后可能处于"未完全初始化"状态
- 相比构造器注入，需要更多的样板代码

### 10.3.3 字段注入 @Autowired（⭐ 方便但不推荐）

```java
@Service
public class OrderService {
    
    @Autowired
    private OrderDao orderDao;          // 直接字段注入

    @Autowired
    private PaymentService paymentService;
}
```

这是最常见的写法（尤其是网上教程），因为写起来最快——几个注解就搞定。但这也是问题最多的写法。

> 🚨 **坑点：字段注入让单元测试无法Mock！**
>
> ```java
> @Test
> void testWithFieldInjection() {
>     OrderService service = new OrderService();  // new出来的！
>     // service.orderDao 是null！因为new出来的对象不在Spring容器中
>     // @Autowired不会生效！
>     
>     // 你没有办法把Mock的orderDao"塞"进去，因为它是private字段
>     // 解决方案1：用反射暴力设置（丑陋）
>     // 解决方案2：启动整个Spring容器（慢）
>     // 解决方案3：用Mockito的@InjectMocks（本质上也是反射）
> }
> ```
>
> IDEA也会直接给你警告：**"Field injection is not recommended"**。这不是空穴来风。

### 10.3.4 三种注入方式对比总表

| 对比维度 | 构造器注入 | Setter注入 | 字段注入(@Autowired) |
|----------|-----------|-----------|---------------------|
| **推荐度** | ⭐⭐⭐ 强烈推荐 | ⭐⭐ 特定场景 | ⭐ 不推荐 |
| **依赖不可变性** | ✅ 可声明final | ❌ 不可final | ❌ 不可final |
| **非空保证** | ✅ 编译期+启动期双重保证 | ❌ 可能为null | ❌ 可能为null |
| **测试友好度** | ✅ 直接用构造函数传参 | ✅ 直接调setter传参 | ❌ 需要反射或Spring容器 |
| **代码简洁度** | 依赖多时构造函数膨胀 | 每个依赖一个setter | 最简洁 |
| **循环依赖** | ❌ 启动时直接报错 | ⚠ 可能"瞒过去" | ⚠ 可能"瞒过去" |
| **IDE警告** | 无 | 无 | ⚠ "Field injection not recommended" |
| **适用场景** | 必需的依赖 | 可选的依赖 | ~~遗留代码~~ |

### 10.3.5 循环依赖：A→B→A的死锁困境

这是DI中最经典的坑，没有之一。

```java
@Service
public class ServiceA {
    @Autowired
    private ServiceB serviceB;  // A依赖B
}

@Service
public class ServiceB {
    @Autowired
    private ServiceA serviceA;  // B依赖A  →  循环依赖！
}
```

**不同注入方式的表现**：

| 注入方式 | 行为 | 严重程度 |
|----------|------|---------|
| **构造器注入** | 启动时立即抛出 `BeanCurrentlyInCreationException` | ✅ 暴露问题 |
| **字段注入 / Setter注入** | 可能"正常"启动（Spring通过三级缓存解决singleton的循环依赖） | ⚠ 隐藏了设计问题 |

> 🚨 **坑点：字段注入允许循环依赖"静默通过"，但这不代表没问题！**
>
> Spring的三级缓存机制确实可以解决**singleton** Bean的**setter/字段注入**循环依赖：
> 1. ServiceA实例化（刚创建，未注入属性）
> 2. 发现需要注入ServiceB → 去创建ServiceB
> 3. ServiceB实例化 → 发现需要注入ServiceA → 将"半成品"ServiceA注入给ServiceB
> 4. ServiceB创建完成 → 回到ServiceA，注入完整的ServiceB
>
> 但这只是在"技术层面"绕过了问题。**循环依赖往往是设计缺陷的信号**——你真的需要A依赖B、B又依赖A吗？是不是该抽出一个公共的ServiceC？

**构造函数注入直接暴露问题，是好事！**

```java
@Service
public class ServiceA {
    private final ServiceB serviceB;
    
    public ServiceA(ServiceB serviceB) {  // ← 构造函数注入
        this.serviceB = serviceB;
    }
}

@Service
public class ServiceB {
    private final ServiceA serviceA;
    
    public ServiceB(ServiceA serviceA) {  // ← 构造函数注入
        this.serviceA = serviceA;
    }
}

// 启动直接报错：
// BeanCurrentlyInCreationException: 
//   Error creating bean with name 'serviceA': 
//   Requested bean is currently in creation: 
//   Is there an unresolvable circular reference?
```

**解决方案（按推荐度排序）**：

1. **重新设计（最佳方案）**：分析为什么会产生循环依赖，通常是因为职责划分不清。拆分出一个公共的ServiceC。
2. **@Lazy打破循环**：在其中一个注入点加上`@Lazy`，Spring会先注入一个代理对象，等真正调用时才去获取真实Bean。

```java
@Service
public class ServiceA {
    private final ServiceB serviceB;
    
    public ServiceA(@Lazy ServiceB serviceB) {  // @Lazy打破循环
        this.serviceB = serviceB;
    }
}
```

---

## 10.4 Spring容器深度解析

### 10.4.1 BeanFactory — 最底层的容器

`BeanFactory`是Spring IoC容器最底层的接口，提供了最基本的Bean管理能力：

- `getBean(String name)`：按名称获取Bean
- `containsBean(String name)`：判断是否包含Bean
- `isSingleton(String name)`：判断是否单例

**最大的特点：延迟加载（Lazy Initialization）。** BeanFactory在`getBean()`被调用时才创建Bean实例。

```java
BeanFactory factory = new DefaultListableBeanFactory();
// ... 读取配置 ...
// 此时还没有创建任何Bean！

UserService service = factory.getBean(UserService.class);
// getBean时才真正创建UserService实例
```

**BeanFactory几乎不会在应用代码中直接使用**，它更多是作为Spring内部的基础设施存在。了解它存在即可。

### 10.4.2 ApplicationContext — 你实际使用的容器

`ApplicationContext`是`BeanFactory`的子接口，提供了企业级功能。我们平时说的"Spring容器"，指的就是`ApplicationContext`。

| 特性 | BeanFactory | ApplicationContext |
|------|------------|-------------------|
| Bean实例化时机 | 延迟（getBean时） | **预初始化**（启动时创建所有singleton） |
| 国际化（MessageSource） | ❌ | ✅ |
| 事件发布 | ❌ | ✅ ApplicationEvent |
| 资源加载 | 手动 | ✅ ResourceLoader |
| 环境与Profile | ❌ | ✅ Environment |
| AOP集成 | 需手动 | ✅ 自动 |

**常见的ApplicationContext实现**：

```java
// 1. 基于注解（现代Spring项目标准）
ApplicationContext ctx = 
    new AnnotationConfigApplicationContext(AppConfig.class);

// 2. 基于XML（遗留项目）
ApplicationContext ctx = 
    new ClassPathXmlApplicationContext("applicationContext.xml");

// 3. 基于文件系统路径的XML
ApplicationContext ctx = 
    new FileSystemXmlApplicationContext("/path/to/applicationContext.xml");
```

> 🚨 **坑点：ApplicationContext启动慢？检查@PostConstruct中的代码！**
>
> `ApplicationContext`在启动时会预初始化所有singleton Bean。如果你在某个Bean的`@PostConstruct`方法或`InitializingBean.afterPropertiesSet()`中写了耗时操作（如网络请求、大文件加载、数据库全量查询），容器启动就会特别慢。
>
> 这些耗时操作应该放到**第一次使用时**做懒加载，而不是在Bean初始化时。

---

## 10.5 Bean配置方式演进

Spring的Bean配置方式经历了三个时代：XML → 注解 → Java Config。我们快速过一遍，把重点放在现代主流方式上。

### 10.5.1 XML方式（了解即可）

这是Spring 1.x/2.x时代的配置方式，现在**新项目基本不用**，但在维护老项目时会遇到。

```xml
<?xml version="1.0" encoding="UTF-8"?>
<beans xmlns="http://www.springframework.org/schema/beans"
       xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
       xsi:schemaLocation="http://www.springframework.org/schema/beans
       http://www.springframework.org/schema/beans/spring-beans.xsd">

    <!-- 定义一个Bean -->
    <bean id="userDao" class="com.example.dao.UserDaoImpl" />

    <!-- 定义另一个Bean，通过setter注入依赖 -->
    <bean id="userService" class="com.example.service.UserService">
        <property name="userDao" ref="userDao" />
    </bean>

</beans>
```

XML方式的问题是显而易见的：
- 一个Java类就要配一段XML，项目一大XML文件就成灾难
- XML中写Java类名，IDE不能自动重构
- 排查问题时要在XML和Java之间反复横跳

### 10.5.2 注解方式（现代主流）

Spring提供了四个功能完全一样的注解，仅仅为了**语义区分**：

| 注解 | 语义（推荐的层） | 额外能力 |
|------|----------------|---------|
| `@Component` | 通用组件（不确定属于哪层时用） | 无 |
| `@Service` | 业务逻辑层 | 无 |
| `@Repository` | 数据访问层 | **自动翻译数据库异常为Spring的DataAccessException** |
| `@Controller` | Web控制层 | Spring MVC识别（第12章详述） |

> **为什么功能一样还要分四个？**
>
> 1. 代码可读性：`@Service`一看就知道是业务层
> 2. AOP切面：可以通过`@within(org.springframework.stereotype.Service)`精确切到所有Service层方法
> 3. 工具支持：IDE和监控工具可以按注解类型分类展示

`@Repository`独有的数据库异常翻译：

```java
@Repository
public class UserDaoImpl implements UserDao {
    @Autowired
    private JdbcTemplate jdbcTemplate;
    
    @Override
    public User findById(Long id) {
        // 如果数据库连接断了，JDBC驱动会抛出SQLException
        // Spring自动将SQLException翻译为DataAccessException体系中的具体异常
        // 比如 CannotGetJdbcConnectionException
        return jdbcTemplate.queryForObject("SELECT * FROM user WHERE id = ?", 
                new BeanPropertyRowMapper<>(User.class), id);
    }
}
```

如果没有`@Repository`（比如用了`@Component`），异常就不会被自动翻译，你需要自己处理`SQLException`。这就是`@Repository`的独特价值。

### 10.5.3 @ComponentScan — 告诉Spring去哪找Bean

```java
@Configuration
@ComponentScan("com.example")  // 扫描com.example包及其所有子包
public class AppConfig {
}
```

> 🚨 **坑点1：扫描路径太大 → 启动慢**
>
> 如果配置`@ComponentScan("com")`，Spring会扫描整个classpath下所有`com`开头的包……启动时间可能从1秒变成30秒。
>
> **正确做法**：精确到项目的根包，如`@ComponentScan("com.ems")`。

> 🚨 **坑点2：@ComponentScan自己写会覆盖默认扫描**
>
> 在第15章我们会学到`@SpringBootApplication`，它内部已经包含了`@ComponentScan`（默认扫描启动类所在包及子包）。如果你在启动类上又自己写了`@ComponentScan`，**你的会覆盖默认的**，导致默认扫描失效。记住：**除非需要非默认行为，否则不需要手动加@ComponentScan。**

---

## 10.6 @Autowired详解

### 10.6.1 默认按类型注入（byType）

```java
@Autowired
private UserDao userDao;  // Spring在容器中找"类型为UserDao的Bean"
```

Spring的匹配逻辑是：
1. 按类型（byType）查找所有匹配的Bean
2. 如果只有一个匹配 → 直接注入
3. 如果有多个匹配 → 按名称（byName）尝试精确匹配
4. 如果仍无法确定 → 抛出异常

### 10.6.2 同类型多Bean的解决方案

当UserDao有多个实现时（比如`UserDaoMysqlImpl`和`UserDaoOracleImpl`），`@Autowired`会报错。

> 🚨 **坑点：同类型多个Bean时@Autowired直接报错！**
>
> ```
> NoUniqueBeanDefinitionException: 
> No qualifying bean of type 'com.example.dao.UserDao' available: 
> expected single matching bean but found 2: userDaoMysqlImpl, userDaoOracleImpl
> ```

**解决方案1：@Qualifier指定Bean名称**

```java
@Repository("mysqlDao")  // 给Bean起个名字
public class UserDaoMysqlImpl implements UserDao { ... }

@Service
public class UserService {
    @Autowired
    @Qualifier("mysqlDao")  // 指定注入名为mysqlDao的Bean
    private UserDao userDao;
}
```

**解决方案2：@Primary标记首选Bean**

```java
@Repository
@Primary  // 标记为"首选"：当有多个同类型Bean时，优先选我
public class UserDaoMysqlImpl implements UserDao { ... }

@Service
public class UserService {
    @Autowired
    private UserDao userDao;  // 自动注入标记了@Primary的
}
```

**解决方案3：@Resource（JSR-250标准注解）**

`@Resource`是Java标准注解（`jakarta.annotation.Resource`），不是Spring特有的。它与`@Autowired`的核心区别：

| 对比维度 | @Autowired (Spring) | @Resource (JSR-250) |
|----------|---------------------|---------------------|
| **默认匹配方式** | 按类型（byType） | 按名称（byName） |
| **可指定名称** | @Qualifier配合 | name属性 |
| **是否Spring特有** | 是 | 否（Java标准，可跨框架） |
| **required属性** | 有（默认true） | 无（找不到就null） |

```java
@Service
public class UserService {
    @Resource(name = "mysqlDao")  // 直接按名称指定
    private UserDao userDao;
}
```

### 10.6.3 @Autowired的required属性

```java
@Autowired(required = false)  // 如果容器中没有UserDao类型的Bean，也不会报错
private UserDao userDao;      // 此时userDao为null
```

适用于可选依赖的场景：有就用，没有也能正常工作。

---

## 10.7 Bean作用域

### 10.7.1 singleton（默认）

**整个Spring IoC容器中，该Bean只有一个实例。** 无论调用多少次`getBean()`，返回的都是同一个对象。

```java
@Component
// 默认就是@Scope("singleton")，不需要显式声明
public class Counter {
    private int count = 0;
    
    public int increment() {
        return ++count;
    }
}

// 测试
Counter c1 = context.getBean(Counter.class);
Counter c2 = context.getBean(Counter.class);

System.out.println(c1 == c2);        // true  → 同一个对象
System.out.println(c1.increment());  // 1
System.out.println(c2.increment());  // 2  → c1和c2是同一个，count=2
```

> **注意**：Singleton在**整个Spring容器范围内**是单例的，不是JVM级别的。如果你创建了两个ApplicationContext，它们各自有一个Counter实例。

### 10.7.2 prototype

**每次`getBean()`都创建一个新实例。**

```java
@Component
@Scope("prototype")  // prototype：每次获取都创建新实例
public class PrototypeBean {
    private int value;
    // ...
}
```

### 10.7.3 ⚠️ prototype注入到singleton的"失效"问题

> 🚨 **坑点：把prototype注入到singleton中，prototype会"失效"！**

这是一个极具迷惑性的问题。看以下代码：

```java
@Component
@Scope("prototype")
public class PrototypeBean {
    private final String id = java.util.UUID.randomUUID().toString();
    
    public String getId() {
        return id;
    }
}

@Component
public class SingletonService {
    @Autowired
    private PrototypeBean prototypeBean;  // 注入prototype
    
    public String getProtoId() {
        return prototypeBean.getId();
    }
}

// 测试代码
SingletonService service1 = context.getBean(SingletonService.class);
SingletonService service2 = context.getBean(SingletonService.class);

System.out.println(service1.getProtoId());  // 输出: abc-123
System.out.println(service2.getProtoId());  // 输出: abc-123  ← 跟上面一样！
// 你可能期望每次获取SingletonService时，它内部的prototypeBean都是新的
// 但实际不是！因为SingletonService只被创建了一次，
// 它的prototypeBean属性也只被注入了一次！
```

**为什么？**
- `SingletonService`是singleton，只在容器启动时创建一次
- 创建`SingletonService`时，Spring需要注入它的依赖`PrototypeBean`
- 于是创建了一个`PrototypeBean`实例并注入
- 之后不管多少次调用`getBean(SingletonService.class)`，返回的都是同一个`SingletonService`，它内部的`prototypeBean`字段始终指向**第一次注入的那个**实例

用hashCode验证更直观：

```java
@Component
public class SingletonService {
    @Autowired
    private PrototypeBean prototypeBean;
    
    public void show() {
        System.out.println("SingletonService的hashCode: " + this.hashCode());
        System.out.println("PrototypeBean的hashCode:   " + prototypeBean.hashCode());
    }
}

// 连续调用三次
SingletonService s1 = context.getBean(SingletonService.class);
s1.show();
// SingletonService的hashCode: 1234567
// PrototypeBean的hashCode:   7654321

SingletonService s2 = context.getBean(SingletonService.class);
s2.show();
// SingletonService的hashCode: 1234567  ← 同一个SingletonService（同hashCode）
// PrototypeBean的hashCode:   7654321  ← 同一个PrototypeBean！（同hashCode）
// ↑ prototype"失效"了！
```

**解决方案1：@Lookup注解（推荐）**

```java
@Component
public abstract class SingletonService {  // 注意：变成了abstract！
    
    public String getProtoId() {
        return getPrototypeBean().getId();  // 每次调用getPrototypeBean()都获取新实例
    }
    
    @Lookup  // Spring通过CGLIB生成子类，覆盖此方法，每次返回新的prototype实例
    public abstract PrototypeBean getPrototypeBean();
}
```

**解决方案2：ApplicationContext.getBean()**

```java
@Component
public class SingletonService {
    @Autowired
    private ApplicationContext context;
    
    public String getProtoId() {
        PrototypeBean proto = context.getBean(PrototypeBean.class);  // 每次手动获取
        return proto.getId();
    }
}
```

但这让代码依赖了Spring容器本身，不够优雅。`@Lookup`是更推荐的做法。

---

## 10.8 @Configuration与@Bean

### 10.8.1 为什么需要@Bean？

当你需要管理的类**不是你自己写的**（比如第三方库中的类），你不能去别人代码里加`@Component`注解。这时就需要在配置类中用`@Bean`方法手动创建。

```java
@Configuration
public class AppConfig {
    
    @Bean  // 将该方法的返回值注册为一个Spring Bean
    public DataSource dataSource() {
        DruidDataSource ds = new DruidDataSource();
        ds.setUrl("jdbc:mysql://localhost:3306/ems");
        ds.setUsername("root");
        ds.setPassword("123456");
        ds.setMaxActive(20);
        return ds;
    }
    
    @Bean
    public JdbcTemplate jdbcTemplate(DataSource dataSource) {
        // 方法的参数DataSource会被Spring自动注入
        return new JdbcTemplate(dataSource);
    }
}
```

### 10.8.2 @Configuration的CGLIB代理机制

> 🚨 **坑点：@Configuration中的@Bean方法互相调用——Spring通过CGLIB代理保证单例！**

```java
@Configuration
public class AppConfig {
    
    @Bean
    public DataSource dataSource() {
        return new DruidDataSource();
    }
    
    @Bean
    public JdbcTemplate jdbcTemplate() {
        return new JdbcTemplate(dataSource());  // ← 直接调用另一个@Bean方法！
    }
}
```

你可能会想：`jdbcTemplate()`中直接调`dataSource()`，不会创建两个DataSource吗？

**不会！因为`@Configuration`类会被CGLIB代理。** 当你在一个`@Bean`方法中调用另一个`@Bean`方法时，代理会拦截这次调用，**如果已经创建过该Bean，直接返回已有实例而不是再次执行方法体。**

这就是**Full模式**（`@Configuration`，有CGLIB代理）vs **Lite模式**（`@Component`，无代理）：

```java
// Full模式：@Configuration → CGLIB代理 → @Bean间调用保证单例
@Configuration
public class FullConfig {
    @Bean
    public A a() { return new A(); }
    
    @Bean
    public B b() {
        return new B(a());  // a()被代理拦截，返回的是Spring容器中的单例A
    }
}

// Lite模式：@Component → 无代理 → @Bean间直接调用会创建多个实例！
@Component
public class LiteConfig {
    @Bean
    public A a() { return new A(); }
    
    @Bean
    public B b() {
        return new B(a());  // a()是普通Java方法调用，每次都会new一个新A！
    }
}
```

> **结论**：定义配置类时，请始终使用`@Configuration`而不是`@Component`，除非你确定不需要`@Bean`之间的互相调用。

---

## 10.9 Bean生命周期

Spring Bean从"出生"到"死亡"经历了一个完整的生命周期。理解这个生命周期对排查初始化问题和合理利用扩展点非常重要。

### 10.9.1 完整生命周期图

```text
┌─────────────────────────────────────────────────────────────────────┐
│                       Spring Bean 生命周期                           │
└─────────────────────────────────────────────────────────────────────┘

   ┌──────────┐
   │ 1. 实例化  │  ← 调用构造函数，创建对象（此时属性尚未赋值）
   └─────┬────┘
         ▼
   ┌──────────┐
   │ 2. 属性赋值 │  ← @Autowired / @Value 注入依赖
   └─────┬────┘
         ▼
   ┌──────────────────────────────────────┐
   │         3. 初始化（按顺序）           │
   │                                      │
   │  3.1 BeanNameAware / BeanFactoryAware │ ← 感知容器回调（让Bean获取容器引用）
   │        ↓                              │
   │  3.2 @PostConstruct                   │ ← 推荐！初始化回调
   │        ↓                              │
   │  3.3 InitializingBean.afterPropertiesSet() │ ← 框架接口（耦合，少用）
   │        ↓                              │
   │  3.4 @Bean(initMethod = "init")       │ ← 自定义初始化方法
   │                                      │
   └──────────────────┬───────────────────┘
                      ▼
   ┌──────────┐
   │ 4. 就绪使用 │  ← Bean完全初始化，可以被业务代码使用了
   └─────┬────┘
         ▼
   ┌──────────────────────────────────────┐
   │         5. 销毁（容器关闭时）         │
   │                                      │
   │  5.1 @PreDestroy                     │ ← 推荐！销毁回调
   │        ↓                              │
   │  5.2 DisposableBean.destroy()        │ ← 框架接口（少用）
   │        ↓                              │
   │  5.3 @Bean(destroyMethod = "cleanup")│ ← 自定义销毁方法
   │                                      │
   └──────────────────┬───────────────────┘
                      ▼
              ┌──────────────┐
              │ 6. Bean 已销毁 │
              └──────────────┘
```

### 10.9.2 生命周期完整代码演示

```java
import jakarta.annotation.PostConstruct;
import jakarta.annotation.PreDestroy;
import org.springframework.beans.factory.DisposableBean;
import org.springframework.beans.factory.InitializingBean;
import org.springframework.stereotype.Component;

@Component
public class LifecycleBean implements InitializingBean, DisposableBean {
    
    public LifecycleBean() {
        System.out.println("【1. 实例化】构造函数被调用");
    }
    
    @PostConstruct
    public void postConstruct() {
        System.out.println("【3.2 @PostConstruct】初始化");
    }
    
    @Override
    public void afterPropertiesSet() throws Exception {
        System.out.println("【3.3 InitializingBean】afterPropertiesSet()");
    }
    
    public void customInit() {
        System.out.println("【3.4 自定义init方法】");
    }
    
    public void doWork() {
        System.out.println("【4. 就绪使用】Bean正常工作...");
    }
    
    @PreDestroy
    public void preDestroy() {
        System.out.println("【5.1 @PreDestroy】即将销毁");
    }
    
    @Override
    public void destroy() throws Exception {
        System.out.println("【5.2 DisposableBean】destroy()");
    }
    
    public void customDestroy() {
        System.out.println("【5.3 自定义destroy方法】");
    }
}
```

```java
@Configuration
public class AppConfig {
    
    @Bean(initMethod = "customInit", destroyMethod = "customDestroy")
    public LifecycleBean lifecycleBean() {
        return new LifecycleBean();
    }
}
```

运行输出：

```text
【1. 实例化】构造函数被调用       ← 第一步：new对象
─────────────────────────────────────  ← 第二步：依赖注入（如果有@Autowired）
【3.2 @PostConstruct】初始化       ← 第三步：初始化回调
【3.3 InitializingBean】afterPropertiesSet()
【3.4 自定义init方法】customInit()
─────────────────────────────────────
【4. 就绪使用】Bean正常工作...
─────────────────────────────────────  ← 容器关闭...
【5.1 @PreDestroy】即将销毁
【5.2 DisposableBean】destroy()
【5.3 自定义destroy方法】customDestroy()
```

> **最佳实践**：优先使用`@PostConstruct`和`@PreDestroy`（Jakarta标准注解，不依赖Spring），次选`@Bean`的`initMethod/destroyMethod`属性，少用`InitializingBean/DisposableBean`接口（会让代码和Spring耦合）。

---

## 10.10 本章小结

这一章我们从零开始，深入了Spring Framework最核心的概念——IoC容器。回顾核心收获：

1. **Spring生态全景**：Spring Framework是地基，Spring Boot是精装修，Spring Cloud是城市基础设施。先学地基再上楼，顺序不能乱。
2. **IoC思想的三阶段演进**：
   - 阶段一`new UserDaoImpl()`：硬编码地狱，强耦合
   - 阶段二工厂模式：部分解耦，但工厂自身膨胀
   - 阶段三Spring IoC：完全解耦，容器管理一切
3. **IoC与DI的关系**：IoC是思想（控制反转），DI是手段（依赖注入）。IoC还可以用依赖查找实现。
4. **三种注入方式**：构造器注入（⭐⭐⭐）> Setter注入（⭐⭐，可选依赖）> 字段注入（⭐，测试困难）
5. **Bean容器**：BeanFactory是底层基础，ApplicationContext是企业级容器。现代项目用`AnnotationConfigApplicationContext`。
6. **Bean配置演进**：XML（了解）→ 注解（主流：@Component/@Service/@Repository/@Controller）
7. **@Autowired细节**：默认按类型注入，多Bean时用@Qualifier/@Primary/@Resource解决
8. **作用域陷阱**：prototype注入到singleton中只创建一次，需用@Lookup解决
9. **@Configuration vs @Component**：@Configuration通过CGLIB代理保证@Bean间调用单例
10. **Bean生命周期**：实例化→属性赋值→初始化（@PostConstruct→InitializingBean→initMethod）→就绪→销毁（@PreDestroy→DisposableBean→destroyMethod）

---

## 思考题

1. 以下代码使用了什么注入方式？存在什么问题？

   ```java
   @Service
   public class ReportService {
       @Autowired
       private ReportDao reportDao;
       
       public ReportService(ReportDao reportDao) {
           this.reportDao = reportDao;  // 这一行有用吗？
       }
   }
   ```

2. 以下配置能否正常工作？如果不能，为什么？

   ```java
   @Configuration
   public class DataConfig {
       @Bean
       public DataSource dataSource() {
           return new HikariDataSource();
       }
       
       @Bean
       public JdbcTemplate jdbcTemplate() {
           return new JdbcTemplate(dataSource());
       }
       
       @Bean
       public TransactionTemplate txTemplate() {
           return new TransactionTemplate(txManager());
       }
       
       @Bean
       public PlatformTransactionManager txManager() {
           return new DataSourceTransactionManager(dataSource());
       }
   }
   ```

3. UserService是singleton，它注入了一个prototype的ShoppingCart。用户A和用户B同时调用`userService.getCart()`，他们拿到的是同一个ShoppingCart吗？为什么？如何修复？

4. 为什么构造器注入的循环依赖会在启动时报错而字段注入的不一定报错？（提示：思考Bean创建的步骤顺序）

5. 下面的组件扫描配置有问题吗？

   ```java
   @SpringBootApplication
   @ComponentScan("com.example")  // 项目实际包是 com.ems
   public class Application {
       public static void main(String[] args) {
           SpringApplication.run(Application.class, args);
       }
   }
   ```

---

<details>
<summary>思考题参考答案（点击展开）</summary>

**第1题**：
这是**构造器注入和字段注入的混合使用**，但实际上存在冗余和不明确的问题。

问题分析：
- `@Autowired private ReportDao reportDao;` 是字段注入
- 构造函数中的 `this.reportDao = reportDao;` 实际上**会被字段注入的值覆盖**，因为字段注入发生在构造函数执行之后
- 最终 reportDao 由 @Autowired 字段注入确定，构造函数的赋值是徒劳的

正确的构造器注入写法（移除字段的@Autowired）：

```java
@Service
public class ReportService {
    private final ReportDao reportDao;
    
    // @Autowired 可省略（Spring 4.3+，单构造函数）
    public ReportService(ReportDao reportDao) {
        this.reportDao = reportDao;
    }
}
```

**第2题**：
能正常工作。虽然看起来`dataSource()`被调用了三次（在`jdbcTemplate()`、`txTemplate()`通过`txManager()`间接调用、以及`txManager()`直接调用），但因为`@Configuration`类的CGLIB代理机制，所有对`@Bean`方法的调用都会被拦截：第一次执行方法体创建Bean，之后直接返回已有实例。因此只会创建一个DataSource实例。

**第3题**：
是同一个ShoppingCart。因为UserService是singleton，容器只创建一次UserService实例，在创建时注入ShoppingCart（也只创建一次）。之后不管用户A还是用户B调用`getCart()`，拿到的都是**同一个**ShoppingCart实例。

修复方案（@Lookup）：

```java
@Component
public abstract class UserService {
    
    public ShoppingCart getCart() {
        return createCart();
    }
    
    @Lookup
    public abstract ShoppingCart createCart();
}
```

或者注入ApplicationContext手动获取：

```java
@Component
public class UserService {
    @Autowired
    private ApplicationContext context;
    
    public ShoppingCart getCart() {
        return context.getBean(ShoppingCart.class);
    }
}
```

**第4题**：
构造器注入的循环依赖报错，是因为Bean的创建步骤决定的：

Bean创建步骤：**实例化 → 属性赋值 → 初始化**

- **构造器注入**在"实例化"阶段就需要依赖：创建ServiceA → 需要ServiceB作为构造参数 → 去创建ServiceB → 需要ServiceA作为构造参数 → 去创建ServiceA……此时ServiceA还在创建中（半成品），Spring检测到循环并抛出`BeanCurrentlyInCreationException`
- **字段注入**在"属性赋值"阶段进行：ServiceA实例化（此时还没注入属性，是半成品）→ 把半成品放入三级缓存 → 需要注入ServiceB → 创建ServiceB实例 → 需要注入ServiceA → 从缓存中拿到ServiceA半成品 → 注入到ServiceB → ServiceB创建完成 → 回到ServiceA完成注入

Spring通过三级缓存只支持singleton Bean的setter/字段注入循环依赖。constructor注入因在实例化阶段就无法满足依赖而无法通过缓存解决。

**第5题**：
有问题。`@SpringBootApplication`已经包含了`@ComponentScan`（默认扫描启动类所在包 `com.ems` 及子包），但这里手动添加的 `@ComponentScan("com.example")` 会**覆盖**默认扫描路径。结果Spring只会扫描 `com.example` 包，而项目实际在 `com.ems` 包下 → 所有Bean都不会被扫描到 → 启动虽然不报错，但所有@Autowired注入都会失败。

修复：删除手动添加的`@ComponentScan`，或改为`@ComponentScan("com.ems")`。

</details>

---

> **下一篇预告**：第11章我们将学习Spring的第二大核心——AOP（面向切面编程）。如果说IoC帮你管理对象之间的依赖关系，那么AOP帮你管理散布在各处的横切关注点（日志、事务、权限……）。你会发现`@Transactional`注解的原理就是AOP。
>
> **学习路线提醒**：
> - 第10章（本章）：IoC容器 → 对象的"出生"归Spring管
> - 第11章：AOP → 方法的前后拦截归Spring管
> - 第12章：Spring MVC → HTTP请求的处理归Spring管
>
> 三章学完，你就掌握了Spring Framework的核心三支柱。这也是后续Spring Boot（第15章起）能帮你自动配置一切的基础。