# 第33章 集合框架（三）：Map

> 想查一个人的电话号码，你不会翻整个电话号码本一页页找，而是直接按名字首字母定位。Map 就是这样的"名字→号码"对照表——给定一个 **key**，瞬间找到对应的 **value**。没有索引，没有顺序（大多数实现），只有键值对。

---

## 33.1 Map 接口概述

`Map` **不是** `Collection` 的子接口——它是独立体系。核心特征：**键值对映射，键不能重复**。

| 特性 | 说明 |
|------|------|
| 键唯一 | 同一个 key 只能对应一个 value，重复 put 会覆盖 |
| 值可重复 | 不同 key 可以映射到相同的 value |
| 允许 null | HashMap 允许 1 个 null key + 多个 null value；TreeMap 不允许 null key |

`Map` 三个常用实现：

| 实现类 | 底层 | 顺序 | null key | 特点 |
|--------|------|------|----------|------|
| `HashMap` | 数组+链表+红黑树 | 无序 | 允许 | O(1)，最常用 |
| `LinkedHashMap` | HashMap+双向链表 | 插入顺序/访问顺序 | 允许 | 有序的 HashMap |
| `TreeMap` | 红黑树 | 键自然排序 | 不允许 | O(log n)，范围查询 |

---

## 33.2 HashMap

### 33.2.1 核心原理

> 🏷️ 此术语需进附录：**HashMap**——基于"数组+链表+红黑树"实现的键值对映射。通过 key 的 hashCode 确定桶位置，哈希冲突时用链表解决，链表过长（≥8）时转为红黑树。

简单理解：一个酒店有 16 层（默认容量），每个客人（key）的房号 = 名字的哈希值 % 16。两个客人可能被分到同一层（哈希冲突），同一层的人用链表串联。当同一层超过 8 个人时，改用更高效的红黑树查找。

```
HashMap 内部结构示意：
bucket[0]  → (k1,v1) → (k2,v2)   ← 链表
bucket[1]  → null
bucket[2]  → (k3,v3)
...
bucket[n]  → TreeNode → TreeNode  ← 红黑树（链表长度 ≥ 8 时）
```

### 33.2.2 基本用法

```java
import java.util.HashMap;
import java.util.Map;

Map<String, Integer> map = new HashMap<>();

// 增/改
map.put("Alice", 25);
map.put("Bob", 30);
map.put("Alice", 26);    // 覆盖旧值
System.out.println(map); // {Bob=30, Alice=26}

// 查
int age = map.get("Alice");             // 26
int unknown = map.getOrDefault("Tom", 0); // 0（不存在时返回默认值）
boolean hasBob = map.containsKey("Bob");  // true

// 安全地 put（不存在才放）
map.putIfAbsent("Alice", 100); // Alice 已存在，不生效
map.putIfAbsent("Tom", 20);    // Tom 不存在，放入

// 删
map.remove("Bob");

// 大小
System.out.println(map.size()); // 2
```

### 33.2.3 遍历 Map

**强烈推荐 `entrySet()` 方式**——效率最高，一次遍历同时拿到 key 和 value。

```java
Map<String, Integer> scores = new HashMap<>();
scores.put("语文", 90);
scores.put("数学", 85);
scores.put("英语", 92);

// ✅ 推荐方式1：entrySet（效率最高）
for (Map.Entry<String, Integer> entry : scores.entrySet()) {
    System.out.println(entry.getKey() + " = " + entry.getValue());
}

// ✅ 推荐方式2：forEach + Lambda（Java 8+）
scores.forEach((key, value) -> System.out.println(key + " = " + value));

// ⚠️ 可行但效率稍低：遍历 keySet 再 get
for (String key : scores.keySet()) {
    System.out.println(key + " = " + scores.get(key)); // 每次 get 都要哈希查找
}

// ⚠️ 只遍历值：values()
for (Integer value : scores.values()) {
    System.out.println(value);
}
```

> 🤔 **想多一点**：为什么 `keySet + get` 效率低？因为 `get()` 内部需要 `hash(key) → 定位桶 → 遍历链表/树`。而 `entrySet` 遍历时已经拿到了节点，直接访问即可，省去了一次哈希查找。

---

## 33.3 LinkedHashMap

`LinkedHashMap` 在 `HashMap` 的基础上，用双向链表维护了元素的顺序。可以按**插入顺序**或**访问顺序**排列。

```java
import java.util.LinkedHashMap;
import java.util.Map;

// 按插入顺序
Map<String, Integer> map = new LinkedHashMap<>();
map.put("C", 3);
map.put("A", 1);
map.put("B", 2);

// 遍历顺序 = 插入顺序
map.forEach((k, v) -> System.out.print(k + " ")); // C A B
```

**LRU 缓存（访问顺序模式）**：

```java
// accessOrder=true：按访问顺序排序（最近访问的放最后）
LinkedHashMap<String, Integer> lruCache = new LinkedHashMap<>(16, 0.75f, true) {
    @Override
    protected boolean removeEldestEntry(Map.Entry<String, Integer> eldest) {
        return size() > 3; // 超过3个元素时，自动删除最老的
    }
};

lruCache.put("A", 1);
lruCache.put("B", 2);
lruCache.put("C", 3);
lruCache.get("A");        // 访问 A，A 被移到末尾
lruCache.put("D", 4);     // 超过3个，删除最老的（B）

System.out.println(lruCache); // {C=3, A=1, D=4} —— B 被自动移除了
```

