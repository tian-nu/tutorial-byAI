# Git到GitHub 教程 — 细纲（修订版 v1.1）

> 基于大纲 `git_to_github_outline.md` v1.0
> 修订依据：模拟读者反馈 2026-05-28

---

## 步骤1 · 环境准备与SSH密钥配置

### 1.1 检查Git是否已安装
- 命令：`git --version`
- 预期：输出 `git version 2.xx.xx`
- 未安装？引导到 https://git-scm.com 下载安装（Windows选64-bit Git for Windows Setup）
- 文件路径：无（纯环境检查）
- 术语：无

### 1.2 注册/登录GitHub账号
- 浏览器打开 https://github.com
- 页面右上角 "Sign up" 按钮 → 输入邮箱 → 设置密码 → 设置用户名 → 邮箱验证码
- 关键提醒：用户名会出现在你的仓库URL中（`github.com/你的用户名/仓库名`），选一个专业的
- 术语：无

### 1.3 SSH密钥是什么、为什么需要
- 通俗解释：SSH密钥是一对"锁和钥匙"
  - 公钥 = 锁，放在GitHub上，谁都可以看到（没关系）
  - 私钥 = 钥匙，留在你自己电脑上，绝不能给别人
  - GitHub通过"这把锁能不能被你的钥匙打开"来验证你的身份
- 对比HTTPS：HTTPS每次push/pull都要输密码（或Personal Access Token），SSH配置一次永久免密
- 路径说明：`~/.ssh/` 在不同系统上的位置：
  - Windows：`C:\Users\你的用户名\.ssh\`
  - Mac/Linux：`/home/你的用户名/.ssh/`
- 术语清单：SSH Key、公钥(Public Key)、私钥(Private Key)、HTTPS vs SSH

### 1.4 生成SSH密钥对
- 命令：`ssh-keygen -t ed25519 -C "你的GitHub注册邮箱"`
  - ⚠️ 邮箱必须和GitHub注册时用的邮箱一致！否则GitHub无法识别
  - `-t ed25519`：使用ed25519算法（2024年推荐，比RSA更快更安全）
  - `-C "邮箱"`：添加备注，方便你在GitHub上识别这是哪台电脑的密钥
- 关键操作：一路回车意味着：
  1. "Enter file in which to save the key" → 回车，使用默认路径 `~/.ssh/id_ed25519`
  2. "Enter passphrase" → 建议输入密码（至少8位），或直接回车跳过
     - ⚠️ 设了passphrase 的话，每次用SSH都需要输入这个密码；不设则完全免密但安全性稍低
     - 新手建议：先不设，熟悉后再补
  3. "Enter same passphrase again" → 再输一遍或回车
- 查看公钥：`cat ~/.ssh/id_ed25519.pub`（Windows PowerShell 用 `type $env:USERPROFILE\.ssh\id_ed25519.pub`）
- ⚠️ 粘贴时注意：从 `ssh-ed25519` 开头一直复制到末尾邮箱，整行全部复制，不要漏掉任何字符
- 术语：ed25519、passphrase

### 1.5 将公钥添加到GitHub
- GitHub网页操作详细路径：
  1. 点击页面**右上角你的头像** → 下拉菜单中选 **"Settings"**
  2. 左侧边栏找到 **"SSH and GPG keys"**（在 "Access" 分组下）
  3. 点击绿色 **"New SSH key"** 按钮
  4. Title：随意填，如 "我的笔记本" 或 "My Laptop"
  5. Key：粘贴刚才复制的公钥**完整内容**
  6. 点击 **"Add SSH key"**
- ⚠️ 粘贴后确认：内容以 `ssh-ed25519` 开头，以你的邮箱结尾，中间没有换行

### 1.6 验证SSH连接
- 命令：`ssh -T git@github.com`
  - `-T`：禁止分配终端（因为GitHub不需要你远程登录操作shell，只需要验证密钥）
  - `git@github.com`：这是GitHub的SSH服务器地址，不是你自己的用户名。GitHub用一个统一的 `git` 用户来处理所有SSH连接，然后通过你的公钥识别你是哪个GitHub用户
- 预期输出：`Hi <你的GitHub用户名>! You've successfully authenticated, but GitHub does not provide shell access.`
  - 看到这段话说明成功！后面的"does not provide shell access"是正常的，GitHub不让你远程登录而已
- 常见错误与排错：
  - 首次连接会提示：`The authenticity of host 'github.com' can't be established.` → 输入 `yes` 回车
  - `Permission denied (publickey)` → 公钥没加对。检查：①粘贴是否完整？②邮箱是否和GitHub一致？③有没有多加空格或换行？
  - 深度排查：`ssh -vT git@github.com` 查看详细日志，搜索 `Offering public key` 附近的内容

