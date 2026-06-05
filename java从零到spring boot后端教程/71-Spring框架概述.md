# 71-Spring框架概述

> 💡 想象你是一个建筑工人。在没有吊车之前，每一块砖，每一袋水泥，你都得自己亲手去搬。今天要砌第17层的墙，你扛着水泥爬了17层——这就是"没有Spring的世界"。有了Spring，你只需要坐在设计图上画线，说"这儿要水泥、那儿要砖头"，材料自动飞到该去的地方。这就是依赖注入。你甚至能在每层楼施工前后自动拍照存档，完全不用改施工流程——这就是AOP。Spring就是建筑工地的自动化系统，让你从搬砖工变成设计师。

---

> ⚠️ 本章是Spring系列的第一章。如果你还没有看过前一章 [70a-RESTful API设计规范](./70a-RESTful%20API设计规范.md)，强烈建议先去看——它讲了HTTP方法和URL设计的通用原则，这些是Spring MVC的基石。

---

## 本章目标
- 理解 Spring 框架解决的核心问题（IoC / DI / AOP）
- 用生活比喻深刻理解控制反转、依赖注入、面向切面编程
- 了解 Spring 发展史与 Spring Boot 的定位
- 明确 Spring Boot 不是你之前学的 Spring 的对立，而是它的"一键启动版"

---

## 71.1 没有 Spring 的世界——泥巴比喻

想象你开一家奶茶店。你卖一杯奶茶，需要：

1. 自己去种茶叶
2. 自己去挤牛奶
3. 自己去烧水
4. 自己搅拌
5. 最后才端给客人

这就是**没有Spring的Java开发**。你的代码里到处是 `new`：

```java
public class TeaShop {
    private TeaMaker teaMaker = new TeaMaker();
    private MilkProvider milkProvider = new MilkProvider();
    private WaterBoiler waterBoiler = new WaterBoiler();

    public void makeTea() {
        Tea tea = teaMaker.make();
        Milk milk = milkProvider.get();
        Water water = waterBoiler.boil();
        // ... 混合、搅拌、出杯
    }
}
```

看起来没问题。但问题来了：

- **换供应商**：绿茶换成红茶，你得改 TeaShop 源码。
- **测试困难**：想单独测"搅拌"这段逻辑，却被迫初始化了整个茶供应链。
- **蔓延失控**：连锁店开100家，TeaMaker 的 new 出现了一百次。
- **耦合紧密**：TeaShop 和 TeaMaker 焊死在一起，改一个必须动另一个。

> 🤔 想多一点：上面的代码违反了面向对象设计中的"依赖倒置原则"——高层模块（TeaShop）不应该依赖低层模块（TeaMaker）的 concrete 实现。它们都该依赖抽象（接口）。但在没有Spring的世界里，即便你定义了接口 `public interface TeaMaker`，你还是得在某处 `new` 一个具体实现——这个 `new` 本身就在写死依赖。

---

## 71.2 IoC ——饭来张口的世界

**IoC（Inversion of Control，控制反转）** 名字唬人，但一句话说清楚：

**以前是你自己造对象（new），现在是别人做好了端给你。**

就像你去餐厅：
- 没有 IoC：你冲进后厨，自己切菜、炒菜、装盘。
- 有 IoC：你坐在餐桌前，喊一声"糖醋排骨"，菜就端上来了。你只管吃，不管做。

Spring 的 IoC 容器就是这个"后厨"。你只需要声明"我需要什么"，Spring 负责创建、组装、递到你手里。你失去了"new 对象"的控制权，但换来了"声明即可得"的自由。

```java
// 反思：TeaShop 不再 new 任何东西，Spring 会自动注入
@Component
public class TeaShop {
    @Autowired
    private TeaMaker teaMaker;  // Spring 给你端上来的
    // ...
}
```

**控制反转的"反转"到底是什么？**

| 传统模式 | IoC 模式 |
|----------|----------|
| 你控制创建什么对象 | Spring 控制创建什么对象 |
| 你控制何时创建 | Spring 控制何时创建 |
| 你控制对象之间的关系 | Spring 控制对象之间的 wiring |
| 你的代码拿回控制权 | 你的代码交出控制权 |

> 字面陷阱："反转"听起来像东西翻了个面，其实它是"控制权的转移"。把 new 这种脏活累活的"控制权"从你的业务代码中移走，交给Spring容器。你失去的是 new 的自由，得到的是专注于业务逻辑的自由。

---

## 71.3 DI ——三种送菜方式

**DI（Dependency Injection，依赖注入）** 是 IoC 的具体实现方式。IoC 说"不用你自己造了"，DI 说"我具体怎么递给你"。

三种方式，对应奶茶店三种送原料的方式：

