# 108-Linux必备知识

> 💡 你的 Spring Boot 应用在本地跑得好好的。现在你要把它部署到服务器上——你租了一台"远程电脑"，但发现它没有桌面、没有鼠标、不能双击图标。这就是 Linux 服务器的日常：一切靠命令行。本章不会把你变成运维大神，但能让你从容地 SSH 登录服务器、装软件、看日志、杀进程——这是每个后端程序员的生存技能。

---

## 本章目标
- 理解 Linux 是什么，为什么服务器都用它
- 用 SSH 登录远程服务器
- 掌握最常用的 25 个命令
- 能用 vim 编辑文件（不迷路、不崩溃）
- 管理文件权限和进程

---

## 108.1 Linux 是什么

Linux 是一个**操作系统内核**。你平时听到的 Ubuntu、CentOS、Debian 是"Linux 发行版"——在内核之上打包了工具、包管理器、桌面环境等。

```
Windows          macOS            Linux
  有桌面           有桌面          有桌面版(但服务器不装)
  GUI为主          GUI为主         CLI为主(服务器)
  .exe             .dmg/.app       包管理器
```

服务器 99% 用 Linux 的原因：免费、稳定、资源占用小、生态完善。

### 你需要知道的主流发行版

| 发行版 | 包管理器 | 常见场景 |
|--------|----------|----------|
| Ubuntu | `apt` | 个人服务器、学习首选 |
| CentOS Stream | `yum`/`dnf` | 企业（Red Hat 系） |
| Debian | `apt` | 稳定性要求高的场景 |
| Alpine | `apk` | Docker 镜像（超轻量） |

> ⚠️ 本教程统一使用 **Ubuntu 22.04 LTS** 作为服务器操作系统。

---

## 108.2 SSH——连接远程服务器

### 什么是 SSH

SSH = Secure Shell，一个加密协议，让你安全地操作远程电脑的命令行。

### 连接命令

```bash
ssh username@your_server_ip
```

实际示例：

```bash
ssh root@123.45.67.89
```

第一次连接会看到：

```
The authenticity of host '123.45.67.89' can't be established.
ECDSA key fingerprint is SHA256:xxxxxxxxxxxxx.
Are you sure you want to continue connecting (yes/no)?
```

输入 `yes` 回车。这是正常的安全确认，只需要做一次。

### 使用密钥登录（更安全）

在**你自己的电脑**上生成密钥对：

```bash
ssh-keygen -t ed25519 -C "your_email@example.com"
```

一路回车即可。然后把公钥复制到服务器：

```bash
ssh-copy-id username@your_server_ip
```

此后登录不再需要密码。

### 验证方法

```bash
ssh username@your_server_ip "whoami && hostname"
```

如果能输出你的用户名和服务器主机名，说明 SSH 正常工作。

---

## 108.3 最常用的 25 个命令

### 导航类

| 命令 | 作用 | 示例 |
|------|------|------|
| `pwd` | 显示当前目录 | `pwd` → `/home/ubuntu` |
| `ls` | 列出文件 | `ls -la` 显示隐藏文件和详情 |
| `cd` | 切换目录 | `cd /var/log` |
| `cd ..` | 返回上级 | — |
| `cd ~` | 回到用户家目录 | — |

### 文件操作类

| 命令 | 作用 | 示例 |
|------|------|------|
| `cat` | 查看文件内容 | `cat app.log` |
| `less` | 分页查看（可上下滚动） | `less app.log`，按 `q` 退出 |
| `tail` | 查看文件末尾 | `tail -f app.log` 实时追踪 |
| `head` | 查看文件开头 | `head -20 app.log` |
| `cp` | 复制 | `cp a.txt b.txt` |
| `mv` | 移动/重命名 | `mv old.txt new.txt` |
| `rm` | 删除 | `rm file.txt` |
| `rm -rf` | 强制递归删除 | **极度危险，三思后用** |
| `mkdir` | 创建目录 | `mkdir -p /opt/myapp/logs` |
| `touch` | 创建空文件/更新时间戳 | `touch app.log` |

### 权限类

| 命令 | 作用 | 示例 |
|------|------|------|
| `chmod` | 修改权限 | `chmod +x start.sh` 添加执行权限 |
| `chown` | 修改所有者 | `chown ubuntu:ubuntu app.jar` |

### 系统信息类

| 命令 | 作用 | 示例 |
|------|------|------|
| `top` | 实时进程监控 | 按 `q` 退出 |
| `df -h` | 磁盘使用情况 | 看 `Avail` 列 |
| `free -h` | 内存使用情况 | — |
| `ps aux` | 列出所有进程 | 常配合 `grep` |
| `grep` | 文本搜索 | `grep "ERROR" app.log` |
| `find` | 查找文件 | `find / -name "*.jar"` |
| `systemctl` | 管理服务 | `systemctl status nginx` |
| `curl` | 发送 HTTP 请求 | `curl http://localhost:8080/health` |

### 重要组合技

```bash
ps aux | grep java              # 找到所有Java进程
tail -f app.log | grep ERROR    # 实时看错误日志
find /opt -name "*.log" -mtime +7 -delete  # 删除7天前的日志
```

---

## 108.4 vim 逃生指南

`vim` 是 Linux 上最常用的文本编辑器。它最大的"坑"是：**它有模式，新手进去不知道怎么退出。**

### 你在做什么？
你需要修改服务器上的配置文件（如 `application.yml`）。

### 核心概念：三种模式

```
普通模式 ←→ 插入模式 ←→ 命令模式
 (默认)      (编辑)      (保存/退出)
```

