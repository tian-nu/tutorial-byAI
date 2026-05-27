# 第11章：Spring AOP面向切面编程

## 本章目标

学完本章你将能够：

- 用生活化类比理解AOP的核心概念（切面、切点、通知、代理）
- 区分JDK动态代理与CGLIB代理，知道什么情况下用哪种
- 编写五种通知类型（@Before / @After / @AfterReturning / @AfterThrowing / @Around）
- 写出精确的切入点表达式（execution / @annotation / within）
- 独立实现日志记录、权限校验、接口限流等实战切面
- 理解AOP失效的四大场景，掌握解决方案
- **完成EMS v3的AOP日志功能**：用@Around为Service层所有方法自动记录执行时间

---

## 11.1 AOP核心概念

### 11.1.1 从一把梳子理解AOP

想象你每天早上要梳头、洗脸、刷牙。这三件事各自独立，但它们有一个"横切"的共同点——**都得照镜子**。你把"照镜子"抽取出来放在镜子前，而不是把镜子嵌入到梳子、毛巾、牙刷里。

AOP（Aspect-Oriented Programming，面向切面编程）就是这个思想：

- 梳头、洗脸、刷牙 = **核心业务逻辑**（分散在各个方法中）
- 照镜子 = **横切关注点**（散落在每个方法里，代码重复）
- 镜子 = **切面（Aspect）**（把横切关注点集中管理的地方）

**在编程中**，你有10个Service方法，每个方法都要记录日志：

```java
// ❌ 没有AOP：日志代码散落在每个方法中
public void createOrder(Order order) {
    System.out.println(">>> 进入 createOrder, 参数: " + order);  // 日志
    // 核心业务逻辑...
    System.out.println("<<< 退出 createOrder");                   // 日志
}

public void cancelOrder(Long orderId) {
    System.out.println(">>> 进入 cancelOrder, 参数: " + orderId);  // 日志
    // 核心业务逻辑...
    System.out.println("<<< 退出 cancelOrder");                    // 日志
}

// ... 每个方法都重复这两行日志代码！
```

用AOP后：

```java
// ✅ AOP：日志代码集中在一个切面中
@Service
public class OrderService {
    public void createOrder(Order order) {
        // 只写业务逻辑！日志由切面自动完成
    }
    
    public void cancelOrder(Long orderId) {
        // 只写业务逻辑！
    }
}

// 日志切面（集中管理所有日志逻辑）
@Aspect
@Component
public class LogAspect {
    @Around("execution(* com.example.service.*.*(..))")
    public Object log(ProceedingJoinPoint joinPoint) throws Throwable {
        System.out.println(">>> 进入 " + joinPoint.getSignature().getName());
        Object result = joinPoint.proceed();  // 执行目标方法
        System.out.println("<<< 退出 " + joinPoint.getSignature().getName());
        return result;
    }
}
```

这就是AOP的威力：**把散落在各处的重复代码，抽取到一个集中的切面中**。

### 11.1.2 七大山头 — AOP术语图解

AOP有一些听起来很唬人的术语，但理解起来并不难。我们用"电影院"来类比：

```text
                        ┌─────────────────────────────────┐
                        │     切面 (Aspect)                │
                        │   = 保安部门                     │
                        │   "负责所有安全检查的模块"        │
                        │                                  │
                        │  ┌────────────────────────────┐  │
                        │  │ 切入点 (Pointcut)            │  │
                        │  │ = "哪些地方需要检查"         │  │
                        │  │ "所有标了@Vip的方法"         │  │
                        │  └────────────────────────────┘  │
                        │                                  │
                        │  ┌────────────────────────────┐  │
                        │  │ 通知 (Advice)               │  │
                        │  │ = "检查什么+何时检查"        │  │
                        │  │ 入场前查票(@Before)          │  │
                        │  │ 出场后清场(@After)           │  │
                        │  └────────────────────────────┘  │
                        └─────────────────────────────────┘
                                    │
                                    │ 织入 (Weaving)
                                    │ = "把保安部署到岗位上"
                                    ▼
┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐
│ 影厅1    │  │ 影厅2    │  │ 影厅3    │  │ 影厅4    │
│(连接点1) │  │(连接点2) │  │(连接点3) │  │(连接点4) │
│=看《阿凡达》│  │=看《让子弹飞》│ │=看《流浪地球》│ │=看《熊出没》│
└──────────┘  └──────────┘  └──────────┘  └──────────┘
     ▲              ▲              ▲              ▲
     └──────────────┴──────────────┴──────────────┘
                    目标对象 (Target) — 被代理的影厅
```

| AOP术语 | 生活类比（电影院） | 严格定义 |
|---------|-------------------|---------|
| **切面 (Aspect)** | 保安部门 | 横切关注点的模块化封装，包含切点和通知 |
| **连接点 (JoinPoint)** | 影厅1、影厅2……（每个可能被检查的点） | 程序执行过程中的某个点（如方法调用、异常抛出） |
| **切入点 (Pointcut)** | "所有VIP影厅"（筛选出要检查的连接点） | 匹配连接点的表达式，决定通知应用到哪些方法上 |
| **通知 (Advice)** | "入场前查票"（在连接点执行的动作+时机） | 在特定切入点执行的动作 |
| **目标对象 (Target)** | 被检查的影厅 | 被代理的原始对象 |
| **织入 (Weaving)** | 把保安部署到影厅门口 | 将切面应用到目标对象来创建代理对象的过程 |
| **代理 (Proxy)** | 有保安把守的影厅 | AOP框架创建的增强对象 |

