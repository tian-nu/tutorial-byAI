# 97-Kafka入门

> 💡 RabbitMQ 是快递站——包裹到了通知你来取。Kafka 是高速公路上的监控录像——把所有车辆（事件）按时间顺序全部录下来，谁想看随时回放。Kafka 的设计哲学不是"把消息推给你"，而是"消息全存着，你自己来拉"。这决定了它能处理海量数据。

---

## 本章目标
- 理解 Kafka 的核心概念：Topic、Partition、Offset、Consumer Group
- 安装并启动 Kafka
- 理解 Kafka 为什么快（顺序写磁盘 + 零拷贝）
- 用 Java 客户端发送和消费消息

---

## 97.1 Kafka 是什么

Kafka 最初由 LinkedIn 开发，用于收集和传输海量日志。现在它已经是一个**分布式流平台**：

- **消息系统**：像 RabbitMQ 一样收发消息，但吞吐量高几个数量级
- **存储系统**：消息持久化到磁盘，可以回溯历史数据
- **流处理**：通过 Kafka Streams 实时处理数据流

**一句话理解**：Kafka 是一个**分布式的、分区的、可回溯的提交日志（Commit Log）**。

---

## 97.2 Kafka 的核心概念

```
Topic: order-events
├── Partition 0: [msg0, msg1, msg2, msg3, msg4, msg5, msg6]
│                  offset→  0     1     2     3     4     5     6
├── Partition 1: [msg0, msg1, msg2, msg3]
│                  offset→  0     1     2     3
└── Partition 2: [msg0, msg1, msg2, msg3, msg4]
                   offset→  0     1     2     3     4
```

### 核心概念表

| 概念 | 说明 | 类比 |
|------|------|------|
| **Topic** | 消息的逻辑分类 | 文件夹名称 |
| **Partition** | Topic 的物理分片，分布在不同机器上 | 文件夹里的分卷 |
| **Offset** | 消息在 Partition 中的唯一序号（递增） | 行号 |
| **Producer** | 发送消息，可指定 Partition | 写入者 |
| **Consumer** | 消费消息，按 Offset 顺序读取 | 读取者 |
| **Consumer Group** | 一组消费者共享消费进度 | 团队协作 |
| **Broker** | Kafka 服务器实例 | 服务器 |

> 🤔 想多一点：一条 Kafka 消息被消费后**不会被删除**（默认保留 7 天）。这与 RabbitMQ 完全不同——RabbitMQ 是"消费完就删"，Kafka 是"消息一直留着，你想重新读从 offset 0 开始都可以"。这就是 Kafka 可以回溯历史数据的原因。

---

## 97.3 安装 Kafka（Docker）

```bash
docker run -d --name kafka -p 9092:9092 \
  -e KAFKA_ADVERTISED_LISTENERS=PLAINTEXT://localhost:9092 \
  -e KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR=1 \
  apache/kafka:latest
```

> 📖 Docker 详细教程见第112章。

---

## 97.4 为什么 Kafka 这么快？

### 原因一：顺序写磁盘

```
随机写磁盘：100 KB/s
顺序写磁盘：600 MB/s  ← Kafka 用的就是这个
```

Kafka 每条消息只是**追加到文件末尾**（append-only），不需要寻道，比随机读写快 6000 倍。

### 原因二：零拷贝（Zero Copy）

```
传统方式：
磁盘 → 内核缓冲区 → 用户缓冲区 → Socket 缓冲区 → 网卡
         copy1        copy2          copy3

Kafka 零拷贝：
磁盘 → 内核缓冲区 → 网卡（通过 sendfile 系统调用，跳过用户态）
         DMA 传输
```

减少 CPU 拷贝次数，大幅提升传输效率。

### 原因三：Page Cache

Kafka 不自己管理缓存，而是利用操作系统的 Page Cache。消息写入 Page Cache 就算"写入成功"（不是每次写磁盘），操作系统负责异步刷盘。

---

## 97.5 Java 生产者

### 依赖

```xml
<dependency>
    <groupId>org.apache.kafka</groupId>
    <artifactId>kafka-clients</artifactId>
    <version>3.7.0</version>
</dependency>
```

### 发送消息

```java
public class KafkaProducerExample {

    public static void main(String[] args) {
        Properties props = new Properties();
        props.put("bootstrap.servers", "localhost:9092");
        props.put("key.serializer",
                "org.apache.kafka.common.serialization.StringSerializer");
        props.put("value.serializer",
                "org.apache.kafka.common.serialization.StringSerializer");
        // acks=all 确保所有副本都收到（不丢消息）
        props.put("acks", "all");

        try (KafkaProducer<String, String> producer =
                     new KafkaProducer<>(props)) {

            for (int i = 0; i < 10; i++) {
                ProducerRecord<String, String> record =
                        new ProducerRecord<>("order-events",
                                "key-" + i, "message-" + i);

                producer.send(record, (metadata, exception) -> {
                    if (exception == null) {
                        System.out.printf("发送成功: topic=%s, partition=%d, offset=%d%n",
                                metadata.topic(), metadata.partition(), metadata.offset());
                    } else {
                        exception.printStackTrace();
                    }
                });
            }

            producer.flush();
        }
    }
}
```

### 生产者关键配置

