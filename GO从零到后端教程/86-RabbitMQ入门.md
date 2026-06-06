# 第86章 · RabbitMQ入门

> "如果说消息队列的世界是一个江湖，RabbitMQ就是那个最老牌的、规矩最多的、但也是最可靠的门派。本章你将亲手用Docker启动一个RabbitMQ实例，然后逐一修炼五种工作模式——从最简单的'一个发一个收'到复杂的'topic模糊匹配路由'。学完本章，你就拿到了消息队列的'驾照'。"

---

## 86.1 RabbitMQ是什么

RabbitMQ是一个基于**AMQP（高级消息队列协议）**的开源消息代理，由**Erlang**语言编写。2007年发布至今，已经在无数生产系统中服役了一二十年。

为什么用Erlang？Erlang是爱立信为了电话交换机开发的语言——天生为高并发、高可用、软实时系统设计。电话交换机一秒要处理成千上万次通话建立和挂断，一条都不能出错，一个通话都不能中断。这正好和消息队列的需求完美吻合。

就像一辆**日本皮卡**——不是最快的（吞吐量不如Kafka），也不是最时髦的（架构不如Pulsar新潮），但**极其可靠**，维修方便（社区成熟），配件到处都是（资料丰富）。

---

## 86.2 核心概念

RabbitMQ的世界由七个核心角色组成。一旦你理解了这七者之间的关系，RabbitMQ的所有配置都会变得一目了然。

```
Producer（生产者）
       │
       │ 发布消息
       ↓
   Exchange（交换机）
       │
       │ 根据RoutingKey路由
       ↓
   Binding（绑定规则）
       │
       ↓
    Queue（队列）
       │
       │ 消费者监听
       ↓
  Consumer（消费者）
```

### 1. Producer（生产者）

生产消息的人。在Go里，就是一个连接到RabbitMQ、然后调用 `Publish` 方法的程序。生产者不直接把消息送到队列——而是送到**Exchange**。

关键点：生产者只需要知道"我要发到哪个Exchange"和"RoutingKey是什么"，完全不需要知道后面有哪些队列、有哪些消费者。这就是解耦。

### 2. Exchange（交换机）

消息的第一站。Exchange不存消息——它只是看一眼消息的RoutingKey，然后按照规则**转发**到对应的队列。就像一个快递分拣中心：看到上海的去左边传送带、北京的去右边传送带——分拣中心自己不堆货。

RabbitMQ有四种交换机类型（后面详述）：

| 类型 | 行为 |
|------|------|
| Direct | 精确匹配 RoutingKey |
| Fanout | 广播给所有绑定的队列 |
| Topic | 按模式匹配 RoutingKey（支持通配符） |
| Headers | 按消息头匹配（很少用） |

### 3. Queue（队列）

真正存储消息的地方。消息在队列里排队等待消费者来取。队列的特性：
- **先进先出（FIFO）**：先到的消息先被消费
- **持久化**（可选）：重启RabbitMQ后消息还在
- **独立命名**：每个队列有自己的名字

### 4. Binding（绑定）

连接Exchange和Queue的"绳子"。Binding（绑定规则，定义消息从Exchange到Queue的路由条件，详见附录I）说："这个Exchange上的消息，如果RoutingKey是XXX，就转发到这个Queue。"

```
Exchange ─── Binding(RoutingKey="order.created") ───→ Queue
```

一个Exchange可以绑定多个Queue，一个Queue也可以从属于多个Exchange（虽然不常见）。

### 5. RoutingKey（路由键）

生产者在发送消息时指定的一个字符串。Exchange根据这个字符串决定把消息投递到哪些队列。

```
channel.Publish(
    "order_exchange",    
    "order.created",     
    false,
    false,
    amqp.Publishing{
        ContentType: "application/json",
        Body:        []byte(`{"order_id": 123}`),
    },
)
```

在上面的代码中，`"order.created"` 就是RoutingKey。

### 6. Consumer（消费者）

从队列中取消息并处理的人。消费者启动后，RabbitMQ会自动把队列中的消息推送给它（Push模式），或者消费者主动去拉（Pull模式，较少用）。

消费者处理完消息后发送**ACK（确认）**——告诉RabbitMQ"这条消息我处理完了，你可以删了"。如果消费者在处理过程中挂了、没有发送ACK，RabbitMQ会把这条消息重新投递给另一个消费者。

### 7. Connection 和 Channel

这两个概念容易混淆，但很重要：

