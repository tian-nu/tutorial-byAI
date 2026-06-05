# 附录 J：配套练习册（上）—— 第0章 ~ 第39章

> **使用说明**：
> - 每章练习分「基础练习」和「挑战练习」两级。基础练习用于验证理解，挑战练习(标⭐)需综合本章及前几章知识。
> - 编程题均给出明确的输入示例和期望输出，请严格遵循。
> - 每道题标注预计耗时，供自我评估。
> - 前14章（第0~14章）为计算机基础，无 Go 编程，练习形式以思考题、画图题、选择题为主。
> - **题号格式**：本册题号格式为 `章-级-序`（如 `0-1-1` 表示第0章基础练习第1题，`17-2-1` 表示第17章挑战练习第1题）。下册（附录K）题号格式为 `K-章-序`（如 `K-50-1`），加了 `K-` 前缀以区分上下册。
> - 参考答案见 **附录O-练习参考答案（上）**。
> - 建议每完成一章教程后立即完成对应练习，不要跨章堆积。

---

## 第0章：计算机是如何工作的——从输入URL到页面显示

### 基础练习

**0-1-1 DNS 查询流程排序（预计 5 分钟）**
将以下步骤按正确顺序排列：
A. 浏览器向 DNS 服务器查询域名对应的 IP 地址
B. 操作系统检查本地 hosts 文件
C. 浏览器检查自身 DNS 缓存
D. DNS 服务器返回 IP 地址给浏览器
E. 浏览器向目标 IP 发起 HTTP 请求

请写出正确顺序（用字母表示，如 C → B → …）。

**0-1-2 HTTP 请求完整旅程流程图（预计 20 分钟）**
用纸笔或任意绘图工具，画出一张流程图，描述"用户在浏览器输入 `https://www.example.com` 并按下回车后"发生的完整过程。至少包含以下节点：
- DNS 解析
- TCP 三次握手
- TLS 握手
- HTTP 请求发送
- 服务器处理
- HTTP 响应返回
- 浏览器渲染

每个节点旁用一句话标注其作用。

**0-1-3 前后端区别简述（预计 15 分钟）**
用自己的语言写一段约 200 字的文字，解释"前端"和"后端"的区别。要求包含：
- 各自的职责
- 运行的位置
- 关心的核心问题
- 至少举一个具体交互场景的例子

### 挑战练习

**0-2-1 ⭐ 抓包验证（预计 30 分钟）**
打开浏览器的开发者工具（F12），切换到 Network 标签页，访问任意一个 HTTPS 网站（如 `https://www.baidu.com`）。观察并回答：
1. 第一个请求的状态码是多少？
2. 你能看到多少个请求？（大致数量即可）
3. 找一个 CSS 或 JS 文件请求，查看它的 Request Headers 和 Response Headers，记录 3 个你感兴趣的字段并解释含义。
4. 哪些请求的耗时最长？猜测原因。

**0-2-2 ⭐ 对比 HTTP 与 DNS 的作用（预计 10 分钟）**
有人把 DNS 比喻成"互联网的电话簿"，把 HTTP 比喻成"电话接通后的对话语言"。你认为这个比喻贴切吗？如果不贴切，请给出你自己的比喻，并用 100 字左右解释。

---

## 第1章：CPU——计算机的大脑

### 基础练习

**1-1-1 主频迷思（预计 10 分钟）**
小明说："3.0GHz 的 CPU 一定比 2.0GHz 的快。" 请用你自己的话解释为什么这句话不一定正确。要求至少提到两个影响因素。

**1-1-2 核心数与并发（预计 10 分钟）**
小红有一台 4 核 CPU 的电脑，她同时打开了浏览器、音乐播放器和代码编辑器。请问这 3 个程序能否真正"同时"运行？为什么？请用"并发"和"并行"两个概念来解释。

**1-1-3 指令周期（预计 5 分钟）**
CPU 执行一条指令的基本流程是什么？请按顺序写出取指、译码、执行、写回的英文术语，并各用一句话解释。

### 挑战练习

**1-2-1 ⭐ CPU 缓存层级（预计 15 分钟）**
CPU 有 L1、L2、L3 三级缓存。请查阅资料后回答：
1. 为什么需要多级缓存而不是一级超大缓存？
2. L1 缓存通常被分为指令缓存和数据缓存，为什么？
3. 你电脑 CPU 的缓存大小是多少？（提示：Windows 任务管理器 → 性能 → CPU）

**1-2-2 ⭐ 单线程 vs 多线程场景分析（预计 15 分钟）**
以下场景分别更适合高频少核 CPU 还是低频多核 CPU？请说明原因：
- (a) 一个超大型的 Excel 公式计算（单线程计算引擎）
- (b) 同时运行 100 个独立的图片缩略图生成任务
- (c) 一个大型编译任务（如编译 Go 项目，支持并行编译）
- (d) 玩老旧的单线程游戏

---

## 第2章：内存——程序的临时舞台

### 基础练习

**2-1-1 栈与堆的关系图（预计 15 分钟）**
画出栈（Stack）和堆（Heap）在内存中的位置关系示意图,标注以下内容：
- 栈的地址增长方向（高→低 / 低→高）
- 堆的地址增长方向
- 栈帧（Stack Frame）的概念
- 函数调用时栈帧的入栈和出栈

**2-1-2 变量存放位置判断（预计 10 分钟）**
判断以下场景中的变量存放在栈还是堆，并解释原因：
- (a) Go 语言中函数内部声明的 `var x int = 42`
- (b) Go 语言中 `func foo() *int { x := 42; return &x }` 中的 `x`
- (c) C 语言中 `malloc(sizeof(int))` 分配的内存
- (d) 函数参数 `func bar(n int)` 中的 `n`

**2-1-3 内存地址概念（预计 5 分钟）**
什么是内存地址？如果内存是 1GB（2^30 字节），地址至少需要多少位（bit）？请写计算过程。

### 挑战练习

**2-2-1 ⭐ 栈溢出实验（预计 15 分钟）**
了解"栈溢出（Stack Overflow）"的概念。写一段伪代码或描述一段逻辑，说明什么样的代码会导致栈溢出。要求给出具体场景，并解释为什么堆不会出现类似问题。

**2-2-2 ⭐ 内存布局猜想（预计 20 分钟）**
一个典型的进程在内存中分为代码段、数据段、堆、栈四个区域。请画出这四者的位置关系图，并标注：
- 哪些区域是编译时确定的？
- 哪些区域是运行时动态变化的？
- 全局变量和局部变量分别存放在哪个区域？

---

## 第3章：硬盘——数据的永久居所

### 基础练习

**3-1-1 SSD 为什么比 HDD 快（预计 10 分钟）**
用你自己的话解释 SSD 为什么比 HDD 快。要求至少提到 3 个原因，并说明哪个原因是决定性的。

**3-1-2 顺序读写 vs 随机读写（预计 10 分钟）**
对于 HDD 和 SSD 来说，"顺序读写"和"随机读写"的性能差距分别有多大差异？请查阅资料，给出典型数值，并解释为什么 HDD 的差距更大。

**3-1-3 文件系统的作用（预计 5 分钟）**
一句话概述文件系统的作用。然后列举 2 个常见的文件系统（Windows 和 Linux 各一个）。

### 挑战练习

**3-2-1 ⭐ IO 等待分析（预计 15 分钟）**
假设你的后端程序需要从数据库中读取 10000 条记录写入本地文件。请分析：
1. 这个过程中的瓶颈可能在 CPU、内存还是硬盘？
2. 为什么磁盘 IO 通常是后端程序中最慢的操作之一？
3. 程序员可以采取哪些策略来缓解磁盘 IO 的性能问题？（至少列出 2 种）

**3-2-2 ⭐ 数据持久化方案对比（预计 15 分钟）**
谈谈你对"内存是临时存储，硬盘是持久存储"这句话的理解。那么是否存在介于两者之间的存储方案？给出一个例子并简述其原理。

---

## 第4章：操作系统——程序的管家

### 基础练习

**4-1-1 进程 vs 线程类比（预计 10 分钟）**
用自己的语言，用一个生活中的类比来解释"进程"和"线程"的区别。经典类比如"工厂与工人"，如果你觉得不够好，可以给一个自己的版本。

**4-1-2 上下文切换（预计 10 分钟）**
什么是"上下文切换（Context Switch）"？请回答：
1. 上下文切换发生在什么时候？
2. 为什么频繁的上下文切换会影响性能？
3. 进程切换和线程切换哪个开销更大？为什么？

**4-1-3 操作系统核心功能（预计 10 分钟）**
列举操作系统的 4 个核心功能，并对每个功能用一句话举例说明它如何影响你的日常编程。

### 挑战练习

**4-2-1 ⭐ 死锁场景设计（预计 20 分钟）**
用伪代码描述一个死锁（Deadlock）场景。要求：
1. 涉及 2 个线程和 2 个资源
2. 说明死锁的 4 个必要条件如何在这个场景中体现
3. 给出至少一种预防死锁的方法

**4-2-2 ⭐ 用户态与内核态（预计 15 分钟）**
什么是"用户态"和"内核态"？为什么操作系统要区分这两种状态？从用户态切换到内核态需要什么代价？请举例说明一次典型的"用户态→内核态→用户态"的完整过程。

---

## 第5章：终端——程序员的控制台

### 基础练习

**5-1-1 目录结构创建（预计 10 分钟）**
在终端中完成以下操作，并截图保留结果：
```
在 ~/exercises/ 下创建以下目录结构：
exercises/
├── src/
│   ├── go/
│   └── python/
├── data/
│   ├── input/
│   └── output/
└── logs/
```
写出你使用的完整命令序列。

**5-1-2 grep 搜索练习（预计 10 分钟）**
假设有一个文件 `server.log`，包含 1000 行日志，格式如下：
```
2024-01-15 10:30:01 [INFO] Server started on port 8080
2024-01-15 10:30:05 [ERROR] Database connection failed
2024-01-15 10:30:10 [INFO] Retrying connection...
2024-01-15 10:30:15 [WARN] High memory usage: 85%
2024-01-15 10:30:20 [ERROR] Connection timeout
```
请写出 grep 命令来实现以下需求：
- (a) 找出所有 ERROR 行
- (b) 找出所有 ERROR 行并显示行号
- (c) 统计 ERROR 出现的次数
- (d) 找出包含 "ERROR" 或 "WARN" 的行

**5-1-3 管道组合练习（预计 10 分钟）**
使用管道符 `|` 完成以下任务（可在本地创建测试文件后验证）：
- (a) 列出当前目录所有 `.go` 文件，按文件大小排序
- (b) 统计某个 `.go` 文件中非空行的数量（提示：`grep -v "^$"` 过滤空行）
- (c) 找出当前目录及子目录下所有 `.go` 文件，统计总行数（提示：`find` + `xargs` + `wc -l`）

### 挑战练习

