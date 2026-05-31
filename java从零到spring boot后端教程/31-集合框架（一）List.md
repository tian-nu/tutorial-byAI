# 第31章 集合框架（一）：List

> 想象你有一个购物清单。你可以随时往清单末尾加东西（追加），可以检查某样东西在不在清单上（查找），可以删掉已经买到的东西（删除），也可以按编号直接拿第 N 样东西（随机访问）。在 Java 中，这个购物清单就是 **List**——最常用的有序集合。

---

## 31.1 List 接口概述

`List` 是 `Collection` 的子接口，核心特征三个词：**有序、可重复、有索引**。

| 特性 | 说明 |
|------|------|
| 有序 | 元素的存入顺序和遍历顺序一致 |
| 可重复 | `list.add("a"); list.add("a");` 完全合法 |
| 有索引 | 可以通过 `list.get(3)` 按位置访问 |

`List` 接口定义的核心方法：

```java
List<E>
├── add(E e)              // 尾部追加
├── add(int index, E e)   // 指定位置插入
├── get(int index)        // 按索引获取
├── set(int index, E e)   // 替换指定位置元素
├── remove(int index)     // 按索引删除
├── remove(Object o)      // 按值删除（删除第一个匹配项）
├── indexOf(Object o)     // 查找位置
├── size()                // 元素个数
├── contains(Object o)    // 是否包含
└── sort(Comparator)      // 排序（Java 8+默认方法）
```

Java 提供了三个主要实现类：

| 实现类 | 底层结构 | 最佳场景 |
|--------|---------|---------|
| `ArrayList` | 动态数组 | 随机访问多、尾部追加多 |
| `LinkedList` | 双向链表 | 头部/中间频繁增删 |
| `Vector` | 动态数组（线程安全） | 遗留代码，现代用 CopyOnWriteArrayList 替代 |

---

## 31.2 ArrayList

### 31.2.1 底层原理

> 🏷️ 此术语需进附录：**ArrayList**——基于动态数组实现的 List，随机访问 O(1)，尾部追加 O(1) 均摊，中间插入/删除 O(n)。扩容时容量变为原来的 **1.5 倍**。

想象一个停车场，划好了 10 个车位（初始容量）。车按顺序停进去，第 0 号位、第 1 号位……当第 11 辆车来时，停车场自动扩建 15 个车位（1.5 倍扩容），把原来的车复制到新停车场。

```java
// 内部结构示意
// ArrayList 底层是一个 Object[]
// Object[] elementData;
```

### 31.2.2 基本用法

```java
import java.util.ArrayList;
import java.util.List;

List<String> list = new ArrayList<>();

// 增
list.add("Java");
list.add("Python");
list.add(1, "C++");     // 在索引1处插入
System.out.println(list); // [Java, C++, Python]

// 查
String first = list.get(0);        // Java
boolean hasGo = list.contains("Go"); // false
int idx = list.indexOf("Python");   // 2

// 改
list.set(0, "Kotlin");
System.out.println(list); // [Kotlin, C++, Python]

// 删
list.remove(0);           // 按索引删除
list.remove("Python");    // 按值删除
System.out.println(list); // [C++]

// 遍历
for (int i = 0; i < list.size(); i++) {
    System.out.println(list.get(i));
}

for (String item : list) {
    System.out.println(item);
}
```

### 31.2.3 扩容机制详解

```java
// ArrayList 默认初始容量为 10（JDK 7+ 是延迟初始化的空数组，首次 add 时才扩到 10）
List<Integer> list = new ArrayList<>();  // elementData = {} (空数组)
list.add(1);                             // 首次扩容 → 容量 10

// 扩容公式：newCapacity = oldCapacity + (oldCapacity >> 1)
// 即 oldCapacity * 1.5

// 如果知道大概要放多少元素，指定初始容量避免多次扩容
List<String> bigList = new ArrayList<>(1000); // 预分配 1000 容量
```

> 🤔 **想多一点**：为什么扩容倍数是 1.5 而不是 2？这是时间和空间的折中。2 倍扩容会导致内存浪费（可能有一半空间不用），1.5 倍更省内存，同时扩容次数在可接受范围内。

---

## 31.3 LinkedList

### 31.3.1 底层原理

> 🏷️ 此术语需进附录：**LinkedList**——基于双向链表实现的 List 和 Deque。每个节点包含数据、前驱指针、后继指针。随机访问 O(n)，头尾操作 O(1)，中间插入/删除 O(1)（前提是已定位到该节点）。

想象一列手拉手的小朋友。每个人都记住前面是谁、后面是谁。要在中间插入一个人，只需让前后两个人换手即可，不需要所有人重新排队。