- **Connection**：TCP长连接。你的程序和RabbitMQ之间建立的一条TCP通道。建立Connection很昂贵（三次握手、认证等）。
- **Channel**：虚拟连接，复用同一个TCP Connection。一个Connection上可以打开多个Channel。Channel的创建和销毁成本极低。

最佳实践：一个进程只建立一个Connection，然后为每个goroutine（或每种操作类型）创建一个Channel。就像一栋楼只拉一根光纤进来（Connection），每户人家分一根网线（Channel）。

```
进程
 └── Connection（TCP长连接，1个）
       ├── Channel 1（给生产者用）
       ├── Channel 2（给消费者A用）
       └── Channel 3（给消费者B用）
```

---

## 86.3 安装Docker RabbitMQ

用Docker安装RabbitMQ只需要一行命令。Docker基础知识请回顾第59章。

```bash
docker run -d \
  --name rabbitmq-tutorial \
  -p 5672:5672 \
  -p 15672:15672 \
  -e RABBITMQ_DEFAULT_USER=admin \
  -e RABBITMQ_DEFAULT_PASS=admin123 \
  rabbitmq:3.12-management
```

参数解释：
- `5672`：RabbitMQ的服务端口（你的Go程序连接这个端口）
- `15672`：管理界面端口（浏览器访问这个端口）
- `3.12-management`：带管理插件的RabbitMQ镜像
- `RABBITMQ_DEFAULT_USER/PASS`：管理界面的默认用户名和密码

启动后验证：

```bash
docker ps | grep rabbitmq
```

---

## 86.4 管理界面

打开浏览器访问 `http://localhost:15672`，用 `admin / admin123` 登录。

管理界面包含以下重点区域：

- **Overview**：总体情况，包括消息速率、连接数、队列数
- **Connections**：当前所有客户端连接
- **Channels**：当前所有Channel
- **Exchanges**：所有交换机及其绑定关系
- **Queues**：所有队列，可以看到每个队列的消息数量、消费者数量
- **Admin**：用户管理和虚拟机（vhost）管理

你可以在Queues页面手动发送消息、查看队列内容，对调试极其有用。

---

## 86.5 五种工作模式

### Go依赖安装

在开始之前，安装Go的RabbitMQ客户端库：

```bash
go get github.com/rabbitmq/amqp091-go
```

### 模式一：Simple模式（一个生产者 → 一个消费者）

最简单的模式：一根管子直通。没有交换机（使用默认交换机），没有路由规则。

```
Producer ──→ [默认Exchange] ──→ [hello队列] ──→ Consumer
```

**生产者代码**（producer_simple.go）：

```go
package main

import (
	"context"
	"log"
	"time"

	amqp "github.com/rabbitmq/amqp091-go"
)

func main() {
	conn, err := amqp.Dial("amqp://admin:admin123@localhost:5672/")
	if err != nil {
		log.Fatalf("连接RabbitMQ失败: %v", err)
	}
	defer conn.Close()

	ch, err := conn.Channel()
	if err != nil {
		log.Fatalf("打开Channel失败: %v", err)
	}
	defer ch.Close()

	q, err := ch.QueueDeclare(
		"hello", 
		false,   
		false,   
		false,   
		false,   
		nil,     
	)
	if err != nil {
		log.Fatalf("声明队列失败: %v", err)
	}

	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	body := "你好，消息队列！"
	err = ch.PublishWithContext(
		ctx,
		"",     
		q.Name, 
		false,  
		false,  
		amqp.Publishing{
			ContentType: "text/plain",
			Body:        []byte(body),
		},
	)
	if err != nil {
		log.Fatalf("发送消息失败: %v", err)
	}

	log.Printf(" [x] 发送: %s", body)
}
```

**消费者代码**（consumer_simple.go）：

```go
package main

import (
	"log"

	amqp "github.com/rabbitmq/amqp091-go"
)

func main() {
	conn, err := amqp.Dial("amqp://admin:admin123@localhost:5672/")
	if err != nil {
		log.Fatalf("连接RabbitMQ失败: %v", err)
	}
	defer conn.Close()

	ch, err := conn.Channel()
	if err != nil {
		log.Fatalf("打开Channel失败: %v", err)
	}
	defer ch.Close()

	q, err := ch.QueueDeclare(
		"hello", 
		false,   
		false,   
		false,   
		false,   
		nil,     
	)
	if err != nil {
		log.Fatalf("声明队列失败: %v", err)
	}

	msgs, err := ch.Consume(
		q.Name, 
		"",     
		true,   
		false,  
		false,  
		false,  
		nil,    
	)
	if err != nil {
		log.Fatalf("注册消费者失败: %v", err)
	}

	forever := make(chan struct{})
	go func() {
		for d := range msgs {
			log.Printf("收到消息: %s", d.Body)
		}
	}()
	log.Printf(" [*] 等待消息中，按CTRL+C退出")
	<-forever
}
```

