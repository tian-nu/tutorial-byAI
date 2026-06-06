# 附录A · Java标准库速查

> "Java标准库就像一座超大型图书馆——几乎所有日常开发需要的工具都在里面。本附录按功能分类列出最常用的类和函数，作为你日常编码时的快速参考。"

---

## A.1 java.lang — 自动导入的基础包

java.lang是唯一不需要手动import的包，Java自动为你导入。所有最基础的类都在这里。

### 字符串处理

| 方法 | 作用 | 返回值示例 |
|------|------|-----------|
| `"hello".length()` | 字符数 | `5` |
| `"hello".charAt(1)` | 第1个字符（从0开始） | `'e'` |
| `"hello".substring(1, 4)` | 截取[1,4) | `"ell"` |
| `"hello".indexOf("l")` | 首次出现位置 | `2` |
| `"hello".lastIndexOf("l")` | 最后出现位置 | `3` |
| `"hello".contains("ll")` | 是否包含 | `true` |
| `"hello".startsWith("he")` | 是否以he开头 | `true` |
| `"hello".endsWith("lo")` | 是否以lo结尾 | `true` |
| `String.join(",", "a", "b")` | 用分隔符连接 | `"a,b"` |
| `"a,b,c".split(",")` | 按分隔符拆分 | `["a","b","c"]` |
| `"hello".replace("l", "x")` | 替换所有 | `"hexxo"` |
| `"hello".replaceAll("l+", "x")` | 正则替换 | `"he.xo"` |
| `"  hi  ".trim()` | 去首尾空格 | `"hi"` |
| `"hello".toUpperCase()` | 转大写 | `"HELLO"` |
| `"hello".toLowerCase()` | 转小写 | `"hello"` |
| `"hello".equals("hello")` | 内容相等（不是==） | `true` |
| `"hello".equalsIgnoreCase("HELLO")` | 忽略大小写比较 | `true` |
| `"hello".isEmpty()` | 长度是否为0 | `false` |
| `"hello".isBlank()` | 是否空白（Java 11+） | `false` |
| `"hello %s".formatted("world")` | 格式化（Java 15+） | `"hello world"` |
| `String.format("age: %d", 25)` | 格式化 | `"age: 25"` |

### StringBuilder — 高效拼接字符串

不要用 `s += "xxx"` 在循环里拼接字符串，String是不可变的，每次 `+=` 都会创建新对象。`StringBuilder` 内部用可变字符数组，性能高百倍。

| 方法 | 作用 |
|------|------|
| `new StringBuilder()` | 创建空的 |
| `new StringBuilder("hello")` | 带初始值 |
| `sb.append("xxx")` | 追加 |
| `sb.insert(0, "xxx")` | 在指定位置插入 |
| `sb.delete(0, 3)` | 删除[0,3) |
| `sb.reverse()` | 反转 |
| `sb.toString()` | 转为String |
| `sb.length()` | 当前长度 |

```java
var sb = new StringBuilder();
sb.append("Hello ");
sb.append("World");
System.out.println(sb.toString()); // Hello World
```

StringBuffer是StringBuilder的线程安全版本，方法几乎一样，但日常开发用StringBuilder即可。

### Integer / Double / Boolean — 基本类型的"包装类"

| 方法 | 作用 | 示例 |
|------|------|------|
| `Integer.parseInt("123")` | 字符串→int | `123` |
| `Integer.valueOf("123")` | 字符串→Integer对象 | `123` |
| `Integer.toString(123)` | int→字符串 | `"123"` |
| `Integer.MAX_VALUE` | int最大值 | `2147483647` |
| `Integer.MIN_VALUE` | int最小值 | `-2147483648` |
| `Integer.compare(a, b)` | 比较两个int | 0/-1/1 |
| `Double.parseDouble("3.14")` | 字符串→double | `3.14` |
| `Boolean.parseBoolean("true")` | 字符串→boolean | `true` |

### Math — 数学计算

| 方法 | 作用 |
|------|------|
| `Math.abs(x)` | 绝对值 |
| `Math.max(a, b)` | 最大值 |
| `Math.min(a, b)` | 最小值 |
| `Math.ceil(3.14)` | 向上取整 → 4.0 |
| `Math.floor(3.14)` | 向下取整 → 3.0 |
| `Math.round(3.5)` | 四舍五入 → 4 |
| `Math.pow(2, 3)` | 2的3次方 → 8.0 |
| `Math.sqrt(16)` | 平方根 → 4.0 |
| `Math.random()` | [0.0, 1.0)随机数 |
| `Math.PI` | 圆周率 |

### Object — 万物之父

Java中所有类的终极父类。每个对象都继承了这些方法：

