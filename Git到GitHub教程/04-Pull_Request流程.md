# 步骤4 · Pull Request 完整流程

> "代码写完了，你想把它合进主分支。但万一你写的代码有 Bug 呢？万一同事觉得你的思路不对呢？直接把代码推上 main 分支，就像把自己还没检查过的作业直接交给老师——太冒险了。Pull Request 就是解决这个问题的：它在你和 main 分支之间加了一道审查关卡，你的代码必须先经过审视、讨论、批准，才能合进去。这就像写报告——你在复印件上改，改完提交给领导审阅，领导点了'批准'，复印件才会替换原件。"

---

## 4.1 PR 是什么？为什么要用 PR？

### 一个比喻：写报告

想象你在公司写一份重要的季度报告。有两种做法：

**做法一（不用 PR）：**
你直接在报告的原始文件上改。改完直接保存，原来的内容被覆盖。没人审核你的修改。如果里面有个大错误——比如把"盈利 100 万"错写成了"亏损 100 万"——报告就发出去了，覆水难收。

**做法二（用 PR）：**
你先复印一份报告。在**复印件**上改。改完之后，通过公司的审批系统提交给领导。领导可以：
- 逐行看你的修改
- 在有问题的地方写批注："这里数字不对，请核实"
- 要求你修改后再提交
- 觉得没问题了就点"批准"

只有领导点了"批准"，你的复印件才会替换原始文件。

**Pull Request（简称 PR）就是这个"通过系统提交给领导审阅"的过程。**（此术语需进附录：Pull Request (PR)）

```
你在分支上改代码 → 发起PR（提交审查）→ 审查讨论 → 批准 → 合并到 main 分支
```

### PR 这个名字为什么叫"拉取请求"？

PR 的全称是 Pull Request，直译是"拉取请求"。明明是我要把代码推上去，为什么叫"拉取"？

换个角度就通了：PR 的意思是——"我这边改好了代码，**请你把我的分支拉过去合并到 main**"。你不是在"推送"代码，而是在**请求仓库的维护者把你的修改拉取过去**。

在 GitLab 上，同样的东西叫 **Merge Request（MR，合并请求）**。（此术语需进附录：Merge Request (MR)）名字不一样，干的是一回事。

### PR vs 直接 push 到 main

| 操作 | 直接 push 到 main | 通过 PR 合并 |
|------|-------------------|--------------|
| 审查关卡 | 无，代码直接进入主线 | 有，必须有人 Review |
| 出错后果 | Bug 直接进入生产代码 | 审查阶段就能发现和拦截 |
| 讨论记录 | 无 | PR 页面有完整讨论时间线 |
| 回退难度 | 需要用 git revert | 直接关闭 PR 不合并即可 |
| 适用场景 | 个人随手小项目 | 任何正经项目 |

一句话：**PR 是代码质量的守门员。**

---

## 4.2 实操：建分支 → 改代码 → 推送 → 发起 PR

接下来的操作全部在你的 `<你的用户名>/my-first-project` 仓库中进行（如果你在第2章给仓库起了不同的名字，请替换 `my-first-project`）。因为是个人项目，所以你是"开发者"也是"审查者"——自己给自己发 PR、自己审查自己、自己合并。听起来像自言自语，但流程和团队协作完全一样。

### 步骤A：确认你在正确的文件夹里

打开终端（忘了怎么打开？回头看 3.2 节）。先确认当前在 `my-first-project` 文件夹里。

打字：
```
pwd
```
按 **Enter 键**。（Windows PowerShell 用户用 `Get-Location`）

你应该看到路径末尾是 `my-first-project`。如果不是，用 `cd` 命令进入——回忆一下：`cd $env:USERPROFILE\Desktop\my-first-project`（Windows）或 `cd ~/Desktop/my-first-project`（Mac）。

---

### 步骤B：创建功能分支（`git checkout -b`）

在终端里打字：
```
git checkout -b feature/add-greeting
```
按 **Enter 键**。