**5-1-4 ⭐ Shell 脚本自动化（预计 20 分钟）**
编写一个 Shell 脚本（Bash），功能如下：
1. 在 `~/exercises/auto/` 下创建按日期命名的目录，格式 `YYYY-MM-DD`
2. 在该目录下创建一个 `readme.txt`，内容为创建时间
3. 将该目录压缩为 `YYYY-MM-DD.tar.gz`
4. 运行脚本 3 次，确认产生 3 个不同的压缩包

### 挑战练习

**5-2-1 ⭐ 环境变量与 PATH（预计 15 分钟）**
1. 查看当前 PATH 环境变量的值
2. 解释 PATH 的作用原理
3. 如果你安装了一个新工具 `my-tool` 在 `/opt/myapp/bin/my-tool`，如何不移动文件而让终端能直接执行？
4. 写出加到 `.bashrc` 或 `.zshrc` 中的配置行

---

## 第6章：网络基础（一）——从网线到局域网

### 基础练习

**6-1-1 局域网拓扑图（预计 15 分钟）**
画出你家里的网络拓扑图。要求包含：
- 光猫/调制解调器
- 路由器
- 所有终端设备（电脑、手机、智能家居等）
- 标注有线连接和无线连接
- 标注公网 IP 和内网 IP 的分界点

**6-1-2 IP 地址与子网掩码（预计 10 分钟）**
1. 你的电脑当前的内网 IP 地址是多少？（用 `ipconfig` 或 `ifconfig` 查看）
2. 子网掩码是多少？
3. 根据子网掩码计算你的局域网最多能容纳多少台设备。
4. `192.168.1.0/24` 中 `/24` 表示什么？

**6-1-3 MAC 地址 vs IP 地址（预计 10 分钟）**
用你自己的话解释 MAC 地址和 IP 地址的区别。思考：为什么需要两种地址，只用一种不行吗？

### 挑战练习

**6-2-1 ⭐ ping 与 traceroute 实验（预计 15 分钟）**
在终端中执行：
1. `ping www.baidu.com` —— 记录平均延迟
2. `ping www.google.com` —— 观察能否 ping 通，如果不能，思考为什么
3. `tracert www.baidu.com`（Windows）或 `traceroute www.baidu.com`（Linux/Mac）—— 记录经过了多少跳（hop），哪一跳延迟最高？

**6-2-2 ⭐ NAT 原理简述（预计 15 分钟）**
什么是 NAT（网络地址转换）？请回答：
1. 为什么需要 NAT？
2. 你的手机和电脑共享同一个公网 IP，外部服务器如何区分请求来自哪个设备？
3. NAT 给后端开发带来什么挑战？（提示：P2P、内网穿透）

---

## 第7章：网络基础（二）——互联网如何互联

### 基础练习

**7-1-1 DNS 查询过程描述（预计 15 分钟）**
从 `www.example.com` 到你拿到 IP 地址，DNS 查询经过哪些步骤？请画出流程图，标注递归查询和迭代查询的区别。

**7-1-2 域名结构（预计 10 分钟）**
将域名 `api.user.example.com.cn` 拆分为各个层级，并标注：
- 根域
- 顶级域
- 二级域
- 三级域
- 子域

**7-1-3 CDN 工作原理（预计 10 分钟）**
用 100 字左右解释 CDN 的工作原理。为什么图片、CSS、JS 等静态资源适合用 CDN 加速，而实时性要求高的动态 API 请求不一定适合？

### 挑战练习

**7-2-1 ⭐ 负载均衡策略（预计 20 分钟）**
后端服务通常部署在多台服务器上，由负载均衡器分发请求。请列举至少 3 种常见的负载均衡策略（算法），并分析各自的优缺点。如果用户需要保持会话状态（Session），哪种策略最合适？

**7-2-2 ⭐ 网络分层模型对比（预计 15 分钟）**
画出 OSI 七层模型和 TCP/IP 四层模型的对照图，并标注每层对应的典型协议。然后回答：分层设计的好处是什么？这种思想在你的日常编程中有什么可借鉴之处？

---

## 第8章：网络基础（三）——端口与Socket

### 基础练习

**8-1-1 端口场景判断（预计 10 分钟）**
判断以下场景中使用的端口，并说明理由：
- (a) 浏览器访问 `https://github.com`
- (b) 开发者本地启动一个 Web 服务
- (c) SSH 连接到远程服务器
- (d) 连接 MySQL 数据库

**8-1-2 端口号范围（预计 5 分钟）**
端口号的范围是多少？分为哪三类？各类的范围是什么？如果你自己开发服务，应该选择哪个范围的端口？

**8-1-3 Socket 概念（预计 10 分钟）**
用自己的话解释 Socket 是什么。一个 Socket 连接由哪五个要素唯一确定？为什么同一个端口可以同时建立多个连接？

### 挑战练习

**8-2-1 ⭐ 端口占用排错（预计 15 分钟）**
在本地启动一个占用 8080 端口的程序后，尝试再启动一个同样端口的程序。观察报错信息。然后：
1. 用命令查看 8080 端口被哪个进程占用（Windows: `netstat -ano | findstr 8080`，Linux/Mac: `lsof -i :8080`）
2. 解释为什么一个端口不能被两个程序同时占用
3. 说明 `SO_REUSEADDR` 选项的作用

**8-2-2 ⭐ 多路复用初识（预计 10 分钟）**
Nginx 和 Redis 等高性能服务器通常使用 IO 多路复用技术。请查阅资料后，用自己的话解释什么是 IO 多路复用，以及它为什么比"一个连接一个线程"效率更高。不需要深入技术细节。

---

## 第9章：TCP——可靠传输的基石

### 基础练习

**9-1-1 对比表格填空（预计 10 分钟）**
完成以下 TCP 和 UDP 对比表格：

| 特性 | TCP | UDP |
|------|-----|-----|
| 连接方式 | 面向连接 | |
| 可靠性 | | 不可靠 |
| 顺序保证 | | |
| 传输速度 | | 快 |
| 适用场景 | | |
| 头部开销 | 20~60 字节 | |
| 流控/拥塞控制 | | 无 |

**9-1-2 三次握手顺序题（预计 10 分钟）**
TCP 三次握手的过程如下，请按正确顺序排列并标注每条消息的标志位（SYN/ACK）：
A. 客户端发送 SYN，seq=x
B. 客户端发送 ACK，seq=x+1，ack=y+1
C. 服务器发送 SYN+ACK，seq=y，ack=x+1

请画出完整的时序图，标注客户端和服务器在每个阶段的状态（CLOSED / SYN_SENT / SYN_RCVD / ESTABLISHED）。

**9-1-3 四次挥手（预计 10 分钟）**
为什么 TCP 断开连接需要四次挥手而不是三次？三次握手中服务器可以把 SYN 和 ACK 合并在一条消息中，为什么四次挥手中 FIN 和 ACK 不能合并？

### 挑战练习

**9-2-1 ⭐ TCP 可靠传输机制（预计 20 分钟）**
TCP 通过哪些机制保证可靠传输？请列举至少 4 种，并对每种机制用一句话解释。其中"滑动窗口"机制是如何同时兼顾可靠性和传输效率的？

**9-2-2 ⭐ 粘包问题（预计 15 分钟）**
什么是 TCP 的"粘包"问题？它为什么会发生？列出至少 3 种解决粘包问题的方法。在 Go 后端开发中，如果你自己实现一个 TCP 服务，你倾向于用哪种方法？为什么？

---

## 第10章：UDP——轻量级传输协议

### 基础练习

**10-1-1 UDP 适用场景判断（预计 10 分钟）**
以下场景分别更适合 TCP 还是 UDP？请说明理由：
- (a) 视频会议（如 Zoom）
- (b) 文件下载
- (c) 在线游戏的位置同步
- (d) 发送电子邮件
- (e) DNS 查询

**10-1-2 UDP 数据报结构（预计 10 分钟）**
UDP 的数据报头部只有 8 个字节，包含 4 个字段。请列出这 4 个字段及其长度。相对于 TCP 头部，少了哪些字段？这些缺失如何影响 UDP 的功能？

**10-1-3 无连接的含义（预计 5 分钟）**
"UDP 是无连接的"是什么意思？这对应用程序意味着什么？如果应用程序需要可靠性，它必须自己做什么？

### 挑战练习

**10-2-1 ⭐ TCP vs UDP 选型分析（预计 20 分钟）**
你正在设计一个实时多人在线游戏的网络协议。请分析：
1. 哪些类型的游戏数据应该用 TCP 传输？为什么？
2. 哪些类型的游戏数据应该用 UDP 传输？为什么？
3. 如果必须全部使用 TCP，游戏体验会出现什么问题？
4. 什么是"可靠UDP"？列举一个基于 UDP 实现可靠传输的应用层协议。

**10-2-2 ⭐ UDP 在 QUIC 中的应用（预计 20 分钟）**
HTTP/3 使用基于 UDP 的 QUIC 协议代替了基于 TCP 的 TLS。请查阅资料后：
1. 解释 QUIC 相对于 TCP+TLS 的主要优势
2. 为什么 QUIC 选择 UDP 作为底层传输协议？
3. 这对未来后端开发意味着什么？

---

## 第11章：HTTP（一）——万维网的语言

### 基础练习

**11-1-1 HTTP 请求方法（预计 10 分钟）**
完成以下 HTTP 方法的对比表格：

| 方法 | 幂等性 | 安全性 | 有无请求体 | 典型用途 |
|------|--------|--------|-----------|---------|
| GET | 是 | 是 | | 获取资源 |
| POST | | | 有 | |
| PUT | | | | 更新资源（全量替换）|
| PATCH | | | | |
| DELETE | | | 通常无 | |
| HEAD | | | | |
| OPTIONS | | | | |

**11-1-2 状态码分类（预计 10 分钟）**
HTTP 状态码分为 5 类。请写出各类的范围和含义，并各举一例：
- 1xx：___________，例如 ___
- 2xx：___________，例如 ___
- 3xx：___________，例如 ___
- 4xx：___________，例如 ___
- 5xx：___________，例如 ___

**11-1-3 常见状态码场景判断（预计 10 分钟）**
以下场景应该返回什么状态码？
- (a) 用户成功创建了一个资源
- (b) 用户请求一个不存在的页面
- (c) 服务器内部出错
- (d) 用户未登录访问需要认证的接口
- (e) 资源被永久移动到了新 URL
- (f) 请求格式正确但业务逻辑拒绝（如余额不足）

### 挑战练习

**11-2-1 ⭐ API 设计（预计 25 分钟）**
设计一个博客系统的 RESTful API，要求至少包含以下资源：
- 文章（Article）：CRUD + 按分类筛选 + 按关键词搜索
- 评论（Comment）：针对某篇文章的评论列表 + 发表评论 + 删除评论

请写出：
1. 每个接口的 URL 路径
2. HTTP 方法
3. 请求体示例（JSON）
4. 响应体示例（JSON）
5. 对应的状态码

