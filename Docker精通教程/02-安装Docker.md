# 02 — 安装 Docker

> - 对应文档版本：Docker精通教程 outline v1
> - 适用环境：Windows 10+ / macOS 11+ / Ubuntu 20.04+ / CentOS 7+
> - 读者角色：Docker 零基础，需有终端基础
> - 预计耗时：新手 40 分钟 / 熟手 15 分钟
> - 前置教程：第 01 章（理解 Docker 是什么）
> - 可视化：无

---

## 我在做什么？

上一章你知道了 Docker 是什么、为什么要用它。这一章，我们来把它装到你的电脑上。

装 Docker 这件事，本质上是从"纸上谈兵"到"手握武器"的转折点。装完之后，你就能在终端里敲 `docker version` 看到版本号，敲 `docker run hello-world` 看到那只鲸鱼向你打招呼。

学完这一章，你的电脑上会有一个可以正常工作的 Docker 环境。

---

## 一、安装前的选择：Docker Desktop 还是 Docker Engine？

Docker 有两种安装方式，你只需要选一种：

| | Docker Desktop | Docker Engine |
|------|---------------|--------------|
| **是什么** | 图形化桌面应用，带 GUI 管理界面 | 纯命令行服务，只有后台进程 |
| **包含什么** | Docker Engine + GUI + Kubernetes + 各种工具 | 只有 Docker Engine（dockerd） |
| **适合谁** | 开发者在个人电脑上用 | 服务器（Linux）上用 |
| **平台** | Windows、macOS、Linux | 仅 Linux |

> **简单原则**：个人电脑装 Docker Desktop，服务器装 Docker Engine。本章以 Docker Desktop 为主（覆盖 Windows 和 macOS），Linux 服务器部分给出 Docker Engine 安装步骤。

---

## 二、Windows 安装

### 前置条件

安装前，确认你的电脑满足以下条件：

- **Windows 10 版本 2004 或更高**（Build 19041 及以上）或 Windows 11
- **开启了虚拟化**（在 BIOS 中启用，绝大多数电脑默认开启）
- **至少 4GB 内存**（推荐 8GB，不然跑容器会卡）

> 检查 Windows 版本：按 `Win + R`，输入 `winver`，回车。如果版本号低于 2004，请先升级系统。

### 步骤 1：启用 WSL 2

Docker Desktop 在 Windows 上需要 **WSL 2**（Windows Subsystem for Linux 2）*此术语见附录C* 来提供 Linux 内核。WSL 2 是微软官方的"在 Windows 里跑 Linux"方案，性能比老式的 Hyper-V 虚拟机好很多。

**以管理员身份打开 PowerShell**（右键开始菜单 → Windows PowerShell（管理员）），执行：

```powershell
# 一条命令启用 WSL 2
wsl --install
```

如果命令执行成功，会提示你重启电脑。**重启**。

> 如果你的电脑已经很旧（2018 年以前），`wsl --install` 可能提示不支持。别慌，用备用方案：手动启用 Hyper-V。在"启用或关闭 Windows 功能"中勾选"Hyper-V"，重启即可。Docker Desktop 会自动检测并使用 Hyper-V。

### 步骤 2：下载并安装 Docker Desktop

