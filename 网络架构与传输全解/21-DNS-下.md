# 21 — DNS（下）：记录类型、CDN 调度与排错

## 学习目标
- 能说出 6 种常见 DNS 记录类型及其用途，每种能用 dig 查出来
- 理解 CNAME 为什么不能和 A 记录共存
- 知道 DNS 怎么做最简单的负载均衡（多 IP 轮询）
- 理解 CDN 为什么能给不同地区的用户返回不同 IP
- 掌握 3 种 DNS 排错工具和操作
- 了解 DNS 污染/劫持的基本概念和缓解手段

---

## 21.1 DNS 记录的"身份证"——六种常见记录类型

第 20 章我们只用了 A 记录（域名 → IPv4）和 CNAME（别名）。实际上 DNS 有几十种记录类型，就像仓库里的货物有不同的标签。我们来看最常用的六种。

先把每种记录干什么用的一句话总结放前面：

| 记录类型 | 全称 | 一句话 | 生活类比 |
|---------|------|--------|----------|
| **A** | Address | 域名 → IPv4 地址 | "张三住在 1 号楼 302" |
| **AAAA** | 四倍 A | 域名 → IPv6 地址 | "张三还住在新城区 8 栋"（新门牌体系） |
| **CNAME** | Canonical Name | 域名别名 → 真实域名 | "张三的小名叫阿三，找阿三等于找张三" |
| **MX** | Mail Exchange | 域名的邮件服务器地址 | "给张三寄信，送到 3 号邮箱" |
| **NS** | Name Server | 域名的权威 DNS 服务器 | "张三的户口本在 XX 派出所" |
| **TXT** | Text | 任意文本记录（验证、SPF） | "张三的备注：身高 180，电话 138xxxx" |

下面逐个用 `dig` 实操。Windows 用户用第 20 章教的方案（BIND Tools 或 WSL），或用 `nslookup -type=xxx` 替代。

---

### 21.1.1 A 记录：域名 → IPv4

最基础的记录，把域名映射到一个 IPv4 地址：

```bash
dig www.baidu.com A

# 输出关键行
www.baidu.com.      1200    IN    CNAME    www.a.shifen.com.
www.a.shifen.com.   300     IN    A        110.242.68.66
```

```powershell
# Windows nslookup
nslookup -type=A www.baidu.com
```

### 21.1.2 AAAA 记录：域名 → IPv6

和 A 记录一样的功能，但返回的是 IPv6 地址（128 位的"下一代门牌号"）：

```bash
dig google.com AAAA

# 典型输出
google.com.         300     IN    AAAA    2a00:1450:4009:822::200e
```

IPv6 目前还没完全普及（特别是国内），所以很多域名查不到 AAAA 记录，这是正常的。**一个域名可以同时有 A 和 AAAA 记录**——支持 IPv6 的客户端会优先用 AAAA，不支持的用 A。

### 21.1.3 CNAME：别名记录

CNAME 不直接指向 IP，而是指向**另一个域名**。意思是："我不负责解析，你去问 XXX。"

```bash
dig www.baidu.com CNAME

# 输出
www.baidu.com.      1200    IN    CNAME    www.a.shifen.com.
```

`www.baidu.com` 本身没有 A 记录——它告诉 DNS："去找 `www.a.shifen.com`，它知道我的 IP。"

---

#### ❌ 经典错误：CNAME 和 A 记录共存

很多人在配置 DNS 时会犯这个错：

```
www.example.com.    IN    CNAME    cdn-provider.example.net.
www.example.com.    IN    A        1.2.3.4
```

**这样做是无效的。** RFC 规范明确规定：**如果一个域名有 CNAME 记录，就不能同时有其他任何记录类型**（除 DNSSEC 相关记录外）。

为什么？回到 CNAME 的设计意图：**CNAME 的意思是"我的解析权已经委托给别人了，请你去问它"**。既然你说了"去问别人"，又自己给了一个 A 记录（"我也告诉你 IP"），DNS 解析器就懵了——到底听谁的？RFC 直接禁止了这种自相矛盾的配置。

用生活场景来理解：你搬家了，在旧家门口贴了张条："我搬到新地址 XXX 了，请去那里找我。" 结果你在旧家新家的地址都写上了——那邮递员到底该往哪个地址送信？

