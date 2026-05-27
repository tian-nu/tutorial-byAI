# 第99章 · Linux必备知识

> "架构设计好了，代码写完了，单元测试也全部通过了——现在怎么办？你的程序还活在你自己的笔记本电脑里，别人根本用不了。从这一章开始，我们要把Go程序从你的电脑搬到互联网上的服务器，让全世界的人都能访问。而服务器的操作系统，99%是Linux（开源的类Unix操作系统，详见附录I）。所以，第一步就是：学会在Linux上生存。"

---

## 99.1 Linux目录结构：每个文件夹都是干什么的

Windows用户习惯了C盘D盘、Program Files、Users这些概念。Linux不一样——它没有盘符，所有东西都从**一个根**开始：`/`（读作"根目录"）。

想象一下，Linux的文件系统是一棵**倒着长的树**：根`/`是最顶端，所有目录、文件、设备、甚至内存里的数据都挂在这棵树上。

```
/
├── bin/          ← 最基础的命令（所有用户都能用）
├── boot/         ← 启动系统需要的文件（内核、引导程序）
├── dev/          ← 设备文件（硬盘、键盘、鼠标，全被伪装成文件）
├── etc/          ← 配置文件的大本营
├── home/         ← 普通用户的家目录（C:\Users 的对应物）
├── lib/          ← 系统库文件（程序的"共享零件"）
├── media/        ← 自动挂载的U盘、光盘
├── mnt/          ← 手动挂载（临时挂东西的地方）
├── opt/          ← 可选的第三方软件（你自己装的软件放在这）
├── proc/         ← 虚拟文件系统（内存里的东西，进程信息）
├── root/         ← root用户（超级管理员）的家目录
├── run/          ← 运行时临时文件（系统启动后产生的数据）
├── sbin/         ← 系统管理员用的命令（普通用户一般用不了）
├── srv/          ← 服务数据（Web服务器、FTP的数据放这）
├── sys/          ← 内核信息（硬件、驱动等）
├── tmp/          ← 临时文件（所有人可读写，重启可能清空）
├── usr/          ← 用户软件的大本营（大多数程序装在这）
└── var/          ← 经常变化的文件（日志、缓存、数据库）
```

### 逐目录详解

**`/` —— 根目录**

