# 29-Nginx 反向代理 + HTTPS

> "你的博客在服务器 3000 端口上跑着，但用户不会记 `http://123.456.78.90:3000` 这种地址。这一章，Nginx 变成'前台接待员'——用户在 80 端口敲门，Nginx 把他们引到后台 3000 端口的 Node.js。再加上 Let's Encrypt 免费 SSL 证书，地址栏挂上小锁🔒——你的博客，真正像个正经网站了。"

---

## 一、目标与完成效果

**一句话目标**：安装 Nginx 并配置反向代理（80 端口 → 3000 端口），配置域名 DNS 解析，用 Let's Encrypt + Certbot 申请免费 SSL 证书，实现 HTTPS 加密访问和 HTTP 自动跳转 HTTPS。

**完成后的可观测效果**：
- Nginx 安装在服务器上，`sudo systemctl status nginx` 显示 `active (running)`。
- 创建了 Nginx 站点配置文件 `/etc/nginx/sites-available/blog`，反向代理 `localhost:3000`。
- 站点已启用（软链接到 `sites-enabled/`），`sudo nginx -t` 测试通过。
- 域名 DNS 解析已配置（A 记录指向服务器 IP），`ping 你的域名.com` 返回服务器 IP。
- 访问 `http://你的域名.com/api/articles` 返回 JSON 数据（和之前 `localhost:3000` 一样）。
- Let's Encrypt 证书已安装，访问 `https://你的域名.com/api/articles` 返回 JSON 数据，浏览器地址栏显示 🔒。
- HTTP 访问 `http://你的域名.com` 自动跳转到 `https://你的域名.com`。
- 证书自动续期已配置（`certbot renew --dry-run` 测试通过）。

---

## 二、前置条件

| 序号 | 条件 | 验证命令 |
|------|------|------|
| 1 | 已完成教程 28，博客在服务器上通过 PM2 运行 | `pm2 list` 显示 `blog` 进程状态为 `online` |
| 2 | 服务器安全组已开放 80 和 443 端口 | 阿里云控制台 → 安全组 → 入方向规则包含 TCP 80 和 TCP 443 |
| 3 | 拥有一个域名（如 `yourdomain.com`） | 如果没有，可以去阿里云/腾讯云/Namecheap 买一个（.com 约 50-70 元/年） |
| 4 | 域名 DNS 管理权限（能在域名提供商处添加 DNS 记录） | 在域名提供商网站登录，找到"DNS 解析"或"DNS 管理"页面 |

**一条命令确认前置满足**：

```bash
pm2 list && curl http://localhost:3000/api/articles
```

`pm2 list` 显示 `blog` 为 `online`，`curl` 返回 JSON 数据（不报错），前置条件满足。

---

## 三、分步操作

### 步骤 1：Nginx 是什么？

在理解 Nginx 之前，先理解当前的问题：

```
用户浏览器 → http://你的IP:3000 → Node.js (Express)
```

问题：
1. 用户要记端口号 `:3000`——不专业。
2. 没有 HTTPS 加密——密码明文传输，中间人能看到。
3. Node.js 直接暴露在公网——攻击者可以直接向 Express 发恶意请求。

**Nginx 解决所有这些问题**：

```
用户浏览器 → https://你的域名.com (443) → Nginx → http://localhost:3000 → Node.js
```

Nginx 是一个**反向代理服务器**。此术语需进附录。它站在用户和 Node.js 之间：
- 接收用户的 HTTPS 请求（443 端口）
- 解密 HTTPS
- 把请求转发给 Node.js（3000 端口）
- 把 Node.js 的响应加密后返回给用户

> 餐厅比喻：Nginx 是"前台接待员"——客人（用户）走进餐厅大门（80/443），接待员问"请问几位？"然后引导客人到后厨（Node.js 3000 端口）取餐。客人不需要知道后厨在哪条走廊、哪个窗口——这些细节由接待员处理。接待员还负责安全检查（HTTPS 加密）——让客人和后厨之间的对话不被隔壁桌听到。

**Nginx 还能做什么？**
- 静态文件服务（直接返回 HTML/CSS/JS/图片，不经过 Node.js）
- 负载均衡（把请求分发给多个 Node.js 实例）
- 限流（防止恶意请求刷爆服务器）
- Gzip 压缩（减小响应体积，加快传输）

