# 第2章 Java基础语法

## 本章目标

学完本章后，你将能够：
- 掌握 Java 的 **八大基本数据类型**，理解类型选择原则与自动类型提升规则
- 熟练使用 **算术、关系、逻辑、赋值、三元及位运算符**，避开短路与非短路的陷阱
- 深刻理解 **`==` 与 `equals()` 的本质区别**——这是 Java 面试中最常被问到的基础题之一
- 灵活运用 **if-else、switch、for、while、do-while** 等流程控制语句
- 熟练掌握 **数组的声明、初始化、遍历和排序**

如果你有其他语言的编程经验，本章会特别关注 Java 的**独特之处**——那些在其他语言中不存在、或者行为大不相同的语法细节。掌握这些，你就拿到了打开 Java 编程大门的钥匙。

---

## 2.1 变量与数据类型

### 2.1.1 Java 是强类型语言——思维上的第一个转变

如果你来自 Python 或 JavaScript 的世界，你可能习惯了这种写法：

```python
x = 1       # Python：x 是整数
x = "hello" # 同一个变量，现在变成字符串了，完全合法
```

```javascript
var x = 1;       // JavaScript：x 是 number
x = "hello";     // 完全没问题，类型自动变了
```

但在 Java 中，**这行不通**。Java 是**强类型语言**，每一个变量在声明时就必须确定类型，而且类型**终身不变**：

```java
int x = 1;       // 声明 x 为 int 类型
x = "hello";     // ❌ 编译错误！int 类型的变量不能赋字符串
```

这种设计看似"不灵活"，实际上是大项目开发的**保护机制**：类型一旦声明，编译器就能在代码运行之前发现大量错误。Python 要到实际执行时才会因为类型不匹配而报错，而 Java 在你写完代码、按下编译按钮的那一刻就能发现问题。

**变量声明的标准语法：**

```
类型  变量名  =  初始值;
int  count   =  0;
```

分号（`;`）是 Java 语句的**强制终结符**，不能省略。这与 Python 的"靠换行区分语句"完全不同。

### 2.1.2 八大基本数据类型（Primitive Types）

Java 的数据类型体系分为两大类：**基本类型**（存储的是数值本身）和**引用类型**（存储的是对象的内存地址）。我们先来掌握八大基本类型。

| 类型 | 占用字节 | 取值范围 | 默认值 | 示例 | 常见用途 |
|------|---------|---------|--------|------|----------|
| `byte` | 1 | -128 ~ 127 | 0 | `byte b = 100;` | 文件IO、网络传输的字节流 |
| `short` | 2 | -32768 ~ 32767 | 0 | `short s = 30000;` | 极少使用（int 基本替代了） |
| `int` | 4 | -2^31 ~ 2^31-1（约±21亿） | 0 | `int i = 100000;` | **整数默认选择** |
| `long` | 8 | -2^63 ~ 2^63-1 | 0L | `long l = 10000000000L;` | 超出 int 范围时使用（如时间戳） |
| `float` | 4 | 约 ±3.4E+38（6-7位有效数字） | 0.0f | `float f = 3.14f;` | 节省内存时（如游戏中的坐标） |
| `double` | 8 | 约 ±1.8E+308（15位有效数字） | 0.0d | `double d = 3.1415926;` | **小数默认选择** |
| `char` | 2 | 0 ~ 65535（Unicode字符） | `\u0000` | `char c = 'A';` | 单个字符（注意用**单引号**） |
| `boolean` | 1（JVM 相关） | `true` 或 `false` | `false` | `boolean b = true;` | 条件判断 |

**类型选择原则**（背下来，帮你少走弯路）：
1. **整数**：默认用 `int`。需要超出 ±21 亿范围（比如表示毫秒时间戳）时用 `long`。
2. **小数**：默认用 `double`。只有内存极度紧张时才考虑 `float`。
3. **字符**：用 `char`，不是 `String`！`'A'`（单引号）是 char，`"A"`（双引号）是 String。
4. **布尔**：用 `boolean`，不是 `int`！Java 与 C 语言不同，**1 和 0 不能代替 true 和 false**。

下面是每种类型的完整示例：

```java
package com.example;

public class PrimitiveTypesDemo {
    public static void main(String[] args) {
        byte b = 100;
        short s = 30000;
        int i = 2000000000;
        long l = 9000000000000000000L;  // 注意结尾的 L
        float f = 3.14f;                // 注意结尾的 f
        double d = 3.141592653589793;
        char c = '中';                  // char 可以存中文（一个汉字占 2 字节）
        boolean flag = true;

        System.out.println("byte:   " + b);
        System.out.println("short:  " + s);
        System.out.println("int:    " + i);
        System.out.println("long:   " + l);
        System.out.println("float:  " + f);
        System.out.println("double: " + d);
        System.out.println("char:   " + c);
        System.out.println("boolean:" + flag);
    }
}
```

这段代码展示了每种基本类型的声明和打印。注意 `long` 值的 `L` 后缀和 `float` 值的 `f` 后缀——它们不是装饰品，是语法要求。

> 🚨 **坑点：`float a = 3.14;` 编译错误**
>
> - **现象**：代码 `float a = 3.14;`，IDEA 红色波浪线报错 `incompatible types: possible lossy conversion from double to float`。
> - **原因**：Java 中带小数点的数字字面量**默认是 `double` 类型**。`3.14` 是一个 `double`（8 字节），你不能把它塞进 `float`（4 字节）而不做转换。
> - **正确做法**：`float a = 3.14f;` ——加上 `f` 或 `F` 后缀，告诉编译器"这是一个 float 字面量"。
> - **或者显式强转**（不推荐）：`float a = (float) 3.14;`

### 2.1.3 引用类型概述

