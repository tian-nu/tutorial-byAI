# 31 — 实战抓包（三）：DNS 解析全过程

## 学习目标

- 用 `dig +trace` 追踪 DNS 从根到权威的完整解析链
- 对比 `dig` 普通解析和 `dig +trace` 迭代解析的区别
- 在 Wireshark 中观察 DNS 请求与响应的对应关系
- 理解 DNS 层级解析的每一跳

---

第 20 章讲了 DNS 层级结构和解析流程。这一章，我们用 `dig +trace` 和 Wireshark 双管齐下，亲眼看着一个域名是怎么从根 DNS 一路问到权威 DNS 的。

---

## 31.1 准备实验

### Windows 用户：安装 dig

Windows 默认没有 `dig` 命令。BIND 官方提供 Windows 版：

1. 下载 BIND：https://www.isc.org/download/
2. 安装后，把 `C:\Program Files\ISC BIND 9\bin` 加入系统 PATH
3. 重新打开 PowerShell，输入 `dig -v` 验证

或者用 WSL（Windows Subsystem for Linux），WSL 自带 `dig`。

### macOS / Linux 用户

`dig` 通常预装。如果没有：

```bash
# macOS
brew install bind

# Linux (Debian/Ubuntu)
sudo apt install dnsutils

# Linux (CentOS/RHEL)
sudo yum install bind-utils
```

### 验证

```bash
dig -v
```

输出类似 `DiG 9.x.x` 即表示可用。

---

## 31.2 dig +trace —— DNS 迭代解析实战

### 基本命令

```bash
dig +trace baidu.com
```

`+trace` 参数：告诉 `dig` 自己动手做迭代解析——从根 DNS 开始，一层一层往下问，直到拿到最终答案。这与第 20 章讲的标准 DNS 解析流程完全对应。

注意：**`dig +trace` 是从你本机直接发查询给各级 DNS 服务器，不使用系统的递归 DNS 缓存**。所以你会看到完整的解析链路。

### 解读输出

执行后，你会看到类似这样的输出（以 baidu.com 为例）：

```
; <<>> DiG 9.x.x <<>> +trace baidu.com
;; global options: +cmd

# ===== 第一跳：问根 DNS 服务器 =====
.                       518400  IN      NS      a.root-servers.net.
.                       518400  IN      NS      b.root-servers.net.
(共 13 个根服务器)
;; Received 1097 bytes from 192.168.1.1#53(192.168.1.1) in 32 ms

# ===== 第二跳：问 .com 顶级域 DNS 服务器 =====
com.                    172800  IN      NS      a.gtld-servers.net.
com.                    172800  IN      NS      b.gtld-servers.net.
(多个 .com 顶级域服务器)
;; Received 1168 bytes from 198.41.0.4#53(a.root-servers.net) in 40 ms

# ===== 第三跳：问 baidu.com 权威 DNS 服务器 =====
baidu.com.              172800  IN      NS      ns1.baidu.com.
baidu.com.              172800  IN      NS      ns2.baidu.com.
;; Received 123 bytes from 192.5.6.30#53(a.gtld-servers.net) in 120 ms

# ===== 第四跳：从权威 DNS 拿到最终答案 =====
baidu.com.              600     IN      A       110.242.68.66
baidu.com.              600     IN      A       39.156.66.10
;; Received 75 bytes from 110.242.68.134#53(ns2.baidu.com) in 28 ms
```

### 逐跳解读

| 跳 | dig 问了谁 | 谁回答的 | 回答了什么 | 对应层级 |
|----|-----------|----------|-----------|---------|
| 1 | 你的路由器/DNS | 根服务器 | `.com` 顶级域 DNS 服务器地址 | 根域 |
| 2 | 根服务器 | `.com` 顶级域服务器 | `baidu.com` 的权威 DNS 服务器地址 | 顶级域 |
| 3 | `.com` 顶级域服务器 | 权威 DNS 服务器 | `baidu.com` 的权威 DNS 服务器名单 | 权威域 |
| 4 | 权威 DNS 服务器 | 权威 DNS 服务器 | `baidu.com` → `110.242.68.66` | 最终答案 |

这就是 DNS 的树形查找过程——从根（`.`）到顶级域（`com.`）到权威域（`baidu.com.`），逐级向下，每一级只知道自己下一级在哪。

💡 **想多一点：dig +trace 和 dig 普通查询有什么区别？**

`dig baidu.com`（不加 `+trace`）：

```
baidu.com.  IN  A
baidu.com.  600  IN  A  110.242.68.66
```

它只给你**最终结果**，所有中间过程被你的递归 DNS 服务器（通常是路由器或 8.8.8.8）替你完成了。

`dig +trace baidu.com`：

给你**每一跳的中间结果**，你可以看到整个"接力问路"的过程。

这就像：
- 普通 `dig` = 你问前台"李四在哪个办公室？"前台直接告诉你房间号（因为前台已经帮你查了）
- `dig +trace` = 你问前台"1 号楼在哪？"→ 去 1 号楼问"技术部在哪？"→ 去技术部问"李四坐哪？"→ 自己一路找过去

