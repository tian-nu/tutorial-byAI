# 95-RabbitMQ入门

> 💡 你去邮局寄信。你把信放进"寄往北京的筐"，邮递员从筐里取走信，送到北京。RabbitMQ 的核心就是"Exchange（交换机）+ Queue（队列）+ Binding（绑定）"——你投递到某个交换机，交换机根据规则把消息路由到正确的队列。

---

## 本章目标
- 安装并启动 RabbitMQ
- 理解 Exchange / Queue / Binding / Routing Key 的关系
- 掌握 4 种 Exchange 类型
- 用 Java 客户端发送和接收消息

---

## 95.1 安装 RabbitMQ（一行命令）

```bash
docker run -d --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3-management
```

> 📖 Docker 详细教程见第112章。如果对 Docker 不熟悉，先复制粘贴这行命令即可。

启动后：
- **5672**：AMQP 协议端口（Java 客户端用这个）
- **15672**：管理后台端口（浏览器访问 `http://localhost:15672`）
- 默认用户名：`guest`，密码：`guest`

---

## 95.2 AMQP 协议核心模型

```
Producer 发消息                                      Consumer 收消息
    │                                                     ▲
    │  "我把消息发到 Exchange"                              │  "我从 Queue 取消息"
    ▼                                                     │
┌──────────┐   Binding + Routing Key   ┌──────────┐      │
│ Exchange │ ─────────────────────────→│  Queue   │──────┘
│ (交换机)  │                            │ (队列)   │
└──────────┘                            └──────────┘
```

| 组件 | 职责 |
|------|------|
| **Exchange** | 接收生产者消息，决定路由到哪个队列 |
| **Queue** | 存储消息，直到被消费者取走 |
| **Binding** | Exchange 和 Queue 之间的连接关系 |
| **Routing Key** | 消息的"收件地址"，Exchange 根据它决定投递到哪个 Queue |

> 🤔 想多一点：生产者**从不直接发消息给 Queue**。生产者只和 Exchange 打交道。Queue 由消费者创建和绑定。这带来了极大的灵活性——你可以在不重启生产者的情况下，新增队列、修改路由规则。

---

## 95.3 四种 Exchange 类型

### 1. Direct Exchange（直连交换机）

```
Routing Key = "error"  → Queue_ErrorLog
Routing Key = "info"   → Queue_InfoLog
```

精确匹配 Routing Key。适用于**按日志级别分发**、按业务类型路由。

### 2. Fanout Exchange（广播交换机）

```
忽略 Routing Key → 绑定到该 Exchange 的所有 Queue 都收到
```

适用于**新闻推送**、**配置更新广播**。

### 3. Topic Exchange（主题交换机）

```
Routing Key = "order.us.created"  → Queue_UsOrder
Routing Key = "order.cn.created"  → Queue_CnOrder
Routing Key = "order.*.created"   → 都匹配
```

Routing Key 支持通配符：
- `*` 匹配恰好一个单词
- `#` 匹配零个或多个单词

### 4. Headers Exchange（头交换机）

根据消息的 Header 属性匹配，而不是 Routing Key。很少用。

---

## 95.4 Java 客户端——发送消息

### 依赖

```xml
<dependency>
    <groupId>com.rabbitmq</groupId>
    <artifactId>amqp-client</artifactId>
    <version>5.21.0</version>
</dependency>
```

### 生产者

```java
public class Producer {

    private static final String QUEUE_NAME = "hello_queue";

    public static void main(String[] args) throws Exception {
        ConnectionFactory factory = new ConnectionFactory();
        factory.setHost("localhost");
        factory.setPort(5672);
        factory.setUsername("guest");
        factory.setPassword("guest");

        try (Connection connection = factory.newConnection();
             Channel channel = connection.createChannel()) {

            channel.queueDeclare(QUEUE_NAME, false, false, false, null);

            String message = "Hello RabbitMQ!";
            channel.basicPublish("", QUEUE_NAME, null, message.getBytes());
            System.out.println(" [x] 发送: '" + message + "'");
        }
    }
}
```

### 消费者

