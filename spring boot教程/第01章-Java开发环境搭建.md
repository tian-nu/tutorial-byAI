# 第1章 Java开发环境搭建

## 本章目标

学完本章后，你将能够：
- 清晰区分 **JDK、JRE、JVM** 三者的角色与关系
- 在 Windows、Mac、Linux 任一平台上**独立安装并配置 JDK 17**
- 深入理解 **JAVA_HOME、Path、CLASSPATH** 的作用与配置陷阱
- 安装 **IntelliJ IDEA** 并完成基本配置
- 安装并配置 **Maven**，使用国内镜像加速依赖下载
- 编写并运行你的第一个 Java 程序，**完整理解从源代码到运行的全流程**
- 使用 Maven 创建标准化项目并打出可执行 jar 包

如果你之前写过 Python、JavaScript、C++ 等语言，本章会频繁通过对比帮助你快速建立 Java 开发的思维模型。

---

## 1.1 JDK vs JRE vs JVM——不再混淆的三个概念

### 1.1.1 从一个实际问题出发

假设你从网上下载了一个 Java 写的游戏（比如 Minecraft），你双击 `minecraft.jar`，弹出一个错误框：**"找不到 Java 运行时"**。于是你上网搜索，下载了"Java"，安装后又双击，这次游戏成功启动了。

这其中到底发生了什么？为什么有的"Java"能让程序跑起来，有的却不能？

要回答这个问题，就需要搞清楚三个字母缩写：**JVM**、**JRE**、**JDK**。它们是逐层包含的关系。

### 1.1.2 JVM（Java Virtual Machine）——Java 虚拟机

**JVM 是运行 Java 字节码的虚拟计算机。** 类比一下：
- 你玩任天堂游戏需要一个**模拟器**。`.nes` 或 `.gba` 文件（游戏 ROM）是字节码，模拟器负责把它们翻译成 Windows/Linux 能理解的指令。
- Java 的字节码就是 `.class` 文件，**JVM 就是这个模拟器**。

JVM 的核心职责只有两件事：
1. **加载字节码**（`.class` 文件）
2. **解释执行**（或 JIT 编译后执行）

JVM 本身**不包含任何 Java 标准类库**。如果你只有 JVM，你连 `System.out.println()` 都用不了——因为 `System` 这个类根本不存在。

这就是 JVM 规范的意义：任何符合规范的 JVM 实现（HotSpot、OpenJ9、GraalVM）都能运行同一个 `.class` 文件。这就是"**一次编译，到处运行**"的基础。

### 1.1.3 JRE（Java Runtime Environment）——运行时环境

**JRE = JVM + 核心类库 + 运行时支持文件。**

回到游戏模拟器的类比：如果 JVM 是模拟器本体，那 JRE 就是"模拟器 + 游戏运行所需的系统库"。

JRE 提供了运行 Java 程序所需的一切：
- JVM 本身
- 核心类库（`java.lang.*`、`java.util.*`、`java.io.*` 等）
- 运行时配置文件

**JRE 只能运行程序，不能编译程序。** 它没有 `javac` 编译器。如果你只安装了 JRE，那么：
- `java -version` ✅ 可以运行
- `javac -version` ❌ 命令不存在

