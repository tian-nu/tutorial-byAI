# 第24章 · Map：键值对

> "有时候你想用'名字'而不是'编号'来找东西。比如'查一下张三的成绩'而不是'查一下第3号同学的成绩'。Map就是存'名字→值'这种对应关系的数据结构。"

---

## 24.1 声明与初始化：nil map是个坑

### 声明

```go
var scores map[string]int
```

`map[string]int` 的意思是：键（key）的类型是 `string`，值（value）的类型是 `int`。

**但这样声明出来的map是nil！** nil map不能往里面存数据：

```go
var scores map[string]int
scores["张三"] = 90  // panic: assignment to entry in nil map
```

程序会直接崩溃。记住：nil map能读（返回零值），不能写。

### 初始化——必须用make或字面量

**方式一：make**

```go
scores := make(map[string]int)
scores["张三"] = 90
scores["李四"] = 85
```

**方式二：字面量**

```go
scores := map[string]int{
    "张三": 90,
    "李四": 85,
    "王五": 78,
}
```

注意花括号最后一行也要加逗号（这是Go语法要求）。

### 两种方式对比

```go
var m1 map[string]int           // nil map，不能写！
m2 := make(map[string]int)      // 空map，可以写
m3 := map[string]int{}          // 空map，可以写
m4 := map[string]int{"a": 1}    // 有初始值的map
```

---

## 24.2 增删改查：Map的基本操作

### 增/改

```go
scores := make(map[string]int)

scores["张三"] = 90   // 新增：张三不在map里
scores["李四"] = 85   // 新增
scores["张三"] = 95   // 修改：张三已经在map里了
```

### 查（判断是否存在）

读取map的值有两种写法：

**简单读：**

```go
score := scores["张三"]
fmt.Println(score)  // 95
```

但如果key不存在，返回的是**零值**：

```go
score := scores["赵六"]     // 赵六不在map里
fmt.Println(score)           // 0（int的零值）
```

这里有个问题：返回0是因为key不存在，还是key存在且值就是0？无法区分！

**推荐姿势：comma ok idiom**

```go
score, ok := scores["张三"]
if ok {
    fmt.Println("张三存在，分数：", score)
} else {
    fmt.Println("张三不存在")
}
```

这是Go里最经典的"判断map里有没有某个key"的写法。第二个返回值 `ok` 是 `bool` 类型：
- `true`：key存在，第一个返回值是有效值
- `false`：key不存在，第一个返回值是零值

### 删

用 `delete` 函数删除键值对：

```go
delete(scores, "张三")
```

`delete` 是Go的内置函数，即使key不存在也不会报错——什么都不会发生。

```go
delete(scores, "不存在的人")  // 安全，什么都不会发生
```

### 获取长度

```go
count := len(scores)
```

只返回键值对的数量。没有 `cap`（map不是切片那种结构）。

---

## 24.3 遍历Map：顺序是随机的（故意的！）

```go
scores := map[string]int{
    "张三": 90,
    "李四": 85,
    "王五": 78,
}

for name, score := range scores {
    fmt.Printf("%s: %d分\n", name, score)
}
```

每次运行这段代码，输出顺序**可能不同**。今天是"张三→李四→王五"，明天可能是"王五→张三→李四"。

这不是Bug。Go故意让遍历顺序随机，**防止程序员依赖map的遍历顺序**。其他很多语言虽然不保证但"凑巧"是插入顺序，程序员就开始依赖它了。Go一刀切断——随机，你就别幻想有顺序了。

如果你需要按固定顺序输出，就要自己排：

```go
keys := make([]string, 0, len(scores))
for k := range scores {
    keys = append(keys, k)
}
sort.Strings(keys)

for _, k := range keys {
    fmt.Printf("%s: %d\n", k, scores[k])
}
```

先收集所有key，排序，再按排好序的key去查map。

### 只遍历key或只遍历value

```go
for k := range scores {
    fmt.Println("人名:", k)
}

for _, v := range scores {
    fmt.Println("分数:", v)
}
```

---

## 24.4 Map的底层原理：哈希表

Map的底层是**哈希表（Hash Table）**。

### 哈希表的工作原理

