# 28-Nginx + HTTPS

- 对应文档版本：首版教程
- 适用环境：Ubuntu 22.04 LTS 服务器，已有域名
- 读者角色：后端初学者
- 预计耗时：新手 60 分钟 / 熟手 30 分钟（不含域名购买和 DNS 生效时间）
- 前置教程：[27-买服务器 + 部署]
- 可视化：无

---

## 一、目标与完成效果

**一句话目标**：用 Nginx 做反向代理，让用户通过域名访问你的博客（不用带 `:8000` 端口号），并配置 Let's Encrypt 免费 HTTPS 证书，让浏览器地址栏出现小锁图标。

**完成后的可观测效果**：
- 用户访问 `https://你的域名.com/docs`，浏览器地址栏显示 🔒 小锁图标。
- 用户访问 `http://你的域名.com` 自动跳转到 `https://你的域名.com`。
- Nginx 监听 80/443 端口，把请求转发给后端 FastAPI（8000 端口），用户不需要知道 8000 端口的存在。
- HTTPS 证书由 Let's Encrypt 免费签发，certbot 自动管理续期，你不需要手动操作。
- 安全组可以关闭 8000 端口——只开放 80（HTTP）和 443（HTTPS）。

---

## 二、前置条件

| 序号 | 条件 | 验证命令 |
|------|------|----------|
| 1 | 已完成教程 27，博客系统在服务器上运行 | 浏览器访问 `http://你的公网IP:8000/docs` 能看到 Swagger 页面 |
| 2 | 服务器 SSH 可登录 | `ssh root@你的公网IP` 能成功登录 |
| 3 | 拥有一个域名（需要购买，步骤 5 会讲） | 去云服务商控制台查看域名列表 |
| 4 | 安全组已开放 80 和 443 端口 | 在云服务商控制台检查防火墙规则 |

**一条命令确认前置满足**：

```bash
# 在服务器上执行
curl http://localhost:8000/docs
```

如果返回 HTML 内容（Swagger 页面），前置条件满足。

---

## 三、分步操作

### 步骤 1：为什么需要 Nginx？——反向代理是什么

**我在做什么？** 理解 Nginx 的角色——它不是你程序的替代品，而是站在你程序前面的"门童"。

**当前状态**：用户访问 `http://你的IP:8000/docs`，请求直接打到 FastAPI（uvicorn）。这个方案有两个问题：

| 问题 | 说明 |
|------|------|
| 带端口号 `:8000` | 用户需要记住端口号，不优雅。HTTP 默认端口是 80，HTTPS 是 443 |
| 没有 HTTPS | 数据明文传输，密码、token 都能被中间人截获 |
| 静态文件性能差 | uvicorn 不擅长处理静态文件（图片、CSS、JS），Nginx 专门优化过 |

**Nginx 是"反向代理服务器"**（此术语需进附录）。它站在用户和你的 FastAPI 之间，像这样：

```
用户(浏览器) → Nginx(80/443端口) → FastAPI(8000端口)
```

**比喻**：Nginx 是"公司前台"。访客（用户）不需要知道每个员工的内部分机号（8000），只需要打公司总机（80/443），前台会转接到正确的分机。

**反向代理 vs 正向代理**：

| 类型 | 方向 | 比喻 |
|------|------|------|
| 正向代理 | 客户端 → 代理 → 服务器 | 你翻墙访问 Google，VPN 是正向代理 |
| 反向代理 | 客户端 → 代理 → 后端服务器 | 用户访问 `baidu.com`，Nginx 把请求转发给后端服务器 |

**Nginx 还能做什么？**
- **负载均衡**：把请求分发给多台服务器（流量大了加机器）。
- **静态文件服务**：直接返回图片、CSS、JS，不经过 Python。
- **SSL 终止**：处理 HTTPS 加解密，后端不用管（本教程重点）。
- **限流、缓存、压缩**：这些留给进阶教程。

