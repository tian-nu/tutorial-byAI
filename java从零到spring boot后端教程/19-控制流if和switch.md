# 第19章 · 控制流：if和switch

> "马路上的车不能只往一个方向开——看到红灯要停，绿灯要行。程序也一样，不能只会'一条路走到底'。if-else给程序装上了'红绿灯'，switch则像高速公路的分岔口——根据不同的情况走不同的路。"

---

## 19.1 if：最简单的判断

```java
if (条件) {
    // 条件为true时执行
}
```

**条件必须是 `boolean` 类型**。Java不允许用整数代替布尔值：

```java
int score = 85;
if (score > 60) {          // ✅ score > 60 的结果是boolean
    System.out.println("及格");
}

// if (score) { ... }      // ❌ 编译错误！score是int不是boolean
// Java不能像C语言那样写 if(1) 或 if(0)
```

---

## 19.2 if-else：二选一

```java
int score = 85;
if (score >= 60) {
    System.out.println("及格");
} else {
    System.out.println("不及格");
}
```

if-else是一个整体——**要么走if分支，要么走else分支，不可能两个都走**。

---

## 19.3 if-else if-else：多选一

```java
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
```

**执行逻辑**：从上到下依次检查每个条件，遇到第一个 `true` 就执行那个分支里的代码，然后**跳过后面所有分支**。

### 顺序的重要性

```java
// ❌ 错误顺序：永远不会打印"优秀"
if (score >= 60) {
    System.out.println("及格");    // 任何>=60的分数都进这里
} else if (score >= 90) {
    System.out.println("优秀");    // 永远到不了这里！
}

// ✅ 正确顺序：从高到低
if (score >= 90) {
    System.out.println("优秀");
} else if (score >= 60) {
    System.out.println("及格");
}
```

> ❌ **常见错误**：把最宽松的条件放在前面。记住：条件应该从最严格到最宽松排列。

---

## 19.4 嵌套if：判断里的判断

```java
int age = 20;
boolean hasTicket = true;

if (age >= 18) {
    if (hasTicket) {
        System.out.println("可以入场");
    } else {
        System.out.println("请先购票");
    }
} else {
    System.out.println("未成年人不得入内");
}
```

嵌套可以多层，但太深的嵌套会让代码难以阅读。一般超过3层就应该考虑重构（比如提前return、提取方法等）。

---

## 19.5 花括号可以省略吗？

如果if或else后面只有**一条语句**，花括号可以省略：

```java
if (score >= 60)
    System.out.println("及格");  // 只有一条，可以省花括号
else
    System.out.println("不及格");

// 但这样做很危险！
if (score >= 60)
    System.out.println("及格");
    System.out.println("恭喜你");  // 这一行不在if里面！总会执行！
```

> ❌ **常见错误**：省略花括号时，缩进欺骗了你的眼睛。第二行 `System.out.println("恭喜你")` 实际上不在if的作用域内。**强烈建议永远不要省略花括号**——即使只有一条语句。多打两个花括号能防止未来修改代码时引入Bug。

---

## 19.6 switch：多分支选择（老式语法）

当有很多种固定值需要判断时，if-else-if写起来很冗长。switch可以更清晰地处理这种情况：

```java
int dayOfWeek = 3;
switch (dayOfWeek) {
    case 1:
        System.out.println("星期一");
        break;
    case 2:
        System.out.println("星期二");
        break;
    case 3:
        System.out.println("星期三");
        break;
    case 4:
        System.out.println("星期四");
        break;
    case 5:
        System.out.println("星期五");
        break;
    case 6:
    case 7:
        System.out.println("周末");
        break;
    default:
        System.out.println("无效的星期");
}
```

### 坑：break不能忘！

老式switch有一个臭名昭著的特点——**fall-through（穿透）**：如果一个case最后没有写 `break`，程序会继续执行下一个case的代码：

```java
int num = 1;
switch (num) {
    case 1:
        System.out.println("一");  // 执行
        // 没有break！穿透！
    case 2:
        System.out.println("二");  // 也执行了！
        break;
    case 3:
        System.out.println("三");
        break;
}
// 输出：一
//       二
```

