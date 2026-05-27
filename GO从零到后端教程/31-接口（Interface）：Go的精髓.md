# 第31章 · 接口（Interface）：Go的精髓

> "你家墙上的插座不关心你插的是电视机还是电风扇——三孔、220V，符合标准就能通电。接口就是这个插座：它定义了一套'标准'，任何满足标准的'电器'都能接入。而Go最酷的地方在于：你不需要在电器上贴'我是符合标准的电器'的标签——只要插头能插进去，自然就是。"

---

## 31.1 接口是什么：插座比喻

### 现实中的接口

USB接口：不管你是U盘、键盘、鼠标、风扇——只要能插进USB口，电脑就能用。

电源插座：不管你是电视机、冰箱、微波炉——只要插头匹配，就能通电。

接口的核心思想是：**定义一套行为标准，不关心具体是谁来实现**。

### Go里的接口

```go
type Speaker interface {
    Speak() string
}
```

`Speaker` 接口定义了一个"能说话"的标准：你只要有一个 `Speak() string` 方法，你就是 `Speaker`。

```go
type Dog struct {
    Name string
}

func (d Dog) Speak() string {
    return "汪汪！我是" + d.Name
}

type Cat struct {
    Name string
}

func (c Cat) Speak() string {
    return "喵喵！我是" + c.Name
}
```

`Dog` 和 `Cat` 都有 `Speak() string` 方法，所以它们都"自动"实现了 `Speaker` 接口。

然后你可以写出与具体类型无关的代码：

```go
func greet(s Speaker) {
    fmt.Println(s.Speak())
}

greet(Dog{Name: "旺财"})
greet(Cat{Name: "咪咪"})
```

`greet` 函数接受的是 `Speaker` 接口——它不在乎传进来的是狗还是猫，只要会说话就行。

**这就是接口的威力：解耦。** `greet` 不需要知道狗和猫的存在，它只知道"会说话的东西"。将来你加了 `Parrot`、`Robot`、`Alien`——只要它们有 `Speak() string` 方法，就能直接传给 `greet`，一行代码都不用改。

---

## 31.2 隐式实现：不需要 `implements`！

这是Go接口最颠覆性的设计。

Java：
```java
class Dog implements Speaker {
    public String speak() { return "汪汪"; }
}
```

你必须显式声明 `implements Speaker`，告诉编译器"Dog实现了Speaker"。

Go：
```go
type Dog struct{}

func (d Dog) Speak() string {
    return "汪汪"
}
```

**没有任何 `implements` 关键字！** Dog有没有实现 `Speaker`，取决于Dog有没有 `Speak() string` 方法——如果你有，你自然就是；如果你没有，你就不是。

### 比喻：驾照

你不需要在身上贴一张"我有驾照"的标签。交警拦下你，不是看标签，而是直接问你："请出示驾照"。你掏出驾照——有了，你就可以开车；掏不出来——没有，那就不能开。

Go编译器就是这样：它看的是你**有没有对应的方法**，而不是你有没有声明。

### 隐式实现的好处

**1. 解耦到极致**

你的包定义了一个接口：
```go
package mylib

type Logger interface {
    Log(msg string)
}
```

别人的包定义了一个类型：
```go
package thirdparty

type MyLogger struct{}

func (l MyLogger) Log(msg string) { ... }
```

别人的包完全不知道你的 `mylib.Logger` 接口的存在。但因为 `MyLogger` 有 `Log(string)` 方法，它自动实现了 `mylib.Logger`。你可以直接把 `MyLogger` 传给你的函数——天衣无缝。

**2. 你可以为别人的类型"后补"实现接口**

标准库的 `fmt.Stringer` 接口：
```go
type Stringer interface {
    String() string
}
```

你可以给自己定义的类型实现 `String()` 方法，`fmt.Println` 就会自动使用你的 `String()` 输出——你不需要修改标准库的任何代码。

---

## 31.3 接口值：动态类型 + 动态值

接口类型的变量有两层：

```
var s Speaker = Dog{Name: "旺财"}
```

`s` 这个变量内部存储了两个东西：
- **动态类型**：`Dog`（实际存的是什么类型）
- **动态值**：`Dog{Name: "旺财"}`（实际存的值是什么）

你可以画成这样的图：

```
s (Speaker接口值)
├── 类型指针 → Dog
└── 值指针   → {Name: "旺财"}
```