除了八种基本类型，Java 中所有其他类型都是**引用类型**（Reference Type）。引用类型的变量存储的不是值本身，而是**对象在堆内存中的地址**。

```java
String name = "Alice";     // name 存的是 String 对象的地址，不是 "Alice" 本身
int[] scores = {90, 85};   // scores 存的是数组对象的地址
```

引用类型的默认值是 `null`（表示"没有指向任何对象"），这是 Java 中臭名昭著的 **NullPointerException（空指针异常）** 的根源。我们将在第 3 章面向对象编程中深入讨论。

### 2.1.4 自动类型提升（Implicit Casting）

当不同类型的数据参与运算时，Java 会自动将"小范围"的类型提升为"大范围"的类型。规则如下：

```
byte → short → int → long → float → double
                  ↑
                char
```

箭头方向表示**自动提升**的方向。来看几个例子：

```java
public class TypePromotionDemo {
    public static void main(String[] args) {
        int a = 10;
        double b = 3.5;
        double result = a + b;        // int 自动提升为 double，结果：13.5
        System.out.println(result);   // 13.5

        byte x = 10;
        byte y = 20;
        int z = x + y;                // byte 运算前自动提升为 int！
        System.out.println(z);        // 30

        char ch = 'A';                // 'A' 的 ASCII 值是 65
        int code = ch + 1;            // char 提升为 int，结果：66
        System.out.println(code);     // 66
        System.out.println((char) code); // 强转回 char：'B'
    }
}
```

关于 `byte` 运算的特殊规则：Java 规定 `byte`、`short`、`char` 三者参与算术运算时，**会先自动提升为 `int`**，运算结果也是 `int`。所以 `byte + byte = int`，而不是 `byte`。

### 2.1.5 强制类型转换（Explicit Casting）

当你需要把"大范围"的类型转为"小范围"的类型时，必须使用**强制类型转换**语法：

```
目标类型 变量名 = (目标类型) 原值;
```

强制转换可能导致两种问题：**精度丢失**和**数据溢出**。

```java
public class CastingDemo {
    public static void main(String[] args) {
        double pi = 3.14159;
        int intPi = (int) pi;          // 小数部分被截断，不是四舍五入！
        System.out.println(intPi);     // 3

        int bigNumber = 300;
        byte smallNumber = (byte) bigNumber; // 300 超出 byte 范围 -128~127
        System.out.println(smallNumber);     // 44（发生了溢出！见下文解释）
    }
}
```

第二个例子为什么输出 44？因为 `300` 的二进制是 `100101100`（9 位），`byte` 只能存 8 位，高位被截断后变成了 `00101100`，即十进制的 44。**这是危险的操作，不要盲目强转。**

> 🚨 **坑点：整数溢出——`int` 最大值 + 1 = 最小值（环形）**
>
> - **现象**：
>   ```java
>   int max = Integer.MAX_VALUE;   // 2147483647
>   int overflow = max + 1;
>   System.out.println(overflow);  // -2147483648（变成了最小值！）
>   ```
> - **原因**：Java 的整数是有符号的，使用**补码**表示。`Integer.MAX_VALUE` 的二进制是 `01111111 11111111 11111111 11111111`。加 1 后变成 `10000000 00000000 00000000 00000000`，这正是 `Integer.MIN_VALUE` 的补码。就像时钟走到了 12 点会回到 1 点，整数溢出也会"绕回去"。
> - **解决方案**：
>   1. 使用 `long` 类型存储更大范围的数值
>   2. 使用 `Math.addExact(a, b)`，溢出时会抛出 `ArithmeticException`，而不是静默环绕
>   3. 使用 `BigInteger`（处理任意大小的整数）

> 🚨 **坑点：浮点精度丢失——`0.1 + 0.2 != 0.3`**
>
> - **现象**：
>   ```java
>   System.out.println(0.1 + 0.2);  // 输出：0.30000000000000004
>   System.out.println(0.1 + 0.2 == 0.3); // false！
>   ```
> - **原因**：浮点数使用 IEEE 754 标准，以二进制形式存储。`0.1`、`0.2`、`0.3` 在二进制中都是**无限循环小数**，存储时被截断，运算结果的末尾会累积误差。这不是 Java 的问题，几乎所有语言都有这个问题（用 Python 试试 `0.1 + 0.2`，结果一样）。
> - **解决方案（重要！）**：
>   - **金额计算**绝不能用 `float` 或 `double`，必须用 **`BigDecimal`**：
>     ```java
>     import java.math.BigDecimal;
>     BigDecimal a = new BigDecimal("0.1");  // 用字符串构造！
>     BigDecimal b = new BigDecimal("0.2");
>     System.out.println(a.add(b));          // 0.3（精确）
>     ```
>   - 判断两个浮点数是否"相等"时，用差值绝对值小于一个极小值：
>     ```java
>     double a = 0.1 + 0.2;
>     boolean roughlyEqual = Math.abs(a - 0.3) < 0.0000001;
>     ```

### 2.1.6 var 关键字（Java 10+）

从 Java 10 开始，你可以使用 `var` 关键字让编译器**自动推断**局部变量的类型。注意：`var` 不是动态类型——变量一旦推断出类型，就终生不变。

```java
var name = "Alice";        // 编译器推断为 String
var age = 25;              // 编译器推断为 int
var list = new ArrayList<String>(); // 编译器推断为 ArrayList<String>

name = "Bob";              // ✅ 可以，还是 String
name = 123;                // ❌ 编译错误！name 已被推断为 String
```

这个 `var` 与 JavaScript 的 `var` **完全不同**。JavaScript 的 `var` 是动态类型，可以随时赋不同类型的值；Java 的 `var` 只是让编译器帮你补全类型声明，本质还是强类型。

