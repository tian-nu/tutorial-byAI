# 第70章 · Java操作Redis

> "前两章在redis-cli命令行里玩Redis，这章我们要把它接入Spring Boot项目。Spring Data Redis把Redis的操作封装成了和JPA一样优雅的API——你熟悉的 `@Cacheable` 注解、简洁的 `RedisTemplate`、一行代码搞定缓存的增删改查。从此你写Redis代码就像写JPA一样顺手。"

---

## 70.1 Spring Data Redis概述

Spring Data Redis是Spring对Redis的封装，提供：

- **RedisTemplate / StringRedisTemplate**：编程式操作Redis
- **@Cacheable / @CacheEvict / @CachePut**：声明式缓存注解
- **连接工厂自动配置**：支持Jedis和Lettuce两种客户端
- **序列化策略**：支持JSON、JDK序列化、String等多种格式

---

## 70.2 项目配置

### 70.2.1 Maven依赖

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-data-redis</artifactId>
</dependency>

<!-- 连接池（Spring Boot 2.x+ 默认使用Lettuce，自带连接池能力） -->
<dependency>
    <groupId>org.apache.commons</groupId>
    <artifactId>commons-pool2</artifactId>
</dependency>
```

### 70.2.2 application.yml

```yaml
spring:
  data:
    redis:
      host: localhost
      port: 6379
      password:           # Redis默认无密码，留空即可
      database: 0         # 使用第0号数据库（Redis有0~15共16个数据库）
      timeout: 3000ms     # 连接超时

      lettuce:
        pool:
          max-active: 8   # 最大连接数
          max-idle: 8     # 最大空闲连接
          min-idle: 2     # 最小空闲连接
          max-wait: 1000ms # 等待连接最大时间
```

### 70.2.3 Redis配置类（自定义序列化）

```java
package com.example.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.data.redis.connection.RedisConnectionFactory;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.data.redis.serializer.GenericJackson2JsonRedisSerializer;
import org.springframework.data.redis.serializer.StringRedisSerializer;

@Configuration
public class RedisConfig {

    @Bean
    public RedisTemplate<String, Object> redisTemplate(RedisConnectionFactory factory) {
        RedisTemplate<String, Object> template = new RedisTemplate<>();
        template.setConnectionFactory(factory);

        // key用String序列化（可读性好）
        template.setKeySerializer(new StringRedisSerializer());
        template.setHashKeySerializer(new StringRedisSerializer());

        // value用JSON序列化（支持任意Java对象）
        template.setValueSerializer(new GenericJackson2JsonRedisSerializer());
        template.setHashValueSerializer(new GenericJackson2JsonRedisSerializer());

        return template;
    }
}
```

> 💡 默认的JDK序列化会将数据变成二进制字节，在 `redis-cli` 中看到的是一堆乱码。改为JSON序列化后，数据可读，也方便其他语言读取。

---

## 70.3 RedisTemplate：编程式操作

### 70.3.1 StringRedisTemplate（操作字符串，推荐）

```java
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.data.redis.core.ValueOperations;
import org.springframework.stereotype.Component;

import java.time.Duration;

@Component
public class RedisStringService {

    @Autowired
    private StringRedisTemplate stringRedisTemplate;

    // 设置字符串（带过期时间）
    public void set(String key, String value, long timeoutSeconds) {
        stringRedisTemplate.opsForValue().set(key, value, Duration.ofSeconds(timeoutSeconds));
    }

    // 获取字符串
    public String get(String key) {
        return stringRedisTemplate.opsForValue().get(key);
    }

    // 删除
    public Boolean delete(String key) {
        return stringRedisTemplate.delete(key);
    }

    // 判断是否存在
    public Boolean hasKey(String key) {
        return stringRedisTemplate.hasKey(key);
    }

    // 自增（计数器）
    public Long increment(String key, long delta) {
        return stringRedisTemplate.opsForValue().increment(key, delta);
    }

