# 第14章 · WebSocket

> "HTTP是一问一答——你必须先问，服务器才能答。但聊天消息怎么做到'对方一发你就收到'的？如果服务器有消息想主动告诉你怎么办？HTTP做不到，WebSocket做到了。"

---

## 14.1 HTTP的局限：只能一问一答

HTTP的核心模式是**请求-响应**：

```
客户端：发请求 → 服务器：回响应
客户端：不发请求 → 服务器：沉默（再急也不能主动说话）
```

这就像**写信**——你写一封信寄出去，对方回一封。对方不能在你没写信的情况下主动给你寄信。

### 那聊天软件怎么做的？

用户A给用户B发了一条微信消息，用户B的微信APP立刻弹出了通知——**服务器主动把消息推给了B**。HTTP怎么做？

### 方案一：轮询（Polling）——最笨的办法

客户端每隔几秒问一次服务器："有新消息吗？"

```
时间轴：
t=0s  客户端：有新消息吗？→ 服务器：没有
t=3s  客户端：有新消息吗？→ 服务器：没有
t=6s  客户端：有新消息吗？→ 服务器：没有
t=9s  客户端：有新消息吗？→ 服务器：有一条！
```

问题显而易见：

| 问题 | 后果 |
|------|------|
| **浪费资源** | 99%的请求得到的回答都是"没有"，白白消耗服务器资源和带宽 |
| **实时性差** | 消息可能延迟3秒（取决于轮询间隔） |
| **间隔难选** | 太短→浪费资源；太长→不实时 |

类比：你等一个快递，每分钟开门看一眼——极度低效。

### 方案二：长轮询（Long Polling）——聪明了一点

客户端发请求，服务器**不立刻回复**，而是把请求挂起。直到有新消息了，才回复。

```
客户端：有新消息吗？→ 服务器：...（挂起等待）...
                                ...新消息来了！
                                服务器：有一条消息！
客户端（立刻再发）：有新消息吗？→ 服务器：...（挂起等待）...
```

好处：减少了无效请求。
坏处：本质上还是HTTP的一问一答，服务器必须"等客户端先问"。而且每个连接占一个HTTP连接，服务器需要维护大量挂起的连接。

---

## 14.2 WebSocket：从写信变成打电话

### 核心比喻

| 协议 | 比喻 | 特点 |
|------|------|------|
| HTTP | **写信** | 必须先寄出一封信（请求），才能收到回信（响应）。一方不寄信，另一方就不能回。 |
| WebSocket | **打电话** | 拨通后，双方随时可以说话。你想说就说，对方想说就说——**全双工实时通信**（双向实时通信协议，详见附录I）。 |

### WebSocket连接示意图

```
传统HTTP：
客户端 ──①请求──→ 服务器
客户端 ←──②响应── 服务器
客户端 ──③请求──→ 服务器
客户端 ←──④响应── 服务器
...必须一问一答...

WebSocket：
客户端 ──①握手(HTTP Upgrade)──→ 服务器
客户端   ②连接建立              服务器
客户端 ──③"你好"─────────────→ 服务器
客户端 ←──④"你也好！"──────── 服务器
客户端 ←──⑤"有你的新消息！"─── 服务器  （服务器主动发！）
客户端 ──⑥"收到！"───────────→ 服务器
...双方随时可以发，不再一问一答...
```

---

## 14.3 WebSocket握手：从HTTP升级而来

WebSocket的建立基于HTTP协议。一句话概括：**通过HTTP请求完成"协议升级"，之后切换到WebSocket协议。**

### 握手过程

#### 第1步：客户端发出HTTP升级请求

```http
GET /chat HTTP/1.1
Host: server.example.com
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==
Sec-WebSocket-Version: 13
```

关键头解释：
- `Upgrade: websocket` — "我想升级到WebSocket"
- `Connection: Upgrade` — "这次连接要升级"
- `Sec-WebSocket-Key` — 一个随机编码的字符串，服务端必须用它做验证
- `Sec-WebSocket-Version` — 协议版本，目前是13

#### 第2步：服务端响应"同意升级"

```http
HTTP/1.1 101 Switching Protocols
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Accept: s3pPLMBiTxaQ9kYGzzhZRbK+xOo=
```

状态码 `101 Switching Protocols` 的意思是："好的，我们换WebSocket协议了。"

`Sec-WebSocket-Accept` 是用客户端的 `Sec-WebSocket-Key` 加上一个固定的GUID，经过SHA-1哈希再做Base64编码得到的。客户端会验证这个值，确认服务端真的支持WebSocket。

**从此以后，这条TCP连接上的通信不再走HTTP，而是走WebSocket协议。**

