# 第07章 · 域名与DNS

> "你能记住 `192.168.1.100`，但你能记住 `142.250.80.46` 吗？域名就是给IP地址起一个好记的名字——就像你手机通讯录里给号码备注了'妈妈'。"

## 07.1 域名是什么

**域名（Domain Name）** 是IP地址的人类可读版本。

| IP地址 | 域名 |
|--------|------|
| 142.250.80.46 | google.com |
| 13.107.42.14 | bing.com |
| 你的服务器IP | your-company.com |

域名是分级的，从右往左读：

```
www.example.com
│   │       │
│   │       └── 顶级域名（TLD）：com, org, cn, io...
│   └────────── 二级域名：你在域名商那里注册的名字
└────────────── 子域名：www, api, mail, blog...
```

常见域名结构：

```
api.your-company.com    → 后端API服务器
www.your-company.com    → 前端网站
admin.your-company.com  → 管理后台
mail.your-company.com   → 邮件服务器
```

## 07.2 DNS：互联网的电话簿

**DNS（Domain Name System，域名系统）** 是一个全球分布的"电话簿"——你告诉它域名，它告诉你IP地址。

```
你输入: www.example.com
DNS返回: 93.184.216.34
```

### DNS查询的完整过程

```
浏览器 → ① 先看浏览器缓存（最近访问过的）
       → ② 再看本机hosts文件（C:\Windows\System32\drivers\etc\hosts）
       → ③ 问本地DNS服务器（通常是路由器或电信的DNS）
       → ④ 本地DNS去问根DNS服务器："com在哪查？"
       → ⑤ 根DNS回答："去问 .com 的顶级DNS"
       → ⑥ 本地DNS去问 .com 顶级DNS："example.com在哪查？"
       → ⑦ .com 顶级DNS回答："去问 ns1.example.com（权威DNS）"
       → ⑧ 本地DNS去问权威DNS："www.example.com的IP是多少？"
       → ⑨ 权威DNS回答："93.184.216.34"
       → ⑩ 本地DNS把结果缓存起来，返回给浏览器
```

这个过程看起来很长，但因为有层层缓存，通常几十毫秒就完成了。

> 🤔 想多一点：你买的域名是在域名商（如阿里云、GoDaddy）那里配置的。你在域名商后台添加一条"A记录"：`api → 你的服务器公网IP`。这条记录会同步到权威DNS服务器。全世界任何人访问 `api.your-domain.com` 时，DNS最终都会指向你的服务器。**所以如果网站突然访问不了，先检查DNS解析是否正常：`nslookup your-domain.com`。**

## 07.3 Java InetAddress.getByName() 演示

Java可以直接用 `InetAddress` 做DNS解析：

```java
import java.net.InetAddress;

public class DNSDemo {
    public static void main(String[] args) throws Exception {
        // DNS解析：域名 → IP
        InetAddress addr = InetAddress.getByName("www.example.com");

        System.out.println("主机名: " + addr.getHostName());
        System.out.println("规范主机名: " + addr.getCanonicalHostName());
        System.out.println("IP地址: " + addr.getHostAddress());

        // 一个域名可能对应多个IP（负载均衡）
        InetAddress[] all = InetAddress.getAllByName("www.google.com");
        System.out.println("\nwww.google.com 的所有IP:");
        for (InetAddress a : all) {
            System.out.println("  " + a.getHostAddress());
        }
    }
}
```

输出示例：

```
主机名: www.example.com
规范主机名: www.example.com
IP地址: 93.184.216.34

www.google.com 的所有IP:
  142.250.80.46
  2404:6800:4005:802::2004
```

### 实际应用场景

```java
// Spring Boot应用中，检查远程服务是否可达
public boolean isServiceReachable(String hostname, int timeoutMs) {
    try {
        InetAddress addr = InetAddress.getByName(hostname);
        return addr.isReachable(timeoutMs);
    } catch (Exception e) {
        return false;
    }
}

// 使用
boolean ok = isServiceReachable("db.internal.company.com", 3000);
if (!ok) {
    log.warn("数据库服务器不可达，请检查DNS或网络");
}
```

## 07.4 hosts文件：本地DNS

在DNS系统出现之前，互联网靠一个叫 `hosts` 的文件来维护域名→IP的映射。这个文件至今还存在：

**Windows:** `C:\Windows\System32\drivers\etc\hosts`

**Linux/macOS:** `/etc/hosts`

内容：

```
127.0.0.1       localhost
192.168.1.100   my-dev-server.local
```

你可以在开发时把测试域名指向本地：

```
127.0.0.1       api.myapp.local
```

然后在浏览器访问 `http://api.myapp.local:8080`——它会解析到 `127.0.0.1`（你的本机）。这在本地开发时非常方便，不用记IP。

> ⚠️ hosts文件的优先级高于DNS。如果你在hosts里写了 `127.0.0.1 www.baidu.com`，那你访问百度就会指向你自己的电脑。某些恶意软件会修改hosts文件劫持流量。

---

## 本章小结

| 学了什么 | 一句话说明 |
|----------|-----------|
| 域名 | IP地址的人类可读别名，分级结构 |
| DNS | 全球分布式"电话簿"，域名→IP的查询系统 |
| DNS查询链路 | 浏览器缓存→hosts→本地DNS→根→顶级→权威 |
| Java DNS解析 | InetAddress.getByName() 执行DNS查询 |
| hosts文件 | 本地域名映射，优先级高于DNS |

## 自测题

1. 在浏览器输入 `www.example.com` 后，在TCP连接建立之前，必须先完成什么步骤？这个步骤由哪个系统完成？

2. 你买了一台阿里云服务器，公网IP是 `47.xx.xx.xx`。你想让 `api.myapp.com` 指向它，应该在域名商后台添加什么记录？

3. 下面哪种情况会导致 `InetAddress.getByName("api.internal.com")` 抛出 `UnknownHostException`？
   - A. 目标服务器关机了
   - B. DNS服务器暂时不可达
   - C. 目标服务器的8080端口没开
   - D. 你本地的防火墙拦截了