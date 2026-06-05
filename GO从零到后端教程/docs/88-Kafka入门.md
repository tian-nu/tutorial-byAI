# 第88章 · Kafka入门

> "如果RabbitMQ是一辆精致可靠的日本皮卡，Kafka就是一辆在高速公路上飙到200码的重型卡车——不是为了拉灵活的散货，而是为了在数据高速公路上以百万条/秒的速度狂奔。本章带你理解Kafka的核心概念、搞懂它为什么这么快、然后用Docker启动第一个Kafka实例。"

---

## 88.1 Kafka是什么

Kafka是LinkedIn于2011年开源的**分布式流处理平台**，用Java和Scala编写。它的诞生动机非常单纯：LinkedIn每天产生海量的用户行为数据（点击、浏览、点赞、分享），需要一套系统来**实时收集、存储和分发这些数据**。

讲个故事：LinkedIn早期用RabbitMQ做数据管道。但随着用户量增长，每天要处理的数据量从几GB飙升到几百TB。RabbitMQ开始力不从心——不是它不好，是它设计时就不是为这个场景做的。于是LinkedIn的工程师Jay Kreps（Kafka之父）决定从零设计一套系统，核心目标只有一个：**以最快速度吞吐最大量的数据**。

如今，Kafka已经成为大数据生态的标配——几乎所有需要数据管道的系统里都能看到它的身影。全球Top 10互联网公司至少有8家在用Kafka。

### Kafka与传统MQ的核心区别

| 维度 | RabbitMQ | Kafka |
|------|----------|-------|
| 设计目标 | 灵活路由、可靠投递 | 高吞吐、持久化流存储 |
| 消息保留 | 消费完就删除 | 保留一段时间（默认7天），可回溯 |
| 消费模型 | Push为主 | Pull为主（消费者主动拉） |
| 路由能力 | 极其丰富（4种Exchange） | 简单（Topic→Partition） |
| 吞吐量 | 数万条/秒 | 数百万条/秒 |
| 核心数据结构 | Queue | Partition（分区日志） |

最关键的区别：RabbitMQ把消息当"任务"——发给你、你处理、删掉。Kafka把消息当"日志"——永远追加、保留一段时间、想什么时候读就什么时候读。

---

## 88.2 核心概念

Kafka的世界由六个核心角色组成。理解了这些，就理解了Kafka的架构。

### Broker（经纪人/服务器节点）

一个Kafka服务器实例。就像分布式系统中的一台机器。实际部署中，一个Kafka集群通常有3~5个Broker。

### Topic（主题）

消息的逻辑分类，相当于RabbitMQ的Exchange+Queue的合体。比如"用户行为日志"是一个Topic，"订单事件"是另一个Topic。

### Partition（分区）

这是Kafka最核心的设计。一个Topic被分割成多个Partition，每个Partition是一个**有序的、不可变的日志文件**——只能追加（append-only），不能修改。

```
Topic: user-actions（用户行为）
│
├── Partition 0: [msg1, msg2, msg3, msg4, msg5, ...]  ← 存储在某台Broker上
├── Partition 1: [msg6, msg7, msg8, msg9, ...]        ← 存储在某台Broker上
└── Partition 2: [msg10, msg11, msg12, ...]           ← 存储在某台Broker上
```

为什么分区？两个核心原因：
1. **并行处理**：三个分区可以同时被三个消费者消费，吞吐量x3
2. **数据分布**：每个分区可以存储在不同Broker上，突破了单机磁盘限制

就像图书馆的书架——一本书不能同时被两个人借，但如果把一本热门书复印三份放在三个书架上，三个人就能同时借阅。

### Offset（偏移量）

每条消息在Partition中的唯一编号——从0开始，单调递增。Offset是Kafka的"书签"——消费者说"我读到了Offset 100"，Kafka就知道下次从101开始发。

```
Partition 0:
┌──────┬──────┬──────┬──────┬──────┬──────┐
│ Off 0│ Off 1│ Off 2│ Off 3│ Off 4│ Off 5│ ...
│ msgA │ msgB │ msgC │ msgD │ msgE │ msgF │
└──────┴──────┴──────┴──────┴──────┴──────┘
         ↑
    消费者A已读到这里
    下次从Offset 2开始
```

### Producer（生产者）

发送消息的客户端。Producer决定把消息发送到Topic的**哪个Partition**：
- 指定了key → `hash(key) % 分区数` 决定分区（相同key的消息进入同一分区，保证顺序）
- 没指定key → 轮询（Round Robin）

### Consumer（消费者）和Consumer Group（消费者组）

消费者属于某个Consumer Group（消费者组，一组消费者共享消费进度的逻辑分组，详见附录I）。**一个分区只能被同组内的一个消费者消费**（点对点），但可以被不同组的消费者同时消费（发布订阅）。

