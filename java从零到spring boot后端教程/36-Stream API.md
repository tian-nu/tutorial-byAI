# 第36章 Stream API

> 想象你在流水线上加工一批零件：原料进来 → 筛选合格的 → 打磨 → 喷漆 → 打包。你不会每加工一个就跑一趟仓库，而是一条龙处理完。**Stream** 就是 Java 的数据流水线——声明式地描述"做什么"而不是"怎么做"，代码读起来像说明书一样清晰。

---

## 36.1 什么是 Stream

> 🏷️ 此术语需进附录：**Stream**——Java 8 引入的数据处理流水线 API。它不是数据结构（不存数据），而是一个对数据源（集合、数组、IO 等）进行声明式批量计算的工具。Stream 操作分为创建、中间操作、终端操作三个阶段。

```java
// 需求：从名字列表中筛选长度 > 3 的，转大写，排序，取前 2 个
List<String> names = List.of("Bob", "Alice", "Charlie", "David", "Eve");

// Stream 方式 —— 声明式，像写说明书
List<String> result = names.stream()
    .filter(name -> name.length() > 3)   // 筛
    .map(String::toUpperCase)             // 转大写
    .sorted()                              // 排序
    .limit(2)                              // 取前2
    .toList();                             // 收集

System.out.println(result); // [ALICE, CHARLIE]
```

对比传统方式：

```java
// 传统方式 —— 命令式，关注"怎么做"
List<String> result = new ArrayList<>();
for (String name : names) {
    if (name.length() > 3) {
        result.add(name.toUpperCase());
    }
}
Collections.sort(result);
if (result.size() > 2) {
    result = result.subList(0, 2);
}
```

---

## 36.2 Stream 三阶段

```
数据源 ──→ [中间操作1 → 中间操作2 → ...] ──→ 终端操作 ──→ 结果
                  (惰性，构建流水线)           (触发执行)
```

### 36.2.1 创建 Stream

```java
// 从集合
Stream<String> s1 = list.stream();        // 顺序流
Stream<String> s2 = list.parallelStream(); // 并行流

// 从数组
Stream<Integer> s3 = Arrays.stream(new int[]{1, 2, 3}).boxed();
Stream<String> s4 = Stream.of("a", "b", "c");

// 无限流（配合 limit 使用）
Stream<Integer> s5 = Stream.iterate(0, n -> n + 2);   // 0, 2, 4, 6, ...
Stream<Double> s6 = Stream.generate(Math::random);     // 随机数流

// Builder 模式
Stream<String> s7 = Stream.<String>builder()
    .add("a").add("b").add("c")
    .build();
```

### 36.2.2 中间操作（Intermediate Operations）

中间操作**不会立即执行**，只是构建流水线。返回的都是 Stream。

```java
List<String> words = List.of("apple", "banana", "cherry", "date", "elderberry");

// filter：过滤
words.stream()
    .filter(w -> w.length() > 5)
    .forEach(System.out::println);  // banana, cherry, elderberry

// map：转换
words.stream()
    .map(String::toUpperCase)
    .forEach(System.out::println);  // APPLE, BANANA, ...

// flatMap：扁平化（将多个流合并为一个流）
List<List<Integer>> nested = List.of(List.of(1, 2), List.of(3, 4), List.of(5));
nested.stream()
    .flatMap(List::stream)       // 把嵌套的 List 拍平
    .forEach(System.out::print); // 12345

// distinct：去重
Stream.of(1, 2, 2, 3, 3, 3).distinct().forEach(System.out::print); // 123

// sorted：排序
Stream.of(3, 1, 4).sorted().forEach(System.out::print); // 134

// limit / skip：截取
Stream.of(1, 2, 3, 4, 5).skip(2).limit(2).forEach(System.out::print); // 34

// peek：调试（查看流水线中的元素）
words.stream()
    .peek(w -> System.out.println("处理前：" + w))
    .filter(w -> w.length() > 5)
    .peek(w -> System.out.println("过滤后：" + w))
    .count();
```

### 36.2.3 终端操作（Terminal Operations）

终端操作**触发流水线执行**，执行后 Stream 被消费，不能再用。

