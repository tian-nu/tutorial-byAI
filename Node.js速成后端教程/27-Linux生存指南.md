# 27-Linux 生存指南

> "你的 Windows/Mac 笔记本上跑得好好的博客，放到服务器上就报错——十有八九是 Linux 没玩明白。这一章不讲原理，只讲命令——你需要的不是一本 Linux 百科全书，而是一张能贴在显示器旁边的速查表。学完这章，你能用 SSH 连上服务器、安装软件、查看日志、编辑文件——刚好够你把博客部署上去。"

---

## 一、目标与完成效果

**一句话目标**：掌握 20 个常用 Linux 命令、nano/vim 基本操作、文件权限、SSH 连接、nvm 安装 Node.js，具备在 Linux 服务器上独立操作的能力。

**完成后的可观测效果**：
- 你能熟练使用 `ls`、`cd`、`mkdir`、`rm`、`cp`、`mv`、`cat`、`grep` 等 20 个命令在服务器上操作文件。
- 你能用 `nano` 编辑文件，或用 `vim` 完成基本操作（进入编辑、保存退出、强制退出）。
- 你能读懂 `chmod 755` 和 `chmod 400`，知道为什么 AWS 密钥文件需要 `chmod 400`。
- 你能用 `ssh -i key.pem user@ip` 连接远程服务器。
- 你能在服务器上用 nvm 安装 Node.js，和第一章如出一辙——只是这次在 Linux 上。
- 你理解了 `rm -rf`、`sudo`、LF vs CRLF 换行符等魔鬼细节。

---

## 二、前置条件

| 序号 | 条件 | 验证命令 |
|------|------|----------|
| 1 | 已完成教程 26，博客系统全部测试通过 | `npm test` 输出 `18 passed, 18 total` |
| 2 | 有一台能上网的电脑（Windows/Mac/Linux 均可） | 无需验证，你能看这篇教程就说明能上网 |
| 3 | 如果你想动手练习，需要一个 Linux 环境 | 见步骤 2 的三种方案（虚拟机/WSL/云服务器） |

**一条命令确认前置满足**：

```bash
npm test
```

输出 `18 passed, 18 total`，前置条件满足。

---

## 三、分步操作

### 步骤 1：为什么后端工程师必须会 Linux

> "99% 的服务器都是 Linux。你写的 Node.js 代码，最终都是在 Linux 上跑的。"

这不是夸张。看看各大云平台的数据：

| 平台 | Linux 占比 |
|------|-----------|
| AWS | > 90% |
| 阿里云 | > 95% |
| Azure | > 60% |
| Google Cloud | > 90% |

**原因很简单**：Linux 免费、开源、稳定、轻量。一个 1 核 1G 的 Linux 服务器能跑 Node.js 应用，同样的配置跑 Windows Server 连系统自己都跑不动。

**你需要学到什么程度？** 不是 Linux 运维专家——只需要能在服务器上安装软件、管理文件、查看日志、编辑配置。20 个命令，足够。

**比喻**：你不会修车，但你会开车、会加油、会看仪表盘——这就够了。本章就是教你"在 Linux 上开车"——不用修引擎，但要知道方向盘在哪。

---

### 步骤 2：没有 Linux 环境怎么办？（三种方案）

在学命令之前，你需要一个 Linux 终端。三种方案，按推荐度排序：

#### 方案一：Windows 用户——WSL2（推荐）

WSL（Windows Subsystem for Linux）是 Windows 内置的 Linux 子系统，一个命令就能装好。

```powershell
# 在 PowerShell（管理员权限）中运行
wsl --install
```

安装完成后重启电脑，在开始菜单搜索 "Ubuntu" 打开即可。你已经有了一个完整的 Linux 终端。

**验证**：

```bash
# 在 Ubuntu 终端中
whoami
# → 输出你的用户名
uname -a
# → 输出包含 "Linux" 即成功
```

#### 方案二：Mac 用户——自带终端

Mac 的终端（Terminal.app）就是类 Unix 环境，大部分 Linux 命令都能直接用。打开"终端"即可。

**验证**：

```bash
whoami
# → 输出你的用户名
uname -a
# → 输出包含 "Darwin"（macOS 的内核），命令兼容 Linux
```

