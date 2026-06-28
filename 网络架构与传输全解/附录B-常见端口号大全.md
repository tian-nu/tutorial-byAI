# 附录B：常见端口号大全

> 端口范围分类：**0-1023**（知名端口/Well-Known Ports，需管理员权限绑定）、**1024-49151**（注册端口）、**49152-65535**（动态/私有端口）。

---

## B.1 Web 服务类

| 端口 | 协议 | 用途 | 需管理员绑定 |
|------|------|------|:---:|
| 80 | HTTP | 标准 HTTP 明文传输 | ✅ |
| 443 | HTTPS | HTTP over TLS/SSL 加密传输 | ✅ |
| 8080 | HTTP（备用） | Web 代理、Java 应用服务器（Tomcat/Jetty）默认端口 | ❌ |
| 8443 | HTTPS（备用） | Java 应用服务器 HTTPS 默认端口 | ❌ |
| 3000 | HTTP（开发） | Node.js / React / Ruby on Rails 开发服务器常用 | ❌ |
| 5000 | HTTP（开发） | Flask / Python 开发服务器常用 | ❌ |

---

## B.2 数据库类

| 端口 | 协议 | 用途 | 需管理员绑定 |
|------|------|------|:---:|
| 3306 | MySQL | MySQL 数据库默认端口 | ❌ |
| 5432 | PostgreSQL | PostgreSQL 数据库默认端口 | ❌ |
| 6379 | Redis | Redis 键值存储默认端口 | ❌ |
| 27017 | MongoDB | MongoDB 数据库默认端口 | ❌ |
| 1433 | SQL Server | Microsoft SQL Server 默认端口 | ❌ |
| 1521 | Oracle | Oracle 数据库默认端口 | ❌ |
| 9200 | Elasticsearch | Elasticsearch HTTP API 端口 | ❌ |

---

## B.3 邮件类

| 端口 | 协议 | 用途 | 需管理员绑定 |
|------|------|------|:---:|
| 25 | SMTP | 邮件发送（服务器间转发） | ✅ |
| 465 | SMTPS | SMTP over SSL（已废弃，但仍广泛使用） | ✅ |
| 587 | SMTP | 邮件提交（客户端 → 服务器，STARTTLS） | ✅ |
| 110 | POP3 | 邮件接收（下载到本地，明文） | ✅ |
| 995 | POP3S | POP3 over SSL（加密接收） | ✅ |
| 143 | IMAP | 邮件接收（服务器端管理，明文） | ✅ |
| 993 | IMAPS | IMAP over SSL（加密接收） | ✅ |

---

## B.4 文件传输类

| 端口 | 协议 | 用途 | 需管理员绑定 |
|------|------|------|:---:|
| 20 | FTP-DATA | FTP 数据传输通道（主动模式） | ✅ |
| 21 | FTP | FTP 控制通道 | ✅ |
| 22 | SSH/SFTP | 安全 Shell 和 SFTP 文件传输 | ✅ |
| 445 | SMB | Windows 文件共享（SMB over TCP） | ✅ |
| 990 | FTPS | FTP over SSL 控制通道 | ✅ |

---

## B.5 远程访问类

| 端口 | 协议 | 用途 | 需管理员绑定 |
|------|------|------|:---:|
| 22 | SSH | Linux/macOS 远程终端管理 | ✅ |
| 23 | Telnet | 远程终端（明文，不安全，已弃用） | ✅ |
| 3389 | RDP | Windows 远程桌面 | ✅ |
| 5900 | VNC | Virtual Network Computing 远程桌面 | ❌ |

---

## B.6 其他关键协议端口

| 端口 | 协议 | 用途 | 需管理员绑定 |
|------|------|------|:---:|
| 53 | DNS | 域名解析（UDP为主，大数据包走TCP） | ✅ |
| 67 | DHCP Server | DHCP 服务器监听端口 | ✅ |
| 68 | DHCP Client | DHCP 客户端监听端口 | ✅ |
| 123 | NTP | 网络时间协议 | ✅ |
| 161 | SNMP | 简单网络管理协议 | ✅ |
| 162 | SNMP Trap | SNMP 陷阱通知 | ✅ |
| 443 | QUIC | HTTP/3 基于 UDP（与 HTTPS 共用） | ✅ |
| 1080 | SOCKS | SOCKS 代理 | ❌ |
| 3128 | Squid Proxy | Squid 缓存代理默认端口 | ❌ |
| 5432 | PostgreSQL | 同B.2数据库类，便于关联查阅 | ❌ |
| 9092 | Kafka | Apache Kafka 消息队列 | ❌ |
| 2181 | Zookeeper | Apache Zookeeper 协调服务 | ❌ |

---

## B.7 安全提示

1. **公网暴露原则**：数据库类端口（3306/5432/6379/27017）**绝不能直接暴露在公网**，必须配合防火墙和 VPN。
2. **开发环境**：8080/3000/5000 等仅用于本地开发，切勿绑定 `0.0.0.0` 到公网网卡。
3. **被占用排查**：`netstat -tunlp | grep <端口>`（Linux）/ `netstat -ano | findstr <端口>`（Win）。
4. **权限说明**：0-1023 端口需 root/管理员权限才能监听；1024+ 普通用户即可。