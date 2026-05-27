# 第79章 · JWT认证

> "如果你去参加一场演唱会，检票口的工作人员怎么知道你的票是真的？票上有主办方的防伪水印和签名——工作人员看一眼就知道：'嗯，这票是我们印的，没被篡改，座位号是A区3排5座。'他不需要打电话回总部查数据库。JWT（JSON Web Token，自包含的令牌认证方案，详见附录I）就是这个思路：服务器签发的Token自带防伪签名，拿到Token的任何人都能验证它的真伪，不需要查任何中央存储。"

---

## 79.1 JWT是什么：签名防伪的门票

### Session vs JWT的核心区别

| | Session | JWT |
|---|---------|-----|
| 状态存储 | 服务器端（内存/Redis） | 客户端（Token本身） |
| 每次请求 | 查Redis/内存 → 获取用户信息 | 验证签名 → 直接从Token读取信息 |
| 扩展性 | 需要Redis集中存储 | Token自包含，天然分布式友好 |
| 主动失效 | 删Redis记录即可 | 麻烦（Token签发后独立存在） |
| 数据大小 | Cookie只存ID（几字节） | Token本身可能几百字节 |

### 一句话理解JWT

> JWT是一段经过数字签名的JSON数据。签名保证了两件事：1）这段数据**确实是我签发的**（认证）；2）这段数据**没有被篡改过**（完整性）。

任何拿到JWT的人都能验证签名，但**只有持有密钥的服务器**才能签发新Token。

---

## 79.2 JWT的结构：Header.Payload.Signature

一个完整的JWT长这样（三段Base64用点号连接）：

```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI0MiIsInVzZXJuYW1lIjoi5byg5LiJIiwiZXhwIjoxNzE1MDAwMDAwfQ.5mJpOYe_ABCDEFGHIJKLMNOPQRSTUVWXYZ123456
```

用点号拆成三段，分别做Base64解码：

### 第一段：Header（头部）

```json
{
  "alg": "HS256",
  "typ": "JWT"
}
```

Header只做两件事：
- `alg`：声明签名算法（HS256=HMAC-SHA256，RS256=RSA-SHA256）
- `typ`：声明这是JWT

### 第二段：Payload（载荷）

```json
{
  "sub": "42",
  "username": "张三",
  "iat": 1714900000,
  "exp": 1715000000
}
```

Payload是Token的"内容"，JWT标准定义了七个可选字段（称为Registered Claims）：

| 字段 | 全称 | 含义 |
|------|------|------|
| `iss` | Issuer | 签发者 |
| `sub` | Subject | 主题（通常是用户ID） |
| `aud` | Audience | 接收方 |
| `exp` | Expiration Time | 过期时间（Unix时间戳） |
| `nbf` | Not Before | 在此之前不可用 |
| `iat` | Issued At | 签发时间 |
| `jti` | JWT ID | Token的唯一标识 |

除此之外，你可以加任何自定义字段：`username`、`role`、`email`……

### 第三段：Signature（签名）

签名的计算方式：

```
Signature = HMAC-SHA256(
    base64UrlEncode(header) + "." + base64UrlEncode(payload),
    secret
)
```

用人话说：把前两段的Base64用点号拼起来，用密钥做HMAC-SHA256哈希。

**任何人拿到Token都可以把前两段解码来看**（Base64不是加密！），但没人能伪造第三段——因为签名的计算需要密钥，而密钥只有你的服务器知道。

### 重要提醒：Payload不是加密的！

很多人误以为JWT是加密的。**它不是！** Base64只是一种编码方式，不是加密。任何人拿到Token后，把中间那段Base64解码就能看到全部内容。

```
原始Token：eyJ...（Base64）
解码中间段 → {"sub":"42","username":"张三",...}
```

所以**绝对不能把密码、身份证号等敏感信息放进JWT的Payload**。JWT的作用是防篡改，不是防偷窥。想防偷窥需要用JWE（JSON Web Encryption），但那已经超出了本书的范围——99%的场景你只需要JWT就够了，敏感数据从数据库查。

---

## 79.3 生成JWT

### 安装golang-jwt

```bash
go get github.com/golang-jwt/jwt/v5
```

