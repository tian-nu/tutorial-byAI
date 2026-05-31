# 第69章 · Redis进阶

> "第68章学会了Redis的基本操作。但如果你把Redis当成内存版的HashMap来用，那你只用了它10%的能力。Redis真正的威力在于它能作为生产环境的基础设施——数据不能因为重启丢失（持久化）、缓存不能无限增长（淘汰策略）、高并发下不能被打穿（缓存三大问题）。这章就是让你从'会用Redis'升级到'能用Redis扛生产流量'。"

---

## 69.1 持久化：内存数据不丢失

Redis是内存数据库，断电数据就没了。但它提供了两种持久化机制把内存数据保存到磁盘。

### 69.1.1 RDB（快照）

在**某个时间点**把整个内存数据生成一个**二进制快照文件**（dump.rdb）。

```
触发时机：满足配置条件（如"900秒内至少1次修改"）
原理：fork子进程，子进程把内存数据写入磁盘，主进程继续处理请求
优点：文件紧凑，恢复快（直接加载二进制文件）
缺点：最后一次快照到宕机之间的数据会丢失
```

配置（redis.conf）：

```
save 900 1        # 900秒内至少1次修改 → 触发快照
save 300 10       # 300秒内至少10次修改 → 触发快照
save 60 10000     # 60秒内至少10000次修改 → 触发快照
dbfilename dump.rdb
```

**手动触发**：
```bash
SAVE    # 主进程执行，阻塞所有请求（生产禁用）
BGSAVE  # 子进程执行，不阻塞（推荐）
```

### 69.1.2 AOF（追加日志）

把**每条写命令**追加到日志文件（appendonly.aof）的末尾。

```
原理：每执行一条写命令，就记录到AOF缓冲区 → 根据策略刷到磁盘
优点：数据更安全（最多丢1秒的数据），文件可读（全是RESP协议的命令）
缺点：文件比RDB大，恢复速度比RDB慢
```

配置：

```
appendonly yes                              # 开启AOF
appendfsync everysec                        # 每秒刷一次盘（推荐）
# appendfsync always                        # 每次写都刷盘（最安全但最慢）
# appendfsync no                            # 交给操作系统决定（可能丢数据）

auto-aof-rewrite-percentage 100             # AOF文件大小增长100%时触发重写
auto-aof-rewrite-min-size 64mb              # 最小重写大小
```

### 69.1.3 RDB vs AOF

| 对比维度 | RDB | AOF |
|----------|-----|-----|
| 数据安全性 | 可能丢几分钟数据 | 最多丢1秒（everysec） |
| 文件大小 | 小（二进制压缩） | 大（文本格式） |
| 恢复速度 | 快 | 慢（需要重放所有命令） |
| 对性能影响 | fork时有短暂影响 | 持续但很小的影响 |
| 生产建议 | 保留，作为备份 | 开启，作为主持久化 |

### 69.1.4 生产环境推荐

**同时开启RDB和AOF**，用AOF保证数据安全，用RDB做灾难备份。Redis重启时优先加载AOF（因为数据更完整）。

---

## 69.2 过期策略

设置了TTL的key到期后怎么删除？Redis用了两种策略的组合：

### 69.2.1 惰性删除

访问key的时候才检查是否过期，过期了就删。

```
优点：对CPU友好（不主动检查）
缺点：过期key如果没人访问，一直占着内存
```

### 69.2.2 定期删除

Redis每隔100ms（默认）随机抽取一批设置了TTL的key，检查是否过期并删除。

```
优点：清理没人访问的过期key
缺点：随机抽取可能漏掉，CPU有开销
```

> 💡 **Redis采用的是惰性删除+定期删除的组合策略**。二者互补——惰性删除保证CPU不被占用，定期删除保证过期的key最终被清理。

### 69.2.3 设置合理的TTL