    // 设置过期时间
    public Boolean expire(String key, long seconds) {
        return stringRedisTemplate.expire(key, Duration.ofSeconds(seconds));
    }
}
```

### 70.3.2 RedisTemplate（操作对象）

```java
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.stereotype.Component;

import java.time.Duration;
import java.util.List;
import java.util.Set;

@Component
public class RedisObjectService {

    @Autowired
    private RedisTemplate<String, Object> redisTemplate;

    // ==== String操作 ====
    public void setObject(String key, Object value, long timeoutSeconds) {
        redisTemplate.opsForValue().set(key, value, Duration.ofSeconds(timeoutSeconds));
    }

    public <T> T getObject(String key, Class<T> clazz) {
        Object value = redisTemplate.opsForValue().get(key);
        return clazz.cast(value);
    }

    // ==== Hash操作 ====
    public void putHashField(String key, String field, Object value) {
        redisTemplate.opsForHash().put(key, field, value);
    }

    public Object getHashField(String key, String field) {
        return redisTemplate.opsForHash().get(key, field);
    }

    // ==== List操作 ====
    public void leftPush(String key, Object value) {
        redisTemplate.opsForList().leftPush(key, value);
    }

    public Object rightPop(String key) {
        return redisTemplate.opsForList().rightPop(key);
    }

    public List<Object> listRange(String key, long start, long end) {
        return redisTemplate.opsForList().range(key, start, end);
    }

    // ==== Set操作 ====
    public void addToSet(String key, Object... values) {
        redisTemplate.opsForSet().add(key, values);
    }

    public Set<Object> getSetMembers(String key) {
        return redisTemplate.opsForSet().members(key);
    }

    // ==== Sorted Set操作 ====
    public void addToZSet(String key, Object value, double score) {
        redisTemplate.opsForZSet().add(key, value, score);
    }

    public Set<Object> getZSetRange(String key, long start, long end) {
        return redisTemplate.opsForZSet().reverseRange(key, start, end);
    }
}
```

> 💡 `StringRedisTemplate` 继承自 `RedisTemplate<String, String>`，专门用于字符串操作。当你只存JSON字符串时，用 `StringRedisTemplate` 比 `RedisTemplate` 更轻量，不需要配置序列化。

---

## 70.4 声明式缓存：@Cacheable 系列注解

Spring Cache抽象提供了一套注解，让你几乎不用写Redis操作代码。

### 70.4.1 启用缓存

在启动类上添加 `@EnableCaching`：

```java
@SpringBootApplication
@EnableCaching   // 开启声明式缓存
public class Application {
    public static void main(String[] args) {
        SpringApplication.run(Application.class, args);
    }
}
```

### 70.4.2 @Cacheable：查缓存

```java
@Service
public class UserService {

    @Autowired
    private UserRepository userRepository;

    /**
     * 先从缓存查，有则返回；没有则执行方法体，将结果存入缓存后返回
     * key 的写法：#id 表示取方法参数 id 的值
     */
    @Cacheable(value = "user", key = "#id", unless = "#result == null")
    public User getUserById(Long id) {
        System.out.println("从数据库查询 id=" + id);  // 第二次调用不会打印
        return userRepository.findById(id).orElse(null);
    }

    // 缓存列表
    @Cacheable(value = "users", key = "'all'")
    public List<User> getAllUsers() {
        return userRepository.findAll();
    }
}
```

### 70.4.3 @CacheEvict：删除缓存

```java
@Service
public class UserService {

    // 更新数据时删除缓存（下次查询会重新缓存）
    @CacheEvict(value = "user", key = "#user.id")
    @Transactional
    public User updateUser(User user) {
        return userRepository.save(user);
    }

    // 删除用户时清除缓存
    @CacheEvict(value = "user", key = "#id")
    @Transactional
    public void deleteUser(Long id) {
        userRepository.deleteById(id);
    }

