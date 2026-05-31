# 第32章 集合框架（二）：Set 与 Queue

> 上一章我们学了 List——像购物清单，可以有重复项。这一章学两个"有规矩"的集合：**Set** 像一个不重复的抽奖箱——同一个号码不会出现两次；**Queue** 像奶茶店的排队——先来的先拿，不允许插队。

---

## 32.1 Set 接口概述

`Set` 的核心特征：**不重复、无序（多数实现）**。

| 特性 | 说明 |
|------|------|
| 不重复 | 两个元素 `e1.equals(e2)` 为 true 时，只会存一个 |
| 无索引 | 没有 `get(index)` 方法，不能按位置访问 |
| 允许 null | 多数实现允许一个 null 元素 |

`Set` 的三个常用实现：

| 实现类 | 底层 | 顺序 | null | 特点 |
|--------|------|------|------|------|
| `HashSet` | HashMap | 无序 | 允许 | 最快，O(1) |
| `LinkedHashSet` | LinkedHashMap | 插入顺序 | 允许 | 遍历顺序=插入顺序 |
| `TreeSet` | TreeMap（红黑树） | 自然排序/比较器 | 不允许 | O(log n)，支持范围查找 |

---

## 32.2 HashSet

### 32.2.1 原理与用法

`HashSet` 内部直接复用 `HashMap`——元素作为 key，value 是一个固定的 `PRESENT` 占位对象。

```java
import java.util.HashSet;
import java.util.Set;

Set<String> set = new HashSet<>();

set.add("Java");
set.add("Python");
set.add("Java");         // 重复，不会加进去
System.out.println(set); // [Java, Python]（顺序不确定）

set.remove("Python");
boolean hasJava = set.contains("Java"); // true
int size = set.size();                  // 1
```

### 32.2.2 重写 equals 必须重写 hashCode

这是 Java 初学者踩坑最多的地方之一：

```java
class Person {
    String name;
    int age;

    Person(String name, int age) {
        this.name = name;
        this.age = age;
    }

    @Override
    public boolean equals(Object obj) {
        if (this == obj) return true;
        if (!(obj instanceof Person)) return false;
        Person p = (Person) obj;
        return age == p.age && Objects.equals(name, p.name);
    }

    // 必须重写 hashCode！
    @Override
    public int hashCode() {
        return Objects.hash(name, age);
    }
}

// 测试
Set<Person> people = new HashSet<>();
people.add(new Person("Alice", 25));
people.add(new Person("Alice", 25));

System.out.println(people.size()); // 1 —— 正确去重
// 如果不重写 hashCode，会输出 2 —— 两个"相同"的人都在集合里！
```

> 🤔 **想多一点**：HashSet 判断重复分两步——先比较 `hashCode()`，如果不同就直接认为不重复；如果相同再调用 `equals()` 确认。所以只重写 `equals` 不重写 `hashCode`，两个对象哈希值不同，HashSet 根本不会去调用 `equals`。

---

## 32.3 LinkedHashSet

`LinkedHashSet` 继承 `HashSet`，底层用 `LinkedHashMap`，在哈希表基础上维护了一条**双向链表**记录插入顺序。

```java
import java.util.LinkedHashSet;
import java.util.Set;

Set<String> set = new LinkedHashSet<>();
set.add("C");
set.add("A");
set.add("B");
set.add("A");           // 重复，忽略

// 遍历顺序 = 插入顺序
for (String s : set) {
    System.out.print(s + " "); // C A B
}
```

**适用场景**：需要去重，又想保持元素添加时的顺序。比如记录用户访问的页面（去重 + 保持访问顺序）。

---

## 32.4 TreeSet

`TreeSet` 基于**红黑树**（一种自平衡二叉查找树）实现，元素会按照自然顺序或指定的 `Comparator` 排序。

```java
import java.util.TreeSet;
import java.util.Set;

Set<Integer> set = new TreeSet<>();
set.add(5);
set.add(1);
set.add(3);

System.out.println(set); // [1, 3, 5] —— 自动排序！

// 范围操作（TreeSet 独有）
TreeSet<Integer> tree = new TreeSet<>(set);
System.out.println(tree.first());            // 1 （最小值）
System.out.println(tree.last());             // 5 （最大值）
System.out.println(tree.lower(3));           // 1 （小于3的最大元素）
System.out.println(tree.higher(3));          // 5 （大于3的最小元素）
System.out.println(tree.subSet(1, 5));       // [1, 3]（左闭右开）
```

使用自定义排序：

```java
// 按字符串长度排序
TreeSet<String> set = new TreeSet<>((a, b) -> a.length() - b.length());
set.add("apple");
set.add("pie");
set.add("banana");

System.out.println(set); // [pie, apple, banana] —— 注意：banana 和 apple 长度相同，
                          // TreeSet 认为它们是相等的（compareTo 返回 0），所以 banana 会覆盖 apple！
```

> ⚠️ **关键注意事项**：TreeSet 用 `compareTo()` 或 `Comparator.compare()` 判断相等（而不是 `equals()`）。如果比较器返回 0，TreeSet 就认为两个元素相等。上例中 `"apple".length() == "banana".length()` 导致后者覆盖前者——这是一个常见 bug。

---

## 32.5 Queue 与 Deque 接口

### 32.5.1 队列概念

队列就像奶茶店排队——先进先出（FIFO，First In First Out）。`Queue` 接口定义了队列操作：

| 操作 | 抛异常版本 | 返回特殊值版本 |
|------|-----------|--------------|
| 入队 | `add(e)` | `offer(e)` 返回 false |
| 出队 | `remove()` | `poll()` 返回 null |
| 查看队首 | `element()` | `peek()` 返回 null |

### 32.5.2 ArrayDeque

