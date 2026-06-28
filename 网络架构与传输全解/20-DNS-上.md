# 20 — DNS（上）：域名怎么变成 IP

## 学习目标
- 能画出 DNS 递归解析的完整 8 步流程，讲清每一步在做什么
- 能区分递归查询和迭代查询，并举例说明
- 能用 `dig` 命令追踪域名解析的完整路径（Windows 用户也能用替代方案）
- 知道 hosts 文件在操作系统中哪个位置，以及它的优先级
- 理解 DNS 缓存的作用和潜在陷阱

---

## 20.1 一个你每天都在用但不太注意的翻译官

打开浏览器，地址栏敲 `baidu.com`，回车。零点几秒后，页面出来了。

你有没有想过一个问题：**电脑是怎么从 "baidu.com" 这串字母，找到百度那台服务器的？**

答案是——有一台巨型"翻译机"在帮你做这件事。这台翻译机就是 **DNS（Domain Name System，域名系统）**。它能做的其实就一件事，但你每天都在用：

> **把人类能记住的域名（www.baidu.com），翻译成机器需要的 IP 地址（110.242.68.66）。**

你可以把 DNS 想象成一个**全球分布式电话簿**：你要找"张三"，但电话系统只能按电话号码（IP）接通。DNS 就是那个帮你查"张三的电话号码是多少"的查询台。

那它到底是怎么查的？没有 DNS 的时候，人们又是怎么上网的？

---

## 20.2 DNS 出现之前：hosts 文件

在 DNS 诞生之前（1983 年以前），互联网上只有几百台主机。ARPANET 时代的做法非常朴素：**每台机器上存一个文件，里面记着所有主机的名字和 IP 对照表**。

这个文件叫 **hosts**，至今还在你的电脑里。

### hosts 文件位置

| 操作系统 | hosts 文件路径 |
|---------|---------------|
| **Windows** | `C:\Windows\System32\drivers\etc\hosts` |
| **macOS / Linux** | `/etc/hosts` |

打开看看你会发现长这样：

```
127.0.0.1       localhost
::1             localhost
```

每一行就是一条"域名 → IP"的映射。你可以自己在后面加一行：

```
192.168.1.100   my-test-server.local
```

保存后，你在浏览器里访问 `my-test-server.local`，电脑就会直接连到 `192.168.1.100`，**完全不走 DNS**。

hosts 文件的优先级极高——操作系统在查 DNS 之前，**会先查 hosts 文件**。这个特性也是一把双刃剑：

- ✅ 好处：开发测试时可以本地劫持域名、屏蔽广告域名（把广告域名指向 127.0.0.1）
- ❌ 坏处：恶意软件会篡改 hosts 文件，把银行域名指向钓鱼网站

但 hosts 文件有个致命缺陷：互联网上的主机从几百台增长到几亿台，你不可能在每个电脑上维护一份几亿行的 hosts 文件。于是 DNS 应运而生——把这份"全球电话簿"放在专门的服务器上，谁需要就来查。

---

## 20.3 DNS 的 8 步解析流程

你打开浏览器输入 `www.baidu.com` 之后，背后到底发生了什么？我们一步步来。

先上总览图，然后逐帧解读：

```
浏览器/你的电脑         本地DNS服务器      根DNS        .com TLD       baidu.com权威DNS
    │                       │               │              │                │
    │ ①查本地缓存           │               │              │                │
    │ (hosts+DNS缓存)       │               │              │                │
    │                       │               │              │                │
    │────②请求解析──────→   │               │              │                │
    │    www.baidu.com      │               │              │                │
    │                       │               │              │                │
    │                       │ ③问根：       │              │                │
    │                       │ ".com归谁管？" │              │                │
    │                       │──────────────→│              │                │
    │                       │               │              │                │
    │                       │ ④根回复：      │              │                │
    │                       │ ".com TLD地址" │              │                │
    │                       │←──────────────│              │                │
    │                       │               │              │                │
    │                       │ ⑤问.com TLD：               │                │
    │                       │ "baidu.com归谁管？"          │                │
    │                       │─────────────────────────────→│                │
    │                       │                              │                │
    │                       │ ⑥.com TLD回复：              │                │
    │                       │ "baidu.com权威DNS地址"       │                │
    │                       │←─────────────────────────────│                │
    │                       │                              │                │
    │                       │ ⑦问baidu.com权威DNS：                        │
    │                       │ "www.baidu.com的IP是啥？"                    │
    │                       │─────────────────────────────────────────────→│
    │                       │                                              │
    │                       │ ⑧权威DNS回复：                                │
    │                       │ "www.baidu.com → 110.242.68.66"              │
    │                       │←─────────────────────────────────────────────│
    │                       │                                              │
    │←──⑧返回结果+缓存─────│                                              │
    │                       │                                              │
```