#### 方案三：买一台云服务器（最终方案）

如果你已经打算买服务器（下一章会详细讲），现在买也行。最低配 1 核 1G，约 30-50 元/月。买了之后用 SSH 连上去，直接在真实服务器上练习。

> **如果你暂时不想买服务器**，用方案一或方案二，等下一章再买。本章的命令在 WSL/Mac 终端上都能练。

---

### 步骤 3：基本命令速查（20 个命令，每个一句话解释 + 示例）

以下是你在服务器上最常用的 20 个命令。**不用背，看一遍有个印象，需要时回来查就行。**

#### 3.1 文件与目录操作

| 命令 | 一句话解释 | 示例 | 示例解释 |
|------|-----------|------|----------|
| `ls` | 列出当前目录下的文件和文件夹 | `ls -la` | `-l` 显示详细信息（权限、大小、时间），`-a` 显示隐藏文件 |
| `cd` | 切换目录（Change Directory） | `cd /var/log` | 进入 `/var/log` 目录；`cd ..` 返回上一级；`cd ~` 回用户主目录 |
| `pwd` | 显示当前所在目录的完整路径 | `pwd` | 输出 `/home/deploy/blog-backend`，告诉你"你在哪" |
| `mkdir` | 创建目录（Make Directory） | `mkdir -p a/b/c` | `-p` 递归创建多层目录（如果 a 不存在，自动创建 a 和 a/b） |
| `rm` | 删除文件或目录 | `rm file.txt`，`rm -rf dir/` | `-r` 递归删除目录，`-f` 强制删除不提示（⚠️ 没有回收站！） |
| `cp` | 复制文件 | `cp a.txt b.txt` | 把 a.txt 复制一份叫 b.txt；`cp -r dir1/ dir2/` 复制整个目录 |
| `mv` | 移动/重命名文件 | `mv old.txt new.txt` | 重命名；`mv file.txt /tmp/` 移动到 `/tmp/` |

#### 3.2 文件内容查看

| 命令 | 一句话解释 | 示例 | 示例解释 |
|------|-----------|------|----------|
| `cat` | 一次性显示文件全部内容 | `cat server.js` | 把 `server.js` 的内容全部打印到终端 |
| `less` | 分页浏览文件内容（上下键翻页） | `less /var/log/nginx/access.log` | 按 `q` 退出，按 `/` 搜索，按 `n` 下一个匹配 |
| `head` | 显示文件前 10 行 | `head -n 20 app.log` | 显示前 20 行 |
| `tail` | 显示文件末尾 10 行 | `tail -f app.log` | `-f` 实时追踪文件末尾新增内容（看日志神器） |

#### 3.3 搜索与查找

| 命令 | 一句话解释 | 示例 | 示例解释 |
|------|-----------|------|----------|
| `grep` | 在文件中搜索指定文本 | `grep "error" app.log` | 在 `app.log` 中搜索包含 "error" 的行；`grep -r "TODO" ./src/` 递归搜索目录 |
| `find` | 按文件名查找文件 | `find . -name "*.js"` | 在当前目录及子目录中查找所有 `.js` 文件 |

#### 3.4 权限管理

| 命令 | 一句话解释 | 示例 | 示例解释 |
|------|-----------|------|----------|
| `chmod` | 修改文件权限（Change Mode） | `chmod 755 script.sh` | 设为：所有者可读/写/执行，其他人可读/执行（详见步骤 5） |
| `chown` | 修改文件所有者（Change Owner） | `chown deploy:deploy file.txt` | 把文件的所有者和所属组改为 deploy 用户 |

#### 3.5 系统状态

| 命令 | 一句话解释 | 示例 | 示例解释 |
|------|-----------|------|----------|
| `ps` | 查看正在运行的进程 | `ps aux` | 显示所有用户的所有进程，`\| grep node` 过滤出 Node.js 进程 |
| `top` | 实时查看系统资源使用（CPU、内存） | `top` | 按 `q` 退出，按 `1` 查看每个 CPU 核心 |
| `df` | 查看磁盘使用情况 | `df -h` | `-h` 以人类可读格式显示（GB/MB），不是字节数 |
| `du` | 查看目录/文件占用空间 | `du -sh node_modules/` | `-s` 汇总，`-h` 人类可读——`node_modules` 到底多大？ |