### 签发Token

```go
package main

import (
	"fmt"
	"time"

	"github.com/golang-jwt/jwt/v5"
)

var jwtSecret = []byte("my-256-bit-secret-key-that-nobody-knows")

type MyClaims struct {
	UserID   int64  `json:"user_id"`
	Username string `json:"username"`
	jwt.RegisteredClaims
}

func GenerateToken(userID int64, username string) (string, error) {
	claims := MyClaims{
		UserID:   userID,
		Username: username,
		RegisteredClaims: jwt.RegisteredClaims{
			Issuer:    "my-app",
			Subject:   fmt.Sprintf("%d", userID),
			ExpiresAt: jwt.NewNumericDate(time.Now().Add(15 * time.Minute)),
			IssuedAt:  jwt.NewNumericDate(time.Now()),
		},
	}

	token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)
	return token.SignedString(jwtSecret)
}
```

使用示例：

```go
token, err := GenerateToken(42, "张三")
fmt.Println(token)
```

输出是一长串Base64字符串。

### 几个要点

**密钥长度**：HS256需要至少256位（32字节）的密钥。如果你用短密钥如 `"secret"`，签名安全性极差——攻击者可以暴力破解你的密钥。

生成安全的随机密钥：

```go
package main

import (
	"crypto/rand"
	"encoding/hex"
	"fmt"
)

func main() {
	b := make([]byte, 32)
	rand.Read(b)
	fmt.Println(hex.EncodeToString(b))
}
```

把输出的64位十六进制字符串作为密钥存到环境变量或配置文件里，**千万不要硬编码在代码中然后提交到Git**。

**过期时间**：`ExpiresAt` 是Unix时间戳。`jwt.NewNumericDate()` 帮你转换Go的 `time.Time` 到JWT需要的格式。

---

## 79.4 验证JWT

```go
func ParseToken(tokenString string) (*MyClaims, error) {
	token, err := jwt.ParseWithClaims(tokenString, &MyClaims{}, func(token *jwt.Token) (interface{}, error) {
		if _, ok := token.Method.(*jwt.SigningMethodHMAC); !ok {
			return nil, fmt.Errorf("非预期的签名方法: %v", token.Header["alg"])
		}
		return jwtSecret, nil
	})

	if err != nil {
		return nil, err
	}

	claims, ok := token.Claims.(*MyClaims)
	if ok && token.Valid {
		return claims, nil
	}

	return nil, fmt.Errorf("无效的Token")
}
```

`jwt.ParseWithClaims` 做了三件事：

1. **验签**：用密钥重新计算签名，和Token中的签名对比——不匹配说明Token被篡改
2. **过期检查**：检查 `ExpiresAt` 是否已过
3. **算法验证**：确认签名算法是你期望的（防算法降级攻击）

如果其中任何一步失败，返回error。

### 算法混淆攻击

假设你的密钥长度是HS256标准的，但你允许Token指定 `"alg":"HS256"` 或 `"alg":"none"`。攻击者可以签发一个 `"alg":"none"` 的Token——无需签名就能通过验证。

这就是为什么在回调函数里要检查签名方法：

```go
func(token *jwt.Token) (interface{}, error) {
    if _, ok := token.Method.(*jwt.SigningMethodHMAC); !ok {
        return nil, fmt.Errorf("非预期的签名方法")
    }
    return jwtSecret, nil
}
```

只接受你明确使用的签名方法，拒绝一切"意外"的算法声明。

---

## 79.5 Access Token + Refresh Token：双Token机制

### 为什么需要双Token？

如果你只用一个Token，面临一个两难：

| Token有效期 | 问题 |
|------------|------|
| 很短（5分钟） | 用户每5分钟就要重新登录，体验极差 |
| 很长（30天） | Token一旦被盗，攻击者有30天时间作恶 |

双Token机制用一个巧妙的设计同时解决了这两个问题：

- **Access Token（AT）**：短期有效（15分钟），每次API请求都带
- **Refresh Token（RT）**：长期有效（7天），只用于换新AT