---

## 步骤2 · 创建你的第一个GitHub仓库

### 2.1 在GitHub网页创建仓库
- GitHub网页操作详细路径：
  1. 登录后，点击页面**右上角头像旁边的 `+` 号** → 选 **"New repository"**
  2. 或直接在左边栏点击绿色的 **"New"** 按钮（Dashboard页面）
- 需解释的字段（从上到下）：
  - Repository name：仓库名，会出现在URL里 `github.com/你的用户名/仓库名`。用英文小写+连字符，如 `my-first-project`
  - Description（可选）：一句话描述项目用途
  - Public vs Private：**新手选 Public**（公开免费，便于后面学Pages和Actions都免费）
  - Add a README file：**本次不勾选**。原因：我们步骤3要从本地推送已有项目，如果勾选会生成初始提交，导致push冲突
  - Add .gitignore：**本次不勾选**。理由同上。什么是 .gitignore —— 告诉Git"这些文件/文件夹不要跟踪"，比如编译产物、依赖包、密钥文件。我们会在步骤3本地手动创建
  - Choose a license：**本次不勾选**。如果不选，你的代码默认"保留所有权利"，别人不能随便用。常见的MIT（最宽松，别人可以做任何事）、GPL（传染性，用了你的代码必须也开源）、Apache 2.0（像MIT但有专利保护）。等需要时再加
- 点击绿色 **"Create repository"** 按钮
- 实操：用户 `tian-nu` 已创建好空的 `test` 仓库，我们以此为目标

### 2.2 三种仓库初始状态对比
- 页面截图描述应呈现的内容：
  - 状态A（完全空白 — 你刚创建的）：页面中央显示"Quick setup"引导，有一串 `git remote add origin ...` 命令等着你复制。**这是我们要的状态。**
  - 状态B（带README）：页面显示README.md的内容渲染，顶部有文件列表。下方有绿色"Code"按钮。
  - 状态C（带README+.gitignore+License）：类似B，但文件列表中有 .gitignore 和 LICENSE。
- 对照表（教程中需以表格呈现）：

| 状态 | 页面特征 | 下一步操作 |
|------|---------|-----------|
| A 完全空白 | 显示"Quick setup"引导区 | 直接 `git remote add` + `git push`（步骤3） |
| B 带README | 有文件列表和README内容 | 先 `git clone` 拉到本地再修改 |
| C 完整模板 | B + .gitignore + LICENSE | 同上，先 clone |

### 2.3 GitHub仓库页面导览
- Code标签（默认显示）：文件列表 + 右侧About区域 + 绿色"<> Code"按钮
  - 重点："<> Code"按钮 → 弹出Clone面板 → 有HTTPS/SSH/GitHub CLI三个Tab
  - 我们要用的是 **SSH** Tab 下的地址（步骤3用）
- Issues标签：Bug追踪和功能讨论
- Pull requests标签：代码审查和合并
- Actions标签：自动化流水线（步骤7用）
- Settings标签：仓库设置入口（步骤1.5、步骤8用）
- 术语：Repository、Clone、License、.gitignore

---

## 步骤3 · 本地项目推送上线

> 目标仓库：`git@github.com:tian-nu/test.git`（SSH地址）

### 3.1 创建本地示例项目
- ⚠️ 注意：在任意位置新建，不要放在现有教程目录里
- 操作：
  ```bash
  cd ~/Desktop          # 或任意你喜欢的目录
  mkdir my-first-project
  cd my-first-project
  ```
- 创建三个文件，教程中直接给出完整内容，读者可复制粘贴：

**文件1：`README.md`**（直接给出完整内容）
```markdown
# My First Project

这是我的第一个GitHub项目！

## 功能
- 输出一句问候语
- 运行 `go run main.go`
```

**文件2：`.gitignore`**（直接给出完整内容，以Go为例）
```
# 编译产物
*.exe
*.test
*.out

# 依赖
vendor/
```

**文件3：`main.go`**（直接给出完整内容）
```go
package main

import "fmt"

func main() {
    fmt.Println("Hello, GitHub!")
    fmt.Println("这是我的第一个GitHub项目！")
}
```

- 目的：有一组真实文件可推送，让读者看到效果

### 3.2 本地初始化Git仓库
```bash
git init
git add .
git commit -m "feat: 初始化项目"
```
- 这时 `git status` 应显示 `nothing to commit, working tree clean`
- 术语：初始化(init)、暂存(add)、提交(commit)