本章只讲反向代理 + HTTPS——这是你最需要的功能。

---

### 步骤 2：安装 Nginx

在服务器上（deploy 用户）：

```bash
sudo apt update
sudo apt install nginx -y
```

**验证安装**：

```bash
sudo systemctl status nginx
```

**预期输出**：

```
● nginx.service - A high performance web server and a reverse proxy server
   Loaded: loaded (/lib/systemd/system/nginx.service; enabled; vendor preset: enabled)
   Active: active (running) since ...
```

`Active: active (running)` 表示 Nginx 安装成功且正在运行。

**在浏览器验证**：访问 `http://你的服务器IP`，应该看到 Nginx 的默认欢迎页面（"Welcome to nginx!"）。

---

### 步骤 3：Nginx 配置文件结构

Nginx 的配置文件有两层结构：

| 目录 | 用途 | 类比 |
|------|------|------|
| `/etc/nginx/sites-available/` | 存放所有可用的站点配置文件 | 菜单上"所有可以点的菜" |
| `/etc/nginx/sites-enabled/` | 存放已启用的站点配置文件（是 `sites-available/` 中文件的**软链接**） | "厨房正在做的菜" |

**为什么要分两层？** 方便临时下线某个站点：只需删除 `sites-enabled/` 中的软链接，配置文件还在 `sites-available/` 中，随时可以恢复。不需要删除配置文件。

**比喻**：`sites-available/` 是"衣橱"——所有衣服都在里面。`sites-enabled/` 是"今天穿的衣服"——从衣橱里挑出来挂到衣架上。换衣服就是换软链接，不用把衣服扔掉。

---

### 步骤 4：反向代理配置

#### 4.1 创建站点配置文件

```bash
sudo nano /etc/nginx/sites-available/blog
```

写入以下内容：

```nginx
server {
    listen 80;
    server_name your_domain.com www.your_domain.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

**把 `your_domain.com` 换成你的真实域名。** `www.your_domain.com` 是带 www 前缀的版本——两个都写上，用户访问哪个都能到你的网站。

#### 4.2 逐行解释

| 配置行 | 含义 | 为什么要这样写 |
|--------|------|---------------|
| `listen 80;` | 监听 80 端口（HTTP） | 用户通过 `http://你的域名` 访问时，Nginx 在 80 端口接收请求 |
| `server_name your_domain.com;` | 这个配置块对应的域名 | 一个服务器上可能跑多个网站（不同域名），`server_name` 区分它们 |
| `location / { ... }` | 匹配所有路径（`/` 开头的请求） | 你的博客 API 都在 `/api/` 下，但 `/` 匹配一切——包括将来可能的静态页面 |
| `proxy_pass http://localhost:3000;` | 把请求转发到 `localhost:3000` | 这是 Nginx 最核心的指令——"反向代理"就是这一行。此术语需进附录 |
| `proxy_http_version 1.1;` | 使用 HTTP/1.1 协议向后端转发 | WebSocket 需要 HTTP/1.1，HTTP/1.0 不支持 |
| `proxy_set_header Upgrade $http_upgrade;` | 传递 WebSocket 升级头 | 如果你的应用将来使用 WebSocket（实时通信），这行必不可少 |
| `proxy_set_header Connection 'upgrade';` | 配合 Upgrade 头，维持连接升级 | 同上，WebSocket 支持 |
| `proxy_set_header Host $host;` | 把原始请求的 Host 头传递给后端 | 后端 Node.js 需要知道"用户访问的是哪个域名"（多站点场景） |
| `proxy_cache_bypass $http_upgrade;` | WebSocket 连接不缓存 | 缓存 WebSocket 会导致连接失败 |
| `proxy_set_header X-Real-IP $remote_addr;` | 把用户的真实 IP 传给后端 | 没有这行，Node.js 看到的 `req.ip` 永远是 `127.0.0.1`（Nginx 的 IP） |
| `proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;` | 把完整的代理链传给后端 | 如果你的 Nginx 前面还有 CDN 或负载均衡器，这行能保留完整链路 |
| `proxy_set_header X-Forwarded-Proto $scheme;` | 把原始请求的协议（http/https）传给后端 | 后端可以根据这个判断用户用的是 HTTP 还是 HTTPS |