#### 3.6 网络与下载

| 命令 | 一句话解释 | 示例 | 示例解释 |
|------|-----------|------|----------|
| `wget` | 从 URL 下载文件 | `wget https://example.com/file.tar.gz` | 下载文件到当前目录 |
| `curl` | 发送 HTTP 请求（API 调试神器） | `curl http://localhost:3000/api/articles` | 发 GET 请求；`curl -X POST -d '{"title":"hi"}' -H "Content-Type: application/json" http://localhost:3000/api/articles` |
| `tar` | 打包/解压 tar 文件 | `tar -xzf file.tar.gz` | `-x` 解压，`-z` gzip 格式，`-f` 指定文件；`tar -czf output.tar.gz dir/` 打包压缩 |

**比喻**：这 20 个命令就是你在 Linux 餐厅里的"基础厨具"——`ls` 是"看冰箱里有什么"，`cd` 是"走进厨房"，`mkdir` 是"拿个新碗"，`rm` 是"倒掉剩菜"，`grep` 是"在菜谱里找关键词"，`tail -f` 是"盯着锅看有没有溢出来"。

---

### 步骤 4：文本编辑——nano 入门 vs vim 进阶

在服务器上，你没有 VS Code。你需要用命令行编辑器修改配置文件。两个选择：

#### 4.1 nano——新手友好

nano 是最简单的命令行编辑器。打开后，底部有快捷键提示（`^` 表示 Ctrl 键）。

```bash
nano .env
```

**操作**：
- 直接打字，和在记事本里一样。
- `Ctrl + O`：保存（Write Out）
- `Ctrl + X`：退出
- `Ctrl + W`：搜索

**什么时候用 nano？** 快速改一个配置文件（如 `.env`、`nginx.conf`），改完就走。不用学任何快捷键——底部全写着。

#### 4.2 vim——进阶必备

vim 是 Linux 世界最强大的编辑器，但学习曲线陡峭。**你只需要记住 4 个操作**，就能应付 90% 的场景：

```bash
vim .env
```

| 操作 | 按键 | 含义 |
|------|------|------|
| **进入编辑模式** | 按 `i` | 进入 "Insert" 模式，此时可以打字（底部显示 `-- INSERT --`） |
| **退出编辑模式** | 按 `Esc` | 回到 "Normal" 模式，此时不能打字，只能执行命令 |
| **保存并退出** | `:wq` 然后回车 | `w` = write（保存），`q` = quit（退出） |
| **不保存退出** | `:q!` 然后回车 | `q` = quit，`!` = 强制（放弃修改） |

**记忆口诀**：**i 进 Esc 出，:wq 保存走，:q! 不保存跑。**

**什么时候用 vim？** 有些极简 Linux 发行版（如 Docker 容器内的 Alpine）没有 nano，只有 vi/vim。你必须会 vim 的这四个操作，否则连文件都改不了。

> 🔥 **魔鬼细节**：vim 打开后默认是"Normal 模式"——你按键盘，vim 以为你在发命令，不会输入文字。新手最常见的问题是："为什么我打字没反应？"——因为你没按 `i` 进入编辑模式。**看到 vim 界面，先按 `i`。**

**比喻**：nano 是"便利贴"——打开就能写，写完贴上去。vim 是"专业打字机"——需要先解锁（`i`）、打完锁定（`Esc`）、然后选择保存（`:wq`）还是作废（`:q!`）。一开始觉得麻烦，熟练后效率极高。

---

### 步骤 5：文件权限——chmod 数字密码

#### 5.1 权限的三种角色和三种权限

Linux 中每个文件有三组权限，对应三种角色：

| 角色 | 缩写 | 含义 |
|------|------|------|
| 所有者（Owner） | u | 文件的主人 |
| 所属组（Group） | g | 和主人在同一个组的用户 |
| 其他人（Others） | o | 不是主人也不是同组的用户 |

每种角色有三种权限：

| 权限 | 字母 | 数字 | 含义 |
|------|------|------|------|
| 读（Read） | r | 4 | 可以查看文件内容或列出目录 |
| 写（Write） | w | 2 | 可以修改文件内容或创建/删除目录中的文件 |
| 执行（eXecute） | x | 1 | 可以运行文件（脚本/程序）或进入目录 |

