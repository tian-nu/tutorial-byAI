# 99-Spring集成消息队列

> 💡 你用最基础的 `amqp-client` 连 RabbitMQ，每次都要写 20 行连接代码——这就像你每次开车都要亲手拧钥匙、调后视镜、系安全带。Spring Boot 的 `spring-boot-starter-amqp` 等于给你配了一个智能座舱——上车自动识别你、后视镜自动调好、一键启动。本章教你用 Spring 的方式优雅地发送和消费消息。

---

## 本章目标
- 用 Spring AMQP 集成 RabbitMQ（发送 + 监听）
- 用 Spring Kafka 集成 Kafka（发送 + 监听）
- 理解 `RabbitTemplate` / `KafkaTemplate` 的用法
- 学会配置死信队列、消息确认、重试策略

---

## 99.1 Spring AMQP（RabbitMQ 集成）

### 依赖

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-amqp</artifactId>
</dependency>
```

### application.yml

```yaml
spring:
  rabbitmq:
    host: localhost
    port: 5672
    username: guest
    password: guest
    listener:
      simple:
        acknowledge-mode: manual     # 手动确认
        prefetch: 1                  # 每次取一条
        retry:
          enabled: true
          max-attempts: 3            # 重试 3 次
          initial-interval: 1000     # 首次重试间隔 1s
```

### 配置类

```java
@Configuration
public class RabbitConfig {

    public static final String ORDER_EXCHANGE = "order.exchange";
    public static final String ORDER_QUEUE = "order.queue";

    @Bean
    public DirectExchange orderExchange() {
        return new DirectExchange(ORDER_EXCHANGE);
    }

    @Bean
    public Queue orderQueue() {
        return QueueBuilder.durable(ORDER_QUEUE)
                .deadLetterExchange("dead.letter.exchange")
                .deadLetterRoutingKey("dead.order")
                .build();
    }

    @Bean
    public Binding orderBinding() {
        return BindingBuilder.bind(orderQueue())
                .to(orderExchange())
                .with("order.created");
    }

    @Bean
    public MessageConverter messageConverter() {
        return new Jackson2JsonMessageConverter();  // JSON 序列化
    }
}
```

### 发送消息

```java
@Service
@RequiredArgsConstructor
public class OrderMessageSender {

    private final RabbitTemplate rabbitTemplate;

    public void sendOrderCreated(Long orderId) {
        OrderMessage message = new OrderMessage(orderId, "CREATED", LocalDateTime.now());
        rabbitTemplate.convertAndSend(
                RabbitConfig.ORDER_EXCHANGE,
                "order.created",
                message
        );
    }
}
```

### 接收消息

```java
@Component
@Slf4j
public class OrderMessageListener {

    @RabbitListener(queues = RabbitConfig.ORDER_QUEUE)
    public void handleOrderCreated(OrderMessage message, Channel channel,
                                    @Header(AmqpHeaders.DELIVERY_TAG) long deliveryTag) {
        try {
            log.info("收到订单创建消息: {}", message);
            processOrder(message);
            channel.basicAck(deliveryTag, false);
        } catch (Exception e) {
            log.error("处理订单消息失败: {}", message, e);
            try {
                // 重新入队（如果还要重试）或拒绝（进入死信）
                channel.basicNack(deliveryTag, false, false);
            } catch (IOException ex) {
                log.error("nack失败", ex);
            }
        }
    }

    private void processOrder(OrderMessage message) {
        // 业务处理
    }
}
```

> ⚠️ `@RabbitListener` 的方法参数可以自动注入 `Channel` 和消息头信息，只需加上对应注解。

---

## 99.2 Spring Kafka 集成

### 依赖

```xml
<dependency>
    <groupId>org.springframework.kafka</groupId>
    <artifactId>spring-kafka</artifactId>
</dependency>
```

### application.yml

```yaml
spring:
  kafka:
    bootstrap-servers: localhost:9092
    producer:
      key-serializer: org.apache.kafka.common.serialization.StringSerializer
      value-serializer: org.springframework.kafka.support.serializer.JsonSerializer
      acks: all
    consumer:
      group-id: order-processing-group
      key-deserializer: org.apache.kafka.common.serialization.StringDeserializer
      value-deserializer: org.springframework.kafka.support.serializer.JsonDeserializer
      properties:
        spring.json.trusted.packages: "com.example.demo.dto"
      enable-auto-commit: false
```

### 配置类

```java
@Configuration
public class KafkaConfig {

    @Bean
    public NewTopic orderTopic() {
        return TopicBuilder.name("order-events")
                .partitions(3)
                .replicas(1)
                .build();
    }
}
```

### 发送消息

```java
@Service
@RequiredArgsConstructor
public class OrderKafkaSender {

    private final KafkaTemplate<String, Object> kafkaTemplate;