`var` 只能在**局部变量**中使用（方法内声明的变量），不能用于类的成员变量、方法参数、方法返回类型。

### 2.1.7 命名规范

Java 社区的命名规范非常统一，这有助于团队协作和代码可读性：

| 元素 | 规范 | 示例 |
|------|------|------|
| 包名（package） | 全小写，点分隔 | `com.example.user` |
| 类名（class） | **大驼峰**（PascalCase） | `HelloWorld`, `UserService` |
| 方法名 | **小驼峰**（camelCase） | `getUserName()`, `findById()` |
| 变量名 | **小驼峰** | `userName`, `totalCount` |
| 常量 | **全大写 + 下划线** | `MAX_SIZE`, `DEFAULT_PORT` |

核心原则：**见名知意**。`int a;` 不如 `int age;`，`String s;` 不如 `String userName;`。

---

## 2.2 运算符

### 2.2.1 算术运算符

| 运算符 | 含义 | 示例 | 结果 |
|--------|------|------|------|
| `+` | 加法（或字符串拼接） | `5 + 3` | `8` |
| `-` | 减法 | `5 - 3` | `2` |
| `*` | 乘法 | `5 * 3` | `15` |
| `/` | 除法 | `10 / 3` | `3`（⚠️ 整数除法截断！） |
| `%` | 取模（求余数） | `10 % 3` | `1` |

> 🚨 **坑点：整数除法截断——`10 / 3 = 3` 而不是 `3.333...`**
>
> - **现象**：
>   ```java
>   int a = 10;
>   int b = 3;
>   System.out.println(a / b);  // 输出 3，不是 3.333...
>   ```
> - **原因**：两个 `int` 做除法运算时，结果是 `int`，小数部分被**直接截断（不是四舍五入）**。
> - **正确做法**：想要得到小数结果，至少有一个操作数是浮点数：
>   ```java
>   System.out.println(10.0 / 3);    // 3.3333333333333335
>   System.out.println(10 / 3.0);    // 3.3333333333333335
>   System.out.println((double) 10 / 3); // 3.3333333333333335
>   ```

取模运算符 `%` 常用于判断奇偶性、循环数组索引、计算时间等场景：

```java
System.out.println(7 % 2);    // 1（7 是奇数）
System.out.println(17 % 5);   // 2（17 / 5 = 3 余 2）
System.out.println(10 % 2);   // 0（10 是偶数）
```

### 2.2.2 关系运算符

关系运算符的结果是 `boolean` 类型（`true` 或 `false`）：

| 运算符 | 含义 |
|--------|------|
| `==` | 等于 |
| `!=` | 不等于 |
| `>` | 大于 |
| `<` | 小于 |
| `>=` | 大于等于 |
| `<=` | 小于等于 |

需要特别注意：在 Java 中，`==` 和 `!=` 对于**基本类型**和**引用类型**的行为完全不同——这将在 2.3 节详细展开。

### 2.2.3 逻辑运算符与短路机制

| 运算符 | 含义 | 短路？ |
|--------|------|--------|
| `&&` | 逻辑与（AND） | ✅ 短路：左边为 false 时，右边不执行 |
| `||` | 逻辑或（OR） | ✅ 短路：左边为 true 时，右边不执行 |
| `!` | 逻辑非（NOT） | — |
| `&` | 逻辑与（不短路） | ❌ 两边都执行 |
| `|` | 逻辑或（不短路） | ❌ 两边都执行 |

**短路**意味着：如果根据左边的结果就能确定整个表达式的值，右边就不会被执行。这是非常重要的性能和安全特性。

> 🚨 **坑点：`&` vs `&&`——短路与非短路的生死区别**
>
> - **现象**：下面的代码用 `&` 会**抛出 NullPointerException**，用 `&&` 则安全通过。
>   ```java
>   String s = null;
>   if (s != null && s.length() > 0) {  // ✅ && 短路：s为null时不执行右边
>       System.out.println("字符串非空");
>   }
>   if (s != null & s.length() > 0) {   // ❌ & 不短路：s为null时仍执行右边 → NPE！
>       System.out.println("字符串非空");
>   }
>   ```
> - **原因**：`&&` 发现 `s != null` 是 `false` 后，整个 AND 的结果已经确定为 `false`，所以**跳过**了 `s.length()`。`&` 没有这个优化，它会**强行执行**右边的表达式，导致对 `null` 调用 `.length()`，抛出 `NullPointerException`。
> - **正确做法**：**99% 的场景使用 `&&` 和 `||`（短路版）**。`&` 和 `|` 在不短路的逻辑场景下基本没有实际用途（它们是位运算符，见 2.2.6）。

### 2.2.4 赋值运算符

| 运算符 | 等价于 |
|--------|--------|
| `=` | 直接赋值 |
| `+=` | `x = x + 右值` |
| `-=` | `x = x - 右值` |
| `*=` | `x = x * 右值` |
| `/=` | `x = x / 右值` |
| `%=` | `x = x % 右值` |

复合赋值运算符不仅写起来简洁，还包含了**隐式强制类型转换**：

```java
byte b = 10;
b = b + 5;      // ❌ 编译错误！b + 5 结果是 int，不能赋给 byte
b += 5;         // ✅ 正确！隐式转型 b = (byte)(b + 5);
System.out.println(b); // 15
```

### 2.2.5 三元运算符

三元运算符（条件运算符）是 `if-else` 的简写形式：

```java
数据类型 变量 = 条件表达式 ? 值1 : 值2;
```

```java
int score = 85;
String result = score >= 60 ? "及格" : "不及格";
System.out.println(result); // 及格

int max = (a > b) ? a : b;  // 取两个数中的最大值
```

三元运算符可以嵌套，但**嵌套超过两层会严重降低可读性**，建议拆成 `if-else` 语句。