✅ **正确做法**：CNAME 指向的那个域名（`cdn-provider.example.net`）才需要配 A 记录。

### 21.1.4 MX 记录：邮件服务器

MX 记录告诉全世界：发给这个域名的邮件，应该送到哪个服务器。每个 MX 记录还带一个**优先级数字**——数字越小，优先级越高。

```bash
dig gmail.com MX

# 输出
gmail.com.          3600    IN    MX    5  gmail-smtp-in.l.google.com.
gmail.com.          3600    IN    MX    10 alt1.gmail-smtp-in.l.google.com.
gmail.com.          3600    IN    MX    20 alt2.gmail-smtp-in.l.google.com.
```

发送邮件的服务器会优先尝试优先级 5 的那台，连不上才试优先级 10 的，再连不上试 20 的。这是一种简单的**故障转移机制**。

### 21.1.5 NS 记录：权威 DNS 服务器

NS 记录告诉你：这个域名的"户口所在地"——谁持有这个域名的权威 DNS 记录。

```bash
dig baidu.com NS

# 输出
baidu.com.          172800  IN    NS    dns.baidu.com.
baidu.com.          172800  IN    NS    ns2.baidu.com.
baidu.com.          172800  IN    NS    ns3.baidu.com.
```

NS 记录是 DNS 层级结构的"铰链"——`.com` TLD 通过 NS 记录知道 `baidu.com` 的权威 DNS 是谁，才能在第 20 章的步骤⑤⑥中正确指路。

### 21.1.6 TXT 记录：万能文本记录

TXT 记录最初设计目的是存放任意文本备注，但现在最重要的用途是：

1. **SPF（Sender Policy Framework）**：声明哪些服务器有资格用这个域名发邮件（防伪造）
2. **DKIM**：邮件签名验证的公钥
3. **域名所有权验证**：申请 SSL 证书、Google Search Console 等，服务商会让你添加特定 TXT 记录来证明你拥有这个域名

```bash
dig google.com TXT

# 输出（截取）
google.com.         3600    IN    TXT    "v=spf1 include:_spf.google.com ~all"
```

这条 TXT 记录的意思是：只有 `_spf.google.com` 中列出的服务器可以用 `@google.com` 的地址发邮件。

---

## 21.2 DNS 负载均衡：最简单的"分流量"

你有没有注意过，`dig www.baidu.com` 有时返回两个不同 IP？

```
www.a.shifen.com.   300     IN    A        110.242.68.66
www.a.shifen.com.   300     IN    A        110.242.68.67
```

DNS 服务器每次返回这两个 IP 时，可以**轮换顺序**——第一次把 `110.242.68.66` 排前面，第二次把 `110.242.68.67` 排前面。大多数客户端会优先选第一个 IP 连接。结果就是：两台服务器各分到大约一半的流量。

这就是 **DNS 层面的负载均衡**——最简单、成本最低的流量分发方式。

它的优点是不需要额外设备（不需要负载均衡器），缺点也很明显：
- DNS 缓存会让负载不均（TTL 过期前，客户端一直用缓存的 IP）
- 无法感知后端服务器的真实负载（一台已经跑满了，DNS 还在给它塞流量）
- 无法做会话保持

> 真正的大规模流量调度，靠的是 **CDN 的智能 DNS 调度**，第 34 章会详细展开。

---

## 21.3 TTL：缓存多久才更新？

第 20 章多次提到 TTL，这里正式讲清楚。

**TTL（Time To Live）** 是 DNS 记录的"保质期"，单位是秒。它的值在权威 DNS 服务器上设定，意思是：

