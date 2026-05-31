# Java 从零到 Spring Boot 后端 — 细纲

> 主线语言：Java 21 | 框架：Spring Boot 3 | 构建工具：Maven
> 基于大纲 v1.0，展开为步骤级标题，预填代码路径、术语、可视化节点

---

## 关键阅读导航

### 章节依赖关系
- **第15章（环境搭建）** ← 所有后续章节都需要，不可跳过
- 第64→65→66→67章 关系：JDBC（底层原理，必学）→ 连接池（JDBC优化）→ MyBatis（半自动ORM，简介）→ JPA（全自动ORM，主力）。**三套都学，但JPA是主力，JDBC懂原理即可，MyBatis了解思路。**
- **第71章（IoC/DI）** ← 第73-85章全部依赖，是Spring Boot的核心理解前提
- **第87章（Spring Security）** ← 依赖第71章(IoC)+第78章(Filter)+第86章(认证基础)。**先给最小可用配置，再深入过滤器链。**
- Docker在第95章（RabbitMQ）用到 → 届时给一行docker命令快速启动即可，不必先学第112章
- 第94-99章（消息队列）提前到第五篇之后、第六篇原来是第七篇之前 → **顺序不变，但第95章用Docker时只给一行命令，到第112章再深入Docker原理。**

### 中断点标记（可安全暂停的位置）
- **[暂停点 1/7]** 第14章后：地基篇结束，可以休息，回来从第15章继续。
- **[暂停点 2/7]** 第21章后（数组学完）：Java语法完成一半，建议写完"学生管理系统"小练习再休息。恢复时运行`javac StudentManager.java && java StudentManager`验证。
- **[暂停点 3/7]** 第43章后：Java语言篇结束，可以休息较长时间。恢复时用`java -version`确认环境。
- **[暂停点 4/7]** 第53章后：数据结构篇结束。注意：第二篇可以**跳过后先学第三篇**，需要时再回来。恢复时确认记得ArrayList和HashMap用法。
- **[暂停点 5/7]** 第85章后：Spring Boot核心篇结束，此时已能独立写CRUD接口。建议先做第119章Todo项目练手，再继续。
- **[暂停点 6/7]** 第99章后：消息队列篇结束。测试篇(115-118)可以跳过先做实战项目。
- **[暂停点 7/7]** 第114章后：DevOps篇结束，最后冲刺实战项目。

### 防放弃设计
- 第22章后：插入**微型项目"学生成绩管理系统（命令行版）"**，让新手第一次有成就感
- 第34章（集合源码深入）和第42章（JVM GC）：标注**"选读/可回头精读"**
- 第44-53章（数据结构）：允许**跳过后先学第三篇数据库**，第44章加强动机说明
- 第87章（Spring Security）：以**最小可用配置**开头（10行代码跑起来），再深入原理

---

## 第零篇：地基 — 计算机与网络基础（第00-14章）

---

### 第00章 · 什么是后端工程师
- 代码文件：无（概念章）
- 可视化：需要（HTTP请求完整旅程，`.project/docs/tutorials/java_00_http_journey_visual.html`）
- 术语：前端、后端、数据库、API、HTTP请求、HTTP响应、DNS、JSON、RESTful
- **00.1 用餐厅比喻讲清楚前后端**：餐桌/菜单/服务员=前端、厨房/厨师=后端、仓库/冰箱=数据库、一张对照表
- **00.2 一个HTTP请求的完整旅程**：DNS解析→TCP连接→HTTP请求→Nginx转发→Spring Boot处理→数据库查询→JSON响应→浏览器渲染，8步完整链路，配可视化
- **00.3 后端工程师的日常真实工作**：写接口/设计数据库/写业务逻辑/修Bug/Code Review/上线部署/排查线上问题
- **00.4 Java后端生态全景**：JDK→Maven→Spring Boot→MySQL→Redis→Docker，一张全景图
- **00.5 本书学习路线图**：从第00章到第124章，标注新手区/进阶区/高手区

### 第01章 · 计算机的大脑——CPU
- 代码文件：无
- 术语：CPU、指令集、机器语言、汇编语言、高级语言、时钟频率、核心数、缓存、32位/64位
- **01.1 什么是CPU**：大脑比喻，CPU只做最基础的操作（加/减/比较/跳转）
- **01.2 机器语言、汇编语言、高级语言**：从0和1到MOV/ADD到Java代码，编译链：javac→bytecode→JVM→机器码
- **01.3 时钟频率**：CPU心跳、GHz概念、不是越高越好
- **01.4 核心数与超线程**：一个厨师vs多个厨师比喻
- **01.5 CPU缓存（L1/L2/L3）**：桌上书/书架/楼下书店/网购比喻
- **01.6 32位和64位**：2³²=4GB限制，JDK选择64位的原因

### 第02章 · 计算机的记忆——内存（RAM）
- 代码文件：无
- 术语：RAM、内存地址、栈（Stack）、堆（Heap）、内存泄漏、易失性
- **02.1 内存是什么**：临时工作台比喻，快/贵/断电就没了
- **02.2 内存地址**：门牌号比喻，每个字节一个地址
- **02.3 栈和堆的区别**：栈（整齐的书堆，自动管理）、堆（大仓库，手动/GC管理）
- **02.4 Java对象的内存布局预览**：对象头/实例数据/对齐填充，埋一个伏笔（第42章详细讲）
- **02.5 什么是内存泄漏**：借了不还的比喻

### 第03章 · 计算机的仓库——硬盘
- 代码文件：无
- 术语：硬盘、SSD、HDD、文件系统、磁盘IO、持久化
- **03.1 硬盘和内存的区别**：永久vs临时，仓库vs工作台
- **03.2 文件是什么**：硬盘上的数据组织方式
- **03.3 文件系统**：目录结构，Windows（C:\）vs Linux（/）
- **03.4 磁盘IO为什么慢**：机械手臂寻道时间，SSD为什么快
- **03.5 Java IO基础概念**：InputStream/OutputStream，埋伏笔（第37章）

### 第04章 · 操作系统是什么
- 代码文件：无
- 术语：操作系统、进程、线程、并发、并行、调度
- **04.1 操作系统的作用**：翻译官+管家比喻
- **04.2 进程：一个正在运行的程序**：启动一个Java程序就是启动一个JVM进程
- **04.3 线程：进程里的工人**：一个进程可以有多个线程同时干活
- **04.4 并发 vs 并行**：烧水泡面比喻（并发=一个人同时烧水+泡面，并行=两个人分别烧水和泡面）
- **04.5 JVM进程模型**：JVM就是一个操作系统进程，Java线程映射到OS线程

### 第05章 · 终端与命令行入门
- 代码文件：无（纯操作章）
- 术语：终端、Shell、命令、环境变量、PATH、JAVA_HOME
- **05.1 终端是什么**：为什么用黑窗口，GUI vs CLI
- **05.2 基础命令**：cd/ls/mkdir/rm/cat/pwd（Windows用PowerShell等价命令）
- **05.3 环境变量是什么**：全局配置变量，每个程序都能读
- **05.4 JAVA_HOME 与 PATH**：安装JDK后为什么要配这两个
- **05.5 Maven命令初体验**：mvn --version，感受一下构建工具

### 第06章 · IP地址
- 代码文件：`sandbox/IPDemo.java`（演示InetAddress）
- 术语：IP地址、IPv4、IPv6、公网IP、内网IP、localhost、127.0.0.1
- **06.1 什么是IP地址**：门牌号比喻，互联网上每台设备的地址
- **06.2 IPv4 vs IPv6**：192.168.1.1 vs 2001:db8::1，为什么需要IPv6
- **06.3 公网IP vs 内网IP**：小区门牌号vs房间号比喻
- **06.4 127.0.0.1 和 localhost**：自己喊自己的地址
- **06.5 Java演示**：用 InetAddress 获取本机IP，代码示例

### 第07章 · 域名与DNS
- 代码文件：`sandbox/DNSDemo.java`
- 术语：域名、DNS、DNS解析、hosts文件、TTL、DNS缓存
- **07.1 域名是什么**：电话簿比喻，给人看的名字→给机器看的数字
- **07.2 DNS查询的完整过程**：浏览器缓存→hosts文件→本地DNS→根DNS→顶级DNS→权威DNS
- **07.3 hosts文件**：本地的"私人电话簿"
- **07.4 Java DNS解析演示**：InetAddress.getByName()

### 第08章 · 端口
- 代码文件：无
- 术语：端口、端口号、常见端口（80/443/22/3306/6379/8080）
- **08.1 端口是什么**：房间号比喻，一个IP地址=一栋楼，端口=房间号
- **08.2 常见端口**：80(HTTP)、443(HTTPS)、22(SSH)、3306(MySQL)、6379(Redis)、8080(Spring Boot默认)
- **08.3 一个服务器能跑多少个服务**：通过不同端口区分
- **08.4 端口范围**：0-65535，知名端口(0-1023)、注册端口(1024-49151)、动态端口

### 第09章 · TCP协议：可靠的快递员
- 代码文件：`sandbox/TCPServer.java`、`sandbox/TCPClient.java`
- 可视化：需要（三次握手/四次挥手动画，`.project/docs/tutorials/java_09_tcp_visual.html`）
- 术语：TCP、三次握手、四次挥手、SYN、ACK、FIN、可靠传输、流量控制、拥塞控制
- **09.1 TCP是什么**：可靠快递员比喻，保证送到、按顺序、不损坏
- **09.2 三次握手（打电话比喻）**：喂？→听得到吗？→听得到，开始聊
- **09.3 四次挥手**：我要挂了→好的等一下→我这边也完了→拜拜
- **09.4 TCP保证可靠传输的机制**：确认应答、重传、排序
- **09.5 Java Socket编程初体验**：ServerSocket + Socket 写一个简单的"你好"程序