**逐词拆解：**
- `git` = 叫 Git
- `checkout` = 切换。可以把它想象成"检出一个版本/分支"。（此术语需进附录：Checkout 检出）
- `-b` = **b**ranch（分支）的缩写。意思是"我要新建一个分支**并且**切换过去"。如果不加 `-b`，`checkout` 只会切换到已存在的分支，不会新建。
- `feature/add-greeting` = 新分支的名字。`feature/` 是前缀，表示这是一个功能分支；`add-greeting` 是这个功能的名字。（此术语需进附录：Feature Branch 功能分支）

> 🤔 分支是什么？（此术语需进附录：Branch 分支）
>
> 用"**平行宇宙**"来比喻最容易理解：
>
> 想象你的代码是一条时间线。在某个时刻，你做了一个"分叉"——分出一条新的时间线。在这条新的时间线上，你可以随便改、随便试、甚至把所有代码删光，**都不会影响原来的时间线**。等你觉得改好了、测试通过了，再把两条时间线"合并"到一起。
>
> ```
> 原始时间线（main）:     A --- B --- C
>                                     \
> 你的分支（feature）:                  D --- E --- F（随便改，不影响 main）
> ```
>
> 分支让你可以**安全地做实验**。做坏了？直接删掉分支，main 毫发无损。做对了？合并回去，main 吸纳你的成果。

**你该看到什么？**

终端会输出：
```
Switched to a new branch 'feature/add-greeting'
```

翻译："已切换到新分支 'feature/add-greeting'。"

怎么验证？打字：
```
git branch
```
按 **Enter 键**。

输出类似：
```
* feature/add-greeting
  main
```

前面带 `*` 号的就是你**当前所在的分支**。看到 `* feature/add-greeting`，说明你的"平行宇宙"已经开启，接下来做的所有修改都在这个分支上，绝不会碰到 main。

---

### 步骤C：修改代码文件

现在来修改 `main.go` 文件，添加一行新代码。

**1.** 用文件资源管理器打开 `my-first-project` 文件夹（桌面 → 双击 `my-first-project` 文件夹）。

**2.** 找到 `main.go` 文件，**鼠标左键双击**打开它。它会用记事本（或你的默认程序）打开。

**3.** 找到 `func main() {` 这一行。在这一行下面，有两行 `fmt.Println(...)`。在**第二行 `fmt.Println("这是我的第一个GitHub项目！")` 的后面**，按键盘上的 **Enter 键**换行，然后在新的一行里打字（注意英文引号）：
```
	fmt.Println("来自 feature 分支的问候！")
```

整个文件改完之后应该长这样（只多了最后那行）：

```go
package main

import "fmt"

func main() {
	fmt.Println("Hello, GitHub!")
	fmt.Println("这是我的第一个GitHub项目！")
	fmt.Println("来自 feature 分支的问候！")
}
```

**4.** 在记事本窗口左上角，点击"**文件**" → "**保存**"，然后关掉窗口。

---

### 步骤D：提交修改

回到终端。打字：
```
git add main.go
```
按 **Enter 键**。

这一次我们没有写 `git add .`（添加全部），而是只添加了 `main.go` 这一个文件。为什么？因为有时候你改了 10 个文件，但只想提交其中 3 个，用 `git add 文件名` 可以精确指定。

然后提交：
```
git commit -m "feat: 添加问候语功能"
```
按 **Enter 键**。

**你该看到什么？**
```
[feature/add-greeting abc1234] feat: 添加问候语功能
 1 file changed, 1 insertion(+)
```

翻译：在 `feature/add-greeting` 分支上做了一次提交，改了 1 个文件，新增了 1 行代码。

---

### 步骤E：推送分支到 GitHub

打字：
```
git push -u origin feature/add-greeting
```
按 **Enter 键**。

**逐词拆解：**
- `git push` = 推送
- `-u` = 设置上游分支（和步骤3一样的意思）
- `origin` = 推送到远程仓库 origin
- `feature/add-greeting` = 推送的是这个分支，而不是 main

> 注意：这次推送的是 `feature/add-greeting` 分支，不是 `main`。推完之后，GitHub 上会同时存在 `main` 和 `feature/add-greeting` 两个分支。

