# 17 — TCP（下）四次挥手：优雅地说再见

## 学习目标
- 能默画四次挥手时序图，标注每一步的状态转换
- 理解为什么是四次而不是三次
- 能解释 TIME_WAIT 存在的两个原因（面试高频）
- 知道 MSL 的定义与 Linux 典型值（30 秒，2MSL=60 秒），理解 2MSL 等待
- 知道 CLOSE_WAIT 过多如何排查

---

## 17.1 为什么挥手比握手多一次？

回想三次握手：服务器把 SYN 和 ACK 合并在一个报文里发出去（②），省了一次。那挥手为什么不能合并 FIN 和 ACK 呢？

答案关键在**全双工**。TCP 连接是双向的——你既能发数据，也能收数据，两条通路相互独立。

- 建立连接时：**双方同时开始同步**，所以 SYN 和 ACK 可以合并。
- 关闭连接时：**双方不太可能同时想关闭**。A 说"我说完了"不等于 B 也说完了。B 可能还有数据要发给 A。

所以挥手必须分两步走：

```
A → B: "我不发了"（FIN）
B → A: "好的，我知道你不发了"（ACK）  ← 但 B 可能还要发数据给 A
B → A: "我也不发了"（FIN）           ← B 发完最后的数据后才说
A → B: "好的，我知道了"（ACK）
```

这四步就是四次挥手。如果 B 在收到 A 的 FIN 时也已经没数据要发了，那么 B 的 ACK 和 FIN 可以合并（变成三次）。但在典型场景中，A 是客户端（主动关闭），B 是服务器（被动关闭），服务器在收到 FIN 后通常还有未发完的响应数据。

---

## 17.2 四次挥手，逐帧详解

```
   主动关闭方 (A)                        被动关闭方 (B)
   (通常是客户端)                        (通常是服务器)
         |                                     |
ESTABLISHED                              ESTABLISHED
         |                                     |
         |----------① FIN, seq=u ------------>|
         |                                     |
  FIN_WAIT_1                             CLOSE_WAIT
         |                                     |
         |<---------② ACK, ack=u+1 ----------|
         |                                     |
  FIN_WAIT_2                             CLOSE_WAIT
         |          (B 可能继续发数据)           |
         |<---------③ FIN, seq=v ------------|
         |                                     |
  TIME_WAIT                               LAST_ACK
         |                                     |
         |----------④ ACK, ack=v+1 ---------->|
         |                                     |
  TIME_WAIT                               CLOSED
  (等待 2MSL)
         |
      CLOSED
```

### 第一次挥手：A → B

A 的应用层调用 `close()`（或发送完数据自动关闭），TCP 发送一个 **FIN 报文**：

```
FIN = 1
seq = u（A 已发送数据的最后字节序号）
```

发送后，**A 进入 `FIN_WAIT_1` 状态**。A 不再发送新数据，但仍能接收数据。

### 第二次挥手：B → A

B 收到 FIN 后，回复一个 **ACK 报文**，确认收到了 A 的 FIN：

```
ACK = 1
ack = u + 1（确认 A 的 FIN）
```

发送后，**B 进入 `CLOSE_WAIT` 状态**。此时 B 的 TCP 层通知应用层："对方想关了，你还有数据要发吗？"如果 B 的应用层还有数据要发，就继续发——A 虽然不发了，但还能接收。

A 收到这个 ACK 后，**进入 `FIN_WAIT_2` 状态**，等待 B 的 FIN。

### 第三次挥手：B → A

B 的应用层发完所有数据后，调用 `close()`，TCP 发送 **FIN 报文**：

```
FIN = 1
ACK = 1
seq = v（B 已发送数据的最后字节序号）
ack = u + 1（仍然确认 A 的 FIN，这个值在第二次和第三次中相同）
```

发送后，**B 进入 `LAST_ACK` 状态**，等待 A 的最后确认。

### 第四次挥手：A → B

A 收到 B 的 FIN 后，发送最后一个 **ACK 报文**：

```
ACK = 1
ack = v + 1（确认 B 的 FIN）
```

发送后，**A 进入 `TIME_WAIT` 状态**，等待 2MSL 时间后才进入 CLOSED。

