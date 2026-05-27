# 第5章：Java核心API

## 本章目标

学完本章后，你将能够：

- 深刻理解String的不可变性原理，在循环拼接等场景中正确选择StringBuilder
- 熟练使用Java集合框架（List、Set、Map），理解各集合类的底层数据结构与时间复杂度
- 理解泛型的设计目的，运用PECS原则处理通配符问题
- 掌握包装类与自动装箱拆箱机制，避开Integer缓存的经典陷阱
- 使用Java 8+新日期API进行安全的时间计算与格式化

---

## 5.1 String深度解析

String是Java中最常用的类，没有之一。它表面简单，但背后隐藏着大量精妙的设计。本节将带你深入到字节码级别理解String的工作方式。

### 5.1.1 String的不可变性

打开String类的源码（JDK 9+），你会看到：

```java
public final class String
    implements java.io.Serializable, Comparable<String>, CharSequence {

    @Stable
    private final byte[] value;  // JDK 9+ 用 byte[]，JDK 8 用 final char[]

    // ...
}
```

三个关键点共同保证了不可变性：

1. **`final class`**：String不能被继承，杜绝了子类篡改行为的可能。
2. **`private final byte[] value`**：存储字符的底层数组是`private`（外部无法访问）+ `final`（引用不可变）。JDK 9之前用的是`char[]`，每个char占2字节；JDK 9改用`byte[]`+coder标记，Latin-1字符只需1字节，大幅节省内存——这个优化叫**Compact Strings**。
3. **所有方法返回新对象**：`substring()`、`replace()`、`toUpperCase()`等方法都创建新String返回，绝不修改原数组。

**为什么设计为不可变？** 这是面试高频问题，答好三点即可：

- **安全性**：String被广泛用于类名、文件路径、网络URL、数据库连接字符串等。如果String可变，恶意代码可以篡改这些值造成安全漏洞。同时，JVM的类加载机制依赖String来标识类，可变String会导致类被劫持。
- **字符串常量池**：不可变性是实现String Pool的前提。因为不可变，多个引用可以安全地共享同一个字符串对象，大大节省了堆内存。
- **哈希缓存**：String的hashCode被缓存在`private int hash`字段中，第一次计算后就不再变化（因为内容不变），这使得String作为HashMap的key时性能极佳。

### 5.1.2 字符串常量池（String Pool）

字符串常量池是JVM中一块特殊的内存区域。JDK 7之前它位于方法区（永久代），JDK 7起移到了堆内存中——这让GC可以正常回收池中不再使用的字符串。

两种创建方式的内存行为完全不同：

```java
// 方式一：字面量直接赋值
String s1 = "hello";    // JVM先去常量池找"hello"，找不到就创建一个
String s2 = "hello";    // 找到了！直接复用，s2和s1指向同一个对象
System.out.println(s1 == s2);  // true——同一个池中的对象

// 方式二：new关键字
String s3 = new String("hello");
// 这行代码可能创建了两个对象！
// (1) 字面量"hello"——放入常量池（如果池中没有的话）
// (2) new String(...)——在堆中新建一个String对象，该对象内部的value指向池中"hello"的value副本
System.out.println(s1 == s3);  // false——堆中对象 vs 池中对象
```

下图展示了两种方式的内存布局：

```
字符串常量池（堆中）              堆内存
┌──────────────────┐        ┌─────────────────────────┐
│  "hello"  ◄──────┼─────── │  String对象 (new出来的)   │
│   (char数组)     │        │  value ──► 自己的byte[]  │
└──────────────────┘        └─────────────────────────┘
       ▲
       │ s1, s2
```

`s1`和`s2`的箭头指向常量池中的同一个"hello"对象；`s3`单独指向堆中new出来的新对象。

**intern()方法**：可以手动将一个堆中的String放入常量池并返回池中引用：

```java
String s4 = new String("hello").intern();
System.out.println(s1 == s4);  // true——intern()返回的是池中的"hello"
```

intern()的策略是：先查池中是否已存在equals相等的字符串，有则返回池中引用，无则把当前字符串加入池中并返回。**注意**：JDK 7后的intern()不需要复制对象到永久代了，因为池本身就在堆中。

### 5.1.3 StringBuilder与StringBuffer

> 🚨 **坑点：循环中大量字符串拼接**
>
> ```java
> // 错误写法：每次循环都创建一个新的String对象！
> String result = "";
> for (int i = 0; i < 10000; i++) {
>     result += "data" + i;  // 等价于 result = new StringBuilder(result).append("data").append(i).toString()
> }
> // 10,000次循环创建了约10,000个临时String对象和StringBuilder对象
> // 时间可能从几毫秒变成几百毫秒，GC压力巨大
> ```
>
> **正确做法**：
> ```java
> StringBuilder sb = new StringBuilder();
> for (int i = 0; i < 10000; i++) {
>     sb.append("data").append(i);
> }
> String result = sb.toString();  // 最后才生成一个String
> ```

