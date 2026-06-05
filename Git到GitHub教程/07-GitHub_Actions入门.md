# 步骤7 · GitHub Actions：请个机器人替你跑腿

> 你有没有这种经历：写完代码，忘了跑测试就直接推上去了——然后同事来找你，说你代码把别人的功能搞坏了。或者每次发布新版本，都要手动打包、上传、重启服务器——步骤多到可以写一张清单，每次重复做，烦死人。GitHub Actions 就是来解决这些问题的：它让你把"测试、检查、打包、部署"这些重复的体力活写成一张"任务清单"，每次你推代码，GitHub 就自动帮你执行——从不忘记，从不出错，还免费。

---

## 7.1 用工厂的比喻来理解 CI/CD 和 GitHub Actions

### 没有 CI/CD 的工厂：全靠人肉质检

想象你是一家工厂的质检员。你的工作流程是：

1. 产品从流水线上下来一个
2. 你拿起来，用眼睛仔细检查有没有瑕疵
3. 检查合格 → 放到"合格"箱子里；有瑕疵 → 退回重做

一天检查 50 个，你还能撑住。

现在工厂发展壮大了，一天要检查 5000 个。你一个人检查——会漏、会累、会出错。而且万一你请假了，整个流水线就停了。

### CI/CD 就是流水线上的全自动质检机器

> **此术语需进附录：CI/CD**——持续集成（Continuous Integration）和持续交付/持续部署（Continuous Delivery/Deployment）的合称。

- **CI（持续集成）**：每次有人提交代码，机器自动拉取最新代码、自动跑测试。如果测试不通过，马上通知你。**相当于：质检机会自动检查每个产品，不合格的立刻打回。**
- **CD（持续交付/部署）**：CI 通过之后，机器自动把代码部署到测试环境或生产环境。**相当于：质检合格的产品自动送到打包车间和发货仓库。**

两者合在一起就是：**代码推上去 → 自动测试 → 自动部署。** 全程不需要人动手。

### GitHub Actions 就是 GitHub 送的免费机器人

GitHub Actions 是 GitHub 内置的 CI/CD 服务。你用一张"任务清单"（一个 `.yml` 文件）告诉 GitHub："每次我推代码，请帮我做以下这些事情"。GitHub 就会在每次你 push 代码时，拿出一台**免费虚拟机**，自动执行你的任务清单。

**一个生活化的类比：**

你在家门口贴了一张纸条："每次快递员来了，帮我把包裹放到玄关的柜子里，然后发短信通知我。"

- 这张纸条 = workflow 文件（任务清单）
- 快递员来了 = 触发条件（push 事件）
- 放包裹 + 发短信 = 具体的 job（任务）

GitHub Actions 就是那个帮你自动执行纸条上任务的"机器人管家"。

### 免费额度说明

| 仓库类型 | 免费额度 |
|----------|---------|
| **公开仓库**（Public） | **完全免费，不限量** |
| **私有仓库**（Private） | 每月 2000 分钟（约 33 小时） |

我们用的仓库是公开仓库（如果你按第2章的指导选了 Public 的话），所以完全免费。

你不需要自己买服务器来跑 Actions——GitHub 提供虚拟机（叫 **Runner**）。Runner 上已经装好了常见语言环境（Python、Node.js、Go、Java 等），你直接就能用。

> **此术语需进附录：Runner**——GitHub Actions 中执行 workflow 的虚拟机。GitHub 提供 Ubuntu、Windows、macOS 三种 Runner，免费额度内随便用。

---

## 7.2 创建你的第一个 Workflow 文件

### 什么是 Workflow 文件？

一个 Workflow 文件就是一张"任务清单"。它告诉 GitHub：
1. **什么时候触发**（比如：有人往 main 分支 push 代码的时候）
2. **做什么事**（比如：下载代码 → 显示一条问候 → 列出文件）

Workflow 文件必须放在仓库里的 `.github/workflows/` 文件夹中，文件名以 `.yml` 结尾。

### 第1步：在文件资源管理器中创建文件夹

你需要在你的项目文件夹里创建一个叫 `.github` 的文件夹，然后在里面再创建一个 `workflows` 文件夹。

**下面是最详细的鼠标操作指南：**

1. **打开文件资源管理器**（就是那个黄色文件夹图标 📁——通常在屏幕底部的任务栏上。如果找不到，按键盘上的 Win 键 然后输入"文件资源管理器"，用鼠标点出现的图标）

