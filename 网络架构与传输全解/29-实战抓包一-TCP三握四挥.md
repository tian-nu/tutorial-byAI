# 29 — 实战抓包（一）：TCP 三握四挥亲眼看看

## 学习目标

- 用 Wireshark 抓到一次完整的 TCP 连接
- 逐包辨认三次握手和四次挥手的关键字段
- 理解为什么有时候四挥只看到 3 个包
- 掌握 `tcp.flags.syn==1` 过滤器的使用场景

---

第 15-17 章讲过 TCP 的三次握手和四次挥手，当时你可能看了很多图，背了很久。这一章，我们用 Wireshark 亲自抓一次，让那些 SEQ、ACK、SYN、FIN 从抽象概念变成你亲眼看见的东西。

---

## 29.1 准备实验

本实验用 httpbin.org 作为目标。为什么不用 example.com？

💡 **想多一点：为什么用 httpbin.org 而不是 example.com？**

example.com 现在会自动把 HTTP 请求 301 重定向到 HTTPS。如果你用 `curl http://example.com`，实际抓到的可能是一个重定向 + 一个 TLS 握手的 HTTPS 连接。TLS 加密后 TCP 依然是明文（TCP 头不加密），但 HTTP 内容就看不到了。而 httpbin.org 支持纯 HTTP 明文访问，实验更干净。

### 实验命令

打开两个窗口：

**窗口 1**：Wireshark

- 选对网卡（参考 28.3 节），在捕获过滤器里输入：`host httpbin.org`
- 点击开始抓包

**窗口 2**：终端

```powershell
# Windows PowerShell
curl.exe --http1.1 -v http://httpbin.org/get
```

```bash
# macOS / Linux
curl --http1.1 -v http://httpbin.org/get
```

命令解释：

- `--http1.1`：强制使用 HTTP/1.1（不用 HTTP/2，因为 HTTP/2 的 TCP 行为略有不同，不利于观察经典的四挥）
- `-v`：显示详细信息，包括 TCP 握手过程
- `http://httpbin.org/get`：HTTP 明文，端口 80

### 执行顺序

1. 先在 Wireshark 点"开始抓包"
2. 在终端执行 curl 命令
3. 看到终端输出完毕后，在 Wireshark 点"停止"

---

## 29.2 三次握手——逐包解剖

停止抓包后，在 Wireshark 过滤器中输入 `tcp`，你应该看到大约 10 个包左右。前 3 个就是三次握手。

### 包 1：SYN —— 客户端说"我想连接"

在包列表中找第一个包，它应该长这样：

```
[SYN]  Seq=0  Win=65535  Len=0  MSS=1460
```

点开这个包，展开 Internet Protocol Version 4 → Transmission Control Protocol：

```
Source Port: 5XXXX（你的随机端口）
Destination Port: 80
Sequence Number: 0（相对序号）
Acknowledgment Number: 0
Flags: 0x002 (SYN)
    .... .... ..1. = Syn: Set
Window: 65535
```

关键点：

- **SYN 标志位**：值为 1，表示这是连接请求
- **Seq=0**：Wireshark 默认显示**相对序号**（真实序号是一个随机大数，但 Wireshark 帮你归零了，方便阅读）
- **Ack=0**：第一次握手还没有确认号
- **没有数据**（Len=0）：SYN 包不携带应用数据

翻译成人话：客户端对服务器说："你好，我的起始序号是 X，我想建立连接。"

### 包 2：SYN+ACK —— 服务器说"好，我也来"

```
[SYN, ACK]  Seq=0  Ack=1  Win=65535  Len=0  MSS=1460
```

展开 TCP 头：

```
Source Port: 80
Destination Port: 5XXXX
Sequence Number: 0（相对序号）
Acknowledgment Number: 1
Flags: 0x012 (SYN, ACK)
    .... .... ..1. = Syn: Set
    .... .... .1.. = Acknowledgment: Set
```

关键点：

- **SYN 和 ACK 同时置 1**：这是第二次握手的标志
- **Ack=1**：确认收到了客户端的 Seq=0（Ack = 对方 Seq + 1 = 0 + 1）
- **Seq=0**：服务器给出了自己的初始序号