```java
// 内部节点结构示意
// private static class Node<E> {
//     E item;
//     Node<E> prev;  // 前一个节点
//     Node<E> next;  // 后一个节点
// }
```

### 31.3.2 基本用法

```java
import java.util.LinkedList;

LinkedList<String> list = new LinkedList<>();

// 头部操作（特有方法）
list.addFirst("A");       // [A]
list.addFirst("B");       // [B, A]
list.addLast("C");        // [B, A, C]
String first = list.getFirst();  // B
String last = list.getLast();    // C

// 删除头尾
list.removeFirst();       // [A, C]
list.removeLast();        // [A]

// LinkedList 也可以当栈或队列用
list.push("X");           // 压栈（等价于 addFirst），[X, A]
String top = list.pop();  // 弹栈（等价于 removeFirst），返回 X
```

> ⚠️ **重要提醒**：`LinkedList` 实现了 `List`，所以也可以用 `get(index)` 按索引访问。但**每次调用 `get(index)` 都会从头（或尾）遍历链表**，时间复杂度 O(n)，不要用 for 循环遍历 LinkedList！

```java
// ❌ 错误：O(n²) —— 每次 get 都要遍历
LinkedList<Integer> list = new LinkedList<>();
for (int i = 0; i < list.size(); i++) {
    System.out.println(list.get(i));
}

// ✅ 正确：用增强 for 或 iterator，O(n)
for (Integer item : list) {
    System.out.println(item);
}
```

---

## 31.4 ArrayList vs LinkedList 性能实测

```java
import java.util.*;

public class ListBenchmark {
    public static void main(String[] args) {
        final int N = 100_000;

        // --- 尾部追加 ---
        long start = System.nanoTime();
        List<Integer> arrList = new ArrayList<>();
        for (int i = 0; i < N; i++) arrList.add(i);
        long arrEnd = System.nanoTime() - start;

        start = System.nanoTime();
        List<Integer> linkList = new LinkedList<>();
        for (int i = 0; i < N; i++) linkList.add(i);
        long linkEnd = System.nanoTime() - start;

        System.out.println("=== 尾部追加 10万次 ===");
        System.out.println("ArrayList:  " + arrEnd / 1_000_000 + " ms");
        System.out.println("LinkedList: " + linkEnd / 1_000_000 + " ms");

        // --- 头部插入 ---
        start = System.nanoTime();
        for (int i = 0; i < 10000; i++) arrList.add(0, i);
        long arrHead = System.nanoTime() - start;

        start = System.nanoTime();
        for (int i = 0; i < 10000; i++) linkList.add(0, i);
        long linkHead = System.nanoTime() - start;

        System.out.println("\n=== 头部插入 1万次 ===");
        System.out.println("ArrayList:  " + arrHead / 1_000_000 + " ms");
        System.out.println("LinkedList: " + linkHead / 1_000_000 + " ms");

        // --- 随机访问 ---
        start = System.nanoTime();
        long sum = 0;
        for (int i = 0; i < N; i++) sum += arrList.get(i);
        long arrGet = System.nanoTime() - start;

        start = System.nanoTime();
        sum = 0;
        for (int i = 0; i < N; i++) sum += linkList.get(i);
        long linkGet = System.nanoTime() - start;

        System.out.println("\n=== 随机访问 10万次 ===");
        System.out.println("ArrayList:  " + arrGet / 1_000_000 + " ms");
        System.out.println("LinkedList: " + linkGet / 1_000_000 + " ms (可能非常慢！)");
    }
}
```

典型输出（你的机器可能不同）：

```
=== 尾部追加 10万次 ===
ArrayList:  3 ms
LinkedList: 5 ms

=== 头部插入 1万次 ===
ArrayList:  48 ms       ← 太慢了！每次插入都要移动所有元素
LinkedList: 1 ms

=== 随机访问 10万次 ===
ArrayList:  1 ms
LinkedList: 4500 ms     ← 灾难！O(n²)
```

结论表：

| 操作 | ArrayList | LinkedList |
|------|-----------|------------|
| 尾部追加 | ⚡ 很快（均摊 O(1)） | ⚡ 很快（O(1)） |
| 头部插入 | 🐢 慢（O(n)） | ⚡ 很快（O(1)） |
| 随机访问 get(i) | ⚡ 很快（O(1)） | 🐢 很慢（O(n)），不要用 for-i |
| 内存 | 紧凑（连续内存） | 每个节点多 2 个指针 |

> **简单选择口诀**：95% 的场景直接用 `ArrayList`。只有频繁在头部/中间插入删除时才考虑 `LinkedList`（这种情况其实很少见）。

---

## 31.5 Vector 与 Stack（了解即可）