先运行消费者，再运行生产者，消费者终端会打印出"你好，消息队列！"。

### 模式二：Work Queue模式（多个消费者竞争消费）

多个消费者监听同一个队列，每条消息只会被一个消费者处理（竞争关系）。谁先抢到算谁的——天然实现了**负载均衡**。

```
               ┌─────→ Consumer A（抢到msg1, msg3）
Producer ──→ [task_queue] ──┤
               └─────→ Consumer B（抢到msg2）
```

场景：异步发送邮件。高峰期有1000封邮件要发，一个消费者得发一小时。启动5个消费者，每人分200封，十分钟搞定。

**生产者**（producer_worker.go）：

```go
package main

import (
	"context"
	"fmt"
	"log"
	"strconv"
	"time"

	amqp "github.com/rabbitmq/amqp091-go"
)

func main() {
	conn, err := amqp.Dial("amqp://admin:admin123@localhost:5672/")
	if err != nil {
		log.Fatalf("连接失败: %v", err)
	}
	defer conn.Close()

	ch, err := conn.Channel()
	if err != nil {
		log.Fatalf("打开Channel失败: %v", err)
	}
	defer ch.Close()

	q, err := ch.QueueDeclare(
		"task_queue",
		true,  
		false, 
		false, 
		false, 
		nil,   
	)
	if err != nil {
		log.Fatalf("声明队列失败: %v", err)
	}

	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	for i := 1; i <= 10; i++ {
		body := fmt.Sprintf("任务 #%d", i)
		err = ch.PublishWithContext(
			ctx,
			"",
			q.Name,
			false,
			false,
			amqp.Publishing{
				DeliveryMode: amqp.Persistent,
				ContentType:  "text/plain",
				Body:         []byte(body),
			},
		)
		if err != nil {
			log.Fatalf("发送失败: %v", err)
		}
		log.Printf(" [x] 发送: %s", body)
		time.Sleep(200 * time.Millisecond)
	}
}
```

**消费者**（consumer_worker.go）：

```go
package main

import (
	"bytes"
	"log"
	"time"

	amqp "github.com/rabbitmq/amqp091-go"
)

func main() {
	conn, err := amqp.Dial("amqp://admin:admin123@localhost:5672/")
	if err != nil {
		log.Fatalf("连接失败: %v", err)
	}
	defer conn.Close()

	ch, err := conn.Channel()
	if err != nil {
		log.Fatalf("打开Channel失败: %v", err)
	}
	defer ch.Close()

	q, err := ch.QueueDeclare(
		"task_queue",
		true,  
		false, 
		false, 
		false, 
		nil,   
	)
	if err != nil {
		log.Fatalf("声明队列失败: %v", err)
	}

	err = ch.Qos(
		1,     
		0,     
		false, 
	)
	if err != nil {
		log.Fatalf("设置Qos失败: %v", err)
	}

	msgs, err := ch.Consume(
		q.Name,
		"",
		false, 
		false, 
		false, 
		false, 
		nil,   
	)
	if err != nil {
		log.Fatalf("注册消费者失败: %v", err)
	}

	forever := make(chan struct{})
	go func() {
		for d := range msgs {
			log.Printf("收到: %s", d.Body)
			dotCount := bytes.Count(d.Body, []byte("."))
			t := time.Duration(dotCount+1) * time.Second
			time.Sleep(t)
			log.Printf("完成: %s（处理了%v）", d.Body, t)
			d.Ack(false)
		}
	}()
	log.Printf(" [*] 等待消息，按CTRL+C退出")
	<-forever
}
```

关键变化：
1. `d.Ack(false)` — 手动确认，消费者处理完才告诉RabbitMQ"我好了"
2. `ch.Qos(1, ...)` — 每次只取一条消息（公平分发，见87章详述）
3. `DeliveryMode: amqp.Persistent` — 消息持久化到磁盘

### 模式三：Publish/Subscribe（发布订阅——Fanout广播）

生产者发一条消息，所有绑定到Exchange的队列都能收到。交换机类型：**fanout**（扇出——像扇子一样散开）。