**11-2-2 ⭐ RESTful 设计原则（预计 15 分钟）**
以下 URL 设计哪些不符合 RESTful 风格？请指出问题并给出改进方案：
- (a) `GET /api/getAllUsers`
- (b) `POST /api/users/create`
- (c) `GET /api/users/123`
- (d) `GET /api/users?page=1&size=20`
- (e) `POST /api/users/123/delete`
- (f) `PUT /api/users/123`

---

## 第12章：HTTP（二）——请求与响应的细节

### 基础练习

**12-1-1 请求头与响应头（预计 10 分钟）**
解释以下 HTTP 头字段的作用，并标注它们属于请求头还是响应头：
- `Content-Type`
- `Authorization`
- `User-Agent`
- `Set-Cookie`
- `Cache-Control`
- `Accept-Encoding`

**12-1-2 Cookie vs Session vs Token（预计 15 分钟）**
用你自己的话解释 Cookie、Session、Token（如 JWT）的区别。可以用"你去图书馆借书"的类比来组织你的解释。

**12-1-3 CORS 理解（预计 10 分钟）**
什么是跨域（CORS）？为什么浏览器要限制跨域请求？如果后端 API 需要被前端跨域调用，后端应该设置哪个响应头？

### 挑战练习

**12-2-1 ⭐ 设计一个认证流程（预计 25 分钟）**
设计一个基于 JWT 的认证流程：
1. 画出用户登录→获取 Token→携带 Token 访问受保护资源→Token 过期→刷新 Token 的完整时序图
2. 说明 Access Token 和 Refresh Token 的区别和各自的有效期建议
3. Token 应该存放在哪里？（对比 Cookie、localStorage、内存的优劣）

**12-2-2 ⭐ 缓存策略设计（预计 20 分钟）**
一个新闻网站 API 需要设计缓存策略。请为以下资源设计合适的 `Cache-Control` 头，并说明理由：
- (a) 静态图片 / JS / CSS 文件
- (b) 新闻列表（每 5 分钟更新一次）
- (c) 新闻详情（发布后几乎不变）
- (d) 用户个人信息（仅该用户可见）
- (e) 实时股票行情数据

---

## 第13章：HTTPS——安全的 HTTP

### 基础练习

**13-1-1 对称加密 vs 非对称加密（预计 15 分钟）**
用你自己的话解释：
1. 对称加密和非对称加密的核心区别
2. 各自的优缺点
3. HTTPS 为什么同时使用两种加密方式？
4. 给一个生活化的类比来解释这两种加密方式

**13-1-2 HTTPS 握手过程（预计 10 分钟）**
将 HTTPS（TLS 1.3）握手的以下步骤按正确顺序排列，并对每步做一句话解释：
A. 服务器发送证书和公钥
B. 客户端验证证书有效性
C. 客户端生成对称密钥并用服务器公钥加密发送
D. 客户端发送支持的加密套件列表
E. 双方用对称密钥开始加密通信
F. 服务器确认加密套件

**13-1-3 证书与 CA（预计 10 分钟）**
什么是数字证书？CA（证书颁发机构）的作用是什么？如果你的网站使用了自签名证书，浏览器会出现什么现象？为什么？

### 挑战练习

**13-2-1 ⭐ 中间人攻击（预计 15 分钟）**
什么是中间人攻击（Man-in-the-Middle Attack）？请描述一个具体的攻击场景。HTTPS 是如何防御中间人攻击的？使用 HTTPS 是否意味着绝对安全？如果不是，还存在哪些可能的风险？

**13-2-2 ⭐ 证书链验证（预计 15 分钟）**
打开任意 HTTPS 网站，点击浏览器地址栏的锁图标，查看证书信息：
1. 证书由哪个 CA 签发？
2. 证书的有效期是多久？
3. 你能看到证书链吗？它有几层？
4. 为什么需要证书链而不是直接信任服务器证书？

---

## 第14章：WebSocket——实时双向通信

### 基础练习

**14-1-1 WebSocket 使用场景判断（预计 10 分钟）**
以下场景中，哪些适合使用 WebSocket，哪些适合使用普通 HTTP 请求或轮询？请说明理由：
- (a) 在线聊天室
- (b) 提交订单
- (c) 实时股票行情
- (d) 查看用户列表（一次性加载）
- (e) 协同文档编辑
- (f) 天气预报查询

**14-1-2 WebSocket vs HTTP 对比（预计 10 分钟）**
完成 WebSocket 和 HTTP 的对比表格：

| 特性 | HTTP | WebSocket |
|------|------|-----------|
| 通信模式 | | 全双工 |
| 连接方式 | | 持久连接 |
| 服务器推送 | | 支持 |
| 协议标识 | http/https | |
| 适用场景 | | |

**14-1-3 WebSocket 握手（预计 10 分钟）**
WebSocket 连接建立前会进行一次 HTTP Upgrade 握手。请描述这个握手过程，并说明以下请求头的含义：
- `Upgrade: websocket`
- `Connection: Upgrade`
- `Sec-WebSocket-Key`

### 挑战练习

**14-2-1 ⭐ 多方案对比（预计 20 分钟）**
实现"服务器向客户端实时推送消息"的能力，有哪几种常见方案？至少列举 3 种（如轮询、长轮询、WebSocket、SSE），对比它们的优缺点和适用场景。

**14-2-2 ⭐ 设计一个在线白板系统（预计 25 分钟）**
假设你要设计一个在线协作白板的通信方案：
1. 画出客户端和服务器之间的通信流程图
2. 哪些信息通过 WebSocket 传输？
3. 如何处理多个用户同时编辑同一元素？（提示：操作转换 OT 或 CRDT 的思路）
4. 断线重连后如何恢复状态？

---

## 第15章：Go 环境搭建

### 基础练习

**15-1-1 环境验证实操（预计 10 分钟）**
在终端中依次执行以下命令，记录输出结果：
```bash
go version
go env GOROOT
go env GOPATH
go env GOPROXY
```
确认 `go version` 显示 1.21 或更高版本。如果版本不符，请先升级。

**15-1-2 第一个 Go 程序（预计 10 分钟）**
创建文件 `hello.go`：
```go
package main

import "fmt"

func main() {
    fmt.Println("Hello, Go!")
}
```
在终端中使用 `go run hello.go` 运行，确认输出 `Hello, Go!`。

**15-1-3 go mod 初始化（预计 10 分钟）**
在一个空目录下执行：
```bash
go mod init exercise/hello
```
观察生成的 `go.mod` 文件内容。然后在该目录的 `main.go` 中编写一个 Hello World 程序并运行。记录 `go.mod` 中的 module 路径和 Go 版本号。

### 挑战练习

**15-2-1 ⭐ GOPROXY 配置（预计 15 分钟）**
1. 将 GOPROXY 设置为国内代理：`go env -w GOPROXY=https://goproxy.cn,direct`
2. 安装一个外部包（如 `github.com/gin-gonic/gin`）测试下载速度
3. 解释 `direct` 的含义
4. 说明 GONOSUMCHECK 和 GOPRIVATE 的作用

**15-2-2 ⭐ 跨平台编译（预计 15 分钟）**
Go 支持交叉编译。请完成以下实验：
1. 编写一个简单的 Go 程序，打印当前操作系统和架构（使用 `runtime.GOOS` 和 `runtime.GOARCH`）
2. 使用 `GOOS=linux GOARCH=amd64 go build` 编译为 Linux 可执行文件
3. 使用 `GOOS=windows GOARCH=amd64 go build` 编译为 Windows 可执行文件
4. 观察生成的文件大小差异
5. 解释为什么 Go 可以轻松实现跨平台编译

---

## 第16章：Go 程序基本结构

### 基础练习

**16-1-1 多文件项目（预计 15 分钟）**
创建以下结构的项目：
```
myapp/
├── go.mod          (module myapp)
├── main.go         (package main, 入口)
├── greeting/
│   └── hello.go    (package greeting, 导出函数 SayHello())
└── mathutil/
    └── calc.go     (package mathutil, 导出函数 Add(a, b int) int)
```
要求：
- `main.go` 调用 `greeting.SayHello()` 和 `mathutil.Add()`
- 所有文件正确使用 package 声明
- `SayHello` 和 `Add` 必须首字母大写（导出标识符）

### 挑战练习

**16-1-2 ⭐ package 与 import 探究（预计 15 分钟）**
编写一个程序验证以下知识点：
1. 同一个目录下的所有 `.go` 文件必须属于同一个 package，验证如果 package 不一致是否编译失败
2. import 路径对应的是目录路径还是 package 名称
3. 如果 import 的包没有被使用，会发生什么？有什么方式可以绕过这个限制（如 `_ "package"` 的作用）？
4. 什么是 init() 函数？它什么时候被调用？一个包中可以有多个 init() 吗？

**16-2-1 ⭐ 内部包访问控制（预计 10 分钟）**
Go 语言没有 `public`/`private`/`protected` 关键字，它是如何控制访问权限的？请回答：
1. 什么使得一个标识符可以被外部包访问？
2. 什么使得它只能在本包内访问？
3. `internal` 目录的特殊规则是什么？

---

## 第17章：变量与常量

### 基础练习

**17-1-1 变量声明方式互换（预计 10 分钟）**
Go 有四种变量声明方式，请将以下声明各用另外三种方式重写：
```go
var x int = 10
```
```go
var y = "hello"
```
```go
z := 3.14
```
```go
var (
    a int
    b string
)
```

**17-1-2 iota 枚举题（预计 15 分钟）**
使用 `iota` 编写以下枚举：
- (a) 星期枚举：Sunday=0, Monday=1, ..., Saturday=6
- (b) 文件大小单位：KB=1<<10, MB=1<<20, GB=1<<30, TB=1<<40
- (c) 权限位标志：Read=1, Write=2, Execute=4（使用 `1 << iota`）

要求输出结果验证。

**17-1-3 零值判断题（预计 10 分钟）**
判断以下变量的零值，并用代码验证：
```go
var a int
var b float64
var c string
var d bool
var e *int
var f []int
var g map[string]int
var h struct{ Name string }
var i interface{}
```

### 挑战练习

**17-2-1 ⭐ 变量作用域与遮蔽（预计 20 分钟）**
编写一个程序展示变量遮蔽（Variable Shadowing）现象：
```go
package main

import "fmt"

var x = 100 // 包级变量

func main() {
    fmt.Println("包级 x:", x) // 输出？
    
    x := 200 // 局部变量，遮蔽包级 x
    fmt.Println("局部 x:", x) // 输出？
    
    if true {
        x := 300 // 块级变量
        fmt.Println("块级 x:", x) // 输出？
    }
    
    fmt.Println("退出块后 x:", x) // 输出？
}
```
1. 写出期望输出
2. 运行验证
3. 解释每一步的 `x` 指向哪个变量
4. 如何在被遮蔽后访问包级变量 `x`？