> 🔥 **魔鬼细节**：`proxy_pass http://localhost:3000/` 末尾的 `/` 影响路径拼接。**不带 `/`**（本教程配置）：`proxy_pass http://localhost:3000` → 请求 `/api/articles` → 转发到 `http://localhost:3000/api/articles`。**带 `/`**：`proxy_pass http://localhost:3000/` → 请求 `/api/articles` → 转发到 `http://localhost:3000/articles`（注意 `/api` 被去掉了）。这种细微差别是 Nginx 最常见的坑。

#### 4.3 配置中的 `$` 变量

Nginx 中有很多以 `$` 开头的变量：

| 变量 | 含义 | 示例值 |
|------|------|--------|
| `$host` | 请求的 Host 头（域名） | `your_domain.com` |
| `$remote_addr` | 客户端的 IP 地址 | `123.45.67.89` |
| `$scheme` | 请求的协议 | `http` 或 `https` |
| `$http_upgrade` | 请求头中的 Upgrade 字段 | `websocket` |

---

### 步骤 5：启用站点

#### 5.1 创建软链接

```bash
sudo ln -s /etc/nginx/sites-available/blog /etc/nginx/sites-enabled/
```

- `ln -s`：创建软链接（Symbolic link），相当于 Windows 的"快捷方式"
- 源文件：`/etc/nginx/sites-available/blog`
- 目标：`/etc/nginx/sites-enabled/blog`

#### 5.2 删除默认站点（可选）

Nginx 安装后自带一个默认站点配置，会干扰你的配置：

```bash
sudo rm /etc/nginx/sites-enabled/default
```

这只是删除软链接，默认配置文件仍在 `/etc/nginx/sites-available/default`，随时可以恢复。

#### 5.3 测试配置语法

```bash
sudo nginx -t
```

**预期输出**：

```
nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
nginx: configuration file /etc/nginx/nginx.conf test is successful
```

> 🔥 **魔鬼细节**：**每次修改 Nginx 配置后，必须先 `nginx -t` 测试语法，再 `reload`。** 如果语法错误就直接 `reload`，Nginx 会拒绝加载新配置，继续用旧配置运行——但你可能以为自己改好了，实际上没生效。

#### 5.4 重载配置

```bash
sudo systemctl reload nginx
```

**`reload` vs `restart`**：
- `reload`：平滑重载——Nginx 加载新配置，不中断正在处理的请求。
- `restart`：完全重启——先关闭 Nginx，再启动。中间有短暂的服务中断。

**优先使用 `reload`**。

---

### 步骤 6：域名 DNS 解析

在使 Nginx 配置生效之前，你需要让域名指向你的服务器 IP。

#### 6.1 什么是 DNS？

DNS（Domain Name System）把域名翻译成 IP 地址。此术语需进附录。

```
用户输入 your_domain.com → DNS 查询 → 返回 IP 123.45.67.89 → 浏览器连接这个 IP
```

#### 6.2 添加 A 记录

登录你的域名提供商（阿里云/腾讯云/Namecheap/GoDaddy 等），找到"DNS 解析"或"DNS 管理"页面。

添加一条 **A 记录**：

| 记录类型 | 主机记录 | 记录值 | TTL |
|----------|---------|--------|-----|
| A | @ | 你的服务器 IP | 600（10 分钟） |
| A | www | 你的服务器 IP | 600（10 分钟） |

- `A`：Address 记录，把域名指向 IPv4 地址
- `@`：表示根域名（`your_domain.com`）
- `www`：表示 `www.your_domain.com`
- TTL：Time To Live，DNS 缓存时间（秒），越短越容易快速生效

#### 6.3 验证 DNS 生效

DNS 变更需要时间传播（通常几分钟到几小时）。验证：

```bash
# 在本地电脑上运行
ping your_domain.com
```

如果返回的 IP 是你的服务器 IP，DNS 已生效。如果返回 `Ping request could not find host`，说明还没生效，等几分钟再试。

**或者用 `nslookup`**：

```bash
nslookup your_domain.com
```

---

### 步骤 7：验证 HTTP 反向代理

