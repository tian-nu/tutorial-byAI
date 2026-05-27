# 第34章 · Goroutine

> "你在烧水的同时可以刷牙、可以看手机——这三件事在同时进行。计算机里，一个程序同时做多件事，这就是并发。Go的Goroutine让并发变得像呼吸一样自然：写一个 `go` 关键字就够了。"

---

## 34.1 并发 vs 并行复习

操作系统中我们讲过进程和线程的区别，这里快速回顾：

### 比喻：一个人做三件事

**并发（Concurrency，多个任务交替执行，看起来同时进行，详见附录I）**：你在一个小时内交替做三件事——烧水（等水开的时候刷牙）、刷牙（刷的时候看手机新闻）、看手机。看起来三件事"同时"在做，但其实你的注意力在快速切换。

**并行（Parallelism，多个任务真正在同一时刻同时执行，详见附录I）**：你们三个人一起做事——你烧水、你室友刷牙、你朋友看手机。三件事真正在同一时刻发生。

简单记：**并发是"看起来同时"，并行是"真的同时"。**

Go的Goroutine是**并发**的——多个Goroutine可以轮流在一个CPU核心上运行。如果有多核CPU，多个Goroutine也可以并行运行。但你不能也不应该假设它们在并行——只需要把它们当作"独立地轮流执行"即可。

---

## 34.2 Goroutine：轻量级线程

### 操作系统的线程有多重？

操作系统线程是"重量级"的：
- 创建时需要分配约1MB的栈空间
- 线程切换需要进入内核态，保存/恢复大量寄存器
- 一台普通服务器通常只能跑几千个线程

### Goroutine是轻量级的

```go
go doSomething()
```

就一个 `go` 关键字——后面的函数调用就变成了一个Goroutine。Goroutine的初始栈大小只有**2KB**（Go 1.4起，早期是4KB），而且能按需伸缩。

一台普通服务器上，你可以轻松启动**十万个**甚至更多Goroutine——这在传统线程模型里是不可想象的。

### 第一个Goroutine示例

```go
func printNumbers() {
    for i := 1; i <= 5; i++ {
        fmt.Println(i)
        time.Sleep(100 * time.Millisecond)
    }
}

func printLetters() {
    for _, c := range "ABCDE" {
        fmt.Printf("%c\n", c)
        time.Sleep(150 * time.Millisecond)
    }
}

func main() {
    go printNumbers()
    go printLetters()

    time.Sleep(2 * time.Second)
    fmt.Println("主Goroutine结束")
}
```

可能的输出：
```
1
A
2
B
3
C
4
D
5
E
主Goroutine结束
```

`printNumbers` 和 `printLetters` 交替执行——两个Goroutine在"轮流"运行。

### 关键点：主Goroutine结束 = 程序结束

```go
func main() {
    go func() {
        time.Sleep(1 * time.Second)
        fmt.Println("这条信息你可能永远看不到")
    }()
}
```

程序直接退出了，子Goroutine还没跑完就被"杀"了。`main` 函数所在的Goroutine（主Goroutine）结束了，整个程序就结束了——不管还有其他多少Goroutine在跑。

**比喻**：主Goroutine是"总开关"。总开关拉了，整栋楼都断电，不管哪层还有人在工作。

所以上面的例子里我用 `time.Sleep(2 * time.Second)` 等着子Goroutine跑完——这不是好做法（后面会用 `sync.WaitGroup` 或 `channel` 来优雅地等待）。

### 匿名函数的Goroutine

```go
go func() {
    fmt.Println("我是一个匿名Goroutine")
}()
```

---

## 34.3 GMP调度模型

Goroutine为什么这么高效？这要讲到Go运行时的**GMP调度模型**。

### G、M、P分别是什么

| 缩写 | 全称 | 角色 | 比喻 |
|------|------|------|------|
| **G** | Goroutine | 要执行的任务 | 快递包裹 |
| **M** | Machine（OS线程） | 真正干活的工人 | 快递员 |
| **P** | Processor（逻辑处理器） | 持有运行队列的调度器 | 快递站点 |

### 工作流程

```
┌─────────────────────────────────┐
│  P（快递站点）                    │
│  ┌──────┬──────┬──────┬──────┐  │
│  │  G1  │  G2  │  G3  │  G4  │  │  ← 本地运行队列
│  └──────┴──────┴──────┴──────┘  │
│                                 │
│  M（快递员）正在送 G1             │
│  送完 G1 之后，从队列取下一个 G2  │
└─────────────────────────────────┘
```

- 每个 **P** 对应一个本地Goroutine队列
- 每个 **M** 必须绑定一个 **P** 才能执行Goroutine
- P的数量由 `GOMAXPROCS` 决定，默认等于CPU核心数
- 当一个M阻塞（比如系统调用），P会"解绑"这个M，绑定另一个可用的M继续干活
- 当一个P的本地队列空了，它会从全局队列或"偷"其他P队列里的Goroutine

### 比喻：快递站

- 快递包裹（G）源源不断地到达快递站（P）
- 每个快递站有几名快递员（M），快递员从站点取包裹去送
- 包裹太多？快递站之间会互相"借"包裹——你的站点空了，隔壁站点堆成山，你就去偷几个来送。这叫 **work stealing**。
- 快递员路上堵车了（系统调用阻塞）？别担心，站点会把这名快递员的包裹转给闲着的快递员

这就是GMP模型的核心思想：**用少量的线程（M）驱动大量的协程（G），通过高效的调度避免阻塞和饥饿。**

### GOMAXPROCS

```go
import "runtime"

func main() {
    fmt.Println("CPU核心数:", runtime.NumCPU())
    fmt.Println("当前GOMAXPROCS:", runtime.GOMAXPROCS(0))
}
```

`GOMAXPROCS` 是P的数量，默认等于CPU核心数。你一般不需要改它，除非在做性能调优。

---

## 🤔 想多一点：Goroutine vs 线程 vs 协程

| 特性 | OS线程 | Goroutine |
|------|--------|-----------|
| 栈大小 | 固定约1MB | 初始2KB，可伸缩 |
| 创建开销 | 大（系统调用） | 极小（用户态） |
| 切换开销 | 内核态切换 | 用户态切换 |
| 可创建数量 | 几千 | 数十万 |
| 调度器 | OS内核 | Go运行时 |
| 通信方式 | 共享内存+锁 | Channel/CSP模型 |

Goroutine不是操作系统线程——它是运行在Go运行时里的用户态"协程"。这也是为什么创建和切换Goroutine如此便宜：因为不需要陷入内核。

---

## 本章小结

| 知识点 | 要点 |
|--------|------|
| 并发vs并行 | 并发=交替执行，并行=同时执行 |
| Goroutine | `go func()` 启动，初始2KB栈，可跑十万+ |
| 主Goroutine | main结束→程序结束，子Goroutine随之终止 |
| GMP模型 | G=任务，M=线程，P=调度器 |
| work stealing | P之间互相"偷"Goroutine平衡负载 |
| GOMAXPROCS | P的数量，默认=CPU核心数 |

> 🚀 下一章：第35章 · Channel——Go并发的另一半。Goroutine是"谁来做"，Channel是"怎么做"和"怎么沟通"。Go的格言是："不要通过共享内存来通信，而要通过通信来共享内存。"

---
[← 上一章：33-包与模块](33-包与模块.md) | [下一章：35-Channel →](35-Channel.md)