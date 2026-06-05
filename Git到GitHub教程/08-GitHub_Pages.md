# 步骤8 · GitHub Pages：免费拥有一个网站

> 你写了一个网页——超级棒的那种。你的朋友想看，你总不能把你的电脑抱去他家吧？你想把网页放到互联网上，但买服务器要钱、配 Nginx 要技术、搞域名要花钱还要备案——听起来就头疼。GitHub Pages 就是解决这个问题的：你只需要把 HTML 文件放在仓库里，点几下按钮，一个公网能访问的网站就上线了。**完全免费，自动提供 HTTPS 加密，不需要你会任何服务器知识。**

---

## 8.1 什么是 GitHub Pages——把仓库变成网站

### 一句话解释

**GitHub Pages 是 GitHub 免费提供的"网页寄存服务"。** 你把 HTML 文件放在仓库里，GitHub 自动把这些文件变成一个别人可以通过网址访问的网站。

网址长这样：

```
https://<你的GitHub用户名>.github.io/<仓库名>
```

比如你的用户名是 `zhangsan`，仓库名是 `my-first-project`，那网站地址就是：

```
https://zhangsan.github.io/my-first-project
```

> **此术语需进附录：GitHub Pages**——GitHub 提供的免费静态网站托管服务。把仓库里的 HTML/CSS/JS 文件自动发布成公网可访问的网站。免费域名格式为 `https://<用户名>.github.io/<仓库名>`。

### 能放什么、不能放什么

GitHub Pages **只能放静态文件**——就是那些直接由浏览器打开的文件。

> **此术语需进附录：静态网站**——全部由 HTML/CSS/JS 组成的网站。浏览器拿到这些文件后直接显示给用户看，后端没有程序在处理逻辑。和"动态网站"（有后端处理、连接数据库的网站）相对。

| 能放 | 不能放 |
|------|--------|
| HTML 网页文件 | 后端代码（Python、Java、Go 等需要服务器运行的程序） |
| CSS 样式文件 | 连接数据库进行增删改查 |
| JavaScript 脚本 | 处理用户上传的文件 |
| 图片（JPG、PNG、SVG 等） | 需要操作系统权限的程序 |
| 字体文件 | 实时动态生成的内容（需要后端运算的） |
| 纯数据文件（JSON、CSV） | 需要密码保护的页面 |
| React/Vue 打包后的文件 | 聊天服务器、WebSocket 后端 |

**简单记：** 能放的 = 浏览器能直接打开的东西；不能放的 = 需要服务器运行程序才能产生的东西。

### 免费限额

| 限制项 | 额度 |
|--------|------|
| 每个仓库的网站大小 | 不超过 1 GB |
| 每月流量（带宽） | 100 GB |
| 每小时构建次数 | 最多 10 次 |
| 仓库类型要求 | **必须是 Public（公开仓库）**，私有仓库要付费 |

对我们的教程来说，这些额度远远够用了。

---

## 8.2 三种部署方式——新手只用最简单的

GitHub Pages 支持三种部署方式。作为新手，我们用第一种：

| 方式 | 难度 | 说明 |
|------|------|------|
| **方式一：分支部署** | ⭐ 最简单 | 指定一个分支 + 一个文件夹，GitHub 自动把里面的文件发布成网站 |
| 方式二：Actions 部署 | ⭐⭐ 进阶 | 用 GitHub Actions（第7步学的）自定义部署流程 |
| 方式三：自定义域名 | ⭐⭐⭐ 高级 | 绑定你自己的域名（如 `www.myproject.com`） |

本教程只用**方式一：分支部署，根目录**。三步搞定。

---

## 8.3 实操：发布你的第一个 GitHub Pages 网站

### 前置检查：仓库必须是 Public（公开）

GitHub Pages 的免费版要求仓库是公开的。检查一下：

1. 打开你的仓库页面：`https://github.com/<你的用户名>/my-first-project`
2. 看页面的左上部分。在仓库名字右边有没有一个灰色小标签写着 **"Public"**？

如果有 → 继续下一步。
如果是 **"Private"** → 需要改成 Public：

   1. 点击顶部最右边的 **"Settings"** 标签
   2. 在左侧菜单里往下滚，找到 **"General"**（一般设置），点击它
   3. 一直往下滚动页面，滚到最底部，找到红色背景的区域叫 **"Danger Zone"**（危险区域）
   4. 在 Danger Zone 里找到 **"Change repository visibility"**（修改仓库可见性），点击右边的按钮
   5. 在弹出的确认窗口里，选择 **"Make public"**
   6. 可能会让你输入仓库名确认（在白色输入框里输入 `my-first-project`）
   7. 点击确认按钮