### 11.1.3 JDK动态代理 vs CGLIB代理

Spring AOP背后有两种创建代理的方式：

```text
┌──────────────────────────────────────────────────────────────┐
│                    Spring AOP 代理策略                        │
├────────────────────────────┬─────────────────────────────────┤
│   JDK 动态代理              │   CGLIB 代理                    │
│   (基于接口)                │   (基于继承)                    │
├────────────────────────────┼─────────────────────────────────┤
│                            │                                 │
│  UserDao接口               │  UserDaoImpl                    │
│     ▲                      │      ▲                          │
│     │ 实现                  │      │ 继承                     │
│  UserDaoImpl ───代理─── $Proxy │  $CGLIB_UserDaoImpl          │
│                            │  (extends UserDaoImpl)          │
├────────────────────────────┼─────────────────────────────────┤
│ ✅ 只能代理接口方法          │ ✅ 可以代理普通类方法             │
│ ❌ 不依赖第三方库             │ ❌ 需要cglib依赖                 │
│ ❌ final类无法代理            │ ❌ final方法无法代理              │
│ ❌ 非public方法不能代理       │ ❌ private方法无法代理            │
│                            │ ✅ Spring Boot 2.x+ 默认策略      │
└────────────────────────────┴─────────────────────────────────┘
```

**Spring Boot的默认选择**：
- Spring Boot 1.x：默认JDK动态代理（`spring.aop.proxy-target-class=false`）
- Spring Boot 2.x/3.x：默认CGLIB代理（`spring.aop.proxy-target-class=true`）

**什么时候用哪个？**
- 有接口 → 两种都行，默认CGLIB
- 没接口 → 只能用CGLIB
- 强制用JDK → `@EnableAspectJAutoProxy(proxyTargetClass = false)`（但基本不需要）

> 🚨 **坑点1：final类不能被CGLIB代理！**
>
> ```java
> public final class FinalService {  // final类 → CGLIB无法继承 → 代理失败！
>     public void doWork() { ... }
> }
> // CGLIB代理原理是继承目标类，final类不能继承，所以无法代理
> // 解决方案：去掉final，或改用接口+JDK动态代理
> ```

> 🚨 **坑点2：private方法不能被AOP代理！**
>
> ```java
> @Service
> public class UserService {
>     private void internalHelper() {  // private → 代理类继承后不可见！
>         // 这个方法永远不会被AOP拦截
>     }
> }
> // 无论是JDK动态代理还是CGLIB，都无法代理private方法
> // JDK代理只代理接口中的public方法
> // CGLIB代理继承后private方法不可见
> ```

---

## 11.2 五种通知类型

Spring AOP提供了五种通知（Advice），你只需在方法上加注解，Spring就会在合适的时机调用它。

### 11.2.1 @Before — 前置通知

**目标方法执行之前执行。** 适合做权限校验、参数预处理。

```java
@Aspect
@Component
public class BeforeAspect {
    
    @Before("execution(* com.example.service.UserService.*(..))")
    public void before(JoinPoint joinPoint) {
        String methodName = joinPoint.getSignature().getName();
        Object[] args = joinPoint.getArgs();
        System.out.println("[前置通知] 即将执行: " + methodName);
        System.out.println("[前置通知] 参数: " + Arrays.toString(args));
    }
}
```

**JoinPoint能拿到什么？**

| 方法 | 返回值 | 说明 |
|------|--------|------|
| `getSignature().getName()` | String | 方法名 |
| `getSignature().getDeclaringTypeName()` | String | 类名 |
| `getArgs()` | Object[] | 方法参数数组 |
| `getTarget()` | Object | 目标对象（原始对象） |
| `getThis()` | Object | 代理对象 |

```java
// 实战示例：参数合法性预检查
@Before("execution(* com.example.service.*.save*(..))")
public void validateSaveArgs(JoinPoint joinPoint) {
    for (Object arg : joinPoint.getArgs()) {
        if (arg == null) {
            String methodName = joinPoint.getSignature().getName();
            System.out.println("⚠ 警告：" + methodName + " 收到了null参数！");
        }
    }
}
```

### 11.2.2 @After — 后置通知（finally语义）

**目标方法执行之后执行，不论是否抛异常（相当于finally）。**

```java
@Aspect
@Component
public class AfterAspect {
    
    @After("execution(* com.example.service.*.*(..))")
    public void after(JoinPoint joinPoint) {
        String methodName = joinPoint.getSignature().getName();
        System.out.println("[后置通知] " + methodName + " 执行完毕（不论是否异常）");
        // 适合：清理资源、记录结束日志、释放ThreadLocal
    }
}
```

> **注意**：`@After`在`@AfterReturning`和`@AfterThrowing`**之前**执行。它不关心方法是正常返回还是抛异常，只要方法结束（包括异常退出）它就执行。

### 11.2.3 @AfterReturning — 返回通知

**目标方法正常返回后执行，可以获取返回值。**

```java
@Aspect
@Component
public class AfterReturningAspect {
    
    @AfterReturning(
        pointcut = "execution(* com.example.service.OrderService.create*(..))",
        returning = "result"  // 用result变量接收返回值
    )
    public void afterReturning(JoinPoint joinPoint, Object result) {
        String methodName = joinPoint.getSignature().getName();
        System.out.println("[返回通知] " + methodName + " 正常返回");
        System.out.println("[返回通知] 返回值: " + result);
        
        // 实战：缓存返回值
        // cacheManager.put(key, result);
    }
}
```