**17-2-2 ⭐ 类型推导与常量（预计 15 分钟）**
分析以下代码的输出并运行验证：
```go
const (
    a = iota
    b
    c = 100
    d
    e = iota
    f
)

func main() {
    fmt.Println(a, b, c, d, e, f)
}
```
请解释 `iota` 的值的规律，特别是 `c=100` 之后发生了什么。

---

## 第18章：数据类型

### 基础练习

**18-1-1 类型转换练习（预计 15 分钟）**
编写代码完成以下类型转换，并打印结果：
```go
// 输入
var i int = 65
var f float64 = 3.14
var b byte = 66
var s string = "hello"

// 要求输出：
// i 转 float64：65.0
// f 转 int：3（注意截断）
// i 转 string（注意不是 "65" 而是 "A"，因为 65 是 'A' 的 ASCII 码）
// b 转 rune 并打印字符
// s 中每个字符的 rune 值
```
写出完整可运行代码并验证输出。

**18-1-2 byte 和 rune 的区别实操（预计 15 分钟）**
编写一个程序，接收一个包含中英文混合的字符串（如 `"Hello世界！"`），完成以下操作：
1. 用 `[]byte` 遍历并打印每个字节
2. 用 `[]rune` 遍历并打印每个字符
3. 用 `len()` 分别统计字节数和字符数
4. 解释为什么两个长度不同

**18-1-3 类型别名 vs 类型定义（预计 10 分钟）**
```go
type MyInt1 int    // 类型定义
type MyInt2 = int  // 类型别名
```
两者有什么区别？编写代码验证：
- `MyInt1` 和 `int` 是否可以直接相互赋值？
- `MyInt2` 和 `int` 是否可以直接相互赋值？
- 哪个可以添加自己的方法？

### 挑战练习

**18-2-1 ⭐ 数值溢出（预计 15 分钟）**
```go
var a uint8 = 255
a = a + 1
fmt.Println(a) // 输出？
```
1. 写出期望输出
2. 解释为什么
3. 在 Go 中如何检测溢出？（提示：math 包或手动检查）
4. 编写一个安全的加法函数 `SafeAddUint8(a, b uint8) (uint8, error)`

**18-2-2 ⭐ 类型系统深度理解（预计 20 分钟）**
Go 是强类型、静态类型的语言。请回答：
1. "强类型"和"静态类型"分别是什么意思？
2. Go 没有隐式类型转换，这有什么好处和代价？
3. 与 JavaScript、Python 的类型系统相比，Go 的设计哲学是什么？
4. `interface{}`（或 `any`）在 Go 类型系统中扮演什么角色？

---

## 第19章：运算符

### 基础练习

**19-1-1 位运算练习（预计 15 分钟）**
不写代码，手工计算以下表达式的值：
```go
a := 0b1010_1010  // 二进制：170
b := 0b1111_0000  // 二进制：240
```
计算：
- (a) `a & b`  = ？（二进制和十进制）
- (b) `a | b`  = ？
- (c) `a ^ b`  = ？
- (d) `^a`     = ？（按位取反，Go 中 `^a` 等价于 `^a` 一元运算）
- (e) `a << 2` = ？
- (f) `b >> 3` = ？

写出计算过程，然后用代码验证。

**19-1-2 运算符优先级判断（预计 10 分钟）**
判断以下表达式的值（不运行代码，手工推算优先级）：
```go
a := 2 + 3*4        // ?
b := (2 + 3) * 4    // ?
c := 10 / 3         // ?（整数除法）
d := 10 % 3         // ?
e := 1<<2 + 3       // ?（注意位移运算符的优先级）
f := true || false && false  // ?
g := !true || false  // ?
```
写出期望结果，然后运行验证。

**19-1-3 赋值运算符简化（预计 10 分钟）**
将以下代码简化为使用复合赋值运算符（`+=`、`-=`、`*=` 等）的版本：
```go
x = x + 10
y = y - 5
z = z * 2
count = count + 1
flag = !flag
```

### 挑战练习

**19-2-1 ⭐ 位运算实战——权限系统（预计 20 分钟）**
设计一个使用位运算的权限系统：
```go
const (
    PermRead    = 1 << iota // 1
    PermWrite               // 2
    PermExecute             // 4
    PermDelete              // 8
)
```
要求实现以下功能：
1. 给用户添加权限：`AddPerm(current, PermWrite)`
2. 移除用户权限：`RemovePerm(current, PermWrite)`
3. 检查用户是否有某权限：`HasPerm(current, PermWrite)` 返回 bool
4. 切换权限：`TogglePerm(current, PermWrite)`

输入示例：
```go
userPerm := PermRead | PermExecute // 用户有读和执行权限
fmt.Println(HasPerm(userPerm, PermRead))    // true
fmt.Println(HasPerm(userPerm, PermWrite))   // false
```

**19-2-2 ⭐ 位运算高级——交换变量（预计 10 分钟）**
使用异或运算（^）不借助临时变量交换两个整数的值：
```go
a, b := 10, 20
// TODO: 使用 ^ 交换 a 和 b 的值
```
写出代码并解释每一步的数学原理。

---

## 第20章：流程控制——if 与 switch

### 基础练习

**20-1-1 判断闰年（预计 10 分钟）**
编写函数 `IsLeapYear(year int) bool`，判断给定年份是否为闰年。
闰年规则：能被 4 整除但不能被 100 整除，或能被 400 整除。
```
输入: 2000  → 输出: true
输入: 1900  → 输出: false
输入: 2024  → 输出: true
输入: 2023  → 输出: false
```

**20-1-2 成绩等级（预计 10 分钟）**
编写函数 `GetGrade(score int) string`，使用 switch 实现以下映射：
```
90-100 → "A"
80-89  → "B"
70-79  → "C"
60-69  → "D"
0-59   → "F"
其他   → "Invalid"
```
```
输入: 85 → 输出: "B"
输入: 72 → 输出: "C"
输入: 101 → 输出: "Invalid"
```

**20-1-3 季节判断（预计 10 分钟）**
编写函数 `GetSeason(month int) string`：
```
3-5   → "Spring"
6-8   → "Summer"
9-11  → "Autumn"
12,1,2 → "Winter"
其他  → "Unknown"
```
使用 switch 的多种写法实现（带表达式的 switch 和条件 switch）。

### 挑战练习

**20-2-1 ⭐ 简易计算器（预计 20 分钟）**
编写一个从命令行读取表达式的简易计算器：
```
输入格式: "12 + 5"
支持运算符: + - * /
```
要求：
1. 使用 `fmt.Scanf` 或 `fmt.Sscan` 解析输入
2. 使用 switch 判断运算符
3. 处理除数为零的错误
4. 支持浮点数运算

```
输入: "10 + 3.5"   → 输出: 13.5
输入: "8 / 0"      → 输出: "Error: division by zero"
输入: "7 * 2.5"    → 输出: 17.5
```

**20-2-2 ⭐ if 初始化语句（预计 10 分钟）**
Go 的 if 语句支持在条件前加一个初始化语句。分析以下代码，写出期望输出并解释作用域：
```go
func demo() {
    x := 10
    if y := x * 2; y > 15 {
        fmt.Println("y is", y)
    }
    // fmt.Println(y) // 这里能否编译通过？为什么？
    
    if z, err := someFunc(); err != nil {
        fmt.Println("error:", err)
    } else {
        fmt.Println("z:", z)
    }
    // 这里 z 和 err 还能访问吗？
}
```

---

## 第21章：for 循环

### 基础练习

**21-1-1 九九乘法表（预计 15 分钟）**
编写程序输出标准的九九乘法表，格式如下：
```
1×1=1
1×2=2  2×2=4
1×3=3  2×3=6  3×3=9
...
1×9=9  2×9=18 3×9=27 4×9=36 5×9=45 6×9=54 7×9=63 8×9=72 9×9=81
```
要求：使用两个嵌套 for 循环，对齐方式不作强制要求，但每个算式之间用 tab 分隔。

**21-1-2 斐波那契数列（预计 15 分钟）**
编写函数 `Fibonacci(n int) []int`，返回前 n 项斐波那契数列：
```
输入: 7  → 输出: [0, 1, 1, 2, 3, 5, 8]
输入: 1  → 输出: [0]
输入: 2  → 输出: [0, 1]
```
要求使用 for 循环而不是递归。

**21-1-3 break 与 continue 练习（预计 15 分钟）**
编写程序，遍历 1 到 100：
1. 打印所有奇数（使用 continue 跳过偶数）
2. 找到第一个能被 3、5、7 同时整除的数时停止循环（使用 break）
3. 使用带标签的 for 循环，在内层循环中使用 `break 标签` 跳出外层循环

### 挑战练习

**21-2-1 ⭐ for range 遍历探究（预计 15 分钟）**
编写代码探究以下问题，每个用代码验证并解释：
1. `for range` 遍历切片时，第二个返回值是元素的值还是副本？
2. 修改遍历过程中的切片（追加元素），for range 会怎样？
3. `for range` 遍历 map 时，顺序是否固定？
4. 如何按顺序遍历 map？

**21-2-2 ⭐ 水仙花数（预计 20 分钟）**
"水仙花数"是指一个 n 位数（n≥3），它的每个位上的数字的 n 次幂之和等于它本身。例如：153 = 1³ + 5³ + 3³。
编写程序找出所有三位数的水仙花数（100~999）。
```
期望输出: [153, 370, 371, 407]
```
额外要求：将算法扩展为可处理任意 n 位的自幂数，函数签名 `FindArmstrongNumbers(n int) []int`。

---

## 第22章：数组

### 基础练习

**22-1-1 数组反转（预计 10 分钟）**
编写函数 `ReverseArray(arr [5]int) [5]int`，返回反转后的数组：
```
输入: [1, 2, 3, 4, 5]  → 输出: [5, 4, 3, 2, 1]
输入: [10, 20, 30, 40, 50] → 输出: [50, 40, 30, 20, 10]
```
注意：数组长度是类型的一部分，请使用确定长度的数组。

**22-1-2 查找最大值与位置（预计 10 分钟）**
编写函数 `FindMax(arr []int) (max int, index int)`：
```
输入: [3, 7, 2, 9, 1, 5] → 输出: max=9, index=3
输入: [1, 2, 3]           → 输出: max=3, index=2
```
如果有多个最大值，返回第一个出现的索引。

**22-1-3 二维数组操作（预计 15 分钟）**
编写代码完成以下二维数组操作：
1. 创建 3×3 的二维数组并初始化为单位矩阵
```
1 0 0
0 1 0
0 0 1
```
2. 计算对角线元素之和
3. 转置矩阵（行列互换）

### 挑战练习

**22-2-1 ⭐ 数组是值类型（预计 15 分钟）**
Go 中数组是值类型而非引用类型。请编写代码验证：
1. 将一个数组赋值给另一个变量，修改新变量，原数组不变
2. 将数组传给函数，函数内修改，函数外不变
3. 将数组的指针传给函数，函数内修改，函数外是否变化？
4. 对比切片的行为差异