### 第 ① 步：本地缓存先查

操作系统的 DNS 解析器会按以下优先级查询：

1. **浏览器 DNS 缓存**（Chrome 有自己独立的 DNS 缓存，地址栏输入 `chrome://net-internals/#dns` 可以看）
2. **操作系统 DNS 缓存**
3. **hosts 文件**

如果这三层都没有找到 `www.baidu.com` 的记录，进入下一步。

### 第 ② 步：问本地 DNS 服务器

操作系统把查询请求发给**本地 DNS 服务器**（也叫"递归解析器"，Recursive Resolver）。这个地址通常由 DHCP 自动分配——连 WiFi 时，路由器会自动告诉你"DNS 服务器在哪"。

你的本地 DNS 服务器可能是：
- 家里的路由器（最常见，路由器会再转发给 ISP 的 DNS）
- ISP（电信/联通/移动）的 DNS 服务器
- 你自己手动设置的一个公共 DNS（比如 8.8.8.8 或 114.114.114.114）

本地 DNS 收到请求后，它也没有现成答案（假设是第一次查）。接下来，它会**替你去跑腿**——这就进入了最精彩的部分。

### 第 ③~⑧ 步：本地 DNS 的"跑腿之旅"

#### ③ 问根域名服务器："`.com` 归谁管？"

全世界有 13 组根域名服务器（从 a.root-servers.net 到 m.root-servers.net），它们不存具体域名的 IP，只存**顶级域名（TLD）服务器的地址**。

本地 DNS 问根服务器："请告诉我 `.com` 的 DNS 服务器在哪？"

> **根服务器只有 13 组，不是 13 台。** 每组背后是有几百台物理服务器的任播（Anycast）集群，全球分布。

#### ④ 根服务器回复

根服务器回复一堆 `.com` TLD 服务器的地址。根服务器说："我不认识 `www.baidu.com` 是谁，但我知道 `.com` 的 DNS 服务器在哪，你去问它们。"

#### ⑤ 问 .com TLD 服务器："`baidu.com` 归谁管？"

本地 DNS 拿到 `.com` TLD 地址后，去问："`baidu.com` 这个域名的权威 DNS 在哪？"

#### ⑥ .com TLD 回复

`.com` TLD 服务器回复："`baidu.com` 的权威 DNS 是 `dns.baidu.com` 和 `ns2.baidu.com`，地址分别是 xxx。"

#### ⑦ 问 baidu.com 的权威 DNS："`www.baidu.com` 的 IP？"

本地 DNS 终于找到了能拍板的——**权威 DNS 服务器**。权威 DNS 存着 `baidu.com` 域下所有子域名的真实记录，它说了算。

#### ⑧ 权威 DNS 回复 + 缓存

权威 DNS 查自己的记录："`www.baidu.com` 的 A 记录是 `110.242.68.66`（也可能是动态变化的）"，把结果返回。

本地 DNS 收到结果后，**缓存起来**（缓存多久取决于 TTL），然后返回给你的电脑。你的电脑也会缓存一份。

---

## 20.4 递归查询 vs 迭代查询

上面那 8 步中，DNS 的查询方式分两种：

| 类型 | 英文 | 含义 | 谁干活？ |
|------|------|------|----------|
| **递归查询** | Recursive Query | "你替我去查，给我最终结果" | 服务器替你跑腿 |
| **迭代查询** | Iterative Query | "我不认识，但我告诉你下一步该问谁" | 服务器指路，你自己跑 |

用图书馆找书打比方：

- **递归**：你问图书管理员"《TCP/IP 详解》在哪？"管理员说"你等着"，然后自己去书库、去别的分馆找，5 分钟后回来把书递给你。你只发了一次请求，得到了最终结果。
- **迭代**：你问管理员，管理员说"计算机类在 3 楼"。你自己去 3 楼，又问另一个管理员，他说"网络类在 3 楼 C 区"。你自己去 C 区，又问管理员……你跑了好几趟才找到书。

