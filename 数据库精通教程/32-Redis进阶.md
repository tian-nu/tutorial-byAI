# 32 — Redis 进阶：缓存实战

> - 对应文档版本：本篇为数据库精通教程第七篇第 3 章
> - 适用环境：Redis 7.0+，redis-cli，应用层可用任意语言
> - 读者角色：已学完第 31 章 Redis 基础数据结构的开发者
> - 预计耗时：新手 90 分钟 / 熟手 45 分钟
> - 前置教程：第 31 章（Redis 入门）
> - 可视化：无

---

## 本章假设你已掌握 MySQL 基础（第 1-5 篇）

---

## 从 MySQL 到 Redis 进阶的思维转换

上一章你学会了 Redis 的五种数据结构，就像学会了螺丝刀、扳手、锤子的用法。但"会用工具"和"造出房子"是两回事。

这一章，我们不再纠结于命令本身，而是回答一个问题：**Redis 在真实项目中到底怎么用？**

你从 MySQL 的世界来，最自然的场景就是"用 Redis 给 MySQL 做缓存"。这看似简单，但实际坑非常多——数据什么时候更新？缓存和数据库不一致怎么办？Redis 内存满了怎么办？Redis 自己挂了怎么办？

这一章，我会把这些问题一个一个拆开，让你不仅会用 Redis，更知道**怎么用得对、用得稳**。

---

## 我在做什么？

上一章你学会了 Redis 的基本命令。这一章，我们把 Redis 放到真实项目的**缓存层**，解决三个核心问题：

1. **缓存怎么防穿透/击穿/雪崩**？（这三个词 90% 的面试都会问）
2. **缓存和数据库怎么保持一致性**？（这是分布式系统最经典的问题之一）
3. **Redis 自己怎么保证不丢数据**？（持久化 RDB/AOF + 集群入门）

学完这一章，你能画出"Cache Aside 模式"的时序图，能解释缓存穿透/击穿/雪崩的区别和解决方案，能在面试中从容应答"Redis 怎么保证缓存一致性"。

---

## 一、缓存三大坑：穿透、击穿、雪崩

这三个词经常被一起提起，但很多人分不清它们的区别。我们用"图书馆还书"来比喻，一次讲清楚。

### 1.1 缓存穿透（Cache Penetration）

**缓存穿透** *此术语见附录E* 是指：**查询一个数据库中根本不存在的 key，缓存和数据库都没有，每次请求都打到数据库上。**

```
比喻：你去图书馆问"有没有《火星种菜指南》这本书？"
  - 图书馆前台（缓存）说：没有
  - 然后你去书架（数据库）找：也没有
  - 下一个人又问，又去书架找一遍……
  - 如果恶意攻击者每分钟问 100 万次，书架管理员（数据库）就累死了
```

❌ **问题代码**：
```python
def get_user(user_id):
    # 查缓存
    user = cache.get(f"user:{user_id}")
    if user:
        return user
    
    # 查数据库
    user = db.query(f"SELECT * FROM users WHERE id = {user_id}")
    if user:
        cache.setex(f"user:{user_id}", 3600, user)  # 缓存 1 小时
    return user
    # 如果 user_id 不存在，每次请求都穿透到数据库！
```

✅ **解决方案一：缓存空值**
```python
def get_user(user_id):
    user = cache.get(f"user:{user_id}")
    if user is not None:
        return user if user != "NULL" else None  # 缓存了空值
    
    user = db.query(f"SELECT * FROM users WHERE id = {user_id}")
    if user:
        cache.setex(f"user:{user_id}", 3600, user)
    else:
        # 缓存空值，但过期时间短一些（防止缓存大量空值占用内存）
        cache.setex(f"user:{user_id}", 60, "NULL")
    return user
```

✅ **解决方案二：布隆过滤器**
**布隆过滤器（Bloom Filter）** *此术语见附录E* 是一个神奇的数据结构：

```
布隆过滤器可以告诉你两件事：
  - "这个 key 一定不存在"（100% 准确）
  - "这个 key 可能存在"（有误判率，但可控）

流程变为：
  请求 → 布隆过滤器 → "不存在" → 直接返回（不查数据库）
                    → "可能存在" → 查缓存 → 查数据库
```

