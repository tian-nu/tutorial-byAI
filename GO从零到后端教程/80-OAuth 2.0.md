# 第80章 · OAuth 2.0

> "你的用户想用GitHub账号登录你的网站，你怎么做？最蠢的办法是让用户把他的GitHub用户名和密码给你——但这意味着：1）用户凭什么信任你？2）你能用他的密码做任何事，包括删他的仓库。OAuth 2.0（开放授权协议，让用户在不交出密码的前提下授予第三方有限访问权限，详见附录I）就是来解决这个问题的：用户不用交出密码，而是通过一个授权流程，给你一张'只能做特定事情'的Token。就像你给邻居一把只能开次卧的门禁卡，而不是把家里钥匙给了他。"

---

## 80.1 OAuth 2.0的本质：委托授权

### 一个贯穿始终的比喻

你要出门旅游一周，想把猫交给邻居照顾。有三种方案：

**方案A（密码共享）**：把家里钥匙的密码告诉邻居。
- 邻居能进任何房间、翻任何抽屉、用你的电脑
- 你完全信任邻居，但万一他不可靠呢？

**方案B（OAuth 2.0）**：给邻居一把**只能开客厅门的临时门禁卡**。
- 邻居只能进客厅（喂猫），进不了卧室和书房
- 门禁卡7天后自动失效
- 你可以随时在门禁系统里注销这张卡
- 邻居不需要知道你家大门密码

这就是OAuth 2.0的精髓：**在不共享密码的前提下，授予第三方有限、可控、可撤销的访问权限。**

### OAuth 2.0 vs 普通登录

很多人以为OAuth 2.0就是"用第三方账号登录"。这是误解。

| | 普通登录（身份认证） | OAuth 2.0（委托授权） |
|---|---|---|
| 核心问题 | 你是谁？ | 你能代表用户做什么？ |
| 类比 | 出示身份证 | 拿到一张授权书 |
| 产物 | 身份信息 | 访问Token（有权限范围） |
| 例子 | 输入密码登录 | 允许APP访问你的Google相册 |

实际上，OAuth 2.0的原始设计目标是**授权**而不是**认证**。但因为它顺手能拿到用户信息（通过返回的用户ID），所以也被广泛用于"第三方登录"。严格来说，用于登录的是**OpenID Connect**——基于OAuth 2.0之上的一个身份认证层。但在日常开发中，用OAuth 2.0做登录基本够用。

---

## 80.2 四个核心角色

```
┌──────────────┐     ┌──────────────────┐
│ Resource     │     │ Authorization    │
│ Owner        │     │ Server           │
│ (用户/资源   │     │ (授权服务器)       │
│  拥有者)     │     │ 如GitHub的授权页   │
└──────┬───────┘     └────────┬─────────┘
       │                      │
       │  用户点"授权"         │
       │─────────────────────>│
       │                      │
       │  返回授权码          │
       │<─────────────────────│
       │                      │
       │   把授权码交给Client  │
       └──────────────────────│
                              │
┌──────────────┐     ┌───────┴─────────┐
│ Client       │     │ Resource        │
│ (第三方应用)  │     │ Server          │
│ 你的网站      │     │ (资源服务器)      │
└──────────────┘     │ 如GitHub的API    │
                     └──────────────────┘
```

**Resource Owner（资源拥有者）**：用户本人。他的数据（GitHub仓库、Google相册）被存在某个平台上。

**Client（客户端）**：你的应用——想要访问用户数据的第三方。比如你做的博客平台，想让用户授权你用GitHub的头像和用户名。

**Authorization Server（授权服务器）**：负责认证用户身份、展示授权页面、签发Token的服务器。比如 `github.com/login/oauth/authorize`。

**Resource Server（资源服务器）**：存放用户数据的服务器。拿到Token后访问的API，比如 `api.github.com/user`。

在实际部署中，授权服务器和资源服务器可以是同一台（比如它们都是GitHub的），也可以是分开的。

---