---

### 步骤 2：安装 Nginx

**我在做什么？** 在服务器上安装 Nginx。

```bash
# SSH 登录服务器
ssh root@你的公网IP

# 安装 Nginx
apt install nginx -y
```

**验证安装**：

```bash
nginx -v
# 预期输出：nginx version: nginx/1.18.0 (Ubuntu)

systemctl status nginx
# 预期输出：Active: active (running)
```

**如果 Nginx 没有自动启动**：

```bash
systemctl start nginx      # 启动
systemctl enable nginx     # 设置开机自启
```

**现在测试**：浏览器访问 `http://你的公网IP`（注意：不带端口号，默认就是 80 端口）。

**你应该看到 Nginx 默认欢迎页面**——"Welcome to nginx!"。

**我做得对不对？** 浏览器访问 `http://你的公网IP`，看到 Nginx 欢迎页。

**不对怎么办？**

| 问题 | 解决 |
|------|------|
| 看不到 Nginx 欢迎页 | 检查安全组是否开放了 80 端口。添加规则：端口 80，协议 TCP，来源 0.0.0.0/0 |
| Nginx 启动失败 | `journalctl -xeu nginx` 查看错误日志。常见原因：80 端口被其他程序占用 |
| 80 端口被占用 | `lsof -i:80` 查看占用者，关掉或用其他端口 |

---

### 步骤 3：配置反向代理

**我在做什么？** 写 Nginx 配置文件，告诉它：把 80 端口的请求，转发给 8000 端口的 FastAPI。

#### 3.1 创建站点配置文件

Nginx 的配置文件在 `/etc/nginx/` 目录下。**正确的做法**是在 `sites-available/` 中创建配置文件，然后链接到 `sites-enabled/`。不要直接修改 `nginx.conf`。

```bash
# 创建配置文件
vim /etc/nginx/sites-available/blog
```

**按 `i` 进入编辑模式，粘贴以下内容**：

```nginx
server {
    listen 80;
    server_name 你的域名.com www.你的域名.com;

    # 日志文件
    access_log /var/log/nginx/blog_access.log;
    error_log /var/log/nginx/blog_error.log;

    # 静态文件直接由 Nginx 处理（如果有）
    location /static/ {
        alias /root/blog_backend/static/;
    }

    # 所有其他请求转发给 FastAPI
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

**逐行解释**：

| 配置项 | 含义 |
|--------|------|
| `listen 80;` | 监听 80 端口（HTTP 默认端口） |
| `server_name` | 这个配置块为哪些域名服务。可以写多个，用空格分隔 |
| `access_log` | 访问日志的存放位置，记录所有请求 |
| `error_log` | 错误日志的存放位置 |
| `location /static/` | 匹配 `/static/` 开头的 URL（如图片），直接返回文件，不经过 Python |
| `location /` | 匹配所有其他请求 |
| `proxy_pass http://127.0.0.1:8000;` | **核心配置**：把请求转发给本机的 8000 端口（FastAPI）。此术语需进附录：proxy_pass |
| `proxy_set_header Host $host;` | 把原始请求的域名传给后端 |
| `proxy_set_header X-Real-IP $remote_addr;` | 把真实客户端 IP 传给后端（否则后端只能看到 Nginx 的 IP 127.0.0.1） |
| `proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;` | 传递完整的代理链 IP |
| `proxy_set_header X-Forwarded-Proto $scheme;` | 告诉后端原始请求用的是 http 还是 https |

**比喻**：`proxy_pass` 就像"转接电话"。用户打公司总机（80 端口），总机说"请稍等，我帮你转接"，然后接通内部分机（8000 端口）。`proxy_set_header` 是"来电显示"——告诉分机"这通电话是从哪个号码（IP）打来的"。

**注意**：`server_name` 先填 `_`（下划线，匹配所有域名），等你买了域名再改回来。或者直接用你的公网 IP：