**22-2-2 ⭐ 螺旋矩阵生成（预计 25 分钟）**
编写函数 `GenerateSpiralMatrix(n int) [][]int`，生成 n×n 的螺旋矩阵：
```
输入: 3
输出:
1 2 3
8 9 4
7 6 5

输入: 4
输出:
1  2  3  4
12 13 14 5
11 16 15 6
10 9  8  7
```

---

## 第23章：切片

### 基础练习

**23-1-1 切片操作练习（预计 15 分钟）**
给定切片 `s := []int{1, 2, 3, 4, 5, 6, 7, 8}`，写出以下操作的期望结果，然后运行验证：
```go
s[:4]       // ?
s[3:]       // ?
s[2:5]      // ?
s[2:5:6]    // ?（注意第三个参数控制容量）
s = append(s[:3], s[4:]...) // 删除索引 3 的元素
```

**23-1-2 切片去重（预计 15 分钟）**
编写函数 `RemoveDuplicates(s []int) []int`：
```
输入: [1, 2, 2, 3, 4, 4, 4, 5] → 输出: [1, 2, 3, 4, 5]
输入: [1, 1, 1]                 → 输出: [1]
```
要求保持原有顺序。

**23-1-3 共享底层数组陷阱验证（预计 15 分钟）**
```go
a := []int{1, 2, 3, 4}
b := a[1:3]    // b 是 [2, 3]
b[0] = 100     // 修改 b 的第一个元素
fmt.Println(a) // 输出？
fmt.Println(b) // 输出？

b = append(b, 200) // b 的容量足够时
fmt.Println(a) // 输出？
fmt.Println(b) // 输出？

b = append(b, 300, 400, 500) // b 的容量不够，发生扩容
fmt.Println(a) // 输出？
fmt.Println(b) // 输出？
```
写出各阶段期望输出，解释底层数组发生了什么变化。

### 挑战练习

**23-2-1 ⭐ 切片扩容机制探究（预计 20 分钟）**
编写代码探究 Go 切片的扩容规则：
1. 创建一个空切片，用 for 循环不断 append，在每次 append 后打印 len 和 cap
2. 观察 cap 的变化规律
3. 当切片容量较小时（< 1024），扩容倍率是多少？
4. 当容量较大时（>= 1024），扩容倍率是多少？
5. 一次性 append 多个元素时，扩容行为如何？

**23-2-2 ⭐ 实现自定义切片功能（预计 25 分钟）**
不使用 Go 内置的切片 append 功能（不允许用 `append`），使用数组和手动内存管理实现：
1. `MyAppend(s []int, elem int) []int`
2. `MyInsert(s []int, index int, elem int) []int`
3. `MyRemove(s []int, index int) []int`

提示：使用 `make` 创建新切片，手动复制元素。
```
输入: MyInsert([]int{1, 2, 4, 5}, 2, 3)  → 输出: [1, 2, 3, 4, 5]
输入: MyRemove([]int{1, 2, 3, 4}, 1)      → 输出: [1, 3, 4]
```

---

## 第24章：Map

### 基础练习

**24-1-1 词频统计（预计 15 分钟）**
编写函数 `WordCount(text string) map[string]int`，统计一段英文文本中每个单词出现的次数。忽略大小写，假设单词由空格和标点分隔。
```
输入: "Hello world, hello Go. Go is great!"
输出: map[string]int{"hello":2, "world":1, "go":2, "is":1, "great":1}
```
提示：使用 `strings.FieldsFunc` 或 `strings.Split`。

**24-1-2 学生成绩管理（预计 20 分钟）**
实现一个简单的学生成绩管理系统：
```go
func AddScore(scores map[string]int, name string, score int)
func GetScore(scores map[string]int, name string) (int, bool)
func DeleteStudent(scores map[string]int, name string)
func AverageScore(scores map[string]int) float64
func HighestScore(scores map[string]int) (string, int)
```
```
操作示例:
scores := make(map[string]int)
AddScore(scores, "Alice", 85)
AddScore(scores, "Bob", 92)
AddScore(scores, "Charlie", 78)
AverageScore(scores)         // → 85.0
HighestScore(scores)         // → "Bob", 92
```

**24-1-3 map 遍历排序（预计 15 分钟）**
编写函数 `PrintSortedByKey(m map[string]int)`，按键的字母顺序打印 map 内容：
```
输入: map[string]int{"banana":3, "apple":5, "cherry":2}
输出:
apple: 5
banana: 3
cherry: 2
```
提示：先提取所有 key → 排序 → 遍历。

### 挑战练习

**24-2-1 ⭐ map 并发安全问题（预计 20 分钟）**
Go 的 map 不是并发安全的。请编写代码验证：
1. 启动 100 个 goroutine 同时向同一个 map 写入数据
2. 观察是否出现 `fatal error: concurrent map writes`
3. 使用 `sync.Mutex` 解决这个问题
4. 使用 `sync.Map` 解决这个问题
5. 对比两种方案的使用场景和性能

**24-2-2 ⭐ 字符频率分析（预计 25 分钟）**
编写函数 `CharFrequency(filename string) (map[rune]int, error)`，读取文本文件（支持中文），统计每个字符出现的频率，按频率从高到低输出 Top 10。
```
输入文件内容: "你好世界，Hello World！"
输出:
' ' 2
'l' 3
'o' 2
'世' 1
'界' 1
...
```
提示：需要处理 UTF-8 编码。

---

## 第25章：字符串

### 基础练习

**25-1-1 字符串反转（注意 rune）（预计 15 分钟）**
编写函数 `ReverseString(s string) string`：
```
输入: "hello"         → 输出: "olleh"
输入: "你好世界"       → 输出: "界世好你"
输入: "Go语言"         → 输出: "言语oG"
```
注意：不能简单地将 string 转为 `[]byte` 再反转，需要正确处理 UTF-8 多字节字符。

**25-1-2 敏感词过滤（预计 15 分钟）**
编写函数 `FilterSensitive(text string, words []string) string`：
```
输入: text = "这是一条包含敏感信息的消息"
      words = ["敏感", "消息"]
输出: "这是一条包含**信息的**"
```
要求：将匹配到的敏感词替换为相同长度的 `*`。

**25-1-3 统计中文字符数（预计 10 分钟）**
编写函数 `CountChinese(s string) int`，统计字符串中中文字符的数量：
```
输入: "Hello世界！Go语言"  → 输出: 5
输入: "ABC123"              → 输出: 0
```
提示：中文字符的 Unicode 范围约为 `\u4E00`~`\u9FFF`。

### 挑战练习

**25-2-1 ⭐ strings.Builder vs + 拼接（预计 15 分钟）**
编写代码对比字符串拼接的几种方式：
1. 使用 `+` 拼接
2. 使用 `fmt.Sprintf`
3. 使用 `strings.Builder`
4. 使用 `bytes.Buffer`

每种方式拼接 10000 个字符串，使用 `time.Now()` 计时，输出每种方式的耗时。解释为什么效率差异这么大。

**25-2-2 ⭐ 简单的正则匹配（预计 20 分钟）**
使用 `regexp` 包完成以下功能（不要求手写正则引擎）：
1. 验证邮箱格式是否有效
2. 验证手机号是否是中国大陆手机号（1 开头的 11 位数字）
3. 从一段文本中提取所有 URL

```
输入: "联系我: test@example.com 或 13800138000，访问 https://golang.org"
输出:
邮箱: test@example.com
手机号: 13800138000
URL: https://golang.org
```

---

## 第26章：函数基础

### 基础练习

**26-1-1 计算器函数（预计 15 分钟）**
编写四个独立函数，每个接收两个 float64 参数并返回 float64：
```go
func Add(a, b float64) float64
func Subtract(a, b float64) float64
func Multiply(a, b float64) float64
func Divide(a, b float64) (float64, error)  // 除数为 0 时返回 error
```
```
Add(3, 5)         → 8.0
Subtract(10, 3)   → 7.0
Multiply(4, 2.5)  → 10.0
Divide(10, 2)     → 5.0
Divide(10, 0)     → error: "division by zero"
```

**26-1-2 多返回值练习（预计 10 分钟）**
编写函数 `MinMax(s []int) (min, max int)`：
```
输入: [3, 7, 1, 9, 4]  → 输出: min=1, max=9
输入: [5]              → 输出: min=5, max=5
输入: []               → 输出: min=0, max=0（使用命名返回值）
```

**26-1-3 命名返回值（预计 10 分钟）**
将 26-1-2 改为使用命名返回值（named return values）的版本。解释命名返回值的好处和潜在陷阱，特别说明"裸露 return"的含义和何时应该避免。

### 挑战练习

**26-2-1 ⭐ 可变参数函数（预计 15 分钟）**
编写函数 `Sum(nums ...int) int`，支持传入任意数量的 int：
```
Sum(1, 2, 3)          → 6
Sum(10, 20, 30, 40)   → 100
Sum()                 → 0
```
然后编写 `Max(nums ...int) int`，找出最大值。思考：如果传入 0 个参数，如何合理处理？

**26-2-2 ⭐ 函数作为参数（预计 20 分钟）**
编写函数 `Filter(s []int, fn func(int) bool) []int`：
```go
nums := []int{1, 2, 3, 4, 5, 6, 7, 8, 9, 10}

// 过滤偶数
Filter(nums, func(n int) bool { return n%2 == 0 })  // → [2, 4, 6, 8, 10]

// 过滤大于5的数
Filter(nums, func(n int) bool { return n > 5 })      // → [6, 7, 8, 9, 10]
```

**26-2-3 ⭐ 高阶函数链（预计 25 分钟）**
实现以下泛化的数据转换函数：
```go
func Map(s []int, fn func(int) int) []int
func Reduce(s []int, fn func(int, int) int, initial int) int
```
```
Map([]int{1, 2, 3}, func(n int) int { return n * 2 })     // → [2, 4, 6]
Reduce([]int{1, 2, 3, 4}, func(a, b int) int { return a + b }, 0) // → 10
```

---

## 第27章：函数高级

### 基础练习

**27-1-1 闭包计数器（预计 15 分钟）**
编写函数 `NewCounter() func() int`，每次调用返回的闭包时计数器加 1：
```go
c1 := NewCounter()
c1() // → 1
c1() // → 2
c1() // → 3

c2 := NewCounter()
c2() // → 1
c2() // → 2
c1() // → 4  （c1 和 c2 独立）
```

**27-1-2 defer 执行顺序（预计 10 分钟）**
写出以下代码的输出并解释 defer 的 LIFO 行为：
```go
func demo() {
    defer fmt.Println("A")
    defer fmt.Println("B")
    defer fmt.Println("C")
    fmt.Println("D")
}
// 输出顺序？
```
以及：
```go
func demo2() {
    for i := 0; i < 3; i++ {
        defer fmt.Println(i)
    }
}
// 输出顺序？注意 defer 捕获变量的时机
```

**27-1-3 panic 与 recover 练习（预计 15 分钟）**
编写函数 `SafeDivide(a, b int) (result int, err error)`：
1. 正常除法时返回结果
2. 当 b 为 0 时触发 panic
3. 使用 defer + recover 捕获 panic 并转换为 error 返回

