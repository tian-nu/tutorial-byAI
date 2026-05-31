# 第14章 · WebSocket

> "HTTP是'你问一句，我答一句'——请求-响应模式。但如果你需要'实时聊天'呢？发完消息后等着对方回复，HTTP就得不停轮询'有新消息吗？有新消息吗？'——WebSocket解决了这个问题。"

## 14.1 WebSocket是什么

**WebSocket** 是一种在单个TCP连接上进行**全双工通信**的协议。和HTTP的关键区别：

| | HTTP | WebSocket |
|---|------|-----------|
| 通信方向 | 客户端请求→服务端响应（单向发起） | 双向，任一方可随时发送 |
| 连接 | 短连接/长连接 | 持久连接 |
| 开销 | 每次请求带完整请求头 | 建立后头部极小 |
| 协议 | http:// 或 https:// | ws:// 或 wss:// |
| 适用场景 | 页面加载、表单提交、API调用 | 聊天、实时通知、股票行情、在线协作 |

### 比喻

- **HTTP**：你去窗口办事，每次只能问一个问题，然后回座位。想再问必须重新排队。
- **WebSocket**：你跟朋友视频通话，双方可以随时说话，连线一直保持。

## 14.2 WebSocket握手

WebSocket连接借用了HTTP来"升级"：

```
客户端 → GET /chat HTTP/1.1
         Host: example.com
         Upgrade: websocket               ← "我想升级成WebSocket"
         Connection: Upgrade
         Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==

服务端 → HTTP/1.1 101 Switching Protocols  ← "好的，切换协议"
         Upgrade: websocket
         Connection: Upgrade
         Sec-WebSocket-Accept: s3pPLMBiTxaQ9kYGzzhZRbK+xOo=

══════════ WebSocket连接建立 ══════════
         双方可以随时发送文本或二进制数据
```

握手只发生一次。建立后，这条TCP连接就变成了WebSocket专线，无需再带HTTP头。

## 14.3 WebSocket使用场景

### 实时聊天

```
用户A ──WebSocket──→ 服务器 ──WebSocket──→ 用户B
  "你好！"           （转发）           "你好！"
```

### 实时通知

```
系统事件 → 服务器 ──WebSocket──→ 浏览器
  "订单已发货"                 弹出提示
```

### 实时数据推送

```
服务器 ──WebSocket──→ 浏览器
  每0.5秒推送一次实时股价
```

### 在线协作

```
用户A编辑文档 ──WebSocket──→ 服务器 ──WebSocket──→ 用户B
    "第3行改为..."            （同步）         "第3行改为..."
```

## 14.4 WebSocket在Spring Boot中的实现

Spring Boot提供了对WebSocket的原生支持。

**1. 添加依赖（pom.xml）：**

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-websocket</artifactId>
</dependency>
```

**2. 配置WebSocket：**

```java
@Configuration
@EnableWebSocket
public class WebSocketConfig implements WebSocketConfigurer {

    @Override
    public void registerWebSocketHandlers(WebSocketHandlerRegistry registry) {
        registry.addHandler(new ChatHandler(), "/chat")
                .setAllowedOrigins("*");
    }
}
```

**3. 编写消息处理器：**

```java
public class ChatHandler extends TextWebSocketHandler {

    // 保存所有连接的会话
    private static final Set<WebSocketSession> sessions =
        Collections.synchronizedSet(new HashSet<>());

    @Override
    public void afterConnectionEstablished(WebSocketSession session) {
        sessions.add(session);
        System.out.println("新连接: " + session.getId());
    }

    @Override
    protected void handleTextMessage(WebSocketSession session,
                                     TextMessage message) throws Exception {
        String payload = message.getPayload();
        System.out.println("收到消息: " + payload);

        // 广播给所有连接的客户端
        for (WebSocketSession s : sessions) {
            if (s.isOpen()) {
                s.sendMessage(new TextMessage("用户" + session.getId() + ": " + payload));
            }
        }
    }

    @Override
    public void afterConnectionClosed(WebSocketSession session,
                                      CloseStatus status) {
        sessions.remove(session);
        System.out.println("连接关闭: " + session.getId());
    }
}
```

**4. 前端JavaScript连接：**

```javascript
// 在浏览器控制台中运行
const ws = new WebSocket("ws://localhost:8080/chat");

ws.onopen = () => console.log("WebSocket连接已建立");
ws.onmessage = (event) => console.log("收到消息:", event.data);
ws.onclose = () => console.log("WebSocket连接已关闭");

// 发送消息
ws.send("你好，Spring Boot！");
```

## 14.5 WebSocket vs HTTP轮询 vs SSE

三种实现"实时通信"的方式：

| | HTTP轮询 | HTTP长轮询 | SSE | WebSocket |
|---|---------|-----------|-----|-----------|
| 原理 | 定时发请求检查 | 请求挂起，有数据再返回 | 服务端单向推送 | 全双工双向 |
| 实时性 | 取决于轮询间隔 | 较好 | 好 | 最好 |
| 开销 | 大（大量无意义请求） | 中 | 小 | 最小 |
| 方向 | 客户端→服务端 | 客户端→服务端 | 服务端→客户端 | 双向 |
| 协议 | HTTP | HTTP | HTTP | WebSocket |

**选择指南：**
- 只需要服务端推送（如股票行情）→ SSE
- 需要双向实时通信（如聊天）→ WebSocket
- 不要求实时，几秒刷新一次就够了 → HTTP轮询

> 🤔 想多一点：WebSocket虽然强大，但不是银弹。它需要维护长连接，对服务器资源有额外开销。如果你的应用只需要"服务端偶尔推送通知"，用SSE（Server-Sent Events）更简单、更省资源。而且WebSocket穿透某些代理/Nginx时需要额外配置。**原则：够用就好，别杀鸡用牛刀。**

---

## 本章小结

| 学了什么 | 一句话说明 |
|----------|-----------|
| WebSocket | 基于TCP的全双工持久连接协议 |
| 与HTTP的区别 | HTTP请求-响应单向，WebSocket双向实时 |
| 握手 | 借HTTP Upgrade头切换到WebSocket协议 |
| Spring Boot实现 | spring-boot-starter-websocket依赖 + WebSocketHandler |
| 使用场景 | 聊天、实时通知、股票行情、在线协作 |

## 自测题

1. WebSocket和HTTP的核心区别是什么？为什么聊天应用不能用HTTP实现？

2. WebSocket连接建立时使用了HTTP的什么机制？连接建立后还需要HTTP吗？

3. 你需要在网页上实时显示服务器CPU使用率（每2秒更新一次）。应该用WebSocket还是HTTP轮询？为什么？