| 方法 | 作用 |
|------|------|
| `obj.toString()` | 默认返回 `类名@哈希值`，常被重写 |
| `obj.equals(other)` | 默认比较地址（==），String重写为比较内容 |
| `obj.hashCode()` | 返回哈希值，equals为true则hashCode必须相同（这是约定） |
| `obj.getClass()` | 返回运行时Class对象 |

### System — 与系统打交道

| 方法/字段 | 作用 |
|-----------|------|
| `System.out.println()` | 标准输出 |
| `System.err.println()` | 标准错误输出 |
| `System.currentTimeMillis()` | 当前毫秒时间戳 |
| `System.nanoTime()` | 纳秒计时（用于测性能） |
| `System.getenv("JAVA_HOME")` | 读取环境变量 |
| `System.getProperty("user.dir")` | 读取系统属性 |
| `System.exit(0)` | 退出程序 |
| `System.gc()` | 建议JVM执行GC（不保证立即执行） |
| `System.arraycopy(src, srcPos, dest, destPos, length)` | 高效数组拷贝 |

### Thread — 线程基础

| 方法 | 作用 |
|------|------|
| `Thread.sleep(1000)` | 当前线程休眠1秒 |
| `thread.start()` | 启动线程（调用run方法，不是直接调run） |
| `thread.join()` | 等待该线程执行完毕 |
| `Thread.currentThread().getName()` | 获取当前线程名 |
| `thread.setDaemon(true)` | 设为守护线程 |

---

## A.2 java.util — 集合与工具

### ArrayList — 动态数组（最常用）

| 方法 | 作用 |
|------|------|
| `new ArrayList<>()` | 创建空列表 |
| `list.add(e)` | 末尾添加 |
| `list.add(0, e)` | 在指定位置插入 |
| `list.get(0)` | 按索引获取 |
| `list.set(0, e)` | 按索引修改 |
| `list.remove(0)` | 按索引删除（返回被删元素） |
| `list.remove(obj)` | 按对象删除（只删第一个匹配的） |
| `list.size()` | 元素个数 |
| `list.isEmpty()` | 是否为空 |
| `list.contains(obj)` | 是否包含 |
| `list.indexOf(obj)` | 首次出现位置，-1表示不存在 |
| `list.clear()` | 清空 |
| `list.forEach(e -> ...)` | Lambda遍历 |
| `new ArrayList<>(anotherList)` | 从另一个集合复制构造 |

### HashMap — 键值对（最常用）

| 方法 | 作用 |
|------|------|
| `new HashMap<>()` | 创建空Map |
| `map.put(key, value)` | 放入键值对（返回旧值或null） |
| `map.get(key)` | 取值，不存在返回null |
| `map.getOrDefault(key, default)` | 取值，不存在返回默认值 |
| `map.remove(key)` | 删除 |
| `map.containsKey(key)` | 是否包含键 |
| `map.containsValue(value)` | 是否包含值 |
| `map.size()` | 键值对个数 |
| `map.keySet()` | 所有键的Set |
| `map.values()` | 所有值的Collection |
| `map.entrySet()` | 所有键值对（用于遍历） |
| `map.forEach((k, v) -> ...)` | Lambda遍历 |
| `map.putIfAbsent(key, value)` | 仅当键不存在时放入 |

### Collections — 集合工具类

| 方法 | 作用 |
|------|------|
| `Collections.sort(list)` | 排序（元素必须实现Comparable） |
| `Collections.sort(list, comparator)` | 按自定义规则排序 |
| `Collections.reverse(list)` | 反转 |
| `Collections.shuffle(list)` | 随机打乱 |
| `Collections.max(list)` / `min(list)` | 最大/最小值 |
| `Collections.unmodifiableList(list)` | 返回不可修改的视图 |
| `Collections.synchronizedList(list)` | 返回线程安全的包装 |
| `Collections.emptyList()` / `emptyMap()` | 不可变的空集合 |

### Date / LocalDate / LocalDateTime — 日期时间

Java 8之前用`java.util.Date`（已过时），现在统一用`java.time`包：

| 类 | 说明 | 创建方式 |
|----|------|---------|
| `LocalDate` | 只有日期（年-月-日），没有时间 | `LocalDate.now()`, `LocalDate.of(2024, 1, 1)` |
| `LocalTime` | 只有时间（时:分:秒） | `LocalTime.now()`, `LocalTime.of(14, 30)` |
| `LocalDateTime` | 日期+时间 | `LocalDateTime.now()`, `LocalDateTime.of(date, time)` |
| `Instant` | 时间戳（从1970-01-01T00:00:00Z开始） | `Instant.now()`, `Instant.ofEpochMilli(ms)` |
| `Duration` | 时间差（精确到纳秒） | `Duration.between(start, end)` |
| `Period` | 日期差（年/月/日） | `Period.between(start, end)` |

**常用操作**：