> 🚨 **坑点：以为装了 = 能开发**
>
> - **现象**：新手下载安装了"Java"，命令行输入 `java` 有输出，但 `javac` 报错"'javac' 不是内部或外部命令"。
> - **原因**：你安装的是 **JRE 而非 JDK**。许多电脑预装的是 JRE，只够运行现有 Java 程序，不具备开发能力。
> - **正确做法**：去 [Adoptium](https://adoptium.net/) 下载 **JDK**（开发工具包），安装后同时检查 `java -version` 和 `javac -version` 都正常输出。

### 1.1.4 JDK（Java Development Kit）——开发工具包

**JDK = JRE + 开发工具。** 三层包含关系如下：

```
┌─────────────────────────────────────────┐
│                 JDK                      │
│  ┌───────────────────────────────────┐   │
│  │              JRE                   │   │
│  │  ┌─────────────────────────────┐  │   │
│  │  │            JVM               │  │   │
│  │  │  - 类加载器                   │  │   │
│  │  │  - 字节码解释器/JIT编译器     │  │   │
│  │  │  - 垃圾回收器                 │  │   │
│  │  └─────────────────────────────┘  │   │
│  │  - Java核心类库 (rt.jar/模块)     │   │
│  │  - 运行时配置文件                  │   │
│  └───────────────────────────────────┘   │
│  - javac（编译器）                        │
│  - javadoc（文档生成器）                  │
│  - jar（打包工具）                        │
│  - jshell（交互式编程工具）               │
│  - jdb（调试器）                          │
│  - ... 其他开发工具                       │
└─────────────────────────────────────────┘
```

JDK 中的开发工具包括：
| 工具 | 作用 | 类比 |
|------|------|------|
| `javac` | 将 `.java` 源码编译为 `.class` 字节码 | C 语言的 `gcc` |
| `java` | 启动 JVM 运行程序 | Python 的 `python` 命令 |
| `jar` | 将多个 `.class` 打包为 `.jar` 档案 | Unix 的 `tar` |
| `javadoc` | 从源码注释生成 HTML 文档 | Python 的 pydoc |
| `jshell` | Java 的 REPL 交互式环境 | Python 的交互式解释器 |
| `jdb` | Java 调试器 | C 语言的 `gdb` |

### 1.1.5 三者的关系表

| 特性 | JVM | JRE | JDK |
|------|-----|-----|-----|
| 包含关系 | 最核心 | = JVM + 类库 | = JRE + 开发工具 |
| 能否运行 Java 程序 | ❌（无类库） | ✅ | ✅ |
| 能否编译 Java 程序 | ❌ | ❌ | ✅ |
| 安装后 java 命令可用 | 不单独安装 | ✅ | ✅ |
| 安装后 javac 命令可用 | 不单独安装 | ❌ | ✅ |
| 适用人群 | JVM 开发者 | 终端用户 | Java 开发者 |

---

## 1.2 JDK 17 安装指南（三平台）

本书统一使用 **JDK 17**（长期支持版本 LTS）。推荐使用 **Adoptium（Eclipse Temurin）** 发行的 OpenJDK，它是目前最主流的开源 JDK 发行版，完全免费且持续维护。

### 1.2.1 Windows 平台安装

**第1步：下载 JDK 17**

打开浏览器访问 [https://adoptium.net/](https://adoptium.net/)，选择 **Temurin 17 (LTS)**，操作系统选 Windows，架构选 x64，下载 `.msi` 安装包。

> 🚨 **坑点：安装路径含空格或中文**
>
> - **现象**：JDK 安装到 `C:\Program Files\Java\jdk-17` 后，某些旧版脚本或工具解析 `Program Files` 中的空格时出错。
> - **原因**：Windows 的 `Program Files` 路径中含空格，部分工具（特别是古董级的批处理脚本）分割路径时会从空格处断开。
> - **正确做法**：安装时选择自定义路径，建议使用 `C:\java\jdk-17`（无空格、无中文、无特殊字符）。一路 `Next` 完成安装。

**第2步：配置环境变量**

这是 Windows 安装中**最容易出问题的环节**。请按以下步骤操作：

1. 右键"此电脑" → "属性" → "高级系统设置" → "环境变量"
2. 在**系统变量**中点击"新建"：
   - 变量名：`JAVA_HOME`
   - 变量值：`C:\java\jdk-17`（你的实际安装路径）
3. 在系统变量中找到 `Path`，双击编辑，**新建**一条：`%JAVA_HOME%\bin`
4. 依次点击"确定"关闭所有对话框

> 🚨 **坑点：JAVA_HOME 末尾多了分号或反斜杠**
>
> - **现象**：配置 `JAVA_HOME=C:\java\jdk-17\` 或 `C:\java\jdk-17;` 后，`%JAVA_HOME%\bin` 拼接为 `C:\java\jdk-17\\bin` 或 `C:\java\jdk-17;\bin`，路径无效。
> - **原因**：`JAVA_HOME` 被用作路径前缀拼接，末尾多出的字符会破坏拼接结果。
> - **正确做法**：`JAVA_HOME` 的值末尾**不加任何符号**，干干净净写成 `C:\java\jdk-17`。

**第3步：验证安装**

打开**新的**命令提示符（注意：必须新开窗口，已打开的窗口不会加载新环境变量）：

```bash
java -version
javac -version
echo %JAVA_HOME%
```

预期输出类似：

```
openjdk version "17.0.9" 2023-10-17
OpenJDK Runtime Environment Temurin-17.0.9+9 (build 17.0.9+9)
OpenJDK 64-Bit Server VM Temurin-17.0.9+9 (build 17.0.9+9, mixed mode, sharing)
javac 17.0.9
C:\java\jdk-17
```

三条命令全部正常输出，说明安装成功。

### 1.2.2 Mac 平台安装

最推荐使用 Homebrew：

```bash
# 安装 JDK 17
brew install openjdk@17

# 创建符号链接（让系统识别这个 JDK）
sudo ln -sfn $(brew --prefix)/opt/openjdk@17/libexec/openjdk.jdk \
    /Library/Java/JavaVirtualMachines/openjdk-17.jdk
```

> 🚨 **坑点：brew 安装后 JAVA_HOME 路径不固定**
>
> - **现象**：`brew` 安装的 JDK 放在 Homebrew 的 cellar 目录中，不同版本路径不同（如 `/opt/homebrew/Cellar/openjdk@17/17.0.9/...`），硬编码 `JAVA_HOME` 会在升级后失效。
> - **正确做法**：使用 `/usr/libexec/java_home -v17` 动态获取路径。在 `~/.zshrc` 中添加：
>   ```bash
>   export JAVA_HOME=$(/usr/libexec/java_home -v17)
>   export PATH="$JAVA_HOME/bin:$PATH"
>   ```

验证安装：

```bash
java -version
javac -version
echo $JAVA_HOME
```

### 1.2.3 Linux 平台安装（Ubuntu / CentOS）

**Ubuntu（apt）：**

```bash
sudo apt update
sudo apt install openjdk-17-jdk
```

**CentOS / Rocky Linux（yum）：**

```bash
sudo yum install java-17-openjdk java-17-openjdk-devel
```

**通用方式（tar.gz 解压）：**

```bash
# 下载（以 Adoptium 为例）
wget https://github.com/adoptium/temurin17-binaries/releases/download/jdk-17.0.9%2B9/OpenJDK17U-jdk_x64_linux_hotspot_17.0.9_9.tar.gz

# 解压到 /usr/local/java
sudo mkdir -p /usr/local/java
sudo tar -xzf OpenJDK17U-jdk_x64_linux_hotspot_17.0.9_9.tar.gz -C /usr/local/java

# 配置环境变量（写入 ~/.bashrc 或 /etc/profile）
echo 'export JAVA_HOME=/usr/local/java/jdk-17.0.9+9' >> ~/.bashrc
echo 'export PATH=$JAVA_HOME/bin:$PATH' >> ~/.bashrc
source ~/.bashrc
```

验证安装：

```bash
java -version
javac -version
echo $JAVA_HOME
```

---

## 1.3 环境变量深度理解

### 1.3.1 JAVA_HOME——被工具依赖的"指南针"

也许你有一个疑问：既然 `Path` 里已经有 `%JAVA_HOME%\bin` 了，为什么还要单独设 `JAVA_HOME`？直接把 `C:\java\jdk-17\bin` 加到 `Path` 不行吗？

答案是：**`JAVA_HOME` 不是给操作系统看的，是给工具看的。**

大量 Java 生态工具会读取 `JAVA_HOME` 来定位 JDK，比如：

| 工具 | 如何使用 JAVA_HOME |
|------|-------------------|
| **Maven** | 启动脚本 `mvn` 中读取 `JAVA_HOME` 定位 JDK |
| **Gradle** | 同样依赖 `JAVA_HOME` |
| **Tomcat** | `catalina.sh/bat` 中使用 `JAVA_HOME` |
| **IntelliJ IDEA** | 检测系统 JDK 列表时读取 `JAVA_HOME` |
| **Ant** | 构建前校验 `JAVA_HOME` |

> 🚨 **坑点：只配 Path 不配 JAVA_HOME**
>
> - **现象**：命令行 `javac` 能用，但 `mvn` 命令报错 `JAVA_HOME is not defined correctly`。
> - **原因**：`Path` 只让操作系统找到可执行文件，但 Maven/Gradle/Tomcat 的启动脚本中直接引用 `%JAVA_HOME%` 变量，变量为空就报错。
> - **正确做法**：**同时配置** `JAVA_HOME` 和 `Path`（引用 `JAVA_HOME`）。两个变量缺一不可。

### 1.3.2 Path——操作系统的"找人清单"

当你在命令行输入 `java`，操作系统会在当前目录找不到 `java.exe` 时，依次去 `Path` 中列出的每个目录搜索。这是一个**顺序查找**的过程。

这就是为什么多个 JDK 版本共存时，**排在 Path 前面的那个版本生效**。比如：

```
Path = C:\java\jdk-8\bin;C:\java\jdk-17\bin;...
```

此时 `java -version` 输出的是 **JDK 8**，因为它在列表中排在更前面。

> 🚨 **坑点：多 JDK 版本共存导致版本混乱**
>
> - **现象**：明明装了 JDK 17，`java -version` 却显示 1.8。或者 Maven 项目配置了 Java 17，但编译报错说语法不支持。
> - **原因**：系统中存在多个 JDK（可能被 Oracle 安装程序静默装过），Path 中多个 `java.exe` 所在目录，第一个命中的不是你期望的版本。
> - **排查方法**：
>   1. `where java`（Windows）或 `which java`（Mac/Linux）查看实际使用的是哪个路径的 java
>   2. `echo %Path%` 检查 JDK bin 目录在列表中的顺序
>   3. IDEA 中 `File → Project Structure → SDK` 检查项目引用的 JDK 版本
> - **正确做法**：统一使用 `JAVA_HOME` 指向期望版本，Path 中只用 `%JAVA_HOME%\bin` 一处 JDK 路径。需要暂时切换版本时，只改 `JAVA_HOME` 变量的值即可。

### 1.3.3 CLASSPATH——可以遗忘但应该了解的概念

早年间（Java 1.x 时代），运行 Java 程序往往需要设置 `CLASSPATH` 环境变量，告诉 JVM 去哪里找 `.class` 文件。

**现代 Java 开发中你基本不需要手动设置 CLASSPATH**，原因是：
- `java` 和 `javac` 命令支持 `-cp`（`--class-path`）参数动态指定
- IDE 自动管理项目的 classpath
- Maven/Gradle 自动处理依赖路径
- 从 JDK 9 开始引入模块系统（JPMS），classpath 的概念在弱化

但理解 CLASSPATH 的原理仍有价值：JVM 按 `CLASSPATH`（或 `-cp` 指定的路径）**顺序搜索** `.class` 文件，找到第一个就停止。这解释了为什么同名类的不同版本会产生冲突。

### 1.3.4 验证三件套

每次安装或切换 JDK 后，请执行以下三条命令确认一切正常：

```
java -version      → 确认JVM和运行时版本
javac -version     → 确认编译器版本（应与java版本一致）
echo %JAVA_HOME%   → 确认变量指向正确路径
```

---

## 1.4 IntelliJ IDEA——你的主力开发工具

### 1.4.1 下载与安装

IntelliJ IDEA 是 JetBrains 公司开发的 Java IDE，是目前**全球使用率最高的 Java 开发工具**。

本书推荐使用 **Community（社区版）**，完全免费且功能足够覆盖本书全部内容。

下载地址：[https://www.jetbrains.com/idea/download/](https://www.jetbrains.com/idea/download/)

安装过程（Windows）：
1. 下载 `.exe` 安装包，双击运行
2. 安装选项建议勾选：
   - **Add "Open Folder as Project"**：右键文件夹直接以 IDEA 项目方式打开
   - **Add "bin" folder to the PATH**：在命令行可使用 `idea` 命令启动
   - **Create Associations: .java**：双击 `.java` 文件用 IDEA 打开
3. 一路 Next 完成安装

### 1.4.2 界面布局速览

首次打开 IDEA，你会看到以下核心区域：

- **Project 面板**（左侧）：项目文件树，对应磁盘目录结构
- **Editor 面板**（中央）：代码编辑区，支持语法高亮、自动补全、实时报错
- **Terminal 面板**（底部）：内嵌终端，直接执行命令，相当于 `cmd`/`bash`

**常用快捷键**（初学者先记这几个）：

| 快捷键（Windows） | 作用 |
|-------------------|------|
| `Ctrl+Shift+F10` | 运行当前类 |
| `Ctrl+Alt+L` | 格式化代码 |
| `Ctrl+D` | 复制当前行 |
| `Ctrl+/` | 单行注释/取消注释 |
| `Alt+Enter` | 万能修复建议（非常常用！） |

### 1.4.3 必装插件

IDEA 的强大很大程度来自插件生态。以下是本书会用到的重要插件：

| 插件 | 作用 | 是否必须 |
|------|------|----------|
| **Lombok** | 用注解消除样板代码（`@Data`、`@Getter` 等） | ✅ 必须 |
| **Maven Helper** | 可视化依赖树、快速排除冲突依赖 | ✅ 必须 |
| **Chinese Language Pack** | 汉化界面（英文无压力可跳过） | 推荐 |
| **MyBatisX** | MyBatis 增强：Mapper 跳转、代码生成 | 推荐 |

安装方式：`File → Settings → Plugins → Marketplace → 搜索插件名 → Install`。

### 1.4.4 关键设置

打开 `File → Settings`（Mac 是 `Preferences`），进行以下设置：

1. **编码**：`Editor → File Encodings` → 全部设置为 **UTF-8**，勾选 `Transparent native-to-ascii conversion`
2. **自动导入**：`Editor → General → Auto Import` → 勾选 `Add unambiguous imports on the fly`
3. **JDK 配置**：`File → Project Structure → SDK` → 点击 `+` → `Add JDK` → 选择 JDK 17 安装目录

> 🚨 **坑点：IDEA 项目 JDK 版本与系统 JAVA_HOME 不一致**
>
> - **现象**：命令行 `javac -version` 显示 17，但 IDEA 中代码报错 `java: 不再支持源选项 5`。
> - **原因**：IDEA 的项目 SDK 设置独立于系统环境变量。新建项目时如果未指定，可能回退到 IDEA 内置的低版本 JDK。
> - **排查**：`File → Project Structure → Project → SDK` 确认选中的是 JDK 17。`Language level` 也设为 17。
> - **正确做法**：每次创建新项目后，**第一件事**就是检查 Project SDK 设置。

---

## 1.5 Maven 包管理工具入门

### 1.5.1 为什么需要 Maven

如果你写过 Python，你一定用过 `pip install`；如果你写过 JavaScript，你一定用过 `npm install`；如果你写过 C++，你可能手动下载过 boost、openssl 的源码然后 `cmake`...

**Java 世界的包管理器就是 Maven。** 它做的事情包括：

| 功能 | Maven | Python | Node.js |
|------|-------|--------|---------|
| 依赖管理 | `pom.xml` | `requirements.txt` | `package.json` |
| 构建工具 | `mvn compile` | `setuptools` | `npm run build` |
| 中央仓库 | Maven Central | PyPI | npm registry |
| 项目模板 | Archetype | cookiecutter | create-react-app |

在没有 Maven 的年代，管理 Java 项目的依赖是一场噩梦：你需要手动下载每个第三方 `.jar` 文件，放到 `lib/` 目录，加到 classpath，处理版本冲突全部靠人工。Maven 解决了这一切。

### 1.5.2 Maven 安装

1. 下载：[https://maven.apache.org/download.cgi](https://maven.apache.org/download.cgi)，选择 `Binary zip archive`
2. 解压到 `C:\java\apache-maven-3.9.x`（Windows）或 `~/tools/maven`（Mac/Linux）
3. 配置环境变量：
   - 新建 `MAVEN_HOME` 指向 Maven 安装目录
   - `Path` 中添加 `%MAVEN_HOME%\bin`（Windows）或 `$MAVEN_HOME/bin`（Mac/Linux）
4. 验证：`mvn -version`

### 1.5.3 配置国内镜像——否则慢到怀疑人生

Maven 默认从 [Maven Central](https://repo.maven.apache.org/) 下载依赖。这个仓库的服务器在海外，国内直接访问可能只有 **几 KB/s** 甚至超时。

> 🚨 **坑点：忘记配置镜像源导致依赖下载奇慢或失败**
>
> - **现象**：执行 `mvn compile` 后卡在 `Downloading from central...` 几十分钟不动，最后超时报错。
> - **原因**：Maven Central 服务器在海外，GFW 或国际带宽瓶颈导致速度极慢。
> - **正确做法**：配置**阿里云镜像**。编辑 `{MAVEN_HOME}/conf/settings.xml`，在 `<mirrors>` 标签内添加如下配置。

打开 Maven 安装目录下的 `conf/settings.xml`，找到 `<mirrors>` 标签（通常在文件末尾附近），加入：

```xml
<mirror>
    <id>aliyunmaven</id>
    <mirrorOf>central</mirrorOf>
    <name>阿里云公共仓库</name>
    <url>https://maven.aliyun.com/repository/public</url>
</mirror>
```

保存后重新执行 Maven 命令，下载速度应该能达到几 MB/s。

### 1.5.4 Maven 坐标三要素

在 Maven 的世界里，每一个依赖都由一个唯一的"坐标"定位：

```
groupId : artifactId : version
```

| 要素 | 含义 | 示例 |
|------|------|------|
| **groupId** | 组织/公司标识（通常是域名倒置） | `org.springframework.boot` |
| **artifactId** | 项目/模块名称 | `spring-boot-starter-web` |
| **version** | 版本号 | `3.2.0` |

这三个要素的组合可以唯一确定一个 jar 包，这就像公民身份证号一样全球唯一。

### 1.5.5 pom.xml 最小结构详解

`pom.xml` 是 Maven 项目的核心配置文件。以下是一个最简结构：

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!-- 项目根元素，声明命名空间和 schema -->
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0
         http://maven.apache.org/xsd/maven-4.0.0.xsd">

    <!-- POM 模型版本号，Maven 2/3 固定用 4.0.0 -->
    <modelVersion>4.0.0</modelVersion>

    <!-- 本项目的坐标三要素 -->
    <groupId>com.example</groupId>     <!-- 组织标识 -->
    <artifactId>hello-world</artifactId> <!-- 项目名 -->
    <version>1.0-SNAPSHOT</version>    <!-- 版本号（SNAPSHOT=快照/开发中） -->

    <!-- 打包方式：jar（默认）、war（Web应用）、pom（父工程） -->
    <packaging>jar</packaging>

    <!-- 项目元信息（可选） -->
    <name>Hello World</name>
    <description>我的第一个 Maven 项目</description>

    <!-- 属性占位符，可通过 ${java.version} 引用 -->
    <properties>
        <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
        <maven.compiler.source>17</maven.compiler.source>   <!-- 源码 JDK 版本 -->
        <maven.compiler.target>17</maven.compiler.target>   <!-- 编译目标版本 -->
    </properties>

    <!-- 依赖列表，每条 dependency 引用一个第三方库 -->
    <dependencies>
        <!-- 示例：引入 JUnit 5 测试框架 -->
        <dependency>
            <groupId>org.junit.jupiter</groupId>
            <artifactId>junit-jupiter</artifactId>
            <version>5.10.1</version>
            <scope>test</scope> <!-- scope=test 只在测试代码中可用 -->
        </dependency>
    </dependencies>

</project>
```

逐行解释：
- `<modelVersion>`：Maven 使用的 POM 模型版本，从 Maven 2 开始固定为 `4.0.0`，新项目直接抄。
- `<groupId>`：一般写你的域名倒置（实际项目）；本书练习统一用 `com.example`。
- `<artifactId>`：项目名字，决定最终生成的 jar 文件名。
- `<version>`：`SNAPSHOT` 后缀表示"快照版"（开发中），去掉后缀表示"发布版"。
- `<packaging>`：默认 `jar`，不需要显式写也行。
- `<properties>`：定义可复用变量，`${变量名}` 引用。
- `<dependencies>`：所有第三方库都作为 `<dependency>` 放在这里。

> 🚨 **坑点：依赖传递冲突——A 依赖 C v1，B 依赖 C v2**
>
> - **现象**：运行时报 `NoSuchMethodError` 或 `ClassNotFoundException`，你去看自己的代码明明没问题。
> - **原因**：Maven 的依赖传递机制。你的项目依赖了 A 和 B，A 内部依赖了 C 库的 v1 版本，B 内部依赖了 C 库的 v2 版本。Maven 仲裁后可能选了 v1，但 B 需要 v2 中存在而 v1 不存在的类/方法。
> - **排查方法**：在项目根目录执行：
>   ```bash
>   mvn dependency:tree
>   ```
>   它会打印完整的依赖树，你可以清晰地看到哪个库引入了哪个版本。
> - **解决方法**：在你的 `pom.xml` 中**显式声明** C 库的依赖，指定你需要的版本。Maven 遵循"最短路径优先 → 最先声明优先"的仲裁规则，显式声明可以覆盖。

### 1.5.6 常用 Maven 命令

| 命令 | 作用 | 详细说明 |
|------|------|----------|
| `mvn clean` | 清理 target 目录 | 删除上次编译生成的所有文件 |
| `mvn compile` | 编译 Java 源码 | 只编译 `src/main/java` 下的代码 |
| `mvn test` | 运行测试 | 先 compile，再运行 `src/test/java` 下的测试代码 |
| `mvn package` | 打包 | compile → test → 打包成 jar/war |
| `mvn install` | 安装到本地仓库 | package → 将 jar 复制到 `~/.m2/repository/` |

这些命令可以组合：`mvn clean package`（先清理再打包）。

---

## 1.6 Hello World 深度剖析

现在我们来写每一个 Java 程序员的"第一行代码"，并逐字逐句理解它。

### 1.6.1 代码

```java
// 文件：HelloWorld.java
package com.example;

/**
 * 我的第一个 Java 程序
 */
public class HelloWorld {

    /**
     * JVM 程序入口方法
     * @param args 命令行参数
     */
    public static void main(String[] args) {
        System.out.println("Hello, World!");
    }
}
```

### 1.6.2 逐行深度解释

**第 1 行：`package com.example;`**

> 类比：Python 的包文件目录（`__init__.py`）、JavaScript 的 namespace。

`package` 声明了当前文件所属的**命名空间**（即包）。它有两层含义：
1. **逻辑上**：`com.example` 表示这个类归属于 `com.example` 包
2. **物理上**：这个 `.java` 文件**必须**放在 `com/example/` 目录下（相对于源码根目录）

如果不写 `package`，类就属于"默认包"（无名包）。实际开发中你**永远**应该声明包名。

**第 4-6 行：`public class HelloWorld {`**

这是**类声明**：

- `public`：**访问修饰符**，表示这个类对所有其他类可见。如果去掉 `public`，就只有同包下的类能看到它（第3章会详讲）。
- `class`：关键字，告诉编译器"我要定义一个类"。
- `HelloWorld`：类名，按 Java 规范**首字母必须大写**，采用驼峰命名法。

> 🚨 **坑点：文件名必须与 public 类名一致**
>
> - **现象**：`HelloWorld.java` 文件中定义了 `public class Hello`，`javac` 编译时报错 `class Hello is public, should be declared in a file named Hello.java`。
> - **原因**：Java 编译器的硬性约定：一个 `.java` 文件中最多有一个 public 类，且文件名必须与这个 public 类名完全一致（大小写敏感）。
> - **正确做法**：`public class HelloWorld` 必须在 `HelloWorld.java` 文件中。

**第 9 行：`public static void main(String[] args) {`**

这是全 Java 世界**最重要的一行代码**。它是 JVM 启动时寻找的程序入口。拆解来看：

| 修饰符 | 为什么 |
|--------|--------|
| `public` | JVM 位于类的外部，需要 public 才能访问这个方法 |
| `static` | JVM 调用 main 时，还没有创建任何 HelloWorld 对象，只能用静态方法直接通过类名调用 |
| `void` | main 方法的返回值给 JVM 没有意义。JVM 只看退出状态码 |
| `main` | 约定俗成的入口方法名（由 JVM 规范规定，不能改） |
| `String[] args` | 命令行参数数组。你执行 `java HelloWorld a b c` 时，`args = ["a", "b", "c"]` |

> 🚨 **坑点：main 方法签名写错**
>
> - **常见错误 1**：写成 `public static void main(String args)`，没有方括号——编译通过，但 JVM 说找不到 main 方法。
> - **常见错误 2**：大小写错误——`Main`、`MAIN`。JVM 严格区分大小写。
> - **常见错误 3**：漏掉 `static`。`javac` 编译通过，但 `java` 运行时报 `NoSuchMethodError: main`。
> - **标准写法（抄就完事了）**：`public static void main(String[] args)`。**一个字也别改。**

**第 10 行：`System.out.println("Hello, World!");`**

这是 Java 最常用的控制台输出语句。拆解开来：

- `System`：`java.lang` 包下的**类**（全称 `java.lang.System`，`java.lang` 包自动导入）
- `out`：`System` 类中的**静态 PrintStream 对象**，代表**标准输出流**
- `println()`：`PrintStream` 的实例方法，打印一行并换行。`print()` 不换行

这条语句经历了三层嵌套：**类 → 静态属性 → 实例方法**。如果你是 Python 用户，对标 `print("Hello")`；C/C++ 用户对标 `printf("Hello\n")`。

### 1.6.3 编译与运行全流程

Java 的开发流程分为**编译**和**运行**两步，这是与 Python/JavaScript 等解释型语言最大的不同。

```
┌──────────────┐    javac    ┌──────────────┐    java    ┌──────────────┐
│ HelloWorld.java │  ────────→ │ HelloWorld.class │  ────────→ │  JVM 解释执行   │
│  (源代码/文本)    │   编译器     │  (字节码/二进制)   │  启动JVM    │  输出结果      │
└──────────────┘             └──────────────┘            └──────────────┘
       ↑                          ↑                          ↑
   人类可读                     JVM可读                   任何OS都能跑
```

**第1步：编译**

打开命令行，进入 `HelloWorld.java` 所在目录：

```bash
javac HelloWorld.java
```

执行后目录下会多出一个 `HelloWorld.class` 文件。用记事本打开它，里面是乱码——这是字节码，不是给人看的。

**第2步：运行**

```bash
java HelloWorld
```

注意：**不需要写 `.class` 后缀**！`java` 命令的参数是**类名**，不是文件名。

输出：

```
Hello, World!
```

**第3步：在另一个操作系统上运行**

把这个 `HelloWorld.class` 文件复制到 Mac 或 Linux 上，安装 JDK 后执行同一个 `java HelloWorld` 命令，**输出完全相同**。你不需要重新编译，不需要改源代码，甚至不需要有 `HelloWorld.java` 原文件。**这就是"一次编译，到处运行"。**

### 1.6.4 跨平台原理（简化版）

不同的操作系统（Windows / Mac / Linux）底层提供的 API 完全不同。Java 的解决思路是：**不管底层 OS 是什么，我先编译出一套"中间代码"（字节码），然后为每种 OS 各写一个 JVM 来翻译它。**

```
┌──────────────────────────────────────────────────────────────────────┐
│                       Java 跨平台原理                                 │
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│   同一个 HelloWorld.class（字节码）                                    │
│         │              │                │                            │
│    ┌────▼────┐   ┌────▼────┐    ┌─────▼─────┐                       │
│    │ Windows │   │  macOS  │    │   Linux   │   ← 不同操作系统        │
│    │  JVM    │   │   JVM  │    │    JVM    │     各自拥有JVM实现      │
│    └────┬────┘   └────┬────┘    └─────┬─────┘                       │
│         │              │                │                            │
│    ┌────▼────┐   ┌────▼────┐    ┌─────▼─────┐                       │
│    │ Windows │   │  macOS  │    │   Linux   │   ← OS原生API          │
│    │   API   │   │   API   │    │    API    │                        │
│    └─────────┘   └─────────┘    └───────────┘                       │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
```

### 1.6.5 命令行参数演示

修改 `HelloWorld.java`，使用 `args` 参数：

```java
package com.example;

public class HelloWorld {
    public static void main(String[] args) {
        if (args.length == 0) {
            System.out.println("你好，世界！");
        } else {
            System.out.println("你好，" + args[0] + "！");
            System.out.println("一共接收到了 " + args.length + " 个参数：");
            for (int i = 0; i < args.length; i++) {
                System.out.println("  参数[" + i + "]：" + args[i]);
            }
        }
    }
}
```

编译并运行：

```bash
javac HelloWorld.java
java HelloWorld             # 输出：你好，世界！
java HelloWorld Java        # 输出：你好，Java！
java HelloWorld a b c       # 输出3个参数
```

---

## 1.7 创建第一个 Maven 项目

### 1.7.1 使用 IDEA 创建

1. `File → New → Project`
2. 左侧选择 **Maven Archetype**（Maven 项目模板）
3. JDK 选择 JDK 17
4. Archetype 选择 `org.apache.maven.archetypes:maven-archetype-quickstart`
5. 填写 GroupId：`com.example`，ArtifactId：`hello-maven`
6. 点击 Create，等待 Maven 下载模板依赖（首次较慢，之后缓存）

### 1.7.2 项目结构详解

创建完成后，项目的目录结构如下：

```
hello-maven/
├── pom.xml                        ← Maven 核心配置文件
└── src/
    ├── main/
    │   ├── java/                  ← Java 源码目录
    │   │   └── com/
    │   │       └── example/
    │   │           └── App.java   ← 默认生成的入口类
    │   └── resources/             ← 资源文件（配置文件、xml等）
    └── test/
        └── java/                  ← 测试代码目录
            └── com/
                └── example/
                    └── AppTest.java ← 默认生成的测试类
```

| 目录 | 用途 |
|------|------|
| `src/main/java` | **你写业务代码的地方** |
| `src/main/resources` | 放 Spring 配置文件、MyBatis XML、`application.yml` 等 |
| `src/test/java` | **你写测试代码的地方** |
| `pom.xml` | 项目元信息 + 依赖声明 |

### 1.7.3 打可执行 jar 包

修改 `pom.xml`，在 `<build>` 标签中加入 `maven-jar-plugin` 配置：

```xml
<build>
    <plugins>
        <plugin>
            <groupId>org.apache.maven.plugins</groupId>
            <artifactId>maven-jar-plugin</artifactId>
            <version>3.3.0</version>
            <configuration>
                <archive>
                    <manifest>
                        <!-- 指定 jar 包的入口类 -->
                        <mainClass>com.example.App</mainClass>
                    </manifest>
                </archive>
            </configuration>
        </plugin>
    </plugins>
</build>
```

然后在命令行执行：

```bash
cd hello-maven
mvn clean package
```

成功后，`target/` 目录下会生成 `hello-maven-1.0-SNAPSHOT.jar`：

```bash
java -jar target/hello-maven-1.0-SNAPSHOT.jar
# 输出：Hello World!
```

---

## 本章小结

- **JDK = JRE + 开发工具**，JRE = JVM + 核心类库。开发者必须装 JDK。
- **三平台安装 JDK 17**：Windows 注意路径无空格；Mac 推荐 brew + `java_home`；Linux 推荐 apt/yum。
- **环境变量**：`JAVA_HOME` 是工具链的指南针，`Path` 是操作系统的找人清单。两者都要配，末尾不加多余符号。
- **IntelliJ IDEA Community** 免费够用，必装插件：Lombok、Maven Helper。
- **Maven** 是 Java 世界的 `pip`/`npm`，核心配置在 `settings.xml`（镜像）和 `pom.xml`（依赖）。
- **Hello World** 的 `main` 方法签名 `public static void main(String[] args)` 一个字都不能错。编译 → 字节码 → JVM 解释执行。
- **"一次编译，到处运行"**：`.class` 字节码文件可以在任何装有 JVM 的系统上直接运行。

---

## 思考题

### 题 1

你电脑上同时装了 JDK 8 和 JDK 17。`JAVA_HOME` 指向 JDK 17，但 IDEA 中某个老项目设置了 Project SDK 为 JDK 8。请问这个项目的 `pom.xml` 中的 `<maven.compiler.source>17</maven.compiler.source>` 会不会导致编译失败？为什么？

<details>
<summary>点击查看答案</summary>

会。IDEA 的 Project SDK 决定了编译器实际操作时使用的 JDK 版本。如果 Project SDK 是 JDK 8，编译器只认识 Java 8 的语法（比如不认识 `var` 关键字）。而 `pom.xml` 中的 `<maven.compiler.source>17</maven.compiler.source>` 只是告诉 Maven "目标版本是 17"，**实际执行编译时用的还是 Project SDK 指定的 JDK**。如果 Project SDK 是 JDK 8 但它没有 Java 17 的语法支持，就会报错。所以三处要一致：`pom.xml` 中的 source/target、IDEA Project SDK、系统 JAVA_HOME。

</details>

### 题 2

不用 IDE，你在 `D:\workspace\` 下创建了 `com/example/` 目录，写了 `Hello.java`，里面声明了 `package com.example;`。请问纯命令行如何编译和运行这个文件？

<details>
<summary>点击查看答案</summary>

编译：

```bash
# 进入 D:\workspace
cd D:\workspace
# 编译时指定源文件路径（相对于当前目录）
javac com/example/Hello.java
```

运行：

```bash
# 必须使用全限定类名（包名.类名）
java com.example.Hello
```

关键点：
1. `javac` 的参数是**文件路径**（含目录），不是类名
2. `java` 的参数是**全限定类名**（包名 + 类名），不是文件路径
3. 当前工作目录必须在包的根目录（即 `com` 目录的父目录），否则 JVM 找不到类

</details>

### 题 3

执行 `mvn clean package` 时卡在 `Downloading from central...` 超过 5 分钟。可能是什么原因？如何解决？

<details>
<summary>点击查看答案</summary>

原因：Maven 默认从 Maven Central 中央仓库下载依赖，该仓库服务器在海外，国内直连速度极慢（可能只有几 KB/s），大文件甚至超时。

解决方案：
1. **首选方案**：修改 `{MAVEN_HOME}/conf/settings.xml`，在 `<mirrors>` 中添加阿里云镜像配置
2. **备选方案**：使用其他国内镜像（如华为云、腾讯云）
3. **临时方案**：配置 VPN/代理

验证方法：配完镜像后重新执行 `mvn clean package`，观察日志中的下载 URL 是否变成了 `maven.aliyun.com` 开头。

</details>

### 题 4

下面这段代码编译运行后会输出什么？

```java
public class Test {
    public static void main(String[] args) {
        System.out.println("args 长度：" + args.length);
        for (int i = 0; i < args.length; i++) {
            System.out.println("args[" + i + "]: " + args[i]);
        }
    }
}
```

执行命令：`java Test "Hello World" 42`

<details>
<summary>点击查看答案</summary>

```
args 长度：2
args[0]: Hello World
args[1]: 42
```

说明：
- 命令行参数用**空格分隔**，`"Hello World"` 被双引号包裹，视为**一个参数**（空格不会被拆分）
- `42` 作为第 2 个参数，类型是 String（不是 int）。所有命令行参数在 Java 中都是 `String[]`
- `args.length` 是数组的**属性**（不是方法），后面不加括号

</details>

### 题 5

你认为 JVM 类似于"模拟器"的类比是否完全准确？请说出至少一个不准确的点。

<details>
<summary>点击查看答案</summary>

不完全准确，至少有以下差异：

1. **JIT 编译**：JVM 不只是"模拟器"式的纯解释执行。HotSpot JVM 会监控热点代码，触发 **JIT（Just-In-Time）编译**，将字节码直接编译为**机器码**，后续执行直接跑机器码——这已经超出了"模拟器"的行为范畴。

2. **不是纯软件抽象**：JVM 规范定义了字节码格式和指令集，但实现可以千差万别。GraalVM 甚至可以将 Java 字节码 **AOT（Ahead-of-Time）编译**为原生可执行文件（不依赖 JVM）。

3. **内存管理**：JVM 包含完备的**自动垃圾回收**（GC）机制，模拟器通常不具备这个能力。

所以更准确的说：**JVM 是一个运行时环境，它结合了字节码解释、JIT 编译、垃圾回收等功能。**

</details>

---

> **下一章预告**：在下一章中，你将正式进入 Java 编程的大门，学习 Java 的基本数据类型、运算符、流程控制和数组——这些是你编写任何 Java 程序都离不开的语法基石。