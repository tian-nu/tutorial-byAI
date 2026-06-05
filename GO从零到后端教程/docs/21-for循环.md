# 第21章 · for循环

> "如果要处理100条数据，你不可能写100遍同样的代码。循环就是'把同一段逻辑重复执行N次'的机制。别的语言有for、while、do-while...Go只有for。但就这一个，够用了。"

---

## 21.1 Go只有for一种循环

Python有 `for` 和 `while`，C/Java有 `for`、`while`、`do-while`。Go把这些全砍了，只留了 `for`。

这又是一个"少即是多"的设计——一个for关键字能覆盖所有循环场景。你是新手的话，也不用纠结"什么时候用for什么时候用while"。

---

## 21.2 标准for：最熟悉的样子

```go
for i := 0; i < 10; i++ {
    fmt.Println(i)
}
```

标准for有三个部分，用分号分隔：

```
for 初始化语句; 条件表达式; 后置语句 {
    循环体
}
```

执行顺序：
1. **初始化语句**：在循环开始前执行一次（`i := 0`）
2. **条件表达式**：每次循环前判断，为true就执行循环体，为false就跳出（`i < 10`）
3. **循环体**：花括号里的代码
4. **后置语句**：每次循环体执行完后执行（`i++`）
5. 回到第2步

把上面的循环展开，等价于：

```
i=0 → 判断0<10=true → 打印0 → i++变成1
i=1 → 判断1<10=true → 打印1 → i++变成2
...
i=9 → 判断9<10=true → 打印9 → i++变成10
i=10 → 判断10<10=false → 退出循环
```

### 三个部分都可以省略

**省略初始化语句：**

```go
i := 0
for ; i < 10; i++ {
    fmt.Println(i)
}
```

如果变量已经在外面初始化了，可以省略初始化部分。

**省略后置语句：**

```go
for i := 0; i < 10; {
    fmt.Println(i)
    i++
}
```

后置操作放到循环体里面手动写。但这其实就变成了while风格（见下一节）。

**全部省略——死循环！**

```go
for {
    fmt.Println("我停不下来了")
}
```

---

## 21.3 while风格for：只有条件

Python的 `while True:`，C/Java的 `while (condition)`，在Go里就是 `for condition`：

```go
i := 0
for i < 10 {
    fmt.Println(i)
    i++
}
```

把for的三个部分拆出来，只留条件表达式。这就是Go的"while循环"。

再比如从数据库里逐条读取数据：

```go
// 从数据库逐条读取——这里只是演示for语法，数据库操作详见第50章
for rows.Next() {
    var user User
    rows.Scan(&user.ID, &user.Name)
    users = append(users, user)
}
```

为什么Go不叫while而用for？因为for已经能表达所有循环语义，没必要多一个关键字。记住：**25个关键字**。

---

## 21.4 死循环：for {}

这是Go里最简单的死循环：

```go
for {
    fmt.Println("一直执行")
}
```

等价于其他语言的 `while True` 或 `while(1)`。

死循环必须有 `break` 或 `return` 来跳出，否则程序永远不会结束：

```go
for {
    data, err := readNextChunk()
    if err != nil {
        break
    }
    process(data)
}
```

服务器程序的主循环——接受请求、处理、再接受请求——本质上就是死循环。

---

## 21.5 range遍历：最常用的循环形式

当你要遍历一个**集合**（数组、切片、map、字符串、channel）时，`range` 是最好用的工具。

### 遍历切片/数组

```go
numbers := []int{10, 20, 30, 40, 50}

for i, v := range numbers {
    fmt.Printf("索引: %d, 值: %d\n", i, v)
}
```

输出：
```
索引: 0, 值: 10
索引: 1, 值: 20
索引: 2, 值: 30
索引: 3, 值: 40
索引: 4, 值: 50
```

`range` 返回两个值：**索引** 和 **值**。

如果只需要索引（不需要值），可以省略第二个：

```go
for i := range numbers {
    fmt.Println(i)
}
```

如果只需要值（不需要索引），用 `_` 忽略索引：

```go
for _, v := range numbers {
    fmt.Println(v)
}
```

### 遍历map

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

注意：map的遍历顺序是**随机的**！每次运行结果可能不同。Go故意这样设计，防止你依赖遍历顺序。

### 遍历字符串

```go
s := "Hello你好"

for i, r := range s {
    fmt.Printf("字节位置: %d, 字符: %c\n", i, r)
}
```