```python
# 使用 Redis 布隆过滤器模块（RedisBloom）
# docker run -p 6379:6379 redislabs/rebloom:latest

# 初始化布隆过滤器
BF.RESERVE user_filter 0.01 1000000  # 误判率 1%，预期 100 万元素

# 添加存在的用户 ID
BF.ADD user_filter 1
BF.ADD user_filter 2
BF.MADD user_filter 3 4 5

# 查询
BF.EXISTS user_filter 1    # 1（可能存在）
BF.EXISTS user_filter 999  # 0（一定不存在）
```

### 1.2 缓存击穿（Cache Breakdown）

**缓存击穿** *此术语见附录E* 是指：**一个热点 key 在过期瞬间，大量请求同时打到数据库上。**

```
比喻：图书馆里《三体》是热门书，只有一本（热点 key）。
  - 这本书被借走了（key 过期），所有想看的人都涌到书架前（数据库）
  - 瞬间涌入 1000 人，书架管理员（数据库）崩溃
```

**穿透 vs 击穿的区别**：
- 穿透：查的 key 从来不存在（数据库里也没有）
- 击穿：查的 key 存在，但缓存刚好过期了

✅ **解决方案一：互斥锁（Mutex Lock）**
```python
import redis
import time

r = redis.Redis()

def get_hot_data(key):
    # 1. 先查缓存
    data = r.get(key)
    if data:
        return data
    
    # 2. 缓存没有，尝试获取锁
    lock_key = f"lock:{key}"
    if r.setnx(lock_key, "1"):
        # 3. 拿到锁，设置过期时间，查数据库，更新缓存
        r.expire(lock_key, 10)  # 锁 10 秒过期，防止死锁
        
        # 双重检查：可能别的线程已经更新了缓存
        data = r.get(key)
        if data:
            r.delete(lock_key)
            return data
        
        data = db_query(key)  # 查数据库
        r.setex(key, 3600, data)
        r.delete(lock_key)    # 释放锁
        return data
    else:
        # 4. 没拿到锁，等一会儿再查缓存
        time.sleep(0.1)
        return r.get(key) or get_hot_data(key)  # 重试
```

✅ **解决方案二：逻辑过期（永不过期 + 异步更新）**
```python
def get_hot_data_v2(key):
    data = r.get(key)
    if data is None:
        # 缓存完全没有，加载
        data = db_query(key)
        r.set(key, data)  # 不设过期时间
        return data
    
    # 检查逻辑过期时间（应用程序自己维护的）
    expire_time = r.get(f"{key}:expire")
    if expire_time and time.time() > float(expire_time):
        # 已逻辑过期，尝试获取锁去异步更新
        if r.setnx(f"lock:{key}", "1"):
            # 异步更新缓存
            thread_pool.submit(refresh_cache, key)
            r.expire(f"lock:{key}", 10)
    
    return data  # 返回旧数据（保证可用性）
```

### 1.3 缓存雪崩（Cache Avalanche）

**缓存雪崩** *此术语见附录E* 是指：**大量 key 在同一时间过期，或 Redis 宕机，导致所有请求直接打到数据库，数据库瞬间崩溃。**

```
比喻：图书馆每天晚上 12 点把所有热门书都收走（统一过期时间）。
  第二天早上 8 点开门，所有人同时涌进来借书，书架管理员（数据库）直接崩溃。
```

✅ **解决方案一：随机过期时间**
```python
import random

# ❌ 错误：所有 key 同一时间过期
cache.setex(f"user:{user_id}", 3600, data)  # 全部 1 小时

# ✅ 正确：加上随机偏差
base_ttl = 3600
random_ttl = random.randint(0, 600)  # 0-10 分钟随机
cache.setex(f"user:{user_id}", base_ttl + random_ttl, data)
```

✅ **解决方案二：多级缓存**

```
请求 → 本地缓存（Caffeine/Guava，毫秒级）
         ↓ 未命中
       Redis 集群（内存，毫秒级）
         ↓ 未命中
       MySQL（磁盘，百毫秒级）
```

每一层缓存都兜底，避免雪崩传导到数据库。