### 3.3 关联远程仓库并推送
- 首先获取远程仓库的SSH地址：
  1. 浏览器打开 `https://github.com/tian-nu/test`
  2. 点击页面上的绿色 **"<> Code"** 按钮（在文件列表上方偏右）
  3. 弹出的面板上方有三个Tab：HTTPS / SSH / GitHub CLI，**点击 "SSH"**
  4. 看到 `git@github.com:tian-nu/test.git`，点击右侧的复制图标
- 关联并推送：
  ```bash
  git remote add origin git@github.com:tian-nu/test.git
  git branch -M main          # 确保分支名是 main
  git push -u origin main
  ```
- 解释：
  - `origin`：远程仓库的别名，"源头"的意思，约定俗成叫origin
  - `main`：主分支名。Git 2.28+ 默认用 `main`，旧版用 `master`——本质一样，只是名字不同
  - `-M main`：强制重命名当前分支为main（如果git init后是master的话）
  - `-u` = `--set-upstream`，设置"上游分支"，之后只需 `git push` 不用加参数
- 验证：浏览器刷新 `https://github.com/tian-nu/test`，看到README.md、.gitignore、main.go三个文件

### 3.4 常见错误与排错
- `remote origin already exists`
  → 已经有origin了。`git remote set-url origin git@github.com:tian-nu/test.git` 修改它
- `failed to push some refs to ...`
  → 远程仓库有你本地没有的提交。`git pull origin main --rebase` 拉取并合并后再push。如果提示冲突，教程中给出冲突解决指引
- `Permission denied (publickey)`
  → SSH没配好，回到步骤1.6重新验证
- `403 Forbidden`
  → 你对这个仓库没有写权限。检查：①是不是把别人的仓库URL地址当成了自己的？②仓库是不是Private且你不是Owner？
- `error: src refspec main does not match any`
  → 本地没有main分支。执行 `git branch` 看当前分支名，如果是 `master`，执行 `git branch -M main` 改名
- 术语：origin、remote、upstream、main/master

---

## 步骤4 · Pull Request 完整流程

> 实操内容：在 `tian-nu/test` 仓库中完整走一遍PR流程（自己给自己发PR）

### 4.1 PR是什么、为什么需要
- PR = Pull Request，请求别人把你的代码"拉"进主分支
- 完整流程：你改好代码 → 发起PR → 别人审查 → 通过后合并到主分支
- 类比：你写了一份报告修改稿，通过系统提交给你的领导，领导在线审阅、批注，最后签字同意合并到正式版本
- PR vs 直接push到main：PR多了一道"审查关卡"，防止错误直接进主分支
- 术语：Pull Request (PR)、Merge Request (MR，GitLab的叫法，一回事)

### 4.2 实操：创建分支→修改→推送→发起PR

**步骤A：创建功能分支**
```bash
git checkout -b feature/add-greeting
```
- 解释：从当前分支（main）分出一条叫 `feature/add-greeting` 的新分支。两个分支此刻内容完全一样，但从现在起你在这个分支上的修改不会影响main

**步骤B：修改代码**
- 打开 `main.go`，在 `func main()` 里添加一行：
  ```go
  fmt.Println("来自 feature 分支的问候！")
  ```
- 修改后的完整 `func main()`：
  ```go
  func main() {
      fmt.Println("Hello, GitHub!")
      fmt.Println("这是我的第一个GitHub项目！")
      fmt.Println("来自 feature 分支的问候！")
  }
  ```

**步骤C：提交并推送**
```bash
git add main.go
git commit -m "feat: 添加问候语功能"
git push -u origin feature/add-greeting
```
- push后终端会显示一个GitHub链接，类似：
  ```
  remote: Create a pull request for 'feature/add-greeting' on GitHub by visiting:
  remote: https://github.com/tian-nu/test/pull/new/feature/add-greeting
  ```

**步骤D：在GitHub网页发起PR**
- 方式一（自动）：push后立即刷新GitHub仓库页面，顶部会出现一个黄色提示条："feature/add-greeting had recent pushes" + 绿色 **"Compare & pull request"** 按钮 → 点击
- 方式二（手动）：进入仓库 → 点击 **"Pull requests"** 标签 → 点击绿色 **"New pull request"** 按钮 → base选 `main`，compare选 `feature/add-greeting` → 点击 **"Create pull request"**

**步骤E：写PR描述**
- 标题：`添加问候语功能`（一句话说清楚改了什么）
- 描述（用模板）：
  ```markdown
  ## 做了什么
  - 在 main.go 中添加了一行问候语输出

  ## 为什么做
  - 练习 Pull Request 流程

  ## 如何测试
  - 运行 `go run main.go`，应该看到新的问候语
  ```

