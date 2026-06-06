# 第15章 · Java介绍与环境搭建

> "前面14章我们搞清楚了互联网是怎么连上的、数据是怎么传输的。但从这一章开始，我们终于要动真格的了——学一门真正的编程语言，用它来写后端代码。这门语言就是Java，全球最流行的后端语言。"

---

## 15.1 Java的诞生：一次失败的机顶盒项目

1991年，Sun公司（Sun Microsystems）有个叫"Green项目"的内部小组，领头人是James Gosling。他们的任务是给电视机顶盒、微波炉等家用电器写控制程序。

那个年代写代码用的是C语言。C语言的程序必须针对每一种芯片单独编译。机顶盒用的芯片和微波炉用的芯片不一样——你得为每种电器重新编译一遍，这很不方便。

Gosling想出一个办法：**能不能让程序编译成一种中间格式，然后在每种设备上装一个"翻译器"来执行它？**

这个思路就是Java的核心思想——**"一次编写，到处运行"（Write Once, Run Anywhere）**。他把这个中间格式叫做**字节码**（bytecode），翻译器叫做**JVM**（Java Virtual Machine，Java虚拟机。此术语需进附录）。

本来这是做给机顶盒的，但1993年之后，互联网爆发了。Sun公司发现：互联网上也是各种不同的电脑（Windows、Mac、Unix），大家同样面临"一种程序要跑在所有机器上"的问题。于是1995年，Java正式对外发布。

Java的第一个公开版本叫Java 1.0，发布于1996年。

### 三个关键人物

| 人物 | 角色 |
|------|------|
| James Gosling | Java之父，Green项目负责人 |
| Patrick Naughton | Green项目核心成员，后来搭建了Java最初的图形界面库 |
| Bill Joy | Sun联合创始人之一，Berkeley Unix作者，Java战略推手 |

### 为什么叫"Java"？

Java这个名字跟技术毫无关系。最初叫Oak（橡树），因为Gosling办公室窗外有一棵橡树。后来发现Oak已经被人注册了商标，团队开会想了个新名字。有人提议Java（爪哇咖啡），因为程序员最爱喝咖啡——于是Java的Logo就是一杯冒着热气的咖啡。

---

## 15.2 Java的版本历史：你在2024年应该用哪个？

Java版本号的混乱程度在编程语言里能排前三。这里帮你理清：

### 大版本十字路口

| 版本 | 年份 | 意义 |
|------|------|------|
| Java 1.0 | 1996 | 诞生 |
| Java 5（1.5） | 2004 | 里程碑：泛型、注解、枚举、增强for（从此Java现代化） |
| Java 8（1.8） | 2014 | **最伟大的版本**：Lambda表达式、Stream API、Optional。至今还有很多公司在用 |
| Java 9 | 2017 | 模块化系统（JPMS），但不算成功，很多项目直接从8跳到11 |
| Java 11 | 2018 | 第一个**LTS**版本（Long Term Support，长期支持）。很多公司的生产环境版本 |
| **Java 17** | 2021 | LTS版本。目前最推荐的稳定生产版本 |
| **Java 21** | 2023 | **最新LTS版本。本书使用的版本。** |

> 🤔 **想多一点**：为什么Java的版本号从1.0到1.4，然后突然跳到5，又跳到8？因为在Java 5之前，官方称呼是"Java 1.x"，但开发者社区心理上认为"1.2就是第二个大版本"。Sun公司干脆在Java 5时把前面的"1."去掉了。这就是为什么有人说"Java 8"有人说"1.8"——是一个东西。Java 8的实际内部版本号就是1.8.0_xxx。

### LTS是什么意思？

LTS（Long Term Support，长期支持）意味着Oracle公司承诺这个版本的Java会获得**多年的安全更新和Bug修复**。非LTS版本每6个月就出一个新的，但只有6个月的支持周期。

**本书约定：使用Java 21。** 你装入门时遇到的所有代码在Java 17或Java 21上都能跑。如果某特性是Java 14/16/21引入的，我会标注。

---

## 15.3 JDK vs JRE vs JVM：三个J，一个都不能错

这是初学者最容易搞混的概念。先看一张逐层递进的关系图：

