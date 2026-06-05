# 第62章 · Redis实战

> "缓存用好了是核武器，用不好是自杀炸弹。你以为加个缓存就能让数据库减负——结果缓存一挂，数据库瞬间承受了原本三倍的流量（不仅原来的请求过来了，还多了缓存失败的重试），直接宕机。这就是著名的'缓存雪崩'。这一章讲的不只是怎么用Redis，而是怎么用Redis**不出事**。"

---

## 62.1 缓存穿透：查不存在的数据

### 场景

用户请求 `GET /products/99999`，商品99999根本不存在。你的代码逻辑是：

1. 先查Redis缓存——没命中。
2. 再查MySQL——也没找到。
3. 返回"商品不存在"。

攻击者用脚本瞬间发起10万个请求，全部查不存在的商品ID——Redis每次都没命中，MySQL每次都要查。10万个请求直接打在数据库上——这就是**缓存穿透**。

### 为什么发生

Redis里没有不存在商品的缓存标记。正常逻辑是"查到就缓存，查不到就过"。但"查不到"也可以缓存——这就是解决方案。

### 解决方案一：缓存空值

MySQL返回"不存在"时，在Redis中**也缓存一个空标记**：

```go
val := redis.Get("product:99999")
if val == "NULL" {
    return nil
}
data := mysql.Query("SELECT * FROM products WHERE id = ?", 99999)
if len(data) == 0 {
    redis.Set("product:99999", "NULL", EX, 60)
    return nil
}
redis.Set("product:99999", data)
return data
```

用一个特殊值 `"NULL"` 标记"不存在"，设较短过期时间（防止后面真的有这个商品了，被空标记挡着）。

**缺点**：如果攻击者遍历不同的不存在的ID，内存里会塞满空标记。

### 解决方案二：布隆过滤器

布隆过滤器是一种**概率型数据结构**——它能告诉你"这个ID**肯定不存在**"或"这个ID**可能存在**"（不会漏判，只会误判）。

原理简单说：多个哈希函数 + 一个比特数组。插入一个ID时，在多个位置置1。查询时检查所有位置是否都是1——有一个不是1说明肯定没插过。

**使用**：在Redis和MySQL之前加一层布隆过滤器。请求到达 → 布隆过滤器判断 → 不存在直接返回，存在的再去Redis查。

- 优点：内存占用极低（亿级数据只需几十MB），不会误杀（说"不存在"就一定不存在）。
- 缺点：有误判率（说"可能存在"时可能实际不存在），不能删除元素。

**Go布隆过滤器库**：

```go
import "github.com/bits-and-blooms/bloom/v3"

filter := bloom.NewWithEstimates(1000000, 0.01)
filter.Add([]byte("product:12345"))

if !filter.Test([]byte("product:99999")) {
    return nil
}
```

---

## 62.2 缓存击穿：热点数据过期

### 场景

双11零点，一件爆款商品秒杀。它的数据在Redis中刚好到期了——一秒后10万个并发请求同时来查这个商品。

- 请求1~100000：Redis没命中 → 全部打到MySQL。
- MySQL：一个SELECT扛住了，100000个——当场跪下。

这与缓存穿透的区别：缓存穿透查的是**不存在**的数据，缓存击穿（某个热点key过期瞬间，大量请求打到数据库，详见附录I）查的是**存在但刚好过期**的数据。

### 解决方案一：互斥锁

第一个请求发现缓存没命中后，去**拿一把锁**。拿到锁的请求去查MySQL回填缓存，其他请求等待锁释放后再读缓存：

```go
func GetProduct(id string) (string, error) {
    val := redis.Get("product:" + id)
    if val != "" {
        return val, nil
    }

    lockKey := "lock:product:" + id
    locked := redis.SetNX(lockKey, "1", 10)
    if !locked {
        time.Sleep(50 * time.Millisecond)
        return GetProduct(id)
    }
    defer redis.Del(lockKey)

    data := mysql.Query("SELECT * FROM products WHERE id = ?", id)
    redis.Set("product:"+id, data, EX, 3600)
    return data, nil
}
```

**注意**：检查锁之后还要**二次检查缓存**——可能锁住的线程已经把数据加载好了。

### 解决方案二：永不过期

热点数据不设过期时间，通过**异步更新**的方式刷新：