✅ **解决方案三：Redis 高可用**
- 主从复制 + 哨兵（Sentinel）：自动故障切换
- Redis Cluster：数据分片 + 高可用
- 限流降级：数据库压力过大时，直接返回默认值或错误，保证不崩溃

### 1.4 三者对比（防止混淆）

| 维度 | 缓存穿透 | 缓存击穿 | 缓存雪崩 |
|------|---------|---------|---------|
| **原因** | 查询不存在的数据 | 热点 key 过期 | 大量 key 同时过期 / Redis 宕机 |
| **现象** | 每次请求都打到 DB | 过期瞬间大量请求打 DB | 大量请求同时打 DB |
| **数据库压力** | 持续高 | 瞬间高 | 瞬间极高 |
| **缓存中是否有数据** | 从来没有 | 刚好过期 | 大量同时过期 |
| **核心解决方案** | 缓存空值 / 布隆过滤器 | 互斥锁 / 逻辑过期 | 随机过期时间 / 多级缓存 |
| **一句话区别** | 查"不存在"的数据 | 查"刚好过期"的热点数据 | 查"大面积过期"的数据 |

---

## 二、过期策略：Redis 怎么删除过期 key？

你设了 `EXPIRE key 60`，Redis 怎么在 60 秒后删除它？不是"到了 60 秒就删"这么简单。

### 2.1 惰性删除（Lazy Deletion）

访问 key 时，先检查是否过期，过期就删除。

```
优点：对 CPU 友好（不主动扫描）
缺点：过期 key 如果没人访问，会一直占着内存
```

### 2.2 定期删除（Periodic Deletion）

Redis 每秒执行 10 次（默认 `hz=10`）的定期任务，随机抽取一批 key 检查过期时间并删除。

```
优点：清理过期 key，释放内存
缺点：不能一次性扫太多（CPU 开销）
```

**Redis 的过期策略 = 惰性删除 + 定期删除**，两者配合，平衡 CPU 和内存。

---

## 三、内存淘汰策略：内存满了怎么办？

`maxmemory` 设置了 Redis 最大可用内存。当内存满了，又有新写入请求时，Redis 怎么办？

```bash
# 查看当前淘汰策略
CONFIG GET maxmemory-policy

# 设置淘汰策略
CONFIG SET maxmemory-policy allkeys-lru
```

Redis 提供了 8 种淘汰策略：

| 策略 | 含义 | 适用场景 |
|------|------|---------|
| `noeviction` | 不淘汰，写入报错 | 数据不能丢的场景（默认） |
| `allkeys-lru` | 所有 key 中淘汰最久未使用的 | **通用缓存，推荐** |
| `allkeys-lfu` | 所有 key 中淘汰使用频率最低的 | 访问频率差异大 |
| `allkeys-random` | 所有 key 中随机淘汰 | 访问模式均匀 |
| `volatile-lru` | 有过期时间的 key 中淘汰 LRU | 缓存和永久数据混合 |
| `volatile-lfu` | 有过期时间的 key 中淘汰 LFU | 同上 |
| `volatile-random` | 有过期时间的 key 中随机淘汰 | 同上 |
| `volatile-ttl` | 有过期时间的 key 中淘汰 TTL 最短的 | 希望尽量保留"长期"数据 |

**LRU（Least Recently Used）**：最久没被访问的先淘汰
**LFU（Least Frequently Used）**：访问次数最少的先淘汰

```bash
# 设置最大内存和淘汰策略
CONFIG SET maxmemory 256mb
CONFIG SET maxmemory-policy allkeys-lru
```

**想多一点**：`noeviction` 是默认策略，但**生产环境不建议用默认**。如果你的 Redis 主要做缓存，一定要改成 `allkeys-lru`。否则内存满了客户端直接报错，用户体验极差。

---

## 四、持久化：RDB vs AOF

Redis 是内存数据库，重启数据就没了。持久化就是"把内存数据写到磁盘"。

### 4.1 RDB（快照）

**RDB（Redis Database）** *此术语见附录E* 是**全量快照**——到某个时间点，把整个 Redis 内存数据拍一张"照片"存到磁盘。

