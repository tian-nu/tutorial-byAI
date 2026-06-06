# 附录E · Git常用命令速查

> "Git是程序员最基本也是最重要的工具——比任何编程语言都更频繁使用。本附录按场景分类，从日常提交到灾难恢复，覆盖你工作中90%会用到的Git命令。"

---

## E.1 基本操作

| 命令 | 作用 |
|------|------|
| `git init` | 初始化仓库 |
| `git clone url` | 克隆仓库 |
| `git status` | 查看工作区状态 |
| `git add file` | 添加到暂存区 |
| `git add .` | 添加所有变更 |
| `git add -p` | 交互式选择添加 |
| `git commit -m "msg"` | 提交 |
| `git commit -am "msg"` | 添加+提交（仅已跟踪文件） |
| `git push origin branch` | 推送到远程 |
| `git pull origin branch` | 拉取+合并 |
| `git fetch origin` | 拉取（不合并） |
| `git log` | 查看提交历史 |
| `git log --oneline --graph` | 简洁图形化日志 |
| `git diff` | 查看工作区差异 |
| `git diff --staged` | 查看暂存区差异 |
| `git show commit` | 查看某次提交的详情 |

### 提交信息规范

```
[类型] 简短描述

详细描述（可选）
```

常用类型：`feat`（新功能）、`fix`（修复bug）、`refactor`（重构）、`docs`（文档）、`test`（测试）、`chore`（杂项）

---

## E.2 分支操作

| 命令 | 作用 |
|------|------|
| `git branch` | 列出本地分支 |
| `git branch -r` | 列出远程分支 |
| `git branch -a` | 列出所有分支 |
| `git branch name` | 创建分支 |
| `git checkout name` | 切换分支 |
| `git checkout -b name` | 创建并切换 |
| `git switch name` | 切换分支（Git 2.23+） |
| `git switch -c name` | 创建并切换（新语法） |
| `git merge branch` | 合并分支到当前 |
| `git merge --no-ff branch` | 禁止快进合并（保留分支历史） |
| `git branch -d name` | 删除分支 |
| `git branch -D name` | 强制删除分支 |
| `git push origin --delete name` | 删除远程分支 |
| `git stash` | 暂存当前工作 |
| `git stash pop` | 恢复最近暂存 |
| `git stash list` | 查看暂存列表 |
| `git cherry-pick commit` | 把某次提交应用到当前分支 |

### 合并冲突解决

```bash
git merge feature
```

如果冲突，编辑冲突文件，保留需要的代码，删除冲突标记。然后：

```bash
git add .
git commit -m "解决合并冲突"
```

```
<<<<<<< HEAD
当前分支的代码
=======
要合并分支的代码
>>>>>>> feature
```

---

## E.3 撤销操作

| 命令 | 作用 | 危险等级 |
|------|------|---------|
| `git restore file` | 撤销工作区修改 | ⚠ 丢失未提交修改 |
| `git restore --staged file` | 取消暂存 | 安全 |
| `git reset --soft HEAD~1` | 撤销commit，保留修改 | 安全 |
| `git reset --mixed HEAD~1` | 撤销commit+暂存，保留修改 | 安全 |
| `git reset --hard HEAD~1` | 撤销一切，回到上次commit | ⚠⚠⚠ 不可恢复 |
| `git revert commit` | 创建新commit来撤销旧commit | 安全 |
| `git commit --amend` | 修改最近一次commit | 安全（未push时） |
| `git reflog` | 查看所有HEAD移动历史 | 救命稻草 |

### 三种reset的区别（重要！）

| 模式 | HEAD | 暂存区 | 工作区 |
|------|------|--------|--------|
| `--soft` | 回退 | 保留 | 保留 |
| `--mixed`（默认） | 回退 | 回退 | 保留 |
| `--hard` | 回退 | 回退 | 回退（清空） |

`git reflog` 是Git的"后悔药"——即使你执行了 `reset --hard`，只要知道commit hash，还能从reflog里找回来。

---

## E.4 标签

| 命令 | 作用 |
|------|------|
| `git tag` | 列出标签 |
| `git tag v1.0.0` | 创建轻量标签 |
| `git tag -a v1.0.0 -m "msg"` | 创建附注标签 |
| `git tag -d v1.0.0` | 删除本地标签 |
| `git push origin v1.0.0` | 推送标签 |
| `git push origin --tags` | 推送所有标签 |
| `git push origin --delete v1.0.0` | 删除远程标签 |

---

## E.5 远程操作

| 命令 | 作用 |
|------|------|
| `git remote -v` | 查看远程仓库 |
| `git remote add name url` | 添加远程仓库 |
| `git remote remove name` | 移除远程仓库 |
| `git push -u origin branch` | 推送并设置上游 |
| `git push --force` | 强制推送（⚠⚠⚠） |
| `git push --force-with-lease` | 安全强制推送 |
| `git fetch --prune` | 拉取并清理已删除的远程分支 |

`--force-with-lease` vs `--force`：前者在推送前检查远程是否有你不知道的新提交——如果有人在你之后推送了，你的强制推送会被拒绝。这是防止覆盖同事代码的安全网。

---

## E.6 查看历史

| 命令 | 作用 |
|------|------|
| `git log --author="name"` | 按作者过滤 |
| `git log --since="2024-01-01"` | 按日期过滤 |
| `git log -S "keyword"` | 搜索代码变更（内容） |
| `git log -- file` | 某文件的历史 |
| `git blame file` | 逐行查看修改者 |
| `git blame -L 10,20 file` | 查看10-20行的修改者 |
| `git shortlog -sn` | 贡献者统计 |

---

## E.7 配置

| 命令 | 作用 |
|------|------|
| `git config --global user.name "name"` | 设置用户名 |
| `git config --global user.email "email"` | 设置邮箱 |
| `git config --global alias.co checkout` | 设置别名 |
| `git config --list` | 查看所有配置 |
| `git config --global core.editor vim` | 设置编辑器 |

常用别名推荐：

```bash
git config --global alias.co checkout
git config --global alias.br branch
git config --global alias.st status
git config --global alias.lg "log --oneline --graph --all"
git config --global alias.last "log -1 HEAD"
```

---

## E.8 常见工作流

### 功能分支工作流

```bash
git checkout -b feature/new-login
git add .
git commit -m "[feat] 实现新的登录页面"
git push -u origin feature/new-login
```

在GitHub/GitLab上创建Pull Request/Merge Request，代码审核通过后合并。

### 紧急修复工作流

```bash
git checkout main
git pull origin main
git checkout -b hotfix/login-bug
git add .
git commit -m "[fix] 修复登录页面500错误"
git checkout main
git merge hotfix/login-bug
git push origin main
git branch -d hotfix/login-bug
```

---

## E.9 .gitignore 模板（Java项目）

```gitignore
# Maven
target/
pom.xml.tag
pom.xml.releaseBackup
pom.xml.versionsBackup

# IDE
.idea/
*.iml
.vscode/
.project
.classpath
.settings/

# OS
.DS_Store
Thumbs.db

# 环境变量
.env
*.log

# 上传目录
uploads/*
!uploads/.gitkeep

# JVM
*.hprof
```

---

Git是程序员一生中用的最多的工具。熟练使用分支、合并、撤销这些操作，能让你在团队协作中游刃有余。记住：`git reflog` 永远是最后的救命稻草。

---

[← 上一章：附录D-Docker命令速查.md](附录D-Docker命令速查/) | [下一章：附录F-技术术语速查.md →](附录F-技术术语速查/)