翻译成人话：服务器说："收到，我的序号是 Y，我确认你的序号 X。"

### 包 3：ACK —— 客户端说"确认"

```
[ACK]  Seq=1  Ack=1  Win=65535  Len=0
```

展开 TCP 头：

```
Sequence Number: 1
Acknowledgment Number: 1
Flags: 0x010 (ACK)
    .... .... .1.. = Acknowledgment: Set
```

关键点：

- **只有 ACK，没有 SYN**：第三次握手
- **Seq=1**：客户端发送确认（虽然这个包也没数据，但序号推进了）
- **Ack=1**：确认收到了服务器的 SYN（Ack = 对方 Seq + 1 = 0 + 1）

翻译成人话：客户端说："收到你的确认，连接建立完毕！"

### 三次握手汇总

| 包序号 | 方向 | 标志位 | Seq | Ack | 含义 |
|--------|------|--------|-----|-----|------|
| 1 | 客户端→服务器 | SYN | 0 | 0 | 我要连接 |
| 2 | 服务器→客户端 | SYN+ACK | 0 | 1 | 好，我也来 |
| 3 | 客户端→服务器 | ACK | 1 | 1 | 确认 |

这就是你第 15-17 章看过的三次握手，现在亲眼看到了。

---

## 29.3 数据传输——PSH+ACK 与 HTTP 请求

三握之后，Wireshark 中接下来的几个包是实际的数据传输：

```
包4: [PSH, ACK]  Seq=1  Ack=1  Len=82  → 客户端发送 HTTP GET 请求
包5: [ACK]       Seq=1  Ack=83 Len=0   → 服务器确认收到请求
包6: [PSH, ACK]  Seq=1  Ack=83 Len=XXX → 服务器发送 HTTP 响应
```

**PSH（Push）标志**：告诉接收方"数据到了别缓存，立刻交给应用程序"。HTTP 请求和响应通常都带 PSH 标志。

包 4 中如果你展开应用层数据，能看到：

```
GET /get HTTP/1.1
Host: httpbin.org
User-Agent: curl/8.x.x
Accept: */*
```

这就是你执行的 curl 命令发出的 HTTP 请求明文！

💡 **想多一点：为什么需要 PSH 标志？**

TCP 为了提高效率，有时会等攒够一定数据量再发送（Nagle 算法），或者接收方攒够一定量再提交给应用。但对于 HTTP 这种"请求-响应"模型，客户端发完请求就等着，服务器也需要立刻处理。PSH 就是告诉对方："这个包里的内容别等了，立刻处理。"这就像你快递上贴了个"生鲜急送"的标签。

---

## 29.4 四次挥手——逐包解剖

数据传输完毕后，连接需要关闭。在 Wireshark 中找到最后几个包。

### 包 7：FIN+ACK —— 服务器先主动关闭

httpbin.org 作为 HTTP 服务器，收到请求、回复响应后，会主动关闭连接：

```
[FIN, ACK]  Seq=YYY  Ack=83  Len=0
Flags: 0x011 (FIN, ACK)
```

关键点：

- **FIN 置 1**：表示"我没有数据要发了，我要关闭"
- **ACK 也置 1**：同时确认之前收到的数据

翻译：服务器说："我说完了，我要挂电话了。"

### 包 8：ACK —— 客户端确认服务器的 FIN

```
[ACK]  Seq=83  Ack=YYY+1  Len=0
```

翻译：客户端说："好的，我知道你要挂了。"

此时**半关闭状态**：服务器→客户端方向已关闭，客户端→服务器方向还没有。但在这个场景中，客户端也没数据要发了，所以紧接着：

### 包 9：FIN+ACK —— 客户端也发 FIN

```
[FIN, ACK]  Seq=83  Ack=YYY+1  Len=0
```

翻译：客户端说："我也说完了，我也要挂。"

### 包 10：ACK —— 服务器确认客户端的 FIN

```
[ACK]  Seq=YYY+1  Ack=84  Len=0
```

翻译：服务器说："好的，拜拜。"

### 四次挥手汇总