```nginx
server_name 你的公网IP;
```

---

### 步骤 4：启用站点并重载 Nginx

**我在做什么？** 激活配置文件，让 Nginx 生效。

```bash
# 创建符号链接（类似 Windows 的快捷方式）
ln -s /etc/nginx/sites-available/blog /etc/nginx/sites-enabled/

# 检查配置语法
nginx -t
```

**预期输出**：

```
nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
nginx: configuration file /etc/nginx/nginx.conf test is successful
```

**如果 `nginx -t` 报错**，检查 vim 编辑时有没有漏掉分号（`;`）。Nginx 配置的每一行指令必须以分号结尾。

```bash
# 重载 Nginx（不中断服务）
systemctl reload nginx
```

**现在测试**：浏览器访问 `http://你的公网IP/docs`。

**你应该看到 Swagger 文档页面！** 而且 URL 里没有 `:8000` 了——Nginx 帮你把 80 端口的请求转发给了 8000 端口。

**我做得对不对？** `http://你的公网IP/docs` 能正常显示 Swagger UI，和之前 `http://你的公网IP:8000/docs` 一样。

**不对怎么办？**

| 问题 | 现象 | 解决 |
|------|------|------|
| `nginx -t` 报语法错误 | `unexpected "}"` 或 `unknown directive` | 检查分号是否遗漏，大括号是否配对 |
| 访问 `http://IP/docs` 返回 502 Bad Gateway | Nginx 连不上 FastAPI | FastAPI 没启动。`ps aux \| grep uvicorn` 确认服务在运行 |
| 访问返回 404 | Nginx 没找到配置 | 检查 `ln -s` 是否正确创建了链接 |
| Swagger 能打开，但接口测试报错 | 可能是 CORS 或路径问题 | 检查 `proxy_set_header Host` 配置是否正确 |

---

### 步骤 5：域名绑定

**我在做什么？** 购买一个域名，设置 DNS 解析，让域名指向你的服务器 IP。

#### 5.1 购买域名

在任意域名注册商购买（推荐和云服务器同一家，管理方便）：

| 平台 | 参考价格 |
|------|----------|
| 阿里云（万网） | `.com` ~60 元/年，`.top` ~20 元/年 |
| 腾讯云（DNSPod） | 同上 |
| Namesilo（国外） | `.com` ~$10/年 |

**选择建议**：`.com` 最通用，`.top`/`.xyz` 便宜。学习阶段选便宜的就行。

#### 5.2 DNS 解析——添加 A 记录

**DNS**（Domain Name System，此术语需进附录）把域名翻译成 IP 地址。你需要添加一条 **A 记录**（此术语需进附录），告诉全世界"这个域名指向我的服务器"。

在域名控制台 → DNS 解析 → 添加记录：

| 字段 | 值 | 说明 |
|------|-----|------|
| 记录类型 | `A` | A 记录 = 域名 → IPv4 地址 |
| 主机记录 | `@` | `@` 代表根域名（如 `yourdomain.com`），`www` 代表 `www.yourdomain.com` |
| 记录值 | `你的公网IP` | 如 `47.96.123.45` |
| TTL | `600`（默认） | 缓存时间，单位秒。越小生效越快，但查询压力大 |

**添加两条记录**：

| 主机记录 | 记录类型 | 记录值 | 效果 |
|----------|----------|--------|------|
| `@` | A | 你的公网IP | `yourdomain.com` → 你的服务器 |
| `www` | A | 你的公网IP | `www.yourdomain.com` → 你的服务器 |

**DNS 生效需要时间**：通常在几分钟到几小时内生效。可以用 `ping` 命令检查：

```powershell
ping yourdomain.com
```

如果返回的 IP 是你的服务器 IP，说明 DNS 已生效。

**DNS 生效后，更新 Nginx 配置**：

```bash
vim /etc/nginx/sites-available/blog
```