2. 在文件资源管理器的左侧或顶部地址栏里，找到你的项目文件夹 `my-first-project`。如果你把它放在了桌面，路径大概是：
   ```
   C:\Users\<你的用户名>\Desktop\my-first-project
   ```
   双击 `my-first-project` 文件夹，进入它。

3. 现在你看到的是项目文件夹里的内容。在文件夹里的**空白区域**（不要点在文件上），**按一下鼠标右键**，会弹出一个菜单。

4. 把鼠标移到菜单里的 **"新建"** 上（通常有一个小箭头在旁边，表示还有子菜单）。

5. 子菜单展开后，把鼠标移到 **"文件夹"** 上，按一下鼠标左键。

6. 文件资源管理器里出现了一个新的文件夹，名字是高亮蓝色的，在等待你输入名字。直接在键盘上打出：

   ```
   .github
   ```

   注意：前面有一个英文句号 `.`！这和上一章里你见过的 `.gitignore` 一样，都是隐藏文件夹的命名方式。

7. 按键盘上的 **Enter 键**确认。

8. 如果听到一声警告音或者弹出一个框说"您必须键入文件名"——别慌，再试一次，特别注意 `.github` 最后不要有空格。如果 Windows 不让建以点开头的文件夹，尝试输入 `.github.`（末尾再加一个点），Windows 会自动去掉末尾的点。

9. 创建成功后，**双击** `.github` 文件夹进入。

10. 在 `.github` 文件夹里，重复第 3 到第 7 步——右键 → 新建 → 文件夹 → 输入 `workflows` → 按 Enter。

现在你有了一条路径：`my-first-project/.github/workflows/`。

### 第2步：在 workflows 文件夹里创建 YAML 文件

1. 确保你现在在 `workflows` 文件夹里（文件夹路径应该类似于 `...\my-first-project\.github\workflows`）

2. 在文件夹的空白区域，**按右键** → 移到 **"新建"** → 移到 **"文本文档"** → 按鼠标左键

3. 出现了一个新的文本文档，名字是蓝色的，在等待你输入。在键盘上输入：

   ```
   hello.yml
   ```

   **注意：** 你输入的是 `hello.yml`，**不是** `hello.yml.txt`。如果输入后文件图标变成像一张纸上面有几行字的样式（不是你熟悉的记事本图标），说明成功了。如果还是显示记事本图标，说明文件名实际是 `hello.yml.txt`——按键盘上的 **F2 键**（改名），把末尾的 `.txt` 删掉，改成 `hello.yml` 就行。

4. 按 **Enter 键**确认。可能会弹出一个窗口说"更改文件扩展名可能导致文件不可用"——点 **"是"**。

### 第3步：用记事本打开 hello.yml 并粘贴内容

1. 在刚创建的 `hello.yml` 文件上**按右键**。
2. 在弹出的菜单里，移到 **"打开方式"**（Open with）。
3. 在子菜单里找到 **"记事本"**（Notepad）然后点击。
4. 记事本打开了，里面是空白的。把鼠标在空白处点一下，然后**把下面的完整内容全部复制粘贴进去**：

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
        run: echo "GitHub Actions 运行成功！"

      - name: 列出文件
        run: ls -la
```

5. 检查一下你粘贴的内容是不是和上面完全一样（特别注意缩进——YAML 文件对空格非常敏感）。

6. 在记事本的菜单栏点击 **"文件"** → **"保存"**（或者直接按键盘上的 **Ctrl + S** 快捷键）。

7. 关闭记事本（点右上角的 ✕）。

### 第4步：逐行解释这个 YAML 文件在说什么

刚才你粘贴的那段文字叫做 **YAML**（读作"呀莫"或"呀姆"）格式。它是一种"配置文件"，用来写配置规则。下面逐行解释每一块是什么意思。

> **此术语需进附录：YAML**——一种人类可读的配置文件格式。用缩进（空格）表示层级关系。GitHub Actions 的 workflow 文件就是用 YAML 写的。

**第1行：`name: Hello GitHub Actions`**

这是你给这个 workflow 起的名字。它会在 GitHub Actions 页面上显示出来。你可以改成任何你喜欢的名字。

**第3-7行：触发条件**

```yaml
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
```

`on:` 后面跟的是"什么时候触发这个 workflow"。这里的设置是：
- 当有人向 `main` 分支 **push**（推送）代码时触发
- 当有人向 `main` 分支发起 **pull_request**（拉取请求）时也触发

**第9行：`jobs:`**

`jobs:` 后面跟的是"这个 workflow 里有哪些任务要执行"。一个 workflow 可以包含多个 job（默认会并行执行）。

> **此术语需进附录：Job**——Workflow 中的一个独立任务单元。多个 job 可以并行运行，也可以设置先后顺序串行。

**第10行：`say-hello:`**

这是这个 job 的名字。你随便起。这个名字会显示在 Actions 页面上的 job 列表里。

**第11行：`runs-on: ubuntu-latest`**

告诉 GitHub："给这个 job 分配一台最新版 Ubuntu 系统的虚拟机来执行"。Ubuntu 是一种 Linux 操作系统。

**第12行：`steps:`**

一个 job 里包含多个 step（步骤），按从上到下的顺序依次执行。

> **此术语需进附录：Step**——Job 中的一个执行步骤。一个 job 由多个 step 组成，按顺序执行。每个 step 要么执行一条命令（`run`），要么调用别人写好的 action（`uses`）。

**第13-15行：第一个 step**

```yaml
- name: 检出代码
  uses: actions/checkout@v4
