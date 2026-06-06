# 附录G · 常见错误排查指南

> "Bug是程序员永恒的敌人。但80%的Bug都能归类到有限的几种模式中。本附录整理了后端开发中最常见的错误类型——Go panic、MySQL连接问题、Redis连接问题、网络问题、内存问题和性能问题——每种都给出症状→排查→解决的完整方案。"

---

## G.1 Go Panic常见原因

### G.1.1 空指针引用（nil pointer dereference）

**症状：**
```
panic: runtime error: invalid memory address or nil pointer dereference
```

**排查：**
找到panic所在行，检查该行所有`.`操作符前面的变量。最容易出错的是：
- 函数返回了nil，调用方没检查
- map/slice/channel没有初始化
- 接口变量底层是nil

```go
var m map[string]string
m["key"] = "value"

var s []int
s[0] = 1

type User struct { Name string }
var u *User
fmt.Println(u.Name)
```

**解决：**
- 初始化：`m := make(map[string]string)`、`s := make([]int, 0)`
- nil检查：`if u != nil { fmt.Println(u.Name) }`
- 函数返回错误时检查：`if err != nil { return err }`

### G.1.2 切片越界（index out of range）

**症状：**
```
panic: runtime error: index out of range [5] with length 3
```

**排查：**
检查切片长度和要访问的索引。常见场景：
- 循环条件写错了：`for i := 0; i <= len(s); i++`
- 没检查空切片直接访问s[0]
- 切分时范围错误：`s[10:20]`

**解决：**
- 访问前检查长度：`if len(s) > 0 { s[0] }`
- 循环用`for i, v := range s`
- 切分时用安全的辅助函数

### G.1.3 向已关闭的Channel发送

**症状：**
```
panic: send on closed channel
```

**排查：**
找到close(ch)的位置和ch <- val的位置。确保close只在发送方调用，且close后不再发送。

**解决：**
- 使用sync.WaitGroup确保close在所有发送完成后
- 使用select+ok模式安全发送：
```go
select {
case ch <- val:
default:
}
```
- 只让一个固定的goroutine负责close

### G.1.4 并发写map

**症状：**
```
fatal error: concurrent map writes
```

**排查：**
找到所有对同一个map进行写操作的goroutine。

**解决：**
- 用`sync.RWMutex`保护map
- 用`sync.Map`代替普通map
- 重构为每个goroutine写自己的局部数据

---

## G.2 MySQL连接问题

### G.2.1 连接被拒绝（Connection Refused）

**症状：**
```
Error 2003: Can't connect to MySQL server on '127.0.0.1:3306' (10061)
dial tcp 127.0.0.1:3306: connect: connection refused
```

**排查：**
1. MySQL服务是否启动：`systemctl status mysql`
2. 端口是否正确：`netstat -an | grep 3306`（或 `ss -tlnp | grep 3306`）
3. 防火墙是否拦截：`telnet 127.0.0.1 3306`（或 `nc -zv 127.0.0.1 3306`）
4. 是否绑定了正确地址：`SHOW VARIABLES LIKE 'bind_address'`

**解决：**
- 启动MySQL：`sudo systemctl start mysql`
- 修改bind-address为0.0.0.0允许远程连接（注意安全）
- 开放防火墙端口

### G.2.2 连接过多（Too many connections）

**症状：**
```
Error 1040: Too many connections
```

**排查：**
```sql
SHOW VARIABLES LIKE 'max_connections';
SHOW STATUS LIKE 'Threads_connected';
SHOW PROCESSLIST;
```

**解决：**
- 临时提高上限：`SET GLOBAL max_connections = 500;`
- 检查代码是否有连接泄漏——确保每次查询后关闭连接
- Go中配置连接池参数：
```go
sqlDB, _ := db.DB()
sqlDB.SetMaxOpenConns(25)
sqlDB.SetMaxIdleConns(10)
sqlDB.SetConnMaxLifetime(5 * time.Minute)
```

### G.2.3 连接超时（MySQL server has gone away）

**症状：**
```
Error 2006: MySQL server has gone away
```

**原因：**
- 连接空闲太久被MySQL断开（默认8小时）
- 查询数据包太大超出`max_allowed_packet`
- 服务器重启

**解决：**
- Go中设置`SetConnMaxLifetime`短于MySQL的`wait_timeout`
- 增大`max_allowed_packet`：`SET GLOBAL max_allowed_packet = 64M`
- 实现连接健康检查（ping后再用）

### G.2.4 慢查询

**症状：**
某个SQL执行时间超过1秒，导致接口超时。

**排查：**
```sql
SHOW VARIABLES LIKE 'slow_query%';
SET GLOBAL slow_query_log = 1;
SET GLOBAL long_query_time = 0.1;
```

然后用`EXPLAIN`分析查询计划：
```sql
EXPLAIN SELECT * FROM orders WHERE user_id = 1 ORDER BY created_at DESC;
```