**如果方法抛异常了，`@AfterReturning`不会执行。**

### 11.2.4 @AfterThrowing — 异常通知

**目标方法抛异常后执行，可以获取异常信息。**

```java
@Aspect
@Component
public class AfterThrowingAspect {
    
    @AfterThrowing(
        pointcut = "execution(* com.example.service.*.*(..))",
        throwing = "ex"  // 用ex变量接收抛出的异常
    )
    public void afterThrowing(JoinPoint joinPoint, Exception ex) {
        String methodName = joinPoint.getSignature().getName();
        System.out.println("[异常通知] " + methodName + " 抛出异常: " + ex.getMessage());
        
        // 实战：发送报警邮件、记录错误日志
        // alertService.sendAlert(methodName, ex);
    }
}
```

> **注意**：`throwing`属性的参数名必须和方法参数名一致。如果方法抛出的异常类型不匹配（比如这里指定了`Exception`但实际上抛了`Error`），该通知不会执行。

### 11.2.5 @Around — 环绕通知（最强大）

**包围目标方法的执行，可以控制方法是否执行、修改参数、修改返回值、捕获异常。**

```java
@Aspect
@Component
public class AroundAspect {
    
    @Around("execution(* com.example.service.*.*(..))")
    public Object around(ProceedingJoinPoint joinPoint) throws Throwable {
        String methodName = joinPoint.getSignature().getName();
        long start = System.currentTimeMillis();
        
        System.out.println("[环绕-前] 开始执行: " + methodName);
        
        Object result;
        try {
            // ★ 关键：调用proceed()才真正执行目标方法！
            result = joinPoint.proceed();
            
            long elapsed = System.currentTimeMillis() - start;
            System.out.println("[环绕-后] " + methodName + " 正常返回");
            System.out.println("[环绕-后] 耗时: " + elapsed + "ms");
            return result;
            
        } catch (Exception e) {
            long elapsed = System.currentTimeMillis() - start;
            System.out.println("[环绕-异常] " + methodName + " 异常: " + e.getMessage());
            System.out.println("[环绕-异常] 耗时: " + elapsed + "ms");
            throw e;  // 重新抛出，不吞异常
        }
    }
}
```

> 🚨 **坑点：@Around必须调用proceedingJoinPoint.proceed()！**
>
> ```java
> @Around("execution(* com.example.service.*.*(..))")
> public Object around(ProceedingJoinPoint joinPoint) {
>     System.out.println("进入切面");
>     // ❌ 忘记调用 joinPoint.proceed()！
>     // 目标方法永远不会执行！而且方法返回null！
>     return null;
> }
> ```
>
> **不调proceed()的后果**：目标方法不会执行，调用方拿到null（除非你返回了别的值）。这是AOP中排名第一的Bug。

> 🚨 **坑点：@Around中修改参数类型会导致后续通知失效**
>
> ```java
> @Around("execution(* com.example.service.*.*(..))")
> public Object around(ProceedingJoinPoint joinPoint) throws Throwable {
>     Object[] args = joinPoint.getArgs();
>     // 修改参数类型（比如把String改成Integer）
>     args[0] = 999;  // 原类型是String！
>     
>     // proceed(修改后的参数) 会传给目标方法
>     // 但后续的@Before等通知拿到的还是原始参数！
>     return joinPoint.proceed(args);
> }
> ```
>
> @Around修改参数后调用`proceed(args)`，修改后的参数会传给**目标方法**和**后续@Before通知**，但@AfterReturning等通知收到的参数由JoinPoint决定。建议只在确实需要时才修改参数，并保持类型一致。

### 11.2.6 五种通知执行顺序 — 一图胜千言

我们用一段完整代码来演示五种通知的执行顺序，并分正常和异常两种情况。

```java
@Aspect
@Component
public class OrderAspect {
    
    @Before("execution(* com.example.service.OrderService.*(..))")
    public void before(JoinPoint jp) {
        System.out.println("① @Before");
    }
    
    @After("execution(* com.example.service.OrderService.*(..))")
    public void after(JoinPoint jp) {
        System.out.println("④/④ @After");
    }
    
    @AfterReturning(pointcut = "execution(* com.example.service.OrderService.*(..))", 
                    returning = "result")
    public void afterReturning(JoinPoint jp, Object result) {
        System.out.println("⑤ @AfterReturning → 返回值: " + result);
    }
    
    @AfterThrowing(pointcut = "execution(* com.example.service.OrderService.*(..))", 
                   throwing = "ex")
    public void afterThrowing(JoinPoint jp, Exception ex) {
        System.out.println("⑤ @AfterThrowing → 异常: " + ex.getMessage());
    }
    
    @Around("execution(* com.example.service.OrderService.*(..))")
    public Object around(ProceedingJoinPoint pjp) throws Throwable {
        System.out.println("② @Around - 前");
        try {
            Object result = pjp.proceed();  // ← 执行目标方法
            System.out.println("③ @Around - 正常返回");
            return result;
        } catch (Exception e) {
            System.out.println("③ @Around - 异常: " + e.getMessage());
            throw e;
        }
    }
}
```

**正常流程输出**（目标方法不抛异常）：

```text
② @Around - 前
① @Before
=== 目标方法执行中... ===
③ @Around - 正常返回
④ @After
⑤ @AfterReturning → 返回值: Order[id=1, name=测试订单]
```