```
save 900 1     # 900 秒内至少 1 次修改，触发 RDB
save 300 10    # 300 秒内至少 10 次修改
save 60 10000  # 60 秒内至少 10000 次修改
```

| 优点 | 缺点 |
|------|------|
| 文件紧凑，适合备份 | 两次快照之间的数据可能丢失 |
| 恢复速度快（直接加载） | 大数据量时 fork 子进程会阻塞 |
| 对性能影响小（子进程写） | 不适合实时性要求高的场景 |

```bash
# 手动触发 RDB
SAVE       # 主线程阻塞（不推荐生产用）
BGSAVE     # 后台异步快照（推荐）

# 查看上次快照时间
LASTSAVE
```

### 4.2 AOF（追加日志）

**AOF（Append Only File）** *此术语见附录E* 是**增量日志**——每次写操作都追加到日志文件末尾，重启时"重放"日志恢复数据。

```bash
# 开启 AOF
CONFIG SET appendonly yes

# AOF 刷盘策略
# appendfsync always   # 每次写都刷盘（最安全，最慢）
# appendfsync everysec # 每秒刷一次（推荐，平衡安全与性能）
# appendfsync no       # 交给操作系统（最快，最不安全）
```

| 优点 | 缺点 |
|------|------|
| 数据安全性高（最多丢 1 秒） | AOF 文件比 RDB 大 |
| 支持自动重写（压缩） | 恢复速度比 RDB 慢 |
| 可读（文本格式，可手动修改） | 写 QPS 高时性能压力大 |

### 4.3 RDB + AOF 混合持久化（Redis 4.0+）

```
混合持久化流程：
  AOF 重写时，前半部分是 RDB 格式的快照，后半部分是 AOF 增量日志
  → 既有 RDB 的恢复速度，又有 AOF 的数据安全性
```

```bash
CONFIG SET aof-use-rdb-preamble yes
```

### 4.4 选型建议

| 场景 | 推荐方案 |
|------|---------|
| 纯缓存（数据可重建） | 不需要持久化，`save ""` 关闭 |
| 缓存 + 少量持久数据 | RDB（性能好，能接受少量数据丢失） |
| 数据不能丢（如订单、积分） | AOF everysec（即使丢也只丢 1 秒） |
| 既要安全又要快 | 混合持久化（Redis 4.0+） |

---

## 五、集群入门：从单机到分布式

### 5.1 主从复制（Replication）

```bash
# 在从节点上执行
SLAVEOF master_ip master_port
# 或 Redis 5.0+ 用
REPLICAOF master_ip master_port

# 查看复制状态
INFO replication
```

```
主节点（Master）：处理读写
从节点（Slave）：复制主节点数据，只读
```

### 5.2 哨兵（Sentinel）

**哨兵（Sentinel）** *此术语见附录E* 是 Redis 的高可用方案：监控主节点，主节点挂了自动选举新的主节点。

```
Sentinel 做三件事：
  1. 监控（Monitoring）：持续检查主从节点是否健康
  2. 通知（Notification）：节点故障时通知管理员
  3. 自动故障转移（Automatic Failover）：主节点挂了，选新主节点
```

```bash
# sentinel.conf
sentinel monitor mymaster 127.0.0.1 6379 2  # 2 个哨兵同意才认为挂了
sentinel down-after-milliseconds mymaster 5000
sentinel failover-timeout mymaster 10000

# 启动哨兵
redis-sentinel sentinel.conf
```

### 5.3 Cluster（分片集群）

**Redis Cluster** *此术语见附录E* 是 Redis 的分布式方案：数据自动分片到多个节点，每个节点只存一部分数据。

```
Redis Cluster 核心概念：
  - 16384 个哈希槽（slot）
  - 每个 key 通过 CRC16(key) % 16384 计算属于哪个槽
  - 每个节点负责一部分槽
  - 支持主从（每个分片一个主 + 多个从）
```

```bash
# 创建 6 节点集群（3 主 3 从）
redis-cli --cluster create \
  127.0.0.1:7000 127.0.0.1:7001 127.0.0.1:7002 \
  127.0.0.1:7003 127.0.0.1:7004 127.0.0.1:7005 \
  --cluster-replicas 1

# 连接集群
redis-cli -c -p 7000

# 查看集群信息
CLUSTER INFO
CLUSTER NODES
```