### 2.2.6 位运算符（理解即可）

位运算符直接操作二进制位，在底层开发、权限控制、高性能计算等场景会用到：

| 运算符 | 含义 | 示例 |
|--------|------|------|
| `&` | 按位与 | `5 & 3 = 1`（`101 & 011 = 001`） |
| `|` | 按位或 | `5 | 3 = 7`（`101 | 011 = 111`） |
| `^` | 按位异或 | `5 ^ 3 = 6`（`101 ^ 011 = 110`） |
| `~` | 按位取反 | `~5 = -6` |
| `<<` | 左移（每移一位相当于×2） | `5 << 1 = 10` |
| `>>` | 右移（每移一位相当于÷2，保留符号） | `10 >> 1 = 5` |
| `>>>` | 无符号右移（高位补0） | `-1 >>> 1 = 2147483647` |

**典型应用——权限位判断：**

```java
int READ    = 1 << 0;  // 0001（十进制 1）
int WRITE   = 1 << 1;  // 0010（十进制 2）
int EXECUTE = 1 << 2;  // 0100（十进制 4）

int userPermission = READ | WRITE;  // 0011，用户有读和写权限

boolean canRead    = (userPermission & READ) != 0;    // true
boolean canExecute = (userPermission & EXECUTE) != 0; // false
```

### 2.2.7 运算符优先级速查

当表达式中有多个运算符时，优先级决定计算顺序。以下从高到低列出常用运算符：

```
1. ()          括号 — 最高优先级
2. ! ~ ++ --   一元运算符
3. * / %       乘除取模
4. + -         加减
5. << >> >>>   移位
6. < > <= >=   关系比较
7. == !=       相等判断
8. &           按位与
9. ^           按位异或
10. |          按位或
11. &&         逻辑与（短路）
12. ||         逻辑或（短路）
13. ?:         三元运算符
14. = += -= *= 赋值 — 最低优先级
```

**口诀**：记不住优先级就用**括号**。`(a + b) * c` 比 `a + b * c` 清晰一万倍。

---

## 2.3 `==` vs `equals()`——本章最重要的知识点

这是 Java 面试中最常被问到的基础问题之一。我们来分层次彻底讲清楚。

### 2.3.1 第一层：`==` 永远比较"栈中的值"

Java 内存粗略分为**栈（Stack）**和**堆（Heap）**：
- **基本类型**的变量名和值都在**栈**中
- **引用类型**的变量名在**栈**中，变量名保存的是一个指向**堆**中对象的地址

`==` 做的事情只有一件：**比较栈中存储的值是否相等。**

```java
// 基本类型：栈中存的就是数值本身
int a = 100;
int b = 100;
System.out.println(a == b);  // true — "100 == 100"，数值相等

// 引用类型：栈中存的是对象的地址
String s1 = new String("hello");
String s2 = new String("hello");
System.out.println(s1 == s2); // false — 两个对象在堆中的地址不同！
```

在第二个例子中，`s1` 和 `s2` 这两个变量各自存储了**不同的堆地址**（因为 `new` 了两次，创建了两个 String 对象），尽管两个对象的**内容**都是 `"hello"`，但它们的地址不同，所以 `==` 返回 `false`。

### 2.3.2 第二层：`equals()` 的默认行为就是 `==`

`equals()` 是 `Object` 类定义的方法。所有 Java 类都继承自 `Object`，而 `Object` 中 `equals()` 的默认实现就是：

```java
// Object 类中的 equals 方法（源码简化版）
public boolean equals(Object obj) {
    return (this == obj);  // 默认就是比较地址！
}
```

所以，**如果一个类没有重写 `equals()`，那么 `equals()` 的行为与 `==` 完全一样**。

### 2.3.3 第三层：String 重写了 `equals()`

`String` 类是 Java 中少数重写了 `equals()` 方法的类——它不再比较地址，而是**比较两个字符串的内容是否相同**。

```java
String s1 = new String("hello");
String s2 = new String("hello");
System.out.println(s1 == s2);       // false — 不同对象，地址不同
System.out.println(s1.equals(s2));  // true — String.equals() 比较了内容！
```

### 2.3.4 第四层：字符串常量池——`==` 的"定时炸弹"

Java 有一个**字符串常量池（String Pool）**的机制：

```java
String a = "hello";              // 在常量池中创建 "hello"
String b = "hello";              // 常量池中已有 "hello"，直接复用！
String c = new String("hello");  // 强制在堆中创建新对象

System.out.println(a == b);      // true  — a 和 b 指向常量池中同一个对象！
System.out.println(a == c);      // false — c 指向堆中单独创建的对象
System.out.println(a.equals(c)); // true  — equals() 比较内容，内容相同
```

用一张图来表示内存布局：

```
        栈                          堆                          字符串常量池
   ┌──────────┐              ┌───────────────┐              ┌───────────────┐
   │  a  ─────┼──────────────┼───────────────┼─────────────→│   "hello"     │
   │  b  ─────┼──────────────┼───────────────┼──────────────│   (同一个)     │
   │  c  ─────┼──────┐       │               │              └───────────────┘
   └──────────┘      │       │  ┌─────────┐  │
                     └───────┼─→│ "hello" │  │
                             │  └─────────┘  │
                             └───────────────┘
```