#### 5.2 chmod 数字 = 三位权限的加和

`chmod 755 file` 中，`755` 分别对应 **所有者 / 所属组 / 其他人** 的权限：

| 数字 | 计算 | 权限 | 含义 |
|------|------|------|------|
| 7 | 4 + 2 + 1 | rwx | 读 + 写 + 执行 |
| 5 | 4 + 0 + 1 | r-x | 读 + 执行（不能写） |
| 5 | 4 + 0 + 1 | r-x | 读 + 执行（不能写） |

所以 `chmod 755 file` 的意思是：
- 所有者（7 = rwx）：可以读、写、执行
- 所属组（5 = r-x）：可以读、执行，不能写
- 其他人（5 = r-x）：可以读、执行，不能写

**常用权限组合**：

| 命令 | 数字 | 含义 | 使用场景 |
|------|------|------|----------|
| `chmod 755 script.sh` | rwxr-xr-x | 所有者全权限，其他人只读+执行 | 可执行脚本 |
| `chmod 644 file.txt` | rw-r--r-- | 所有者可读写，其他人只读 | 普通配置文件 |
| `chmod 400 key.pem` | r-------- | 只有所有者可读 | SSH 私钥文件 |
| `chmod 777 file` | rwxrwxrwx | 所有人全权限 | ⚠️ 几乎永远不要用——安全灾难 |

#### 5.3 AWS 密钥文件的必要性：chmod 400

当你从 AWS（或阿里云、腾讯云）下载密钥文件（`.pem`）后，如果直接 `ssh -i key.pem user@ip`，可能会报错：

```
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@         WARNING: UNPROTECTED PRIVATE KEY FILE!          @
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
Permissions for 'key.pem' are too open.
It is required that your private key files are NOT accessible by others.
This private key will be ignored.
```

**原因**：SSH 要求私钥文件只能被所有者读取——其他人碰都不能碰。如果权限太宽松（比如 `644`），SSH 会拒绝使用这个密钥。

**解决**：

```bash
chmod 400 key.pem
```

`400` = 所有者只读（r--------），其他人都没权限。这是 SSH 密钥文件的标准权限。

> 🔥 **魔鬼细节**：Windows 用户从 AWS 下载 `.pem` 文件后，文件的权限继承自 Windows 文件系统，可能没有 Linux 权限概念。如果 WSL 中 `chmod 400` 不生效，把 `.pem` 文件复制到 WSL 的文件系统内（如 `~/` 目录），再 `chmod 400`。

**比喻**：`chmod 400` 就像给密钥文件上了一把锁——"这把钥匙只有我能看，别人看一眼都不行。"SSH 就像一个严格的保安——"你的钥匙被人看过了？那我不能让你进门。"

---

### 步骤 6：SSH 连接服务器

SSH（Secure Shell）是连接远程 Linux 服务器的标准方式。此术语需进附录。

#### 6.1 基本语法

```bash
ssh user@ip_address
```

- `user`：服务器上的用户名（如 `root`、`deploy`）
- `ip_address`：服务器的公网 IP 地址

**首次连接**会提示：

```
The authenticity of host 'xxx.xxx.xxx.xxx' can't be established.
ECDSA key fingerprint is SHA256:xxxxxxxxxxxxxxxxxxxxxxxxxxxx.
Are you sure you want to continue connecting (yes/no)?
```

输入 `yes` 然后回车。这是 SSH 在确认"你确定要连接这台服务器吗？"——第一次连接陌生服务器都会问。之后就不会再问了。

#### 6.2 使用密钥文件连接

云服务商通常提供密钥文件（`.pem`）而不是密码：

```bash
ssh -i key.pem user@ip_address
```

- `-i`：指定身份文件（Identity file），即你的私钥文件
- `key.pem`：从云服务商下载的密钥文件
- 连接前必须 `chmod 400 key.pem`（见步骤 5.3）

#### 6.3 退出 SSH

```bash
exit
```

或按 `Ctrl + D`。

