# 第68章 · Redis入门

> "MySQL是档案馆——存得久、查得准、容量大，但你每查一次都要走进去翻柜子（磁盘IO），少说几毫秒。Redis是你脑袋顶上的便签纸——伸手就能贴、抬头就能看，只需0.0001秒。用MySQL存储核心数据，用Redis给热点数据加速——后端开发的黄金搭档。"

---

## 68.1 Redis是什么

**Redis**（Remote Dictionary Server）是一个**基于内存**的键值存储数据库。它的核心特点就一个字：**快**。

| 特性 | 说明 |
|------|------|
| 基于内存 | 所有数据存在RAM中，读写速度是纳秒级 |
| 单线程 | 6.x之前命令处理是单线程的，但有I/O多线程 |
| 支持持久化 | 可以定期把内存数据保存到磁盘（RDB/AOF） |
| 丰富的数据类型 | 不止key-value，还有List、Set、Hash、Sorted Set、Stream等 |
| 内置功能 | 发布订阅、Lua脚本、事务、过期策略、Pipeline |

### Redis为什么快？

1. **纯内存操作**：没有磁盘IO，绝大部分命令的复杂度是O(1)或O(n)（n是集合大小，但全在内存中）
2. **单线程处理命令**：没有多线程的上下文切换和锁竞争开销
3. **IO多路复用**：一个线程同时监听多个连接，哪个有数据就处理哪个
4. **精心设计的数据结构**：不是简单的字符串拼接，是高度优化的C语言结构体

```
MySQL 单次查询：   1~50ms（磁盘IO）
Redis 单次操作：   0.01~0.1ms（纯内存）
性能差距：        100~5000 倍
```

---

## 68.2 安装Redis

### Windows安装（推荐用WSL或Docker）

Redis官方不直接支持Windows。推荐两种方案：

**方案一：WSL2（推荐）**

```bash
# 在WSL2的Ubuntu中
sudo apt update
sudo apt install redis-server -y
sudo systemctl start redis-server
redis-cli ping  # 返回 PONG 表示成功
```

**方案二：Docker**

```bash
docker run --name redis -p 6379:6379 -d redis:7-alpine
```

### macOS安装

```bash
brew install redis
brew services start redis
redis-cli ping
```

### Linux安装

```bash
sudo apt update
sudo apt install redis-server -y
sudo systemctl start redis-server
redis-cli ping
```

### 进入Redis命令行

```bash
redis-cli
```

看到 `127.0.0.1:6379>` 提示符，说明进入了Redis交互命令行。6379是Redis的默认端口（手机键盘上拼出"REDIS"就是6379）。

---

## 68.3 五大数据类型

Redis不是简单的key-value。它提供了五种核心数据类型，每种都有专门的命令。

### 68.3.1 String（字符串）

最基本也是最常用的类型。key是字符串，value也是。

```bash
# 基本操作
SET name "zhangsan"            # 设置
GET name                       # 获取 → "zhangsan"
SET name "lisi"                # 覆盖
GET name                       # → "lisi"
DEL name                       # 删除

# 数字操作（value是数字字符串时）
SET counter 100
INCR counter                   # 101（自增1）
INCRBY counter 50              # 151（自增指定值）
DECR counter                   # 150（自减1）

# 过期时间（TTL）
SET token "abc123" EX 3600     # 3600秒后自动删除
SETEX token 3600 "abc123"      # 同上
TTL token                      # 查看剩余秒数，-1表示永不过期，-2表示已过期

# 条件设置
SETNX lock "1"                 # 如果key不存在才设置（Set if Not eXists）
GET lock
```

**典型场景**：
- 缓存：JSON序列化后的对象、HTML片段
- 计数器：文章阅读数、点赞数
- 分布式锁：`SETNX lock:order:123 uuid EX 30`
- Session共享

### 68.3.2 Hash（哈希）

存储对象的字段-值对。类比Java的 `Map<String, Map<String, String>>`。