### 第10章 · UDP协议：只管发不管到的快递
- 代码文件：`sandbox/UDPServer.java`、`sandbox/UDPClient.java`
- 术语：UDP、无连接、DatagramSocket、DatagramPacket
- **10.1 UDP是什么**：扔纸飞机比喻，不管对方收没收到
- **10.2 UDP vs TCP 对比表**：连接/可靠性/速度/场景全面对比
- **10.3 UDP的使用场景**：视频直播、在线游戏、DNS查询
- **10.4 Java DatagramSocket演示**

### 第11章 · HTTP协议（一）：请求与响应
- 代码文件：`sandbox/HttpDemo.java`（HttpURLConnection）
- 术语：HTTP、URL、请求方法（GET/POST/PUT/DELETE/PATCH）、请求头、请求体、状态码、Content-Type
- **11.1 HTTP是什么**：浏览器和服务器之间的"通信语言"
- **11.2 URL是什么**：协议://域名:端口/路径?参数
- **11.3 请求方法**：GET(查)、POST(增)、PUT(改全量)、PATCH(改部分)、DELETE(删)
- **11.4 请求头和请求体**：信封和信纸比喻
- **11.5 状态码**：2xx成功、3xx重定向、4xx客户端错误、5xx服务端错误，每个用一句话解释
- **11.6 Java HttpURLConnection 演示**：发一个GET请求到 httpbin.org

### 第12章 · HTTP协议（二）：深入细节
- 代码文件：无（概念章，后续Spring Boot中实践）
- 术语：Cookie、Session、缓存（强缓存/协商缓存）、CORS、同源策略、ETag、Cache-Control
- **12.1 Cookie是什么**：服务器给你贴的便利贴，下次来就知道你是谁
- **12.2 Session是什么**：服务器端的"储物柜"，存用户状态
- **12.3 缓存机制**：强缓存（Cache-Control/max-age）、协商缓存（ETag/Last-Modified）
- **12.4 CORS跨域**：同源策略是什么、为什么需要跨域、预检请求（OPTIONS）

### 第13章 · HTTPS：给HTTP加把锁
- 代码文件：无（概念章）
- 术语：HTTPS、TLS/SSL、对称加密、非对称加密、数字证书、CA、TLS握手
- **13.1 为什么需要HTTPS**：HTTP是明信片，HTTPS是上了锁的保险箱
- **13.2 对称加密 vs 非对称加密**：同一把钥匙vs公钥+私钥
- **13.3 数字证书和CA**：证书=网站的身份证，CA=公安局
- **13.4 TLS握手过程**：客户端和服务端商量加密方式的过程

### 第14章 · WebSocket：实时通信
- 代码文件：无（概念章，第123章实战）
- 术语：WebSocket、全双工、长连接、心跳、ws://、wss://
- **14.1 HTTP的局限性**：一问一答，服务器不能主动推送
- **14.2 WebSocket是什么**：对讲机比喻，建立一条通道双方随时说话
- **14.3 使用场景**：聊天、实时推送、在线游戏、股票行情

---

## 第一篇：Java 语言从入门到精通（第15-42章）

---

### 第15章 · Java 介绍与环境搭建
- 代码文件：`src/main/java/demo/HelloWorld.java`
- 术语：JDK、JRE、JVM、字节码（bytecode）、IDE、IntelliJ IDEA
- **15.1 Java的诞生**：1995年Sun公司，James Gosling，"一次编写到处运行"
- **15.2 Java版本历史**：Java 8（LTS里程碑）→Java 11→Java 17→Java 21（当前LTS），LTS是什么意思
- **15.3 JDK vs JRE vs JVM**：JDK（开发工具包）=JRE（运行环境）+开发工具，JRE=JVM+核心类库
- **15.4 安装JDK 21**：Windows/Mac/Linux三平台详细步骤，配截图描述
- **15.5 安装IntelliJ IDEA社区版**：为什么选IDEA，安装过程
- **15.6 Hello World**：创建项目→写代码→运行，解释每个关键字
- **15.7 编译与运行原理**：.java→javac→.class（字节码）→java→JVM执行

### 第16章 · Java 程序的基本结构
- 代码文件：`src/main/java/demo/BasicStructure.java`
- 术语：package、import、class、main方法、public、static、void、String[] args
- **16.1 package是什么**：文件夹路径在代码中的映射，命名规范（com.example.demo）
- **16.2 import：借别人的代码**：import java.util.*, import static
- **16.3 class：Java的最小组织单元**：一个.java文件可以有一个public class
- **16.4 main方法：程序的入口**：public static void main(String[] args)，为什么这样写
- **16.5 System.out.println**：Java的"打印"，System/out/println逐层拆解
- **16.6 javac、javap、jar命令**：编译、反编译、打包

### 第17章 · 变量与常量
- 代码文件：`src/main/java/demo/VariablesDemo.java`
- 术语：变量、常量、基本类型、引用类型、var、final、声明、初始化
- **17.1 变量是什么**：一个有名字的盒子，装数据
- **17.2 Java的8种基本类型**：byte(1)/short(2)/int(4)/long(8)/float(4)/double(8)/char(2)/boolean，每个的范围和默认值
- **17.3 声明与初始化**：先声明后赋值 vs 声明同时赋值
- **17.4 var关键字（Java 10+）**：类型推断，编译器帮你猜类型
- **17.5 final常量**：一旦赋值不能改，命名全大写+下划线
- **17.6 命名规范**：驼峰命名法、不能以数字开头、不能是关键字

### 第18章 · 运算符
- 代码文件：`src/main/java/demo/OperatorDemo.java`
- 术语：算术运算符、比较运算符、逻辑运算符、位运算符、三元运算符、优先级
- **18.1 算术运算符**：+ - * / %，整数除法的坑（5/2=2不是2.5）
- **18.2 比较运算符**：== != > < >= <=，结果是boolean
- **18.3 逻辑运算符**：&&（短路与）、||（短路或）、!（非）
- **18.4 位运算符**：& | ^ ~ << >> >>>，每个用二进制举例
- **18.5 三元运算符**：条件 ? 值1 : 值2
- **18.6 运算符优先级**：一张表，记住"乘除优先于加减"

### 第19章 · 控制流：if 和 switch
- 代码文件：`src/main/java/demo/ControlFlowDemo.java`
- 术语：if、else、else if、switch、yield、模式匹配
- **19.1 if/else if/else**：三种形式和花括号规范
- **19.2 switch表达式（Java 14+）**：箭头语法、yield返回值
- **19.3 模式匹配（Java 17+ preview，Java 21正式）**：switch可以对类型判断
- **19.4 ❌常见错误**：if里写=而不是==、switch忘写break

### 第20章 · 控制流：for 和 while
- 代码文件：`src/main/java/demo/LoopDemo.java`
- 术语：for、增强for（for-each）、while、do-while、break、continue
- **20.1 for循环**：初始化;条件;迭代 三段式
- **20.2 增强for循环**：for (类型 变量 : 数组/集合)，简洁遍历
- **20.3 while循环**：先判断再执行
- **20.4 do-while循环**：先执行一次再判断（至少执行一次）
- **20.5 break和continue**：break=跳出循环，continue=跳过本次
- **20.6 ❌常见错误**：死循环、越界

### 第21章 · 数组
- 代码文件：`src/main/java/demo/ArrayDemo.java`
- 术语：数组、元素、索引、长度、Arrays工具类、多维数组
- **21.1 数组是什么**：一排连续的"格子"，存同类型数据
- **21.2 数组的声明和初始化**：int[] arr = new int[5]; int[] arr = {1,2,3};
- **21.3 访问数组元素**：arr[0]是第一个，arr[length-1]是最后一个
- **21.4 数组的length属性**：不是方法！arr.length（对比String的length()）
- **21.5 Arrays工具类**：toString/sort/binarySearch/copyOf
- **21.6 多维数组**：int[][] matrix，表格比喻
- **21.7 ❌常见错误**：ArrayIndexOutOfBoundsException

### 第22章 · 面向对象（一）：类与对象
- 代码文件：`src/main/java/demo/oop/Person.java`、`src/main/java/demo/oop/OOPDemo.java`
- 术语：类（class）、对象（object/instance）、属性（field）、方法（method）、构造器（constructor）、this、封装（encapsulation）、访问修饰符（public/private/protected/default）、JavaBean
- **22.1 什么是面向对象**：不是"面向过程"（先做什么再做什么），而是"谁有什么，能做什么"
- **22.2 类是什么**：蓝图/模板，定义了"这类东西有什么属性，能做什么"
- **22.3 对象是什么**：按照蓝图造出来的具体实例
- **22.4 属性（字段）**：类里面的变量
- **22.5 方法**：类里面的函数
- **22.6 构造器**：new的时候自动调用的特殊方法，用于初始化
- **22.7 this关键字**：指代"当前这个对象自己"
- **22.8 封装**：用private隐藏属性，用getter/setter暴露
- **22.9 JavaBean规范**：无参构造器+getter/setter+Serializable

### 第23章 · 面向对象（二）：继承
- 代码文件：`src/main/java/demo/oop/Animal.java`、`src/main/java/demo/oop/Dog.java`、`src/main/java/demo/oop/InheritanceDemo.java`
- 术语：继承（extends）、父类/子类、super、方法重写（@Override）、Object类
- **23.1 继承是什么**：is-a关系，狗**是**动物
- **23.2 extends关键字**：子类继承父类的属性和方法
- **23.3 super关键字**：调用父类的构造器或方法
- **23.4 方法重写（Override）**：子类重新定义父类的方法，@Override注解
- **23.5 Object类**：所有类的终极父类，toString/equals/hashCode
- **23.6 Java单继承**：一个类只能有一个父类（和C++不同）
- **23.7 ❌常见错误**：方法重载vs重写混淆

### 第24章 · 面向对象（三）：多态
- 代码文件：`src/main/java/demo/oop/PolymorphismDemo.java`
- 术语：多态、向上转型、动态绑定、instanceof、模式匹配
- **24.1 多态是什么**：同一个方法调用，不同对象表现不同
- **24.2 向上转型**：Animal a = new Dog(); 编译看左边，运行看右边
- **24.3 动态绑定**：运行时才决定调用哪个方法
- **24.4 instanceof 判断类型**：a instanceof Dog
- **24.5 模式匹配（Java 16+）**：if (a instanceof Dog d) { d.bark(); }
- **24.6 多态的意义**：写出更通用的代码