**比喻**：SSH 就像一条"加密隧道"——你在本地电脑上打字，命令通过隧道传到服务器上执行，结果通过隧道传回来显示。外面的人看不到隧道里在传什么（加密），但他们能看到有隧道存在（知道你在连服务器）。

---

### 步骤 7：在服务器上安装 Node.js（用 nvm）

这和第一章你在本地做的事几乎一模一样——只是现在在 Linux 服务器上操作。

#### 7.1 安装 nvm

```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
```

这条命令下载 nvm 安装脚本并执行。安装完成后，**退出终端重新登录**，或者执行：

```bash
source ~/.bashrc
```

**验证 nvm 安装**：

```bash
nvm --version
# → 0.39.7
```

#### 7.2 安装 Node.js LTS

```bash
nvm install --lts
```

这会安装最新的 LTS（长期支持）版本。安装完成后：

```bash
node --version
# → v20.x.x（或更高）
npm --version
# → 10.x.x（或更高）
```

#### 7.3 设置默认版本

```bash
nvm alias default node
```

这样每次登录服务器，Node.js 都是可用的。

**对比第一章**：你在本地做的事——下载 nvm、安装 Node.js、验证版本——和服务器上完全一样。这就是 nvm 的好处：不管在哪台机器上，装 Node.js 的步骤都是这两行命令。

> 🔥 **魔鬼细节**：`curl ... | bash` 这种"下载脚本并直接执行"的方式，在安全敏感的环境中要谨慎——你应该先查看脚本内容再执行。但 nvm 是 GitHub 上 75k+ star 的知名项目，相对安全。如果你不放心，可以先去 https://github.com/nvm-sh/nvm 看源码。

---

### 🤔 想多一点：Linux 换行符（LF）vs Windows 换行符（CRLF）

这是一个让无数新手抓狂的问题。

- **Windows**：换行符是 `\r\n`（CRLF，Carriage Return + Line Feed）
- **Linux/Mac**：换行符是 `\n`（LF，Line Feed）

**现象**：你在 Windows 上写的 `.sh` 脚本，上传到 Linux 服务器后运行报错：

```bash
bash: ./script.sh: /bin/bash^M: bad interpreter: No such file or directory
```

那个 `^M` 就是 Windows 的 `\r` 字符。Linux 不认识它。

**解决**：

- **预防**：在 VS Code 右下角点击 "CRLF"，选择 "LF"，然后保存。之后新建的文件都会用 LF。
- **修复已有文件**：`dos2unix file.sh`（需要先安装 `sudo apt install dos2unix`）
- **或者用 sed**：`sed -i 's/\r$//' file.sh`

**什么时候容易踩坑？**
- 在 Windows 上写 `.env` 文件，然后 `scp` 上传到服务器 → 环境变量里多了看不见的 `\r`，导致 JWT_SECRET 不匹配。
- 在 Windows 上写 shell 脚本，上传后无法执行。

**建议**：在 VS Code 中把默认换行符设为 LF（`File > Preferences > Settings > 搜索 "eol" > 设为 "\n"`）。

---

### 🤔 想多一点：`rm -rf` 的威力——没有回收站！

```bash
rm -rf /
```

这条命令会删除整个系统。**能执行吗？** 现代 Linux 发行版（如 Ubuntu）会阻止你——`rm` 命令加了 `--preserve-root` 保护。但以下命令仍然危险：

```bash
rm -rf ~/important-project/   # 删除整个项目，没有回收站！
rm -rf *                       # 删除当前目录下所有文件
```

**Linux 没有回收站**。`rm` 就是永久删除，不可恢复。所以：

- 删除前先用 `ls` 确认目录内容。
- 重要文件先备份。
- 不确定的命令，先去掉 `-f` 参数（`rm -r dir/` 会逐个文件确认）。

**比喻**：Windows 的删除是"扔进垃圾桶"——还能捡回来。Linux 的删除是"碎纸机"——进去了就没了。

---

### 🤔 想多一点：`sudo`——以管理员身份运行

`sudo`（Super User DO）以管理员（root）权限执行命令。此术语需进附录。

```bash
sudo apt install nginx
# ↑ 普通用户没有权限安装系统级软件，需要 sudo 提权
```

