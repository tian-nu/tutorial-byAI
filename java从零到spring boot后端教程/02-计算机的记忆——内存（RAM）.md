# 第02章 · 计算机的记忆——内存（RAM）

> "你声明一个 `int count = 0;`，count存在哪里？存在内存里。但内存不是一块均匀的铁板——它分了区，每个区住着不同身份的居民。"

## 02.1 内存是什么

内存（RAM，Random Access Memory）是计算机的"短期记忆"。CPU处理数据时，必须先把数据从硬盘加载到内存，然后在内存中读写。

关键特征：
- **快**：比硬盘快几千倍（纳秒级 vs 毫秒级）
- **断电就忘**：关机后数据全部消失
- **容量有限**：你的电脑可能是16GB，服务器可能是64GB~256GB

对Java程序员来说，内存被JVM管理着。你不需要手动 `malloc` 和 `free`——JVM的垃圾回收器（GC）会自动帮你回收不再使用的内存。

## 02.2 栈与堆：Java内存的两大区域

JVM把内存划分成几个区域。最重要的是 **栈（Stack）** 和 **堆（Heap）**。

```java
public class MemoryDemo {
    public static void main(String[] args) {
        int age = 25;                    // ① 基本类型，存在栈上
        String name = "张三";             // ② name引用在栈上，"张三"对象在堆上
        User user = new User("李四", 30); // ③ user引用在栈上，User对象在堆上
    }
}

class User {
    String name;   // ④ name引用在堆上的User对象内部
    int age;       // ⑤ 基本类型，直接存在堆上的User对象内部

    User(String name, int age) {
        this.name = name;
        this.age = age;
    }
}
```

### 栈（Stack）

| 特征 | 说明 |
|------|------|
| 存什么 | 基本类型（int, long, double...）、对象引用（指针） |
| 生命周期 | 方法调用时分配，方法结束时自动释放 |
| 大小 | 通常较小（默认1MB/线程） |
| 速度 | 极快，LIFO（后进先出） |
| 管理 | 自动，不需要GC |

### 堆（Heap）

| 特征 | 说明 |
|------|------|
| 存什么 | 所有对象实例、数组 |
| 生命周期 | 对象不再被引用时，由GC回收 |
| 大小 | 通常很大（几个GB） |
| 速度 | 比栈慢，需要GC管理 |
| 管理 | JVM的垃圾回收器自动管理 |

用图表示上面的代码在内存中的布局：

```
栈（每个线程独立）              堆（所有线程共享）
┌─────────────────┐          ┌──────────────────────┐
│ main() 栈帧      │          │                      │
│                 │          │   "张三" (String对象)  │
│ age = 25 ───────│── 基本类型直接存值                 │
│                 │          │                      │
│ name ───────────│──────────│→  String@0x1a2b      │
│                 │          │                      │
│ user ───────────│──────────│→  User@0x3c4d        │
│                 │          │   ├ name ────────────│──→ "李四" (String对象)
│                 │          │   └ age = 30         │
└─────────────────┘          └──────────────────────┘
```

## 02.3 为什么要知道栈和堆？

**场景一：NullPointerException（空指针异常）**

```java
User user;              // 栈上的user引用指向null（堆上没有任何User对象）
System.out.println(user.getName());  // ❌ NullPointerException！
```

栈上的 `user` 变量存在，但它指向 `null`（堆上没有对象）。你试图通过一个空引用去访问对象的方法，JVM直接抛异常。

**场景二：两个引用指向同一个对象**

```java
User a = new User("王五", 25);
User b = a;           // b指向堆上同一个User对象
b.setAge(26);         // 修改b的age
System.out.println(a.getAge());  // 输出 26，不是25！
```

栈上有两个引用 `a` 和 `b`，但堆上只有一个 `User` 对象。通过 `b` 修改，`a` 看到的也跟着变了——因为它们指向的是同一个东西。

> 🤔 想多一点：这就是所谓的"引用传递"。Java中所有对象变量存的都是引用（指针），不是对象本身。面试常考的"Java是值传递还是引用传递？"——实际上Java永远是值传递，但对象类型传递的是引用的值。这个概念在第22章讲面向对象时会详细展开。

## 02.4 JVM堆内存参数

Spring Boot应用启动时，你可以配置JVM的堆内存大小：

```bash
java -Xms512m -Xmx2048m -jar myapp.jar
```

- `-Xms512m`：堆的初始大小512MB
- `-Xmx2048m`：堆的最大大小2GB

如果你的Spring Boot应用要处理大量并发请求，2GB可能不够。这时候你会看到 `OutOfMemoryError: Java heap space`——意味着堆满了，GC回收不过来，JVM崩溃了。

---

## 本章小结

| 学了什么 | 一句话说明 |
|----------|-----------|
| 内存的角色 | 短期记忆，快但断电就忘，CPU直接读写 |
| 栈 | 存基本类型和引用，方法结束自动释放，1MB/线程 |
| 堆 | 存所有对象，由GC自动回收，大小可达GB级 |
| 引用指向 | 多个引用指向同一对象，改一个全变 |
| JVM堆参数 | -Xms初始大小，-Xmx最大大小 |

## 自测题

1. 下面代码中，哪些变量存在栈上？哪些对象存在堆上？
   ```java
   int x = 100;
   String s = "hello";
   List<String> list = new ArrayList<>();
   ```

2. 为什么说"Java程序员不用手动管理内存"？这个方便的背后是什么机制在干活？

3. 如果你的Spring Boot应用报了 `OutOfMemoryError: Java heap space`，你最先应该调整哪个JVM参数？