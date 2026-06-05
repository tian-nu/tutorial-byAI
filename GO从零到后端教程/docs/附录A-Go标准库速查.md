# 附录A · Go标准库速查

> "Go标准库就像一把瑞士军刀——几乎所有日常开发需要的工具都在里面。本附录按功能分类列出最常用的包和函数，作为你日常编码时的快速参考。"

---

## A.1 字符串处理 — `strings`

| 函数 | 作用 | 示例 |
|------|------|------|
| `Contains(s, substr)` | s是否包含substr | `strings.Contains("hello", "ll")` → true |
| `HasPrefix(s, prefix)` | s是否以prefix开头 | `strings.HasPrefix("file.go", "file")` → true |
| `HasSuffix(s, suffix)` | s是否以suffix结尾 | `strings.HasSuffix("file.go", ".go")` → true |
| `Index(s, substr)` | substr首次出现位置 | `strings.Index("hello", "l")` → 2 |
| `LastIndex(s, substr)` | substr最后出现位置 | `strings.LastIndex("hello", "l")` → 3 |
| `Join(elems, sep)` | 用分隔符连接 | `strings.Join([]string{"a","b"}, ",")` → "a,b" |
| `Split(s, sep)` | 按分隔符拆分 | `strings.Split("a,b,c", ",")` → ["a","b","c"] |
| `SplitN(s, sep, n)` | 拆成最多n份 | `strings.SplitN("a,b,c", ",", 2)` → ["a","b,c"] |
| `Replace(s, old, new, n)` | 替换n次（-1=全部） | `strings.Replace("foo", "o", "a", -1)` → "faa" |
| `ToLower(s)` | 转小写 | `strings.ToLower("HELLO")` → "hello" |
| `ToUpper(s)` | 转大写 | `strings.ToUpper("hello")` → "HELLO" |
| `Trim(s, cutset)` | 去除首尾字符 | `strings.Trim("!!!hello!!!", "!")` → "hello" |
| `TrimSpace(s)` | 去除首尾空格 | `strings.TrimSpace(" hi ")` → "hi" |
| `Fields(s)` | 按空格拆分成单词 | `strings.Fields("a b c")` → ["a","b","c"] |
| `Repeat(s, count)` | 重复字符串 | `strings.Repeat("Go", 3)` → "GoGoGo" |
| `Builder` | 高效拼接字符串 | 代替循环中的`+=`，性能提升百倍 |

### strings.Builder（必须会用）

```go
var b strings.Builder
b.WriteString("Hello ")
b.WriteString("World")
fmt.Println(b.String())
```

为什么不用 `s += "xxx"`？因为Go的字符串是不可变的——每次 `+=` 都创建新字符串然后复制，循环一万次就是灾难。`Builder` 内部用 `[]byte` 缓冲区，零额外分配。

### 字符串转数字 — `strconv`

| 函数 | 作用 |
|------|------|
| `Atoi(s)` | 字符串→int |
| `Itoa(i)` | int→字符串 |
| `ParseInt(s, base, bitSize)` | 字符串→int64（可指定进制） |
| `ParseFloat(s, bitSize)` | 字符串→float64 |
| `ParseBool(s)` | "true"/"false"→bool |
| `FormatInt(i, base)` | int64→字符串 |
| `FormatFloat(f, fmt, prec, bitSize)` | float→字符串 |

---

## A.2 输入输出 — `io` / `os` / `bufio` / `fmt`

### os包 — 操作系统交互

| 函数 | 作用 |
|------|------|
| `os.Open(path)` | 只读打开文件 |
| `os.Create(path)` | 创建/覆盖文件 |
| `os.OpenFile(path, flag, perm)` | 通用打开（指定读写模式） |
| `os.Remove(path)` | 删除文件 |
| `os.RemoveAll(path)` | 删除目录（含子内容） |
| `os.Mkdir(path, perm)` | 创建目录 |
| `os.MkdirAll(path, perm)` | 递归创建目录 |
| `os.ReadFile(path)` | 读整个文件到[]byte |
| `os.WriteFile(path, data, perm)` | 写[]byte到文件 |
| `os.Getenv(key)` | 读环境变量 |
| `os.Setenv(key, value)` | 写环境变量 |
| `os.Exit(code)` | 退出程序 |
| `os.Args` | 命令行参数 |
| `os.Stdin / Stdout / Stderr` | 标准输入/输出/错误 |

