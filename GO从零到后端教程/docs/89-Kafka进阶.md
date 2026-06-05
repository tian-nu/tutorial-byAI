# 第89章 · Kafka进阶

> "上一章你学会了启动Kafka、创建Topic、收发消息。但如果这就是全部，Kafka不可能支撑起LinkedIn每天万亿级的消息处理。本章进入Kafka的内核——消息如何路由到分区？什么是ISR？消费者组Rebalance是什么鬼？你的消息到底丢没丢？这些问题在面试中反复出现，在生产环境中每天都在发生。"

---

## 89.1 分区策略

### 为什么需要分区策略

Producer发送消息时，Kafka需要决定：这条消息该去哪个Partition？

这个决定影响三件事：
- **顺序性**：相同key的消息进入同一分区→在该分区内有序
- **负载均衡**：消息均匀分布在各分区→吞吐最优
- **业务语义**：同一用户的订单进入同一分区→按用户顺序处理

### 三种分区策略

**策略一：指定Key → Hash分区（默认）**

```go
producer.SendMessage(&kafka.Message{
    Topic: "order-events",
    Key:   []byte("user_123"), 
    Value: []byte("订单创建"),
})
```

Kafka对Key做Hash然后模分区数：`partition = hash(key) % partition_count`

同一`user_123`的所有消息都进入同一个分区，保证了**该用户的时序**。

**策略二：不指定Key → 轮询**

```go
producer.SendMessage(&kafka.Message{
    Topic: "order-events",
    Value: []byte("订单创建"),
})
```

消息均匀分布在各个分区上，负载最均衡，但不保证顺序。

**策略三：自定义分区器**

```go
type MyPartitioner struct{}

func (p *MyPartitioner) Partition(msg *kafka.Message, partitions int32) (int32, error) {
    country := parseCountry(msg.Value)
    switch country {
    case "CN":
        return 0, nil 
    case "US":
        return 1, nil 
    default:
        return 2, nil 
    }
}
```

### 选型指南

| 需求 | 策略 |
|------|------|
| 需要同用户/同订单的时序 | 指定Key，Hash分区 |
| 纯粹追求最大吞吐，不关心顺序 | 不指定Key，轮询 |
| 按业务规则精确控制（如按地区） | 自定义分区器 |

---

## 89.2 消息可靠性

### 生产者的可靠性保障

Kafka通过**acknowledgements（acks）**配置控制生产者的可靠性等级：

| acks值 | 含义 | 可靠性 | 性能 |
|--------|------|--------|------|
| `acks=0` | 生产者不等待任何确认，发完就走 | 最低（可能丢数据） | 最高 |
| `acks=1` | Leader分区写入成功即可 | 中等（Leader挂了可能丢） | 中等 |
| `acks=all`（或-1） | 所有ISR（In-Sync Replicas）都写入成功 | 最高 | 最低 |

**acks=all的代价**：生产者必须等待所有副本都确认写入，延迟显著增加。但如果追求"绝对不丢"，这是必须的。

### 副本机制与ISR

每个Partition可以有多个副本（Replica），分布在不同的Broker上：

```
Partition 0：
  Broker 1: Leader（负责读写）
  Broker 2: Follower（同步Leader的数据）
  Broker 3: Follower（同步Leader的数据）
```

ISR（In-Sync Replicas）是**和Leader保持同步的副本集合**。如果一个Follower落后太多（`replica.lag.time.max.ms=10s`还没追上），就会被踢出ISR列表。

```
min.insync.replicas=2 + acks=all
→ Leader写入后，至少还有1个Follower也写入了，Producer才能收到成功确认
→ 即使Leader挂了，至少有一个Follower有完整数据，可以接任
```

### 消费者手动提交Offset

与RabbitMQ的ACK类似，Kafka消费者也需要"确认"——只不过确认的不是单条消息，而是**Offset**（读到哪了）。

**自动提交（危险）**：

```go
config := &kafka.ConfigMap{
    "enable.auto.commit": true,
    "auto.commit.interval.ms": 5000,
}
```

每5秒自动提交一次Offset。问题：消费者拉了一批消息，还没处理完，自动提交了Offset → 消费者挂了 → 重启后从已提交的Offset开始 → **中间那批消息丢了**。

**手动提交（安全）**：

```go
config := &kafka.ConfigMap{
    "enable.auto.commit": false,
}

for {
    msg, err := consumer.ReadMessage(-1)
    if err != nil {
        continue
    }

    err = processMessage(msg)
    if err != nil {
        log.Printf("处理失败: %v", err)
        continue
    }

    consumer.CommitMessage(msg)
}
```

只有消息处理成功了，才提交Offset。挂了重启后从上一个已提交的位置重来，保证不丢。

### 幂等生产者

Kafka从0.11版本开始支持**幂等生产者**：开启后，即使生产者因网络问题重试发送同一条消息，Broker也能识别出"这是一条重复消息"并丢弃。