> 🤔 想多一点：WebSocket为什么选择"基于HTTP握手"的设计？因为互联网上到处都是HTTP代理、防火墙、负载均衡器——它们都认识HTTP，会把非HTTP的流量拦截掉。如果WebSocket完全自创一套协议走新的端口，在大多数企业网络里根本通不了。伪装成HTTP握手可以利用现成的HTTP基础设施，而且WebSocket用80/443端口（ws://ws用80，wss://ws用443），完美绕过防火墙限制。这是一个精妙的设计——**用HTTP的船票上了船，然后在船上换了一种交流方式。**

### 用Go实现WebSocket服务端

Go标准库没有内置WebSocket支持，通常使用 `gorilla/websocket` 库（你也可以用 `nhooyr.io/websocket` 或 `gobwas/ws`，但gorilla是最经典的）。

```go
package main

import (
    "fmt"
    "net/http"

    "github.com/gorilla/websocket"
)

var upgrader = websocket.Upgrader{
    CheckOrigin: func(r *http.Request) bool {
        return true
    },
}

func handleWebSocket(w http.ResponseWriter, r *http.Request) {
    conn, err := upgrader.Upgrade(w, r, nil)
    if err != nil {
        fmt.Println("升级WebSocket失败:", err)
        return
    }
    defer conn.Close()

    fmt.Println("新客户端已连接！")

    conn.WriteMessage(websocket.TextMessage, []byte("欢迎连接到WebSocket服务器！"))

    for {
        messageType, message, err := conn.ReadMessage()
        if err != nil {
            fmt.Println("读取消息失败，客户端可能已断开:", err)
            break
        }
        fmt.Printf("收到消息: %s\n", string(message))

        reply := []byte("服务器收到: " + string(message))
        if err := conn.WriteMessage(messageType, reply); err != nil {
            fmt.Println("发送消息失败:", err)
            break
        }
    }
}

func main() {
    http.HandleFunc("/ws", handleWebSocket)
    fmt.Println("WebSocket服务器启动在 :8080")
    http.ListenAndServe(":8080", nil)
}
```

核心步骤：
1. `Upgrader` — 负责把HTTP连接升级为WebSocket连接
2. `conn.ReadMessage()` — 阻塞式读取消息（WebSocket是全双工的，读写可以同时进行）
3. `conn.WriteMessage()` — 发送消息

### 客户端代码（浏览器端）

```javascript
const ws = new WebSocket("ws://localhost:8080/ws");

ws.onopen = function() {
    console.log("已连接到服务器");
    ws.send("你好服务器！");
};

ws.onmessage = function(event) {
    console.log("服务器说:", event.data);
};

ws.onclose = function() {
    console.log("连接已断开");
};

ws.onerror = function(err) {
    console.error("WebSocket错误:", err);
};
```

### WebSocket的帧格式

WebSocket有自己的帧格式（Frame），和HTTP请求/响应完全不同：

```
┌──────────────────────────────────────────┐
│ FIN│RSV│ OPCODE │ MASK │ Payload Len │  ← 头部（2~14字节）
├──────────────────────────────────────────┤
│           Payload Data                    │  ← 数据部分
└──────────────────────────────────────────┘
```

- **OPCODE**：0x1=文本帧，0x2=二进制帧，0x8=关闭帧，0x9=Ping帧，0xA=Pong帧
- **MASK**：客户端发往服务器的帧**必须**掩码（防止缓存投毒攻击），服务器发往客户端的帧不掩码
- **Ping/Pong**：心跳机制。服务器发Ping帧，客户端必须回Pong帧，用于检测连接是否还活着

> 🤔 想多一点：掩码的目的。如果WebSocket客户端不掩码数据，攻击者可以通过构造特殊的WebSocket数据，欺骗中间代理服务器把它当成HTTP请求来处理——这就是"缓存投毒"攻击。掩码后数据就变成无意义的随机数据，代理不会误解。RFC 6455强制要求客户端到服务端的帧必须掩码。

---

## 14.4 WebSocket的使用场景

### 14.4.1 即时通讯（聊天）

这是最经典的场景。用户之间的消息需要**毫秒级传递**。

```
用户A → [发送消息] → WebSocket → 服务器 → WebSocket → 用户B
```

注意：**WebSocket解决的是服务器到客户端的实时推送，不是用户之间的直接通信**。用户A和用户B之间必然经过服务器中转，服务器负责把消息路由到正确的接收者。

### 14.4.2 实时推送/通知

- 股票价格变动
- 体育比分更新
- 新闻快讯
- 系统告警

这些场景的共同特征：**数据源在变，客户端需要即时知道。**

### 14.4.3 在线协作

- 在线文档多人编辑（Google Docs）
- 在线白板（Miro、Excalidraw）
- 在线代码编辑器（VS Code Online、Replit）