```java
// forEach：遍历
stream.forEach(System.out::println);

// collect：收集（最常用）
List<String> list = stream.collect(Collectors.toList());
Set<String> set = stream.collect(Collectors.toSet());

// toList()：Java 16+ 更简洁
List<String> list = stream.toList(); // 不可变

// count：计数
long count = stream.count();

// anyMatch / allMatch / noneMatch：匹配
boolean hasLongName = stream.anyMatch(w -> w.length() > 10);
boolean allLong = stream.allMatch(w -> w.length() > 3);

// findFirst / findAny：查找
Optional<String> first = stream.findFirst();

// reduce：归约
Optional<Integer> sum = Stream.of(1, 2, 3).reduce((a, b) -> a + b);
Integer sumWithIdentity = Stream.of(1, 2, 3).reduce(0, Integer::sum);
```

---

## 36.3 Collectors 详解

`Collectors` 是 `collect()` 的参数工厂，提供了丰富的收集器。

### 36.3.1 基础收集

```java
List<String> list = stream.collect(Collectors.toList());
Set<String> set = stream.collect(Collectors.toSet());
Map<String, Integer> map = stream.collect(
    Collectors.toMap(User::getName, User::getAge)
);

// 指定集合类型
ArrayList<String> arrayList = stream.collect(Collectors.toCollection(ArrayList::new));

// 字符串拼接
String joined = stream.collect(Collectors.joining(", ", "[", "]"));
// 示例：[apple, banana, cherry]
```

### 36.3.2 分组（groupingBy）

分组就像 SQL 的 GROUP BY：

```java
record Person(String name, String city, int age) {}

List<Person> people = List.of(
    new Person("Alice", "北京", 25),
    new Person("Bob", "上海", 30),
    new Person("Charlie", "北京", 28),
    new Person("David", "上海", 22)
);

// 按城市分组
Map<String, List<Person>> byCity = people.stream()
    .collect(Collectors.groupingBy(Person::city));

System.out.println(byCity);
// {北京=[Alice, Charlie], 上海=[Bob, David]}

// 分组 + 下游收集器：统计每个城市的平均年龄
Map<String, Double> avgAgeByCity = people.stream()
    .collect(Collectors.groupingBy(
        Person::city,
        Collectors.averagingInt(Person::age)
    ));
System.out.println(avgAgeByCity); // {北京=26.5, 上海=26.0}

// 多级分组
Map<String, Map<Integer, List<Person>>> byCityAndAge = people.stream()
    .collect(Collectors.groupingBy(
        Person::city,
        Collectors.groupingBy(Person::age)
    ));
```

### 36.3.3 分区（partitioningBy）

分区是特殊的分组——只分 true/false 两组：

```java
Map<Boolean, List<Person>> isAdult = people.stream()
    .collect(Collectors.partitioningBy(p -> p.age() >= 18));
// {true=[所有人], false=[]}
```

### 36.3.4 常用聚合

```java
// 统计
IntSummaryStatistics stats = people.stream()
    .collect(Collectors.summarizingInt(Person::age));
System.out.println("平均年龄: " + stats.getAverage());
System.out.println("最大年龄: " + stats.getMax());
System.out.println("总人数: " + stats.getCount());

// 计数
long count = stream.collect(Collectors.counting());

// 最大/最小
Optional<Person> oldest = people.stream()
    .collect(Collectors.maxBy(Comparator.comparingInt(Person::age)));
```

---

## 36.4 并行流

`.parallelStream()` 或 `.stream().parallel()` 可以让流操作在多核 CPU 上并行执行。

```java
List<Integer> numbers = IntStream.rangeClosed(1, 10_000_000)
    .boxed().toList();

// 顺序流
long start = System.currentTimeMillis();
long sum = numbers.stream()
    .mapToLong(Integer::longValue)
    .sum();
System.out.println("顺序流：" + (System.currentTimeMillis() - start) + "ms");

// 并行流
start = System.currentTimeMillis();
sum = numbers.parallelStream()
    .mapToLong(Integer::longValue)
    .sum();
System.out.println("并行流：" + (System.currentTimeMillis() - start) + "ms");
```

> ⚠️ **并行流的陷阱**：
> - 数据量小的时候，并行开销大于收益
> - 共享可变状态会导致线程安全问题
> - `forEach` 不保证顺序，用 `forEachOrdered` 保序