    // 清空整个缓存区域
    @CacheEvict(value = "users", allEntries = true)
    public void clearUserCache() {
        // 比如批量更新了用户后
    }
}
```

### 70.4.4 @CachePut：更新缓存

```java
// 不管缓存中有没有，都执行方法，并将结果放入缓存
@CachePut(value = "user", key = "#result.id")
public User saveUser(User user) {
    return userRepository.save(user);
}
```

### 70.4.5 三大缓存注解对比

| 注解 | 是否执行方法 | 是否更新缓存 | 使用场景 |
|------|-------------|-------------|---------|
| `@Cacheable` | 缓存命中时不执行 | 缓存未命中时写入 | 查询 |
| `@CachePut` | 每次都执行 | 每次都更新 | 新增/保存 |
| `@CacheEvict` | 每次都执行 | 删除缓存 | 删除/更新 |

### 70.4.6 自定义缓存配置

```yaml
spring:
  cache:
    type: redis
    redis:
      time-to-live: 3600000    # 缓存过期时间，毫秒（1小时）
      cache-null-values: false  # 不缓存null值
      key-prefix: "myapp:"     # key前缀
      use-key-prefix: true
```

---

## 70.5 实战：缓存用户信息

完整示例——一个带Redis缓存的用户查询服务：

```java
package com.example.service;

import com.example.entity.User;
import com.example.repository.UserRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.cache.annotation.CacheEvict;
import org.springframework.cache.annotation.Cacheable;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.Duration;
import java.util.Random;
import java.util.concurrent.TimeUnit;

@Service
public class CachedUserService {

    @Autowired
    private UserRepository userRepository;

    @Autowired
    private StringRedisTemplate stringRedisTemplate;

    // 声明式缓存：查询
    @Cacheable(value = "user", key = "#id", unless = "#result == null")
    public User getUserById(Long id) {
        simulateSlowQuery();
        return userRepository.findById(id).orElse(null);
    }

    // 编程式缓存：高并发下用互斥锁防止缓存击穿
    public User getUserWithLock(Long id) {
        String cacheKey = "user:" + id;
        String lockKey = "lock:user:" + id;

        // 1. 先查缓存
        String cached = stringRedisTemplate.opsForValue().get(cacheKey);
        if (cached != null) {
            return parseJson(cached);
        }

        try {
            // 2. 尝试获取锁
            Boolean locked = stringRedisTemplate.opsForValue()
                    .setIfAbsent(lockKey, "1", Duration.ofSeconds(10));

            if (Boolean.TRUE.equals(locked)) {
                // 3. 双重检查（拿到锁后再查一次缓存）
                cached = stringRedisTemplate.opsForValue().get(cacheKey);
                if (cached != null) {
                    return parseJson(cached);
                }

                // 4. 查数据库
                User user = userRepository.findById(id).orElse(null);
                if (user != null) {
                    int ttl = 3600 + new Random().nextInt(600); // 加随机值防雪崩
                    stringRedisTemplate.opsForValue()
                            .set(cacheKey, toJson(user), Duration.ofSeconds(ttl));
                } else {
                    // 缓存空值防穿透
                    stringRedisTemplate.opsForValue()
                            .set(cacheKey, "NULL", Duration.ofSeconds(300));
                }
                return user;
            } else {
                // 5. 没拿到锁，等待后重试
                Thread.sleep(100);
                return getUserWithLock(id);
            }
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            return null;
        } finally {
            // 6. 释放锁（简化版，生产环境建议用Redisson的RLock）
            stringRedisTemplate.delete(lockKey);
        }
    }

    @CacheEvict(value = "user", key = "#id")
    @Transactional
    public User updateUser(User user) {
        return userRepository.save(user);
    }

    private void simulateSlowQuery() {
        try { Thread.sleep(50); } catch (InterruptedException e) { }
    }