> "这条记录你可以缓存 TT L秒。过期之前，不必再来问我。"
dig www.baidu.com  # 看到 300 = 5分钟
```

每当一个 DNS 解析器（你的电脑、路由器、ISP 的 DNS）收到一条记录，它就会启动一个倒计时。TTL 到期之前，直接用缓存；到期之后，才重新去问权威 DNS。

TTL 是**速度与灵活性的权衡**：

| TTL 设置 | 好处 | 代价 |
|---------|------|------|
| **长 TTL（如 86400 = 1天）** | DNS 查询少、响应快、权威服务器压力小 | IP 变更后要等一天才能全网生效 |
| **短 TTL（如 60 = 1分钟）** | IP 变更后很快全网生效 | 查询频繁、权威服务器压力大 |

运维中最常见的教训：**切换服务器 IP 前 24 小时，先把 TTL 降到 60 秒**。等全网缓存都过期（原 TTL 时间过后），再切 IP。否则旧 IP 要等原 TTL 过期才能被全网抛弃，在此期间部分用户访问失败。

---

## 21.4 DNS 排错工具箱

DNS 出问题是运维中最常见的"灵异事件"——网站打不开，可能不是服务器挂了，而是 DNS 解析失败。以下是三个排错武器。

### 武器一：nslookup

Windows 和 Mac/Linux 都自带。最简单也最常用：

```bash
# 基础查询
nslookup www.baidu.com

# 指定 DNS 服务器
nslookup www.baidu.com 8.8.8.8

# 查特定类型
nslookup -type=MX gmail.com
```

### 武器二：清 DNS 缓存

改了 hosts、换了 DNS 服务器、域名 IP 变更后，如果新结果不生效，第一个怀疑的就是**本地 DNS 缓存还没过期**。

```powershell
# Windows
ipconfig /flushdns
ipconfig /displaydns     # 查看当前缓存内容
```

```bash
# macOS
sudo dscacheutil -flushcache && sudo killall -HUP mDNSResponder

# Linux（systemd-resolved）
sudo resolvectl flush-caches

