# 93-HTTPS与证书管理

> 💡 你在嘈杂的菜市场大声告诉朋友你的银行卡密码。旁边所有人都听到了——这就是 HTTP。你改用了两台对讲机，信号加密，只有你俩能听懂——这就是 HTTPS。HTTPS 不只是 HTTP + 一把锁，它是一个精密的信任链条：证书、CA、签名、TLS 握手。本章让你彻底搞懂"浏览器地址栏那把锁"到底是怎么工作的。

---

## 本章目标
- 理解 HTTPS 的核心原理：TLS 握手
- 搞懂证书链和 CA 的信任模型
- 用 keytool 生成自签名证书
- 在 Spring Boot 中启用 HTTPS
- 了解 Let's Encrypt 免费证书的获取方式

---

## 93.1 HTTP 的问题——三大威胁

| 威胁 | HTTP 表现 | HTTPS 解决 |
|------|-----------|------------|
| **窃听** | 明文传输，任何人可以抓包看内容 | 加密通信，抓包看到的是乱码 |
| **篡改** | 中间人可以修改请求/响应内容 | 完整性校验，篡改会被发现 |
| **冒充** | 任何人都可以声称是 `google.com` | 证书验证，冒充会被浏览器警告 |

---

## 93.2 HTTPS = HTTP + TLS

HTTPS 不是一种新协议，而是在 HTTP 和 TCP 之间插了一层 TLS：

```
HTTP 层      ──┐
                ├── 应用数据
TLS 层         │    ├── 握手协议（建立安全连接）
                │    └── 记录协议（加密传输数据）
TCP 层      ──┘
```

---

## 93.3 TLS 握手——4 步建立安全连接

```
客户端（浏览器）                                    服务器（nginx/Spring Boot）

① ClientHello ─────────────────────────────────→
   "我能支持 TLS 1.3 + AES-GCM + ECDHE 密钥交换"
   + 客户端随机数 (client_random)

                                                 ② ServerHello ←──────────────────────────
                                                     "我们用 TLS 1.3 + AES-GCM"
                                                     + 服务器随机数 (server_random)
                                                     + 服务器证书（含公钥）

③ 验证证书：                                         ④ ServerHelloDone ←───────────────────
   - 证书是否在有效期内？
   - 证书的域名是否匹配？                               
   - CA 签名是否有效？
   通过 → 生成 Premaster Secret
   用服务器公钥加密 Premaster Secret
   → ClientKeyExchange ─────────────────────────→

                                                    ⑤ 双方用 client_random + server_random
                                                        + premaster_secret 算出 Session Key

⑥ 算出相同的 Session Key

⑦ Finished (加密) ──────────────────────────────→
                                                 ⑧ Finished (加密) ←───────────────────────

⑨ 后续全部数据用 Session Key 对称加密传输
```

> 🤔 想多一点：握手的前几步是明文传输的（ClientHello、ServerHello、证书），所以抓包能看到你访问了哪个域名（SNI 字段暴露域名）。但如果用 ECH（Encrypted ClientHello），连域名都能加密，中间人完全不知道你在访问哪个网站。

---

## 93.4 证书是什么？CA 是什么？

### 证书包含

```
证书 = {
    拥有者：example.com
    公钥：-----BEGIN PUBLIC KEY-----
          MIIBIjANBgkqh...
          -----END PUBLIC KEY-----
    有效期：2025-01-01 到 2026-01-01
    签发者：DigiCert Inc
    签发者签名：0xABCD...（CA 用自己的私钥对以上内容做的签名）
}
```

### CA（Certificate Authority）的信任链

```
根 CA（操作系统/浏览器内置信任）
  │  例：DigiCert Global Root CA
  │  自签名证书，私钥离线保管
  ▼
中间 CA
  │  例：DigiCert TLS RSA SHA256 2020 CA1
  │  由根 CA 签名，用于日常签发
  ▼
网站证书（你买的）
    例：*.example.com
    由中间 CA 签名
```

浏览器验证逻辑：
1. 看网站证书的签发者 → 中间 CA
2. 看中间 CA 的签发者 → 根 CA
3. 根 CA 在浏览器内置信任列表里 → 信任整条链
4. 如果任何一环缺失或失效 → 显示"不安全"警告

---

## 93.5 生成自签名证书（开发用）

```bash
keytool -genkeypair \
  -alias tomcat \
  -keyalg RSA \
  -keysize 2048 \
  -keystore keystore.p12 \
  -storetype PKCS12 \
  -validity 365 \
  -storepass your_password \
  -dname "CN=localhost, OU=Dev, O=MyCompany, L=Beijing, ST=Beijing, C=CN" \
  -ext "SAN=dns:localhost,ip:127.0.0.1"
```

- `-storetype PKCS12`：PKCS12 是标准格式，推荐
- `-dname`：`CN=localhost` 是最关键的字段，必须和访问的域名匹配
- `-ext SAN`：Subject Alternative Name，现代浏览器必须检查此项

