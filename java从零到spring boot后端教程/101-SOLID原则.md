# 101-SOLID原则

> 💡 你建了一座房子。住了三年，想加个阳台——结果发现必须拆掉整面墙。隔壁小区同样结构的房子，加阳台只用了半天——因为设计时留了扩展接口。SOLID 原则就是让你的代码像隔壁小区一样"好改"——不拆墙、不打洞、不伤筋动骨。

---

## 本章目标
- 理解五个原则各自的含义与反例
- 能识别违反 SOLID 的代码
- 用 Java 代码展示"违反 vs 遵守"的对比
- 知道 SOLID 在 Spring 中的体现

---

## 101.1 S — 单一职责原则（SRP）

**定义**：一个类应该有且只有一个引起它变化的原因。

**违反的例子**：

```java
// ❌ 这个类做了太多事：处理订单 + 发邮件 + 打日志
public class OrderProcessor {
    public void process(Order order) {
        validate(order);          // 1. 校验
        saveToDatabase(order);    // 2. 持久化
        sendEmail(order);         // 3. 发邮件
        logOperation(order);      // 4. 记日志
    }
}
```

如果发邮件的逻辑要改，你就要改 `OrderProcessor`——而这个类本应该只关心订单处理。

**遵守的例子**：

```java
public class OrderProcessor {
    private final OrderRepository repository;
    private final EmailService emailService;
    private final LogService logService;

    public void process(Order order) {
        repository.save(order);
        emailService.send(order);
        logService.record(order);
    }
}
```

---

## 101.2 O — 开闭原则（OCP）

**定义**：对扩展开放，对修改关闭。新增功能应该通过**新增代码**实现，而不是**修改已有代码**。

**违反的例子**：

```java
// ❌ 每新增一种报表格式，就要改动 switch
public class ReportGenerator {
    public String generate(String type) {
        switch (type) {
            case "pdf": return generatePdf();
            case "excel": return generateExcel();
            case "word": return generateWord();
            default: throw new IllegalArgumentException();
        }
    }
}
```

**遵守的例子**：

```java
// ✅ 新增格式只需新增类，不改已有代码
public interface ReportGenerator {
    String generate();
}

@Component("pdf")
public class PdfGenerator implements ReportGenerator { ... }

@Component("excel")
public class ExcelGenerator implements ReportGenerator { ... }

// 调用方
@Service
@RequiredArgsConstructor
public class ReportService {
    private final Map<String, ReportGenerator> generators;  // Spring 自动注入所有实现
    public String generate(String type) {
        return generators.get(type).generate();
    }
}
```

---

## 101.3 L — 里氏替换原则（LSP）

**定义**：子类必须能够替换父类，而不破坏程序的正确性。

**违反的例子**：

```java
// ❌ 正方形继承了长方形，但 setWidth 也改了 height——破坏父类行为
public class Rectangle {
    protected int width, height;
    public void setWidth(int w) { this.width = w; }
    public void setHeight(int h) { this.height = h; }
    public int getArea() { return width * height; }
}

public class Square extends Rectangle {
    @Override
    public void setWidth(int w) { super.setWidth(w); super.setHeight(w); }
    @Override
    public void setHeight(int h) { super.setWidth(h); super.setHeight(h); }
}

// 使用方崩溃了
Rectangle r = new Square();
r.setWidth(5);
r.setHeight(10);
// 期望面积=50，实际=100！
```

**教训**：数学上正方形是长方形，但 OOP 中，如果子类改变了父类的行为契约，就不该继承。

---

## 101.4 I — 接口隔离原则（ISP）

**定义**：不应该强迫一个类实现它不需要的接口方法。

**违反的例子**：

```java
// ❌ 一个臃肿的接口
public interface Worker {
    void work();
    void eat();
    void sleep();
}

// 机器人被迫实现 eat() 和 sleep()，但根本不需要
public class Robot implements Worker {
    public void work() { /* 干活 */ }
    public void eat() { throw new UnsupportedOperationException(); }
    public void sleep() { throw new UnsupportedOperationException(); }
}
```