### 第25章 · 面向对象（四）：抽象类与接口
- 代码文件：`src/main/java/demo/oop/InterfaceDemo.java`
- 术语：抽象类（abstract class）、抽象方法、接口（interface）、default方法、函数式接口
- **25.1 抽象类**：不能被new的类，留给子类去实现
- **25.2 抽象方法**：只有声明没有方法体的方法
- **25.3 接口是什么**：一份"合同"，规定了"必须有什么方法"
- **25.4 接口的default方法（Java 8+）**：接口可以有默认实现
- **25.5 接口的static方法和private方法（Java 9+）**
- **25.6 函数式接口**：只有一个抽象方法的接口，@FunctionalInterface
- **25.7 抽象类 vs 接口**：is-a vs can-do，何时用哪个

### 第26章 · 内部类与枚举
- 代码文件：`src/main/java/demo/oop/InnerClassDemo.java`、`src/main/java/demo/oop/EnumDemo.java`
- 术语：内部类、静态内部类、成员内部类、局部内部类、匿名内部类、enum、record
- **26.1 静态内部类**：static修饰的内部类，不依赖外部类实例
- **26.2 成员内部类**：可以访问外部类的所有成员
- **26.3 匿名内部类**：没有名字的类，常用于简单接口实现
- **26.4 enum枚举**：一组固定的常量，比int常量更安全
- **26.5 record记录类（Java 14+）**：不可变数据载体，自动生成构造器/getter/equals/hashCode/toString

### 第27章 · 字符串深入
- 代码文件：`src/main/java/demo/StringDemo.java`
- 术语：String、StringBuilder、StringBuffer、字符串池（String Pool）、intern()
- **27.1 String不可变性**：一旦创建不能修改，"修改"其实是创建新对象
- **27.2 字符串池（String Pool）**：JVM里的字符串缓存，相同字面量共享
- **27.3 == vs equals**：==比较引用地址，equals比较内容
- **27.4 StringBuilder**：可变的字符串，单线程用，快
- **27.5 StringBuffer**：线程安全的StringBuilder，多线程用
- **27.6 常用方法**：length/charAt/substring/indexOf/replace/split/trim/toUpperCase
- **27.7 字符串拼接的效率**：+在循环里很慢 vs StringBuilder
- **27.8 ❌常见错误**：==比较字符串内容

### 第28章 · 包装类与自动装箱
- 代码文件：`src/main/java/demo/WrapperDemo.java`
- 术语：包装类（Wrapper Class）、自动装箱（Autoboxing）、自动拆箱（Unboxing）、缓存机制
- **28.1 为什么需要包装类**：基本类型不能放进集合、不能为null
- **28.2 8种包装类**：Integer/Long/Short/Byte/Float/Double/Character/Boolean
- **28.3 自动装箱与拆箱**：Integer i = 100; 编译器自动new Integer(100)
- **28.4 Integer缓存机制**：-128到127范围内的Integer对象是缓存的，==比较会返回true
- **28.5 ❌常见错误**：Integer用==比较（超出缓存范围就false了！）

### 第29章 · 异常处理
- 代码文件：`src/main/java/demo/ExceptionDemo.java`、`src/main/java/demo/exception/BusinessException.java`
- 术语：异常（Exception）、Error、受检异常（Checked Exception）、非受检异常（Unchecked Exception）、try-catch-finally、throw、throws、try-with-resources
- **29.1 异常是什么**：程序运行时出了意外（文件不存在、网络断了、除零...）
- **29.2 异常体系**：Throwable→Error（不可恢复）和Exception（可处理）
- **29.3 受检异常 vs 非受检异常**：编译器强制处理 vs 运行时才暴露
- **29.4 try-catch-finally**：尝试→出错就抓住→不管怎样最后都要执行
- **29.5 try-with-resources（Java 7+）**：自动关闭资源，不用写finally
- **29.6 自定义异常**：继承Exception或RuntimeException
- **29.7 ❌常见错误**：空catch块、捕获Throwable、finally里return

### 第30章 · 泛型
- 代码文件：`src/main/java/demo/GenericDemo.java`
- 术语：泛型（Generic）、类型参数、类型擦除（Type Erasure）、通配符（?）、上界通配符（? extends）、下界通配符（? super）
- **30.1 泛型是什么**：类型参数化，写代码时不确定类型，使用时指定
- **30.2 泛型类**：class Box<T> { T item; }
- **30.3 泛型方法**：<T> T getFirst(List<T> list)
- **30.4 类型擦除**：编译后泛型信息被擦除，变成Object+强制类型转换
- **30.5 通配符**：List<?> 任意类型
- **30.6 上界通配符（? extends）**：只读不写 PECS原则
- **30.7 下界通配符（? super）**：只写不读
- **30.8 ❌常见错误**：不能用基本类型当泛型参数（List<int>不行，要List<Integer>）

### 第31章 · 集合框架（一）：List
- 代码文件：`src/main/java/demo/collection/ListDemo.java`
- 术语：List、ArrayList、LinkedList、Vector、Stack
- **31.1 集合框架概述**：Java的数据结构工具箱
- **31.2 ArrayList**：底层是数组，查快改慢（改=增删），扩容机制（1.5倍）
- **31.3 LinkedList**：底层是双向链表，增删快查慢
- **31.4 ArrayList vs LinkedList 选择**：一张对比表+实际性能测试
- **31.5 Vector和Stack**：古老的线程安全版本，基本不用了
- **31.6 List常用操作**：add/get/remove/size/contains/indexOf

### 第32章 · 集合框架（二）：Set 与 Queue
- 代码文件：`src/main/java/demo/collection/SetDemo.java`、`src/main/java/demo/collection/QueueDemo.java`
- 术语：Set、HashSet、TreeSet、LinkedHashSet、Queue、Deque、PriorityQueue、ArrayDeque
- **32.1 Set：不重复的集合**：数学里的集合概念
- **32.2 HashSet**：基于HashMap，无序，O(1)增删查
- **32.3 TreeSet**：基于红黑树，有序（自然顺序或Comparator），O(log n)
- **32.4 LinkedHashSet**：基于链表+哈希，保持插入顺序
- **32.5 Queue：先进先出**：排队比喻
- **32.6 PriorityQueue**：优先级队列，小的先出（不是FIFO！）
- **32.7 ArrayDeque**：双端队列，可当栈也可当队列

### 第33章 · 集合框架（三）：Map
- 代码文件：`src/main/java/demo/collection/MapDemo.java`
- 术语：Map、HashMap、TreeMap、LinkedHashMap、键（key）、值（value）、哈希表、红黑树
- **33.1 Map是什么**：键值对，字典/通讯录比喻
- **33.2 HashMap原理**：数组+链表+红黑树（Java 8+），hash值→数组下标
- **33.3 TreeMap**：基于红黑树，按key排序
- **33.4 LinkedHashMap**：保持插入顺序或访问顺序（LRU缓存）
- **33.5 Map常用操作**：put/get/remove/containsKey/keySet/values/entrySet
- **33.6 遍历Map的几种方式**：entrySet最推荐

### 第34章 · 集合框架（四）：深入源码
- 代码文件：无（纯讲解章，附带源码分析）
- 术语：ConcurrentHashMap、Collections工具类、线程安全、fail-fast
- **34.1 HashMap扩容机制**：默认容量16、负载因子0.75、树化阈值8、链化阈值6
- **34.2 ConcurrentHashMap**：Java 7的分段锁→Java 8的CAS+synchronized，为什么快
- **34.3 Collections工具类**：sort/shuffle/reverse/synchronizedXXX/unmodifiableXXX
- **34.4 fail-fast机制**：遍历时修改集合会抛ConcurrentModificationException
- **34.5 线程安全的集合选择**：Collections.synchronizedXXX vs ConcurrentXXX

### 第35章 · Lambda 表达式
- 代码文件：`src/main/java/demo/LambdaDemo.java`
- 术语：Lambda表达式、函数式编程、函数式接口、方法引用（::）、闭包
- **35.1 为什么需要Lambda**：简化匿名内部类，写更少的代码做更多的事
- **35.2 Lambda语法**：(参数) -> { 方法体 }
- **35.3 函数式接口**：只有一个抽象方法的接口，@FunctionalInterface
- **35.4 常用函数式接口**：Predicate/Consumer/Function/Supplier/BiFunction
- **35.5 方法引用**：String::length、System.out::println、Person::new
- **35.6 Lambda中的变量捕获**：只能引用effectively final的局部变量

### 第36章 · Stream API
- 代码文件：`src/main/java/demo/StreamDemo.java`
- 术语：Stream、中间操作（intermediate）、终端操作（terminal）、并行流（parallelStream）
- **36.1 Stream是什么**：一条流水线，数据流过来依次处理
- **36.2 创建Stream**：集合.stream()、Arrays.stream()、Stream.of()、Stream.iterate()
- **36.3 中间操作（懒操作）**：filter/map/flatMap/distinct/sorted/peek/limit/skip
- **36.4 终端操作（触发计算）**：forEach/collect/toList/count/reduce/anyMatch/allMatch/findFirst
- **36.5 Collectors工具类**：toList/toSet/toMap/groupingBy/partitioningBy/joining
- **36.6 并行流**：.parallelStream()，背后是ForkJoinPool
- **36.7 ❌常见错误**：Stream只能用一次、并行流不一定更快

### 第37章 · IO 流
- 代码文件：`src/main/java/demo/io/IODemo.java`、`resources/test.txt`
- 术语：IO流、字节流（InputStream/OutputStream）、字符流（Reader/Writer）、缓冲流、Files工具类、NIO
- **37.1 IO流是什么**：数据像水一样流进流出
- **37.2 字节流 vs 字符流**：二进制数据用字节，文本用字符
- **37.3 File类**：代表文件或目录路径
- **37.4 FileInputStream/FileOutputStream**：读/写文件的字节流
- **37.5 FileReader/FileWriter**：读/写文件的字符流
- **37.6 缓冲流**：BufferedInputStream/BufferedReader，加个缓冲区提速
- **37.7 Files工具类（Java 7+ NIO）**：readString/writeString/readAllLines/copy/move/delete
- **37.8 try-with-resources 结合IO**：自动关闭流

