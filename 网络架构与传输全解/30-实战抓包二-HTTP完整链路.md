# 30 — 实战抓包（二）：HTTP 请求完整链路

## 学习目标

- 用 Wireshark 观察一次 HTTP 请求从 DNS 到挥手结束的完整时间线
- 掌握多阶段分析技巧（不同阶段用不同过滤器）
- 理解 Keep-Alive 对 TCP 连接复用的影响
- 学会用 `||` 组合过滤器同时观察多种协议

---

上一章我们只盯着 TCP 看了三握四挥。这一章放大视野——从一个 URL 输入到页面返回，中间到底发生了什么？我们按时间线步步追踪。

---

## 30.1 准备实验

### 清空 DNS 缓存

为了让 DNS 解析也在抓包中出现（而不是从缓存直接拿），先清空缓存：

```powershell
# Windows PowerShell（管理员权限）
ipconfig /flushdns
```

```bash
# macOS
sudo dscacheutil -flushcache; sudo killall -HUP mDNSResponder

# Linux
sudo systemd-resolve --flush-caches
```

### 实验步骤

1. 打开 Wireshark，**不要设捕获过滤器**（我们要抓全流程），直接双击网卡开始抓包
2. 打开浏览器，**新标签页**中输入：`http://httpbin.org/get`
3. 页面加载完成后，回到 Wireshark 点"停止"

---

## 30.2 分阶段分析——一条时间线，四个阶段

一个完整的 HTTP 请求（不带 HTTPS，纯明文），按时间线分为四个阶段：

```
[DNS 解析] → [TCP 三次握手] → [HTTP 请求/响应] → [TCP 四次挥手]
```

现在在 Wireshark 中按阶段逐个过滤分析。

---

### 阶段一：DNS 解析

**过滤器**：`dns`

你要找的是一条 DNS 查询和一条 DNS 响应。在包列表中，DNS 包默认**浅蓝色**。

查询包展开后长这样：

```
Domain Name System (query)
    Queries
        httpbin.org: type A, class IN
```

响应包展开后：

```
Domain Name System (response)
    Queries
        httpbin.org: type A, class IN
    Answers
        httpbin.org: type A, class IN, addr 54.XXX.XXX.XXX
```

解释：浏览器不知道 `httpbin.org` 的 IP 是什么，所以先问 DNS 服务器："httpbin.org 在哪？"DNS 回答："在 IP `54.XXX.XXX.XXX`。"

记住这个 IP，后面 TCP 握手就是跟这个 IP 做的。

---

### 阶段二：TCP 三次握手

**过滤器**：`tcp and ip.addr == <上一步查到的IP>`

比如 IP 是 `54.91.108.226`，就输入：

```
ip.addr == 54.91.108.226 and tcp
```

你应该看到熟悉的三个包：

```
[SYN]        →  Seq=0
[SYN, ACK]   →  Seq=0, Ack=1
[ACK]        →  Seq=1, Ack=1
```

如果包很多，用更精确的过滤器：

```
tcp.flags.syn == 1 and tcp.flags.ack == 0 and ip.addr == 54.91.108.226
```

只显示纯 SYN 包，定位三次握手的起点。

💡 **想多一点：TCP 三握中端口号说明了什么？**

客户端端口是一个**随机高端口**（如 52341），服务器端口是 **80**。Wireshark 中：
- Source Port 为 80 = 服务器发来的包
- Destination Port 为 80 = 客户端发给服务器的包

通过端口号对，你就能判断"这个包是谁发给谁的"。第 15-17 章讲 TCP 时提到过，这一步亲眼验证。

---

### 阶段三：HTTP 请求与响应

**过滤器**：`http`

现在你会看到至少两个 HTTP 包。第一个（客户端发）：

```
GET /get HTTP/1.1
Host: httpbin.org
Connection: keep-alive
User-Agent: Mozilla/5.0 ...
Accept: text/html, ...
```

第二个（服务器回）：

```
HTTP/1.1 200 OK
Date: ...
Content-Type: application/json
Content-Length: XXX

{"args": {}, "headers": { ... }, "origin": "你的IP", "url": "http://httpbin.org/get"}
```

在包细节区域，Wireshark 帮你把 HTTP 头逐行展开了，非常清晰。

---

### 阶段四：TCP 四次挥手

**过滤器**：`tcp.flags.fin == 1 and ip.addr == <IP>`

只显示所有带 FIN 标志的包：

```
ip.addr == 54.91.108.226 and tcp.flags.fin == 1
```

你应该看到 2~4 个 FIN 包。结合 29.5 节的结论判断：你看到的是 3 个还是 4 个挥手包？

---

## 30.3 Keep-Alive 的观察

如果浏览器和服务器都支持 Keep-Alive（HTTP/1.1 默认开启），连接不会立刻关闭。你可能会看到：

1. 第一个 GET 请求完成后，TCP 连接**没有立即挥手**
2. 浏览器可能复用同一个 TCP 连接发第二个请求（比如加载 favicon.ico）
3. 一段时间没有新请求后，连接才关闭