### 4.3 PR页面详解
- PR页面自上而下分四个区域：
  1. **标题和状态**：PR标题 + 状态标签（Open绿色/Merged紫色/Closed红色）
  2. **标签栏**：Conversation / Commits / Checks / Files changed（四个Tab）
  3. **右侧边栏**：Reviewers / Assignees / Labels / Projects / Milestone / Development
  4. **底部**：Merge pull request 按钮（旁边有下拉选择合并策略，见4.5）
- Conversation：所有人可以在这讨论，显示时间线（提交、评论、审查意见）
- Commits：这个PR包含的所有提交记录
- Files changed：红色=删除的行，绿色=新增的行——这就是diff视图
- Reviewers：指定谁来审查代码（输入GitHub用户名）
- Assignees：谁负责处理这个PR（通常是作者自己，默认自动分配）
- Labels：分类标签（bug/enhancement/documentation）

### 4.4 Code Review 流程（含单人模式说明）
- ⚠️ 如果你是一个人（没有团队成员review）：可以自己审查自己
  - 在Files changed标签中，点击行号旁边的蓝色 `+` 号，给自己加一条评论
  - 然后点击绿色 **"Review changes"** 按钮 → 选 **"Approve"** → 提交
  - 团队场景：三种结论：Comment（纯讨论）、Approve（通过）、Request changes（要求修改后重新审查）
- Review后需要修改代码：
  - 本地修改 → `git add` → `git commit` → `git push`（在feature分支上）
  - PR页面自动更新，显示新的提交
- 术语：Code Review、Approve、Request Changes

### 4.5 合并PR + 事后清理
- 点击底部绿色 **"Merge pull request"** 按钮旁的下拉箭头，出现三种策略：
  - **Create a merge commit**（默认）：保留所有提交，新增一个"合并提交"。适合团队，历史完整
  - **Squash and merge**：把所有提交压成一个干净提交 → **新手和小项目推荐！**
  - **Rebase and merge**：变基后合并，历史完全线性。适合追求整洁的团队
- 选择 Squash and merge → 点击 **"Squash and merge"** → **"Confirm squash and merge"**
- 合并后清理本地分支（必须做！）：
  ```bash
  git checkout main
  git pull origin main          # 拉取合并后的最新 main
  git branch -d feature/add-greeting   # 删除本地功能分支
  ```
- 验证：`git log --oneline` 应看到合并后的提交历史
- 术语：Squash、Merge Commit、Rebase、Fast-forward

---

## 步骤5 · Issue 追踪与项目管理

### 5.1 Issue是什么
- Issue = 贴在项目里的"便利贴"：Bug报告、功能请求、待办事项、讨论话题
- 和PR的关系：先有Issue提出需求/报告Bug → 再创建PR来实现/修复 → 合并PR时自动关闭Issue
- 术语：Issue、Bug Report、Feature Request

### 5.2 创建和管理Issue
- 操作路径：仓库页面 → 顶部 **"Issues"** 标签 → 点击绿色 **"New issue"** 按钮
- 标题：一行说清楚（如 `添加用户欢迎页面` 或 `修复首页链接404错误`）
- 描述：教程中提供两种模板——

**Bug报告模板：**
```markdown
## 复现步骤
1. 运行 go run main.go
2. 观察输出

## 预期行为
输出 "Hello, GitHub!"

## 实际行为
输出了乱码

## 环境
- OS: Windows 11
- Go 版本: 1.22
```

**功能请求模板：**
```markdown
## 想要的功能
添加一个显示当前时间的输出

## 为什么需要
用户经常需要查看时间

## 建议实现
在 main.go 中添加 time.Now() 调用
```

- Markdown支持：代码用三个反引号包裹、列表用 `-`、图片直接拖入文本框
- 点击绿色 **"Submit new issue"** 创建

### 5.3 用Label/Milestone/Assignee管理Issue
- **Labels**（右侧边栏 → 齿轮图标）：分类标签，都是可选的（不选也没事）
  - `bug`：确认是Bug | `enhancement`：功能改进 | `documentation`：文档相关
  - `good first issue`：适合新贡献者 | `help wanted`：需要帮助
  - 单人项目建议：至少用 `bug` 和 `enhancement` 区分类型
- **Milestones**（右侧边栏）：把一组Issue/PR归到一个"里程碑"
  - 如 "v1.0上线" 包含5个Issue，完成后关闭这个Milestone
  - 单人项目选填，不做也没事
- **Assignees**（右侧边栏）：指定谁负责
  - 单人项目：默认不填也行，填自己也没毛病