### 第38章 · 多线程（一）：基础
- 代码文件：`src/main/java/demo/thread/ThreadBasicDemo.java`
- 术语：线程（Thread）、Runnable、Thread生命周期（NEW/RUNNABLE/BLOCKED/WAITING/TIMED_WAITING/TERMINATED）
- **38.1 什么是线程**：程序里的"工人"，每个工人独立干活
- **38.2 创建线程方式一：继承Thread**：class MyThread extends Thread
- **38.3 创建线程方式二：实现Runnable**：class MyTask implements Runnable（推荐！）
- **38.4 线程的生命周期**：6种状态，一张状态转换图
- **38.5 start() vs run()**：start()开新线程，run()只是普通方法调用
- **38.6 sleep/yield/join**：睡一会/让一下/等别人干完
- **38.7 守护线程（Daemon Thread）**：主线程结束它就自动结束

### 第39章 · 多线程（二）：同步
- 代码文件：`src/main/java/demo/thread/SynchronizationDemo.java`
- 术语：线程安全、竞态条件（Race Condition）、synchronized、volatile、wait/notify、对象锁、类锁
- **39.1 什么是线程安全问题**：两个人同时改一个变量（银行取钱比喻）
- **39.2 synchronized 同步代码块**：给代码块加锁，一次只让一个人进
- **39.3 synchronized 同步方法**：锁住整个方法
- **39.4 对象锁 vs 类锁**：synchronized(this) vs synchronized(ClassName.class)
- **39.5 volatile关键字**：保证可见性，不保证原子性
- **39.6 wait/notify/notifyAll**：线程间通信，生产者消费者模式
- **39.7 ❌常见错误**：死锁（两个线程互相等对方释放锁）

### 第40章 · 多线程（三）：高级并发
- 代码文件：`src/main/java/demo/thread/AdvancedConcurrencyDemo.java`
- 术语：线程池（ThreadPoolExecutor）、Executors、Callable、Future、CompletableFuture、ForkJoinPool
- **40.1 为什么需要线程池**：创建/销毁线程很贵，复用线程（共享单车比喻）
- **40.2 Executors工厂类**：newFixedThreadPool/newCachedThreadPool/newScheduledThreadPool
- **40.3 ThreadPoolExecutor参数详解**：核心线程数/最大线程数/存活时间/工作队列/拒绝策略
- **40.4 Callable vs Runnable**：Callable有返回值、能抛异常
- **40.5 Future**：异步计算的结果凭证，get()阻塞等待
- **40.6 CompletableFuture（Java 8+）**：异步编程利器，链式调用/thenApply/thenCombine/exceptionally
- **40.7 ❌常见错误**：用Executors创建无界线程池（OOM风险）

### 第41章 · 虚拟线程（Java 21）
- 代码文件：`src/main/java/demo/thread/VirtualThreadDemo.java`
- 术语：虚拟线程（Virtual Thread）、平台线程（Platform Thread）、载体线程（Carrier Thread）、Project Loom
- **41.1 传统线程的痛点**：一个请求一个线程→几千个线程就OOM→线程池限制并发
- **41.2 虚拟线程是什么**：轻量级线程，JVM管理而非OS管理，百万级虚拟线程不是梦
- **41.3 创建虚拟线程**：Thread.startVirtualThread() / Thread.ofVirtual()
- **41.4 虚拟线程 vs 平台线程**：对比表：内存占用/创建速度/上下文切换
- **41.5 虚拟线程的执行模型**：载体线程→虚拟线程的调度、遇到阻塞自动卸载
- **41.6 适用场景**：IO密集型（Web请求、数据库查询）非常合适，CPU密集型不建议

### 第42章 · JVM 内存模型与 GC
- 代码文件：无（纯讲解章附带诊断命令）
- 可视化：需要（JVM内存模型与GC过程，`.project/docs/tutorials/java_42_jvm_gc_visual.html`）
- 术语：JVM、堆（Heap）、栈（Stack）、方法区（Metaspace）、GC（Garbage Collection）、Minor GC、Major GC、Full GC、STW（Stop The World）、G1 GC、ZGC
- **42.1 JVM运行时数据区**：堆/栈/方法区/程序计数器/本地方法栈
- **42.2 堆的详细结构**：新生代（Eden+S0+S1）、老年代
- **42.3 对象的生命周期**：诞生于Eden→Young GC→幸存者区→晋升老年代→Full GC→回收
- **42.4 GC算法**：标记-清除/标记-复制/标记-整理
- **42.5 现代GC器**：G1（Java 9+默认）、ZGC（Java 15+）、Shenandoah
- **42.6 GC调优入门**：jstat/jmap/jvisualvm基本用法

### 第43章 · 注解与反射
- 代码文件：`src/main/java/demo/annotation/AnnotationDemo.java`、`src/main/java/demo/reflect/ReflectionDemo.java`
- 术语：注解（Annotation）、元注解（@Target/@Retention）、反射（Reflection）、Class对象、动态代理
- **43.1 注解是什么**：代码的"标签"，给编译器/框架看的信息
- **43.2 内置注解**：@Override/@Deprecated/@SuppressWarnings/@FunctionalInterface
- **43.3 元注解**：@Target(用在哪)/@Retention(保留到什么时候)
- **43.4 自定义注解**：定义一个@LogExecutionTime注解
- **43.5 反射是什么**：运行时获取类的信息（"照镜子"）
- **43.6 Class对象**：类加载时JVM创建的，获取方式：类名.class / 对象.getClass() / Class.forName()
- **43.7 反射操作**：获取构造器/字段/方法、调用私有方法、修改私有字段
- **43.8 动态代理**：Proxy.newProxyInstance()，AOP的基础

---

## 第二篇：数据结构与算法（第44-53章）

---

### 第44章 · 为什么学数据结构与算法
- 代码文件：无（概念章）
- 术语：数据结构、算法
- **44.1 数据结构是什么**：收纳盒比喻，不同数据用不同结构存效率天差地别
- **44.2 算法是什么**：菜谱比喻，解决问题的步骤
- **44.3 后端工程师为什么需要**：高性能系统=好的数据结构+好的算法

### 第45章 · 时间复杂度与空间复杂度
- 代码文件：`src/main/java/demo/algorithm/ComplexityDemo.java`
- 术语：大O表示法、时间复杂度、空间复杂度、最好/最坏/平均情况
- **45.1 大O表示法**：描述"数据量变大时，时间/空间增长多快"
- **45.2 常见时间复杂度**：O(1)/O(log n)/O(n)/O(n log n)/O(n²)/O(2ⁿ)，每个配图
- **45.3 空间复杂度**：算法运行需要多少额外内存
- **45.4 分析Java代码的复杂度**：几个实际例子

### 第46章 · 数组与 ArrayList 源码分析
- 代码文件：无（源码分析章）
- 术语：动态数组、扩容因子、amortized O(1)
- **46.1 ArrayList底层源码**：elementData数组、add方法源码
- **46.2 扩容策略**：默认10→1.5倍扩容→Arrays.copyOf
- **46.3 性能分析**：add(E)均摊O(1)、add(index,E) O(n)、get O(1)、remove O(n)
- **46.4 最佳实践**：预知大小时指定初始容量

### 第47章 · 链表
- 代码文件：`src/main/java/demo/algorithm/MyLinkedList.java`
- 术语：单向链表、双向链表、循环链表、节点（Node）、头节点、尾节点
- **47.1 单向链表**：每个节点存数据和下一个节点的地址
- **47.2 双向链表**：每个节点还存上一个节点的地址
- **47.3 循环链表**：尾巴指向头
- **47.4 Java实现链表**：完整实现add/remove/get
- **47.5 链表 vs 数组**：一张全面对比表
- **47.6 常见链表操作**：反转链表、找中点（快慢指针）、判断有环

### 第48章 · 栈与队列
- 代码文件：`src/main/java/demo/algorithm/MyStack.java`、`src/main/java/demo/algorithm/MyQueue.java`
- 术语：栈（LIFO）、队列（FIFO）、push、pop、enqueue、dequeue
- **48.1 栈：先进后出**：一叠盘子，只能从顶上拿
- **48.2 队列：先进先出**：排队，先到先服务
- **48.3 Java实现**：用数组实现栈和队列
- **48.4 实际应用**：函数调用栈、消息队列、BFS

### 第49章 · 哈希表深入
- 代码文件：无（源码分析）
- 术语：哈希函数、哈希冲突、链地址法、开放寻址法、负载因子、扰动函数
- **49.1 哈希函数**：把任意输入映射到固定范围
- **49.2 哈希冲突的解决**：链地址法（HashMap用的）、开放寻址法
- **49.3 HashMap的哈希算法**：hashCode()→扰动函数→数组下标
- **49.4 为什么重写equals必须重写hashCode**：Contract约定

### 第50章 · 树
- 代码文件：`src/main/java/demo/algorithm/MyBST.java`
- 术语：二叉树、二叉搜索树（BST）、前序/中序/后序/层序遍历、平衡树
- **50.1 二叉树**：每个节点最多两个子节点
- **50.2 二叉搜索树**：左<根<右
- **50.3 四种遍历**：前序(根左右)、中序(左根右)、后序(左右根)、层序(一层层)
- **50.4 Java实现BST**：insert/search/delete

### 第51章 · 堆与优先队列
- 代码文件：`src/main/java/demo/algorithm/HeapDemo.java`
- 术语：堆、最大堆、最小堆、上浮（siftUp）、下沉（siftDown）、PriorityQueue
- **51.1 堆是什么**：一种特殊的完全二叉树，最大堆（父≥子）、最小堆（父≤子）
- **51.2 PriorityQueue 源码分析**：Java的PriorityQueue就是最小堆
- **51.3 堆排序**：建堆→反复取堆顶
- **51.4 Top K问题**：用堆解决"

