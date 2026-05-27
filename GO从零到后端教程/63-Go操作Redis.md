# 第63章 · Go操作Redis

> "Redis的命令你已经烂熟于心——SET、GET、ZADD、LPUSH……现在回到Go的世界，把这些redis-cli里的命令翻译成Go函数。go-redis是Go生态中最成熟的Redis客户端，它把Redis命令封装成了Go方法，参数类型安全，Pipeline和事务支持完善。这一章带你从连接到实战，全面掌握Go操作Redis。"

---

## 63.1 go-redis入门

### 安装

```bash
go get github.com/redis/go-redis/v9
```

### 建立连接

```go
package main

import (
    "context"
    "fmt"
    "log"

    "github.com/redis/go-redis/v9"
)

func main() {
    rdb := redis.NewClient(&redis.Options{
        Addr:     "127.0.0.1:6379",
        Password: "",
        DB:       0,
    })

    ctx := context.Background()
    pong, err := rdb.Ping(ctx).Result()
    if err != nil {
        log.Fatal("连接Redis失败:", err)
    }
    fmt.Println(pong)

    defer rdb.Close()
}
```

- `Addr`：Redis服务器的地址和端口。
- `Password`：没有密码就留空。
- `DB`：Redis有16个逻辑数据库（0~15），默认用0。**多应用共享一个Redis时，用不同DB编号隔离**。
- `ctx`：Go 1.7+的context标准——每个Redis操作都传context，用于超时控制和取消。

### 单机 vs 集群 vs 哨兵

```go
rdb := redis.NewClient(&redis.Options{...})

rdb := redis.NewClusterClient(&redis.ClusterOptions{
    Addrs: []string{":7000", ":7001", ":7002"},
})

rdb := redis.NewFailoverClient(&redis.FailoverOptions{
    MasterName:    "mymaster",
    SentinelAddrs: []string{":26379", ":26380", ":26381"},
})
```

本书以单机模式为主，集群和哨兵只是在Options上换一个Client类型——API完全一样。

---

## 63.2 基本操作

### String

```go
err := rdb.Set(ctx, "username", "zhangsan", 0).Err()

val, err := rdb.Get(ctx, "username").Result()
if err == redis.Nil {
    fmt.Println("key不存在")
} else if err != nil {
    log.Fatal(err)
}
fmt.Println(val)

rdb.Del(ctx, "username")

rdb.Set(ctx, "counter", 0, 0)
rdb.Incr(ctx, "counter")
rdb.IncrBy(ctx, "counter", 10)

rdb.SetNX(ctx, "lock:task", "locked", 10*time.Second)

rdb.Expire(ctx, "session:abc", 30*time.Minute)

rdb.MSet(ctx, "key1", "val1", "key2", "val2")
vals, _ := rdb.MGet(ctx, "key1", "key2").Result()
```

注意事项：
- `redis.Nil`：Redis的"key不存在"错误。判断时用它而不是直接和nil比较。
- `0` 作为过期时间：表示永不过期。
- `Set` 返回的是 `*StatusCmd`，用 `.Err()` 判断是否出错。

### Hash

```go
rdb.HSet(ctx, "user:1",
    "username", "zhangsan",
    "email", "zs@test.com",
    "age", 25,
)

name, _ := rdb.HGet(ctx, "user:1", "username").Result()

allFields, _ := rdb.HGetAll(ctx, "user:1").Result()
for k, v := range allFields {
    fmt.Printf("%s: %s\n", k, v)
}

rdb.HIncrBy(ctx, "user:1", "age", 5)

exists, _ := rdb.HExists(ctx, "user:1", "email").Result()

rdb.HDel(ctx, "user:1", "age")
```

### List

```go
rdb.LPush(ctx, "tasks", "task1", "task2")
rdb.RPush(ctx, "tasks", "task3")

all, _ := rdb.LRange(ctx, "tasks", 0, -1).Result()
fmt.Println(all)

left, _ := rdb.LPop(ctx, "tasks").Result()
right, _ := rdb.RPop(ctx, "tasks").Result()

length, _ := rdb.LLen(ctx, "tasks").Result()
```

### Set

```go
rdb.SAdd(ctx, "tags:article1", "golang", "redis", "database")

members, _ := rdb.SMembers(ctx, "tags:article1").Result()

isMember, _ := rdb.SIsMember(ctx, "tags:article1", "golang").Result()

rdb.SAdd(ctx, "tags:article2", "redis", "python", "java")

common, _ := rdb.SInter(ctx, "tags:article1", "tags:article2").Result()
union, _ := rdb.SUnion(ctx, "tags:article1", "tags:article2").Result()
diff, _ := rdb.SDiff(ctx, "tags:article1", "tags:article2").Result()
```