> 🚨 **坑点：用 `==` 比较两个 String 的内容——"运气测试"**
>
> - **现象**：
>   ```java
>   String s1 = "hello";
>   String s2 = "hello";
>   System.out.println(s1 == s2);  // true — "运气好"，常量池复用
>
>   String s3 = new String("hello");
>   String s4 = new String("hello");
>   System.out.println(s3 == s4);  // false — "运气差"，两个新对象
>   ```
> - **结论**：如果你用 `==` 比较字符串内容，你的程序有时候正确（常量池命中），有时候错误（new 新对象）。这写出来的不是代码，是**赌博**。
> - **正确做法**：**永远用 `equals()` 比较字符串内容**。这是铁律。
> - **面试标准回答**：当面试官问"`==` 和 `equals` 有什么区别？"时，你的回答结构应该是：
>   1. `==` 比较栈中的值：基本类型比较数值，引用类型比较地址
>   2. `equals()` 是 `Object` 的方法，默认实现就是 `==`
>   3. `String` 等类重写了 `equals()`，比较的是内容
>   4. 结合字符串常量池说明 `==` 在比较字符串时的不可靠性

---

## 2.4 流程控制

### 2.4.1 if-else

`if-else` 是任何编程语言的基础控制结构，Java 的写法与 C/C++ 完全相同：

```java
if (条件表达式) {
    // 条件为 true 时执行
} else if (另一个条件) {
    // 上一个条件为 false，这个条件为 true 时执行
} else {
    // 所有条件都为 false 时执行
}
```

```java
public class IfElseDemo {
    public static void main(String[] args) {
        int score = 85;

        if (score >= 90) {
            System.out.println("优秀");
        } else if (score >= 80) {
            System.out.println("良好");
        } else if (score >= 60) {
            System.out.println("及格");
        } else {
            System.out.println("不及格");
        }
    }
}
```

> 🚨 **坑点：悬空 else——缺少大括号时 else 匹配最近的 if**
>
> - **现象**：以下代码输出的是什么？
>   ```java
>   int x = 10;
>   if (x > 5)
>       if (x > 8)
>           System.out.println("A");
>   else
>       System.out.println("B");  // 这个 else 匹配的是哪个 if？
>   ```
>   输出是 `"A"`。`else` 匹配的是最近的、没有 `else` 的 `if`（即 `if (x > 8)`），而不是 `if (x > 5)`。所以当 `x=10` 时，`x > 5` 为 true 进入外层，`x > 8` 也为 true 输出 A，内层 else 不执行。
> - **正确做法**：**永远加大括号**，即使 if/else 后面只有一行代码：
>   ```java
>   if (x > 5) {
>       if (x > 8) {
>           System.out.println("A");
>       }
>   } else {
>       System.out.println("B");  // 意图明确！
>   }
>   ```

### 2.4.2 switch 语句

Java 的 switch 经历了重大升级。我们先看**传统写法**，再看 **Java 14+ 增强写法**。

**传统 switch（有穿透风险）：**

```java
int day = 3;
String dayName;

switch (day) {
    case 1:
        dayName = "星期一";
        break;  // ⚠️ 每个 case 末尾必须加 break！
    case 2:
        dayName = "星期二";
        break;
    case 3:
        dayName = "星期三";
        break;
    default:
        dayName = "未知";
        break;
}

System.out.println(dayName);  // 星期三
```

> 🚨 **坑点：switch 的 fall-through（穿透）——忘记 break 的后果**
>
> - **现象**：如果把上面代码中 `case 3:` 的 `break` 删掉，当 `day=3` 时，程序会从 `case 3` 进入，执行 `dayName = "星期三"`，然后**继续执行** `default` 的代码，最终 `dayName` 变成 `"未知"`。
> - **原因**：switch 的 fall-through 机制：一旦匹配成功，会**顺序执行**后面所有 case 的代码，直到遇到 `break` 或 `switch` 结束。
> - **什么时候故意用穿透**：极少数情况下，多个 case 共享同一段逻辑，需要显式加注释说明：
>   ```java
>   case 1:
>   case 2:
>   case 3:
>       System.out.println("第一季度");
>       break; // 三个 case 共享，有意穿透
>   ```
> - **正确做法**：**每个 case 末尾都加 break**，除非你非常清楚自己在做什么并已加注释。

**Java 14+ 增强 switch（箭头语法）：**

```java
int day = 3;
String dayName = switch (day) {
    case 1 -> "星期一";
    case 2 -> "星期二";
    case 3 -> "星期三";
    case 4, 5 -> "星期四或五";  // 多 case 合并
    default  -> "未知";
};

System.out.println(dayName);  // 星期三
```

箭头语法（`->`）的好处：
1. **不需要 `break`**——不会穿透
2. 多个 case 可以直接用逗号合并：`case 4, 5 ->`
3. 它是一个**表达式**，可以返回值（如上例中直接赋值）

**使用 `yield` 返回值（当 case 中有多行逻辑时）：**

```java
String result = switch (score / 10) {
    case 10, 9 -> "优秀";
    case 8 -> "良好";
    case 7 -> {
        String grade = "中等";
        yield grade;  // yield 用于返回多行逻辑的结果
    }
    default -> "需努力";
};
```

> 🚨 **坑点：switch 支持的类型有限**
>
> switch 表达式/语句中的条件变量必须是以下类型之一：
> - `byte`、`short`、`char`、`int`（及其包装类）
> - `String`（Java 7+）
> - `enum` 枚举类型
> - **不支持**：`long`、`float`、`double`、`boolean`
>
> 如果你试图用 switch 匹配 `long` 或 `double` 值，编译器会直接报错。

### 2.4.3 for 循环

Java 的 for 循环有两种形式：

**传统 for 循环：**

```java
for (初始化; 条件; 更新) {
    // 循环体
}
```

```java
for (int i = 0; i < 5; i++) {
    System.out.println("i = " + i);
}
// 输出：
// i = 0
// i = 1
// i = 2
// i = 3
// i = 4
```

三个表达式都可以省略（但分号不能省），例如 `for(;;)` 就是无限循环。

**增强 for-each 循环（Java 5+）：**

```java
for (元素类型 变量名 : 数组或集合) {
    // 使用变量名访问每个元素
}
```

