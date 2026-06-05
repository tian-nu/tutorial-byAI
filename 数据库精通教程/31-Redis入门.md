# 31 — Redis 入门：数据结构

> - 对应文档版本：本篇为数据库精通教程第七篇第 2 章
> - 适用环境：Redis 7.0+，redis-cli 命令行工具
> - 读者角色：已学完第 1-2 篇 MySQL 基础，首次接触 NoSQL 的开发者
> - 预计耗时：新手 90 分钟 / 熟手 40 分钟
> - 前置教程：第 1-2 篇（MySQL 基础）
> - 可视化：无

---

## 本章假设你已掌握 MySQL 基础（第 1-5 篇）

---

## 从 MySQL 到 Redis 的思维转换

在 MySQL 里，你的世界是这样的：
- 有数据库（Database）
- 数据库里有表（Table）
- 表有行（Row）和列（Column）
- 每行数据按 Schema 定义好的字段存储

现在闭上眼睛，忘掉这一切。Redis 的世界完全不同：

```
MySQL 思维：
  Database → Table →  Row（id=1, name="张三", age=25）
  "我要查 id=1 的用户名"

Redis 思维：
  Key → Value
  "user:1:name" → "张三"
  "user:1:age" → "25"
  "我要查 user:1:name 这个 key"
```

**Redis 没有表结构**。它就像一个"超大内存字典"——你给一个 key，它返回一个 value。key 是什么你自己定，value 可以是字符串、列表、哈希、集合……所以 Redis 的全称是 **REmote DIctionary Server**（远程字典服务）。

**一句话定位**：MySQL 是磁盘上的"表格仓库"，Redis 是内存里的"数据结构工具箱"。

---

## 我在做什么？

上一章你对比了 MySQL 和 PostgreSQL，现在你走进 NoSQL 的世界。第一个要认识的，就是 NoSQL 里最不像数据库的数据库——Redis。

这一章你只做一件事：**把 Redis 的五种核心数据结构全部玩一遍**。不聊集群、不聊持久化、不聊缓存策略——那些是下一章的事。这一章就是让你"上手感受"这种和 MySQL 完全不同的数据模型。

学完这一章，你能在 `redis-cli` 里熟练操作 String、Hash、List、Set、Sorted Set，并且知道每种结构适合什么场景。

---

## 一、Redis 是什么？

**Redis（Remote Dictionary Server）** *此术语见附录E* 是一个开源的、基于内存的键值存储系统，同时也是一个"数据结构服务器"。

三个关键事实：
1. **数据在内存中**：所以极快（单机 10 万 QPS 是家常便饭）
2. **支持持久化**：虽然主要在内存，但可以定期存到磁盘（下一章细讲）
3. **不仅是 key-value**：value 可以是 String、Hash、List、Set、Sorted Set 等复杂结构

**比喻**：Redis 就像你办公桌上的便签本——随手记、随手看、极快，但如果你不抄到本子上（持久化），停电就没了。

---

## 二、安装 Redis

```bash
# Windows：推荐用 WSL 或 Docker
docker run --name redis-local -p 6379:6379 -d redis:7

# 或者用 Memurai（Windows 原生 Redis 兼容替代品）
# 下载：https://www.memurai.com/

# macOS
brew install redis
brew services start redis

# Linux (Ubuntu/Debian)
sudo apt update && sudo apt install redis
sudo systemctl start redis
```

验证安装：
```bash
# 启动 redis-cli
redis-cli

# 在 redis-cli 中执行
127.0.0.1:6379> PING
PONG    # ← 看到 PONG 就说明 Redis 在运行

# 如果通过 Docker，用：
docker exec -it redis-local redis-cli
```

---

## 三、String：最基础的类型

**String** *此术语见附录E* 是 Redis 中最简单的类型——一个 key 对应一个字符串。但"简单"不代表"没用"——String 是缓存、计数器、分布式锁的基石。

