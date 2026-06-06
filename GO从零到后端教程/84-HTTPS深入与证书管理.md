# 第84章 · HTTPS深入与证书管理

> "第13章我们快速过了一遍HTTPS的TLS握手——现在有了加密基础（第83章），我们可以深入到TLS的每一个细节。本章的目标不是让你成为密码学专家，而是让你真正理解TLS握手过程中到底发生了什么、证书是怎么验证的、以及如何在你的Go服务上正确配置HTTPS。最后一节还会给出一个安全最佳实践清单——一份你可以在每个项目中反复对照的检查表。"

---

## 84.1 TLS握手：逐步拆解

### 先回顾：HTTPS的两阶段设计

HTTPS = HTTP over TLS。TLS（传输层安全协议，为HTTP提供加密传输，详见附录I）用两种加密实现了一个巧妙的设计：

- **非对称加密**只在握手阶段用一次——交换"会话密钥"
- **对称加密**在之后的整个会话中使用——加密实际数据流量

为什么这样设计？因为非对称加密太慢（RSA比AES慢1000倍），如果全程用非对称加密，你的网站会比乌龟还慢。但对称加密的密钥分发问题，又需要用非对称加密来解决。

这就是HTTPS的精妙之处：用慢但安全的非对称加密交换密钥，用快但需要共享密钥的对称加密传输数据。

### 完整TLS 1.3握手（12个步骤）

TLS 1.3是当前最新版本，比TLS 1.2更简洁更快。以下是完整的握手过程：

```
客户端（浏览器）                             服务器（Go服务）
    │                                              │
    │ 1. ClientHello                                │
    │    支持的TLS版本、加密套件                     │
    │    key_share（客户端公钥）                     │
    │─────────────────────────────────────────────>│
    │                                              │
    │                                   2. 选择加密套件
    │                                   3. 生成服务器密钥对
    │                                              │
    │                             4. ServerHello    │
    │                                选定的加密套件  │
    │                                key_share（服务器公钥）
    │                             5. 证书（含服务器公钥+CA签名）
    │                             6. CertificateVerify（签名验证）
    │                             7. ServerFinished   │
    │<─────────────────────────────────────────────│
    │                                              │
    │ 8. 验证证书链                                 │
    │ 9. 用双方公钥计算会话密钥                       │
    │                                              │
    │ 10. ClientFinished                            │
    │─────────────────────────────────────────────>│
    │                                              │
    │                   11. 计算会话密钥              │
    │                                              │
    │ 12. 双方切换为对称加密通信                      │
    │<═══════════ AES-GCM加密通道 ═══════════════>│
```

### 各步骤详解

**步骤1 — ClientHello：** 浏览器说"我想建立安全连接，我支持TLS 1.3和1.2，我支持这些加密套件（AES-256-GCM、ChaCha20-Poly1305等），这是我的密钥交换公钥。"

**步骤2-3 — 服务器端处理：** 服务器选择双方都支持的最高级加密套件。同时生成自己的临时密钥对（用于密钥交换）。

**步骤4 — ServerHello：** "OK，我们用TLS 1.3 + AES-256-GCM，这是我的密钥交换公钥。"

**步骤5 — 发送证书：** 服务器把自己的证书发给浏览器。证书里包含：
- 服务器域名（如 `example.com`）
- 服务器的公钥
- CA的数字签名（证明这个证书是CA签发的）

**步骤6 — CertificateVerify：** 服务器用**证书私钥**对握手消息做签名。这一步证明服务器**确实持有证书对应的私钥**——没有私钥的中间人即使拿到了证书也无法完成这一步。

**步骤7 — ServerFinished：** 服务器说"我这边握手数据发完了，你验证吧。"

**步骤8 — 浏览器验证证书链：** 浏览器做三件事：
1. 检查证书是否由信任的CA签发（浏览器内置了信任的CA根证书列表）
2. 检查证书是否在有效期内
3. 检查证书绑定的域名是否匹配当前访问的域名
4. 验证CertificateVerify中的签名——用证书中的公钥验签，确认服务器确实持有私钥

**步骤9 — 计算会话密钥：** 浏览器和服务器各自持有对方的密钥交换公钥。通过**ECDHE**（椭圆曲线Diffie-Hellman密钥交换），双方独立计算出**完全相同的会话密钥**——这个密钥从未在网络上传输过。