DNS 生效后，在浏览器访问：

```
http://your_domain.com/api/articles
```

**预期**：返回 JSON 数据，和之前 `curl http://localhost:3000/api/articles` 的结果一样。

**如果返回 502 Bad Gateway**：Nginx 无法连接到 `localhost:3000`。检查：
- `pm2 list` → `blog` 是否为 `online`
- `curl http://localhost:3000/api/articles` → 在服务器上能返回数据吗？

**如果返回 Nginx 默认页面**：你的站点配置没生效。检查：
- `sudo nginx -t` → 语法是否正确？
- `ls -la /etc/nginx/sites-enabled/` → 你的 `blog` 软链接是否存在？
- 是否删除了 `default` 软链接？

---

### 步骤 8：Let's Encrypt + Certbot 免费 SSL 证书

现在你的网站是 HTTP 的——浏览器地址栏显示"不安全"。接下来给它加上 HTTPS 小锁🔒。

#### 8.1 Let's Encrypt 是什么？

Let's Encrypt 是一个免费的、自动化的、开放的证书颁发机构（CA）。此术语需进附录。它提供完全免费的 SSL/TLS 证书，每次有效期 90 天，但可以自动续期。

**为什么免费？** Let's Encrypt 由各大科技公司（Mozilla、Google、Facebook、Cisco 等）赞助，目标是"让整个互联网都加密"。

#### 8.2 Certbot 是什么？

Certbot 是 Let's Encrypt 的官方客户端工具。此术语需进附录。它自动完成：
1. 向 Let's Encrypt 证明你拥有这个域名（通过 HTTP 验证）
2. 申请并下载 SSL 证书
3. 自动修改 Nginx 配置，添加 HTTPS 支持
4. 设置自动续期定时任务

#### 8.3 安装 Certbot

```bash
sudo apt install certbot python3-certbot-nginx -y
```

- `certbot`：核心工具
- `python3-certbot-nginx`：Nginx 插件，让 Certbot 能自动修改 Nginx 配置

#### 8.4 申请证书

```bash
sudo certbot --nginx -d your_domain.com -d www.your_domain.com
```

- `--nginx`：使用 Nginx 插件（自动修改 Nginx 配置）
- `-d your_domain.com`：为这个域名申请证书（可以写多个 `-d`，一个证书覆盖多个域名）

**把 `your_domain.com` 换成你的真实域名。**

**交互流程**：

1. **输入邮箱**：输入你的邮箱地址（用于证书到期提醒和紧急通知）
2. **同意条款**：输入 `A`（Agree）
3. **是否接收推广邮件**：输入 `Y` 或 `N`（无所谓）
4. **是否自动重定向 HTTP → HTTPS**：选择 `2`（Redirect）——自动把 HTTP 请求重定向到 HTTPS

**预期输出**：

```
Congratulations! You have successfully enabled https://your_domain.com and
https://www.your_domain.com

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

IMPORTANT NOTES:
 - Congratulations! Your certificate and chain have been saved at:
   /etc/letsencrypt/live/your_domain.com/fullchain.pem
   Your key file has been saved at:
   /etc/letsencrypt/live/your_domain.com/privkey.pem
   Your certificate will expire on YYYY-MM-DD.
```

#### 8.5 Certbot 自动修改了什么？

Certbot 自动修改了你的 Nginx 配置文件 `/etc/nginx/sites-available/blog`，添加了：

- `listen 443 ssl;`：监听 443 端口（HTTPS）
- SSL 证书路径
- HTTP → HTTPS 自动重定向（如果你选了 Redirect）

你现在可以查看被修改后的配置：

```bash
sudo cat /etc/nginx/sites-available/blog
```

你会看到两段 `server` 块——一段监听 80（HTTP，重定向到 HTTPS），一段监听 443（HTTPS，反向代理到 Node.js）。

> 🔥 **魔鬼细节**：Let's Encrypt 有**频率限制**——每周最多 5 个证书（同一域名）。如果你在测试，用 `--staging` 模式（`sudo certbot --nginx --staging -d your_domain.com`），它使用测试环境，没有频率限制，但浏览器会显示"不安全"（因为用的是测试证书）。正式上线时再去掉 `--staging`。

---