```go
config := &kafka.ConfigMap{
    "enable.idempotence": true, 
    "acks":                "all",
    "max.in.flight":        5,
}
```

原理：Broker为每个Producer分配一个Producer ID（PID），每条消息带上序号。如果收到相同PID+序号的消息，直接丢弃。

---

## 89.3 消费者Offset管理

### Offset存储在哪里

Kafka早期把Offset存在Zookeeper中，后来改为存在一个特殊的内部Topic——`__consumer_offsets`。每个消费者组的Offset就像一个HashMap：

```
消费者组: "order-service-group"
  Topic: order-events, Partition 0 → Offset 1500
  Topic: order-events, Partition 1 → Offset 2300
  Topic: order-events, Partition 2 → Offset 1800
```

### 自动提交 vs 手动提交

| 方式 | 何时提交 | 风险 |
|------|---------|------|
| 自动提交 | 每隔N秒自动提交 | 消息可能重复消费，也可能丢失 |
| 手动提交-同步 | 处理完后立即commitSync | 安全但有性能开销 |
| 手动提交-异步 | 处理完后异步commitAsync | 快但commit可能失败 |
| 手动提交-组合 | 平时异步+关闭前同步 | 兼顾性能和安全 |

**推荐：手动异步提交+优雅关闭**：

```go
func runConsumer() {
    defer func() {
        consumer.Commit()
        consumer.Close()
    }()

    for {
        msg, err := consumer.ReadMessage(-1)
        if err != nil {
            break
        }
        processMessage(msg)
        consumer.CommitMessage(msg)
    }
}
```

### 重置Offset

如果消费者需要"回放"历史消息（比如业务逻辑改了，需要重新处理过去的订单）：

```bash
kafka-consumer-groups --bootstrap-server localhost:9092 \
  --group order-service-group \
  --topic order-events \
  --reset-offsets --to-earliest \
  --execute
```

重置选项：
- `--to-earliest`：回到最早的消息
- `--to-latest`：跳到最新的消息
- `--to-offset 1000`：跳到指定的Offset
- `--shift-by -100`：往前挪100条
- `--to-datetime 2024-01-01T00:00:00.000`：按时间回溯

---

## 89.4 Rebalance（重平衡）

### 什么是Rebalance

消费者组里消费者数量变化时（新增消费者、有消费者挂了、分区数变了），Kafka需要**重新分配分区给消费者**。这个过程叫Rebalance。

```
Rebalance前：
  Consumer A → Partition 0, 1
  Consumer B → Partition 2

Consumer C加入后，发生Rebalance：
  Consumer A → Partition 0
  Consumer B → Partition 1
  Consumer C → Partition 2
```

### Rebalance的影响

⚠️ **Rebalance期间，整个消费者组暂停消费！** 这是Kafka最容易被踩的坑之一。

如果消费者组频繁Rebalance（比如消费者处理慢导致心跳超时被踢出组→重新加入→又超时……），就会陷入"惊群效应"——消费者忽上忽下，消息大量堆积，系统的吞吐量跌到谷底。

这种情况就像公司团建在玩抢凳子——音乐一停（Rebalance）大家都要停下来抢位置（重新分配分区），音乐响起来才能继续干活（消费）。

### 如何避免不必要的Rebalance

**1. 合理配置心跳超时**

```go
config := &kafka.ConfigMap{
    "session.timeout.ms":   30000, 
    "heartbeat.interval.ms": 3000,  
}
```

`session.timeout.ms` 太短→稍有GC停顿或网络抖动就触发Rebalance。太长→消费者真挂了也要等很久才被发现。

**2. 合理配置消费超时**

```go
config := &kafka.ConfigMap{
    "max.poll.interval.ms":   300000, 
    "max.poll.records":       500,    
}
```

`max.poll.interval.ms`：两次poll之间的最大间隔。如果消费者处理一批消息花了超过这个时间，Kafka认为它"死了"→触发Rebalance。

**3. 使用协作式Rebalance（Cooperative Rebalance）**

Kafka 2.4引入的新特性。传统的Eager Rebalance：先释放全部分区再重新分配（全部暂停）。协作式Rebalance：只重新分配变动的分区（大部分消费者继续工作）。

```go
config := &kafka.ConfigMap{
    "partition.assignment.strategy": "cooperative-sticky",
}
```

---

## 89.5 高水位HW与LEO

这两个概念是Kafka数据同步机制的基础。

### LEO（Log End Offset）

每个副本（包括Leader和Follower）都有自己的LEO——**当前日志的末尾Offset**。

```
Partition 0 Leader（Broker 1）：
  [msg0, msg1, msg2, msg3, msg4]
                              ↑
                           LEO = 5

Partition 0 Follower（Broker 2）：
  [msg0, msg1, msg2, msg3]
                        ↑
                     LEO = 4（落后Leader一条消息）
```

### HW（High Watermark）