```bash
# === 基础操作 ===
SET user:1:name "张三"       # 设置 key=user:1:name, value=张三
GET user:1:name              # "张三"
SET user:1:age 25            # 数字也是存成字符串
GET user:1:age               # "25"（注意：返回的是字符串）

# === 自增/自减（计数器） ===
SET page:home:visits 0
INCR page:home:visits        # 1（原子操作，不用担心并发）
INCR page:home:visits        # 2
INCRBY page:home:visits 10   # 12（一次加 10）
DECR page:home:visits        # 11
DECRBY page:home:visits 3    # 8

# === 带过期时间的 SET（缓存用法） ===
SETEX session:token:abc123 3600 "user_id=42"   # 3600 秒后自动删除
TTL session:token:abc123     # 查看剩余过期时间（秒），返回 3587
TTL user:1:name              # -1 表示没有设置过期时间（永不过期）

# === SET NX：只在 key 不存在时设置（分布式锁基础） ===
SETNX lock:order:123 "locked"    # 返回 1（成功）
SETNX lock:order:123 "locked"    # 返回 0（key 已存在，设置失败）
# Redis 2.6.12+ 推荐写法：
SET lock:order:123 "locked" NX EX 10  # 原子操作：设置 + 过期时间

# === 获取并设置（GETSET） ===
SET counter 100
GETSET counter 200           # 返回旧值 "100"，然后设置新值 200
GET counter                  # "200"

# === 批量操作 ===
MSET user:1:name "张三" user:1:age 25 user:1:city "北京"
MGET user:1:name user:1:age user:1:city
# 1) "张三"
# 2) "25"
# 3) "北京"
```

**String 典型场景**：
| 场景 | 命令 | 示例 |
|------|------|------|
| 缓存 | `SETEX key ttl value` | 缓存用户信息，30 分钟过期 |
| 计数器 | `INCR key` | 文章阅读量、点赞数 |
| 分布式锁 | `SET key value NX EX 10` | 防止重复提交 |
| 限流 | `INCR + EXPIRE` | 1 分钟内最多请求 100 次 |

---

## 四、Hash：存储对象

**Hash** *此术语见附录E* 是一个 key 下存储多个 field-value 对。你可以在心里把它映射为"一个 key 对应一个小型字典"。

```bash
# === 基础操作 ===
HSET user:1 name "张三" age 25 city "北京"
HGET user:1 name             # "张三"
HGET user:1 age              # "25"
HGETALL user:1               # 返回所有 field-value
# 1) "name"
# 2) "张三"
# 3) "age"
# 4) "25"
# 5) "city"
# 6) "北京"

# === 字段级别的操作 ===
HEXISTS user:1 email         # 0（字段不存在）
HSET user:1 email "zhangsan@example.com"
HEXISTS user:1 email         # 1

HDEL user:1 city             # 删除单个字段
HGETALL user:1               # city 已经没了

# === 批量获取 ===
HMGET user:1 name age        # 1) "张三" 2) "25"

# === 数值操作 ===
HINCRBY user:1 age 1         # 26（年龄 +1）
HINCRBYFLOAT user:1 balance 9.99  # 浮点数自增

# === 只获取字段名或字段值 ===
HKEYS user:1                 # 1) "name" 2) "age" 3) "email" 4) "balance"
HVALS user:1                 # 1) "张三" 2) "26" 3) "zhangsan@example.com" 4) "9.99"
HLEN user:1                  # 4（字段数量）
```

**Hash vs MySQL 的思维映射**：

```
MySQL 表 users：
| id | name | age | city |
|----|------|-----|------|
| 1  | 张三 | 25  | 北京 |

Redis Hash：
key = "user:1"
  field: "name" → "张三"
  field: "age"  → "25"
  field: "city" → "北京"
```

**Hash 典型场景**：
- 用户信息存储（每个用户一个 Hash）
- 配置项（一个 Hash 存所有配置）
- 购物车（用户 ID 为 key，商品 ID 为 field，数量为 value）