有意利用穿透时（比如上面的周末两个case），务必写注释说明。

> ❌ **常见错误**：写老式switch忘记break，导致出现莫名其妙的输出。每次写完case先写break作为习惯。

### switch支持的判断类型

老式switch支持：`byte`、`short`、`int`、`char`、`String`（Java 7+）、`enum`（枚举。此术语需进附录）。

---

## 19.7 新式switch表达式（Java 14+）：推荐

Java 14引入了一种全新的switch语法，用 `->` 箭头代替 `case ... break`，彻底杜绝了穿透问题：

```java
int dayOfWeek = 3;
String dayName = switch (dayOfWeek) {
    case 1 -> "星期一";
    case 2 -> "星期二";
    case 3 -> "星期三";
    case 4 -> "星期四";
    case 5 -> "星期五";
    case 6, 7 -> "周末";      // 多个值用逗号合并
    default -> "无效";
};
System.out.println(dayName);  // 星期三
```

**新语法的好处**：
1. **没有穿透**：每个 `case ->` 后面默认就是独立的，不需要break
2. **可作为表达式**：switch整体可以返回一个值赋给变量
3. **多个值合并**：`case 6, 7 ->` 比老式的穿透更清晰
4. **编译器强制覆盖**：如果漏了某个枚举值，编译报错（配合enum使用时）

### 多条语句时用花括号

```java
int score = 85;
String grade = switch (score / 10) {
    case 10, 9 -> "优秀";
    case 8 -> "良好";
    case 7, 6 -> "及格";
    default -> {
        if (score >= 0 && score < 60) {
            yield "不及格";
        } else {
            yield "无效分数";
        }
    }
};
```

`yield` 是Java 14引入的关键字，用于在switch表达式的花括号块中"返回"一个值。可以理解为switch块里的 `return`。

### 老式vs新式：一表对比

| 特性 | 老式 `case: break` | 新式 `case ->` |
|------|--------------------|-----------------|
| 穿透（fall-through） | 有（默认行为） | 没有 |
| 需要break | 是 | 否 |
| 可作为表达式返回值 | 否 | 是 |
| 多值合并 | 用穿透 `case 6: case 7:` | 直接写 `case 6, 7 ->` |
| 返回值关键字 | 无 | `yield` |

---

## 本章小结

| 知识点 | 核心要点 |
|--------|----------|
| if | 条件必须是boolean类型。单条件判断 |
| if-else | 二选一，两个分支互斥 |
| if-else if-else | 多选一，从上到下检查，命中即跳过余下 |
| 嵌套if | 判断里的判断。嵌套过深应重构 |
| 花括号 | 省略花括号有风险，强烈建议始终保留 |
| 老式switch | `case:` + `break`。会穿透，容易忘记break |
| 新式switch（Java 14+） | `case ->` 箭头语法。不穿透，可做表达式返回值，多值用逗号合并 |
| yield | 在switch花括号块中返回值。此术语需进附录 |

---

## 自测题

**1.** 以下代码会输出什么？

```java
int x = 10;
if (x > 5)
    System.out.print("A");
    System.out.print("B");
```

**2.** 以下switch代码的输出是什么？如果没有 `break` 会怎样？

```java
int n = 2;
switch (n) {
    case 1: System.out.print("一");
    case 2: System.out.print("二");
    case 3: System.out.print("三");
    default: System.out.print("其他");
}
```

**3.** 用Java 14的新式switch语法，将 `month`（1-12）转换为对应的季节字符串（3-5春、6-8夏、9-11秋、12/1/2冬）。

---

> 🚀 **下一章**：第20章 · 控制流for和while——程序有了判断力还不够，还得会"反复做同一件事"。循环是计算机最强大的能力：一秒算一亿次，人做不到的事情它能做。

---

[← 上一章：18-运算符](18-运算符/) | [下一章：20-控制流for和while →](20-控制流for和while/)