```
┌─────────────────────────────────────┐
│                 JDK                 │  ← Java Development Kit
│  ┌───────────────────────────────┐  │
│  │             JRE               │  │  ← Java Runtime Environment
│  │  ┌─────────────────────────┐  │  │
│  │  │          JVM            │  │  │  ← Java Virtual Machine
│  │  │  ┌───────────────────┐  │  │  │
│  │  │  │   字节码执行引擎    │  │  │  │
│  │  │  │   垃圾回收器(GC)   │  │  │  │
│  │  │  │   即时编译器(JIT)  │  │  │  │
│  │  │  └───────────────────┘  │  │  │
│  │  └─────────────────────────┘  │  │
│  │     Java标准类库（String,     │  │
│  │     ArrayList, HashMap...）   │  │
│  └───────────────────────────────┘  │
│     编译工具(javac)、调试工具(jdb)、│
│     文档工具(javadoc)...            │
└─────────────────────────────────────┘
```

### 比喻：DVD播放器

- **JDK** = 一整套DVD制作工具（摄像机 + DVD播放器 + 剪辑软件 + 刻录机）。你既是"制作DVD"的人（开发者），也是"播放DVD"的人。
- **JRE** = 一台DVD播放器。你只能"播放"（运行）已经做好的Java程序，不能制作新程序。
- **JVM** = DVD播放器里的核心解码芯片。它读光盘内容，翻译成画面和声音。不同品牌的播放器（Windows/Mac/Linux）有不同的解码芯片实现，但都能播放同一张光盘。

| 缩写 | 全称 | 作用 | 谁需要 |
|------|------|------|--------|
| JVM | Java Virtual Machine | 执行字节码的虚拟计算机。此术语需进附录 | 运行Java程序的每个人 |
| JRE | Java Runtime Environment | JVM + Java标准类库 | 只运行Java程序的普通用户 |
| JDK | Java Development Kit | JRE + javac等开发工具 | 写Java代码的开发者（你） |

一句话总结：**你是开发者，你装JDK。你写好的程序给用户，用户只需要装JRE（或者你把JRE打包进去）。**

---

## 15.4 安装JDK 21

### Windows用户

1. 打开浏览器，访问 `https://adoptium.net/`（推荐Eclipse Adoptium版，开源免费，Oracle官方版的替代品）
2. 在首页找到"JDK 21"，选择Windows平台，点击下载 `.msi` 安装包
3. 双击下载的 `.msi` 文件，安装过程中**务必记住安装路径**（默认是 `C:\Program Files\Eclipse Adoptium\jdk-21.0.0.0-hotspot\`）
4. 一路点"Next"完成安装
5. 打开**PowerShell**，输入：

```powershell
java -version
```

如果看到类似输出：

```
openjdk version "21.0.x" 2024-xx-xx LTS
OpenJDK Runtime Environment Temurin-21.0.x+xx
OpenJDK 64-Bit Server VM Temurin-21.0.x+xx
```

恭喜！JDK安装成功。

6. 再验证编译工具：

```powershell
javac -version
```

应该看到：

```
javac 21.0.x
```

如果没有看到版本号，而是提示"javac不是内部或外部命令"，说明环境变量没配好，按下面的"环境变量配置"处理。

#### 环境变量配置（Windows）

如果 `java -version` 正常但 `javac` 不行，或者两个都不行：

1. 按 `Win + X`，选择"系统" → "高级系统设置" → "环境变量"
2. 在"系统变量"里找到 `Path`，双击编辑
3. 新增一条：你的JDK安装路径下的 `bin` 目录，例如 `C:\Program Files\Eclipse Adoptium\jdk-21.0.0.0-hotspot\bin`
4. 确定保存，**关闭PowerShell重新打开**，再试

### Mac用户

```bash
# 方式一：用Homebrew（推荐）
brew install openjdk@21

# 建立链接（让系统能找到这个JDK）
sudo ln -sfn $(brew --prefix)/opt/openjdk@21/libexec/openjdk.jdk /Library/Java/JavaVirtualMachines/openjdk-21.jdk

# 验证
java -version
javac -version
```

### Linux用户（Ubuntu/Debian）

```bash
sudo apt update
sudo apt install openjdk-21-jdk

# 验证
java -version
javac -version
```

---

## 15.5 安装IntelliJ IDEA社区版

虽然你可以用任何文本编辑器写Java代码然后用命令行编译，但现代开发99%的时间都在使用**IDE**（Integrated Development Environment，集成开发环境。此术语需进附录）。IDE就像一个"超级代码编辑器"，不仅能写代码，还能：
- 自动补全（你打 `System.`，它自动列出所有方法）
- 实时检查错误（红色波浪线提示）
- 一键编译运行
- 代码导航（点一下就能跳转到定义）
- 重构（给变量改名、提取方法等）

Java生态里最主流的IDE有三个：

| IDE | 特点 | 适合 |
|-----|------|------|
| **IntelliJ IDEA** | 最强大、最智能，业界标配 | 所有Java开发者 |
| Eclipse | 老牌免费IDE，插件丰富 | 传统企业项目 |
| VS Code + 插件 | 轻量级，但不如IntelliJ成熟 | 偶尔写Java的人 |

**本书推荐IntelliJ IDEA社区版**（免费）。

### 安装步骤

1. 访问 `https://www.jetbrains.com/idea/download/`
2. 向下滚动，找到**"Community Edition"（社区版）**——免费开源
3. 下载对应平台的安装包
4. 安装时一路默认选项即可
5. 首次启动时，可以选择跳过导入旧设置（Dark主题推荐Darcula）

