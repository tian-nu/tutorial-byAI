# 98-Kafka进阶

> 💡 你用 Kafka 存了一个月的订单数据。突然有一天，你想"把上个月所有已取消的订单重新处理一遍"。在 RabbitMQ 里，消息早删了。在 Kafka 里——你只需要把消费者 offset 重置到一个月前，所有历史消息重新消费一遍。这就是 Kafka 最独特的超能力：**时间旅行**。

---

## 本章目标
- 掌握 Kafka 的三种消息语义（at-most-once、at-least-once、exactly-once）
- 理解 Offset 管理策略
- 了解 ISR 机制与高可用
- 知道 Kafka 的常见问题与排错方法

---

## 98.1 三种消息语义

| 语义 | 含义 | 实现方式 |
|------|------|----------|
| **at-most-once** | 最多一次，可能丢 | 先提交 offset，再处理消息 |
| **at-least-once** | 至少一次，可能重复 | 先处理消息，再提交 offset（默认） |
| **exactly-once** | 精确一次 | 幂等生产者 + 事务 |

### at-most-once（容易丢，不推荐）

```java
// ❌ 先提交 offset，再处理
consumer.commitSync();
processMessage(record);  // 如果这里崩溃，消息就丢了
```

### at-least-once（默认，可能重复）

```java
// ✅ 先处理，再提交 offset（Kafka 默认行为）
processMessage(record);
consumer.commitSync();  // 如果这里崩溃，重启后会重新消费
```

### exactly-once（最理想，成本最高）

```java
// 生产者幂等
props.put("enable.idempotence", "true");

// 消费者使用事务
props.put("isolation.level", "read_committed");
```

> 🤔 想多一点：现实中大多数业务用 at-least-once + 消费者自己做幂等就够了。Kafka 的 exactly-once 事务性能开销很大（延迟增加 30-50%），只有金融/支付等强一致性场景才需要。

---

## 98.2 Offset 管理

### Offset 存在哪里？

Kafka 内部有一个特殊 Topic：`__consumer_offsets`（50 个 Partition），存储每个 Consumer Group 在每个 Partition 的消费位置。

### 自动提交 vs 手动提交

```java
// 自动提交（不推荐）
props.put("enable.auto.commit", "true");
props.put("auto.commit.interval.ms", "5000");  // 每 5 秒自动提交

// 手动同步提交（每条消息后提交，慢但可靠）
consumer.commitSync();

// 手动异步提交（批量提交，快但可能丢进度）
consumer.commitAsync();
```

### Offset 越界处理

```java
// earliest：从头开始（group 首次消费 / offset 已过期）
props.put("auto.offset.reset", "earliest");

// latest：只消费新消息（默认）
props.put("auto.offset.reset", "latest");

// none：没有初始 offset 时报错
props.put("auto.offset.reset", "none");
```

### 手动重置 Offset

```bash
# 将 consumer group "order-group" 在 topic "order-events" 的 offset
# 重置到最早位置
kafka-consumer-groups --bootstrap-server localhost:9092 \
  --group order-group --topic order-events \
  --reset-offsets --to-earliest --execute
```

---

## 98.3 ISR 与高可用

### ISR（In-Sync Replicas）

每个 Partition 有一个 **Leader** 和多个 **Follower**：

```
Partition 0:
├── Leader (Broker 1)        ← 读写都走 Leader
├── Follower (Broker 2)      ← 从 Leader 同步数据
└── Follower (Broker 3)      ← 从 Leader 同步数据

ISR = {Broker 1, Broker 2, Broker 3}  正常情况
ISR = {Broker 1, Broker 2}            Broker 3 落后太多，被踢出 ISR
ISR = {Broker 2}                      Broker 1 挂了，Broker 2 当选新 Leader
```

### 关键配置

```properties
# 每条消息写入 ISR 中所有副本后才确认（不丢消息）
acks=all

# 最少要有多少个 ISR 副本才能写入（防止所有副本都挂）
min.insync.replicas=2

# 每个 Topic 的默认副本数
default.replication.factor=3
```

### 可靠性公式

```
数据不丢的条件：
    acks=all
    AND min.insync.replicas >= 2
    AND replication.factor >= 3
```

---

## 98.4 消息积压处理

### 原因诊断

| 现象 | 原因 |
|------|------|
| 消费者处理速度 < 生产者发送速度 | 消费者逻辑太重 / 外部调用慢 |
| 消费者数量不足 | 一个 Partition 只能一个消费者 |
| 消费者组 Rebalance | 频繁加入/离开，停止消费 |