| 方法 | 作用 |
|------|------|
| `date.plusDays(7)` | 加7天 |
| `date.minusMonths(1)` | 减1个月 |
| `date.getYear()` / `getMonthValue()` / `getDayOfMonth()` | 获取年月日 |
| `date.isBefore(other)` / `isAfter(other)` | 日期比较 |
| `LocalDate.parse("2024-01-01")` | 字符串解析 |
| `date.format(DateTimeFormatter.ofPattern("yyyy/MM/dd"))` | 格式化输出 |
| `LocalDate.now().toEpochDay()` | 从1970-01-01起的天数 |

### DateTimeFormatter — 日期格式化

| 模式字符 | 含义 | 示例 |
|----------|------|------|
| `yyyy` | 四位年份 | `2024` |
| `MM` | 两位月份 | `01` |
| `dd` | 两位日 | `15` |
| `HH` | 24小时制小时 | `14` |
| `mm` | 分钟 | `30` |
| `ss` | 秒 | `05` |

```java
var dtf = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");
System.out.println(LocalDateTime.now().format(dtf));
// 2024-01-15 14:30:05
```

### Random — 随机数

| 方法 | 作用 |
|------|------|
| `new Random()` | 创建随机数生成器 |
| `random.nextInt(100)` | [0, 100)的随机整数 |
| `random.nextInt()` | 任意int范围的随机数 |
| `random.nextDouble()` | [0.0, 1.0)的随机浮点数 |
| `random.nextBoolean()` | 随机true/false |

### Scanner — 读取输入

| 方法 | 作用 |
|------|------|
| `new Scanner(System.in)` | 从标准输入读取 |
| `scanner.nextLine()` | 读一行字符串 |
| `scanner.nextInt()` | 读一个int |
| `scanner.nextDouble()` | 读一个double |
| `scanner.hasNext()` | 是否还有下一个token |
| `scanner.close()` | 关闭Scanner |

---

## A.3 java.io / java.nio.file — 文件操作

### Files（java.nio.file，Java 7+推荐）

| 方法 | 作用 |
|------|------|
| `Files.readString(path)` | 读整个文件为String（Java 11+） |
| `Files.readAllLines(path)` | 读所有行→`List<String>` |
| `Files.writeString(path, content)` | 写String到文件 |
| `Files.copy(src, dst)` | 复制文件 |
| `Files.move(src, dst)` | 移动/重命名 |
| `Files.delete(path)` | 删除文件（不存在则抛异常） |
| `Files.deleteIfExists(path)` | 存在则删除 |
| `Files.exists(path)` | 是否存在 |
| `Files.isDirectory(path)` / `isRegularFile(path)` | 是否目录/普通文件 |
| `Files.size(path)` | 文件字节数 |
| `Files.createDirectory(path)` | 创建目录 |
| `Files.createDirectories(path)` | 递归创建目录 |
| `Files.list(path)` | 列出目录下文件（返回Stream） |
| `Files.walk(path)` | 递归遍历目录树（返回Stream） |
| `Files.newBufferedReader(path)` | 创建BufferedReader |
| `Files.newBufferedWriter(path)` | 创建BufferedWriter |

### Path（替代java.io.File）

| 方法 | 作用 |
|------|------|
| `Path.of("dir", "file.txt")` | 创建Path（Java 11+） |
| `Path.of("a").resolve("b")` | 拼接路径 → `a/b` |
| `path.getParent()` | 父目录 |
| `path.getFileName()` | 文件名 |
| `path.toAbsolutePath()` | 绝对路径 |
| `path.toFile()` | 转为File对象（兼容旧API） |

### 传统IO（java.io，了解即可）

| 类 | 作用 |
|----|------|
| `FileInputStream("a.txt")` | 字节输入流 |
| `FileOutputStream("a.txt")` | 字节输出流 |
| `FileReader("a.txt")` | 字符输入流 |
| `FileWriter("a.txt")` | 字符输出流 |
| `BufferedReader(new FileReader("a.txt"))` | 带缓冲的字符读 |
| `BufferedWriter(new FileWriter("a.txt"))` | 带缓冲的字符写 |
| `bufferedReader.readLine()` | 读一行（返回null表示末尾） |

---

## A.4 java.util.stream — Stream API（Java 8+）

### Stream创建

| 方法 | 作用 |
|------|------|
| `list.stream()` | 从集合创建流 |
| `Arrays.stream(array)` | 从数组创建流 |
| `Stream.of("a", "b", "c")` | 从值创建流 |
| `IntStream.range(0, 10)` | [0, 10)的整数流 |
| `Stream.generate(supplier)` | 无限流（需limit截断） |
| `Stream.iterate(seed, f)` | 迭代生成无限流 |

### 中间操作（返回Stream，可链式调用）

