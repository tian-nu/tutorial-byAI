# 第54章 · 数据库基础与MySQL安装

> "从第1章到现在，我们写的所有Java程序都有一个共同的问题——只要程序关了，数据就没了。用户注册了账号、发表的文章、上传的文件，统统消失在内存里。就像你在沙滩上写字，潮水一来全都抹平。数据库，就是那堵水泥墙，刻上去的东西，十年后还在。"

---

## 54.1 什么是数据库

想象你开了一家快递公司。刚开始只有三个客户，你用一张纸就能记下所有信息：

```
张三 - 13800001111 - 北京市朝阳区
李四 - 13800002222 - 上海市浦东新区
王五 - 13800003333 - 广州市天河区
```

后来客户发展到三千个，你翻纸找"李四"找到眼冒金星。你又用Excel建了个表，可以筛选、排序、搜索，爽了几天。

再后来客户到了三十万。Excel打开都要卡三分钟，而且你和同事同时编辑时就乱了——他改他的，你改你的，保存时互相覆盖。

**数据库**就是解决这些问题的终极方案。你可以把它想象成一个**全自动的电子化仓库**：

| 仓库概念 | 数据库概念 | 说明 |
|----------|-----------|------|
| 仓库本身 | Database（数据库） | 存放所有数据的大房子 |
| 货架 | Table（表） | 同一类东西放在同一个货架上 |
| 周转箱 | Row（行） | 一条完整的记录 |
| 箱子里的每个物品 | Column（列） | 记录的某个属性 |

Excel是一张纸，一个人趴在上面用笔改。数据库是一个全自动仓库，有传送带、机械臂、监视器，可以**同时服务几千个人**而不混乱。

> **数据库的核心能力**：存（增）、查、改、删——简称**CRUD**（Create、Read、Update、Delete），同时保证多人操作不出错。

> 🤔 **想多一点**：你可能会问——"都2026年了，为什么不直接用Excel存数据？"
>
> 1. **并发冲突**：Excel被小王打开后，小李只能以"只读"方式打开，否则互相覆盖。
> 2. **数据量限制**：Excel超过10万行就开始卡，数据库轻松处理亿级数据。
> 3. **关联复杂**：你的用户表和订单表需要关联查询，Excel只能用VLOOKUP死撑。
> 4. **安全控制**：数据库可以精确到"小李只能查用户表，不能改"、"小王只能查自己负责的订单"。
> 5. **崩溃恢复**：数据库写一半断电了，重启后能自动恢复到一致状态，Excel直接文件损坏。

---

## 54.2 关系型数据库 vs 非关系型数据库

数据库世界分为两大门派：

### 关系型数据库（SQL数据库）

**比喻**：一个**格式极其严格的仓库**。每个货架（表）在放东西之前，必须先定义好每层放什么类型的东西。第一个格子只能放整数，第二个格子只能放不超过50个字的文本……所有货架之间还可以用"编号"互相引用。

- 代表选手：**MySQL**、PostgreSQL、Oracle、SQL Server
- 数据以**表**的形式组织，表和表之间通过**外键**建立关系
- 使用**SQL**（Structured Query Language，结构化查询语言）操作，所有关系型数据库的SQL大同小异
- 适合：用户系统、电商订单、银行账目——总之，**结构固定、数据之间有关联**的场景

### 非关系型数据库（NoSQL数据库）

**比喻**：不设固定格式，想放什么就放什么。有三种典型代表：

**Redis = 大脑中的便签纸**

写一个字只要0.00001秒，但容量受限于内存，关机就忘（但可以"拍照"存到硬盘）。适合：临时缓存、实时排行榜、消息队列。

**MongoDB = 文件柜**

不需要预先设计表格结构，直接把一沓文档（JSON格式）塞进柜子。适合：日志记录、内容管理系统、数据结构频繁变动的场景。

**Elasticsearch = 超级搜索引擎**

