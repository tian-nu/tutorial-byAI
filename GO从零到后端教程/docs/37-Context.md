# 第37章 · Context

> "你给一个外卖骑手发了一条消息：'送完这一单就下班吧'。骑手收到后，送完手上这单，就不再接新单了。你怎么让一个正在跑的Goroutine停下来？怎么设置'如果5秒内没完成就算了'？Context就是Go里传递这类'控制信号'的机制。"

---

## 37.1 为什么需要Context

### 场景一：取消

用户在浏览器里发起了一个请求，后端开始处理。处理过程中用户关掉了浏览器——这个请求的处理应该停止，不要浪费CPU和数据库连接。

### 场景二：超时

后端要调用一个第三方API。第三方有时候很慢，如果5秒还没返回，就应该放弃，不要无限期等待。

### 场景三：传递数据

一个HTTP请求进来，经过了认证中间件、日志中间件、业务处理器……每个环节都需要知道请求ID、用户ID等信息。怎么在整个调用链中传递这些数据？

**Context就是解决这三个问题的统一方案。**

---

## 37.2 Context的四个核心方法

```go
type Context interface {
    Deadline() (deadline time.Time, ok bool)
    Done() <-chan struct{}
    Err() error
    Value(key interface{}) interface{}
}
```

| 方法 | 作用 | 比喻 |
|------|------|------|
| `Deadline()` | 返回截止时间（如果有） | 快递单上写着"今日18:00前送达" |
| `Done()` | 返回一个Channel，Context取消时它会被关闭 | 收到"可以下班了"的通知 |
| `Err()` | 返回Context被取消的原因 | 查看为什么被取消了（超时？主动取消？） |
| `Value()` | 获取Context中存储的值 | 从档案袋里翻出一张纸条 |

---

## 37.3 创建Context

### context.Background()

```go
ctx := context.Background()
```

这是"根源"Context——通常用于 `main` 函数、测试和请求处理的入口。它是一个空的、永不取消的Context。所有其他Context都派生自它。

**比喻**：Background就像宇宙大爆炸的起点——一切派生的Context都从这里开始。

### context.TODO()

```go
ctx := context.TODO()
```

功能和 `Background()` 一样，但语义不同：**"这里应该传Context，但我还没想好传什么"**。它是一个占位符，提醒你将来要替换掉。

### WithCancel：手动取消

```go
ctx, cancel := context.WithCancel(context.Background())

go func() {
    select {
    case <-ctx.Done():
        fmt.Println("收到取消信号，收工")
        return

    }
}()

time.Sleep(1 * time.Second)
cancel()
time.Sleep(100 * time.Millisecond)
```

输出：`收到取消信号，收工`

`cancel()` 被调用后，`ctx.Done()` 返回的Channel被关闭，所有监听这个Channel的Goroutine都能感知到。

**记住**：`cancel` 函数必须被调用（即使没主动取消，也要 `defer cancel()`），否则Context永远不会被回收——造成内存泄漏。

### WithTimeout：超时自动取消

```go
ctx, cancel := context.WithTimeout(context.Background(), 2*time.Second)
defer cancel()

select {
case <-time.After(5 * time.Second):
    fmt.Println("任务完成")
case <-ctx.Done():
    fmt.Println("超时了:", ctx.Err())
}
```

输出：`超时了: context deadline exceeded`

`WithTimeout` 创建的Context会在指定的时间后自动取消。`ctx.Err()` 告诉你原因。

### WithDeadline：指定截止时间点

```go
deadline := time.Now().Add(5 * time.Second)
ctx, cancel := context.WithDeadline(context.Background(), deadline)
defer cancel()
```

和 `WithTimeout` 一样，只是指定的是**时间点**而不是**时长**。

### WithValue：传递数据

```go
type contextKey string

const (
    requestIDKey contextKey = "requestID"
    userIDKey    contextKey = "userID"
)

func process(ctx context.Context) {
    requestID := ctx.Value(requestIDKey).(string)
    fmt.Println("处理请求:", requestID)
}

func main() {
    ctx := context.Background()
    ctx = context.WithValue(ctx, requestIDKey, "req-12345")
    ctx = context.WithValue(ctx, userIDKey, 10086)

    process(ctx)
}
```

**比喻**：Context像一个"档案袋"，一路传递。每个中间环节可以往档案袋里塞东西（`WithValue`），后面的环节可以查阅（`Value`）。

---

## 37.4 使用模式

### 模式一：select + ctx.Done()

```go
func doWork(ctx context.Context) error {
    for {
        select {
        case <-ctx.Done():
            return ctx.Err()
        default:
            fmt.Println("工作中...")
            time.Sleep(500 * time.Millisecond)
        }
    }
}
```

