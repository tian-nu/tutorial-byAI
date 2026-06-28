# 附录D：Wireshark过滤器速查

> **捕获过滤器（Capture Filter）**：抓包前设置，使用 BPF（Berkeley Packet Filter）语法，抓不到的包不会出现在分析界面。
> **显示过滤器（Display Filter）**：抓包后使用，使用 Wireshark 自有语法，只隐藏不删除，可随时切换。

---

## D.1 捕获过滤器（BPF 语法）

### D.1.1 TCP 排查

| 过滤器表达式 | 用途 | 示例场景 |
|------|------|------|
| `tcp` | 只抓TCP包 | 排除UDP/ICMP干扰 |
| `tcp port 80` | 抓取80端口的TCP包 | 只看HTTP明文流量 |
| `tcp port 443` | 抓取443端口的TCP包 | 只看HTTPS流量（加密） |
| `tcp portrange 8000-9000` | 抓取8000-9000区间的TCP端口 | 抓应用服务器集群 |
| `host 192.168.1.100` | 抓取该IP的所有包 | 聚焦某台服务器 |
| `host 192.168.1.100 and tcp port 80` | 组合过滤 | 该IP的HTTP流量 |
| `src host 192.168.1.100` | 只抓源地址为该IP的包 | 排除返回流量 |
| `dst host 192.168.1.100` | 只抓目标地址为该IP的包 | 只看对该机器的请求 |

### D.1.2 DNS 排查

| 过滤器表达式 | 用途 | 示例场景 |
|------|------|------|
| `port 53` | 抓取DNS流量（UDP+TCP） | DNS查询/响应 |
| `udp port 53` | 只抓UDP DNS | 常规DNS查询 |
| `host 8.8.8.8 and udp port 53` | 抓去往特定DNS服务器的查询 | 验证DNS服务器是否可达 |

### D.1.3 HTTP 排查

| 过滤器表达式 | 用途 | 示例场景 |
|------|------|------|
| `tcp port 80 or tcp port 8080` | 抓HTTP明文流量 | 查看明文交互 |
| `host baidu.com` | 抓与该主机的所有流量 | 查看完整连接过程 |

### D.1.4 安全问题排查

| 过滤器表达式 | 用途 | 示例场景 |
|------|------|------|
| `not port 22 and not port 3389` | 排除SSH和RDP（避免抓到自己） | 远程调试时排除管理连接 |
| `net 192.168.1.0/24` | 抓整个子网流量 | 监控内网活动 |
| `broadcast or multicast` | 抓广播和组播 | ARP洪泛、DHCP广播分析 |

### D.1.5 通用过滤

| 过滤器表达式 | 用途 | 示例场景 |
|------|------|------|
| `icmp` | 只抓ICMP包 | 排查 ping/traceroute |
| `arp` | 只抓ARP包 | 分析ARP请求/应答 |
| `ether host aa:bb:cc:dd:ee:ff` | 按MAC地址过滤 | 物理层设备排查 |
| `less 128` | 只抓小于128字节的包 | 聚焦小包（ACK/RST/FIN） |
| `greater 1024` | 只抓大于1KB的包 | 聚焦数据传输 |

---

## D.2 显示过滤器（Wireshark 语法）

### D.2.1 TCP 分析

| 过滤器表达式 | 用途 | 示例场景 |
|------|------|------|
| `tcp` | 只显示TCP | 基础过滤 |
| `tcp.port == 443` | 显示端口443的TCP | 精确端口 |
| `tcp.stream eq 5` | 显示编号为5的TCP流 | ⭐ 右击包 → "Follow TCP Stream" 自动生成 |
| `tcp.flags.syn == 1 and tcp.flags.ack == 0` | 只看SYN包 | 排查握手开始 |
| `tcp.flags.fin == 1` | 只看FIN包 | 排查挥手 |
| `tcp.flags.reset == 1` | 只看RST包 | 排查异常断开 |
| `tcp.analysis.retransmission` | 只看重传包 | 排查网络丢包 |
| `tcp.analysis.duplicate_ack` | 只看重复ACK | 排查乱序/丢包 |
| `tcp.analysis.zero_window` | 只看零窗口通知 | 排查接收端拥塞 |
| `tcp.window_size < 1024` | 窗口小于1KB的包 | 排查低吞吐 |
| `tcp.len > 0` | 只看有数据的TCP段 | 排除纯ACK |

