# 第60章 · Redis入门

> "MySQL就像一个大型仓库，东西存在硬盘里，安全可靠但每次取货都要走一段路。Redis（数据存在内存里的超快存储，详见附录I）是你办公桌上的便签纸——伸手就能写，低头就能看，快得不可思议。但便签纸有缺点：桌上的空间有限（内存毕竟比硬盘小），而且不小心被人泼杯水就没了（宕机数据可能丢）。Redis的设计哲学就是在这个'快但脆弱'的基础上，尽可能地加保险。今天先用一天学会Redis的五种基本数据类型——它们覆盖了90%的缓存（把热点数据放内存里加速读取，详见附录I）场景。"

---

## 60.1 Redis为什么这么快

Redis官方benchmark：单机实例可以达到**10万QPS**（每秒请求数），而同等硬件下的MySQL约1000~3000 QPS。为什么差距这么大？

### 1. 数据存在内存中

MySQL的数据在硬盘上。硬盘读写需要机械臂移动（HDD）或电子层寻址（SSD），延迟是毫秒级。内存的延迟是纳秒级——差了1000倍。

**比喻**：内存是桌上伸手就能拿到的东西，硬盘是走到隔壁仓库取东西——多出来的"走过去"这几十米就是性能差距。

### 2. 单线程架构

Redis的核心操作是**单线程**的。听到"单线程"你可能以为它慢——恰恰相反。

多线程需要在多个线程间切换（上下文切换开销），还要用锁保护共享数据（锁竞争开销）。Redis说"我不需要跑多快，我就一条跑道，但这条路是8车道的高速公路"——没有任何锁开销，没有任何上下文切换。

**一个反直觉的事实**：Redis的瓶颈从来不是CPU，而是**网络带宽**和**内存大小**。

### 3. 高效的数据结构

Redis的每种数据结构都经过了极致的底层优化。比如Hash在数据量小时用压缩列表（ziplist），大了自动转哈希表——在空间和速度之间做动态平衡。

### 4. 事件驱动+I/O多路复用

Redis使用epoll/kqueue等机制，一个线程同时监听多个客户端连接。这跟Node.js的单线程事件循环是同一个原理。你在第9章学过epoll——Redis就是它的教科书级应用。

---

## 60.2 安装和基本操作

### Windows安装

Redis官方不直接支持Windows。两种方案：

1. **WSL2（推荐）**：在WSL2的Ubuntu中安装Redis，性能好，和Linux环境一致。
2. **Memurai**：Redis Windows兼容版，免费开发者版够用。

WSL2方案：

```bash
wsl
sudo apt update
sudo apt install redis-server -y
sudo systemctl start redis
redis-cli ping
```

如果返回 `PONG`，恭喜安装成功。

### Linux安装

```bash
sudo apt install redis-server -y
sudo systemctl start redis
```

### 进入redis-cli

```bash
redis-cli
```

你会看到 `127.0.0.1:6379>` 这个提示符——6379是Redis的默认端口（MERZ在手机键盘上对应的数字，Redis作者antirez的一个小彩蛋）。

### 基本命令

```bash
SET key value     # 设置键值
GET key           # 获取键值
DEL key           # 删除键
EXISTS key        # 检查键是否存在
EXPIRE key 60     # 设键60秒后过期
TTL key           # 查看剩余过期时间
KEYS pattern      # 查找匹配的键（生产环境禁用！）
FLUSHALL          # 清空所有数据（等同于DROP DATABASE）
```

---

## 60.3 String：最基础的数据类型

Redis的String是**二进制安全**的——你可以存文本、数字、序列化的JSON，甚至是图片的二进制数据。单个value最大512MB。

### SET / GET

```bash
SET username "zhangsan"
GET username
```

```bash
SET counter 100
GET counter
```

GET返回的总是字符串。`counter` 的值是字符串 `"100"`，不是数字100。但Redis内置了数值操作：

### INCR / DECR

```bash
SET views 0
INCR views
(integer) 1
INCR views
(integer) 2
INCRBY views 10
(integer) 12
DECR views
(integer) 11
```

- `INCR`：值加1（原子操作！）
- `DECR`：值减1
- `INCRBY`：加指定值
- `DECRBY`：减指定值

**这些都是原子操作**——1000个客户端同时INCR同一个key，绝对不会出现计数不准的问题。因为Redis是单线程的，每个命令执行时都是独占的。

