# 第09章 · TCP协议

> "你给朋友打电话——先拨号（对方接听）、确认'喂，听得到吗？'、然后才开始说正事，说完还要'好的，拜拜'才能挂断。TCP就是网络世界的'打电话'协议。"

## 09.1 TCP是什么

**TCP（Transmission Control Protocol，传输控制协议）** 是互联网最基础的传输协议。它解决一个核心问题：**如何在不稳定的网络上，可靠地传输数据。**

TCP的三大特征：

| 特征 | 说明 | 比喻 |
|------|------|------|
| **面向连接** | 通信前必须先建立连接 | 打电话前必须拨号接通 |
| **可靠传输** | 数据不丢、不重、不乱序 | 快递有单号、可追踪、按序送达 |
| **字节流** | 数据无边界，像水流一样 | 把数据当作连续的水流 |

> 📊 可视化演示见 [java_09_tcp_visual.html](java_09_tcp_visual.html)

## 09.2 三次握手：建立连接

TCP建立连接需要**三次握手**。这个过程就像：

```
客户端（你）                        服务端（你朋友）
    │                                    │
    │ ───① SYN: "在吗？我想跟你说话"────→   │
    │                                    │
    │ ←──② SYN-ACK: "在的，你说吧"───────  │
    │                                    │
    │ ───③ ACK: "好，那我开始说了"────→   │
    │                                    │
    │         ✅ 连接建立，开始传数据       │
```

为什么是三次，不是两次？因为网络可能丢包。如果只用两次握手，可能出现这种情况：客户端发了一个连接请求（SYN），但网络延迟导致这个请求在路上卡了很久。客户端以为丢包了，又发了一个新的SYN。然后旧的SYN终于到达服务端——如果只用两次握手，服务端就会以为"客户端要跟我说话了"，于是就傻等着，但客户端早已经用新连接说完了。

三次握手的第三次ACK就是为了防止这种"旧请求"造成的错误。

## 09.3 四次挥手：断开连接

断开连接需要**四次挥手**。为什么比建立连接多一次？因为TCP是全双工的——双方都可以同时发送数据。断开时需要两方分别说"我说完了"。

```
客户端                                服务端
    │                                    │
    │ ───① FIN: "我说完了"────────────→   │
    │                                    │
    │ ←──② ACK: "好的，知道了"────────   │
    │                                    │
    │ (服务端可能还有数据要发...)           │
    │                                    │
    │ ←──③ FIN: "我也说完了"────────────  │
    │                                    │
    │ ───④ ACK: "好的，拜拜"─────────→   │
    │                                    │
    │         ⛔ 连接关闭                  │
```

第②步和第③步之间可能有时间间隔——因为服务端收到客户端的FIN后，可能还有没发完的数据。所以服务端先回一个ACK（知道了），等发完剩余数据后再发自己的FIN。

> 🤔 想多一点：你在写Spring Boot应用时不需要手动处理TCP握手和挥手。Java的Socket API、Tomcat、Netty都帮你做了。但理解这些过程能帮你排查问题：比如为什么有些请求特别慢？可能是TCP连接建立本身花了时间。为什么大量连接处于TIME_WAIT状态？那是四次挥手后的正常状态，服务器需要等待以确保最后的ACK被对方收到。

## 09.4 Java Socket编程：一个"你好"程序

接下来写一个完整的TCP客户端-服务端程序。这是你第一次用Java直接操作网络。

### 服务端

```java
// TCPServer.java — 先运行这个
import java.io.*;
import java.net.*;

public class TCPServer {
    public static void main(String[] args) throws Exception {
        // 在8888端口上监听
        ServerSocket serverSocket = new ServerSocket(8888);
        System.out.println("服务端启动，等待连接... (端口: 8888)");

        while (true) {
            // accept() 会阻塞，直到有客户端连接进来
            Socket clientSocket = serverSocket.accept();
            System.out.println("客户端连接: " + clientSocket.getInetAddress());

            // 读取客户端发来的数据
            BufferedReader in = new BufferedReader(
                new InputStreamReader(clientSocket.getInputStream()));
            String message = in.readLine();
            System.out.println("收到: " + message);

            // 回复客户端
            PrintWriter out = new PrintWriter(clientSocket.getOutputStream(), true);
            out.println("你好！服务端收到你的消息: " + message);

            clientSocket.close();
        }
    }
}
```

### 客户端

```java
// TCPClient.java — 服务端运行后，再运行这个
import java.io.*;
import java.net.*;

public class TCPClient {
    public static void main(String[] args) throws Exception {
        // 连接到本机8888端口
        Socket socket = new Socket("127.0.0.1", 8888);
        System.out.println("已连接到服务端");

        // 发送消息
        PrintWriter out = new PrintWriter(socket.getOutputStream(), true);
        out.println("你好，服务端！我是客户端。");

        // 读取服务端回复
        BufferedReader in = new BufferedReader(
            new InputStreamReader(socket.getInputStream()));
        String response = in.readLine();
        System.out.println("服务端回复: " + response);

        socket.close();
    }
}
```

### 运行步骤

**终端1（服务端）：**

```bash
javac TCPServer.java
java TCPServer
# 输出: 服务端启动，等待连接... (端口: 8888)
```

**终端2（客户端）：**

```bash
javac TCPClient.java
java TCPClient
# 输出:
# 已连接到服务端
# 服务端回复: 你好！服务端收到你的消息: 你好，服务端！我是客户端。
```

**服务端终端此时显示：**

```
客户端连接: /127.0.0.1
收到: 你好，服务端！我是客户端。
```

## 09.5 TCP在Spring Boot中的体现

你在第64章学JDBC时配置的数据源连接，底层就是TCP：

```yaml
spring:
  datasource:
    url: jdbc:mysql://127.0.0.1:3306/mydb?useSSL=true
    #                 ↑       ↑
    #               TCP连接  端口
```

`jdbc:mysql://127.0.0.1:3306` 这串东西的本质是：
1. 通过TCP连接到 `127.0.0.1` 的 `3306` 端口
2. 在TCP连接之上，用MySQL协议进行数据库通信

你的Spring Boot应用和MySQL之间的每一次SQL查询，都跑在TCP连接之上。

---

## 本章小结

| 学了什么 | 一句话说明 |
|----------|-----------|
| TCP特征 | 面向连接、可靠传输、字节流 |
| 三次握手 | SYN → SYN-ACK → ACK，建立可靠连接 |
| 四次挥手 | FIN → ACK → FIN → ACK，断开双向连接 |
| Java Socket | ServerSocket监听，Socket连接，readLine/write通信 |
| Spring Boot中的TCP | 数据库连接、HTTP请求都跑在TCP之上 |

## 自测题

1. 为什么TCP建立连接需要三次握手，断开连接需要四次挥手？关键原因是什么？

2. 下面这段服务端代码有什么问题？（提示：它只能服务一个客户端）
   ```java
   ServerSocket server = new ServerSocket(8888);
   Socket client = server.accept();
   // 处理client...
   client.close();
   server.close();
   ```

3. 你在浏览器输入 `http://localhost:8080` 访问Spring Boot应用。这个通信使用的传输层协议是什么？为什么不用UDP？