### D.2.2 DNS 分析

| 过滤器表达式 | 用途 | 示例场景 |
|------|------|------|
| `dns` | 显示所有DNS包 | 基础过滤 |
| `dns.flags.response == 1` | 只显示DNS响应 | 看解析结果 |
| `dns.flags.response == 0` | 只显示DNS查询 | 看请求了什么 |
| `dns.qry.name == "baidu.com"` | 查询特定域名的DNS包 | 定位目标域名 |
| `dns.qry.type == 1` | A记录查询（1=A, 28=AAAA, 15=MX） | 按记录类型过滤 |
| `dns.resp.ttl` | 有TTL值的DNS响应 | 检查缓存时长 |

### D.2.3 HTTP/HTTPS 分析

| 过滤器表达式 | 用途 | 示例场景 |
|------|------|------|
| `http` | 显示HTTP包 | 基础过滤 |
| `http.request.method == "GET"` | 只看GET请求 | 按方法过滤 |
| `http.request.method == "POST"` | 只看POST请求 | 查看表单/API提交 |
| `http.response.code == 200` | 只看200响应 | 按状态码过滤 |
| `http.response.code >= 400` | 只看所有错误响应 | 排错利器 |
| `http.host == "api.example.com"` | 特定Host的HTTP流量 | 微服务排查 |
| `http.request.uri contains "login"` | URI中包含login的请求 | 聚焦业务接口 |
| `http.content_type contains "json"` | JSON响应的HTTP包 | API调试 |
| `tls.handshake.type == 1` | TLS ClientHello | HTTPS握手分析 |
| `tls.handshake.type == 2` | TLS ServerHello | 服务端响应 |
| `tls.handshake.extensions_server_name` | 查看SNI（Server Name Indication） | 多域名HTTPS排查 |

### D.2.4 安全问题排查

| 过滤器表达式 | 用途 | 示例场景 |
|------|------|------|
| `arp.duplicate-address-frame` | ARP地址重复检测 | 排查ARP欺骗 |
| `tcp.flags.syn == 1 and tcp.flags.ack == 1` | SYN-ACK包（可统计连接数） | 排查SYN Flood |
| `icmp.type == 8` | ICMP Echo Request（ping请求） | 排查ICMP隧道/探测 |
| `!(tcp.port == 22) and !(tcp.port == 3389)` | 排除管理流量 | 避免干扰 |

### D.2.5 通用技巧

| 过滤器表达式 | 用途 | 示例场景 |
|------|------|------|
| `ip.addr == 192.168.1.100` | 源或目标为该IP的所有包 | 聚焦一台主机 |
| `ip.src == 192.168.1.100` | 源为该IP | 查看发出的包 |
| `ip.dst == 192.168.1.100` | 目标为该IP | 查看收到的包 |
| `eth.addr == aa:bb:cc:dd:ee:ff` | 按MAC地址过滤 | 物理层排查 |
| `frame contains "password"` | 包内容含特定字符串 | ⚠️ 慎用，性能差 |
| `!arp and !dns and !icmp` | 排除常见噪音 | 快速聚焦TCP业务 |

---

## D.3 常用组合速查

| 场景 | 捕获过滤器 | 显示过滤器 |
|:---|------|------|
| 抓某台机器的HTTP | `host 10.0.0.5 and tcp port 80` | `ip.addr == 10.0.0.5 and http` |
| TCP握手失败排查 | `host 10.0.0.5 and tcp` | `tcp.flags.syn == 1 and tcp.flags.ack == 0` |
| 重传分析 | `tcp` | `tcp.analysis.retransmission` |
| DNS解析慢 | `udp port 53` | `dns` → 关注 `dns.time` |
| HTTP 4xx 错误 | `tcp port 80 or tcp port 8080` | `http.response.code >= 400` |
| TLS握手失败 | `tcp port 443` | `tls.handshake` → 关注 `tls.alert_message` |