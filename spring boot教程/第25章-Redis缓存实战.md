# 第25章：Redis缓存实战

## 本章目标

学完本章你将能够：

- 理解Redis与MySQL的本质区别，掌握Redis五大核心数据类型及其适用场景
- 在Spring Boot中集成Redis，正确配置Lettuce连接池和JSON序列化（**不用JDK序列化！**）
- 使用Spring Cache三大注解（`@Cacheable`/`@CachePut`/`@CacheEvict`）实现声明式缓存
- **亲手解决缓存穿透、击穿、雪崩三大经典问题**——每种问题都有概念图、问题代码和解决方案代码
- 使用布隆过滤器防止缓存穿透，使用Redisson分布式锁防止缓存击穿
- 理解缓存与数据库的数据一致性方案（先更新DB再删缓存 + 延迟双删）
- 使用Redisson分布式锁防止重复提交，掌握try-finally正确释放锁的范式
- **完成EMS v8：缓存优化版**——为员工查询接口加缓存、防穿透/击穿、加分布式锁

---

> **本章定位**：第24章我们用JWT实现了无状态认证，RefreshToken存到了Redis中——那只是Redis的冰山一角。本章将全面展开Redis在缓存领域的实战应用。缓存是面试必考、实战必用的核心技术，三大缓存问题更是高级工程师的试金石。

---

## 25.1 Redis入门

### 25.1.1 Redis是什么

Redis（Remote Dictionary Server，远程字典服务）是一个基于内存的键值对存储系统。和MySQL做个对比：

```
┌──────────────────────────────────────────────────────┐
│              MySQL vs Redis 定位对比                   │
├──────────────┬──────────────────┬────────────────────┤
│     维度      │     MySQL        │      Redis         │
├──────────────┼──────────────────┼────────────────────┤
│  存储介质     │  硬盘（SSD/HDD）  │  内存（RAM）        │
│  读写速度     │  毫秒级           │  微秒级（100x+）    │
│  数据持久化   │  天然持久化       │  可选（RDB/AOF）    │
│  数据可靠性   │  ACID事务保证     │  不保证不丢数据      │
│  数据结构     │  表+行+列        │  五种数据类型        │
│  适用场景     │  持久化存储       │  缓存/临时数据       │
└──────────────┴──────────────────┴────────────────────┘
```

**一句话定位**：MySQL是"数据的家"，数据长期住在那里；Redis是"数据的快递站"，数据只是路过——快，但不保证永远在。

Redis的核心使用场景：

| 场景 | 说明 | 数据类型 |
|------|------|---------|
| 缓存 | 最核心场景，热点数据放内存 | String/Hash |
| 分布式锁 | 多实例互斥访问共享资源 | String（SETNX） |
| 消息队列 | 简单的异步消息处理 | List（LPUSH+BRPOP） |
| 排行榜 | 实时排名计算 | ZSet |
| 计数器 | 点赞数、访问量 | String（INCR） |
| 共同关注 | 社交关系交集 | Set（SINTER） |

### 25.1.2 Redis 7安装

**Windows**：推荐使用WSL（Windows Subsystem for Linux）安装原生Redis，或使用Memurai（Windows原生Redis兼容服务）。

```bash
# WSL (Ubuntu) 中安装
sudo apt update
sudo apt install redis-server
sudo service redis-server start
```

**Mac**：

```bash
brew install redis
brew services start redis
```

**Linux (Ubuntu/Debian)**：

```bash
sudo apt update
sudo apt install redis-server
sudo systemctl enable redis-server
sudo systemctl start redis-server
```

### 25.1.3 Redis-cli基本操作

安装完成后，用`redis-cli`连接Redis服务器：

```bash
# 连接本地Redis（默认端口6379）
redis-cli

# 带密码连接
redis-cli -h 127.0.0.1 -p 6379 -a your_password

# 测试连通性
127.0.0.1:6379> PING
PONG

# 基本操作
127.0.0.1:6379> SET name "张三"       # 设置键值
OK
127.0.0.1:6379> GET name              # 获取值
"\xe5\xbc\xa0\xe4\xb8\x89"            # 中文显示为UTF-8字节
127.0.0.1:6379> SET name "张三"        # 加raw模式显示中文
127.0.0.1:6379> GET name
"张三"
127.0.0.1:6379> DEL name              # 删除键
(integer) 1
127.0.0.1:6379> EXISTS name           # 判断键是否存在
(integer) 0
127.0.0.1:6379> EXPIRE name 60        # 设置过期时间60秒
(integer) 1
127.0.0.1:6379> TTL name              # 查看剩余过期时间
(integer) 58
127.0.0.1:6379> DBSIZE                # 查看键总数
(integer) 5
```

> 🚨 **致命坑点：Redis默认无密码 + 绑定127.0.0.1**
>
> Redis安装后默认`requirepass`为空，`bind`为`127.0.0.1`。开发环境没问题，但**生产环境必须**：
> 1. 设置密码：`requirepass your_strong_password`
> 2. 绑定内网IP：`bind 10.0.0.1`（不要绑定公网IP！）
> 3. 禁用危险命令：`rename-command FLUSHALL ""`
>
> 历史上无数Redis未授权访问导致服务器被植入挖矿脚本的案例——这不是开玩笑。

> 🚨 **致命坑点：生产环境禁用`keys *`**
>
> `keys *`会遍历Redis中所有键，当键数量达到百万级时，这条命令会阻塞Redis数秒，期间所有请求超时。**用`scan`替代**：
>
> ```bash
> # ❌ 灾难级操作
> 127.0.0.1:6379> KEYS user:*
>
> # ✅ 安全替代
> 127.0.0.1:6379> SCAN 0 MATCH user:* COUNT 100
> ```
>
> `scan`是增量式遍历，每次只返回少量结果和一个游标，不会阻塞Redis。

---

## 25.2 五种数据类型

Redis提供五种核心数据类型，每种类型有独特的底层结构和适用场景。理解它们，是正确使用Redis的基础。

### 25.2.1 String — 最基础的KV存储

String是Redis最基本的数据类型，底层使用SDS（Simple Dynamic String）动态字符串实现，最大可存储512MB数据。

**常用命令**：

| 命令 | 说明 | 示例 |
|------|------|------|
| `SET key value` | 设置键值 | `SET user:1:name "张三"` |
| `GET key` | 获取值 | `GET user:1:name` |
| `DEL key` | 删除键 | `DEL user:1:name` |
| `EXISTS key` | 判断键是否存在 | `EXISTS user:1:name` |
| `EXPIRE key seconds` | 设置过期时间（秒） | `EXPIRE user:1:name 3600` |
| `TTL key` | 查看剩余过期时间 | `TTL user:1:name` |
| `SETNX key value` | 仅当key不存在时设置 | `SETNX lock:order:1 "locked"` |
| `SETEX key seconds value` | 设置键值+过期时间（原子操作） | `SETEX token:abc 1800 "user1"` |
| `INCR key` | 自增1 | `INCR article:1001:views` |
| `DECR key` | 自减1 | `DECR stock:1001` |
| `INCRBY key increment` | 自增指定值 | `INCRBY stock:1001 10` |

**典型场景**：

```bash
# 场景1：缓存对象（JSON字符串）
SET user:1001 '{"id":1001,"name":"张三","age":28}'
GET user:1001

# 场景2：计数器
SET article:1001:views 0
INCR article:1001:views        # 阅读量+1
INCR article:1001:views        # 再+1
GET article:1001:views          # "2"

# 场景3：分布式锁基础
SETNX lock:order:1001 "locked"  # 返回1表示获取锁成功
SETNX lock:order:1001 "locked"  # 返回0表示锁已被占用
DEL lock:order:1001              # 释放锁
```

> **关键点**：`SETNX`+`EXPIRE`不是原子操作！如果SETNX成功但EXPIRE前进程崩溃，锁永远不会释放。Redis 2.6.12+支持原子操作：`SET lock:order:1001 "locked" EX 30 NX`。

### 25.2.2 List — 双向链表

List是按插入顺序排序的字符串链表，底层使用quicklist（压缩列表+双向链表）实现。

**常用命令**：

| 命令 | 说明 | 示例 |
|------|------|------|
| `LPUSH key value` | 左端（头部）插入 | `LPUSH tasks "task3"` |
| `RPUSH key value` | 右端（尾部）插入 | `RPUSH tasks "task1"` |
| `LPOP key` | 左端弹出 | `LPOP tasks` |
| `RPOP key` | 右端弹出 | `RPOP tasks` |
| `LRANGE key start stop` | 获取指定范围元素 | `LRANGE tasks 0 -1` |
| `LLEN key` | 获取列表长度 | `LLEN tasks` |
| `BRPOP key timeout` | 阻塞式右端弹出 | `BRPOP tasks 30` |