**规则**：
- **需要 sudo 的操作**：安装软件（`apt install`）、修改系统配置（`/etc/` 下的文件）、重启服务（`systemctl restart`）。
- **不需要 sudo 的操作**：在自己目录下操作文件（`~/`）、运行 Node.js 应用、编辑自己的 `.env` 文件。

**禁忌**：
- ❌ **别在 root 用户下日常操作**。root 是超级管理员，没有任何限制——一个手滑 `rm -rf /` 真的会删掉系统。创建普通用户（下一章会讲），sudo 只在需要时用。
- ❌ **别用 `sudo npm install -g`**。全局安装 Node.js 包不需要 sudo（nvm 安装在用户目录下）。如果用了 sudo，可能导致权限问题。

---

## 四、完整代码清单

本章为纯命令速查章节，无代码变更。所有命令在上文已列出。

---

## 五、验证方法

打开终端（WSL/Mac 终端/SSH 连接的服务器），依次执行以下命令，确认都能正常输出：

```bash
# 1. 文件操作
ls -la ~/
pwd
mkdir -p ~/test-linux/subdir
cd ~/test-linux
touch hello.txt
echo "Hello Linux" > hello.txt
cat hello.txt
# → Hello Linux

# 2. 查看内容
head -n 1 hello.txt
tail -n 1 hello.txt

# 3. 搜索
grep "Hello" hello.txt
# → Hello Linux

# 4. 权限
chmod 644 hello.txt
ls -la hello.txt
# → -rw-r--r-- ...

# 5. 清理
cd ~
rm -rf ~/test-linux

# 6. 确认 Node.js 可用（如果安装了 nvm）
node --version
npm --version
```

全部通过？你已经是 Linux 合格用户了。

---

## 六、小结表格

| 学到的东西 | 一句话解释 |
|-----------|-----------|
| Linux 为何重要 | 99% 的服务器是 Linux，你的 Node.js 代码最终在上面跑 |
| 20 个基础命令 | `ls`、`cd`、`pwd`、`mkdir`、`rm`、`cp`、`mv`、`cat`、`less`、`head`、`tail`、`grep`、`find`、`chmod`、`chown`、`ps`、`top`、`df`、`du`、`wget`、`curl`、`tar` |
| nano vs vim | nano 适合快速改配置文件（底部有快捷键提示）；vim 是进阶编辑器（记住 i/Esc/:wq/:q! 四个操作） |
| chmod 数字 | r=4, w=2, x=1；三位数字分别对应所有者/组/其他人 |
| chmod 755 | 所有者 rwx，其他人 r-x——适合可执行脚本 |
| chmod 400 | 只有所有者可读——SSH 密钥文件的标准权限 |
| chmod 777 | 所有人全权限——几乎永远不要用 |
| SSH 连接 | `ssh -i key.pem user@ip`；首次连接输入 yes |
| nvm 安装 Node.js | `curl -o- ... | bash` → `nvm install --lts` → 和第一章一样 |
| `rm -rf` 的威力 | Linux 没有回收站，删除即永久 |
| `sudo` | 以管理员身份运行命令，只在需要时用，别用 root 日常操作 |
| LF vs CRLF | Linux 换行符是 `\n`，Windows 是 `\r\n`——混用会导致脚本报错 |

---

## 七、术语附录

