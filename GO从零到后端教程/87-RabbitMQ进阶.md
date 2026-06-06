# 第87章 · RabbitMQ进阶

> "能跑通代码和能在生产环境用是两码事。消息丢了怎么办？消费者挂了消息去哪了？同样的消息被处理了两次怎么查？30分钟不付款的订单怎么自动取消？本章不教你新功能，而是教你如何在真实的不完美的世界里，让消息队列变得可靠。"

---

## 87.1 消息确认（ACK）

上一章Work Queue模式里我们用了 `d.Ack(false)`，但没有解释原因。

### 问题：autoAck=true的危险

如果你设置 `autoAck=true`，RabbitMQ把消息发给消费者的那一瞬间，就会在队列中删除该消息。如果消费者收到消息后还没来得及处理就崩溃了——这条消息**永远丢失**了。

就像快递员把包裹扔到你家门口，没等你签收就走了。包裹被人拿走了，快递公司说"我已经送到了"——但你什么都没收到。

### 解决：手动确认

`autoAck=false` + 消费者处理完手动调用 `d.Ack(false)`：

```go
msgs, err := ch.Consume(
    q.Name,
    "",     
    false,  
    false,  
    false,  
    false,  
    nil,    
)

go func() {
    for d := range msgs {
        err := processMessage(d.Body)
        if err != nil {
            d.Nack(false, true) 
            continue
        }
        d.Ack(false) 
    }
}()
```

- `d.Ack(false)`：确认当前这一条消息已处理
- `d.Nack(false, true)`：拒绝当前这条，并让它重新入队（requeue=true）
- `d.Nack(false, false)`：拒绝当前这条，不重新入队（消息进入死信或丢弃）

### 确认的时机很重要

千万不要在处理消息**之前**就Ack：

```go
for d := range msgs {
    d.Ack(false) 
    processMessage(d.Body) 
}
```

这比 `autoAck=true` 更危险——你给了RabbitMQ一个虚假的承诺。

正确的做法：**消息处理成功后立刻Ack，处理失败根据情况决定Nack+requeue还是记日志后Ack**（避免无限循环）。

```go
for d := range msgs {
    err := processMessage(d.Body)
    if err != nil {
        log.Printf("处理失败: %v, 消息: %s", err, d.Body)
        d.Ack(false)
        continue
    }
    d.Ack(false)
}
```

为什么失败了还要Ack？因为有些消息是"有毒"的——格式错误、数据不存在、业务逻辑上永远无法处理。如果每次都Nack+requeue，这条坏消息会在队列里反复循环，永远出不来。

---

## 87.2 消息持久化

如果RabbitMQ服务器重启了，队列和消息还在吗？取决于你的配置。

### 两个层面的持久化

| 持久化对象 | 配置方式 | 作用 |
|-----------|---------|------|
| 队列持久化 | `QueueDeclare`的`durable=true` | 队列本身不因重启而消失 |
| 消息持久化 | `DeliveryMode: amqp.Persistent` | 队列中的消息不因重启而消失 |

两者缺一不可：如果队列持久化但消息不持久化→重启后队列还在但里面空了。如果消息持久化但队列不持久化→重启后队列都没了，消息也无从依附。

### 持久化 ≠ 100%不丢

RabbitMQ不是每收到一条消息就立刻刷盘（那样性能太差了）。它有一个短暂的"窗口期"——消息已经收到但还没写入磁盘。这个窗口期通常很短（毫秒级），但如果服务器恰好在这个窗口期断电，消息仍然可能丢失。

对于绝大多数场景，这个风险可以接受。如果需要"绝对不丢"（金融交易等），需要用**Publisher Confirm**（生产者确认）——87.3后详述。

### 完整配置

```go
q, err := ch.QueueDeclare(
    "task_queue", 
    true,   
    false,  
    false,  
    false,  
    nil,    
)

err = ch.PublishWithContext(
    ctx,
    "",
    q.Name,
    false,
    false,
    amqp.Publishing{
        DeliveryMode: amqp.Persistent, 
        ContentType:  "application/json",
        Body:         jsonData,
    },
)
```

---

## 87.3 公平分发（Qos Prefetch）

### 默认分发的不公平性

默认情况下，RabbitMQ按**轮询**方式把消息分发给消费者：第1条给A、第2条给B、第3条给A……不管A和B的处理能力如何。