### nil接口 vs nil值：一个巨坑

这是Go面试高频陷阱题：

```go
type MyError struct{}

func (e *MyError) Error() string {
    return "出错了"
}

func getError() error {
    var e *MyError
    return e
}

func main() {
    err := getError()
    if err != nil {
        fmt.Println("有错误:", err)
    } else {
        fmt.Println("没有错误")
    }
}
```

输出是 `有错误: <nil>`？还是 `没有错误`？

答案是：**`有错误: <nil>`**。

为什么？因为 `err` 不是 `nil`！

```
err (error接口值)
├── 类型指针 → *MyError   ← 不是nil！
└── 值指针   → nil        ← 值是nil，但类型不是nil
```

**一个接口值只有在"类型"和"值"都是nil时，才等于nil。**

`getError()` 返回的 `error` 接口里装了一个 `*MyError` 类型（不是nil），尽管值是nil。所以 `err != nil` 是 `true`。

正确的写法：

```go
func getError() error {
    return nil
}
```

直接返回 `nil`，这样接口值的类型和值都是 `nil`。

### 比喻：空信封

一个信封（接口值），信封上写着"寄件人：张三"，但里面是空的（nil值）。你问"这个信封是空的吗？"——不是。因为有寄件人信息。

---

## 31.4 类型断言：把接口值还原成具体类型

接口让你能处理"任何会说话的东西"，但有时候你确实需要知道"它到底是狗还是猫"。

```go
func inspect(speaker Speaker) {
    dog, ok := speaker.(Dog)
    if ok {
        fmt.Println("这是一只狗，名字叫", dog.Name)
        return
    }

    cat, ok := speaker.(Cat)
    if ok {
        fmt.Println("这是一只猫，名字叫", cat.Name)
        return
    }

    fmt.Println("不知道是什么，但它说:", speaker.Speak())
}
```

`s := x.(Type)` 的意思是："x 是 Type 类型吗？如果是，把它的具体值赋给 s，ok为true；如果不是，s是Type的零值，ok为false"。

如果不用 `ok` 而直接断言：

```go
dog := speaker.(Dog)
```

如果 `speaker` 不是 `Dog` 类型，程序直接 `panic`。所以推荐用 `ok` 模式。

### 比喻：安检

接口值就像过安检的人——你只知道"这是一个会说话的人"。类型断言就像安检员检查："你是狗吗？""你是猫吗？" ——如果刚好是，就能获取详细信息（狗的名字）；如果不是，就继续问下一个。

---

## 31.5 类型开关：分类处理

当你要判断的类型很多时，类型断言写一堆 `if` 很啰嗦。`type switch` 更优雅：

```go
func inspect(s Speaker) {
    switch v := s.(type) {
    case Dog:
        fmt.Println("狗:", v.Name)
    case Cat:
        fmt.Println("猫:", v.Name)
    case Parrot:
        fmt.Println("鹦鹉:", v.Color)
    default:
        fmt.Println("未知生物:", v.Speak())
    }
}
```

`x.(type)` 只能在 `switch` 语句中使用。每个 `case` 里，`v` 会自动被转换为该 `case` 对应的类型——不需要你再做类型断言。

> 📌 类型断言和类型开关让你在编译时处理已知类型，但有时你需要处理完全未知的类型——这时可以用反射（程序在运行时检查自身结构，详见附录I），通过 `reflect` 包动态获取类型信息。不过反射性能开销大且代码复杂，日常开发优先使用接口和类型断言。

---

## 31.6 接口组合：搭积木

你可以把多个小接口拼成一个大接口：

```go
type Reader interface {
    Read(p []byte) (n int, err error)
}

type Writer interface {
    Write(p []byte) (n int, err error)
}

type Closer interface {
    Close() error
}

type ReadWriter interface {
    Reader
    Writer
}

type ReadWriteCloser interface {
    Reader
    Writer
    Closer
}
```

`ReadWriter` 包含了 `Reader` 和 `Writer` 的所有方法。这意味着，实现 `ReadWriter` 的类型必须**同时有** `Read` 和 `Write` 方法。

### 比喻：套餐

`Reader` 是"识字套餐"，`Writer` 是"写字套餐"，`ReadWriter` 是"全能套餐"——你必须两个都会才行。而 `ReadWriteCloser` 是"全能+善后套餐"。