```java
public class Consumer {

    private static final String QUEUE_NAME = "hello_queue";

    public static void main(String[] args) throws Exception {
        ConnectionFactory factory = new ConnectionFactory();
        factory.setHost("localhost");
        factory.setPort(5672);
        factory.setUsername("guest");
        factory.setPassword("guest");

        Connection connection = factory.newConnection();
        Channel channel = connection.createChannel();

        channel.queueDeclare(QUEUE_NAME, false, false, false, null);
        System.out.println(" [*] 等待消息...");

        DeliverCallback deliverCallback = (consumerTag, delivery) -> {
            String message = new String(delivery.getBody(), "UTF-8");
            System.out.println(" [x] 收到: '" + message + "'");
        };

        channel.basicConsume(QUEUE_NAME, true, deliverCallback, consumerTag -> {});
    }
}
```

---

## 95.5 queueDeclare 参数详解

```java
channel.queueDeclare(String queue, boolean durable, boolean exclusive,
                     boolean autoDelete, Map<String, Object> arguments);
```

| 参数 | 说明 |
|------|------|
| `queue` | 队列名称 |
| `durable` | `true` = 队列持久化（Broker 重启后队列不丢） |
| `exclusive` | `true` = 只被当前连接使用，连接关闭时自动删除 |
| `autoDelete` | `true` = 最后一个消费者断开后，队列自动删除 |
| `arguments` | 扩展参数（TTL、死信队列等） |

---

## 95.6 使用 Direct Exchange 的完整示例

```java
// 生产者
try (Connection connection = factory.newConnection();
     Channel channel = connection.createChannel()) {

    channel.exchangeDeclare("logs_direct", BuiltinExchangeType.DIRECT);

    // 发送 error 级别日志
    channel.basicPublish("logs_direct", "error", null, "Disk full!".getBytes());
    // 发送 info 级别日志
    channel.basicPublish("logs_direct", "info", null, "Server started".getBytes());
}

// 消费者
channel.exchangeDeclare("logs_direct", BuiltinExchangeType.DIRECT);
String queueName = channel.queueDeclare().getQueue();
channel.queueBind(queueName, "logs_direct", "error");  // 只接收 error

DeliverCallback callback = (consumerTag, delivery) -> {
    String routingKey = delivery.getEnvelope().getRoutingKey();
    String message = new String(delivery.getBody());
    System.out.println(" [" + routingKey + "] " + message);
};
channel.basicConsume(queueName, true, callback, consumerTag -> {});
```

---

## 95.7 管理后台一览

访问 `http://localhost:15672`，你会看到：

| Tab | 功能 |
|------|------|
| Overview | 消息速率、连接数、内存/磁盘使用 |
| Connections | 当前所有客户端连接 |
| Channels | 连接内的信道（轻量连接） |
| Exchanges | 所有交换机及绑定关系 |
| Queues | 所有队列，可查看消息数、消费者数 |

---

## 95.8 小结

| 知识点 | 核心内容 |
|--------|----------|
| 安装 | `docker run -d --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3-management` |
| 核心组件 | Exchange（路由） + Queue（存储） + Binding（连接） |
| 四种 Exchange | Direct（精确）、Fanout（广播）、Topic（通配符）、Headers（头匹配） |
| Java 客户端 | `ConnectionFactory → Connection → Channel → basicPublish/basicConsume` |

---

## 95.9 自测题

**1. 生产者能不能直接向某个 Queue 发送消息？为什么 RabbitMQ 要引入 Exchange 这个中间层？**

**2. 你需要实现：用户注册后，短信服务和邮件服务都能收到通知。该用哪种 Exchange？Routing Key 怎么设置？**

**3. 以下代码中的 `basicPublish` 各参数是什么含义？**

```java
channel.basicPublish("order_exchange", "order.created", null, message.getBytes());
```

---

**答案提示**：1→可以（对默认的无名 Exchange 使用空字符串 + queue name），但不推荐。Exchange 层将路由逻辑与队列解耦——新增队列不需要改生产者代码，只需添加 Binding。2→Fanout Exchange，不需要 Routing Key（或者任意值），两个服务各自声明自己的队列并绑定到同一个 Fanout Exchange。3→第一个参数 `order_exchange` 是 Exchange 名称；第二个参数 `order.created` 是 Routing Key；第三个参数是消息属性（`null` = 默认）；第四个参数是消息体字节数组。下一章——RabbitMQ 进阶。