| 配置 | 值 | 说明 |
|------|------|------|
| `acks` | `0` / `1` / `all` | 0=不等确认, 1=leader确认, all=所有副本确认 |
| `retries` | 3 | 发送失败重试次数 |
| `batch.size` | 16384 | 批量发送大小（字节） |
| `linger.ms` | 5 | 等 5ms 凑一批再发 |
| `compression.type` | `snappy` | 压缩算法 |

---

## 97.6 Java 消费者

```java
public class KafkaConsumerExample {

    public static void main(String[] args) {
        Properties props = new Properties();
        props.put("bootstrap.servers", "localhost:9092");
        props.put("group.id", "order-processing-group");
        props.put("key.deserializer",
                "org.apache.kafka.common.serialization.StringDeserializer");
        props.put("value.deserializer",
                "org.apache.kafka.common.serialization.StringDeserializer");
        props.put("enable.auto.commit", "false");  // 手动提交 offset

        try (KafkaConsumer<String, String> consumer =
                     new KafkaConsumer<>(props)) {

            consumer.subscribe(List.of("order-events"));

            while (true) {
                ConsumerRecords<String, String> records =
                        consumer.poll(Duration.ofMillis(100));

                for (ConsumerRecord<String, String> record : records) {
                    System.out.printf("收到: topic=%s, partition=%d, offset=%d, key=%s, value=%s%n",
                            record.topic(), record.partition(), record.offset(),
                            record.key(), record.value());

                    processOrder(record.value());
                }

                consumer.commitSync();  // 处理完成后提交 offset
            }
        }
    }

    private static void processOrder(String message) {
        System.out.println("处理订单: " + message);
    }
}
```

### 消费者关键配置

| 配置 | 说明 |
|------|------|
| `group.id` | 消费者组 ID |
| `enable.auto.commit` | `false` = 手动提交 offset（推荐） |
| `auto.offset.reset` | `earliest` = 从头开始读；`latest` = 只读新消息 |
| `max.poll.records` | 每次 poll 最多返回几条 |

---

## 97.7 Consumer Group —— Kafka 的精髓

```
Consumer Group: order-group
├── Consumer 1 → Partition 0   (消息 0,1,2,3...)
├── Consumer 2 → Partition 1   (消息 0,1,2...)
└── Consumer 3 → Partition 2   (消息 0,1,2,3...)
```

规则：
- **一个 Partition 只能被同一个 Consumer Group 中的一个消费者消费**（保证顺序）
- **一个消费者可以消费多个 Partition**
- **消费者数量 > Partition 数量时，多余消费者会空闲**

这意味着：**Partition 数量决定了最大并行度**。如果你的 Topic 只有 3 个 Partition，加第 4 个消费者是没用的。

> 🤔 想多一点：RabbitMQ 的关注点是"消息不能丢、不能重复"，Kafka 的关注点是"顺序、持久化、高吞吐"。Kafka 以 Partition 为单位保证消息顺序——同一个 Partition 内的消息严格按 offset 顺序消费。跨 Partition 不保证顺序。

---

## 97.8 Kafka vs RabbitMQ 最终对比

| | Kafka | RabbitMQ |
|------|------|------|
| 设计哲学 | 分布式日志 | 消息代理 |
| 吞吐量 | 百万级/秒 | 万级/秒 |
| 消息持久化 | 默认持久化（保留 N 天） | 可选持久化 |
| 消费后是否删除 | 不删（按时间/大小清理） | 删除（ACK 后） |
| 可否回溯 | ✅ 可以 | ❌ 不支持 |
| 消息顺序 | Partition 内有序 | Queue 内有序 |
| 路由灵活性 | 简单 | 复杂（4 种 Exchange） |
| 运维复杂度 | 高 | 中低 |

---

## 97.9 小结

| 知识点 | 核心内容 |
|--------|----------|
| Kafka 本质 | 分布式、分区、可回溯的提交日志 |
| Partition | 物理分片，决定并行度 |
| Offset | 消息在 Partition 中的唯一序号 |
| Consumer Group | 组内消费者共享消费，一个 Partition 只被一个消费者消费 |
| 为什么快 | 顺序写磁盘 + 零拷贝 + Page Cache |
| 关键配置 | `acks=all`、`enable.auto.commit=false`、`auto.offset.reset` |

---

## 97.10 自测题

**1. 一个 Topic 有 4 个 Partition，Consumer Group 有 5 个消费者。请问第 5 个消费者会收到消息吗？为什么？**

**2. Kafka 中 offset 是什么？如果消费者在处理消息后立即提交 offset，但业务处理本身失败了，会发生什么？**

**3. Kafka 为什么比 RabbitMQ 快那么多？列出至少两个原因。**

---

**答案提示**：1→不会。一个 Partition 只能被同一个 Consumer Group 中的一个消费者消费。4 个 Partition 最多对应 4 个活跃消费者，第 5 个空闲。2→offset 是消息在 Partition 中的唯一序号。如果先提交 offset 再处理业务但你代码崩了，这条消息的 offset 已被提交，重启后 Kafka 认为已消费，消息丢失。所以应该处理完再提交（at-least-once 语义）。3→① 顺序写磁盘（append-only）比随机写快 6000 倍；② 零拷贝（sendfile 系统调用，绕过用户态）；③ 利用 OS 的 Page Cache；④ 批量发送和压缩。下一章——Kafka 进阶。