**异常流程输出**（目标方法抛出异常）：

```text
② @Around - 前
① @Before
=== 目标方法执行中...抛异常了！===
③ @Around - 异常: 库存不足
④ @After
⑤ @AfterThrowing → 异常: 库存不足
```

**记住这张顺序图**：

```text
正常流程：                         异常流程：
                                  @Around前半
@Around前半                             ↓
    ↓                              @Before
@Before                                 ↓
    ↓                          目标方法(抛异常) ✕
目标方法(正常返回) ✓                    ↓
    ↓                        @AfterThrowing
@Around后半                             ↓
    ↓                              @After
@AfterReturning
    ↓
@After
```

---

## 11.3 切入点表达式

切入点表达式是AOP的"导航系统"，决定了切面织入到哪里。写错了不会报错只会"静默不生效"。

### 11.3.1 execution表达式（最常用、最灵活）

完整语法：

```text
execution(
    修饰符?                    ← 可选，访问修饰符
    返回类型                   ← 必须，支持通配符 *
    声明类型?                  ← 可选，包名+类名
    方法名(参数类型列表)       ← 必须
    throws 异常类型?           ← 可选
)
```

**从简单到复杂的示例集合**：

```java
// 1. 最宽泛：拦截所有方法
execution(* *(..))
//    │   │ │
//    │   │ └── ..  任意参数
//    │   └── *   任意方法名
//    └── *       任意返回类型

// 2. 拦截指定包下所有类的所有方法
execution(* com.example.service.*.*(..))
//                          │  │ │
//                          │  │ └── 任意参数
//                          │  └── 任意方法名
//                          └── 任意类名（不包含子包！）

// 3. 拦截指定包及所有子包
execution(* com.example.service..*.*(..))
//                             │
//                             └── ..  包含所有子包

// 4. 拦截指定类
execution(* com.example.service.OrderService.*(..))

// 5. 拦截返回类型为String的方法
execution(String com.example.service.*.*(..))

// 6. 拦截public方法
execution(public * com.example.service.*.*(..))

// 7. 拦截以save开头的方法
execution(* com.example.service.*.save*(..))
//                                    │
//                                    └── save*  匹配save/saveOrder/saveAll...

// 8. 拦截只有一个参数且类型为Long的方法
execution(* com.example.service.*.*(Long))
//                                  │
//                                  └── (Long) 精确匹配一个Long参数

// 9. 拦截第一个参数为Long，其余任意的方法
execution(* com.example.service.*.*(Long, ..))
//                                       │
//                                       └── .. 匹配剩余任意参数

// 10. 拦截无参数的方法
execution(* com.example.service.*.*())
//                                  │
//                                  └── () 无参数
```

**通配符总结**：

| 通配符 | 含义 | 使用位置 |
|--------|------|---------|
| `*` | 匹配任意一个部分 | 返回类型、包名、类名、方法名 |
| `..` | 匹配任意多个部分 | 包路径（含子包）、参数列表 |

> 🚨 **坑点：execution表达式写错 → 静默不生效 → 加日志排查**
>
> 这是AOP中最让人头疼的问题。写错表达式不会有任何报错——因为从Spring的角度看，只是"没有匹配到任何连接点"而已，这是合法的情况。
>
> ```java
> // 这句永远匹配不到，但不会报错！
> execution(* com.example.service.OrderService.*(..))
> // 如果包名写成了 com.exmaple（拼写错误），就是0个匹配
> ```
>
> **排查技巧**：在通知方法中加日志打印JoinPoint信息：
>
> ```java
> @Before("execution(* com.example.service.*.*(..))")
> public void before(JoinPoint jp) {
>     System.out.println("切面生效！目标方法: " + jp.getSignature());
>     // 如果没有输出 → 表达式没匹配到 → 检查表达式
> }
> ```

### 11.3.2 @annotation — 基于自定义注解的切入（实用性强）

这是实战中最灵活的切入方式。自己定义一个注解，然后切面匹配所有加了该注解的方法。

**步骤1：定义注解**

```java
import java.lang.annotation.*;

@Target(ElementType.METHOD)     // 只能用在方法上
@Retention(RetentionPolicy.RUNTIME)  // 运行时保留（AOP需要！）
public @interface LogExecution {
    String value() default "";  // 可选描述
}
```

**步骤2：编写切面**

```java
@Aspect
@Component
public class LogExecutionAspect {
    
    @Around("@annotation(logExecution)")  // 匹配所有加了@LogExecution的方法
    public Object around(ProceedingJoinPoint pjp, LogExecution logExecution) throws Throwable {
        String desc = logExecution.value();
        String methodName = pjp.getSignature().getName();
        long start = System.currentTimeMillis();
        
        System.out.println("[" + desc + "] 开始执行: " + methodName);
        Object result = pjp.proceed();
        long elapsed = System.currentTimeMillis() - start;
        System.out.println("[" + desc + "] 执行完成: " + methodName + " 耗时 " + elapsed + "ms");
        
        return result;
    }
}
```

**步骤3：使用注解**

```java
@Service
public class OrderService {
    
    @LogExecution("创建订单")  // 这个方法会被AOP拦截
    public Order createOrder(Order order) {
        // 业务逻辑...
        return order;
    }
    
    @LogExecution("取消订单")
    public void cancelOrder(Long orderId) {
        // 业务逻辑...
    }
    
    public Order queryOrder(Long orderId) {
        // 没加@LogExecution → 不会被拦截
        return null;
    }
}
```