    public void sendOrderCreated(Long orderId) {
        OrderMessage message = new OrderMessage(orderId, "CREATED", LocalDateTime.now());

        kafkaTemplate.send("order-events", String.valueOf(orderId), message)
                .whenComplete((result, ex) -> {
                    if (ex == null) {
                        log.info("消息发送成功: offset={}, partition={}",
                                result.getRecordMetadata().offset(),
                                result.getRecordMetadata().partition());
                    } else {
                        log.error("消息发送失败", ex);
                    }
                });
    }
}
```

### 接收消息

```java
@Component
@Slf4j
public class OrderKafkaListener {

    @KafkaListener(topics = "order-events", groupId = "order-processing-group")
    public void handleOrder(OrderMessage message,
                            @Header(KafkaHeaders.RECEIVED_PARTITION) int partition,
                            @Header(KafkaHeaders.OFFSET) long offset) {
        log.info("收到消息: partition={}, offset={}, data={}", partition, offset, message);
        processOrder(message);
    }

    private void processOrder(OrderMessage message) {
        // 业务处理
    }
}
```

---

## 99.3 消息实体定义

```java
@Data
@NoArgsConstructor
@AllArgsConstructor
public class OrderMessage implements Serializable {

    private static final long serialVersionUID = 1L;

    private Long orderId;
    private String status;
    private LocalDateTime timestamp;

    @JsonSerialize(using = LocalDateTimeSerializer.class)
    @JsonDeserialize(using = LocalDateTimeDeserializer.class)
    public LocalDateTime getTimestamp() {
        return timestamp;
    }
}
```

---

## 99.4 RabbitMQ vs Kafka 在 Spring 中的对比

| | Spring AMQP (RabbitMQ) | Spring Kafka |
|------|------|------|
| 核心类 | `RabbitTemplate` | `KafkaTemplate` |
| 监听注解 | `@RabbitListener` | `@KafkaListener` |
| 配置前缀 | `spring.rabbitmq.*` | `spring.kafka.*` |
| 序列化 | `Jackson2JsonMessageConverter` | `JsonSerializer` / `JsonDeserializer` |
| 手动确认 | `basicAck` / `basicNack` | `Acknowledgment.acknowledge()` |
| 自动创建资源 | ✅ Queue/Exchange/Binding | ✅ Topic（通过 `NewTopic` Bean） |

---

## 99.5 错误处理与重试

### RabbitMQ 重试配置

```yaml
spring:
  rabbitmq:
    listener:
      simple:
        retry:
          enabled: true
          max-attempts: 5
          initial-interval: 2000ms
          multiplier: 2.0         # 间隔翻倍：2s → 4s → 8s → 16s
          max-interval: 30000ms
```

### Kafka 错误处理（Spring Kafka 方式）

```java
@Configuration
public class KafkaErrorConfig {

    @Bean
    public DefaultErrorHandler errorHandler() {
        // 重试 3 次，间隔 1 秒，失败后暂停 10 秒再继续
        DefaultErrorHandler handler = new DefaultErrorHandler(
                (record, exception) -> {
                    log.error("消息处理最终失败: {}", record, exception);
                },
                new FixedBackOff(1000L, 3L)
        );
        return handler;
    }
}
```

---

## 99.6 小结

| 知识点 | Spring AMQP | Spring Kafka |
|--------|-------------|--------------|
| 发送消息 | `rabbitTemplate.convertAndSend()` | `kafkaTemplate.send()` |
| 接收消息 | `@RabbitListener` | `@KafkaListener` |
| 序列化 | `Jackson2JsonMessageConverter` | `JsonSerializer` / `JsonDeserializer` |
| 配置前缀 | `spring.rabbitmq` | `spring.kafka` |
| 重试 | `listener.simple.retry` | `DefaultErrorHandler` |

---

## 99.7 自测题

**1. `@RabbitListener` 注解的方法中，如何实现手动 ACK？需要传递哪两个参数？**

**2. Spring Kafka 中 `@KafkaListener` 的 `groupId` 属性有什么作用？如果不指定会怎样？**

**3. 你有一台 Spring Boot 服务器，同时集成了 RabbitMQ 和 Kafka。`application.yml` 中分别用什么前缀配置它们？会不会有冲突？**

---

**答案提示**：1→需要传 `Channel channel` 和 `@Header(AmqpHeaders.DELIVERY_TAG) long deliveryTag`，在方法中调用 `channel.basicAck(deliveryTag, false)`。2→`groupId` 指定消费者组。不指定时 Spring 会使用默认 groupId（通常是 `application.properties` 中的 `spring.application.name`）。3→`spring.rabbitmq.*` 和 `spring.kafka.*`，前缀不同，不存在冲突。下一章——设计模式（Java 实现）。