**你该看到什么？**

终端输出类似：
```
Enumerating objects: 5, done.
Counting objects: 100% (5/5), done.
Delta compression using up to 8 threads
Compressing objects: 100% (3/3), done.
Writing objects: 100% (3/3), 345 bytes | 345.00 KiB/s, done.
Total 3 (delta 1), reused 0 (delta 0), pack-reused 0
remote: Resolving deltas: 100% (1/1), completed with 1 local object.
remote:
remote: Create a pull request for 'feature/add-greeting' on GitHub by visiting:
remote:      https://github.com/<你的用户名>/my-first-project/pull/new/feature/add-greeting
remote:
To git@github.com:<你的用户名>/my-first-project.git
 * [new branch]      feature/add-greeting -> feature/add-greeting
branch 'feature/add-greeting' set up to track 'origin/feature/add-greeting'.
```

重点关注输出中间的两行：
```
remote: Create a pull request for 'feature/add-greeting' on GitHub by visiting:
remote:      https://github.com/<你的用户名>/my-first-project/pull/new/feature/add-greeting
```

GitHub 贴心地给了你一个链接——点这个链接就能直接进入创建 PR 的页面。这就是我们下一步要用的。

---

### 步骤F：在 GitHub 网页上发起 PR

现在切换到浏览器。

**方式一（最方便 —— GitHub 自动提示）：**

先**按 F5 键**刷新你的仓库首页（`github.com/<你的用户名>/my-first-project`）。刷新后，注意看页面顶部，有没有出现一个**黄色的横条**，上面写着类似的话：

> `feature/add-greeting had recent pushes 2 minutes ago`

这个黄色横条的右边，有一个**绿色的长方形按钮**，上面写着"**Compare & pull request**"。鼠标左键单击它——直接进入创建 PR 的页面。

> ⚠️ 如果你刷新后没看到黄色提示条，别急，用方式二。

**方式二（手动操作 —— 100% 能找到）：**

**1.** 在仓库页面顶部，找到一排标签（是在文件列表上方，不是在页面最顶上），分别写着：**▦ Code**、**◎ Issues**、**⇄ Pull requests**、**▶ Actions** 等。鼠标左键单击"**Pull requests**"这个标签。

**2.** 页面变成 PR 列表页（目前应该是空的）。在页面右侧偏上位置，有一个**绿色按钮**，上面写着"**New pull request**"。鼠标左键单击它。

**3.** 现在你看到一个"Compare changes"页面。这个页面有两个重要的下拉选择框：
- 左边那个框，前面写着"**base:**"，后面是 `main`。意思是"**目标分支**"——你要把代码合到哪个分支。确保这里选的是 `main`。
- 右边那个框，前面写着"**compare:**"，后面应该自动选好了 `feature/add-greeting`。意思是"**来源分支**"——你的代码在哪个分支。

如果 compare 没有自动选中 `feature/add-greeting`，点击那个框，在展开的列表里找到并点击 `feature/add-greeting`。

**4.** 两个框下面，GitHub 自动显示了两个分支的差异对比。你会看到 `main.go` 文件里新增的那行 `fmt.Println("来自 feature 分支的问候！")` 显示在**绿色背景**上（绿色 = 新增的代码）。

**5.** 确认无误后，点击页面中下方的**绿色大按钮**"**Create pull request**"。

---

### 步骤G：写 PR 描述

点击"Create pull request"后，进入 PR 的描述页面。

**1.** 页面顶部有一个**白色的输入框**，里面可能已经自动填了你的 commit 信息 "feat: 添加问候语功能"。这是 PR 的**标题**——你可以保留它，也可以改成更详细的描述。

**2.** 标题框下面有一个大的**文本框**（灰色的背景），在这里写 PR 的**描述**。鼠标左键在文本框里点一下，然后粘贴下面的模板：

```
## 做了什么
- 在 main.go 中添加了一行问候语输出

## 为什么做
- 练习 Pull Request 流程

## 如何测试
- 运行 `go run main.go`，应该看到新的问候语输出
```