问题来了：如果A处理的都是简单任务（1秒完成），B处理的都是复杂任务（10秒完成）：
- A手头永远是空的（处理完一条马上拿到下一条，又立刻处理完）
- B手头堆了一大堆消息（RabbitMQ不管B手头还有多少没处理完的，继续按轮询发给它）

结果：A很闲，B累死，整体效率低下。

### Prefetch = 1：能者多劳

```go
err = ch.Qos(
    1,     
    0,     
    false, 
)
```

设置 `prefetch=1`后，RabbitMQ会等消费者确认了当前的消息，才会发下一条给它。于是：
- A处理快→Ack快→拿到更多消息→处理更多
- B处理慢→Ack慢→拿到消息少→不会被压垮

这才是真正的**按能力分配**——"能者多劳"。

### Prefetch值的设置

| prefetch值 | 适用场景 |
|-----------|---------|
| 1 | 最安全，适合处理时间不均的任务 |
| 10-50 | 处理时间较均匀，减少网络往返 |
| 0 | 无限制（RabbitMQ会尽可能快地把消息推给消费者） |

prefetch不是越大越好。太大→消息在消费者端堆着→消费者挂了消息全丢。太小→频繁ACK带来额外网络开销。一般10-50是合理区间。

---

## 87.4 死信队列（DLX — Dead Letter Exchange）

### 什么是死信

一条消息"寿终正寝"有三种情况：
1. **被消费者拒绝**（Nack/Reject且requeue=false）
2. **消息过期**（TTL超时，见87.5）
3. **队列满了**（max-length或max-length-bytes超出限制）

这些"被遗弃"的消息如果不处理就永远消失了，无法追溯、无法补偿。死信队列就是给这些消息一个"收容所"——先存着，运维人员可以以后排查。

### 配置死信队列

死信队列只是"一个普通的队列+一个普通的Exchange"，特殊之处在于声明原队列时指定 `x-dead-letter-exchange`：

```go
dlxArgs := amqp.Table{
    "x-dead-letter-exchange":    "order_dlx_exchange",
    "x-dead-letter-routing-key": "order.dead",
}

q, err := ch.QueueDeclare(
    "order_queue",
    true,
    false,
    false,
    false,
    dlxArgs,
)
```

完整架构：

```
Producer ──→ [order_exchange] ──→ [order_queue]
                                      │
                                      │ 消息被拒绝/过期/溢出
                                      ↓
                               [order_dlx_exchange] ──→ [order_dead_queue]
                                                            │
                                                            ↓
                                                        运维排查
```

消费者代码中使用Nack拒绝：

```go
for d := range msgs {
    err := processOrder(d.Body)
    if err != nil {
        log.Printf("订单处理失败: %v", err)
        d.Nack(false, false) 
    } else {
        d.Ack(false)
    }
}
```

`Nack(false, false)` 的第二个 `false` 表示"不要再放回原队列"→消息会进入死信队列。

---

## 87.5 延迟队列（TTL + DLX）

### 场景：30分钟未支付自动取消订单

用户下单后，如果30分钟内没有付款，系统需要自动取消订单、释放库存。这个"30分钟后执行某个操作"的需求，是延迟队列的经典应用。

RabbitMQ**原生不支持延迟队列**，但可以用TTL（Time To Live）和DLX组合实现。

### TTL（消息存活时间）

可以为队列设置TTL，也可以为单条消息设置TTL：

**队列级别的TTL**（队列中所有消息统一的过期时间）：

```go
args := amqp.Table{
    "x-message-ttl": 30 * 60 * 1000, 
}
q, err := ch.QueueDeclare(
    "order_delay_queue",
    true,
    false,
    false,
    false,
    args,
)
```

**消息级别的TTL**（每条消息单独指定）：

```go
err = ch.PublishWithContext(
    ctx,
    "",
    q.Name,
    false,
    false,
    amqp.Publishing{
        Expiration:  "1800000", 
        ContentType: "application/json",
        Body:        jsonData,
    },
)
```

### 完整实现：订单超时取消

**第一步：创建延迟队列和死信队列**

```go
func setupOrderDelayQueues(ch *amqp.Channel) error {
    err := ch.ExchangeDeclare("order_dlx_exchange", "direct", true, false, false, false, nil)
    if err != nil {
        return err
    }

    _, err = ch.QueueDeclare(
        "order_dead_queue",
        true,
        false,
        false,
        false,
        nil,
    )
    if err != nil {
        return err
    }

    err = ch.QueueBind("order_dead_queue", "order.timeout", "order_dlx_exchange", false, nil)
    if err != nil {
        return err
    }

    delayArgs := amqp.Table{
        "x-dead-letter-exchange":    "order_dlx_exchange",
        "x-dead-letter-routing-key": "order.timeout",
        "x-message-ttl":             int32(30 * 60 * 1000),
    }

    _, err = ch.QueueDeclare(
        "order_delay_queue",
        true,
        false,
        false,
        false,
        delayArgs,
    )
    return err
}
```