### 5.4 PR联动关闭Issue
- 在PR描述的**任意位置**写 `Closes #1` 或 `Fixes #1`（#1 是Issue编号）
- 大小写不敏感：`closes #1`、`CLOSES #1`、`Fixes #1` 都行
- 但 `close #1` 也行吗？→ 可以，GitHub支持的关键词：`close`、`closes`、`closed`、`fix`、`fixes`、`fixed`、`resolve`、`resolves`、`resolved`
- PR合并后，Issue自动关闭，Issue页面显示 "Closed as completed"
- 实操：创建一个Issue（如"添加时间显示"），然后在PR描述中写 `Closes #X`，合并后观察Issue自动关闭
- 术语：Label、Milestone、Assignee

---

## 步骤6 · Fork：参与开源的正确姿势

> 📊 本步骤涉及跨仓库时序流程 → 对应可视化文件：`pr_fork_visual.html`

### 6.1 Fork vs Clone
- Clone：从远程仓库下载到本地。前提是你对原仓库有"写权限"（你是Owner或被邀请为Collaborator）
- Fork：把别人的仓库完整复制一份到**你自己的GitHub账户**下。你对自己的Fork有完全控制权
- 关键区别：Clone只下载代码，Fork在GitHub上创建了一个新的远程仓库副本
- 类比：Fork = 去图书馆复印了一本书带回家，你在复印件上随意批注。Clone = 借了书只能看不能改（除非你是图书管理员）

### 6.2 Fork实操流程
- 操作详细路径：
  1. 浏览器打开 `https://github.com/tian-nu/test`（原仓库）
  2. 页面右上角，Star按钮左边，找到 **"Fork"** 按钮（旁边有个数字是Fork人数）
  3. 点击Fork → 弹出确认页 → 点击 **"Create fork"**
  4. 等待几秒，页面自动跳转到你账户下的副本：`https://github.com/<你的用户名>/test`
  5. 确认页面左上角显示 `你的用户名/test`，下方有 "forked from tian-nu/test"——说明Fork成功
- Clone你的Fork到本地：
  1. 在你Fork的仓库页面，点击绿色 **"<> Code"** 按钮
  2. SSH Tab → 复制 `git@github.com:<你的用户名>/test.git`
  3. ```bash
     cd ~/Desktop
     git clone git@github.com:<你的用户名>/test.git my-forked-project
     cd my-forked-project
     ```
- 修改代码 → `git add` → `git commit` → `git push`

### 6.3 向上游仓库发起PR
- ⚠️ "上游"（upstream）= 原始仓库（被Fork的那个），即 `tian-nu/test`
- 在你的Fork仓库页面 → 如果刚push，页面顶部会出现提示条 + **"Contribute"** 按钮
- 或手动：点击 **"Pull requests"** 标签 → **"New pull request"** → GitHub自动检测到你的Fork有比原仓库多的提交 → **"Create pull request"**
- 其余流程同步骤4

### 6.4 保持Fork与上游同步（关键操作）
- 为什么需要：原仓库可能在你Fork之后有了新提交，你的Fork会"过时"
- 获取原仓库URL：
  1. 打开原仓库页面 `https://github.com/tian-nu/test`
  2. 点击绿色"<> Code" → SSH Tab → 复制 `git@github.com:tian-nu/test.git`
- 在你的Fork本地目录中：
  ```bash
  git remote add upstream git@github.com:tian-nu/test.git
  git remote -v            # 验证：origin指向你的Fork，upstream指向原仓库
  ```
- 解释每个命令：
  - `git remote add upstream <URL>`：添加第二个远程仓库，别名叫upstream
  - `git fetch upstream`：从原仓库下载**所有**更新（包括新分支、新提交），但**不修改**你当前的代码
  - `git merge upstream/main`：把原仓库main分支上新内容合并到你当前的本地代码
  - `git push origin main`：把合并后的main推送到你自己的Fork仓库
- 定期执行以下命令保持同步：
  ```bash
  git fetch upstream
  git checkout main
  git merge upstream/main
  git push origin main
  ```
- 如果合并有冲突 → 解决方式同步骤4.4
- 术语：Fork、upstream（上游）、downstream（下游）、origin

---

## 步骤7 · GitHub Actions 入门

### 7.1 Actions是什么 + CI/CD 解释
- CI/CD 简单解释：
  - **CI（持续集成）**：每次提交代码，自动跑测试 —— "你的代码有没有把之前的功能搞坏？"
  - **CD（持续交付/部署）**：测试通过后，自动部署到服务器 —— "代码能自动上线吗？"
  - 类比：工厂流水线的质检机器。产品从流水线上经过，机器自动检测有没有瑕疵，合格的自动装箱