### 构造器注入（推荐）——建店时就配好供应商

```java
@Component
public class TeaShop {

    private final TeaMaker teaMaker;
    private final MilkProvider milkProvider;

    // Spring 调用这个构造器，把所有依赖传进来
    public TeaShop(TeaMaker teaMaker, MilkProvider milkProvider) {
        this.teaMaker = teaMaker;
        this.milkProvider = milkProvider;
    }
}
```

优势：**对象一旦创建就处于可用状态**，依赖不可变（final），安全、可测试。

### 字段注入（简单但不推荐）——直接从外面伸进来的管子

```java
@Component
public class TeaShop {

    @Autowired
    private TeaMaker teaMaker;  // 直接从外部接进来
}
```

缺陷：依赖藏在类内部，测试时难以Mock；final 无法使用，依赖可能被意外修改；可能导致循环依赖难排查。

### Setter 注入（可选依赖）—— 随时更换供应商

```java
@Component
public class TeaShop {

    private TeaMaker teaMaker;

    @Autowired
    public void setTeaMaker(TeaMaker teaMaker) {
        this.teaMaker = teaMaker;
    }
}
```

适用场景：**可选依赖**——有些依赖不是必须的，可以在运行时更换而不需重建对象。

> 🤔 想多一点：Spring 官方推荐**构造器注入**。理由有三：① 不可变对象线程更安全 ② 避免 NPE——你想不传参都过不了编译 ③ 循环依赖时构造器注入会直接抛错，强迫你重审设计。字段注入是"写起来最爽但埋坑最多"的方式。

---

## 71.4 AOP ——横切关注点的自动化

回到奶茶店。老板要求：

> "记录每一杯奶茶的制作耗时。"

你打算怎么做？在每个奶茶品类里加计时代码？这样：

```java
public void makeBubbleTea() {
    long start = System.currentTimeMillis();
    // ... 制作珍珠奶茶的 20 行代码
    long end = System.currentTimeMillis();
    log.info("耗时：" + (end - start) + "ms");
}

public void makeFruitTea() {
    long start = System.currentTimeMillis();
    // ... 制作水果茶的 20 行代码
    long end = System.currentTimeMillis();
    log.info("耗时：" + (end - start) + "ms");
}
```

两个问题：
1. **重复代码**：每个方法前后各加三行。
2. **关注点污染**：核心逻辑（做茶）被辅助逻辑（计时）搅乱。

AOP 的解法：**计时逻辑独立写成一个"切面"，让它自动切到所有需要计时的业务方法上。**

```java
@Aspect
@Component
public class TimingAspect {

    @Around("execution(* com.teashop.TeaShop.make*())")
    public Object recordTime(ProceedingJoinPoint joinPoint) throws Throwable {
        long start = System.currentTimeMillis();
        Object result = joinPoint.proceed();  // 执行原来的方法
        long end = System.currentTimeMillis();
        System.out.println("耗时：" + (end - start) + "ms");
        return result;
    }
}
```

`makeBubbleTea()` 和 `makeFruitTea()` 里一行计时代码都没有，但计时功能生效了。图景：

```
┌─────────────────────────────────────────┐
│          AOP 切面（计时逻辑）             │
│  ① 记录开始时间                           │
│       ┌──────────────────────┐          │
│       │  业务方法（核心逻辑）  │          │
│       └──────────────────────┘          │
│  ② 记录结束时间，输出耗时                  │
└─────────────────────────────────────────┘
```

AOP 的核心概念表：

| 概念 | 解释 | 比喻 |
|------|------|------|
| 切面（Aspect） | 横切关注点的模块化 | 计时模块本身 |
| 连接点（Join Point） | 可切入的位置 | 每个方法入口和出口 |
| 切点（Pointcut） | 切面实际切到哪些连接点 | `execution(* make*())` ——切到所有 make 开头的方法 |
| 通知（Advice） | 切面的具体逻辑 + 时机 | `@Before`（方法前）、`@After`（方法后）、`@Around`（环绕） |
| 织入（Weaving） | 切面应用到目标对象的过程 | "自动给奶茶机装了计时器" |

---

## 71.5 Spring 发展简史

```
2002  Rod Johnson 出版《Expert One-on-One J2EE Design and Development》
      ↓  指出 EJB 过于笨重，提出轻量级替代方案
2003  发布 infrastructure 代码（Spring 前身）
2004  Spring Framework 1.0 发布（Rod Johnson + Juergen Hoeller）
      ↓  核心：IoC 容器 + AOP
2007  Spring 2.5 引入注解配置（@Autowired、@Component）
2009  Spring 3.0 引入 Java Config、支持 REST
2013  Spring 4.0 全面支持 Java 8
2014  **Spring Boot 1.0 发布** ← 里程碑
      ↓  核心创新：自动配置、嵌入式服务器、Starter
2017  Spring 5.0 响应式编程支持（WebFlux）
2022  Spring Boot 3.0 / Spring 6.0：Jakarta EE 迁移、AOT 编译、虚拟线程
```