## 80.3 授权码模式（Authorization Code Grant）

这是OAuth 2.0中**最安全、最常用**的模式。任何服务端应用（有后端服务器的）都应该用这种模式。

### 为什么需要授权码？

为什么不能直接把Token发给前端？因为**Token不能经过浏览器**。

假设授权服务器把Access Token放在URL重定向回你的网站：
```
https://yourapp.com/callback?access_token=abc123
```

这个Token会出现在：
- 浏览器地址栏（旁边的人可以看到）
- 浏览器历史记录（之后可以翻出来）
- HTTP Referer头（如果页面里有其他链接，Token会泄露给第三方）
- 各种日志系统

授权码模式多了一步：浏览器拿到的只是一个**一次性的授权码**（authorization code），这个码本身没有权限。你的**后端服务器**拿授权码去换Token——Token从始至终不经过浏览器，只在服务器之间传输。

### 完整流程图解

```
浏览器                           你的后端               GitHub(授权服务器)
  │                                │                        │
  │  1. 用户点"GitHub登录"          │                        │
  │──────────────────────────────>│                        │
  │                                │                        │
  │  2. 302 重定向到GitHub          │                        │
  │<──────────────────────────────│                        │
  │                                │                        │
  │  3. GET /authorize?            │                        │
  │     client_id=xxx              │                        │
  │     redirect_uri=callback      │                        │
  │──────────────────────────────────────────────────────>│
  │                                │                        │
  │  4. GitHub显示授权页            │                        │
  │   "xxx App 想要访问你的：       │                        │
  │    ✅ 公开信息                  │                        │
  │    ✅ 邮箱地址"                 │                        │
  │<──────────────────────────────────────────────────────│
  │                                │                        │
  │  5. 用户点击"授权"              │                        │
  │──────────────────────────────────────────────────────>│
  │                                │                        │
  │  6. 302 重定向回你的网站        │                        │
  │     /callback?code=AUTH_CODE   │                        │
  │<──────────────────────────────────────────────────────│
  │                                │                        │
  │  7. 把code传给后端              │                        │
  │──────────────────────────────>│                        │
  │                                │                        │
  │                                │  8. POST /token        │
  │                                │     code=AUTH_CODE     │
  │                                │     client_secret=xxx  │
  │                                │────────────────────>│  │
  │                                │                        │
  │                                │  9. 返回 access_token  │
  │                                │<────────────────────│  │
  │                                │                        │
  │                                │ 10. 用token调GitHub API│
  │                                │    GET /user            │
  │                                │────────────────────>│  │
  │                                │                        │
  │                                │ 11. 返回用户信息        │
  │                                │<────────────────────│  │
  │                                │                        │
  │  12. 返回登录成功               │                        │
  │<──────────────────────────────│                        │
```

### 第一步：构造授权请求

```go
func GitHubLogin(c *gin.Context) {
	authURL := "https://github.com/login/oauth/authorize"
	params := url.Values{
		"client_id":    {os.Getenv("GITHUB_CLIENT_ID")},
		"redirect_uri": {"https://yourapp.com/api/v1/oauth/github/callback"},
		"scope":        {"user:email"},
		"state":        {generateState()},
	}
	redirectURL := authURL + "?" + params.Encode()
	c.Redirect(http.StatusFound, redirectURL)
}
```

URL参数说明：

| 参数 | 含义 |
|------|------|
| `client_id` | 你的应用在GitHub注册后获得的ID（公开的，不是密码） |
| `redirect_uri` | 用户授权后跳回的地址，必须和注册时一致 |
| `scope` | 你请求的权限范围（`user:email` = 读用户邮箱） |
| `state` | 防CSRF的随机字符串 |

**state参数的重要性**：

如果没有state，攻击者可以这样操作：
1. 攻击者用自己的GitHub账号走完OAuth流程，获得一个自己的授权码
2. 攻击者诱导受害者点击 `https://yourapp.com/callback?code=攻击者的授权码`
3. 受害者"登录"到了**攻击者的GitHub账号**，之后受害者的所有操作都在攻击者账号下