- Actions = GitHub内置的CI/CD工具。定义一个workflow文件，GitHub免费提供虚拟机帮你跑
- 免费额度：
  - 公开仓库：完全免费，不限时长
  - 私有仓库：每月2000分钟（约33小时，个人使用绰绰有余）
  - 超出2000分钟：不会自动扣费，但workflow会暂停，需手动升级付费方案（极少需要）
- 术语：CI/CD、Workflow、Job、Step、Runner

### 7.2 手写第一个Workflow（完整可复制代码）
- ⚠️ 如果你的项目没有测试代码怎么办？→ 先用一个"不需要测试"的workflow来练手
- 创建目录和文件：
  ```bash
  # 在项目根目录下
  mkdir -p .github/workflows
  ```
  然后用任意文本编辑器创建 `.github/workflows/hello.yml`，内容：

```yaml
name: Hello GitHub Actions

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  say-hello:
    runs-on: ubuntu-latest
    steps:
      - name: 检出代码
        uses: actions/checkout@v4

      - name: 显示问候
        run: echo "🎉 GitHub Actions 运行成功！提交者是 ${{ github.actor }}"

      - name: 列出文件
        run: ls -la
```

- 逐块解释：
  - `name`：这个workflow在Actions页面显示的名字
  - `on: push: branches: [main]`：当向main分支push时触发。`pull_request`：当有人对main发起PR时触发
  - `jobs`：下面是要执行的任务列表。"say-hello"是任务名（可以改成任意名字）
  - `runs-on: ubuntu-latest`：运行在最新版Ubuntu虚拟机上（GitHub提供）
  - `steps`：按顺序执行。每个step有`name`（显示名）和`run`（要执行的命令）或`uses`（使用别人写好的action）
  - `actions/checkout@v4`：GitHub官方提供的action，把仓库代码下载到虚拟机里（几乎每个workflow的第一步都是它）
- 提交并推送：
  ```bash
  git add .github/workflows/hello.yml
  git commit -m "ci: 添加第一个GitHub Actions"
  git push
  ```

### 7.3 查看运行结果 + 排错
- 浏览器打开仓库 → **"Actions"** 标签（顶部导航栏）
- 左边栏：workflow名称列表（"Hello GitHub Actions"），右边：运行记录
- 点击最新一次运行 → 点击 **"say-hello"** job → 展开看每个step的输出
  - ✅ 绿色对勾 = 该步骤成功
  - ❌ 红叉 = 失败，点击展开看日志
- 常见失败原因与解读：
  - `Permission denied`：workflow没有权限，检查仓库 Settings → Actions → General → Workflow permissions 设为 "Read and write"
  - `command not found: go`：环境里没装Go。如果要跑Go测试，需要加一个 `actions/setup-go@v5` step
  - `No tests found`：项目里没有测试文件。先跳过测试，或写一个简单的测试
- 术语：Workflow、Job、Step、Runner、Action（注意：Action可以指整个GitHub Actions产品，也可以指 `uses` 调用的单个可复用模块）

---

## 步骤8 · GitHub Pages：免费发布网站

### 8.1 Pages是什么
- 把仓库里的HTML/CSS/JS文件变成一个公网可访问的网站
- 免费域名：`https://<你的用户名>.github.io/<仓库名>`
- 适合：项目文档、个人博客、作品集、产品介绍页
- 限制：只能放静态文件（HTML/CSS/JS/图片），不能运行后端代码（Python/Go/Java等）

### 8.2 三种部署方式 → 新手推荐
- **方式一：分支部署**（最简单，本次教程用这个）
  - 指定一个分支（如main）和目录（根目录 `/` 或 `/docs`），GitHub自动把里面的静态文件发布
  - 选根目录 `/ (root)`：直接把 `index.html` 放在仓库根目录即可
  - 选 `/docs`：把文件放在 docs 文件夹里，其他代码不受影响
- **方式二：Actions部署**（进阶）
  - 用步骤7的workflow来做自定义构建（如用Hugo/Jekyll生成静态网站），再部署
- **方式三：自定义域名**
  - 绑定你自己的域名（需额外DNS配置，暂不展开）
- 新手建议：选**方式一 → 分支部署 → 根目录**，3步搞定