```
                              ┌──→ [queue_a] ──→ Consumer A
Producer ──→ [logs_exchange] ──┤
                   (fanout)    └──→ [queue_b] ──→ Consumer B
```

**生产者**（producer_pubsub.go）：

```go
package main

import (
	"context"
	"log"
	"time"

	amqp "github.com/rabbitmq/amqp091-go"
)

func main() {
	conn, err := amqp.Dial("amqp://admin:admin123@localhost:5672/")
	if err != nil {
		log.Fatalf("连接失败: %v", err)
	}
	defer conn.Close()

	ch, err := conn.Channel()
	if err != nil {
		log.Fatalf("打开Channel失败: %v", err)
	}
	defer ch.Close()

	err = ch.ExchangeDeclare(
		"logs",
		"fanout",
		true,  
		false, 
		false, 
		false, 
		nil,   
	)
	if err != nil {
		log.Fatalf("声明Exchange失败: %v", err)
	}

	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	body := "系统通知：今晚10点服务器维护"
	err = ch.PublishWithContext(
		ctx,
		"logs",
		"",
		false,
		false,
		amqp.Publishing{
			ContentType: "text/plain",
			Body:        []byte(body),
		},
	)
	if err != nil {
		log.Fatalf("发送失败: %v", err)
	}

	log.Printf(" [x] 广播: %s", body)
}
```

注意：`PublishWithContext`的第二个参数（RoutingKey）为空字符串——fanout交换机不关心RoutingKey，直接广播给所有绑定的队列。

**消费者**（consumer_pubsub.go）：

```go
package main

import (
	"log"

	amqp "github.com/rabbitmq/amqp091-go"
)

func main() {
	conn, err := amqp.Dial("amqp://admin:admin123@localhost:5672/")
	if err != nil {
		log.Fatalf("连接失败: %v", err)
	}
	defer conn.Close()

	ch, err := conn.Channel()
	if err != nil {
		log.Fatalf("打开Channel失败: %v", err)
	}
	defer ch.Close()

	err = ch.ExchangeDeclare(
		"logs",
		"fanout",
		true,
		false,
		false,
		false,
		nil,
	)
	if err != nil {
		log.Fatalf("声明Exchange失败: %v", err)
	}

	q, err := ch.QueueDeclare(
		"",
		false,
		false,
		true, 
		false,
		nil,
	)
	if err != nil {
		log.Fatalf("声明队列失败: %v", err)
	}

	err = ch.QueueBind(
		q.Name,
		"",
		"logs",
		false,
		nil,
	)
	if err != nil {
		log.Fatalf("绑定队列失败: %v", err)
	}

	msgs, err := ch.Consume(
		q.Name,
		"",
		true,
		false,
		false,
		false,
		nil,
	)
	if err != nil {
		log.Fatalf("注册消费者失败: %v", err)
	}

	forever := make(chan struct{})
	go func() {
		for d := range msgs {
			log.Printf(" [x] %s", d.Body)
		}
	}()
	log.Printf(" [*] 等待消息，按CTRL+C退出")
	<-forever
}
```

关键点：
1. 队列名为空字符串 → RabbitMQ自动生成一个随机队列名（`autoDelete=true`）
2. 消费者断开连接时队列自动删除（不留下垃圾队列）
3. `QueueBind`把队列绑定到`logs` Exchange

**验证**：启动两个消费者，然后运行一次生产者。两个消费者都会收到同一条消息。

### 模式四：Routing模式（Direct——精确匹配）

交换机类型：**direct**。根据RoutingKey**精确匹配**，把消息路由到对应队列。

```
               RoutingKey="error" ───→ [error_queue] ──→ 告警消费者
Producer ──→ [direct_logs]
               RoutingKey="info"  ───→ [info_queue]  ──→ 日志存档消费者
```

**生产者**（producer_routing.go）：

```go
package main

import (
	"context"
	"log"
	"time"

	amqp "github.com/rabbitmq/amqp091-go"
)

func main() {
	conn, err := amqp.Dial("amqp://admin:admin123@localhost:5672/")
	if err != nil {
		log.Fatalf("连接失败: %v", err)
	}
	defer conn.Close()

	ch, err := conn.Channel()
	if err != nil {
		log.Fatalf("打开Channel失败: %v", err)
	}
	defer ch.Close()

	err = ch.ExchangeDeclare(
		"direct_logs",
		"direct",
		true,
		false,
		false,
		false,
		nil,
	)
	if err != nil {
		log.Fatalf("声明Exchange失败: %v", err)
	}

	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	severities := []string{"info", "warning", "error", "info", "error"}
	for i, severity := range severities {
		body := severity + " 日志 #" + string(rune('0'+i+1))
		err = ch.PublishWithContext(
			ctx,
			"direct_logs",
			severity,
			false,
			false,
			amqp.Publishing{
				ContentType: "text/plain",
				Body:        []byte(body),
			},
		)
		if err != nil {
			log.Fatalf("发送失败: %v", err)
		}
		log.Printf(" [x] 发送[%s]: %s", severity, body)
	}
}
```