有了state：你在第一步生成随机state → 存到Cookie或Session → GitHub在回调时原样返回 → 对比state是否一致。攻击者不知道你生成的state，无法伪造回调URL。

```go
func generateState() string {
	b := make([]byte, 32)
	rand.Read(b)
	return hex.EncodeToString(b)
}
```

### 第二步：处理回调，用code换Token

```go
func GitHubCallback(c *gin.Context) {
	code := c.Query("code")
	state := c.Query("state")

	expectedState, _ := c.Cookie("oauth_state")
	if state != expectedState {
		c.JSON(http.StatusBadRequest, gin.H{"msg": "state不匹配，可能是CSRF攻击"})
		return
	}

	token, err := exchangeCodeForToken(code)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"msg": "换取Token失败"})
		return
	}

	userInfo, err := fetchGitHubUser(token)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"msg": "获取用户信息失败"})
		return
	}

	localUser := findOrCreateUser(userInfo)
	jwtToken, _ := GenerateAccessToken(localUser.ID, localUser.Username)

	c.JSON(http.StatusOK, gin.H{
		"access_token": jwtToken,
		"user":         localUser,
	})
}
```

### 第三步：服务端换取Token

```go
func exchangeCodeForToken(code string) (string, error) {
	data := url.Values{
		"client_id":     {os.Getenv("GITHUB_CLIENT_ID")},
		"client_secret": {os.Getenv("GITHUB_CLIENT_SECRET")},
		"code":          {code},
		"redirect_uri":  {"https://yourapp.com/api/v1/oauth/github/callback"},
	}

	resp, err := http.PostForm("https://github.com/login/oauth/access_token", data)
	if err != nil {
		return "", err
	}
	defer resp.Body.Close()

	body, _ := io.ReadAll(resp.Body)
	values, _ := url.ParseQuery(string(body))
	return values.Get("access_token"), nil
}
```

注意这个请求是**服务端到服务端**的。Authorization头里带着 `client_secret`——这是你的应用在GitHub注册后获得的**私密凭证**，绝对不能暴露给前端。

### 第四步：用Token获取用户信息

```go
func fetchGitHubUser(accessToken string) (*GitHubUser, error) {
	req, _ := http.NewRequest("GET", "https://api.github.com/user", nil)
	req.Header.Set("Authorization", "Bearer "+accessToken)
	req.Header.Set("Accept", "application/json")

	resp, err := http.DefaultClient.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	var user GitHubUser
	json.NewDecoder(resp.Body).Decode(&user)
	return &user, nil
}

type GitHubUser struct {
	ID        int64  `json:"id"`
	Login     string `json:"login"`
	AvatarURL string `json:"avatar_url"`
	Email     string `json:"email"`
}
```

### 使用golang.org/x/oauth2简化

官方的 `golang.org/x/oauth2` 包封装了上述所有步骤，大幅减少样板代码：

```go
import (
	"golang.org/x/oauth2"
	"golang.org/x/oauth2/github"
)

var githubOAuth = &oauth2.Config{
	ClientID:     os.Getenv("GITHUB_CLIENT_ID"),
	ClientSecret: os.Getenv("GITHUB_CLIENT_SECRET"),
	RedirectURL:  "https://yourapp.com/api/v1/oauth/github/callback",
	Scopes:       []string{"user:email"},
	Endpoint:     github.Endpoint,
}

func GitHubLogin(c *gin.Context) {
	state := generateState()
	// 注意：Secure=true 在 localhost HTTP 环境下会导致 Cookie 无法存储，
	// 本地调试时请将 Secure 设为 false
	c.SetCookie("oauth_state", state, 600, "/", "", true, true)
	url := githubOAuth.AuthCodeURL(state)
	c.Redirect(http.StatusFound, url)
}

func GitHubCallback(c *gin.Context) {
	code := c.Query("code")
	state := c.Query("state")

	expectedState, _ := c.Cookie("oauth_state")
	if state != expectedState {
		c.JSON(400, gin.H{"msg": "state不匹配"})
		return
	}

	ctx := context.Background()
	token, err := githubOAuth.Exchange(ctx, code)
	if err != nil {
		c.JSON(500, gin.H{"msg": "换取Token失败"})
		return
	}

	client := githubOAuth.Client(ctx, token)
	resp, err := client.Get("https://api.github.com/user")
	if err != nil {
		c.JSON(500, gin.H{"msg": "获取用户信息失败"})
		return
	}
	defer resp.Body.Close()

	var user GitHubUser
	json.NewDecoder(resp.Body).Decode(&user)

	c.JSON(200, gin.H{"msg": "登录成功", "user": user})
}
```