---

## 五、List：有序列表

**List** *此术语见附录E* 是一个有序的字符串列表，支持从两端推入/弹出。Redis 的 List 底层是**双向链表**，所以两端操作都是 O(1)。

```bash
# === 从右端推入（RPUSH）和左端推入（LPUSH） ===
RPUSH queue:tasks "任务1" "任务2" "任务3"   # 从右边推入
# 列表状态：["任务1", "任务2", "任务3"]

LPUSH queue:tasks "任务0"                   # 从左边推入
# 列表状态：["任务0", "任务1", "任务2", "任务3"]

# === 弹出（POP） ===
LPOP queue:tasks             # "任务0"（从左边弹出）
RPOP queue:tasks             # "任务3"（从右边弹出）

# === 查看列表（不弹出） ===
LRANGE queue:tasks 0 -1      # 查看所有元素
# 1) "任务1"
# 2) "任务2"

# === 长度 ===
LLEN queue:tasks             # 2

# === 按索引获取 ===
LINDEX queue:tasks 0         # "任务1"（第 0 个元素）
LINDEX queue:tasks 1         # "任务2"

# === 阻塞弹出（BRPOP/BLPOP）：消息队列的核心 ===
# 终端 1（消费者）：等待新任务
BRPOP queue:tasks 0          # 0 = 无限等待，直到有数据
# 此时会阻塞...

# 终端 2（生产者）：推入一个任务
RPUSH queue:tasks "紧急任务"
# 终端 1 立刻返回：
# 1) "queue:tasks"
# 2) "紧急任务"

# === 修剪列表（保留最近的 N 条） ===
RPUSH news:latest "新闻1" "新闻2" "新闻3" "新闻4" "新闻5"
LTRIM news:latest 0 2        # 只保留前 3 条（索引 0-2）
LRANGE news:latest 0 -1
# 1) "新闻1" 2) "新闻2" 3) "新闻3"
```

**Queue 模式 vs Stack 模式**：
```
队列（Queue：FIFO 先进先出）：
  LPUSH + RPOP  →  左边进，右边出
  RPUSH + LPOP  →  右边进，左边出

栈（Stack：LIFO 后进先出）：
  LPUSH + LPOP  →  左边进，左边出
  RPUSH + RPOP  →  右边进，右边出
```

**List 典型场景**：
| 场景 | 命令组合 | 说明 |
|------|---------|------|
| 消息队列 | `RPUSH` + `BLPOP` | 生产者推入，消费者阻塞等待 |
| 最新列表 | `LPUSH` + `LTRIM` | 保留最新 N 条（如微博时间线） |
| 栈 | `LPUSH` + `LPOP` | 后进先出 |

---

## 六、Set：无序集合

**Set** *此术语见附录E* 是 Redis 的无序去重集合。它的核心价值在于**集合运算**——交集、并集、差集。

```bash
# === 基础操作 ===
SADD tags:article:1 "Redis" "数据库" "NoSQL"
SADD tags:article:2 "MySQL" "数据库" "SQL"
SADD tags:article:3 "Redis" "缓存" "NoSQL"

SMEMBERS tags:article:1     # 查看所有成员
# 1) "Redis" 2) "数据库" 3) "NoSQL"（顺序可能不同，Set 是无序的）

SISMEMBER tags:article:1 "Redis"   # 1（是成员）
SISMEMBER tags:article:1 "Python"  # 0（不是成员）

SCARD tags:article:1        # 3（集合大小）
SREM tags:article:1 "NoSQL" # 移除一个成员

# === 集合运算（这才是 Set 的核心价值） ===

# 交集：文章 1 和文章 2 的共同标签
SINTER tags:article:1 tags:article:2
# 1) "数据库"

# 并集：文章 1 和文章 2 的所有标签
SUNION tags:article:1 tags:article:2
# 1) "Redis" 2) "数据库" 3) "NoSQL" 4) "MySQL" 5) "SQL"

# 差集：文章 1 有但文章 2 没有的标签
SDIFF tags:article:1 tags:article:2
# 1) "Redis" 2) "NoSQL"

# === 随机弹出（抽奖场景） ===
SADD lottery:users "user1" "user2" "user3" "user4" "user5"
SPOP lottery:users          # 随机弹出一个（如 "user3"）
SPOP lottery:users 2        # 随机弹出 2 个

# === 随机获取但不删除 ===
SRANDMEMBER lottery:users 2 # 随机取 2 个，不删除
```