**典型场景**：

```bash
# 场景：简单消息队列
# 生产者：从左端推入消息
LPUSH queue:email "send_email:user:1001"
LPUSH queue:email "send_email:user:1002"

# 消费者：从右端阻塞弹出（没有消息时等待30秒）
BRPOP queue:email 30
# 返回：1) "queue:email"  2) "send_email:user:1001"
```

```
消息队列模型：
生产者                         Redis List                     消费者
  │                              │                              │
  │  LPUSH ──────────────────►   │  ┌───┬───┬───┬───┐          │
  │                              │  │ m4│ m3│ m2│ m1│          │
  │                              │  └───┴───┴───┴───┘          │
  │                              │   ▲ LPUSH        BRPOP ▲     │
  │                              │   │                    │     │
  │                              │◄──────────────────────┘     │
```

### 25.2.3 Set — 无序不重复集合

Set是字符串的无序集合，底层使用intset（纯整数时）或hashtable实现，元素不重复。

**常用命令**：

| 命令 | 说明 | 示例 |
|------|------|------|
| `SADD key member` | 添加元素 | `SADD tags:article:1 "Java"` |
| `SREM key member` | 移除元素 | `SREM tags:article:1 "Java"` |
| `SMEMBERS key` | 获取所有元素 | `SMEMBERS tags:article:1` |
| `SISMEMBER key member` | 判断元素是否存在 | `SISMEMBER tags:article:1 "Java"` |
| `SINTER key1 key2` | 交集 | `SINTER follows:user:1 follows:user:2` |
| `SUNION key1 key2` | 并集 | `SUNION tags:article:1 tags:article:2` |
| `SDIFF key1 key2` | 差集 | `SDIFF follows:user:1 follows:user:2` |
| `SCARD key` | 获取元素数量 | `SCARD tags:article:1` |

**典型场景**：

```bash
# 场景1：共同关注
SADD follows:user:1 "Java" "Spring" "Redis"
SADD follows:user:2 "Spring" "Redis" "MySQL"
SINTER follows:user:1 follows:user:2
# 返回：1) "Spring"  2) "Redis"

# 场景2：抽奖去重
SADD lottery:activity:1 "user1" "user2" "user3"
SADD lottery:activity:1 "user1"          # 重复添加，自动去重
SCARD lottery:activity:1                  # 返回3，不是4
SRANDMEMBER lottery:activity:1 1          # 随机抽1人
SPOP lottery:activity:1 1                 # 随机抽1人并移除（中奖后不可再抽）
```

### 25.2.4 Hash — 字段-值映射

Hash是字段（field）到值（value）的映射表，底层使用listpack（小Hash）或hashtable（大Hash）实现。适合存储对象——比用JSON String存对象更灵活，可以单独修改某个字段。

**常用命令**：

| 命令 | 说明 | 示例 |
|------|------|------|
| `HSET key field value` | 设置字段值 | `HSET user:1001 name "张三"` |
| `HGET key field` | 获取字段值 | `HGET user:1001 name` |
| `HMSET key field value ...` | 批量设置 | `HMSET user:1001 name "张三" age 28` |
| `HGETALL key` | 获取所有字段和值 | `HGETALL user:1001` |
| `HDEL key field` | 删除字段 | `HDEL user:1001 age` |
| `HINCRBY key field increment` | 字段值自增 | `HINCRBY user:1001 age 1` |
| `HEXISTS key field` | 判断字段是否存在 | `HEXISTS user:1001 name` |

**String vs Hash存储对象对比**：

```bash
# 方式1：String存JSON（整体读写）
SET user:1001 '{"name":"张三","age":28,"dept":"技术部"}'
# 修改age → 需要读取整个JSON → 修改 → 写回（非原子，有并发问题）

# 方式2：Hash存对象（字段级读写）
HMSET user:1001 name "张三" age 28 dept "技术部"
# 修改age → 一条命令搞定
HINCRBY user:1001 age 1    # 原子操作，只改age字段
HGET user:1001 name         # 只读name字段，不传输整个对象
```

**选择建议**：对象字段经常单独修改用Hash；对象整体读写用String+JSON。

### 25.2.5 ZSet — 有序集合

ZSet（Sorted Set）在Set的基础上为每个元素关联一个score（分数），按分数排序。底层使用listpack（小规模）或skiplist+hashtable（大规模）实现。

**常用命令**：

| 命令 | 说明 | 示例 |
|------|------|------|
| `ZADD key score member` | 添加元素（带分数） | `ZADD rank:score 95 "张三"` |
| `ZRANGE key start stop` | 按分数升序获取 | `ZRANGE rank:score 0 -1` |
| `ZREVRANGE key start stop` | 按分数降序获取 | `ZREVRANGE rank:score 0 9` |
| `ZRANK key member` | 获取升序排名 | `ZRANK rank:score "张三"` |
| `ZREVRANK key member` | 获取降序排名 | `ZREVRANK rank:score "张三"` |
| `ZSCORE key member` | 获取元素分数 | `ZSCORE rank:score "张三"` |
| `ZINCRBY key increment member` | 增加分数 | `ZINCRBY rank:score 5 "张三"` |
| `ZREM key member` | 移除元素 | `ZREM rank:score "张三"` |

**典型场景**：

```bash
# 场景：排行榜
ZADD rank:score 95 "张三" 88 "李四" 92 "王五" 78 "赵六"
ZADD rank:score 99 "钱七"

# Top 3（降序）
ZREVRANGE rank:score 0 2 WITHSCORES
# 返回：1) "钱七" 2) "99" 3) "张三" 4) "95" 5) "王五" 6) "92"

# 查张三的排名（降序，从0开始）
ZREVRANK rank:score "张三"
# 返回：(integer) 1    → 第2名

# 张三加5分
ZINCRBY rank:score 5 "张三"
ZSCORE rank:score "张三"
# 返回："100"
```

**五种数据类型速查表**：

```
┌──────────┬──────────────────┬─────────────────────────────────┐
│  类型     │  核心特征         │  典型场景                        │
├──────────┼──────────────────┼─────────────────────────────────┤
│  String  │  KV，最基础       │  缓存、计数器、分布式锁           │
│  List    │  有序可重复       │  消息队列、最新列表               │
│  Set     │  无序不重复       │  共同关注、去重、抽奖             │
│  Hash    │  字段-值映射      │  对象存储、字段级修改             │
│  ZSet    │  有序不重复+分数  │  排行榜、延迟队列                │
└──────────┴──────────────────┴─────────────────────────────────┘
```

---

## 25.3 Spring Boot集成Redis

### 25.3.1 添加依赖

在`pom.xml`中添加：

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-data-redis</artifactId>
</dependency>

<!-- Lettuce连接池依赖（必须加！否则连接池配置不生效） -->
<dependency>
    <groupId>org.apache.commons</groupId>
    <artifactId>commons-pool2</artifactId>
</dependency>
```

### 25.3.2 连接配置

在`application.yml`中：

```yaml
spring:
  data:
    redis:
      host: 127.0.0.1
      port: 6379
      password: your_password        # 生产必须设密码
      database: 0                    # 默认使用0号数据库（0-15共16个）
      timeout: 3000ms                # 连接超时时间
      lettuce:                       # Lettuce客户端配置
        pool:
          max-active: 20             # 连接池最大连接数
          max-idle: 10               # 连接池最大空闲连接数
          min-idle: 5                # 连接池最小空闲连接数
          max-wait: 3000ms           # 连接池最大阻塞等待时间