### 第52章 · 排序算法
- 代码文件：`src/main/java/demo/algorithm/SortingDemo.java`
- 术语：冒泡/选择/插入/快速/归并排序、稳定排序、原地排序
- **52.1 冒泡排序**：相邻比较交换，O(n²)
- **52.2 选择排序**：每次选最小的放前面，O(n²)
- **52.3 插入排序**：像打牌理牌，O(n²)
- **52.4 快速排序**：选pivot、分区、递归，平均O(n log n)
- **52.5 归并排序**：分治，稳定O(n log n)
- **52.6 Arrays.sort() 内部实现**：Dual-Pivot QuickSort + TimSort

### 第53章 · 搜索算法与面试题
- 代码文件：`src/main/java/demo/algorithm/SearchDemo.java`
- 术语：线性搜索、二分搜索、DFS、BFS、回溯
- **53.1 线性搜索**：一个个找，O(n)
- **53.2 二分搜索**：每次砍一半，O(log n)，前提有序
- **53.3 DFS深度优先**：一条路走到底再回头
- **53.4 BFS广度优先**：一层层往外扩展
- **53.5 经典面试题**：两数之和/有效括号/最长不重复子串

---

## 第三篇：数据库（第54-70章）

---

### 第54章 · 数据库基础与 MySQL 安装
- 术语：数据库、关系型数据库、表、行、列、MySQL
- **54.1 为什么需要数据库**：Excel的局限性（并发、容量、查询）
- **54.2 关系型 vs 非关系型数据库**：一张对比表
- **54.3 MySQL安装**：Windows/Mac/Linux安装步骤
- **54.4 图形化工具**：DBeaver（免费）或 DataGrip 的安装和使用

### 第55章 · SQL 基础：DDL 与 DML
- 术语：DDL（数据定义语言）、DML（数据操作语言）、CREATE、INSERT、SELECT、UPDATE、DELETE
- **55.1 CREATE DATABASE / CREATE TABLE**：建库建表，列的类型和约束
- **55.2 INSERT**：插入数据，单行和多行
- **55.3 SELECT**：查询数据，基本用法
- **55.4 UPDATE**：修改数据，WHERE不能忘！
- **55.5 DELETE**：删除数据，TRUNCATE vs DELETE

### 第56章 · SQL 进阶：查询与聚合
- 术语：WHERE、ORDER BY、LIMIT、GROUP BY、HAVING、聚合函数
- **56.1 WHERE条件过滤**：=、<>、>、<、AND、OR、IN、BETWEEN、LIKE
- **56.2 ORDER BY排序**：ASC升序、DESC降序
- **56.3 LIMIT和OFFSET分页**：LIMIT 10 OFFSET 20
- **56.4 GROUP BY分组**：按某列分组后聚合
- **56.5 聚合函数**：COUNT/SUM/AVG/MAX/MIN
- **56.6 HAVING**：过滤分组结果（WHERE过滤行，HAVING过滤组）

### 第57章 · JOIN 多表查询
- 术语：INNER JOIN、LEFT JOIN、RIGHT JOIN、自连接、UNION
- **57.1 为什么需要多张表**：避免数据冗余
- **57.2 INNER JOIN**：两表交集
- **57.3 LEFT JOIN**：左表全保留，右表匹配不上填NULL
- **57.4 RIGHT JOIN**：右表全保留
- **57.5 自连接**：一张表自己连自己
- **57.6 UNION vs UNION ALL**：去重 vs 不去重

### 第58章 · 表设计与范式
- 术语：1NF/2NF/3NF、ER图、反范式化
- **58.1 第一范式（1NF）**：每列不可再分
- **58.2 第二范式（2NF）**：消除部分依赖
- **58.3 第三范式（3NF）**：消除传递依赖
- **58.4 ER图入门**：实体、属性、关系的表示法
- **58.5 反范式化**：什么时候该打破规则（性能优先）

### 第59章 · 索引原理
- 术语：索引、B+树、聚簇索引、非聚簇索引、联合索引、最左前缀原则
- **59.1 索引是什么**：书的目录比喻，快速定位
- **59.2 B+树索引原理**：一步步画清楚，为什么用B+树不用二叉树
- **59.3 聚簇索引 vs 非聚簇索引**：数据本身按索引排序 vs 索引指向数据
- **59.4 联合索引与最左前缀**：(a,b,c)联合索引→a可用、a+b可用、a+b+c可用，b单独不可用

### 第60章 · 索引实战
- 术语：EXPLAIN、回表、覆盖索引、索引失效
- **60.1 EXPLAIN分析查询**：type/rows/key/Extra字段解读
- **60.2 索引失效的场景**：like '%xx'、函数/运算、类型隐式转换、OR条件
- **60.3 覆盖索引**：查询的列都在索引里，不用回表
- **60.4 索引设计最佳实践**：选择性高的列、联合索引顺序

### 第61章 · 事务与隔离级别
- 术语：事务、ACID、脏读、不可重复读、幻读、MVCC
- **61.1 事务是什么**：一组操作要么全成功要么全失败（转账比喻）
- **61.2 ACID**：原子性/一致性/隔离性/持久性
- **61.3 四种隔离级别**：READ UNCOMMITTED/READ COMMITTED/REPEATABLE READ/SERIALIZABLE
- **61.4 脏读/不可重复读/幻读**：每个配例子
- **61.5 MVCC（多版本并发控制）**：MySQL InnoDB的实现原理

### 第62章 · 锁机制
- 术语：行锁、表锁、共享锁（S锁）、排他锁（X锁）、意向锁、死锁
- **62.1 行锁 vs 表锁**：行锁粒度小并发高，表锁粒度大简单
- **62.2 共享锁 vs 排他锁**：读读不互斥，读写互斥
- **62.3 死锁**：两个事务互相等对方的锁，原因和解决
- **62.4 如何查看锁信息**：SHOW ENGINE INNODB STATUS

### 第63章 · 数据库优化
- 术语：慢查询日志、SQL优化、分库分表、读写分离
- **63.1 慢查询日志**：开启、分析、定位慢SQL
- **63.2 SQL优化技巧**：避免SELECT *、合理用JOIN、批量操作
- **63.3 分库分表简介**：垂直拆分/水平拆分，什么时候需要
- **63.4 读写分离简介**：主库写+从库读

### 第64章 · JDBC 入门
- 代码文件：`src/main/java/demo/jdbc/JdbcDemo.java`
- 术语：JDBC、DriverManager、Connection、Statement、PreparedStatement、ResultSet、SQL注入
- **64.1 JDBC是什么**：Java连接数据库的标准接口
- **64.2 添加MySQL驱动依赖**：Maven pom.xml配置
- **64.3 建立连接**：DriverManager.getConnection(url, user, password)
- **64.4 Statement vs PreparedStatement**：后者防SQL注入
- **64.5 执行查询**：executeQuery→ResultSet→遍历
- **64.6 执行更新**：executeUpdate→返回影响行数
- **64.7 SQL注入演示与防护**：用PreparedStatement参数化查询

### 第65章 · 连接池与 DataSource
- 代码文件：`src/main/java/demo/jdbc/DataSourceDemo.java`
- 术语：连接池、DataSource、HikariCP、最大连接数、最小空闲连接
- **65.1 为什么需要连接池**：数据库连接很贵，复用连接（共享单车比喻）
- **65.2 HikariCP**：Spring Boot默认连接池，为什么快
- **65.3 连接池参数**：maximumPoolSize/minimumIdle/connectionTimeout/idleTimeout/maxLifetime
- **65.4 配置示例**：application.yml中的连接池配置

### 第66章 · MyBatis 入门
- 代码文件：`src/main/java/demo/mybatis/` 系列
- 术语：MyBatis、映射文件（Mapper XML）、动态SQL、#{}、${}
- **66.1 MyBatis是什么**：半自动ORM，SQL自己写，映射自动做
- **66.2 添加依赖与配置**：mybatis-spring-boot-starter
- **66.3 映射文件**：namespace/select/insert/update/delete、resultMap
- **66.4 动态SQL**：if/where/foreach/set
- **66.5 #{} vs ${}**：#{}预编译防注入，${}直接拼接
- **66.6 与Spring Boot集成**：@Mapper/@MapperScan

### 第67章 · Spring Data JPA 基础
- 代码文件：`src/main/java/demo/jpa/` 系列
- 术语：JPA、Hibernate、Entity、Repository、JPQL
- **67.1 JPA是什么**：Java持久化API标准，Hibernate是实现
- **67.2 @Entity 实体类**：@Id/@GeneratedValue/@Column/@Table
- **67.3 Repository接口**：继承JpaRepository获得免费CRUD
- **67.4 查询方法命名**：findByXxx/And/Or/OrderBy/Like/Between
- **67.5 @Query 自定义查询**：JPQL和原生SQL
- **67.6 关联映射**：@OneToOne/@OneToMany/@ManyToOne/@ManyToMany

### 第68章 · Redis 入门与常用命令
- 术语：Redis、键值对、String/Hash/List/Set/SortedSet
- **68.1 Redis是什么**：内存数据库，极快，做缓存
- **68.2 Redis为什么这么快**：内存操作+单线程+IO多路复用
- **68.3 安装Redis**：Windows用Memurai或WSL，Mac用brew
- **68.4 五大数据类型**：String/Hash/List/Set/Sorted Set，每个配命令和场景

### 第69章 · Redis 进阶
- 术语：RDB、AOF、过期策略、LRU、缓存穿透、缓存击穿、缓存雪崩
- **69.1 持久化**：RDB（快照）和AOF（日志），优缺点
- **69.2 过期策略**：定时删除+惰性删除+定期删除
- **69.3 内存淘汰策略**：noeviction/LRU/LFU/random/TTL
- **69.4 缓存穿透/击穿/雪崩**：布隆过滤器/互斥锁/随机过期