---

## 六、缓存与数据库一致性：Cache Aside 模式

这是分布式系统中最经典的问题之一：**缓存和数据库的数据怎么保持一致？**

### 6.1 先更新数据库还是先删缓存？

| 方案 | 流程 | 问题 |
|------|------|------|
| 先删缓存，再更新数据库 | 删缓存 → 更新 DB | 更新 DB 前，另一个请求查 DB 的旧数据并写入缓存，造成缓存是旧数据 |
| 先更新数据库，再删缓存 | 更新 DB → 删缓存 | 删除缓存失败怎么办？查询到旧缓存（缓存未命中，查 DB 写缓存有极短窗口，概率极低） |

**结论：先更新数据库，再删缓存**（Cache Aside 模式）。

### 6.2 Cache Aside 模式

**Cache Aside** *此术语见附录E* 是缓存使用的最经典模式：

```
读操作：
  1. 查缓存
  2. 缓存命中 → 返回
  3. 缓存未命中 → 查数据库 → 写入缓存 → 返回

写操作：
  1. 更新数据库
  2. 删除缓存（不是更新缓存！）
```

**为什么是删缓存而不是更新缓存？**
- 更新缓存需要知道"最终值"，而写操作可能只更新了部分字段
- 删缓存更简单，下次读的时候自然会重建
- 避免并发写导致缓存与数据库不一致

```python
def update_user(user_id, new_name):
    # 1. 更新数据库
    db.execute("UPDATE users SET name = %s WHERE id = %s", (new_name, user_id))
    # 2. 删除缓存
    cache.delete(f"user:{user_id}")
    # 3. 下次读 user_id 时，缓存未命中，查数据库并写入缓存
```

### 6.3 延迟双删：加一道保险

如果"删缓存"这一步失败了怎么办？缓存里就一直是旧数据。

```python
def update_user_with_retry(user_id, new_name):
    # 1. 更新数据库
    db.execute("UPDATE users SET name = %s WHERE id = %s", (new_name, user_id))
    
    # 2. 删除缓存
    try:
        cache.delete(f"user:{user_id}")
    except Exception:
        # 3. 删除失败，发送消息到延迟队列，稍后重试
        delay_queue.send("delete_cache", f"user:{user_id}", delay=1)
    
    # 4. 延迟双删：等 500ms 后再删一次
    # （防止并发读将旧数据写回缓存）
    time.sleep(0.5)
    cache.delete(f"user:{user_id}")
```

### 6.4 Cache Aside 时序图

```
写操作：                          读操作：
  Client                              Client
    |                                    |
    |-- UPDATE users SET name='new' --> DB|
    |                                    |
    |-- DELETE cache:user:1 --> Cache     |
    |                                    |
    |                              (缓存未命中)
    |                                    |
    |                              |-- SELECT * FROM users --> DB
    |                              |  (查到新的 name='new')
    |                              |
    |                              |-- SET cache:user:1 --> Cache
    |                              |  (写入新数据)
```

---

## 七、验证方法

### 验证 1：能画 Cache Aside 时序图

拿张纸，画出"更新用户信息"的完整时序图，包括：
- 应用层
- Redis 缓存层
- MySQL 数据库层
- 标注每一步的箭头方向和数据流向

### 验证 2：穿透/击穿/雪崩区分

不看笔记，用自己的话解释：
- 什么是缓存穿透？怎样解决？
- 什么是缓存击穿？和穿透有什么区别？
- 什么是缓存雪崩？怎样预防？

### 验证 3：Redis 配置检查

```bash
# 检查当前 Redis 的持久化配置
redis-cli INFO persistence

# 检查内存淘汰策略
redis-cli CONFIG GET maxmemory-policy

# 检查过期 key 情况
redis-cli INFO stats | grep expired
```

---

## 八、常见错误

### 错误 1：先删缓存再更新数据库

**现象**：更新用户信息时，先 `DEL cache:user:1`，再 `UPDATE users ...`。在两次操作之间，另一个请求读了旧数据并写入了缓存。