### SETNX（SET if Not eXists）

```bash
SETNX lock:order:123 "locked"
(integer) 1
SETNX lock:order:123 "locked"
(integer) 0
```

第一次SETNX返回1（成功），第二次返回0（失败）。这是**分布式锁**的基础。

### EXPIRE

```bash
SET session:token_abc "user_id_1"
EXPIRE session:token_abc 3600
TTL session:token_abc
(integer) 3598
```

登录token存1小时就自动删除——完美的会话管理。SET也可以用一条命令同时设值和过期时间：

```bash
SET session:token_abc "user_id_1" EX 3600
```

### 批量操作

```bash
MSET key1 "value1" key2 "value2" key3 "value3"
MGET key1 key2 key3
```

批量比单个GET少了很多次网络往返。

---

## 60.4 Hash：对象存储

Hash存的是**键值对的键值对**——就像Go的 `map[string]string`。

### HSET / HGET

```bash
HSET user:1 username "zhangsan" email "zs@test.com" age "25"
HGET user:1 username
"zhangsan"
HGET user:1 email
"zs@test.com"
```

一个Hash key可以存成百上千个字段。你可以把它理解为一行的数据——比MySQL快得多。

### HGETALL / HMGET

```bash
HGETALL user:1
1) "username"
2) "zhangsan"
3) "email"
4) "zs@test.com"
5) "age"
6) "25"
```

返回的是一个扁平的key-value列表（奇数位是字段名，偶数位是值）。

```bash
HMGET user:1 username email
1) "zhangsan"
2) "zs@test.com"
```

只取指定字段。

### HINCRBY

```bash
HINCRBY user:1 age 5
(integer) 30
```

Hash里的数值字段也可以自增。

### HDEL / HEXISTS / HKEYS / HVALS / HLEN

```bash
HDEL user:1 age
HEXISTS user:1 username
HKEYS user:1
HVALS user:1
HLEN user:1
```

---

## 60.5 List：有序列表

Redis的List是一个**双向链表**——左边是head，右边是tail。你可以从两端推入和弹出。

### LPUSH / RPUSH

```bash
LPUSH tasks "send_email"
LPUSH tasks "clean_db"
RPUSH tasks "generate_report"
```

```
head ← "clean_db" ← "send_email" ← "generate_report" → tail
```

### LRANGE

```bash
LRANGE tasks 0 -1
1) "clean_db"
2) "send_email"
3) "generate_report"
```

`0` 是第一个元素，`-1` 是最后一个元素（Python风格的负索引）。

### LPOP / RPOP

```bash
LPOP tasks
"clean_db"
RPOP tasks
"generate_report"
```

**List做消息队列**：生产者 `RPUSH` 任务到尾部，消费者 `LPOP` 从头部取任务。虽然简单，但耐用性不足（消费失败无法重试）。改进方案：使用 `BLPOP`（阻塞弹出）替代 `LPOP`，当队列为空时消费者自动阻塞等待，避免空轮询浪费CPU。不过生产环境的消息队列还是用RabbitMQ/Kafka更靠谱。

### LLEN

```bash
LLEN tasks
```

### LTRIM（裁剪）

```bash
RPUSH logs "log1" "log2" "log3" "log4" "log5"
LTRIM logs 0 2
LRANGE logs 0 -1
1) "log1"
2) "log2"
3) "log3"
```

只保留前3个元素。适合实现"最近N条"功能（如最近浏览记录）。

---

## 60.6 Set：无序不重复集合

Set是不可重复的字符串集合——**自动去重**。

### SADD / SMEMBERS

```bash
SADD tags:article1 "golang" "redis" "database"
SADD tags:article1 "golang"
(integer) 0
SMEMBERS tags:article1
1) "golang"
2) "redis"
3) "database"
```

第二次SADD "golang"返回0——说明已存在，没插入。

### SINTER / SUNION / SDIFF

```bash
SADD user1:tags "golang" "redis" "python"
SADD user2:tags "redis" "python" "java"

SINTER user1:tags user2:tags
1) "redis"
2) "python"

SUNION user1:tags user2:tags
1) "golang"
2) "redis"
3) "python"
4) "java"

SDIFF user1:tags user2:tags
1) "golang"
```

这三个集合运算在做"共同好友"、"推荐好友"等功能时极其好用：