StringBuilder和StringBuffer的区别只有一点：**线程安全**。

| 特性 | StringBuilder | StringBuffer |
|------|--------------|-------------|
| 线程安全 | 否 | 是（方法用synchronized修饰） |
| 性能 | 快 | 慢（锁开销） |
| 使用场景 | 单线程、局部变量 | 多线程共享 |

绝大多数情况我们用StringBuilder就够了（方法内局部变量天然线程安全）。常用方法：

```java
StringBuilder sb = new StringBuilder("Hello");
sb.append(" World");        // "Hello World"——追加
sb.insert(5, " Java");      // "Hello Java World"——在位置5插入
sb.delete(5, 10);           // "Hello World"——删除 [5, 10) 的字符
sb.reverse();               // "dlroW olleH"——反转
sb.replace(0, 5, "Hi");     // "Hi World"——替换
String result = sb.toString();
```

链式调用的风格很常见：`sb.append("a").append("b").append("c");`

### 5.1.4 常用API速查

以下每个方法都会给出可运行示例，注意`substring`的区间是**左闭右开**。

```java
public class StringApiDemo {
    public static void main(String[] args) {
        String str = "Hello, Java 世界!";

        // length() — 返回字符数（不是字节数）
        System.out.println(str.length());  // 15

        // charAt(int index) — 索引从0开始
        System.out.println(str.charAt(0));   // 'H'
        System.out.println(str.charAt(7));   // 'J'

        // substring(beginIndex, endIndex) — [begin, end)
        System.out.println(str.substring(0, 5));    // "Hello"
        System.out.println(str.substring(7));       // "Java 世界!"（到末尾）

        // indexOf — 查找子串位置，找不到返回 -1
        System.out.println(str.indexOf("Java"));      // 7
        System.out.println(str.indexOf("Python"));    // -1
        System.out.println(str.lastIndexOf("a"));     // 9（从后往前找）

        // contains — 是否包含
        System.out.println(str.contains("Java"));     // true

        // startsWith / endsWith
        System.out.println(str.startsWith("Hello"));  // true
        System.out.println(str.endsWith("!"));        // true
    }
}
```

> 🚨 **坑点：split()的参数是正则表达式**
>
> ```java
> String s = "a.b.c";
> String[] parts = s.split(".");   // 错误！.是正则特殊字符，匹配任意字符
> System.out.println(parts.length); // 0（什么都没匹配到）
>
> // 正确：转义
> String[] parts2 = s.split("\\."); // \\. → 正则中的字面量点号
> System.out.println(parts2.length); // 3 → ["a", "b", "c"]
> ```
>
> 需要转义的常见字符：`.` `|` `*` `+` `?` `^` `$` `(` `)` `[` `]` `{` `}` `\`

> 🚨 **坑点：split对空字符串和尾随空元素的处理**
>
> ```java
> String s1 = "a,,b";
> String[] arr1 = s1.split(",");
> System.out.println(arr1.length);  // 3 → ["a", "", "b"]（空串也保留）
>
> String s2 = "a,b,";
> String[] arr2 = s2.split(",");
> System.out.println(arr2.length);  // 2 → ["a", "b"]（尾部空元素被丢弃！）
>
> // 如果不想丢弃尾部空元素，用 split(regex, -1)
> String[] arr3 = s2.split(",", -1);
> System.out.println(arr3.length);  // 3 → ["a", "b", ""]
> ```

```java
// replace — 字符替换（替换所有匹配的字符）
System.out.println("hello".replace('l', 'x'));  // "hexxo"

// replaceAll — 正则替换
System.out.println("a1b2c3".replaceAll("\\d", "X")); // "aXbXcX"

// trim — 去掉首尾ASCII空格（\t \n \r 等）
System.out.println("  hello  ".trim());  // "hello"

// strip — Java 11+，支持Unicode空格（如中文全角空格）
System.out.println("  hello\u2003".strip()); // "hello"（\u2003是em space）