```go
redis.Set("product:"+id, data)

go func() {
    time.Sleep(5 * time.Minute)
    fresh := mysql.Query("SELECT * FROM products WHERE id = ?", id)
    redis.Set("product:"+id, fresh)
}()
```

逻辑过期（在value里存一个过期时间戳），读取时发现过期了，异步刷新。

---

## 62.3 缓存雪崩：大量缓存同时过期

### 场景

你给100万个商品缓存设了1小时过期时间。上线一小时后——同一秒内，100万个key集体过期。

```
时刻 T-1：Redis 100万key，MySQL扛着100 QPS（大部分请求被缓存挡住）
时刻 T：100万key集体过期
时刻 T+1：所有请求直接打到MySQL——瞬间10000 QPS
时刻 T+2：MySQL崩溃，整个系统不可用
```

### 解决方案

**过期时间加随机值**：

```go
baseTTL := 3600
randomOffset := rand.Intn(600)
redis.Set(key, value, baseTTL+randomOffset)
```

不是3600秒统一过期，而是3600~4200秒之间随机分布。把"雪崩"拆散成小规模降雪。

**多级缓存**：本地缓存（进程内存）→ Redis → MySQL。即使Redis挂了，本地缓存还能撑一阵。

**限流降级**：缓存失效后，先不急着全量查DB——对数据库查询做限流，让系统慢慢恢复。

**Redis集群**：主从+哨兵，一台Redis挂了不影响服务。

---

## 62.4 缓存与数据库一致性

这是分布式系统中最顽固的难题之一——缓存的本质是"一份数据的两个副本"，两个副本必然存在不一致。

### 先删缓存，再写DB？❌

```
1. 删缓存
2. 写DB（还没写完）
3. 另一个线程读 → 缓存miss → 查DB（读到旧值）→ 写缓存（旧值写入缓存）
4. 写完DB（新值）
```

结果：缓存中是旧值，DB是新值——不一致。

### 先写DB，再删缓存？⚠️ 大部分场景可行

```
1. 写DB（新值）
2. 删缓存
3. 下次读 → 缓存miss → 查DB → 写缓存（新值）
```

但如果步骤2失败（删缓存失败）——DB是新值，缓存是旧值。概率低但存在。

### 延迟双删：稳健方案

```
1. 删缓存
2. 写DB
3. 等500ms
4. 再删一次缓存
```

第二次删除是为了清除"步骤2期间其他线程读到的旧值写入的缓存"。500ms是一个经验值。

### 终极方案：订阅binlog

最可靠的做法：不直接在业务代码里删缓存——**监听MySQL的binlog变更**，通过Canal等工具解析binlog，自动更新或删除对应的缓存。

**流程**：

```
业务写DB → MySQL生成binlog → Canal监听binlog → 解析变更 → 更新/删除Redis
```

这是阿里开源的方案，做数据同步和缓存一致性非常可靠。但架构复杂度上升——小项目用延迟双删就够了。

### 实践准则

1. 如果缓存是**辅助加速**（数据丢了不致命），先写DB再删缓存，容忍短暂不一致。
2. 如果缓存数据**必须一致**，考虑不用缓存——直接查DB，或者用binlog同步。
3. 给缓存设**合理的过期时间**——即使不一致，过期后也会自动修正。

---

## 62.5 分布式锁

### 为什么需要分布式锁

单机程序可以用Go的 `sync.Mutex` 互斥——所有goroutine在一个进程里。但分布式系统中，多个服务实例部署在不同机器上，它们之间没有"共享内存"，需要用外部工具（Redis）协调。

**场景**：定时任务。10台服务器都在凌晨3点执行"生成日报"任务——如果没有分布式锁，10份相同的日报会被生成10次。

### SET NX PX 实现

```go
func AcquireLock(client *redis.Client, key string, value string, ttl time.Duration) bool {
    result, err := client.SetNX(ctx, key, value, ttl).Result()
    if err != nil {
        return false
    }
    return result
}
```

`value` 必须是**唯一标识**（如UUID），用于释放时验证：

```go
func ReleaseLock(client *redis.Client, key string, value string) {
    script := `
        if redis.call("GET", KEYS[1]) == ARGV[1] then
            return redis.call("DEL", KEYS[1])
        else
            return 0
        end
    `
    client.Eval(ctx, script, []string{key}, value)
}
```

