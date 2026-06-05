# 附录C · Redis常用命令速查

> "Redis是你的高速缓存引擎——它把数据存在内存里，读写速度比MySQL快100倍以上。本附录覆盖5种数据类型的常用命令和运维命令，是你操作Redis时的快速参考。"

---

## C.1 通用命令

| 命令 | 作用 | 返回值 |
|------|------|--------|
| `KEYS pattern` | 查找匹配的键 | 匹配的键列表（生产禁用，用SCAN代替） |
| `SCAN cursor MATCH pattern COUNT n` | 渐进式遍历键 | 下一个游标+当前批次的键 |
| `DEL key [key...]` | 删除键 | 成功删除的键数量 |
| `EXISTS key` | 判断键是否存在 | 1存在 / 0不存在 |
| `EXPIRE key seconds` | 设置过期时间（秒） | 1成功 / 0失败（键不存在） |
| `EXPIREAT key timestamp` | 设置过期时间（Unix时间戳） | 1成功 / 0失败 |
| `TTL key` | 查看剩余过期时间（秒） | 正数=剩余秒数 / -1=未设过期 / -2=键不存在 |
| `PERSIST key` | 移除过期时间 | 1成功 / 0不存在或无过期 |
| `TYPE key` | 查看键的数据类型 | string/hash/list/set/zset/none |
| `RENAME key newkey` | 重命名 | OK |
| `RANDOMKEY` | 随机返回一个键 | 键名或nil |
| `MOVE key db` | 把键移到另一个数据库 | 1成功 / 0失败 |
| `SELECT db` | 切换数据库（0-15） | OK |
| `DBSIZE` | 当前数据库键数量 | 整数 |
| `FLUSHDB` | 清空当前数据库（危险！） | OK |
| `FLUSHALL` | 清空所有数据库（极度危险！） | OK |
| `INFO` | 服务器信息 | 键值对文本 |

---

## C.2 字符串（String）

Redis的String最大512MB，可以存文本、数字、二进制（图片缩略图等）。

| 命令 | 作用 | 返回值 |
|------|------|--------|
| `SET key value` | 设置值 | OK |
| `SET key value EX seconds` | 设置值+过期时间 | OK |
| `SET key value NX` | 仅不存在时设置（分布式锁） | OK / (nil) |
| `SET key value XX` | 仅存在时设置 | OK / (nil) |
| `GET key` | 获取值 | 值或(nil) |
| `GETSET key value` | 返回旧值并设新值 | 旧值或(nil) |
| `MSET k1 v1 k2 v2` | 批量设置 | OK |
| `MGET k1 k2` | 批量获取 | 值数组 |
| `INCR key` | 原子+1 | 增加后的值 |
| `DECR key` | 原子-1 | 减少后的值 |
| `INCRBY key n` | 原子+n | 增加后的值 |
| `DECRBY key n` | 原子-n | 减少后的值 |
| `APPEND key value` | 追加到末尾 | 追加后总长度 |
| `STRLEN key` | 字符串长度 | 长度整数 |
| `SETRANGE key offset value` | 从指定位置覆盖 | 修改后总长度 |
| `GETRANGE key start end` | 截取子字符串 | 子字符串 |
| `SETEX key seconds value` | 设置值并指定过期秒数 | OK |

### 典型场景

```bash
SET user:1:name "张三"
SET user:1:login_count 0
INCR user:1:login_count
SET lock:order:123 "token" NX EX 30
MGET user:1:name user:1:login_count
```

---

## C.3 哈希（Hash）

适合存储对象——相当于"Redis里的小型数据库表"。

| 命令 | 作用 | 返回值 |
|------|------|--------|
| `HSET key field value` | 设置字段 | 新增的字段数 |
| `HSET key f1 v1 f2 v2` | 批量设置 | 新增的字段数 |
| `HGET key field` | 获取字段值 | 值或(nil) |
| `HMGET key f1 f2` | 批量获取 | 值数组 |
| `HGETALL key` | 获取所有字段和值 | 字段值交替数组（field,value,field,value...） |
| `HEXISTS key field` | 判断字段是否存在 | 1存在 / 0不存在 |
| `HDEL key field` | 删除字段 | 成功删除的字段数 |
| `HLEN key` | 字段数量 | 整数 |
| `HKEYS key` | 所有字段名 | 字段名数组 |
| `HVALS key` | 所有字段值 | 字段值数组 |
| `HINCRBY key field n` | 字段值+n（整数） | 增加后的值 |
| `HINCRBYFLOAT key field n` | 字段值+n（浮点数） | 增加后的值 |
| `HSCAN key cursor` | 渐进式遍历 | 下一个游标+当前批次的字段值 |

### 典型场景

```bash
HSET user:1 name "张三" email "zhang@test.com" age 25
HGET user:1 name
HGETALL user:1
HINCRBY user:1 login_count 1
```

---

## C.4 列表（List）

有序可重复，底层是双向链表。适合消息队列、最新消息列表。