```bash
# 设置
HSET user:1001 username "zhangsan" email "zhangsan@qq.com" age "25"

# 获取单个字段
HGET user:1001 username         # "zhangsan"

# 获取所有字段和值
HGETALL user:1001               # username, zhangsan, email, zhangsan@qq.com, age, 25

# 获取所有字段名 / 所有值
HKEYS user:1001                 # username, email, age
HVALS user:1001                 # zhangsan, zhangsan@qq.com, 25

# 判断字段是否存在
HEXISTS user:1001 email         # 1 (存在)

# 删除字段
HDEL user:1001 age              # 删除age字段

# 数字操作
HINCRBY user:1001 age 1         # 26

# 获取所有字段数量
HLEN user:1001                  # 3
```

**典型场景**：存储对象（比String存JSON更节省空间，可以单独修改某个字段）

### 68.3.3 List（列表）

有序的字符串列表，类比Java的 `LinkedList`。可以左进左出、左进右出……非常灵活。

```bash
# 从左边插入
LPUSH queue "msg1" "msg2"       # 左侧依次压入，结果是 msg2, msg1

# 从右边插入
RPUSH queue "msg3"              # 右侧追加，结果是 msg2, msg1, msg3

# 范围查看（不会移除元素）
LRANGE queue 0 -1               # 查看全部：msg2, msg1, msg3
LRANGE queue 0 1                # 查看前2个：msg2, msg1

# 弹出（移除并返回）
LPOP queue                      # 左侧弹出 → "msg2"
RPOP queue                      # 右侧弹出 → "msg3"

# 获取长度
LLEN queue                      # 1

# 阻塞弹出（队列为空时等待）
BLPOP queue 10                  # 等待10秒，有数据就弹出；超时返回nil
BRPOP queue 10
```

**典型场景**：
- 消息队列（用 `LPUSH` + `BRPOP` 实现生产者消费者）
- 最新消息列表（`LPUSH` + `LTRIM` 保持固定长度）
- 分页列表

### 68.3.4 Set（集合）

无序、不重复的字符串集合，类比Java的 `HashSet`。

```bash
# 添加
SADD tags:article:1 "Java" "Spring" "Redis"
SADD tags:article:2 "Spring" "MySQL" "Docker"

# 查看所有成员
SMEMBERS tags:article:1          # Java, Spring, Redis（无序）

# 判断是否存在
SISMEMBER tags:article:1 "Java"  # 1 (存在)

# 获取集合大小
SCARD tags:article:1             # 3

# 差集：在1中但不在2中的
SDIFF tags:article:1 tags:article:2    # Java, Redis

# 交集：两个集合都有的
SINTER tags:article:1 tags:article:2   # Spring

# 并集：两个集合合并去重
SUNION tags:article:1 tags:article:2   # Java, Spring, Redis, MySQL, Docker

# 随机弹出
SPOP tags:article:1              # 随机弹出一个

# 随机获取不删除
SRANDMEMBER tags:article:1 2     # 随机取2个（不删除）
```

**典型场景**：
- 标签系统：`SINTER` 实现"同时包含Java和Redis标签的文章"
- 点赞/关注列表：`SADD`、`SREM`、`SISMEMBER`
- 共同好友：`SINTER user:1:friends user:2:friends`
- 抽奖：`SRANDMEMBER` 或 `SPOP`

### 68.3.5 Sorted Set（有序集合）

Set的升级版——每个成员有一个**分数（score）**，按分数排序。类比Java的 `TreeSet` + 权重。

```bash
# 添加（member + score）
ZADD leaderboard 100 "zhangsan"
ZADD leaderboard 95  "lisi"
ZADD leaderboard 88  "wangwu"
ZADD leaderboard 95  "zhaoliu"     # score可以重复，member唯一

# 按分数升序查看
ZRANGE leaderboard 0 -1            # wangwu(88), lisi(95), zhaoliu(95), zhangsan(100)

# 按分数降序查看（带分数）
ZREVRANGE leaderboard 0 -1 WITHSCORES
# zhangsan 100, zhaoliu 95, lisi 95, wangwu 88

# 获取排名（从0开始）
ZRANK leaderboard "zhangsan"       # 3（升序排名）
ZREVRANK leaderboard "zhangsan"    # 0（降序排名——第一名）

# 分数范围查询
ZRANGEBYSCORE leaderboard 90 100   # lisi, zhaoliu, zhangsan

# 获取成员的分数
ZSCORE leaderboard "zhangsan"      # "100"

# 增加分数
ZINCRBY leaderboard 5 "wangwu"     # wangwu 变成93分

# 移除成员
ZREM leaderboard "zhaoliu"

# 获取成员数
ZCARD leaderboard                  # 3

# 按排名范围获取
ZREVRANGE leaderboard 0 2          # 前三名：zhangsan, lisi, wangwu
```