B 收到这个 ACK 后，**立即进入 CLOSED 状态**，连接彻底关闭。

> 💡 **想多一点**：TCP 关闭没有"双方同时 CLOSED"的时刻。B 先 CLOSED，但 A 还在 TIME_WAIT。如果在 TIME_WAIT 期间 A 收到来自同一个四元组的新 SYN，A 会怎么处理？RFC 规定：如果新 SYN 的序列号在 TIME_WAIT 连接的序列号范围内，A 会忽略它，防止旧数据混入新连接。

---

## 17.3 TIME_WAIT 为什么等 2MSL？（面试高频）

这是面试官最爱问的问题之一。先定义 MSL：

> **MSL（Maximum Segment Lifetime）**：一个 TCP 报文在网络中能存活的最长时间。RFC 793 建议 MSL = 120 秒（故 2MSL = 240 秒）。Linux 内核将 MSL 实现为 30 秒（定义在 `include/net/tcp.h` 的 `TCP_TIMEWAIT_LEN = 60 秒 = 2MSL`），所以 Linux 上 TIME_WAIT 默认持续 60 秒。
>
> ⚠️ **易混淆点**：`net.ipv4.tcp_fin_timeout` 控制的是 **FIN_WAIT_2** 状态的超时（默认 60 秒），**不是** TIME_WAIT 时长。TIME_WAIT 时长由内核宏 `TCP_TIMEWAIT_LEN` 固定为 60 秒，**不可通过 sysctl 调整**。下文用"60 秒"指代 Linux 上的 2MSL。

主动关闭方进入 TIME_WAIT 并等 2MSL（Linux 上 60 秒），有两个原因：

### 原因一：确保最后的 ACK 能到达对方

第四次挥手的 ACK 可能丢失。如果 A 不等就关了，B 没收到 ACK 会重发 FIN，但 A 已经 CLOSED 了——要么回复 RST（被 B 当成错误），要么什么都不回（B 一直 LAST_ACK）。等 2MSL 让 A 有机会接收并回应 B 的重传 FIN。

```
场景：第四次 ACK 丢了

A                        B
|--- ④ ACK ----X 丢了!    B 没收到 ACK
|                          B 超时重发 FIN
|<-- ③ FIN (重传) -----|
|--- ④ ACK (重发) ---->|  B 收到，进入 CLOSED
|                          ← 因为 A 还在 TIME_WAIT，能回应这次重传
```

### 原因二：让旧连接的所有残包在网络中过期

如果 A 和 B 立刻关闭又立刻新建一个连接（相同的 IP+端口四元组），上次连接中还在网络上飘的旧报文可能被误认为新连接的数据。等 2MSL（两个方向各 MSL）确保所有旧包都已经"死"在网络中了。

```
旧连接: (A:52134, B:443), 关闭 → 可能有残包还在路上
等待 2MSL = 60 秒 → 所有残包都已过期
新连接: (A:52134, B:443), 现在是安全的
```

❌ **常见错误**：以为 TIME_WAIT 只会在客户端出现。实际上，**主动关闭方**才会进入 TIME_WAIT。如果服务器主动断开连接（比如 HTTP 的 Keep-Alive 超时），服务器也会进入 TIME_WAIT。

---

## 17.4 CLOSE_WAIT 过多怎么办？（常见线上问题）

如果你在服务器上执行 `netstat`，发现大量连接卡在 CLOSE_WAIT 状态：

**Windows：**
```powershell
netstat -ano | findstr CLOSE_WAIT
```

**Linux：**
```bash
netstat -an | grep CLOSE_WAIT
# 或
ss -tan | grep CLOSE_WAIT
```

这几乎永远意味着**应用层 Bug**——服务器程序收到了客户端的 FIN（第二次挥手已完成），但**没有调用 `close()`**。服务器卡在 CLOSE_WAIT，既不读数据，也不发 FIN，连接永远关不掉。

排查思路：
1. 检查代码中是否在接收循环里忘记处理 EOF（`recv()` 返回 0）
2. 检查是否有异常处理遗漏导致 `close()` 没有被执行到
3. 检查数据库连接池、HTTP 客户端库是否正确释放连接