**消费者**（consumer_routing.go，接收error和warning）：

```go
package main

import (
	"log"
	"os"

	amqp "github.com/rabbitmq/amqp091-go"
)

func main() {
	conn, err := amqp.Dial("amqp://admin:admin123@localhost:5672/")
	if err != nil {
		log.Fatalf("连接失败: %v", err)
	}
	defer conn.Close()

	ch, err := conn.Channel()
	if err != nil {
		log.Fatalf("打开Channel失败: %v", err)
	}
	defer ch.Close()

	err = ch.ExchangeDeclare(
		"direct_logs",
		"direct",
		true,
		false,
		false,
		false,
		nil,
	)
	if err != nil {
		log.Fatalf("声明Exchange失败: %v", err)
	}

	q, err := ch.QueueDeclare(
		"",
		false,
		false,
		true,
		false,
		nil,
	)
	if err != nil {
		log.Fatalf("声明队列失败: %v", err)
	}

	for _, s := range os.Args[1:] {
		log.Printf("绑定RoutingKey: %s", s)
		err = ch.QueueBind(
			q.Name,
			s,
			"direct_logs",
			false,
			nil,
		)
		if err != nil {
			log.Fatalf("绑定失败: %v", err)
		}
	}

	msgs, err := ch.Consume(
		q.Name,
		"",
		true,
		false,
		false,
		false,
		nil,
	)
	if err != nil {
		log.Fatalf("注册消费者失败: %v", err)
	}

	forever := make(chan struct{})
	go func() {
		for d := range msgs {
			log.Printf(" [x] %s", d.Body)
		}
	}()
	log.Printf(" [*] 等待消息，按CTRL+C退出")
	<-forever
}
```

启动消费者时指定要接收的RoutingKey：
```bash
go run consumer_routing.go error warning
```

这个消费者只会收到error和warning级别的日志——info日志不会发到它这里。

### 模式五：Topics模式（Topic——模糊匹配）

交换机类型：**topic**。RoutingKey用点号分隔（`订单.创建.成功`），消费者用通配符匹配：
- `*` 匹配**一个**单词
- `#` 匹配**零个或多个**单词

```
RoutingKey示例：
  订单.创建.成功
  订单.取消.超时
  用户.注册.新用户
  物流.发货.顺丰

绑定模式示例：
  订单.*.成功   → 匹配"订单.创建.成功"、"订单.支付.成功"
  订单.#        → 匹配所有以"订单"开头的消息
  #.新用户      → 匹配所有以"新用户"结尾的消息
  *.*.顺丰     → 匹配所有以"顺丰"结尾且共3段的消息
```

**生产者**（producer_topics.go）：

```go
package main

import (
	"context"
	"log"
	"time"

	amqp "github.com/rabbitmq/amqp091-go"
)

func main() {
	conn, err := amqp.Dial("amqp://admin:admin123@localhost:5672/")
	if err != nil {
		log.Fatalf("连接失败: %v", err)
	}
	defer conn.Close()

	ch, err := conn.Channel()
	if err != nil {
		log.Fatalf("打开Channel失败: %v", err)
	}
	defer ch.Close()

	err = ch.ExchangeDeclare(
		"topic_logs",
		"topic",
		true,
		false,
		false,
		false,
		nil,
	)
	if err != nil {
		log.Fatalf("声明Exchange失败: %v", err)
	}

	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	messages := map[string]string{
		"order.create.success":   "订单创建成功: #12345",
		"order.cancel.timeout":   "订单超时取消: #12346",
		"user.register.new":     "新用户注册: 张三",
		"order.pay.success":     "订单支付成功: #12345",
		"logistics.ship.shunfeng": "顺丰发货: SF123456",
	}

	for key, body := range messages {
		err = ch.PublishWithContext(
			ctx,
			"topic_logs",
			key,
			false,
			false,
			amqp.Publishing{
				ContentType: "text/plain",
				Body:        []byte(body),
			},
		)
		if err != nil {
			log.Fatalf("发送失败: %v", err)
		}
		log.Printf(" [x] 发送[%s]: %s", key, body)
	}
}
```