// toUpperCase / toLowerCase
System.out.println("Hello".toUpperCase());  // "HELLO"
System.out.println("Hello".toLowerCase());  // "hello"
```

---

## 5.2 集合框架体系

Java集合框架是面试的重中之重。不同于数组的固定大小和单一类型操作，集合框架提供了一套统一、灵活的数据结构API。

### 5.2.1 Collection继承体系（ASCII全景图）

```
Iterable（可迭代）
  │
  └── Collection（单列集合根接口）
        │
        ├── List（有序，可重复）
        │     ├── ArrayList    — 底层 Object[]，查询 O(1)，尾部增删 O(1)
        │     ├── LinkedList   — 底层双向链表，头尾增删 O(1)，随机访问 O(n)
        │     ├── Vector       — 线程安全的ArrayList（已过时，基本不用）
        │     └── Stack        — Vector的子类，模拟栈（也基本不用了）
        │
        ├── Set（无序，不可重复）
        │     ├── HashSet      — 底层 HashMap，增删查 O(1)，无序
        │     ├── LinkedHashSet — 底层 LinkedHashMap，增删查 O(1)，保持插入顺序
        │     └── TreeSet      — 底层 TreeMap（红黑树），增删查 O(log n)，排序
        │
        └── Queue（队列）
              ├── LinkedList   — 也实现了 Deque（双端队列）
              ├── PriorityQueue — 优先级队列（二叉堆）
              └── ArrayDeque   — 循环数组双端队列（比Stack和LinkedList高效）

Map（双列集合，独立接口，不继承Collection）
  │
  ├── HashMap      — 数组+链表+红黑树（JDK 8+），O(1)
  ├── LinkedHashMap — HashMap + 双向链表，保持插入/访问顺序
  ├── TreeMap      — 红黑树，按key排序，O(log n)
  └── Hashtable    — 线程安全的HashMap（已过时，基本不用）
```

**记忆口诀**：
- 要顺序用List，要唯一用Set，要键值用Map
- 查多改少用ArrayList，改多查少用LinkedList
- 要排序用TreeXXX，否则用HashXXX

### 5.2.2 ArrayList vs LinkedList深入对比

"ArrayList查询快增删慢，LinkedList查询慢增删快"——这句话流传很广，但**只有一半是对的**。

**ArrayList的真相**：

```java
// ArrayList底层就是个Object[]数组
// transient Object[] elementData;

ArrayList<String> list = new ArrayList<>();
list.add("A");       // 尾部添加 — O(1)
list.add(0, "B");    // 头部/中间添加 — O(n)，需要移动后面所有元素
list.get(0);         // 按索引访问 — O(1)，直接通过数组下标
list.remove(0);      // 头部/中间删除 — O(n)，需要移动后面所有元素
list.remove(list.size() - 1); // 尾部删除 — O(1)，不用移动
```

ArrayList的扩容机制：默认初始容量10，每次扩容为原来的**1.5倍**（`newCapacity = oldCapacity + (oldCapacity >> 1)`），扩容时涉及数组复制（`Arrays.copyOf`），这也是一个开销。如果你知道大概要存100个元素，用`new ArrayList<>(100)`避免多次扩容。

**LinkedList的真相**：

```java
// LinkedList底层是双向链表
// private static class Node<E> {
//     E item;
//     Node<E> next;
//     Node<E> prev;
// }

LinkedList<String> list = new LinkedList<>();
list.add("A");           // 尾部添加 — O(1)（维护了尾指针）
list.addFirst("B");      // 头部添加 — O(1)
list.get(2);             // 按索引访问 — O(n)，需要从头/尾遍历
list.remove(0);          // 按索引删除 — O(n)，先遍历找到位置
list.removeFirst();      // 头部删除 — O(1)
```

LinkedList实现了Deque接口，所以它既可以当List用，也可以当队列（FIFO）和栈（LIFO）用：

```java
LinkedList<String> deque = new LinkedList<>();
deque.offer("first");     // 入队（尾部添加），等价于 addLast
deque.push("second");     // 入栈（头部添加），等价于 addFirst
System.out.println(deque.poll()); // "second" — 出队（头部取出并删除）
System.out.println(deque.pop());  // "first"  — 出栈（头部取出并删除）
```

> 🚨 **坑点："ArrayList增删慢"不准确**
>
> ArrayList尾部增删是O(1)，只有头部和中间的增删才是O(n)。
> 此外，现代CPU的缓存行（Cache Line）机制会让连续内存的ArrayList在实际访问中比分散内存的LinkedList快很多——即使理论复杂度都是O(n)，内存局部性带来的常数因子差距可能高达10倍以上。**大部分场景优先选ArrayList。**

### 5.2.3 遍历方式的正确选择

遍历集合有五种方式，各有坑点：

```java
List<String> list = new ArrayList<>(Arrays.asList("A", "B", "C", "D"));