**Set 典型场景**：
| 场景 | 命令 | 示例 |
|------|------|------|
| 标签系统 | `SADD`, `SINTER` | 文章标签，找共同标签 |
| 共同好友 | `SINTER` | 用户 A 和用户 B 的共同好友 |
| 去重 | `SADD` | 独立访客（UV）统计 |
| 抽奖 | `SPOP`, `SRANDMEMBER` | 随机抽取中奖用户 |
| 关注列表 | `SADD`, `SISMEMBER` | 关注/取关 |

---

## 七、Sorted Set：有序集合

**Sorted Set（ZSet）** *此术语见附录E* 是 Redis 中最强大的数据结构之一。它在 Set 的基础上给每个成员加了一个**分数（score）**，按分数自动排序。

```bash
# === 基础操作 ===
ZADD leaderboard 100 "玩家A" 85 "玩家B" 92 "玩家C" 78 "玩家D"
# ZADD key score member [score member ...]

# === 按分数升序查看 ===
ZRANGE leaderboard 0 -1 WITHSCORES
# 1) "玩家D"  2) "78"
# 3) "玩家B"  4) "85"
# 5) "玩家C"  6) "92"
# 7) "玩家A"  8) "100"

# === 按分数降序查看（排行榜） ===
ZREVRANGE leaderboard 0 -1 WITHSCORES
# 1) "玩家A"  2) "100"
# 3) "玩家C"  4) "92"
# 5) "玩家B"  6) "85"
# 7) "玩家D"  8) "78"

# === 获取排名 ===
ZRANK leaderboard "玩家A"           # 3（升序排第几，从 0 开始）
ZREVRANK leaderboard "玩家A"        # 0（降序排第几，从 0 开始）

# === 按分数范围查询 ===
ZRANGEBYSCORE leaderboard 80 95 WITHSCORES
# 1) "玩家B" 2) "85" 3) "玩家C" 4) "92"

# === 更新分数（排行榜更新） ===
ZINCRBY leaderboard 10 "玩家B"      # 玩家 B 分数 +10，变成 95
ZREVRANK leaderboard "玩家B"        # 排名上升到第 2

# === 获取分数 ===
ZSCORE leaderboard "玩家A"           # "100"

# === 删除 ===
ZREM leaderboard "玩家D"            # 移除玩家 D

# === 按排名删除（保留前 3 名） ===
ZREMRANGEBYRANK leaderboard 0 -4    # 删除排名 0 到 -4（即除了前 3 名）
# 等价于保留前 3 名

# === 延迟队列（用时间戳作为 score） ===
ZADD delay_queue 1700000000 "task1"   # 1700000000 = 某个时间戳
ZADD delay_queue 1700000100 "task2"
ZADD delay_queue 1700000200 "task3"

-- 获取当前时间之前到期的任务
ZRANGEBYSCORE delay_queue 0 1700000050
# 返回 task1（时间戳 < 1700000050）
```

**Sorted Set 典型场景**：
| 场景 | 命令 | 示例 |
|------|------|------|
| 排行榜 | `ZADD`, `ZREVRANGE` | 游戏分数排行、文章热度排行 |
| 延迟队列 | `ZADD`（时间戳为 score），`ZRANGEBYSCORE` | 定时任务 |
| 带权重的集合 | `ZADD`（权重为 score） | 搜索热词权重 |
| 时间线（按时间排序） | 时间戳为 score | 最新消息流 |

