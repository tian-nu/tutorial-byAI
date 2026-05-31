# 第20章 · 控制流：for和while

> "洗一只碗只要5秒，洗1000只碗呢？手动洗要一个多小时，但程序循环洗0.005秒都不要。循环是计算机最可怕的能力——重复，精确，不知疲倦。"

---

## 20.1 for循环：三句话定义一个循环

for循环是Java里最常用的循环，它的语法是：

```java
for (初始化; 条件; 更新) {
    // 循环体
}
```

三句话各司其职：

| 部分 | 何时执行 | 作用 |
|------|----------|------|
| 初始化 | 循环开始前执行**一次** | 创建并初始化计数器 |
| 条件 | 每次迭代**开始前**检查 | 为true则继续，为false则结束 |
| 更新 | 每次迭代**结束后**执行 | 改变计数器（通常自增） |

### 标准示例：打印1到5

```java
for (int i = 1; i <= 5; i++) {
    System.out.println("第" + i + "次循环");
}
// 输出：
// 第1次循环
// 第2次循环
// 第3次循环
// 第4次循环
// 第5次循环
```

#### 执行过程推演

| 步骤 | 发生了什么 | i的值 | 条件 i<=5 |
|------|-----------|-------|-----------|
| 1 | 初始化 `int i = 1` | 1 | true → 执行循环体 |
| 2 | 更新 `i++` | 2 | true → 执行循环体 |
| 3 | 更新 `i++` | 3 | true → 执行循环体 |
| 4 | 更新 `i++` | 4 | true → 执行循环体 |
| 5 | 更新 `i++` | 5 | true → 执行循环体 |
| 6 | 更新 `i++` | 6 | false → 退出循环 |

### for循环的变体

```java
// 倒序循环
for (int i = 10; i >= 1; i--) {
    System.out.print(i + " ");
}
// 输出：10 9 8 7 6 5 4 3 2 1

// 步长不为1
for (int i = 0; i <= 100; i += 10) {
    System.out.print(i + " ");
}
// 输出：0 10 20 30 40 50 60 70 80 90 100

// 多个变量
for (int i = 0, j = 10; i < j; i++, j--) {
    System.out.println("i=" + i + " j=" + j);
}
// 输出：i=0 j=10   i=1 j=9   i=2 j=8   i=3 j=7   i=4 j=6

// 三部分都可以省略（死循环）
// for (;;) { ... }   ← 死循环！慎用
```

> ❌ **常见错误**：在条件里写 `i <= 5` 时，分号写错位置。`for (int i = 1; i <= 5; i++);` ——多了一个分号，循环体为空，后面的 `{...}` 只执行一次。这是最难排查的Bug之一。

---

## 20.2 增强for循环（for-each）：遍历集合的神器

Java 5引入的增强for循环，专门用来遍历数组或集合，不需要手动管理索引：

```java
int[] scores = {90, 85, 78, 92, 88};

// 传统for
for (int i = 0; i < scores.length; i++) {
    System.out.println(scores[i]);
}

// 增强for（更简洁，更安全）
for (int score : scores) {
    System.out.println(score);
}
```

**语法**：`for (元素类型 变量名 : 数组或集合) { 循环体 }`

**增强for的优点**：
- 不需要写数组长度 `scores.length`
- 不会出现索引越界错误
- 代码更短更清晰

**增强for的局限**：
- 不能修改数组元素（你拿到的是值拷贝）
- 不能获取当前索引（如果你需要知道"第几个"，就得用传统for）
- 不能反向遍历

```java
// 增强for不能改数组元素
for (int score : scores) {
    score = score + 10;  // 这改了局部变量score，不影响数组！
}
System.out.println(scores[0]);  // 还是90，没变

// 要修改元素，还是得用传统for
for (int i = 0; i < scores.length; i++) {
    scores[i] += 10;
}
```

---

## 20.3 while循环：条件为真就一直跑

while循环在每次执行循环体**之前**检查条件：

```java
int count = 0;
while (count < 5) {
    System.out.println("count = " + count);
    count++;
}
// 输出：0 1 2 3 4
```