在Windows里是 `C:\`，在Linux里就是 `/`。一切从这里开始。你永远打不开"上面还有一层"——因为 `/` 就是最顶层。就像一栋大楼没有"-1层以上的-2层"一样，这个概念需要一点时间来适应。

**`/bin` —— 二进制命令（binary）**

存放最基础的命令，比如 `ls`（列出文件）、`cat`（看文件内容）、`cp`（复制）、`mv`（移动）。为什么叫"二进制"？因为这些命令都已经被编译成了机器码（用C语言写的），不是文本脚本。

这些命令即使系统出问题时也能用，因为它们是救援模式下的救命稻草。现代Linux发行版中，`/bin` 往往是 `/usr/bin` 的软链接。

**`/boot` —— 启动文件**

这个目录不大，但极其重要。里面放着：
- `vmlinuz-*`：Linux内核本身（压缩过的）
- `initrd.img-*`：初始化RAM磁盘镜像（启动时需要的临时根文件系统）
- `grub/`：GRUB引导程序的配置文件

如果你脑子一热 `rm -rf /boot/*`，电脑就再也起不来了。**别碰它。**

**`/dev` —— 设备文件**

Linux的设计哲学：**一切皆文件**。你的键盘、鼠标、硬盘、U盘、甚至 `/dev/null`（一个永久丢数据的黑洞），都以文件的形式存在这个目录里。

```bash
ls /dev
```

你会看到：
- `sda`、`sda1`、`sda2`：你的第一块硬盘和分区（s=SCSI, d=disk, a=第一块, 1=第一个分区）
- `tty`：终端设备
- `null`：数据黑洞，写进去的东西永远消失
- `zero`：无限的零字节流
- `random`、`urandom`：随机数生成器

**`/etc` —— 配置文件**

这是最重要的目录之一。`etc` 不是"等等"（et cetera）——虽然名字确实来源于此，但实际功能是存放**所有系统和软件的配置文件**。

重要的文件：
- `/etc/passwd`：用户账号信息
- `/etc/shadow`：加密后的密码
- `/etc/group`：用户组信息
- `/etc/hosts`：本地主机名→IP映射
- `/etc/nginx/nginx.conf`：Nginx的配置文件
- `/etc/systemd/system/`：systemd服务配置

**`/home` —— 用户的家**

相当于Windows的 `C:\Users\`。每个普通用户在这个目录下有自己的文件夹：
- `/home/alice/`：Alice的家目录
- `/home/bob/`：Bob的家目录

每个用户的家目录里可以随便读写，但是不能碰别的用户的文件（除非你是root）。你的代码、下载的文件、配置文件通常都在家目录下。

**`/lib` 和 `/lib64` —— 共享库**

程序的"共享零件"。类似Windows的DLL文件。当你在Go里 `import "fmt"` 时，Go是静态编译所以不需要系统库——但很多其他程序（比如Python、C程序）需要这些。

**`/opt` —— 可选软件**

你自己下载安装的第三方软件通常放这里。比如你手动下载了JDK、Node.js、Go，可以解压到 `/opt/` 下。

**`/proc` —— 进程信息（虚拟文件系统）**

这个目录**不占硬盘空间**——它是内核在内存里动态生成的虚拟文件系统。每一个正在运行的进程在这里都有一个以PID（进程ID）命名的文件夹。

```bash
cat /proc/cpuinfo    # 查看CPU信息
cat /proc/meminfo    # 查看内存信息
cat /proc/version    # 查看内核版本
```

**`/root` —— root用户的家**

普通用户的家在 `/home/用户名`，root（超级管理员）的家在 `/root`。为什么不在 `/home/root`？因为 `/home` 可能挂载在另一个分区或通过网络挂载——系统必须保证root的家目录永远可访问。

**`/tmp` —— 临时文件**

所有人的临时文件都扔这里，任何用户都能读写。系统重启时这个目录通常会被清空。**不要在这里放重要文件。**

**`/usr` —— 用户软件**

这个目录最大。`usr` 不是"user"的缩写（虽然历史来源与此有关），现在的角色是存放**所有用户级别的程序和数据**：
- `/usr/bin/`：大部分用户命令（比 `/bin` 多得多）
- `/usr/lib/`：用户程序的库
- `/usr/local/`：本地编译安装的软件
- `/usr/share/`：共享数据（文档、图标、字体等）

**`/var` —— 变化文件**

存放运行过程中**不断变化**的数据：
- `/var/log/`：系统日志（排查问题的第一站）
- `/var/lib/mysql/`：MySQL数据库的实际数据文件
- `/var/cache/`：各种缓存
- `/var/spool/`：邮件队列、打印队列
- `/var/www/`：Web服务器的网站文件（部分发行版）

### 🤔 想多一点：为什么Linux没有C盘D盘？

Windows的设计源自DOS时代，当时每台电脑可能有好几个物理驱动器（软驱A:、硬盘C:、光驱D:）。所以用字母区分。

Linux的设计源自Unix，当时硬盘很贵，一台机器可能只有一个物理硬盘但需要灵活的组织方式。所以设计了"挂载"机制——任何物理设备（硬盘、U盘、网络存储）都可以"挂"到目录树的任何一个位置。你在 `/home` 下面操作文件，可能根本不知道这些文件实际存在哪块硬盘上。

**类比**：Windows像一栋楼里每层都有独立的电梯（C盘一个电梯，D盘一个电梯），Linux像一栋楼只有一部电梯，但每层根据功能命名（/bin层、/home层、/var层）。你不需要关心电梯背后的机器在哪个地下室。

---

## 99.2 文件权限：谁能看、谁能改、谁能执行

### 三种身份、三种权限

Linux的权限模型基于**三三制**：

**三种身份：**
- **u（user/owner）**：文件所有者——通常是创建这个文件的人
- **g（group）**：用户组——和所有者同组的人
- **o（others）**：其他人——系统上其他所有人

**三种权限：**
- **r（read=4）**：读取——能看文件内容（目录：能列出文件名）
- **w（write=2）**：写入——能修改文件内容（目录：能创建/删除文件）
- **x（execute=1）**：执行——能运行这个文件（目录：能进入这个目录）

### 看懂权限字符串

```bash
ls -l
```

你会看到：

```
-rwxr-xr-- 1 alice developers 4096 May 18 10:30 myapp
```

拆解第一个字段 `-rwxr-xr--`：

```
位置: 1   234   567   890
含义: 类型 u权限 g权限 o权限
```

| 位置 | 字符 | 含义 |
|------|------|------|
| 1 | `-` | 文件类型：`-`=普通文件，`d`=目录，`l`=软链接 |
| 2-4 | `rwx` | 所有者：读+写+执行（4+2+1=7） |
| 5-7 | `r-x` | 同组用户：读+执行（4+0+1=5） |
| 8-10 | `r--` | 其他人：只能读（4+0+0=4） |

这个文件的权限用数字表示就是 **754**：
- 所有者 = 7（rwx）
- 用户组 = 5（r-x）
- 其他人 = 4（r--）

### 常见权限组合

| 数字 | 权限 | 含义 | 用例 |
|------|------|------|------|
| 777 | rwxrwxrwx | 所有人可读可写可执行 | **危险！** 只能在特殊情况用 |
| 755 | rwxr-xr-x | 所有者全权，其他人只读+执行 | 可执行程序、目录 |
| 644 | rw-r--r-- | 所有者可读写，其他人只读 | 普通文件、配置文件 |
| 600 | rw------- | 只有所有者可读写 | 私钥文件、敏感配置 |
| 700 | rwx------ | 只有所有者全权 | 私人脚本、私密目录 |

### chmod：修改文件权限

**符号方式**（人类可读）：

```bash
chmod u+x myapp.sh        # 给所有者添加执行权限
chmod g-w config.txt       # 去掉同组用户的写权限
chmod o= doc/              # 其他用户没有任何权限
chmod a+r README.md        # 所有人（all）增加读权限
chmod u=rwx,g=rx,o= main   # 精确设定：所有者7，组5，其他人0
```

**数字方式**（最常用）：

```bash
chmod 755 myprogram        # rwxr-xr-x
chmod 644 config.yaml      # rw-r--r--
chmod 600 id_rsa            # rw-------（SSH私钥必须是600）
chmod 777 shared_dir/      # rwxrwxrwx（尽量不要用）
```

### chown：修改文件所有者

```bash
chown alice report.txt            # 把文件所有者改为alice
chown alice:developers report.txt # 所有者和组一起改
chown -R bob:bob /home/bob/app/   # 递归修改整个目录（-R）
```

### chgrp：只改用户组

```bash
chgrp developers project/
chgrp -R developers project/     # 递归
```

### 目录权限的特殊性

**目录的权限和文件不一样！**

- **r（读目录）**：能列出目录里有哪些文件（`ls` 能工作）
- **w（写目录）**：能在目录里创建、删除、重命名文件
- **x（执行目录）**：能"进入"目录（`cd` 能工作，访问目录里的文件）

> ⚠️ 常见坑：目录权限是755，你以为"其他人只能读不能写，安全！"。但如果目录里有一个权限为777的文件，其他人虽然不能创建新文件，但可以修改那个777文件的内容（因为文件本身的权限允许）。要真正保护文件，必须同时控制好文件权限和目录权限。

### 🤔 想多一点：为什么私钥必须是600？

SSH私钥（`~/.ssh/id_rsa`）是你的"数字身份证"。如果别人拿到了你的私钥，就能冒充你登录任何你注册过的服务器。

600权限 = `rw-------`，意思是：只有你（所有者）能读写，其他任何人（同组用户、其他人、root除外——不是，root什么都能看）都不能碰。

如果你把私钥设成644（`rw-r--r--`），SSH会直接拒绝使用它，报错：
```
Permissions 0644 for 'id_rsa' are too open.
```
这是SSH的安全设计——宁可让程序报错，也不让你的私钥处于不安全状态。

---

## 99.3 用户和用户组

### Linux是"多用户"系统

Windows一般一个人用一台电脑。Linux天生就支持**多用户同时登录**——一台服务器上可能同时有几百个用户通过SSH（安全的远程登录协议，详见附录I）连接着，每个人运行着自己的程序，互不干扰。

### 用户账号文件

**`/etc/passwd`** —— 用户信息（虽然叫passwd但密码不在里面）

```
root:x:0:0:root:/root:/bin/bash
alice:x:1001:1001:Alice Smith:/home/alice:/bin/bash
```

每行7个字段，用冒号分隔：
1. 用户名
2. 密码占位符（`x` 表示密码在 `/etc/shadow`）
3. UID（用户ID，0=root）
4. GID（主组ID）
5. 全名/描述
6. 家目录
7. 登录Shell（命令行解释器，详见附录I）

**`/etc/shadow`** —— 真正的密码（加密后的）

```
alice:$6$randomSalt$veryLongEncryptedString:19500:0:99999:7:::
```

这个文件只有root能读。密码用的是SHA512哈希+盐值，不可逆。

**`/etc/group`** —— 用户组

```
developers:x:1002:alice,bob,charlie
```

### 用户管理命令

```bash
sudo useradd -m -s /bin/bash alice   # 创建用户：-m创建家目录，-s指定Shell
sudo passwd alice                      # 设置密码
sudo userdel -r alice                 # 删除用户：-r同时删除家目录
sudo usermod -aG docker alice         # 把alice加入docker组（-a=追加，否则会覆盖）
```

### root和sudo

**root** 是Linux的"超级管理员"，UID=0，拥有所有权限。能删除系统文件、格式化硬盘、修改任何文件。

**千万不要用root登录做日常操作！** 原因：
1. 手滑 `rm -rf /` 会删掉整个系统（root有这个权限）
2. 被攻击的程序如果以root运行，攻击者就获得了root权限
3. 你不知道是谁执行的操作（审计困难）

**sudo**（Super User DO）让你临时以root身份执行一条命令：

```bash
sudo apt-get install nginx        # 以root身份安装软件
sudo systemctl restart myapp      # 以root身份重启服务
```

`sudo` 会记录每次操作，并且可以精确控制谁可以用 `sudo` 做什么（通过 `/etc/sudoers`）。

### su：切换用户

```bash
su - alice    # 切换到alice用户（带-会加载alice的环境变量）
su -           # 切换到root
```

---

## 99.4 进程管理

### 进程是什么

一个程序运行起来之后，在内存中的那个"活的实例"就叫**进程（Process）**。一个程序可以启动多个进程（比如你打开了三个终端窗口，就有三个终端进程）。

每个进程有：
- **PID**（Process ID）：唯一编号（身份证号）
- **PPID**（Parent PID）：父进程的ID（谁启动了这个进程）
- **状态**：运行中、睡眠中、僵尸、停止

### ps：查看进程

```bash
ps aux                 # 查看所有用户的进程（最常用）
ps aux | grep nginx    # 搜索包含nginx的进程
ps -ef                 # 另一种显示格式
```

`ps aux` 输出解读：

```
USER    PID  %CPU %MEM    VSZ   RSS TTY   STAT START   TIME COMMAND
root      1   0.0  0.1  22576  5476 ?     Ss   09:00   0:02 /sbin/init
alice   1234   0.5  2.3 234567 89012 ?     Sl   10:30   0:15 ./myapp
```

关键字段：
- PID：进程ID
- %CPU：CPU使用率
- %MEM：内存使用率
- STAT：进程状态（S=睡眠，R=运行，Z=僵尸，T=停止）
- COMMAND：启动命令

### top：实时进程监控

```bash
top              # 实时显示进程列表，按q退出
top -u alice     # 只看alice用户的进程
```

`top` 显示的信息：
- 第一行：系统运行时间、负载
- 第二行：总任务数、运行中、睡眠中
- 第三行：CPU使用率（us=用户态，sy=内核态，id=空闲）
- 第四行：内存使用情况

进程列表按CPU使用率排序，最耗CPU的在最上面。

### kill：终止进程

```bash
kill 1234             # 优雅终止（发送SIGTERM信号）
kill -9 1234          # 强制杀死（发送SIGKILL信号，不给清理机会）
kill -l               # 列出所有信号
killall nginx         # 按名称终止所有nginx进程
```

**SIGTERM（信号15）vs SIGKILL（信号9）**：
- SIGTERM：礼貌地请进程退出。进程收到后可以清理资源、保存数据、然后退出。大部分程序（包括Go的 `signal.Notify`）都能处理。
- SIGKILL：直接枪毙。内核强制终止进程，不给任何清理机会。**只在进程卡死无响应时使用。**

### nohup：后台运行不挂断

```bash
nohup ./myapp &        # 后台运行，即使关闭终端也不终止
nohup ./myapp > app.log 2>&1 &   # 后台运行，输出重定向到文件
```

`nohup` = "no hangup"（不挂断）。正常情况下，关闭终端时系统会发送SIGHUP信号给该终端下所有进程，进程收到后退出。`nohup` 让进程忽略SIGHUP信号。

### 前台后台切换

```bash
./myapp &           # 在后台启动
jobs                # 查看当前终端下的后台任务
fg %1               # 把1号后台任务调到前台
bg %1               # 把1号任务放回后台继续运行
Ctrl+Z              # 暂停当前前台任务，放回后台（状态是"已停止"）
```

### 🤔 想多一点：什么是"僵尸进程"？

当一个子进程结束后，它的退出状态需要被父进程"收尸"（调用 `wait()`）。如果父进程忘了收尸，子进程的"墓碑"（进程表项）就一直留着——这个墓碑就是僵尸进程。

僵尸进程不占CPU和内存（只是进程表里的一条记录），但太多僵尸进程会占满进程表，导致无法创建新进程。

在Go中，如果你用 `exec.Command` 启动外部程序，记得调用 `cmd.Wait()` 来收尸。

---

## 99.5 磁盘管理

### df：查看磁盘空间

```bash
df -h       # -h=人类可读格式（显示GB/MB而不是字节数）
```

输出示例：
```
Filesystem      Size  Used Avail Use% Mounted on
/dev/sda1        50G   20G   28G  42% /
/dev/sdb1       200G  150G   40G  79% /data
```

### du：查看目录/文件大小

```bash
du -sh /home/alice/       # 查看alice家目录总大小
du -sh *                  # 查看当前目录下每个文件/文件夹的大小
du -h --max-depth=1 /var  # 只列/var下一级子目录的大小
```

### fdisk：分区管理

```bash
sudo fdisk -l                       # 列出所有磁盘和分区
sudo fdisk /dev/sdb                 # 进入sdb磁盘的交互式分区工具
```

### mount：挂载文件系统

```bash
mount                                   # 查看所有已挂载的文件系统
sudo mount /dev/sdb1 /data              # 把sdb1分区挂载到/data目录
sudo mount -t ext4 /dev/sdc1 /backup    # 指定文件系统类型
sudo umount /data                       # 卸载
```

**重要概念**：Linux的"挂载"就是把一个设备（硬盘分区、U盘、网络存储）"放在"目录树的某个位置上。对用户来说，挂载后访问 `/data` 就是访问那块硬盘的分区，完全透明。

---

## 99.6 网络命令

### ping：测试连通性

```bash
ping google.com          # 发送ICMP包，测试网络是否通
ping -c 4 8.8.8.8        # 只发4个包（-c=count）
```

工作原理：向目标发ICMP Echo Request，目标回复ICMP Echo Reply。就像喊一声"在吗？"，对方回"在！"。`ping` 还能告诉你往返时间（RTT），是诊断网络延迟的第一步。

### netstat / ss：查看网络连接

```bash
netstat -tlnp                # 查看所有监听的TCP端口
netstat -an | grep 8080      # 查看8080端口的情况
ss -tlnp                     # ss是netstat的现代替代品，更快
```

`-tlnp` 含义：
- `-t`：TCP连接
- `-l`：只显示正在监听（listening）的
- `-n`：显示数字（不把端口号转为服务名，更快）
- `-p`：显示进程名

输出示例：
```
Proto  Local Address    State       PID/Program name
tcp    0.0.0.0:8080     LISTEN      1234/myapp
tcp    127.0.0.1:3306   LISTEN      5678/mysqld
```

第一行：`myapp` 在监听所有网卡的8080端口（外网可以访问）
第二行：`mysqld` 只在本地监听3306端口（只有本机可以访问，安全！）

### curl：命令行HTTP客户端

```bash
curl http://localhost:8080/api/users       # GET请求
curl -X POST http://localhost:8080/api/users \
  -H "Content-Type: application/json" \
  -d '{"name":"Alice"}'                      # POST请求+请求体
curl -I https://google.com                  # 只看响应头（HEAD请求）
curl -v https://example.com                 # 详细输出（调试神器）
```

`curl` 是后端工程师调试API的第一利器。不用打开Postman，不用写代码，一条命令就能验证接口。

### wget：命令行下载工具

```bash
wget https://example.com/file.tar.gz        # 下载文件
wget -O myfile.tar.gz https://...           # 指定保存文件名
wget -c https://example.com/large.zip       # 断点续传
```

### traceroute：追踪路由路径

```bash
traceroute google.com        # 显示数据包经过的每一跳路由器
```

这个命令能让你看到从你的服务器到目标地址经过了哪些中间节点，以及每一跳的延迟。是诊断"为什么我的服务器连不到Google"的利器。

---

## 99.7 压缩解压

### tar：打包（最常用的压缩工具）

```bash
tar -czf archive.tar.gz myfolder/     # 打包并gzip压缩（c=create, z=gzip, f=file）
tar -xzf archive.tar.gz               # 解压到当前目录（x=extract）
tar -xzf archive.tar.gz -C /tmp/      # 解压到指定目录（-C=directory）
tar -czf backup.tar.gz --exclude=*.log /var/log/   # 排除.log文件
tar -tzf archive.tar.gz               # 只看内容不解压（t=list）
```

记忆技巧：
- `c` = **c**reate（创建/打包）
- `x` = e**x**tract（解压）
- `z` = g**z**ip（压缩）
- `f` = **f**ile（指定文件名，必须放最后）
- `v` = **v**erbose（显示详细信息，可选）

### gzip / gunzip：直接压缩文件

```bash
gzip largefile.txt         # 压缩，生成largefile.txt.gz（原文件被删除）
gunzip largefile.txt.gz    # 解压
gzip -k largefile.txt      # -k保留原文件
```

### bzip2 / bunzip2：更高压缩率

```bash
bzip2 largefile.txt        # 比gzip压得更小，但更慢
bunzip2 largefile.txt.bz2
tar -cjf archive.tar.bz2 myfolder/    # j=bzip2
```

### zip / unzip：兼容Windows

```bash
zip -r archive.zip myfolder/       # -r递归打包目录
unzip archive.zip
unzip -l archive.zip               # 只看内容
```

---

## 99.8 包管理器

### apt（Debian/Ubuntu系）

```bash
sudo apt-get update                  # 更新软件源列表（查"菜单"有什么新菜）
sudo apt-get upgrade                 # 升级所有已安装的软件
sudo apt-get install nginx           # 安装软件
sudo apt-get remove nginx            # 卸载（保留配置文件）
sudo apt-get purge nginx             # 彻底卸载（连配置文件一起删）
sudo apt-get autoremove              # 删除不再需要的依赖包
apt-cache search redis               # 搜索软件包
apt-cache show nginx                 # 查看软件包详细信息
```

### yum（RHEL/CentOS/Fedora系）

```bash
sudo yum update                  # 升级所有软件
sudo yum install nginx           # 安装
sudo yum remove nginx            # 卸载
sudo yum search redis            # 搜索
sudo yum info nginx              # 查看信息
```

> 现代CentOS/Fedora推荐用 `dnf`（yum的下一代），命令基本一样，把 `yum` 换成 `dnf` 就行。

### 软件源（repository）是什么

包管理器不直接维护软件包——它维护的是**软件源**（repository）的地址列表。当你执行 `apt-get install nginx` 时：

1. 去 `/etc/apt/sources.list` 配置的源地址拉取软件包索引
2. 找到nginx的最新版本
3. 下载nginx和它依赖的所有包
4. 自动安装到正确的位置

这就是为什么你要先 `apt-get update`——因为本地缓存的索引可能过期了，需要重新拉取。

---

## 99.9 systemd服务管理

### systemd是什么

systemd是Linux系统的"大管家"，PID永远为1——它是所有进程的祖先。systemd负责：
- 启动系统（按顺序启动所有服务）
- 管理服务（启动/停止/重启/状态查看）
- 日志管理（journalctl）

### 编写一个systemd服务文件

把Go程序变成系统服务，让它开机自启、崩溃自动重启。在 `/etc/systemd/system/` 下创建 `.service` 文件：

```ini
[Unit]
Description=My Go Web Application
After=network.target
Documentation=https://myapp.com/docs

[Service]
Type=simple
User=myapp
Group=myapp
WorkingDirectory=/opt/myapp
ExecStart=/opt/myapp/myapp
ExecReload=/bin/kill -HUP $MAINPID
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal
SyslogIdentifier=myapp
EnvironmentFile=/opt/myapp/.env
LimitNOFILE=65536

[Install]
WantedBy=multi-user.target
```

**字段详解：**

`[Unit]` — 基本信息：
- `Description`：服务描述
- `After=network.target`：等网络就绪后再启动（否则你的程序连不上数据库）
- `Documentation`：可选的文档链接

`[Service]` — 核心配置：
- `Type=simple`：最简单的类型，systemd认为ExecStart启动后服务就起来了
- `User`/`Group`：以哪个用户身份运行（**不要用root！**）
- `WorkingDirectory`：工作目录
- `ExecStart`：启动命令（必须用绝对路径）
- `ExecReload`：重新加载配置的命令（非重启）
- `Restart=always`：无论什么原因退出都自动重启
- `RestartSec=5`：重启前等5秒（防止疯狂重启）
- `StandardOutput/StandardError=journal`：输出到systemd日志
- `EnvironmentFile`：从文件加载环境变量
- `LimitNOFILE=65536`：最大可打开文件数（高并发程序必须设）

`[Install]` — 安装信息：
- `WantedBy=multi-user.target`：在多用户模式启动（正常服务器模式）

### systemctl命令

```bash
sudo systemctl daemon-reload           # 修改service文件后重载配置
sudo systemctl enable myapp            # 设置开机自启
sudo systemctl disable myapp           # 取消开机自启
sudo systemctl start myapp             # 启动
sudo systemctl stop myapp              # 停止
sudo systemctl restart myapp           # 重启（先stop再start）
sudo systemctl reload myapp            # 重新加载配置（不中断服务）
sudo systemctl status myapp            # 查看状态（是否运行、PID、最近日志）
sudo systemctl is-active myapp         # 检查是否在运行

journalctl -u myapp -f                 # 实时查看myapp的日志
journalctl -u myapp --since "1 hour ago"  # 查看最近1小时的日志
journalctl -u myapp -n 100             # 查看最近100行日志
```

### 实战：部署Go应用到systemd

```bash
sudo cp /home/alice/myapp /opt/myapp/myapp

sudo nano /etc/systemd/system/myapp.service

sudo systemctl daemon-reload
sudo systemctl enable myapp
sudo systemctl start myapp
sudo systemctl status myapp
```

现在你的Go程序就是系统服务了——服务器重启后自动启动，崩溃后自动恢复。

---

## 99.10 文本处理三剑客

后端工程师60%的时间都在处理文本：看日志、过滤数据、修改配置文件。grep、sed、awk就是三把瑞士军刀。

### grep：搜索文本

```bash
grep "error" app.log                        # 搜索包含error的行
grep -i "error" app.log                     # -i忽略大小写（Error、ERROR都能匹配）
grep -v "debug" app.log                     # -v反向匹配（不含debug的行）
grep -n "panic" app.log                     # -n显示行号
grep -c "error" app.log                     # -c统计匹配行数
grep -r "TODO" ./src/                       # -r递归搜索目录
grep -E "error|panic|fatal" app.log         # -E使用扩展正则（匹配多个关键词）
grep -A 3 "error" app.log                   # -A 3显示匹配行及其后3行
grep -B 2 "error" app.log                   # -B 2显示匹配行及其前2行
grep -C 5 "error" app.log                   # -C 5显示匹配行及其前后各5行
```

**实战：排查Nginx 502错误**

```bash
grep "502" /var/log/nginx/access.log | tail -20
grep -B 2 -A 5 "upstream timed out" /var/log/nginx/error.log
```

### sed：流编辑器（修改文本）

```bash
sed 's/old/new/' file.txt                   # 替换每行第一个old为new
sed 's/old/new/g' file.txt                  # g=全局替换（一行中所有）
sed 's/old/new/2' file.txt                  # 替换每行第2个匹配
sed '3s/old/new/' file.txt                  # 只替换第3行
sed 's/old/new/g' file.txt > new.txt        # 输出到新文件（原文件不变）
sed -i 's/old/new/g' file.txt               # -i直接修改原文件（小心！）
sed -i.bak 's/old/new/g' file.txt           # 修改前备份为.bak文件
sed '/error/d' app.log                      # 删除包含error的行
sed -n '10,20p' app.log                     # 只打印第10到20行
```

**实战：批量修改配置文件**

```bash
sed -i 's/127.0.0.1/0.0.0.0/g' /etc/nginx/nginx.conf
sed -i 's|/var/www|/opt/web|g' /etc/nginx/sites-enabled/default
```

### awk：数据处理

awk是一种微型编程语言，专门处理按列排列的文本数据。

```bash
awk '{print $1}' access.log                 # 打印第1列
awk '{print $1, $7}' access.log             # 打印第1列和第7列（Nginx日志：IP+URL）
awk '$9 == 200 {print $0}' access.log       # 状态码为200的行
awk '$9 >= 500 {print $1, $9, $7}' access.log  # 服务器错误的IP、状态码、URL
awk '{sum += $1} END {print sum}' data.txt  # 第1列求和
awk -F: '{print $1}' /etc/passwd            # -F:指定分隔符为冒号
awk -F',' '{print $2}' users.csv            # 取CSV第2列
```

**实战：统计Nginx日志中每种状态码的数量**

```bash
awk '{count[$9]++} END {for (code in count) print code, count[code]}' /var/log/nginx/access.log
```

输出：
```
200 15230
301 450
404 89
500 3
```

### 🤔 想多一点：三剑客怎么分工？

| 工具 | 角色 | 用在哪 |
|------|------|--------|
| grep | 筛子 | 从海量数据中找到你想要的行（一行都不漏） |
| sed | 剪刀 | 批量修改文本内容（改配置文件、替换字符串） |
| awk | 计算器 | 处理结构化的列数据（统计、求和、报表） |

一句话总结：**grep负责找，sed负责改，awk负责算。**

---

## 99.11 常用命令速查表

### 文件与目录

| 命令 | 说明 |
|------|------|
| `ls -la` | 列出所有文件（含隐藏），详细模式 |
| `cd /path` | 切换目录 |
| `pwd` | 显示当前目录的绝对路径 |
| `mkdir -p a/b/c` | 递归创建目录 |
| `rm -rf dir/` | 强制递归删除（**非常危险，三思后行**） |
| `cp -r src/ dst/` | 递归复制 |
| `mv old new` | 移动/重命名 |
| `ln -s /target link` | 创建软链接（快捷方式） |
| `find . -name "*.go"` | 在当前目录及子目录找.go文件 |

### 文件查看

| 命令 | 说明 |
|------|------|
| `cat file` | 输出整个文件内容 |
| `less file` | 分页查看（上下翻，q退出） |
| `head -n 20 file` | 看前20行 |
| `tail -n 20 file` | 看最后20行 |
| `tail -f file` | 实时追踪（看日志神器） |
| `wc -l file` | 统计行数 |

### 权限

| 命令 | 说明 |
|------|------|
| `chmod 755 file` | 设为rwxr-xr-x |
| `chmod 644 file` | 设为rw-r--r-- |
| `chown user:group file` | 改所有者和组 |

### 进程

| 命令 | 说明 |
|------|------|
| `ps aux` | 查看所有进程 |
| `top` / `htop` | 实时监控 |
| `kill -9 PID` | 强制杀进程 |
| `nohup cmd &` | 后台运行不挂断 |
| `Ctrl+C` | 终止前台进程 |
| `Ctrl+Z` | 暂停前台进程 |

### 网络

| 命令 | 说明 |
|------|------|
| `ping host` | 测连通性 |
| `ss -tlnp` | 看监听端口 |
| `curl URL` | HTTP请求 |
| `wget URL` | 下载文件 |
| `scp file user@host:/path` | 安全复制到远程服务器 |

### 系统

| 命令 | 说明 |
|------|------|
| `df -h` | 磁盘空间 |
| `du -sh dir/` | 目录大小 |
| `free -h` | 内存使用 |
| `uname -a` | 系统信息 |
| `uptime` | 系统运行时间和负载 |
| `who` | 当前登录的用户 |
| `history` | 命令历史 |

### systemd

| 命令 | 说明 |
|------|------|
| `systemctl start name` | 启动服务 |
| `systemctl stop name` | 停止服务 |
| `systemctl restart name` | 重启服务 |
| `systemctl status name` | 查看状态 |
| `systemctl enable name` | 开机自启 |
| `journalctl -u name -f` | 实时日志 |

---

## 本章小结

| 知识点 | 要点 |
|--------|------|
| 目录结构 | 一切从 `/` 开始，没有盘符概念 |
| /etc | 配置文件大本营，修改系统行为从这里入手 |
| /var | 变化数据：日志、数据库、缓存 |
| /home | 普通用户的家目录 |
| /proc | 虚拟文件系统，内存中的进程和系统信息 |
| 权限模型 | u/g/o × r/w/x，数字表示（4读2写1执行） |
| chmod | 755程序、644文件、600私钥 |
| 用户管理 | useradd创建、passwd设密码、usermod改属性 |
| root | UID=0，全能但危险，日常用sudo |
| 进程管理 | ps查看、top监控、kill终止、nohup后台 |
| 网络命令 | ping测连通、ss看端口、curl测API |
| 压缩 | tar -czf打包压缩、tar -xzf解压 |
| 包管理 | apt(Ubuntu)、yum/dnf(CentOS) |
| systemd | 服务管理器，编写.service文件，systemctl控制 |
| 三剑客 | grep搜索、sed修改、awk统计 |

> 🚀 下一章：第100章 · Shell脚本基础。现在你学会了Linux的基本操作，下一步是把这些命令串成自动化脚本——备份数据库、部署代码、监控日志，全让脚本替你跑。准备好告别重复的手工操作了吗？

---
[← 上一章：98-系统设计面试经典题.md](98-系统设计面试经典题.md) | [下一章：100-Shell脚本基础.md →](100-Shell脚本基础.md)