**步骤10 — ClientFinished：** 浏览器说"我也算好了，我用会话密钥加密一条测试消息，你能解开就对了。"

**步骤12 — 安全通道建立：** 接下来所有的HTTP数据都用AES-GCM加密。窃听者看到的是一堆乱码。

### ECDHE密钥交换的精妙之处

这是整个TLS最天才的部分。想象一下：

- Alice和Bob各有一种颜料（私钥）
- 他们各自把颜料混入一桶公共颜料（公钥），把混合后的颜色发给对方
- Alice收到Bob的混合颜料，加入自己的私钥颜料 → 得到最终颜色（会话密钥）
- Bob收到Alice的混合颜料，加入自己的私钥颜料 → 得到同样的最终颜色
- 旁观的Eve看到两种混合颜料在网络上传输，但无法从中还原出最终颜色

这就是Diffie-Hellman密钥交换的直觉理解。ECDHE是用椭圆曲线数学实现的版本——同样的原理，更短的密钥，更快的计算。

关键点：**会话密钥从未在网络上传输过。** 即使攻击者记录了所有网络数据包，也无法推导出会话密钥。

### TLS 1.3 vs TLS 1.2的改进

| | TLS 1.2 | TLS 1.3 |
|---|---------|---------|
| 握手往返 | 2次（4段） | 1次（2段） |
| 握手速度 | 慢 | 快（减少1个RTT） |
| 加密套件 | 复杂，37种 | 简化，5种 |
| 密钥交换 | RSA或ECDHE | 只支持ECDHE（前向安全） |
| 过时算法 | 支持 | 全部移除 |

TLS 1.3移除了所有不安全的算法（RSA密钥交换、CBC模式、SHA1、RC4、3DES），大幅减少了攻击面。

---

## 84.2 证书链验证过程

### 证书是什么

数字证书就像网站的**数字身份证**——由权威机构（CA）签发，证明"这个公钥确实属于 example.com"。

一个X.509证书包含：

| 字段 | 说明 |
|------|------|
| Subject | 证书持有者（域名） |
| Issuer | 签发者（CA的名称） |
| Valid From/To | 有效期 |
| Public Key | 证书对应的公钥 |
| Signature | CA对以上所有字段的数字签名 |
| SAN | 支持的域名列表（Subject Alternative Name） |

### 证书链：信任的传递

你的浏览器不可能预先信任世界上所有网站的证书。它只信任极少数的**根CA证书**（Root CA）——这些证书预装在你的操作系统或浏览器里。

证书链就是通过层层签名把信任从根CA传递到你的网站：

```
根CA证书（预装在浏览器/操作系统中）
    │
    │ 用自己的私钥签名 ↓
    │
中间CA证书（由根CA签发）
    │
    │ 用自己的私钥签名 ↓
    │
服务器证书（你的域名 example.com）
```

验证过程是自下而上的：

1. 浏览器拿到服务器证书，检查它是否由"中间CA"签发
2. 验证中间CA的签名（用中间CA的公钥）
3. 检查中间CA证书是否由"根CA"签发
4. 验证根CA的签名（用根CA的公钥——根CA**自签名**）
5. 确认根CA在浏览器信任列表中

任何一环断开，浏览器就弹出"此网站的安全证书不受信任"的警告。

### 在Go中加载证书链

```go
package main

import (
	"crypto/tls"
	"net/http"

	"github.com/gin-gonic/gin"
)

func main() {
	r := gin.Default()
	r.GET("/", func(c *gin.Context) {
		c.String(200, "Hello HTTPS")
	})

	cert, err := tls.LoadX509KeyPair("cert.pem", "key.pem")
	if err != nil {
		panic(err)
	}

	tlsConfig := &tls.Config{
		Certificates: []tls.Certificate{cert},
		MinVersion:   tls.VersionTLS13,
	}

	server := &http.Server{
		Addr:      ":443",
		Handler:   r,
		TLSConfig: tlsConfig,
	}

	server.ListenAndServeTLS("", "")
}
```

`tls.LoadX509KeyPair` 加载证书和私钥。`MinVersion: tls.VersionTLS13` 强制至少TLS 1.3——拒绝更老的、不安全的版本。

---

## 84.3 自签名证书

### 什么时候用自签名证书

- 本地开发测试
- 内网服务之间通信
- 不面向浏览器的API（如微服务之间用mTLS）