### 为什么这样设计

**接口隔离原则**：使用者只依赖自己需要的最小接口。

如果你写的函数只需要读数据：

```go
func process(r Reader) { ... }
```

而不是：

```go
func process(r ReadWriteCloser) { ... }
```

这样调用者只需要传一个实现了 `Reader` 的东西，不需要实现 `Write` 和 `Close`。接口越小，适用范围越广，耦合越低。

---

## 31.7 常用标准接口

Go标准库定义了很多小巧的接口，理解它们能帮你读懂大量标准库和第三方库的代码。

### io.Reader：一切读取的源头

```go
type Reader interface {
    Read(p []byte) (n int, err error)
}
```

任何可以"读"的东西都实现了 `io.Reader`：文件、网络连接、HTTP请求体、内存中的字节切片、压缩流、加密流……

一个简单的读取：

```go
file, _ := os.Open("data.txt")
buffer := make([]byte, 1024)
n, err := file.Read(buffer)
fmt.Println(string(buffer[:n]))
```

### io.Writer：一切写入的去处

```go
type Writer interface {
    Write(p []byte) (n int, err error)
}
```

任何可以"写"的东西：文件、网络连接、HTTP响应、标准输出、内存buffer……

```go
file, _ := os.Create("output.txt")
file.Write([]byte("Hello World"))
```

### fmt.Stringer：控制打印输出

```go
type Stringer interface {
    String() string
}
```

实现了 `String()` 方法的类型，在用 `fmt.Println` 打印时会自动调用 `String()`：

```go
type User struct {
    Name string
    Age  int
}

func (u User) String() string {
    return fmt.Sprintf("用户[%s, %d岁]", u.Name, u.Age)
}

u := User{Name: "张三", Age: 25}
fmt.Println(u)
```

输出：`用户[张三, 25岁]`

### error：最常用的接口

```go
type error interface {
    Error() string
}
```

只有一个方法 `Error() string`——这就是Go的错误机制的全部。任何有 `Error() string` 方法的类型都是一个error。这将在下一章详细展开。

### http.Handler：Web服务器的灵魂

```go
type Handler interface {
    ServeHTTP(ResponseWriter, *Request)
}
```

实现 `ServeHTTP` 方法就能处理HTTP请求。这就是为什么你能写出：

```go
http.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
    fmt.Fprintf(w, "Hello")
})
```

---

## 🤔 想多一点：为什么Go的接口设计这么特别？

Go的接口设计解决了面向对象编程的一个经典问题：**紧耦合**。

在Java/C++中，如果 `class A` 实现了 `interface I`，A就"依赖"了I（`class A implements I`）。如果你想在一个没有引入I的包里直接复用A，不行——你必须引入I的包，或者写适配器。

Go的隐式实现打破了这个依赖：A不需要知道I的存在。**接口由调用者定义，而不是由实现者声明。** 这完美体现了"依赖反转"原则。

在实际项目中，这意味着你可以：
1. 在自己的包里定义小而专的接口（只包含你需要的方法）
2. 任何第三方库的类型只要恰好有那些方法，就能无缝接入
3. 不需要写适配器、包装类、桥接模式……

少写很多胶水代码，这就是Go的工程哲学。

---

## 本章小结

| 知识点 | 要点 |
|--------|------|
| 接口定义 | `type 接口名 interface { 方法列表 }` |
| 隐式实现 | 有方法就行，不需要 `implements` |
| 接口值 | 两个字段：动态类型 + 动态值 |
| nil接口陷阱 | 类型非nil + 值nil → 接口非nil |
| 类型断言 | `x.(Type)`，推荐带 `ok` 的安全模式 |
| 类型开关 | `switch x.(type) { case ... }` |
| 接口组合 | 小接口拼成大接口，遵循接口隔离原则 |
| 常用标准接口 | `io.Reader`、`io.Writer`、`error`、`fmt.Stringer`、`http.Handler` |

> 🚀 下一章：第32章 · 错误处理——Go最"啰嗦"也最坦率的设计。`if err != nil` 写了无数遍，但Go的哲学是：错误不是异常，它是程序正常流程的一部分。学会用 `%w` 包装错误、用 `errors.Is` 和 `errors.As` 判断错误。

---
[← 上一章：30-方法](30-方法.md) | [下一章：32-错误处理 →](32-错误处理.md)