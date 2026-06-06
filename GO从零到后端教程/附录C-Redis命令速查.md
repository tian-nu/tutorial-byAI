# 附录C · Redis常用命令速查

> "Redis是你的高速缓存引擎——它把数据存在内存里，读写速度比MySQL快100倍以上。本附录覆盖5种数据类型的常用命令和运维命令，是你操作Redis时的快速参考。"

---

## C.1 通用命令

| 命令 | 作用 |
|------|------|
| `KEYS pattern` | 查找匹配的键（生产禁用，用SCAN代替） |
| `SCAN cursor MATCH pattern COUNT n` | 渐进式遍历键 |
| `DEL key [key...]` | 删除键 |
| `EXISTS key` | 判断键是否存在 |
| `EXPIRE key seconds` | 设置过期时间（秒） |
| `EXPIREAT key timestamp` | 设置过期时间（Unix时间戳） |
| `TTL key` | 查看剩余过期时间（秒） |
| `PERSIST key` | 移除过期时间 |
| `TYPE key` | 查看键的类型 |
| `RENAME key newkey` | 重命名键 |
| `RANDOMKEY` | 随机返回一个键 |
| `MOVE key db` | 把键移到另一个数据库 |
| `SELECT db` | 切换数据库（0-15） |
| `DBSIZE` | 当前数据库键数量 |
| `FLUSHDB` | 清空当前数据库（危险！） |
| `FLUSHALL` | 清空所有数据库（极度危险！） |
| `INFO` | 服务器信息 |

---

## C.2 字符串（String）

Redis的String最大512MB，可以存文本、数字、二进制（图片缩略图等）。

| 命令 | 作用 |
|------|------|
| `SET key value` | 设置值 |
| `SET key value EX seconds` | 设置值+过期时间 |
| `SET key value NX` | 仅不存在时设置（分布式锁） |
| `SET key value XX` | 仅存在时设置 |
| `GET key` | 获取值 |
| `GETSET key value` | 返回旧值并设新值 |
| `MSET k1 v1 k2 v2` | 批量设置 |
| `MGET k1 k2` | 批量获取 |
| `INCR key` | 原子+1 |
| `DECR key` | 原子-1 |
| `INCRBY key n` | 原子+n |
| `DECRBY key n` | 原子-n |
| `APPEND key value` | 追加到末尾 |
| `STRLEN key` | 字符串长度 |
| `SETRANGE key offset value` | 从指定位置覆盖 |
| `GETRANGE key start end` | 截取子字符串 |

### 典型场景

```bash
SET user:1:name "张三"
SET user:1:login_count 0
INCR user:1:login_count
SET lock:order:123 "token" NX EX 30
```

---

## C.3 哈希（Hash）

适合存储对象——相当于"Redis里的小型MySQL表"。

| 命令 | 作用 |
|------|------|
| `HSET key field value` | 设置字段 |
| `HMSET key f1 v1 f2 v2` | 批量设置（已废弃，推荐 `HSET key f1 v1 f2 v2`） |
| `HGET key field` | 获取字段值 |
| `HMGET key f1 f2` | 批量获取 |
| `HGETALL key` | 获取所有字段和值 |
| `HEXISTS key field` | 判断字段是否存在 |
| `HDEL key field` | 删除字段 |
| `HLEN key` | 字段数量 |
| `HKEYS key` | 所有字段名 |
| `HVALS key` | 所有字段值 |
| `HINCRBY key field n` | 字段值+n |
| `HSCAN key cursor` | 渐进式遍历 |

### 典型场景

```bash
HSET user:1 name "张三" email "zhang@test.com" age 25
HGET user:1 name
HINCRBY user:1 login_count 1
```

---

## C.4 列表（List）

有序可重复，底层是双向链表。适合消息队列、最新消息列表。

| 命令 | 作用 |
|------|------|
| `LPUSH key v1 v2` | 从左侧插入 |
| `RPUSH key v1 v2` | 从右侧插入 |
| `LPOP key` | 从左侧弹出 |
| `RPOP key` | 从右侧弹出 |
| `LRANGE key start stop` | 获取范围（0 -1 = 全部） |
| `LLEN key` | 列表长度 |
| `LINDEX key index` | 按索引获取 |
| `LSET key index value` | 按索引设置 |
| `LREM key count value` | 删除指定值 |
| `BLPOP key timeout` | 阻塞式左弹出 |
| `BRPOP key timeout` | 阻塞式右弹出 |

### 典型场景

```bash
LPUSH messages "hello"
RPUSH messages "world"
LRANGE messages 0 -1
BLPOP queue 30
```

---

## C.5 集合（Set）

无序、不可重复。适合标签、好友列表、共同好友。