### io包 — 读写抽象

| 接口/函数 | 作用 |
|-----------|------|
| `io.Reader` | 万物皆可Read() |
| `io.Writer` | 万物皆可Write() |
| `io.Copy(dst, src)` | 从Reader拷贝到Writer |
| `io.ReadAll(r)` | 读取Reader全部内容 |
| `io.NopCloser(r)` | 把Reader包装成ReadCloser |
| `io.TeeReader(r, w)` | 读的同时写一份副本（用于日志） |
| `io.LimitReader(r, n)` | 限制最多读n字节 |
| `io.MultiReader` | 串联多个Reader |
| `io.MultiWriter` | 同时写入多个Writer |

### bufio — 缓冲读写

| 类型/函数 | 作用 |
|-----------|------|
| `bufio.NewReader(r)` | 创建缓冲Reader |
| `bufio.NewWriter(w)` | 创建缓冲Writer |
| `bufio.NewScanner(r)` | 逐行/逐词扫描 |
| `reader.ReadString('\n')` | 读一行 |
| `writer.Flush()` | 刷新缓冲区 |

### fmt — 格式化

| 函数 | 作用 |
|------|------|
| `fmt.Print(args...)` | 输出 |
| `fmt.Printf(format, args...)` | 格式化输出 |
| `fmt.Println(args...)` | 输出+换行 |
| `fmt.Sprintf(format, args...)` | 格式化为字符串 |
| `fmt.Errorf(format, args...)` | 格式化为error |
| `fmt.Scan` | 从标准输入读取 |

常用格式化动词：
- `%v`：默认格式
- `%+v`：结构体带字段名
- `%#v`：Go语法表示
- `%T`：类型
- `%d`：十进制整数
- `%s`：字符串
- `%q`：带引号的字符串
- `%f`：浮点数
- `%t`：布尔值
- `%p`：指针地址

---

## A.3 网络编程 — `net` / `net/http`

### net包

| 类型/函数 | 作用 |
|-----------|------|
| `net.Listen(network, address)` | 监听端口 |
| `net.Dial(network, address)` | 建立连接 |
| `net.ResolveTCPAddr` | 解析TCP地址 |
| `net.SplitHostPort` | 拆分 "host:port" |
| `net.JoinHostPort` | 拼接 "host:port" |
| `net.IPv4(a,b,c,d)` | 创建IPv4地址 |
| `net.InterfaceAddrs()` | 获取本机IP |

### net/http

| 类型/函数 | 作用 |
|-----------|------|
| `http.HandleFunc(pattern, handler)` | 注册路由 |
| `http.ListenAndServe(addr, handler)` | 启动HTTP服务 |
| `http.Get(url)` | GET请求 |
| `http.Post(url, contentType, body)` | POST请求 |
| `http.NewRequest(method, url, body)` | 构造请求 |
| `http.Client{}.Do(req)` | 发送请求 |
| `http.StatusOK` / `StatusNotFound`... | HTTP状态码常量 |
| `http.FileServer(dir)` | 静态文件服务 |
| `http.Redirect(w, r, url, code)` | 重定向 |
| `http.Error(w, msg, code)` | 错误响应 |
| `http.TimeoutHandler` | 超时包装 |

---

## A.4 加密与哈希 — `crypto`

| 包 | 作用 |
|----|------|
| `crypto/md5` | MD5哈希（仅用于非安全校验） |
| `crypto/sha256` | SHA256哈希 |
| `crypto/sha512` | SHA512哈希 |
| `crypto/hmac` | HMAC消息认证码 |
| `crypto/rand` | 加密安全随机数 |
| `crypto/aes` | AES对称加密 |
| `crypto/rsa` | RSA非对称加密 |
| `crypto/tls` | TLS/SSL配置 |
| `golang.org/x/crypto/bcrypt` | bcrypt密码哈希 |

---

## A.5 并发编程 — `sync` / `context`

### sync包

| 类型 | 作用 |
|------|------|
| `sync.Mutex` | 互斥锁 |
| `sync.RWMutex` | 读写锁（多读单写） |
| `sync.WaitGroup` | 等待一组goroutine完成 |
| `sync.Once` | 只执行一次 |
| `sync.Map` | 并发安全Map |
| `sync.Pool` | 临时对象池（减少GC） |
| `sync.Cond` | 条件变量 |

### context包

