# 第35章 Lambda 表达式

> 想象你让朋友帮忙买杯咖啡。传统方式：你写一份详细的委托书（定义类、实现接口、重写方法），签名盖章交给朋友。Lambda 方式：你直接说一句"帮我买杯拿铁"就行。Lambda 就是让你把"行为"当作参数一样传递——代码更简洁，意图更直接。

---

## 35.1 从匿名内部类到 Lambda

### 35.1.1 回忆匿名内部类的痛

在 Java 8 之前，想传递一段行为必须写匿名内部类：

```java
// 对字符串列表排序（Java 7 方式）
List<String> names = Arrays.asList("Charlie", "Alice", "Bob");

Collections.sort(names, new Comparator<String>() {
    @Override
    public int compare(String s1, String s2) {
        return s1.compareTo(s2);
    }
});
// 核心逻辑就一行 compareTo，但包装代码多达 5 行！
```

Java 8 的 Lambda：

```java
// Java 8 Lambda 方式
Collections.sort(names, (s1, s2) -> s1.compareTo(s2));

// 更进一步，用方法引用
Collections.sort(names, String::compareTo);

// 甚至直接用 List.sort
names.sort(String::compareTo);
```

### 35.1.2 Lambda 基本语法

```
(参数列表) -> { 方法体 }
```

五种写法演进：

```java
// 1. 完整形式：参数类型 + 大括号 + return
(String s) -> { return s.length(); }

// 2. 省略参数类型（编译器自动推断）
(s) -> { return s.length(); }

// 3. 单个参数可省略括号
s -> { return s.length(); }

// 4. 方法体只有一行可省略 {} 和 return
s -> s.length()

// 5. 无参数
() -> System.out.println("Hello")
```

---

## 35.2 函数式接口

> 🏷️ 此术语需进附录：**函数式接口**（Functional Interface）——有且只有一个抽象方法的接口。Lambda 表达式只能赋值给函数式接口类型的变量。可以用 `@FunctionalInterface` 注解标记，编译期会检查是否符合规则。

```java
@FunctionalInterface
interface MyFunction {
    int apply(int x);
    // int apply2(int x); // ❌ 如果加第二个抽象方法，编译报错

    // ✅ 可以有默认方法和静态方法，不影响"函数式接口"身份
    default void print() {
        System.out.println("default method");
    }
}

// Lambda 赋值给函数式接口
MyFunction square = x -> x * x;
System.out.println(square.apply(5)); // 25
```

---

## 35.3 Java 内置函数式接口

`java.util.function` 包提供了四大核心函数式接口，覆盖绝大多数场景：

### 35.3.1 Predicate<T> —— 判断

> 🏷️ 此术语需进附录：**Predicate**——接收一个参数，返回 `boolean`。用于条件判断/过滤。

```java
import java.util.function.Predicate;

Predicate<String> isEmpty = s -> s.isEmpty();
System.out.println(isEmpty.test(""));     // true
System.out.println(isEmpty.test("abc"));  // false

// 组合判断
Predicate<String> isLong = s -> s.length() > 5;
Predicate<String> isLongAndNotEmpty = isEmpty.negate().and(isLong);
System.out.println(isLongAndNotEmpty.test("hello world")); // true
```

### 35.3.2 Consumer<T> —— 消费

> 🏷️ 此术语需进附录：**Consumer**——接收一个参数，无返回值。用于对参数执行操作（打印、存储等）。

```java
import java.util.function.Consumer;

Consumer<String> printer = s -> System.out.println("输出：" + s);
printer.accept("Hello"); // 输出：Hello

// 链式消费
Consumer<String> upperPrinter = s -> System.out.println("大写：" + s.toUpperCase());
printer.andThen(upperPrinter).accept("hello");
// 输出：Hello
// 输出：大写：HELLO
```

### 35.3.3 Function<T, R> —— 转换

> 🏷️ 此术语需进附录：**Function**——接收一个参数，返回一个结果。用于转换/映射。

```java
import java.util.function.Function;

Function<String, Integer> length = s -> s.length();
System.out.println(length.apply("hello")); // 5

// 链式转换
Function<Integer, String> toString = i -> "长度是：" + i;
Function<String, String> composed = length.andThen(toString);
System.out.println(composed.apply("abc")); // 长度是：3
```

### 35.3.4 Supplier<T> —— 供应

> 🏷️ 此术语需进附录：**Supplier**——无参数，返回一个结果。用于延迟计算/工厂模式。

```java
import java.util.function.Supplier;

Supplier<Double> random = () -> Math.random();
System.out.println(random.get()); // 0.723...
System.out.println(random.get()); // 0.156...

// 懒加载
Supplier<ExpensiveObject> lazyObj = () -> new ExpensiveObject();
// 只有调用 get() 时才真正创建对象
```

### 35.3.5 四大接口速查表

| 接口 | 参数 | 返回值 | 用途 |
|------|------|--------|------|
| `Predicate<T>` | T | boolean | 判断、过滤 |
| `Consumer<T>` | T | void | 消费、执行 |
| `Function<T,R>` | T | R | 转换、映射 |
| `Supplier<T>` | 无 | T | 提供、创建 |

此外还有变体：
- `BiPredicate<T,U>`：两个参数 → boolean
- `BiConsumer<T,U>`：两个参数 → void
- `BiFunction<T,U,R>`：两个参数 → R
- `UnaryOperator<T>`：`Function<T,T>`（同类型转换）
- `BinaryOperator<T>`：`BiFunction<T,T,T>`（同类型二元运算）

---

## 35.4 方法引用

方法引用是 Lambda 的语法糖——当 Lambda 只是调用一个已存在的方法时，可以直接引用这个方法。