| 命令 | 作用 |
|------|------|
| `SADD key member` | 添加成员 |
| `SREM key member` | 删除成员 |
| `SMEMBERS key` | 所有成员 |
| `SISMEMBER key member` | 判断是否成员 |
| `SCARD key` | 成员数量 |
| `SPOP key` | 随机弹出 |
| `SRANDMEMBER key count` | 随机获取 |
| `SINTER k1 k2` | 交集 |
| `SUNION k1 k2` | 并集 |
| `SDIFF k1 k2` | 差集 |
| `SINTERSTORE dest k1 k2` | 交集存入dest |

### 典型场景

```bash
SADD user:1:friends 2 3 4
SADD user:2:friends 3 4 5
SINTER user:1:friends user:2:friends
```

---

## C.6 有序集合（Sorted Set）

每个成员有一个分数，按分数排序。适合排行榜、延迟队列、带权重的标签。

| 命令 | 作用 |
|------|------|
| `ZADD key score member` | 添加/更新 |
| `ZREM key member` | 删除 |
| `ZSCORE key member` | 获取分数 |
| `ZRANK key member` | 排名（升序，0开始） |
| `ZREVRANK key member` | 排名（降序） |
| `ZCARD key` | 成员数量 |
| `ZCOUNT key min max` | 分数范围计数 |
| `ZRANGE key start stop` | 按索引范围获取（升序） |
| `ZREVRANGE key start stop` | 按索引范围获取（降序） |
| `ZRANGEBYSCORE key min max` | 按分数范围获取 |
| `ZINCRBY key n member` | 分数+n |
| `ZREMRANGEBYRANK key start stop` | 按排名删除 |
| `ZREMRANGEBYSCORE key min max` | 按分数删除 |
| `ZUNIONSTORE dest n k1 k2` | 并集存入dest |

### 典型场景

```bash
ZADD leaderboard 100 "张三" 200 "李四" 150 "王五"
ZREVRANGE leaderboard 0 2 WITHSCORES
ZINCRBY leaderboard 10 "张三"
```

---

## C.7 发布订阅（Pub/Sub）

| 命令 | 作用 |
|------|------|
| `SUBSCRIBE channel` | 订阅频道 |
| `UNSUBSCRIBE channel` | 取消订阅 |
| `PUBLISH channel message` | 发布消息 |
| `PSUBSCRIBE pattern` | 模式订阅 |

---

## C.8 Lua脚本

```bash
EVAL "return redis.call('GET', KEYS[1])" 1 key
EVAL "return redis.call('SET', KEYS[1], ARGV[1])" 1 key value
EVALSHA sha1 1 key
SCRIPT LOAD "return ..."
```

Lua脚本在Redis中原子执行——整个脚本作为一个整体，不会被其他命令打断。

---

## C.9 运维命令

| 命令 | 作用 |
|------|------|
| `INFO [section]` | 服务器信息（server/clients/memory/stats/replication） |
| `CONFIG GET parameter` | 获取配置 |
| `CONFIG SET parameter value` | 动态修改配置 |
| `SLOWLOG GET n` | 获取慢查询日志 |
| `SLOWLOG RESET` | 清空慢查询 |
| `CLIENT LIST` | 客户端列表 |
| `CLIENT KILL ip:port` | 断开客户端 |
| `MONITOR` | 实时监控所有命令 |
| `SAVE` | 同步保存RDB |
| `BGSAVE` | 异步保存RDB |
| `LASTSAVE` | 上次保存时间 |
| `MEMORY USAGE key` | 键占用内存 |
| `MEMORY STATS` | 内存统计 |

### 慢查询配置

```bash
CONFIG SET slowlog-log-slower-than 10000
CONFIG SET slowlog-max-len 128
SLOWLOG GET 10
```

---

## C.10 Redis与Go（go-redis v9需Go 1.18+）

```go
import "github.com/redis/go-redis/v9"

rdb := redis.NewClient(&redis.Options{
    Addr:     "localhost:6379",
    Password: "",
    DB:       0,
})

ctx := context.Background()

rdb.Set(ctx, "key", "value", 10*time.Minute)
val, _ := rdb.Get(ctx, "key").Result()

rdb.HSet(ctx, "user:1", "name", "张三", "age", 25)
name, _ := rdb.HGet(ctx, "user:1", "name").Result()

result, _ := rdb.Eval(ctx, luaScript, []string{key}, arg).Result()
```

---

Redis五种数据类型各有适用场景：String做缓存和计数，Hash存对象，List做消息队列，Set做标签和共同好友，Sorted Set做排行榜。掌握这五种类型，就能应对90%的缓存场景。

---
[← 上一章：附录B-MySQL常用命令速查.md](附录B-MySQL常用命令速查/) | [下一章：附录D-Docker命令速查.md →](附录D-Docker命令速查/)