```bash
# 缓存数据设置TTL
SETEX cache:user:1001 3600 '{"name":"zhangsan"}'

# 已存在的key追加过期时间
EXPIRE session:token123 1800

# 查看剩余时间
TTL cache:user:1001       # 秒
PTTL cache:user:1001      # 毫秒
```

---

## 69.3 内存淘汰策略

当Redis内存满了（到达 `maxmemory` 限制），新的写入怎么办？Redis提供了8种淘汰策略：

| 策略 | 行为 | 适用场景 |
|------|------|---------|
| `noeviction`（默认） | 拒绝写入，返回错误 | 不允许丢数据的场景 |
| `allkeys-lru` | 在所有key中淘汰最近最少使用的 | **通用缓存（推荐）** |
| `volatile-lru` | 在设置了TTL的key中淘汰最近最少使用的 | 过期key为主时 |
| `allkeys-lfu` | 在所有key中淘汰最不频繁使用的 | 有热key冷key明显分化的场景 |
| `volatile-lfu` | 在设置了TTL的key中淘汰最不频繁使用的 | - |
| `allkeys-random` | 在所有key中随机淘汰 | - |
| `volatile-random` | 在设置了TTL的key中随机淘汰 | - |
| `volatile-ttl` | 淘汰TTL最短的key | - |

配置：

```
maxmemory 2gb                        # 最大内存
maxmemory-policy allkeys-lru         # 淘汰策略
```

> 🚨 **默认的 `noeviction` 策略在生产环境中非常危险**——内存满了所有写操作失败，从业务角度看就是系统突然"坏了"。务必根据场景选择一个淘汰策略，缓存场景推荐 `allkeys-lru`。

---

## 69.4 缓存三大问题

### 69.4.1 缓存穿透

**问题**：查询一个**数据库中也不存在**的数据，Redis中没有，每次请求都穿透到数据库。

```
攻击者：查询 userId = -1（不存在）
Redis：查不到
MySQL：查不到 → 返回空
攻击者：×10000次 → MySQL被打垮
```

**解决方案**：

**方案一：缓存空值**
```java
public User getUser(Long id) {
    String key = "user:" + id;
    User user = redis.get(key);
    if (user != null) return user;

    user = db.findById(id);
    if (user != null) {
        redis.setex(key, 3600, user);  // 缓存1小时
    } else {
        redis.setex(key, 300, EMPTY_OBJECT);  // 缓存空值5分钟，防止穿透
    }
    return user;
}
```

**方案二：布隆过滤器**（Bloom Filter）

在Redis前加一层布隆过滤器，快速判断一个key"一定不存在"（存在可能是误判，但不存在一定是准确的）。不存在的数据直接返回，不查Redis也不查数据库。

### 69.4.2 缓存击穿

**问题**：一个**热点key**在过期的一瞬间，大量并发请求同时查询数据库。

```
时间线：
时刻1：hot:product:1001 在Redis中，一切正常
时刻2：hot:product:1001 过期了！
时刻3：1000个请求同时发现Redis中没有 → 1000个请求同时打到MySQL
结果：MySQL瞬间压力暴增，可能宕机
```

**解决方案**：

**方案一：互斥锁**
```java
public Product getProduct(Long id) {
    String key = "product:" + id;
    Product product = redis.get(key);
    if (product != null) return product;

    // 只有第一个请求能拿到锁，去查数据库
    String lockKey = "lock:product:" + id;
    if (redis.setnx(lockKey, "1", 10)) {  // 设置10秒过期，防死锁
        try {
            product = db.findById(id);
            redis.setex(key, 3600, product);
        } finally {
            redis.del(lockKey);
        }
    } else {
        // 没拿到锁的请求等待100ms后重试
        Thread.sleep(100);
        return getProduct(id);  // 重试
    }
    return product;
}
```

**方案二：永不过期**
热点key不设TTL，通过异步任务更新数据。

### 69.4.3 缓存雪崩