// 方式一：传统for + 索引
for (int i = 0; i < list.size(); i++) {
    System.out.println(list.get(i));
}
```

> 🚨 **坑点：正向for循环删除元素会导致跳过问题**
>
> ```java
> List<String> list = new ArrayList<>(Arrays.asList("A", "B", "C", "D"));
> for (int i = 0; i < list.size(); i++) {
>     if ("B".equals(list.get(i))) {
>         list.remove(i);  // 删除B后，后面的C移动到索引1，但i++跳到了索引2
>     }
> }
> System.out.println(list); // [A, C, D] — C没被检查！
> ```
>
> **解决方案一：倒序删除**
> ```java
> for (int i = list.size() - 1; i >= 0; i--) {
>     if (shouldRemove(list.get(i))) {
>         list.remove(i);  // 倒序删除不影响未遍历的元素索引
>     }
> }
> ```
>
> **解决方案二：Iterator.remove()（推荐）**
> ```java
> Iterator<String> it = list.iterator();
> while (it.hasNext()) {
>     String s = it.next();
>     if (shouldRemove(s)) {
>         it.remove();  // 安全删除
>     }
> }
> ```

```java
// 方式二：for-each（增强for）
for (String s : list) {
    System.out.println(s);
    // list.remove(s); // 危险！ConcurrentModificationException
}
```

> 🚨 **坑点：for-each遍历中修改集合 → ConcurrentModificationException**
>
> for-each本质上是Iterator的语法糖。Iterator内部维护了一个`expectedModCount`，当检测到集合被其他方式修改（modCount不一致），就会抛出这个异常。
>
> 如果只是想在遍历时删除，可以用`removeIf`（Java 8+）：
> ```java
> list.removeIf(s -> s.startsWith("A")); // 一行搞定，内部用Iterator
> ```

```java
// 方式三：forEach + Lambda
list.forEach(System.out::println);
// 缺点：无法使用 break / continue / return 跳过元素
```

### 5.2.4 HashSet的去重原理

HashSet的底层实际上是一个HashMap，元素作为key，value是一个固定的Object常量（叫PRESENT）：

```java
// HashSet源码简化
public class HashSet<E> {
    private transient HashMap<E, Object> map;
    private static final Object PRESENT = new Object();

    public boolean add(E e) {
        return map.put(e, PRESENT) == null; // 放进去返回null说明之前没有，添加成功
    }
}
```

去重流程分两步：

1. **先算hashCode()**：定位到哈希表的某个桶（bucket）。
2. **再调用equals()**：桶中有元素时，逐个用equals比较，相同就不存。

> 🚨 **坑点：存入HashSet的对象必须同时重写hashCode()和equals()**
>
> 如果只重写equals()而不重写hashCode()：
> ```java
> class Person {
>     String name;
>     int age;
>
>     Person(String name, int age) { this.name = name; this.age = age; }
>
>     @Override
>     public boolean equals(Object o) {  // 只重写了equals
>         if (this == o) return true;
>         if (!(o instanceof Person)) return false;
>         Person p = (Person) o;
>         return age == p.age && Objects.equals(name, p.name);
>     }
>     // 没有重写hashCode()！
> }
>
> Set<Person> set = new HashSet<>();
> set.add(new Person("张三", 25));
> set.add(new Person("张三", 25));
> System.out.println(set.size()); // 2！！—— 因为是两个对象，Object的hashCode()返回不同值
> ```
>
> **Object默认的hashCode()**返回的是对象的内存地址（经过转换），两个内容相同的不同对象hashCode不同 → 放入不同的桶 → equals根本没机会调用 → 重复了！
>
> **正确做法**（两个方法重写必须遵守同一个约定：equals为true的对象，hashCode必须相等）：
> ```java
> @Override
> public int hashCode() {
>     return Objects.hash(name, age);  // 用Objects.hash()生成
> }
> ```

**TreeSet的排序要求**：存入TreeSet的元素必须实现`Comparable`接口，或构造TreeSet时传入`Comparator`：

```java
// 方式一：元素实现Comparable
class Student implements Comparable<Student> {
    String name; int score;
    public int compareTo(Student o) { return Integer.compare(o.score, this.score); } // 按分数降序
}