**为什么释放锁要用Lua脚本？** 保证"检查值 → 释放锁"是原子操作。如果分两步：
1. `GET lock` → 值是我的 → 可以删
2. 在1和2之间锁过期了，别人拿到了锁
3. `DEL lock` → 把别人的锁删了！

### 锁续期问题

如果一个任务执行了太久，锁过期了——任务还在跑。用**看门狗机制**：启动一个协程定期刷新锁的过期时间。

Redisson（Java库）有看门狗实现。Go社区常用 `redsync` 或自己用goroutine + EXPIRE实现。

### Redlock算法

Redis官方作者提出的多节点分布式锁方案：在N个独立的Redis实例上获取锁，必须获得半数以上才认为获取成功。防止单节点故障导致锁失效。

**争议**：Martin Kleppmann（《数据密集型应用系统设计》作者）和Redis作者antirez就此有过激烈辩论。Redlock在极端网络分区下存在安全性问题。对绝大多数业务，**单节点SET NX + Lua解锁**已经够用。

---

## 62.6 计数器、限流器与延时队列

### 计数器

```go
func IncrementPageView(pageID string) int64 {
    return redis.Incr(ctx, "pv:"+pageID).Val()
}
```

INCR是原子的——并发安全天生保证。

### 滑动窗口限流器

```go
func IsRateLimited(userID string, limit int, window time.Duration) bool {
    key := "rate:" + userID
    now := time.Now().UnixMilli()
    windowStart := now - window.Milliseconds()

    pipe := redis.Pipeline()
    pipe.ZAdd(ctx, key, &redis.Z{Score: float64(now), Member: fmt.Sprintf("%d:%d", userID, now)})
    pipe.ZRemRangeByScore(ctx, key, "0", fmt.Sprintf("%d", windowStart))
    pipe.ZCard(ctx, key)
    pipe.Expire(ctx, key, window)
    cmds, _ := pipe.Exec(ctx)

    count := cmds[2].(*redis.IntCmd).Val()
    return count > int64(limit)
}
```

用Sorted Set做滑动窗口：每个元素的score是时间戳，删除窗口外的旧记录，统计剩余数量。超过限制就拒绝请求。

### 延时队列

用Sorted Set的score存"到期时间"：

```go
func AddDelayedTask(task string, delay time.Duration) {
    executeAt := time.Now().Add(delay).Unix()
    redis.ZAdd(ctx, "delay_queue", &redis.Z{Score: float64(executeAt), Member: task})
}

func PollDelayedTasks() {
    for {
        now := time.Now().Unix()
        tasks := redis.ZRangeByScore(ctx, "delay_queue", &redis.ZRangeBy{
            Min: "0",
            Max: fmt.Sprintf("%d", now),
        }).Val()

        for _, task := range tasks {
            process(task)
            redis.ZRem(ctx, "delay_queue", task)
        }
        time.Sleep(time.Second)
    }
}
```

比如"30分钟后未支付自动取消订单"——把取消任务的执行时间设为 `now + 30分钟`，定时轮询到期任务。

---

## 本章小结

| 知识点 | 要点 |
|--------|------|
| 缓存穿透 | 查不存在的数据穿透缓存，方案：缓存空值 / 布隆过滤器 |
| 缓存击穿 | 热点数据过期，大量请求打DB，方案：互斥锁 / 永不过期 |
| 缓存雪崩 | 大量key同时过期，方案：随机TTL / 多级缓存 / 限流 |
| 缓存一致性 | 经典难题，先写DB再删缓存/延迟双删/binlog同步 |
| 分布式锁 | SET NX PX + Lua解锁（原子），看门狗续期，Redlock多节点 |
| 计数器 | INCR天然原子，页面PV、点赞数 |
| 限流器 | Sorted Set滑动窗口 / 简单计数器 + 过期时间 |
| 延时队列 | Sorted Set按时间戳排序，轮询到期任务 |

> 🚀 下一章：第63章 · Go操作Redis。Redis的命令和原理你都懂了，现在回到Go代码里——用go-redis库把这些命令变成Go的函数调用。连接Redis、操作五种数据类型、Pipeline、事务、分布式锁的Go实现……全部给你代码。

---
[← 上一章：61-Redis进阶](61-Redis进阶.md) | [下一章：63-Go操作Redis →](63-Go操作Redis.md)