```

**Lettuce vs Jedis**：

```
┌──────────────┬──────────────────────┬──────────────────────┐
│     维度      │      Lettuce         │       Jedis          │
├──────────────┼──────────────────────┼──────────────────────┤
│  线程安全     │  是（基于Netty）      │  否（多线程需池化）   │
│  连接方式     │  单连接+复用          │  每操作一个连接       │
│  异步支持     │  原生支持             │  不支持              │
│  Spring Boot │  默认选择 ✅          │  需手动切换           │
│  集群支持     │  完善                │  一般                │
└──────────────┴──────────────────────┴──────────────────────┘
```

Spring Boot 2.x+默认使用Lettuce，基于Netty实现异步非阻塞IO，单连接即可支持多线程并发访问。

> 🚨 **致命坑点：Lettuce连接池默认不开启！**
>
> 添加`spring-boot-starter-data-redis`后，Lettuce的连接池功能是**关闭**的。你必须：
> 1. 额外添加`commons-pool2`依赖
> 2. 在yaml中配置`spring.data.redis.lettuce.pool.*`
>
> 如果不加`commons-pool2`，配置了pool也不会报错——只是不生效！Lettuce会使用默认的单一连接，高并发下可能超时。

### 25.3.3 RedisTemplate vs StringRedisTemplate

Spring Boot自动配置了两个操作Redis的模板类：

| 类 | 泛型 | 序列化 | 适用场景 |
|----|------|--------|---------|
| `StringRedisTemplate` | `String, String` | String序列化 | 简单字符串操作 |
| `RedisTemplate<K,V>` | 泛型 | **JDK序列化**（默认） | 对象操作（需自定义序列化） |

**RedisTemplate操作五种数据类型**：

```java
@Autowired
private RedisTemplate<String, Object> redisTemplate;

@Autowired
private StringRedisTemplate stringRedisTemplate;

public void demo() {
    // String操作
    redisTemplate.opsForValue().set("user:name", "张三");
    String name = (String) redisTemplate.opsForValue().get("user:name");

    // Hash操作
    redisTemplate.opsForHash().put("user:1001", "name", "张三");
    redisTemplate.opsForHash().put("user:1001", "age", "28");
    Map<Object, Object> userMap = redisTemplate.opsForHash().entries("user:1001");

    // List操作
    redisTemplate.opsForList().leftPush("queue:email", "email:1001");
    redisTemplate.opsForList().rightPop("queue:email");

    // Set操作
    redisTemplate.opsForSet().add("tags:article:1", "Java", "Spring");
    Set<Object> tags = redisTemplate.opsForSet().members("tags:article:1");

    // ZSet操作
    redisTemplate.opsForZSet().add("rank:score", "张三", 95);
    Set<Object> top3 = redisTemplate.opsForZSet().reverseRange("rank:score", 0, 2);
}
```

### 25.3.4 JSON序列化配置（不用JDK序列化！）

> 🚨 **致命坑点：RedisTemplate默认使用JDK序列化**
>
> 默认的`RedisTemplate`使用`JdkSerializationRedisSerializer`，存入Redis的值是一堆不可读的二进制：
>
> ```
> \xac\xed\x00\x05sr\x00\x18com.example.entity.Employee\x8a...
> ```
>
> 这带来三个严重问题：
> 1. **不可读**——Redis-cli无法直接查看数据
> 2. **体积大**——JDK序列化包含大量类信息，比JSON大3-5倍
> 3. **跨语言障碍**——其他语言无法解析Java序列化数据
>
> **必须配置JSON序列化！**

**完整配置类**：

```java
@Configuration
public class RedisConfig {

    @Bean
    public RedisTemplate<String, Object> redisTemplate(RedisConnectionFactory factory) {
        RedisTemplate<String, Object> template = new RedisTemplate<>();
        template.setConnectionFactory(factory);

        // JSON序列化器（能保存类型信息，反序列化时还原为原始类型）
        GenericJackson2JsonRedisSerializer jsonSerializer =
                new GenericJackson2JsonRedisSerializer();

        // String序列化器
        StringRedisSerializer stringSerializer = new StringRedisSerializer();

        // Key使用String序列化
        template.setKeySerializer(stringSerializer);
        template.setHashKeySerializer(stringSerializer);

        // Value使用JSON序列化
        template.setValueSerializer(jsonSerializer);
        template.setHashValueSerializer(jsonSerializer);

        template.afterPropertiesSet();
        return template;
    }

    @Bean
    public CacheManager cacheManager(RedisConnectionFactory factory) {
        GenericJackson2JsonRedisSerializer jsonSerializer =
                new GenericJackson2JsonRedisSerializer();
        StringRedisSerializer stringSerializer = new StringRedisSerializer();

        RedisCacheConfiguration config = RedisCacheConfiguration.defaultCacheConfig()
                .entryTtl(Duration.ofMinutes(10))          // 默认缓存过期时间10分钟
                .serializeKeysWith(RedisSerializationContext.SerializationPair
                        .fromSerializer(stringSerializer))
                .serializeValuesWith(RedisSerializationContext.SerializationPair
                        .fromSerializer(jsonSerializer))
                .disableCachingNullValues();                // 不缓存null值

        return RedisCacheManager.builder(factory)
                .cacheDefaults(config)
                .build();
    }
}
```

配置后Redis中存储的数据变成了可读的JSON：

```json
{
  "@class": "com.example.springbootdemo.entity.Employee",
  "id": 1001,
  "name": "张三",
  "age": 28,
  "department": "技术部",
  "salary": 15000.00
}
```

> 🚨 **坑点：JSON序列化需要无参构造方法 + getter/setter**
>
> `GenericJackson2JsonRedisSerializer`使用Jackson进行序列化/反序列化。你的实体类**必须**有无参构造方法（Lombok `@Data`/`@NoArgsConstructor`会自动生成），否则反序列化时报错：
>
> ```java
> // ❌ 没有无参构造方法 → 反序列化失败
> public class Employee {
>     private final Long id;
>     public Employee(Long id) { this.id = id; }
> }
>
> // ✅ 正确：Lombok自动生成无参构造
> @Data
> @NoArgsConstructor
> public class Employee {
>     private Long id;
>     private String name;
> }
> ```

---

## 25.4 Spring Cache

Spring Cache是Spring提供的缓存抽象层，通过注解实现声明式缓存——你不需要手动调用`redisTemplate`，只需在方法上加注解，框架自动完成缓存的读取和写入。

### 25.4.1 启用缓存

在启动类上添加`@EnableCaching`：

```java
@SpringBootApplication
@EnableCaching
public class Application {
    public static void main(String[] args) {
        SpringApplication.run(Application.class, args);
    }
}
```

### 25.4.2 @Cacheable — 查缓存，没有则执行方法并存缓存

`@Cacheable`是最核心的缓存注解：方法调用前先查缓存，缓存命中则直接返回，不执行方法；缓存未命中则执行方法，将返回值存入缓存。

```java
@Service
@Slf4j
public class EmployeeService {

    @Autowired
    private EmployeeMapper employeeMapper;

    @Cacheable(value = "employee", key = "#id")
    public Employee getById(Long id) {
        log.info("查询数据库，id={}", id);   // 缓存命中时这行不会执行
        return employeeMapper.selectById(id);
    }
}
```

**第一次调用**（缓存未命中）：

```
查询数据库，id=1001    ← 执行了方法
返回：Employee(id=1001, name=张三, ...)
```

**第二次调用**（缓存命中）：

```
（没有日志输出）        ← 方法没执行，直接从Redis返回
返回：Employee(id=1001, name=张三, ...)
```

**注解属性详解**：

| 属性 | 说明 | 示例 |
|------|------|------|
| `value`/`cacheNames` | 缓存命名空间 | `"employee"` |
| `key` | 缓存key（SpEL表达式） | `"#id"`、`"#result.id"` |
| `condition` | 满足条件才缓存 | `"#id > 0"` |
| `unless` | 满足条件不缓存 | `"#result == null"` |
| `sync` | 同步模式（防击穿） | `true` |

> 🚨 **坑点：同类内部调用不走代理 → 缓存不生效**
>
> 这和第11章AOP失效是同一个原因——Spring Cache基于AOP代理实现，同类内部方法调用不走代理：
>
> ```java
> @Service
> public class EmployeeService {
>
>     public Employee getEmployee(Long id) {
>         return getById(id);    // ❌ 内部调用，@Cacheable不生效！
>     }
>
>     @Cacheable(value = "employee", key = "#id")
>     public Employee getById(Long id) {
>         return employeeMapper.selectById(id);
>     }
> }
> ```
>
> 解决方案：拆到不同类，或用`AopContext.currentProxy()`获取代理对象。

> 🚨 **坑点：缓存null值 → 穿透漏洞**
>
> 如果方法返回null，默认也会缓存null值。这会带来两个问题：
> 1. 浪费Redis内存存储大量null
> 2. 数据库中后来插入了这条数据，但缓存还是null → 数据不一致
>
> **用`unless`排除null值**：
>
> ```java
> @Cacheable(value = "employee", key = "#id", unless = "#result == null")
> public Employee getById(Long id) {
>     return employeeMapper.selectById(id);
> }
> ```
>
> 或者在CacheManager配置中全局禁用null缓存（我们上面的配置已经加了`.disableCachingNullValues()`）。

### 25.4.3 @CachePut — 总是执行方法并更新缓存

`@CachePut`不管缓存有没有，**总是执行方法**，然后用返回值更新缓存。适用于更新操作。

```java
@CachePut(value = "employee", key = "#result.id")
public Employee update(Employee employee) {
    employeeMapper.updateById(employee);
    return employee;     // 返回值会存入缓存
}
```

**注意**：`@CachePut`的`key`通常用`#result.id`（返回值的属性），而不是`#employee.id`——因为参数对象的id可能为null（新增场景），而返回值一定有id。

