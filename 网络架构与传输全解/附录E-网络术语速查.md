# 附录E：网络术语速查

> 本附录聚焦本教程内出现的项目特有概念与反直觉术语。通用名词（如 HTTP、Git）不收录。按首字母/拼音排序。

| 术语 | 简要解释 | 出处章节 |
|------|------|------|
| ACK | TCP 确认标志位，表示"我已收到"。并非只用于确认数据，SYN-ACK 中的 ACK 还用于握手确认。 | 15-TCP三次握手、16-TCP数据传输、17-TCP四次挥手 |
| ACK 延迟确认 | TCP 收到数据后不立即回 ACK，等段时间（通常 ≤500ms）以合并确认多个段，减少包数但引入延迟。 | 16-TCP数据传输 |
| API 网关 | 作为所有客户端入口，统一处理认证、限流、路由的中间层。是微服务架构中的"门面"。 | 37a-服务发现与API网关 |
| ARP 缓存投毒 | ARP 表中写入错误的 IP-MAC 映射，导致流量被劫持。防御手段：静态 ARP 条目、交换机端口安全。 | 08-ARP协议 |
| ARP 请求/应答 | 局域网内用 IP 查 MAC 地址的机制。请求是广播（问"谁是 192.168.1.1？"），应答是单播。 | 08-ARP协议 |
| BDP（带宽延迟积） | 带宽 × RTT = 在途最大数据量。TCP 窗口必须 ≥ BDP 才能跑满带宽。 | 18-TCP拥塞控制、33-网络性能调优入门 |
| Berkeley Packet Filter (BPF) | tcpdump/Wireshark 捕获过滤器的底层语法，在抓包前就决定取舍。仅凭 BPF 语法控制，功能受限。 | 28-Wireshark入门 |
| CDN | Content Delivery Network，内容分发网络。通过边缘节点缓存静态资源，减少延迟和服务端压力。 | 34-CDN |
| CIDR | Classless Inter-Domain Routing，无类域间路由。用 `IP/前缀长度` 表示子网（如 `192.168.1.0/24`），已取代 ABCDE 分类法。 | 09-IP地址-上、10-IP地址-下 |
| ClientHello | TLS 握手第一步，客户端告知支持的加密套件、TLS版本、随机数、SNI。 | 25-HTTPS与TLS |
| CORS | Cross-Origin Resource Sharing，跨域资源共享。由服务端通过 `Access-Control-*` 头控制浏览器跨域行为，不是限制服务器端通信。 | 24b-CORS与同源策略 |
| CUBIC | Linux 默认 TCP 拥塞控制算法。用三次函数调整窗口，比传统 Reno 在高速网络中更快达到稳定状态。 | 18-TCP拥塞控制 |
| Data Offset | TCP 头中的字段（4位），表示 TCP 头长度（单位 4 字节），最小值为 5（即 20 字节 TCP 头，无选项）。 | 05-信号与编码（TCP段结构） |
| DHCP | Dynamic Host Configuration Protocol，自动分配 IP 地址、子网掩码、网关、DNS 等配置。四步：Discover → Offer → Request → ACK(DORA)。 | 09-IP地址-上 |
| DNS 递归 vs 迭代查询 | 递归：你问 A，A 帮你查到底并返回结果。迭代：你问 A，A 说不知道，问 B；循环直到查到或失败。 | 20-DNS-上、21-DNS-下 |
| DNS 污染/劫持 | 本地/运营商/GFW 返回错误 DNS 结果。症状：`nslookup` 返回的 IP 不对。防御：DoH/DoT/换 DNS。 | 21-DNS-下、32-网络故障排查方法论 |
| DoH / DoT | DNS over HTTPS / DNS over TLS。将 DNS 查询加密在 HTTPS/TLS 隧道中，防止中间人窥探和篡改。 | 21-DNS-下 |
| DORA | DHCP 四步流程缩写：Discover → Offer → Request → Acknowledge。 | 09-IP地址-上 |
| DTLS | Datagram TLS，为 UDP 提供加密层的 TLS 变体，WebRTC 中使用。 | 27-其他协议速览 |
| ETag | HTTP 实体标签，标识资源版本。与 `If-None-Match` 配合实现条件请求和缓存验证。 | 24a-HTTP缓存与Cookie |
| FIN | TCP 结束标志位，表示"我没有数据要发了"。FIN-WAIT 和 TIME-WAIT 状态围绕它展开。 | 17-TCP四次挥手 |
| FIN-WAIT-1 / FIN-WAIT-2 | TCP 连接关闭时的中间状态。主动方发出 FIN 后进入 FIN-WAIT-1，收到 ACK 后进入 FIN-WAIT-2。 | 17-TCP四次挥手 |
| FTP 主动 vs 被动模式 | 主动：服务器主动连客户端（端口20→客户端随机端口），易被防火墙挡。被动：客户端连服务器（连接均由客户端发起），更适应NAT环境。 | 27-其他协议速览 |
| GBN（Go-Back-N） | 回退 N 步重传协议。一个包丢，之后所有已发送包全部重传。简单但浪费带宽。TCP 用选择性重传（SACK）改进。 | 16-TCP数据传输、18-TCP拥塞控制 |
| ICMP 洪泛攻击 | 大量 ICMP Echo Request（ping）淹没目标带宽。简单 DoS 攻击手段。 | 13-ICMP |
| IMAP vs POP3 | IMAP 在服务器管理邮件（多设备同步），POP3 下载到本地后删除服务器副本（单设备）。 | 27-其他协议速览 |
| Karn's 算法 | TCP 重传时不计入 RTT 样本，避免"重传的二义性"。即：重传的包，不知道对应的是第几次发送的。 | 18-TCP拥塞控制 |
| Keep-Alive（HTTP层） | HTTP/1.1 默认开启，复用 TCP 连接发送多个请求，减少握手开销。通过 `Connection: keep-alive` 头控制。 | 22-HTTP上 |
| Keep-Alive（TCP层） | 周期性发探测包检查连接是否存活，防止被中间设备静默断开。与 HTTP Keep-Alive 不同。 | 16-TCP数据传输 |
| LACP | Link Aggregation Control Protocol，链路聚合控制协议。多条物理链路绑定为一条逻辑链路，增加带宽和冗余。 | 07-交换机（进阶内容） |
| 乐观锁（HTTP ETag） | 用 ETag / If-Match 实现并发写保护：若资源版本已变，拒绝覆盖。避免"last write wins"丢数据。 | 24a-HTTP缓存与Cookie |
| MAC 地址 | Media Access Control 地址，48位，网卡出厂时烧录的唯一标识。二层设备（交换机）依据 MAC 转发帧。 | 06-MAC地址 |
| MAC 地址表（CAM表） | 交换机内部维护的 MAC ↔ 端口映射表。通过自学习（源MAC出现在哪个口）动态更新。 | 07-交换机 |
| MSS | Maximum Segment Size，TCP 单个段能携带的最大数据量 = MTU - IP头(20) - TCP头(20) = 1460（以太网典型值）。在 SYN 包中协商。 | 15-TCP三次握手、16-TCP数据传输 |
| MTU | Maximum Transmission Unit，链路层能承载的最大包大小。以太网标准 MTU = 1500 字节。超 MTU 需分片。 | 09-IP地址-上、15-TCP三次握手 |
| Nagle 算法 | 小数据先不发，等之前发送的数据被 ACK 后才发，减少小包。在延迟敏感的交互场景（如SSH）应关闭。 | 16-TCP数据传输、33-网络性能调优入门 |
| NAT | Network Address Translation，网络地址转换。私有 IP 通过路由器映射为公网 IP 上网。解决 IPv4 不够用的问题。 | 12-NAT |
| NAT 穿透 | NAT 环境下两端（均在NAT后）如何建立直连。方案：STUN/TURN/ICE。WebRTC 中使用。 | 12-NAT、27-其他协议速览 |
| OSI 七层模型 | 理论参考模型：物理层→数据链路层→网络层→传输层→会话层→表示层→应用层。现实中 TCP/IP 四层合并了上三层。 | 03-OSI七层模型 |
| OUI（组织唯一标识符） | MAC 地址前 24 位，标识网卡制造商。可通过 OUI 数据库查询设备厂商。 | 06-MAC地址 |
| PMTUD | Path MTU Discovery，路径最大传输单元发现。发送端通过设置 IP 不分片标志 + 接收 ICMP 反馈来探测端到端最小 MTU。 | 16-TCP数据传输 |
| PRG 模式 | POST → Redirect → GET。表单提交后重定向到结果页，避免刷新浏览器时重复提交。HTTP 303 See Other 用于此。 | 23-HTTP中 |
| QUIC | Quick UDP Internet Connections，Google 提出的基于 UDP 的传输协议，HTTP/3 底层。内置加密和多路复用，解决 TCP 队头阻塞。 | 27-其他协议速览 |
| RESTful | 一种 API 设计风格：用 URL 定位资源，用 HTTP 方法描述操作（GET查/POST增/PUT改/DELETE删），无状态。 | 22-HTTP上 |
| RST | TCP 重置标志位，表示"立即断开连接"（异常终止）。见到 RST 意味着连接被强行终止，可能有防火墙或应用崩溃。 | 17-TCP四次挥手 |
| RTO（重传超时） | Retransmission Timeout。发送数据后若在 RTO 时间内未收到 ACK，触发重传。通过 RTT 平滑样本动态计算。 | 16-TCP数据传输、18-TCP拥塞控制 |
| RTT | Round-Trip Time，往返延迟。一个包从发送到收到 ACK 的时间。RTT 受物理距离、拥塞、中间设备影响。 | 15-TCP三次握手、18-TCP拥塞控制、33-网络性能调优入门 |
| SACK | Selective ACK，选择性确认。告诉发送方"哪些段已收到、哪些没收到"，只重传丢失段而非整窗。大幅提升丢包场景效率。 | 16-TCP数据传输、18-TCP拥塞控制 |
| ServerHello | TLS 握手第二步，服务器选定加密套件、TLS版本，发送证书和随机数。 | 25-HTTPS与TLS |
| Service Mesh | 服务网格。用 Sidecar 代理（如 Envoy）接管微服务间通信，实现流量控制、观测、安全，与业务解耦。 | 37b-Service-Mesh与全链路追踪 |
| Silly Window Syndrome | 糊涂窗口综合症：接收端窗口很小，发送端每次都只发一点点，包效率极低。解决：Nagle算法(发送方)+Clark方案(接收方不广播小窗口)。 | 16-TCP数据传输、18-TCP拥塞控制 |
| SLIP/PPP | 串行线路 IP / 点对点协议，用于串行链路封装 IP 包。PPP 是早期拨号上网的基础协议。 | 27-其他协议速览 |
| Slow Start | 慢启动。TCP 拥塞控制的一个阶段：cwnd 从 1 MSS 开始，每个 RTT 翻倍指数增长，直到达到 ssthresh。名为"慢"但增长很快。 | 18-TCP拥塞控制 |
| SMTP | Simple Mail Transfer Protocol，发邮件用的协议。客户端提交用 587 端口（STARTTLS），服务器转发用 25 端口。 | 27-其他协议速览 |
| SNI | Server Name Indication。TLS 握手 ClientHello 中的扩展字段，告诉服务器要访问的域名，使同一 IP 可托管多个 HTTPS 站点。 | 25-HTTPS与TLS |
| SSID | Service Set Identifier，无线网络名称标识。Wi-Fi 接入点的名字。 | 05-信号与编码 |
| ssthresh | Slow Start Threshold。TCP 拥塞控制中控制算法切换的阈值：cwnd < ssthresh 走慢启动，≥ ssthresh 走拥塞避免。 | 18-TCP拥塞控制 |
| SYN | TCP 同步标志位，建立连接时使用。SYN=1, ACK=0 表示连接请求（第一次握手），SYN=1, ACK=1 表示确认（第二次握手）。 | 15-TCP三次握手 |
| SYN Cookie | 防范 SYN Flood 攻击的机制：不立即分配连接资源，而是将连接信息编码到 Cookies 中的 ISN 值，收到第三次握手 ACK 时才分配资源。 | 15-TCP三次握手 |
| SYN Flood | 只发 SYN 不发 ACK，耗尽服务器半连接队列。DDoS 常见手段。防御：SYN Cookie、增大 backlog、限制速率。 | 15-TCP三次握手 |
| TCP 半连接队列 | 服务器维护的处于 SYN-RCVD 状态的连接队列。SYN Flood 就是攻击这个队列。 | 15-TCP三次握手 |
| TCP 拥塞窗口（cwnd） | 拥塞控制中，发送方允许在未收到 ACK 时发送的数据量上限。区别于接收方通告的 rwnd（接收窗口）。实际发送窗口 = min(cwnd, rwnd)。 | 18-TCP拥塞控制 |
| TCP 接收窗口（rwnd） | 接收方在 TCP 头中通告的剩余缓冲区大小，相当于"我还能收多少"。若 rwnd=0 则窗口关闭，发送方暂停。 | 16-TCP数据传输、18-TCP拥塞控制 |
| TIME-WAIT | TCP 主动关闭方最后的状态，持续 2MSL（通常 60-120 秒）。目的：①确保最后的 ACK 能被对方收到 ②让旧连接的残余包在网络中消散。 | 17-TCP四次挥手 |
| TLD | Top-Level Domain，顶级域名。如 `.com` `.cn` `.org`。DNS 解析从根→TLD→权威依次查询。 | 20-DNS-上、21-DNS-下 |
| TLS 握手 | HTTPS 建立加密通道的前置步骤，约 2 RTT（TLS 1.2）/ 1 RTT（TLS 1.3）。包括：加密套件协商、证书验证、会话密钥生成。 | 25-HTTPS与TLS |
| TTL | Time To Live，存活跳数（IP层）或缓存时间（DNS层）。IP层TTL每跳减1，归零丢弃，防止包无限循环。DNS层TTL是缓存秒数。 | 09-IP地址-上、13-ICMP、20-DNS-上 |
| UPnP / NAT-PMP | 通用即插即用 / NAT端口映射协议。允许局域网内设备自动请求路由器打开端口映射。方便但有不安全隐患。 | 12-NAT |
| WebSocket | 基于TCP的全双工通信协议，通过HTTP Upgrade握手后保持长连接。适合实时推送、聊天、游戏。 | 26-WebSocket |
| WebSocket 心跳/Ping-Pong | WebSocket 层面的保活机制（区别于TCP Keep-Alive）。客户端发 ping，服务端回 pong，用于检测连接是否断开。 | 26-WebSocket |
| 三握四挥 | "三次握手"建立 TCP 连接，"四次挥手"关闭 TCP 连接。握手=3步因SYN+ACK合一步，挥手=4步因FIN与ACK需分开发。 | 15-TCP三次握手、17-TCP四次挥手 |
| 子网掩码 | 将 IP 地址分为网络部分和主机部分。如 `255.255.255.0` 表示前24位是网络部分，后8位是主机部分。 | 09-IP地址-上、10-IP地址-下 |
| 广播 / 组播 / 单播 | 广播：一对所有（一个网段），组播：一对多（指定组），单播：一对一。ARP请求是广播，视频会议用组播。 | 06-MAC地址、08-ARP协议、09-IP地址-上 |
| 拥塞避免 | 慢启动后的阶段，cwnd 线性增长（每个 RTT +1 MSS），而非指数增长。配合各种丢包检测算法调整 cwnd。 | 18-TCP拥塞控制 |
| 拥塞控制 vs 流量控制 | 拥塞控制（cwnd）：防止网络被塞满，发送方自觉降速。流量控制（rwnd）：防止接收方被压垮，接收方告知能收多少。 | 18-TCP拥塞控制 |
| 毫秒级 RTT 优化 | 缩短 RTT 可通过：减少地理距离（CDN）、选择更好路由、升级带宽（减少排队）、减少中间设备跳数。 | 33-网络性能调优入门、34-CDN |
| 滑动窗口协议 | TCP 的核心传输机制：一次可发多个段而不等 ACK，窗口可动态滑动。既保证可靠性又提高吞吐。 | 16-TCP数据传输 |
| 熔断（Circuit Breaker） | 微服务保护机制：连续失败 N 次后，直接拒绝请求（不再调用故障服务），一段时间后半开探测是否恢复。 | 35-负载均衡、37a-服务发现与API网关 |
| 私有 IP 地址 | 仅局域网内使用的 IP：`10.x.x.x`、`172.16-31.x.x`、`192.168.x.x`。不能直接出现在公网路由表中，需 NAT 转换。 | 09-IP地址-上、12-NAT |
| 粘滞会话（Session Affinity） | 负载均衡器将同一用户的请求始终路由到同一台后端服务器。解决有状态应用的水平扩展问题。 | 35-负载均衡 |
| 缩短 TCP 初始窗口 | TCP 慢启动从 10 MSS（Linux 默认 IW10）开始而非 1 MSS，可减少小文件传输延迟。 | 18-TCP拥塞控制、33-网络性能调优入门 |
| 自治系统（AS） | 由单一机构管理的 IP 路由域，拥有统一的 AS 号。BGP 协议在 AS 之间交换路由信息。 | 11-路由 |
| 负载均衡算法 | 轮询(RR)/加权轮询/最少连接/IP哈希/一致性哈希。选择策略影响性能和粘滞会话需求。 | 35-负载均衡 |
| 路由表 | 路由器/主机判断包"下一跳往哪走"的依据。条目包括：目标网络、掩码、网关、接口、Metric（开销）。 | 11-路由 |
| 透明代理 vs 反向代理 | 透明代理：客户端不需配置，中间设备劫持流量（企业出口）。反向代理：服务端配置，接收外网请求转内网（Nginx）。 | 36-反向代理 |
| 长连接 vs 短连接 | 长连接：复用连接发多请求（HTTP/1.1 Keep-Alive、WebSocket）。短连接：一次请求/响应后关闭（HTTP/1.0 默认）。 | 22-HTTP上、26-WebSocket |
| 队头阻塞（Head-of-Line Blocking） | HTTP/1.1 的痛点：一个请求慢会阻塞后续请求（TCP有序交付）。HTTP/2 多路复用和 QUIC 分别在不同层解决。 | 26-WebSocket、27-其他协议速览 |
| 高可用（HA） | 系统通过冗余消除单点故障。常见手段：多副本部署、健康检查+自动剔除、数据库主从切换。 | 35-负载均衡、36-反向代理 |
| 默认网关 | 局域网内连往外网的出口。路由表中有 `0.0.0.0/0` 的路由条目指向默认网关。 | 09-IP地址-上、11-路由 |

---

> **收录标准**：本附录术语来自教程各章，聚焦项目内首次出现时需解释的概念。若术语在教程中已有自解释的上下文，不重复收录。
>
> **使用建议**：查阅时优先按"出处章节"跳转到原文对应段落，本附录仅提供快速定位与简短回顾。