**消费者A**（接收所有订单相关消息，`order.#`）：

```go
package main

import (
	"log"
	"os"

	amqp "github.com/rabbitmq/amqp091-go"
)

func main() {
	conn, err := amqp.Dial("amqp://admin:admin123@localhost:5672/")
	if err != nil {
		log.Fatalf("连接失败: %v", err)
	}
	defer conn.Close()

	ch, err := conn.Channel()
	if err != nil {
		log.Fatalf("打开Channel失败: %v", err)
	}
	defer ch.Close()

	err = ch.ExchangeDeclare(
		"topic_logs",
		"topic",
		true,
		false,
		false,
		false,
		nil,
	)
	if err != nil {
		log.Fatalf("声明Exchange失败: %v", err)
	}

	q, err := ch.QueueDeclare(
		"",
		false,
		false,
		true,
		false,
		nil,
	)
	if err != nil {
		log.Fatalf("声明队列失败: %v", err)
	}

	for _, bindingKey := range os.Args[1:] {
		log.Printf("绑定模式: %s", bindingKey)
		err = ch.QueueBind(
			q.Name,
			bindingKey,
			"topic_logs",
			false,
			nil,
		)
		if err != nil {
			log.Fatalf("绑定失败: %v", err)
		}
	}

	msgs, err := ch.Consume(
		q.Name,
		"",
		true,
		false,
		false,
		false,
		nil,
	)
	if err != nil {
		log.Fatalf("注册消费者失败: %v", err)
	}

	forever := make(chan struct{})
	go func() {
		for d := range msgs {
			log.Printf(" [订单消费者] RoutingKey=%s: %s", d.RoutingKey, d.Body)
		}
	}()
	log.Printf(" [*] 等待消息，按CTRL+C退出")
	<-forever
}
```

**消费者B**（接收物流相关 + 所有#结尾的，`logistics.#` 和 `*.*.shunfeng`）：

```bash
go run consumer_topics.go "logistics.#" "*.*.shunfeng"
```

运行生产者后：
- 消费者A（`order.#`）收到：order.create.success、order.cancel.timeout、order.pay.success
- 消费者B用 `logistics.#` 收到物流消息（logistics.ship.shunfeng）。`order.pay.success` 不匹配 `*.*.shunfeng`，因为末段是 `success` 而非 `shunfeng`。

---

🤔 **想多一点**：五种模式该选哪个？

很多初学者会纠结："我的场景到底该用direct还是topic？"一个简单的决策逻辑：

1. 如果你只是"一个任务找人做" → **Work Queue**（Simple是它的特例）
2. 你需要"一条消息同时发给多个人" → 考虑Fanout还是Direct/Topic
3. 所有人都要收到 → **Fanout**
4. 按"类别"区分（error给A，info给B）→ **Direct**
5. 按"层级/层级关系"区分（订单相关的都给A，支付相关的给B）→ **Topic**

如果还不确定，直接选**Topic**——它最灵活，兼容性最好。你完全可以用topic模拟direct（只用完整的单词做精确匹配，不用通配符）和fanout（用 `#` 匹配所有）。

---

## 本章小结

| 知识点 | 要点 |
|--------|------|
| RabbitMQ | AMQP协议，Erlang实现，功能丰富的消息代理 |
| 核心七角色 | Producer→Exchange→Binding→Queue→Consumer，外加Connection和Channel |
| Connection vs Channel | Connection是TCP连接，Channel是复用该连接的虚拟通道 |
| Docker安装 | `rabbitmq:3.12-management`，端口5672（服务）和15672（管理界面） |
| Simple模式 | 默认Exchange，一个生产者一个消费者 |
| Work Queue | 多个消费者竞争消费，公平分发（Qos=1），手动ACK |
| Publish/Subscribe | Fanout Exchange，广播给所有绑定的队列 |
| Routing | Direct Exchange，按RoutingKey精确匹配路由 |
| Topics | Topic Exchange，`*`匹配一个单词，`#`匹配零或多个单词 |

> 🚀 下一章：五种模式只是"会用"RabbitMQ。下一章你将进入进阶实战——消息确认ACK到底怎么保证不丢？死信队列怎么处理"坏消息"？30分钟未支付怎么自动取消订单？这些才是生产环境的真正核心。

---
[← 上一章：85-消息队列基础.md](85-消息队列基础/) | [下一章：87-RabbitMQ进阶.md →](87-RabbitMQ进阶/)
