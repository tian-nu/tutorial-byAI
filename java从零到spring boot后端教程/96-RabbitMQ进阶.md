# 96-RabbitMQ进阶

> 💡 收发快递很简单。但快递丢了怎么办？快递员送错了怎么办？高峰期包裹堆积如山怎么办？本章讲的就是消息队列的"物流管理"——如何保证消息不丢、不重复、能重试、超时自动处理。

---

## 本章目标
- 理解消息确认（ACK）机制，防止消息丢失
- 掌握消息持久化配置
- 理解死信队列与 TTL
- 实现消息的幂等消费
- 掌握延迟消息的实现方式

---

## 96.1 消息确认（ACK）——防止消费者侧丢失

### 问题

消费者从 Queue 取到消息，正在处理时崩溃了。如果消息已经被删除，这条消息就永久丢失了。

### 解决方案：手动 ACK

```java
// 生产者端确认：确保消息成功到达 Broker
channel.confirmSelect();
channel.basicPublish(EXCHANGE_NAME, ROUTING_KEY, null, message.getBytes());

if (channel.waitForConfirms()) {
    System.out.println("消息成功到达 Broker");
} else {
    System.out.println("消息发送失败，需要重试");
}
```

```java
// 消费者端确认：确保消息被成功处理
boolean autoAck = false;  // ← 关键：关掉自动确认
channel.basicConsume(QUEUE_NAME, autoAck, (consumerTag, delivery) -> {
    String message = new String(delivery.getBody());
    try {
        processMessage(message);       // 处理业务
        channel.basicAck(delivery.getEnvelope().getDeliveryTag(), false);
        //  false = 只确认当前这条，不批量
    } catch (Exception e) {
        // basicNack 第三个参数 true = 重新入队，false = 丢弃或进死信
        channel.basicNack(delivery.getEnvelope().getDeliveryTag(), false, true);
    }
}, consumerTag -> {});
```

### ACK 的三种操作

| 方法 | 效果 |
|------|------|
| `basicAck` | 确认处理成功，消息从队列删除 |
| `basicNack(deliveryTag, multiple, requeue)` | 拒绝，requeue=true 重新入队 |
| `basicReject` | 拒绝单条（不支持批量），不重新入队 |

> 🤔 想多一点：`requeue=true` 是危险的。如果消息本身有问题导致永远处理失败，它会无限循环——消费 → 失败 → 重新入队 → 再消费 → 再失败。这就是为什么需要死信队列。

---

## 96.2 消息持久化——防止 Broker 侧丢失

```java
// 队列持久化
boolean durable = true;
channel.queueDeclare(QUEUE_NAME, durable, false, false, null);

// 消息持久化
AMQP.BasicProperties props = new AMQP.BasicProperties.Builder()
        .deliveryMode(2)  // 2 = 持久化，1 = 非持久化
        .build();
channel.basicPublish(EXCHANGE_NAME, ROUTING_KEY, props, message.getBytes());
```

| 持久化了什么 | 作用 |
|------|------|
| 队列持久化 | RabbitMQ 重启后队列元数据不丢 |
| 消息持久化 | RabbitMQ 重启后消息体不丢 |
| 两者都不做 | 重启后队列和消息全部消失 |

> ⚠️ 持久化有性能代价（写磁盘）。不要把持久化当默认选项——只有不能丢的消息才持久化。

---

## 96.3 死信队列（DLX, Dead Letter Exchange）

当消息满足以下条件之一，会被转发到死信队列：

1. 消费者 `basicNack` / `basicReject` 且 `requeue=false`
2. 消息 TTL 过期
3. 队列达到最大长度

```java
// 声明死信交换机
channel.exchangeDeclare("dlx_exchange", BuiltinExchangeType.DIRECT);
channel.queueDeclare("dlx_queue", true, false, false, null);
channel.queueBind("dlx_queue", "dlx_exchange", "dead");

// 声明业务队列，关联死信交换机
Map<String, Object> args = new HashMap<>();
args.put("x-dead-letter-exchange", "dlx_exchange");
args.put("x-dead-letter-routing-key", "dead");
channel.queueDeclare("business_queue", true, false, false, args);
```

处理流程：

```
业务消息 → business_queue → 消费失败 (basicNack, requeue=false)
                                │
                                ▼
                          dlx_exchange → dlx_queue → 死信消费者（记录日志/告警/人工处理）
```

---

## 96.4 TTL（Time To Live）——消息过期

### 方式一：队列级别 TTL

```java
Map<String, Object> args = new HashMap<>();
args.put("x-message-ttl", 60000);  // 队列中所有消息 60 秒后过期
channel.queueDeclare(QUEUE_NAME, true, false, false, args);
```

### 方式二：消息级别 TTL

```java
AMQP.BasicProperties props = new AMQP.BasicProperties.Builder()
        .expiration("60000")  // 这条消息 60 秒后过期
        .build();
channel.basicPublish(EXCHANGE_NAME, ROUTING_KEY, props, message.getBytes());
```