---

## 31.3 Wireshark 中观察 DNS

### 同步抓包

**Step 1**：Wireshark 过滤器栏输入 `dns`，开始抓包

**Step 2**：终端执行：

```bash
dig +trace baidu.com
```

**Step 3**：停止 Wireshark

### 查看结果

Wireshark 中你应该看到多组 DNS 查询/响应对。注意观察以下几点：

1. **目的 IP 变化**：第一个查询发给 192.168.1.1（你的路由器），后续查询发给不同的远程 DNS 服务器（根服务器 IP → .com 服务器 IP → 权威 DNS IP）
2. **源端口**：dig 每次查询通常用不同的源端口
3. **事务 ID**：每个 DNS 包的 Transaction ID 字段——请求和响应的 ID 必须匹配，这是 DNS 用来配对问答的机制

展开任意一个 DNS 包的 Details：

```
Domain Name System (query)
    Transaction ID: 0x1234
    Flags: 0x0100 Standard query
    Questions: 1
    Queries
        baidu.com: type A, class IN
```

响应的 Details：

```
Domain Name System (response)
    Transaction ID: 0x1234    ← 匹配！
    Flags: 0x8180 Standard query response, No error
    Questions: 1
    Answers
        baidu.com: type A, class IN, addr 110.242.68.66
```

### 同一请求中的 NS 记录

在 `.com` 顶级域的响应包中，展开 Answers 区域，你会看到：

```
baidu.com.  172800  IN  NS  ns1.baidu.com.
baidu.com.  172800  IN  NS  ns2.baidu.com.

;; Additional Section:
ns1.baidu.com.  172800  IN  A  110.242.68.134
```

注意 **Additional Section（附加段）**——DNS 协议的设计很聪明：它知道你要查 `baidu.com` 的 NS，顺带把 NS 的 IP 也塞给你，省得你再发一次查询去解析 `ns1.baidu.com` 的 IP。

---

## 31.4 对比：dig baidu.com vs dig +trace baidu.com

| 维度 | dig baidu.com | dig +trace baidu.com |
|------|--------------|---------------------|
| 查询方式 | 递归（让上游 DNS 帮你完成） | 迭代（自己一层一层问） |
| 输出内容 | 只有最终 A 记录 | 每跳的 NS 记录 + 最终 A 记录 |
| 中间服务器 | 不显示 | 全部显示 |
| 网络包数量 | 2 个（一请求一响应） | 8~12 个（每跳一对） |
| 用途 | 快速查 IP | 排查 DNS 链路问题 |

---

## 31.5 常见问题

### 问题 1：Windows 下 dig 命令找不到

如果你在 Ch20 就有这个问题，回到 20.5 节，那里有详细的 Windows DNS 工具安装指引。

本章 31.1 节也给出了独立安装步骤。

### 问题 2：dig +trace 被 DNS 代理拦截

如果你用了 VPN、公司网络代理、或某些运营商 DNS，`dig +trace` 可能被拦截（返回错误或不完整）。

❌ **错误现象**：`dig +trace` 只输出了一跳（直接给了最终答案），看不到逐级过程

✅ **排查方法**：

1. 先试 `dig +trace example.com`（更简单的域名）
2. 如果还是不行，检查是否开了 VPN——关掉 VPN 再试
3. 如果还不行，强制指定根服务器：`dig +trace baidu.com @8.8.8.8`

### 问题 3：不知道每跳在干什么

回到第 20 章，理解 DNS 的根→顶级域→权威域三层结构。`dig +trace` 的输出就是这三层的一一对应。

---

## 本章小结

| 你学了什么 | 具体内容 |
|-----------|---------|
| dig +trace | 从根 DNS 开始迭代解析，逐跳输出 |
| 解析层级对应 | 根域→顶级域(.com)→权威域(baidu.com)→最终 A 记录 |
| Wireshark DNS 包 | Transaction ID 配对、NS 记录、Additional Section |
| dig 对比 | 普通查询=递归一次返回，+trace=迭代逐跳返回 |
| 常见坑点 | Win 无 dig、代理拦截 +trace |

## 术语表（无新术语）

本章无新增术语。DNS 相关概念（递归/迭代、根域/顶级域/权威域、A 记录、NS 记录）已在第 20 章讲解。本章是对 DNS 解析流程的**实操验证**。

## 验证方法

不看本章，独立完成以下操作即通过：

1. 打开 Wireshark，过滤 `dns`，开始抓包
2. 终端执行 `dig +trace baidu.com`
3. 解释 `dig +trace` 输出中每一跳的作用（问的是谁？答的是什么？对应 DNS 哪一层？）
4. 在 Wireshark 中找到至少两组 DNS 查询/响应对，确认 Transaction ID 匹配
5. 找出至少一个包含 Additional Section 的 DNS 响应包

---

> ⏸️ **推荐暂停点**：本章结束可暂停，三大实战抓包完成。恢复时下一章进入网络故障排查方法论——从理论到实战的切换点。