把 `server_name` 改成你的域名：

```nginx
server_name yourdomain.com www.yourdomain.com;
```

然后重载：

```bash
nginx -t && systemctl reload nginx
```

**现在访问 `http://yourdomain.com/docs`，应该能看到 Swagger 页面！**

---

### 步骤 6：HTTPS 免费证书——Let's Encrypt + Certbot

**我在做什么？** 配置 HTTPS，让域名从 `http://` 变成 `https://`，浏览器显示小锁图标。

**HTTPS 需要 SSL/TLS 证书**（此术语需进附录）。证书通常要花钱买（几百到几千元/年），但 **Let's Encrypt**（此术语需进附录）提供**完全免费**的证书，自动签发、自动续期。

**Certbot**（此术语需进附录）是 Let's Encrypt 的官方客户端，一条命令搞定证书申请和配置。

#### 6.1 安装 Certbot

```bash
# 安装 certbot 和 Nginx 插件
apt install certbot python3-certbot-nginx -y
```

#### 6.2 获取证书

```bash
# 自动配置 Nginx 并获取证书
certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

**参数说明**：
- `--nginx`：使用 Nginx 插件，自动修改 Nginx 配置。
- `-d yourdomain.com`：为这个域名申请证书。可以多次使用 `-d` 添加多个域名。

**交互过程**：

```
Enter email address: your_email@example.com    ← 输入你的邮箱（用于证书到期提醒）
- - - - - - - - - - - - - - - - - - - - - - - -
Please read the Terms of Service at https://letsencrypt.org/...
- - - - - - - - - - - - - - - - - - - - - - - -
(A)gree/(C)ancel: A   ← 输入 A 同意服务条款
- - - - - - - - - - - - - - - - - - - - - - - -
Would you be willing to share your email address with the Electronic Frontier
Foundation? (Y)es/(N)o: N   ← 输入 N（不分享邮箱）
- - - - - - - - - - - - - - - - - - - - - - - -
Please choose whether or not to redirect HTTP traffic to HTTPS...
1: No redirect
2: Redirect
Select the appropriate number: 2   ← 输入 2（HTTP 自动跳转 HTTPS）
```

**选 2** 的好处：用户访问 `http://yourdomain.com` 会自动跳转到 `https://yourdomain.com`。

**成功后你会看到**：

```
Congratulations! You have successfully enabled https://yourdomain.com and
https://www.yourdomain.com
```

**现在访问 `https://yourdomain.com/docs`，浏览器地址栏显示 🔒 小锁图标！** 🎉

**我做得对不对？** 浏览器访问 `https://yourdomain.com/docs`，地址栏左侧有小锁图标，点击可以看到"连接是安全的"和证书信息。

**不对怎么办？**

| 问题 | 现象 | 解决 |
|------|------|------|
| DNS 还没生效 | `certbot` 报错 DNS 解析不到你的域名 | 等 DNS 生效（几分钟到几小时）。用 `ping yourdomain.com` 检查 |
| 安全组没开 443 端口 | HTTPS 访问不了，HTTP 正常 | 在安全组添加规则：端口 443，协议 TCP，来源 0.0.0.0/0 |
| 80 端口没开 | certbot 验证失败（Let's Encrypt 通过 HTTP 验证域名所有权） | 安全组必须开放 80 端口，certbot 才能完成验证 |
| 域名解析到了 CDN 或其他 IP | certbot 验证失败 | 确保 A 记录指向你的服务器 IP，如果有 CDN 先暂停 |

---

### 步骤 7：自动续期

**我在做什么？** Let's Encrypt 证书有效期只有 90 天，需要设置自动续期。

**好消息**：certbot 安装时会自动添加一个定时任务（systemd timer），每天检查两次，证书到期前自动续期。

**验证自动续期是否正常**：

```bash
# 模拟续期（不真正续期，只测试流程是否正常）
certbot renew --dry-run
```

**预期输出**：