```go
SafeDivide(10, 2)  // → result=5, err=nil
SafeDivide(10, 0)  // → result=0, err="division by zero"
```

### 挑战练习

**27-2-1 ⭐ defer 与返回值陷阱（预计 15 分钟）**
写出以下代码的输出并解释：
```go
func f1() (r int) {
    defer func() {
        r++
    }()
    return 0
}

func f2() int {
    r := 0
    defer func() {
        r++
    }()
    return r
}
```
f1() 返回什么？f2() 返回什么？详细解释 defer 修改命名返回值和修改局部变量的区别。

**27-2-2 ⭐ 函数选项模式（预计 20 分钟）**
实现 Go 中常用的"函数选项模式（Functional Options Pattern）"来配置一个 HTTP 服务器：
```go
type ServerConfig struct {
    Port    int
    Timeout time.Duration
    MaxConn int
}

type Option func(*ServerConfig)

func WithPort(port int) Option { ... }
func WithTimeout(t time.Duration) Option { ... }
func WithMaxConn(n int) Option { ... }
func NewServer(opts ...Option) *ServerConfig { ... }
```
```go
s := NewServer(
    WithPort(8080),
    WithTimeout(30 * time.Second),
    WithMaxConn(100),
)
fmt.Printf("%+v\n", s) // {Port:8080 Timeout:30s MaxConn:100}
```

---

## 第28章：指针

### 基础练习

**28-1-1 swap 函数用指针实现（预计 10 分钟）**
编写函数 `Swap(a, b *int)`，交换两个整数的值：
```go
x, y := 10, 20
Swap(&x, &y)
fmt.Println(x, y)  // → 20 10
```
不修改函数签名，确保函数通过指针直接修改原始变量。

**28-1-2 new vs make 区别题（预计 15 分钟）**
| 特性 | new | make |
|------|-----|------|
| 适用类型 | | slice/map/chan |
| 返回值 | 指针 | |
| 是否初始化 | | 是（初始化内部结构）|
| 示例代码 | | |

填空完成后，编写代码验证 `new` 和 `make` 对 slice 的区别：
```go
s1 := new([]int)
s2 := make([]int, 0)
// s1 和 s2 的类型分别是什么？
// 哪个可以直接 append？
```

**28-1-3 指针访问结构体（预计 10 分钟）**
```go
type Person struct {
    Name string
    Age  int
}

p := &Person{Name: "Alice", Age: 30}
```
以下两种写法是否等价？
```go
(*p).Name = "Bob"
p.Name = "Bob"
```
Go 编译器做了什么来简化指针访问结构体字段？

### 挑战练习

**28-2-1 ⭐ 指针与逃逸分析（预计 20 分钟）**
使用 `go build -gcflags="-m"` 查看以下代码的逃逸分析结果：
```go
func foo() *int {
    x := 42
    return &x // x 逃逸到堆上
}

func bar() int {
    x := 42
    return x // x 不逃逸，在栈上
}
```
1. 运行逃逸分析命令，观察输出
2. 解释什么是"逃逸"
3. 逃逸到堆和留在栈上各有什么优缺点？
4. 作为开发者，何时应该关心逃逸分析？

**28-2-2 ⭐ 指针接收者的坑（预计 15 分钟）**
```go
type Counter struct {
    count int
}

func (c Counter) Increment() {
    c.count++  // 值接收者，不影响原始值
}

func (c *Counter) IncrementPtr() {
    c.count++  // 指针接收者，影响原始值
}
```
编写代码验证两种接收者的区别。特别注意：
```go
c := Counter{}
c.Increment()
fmt.Println(c.count)  // 输出？

// Go 会自动取地址或解引用
c.IncrementPtr()  // c 是值，但 Go 自动帮你取地址 (&c).IncrementPtr()
fmt.Println(c.count)  // 输出？
```

---

## 第29章：结构体

### 基础练习

**29-1-1 学生信息管理系统（CRUD）（预计 30 分钟）**
实现学生信息管理：
```go
type Student struct {
    ID    int
    Name  string
    Age   int
    Grade string
}

// 使用切片存储所有学生
var students []Student

func AddStudent(s Student)           // 添加学生，ID 自动递增
func GetStudent(id int) (Student, bool) // 按 ID 查找
func UpdateStudent(id int, s Student) bool // 按 ID 更新
func DeleteStudent(id int) bool      // 按 ID 删除
func ListStudents() []Student        // 返回所有学生
```
```go
AddStudent(Student{Name: "Alice", Age: 20, Grade: "A"})
AddStudent(Student{Name: "Bob", Age: 22, Grade: "B"})
ListStudents()  // → [{1 Alice 20 A} {2 Bob 22 B}]
```

**29-1-2 结构体嵌套与 JSON 序列化（预计 20 分钟）**
```go
type Address struct {
    City    string `json:"city"`
    Street  string `json:"street"`
    ZipCode string `json:"zip_code"`
}

type Employee struct {
    Name    string  `json:"name"`
    Age     int     `json:"age"`
    Address Address `json:"address"`
    Salary  float64 `json:"salary,omitempty"`
}
```
1. 创建 Employee 实例
2. 序列化为 JSON（`json.Marshal`）
3. 反序列化回来（`json.Unmarshal`）
4. 解释 struct tag（如 `json:"city"`、`json:"salary,omitempty"`）的作用
5. 如果 Address 的某个字段为空，JSON 中会怎样？

### 挑战练习

**29-2-1 ⭐ 结构体比较（预计 15 分钟）**
Go 中哪些结构体可以比较（使用 `==`）？哪些不能？编写代码验证：
```go
type A struct { x int }
type B struct { x int; y []int }
type C struct { x int; m map[string]int }
```
- `A{} == A{}` 能否编译？结果是什么？
- `B{} == B{}` 能否编译？为什么？
- `C{} == C{}` 能否编译？为什么？
- 如何使用 `reflect.DeepEqual` 来比较不可比较的结构体？

**29-2-2 ⭐ 构建一个图书管理系统（预计 30 分钟）**
设计一个图书管理系统：
```go
type Book struct {
    ISBN   string
    Title  string
    Author string
    Status string // "available", "borrowed"
}

type Library struct {
    Books map[string]*Book // key: ISBN
}
```
实现方法：
```go
func (lib *Library) AddBook(b *Book)
func (lib *Library) BorrowBook(isbn string) error  // 借书，状态改为 borrowed
func (lib *Library) ReturnBook(isbn string) error  // 还书，状态改为 available
func (lib *Library) SearchByTitle(title string) []*Book
func (lib *Library) ListAvailable() []*Book
```

---

## 第30章：方法

### 基础练习

**30-1-1 为结构体添加方法（预计 15 分钟）**
为上一章的学生结构体添加方法：
```go
type Student struct {
    ID    int
    Name  string
    Age   int
    Scores []int
}

func (s Student) AverageScore() float64  // 计算平均分
func (s Student) IsPass() bool            // 平均分 >= 60 为通过
func (s *Student) AddScore(score int)     // 添加成绩
func (s Student) String() string          // 自定义打印格式: "ID:1, Name:Alice, Avg:85.5"
```
```go
s := Student{ID: 1, Name: "Alice", Scores: []int{80, 90, 85}}
fmt.Println(s.AverageScore())  // → 85.0
fmt.Println(s.IsPass())        // → true
s.AddScore(95)
fmt.Println(s.AverageScore())  // → 87.5
fmt.Println(s)                 // → "ID:1, Name:Alice, Avg:87.5"
```

**30-1-2 值接收者 vs 指针接收者实验（预计 15 分钟）**
编写代码对比值接收者和指针接收者的区别，包含以下场景：
1. 使用值接收者修改结构体字段 → 验证原始值不变
2. 使用指针接收者修改结构体字段 → 验证原始值变了
3. 值接收者方法能被指针类型调用吗？
4. 指针接收者方法能被值类型调用吗？

设计一个带计数器的结构体验证以上所有场景。

### 挑战练习

**30-2-1 ⭐ 方法集与接口实现（预计 20 分钟）**
"方法集（Method Set）"决定了类型实现了哪些接口。请完成以下探究：
```go
type MyInt int

func (m MyInt) ValueMethod() {}
func (m *MyInt) PointerMethod() {}
```
1. `var i MyInt = 10` —— `i.ValueMethod()` 能调用吗？
2. `i.PointerMethod()` 能调用吗？（Go 会自动取地址吗？）
3. 定义一个接口 `type MyInterface interface { ValueMethod(); PointerMethod() }`，`MyInt` 和 `*MyInt` 分别实现了这个接口吗？
4. 将接口变量赋值为 `MyInt` 值和 `*MyInt` 指针，分别测试

**30-2-2 ⭐ 实现一个简单的栈结构（预计 20 分钟）**
使用方法和结构体实现一个泛型（用 `interface{}` 或 Go 1.18+ 的泛型）栈：
```go
type Stack struct {
    data []int
}

func (s *Stack) Push(v int)
func (s *Stack) Pop() (int, bool)
func (s *Stack) Peek() (int, bool)
func (s *Stack) Len() int
func (s *Stack) IsEmpty() bool
```
```go
s := &Stack{}
s.Push(1)
s.Push(2)
s.Push(3)
s.Pop()  // → (3, true)
s.Pop()  // → (2, true)
s.Peek() // → (1, true)
s.Pop()  // → (1, true)
s.Pop()  // → (0, false)  -- 栈空
```

---

## 第31章：接口

### 基础练习

**31-1-1 接口实现多态（预计 20 分钟）**
```go
type Shape interface {
    Area() float64
    Perimeter() float64
}

type Rectangle struct {
    Width, Height float64
}

type Circle struct {
    Radius float64
}

type Triangle struct {
    A, B, C float64 // 三边长
}
```
为以上三个结构体实现 `Shape` 接口，然后编写函数：
```go
func PrintShapeInfo(s Shape) {
    fmt.Printf("Area: %.2f, Perimeter: %.2f\n", s.Area(), s.Perimeter())
}
```
```go
PrintShapeInfo(Rectangle{Width: 3, Height: 4})  // → Area: 12.00, Perimeter: 14.00
PrintShapeInfo(Circle{Radius: 5})               // → Area: 78.54, Perimeter: 31.42
PrintShapeInfo(Triangle{A: 3, B: 4, C: 5})      // → Area: 6.00, Perimeter: 12.00
```

**31-1-2 类型断言练习（预计 15 分钟）**
编写函数 `DescribeShape(s Shape)`，使用类型断言和类型 switch 来识别具体的形状类型：
```go
func DescribeShape(s Shape) {
    switch sh := s.(type) {
    case Rectangle:
        fmt.Printf("这是矩形，宽=%.1f，高=%.1f\n", sh.Width, sh.Height)
    case Circle:
        fmt.Printf("这是圆形，半径=%.1f\n", sh.Radius)
    case Triangle:
        fmt.Printf("这是三角形，边长=%.1f, %.1f, %.1f\n", sh.A, sh.B, sh.C)
    default:
        fmt.Println("未知形状")
    }
}
```