**适用场景**：当你不确定要循环多少次时（比如"用户输入exit之前一直读"）：

```java
import java.util.Scanner;

Scanner scanner = new Scanner(System.in);
String input = "";
while (!input.equals("exit")) {
    System.out.print("请输入（输入exit退出）：");
    input = scanner.nextLine();
    System.out.println("你输入了：" + input);
}
System.out.println("程序结束");
```

> ❌ **常见错误**：在while里面忘记更新循环条件中的变量，导致**死循环**。永远检查：循环体里有没有某一步能让条件变false？

---

## 20.4 do-while循环：先斩后奏

do-while和while的唯一区别：**先执行一次循环体，再检查条件**。这保证了循环体至少执行一次：

```java
int count = 0;
do {
    System.out.println("count = " + count);
    count++;
} while (count < 5);
// 输出：0 1 2 3 4

// 条件一开始就是false——但循环体仍然执行了一次
int x = 10;
do {
    System.out.println("执行了");
} while (x < 5);
// 输出：执行了（只输出一次）
```

**适用场景**：用户输入验证（先让用户输入一次，再检查）：

```java
Scanner scanner = new Scanner(System.in);
int number;
do {
    System.out.print("请输入一个1到100之间的数字：");
    number = scanner.nextInt();
} while (number < 1 || number > 100);
System.out.println("有效数字：" + number);
```

---

## 20.5 break：强行退出循环

`break` 立即结束**整个循环**，不执行后续迭代：

```java
// 找第一个能被7整除的数
for (int i = 1; i <= 100; i++) {
    if (i % 7 == 0) {
        System.out.println("找到了：" + i);  // 7
        break;  // 退出循环
    }
}
```

---

## 20.6 continue：跳过本次迭代

`continue` 跳过本次循环中**continue后面的代码**，直接进入下一次迭代：

```java
// 打印1-10中的奇数
for (int i = 1; i <= 10; i++) {
    if (i % 2 == 0) {
        continue;  // 偶数跳过，不打印
    }
    System.out.print(i + " ");
}
// 输出：1 3 5 7 9
```

> 🤔 **想多一点**：break和continue可以用在任何循环里（for、while、do-while）。break和continue后面可以跟**标签**（label）来跳出外层循环，但几乎用不到，而且会让代码难以理解。见到带标签的break/continue，大概率可以重构为更清晰的写法。

---

## 20.7 循环选择指南

| 场景 | 推荐循环 |
|------|----------|
| 知道循环次数（遍历数组、执行N次） | `for` 三段式 |
| 遍历数组/集合的每个元素 | 增强 `for`（for-each） |
| 不确定循环次数，条件判断 | `while` |
| 至少执行一次 | `do-while` |

---

## 本章小结

| 知识点 | 核心要点 |
|--------|----------|
| for三段式 | `for(初始化; 条件; 更新)`。三段都可以省略，分号不能省略 |
| 增强for | `for(类型 变量 : 数组)`。简洁安全，但不能获取索引也不能修改元素 |
| while | 先判断后执行。循环体内必须改变条件变量，防止死循环 |
| do-while | 先执行后判断。循环体至少执行一次 |
| break | 立即终止整个循环 |
| continue | 跳过本次迭代，继续下一次 |
| 标签 | 用于跳出外层循环，极少使用 |

---

## 自测题

**1.** 以下代码输出什么？

```java
int sum = 0;
for (int i = 1; i <= 5; i++) {
    if (i == 3) continue;
    sum += i;
}
System.out.println(sum);
```

**2.** 用增强for循环重写以下代码：

```java
String[] names = {"张三", "李四", "王五"};
for (int i = 0; i < names.length; i++) {
    System.out.println(names[i]);
}
```

**3.** while和do-while的根本区别是什么？什么场景下必须用do-while？

---

> 🚀 **下一章**：第21章 · 数组——把同类型的数据排成一排，用索引快速访问。数组是Java里最基础的数据容器，但它的长度一旦创建就固定了。准备好迎接 `ArrayIndexOutOfBoundsException` 了吗？

---

[← 上一章：19-控制流if和switch](19-控制流if和switch.md) | [下一章：21-数组 →](21-数组.md)