### 25.4.4 @CacheEvict — 删除缓存

`@CacheEvict`用于删除缓存，通常在删除或更新数据时使用。

```java
// 删除指定key的缓存
@CacheEvict(value = "employee", key = "#id")
public void deleteById(Long id) {
    employeeMapper.deleteById(id);
}

// 清空整个缓存命名空间
@CacheEvict(value = "employee", allEntries = true)
public void clearAllCache() {
    // 方法体不需要操作缓存，注解会自动清空
}
```

| 属性 | 说明 |
|------|------|
| `allEntries` | 是否清空整个缓存命名空间（默认false） |
| `beforeInvocation` | 是否在方法执行前清缓存（默认false） |

> 🚨 **坑点：allEntries=true 清空整个缓存命名空间 → 误伤其他缓存**
>
> `allEntries = true`会删除`employee`命名空间下**所有**缓存key，不仅仅是当前方法相关的。如果你只想删一条，用`key`精确指定。
>
> 🚨 **坑点：方法执行前清缓存 vs 执行后清缓存**
>
> - `beforeInvocation = false`（默认）：方法执行**后**删缓存。如果方法抛异常，缓存不会被删除。
> - `beforeInvocation = true`：方法执行**前**删缓存。即使方法失败，缓存也已删除。
>
> 推荐使用默认值（方法后删），因为方法失败时数据没变，缓存不应删除。

### 25.4.5 @Caching — 组合多缓存操作

当一个方法需要同时操作多个缓存时，用`@Caching`组合：

```java
@Caching(
    put = @CachePut(value = "employee", key = "#result.id"),
    evict = @CacheEvict(value = "employee:list", allEntries = true)
)
public Employee update(Employee employee) {
    employeeMapper.updateById(employee);
    return employee;
}
```

### 25.4.6 完整CRUD缓存示例

```java
@Service
@Slf4j
public class EmployeeService {

    @Autowired
    private EmployeeMapper employeeMapper;

    @Cacheable(value = "employee", key = "#id", unless = "#result == null")
    public Employee getById(Long id) {
        log.info("查询数据库，id={}", id);
        return employeeMapper.selectById(id);
    }

    @Cacheable(value = "employee:list", key = "#query.toString()")
    public List<Employee> list(EmployeeQuery query) {
        log.info("查询数据库，条件={}", query);
        return employeeMapper.selectList(query);
    }

    @CachePut(value = "employee", key = "#result.id")
    @CacheEvict(value = "employee:list", allEntries = true)
    public Employee update(Employee employee) {
        employeeMapper.updateById(employee);
        return employee;
    }

    @CacheEvict(value = {"employee", "employee:list"}, key = "#id")
    @CacheEvict(value = "employee:list", allEntries = true)
    public void deleteById(Long id) {
        employeeMapper.deleteById(id);
    }
}
```

> 🚨 **坑点：缓存过期时间不在注解中配置！**
>
> Spring Cache的注解**没有**过期时间属性。过期时间在CacheManager中统一配置：
>
> ```yaml
> spring:
>   cache:
>     redis:
>       time-to-live: 600000    # 毫秒，10分钟
>   ```
>
> 如果不同缓存需要不同过期时间，在CacheManager中为每个缓存名配置：
>
> ```java
> @Bean
> public CacheManager cacheManager(RedisConnectionFactory factory) {
>     RedisCacheConfiguration defaultConfig = RedisCacheConfiguration.defaultCacheConfig()
>             .entryTtl(Duration.ofMinutes(10))
>             .serializeKeysWith(RedisSerializationContext.SerializationPair
>                     .fromSerializer(new StringRedisSerializer()))
>             .serializeValuesWith(RedisSerializationContext.SerializationPair
>                     .fromSerializer(new GenericJackson2JsonRedisSerializer()))
>             .disableCachingNullValues();
>
>     Map<String, RedisCacheConfiguration> cacheConfigurations = new HashMap<>();
>     cacheConfigurations.put("employee", defaultConfig.entryTtl(Duration.ofMinutes(30)));
>     cacheConfigurations.put("employee:list", defaultConfig.entryTtl(Duration.ofMinutes(5)));
>
>     return RedisCacheManager.builder(factory)
>             .cacheDefaults(defaultConfig)
>             .withInitialCacheConfigurations(cacheConfigurations)
>             .build();
> }
> ```

---

## 25.5 缓存三大问题（面试必考）

缓存穿透、击穿、雪崩是缓存系统的三大经典问题，面试几乎必问。每种问题我们都按"概念图→问题代码→解决方案代码"的顺序展开。

### 25.5.1 缓存穿透

**概念**：查询一个**数据库中根本不存在**的数据，缓存中没有，数据库中也没有，每次请求都会穿透缓存直达数据库。

```
缓存穿透时序图：

请求1 (id=99999，不存在)          请求2 (id=99999)           请求3 (id=99999)
    │                                │                         │
    ▼                                ▼                         ▼
┌─────────┐  miss  ┌─────────┐  miss  ┌─────────┐  miss  ┌─────────┐
│  Redis  │ ────► │  Redis  │ ────► │  Redis  │ ────► │  Redis  │
└─────────┘       └─────────┘       └─────────┘       └─────────┘
    │                 │                  │                  │
    ▼                 ▼                  ▼                  ▼
┌─────────┐      ┌─────────┐       ┌─────────┐       ┌─────────┐
│  MySQL  │      │  MySQL  │       │  MySQL  │       │  MySQL  │
│ (无数据) │      │ (无数据) │       │ (无数据) │       │ (无数据) │
└─────────┘      └─────────┘       └─────────┘       └─────────┘

→ 每次请求都打到MySQL，Redis形同虚设！
```

**问题代码**（无防护）：

```java
public Employee getById(Long id) {
    // 1. 查缓存
    String key = "employee:" + id;
    Employee employee = (Employee) redisTemplate.opsForValue().get(key);
    if (employee != null) {
        return employee;
    }
    // 2. 缓存未命中，查数据库
    employee = employeeMapper.selectById(id);
    if (employee != null) {
        redisTemplate.opsForValue().set(key, employee, 30, TimeUnit.MINUTES);
    }
    // 3. employee为null时不缓存 → 下次还会查DB → 穿透！
    return employee;
}
```

**解决方案1：缓存null值（短过期）**

```java
public Employee getByIdWithNullCache(Long id) {
    String key = "employee:" + id;
    Employee employee = (Employee) redisTemplate.opsForValue().get(key);
    if (employee != null) {
        return employee;
    }

    // 检查是否是null标记（防止和真实null混淆）
    String nullKey = "employee:null:" + id;
    if (Boolean.TRUE.equals(redisTemplate.hasKey(nullKey))) {
        return null;    // 之前查过，确认不存在
    }

    employee = employeeMapper.selectById(id);
    if (employee != null) {
        redisTemplate.opsForValue().set(key, employee, 30, TimeUnit.MINUTES);
    } else {
        // 缓存null标记，短过期（3-5分钟），避免长期占用内存
        redisTemplate.opsForValue().set(nullKey, "", 3, TimeUnit.MINUTES);
    }
    return employee;
}
```

> 🚨 **坑点：null值太多占内存**
>
> 如果攻击者用大量不同id请求，每个id都会在Redis中存一个null标记，导致Redis内存暴增。解决方案：
> 1. null值过期时间设短（3-5分钟）
> 2. 对请求参数做校验（id格式不合法直接拒绝）
> 3. 使用布隆过滤器（终极方案）

**解决方案2：布隆过滤器（终极方案）**

布隆过滤器的核心思想：**用一个空间效率极高的数据结构，判断某个元素"一定不存在"或"可能存在"**。