**输出**：
```text
[创建订单] 开始执行: createOrder
[创建订单] 执行完成: createOrder 耗时 35ms
```

### 11.3.3 within表达式

`within`按类型匹配，比`execution`粒度更粗：

```java
// 拦截OrderService类中的所有方法
@Before("within(com.example.service.OrderService)")

// 拦截service包下所有类
@Before("within(com.example.service.*)")

// 拦截实现了UserDao接口的所有类
@Before("within(com.example.dao.UserDao+)")
//                                       │
//                                       └── +  匹配接口的所有实现类
```

### 11.3.4 切入点组合（&&、||、!）

```java
// AND：必须同时满足两个条件
@Around("execution(* com.example.service.*.*(..)) && @annotation(logExecution)")

// OR：满足任一条件
@Around("execution(* com.example.service.*.save*(..)) || execution(* com.example.service.*.update*(..))")

// NOT：排除
@Around("execution(* com.example.service.*.*(..)) && !execution(* com.example.service.*.toString())")

// 组合使用
@Around("execution(* com.example.service..*.*(..)) "
      + "&& !within(com.example.service.internal.*) "
      + "&& !execution(* *.get*(..)) "
      + "&& !execution(* *.set*(..))")
// 含义：拦截service包及子包下所有public方法，但不包括internal包，不包括getter/setter

// 复用切入点（用@Pointcut定义）
@Aspect
@Component
public class ServiceAspect {
    
    @Pointcut("execution(* com.example.service.*.*(..))")
    public void serviceLayer() {}  // 切入点签名，方法体为空
    
    @Pointcut("execution(* com.example.service.*.get*(..))")
    public void getterMethods() {}
    
    @Around("serviceLayer() && !getterMethods()")
    public Object aroundService(ProceedingJoinPoint pjp) throws Throwable {
        // 拦截service层所有方法，但排除getter
        return pjp.proceed();
    }
}
```

---

## 11.4 AOP四大实战

光说不练假把式。四个完整可运行的实战切面，覆盖了AOP 90%的应用场景。

### 11.4.1 实战一：统一日志记录（@Around + 执行时间统计）

这是最常见的AOP应用，为所有Service方法自动记录执行时间。

```java
@Aspect
@Component
public class ServiceLogAspect {
    
    private static final String LOG_FORMAT = "[{}] {}.{}() 参数={} 耗时={}ms 结果={}";
    
    @Around("execution(* com.example.service..*.*(..))")
    public Object logAround(ProceedingJoinPoint joinPoint) throws Throwable {
        String className = joinPoint.getSignature().getDeclaringType().getSimpleName();
        String methodName = joinPoint.getSignature().getName();
        Object[] args = joinPoint.getArgs();
        
        long start = System.currentTimeMillis();
        Object result = null;
        
        try {
            result = joinPoint.proceed();
            return result;
        } catch (Throwable e) {
            System.out.printf("[ERROR] %s.%s() 参数=%s 异常=%s%n",
                    className, methodName, Arrays.toString(args), e.getMessage());
            throw e;
        } finally {
            long elapsed = System.currentTimeMillis() - start;
            System.out.printf("[INFO] %s.%s() 参数=%s 耗时=%dms 结果=%s%n",
                    className, methodName, Arrays.toString(args), elapsed, result);
        }
    }
}
```

**输出示例**：
```text
[INFO] OrderService.createOrder() 参数=[Order(id=null, name=测试订单)] 耗时=45ms 结果=Order(id=101, name=测试订单)
[INFO] UserService.findById() 参数=[1001] 耗时=12ms 结果=User(id=1001, name=张三)
[ERROR] PaymentService.pay() 参数=[101] 异常=余额不足
```

### 11.4.2 实战二：权限校验（@Before + 自定义注解）

自定义一个`@RequirePermission`注解，放在需要权限控制的方法上。

**权限注解定义**：

```java
@Target(ElementType.METHOD)
@Retention(RetentionPolicy.RUNTIME)
public @interface RequirePermission {
    String value();  // 权限标识，如 "user:delete"
}
```

**权限切面**：

```java
@Aspect
@Component
public class PermissionAspect {
    
    // 模拟当前登录用户的权限（实际项目中从SecurityContext获取）
    private static final ThreadLocal<Set<String>> CURRENT_PERMISSIONS = 
            ThreadLocal.withInitial(HashSet::new);
    
    @Before("@annotation(requirePermission)")
    public void checkPermission(JoinPoint joinPoint, RequirePermission requirePermission) {
        String required = requirePermission.value();
        Set<String> currentPermissions = CURRENT_PERMISSIONS.get();
        
        if (!currentPermissions.contains(required)) {
            String methodName = joinPoint.getSignature().getName();
            System.err.println("[权限拒绝] " + methodName + " 需要权限: " + required);
            System.err.println("[权限拒绝] 当前用户拥有权限: " + currentPermissions);
            throw new SecurityException("权限不足，需要: " + required);
        }
        
        System.out.println("[权限通过] " + joinPoint.getSignature().getName() 
                + " 权限: " + required);
    }
    
    // 设置当前用户权限（演示用）
    public static void setPermissions(String... permissions) {
        CURRENT_PERMISSIONS.set(new HashSet<>(Arrays.asList(permissions)));
    }
    
    // 清除权限
    public static void clearPermissions() {
        CURRENT_PERMISSIONS.remove();
    }
}
```

**使用**：