---

## 八、通用命令：所有类型都能用

这些命令不挑数据类型，是所有 key 都能用的。

```bash
# === 查看 key 是否存在 ===
EXISTS user:1:name          # 1（存在）
EXISTS user:999:name        # 0（不存在）

# === 删除 key ===
DEL user:1:name             # 1（删除成功）
DEL user:999:name           # 0（key 不存在）

# === 查看 key 的类型 ===
TYPE user:1                 # hash
TYPE leaderboard            # zset
TYPE queue:tasks            # list
TYPE tags:article:1         # set
TYPE user:1:name            # string（如果还存在的话）

# === 设置过期时间 ===
EXPIRE user:1:name 60       # 60 秒后过期
TTL user:1:name             # 剩余秒数
PERSIST user:1:name         # 移除过期时间，变永不过期

# === 重命名 ===
RENAME old_key new_key      # 重命名
RENAMENX old_key new_key    # 仅在 new_key 不存在时重命名

# === 随机 key ===
RANDOMKEY                   # 随机返回一个 key

# ⚠️ KEYS：生产环境禁止使用！ ===
KEYS user:*                 # 返回所有匹配 user: 开头的 key
# 为什么禁用？KEYS 会阻塞 Redis，遍历所有 key，如果 key 有几百万个，Redis 会卡住几秒甚至更久
# 正确做法：用 SCAN（后面讲）
```

---

## 九、SCAN：安全的 key 遍历

```bash
# SCAN cursor [MATCH pattern] [COUNT count]
# 游标从 0 开始，返回 (新游标, 匹配的 key 列表)

SCAN 0 MATCH user:* COUNT 10
# 1) "15"  ← 下一次扫描的游标
# 2) 1) "user:1:name"
#    2) "user:1:age"
#    3) "user:3:name"

SCAN 15 MATCH user:* COUNT 10
# 1) "0"   ← 游标为 0 表示扫描完成
# 2) 1) "user:5:name"
#    2) "user:2:city"
```

**想多一点**：为什么 KEYS 这么危险 Redis 还保留它？因为它在调试场景下确实方便，而且早期 Redis 没有 SCAN。现在所有生产环境都应该用 `SCAN` 代替 `KEYS`。如果你在代码审查中看到 `KEYS`，直接标记为阻塞。

---

## 十、验证方法

### 实验：在 redis-cli 中完成一个完整的"排行榜系统"

```bash
# 1. 添加玩家分数
ZADD game:rank 1000 "player:A"
ZADD game:rank 850 "player:B"
ZADD game:rank 920 "player:C"
ZADD game:rank 780 "player:D"
ZADD game:rank 990 "player:E"

# 2. 查看排行榜（前 3 名）
ZREVRANGE game:rank 0 2 WITHSCORES

# 3. 玩家 B 完成一局，加 50 分
ZINCRBY game:rank 50 "player:B"

# 4. 查玩家 B 新排名
ZREVRANK game:rank "player:B"
ZSCORE game:rank "player:B"

# 5. 验证数据类型
TYPE game:rank               # 应该返回 zset
```

如果你能独立完成以上操作，并且理解每一步的含义，说明你已经掌握了 Redis 的基础数据结构。

---

## 十一、常见错误

### 错误 1：生产环境用 KEYS

**现象**：代码里写了 `KEYS user:*` 来获取所有用户 key，Redis 突然卡住，所有请求超时。

❌ **错误**：
```python
# Python redis 客户端
keys = redis_client.keys("user:*")  # 危险！
```

✅ **正确**：
```python
cursor = 0
while True:
    cursor, keys = redis_client.scan(cursor, match="user:*", count=100)
    for key in keys:
        # 处理 key
        pass
    if cursor == 0:
        break
```