**3.** 页面右侧有一列选项（Reviewers、Assignees、Labels 等），**现在不用管它们**，全部留空。

**4.** 一切就绪后，点击页面中下方的**绿色按钮**"**Create pull request**"。

**🎉 你的第一个 PR 创建好了！**

页面跳转到一个新的网址，浏览器地址栏里显示类似：
```
https://github.com/<你的用户名>/my-first-project/pull/1
```

`/pull/1` 末尾的数字就是你 PR 的编号。每创建一个新 PR，编号自动 +1（下一个是 #2，再下一个是 #3...）。

---

### 我做得对不对？——验证

- 浏览器地址栏显示 `github.com/<你的用户名>/my-first-project/pull/1`（或 /pull/2、/pull/3...）
- 页面顶部显示你的 PR 标题
- 标题右边有一个**绿色的圆角小方块**，里面写着"**Open**"
- 页面下方显示着代码改动，新增的那行 `fmt.Println("来自 feature 分支的问候！")` 在绿色背景上
- 右侧边栏的 Assignees 栏目可能自动填了你的用户名

全部满足 = PR 创建成功。

---

## 4.3 PR 页面详解

PR 页面上的信息很多。从头到尾走一遍，把每个区域搞清楚。

### 区域一：顶部 —— 标题和状态

页面最顶部是 PR 的**标题**（大写加粗字体）。标题右边有一个**状态标签**（一个圆角小色块）：

| 状态标签颜色 | 文字 | 含义 |
|------------|------|------|
| **绿色** | Open | PR 正在讨论中，尚未合并或关闭 |
| **紫色** | Merged | PR 已被合并，改动已进入 main 分支 |
| **红色** | Closed | PR 被关闭了，但**没有**合并（被拒绝或放弃）|

标题下方有一行小字，显示：谁发起的 PR、想合并到哪个分支、从哪个分支来。比如：
> `你的用户名` wants to merge 1 commit into `main` from `feature/add-greeting`

### 区域二：标签栏（Conversation / Commits / Checks / Files changed）

标题下方有一排**四个灰色标签**：

| 标签 | 英文 | 功能 |
|------|------|------|
| **对话** | Conversation | 讨论区。审查者在这里提问、评论，你在这里回复。所有对话按时间线排列。这是 PR 的核心交流区域。 |
| **提交** | Commits | 列出这个 PR 包含的所有 commit。每个 commit 点进去能看到改了哪些文件。 |
| **检查** | Checks | CI/CD 测试结果。如果配置了 GitHub Actions（步骤7会讲），每次 push 自动运行的测试结果显示在这里。绿色 ✓ = 通过，红色 ✗ = 失败。 |
| **文件变更** | Files changed | 展示所有被修改的文件。红色背景 = 删除的行，绿色背景 = 新增的行。这是审查代码的核心页面。 |

### 区域三：右侧边栏（从上到下）

PR 页面的**右侧竖排**有一列选项：

- **Reviewers（审查者）**：（此术语需进附录）指定谁来审查代码。点击旁边的齿轮图标，输入 GitHub 用户名指定。单人项目可以为空。
- **Assignees（负责人）**：这个 PR 归谁负责。通常默认是自己。
- **Labels（标签）**：给 PR 贴分类标签（比如 `bug`、`feature`、`documentation`），方便筛选。
- **Projects（项目看板）**：关联到 GitHub Projects 看板。单人项目暂时用不到。
- **Milestones（里程碑）**：关联到某个版本目标（比如 `v1.0`）。
- **Development（开发关联）**：关联某个 Issue（步骤5会讲），PR 合并后自动关闭对应的 Issue。
- **Notifications（通知）**：设置是否接收这个 PR 的通知邮件。

### 区域四：底部合并区域

页面向下滚动，在Conversation标签页的最底部（所有讨论内容的下方），有一个大的**绿色按钮**，写着"**Merge pull request**"。这个按钮的右边有一个**向下的小三角箭头（▾）**——点击它可以切换合并方式。具体的三种合并方式在 4.5 节讲。