输出：
```
字节位置: 0, 字符: H
字节位置: 1, 字符: e
字节位置: 2, 字符: l
字节位置: 3, 字符: l
字节位置: 4, 字符: o
字节位置: 5, 字符: 你
字节位置: 8, 字符: 好
```

注意：`i` 是**字节位置**，不是字符位置！"你"在字节位置5（因为"H"=1字节，"e"=1，"l"=1，"l"=1，"o"=1，共5字节），"好"在字节位置8（"你"占3字节：5+3=8）。而 `r` 是完整的字符（rune）。

### range返回的是副本（重要！）

`range` 遍历时，返回的值是**元素的副本**，不是元素本身。这意味着你修改 `v` 不会影响原集合：

```go
numbers := []int{10, 20, 30}

for _, v := range numbers {
    v = v * 2  // 修改的是副本，不影响原切片
}
fmt.Println(numbers)  // [10 20 30] — 没变！

for i := range numbers {
    numbers[i] = numbers[i] * 2  // 通过索引修改原切片
}
fmt.Println(numbers)  // [20 40 60] — 变了！
```

> 🤔 **想多一点**：range返回副本这个行为，对 `int`、`string` 这种简单类型没啥影响（反正你也改不了原值），但对于结构体这种复杂类型就有影响——`v.Field = xxx` 改的是副本。不过对切片和map的元素，`v`是值副本但如果你拿的是指针就没这个问题。这个细节在面试中常被问到。

---

## 21.6 break和continue：控制循环流程

### break：立即退出循环

```go
for i := 0; i < 10; i++ {
    if i == 5 {
        break  // 循环到此为止，后面的5,6,7,8,9都不会执行
    }
    fmt.Println(i)
}
```

输出：`0 1 2 3 4`

`break` 只在**最内层**的循环生效。如果有嵌套循环，内层的break只退出内层循环。

### continue：跳过本次循环，继续下一次

```go
for i := 0; i < 10; i++ {
    if i%2 == 0 {
        continue  // 跳过偶数，不打印
    }
    fmt.Println(i)
}
```

输出：`1 3 5 7 9`

`continue` 跳过本次循环的剩余代码，直接进入下一次循环的条件判断。

### break label：跳出多层循环

当你有嵌套循环，想在**内层直接跳出外层循环**时，用标签（label）：

```go
outer:
for i := 0; i < 3; i++ {
    for j := 0; j < 3; j++ {
        if i == 1 && j == 1 {
            break outer  // 跳出outer标签标记的外层循环
        }
        fmt.Printf("(%d, %d) ", i, j)
    }
}
```

输出：`(0, 0) (0, 1) (0, 2) (1, 0) `

当 `i=1, j=1` 时，`break outer` 直接跳出了**最外层的for循环**，整个循环结束。

同理，`continue label` 也能用：

```go
outer:
for i := 0; i < 3; i++ {
    for j := 0; j < 3; j++ {
        if j == 1 {
            continue outer  // 跳到外层循环的下一次迭代
        }
        fmt.Printf("(%d, %d) ", i, j)
    }
}
```

输出：`(0, 0) (1, 0) (2, 0) `

每次 `j==1` 时，`continue outer` 跳过内层剩余的所有迭代和外层当前迭代的剩余部分，直接进入外层的下一个 `i`。

> 🤔 **想多一点**：`break label` 和 `goto` 有点像，但比 `goto` 更受控制——你只能跳到包裹当前代码的某个循环的标签上，不能随便跳。Go实际上也有 `goto` 关键字，但在Go社区里极其少见，绝大多数场景用 `break label` 就够了。

---

## 本章小结

| 知识点 | 核心要点 |
|--------|----------|
| 标准for | `for i:=0; i<10; i++` — 三个部分都可以省略 |
| while风格for | `for i < 10` — 只留条件，Go的"while" |
| 死循环 | `for {}` — 用break/return退出 |
| range遍历 | `for i, v := range collection` — 返回索引+值 |
| range返回副本 | 修改 `v` 不影响原集合，要修改用 `索引` |
| break | 立即退出循环（最内层） |
| continue | 跳过本次，进入下一次 |
| break label | `break outer` 跳出指定标签的循环 |

---

> 🚀 **下一章**：循环有了，但怎么存一批数据？数组是Go里最基础的数据容器。但Go的数组有一个大坑——它是值类型！这和其他语言完全不一样。第22章见。

---
[← 上一章：20-if 和 switch](20-if%20和%20switch.md) | [下一章：22-数组 →](22-数组.md)