> 🏷️ 此术语需进附录：**LRU 缓存**（Least Recently Used）—— 最近最少使用淘汰策略。缓存满时，删除最长时间未被访问的数据。LinkedHashMap 开启 accessOrder 后天然支持。

---

## 33.4 TreeMap

`TreeMap` 按 key 的**自然顺序**（或自定义 `Comparator`）排序，底层是红黑树。

```java
import java.util.TreeMap;
import java.util.Map;

Map<String, Integer> map = new TreeMap<>();
map.put("C", 3);
map.put("A", 1);
map.put("B", 2);

System.out.println(map); // {A=1, B=2, C=3} —— 自动按 key 排序
```

范围查询（TreeMap 独有）：

```java
TreeMap<Integer, String> tree = new TreeMap<>();
tree.put(10, "十");
tree.put(20, "二十");
tree.put(30, "三十");
tree.put(40, "四十");

System.out.println(tree.firstKey());          // 10
System.out.println(tree.lastKey());           // 40
System.out.println(tree.headMap(30));         // {10=十, 20=二十}（小于30）
System.out.println(tree.tailMap(30));         // {30=三十, 40=四十}（≥30）
System.out.println(tree.subMap(15, 35));      // {20=二十, 30=三十}
System.out.println(tree.ceilingKey(15));      // 20（≥15的最小key）
System.out.println(tree.floorKey(15));        // 10（≤15的最大key）
```

---

## 33.5 HashMap key 的不可变性

**用可变对象做 HashMap 的 key 是件危险的事。**

```java
import java.util.*;

class MutableKey {
    String name;
    MutableKey(String name) { this.name = name; }

    @Override
    public int hashCode() { return Objects.hash(name); }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (!(o instanceof MutableKey)) return false;
        return Objects.equals(name, ((MutableKey) o).name);
    }
}

// ❌ 危险操作
Map<MutableKey, Integer> map = new HashMap<>();
MutableKey key = new MutableKey("Alice");
map.put(key, 25);

key.name = "Bob";  // 修改了 key！
System.out.println(map.get(key)); // null！找不到了！
// hashCode 变了，HashMap 去新的桶位置找，自然是 null
// 但旧数据还留在旧的桶位置——造成了"内存泄漏"
```

> ✅ **最佳实践**：使用不可变对象作为 key，比如 `String`、`Integer`、`LocalDate` 等。如果需要自定义类型作 key，确保放入后不再修改其参与 hashCode/equals 的字段。

---

## 33.6 ❌ 常见错误

### 错误1：用 keySet + get 遍历

```java
Map<String, Integer> map = new HashMap<>();
// ❌ 效率较低
for (String key : map.keySet()) {
    Integer value = map.get(key); // 每次都要哈希查找
}

// ✅ 一次查完
for (Map.Entry<String, Integer> entry : map.entrySet()) {
    String key = entry.getKey();
    Integer value = entry.getValue();
}
```

### 错误2：HashMap 线程不安全

```java
// ❌ HashMap 不是线程安全的
Map<String, Integer> map = new HashMap<>();
// 多线程同时 put 可能导致：
// 1. 数据丢失
// 2. 链表成环 → CPU 100%（JDK 7）

// ✅ 需要线程安全时用 ConcurrentHashMap
Map<String, Integer> safeMap = new ConcurrentHashMap<>();
```

### 错误3：TreeMap key 不能为 null

```java
TreeMap<String, Integer> tree = new TreeMap<>();
tree.put(null, 1);  // ❌ NullPointerException！TreeMap 不允许 null key

// HashMap 允许一个 null key
HashMap<String, Integer> hashMap = new HashMap<>();
hashMap.put(null, 1);  // ✅
```

### 错误4：可变 key 导致数据丢失

已在 33.5 节详述。核心：放入 HashMap 后不要再修改 key 的 hashCode 相关字段。

---

## 33.7 小结

| 知识点 | 一句话总结 |
|--------|-----------|
| HashMap | 数组+链表+红黑树，O(1)，无序，最常用 |
| LinkedHashMap | HashMap + 双向链表，保持插入/访问顺序，可实现 LRU 缓存 |
| TreeMap | 红黑树，按 key 排序 O(log n)，支持范围操作 |
| 遍历推荐 | entrySet() 效率最高，一次同时拿到 key 和 value |
| key 不可变 | 用可变对象做 key 修改后数据可能找不回来 |
| 线程安全 | HashMap 非线程安全，用 ConcurrentHashMap |

---

## 33.8 自测题

**1.** 以下代码输出什么？

```java
Map<String, Integer> map = new HashMap<>();
map.put("A", 1);
map.put("B", 2);
map.put("A", 3);
map.put(null, 4);
map.put(null, 5);
System.out.println(map.size() + " " + map.get(null) + " " + map.get("A"));
```

**2.** 如何用 `LinkedHashMap` 实现一个最大容量为 100 的 LRU 缓存？

**3.** `HashMap` 遍历时，为什么说 `entrySet()` 比 `keySet() + get()` 效率高？请从内部实现角度解释。

> 答案提示：1. 输出 "2 5 3"——A 重复被覆盖，null key 也只有一个；2. 设置 accessOrder=true，重写 removeEldestEntry 当 size()>100 返回 true；3. entrySet 遍历时节点已获取，而 keySet+get 每次 get 都要重新 hash 定位桶位置。