扔进去一堆文本，它能帮你瞬间找到包含某个关键词的所有内容。适合：全文搜索、日志分析。

| 对比维度 | 关系型（如MySQL） | 非关系型（如Redis/MongoDB） |
|----------|------------------|---------------------------|
| 数据结构 | 严格，先定义表结构 | 灵活，随存随改 |
| 关联能力 | 强（JOIN、外键） | 弱或无 |
| 事务支持 | 完善（ACID） | 有限或不支持 |
| 扩展方式 | 垂直扩展为主 | 水平扩展方便 |
| 典型场景 | 金融、电商、ERP | 缓存、搜索、日志 |

**本书的策略**：MySQL作为主力学透，Redis作为"性能加速器"重点学，MongoDB了解即可。

---

## 54.3 数据库管理系统（DBMS）

数据库本身只是一堆数据文件，需要一个**程序**来管理这些文件。这个程序就是**DBMS**（Database Management System，数据库管理系统）。

```
┌─────────────────────────────────┐
│           你的Java程序            │
│                                 │
│   "SELECT * FROM users          │
│    WHERE age > 18;"             │
│              │                  │
│              ▼                  │
│    ┌─────────────────┐          │
│    │      MySQL       │          │
│    │  (DBMS, 端口3306) │          │
│    └────────┬────────┘          │
│             │                   │
│             ▼                   │
│    ┌─────────────────┐          │
│    │  数据文件 (.ibd等) │          │
│    └─────────────────┘          │
└─────────────────────────────────┘
```

你的Java程序不直接读写数据文件，而是通过**网络连接**（TCP 3306端口）向MySQL发送SQL语句，MySQL替你读写文件，再把结果返回给你。

> **关键认知**：MySQL是一个**服务程序**，像外卖店一样开着门等着你下单。你需要先启动MySQL服务（开店），然后通过客户端连接它（进门点菜），最后发送SQL（下单）。

---

## 54.4 安装MySQL

### 54.4.1 Windows安装

**第一步：下载安装包**

打开浏览器，访问 MySQL 官网下载页面：https://dev.mysql.com/downloads/installer/

选择 `mysql-installer-community-8.0.xx.msi`（约400MB），点击下载。

> 💡 官网会提示登录Oracle账号，点击下方小字 "No thanks, just start my download." 即可跳过。

**第二步：运行安装程序**

双击下载好的 `.msi` 文件，依次操作：

1. **Choosing a Setup Type**：选择 `Developer Default`（开发默认），点击 Next
2. **Check Requirements**：如果提示缺少 Visual C++ Redistributable，点击 Execute 自动安装
3. **Installation**：点击 Execute 开始安装所有组件
4. **Product Configuration**：
   - **Type and Networking**：保持默认端口 `3306`，点击 Next
   - **Authentication Method**：选择 `Use Strong Password Encryption`，点击 Next
   - **Accounts and Roles**：设置 root 密码。**输入两遍你记住的密码**，例如 `YourPassword123!`。点击 Next
   - **Windows Service**：确保 `Configure MySQL Server as a Windows Service` 打勾，Service Name 为 `MySQL80`，勾选 `Start the MySQL Server at System Startup`（开机自启）。点击 Next
5. **Apply Configuration**：点击 Execute，等待所有配置项打上绿色对勾，点击 Finish

**第三步：验证安装**

打开 **命令提示符（cmd）** 或 **PowerShell**，输入：

```powershell
mysql -u root -p
```

输入你刚才设置的root密码。如果看到 `mysql>` 提示符，安装成功。

输入 `exit` 退出。

**第四步：配置PATH环境变量（可选但推荐）**

如果提示 `'mysql' 不是内部或外部命令`，需要把MySQL的bin目录加入PATH：