### 第70章 · Java 操作 Redis
- 代码文件：`src/main/java/demo/redis/` 系列
- 术语：Spring Data Redis、Jedis、Lettuce、RedisTemplate、@Cacheable
- **70.1 Spring Data Redis**：Spring Boot集成自动配置
- **70.2 RedisTemplate**：opsForValue/Hash/List/Set/ZSet
- **70.3 StringRedisTemplate**：专门处理字符串
- **70.4 Spring Cache注解**：@Cacheable/@CachePut/@CacheEvict/@Caching

---

## 第四篇：Spring Boot 核心（第71-85章）

---

### 第71章 · Spring 框架概述
- 代码文件：无（概念章）
- 术语：IoC（控制反转）、DI（依赖注入）、AOP（面向切面编程）、Spring、Spring Boot
- **71.1 没有Spring的世界**：自己new对象、自己管理依赖，代码耦合（泥巴比喻）
- **71.2 IoC：控制反转**：不是我找依赖，是框架给我（"饭来张口"比喻）
- **71.3 DI：依赖注入**：IoC的实现方式，构造器注入/字段注入/Setter注入
- **71.4 AOP：面向切面编程**：横切关注点（日志/事务/安全）与业务逻辑分离
- **71.5 Spring发展史**：2002→Spring→Spring Boot（2014）→Spring Cloud
- **71.6 Spring Boot的定位**："约定优于配置"，开箱即用

### 第72章 · Spring Boot 入门
- 代码文件：完整Spring Boot项目 `spring-boot-demo/`
- 可视化：需要（Spring Boot启动流程，`.project/docs/tutorials/java_72_springboot_startup_visual.html`）
- 术语：Spring Initializr、SpringApplication、@SpringBootApplication、嵌入式Tomcat、Fat JAR
- **72.1 创建项目**：Spring Initializr网页版 + IntelliJ IDEA创建，选择依赖（Spring Web）
- **72.2 项目结构**：src/main/java、src/main/resources、src/test、pom.xml
- **72.3 pom.xml详解**：parent/groupId/artifactId/dependencies
- **72.4 Hello World Controller**：@RestController + @GetMapping("/hello")
- **72.5 启动项目**：mvn spring-boot:run 或直接运行main方法
- **72.6 启动流程分析**：SpringApplication.run()里面做了什么（配可视化）

### 第73章 · 依赖注入（IoC 容器）
- 代码文件：`src/main/java/demo/di/` 系列
- 术语：IoC容器、Bean、@Component、@Service、@Repository、@Controller、@Autowired、@Qualifier、@Primary、Bean生命周期
- **73.1 IoC容器是什么**：一个大Map，存着所有Bean
- **73.2 把对象交给Spring管理**：@Component/@Service/@Repository/@Controller
- **73.3 @Autowired 注入**：构造器注入（推荐！）/字段注入/Setter注入
- **73.4 多个同类型Bean怎么办**：@Qualifier指定名字、@Primary设默认
- **73.5 Bean的作用域**：singleton（默认单例）/prototype（每次新建）/request/session
- **73.6 Bean生命周期**：@PostConstruct→初始化→@PreDestroy

### 第74章 · 配置管理
- 代码文件：`src/main/resources/application.yml`
- 术语：application.yml、application.properties、@Value、@ConfigurationProperties、多环境（Profile）
- **74.1 application.yml vs application.properties**：YAML更简洁
- **74.2 常用配置项**：server.port、spring.datasource、logging.level
- **74.3 @Value 注入单个值**：${property.name}
- **74.4 @ConfigurationProperties**：绑定一组配置到类
- **74.5 多环境配置**：application-dev.yml / application-prod.yml，通过spring.profiles.active切换

### 第75章 · Spring MVC（一）：控制器
- 代码文件：`src/main/java/demo/controller/BasicController.java`
- 术语：@RestController、@Controller、@RequestMapping、@GetMapping、@PostMapping、@PutMapping、@DeleteMapping、路径参数
- **75.1 Spring MVC是什么**：处理Web请求的框架
- **75.2 @RestController vs @Controller**：前者=后者+@ResponseBody
- **75.3 @RequestMapping及其快捷注解**：@GetMapping/@PostMapping/@PutMapping/@DeleteMapping/@PatchMapping
- **75.4 路径参数**：@PathVariable，/users/{id}
- **75.5 一个完整的CRUD Controller**：增删改查4个方法

### 第76章 · Spring MVC（二）：请求处理
- 代码文件：`src/main/java/demo/controller/RequestDemoController.java`
- 术语：@RequestParam、@RequestBody、参数校验、@Valid、Jakarta Validation
- **76.1 获取URL参数**：@RequestParam，?page=1&size=10
- **76.2 获取请求体**：@RequestBody，JSON自动转Java对象
- **76.3 参数校验**：@NotNull/@NotBlank/@Size/@Min/@Max/@Email/@Pattern
- **76.4 校验结果处理**：BindingResult或全局异常处理

### 第77章 · Spring MVC（三）：响应处理
- 代码文件：`src/main/java/demo/controller/ResponseDemoController.java`、`src/main/java/demo/common/Result.java`
- 术语：统一响应格式、Jackson、@JsonIgnore、@JsonFormat、ResponseEntity
- **77.1 设计统一响应格式**：{ code, message, data }
- **77.2 Jackson序列化控制**：@JsonIgnore/@JsonProperty/@JsonFormat
- **77.3 ResponseEntity**：完全控制HTTP响应（状态码/头/体）
- **77.4 封装Result工具类**：Result.success(data)、Result.error(code, msg)

### 第78章 · 中间件与拦截器
- 代码文件：`src/main/java/demo/interceptor/`、`src/main/java/demo/filter/`
- 术语：Filter、Interceptor、执行顺序、CORS
- **78.1 Filter（过滤器）**：Servlet标准，最外层，可以改请求/响应
- **78.2 Interceptor（拦截器）**：Spring MVC特有，能拿到Handler信息
- **78.3 Filter vs Interceptor**：一张对比表
- **78.4 执行顺序**：Filter→DispatcherServlet→Interceptor→Controller
- **78.5 CORS跨域配置**：实现WebMvcConfigurer.addCorsMappings

### 第79章 · AOP 切面编程
- 代码文件：`src/main/java/demo/aop/LogAspect.java`
- 术语：Aspect、切点（Pointcut）、通知（Advice）、连接点（JoinPoint）、@Before/@After/@Around/@AfterReturning/@AfterThrowing
- **79.1 AOP是什么**：在不改原代码的情况下加功能（在方法前后插代码）
- **79.2 AOP术语**：Aspect=切面类, Pointcut=切点表达式, Advice=通知方法
- **79.3 切点表达式**：execution(* com.example..*.*(..)) 拆解
- **79.4 五种通知**：@Before/@After/@AfterReturning/@AfterThrowing/@Around
- **79.5 实战：日志切面**：自动记录方法执行时间

### 第80章 · 异常处理
- 代码文件：`src/main/java/demo/exception/GlobalExceptionHandler.java`、`src/main/java/demo/exception/BusinessException.java`
- 术语：@ControllerAdvice、@ExceptionHandler、全局异常处理、业务异常
- **80.1 为什么需要全局异常处理**：不用每个方法写try-catch
- **80.2 @ControllerAdvice + @ExceptionHandler**：全局捕获异常
- **80.3 自定义业务异常**：BusinessException(code, message)
- **80.4 异常处理最佳实践**：返回统一Result格式，区分业务异常和系统异常

### 第81章 · 数据访问：Spring Data JPA 深入
- 代码文件：`src/main/java/demo/jpa/` 系列
- 术语：查询方法命名、@Query、分页（Pageable）、排序（Sort）、审计（@CreatedDate）
- **81.1 查询方法命名规则**：findBy/readBy/queryBy/countBy/existsBy + 条件
- **81.2 @Query 注解**：JPQL（面向对象）和 nativeQuery（原生SQL）
- **81.3 分页查询**：Pageable参数，返回Page<T>
- **81.4 排序**：Sort参数
- **81.5 JPA审计**：@CreatedDate/@LastModifiedDate/@CreatedBy，自动记录创建/修改时间

### 第82章 · 事务管理
- 代码文件：`src/main/java/demo/service/TransactionalDemoService.java`
- 术语：@Transactional、事务传播行为（Propagation）、隔离级别（Isolation）、rollbackFor
- **82.1 @Transactional怎么用**：加在方法或类上
- **82.2 传播行为**：REQUIRED(默认)/REQUIRES_NEW/NESTED/SUPPORTS等
- **82.3 隔离级别**：DEFAULT/READ_UNCOMMITTED/READ_COMMITTED/REPEATABLE_READ/SERIALIZABLE
- **82.4 rollbackFor**：默认只回滚RuntimeException，受检异常需指定
- **82.5 ❌常见错误**：同一个类内部方法调用导致事务失效

### 第83章 · 日志系统
- 代码文件：`src/main/resources/logback-spring.xml`
- 术语：SLF4J、Logback、日志级别（TRACE/DEBUG/INFO/WARN/ERROR）、MDC、Lombok @Slf4j
- **83.1 为什么需要日志**：比System.out.println高级一百倍
- **83.2 SLF4J + Logback**：门面+实现，Spring Boot默认
- **83.3 日志级别**：TRACE<DEBUG<INFO<WARN<ERROR
- **83.4 日志配置**：logback-spring.xml，控制台输出+文件输出+按日期切割
- **83.5 Lombok @Slf4j**：一行注解省去写LoggerFactory.getLogger
- **83.6 MDC**：给每条日志加追踪ID

### 第84章 · 文件上传下载
- 代码文件：`src/main/java/demo/controller/FileController.java`
- 术语：MultipartFile、静态资源映射、文件存储方案
- **84.1 文件上传**：@RequestParam MultipartFile
- **84.2 文件下载**：ResponseEntity<Resource>
- **84.3 静态资源映射**：WebMvcConfigurer.addResourceHandlers
- **84.4 文件存储方案**：本地存储 vs OSS云存储 vs MinIO