```java
int[] numbers = {10, 20, 30, 40, 50};
for (int num : numbers) {
    System.out.println(num);
}
```

for-each 语法简洁，没有下标越界的风险，但有局限：

> 🚨 **坑点：for-each 不能修改基本类型数组的元素值**
>
> - **现象**：
>   ```java
>   int[] arr = {1, 2, 3};
>   for (int x : arr) {
>       x = x * 2;  // 修改的是局部变量 x，不是数组元素！
>   }
>   System.out.println(arr[0]);  // 仍然是 1，没有被修改
>   ```
> - **原因**：for-each 循环中 `x` 是每次取出的元素的**副本**（基本类型值拷贝），修改 `x` 不会影响原数组。对于引用类型数组（如 `String[]`），你可以通过 `x` 修改对象内部的属性（因为 `x` 和数组元素指向同一个堆对象），但**不能替换引用本身**。
> - **正确做法**：如果需要修改数组元素，使用传统 for 循环：
>   ```java
>   for (int i = 0; i < arr.length; i++) {
>       arr[i] = arr[i] * 2;
>   }
>   ```

### 2.4.4 while 与 do-while

```java
// while：先判断，后执行（可能一次都不执行）
int i = 0;
while (i < 5) {
    System.out.println(i);
    i++;
}

// do-while：先执行，后判断（至少执行一次）
int j = 0;
do {
    System.out.println(j);
    j++;
} while (j < 5);
```

两者在大多数场景下可以互换，唯一的区别是 `do-while` **保证循环体至少执行一次**。这在"先问用户是否继续，再决定是否循环"的场景中非常有用。

### 2.4.5 break 与 continue

| 关键字 | 作用 |
|--------|------|
| `break` | **终止**当前循环，跳到循环后的语句 |
| `continue` | **跳过**本次循环的剩余代码，进入下一次迭代 |

**带标签的 break/continue（跳出多层循环）：**

```java
public class LabeledBreakDemo {
    public static void main(String[] args) {
        outer:  // 标签名可以自定义
        for (int i = 1; i <= 3; i++) {
            for (int j = 1; j <= 3; j++) {
                if (i == 2 && j == 2) {
                    break outer;  // 跳出外层循环，不再执行任何迭代
                }
                System.out.println("i=" + i + ", j=" + j);
            }
        }
        System.out.println("循环结束");
    }
}
```

输出：

```
i=1, j=1
i=1, j=2
i=1, j=3
i=2, j=1
循环结束
```

当 `i=2, j=2` 时，`break outer` 直接跳出了整个外层循环。这是 Java 中跳出多层嵌套最干净的方式。

---

## 2.5 数组

### 2.5.1 数组的声明与初始化

Java 数组是一个**固定长度**、**同类型**元素的**引用类型**对象。有两种声明语法：

```java
int[] arr1;    // 推荐：类型后面跟方括号
int arr2[];    // 也可以，但不推荐（C语言风格）
```

**静态初始化**（声明时直接赋值）：

```java
int[] scores = {95, 88, 76, 92, 84};  // 长度自动推断为 5
String[] names = {"张三", "李四", "王五"};
```

**动态初始化**（先指定长度，再逐个赋值）：

```java
int[] scores = new int[5];    // 创建长度为5的数组，默认值全为 0
scores[0] = 95;
scores[1] = 88;
scores[2] = 76;
scores[3] = 92;
scores[4] = 84;
```

不同元素类型的数组默认值：

| 数组元素类型 | 默认值 |
|-------------|--------|
| `byte[]` / `short[]` / `int[]` / `long[]` | `0` |
| `float[]` / `double[]` | `0.0` |
| `char[]` | `'\u0000'`（空字符） |
| `boolean[]` | `false` |
| 引用类型数组（如 `String[]`） | `null` |

### 2.5.2 length 属性

```java
int[] arr = {10, 20, 30, 40, 50};
System.out.println(arr.length);  // 5
```

> 🚨 **坑点：`length` 是属性不是方法——后面不加括号**
>
> - **现象**：
>   ```java
>   int[] arr = {1, 2, 3};
>   System.out.println(arr.length());  // ❌ 编译错误！
>   ```
> - **原因**：`length` 是数组对象的**成员属性**（field），不是一个方法。这与 `String` 的 `length()` 不同——`"hello".length()` 是方法（有括号），`arr.length` 是属性（无括号）。这是 Java 设计的不一致之处，也是初学者最容易搞混的地方。
> - **记忆技巧**：数组 `.length`（无括号），字符串 `.length()`（有括号），集合 `.size()`（有括号）。

### 2.5.3 数组的四种遍历方式

```java
int[] arr = {10, 20, 30, 40, 50};

// 方式1：传统 for（可以获取索引，可以修改元素）
for (int i = 0; i < arr.length; i++) {
    System.out.println("arr[" + i + "] = " + arr[i]);
}

// 方式2：增强 for-each（简洁，但不能获取索引）
for (int num : arr) {
    System.out.println(num);
}

// 方式3：Arrays.toString() 快速打印（调试专用）
import java.util.Arrays;
System.out.println(Arrays.toString(arr));  // [10, 20, 30, 40, 50]

// 方式4：Java 8+ Stream + forEach
import java.util.Arrays;
Arrays.stream(arr).forEach(System.out::println);
```

> 🚨 **坑点：ArrayIndexOutOfBoundsException——数组下标越界**
>
> - **现象**：
>   ```java
>   int[] arr = new int[5];
>   arr[5] = 100;  // ❌ 运行时：ArrayIndexOutOfBoundsException
>   ```
> - **原因**：数组长度为 5，有效下标是 `0~4`。访问 `arr[5]` 或 `arr[-1]` 都会抛出此异常。
> - **正确做法**：遍历数组时，循环条件永远写成 `i < arr.length`（不是 `i <= arr.length`）。