### Sorted Set

```go
rdb.ZAdd(ctx, "leaderboard",
    redis.Z{Score: 100, Member: "player1"},
    redis.Z{Score: 250, Member: "player2"},
    redis.Z{Score: 180, Member: "player3"},
)

top3, _ := rdb.ZRevRangeWithScores(ctx, "leaderboard", 0, 2).Result()
for _, z := range top3 {
    fmt.Printf("%s: %.0f\n", z.Member, z.Score)
}

rank, _ := rdb.ZRank(ctx, "leaderboard", "player3").Result()
fmt.Printf("player3 排名: %d\n", rank+1)

score, _ := rdb.ZScore(ctx, "leaderboard", "player3").Result()

rdb.ZIncrBy(ctx, "leaderboard", 50, "player1")

rangeRes, _ := rdb.ZRangeByScoreWithScores(ctx, "leaderboard", &redis.ZRangeBy{
    Min: "150",
    Max: "250",
}).Result()
```

---

## 63.3 Pipeline

把多个命令打包一次发送：

```go
pipe := rdb.Pipeline()

incr := pipe.Incr(ctx, "counter")
pipe.Expire(ctx, "counter", time.Hour)

_, err := pipe.Exec(ctx)
if err != nil {
    log.Fatal(err)
}

fmt.Println(incr.Val())
```

Pipeline不是事务——中间可能被其他客户端命令穿插。它只是减少了网络RTT。

### Pipelined：更优雅的批量操作

```go
var incr *redis.IntCmd

cmds, err := rdb.Pipelined(ctx, func(pipe redis.Pipeliner) error {
    incr = pipe.Incr(ctx, "counter")
    pipe.Expire(ctx, "counter", time.Hour)
    return nil
})

for _, cmd := range cmds {
    fmt.Println(cmd)
}
fmt.Println(incr.Val())
```

---

## 63.4 事务

```go
func TransferPoints(ctx context.Context, rdb *redis.Client, from, to string, amount int) error {
    txf := func(tx *redis.Tx) error {
        fromBalance, err := tx.Get(ctx, "points:"+from).Int()
        if err != nil && err != redis.Nil {
            return err
        }
        if fromBalance < amount {
            return fmt.Errorf("余额不足")
        }

        _, err = tx.TxPipelined(ctx, func(pipe redis.Pipeliner) error {
            pipe.DecrBy(ctx, "points:"+from, int64(amount))
            pipe.IncrBy(ctx, "points:"+to, int64(amount))
            return nil
        })
        return err
    }

    for i := 0; i < 3; i++ {
        err := rdb.Watch(ctx, txf, "points:"+from)
        if err == nil {
            return nil
        }
        if err == redis.TxFailedErr {
            continue
        }
        return err
    }

    return fmt.Errorf("事务重试达到最大次数")
}
```

- `rdb.Watch`：内部用WATCH实现乐观锁。如果被Watch的key在事务执行前被修改，`txf` 返回 `redis.TxFailedErr`——重试。
- `tx.TxPipelined`：在WATCH保护的上下文中批量执行命令。
- 代码逻辑：查余额 → 检查是否够 → 在事务中扣减 → 如果被其他修改打断就重试（最多3次）。

---

## 63.5 Lua脚本

```go
var deductStockScript = redis.NewScript(`
    local stock = redis.call("GET", KEYS[1])
    if not stock then
        return -1
    end
    stock = tonumber(stock)
    if stock <= 0 then
        return 0
    end
    redis.call("DECR", KEYS[1])
    return 1
`)

func DeductStock(ctx context.Context, rdb *redis.Client, productID string) (int, error) {
    key := "stock:" + productID
    result, err := deductStockScript.Run(ctx, rdb, []string{key}).Int()
    return result, err
}
```

`redis.NewScript` 会计算脚本的SHA1，初次执行时用EVAL发送完整脚本，之后自动用EVALSHA——不需要你手动管理。

---

## 63.6 发布订阅

```go
func SubscribeMessages(ctx context.Context, rdb *redis.Client) {
    pubsub := rdb.Subscribe(ctx, "news:system")
    defer pubsub.Close()

    ch := pubsub.Channel()
    for msg := range ch {
        fmt.Printf("收到消息 [%s]: %s\n", msg.Channel, msg.Payload)
    }
}
```