多个用户同时编辑同一个文档，每个人的修改（增删字符、移动光标）都需要实时同步给所有人。几十到几百条消息每秒——这才能实现"流畅的协作体验"。

### 14.4.4 在线游戏

- 多人在线游戏的实时位置同步
- 棋牌类游戏的出牌广播
- 游戏中的聊天频道

游戏通常用**UDP**做位置同步（延迟敏感），但用**WebSocket**做聊天、大厅匹配、房间管理等（可靠性要求高）。

### 14.4.5 物联网（IoT）

- 设备状态实时监控
- 远程控制指令下发
- 传感器数据流推送

一个温度传感器不需要每秒发一次HTTP请求——它建立一次WebSocket连接，然后持续推送数据直到断开。

### 14.4.6 直播弹幕

看直播时屏幕上滚过的弹幕——弹幕就是典型的WebSocket场景：服务器主动把每个用户的弹幕**广播**给正在观看的所有人，一秒钟成百上千条，HTTP轮询根本扛不住。

---

## 14.5 WebSocket vs HTTP vs SSE

| 特性 | HTTP | WebSocket | SSE（Server-Sent Events） |
|------|------|-----------|--------------------------|
| **通信方向** | 单向（客户端→服务端，然后服务端→客户端） | 全双工（双向任意发） | 单向（服务端→客户端） |
| **协议** | HTTP | WebSocket（ws:// / wss://） | HTTP |
| **自动重连** | 无 | 需要手动实现 | 浏览器内置自动重连 |
| **二进制数据** | 支持 | 支持 | 只支持文本 |
| **实现难度** | 简单 | 中等 | 简单 |
| **适用场景** | REST API | 聊天、游戏、协作 | 纯推送（股票、新闻） |

Server-Sent Events（SSE）是另一个服务端推送方案。它基于HTTP，但只支持服务端→客户端单向推送。如果只需要服务器推数据（如股票行情），SSE比WebSocket简单。但如果你需要双向通信，WebSocket是不二之选。

---

## 14.6 生产环境的WebSocket注意事项

1. **心跳保活**：WebSocket连接可能因为网络波动或中间代理超时而被断开。需要定期发送Ping帧或应用层心跳包，检测连接是否存活。

2. **断线重连**：客户端需要实现自动重连逻辑（指数退避：1秒→2秒→4秒→8秒...）。

3. **连接数限制**：每个WebSocket连接就是一个常驻的TCP连接。一台服务器能维护的WebSocket连接数受限于文件描述符和内存。单机通常几万到几十万条。水平扩展需要分布式方案（如用Redis做消息中转）。

4. **负载均衡**：传统的HTTP负载均衡（如Nginx）对WebSocket需要特殊配置——因为连接是长久的，不能随便切换后端。

```nginx
location /ws {
    proxy_pass http://backend;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
}
```

5. **安全性**：生产环境用 `wss://`（WebSocket over TLS），相当于HTTPS之于HTTP。

> 🤔 想多一点：你可能听说过Socket.IO。它不是一个协议，而是WebSocket的一个**封装库**。如果WebSocket连接建立失败（比如客户端浏览器太老，或者企业防火墙拦WebSocket），Socket.IO会自动降级到HTTP长轮询——对用户来说完全透明。Socket.IO还内置了自动重连、房间/命名空间、广播等功能。如果你在做聊天应用，Socket.IO可以节省大量重复造轮子的时间。

---

## 本章小结

| 知识点 | 一句话概括 |
|--------|------------|
| HTTP的局限 | 只能一问一答，服务器不能主动推送 |
| 轮询 vs 长轮询 | 轮询=每隔N秒问一次（浪费），长轮询=挂起等待（略好但仍是一问一答） |
| WebSocket是什么 | 全双工通信协议，双方随时可以互发消息 |
| WebSocket比喻 | HTTP=写信，WebSocket=打电话 |
| WebSocket握手 | 通过HTTP Upgrade头完成协议升级（状态码101） |
| WebSocket帧 | 有自己的帧格式，带Ping/Pong心跳机制 |
| 使用场景 | 聊天、推送、协作、游戏、IoT、弹幕 |
| 生产注意事项 | 心跳保活、断线重连、负载均衡配置、wss加密 |

> 🚀 下一章：从IP到端口，从TCP到HTTP，从Cookie到HTTPS再到WebSocket——网络层的知识你已全部打通。地基打好了，接下来要学一门真正的编程语言。Go语言，简洁、高效、并发能力强——后端工程师的首选武器，从下一章开始。

---
[← 上一章：13-HTTPS](13-HTTPS/) | [下一章：15-Go语言介绍与环境搭建 →](15-Go语言介绍与环境搭建/)