```
┌─────────┐                         ┌──────────┐
│  客户端   │                         │  服务器   │
└────┬────┘                         └────┬─────┘
     │  1. 登录                          │
     │──────────────────────────────────>│
     │  2. 返回 AT(15分钟) + RT(7天)      │
     │<──────────────────────────────────│
     │                                    │
     │  3. 请求API（带AT）                │
     │──────────────────────────────────>│
     │  4. AT有效 → 正常响应              │
     │<──────────────────────────────────│
     │                                    │
     │  ... 20分钟后 ...                  │
     │                                    │
     │  5. 请求API（带AT）                │
     │──────────────────────────────────>│
     │  6. AT过期 → 401                   │
     │<──────────────────────────────────│
     │                                    │
     │  7. 用RT换新AT                     │
     │──────────────────────────────────>│
     │  8. 返回新AT + 新RT                │
     │<──────────────────────────────────│
     │                                    │
     │  9. 用新AT重新请求API              │
     │──────────────────────────────────>│
     │  10. 正常响应                       │
     │<──────────────────────────────────│
```

**核心思想：**
- AT天天在外面跑（每次请求都发），风险高，所以有效期短
- RT大部分时间躺在客户端本地，只在AT过期时才用一次，风险低，所以有效期长
- 即使AT被盗，攻击者也只有15分钟窗口期

### RefreshToken的存储

RT长期有效，比AT更敏感。**RT绝对不能存在localStorage**——任何JS能读到的存储都是XSS的猎物。推荐方案：

- **HttpOnly Cookie**：RT存在Cookie里，设置 `HttpOnly=true, Secure=true, SameSite=Strict, Path=/api/auth/refresh`。JS读不到，只在刷新Token的特定路径才发送

### 完整实现

```go
func GenerateAccessToken(userID int64, username string) (string, error) {
	claims := MyClaims{
		UserID:   userID,
		Username: username,
		RegisteredClaims: jwt.RegisteredClaims{
			Issuer:    "my-app",
			Subject:   fmt.Sprintf("%d", userID),
			ExpiresAt: jwt.NewNumericDate(time.Now().Add(15 * time.Minute)),
			IssuedAt:  jwt.NewNumericDate(time.Now()),
		},
	}
	token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)
	return token.SignedString(jwtSecret)
}

func GenerateRefreshToken(userID int64, username string) (string, error) {
	claims := MyClaims{
		UserID:   userID,
		Username: username,
		RegisteredClaims: jwt.RegisteredClaims{
			Subject:   fmt.Sprintf("%d", userID),
			ExpiresAt: jwt.NewNumericDate(time.Now().Add(7 * 24 * time.Hour)),
			IssuedAt:  jwt.NewNumericDate(time.Now()),
			ID:        generateTokenID(),
		},
	}
	token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)
	return token.SignedString(jwtRefreshSecret)
}

func RefreshAccessToken(c *gin.Context) {
	var req struct {
		RefreshToken string `json:"refresh_token" binding:"required"`
	}
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(400, gin.H{"msg": "参数错误"})
		return
	}

	claims, err := ParseToken(req.RefreshToken)
	if err != nil {
		c.JSON(401, gin.H{"msg": "RefreshToken无效或已过期，请重新登录"})
		return
	}

	userID, _ := strconv.ParseInt(claims.Subject, 10, 64)

	newAT, _ := GenerateAccessToken(userID, claims.Username)
	newRT, _ := GenerateRefreshToken(userID, claims.Username)

	c.JSON(200, gin.H{
		"access_token":  newAT,
		"refresh_token": newRT,
	})
}
```

**Refresh Token Rotation（刷新轮转）**：每次用RT换新AT时，也返回一个新RT，旧RT作废。如果攻击者偷到了一个RT，正当用户用RT刷新时旧RT就失效了——攻击者的偷来的RT也同时失效。

---

## 79.6 JWT的优缺点

### 优点

**无状态（Stateless）**：服务器不需要存储任何Session数据，从Token本身就能验证身份。

**分布式天然友好**：不管你有多少台服务器，只要它们共享同一个密钥，任何一台都能独立验证Token。不需要Redis集中存储。

**跨域方便**：Token可以放在HTTP头里（`Authorization: Bearer <token>`），不受Cookie的Same-Origin限制。微服务之间传Token验证身份也特别方便。