**第二步：下单时把订单发到延迟队列**

```go
err = ch.PublishWithContext(
    ctx,
    "",
    "order_delay_queue",
    false,
    false,
    amqp.Publishing{
        DeliveryMode: amqp.Persistent,
        ContentType:  "application/json",
        Body:         jsonData,
    },
)
```

**第三步：消费者监听死信队列，处理"到期了还没付款"的订单**

```go
msgs, err := ch.Consume(
    "order_dead_queue",
    "",
    false,
    false,
    false,
    false,
    nil,
)

go func() {
    for d := range msgs {
        var order Order
        json.Unmarshal(d.Body, &order)
        err := cancelOrder(order.ID)
        if err != nil {
            d.Nack(false, true)
            continue
        }
        d.Ack(false)
    }
}()
```

### 流程图

```
下单
 │
 ├──→ 创建订单记录 (status=pending)
 │
 └──→ 发消息到 delay_queue (TTL=30分钟)
        │
        │ 30分钟倒计时...
        │ 如果用户付款了 → 订单状态改为paid → 啥也不用做
        │
        │ 30分钟到了，消息过期
        ↓
    死信队列
        │
        │ 收到"order.timeout"消息
        │
        ├──→ 查询订单状态
        │       │
        │       ├── 还是pending → 取消订单、恢复库存
        │       │
        │       └── 已经是paid → 忽略（用户已付款）
        │
        └──→ Ack
```

---
## 87.6 消息幂等性

### 什么是幂等

"幂等"这个词听起来高大上，其实意思很简单：**同样的操作执行一次和执行一百次，结果一样。**

比如：
- 查询用户信息：查多少次都一样 → 天然幂等
- 扣款100元：扣一次和扣两次，结果不一样 → 不幂等
- 基于ID的UPDATE：`UPDATE users SET name='张三' WHERE id=1` → 执行多少次结果一样 → 幂等
- 基于条件的UPDATE：`UPDATE users SET balance = balance - 100 WHERE id=1` → 不幂等

### RabbitMQ中的幂等问题

RabbitMQ保证"至少投递一次"（at-least-once delivery），但不保证"恰好一次"（exactly-once）。在以下场景中，同一条消息可能被消费多次：

1. 消费者处理完消息，但在发送ACK之前网络断了→RabbitMQ没收到ACK→消息重新入队→发送给另一个消费者
2. 生产者发送消息成功后没收到确认→重试→消息重复
3. 网络抖动导致ACK消息丢失

### 解决方案：唯一ID去重

每条消息带上一个**全局唯一的ID**（如雪花ID、UUID），消费者维护"已处理的消息ID"集合（可以用Redis、数据库唯一约束、或布隆过滤器）。

```go
func handleMessage(msg Message) error {
    exists, err := redis.Exists(ctx, "processed:"+msg.MessageID).Result()
    if err != nil {
        return err
    }
    if exists > 0 {
        return nil
    }

    err = doActualWork(msg)
    if err != nil {
        return err
    }

    redis.Set(ctx, "processed:"+msg.MessageID, "1", 24*time.Hour)
    return nil
}
```

也可以用数据库的唯一约束：

```sql
CREATE TABLE processed_messages (
    message_id VARCHAR(64) PRIMARY KEY,
    processed_at TIMESTAMP DEFAULT NOW()
);
```

```go
_, err := db.Exec("INSERT INTO processed_messages (message_id) VALUES (?)", msg.MessageID)
if err != nil {
    if isDuplicateKeyError(err) {
        return nil 
    }
    return err
}
```

生产者发送消息时带上ID：

```go
err = ch.PublishWithContext(
    ctx,
    "",
    q.Name,
    false,
    false,
    amqp.Publishing{
        MessageId:   generateUniqueID(),
        ContentType: "application/json",
        Body:        jsonData,
    },
)
```

---

## 87.7 消息顺序性

### RabbitMQ的顺序保证

在**单队列 + 单消费者**的情况下，RabbitMQ严格保证FIFO顺序——先发的消息一定先被消费。