**问题**：**大量key在同一时间过期**，或者Redis服务宕机，导致所有请求打到数据库。

```
场景一：大批缓存设置了相同的TTL，同时过期 → 瞬间大量请求穿透
场景二：Redis宕机 → 所有请求直接打到MySQL → MySQL也宕机
```

**解决方案**：

**方案一：TTL加随机值**
```java
// 基础TTL 3600秒，加0~600秒的随机值，避免同时过期
int ttl = 3600 + new Random().nextInt(600);
redis.setex(key, ttl, value);
```

**方案二：Redis高可用（哨兵/集群）**
搭建Redis Sentinel（哨兵）或Redis Cluster（集群），主节点挂了自动切换到从节点。

**方案三：本地缓存+限流**
在应用层加一道Caffeine（本地缓存）+ 限流（Sentinel/Guava RateLimiter），即使Redis全挂也不会瞬间压垮数据库。

---

## 69.5 Pipeline：批量操作

每次Redis命令都是一次网络往返（RTT，Round Trip Time）。当需要执行大量命令时，网络延迟累计起来非常可观。

```java
// ❌ 慢：每条命令一次网络往返
for (int i = 0; i < 1000; i++) {
    redis.set("key:" + i, "value:" + i);
}
// 1000次命令 = 1000次网络往返

// ✅ 快：Pipeline打包发送
Pipeline pipeline = jedis.pipelined();
for (int i = 0; i < 1000; i++) {
    pipeline.set("key:" + i, "value:" + i);
}
pipeline.sync();
// 1次网络往返
```

性能差距：1000次命令，不用Pipeline可能耗时500ms，用Pipeline可能只要10ms——**50倍差距**。

---

## 本章小结

| 概念 | 要点 |
|------|------|
| RDB | 时间点快照，文件小恢复快，但可能丢数据 |
| AOF | 追加写命令日志，数据更安全，everysec最多丢1秒 |
| 过期策略 | 惰性删除+定期删除组合 |
| 内存淘汰 | noeviction最危险，缓存推荐allkeys-lru |
| 缓存穿透 | 查不存在的数据穿透到DB，解决：缓存空值+布隆过滤器 |
| 缓存击穿 | 热点key过期瞬间大量请求打DB，解决：互斥锁 |
| 缓存雪崩 | 大量key同时过期或Redis宕机，解决：TTL加随机+高可用 |
| Pipeline | 批量打包命令，减少网络往返 |

---

## 自测题

1. **RDB和AOF的区别是什么？生产环境中应该怎么配置持久化？**

2. **什么是缓存穿透、缓存击穿、缓存雪崩？各举一个解决方案。**

3. **Redis内存满后 `maxmemory-policy` 设为 `noeviction` 会发生什么？为什么生产环境不能这么设？**

<details>
<summary>参考答案（做完再看）</summary>

1. RDB是定时快照，把某个时间点的内存数据保存为二进制文件，文件小恢复快但可能丢几分钟数据。AOF是追加写命令日志，数据更安全（最多丢1秒），但文件大恢复慢。生产环境建议同时开启两者：AOF保证数据安全（appendfsync everysec），RDB做冷备份。

2. 缓存穿透：查询不存在的数据，缓存和DB都没有，大量请求穿透到DB。解决：缓存空值或使用布隆过滤器。缓存击穿：热点key过期瞬间，大量并发请求同时查DB。解决：互斥锁（SETNX）控制只有一个请求查DB。缓存雪崩：大量key同时过期或Redis宕机。解决：TTL加随机值+Redis集群高可用+本地缓存做降级。

3. noeviction策略下，内存满后所有写操作都会被拒绝并返回错误。从业务角度看，这意味着用户的所有"写"操作（收藏、下单、更新资料等）全部失败——系统等于瘫痪。生产环境的缓存场景应使用allkeys-lru，让Redis自动淘汰不常用的数据，保证新的写入能成功。
</details>