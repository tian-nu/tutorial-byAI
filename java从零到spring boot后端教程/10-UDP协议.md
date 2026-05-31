# 第10章 · UDP协议

> "TCP像打电话——先接通、确认能听清、然后一句一句说。UDP像对讲机——按了就说，对方听没听到、听没听清，你不管。"

## 10.1 UDP是什么

**UDP（User Datagram Protocol，用户数据报协议）** 是另一种传输层协议。和TCP相反：

| | TCP | UDP |
|---|-----|-----|
| 连接 | 需要建立连接（三次握手） | 无连接，直接发 |
| 可靠性 | 保证送达、有序、不重复 | 不保证送达，可能丢包、乱序 |
| 速度 | 相对慢（开销大） | 快（开销小） |
| 数据边界 | 字节流（无边界） | 数据报（有边界，一次一个完整包） |
| 适用场景 | 网页、文件传输、邮件 | 视频直播、语音通话、DNS查询、游戏 |

## 10.2 UDP的"不靠谱"反而是优势？

UDP不保证送达，听起来很差。但"不保证送达"意味着它不需要维护连接状态、不需要重传机制——**省了大量开销**。

直播场景：视频每秒30帧。如果丢了一帧，画面卡一下，但马上就过去了。如果用TCP保证每一帧都送到，那丢了一帧就得停下来等重传，直播就变成了"先缓冲3秒"的体验。

同样的道理，在线游戏、VoIP电话、DNS查询（第07章学的），都用UDP。

## 10.3 Java DatagramSocket 演示

```java
// UDPServer.java — 先运行这个
import java.net.*;

public class UDPServer {
    public static void main(String[] args) throws Exception {
        // 在9999端口上监听UDP数据报
        DatagramSocket socket = new DatagramSocket(9999);
        System.out.println("UDP服务端启动，等待数据... (端口: 9999)");

        byte[] buffer = new byte[1024];

        while (true) {
            // 准备接收数据报
            DatagramPacket packet = new DatagramPacket(buffer, buffer.length);
            socket.receive(packet);  // 阻塞，直到收到数据

            String message = new String(packet.getData(), 0, packet.getLength());
            System.out.println("收到来自 " + packet.getAddress() + ":" +
                packet.getPort() + " 的消息: " + message);

            // 回复客户端（可选——UDP也可以不回复）
            String reply = "收到: " + message;
            byte[] replyData = reply.getBytes();
            DatagramPacket replyPacket = new DatagramPacket(
                replyData, replyData.length,
                packet.getAddress(), packet.getPort());
            socket.send(replyPacket);
        }
    }
}
```

```java
// UDPClient.java — 服务端运行后，再运行这个
import java.net.*;

public class UDPClient {
    public static void main(String[] args) throws Exception {
        DatagramSocket socket = new DatagramSocket();  // 系统随机分配端口

        // 准备发送的数据
        String message = "你好，UDP服务端！";
        byte[] data = message.getBytes();

        // 发送数据报到本机9999端口
        InetAddress address = InetAddress.getByName("127.0.0.1");
        DatagramPacket packet = new DatagramPacket(data, data.length, address, 9999);
        socket.send(packet);
        System.out.println("已发送: " + message);

        // 等待服务端回复（如果服务端会回复的话）
        byte[] buffer = new byte[1024];
        DatagramPacket replyPacket = new DatagramPacket(buffer, buffer.length);
        socket.receive(replyPacket);

        String reply = new String(replyPacket.getData(), 0, replyPacket.getLength());
        System.out.println("服务端回复: " + reply);

        socket.close();
    }
}
```

### 运行

```bash
# 终端1
javac UDPServer.java && java UDPServer

# 终端2
javac UDPClient.java && java UDPClient
```

> 🤔 想多一点：UDP客户端 `new DatagramSocket()` 没有指定端口，操作系统会给它随机分配一个（比如54321）。服务端 `receive()` 拿到 `DatagramPacket` 后，可以通过 `packet.getPort()` 知道是从客户端的哪个端口发来的——这样回复时就能正确投递。这个设计和TCP完全不同：TCP是"先建立专属通道再通信"，UDP是"每个包自己带着寄件人和收件人地址旅行"。

## 10.4 TCP vs UDP 选择指南

```
需要可靠送达？ ────Yes────→ 用 TCP
     │
    No
     │
     ↓
能容忍丢包？ ────Yes────→ 用 UDP（直播、游戏、DNS）
     │
    No
     │
     ↓
那就还是用 TCP
```

一个简单的口诀：

> **需要"每一句话都让对方听清楚"→ TCP。需要"越快越好，漏一两句没关系"→ UDP。**

## 10.5 UDP在Java后端中的实际应用

虽然UDP看起来"不靠谱"，但在后端架构中有不少应用：

- **DNS查询**：第07章学的 `InetAddress.getByName()`，底层发的就是UDP包到DNS服务器的53端口
- **日志收集**：高性能日志系统（如Logstash）有时用UDP接收日志——丢几条日志无所谓，但日志吞吐量必须高
- **服务发现**：微服务架构中，健康检查有时用UDP广播"我还活着"
- **QUIC协议**：HTTP/3底层用的是基于UDP的QUIC协议，结合了UDP的低延迟和TCP的可靠性

---

## 本章小结

| 学了什么 | 一句话说明 |
|----------|-----------|
| UDP特征 | 无连接、不可靠、快速、数据报边界 |
| UDP vs TCP | TCP可靠慢，UDP快不可靠，各有用武之地 |
| Java UDP编程 | DatagramSocket发送接收DatagramPacket |
| UDP应用场景 | DNS、直播、游戏、语音通话、日志采集 |

## 自测题

1. 你正在开发一个实时多人在线游戏。玩家位置数据每秒更新30次。应该用TCP还是UDP传输位置数据？为什么？

2. 下面代码有什么问题？
   ```java
   DatagramSocket socket = new DatagramSocket();
   byte[] data = "hello".getBytes();
   // 漏了什么？
   socket.send(new DatagramPacket(data, data.length));
   ```

3. DNS查询为什么用UDP而不是TCP？如果用TCP会有什么问题？