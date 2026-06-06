# 第35章 · Channel

> "两个人在厨房里合作做饭，一个人切菜，一个人炒菜。切菜的人切好一盘就递过去，炒菜的人接过来倒进锅里——这个传递菜盘的窗口就是Channel。在Go里，Goroutine之间不直接碰对方的数据，而是通过Channel传递消息。"

---

## 35.1 Channel是什么

### Go的并发哲学

大多数语言（Java、C++）的并发模型是：**共享内存 + 锁**。多个线程访问同一块数据，用锁来保护，避免数据竞争。

Go的哲学不同：**"不要通过共享内存来通信，而要通过通信来共享内存。"**

什么意思？

- 传统方式：多个线程共享一个变量，谁要用就先加锁，用完解锁
- Go的方式：Goroutine之间不共享变量，而是通过Channel传递数据的**副本**。收到数据的那一方拥有"所有权"，不需要锁

### 比喻：流水线

工厂里的流水线：工人A负责组装零件，工人B负责质检。A装好一个，放到传送带上；B从传送带上取下来检查。

- **传送带 = Channel**：连接两个工序
- **零件 = 数据**：通过Channel传递
- **A和B不需要共享工作台**：各自有自己的工作台，互不干扰

---

## 35.2 创建Channel

Channel是类型化的管道——只能传输一种类型的数据：

```go
ch := make(chan int)
```

`chan int` 的意思是"传输int的管道"。

```go
ch1 := make(chan string)
ch2 := make(chan bool)
ch3 := make(chan User)
```

### 无缓冲 vs 有缓冲

```go
ch := make(chan int)
```

无缓冲Channel——没有"暂存区"。

```go
ch := make(chan int, 10)
```

有缓冲Channel——有10个位置的"暂存区"。

---

## 35.3 发送和接收

```go
ch := make(chan string)

go func() {
    ch <- "你好"
}()

msg := <-ch
fmt.Println(msg)
```

| 操作 | 语法 | 说明 |
|------|------|------|
| 发送 | `ch <- value` | 把value放进管道 |
| 接收 | `value := <-ch` | 从管道取出数据 |

`<-` 箭头的方向就是数据流动的方向——往管道里丢（`ch <-`）或从管道里拿（`<-ch`）。

---

## 35.4 无缓冲 vs 有缓冲

### 无缓冲Channel：面对面交接

```go
ch := make(chan int)

go func() {
    fmt.Println("准备发送...")
    ch <- 42
    fmt.Println("发送完成！")
}()

time.Sleep(1 * time.Second)  // 需 import "time"（标准库详见第33章）
fmt.Println("准备接收...")
value := <-ch
fmt.Println("收到:", value)
```

输出：
```
准备发送...
准备接收...
收到: 42
发送完成！
```

注意顺序：**发送方在 "ch <- 42" 这一行被阻塞了**，直到接收方准备好接收。接收方开始接收后，发送才完成。这就是"面对面交接"——你必须站在窗口等，直到对方过来拿。

**比喻**：你把一份文件交给同事，你站在他工位旁边等他伸手接。他没接之前，你不能走。他一接，交接完成。

### 有缓冲Channel：快递柜

```go
ch := make(chan int, 3)

ch <- 1
ch <- 2
ch <- 3
```

前三发送不会阻塞——"快递柜"有3个空位。放完3个之后：

```go
ch <- 4
```

第四个发送会**阻塞**，直到有人取走至少一个包裹。

```go
value := <-ch
```

取走第一个（1），腾出一个位置，第四个发送可以放进去（4）。

**比喻**：快递柜有3个格子。你放了3个快递（不阻塞）。放第4个时柜子满了，你得等别人取走一个才能放。别人取件（接收）时如果柜子是空的，也得等有人放进去。

### 对比

| 特性 | 无缓冲 | 有缓冲 |
|------|--------|--------|
| 容量 | 0 | N（创建时指定） |
| 发送阻塞条件 | 没有接收者等着 | 缓冲区满了 |
| 接收阻塞条件 | 没有发送者等着 | 缓冲区空了 |
| 同步效果 | 收发必须同时就绪，强同步 | 收发可以异步到缓冲区容量内 |
| 比喻 | 面对面交接 | 快递柜 |

---

## 35.5 关闭Channel

Channel可以关闭，关闭后不能再发送，但可以继续接收剩余数据：

```go
ch := make(chan int, 3)
ch <- 1
ch <- 2
ch <- 3
close(ch)

v, ok := <-ch
fmt.Println(v, ok)

v, ok = <-ch
fmt.Println(v, ok)

v, ok = <-ch
fmt.Println(v, ok)

v, ok = <-ch
fmt.Println(v, ok)
```