// 方式二：构造时传入Comparator
Set<Student> set = new TreeSet<>((a, b) -> a.name.compareTo(b.name)); // 按姓名升序
```

> 🚨 **坑点**：往TreeSet中放的第一个元素不需要比较（因为空树），但从第二个开始如果类没实现Comparable且没传Comparator，会抛`ClassCastException`。

### 5.2.5 HashMap深入解析（面试重量级）

HashMap是Java中最复杂的集合类之一，也是面试的"常驻嘉宾"。

**JDK 8+底层结构**：

```
HashMap内部结构（数组+链表+红黑树）
┌───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┐
│ 0 │ 1 │ 2 │ 3 │ 4 │ 5 │ 6 │ 7 │ 8 │ 9 │10 │11 │12 │13 │14 │15 │  桶索引
└───┴─┬─┴───┴───┴───┴───┴─┬─┴───┴───┴───┴───┴───┴───┴───┴───┴───┘
      │                   │
      ▼                   ▼
   ┌─────┐            ┌─────┐
   │key1 │            │key5 │
   └──┬──┘            └──┬──┘
      ▼                  ▼
   ┌─────┐            ┌─────┐    ←  链表长度 ≤ 6
   │key2 │            │key6 │        (树退化回链表的阈值)
   └──┬──┘            └─────┘
      ▼
   ┌─────┐
   │key3 │
   └──┬──┘
      ▼
   ┌──────┐  ┌──────┐  ┌──────┐  ← 如果链表长度 > 8 且数组长度 ≥ 64
   │key8  │─→│key9  │─→│key10 │     链表 → 红黑树（TreeNode）
   └──┬───┘  └──────┘  └──────┘
      ▼
   红黑树节点...
```

**为什么是8和64这两个数字？** 根据泊松分布，链表长度达到8的概率约为千万分之六——几乎不可能。如果真的到了8，大概率是hashCode设计得不好，此时转红黑树可以防止退化成O(n)查询。

**HashMap的put过程分步详解**：

```java
// 简化的put源码逻辑
public V put(K key, V value) {
    // 第1步：计算hash值
    // hash = (key == null) ? 0 : (h = key.hashCode()) ^ (h >>> 16);
    // 解释：高16位和低16位做异或，让高位参与运算，减少哈希碰撞

    // 第2步：计算桶索引
    // index = (n - 1) & hash;    （n是当前数组长度，2的幂）
    // 等价于 hash % n，但位运算更快

    // 第3步：桶为空 → 直接放
    // if (table[index] == null) → table[index] = newNode(hash, key, value, null);

    // 第4步：桶有元素 → 判断是TreeNode还是普通Node
    // 4a. 是红黑树 → 调用 putTreeVal 插入树
    // 4b. 是链表 → 遍历链表：
    //     - 发现相同key → 覆盖value
    //     - 遍历到末尾 → 追加新节点
    //     - 追加后链表长度 ≥ 8 → treeifyBin()转红黑树
    //       （treeifyBin内部还会检查数组长度是否≥64，不够则扩容）

    // 第5步：size++后是否 > threshold（容量×负载因子）→ resize()扩容
    // 扩容：容量变为2倍，所有元素重新计算桶位置（rehash）
}
```

核心参数：
- **初始容量**：默认16（必须为2的幂，方便位运算取模）
- **负载因子（loadFactor）**：默认0.75（平衡时间和空间，太高碰撞多，太低浪费内存）
- **扩容阈值（threshold）**：容量 × 0.75，例如默认16×0.75=12
- **树化阈值**：8（链表长度达到8考虑树化）
- **退化阈值**：6（红黑树节点数降到6退化回链表）

> 🚨 **坑点：可变对象做HashMap的key**
>
> ```java
> class MutableKey {
>     String name;
>     MutableKey(String name) { this.name = name; }
>     @Override public int hashCode() { return Objects.hash(name); }
>     @Override public boolean equals(Object o) { /* 基于name比较 */ }
> }
>
> Map<MutableKey, String> map = new HashMap<>();
> MutableKey key = new MutableKey("张三");
> map.put(key, "员工A");
>
> key.name = "李四";  // 修改了key的关键属性！
>
> // 此时hashCode变了，但是元素还在原来的桶里
> System.out.println(map.get(key));           // null——新hashCode定位到新桶，找不到
> System.out.println(map.get(new MutableKey("张三"))); // null——桶里有但equals不匹配
> System.out.println(map.get(new MutableKey("李四"))); // null——也找不到
> // 这个元素永远待在一个错误的桶里，直到垃圾回收！
> ```
>
> **教训**：HashMap的key应该用不可变对象（String、Integer、LocalDate等），或者确保对象存入后不再修改参与hashCode和equals计算的属性。

**HashMap遍历性能对比**：

```java
Map<String, Integer> map = new HashMap<>();
// ... 放入大量数据

// 方式一：entrySet（推荐！一次遍历同时拿key和value）
for (Map.Entry<String, Integer> entry : map.entrySet()) {
    String key = entry.getKey();
    Integer value = entry.getValue();
}

// 方式二：keySet + get（每次get都要重新hash查找！效率低）
for (String key : map.keySet()) {
    Integer value = map.get(key);  // 又做了一次hash计算+链表/红黑树查找
}