❌ 缓存中永远是旧数据，直到下次更新。

✅ 正确顺序：先 `UPDATE users ...`，再 `DEL cache:user:1`。

### 错误 2：缓存所有数据不管内存

**现象**：所有查询结果都放缓存，Redis 内存爆满，触发淘汰策略后命中率暴跌。

✅ **解决**：
- 只缓存热点数据（20% 的数据贡献 80% 的请求）
- 设置合理的过期时间
- 监控内存使用：`INFO memory`

### 错误 3：只用 RDB 不做 AOF

**现象**：RDB 配置为 `save 900 1`（15 分钟），Redis 在第 14 分钟挂了，丢失 14 分钟的数据。

✅ **解决**：如果数据不能丢，开启 AOF `appendfsync everysec`，最多丢 1 秒。

### 错误 4：以为哨兵能解决所有问题

**现象**：Redis 主从 + 哨兵，数据量大了还是慢。

**原因**：哨兵解决的是**高可用**（自动故障切换），不是**性能扩展**。数据量大要用 Cluster 分片。

### 错误 5：缓存预热没做

**现象**：Redis 重启后缓存全空，大量请求直接打到数据库，数据库瞬间高压。

✅ **解决**：系统启动时预加载热点数据到缓存，或等缓存逐步"热"起来（但要防止首次请求雪崩）。

---

## 本章小结

| 本章学了什么 | 对应命令/概念 | 注意事项 |
|-------------|-------------|---------|
| 缓存穿透 | 查不存在的数据 → 缓存空值 / 布隆过滤器 | 穿透 ≠ 击穿，穿透是 key 从来不存在 |
| 缓存击穿 | 热点 key 过期 → 互斥锁 / 逻辑过期 | 击穿是热点 key 刚好过期 |
| 缓存雪崩 | 大量 key 同时过期 → 随机过期时间 / 多级缓存 | 加随机偏差是最简单有效的方案 |
| 过期策略 | 惰性删除 + 定期删除 | 不是精确的定时删除 |
| 内存淘汰策略 | `allkeys-lru`（推荐）/ `volatile-lru` 等 | 生产环境不要用默认 `noeviction` |
| RDB 持久化 | `BGSAVE`，快照，全量 | 恢复快，但可能丢数据 |
| AOF 持久化 | `appendfsync everysec`，增量日志 | 数据安全，但恢复慢 |
| 混合持久化 | Redis 4.0+ RDB + AOF | 推荐：兼顾安全与恢复速度 |
| 主从复制 | `REPLICAOF master_ip port` | 读写分离，数据冗余 |
| 哨兵 | Sentinel，监控 + 自动故障转移 | 解决高可用，不是性能 |
| Cluster | 分片集群，16384 个哈希槽 | 解决大数据量和高并发 |
| Cache Aside | 读：查缓存 → 查 DB → 写缓存；写：更新 DB → 删缓存 | 先更新 DB 再删缓存，不要反过来 |
| 延迟双删 | 删缓存 + 延迟重试 + 再次删除 | 防止删除失败导致不一致 |
| 缓存预热 | 启动时预加载热点数据 | 防止重启后雪崩 |

---

## 最可能出错的地方及原因

1. **穿透/击穿/雪崩概念混淆**：面试时最常见的错误——把击穿说成穿透，把雪崩说成击穿，原因是三个词听起来像但场景完全不同，记住"不存在/刚好过期/大面积过期"这个口诀。
2. **先删缓存再更新数据库**：缓存和数据库不一致的经典原因，正确的 Cache Aside 模式是先更新数据库再删缓存。
3. **生产环境用默认淘汰策略**：`noeviction` 是默认策略，内存满了直接报错，用户看到 500 错误，原因是部署时没检查 `maxmemory-policy`。
4. **只用 RDB 以为数据不会丢**：RDB 是定期快照，两次快照之间的数据可能丢失，如果数据不能丢必须加 AOF。
5. **哨兵和 Cluster 搞混**：哨兵解决的是"主节点挂了怎么办"（高可用），Cluster 解决的是"数据太大了单机存不下怎么办"（分片），两者解决的问题不同。