# 第7章 · 域名与DNS

> "你记得住 110.242.68.66 吗？记不住吧。所以你用 www.baidu.com。但从域名到IP，中间发生了什么？"

---

## 7.1 域名是什么

### 人的名字 vs 电话号码

- 你能记住"张三"，但记不住他的电话号码：`13800138000`
- 你能记住 `www.baidu.com`，但记不住百度的IP：`110.242.68.66`

**域名就是IP地址的"人类友好版"**。

### 域名的结构

```
www.baidu.com
 │    │     │
 │    │     └── 顶级域名（TLD，Top-Level Domain）
 │    └──────── 二级域名（百度的名字）
 └───────────── 子域名（www是默认的，也可以是 mail.baidu.com）
```

从右往左读：
- `.com` = 顶级域名（商业机构）
- `baidu` = 二级域名（百度的品牌名）
- `www` = 子域名（World Wide Web，网站）

常见顶级域名：
- `.com`：商业（最通用）
- `.org`：非营利组织
- `.net`：网络服务
- `.gov`：政府
- `.edu`：教育
- `.cn`、`.jp`、`.uk`：国家/地区代码

---

## 7.2 DNS查询的完整过程

DNS = **Domain Name System** = 域名系统

当你在浏览器输入 `www.baidu.com` 并回车，DNS查询的过程是这样的：

### 第1步：查浏览器缓存

浏览器自己会缓存最近查过的DNS结果。

- Chrome：打开 `chrome://net-internals/#dns` 可以看到缓存的DNS记录
- 缓存时间由TTL（Time To Live）决定，过期了就删掉

### 第2步：查操作系统缓存 + hosts文件

浏览器没缓存？操作系统自己也有DNS缓存。

另外，操作系统还有一个**hosts文件**——你电脑上的"私人电话簿"：

```
# Linux/Mac: /etc/hosts
# Windows: C:\Windows\System32\drivers\etc\hosts

127.0.0.1       localhost
127.0.0.1       myapp.local       # 开发时常用
0.0.0.0         annoying-ad.com   # 屏蔽广告网站
```

如果你在hosts里写了 `110.242.68.66 www.baidu.com`，那么浏览器会直接跳到那个IP，不再进行后面的DNS查询。（这就是为什么hosts可以用来测新服务器——先改hosts指向新IP，看看行不行，没问题了再改正式DNS）

### 第3步：问本地DNS服务器

操作系统缓存也没有？那就去问**本地DNS服务器**（也叫递归DNS服务器）。

本地DNS服务器通常是：
- 你的路由器（`192.168.1.1`）
- 或者运营商（电信/联通）的DNS服务器
- 或者你自己设置的公共DNS（如 `8.8.8.8` Google DNS，`114.114.114.114` 国内DNS）

### 第4~7步：本地DNS去互联网上找

本地DNS服务器也不知道？它不会放弃，它会**从根服务器开始一层一层往下问**：

```
Q: www.baidu.com 的IP是什么？

第4步 → 本地DNS问根DNS服务器（.）
        根DNS: "我不知道，但 .com 的DNS服务器在xxx，你去问它"

第5步 → 本地DNS问 .com 的顶级DNS服务器
         .com DNS: "我不知道，但 baidu.com 的DNS服务器在xxx，你去问它"

第6步 → 本地DNS问 baidu.com 的权威DNS服务器
         baidu.com DNS: "www.baidu.com 的IP是 110.242.68.66"

第7步 → 本地DNS得到答案！
```

> 🤔 世界上有13台根DNS服务器（逻辑上的，物理上更多镜像）——编号从a.root-servers.net到m.root-servers.net。这些服务器几乎从来不变，所以它们的IP地址是"硬编码"在操作系统里的。

### 第8步：缓存结果

本地DNS拿到结果后，把它缓存起来。TTL（比如600秒）内再有人问同样的域名，直接返回缓存结果，不再重新查。

### 第9步：返回给浏览器

最终，本地DNS把 `110.242.68.66` 返回给浏览器。浏览器拿到IP，开始建立TCP连接。

### 全过程示意图

```
浏览器
  │
  ├─ ① 浏览器DNS缓存 → 有？直接返回
  │
  ├─ ② OS缓存 + hosts → 有？直接返回
  │
  ├─ ③ 问本地DNS (192.168.1.1 / 8.8.8.8)
  │      │
  │      ├─ ④ 问根DNS (.)
  │      │       └→ "去问 .com"
  │      ├─ ⑤ 问 .com DNS
  │      │       └→ "去问 baidu.com"
  │      ├─ ⑥ 问 baidu.com DNS
  │      │       └→ "是 110.242.68.66"
  │      ├─ ⑦ 拿到答案
  │      └─ ⑧ 缓存结果
  │
  └─ ⑨ 浏览器拿到IP → 开始TCP连接
```

---

## 7.3 hosts文件

### 位置

```
Linux/Mac:  /etc/hosts
Windows:    C:\Windows\System32\drivers\etc\hosts
```

### 格式

```
IP地址           域名1          域名2...
127.0.0.1       localhost
127.0.0.1       myapp.local    api.myapp.local
0.0.0.0         ads.example.com
```

### 用途

1. **本地开发**：把 `myapp.local` 指向 `127.0.0.1`，就能用域名访问你本机的开发服务器
2. **屏蔽网站**：把广告域名指向 `0.0.0.0`（一个不可达的地址）
3. **测试新服务器**：正式切换DNS前先用hosts测试

### 优先级

hosts的优先级**高于**DNS查询。如果hosts里有记录，就不会去问DNS。这就是为什么hosts可以用来"劫持"任何域名。

---

## 7.4 DNS记录类型

DNS不只是"域名→IP"这么简单。它支持多种记录类型：

| 记录类型 | 作用 | 例子 |
|----------|------|------|
| **A** | 域名 → IPv4 | `www.example.com → 93.184.216.34` |
| **AAAA** | 域名 → IPv6 | `www.example.com → 2606:2800:220:1:248:1893:25c8:1946` |
| **CNAME** | 域名 → 另一个域名（别名） | `www.example.com → example.com`（然后继续查example.com的A记录） |
| **MX** | 邮件服务器 | `example.com → mail.example.com (priority 10)` |
| **NS** | 指定权威DNS服务器 | `example.com → ns1.dnsprovider.net` |
| **TXT** | 任意文本 | 常用来验证域名所有权（"请加一条TXT记录来证明这个域名是你的"） |
| **SRV** | 指定服务的位置 | `_sip._tcp.example.com → sipserver.example.com:5060` |

### CNAME的注意事项

CNAME会多一次DNS查询：先查CNAME得到目标域名，再查目标域名的A记录。

如果 `www.example.com` → CNAME → `example.com` → A → `93.184.216.34`

根域名（也叫裸域名 `example.com`）**不能用CNAME**（RFC规定）。这就是为什么很多CDN服务商让你把裸域名做URL重定向到 `www`。

---

## 本章小结

- 域名 = IP地址的人类友好版
- DNS = 互联网的电话号码簿
- DNS查询走9步，从浏览器缓存到根DNS到权威DNS
- hosts文件 = 你电脑的私人DNS，优先级最高
- A记录映射域名到IP，CNAME映射域名到另一个域名

> 🚀 下一章：端口是什么？一个服务器只有1个IP，凭什么能同时跑网站、数据库、文件服务？

---
[← 上一章：06-IP地址](06-IP地址/) | [下一章：08-端口 →](08-端口/)