### 第一步：创建 index.html 并推送到 GitHub

你需要在你本地的项目文件夹里创建一个 `index.html` 文件。`index.html` 是网站的"首页"——访问者打开你的网站时，浏览器会自动显示这个文件的内容。

**下面是最详细的操作指南：**

**1. 在文件资源管理器中创建 index.html：**

- 打开文件资源管理器（任务栏上黄色文件夹图标 📁）
- 导航到你的 `my-first-project` 文件夹
- 在文件夹的**空白区域按一下鼠标右键**
- 弹出菜单里，鼠标移到 **"新建"** → 移到 **"文本文档"** → 按左键
- 出现一个新的文本文档，名字是高亮蓝色的。在键盘上输入：

  ```
  index.html
  ```

- **注意：** 输入的是 `index.html`，不是 `index.html.txt`。如果创建后图标还是记事本图标，说明名字实际上是 `index.html.txt`——按键盘 **F2 键**改名，删掉末尾的 `.txt`
- 按 **Enter 键**。如果弹出"更改文件扩展名可能导致文件不可用"——点 **"是"**

**2. 用记事本打开并粘贴 HTML 内容：**

- 在 `index.html` 文件上**按右键** → **"打开方式"** → **"记事本"**
- 记事本打开了，里面是空白的。**把下面的完整内容全部复制粘贴进去：**

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>我的第一个GitHub Pages</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 600px;
            margin: 50px auto;
            padding: 0 20px;
            background-color: #f5f5f5;
            color: #333;
        }
        h1 {
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }
        .success {
            color: #27ae60;
            font-weight: bold;
            background-color: #eafaf1;
            padding: 15px;
            border-radius: 5px;
            border-left: 4px solid #27ae60;
        }
        .info {
            background-color: #ebf5fb;
            padding: 15px;
            border-radius: 5px;
            border-left: 4px solid #3498db;
            margin-top: 15px;
        }
        code {
            background-color: #e8e8e8;
            padding: 2px 6px;
            border-radius: 3px;
            font-size: 0.95em;
        }
    </style>
</head>
<body>
    <h1>Hello, GitHub Pages!</h1>
    <p class="success">部署成功！这是来自 GitHub Pages 的网页。</p>
    <div class="info">
        <p>仓库：<code>github.com/&lt;你的用户名&gt;/my-first-project</code></p>
        <p>如果你能看到这个页面，说明 GitHub Pages 已经在正常运行了。</p>
    </div>
</body>
</html>
```

- 在记事本菜单栏点击 **"文件"** → **"保存"**（或按键盘 Ctrl+S）
- 关闭记事本

**3. 提交并推送到 GitHub：**

回到终端，输入：

```bash
git add index.html
```

按 Enter。

```bash
git commit -m "feat: 添加GitHub Pages首页"
```

按 Enter。

```bash
git push origin main
```

按 Enter。

**4. 验证 index.html 已经在正确位置：**

打开浏览器，访问 `https://github.com/<你的用户名>/my-first-project`。在文件列表中，`index.html` 应该出现在根目录（和其他文件如 `README.md`、`main.go` 并列在一起）。

如果 `index.html` 在某个子文件夹里（比如 `pages/index.html`），那你需要把它移到根目录来。

### ❌ 常见错误：index.html 放错了位置

```
❌ 在项目根目录下创建了一个 pages/ 文件夹，把 index.html 放在了 pages/ 里面
   结果：GitHub Pages 默认读取根目录的 index.html，找不到 → 网站 404

✅ index.html 直接放在仓库根目录（和 README.md、main.go 同级别）
```

### 第二步：在 GitHub 网页上启用 Pages

现在仓库里有 index.html 了，但 GitHub 还不知道你想把它变成网站。你需要手动开启 Pages 功能。

**1. 进入 Settings 页面：**

在 `https://github.com/<你的用户名>/my-first-project` 页面，看页面顶部的标签栏，最右边有一个 **"Settings"** 标签（齿轮图标 ⚙️）。

把鼠标移过去，按一下鼠标左键。

**2. 找到 Pages 设置：**

Settings 页面加载后，你会看到**左侧有一长排菜单**。不同的设置按类别分了组。

往下滚动左侧菜单，找到 **"Code and automation"** 这个分组（分组名字是灰色粗体字）。

在这个分组下面，找到 **"Pages"** 这个菜单项。它在 "Actions" 和 "Environments" 附近。

用鼠标点击 **"Pages"**。

**3. 配置 Pages：**