```java
@Service
public class UserManageService {
    
    @RequirePermission("user:query")
    public User findById(Long id) {
        return userDao.findById(id);
    }
    
    @RequirePermission("user:delete")
    public void deleteUser(Long id) {
        userDao.delete(id);
    }
}

// 测试
PermissionAspect.setPermissions("user:query");
userManageService.findById(1L);     // ✅ 权限通过
userManageService.deleteUser(1L);   // ❌ SecurityException: 权限不足，需要: user:delete
PermissionAspect.clearPermissions();
```

### 11.4.3 实战三：接口限流（@Around + 计数器）

防止某些接口被频繁调用。这里用简单的内存计数器演示，生产环境建议用Redis。

```java
@Target(ElementType.METHOD)
@Retention(RetentionPolicy.RUNTIME)
public @interface RateLimit {
    int maxCalls() default 10;       // 最大调用次数
    int timeWindowSeconds() default 60;  // 时间窗口（秒）
}
```

**限流切面**：

```java
@Aspect
@Component
public class RateLimitAspect {
    
    // 记录每个方法的上次重置时间和当前窗口内的调用次数
    private final ConcurrentHashMap<String, RateLimitBucket> buckets = new ConcurrentHashMap<>();
    
    @Around("@annotation(rateLimit)")
    public Object limit(ProceedingJoinPoint joinPoint, RateLimit rateLimit) throws Throwable {
        String key = joinPoint.getSignature().toLongString();
        long now = System.currentTimeMillis();
        long windowMs = rateLimit.timeWindowSeconds() * 1000L;
        
        RateLimitBucket bucket = buckets.computeIfAbsent(key, 
                k -> new RateLimitBucket(now, windowMs));
        
        synchronized (bucket) {
            if (now - bucket.windowStart > windowMs) {
                // 窗口过期，重置
                bucket.windowStart = now;
                bucket.count = 0;
            }
            
            bucket.count++;
            
            if (bucket.count > rateLimit.maxCalls()) {
                System.err.println("[限流] " + joinPoint.getSignature().getName() 
                        + " 超过限制 " + rateLimit.maxCalls() + "次/" 
                        + rateLimit.timeWindowSeconds() + "秒");
                throw new RuntimeException("请求过于频繁，请稍后再试！");
            }
        }
        
        return joinPoint.proceed();
    }
    
    private static class RateLimitBucket {
        long windowStart;
        int count;
        final long windowMs;
        
        RateLimitBucket(long windowStart, long windowMs) {
            this.windowStart = windowStart;
            this.windowCount = 0;
            this.windowMs = windowMs;
        }
    }
}
```

**使用**：

```java
@RateLimit(maxCalls = 5, timeWindowSeconds = 60)  // 60秒内最多5次
public String sendVerifyCode(String phone) {
    return "验证码已发送";
}
```

### 11.4.4 实战四：缓存结果（@AfterReturning）

方法返回值放入缓存，下次相同参数直接返回缓存。

```java
@Aspect
@Component
public class CacheAspect {
    
    private final Map<String, Object> cache = new ConcurrentHashMap<>();
    private final Map<String, Long> expireMap = new ConcurrentHashMap<>();
    
    @Around("@annotation(cacheable)")
    public Object cache(ProceedingJoinPoint joinPoint, Cacheable cacheable) throws Throwable {
        String key = buildCacheKey(joinPoint);
        long expireMs = cacheable.expireSeconds() * 1000L;
        
        // 检查缓存
        Object cachedValue = cache.get(key);
        Long expireTime = expireMap.get(key);
        if (cachedValue != null && expireTime != null 
                && System.currentTimeMillis() < expireTime) {
            System.out.println("[缓存命中] " + key + " → " + cachedValue);
            return cachedValue;
        }
        
        // 缓存未命中，执行目标方法
        Object result = joinPoint.proceed();
        cache.put(key, result);
        expireMap.put(key, System.currentTimeMillis() + expireMs);
        System.out.println("[缓存写入] " + key + " → " + result);
        return result;
    }
    
    private String buildCacheKey(ProceedingJoinPoint joinPoint) {
        return joinPoint.getSignature().toShortString() 
                + ":" + Arrays.toString(joinPoint.getArgs());
    }
}
```

---

## 11.5 AOP失效场景（重点中的重点）

AOP失效是Spring开发中最常见的坑。理解原理才能正确排查。

### 11.5.1 ⚠️ 同类内部调用 — AOP失效

> 🚨 **坑点：同一个类中，方法A调用方法B时，B不会被AOP拦截！**

这是AOP中出镜率最高的坑。

**失效代码（可复现）**：

```java
@Service
public class OrderService {
    
    public void publicMethod() {
        System.out.println("publicMethod 开始");
        privateMethod();  // ← 直接调用，不走代理！
        System.out.println("publicMethod 结束");
    }
    
    @LogExecution("内部方法")  // 这个注解不会生效！
    public void privateMethod() {
        System.out.println("privateMethod 执行中...");
    }
}

// 测试
@Configuration
@ComponentScan("com.example")
@EnableAspectJAutoProxy  // 启用AOP
public class AppConfig { }

public class Main {
    public static void main(String[] args) {
        ApplicationContext ctx = new AnnotationConfigApplicationContext(AppConfig.class);
        OrderService service = ctx.getBean(OrderService.class);
        
        service.publicMethod();
        // 输出：
        // publicMethod 开始
        // privateMethod 执行中...   ← @LogExecution 注解没有生效！
        // publicMethod 结束
    }
}
```