```
Consumer Group A（订单处理组）：
  Consumer A1 ──→ Partition 0
  Consumer A2 ──→ Partition 1
  Consumer A3 ──→ Partition 2
  （每个分区只被一个消费者处理，组内是点对点）

Consumer Group B（审计日志组）：
  Consumer B1 ──→ Partition 0, 1, 2
  （不同组之间互相独立，组间是发布订阅）

总效果：每条消息被A组处理一次、B组处理一次
```

**重要规则**：如果消费者数量 > 分区数量，多出来的消费者会**空闲**——因为它分不到分区。因此，**分区数 = 消费者数的上限**。一般分区数设为消费者数的1~2倍，方便扩容。

---

## 88.3 Kafka为什么这么快

这是面试高频题，也是理解Kafka设计哲学的关键。

### 1. 顺序写磁盘

传统的理解：磁盘很慢，内存很快。但这句话只对了一半——**随机写磁盘很慢，顺序写磁盘很快**。

现代硬盘（SSD）的顺序写入速度可以达到几百MB/s甚至几GB/s，而Kafka的所有操作都是**顺序追加**（append-only）——新消息永远追加到日志文件末尾。没有任何随机读写、没有任何修改、没有任何删除（直到整个日志段过期）。

这就像在笔记本上记日记——从上往下一行行写（顺序写）vs 在已经写满的笔记本里找到一页空白再写（随机写）。前者是一气呵成，后者要翻来翻去。

### 2. 零拷贝（Zero Copy）

传统的网络传输流程（比如从磁盘读文件通过网络发给客户端）：

```
磁盘 → 内核缓冲区 → 用户态缓冲区 → 内核Socket缓冲区 → 网卡
```

数据在"内核态"和"用户态"之间来回拷贝了两次，CPU参与每步拷贝。

Kafka用了Linux的 `sendfile` 系统调用：

```
磁盘 → 内核缓冲区 → 网卡（内核Socket缓冲区）
```

数据从磁盘直接到网卡，不经过用户态，CPU几乎不参与。这就是"零拷贝"——数据复制的次数从4次降到2次（甚至1次），省掉了最昂贵的CPU拷贝。

### 3. Page Cache（页缓存）

操作系统会把磁盘上经常读写的数据缓存到内存中（Page Cache）。Kafka的数据是顺序读写的，访问模式非常规律，这让Page Cache的命中率极高。大多数情况下，Kafka的"读磁盘"操作实际上是在读内存。

这相当于把操作系统变成了Kafka的"免费缓存"——你不写缓存代码，操作系统自己帮你做了。

### 4. 批量压缩

Kafka的Producer和Broker都会把多条消息**打包成一个批次**（batch），一起压缩后发送。比如100条消息打包成一批：

- 网络开销从100次变成了1次
- 压缩率更高（一批数据有更多相似模式）
- 磁盘写入也更高效

Kafka支持Gzip、Snappy、LZ4、ZSTD等多种压缩算法。

### 5. 分区并行

这是Kafka的"水平扩展"能力。一个Topic分成10个分区，每个分区独立写入、独立消费：

```
Topic: logs（10个分区）
  Partition 0 → 写入 100MB/s
  Partition 1 → 写入 100MB/s
  ...
  Partition 9 → 写入 100MB/s
  ─────────────────
  总吞吐: 1000MB/s = 1GB/s
```

加一台Broker，分区分布到更多机器上，总吞吐量线性增长。这就是分布式系统的"水平扩展"。

### 快的原因总结

| 因素 | 贡献 |
|------|------|
| 顺序写磁盘 | 避免了磁盘随机寻道的开销 |
| 零拷贝（sendfile） | 省掉用户态和内核态之间的数据拷贝 |
| Page Cache | 把OS内存变成Kafka的免费缓存 |
| 批量压缩 | 减少网络和磁盘的IO次数 |
| 分区并行 | 水平扩展，吞吐量线性增长 |

> 一句话总结：**Kafka用"日志"这个最简单的数据结构（append-only），把现代操作系统的各项能力（顺序IO、零拷贝、页缓存）利用到了极致。**

---

## 88.4 安装Docker Kafka

用Docker Compose启动Kafka（需要Zookeeper或使用KRaft模式）：

**docker-compose.yml**：

```yaml
version: '3.8'
services:
  zookeeper:
    image: confluentinc/cp-zookeeper:7.5.0
    environment:
      ZOOKEEPER_CLIENT_PORT: 2181
      ZOOKEEPER_TICK_TIME: 2000
    ports:
      - "2181:2181"

  kafka:
    image: confluentinc/cp-kafka:7.5.0
    depends_on:
      - zookeeper
    ports:
      - "9092:9092"
    environment:
      KAFKA_BROKER_ID: 1
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://localhost:9092
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
```

