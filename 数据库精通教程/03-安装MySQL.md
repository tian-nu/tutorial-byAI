# 03 — 安装 MySQL 与环境配置

> - 对应文档版本：database_mastery_outline.md v1, database_mastery_detailed_outline.md v2
> - 适用环境：Windows / macOS / Linux
> - 读者角色：数据库零基础的开发者（需有终端基础）
> - 预计耗时：新手 60 分钟 / 熟手 15 分钟
> - 前置教程：第 01、02、02b 章
> - 可视化：无

---

## 我在做什么？

前 3 章我们一直在"纸上谈兵"——讲概念、画表格、聊分类。现在，该动手了。

这一章，你会在自己的电脑上安装 **MySQL Server** *此术语见附录E*（数据库核心服务）和 **MySQL Workbench** *此术语见附录E*（图形化管理工具），然后执行你的第一条数据库命令。

学完这一章，你的终端里会显示 `mysql>` 提示符——这意味着你拥有了一个真正可用的数据库。

---

## 一、安装前的准备

### 你需要知道的东西

- **MySQL 是什么**：一种关系型数据库管理系统（DBMS），由 Oracle 公司维护。社区版免费。
- **MySQL 的架构**：分为 **Server**（后台服务，负责存取数据）和 **Client**（客户端，你用来连接 Server 的工具）。你需要两个都装。
- **MySQL 的默认端口**：**3306** *此术语见附录E*。这是 MySQL 的"门牌号"，后面排错时会用到。

### 选择安装版本

| 版本 | 说明 |
|------|------|
| **MySQL Community Server** | 免费社区版，我们用的就是这个 |
| MySQL Installer（Windows） | Windows 平台的向导式安装包，包含 Server + Workbench |

> ⚠️ **安全提醒**：以下所有命令中的 `your_password_here` 请替换为你自己的密码。**不要用 123456、password、admin 等弱密码，也不要和你的其他账户密码相同。**

---

## 二、Windows 安装

### 步骤 1：下载 MySQL Installer

