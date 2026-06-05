# 第61章 · Redis进阶

> "五种基本数据类型可以应付80%的场景，但那剩下的20%才是最考验功力的地方。你需要在Redis里原子地执行多条命令、你要让服务宕机后数据不丢、你的内存满了要优雅地撵人——这些高级特性决定了你能不能用Redis撑起一个真正的生产系统。"

---

## 61.1 发布订阅（Pub/Sub）

发布订阅是一种**消息广播**模式——发布者往频道扔消息，订阅了这个频道的所有人都能收到。

```bash
SUBSCRIBE news:system
```

在一个终端订阅 `news:system` 频道：

```
Reading messages... (press Ctrl-C to quit)
1) "subscribe"
2) "news:system"
3) (integer) 1
```

在另一个终端发布消息：

```bash
PUBLISH news:system "服务器将于00:00进行维护"
(integer) 1
```

订阅者立刻收到：

```
1) "message"
2) "news:system"
3) "服务器将于00:00进行维护"
```

### 模式订阅

用通配符订阅一组频道：

```bash
PSUBSCRIBE news:*
```

现在 `news:system`、`news:update`、`news:emergency` 都能收到。

### Pub/Sub的致命缺陷

1. **消息不持久化**：订阅者断开期间的错过的消息，不会重发——丢了就丢了。
2. **没有ACK机制**：Redis扔出去就不管了，不管你有没有处理成功。
3. **消费者不均衡**：所有订阅者收到全部消息——无法做消费者组负载均衡。

**结论**：Pub/Sub适合实时通知、简单的广播场景。**不适合**做真正的消息队列——那得用Redis的Stream类型（5.0+）或者专业的RabbitMQ/Kafka。

---

## 61.2 事务

Redis的事务和MySQL的事务是两种东西——Redis的事务**没有回滚**，但保证**原子性**（一系列命令要么全执行，要么全不执行）。

```bash
MULTI
SET key1 "value1"
INCR counter
SET key2 "value2"
EXEC
```

进入MULTI模式后，命令不会立即执行——而是排入队列。EXEC一次性按顺序执行全部。结果：

```
1) OK
2) (integer) 1
3) OK
```

### DISCARD：取消事务

```bash
MULTI
SET key1 "value1"
DISCARD
GET key1
(nil)
```

DISCARD清空队列，key1根本没被设置。

### 事务的局限

在执行队列期间，如果某条命令语法错误（比如写成了 `SETT` 而不是 `SET`），EXEC时**整队都不执行**。但如果命令语法对、运行时出错（比如对String类型执行LPUSH），**其他命令不受影响，继续执行**。

没有回滚！这不是bug，是设计取舍——Redis追求极简和极速，回滚意味着要记录操作日志，违背了它"快"的理念。

### WATCH：乐观锁

WATCH让事务有了"条件执行"的能力：

```bash
WATCH mykey
val = GET mykey
val = val + 1
MULTI
SET mykey val
EXEC
```

在 `WATCH mykey` 到 `EXEC` 之间，如果 `mykey` 被其他客户端修改了——**EXEC不会执行，返回nil**（而不是报错）。这叫**乐观锁**——假设没人来抢，先做；如果发现有人抢了，你的操作无效，你自己重试。

**现实案例**：秒杀库存扣减。

```bash
WATCH stock:product1
GET stock:product1
(integer) 0
MULTI
DECR stock:product1
EXEC
(nil)
```

库存已经是0了，WATCH保证了不会减到负数。在Go代码中捕获EXEC返回nil，做相应处理。

🤔 **想多一点**：Redis的事务和MySQL事务的区别是面试常见题。MySQL事务有ACID全套（原子性、回滚、隔离级别），Redis事务只有"原子性执行一批命令"——因为Redis不是关系型数据库，它追求的是"够用且飞快"而不是"完备且稳妥"。

---

## 61.3 Lua脚本

Lua脚本让Redis在**服务端原子执行**多条命令——比事务强的地方是：可以在执行过程中做逻辑判断（if/else/循环）。

### EVAL

```bash
EVAL "return redis.call('GET', KEYS[1])" 1 mykey
```

- 第一个参数：Lua脚本（字符串）。
- 第二个参数：KEYS的数量。
- 后面依次：KEYS[1], KEYS[2], ..., ARGV[1], ARGV[2], ...