> ❌ **常见错误**：不小心下了Ultimate（旗舰版）。旗舰版要付费（30天试用），虽然功能更多但社区版已经足够学完整本书。**请确认下载的是Community Edition。**

---

## 15.6 Hello World：你的第一行Java代码

现在创建一个Java项目并运行你的第一个程序。

### 方式一：命令行（理解本质）

1. 新建一个文件夹，比如 `D:\java-learning\`（Windows）或 `~/java-learning/`（Mac/Linux）
2. 在文件夹里新建一个文本文件，命名为 `HelloWorld.java`
3. 用记事本（或任何编辑器）打开，写入以下内容：

```java
public class HelloWorld {
    public static void main(String[] args) {
        System.out.println("Hello, World!");
    }
}
```

4. 打开终端，进入这个文件夹，执行：

```powershell
javac HelloWorld.java
```

如果没有任何输出——这是**好消息**。`javac` 是Java编译器，它把 `.java` 文件编译成 `.class` 文件（字节码文件）。现在看文件夹，多了一个 `HelloWorld.class` 文件。

5. 运行：

```powershell
java HelloWorld
```

**注意**：运行时不加 `.class` 后缀！你会看到：

```
Hello, World!
```

### 方式二：IntelliJ IDEA（日常开发方式）

1. 打开IntelliJ IDEA，点击 **New Project**
2. Name（项目名）：`java-learning`
3. Location（位置）：自己选一个目录
4. Language（语言）：Java
5. Build system（构建工具）：先选 **IntelliJ**（后面学了Maven再换）
6. JDK：选择你刚装的JDK 21（如果没出现，点"Add JDK"手动选路径）
7. 点击 **Create**
8. 在左侧项目面板里，右键 `src` 文件夹 → New → Java Class，命名为 `HelloWorld`
9. 输入上面的5行代码
10. 点击 `main` 方法左边的绿色播放按钮▶️，选择 "Run 'HelloWorld.main()'"
11. 底部控制台输出 `Hello, World!`

### 逐行解读：这5行代码每一行在做什么？

```java
public class HelloWorld {
```

`public` 是访问修饰符，表示"这个类是公开的，谁都能用"。`class` 是关键字，表示"我要定义一个类（此术语需进附录）"。`HelloWorld` 是类名——**必须和文件名 `HelloWorld.java` 完全一致**，包括大小写。`{` 表示类的内容从这里开始。

```java
    public static void main(String[] args) {
```

这一行信息量很大，拆开看：

| 关键字 | 含义 |
|--------|------|
| `public` | 这个方法是公开的，JVM启动时要从外部调用它 |
| `static` | 静态方法——不需要创建对象就能调用。JVM启动时还没有任何对象存在，所以main必须是static |
| `void` | 这个方法不返回任何值 |
| `main` | 特殊的方法名——JVM启动时自动寻找并执行的方法。必须是"main" |
| `String[] args` | 接收命令行参数。`String[]` 是字符串数组，`args` 是参数名（可以叫别的但习惯叫args） |

```java
        System.out.println("Hello, World!");
```

`System` 是Java标准库里的一个类，提供了很多系统级功能。`out` 是System类里的一个静态变量，代表"标准输出流"（默认就是控制台）。`println` 是out对象的方法，意思是"print line"——打印一行内容并换行。`"Hello, World!"` 是要打印的字符串。

```java
    }
}
```

两个右花括号分别关闭 `main` 方法和 `HelloWorld` 类。

---

## 15.7 编译与运行原理：从.java到屏幕输出

你可能好奇：为什么要先 `javac` 再 `java`？在Python里直接 `python hello.py` 不就行了吗？

这是因为**Java是编译型语言**。过程如下：

```
HelloWorld.java           →   javac编译   →   HelloWorld.class
（你写的源代码）                                 （字节码文件）

HelloWorld.class          →   java命令    →   加载到JVM
（字节码文件）              启动JVM              ↓
                                         JVM把字节码翻译成
                                         机器指令并执行
                                              ↓
                                         屏幕输出: Hello, World!
```

### 关键概念：字节码（Bytecode）

字节码（此术语需进附录）不是机器码。机器码是CPU直接能执行的0和1，不同CPU的机器码不同（Intel和ARM的机器码就完全不同）。字节码是给JVM看的"中间语言"——任何平台的JVM都能读懂同一份 `.class` 文件，JVM再把它翻译成当前平台的机器码。

这也是为什么你在Windows上编译的 `HelloWorld.class` 可以直接复制到Mac或Linux上运行——只要那台机器装了对应平台的JVM就行。这就是"一次编写，到处运行"的本质。

### javac做了什么？

`javac`（Java Compiler）做了三件事：
1. **语法检查**：检查你的代码有没有语法错误（少了分号、括号不匹配等）
2. **类型检查**：检查变量类型是否正确（你不会把一个数字赋值给一个字符串变量）
3. **生成字节码**：把检查通过的代码编译成 `.class` 文件

如果 `javac` 报错，你的 `.class` 文件不会生成——你必须先修好所有错误。

> 🤔 **想多一点**：Java不是纯粹的编译型语言，也不是纯粹的解释型语言。`.java` → `.class` 是编译，`.class` → 机器码时，JVM使用**JIT（Just-In-Time，即时编译）**技术——它不会从头到尾解释执行字节码，而是把热点代码（频繁执行的代码）动态编译成机器码，下次执行直接跑机器码，速度很快。JIT是Java性能接近C++的关键技术。

---

## 15.8 你的第一个Bug：刻意写错，学会看报错

学会看报错信息比学会写正确代码更重要——因为你会花大量时间在修Bug上。

### 错误一：类名和文件名不一致

把代码里的 `HelloWorld` 改成 `helloworld`（首字母小写），保存，编译：

```powershell
javac HelloWorld.java
```

报错：

```
HelloWorld.java:1: error: class helloworld is public, should be declared in a file named helloworld.java
public class helloworld {
       ^
1 error
```

JVM告诉你：**类名和文件名必须一致**。Java要求public类的名字必须等于文件名（不含.java后缀），且**大小写敏感**。

### 错误二：main方法签名写错

把 `String[]` 改成 `String`（少了方括号），编译：

```powershell
javac HelloWorld.java
```

这次编译能成功（因为语法上没错误），但运行时报错：

```powershell
java HelloWorld
```

报错：

```
Error: Main method not found in class HelloWorld, please define the main method as:
   public static void main(String[] args)
```

JVM告诉你：我找不到可以启动的main方法。它甚至贴心地给出了正确的写法。**签名（signature）**必须丝毫不差：`public static void main(String[] args)`。

> ❌ **常见错误**：初学者经常把 `main` 写成 `Main`（Java区分大小写）、把 `String[] args` 写错位置、把 `println` 写成 `printline`。记住：**报错就是你最好的老师**——仔细读报错信息的第一行，90%的问题都能自己解决。

---

## 本章小结

| 知识点 | 核心要点 |
|--------|----------|
| Java诞生 | 1995年，James Gosling，Sun公司。最初为机顶盒设计 |
| 核心口号 | "Write Once, Run Anywhere"——代码编译成字节码，在不同平台的JVM上运行 |
| JDK vs JRE vs JVM | JDK = 开发工具包（含JRE+编译器）。JRE = 运行环境（含JVM+类库）。JVM = 虚拟机（执行字节码） |
| 版本选择 | 本书使用Java 21（最新LTS）。Java 8和17也是常见生产版本 |
| IDE | IntelliJ IDEA社区版（免费），业内标配 |
| javac | Java编译器，`.java` → `.class` |
| java | 启动JVM，执行 `.class` 文件 |
| 字节码 | `.class`文件内容，JVM能读懂的中间格式。此术语需进附录 |

---

## 自测题

**1.** 以下哪个说法正确？
- A. JRE包含JDK
- B. JDK包含JRE
- C. JVM包含JDK
- D. JRE和JDK没有任何关系

**2.** 编译HelloWorld.java后生成的文件叫什么名字？运行它时，命令行应该怎么写？

**3.** 如果运行时提示 `Error: Main method not found`，最可能的原因是什么？

---

> 🚀 **下一章**：第16章 · Java程序的基本结构——package、import、class、main方法到底怎么组织？一个真正的Java项目是怎么分目录的？

---

[← 上一章：14-WebSocket](14-WebSocket/) | [下一章：16-Java程序的基本结构 →](16-Java程序的基本结构/)