### 步骤 9：验证 HTTPS

在浏览器访问：

```
https://your_domain.com/api/articles
```

**预期**：
- 地址栏显示 🔒（小锁图标）
- 返回 JSON 数据
- 点击小锁 → 证书 → 可以看到"颁发给：your_domain.com"，"颁发者：R3（Let's Encrypt）"

访问 HTTP 版本：

```
http://your_domain.com/api/articles
```

**预期**：自动跳转到 `https://your_domain.com/api/articles`（HTTP 301 重定向）。此术语需进附录。

---

### 步骤 10：证书自动续期

Let's Encrypt 证书有效期只有 90 天。Certbot 安装时自动创建了 systemd timer，每天检查两次，在证书到期前自动续期。

#### 10.1 验证自动续期

```bash
sudo certbot renew --dry-run
```

`--dry-run`：模拟续期，不真正执行。如果输出 `Congratulations, all simulated renewals succeeded`，自动续期配置正确。

#### 10.2 查看定时器状态

```bash
sudo systemctl status certbot.timer
```

**预期输出**：`Active: active (waiting)`，说明定时器正在等待触发。

**比喻**：`certbot renew` 就像"自动续费会员"——你不是每 90 天手动续费一次，而是系统自动帮你续。`--dry-run` 是"续费预演"——确认续费流程没问题，但不动真格的。

---

### 🤔 想多一点：HTTPS 只加密传输，不保证服务器安全

很多人以为"有了 HTTPS 小锁 🛡️，网站就安全了"。这是误解。

**HTTPS 做了什么**：
- 加密浏览器和服务器之间的数据传输——中间人看不到内容（密码、文章内容等）
- 验证服务器身份——用户能确认自己连的是真的 `your_domain.com`，不是伪造的

**HTTPS 没做什么**：
- 不保证你的 Node.js 代码没有 SQL 注入漏洞
- 不保证你的 JWT_SECRET 没有被泄露
- 不保证你的服务器没有被黑客入侵
- 不保证你的数据库没有被人拖走

**比喻**：HTTPS 就像一个"加密快递箱"——快递员（中间人）看不到箱子里装了什么。但如果箱子里的东西本身就是假的（你的代码有漏洞），快递箱再安全也没用。

---

### 🤔 想多一点：80 端口必须开放——Let's Encrypt 验证需要

Let's Encrypt 验证你拥有域名的方式是：通过 HTTP（80 端口）访问 `http://your_domain.com/.well-known/acme-challenge/...`，检查一个临时文件。如果你关闭了 80 端口，Let's Encrypt 无法验证，证书申请失败。

**但你不是配置了 HTTP → HTTPS 重定向吗？** Certbot 足够聪明——验证请求不会被重定向，直接返回验证文件。其他请求才会被重定向到 HTTPS。

**所以在安全组中，80 端口必须保持开放。**

---

## 四、完整代码清单

### `/etc/nginx/sites-available/blog`（Certbot 修改后的最终版本）

```nginx
# HTTP → HTTPS 重定向（Certbot 自动添加）
server {
    listen 80;
    server_name your_domain.com www.your_domain.com;

    # Certbot 验证路径（不重定向）
    location /.well-known/acme-challenge/ {
        root /var/www/html;
    }

    # 其他所有请求重定向到 HTTPS
    location / {
        return 301 https://$host$request_uri;
    }
}

# HTTPS 反向代理（Certbot 自动修改）
server {
    listen 443 ssl;
    server_name your_domain.com www.your_domain.com;

    # SSL 证书（Certbot 自动添加）
    ssl_certificate /etc/letsencrypt/live/your_domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your_domain.com/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    # 反向代理到 Node.js
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## 五、验证方法

```bash
# 在服务器上，确保以下命令全部通过：

# 1. Nginx 运行正常
sudo systemctl status nginx
# → Active: active (running)

# 2. 配置语法正确
sudo nginx -t
# → syntax is ok, test is successful

# 3. 站点已启用
ls -la /etc/nginx/sites-enabled/
# → blog -> /etc/nginx/sites-available/blog

# 4. PM2 进程正常
pm2 list
# → blog 状态为 online

# 5. curl 本地验证
curl http://localhost:3000/api/articles
# → 返回 JSON 数据