1. 打开浏览器，访问 [Docker Desktop for Windows 下载页](https://docs.docker.com/desktop/setup/install/windows-install/)。
2. 点击 **Download Docker Desktop for Windows**。
3. 双击下载的 `Docker Desktop Installer.exe`。
4. 安装向导中**确保勾选 "Use WSL 2 instead of Hyper-V"**（推荐，性能更好）。
5. 一路 Next，等待安装完成。
6. 安装完成后，**重启电脑**（Docker Desktop 会提示你重启）。

### 步骤 3：启动 Docker Desktop

1. 重启后，在开始菜单搜索 **Docker Desktop**，打开。
2. 第一次启动会弹出服务协议，点 **Accept**。
3. 等待左下角的鲸鱼图标变成绿色，状态显示 "Engine running"。

> 这里可能需要等 1-2 分钟。如果等了 5 分钟还没好，翻到后面的"排错预案"。

### 步骤 4：验证安装

打开 PowerShell（普通用户即可，不需要管理员），执行：

```bash
docker version
```

你应该看到类似这样的输出（版本号可能不同）：

```
Client:
 Version:           27.x.x
 API version:       1.46
 ...

Server:
 Engine:
  Version:          27.x.x
  ...
```

如果同时看到 `Client` 和 `Server` 的版本信息，说明 Docker 安装成功。

---

## 三、macOS 安装

### 前置条件

- macOS 11（Big Sur）或更高版本
- Intel 芯片或 Apple Silicon（M1/M2/M3/M4）都支持

### 步骤 1：下载并安装 Docker Desktop

**方法一：官网下载（推荐）**

1. 访问 [Docker Desktop for Mac 下载页](https://docs.docker.com/desktop/setup/install/mac-install/)。
2. 根据你的芯片选择：
   - **Apple Silicon**（M1/M2/M3/M4）→ 下载 "Apple Chip" 版本
   - **Intel 芯片** → 下载 "Intel Chip" 版本
3. 双击下载的 `.dmg` 文件。
4. 把 Docker 图标拖到 Applications 文件夹。
5. 在 Applications 中双击 Docker 图标启动。

**方法二：Homebrew 安装（如果你已经装了 Homebrew）**

```bash
brew install --cask docker
```

安装完成后，同样在 Applications 中找到 Docker 并启动。

### 步骤 2：启动并授权

1. 第一次启动 Docker Desktop 时，macOS 会弹出权限请求。
2. **必须授权**，否则 Docker 无法运行。在弹出的对话框中点"好"或"允许"。
3. 输入你的系统密码确认。
4. 等待顶部菜单栏出现鲸鱼图标，状态变为 "Docker Desktop is running"。

### 步骤 3：验证安装

打开终端（Terminal），执行：

```bash
docker version
```

和 Windows 一样，看到 `Client` 和 `Server` 的版本信息就是成功了。

---

## 四、Linux（Ubuntu/Debian）安装

在 Linux 服务器上，通常安装 **Docker Engine**（不装 GUI）。

### 步骤 1：卸载旧版本（如果有）

```bash
sudo apt-get remove docker docker-engine docker.io containerd runc
```

如果提示"未找到相关软件包"，没关系，继续下一步。

### 步骤 2：使用官方安装脚本（最简单）

Docker 官方提供了一个一键安装脚本：

```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
```

> 这个脚本会检测你的系统版本，自动添加 Docker 官方源并安装最新稳定版。安装完成后可以删除脚本：`rm get-docker.sh`。

### 步骤 3：启动 Docker 服务

```bash
sudo systemctl start docker
sudo systemctl enable docker   # 设置开机自启
```

### 步骤 4：验证安装

```bash
sudo docker version
sudo docker run hello-world
```

如果看到 Hello from Docker! 的欢迎信息，安装成功。

### 步骤 5：让非 root 用户也能用 Docker（强烈推荐）

默认情况下，只有 root 用户能操作 Docker。每次都要加 `sudo` 很烦，而且有些工具（如 VS Code 的 Docker 插件）需要非 root 权限。

```bash
# 把当前用户加入 docker 组
sudo usermod -aG docker $USER
```

**执行完这条命令后，必须重新登录**（注销当前会话或 `exit` 后重新 SSH），组权限才会生效。

验证：

```bash
# 重新登录后，不需要 sudo 也能执行
docker version
```

---

## 五、Linux（CentOS/RHEL）安装

### 步骤 1：卸载旧版本

```bash
sudo yum remove docker docker-client docker-client-latest docker-common \
                docker-latest docker-latest-logrotate docker-logrotate \
                docker-engine
```

### 步骤 2：使用官方脚本

和 Ubuntu 一样，CentOS 也能用官方脚本：

```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
```

### 步骤 3：启动与验证

```bash
sudo systemctl start docker
sudo systemctl enable docker
sudo docker run hello-world
```

### 步骤 4：非 root 用户权限

```bash
sudo usermod -aG docker $USER
# 重新登录后生效
```

---

## 六、Docker Desktop 界面速览

如果你装的是 Docker Desktop（Windows/macOS），打开后你会看到这些区域：

| 界面区域 | 功能 | 你会用到 |
|---------|------|---------|
| **Containers** | 列出所有容器，可以启动/停止/删除 | 每次跑容器都要看 |
| **Images** | 列出本地所有镜像，可以拉取/删除 | 管理镜像时用 |
| **Volumes** | 管理数据卷（后面章节会讲） | 持久化数据时用 |
| **Settings** | 配置 Docker 资源、镜像源、代理等 | 修改配置时用 |

> 现在不用深究每个功能，先记住：**Containers 看容器，Images 看镜像**。这两个就够了。

---

## 我做得对不对？

### 验证方法

执行以下两条命令，**全部成功**才算安装完成：

```bash
# 命令 1：查看版本信息
docker version

# 命令 2：运行 Hello World
docker run hello-world
```

**命令 1 的预期输出**：同时显示 `Client` 和 `Server` 的版本信息，没有报错。

**命令 2 的预期输出**：

```
Hello from Docker!
This message shows that your installation appears to be working correctly.

To generate this message, Docker took the following steps:
 1. The Docker client contacted the Docker daemon.
 2. The Docker daemon pulled the "hello-world" image from the Docker Hub.
 3. The Docker daemon created a new container from that image which runs the
    executable that produces the output you are currently reading.
 4. The Docker daemon streamed that output to the Docker client, which sent it
    to your terminal.
```

---

## 不对怎么办？

### 排错预案 1：Docker 服务未启动

**Windows**：
- 检查右下角系统托盘的 Docker 鲸鱼图标是否**绿色**。
- 如果是红色或黄色，右键 → Restart。
- 如果 Docker Desktop 打不开，尝试以管理员身份运行。

**macOS**：
- 检查顶部菜单栏的 Docker 图标状态。
- 点开菜单 → Restart。

**Linux**：
```bash
# 检查服务状态
sudo systemctl status docker

# 如果没运行，启动它
sudo systemctl start docker
```

### 排错预案 2：镜像拉取太慢（中国大陆用户必看）

`docker run hello-world` 半天没反应，或者报错 `Error response from daemon: Get https://registry-1.docker.io/v2/: net/http: request canceled`。

这是因为 Docker Hub 的服务器在国外，国内网络访问慢。解决方法是配置国内镜像加速器。

**Docker Desktop（推荐）**：

1. 打开 Docker Desktop → 右上角齿轮图标（Settings）。
2. 左侧选择 **Docker Engine**。
3. 在 JSON 配置中，找到或添加 `registry-mirrors` 字段：

```json
{
  "registry-mirrors": [
    "https://docker.1ms.run",
    "https://docker.xuanyuan.me"
  ]
}
```

4. 点击 **Apply & Restart**。
5. 重启后重试 `docker run hello-world`。

> 镜像源地址会随时间变化，以上地址为 2026 年可用的公共镜像源。如果拉取仍然慢，可以搜索"2026 年 Docker 国内镜像源"获取最新地址。

**Linux（Docker Engine）**：

编辑 `/etc/docker/daemon.json`（如果文件不存在则创建）：

```bash
sudo nano /etc/docker/daemon.json
```

写入以下内容：

```json
{
  "registry-mirrors": [
    "https://docker.1ms.run",
    "https://docker.xuanyuan.me"
  ]
}
```

然后重启 Docker：

```bash
sudo systemctl daemon-reload
sudo systemctl restart docker
```

### 排错预案 3：WSL 2 相关问题（Windows）

**问题 A**：`wsl --install` 提示"请启用虚拟机平台功能"。

```powershell
# 以管理员身份执行
dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart
dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
# 重启电脑
```

**问题 B**：Docker Desktop 启动后一直在 "Docker Desktop starting..."。

```powershell
# 在 PowerShell 中更新 WSL 2 内核
wsl --update
# 重启 Docker Desktop
```

**问题 C**：WSL 2 内存占用过高。

在 `%USERPROFILE%\.wslconfig` 文件中添加限制（如果文件不存在，新建一个）：

```ini
[wsl2]
memory=4GB
processors=2
```

保存后，在 PowerShell 中执行 `wsl --shutdown`，然后重启 Docker Desktop。

### 排错预案 4：Linux 上 `docker` 命令需要 `sudo`

```bash
# 执行后重新登录
sudo usermod -aG docker $USER
```

❌ 错误做法：每次都用 `sudo docker`。

✅ 正确做法：把用户加入 docker 组，一劳永逸。

> 为什么刚执行完 `usermod` 还是需要 `sudo`？因为组权限只在**登录时**加载。你必须注销并重新登录（或 `newgrp docker` 临时生效），权限才会更新。

### 排错预案 5：CentOS 上防火墙阻止 Docker

```bash
# 检查防火墙状态
sudo firewall-cmd --state

# 如果防火墙阻止了 Docker 的网络，重启 Docker 会自动添加规则
sudo systemctl restart docker
```

---

## 本章小结

| 本章学了什么 | 对应命令/概念 | 注意事项 |
|-------------|-------------|---------|
| 两种安装方式 | Docker Desktop（GUI）vs Docker Engine（纯命令行） | 个人电脑用 Desktop，服务器用 Engine |
| Windows 安装 | 启用 WSL 2 → 下载安装 Docker Desktop → `docker version` | 必须开启虚拟化，WSL 2 性能优于 Hyper-V |
| macOS 安装 | 下载 Docker Desktop → 授权 → `docker version` | Apple Silicon 选 Apple Chip 版本 |
| Ubuntu/Debian 安装 | 官方脚本 `get.docker.com` → `systemctl start docker` | 装完后记得 `usermod -aG docker $USER` |
| CentOS/RHEL 安装 | 同上，用 yum 管理 | 注意防火墙规则 |
| 验证安装 | `docker version` + `docker run hello-world` | 两条命令都成功才算安装完成 |
| 镜像加速 | 配置 `registry-mirrors` | 中国大陆用户强烈建议配置，否则拉取极慢 |
| 非 root 权限 | `sudo usermod -aG docker $USER` | **必须重新登录才能生效**，这是最常见的坑 |
| WSL 2 配置 | `.wslconfig` 限制内存/CPU | 内存占用过高时限制，防止卡死宿主机 |