### 实战：原子扣库存

```bash
EVAL "
    local stock = redis.call('GET', KEYS[1])
    if not stock then
        return -1
    end
    stock = tonumber(stock)
    if stock <= 0 then
        return 0
    end
    redis.call('DECR', KEYS[1])
    return 1
" 1 stock:product1
```

逻辑：查库存 → 判断是否够 → 减库存 → 返回结果。**整个过程在Redis内部原子执行**，不会被其他命令打断。

### SCRIPT LOAD + EVALSHA

Lua脚本每次都要传完整文本，网络开销大。可以先load脚本，得到一个SHA1摘要，之后用摘要调用：

```bash
SCRIPT LOAD "return redis.call('GET', KEYS[1])"
"a59fae4f1c7b6e9a..."

EVALSHA a59fae4f1c7b6e9a... 1 mykey
```

### Lua脚本的原子性

- 脚本执行期间，Redis不处理其他命令——**天然原子**。
- 但意味着脚本不能太慢——一条脚本执行10秒，整个Redis卡10秒。
- **生产环境铁则**：Lua脚本必须极轻量，只做简单的逻辑判断和命令组合。

---

## 61.4 持久化：RDB vs AOF

Redis是内存数据库，不持久化的话一关机数据全丢。Redis提供两种持久化方案：

### RDB（快照）

RDB在**某个时间点**给整个内存拍一张"快照"，存到 `.rdb` 文件。

**触发方式**：

```bash
SAVE
```

立即拍快照——**会阻塞所有请求**，生产禁用。

```bash
BGSAVE
```

fork一个子进程拍快照，主进程继续服务。推荐。

**自动触发**（配置）：

```
save 900 1
save 300 10
save 60 10000
```

- 900秒内至少1次修改 → 触发BGSAVE。
- 300秒内至少10次修改 → 触发BGSAVE。
- 60秒内至少10000次修改 → 触发BGSAVE。

**优点**：文件紧凑，恢复快，子进程做不影响主进程。
**缺点**：不是实时持久化——最近一次快照之后的数据，挂了就丢了。

### AOF（追加日志）

AOF把每一条写命令追加到日志文件末尾，类似MySQL的binlog。

```
appendonly yes
```

AOF文件内容大致为：

```
*3
$3
SET
$6
mykey
$7
myvalue
```

**fsync策略**：

```
appendfsync always   每次写都刷盘  最安全，最慢
appendfsync everysec 每秒刷一次    推荐，数据最多丢1秒
appendfsync no       系统决定    最快，最不安全
```

`everysec` 是生产环境的默认选择——在安全和性能之间平衡。

**缺点**：AOF文件会越来越大。Redis提供 `BGREWRITEAOF`——在后台重写AOF，去掉冗余命令（比如同一个key被SET了5次，只保留最后一次）。

### 混合持久化（Redis 4.0+）

RDB快照 + AOF增量：

```
aof-use-rdb-preamble yes
```

AOF文件的前半部分是RDB格式的快照（加载快），后半部分是RDB之后的AOF增量（数据新）。这是当前最推荐的方案——兼顾恢复速度和数据完整性。

### 选择建议

| 场景 | 推荐方案 |
|------|---------|
| 纯缓存（可以丢） | 不用持久化 |
| 一般业务 | RDB，save配置合理间隔 |
| 数据不能丢 | AOF everysec 或混合持久化 |
| 最高安全 | AOF always（但性能差） |

---

## 61.5 过期策略

设了EXPIRE的key到了时间怎么被删除？Redis用了**两套组合拳**：

### 惰性删除

每次访问一个key时，先检查它是否过期——过期了就删掉，返回nil。

**优点**：CPU友好（只在访问时才检查）。
**缺点**：有些key过期后没人访问，就一直占着内存——"内存泄漏"。

### 定期删除

Redis每100ms随机抽查一批key，删除其中过期的。

**不是全量扫描**——如果100万个key同时过期，全扫一遍CPU炸了。所以是随机抽查，每次处理总key的25%左右。

### 两套组合

惰性删除 + 定期删除 配合，让Redis在CPU消耗和内存浪费之间取得平衡。但如果内存真的满了，还是有过期的key没被删掉——这时候**内存淘汰策略**就出场了。