在 Wireshark 中，你可以通过**时间间隔**来判断：

- 如果 HTTP 响应后紧接着就有 FIN 包 → 没有 Keep-Alive
- 如果 HTTP 响应后秒级别没有 FIN 包 → 使用了 Keep-Alive

🎯 **验证方式**：看 HTTP 响应头中是否包含 `Connection: keep-alive`，以及响应的包序号和第一个 FIN 包的序号之间隔了多少个其他包。

---

## 30.4 多过滤器组合——用 `||` 同时看多种协议

盯着一种协议看清楚了，想同时看 DNS + TCP + HTTP 在同一视图中？

用 `||`（逻辑或）组合：

```
dns || http || (tcp.port == 80)
```

这个过滤器会同时显示 DNS 包、HTTP 包，以及所有端口 80 的 TCP 包（包括三握四挥）。

更精确的写法——只显示跟 httpbin.org 相关的东西：

```
dns.qry.name contains "httpbin.org" || http.host contains "httpbin.org" || (tcp.port == 80 and ip.addr == 54.91.108.226)
```

💡 **想多一点：用 `||` 就等于把时间线拼起来了**

分别过滤 DNS、TCP、HTTP 时，你看到的是三个独立片段。用 `||` 组合后，你看到的是按时间排列的完整故事：

```
时间 →  DNS查询 → DNS响应 → TCP SYN → TCP SYN+ACK → TCP ACK → HTTP GET → HTTP 200 OK → TCP FIN ...
```

这就是"一条 URL 的生命周期"。

---

## 30.5 DNS 包找不到？可能是 DoH

如果你清空了 DNS 缓存，但 Wireshark 中就是找不到 `dns` 包，可能原因：

1. **浏览器用了 DoH（DNS over HTTPS）**：Chrome/Firefox 默认可能启用 DoH，DNS 查询走加密 HTTPS 通道，Wireshark 中表现为普通的 TLS 流量，不会显示为 `dns` 协议
2. **DNS 被系统代理拦截**：如果你开了 VPN 或系统代理，DNS 可能被劫持走代理通道

❌ **不要以为没抓到 DNS 包就是实验失败**

✅ **应对方法**：
- 在浏览器地址栏输入 `chrome://settings/security`（Chrome）或 `about:preferences#privacy`（Firefox），关掉"使用安全 DNS"，再试一次
- 或者用命令行工具代替浏览器：`curl -v http://httpbin.org/get`，curl 默认不走 DoH，DNS 包一定能抓到
- 也可以在 Wireshark 过滤器中输入 `dns || tls`，看 TLS 流量中是否包含 DNS 服务器 IP（通常是 `8.8.8.8` 或 `1.1.1.1` 的 443 端口）

---

## 30.6 本章实战对比：HTTP vs HTTPS 链路差异

作为额外挑战，抓一次 HTTPS 请求，对比差异：

```bash
curl -v https://httpbin.org/get
```

Wireshark 过滤：`ip.addr == <IP>`

额外看到了什么？

- 三握之后多了 **TLS 握手**（Client Hello → Server Hello → Certificate → ...）
- HTTP 内容完全加密（Wireshark 中显示为 `Application Data`）
- TCP 头和 IP 头依然是明文的（源 IP、目的 IP、端口号都可见）

这说明 HTTPS = HTTP over TLS over TCP。底层 TCP 的三握四挥不变，中间插了一层 TLS 加密。

---

## 本章小结

| 你学了什么 | 具体内容 |
|-----------|---------|
| 完整 HTTP 链路 | DNS→TCP 三握→HTTP 请求/响应→TCP 四挥 |
| 分阶段过滤 | DNS 用 `dns`，TCP 用 `tcp`，HTTP 用 `http` |
| `||` 组合过滤 | `dns \|\| http \|\| (tcp.port == 80)` 同时看多协议 |
| Keep-Alive | HTTP/1.1 默认复用连接，延迟挥手 |
| DNS 包找不到 | 可能是 DoH 加密 DNS 或被代理拦截 |
| HTTP vs HTTPS | HTTPS 多了 TLS 层，TCP 部分不变 |

## 术语表（无新术语）

本章无新增术语。涉及的 DNS、TCP、HTTP、TLS 概念已在前序章节讲解。

DNS 基础见第 20 章，TCP 基础见第 15-17 章，TLS 基础见第 24 章。

## 验证方法

不看本章，独立完成以下操作即通过：

1. 清空 DNS 缓存
2. Wireshark 全量抓包，浏览器访问 `http://httpbin.org/get`
3. 用过滤器 `dns` 找到 DNS 查询和响应
4. 用过滤器 `tcp` 找到三次握手
5. 用过滤器 `http` 找到 HTTP GET 和 200 OK
6. 用 `||` 过滤器同时显示 DNS、TCP、HTTP，按时间顺序描述完整链路

---

> ⏸️ **推荐暂停点**：本章结束可暂停。下一章深入 DNS。恢复时确认：能用 `dns` 过滤器找到 DNS 查询和响应包。