```go
func PublishMessage(ctx context.Context, rdb *redis.Client) {
    rdb.Publish(ctx, "news:system", "服务器维护通知")
}
```

---

## 63.7 连接池配置

go-redis默认的连接池参数：

```go
rdb := redis.NewClient(&redis.Options{
    Addr:         "127.0.0.1:6379",
    PoolSize:     10,
    MinIdleConns: 3,
    MaxRetries:   3,
    DialTimeout:  5 * time.Second,
    ReadTimeout:  3 * time.Second,
    WriteTimeout: 3 * time.Second,
    PoolTimeout:  4 * time.Second,
})
```

| 参数 | 默认值 | 说明 |
|------|--------|------|
| PoolSize | 10 * runtime.GOMAXPROCS | 最大连接数 |
| MinIdleConns | 0 | 最小空闲连接（保持预连接减少延迟） |
| MaxRetries | 3 | 命令失败重试次数 |
| DialTimeout | 5s | 建立TCP连接超时 |
| ReadTimeout | 3s | 等待Redis返回结果的超时 |
| WriteTimeout | 3s | 发送命令到Redis的超时 |
| PoolTimeout | 4s | 等待空闲连接的超时 |

`PoolSize` 设太大没用——Redis是单线程的，连接再多也是排队执行。一般设为CPU核数的1~2倍即可。

---

## 63.8 分布式锁的Go实现

完整版：

```go
type RedisLock struct {
    client *redis.Client
    key    string
    value  string
    ttl    time.Duration
}

func NewRedisLock(client *redis.Client, key string, ttl time.Duration) *RedisLock {
    return &RedisLock{
        client: client,
        key:    "lock:" + key,
        value:  uuid.New().String(),
        ttl:    ttl,
    }
}

func (l *RedisLock) Lock(ctx context.Context) (bool, error) {
    return l.client.SetNX(ctx, l.key, l.value, l.ttl).Result()
}

var unlockScript = redis.NewScript(`
    if redis.call("GET", KEYS[1]) == ARGV[1] then
        return redis.call("DEL", KEYS[1])
    else
        return 0
    end
`)

func (l *RedisLock) Unlock(ctx context.Context) error {
    _, err := unlockScript.Run(ctx, l.client, []string{l.key}, l.value).Result()
    return err
}

func (l *RedisLock) Refresh(ctx context.Context) (bool, error) {
    result, err := l.client.Expire(ctx, l.key, l.ttl).Result()
    return result, err
}
```

使用：

```go
lock := NewRedisLock(rdb, "order:123", 30*time.Second)

ok, err := lock.Lock(ctx)
if !ok {
    return fmt.Errorf("获取锁失败")
}
defer lock.Unlock(ctx)

processOrder()
```

---

## 本章小结

| 知识点 | 要点 |
|--------|------|
| 连接 | `redis.NewClient(&redis.Options{...})`，Ping验证连接，defer Close |
| String | Set/Get/Del/Incr/IncrBy/SetNX/MGet/MSet，`redis.Nil` 表示不存在 |
| Hash | HSet/HGet/HGetAll/HIncrBy/HExists/HDel |
| List | LPush/RPush/LRange/LPop/RPop/LLen |
| Set | SAdd/SMembers/SIsMember/SInter/SUnion/SDiff |
| Sorted Set | ZAdd/ZRevRangeWithScores/ZRank/ZScore/ZIncrBy/ZRangeByScore |
| Pipeline | `rdb.Pipeline()` 或 `rdb.Pipelined()`，减少RTT，非原子 |
| 事务 | `rdb.Watch()` 乐观锁，`tx.TxPipelined()` 批量执行，冲突时重试 |
| Lua脚本 | `redis.NewScript` 自动管理SHA1，原子执行复杂逻辑 |
| Pub/Sub | `rdb.Subscribe/Publish`，Channel()接收消息 |
| 连接池 | PoolSize/MaxRetries/各种Timeout，单线程Redis无需太大连接池 |
| 分布式锁 | SetNX + UUID + Lua解锁 + 可选的Refresh续期 |

> 🚀 下一章：第64章 · 数据库篇总结。15章的数据库之旅即将到达终点。我们来做一个总回顾——MySQL和Redis各自的核心知识体系梳理、高频面试题速查、以及下一篇的精彩预告。这一章是你面试前的最后一页"小抄"。

---
[← 上一章：62-Redis实战](62-Redis实战.md) | [下一章：64-数据库篇总结 →](64-数据库篇总结.md)