Goroutine定期检查Context是否被取消——如果取消了就退出。

### 模式二：把Context传给下游

```go
func handleRequest(ctx context.Context) {
    userID := ctx.Value(userIDKey).(int)

    data, err := queryDatabase(ctx, userID)
    if err != nil {
        return
    }

    result, err := callExternalAPI(ctx, data)
    if err != nil {
        return
    }

    saveResult(ctx, result)
}
```

`queryDatabase` 和 `callExternalAPI` 拿到Context后：
- 如果Context超时了还没返回，它们应该放弃
- 如果Context被取消了（比如用户断开连接），它们应该停止

这就是Context的威力：**控制信号能穿透整个调用链。**

### 模式三：http.Server使用Context

```go
func handler(w http.ResponseWriter, r *http.Request) {  // net/http 详见第66章（Gin框架入门）
    ctx := r.Context()

    select {
    case <-time.After(3 * time.Second):
        w.Write([]byte("完成"))
    case <-ctx.Done():
        fmt.Println("客户端已断开:", ctx.Err())
    }
}
```

`r.Context()` 获取的是该HTTP请求的Context。如果客户端断开连接（关掉浏览器、网络中断），Context会被自动取消。

---

## 37.5 最佳实践

### 1. Context必须是函数的第一个参数

```go
func doSomething(ctx context.Context, arg string) error {
```

这是Go社区的约定。`ctx` 永远是第一个参数，通常命名为 `ctx`。

### 2. 不要把Context存在结构体里

```go
type Worker struct {
    ctx context.Context
}
```

Context应该通过参数传递，而不是作为结构体的字段。因为Context是"请求级别"的，不是"对象级别"的——同一个Worker可能处理多个不同Context的请求。

### 3. 不要传nil Context

```go
func doSomething(ctx context.Context) {
}
```

调用方不应该传 `nil`。如果你不确定传什么，用 `context.TODO()`。

### 4. WithValue只传请求级数据

```go
ctx = context.WithValue(ctx, "requestID", "123")
```

不要把业务配置、数据库连接、函数指针等放在Context里。Context只适合传递：
- 请求ID（用于日志追踪）
- 用户认证信息
- 请求开始时间
- 链路追踪信息

### 5. 不要用基础类型做Context的Key

```go
ctx = context.WithValue(ctx, "id", "123")
```

用字符串做key，不同的包可能冲突。应该定义自己的类型：

```go
type myKey string
ctx = context.WithValue(ctx, myKey("id"), "123")
```

不同包定义的类型天然不同——即使字面量一样，类型不同的key也不会冲突。

### 6. 始终调用cancel

```go
ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
defer cancel()
```

即使超时自动cancel了，`defer cancel()` 也不会造成问题（重复调用cancel是安全的）。关键是：**不要让cancel漏掉**，否则Context相关的资源永远不会被释放。

---

## 🤔 想多一点：为什么Context设计成这样？

Context不是Go一开始就有的——它是2014年才被引入标准库的（在 `golang.org/x/net/context`，后来移到标准库）。

设计者们看到了一个普遍问题：在并发程序（特别是HTTP服务器）中，你需要一种机制来：
1. 跨Goroutine传播取消信号
2. 跨Goroutine传播截止时间
3. 跨Goroutine传播请求级别的数据

他们经过多轮讨论，最终确定了这个简洁的接口——只有四个方法，却覆盖了几乎所有场景。

Context是Go并发的"最后一块拼图"。Goroutine让你能并发，Channel让你能通信，同步原语让你能保护共享数据，而Context让你能**控制**并发——什么时候开始，什么时候停止，什么时候放弃。

---

## 本章小结

| 知识点 | 要点 |
|--------|------|
| Context接口 | `Deadline()`/`Done()`/`Err()`/`Value()` |
| Background() | 根Context，永不取消，用于main/测试 |
| TODO() | 占位符，表示还没想好传什么 |
| WithCancel | 手动取消，必须调用cancel() |
| WithTimeout | 超时自动取消 |
| WithDeadline | 指定时间点自动取消 |
| WithValue | 传递请求级数据 |
| 最佳实践 | 第一个参数、不存结构体、不传nil、定义key类型 |

> 🚀 下一章：并发编程的四件套（Goroutine + Channel + 同步原语 + Context）全部学完。现在换个实用的方向：让你的Go程序读写文件——读取配置、写入日志、遍历目录，这些都是日常开发的必备技能。

---
[上一章：36-同步原语](36-同步原语.md) | [下一章：38-文件操作](38-文件操作.md)