### 2.5.4 多维数组

Java 的二维数组本质是"数组的数组"——每一行可以有不同的列数：

```java
// 规则二维数组：3行4列
int[][] matrix = new int[3][4];
matrix[0][0] = 1;
matrix[1][2] = 5;

// 静态初始化
int[][] matrix2 = {
    {1, 2, 3},
    {4, 5, 6},
    {7, 8, 9}
};

// 不规则的"锯齿数组"：每行列数不同
int[][] jagged = {
    {1, 2},
    {3, 4, 5},
    {6}
};

// 遍历
for (int i = 0; i < jagged.length; i++) {
    for (int j = 0; j < jagged[i].length; j++) {
        System.out.print(jagged[i][j] + " ");
    }
    System.out.println();
}
```

### 2.5.5 Arrays 工具类

`java.util.Arrays` 提供了大量操作数组的静态方法：

```java
import java.util.Arrays;

public class ArraysDemo {
    public static void main(String[] args) {
        int[] arr = {5, 2, 8, 1, 9};

        // 排序
        Arrays.sort(arr);
        System.out.println(Arrays.toString(arr));  // [1, 2, 5, 8, 9]

        // 二分查找（数组必须先排序！）
        int index = Arrays.binarySearch(arr, 5);
        System.out.println("5 的位置：" + index);    // 2

        // 拷贝
        int[] copied = Arrays.copyOf(arr, arr.length);
        System.out.println(Arrays.toString(copied)); // [1, 2, 5, 8, 9]

        // 部分拷贝
        int[] subArray = Arrays.copyOfRange(arr, 1, 3);
        System.out.println(Arrays.toString(subArray)); // [2, 5]

        // 填充
        int[] filled = new int[5];
        Arrays.fill(filled, 42);
        System.out.println(Arrays.toString(filled));  // [42, 42, 42, 42, 42]

        // 比较两个数组
        int[] a = {1, 2, 3};
        int[] b = {1, 2, 3};
        System.out.println(Arrays.equals(a, b));      // true（逐个元素比较）
    }
}
```

### 2.5.6 综合练习：冒泡排序

冒泡排序是学习数组和循环的综合练习题。它的原理是：每一轮遍历，将当前未排序部分的最大值"冒泡"到末尾：

```java
import java.util.Arrays;

public class BubbleSort {
    public static void main(String[] args) {
        int[] arr = {64, 34, 25, 12, 22, 11, 90};

        System.out.println("排序前：" + Arrays.toString(arr));

        // 冒泡排序
        for (int i = 0; i < arr.length - 1; i++) {         // 外层：比较的轮数
            boolean swapped = false;                       // 优化：如果本轮无交换，提前结束
            for (int j = 0; j < arr.length - 1 - i; j++) { // 内层：每轮比较
                if (arr[j] > arr[j + 1]) {                 // 相邻元素比较
                    int temp = arr[j];                     // 交换
                    arr[j] = arr[j + 1];
                    arr[j + 1] = temp;
                    swapped = true;
                }
            }
            if (!swapped) {                                // 本轮没有发生任何交换
                break;                                     // 数组已经有序，提前结束
            }
        }

        System.out.println("排序后：" + Arrays.toString(arr));
        // 输出：[11, 12, 22, 25, 34, 64, 90]
    }
}
```

逐行解释：
1. **外层循环** `i`：控制比较的**轮数**。长度为 7 的数组需要 6 轮比较（最后一个元素自动就位）。
2. **内层循环** `j`：控制每轮中**相邻比较的次数**。每过一轮，最后 i 个元素已经排好序，不需要再比较，因此 `j < arr.length - 1 - i`。
3. **`swapped` 优化**：如果某一轮没有任何交换，说明数组已经有序，可以提前退出。这使最好情况（已排序数组）的时间复杂度从 O(n²) 降为 O(n)。

---

## 本章小结

- **强类型语言**：Java 变量必须先声明类型，类型终生不变。八种基本类型中，整数用 `int`，小数用 `double`。
- **类型转换**：小→大自动提升（`byte→short→int→long→float→double`）；大→小需强转（`(目标类型)`），注意精度丢失和溢出风险。
- **常见数值陷阱**：`float` 要加 `f` 后缀；整数溢出是环形；浮点小数 `0.1+0.2 ≠ 0.3`，金额必须用 `BigDecimal`。
- **`var` 关键字**：仅用于局部变量类型推断，本质仍是强类型，与 JavaScript 的 `var` 完全不同。
- **运算符**：注意整数除法截断（`10/3=3`）、短路 `&&` 与不短路 `&` 的区别（99% 场景用 `&&`）。
- **`==` vs `equals()`**：`==` 比较栈中的值（基本类型比数值，引用类型比地址），`equals()` 默认就是 `==`，`String` 重写了 `equals()` 比较内容。**永远用 `equals()` 比较字符串内容。**
- **流程控制**：`if-else` 加大括号防悬空；`switch` 注意 break（Java 14+ 箭头语法无需 break）；`for-each` 不能修改基本类型数组元素。
- **数组**：`length` 是属性不加括号；下标从 0 到 `length-1`。`Arrays` 工具类提供排序、查找、拷贝等常用操作。

---

## 思考题

### 题 1

为什么 `BigDecimal` 推荐用 `String` 构造器（`new BigDecimal("0.1")`）而不是 `double` 构造器（`new BigDecimal(0.1)`）？

<details>
<summary>点击查看答案</summary>

因为 `new BigDecimal(0.1)` 中的 `0.1` 字面量首先会被 Java 解释为 `double` 类型的值，而 `0.1` 在 `double` 中已经是**不精确**的（二进制无限循环小数）。构造器拿到的是那个已经产生了误差的 `double` 值，所以结果也是不精确的。