`ArrayDeque` 是基于**循环数组**实现的双端队列，可以高效地在两端添加/删除元素。它是 `Stack` 和 `LinkedList`（当队列用）的**最佳替代品**。

```java
import java.util.ArrayDeque;
import java.util.Deque;

Deque<String> deque = new ArrayDeque<>();

// 作为队列（FIFO）：队尾进，队首出
deque.offer("A");       // 队尾入
deque.offer("B");
deque.offer("C");
System.out.println(deque.poll()); // A（队首出）
System.out.println(deque);        // [B, C]

// 作为栈（LIFO）：同一端进出
Deque<Integer> stack = new ArrayDeque<>();
stack.push(1);          // 压栈（等价于 addFirst）
stack.push(2);
stack.push(3);
System.out.println(stack.pop()); // 3（弹栈）
System.out.println(stack.pop()); // 2
System.out.println(stack.pop()); // 1

// 双端操作
deque.addFirst("X");    // 头部加
deque.addLast("Y");     // 尾部加
deque.removeFirst();    // 头部删
deque.removeLast();     // 尾部删
```

### 32.5.3 PriorityQueue

`PriorityQueue` 是**优先级队列**——不是按进入顺序出队，而是按优先级（自然排序或比较器）出队。

想象医院的急诊室：危重病人优先处理，不管他是不是最后来的。

```java
import java.util.PriorityQueue;
import java.util.Queue;

Queue<Integer> pq = new PriorityQueue<>();
pq.offer(5);
pq.offer(1);
pq.offer(3);

System.out.println(pq.poll()); // 1（最小先出）
System.out.println(pq.poll()); // 3
System.out.println(pq.poll()); // 5
```

> ⚠️ 注意：`PriorityQueue` 的遍历顺序**不保证有序**！只有 `poll()`/`peek()` 才保证按优先级返回。

```java
Queue<Integer> pq = new PriorityQueue<>(List.of(5, 1, 3));
System.out.println(pq);             // [1, 5, 3] —— 内部数组不完全有序
System.out.println(pq.poll());      // 1（这才是优先级最高的）
System.out.println(pq.poll());      // 3
```

自定义优先级（大顶堆）：

```java
// 从大到小
Queue<Integer> maxHeap = new PriorityQueue<>((a, b) -> b - a);
maxHeap.offer(5);
maxHeap.offer(1);
maxHeap.offer(3);
System.out.println(maxHeap.poll()); // 5（最大先出）
```

实际应用——Top K 问题：

```java
// 找出数组中第 K 大的元素
int[] nums = {3, 2, 1, 5, 6, 4};
int k = 2;

Queue<Integer> minHeap = new PriorityQueue<>();
for (int num : nums) {
    minHeap.offer(num);
    if (minHeap.size() > k) {
        minHeap.poll(); // 弹出最小的，保留 K 个最大的
    }
}
System.out.println(minHeap.peek()); // 5（第2大）
```

---

## 32.6 ❌ 常见错误

### 错误1：HashSet 存放自定义对象不去重

```java
class User {
    String name;
    User(String name) { this.name = name; }
}
// ❌ 没有重写 equals 和 hashCode
Set<User> set = new HashSet<>();
set.add(new User("Alice"));
set.add(new User("Alice"));
System.out.println(set.size()); // 2 —— 因为默认用 Object 的 equals（比较引用）

// ✅ 重写 equals 和 hashCode 后
System.out.println(set.size()); // 1
```

### 错误2：TreeSet 存放不能比较的对象

```java
// ❌ 运行时 ClassCastException
Set<Object> set = new TreeSet<>();
set.add("hello");
set.add(123);  // 字符串和整数无法比较！

// ✅ TreeSet 的元素必须可比较（实现 Comparable 或提供 Comparator）
```

### 错误3：PriorityQueue 用 for-each 遍历

```java
Queue<Integer> pq = new PriorityQueue<>(List.of(5, 1, 3));
// ❌ 遍历顺序不是优先级顺序！
for (Integer i : pq) {
    System.out.print(i + " ");  // 输出顺序不确定
}

// ✅ 用 poll() 按优先级顺序取出
while (!pq.isEmpty()) {
    System.out.print(pq.poll() + " "); // 1 3 5
}
```

---

## 32.7 小结

| 知识点 | 一句话总结 |
|--------|-----------|
| HashSet | 哈希表实现，O(1)，无序，自定义对象必须重写 equals+hashCode |
| LinkedHashSet | HashSet + 双向链表，保持插入顺序 |
| TreeSet | 红黑树实现，自动排序 O(log n)，用 compareTo 判等 |
| ArrayDeque | 循环数组双端队列，栈和队列都推荐用它 |
| PriorityQueue | 优先级队列（二叉堆），poll() 按优先级出队 |
| 队列操作 | offer/poll/peek（返回特殊值）优于 add/remove/element（抛异常） |

---

## 32.8 自测题

**1.** 以下代码输出什么？为什么？

```java
TreeSet<String> set = new TreeSet<>((a, b) -> a.length() - b.length());
set.add("hello");
set.add("world");
set.add("java");
System.out.println(set.size());
```

**2.** 用 `PriorityQueue` 实现一个支持泛型的"大顶堆"（最大的元素先出队）。

**3.** `HashSet` 判断两个元素是否相等的完整过程是什么？为什么必须同时重写 `equals()` 和 `hashCode()`？

> 答案提示：1. 输出 2，因为 "hello"(5) 和 "world"(5) 长度相同，比较器返回 0，后者覆盖前者；2. `new PriorityQueue<>((a, b) -> ((Comparable) b).compareTo(a))`；3. 先比较 hashCode，不同则直接认为不等，相同再调用 equals 确认。