1. 打开浏览器，访问 [MySQL 官方下载页](https://dev.mysql.com/downloads/installer/)。
2. 选择 **Windows (x86, 32-bit), MSI Installer** 中**文件较大**的那个（通常约 400MB，标注 "mysql-installer-community-8.x.x.msi"）。选大的那个是因为它包含了 Server 和 Workbench，不需要在线下载额外组件。
3. 点击 "No thanks, just start my download." 开始下载。

### 步骤 2：运行安装向导

1. 双击下载的 `.msi` 文件。
2. 选择安装类型：**Custom**（自定义），这样你可以看到选择了哪些组件。

> 为什么选 Custom？因为可以确保同时安装 Server 和 Workbench。选 "Developer Default" 也可以，但会安装很多你可能暂时用不上的东西。

3. 在组件列表中，确保勾选：
   - **MySQL Server 8.x**（核心服务）
   - **MySQL Workbench 8.x**（图形化管理工具）
4. 点击 Next，然后 Execute，等待安装完成。

### 步骤 3：配置 MySQL Server

安装完成后，安装向导会自动进入配置阶段：

1. **Type and Networking**：保持默认（Development Computer，Port 3306），点击 Next。
2. **Authentication Method**：选择 **Use Strong Password Encryption for Authentication**（推荐），点击 Next。
3. **Accounts and Roles**：
   - 设置 **root 密码**（root 是 MySQL 的超级管理员账户）*此术语见附录E*。输入两次你选定的密码，务必记住。
   - 可以点击 "Add User" 创建一个普通用户，但暂时不创建也可以。
4. **Windows Service**：
   - 确保 "Configure MySQL Server as a Windows Service" 已勾选。
   - Windows Service Name 保持默认 `MySQL80`。
   - 勾选 "Start the MySQL Server at System Startup"（开机自启动，推荐）。
5. 点击 Next → Execute，等待配置完成。

### 步骤 4：验证安装

打开 **命令提示符**（Win+R → 输入 `cmd` → 回车），输入：

```bash
mysql -u root -p
```

输入你在步骤 3 设置的 root 密码。如果看到以下内容，说明安装成功：

```
Welcome to the MySQL monitor.  Commands end with ; or \g.
Your MySQL connection id is 8
Server version: 8.x.x MySQL Community Server - GPL
...
mysql>
```

在 `mysql>` 提示符下输入：

```sql
SELECT VERSION();
```

你应该看到类似输出：

```
+-----------+
| VERSION() |
+-----------+
| 8.x.x    |
+-----------+
1 row in set (0.00 sec)
```

输入 `exit` 退出 MySQL 命令行。

### 步骤 5：认识 MySQL Workbench

MySQL Workbench 是官方提供的图形化工具。安装后从开始菜单打开 "MySQL Workbench 8.0 CE"。

界面分为三个主要区域：

```
┌──────────────────────────────────────────────────────────┐
│  MySQL Workbench                                        │
├────────────────────┬─────────────────────────────────────┤
│                    │                                     │
│   连接管理面板      │      工作区                         │
│   (左侧)          │      (右侧)                          │
│                    │                                     │
│  ┌──────────────┐ │  ┌─────────────────────────────────┐│
│  │ MySQL         │ │  │  SQL 编辑器                     ││
│  │ Connections   │ │  │  (在这里写 SQL)                 ││
│  │  ├─ local     │ │  │                                 ││
│  │  └─ ...       │ │  └─────────────────────────────────┘│
│  └──────────────┘ │  ┌─────────────────────────────────┐│
│                    │  │  结果面板                        ││
│                    │  │  (查询结果在这里显示)             ││
│                    │  └─────────────────────────────────┘│
└────────────────────┴─────────────────────────────────────┘
```

双击你创建的连接（通常是 `Local instance MySQL80`），输入 root 密码，就进入了 SQL 编辑器。

**做一个快速测试**：在 SQL 编辑器里输入 `SELECT VERSION();`，点击上方的 ⚡（闪电）图标执行，结果面板会显示版本号。

---

## 三、macOS 安装

### 步骤 1：使用 Homebrew 安装

如果你还没有 Homebrew，先安装它（打开终端，粘贴以下命令）：

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

安装 MySQL：

```bash
brew install mysql
```

### 步骤 2：启动 MySQL 服务

```bash
brew services start mysql
```

输出类似 `==> Successfully started mysql` 即为成功。

### 步骤 3：安全配置

```bash
mysql_secure_installation
```

按提示操作：
1. 是否设置 VALIDATE PASSWORD 组件？→ 输入 `y`，然后选择密码强度（建议选 `2` = STRONG）。
2. 输入 root 密码（两次）。
3. Remove anonymous users?（删除匿名用户）→ `y`
4. Disallow root login remotely?（禁止 root 远程登录）→ `y`
5. Remove test database?（删除测试库）→ `y`
6. Reload privilege tables?（重新加载权限表）→ `y`

### 步骤 4：验证安装

```bash
mysql -u root -p
```

输入密码后，执行：

```sql
SELECT VERSION();
SHOW DATABASES;
```

如果看到版本号和数据库列表，安装成功。

### 步骤 5：安装 MySQL Workbench（可选）

从 [MySQL 官网](https://dev.mysql.com/downloads/workbench/) 下载 macOS 版 Workbench 安装。或者你可以继续使用终端——所有操作终端都能完成。

---

## 四、Linux 安装（Ubuntu / Debian）

### 步骤 1：安装 MySQL Server

```bash
sudo apt update
sudo apt install mysql-server -y
```

### 步骤 2：检查服务状态

```bash
sudo systemctl status mysql
```

如果服务没有启动，手动启动：

```bash
sudo systemctl start mysql
```

设置开机自启动：

```bash
sudo systemctl enable mysql
```

### 步骤 3：安全配置

```bash
sudo mysql_secure_installation
```

操作内容与 macOS 的步骤 3 相同。

### 步骤 4：修改 root 认证方式（Ubuntu 特定）

Ubuntu 默认使用 `auth_socket` 插件认证，这意味着 root 用户只能通过 `sudo mysql` 登录。如果你想让 `mysql -u root -p` 也能工作：

```bash
sudo mysql
```

进入 MySQL 后执行：

```sql
ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'your_password_here';
FLUSH PRIVILEGES;
EXIT;
```

之后就可以用 `mysql -u root -p` 登录了。

### 步骤 5：验证安装

```bash
mysql -u root -p -e "SELECT VERSION();"
```

如果直接返回版本号，安装成功。

---

## 四、Linux 安装（CentOS / RHEL / Fedora）

### 步骤 1：安装 MySQL Server

```bash
sudo yum install mysql-server -y
# 或对于较新版本：sudo dnf install mysql-server -y
```

### 步骤 2：启动服务

```bash
sudo systemctl start mysqld
sudo systemctl enable mysqld
```

### 步骤 3：获取临时密码

MySQL 安装后会生成一个临时密码：

```bash
sudo grep 'temporary password' /var/log/mysqld.log
```

输出类似：

```
[Note] A temporary password is generated for root@localhost: aB3!xYz9pQ
```

记下 `aB3!xYz9pQ` 这部分（你的会和这个不同）。

### 步骤 4：安全配置

```bash
sudo mysql_secure_installation
```

先用临时密码登录，然后按提示设置新密码，其余步骤与前述相同。

### 步骤 5：验证安装

```bash
mysql -u root -p -e "SELECT VERSION();"
```

---

## 我做得对不对？

### 验证方法

打开终端，执行以下命令：

```bash
mysql -u root -p -e "SELECT VERSION();"
```

如果你看到类似以下输出，恭喜你——MySQL 安装成功！

```
+-----------+
| VERSION() |
+-----------+
| 8.0.37    |
+-----------+
```

继续执行：

```bash
mysql -u root -p -e "SHOW DATABASES;"
```

你应该看到：

```
+--------------------+
| Database           |
+--------------------+
| information_schema |
| mysql              |
| performance_schema |
| sys                |
+--------------------+
```

这 4 个是 MySQL 自带的系统数据库，**不要动它们**。

---

## 不对怎么办？

以下是安装 MySQL 时最常遇到的 5 个问题及排错方法。

### 问题 1：MySQL 服务未启动

**症状**：`mysql -u root -p` 报错：

```
ERROR 2003 (HY000): Can't connect to MySQL server on 'localhost:3306' (10061)
```

**原因**：MySQL Server 服务没有运行。

**排查**：

Windows：
1. 按 `Win+R`，输入 `services.msc`，回车。
2. 找到 `MySQL80`（或类似名称），查看状态是否为"正在运行"。
3. 如果没运行，右键 → 启动。

macOS / Linux：
```bash
# macOS
brew services list | grep mysql

# Linux
sudo systemctl status mysql
# 或
sudo systemctl status mysqld
```

如果服务未运行：
```bash
# macOS
brew services start mysql

# Linux
sudo systemctl start mysql
```

### 问题 2：root 密码忘记

**症状**：`mysql -u root -p` 提示输入密码，但你忘了。

**解决方法 A（还有机会时）**：如果之前运行过 `mysql_secure_installation`，可以再次运行它来重置密码：

```bash
sudo mysql_secure_installation
```

**解决方法 B（Linux 安全模式）**：

```bash
# 停止 MySQL
sudo systemctl stop mysql

# 以安全模式启动（跳过权限验证）
sudo mysqld_safe --skip-grant-tables &

# 无密码登录
mysql -u root

# 在 MySQL 中重置密码
FLUSH PRIVILEGES;
ALTER USER 'root'@'localhost' IDENTIFIED BY 'your_new_password_here';
EXIT;

# 停止安全模式
sudo killall mysqld
sudo systemctl start mysql
```

**解决方法 C（Windows）**：
1. 停止 MySQL 服务（`services.msc` → 找到 MySQL80 → 停止）。
2. 以管理员身份打开命令提示符，进入 MySQL 安装目录的 `bin` 文件夹（如 `C:\Program Files\MySQL\MySQL Server 8.0\bin`）。
3. 执行：`mysqld --skip-grant-tables --console`
4. 另开一个命令提示符，输入 `mysql -u root`（无需密码）。
5. 执行 `FLUSH PRIVILEGES;` 然后 `ALTER USER 'root'@'localhost' IDENTIFIED BY 'your_new_password_here';`。
6. 关闭两个窗口，重新启动 MySQL 服务。

### 问题 3：端口 3306 被占用

**症状**：MySQL 启动失败，日志提示 `Can't start server: Bind on TCP/IP port: No such file or directory` 或 `Address already in use`。

**原因**：端口 3306 已经被其他程序占用（可能是另一个 MySQL 实例、或其他数据库软件）。

**排查**：

Windows：
```bash
netstat -an | findstr 3306
```

macOS / Linux：
```bash
sudo lsof -i :3306
```

如果看到有进程占用 3306 端口：
- 如果是旧的 MySQL 进程：`sudo kill <PID>`
- 如果是其他程序：要么停止那个程序，要么修改 MySQL 的端口（修改 `my.cnf` 或 `my.ini` 中的 `port` 参数）。

### 问题 4：权限不足（Permission Denied）

**症状**：Linux/macOS 执行 `mysql_secure_installation` 或 `systemctl start mysql` 时提示 `Permission denied`。

**原因**：需要管理员权限。

**解决**：在命令前加 `sudo`：

```bash
sudo mysql_secure_installation
sudo systemctl start mysql
```

### 问题 5：找不到配置文件（my.ini / my.cnf）

**症状**：你想修改 MySQL 的配置，但不知道配置文件在哪。

**各平台默认路径**：

| 平台 | 路径 |
|------|------|
| Windows | `C:\ProgramData\MySQL\MySQL Server 8.0\my.ini` |
| macOS (Homebrew) | `/usr/local/etc/my.cnf` 或 `/opt/homebrew/etc/my.cnf` |
| Ubuntu/Debian | `/etc/mysql/mysql.conf.d/mysqld.cnf` |
| CentOS/RHEL | `/etc/my.cnf` |

你也可以在 MySQL 中查询：

```sql
SHOW VARIABLES LIKE 'basedir';
SHOW VARIABLES LIKE 'datadir';
```

`basedir` 是安装目录，`my.ini` 或 `my.cnf` 通常在其附近。

---

## 第一个连接：完整流程回顾

从安装到连接，你走过了这些步骤：

```
下载安装包 → 安装 Server + Workbench → 设置 root 密码
    → 启动服务 → 终端连接 (mysql -u root -p)
    → SELECT VERSION(); → 看到版本号 → 安装成功！
```

---

## 本章小结

| 本章学了什么 | 对应命令/概念 | 注意事项 |
|-------------|-------------|---------|
| Windows 安装 MySQL | MySQL Installer → Custom 安装 → 选择 Server + Workbench | 记住 root 密码，不要用弱密码 |
| macOS 安装 MySQL | `brew install mysql` → `brew services start mysql` | 安装后务必运行 `mysql_secure_installation` |
| Linux 安装 MySQL | `apt install mysql-server` 或 `yum install mysql-server` | Ubuntu 需额外配置认证方式；CentOS 需查临时密码 |
| 安全配置 | `mysql_secure_installation` | 删除匿名用户、禁止远程 root、删除 test 库 |
| 第一个连接 | `mysql -u root -p` → `SELECT VERSION();` → `SHOW DATABASES;` | 4 个系统数据库不要动 |
| MySQL Workbench 基础 | 连接管理 → SQL 编辑器 → 结果面板 | Workbench 是辅助工具，核心操作终端也能完成 |
| 排错：服务未启动 | `services.msc`（Win）/ `systemctl status mysql`（Linux） | 最常见的问题，先检查服务状态 |
| 排错：密码忘记 | `mysql_secure_installation` 或安全模式启动 | 不同平台的恢复方法不同，详见本章"不对怎么办" |
| 排错：端口被占用 | `netstat -an \| findstr 3306` / `lsof -i :3306` | 停掉占用端口的进程或修改 MySQL 端口 |
| 排错：权限不足 | 加 `sudo` 前缀 | Linux/macOS 很多操作需要 root 权限 |
| 排错：配置文件找不到 | 各平台默认路径表 | 也可用 `SHOW VARIABLES` 在 MySQL 中查询 |

> **[可暂停点 1/7]**：第一篇结束。恭喜你完成了数据库的基础认知和安装！下次开始前，重启命令：`mysql -u root -p -e "SELECT VERSION();"` 确认连接正常。
>
> 下一篇预告：我们将开始写真正的 SQL 语句 —— 创建数据库和表（DDL）。