对外服务的网站**绝不能用**自签名证书——浏览器会弹出安全警告，用户无法信任。

### 使用OpenSSL生成自签名证书

```bash
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes -subj "/CN=localhost"
```

参数解释：
- `-x509`：生成自签名证书（不是证书签名请求）
- `-newkey rsa:4096`：生成新的4096位RSA密钥
- `-keyout key.pem`：私钥输出文件
- `-out cert.pem`：证书输出文件
- `-days 365`：有效期365天
- `-nodes`：不加密私钥（No DES——不带密码保护，方便自动化）
- `-subj "/CN=localhost"`：证书持有者 `localhost`

生成后得到两个文件：
- `cert.pem`：证书（公钥+域名信息+自签名）
- `key.pem`：私钥（**绝对不要提交到Git或分享**）

### 配置Go使用自签名证书

```go
func main() {
	r := gin.Default()
	r.GET("/", func(c *gin.Context) {
		c.String(200, "本地HTTPS测试")
	})
	r.RunTLS(":8443", "cert.pem", "key.pem")
}
```

访问 `https://localhost:8443`，浏览器会警告证书不安全——这是正常的，因为自签名证书不在浏览器信任列表里。点"高级→继续访问"即可。

### 生成SAN自签名证书

现代浏览器要求证书必须有SAN（Subject Alternative Name）。单用 `CN=localhost` 可能不被Chrome接受：

```bash
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes \
  -subj "/CN=localhost" \
  -addext "subjectAltName=DNS:localhost,DNS:*.localhost,IP:127.0.0.1"
```

`-addext` 添加了SAN扩展，指定了域名和IP。

---

## 84.4 Let's Encrypt免费证书

### Let's Encrypt是什么

Let's Encrypt是一个免费、自动化、开放的CA（证书颁发机构）。它由非营利组织ISRG运营（赞助商包括Google、Mozilla、Cisco等科技巨头），致力于让每个网站都能用上HTTPS。

特点：
- **完全免费**：不需要花钱买证书
- **自动化**：通过ACME协议自动续期
- **有效期90天**：短有效期迫使运维自动化（手动每90天换一次太痛苦了）
- **被所有主流浏览器信任**：Let's Encrypt的根证书预装在所有主流浏览器和操作系统中

### 使用Certbot

Certbot是Let's Encrypt官方推荐的ACME客户端工具。

**安装Certbot：**

```bash
apt install certbot    # Ubuntu/Debian
yum install certbot    # CentOS
```

**获取证书（HTTP验证方式）：**

```bash
certbot certonly --standalone -d example.com -d www.example.com
```

`--standalone` 表示Certbot自己启动一个临时HTTP服务器（占用80端口）来完成域名验证。Let's Encrypt会访问 `http://example.com/.well-known/acme-challenge/xxx` 确认你确实控制这个域名。

证书生成后存储在：
- `/etc/letsencrypt/live/example.com/fullchain.pem`（完整证书链）
- `/etc/letsencrypt/live/example.com/privkey.pem`（私钥）

**自动续期：**

```bash
certbot renew --dry-run   # 测试续期流程是否正常
certbot renew             # 实际续期
```

Certbot安装时会自动创建一个systemd timer（类似cron job），每天检查一次，在证书过期前30天自动续期。

查看定时任务：

```bash
systemctl list-timers | grep certbot
```

### Go程序中使用Let's Encrypt证书

```go
func main() {
	r := gin.Default()
	r.GET("/", func(c *gin.Context) {
		c.String(200, "Hello HTTPS with Let's Encrypt")
	})
	r.RunTLS(":443", "/etc/letsencrypt/live/example.com/fullchain.pem", "/etc/letsencrypt/live/example.com/privkey.pem")
}
```

注意用的是 `fullchain.pem` 而不是 `cert.pem`。`fullchain.pem` 包含了完整的证书链（服务器证书 + 中间CA证书），浏览器验证时需要的中间CA证书都在里面。

### Go程序自动获取Let's Encrypt证书

`golang.org/x/crypto/acme/autocert` 包可以在Go程序内自动获取和管理Let's Encrypt证书——不需要Certbot：