### 8.3 实操：发布你的第一个Pages
- **前置检查**：仓库必须是 **Public**（Settings → General → Danger Zone底部可改）
- **第一步：创建页面文件**
  在项目根目录创建 `index.html`，完整内容（直接复制粘贴）：
  ```html
  <!DOCTYPE html>
  <html lang="zh-CN">
  <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>我的第一个GitHub Pages</title>
      <style>
          body { font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; padding: 0 20px; }
          h1 { color: #333; }
          .success { color: #28a745; font-weight: bold; }
      </style>
  </head>
  <body>
      <h1>Hello, GitHub Pages!</h1>
      <p class="success">部署成功！这是来自 GitHub Pages 的网页。</p>
      <p>仓库：<code>github.com/tian-nu/test</code></p>
  </body>
  </html>
  ```
  提交并推送：`git add index.html && git commit -m "feat: 添加Pages首页" && git push`

- **第二步：启用Pages**
  1. 仓库页面 → **"Settings"** 标签（顶部导航栏最右边）
  2. 左侧边栏找到 **"Pages"**（在 "Code and automation" 分组下）
  3. "Build and deployment" → Source：下拉选 **"Deploy from a branch"**
  4. Branch：下拉选 **"main"**，旁边目录选 **"/ (root)"**
  5. 点击 **"Save"**
  6. 页面自动刷新，等待1-2分钟

- **第三步：验证部署**
  1. 回到 Settings → Pages 页面，顶部出现蓝色提示框：`Your site is live at https://tian-nu.github.io/test/`
  2. 点击链接或手动访问 `https://tian-nu.github.io/test/`
  3. 看到网页上的 "Hello, GitHub Pages!" 和绿色"部署成功" → 成功！
- **没有看到蓝色提示框？** 回到Actions标签页，看看是否有一个叫"pages build and deployment"的workflow在运行
- **看到404？** 等1-2分钟，GitHub部署需要时间。如果超过5分钟还是404：
  1. 检查仓库是否为Public
  2. 检查 `index.html` 是否在根目录（不是子文件夹里）
  3. Settings → Pages 里 Branch 是否选了 "main" 而非 "none"
- 术语：GitHub Pages、静态网站、index.html

---

## 附加模块规划

### 术语附录（候选词）
| 术语 | 出现步骤 | 简要解释 | 是否项目特有 |
|---|---|---|---|
| SSH Key / 公钥 / 私钥 | 步骤1 | 锁和钥匙模型，公钥放GitHub，私钥留本地 | 否 |
| ed25519 | 步骤1 | 一种现代SSH加密算法，比RSA更快更安全 | 否 |
| passphrase | 步骤1 | SSH私钥的密码，可选但推荐设置 | 否 |
| HTTPS vs SSH | 步骤1 | 两种Git远程连接方式，SSH免密更安全 | 否 |
| Repository（仓库） | 步骤2 | 一个项目的Git存储空间，包含所有文件和历史 | 否 |
| .gitignore | 步骤2,3 | 告诉Git忽略哪些文件的配置文件 | 否 |
| License（许可证） | 步骤2 | 声明别人可以如何使用你的代码 | 否 |
| origin | 步骤3 | 默认远程仓库别名，通常指向你自己的GitHub仓库 | 否（Git约定） |
| upstream | 步骤6 | 第二个远程仓库别名，指向原始仓库（被Fork的那个） | 否（Git约定） |
| Fork | 步骤6 | 把别人的仓库复制到自己账户下 | 否（GitHub概念） |
| Pull Request (PR) | 步骤4 | 请求合并代码的机制 | 否（GitHub概念） |
| Merge / Squash / Rebase | 步骤4 | 三种合并策略 | 否（Git操作） |
| Code Review | 步骤4 | 代码审查，合并前的检查环节 | 否 |
| Issue | 步骤5 | 任务/Bug/讨论的追踪卡片 | 否（GitHub概念） |
| Label / Milestone / Assignee | 步骤5 | Issue的分类标签、里程碑、负责人 | 否 |
| CI/CD | 步骤7 | 持续集成/持续交付，自动化测试与部署 | 否 |
| Workflow / Job / Step | 步骤7 | GitHub Actions的三级结构：流水线→任务→步骤 | 否 |
| Runner | 步骤7 | 执行workflow的虚拟机 | 否 |
| GitHub Pages | 步骤8 | 从仓库直接托管静态网站的服务 | 否 |
| `~` (tilde) | 步骤1 | 表示用户主目录的简写 | 否 |