**典型场景**：
- 排行榜：游戏积分、文章热度、销量排行
- 延时队列：score存时间戳，定时任务`ZRANGEBYSCORE`获取到期的任务
- 带权重的标签

---

## 68.4 通用命令

```bash
# 查找所有匹配的key（生产环境禁用！会阻塞Redis）
KEYS user:*                      # 🚨 数据量大时非常危险

# 迭代查找key（生产环境用这个）
SCAN 0 MATCH user:* COUNT 10     # 返回游标和一批key

# 判断key是否存在
EXISTS name                      # 1 (存在) 或 0 (不存在)

# 查看key的类型
TYPE name                        # string
TYPE leaderboard                 # zset

# 设置过期
EXPIRE name 60                   # 60秒后过期

# 查看剩余时间
TTL name                         # 秒

# 移除过期
PERSIST name                     # 取消过期时间

# 重命名
RENAME old_key new_key

# 随机返回一个key（不删除）
RANDOMKEY

# 查看数据库大小
DBSIZE                           # key的数量

# 清空当前数据库
FLUSHDB                          # 🚨 危险！

# 清空所有数据库
FLUSHALL                         # 🚨🚨 极度危险！
```

---

## 68.5 数据类型选择指南

| 需求 | 选型 | 示例 |
|------|------|------|
| 缓存单个值 | String | 缓存用户信息JSON、验证码 |
| 缓存对象，需要单独修改字段 | Hash | 用户资料（只改昵称不用更新整个JSON） |
| 队列/栈/最新列表 | List | 消息队列、最近浏览记录 |
| 去重集合/标签/共同好友 | Set | 标签、点赞用户、关注列表 |
| 排行榜/带权重的集合 | Sorted Set | 积分榜、销量排行、延时队列 |

---

## 本章小结

| 概念 | 要点 |
|------|------|
| Redis | 基于内存的键值数据库，读写速度纳秒级 |
| 为什么快 | 纯内存+单线程+IO多路复用+高效数据结构 |
| String | 最基本类型，支持数字原子操作和过期 |
| Hash | 存储对象，节省空间，可单独修改字段 |
| List | 有序列表，可用作队列或栈 |
| Set | 无序去重集合，支持交并差集运算 |
| Sorted Set | 带分数的有序集合，天然适合排行榜 |
| KEYS vs SCAN | KEYS阻塞，生产用SCAN |

---

## 自测题

1. **Redis的五大数据类型分别适用于什么场景？各举一个具体例子。**

2. **Redis为什么这么快？（至少说三个原因）**

3. **有一个文章阅读量的排行榜需求，实时更新阅读量并按阅读量排名。用Redis的哪种数据类型？写出关键命令。**

<details>
<summary>参考答案（做完再看）</summary>

1. String：缓存JSON对象、计数器、分布式锁。Hash：用户资料缓存，可以单独修改昵称。List：消息队列（LPUSH+BRPOP）、最新动态列表。Set：标签、共同好友（SINTER取交集）。Sorted Set：排行榜、延时队列。

2. 1) 纯内存操作，没有磁盘IO；2) 单线程处理命令，没有锁竞争和上下文切换；3) IO多路复用技术，一个线程处理多个客户端连接；4) 数据结构高度优化，RESP协议简单高效。

3. Sorted Set。命令：
```bash
ZINCRBY article:reads 1 "article:1001"    # 阅读量+1
ZREVRANGE article:reads 0 9 WITHSCORES    # 前10名
ZREVRANK article:reads "article:1001"     # 某篇文章的排名
```
</details>