---

## 36.5 ❌ 常见错误

### 错误1：Stream 重复使用

```java
Stream<String> stream = list.stream();
stream.forEach(System.out::println);
// ❌ 第二次使用抛 IllegalStateException: stream has already been operated upon or closed
stream.forEach(System.out::println);

// ✅ 需要多次使用时重新创建
list.stream().forEach(System.out::println);
list.stream().forEach(System.out::println);
```

### 错误2：并行流中使用非线程安全的集合

```java
// ❌ ArrayList 不是线程安全的
List<Integer> result = new ArrayList<>();
IntStream.range(0, 1000)
    .parallel()
    .forEach(result::add);  // 数据可能丢失或异常！

// ✅ 使用 collect 收集
List<Integer> result = IntStream.range(0, 1000)
    .parallel()
    .boxed()
    .collect(Collectors.toList());
```

### 错误3：filter 和 map 顺序搞反

```java
// ❌ 先转换再过滤——做了多余的工作
stream.map(expensiveTransform)  // 全部都要转换
      .filter(condition)
      .collect(...);

// ✅ 先过滤再转换——只转换需要的元素
stream.filter(condition)         // 先筛掉不需要的
      .map(expensiveTransform)   // 再转换剩下的
      .collect(...);
```

### 错误4：toMap key 重复不处理

```java
// ❌ key 重复时抛 IllegalStateException
List<Person> people = List.of(
    new Person("Alice", "北京", 25),
    new Person("Alice", "上海", 30)  // 同名！
);
// Map<String, Person> map = people.stream()
//     .collect(Collectors.toMap(Person::name, p -> p)); // ❌ 异常

// ✅ 指定冲突解决策略
Map<String, Person> map = people.stream()
    .collect(Collectors.toMap(
        Person::name,
        p -> p,
        (existing, replacement) -> replacement  // 后者覆盖前者
    ));
```

---

## 36.6 常用模式总结

```java
// 1. 过滤 + 转换 + 收集
List<DTO> dtos = entities.stream()
    .filter(e -> e.isActive())
    .map(this::toDTO)
    .toList();

// 2. 分组统计
Map<String, Long> countByType = items.stream()
    .collect(Collectors.groupingBy(Item::getType, Collectors.counting()));

// 3. List → Map
Map<Long, User> userMap = users.stream()
    .collect(Collectors.toMap(User::getId, Function.identity()));

// 4. 扁平化
List<String> allTags = articles.stream()
    .flatMap(a -> a.getTags().stream())
    .distinct()
    .toList();

// 5. 求最值
Optional<Product> cheapest = products.stream()
    .min(Comparator.comparing(Product::getPrice));
```

---

## 36.7 小结

| 知识点 | 一句话总结 |
|--------|-----------|
| Stream 三阶段 | 创建 → 中间操作（惰性）→ 终端操作（触发） |
| filter/map/sorted | 最常用的中间操作 |
| collect | 最常用的终端操作，把流收集为集合 |
| groupingBy | 分组，类似 SQL GROUP BY |
| partitioningBy | 二分分区，true/false 两组 |
| 并行流 | 多核加速，但注意线程安全 |
| 最大坑 | Stream 只能消费一次，用完即弃 |

---

## 36.8 自测题

**1.** 以下代码输出什么？

```java
List<Integer> list = List.of(1, 2, 3, 4, 5);
List<Integer> result = list.stream()
    .filter(n -> n % 2 == 0)
    .map(n -> n * n)
    .toList();
System.out.println(result);
```

**2.** 用 Stream 实现：将一个 `List<String>` 中的所有元素按长度分组，返回 `Map<Integer, List<String>>`。

**3.** 以下代码有什么问题？

```java
List<String> names = List.of("Alice", "Bob", "Charlie");
Stream<String> stream = names.stream();
System.out.println(stream.count());
System.out.println(stream.collect(Collectors.joining(", ")));
```

> 答案提示：1. `[4, 16]`；2. `list.stream().collect(Collectors.groupingBy(String::length))`；3. `count()` 是终端操作，消费了 Stream，第二次调用 `collect()` 会抛 `IllegalStateException`。