```java
// 四种方法引用形式

// 1. 静态方法引用：类名::静态方法
Function<String, Integer> parser = Integer::parseInt;
// 等价于：s -> Integer.parseInt(s)

// 2. 实例方法引用（特定对象）：实例::方法
String prefix = "Hello ";
Consumer<String> printer = System.out::println;
// 等价于：s -> System.out.println(s)

// 3. 实例方法引用（任意对象）：类名::实例方法
Function<String, Integer> getLen = String::length;
// 等价于：s -> s.length()

// 4. 构造器引用：类名::new
Supplier<ArrayList<String>> listFactory = ArrayList::new;
Function<Integer, ArrayList<String>> sizedFactory = ArrayList::new;
```

> 🤔 **想多一点**：`String::length` 这种写法看起来很奇怪——为什么"类名"能引用"实例方法"？实际上，编译器会将其转换为 `(String s) -> s.length()`，第一个参数变成方法调用的接收者。这是编译器在背后做的魔法。

---

## 35.5 变量捕获（effectively final）

Lambda 可以访问外部变量，但有严格限制：

```java
int number = 10;

// ✅ 可以读取外部变量
Runnable r1 = () -> System.out.println(number);

// ❌ 不能修改外部变量
// Runnable r2 = () -> number++; // 编译错误！number 不是 effectively final

// 实际上，即使你不显式修改，编译器也会检查
int x = 5;
// x = 6;        // 如果取消这行注释，下面 Lambda 就编译报错
Runnable r3 = () -> System.out.println(x);
// 因为 x 被赋值了两次，不再是 effectively final
```

什么是 **effectively final**？一个变量即使没有 `final` 修饰符，但只要它**只被赋值一次**（初始化那次），编译器就认为它是 effectively final，Lambda 就可以捕获它。

**为什么有这个限制？** Lambda 内部捕获的是变量的**值拷贝**，而不是引用。如果允许修改变量，会出现"内部改了但外部看不到"或"外部改了但内部看不到"的不一致问题。

---

## 35.6 Lambda vs 匿名内部类

| 对比项 | Lambda | 匿名内部类 |
|--------|--------|-----------|
| 实现方式 | `invokedynamic` 指令 | 生成独立的 .class 文件 |
| `this` 含义 | 指向外部类实例 | 指向匿名内部类自身 |
| 适用范围 | 仅函数式接口 | 任何接口/抽象类 |
| 代码量 | 极简 | 冗余 |

```java
public class LambdaVsInner {
    private String name = "外部";

    public void test() {
        // Lambda 中的 this = 外部类实例
        Runnable r1 = () -> System.out.println(this.name); // "外部"

        // 匿名内部类中的 this = 匿名内部类自身
        Runnable r2 = new Runnable() {
            @Override
            public void run() {
                System.out.println(this.getClass()); // LambdaVsInner$1
            }
        };
    }
}
```

---

## 35.7 ❌ 常见错误

### 错误1：Lambda 赋值给非函数式接口

```java
// ❌ 错误：Object 不是函数式接口
// Object obj = () -> System.out.println("Hello");

// ✅ 正确：赋值给函数式接口
Runnable r = () -> System.out.println("Hello");
```

### 错误2：Lambda 中修改外部变量

```java
int count = 0;
// ❌ 编译错误：count 不是 effectively final
// Runnable r = () -> count++;

// ✅ 正确：使用数组或 AtomicInteger 绕过
int[] counter = {0};
Runnable r = () -> counter[0]++; // ✅ 数组引用不变，内容可变
```

### 错误3：方法引用找不到合适的方法

```java
// ❌ 编译器不知道调用哪个 parseInt（参数类型不明确）
// Function<String, Integer> f = Integer::parseInt; // 编译错误？

// ✅ 其实是合法的，因为只有一个 int parseInt(String) 版本
Function<String, Integer> f = Integer::parseInt; // ✅

// ❌ 但这里有问题——有两个 max 重载
// BinaryOperator<Integer> max = Math::max;  // 编译错误，歧义！
// 有 Math.max(int, int) 和 Math.max(long, long)
```

---

## 35.8 小结

| 知识点 | 一句话总结 |
|--------|-----------|
| Lambda 语法 | `(参数) -> { 方法体 }`，单行可省略 {} 和 return |
| 函数式接口 | 只有一个抽象方法的接口，Lambda 的赋值目标 |
| Predicate | T → boolean，用于判断 |
| Consumer | T → void，用于消费 |
| Function | T → R，用于转换 |
| Supplier | () → T，用于提供 |
| 方法引用 | `类名::方法`，Lambda 的语法糖 |
| effectively final | Lambda 只能读不能改的外部变量 |

---

## 35.9 自测题

**1.** 将以下匿名内部类改写为 Lambda 表达式：

```java
Runnable r = new Runnable() {
    @Override
    public void run() {
        System.out.println("Hello");
    }
};
```

**2.** 以下代码为什么编译失败？如何修改？

```java
int sum = 0;
List<Integer> nums = List.of(1, 2, 3);
nums.forEach(n -> sum += n);  // 为什么这里报错？
```

**3.** 写出以下 Lambda 对应的方法引用形式：

```java
Function<String, Integer> f1 = s -> Integer.parseInt(s);
Consumer<String> c1 = s -> System.out.println(s);
Function<List<String>, Integer> f2 = list -> list.size();
Supplier<Object> s1 = () -> new Object();
```

> 答案提示：1. `Runnable r = () -> System.out.println("Hello");`；2. `sum` 不是 effectively final，Lambda 不能修改外部局部变量；3. `Integer::parseInt`、`System.out::println`、`List::size`、`Object::new`。