```go
package main

import (
	"crypto/tls"
	"net/http"
	"os"

	"golang.org/x/crypto/acme/autocert"
	"github.com/gin-gonic/gin"
)

func main() {
	r := gin.Default()
	r.GET("/", func(c *gin.Context) {
		c.String(200, "Hello Auto HTTPS")
	})

	certManager := autocert.Manager{
		Prompt:     autocert.AcceptTOS,
		HostPolicy: autocert.HostWhitelist("example.com", "www.example.com"),
		Cache:      autocert.DirCache("/var/www/.cache"),
	}

	server := &http.Server{
		Addr: ":443",
		TLSConfig: &tls.Config{
			GetCertificate: certManager.GetCertificate,
			MinVersion:     tls.VersionTLS13, // 强制至少TLS 1.3，与前面TLSConfig配置一致
		},
		Handler: r,
	}

	go http.ListenAndServe(":80", certManager.HTTPHandler(nil))

	server.ListenAndServeTLS("", "")
}
```

这比Certbot更优雅——证书管理完全集成在Go程序里。程序启动时自动检查证书，没有就申请，快过期就自动续期。80端口用来处理ACME的HTTP验证挑战。

`autocert.DirCache("/var/www/.cache")` 把证书缓存到磁盘，避免每次重启都重新申请。Let's Encrypt有速率限制（每周最多50个新证书），缓存是必须的。

---

## 84.5 Go程序配置HTTPS实战

### 使用r.RunTLS（最简单）

```go
r.RunTLS(":443", "fullchain.pem", "privkey.pem")
```

适合简单场景，缺点是配置不灵活。

### 使用http.Server + TLSConfig（推荐）

```go
tlsConfig := &tls.Config{
	MinVersion:               tls.VersionTLS13,
	CurvePreferences:         []tls.CurveID{tls.X25519, tls.CurveP256},
	PreferServerCipherSuites: true,
}

server := &http.Server{
	Addr:         ":443",
	Handler:      r,
	TLSConfig:    tlsConfig,
	ReadTimeout:  10 * time.Second,
	WriteTimeout: 10 * time.Second,
	IdleTimeout:  120 * time.Second,
}

server.ListenAndServeTLS("fullchain.pem", "privkey.pem")
```

`CurvePreferences` 指定优先使用的椭圆曲线。X25519是目前最快最安全的选项。

### HTTP自动跳转HTTPS

启动一个单独的80端口服务，把所有HTTP请求重定向到HTTPS：

```go
go func() {
	redirect := http.NewServeMux()
	redirect.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		target := "https://" + r.Host + r.URL.Path
		if r.URL.RawQuery != "" {
			target += "?" + r.URL.RawQuery
		}
		http.Redirect(w, r, target, http.StatusMovedPermanently)
	})
	http.ListenAndServe(":80", redirect)
}()
```

所有 `http://example.com/xxx` 的请求自动301重定向到 `https://example.com/xxx`。

---

## 84.6 HSTS：强制浏览器只用HTTPS

### 什么是HSTS

HSTS（HTTP Strict Transport Security）——服务器告诉浏览器："以后访问我这个域名，**只准用HTTPS**，不准用HTTP。记住这一点，记1825天。"

浏览器收到这个头后：
1. 把所有 `http://` 请求**在浏览器内部**自动升级为 `https://`（不经过网络）
2. 遇到证书错误时**不允许用户点"继续访问"**——彻底阻止中间人攻击

### 配置HSTS

```go
r.Use(func(c *gin.Context) {
	if c.Request.TLS != nil {
		c.Header("Strict-Transport-Security", "max-age=63072000; includeSubDomains; preload")
	}
	c.Next()
})
```

- `max-age=63072000`：1825天（2年）
- `includeSubDomains`：子域名也强制HTTPS
- `preload`：允许把你的域名提交到浏览器的HSTS预加载列表（Chrome/Firefox内置列表，**出厂自带HSTS**）

### ⚠️ HSTS的"不可逆"特性

一旦浏览器收到HSTS头，在 `max-age` 时间内**无法回退HTTP**。如果你的HTTPS出了问题（证书过期、配置错误），用户在有效期内**完全无法访问你的网站**——浏览器拒绝降级到HTTP。

所以部署HSTS的建议：
1. 先在测试环境验证HTTPS配置稳定
2. 先用短 `max-age`（如 3600 = 1小时）测试
3. 确认一切正常后，逐渐增加到半年、一年
4. 不要一开始就设置1825天