```bash
SADD friends:user1 "user2" "user3" "user4"
SADD friends:user5 "user3" "user4" "user6"
SINTER friends:user1 friends:user5
```

返回 `["user3", "user4"]`——user1和user5的共同好友。

### SCARD / SISMEMBER / SPOP / SRANDMEMBER

```bash
SCARD tags:article1
SISMEMBER tags:article1 "golang"
SPOP tags:article1
SRANDMEMBER tags:article1 2
```

---

## 60.7 Sorted Set：带分数的有序集合

如果说Set是"篮子里的球"，Sorted Set就是"按得分排名的排行榜"。每个元素都关联一个**分数（score）**，Redis按分数从小到大自动排序。分数相同时按字典序排。

### ZADD / ZRANGE

```bash
ZADD leaderboard 100 "player1"
ZADD leaderboard 250 "player2"
ZADD leaderboard 180 "player3"
ZADD leaderboard 300 "player4"

ZRANGE leaderboard 0 -1
1) "player1"
2) "player3"
3) "player2"
4) "player4"
```

### ZRANGE WITHSCORES（带分数）

```bash
ZRANGE leaderboard 0 -1 WITHSCORES
1) "player1"
2) "100"
3) "player3"
4) "180"
5) "player2"
6) "250"
7) "player4"
8) "300"
```

### ZREVRANGE（降序）

```bash
ZREVRANGE leaderboard 0 -1 WITHSCORES
1) "player4"
2) "300"
3) "player2"
4) "250"
5) "player3"
6) "180"
7) "player1"
8) "100"
```

### ZRANK / ZSCORE（查排名和分数）

```bash
ZRANK leaderboard "player3"
(integer) 1
ZSCORE leaderboard "player3"
"180"
```

`ZRANK` 返回的是升序排名（从0开始），player3分数180排第2（player1的100是第0）。

如果是降序排名用 `ZREVRANK`。

### ZINCRBY（增减分数）

```bash
ZINCRBY leaderboard 50 "player1"
```

player1加了50分，排名自动调整——不用手动重新排序。

### ZRANGEBYSCORE（按分数范围取）

```bash
ZRANGEBYSCORE leaderboard 150 250 WITHSCORES
```

返回分数在150~250之间的玩家。支持 `(` 开区间：`(150 (250` 表示不包含边界。

### 实战：游戏排行榜

```bash
ZADD rank:daily 0 "user:1"
ZADD rank:daily 0 "user:2"
ZADD rank:daily 0 "user:3"

ZINCRBY rank:daily 100 "user:2"
ZINCRBY rank:daily 50 "user:1"
ZINCRBY rank:daily 200 "user:3"

ZREVRANGE rank:daily 0 2 WITHSCORES
1) "user:3"
2) "200"
3) "user:2"
4) "100"
5) "user:1"
6) "50"
```

这就是各大游戏实时排行榜的底层实现——Sorted Set让这一切简单到令人发指。

---

## 本章小结

| 知识点 | 要点 |
|--------|------|
| 为什么快 | 内存存储、单线程无锁、高效数据结构、事件驱动IO |
| 安装 | WSL2中apt install，`redis-cli ping` 验证 |
| String | SET/GET/INCR/DECR/SETNX/EXPIRE，二进制安全，最大512MB |
| Hash | HSET/HGET/HGETALL/HINCRBY，存对象（map字段值） |
| List | LPUSH/RPUSH/LPOP/RPOP/LRANGE，双向链表，可做简单消息队列 |
| Set | SADD/SMEMBERS/SINTER/SUNION/SDIFF，无序去重，社交关系计算 |
| Sorted Set | ZADD/ZRANGE/ZREVRANGE/ZINCRBY/ZRANK，按分数排序，排行榜神器 |

> 🚀 下一章：第61章 · Redis进阶。五种基本数据类型你已经会了，但Redis远不止这些。它支持发布订阅（像聊天室一样广播消息）、事务（MULTI/EXEC）、Lua脚本（原子执行多条命令），还有RDB和AOF两种持久化方案让内存数据不丢——以及内存满了怎么办的淘汰策略。进阶内容让你的Redis能力提升一个层次。

---
[← 上一章：59-Go操作MySQL](59-Go操作MySQL.md) | [下一章：61-Redis进阶 →](61-Redis进阶.md)