给Map一个字符串key（比如 `"张三"`），Map把它交给**哈希函数**算出一个数字。这个数字就用来定位数据存在哪个位置。

好比图书馆给每本书一个编号（哈希值），下次你报书名，管理员一查编号就知道这本书在哪个书架的哪个位置。

查找过程：
1. 输入key `"张三"`
2. 计算哈希值：`hash("张三")` → 一个大数，如 `1738562941`
3. 用哈希值定位到存储位置
4. 找到对应的value `90`

所以从Map里查数据的速度基本是 `O(1)`——不管Map里有10条还是100万条数据，查找时间差不多。

### 哈希冲突

两个不同的key算出了同一个哈希值怎么办？这叫**哈希冲突**。Go用**链地址法**解决：

发生冲突时，同一个位置变成一个链表（或更准确地说，连续的bucket），挨个比较key看哪个是对的。

### 扩容

当你往Map里不断加数据，Map装不下了就会**扩容**——Go分配一块更大的内存，把所有数据重新哈希然后搬过去。

```
扩容前:  8个桶（buckets），每条链平均2个元素
扩容后: 16个桶（buckets），每条链平均1个元素
```

Map扩容不是在插入时立刻完成的，而是**渐进式**的——每次插入或删除时搬一点。

> 🤔 **想多一点**：Map的渐进式扩容（incremental）是个很巧妙的设计。想象你搬家，有两种方式：一是把所有东西一口气搬过去（可能搬好几个小时，期间没法生活）；二是每天搬一点，不影响日常生活。Map选择了第二种——扩容时旧数据慢慢迁移到新家，不会因为一次扩容就卡住。

---

## 24.5 sync.Map：并发安全的Map

普通的Map**不是并发安全的**。如果两个goroutine（Go的轻量级线程，详见第34章）同时读写一个Map，程序会报错甚至崩溃。

```go
m := make(map[int]int)

go func() {
    for i := 0; i < 1000; i++ {
        m[i] = i  // goroutine 1：写
    }
}()

go func() {
    for i := 0; i < 1000; i++ {
        _ = m[i]  // goroutine 2：读
    }
}()

// 运行一段时间会 panic: concurrent map read and map write
```

解决方案之一是用 `sync.RWMutex` 加锁（后面第36章会深入讲）。但Go标准库也提供了 `sync.Map`——一个开箱即用的并发安全Map：

```go
var sm sync.Map

sm.Store("张三", 90)
sm.Store("李四", 85)

value, ok := sm.Load("张三")
if ok {
    fmt.Println(value)  // 90
}

sm.Delete("李四")

sm.Range(func(key, value interface{}) bool {
    fmt.Printf("%v: %v\n", key, value)
    return true
})
```

`sync.Map` 的API和普通Map不太一样，用 `Store`/`Load`/`Delete`/`Range` 方法来操作。

不过 `sync.Map` 不是银弹——它在**写多读少**的场景下性能不如普通Map加锁。Go的官方建议是：大多数场景用普通Map加 `sync.RWMutex`，只有特定场景（如缓存中有大量只读操作）才用 `sync.Map`。

初学阶段，你不需要太操心并发安全——`sync.Map`更多是用来了解"有这个东西"。

---

## 本章小结

| 知识点 | 核心要点 |
|--------|----------|
| nil map | `var m map[K]V` 是nil，**不能赋值**，可以用make或字面量初始化 |
| 增删改查 | `m[k]=v`（增/改），`v, ok := m[k]`（查），`delete(m, k)`（删） |
| comma ok | `v, ok := m[k]` 判断key是否存在，不要只读v然后猜 |
| 遍历随机 | Go故意让遍历顺序随机，防止你依赖顺序 |
| 底层原理 | 哈希表，链地址法解决冲突，渐进式扩容 |
| sync.Map | 并发安全的Map，Store/Load/Delete/Range，但不是万能的 |

---

> 🚀 **下一章**：Map搞懂了，但前面有一章留了尾巴——字符串。字符串的底层长什么样？怎么高效拼接？strings包和strconv包里有哪些宝藏在等你？第25章，字符串深入篇。

---
[← 上一章：23-切片（Slice）](23-切片（Slice）.md) | [下一章：25-字符串深入 →](25-字符串深入.md)