在上面的 8 步流程中：
- **你的电脑 → 本地 DNS 服务器**：递归查询（本地 DNS 替你跑腿）
- **本地 DNS → 根/TLD/权威**：迭代查询（每步只告诉下一步问谁）

这样设计是有道理的：让本地 DNS（服务器）去做繁重的迭代查询工作，你的电脑只发起一次请求就拿到结果。否则你的电脑得自己从根问到权威，比别人慢好几倍。

> 💡 **想多一点**：如果你用 `dig +trace` 命令，dig 会模拟迭代查询的过程——从根开始，一步一问，直到查出最终答案。你此时充当的就是那个"本地 DNS 服务器"的角色。后面 20.6 节会实操。

---

## 20.5 实操准备：Windows 用户怎么用 dig

`dig`（Domain Information Groper）是 DNS 排错的神器，但**Windows 默认不带**。你有三个选择：

### 方案 A：安装 BIND Tools（推荐，最快）

1. 去 [ISC BIND 下载页](https://www.isc.org/download/) 下载 Windows 版 BIND
2. 安装后，把 BIND 的 `bin` 目录（通常是 `C:\Program Files\ISC BIND 9\bin`）加入系统环境变量 PATH
3. 重新打开终端，输入 `dig -v` 验证

### 方案 B：使用 WSL（Windows Subsystem for Linux）

如果你已经装了 WSL（Ubuntu 等），直接在 WSL 终端里用 `dig`：

```powershell
# PowerShell 中进入 WSL
wsl
# 装 dig（Ubuntu/Debian）
sudo apt update && sudo apt install dnsutils -y
# 验证
dig -v
```

### 方案 C：用 nslookup 替代（功能有限但够用）

Windows 自带 `nslookup`，虽然功能不如 `dig` 丰富，但基本查询够用：

```powershell
nslookup www.baidu.com
```

本章的命令示例以 `dig` 为主，Windows 用户用方案 A 或 B 后跟上即可。如果实在不想装，每个示例后面我会给出 nslookup 的等效命令。

---

## 20.6 dig 命令实操：追踪 DNS 解析

### 基础查询

```bash
# 查 www.baidu.com 的 A 记录
dig www.baidu.com

# Windows nslookup 等效
nslookup www.baidu.com
```

输出会很长，我们只看关键部分：

```
;; ANSWER SECTION:
www.baidu.com.      1200    IN    CNAME    www.a.shifen.com.
www.a.shifen.com.   300     IN    A        110.242.68.66
www.a.shifen.com.   300     IN    A        110.242.68.67
```

解读：
- `www.baidu.com` 其实是个 **CNAME**（别名），它指向了 `www.a.shifen.com`
- `www.a.shifen.com` 有两个 A 记录（返回了两个 IP），这就是最简单的 DNS 负载均衡——轮询返回不同 IP
- `1200` 和 `300` 是 **TTL**（秒），表示这条记录能缓存多久

### 用 +trace 追踪完整解析路径

这是 `dig` 最酷的功能——让你亲眼看到迭代查询的每一步：

```bash
dig +trace www.baidu.com
```

输出类似：

```
; <<>> DiG 9.x <<>> +trace www.baidu.com
;; global options: +cmd
.           518400  IN    NS    a.root-servers.net.
.           518400  IN    NS    b.root-servers.net.
;; Received 525 bytes from 127.0.0.1#53(127.0.0.1) in 0 ms

com.        172800  IN    NS    a.gtld-servers.net.
com.        172800  IN    NS    b.gtld-servers.net.
;; Received 1172 bytes from 198.41.0.4#53(a.root-servers.net) in 28 ms

baidu.com.  172800  IN    NS    dns.baidu.com.
baidu.com.  172800  IN    NS    ns2.baidu.com.
;; Received 237 bytes from 192.5.6.30#53(a.gtld-servers.net) in 156 ms

www.baidu.com.  1200  IN    CNAME  www.a.shifen.com.
;; Received 72 bytes from 110.242.68.134#53(dns.baidu.com) in 8 ms
```

一眼就能看到查询的完整路径：**根（.）→ .com TLD → baidu.com 权威 DNS → 最终答案**。

### 指定 DNS 服务器查询

有时候你需要绕过本地 DNS，直接问某个知名公共 DNS：

```bash
# 用 Google 的 DNS 8.8.8.8 查询
dig @8.8.8.8 www.baidu.com

# 用 Cloudflare 的 DNS 1.1.1.1 查询
dig @1.1.1.1 www.baidu.com

# 用国内 114 DNS 查询
dig @114.114.114.114 www.baidu.com

# Windows nslookup 等效
nslookup www.baidu.com 8.8.8.8
```

这个操作非常有用——当你的默认 DNS 出问题时，可以换个 DNS 验证是不是 DNS 服务器本身的问题。

---

## 20.7 常见误解与纠正

❌ **以为 DNS 只有迭代查询。** 实际上客户端到本地 DNS 是递归查询（替我跑腿），本地 DNS 到外部才是迭代查询（逐级问）。

❌ **以为改了 hosts 文件立刻生效。** 浏览器和操作系统都有 DNS 缓存，修改 hosts 后需要刷新缓存。

```bash
# 查看 DNS 缓存（macOS）
sudo dscacheutil -cachedump -entries host

# 刷新 DNS 缓存
# macOS
sudo dscacheutil -flushcache && sudo killall -HUP mDNSResponder

# Windows
ipconfig /flushdns

# Linux（取决于使用的 DNS 服务）
sudo systemd-resolve --flush-caches
# 或
sudo resolvectl flush-caches
```

❌ **以为 `dig +trace` 显示的是递归查询。** `+trace` 模拟的是迭代查询——从根开始一步步往下问。真正的递归查询是你不加参数直接用 `dig` 时，DNS 服务器替你做了 `+trace` 的工作。

---

## 20.8 小结

| 概念 | 要点 |
|------|------|
| DNS 是什么 | 域名系统，把人能记的域名翻译成机器需要的 IP（全球分布式电话簿） |
| hosts 文件 | DNS 之前的解决方案，每台机器本地存一份域名→IP 映射表，优先级高于 DNS |
| 8 步解析 | ①查本地缓存 → ②问本地DNS → ③问根 → ④根返回TLD → ⑤问TLD → ⑥TLD返回权威 → ⑦问权威 → ⑧权威返回IP+缓存 |
| 递归查询 | "你替我去查，给我最终结果"，客户端 → 本地DNS 用递归 |
| 迭代查询 | "我不认识，你去问 XXX"，本地DNS → 根/TLD/权威 用迭代 |
| 根服务器 | 13 组（非 13 台），只存 TLD 服务器地址，不存具体域名 |
| TLD | 顶级域名服务器，如 .com、.org、.cn 的 DNS |
| 权威 DNS | 域名的"最终权威"，存着该域名下所有记录的真实数据 |
| TTL | Time To Live，DNS 记录可被缓存的最长时间（秒） |
| dig | DNS 排错神器，`+trace` 追踪迭代路径，`@` 指定 DNS 服务器 |

---

## 术语表

| 术语 | 解释 |
|------|------|
| **DNS（Domain Name System）** | 域名系统，互联网的"电话簿"，负责域名和 IP 地址的相互映射 |
| **hosts 文件** | 操作系统本地的域名→IP 静态映射文件，DNS 出现之前的解析方案，优先级高于 DNS |
| **本地 DNS 服务器（Recursive Resolver）** | 接收客户端请求并负责完成完整解析的 DNS 服务器，通常由 ISP 或路由器提供 |
| **根域名服务器（Root Server）** | DNS 层级的最顶端，全球 13 组，只存 TLD 服务器地址 |
| **TLD（Top-Level Domain）** | 顶级域名，如 .com、.org、.net、.cn |
| **权威 DNS（Authoritative DNS）** | 特定域名的"官方"DNS 服务器，存有该域名的真实记录 |
| **递归查询（Recursive Query）** | DNS 查询方式之一：要求服务器替你完成全部查询，返回最终结果 |
| **迭代查询（Iterative Query）** | DNS 查询方式之一：服务器只返回下一步该问谁，不替你跑腿 |
| **A 记录（A Record）** | DNS 记录类型，域名 → IPv4 地址 |
| **CNAME（Canonical Name）** | DNS 记录类型，域名别名，指向另一个域名 |
| **TTL（Time To Live）** | 记录生存时间（秒），决定 DNS 缓存能保留多久 |
| **dig（Domain Information Groper）** | DNS 诊断命令行工具，功能远比 nslookup 强大 |

---

## 验证方法

在终端执行以下命令并口头解释每一步输出：

```bash
dig +trace www.baidu.com
```

对于输出的每一段，回答：
1. 这一步问的是谁？（根/TLD/权威）
2. 回复里给了什么信息？
3. 整个过程是递归还是迭代？

如果你能清楚解释这三个问题，说明本章目标达成。