```
布隆过滤器原理：

位数组（初始全0）：[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

添加元素"张三"：
  hash1("张三") = 3  → 位数组[3] = 1
  hash2("张三") = 7  → 位数组[7] = 1
  hash3("张三") = 11 → 位数组[11] = 1
  结果：[0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1]

查询"李四"是否存在：
  hash1("李四") = 2  → 位数组[2] = 0  → "李四"一定不存在 ✅

查询"王五"是否存在：
  hash1("王五") = 3  → 位数组[3] = 1
  hash2("王五") = 7  → 位数组[7] = 1
  hash3("王五") = 11 → 位数组[11] = 1
  → "王五"可能存在（也可能是hash冲突）⚠️

结论：说"不存在" → 一定不存在；说"存在" → 可能存在
```

使用Redisson实现布隆过滤器：

```xml
<!-- pom.xml添加Redisson依赖 -->
<dependency>
    <groupId>org.redisson</groupId>
    <artifactId>redisson-spring-boot-starter</artifactId>
    <version>3.27.0</version>
</dependency>
```

```java
@Configuration
public class BloomFilterConfig {

    @Bean
    public RBloomFilter<Long> employeeBloomFilter(RedissonClient redissonClient) {
        RBloomFilter<Long> bloomFilter = redissonClient.getBloomFilter("employee:bloom");
        // 参数：预期插入数量100000，误判率0.01（1%）
        bloomFilter.tryInit(100000L, 0.01);
        return bloomFilter;
    }
}
```

```java
@Service
@Slf4j
public class EmployeeService {

    @Autowired
    private RBloomFilter<Long> employeeBloomFilter;

    @Autowired
    private RedisTemplate<String, Object> redisTemplate;

    @Autowired
    private EmployeeMapper employeeMapper;

    public Employee getByIdWithBloomFilter(Long id) {
        // 第1层：布隆过滤器判断（一定不存在 → 直接返回null）
        if (!employeeBloomFilter.contains(id)) {
            log.info("布隆过滤器拦截，id={}不存在", id);
            return null;
        }

        // 第2层：查Redis缓存
        String key = "employee:" + id;
        Employee employee = (Employee) redisTemplate.opsForValue().get(key);
        if (employee != null) {
            return employee;
        }

        // 第3层：查数据库
        employee = employeeMapper.selectById(id);
        if (employee != null) {
            redisTemplate.opsForValue().set(key, employee, 30, TimeUnit.MINUTES);
        }
        return employee;
    }

    // 新增员工时，同步更新布隆过滤器
    public void addEmployee(Employee employee) {
        employeeMapper.insert(employee);
        employeeBloomFilter.add(employee.getId());
    }
}
```

> 🚨 **坑点：布隆过滤器的两个限制**
>
> 1. **有误判率**：说"存在"可能不存在（hash冲突），说"不存在"一定不存在。误判率越低，占用空间越大。
> 2. **不能删除元素**：因为多个元素可能映射到同一个位，删除一个会影响其他元素。如果需要删除，用Counting Bloom Filter（每个位用计数器替代）。

### 25.5.2 缓存击穿

**概念**：某个**热点key**过期的瞬间，大量并发请求同时发现缓存失效，全部涌向数据库重建缓存。

```
缓存击穿时序图：

时间线 ──────────────────────────────────────────────────►

T1: 热点key过期
    │
T2: 1000个并发请求同时发现缓存miss
    │    │    │    │    │    │    │    │
    ▼    ▼    ▼    ▼    ▼    ▼    ▼    ▼
  ┌──────────────────────────────────────┐
  │          1000个请求同时查MySQL        │  ← 数据库瞬间压力暴增！
  └──────────────────────────────────────┘

T3: 1000个请求都查到结果，都写缓存（重复写999次）
```

**问题代码**（无防护）：

```java
@Cacheable(value = "employee", key = "#id")
public Employee getById(Long id) {
    // 热点key过期时，大量线程同时执行到这里
    return employeeMapper.selectById(id);  // 1000个线程同时查DB！
}
```

**解决方案1：互斥锁（SETNX）**

只允许一个线程查DB重建缓存，其他线程等待后读缓存即可：

```java
public Employee getByIdWithMutex(Long id) {
    String key = "employee:" + id;
    String lockKey = "lock:employee:" + id;

    // 第1次查缓存
    Employee employee = (Employee) redisTemplate.opsForValue().get(key);
    if (employee != null) {
        return employee;
    }

    // 缓存未命中，尝试获取互斥锁
    try {
        Boolean locked = redisTemplate.opsForValue()
                .setIfAbsent(lockKey, "1", 10, TimeUnit.SECONDS);
        if (Boolean.TRUE.equals(locked)) {
            // 获取锁成功 → 双重检查（DCL）
            employee = (Employee) redisTemplate.opsForValue().get(key);
            if (employee != null) {
                return employee;    // 其他线程已经重建了缓存
            }

            // 查数据库
            employee = employeeMapper.selectById(id);
            if (employee != null) {
                redisTemplate.opsForValue().set(key, employee, 30, TimeUnit.MINUTES);
            }
        } else {
            // 获取锁失败 → 短暂等待后重试
            Thread.sleep(50);
            return getByIdWithMutex(id);    // 递归重试（实际项目用循环+最大重试次数）
        }
    } catch (InterruptedException e) {
        Thread.currentThread().interrupt();
    } finally {
        redisTemplate.delete(lockKey);    // 释放锁
    }
    return employee;
}
```

**双重检查（DCL）的意义**：获取锁后再次查缓存——因为在你等锁的期间，其他线程可能已经重建了缓存，不需要再查DB。

**解决方案2：逻辑过期（永不过期 + 异步更新）**

缓存永不过期，但在Value中嵌入逻辑过期时间。查询时发现逻辑过期，返回旧数据的同时异步更新：

```java
@Data
public class CacheData<T> {
    private T data;
    private LocalDateTime expireTime;    // 逻辑过期时间
}
```

```java
@Service
@Slf4j
public class EmployeeService {

    @Autowired
    private RedisTemplate<String, Object> redisTemplate;

    @Autowired
    private EmployeeMapper employeeMapper;

    @Autowired
    private ThreadPoolExecutor cacheRebuildExecutor;

    public Employee getByIdWithLogicalExpire(Long id) {
        String key = "employee:logical:" + id;
        CacheData<Employee> cacheData = (CacheData<Employee>) redisTemplate.opsForValue().get(key);

        // 缓存不存在（非热点数据，不走逻辑过期方案）
        if (cacheData == null) {
            return null;
        }

        // 未逻辑过期 → 直接返回
        if (cacheData.getExpireTime().isAfter(LocalDateTime.now())) {
            return cacheData.getData();
        }

        // 已逻辑过期 → 异步重建缓存
        String lockKey = "lock:employee:rebuild:" + id;
        Boolean locked = redisTemplate.opsForValue()
                .setIfAbsent(lockKey, "1", 10, TimeUnit.SECONDS);
        if (Boolean.TRUE.equals(locked)) {
            // 获取锁成功 → 提交异步重建任务
            cacheRebuildExecutor.submit(() -> {
                try {
                    Employee employee = employeeMapper.selectById(id);
                    CacheData<Employee> newData = new CacheData<>();
                    newData.setData(employee);
                    newData.setExpireTime(LocalDateTime.now().plusMinutes(30));
                    redisTemplate.opsForValue().set(key, newData);
                } finally {
                    redisTemplate.delete(lockKey);
                }
            });
        }

        // 无论是否获取锁，都返回旧数据（保证高可用）
        return cacheData.getData();
    }
}
```

**两种方案对比**：

```
┌──────────────┬──────────────────────┬──────────────────────┐
│     维度      │    互斥锁方案         │   逻辑过期方案        │
├──────────────┼──────────────────────┼──────────────────────┤
│  数据一致性   │  强一致（重建后返回）  │  短暂不一致（返回旧值）│
│  性能影响     │  等锁期间有短暂延迟   │  几乎无影响           │
│  实现复杂度   │  中等                │  较高（需异步线程池）  │
│  适用场景     │  一致性要求高         │  高并发、可容忍旧数据  │
│  额外风险     │  死锁（锁未释放）     │  线程池耗尽           │
└──────────────┴──────────────────────┴──────────────────────┘
```

> 🚨 **坑点：互斥锁方案会有短暂性能下降**
>
> 互斥锁方案在缓存重建期间，其他线程需要等待，QPS会有短暂下降。但这是保证数据一致性的代价。如果业务能容忍短暂不一致，选逻辑过期方案。