**31-1-3 空接口应用（预计 15 分钟）**
使用空接口 `interface{}`（或 `any`）编写以下功能：
```go
// 判断值类型
func TypeOf(v interface{}) string

// 打印任意类型的切片
func PrintAnySlice(slice []interface{})

// 判断两个 interface{} 类型是否相同
func SameType(a, b interface{}) bool
```
```go
TypeOf(42)           // → "int"
TypeOf("hello")      // → "string"
TypeOf(3.14)         // → "float64"
TypeOf([]int{1,2})   // → "[]int"
```

### 挑战练习

**31-2-1 ⭐ 接口组合（预计 20 分钟）**
```go
type Reader interface {
    Read(p []byte) (n int, err error)
}

type Writer interface {
    Write(p []byte) (n int, err error)
}

type Closer interface {
    Close() error
}

type ReadWriter interface {
    Reader
    Writer
}

type ReadWriteCloser interface {
    Reader
    Writer
    Closer
}
```
1. 实现一个 `File` 结构体，满足 `ReadWriteCloser` 接口（模拟实现即可）
2. 验证接口组合的继承关系
3. 编写函数 `Copy(r Reader, w Writer) (int, error)`，从 Reader 读取并写入 Writer

**31-2-2 ⭐ 排序接口（预计 20 分钟）**
Go 标准库的 `sort.Interface` 要求实现三个方法：`Len()`、`Less(i, j int)`、`Swap(i, j int)`。请实现：
```go
type StudentSlice []Student

// 实现 sort.Interface
func (s StudentSlice) Len() int
func (s StudentSlice) Less(i, j int) bool  // 按分数降序，分数相同按姓名升序
func (s StudentSlice) Swap(i, j int)
```
```go
students := StudentSlice{
    {Name: "Alice", Score: 85},
    {Name: "Bob", Score: 92},
    {Name: "Charlie", Score: 85},
}
sort.Sort(students)
// 期望顺序: Bob(92), Alice(85), Charlie(85)
```

---

## 第32章：错误处理

### 基础练习

**32-1-1 自定义错误类型（预计 20 分钟）**
实现自定义错误类型：
```go
type ValidationError struct {
    Field   string
    Message string
}

// 实现 error 接口
func (e *ValidationError) Error() string
```
编写函数 `ValidateUser(name string, age int) error`：
- name 为空 → 返回 `&ValidationError{Field: "name", Message: "name is required"}`
- age < 0 或 age > 150 → 返回 `&ValidationError{Field: "age", Message: "age must be between 0 and 150"}`
- 验证通过 → 返回 nil
- 通过类型断言区分不同的错误类型

**32-1-2 错误包装与解包（预计 15 分钟）**
使用 `fmt.Errorf` 的 `%w` 格式化动词和 `errors.Unwrap`：
```go
func ReadConfig(path string) error {
    // 模拟：底层返回 "file not found"
    baseErr := errors.New("file not found")
    return fmt.Errorf("failed to read config from %s: %w", path, baseErr)
}

func LoadApp() error {
    err := ReadConfig("/etc/app/config.json")
    if err != nil {
        return fmt.Errorf("load app failed: %w", err)
    }
    return nil
}
```
要求：
1. 调用 `LoadApp()`，打印完整的错误链
2. 使用 `errors.Is(err, baseErr)` 判断是否是文件找不到的错误
3. 使用 `errors.As(err, &target)` 进行错误类型断言
4. 解释 `%w` 和 `%v` 在 `fmt.Errorf` 中的区别

### 挑战练习

**32-2-1 ⭐ 重试机制（预计 25 分钟）**
编写一个带指数退避的重试机制：
```go
func Retry(fn func() error, maxRetries int, baseDelay time.Duration) error
```
要求：
1. 调用 `fn`，如果返回 nil 则成功
2. 如果返回 error，等待 `baseDelay` 后重试
3. 每次重试等待时间翻倍（指数退避），如 100ms → 200ms → 400ms → 800ms
4. 达到 `maxRetries` 次后仍失败，返回包含所有尝试错误信息的 error
5. 使用 `context.Context` 支持超时取消（前瞻第37章内容，可简化为 time.After）

**32-2-2 ⭐ 错误处理模式对比（预计 20 分钟）**
对比 Go 的错误处理模式和其他语言（如 Java 的 try-catch、Rust 的 Result）：
1. Go 的显式错误返回有什么优缺点？
2. 写出一个容易出现的 Go 错误处理陷阱：忘记检查 error 或遮蔽 error
3. `if err != nil` 的大量重复是 Go 社区常被诟病的地方，你如何看？有什么缓解的方法？

---

## 第33章：包与模块

### 基础练习

**33-1-1 创建自己的包（预计 25 分钟）**
创建一个简单的 math 工具包，目录结构：
```
mymath/
├── go.mod
├── arith/
│   └── arith.go        (package arith: Add, Subtract, Multiply, Divide)
├── stats/
│   └── stats.go        (package stats: Mean, Max, Min)
└── main.go             (使用以上两个包)
```
要求：
1. 包名与目录名一致
2. 导出的函数首字母大写
3. 使用 `go mod init` 初始化模块
4. `main.go` 正确 import 并使用函数
5. 使用 `go run .` 运行验证

**33-1-2 init 函数实验（预计 15 分钟）**
编写一个包含 `init()` 函数的包，验证以下行为：
1. init 函数在 main 函数之前自动执行
2. 一个包可以有多个 init 函数（分布在不同文件中）
3. 被导入的包的 init 先于当前包的 init 执行
4. 空白导入（`_ "package"`）是否会触发 init

### 挑战练习

**33-2-1 ⭐ internal 目录的使用（预计 15 分钟）**
Go 中 `internal` 目录有特殊含义：
```
myapp/
├── go.mod
├── internal/
│   └── db/
│       └── db.go       (package db)
├── api/
│   └── handler.go      (package api)
└── main.go
```
1. 验证 `api/handler.go` 能否 import `myapp/internal/db`
2. 创建一个外部项目，看能否 import `myapp/internal/db`
3. 解释 `internal` 的限制规则是什么
4. 这种设计对项目架构有什么好处

---
## 第34章：Goroutine

### 基础练习

**34-1-1 并发打印（预计 15 分钟）**
编写程序启动 5 个 goroutine，每个 goroutine 打印自己的编号和当前时间戳：
```go
for i := 1; i <= 5; i++ {
    go func(id int) {
        fmt.Printf("Goroutine %d: %s\n", id, time.Now().Format("15:04:05.000"))
    }(i) // 注意：需要传参，否则闭包会捕获循环变量
}
time.Sleep(1 * time.Second)
```
1. 连续运行 3 次，观察顺序是否相同
2. 如果把 `(i)` 参数去掉会怎样？验证一下
3. 为什么 goroutine 的执行顺序不可预测

**34-1-2 观察 Goroutine 调度（预计 15 分钟）**
编写程序对比以下两种方式计算 1 到 1000000 的平方和：
1. 单 goroutine 顺序计算
2. 4 个 goroutine 并行计算（每个负责 1/4 的数字范围）

记录两种方式的执行时间，观察加速比。思考：为什么加速比可能不到 4 倍？

### 挑战练习

**34-2-1 ⭐ 并发爬虫模拟（预计 30 分钟）**
模拟并发爬取 20 个 URL（用一个随机延时函数模拟网络请求），要求：
1. 限制最大并发数为 5（使用带缓冲的 channel 作为信号量）
2. 使用 `sync.WaitGroup` 等待所有 goroutine 完成
3. 收集结果并汇总打印每个 URL 的抓取耗时
4. 打印总耗时对比（并发 vs 串行预期的耗时）

**34-2-2 ⭐ Goroutine 泄漏（预计 15 分钟）**
编写一个会造成 goroutine 泄漏的程序，并回答：
1. 什么是 goroutine 泄漏？
2. 如何用 `runtime.NumGoroutine()` 检测泄漏？
3. 使用 `context.Context` 来优雅地取消 goroutine

---
## 第35章：Channel

### 基础练习

**35-1-1 生产者消费者（预计 20 分钟）**
使用无缓冲 channel 实现生产者-消费者模型：
```go
func producer(ch chan<- int) // 生产 1-10，生产完关闭 channel
func consumer(ch <-chan int) // 消费并打印，直到 channel 关闭
```
```go
期望输出（顺序可能不同）：
生产者生产: 1
消费者消费: 1
生产者生产: 2
消费者消费: 2
...
生产者生产: 10
消费者消费: 10
```

**35-1-2 管道 Pipeline（预计 20 分钟）**
实现数字处理管道：`生成数字 → 平方 → 过滤(>50) → 打印`
```go
func generate(nums ...int) <-chan int
func square(in <-chan int) <-chan int
func filter(in <-chan int, threshold int) <-chan int
```
```go
输入: generate(1,2,3,4,5,6,7,8,9,10)
经过 square 后: 1,4,9,16,25,36,49,64,81,100
经过 filter(>50) 后: 64,81,100
最终输出: 64, 81, 100
```

**35-1-3 select 超时控制（预计 15 分钟）**
用 `select` 和 `time.After` 实现超时控制：
```go
func FetchWithTimeout(url string, timeout time.Duration) (string, error)
```
模拟网络请求（随机延时 0-3 秒），超时时间设为 1.5 秒：
```
请求1 耗时 0.8s → 成功返回
请求2 耗时 2.1s → 超时错误
```

### 挑战练习

**35-2-1 ⭐ 扇出-扇入模式（预计 30 分钟）**
实现 Fan-Out / Fan-In 模式：
1. 一个 generator 持续生成任务
2. 启动 3 个 worker（fan-out）从同一个 channel 读取并处理
3. 将 3 个 worker 的结果合并到一个 channel（fan-in）
4. 主 goroutine 从合并的 channel 读取结果并打印

处理函数：模拟处理任务（随机延时 100-500ms），返回 `"任务 X 被 Worker Y 处理完成"`。

**35-2-2 ⭐ 用 channel 实现信号量（预计 20 分钟）**
使用带缓冲的 channel 实现一个信号量，限制并发访问数：
```go
type Semaphore struct {
    ch chan struct{}
}

func NewSemaphore(maxConcurrency int) *Semaphore
func (s *Semaphore) Acquire()
func (s *Semaphore) Release()
```
用 10 个 goroutine，但信号量限制为 3，验证最多同时 3 个 goroutine 在执行。

---
## 第36章：同步原语

### 基础练习

**36-1-1 互斥锁保护计数器（预计 15 分钟）**
编写两个版本的程序，对比结果：
1. 100 个 goroutine 各对共享计数器 +1000 次，**不加锁**
2. 同样操作，使用 `sync.Mutex` 保护
```go
不加锁版本：每次结果不同，可能 < 100000
加锁版本：结果恒为 100000
```