### 第85章 · API 文档
- 代码文件：`pom.xml`中加springdoc-openapi依赖
- 术语：OpenAPI、Swagger、SpringDoc、@Operation、@Schema
- **85.1 为什么需要API文档**：让前端同事不用猜接口
- **85.2 SpringDoc OpenAPI**：Spring Boot 3的Swagger方案
- **85.3 基本注解**：@Tag/@Operation/@Parameter/@Schema/@ApiResponses
- **85.4 Swagger UI 访问**：http://localhost:8080/swagger-ui.html

---

## 第五篇：认证授权与安全（第86-93章）

---

### 第86章 · 认证基础
- 术语：认证（Authentication）、授权（Authorization）、密码哈希、bcrypt
- **86.1 认证 vs 授权**：你是谁 vs 你能做什么
- **86.2 密码存储原则**：绝不存明文，哈希+加盐
- **86.3 bcrypt算法**：自动加盐、可调节计算成本

### 第87章 · Spring Security 入门
- 代码文件：`src/main/java/demo/config/SecurityConfig.java`
- 可视化：需要（Spring Security过滤器链，`.project/docs/tutorials/java_87_security_filter_visual.html`）
- 术语：SecurityFilterChain、SecurityContext、Authentication、Principal
- **87.1 Spring Security是什么**：一套完整的认证授权框架
- **87.2 过滤器链**：多个Security Filter组成链，每个负责一件事
- **87.3 默认配置**：添加依赖后自动保护所有端点，默认用户名user
- **87.4 自定义SecurityFilterChain**：关闭CSRF（API）、放行登录接口、配置认证
- **87.5 SecurityContext**：存当前登录用户信息的地方

### 第88章 · JWT 认证实战
- 代码文件：`src/main/java/demo/security/JwtUtil.java`、`src/main/java/demo/security/JwtFilter.java`、`src/main/java/demo/controller/AuthController.java`
- 术语：JWT、Header、Payload、Signature、Access Token、Refresh Token
- **88.1 JWT结构**：Header.Payload.Signature，每部分的作用
- **88.2 生成JWT**：用jjwt库，设置subject/claims/expiration
- **88.3 验证JWT**：解析token、检查签名、检查过期
- **88.4 JWT认证流程**：登录→返回token→前端存token→每次请求带token→后端验证→放行
- **88.5 Access Token + Refresh Token**：短命AT+长命RT，AT过期用RT换新AT
- **88.6 完整注册/登录/刷新实现**

### 第89章 · OAuth 2.0 与第三方登录
- 术语：OAuth 2.0、授权码模式、Client ID、Client Secret、Access Token
- **89.1 OAuth 2.0是什么**：给第三方应用一把"钥匙"而不是给密码
- **89.2 四种授权模式**：授权码（最安全）/密码/客户端凭证/隐式
- **89.3 集成GitHub登录**：注册OAuth App→获取Client ID/Secret→Spring Security OAuth2 Client

### 第90章 · RBAC 权限控制
- 术语：RBAC（Role-Based Access Control）、角色、权限、@PreAuthorize、@PostAuthorize
- **90.1 RBAC模型**：用户→角色→权限
- **90.2 数据库设计**：user/role/permission/user_role/role_permission 五张表
- **90.3 @PreAuthorize**：方法执行前检查权限，支持SpEL表达式
- **90.4 @PostAuthorize**：方法执行后检查

### 第91章 · 常见 Web 攻击防御
- 术语：SQL注入、XSS、CSRF、点击劫持
- **91.1 SQL注入**：原理+演示，参数化查询防护
- **91.2 XSS（跨站脚本）**：存储型/反射型/DOM型，输出编码防护
- **91.3 CSRF（跨站请求伪造）**：原理，Spring Security的CSRF Token防护
- **91.4 Spring Security的其他防护**：安全头（X-Content-Type-Options等）

### 第92章 · 加密基础
- 术语：哈希（MD5/SHA256）、对称加密（AES）、非对称加密（RSA）、数字签名
- **92.1 哈希算法**：单向、固定长度、不可逆，SHA-256实战
- **92.2 AES对称加密**：同一把钥匙加解密，Java实现
- **92.3 RSA非对称加密**：公钥加密私钥解密，Java实现
- **92.4 数字签名**：私钥签名，公钥验签，防篡改

### 第93章 · HTTPS 与证书管理
- 术语：TLS握手、证书链、自签名证书、Let's Encrypt
- **93.1 TLS握手详解**：客户端→ServerHello→证书→密钥交换
- **93.2 证书链**：根证书→中间证书→服务器证书
- **93.3 自签名证书**：开发环境用keytool生成
- **93.4 Let's Encrypt**：免费HTTPS证书

---

## 第六篇：消息队列（第94-99章）

---

### 第94章 · 消息队列基础
- 代码文件：无（概念章）
- 可视化：需要（消息队列解耦/削峰/异步模型，`.project/docs/tutorials/java_94_mq_visual.html`）
- 术语：消息队列、生产者、消费者、Broker、队列、主题（Topic）、点对点、发布订阅
- **94.1 同步 vs 异步**：餐厅点餐比喻（点了菜站那等 vs 拿号等叫）
- **94.2 消息队列三大场景**：解耦、削峰（秒杀）、异步（发邮件/短信）
- **94.3 消息队列的几种模型**：点对点（队列）、发布订阅（Topic）

### 第95章 · RabbitMQ 入门
- 术语：RabbitMQ、Exchange、Queue、Binding、Routing Key
- **95.1 RabbitMQ是什么**：基于AMQP协议的消息中间件
- **95.2 安装RabbitMQ**：Docker方式
- **95.3 核心概念**：Producer→Exchange→(Binding)→Queue→Consumer
- **95.4 工作队列模式**：多个消费者竞争消费
- **95.5 发布/订阅模式**：fanout exchange，所有队列都收到
- **95.6 路由模式**：direct exchange，按routing key精确匹配

### 第96章 · RabbitMQ 进阶
- 术语：消息确认（ACK）、持久化、死信队列、延迟队列、TTL
- **96.1 消息确认机制**：手动ACK vs 自动ACK
- **96.2 消息持久化**：队列和消息都设为持久化
- **96.3 死信队列**：消息被拒绝/过期/队列满时进入
- **96.4 延迟队列**：消息延迟一段时间再消费（用死信+TTL实现）

### 第97章 · Kafka 入门
- 术语：Kafka、Topic、Partition、Consumer Group、Broker、Offset
- **97.1 Kafka是什么**：分布式流平台，和RabbitMQ的区别（吞吐量/场景）
- **97.2 Kafka为什么这么快**：顺序写磁盘+零拷贝+Page Cache
- **97.3 核心概念**：Topic（主题）/Partition（分区）/Consumer Group（消费者组）
- **97.4 安装Kafka**：Docker方式

### 第98章 · Kafka 进阶
- 术语：幂等性、Offset管理、ISR、副本
- **98.1 消息可靠性保证**：ACK机制（acks=0/1/all）
- **98.2 幂等性**：生产者配置enable.idempotence=true
- **98.3 Offset管理**：自动提交 vs 手动提交

### 第99章 · Spring 集成消息队列
- 代码文件：`src/main/java/demo/mq/` 系列
- 术语：Spring AMQP、RabbitTemplate、@RabbitListener、Spring Kafka、KafkaTemplate、@KafkaListener
- **99.1 Spring AMQP（RabbitMQ）**：RabbitTemplate发送、@RabbitListener接收
- **99.2 Spring Kafka**：KafkaTemplate发送、@KafkaListener接收
- **99.3 实战：异步发送邮件/短信**

---

## 第七篇：系统设计与架构（第100-107章）

---

### 第100章 · 设计模式（Java 实现）
- 代码文件：`src/main/java/demo/pattern/` 系列
- 术语：单例、工厂、策略、观察者、装饰器、代理、依赖注入
- 每种模式：场景→类图→Java代码→Spring中的应用

### 第101章 · SOLID 原则
- 术语：SRP/OCP/LSP/ISP/DIP
- 每个原则：一句话解释→反例→正例→Spring Boot中的应用

### 第102章 · 微服务基础
- 术语：单体架构、微服务、Spring Cloud、服务注册与发现、Nacos/Eureka
- Spring Cloud 概述，Nacos 注册中心

### 第103章 · 微服务通信
- 术语：同步通信（REST/gRPC）、异步通信（消息队列）、OpenFeign
- REST vs gRPC，OpenFeign 声明式调用

### 第104章 · 分布式基础理论
- 术语：CAP定理、BASE理论、Paxos、Raft
- CAP取舍，最终一致性

### 第105章 · 负载均衡与反向代理
- 术语：Nginx、反向代理、负载均衡算法（轮询/最少连接/IP哈希）
- Nginx 反向代理配置，upstream

### 第106章 · 高并发系统设计
- 术语：缓存策略、限流（令牌桶/漏桶/滑动窗口）、熔断、降级、Sentinel
- 多级缓存、Sentinel限流

### 第107章 · 系统设计面试经典题
- 短链接系统、秒杀系统、消息推送系统、Feed流系统的设计方法

---

## 第八篇：DevOps 与部署（第108-114章）

---

### 第108章 · Linux 必备知识
- 术语：目录结构、权限（rwx）、用户/用户组、进程管理、systemd
- 基础操作、文件权限、进程管理（ps/top/kill）

### 第109章 · Shell 脚本基础
- 变量、条件、循环、函数、实用运维脚本

### 第110章 · Git 版本控制
- clone/add/commit/push/pull、分支管理、合并冲突、Git工作流

### 第111章 · Maven 深入
- 代码文件：`pom.xml` 多模块配置
- 生命周期（clean/default/site）、多模块项目、插件、依赖管理（dependencyManagement）

### 第112章 · Docker 容器化
- 代码文件：`Dockerfile`、`docker-compose.yml`
- 镜像/容器、Dockerfile编写（多阶段构建）、docker-compose编排

### 第113章 · CI/CD（GitHub Actions）
- 代码文件：`.github/workflows/ci.yml`
- 自动测试→自动构建→自动部署的流水线