点击 "Pages" 后，页面右边的内容区域变了。你现在看到的是 GitHub Pages 的配置页面。

在页面中间有一个区域叫 **"Build and deployment"**（构建和部署）。

这个区域下面有两个下拉选择框和一个按钮：

- **Source**（来源）：一个灰色边框的下拉选择框。点击它 → 在弹出的选项中选择 **"Deploy from a branch"**

- **Branch**（分支）：Source 选好之后，下面会出现一个分支选择器。点击下拉框 → 选择 **"main"**

- Branch 选择器右边还有一个目录选择器。点击它 → 选择 **"/ (root)"**（意思是读取 main 分支的根目录里的文件）

- 配置好之后，点击下面的 **"Save"** 按钮

**配置总结：**

| 设置项 | 选择什么 |
|--------|---------|
| Source | Deploy from a branch |
| Branch | main |
| 目录 | / (root) |

点击 Save 后页面会刷新。你现在看到的是 Pages 配置页面。网站还没有立即上线——GitHub 需要一两分钟在后台部署。

### 第三步：等待部署并验证

**1. 等待部署完成：**

点了 Save 之后，等等就行。通常需要 **1 到 2 分钟**。在这期间你可以去喝口水。

**2. 检查部署是否完成：**

刷新 Settings → Pages 页面（按键盘 **F5 键**）。

如果部署成功了，页面顶部会出现一个**蓝色背景的提示框**，里面写着一行文字：

```
✅ Your site is live at https://<你的用户名>.github.io/my-first-project/
```

看到这行蓝色提示框，说明网站已经上线了！

**3. 访问你的网站：**

点击那个蓝色的链接（`https://<你的用户名>.github.io/my-first-project/`），或者在浏览器地址栏里输入这个地址然后按 Enter。

页面加载出来，你应该看到：

- 大标题：**Hello, GitHub Pages!**（深灰色的粗体大字）
- 绿色背景框：**部署成功！这是来自 GitHub Pages 的网页。**
- 蓝色背景框：显示仓库信息

**看到这三个内容，恭喜！你的第一个网站已经正式上线了。** 全世界任何能上网的人都可以通过这个网址看到你的网页。

### 部署失败的三种常见情况

**情况1：Settings → Pages 页面没有蓝色提示框**

等 2 分钟还没有 → 可能是部署失败了。

解决方法：
1. 去仓库的 **"Actions"** 标签页
2. 找到一个叫 **"pages build and deployment"** 的 workflow
3. 看它是不是显示红色 ❌。如果是，点进去看日志
4. 最常见的失败原因：仓库是 Private（私有）的 → 回看本章"前置检查"

**情况2：访问网址显示 404 页面（页面不存在）**

可能的原因和解决方法：

| 原因 | 怎么修 |
|------|--------|
| 部署还没完成 | 再等 2 分钟，刷新页面重试 |
| 仓库是 Private | 改成 Public（见本章"前置检查"） |
| `index.html` 不在根目录 | 检查文件列表，确认 `index.html` 和 `README.md` 在同一个目录层级 |
| Branch 选错了 | 回到 Settings → Pages → Branch → 确认选的是 `main` 和 `/ (root)` |
| 访问的网址写错了 | 确认是 `https://<用户名>.github.io/my-first-project/`，注意是 `.github.io` 不是 `.github.com` |

**情况3：网站能打开但图片显示不出来 / 样式不对**

原因：如果你在 HTML 里用到了图片或 CSS 文件，路径可能写错了。

解决：GitHub Pages 的网址包含仓库名（`/my-first-project/`），所以引用资源时**用相对路径**：
- ✅ `images/logo.png`（相对路径）
- ❌ `/images/logo.png`（绝对路径——在 GitHub Pages 上它会去找 `<用户名>.github.io/images/logo.png`，而不是 `<用户名>.github.io/my-first-project/images/logo.png`）

### 🤔 想多一点：GitHub Pages 背后发生了什么

你可能会好奇：GitHub 怎么做到"把仓库文件变成网站"的？它在后台做了这些事：

1. 你开启 Pages 后，GitHub 在你指定的分支上启动了一个后台构建过程
2. 它把你指定文件夹里的所有文件复制到 GitHub 的 Web 服务器上
3. 分配一个网址：`https://<用户名>.github.io/<仓库名>/`
4. 当有人访问这个网址时，Web 服务器把对应的文件发送到对方的浏览器
5. GitHub 自动提供 HTTPS 加密（就是网址前面那个小锁图标 🔒），你不用自己买 SSL 证书

**这意味着什么：**