**为什么失效？**

```text
外部调用者
    │
    ▼
┌─────────────┐     调用 publicMethod()
│   代理对象   │  ←────────────────── ctx.getBean() 拿到的是这个
│ $Proxy/     │
│ $CGLIB      │     调用 publicMethod()
│   ┌───────┐ │  ←────────────────── 走代理 → 触发AOP
│   │ 真实   │ │
│   │ 对象   │ │     调用 privateMethod()
│   │       │◄── ←────────────────── this.privateMethod()
│   └───────┘ │                       ↑
└─────────────┘                  this是真实对象，不是代理！
                                 所以不走AOP！
```

关键：`this.privateMethod()`中的`this`指向的是**真实对象**（被代理的目标对象），而不是代理对象。只有通过**代理对象**的调用才会触发AOP拦截。

**解决方案1：AopContext.currentProxy()（推荐）**

```java
@Service
public class OrderService {
    
    public void publicMethod() {
        System.out.println("publicMethod 开始");
        // 通过AopContext获取当前代理对象
        OrderService proxy = (OrderService) AopContext.currentProxy();
        proxy.privateMethod();  // ← 走代理，AOP生效！
        System.out.println("publicMethod 结束");
    }
    
    @LogExecution("内部方法")
    public void privateMethod() {
        System.out.println("privateMethod 执行中...");
    }
}
```

需要额外配置暴露代理：

```java
@Configuration
@EnableAspectJAutoProxy(exposeProxy = true)  // ★ 必须加 exposeProxy = true
@ComponentScan("com.example")
public class AppConfig { }
```

或者Spring Boot中：
```yaml
spring:
  aop:
    auto: true
```

> **注意**：`exposeProxy = true`会让Spring把当前代理对象绑定到`AopContext`的ThreadLocal中。这是一个全局配置，如果有性能顾虑，仅在需要时开启。

**解决方案2：拆到不同类（架构上最干净）**

```java
@Service
public class OrderService {
    
    @Autowired
    private OrderInternalService internalService;
    
    public void publicMethod() {
        System.out.println("publicMethod 开始");
        internalService.privateMethod();  // ← 跨类调用，走代理！
        System.out.println("publicMethod 结束");
    }
}

@Service
public class OrderInternalService {
    
    @LogExecution("内部方法")
    public void privateMethod() {
        System.out.println("privateMethod 执行中...");
    }
}
```

这是从架构上解决问题——需要被AOP拦截的方法本来就应该属于一个独立的Service。

**解决方案3：@Autowired注入自己（不优雅但能用）**

```java
@Service
public class OrderService {
    
    @Autowired
    private OrderService self;  // 注入自己的代理对象
    
    public void publicMethod() {
        System.out.println("publicMethod 开始");
        self.privateMethod();  // ← 通过注入的代理调用
        System.out.println("publicMethod 结束");
    }
    
    @LogExecution("内部方法")
    public void privateMethod() {
        System.out.println("privateMethod 执行中...");
    }
}
```

### 11.5.2 ⚠️ private方法不能被代理

```java
@Service
public class UserService {
    
    @LogExecution  // 不会生效！
    private void internalMethod() {
        // private方法，CGLIB继承后不可见，AOP无法拦截
    }
}
```

**原因**：CGLIB通过继承目标类创建代理，`private`方法在子类中不可见。JDK动态代理更是只能代理接口中的public方法。

### 11.5.3 ⚠️ final方法不能被代理

```java
@Service
public class UserService {
    
    @LogExecution  // 不会生效！
    public final void doSomething() {
        // final方法，CGLIB无法重写，AOP无法拦截
    }
}
```

**原因**：CGLIB通过继承+重写方法来创建代理，`final`方法不能被重写。

### 11.5.4 AOP失效场景总结

| 失效场景 | 原因 | 解决方案 |
|----------|------|---------|
| 同类内部调用 | this调用的是原始对象而非代理 | AopContext.currentProxy() / 拆到不同类 |
| private方法 | 代理无法访问private方法 | 改为protected或public |
| final方法 | CGLIB无法重写final方法 | 去掉final |
| final类 | CGLIB无法继承final类 | 去掉final / 用接口+JDK代理 |
| 切入点表达式写错 | 没有匹配到任何方法 | 加日志验证切入点是否生效 |
| @Configuration中@Bean方法 | @Bean方法间的调用被CGLIB拦截 | （这个通常不是问题，而是特性） |

---

## 11.6 本章小结

这一章我们从"横切关注点"出发，全面学习了Spring AOP：

1. **AOP核心概念**：切面=横切关注点的模块、通知=在连接点的动作、切入点=匹配规则、代理=增强后的对象
2. **代理原理**：JDK动态代理（基于接口）vs CGLIB（基于继承，Spring Boot默认）
3. **五种通知**：
   - @Before：前置
   - @After：最后执行（finally语义）
   - @AfterReturning：正常返回后
   - @AfterThrowing：异常抛后
   - @Around：环绕（最强大，必须调proceed()）
4. **通知执行顺序**（正常/异常两种情况，Around→Before→目标方法→Around正常/异常→AfterReturning/AfterThrowing→After）
5. **切入点表达式**：execution（最常用）、@annotation（灵活）、within、组合（&&/||/!）
6. **四大实战切面**：日志记录、权限校验、接口限流、缓存结果
7. **AOP失效场景**：同类内部调用（`this.xxx()`不走代理）、private方法、final方法/类
8. **内部调用失效的三种解决方案**：AopContext.currentProxy()（需`exposeProxy=true`）、拆到不同类（架构最干净）、@Autowired注入自己（不优雅但能用）