```

- `name:` 是这个 step 的显示名称，会在 Actions 页面上显示
- `uses: actions/checkout@v4` 的意思是"使用 GitHub 官方提供的 `checkout` action，版本 v4"

这个 action 的作用是：**把你的仓库代码下载到虚拟机的当前目录里**。没有这一步，虚拟机打开来是空的——里面啥代码都没有。

> **此术语需进附录：Action**——GitHub Actions 中的可复用步骤单元。类似于编程中的"函数库"，别人封装好了你直接调用。`actions/checkout` 是最常用的 action，用于把仓库代码下载到 Runner 里。

**第16-17行：第二个 step**

```yaml
- name: 显示问候
  run: echo "GitHub Actions 运行成功！"
```

`run:` 后面的内容是**直接在虚拟机的终端里执行的命令**。`echo` 是一条终端命令，意思是"在屏幕上显示一段文字"。

**第18-19行：第三个 step**

```yaml
- name: 列出文件
  run: ls -la
```

`ls -la` 是一条终端命令，意思是"列出当前目录下所有文件的详细信息"。因为第一个 step 已经把代码下载下来了，所以这一步执行后，你会看到你的仓库文件列表。

### 第5步：提交并推送 Workflow 文件

回到你的**终端**（黑底白字窗口），确保你在 `my-first-project` 文件夹里：

```bash
git add .github/workflows/hello.yml
```

按 Enter。这行命令把新建的 workflow 文件加入暂存区。

```bash
git commit -m "ci: 添加第一个 GitHub Actions workflow"
```

按 Enter。提交到本地仓库。

```bash
git push origin main
```

按 Enter。推送到 GitHub。

---

## 7.3 去 GitHub 上看你的自动化流水线跑起来

### 第1步：进入 Actions 页面

1. 打开浏览器，输入你的仓库地址：
   ```
   https://github.com/<你的用户名>/my-first-project
   ```
2. 在仓库名字下面，有一排灰色标签。找到 **"Actions"** 标签（它在"Issues"和"Pull requests"右边），用鼠标点击它

### 第2步：看 Actions 页面的布局

点击"Actions"之后，页面加载出来。你看到的内容分为两个区域：

**左侧：Workflow 列表**
- 显示仓库里所有 workflow 的名字
- 你刚创建的 "Hello GitHub Actions" 应该出现在第一条
- 每个 workflow 名字下面列出了最近的运行记录

**右侧：运行记录详情**
- 显示某次运行的具体信息

因为你的 workflow 触发条件是 `push: branches: [main]`，你推送到 main 分支的那一刻它就自动触发了。

### 第3步：查看运行状态

在左侧 workflow 列表里，找到 **"Hello GitHub Actions"**，它下面应该有一条运行记录。这条记录前面有一个小图标：

- 🟡 **黄色圆点** = 正在运行（排队或执行中）
- ✅ **绿色对勾** = 运行成功，全部通过
- ❌ **红色叉号** = 运行失败，某个步骤出错了

如果图标是黄色圆点，说明还在跑——等几十秒再刷新页面（按键盘上的 **F5 键**）。

如果图标变成了绿色对勾 ✅，说明成功了！**点击这条运行记录**，进入详情。

### 第4步：看运行详情

点击运行记录后，页面右边显示了这次运行的详细信息。

你看到一个叫 **"say-hello"** 的 job（这是你在 YAML 文件里起的名字）。点击它。

页面展开，显示了一串 step 列表。从上到下依次是：

1. **Set up job**（准备环境）—— 系统自动做的，你不管它
2. **检出代码**（`actions/checkout@v4`）—— 下载你的仓库代码到虚拟机
3. **显示问候**（你的 `echo` 命令）—— 输出那段文字
4. **列出文件**（你的 `ls -la` 命令）—— 列出仓库文件
5. **Post 检出代码** —— 系统自动清理
6. **Complete job** —— 任务完成

**点一下"显示问候"这个 step**（把鼠标移过去按左键），它会展开显示这一步的日志输出。你应该能在日志里看到绿色或白色的文字：

```
GitHub Actions 运行成功！
```

同样，**点一下"列出文件"**，展开后你应该能看到类似这样的输出：

```
total 12
drwxr-xr-x  3 runner runner  96 ...
-rw-r--r--  1 runner runner  42 README.md
-rw-r--r--  1 runner runner  68 main.go
```

这就是你仓库里的文件！它们在 GitHub 的免费虚拟机上运行了一遍你的 workflow。

### 第5步：再看看"显示问候"的详细信息

如果你留意到日志中会有这样一行：

```
Run echo "GitHub Actions 运行成功！"
```

这意味着 GitHub Actions 执行的正是你写的 `run:` 命令行。每一行日志你都可以展开看细节。

> **恭喜！你的第一个自动化流水线跑通了。** 每次你 push 代码到 main 分支，这个 workflow 都会自动跑一遍。你什么都不用做——GitHub 的机器人替你做了。

---

## 7.4 排错：Actions 不运行或运行失败怎么办

### 问题1：Actions 标签页里什么都没有（没有运行记录）

**原因：** workflow 文件没有被正确识别，通常是因为文件路径或文件名不对。

**排查步骤：**

1. 打开你的仓库页面 → 点击仓库顶部 **"Code"** 标签 → 在文件列表中你应该能看到 `.github` 文件夹（注意前面有个点）
2. 如果看不到 `.github` 文件夹 → 说明你没有把它推送到 GitHub 上。回到终端，检查：
   ```bash
   git status
   ```
   看 `.github/workflows/hello.yml` 是否被标记为 untracked。如果是，重新执行：
   ```bash
   git add .github/
   git commit -m "ci: 添加 workflow"
   git push origin main
   ```
3. 如果能看到 `.github` 文件夹，点击进入 → 再进入 `workflows` → 确认 `hello.yml` 在里面
4. 确认文件名后缀是 `.yml` 不是 `.yml.txt` 或 `.yaml.txt`

### 问题2：有运行记录但是红色的 ❌

**原因：** workflow 执行过程中某个步骤报错了。

**解决方法：**

1. 点击那条红色的运行记录
2. 点击 `say-hello` job
3. 找到标记了 ❌ 的 step，点开
4. 读里面的错误信息

**最常见的失败原因：**

**"权限不够"** —— 日志里有 `Permission denied` 字样：

解决方法：
1. 仓库页面 → 顶部最右边 **"Settings"** 标签
2. 左侧菜单找到 **"Actions"** → 点击 **"General"**
3. 往下滚动到 **"Workflow permissions"** 部分
4. 选择 **"Read and write permissions"**
5. 点击 **"Save"**
6. 回到 Actions 页面，找到那条失败的记录，点击进入后，右上角有一个 **"Re-run all jobs"** 按钮——点它重新跑

**"找不到某个命令"** —— 日志里有 `command not found`：

这说明虚拟机里没有安装你要用的程序。比如你想用 `python` 但虚拟机里没有 Python。解决方法是在 steps 里加上对应的 setup action：

```yaml
- uses: actions/setup-python@v5
  with:
    python-version: '3.12'