```
Producer → msg1, msg2, msg3 → [Queue] → Consumer → msg1, msg2, msg3 ✅ 顺序一致
```

### 什么情况会破坏顺序

1. **多个消费者竞争消费**：消费者A处理msg1慢、消费者B处理msg2快→msg2比msg1先处理完
2. **消息重试**：msg1处理失败→Nack→requeue→排到队尾→msg2和msg3跑到msg1前面了
3. **优先级队列**：高优先级的消息插队

### 如何保证顺序

如果你的业务**必须**按顺序处理（比如：同一个订单的"创建→支付→发货"必须按顺序处理），有几种方案：

**方案一：分区有序**

让同一类（如同一订单ID）的消息走同一个队列、被同一个消费者处理：

```
订单ID: 123
  msg1(创建) → [order.123.queue] → Consumer(只消费这一个队列) → 保证顺序
  msg2(支付) → [order.123.queue]
  msg3(发货) → [order.123.queue]

订单ID: 456
  另一组消息 → [order.456.queue] → 另一个Consumer
```

在Go中实现：

```go
func getQueueName(orderID string) string {
    return "order." + orderID + ".queue"
}

q, err := ch.QueueDeclare(
    getQueueName(order.ID),
    true,
    false,
    false,
    false,
    nil,
)
```

**方案二：消息体中带序号**

消费者收到消息后自己排序：

```go
type OrderMessage struct {
    OrderID   string `json:"order_id"`
    Sequence  int    `json:"sequence"`  
    EventType string `json:"event_type"` 
}

var orderBuffers = make(map[string][]OrderMessage)
var mu sync.Mutex

func handleOrderMessage(msg OrderMessage) {
    mu.Lock()
    buffer := append(orderBuffers[msg.OrderID], msg)
    sort.Slice(buffer, func(i, j int) bool {
        return buffer[i].Sequence < buffer[j].Sequence
    })
    orderBuffers[msg.OrderID] = buffer
    mu.Unlock()

    processCompletedSequences(msg.OrderID)
}
```

**方案三：不要强求全局有序**

大多数场景，你并不需要所有消息严格有序——你只需要**同一业务实体的消息有序**。比如订单A和订单B的消息可以交错处理，但订单A自己的消息要按顺序。这就是**分区有序**的概念，也是Kafka的核心设计思想。

🤔 **想多一点**：ACK、持久化、幂等、顺序——你真的每样都需要吗？

新手容易犯的错误是"把每一样都配置到极致"——每条消息都持久化、每个消费者都手动ACK、每条消息都带唯一ID做幂等、每个队列都考虑顺序。

但在真实项目中，**要根据消息的重要性分级处理**：

| 消息级别 | 示例 | ACK | 持久化 | 幂等 | 有序 |
|---------|------|-----|--------|------|------|
| 核心交易 | 扣款、创建订单 | 手动 | 是 | 必须 | 分区有序 |
| 重要通知 | 发货通知、验证码 | 手动 | 是 | 建议 | 不需要 |
| 普通通知 | 营销短信、日志 | 自动 | 否 | 不需要 | 不需要 |

不是每一条消息都需要最高级别的保证。过度设计会让系统复杂度和运维成本爆炸，而收益微乎其微。

---

## 本章小结

| 知识点 | 要点 |
|--------|------|
| 手动ACK | `autoAck=false`，处理完再Ack，避免消息丢失 |
| Nack | 拒绝消息：requeue=true重新入队，false进入死信 |
| 持久化 | 队列持久化（durable=true）+ 消息持久化（Persistent），双重保险 |
| 公平分发 | `Qos(prefetch=1)`，能者多劳，防止慢消费者堆积 |
| 死信队列DLX | 拒绝/过期/溢出消息的去处，便于问题排查 |
| TTL | 队列级或消息级设置存活时间 |
| 延迟队列 | TTL + DLX实现，经典场景：订单超时取消 |
| 幂等性 | 同样操作多次执行结果相同，用唯一ID + Redis/DB去重 |
| 顺序性 | 单队列单消费者FIFO，多消费者用分区有序（按订单ID分队列） |

> 🚀 下一章：离开RabbitMQ的温柔乡，我们进入Kafka的世界——一个为海量数据而生、每秒百万条消息的"高速公路"。Kafka为什么快？什么是Partition？Consumer Group又是什么？

---
[← 上一章：86-RabbitMQ入门.md](86-RabbitMQ入门/) | [下一章：88-Kafka入门.md →](88-Kafka入门/)