**常见问题和解决：**
- 缺少索引：添加合适的索引
- 索引失效：避免`WHERE func(column) = value`
- SELECT *：只查需要的字段
- 大OFFSET：用游标分页代替

---

## G.3 Redis连接问题

### G.3.1 无法连接

**症状：**
```
dial tcp 127.0.0.1:6379: connect: connection refused
```

**排查：**
1. Redis是否启动：`redis-cli ping`（期待返回PONG）
2. 是否绑定127.0.0.1：`redis-cli -h 0.0.0.0 ping`
3. 端口是否被占用

**解决：**
- 启动Redis：`redis-server`
- 修改配置允许外部连接：`bind 0.0.0.0`

### G.3.2 内存不足

**症状：**
```
OOM command not allowed when used memory > 'maxmemory'
```

**查询：**
```bash
redis-cli INFO memory
redis-cli CONFIG GET maxmemory
```

**解决：**
- 增大maxmemory：`CONFIG SET maxmemory 2gb`
- 设置淘汰策略：`CONFIG SET maxmemory-policy allkeys-lru`
- 给缓存键设置过期时间

### G.3.3 响应慢

**排查：**
```bash
redis-cli --latency
redis-cli SLOWLOG GET 10
```

**原因：**
- 网络延迟：客户端和Redis不在同一机器
- 大Key操作：`KEYS *`、`HGETALL`超大Hash
- CPU瓶颈：单线程模型下复杂操作阻塞

**解决：**
- 把Redis和App部署在同一机器或同机房
- 禁用`KEYS`，用`SCAN`代替
- 拆分大Key
- 避免`HGETALL`大Hash，用`HSCAN`

---

## G.4 网络问题

### G.4.1 TIME_WAIT过多

**症状：**
```bash
netstat -an | grep TIME_WAIT | wc -l
```
输出几百上千。

**原因：**
HTTP客户端每次请求都创建新连接而不是复用。

**解决：**
```go
client := &http.Client{
    Transport: &http.Transport{
        MaxIdleConns:        100,
        MaxIdleConnsPerHost: 10,
        IdleConnTimeout:     90 * time.Second,
    },
}
```

### G.4.2 DNS解析慢

**症状：**
gRPC调用偶尔卡住好几秒。

**原因：**
DNS解析超时，特别是跨机房部署时。

**解决：**
```go
conn, _ := grpc.Dial(
    "dns:///service-name:50051",
    grpc.WithDefaultServiceConfig(`{"loadBalancingPolicy":"round_robin"}`),
)
```

---

## G.5 内存问题

### G.5.1 内存泄漏

**症状：**
程序内存使用持续增长，最终OOM。

**排查：**
```bash
go tool pprof http://localhost:6060/debug/pprof/heap
```
（需先在代码中 `import _ "net/http/pprof"` 并启动HTTP服务，见上方G.5.1小节）

常见泄漏场景：
- goroutine泄漏：启动了goroutine但从不退出
- 长时间运行的map不断增长没有清理
- time.Ticker没有Stop
- 闭包捕获了大对象的引用

**解决（goroutine泄漏检查）：**
```go
import _ "net/http/pprof"

go func() {
    log.Println(http.ListenAndServe("localhost:6060", nil))
}()

fmt.Println(runtime.NumGoroutine())
```

### G.5.2 频繁GC

**症状：**
CPU使用率高，大量时间花在GC上。

**排查：**
```bash
GODEBUG=gctrace=1 ./app
```

**解决：**
- 减少对象分配（复用buffer、用sync.Pool）
- 用`strings.Builder`代替`+=`
- 调整GOGC环境变量

---

## G.6 性能问题

### G.6.1 接口响应慢

**排查清单：**
1. 这个请求走了几次数据库？有没有N+1查询？
2. 有没有加缓存？缓存命中率多少？
3. JSON序列化大对象花了多久？
4. 有没有不需要的外部HTTP调用？
5. 日志打印是否太多？

**解决：**
- N+1查询：用Preload或JOIN一次性加载
- 加Redis缓存热数据
- 分页限制最大值
- 用`encoding/json`的`Encoder`代替`Marshal`（流式）

### G.6.2 CPU 100%

**排查：**
```bash
go tool pprof http://localhost:6060/debug/pprof/profile?seconds=30
```

**常见原因：**
- 循环中的正则编译（`regexp.Compile`在循环里）
- JSON反复编解码
- 不合理的递归或死循环
- 锁竞争导致自旋等待

---

排查Bug的黄金法则：**先复现，再看日志，然后二分定位**。80%的问题在前两步就能定位，剩下20%需要工具和经验的帮助。这份指南就是帮你缩短那20%的排查时间。

---
[← 上一章：附录F-HTTP状态码大全.md](附录F-HTTP状态码大全/) | [下一章：附录H-推荐学习资源.md →](附录H-推荐学习资源/)