按钮上方有一行检查结果。如果状态是绿色的勾旁边写着"All checks have passed"或"此分支没有冲突"，说明可以安全合并。

### 🤔 想多一点：Files changed 为什么这么重要？

Files changed 是 PR 审查的核心战场。它不只是一张"改了什么"的清单——审查者的工作就是**逐行阅读这里的所有改动**。

GitHub 用 **diff 格式**展示改动（此术语需进附录：Diff 差异对比）：
- 红色行前面有红色的 `-` 号 = 被删除的代码（旧版本）
- 绿色行前面有绿色的 `+` 号 = 新增的代码（新版本）

例如你这次的 PR，在 Files changed 里会看到：
```diff
  func main() {
      fmt.Println("Hello, GitHub!")
      fmt.Println("这是我的第一个GitHub项目！")
+     fmt.Println("来自 feature 分支的问候！")
  }
```

只有最后一行前面有绿色的 `+` 号——这正是你新增的那行代码。

---

## 4.4 Code Review（代码审查）

### 单人模式：自己审查自己

你是自己的审查者。虽然听起来有点滑稽——自己写的代码有什么好审的？——但这个过程强迫你**把改动重新看一遍**，很多低级错误就是在这个"重新审视"时被发现的。

操作步骤（全程在网页上操作）：

**1. 进入 Files changed 页面**

在 PR 页面的标签栏里，鼠标左键单击"**Files changed**"。

**2. 逐行审阅改动**

现在你看到的就是你改动前的代码（红色背景）和改动后的代码（绿色背景）的对比。一行一行看过去。

**3. 添加行级评论**

如果你对某一行的代码有想法（比如"这里的变量名字可以改得更清晰"），把鼠标移到那一行的**行号**（左侧的数字）上，会出现一个**蓝色的小加号 ⊕**。鼠标左键单击它。

一个文本框弹出来。在文本框里用键盘打字，写下你的看法。然后点击文本框下方的绿色"**Start a review**"按钮——评论就被记录下来了。

**4. 提交审查结论**

看完所有文件后，看 Files changed 页面的**右上角**，有一个绿色的按钮写着"**Review changes**"，鼠标左键单击它。

弹出一个面板，上面有一个大文本框（可以写审查总结），下面有三个**单选项**：

| 选项 | 英文 | 含义 |
|------|------|------|
| **评论** | Comment | 我只是说几句，不表态通过还是不通过 |
| **批准** | Approve | 我认为代码没问题，可以合并 |
| **要求修改** | Request changes | 代码有问题，必须先修改，改完再给我看 |

**5. 选择"批准"**

鼠标左键单击"**Approve**"前面的圆形单选框（让它变成选中状态）。然后在上面的大文本框里，用键盘打字输入：
```
LGTM! (Looks Good To Me)
```
这是开发者社区的常用缩写，意思是"我看过了，看起来没问题"。

**6. 提交审查**

点击面板底部的绿色"**Submit review**"按钮。

审查通过后，回到 PR 的 Conversation 页面，你会发现 Merge 按钮旁边出现了一个**绿色的勾号 ✓**，旁边写着一个绿色的小字"1 approval"——表示"有一个人审查通过了"。

---

### 团队场景：三种审查结论（供参考）

在实际团队中，审查者可以做出三种结论。虽然你现在是单人操作，了解这些对将来有帮助：

| 结论 | 含义 | 后果 |
|------|------|------|
| **Comment** | 我有话要说，但不表态通过还是拒绝 | 不影响合并状态 |
| **Approve** | 我认为代码没问题，可以合并 | PR 获得一个批准标记 |
| **Request changes** | 代码有问题，必须先修改 | PR 被"锁定"，修改完成前不能被合并 |

大多数团队要求 PR **至少获得一个 Approve** 才能合并。大项目可能要求两个或更多。

---

### 如果审查发现了问题怎么办？

如果你（或你模拟的"审查者"）发现了问题，需要修改代码——**不要关闭 PR 重建！** PR 的最大好处就是"改完自动更新"。

**步骤：**