# Linux（nscd）
sudo /etc/init.d/nscd restart
```

### 武器三：切换 DNS 服务器

有时候是你的默认 DNS（如 ISP 提供的）挂了或者被污染。手动换成公共 DNS 是最快的验证方法：

**常用的公共 DNS：**

| DNS 服务商 | 主要地址 | 备用地址 | 特点 |
|-----------|---------|---------|------|
| **Google** | `8.8.8.8` | `8.8.4.4` | 全球最快之一，支持 DoH/DoT |
| **Cloudflare** | `1.1.1.1` | `1.0.0.1` | 隐私友好，支持 DoH/DoT |
| **国内 114 DNS** | `114.114.114.114` | `114.114.115.115` | 国内节点多，延迟低 |

**怎么改 DNS：**

- **Windows**：控制面板 → 网络和共享中心 → 更改适配器设置 → 右键网卡 → 属性 → Internet 协议版本 4 (TCP/IPv4) → 属性 → 使用下面的 DNS 服务器地址
- **macOS**：系统设置 → 网络 → 高级 → DNS → 点 + 添加
- **验证修改**：`nslookup baidu.com`，看前面显示的 `Server` 是不是你刚改的地址

> 💡 **想多一点**：如果换了 `8.8.8.8` 能解析但你的默认 DNS 不能，那问题就在你的 DNS 服务器上——联系 ISP 或者直接永久切到 `8.8.8.8`。如果换了所有 DNS 都不行，那问题在你的网络本身（网线、WiFi、路由器）。

---

## 21.5 DNS 污染与劫持

### DNS 劫持（Hijacking）

你的 DNS 请求在路上被"截胡"了——返回一个不是你想要的 IP。常见形式：

- **ISP 劫持**：你访问一个不存在的域名，ISP 的 DNS 不返回"不存在"，而是返回他们自己的广告页面 IP（俗称"强插广告页"）
- **路由器劫持**：恶意软件改了你路由器的 DNS 设置，所有设备都被导向钓鱼网站

### DNS 污染（Poisoning / Spoofing）

比劫持更隐蔽。攻击者在你的 DNS 查询到达真正的 DNS 服务器之前，抢先发一个**伪造的应答**给你的 DNS 解析器。因为 UDP（DNS 主要用 UDP）是无连接的，验证只能靠端口号和事务 ID——如果攻击者猜中了这两个值，伪造的应答就会被接受。

**现象**：你 `dig www.example.com`，返回了一个莫名其妙的 IP，但 `dig @8.8.8.8 www.example.com` 又正常。说明你的默认 DNS 被污染了。

### 对策：DoH 和 DoT

传统的 DNS 查询是**明文 + UDP**，任何人都能看到你在查什么域名（隐私问题），任何人都能伪造应答（安全问题）。

两个现代解决方案：

- **DoH（DNS over HTTPS）**：DNS 查询走 HTTPS 加密通道（端口 443），从外面看和普通网页流量一模一样。无法被中间人窥探或篡改。
- **DoT（DNS over TLS）**：DNS 查询走 TLS 加密通道（专用端口 853），同样加密，但端口独立所以网络管理员可以识别并放行/阻止。

两者都能有效缓解 DNS 污染和劫持——攻击者无法解密 TLS/HTTPS 加密的 DNS 查询和应答。

主流浏览器（Chrome、Firefox、Edge）都已经内置 DoH 支持，在设置里搜 "DNS over HTTPS" 即可开启。

---

## 21.6 小结

| 概念 | 要点 |
|------|------|
| A 记录 | 域名 → IPv4，最基础的 DNS 记录 |
| AAAA 记录 | 域名 → IPv6，和 A 记录可共存 |
| CNAME | 域名别名 → 真实域名，"我不负责解析，去问别人"，**不能和其他记录共存** |
| MX 记录 | 邮件服务器地址 + 优先级，实现邮件故障转移 |
| NS 记录 | 权威 DNS 服务器地址，DNS 层级结构的"铰链" |
| TXT 记录 | 万能文本，主要用于 SPF（防伪造邮件）和域名所有权验证 |
| DNS 负载均衡 | 同一域名返回多个 IP，DNS 轮换顺序分发流量 |
| TTL | 记录保质期（秒），运维铁律：切 IP 前先降 TTL |
| DNS 劫持 | DNS 请求被截胡返回错误 IP（如 ISP 强插广告页） |
| DNS 污染 | 攻击者抢先伪造 DNS 应答，让解析器接受错误 IP |
| DoH | DNS over HTTPS，DNS 走 HTTPS 加密，防窥探和篡改 |
| DoT | DNS over TLS，DNS 走 TLS 加密，端口 853 |

---

## 术语表

| 术语 | 解释 |
|------|------|
| **A 记录（A Record）** | DNS 记录类型，将域名映射到 IPv4 地址（如 `www → 1.2.3.4`） |
| **AAAA 记录（Quad-A Record）** | DNS 记录类型，将域名映射到 IPv6 地址（如 `www → 2001:db8::1`） |
| **CNAME（Canonical Name）** | 域名别名记录，指向另一个域名而非 IP。CNAME 意思是"我不负责解析，去问别人"，因此不能和其他记录共存 |
| **MX 记录（Mail Exchange）** | 指定接收该域名邮件的服务器，带优先级数字实现故障转移 |
| **NS 记录（Name Server）** | 指定该域名的权威 DNS 服务器 |
| **TXT 记录（Text Record）** | 任意文本记录，常用于 SPF（防伪造邮件）、DKIM（邮件签名）、域名所有权验证 |
| **SPF（Sender Policy Framework）** | 通过 TXT 记录声明哪些服务器有权用该域名发邮件 |
| **TTL（Time To Live）** | DNS 记录缓存有效期（秒），过期后解析器需重新查询权威 DNS |
| **DNS 劫持（DNS Hijacking）** | 恶意拦截 DNS 请求，返回错误 IP（如 ISP 插入广告页） |
| **DNS 污染（DNS Poisoning / Spoofing）** | 攻击者抢先伪造 DNS 应答，使解析器缓存错误记录 |
| **DoH（DNS over HTTPS）** | 通过 HTTPS（端口 443）加密传输 DNS 查询，防窥探和篡改 |
| **DoT（DNS over TLS）** | 通过 TLS（端口 853）加密传输 DNS 查询，功能同 DoH 但端口独立 |

---

## 验证方法

在终端依次执行以下查询，并解释每条输出：

```bash
# 1. 查 A 记录
dig baidu.com A

# 2. 查 AAAA 记录（可能为空）
dig google.com AAAA

# 3. 查 CNAME
dig www.baidu.com CNAME

# 4. 查 MX 记录
dig qq.com MX

# 5. 查 NS 记录
dig baidu.com NS

# 6. 查 TXT 记录
dig google.com TXT
```

每一条输出能回答：
- 这条记录的类型是什么？
- 返回了什么内容？
- TTL 是多少秒？

如果你能认全这六种记录类型，说明本章目标达成。