```

GitHub 提供了各种语言的 setup action：`setup-node`、`setup-python`、`setup-go`、`setup-java` 等。

### 问题3：workflow 触发了但"显示问候"步骤显示的内容和预期不一样

这说明你 YAML 文件里的 `run:` 命令写错了。回到本地修改 `hello.yml` → 保存 → `git add` → `git commit` → `git push` → 自动重新触发。

### 🤔 想多一点：Workflow、Job、Step、Action 四个词的关系

这四个词初学者很容易搞混。用一句话记住它们的关系：

> 一个 **Workflow** 包含多个 **Job**，每个 **Job** 包含多个 **Step**，每个 **Step** 可以是一个终端命令（`run`）或者一个 **Action**（`uses`）。

| 层级 | 英文 | 中文翻译 | 通俗类比 |
|------|------|---------|---------|
| 最外层 | Workflow | 工作流 | 一整张"任务清单"（整张纸） |
| 第二层 | Job | 任务 | 清单上的一个大项（如"质量检查"） |
| 第三层 | Step | 步骤 | 大项下的具体操作（如"检查外观""测量尺寸"） |
| 复用单元 | Action | 动作 | 别人写好的步骤模板，拿来即用（类似乐高积木块） |

---

## 7.5 一个更实用的 Workflow 示例

上面那个 `hello.yml` 只是一个"Hello World"级别的演示。下面是稍微实用一点的例子：每次 push 代码，自动检查仓库里有哪些文件。

把 `hello.yml` 的内容替换成下面这个（用记事本打开 `hello.yml`，Ctrl+A 全选，删除，粘贴新内容，保存）：

```yaml
name: Code Check

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - name: 检出代码
        uses: actions/checkout@v4

      - name: 检查文件编码
        run: |
          echo "正在检查仓库文件..."
          file_count=$(find . -type f -not -path './.git/*' | wc -l)
          echo "仓库共有 $file_count 个文件"

      - name: 检查是否有大文件
        run: |
          echo "检查是否有超过1MB的文件..."
          find . -type f -size +1M -not -path './.git/*'
          echo "检查完成"