# 6. curl Nginx 反向代理验证
curl http://localhost/api/articles
# → 返回 JSON 数据（和上面一样）

# 7. 证书自动续期
sudo certbot renew --dry-run
# → Congratulations, all simulated renewals succeeded
```

**在浏览器中验证**：
- `https://你的域名.com/api/articles` → 返回 JSON 数据，地址栏显示 🔒
- `http://你的域名.com/api/articles` → 自动跳转到 HTTPS 版本

全部通过？恭喜！你的博客现在有了"正经网站"的门面——域名 + HTTPS 小锁。下一章用 Docker 让部署更优雅。

---

## 六、小结表格

| 学到的东西 | 一句话解释 |
|-----------|-----------|
| Nginx | 高性能 Web 服务器 + 反向代理——前台接待员，把用户引导到后台 Node.js |
| 反向代理 | 用户访问 Nginx 的 80/443 端口，Nginx 转发到 `localhost:3000` |
| `sites-available/` vs `sites-enabled/` | 可用站点（衣橱）vs 已启用站点（今天穿的衣服），通过软链接关联 |
| `proxy_pass http://localhost:3000` | 反向代理核心指令——把请求转发到 Node.js |
| `proxy_set_header X-Real-IP` | 把用户的真实 IP 传给后端（否则 Node.js 只看到 `127.0.0.1`） |
| `proxy_set_header X-Forwarded-Proto` | 告诉后端用户用的是 HTTP 还是 HTTPS |
| `nginx -t` | 测试 Nginx 配置语法——每次修改配置后必执行 |
| `systemctl reload nginx` | 平滑重载配置（不中断服务），优于 `restart` |
| DNS A 记录 | 把域名指向服务器 IP 地址 |
| Let's Encrypt | 免费 SSL/TLS 证书颁发机构，证书有效期 90 天 |
| Certbot | Let's Encrypt 官方客户端，自动申请、安装、续期证书 |
| SSL/TLS | 加密浏览器和服务器之间的数据传输，地址栏显示 🔒 |
| HTTP 301 重定向 | HTTP 自动跳转到 HTTPS（浏览器地址栏从 `http://` 变成 `https://`） |
| `certbot renew --dry-run` | 模拟证书续期，验证自动续期配置正确 |

---

## 七、术语附录

| 术语 | 英文 | 通俗解释 | 本章出现位置 | 字面陷阱 |
|------|------|----------|-------------|----------|
| Nginx | Engine X | 高性能 Web 服务器和反向代理服务器。发音 "engine-x"。在 Node.js 项目中，Nginx 通常作为"前台"，接收用户请求，转发给后台的 Node.js。 | 步骤 1 | 不是"N-ginx"（分开发音）——发音是"engine-x"，因为它是"engine"（引擎）的变体。 |
| 反向代理 | Reverse Proxy | 代理服务器接收客户端的请求，转发给后端服务器，再把响应返回给客户端。客户端不知道后端服务器的存在——它只和代理通信。 | 步骤 1、4 | 不是"反向的代理"——"正向代理"是代理客户端（如翻墙工具），"反向代理"是代理服务器（如 Nginx）。方向是从"谁被代理"的角度看的。 |
| SSL/TLS | Secure Sockets Layer / Transport Layer Security | 加密浏览器和服务器之间数据传输的协议。TLS 是 SSL 的升级版，但大家习惯统称为 SSL。效果：地址栏显示 🔒。 | 步骤 8 | 不是"安全锁"——SSL/TLS 是加密协议，🔒 只是浏览器对这个协议的视觉表示。 |
| Let's Encrypt | — | 免费、自动化、开放的 SSL 证书颁发机构。由 Mozilla、Google、Cisco 等赞助，目标是"让互联网全部加密"。 | 步骤 8 | 不是"让我们加密吧"——虽然字面意思是这个，但它是一个组织名称，不是口号。 |
| Certbot | — | Let's Encrypt 的官方客户端工具。自动证明域名所有权、申请证书、安装证书、配置自动续期。 | 步骤 8 | 不是"证书机器人"——"bot"在这里是"自动化工具"的意思。 |
| HTTP 301 重定向 | HTTP 301 Redirect | HTTP 状态码 301，表示"永久重定向"。浏览器收到 301 后，自动跳转到新的 URL。HTTP → HTTPS 跳转就是 301 重定向。 | 步骤 9 | 不是"301 号错误"——3xx 是重定向状态码，不是错误。4xx 和 5xx 才是错误。 |
| proxy_pass | — | Nginx 指令。将请求转发到指定的后端服务器地址。`proxy_pass http://localhost:3000` 表示转发到本机的 3000 端口。 | 步骤 4 | 不是"代理通过"——"pass"是"传递"的意思，表示"把请求传递给后端"。 |
| DNS | Domain Name System | 域名解析系统。把人类可读的域名（`your_domain.com`）翻译成机器可读的 IP 地址（`123.45.67.89`）。 | 步骤 6 | 不是"域名服务器"——DNS 是一个分布式系统，不是单台服务器。 |