**信息自包含**：Token里可以放一些基本信息（用户名、角色），减少数据库查询。

### 缺点

**无法主动失效（最大的坑）**：Token一旦签发，在过期之前就是一张"有效门票"。你不能像删Redis记录那样"撤销"一个JWT。

- 用户修改密码后，旧Token仍然有效（直到过期）
- 管理员封禁用户后，用户的Token仍然有效
- 用户登出后，Token仍然有效

**变通方案**：
1. Token黑名单：维护一个Redis集合，存已失效的TokenID。每次验证时先查黑名单——但这又回到了有状态（违背了JWT的初衷）
2. 短有效期：AT 15分钟过期，最多15分钟的"失效延迟"
3. 版本号：用户表加一个 `token_version` 字段，修改密码时递增。Token的Payload里也带版本号，验证时对比

**Payload明文**：任何人都能看到Token内容。不能存敏感数据。

**体积大**：一个JWT通常300-600字节，Session只有几十字节的Cookie。每次请求多传几百字节，对于高并发API是额外开销。

**密钥管理**：如果密钥泄露，攻击者可以签发任意Token。必须安全保管密钥，定期轮换。

### 什么时候用JWT？什么时候用Session？

| 场景 | 推荐方案 | 原因 |
|------|---------|------|
| 单页面应用（SPA）前后端分离 | JWT | 跨域方便，前后端独立部署 |
| 移动App API | JWT | 移动端没有Cookie概念，Token放Header最自然 |
| 微服务间通信 | JWT | 服务间传递身份信息，不依赖中心存储 |
| 传统服务端渲染网站 | Session | Cookie天然支持，有Redis集中存储 |
| 需要即时失效的能力 | Session + JWT短AT | Session可即时删除，或用极短AT降低延迟 |
| 高安全要求（如银行） | Session | 更严格的控制能力 |

---

## 79.7 Gin JWT中间件完整实现

### 中间件代码

```go
package middleware

import (
	"net/http"
	"strings"

	"github.com/gin-gonic/gin"
	"github.com/golang-jwt/jwt/v5"
)

func JWTAuth(secret []byte) gin.HandlerFunc {
	return func(c *gin.Context) {
		authHeader := c.GetHeader("Authorization")
		if authHeader == "" {
			c.JSON(http.StatusUnauthorized, gin.H{
				"code": 401,
				"msg":  "缺少Authorization头",
			})
			c.Abort()
			return
		}

		parts := strings.SplitN(authHeader, " ", 2)
		if len(parts) != 2 || strings.ToLower(parts[0]) != "bearer" {
			c.JSON(http.StatusUnauthorized, gin.H{
				"code": 401,
				"msg":  "Authorization格式错误，应为: Bearer <token>",
			})
			c.Abort()
			return
		}

		tokenString := parts[1]

		token, err := jwt.ParseWithClaims(tokenString, &MyClaims{}, func(token *jwt.Token) (interface{}, error) {
			if _, ok := token.Method.(*jwt.SigningMethodHMAC); !ok {
				return nil, jwt.ErrSignatureInvalid
			}
			return secret, nil
		})

		if err != nil || !token.Valid {
			c.JSON(http.StatusUnauthorized, gin.H{
				"code": 401,
				"msg":  "Token无效或已过期",
			})
			c.Abort()
			return
		}

		claims, ok := token.Claims.(*MyClaims)
		if !ok {
			c.JSON(http.StatusUnauthorized, gin.H{
				"code": 401,
				"msg":  "Token解析失败",
			})
			c.Abort()
			return
		}

		c.Set("user_id", claims.UserID)
		c.Set("username", claims.Username)

		c.Next()
	}
}
```

### 路由使用

```go
func SetupRoutes(r *gin.Engine) {
	api := r.Group("/api/v1")

	api.POST("/login", handler.Login)
	api.POST("/register", handler.Register)
	api.POST("/refresh", handler.RefreshAccessToken)

	authorized := api.Group("")
	authorized.Use(middleware.JWTAuth(jwtSecret))
	{
		authorized.GET("/profile", handler.GetProfile)
		authorized.POST("/articles", handler.CreateArticle)
		authorized.PUT("/articles/:id", handler.UpdateArticle)
		authorized.DELETE("/articles/:id", handler.DeleteArticle)
	}
}
```