```
Congratulations, all simulated renewals succeeded...
```

如果看到 `succeeded`，说明自动续期配置正确，你不需要做任何事。

**查看定时任务**：

```bash
systemctl list-timers | grep certbot
```

**比喻**：certbot 的自动续期就像"自动续费的会员"——到期前自动帮你续，你不需要操心。

---

### 步骤 8：最终效果——关掉 8000 端口

**我在做什么？** 安全加固——既然 Nginx 已经接管了 80/443 端口，8000 端口只对服务器内部开放，不需要对外暴露。

在云服务商安全组中，删除 8000 端口的规则（或保留但不开放 0.0.0.0/0）。

**现在外网只能通过 80（HTTP）和 443（HTTPS）访问你的服务，8000 端口被 Nginx 隐藏在后面。**

**比喻**：之前你的家（FastAPI）大门敞开，任何人找 8000 号门就能进来。现在你雇了一个前台（Nginx），所有人都从大门（80/443）进来，前台再转接。8000 号门只对内部开放，外面的人找不到。

---

## 四、完整代码清单

### `/etc/nginx/sites-available/blog`（Nginx 配置文件）

<details>
<summary>点击展开完整代码</summary>

```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    access_log /var/log/nginx/blog_access.log;
    error_log /var/log/nginx/blog_error.log;

    location /static/ {
        alias /root/blog_backend/static/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

> 注意：certbot 运行后会修改此文件，自动添加 SSL 相关配置（`listen 443 ssl`、证书路径等）。

</details>

---

## 五、验证方法

```bash
# 在任意终端（不是服务器）执行以下验证：

# 1. HTTP 访问
curl -I http://yourdomain.com
# → 应该返回 301 或 302 重定向到 https://

# 2. HTTPS 访问
curl -I https://yourdomain.com
# → 返回 HTTP/2 200，说明 HTTPS 正常

# 3. API 文档访问
# 浏览器打开 https://yourdomain.com/docs
# → 能看到 Swagger 文档页面，地址栏有小锁 🔒

# 4. 证书信息
curl -vI https://yourdomain.com 2>&1 | grep "expire date"
# → 能看到证书到期时间（约 90 天后）

# 5. 自动续期检查
# 在服务器上执行
certbot renew --dry-run
# → 输出 "Congratulations, all simulated renewals succeeded"
```

---

## 六、术语附录

| 术语 | 英文 | 通俗解释 | 本章出现位置 |
|------|------|----------|-------------|
| Nginx | — | 高性能的 HTTP 服务器和反向代理服务器。发音 "Engine-X"。 | 步骤 1 |
| 反向代理 | Reverse Proxy | 代理服务器站在服务器端，接收客户端请求后转发给后端服务器。客户端不知道后端的存在。 | 步骤 1 |
| proxy_pass | — | Nginx 的核心指令，定义把请求转发到哪个地址。`proxy_pass http://127.0.0.1:8000;`。 | 步骤 3 |
| DNS | Domain Name System | 域名系统，把域名（如 `baidu.com`）翻译成 IP 地址（如 `110.242.68.66`）。互联网的"电话簿"。 | 步骤 5 |
| A 记录 | A Record | DNS 记录类型之一，把域名指向一个 IPv4 地址。`yourdomain.com → 47.96.123.45`。 | 步骤 5 |
| SSL/TLS | Secure Sockets Layer / Transport Layer Security | 加密协议，保护浏览器和服务器之间的数据传输不被窃听或篡改。TLS 是 SSL 的升级版，但大家习惯叫 SSL。 | 步骤 6 |
| HTTPS | HTTP over TLS | HTTP + 加密 = HTTPS。浏览器地址栏显示 🔒 小锁。 | 步骤 6 |
| Let's Encrypt | — | 免费、自动化、开放的证书颁发机构。提供 90 天有效期的 SSL/TLS 证书，支持自动续期。 | 步骤 6 |
| Certbot | — | Let's Encrypt 的官方客户端，自动申请和续期证书，自动配置 Nginx。 | 步骤 6 |
| 符号链接 | Symbolic Link（symlink） | 类似 Windows 的"快捷方式"——一个文件指向另一个文件。`ln -s 源文件 链接名`。 | 步骤 4 |
| systemctl | System Control | systemd 的管理命令，用于启动/停止/重启/查看服务状态。`systemctl reload nginx`。 | 步骤 4 |