### 25.5.3 缓存雪崩

**概念**：大量缓存key**同时过期**，或Redis服务宕机，导致大量请求同时打到数据库，数据库压力暴增甚至崩溃。

```
缓存雪崩时序图：

T0: 批量导入10000条员工数据，都设了30分钟过期
    │
T0+30min: 10000个key同时过期！
    │
    ▼
┌──────────────────────────────────────────────────────┐
│  10000个请求同时miss → 10000个请求同时查MySQL         │
│  MySQL: "我扛不住了！" 💥                             │
└──────────────────────────────────────────────────────┘
```

**解决方案1：过期时间加随机值**

```java
// ❌ 所有缓存相同过期时间 → 同时过期 → 雪崩
redisTemplate.opsForValue().set(key, value, 30, TimeUnit.MINUTES);

// ✅ 过期时间加随机偏移（±30%）
Random random = new Random();
long baseTtl = 30;
long randomTtl = baseTtl + random.nextInt((int) (baseTtl * 0.6)) - (int) (baseTtl * 0.3);
// randomTtl范围：30 - 9 = 21分钟 ~ 30 + 9 = 39分钟
redisTemplate.opsForValue().set(key, value, randomTtl, TimeUnit.MINUTES);
```

在Spring Cache中，可以通过自定义CacheManager实现随机TTL：

```java
@Bean
public CacheManager cacheManager(RedisConnectionFactory factory) {
    RedisCacheConfiguration defaultConfig = RedisCacheConfiguration.defaultCacheConfig()
            .computePrefixWith(CacheKeyPrefix.simple())
            .serializeKeysWith(RedisSerializationContext.SerializationPair
                    .fromSerializer(new StringRedisSerializer()))
            .serializeValuesWith(RedisSerializationContext.SerializationPair
                    .fromSerializer(new GenericJackson2JsonRedisSerializer()))
            .disableCachingNullValues()
            .entryTtl(Duration.ofMinutes(10 + ThreadLocalRandom.current().nextLong(5)));
    // TTL在10~15分钟之间随机

    return RedisCacheManager.builder(factory)
            .cacheDefaults(defaultConfig)
            .build();
}
```

**解决方案2：多级缓存（本地Caffeine + 远程Redis）**

```
请求 → L1 Caffeine(本地) → L2 Redis(远程) → MySQL
         命中率60%           命中率35%         命中率5%

Redis宕机 → Caffeine仍能挡住60%的请求 → MySQL压力可控
```

添加Caffeine依赖：

```xml
<dependency>
    <groupId>com.github.ben-manes.caffeine</groupId>
    <artifactId>caffeine</artifactId>
</dependency>
```

```java
@Configuration
public class MultiLevelCacheConfig {

    @Bean
    public Cache<Long, Employee> localCache() {
        return Caffeine.newBuilder()
                .maximumSize(1000)
                .expireAfterWrite(Duration.ofMinutes(5))
                .build();
    }
}
```

```java
@Service
@Slf4j
public class EmployeeService {

    @Autowired
    private Cache<Long, Employee> localCache;

    @Autowired
    private RedisTemplate<String, Object> redisTemplate;

    @Autowired
    private EmployeeMapper employeeMapper;

    public Employee getByIdMultiLevel(Long id) {
        // L1: 本地缓存
        Employee employee = localCache.getIfPresent(id);
        if (employee != null) {
            log.debug("L1缓存命中，id={}", id);
            return employee;
        }

        // L2: Redis缓存
        String key = "employee:" + id;
        employee = (Employee) redisTemplate.opsForValue().get(key);
        if (employee != null) {
            log.debug("L2缓存命中，id={}", id);
            localCache.put(id, employee);
            return employee;
        }

        // L3: 数据库
        log.debug("查询数据库，id={}", id);
        employee = employeeMapper.selectById(id);
        if (employee != null) {
            redisTemplate.opsForValue().set(key, employee, 30, TimeUnit.MINUTES);
            localCache.put(id, employee);
        }
        return employee;
    }
}
```

**解决方案3：限流降级**

当缓存大面积失效时，对数据库查询请求进行限流，超出阈值的请求直接返回降级数据（如"系统繁忙，请稍后重试"）。可使用Sentinel或Hystrix实现——此阶段理解概念即可，后续深入学习。

### 25.5.4 数据一致性

缓存和数据库是两个独立的数据存储，如何保证它们之间的数据一致性是缓存系统的核心难题。

> 🚨 **坑点：先删缓存还是先更新数据库？**

**方案A：先删缓存，再更新数据库（❌ 有问题）**

```
时间线    线程A（更新）              线程B（读取）
  T1     删除缓存(employee:1001)
  T2                               查缓存 → miss
  T3                               查数据库 → 旧值
  T4                               写缓存(旧值) ← 脏数据写回！
  T5     更新数据库(新值)

结果：数据库是新值，缓存是旧值 → 不一致！直到缓存过期才能恢复
```

**方案B：先更新数据库，再删缓存（✅ 推荐）**

```
时间线    线程A（更新）              线程B（读取）
  T1     更新数据库(新值)
  T2                               查缓存 → 旧值（短暂不一致）
  T3     删除缓存(employee:1001)
  T4                               下次查询 → miss → 查DB → 新值

结果：只有T2~T3之间有短暂不一致，影响极小
```

**方案B的极端情况**（概率极低但存在）：

```
时间线    线程A（读取）              线程B（更新）
  T1     查缓存 → miss
  T2     查数据库 → 旧值
  T3                               更新数据库(新值)
  T4                               删除缓存
  T5     写缓存(旧值) ← 脏数据！

条件极其苛刻：T1 miss + T2读到旧值 + T3~T4在T5之前完成 + T5写入旧值
实际概率极低（读操作远快于写操作），但不是零
```

**终极方案：先更新DB + 再删缓存 + 延迟双删**

```java
@Service
@Slf4j
public class EmployeeService {

    @Autowired
    private EmployeeMapper employeeMapper;

    @Autowired
    private RedisTemplate<String, Object> redisTemplate;

    @Transactional
    public void updateWithDoubleDelete(Employee employee) {
        // 1. 更新数据库
        employeeMapper.updateById(employee);

        // 2. 第一次删除缓存
        String key = "employee:" + employee.getId();
        redisTemplate.delete(key);

        // 3. 延迟第二次删除（异步执行，避免阻塞当前线程）
        CompletableFuture.runAsync(() -> {
            try {
                Thread.sleep(500);    // 延迟500ms，等待可能存在的脏缓存写入完成
                redisTemplate.delete(key);
                log.info("延迟双删完成，key={}", key);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        });
    }
}
```

**延迟双删的原理**：第一次删除后，如果有线程在读旧数据并准备写回缓存，延迟500ms后第二次删除会把那个脏缓存清掉。500ms的选择取决于你的业务读操作耗时——一般读操作不会超过500ms。

**Canal订阅binlog异步更新缓存**（了解即可）：Canal是阿里巴巴开源的MySQL binlog增量订阅组件，可以监听数据库变更事件，自动更新或删除对应缓存。这是大型系统中保证缓存一致性的主流方案，但引入了额外的组件复杂度。

---

## 25.6 分布式锁

### 25.6.1 为什么需要分布式锁

在单机环境下，Java的`synchronized`或`ReentrantLock`可以保证互斥。但在分布式系统中，多个服务实例各自有独立的JVM，`synchronized`只能锁住单个JVM内的线程，无法跨实例互斥。

```
单机环境：                    分布式环境：

┌──────────────────┐         ┌──────────┐  ┌──────────┐  ┌──────────┐
│    JVM           │         │  实例A    │  │  实例B    │  │  实例C    │
│  ┌───┐ ┌───┐    │         │ JVM      │  │ JVM      │  │ JVM      │
│  │T1 │ │T2 │    │         │ ┌───┐    │  │ ┌───┐    │  │ ┌───┐    │
│  └─┬─┘ └─┬─┘    │         │ │T1 │    │  │ │T2 │    │  │ │T3 │    │
│    │     │      │         │ └─┬─┘    │  │ └─┬─┘    │  │ └─┬─┘    │
│    ▼     ▼      │         │   │      │  │   │      │  │   │      │
│  synchronized ✅ │         │   ▼      │  │   ▼      │  │   ▼      │
│  (同一把锁)      │         │  ❌各锁各的  ❌各锁各的  ❌各锁各的   │
└──────────────────┘         └──────────┘  └──────────┘  └──────────┘
                             → 需要Redis分布式锁，锁在Redis中，所有实例共享！
```