---

## 思考题

1. 以下切面有什么严重Bug？

   ```java
   @Around("execution(* com.example.service.*.*(..))")
   public Object around(ProceedingJoinPoint pjp) {
       System.out.println("进入切面");
       System.out.println("离开切面");
       return "intercepted!";
   }
   ```

2. 为什么下面的AOP不生效？如何修正？

   ```java
   @Service
   public class Calculator {
       public int add(int a, int b) {
           return a + b;
       }
       
       @LogExecution("乘方运算")
       public int power(int base, int exp) {
           add(base, power(base, exp - 1));  // ← 这里的add会被拦截吗？
           int result = 1;
           for (int i = 0; i < exp; i++) {
               result *= base;
           }
           return result;
       }
   }
   ```

3. 以下两个切入点表达式分别能匹配到哪些方法？

   ```java
   // 表达式A
   execution(* com.example.service.*.*(..))
   
   // 表达式B
   execution(* com.example.service..*.*(..))
   ```

   假设项目结构为：`com.example.service.OrderService`、`com.example.service.impl.OrderServiceImpl`。

4. 如果需要在同一个切面中同时记录成功返回和异常两种情况的日志，最少需要定义哪几种通知？

5. 为什么Spring Boot默认使用CGLIB代理而不是JDK动态代理？

---

<details>
<summary>思考题参考答案（点击展开）</summary>

**第1题**：

严重Bug：**没有调用`pjp.proceed()`**！目标方法永远不会执行。

另外：
- `return "intercepted!"` 会覆盖目标方法的真实返回值
- 即使目标方法抛异常，这里也不会感知（因为根本没执行目标方法）

正确写法：

```java
@Around("execution(* com.example.service.*.*(..))")
public Object around(ProceedingJoinPoint pjp) throws Throwable {
    System.out.println("进入切面");
    try {
        Object result = pjp.proceed();  // ★ 必须调用！
        System.out.println("正常离开切面");
        return result;
    } catch (Throwable e) {
        System.out.println("异常离开切面: " + e.getMessage());
        throw e;
    }
}
```

**第2题**：

`add()`不会被AOP拦截。原因有两个：

1. **`add()`所在的`Calculator`类虽然有其他方法加了`@LogExecution`，但切面是按方法粒度匹配的**：`add()`方法本身没有`@LogExecution`注解，所以不会触发权限校验切面。但如果有一个基于`execution(* com.example.service.Calculator.*(..))`的切面，那就要看第2点。

2. **同类内部调用问题**：`power()`中`add(base, power(base, exp-1))`中的`add()`是通过`this.add()`调用的（this被省略），`this`指向的是原始对象，不是代理对象。所以即使`add()`方法上有切面注解，也不会生效。

改造方案：将`add()`方法所在逻辑拆到独立的`AdderService`中，或者用`AopContext.currentProxy()`。

**第3题**：

| 表达式 | 能匹配 `com.example.service.OrderService` | 能匹配 `com.example.service.impl.OrderServiceImpl` |
|--------|------|------|
| `execution(* com.example.service.*.*(..))` | ✅ 能 | ❌ 不能（`impl`是子包，`*`不包含子包） |
| `execution(* com.example.service..*.*(..))` | ✅ 能 | ✅ 能（`..`包含子包） |

关键区别：单个`*`匹配一层包，`..`匹配多层（含零层）包。

**第4题**：

最少需要三种：

1. `@Before` 记录进入方法
2. `@AfterReturning` 记录正常返回
3. `@AfterThrowing` 记录异常

也可以用`@Around`一个通知替代以上三种（推荐，因为可以在一个方法里统一管理所有逻辑）。

但注意：`@AfterReturning`和`@AfterThrowing`是互斥的（一个方法只能走其中一种），所以两者都需要。

**第5题**：

Spring Boot默认使用CGLIB代理，主要有三个原因：

1. **更通用**：CGLIB不要求目标类实现接口。大多数Service类并不实现接口，用JDK动态代理就没法代理。
2. **避免类型转换错误**：如果用了JDK动态代理，`getBean()`返回的是`$Proxy`实例，当代码中需要具体类型而非接口时会报`ClassCastException`。CGLIB返回的是目标类的子类，可以安全转型。
3. **表现一致**：不管有没有接口，表现都一样，开发者不需要关心代理细节。

在Spring Boot中可以通过 `spring.aop.proxy-target-class=false` 改回JDK动态代理，但基本没理由这么做。

</details>

---

> **下一篇预告**：第12章我们将学习Spring MVC——HTTP请求的处理。如果说IoC管理对象的"出生"、AOP管理方法调用的"前后"，那么Spring MVC管理的是从用户浏览器到你Service方法的整条链路。你将看到DispatcherServlet如何像一个高度智能的交通指挥员，把每个HTTP请求准确路由到对应的Controller方法。同时我们会在第12章末尾完成**EMS v3**：用Spring IoC + AOP + MVC分层重构员工管理系统。
>
> **知识串联提醒**：
> - `@Controller`注解本质上就是`@Component`（IoC容器管理）
> - `@Transactional`注解的底层就是AOP（环绕通知管理事务）
> - Spring Security的`@PreAuthorize`也是AOP
> - 理解了本章的AOP，后面所有"注解增强"类的功能你都可以一眼看出原理