> 注意：Kafka社区从3.3版本开始引入KRaft模式（不依赖Zookeeper），但Zookeeper模式目前仍是生产环境的主流，本书以此为例。

启动：

```bash
docker-compose up -d
```

验证：

```bash
docker-compose ps
```

---

## 88.5 基础操作

进入Kafka容器操作：

```bash
docker exec -it kafka bash
```

### 创建Topic

```bash
kafka-topics --bootstrap-server localhost:9092 \
  --create \
  --topic order-events \
  --partitions 3 \
  --replication-factor 1
```

参数解释：
- `--partitions 3`：3个分区，支持最多3个消费者并行消费
- `--replication-factor 1`：每个分区1个副本（生产环境至少3）

### 查看Topic列表

```bash
kafka-topics --bootstrap-server localhost:9092 --list
```

### 查看Topic详情

```bash
kafka-topics --bootstrap-server localhost:9092 --describe --topic order-events
```

输出示例：
```
Topic: order-events  PartitionCount: 3  ReplicationFactor: 1
  Topic: order-events  Partition: 0  Leader: 1  Replicas: 1  Isr: 1
  Topic: order-events  Partition: 1  Leader: 1  Replicas: 1  Isr: 1
  Topic: order-events  Partition: 2  Leader: 1  Replicas: 1  Isr: 1
```

### 生产消息（命令行）

```bash
kafka-console-producer --bootstrap-server localhost:9092 --topic order-events
```

然后逐行输入消息内容（每行一条消息，Ctrl+C退出）：
```
订单123创建成功
订单123已付款
订单456创建成功
```

### 消费消息（命令行）

```bash
kafka-console-consumer --bootstrap-server localhost:9092 \
  --topic order-events \
  --from-beginning
```

`--from-beginning` 表示从第一条消息开始读（Offset=0）。不指定则从最新消息开始。

运行后你会看到之前生产的三条消息被打印出来。

### 从头消费（重置Offset）

```bash
kafka-console-consumer --bootstrap-server localhost:9092 \
  --topic order-events \
  --from-beginning \
  --group my-consumer-group
```

指定 `--group` 后，Kafka会记录这个消费者组读到哪了（Offset），下次重启不会重复消费。

### 删除Topic

```bash
kafka-topics --bootstrap-server localhost:9092 --delete --topic order-events
```

---

🤔 **想多一点**：为什么Kafka的消息可以重复读？

在RabbitMQ中，消息被确认后就删除了——你不能"回到昨天重新消费一遍订单事件"。但在Kafka中，消息在Partition中保存一段时间（默认7天），你可以随时重置Offset回到之前的位置重读。

这个特性让Kafka不仅仅是一个"消息队列"，更是一个**事件存储系统**。如果你的新服务上线后需要"处理过去7天所有的订单事件"——在RabbitMQ上做不到，在Kafka上只需要把Offset重置到7天前。

这也是为什么Kafka被称为**事件溯源（Event Sourcing）**的基础设施——系统状态不是存一份最终结果，而是存一份完整的"事件日志"。任何时刻的系统状态都可以通过"重放日志"推导出来。就像银行的流水账单——你不会只存"余额100元"，你存的是"+1000、-200、+500、-300……"所有交易记录。

---

## 本章小结

| 知识点 | 要点 |
|--------|------|
| Kafka定位 | 分布式流处理平台，海量数据管道，不是传统MQ |
| Broker | Kafka服务器节点，集群通常3~5台 |
| Topic | 消息逻辑分类，被分割为多个Partition |
| Partition | 有序不可变的日志文件，Kafka并行处理的基础 |
| Offset | 消息在Partition中的唯一编号，消费者的"书签" |
| Consumer Group | 组内点对点（一个分区一个消费者），组间发布订阅 |
| 顺序写磁盘 | append-only，把OS的顺序IO能力用到了极致 |
| 零拷贝 | sendfile系统调用，数据从磁盘直达网卡，不经过用户态 |
| Page Cache | OS内存自动缓存热数据，Kafka免费获得了内存级读取速度 |
| 批量压缩 | 多条消息打包，减少IO次数，提高压缩率 |
| 分区并行 | 加分区=加吞吐，水平扩展 |
| Docker安装 | Zookeeper + Kafka，端口9092 |
| 命令行操作 | kafka-topics创建/查看，kafka-console-producer/consumer |

> 🚀 下一章：Kafka的进阶话题——分区策略怎么选？acks=all到底有多可靠？消费者Rebalance是什么？高水位HW和LEO是怎么回事？这些是Kafka面试的核心考点。

---
[← 上一章：87-RabbitMQ进阶.md](87-RabbitMQ进阶.md) | [下一章：89-Kafka进阶.md →](89-Kafka进阶.md)