---

## 93.6 Spring Boot 启用 HTTPS

### 方式一：application.yml 配置

```yaml
server:
  port: 8443
  ssl:
    key-store: classpath:keystore.p12
    key-store-password: your_password
    key-store-type: PKCS12
    key-alias: tomcat
```

将 `keystore.p12` 放在 `src/main/resources/` 下。启动后访问 `https://localhost:8443`。

### 方式二：同时支持 HTTP 和 HTTPS

```java
@Configuration
public class HttpsConfig {

    @Bean
    public ServletWebServerFactory servletContainer() {
        TomcatServletWebServerFactory tomcat = new TomcatServletWebServerFactory();
        tomcat.addAdditionalTomcatConnectors(httpConnector());
        return tomcat;
    }

    private Connector httpConnector() {
        Connector connector = new Connector(TomcatServletWebServerFactory.DEFAULT_PROTOCOL);
        connector.setScheme("http");
        connector.setPort(8080);
        connector.setSecure(false);
        connector.setRedirectPort(8443);  // HTTP 请求自动重定向到 HTTPS
        return connector;
    }
}
```

### 方式三：HTTP 自动跳转 HTTPS

```java
@Bean
public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
    http
        .requiresChannel(channel -> channel
            .anyRequest().requiresSecure());  // 强制所有请求走 HTTPS
    return http.build();
}
```

---

## 93.7 生产环境证书：Let's Encrypt

Let's Encrypt 提供免费 DV（域名验证）证书，有效期 90 天，需自动续期。

### 获取流程（使用 Certbot）

```bash
# 安装 certbot（Ubuntu/Debian）
sudo apt install certbot

# 获取证书（standalone 模式，certbot 会临时启动一个 Web 服务器）
sudo certbot certonly --standalone -d example.com -d www.example.com

# 证书文件位置
# /etc/letsencrypt/live/example.com/fullchain.pem   → 完整证书链
# /etc/letsencrypt/live/example.com/privkey.pem     → 私钥

# 自动续期
sudo certbot renew --dry-run  # 先测试
# 添加 crontab: 0 3 * * * certbot renew --quiet
```

### Spring Boot 使用 Let's Encrypt 证书

PKCS12 格式转换：

```bash
openssl pkcs12 -export \
  -in /etc/letsencrypt/live/example.com/fullchain.pem \
  -inkey /etc/letsencrypt/live/example.com/privkey.pem \
  -out keystore.p12 \
  -name tomcat \
  -password pass:your_password
```

---

## 93.8 常见问题

### 问题一：浏览器显示"您的连接不是私密连接"

| 原因 | 解决 |
|------|------|
| 自签名证书 | 浏览器不信任自签名，点"高级 → 继续访问"（仅开发） |
| 证书域名不匹配 | 确保 CN 或 SAN 包含你访问的域名 |
| 证书过期 | 检查 `-validity`，续期 |
| 使用了 IP 而非域名 | 自签名证书的 SAN 要包含 IP：`-ext "SAN=ip:192.168.1.100"` |

### 问题二：Spring Boot 启动报 `No private key`

通常是 `-storetype PKCS12` 和 `key-store-type: PKCS12` 不匹配，或者密码错误。

---

## 93.9 小结

| 知识点 | 核心内容 |
|--------|----------|
| HTTPS = HTTP + TLS | TLS 在 TCP 之上加密 |
| TLS 握手 | 4 步：协商算法 → 发证书 → 交换密钥 → 确认 |
| 证书链 | 根 CA → 中间 CA → 网站证书 |
| keytool | 生成自签名证书，开发用 |
| Let's Encrypt | 免费 DV 证书，90 天自动续期 |
| Spring Boot 配置 | `server.ssl.*` 几行配置即可 |

---

## 93.10 自测题

**1. 以下关于 HTTPS 的描述，哪一项是错误的？**

A. HTTPS 可以防止数据被窃听  
B. HTTPS 可以防止中间人篡改数据  
C. HTTPS 可以隐藏你访问的域名  
D. HTTPS 需要通过 CA 证书来验证服务器身份  

**2. 你用 keytool 生成了自签名证书，浏览器访问 `https://localhost:8443` 时仍然提示不安全，为什么？怎么让浏览器信任？**

**3. `server.ssl.key-store` 和 `server.ssl.key-alias` 分别指什么？**

---

**答案提示**：1→C。TLS 握手的 SNI（Server Name Indication）字段是明文传输的，中间人可以看到你访问的域名。隐藏域名需要 ECH（Encrypted ClientHello）。2→因为自签名证书不在浏览器内置的信任 CA 列表中。开发时可以点"高级 → 继续访问"，生产必须用 CA 签发的证书。3→`key-store` 是存放私钥和证书的密钥库文件路径；`key-alias` 是密钥库中该条目的别名（一个密钥库可以存多个密钥对）。下一章——消息队列基础。