// 方式三：forEach + Lambda（JDK 8+，内部也是entrySet）
map.forEach((key, value) -> System.out.println(key + " = " + value));
```

`keySet + get` 比 `entrySet` 慢很多：因为拿到key后再调用get，等于把查找过程又执行了一遍。在大数据量下这个差异非常明显。

---

## 5.3 泛型

### 5.3.1 为什么需要泛型

在没有泛型的时代（Java 5之前），集合可以装任意类型：

```java
List list = new ArrayList();
list.add("hello");
list.add(123);        // 不会报错！
String s = (String) list.get(0); // 需要强制类型转换
String s2 = (String) list.get(1); // 运行时 ClassCastException！
```

泛型解决了两个问题：**编译期类型安全检查**和**消除强制转换**。

```java
List<String> list = new ArrayList<>();
list.add("hello");
// list.add(123); // 编译错误！不允许放入Integer
String s = list.get(0); // 不需要强转，编译器保证类型安全
```

### 5.3.2 泛型类、泛型方法、泛型接口

```java
// 泛型类：类名后加 <T>
public class Box<T> {
    private T content;

    public void set(T content) { this.content = content; }
    public T get() { return content; }
}

Box<String> box = new Box<>();  // JDK 7+ 右边可省略类型参数（菱形语法）
box.set("Hello");
String s = box.get();

// 泛型方法：方法返回值前加 <T>
public static <T> T getFirst(List<T> list) {
    return list.isEmpty() ? null : list.get(0);
}

// 泛型接口
public interface Processor<T> {
    void process(T item);
}
```

### 5.3.3 类型擦除

Java的泛型是通过**类型擦除**实现的——编译器编译后，泛型信息就被移除了，所有类型参数被替换为它们的上界（如果没有指定就是Object）。这意味着：

```java
List<String> list1 = new ArrayList<>();
List<Integer> list2 = new ArrayList<>();
System.out.println(list1.getClass() == list2.getClass()); // true——都是ArrayList.class
```

类型擦除带来的限制：

> 🚨 **坑点1：泛型不能使用基本类型**
>
> ```java
> // List<int> list = new ArrayList<>(); // 编译错误！
> List<Integer> list = new ArrayList<>(); // 正确，用包装类
> ```

> 🚨 **坑点2：不能创建泛型数组**
>
> ```java
> // Box<String>[] boxes = new Box<String>[10]; // 编译错误！
> // 解决：用 ArrayList<Box<String>> 代替
> List<Box<String>> boxes = new ArrayList<>();
> ```

> 🚨 **坑点3：不能对泛型类型做instanceof检查**
>
> ```java
> // if (obj instanceof List<String>) // 编译错误！
> if (obj instanceof List)  // 正确（但失去了具体的类型信息）
> ```

### 5.3.4 通配符与PECS原则

通配符有三种形式：

```java
// ? — 任意类型（相当于 ? extends Object）
void printList(List<?> list) {
    for (Object o : list) System.out.println(o);
    // list.add("x"); // 编译错误！不知道具体类型，不能写
}

// ? extends T — 上界通配符：T及其子类
// PECS: Producer Extends — 生产数据（读），不能消费（写）
void readNumbers(List<? extends Number> list) {
    Number n = list.get(0);    // OK —— 读出来的至少是Number
    // list.add(1);            // 编译错误！可能是List<Double>，不能加Integer
}

// ? super T — 下界通配符：T及其父类
// PECS: Consumer Super — 消费数据（写），读只能到Object
void addNumbers(List<? super Integer> list) {
    list.add(1);               // OK —— Integer是Integer及其父类型的安全子类型
    // Integer i = list.get(0); // 编译错误！可能是List<Number>，不能保证是Integer
    Object o = list.get(0);    // OK —— 只能读到Object
}
```

**PECS记忆法**：`Producer Extends, Consumer Super`——如果要从泛型容器中获取数据（生产者），用`extends`；如果要往泛型容器中放入数据（消费者），用`super`。

---

## 5.4 包装类与日期API

### 5.4.1 八种包装类与自动装箱拆箱

| 基本类型 | 包装类 | 大小 |
|---------|--------|------|
| byte | Byte | 1字节 |
| short | Short | 2字节 |
| int | **Integer** | 4字节 |
| long | Long | 8字节 |
| float | Float | 4字节 |
| double | Double | 8字节 |
| char | Character | 2字节 |
| boolean | Boolean | JVM相关 |

```java
// 自动装箱（Auto-boxing）：基本类型 → 包装类
Integer i = 100;  // 编译器自动插入 Integer.valueOf(100)

// 自动拆箱（Auto-unboxing）：包装类 → 基本类型
int j = i;        // 编译器自动插入 i.intValue()