`c.Abort()` 阻止后续Handler执行。`c.Set("user_id", ...)` 把解析出的用户信息注入到上下文，后续Handler通过 `c.Get("user_id")` 直接获取。

---

## 79.8 Token存储：localStorage vs Cookie

### localStorage方案

```javascript
localStorage.setItem("access_token", token);
```

```
优点：简单，不受Cookie限制，跨域时自动携带不干扰
缺点：任何JS都能读到 → XSS攻击可以偷Token
```

localStorage里的Token对XSS**完全不设防**。一旦页面被注入脚本，攻击者一行代码就能拿到Token并通过API冒充用户。

### HttpOnly Cookie方案

```go
c.SetCookie("access_token", token, 900, "/", "", true, true)
```

```
优点：JS不可读，XSS攻击偷不到Token
缺点：受同源策略限制，跨域麻烦；CSRF攻击可能利用
```

**推荐的安全组合**：

| Token | 存储方式 | 原因 |
|-------|---------|------|
| Access Token（15分钟） | 内存变量（React state/Vue data） | 刷新就丢，有效期短风险可控 |
| Refresh Token（7天） | HttpOnly Cookie（Secure+SameSite Strict） | 长期存储，必须防XSS |

Access Token存在内存里，页面刷新就需要用Refresh Token换新的——这里有一个自然的"冷启动"流程：刷新页面 → cookie里没有AT → 自动调 `/refresh` 用RT换新AT → 把新AT放回内存。

还有一个高级方案：**BFF（Backend For Frontend）模式**。Token完全不暴露给浏览器——前端和BFF之间用Session Cookie，BFF和API之间用JWT。浏览器永远看不到Token。

### 🤔 想多一点

JWT在业界有很多争论。有人说JWT解决了Session的问题但引入了更大的问题。这些争论的有道理，但JWT依然是现代API认证的事实标准。

关键不是选JWT还是Session，而是理解各自的trade-off，根据场景做正确选择。用JWT的话，记住三条铁律：

1. **AT有效期要短**（15分钟），RT用HttpOnly Cookie存
2. **密钥不要硬编码**，从环境变量/配置中心读取
3. **Payload不放敏感数据**，JWT不是加密的

---

## 本章小结

| 知识点 | 要点 |
|--------|------|
| JWT是什么 | 签名防伪的自包含Token，三段Base64 |
| Header | 声明算法（HS256/RS256） |
| Payload | 存放Claims（sub/exp/iat等），**不加密** |
| Signature | 前两段+密钥的HMAC，防篡改 |
| 生成 | `jwt.NewWithClaims` + `SignedString` |
| 验证 | `jwt.ParseWithClaims`：验签+过期检查+算法检查 |
| 算法混淆攻击 | 回调中检查 `token.Method`，拒绝非预期算法 |
| Access Token（AT） | 短期(15分钟)，每次请求使用 |
| Refresh Token（RT） | 长期(7天)，只用于换新AT |
| RT Rotation | 每次刷新返回新RT，旧RT作废 |
| JWT优点 | 无状态、分布式友好、跨域方便 |
| JWT缺点 | 无法主动失效、Payload明文、体积大 |
| 主动失效方案 | 黑名单 / 短有效期 / 版本号 |
| JWT中间件 | 从Authorization头提取Token→解析→注入上下文 |
| Token存储 | AT→内存，RT→HttpOnly Cookie |
| BFF模式 | 浏览器用Session Cookie，BFF转发JWT |

> 🚀 下一章：第80章 · OAuth 2.0。JWT帮我们把用户身份验证搞定了，但如果你的产品想让用户"用GitHub登录"或"用微信登录"呢？你不能让用户把GitHub密码交给你吧？OAuth 2.0就是解决"在不交出密码的情况下，让第三方应用获得有限权限"的协议。它就像你给朋友一把只能开次卧的钥匙，而不是家里的大门密码。

---
[← 上一章：78-Session认证](78-Session认证.md) | [下一章：80-OAuth 2.0 →](80-OAuth 2.0.md)