---

## 61.6 内存淘汰策略

当Redis内存达到 `maxmemory` 上限时，再有新数据要写入——Redis必须"赶走"一些旧数据。赶谁？有8种策略：

| 策略 | 说明 |
|------|------|
| **noeviction** | 不淘汰，直接报错（默认） |
| **allkeys-lru** | 对所有key，淘汰**最近最少使用**的 |
| **volatile-lru** | 只对设了过期时间的key，淘汰LRU |
| **allkeys-lfu** | 对所有key，淘汰**最不频繁使用**的 |
| **volatile-lfu** | 只对设了过期时间的key，淘汰LFU |
| **allkeys-random** | 对所有key，随机淘汰 |
| **volatile-random** | 只对设了过期时间的key，随机淘汰 |
| **volatile-ttl** | 只对设了过期时间的key，淘汰**快要过期**的 |

### LRU vs LFU

**LRU（Least Recently Used）**：看"多久没用过"。最近被访问过的key不会被淘汰。

**LFU（Least Frequently Used）**：看"被用过多少次"。即使昨天访问过但只访问了1次，也比不上今天被访问了100次的key。

**实战建议**：
- 缓存场景用 `allkeys-lru`（最常用）。
- 热点数据效应明显的（如热点新闻、热榜商品），用 `allkeys-lfu`。

### 配置

```
maxmemory 2gb
maxmemory-policy allkeys-lru
```

🤔 **想多一点**：面试官问"Redis过期key没被删、内存又满了怎么办？"答案就是淘汰策略。默认是 `noeviction`（拒绝写入），这是很危险的——你的应用突然发现Redis写不进去数据了。一定要设置 `maxmemory` 和 `maxmemory-policy`，这是运维的基本功。

---

## 61.7 Pipeline：批量命令

Pipeline允许客户端**一次性发送多个命令**而不等待每个命令的响应——类似攒一批快递一起寄，比分10次寄省了9次往返时间。

Redis的单次命令RTT（Round Trip Time）在局域网约0.1ms，但客户端和服务器的网络延迟加上处理开销，累积起来就是性能瓶颈。

```
单条发送（100次）：
客户端→服务器 [等待] 服务器→客户端 [等待]
客户端→服务器 [等待] 服务器→客户端 [等待]
... 重复100次
总时间 ≈ 100 × RTT + 执行时间

Pipeline（100条）：
客户端→服务器 [100条批量发]
服务器→客户端 [100条批量回]
总时间 ≈ 1 × RTT + 执行时间
```

**严禁**：Pipeline不是原子性的——中间可能穿插其他客户端的命令。它不是事务的替代品。

**适用场景**：批量初始化数据、批量查询（MGET就是Pipeline的封装）、预热缓存。

在Go中，go-redis自动支持Pipeline，下一章会演示。

---

## 本章小结

| 知识点 | 要点 |
|--------|------|
| Pub/Sub | 消息广播，不持久化、无ACK，适合实时通知，不适合消息队列 |
| 事务 | MULTI/EXEC原子执行一组命令，无回滚，WATCH实现乐观锁 |
| Lua脚本 | 服务端原子执行+逻辑判断，SCRIPT LOAD减少网络开销，脚本必须极轻量 |
| RDB | 快照持久化，子进程执行，恢复快但有数据丢失窗口 |
| AOF | 追加日志，everysec推荐，重写减少体积 |
| 混合持久化 | RDB快照+AOF增量，4.0+最佳选择 |
| 过期策略 | 惰性删除（访问时检查）+ 定期删除（随机抽查） |
| 淘汰策略 | allkeys-lru最常用，noeviction（默认拒绝）危险需改 |
| Pipeline | 批量发命令减少RTT，非原子，适合批量操作 |

> 🚀 下一章：第62章 · Redis实战。理论和工具都有了，现在把它们组装成真正的解决方案。缓存穿透、击穿、雪崩——这"缓存三兄弟"一个比一个凶。还有缓存与数据库的一致性、分布式锁、计数器、限流器……这些才是你每天工作中真正要写的东西。

---
[← 上一章：60-Redis入门](60-Redis入门.md) | [下一章：62-Redis实战 →](62-Redis实战.md)