1. **确保本地还在那个分支上**——在终端里打字：
```
git checkout feature/add-greeting
```
按 **Enter 键**。

2. **在文件资源管理器里打开 `main.go`，修改代码**（比如改一下问候语的措辞）。

3. **保存后，在终端里提交**：
```
git add main.go
git commit -m "fix: 根据审查意见修改问候语措辞"
```
按 **Enter 键**。

4. **推送**（这次不需要 `-u` 了，因为之前已经绑定过上游分支）：
```
git push
```
按 **Enter 键**。

5. **回到浏览器，刷新 PR 页面**（按 F5）。你会发现新的 commit 已经自动出现在 Conversation 时间线里——PR 会自动包含同一分支上的所有新提交，**完全不需要重新发起 PR**。

这就是 PR 工作流的美妙之处：修改 → commit → push → PR 自动更新 → 审查者再看，全程无缝衔接。

### ❌ 错误做法 vs ✅ 正确做法

```
❌ 错误：发现审查意见后，关掉旧 PR，创建新分支，重新发起新 PR
   问题：讨论记录丢失、浪费时间、把简单事搞复杂了

✅ 正确：在原 feature 分支上修改 → commit → push，PR 自动更新
   好处：讨论记录连续完整，审查者能看到"上次提的问题这次怎么改的"
```

```
❌ 错误：为了省事，直接在 main 分支上修改然后 push
   问题：绕过了 PR 审查，代码不经审查就进了主分支——PR 的整个意义就没有了

✅ 正确：始终在 feature 分支上修改，通过 PR 合并
   好处：每一次改动都有审查记录，任何人打开 PR 页面都能追溯改动历史
```

---

## 4.5 合并 PR + 事后清理

### 三种合并策略

现在 PR 已经审查通过、准备合并了。点击 Merge 按钮**右边的小三角箭头（▾）**，弹出一个下拉菜单，GitHub 提供三种合并方式：

| 策略 | 按钮上的文字 | 效果 |
|------|-------------|------|
| **创建合并提交** | Create a merge commit | 创建一个专门的"合并提交"，完整保留分支的所有提交历史 |
| **压缩合并**（推荐新手） | Squash and merge | 把 PR 里的所有 commit 压缩成一个干净的提交 |
| **变基合并** | Rebase and merge | 把 PR 的 commit 搬到 main 最新位置，形成一条完美的直线 |

（此术语需进附录：Merge 合并 / Squash 压缩 / Rebase 变基）

下面用图形解释每种策略的区别。

**策略一：Create a merge commit（创建合并提交）**

```
合并前:
main:    A --- B --- C
              \
feature:       D --- E --- F（你的3个commit）

合并后:
main:    A --- B --- C ------- M（M是"合并提交"，把两条线连在一起）
              \              /
feature:       D --- E --- F
```

- 优点：完整保留开发历史，不会丢失任何信息
- 缺点：分支多了之后历史看起来是一张复杂的"网"，不太清爽
- 适合：多人协作的大型团队，需要追溯"这个功能谁什么时候开发的"

**策略二：Squash and merge（压缩合并 —— 新手强烈推荐！）**

```
合并前:
feature 上有 3 个 commit:
  D: "初稿——加了个问候语"
  E: "修复——发现打错字了"
  F: "调整——改了措辞"

合并后:
main 上只多了一个 commit:
  "feat: 添加问候语功能"（包含了 D+E+F 的所有改动，但历史记录只有一条）
```

- 优点：main 分支的历史极其干净，每个 PR 对应一个 commit，一目了然
- 缺点：feature 分支上的小 commit 细节在 main 上看不到了（但 feature 分支本身还在，需要的时候可以回去查）
- 适合：个人项目、小团队、追求干净历史的人

**策略三：Rebase and merge（变基合并）**

```
合并后:
main:    A --- B --- C --- D' --- E' --- F'
（D/E/F 被"搬"到了 C 之后，仿佛它们本来就是接着 C 写的）
```

- 优点：历史完全是一条直线，没有任何分叉
- 缺点：操作相对复杂，对 rebase 不熟悉的话容易出问题
- 适合：对历史整洁度有极致追求的团队