一切都被简化了：不需要手动拼URL、手动做HTTP请求、手动处理Token——`oauth2`包全帮你做了。

---

## 80.4 其他授权模式简介

### 简化模式（Implicit Grant）— 已废弃

Token直接返回给浏览器，不需要授权码这一跳。因为Token暴露在浏览器端已被大多数安全标准标记为不安全。**不要在新项目中使用**。

### 密码模式（Resource Owner Password Credentials）— 已废弃

用户把用户名密码直接交给第三方应用，应用代理用户去授权服务器拿Token。问题显而易见——第三方应用看到了用户密码。**不要在新项目中使用**。

### 客户端凭证模式（Client Credentials）

用于**服务到服务**的认证。没有用户参与，Client用自己的 `client_id` + `client_secret` 直接换取Token。

适用场景：微服务A访问微服务B、定时任务访问API、CLI工具访问服务。

```go
token, err := oauthConfig.ClientCredentials(ctx).Token()
```

### PKCE（Proof Key for Code Exchange）

授权码模式的升级版，增加了 `code_verifier`（一个随机字符串）和 `code_challenge`（verifier的哈希），防止授权码在传输过程中被拦截后使用。

现在OAuth 2.1草案已经将PKCE作为**所有授权码流程的强制要求**。移动应用和单页应用尤其需要PKCE（因为它们没有 `client_secret`，或者说 `client_secret` 无法安全存储）。

---

## 80.5 第三方登录实战

### 微信登录

微信OAuth 2.0流程稍有不同，但核心思路一样：

```go
import "golang.org/x/oauth2"

var wechatOAuth = &oauth2.Config{
	ClientID:     os.Getenv("WECHAT_APP_ID"),
	ClientSecret: os.Getenv("WECHAT_APP_SECRET"),
	RedirectURL:  "https://yourapp.com/api/v1/oauth/wechat/callback",
	Scopes:       []string{"snsapi_userinfo"},
	Endpoint: oauth2.Endpoint{
		AuthURL:  "https://open.weixin.qq.com/connect/qrconnect",
		TokenURL: "https://api.weixin.qq.com/sns/oauth2/access_token",
	},
}
```

微信的特殊点：
- 需要先在微信开放平台注册应用，审核通过后才能使用
- `scope` 分 `snsapi_base`（静默授权，只拿openid）和 `snsapi_userinfo`（弹窗授权，拿用户信息）
- 获取用户信息的接口不是标准的 `/user`，而是 `https://api.weixin.qq.com/sns/userinfo?access_token=...&openid=...`

### 统一多平台登录

系统中通常不止一个第三方登录方式（GitHub、微信、Google……），每个平台的返回数据格式不同。需要在内部做一层适配：

```go
type OAuthProvider interface {
	GetAuthURL(state string) string
	ExchangeCode(code string) (*OAuthUserInfo, error)
}

type OAuthUserInfo struct {
	Provider    string
	ProviderID  string
	Username    string
	AvatarURL   string
	Email       string
}
```

然后针对每个平台实现这个接口。你的业务代码只依赖 `OAuthProvider` 接口，不关心底层是GitHub还是微信。