当你用 `new BigDecimal("0.1")` 时，`BigDecimal` 直接解析字符串 `"0.1"`，精确地按照十进制表示来构建数值，不会有任何误差。

验证代码：

```java
System.out.println(new BigDecimal(0.1));
// 输出：0.1000000000000000055511151231257827021181583404541015625

System.out.println(new BigDecimal("0.1"));
// 输出：0.1（精确！）
```

</details>

### 题 2

以下代码输出什么？为什么？

```java
Integer a = 127;
Integer b = 127;
System.out.println(a == b);  // ?

Integer c = 128;
Integer d = 128;
System.out.println(c == d);  // ?
```

<details>
<summary>点击查看答案</summary>

```
true
false
```

原因：Java 为 `Integer` 类型设计了一个**缓存机制**。`Integer.valueOf()` 方法（自动装箱底层调用它）会将 -128 到 127 之间的 `Integer` 对象**缓存起来**，重复使用。

- `Integer a = 127` → 自动装箱 → `Integer.valueOf(127)` → 命中缓存 → 返回缓存中的对象
- `Integer b = 127` → 同样命中缓存 → 返回**同一个**对象
- 所以 `a == b` 为 `true`（因为它们指向同一个缓存对象）

- `Integer c = 128` → 128 超出缓存范围 → 创建新 `Integer` 对象
- `Integer d = 128` → 同样创建新对象
- 所以 `c == d` 为 `false`（不同的对象，地址不同）

这进一步印证了：**永远用 `equals()` 比较引用类型的内容，不要用 `==`**。

</details>

### 题 3

下列代码会导致什么问题？如何修正？

```java
String s = null;
if (s.equals("hello")) {
    System.out.println("匹配");
}
```

<details>
<summary>点击查看答案</summary>

会导致 **NullPointerException（空指针异常）**，因为对 `null` 调用 `.equals()` 方法。

修正方案（任选其一）：

方案 1 — 反转调用方（推荐）：
```java
if ("hello".equals(s)) {  // 字符串常量调用 equals，永远不会 NPE
    System.out.println("匹配");
}
```

方案 2 — 先判空：
```java
if (s != null && s.equals("hello")) {  // 短路 && 保护
    System.out.println("匹配");
}
```

</details>

### 题 4

下面两段代码在遍历过程中有什么区别？哪段能正确地将每个元素乘以 2？

```java
// 代码A
int[] arr = {1, 2, 3, 4, 5};
for (int i = 0; i < arr.length; i++) {
    arr[i] = arr[i] * 2;
}

// 代码B
int[] arr = {1, 2, 3, 4, 5};
for (int x : arr) {
    x = x * 2;
}
```

<details>
<summary>点击查看答案</summary>

- **代码 A** 能正确修改：通过索引 `arr[i]` 直接操作数组元素，每个元素都被乘以 2，最终数组变为 `{2, 4, 6, 8, 10}`。
- **代码 B** 不能修改：`for-each` 中的 `x` 是数组元素的**值拷贝**（对基本类型而言），修改 `x` 只改变了局部变量，不影响原数组。最终数组仍然是 `{1, 2, 3, 4, 5}`。

总结：需要**修改数组元素**时，使用传统 `for` 循环（通过索引）。只**读取元素**时，使用 `for-each`（更简洁安全）。

</details>

### 题 5

请解释 `switch` 语句中"穿透"（fall-through）现象，并用代码示范**有意利用穿透**的场景。

<details>
<summary>点击查看答案</summary>

"穿透"是指：当 `switch` 匹配到一个 `case` 后，如果没有遇到 `break`，程序会**继续执行**后续所有 `case` 的代码，直到遇到 `break` 或 `switch` 结束。

有意利用穿透的场景——同一段逻辑适用于多个 `case`：

```java
public class SwitchFallThrough {
    public static void main(String[] args) {
        int month = 3;  // 3月

        switch (month) {
            case 12:
            case 1:
            case 2:
                System.out.println("冬季");
                break; // 上面三个 case 共享，穿透到此结束
            case 3:
            case 4:
            case 5:
                System.out.println("春季");
                break;
            case 6:
            case 7:
            case 8:
                System.out.println("夏季");
                break;
            case 9:
            case 10:
            case 11:
                System.out.println("秋季");
                break;
            default:
                System.out.println("无效月份");
        }
    }
}
```

在 Java 14+ 中，同一场景用箭头语法更清晰：
```java
String season = switch (month) {
    case 12, 1, 2  -> "冬季";
    case 3, 4, 5   -> "春季";
    case 6, 7, 8   -> "夏季";
    case 9, 10, 11 -> "秋季";
    default         -> "无效月份";
};
```

</details>

---

> 🚀 **EMS v1 项目预告**
>
> 恭喜你完成了 Java 基础语法的学习！你已经掌握了变量、运算符、流程控制和数组——这些是构建任何 Java 程序的地基。
>
> 在接下来的第 3~7 章中，你将进入 Java 最核心的领域：**面向对象编程、集合框架、异常处理、IO 流和多线程**。学完这些后，我们将一起实现 **EMS v1：一个命令行版的员工管理系统**。
>
> 想象一下：你可以用纯 Java 编写一个程序，在命令行中录入员工信息、按部门查询、计算薪资统计，甚至将数据持久化到文件。这些代码将综合运用你学到的每一点知识，是一个完美的阶段成果检验。
>
> 准备好了吗？让我们继续前进！

---

> **下一章预告**：在第 3 章中，你将学习 Java 最核心的编程思想——**面向对象编程（OOP）**：类与对象、封装、构造方法、`static` 关键字和包——这些是 Java 程序员的"母语"。