// 混合运算中的自动转换
Integer a = 10;
Integer b = 20;
Integer c = a + b; // 拆箱 → 计算 → 装箱，等价于 Integer.valueOf(a.intValue() + b.intValue())
```

> 🚨 **坑点：Integer缓存 -128~127**
>
> ```java
> Integer a = 127;
> Integer b = 127;
> System.out.println(a == b);  // true —— 缓存范围内，同一个对象
>
> Integer c = 128;
> Integer d = 128;
> System.out.println(c == d);  // false —— 超出缓存范围，是两个不同对象
> ```
>
> Integer内部维护了[-128, 127]共256个Integer对象的缓存。`Integer.valueOf()`在这个范围内返回缓存对象，超出则new新对象。自动装箱调用的是`valueOf()`，所以`Integer i = 127`用到了缓存。
>
> **教训**：比较两个Integer的值，永远用`equals()`而非`==`。

```java
// 包装类的解析方法
int i = Integer.parseInt("123");        // 字符串 → 基本类型
Integer ii = Integer.valueOf("123");    // 字符串 → 包装类

// 常量
System.out.println(Integer.MAX_VALUE);  // 2147483647
System.out.println(Integer.MIN_VALUE);  // -2147483648

// 进制转换
System.out.println(Integer.toBinaryString(10));  // "1010"
System.out.println(Integer.toHexString(255));    // "ff"
```

### 5.4.2 旧日期API的痛

以下旧API知道即可，**新项目禁止使用**：

```java
// Date（JDK 1.0）—— 设计烂，大部分方法已废弃
Date date = new Date();  // 当前时间
System.out.println(date); // Wed May 22 10:30:00 CST 2026

// Calendar（JDK 1.1）—— 月份从0开始！操作繁琐
Calendar cal = Calendar.getInstance();
cal.set(2026, 4, 22);  // 5月是4！反人类设计
```

> 🚨 **坑点：SimpleDateFormat线程不安全**
>
> ```java
> SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM-dd");
> // 多线程环境下同时调用 sdf.format() 或 sdf.parse() 会得到错误结果或抛异常！
> // 原因：SimpleDateFormat内部维护了一个Calendar对象用于格式化，多线程共享会互相干扰
> ```
>
> Java 8+使用**DateTimeFormatter**（不可变，线程安全）：
> ```java
> DateTimeFormatter dtf = DateTimeFormatter.ofPattern("yyyy-MM-dd");
> // 可以安全地在多线程中共享
> ```

### 5.4.3 Java 8+ 新日期API

新API的核心类都是**不可变的**（线程安全！），位于`java.time`包：

```java
import java.time.*;
import java.time.format.DateTimeFormatter;
import java.time.temporal.ChronoUnit;

public class NewDateApiDemo {
    public static void main(String[] args) {
        // ========== 创建日期时间 ==========
        LocalDate today = LocalDate.now();              // 当前日期：2026-05-22
        LocalTime now = LocalTime.now();                // 当前时间：10:30:00.123
        LocalDateTime dateTime = LocalDateTime.now();   // 日期+时间

        LocalDate birthday = LocalDate.of(2000, 1, 15); // 指定日期
        LocalTime meeting = LocalTime.of(14, 30);       // 14:30
        LocalDateTime appointment = LocalDateTime.of(2026, 6, 1, 9, 0);

        // ========== 日期计算（plus/minus） ==========
        LocalDate tomorrow = today.plusDays(1);         // 明天
        LocalDate lastMonth = today.minusMonths(1);     // 上个月
        LocalDate nextWeek = today.plusWeeks(1);        // 下周
        LocalDate tenYearsAgo = today.minus(10, ChronoUnit.YEARS);

        // ========== 比较 ==========
        boolean isAfter = birthday.isAfter(LocalDate.of(1999, 12, 31));
        boolean isBefore = birthday.isBefore(LocalDate.of(2000, 12, 31));

        // ========== 格式化 ==========
        DateTimeFormatter dtf = DateTimeFormatter.ofPattern("yyyy年MM月dd日");
        System.out.println(today.format(dtf));  // "2026年05月22日"

        // 解析字符串为日期
        LocalDate parsed = LocalDate.parse("2026-05-22", DateTimeFormatter.ISO_LOCAL_DATE);

        // ========== 获取日期字段 ==========
        System.out.println(today.getYear());     // 2026
        System.out.println(today.getMonth());    // MAY（Month枚举）
        System.out.println(today.getDayOfWeek());// FRIDAY（DayOfWeek枚举）
        System.out.println(today.getDayOfMonth()); // 22

        // ========== 时间戳与时区 ==========
        Instant instant = Instant.now();         // UTC时间戳
        ZoneId shanghaiZone = ZoneId.of("Asia/Shanghai");
        ZonedDateTime shanghaiTime = ZonedDateTime.now(shanghaiZone);
        System.out.println(shanghaiTime);        // 2026-05-22T10:30:00+08:00[Asia/Shanghai]
    }
}
```

> 🚨 **坑点：LocalDateTime不带时区信息**
>
> ```java
> LocalDateTime ldt = LocalDateTime.now();  // 不带时区，只是一个日期+时间组合
> // 这个"now"是什么时区的now？取决于操作系统/JVM的默认时区
>
> // 如果要在不同时区之间转换，必须用ZonedDateTime或OffsetDateTime
> ZonedDateTime tokyo = ZonedDateTime.now(ZoneId.of("Asia/Tokyo"));
> ZonedDateTime ny = tokyo.withZoneSameInstant(ZoneId.of("America/New_York"));
> ```

**计算两个日期之间的差距**：

```java
LocalDate start = LocalDate.of(2026, 1, 1);
LocalDate end = LocalDate.of(2026, 5, 22);