| 术语 | 英文 | 通俗解释 | 本章出现位置 | 字面陷阱 |
|------|------|----------|-------------|----------|
| SSH | Secure Shell | 加密的网络协议，用于安全地远程登录 Linux 服务器。所有数据传输都是加密的，中间人看不到内容。 | 步骤 6 | 不是"远程桌面"——SSH 是命令行界面，不是图形界面。 |
| chmod | Change Mode | 修改文件权限的命令。用数字（755、644、400）表示所有者/组/其他人的读(4)写(2)执行(1)权限。 | 步骤 5 | 不是"修改模式"——"mode"在 Linux 中特指"文件权限位"。 |
| chown | Change Owner | 修改文件所有者和所属组的命令。 | 步骤 3 | 不是"改变拥有"——"own"是"owner"的缩写。 |
| systemd | System Daemon | Linux 的系统和服务管理器。负责开机启动服务、管理进程、定时任务等。几乎所有现代 Linux 发行版都用它。 | 步骤 7（概念） | 不是"系统守护进程"——"d"是 Unix 传统，表示 daemon（后台服务）。 |
| apt | Advanced Package Tool | Debian/Ubuntu 系统的包管理器。`apt install` 安装软件，`apt update` 更新软件列表。 | 步骤 7（概念） | 不是"适合"——APT 是 Advanced Packaging Tool 的缩写，和"恰当"无关。 |
| sudo | Super User DO | 以管理员（root）权限执行命令。普通用户没有权限操作系统级文件时，用 sudo 临时提权。 | 想多一点 | 不是"伪用户"——"su"是"superuser"的缩写，"do"就是"做"。 |
| nano | — | 最简单的命令行文本编辑器。底部有快捷键提示（^O 保存、^X 退出），新手友好。 | 步骤 4 | 不是"纳米"——名字来源于"nano"（小），表示它很轻量。 |
| vim | Vi IMproved | 最强大的命令行文本编辑器。学习曲线陡峭，但几乎所有 Linux 系统都预装。记住 i/Esc/:wq/:q! 四个操作即可。 | 步骤 4 | 不是"活力"——"vim"是"vi improved"（vi 增强版）的缩写。 |

---

## 八、已知坑点与禁止事项

| 坑点 | 现象 | 原因 | 解决 |
|------|------|------|------|
| vim 打开后打字没反应 | 按键盘，屏幕上出现奇怪的字符或者光标乱跳 | vim 默认是 Normal 模式，不是编辑模式 | 按 `i` 进入编辑模式，底部显示 `-- INSERT --` 后就可以打字了 |
| SSH 拒绝密钥文件 | `Permissions for 'key.pem' are too open` | 密钥文件权限太宽松，其他用户也能读 | `chmod 400 key.pem` |
| Windows 换行符导致脚本报错 | `bash: ./script.sh: /bin/bash^M: bad interpreter` | Windows 的 CRLF 换行符在 Linux 上不兼容 | 在 VS Code 右下角切换为 LF 再保存，或用 `dos2unix` 转换 |
| 在 root 用户下日常操作 | 不小心 `rm -rf /` 删了系统 | root 没有任何限制，任何操作都直接执行 | 创建普通用户（下一章教），只在必要时用 `sudo` |
| `rm -rf` 误删 | 项目代码永久丢失 | Linux 没有回收站 | 删除前用 `ls` 确认；重要文件先备份；不确定时去掉 `-f` 参数 |
| nvm 命令找不到 | `nvm: command not found` | 安装 nvm 后没有退出重登，或没有 `source ~/.bashrc` | 退出终端重新登录，或执行 `source ~/.bashrc` |
| 全局安装 npm 包用 sudo | `sudo npm install -g pm2` 后，普通用户用不了 pm2 | nvm 管理的 Node.js 在用户目录下，用 sudo 会导致权限混乱 | 用 nvm 管理 Node.js 时，全局安装 npm 包不需要 sudo |
| `curl ... | bash` 安全风险 | 下载并执行了恶意脚本 | 没有查看脚本内容就直接执行 | 知名项目（如 nvm）可以信任；不确定的脚本，先 `curl -o script.sh` 下载，用 `less` 查看后再执行 |

---

## 九、下一步建议

你掌握了 Linux 的基本操作。下一章就是实战——买一台真实的云服务器，把你的博客系统部署上去，让全世界都能访问。

**下一章（教程 28：买服务器 + PM2 部署）**，你将：
- 在阿里云/腾讯云/AWS 上购买一台云服务器（最低配 1 核 1G，约 30-50 元/月）
- 配置安全组/防火墙（只开放 22、80、443 端口）
- 创建普通用户（不用 root 日常操作）
- 用 nvm 安装 Node.js
- 上传代码到服务器
- 用 PM2 管理 Node.js 进程（开机自启、日志查看、零停机重启）

---

> [可暂停点 7/9]：阶段八（部署）第一部分完成。你掌握了 20 个 Linux 常用命令、nano/vim 文件编辑、文件权限、SSH 连接、nvm 安装 Node.js。下一章将购买真实的云服务器并部署博客系统。
>
> 📊 本教程无可视化
>
> 本教程编辑记录：2026-06-12 初始版本（第 7 批：27-31 章）。