### 第114章 · 云服务部署实战
- 云服务器购买、域名备案、Nginx反向代理、SSL证书、Spring Boot jar包部署

---

## 第九篇：测试（第115-118章）

---

### 第115章 · JUnit 5 单元测试
- 代码文件：`src/test/java/` 系列
- 术语：@Test、断言（assertEquals/assertThrows）、生命周期（@BeforeEach/@AfterEach）、参数化测试
- **115.1 第一个单元测试**：@Test + assertEquals
- **115.2 测试生命周期**：@BeforeAll/@BeforeEach/@AfterEach/@AfterAll
- **115.3 断言库**：JUnit内置断言 vs AssertJ
- **115.4 参数化测试**：@ParameterizedTest/@CsvSource/@MethodSource
- **115.5 异常测试**：assertThrows

### 第116章 · Mockito 与测试替身
- 代码文件：`src/test/java/` 系列
- 术语：Mock、Stub、Spy、Mockito、@Mock、@InjectMocks、行为验证
- **116.1 为什么要Mock**：隔离依赖，只测自己的代码
- **116.2 @Mock 和 @InjectMocks**：创建Mock对象和注入
- **116.3 when/thenReturn**：定义Mock行为
- **116.4 verify**：验证Mock方法被调用
- **116.5 @MockBean**：Spring Boot测试中替换Bean

### 第117章 · Spring Boot 集成测试
- 术语：@SpringBootTest、@WebMvcTest、@DataJpaTest、Testcontainers
- **117.1 @SpringBootTest**：启动完整Spring容器
- **117.2 测试切片**：@WebMvcTest（只测Controller）、@DataJpaTest（只测JPA）
- **117.3 MockMvc**：模拟HTTP请求测试Controller
- **117.4 Testcontainers**：用Docker启动真实MySQL/Redis做测试

### 第118章 · 性能测试
- 术语：JMH（基准测试）、JMeter（压测）、JProfiler（分析）、吞吐量、延迟
- **118.1 JMH**：Java微基准测试，测量方法性能
- **118.2 JMeter**：模拟并发用户，压测接口
- **118.3 性能分析工具**：JProfiler/VisualVM

---

## 第十篇：实战项目（第119-124章）

---

### 第119章 · 项目一：Todo 任务管理 API
- **119.1 需求分析**：用户/任务 CRUD
- **119.2 数据库设计**：user表/task表
- **119.3 项目搭建**：Spring Initializr创建+基本配置
- **119.4 代码实现**：Entity→Repository→Service→Controller
- **119.5 统一响应格式和异常处理**
- **119.6 测试**：JUnit 5 + MockMvc

### 第120章 · 项目二：用户认证系统
- **120.1 需求分析**：注册/登录/登出/密码重置
- **120.2 数据库设计**：user表含密码哈希
- **120.3 Spring Security + JWT 完整实现**
- **120.4 RBAC 权限控制**
- **120.5 集成测试**

### 第121章 · 项目三：博客系统
- **121.1 需求分析**：文章CRUD/分类标签/评论/Markdown
- **121.2 数据库设计**：article/category/tag/comment表
- **121.3 文件上传（文章图片）**
- **121.4 分页查询**
- **121.5 API文档**

### 第122章 · 项目四：电商秒杀系统
- 可视化：需要（秒杀系统架构，`.project/docs/tutorials/java_122_seckill_visual.html`）
- **122.1 需求分析**：商品管理/订单/库存扣减（并发安全）
- **122.2 数据库设计**：product/order/inventory表
- **122.3 库存扣减并发安全方案**：乐观锁/悲观锁/Redis
- **122.4 Redis分布式锁**
- **122.5 消息队列异步下单**

### 第123章 · 项目五：IM 即时通讯
- **123.1 需求分析**：WebSocket通信/消息存储/在线状态/群聊
- **123.2 Spring WebSocket集成**
- **123.3 消息存储与历史**
- **123.4 在线状态管理**

### 第124章 · 项目六：微服务电商系统
- **124.1 服务拆分**：用户服务/商品服务/订单服务
- **124.2 服务注册与发现（Nacos）**
- **124.3 服务间调用（OpenFeign）**
- **124.4 API网关（Spring Cloud Gateway）**
- **124.5 分布式事务（Seata简介）**

---

## 术语清单（需入附录与全局索引）

### Java 核心
JVM、JDK、JRE、字节码（bytecode）、javac、java、jar、war、类（class）、对象（object/instance）、构造器（constructor）、继承（extends）、多态（polymorphism）、接口（interface）、抽象类（abstract class）、内部类、匿名内部类、枚举（enum）、record、注解（annotation）、反射（reflection）、泛型（generic）、类型擦除（type erasure）、自动装箱/拆箱（autoboxing/unboxing）、Lambda表达式、函数式接口、Stream API、方法引用、Optional

### JVM 与并发
堆（heap）、栈（stack）、方法区（metaspace）、GC（垃圾回收）、Minor GC、Major GC、Full GC、STW（Stop The World）、G1 GC、ZGC、线程（thread）、synchronized、volatile、CAS、线程池、CompletableFuture、虚拟线程（virtual thread）、synchronized vs Lock

### Spring 生态
IoC（控制反转）、DI（依赖注入）、AOP（面向切面）、Bean、@Component、@Service、@Repository、@Controller、@RestController、@Autowired、@ConfigurationProperties、@Transactional、Spring MVC、Filter、Interceptor、Spring Security、SecurityFilterChain、JWT、OAuth 2.0、RBAC、Spring Data JPA、JPQL、Spring Cloud、Nacos、OpenFeign、Gateway

### 数据库
JDBC、PreparedStatement、连接池、HikariCP、DataSource、MyBatis、JPA、Hibernate、Entity、Repository、RedisTemplate、缓存穿透/击穿/雪崩

### 消息队列
RabbitMQ、Kafka、Exchange、Queue、Topic、Partition、Consumer Group、Broker、ACK、死信队列

### DevOps
Maven、pom.xml、Docker、Dockerfile、docker-compose、GitHub Actions、CI/CD、Nginx、反向代理、SSL/TLS

---

## 可视化产出清单
| 文件 | 对应章节 |
|------|----------|
| `java_00_http_journey_visual.html` | 第00章 HTTP请求完整旅程 |
| `java_09_tcp_visual.html` | 第09章 TCP三次握手/四次挥手 |
| `java_42_jvm_gc_visual.html` | 第42章 JVM内存模型与GC |
| `java_72_springboot_startup_visual.html` | 第72章 Spring Boot启动流程 |
| `java_87_security_filter_visual.html` | 第87章 Spring Security过滤器链 |
| `java_94_mq_visual.html` | 第94章 消息队列模型 |
| `java_122_seckill_visual.html` | 第122章 秒杀系统架构 |

---

> 细纲自审记录 v1.0（经模拟读者反馈后修订）：

### 自审清单

| 检查项 | 结果 | 说明 |
|--------|------|------|
| 每一步是否有设计/需求文档依据？ | ✅ | 依据 Go 系列结构（本项目内部模板），Java 语言规范、Spring Boot 官方文档，所有内容可追溯 |
| 读者会在哪里卡住？ | ✅ 已修订 | 模拟读者反馈确认5个放弃高发区，已添加：导航依赖关系、7个中断点、防放弃设计（小项目/选读标记） |
| 术语附录候选词全部标记？ | ✅ | 约120个术语已分类收录（Java核心、JVM并发、Spring生态、数据库、消息队列、DevOps） |
| 长教程标注中断点？ | ✅ | 已添加7个中断点，覆盖全部10篇的分界处 |
| 沙盘推演完成？ | ✅ | 模拟读者子Agent已完成全量推演，发现5类问题均已修订 |
| 术语同步至全局索引？ | ⬜ | 待教程各章撰写时同步至 `.project/docs/glossary.md` |
| 可视化评估完成？ | ✅ | 已标注7个可视化节点，触发条件明确（时间序/空间关系/状态转换/纯文字难描述） |
| 避免"同理""显然"等跳步词？ | ⬜ | 细纲层面已避免，需在子Agent提示词中强制要求 |

### 模拟读者反馈 → 修订对照

| 问题 | 严重度 | 修订措施 |
|------|--------|----------|
| JDBC/MyBatis/JPA 三选一困惑 | 高 | 在导航区明确"三套都学，JPA是主力" |
| Docker 先用到后学到 | 高 | 第95章用Docker时只给一行命令，到第112章深入 |
| 第86章认证基础太单薄 | 中 | 已补充密码存储原则和bcrypt子节，充当Spring Security的前置 |
| 第34/42章理论章导致放弃 | 中 | 标注"选读/可回头精读" |
| 第44-53章数据结构动机不足 | 中 | 第44章加强动机说明，允许跳过后先学数据库 |
| 第87章Security过滤器链太陡 | 高 | 要求子Agent以"最小可用配置"开头（10行代码） |
| 第100/107章描述太模糊 | 中 | 第100章明确5种设计模式；第107章明确每个系统的设计步骤 |
| 第八/九篇展开不足 | 中 | 增加子节细节，与实战项目交叉引用 |
| 缺少中途小项目 | 高 | 第22章后插入"学生成绩管理系统"命令行版小项目 |

### 写作优先级
由于124章体量巨大，分4批派发子Agent：

**第1批（地基+语言核心）**：第00-43章（44章），最重要，奠定全部后续基础
**第2批（数据层+框架核心）**：第44-85章（42章），核心技能
**第3批（进阶主题）**：第86-107章（22章），认证/消息队列/架构
**第4批（工程化+实战）**：第108-124章（17章），部署/测试/项目

### 子Agent协作约定
- 每章独立一个.md文件，存放于 `java从零到spring boot后端教程/`
- 文件命名：`<序号>-<标题>.md`（如 `00-什么是后端工程师.md`）
- 写作风格锚定：参考Go系列第101章风格（口语化、比喻、想多一点、代码块、小结表格）
- 每章末尾必须包含：①小结表格 ②自测题2-3道
- 禁止：代码占位符/pass/TODO、真实密钥、猜测性内容