    private User parseJson(String json) { /* JSON反序列化 */ return null; }
    private String toJson(User user) { /* JSON序列化 */ return null; }
}
```

> 💡 上面的 `getUserWithLock` 实现了第69章讲的**缓存击穿防护**（互斥锁）+ **雪崩防护**（随机TTL）+ **穿透防护**（缓存空值）的完整方案。

---

## 70.6 分布式锁（进阶）

Redis可以实现分布式锁。但手动实现有坑（锁超时、误删别人锁等），推荐用**Redisson**：

```xml
<dependency>
    <groupId>org.redisson</groupId>
    <artifactId>redisson-spring-boot-starter</artifactId>
    <version>3.24.3</version>
</dependency>
```

```java
@Service
public class OrderService {

    @Autowired
    private RedissonClient redissonClient;

    public void createOrder(Long productId) {
        String lockKey = "lock:order:" + productId;
        RLock lock = redissonClient.getLock(lockKey);

        try {
            // 尝试加锁，最多等待5秒，锁30秒后自动释放
            if (lock.tryLock(5, 30, TimeUnit.SECONDS)) {
                // 扣库存、创建订单的业务逻辑
            }
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        } finally {
            if (lock.isHeldByCurrentThread()) {
                lock.unlock();
            }
        }
    }
}
```

---

## 本章小结

| 概念 | 要点 |
|------|------|
| Spring Data Redis | Spring对Redis的封装，提供Template和Cache注解 |
| StringRedisTemplate | 操作字符串的Template，轻量且无需序列化配置 |
| RedisTemplate | 操作任意Java对象的Template，需配置JSON序列化 |
| @Cacheable | 声明式查询缓存，缓存命中不执行方法 |
| @CacheEvict | 声明式删除缓存，更新/删除时用 |
| @CachePut | 声明式更新缓存，每次都执行方法 |
| 互斥锁 | 解决缓存击穿，SETNX获取锁，只有拿到锁的请求查DB |
| Redisson | 生产级Redis客户端，提供分布式锁等高级功能 |

---

## 自测题

1. **Spring Data Redis中 `StringRedisTemplate` 和 `RedisTemplate` 有什么区别？什么时候用哪个？**

2. **`@Cacheable` 和 `@CacheEvict` 的作用分别是什么？写出一个使用这两个注解的Service方法示例。**

3. **用Redis实现一个防止缓存击穿的方案（伪代码即可），说明互斥锁的关键步骤。**

<details>
<summary>参考答案（做完再看）</summary>

1. `StringRedisTemplate` 继承自 `RedisTemplate<String, String>`，专门操作字符串类型，不需要配置序列化器，轻量。`RedisTemplate` 可以操作任意Java对象，但需要配置序列化策略（推荐JSON序列化）。如果只是缓存JSON字符串或做简单的计数/锁，用 `StringRedisTemplate` 更简单。如果需要直接存取Java对象（如Hash类型存对象字段），用 `RedisTemplate`。

2. `@Cacheable`：先查缓存，有则直接返回，没有则执行方法并将结果放入缓存。`@CacheEvict`：执行方法后删除指定缓存。示例：
```java
@Cacheable(value = "product", key = "#id")
public Product getProduct(Long id) { return repo.findById(id).orElse(null); }

@CacheEvict(value = "product", key = "#product.id")
@Transactional
public Product updateProduct(Product product) { return repo.save(product); }
```

3. 互斥锁关键步骤：
```java
public User getUser(Long id) {
    String key = "user:" + id;
    // 1. 查缓存，有则返回
    User user = redis.get(key);
    if (user != null) return user;
    // 2. 尝试获取锁
    if (redis.setnx("lock:" + id, "1", 10)) {
        try {
            // 3. 双重检查
            user = redis.get(key);
            if (user != null) return user;
            // 4. 查数据库
            user = db.findById(id);
            // 5. 写入缓存（TTL加随机值防雪崩）
            redis.setex(key, 3600 + random(600), user);
        } finally {
            redis.del("lock:" + id); // 6. 释放锁
        }
    } else {
        Thread.sleep(100); // 没拿到锁，等待重试
        return getUser(id);
    }
    return user;
}
```
</details>