### 已知坑点（待写入教程末尾）
- `git push --force` 会覆盖远程历史，团队协作中严禁使用。替代：`git push --force-with-lease`
- Windows CRLF/LF 换行符问题：`git config --global core.autocrlf true`（Windows）或 `input`（Mac/Linux）
- SSH Permission denied 排错四步法：①重读公钥 ②检查GitHub邮箱一致 ③`ssh -vT` 看详细日志 ④确认粘贴无多余空白
- Fork后忘记添加upstream → 你的PR永远落后原仓库，合并时会冲突
- `remote origin already exists` → `git remote set-url` 改地址，或 `git remote remove` 删掉重新加
- Actions触发不了 → 检查 `.github/workflows/` 路径拼写和YAML缩进（只能用空格不能用Tab）
- Pages部署后404 → Public仓库 + main分支 + index.html在根目录 + 等待2分钟

### 可视化
- 文件：`pr_fork_visual.html`
- 对应：步骤6
- 内容：Fork→Clone→修改→Push→向上游发PR→Review→Merge 全流程动画
- 风格：逐步播放，每步高亮当前节点，支持暗色/亮色切换

### 中断点标记
- [可暂停点 1/2]：步骤3结束后 — 用法：`git status` 确认无未提交修改后即可停止。恢复：`cd my-first-project && git status` 确认环境
- [可暂停点 2/2]：步骤5结束后 — 恢复：`git checkout main && git pull origin main`

---

## 自审记录（修订版）

### 每步三问检查
| 步骤 | 做什么清楚？ | 验证方法有？ | 排错指引有？ |
|------|:--:|:--:|:--:|
| 步骤1 SSH | ✅ 含Windows路径和UI路径 | ✅ `ssh -T` | ✅ 三种错误的详细排错 |
| 步骤2 创建仓库 | ✅ 含按钮位置和每个字段建议 | ✅ 页面特征描述 | ✅ 给出默认选择建议 |
| 步骤3 推送上线 | ✅ 含URL获取路径+文件模板 | ✅ 浏览器验证 | ✅ 5种常见错误+具体解决命令 |
| 步骤4 PR流程 | ✅ 含按钮位置+描述模板 | ✅ 合并后git log验证 | ✅ 单人模式说明+事后清理 |
| 步骤5 Issue | ✅ 含两种模板(Bug/功能) | ✅ 创建后可观察 | ✅ 关键词列表 |
| 步骤6 Fork | ✅ 含URL获取+Fork按钮位置 | ✅ 页面变化可观察 | ✅ upstream同步+冲突处理 |
| 步骤7 Actions | ✅ **含完整YAML代码** | ✅ Actions标签页日志 | ✅ 三种失败原因+解读 |
| 步骤8 Pages | ✅ 含完整index.html+UI路径 | ✅ 访问URL验证 | ✅ 404排查清单 |

### 模拟读者反馈修订记录
| 反馈点 | 修订内容 |
|--------|---------|
| 1.4 Windows路径不明确 | 补充`~`在Windows/Mac/Linux上的对应路径 |
| 1.4 passphrase影响不清 | 补充设置与不设置的利弊，给出新手建议 |
| 1.5 Settings入口找不到 | 补充"头像→Settings→SSH and GPG keys"完整路径 |
| 1.6 `-T`和`git@github.com`含义不明 | 补充参数和地址的通俗解释 |
| 2.1 `.gitignore`和License创建时没解释 | 补充创建时就解释，给出新手建议(全不勾选) |
| 2.2 三种状态的具体屏幕特征 | 补充每种的页面描述和下一步操作对照表 |
| 3.1 不知道创建什么文件 | **给出三个文件的完整可复制内容** |
| 3.3 不知道远程URL从哪复制 | 补充"Code→SSH Tab→复制"的完整操作路径 |
| 3.3 `main`和`master`困惑 | 补充`git branch -M main`和名字由来的解释 |
| 4.2 PR按钮在哪 | 补充两种触发方式的详细路径 |
| 4.2 PR描述怎么写 | **给出Markdown描述模板** |
| 4.4 单人没有reviewer | 补充单人自审流程 |
| 4.5 合并后本地怎么处理 | 补充切回main+pull+删除分支的清理步骤 |
| 5.4 `Closes`关键词细节 | 补充完整的关键词列表，说明大小写不敏感 |
| 6.2 Fork按钮位置 | 补充"右上角Star旁边"的定位描述 |
| 6.4 fetch/merge没解释 | 逐命令补充通俗解释 |
| 7.1 CI/CD概念陌生 | 补充CI/CD通俗解释+工厂流水线类比 |
| 7.2 **Workflow没有完整代码** | **给出完整的hello.yml可复制内容+逐块解释** |
| 7.2 `.github`目录不知道怎么创建 | 补充 `mkdir -p` 命令 |
| 8.2 不知道选哪种部署 | 给出新手推荐（分支部署→根目录） |
| 8.3 Settings入口+404排错 | 补充完整路径+404排查三步法 |