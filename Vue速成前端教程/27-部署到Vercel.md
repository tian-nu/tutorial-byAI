# 27 — 部署到 Vercel：让你的博客"上线"

- 对应文档版本：N/A（独立教程）
- 适用环境：Vite + Vue 3 项目，GitHub 仓库
- 读者角色：前端开发者
- 预计耗时：新手 30 分钟 / 熟手 15 分钟
- 前置教程：教程 26（构建与优化）
- 可视化：无

---

## 一、目标与完成效果

**一句话目标**：把博客部署到 Vercel，获得一个免费的、全球可访问的 HTTPS 域名。

**完成后你将看到**：
- 任何人访问 `https://你的项目名.vercel.app` 都能看到你的博客。
- 每次向 GitHub 推送代码，Vercel 自动重新部署（无需手动操作）。
- 自定义域名（如果你有的话）也可以绑定上去。

---

## 二、前置条件

- 项目代码已推送到 GitHub 仓库（公开或私有均可）
- 教程 26 完成，`npm run build` 无报错
- 一个 GitHub 账号（没有的话去 [github.com](https://github.com) 注册，免费）

**环境验证命令**：
```bash
git remote -v
```
应该看到你的 GitHub 仓库地址（如 `origin  https://github.com/你的用户名/你的项目名.git`）。

---

## 三、分步操作

### 步骤 1：为什么选 Vercel？

**我在做什么？**
在部署之前，先理解为什么推荐 Vercel 而不是其他平台。

| 特性 | Vercel | 传统 VPS（如阿里云 ECS） |
|------|--------|--------------------------|
| **费用** | 免费额度足够个人项目 | 最低配 ~50 元/月 |
| **HTTPS** | 自动配置，免费 SSL 证书 | 需要手动申请和续期 |
| **CDN** | 自动全球加速 | 需要额外购买 CDN 服务 |
| **部署方式** | 连接 GitHub 仓库，自动部署 | 手动 SSH 上传文件 + 配置 Nginx |
| **自定义域名** | 免费支持 | 需要手动配置 DNS + Nginx |
| **学习成本** | 5 分钟上手 | 需要了解 Linux、Nginx、SSL 等 |

**比喻**：Vercel 就像快递代发——你把包裹（代码）交给它，它帮你打包、贴标签、送到全世界的用户手里。传统 VPS 就像你自己买货车、考驾照、规划路线——能做，但麻烦得多。

🤔 **想多一点**：Vercel 的免费额度限制是什么？带宽 100GB/月，构建时间 6000 分钟/月，对个人博客来说绰绰有余。如果你的博客日访问量超过 10 万，才会触及免费额度上限——到那时候你已经有能力付费了。

---

### 步骤 2：注册 Vercel 并连接 GitHub

**我在做什么？**
用 GitHub 账号一键登录 Vercel，让 Vercel 能读取你的仓库。

1. 打开 [vercel.com](https://vercel.com)
2. 点击右上角 **Sign Up**
3. 选择 **Continue with GitHub**（用 GitHub 账号登录）
4. 授权 Vercel 访问你的 GitHub 仓库（选 "All repositories" 或只选博客项目仓库，两者都可以）
5. 注册完成后进入 Vercel Dashboard（仪表盘）

---

### 步骤 3：导入项目并部署

**我在做什么？**
告诉 Vercel："这个 GitHub 仓库是一个 Vite 项目，帮我部署它。"

1. 在 Vercel Dashboard 点击 **Add New...** → **Project**
2. 在仓库列表中找到你的博客项目，点击 **Import**
3. 配置页面：

   | 配置项 | 填写内容 | 说明 |
   |--------|----------|------|
   | **Framework Preset** | Vite | Vercel 自动检测到，一般不用手动选 |
   | **Build Command** | `npm run build` | 默认值，不用改 |
   | **Output Directory** | `dist` | 默认值，Vite 的输出目录 |
   | **Install Command** | `npm install` | 默认值，不用改 |

4. **环境变量**（如果你在教程 26 中配置了 `.env.production`）：
   - 点击 **Environment Variables** 展开
   - Key 填 `VITE_API_BASE_URL`，Value 填生产环境 API 地址（如 `https://api.your-blog.com/api`）
   - 点击 **Add**

5. 点击 **Deploy** 按钮

**等待过程**：Vercel 会执行以下步骤，你可以在界面上看到实时日志：
1. Cloning repository（克隆代码）
2. Installing dependencies（`npm install`）
3. Building（`npm run build`）
4. Deploying（上传到 CDN）

整个过程通常 1-2 分钟。

**部署成功**：你会看到一个 🎉 庆祝页面，上面写着：
> Congratulations! Your project has been deployed.
> **https://你的项目名.vercel.app**

点击链接，你的博客就上线了！全世界都能访问。

---

### 步骤 4：配置环境变量（如果跳过了步骤 3）

如果你在步骤 3 忘了配环境变量，或者后续需要修改，可以这样操作：

1. 进入项目 Dashboard → 点击 **Settings**
2. 左侧菜单选择 **Environment Variables**
3. 添加 Key/Value：
   - `VITE_API_BASE_URL` → `https://api.your-blog.com/api`
4. 保存后，需要**重新部署**才能生效：
   - 点击顶部的 **Deployments** 标签
   - 点击最新部署右侧的 `...` → **Redeploy**

---

### 步骤 5：自动部署 — 每次 push 自动更新

**我在做什么？**
Vercel 默认就开启了自动部署。你什么都不用做！

**验证流程**：
1. 在本地修改任意代码（比如改一下首页标题）
2. `git add . && git commit -m "test: 测试自动部署" && git push`
3. 打开 Vercel Dashboard → 你的项目 → Deployments 标签
4. 你会看到一个新的部署正在 Building → Ready
5. 访问 `https://你的项目名.vercel.app`，标题已经更新

**比喻**：这就像你有一个机器人管家，你每次把新的菜谱（代码）放到厨房（GitHub），机器人自动帮你做菜、摆盘、端到每一位客人面前。

🤔 **想多一点**：如果 push 后部署失败了怎么办？Vercel 会自动回滚到上一个成功的版本——用户访问的还是旧版，不会看到错误页面。你可以在 Deployments 页面查看构建日志，找到错误原因，修复后再次 push。

---

### 步骤 6：自定义域名（可选）

**我在做什么？**
`xxx.vercel.app` 虽然能用，但不够专业。如果你有自己的域名（如 `yourblog.com`），可以绑定到 Vercel。

1. 在项目 Dashboard → **Settings** → **Domains**
2. 输入你的域名（如 `blog.yourdomain.com`）→ 点击 **Add**
3. Vercel 会给出 DNS 配置指引：
   - 推荐方式：在你的域名注册商（如阿里云、Cloudflare）的 DNS 设置中添加一条 CNAME 记录，指向 `cname.vercel-dns.com`
4. 等 DNS 生效（通常几分钟到几小时），Vercel 会自动申请 SSL 证书
5. 生效后，访问 `https://blog.yourdomain.com` 就能看到你的博客

> 如果你还没有域名，跳过这一步完全不影响使用。`vercel.app` 域名对个人项目来说完全够用。

---

## 四、小结

| 步骤 | 做了什么 | 关键操作 |
|------|----------|----------|
| 1. 选平台 | 对比 Vercel 和传统 VPS | Vercel 免费、自动 HTTPS、CDN、自动部署 |
| 2. 注册 | GitHub 一键登录 | vercel.com → Sign Up → Continue with GitHub |
| 3. 导入项目 | 连接 GitHub 仓库 | Import → 确认 Framework Preset = Vite → Deploy |
| 4. 环境变量 | 配置生产 API 地址 | Settings → Environment Variables → `VITE_API_BASE_URL` |
| 5. 自动部署 | push 即部署 | `git push` → Vercel 自动检测 → 构建 → 上线 |
| 6. 自定义域名 | 绑自己的域名 | Settings → Domains → 添加 CNAME 记录 |

---

## 五、术语附录

| 术语 | 解释 |
|------|------|
| **Vercel** | 前端部署平台，由 Next.js 的团队开发。支持 Vite、React、Vue 等几乎所有前端框架，提供免费 HTTPS、全球 CDN 和自动部署。 |
| **CDN (Content Delivery Network)** | 内容分发网络。将你的网站文件复制到全球多个服务器上，用户访问时从离他最近的服务器获取，速度快。就像在全世界开连锁店，而不是只有一个总店。 |
| **自动部署 (Auto Deploy)** | 代码推送到 GitHub 后，平台自动执行构建和部署，无需手动操作。CI/CD（持续集成/持续部署）的具体实践。 |
| **CNAME 记录** | DNS 中的一种记录类型，将一个域名指向另一个域名。例如 `blog.yourdomain.com` → `cname.vercel-dns.com`。 |
| **SSL 证书** | 用于实现 HTTPS 加密的数字证书。Vercel 自动申请和续期 Let's Encrypt 免费证书，你不需要关心。 |
| **DNS (Domain Name System)** | 域名系统，将人类可读的域名（如 `google.com`）翻译成机器可读的 IP 地址（如 `142.250.80.46`）。 |

---

## 六、已知坑点与禁止事项

- **Vercel 不支持 `localhost` 后端**：部署后，`VITE_API_BASE_URL` 不能是 `http://localhost:8000`，必须是公网可访问的地址。如果你的后端还没部署，先暂时用 Mock 数据或跳过 API 调用（教程 28 会解决后端部署问题）。
- **环境变量修改后必须 Redeploy**：在 Settings 中修改环境变量不会自动触发部署，需要手动点击 Redeploy。
- **Vercel 的 Serverless 函数有时间限制**：如果你在项目里用了 Vercel 的 API Routes（后端函数），单次请求最多 10 秒（免费版），不适合长耗时任务。
- **不要提交 `.env` 文件到 GitHub**：Vercel 的环境变量在平台上配置，不需要文件。如果 `.env` 被提交了，可能被他人看到。

---

## 七、下一步建议

- 教程 28：对接后端教程——把后端也部署上去，前后端打通。
- 如果你有自己的域名，参考 [Vercel Domains 文档](https://vercel.com/docs/projects/domains) 配置自定义域名。