- 你每次 `git push` 新代码到 main 分支，网站会**自动更新**（大约等 1 分钟）
- 你不需要维护服务器、不需要配 SSL 证书——GitHub 全包了
- 如果你创建一个特殊名字的仓库：`<你的用户名>.github.io`，网站域名会缩短为 `https://<用户名>.github.io/`（不需要加仓库名）

---

## 8.4 不止是 index.html——你可以放更多

虽然本教程只用了一个 `index.html`，但 GitHub Pages 可以放的远不止这些：

### 能放的东西

- **多个 HTML 页面互相链接**：比如 `about.html`、`contact.html`，访问 `/about.html` 就能看到
- **CSS 样式表**：把样式单独放在 `css/style.css` 里，HTML 中引用
- **JavaScript 脚本**：放在 `js/main.js` 里
- **图片和字体文件**
- **React/Vue 项目打包后的文件**：把构建输出放到仓库里，网站就是整个前端应用

### 多页面网站的目录结构示例

```
my-first-project/             ← 仓库根目录
├── index.html              ← 首页（自动被识别）
├── about.html              ← 关于页面
├── contact.html            ← 联系我们页面
├── css/
│   └── style.css           ← 样式表
├── js/
│   └── main.js             ← JavaScript 脚本
├── images/
│   ├── logo.png            ← 网站 Logo
│   └── banner.jpg          ← 横幅图片
└── README.md               ← 仓库说明（不影响网站）
```

每个 `.html` 文件的访问方式就是在根网址后面加上文件名。比如：
- 首页：`https://<用户名>.github.io/my-first-project/`（自动读取 `index.html`）
- 关于：`https://<用户名>.github.io/my-first-project/about.html`

### 配合 GitHub Actions 做自动构建部署

如果你的项目使用 React、Vue 等前端框架，源代码需要先"构建"（build）才能生成可以部署的 HTML 文件。你可以用第7步学的 GitHub Actions 来自动构建和部署。这个是进阶用法，等你真正用到前端框架时再回来学。

---

## 本章小结

| 知识点 | 一句话要点 |
|--------|-----------|
| GitHub Pages 是什么 | GitHub 免费提供的"把仓库文件变成网站"的服务 |
| 免费域名格式 | `https://<用户名>.github.io/<仓库名>` |
| 能放什么 | HTML、CSS、JS、图片、字体等静态文件（浏览器能直接打开的） |
| 不能放什么 | 后端代码、数据库、动态逻辑（需要服务器运行的） |
| 仓库要求 | 必须是 Public（公开），Private 要付费 |
| 免费额度 | 1GB 空间、100GB/月流量、每小时10次构建 |
| 三种部署方式 | 分支部署（新手）→ Actions 部署（进阶）→ 自定义域名（高级） |
| 创建 index.html | 文件资源管理器 → 右键新建文本文档 → 改名 `index.html` → 记事本打开粘贴 HTML → 保存 |
| index.html 放哪里 | 仓库根目录，和 README.md 同一层级 |
| 启用 Pages 入口 | 仓库 → Settings 标签 → 左侧菜单 "Pages" |
| Pages 三步骤 | Settings → Pages → Source: Deploy from a branch → Branch: main → / (root) → Save |
| 等待时间 | 点击 Save 后等 1~2 分钟 |
| 部署成功标志 | Settings → Pages 页面顶部出现蓝色提示框 "Your site is live at ..." |
| 验证网站 | 浏览器输入 `https://<用户名>.github.io/my-first-project/`，看到标题"Hello, GitHub Pages!" |
| 自动更新 | 每次 push 代码到 main 分支，网站自动更新（约 1 分钟） |
| 常见错误1 | index.html 不在根目录 → 网站显示 404 |
| 常见错误2 | 仓库是 Private → Pages 不可用（免费版要求 Public） |
| 常见错误3 | 没等部署完成就去访问 → 等 2 分钟再试 |
| 常见错误4 | 访问网址写成了 `.github.com` → 应该是 `.github.io` |
| 常见错误5 | 图片/CSS 路径用绝对路径 → 改成相对路径 |

> 🎉 恭喜！这是 Git 到 GitHub 教程系列的最后一章。回顾一下你走过的路：Git 基础（add/commit/push/pull）→ GitHub 仓库创建 → 分支出分支与 PR → Issue 项目管理 → Fork 参与开源 → GitHub Actions 自动化 → GitHub Pages 免费网站。你已经掌握了一个现代开发者最基本的协作工具链。现在，去用它们吧！

---

[← 上一章：步骤7 · GitHub Actions入门](07-GitHub_Actions入门.md)