**36-1-2 WaitGroup 等待（预计 10 分钟）**
使用 `sync.WaitGroup` 改写第 35 章的生产者消费者程序：
1. 不再使用 `time.Sleep` 等待 goroutine
2. 使用 `wg.Add()`、`wg.Done()`、`wg.Wait()` 精确控制
3. 解释如果 `wg.Add(1)` 写在 goroutine 内部而非外部会造成什么竞态问题

**36-1-3 sync.Once 实验（预计 15 分钟）**
```go
var once sync.Once
var config map[string]string

func InitConfig() {
    once.Do(func() {
        fmt.Println("初始化配置...")
        time.Sleep(500 * time.Millisecond)
        config = map[string]string{"host": "localhost"}
    })
}
```
1. 在 10 个 goroutine 中同时调用 `InitConfig()`，验证初始化函数只执行一次
2. 如果 `once.Do` 中的函数 panic 了，再次调用会重新执行吗？实验验证

### 挑战练习

**36-2-1 ⭐ RWMutex 读写锁对比（预计 20 分钟）**
使用 `sync.RWMutex` 实现并发安全的缓存：
1. 读操作用 `RLock/RUnlock`，写操作用 `Lock/Unlock`
2. 对比 `Mutex` 和 `RWMutex` 在读多写少场景下的性能差异
3. 编写 benchmark 对比：100 个读 goroutine + 1 个写 goroutine

**36-2-2 ⭐ sync.Map vs map + Mutex（预计 20 分钟）**
Go 1.9 引入了 `sync.Map`。请编写代码对比：
1. `map + sync.Mutex` 方案
2. `sync.Map` 方案
3. 在什么场景下 `sync.Map` 比 `map+Mutex` 有优势？
4. 在什么场景下 `sync.Map` 反而不如？

---
## 第37章：Context

### 基础练习

**37-1-1 Context 超时控制（预计 20 分钟）**
```go
func SimulateWork(ctx context.Context, name string, duration time.Duration) error {
    select {
    case <-time.After(duration):
        fmt.Printf("%s: 完成\n", name)
        return nil
    case <-ctx.Done():
        fmt.Printf("%s: 被取消 (%v)\n", name, ctx.Err())
        return ctx.Err()
    }
}
```
1. 创建 2 秒超时的 context，启动一个 1 秒的操作 → 应成功
2. 创建 2 秒超时的 context，启动一个 3 秒的操作 → 应超时
3. 使用 `defer cancel()` 释放资源

**37-1-2 Context 取消传播（预计 20 分钟）**
创建三层 context 树：
```
Background → ctx1 (timeout 3s) → ctx2 (timeout 5s) → ctx3 (无超时)
```
启动 3 个 goroutine 分别使用 ctx1、ctx2、ctx3，观察当 ctx1 的 deadline 到达后：
1. ctx2 是否也被取消？（父取消→子自动取消）
2. ctx3 是否也被取消？

**37-1-3 WithValue 传递（预计 15 分钟）**
```go
type contextKey string

const (
    KeyRequestID contextKey = "requestID"
    KeyUserID    contextKey = "userID"
)
```
在请求处理的 3 层函数调用中，通过 context 传递 requestID 和 userID：
1. 不要用 string 直接作为 context key（避免冲突）
2. 编写辅助函数 `GetRequestID(ctx)` 和 `GetUserID(ctx)` 做类型安全的值提取

### 挑战练习

**37-2-1 ⭐ 实现 HTTP 请求超时中间件（预计 25 分钟）**
使用 `net/http` 和 `context` 实现一个简单的 HTTP 客户端：
```go
func FetchWithContext(ctx context.Context, url string) (string, error)
```
要求：
1. 创建 `http.Request` 时附带 context
2. 整个请求（DNS + 连接 + 读取）都有超时控制
3. context 取消时，正在进行的 HTTP 请求应该被终止
4. 测试正常请求和超时请求

**37-2-2 ⭐ Context 最佳实践总结（预计 15 分钟）**
请总结以下 context 使用的最佳实践：
1. context 应该作为函数的第几个参数？
2. context 应该存储在结构体中吗？
3. 什么时候应该用 `context.Background()`，什么时候用 `context.TODO()`？
4. 传 nil context 给函数可以吗？有什么风险？
5. 为什么 context 的 Value 只应用于传递请求范围的数据？

---
## 第38章：文件操作

### 基础练习

**38-1-1 读取文件统计行数/字数（预计 20 分钟）**
```go
func FileStats(filename string) (lines, words, chars, bytes int, err error)
```
测试：读取一个自建的测试文件，统计行数、单词数、字符数、字节数。
要求：
1. 使用 `bufio.Scanner` 逐行读取
2. 单词按空白字符分割
3. 对比 `wc` 命令的输出验证结果

```go
stats, err := FileStats("sample.txt")
// lines=10, words=150, chars=850, bytes=850
```

**38-1-2 写入 CSV 文件（预计 20 分钟）**
使用 `encoding/csv` 包：
```go
func WriteStudentsCSV(filename string, students []Student) error
func ReadStudentsCSV(filename string) ([]Student, error)
```
数据示例：
```csv
ID,Name,Age,Grade
1,张三,20,A
2,李四,22,B
3,王五,21,A
```
要求：读写后数据一致。

**38-1-3 递归遍历目录（预计 15 分钟）**
使用 `filepath.Walk` 或 `filepath.WalkDir`：
```go
func WalkDirectory(root string) error
```
统计指定目录下：
1. 文件总数
2. 各文件扩展名分布
3. 总文件大小（人类可读格式：B/KB/MB）

### 挑战练习

**38-2-1 ⭐ 简易日志文件轮转（预计 35 分钟）**
实现支持文件大小轮转的日志写入器：
```go
type RotatingWriter struct {
    dir        string
    prefix     string
    maxSize    int64 // 单文件最大字节
    maxFiles   int   // 保留文件数
    current    *os.File
    currentSize int64
    mu         sync.Mutex
}
```
```go
func NewRotatingWriter(dir, prefix string, maxSize int64, maxFiles int) (*RotatingWriter, error)
func (w *RotatingWriter) Write(p []byte) (n int, err error)
func (w *RotatingWriter) Close() error
```
要求：
1. 单个文件超过 `maxSize` 时自动创建新文件
2. 文件名格式：`prefix_2024-01-15_001.log`
3. 超过 `maxFiles` 时删除最旧的文件
4. 并发写入安全

**38-2-2 ⭐ 实现 tail -f 功能（预计 30 分钟）**
实现类似 Linux `tail -f` 的功能：
```go
func TailFollow(filename string) error
```
1. 打开文件并输出最后 N 行（N 默认 10，可配置）
2. 持续监听文件变化（新写入内容），实时输出到控制台
3. 处理文件被轮转（logrotate）的情况（文件名变了但内容需要续上）
4. 支持优雅退出（Ctrl+C）

---
## 第39章：序列化

### 基础练习

**39-1-1 JSON 编解码结构体（预计 20 分钟）**
```go
type BlogPost struct {
    ID        int       `json:"id"`
    Title     string    `json:"title"`
    Content   string    `json:"content"`
    Author    string    `json:"author"`
    Tags      []string  `json:"tags"`
    CreatedAt time.Time `json:"created_at"`
    Published bool      `json:"published"`
}
```
1. 创建实例并填充数据
2. Marshal → 漂亮的 JSON 字符串
3. Unmarshal JSON 字符串 → 新结构体
4. 对比原始数据和解码数据
5. 处理 JSON 中不存在的字段（结构体字段设为零值）

**39-1-2 自定义 JSON 字段名（预计 15 分钟）**
```go
type ServerConfig struct {
    Host    string `json:"host"`                    // 基础映射
    Port    int    `json:"port"`                    // 基础映射
    Debug   bool   `json:"debug,omitempty"`         // 零值时省略
    SSL     bool   `json:"ssl_enabled"`             // 自定义名称
    Token   string `json:"-"`                       // 不序列化
    Addr    string `json:"address,omitempty"`       // 零值省略 + 自定义名
}
```
1. 创建包含零值的实例，序列化观察 omitempty 效果
2. 反序列化时不包含 `token` 字段，验证结构体字段值为空
3. 写出 struct tag 的通用语法格式

### 挑战练习

**39-2-1 ⭐ 自定义 JSON Marshaler/Unmarshaler（预计 30 分钟）**
为以下类型实现 `json.Marshaler` 和 `json.Unmarshaler` 接口：
```go
type Temperature float64
// JSON 中格式: "25.5°C"
// Go 中存储: 25.5

type PhoneNumber struct {
    CountryCode string // "+86"
    Number      string // "13800138000"
}
// JSON 中格式: "+86-13800138000"
// Go 中存储: PhoneNumber{CountryCode: "+86", Number: "13800138000"}

type EventTime time.Time
// JSON 中格式: "2024-01-15 10:30:00"（自定义格式，非 RFC3339）
// Go 中存储: time.Time 类型
```
测试序列化和反序列化的往返一致性。

**39-2-2 ⭐ JSON 与配置文件（预计 25 分钟）**
设计并实现一个读取 JSON 配置文件的程序：
```go
type AppConfig struct {
    Server   ServerConfig   `json:"server"`
    Database DatabaseConfig `json:"database"`
    Logging  LoggingConfig  `json:"logging"`
}

type ServerConfig struct {
    Host string `json:"host"`
    Port int    `json:"port"`
}

type DatabaseConfig struct {
    Driver string `json:"driver"`
    DSN    string `json:"dsn"`  // Data Source Name
}

type LoggingConfig struct {
    Level  string `json:"level"`
    Output string `json:"output"` // "stdout" 或文件路径
}
```
1. 创建默认配置实例
2. 序列化写入 `config.json` 文件
3. 从文件读取并反序列化
4. 实现配置验证函数 `func (c *AppConfig) Validate() error`
5. 环境变量覆盖配置的功能（如 `SERVER_PORT` 覆盖 `server.port`）

---
## 参考答案索引

本练习册的参考答案见 **附录K：配套练习册参考答案（上）**，包含：
- 第0-14章：思考题参考要点、图表示例、选择题答案
- 第15-39章：编程题参考代码、测试用例、关键思路解析

| 章节范围 | 参考答案位置 | 说明 |
|---------|-------------|------|
| 第0章 ~ 第14章 | 附录K §K.0 ~ §K.14 | 思考题要点、图表示例、表格答案 |
| 第15章 ~ 第29章 | 附录K §K.15 ~ §K.29 | Go基础编程参考代码 |
| 第30章 ~ 第39章 | 附录K §K.30 ~ §K.39 | Go进阶编程参考代码 |

> **建议**：先独立完成所有练习，遇到卡点至少思考 15 分钟后再查阅参考答案。学会读懂错误信息、查阅官方文档，也是学习的一部分。

---

> **完成日期记录**：`____年____月____日`
>
> **自我评估**：完成率 ____% ｜ 无需参考答案独立解决率 ____% ｜ 需重点复习的章节：________