`preload` 尤其需要谨慎——一旦提交到浏览器预加载列表，**全世界所有Chrome/Firefox用户都永远只能通过HTTPS访问你的域名**。预加载列表的移除非常麻烦，需要数月的流程。

---

## 84.7 安全最佳实践清单

这是你在每个后端项目上线前应该对照检查的清单：

### HTTPS与TLS

- [ ] 全部流量走HTTPS，HTTP做301重定向
- [ ] TLS版本最低1.2，推荐1.3
- [ ] 使用Let's Encrypt或商业CA证书（勿用自签名证书对外服务）
- [ ] 证书自动续期已配置（Certbot cron/systemd timer 或 autocert）
- [ ] HSTS已配置（先短后长，谨慎 preload）
- [ ] 私钥文件权限 600（仅root可读写）

### 认证与授权

- [ ] 密码用bcrypt存储（cost≥10，绝不存明文）
- [ ] 登录失败返回统一模糊错误信息
- [ ] JWT密钥从环境变量读取，不硬编码
- [ ] Access Token有效期≤15分钟
- [ ] Refresh Token用HttpOnly Cookie存储
- [ ] 敏感操作（改密码、改邮箱）要求重新输入密码
- [ ] 权限校验在**后端**实现（前端权限控制只是UI优化）

### 攻击防护

- [ ] 所有SQL使用参数化查询 `?` 占位符
- [ ] 用户输入在输出到HTML时经过转义（Go模板自动做）
- [ ] Cookie设置HttpOnly + Secure + SameSite=Strict
- [ ] 上传文件验证MIME类型和扩展名
- [ ] 上传文件重命名为随机名称
- [ ] 上传文件存储在Web不可直接访问的位置
- [ ] SSRF防护：URL白名单+禁止内网IP
- [ ] 请求频率限制（Rate Limiting）

### 基础设施

- [ ] 数据库连接使用最小权限账号
- [ ] 数据库连接字符串不硬编码（环境变量）
- [ ] 所有外部请求设置超时（`http.Client{Timeout: 30s}`）
- [ ] 日志不记录密码、Token等敏感信息
- [ ] 生产环境关闭Debug模式（Gin的 `gin.SetMode(gin.ReleaseMode)`）
- [ ] 依赖定期更新（`go get -u` + 安全审计）
- [ ] 敏感配置文件（`.env`）在 `.gitignore` 中

### 持续运维

- [ ] 证书到期监控（Let's Encrypt有邮件提醒，但自己也要配置告警）
- [ ] 安全漏洞通告订阅（关注Go官方安全公告）
- [ ] 定期安全扫描（用 `gosec`、`trivy` 等工具扫描代码和镜像）
- [ ] 应急预案：证书过期、密钥泄露、数据库被删时的恢复流程

---

## 本章小结

| 知识点 | 要点 |
|--------|------|
| TLS设计 | 非对称加密交换密钥 + 对称加密传输数据 |
| TLS 1.3握手 | 1次往返（TLS 1.2需要2次），更快更安全 |
| ECDHE | 椭圆曲线密钥交换，会话密钥不在网络上传输 |
| CertificateVerify | 服务器用私钥签名，证明持有证书私钥 |
| 证书链 | 根CA→中间CA→服务器证书，信任层层传递 |
| 自签名证书 | 仅开发/内网使用，外网必须用CA证书 |
| Let's Encrypt | 免费、自动化、90天有效期、浏览器信任 |
| Certbot | Let's Encrypt官方ACME客户端 |
| autocert | Go内置ACME客户端，程序自动管理证书 |
| RunTLS | `r.RunTLS(":443", "cert.pem", "key.pem")` |
| HSTS | 强制浏览器只用HTTPS，max-age谨慎设置 |
| 安全清单 | 上线前逐项检查的防护措施列表 |

> 🚀 恭喜你完成了第五篇——认证授权与安全的全部8章！从密码哈希到JWT，从OAuth 2.0到RBAC，从SQL注入到TLS握手——你现在已经掌握了后端工程师必须理解的所有安全知识。接下来，第六篇将带你进入消息队列与异步处理的世界：为什么需要异步？RabbitMQ怎么用？Kafka为什么这么快？准备好迎接分布式系统的挑战了吗？

---
[← 上一章：83-加密基础.md](83-加密基础/) | [下一章：85-消息队列基础.md →](85-消息队列基础/)