### 错误 2：用 List 做队列但没做持久化

**现象**：用 `RPUSH` + `BLPOP` 做消息队列，Redis 重启后队列里的消息全部丢失。

**原因**：Redis 默认不持久化，List 里的数据在内存中，重启就没了。

✅ **解决**：如果消息不能丢，要么开启 RDB/AOF 持久化（下一章），要么用专门的消息队列（RabbitMQ、Kafka）。

### 错误 3：忘记设 EXPIRE

**现象**：缓存数据越来越多，Redis 内存满了，开始淘汰数据。

❌ **错误**：`SET user:1:data "..."`  —— 永不过期
✅ **正确**：`SETEX user:1:data 1800 "..."`  —— 30 分钟过期

> **经验法则**：所有缓存类数据，必须设过期时间。除非你明确知道它可以永久存在。

### 错误 4：Hash 存太多字段

**现象**：一个 Hash 存了 10 万个字段，`HGETALL` 时 Redis 阻塞。

✅ **解决**：Hash 单个 key 不宜超过数千个 field。如果数据量大，用 `HSCAN` 分批获取，或拆分成多个 Hash。

### 错误 5：把 Redis 当 MySQL 用

**现象**：在 Redis 里存大量数据，试图用 Redis 做复杂的条件查询。

❌ Redis 的设计哲学不是"通用查询"，它是"精确定位"——你知道 key 就能 O(1) 拿到数据。
✅ 如果你需要 `WHERE age > 25 AND city = '北京'`，请用 MySQL 或 PostgreSQL。Redis 是缓存和加速层，不是主数据库。

---

## 本章小结

| 本章学了什么 | 对应命令/概念 | 注意事项 |
|-------------|-------------|---------|
| Redis 思维转换 | 从表/行/列 → key/value | 没有 Schema，没有表结构 |
| String | `SET/GET/INCR/DECR/SETEX/SETNX` | 计数器、缓存、分布式锁 |
| Hash | `HSET/HGET/HGETALL/HINCRBY` | 存对象，单个 key 不宜超数千 field |
| List | `LPUSH/RPUSH/LPOP/RPOP/BRPOP` | 双向链表，做消息队列注意持久化 |
| Set | `SADD/SMEMBERS/SINTER/SUNION/SDIFF` | 去重、集合运算、共同好友 |
| Sorted Set | `ZADD/ZRANGE/ZREVRANGE/ZINCRBY` | 排行榜、延迟队列 |
| 通用命令 | `EXISTS/DEL/TYPE/EXPIRE/TTL` | 所有类型都能用 |
| KEYS 禁用 | 生产用 `SCAN` 代替 `KEYS` | KEYS 会阻塞 Redis！ |
| SCAN | `SCAN 0 MATCH pattern COUNT 100` | 游标遍历，安全不阻塞 |
| 过期时间 | `EXPIRE key seconds` | 缓存数据必须设过期时间 |

---

## 最可能出错的地方及原因

1. **生产环境用 KEYS**：从教程/调试直接复制到生产代码，原因是 KEYS 在开发环境很快（数据少），但生产环境几百万 key 时直接阻塞 Redis。
2. **忘记设过期时间**：缓存数据越来越多，内存爆满，原因是开发时数据量小不明显，上线后数据累积才发现问题。
3. **把 Redis 当主数据库**：试图在 Redis 里做复杂查询（如 `WHERE` 多条件过滤），原因是习惯了 MySQL 的思维模式，没理解 Redis 是"key-value 精确查找"模型。
4. **List 做消息队列不考虑持久化**：Redis 重启后消息丢失，原因是没意识到 Redis 默认是内存数据库，持久化需要额外配置。
5. **Hash 字段过多导致 HGETALL 阻塞**：单个 Hash 存储海量字段，HGETALL 时数据量大导致 Redis 单线程阻塞，原因是 Redis 是单线程处理命令的。