HW是**所有ISR副本中最小的LEO**。消费者只能读到HW之前的消息。

```
Leader:   [msg0, msg1, msg2, msg3, msg4]  LEO=5
Follower: [msg0, msg1, msg2, msg3]        LEO=4

HW = min(5, 4) = 3
```

消费者最多读到msg2（Offset 2）。msg3和msg4虽然Leader已经有了，但Follower还没同步到——如果现在Leader挂了，Follower变成新Leader，msg3和msg4就丢了。所以Kafka不让消费者读到还没被所有ISR副本确认的消息。

这就是**HW的作用**：定义"哪些消息是安全的、可以被消费者读到的"。HW也是消费者Offset提交的上限——你不能提交一个大于HW的Offset。

### 数据同步流程

```
时间线：
T1: Leader收到msg5，LEO=6，HW=3
T2: Follower从Leader拉取msg4，LEO=4
T3: Follower拉取msg5，LEO=5
T4: 所有ISR副本的min(LEO)=4 → HW推进到4
T5: Follower继续同步...
T6: min(LEO)=5 → HW推进到5
```

---

## 89.6 Kafka vs RabbitMQ 选型指导

学了两章RabbitMQ和两章Kafka，现在应该清楚了：它们不是竞争对手，而是为**不同场景**设计的两种工具。

### 快速决策表

| 你的需求 | 用谁 | 原因 |
|---------|------|------|
| "订单创建后发短信、发邮件" | RabbitMQ | 路由灵活，ACK可靠 |
| "收集全站用户点击日志" | Kafka | 海量吞吐，可回溯 |
| "微服务之间异步通信" | 两者都可以 | RabbitMQ更简单，Kafka吞吐更高 |
| "需要消息回溯重处理" | Kafka | 消息不删除，可重置Offset |
| "30分钟未付款取消订单" | RabbitMQ | TTL+DLX原生支持 |
| "实时风控/流计算" | Kafka | 天然对接Flink/Spark Streaming |
| "团队只有1~2人" | RabbitMQ | 运维简单，管理界面友好 |
| "每天百亿级消息" | Kafka | 分区并行，吞吐量天花板更高 |

### 双剑合璧

很多大厂同时用Kafka和RabbitMQ：

```
用户行为日志 ──→ Kafka ──→ Flink实时分析 ──→ 触发告警
                                          ──→ 发送通知
                                                    │
                                                    ↓
                                               RabbitMQ ──→ 短信
                                                         ──→ 邮件
                                                         ──→ Push
```

Kafka做"数据管道"（粗管道、大流量），RabbitMQ做"业务分发"（细路由、多消费者）。各取所长。

🤔 **想多一点**：哪个消息队列"更好"？

在技术圈，经常看到这种争论："Kafka完爆RabbitMQ！""不，RabbitMQ功能比Kafka多多了！"

这种争论没有意义——就像争论"卡车和轿车哪个更好"。卡车拉货多但你不会开着卡车去菜市场买菜，轿车灵活但你不会用轿车运钢材。

**选型的第一原则**：不是选"最好的"，而是选"你的场景最适合的"。如果团队只有2个人、每天几万条消息、需要一个可靠的消息中转站——RabbitMQ是最优解。如果你要构建公司的数据中台、每天数百亿条日志、要和Flink对接——Kafka是唯一合理的选择。

**选型的第二原则**：团队熟悉什么就用什么。你全团队都是RabbitMQ高手，接了一个"日志收集"的需求——用RabbitMQ也能做，没必要为了"理论最优"强行引入一个团队完全陌生的Kafka。

---

## 本章小结

| 知识点 | 要点 |
|--------|------|
| 分区策略 | 指定Key→Hash分区（有序），不指定→轮询（均衡），自定义分区器 |
| acks | 0=最快最丢，1=折中，all=最安全最慢 |
| ISR | 与Leader保持同步的副本集合，`min.insync.replicas` 决定最少确认数 |
| 手动提交Offset | 处理完再提交，保证不丢数据 |
| Rebalance | 消费者变动时重新分配分区，期间组内暂停消费 |
| 避免频繁Rebalance | 合理配置session.timeout、max.poll.interval，使用协作式Rebalance |
| LEO | Log End Offset，副本当前日志末尾 |
| HW | High Watermark，所有ISR的最小LEO，消费者只能读到HW之前 |
| 幂等生产者 | `enable.idempotence=true`，防止生产者重试导致消息重复 |
| 选型 | RabbitMQ=业务分发，Kafka=数据管道，可以双剑合璧 |

> 🚀 下一章：理论总是要落地。下一章我们用Go同时操作RabbitMQ和Kafka，构建一个完整的"异步下单系统"——从下单投递消息到库存扣减到通知发送，一镜到底。

---
[← 上一章：88-Kafka入门.md](88-Kafka入门.md) | [下一章：90-Go中使用消息队列.md →](90-Go中使用消息队列.md)