有个经典的复合键设计：`users` 表中用 `provider + provider_id` 联合唯一索引，区分不同来源的用户。同一个用户可能有 `github:12345` 和 `wechat:openid_abc` 两个关联记录，需要提供"账号绑定"功能将它们关联到同一个内部用户。

---

## 80.6 OAuth 2.0 vs 普通登录：彻底分清

### 两种根本不同的东西

| | 普通登录 | OAuth 2.0 |
|---|---|---|
| **解决的问题** | 你是谁（身份） | 你能做什么（权限） |
| **类比** | 出示身份证给门卫 | 签署一份授权委托书 |
| **谁持有凭证** | 用户（自己知道密码） | 第三方（拿到Token） |
| **凭证能做什么** | 用户自己能做的所有事 | 只能做授权范围内的事 |
| **凭证能撤销吗** | 改密码 | 随时注销Token |
| **协议** | 没有标准协议 | RFC 6749 |

### 为什么OAuth 2.0也能做登录？

虽然OAuth 2.0的设计目标是授权，但它附带了一个"副产品"：**用户信息API**。第三方拿到Token后，调用户信息接口，就能拿到用户的唯一标识（ID）和基本信息。有了ID，就能在你的系统里"认"出这个用户——这就是"用第三方登录"的原理。

严格来说，如果只是为了做登录，应该用 **OpenID Connect (OIDC)**——它是基于OAuth 2.0之上增加了一个 `id_token`（JWT格式，包含用户身份信息）的身份认证层。但在实践中，直接用OAuth 2.0的Token调用户信息API已经能满足大多数需求。

### 🤔 想多一点

OAuth 2.0看起来很复杂——授权码、重定向、Token交换、scope……但它解决的是一个非常真实的问题：**在用户控制下，安全地授权第三方访问用户的资源**。

回想一下这个场景的复杂程度：用户的数据在平台A（比如GitHub）手里，平台B（你的应用）想访问用户的数据，用户希望整个过程安全可控——不把密码交给B，能决定B能访问什么，能随时撤销B的权限。OAuth 2.0用了四个角色、两种Token、五次重定向来实现这个目标——这个复杂性是不可避免的。

好在有 `golang.org/x/oauth2` 这样的成熟库，把复杂度封装了起来，你只需要关心业务逻辑。

---

## 本章小结

| 知识点 | 要点 |
|--------|------|
| OAuth 2.0本质 | 委托授权，不是身份认证 |
| 四个角色 | Resource Owner / Client / Auth Server / Resource Server |
| 授权码模式 | 最安全：浏览器拿code→后端换Token→Token不经过浏览器 |
| client_id | 公开的应用标识 |
| client_secret | 私密凭证，仅存后端，绝不暴露 |
| scope | 权限范围（`user:email`） |
| state | 防CSRF的随机字符串 |
| 回调流程 | /authorize → 用户授权 → /callback?code=xxx → 后端换Token |
| oauth2包 | 封装了完整的OAuth 2.0客户端逻辑 |
| 简化模式/密码模式 | 已废弃，不要用 |
| 客户端凭证模式 | 服务到服务认证 |
| PKCE | 防授权码拦截的增强安全机制 |
| 微信登录 | 流程相同但接口地址不同 |
| 多平台统一 | OAuthProvider接口 + provider+provider_id联合键 |
| OAuth做登录 | 调用户信息API获取ID，非OAuth 2.0原始设计 |

> 🚀 下一章：第81章 · RBAC权限控制。现在用户能登录了、Token能用了、第三方也能接入了。但新的问题来了：管理员和普通用户看到的数据应该不一样吧？管理员能删文章，普通用户不能——这个"谁能干什么"的控制就是权限管理。RBAC（基于角色的访问控制）是其中最经典、最广泛使用的模型。

---
[← 上一章：79-JWT认证](79-JWT认证/) | [下一章：81-RBAC权限控制.md →](81-RBAC权限控制/)