**遵守的例子**：

```java
// ✅ 拆成小接口
public interface Workable { void work(); }
public interface Eatable { void eat(); }
public interface Sleepable { void sleep(); }

public class Robot implements Workable {
    public void work() { /* 干活 */ }
}

public class Human implements Workable, Eatable, Sleepable {
    public void work() { /* 干活 */ }
    public void eat() { /* 吃饭 */ }
    public void sleep() { /* 睡觉 */ }
}
```

---

## 101.5 D — 依赖倒置原则（DIP）

**定义**：高层模块不应该依赖低层模块，两者都应该依赖抽象。抽象不应该依赖细节，细节应该依赖抽象。

**违反的例子**：

```java
// ❌ OrderService 直接依赖 MySqlUserRepository（具体类）
public class OrderService {
    private MySqlUserRepository userRepo = new MySqlUserRepository();
}
```

**遵守的例子**：

```java
// ✅ 依赖接口，不依赖具体类
public interface UserRepository {
    User findById(Long id);
}

public class OrderService {
    private final UserRepository userRepo;

    public OrderService(UserRepository userRepo) {
        this.userRepo = userRepo;
    }
}

// 随时可以换实现
// 测试时：OrderService service = new OrderService(new InMemoryUserRepository());
// 生产时：OrderService service = new OrderService(new MySqlUserRepository());
```

> 🤔 想多一点：DIP 不是说你不能 import 具体类。它是说你的**代码结构**应该朝抽象倾斜。Spring 的 IoC 容器就是 DIP 的物质化——你永远依赖接口 `@Autowired UserRepository`，Spring 在运行时注入具体实现。

---

## 101.6 SOLID 速查表

| 原则 | 一句话 | 违反的典型表现 |
|------|------|------|
| **S**RP | 一个类只做一件事 | 一个类里塞了 500 行 + 5 种不相关的逻辑 |
| **O**CP | 加功能不代码 | 每次加功能都要改一堆已有类 |
| **L**SP | 子类能无缝替换父类 | 子类 override 后把父类行为搞崩 |
| **I**SP | 接口要小而精 | 实现类被迫 override 空方法或抛异常 |
| **D**IP | 依赖抽象而非具体 | `new` 满天飞，换个实现要改 20 个文件 |

---

## 101.7 SOLID 在 Spring 中的体现

| 原则 | Spring 体现 |
|------|------|
| SRP | `@Service`、`@Repository`——不同职责天然分到不同类 |
| OCP | `@EventListener` + Spring Event——新增监听者不改发布者 |
| LSP | Bean 继承 / `@Primary`——子类 Bean 可以无缝替换父类 |
| ISP | `ApplicationContext` 分为多个子接口（`ListableBeanFactory`、`MessageSource`） |
| DIP | IoC 容器——你依赖接口，容器注入实现 |

---

## 101.8 小结

| 知识点 | 核心内容 |
|--------|----------|
| SOLID 五原则 | SRP、OCP、LSP、ISP、DIP |
| 核心思想 | 让代码易于扩展、易于测试、易于维护 |
| DI（依赖注入） | 就是 DIP 的实践手段 |

---

## 101.9 自测题

**1. 以下代码违反了 SOLID 中的哪个原则？**

```java
public class ReportService {
    private PdfGenerator generator = new PdfGenerator();

    public void generate(Report report) {
        generator.generate(report);
    }
}
```

**2. 接口隔离原则（ISP）和单一职责原则（SRP）有什么不同？**

**3. "高层模块依赖低层模块"——这是错误的。正确的做法是什么？叫什么原则？**

---

**答案提示**：1→违反 DIP（依赖倒置原则）和 OCP（开闭原则）。`ReportService` 应该依赖 `ReportGenerator` 接口而非 `PdfGenerator` 具体类。2→SRP 说的是**类**的职责单一；ISP 说的是**接口**的精简——不应该强迫实现类拥有不需要的方法。3→正确做法是高层模块和低层模块都依赖抽象（接口）。这叫 DIP（依赖倒置原则）。下一章——微服务基础。