| 包序号 | 方向 | 标志位 | 含义 |
|--------|------|--------|------|
| 7 | 服务器→客户端 | FIN+ACK | 我要关了 |
| 8 | 客户端→服务器 | ACK | 知道了 |
| 9 | 客户端→服务器 | FIN+ACK | 我也关了 |
| 10 | 服务器→客户端 | ACK | 拜拜 |

---

## 29.5 为什么四挥有时只看到 3 个包？

这是本实验最可能让你困惑的地方——你可能只看到 3 个挥手包（FIN → ACK+FIN → ACK），而不是 4 个。

原因很简单：

**如果被动关闭方（收到第一个 FIN 的那方）也没有数据要发了，它可以把自己的 FIN 和 ACK 合并到同一个包里。**

具体到本实验：

- 服务器发 FIN+ACK（包 7）
- 客户端本来应该先发 ACK 再发 FIN，但客户端此时也没有数据要发，所以 ACK 和 FIN 可以合并为同一个包：FIN+ACK

于是变成：

```
服务器 → FIN+ACK → 客户端
客户端 → FIN+ACK → 服务器  （ACK 和 FIN 合并）
服务器 → ACK → 客户端
```

3 个包。这是**完全正常**的，不是漏抓了。

❌ **常见困惑**："教科书说四挥，我只看到 3 个包，是不是我抓漏了？"

✅ **真相**：四次挥手是最坏情况（双方都有数据要发完后才关），很多场景下被动方的 ACK 和 FIN 会合并，只看到 3 个包。这在 RFC 793 中有明确定义，不属于异常。

---

## 29.6 找不到 SYN 包怎么办？

如果你抓包范围太大（比如没设捕获过滤器，直接全量抓了 30 秒），SYN 包可能被淹没在几千个包中。

**用了 Wireshark 的 tcp.flags 过滤器**：

```
tcp.flags.syn == 1
```

这会只显示所有 SYN 包（只 SYN，不含 SYN+ACK）：

```
tcp.flags.syn == 1 and tcp.flags.ack == 0
```

第二个写法只匹配纯 SYN 包，排除 SYN+ACK，帮你精确定位每个三次握手的起点。

---

## 29.7 验证题：你能独立找到它们吗？

停止抓包，清空所有过滤器，在数千个包中独立完成以下任务：

1. 过滤出本次实验的所有 TCP 包：`tcp`
2. 找到第一个 SYN 包：`tcp.flags.syn == 1 and tcp.flags.ack == 0`
3. 确认三次握手：SYN → SYN+ACK → ACK
4. 找到 HTTP 请求包：展开应用层看 GET 请求明文
5. 确认四次挥手：找到 FIN 包
6. 判断：你看到了 3 个还是 4 个挥手包？解释原因。

---

## 本章小结

| 你学了什么 | 具体内容 |
|-----------|---------|
| 抓取 TCP 连接 | `host httpbin.org` 捕获过滤器 + `curl --http1.1 -v` |
| 三握逐包分析 | SYN(Seq=0) → SYN+ACK(Seq=0,Ack=1) → ACK(Seq=1,Ack=1) |
| PSH 标志 | 催促接收方立刻处理数据，HTTP 请求/响应常见 |
| 四挥逐包分析 | FIN+ACK → ACK → FIN+ACK → ACK |
| 3 包挥手原因 | 被动方的 ACK 和 FIN 可合并到同一个包 |
| tcp.flags 过滤器 | `tcp.flags.syn==1` 找 SYN 包 |

## 术语表（无新术语）

本章无新增术语，所有概念（SYN、ACK、FIN、三次握手、四次挥手）已在第 15-17 章讲解。本章是对那些概念的**实操验证**，不做重复定义。

若有遗忘，请回第 15-17 章查阅对应术语。

## 验证方法

不看本章，独立完成以下操作即通过：

1. Wireshark 过滤 `host httpbin.org`，开始抓包
2. 终端执行 `curl --http1.1 -v http://httpbin.org/get`
3. 在 Wireshark 中找到并辨认：三次握手（SYN、SYN+ACK、ACK）和四次挥手（FIN 包）
4. 判断本实验看到了 3 个还是 4 个挥手包，并解释原因

---

> ⏸️ **推荐暂停点**：本章结束可暂停。恢复时确认：能在 Wireshark 中用 `tcp.flags.syn==1` 找到三次握手的起点。