> 🤔 想多一点：为什么 Spring Boot 的发明如此重要？因为 Spring Framework 虽然强大，但配置地狱让人崩溃。一个最简单的"Hello World"，在 Spring Framework 年代需要：`web.xml` + `applicationContext.xml` + `dispatcher-servlet.xml` + 至少三个 Maven 依赖。Spring Boot 用一个 `@SpringBootApplication` 干了同样的事。这就是 **约定优于配置**。

---

## 71.6 Spring Boot 定位——约定优于配置

**Spring Boot ≠ 新的框架**。它是 Spring Framework 的"一键启动器"。

| | Spring Framework | Spring Boot |
|------|------|------|
| 配置方式 | XML 或 Java Config，手工声明一切 | 自动配置，开箱即用 |
| 服务器 | 需部署到外部 Tomcat | 内嵌 Tomcat/Jetty，`java -jar` 直接运行 |
| 依赖管理 | 手工协调版本号 | Starter 依赖一站式解决 |
| 启动速度 | 需理解 `web.xml` 所有配置才能启动 | 3 分钟写出 Hello World |
| 适合谁 | 理解底层原理 | 快速交付 |

```java
// Spring Boot 最小可运行应用
@SpringBootApplication
public class Application {
    public static void main(String[] args) {
        SpringApplication.run(Application.class, args);
    }
}
```

这 5 行代码干了什么：
- 启动了内嵌 Tomcat 服务器
- 扫描了所有 Bean 并注入
- 配置了 MVC、JSON 序列化、静态资源……
- 找到 `@RestController` 并暴露为 HTTP 接口
- 关闭时优雅释放所有资源

**约定优于配置的核心思想**：Spring Boot 预设了一套最佳实践。只要你按约定（比如把 Controller 放在 `主类所在包或其子包`），一切自动生效。你只在需要偏离约定时才写配置。

---

## 71.7 Spring 生态全景图

```
                    ┌──────────────────────────┐
                    │     Spring Boot           │
                    │   (一键启动 · 自动配置)     │
                    └──────────┬───────────────┘
                               │
        ┌──────────────────────┼──────────────────────┐
        │                      │                      │
        ▼                      ▼                      ▼
┌───────────────┐    ┌────────────────┐    ┌──────────────────┐
│ Spring MVC    │    │ Spring Data    │    │ Spring Security  │
│ (Web 层)      │    │ (数据访问层)   │    │ (安全框架)        │
└───────────────┘    └────────────────┘    └──────────────────┘
        │                      │                      │
        └──────────────────────┼──────────────────────┘
                               │
                               ▼
                    ┌──────────────────────────┐
                    │    Spring Framework       │
                    │  (IoC 容器 · AOP 核心)    │
                    └──────────────────────────┘
```

从第72章开始，你将沿着这个金字塔自底向上学习。这个教程的目标不是让你背注解，而是让你**理解 Spring 的运-行-逻-辑**。

---

## 71.8 小结

| 概念 | 一句话 | 你失去什么 | 你得到什么 |
|------|--------|-----------|-----------|
| IoC | 不自己 new，别人端给你 | new 对象的控制权 | 声明即可得、解耦 |
| DI | IoC 的具体实现：构造器/字段/Setter | 手动装配的自由 | 自动装配，可测试 |
| AOP | 横切逻辑抽离为切面 | 方法体内部加代码的习惯 | 逻辑解耦，关注点分离 |
| Spring Boot | Spring 的一键启动版 | 精细控制每个 XML | 约定优于配置，3分钟上线 |

---

## 71.9 自测题

**1. 以下关于 IoC 的描述，哪一项是正确的？**

A. IoC 让代码运行更快  
B. IoC 让对象之间的关系由框架管理，代码只需声明依赖  
C. IoC 要求所有对象都用 XML 配置  
D. IoC 是 AOP 的另一种叫法  

**2. 以下哪种注入方式被 Spring 官方推荐？**

A. 字段注入（@Autowired 直接标在字段上）  
B. Setter 注入  
C. 构造器注入  
D. 静态工厂注入  

**3. 你有一个需求："对所有 Service 层的 public 方法记录调用日志"。用 AOP 还是手工在每个方法里加日志代码？请简述理由。**

---

**答案提示**：1→B，2→C，3→AOP，因为日志是横切关注点，手工加会造成代码重复和关注点污染。下一章——亲手启动你的第一个 Spring Boot 项目。