# 附录A：网络命令速查

> 本附录覆盖10个最常用网络诊断命令，每个命令均提供 Windows / Linux（含 macOS）双平台示例。

---

## A.1 ping — 连通性测试

| 项目 | 说明 |
|------|------|
| **用途** | 测试本机到目标主机的网络连通性，测量往返延迟（RTT） |
| **最常用参数** | `-n`(Win)/`-c`(Linux) 发送次数、`-t`(Win)/无(Linux持续) 持续发送、`-l`(Win)/`-s`(Linux) 包大小 |
| **Windows 示例** | `ping -n 4 -l 1472 8.8.8.8` |
| **Linux/macOS 示例** | `ping -c 4 -s 1472 8.8.8.8` |
| **关键指标** | `time=` 延迟(ms)、`TTL=` 跳数上限、丢包率 |

---

## A.2 traceroute / tracert — 路径追踪

| 项目 | 说明 |
|------|------|
| **用途** | 显示数据包从本机到目标主机经过的每一跳路由器 |
| **最常用参数** | `-d`(Win) 不解析主机名、`-h`(Win)/`-m`(Linux) 最大跳数、`-I`(Linux) 使用ICMP |
| **Windows 示例** | `tracert -d -h 15 baidu.com` |
| **Linux/macOS 示例** | `traceroute -I -m 15 baidu.com` |
| **关键指标** | 每跳IP和延迟、`* * *` 表示超时（可能被防火墙屏蔽） |

---

## A.3 netstat — 网络连接查看

| 项目 | 说明 |
|------|------|
| **用途** | 查看本机所有网络连接、监听端口、路由表、网卡统计 |
| **最常用参数** | `-ano`(Win) 数字显示+PID、`-tunlp`(Linux) TCP/UDP+端口号+监听+进程 |
| **Windows 示例** | `netstat -ano \| findstr "80"` |
| **Linux/macOS 示例** | `netstat -tunlp \| grep 80` |
| **注意** | macOS 上 `netstat` 参数体系不同，推荐用 `lsof -i :端口号` 替代 |

---

## A.4 ss — 套接字统计（Linux专属）

| 项目 | 说明 |
|------|------|
| **用途** | 比 netstat 更快的套接字统计工具，查看连接、监听、状态 |
| **最常用参数** | `-t` TCP、`-u` UDP、`-l` 监听、`-p` 进程、`-n` 数字显示、`-s` 统计摘要 |
| **Windows 示例** | N/A（Windows 无此命令，使用 `netstat` 替代） |
| **Linux 示例** | `ss -tunlp`（等效 `netstat -tunlp`） |
| **统计速览** | `ss -s` 查看 TCP/UDP/RAW 套接字数量汇总 |

---

## A.5 tcpdump — 命令行抓包

| 项目 | 说明 |
|------|------|
| **用途** | 命令行网络包捕获工具，按条件过滤实时流量 |
| **最常用参数** | `-i` 网卡、`-n` 不解析域名、`-c` 抓取数量、`-w` 保存为pcap、`-r` 读取pcap |
| **Windows 示例** | N/A（Win 使用 `windump` 或 Wireshark GUI） |
| **Linux/macOS 示例** | `tcpdump -i eth0 -n port 80 -c 100 -w output.pcap` |
| **注意** | macOS 需 `sudo`；新版 macOS 网卡名类似 `en0` |

---

## A.6 curl — HTTP/HTTPS 客户端

| 项目 | 说明 |
|------|------|
| **用途** | 发送 HTTP/HTTPS 请求，查看响应头、body、调试信息 |
| **最常用参数** | `-I` 仅响应头、`-v` 详细、`-o` 保存文件、`-X` 指定方法、`-H` 加头、`-d` POST数据 |
| **Windows 示例** | `curl -v -I https://baidu.com` |
| **Linux/macOS 示例** | `curl -X POST -H "Content-Type: application/json" -d '{"key":"value"}' https://api.example.com` |
| **断点续传** | `curl -C - -O https://example.com/large.file` |

---

## A.7 dig — DNS 查询（Linux/macOS专属）

| 项目 | 说明 |
|------|------|
| **用途** | 灵活的DNS查询工具，查A/AAAA/MX/CNAME/NS/TXT 等记录 |
| **最常用参数** | `+short` 简洁输出、`@` 指定DNS服务器、`-t` 记录类型、`+trace` 追踪完整解析链 |
| **Windows 示例** | N/A（Win 使用 `nslookup` 替代） |
| **Linux/macOS 示例** | `dig @8.8.8.8 baidu.com +short` |
| **追踪解析** | `dig baidu.com +trace` |

---

## A.8 nslookup — DNS 查询（双平台通用）

| 项目 | 说明 |
|------|------|
| **用途** | DNS查询（比dig功能少，但Windows/Mac/Linux均自带） |
| **最常用参数** | 无参数进入交互模式；`-type=` 指定记录类型 |
| **Windows 示例** | `nslookup -type=A baidu.com 8.8.8.8` |
| **Linux/macOS 示例** | `nslookup -type=MX baidu.com` |
| **反向查询** | `nslookup 8.8.8.8`（IP → 域名） |

---

## A.9 arp — ARP 缓存管理

| 项目 | 说明 |
|------|------|
| **用途** | 查看和管理本机 ARP 表（IP ↔ MAC 映射缓存） |
| **最常用参数** | `-a`(Win/Linux) 显示ARP表、`-d`(Win)/`-d`(Linux) 删除条目 |
| **Windows 示例** | `arp -a`（需管理员权限，否则可能显示不完整） |
| **Linux/macOS 示例** | `arp -a` |
| **删除条目** | `arp -d 192.168.1.1` |

---

## A.10 ipconfig / ip — 网卡信息

| 项目 | 说明 |
|------|------|
| **用途** | 查看本机IP地址、子网掩码、默认网关、DNS等网卡配置 |
| **最常用参数** | Win: `/all` 详细信息、`/flushdns` 清DNS缓存、`/renew` 续租DHCP；Linux: `addr`、`route`、`link` |
| **Windows 示例** | `ipconfig /all` |
| **Linux/macOS 示例** | `ip addr show`（Linux）；`ifconfig`（macOS，已弃用但仍可用） |
| **清DNS缓存** | Win: `ipconfig /flushdns`；Linux: `systemd-resolve --flush-caches`；macOS: `sudo dscacheutil -flushcache; sudo killall -HUP mDNSResponder` |

---

> **快速对照口诀**：通了没 → `ping`；走哪了 → `traceroute`；谁连我 → `netstat`/`ss`；抓到没 → `tcpdump`；返回啥 → `curl`；解析对没 → `dig`/`nslookup`；MAC是谁 → `arp`；我IP是啥 → `ipconfig`/`ip`