long daysBetween = ChronoUnit.DAYS.between(start, end);    // 141
long monthsBetween = ChronoUnit.MONTHS.between(start, end); // 4
long yearsBetween = ChronoUnit.YEARS.between(start, end);   // 0

// 获取详细的时间差
Period period = Period.between(start, end);
System.out.println(period.getMonths() + "个月" + period.getDays() + "天"); // 4个月21天
```

---

## 本章小结

本章内容密集，是Java SE中最"实用"的知识板块。回顾要点：

1. **String不可变**是Java最核心的设计之一：final class + final byte[] → 安全、高效、适合做key。循环拼接必须用StringBuilder。
2. **字符串常量池**在不同创建方式下的行为差异是面试经典题：字面量赋值走池、new不走池、intern()强制入池。
3. **split()的参数是正则表达式**，特殊字符需转义；split默认丢弃尾部空元素。
4. **集合框架**记住"底层数据结构 → 时间复杂度 → 适用场景"这条分析链。ArrayList尾部增删O(1)、HashSet去重要写对equals/hashCode、HashMap JDK 8+用数组+链表+红黑树。
5. **HashMap的put过程**：hash → 桶索引 → 空桶直放/链表追加/红黑树插入 → 扩容。可变对象做key是生产事故之源。
6. **泛型通过类型擦除实现**，`? extends T`（生产者）和`? super T`（消费者）的PECS原则是区分高手的分水岭。
7. **Integer缓存-128~127**导致`==`行为不一致——值比较请用`equals()`。
8. **放弃Date/Calendar/SimpleDateFormat**，全面拥抱Java 8+的新日期API，LocalDateTime线程安全且API优雅。

---

## 思考题

1. `String s = new String("abc")` 创建了几个对象？为什么？
2. 下面代码输出什么？
   ```java
   List<String> list = new ArrayList<>(Arrays.asList("A", "B", "C"));
   for (String s : list) {
       if ("A".equals(s)) list.remove(s);
   }
   ```
3. 一个对象存入HashSet后，修改了它的某个属性（该属性参与了hashCode计算），会发生什么？这个对象能被成功remove吗？
4. HashMap中为什么用 `(n - 1) & hash` 而不是 `hash % n` 来计算桶索引？有什么前提条件？
5. 解释 `? extends T` 和 `? super T` 的区别，各举一个使用场景。

<details>
<summary>点击查看参考答案</summary>

1. **两个对象**。字面量`"abc"`在字符串常量池中创建一个对象（如果池中没有），`new String(...)`在堆中创建一个新String对象。如果常量池中已有"abc"，则只创建1个——堆中那个。

2. **抛出ConcurrentModificationException**。for-each遍历时，底层Iterator检测到集合结构被修改（modCount不一致），立即抛出异常。如果想安全删除，可以用`list.removeIf(s -> "A".equals(s))`或显式使用Iterator。

3. **找不到也不能被remove**。属性修改后hashCode变了，对象实际存储位置（旧桶）与hashCode计算出的新位置不一致。remove方法会根据新hashCode去新桶中查找，找不到该对象，返回false。该对象成为"内存泄漏"直到集合被GC。

4. `(n - 1) & hash`等价于`hash % n`但执行更快（位运算 vs 除法）。前提条件是`n`必须是2的幂（如16、32、64），这保证了`n-1`的二进制全是1（如15=1111b），按位与操作等价于取模。

5. `? extends T`用于读数据（生产者），可以从容器中安全读出T类型；`? super T`用于写数据（消费者），可以安全地向容器写入T类型。例如`void copy(List<? extends T> src, List<? super T> dest)`——从src读取T，写入dest。
</details>

---

> 恭喜你掌握了Java核心API！下一章我们将学习异常处理——如何优雅地应对程序中的各种意外情况——以及IO流——让程序具备读写文件的能力。这些都是EMS v1项目的重要基础技能。