---

### 合并操作（用 Squash and merge）

**1.** 在 PR 页面底部，点击 Merge 按钮**右边的小三角箭头（▾）**。

**2.** 在弹出菜单里，鼠标左键单击"**Squash and merge**"。

**3.** 页面刷新，Merge 按钮变成了"**Squash and merge**"。按钮上方出现一个文本框，里面自动填好了压缩后的 commit 信息。通常保持默认即可。

**4.** 点击**绿色按钮**"**Confirm squash and merge**"。

**5.** 合并完成！页面顶部原来的"Open"状态标签变成了**紫色的"Merged"**标签。页面中间出现一个大大的紫色图标（一个合并符号），下面写着"Merged"。

**6.** 紧接着，页面中间出现一个提示框，上面有一个**灰色按钮**写着"**Delete branch**"——这是问你要不要删除远程的 `feature/add-greeting` 分支。鼠标左键单击它。这个分支的使命已经完成了（代码已合并到 main），留着只会让仓库分支列表越来越长。

> ⚠️ 删除的是**GitHub 上的远程分支**，你本地的分支还在。下面我们清理本地。

---

### 合并后清理本地分支

回到终端。依次执行三条命令：

**命令1：切换回 main 分支**

打字：
```
git checkout main
```
按 **Enter 键**。

输出类似 `Switched to branch 'main'`。你现在回到了主分支。

**命令2：把 GitHub 上合并后的最新代码拉到本地**

打字：
```
git pull origin main
```
按 **Enter 键**。

（如果你之前设过 `-u` 上游分支，直接打 `git pull` 也可以）

你该看到类似输出：
```
From git@github.com:<你的用户名>/my-first-project
 * branch            main       -> FETCH_HEAD
Updating abc1234..def5678
Fast-forward
 main.go | 1 +
 1 file changed, 1 insertion(+)
```

这表示 main 分支已经更新了——那行新增的问候语代码现在在 main 里了。

**命令3：删除本地的 feature 分支**

打字：
```
git branch -d feature/add-greeting
```
按 **Enter 键**。

输出类似 `Deleted branch feature/add-greeting (was abc1234).`

**逐词拆解：**
- `git branch` = 操作分支
- `-d` = **d**elete（删除）。**小写 d** 是安全删除——如果这个分支还没被合并，Git 会拒绝删除并警告你"这个分支的代码还没合并到别处，确定要删吗？"
- 如果用大写 `-D`，则是**强制删除**——不管合没合并，直接删。

---

### 验证合并结果

**验证1：看分支列表**

打字：
```
git branch
```
按 **Enter 键**。

应该只看到：
```
* main
```
（`feature/add-greeting` 已经不在了）

**验证2：看提交历史**

打字：
```
git log --oneline
```
按 **Enter 键**。

应该看到类似：
```
abc1234 feat: 添加问候语功能 (#1)
def5678 feat: 初始化项目
```

注意两点：
- Squash and merge 之后，你在 feature 分支上的零碎 commit 被压缩成了**一条干净记录**
- 提交信息末尾的 `(#1)` 是 GitHub 自动加上的 PR 编号，方便以后追溯"这个改动是从哪个 PR 来的"

**验证3：看代码内容**

打字：
```
cat main.go
```
按 **Enter 键**。（Windows PowerShell 用 `type main.go` 或 `Get-Content main.go`）

终端会打印出 `main.go` 的全部内容。你应该看到三行 `fmt.Println`——包括你在 feature 分支上新增的那行。这说明合并成功了。

### 如果忘了清理分支会怎样？

短时间不清理没事。但一个月后，你可能积累了十几个 `feature/xxx`、`bugfix/yyy`、`experiment/zzz` 分支，每个都已合并，`git branch` 一列出来——自己都分不清哪些还有用、哪些已是历史遗物。这就是**分支垃圾**。

养成习惯：**PR 合并后立刻删除远程和本地分支。**

---

## 🤔 想多一点：为什么 PR 这么重要？