### 生命线操作（背下来）

| 你想做的事 | 按键 |
|------------|------|
| 打开文件 | `vim filename` |
| 开始编辑 | 按 `i`（进入插入模式） |
| 停止编辑 | 按 `Esc`（回到普通模式） |
| 保存并退出 | `:wq` 回车 |
| 不保存退出 | `:q!` 回车 |
| 只保存不退出 | `:w` 回车 |
| 搜索文本 | `/关键字` 回车，`n` 下一个 |
| 跳到文件末尾 | `G`（大写，即 Shift+g） |
| 跳到文件开头 | `gg` |
| 删除整行 | `dd` |

### 最可能出错的地方

❌ **错误1**：打开文件后直接敲键盘，发现屏幕乱跳。
- **原因**：vim 默认在普通模式，你敲的字符被当成命令了。
- **解决**：按几次 `Esc` 清空命令缓冲，然后按 `i` 进入插入模式。

❌ **错误2**：不知道怎么退出，直接关终端窗口。
- **解决**：按 `Esc`，输入 `:q!` 回车。

> 💡 如果你只需要改一行配置，用 `nano` 代替 `vim` 会更友好：`nano filename`，底部有按键提示，`Ctrl+X` 退出。

---

## 108.5 文件权限——三位数字的秘密

```bash
ls -l
# -rwxr-xr-x 1 ubuntu ubuntu 12345 May 29 10:00 app.jar
```

这一串 `-rwxr-xr-x` 分为四部分：

| 部分 | 含义 |
|------|------|
| `-` | 文件类型（`-`普通文件，`d`目录） |
| `rwx` | 所有者（owner）权限 |
| `r-x` | 所属组（group）权限 |
| `r-x` | 其他人（others）权限 |

`r`=读(4)，`w`=写(2)，`x`=执行(1)。三位数字就是加和：

```bash
chmod 755 start.sh    # rwxr-xr-x：所有者全权限，其他人读+执行
chmod 644 app.jar     # rw-r--r--：所有者读写，其他人只读
chmod 600 id_rsa      # rw-------：只有自己能读写（私钥标准权限）
```

---

## 108.6 进程管理——杀死一个卡死的应用

### 查看进程

```bash
ps aux | grep java
```

输出：

```
ubuntu   12345  5.2  30.1  xxxxx  xxxxx  ?  Sl  10:00  0:30 java -jar app.jar
         ^^^^^
         这是PID
```

### 终止进程

```bash
kill 12345           # 优雅地请它关闭（SIGTERM）
kill -9 12345        # 强制杀死（SIGKILL），只在 kill 不管用时用
```

### 区分 kill 和 kill -9

- `kill` = 礼貌敲门："请你自己关掉。"
- `kill -9` = 强行断电。Spring Boot 可能来不及执行 `@PreDestroy` 钩子。

先试 `kill`，等几秒如果还在再 `kill -9`。

---

## 108.7 包管理器——apt

```bash
sudo apt update                  # 更新软件包列表
sudo apt upgrade                 # 升级所有已安装的包
sudo apt install nginx           # 安装 nginx
sudo apt remove nginx            # 卸载 nginx（保留配置）
sudo apt purge nginx             # 彻底卸载（含配置）
apt search openjdk               # 搜索软件包
```

---

## 108.8 环境准备（练手用）

如果你没有云服务器，可以在本地用虚拟机或 WSL（Windows Subsystem for Linux）：

### Windows 用户：安装 WSL

以管理员身份打开 PowerShell：

```powershell
wsl --install -d Ubuntu-22.04
```

安装后重启，开始菜单会出现 Ubuntu 图标。

### 验证环境

```bash
uname -a              # 应显示 Linux
whoami                # 应显示你的用户名
df -h                 # 应看到磁盘信息
```

---

## 108.9 完成效果

学完本章，你应该能：
1. SSH 登录一台远程 Linux 服务器
2. 用 `ls`、`cd`、`cat`、`grep`、`ps`、`kill` 完成日常操作
3. 用 `vim` 或 `nano` 编辑配置文件并保存退出
4. 用 `chmod` 给脚本加执行权限
5. 用 `apt` 安装/卸载软件

---

## 小结

| 知识点 | 核心命令 |
|--------|----------|
| 远程连接 | `ssh user@ip` |
| 密钥登录 | `ssh-keygen` + `ssh-copy-id` |
| 文件浏览 | `ls`, `cd`, `pwd`, `cat`, `less`, `tail` |
| 文件操作 | `cp`, `mv`, `rm`, `mkdir`, `touch` |
| 权限管理 | `chmod`, `chown` |
| 系统信息 | `top`, `df -h`, `free -h`, `ps aux` |
| 进程管理 | `kill`, `kill -9` |
| 包管理器 | `apt install/remove/update` |
| 文本编辑器 | `vim` / `nano` |

---

## 自测题

1. 你 SSH 登录服务器后，想看 `/var/log/syslog` 的最后 50 行并实时追踪新日志，用哪条命令？
2. `chmod 644 app.jar` 后，其他用户能否执行这个文件？为什么？
3. 你打开 vim 修改了 `nginx.conf`，想保存并退出，完整的按键序列是什么？

<details>
<summary>点击查看答案</summary>

1. `tail -n 50 -f /var/log/syslog` 或 `tail -50f /var/log/syslog`
2. 不能执行。644 = rw-r--r--，其他人只有读权限（r--），没有执行权限（x）。
3. 按 `Esc`（确保在普通模式），输入 `:wq` 回车。
</details>