> ⚠️ 消息过期后不会立刻从队列中移除——只有当消息到达队列头部（即将被消费）时，RabbitMQ 才检查它是否过期。这意味着"过期的消息还在队列里占着位置"。

---

## 96.5 延迟消息——TTL + DLX 组合

RabbitMQ 没有原生延迟队列，但可以通过 TTL + 死信队列实现：

```
发送消息到 delay_queue（设 TTL=30秒）
    │
    ├── 30 秒内没有消费者 → 消息过期
    │
    ├── 自动转发到 dlx_exchange（死信交换机）
    │
    └── dlx_exchange 路由到 target_queue
            │
            └── 消费者处理（此时已过了 30 秒）
```

```java
// 目标队列（实际处理消息的队列）
channel.exchangeDeclare("target_exchange", BuiltinExchangeType.DIRECT);
channel.queueDeclare("target_queue", true, false, false, null);
channel.queueBind("target_queue", "target_exchange", "order.timeout");

// 延迟队列（TTL 到期后自动转到死信交换机）
Map<String, Object> args = new HashMap<>();
args.put("x-dead-letter-exchange", "target_exchange");
args.put("x-dead-letter-routing-key", "order.timeout");
args.put("x-message-ttl", 30000);  // 30 秒
channel.queueDeclare("delay_queue", true, false, false, args);

// 使用者：发送一条"30 分钟后检查支付状态"的消息
channel.basicPublish("", "delay_queue", null, orderId.getBytes());
```

典型场景：下单 30 分钟后未支付自动取消。

---

## 96.6 消息幂等性

消息可能被重复消费（网络抖动导致 ACK 未到达 Broker，Broker 重新投递）。

```java
public void handleOrderMessage(String orderId) {
    // 用 orderId 作为唯一键，检查是否已处理过
    if (redisTemplate.opsForValue().setIfAbsent(
            "order:processed:" + orderId, "1", Duration.ofHours(24))) {
        // 首次处理
        processOrder(orderId);
    } else {
        // 已处理过，忽略
        log.warn("订单 {} 已处理，跳过重复消息", orderId);
    }
}
```

常用幂等方案：

| 方案 | 适用场景 |
|------|----------|
| 数据库唯一约束 | INSERT 时用 ON DUPLICATE KEY UPDATE |
| Redis setnx | 用消息唯一 ID 做 key |
| 版本号（乐观锁） | UPDATE ... SET version=version+1 WHERE version=? |
| 业务状态机 | "已支付"状态不会再变成"待支付" |

---

## 96.7 Qos（Quality of Service）——消费者限流

```java
// 每次最多拿 1 条未确认消息
channel.basicQos(1);
```

意义：如果队列中有 100 条消息，消费者默认会全部拉下来（不管自己处理速度）。`basicQos(1)` 让消费者一次只拿一条，处理完 ACK 后再拿下一条——实现公平分发。

```
无 Qos：消费者 A 拿到 50 条（空闲），消费者 B 拿到 50 条（繁忙）→ 负载不均
有 Qos(1)：A 处理完一条拿一条，B 处理完一条拿一条 → 能者多劳
```

---

## 96.8 小结

| 知识点 | 核心内容 |
|--------|----------|
| 手动 ACK | `autoAck=false` + `basicAck` / `basicNack` |
| 消息持久化 | `durable=true` + `deliveryMode=2` |
| 死信队列 | `x-dead-letter-exchange` + TTL / 消费失败 → 延迟处理 |
| TTL | `x-message-ttl` 或 message expiration |
| 延迟消息 | TTL + DLX 组合 |
| 幂等 | Redis setnx / 数据库唯一约束 / 版本号 |
| Qos | `basicQos(N)` 限制预取数量 |

---

## 96.9 自测题

**1. 消费者设置了 `autoAck=true`，处理消息时发生了异常但没有崩溃。这条消息会丢失吗？会造成什么后果？**

**2. 描述"下单 30 分钟未支付自动取消"在 RabbitMQ 中的实现方案。涉及哪些组件？**

**3. 什么情况下消息会被消费两次？写出两种处理重复消费的方案。**

---

**答案提示**：1→不会丢失，但也不会重试。`autoAck=true` 表示消息从队列取出时立刻确认删除，异常消息会丢失。应改为 `autoAck=false` + try-catch + `basicNack`。2→创建一个延迟队列（TTL=30 分钟），其死信交换机绑定到目标队列。下单时发送消息到延迟队列，30 分钟后消息过期，通过死信交换机路由到目标队列，消费者检查订单状态，若未支付则取消。3→消费者处理完但 ACK 超时/Broker 未收到确认，Broker 重新投递。方案：① 消息唯一 ID + Redis setnx 去重；② 数据库唯一约束 + INSERT IGNORE。下一章——Kafka 入门。