---

## 七、小结

| 你学到了什么 | 一句话总结 |
|--------------|-----------|
| Nginx 反向代理 | Nginx 监听 80/443 端口，把请求转发给 FastAPI 的 8000 端口 |
| 站点配置 | 在 `sites-available/` 创建配置，`ln -s` 链接到 `sites-enabled/`，`nginx -t` 检查，`systemctl reload` 生效 |
| 域名绑定 | 买域名 → 添加 A 记录指向服务器 IP → DNS 生效后域名可访问 |
| HTTPS 免费证书 | Let's Encrypt + Certbot，一条命令搞定，90 天自动续期 |
| HTTP 自动跳转 HTTPS | certbot 自动配置，用户访问 HTTP 自动跳转 HTTPS |
| 安全加固 | 关掉 8000 端口对外暴露，只开放 80 和 443 |

---

## 八、已知坑点与禁止事项

| 坑点 | 现象 | 原因 | 解决 |
|------|------|------|------|
| DNS 还没生效就申请证书 | certbot 报错域名解析失败 | DNS 传播需要时间（几分钟到 48 小时） | 用 `ping yourdomain.com` 确认 IP 正确后再运行 certbot |
| 安全组没开 443 端口 | HTTPS 访问超时，HTTP 正常 | certbot 能申请证书（通过 80 端口验证），但 HTTPS 需要 443 端口 | 在安全组添加 443 端口规则 |
| 安全组没开 80 端口 | certbot 验证失败 | Let's Encrypt 通过 HTTP（80 端口）验证域名所有权 | 申请证书前确保 80 端口开放 |
| 直接修改 `nginx.conf` | 配置混乱，升级 Nginx 时可能被覆盖 | 正确的做法是在 `sites-available/` 中创建独立配置文件 | 用 `sites-available/` + `sites-enabled/` 模式 |
| `proxy_pass` 末尾带 `/` | 路径拼接行为不同 | `proxy_pass http://127.0.0.1:8000;` vs `proxy_pass http://127.0.0.1:8000/;` 路径处理不同 | 不带 `/` 时，原始 URI 完整传递；带 `/` 时，匹配的 location 部分被替换。本教程用不带 `/` 的写法 |
| 忘记 `systemctl enable nginx` | 服务器重启后 Nginx 不自动启动 | `systemctl enable` 设置开机自启 | 安装后执行 `systemctl enable nginx` |
| certbot 选了 "No redirect" | 用户访问 HTTP 不会自动跳转 HTTPS | certbot 交互时选错了选项 | 重新运行 `certbot --nginx -d yourdomain.com`，选择 redirect |

---

## 九、下一步建议

HTTPS 配置完成！你的博客现在有专业的外表了——域名 + HTTPS + 小锁图标，和商业网站一样。

但还有一个问题：每次换服务器，你都要手动执行 `apt install`、`git clone`、`pip install`、`nohup`……如果能把整个部署流程"打包"成一个命令就好了。

**这正是 Docker 要做的事。** 接下来：教程 29（Docker 入门）。你将学习如何用 Docker 把你的应用和所有依赖打包成"集装箱"，换一台服务器只需 `docker-compose up -d` 一条命令。

---

> [可暂停点 8/9]：阶段八（部署上线）第三部分完成。你的博客系统现在通过 Nginx 反向代理 + HTTPS 域名访问，安全且专业。接下来进入 Docker 入门。