1. 找到MySQL安装路径，通常为 `C:\Program Files\MySQL\MySQL Server 8.0\bin`
2. 右键"此电脑" → 属性 → 高级系统设置 → 环境变量
3. 在系统变量中找到 `Path`，双击 → 新建 → 粘贴上面的路径
4. 确定保存，**重新打开命令行窗口**后再试

### 54.4.2 macOS安装

**方式一：官方安装包（推荐新手）**

1. 访问 https://dev.mysql.com/downloads/mysql/ 下载 `.dmg` 文件
2. 双击 `.dmg`，再双击 `.pkg` 安装文件
3. 按提示操作，在安装过程中会显示一个**临时root密码**，**务必截图保存**
4. 安装完成后，打开"系统偏好设置" → 底部找到 MySQL 图标 → 点击 "Start MySQL Server"
5. 验证：

```bash
# 将MySQL加入PATH
echo 'export PATH="/usr/local/mysql/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc

# 用临时密码登录
mysql -u root -p

# 登录后立即修改密码
ALTER USER 'root'@'localhost' IDENTIFIED BY 'YourNewPassword123!';
```

**方式二：Homebrew（熟悉命令行的用户）**

```bash
brew install mysql
brew services start mysql

# 初始无密码，直接登录后设置
mysql -u root
ALTER USER 'root'@'localhost' IDENTIFIED BY 'YourPassword123!';
```

### 54.4.3 Linux安装（以Ubuntu为例）

```bash
# 1. 更新包列表
sudo apt update

# 2. 安装MySQL Server
sudo apt install mysql-server -y

# 3. 运行安全配置向导（设置root密码、删除匿名用户等）
sudo mysql_secure_installation

# 4. 检查服务状态
sudo systemctl status mysql

# 5. 验证登录
mysql -u root -p
```

> ⚠️ Ubuntu 22.04+ 默认使用 `auth_socket` 认证，安装后可能无法直接用密码登录。需要先 `sudo mysql` 进入，然后执行：
> ```sql
> ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'YourPassword123!';
> FLUSH PRIVILEGES;
> ```

---

## 54.5 安装DBeaver图形化工具

命令行虽然强大，但看表结构、浏览数据时，图形工具效率高得多。**DBeaver** 是完全免费的开源数据库管理工具，支持MySQL、PostgreSQL、Oracle等几乎所有数据库。

### 安装步骤

1. 访问 https://dbeaver.io/download/ 下载对应系统的安装包
2. Windows双击 `.exe`，macOS拖入Applications，Linux用 `sudo dpkg -i dbeaver-*.deb`
3. 启动DBeaver

### 连接MySQL

1. 点左上角 **新建连接** 按钮（蓝色插头图标），或按 `Ctrl+N`
2. 在弹出的窗口中选择 **MySQL**，点击下一步
3. 填写连接信息：
   - **Server Host**: `localhost`
   - **Port**: `3306`
   - **Database**: 留空（连接后会显示所有数据库）
   - **Username**: `root`
   - **Password**: 你设置的密码
4. 点击左下角 **Test Connection**。首次连接会提示下载MySQL驱动，点击 **Download** 自动下载
5. 看到 "Connected" 提示后，点击完成
6. 左侧导航栏展开连接，就能看到 `sys`、`mysql` 等系统数据库

> 💡 DBeaver左侧导航栏的操作方式：右键数据库名 → "SQL Editor" → "New SQL Script" 打开查询窗口。或者直接按 `F3` 打开SQL编辑器。

---

## 54.6 数据库服务器的日常管理

### 启动与停止

**Windows**：
- 方法一：Win+R 输入 `services.msc`，找到 `MySQL80`，右键启动/停止
- 方法二（管理员PowerShell）：
  ```powershell
  net start MySQL80   # 启动
  net stop MySQL80    # 停止
  ```

**macOS**：
```bash
# 官方安装方式
sudo /usr/local/mysql/support-files/mysql.server start
sudo /usr/local/mysql/support-files/mysql.server stop

# Homebrew方式
brew services start mysql
brew services stop mysql
```