### 25.6.2 Redisson集成

Redisson是Redis的Java驻内存数据网格客户端，提供了丰富的分布式对象和服务，包括分布式锁。

```xml
<dependency>
    <groupId>org.redisson</groupId>
    <artifactId>redisson-spring-boot-starter</artifactId>
    <version>3.27.0</version>
</dependency>
```

```yaml
# application.yml
spring:
  redis:
    redisson:
      file: classpath:redisson.yml    # 或直接在spring.data.redis下配置
```

或者使用`redisson.yml`：

```yaml
# redisson.yml
singleServerConfig:
  address: "redis://127.0.0.1:6379"
  password: your_password
  database: 0
  connectionPoolSize: 20
  connectionMinimumIdleSize: 5
```

### 25.6.3 RLock基本使用

```java
@Service
@Slf4j
public class OrderService {

    @Autowired
    private RedissonClient redissonClient;

    public void submitOrder(Long orderId) {
        RLock lock = redissonClient.getLock("lock:order:" + orderId);
        try {
            // tryLock参数：等待时间10秒，锁自动释放时间30秒
            boolean acquired = lock.tryLock(10, 30, TimeUnit.SECONDS);
            if (acquired) {
                // 业务逻辑：检查库存、创建订单、扣减库存
                log.info("获取锁成功，处理订单orderId={}", orderId);
                doCreateOrder(orderId);
            } else {
                log.warn("获取锁失败，订单正在处理中orderId={}", orderId);
                throw new BusinessException("请勿重复提交");
            }
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            throw new BusinessException("操作被中断");
        } finally {
            // 释放锁前必须判断是否是当前线程持有
            if (lock.isHeldByCurrentThread()) {
                lock.unlock();
            }
        }
    }

    private void doCreateOrder(Long orderId) {
        // 订单创建逻辑...
    }
}
```

> 🚨 **致命坑点：忘记unlock → 死锁**
>
> 如果获取锁后方法抛异常，`unlock()`不会执行，锁要等到30秒超时才释放。**必须用try-finally保证锁释放**。
>
> 🚨 **致命坑点：unlock前不判断isHeldByCurrentThread() → IllegalMonitorStateException**
>
> 如果锁已经超时释放（业务执行超过30秒），再调用`unlock()`会抛`IllegalMonitorStateException`——你试图释放一个已经不属于你的锁。**必须在unlock前判断`lock.isHeldByCurrentThread()`**。

### 25.6.4 看门狗机制

Redisson的看门狗（Watchdog）是分布式锁的精妙设计：

- `lock.lock()`不指定leaseTime时，默认锁30秒，但Redisson会每10秒（1/3超时时间）自动续期
- 只要持有锁的客户端还活着，锁就不会过期
- 客户端宕机 → 看门狗停止续期 → 锁30秒后自动释放

```java
// 方式1：使用看门狗（推荐，不指定leaseTime）
lock.lock();    // 默认30秒，看门狗自动续期

// 方式2：指定leaseTime（看门狗不生效！）
lock.lock(30, TimeUnit.SECONDS);    // 30秒后强制释放，不续期

// 方式3：tryLock + 看门狗
boolean acquired = lock.tryLock(10, -1, TimeUnit.SECONDS);
// waitTime=10秒等待，leaseTime=-1使用看门狗
```

> 🚨 **坑点：指定leaseTime后看门狗不生效**
>
> `lock.lock(30, TimeUnit.SECONDS)`或`lock.tryLock(10, 30, TimeUnit.SECONDS)`中指定了leaseTime，Redisson认为你明确知道锁要持有多久，就不会启动看门狗。如果业务执行时间不确定，**不要指定leaseTime，让看门狗自动续期**。

### 25.6.5 Redisson其他锁简介

| 锁类型 | 说明 | 使用场景 |
|--------|------|---------|
| 可重入锁 | `getLock()`，同一线程可多次获取 | 最常用，默认 |
| 公平锁 | `getFairLock()`，按请求顺序获取 | 需要公平调度的场景 |
| 读写锁 | `getReadWriteLock()`，读共享写互斥 | 读多写少场景 |
| 联锁 | `getMultiLock()`，同时锁多个key | 跨资源事务 |

---

## EMS v8：缓存优化版

在EMS v7（安全+JWT版）的基础上，为员工查询接口加缓存、防穿透/击穿、加Redis分布式锁防重复提交。

### 新增依赖

```xml
<!-- Redis -->
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-data-redis</artifactId>
</dependency>
<dependency>
    <groupId>org.apache.commons</groupId>
    <artifactId>commons-pool2</artifactId>
</dependency>

<!-- Redisson -->
<dependency>
    <groupId>org.redisson</groupId>
    <artifactId>redisson-spring-boot-starter</artifactId>
    <version>3.27.0</version>
</dependency>

<!-- Caffeine本地缓存 -->
<dependency>
    <groupId>com.github.ben-manes.caffeine</groupId>
    <artifactId>caffeine</artifactId>
</dependency>
```

### Redis配置

```yaml
spring:
  data:
    redis:
      host: 127.0.0.1
      port: 6379
      password: your_password
      database: 0
      timeout: 3000ms
      lettuce:
        pool:
          max-active: 20
          max-idle: 10
          min-idle: 5
          max-wait: 3000ms
  cache:
    redis:
      time-to-live: 600000    # 默认10分钟
  redis:
    redisson:
      file: classpath:redisson.yml
```

### RedisConfig配置类

```java
@Configuration
public class RedisConfig {

    @Bean
    public RedisTemplate<String, Object> redisTemplate(RedisConnectionFactory factory) {
        RedisTemplate<String, Object> template = new RedisTemplate<>();
        template.setConnectionFactory(factory);

        GenericJackson2JsonRedisSerializer jsonSerializer =
                new GenericJackson2JsonRedisSerializer();
        StringRedisSerializer stringSerializer = new StringRedisSerializer();

        template.setKeySerializer(stringSerializer);
        template.setHashKeySerializer(stringSerializer);
        template.setValueSerializer(jsonSerializer);
        template.setHashValueSerializer(jsonSerializer);

        template.afterPropertiesSet();
        return template;
    }

    @Bean
    public CacheManager cacheManager(RedisConnectionFactory factory) {
        GenericJackson2JsonRedisSerializer jsonSerializer =
                new GenericJackson2JsonRedisSerializer();
        StringRedisSerializer stringSerializer = new StringRedisSerializer();

        RedisCacheConfiguration defaultConfig = RedisCacheConfiguration.defaultCacheConfig()
                .entryTtl(Duration.ofMinutes(10))
                .serializeKeysWith(RedisSerializationContext.SerializationPair
                        .fromSerializer(stringSerializer))
                .serializeValuesWith(RedisSerializationContext.SerializationPair
                        .fromSerializer(jsonSerializer))
                .disableCachingNullValues();

        Map<String, RedisCacheConfiguration> cacheConfigurations = new HashMap<>();
        cacheConfigurations.put("employee", defaultConfig.entryTtl(Duration.ofMinutes(30)));
        cacheConfigurations.put("employee:list", defaultConfig.entryTtl(Duration.ofMinutes(5)));

        return RedisCacheManager.builder(factory)
                .cacheDefaults(defaultConfig)
                .withInitialCacheConfigurations(cacheConfigurations)
                .build();
    }

    @Bean
    public RBloomFilter<Long> employeeBloomFilter(RedissonClient redissonClient) {
        RBloomFilter<Long> bloomFilter = redissonClient.getBloomFilter("employee:bloom");
        bloomFilter.tryInit(100000L, 0.01);
        return bloomFilter;
    }

    @Bean
    public Cache<Long, Employee> localCache() {
        return Caffeine.newBuilder()
                .maximumSize(1000)
                .expireAfterWrite(Duration.ofMinutes(5))
                .build();
    }
}
```

### EmployeeService缓存优化版