| 命令 | 作用 | 返回值 |
|------|------|--------|
| `LPUSH key v1 v2` | 从左侧插入 | 插入后列表长度 |
| `RPUSH key v1 v2` | 从右侧插入 | 插入后列表长度 |
| `LPOP key` | 从左侧弹出 | 弹出的值或(nil) |
| `RPOP key` | 从右侧弹出 | 弹出的值或(nil) |
| `LRANGE key start stop` | 获取范围（0 -1 = 全部） | 值数组 |
| `LLEN key` | 列表长度 | 整数 |
| `LINDEX key index` | 按索引获取 | 值或(nil) |
| `LSET key index value` | 按索引设置 | OK |
| `LREM key count value` | 删除指定值（count>0从左删，<0从右，0删全部） | 删除的个数 |
| `BLPOP key timeout` | 阻塞式左弹出 | 键名 值（timeout秒后无数据返回nil） |
| `BRPOP key timeout` | 阻塞式右弹出 | 键名 值 |
| `LTRIM key start stop` | 只保留范围元素 | OK |
| `RPOPLPUSH src dest` | 从src右弹出，左推入dest | 弹出的值 |

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

| 命令 | 作用 | 返回值 |
|------|------|--------|
| `SADD key member` | 添加成员 | 新增的成员数 |
| `SREM key member` | 删除成员 | 删除的成员数 |
| `SMEMBERS key` | 所有成员 | 成员数组 |
| `SISMEMBER key member` | 判断是否成员 | 1是 / 0否 |
| `SCARD key` | 成员数量 | 整数 |
| `SPOP key` | 随机弹出 | 弹出的成员 |
| `SPOP key n` | 随机弹出n个 | 弹出的成员数组 |
| `SRANDMEMBER key count` | 随机获取count个（不删除） | 成员或成员数组 |
| `SINTER k1 k2` | 交集 | 成员数组 |
| `SUNION k1 k2` | 并集 | 成员数组 |
| `SDIFF k1 k2` | 差集（k1有k2没有的） | 成员数组 |
| `SINTERSTORE dest k1 k2` | 交集存入dest | dest元素个数 |
| `SSCAN key cursor` | 渐进式遍历 | 下一个游标+成员 |

### 典型场景

```bash
SADD user:1:friends 2 3 4
SADD user:2:friends 3 4 5
SINTER user:1:friends user:2:friends
SISMEMBER user:1:friends 3
```

---

## C.6 有序集合（Sorted Set）

每个成员有一个分数，按分数排序。适合排行榜、延迟队列、带权重的标签。

| 命令 | 作用 | 返回值 |
|------|------|--------|
| `ZADD key score member` | 添加/更新 | 新增的成员数 |
| `ZREM key member` | 删除 | 删除的成员数 |
| `ZSCORE key member` | 获取分数 | 分数（字符串）或(nil) |
| `ZRANK key member` | 排名（升序，0开始） | 排名整数或(nil) |
| `ZREVRANK key member` | 排名（降序，0开始） | 排名整数或(nil) |
| `ZCARD key` | 成员数量 | 整数 |
| `ZCOUNT key min max` | 分数范围计数 | 整数 |
| `ZRANGE key start stop` | 按索引范围获取（升序） | 成员数组 |
| `ZRANGE key start stop WITHSCORES` | 按索引范围获取（含分数） | 成员+分数交替数组 |
| `ZREVRANGE key start stop` | 按索引范围获取（降序） | 成员数组 |
| `ZRANGEBYSCORE key min max` | 按分数范围获取 | 成员数组 |
| `ZINCRBY key n member` | 分数+n | 增加后的分数 |
| `ZREMRANGEBYRANK key start stop` | 按排名删除 | 删除的成员数 |
| `ZREMRANGEBYSCORE key min max` | 按分数删除 | 删除的成员数 |
| `ZUNIONSTORE dest n k1 k2` | 并集存入dest | dest元素个数 |

### 典型场景

```bash
ZADD leaderboard 100 "张三" 200 "李四" 150 "王五"
ZREVRANGE leaderboard 0 2 WITHSCORES
ZINCRBY leaderboard 10 "张三"
ZRANK leaderboard "张三"
```

---

## C.7 发布订阅（Pub/Sub）

| 命令 | 作用 |
|------|------|
| `SUBSCRIBE channel` | 订阅频道 |
| `UNSUBSCRIBE channel` | 取消订阅 |
| `PUBLISH channel message` | 发布消息（返回收到消息的订阅者数） |
| `PSUBSCRIBE pattern` | 模式订阅（如`PSUBSCRIBE news.*`匹配所有news.开头的频道） |

---

## C.8 运维命令

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
| `MEMORY USAGE key` | 键占用内存字节数 |
| `MEMORY STATS` | 内存统计 |

### 慢查询配置

```bash
CONFIG SET slowlog-log-slower-than 10000
CONFIG SET slowlog-max-len 128
SLOWLOG GET 10
```

---

## C.9 Redis与Java（Spring Data Redis）

```java
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.data.redis.core.ValueOperations;

@Autowired
private RedisTemplate<String, String> redisTemplate;

// String操作
ValueOperations<String, String> ops = redisTemplate.opsForValue();
ops.set("key", "value", 10, TimeUnit.MINUTES);
String val = ops.get("key");

// Hash操作
redisTemplate.opsForHash().put("user:1", "name", "张三");
Object name = redisTemplate.opsForHash().get("user:1", "name");

// List操作
redisTemplate.opsForList().leftPush("messages", "hello");
redisTemplate.opsForList().rightPush("messages", "world");
List<String> msgs = redisTemplate.opsForList().range("messages", 0, -1);
```

---

Redis五种数据类型各有适用场景：String做缓存和计数，Hash存对象，List做消息队列，Set做标签和共同好友，Sorted Set做排行榜。掌握这五种类型，就能应对90%的缓存场景。

---

[← 上一章：附录B-MySQL命令速查.md](附录B-MySQL命令速查.md) | [下一章：附录D-Docker命令速查.md →](附录D-Docker命令速查.md)