### 解决方案

```
方案 1：增加消费者（但不能超过 Partition 数）
方案 2：增加 Partition（需要重分配，有停服风险）
方案 3：消费者内部并行处理（多线程消费后写入另一个 topic）
方案 4：临时方案——新增一个消费者组，把积压消息
        转发到一个新 Topic（多 Partition），再并行消费
```

---

## 98.5 Rebalance —— 消费者的"地震"

当消费者组中消费者数量变化时，Kafka 会触发 Rebalance（重新分配 Partition 所有权）。在 Rebalance 期间，**所有消费者暂停消费**。

### 触发 Rebalance 的场景

1. 新消费者加入 Consumer Group
2. 消费者离开或崩溃（心跳超时）
3. Topic 的 Partition 数量变化

### 减少 Rebalance 影响

```java
// 增加心跳间隔，避免网络抖动导致误判
props.put("session.timeout.ms", "30000");      // 默认 10s → 30s
props.put("heartbeat.interval.ms", "10000");   // 默认 3s → 10s

// 增加 poll 间隔，避免处理慢被踢
props.put("max.poll.interval.ms", "600000");   // 默认 5min → 10min

// 静态 Group Membership（减少 Rebalance 次数）
props.put("group.instance.id", "consumer-instance-1");
```

---

## 98.6 Kafka 常见问题与排错

| 问题 | 可能原因 | 排查方法 |
|------|----------|----------|
| 生产者发送失败 | Broker 不可达 / acks=all 但 ISR 不足 | 检查 `kafka-topics --describe` |
| 消费者收不到消息 | offset 已到最后 / 消费组 rebalance | `kafka-consumer-groups --describe` |
| 消息乱序 | 同一个 key 被发到不同 Partition | 指定 key 时确保同一业务 ID 落到同一 Partition |
| 磁盘写满 | 日志保留策略太宽松 | 调整 `log.retention.hours` |
| Leader 切换频繁 | Broker 不稳定 | 检查网络延迟和磁盘 I/O |

### 常用运维命令

```bash
# 查看 Topic 详情（Partition 分布、Leader、ISR）
kafka-topics --bootstrap-server localhost:9092 --describe --topic order-events

# 查看消费者组消费进度
kafka-consumer-groups --bootstrap-server localhost:9092 --describe --group order-group

# 查看未消费的消息量（LAG）
kafka-consumer-groups --bootstrap-server localhost:9092 --describe --group order-group
# 关注 LAG 列，如果持续增长说明消费跟不上

# 查看 Topic 最早和最晚 offset
kafka-run-class kafka.tools.GetOffsetShell --broker-list localhost:9092 --topic order-events
```

---

## 98.7 小结

| 知识点 | 核心内容 |
|--------|----------|
| 三种语义 | at-most-once / at-least-once（默认） / exactly-once |
| Offset 管理 | `__consumer_offsets` Topic / 手动提交 > 自动提交 |
| ISR | Leader + 同步中的 Follower，保证高可用 |
| 可靠性公式 | `acks=all` + `min.insync.replicas>=2` + `replication.factor>=3` |
| Rebalance | 消费者变化时暂停消费，减少触发即可 |
| 消息积压 | 增加 Partition + 消费者 / 临时转存新 Topic |

---

## 98.8 自测题

**1. Kafka 默认的消息语义是什么（at-most-once / at-least-once / exactly-once）？它是如何实现的？**

**2. 你的 Topic 有 2 个 Partition，Consumer Group 有 3 个消费者。突然 Consumer 3 崩溃了，会发生什么？Consumer 3 之前消费的 Partition 会怎样？**

**3. 生产者配置 `acks=all`，消费者在处理完消息后调用 `commitSync()`。但消费者刚 commit 完就崩溃了——重启后消息会丢失吗？如果不会，会有什么问题？**

---

**答案提示**：1→默认 at-least-once。通过先处理消息再提交 offset 实现——如果提交前崩溃，重启后会重新消费，因此可能重复。2→Consumer 3 的崩溃会触发 Rebalance。Consumer 3 之前消费的 Partition 会被重新分配给 Consumer 1 或 Consumer 2。在 Rebalance 期间，整个 Consumer Group 暂停消费。3→不会丢失。但存在重复消费问题——commit 成功后崩溃，消息已被消费者处理，但消费者重启后从当前 offset 开始消费（该 offset 之后的消息是新的）。如果恰好有一批消息处理完还没提交就崩溃了，这批消息会被重新处理。下一章——Spring 集成消息队列。