```

这个 workflow 做了两件稍微有点用的事：
- 统计仓库里有多少个文件
- 检查有没有超过 1MB 的大文件（太大的文件通常不该放在 Git 仓库里）

保存后，执行：

```bash
git add .github/workflows/hello.yml
git commit -m "ci: 更新workflow，添加文件检查"
git push origin main
```

然后去 Actions 页面查看运行结果。

---

## 本章小结

| 知识点 | 一句话要点 |
|--------|-----------|
| CI（持续集成） | 每次推代码自动跑测试，第一时间发现有没有搞坏已有功能 |
| CD（持续部署） | 测试通过后自动部署到服务器，不用人手动操作 |
| GitHub Actions | GitHub 内置的免费 CI/CD 服务，push 代码就自动执行 |
| Workflow | 一张 YAML 格式的"任务清单"，写清楚"什么时候触发、做什么事" |
| 触发条件 `on:` | 最常用的是 `push`（推送时触发）和 `pull_request`（发起PR时触发） |
| Job | Workflow 里的一个独立任务，多个 Job 默认并行跑 |
| Step | Job 里的一个操作步骤，用 `run`（执行命令）或 `uses`（调用 action） |
| Runner | GitHub 提供的免费虚拟机（Ubuntu/Windows/macOS），在上面执行你的任务 |
| Action | 别人封装好的可复用步骤，类似函数库。`actions/checkout` 是最常用的 |
| Workflow 文件放哪 | 仓库里 `.github/workflows/` 目录下，文件名以 `.yml` 结尾 |
| `.github` 文件夹 | 前面有个点，和 `.gitignore` 一样是隐藏文件夹的命名方式 |
| YAML | 一种配置文件格式，用空格缩进表示层级关系 |
| 免费额度 | Public 公开仓库完全免费无限量；Private 私有仓库每月 2000 分钟 |
| 创建 Workflow 的步骤 | 在文件资源管理器新建 `.github/workflows/` 文件夹 → 新建 `xxx.yml` → 粘贴 YAML → 保存 → add/commit/push |
| Actions 页面入口 | 仓库页面顶部标签栏"Actions" |
| 黄色圆点 🟡 | Workflow 正在运行中 |
| 绿色对勾 ✅ | Workflow 运行成功 |
| 红色叉号 ❌ | Workflow 运行失败 → 点进去看哪个 step 报错 |
| 常见失败1 | Workflow 文件路径不对 → 确认在 `.github/workflows/` 下，文件名以 `.yml` 结尾 |
| 常见失败2 | 权限不够 → Settings → Actions → General → 选 "Read and write permissions" |
| 常见失败3 | 虚拟机里没有你要的工具 → 加 `setup-*` action 安装 |

> 🚀 下一步：代码能自动测试了——但测试通过之后呢？如果你只是想让别人看到一个简单的展示页面，买服务器太浪费了。**GitHub Pages** 可以把你的仓库文件免费变成一个公网能访问的网站。这就是第8步要讲的内容。

---

[← 上一章：步骤6 · Fork参与开源](06-Fork参与开源.md) | [下一章：步骤8 · GitHub Pages免费网站 →](08-GitHub_Pages.md)