输出：
```
1 true
2 true
3 true
0 false
```

关闭后，接收方可以判断Channel是否已关闭（`ok` 变为 `false`）。

### 关闭的规则

1. **发送方负责关闭**——接收方不应该关闭Channel
2. **重复关闭会panic**
3. **向已关闭的Channel发送会panic**
4. **关闭nil Channel会panic**

```go
ch := make(chan int)
close(ch)
close(ch)
```

### 用range遍历Channel

```go
ch := make(chan int)

go func() {
    for i := 1; i <= 5; i++ {
        ch <- i
    }
    close(ch)
}()

for v := range ch {
    fmt.Println(v)
}
```

`for v := range ch` 会一直读取，直到Channel被关闭且没有剩余数据。**如果不关闭Channel，range会永远阻塞。** 所以，用range时必须由发送方 `close`。

---

## 35.6 select：多路复用

Channel的世界里，"等"是个常见操作。但如果你要同时等多个Channel呢？谁先来就处理谁——用 `select`。

### 基础用法

```go
ch1 := make(chan string)
ch2 := make(chan string)

go func() {
    time.Sleep(1 * time.Second)
    ch1 <- "来自ch1"
}()

go func() {
    time.Sleep(2 * time.Second)
    ch2 <- "来自ch2"
}()

for i := 0; i < 2; i++ {
    select {
    case msg := <-ch1:
        fmt.Println("收到:", msg)
    case msg := <-ch2:
        fmt.Println("收到:", msg)
    }
}
```

`select` 会阻塞，直到**任意一个** `case` 可以执行。如果多个 `case` 同时就绪，**随机选一个**执行。

### 比喻：服务台

你去银行办业务，有三个窗口。你站在大厅中央，哪个窗口先空出来就去哪个。select就是这个"等窗口"的操作。

### default：非阻塞

```go
select {
case msg := <-ch:
    fmt.Println("收到:", msg)
default:
    fmt.Println("没有消息，不等了")
}
```

加了 `default`，如果所有 `case` 都阻塞，立刻执行 `default`——不会等待。这叫"非阻塞select"。

### time.After：超时控制

```go
select {
case msg := <-ch:
    fmt.Println("收到:", msg)
case <-time.After(3 * time.Second):
    fmt.Println("等了3秒，不等了，超时！")
}
```

`time.After(3 * time.Second)` 返回一个Channel，3秒后会收到一个值。如果3秒内 `ch` 没消息，就走超时case。

这是请求超时的标准写法。

### 用select + Channel做心跳

```go
ticker := time.NewTicker(1 * time.Second)
defer ticker.Stop()

for {
    select {
    case <-ticker.C:
        fmt.Println("我还活着")

    }
}
```

---

## 🤔 想多一点：Channel vs 共享内存

为什么Go推崇Channel？

共享内存 + 锁的问题：
1. **锁的正确顺序很难**——A锁→B锁→C锁，稍有不慎就死锁
2. **性能瓶颈**——锁把并行变成了串行
3. **可读性差**——你看到一段代码访问某个变量，你无法确定有没有其他线程在同时访问它

Channel的优势：
1. **所有权清晰**——数据通过Channel传递后，接收方"拥有"它，不需要锁
2. **死锁风险更低**——不涉及多把锁的问题
3. **可读性高**——数据流向清晰可见（沿着Channel走）

但Channel不是银弹。一些场景（比如简单的计数器）用 `sync.Mutex` 或 `atomic` 更简洁高效。Go提供了全套工具，选择最合适的即可。

---

## 本章小结

| 知识点 | 要点 |
|--------|------|
| 创建 | `make(chan T)` 无缓冲，`make(chan T, n)` 有缓冲 |
| 发送 | `ch <- val`，无缓冲时等接收者，有缓冲满时阻塞 |
| 接收 | `val := <-ch`，无缓冲时等发送者，有缓冲空时阻塞 |
| 关闭 | `close(ch)`，发送方关闭，关闭后只接收不发送 |
| range遍历 | `for v := range ch`，需close退出 |
| select | 多路复用，等任意case就绪，random选择 |
| default | 非阻塞select |
| time.After | select中的超时控制 |

> 🚀 下一章：Channel是Go并发的通信利器，但不是唯一的武器。有时候一个简单的共享计数器，用Channel反而杀鸡用牛刀——这时Mutex、WaitGroup、Once这些同步原语才是正确的选择。下一章，Go的同步工具箱。

---
[上一章：34-Goroutine](34-Goroutine/) | [下一章：36-同步原语](36-同步原语/)