如果你回头看一遍这个流程——建分支、改一行代码、commit、push、开 PR、自己审自己、选 squash and merge、然后清理分支——你可能会觉得："就改了一行代码，搞这么复杂？"

这个疑问很合理。但你试着把场景放大：

- 不是改一行，而是改了 **200 个文件，5000 行代码**
- 不是你一个人，是**三个人同时在一个项目上写代码**
- 不是个人项目，是**一个 1000 万用户的产品**

在这种场景下，PR 的价值就显现出来了：

1. **隔离风险**：每个人的改动在各自的分支上，互不干扰。你的代码不会搞崩别人的代码。
2. **强制审查**：每个改动进入 main 之前，至少要经过一个人（甚至多人）的眼睛。一个团队一年产出的数万行代码，每一行都有人看过。
3. **可追溯**：任何一段代码，通过 `git blame` 都能找到是哪个 PR 引入的，再通过 PR 找到当时的讨论——"当初为什么这么写"这个终极问题，有据可查。
4. **自动化卡口**：CI/CD 在合并前自动运行测试，不通过的代码根本进不了 main。

**PR 不是"一行代码的繁文缛节"，而是"一万行代码的安全带"。**

---

## 本章小结

| 知识点 | 要点 |
|--------|------|
| PR 是什么 | "请把我的分支拉过去合并到 main"的请求，代码审查的载体 |
| 分支（Branch）| 代码的"平行宇宙"，在新分支上改代码不影响 main |
| `git checkout -b 分支名` | 新建一个分支并切换过去；`-b` = 同时新建和切换 |
| `git branch` | 查看所有本地分支，前面带 `*` 的是当前分支 |
| `git push -u origin 分支名` | 把新分支推送到 GitHub；`-u` 设置上游 |
| 发起 PR（方式一）| push 后刷新仓库首页 → 黄色提示条 → 绿色"Compare & pull request"按钮 |
| 发起 PR（方式二）| Pull requests 标签 → 绿色"New pull request"按钮 → base 选 main → compare 选 feature 分支 |
| PR 标题和描述 | 标题说明改了什么；描述用模板说明做了什么、为什么、怎么测试 |
| PR 状态 | Open（绿色）= 讨论中；Merged（紫色）= 已合并；Closed（红色）= 已关闭未合并 |
| Conversation | PR 的讨论区，所有评论按时间线排列 |
| Commits | 列出这个 PR 包含的所有 commit |
| Checks | CI/CD 运行结果，绿色 ✓ 通过 / 红色 ✗ 失败 |
| Files changed | 代码改动的核心页面，红删绿增，逐行审查 |
| 添加行级评论 | 鼠标移到行号上 → 蓝色 ⊕ → 写评论 → Start a review |
| Review changes | 右上角绿色按钮；Comment / Approve / Request changes 三种结论 |
| LGTM | "Looks Good To Me"的缩写，审查通过的常用表达 |
| 修改后更新 PR | 在原分支改代码 → commit → push，PR 自动更新，**不需要重建 PR** |
| 三种合并策略 | Merge commit（保留全历史）/ Squash and merge（压成一个提交）/ Rebase and merge（线性历史）|
| Squash and merge | 推荐新手和个人项目，main 历史干净，每个 PR 一条记录 |
| 合并后清理（远程）| 合并成功 → 页面中间提示框 → 点击"Delete branch"删除远程分支 |
| 合并后清理（本地）| `git checkout main` → `git pull` → `git branch -d feature/分支名` |
| 分支垃圾 | 合完不删旧分支，时间一长仓库混乱——养成每次合完就清理的习惯 |

> 🚀 下一步：步骤5 · Issue 追踪与项目管理。代码改好了、PR 合并了——但等等，你当初为什么要改这段代码？是谁提的需求？改完之后解决了什么问题？一个正经项目不能只靠脑子记这些。Issue 就是 GitHub 给你的"项目记忆系统"。

---

[← 上一章：步骤3 · 推送项目上线](03-推送项目上线.md) | [下一章：步骤5 · Issue追踪与项目管理 →](05-Issue与项目管理.md)