```java
@Service
@Slf4j
public class EmployeeService {

    @Autowired
    private EmployeeMapper employeeMapper;

    @Autowired
    private RedisTemplate<String, Object> redisTemplate;

    @Autowired
    private RedissonClient redissonClient;

    @Autowired
    private RBloomFilter<Long> employeeBloomFilter;

    @Autowired
    private Cache<Long, Employee> localCache;

    @Cacheable(value = "employee", key = "#id", unless = "#result == null")
    public Employee getById(Long id) {
        if (!employeeBloomFilter.contains(id)) {
            log.info("布隆过滤器拦截，id={}不存在", id);
            return null;
        }
        log.info("查询数据库，id={}", id);
        return employeeMapper.selectById(id);
    }

    @Cacheable(value = "employee:list", key = "#query.toString()")
    public List<Employee> list(EmployeeQuery query) {
        log.info("查询数据库，条件={}", query);
        return employeeMapper.selectList(query);
    }

    @CachePut(value = "employee", key = "#result.id")
    @CacheEvict(value = "employee:list", allEntries = true)
    public Employee update(Employee employee) {
        employeeMapper.updateById(employee);
        localCache.invalidate(employee.getId());
        return employee;
    }

    @Caching(evict = {
        @CacheEvict(value = "employee", key = "#id"),
        @CacheEvict(value = "employee:list", allEntries = true)
    })
    public void deleteById(Long id) {
        employeeMapper.deleteById(id);
        localCache.invalidate(id);
    }

    public Employee addEmployee(Employee employee) {
        employeeMapper.insert(employee);
        employeeBloomFilter.add(employee.getId());
        localCache.put(employee.getId(), employee);
        return employee;
    }

    public Employee getByIdWithPenetrationProtection(Long id) {
        Employee employee = localCache.getIfPresent(id);
        if (employee != null) {
            return employee;
        }

        String key = "employee:" + id;
        employee = (Employee) redisTemplate.opsForValue().get(key);
        if (employee != null) {
            localCache.put(id, employee);
            return employee;
        }

        if (!employeeBloomFilter.contains(id)) {
            return null;
        }

        String lockKey = "lock:employee:" + id;
        RLock lock = redissonClient.getLock(lockKey);
        try {
            boolean acquired = lock.tryLock(5, 15, TimeUnit.SECONDS);
            if (acquired) {
                employee = (Employee) redisTemplate.opsForValue().get(key);
                if (employee != null) {
                    localCache.put(id, employee);
                    return employee;
                }

                employee = employeeMapper.selectById(id);
                if (employee != null) {
                    redisTemplate.opsForValue().set(key, employee, 30, TimeUnit.MINUTES);
                    localCache.put(id, employee);
                }
            }
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        } finally {
            if (lock.isHeldByCurrentThread()) {
                lock.unlock();
            }
        }
        return employee;
    }
}
```

### 分布式锁防重复提交

```java
@RestController
@RequestMapping("/api/employees")
@Slf4j
public class EmployeeController {

    @Autowired
    private EmployeeService employeeService;

    @Autowired
    private RedissonClient redissonClient;

    @PostMapping
    public Result<Employee> add(@RequestBody @Valid Employee employee) {
        String lockKey = "lock:employee:add:" + employee.getName();
        RLock lock = redissonClient.getLock(lockKey);
        try {
            boolean acquired = lock.tryLock(3, 10, TimeUnit.SECONDS);
            if (!acquired) {
                return Result.error("请勿重复提交");
            }
            Employee saved = employeeService.addEmployee(employee);
            return Result.success(saved);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            return Result.error("操作被中断");
        } finally {
            if (lock.isHeldByCurrentThread()) {
                lock.unlock();
            }
        }
    }

    @PutMapping("/{id}")
    public Result<Employee> update(@PathVariable Long id,
                                   @RequestBody @Valid Employee employee) {
        employee.setId(id);
        Employee updated = employeeService.update(employee);
        return Result.success(updated);
    }

    @DeleteMapping("/{id}")
    public Result<Void> delete(@PathVariable Long id) {
        employeeService.deleteById(id);
        return Result.success();
    }

    @GetMapping("/{id}")
    public Result<Employee> getById(@PathVariable Long id) {
        Employee employee = employeeService.getByIdWithPenetrationProtection(id);
        return Result.success(employee);
    }
}
```

### 数据一致性：延迟双删

```java
@Service
@Slf4j
public class EmployeeService {

    @Transactional
    @Caching(evict = {
        @CacheEvict(value = "employee", key = "#employee.id"),
        @CacheEvict(value = "employee:list", allEntries = true)
    })
    public Employee updateWithConsistency(Employee employee) {
        employeeMapper.updateById(employee);
        localCache.invalidate(employee.getId());

        String key = "employee:" + employee.getId();
        CompletableFuture.runAsync(() -> {
            try {
                Thread.sleep(500);
                redisTemplate.delete(key);
                log.info("延迟双删完成，key={}", key);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        });

        return employee;
    }
}
```

### EMS v8技术栈总结

```
EMS v8 = EMS v7 + Redis缓存全家桶

┌─────────────────────────────────────────────────────────┐
│                    EMS v8 架构                           │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Controller                                             │
│  ├── GET /api/employees/{id}    → 查询（多级缓存+防穿透）│
│  ├── GET /api/employees         → 列表（Spring Cache）  │
│  ├── POST /api/employees        → 新增（分布式锁防重复） │
│  ├── PUT /api/employees/{id}    → 更新（延迟双删）      │
│  └── DELETE /api/employees/{id} → 删除（缓存清除）      │
│                                                         │
│  缓存架构                                               │
│  ├── L1: Caffeine本地缓存（5分钟TTL）                   │
│  ├── L2: Redis远程缓存（30分钟TTL）                     │
│  ├── 布隆过滤器：防缓存穿透                             │
│  ├── Redisson分布式锁：防缓存击穿 + 防重复提交          │
│  └── 延迟双删：保证数据一致性                           │
│                                                         │
│  安全层（EMS v7继承）                                   │
│  ├── Spring Security + JWT                              │
│  └── RBAC权限控制                                       │
│                                                         │
│  数据层                                                 │
│  ├── MySQL（持久化存储）                                │
│  └── Redis（缓存 + 分布式锁 + 布隆过滤器）             │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 本章小结

本章是Redis缓存实战的完整攻略，核心知识点：

1. **Redis入门**：内存数据库，读写速度是MySQL的100倍以上；生产必须设密码、禁用`keys *`
2. **五种数据类型**：String（KV）、List（队列）、Set（去重/交集）、Hash（对象字段级操作）、ZSet（排行榜）
3. **Spring Boot集成Redis**：Lettuce连接池必须加`commons-pool2`；RedisTemplate必须配置JSON序列化（不用JDK序列化）
4. **Spring Cache**：`@Cacheable`查缓存、`@CachePut`更新缓存、`@CacheEvict`删除缓存；同类内部调用缓存不生效；过期时间在CacheManager配置
5. **缓存穿透**：查不存在的数据 → 缓存null值（短过期）+ 布隆过滤器（终极方案）
6. **缓存击穿**：热点key过期 → 互斥锁（DCL双重检查）+ 逻辑过期（异步更新）
7. **缓存雪崩**：大量key同时过期 → 过期时间加随机值 + 多级缓存 + 限流降级
8. **数据一致性**：先更新DB再删缓存 + 延迟双删
9. **分布式锁**：Redisson `tryLock` + `try-finally` + `isHeldByCurrentThread()`；看门狗自动续期

**面试高频问题速答**：

| 问题 | 核心答案 |
|------|---------|
| 缓存穿透怎么解决？ | 布隆过滤器 + 缓存null值（短过期） |
| 缓存击穿怎么解决？ | 互斥锁（SETNX + DCL）+ 逻辑过期 |
| 缓存雪崩怎么解决？ | 过期时间加随机值 + 多级缓存 + 限流 |
| 先删缓存还是先更新DB？ | 先更新DB再删缓存 + 延迟双删 |
| Redisson看门狗是什么？ | 每1/3超时时间自动续期，客户端宕机则锁自动释放 |

---

## 思考题

1. 布隆过滤器说"不存在"一定不存在，说"存在"可能不存在——那么布隆过滤器误判时（说存在但实际不存在），查询会穿透到数据库吗？如何进一步优化？
2. 逻辑过期方案中，如果异步重建线程池满了怎么办？有没有兜底策略？
3. 延迟双删中延迟时间设多少合适？如果延迟时间内又有新的更新操作怎么办？
4. 为什么Redisson的`lock.unlock()`前必须判断`isHeldByCurrentThread()`？如果不判断，在什么场景下会出问题？
5. 多级缓存（Caffeine + Redis）中，如果数据库更新了，如何保证本地缓存和Redis缓存的一致性？有什么方案？

> **预告**：第27章我们将用Docker Compose编排MySQL + Redis + 应用服务，一键启动完整的EMS v8运行环境。Redis将作为容器化部署的重要一环。