```
正常流程：                    Bug流程：
recv() == 0 (FIN)            recv() == 0 (FIN)
→ 处理剩余逻辑               → 代码卡住了/异常被吞了
→ close()                    → 永远不调用 close()
→ 进入 LAST_ACK              → 留在 CLOSE_WAIT
```

CLOSE_WAIT 不会自己消失——除非进程被杀。如果你看到 CLOSE_WAIT 数量随时间只增不减，代码里一定有资源泄漏。

---

## 17.5 半关闭（Half-Close）：只关一半

TCP 支持一个有趣的特性：**只关闭发送方向，接收方向仍然开放**。这在某些协议中很有用——比如客户端说"我的请求发完了"，服务器可以开始处理并返回结果，客户端仍然能接收。

在代码层面：

```c
// shutdown(fd, SHUT_WR) 的通俗理解：
// "关闭写端" = "告诉对方我不再发数据了，但我还能收"
// 对方会收到 EOF，但本端仍能接收对方发来的数据

shutdown(sockfd, SHUT_WR);  // 关闭写端，发送 FIN
// 此时仍可以 recv() 接收数据
```

`close()` 和 `shutdown()` 的区别：
- `close()`：关闭 Socket，减少引用计数；当引用计数为 0 时才发送 FIN
- `shutdown(SHUT_WR)`：立即发送 FIN，不管引用计数，但保留读端

这在多进程共享 Socket 的场景下很重要：`close()` 只在最后一个进程关闭时才发 FIN，而 `shutdown()` 立即发 FIN。

---

## 17.6 小结

| 概念 | 要点 |
|------|------|
| 第一次挥手 | A → B: FIN；A 进入 FIN_WAIT_1 |
| 第二次挥手 | B → A: ACK；B 进入 CLOSE_WAIT，A 进入 FIN_WAIT_2 |
| 第三次挥手 | B → A: FIN；B 进入 LAST_ACK |
| 第四次挥手 | A → B: ACK；A 进入 TIME_WAIT，B 进入 CLOSED |
| 为什么四次 | TCP 全双工：关闭是双向的，双方的数据通道独立关闭 |
| TIME_WAIT | 等 2MSL（~60 秒），确保最后 ACK 到达 + 旧残包过期 |
| MSL | 报文最大存活时间，RFC 建议 120 秒，Linux 实际 30 秒（2MSL=60 秒） |
| CLOSE_WAIT 堆积 | 应用层忘记 `close()`，排查代码中的资源管理逻辑 |
| 半关闭 | `shutdown(SHUT_WR)` 只关发送方向，接收方向仍可用 |

---

## 术语表

| 术语 | 解释 |
|------|------|
| **FIN（Finish）** | TCP 标志位，值为 1 时表示请求关闭连接（"我不发数据了"） |
| **FIN_WAIT_1** | 主动关闭方发出 FIN 后进入的状态，等待对方确认 |
| **FIN_WAIT_2** | 主动关闭方收到 ACK 后进入的状态，等待对方的 FIN |
| **CLOSE_WAIT** | 被动关闭方收到 FIN 并回复 ACK 后进入的状态，等待应用层调用 close() |
| **LAST_ACK** | 被动关闭方发出 FIN 后进入的状态，等待对方最后一次 ACK |
| **TIME_WAIT** | 主动关闭方发出最后 ACK 后进入的状态，等待 2MSL 后进入 CLOSED |
| **MSL（Maximum Segment Lifetime）** | TCP 报文在网络中的最大存活时间 |
| **2MSL** | 两倍 MSL，TIME_WAIT 的等待时长，确保残包过期 |
| **半关闭（Half-Close）** | 只关闭发送方向，接收方向保持开放的状态 |

---

## 验证方法

拿出一张白纸，不参考任何资料，完成以下任务：

1. 画出四次挥手的时序图，标注每一步的：
   - 标志位
   - 状态转换（A 和 B 各进入什么状态）
2. 口头回答：
   - 为什么挥手是四次而不是三次？
   - TIME_WAIT 存在的两个原因分别是什么？
   - 2MSL 大概是多少秒？

如果你能独立完成，说明本章目标达成。