`Vector` 是 Java 1.0 就存在的古老集合类，和 `ArrayList` 几乎一样，区别在于 `Vector` 的所有方法都用 `synchronized` 修饰，是**线程安全**的。

```java
Vector<String> v = new Vector<>();
v.add("old");
v.get(0);
// 内部每个方法都是 synchronized 的
```

`Stack` 继承自 `Vector`，实现了栈的 LIFO 操作：

```java
Stack<Integer> stack = new Stack<>();
stack.push(1);
stack.push(2);
int top = stack.peek();  // 2，不弹出
int pop = stack.pop();   // 2，弹出
```

> ⚠️ **现代 Java 中不推荐使用 Vector 和 Stack**。
> - 需要线程安全的 List：用 `Collections.synchronizedList(new ArrayList<>())` 或 `CopyOnWriteArrayList`
> - 需要栈：用 `ArrayDeque`（第32章会讲），性能远优于 Stack
> - 需要队列：用 `LinkedList` 或 `ArrayDeque`

---

## 31.6 Arrays.asList() 的坑

这是一个非常容易踩的坑：

```java
// ❌ 陷阱：Arrays.asList 返回的是固定大小的 List
List<String> fixedList = Arrays.asList("a", "b", "c");
fixedList.set(0, "x");  // ✅ 可以修改元素
// fixedList.add("d");  // ❌ UnsupportedOperationException！
// fixedList.remove(0); // ❌ UnsupportedOperationException！
```

原因：`Arrays.asList()` 返回的是 `Arrays` 内部类 `ArrayList`（不是 `java.util.ArrayList`），它直接包装原始数组，不支持增删。

```java
// ✅ 正确：如果需要可变的 List
List<String> mutableList = new ArrayList<>(Arrays.asList("a", "b", "c"));
mutableList.add("d");  // ✅
```

---

## 31.7 ❌ 常见错误

### 错误1：for-i 遍历 LinkedList

```java
LinkedList<String> list = new LinkedList<>();
// ... 添加数据 ...
// ❌ 每次 get(i) 都是 O(n)，总体 O(n²)
for (int i = 0; i < list.size(); i++) {
    String s = list.get(i);  // 灾难！
}

// ✅ 用增强 for 或迭代器
for (String s : list) {  // O(n)
    System.out.println(s);
}
```

### 错误2：并发修改异常

```java
List<String> list = new ArrayList<>(List.of("a", "b", "c"));
// ❌ 遍历过程中删除元素，抛出 ConcurrentModificationException
for (String s : list) {
    if (s.equals("b")) {
        list.remove(s);  // ❌ 异常！
    }
}

// ✅ 正确：使用迭代器的 remove()
Iterator<String> it = list.iterator();
while (it.hasNext()) {
    String s = it.next();
    if (s.equals("b")) {
        it.remove();  // ✅
    }
}

// ✅ 或者用 Java 8 的 removeIf
list.removeIf(s -> s.equals("b"));
```

### 错误3：Arrays.asList 当成可变 List

```java
List<Integer> list = Arrays.asList(1, 2, 3);
list.add(4);  // ❌ UnsupportedOperationException

// ✅ 包装一层
List<Integer> list = new ArrayList<>(Arrays.asList(1, 2, 3));
```

---

## 31.8 小结

| 知识点 | 一句话总结 |
|--------|-----------|
| ArrayList | 底层数组，随机访问 O(1)，扩容 1.5 倍，最常用 |
| LinkedList | 双向链表，头尾操作 O(1)，不要用 get(index) 遍历 |
| Vector | 线程安全的 ArrayList，已过时 |
| Stack | 继承 Vector 的栈，用 ArrayDeque 替代 |
| Arrays.asList | 返回固定大小 List，不能增删 |
| 选型 | 默认用 ArrayList，需要频繁头插用 LinkedList |

---

## 31.9 自测题

**1.** 以下代码的输出是什么？

```java
List<String> list = new ArrayList<>(List.of("A", "B", "C"));
list.add(1, "D");
System.out.println(list.get(2));
list.remove("D");
System.out.println(list);
```

**2.** 为什么下面的代码非常慢？应该如何修改？

```java
LinkedList<Integer> list = new LinkedList<>();
for (int i = 0; i < 100000; i++) {
    list.add(i);
}
long sum = 0;
for (int i = 0; i < list.size(); i++) {
    sum += list.get(i);  // 为什么慢？
}
```

**3.** `Arrays.asList("a", "b").add("c");` 会抛出什么异常？为什么？

> 答案提示：1. 输出 "B" 和 [A, B, C]；2. 每次 `get(i)` 都要从链表头部遍历，总复杂度 O(n²)，应改用增强 for；3. `UnsupportedOperationException`，因为 `Arrays.asList` 返回的是固定大小的内部 List。