| 方法 | 作用 |
|------|------|
| `filter(predicate)` | 过滤 |
| `map(function)` | 转换每个元素 |
| `flatMap(function)` | 扁平化（每个元素展开为子Stream再合并） |
| `distinct()` | 去重 |
| `sorted()` / `sorted(comparator)` | 排序 |
| `limit(n)` | 截取前n个 |
| `skip(n)` | 跳过前n个 |
| `peek(consumer)` | 查看每个元素（调试用） |

### 终端操作（执行后流关闭）

| 方法 | 作用 |
|------|------|
| `collect(Collectors.toList())` | 收集为List |
| `collect(Collectors.toSet())` | 收集为Set |
| `collect(Collectors.toMap(k, v))` | 收集为Map |
| `collect(Collectors.groupingBy(classifier))` | 分组 |
| `collect(Collectors.joining(","))` | 连接为字符串 |
| `forEach(consumer)` | 遍历 |
| `count()` | 计数 |
| `anyMatch(predicate)` / `allMatch(predicate)` / `noneMatch(predicate)` | 匹配 |
| `findFirst()` / `findAny()` | 查找（返回Optional） |
| `reduce(identity, accumulator)` | 归约（累加/累乘等） |

### 典型示例

```java
// 过滤+转换+收集
var names = users.stream()
    .filter(u -> u.getAge() > 18)
    .map(User::getName)
    .sorted()
    .collect(Collectors.toList());

// 分组
var byCity = users.stream()
    .collect(Collectors.groupingBy(User::getCity));

// 统计
long count = users.stream()
    .filter(u -> u.getAge() > 18)
    .count();
```

---

## A.5 java.util.concurrent — 并发工具

### ExecutorService — 线程池（推荐代替手动new Thread）

| 方法 | 作用 |
|------|------|
| `Executors.newFixedThreadPool(4)` | 固定大小线程池 |
| `Executors.newCachedThreadPool()` | 弹性线程池（空闲60秒回收） |
| `Executors.newSingleThreadExecutor()` | 单线程池（任务按序执行） |
| `executor.execute(runnable)` | 提交无返回值任务 |
| `executor.submit(callable)` | 提交有返回值任务（返回Future） |
| `executor.shutdown()` | 优雅关闭（等待已提交任务完成） |
| `executor.shutdownNow()` | 立即关闭（中断正在执行的任务） |
| `executor.awaitTermination(10, TimeUnit.SECONDS)` | 等待任务完成 |

### CompletableFuture（Java 8+，异步编程核心）

| 方法 | 作用 |
|------|------|
| `CompletableFuture.supplyAsync(supplier)` | 异步执行，有返回值 |
| `CompletableFuture.runAsync(runnable)` | 异步执行，无返回值 |
| `future.thenApply(fn)` | 结果转换（同步，有返回值） |
| `future.thenAccept(consumer)` | 结果消费（同步，无返回值） |
| `future.thenCompose(fn)` | 结果用于产生新的Future |
| `future.thenCombine(other, fn)` | 合并两个Future的结果 |
| `future.exceptionally(fn)` | 异常处理 |
| `CompletableFuture.allOf(futures...)` | 等待所有完成 |
| `CompletableFuture.anyOf(futures...)` | 等待任一完成 |
| `future.get(5, TimeUnit.SECONDS)` | 阻塞等待结果（带超时） |

### ConcurrentHashMap — 并发安全的Map

方法同HashMap，但线程安全。大量并发读写场景下比`synchronized`包装的HashMap性能好很多。

---

## A.6 其他常用包速览

| 包 | 核心类 | 作用 | 书中位置 |
|----|--------|------|---------|
| `java.math` | `BigDecimal` | 精确小数（金额计算必用，永远不要用double算钱） | 第17章 |
| `java.util.regex` | `Pattern`, `Matcher` | 正则表达式 | — |
| `java.util.function` | `Function<T,R>`, `Predicate<T>`, `Consumer<T>`, `Supplier<T>` | 函数式接口（Lambda的基础） | 第35章 |
| `java.util.Optional` | `Optional<T>` | 优雅处理null，避免NullPointerException | 第36章 |
| `java.util.Objects` | `Objects.requireNonNull()`, `Objects.equals()` | 对象通用工具 | — |
| `java.net` | `HttpURLConnection`, `URI`, `URL` | 网络请求（了解即可，生产用Spring） | 第11章 |
| `java.security` | `MessageDigest` | 哈希（SHA-256等） | 第92章 |
| `javax.crypto` | `Cipher`, `KeyGenerator` | 加密解密（AES等） | 第92章 |
| `org.slf4j` | `Logger`, `LoggerFactory` | 日志门面（Spring Boot标配） | 第83章 |

---

本节速查覆盖了Java日常开发中最常用的标准库类和方法。当你需要某个功能时，先来这边翻一下——Java标准库通常已经有现成的实现，不需要引入第三方依赖。

---

[下一章：附录B-MySQL命令速查.md →](附录B-MySQL命令速查/)