| 函数 | 作用 |
|------|------|
| `context.Background()` | 根context |
| `context.TODO()` | 占位context |
| `context.WithCancel(parent)` | 可取消的子context |
| `context.WithTimeout(parent, d)` | 带超时的子context |
| `context.WithDeadline(parent, t)` | 带截止时间的子context |
| `context.WithValue(parent, key, val)` | 带值的子context |

---

## A.6 时间与日期 — `time`

| 函数/类型 | 作用 |
|-----------|------|
| `time.Now()` | 当前时间 |
| `time.Date(year, month, day, ...)` | 构造指定时间 |
| `time.Parse(layout, value)` | 解析字符串为时间 |
| `time.Since(t)` | 从t到现在的间隔 |
| `time.Until(t)` | 从现在到t的间隔 |
| `t.Format(layout)` | 时间格式化为字符串 |
| `t.Add(d)` | 加一段时间 |
| `t.Sub(u)` | 时间差 |
| `t.Before(u)` / `t.After(u)` | 时间比较 |
| `t.Unix()` | Unix时间戳（秒） |
| `t.UnixMilli()` | Unix时间戳（毫秒） |
| `time.After(d)` | 返回一个channel，d时间后收到值 |
| `time.NewTicker(d)` | 定时器，周期性触发 |
| `time.NewTimer(d)` | 一次性定时器 |
| `time.Sleep(d)` | 休眠 |

Go时间格式化layout：`"2006-01-02 15:04:05"`——记住这个魔法数字：2006年1月2日下午3点4分5秒。（123456——Go的诞生参考时间）

---

## A.7 数学 — `math` / `math/rand`

| 函数 | 作用 |
|------|------|
| `math.Abs(x)` | 绝对值 |
| `math.Max(a, b)` / `math.Min(a, b)` | 最大/最小值 |
| `math.Ceil(x)` | 向上取整 |
| `math.Floor(x)` | 向下取整 |
| `math.Round(x)` | 四舍五入 |
| `math.Pow(x, y)` | x的y次方 |
| `math.Sqrt(x)` | 平方根 |
| `math.Mod(x, y)` | 取余 |
| `rand.Intn(n)` | [0, n) 的随机整数 |
| `rand.Float64()` | [0, 1) 的随机浮点数 |
| `rand.Shuffle(n, swap)` | 随机打乱切片 |
| `crypto/rand.Int(rand.Reader, max)` | 加密安全的随机数 |

---

## A.8 编码与序列化 — `encoding`

| 包 | 作用 |
|----|------|
| `encoding/json` | JSON编解码 |
| `encoding/xml` | XML编解码 |
| `encoding/base64` | Base64编解码 |
| `encoding/hex` | 十六进制编解码 |
| `encoding/csv` | CSV读写 |
| `encoding/binary` | 二进制数据编解码 |

### encoding/json 常用操作

```go
json.Marshal(v)          // Go对象→JSON
json.Unmarshal(data, &v) // JSON→Go对象
json.NewEncoder(w).Encode(v)
json.NewDecoder(r).Decode(&v)
json.Indent(...)         // 格式化输出
```

JSON标签常用选项：`json:"field_name,omitempty"`（值为空时不输出）、`json:"-"`（忽略字段）。

---

## A.9 其他常用包

| 包 | 作用 |
|----|------|
| `errors` | 错误处理：`errors.New()`、`errors.Is()`、`errors.As()`（Go 1.13+） |
| `log` | 标准日志库 |
| `log/slog` | Go 1.21+结构化日志 |
| `flag` | 命令行参数解析 |
| `path/filepath` | 文件路径操作（跨平台） |
| `path` | URL路径操作（用`/`分隔） |
| `regexp` | 正则表达式 |
| `sort` | 排序：`sort.Ints()`、`sort.Slice()` |
| `reflect` | 反射（运行时类型信息） |
| `runtime` | 运行时信息：`GOMAXPROCS`、`NumCPU`、`NumGoroutine` |
| `testing` | 单元测试 |
| `net/http/httptest` | HTTP测试工具 |
| `database/sql` | 通用SQL接口 |
| `html/template` | HTML模板（防XSS） |
| `text/template` | 文本模板 |

---

本节速查覆盖了Go日常开发中最常用的标准库函数。当你需要某个功能时，先来这边翻一下——很可能标准库已经有现成的实现，不需要引入第三方依赖。

---
[下一章：附录B-MySQL常用命令速查.md →](附录B-MySQL常用命令速查.md)