---

## 八、已知坑点与禁止事项

| 坑点 | 现象 | 原因 | 解决 |
|------|------|------|------|
| `proxy_pass` 末尾 `/` 的问题 | 请求 `/api/articles` 返回 404，路径不对 | `proxy_pass http://localhost:3000/`（带 `/`）会去掉 `/api` 前缀 | 用不带 `/` 的写法：`proxy_pass http://localhost:3000` |
| 修改 Nginx 配置后没 reload | 改了配置但没生效 | 只修改了文件，没有 `systemctl reload nginx` | 每次修改配置后执行 `sudo nginx -t && sudo systemctl reload nginx` |
| nginx -t 失败 | `nginx: [emerg] "proxy_pass" directive is not allowed here` | 配置语法错误——比如 `proxy_pass` 放在了 `server` 块而不是 `location` 块中 | 检查大括号匹配，确保 `proxy_pass` 在 `location / { ... }` 内部 |
| 80 端口被占用 | `nginx: [emerg] bind() to 0.0.0.0:80 failed (98: Address already in use)` | 另一个程序（可能是另一个 Nginx 实例或 Apache）占用了 80 端口 | `sudo lsof -i :80` 查看谁占用了 80 端口，停止或卸载它 |
| DNS 没生效 | 浏览器访问域名显示"无法连接" | DNS 记录还没传播到你的网络 | 等几分钟到几小时；用 `ping your_domain.com` 检查；用手机 4G 网络测试（不同 DNS 服务器） |
| Let's Encrypt 频率限制 | `too many certificates already issued for this domain` | 同一域名一周内申请超过 5 次证书 | 等待一周，或用 `--staging` 模式测试：`sudo certbot --nginx --staging -d your_domain.com` |
| 443 端口没开放 | HTTPS 访问超时，`curl https://your_domain.com` 失败 | 安全组没有开放 443 端口 | 在安全组中添加 TCP 443 入方向规则 |
| Certbot 验证失败 | `Challenge failed for domain your_domain.com` | 80 端口没开放，或 DNS 没指向服务器 IP | 确保 80 端口在安全组中开放，确保 DNS A 记录指向服务器 IP |
| 证书过期了 | 浏览器显示"您的连接不是私密连接" | 自动续期没配置好，或 80 端口被关闭导致续期失败 | `sudo certbot renew` 手动续期；`sudo certbot renew --dry-run` 测试自动续期 |

---

## 九、下一步建议

你的博客现在有了域名 + HTTPS 小锁，看起来像个正经网站了。但部署流程还比较手工——每次更新代码要 SSH 登录、`git pull`、`npm install`、`pm2 restart`。下一章用 Docker 把整个部署流程容器化，一次配置，到处运行。

**下一章（教程 30：Docker 容器化部署）**，你将：
- 创建 Dockerfile——把博客代码和环境打包成镜像
- 创建 `.dockerignore`——排除 `node_modules/`、`.env` 等不需要打包的文件
- 构建 Docker 镜像（`docker build`）
- 运行 Docker 容器（`docker run`）
- 用 docker-compose 编排 Node.js + PostgreSQL + Nginx 三容器
- 理解 Docker 的核心概念：镜像、容器、Volume、docker-compose

---

> 📊 本教程无可视化
>
> 本教程编辑记录：2026-06-12 初始版本（第 7 批：27-31 章）。