**Linux**：
```bash
sudo systemctl start mysql
sudo systemctl stop mysql
sudo systemctl restart mysql
```

### 确认MySQL正在运行

**Windows/macOS/Linux通用**：
```bash
mysqladmin -u root -p ping
```
输出 `mysqld is alive` 表示正在运行。

或者查看端口是否被监听：
```bash
# Windows
netstat -ano | findstr 3306

# macOS/Linux
sudo lsof -i :3306
```

---

## 54.7 常见安装问题

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| `mysql: command not found` | MySQL的bin目录未加入PATH | 参考54.4.1第四步配置环境变量 |
| `Can't connect to MySQL server on 'localhost' (10061)` | MySQL服务未启动 | Windows在services.msc中启动MySQL80，macOS/Linux用对应启动命令 |
| `Access denied for user 'root'@'localhost'` | 密码错误 | 确认密码无误，或重置密码 |
| `Port 3306 already in use` | 端口被占用 | 已有其他MySQL实例在运行，或别的程序占用了3306端口 |
| macOS安装后提示密码过期 | 临时密码有有效期 | 用临时密码登录后立即执行 `ALTER USER` 修改密码 |
| DBeaver连接报 "Public Key Retrieval is not allowed" | MySQL 8.0默认认证方式 | 在DBeaver连接设置的Driver properties中，将 `allowPublicKeyRetrieval` 设为 `true`，`useSSL` 设为 `false` |

> 🤔 **想多一点**：为什么安装数据库这么麻烦，而安装一个App只要点一下？
>
> 因为App是给**普通用户**用的，要简单。MySQL是给**开发者**用的，要灵活——它需要让你选择端口、认证方式、字符集、存储路径、内存大小……这些配置直接影响生产环境的性能和安全。安装时的"麻烦"实际上是在教你认识它的每一个零件。等你真正部署到生产环境时，这些零件你都要亲手调。

---

## 本章小结

| 概念 | 要点 |
|------|------|
| 数据库 | 持久化存储数据的系统，解决Excel的并发、容量、安全等局限 |
| 关系型数据库 | 以表结构存储，用SQL操作，代表MySQL，适合结构化数据 |
| 非关系型数据库 | 灵活存储，包括Redis（缓存）、MongoDB（文档）、ES（搜索） |
| DBMS | 数据库管理系统，MySQL是服务程序，监听3306端口 |
| DBeaver | 免费开源的图形化管理工具，替代命令行的日常操作 |
| 安装核心 | 下载→安装→设root密码→启动服务→验证连接 |

---

## 自测题

1. **一个电商系统有用户表、订单表、商品表，这些表之间通过外键互相关联。应该选关系型还是非关系型数据库？为什么？**

2. **MySQL安装完成后，在命令行输入 `mysql -u root -p` 提示 `'mysql' is not recognized as an internal or external command`，怎么解决？**

3. **DBeaver连接MySQL时报错 "Public Key Retrieval is not allowed"，如何处理？**

<details>
<summary>参考答案（做完再看）</summary>

1. 选关系型数据库（如MySQL）。因为用户、订单、商品之间有严格的关联关系（订单关联用户ID和商品ID），关系型数据库的JOIN查询和外键约束天生适合这种场景。如果用MongoDB，做这种关联查询会很绕。

2. MySQL的bin目录没有被加入系统PATH环境变量。解决方法：找到MySQL安装目录下的bin文件夹（通常为 `C:\Program Files\MySQL\MySQL Server 8.0\bin`），将其添加到系统环境变量Path中，重新打开命令行窗口即可。

3. MySQL 8.0默认使用 `caching_sha2_password` 认证插件，DBeaver连接时需要在Driver Properties中添加两个属性：`allowPublicKeyRetrieval=true` 和 `useSSL=false`（仅开发环境）。或者用命令行登录后执行 `ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY '你的密码';` 改用传统认证方式。
</details>