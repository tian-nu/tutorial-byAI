# 后端工程师完全指南 — 细纲

> 主线语言：Go | 详细程度：极致详细

---

## 第零篇：地基 — 计算机与网络基础

---

### 第0章 · 开篇：什么是后端工程师

#### 0.1 用餐厅比喻讲清楚前后端
- 你走进一家餐厅：
  - 服务员（前端）：给你菜单、记录你的点菜、把菜端给你、收钱
  - 厨房（后端）：收到订单、洗菜切菜、炒菜、装盘、出菜
  - 仓库（数据库）：存放食材的地方
- 对应到互联网：
  - 浏览器/App = 服务员
  - 服务器 = 厨房
  - 数据库 = 仓库

#### 0.2 一个HTTP请求的完整旅程
- 你在浏览器输入 `www.example.com/login` 按下回车
- 第1步：浏览器查DNS → 把域名翻译成IP地址
- 第2步：浏览器发起TCP连接 → 三次握手
- 第3步：浏览器发送HTTP请求 → GET /login HTTP/1.1
- 第4步：Nginx收到请求 → 转发给Go应用
- 第5步：Go应用解析请求 → 路由匹配 → 调用处理函数
- 第6步：处理函数查数据库 → 返回数据
- 第7步：Go应用组装响应 → 返回JSON
- 第8步：浏览器收到响应 → 渲染页面
- 用一张流程图串起来

#### 0.3 后端工程师的日常真实工作
- 写接口（API）：定义"别人怎么调用我的服务"
- 设计数据库表：定义"数据怎么存"
- 写业务逻辑：定义"数据怎么处理"
- 修Bug：找出为什么返回了错误的数据
- Code Review：检查同事的代码
- 上线部署：把代码推到服务器上
- 排查线上问题：用户报错了，你去看日志
- 技术方案设计：新功能怎么做

#### 0.4 本书学习路线图全景
- 用一张路线图展示从第0章到第115章的学习路径
- 标注"新手区"→"进阶区"→"高手区"
- 说明每一篇学完能做什么

---

### 第1章 · 计算机的大脑——CPU

#### 1.1 什么是CPU
- 比喻：CPU是计算机的"大脑"，负责思考和计算
- CPU的本质：一块能执行指令的芯片
- 指令是什么：加法、减法、比较、跳转... 这些最基础的操作
- 一切复杂的程序最终都变成这些简单指令

#### 1.2 机器语言、汇编语言、高级语言
- 机器语言：一串0和1，CPU直接能读懂的
- 汇编语言：给0和1起了人类能读的名字（MOV, ADD, JMP）
- 高级语言：Go、Python、Java 这些你写的东西
- 编译的过程：高级语言 → 汇编语言 → 机器语言
- 用 Go 的 `go build` 来举例

#### 1.3 时钟频率是什么
- 时钟频率 = CPU的心跳速度
- 单位：Hz（赫兹），1Hz = 每秒一次
- 现在CPU都是GHz级别，1GHz = 每秒10亿次
- 为什么不是频率越高越好：功耗、发热
- 比喻：不是心跳越快干活越快，还要看每次跳能干多少事

#### 1.4 核心数是什么
- 单核 vs 多核
- 比喻：一个厨师 vs 多个厨师
- 多核的好处：真的在同时做多件事（并行）
- 超线程是什么：一个厨师装成两个人（略有提升但不是翻倍）

#### 1.5 CPU缓存（L1/L2/L3）
- 为什么需要缓存：CPU太快，内存跟不上
- L1缓存：最小最快，离CPU最近
- L2缓存：稍大稍慢
- L3缓存：更大更慢，多核共享
- 比喻：你桌上的书（L1）、书架（L2）、楼下书店（L3）、网购（内存）

#### 1.6 32位和64位
- "位"指的是CPU一次能处理的数据宽度
- 32位CPU最多访问4GB内存（2³²）
- 64位CPU理论可以访问 2⁶⁴ 内存
- 影响：Go编译时选 GOARCH=amd64 还是 GOARCH=386

---

### 第2章 · 计算机的记忆——内存（RAM）

#### 2.1 内存是什么
- 比喻：内存是你的"临时工作台"
- 特点：快、贵、断电就没了（易失性）
- 为什么需要内存：如果所有数据都从硬盘读，电脑会慢1000倍

#### 2.2 内存地址
- 内存像一个巨大的格子仓库
- 每个格子有一个编号 = 地址
- 比如地址 0x7fff1234 里存着一个数字
- Go里的指针本质就是存这个地址

#### 2.3 栈（Stack）和堆（Heap）
- 比喻：栈是便利贴（自动管理），堆是储物间（手动管理）
- 栈：函数调用时分配，函数返回时自动回收
  - 存局部变量、函数参数
  - 速度快，空间小
  - LIFO（后进先出）
- 堆：手动（或GC）管理的内存区域
  - 存大对象、动态分配的数据
  - 速度慢，空间大
  - Go的逃逸分析会自动判断变量该放栈还是堆
- Go里怎么看逃逸分析：`go build -gcflags="-m"`

#### 2.4 内存泄漏是什么
- 比喻：你借了储物间的空间，但你忘了还
- 程序申请了内存，但不再使用了，却没释放
- Go有GC（垃圾回收），但不是万能的
  - 比如：一个Map一直往里面加数据但从不删除
  - 比如：Goroutine一直阻塞，相关的内存无法回收
- 检测内存泄漏：pprof工具

---

### 第3章 · 计算机的仓库——硬盘

#### 3.1 硬盘和内存的区别
- 内存：快、贵、断电消失 → 存正在用着的数据
- 硬盘：慢、便宜、断电保留 → 存需要长久保存的数据
- 比喻：内存是餐桌、硬盘是冰箱

#### 3.2 HDD和SSD
- HDD（机械硬盘）：有物理转盘和磁头
  - 优点：便宜、容量大
  - 缺点：慢、怕震动
- SSD（固态硬盘）：纯电子芯片
  - 优点：快得多、不怕震动
  - 缺点：贵、写入次数有限
- 为什么数据库服务器都用SSD

#### 3.3 文件是什么
- 文件 = 硬盘上一段连续的（或分散的）数据
- 文件系统 = 管理文件的规则（就像图书馆的管理系统）
- 常见文件系统：NTFS（Windows）、ext4（Linux）、APFS（Mac）
- 路径：从根目录出发找到文件的路线图
  - 绝对路径：`/home/user/hello.go`
  - 相对路径：`./hello.go`

#### 3.4 磁盘IO为什么慢
- 每次读硬盘 = 物理动作（机械硬盘要转、磁头要移动）
- 延迟对比（数量级感受）：
  - CPU执行一条指令：~1纳秒
  - 从L1缓存读：~1纳秒
  - 从内存读：~100纳秒
  - 从SSD读：~100微秒
  - 从HDD读：~10毫秒
- 这就是为什么我们要用缓存（Redis）和内存数据库

---

### 第4章 · 操作系统是什么

#### 4.1 操作系统的作用
- 比喻：操作系统是"翻译官 + 管家"
- 翻译官：把程序的请求翻译成硬件能懂的命令
- 管家：管理CPU、内存、硬盘、网络，不让程序互相打架
- 常见操作系统：Windows、Linux、macOS

#### 4.2 进程：一个正在运行的程序
- 进程 = 程序 + 运行时资源（内存、文件、CPU时间）
- 你双击一个程序 = 操作系统创建一个进程
- 进程之间是隔离的，一个进程崩溃不会影响其他
- 每个进程有自己的PID（进程ID）
- Linux命令：`ps aux` 查看所有进程

#### 4.3 线程：进程里的"工人"
- 一个进程至少有一个线程（主线程）
- 线程共享进程的内存空间
- 比喻：进程是一个公司，线程是公司里的员工
- 多线程的好处：能同时做多件事
- Go的Goroutine就是一种更轻量的"线程"

#### 4.4 并发（Concurrency）vs 并行（Parallelism）
- 并发：一个人同时处理多件事（来回切换，看起来像同时）
- 并行：多个人每人处理一件事（真正的物理同时）
- 烧水泡面比喻：
  - 并发：你一个人，先烧水，烧水的时候泡面，最后关火
  - 并行：你和室友，你烧水他泡面
- Go里：
  - 并发：多个Goroutine在一个CPU核上轮流执行
  - 并行：多个Goroutine在多个CPU核上真正同时执行

---

### 第5章 · 终端与命令行入门

#### 5.1 终端是什么
- 比喻：终端是你和操作系统"打字聊天"的窗口
- GUI（图形界面）vs CLI（命令行界面）
- 为什么后端工程师必须会命令行：
  - 服务器没有图形界面
  - 命令行效率更高
  - 自动化脚本需要命令行

#### 5.2 基础命令（每个都演示）
- `pwd` —— 显示当前所在的目录
- `ls` —— 列出当前目录的文件
  - `ls -l` 详细信息
  - `ls -a` 显示隐藏文件
  - `ls -la` 两者结合
- `cd` —— 切换目录
  - `cd /` 去根目录
  - `cd ~` 去家目录
  - `cd ..` 去上一级
  - `cd -` 回上一个目录
- `mkdir` —— 创建目录
- `touch` —— 创建空文件
- `rm` —— 删除
  - `rm file` 删文件
  - `rm -r dir` 删目录
  - `rm -rf dir` 强制删（危险！）
- `cp` —— 复制
- `mv` —— 移动/重命名
- `cat` —— 查看文件内容
- `less` —— 分页查看大文件
- `head` / `tail` —— 查看文件头/尾
  - `tail -f` 实时追踪（看日志神器）
- `grep` —— 搜索文本
- `find` —— 搜索文件
- `管道（|）` —— 把前一个命令的输出传给后一个

#### 5.3 环境变量
- 环境变量是什么：操作系统级的"全局变量"
- `PATH`：命令行去哪找可执行程序
- 查看环境变量：`echo $PATH`（Linux/Mac）或 `echo %PATH%`（Windows）
- Go相关的环境变量：GOROOT、GOPATH、GOBIN
- 设置环境变量的区别（临时 vs 永久）

---

### 第6章 · IP地址

#### 6.1 IP地址是门牌号
- 比喻：IP地址 = 互联网上每台设备的门牌号
- 没有IP地址，数据不知道发给谁
- IP地址的格式：`192.168.1.1`（四个0~255的数字）

#### 6.2 IPv4 vs IPv6
- IPv4：`192.168.1.1`，32位，约43亿个地址 → 不够用了
- IPv6：`2001:0db8:85a3:0000:0000:8a2e:0370:7334`，128位 → 几乎无限
- 为什么IPv6还没完全普及：兼容性、成本

#### 6.3 公网IP vs 内网IP
- 公网IP：全球唯一，能在互联网上直接找到你
- 内网IP：只在局域网内有效
  - `10.x.x.x`
  - `172.16.x.x ~ 172.31.x.x`
  - `192.168.x.x`
- NAT（网络地址转换）：路由器帮你把内网IP翻译成公网IP
- 比喻：公网IP = 小区地址，内网IP = 房间号

#### 6.4 localhost和127.0.0.1
- `127.0.0.1` = "我自己"
- `localhost` = `127.0.0.1` 的域名
- 访问`localhost`就相当于跟自己说话
- 为什么开发时用localhost：不需要网络，速度快，安全

#### 6.5 子网掩码
- 子网掩码用来判断两个IP在不在同一个局域网
- `255.255.255.0` = 前三个数字相同的IP在同一个网络
- CIDR表示法：`192.168.1.0/24`

---

### 第7章 · 域名与DNS

#### 7.1 域名是什么
- 比喻：域名 = 电话号码簿里的名字，IP = 电话号码
- 你记住 `www.baidu.com` 比记住 `110.242.68.66` 容易多了
- 域名的结构：`www.baidu.com`
  - `.com` = 顶级域名
  - `baidu` = 二级域名
  - `www` = 子域名

#### 7.2 DNS查询的完整过程
- 你在浏览器输入 `www.baidu.com` → 然后发生了什么
- 第1步：浏览器自己有没有缓存？有就直接用
- 第2步：操作系统有没有缓存？（hosts文件）
- 第3步：问本地DNS服务器（你家的路由器或运营商的DNS）
- 第4步：本地DNS不知道 → 问根DNS服务器（.）
- 第5步：根DNS说 → 去问 `.com` 的DNS
- 第6步：`.com` DNS 说 → 去问 `baidu.com` 的DNS
- 第7步：`baidu.com` DNS 说 → `www.baidu.com` 的IP是 `110.242.68.66`
- 第8步：本地DNS把结果缓存起来（TTL时间内不再问）
- 第9步：浏览器拿到IP，开始连接
- 用一张流程图串起来

#### 7.3 hosts文件
- hosts文件 = 你电脑上的私人DNS
- 位置：Linux `/etc/hosts`、Windows `C:\Windows\System32\drivers\etc\hosts`
- 作用：
  - 本地开发时把域名指向127.0.0.1
  - 可以屏蔽广告网站
- 例子：`127.0.0.1 myapp.local`

#### 7.4 DNS记录类型
- A记录：域名 → IPv4
- AAAA记录：域名 → IPv6
- CNAME记录：域名 → 另一个域名（别名）
- MX记录：邮件服务器
- NS记录：指定DNS服务器
- TXT记录：放任意文本（常用来验证域名所有权）

---

### 第8章 · 端口

#### 8.1 端口是什么
- 比喻：IP = 小区地址，端口 = 房间号
- 一台服务器只有一个IP，但可以跑N个服务
- 每个服务监听不同的端口，数据就不会送错
- 端口范围：0~65535（0~1023是系统保留的）

#### 8.2 常见端口
- `80`：HTTP（默认网页访问端口）
- `443`：HTTPS（加密的网页访问）
- `22`：SSH（远程登录服务器）
- `3306`：MySQL数据库
- `5432`：PostgreSQL数据库
- `6379`：Redis
- `27017`：MongoDB
- `8080`：开发时常用的HTTP测试端口

#### 8.3 一个服务器能跑多少个服务
- 理论上65535个（端口数量限制）
- 实际上受限于内存和CPU
- 每个端口只能被一个程序监听
- 但一个程序可以监听多个端口
- 为什么Go程序启动时能指定端口：`r.Run(":8080")`

---

### 第9章 · TCP协议

#### 9.1 TCP是什么
- 比喻：TCP是一个"可靠的快递员"
- 它保证：
  - 数据包不丢失
  - 数据包不乱序
  - 数据包不重复
  - 数据包不出错
- 代价：比UDP慢，有额外开销（握手、确认）

#### 9.2 三次握手：建立连接
- 比喻：打电话的过程
  - A："喂，听得到吗？"（SYN）
  - B："听得到，你呢？"（SYN + ACK）
  - A："我也听得到，开始聊吧"（ACK）
- 每次握手发什么数据包
- 为什么是三次不是两次（防止旧连接请求造成混乱）
- 用Wireshark抓包展示

#### 9.3 四次挥手：断开连接
- 比喻：挂电话的过程
  - A："我说完了，挂了啊"（FIN）
  - B："好的，知道了"（ACK）
  - B："我也说完了，我也挂了"（FIN）
  - A："OK，拜拜"（ACK）
- 为什么是四次不是三次（因为TCP是全双工的，双方都要关闭）
- TIME_WAIT状态：主动关闭的一方要等2MSL（确保最后的ACK到达）

#### 9.4 TCP如何保证可靠性
- 序号和确认号：每个字节都有编号
- 超时重传：发了数据没收到确认，就重发
- 流量控制：接收方说"我处理不过来，你慢点发"
- 拥塞控制：网络堵了就减速
- 校验和：检测数据是否损坏

---

### 第10章 · UDP协议

#### 10.1 UDP是什么
- 比喻：UDP是"只管发不管到的快递"
- 没有连接、没有确认、没有重传
- 优点：快、简单、开销小
- 缺点：不可靠、不保证顺序

#### 10.2 UDP vs TCP 对比
| 特性 | TCP | UDP |
|------|-----|-----|
| 连接 | 需要建立连接 | 无连接 |
| 可靠性 | 可靠 | 不可靠 |
| 顺序 | 保证 | 不保证 |
| 速度 | 较慢 | 快 |
| 开销 | 大（20字节头） | 小（8字节头） |
| 场景 | 网页、文件传输、邮件 | 视频直播、语音通话、游戏 |

#### 10.3 UDP使用场景
- 视频直播：丢几帧没关系，重要的是不卡
- 语音通话：延迟比丢包更致命
- 在线游戏：位置信息频繁更新，丢一个无所谓
- DNS查询：一个请求一个响应，简单高效
- DHCP：获取IP地址

---

### 第11章 · HTTP协议（一）

#### 11.1 HTTP是什么
- 全称：HyperText Transfer Protocol（超文本传输协议）
- 比喻：HTTP是浏览器和服务器之间的"沟通语言"
- 版本：HTTP/1.0 → HTTP/1.1 → HTTP/2 → HTTP/3（QUIC）

#### 11.2 URL的结构
- 完整URL：`https://www.example.com:443/path/to/page?key=value#section`
- 拆解：
  - `https://`：协议（scheme）
  - `www.example.com`：主机名（host）
  - `:443`：端口（port）
  - `/path/to/page`：路径（path）
  - `?key=value`：查询参数（query string）
  - `#section`：锚点（fragment）
- 编码：URL里不能有中文和空格，需要编码（URL Encode）

#### 11.3 请求方法
- `GET`：获取数据（查）—— 像去图书馆借书
- `POST`：创建数据（增）—— 像填表交材料
- `PUT`：更新数据（改，全量替换）—— 像换一本新书
- `PATCH`：更新数据（改，部分更新）—— 像只改书的某一页
- `DELETE`：删除数据（删）—— 像把书扔掉
- `HEAD`：只拿响应头，不要响应体
- `OPTIONS`：问服务器支持哪些方法
- GET和POST的区别（面试必问）：
  - GET参数在URL里，POST在请求体里
  - GET有长度限制（浏览器限制），POST理论上没有
  - GET是幂等的（多次请求结果一样），POST不是
  - GET可以被缓存，POST不可以
  - GET可以被收藏为书签，POST不行

#### 11.4 请求头和请求体
- 请求头（Headers）：元数据，描述这次请求
  - `Host`：目标主机
  - `User-Agent`：我是什么浏览器
  - `Content-Type`：我发的数据是什么格式
  - `Content-Length`：数据有多长
  - `Authorization`：我的身份凭证
  - `Cookie`：我存的Cookie
  - `Accept`：我接受什么格式的响应
- 请求体（Body）：真正要传的数据
  - GET请求通常没有Body
  - POST/PUT请求通常在Body里放JSON、表单数据等

#### 11.5 状态码
- `1xx`：信息（很少见到）
- `2xx`：成功
  - `200 OK`：成功了
  - `201 Created`：创建成功
  - `204 No Content`：成功但没返回内容
- `3xx`：重定向
  - `301 Moved Permanently`：永久搬家（SEO权重转移）
  - `302 Found`：临时搬家
  - `304 Not Modified`：内容没变，用缓存
- `4xx`：客户端错误（你的问题）
  - `400 Bad Request`：你的请求格式不对
  - `401 Unauthorized`：你没登录
  - `403 Forbidden`：你登录了但没权限
  - `404 Not Found`：你要的东西不存在
  - `405 Method Not Allowed`：方法用错了（比如用GET去创建数据）
  - `429 Too Many Requests`：你请求太多了，被限流
- `5xx`：服务端错误（我的问题）
  - `500 Internal Server Error`：服务器代码崩了
  - `502 Bad Gateway`：网关/代理收到了无效响应
  - `503 Service Unavailable`：服务器暂时不能处理（可能过载或维护）
  - `504 Gateway Timeout`：网关超时

---

### 第12章 · HTTP协议（二）深入细节

#### 12.1 Cookie是什么
- 比喻：Cookie就像超市给的会员卡
- 你第一次去超市（访问网站），店员给你一张会员卡（Set-Cookie）
- 下次你再去，带着会员卡（Cookie请求头），店员就知道你是谁
- Cookie的属性：
  - `Name=Value`：卡号和名字
  - `Domain`：这张卡在哪些超市能用
  - `Path`：在超市的哪些区域能用
  - `Expires/Max-Age`：有效期，过了就作废
  - `HttpOnly`：这张卡只能给收银员看，不能被JS代码偷看（防XSS）
  - `Secure`：只在HTTPS下传输
  - `SameSite`：防止CSRF攻击

#### 12.2 Session是什么
- 比喻：Session是超市后台的"会员档案"
- Cookie只存一个Session ID（会员卡号）
- 真正的数据（你的积分、余额）存在服务器端
- 流程：
  - 你登录 → 服务器创建Session → 返回Session ID给浏览器（存Cookie）
  - 你下次请求 → 浏览器带Cookie里的Session ID → 服务器查Session → 认出你

#### 12.3 HTTP缓存
- 为什么需要缓存：同样的数据别反复下载
- 强缓存（直接拿本地，不问服务器）：
  - `Cache-Control: max-age=3600`（这数据1小时内有效）
  - `Expires: Thu, 31 Dec 2025 23:59:59 GMT`（在这之前都有效）
- 协商缓存（问一下服务器能不能用本地）：
  - `ETag` / `If-None-Match`：给资源一个版本号，变了才重新下载
  - `Last-Modified` / `If-Modified-Since`：看资源的修改时间

#### 12.4 CORS跨域
- 同源策略：浏览器不允许 `a.com` 的JS请求 `b.com` 的接口
- 为什么：安全！防止恶意网站偷你的数据
- 源 = 协议 + 域名 + 端口，三者相同才是同源
- CORS就是服务端说"我允许这些网站跨域访问我"
  - `Access-Control-Allow-Origin`：允许哪些源
  - `Access-Control-Allow-Methods`：允许哪些方法
  - `Access-Control-Allow-Headers`：允许哪些请求头
- 预检请求（Preflight）：复杂请求前先发一个OPTIONS探路

---

### 第13章 · HTTPS

#### 13.1 为什么需要HTTPS
- HTTP的三大问题：
  - 明文传输 → 谁都能偷看（中间人攻击）
  - 没有身份验证 → 你以为在跟百度聊天，其实是个假网站
  - 数据可能被篡改 → 运营商给你插广告
- HTTPS = HTTP + TLS/SSL

#### 13.2 对称加密
- 比喻：你和朋友共用一把钥匙，用这把钥匙锁箱子、开箱子
- 优点：快
- 缺点：怎么安全地把钥匙交给对方？（钥匙传输过程中可能被偷）

#### 13.3 非对称加密
- 比喻：你有一把锁和一把钥匙（公钥和私钥）
- 公钥（锁）：公开发给所有人，谁都能拿它锁箱子
- 私钥（钥匙）：只有你有，只有你能打开被你的锁锁住的箱子
- 优点：安全，不用传递私钥
- 缺点：慢（比对称加密慢100~1000倍）

#### 13.4 TLS握手过程（HTTPS的核心）
- 第1步：客户端说"你好，我支持这些加密算法"（Client Hello）
- 第2步：服务器说"你好，我们就用这个算法，这是我的证书"（Server Hello + 证书）
- 第3步：客户端验证证书（是不是真的、有没有过期）
- 第4步：客户端生成一个随机数，用服务器的公钥加密发过去
- 第5步：双方用这个随机数生成"会话密钥"（对称加密的钥匙）
- 第6步：后续通信都用这个会话密钥（对称加密，快！）
- 精妙之处：非对称加密只用来传递"会话密钥"，后面的海量数据用对称加密

#### 13.5 数字证书和CA
- 证书是什么：证明"这个公钥真的是百度的"
- CA（Certificate Authority，证书颁发机构）：你信任的第三方
- 证书链：根CA → 中间CA → 你的证书
- 为什么会信任：操作系统和浏览器内置了根CA的公钥
- 自签名证书：你自己给自己发证书（浏览器不信任，会报警告）

---

### 第14章 · WebSocket

#### 14.1 HTTP的局限性
- HTTP是一问一答：你问一句，我答一句，结束
- 如果服务器有新消息，无法主动推送给客户端
- 怎么办：
  - 轮询（Polling）：客户端每隔几秒问一次"有新消息吗？"（浪费资源）
  - 长轮询（Long Polling）：客户端问，服务器hold住，有消息才回答（还是别扭）
  - WebSocket：建立持久连接，双方随时可以发消息

#### 14.2 WebSocket是什么
- 比喻：HTTP是写信，WebSocket是打电话
- WebSocket是HTML5标准
- 特点：
  - 全双工：双方都能同时收发
  - 持久连接：建立一次，一直用
  - 轻量级：数据帧头部只有2~14字节（HTTP头部动不动几百字节）

#### 14.3 WebSocket握手
- WebSocket连接从HTTP升级而来
- 客户端发一个特殊的HTTP请求（带Upgrade头）
- 服务器同意 → 返回101 Switching Protocols
- 协议升级完成 → 从HTTP变成WebSocket
- 用Go演示握手过程

#### 14.4 WebSocket使用场景
- 在线聊天（微信网页版）
- 实时推送（股票行情、体育比分）
- 多人协作（Google Docs）
- 在线游戏
- 物联网设备通信

---

## 第一篇：Go语言从入门到精通

---

### 第15章 · Go语言介绍与环境搭建

#### 15.1 Go的诞生故事
- 2007年，Google三位大佬（Robert Griesemer, Rob Pike, Ken Thompson）受够了C++的编译速度
- 2009年Go正式开源发布
- 设计哲学：
  - 简洁：只有25个关键字（Java有50+，C++有90+）
  - 高效：编译快，运行快
  - 并发：Goroutine是杀手锏

#### 15.2 安装Go
- 去 golang.org 下载对应操作系统的安装包
- Windows：双击安装，一路Next
- Mac：brew install go
- Linux：下载tar.gz解压到 /usr/local
- 验证安装：`go version`

#### 15.3 GOROOT和GOPATH
- GOROOT：Go的安装目录（编译器、标准库在这里）
- GOPATH：你的工作目录（你的代码、下载的第三方包在这里）
  - 结构：`GOPATH/src/` 放源码，`GOPATH/bin/` 放编译好的可执行文件
- Go 1.11之后有了Go Modules，GOPATH不再是必须放在特定位置了
- 但GOROOT还是要正确配置

#### 15.4 第一个程序：Hello World
```go
package main

import "fmt"

func main() {
    fmt.Println("Hello, World!")
}
```
- 逐行解释每一行是什么意思
- `package main`：这是一个可执行程序（不是库）
- `import "fmt"`：引用了格式化输出包
- `func main()`：程序的入口函数（所有Go程序的起点）
- `fmt.Println()`：打印一行，自动加换行

#### 15.5 go run、go build、go install
- `go run hello.go`：编译并运行（不保留可执行文件）
- `go build hello.go`：编译成可执行文件
- `go build -o myapp hello.go`：指定输出文件名
- `go install`：编译并把可执行文件放到 `GOPATH/bin/`
- 三者区别和使用场景

#### 15.6 跨平台编译
- Go的强大特性：一个命令就能编译其他平台的可执行文件
- `GOOS=linux GOARCH=amd64 go build`：在Mac上编译Linux的程序
- `GOOS=windows GOARCH=amd64 go build`：在Mac上编译Windows的.exe

---

### 第16章 · Go程序的基本结构

#### 16.1 package
- Go程序由包（package）组成
- 每个`.go`文件第一行必须是`package xxx`
- 两种包：
  - `package main`：可执行程序
  - `package xxx`：库（给别人用的）
- 同一个目录下的所有`.go`文件必须属于同一个package

#### 16.2 import的写法
- 单行导入：
  ```go
  import "fmt"
  ```
- 分组导入（推荐）：
  ```go
  import (
      "fmt"
      "net/http"
  )
  ```
- 别名导入：
  ```go
  import myfmt "fmt"
  ```
- 点导入（不推荐，污染命名空间）：
  ```go
  import . "fmt"
  ```
- 匿名导入（只执行init函数）：
  ```go
  import _ "github.com/go-sql-driver/mysql"
  ```

#### 16.3 代码格式化：gofmt
- Go官方强制统一代码风格
- `gofmt -w file.go`：格式化文件
- `go fmt ./...`：格式化整个项目
- 大部分IDE保存时自动格式化
- 为什么要强制：减少无意义的风格争论，所有Go代码看起来一样

#### 16.4 注释
- 单行注释：`// 这是注释`
- 多行注释：`/* 这是注释 */`
- 文档注释：在函数/包/类型上面写注释，`go doc`可以提取

---

### 第17章 · 变量与常量

#### 17.1 变量的声明方式
- 方式一：`var name string = "张三"`
- 方式二：`var name = "张三"`（类型推断）
- 方式三：`name := "张三"`（短声明，只能在函数内用）
- 方式四：`var name string`（先声明后赋值，此时name是零值）
- 批量声明：
  ```go
  var (
      name   string = "张三"
      age    int    = 20
      gender bool
  )
  ```

#### 17.2 零值
- Go中所有变量声明后自动赋零值
- `int` → `0`
- `float64` → `0.0`
- `bool` → `false`
- `string` → `""`（空字符串，不是nil）
- `指针` → `nil`
- `切片/map/chan/接口` → `nil`
- 好处：没有未初始化的变量，更安全

#### 17.3 变量命名规范
- Go推荐驼峰命名：`userName`、`UserID`
- 大写开头 = 导出（公开）：`UserName`
- 小写开头 = 不导出（私有）：`userName`
- 缩写全大写或全小写：`userID`（不是`userId`）、`HTTPServer`

#### 17.4 常量
- 声明：`const Pi = 3.14159`
- 常量不能使用 `:=`
- 常量的值必须在编译时就确定
- 批量声明：
  ```go
  const (
      StatusOK    = 200
      StatusError = 500
  )
  ```

#### 17.5 iota：枚举神器
- iota是Go的枚举计数器
- 每个const块中从0开始递增
- 基本用法：
  ```go
  const (
      Monday = iota    // 0
      Tuesday          // 1
      Wednesday        // 2
  )
  ```
- 高级用法：
  ```go
  const (
      _  = iota        // 0（跳过）
      KB = 1 << (10 * iota)  // 1 << 10 = 1024
      MB                 // 1 << 20 = 1048576
      GB                 // 1 << 30
  )
  ```

---

### 第18章 · 基本数据类型

#### 18.1 bool：真和假
- 只有两个值：`true`、`false`
- Go的bool不能和int互转（不像C语言）
- 默认零值：`false`
- 逻辑运算：`&&`（与）、`||`（或）、`!`（非）

#### 18.2 整数类型全家福
- 有符号：`int`、`int8`、`int16`、`int32`、`int64`
- 无符号：`uint`、`uint8`、`uint16`、`uint32`、`uint64`
- `int`和`uint`的长度取决于操作系统（32位系统是32位，64位系统是64位）
- 取值范围计算（帮助理解）：
  - int8：-128 ~ 127（因为 2⁷=128，一半给负数一半给正数和零）
  - uint8：0 ~ 255
- `byte` = `uint8`（处理原始字节时用）
- `rune` = `int32`（处理Unicode字符时用）

#### 18.3 浮点数
- `float32`：约6位有效数字
- `float64`：约15位有效数字（默认推荐）
- 浮点数不能精确表示十进制小数（计算机是用二进制存小数）
- 例子：`0.1 + 0.2 != 0.3`（浮点数精度问题，所有语言都一样）

#### 18.4 字符串
- Go的字符串是UTF-8编码的字节序列
- 用双引号：`"Hello"`
- 用反引号（原始字符串，不转义）：`` `Hello\nWorld` ``（\n就是字面量）
- 字符串是不可变的！
- 获取长度：`len(str)` 返回字节数，不是字符数
- 遍历字符串的正确姿势：
  ```go
  for _, ch := range str {
      fmt.Printf("%c", ch)  // 按字符遍历
  }
  ```

#### 18.5 byte和rune的区别
- `byte`：一个字节，只能表示ASCII字符（英文字母数字符号）
- `rune`：一个Unicode码点，能表示任何字符（包括中文）
- 例子：
  ```go
  s := "你好"
  len(s)           // 6（UTF-8下每个中文字3字节）
  len([]rune(s))   // 2（两个字）
  ```

#### 18.6 类型转换
- Go必须显式类型转换，不会自动转换
- `int(x)`、`float64(x)`、`string(x)`
- 类型转换可能丢失精度：`int(3.14)` → `3`
- 整数转字符串的行为：`string(65)` → `"A"`（65是A的ASCII码）
- 正确的数字转字符串：`strconv.Itoa(65)` → `"65"`

---

### 第19章 · 运算符

#### 19.1 算术运算符
- `+` `-` `*` `/` `%`（取余）

#### 19.2 比较运算符
- `==` `!=` `<` `>` `<=` `>=`

#### 19.3 逻辑运算符
- `&&`（与）：两边都为true才为true
- `||`（或）：任一边为true就为true
- `!`（非）：取反
- 短路求值：`a && b`中如果a是false，b根本不会执行

#### 19.4 位运算符
- 什么情况下用：权限管理、标志位、底层优化
- `&`：按位与
- `|`：按位或
- `^`：按位异或
- `<<`：左移（乘以2的n次方）
- `>>`：右移（除以2的n次方）

#### 19.5 赋值运算符
- `=` `+=` `-=` `*=` `/=` `%=`

#### 19.6 运算符优先级
- 从高到低表
- 不确定的时候加括号最安全

---

### 第20章 · 控制流：if 和 switch

#### 20.1 if的基本写法
```go
if x > 0 {
    fmt.Println("正数")
}
```

#### 20.2 if带初始化语句
```go
if num := getNumber(); num > 0 {
    fmt.Println(num, "是正数")
} else if num < 0 {
    fmt.Println(num, "是负数")
} else {
    fmt.Println("是零")
}
// num只在if-else块内有效
```

#### 20.3 Go的if特点
- 条件不需要括号（`if x > 0` 而不是 `if (x > 0)`）
- 大括号必须有，不能省略
- 左大括号必须和if在同一行

#### 20.4 switch的基本写法
```go
switch day {
case "Monday":
    fmt.Println("周一")
case "Friday":
    fmt.Println("周五")
default:
    fmt.Println("其他")
}
```

#### 20.5 Go的switch特点（和Java/C++不同）
- 不需要break，默认不会穿透
- 如果想穿透（少见），用 `fallthrough`
- case 可以是多个值：`case "Monday", "Tuesday":`
- switch 后面可以没有表达式（相当于一连串if-else）：
  ```go
  switch {
  case score >= 90:
      grade = "A"
  case score >= 80:
      grade = "B"
  default:
      grade = "C"
  }
  ```

---

### 第21章 · for循环

#### 21.1 Go只有一种循环：for
- Go没有while、do-while，全靠for

#### 21.2 标准for循环
```go
for i := 0; i < 10; i++ {
    fmt.Println(i)
}
```

#### 21.3 while风格的for
```go
i := 0
for i < 10 {
    fmt.Println(i)
    i++
}
```

#### 21.4 死循环
```go
for {
    // 一直跑，直到break或return
}
```

#### 21.5 range：遍历神器
- 遍历切片/数组：`for i, v := range slice`
- 遍历Map：`for k, v := range map`
- 遍历字符串：`for i, ch := range str`（ch是rune，i是字节索引）
- 忽略索引：`for _, v := range slice`
- 忽略值：`for i := range slice`
- range返回的是副本，修改v不会影响原数据

#### 21.6 break和continue
- `break`：跳出整个循环
- `continue`：跳过本次循环，进入下一次
- `break label`：跳出指定标签的循环（多层循环时用）
```go
outer:
for i := 0; i < 3; i++ {
    for j := 0; j < 3; j++ {
        if i == 1 && j == 1 {
            break outer  // 跳出外层循环
        }
    }
}
```

---

### 第22章 · 数组

#### 22.1 数组的声明
- `var arr [5]int`：声明一个长度为5的int数组
- `arr := [5]int{1, 2, 3, 4, 5}`：声明并初始化
- `arr := [...]int{1, 2, 3}`：让编译器推断长度

#### 22.2 数组是值类型
- 这一点和大多数语言不同！
- 数组赋值会复制整个数组，不是引用
- 传数组给函数会复制一整份（大数组很浪费）
- 所以实际开发中基本不用数组，用切片

#### 22.3 多维数组
```go
matrix := [3][3]int{
    {1, 2, 3},
    {4, 5, 6},
    {7, 8, 9},
}
```

#### 22.4 数组的局限性
- 长度是类型的一部分：`[3]int`和`[5]int`是不同的类型
- 不能动态改变大小
- 这就是为什么Go设计了切片（Slice）

---

### 第23章 · 切片（Slice）

#### 23.1 什么是切片
- 比喻：数组是一整块地，切片是一扇能看到这块地的窗户
- 切片是数组的"视图"，它不存数据，它指向一个底层数组
- 切片可以动态增长

#### 23.2 切片的底层结构
```go
type slice struct {
    ptr   unsafe.Pointer  // 指向底层数组的指针
    len   int              // 当前长度（窗户能看到多少）
    cap   int              // 容量（从窗户位置往后还有多少空间）
}
```
- 用图解释len和cap的区别

#### 23.3 创建切片的多种方式
- 方式一：从数组创建
  ```go
  arr := [5]int{1, 2, 3, 4, 5}
  s := arr[1:4]  // [2, 3, 4]，len=3，cap=4（从索引1到底）
  ```
- 方式二：字面量
  ```go
  s := []int{1, 2, 3}
  ```
- 方式三：make
  ```go
  s := make([]int, 3, 5)  // len=3, cap=5
  ```
- 方式四：nil切片
  ```go
  var s []int  // nil，len=0, cap=0
  ```

#### 23.4 append
- `s = append(s, 4, 5, 6)`：追加元素
- append的返回值一定要接住（因为可能返回新的底层数组）
- 追加另一个切片：`s = append(s, other...)`（三个点展开）

#### 23.5 切片的扩容机制
- 当append时len超过cap，Go会创建一个更大的底层数组
- 扩容策略（Go 1.18+）：
  - 如果新容量 > 旧容量 * 2，直接扩容到新容量
  - 否则，旧容量 < 256 时翻倍，旧容量 >= 256 时增长约1.25倍
- 扩容后，原来的底层数组可能被垃圾回收

#### 23.6 切片陷阱：共享底层数组
- 多个切片可能共享同一个底层数组
- 修改一个切片可能影响另一个
- 示例：
  ```go
  a := []int{1, 2, 3}
  b := a[0:2]
  b[0] = 100  // a也变了！a = [100, 2, 3]
  ```
- 如何避免：用copy
  ```go
  b := make([]int, len(a))
  copy(b, a)
  ```

#### 23.7 copy函数
- `copy(dst, src)`：把src的元素复制到dst
- 返回复制的元素个数（取两个切片长度的最小值）

---

### 第24章 · Map

#### 24.1 Map的声明和初始化
- `var m map[string]int`：声明一个nil map（不能直接赋值，会panic）
- `m := make(map[string]int)`：创建空map
- `m := map[string]int{"a": 1, "b": 2}`：声明并初始化
- nil map vs 空map的区别：
  - nil map：不能赋值，可以读（返回零值），可以len
  - 空map：可以读可以写

#### 24.2 Map的基本操作
- 增/改：`m["key"] = value`
- 查：`v := m["key"]`（key不存在返回零值）
- 判断key是否存在：`v, ok := m["key"]`（ok是bool）
- 删：`delete(m, "key")`
- 长度：`len(m)`

#### 24.3 Map的遍历
```go
for key, value := range m {
    fmt.Println(key, value)
}
```
- 遍历顺序是随机的！（故意的，防止程序依赖遍历顺序）

#### 24.4 Map的底层原理
- Map底层是哈希表
- 存入过程：
  - key → 哈希函数 → 哈希值 → 对桶数量取模 → 确定放在哪个桶
- 哈希冲突：不同的key算出同一个桶编号怎么办
  - Go用链地址法：每个桶可以存8个键值对，满了就溢出桶
- 扩容：当装载因子太高或溢出桶太多时触发
  - 装载因子 = 元素数量 / 桶数量
  - 扩容时所有key要重新哈希（rehash），渐进式完成

#### 24.5 sync.Map
- 普通Map不是并发安全的
- 多个Goroutine同时读写普通Map会panic
- `sync.Map`是并发安全的
- sync.Map的使用场景：
  - 读多写少
  - 多个Goroutine读写不同的key

---

### 第25章 · 字符串深入

#### 25.1 字符串的底层结构
```go
type stringStruct struct {
    str unsafe.Pointer  // 指向底层字节数组
    len int              // 字符串的字节长度
}
```
- 字符串是不可变的！任何"修改"操作都是创建新字符串

#### 25.2 strings包常用函数
- `strings.Contains(s, substr)`：是否包含
- `strings.HasPrefix(s, prefix)`：是否以...开头
- `strings.HasSuffix(s, suffix)`：是否以...结尾
- `strings.Index(s, substr)`：子串位置
- `strings.Split(s, sep)`：分割
- `strings.Join(parts, sep)`：拼接
- `strings.Replace(s, old, new, n)`：替换（n=-1表示全部替换）
- `strings.TrimSpace(s)`：去首尾空白
- `strings.ToUpper(s)` / `strings.ToLower(s)`：大小写转换
- `strings.Builder`：高效拼接字符串

#### 25.3 strconv包
- `strconv.Itoa(123)`：int → string
- `strconv.Atoi("123")`：string → int
- `strconv.FormatInt(123, 10)`：int64 → string
- `strconv.ParseInt("123", 10, 64)`：string → int64
- `strconv.FormatFloat(3.14, 'f', 2, 64)`：float → string
- `strconv.ParseFloat("3.14", 64)`：string → float
- `strconv.FormatBool(true)`：bool → string
- `strconv.ParseBool("true")`：string → bool

#### 25.4 字符串拼接的效率
- 少量拼接：`+` 最方便
- 大量拼接（循环中）：用 `strings.Builder`
- 为什么Builder快：预分配内存，减少内存分配次数
- 性能对比：Builder > bytes.Buffer > fmt.Sprintf > `+`

---

### 第26章 · 函数（一）：基础

#### 26.1 函数的声明
```go
func 函数名(参数列表) 返回值类型 {
    // 函数体
}
```
- 例子：`func add(a int, b int) int { return a + b }`
- 参数类型相同可以简写：`func add(a, b int) int`

#### 26.2 参数传递：值传递
- Go只有值传递，没有引用传递
- 传基本类型：复制一份值
- 传切片/Map/Channel：复制一份"描述符"，底层数据共享
- 传指针：复制一份地址，指向同一份数据
- 面试考点：Go的函数传参到底是什么？

#### 26.3 多返回值（Go特色）
```go
func divide(a, b int) (int, error) {
    if b == 0 {
        return 0, errors.New("除数不能为零")
    }
    return a / b, nil
}
```
- 通常第二个返回值是error

#### 26.4 命名返回值
```go
func divide(a, b int) (result int, err error) {
    if b == 0 {
        err = errors.New("除数不能为零")
        return  // 裸返回，自动返回result和err
    }
    result = a / b
    return
}
```
- 好处：文档作用，一眼看出返回什么
- 坏处：裸return在长函数中可读性差

---

### 第27章 · 函数（二）：高级

#### 27.1 可变参数
```go
func sum(nums ...int) int {
    total := 0
    for _, n := range nums {
        total += n
    }
    return total
}
// 调用：sum(1, 2, 3, 4, 5)
```
- `...int`：可以传0个或多个int
- 在函数内部，nums就是一个`[]int`切片
- 把切片传给可变参数函数：`sum(slice...)`（三个点展开）

#### 27.2 匿名函数
```go
f := func(x, y int) int {
    return x + y
}
result := f(1, 2)  // 3
```
- 匿名函数可以立即执行：
  ```go
  result := func(x, y int) int {
      return x + y
  }(1, 2)
  ```

#### 27.3 闭包（重要！）
- 闭包 = 函数 + 它引用的外部变量
- 比喻：函数带着一个"背包"，背包里装着它需要的外部变量
```go
func counter() func() int {
    count := 0
    return func() int {
        count++  // 这个count是外部的，不会被回收
        return count
    }
}
c := counter()
c()  // 1
c()  // 2
c()  // 3
```
- 闭包的陷阱：
  ```go
  for i := 0; i < 3; i++ {
      go func() {
          fmt.Println(i)  // 打印的都是3！
      }()
  }
  // 正确做法：把i作为参数传进去
  for i := 0; i < 3; i++ {
      go func(n int) {
          fmt.Println(n)
      }(i)
  }
  ```

#### 27.4 defer关键字（非常重要！）
- defer：延迟执行，在函数返回前执行
- 执行顺序：后进先出（LIFO，像堆盘子）
```go
func example() {
    defer fmt.Println("1")
    defer fmt.Println("2")
    fmt.Println("3")
}
// 输出：3, 2, 1
```
- 典型用途：
  - 关闭文件
  - 释放锁
  - 捕获panic
- defer的参数在声明时就确定了：
  ```go
  func example() {
      i := 0
      defer fmt.Println(i)  // 此时i=0，已经确定
      i++
  }
  // 输出：0
  ```

#### 27.5 panic和recover
- panic：程序遇到无法处理的错误，崩溃
- recover：在defer中捕获panic，让程序不崩溃
```go
func safeFunction() {
    defer func() {
        if r := recover(); r != nil {
            fmt.Println("捕获到panic:", r)
        }
    }()
    panic("出大事了！")
}
```
- panic和recover不是用来做异常处理的（和Java的try-catch不同）
- 正确用法：只在不可恢复的严重错误时panic
- 错误处理请用error返回值

---

### 第28章 · 指针

#### 28.1 什么是指针
- 比喻：变量是一栋房子，指针是记录了这栋房子地址的纸条
- 指针的值是一个内存地址
- 指针的类型：`*int` = "指向int的指针"

#### 28.2 &和*操作符
- `&`：取地址（拿到记录地址的纸条）
  ```go
  x := 42
  p := &x  // p是*int类型，存着x的地址
  ```
- `*`：解引用（根据纸条找到房子）
  ```go
  *p = 100  // 通过指针修改x的值
  fmt.Println(x)  // 100
  ```

#### 28.3 为什么需要指针
- 原因1：函数里需要修改原始数据
  ```go
  func changeValue(p *int) {
      *p = 100
  }
  ```
- 原因2：避免复制大对象
  ```go
  func process(data *BigStruct) {
      // 只传了8字节（地址），而不是复制整个BigStruct
  }
  ```
- 原因3：表示"没有值"（nil指针）

#### 28.4 new和make的区别
- `new(T)`：分配内存，返回`*T`（指向T的指针），内存被置为零值
- `make(T, args)`：只用于slice、map、channel，返回T本身（不是指针），会初始化内部结构
- 记忆口诀：new返回指针，make返回初始化后的引用类型
```go
p := new(int)       // p是*int，*p=0
s := make([]int, 5) // s是[]int，len=5
```

#### 28.5 指针 vs 值传递的选择
- 用值传递：
  - 小对象（基本类型、小结构体）
  - 不需要修改原始数据
  - 并发安全（每个Goroutine有自己的副本）
- 用指针传递：
  - 大对象
  - 需要修改原始数据
  - 需要表示"没有值"（nil）
- Go的指针不支持算术运算（不像C，不能p++）

---

### 第29章 · 结构体（Struct）

#### 29.1 结构体的定义
```go
type User struct {
    ID       int
    Name     string
    Age      int
    Email    string
}
```
- 结构体 = 把相关的不同数据打包在一起
- 比喻：结构体就像一张个人信息表

#### 29.2 结构体的创建和初始化
- 方式一：按顺序
  ```go
  u := User{1, "张三", 20, "zhangsan@example.com"}
  ```
- 方式二：按字段名（推荐，顺序无关）
  ```go
  u := User{
      Name: "张三",
      Age:  20,
  }
  ```
- 方式三：new
  ```go
  u := new(User)  // u是*User，所有字段为零值
  u.Name = "张三"
  ```

#### 29.3 匿名字段和结构体嵌套
- 匿名字段（继承效果）：
  ```go
  type Animal struct {
      Name string
  }
  type Dog struct {
      Animal  // 匿名字段，Dog自动拥有Animal的所有字段
      Breed string
  }
  d := Dog{Animal: Animal{Name: "旺财"}, Breed: "金毛"}
  fmt.Println(d.Name)  // 直接访问（提升）
  ```
- 结构体嵌套（组合效果）：
  ```go
  type Address struct {
      City    string
      Street  string
  }
  type User struct {
      Name    string
      Address Address  // 命名字段嵌套
  }
  ```

#### 29.4 结构体标签（Tag）
- Tag是附加在字段上的元数据
```go
type User struct {
    ID   int    `json:"id" gorm:"primaryKey"`
    Name string `json:"name" validate:"required"`
}
```
- 用反射获取Tag：`field.Tag.Get("json")`
- 常见用途：JSON序列化、数据库ORM、参数校验

#### 29.5 空结构体
- `struct{}`：不占内存（0字节）
- 用途：
  - `map[string]struct{}`：实现Set
  - `chan struct{}`：信号通知

---

### 第30章 · 方法

#### 30.1 方法的定义
- 方法 = 绑定到特定类型的函数
```go
type User struct {
    Name string
}

// (u User) 是接收者
func (u User) Greet() string {
    return "你好，我是" + u.Name
}
```
- 调用：`user.Greet()`

#### 30.2 值接收者 vs 指针接收者
- 值接收者：方法内修改不影响原始数据
  ```go
  func (u User) SetName(name string) {
      u.Name = name  // 不影响外部（u是副本）
  }
  ```
- 指针接收者：方法内修改影响原始数据
  ```go
  func (u *User) SetName(name string) {
      u.Name = name  // 影响外部（u是指针）
  }
  ```

#### 30.3 如何选择接收者类型
- 用指针接收者如果：
  - 方法需要修改接收者
  - 接收者是大型结构体（避免复制）
  - 保持一致性（如果一个方法用了指针，其他也都用指针）
- 用值接收者如果：
  - 接收者是小结构体且不需要修改
  - 接收者是基本类型的别名

#### 30.4 方法集
- 值接收者的方法可以被值和指针调用
- 指针接收者的方法只能被指针调用（接口场景下重要）

---

### 第31章 · 接口（Interface）

#### 31.1 接口是什么
- 比喻：接口就是插座标准
- 不管什么电器（电视机、冰箱、电风扇）
- 只要插头符合插座标准（实现了接口定义的方法）
- 就能插上使用
```go
type Writer interface {
    Write([]byte) (int, error)
}
```
- 任何实现了 `Write([]byte) (int, error)` 方法的类型，都算实现了Writer接口

#### 31.2 隐式实现（Go的特色）
- Go不需要 `implements` 关键字
- 只要类型的方法集包含了接口的所有方法，就自动实现了接口
- 好处：解耦，不用显式声明依赖

#### 31.3 接口的值
- 接口变量有两部分：
  - 动态类型：实际存了什么类型
  - 动态值：实际的值是什么
- 一个nil的接口和一个值为nil的接口是不同的
```go
var w Writer        // w == nil（类型和值都是nil）
var buf *bytes.Buffer  // buf == nil
w = buf             // w != nil！（类型不为nil）
```

#### 31.4 类型断言
```go
var w Writer = os.Stdout
f, ok := w.(*os.File)  // ok=true，因为Stdout确实是*os.File
```
- 类型断言可以拿到接口背后的具体类型

#### 31.5 类型开关
```go
switch v := x.(type) {
case int:
    fmt.Println("int:", v)
case string:
    fmt.Println("string:", v)
default:
    fmt.Println("unknown")
}
```

#### 31.6 接口组合
```go
type Reader interface {
    Read([]byte) (int, error)
}
type Writer interface {
    Write([]byte) (int, error)
}
type ReadWriter interface {
    Reader
    Writer
}
```

#### 31.7 常用标准接口
- `io.Reader` / `io.Writer`
- `fmt.Stringer`：定义对象的字符串表示
- `error`：所有错误的接口
- `sort.Interface`：排序接口
- `http.Handler`：HTTP处理接口

---

### 第32章 · 错误处理

#### 32.1 error接口
```go
type error interface {
    Error() string
}
```
- Go最简单的接口，只有一个方法

#### 32.2 创建错误
- `errors.New("出错了")`
- `fmt.Errorf("文件%s不存在", filename)`

#### 32.3 错误处理模式
```go
result, err := doSomething()
if err != nil {
    // 处理错误
    return err
}
// 继续正常流程
```
- Go的哲学：显式处理错误，不隐藏

#### 32.4 错误包装（Go 1.13+）
- `fmt.Errorf("读取配置失败: %w", err)`：%w包装原始错误
- `errors.Unwrap(err)`：解开包装
- `errors.Is(err, target)`：判断是否包含某个错误
- `errors.As(err, &target)`：提取特定类型的错误

#### 32.5 自定义错误类型
```go
type MyError struct {
    Op   string
    Code int
    Msg  string
}
func (e *MyError) Error() string {
    return fmt.Sprintf("operation %s failed (code %d): %s", e.Op, e.Code, e.Msg)
}
```

#### 32.6 错误处理最佳实践
- 不要忽略错误（err必须被检查）
- 错误只处理一次（要么往上抛，要么处理掉）
- 添加上下文信息再往上抛
- 不要在错误信息里暴露敏感信息
- 使用sentinel error（包级错误变量）表示特定错误：
  ```go
  var ErrNotFound = errors.New("not found")
  ```

---

### 第33章 · 包（Package）与模块

#### 33.1 包的定义
- 每个.go文件第一行声明它属于哪个包
- 同一个目录下的文件必须属于同一包

#### 33.2 导出规则
- 大写字母开头 → 导出（公开，其他包能用）
- 小写字母开头 → 不导出（私有，只有本包能用）
- 适用于：变量、函数、类型、方法、结构体字段

#### 33.3 init函数
- init在包被导入时自动执行
- 一个包可以有多个init函数（甚至一个文件多个）
- 执行顺序：被导入的包先执行init，main包最后
- 用途：注册驱动、初始化配置

#### 33.4 Go Modules
- Go 1.11引入，1.16后默认启用
- `go.mod`：定义模块名和依赖
  ```
  module github.com/myuser/myproject
  go 1.21
  require (
      github.com/gin-gonic/gin v1.9.0
  )
  ```
- `go.sum`：依赖的校验和，保证依赖没被篡改
- `go mod init`：初始化模块
- `go mod tidy`：清理不需要的依赖，添加缺失的依赖
- `go get`：添加依赖
- `go mod vendor`：把依赖复制到vendor目录

---

### 第34章 · 并发编程（一）：Goroutine

#### 34.1 并发和并行的区别（再强调）
- 并发：逻辑上同时（交替执行，看起来像同时）
- 并行：物理上同时（多个CPU核同时执行）

#### 34.2 Goroutine是什么
- Goroutine = Go的轻量级"线程"
- 操作系统线程：约1MB栈空间
- Goroutine：初始2KB栈空间，可以动态增长
- 一个程序可以轻松跑上万个Goroutine
- 创建：`go func() { ... }()`

#### 34.3 Goroutine的调度：GMP模型
- G（Goroutine）：要执行的任务
- M（Machine/Thread）：操作系统线程，真正干活的
- P（Processor）：调度器，持有G的队列，把G分配给M
- GMP的工作原理：
  - P管理着G的队列
  - M从P那里取G来执行
  - G被阻塞了（比如等IO），M会换另一个G执行
- 这就是Goroutine高效的原因：少量系统线程调度大量Goroutine

---

### 第35章 · 并发编程（二）：Channel

#### 35.1 Channel是什么
- 比喻：Channel是Goroutine之间的"管道"
- 一个Goroutine往管道里放数据，另一个从管道里取数据
- 这是Go的哲学：**不要通过共享内存来通信，而要通过通信来共享内存**

#### 35.2 创建Channel
- `ch := make(chan int)`：无缓冲channel（双方必须同时到达）
- `ch := make(chan int, 10)`：有缓冲channel（缓冲区大小10）

#### 35.3 发送和接收
```go
ch <- 42     // 发送
v := <-ch    // 接收
v, ok := <-ch  // 接收，ok=false表示channel已关闭且为空
```

#### 35.4 无缓冲 vs 有缓冲
- 无缓冲（同步channel）：
  - 发送方必须等接收方来取
  - 接收方必须等发送方来发
  - 比喻：两个人面对面交接物品
- 有缓冲（异步channel）：
  - 发送方只要缓冲区没满就能发
  - 接收方只要缓冲区不空就能取
  - 比喻：快递柜

#### 35.5 Channel的关闭
- `close(ch)`关闭channel
- 关闭后再发送会panic
- 关闭后再接收：把剩余数据取完，然后返回零值
- 判断是否关闭：`v, ok := <-ch`，ok=false表示已关闭
- 只有发送方应该关闭channel（向已关闭channel发送会panic）
- 不要关闭接收端的channel

#### 35.6 select语句
```go
select {
case v := <-ch1:
    fmt.Println("来自ch1:", v)
case ch2 <- 42:
    fmt.Println("发送到ch2了")
case <-time.After(time.Second):
    fmt.Println("超时了")
default:
    fmt.Println("没有人准备好")
}
```
- select同时监听多个channel操作
- 如果多个case都准备好了，随机选一个
- 有default时是非阻塞的

---

### 第36章 · 并发编程（三）：同步原语

#### 36.1 互斥锁：sync.Mutex
```go
var mu sync.Mutex
var counter int

func increment() {
    mu.Lock()
    counter++
    mu.Unlock()
}
```
- Lock()：加锁，如果锁被占用了就等
- Unlock()：释放锁
- 一定要用defer保证解锁：`defer mu.Unlock()`

#### 36.2 读写锁：sync.RWMutex
- 读锁：多个Goroutine可以同时持有（读不冲突）
- 写锁：独占，其他读和写都要等
- 适用场景：读多写少
```go
var rw sync.RWMutex
rw.RLock()    // 加读锁
rw.RUnlock()  // 解读锁
rw.Lock()     // 加写锁
rw.Unlock()   // 解写锁
```

#### 36.3 等待组：sync.WaitGroup
```go
var wg sync.WaitGroup

for i := 0; i < 5; i++ {
    wg.Add(1)        // 计数+1
    go func() {
        defer wg.Done()  // 计数-1
        // 干活
    }()
}
wg.Wait()  // 阻塞直到计数归零
```

#### 36.4 执行一次：sync.Once
```go
var once sync.Once
once.Do(func() {
    // 这段代码在整个程序生命周期中只执行一次
    // 适合：初始化、单例模式
})
```

#### 36.5 原子操作
- `sync/atomic` 包
- `atomic.AddInt64(&count, 1)`：原子加
- `atomic.LoadInt64(&count)`：原子读
- `atomic.StoreInt64(&count, 100)`：原子写
- `atomic.CompareAndSwapInt64(&count, old, new)`：CAS
- 原子操作比互斥锁快（不需要上下文切换）

---

### 第37章 · Context

#### 37.1 为什么需要Context
- 场景：一个HTTP请求进来，可能要查数据库、调其他服务、写日志...
- 如果用户关了浏览器，这些操作应该被取消（节省资源）
- Context就是用来传递"取消信号"、"超时"、"请求级别的值"的

#### 37.2 Context的四个核心方法
```go
type Context interface {
    Deadline() (deadline time.Time, ok bool)
    Done() <-chan struct{}     // 返回一个channel，Context取消时关闭
    Err() error                // 返回取消的原因
    Value(key interface{}) interface{}  // 获取关联的值
}
```

#### 37.3 创建Context
- `context.Background()`：根Context（main函数、初始化时用）
- `context.TODO()`：占位符，不确定用哪个时先用这个
- `context.WithCancel(parent)`：可取消的Context
- `context.WithTimeout(parent, duration)`：超时取消
- `context.WithDeadline(parent, time)`：截止时间取消
- `context.WithValue(parent, key, value)`：携带值

#### 37.4 Context的使用模式
```go
func doWork(ctx context.Context) {
    select {
    case <-time.After(5 * time.Second):
        fmt.Println("完成")
    case <-ctx.Done():
        fmt.Println("被取消了:", ctx.Err())
    }
}

ctx, cancel := context.WithTimeout(context.Background(), 3*time.Second)
defer cancel()  // 总是调用cancel释放资源
go doWork(ctx)
```

#### 37.5 Context最佳实践
- Context应该是函数的第一个参数：`func(ctx context.Context, ...)`
- 不要把Context存在结构体里（应该显式传递）
- 不要传nil Context（不确定就用context.TODO()）
- WithValue只用来传请求级别的数据（如traceID），不要传函数参数
- Context是并发安全的

---

### 第38章 · 文件操作

#### 38.1 读取文件
- `os.ReadFile(filename)`：一次性读取全部（小文件）
- `os.Open(filename)`：打开文件，返回`*os.File`
- `bufio.NewScanner(file)`：逐行读取（大文件推荐）
- `io.ReadAll(file)`：读取全部到内存

#### 38.2 写入文件
- `os.WriteFile(filename, data, 0644)`：一次性写入
- `os.Create(filename)`：创建文件（已存在则清空）
- `os.OpenFile(filename, flags, perm)`：灵活打开
- `bufio.NewWriter(file)`：缓冲写入

#### 38.3 文件信息
- `os.Stat(filename)`：获取文件信息
- `os.IsNotExist(err)`：判断文件不存在
- `os.IsExist(err)`：判断文件存在

#### 38.4 路径操作
- `filepath.Join("dir", "file.txt")`：拼接路径（跨平台）
- `filepath.Base(path)`：文件名
- `filepath.Dir(path)`：目录部分
- `filepath.Ext(path)`：扩展名
- `os.Mkdir` / `os.MkdirAll`：创建目录

---

### 第39章 · 序列化

#### 39.1 JSON操作
- 序列化：`json.Marshal(v)` → `[]byte`
- 反序列化：`json.Unmarshal(data, &v)`
- 结构体Tag控制JSON：
  ```go
  type User struct {
      Name string `json:"name"`          // 字段名映射
      Age  int    `json:"age,omitempty"` // 零值时不输出
      Pass string `json:"-"`             // 忽略
  }
  ```
- `json.NewEncoder(w).Encode(v)`：直接写入Writer
- `json.NewDecoder(r).Decode(&v)`：直接从Reader读取

#### 39.2 其他格式
- XML：`encoding/xml`
- YAML：第三方库 `gopkg.in/yaml.v3`
- Protobuf：Google的高性能序列化格式，二进制

---

## 第二篇：数据结构与算法

---

### 第40章 · 为什么学数据结构与算法

#### 40.1 数据结构是什么
- 比喻：数据结构就是"装数据的容器"
- 不同的容器适合不同的场景
- 就像厨房里：有盘子、碗、锅、杯子，各有各的用途
- 常见数据结构：
  - 数组：一排连续的小格子
  - 链表：一串用绳子连起来的珠子
  - 栈：一叠盘子（先放后拿）
  - 队列：排队的人（先来先走）
  - 哈希表：有编号的储物柜
  - 树：公司组织架构图

#### 40.2 算法是什么
- 比喻：算法就是"菜谱"
- 菜谱告诉你：用什么原料（输入）、按什么步骤、做出什么菜（输出）
- 同样的原料，不同的做法，速度和味道都不一样
- 对程序员来说：同样的数据，不同的算法，运行速度天差地别

#### 40.3 为什么后端工程师需要学
- 面试必考（大厂尤其重视）
- 写高性能系统必须懂（数据库索引就是B+树，Redis的Sorted Set就是跳表）
- 训练思维方式（遇到问题知道怎么高效解决）
- 读源码的基础（不懂数据结构就看不懂框架源码）

---

### 第41章 · 时间复杂度与空间复杂度

#### 41.1 为什么需要复杂度分析
- 不能用"在我的电脑上跑了5秒"来衡量算法好坏
- 因为不同的电脑性能不一样
- 需要一种不依赖硬件的衡量方式

#### 41.2 大O表示法
- O()表示最坏情况下的增长趋势
- 忽略常数项和低阶项：
  - O(2n+3) → O(n)
  - O(n²+100n) → O(n²)

#### 41.3 常见时间复杂度
- O(1)：常数时间（不管数据多大，时间一样）
  - 例子：数组按下标取值
- O(log n)：对数时间（数据翻倍，时间只增加一点点）
  - 例子：二分查找
- O(n)：线性时间（数据翻倍，时间也翻倍）
  - 例子：遍历数组
- O(n log n)：线性对数时间
  - 例子：归并排序、快速排序
- O(n²)：平方时间（数据翻倍，时间翻4倍）
  - 例子：双重循环、冒泡排序
- O(2ⁿ)：指数时间（数据加1，时间翻倍）
  - 例子：递归求斐波那契

#### 41.4 空间复杂度
- 算法执行需要的额外内存空间
- 同样的分析方式

#### 41.5 如何分析
- 一段代码一行的分析
- 多个例子实战

---

### 第42章 · 数组与切片源码分析

#### 42.1 Go切片的底层源码
- 分析runtime/slice.go的关键代码
- 数据结构定义
- makeslice函数的逻辑
- growslice（扩容）函数的详细逻辑

#### 42.2 扩容策略的数学
- 什么时候触发扩容
- 扩容多少
- 内存对齐的影响

---

### 第43章 · 链表

#### 43.1 单向链表
- 每个节点有两个部分：数据和指向下一个节点的指针
- Go实现：
  ```go
  type Node struct {
      Val  int
      Next *Node
  }
  ```

#### 43.2 双向链表
- 每个节点有三个部分：数据、指向前一个的指针、指向后一个的指针
- Go标准库：`container/list`

#### 43.3 链表 vs 切片
| 操作 | 切片 | 链表 |
|------|------|------|
| 随机访问 | O(1) | O(n) |
| 头部插入 | O(n) | O(1) |
| 尾部插入 | O(1)（平均） | O(1) |
| 中间插入 | O(n) | O(n)（找位置）+ O(1)（插入） |
| 内存 | 连续（缓存友好） | 分散 |

#### 43.4 常见链表算法
- 反转链表（迭代 + 递归）
- 找中间节点（快慢指针）
- 判断是否有环（快慢指针）
- 合并两个有序链表

---

### 第44章 · 栈与队列

#### 44.1 栈（Stack）
- LIFO：Last In First Out（后进先出）
- 比喻：一叠盘子，最后放的先拿
- 操作：Push（入栈）、Pop（出栈）、Peek（看栈顶）
- Go实现：用切片模拟
- 实际应用：
  - 函数调用栈（每个函数调用就是一个栈帧）
  - 括号匹配（编译器检查括号）
  - 浏览器的后退功能
  - DFS（深度优先搜索）

#### 44.2 队列（Queue）
- FIFO：First In First Out（先进先出）
- 比喻：排队买票，先来的先买
- 操作：Enqueue（入队）、Dequeue（出队）
- Go实现：用切片或链表
- 实际应用：
  - 消息队列（RabbitMQ、Kafka）
  - BFS（广度优先搜索）
  - 打印队列
  - 任务调度

#### 44.3 循环队列
- 解决普通队列"假溢出"问题
- 用数组实现，头尾指针循环移动

---

### 第45章 · 哈希表深入

#### 45.1 哈希函数
- 输入任意数据 → 输出固定长度的数字
- 同一个输入永远得到同一个输出
- 不同输入可能得到同一个输出（哈希冲突）
- Go的哈希函数：根据CPU架构选择（AES指令集加速）

#### 45.2 哈希冲突的解决方案
- 链地址法（Go使用）：每个桶后面挂链表
- 开放寻址法：冲突了就找下一个空位

#### 45.3 Go Map底层源码分析
- hmap结构体
- bmap（桶）结构
- tophash的作用
- 扩容的两种类型：增量扩容和等量扩容

---

### 第46章 · 树

#### 46.1 树的基本概念
- 根节点、叶子节点、父节点、子节点
- 深度、高度
- 二叉树：每个节点最多两个子节点

#### 46.2 二叉搜索树（BST）
- 左子树所有节点 < 当前节点 < 右子树所有节点
- 插入、查找、删除操作
- 为什么BST可能退化成链表：插入有序数据时

#### 46.3 树的遍历
- 前序遍历：根 → 左 → 右
- 中序遍历：左 → 根 → 右（BST中序遍历得到有序结果）
- 后序遍历：左 → 右 → 根
- 层序遍历：一层一层来（BFS）
- 递归和非递归实现

#### 46.4 平衡二叉树简介
- 为什么需要平衡：防止退化成链表
- AVL树：严格平衡
- 红黑树：近似平衡，性能更好

---

### 第47章 · 堆与优先队列

#### 47.1 堆是什么
- 完全二叉树
- 最大堆：每个节点 >= 子节点（堆顶最大）
- 最小堆：每个节点 <= 子节点（堆顶最小）

#### 47.2 Go的container/heap
- 实现heap.Interface接口
- Push和Pop操作
- 应用：优先队列

#### 47.3 堆排序
- 建堆
- 不断取堆顶 → 调整堆
- O(n log n)时间复杂度

#### 47.4 实际应用
- Top K问题：找最大的K个数
- 任务调度：优先级高的先执行
- Dijkstra最短路径
- 合并K个有序链表

---

### 第48章 · 排序算法

#### 48.1 冒泡排序
- 原理：相邻比较，大的往后冒
- 时间复杂度：O(n²)
- 空间复杂度：O(1)
- 稳定排序

#### 48.2 选择排序
- 原理：每次找最小的放前面
- 时间复杂度：O(n²)
- 不稳定

#### 48.3 插入排序
- 原理：像打牌，摸一张插一张
- 时间复杂度：最好O(n)（已经有序），最坏O(n²)
- 小规模数据表现好

#### 48.4 快速排序
- 原理：选一个基准，小的放左边大的放右边，递归
- 时间复杂度：平均O(n log n)，最坏O(n²)
- 为什么最坏：基准选得不好（如选到最小/最大）
- 不稳定

#### 48.5 归并排序
- 原理：分一半，分别排序，再合并
- 时间复杂度：O(n log n)（稳定）
- 空间复杂度：O(n)（需要额外空间）
- 稳定排序

#### 48.6 Go的sort.Slice
- 原理：模式击败排序（pdqsort，Go 1.19+）
- 结合了快排、堆排、插入排序的优点

---

### 第49章 · 搜索算法与常见面试题

#### 49.1 线性搜索
- 一个一个找
- O(n)

#### 49.2 二分搜索
- 每次砍掉一半
- O(log n)
- 前提：数据有序
- 变体：找第一个等于、找最后一个等于、找第一个大于等于

#### 49.3 DFS（深度优先搜索）
- 一条路走到黑，不行再退回来
- 用栈（或递归）实现
- 应用：迷宫、排列组合

#### 49.4 BFS（广度优先搜索）
- 一层一层往外找
- 用队列实现
- 应用：最短路径

#### 49.5 常见面试题
- 两数之和（哈希表）
- 链表是否有环（快慢指针）
- 有效的括号（栈）
- 二叉树的最大深度（递归）
- LRU缓存（哈希表+双向链表）
- 最长不重复子串（滑动窗口）

---

## 第三篇：数据库

---

### 第50章 · 数据库基础与MySQL安装

#### 50.1 什么是数据库
- 比喻：数据库就是"电子化的仓库"
- 仓库有货架（表）、货架上有箱子（行）、箱子里有物品（列）
- 数据库 vs Excel：Excel是个人记账本，数据库是大型仓储管理系统
- 数据库的核心能力：存、查、改、删，同时支持多人同时操作
- 为什么后端必须学数据库：用户的数据要存下来，下次还能查到

#### 50.2 关系型数据库 vs 非关系型数据库
- 关系型（SQL）：MySQL、PostgreSQL、Oracle
  - 数据以表格形式存在，表之间可以关联
  - 比喻：Excel表格，每个Sheet一张表，通过某一列的值关联
- 非关系型（NoSQL）：Redis、MongoDB、Elasticsearch
  - Redis：超快的内存键值存储，比喻为"大脑中的便签纸"
  - MongoDB：文档型数据库，存JSON，比喻为"文件柜里直接放文件夹"
  - 选择原则：结构化数据用SQL，缓存/临时数据用Redis

#### 50.3 MySQL是什么
- MySQL是世界上最流行的开源关系型数据库
- 比喻：MySQL就是仓库管理系统软件
- 特点：免费、稳定、社区活跃、与几乎所有语言都有驱动
- 版本：5.7（经典稳定版）和 8.0（新特性版本）

#### 50.4 MySQL安装（Windows）
- 下载MySQL Installer
- 安装过程：选择Server Only → 设置root密码 → 添加环境变量
- 验证安装：`mysql -u root -p` 能进入MySQL命令行即成功
- 图形化工具推荐：Navicat / DBeaver / MySQL Workbench

#### 50.5 MySQL安装（Linux）
- Ubuntu：`sudo apt install mysql-server`
- CentOS：`sudo yum install mysql-server`
- 启动服务：`sudo systemctl start mysql`
- 安全配置：`sudo mysql_secure_installation` 设置密码策略

#### 50.6 MySQL基本架构
- 连接层：处理客户端连接、认证
- 服务层：SQL解析、查询优化、缓存（8.0已移除查询缓存）
- 存储引擎层：负责数据的真正读写（InnoDB最常用）
- 系统文件层：数据最终存到磁盘
- 比喻：客服接电话（连接层）→ 老员工分析问题（服务层）→ 仓库管理员取货（引擎层）→ 实际仓库（磁盘）

#### 50.7 数据库的基本操作命令
```sql
SHOW DATABASES;                          -- 查看所有数据库
CREATE DATABASE mydb;                    -- 创建数据库
USE mydb;                                -- 切换数据库
DROP DATABASE mydb;                      -- 删除数据库（危险操作！）
```
- 比喻：CREATE DATABASE = 建一个新仓库，USE = 走进这个仓库

#### 50.8 字符集与排序规则
- 字符集（Charset）：定义能存哪些字符，utf8mb4 支持emoji
- 排序规则（Collation）：定义字符串如何比较大小
- MySQL的utf8其实是阉割版（最多3字节），utf8mb4才是真utf8
- 创建数据库建议：`CREATE DATABASE mydb CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;`

---

### 第51章 · SQL基础：DDL与DML

#### 51.1 SQL是什么
- SQL = Structured Query Language，结构化查询语言
- 是操作关系型数据库的统一语言，MySQL/Oracle/PostgreSQL都用
- 比喻：SQL就像对仓库管理员下达的标准化指令

#### 51.2 SQL分类
- DDL（数据定义语言）：CREATE、ALTER、DROP —— 改表结构
- DML（数据操作语言）：INSERT、UPDATE、DELETE —— 改表数据
- DQL（数据查询语言）：SELECT —— 查数据
- DCL（数据控制语言）：GRANT、REVOKE —— 改权限
- TCL（事务控制语言）：BEGIN、COMMIT、ROLLBACK —— 改事务

#### 51.3 数据类型概览
- 整数：TINYINT(1字节)、SMALLINT(2)、INT(4)、BIGINT(8)
- 小数：DECIMAL(精确)、FLOAT(近似)、DOUBLE(近似)
- 字符串：CHAR(定长)、VARCHAR(变长)、TEXT(长文本)
- 日期：DATE、TIME、DATETIME、TIMESTAMP
- 二进制：BLOB
- CHAR vs VARCHAR：CHAR(10) 固定占10个字符空间；VARCHAR(10) 实际占用 = 实际长度 + 1字节
- 比喻：CHAR是定制的格子，不管东西多小格子大小不变；VARCHAR是弹性盒子

#### 51.4 创建表（CREATE TABLE）
```sql
CREATE TABLE users (
    id         INT AUTO_INCREMENT PRIMARY KEY COMMENT '用户ID',
    username   VARCHAR(50)  NOT NULL UNIQUE COMMENT '用户名',
    password   VARCHAR(255) NOT NULL COMMENT '密码（加密存储）',
    email      VARCHAR(100) COMMENT '邮箱',
    age        TINYINT UNSIGNED COMMENT '年龄',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';
```
- 每个字段都要仔细考虑类型和约束
- AUTO_INCREMENT：自动递增主键
- NOT NULL：不允许为空
- UNIQUE：值必须唯一
- DEFAULT：默认值

#### 51.5 修改表（ALTER TABLE）
```sql
ALTER TABLE users ADD COLUMN phone VARCHAR(20) AFTER email;   -- 加字段
ALTER TABLE users MODIFY COLUMN age INT;                      -- 修改字段类型
ALTER TABLE users DROP COLUMN age;                            -- 删除字段
ALTER TABLE users RENAME TO users_backup;                     -- 重命名表
```
- ALTER是大操作，在生产环境要谨慎
- 比喻：ALTER = 仓库装修，装修时仓库要停业

#### 51.6 删除表（DROP TABLE / TRUNCATE）
```sql
DROP TABLE users;        -- 表结构和数据一起删除
TRUNCATE TABLE users;    -- 清空数据但保留表结构
DELETE FROM users;       -- 逐行删除，可回滚，触发触发器
```
- TRUNCATE vs DELETE：TRUNCATE瞬间清空（不可回滚），DELETE逐行删（可回滚）
- 比喻：DROP=把货架拆了，TRUNCATE=把货架上所有东西掀掉，DELETE=一件一件拿下来扔

#### 51.7 插入数据（INSERT）
```sql
INSERT INTO users (username, password, email) VALUES ('张三', 'hashed_pwd', 'zhangsan@example.com');
INSERT INTO users (username, password, email) VALUES
    ('李四', 'pwd2', 'lisi@example.com'),
    ('王五', 'pwd3', 'wangwu@example.com');   -- 批量插入
INSERT INTO users SET username='赵六', password='pwd4';       -- 另一种语法
```
- 自增主键不需要手动指定
- 批量INSERT比逐条INSERT快很多

#### 51.8 更新数据（UPDATE）
```sql
UPDATE users SET email='new@example.com' WHERE id = 1;
UPDATE users SET age = age + 1 WHERE age < 18;   -- 把所有未成年人的年龄+1
```
- **WHERE条件必须加！不加WHERE会更新全表！**
- 比喻：UPDATE就像"修改货架上某个箱子的标签"

#### 51.9 删除数据（DELETE）
```sql
DELETE FROM users WHERE id = 1;
DELETE FROM users WHERE created_at < '2020-01-01';  -- 删除三年前的记录
```
- **WHERE条件必须加！**
- 软删除（推荐）：加一个 `deleted_at` 字段，删除时设时间戳，查询时过滤

---

### 第52章 · SQL进阶：查询与聚合

#### 52.1 SELECT基础
```sql
SELECT * FROM users;                               -- 查所有字段（生产环境避免用*）
SELECT id, username, email FROM users;             -- 只查需要的字段
SELECT username AS 用户名, email AS 邮箱 FROM users; -- 别名
```
- 比喻：SELECT = 你告诉仓库管理员"帮我把这些货架上这些箱子的这些标签念给我听"

#### 52.2 WHERE条件筛选
```sql
SELECT * FROM users WHERE age > 18;                          -- 比较
SELECT * FROM users WHERE age BETWEEN 18 AND 30;             -- 范围
SELECT * FROM users WHERE username IN ('张三', '李四');       -- 集合
SELECT * FROM users WHERE email IS NULL;                     -- 空值
SELECT * FROM users WHERE email IS NOT NULL;                 -- 非空
SELECT * FROM users WHERE username LIKE '张%';               -- 模糊匹配（%任意字符）
SELECT * FROM users WHERE username LIKE '__';                -- 两个字符（_一个字符）
```
- 多个条件用 AND / OR 组合：`WHERE age > 18 AND status = 1`

#### 52.3 ORDER BY排序
```sql
SELECT * FROM users ORDER BY age ASC;           -- 升序（默认）
SELECT * FROM users ORDER BY age DESC;          -- 降序
SELECT * FROM users ORDER BY age DESC, id ASC;  -- 多字段排序
```
- 比喻：让仓库管理员按指定顺序报货

#### 52.4 LIMIT分页
```sql
SELECT * FROM users LIMIT 10;                   -- 前10条
SELECT * FROM users LIMIT 10 OFFSET 20;         -- 跳过20条，取10条（第3页）
SELECT * FROM users LIMIT 20, 10;               -- 同上（MySQL特有语法）
```
- 分页公式：LIMIT pageSize OFFSET (pageNum - 1) * pageSize
- 深分页问题：OFFSET很大时性能差，可用游标分页

#### 52.5 DISTINCT去重
```sql
SELECT DISTINCT age FROM users;                 -- 所有不重复的年龄值
SELECT COUNT(DISTINCT age) FROM users;          -- 不重复年龄的数量
```

#### 52.6 聚合函数
```sql
SELECT COUNT(*) FROM users;                     -- 总行数
SELECT AVG(age) FROM users;                     -- 平均年龄
SELECT SUM(salary) FROM employees;              -- 总和
SELECT MAX(age), MIN(age) FROM users;           -- 最大最小值
```
- 聚合函数会忽略NULL值（COUNT(*)除外）
- 比喻：聚合函数 = 仓库管理员帮你做统计报表

#### 52.7 GROUP BY分组
```sql
SELECT age, COUNT(*) AS cnt FROM users GROUP BY age;
SELECT age, COUNT(*) AS cnt FROM users GROUP BY age HAVING cnt > 5;
```
- GROUP BY 把数据按某列分组，每组做聚合运算
- WHERE 作用于分组前，HAVING 作用于分组后
- 比喻：先把货架上的东西按颜色分组，再数每组有多少个

#### 52.8 SQL执行顺序
- 书写顺序：SELECT → FROM → JOIN → WHERE → GROUP BY → HAVING → ORDER BY → LIMIT
- 实际执行顺序：FROM → JOIN → WHERE → GROUP BY → HAVING → SELECT → ORDER BY → LIMIT
- 理解执行顺序才能写出正确的SQL

---

### 第53章 · SQL高级：多表查询

#### 53.1 为什么需要多表查询
- 现实中数据不会都放在一张表里（单表膨胀、数据冗余）
- 比喻：用户信息一个仓库，订单信息另一个仓库，现在要查"张三的所有订单"
- 需要建立表之间的关联（外键）

#### 53.2 外键（Foreign Key）
```sql
CREATE TABLE orders (
    id      INT PRIMARY KEY,
    user_id INT NOT NULL,
    amount  DECIMAL(10,2),
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```
- 外键保证引用完整性：user_id必须在users表中存在
- 比喻：订单上的用户ID必须能对应到真实的用户，不能指一个不存在的用户
- 生产环境有时不用物理外键（性能考虑），但在应用层保证引用完整性

#### 53.3 JOIN连接
- 连接的本质：把两张表按某种条件拼在一起
- 比喻：两张表就像两本花名册，JOIN就是根据关联字段把它们合成一张大表

#### 53.4 INNER JOIN（内连接）
```sql
SELECT users.username, orders.amount
FROM users
INNER JOIN orders ON users.id = orders.user_id;
```
- 只返回两表中匹配上的行
- 比喻：只列出"既有用户信息又有订单信息"的记录

#### 53.5 LEFT JOIN（左连接）
```sql
SELECT users.username, orders.amount
FROM users
LEFT JOIN orders ON users.id = orders.user_id;
```
- 左表全部保留，右表匹配不上的填NULL
- 比喻：列出所有用户，有订单的显示订单，没订单的订单列显示空

#### 53.6 RIGHT JOIN（右连接）
- 和LEFT JOIN对称，保留右表全部
- 实际上LEFT JOIN就能覆盖所有场景（交换表顺序即可）

#### 53.7 多表连接
```sql
SELECT u.username, o.amount, p.name AS product_name
FROM users u
JOIN orders o ON u.id = o.user_id
JOIN order_items oi ON o.id = oi.order_id
JOIN products p ON oi.product_id = p.id;
```
- 可以连任意多张表，每次JOIN都拼入一张新表
- 给表起短别名（u, o, p）让SQL更简洁

#### 53.8 子查询
```sql
-- 查询年龄大于平均年龄的用户
SELECT * FROM users WHERE age > (SELECT AVG(age) FROM users);

-- 查询有订单的用户
SELECT * FROM users WHERE id IN (SELECT DISTINCT user_id FROM orders);

-- 子查询作为临时表
SELECT t.age, t.cnt FROM (
    SELECT age, COUNT(*) AS cnt FROM users GROUP BY age
) AS t WHERE t.cnt > 3;
```
- 子查询可以出现在WHERE、FROM、SELECT中
- 子查询先执行，结果再给外层查询用
- 比喻：先让一个管理员统计某数据，再让另一个管理员用这个结果查

#### 53.9 UNION与UNION ALL
```sql
SELECT username FROM users WHERE age > 30
UNION
SELECT username FROM users WHERE status = 'vip';
```
- UNION：合并两个查询结果，去重
- UNION ALL：合并但不去重，更快
- 要求：两个查询的列数和类型必须一致

#### 53.10 EXISTS
```sql
SELECT * FROM users WHERE EXISTS (
    SELECT 1 FROM orders WHERE orders.user_id = users.id AND amount > 1000
);
```
- EXISTS 检查子查询是否有结果，有就返回true
- 比喻：检查"这个用户有没有下过大单"
- 比 IN 更高效（找到一条就停止，不需要全表扫描子查询）

---

### 第54章 · 索引原理与优化

#### 54.1 什么是索引
- 比喻：索引 = 书的目录
- 没有索引：要找到"第5章"需要从头翻到尾（全表扫描）
- 有索引：看目录直接翻到第5章第1页（索引查找）
- 索引的本质：一种排序的数据结构，让数据库能快速定位数据

#### 54.2 B+树索引（MySQL InnoDB默认索引结构）
- B+树是一棵平衡的多路搜索树
- 所有数据都存在叶子节点，叶子节点之间用链表连接
- 非叶子节点只存键值用于导航
- 为什么用B+树：磁盘读写以页为单位（4KB/16KB），B+树每个节点刚好一页
- 比喻：B+树像多层目录，顶层目录→二级目录→具体页码

#### 54.3 索引类型
- 主键索引（PRIMARY KEY）：唯一、不为空、一张表只能有一个
- 唯一索引（UNIQUE）：值必须唯一，可以为NULL
- 普通索引（INDEX）：最普通的索引，允许重复和NULL
- 全文索引（FULLTEXT）：用于全文搜索
- 联合索引（复合索引）：多个列组成的索引
  ```sql
  CREATE INDEX idx_name_age ON users(name, age);
  ```

#### 54.4 最左前缀原则
- 联合索引 `(a, b, c)` 相当于创建了 `(a)`、`(a,b)`、`(a,b,c)` 三个索引
- `WHERE a=1 AND b=2` → 走索引
- `WHERE b=2` → 不走索引（跳过了a）
- `WHERE a=1 AND c=3` → 只用到a列索引（c跳过了b）
- 比喻：多级目录只能从左往右用，不能跳过前面的直接用后面的

#### 54.5 覆盖索引
- 查询的所有列都在索引中，不需要回表查数据
```sql
-- 有索引 idx_name_age(name, age)
SELECT name, age FROM users WHERE name = '张三';  -- 覆盖索引，不回表
SELECT name, age, email FROM users WHERE name = '张三';  -- email不在索引中，需要回表
```
- 覆盖索引性能远好于回表查询
- 比喻：目录里就写了答案，不用翻到正文

#### 54.6 索引失效的场景
- 在索引列上做函数运算：`WHERE YEAR(created_at) = 2023` → 失效
- 使用不等于：`WHERE age != 18` → 可能失效
- LIKE以%开头：`WHERE name LIKE '%张'` → 失效（`LIKE '张%'` 走索引）
- 隐式类型转换：`WHERE phone = 13800138000`（phone是varchar）→ 失效
- OR连接非索引列：`WHERE name='张三' OR status=1`（status无索引）→ 可能失效

#### 54.7 EXPLAIN分析查询
```sql
EXPLAIN SELECT * FROM users WHERE name = '张三';
```
- type列（从好到差）：system > const > eq_ref > ref > range > index > ALL
  - ALL：全表扫描（最差，必须优化）
  - index：全索引扫描
  - range：索引范围扫描
  - ref：非唯一索引查找
  - const：主键等值查找（极快）
- key列：实际用到的索引
- rows列：预计扫描行数
- Extra列：Using index（覆盖索引，好），Using filesort（文件排序，差），Using temporary（临时表，差）

#### 54.8 索引设计原则
- 为 WHERE、ORDER BY、JOIN 的列建索引
- 选择性高的列优先建索引（选择性 = 不重复值数 / 总行数）
- 不要过度索引（每个索引都要维护，增删改变慢）
- 联合索引优于多个单列索引（减少索引数量）
- 长字符串用前缀索引：`CREATE INDEX idx_title ON articles(title(20));`

#### 54.9 慢查询分析
- 开启慢查询日志：
  ```sql
  SET GLOBAL slow_query_log = ON;
  SET GLOBAL long_query_time = 1;  -- 超过1秒的查询记录
  ```
- 使用mysqldumpslow工具分析慢查询日志
- 定位到慢SQL后用EXPLAIN分析，优化索引或重写SQL

---

### 第55章 · 事务与隔离级别

#### 55.1 什么是事务
- 事务 = 一组不可分割的数据库操作
- 比喻：银行转账 — 从A扣100元 + 给B加100元，这两步要么都成功，要么都失败
- 不能出现"A扣了钱但B没收到"的情况
- 事务保证数据一致性

#### 55.2 ACID四大特性
- **A（原子性 Atomicity）**：事务中的操作要么全做，要么全不做
  - 比喻：你要么把整个月饼吃掉，要么一口都不吃
- **C（一致性 Consistency）**：事务前后，数据库从一个一致状态到另一个一致状态
  - 比喻：转账前后，总金额不变
- **I（隔离性 Isolation）**：并发事务之间互相不干扰
  - 比喻：两个人在不同柜台同时操作，互不影响
- **D（持久性 Durability）**：事务提交后，数据永久保存，即使系统崩溃
  - 比喻：合同签了字、盖了章就不能反悔

#### 55.3 事务的基本操作
```sql
-- 开启事务
START TRANSACTION;
-- 或者 BEGIN;
UPDATE accounts SET balance = balance - 100 WHERE id = 1;
UPDATE accounts SET balance = balance + 100 WHERE id = 2;
-- 如果一切正常
COMMIT;
-- 如果出错
ROLLBACK;
```

#### 55.4 并发事务的问题
- **脏读（Dirty Read）**：读了别人未提交的修改（之后可能回滚）
  - 比喻：看到别人草稿纸上的方案，结果人家后来改了
- **不可重复读（Non-Repeatable Read）**：同一次事务中两次读同一条数据结果不同
  - 比喻：你第一次看价格是100，转个身再看变成120了
- **幻读（Phantom Read）**：同一次事务中两次查询范围结果不同（多了或少了行）
  - 比喻：你统计仓库有多少箱货，第一次10箱，统计过程中有人搬来1箱，你再数变11箱了

#### 55.5 四种隔离级别
| 隔离级别 | 脏读 | 不可重复读 | 幻读 |
|---------|------|-----------|------|
| READ UNCOMMITTED | ✓ | ✓ | ✓ |
| READ COMMITTED | ✗ | ✓ | ✓ |
| REPEATABLE READ（MySQL默认） | ✗ | ✗ | 部分✓* |
| SERIALIZABLE | ✗ | ✗ | ✗ |

- MySQL InnoDB在REPEATABLE READ下通过MVCC+间隙锁解决了大部分幻读
- SERIALIZABLE 性能最差（事务完全串行），生产环境很少用

#### 55.6 设置隔离级别
```sql
-- 查看当前隔离级别
SELECT @@transaction_isolation;
-- 设置隔离级别
SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED;
```

#### 55.7 MVCC（多版本并发控制）
- InnoDB通过MVCC实现高并发
- 每行数据有多个版本，每个事务看到的是自己的"快照"
- 比喻：每个人拿到的是一份数据的"复印件"，你在复印件上改不影响原件的其他复印件
- 核心：undo log + read view
- 这就是为什么InnoDB的REPEATABLE READ能避免脏读和不可重复读

---

### 第56章 · MySQL锁机制

#### 56.1 为什么要加锁
- 比喻：公共浴室 — 一个人进去就锁门，别人不能进
- 数据库锁保证并发操作时数据不错乱
- 不加锁：两人同时买最后一件商品，库存变成-1

#### 56.2 按粒度分类：表锁 vs 行锁
- **表锁**：锁整张表（MyISAM默认，简单粗暴）
  - 比喻：把整个仓库大门锁了，所有人都不许进
- **行锁**：只锁一行数据（InnoDB支持，更精细）
  - 比喻：只锁一个储物柜，其他柜子正常使用
- InnoDB的行锁是加在索引上的，如果没有索引走全表扫描会退化为表锁

#### 56.3 共享锁（S锁）与排他锁（X锁）
- **共享锁（读锁）**：别人也能读，但不能写
  - `SELECT ... LOCK IN SHARE MODE;`（MySQL 8.0后用 `FOR SHARE`）
  - 比喻：你正在看一个文件，别人也能看但不能改
- **排他锁（写锁）**：别人既不能读也不能写
  - `SELECT ... FOR UPDATE;`
  - 比喻：你把文件拿走了别人根本看不到

#### 56.4 死锁
- 死锁：事务A等事务B释放资源，事务B又在等事务A释放资源
- 比喻：两个人在窄巷子里面对面，谁也不让谁，都过不去
```sql
-- 事务A
UPDATE accounts SET balance = balance - 100 WHERE id = 1;  -- 锁住id=1
UPDATE accounts SET balance = balance + 100 WHERE id = 2;  -- 等id=2的锁
-- 事务B
UPDATE accounts SET balance = balance - 50 WHERE id = 2;   -- 锁住id=2
UPDATE accounts SET balance = balance + 50 WHERE id = 1;   -- 等id=1的锁 → 死锁！
```
- 解决：InnoDB自动检测死锁，回滚其中一个事务
- 预防：按相同顺序访问资源（大家都先锁id=1再锁id=2）

#### 56.5 间隙锁（Gap Lock）
- InnoDB在REPEATABLE READ下防止幻读的机制
- 不仅锁住存在的行，还锁住行之间的间隙
- 比喻：锁的不只是储物柜，连柜子之间的空地也锁了，防止有人加塞
- `SELECT * FROM users WHERE id BETWEEN 10 AND 20 FOR UPDATE;`
  - 即使id=15不存在，这个间隙也会被锁住

#### 56.6 乐观锁 vs 悲观锁
- **悲观锁**：认为冲突经常发生，操作前先锁住
  - `SELECT FOR UPDATE` 然后操作
  - 比喻：进门前就把门锁上，以为一定会有人来抢
- **乐观锁**：认为冲突很少发生，更新时检查版本号
  - `UPDATE products SET stock=stock-1, version=version+1 WHERE id=1 AND version=5;`
  - 如果受影响行数为0，说明被人改过了，重试
  - 比喻：先不管门，等回来了发现东西被动过再说
- Go中乐观锁实现思路：用version字段或updated_at比较

---

### 第57章 · 数据库设计范式

#### 57.1 为什么需要范式
- 没有范式：数据冗余、更新异常、删除异常
- 比喻：一个学生表中重复存储了班级名称和班主任名字，班主任换了一个人就要改100个学生的记录
- 范式是数据库表设计的规范，目的是减少冗余、保证完整性

#### 57.2 第一范式（1NF）：字段不可再分
- 每个字段都是最小的原子单位
- 反例：`address`字段存"浙江省杭州市西湖区"三个信息混在一起
- 正例：拆成 `province`、`city`、`district` 三个字段
- 比喻：一个格子里只能放一件东西

#### 57.3 第二范式（2NF）：消除部分依赖
- 先决条件：满足1NF
- 非主键字段必须完全依赖于主键（不能只依赖主键的一部分）
- 反例：订单详情表主键是 (order_id, product_id)，product_name只依赖于product_id
- 正例：把产品信息拆到独立的product表中
- 比喻：一个订单的商品名应该去商品目录查，不应该在订单里重复写

#### 57.4 第三范式（3NF）：消除传递依赖
- 先决条件：满足2NF
- 非主键字段不能依赖于其他非主键字段
- 反例：学生表有 `class_id`、`class_name`、`head_teacher`，`head_teacher` 依赖于 `class_id` 而 `class_id` 依赖于主键
- 正例：`class_name` 和 `head_teacher` 放到独立的班级表中
- 比喻：你不要在每条学生记录里写班主任是谁，应该去班级表查

#### 57.5 反范式化（Denormalization）
- 有时为了提高查询性能，故意违反范式
- 比如：订单表里冗余存 `user_name`，避免每次都JOIN用户表
- 原则：读多写少的场景可以适当冗余
- 代价：数据可能不一致（用户改名了订单里的旧名字怎么办？）
- 比喻：为了快递员送货快，箱子上直接写地址，不做二次查询

#### 57.6 数据库设计实战步骤
1. **需求分析**：搞清楚系统要支持哪些业务
2. **画ER图**：用矩形表实体、菱形表关系、椭圆表属性
3. **确定实体和关系**：用户、订单、商品……以及它们的关系（一对一、一对多、多对多）
4. **设计表结构**：每张表有哪些字段，类型、约束
5. **应用范式**：检查并优化到3NF
6. **适当的反范式化**：根据查询场景权衡
7. **建立索引策略**：根据查询频率设计索引

#### 57.7 ER图绘制工具
- 推荐工具：Draw.io、dbdiagram.io、Navicat自带
- dbdiagram.io语法示例：
```
Table users {
  id int [pk]
  username varchar
}
Table orders {
  id int [pk]
  user_id int [ref: > users.id]
}
Ref: orders.user_id > users.id
```

---

### 第58章 · 数据库优化实战

#### 58.1 SQL优化总览
- 定位慢SQL → EXPLAIN分析 → 加索引/改写法 → 验证效果
- 优化层次：SQL语句 > 索引 > 表结构 > 数据库配置 > 硬件
- 比喻：车慢了先看是不是挂错挡（SQL），再看是不是轮胎没气（索引），最后才换发动机（硬件升级）

#### 58.2 常见SQL优化技巧
- **SELECT只取需要的列**：不要 `SELECT *`
- **用JOIN代替子查询**：子查询可能每行都执行一次
- **WHERE条件中用小表驱动大表**：把筛选性强的条件放前面
- **避免在WHERE子句中使用函数**：`WHERE DATE(created_at)='2024-01-01'` 不如 `WHERE created_at >= '2024-01-01' AND created_at < '2024-01-02'`
- **大批量插入用批量INSERT**：一次插入1000条比1000次单条快10倍+
- **用LIMIT限制返回行数**：避免返回百万行数据
- **分页优化**：深分页时用 `WHERE id > last_id LIMIT N` 代替 `LIMIT N OFFSET M`
- **COUNT优化**：`COUNT(*)` 和 `COUNT(1)` 性能一样，`COUNT(col)` 不统计NULL

#### 58.3 表结构优化
- **字段选最小够用的类型**：能用TINYINT不用INT
- **定长字段放前面，变长放后面**（MyISAM，InnoDB影响不大）
- **NOT NULL优于NULL**：NULL占额外空间，索引处理更复杂
- **垂直拆分**：把大字段（TEXT）和不常用字段独立出去
  ```
  users → user_profiles (bio TEXT, avatar_url TEXT)
  ```
- **水平拆分**：按时间或其他维度拆表
  ```
  orders_2023, orders_2024, orders_2025
  ```

#### 58.4 数据库配置优化
- `innodb_buffer_pool_size`：InnoDB缓存大小，建议设为物理内存的70%（专用服务器）
- `max_connections`：最大连接数，根据业务调整
- `query_cache_size`：查询缓存（MySQL 8.0已废弃，不推荐用）
- `slow_query_log`：开启慢查询日志

#### 58.5 读写分离
- 主库（Master）：负责写操作（INSERT/UPDATE/DELETE）
- 从库（Slave）：负责读操作（SELECT），可以有多个
- 好处：分担压力，读操作不阻塞写操作
- 实现：MySQL主从复制 + 应用层路由（写走主库，读走从库）
- 问题：主从延迟（主库写了从库还没同步到），敏感场景强制读主库

#### 58.6 分库分表
- 当单表数据量达到千万级别时考虑
- 垂直分库：按业务模块拆（用户库、订单库、商品库）
- 水平分表：把一张大表按规则拆成多张小表
  - 按范围：orders_0(id 1~1000万), orders_1(1000万~2000万)……
  - 按哈希：`id % 16` 分16张表
- 工具：ShardingSphere、MyCat，或应用层自己写路由

#### 58.7 连接池
- 数据库连接很昂贵（TCP连接+认证），不能每次请求都新建
- 连接池：预先创建一堆连接放在池子里，用时取，用完还
```go
// Go中使用连接池
db, _ := sql.Open("mysql", dsn)
db.SetMaxOpenConns(25)       // 最大连接数
db.SetMaxIdleConns(10)       // 最大空闲连接数
db.SetConnMaxLifetime(5 * time.Minute)  // 连接最大存活时间
```
- 比喻：连接池=共享单车，用完锁车就行不用自己买一辆

---

### 第59章 · Go操作MySQL（database/sql）

#### 59.1 database/sql是什么
- Go标准库提供的数据库操作抽象接口
- 定义了一套统一的API，不同数据库需要各自的驱动实现
- 比喻：database/sql = 万能遥控器接口，MySQL驱动=遥控器配的电池

#### 59.2 安装MySQL驱动
```bash
go get github.com/go-sql-driver/mysql
```
- 驱动通过 `import _ "github.com/go-sql-driver/mysql"` 匿名导入注册

#### 59.3 建立数据库连接
```go
import (
    "database/sql"
    _ "github.com/go-sql-driver/mysql"
)

func main() {
    dsn := "root:password@tcp(127.0.0.1:3306)/mydb?charset=utf8mb4&parseTime=true"
    db, err := sql.Open("mysql", dsn)
    if err != nil {
        panic(err)
    }
    defer db.Close()

    if err = db.Ping(); err != nil {
        panic(err)
    }
    // 连接池配置
    db.SetMaxOpenConns(25)
    db.SetMaxIdleConns(10)
    db.SetConnMaxLifetime(5 * time.Minute)
}
```
- DSN格式：`用户名:密码@tcp(地址:端口)/数据库名?参数`
- `parseTime=true`：把MySQL的DATETIME自动转为`time.Time`
- `sql.Open` 不一定立即连接，用 `Ping` 验证连接

#### 59.4 查询单行（QueryRow）
```go
type User struct {
    ID       int
    Username string
    Email    string
}

var user User
err := db.QueryRow("SELECT id, username, email FROM users WHERE id = ?", 1).
    Scan(&user.ID, &user.Username, &user.Email)
if err == sql.ErrNoRows {
    // 没有找到
} else if err != nil {
    // 其他错误
}
```
- 占位符 `?` 是防SQL注入的关键（不能用字符串拼接）

#### 59.5 查询多行（Query）
```go
rows, err := db.Query("SELECT id, username, email FROM users WHERE age > ?", 18)
if err != nil {
    return err
}
defer rows.Close()

var users []User
for rows.Next() {
    var u User
    if err := rows.Scan(&u.ID, &u.Username, &u.Email); err != nil {
        return err
    }
    users = append(users, u)
}
if err = rows.Err(); err != nil {
    return err
}
```
- **defer rows.Close() 必须写！** 否则连接不会释放
- 遍历完要检查 `rows.Err()`

#### 59.6 增删改（Exec）
```go
// INSERT
result, err := db.Exec("INSERT INTO users (username, email) VALUES (?, ?)", "张三", "zhangsan@a.com")
lastID, _ := result.LastInsertId()

// UPDATE
result, err = db.Exec("UPDATE users SET email=? WHERE id=?", "new@a.com", 1)
affected, _ := result.RowsAffected()

// DELETE
result, err = db.Exec("DELETE FROM users WHERE id=?", 1)
```
- `RowsAffected()` 返回受影响行数

#### 59.7 预处理语句（Prepared Statement）
```go
stmt, err := db.Prepare("SELECT id, username FROM users WHERE age > ?")
if err != nil {
    return err
}
defer stmt.Close()
rows, err := stmt.Query(18)
```
- Prepare将SQL预编译，重复执行时只传参数，效率高
- 比喻：填好的表格模板，每次只改数字

#### 59.8 事务操作
```go
tx, err := db.Begin()
if err != nil {
    return err
}
defer func() {
    if err != nil {
        tx.Rollback()
    }
}()
_, err = tx.Exec("UPDATE accounts SET balance=balance-100 WHERE id=?", 1)
if err != nil {
    return err
}
_, err = tx.Exec("UPDATE accounts SET balance=balance+100 WHERE id=?", 2)
if err != nil {
    return err
}
err = tx.Commit()
```
- 用defer处理回滚保证异常时一定回滚

#### 59.9 SQL注入与预防
```go
// 错误做法（SQL注入风险！）
query := "SELECT * FROM users WHERE username = '" + userInput + "'"
// 用户输入: ' OR '1'='1  → 查出所有用户

// 正确做法（参数化查询）
db.Query("SELECT * FROM users WHERE username = ?", userInput)
// 占位符自动转义，安全
```
- 比喻：参数化查询 = 你和仓库管理员说"找名字叫张三的"，而不是把门禁卡直接给路人

---

### 第60章 · GORM入门

#### 60.1 什么是ORM
- ORM = Object-Relational Mapping（对象关系映射）
- 把数据库表映射成Go的结构体，把SQL操作映射成方法调用
- 比喻：ORM = 翻译官，你说Go语言，他帮你翻译成SQL
- 优点：不用手写SQL、防注入、迁移方便
- 缺点：复杂查询不如原生SQL灵活、有性能开销

#### 60.2 GORM安装与连接
```bash
go get gorm.io/gorm
go get gorm.io/driver/mysql
```
```go
import (
    "gorm.io/gorm"
    "gorm.io/driver/mysql"
)

dsn := "root:password@tcp(127.0.0.1:3306)/mydb?charset=utf8mb4&parseTime=true"
db, err := gorm.Open(mysql.Open(dsn), &gorm.Config{})
```

#### 60.3 定义模型（Model）
```go
type User struct {
    ID        uint           `gorm:"primaryKey"`
    Username  string         `gorm:"uniqueIndex;size:50;not null"`
    Password  string         `gorm:"size:255;not null"`
    Email     *string        `gorm:"size:100;default:null"`  // 使用指针实现可空
    Age       uint8          `gorm:"default:0"`
    CreatedAt time.Time
    UpdatedAt time.Time
    DeletedAt gorm.DeletedAt `gorm:"index"`  // 软删除
}
```
- GORM约定优于配置：ID默认主键，CreatedAt/UpdatedAt自动管理
- `*string` 表示可以为NULL（string的零值是""不是NULL）
- `gorm.DeletedAt` 实现软删除

#### 60.4 自动迁移
```go
db.AutoMigrate(&User{})
```
- 根据Go结构体自动创建/更新表结构（生产环境慎用）
- 只会加表加字段，不会删已有的字段

#### 60.5 基本CRUD操作
```go
// Create
user := User{Username: "张三", Password: "xxx", Age: 25}
db.Create(&user)  // user.ID 会被回填

// Read
var user User
db.First(&user, 1)                  // 按主键
db.First(&user, "username = ?", "张三")  // 按条件
db.Where("age > ?", 20).Find(&users)    // 多条

// Update
db.Model(&user).Update("age", 26)                          // 单字段
db.Model(&user).Updates(User{Age: 26, Email: &email})      // 多字段（结构体）
db.Model(&user).Updates(map[string]interface{}{"age": 26}) // 多字段（零值也会更新）

// Delete
db.Delete(&user, 1)       // 软删除（有DeletedAt的话）
db.Unscoped().Delete(&user, 1)  // 物理删除
```
- Create会自动设置CreatedAt
- Save会更新所有字段，Updates只更新非零值字段

#### 60.6 链式查询
```go
db.Where("age > ?", 18).
    Where("status = ?", "active").
    Order("created_at desc").
    Limit(10).
    Offset(20).
    Find(&users)
```
- 每个方法都返回 `*gorm.DB`，可以一直链下去

#### 60.7 基本条件查询
```go
db.Where("username = ?", "张三").First(&user)          // 等值
db.Where("age BETWEEN ? AND ?", 18, 30).Find(&users)  // 范围
db.Where("username IN ?", []string{"张三","李四"}).Find(&users) // IN
db.Where("username LIKE ?", "%张%").Find(&users)      // LIKE
db.Not("age = ?", 18).Find(&users)                     // 不等于
db.Or("age = ?", 18).Find(&users)                      // OR
db.Where(&User{Age: 18, Username: "张三"}).Find(&users) // 结构体条件
```

---

### 第61章 · GORM进阶

#### 61.1 关联关系
```go
type User struct {
    ID     uint
    Orders []Order  // Has Many
}
type Order struct {
    ID     uint
    UserID uint    // 外键
    User   User    // Belongs To
}
```
- Has One：一个用户有一个身份证号
- Has Many：一个用户有多个订单
- Belongs To：一个订单属于一个用户
- Many To Many：一个学生选多门课，一门课有多个学生

#### 61.2 Preload预加载
```go
// 查出用户并带上他的所有订单
db.Preload("Orders").Find(&users)
// 条件预加载
db.Preload("Orders", "amount > ?", 100).Find(&users)
```
- 解决N+1问题：不预加载时查100个用户会产生1+100条SQL
- 比喻：预加载=一次性把菜谱和食材单都取来，而不是拿着菜谱去一次取一种食材

#### 61.3 事务
```go
err := db.Transaction(func(tx *gorm.DB) error {
    if err := tx.Create(&user).Error; err != nil {
        return err  // 返回错误自动回滚
    }
    if err := tx.Create(&order).Error; err != nil {
        return err
    }
    return nil  // 返回nil自动提交
})
```
- Transaction自动管理提交和回滚
- 手动事务：`tx := db.Begin()` → `tx.Commit()` / `tx.Rollback()`

#### 61.4 钩子（Hooks）
```go
func (u *User) BeforeCreate(tx *gorm.DB) error {
    u.Password = hashPassword(u.Password)
    return nil
}
func (u *User) AfterCreate(tx *gorm.DB) error {
    // 创建后的操作，比如发邮件通知
    return nil
}
```
- 可用钩子：BeforeCreate/AfterCreate、BeforeUpdate/AfterUpdate、BeforeDelete/AfterDelete、AfterFind
- 用途：密码加密、生成默认值、缓存刷新、审计日志

#### 61.5 原生SQL
```go
// 查询
db.Raw("SELECT id, username FROM users WHERE age > ?", 18).Scan(&users)
// 执行
db.Exec("UPDATE users SET status = ? WHERE age > ?", "vip", 50)
// 使用原生SQL时也能用结构体
db.Raw("SELECT * FROM users WHERE name = @Name", sql.Named("Name", "张三")).Scan(&users)
```

#### 61.6 Scopes（查询作用域）
```go
func ActiveUsers(db *gorm.DB) *gorm.DB {
    return db.Where("status = ?", "active")
}
func AdultUsers(db *gorm.DB) *gorm.DB {
    return db.Where("age >= ?", 18)
}

db.Scopes(ActiveUsers, AdultUsers).Find(&users)
```
- 把常用查询条件封装成可复用的函数

#### 61.7 分页封装
```go
func Paginate(page, pageSize int) func(db *gorm.DB) *gorm.DB {
    return func(db *gorm.DB) *gorm.DB {
        return db.Offset((page - 1) * pageSize).Limit(pageSize)
    }
}
db.Scopes(Paginate(2, 10)).Find(&users)
```

#### 61.8 性能优化
- 批量插入：`db.CreateInBatches(users, 100)`（每批100条）
- 关闭默认事务（单条Write时不需要）：
  ```go
  db, _ := gorm.Open(mysql.Open(dsn), &gorm.Config{
      SkipDefaultTransaction: true,
  })
  ```
- 使用读写分离：配置多个源，GORM根据操作自动选择

---

### 第62章 · Redis基础

#### 62.1 Redis是什么
- Redis（Remote Dictionary Server）是一个内存键值数据库
- 比喻：Redis不是仓库（硬盘），是你大脑中的便签纸（内存）
- 特点：极快（10万QPS+）、支持多种数据结构、有持久化能力
- 与MySQL的关系：MySQL存核心数据，Redis存热点数据/缓存/临时数据
- 比喻：MySQL是图书馆，Redis是你桌上的笔记本

#### 62.2 Redis适用场景
- **缓存**：热点数据/查询结果缓存，减轻MySQL压力
- **Session存储**：分布式下共享用户登录状态
- **计数器**：阅读量、点赞数（INCR很快）
- **排行榜**：Sorted Set天然支持排名
- **分布式锁**：SETNX实现简单互斥
- **消息队列**：List/Stream实现轻量级消息传递
- **限流**：滑动窗口/令牌桶的实现载体

#### 62.3 安装Redis
- Windows：下载Redis for Windows或使用Docker
  ```bash
  docker run -d --name redis -p 6379:6379 redis:7
  ```
- Linux：`sudo apt install redis-server` 或 `sudo yum install redis`
- 启动后 `redis-cli` 进入交互式命令行

#### 62.4 Redis基本数据模型
- 所有数据以 key-value 形式存储
- key是字符串，value可以是多种类型
- 设计key命名的约定：`项目名:模块名:ID:字段名`
  - `app:user:1001:profile`
  - `app:order:20240101:count`
- 比喻：每个key就像一个标签，通过标签瞬间找到内容

#### 62.5 Redis命令行体验
```bash
SET name "张三"        # 设置字符串
GET name               # 获取 -> "张三"
DEL name               # 删除
EXISTS name            # 是否存在
EXPIRE name 60         # 60秒后过期
TTL name               # 查看剩余过期时间
```

#### 62.6 内存淘汰策略
- 当Redis内存满了怎么办：
  - `noeviction`：报错（默认生产不推荐）
  - `allkeys-lru`：最近最少使用的淘汰（推荐）
  - `volatile-lru`：有过期时间的key中淘汰LRU
  - `allkeys-random`：随机淘汰
  - `volatile-ttl`：淘汰最快过期的
- 比喻：冰箱满了要把最久没吃的东西扔掉

#### 62.7 Redis持久化
- **RDB（快照）**：隔一段时间把内存数据全量写到磁盘
  - 优点：恢复快、文件紧凑
  - 缺点：可能丢最后几分钟的数据
- **AOF（日志）**：记录每一条写命令
  - 优点：数据安全性高、最多丢1秒数据
  - 缺点：文件大、恢复慢
- 比喻：RDB=定期给笔记本照相，AOF=每次写笔记都打一张复写纸
- 生产环境建议两者都开

---

### 第63章 · Redis数据类型与实战

#### 63.1 String（字符串）
- 最基本的类型：一个key对应一个字符串值
- 最大能存512MB
```bash
SET counter 0
INCR counter       # 原子递增 -> 1
INCRBY counter 10  # -> 11
DECR counter       # -> 10
SETNX lock owner   # 仅当key不存在时设置（分布式锁核心）
```
- 比喻：String就像脑中的一张便签，写什么都可以
- 应用场景：缓存JSON、计数器、分布式锁

#### 63.2 Hash（哈希表）
- 一个key下面可以有多个field-value对
```bash
HSET user:1001 name "张三" age "25" city "杭州"
HGET user:1001 name          # "张三"
HGETALL user:1001            # 全部field-value
HINCRBY user:1001 age 1      # age+1
```
- 比喻：Hash是一个"个人信息卡"，卡上有姓名、年龄等多个字段
- 应用场景：存储对象（如用户信息），比存一整个JSON String更灵活
- 底层实现：ziplist（小数据）或hashtable（大数据）

#### 63.3 List（列表）
- 有序的字符串列表，可以从两端操作
```bash
LPUSH queue "task1" "task2"    # 从左边插入
RPUSH queue "task3"             # 从右边插入
LPOP queue                      # 从左边取出
RPOP queue                      # 从右边取出
LLEN queue                      # 长度
LRANGE queue 0 -1               # 查看整个列表
```
- 比喻：List就像一条传送带，东西只能从两端放入或取出
- 应用场景：消息队列（生产者LPUSH，消费者RPOP）、最新消息列表

#### 63.4 Set（集合）
- 无序、不重复的字符串集合
```bash
SADD tags:article:1 "Go" "Redis" "MySQL"
SADD tags:article:2 "Go" "Docker"
SINTER tags:article:1 tags:article:2    # 交集 -> {"Go"}
SUNION tags:article:1 tags:article:2    # 并集
SDIFF tags:article:1 tags:article:2     # 差集
SISMEMBER tags:article:1 "Go"           # 判断是否在集合中
```
- 比喻：Set就是一个不允许重复的名单
- 应用场景：标签系统、共同好友、抽奖去重
- 底层实现：整数集合（intset）或哈希表

#### 63.5 Sorted Set（有序集合）
- Set的基础上每个元素带一个分数，按分数排序
```bash
ZADD leaderboard 95 "张三" 88 "李四" 90 "王五"
ZRANGE leaderboard 0 -1          # 按分数升序
ZREVRANGE leaderboard 0 -1       # 按分数降序
ZRANK leaderboard "张三"         # 张三的排名（从0开始）
ZSCORE leaderboard "张三"        # 张三的分数
ZINCRBY leaderboard 5 "张三"     # 加分
```
- 比喻：Sorted Set就是排行榜，分数定了排名自动就好
- 应用场景：排行榜、延迟队列（score存时间戳）、附近的人（存经纬度）
- 底层实现：ziplist（小数据）或skiplist+hashtable

#### 63.6 其他数据类型
- **Bitmap**：位图，适合做签到、在线状态
  ```bash
  SETBIT user:1001:checkin 0 1   # 第0天签到
  BITCOUNT user:1001:checkin     # 签到总天数
  ```
- **HyperLogLog**：基数统计，内存极小但误差约0.81%
  ```bash
  PFADD uv:20240101 "user1" "user2"
  PFCOUNT uv:20240101           # 统计UV
  ```
- **Geospatial**：地理位置
  ```bash
  GEOADD cities 120.15 30.28 "杭州"
  GEODIST cities "杭州" "上海" km  # 计算距离
  ```
- **Stream**：消息队列（Redis 5.0+），支持消费者组、消息确认

---

### 第64章 · Go操作Redis（go-redis）

#### 64.1 go-redis安装
```bash
go get github.com/redis/go-redis/v9
```

#### 64.2 建立连接
```go
import "github.com/redis/go-redis/v9"

rdb := redis.NewClient(&redis.Options{
    Addr:     "localhost:6379",
    Password: "",
    DB:       0,       // 默认db
})
// 测试连接
ctx := context.Background()
pong, err := rdb.Ping(ctx).Result()
fmt.Println(pong)  // "PONG"
```

#### 64.3 String操作
```go
// SET
err := rdb.Set(ctx, "key", "value", 10*time.Minute).Err()
// GET
val, err := rdb.Get(ctx, "key").Result()
// GET + SET（原子操作）
oldVal, err := rdb.GetSet(ctx, "key", "newValue").Result()
// SETNX
ok, err := rdb.SetNX(ctx, "lock", "1", 30*time.Second).Result()
// INCR
newVal, err := rdb.Incr(ctx, "counter").Result()
// MGET 批量获取
vals, err := rdb.MGet(ctx, "key1", "key2", "key3").Result()
```

#### 64.4 Hash操作
```go
rdb.HSet(ctx, "user:1001", map[string]interface{}{
    "name": "张三",
    "age":  25,
})
name, _ := rdb.HGet(ctx, "user:1001", "name").Result()
all, _ := rdb.HGetAll(ctx, "user:1001").Result()
rdb.HIncrBy(ctx, "user:1001", "age", 1)
```

#### 64.5 List操作
```go
rdb.LPush(ctx, "queue", "task1", "task2")
task, _ := rdb.RPop(ctx, "queue").Result()
list, _ := rdb.LRange(ctx, "queue", 0, -1).Result()
```

#### 64.6 Set操作
```go
rdb.SAdd(ctx, "tags:article:1", "Go", "Redis")
members, _ := rdb.SMembers(ctx, "tags:article:1").Result()
isMember, _ := rdb.SIsMember(ctx, "tags:article:1", "Go").Result()
```

#### 64.7 Sorted Set操作
```go
rdb.ZAdd(ctx, "leaderboard", redis.Z{Score: 95, Member: "张三"})
top3, _ := rdb.ZRevRangeWithScores(ctx, "leaderboard", 0, 2).Result()
rank, _ := rdb.ZRank(ctx, "leaderboard", "张三").Result()
```

#### 64.8 Pipeline（管道）
```go
pipe := rdb.Pipeline()
pipe.Set(ctx, "key1", "val1", 0)
pipe.Set(ctx, "key2", "val2", 0)
pipe.Incr(ctx, "counter")
_, err := pipe.Exec(ctx)
```
- 把多个命令打包一次发送，减少网络往返
- 比喻：Pipeline=一次性把一周要买的东西列清单给采购，而不是每天跑一趟

#### 64.9 分布式锁实现
```go
// 加锁
lockKey := "lock:order:123"
ok, err := rdb.SetNX(ctx, lockKey, "unique_value", 30*time.Second).Result()
if !ok {
    return errors.New("获取锁失败")
}
defer func() {
    // 用Lua脚本安全释放锁（判断是否是自己的锁）
    luaScript := `
        if redis.call("GET", KEYS[1]) == ARGV[1] then
            return redis.call("DEL", KEYS[1])
        else
            return 0
        end
    `
    rdb.Eval(ctx, luaScript, []string{lockKey}, "unique_value")
}()
// 业务逻辑...
```

#### 64.10 缓存穿透/击穿/雪崩
- **缓存穿透**：查一个不存在的key，每次都穿透到MySQL
  - 解决：用布隆过滤器或缓存空值（短过期时间）
- **缓存击穿**：热点key过期瞬间大量请求直达MySQL
  - 解决：加分布式锁，让只有一个请求去查MySQL并重建缓存
- **缓存雪崩**：大量key同时过期，MySQL压力暴增
  - 解决：过期时间加随机值（TTL + rand），做多级缓存

#### 64.11 Redis集群简介
- 主从复制：一主多从，读写分离
- 哨兵模式（Sentinel）：自动故障转移，主挂了从顶上
- Cluster模式：数据分片，多主节点分摊存储和请求压力
- 比喻：主从=一个师傅带几个学徒，Cluster=开几家分店

---

## 第四篇：Web框架与API开发

---

### 第65章 · RESTful API设计

#### 65.1 什么是API
- API = Application Programming Interface（应用程序编程接口）
- 比喻：API就是餐厅的菜单——告诉你能点什么、怎么点、点了会得到什么
- 后端提供的API：定义URL、请求方法和参数、返回的数据格式

#### 65.2 什么是RESTful
- REST = Representational State Transfer（表现层状态转移）
- 一种约定俗成的API设计风格，不是协议
- 核心理念：把一切看作资源（Resource），用HTTP方法操作资源
- 比喻：每个URL就像一个名词（/users 表示用户资源），HTTP方法是动词（GET=看, POST=新建, PUT=修改全量, DELETE=删除）

#### 65.3 HTTP方法与RESTful映射
| HTTP方法 | 含义 | REST操作 | 例子 |
|---------|------|---------|------|
| GET | 获取 | 读 | GET /users/1 |
| POST | 创建 | 增 | POST /users |
| PUT | 全量更新 | 改（全量） | PUT /users/1 |
| PATCH | 部分更新 | 改（部分） | PATCH /users/1 |
| DELETE | 删除 | 删 | DELETE /users/1 |

- 比喻：GET=看货，POST=进货，PUT=换货，DELETE=退货

#### 65.4 URL设计规范
- 资源用复数名词：`/users` 而不是 `/getUsers`
- 层级关系用路径表示：`/users/123/orders`（用户123的订单）
- 避免深层嵌套（最多3层）
- 查询参数用于筛选：`/users?age=18&status=active`
- 版本号放在URL或Header：`/api/v1/users` 或 `Accept: application/vnd.api+json;version=1`

#### 65.5 状态码的正确使用
| 状态码 | 含义 | 使用场景 |
|--------|------|---------|
| 200 | OK | GET/PUT/PATCH成功 |
| 201 | Created | POST创建成功 |
| 204 | No Content | DELETE成功（无返回体） |
| 400 | Bad Request | 请求参数有误 |
| 401 | Unauthorized | 未登录/未认证 |
| 403 | Forbidden | 已登录但权限不够 |
| 404 | Not Found | 资源不存在 |
| 409 | Conflict | 资源冲突（如用户名重复） |
| 422 | Unprocessable Entity | 参数语法正确但语义不对 |
| 500 | Internal Server Error | 服务器内部错误 |

#### 65.6 统一响应格式
```json
{
    "code": 200,
    "message": "success",
    "data": {
        "id": 1,
        "username": "张三"
    }
}
```
- 错误响应：
```json
{
    "code": 400,
    "message": "用户名不能为空",
    "data": null
}
```
- 统一格式让前端能一致地处理所有接口

#### 65.7 RESTful的局限与GraphQL
- RESTful问题：获取用户列表时想同时知道用户的订单数，需要查两个接口或接口返回冗余
- GraphQL：由前端定义要什么数据，一个请求精确获取
- 本书聚焦RESTful（目前最主流），GraphQL作了解

---

### 第66章 · Gin框架入门

#### 66.1 什么是Gin
- Gin是Go语言最流行的Web框架（GitHub 70k+ Star）
- 特点：轻量、高性能、中间件生态丰富
- 路由基于Radix Tree（基数树），匹配速度极快
- 比喻：net/http标准库 = 毛坯房，Gin = 精装公寓

#### 66.2 安装Gin
```bash
go get github.com/gin-gonic/gin
```

#### 66.3 第一个Gin程序
```go
package main

import (
    "net/http"
    "github.com/gin-gonic/gin"
)

func main() {
    r := gin.Default()
    r.GET("/ping", func(c *gin.Context) {
        c.JSON(http.StatusOK, gin.H{
            "message": "pong",
        })
    })
    r.Run(":8080") // 默认监听 0.0.0.0:8080
}
```
- `gin.Default()` 带Logger和Recovery中间件
- `c.JSON()` 自动设置Content-Type为application/json

#### 66.4 路由注册
```go
// GET请求
r.GET("/users", getUsers)
r.GET("/users/:id", getUser)       // 路径参数
r.GET("/users/:id/orders", getUserOrders)

// POST请求
r.POST("/users", createUser)
r.POST("/users/:id/avatar", uploadAvatar)

// PUT和DELETE
r.PUT("/users/:id", updateUser)
r.DELETE("/users/:id", deleteUser)

// 匹配任何方法
r.Any("/ping", handler)
```

#### 66.5 获取请求参数
```go
// 路径参数
r.GET("/users/:id", func(c *gin.Context) {
    id := c.Param("id")       // /users/123 → id = "123"
})

// Query参数
r.GET("/users", func(c *gin.Context) {
    page := c.DefaultQuery("page", "1")
    keyword := c.Query("keyword")
    // /users?page=2&keyword=张三
})

// 表单参数
r.POST("/login", func(c *gin.Context) {
    username := c.PostForm("username")
    password := c.PostForm("password")
})
```

#### 66.6 返回响应
```go
// JSON
c.JSON(http.StatusOK, gin.H{"user": user})

// 纯文本
c.String(http.StatusOK, "Hello %s", name)

// XML
c.XML(http.StatusOK, gin.H{"user": user})

// 文件
c.File("./file.pdf")

// 重定向
c.Redirect(http.StatusMovedPermanently, "https://example.com")
```

---

### 第67章 · Gin路由与中间件

#### 67.1 路由分组
```go
v1 := r.Group("/api/v1")
{
    v1.GET("/users", listUsers)
    v1.POST("/users", createUser)
}

v2 := r.Group("/api/v2")
{
    v2.GET("/users", listUsersV2)
}

// 嵌套分组
admin := r.Group("/admin")
{
    admin.GET("/dashboard", adminDashboard)
    admin.GET("/users", adminListUsers)
}
```
- 路由分组方便统一管理、添加中间件
- 比喻：路由分组=不同的部门，每个部门有自己的办事窗口

#### 67.2 中间件是什么
- 中间件是在请求到达处理函数之前和之后执行的代码
- 比喻：中间件就像安检——所有游客进景区前都要过安检（认证、日志、限流等）
- Gin的中间件是一个 `gin.HandlerFunc`
```go
func Logger() gin.HandlerFunc {
    return func(c *gin.Context) {
        t := time.Now()
        c.Next()  // 执行下一个处理
        latency := time.Since(t)
        fmt.Printf("请求耗时: %v\n", latency)
    }
}
```

#### 67.3 全局中间件
```go
r := gin.New()
r.Use(gin.Logger())      // 日志
r.Use(gin.Recovery())    // 异常恢复（防止panic导致服务挂掉）
r.Use(corsMiddleware)    // 跨域
```

#### 67.4 路由组中间件
```go
auth := r.Group("/api")
auth.Use(AuthMiddleware())  // 这个组的所有路由都需要认证
{
    auth.GET("/profile", profile)
    auth.POST("/orders", createOrder)
}
```

#### 67.5 c.Next() vs c.Abort()
```go
func AuthMiddleware() gin.HandlerFunc {
    return func(c *gin.Context) {
        token := c.GetHeader("Authorization")
        if token == "" {
            c.JSON(http.StatusUnauthorized, gin.H{"error": "未登录"})
            c.Abort()  // 不执行后续处理，直接返回
            return
        }
        c.Set("userID", parseUserID(token))  // 把用户信息存入上下文
        c.Next()  // 继续执行
    }
}
```
- `c.Next()`：放行，继续下一个中间件/处理函数
- `c.Abort()`：拦截，直接返回，不再往后执行

#### 67.6 中间件的执行顺序
- 洋葱模型：请求进来 → 中间件1前 → 中间件2前 → 处理函数 → 中间件2后 → 中间件1后 → 响应返回
- 比喻：就像剥洋葱，一层层进去，再一层层出来

#### 67.7 常用第三方中间件
- `gin-contrib/cors`：跨域处理
- `gin-contrib/sessions`：Session管理
- `gin-contrib/gzip`：响应压缩
- `gin-contrib/pprof`：性能分析
- `gin-contrib/ratelimit`：限流

---

### 第68章 · 请求参数绑定与校验

#### 68.1 参数绑定
```go
type CreateUserReq struct {
    Username string `json:"username" binding:"required"`
    Password string `json:"password" binding:"required,min=6"`
    Email    string `json:"email"    binding:"required,email"`
    Age      int    `json:"age"      binding:"gte=0,lte=120"`
}

r.POST("/users", func(c *gin.Context) {
    var req CreateUserReq
    if err := c.ShouldBindJSON(&req); err != nil {
        c.JSON(400, gin.H{"error": err.Error()})
        return
    }
    // req已被填充，可以直接使用
})
```
- `ShouldBindJSON`：自动把JSON请求体绑定到结构体
- `ShouldBindQuery`：绑定URL查询参数
- `ShouldBindUri`：绑定路径参数
- `ShouldBind`：根据Content-Type自动选择绑定方式

#### 68.2 内置校验规则
```go
type Req struct {
    Field string `binding:"required"`           // 必填
    Name  string `binding:"required,min=2,max=20"` // 长度
    Email string `binding:"required,email"`      // 邮箱格式
    URL   string `binding:"url"`                 // URL格式
    Age   int    `binding:"gte=0,lte=120"`       // >=0且<=120
    Tags  []string `binding:"required,min=1,dive,min=1"` // dive=深入数组元素校验
}
```
- 常用标签：`required`、`min`、`max`、`len`、`eq`、`ne`、`gt`、`gte`、`lt`、`lte`、`oneof`、`email`、`url`、`ip`

#### 68.3 自定义校验器
```go
import "github.com/go-playground/validator/v10"

var validate *validator.Validate

func init() {
    validate = validator.New()
    validate.RegisterValidation("is-cool", func(fl validator.FieldLevel) bool {
        return fl.Field().String() == "cool"
    })
}

type Req struct {
    Status string `json:"status" binding:"required,is-cool"`
}
```

#### 68.4 中文错误信息
```go
func translate(err error) string {
    var errs validator.ValidationErrors
    if errors.As(err, &errs) {
        for _, e := range errs {
            switch e.Tag() {
            case "required":
                return fmt.Sprintf("%s 是必填项", e.Field())
            case "min":
                return fmt.Sprintf("%s 长度不能小于 %s", e.Field(), e.Param())
            case "email":
                return "邮箱格式不正确"
            }
        }
    }
    return err.Error()
}
```

#### 68.5 参数校验最佳实践
- 前端做友好提示性校验（用户体验）
- 后端做安全的强校验（安全底线，不能信任前端）
- **永远不要信任客户端传来的任何数据**
- 比喻：前端校验=门迎微笑提醒你穿正装，后端校验=安检门只认数据

---

### 第69章 · 响应处理与错误码

#### 69.1 统一响应结构设计
```go
type Response struct {
    Code    int         `json:"code"`
    Message string      `json:"message"`
    Data    interface{} `json:"data,omitempty"`
}

func Success(c *gin.Context, data interface{}) {
    c.JSON(http.StatusOK, Response{
        Code:    0, // 0表示成功
        Message: "success",
        Data:    data,
    })
}

func Error(c *gin.Context, code int, message string) {
    c.JSON(http.StatusOK, Response{ // HTTP状态码仍然200，业务错误码在Body里
        Code:    code,
        Message: message,
    })
}
```

#### 69.2 错误码设计
```go
const (
    // 通用错误 10000-10099
    ErrParamInvalid  = 10001  // 参数错误
    ErrInternal      = 10002  // 内部错误

    // 用户模块 10100-10199
    ErrUserNotFound  = 10101  // 用户不存在
    ErrUserExists    = 10102  // 用户已存在
    ErrPasswordWrong = 10103  // 密码错误

    // 订单模块 10200-10299
    ErrOrderNotFound = 10201
    ErrOrderPaid     = 10202
)
```
- 按模块分段，方便定位问题
- 不要复用同一个错误码表达不同的含义

#### 69.3 分页响应
```go
type PageResponse struct {
    List     interface{} `json:"list"`
    Total    int64       `json:"total"`
    Page     int         `json:"page"`
    PageSize int         `json:"page_size"`
}
```
- 统一的分页格式，前端能直接渲染分页组件

#### 69.4 全局错误处理中间件
```go
func ErrorHandler() gin.HandlerFunc {
    return func(c *gin.Context) {
        c.Next()
        if len(c.Errors) > 0 {
            err := c.Errors.Last()
            c.JSON(http.StatusOK, Response{
                Code:    10002,
                Message: err.Error(),
            })
        }
    }
}
```

#### 69.5 Panic恢复
- `gin.Recovery()` 已内置panic恢复
- 自定义Recovery可以记录更详细的错误信息（堆栈、请求参数）
- 比喻：Recovery就是安全网，杂技演员（代码）摔下来不至于砸到地面（导致整个服务挂掉）

---

### 第70章 · Go项目结构规范

#### 70.1 标准项目布局
```
myapp/
├── cmd/
│   └── server/
│       └── main.go           # 程序入口
├── internal/                 # 私有代码（不可被外部import）
│   ├── handler/              # HTTP处理层（Controller）
│   │   ├── user_handler.go
│   │   └── order_handler.go
│   ├── service/              # 业务逻辑层
│   │   ├── user_service.go
│   │   └── order_service.go
│   ├── repository/           # 数据访问层（DAO）
│   │   ├── user_repo.go
│   │   └── order_repo.go
│   ├── model/                # 数据模型
│   │   ├── user.go
│   │   └── order.go
│   └── middleware/           # 中间件
│       ├── auth.go
│       └── logger.go
├── pkg/                      # 可被外部import的公共库
│   ├── response/             # 统一响应
│   └── errcode/              # 错误码
├── config/                   # 配置文件
│   └── config.yaml
├── docs/                     # API文档
├── migrations/               # 数据库迁移
├── scripts/                  # 构建/部署脚本
├── go.mod
├── go.sum
└── Makefile
```

#### 70.2 分层架构
```
┌─────────────────────┐
│   Handler 层         │  ← 处理HTTP请求/响应，参数校验
│  （表现层/Controller）│
├─────────────────────┤
│   Service 层         │  ← 核心业务逻辑，事务边界
│  （业务逻辑层）       │
├─────────────────────┤
│   Repository 层      │  ← 数据库CRUD，缓存操作
│  （数据访问层）       │
├─────────────────────┤
│   Model 层           │  ← 数据结构定义
│  （模型层）           │
└─────────────────────┘
```
- 每层只依赖下一层，不允许跨层调用
- 比喻：Handler=服务员，Service=厨师，Repository=仓库管理员，Model=菜谱

#### 70.3 依赖注入模式
```go
// 不使用依赖注入（耦合）
type UserService struct{}
func (s *UserService) GetUser(id int) (*User, error) {
    db, _ := sql.Open("mysql", dsn) // 每次都创建连接
    // ...
}

// 使用构造器注入（推荐）
type UserService struct {
    repo *UserRepository
}
func NewUserService(repo *UserRepository) *UserService {
    return &UserService{repo: repo}
}
func (s *UserService) GetUser(id int) (*User, error) {
    return s.repo.FindByID(id)
}
```

#### 70.4 配置管理
- 用YAML/TOML/JSON配置文件，不要硬编码
- 用Viper库管理配置（支持多种格式、环境变量覆盖）
```go
import "github.com/spf13/viper"

viper.SetConfigName("config")
viper.SetConfigType("yaml")
viper.AddConfigPath("./config")
viper.ReadInConfig()

dbHost := viper.GetString("database.host")
```

#### 70.5 internal vs pkg
- `internal/`：Go编译器保证外部项目无法import，强制达到封装效果
- `pkg/`：可以被外部引用的公共代码
- 绝大部分业务代码应该放在 `internal/`

---

### 第71章 · 日志系统

#### 71.1 为什么需要日志
- 日志是后端的"黑匣子"——出问题时唯一的线索
- 比喻：日志就像监控录像，出了事能回放当时发生了什么
- 没有日志 = 闭着眼睛写代码，出问题只能靠猜

#### 71.2 日志等级
- **DEBUG**：调试信息（开发环境用，生产关掉）
- **INFO**：关键流程节点（请求进入、操作成功等）
- **WARN**：警告（不影响功能但有风险，如接近限流阈值）
- **ERROR**：错误（影响当前请求，但服务没挂）
- **FATAL**：致命错误（服务要挂了）

#### 71.3 Go标准库log
```go
import "log"

log.Println("这是一条日志")
log.Printf("用户 %s 登录成功", username)
log.Fatalf("数据库连接失败: %v", err)  // 打印后调用os.Exit(1)
```

#### 71.4 logrus（流行选择）
```go
import log "github.com/sirupsen/logrus"

func init() {
    log.SetFormatter(&log.JSONFormatter{})  // JSON格式（生产推荐）
    log.SetLevel(log.InfoLevel)              // 只有Info以上才输出
    log.SetOutput(os.Stdout)
}

log.WithFields(log.Fields{
    "user_id": 123,
    "action":  "login",
}).Info("用户登录成功")

log.WithError(err).Error("数据库查询失败")
```
- JSON格式方便被日志系统（ELK/Loki）解析

#### 71.5 zap（高性能选择）
```go
import "go.uber.org/zap"

logger, _ := zap.NewProduction()
defer logger.Sync()

logger.Info("用户登录成功",
    zap.Int("user_id", 123),
    zap.String("action", "login"),
)
```
- zap的性能是logrus的数倍（零内存分配）
- 比喻：logrus是家用轿车，zap是F1赛车

#### 71.6 Gin集成日志
```go
func GinLogger(logger *zap.Logger) gin.HandlerFunc {
    return func(c *gin.Context) {
        start := time.Now()
        path := c.Request.URL.Path
        c.Next()
        latency := time.Since(start)
        logger.Info("请求日志",
            zap.Int("status", c.Writer.Status()),
            zap.String("method", c.Request.Method),
            zap.String("path", path),
            zap.Duration("latency", latency),
            zap.String("client_ip", c.ClientIP()),
        )
    }
}
```

#### 71.7 日志最佳实践
- 生产环境日志必须输出到标准输出（stdout），由容器/日志平台收集
- 不要在日志中打印密码、token等敏感信息
- 每条日志带上 trace_id / request_id，方便串起一次请求的全部日志
- 不要滥用ERROR级别（用户参数错误是业务预期，应该INFO/WARN）

---

### 第72章 · 配置管理

#### 72.1 为什么要做配置管理
- 代码和配置分离是基本原则：代码只负责逻辑，配置负责参数
- 比喻：代码就是菜谱步骤，配置就是"盐放多少、火多大"
- 不同环境（开发/测试/生产）配置不同但代码一样

#### 72.2 Viper库详解
```go
import "github.com/spf13/viper"

func initConfig() {
    viper.SetConfigName("config")    // 文件名（不含扩展名）
    viper.SetConfigType("yaml")      // 格式
    viper.AddConfigPath("./config")  // 搜索路径
    // 也支持环境变量
    viper.AutomaticEnv()
    // 环境变量绑定
    viper.BindEnv("database.host", "DB_HOST")

    if err := viper.ReadInConfig(); err != nil {
        panic(fmt.Errorf("读取配置失败: %w", err))
    }
}
```

#### 72.3 配置文件示例
```yaml
# config/config.yaml
server:
  port: 8080
  mode: release  # debug | release | test

database:
  host: localhost
  port: 3306
  user: root
  password: ${DB_PASSWORD}  # 敏感信息用环境变量
  name: mydb

redis:
  addr: localhost:6379
  db: 0

jwt:
  secret: ${JWT_SECRET}
  expire_hours: 24

log:
  level: info
  format: json
```

#### 72.4 结构体映射
```go
type Config struct {
    Server   ServerConfig   `mapstructure:"server"`
    Database DatabaseConfig `mapstructure:"database"`
    Redis    RedisConfig    `mapstructure:"redis"`
    JWT      JWTConfig      `mapstructure:"jwt"`
}

var cfg Config
viper.Unmarshal(&cfg)  // 自动映射到结构体
```

#### 72.5 环境变量优先级
- Viper的优先级（从高到低）：
  1. 显式调用的 `Set`
  2. 命令行参数（需要pflag配合）
  3. 环境变量
  4. 配置文件
  5. 默认值

#### 72.6 热更新
- 部分场景需要不重启就更新配置
```go
viper.WatchConfig()
viper.OnConfigChange(func(e fsnotify.Event) {
    fmt.Println("配置已更新:", e.Name)
    viper.Unmarshal(&cfg)
})
```

#### 72.7 敏感信息管理
- 数据库密码、API密钥等不应该写在配置文件里提交到Git
- 用环境变量注入：`${DB_PASSWORD}`
- 更成熟的方案：Vault、AWS Secrets Manager
- `.env` 文件只用于本地开发，不要提交到Git

---

### 第73章 · Swagger文档生成

#### 73.1 为什么需要API文档
- API文档就是你的接口说明书，前后端联调的基础
- 比喻：没有API文档就像给了别人一台机器但不给说明书
- Swagger/OpenAPI是目前最通用的API文档标准

#### 73.2 Swagger是什么
- Swagger是一套API文档工具，基于OpenAPI规范
- 能自动生成交互式API文档页面
- 比喻：Swagger就是"会自己更新的产品说明书"

#### 73.3 Go中生成Swagger文档（swaggo）
```bash
go install github.com/swaggo/swag/cmd/swag@latest
```

#### 73.4 添加注解
```go
// @title          用户管理系统API
// @version        1.0
// @description    这是一个用户管理系统的API文档
// @host           localhost:8080
// @BasePath       /api/v1

// @Summary        获取用户列表
// @Description    分页获取所有用户
// @Tags           用户管理
// @Accept         json
// @Produce        json
// @Param          page     query    int    false  "页码"     default(1)
// @Param          size     query    int    false  "每页数量" default(10)
// @Success        200  {object}  Response{data=PageResponse}  "成功"
// @Failure        400  {object}  Response  "参数错误"
// @Router         /users [get]
func ListUsers(c *gin.Context) {
    // ...
}
```

#### 73.5 生成文档
```bash
swag init -g cmd/server/main.go -o docs
```
- 生成 `docs/` 目录下的文档文件
- 在代码中导入：`import _ "myapp/docs"`

#### 73.6 集成到Gin
```go
import (
    swaggerFiles "github.com/swaggo/files"
    ginSwagger "github.com/swaggo/gin-swagger"
)

r.GET("/swagger/*any", ginSwagger.WrapHandler(swaggerFiles.Handler))
```
- 访问 `http://localhost:8080/swagger/index.html` 即可看到交互式文档

#### 73.7 Swagger文档的最佳实践
- 每个接口都要写清晰的描述（不是只写一个标题）
- 参数要注明是否必填、格式要求
- 列出来所有可能的响应状态码
- 代码变更后及时 `swag init` 重新生成

---

### 第74章 · CORS与跨域处理

#### 74.1 什么是跨域
- 浏览器的同源策略：一个源（协议+域名+端口）的脚本不能访问另一个源的资源
- 比喻：你家（前端域）的保姆不能直接去邻居家（后端域）拿东西，除非邻居同意（CORS头）
- 跨域只存在于浏览器端，后端之间调用不受限制（服务器之间不存在跨域）

#### 74.2 CORS是什么
- CORS = Cross-Origin Resource Sharing（跨域资源共享）
- 一种机制，让服务器告诉浏览器：我允许哪些来源来访问我
- 实现方式：后端在响应头里加特殊字段

#### 74.3 关键响应头
```
Access-Control-Allow-Origin: https://example.com  或 *
Access-Control-Allow-Methods: GET, POST, PUT, DELETE
Access-Control-Allow-Headers: Content-Type, Authorization
Access-Control-Allow-Credentials: true
Access-Control-Max-Age: 86400  (预检请求缓存时间)
```
- `Allow-Origin` 为 `*` 时不能同时 `Allow-Credentials: true`

#### 74.4 简单请求与预检请求
- **简单请求**：GET/HEAD/POST + 有限几种Content-Type → 直接发请求
- **预检请求**（Preflight）：PUT/DELETE/自定义头等 → 先发OPTIONS预检，通过了再发真正请求
- 比喻：简单请求=熟人直接进，预检请求=陌生人要先报备

#### 74.5 Gin中处理CORS
```go
import "github.com/gin-contrib/cors"

r.Use(cors.New(cors.Config{
    AllowOrigins:     []string{"http://localhost:3000", "https://example.com"},
    AllowMethods:     []string{"GET", "POST", "PUT", "DELETE", "OPTIONS"},
    AllowHeaders:     []string{"Origin", "Content-Type", "Authorization"},
    ExposeHeaders:    []string{"Content-Length"},
    AllowCredentials: true,
    MaxAge:           12 * time.Hour,
}))
```

#### 74.6 自定义CORS中间件
```go
func CORSMiddleware() gin.HandlerFunc {
    return func(c *gin.Context) {
        c.Header("Access-Control-Allow-Origin", "*")
        c.Header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        c.Header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        if c.Request.Method == "OPTIONS" {
            c.AbortWithStatus(http.StatusNoContent)
            return
        }
        c.Next()
    }
}
```

---

### 第75章 · 文件上传与下载

#### 75.1 文件上传实现
```go
r.POST("/upload", func(c *gin.Context) {
    file, err := c.FormFile("file")
    if err != nil {
        c.JSON(400, gin.H{"error": "文件上传失败"})
        return
    }
    // 限制文件大小
    if file.Size > 10*1024*1024 { // 10MB
        c.JSON(400, gin.H{"error": "文件大小不能超过10MB"})
        return
    }
    // 存储文件
    dst := "./uploads/" + file.Filename
    if err := c.SaveUploadedFile(file, dst); err != nil {
        c.JSON(500, gin.H{"error": "文件保存失败"})
        return
    }
    c.JSON(200, gin.H{"url": "/uploads/" + file.Filename})
})
```

#### 75.2 多文件上传
```go
form, _ := c.MultipartForm()
files := form.File["files"]  // 前端用相同的字段名传多个文件
for _, file := range files {
    c.SaveUploadedFile(file, "./uploads/"+file.Filename)
}
```

#### 75.3 文件类型校验
```go
// 检查MIME类型
contentType := file.Header.Get("Content-Type")
if contentType != "image/png" && contentType != "image/jpeg" {
    c.JSON(400, gin.H{"error": "只允许上传png/jpeg图片"})
    return
}
```
- **永远不要信任文件扩展名**，要检查Content-Type

#### 75.4 文件下载
```go
r.GET("/download/:filename", func(c *gin.Context) {
    filename := c.Param("filename")
    c.File("./uploads/" + filename)  // Gin自动处理Content-Type
})

// 强制下载（而不是浏览器预览）
r.GET("/download/:filename", func(c *gin.Context) {
    filename := c.Param("filename")
    c.Header("Content-Disposition", fmt.Sprintf("attachment; filename=%s", filename))
    c.File("./uploads/" + filename)
})
```

#### 75.5 静态文件服务
```go
r.Static("/uploads", "./uploads")  // /uploads/xxx → 本地 ./uploads/xxx
r.StaticFS("/assets", http.Dir("./public"))
```

#### 75.6 对象存储
- 生产环境文件通常不放在服务器本地（磁盘有限、多实例共享麻烦）
- 使用对象存储服务（阿里云OSS、AWS S3、MinIO）
- MinIO自建对象存储：
```go
import "github.com/minio/minio-go/v7"

client, _ := minio.New("localhost:9000", &minio.Options{
    Creds: credentials.NewStaticV4("accessKey", "secretKey", ""),
})
client.PutObject(ctx, "mybucket", "filename.jpg", reader, size, minio.PutObjectOptions{})
```
- 比喻：本地存文件=把文件放自己抽屉里，对象存储=把文件存到专业的文件仓库

---

### 第76章 · API版本管理

#### 76.1 为什么要做API版本管理
- 上线后的API不能随便改（有客户端在用）
- 要加新功能或改旧接口 → 新开一个版本
- 比喻：API版本就像软件版本号，v1.0和v2.0可以并存，老用户继续用v1

#### 76.2 URL路径版本（最常见）
```
/api/v1/users
/api/v2/users
```
- 最简单直观
- 缺点：URL中混杂版本信息，不够RESTful纯

#### 76.3 Header版本
```
Accept: application/vnd.myapp.v1+json
```
- 更RESTful
- 缺点：客户端不好调试（URL都一样）

#### 76.4 查询参数版本
```
/api/users?version=1
```
- 简单但不够优雅

#### 76.5 Gin中实现版本管理
```go
v1 := r.Group("/api/v1")
{
    v1.GET("/users", handlerV1.ListUsers)
    v1.POST("/users", handlerV1.CreateUser)
}

v2 := r.Group("/api/v2")
{
    v2.GET("/users", handlerV2.ListUsers)      // V2返回格式不同
    v2.POST("/users", handlerV2.CreateUser)    // V2支持新字段
}
```

#### 76.6 版本兼容策略
- 永远不要删接口，只标记为deprecated
- 废弃的接口响应头加 `Deprecation: true` 和 `Sunset: 日期`
- 给客户端足够的缓冲时间来迁移
- 比喻：拆旧楼前要先贴通知、设围挡，给居民搬家时间

#### 76.7 API文档的版本管理
- Swagger中每个版本单独生成文档
- v1文档地址：`/swagger/v1/index.html`
- v2文档地址：`/swagger/v2/index.html`

---

## 第五篇：认证授权与安全

---

### 第77章 · 认证基础：Session与Cookie

#### 77.1 认证 vs 授权
- **认证（Authentication）**：你是谁？→ 登录验证身份
- **授权（Authorization）**：你能干什么？→ 权限控制
- 比喻：认证=刷门禁卡认出你是员工，授权=不同部门门禁卡能开不同门

#### 77.2 HTTP的无状态特性
- HTTP协议本身不记得上个请求是谁发的
- 比喻：HTTP像一个失忆的服务员，每次你点菜他都忘了你是谁
- 需要额外的机制来维持"会话"状态

#### 77.3 Cookie是什么
- 浏览器端存储的小数据（最多4KB）
- 服务器通过 `Set-Cookie` 响应头设置
- 浏览器之后每次请求都会自动带上Cookie
```go
c.SetCookie("username", "张三", 3600, "/", "localhost", false, true)
// 参数: name, value, maxAge(秒), path, domain, secure, httpOnly
```
- 比喻：Cookie就像餐厅给你的号码牌，每次来给服务员看就行

#### 77.4 Session是什么
- 服务器端存储的会话数据
- 用户登录后，服务器创建Session，把Session ID存入Cookie
- 之后用户每次请求带上Session ID，服务器就能找到对应的Session
- 比喻：Session=餐厅后台系统里的"台号-订单"记录，号码牌=Session ID

#### 77.5 Session实现流程
1. 用户登录，服务器验证用户名密码
2. 服务器创建Session（存用户信息），生成Session ID
3. Session ID通过Cookie返回给浏览器
4. 浏览器以后每次请求都带上这个Cookie
5. 服务器根据Session ID找到Session，确认用户身份
6. 用户登出，服务器删除Session

#### 77.6 Session的问题
- 服务器需要存储所有Session（占内存）
- 多服务器时Session不共享（需要存Redis解决）
- CORS场景下Cookie不容易处理

---

### 第78章 · JWT认证

#### 78.1 JWT是什么
- JWT = JSON Web Token（JSON格式的令牌）
- 自包含的：Token本身就携带了用户信息，不用查数据库
- 比喻：JWT像一个盖了章的身份证，不用每次都去派出所查，看到章就知道是真的
- 格式：`Header.Payload.Signature`（三部分用`.`分隔）

#### 78.2 JWT的结构
```
eyJhbGciOiJIUzI1NiJ9.eyJ1c2VySWQiOjEsImV4cCI6MTcwMDAwMDAwMH0.signature
|______ Header ______|_______ Payload ___________|__ Signature __|
```
- **Header**：加密算法、Token类型
  ```json
  {"alg": "HS256", "typ": "JWT"}
  ```
- **Payload**：携带的数据（用户ID、过期时间等）
  ```json
  {"user_id": 1, "exp": 1700000000, "iat": 1699900000}
  ```
- **Signature**：对前两部分 + 密钥的签名，防篡改

#### 78.3 JWT vs Session
| 对比维度 | JWT | Session |
|---------|-----|---------|
| 存储位置 | 客户端（浏览器） | 服务器端 |
| 扩展性 | 天然支持分布式 | 需要共享Session存储 |
| 注销 | 比较麻烦（要黑名单） | 直接删Session |
| 安全性 | Token泄露后有风险 | Cookie httpOnly更安全 |

#### 78.4 Go中生成JWT（golang-jwt）
```bash
go get github.com/golang-jwt/jwt/v5
```
```go
type Claims struct {
    UserID uint   `json:"user_id"`
    jwt.RegisteredClaims
}

func GenerateToken(userID uint, secret string) (string, error) {
    claims := Claims{
        UserID: userID,
        RegisteredClaims: jwt.RegisteredClaims{
            ExpiresAt: jwt.NewNumericDate(time.Now().Add(24 * time.Hour)),
            IssuedAt:  jwt.NewNumericDate(time.Now()),
            Issuer:    "myapp",
        },
    }
    token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)
    return token.SignedString([]byte(secret))
}
```

#### 78.5 验证JWT
```go
func ParseToken(tokenString string, secret string) (*Claims, error) {
    token, err := jwt.ParseWithClaims(tokenString, &Claims{},
        func(token *jwt.Token) (interface{}, error) {
            return []byte(secret), nil
        })
    if err != nil {
        return nil, err
    }
    if claims, ok := token.Claims.(*Claims); ok && token.Valid {
        return claims, nil
    }
    return nil, errors.New("invalid token")
}
```

#### 78.6 Gin中JWT中间件
```go
func JWTAuth(secret string) gin.HandlerFunc {
    return func(c *gin.Context) {
        authHeader := c.GetHeader("Authorization")
        if authHeader == "" || !strings.HasPrefix(authHeader, "Bearer ") {
            c.AbortWithStatusJSON(401, gin.H{"error": "未提供认证令牌"})
            return
        }
        tokenString := authHeader[7:]  // 去掉 "Bearer "
        claims, err := ParseToken(tokenString, secret)
        if err != nil {
            c.AbortWithStatusJSON(401, gin.H{"error": "令牌无效或已过期"})
            return
        }
        c.Set("userID", claims.UserID)
        c.Next()
    }
}
```

#### 78.7 刷新Token（Refresh Token）
- Access Token：短期有效（15分钟），频繁使用
- Refresh Token：长期有效（7天/30天），只用于获取新Access Token
- 比喻：Access Token=酒店房卡（每天换），Refresh Token=身份证（用来换房卡）
- Access Token泄露危害有限（短期内失效）

#### 78.8 JWT安全最佳实践
- Secret Key 必须足够长（至少256位）且严格保密
- 敏感信息不要存在Payload中（Payload是Base64编码，不是加密！）
- Token过期时间不宜过长（15分钟~2小时）
- 使用HTTPS传输，防止Token被拦截
- 登出逻辑：客户端删除Token即可（服务端可加黑名单但违背JWT无状态理念）

---

### 第79章 · OAuth2.0

#### 79.1 什么是OAuth2.0
- OAuth2.0是一个授权框架，让第三方应用在用户授权后获取有限访问权限
- 比喻：你去酒店入住，前台给你一张房卡——只能开你的房间，不能去其他房间，退房就失效
- 典型场景："使用微信登录"、"使用GitHub登录"

#### 79.2 OAuth2.0的四个角色
- **Resource Owner**：资源所有者（用户本人）
- **Client**：第三方应用（要访问资源的一方）
- **Authorization Server**：认证服务器（微信/GitHub的认证服务）
- **Resource Server**：资源服务器（存用户数据的地方）

#### 79.3 四种授权模式
1. **授权码模式（Authorization Code）**：最常用、最安全，适用于有后端的应用
2. **隐式模式（Implicit）**：适用于纯前端应用（已不推荐）
3. **密码模式（Password Credentials）**：用户直接把用户名密码给Client（仅限信任应用）
4. **客户端模式（Client Credentials）**：服务端之间调用

#### 79.4 授权码模式流程
```
用户 → 点击"微信登录" → 跳转微信授权页 → 用户同意 → 
微信返回授权码(code) → 你的后端用code换access_token → 
用access_token获取用户信息
```
- 比喻：去政府办事大厅 → 机器取号 → 出示身份证 → 拿号 → 窗口凭号办事

#### 79.5 Go中实现OAuth2.0客户端
```go
import "golang.org/x/oauth2"

conf := &oauth2.Config{
    ClientID:     "your-client-id",
    ClientSecret: "your-client-secret",
    RedirectURL:  "http://localhost:8080/auth/callback",
    Scopes:       []string{"user:email"},
    Endpoint: oauth2.Endpoint{
        AuthURL:   "https://github.com/login/oauth/authorize",
        TokenURL:  "https://github.com/login/oauth/access_token",
    },
}

// 生成授权URL
url := conf.AuthCodeURL("random-state", oauth2.AccessTypeOnline)
// 跳转到这个URL

// 用code换token
token, err := conf.Exchange(ctx, code)
client := conf.Client(ctx, token)  // 用token创建一个http.Client
```

#### 79.6 OAuth2.0 vs 普通登录
- OAuth2.0是"委托授权"，我不告诉你密码但允许你访问我的某些数据
- 普通登录是"身份认证"，我知道你是谁
- 两者经常结合：用OAuth2.0获取第三方身份，然后在本系统创建一个账户

---

### 第80章 · RBAC权限控制

#### 80.1 什么是RBAC
- RBAC = Role-Based Access Control（基于角色的访问控制）
- 三大实体：用户（User）→ 角色（Role）→ 权限（Permission）
- 比喻：公司里 — 你是员工（User），你的岗位是"会计"（Role），你能"查账""做账"但不能"发布代码"（Permission）

#### 80.2 RBAC数据库设计
```sql
-- 用户表
CREATE TABLE users (
    id       INT PRIMARY KEY,
    username VARCHAR(50)
);
-- 角色表
CREATE TABLE roles (
    id   INT PRIMARY KEY,
    name VARCHAR(20) UNIQUE  -- admin, editor, viewer
);
-- 权限表
CREATE TABLE permissions (
    id   INT PRIMARY KEY,
    code VARCHAR(50) UNIQUE  -- user:read, user:write, order:delete
);
-- 关联表
CREATE TABLE user_roles (user_id INT, role_id INT);
CREATE TABLE role_permissions (role_id INT, permission_id INT);
```
- 用户和角色多对多，角色和权限多对多

#### 80.3 Go中实现RBAC中间件
```go
func RequirePermission(permCode string) gin.HandlerFunc {
    return func(c *gin.Context) {
        userID := c.GetUint("userID")
        hasPermission, err := checkPermission(userID, permCode)
        if err != nil || !hasPermission {
            c.AbortWithStatusJSON(403, gin.H{"error": "没有权限"})
            return
        }
        c.Next()
    }
}

// 使用
admin := r.Group("/admin")
admin.Use(JWTAuth(secret))
{
    admin.GET("/users", RequirePermission("user:read"), listUsers)
    admin.DELETE("/users/:id", RequirePermission("user:delete"), deleteUser)
}
```

#### 80.4 权限的粒度控制
- 粗粒度：角色级别（/admin/* 整体控制）
- 细粒度：操作级别（/users GET和/users DELETE分开控制）
- 数据级别：用户只能看自己的数据（这个要在业务代码中判断 owner_id）
- 比喻：粗粒度=能进哪个房间，细粒度=能开哪个柜子，数据级别=只能看自己的柜子

#### 80.5 Casbin权限框架
```go
import "github.com/casbin/casbin/v2"

e, _ := casbin.NewEnforcer("model.conf", "policy.csv")
// model.conf 定义权限模型
// [request_definition]
// r = sub, obj, act
// [policy_definition]
// p = sub, obj, act
// [policy_effect]
// e = some(where (p.eft == allow))
// [matchers]
// m = r.sub == p.sub && keyMatch(r.obj, p.obj) && regexMatch(r.act, p.act)

// 检查权限
ok, _ := e.Enforce("张三", "/users/1", "read")
```
- Casbin支持RBAC/ABAC/ACL等多种模型，灵活强大

---

### 第81章 · SQL注入防护

#### 81.1 什么是SQL注入
- 攻击者把恶意SQL代码混入输入中，让数据库执行非预期操作
- 比喻：你写"找叫张三的用户"，攻击者写"找叫张三的用户，顺便把所有管理员密码改成123456"
- 后果：数据泄露、数据篡改、账号被盗、甚至删库

#### 81.2 SQL注入示例
```go
// 危险代码
username := c.Query("username")  // 用户输入: ' OR '1'='1
query := "SELECT * FROM users WHERE username = '" + username + "'"
// 拼出来的SQL: SELECT * FROM users WHERE username = '' OR '1'='1'
// 结果：返回所有用户！
```
```go
// 更危险的输入: '; DROP TABLE users; --
// 拼出来: SELECT * FROM users WHERE username = ''; DROP TABLE users; --'
// 如果数据库支持多语句执行，表就没了！
```

#### 81.3 参数化查询（防注入的根本手段）
```go
// 安全代码
db.Query("SELECT * FROM users WHERE username = ?", username)
```
- 占位符把SQL结构和数据彻底分开，数据库不会把数据当SQL执行
- 比喻：占位符就是"先交模板再填空"，而不是"把模板和内容混在一起写"

#### 81.4 GORM的防护
```go
// 安全（参数化）
db.Where("username = ?", username).Find(&users)
db.Raw("SELECT * FROM users WHERE username = ?", username).Scan(&users)

// 危险（直接拼接）
db.Where("username = '" + username + "'").Find(&users) // 千万不要这样做！
```
- GORM的大部分方法都使用了参数化查询
- 危险的是自己拼SQL字符串

#### 81.5 其他防护措施
- 数据库用户最小权限原则：应用连接用有限的账号（不给DROP/ALTER权限）
- 输入校验：限制字符类型和长度
- 存储敏感数据用哈希而不是明文
- WAF（Web应用防火墙）

---

### 第82章 · XSS与CSRF防护

#### 82.1 XSS（跨站脚本攻击）
- 攻击者在网页中注入恶意脚本，其他用户浏览时脚本被执行
- 比喻：有人在公共留言板上贴了"自动偷看别人密码的代码"而不是留言
- 类型：
  - **存储型XSS**：恶意代码存在数据库里（如用户昵称存`<script>...</script>`）
  - **反射型XSS**：恶意代码在URL参数中，服务器直接拼到页面里
  - **DOM型XSS**：前端JS处理用户输入时产生

#### 82.2 XSS防护
- **输出转义**：把`<`变成`&lt;`，防止浏览器当成HTML执行
- Go的 `html/template` 自动转义：
  ```go
  import "html/template"
  tmpl.Execute(w, data)  // 自动转义，安全
  ```
- 后端API返回JSON时，前端要正确处理（React的JSX默认转义）
- CSP（Content Security Policy）：HTTP头告诉浏览器只能从哪些源加载资源

#### 82.3 CSRF（跨站请求伪造）
- 攻击者诱导用户点击链接，借用用户的登录态发起恶意请求
- 比喻：你登录了网银，然后点了一个钓鱼链接，那个链接悄悄发起了一笔转账（用的是你的登录状态）
- 前提：Cookie自动携带、登录状态存在Cookie中

#### 82.4 CSRF防护
- **CSRF Token**：服务器生成随机Token，放在表单中，提交时校验
- **Referer/Origin检查**：检查请求来源是否是自己的站点
- **SameSite Cookie**：`Set-Cookie: session=xxx; SameSite=Strict` → 跨站请求不发送Cookie
- **双重验证**：敏感操作（转账/改密码）要求输入密码或验证码

#### 82.5 Go中的CSRF防护
```go
import "github.com/gin-contrib/sessions"
import "github.com/gorilla/csrf"

// 在模板中放入CSRF Token
c.HTML(200, "form.html", gin.H{
    "csrfToken": csrf.Token(c.Request),
})

// 表单提交
<input type="hidden" name="gorilla.csrf.Token" value="{{ .csrfToken }}">
```
- 对于前后端分离的SPA应用，使用Token（JWT）而不是Cookie可从根本上避免CSRF

---

### 第83章 · 密码加密与存储

#### 83.1 密码存储的红线
- **绝对不能明文存储密码！**
- 比喻：存密码明文 = 把所有用户的家门钥匙串起来挂在公司门口
- 即使被拖库，黑客反推不出密码
- 即使内部人员也看不到用户原始密码

#### 83.2 哈希算法
- 哈希：把任意长度的输入变成固定长度的输出
- 特点：单向不可逆、相同的输入一定相同的输出、雪崩效应（改一个bit输出完全不同）
```go
import "crypto/sha256"
hash := sha256.Sum256([]byte("mypassword"))
// 99f6b72e4c8b0c6e0b94b2de41c0e3c4f4b2a7f8d6b3e5c1a9f0d7e2b3a4c5d6
```
- **SHA256不够安全！** 速度快意味着攻击者可以暴力破解，而且彩虹表攻击能反查

#### 83.3 加盐（Salt）
- 盐：每个用户一个随机字符串，拼在密码后面一起哈希
- 作用1：相同密码产生不同的哈希值
- 作用2：防止彩虹表攻击
- 即使两个用户密码都是"123456"，加不同盐后哈希完全不同

#### 83.4 bcrypt（推荐）
```go
import "golang.org/x/crypto/bcrypt"

// 加密
hashedPassword, err := bcrypt.GenerateFromPassword([]byte("mypassword"), bcrypt.DefaultCost)
// DefaultCost = 10，计算越慢（cost越大）越难暴力破解

// 验证
err = bcrypt.CompareHashAndPassword(hashedPassword, []byte("mypassword"))
if err == nil {
    // 密码正确
}
```
- bcrypt内置了盐，每次加密结果都不同
- cost = 10 时大约需要 100ms，这恰恰是优点——拖慢了暴力破解
- 比喻：bcrypt = 自带随机调味料的慢炖锅，哈希就是慢慢炖出来的菜

#### 83.5 bcrypt的存储
```sql
-- 密码字段要足够长
password_hash VARCHAR(255) NOT NULL
-- bcrypt输出固定60字节: $2a$10$...总共60字符
```

#### 83.6 密码策略
- 最小长度8位（推荐12位以上）
- 不要强制复杂的特殊字符组合（用户会烦，而且`P@ssw0rd!`并不安全）
- 检查密码是否在已知泄露密码库中（Have I Been Pwned API）
- 限制登录失败次数（防暴力破解）
- 密码重置链接有时效性（15-30分钟）

---

### 第84章 · HTTPS与安全通信

#### 84.1 HTTP为什么不安全
- HTTP是明文传输，所有数据裸奔在网络上
- 比喻：HTTP = 写了一张明信片寄出去，邮递员/中间人都能看到内容
- 中间人攻击：攻击者劫持通信，偷看和篡改数据

#### 84.2 HTTPS是什么
- HTTPS = HTTP + TLS（Transport Layer Security，传输层安全协议）
- 数据加密传输，即使被拦截也看不懂
- 比喻：HTTPS = 把明信片装进一个锁着的保险箱寄出去

#### 84.3 TLS握手过程
1. 客户端发送支持的加密套件列表
2. 服务器选择加密套件 + 发证书（含公钥）
3. 客户端验证证书 → 生成会话密钥 → 用服务器公钥加密 → 发给服务器
4. 服务器用私钥解密得到会话密钥
5. 之后双方用对称加密（会话密钥）通信
- 比喻：客户和商店先确认密码本（握手），之后所有的信都加密

#### 84.4 SSL/TLS证书
- 证书 = 网站的身份证，由CA（证书颁发机构）签发
- 包含：域名、公钥、有效期、颁发机构签名
- Let's Encrypt：免费的SSL证书，每90天续期
- 自签名证书：自己签的，浏览器不信任（仅测试用）

#### 84.5 Go中启用HTTPS
```go
// 生产环境
r.RunTLS(":443", "/path/to/cert.pem", "/path/to/key.pem")

// 使用Let's Encrypt自动管理证书
import "golang.org/x/crypto/acme/autocert"
m := autocert.Manager{
    Prompt: autocert.AcceptTOS,
    Cache:  autocert.DirCache("./certs"),
}
server := &http.Server{
    Addr:      ":443",
    TLSConfig: m.TLSConfig(),
}
server.ListenAndServeTLS("", "")
```

#### 84.6 生产环境通常的做法
- Nginx/Caddy 做HTTPS终端（SSL termination）
- Go应用监听HTTP（Nginx在前面处理HTTPS）
- Caddy特别推荐：自动申请和续期Let's Encrypt证书，零配置
```
myapp.example.com {
    reverse_proxy localhost:8080
}
```

#### 84.7 安全HTTP头
```go
func SecureHeaders() gin.HandlerFunc {
    return func(c *gin.Context) {
        c.Header("X-Content-Type-Options", "nosniff")
        c.Header("X-Frame-Options", "DENY")
        c.Header("X-XSS-Protection", "1; mode=block")
        c.Header("Strict-Transport-Security", "max-age=31536000; includeSubDomains")
        c.Next()
    }
}
```
- HSTS（Strict-Transport-Security）：告诉浏览器只能用HTTPS访问

---

## 第六篇：消息队列与异步处理

---

### 第85章 · 消息队列基础概念

#### 85.1 什么是消息队列
- 消息队列 = 一个暂存消息的中间件，生产者发消息，消费者收消息
- 比喻：消息队列就像快递中转站——寄件人（生产者）把快递放到中转站，收件人（消费者）从中转站取件
- 生产者和消费者不需要同时在线，也不需要知道彼此

#### 85.2 为什么需要消息队列
- **解耦**：订单系统不用直接调用短信系统，发一条消息到队列就行
- **异步**：耗时操作（发邮件、生成报表）不用让用户等
- **削峰**：秒杀请求到队列排队，慢慢处理，避免冲垮服务
- **可靠性**：消费者挂了，消息不丢，等服务恢复后继续处理

#### 85.3 消息队列的核心概念
- **Producer**：生产者，发送消息的一方
- **Consumer**：消费者，接收并处理消息的一方
- **Broker**：消息代理（中间件），存消息并转发
- **Queue**：队列，消息存储的地方
- **Topic**：主题，发布/订阅模式中的消息分类
- **Exchange**：交换机（RabbitMQ概念），负责把消息路由到队列

#### 85.4 消息模式
- **点对点（Queue）**：一条消息只有一个消费者处理
  - 比喻：快递只给一个人
- **发布订阅（Pub/Sub）**：一条消息所有订阅者都收到
  - 比喻：微信公众号，所有关注者都看到推送
- **请求/回复（RPC）**：消费者处理完返回结果

#### 85.5 常见的消息队列中间件
| 中间件 | 特点 | 适用场景 |
|--------|------|---------|
| RabbitMQ | 功能完善、路由灵活 | 企业应用、复杂路由 |
| Kafka | 超高吞吐、持久化 | 大数据、日志收集 |
| Redis | 轻量、简单 | 轻量异步任务 |
| RocketMQ | 阿里出品、事务消息 | 电商场景 |

#### 85.6 消息可靠性的三个保证
- **至多一次（At Most Once）**：消息可能丢，但不会重复
- **至少一次（At Least Once）**：消息不会丢，但可能重复（需要消费者做幂等）
- **精确一次（Exactly Once）**：消息不丢不重（最难实现，Kafka支持但有限制）
- 大多数场景选"至少一次" + 消费者幂等处理

---

### 第86章 · RabbitMQ快速上手

#### 86.1 RabbitMQ是什么
- 基于AMQP协议的消息中间件，Erlang语言编写
- 核心角色：Producer → Exchange → Queue → Consumer
- 比喻：Exchange是邮局分拣中心（负责把信按规则发送到对应信箱），Queue是每个人的信箱

#### 86.2 安装RabbitMQ
```bash
# Docker方式（推荐）
docker run -d --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3-management
# 5672: AMQP协议端口  15672: 管理界面端口
```
- 访问 `http://localhost:15672` 用 guest/guest 登录管理界面

#### 86.3 交换机（Exchange）的类型
- **Direct**：精确匹配 routing key
  - `key="order.created"` → 只发到绑定key为 `order.created` 的队列
- **Topic**：通配符匹配 routing key
  - `key="order.created.success"` → 匹配 `order.*.*` 或 `order.created.*`
- **Fanout**：广播，无视routing key，所有绑定的队列都收到
  - 比喻：大喇叭喊，所有人都听到
- **Headers**：根据消息头匹配（不常用）

#### 86.4 用AMQP库连接RabbitMQ
```bash
go get github.com/rabbitmq/amqp091-go
```

```go
conn, err := amqp.Dial("amqp://guest:guest@localhost:5672/")
defer conn.Close()
ch, err := conn.Channel()
defer ch.Close()

// 声明队列
queue, err := ch.QueueDeclare(
    "order_queue", // 队列名
    true,          // durable（持久化）
    false,         // autoDelete
    false,         // exclusive
    false,         // noWait
    nil,           // args
)

// 发送消息
err = ch.PublishWithContext(ctx,
    "",               // exchange（空=默认exchange）
    queue.Name,       // routing key
    false,            // mandatory
    false,            // immediate
    amqp.Publishing{
        ContentType: "application/json",
        Body:        []byte(`{"order_id": 123}`),
    },
)

// 接收消息
msgs, err := ch.Consume(
    queue.Name, // queue
    "",         // consumer tag
    false,      // autoAck（手动确认）
    false,      // exclusive
    false,      // noLocal
    false,      // noWait
    nil,
)

go func() {
    for msg := range msgs {
        processMessage(msg.Body)
        msg.Ack(false)  // 手动确认
    }
}()
```

#### 86.5 消息确认机制（ACK）
- `autoAck = true`：RabbitMQ发出消息就认为成功了（可能丢失）
- `autoAck = false`：消费者处理完后手动 `msg.Ack()`，没ACK前消息不会丢
- `msg.Nack(false, true)`：处理失败，要求重新入队
- 比喻：ACK=收快递时签字确认，没签字快递员不会走

#### 86.6 消息持久化
```go
// 队列持久化
ch.QueueDeclare("order_queue", true, false, false, false, nil)
// 消息持久化
ch.PublishWithContext(ctx, "", queue.Name, false, false, amqp.Publishing{
    DeliveryMode: amqp.Persistent,  // 消息持久化到磁盘
    Body:         msgBody,
})
```
- 即使用持久化也有极小概率丢失（消息还在内存中没来得及刷磁盘），但足够大多数场景

---

### 第87章 · RabbitMQ高级特性

#### 87.1 Qos（质量服务）——公平分发
```go
// 设置每次只给消费者一条消息，处理完ACK后再给下一条
ch.Qos(
    1,     // prefetchCount: 每次预取数量
    0,     // prefetchSize: 0=不限制大小
    false, // global
)
```
- 没有Qos时RabbitMQ轮转分发，快的和慢的消费者拿到一样多
- 有Qos后，处理快的消费者能拿到更多消息（能者多劳）
- 比喻：没有Qos=轮流发传单不管谁快，有Qos=谁发完给谁下一叠

#### 87.2 死信队列（DLX）
- 死信：消息被拒绝（Nack且不重新入队）、消息过期（TTL）、队列满了
- 死信可以被转发到另一个交换机（死信交换机）和队列（死信队列）
- 用途：记录失败消息、延时重试、异常告警
- 比喻：死信队列=快递无人认领存放区

#### 87.3 延时队列
- RabbitMQ没有内置延时队列，可以用死信+TTL实现
- 消息发到A队列（无消费者），设置TTL（如30秒）
- TTL到期后变成死信 → 死信交换机转发到B队列（有消费者）
- 结果：消息延迟了30秒才被处理
- 应用场景：订单30分钟未支付自动取消

#### 87.4 发布确认（Publisher Confirm）
```go
// 开启发布确认模式
ch.Confirm(false)
confirms := ch.NotifyPublish(make(chan amqp.Confirmation, 1))

// 发布消息
ch.PublishWithContext(ctx, "", queue.Name, false, false, msg)

// 等待确认
if confirmed := <-confirms; confirmed.Ack {
    // 消息已到达Broker，放心了
} else {
    // 消息丢失，重新发送
}
```
- 比喻：发快递要求签回执单，确认仓库已收到

#### 87.5 连接重连机制
```go
func connect() (*amqp.Connection, *amqp.Channel) {
    for {
        conn, err := amqp.Dial(rabbitMQURL)
        if err == nil {
            return conn, conn.Channel()
        }
        time.Sleep(5 * time.Second)
    }
}
```
- 生产环境必须处理连接断开、自动重连

---

### 第88章 · Kafka基础

#### 88.1 Kafka是什么
- 分布式消息平台（不只是一个消息队列），由LinkedIn开发，Apache顶级项目
- 设计目标是高吞吐、持久化、分布式
- 比喻：RabbitMQ是精密的邮局系统，Kafka是超级高速公路
- 核心：单机10万+ QPS、消息存磁盘而不是内存、支持回溯

#### 88.2 Kafka核心概念
- **Producer**：生产者，向某个Topic发消息
- **Consumer**：消费者，从Topic读消息
- **Consumer Group**：消费者组，组内消费者分摊一个Topic的分区
- **Broker**：Kafka服务器节点
- **Topic**：消息的分类，像一个文件夹
- **Partition**：Topic的分区，分布在不同Broker上，是Kafka扩展性的核心
- **Offset**：消息在分区中的位置编号，消费者自己记录读到哪了

#### 88.3 为什么Kafka这么快
- **顺序写磁盘**：比随机写快得多，顺序写速度接近写内存
- **零拷贝（Zero Copy）**：数据直接从磁盘到网卡，不经过用户态
- **PageCache**：利用操作系统文件缓存
- **批量处理**：消息打包发送和消费
- 比喻：传送带上一个接一个放货物（顺序写），比满地乱放再找（随机写）快一百倍

#### 88.4 安装Kafka
```bash
# docker-compose方式
version: '3'
services:
  zookeeper:
    image: wurstmeister/zookeeper
    ports:
      - "2181:2181"
  kafka:
    image: wurstmeister/kafka
    ports:
      - "9092:9092"
    environment:
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_ADVERTISED_HOST_NAME: localhost
```
- Kafka依赖ZooKeeper管理集群元数据（3.3.1+可脱离ZooKeeper用KRaft模式）

#### 88.5 Topic与Partition
- 一个Topic可以有多个Partition（分区数量在创建时设定）
- 消息按key或轮询分配到一个Partition
- 一个Partition内的消息是严格有序的
- 不同Partition间不保证全局有序
- 比喻：Topic=高速路，Partition=车道，每个车道内的车顺序在走

#### 88.6 Consumer Group消费模型
- 同一Consumer Group内的消费者分摊Partition（不能超过Partition数）
- 不同Consumer Group独立消费（互不影响）
- 比喻：一组人（Consumer Group）分看几个监控画面（Partition），另一组人独立地也能看相同的画面

---

### 第89章 · Kafka进阶

#### 89.1 Kafka消息可靠性
- **acks=0**：Producer不等确认就认为成功（最快，可能丢）
- **acks=1**：Leader副本确认就认为成功
- **acks=all（或-1）**：所有ISR副本确认（最安全）
- **min.insync.replicas**：最少几个副本确认才算成功
- 生产环境推荐：acks=all + min.insync.replicas=2 + replication.factor=3

#### 89.2 消息幂等性
- `enable.idempotence=true`：Kafka保证Producer消息不重复（通过PID+序列号）
- 消费者的幂等自己去保证：记录offset或用数据库唯一键

#### 89.3 消息回溯
- 与RabbitMQ不同，Kafka消息消费后不删除（按时间或大小淘汰）
- 消费者可以重置Offset重新消费历史消息
- 比喻：Kafka像行车记录仪（可以回看历史），RabbitMQ像监控（实时看，过了就没了）

#### 89.4 Kafka常用命令
```bash
# 创建Topic
kafka-topics.sh --create --topic order-topic --bootstrap-server localhost:9092 --partitions 3 --replication-factor 1

# 查看Topic
kafka-topics.sh --list --bootstrap-server localhost:9092

# 生产者发送消息
kafka-console-producer.sh --topic order-topic --bootstrap-server localhost:9092

# 消费者消费消息
kafka-console-consumer.sh --topic order-topic --from-beginning --bootstrap-server localhost:9092
```

#### 89.5 Kafka Connect与Streams
- **Kafka Connect**：连接外部系统（MySQL→Kafka、Kafka→ES）的预制连接器
- **Kafka Streams**：在Kafka内部做流处理的库（过滤、聚合、join）
- 这是Kafka从消息队列到数据平台的底气

---

### 第90章 · Go集成消息队列

#### 90.1 Kafka Go客户端选型
- **Sarama**：最成熟的Kafka Go客户端（功能全面但API复杂）
- **kafka-go（segmentio）**：更Go风格的API、性能好、推荐
- **confluent-kafka-go**：Confluent官方，底层是C库librdkafka（性能最高但需要CGO）

#### 90.2 kafka-go生产者
```bash
go get github.com/segmentio/kafka-go
```
```go
writer := &kafka.Writer{
    Addr:     kafka.TCP("localhost:9092"),
    Topic:    "order-topic",
    Balancer: &kafka.LeastBytes{},  // 负载均衡策略
}

err := writer.WriteMessages(ctx,
    kafka.Message{
        Key:   []byte("order-123"),
        Value: []byte(`{"order_id": 123, "status": "created"}`),
    },
)
```

#### 90.3 kafka-go消费者
```go
reader := kafka.NewReader(kafka.ReaderConfig{
    Brokers:     []string{"localhost:9092"},
    Topic:       "order-topic",
    GroupID:     "order-consumer-group",
    StartOffset: kafka.LastOffset,  // 从最新开始
    MinBytes:    10e3,  // 10KB
    MaxBytes:    10e6,  // 10MB
})

for {
    msg, err := reader.ReadMessage(ctx)
    if err != nil {
        break
    }
    handleMessage(msg.Value)
}
```

#### 90.4 RabbitMQ Go客户端最佳实践
```go
// 封装连接管理
type RabbitMQ struct {
    conn    *amqp.Connection
    channel *amqp.Channel
}

func NewRabbitMQ(url string) (*RabbitMQ, error) {
    conn, err := amqp.Dial(url)
    ch, err := conn.Channel()
    // 监听连接关闭
    go func() {
        <-conn.NotifyClose(make(chan *amqp.Error))
        // 重连逻辑
    }()
    return &RabbitMQ{conn, ch}, nil
}
```

#### 90.5 选型建议
- 需要复杂路由、可靠确认 → RabbitMQ
- 需要超高吞吐、日志收集、流处理 → Kafka
- 简单任务队列、不需要持久化 → Redis List/Stream
- 一般互联网项目：Redis缓存 + RabbitMQ/Kafka 消息队列

---

## 第七篇：系统设计与架构

---

### 第91章 · 设计模式（上）：创建型与结构型

#### 91.1 为什么学设计模式
- 设计模式是前人在大量工程实践中总结的"代码设计经验"
- 比喻：设计模式就是"装修设计模板"——不是必须套用，但能让你少走弯路
- 注意：不要为了用模式而用模式，简单问题不需要复杂模式

#### 91.2 单例模式（Singleton）
- 保证一个类只有一个实例，并提供全局访问点
```go
var (
    instance *Database
    once     sync.Once
)

func GetDatabase() *Database {
    once.Do(func() {
        instance = &Database{connected: true}
    })
    return instance
}
```
- `sync.Once` 保证初始化的代码只执行一次（线程安全）
- 应用：数据库连接池、配置对象、日志器
- 比喻：一个国家只有一个首都，不管谁问都一样

#### 91.3 工厂模式（Factory）
```go
type Payment interface {
    Pay(amount float64) error
}

func NewPayment(method string) Payment {
    switch method {
    case "alipay":
        return &Alipay{}
    case "wechat":
        return &WechatPay{}
    default:
        return nil
    }
}
```
- 把对象的创建和使用分离
- 比喻：工厂=汽车的流水线，你只需要说"造一辆轿车"而不需要知道每个零件怎么装

#### 91.4 建造者模式（Builder）
```go
type ServerBuilder struct {
    host string
    port int
    tls  bool
}

func NewServerBuilder() *ServerBuilder {
    return &ServerBuilder{port: 8080}  // 设置默认值
}
func (b *ServerBuilder) WithHost(host string) *ServerBuilder {
    b.host = host
    return b
}
func (b *ServerBuilder) WithTLS() *ServerBuilder {
    b.tls = true
    return b
}
func (b *ServerBuilder) Build() *Server {
    return &Server{host: b.host, port: b.port, tls: b.tls}
}

// 使用
server := NewServerBuilder().WithHost("0.0.0.0").WithTLS().Build()
```
- 一步步构建复杂对象，链式调用很优雅
- 比喻：Builder=定制电脑的配置单，一步步选CPU、内存、硬盘，最后组装

#### 91.5 适配器模式（Adapter）
- 把一个接口转成另一个接口，让不兼容的类能一起工作
- 比喻：手机充电转换头 —— 中国大陆的插头插不进香港的插座，加一个转换头就能用

#### 91.6 装饰器模式（Decorator）
```go
// 给Handler加日志、认证、限流等功能
func LoggingMiddleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        log.Println(r.URL.Path)
        next.ServeHTTP(w, r)
    })
}
```
- Go的中间件本质就是装饰器模式

#### 91.7 策略模式（Strategy）
```go
type SortStrategy interface {
    Sort([]int)
}
type BubbleSort struct{}
type QuickSort struct{}

func (b BubbleSort) Sort(data []int) { /* 冒泡排序 */ }
func (q QuickSort) Sort(data []int)   { /* 快速排序 */ }

// 使用：根据数据量选择不同策略
var strategy SortStrategy
if len(data) < 100 {
    strategy = BubbleSort{}
} else {
    strategy = QuickSort{}
}
strategy.Sort(data)
```
- 比喻：去上班（目标），下雨天打车（策略1），晴天骑车（策略2），殊途同归

---

### 第92章 · 设计模式（下）：行为型

#### 92.1 观察者模式（Observer）
```go
type Observer interface {
    OnUpdate(data string)
}
type Subject struct {
    observers []Observer
}
func (s *Subject) NotifyAll(data string) {
    for _, obs := range s.observers {
        obs.OnUpdate(data)
    }
}
```
- Go中实现：用channel代替传统的观察者列表
- 比喻：公众号发推送 → 所有关注者都收到

#### 92.2 责任链模式（Chain of Responsibility）
```go
type Handler interface {
    Handle(req *Request) bool
    SetNext(Handler)
}
```
- Gin的中间件链就是责任链模式
- 每个处理器决定：自己处理掉，还是传给下一个

#### 92.3 模板方法模式
```go
type DataProcessor interface {
    Fetch() ([]byte, error)
    Parse([]byte) (interface{}, error)
    Store(interface{}) error
}
// 骨架方法
func Process(dp DataProcessor) error {
    data, _ := dp.Fetch()
    parsed, _ := dp.Parse(data)
    return dp.Store(parsed)
}
```
- 定义算法骨架，具体步骤由子类实现
- 比喻：炒菜模板=备菜→热锅→下锅→调味→出锅，但具体什么菜各不同

---

### 第93章 · SOLID原则

#### 93.1 什么是SOLID
- 面向对象设计的五个基本原则
- Go虽然没有类继承，但SOLID精神同样适用（通过接口和组合）
- 比喻：SOLID = 建筑设计的规范，遵守了房子就不会轻易倒塌

#### 93.2 S — 单一职责原则（SRP）
- 一个类/模块只做一件事
- 反例：一个函数既查数据库、又发短信、又写日志
- 正例：拆成三个函数各自负责
- Go中的体现：Handler只做参数解析和响应，业务逻辑在Service层
- 比喻：厨师炒菜、洗碗工洗碗，不要让厨师又炒菜又洗碗

#### 93.3 O — 开放封闭原则（OCP）
- 对扩展开放，对修改封闭
- 新增功能时，不应该修改已有的稳定代码
- Go中的体现：定义接口，新增实现类而不改原有代码
- 比喻：给电脑插U盘（扩展），不需要拆开主板焊接（修改）

#### 93.4 L — 里氏替换原则（LSP）
- 子类可以替换父类而不影响程序正确性
- Go中：接口的实现不能破坏接口约定的行为

#### 93.5 I — 接口隔离原则（ISP）
- 接口应该小而专一，不应该强迫用户依赖它不需要的方法
```go
// 不好：大而全的接口
type Worker interface {
    Work()
    Eat()
    Sleep()
}
// 好：小而专的接口
type Worker interface { Work() }
type Eater interface  { Eat() }
```
- Go的接口非常符合ISP（隐式实现 + 小接口）

#### 93.6 D — 依赖反转原则（DIP）
- 高层模块不应该依赖低层模块，两者都依赖抽象（接口）
- Go中：Service依赖 Repository 接口，而不是具体的MySQL实现
```go
type UserRepository interface {
    FindByID(id int) (*User, error)
}
type UserService struct {
    repo UserRepository  // 依赖接口，不依赖具体实现
}
```
- 好处：换数据库（MySQL→PostgreSQL）只需换Repository实现，Service不用改

---

### 第94章 · 微服务架构

#### 94.1 单体架构 vs 微服务架构
- **单体架构**：所有功能在一个应用里，一个进程，一个数据库
  - 优点：开发简单、部署容易、调试方便
  - 缺点：代码越滚越大、部署耦合（改一行要全量部署）
- **微服务架构**：按业务拆分为多个独立的小服务
  - 优点：独立部署、独立扩容、技术异构（不同服务用不同语言）
  - 缺点：分布式复杂性、网络调用延迟、数据一致性难
- 比喻：单体=全家住一个大开间，微服务=每人有自己的房间

#### 94.2 什么时候用微服务
- **不要一上来就微服务！** 先单体快速迭代，验证业务
- 当出现以下信号时考虑拆分：
  - 团队规模大（>20人），不同小组维护不同模块
  - 某些模块需要独立扩容
  - 代码冲突频繁、部署相互阻塞
- 比喻：一个人住不要买别墅，等家庭成员多了再考虑

#### 94.3 微服务拆分原则
- 按业务领域拆分（DDD有界上下文）
- 服务间通信：REST API（同步）/ 消息队列（异步）
- 每个服务有自己的数据库（数据隔离）
- 服务发现：服务注册中心（Consul/Etcd/Nacos）
- API网关：统一入口、认证、路由（Kong/Tyk/自研）

#### 94.4 微服务带来的挑战
- **分布式事务**：一个操作跨多个服务 → Saga模式、TCC、最终一致性
- **服务间调用链追踪**：Jaeger/Zipkin分布式追踪
- **配置管理**：Apollo/Nacos统一配置中心
- **CI/CD复杂度**：多个服务各自构建、部署

#### 94.5 Go微服务框架
- **Go-Zero**：国内流行的微服务框架，含代码生成
- **Go-Micro**：老牌微服务框架
- **Kratos**：B站开源Go微服务框架，设计规范、文档齐全

---

### 第95章 · gRPC与Protobuf

#### 95.1 gRPC是什么
- gRPC是Google开发的高性能RPC框架
- 使用HTTP/2传输，Protobuf序列化
- 支持多种语言（Go、Java、Python等）
- 比喻：REST API = 邮局寄信（慢但通用），gRPC = 内部电话专线（快但需要双方都安装专线）

#### 95.2 Protobuf是什么
- Protocol Buffers（protobuf）= Google的数据序列化格式
- 比JSON小3-10倍、快20-100倍
- 需要先定义 `.proto` 文件，然后自动生成各语言代码
- 比喻：JSON = 写完整句子描述数据，Protobuf = 用缩写暗号

#### 95.3 编写Proto文件
```protobuf
syntax = "proto3";
package user;

option go_package = "myapp/proto/user";

service UserService {
    rpc GetUser (GetUserRequest) returns (GetUserResponse);
}

message GetUserRequest {
    int64 id = 1;
}

message GetUserResponse {
    int64 id = 1;
    string username = 2;
    string email = 3;
}
```
- 每个字段有一个数字编号（=1, =2），编号用于二进制传输，改了编号等于改了协议

#### 95.4 生成Go代码
```bash
protoc --go_out=. --go-grpc_out=. proto/user.proto
```
- 生成两个文件：`user.pb.go`（消息结构体）和 `user_grpc.pb.go`（服务接口）

#### 95.5 gRPC服务端实现
```go
type UserServer struct {
    pb.UnimplementedUserServiceServer
}

func (s *UserServer) GetUser(ctx context.Context, req *pb.GetUserRequest) (*pb.GetUserResponse, error) {
    return &pb.GetUserResponse{Id: req.Id, Username: "张三", Email: "zhangsan@a.com"}, nil
}

func main() {
    lis, _ := net.Listen("tcp", ":50051")
    s := grpc.NewServer()
    pb.RegisterUserServiceServer(s, &UserServer{})
    s.Serve(lis)
}
```

#### 95.6 gRPC客户端调用
```go
conn, _ := grpc.Dial("localhost:50051", grpc.WithInsecure())
defer conn.Close()
client := pb.NewUserServiceClient(conn)
resp, _ := client.GetUser(ctx, &pb.GetUserRequest{Id: 1})
fmt.Println(resp.Username)
```

#### 95.7 REST vs gRPC 对比
| 维度 | REST（JSON） | gRPC（Protobuf） |
|------|-------------|-----------------|
| 协议 | HTTP/1.1 | HTTP/2 |
| 数据格式 | JSON | Protobuf（二进制） |
| 速度 | 较慢 | 很快 |
| 可读性 | 人类可读 | 工具可读 |
| 浏览器支持 | 原生支持 | 需grpc-web |
| 代码生成 | Swagger手动注解 | 自动生成 |
- 内部服务调用用gRPC，对外暴露用REST

---

### 第96章 · CAP理论与分布式一致性

#### 96.1 CAP定理
- **C（Consistency）一致性**：所有节点同一时间看到相同数据
- **A（Availability）可用性**：每个请求都能收到响应（不保证数据是最新的）
- **P（Partition Tolerance）分区容错**：网络分区时系统继续运行
- CAP本质：三者只能同时满足两个
- 比喻：三人两座——永远只有两个人能同时坐下

#### 96.2 CAP在实践中的选择
- **CA**：不允许网络分区（单机数据库，几乎没有分区）
- **CP**：发生分区时牺牲可用性（ZooKeeper、Etcd、Consul）
- **AP**：发生分区时牺牲一致性（Eureka、Cassandra）
- 互联网系统通常选择AP（用户体验优先，宁可见到旧数据也不能白屏）

#### 96.3 BASE理论
- CAP的务实妥协方案：
- **BA（Basically Available）**：基本可用（允许部分故障降级）
- **S（Soft State）**：软状态（数据有中间状态）
- **E（Eventually Consistent）**：最终一致性（数据最终会一致但不保证立刻一致）
- 比喻：微信消息——发出去可能对方几秒后才收到（最终一致），而不是永远收不到

#### 96.4 分布式一致性的实现
- **2PC（两阶段提交）**：协调者先问所有人"准备好了吗"，再让所有人"提交"
  - 比喻：所有人先举手说"准备好了"，再一起行动
  - 缺点：单点故障可能导致阻塞
- **TCC（Try-Confirm-Cancel）**：Try预占资源→Confirm确认执行→Cancel取消释放
  - 比喻：先预订机票（Try），付了款就出票（Confirm），不付款就释放（Cancel）
- **Saga**：长事务拆成多个短事务，每个都有补偿操作（撤销）
  - 比喻：每个步骤都准备了"后悔药"

---

### 第97章 · 负载均衡与反向代理

#### 97.1 什么是负载均衡
- 把请求分发到多台服务器上，避免单台过载
- 比喻：超市收银——只开一个窗口排大队，开8个窗口快速分流
- 作用：提高并发能力、故障转移（一台挂了流量切到其他）、方便扩容

#### 97.2 负载均衡算法
- **轮询（Round Robin）**：一人一次，公平分配
- **加权轮询**：性能好的服务器多分（4核机器权重8，2核权重4）
- **最少连接**：发给当前连接数最少的服务器
- **IP哈希**：同一个用户的请求始终发给同一台服务器（解决Session问题）
- **一致性哈希**：服务器增减时只用重新分配少量请求

#### 97.3 反向代理 vs 正向代理
- **正向代理**：代理客户端（翻墙工具帮你访问外网）
- **反向代理**：代理服务端（Nginx替你的Go服务接收请求再转发）
- 比喻：正向代理=你让朋友替你去买东西，反向代理=商店的接待员替你传达购物需求

#### 97.4 Nginx反向代理配置
```nginx
upstream go_app {
    server 127.0.0.1:8080 weight=3;
    server 127.0.0.1:8081 weight=1;
    server 127.0.0.1:8082 backup;  # 备用
}

server {
    listen 80;
    server_name example.com;

    location / {
        proxy_pass http://go_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

#### 97.5 健康检查
- Nginx定期检查后端服务器是否存活
- 不健康的节点自动摘除，恢复后自动加回
- 主动健康检查（Nginx Plus付费版）vs 被动健康检查（开源版）

---

### 第98章 · 高并发系统设计

#### 98.1 高并发的核心思路
- **缓存**：能缓存就缓存，减少后端压力
- **异步**：能异步就异步，不要阻塞用户
- **分库分表**：一个数据库扛不住就多搞几个
- **横向扩展**：一台服务器扛不住就多买几台
- **降级熔断**：撑不住的时候优先保证核心功能

#### 98.2 限流（Rate Limiting）
- **固定窗口**：每分钟最多1000个请求（边界突刺问题）
- **滑动窗口**：过去60秒内最多1000个（更平滑）
- **令牌桶**：每秒生成N个token，用完就得等（常用）
- **漏桶**：固定速率流出，多了溢出（强制匀速）
- Go实现令牌桶：
  ```go
  limiter := rate.NewLimiter(100, 200)  // 每秒100个，burst=200
  if !limiter.Allow() { /* 限流 */ }
  ```

#### 98.3 熔断（Circuit Breaker）
- 当下游服务故障率高时，直接快速失败而不是等超时
- 比喻：电路保险丝——某一路短路了就断开，保护整个电路
- Go-hystrix实现：
  ```go
  hystrix.Do("my_command", func() error {
      return callDownStreamService()
  }, func(err error) error {
      return returnFallbackData()  // 降级逻辑
  })
  ```

#### 98.4 降级
- 系统压力大时，关闭非核心功能保核心功能
- 比喻：手机低电量自动关闭蓝牙、降低亮度、限制后台
- 案例：秒杀期间关闭推荐系统、关闭积分查询

#### 98.5 缓存策略
- **Cache Aside**：读缓存→没有就读DB→写入缓存、写DB→删除缓存
- **Read/Write Through**：读写都经过缓存层
- **Write Behind**：先写缓存，异步批量写DB

#### 98.6 秒杀系统设计思路
- 核心矛盾：超高并发 > 有限库存
- 解决层次：
  1. 前端：按钮防重复、验证码、倒计时
  2. 网关层：限流、黑名单
  3. 业务层：Redis预减库存、异步下单、消息队列
  4. 数据库层：乐观锁、防超卖
- 比喻：春运抢票=秒杀，解决方案=排队系统+限购

---

## 第八篇：DevOps与部署

---

### 第99章 · Linux基础命令

#### 99.1 为什么要学Linux
- 99%的后端服务跑在Linux上
- 生产环境没有图形界面，一切靠命令行
- 比喻：Linux就是后端的"母语"

#### 99.2 文件与目录操作
```bash
pwd                           # 当前目录
ls -la                        # 列出所有文件（含隐藏）
cd /path                      # 切换目录
mkdir -p a/b/c                # 递归创建目录
cp -r src dst                 # 复制目录
mv old new                    # 移动/重命名
rm -rf /path                  # 删除（危险！）
find / -name "*.log"          # 查找文件
```

#### 99.3 文件内容查看
```bash
cat file.txt                  # 查看全部
head -20 file.txt             # 看前20行
tail -100f app.log            # 实时跟踪日志
grep "ERROR" app.log          # 搜索关键词
less file.txt                 # 分页浏览（大文件推荐）
wc -l file.txt                # 统计行数
```

#### 99.4 权限管理
```bash
chmod 755 script.sh           # rwxr-xr-x（属主读写执行，其他人读执行）
chown user:group file.txt     # 更改所有者
```
- r=4, w=2, x=1
- 755 = rwxr-xr-x = 属主全部权限，其他人读写执行

#### 99.5 进程管理
```bash
ps aux                        # 查看所有进程
ps aux | grep nginx           # 查找nginx进程
kill -9 PID                   # 强制杀进程（-9是SIGKILL）
kill -15 PID                  # 优雅退出（-15是SIGTERM）
top                           # 实时监控（CPU、内存）
htop                          # top的增强版（更直观）
```

#### 99.6 网络命令
```bash
ping google.com               # 测试连通性
curl http://localhost:8080    # 发送HTTP请求
netstat -tlnp                 # 查看监听端口
ss -tlnp                      # netstat的替代（更快）
telnet host port              # 测试端口通不通
```

#### 99.7 磁盘与内存
```bash
df -h                         # 磁盘使用情况
du -sh /path                  # 目录大小
free -h                       # 内存使用情况
```

#### 99.8 用户与系统
```bash
whoami                        # 当前用户
who                           # 当前登录的用户
uname -a                      # 系统信息
uptime                        # 系统运行时间
systemctl start/stop/status nginx  # 管理服务
```

---

### 第100章 · Shell脚本编写

#### 100.1 什么是Shell脚本
- Shell脚本 = 一堆Shell命令组成的文件，能自动执行
- 比喻：Shell脚本就像"自动化流水线操作手册"
- 后缀 `.sh`，首行 `#!/bin/bash`

#### 100.2 第一个Shell脚本
```bash
#!/bin/bash
echo "Hello, $(whoami)!"
echo "当前时间: $(date)"
echo "当前目录: $(pwd)"
```
- `chmod +x hello.sh && ./hello.sh` 执行

#### 100.3 变量
```bash
NAME="张三"
echo "Hello $NAME"
echo "Hello ${NAME}"  # 变量拼接时用{}
```
- 等号两边不能有空格

#### 100.4 条件判断
```bash
if [ $1 -gt 100 ]; then
    echo "大于100"
elif [ $1 -eq 100 ]; then
    echo "等于100"
else
    echo "小于100"
fi
```
- 整数比较：`-eq`（等于）、`-ne`（不等于）、`-gt`、`-lt`、`-ge`、`-le`
- 字符串比较：`=`、`!=`、`-z`（为空）、`-n`（非空）
- 文件判断：`-f`（是文件）、`-d`（是目录）、`-x`（可执行）

#### 100.5 循环
```bash
# for循环
for i in {1..5}; do
    echo "Number: $i"
done

# while循环
count=0
while [ $count -lt 5 ]; do
    echo $count
    ((count++))
done
```

#### 100.6 函数
```bash
function greet() {
    echo "你好, $1"
}
greet "张三"  # 调用，$1是第一个参数
```

#### 100.7 实战：项目部署脚本
```bash
#!/bin/bash
echo "=== 开始部署 ==="
cd /path/to/project
git pull origin main
go build -o app ./cmd/server
systemctl restart myapp
echo "=== 部署完成 ==="
```

---

### 第101章 · Git版本控制

#### 101.1 为什么需要版本控制
- 比喻：Git就是"项目的时空穿梭机"——随时回到过去的任意版本
- 没有Git：代码改来改去，不知道哪个版本是好的
- 多人协作：没有版本控制基本不可能

#### 101.2 Git基本概念
- **工作区（Working Directory）**：你正在编辑的文件夹
- **暂存区（Stage/Index）**：`git add` 后待提交的文件
- **本地仓库（Local Repo）**：`git commit` 后的提交记录
- **远程仓库（Remote Repo）**：GitHub/GitLab上的仓库

#### 101.3 基本操作
```bash
git init                              # 初始化仓库
git clone https://github.com/xxx.git  # 克隆仓库
git status                            # 查看状态
git add file.go                       # 添加到暂存区
git add .                             # 添加所有修改
git commit -m "feat: 添加用户模块"     # 提交
git push origin main                  # 推送到远程
git pull origin main                  # 拉取远程更新
```

#### 101.4 分支管理
```bash
git branch feature-login              # 创建分支
git checkout feature-login            # 切换分支
git checkout -b feature-login         # 创建+切换
git merge feature-login               # 合并到当前分支
git branch -d feature-login           # 删除分支
```
- 分支策略：main（主分支）、develop（开发分支）、feature/xxx（功能分支）

#### 101.5 提交信息规范（Conventional Commits）
```
feat: 添加用户登录功能
fix: 修复订单金额计算错误
docs: 更新API文档
refactor: 重构用户模块
test: 添加订单模块测试
chore: 更新依赖版本
```
- 首行50字符以内，需要详细说明时空一行接着写

#### 101.6 撤销操作
```bash
git reset HEAD file.go          # 取消暂存（add反操作）
git checkout -- file.go         # 撤销工作区修改（危险！）
git commit --amend              # 修改最近一次commit
git reset --soft HEAD~1         # 撤销commit但保留修改
git reset --hard HEAD~1         # 撤销所有（危险！）
git revert HEAD                 # 反向提交撤销（推荐）
```

#### 101.7 解决合并冲突
- 当两分支修改了同一行时，merge会产生冲突
- 冲突标记：
```
<<<<<<< HEAD
你的修改
=======
别人的修改
>>>>>>> feature-branch
```
- 手动选择一个版本（或合并两版），删除标记，commit

#### 101.8 .gitignore
```
# 编译产物
/app
/bin
*.exe

# 环境配置
.env
.env.local

# IDE
.idea/
.vscode/

# 依赖
/vendor
node_modules/
```

---

### 第102章 · Docker容器化

#### 102.1 什么是Docker
- Docker是一个轻量级的容器化平台
- 比喻：Docker就是"标准化集装箱"——里面装什么（应用+环境），外面都是一样大小的箱子，放到任何码头（服务器）都能运行
- "在我电脑上能跑啊" → 用Docker彻底解决环境问题

#### 102.2 核心概念
- **镜像（Image）**：一个只读模板（类）——比喻：制造汽车的模具
- **容器（Container）**：镜像的运行时实例（对象）——比喻：用模具造出来的汽车
- **Dockerfile**：制作镜像的配方
- **Docker Hub**：公共镜像仓库（像GitHub，但是放镜像）

#### 102.3 基本命令
```bash
docker pull golang:1.21          # 拉取Go镜像
docker images                    # 查看本地镜像
docker run -d -p 8080:8080 myapp # 启动容器（-d后台，-p端口映射）
docker ps                        # 查看运行中的容器
docker ps -a                     # 查看所有容器（含停止的）
docker stop container_id         # 停止容器
docker rm container_id           # 删除容器
docker rmi image_id              # 删除镜像
docker exec -it container_id /bin/sh  # 进入容器
docker logs container_id         # 查看容器日志
```

#### 102.4 Dockerfile编写
```dockerfile
# 构建阶段
FROM golang:1.21-alpine AS builder
WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -o server ./cmd/server

# 运行阶段
FROM alpine:latest
RUN apk --no-cache add ca-certificates
WORKDIR /app
COPY --from=builder /app/server .
EXPOSE 8080
CMD ["./server"]
```
- 两阶段构建：编译在一个镜像，运行在另一个最小镜像（从几百MB降到十几MB）

#### 102.5 Docker Compose多服务编排
```yaml
# docker-compose.yml
version: '3.8'
services:
  app:
    build: .
    ports:
      - "8080:8080"
    depends_on:
      - mysql
      - redis
    environment:
      - DB_HOST=mysql
      - REDIS_ADDR=redis:6379

  mysql:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: secret
      MYSQL_DATABASE: mydb
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

volumes:
  mysql_data:
```
- 一条命令启动所有服务：`docker-compose up -d`

#### 102.6 Docker网络
- `bridge`（默认）：容器间通过docker0网桥通信
- `host`：共用宿主机网络
- `none`：无网络
- Compose中的服务名可直接作为hostname：`mysql:3306`

---

### 第103章 · CI/CD持续集成

#### 103.1 什么是CI/CD
- **CI（Continuous Integration）持续集成**：代码提交后自动构建、测试
- **CD（Continuous Delivery/Deployment）持续交付/部署**：自动部署到环境
- 比喻：CI=自动质检，CD=自动发货

#### 103.2 CI/CD流程
```
代码推送 → 触发构建 → 运行测试 → 代码检查 → 构建镜像 →
推送到镜像仓库 → 部署到服务器 → 健康检查 → 完成
```

#### 103.3 GitHub Actions配置
```yaml
# .github/workflows/deploy.yml
name: Build and Deploy
on:
  push:
    branches: [ main ]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-go@v4
        with:
          go-version: '1.21'
      - run: go test ./...
      - run: go build -o app ./cmd/server
      - name: Build Docker Image
        run: docker build -t myapp:latest .
      - name: Push to Registry
        run: |
          docker tag myapp registry.example.com/myapp:${{ github.sha }}
          docker push registry.example.com/myapp:${{ github.sha }}
      - name: Deploy
        run: ssh deploy@server "docker pull && docker-compose up -d"
```

#### 103.4 自建CI/CD工具
- **Jenkins**（传统工业标准，灵活但配置复杂）
- **GitLab CI**（和GitLab深度集成）
- **Drone**（轻量级Go编写）
- **Gitea Actions**（如果你用自建Git）

#### 103.5 CI/CD最佳实践
- 不同环境（dev/staging/prod）分开部署
- 部署前运行完整测试
- 生产环境用蓝绿部署或滚动更新（零停机）
- 保留最近几个版本的镜像方便回滚

---

### 第104章 · 云平台部署

#### 104.1 云服务器基础
- 主流云厂商：阿里云、腾讯云、AWS（国际）
- 云服务器（ECS/EC2）就是一台远程的虚拟电脑
- SSH登录：`ssh root@your-server-ip`

#### 104.2 部署前准备
```bash
# 安装必要软件
apt update
apt install -y docker.io docker-compose git

# 创建部署目录
mkdir -p /opt/myapp
cd /opt/myapp

# 克隆代码
git clone https://github.com/user/myapp.git .
```

#### 104.3 使用Docker Compose部署
```bash
# 拉取并启动
docker-compose pull
docker-compose up -d

# 查看状态
docker-compose ps
docker-compose logs -f
```

#### 104.4 Nginx反向代理配置
```nginx
server {
    listen 80;
    server_name api.example.com;

    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        client_max_body_size 10M;
    }
}
```

#### 104.5 SSL证书（Let's Encrypt）
```bash
# 用certbot自动化
apt install certbot python3-certbot-nginx
certbot --nginx -d api.example.com
# 自动设置HTTPS + 自动续期
```

#### 104.6 云原生服务简介
- **对象存储**：OSS/S3存文件
- **云数据库**：RDS，高可用免运维
- **云Redis**：免运维，高可用
- **CDN**：静态资源全球加速
- **WAF**：Web应用防火墙
- 对比：自建省钱但费力，云服务省力但费钱

---

### 第105章 · 监控与告警

#### 105.1 为什么需要监控
- 上线不是终点，线上可能出现各种问题
- 比喻：监控=ICU病房的生命体征监测仪——心率、血氧、血压实时显示，异常就报警
- 没有监控 = 闭着眼睛开车

#### 105.2 监控的四大黄金指标
- **延迟（Latency）**：请求花了多长时间
- **流量（Traffic）**：每秒多少请求
- **错误（Errors）**：有多少请求失败了
- **饱和度（Saturation）**：资源用了多少（CPU/内存/磁盘）

#### 105.3 Prometheus + Grafana
- **Prometheus**：采集和存储指标（时序数据库）
- **Grafana**：可视化面板
- Go中暴露指标：
  ```go
  import "github.com/prometheus/client_golang/prometheus/promhttp"
  http.Handle("/metrics", promhttp.Handler())
  ```

#### 105.4 日志收集（ELK / Loki）
- **ELK**：Elasticsearch + Logstash + Kibana（重量级但功能全）
- **Loki + Promtail + Grafana**：轻量级，和Grafana无缝集成
- 比喻：ELK=完整监控中心，Loki=简洁看板

#### 105.5 分布式链路追踪（Jaeger）
- 一个请求可能经过多个微服务，Jaeger串起全链路
- 可视化展示每个服务环节的耗时
- Go中使用OpenTelemetry：
  ```go
  import "go.opentelemetry.io/otel"
  tracer := otel.Tracer("my-service")
  ctx, span := tracer.Start(ctx, "GetUser")
  defer span.End()
  ```

#### 105.6 告警配置
- Prometheus AlertManager：定义告警规则 → 发邮件/短信/企业微信
- 告警规则示例：
  ```yaml
  - alert: HighErrorRate
    expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.05
    for: 5m
    annotations:
      summary: "错误率超过5%"
  ```

---

## 第九篇：测试

---

### 第106章 · 单元测试

#### 106.1 为什么要写测试
- 测试是代码的"防护网"，改了代码跑测试就知道有没有破坏
- 比喻：测试就像修路时放的安全锥，防止后面的车掉进坑里
- Go把测试作为一等公民（内置testing包）

#### 106.2 Go测试文件规范
- 文件名以 `_test.go` 结尾
- 测试函数以 `Test` 开头
- 放在同一个package下（或 `_test` 后缀的独立包）
```go
// user_test.go
func TestCreateUser(t *testing.T) {
    user := CreateUser("张三")
    if user.Name != "张三" {
        t.Errorf("期望张三，得到%s", user.Name)
    }
}
```

#### 106.3 表驱动测试（Table-Driven Tests）
```go
func TestAdd(t *testing.T) {
    tests := []struct {
        name string
        a, b, want int
    }{
        {"正数相加", 1, 2, 3},
        {"零相加", 0, 5, 5},
        {"负数相加", -1, -2, -3},
    }
    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            got := Add(tt.a, tt.b)
            if got != tt.want {
                t.Errorf("Add(%d,%d)=%d, want %d", tt.a, tt.b, got, tt.want)
            }
        })
    }
}
```
- Go推荐的测试风格，比写一堆重复的测试函数更清晰
- 添加测试用例只需在表格里加一行

#### 106.4 运行测试
```bash
go test ./...                    # 运行所有测试
go test -v ./...                 # 详细输出
go test -run TestAdd ./...       # 运行特定测试
go test -cover ./...             # 显示测试覆盖率
go test -coverprofile=coverage.out ./...
go tool cover -html=coverage.out # 浏览器查看覆盖率
```

#### 106.5 子测试（t.Run）
- 每个test case独立运行，某个失败不影响其他
- 可以单独运行某个子测试：`go test -run TestAdd/正数相加`

#### 106.6 测试辅助函数（Test Helpers）
```go
func assertEqual(t *testing.T, got, want interface{}) {
    t.Helper()  // 标记为helper，错误信息回指到调用处
    if got != want {
        t.Errorf("got %v, want %v", got, want)
    }
}
```

---

### 第107章 · Mock与测试替身

#### 107.1 为什么要Mock
- 单元测试应该只测自己的逻辑，不依赖外部系统（数据库、API）
- 比喻：测试菜刀不需要真的切菜，砍空气就能知道刀快不快
- Mock：创建一个假的替身代替真实的依赖

#### 107.2 手动Mock（接口方式）
```go
type UserRepository interface {
    FindByID(id int) (*User, error)
}

// 真实实现
type MySQLUserRepo struct { db *sql.DB }

// Mock实现
type MockUserRepo struct {
    Users map[int]*User
}
func (m *MockUserRepo) FindByID(id int) (*User, error) {
    if user, ok := m.Users[id]; ok {
        return user, nil
    }
    return nil, errors.New("not found")
}

// 测试
func TestGetUser(t *testing.T) {
    mockRepo := &MockUserRepo{Users: map[int]*User{1: {Name: "张三"}}}
    svc := NewUserService(mockRepo)
    user, _ := svc.GetUser(1)
    assertEqual(t, user.Name, "张三")
}
```

#### 107.3 testify/mock库
```go
import "github.com/stretchr/testify/mock"

type MockUserRepo struct {
    mock.Mock
}
func (m *MockUserRepo) FindByID(id int) (*User, error) {
    args := m.Called(id)
    return args.Get(0).(*User), args.Error(1)
}

func TestGetUser(t *testing.T) {
    mockRepo := new(MockUserRepo)
    mockRepo.On("FindByID", 1).Return(&User{Name: "张三"}, nil)
    svc := NewUserService(mockRepo)
    user, err := svc.GetUser(1)
    assert.NoError(t, err)
    assert.Equal(t, "张三", user.Name)
    mockRepo.AssertExpectations(t)  // 验证方法被调用了
}
```

#### 107.4 HTTP Mock
```go
import "net/http/httptest"

func TestHandler(t *testing.T) {
    router := setupRouter()
    req := httptest.NewRequest("GET", "/users/1", nil)
    w := httptest.NewRecorder()
    router.ServeHTTP(w, req)

    assert.Equal(t, 200, w.Code)
    assert.Contains(t, w.Body.String(), "张三")
}
```

#### 107.5 SQL Mock（sqlmock）
```go
import "github.com/DATA-DOG/go-sqlmock"

db, mock, _ := sqlmock.New()
defer db.Close()

// 设置预期SQL和返回结果
mock.ExpectQuery("SELECT id, name FROM users WHERE id = \\?").
    WithArgs(1).
    WillReturnRows(sqlmock.NewRows([]string{"id", "name"}).AddRow(1, "张三"))
```
- sqlmock拦截SQL执行，不真正连数据库

---

### 第108章 · 集成测试

#### 108.1 什么是集成测试
- 单元测试测单个函数，集成测试测多个组件协作
- 比喻：单元测试=测试单个零件，集成测试=测试零件组装后能不能工作
- 需要真实的数据库、Redis等外部依赖

#### 108.2 Testcontainers
```go
import "github.com/testcontainers/testcontainers-go"
import "github.com/testcontainers/testcontainers-go/modules/mysql"

func TestUserRepository_Integration(t *testing.T) {
    ctx := context.Background()
    mysqlContainer, _ := mysql.RunContainer(ctx, testcontainers.WithImage("mysql:8.0"))
    defer mysqlContainer.Terminate(ctx)

    dsn, _ := mysqlContainer.ConnectionString(ctx)
    db, _ := gorm.Open(mysql.Open(dsn), &gorm.Config{})
    db.AutoMigrate(&User{})

    repo := NewUserRepository(db)
    user, err := repo.Create(&User{Name: "张三"})
    assert.NoError(t, err)
    assert.NotZero(t, user.ID)
}
```
- Testcontainers自动拉取Docker镜像、启动容器，测试结束后自动清理
- 比喻：在你的电脑上临时搭了一个"微型生产环境"

#### 108.3 集成测试的最佳实践
- 每次测试用独立的数据库（或独立的数据前缀）
- 测试数据用完后清理（setup/teardown）
- 不要依赖外部系统的状态（测试应该是可重复的）
- CI中运行集成测试时确保Docker环境可用

---

### 第109章 · 性能测试

#### 109.1 什么是性能测试
- 测试系统在高负载下的表现：能撑多少QPS、RT（响应时间）多少
- 比喻：性能测试=测一辆车的极限——0到100加速多少秒、最高时速多少

#### 109.2 Go Benchmark
```go
func BenchmarkAdd(b *testing.B) {
    for i := 0; i < b.N; i++ {
        Add(1, 2)
    }
}
```
- 运行：`go test -bench=. -benchmem`
- b.N由框架自动调整，直到运行时间稳定

#### 109.3 pprof性能分析
```go
import _ "net/http/pprof"

// 运行程序后访问：
// http://localhost:6060/debug/pprof/  （概览）
// http://localhost:6060/debug/pprof/profile  （CPU分析）
// http://localhost:6060/debug/pprof/heap   （内存分析）
```
```bash
# CLI分析
go tool pprof http://localhost:6060/debug/pprof/profile?seconds=30
# 在pprof交互中: top, list 函数名, web
```
- 火焰图是最直观的性能分析工具

#### 109.4 压测工具
- **wrk**：轻量HTTP压测
  ```bash
  wrk -t4 -c100 -d30s http://localhost:8080/api/users
  ```
- **ab（Apache Bench）**：经典压测工具
- **vegeta**：Go写的压测，输出更丰富
- **JMeter**：图形化，功能最强但学习曲线陡

#### 109.5 性能优化思路
1. 用pprof找到瓶颈（CPU热点 / 内存分配最多）
2. 优化慢的部分（算法、数据结构、减少分配）
3. 再次压测验证（A/B对比）
4. 注意：先跑通再优化，不要过早优化

---

## 第十篇：实战项目

---

### 第110章 · 项目一：任务管理系统（Todo API）

#### 110.1 项目目标
- 用Go + Gin + GORM + MySQL + Redis 做一个完整的任务管理API
- 功能：任务CRUD、标记完成/未完成、分类标签、到期提醒
- 比喻：这是你的第一个"完整餐厅"——从仓库（数据库）到厨房（业务）到服务员（API）全部自己搭

#### 110.2 项目结构
```
todo-api/
├── cmd/server/main.go
├── internal/
│   ├── handler/task_handler.go
│   ├── service/task_service.go
│   ├── repository/task_repo.go
│   ├── model/task.go
│   └── middleware/auth.go
├── config/config.yaml
├── migrations/
├── Dockerfile
└── docker-compose.yml
```

#### 110.3 数据库设计
```sql
CREATE TABLE tasks (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    user_id     INT NOT NULL,
    title       VARCHAR(200) NOT NULL,
    description TEXT,
    priority    TINYINT DEFAULT 0,     -- 0普通 1重要 2紧急
    status      TINYINT DEFAULT 0,     -- 0未完成 1已完成
    due_date    DATETIME,
    category_id INT,
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at  DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

#### 110.4 API设计
| 方法 | 路径 | 功能 |
|------|------|------|
| GET | /api/v1/tasks | 获取任务列表（支持分页、筛选） |
| POST | /api/v1/tasks | 创建任务 |
| GET | /api/v1/tasks/:id | 获取单个任务 |
| PUT | /api/v1/tasks/:id | 更新任务 |
| DELETE | /api/v1/tasks/:id | 删除任务 |
| PATCH | /api/v1/tasks/:id/complete | 标记完成 |

#### 110.5 核心代码要点
- Handler层：参数绑定、参数校验、调用Service、返回响应
- Service层：从Redis缓存取→没有就查DB→设置缓存
- Repository层：GORM操作数据库
- 中间件链：Logger → Recovery → CORS → JWT认证
- 统一响应格式、统一错误码

#### 110.6 项目要点
- 用户只能操作自己的任务（数据隔离）
- 任务列表用Redis缓存（提高性能）
- 搜索任务用LIKE查询
- 分页用GORM的Limit+Offset

---

### 第111章 · 项目二：用户认证系统

#### 111.1 项目目标
- 实现完整的用户注册、登录、Token刷新、密码重置系统
- 技术栈：Go + Gin + JWT + bcrypt + Redis + 邮件

#### 111.2 功能清单
1. 注册：邮箱+密码，bcrypt加密存储
2. 登录：返回 Access Token（15分钟） + Refresh Token（7天）
3. 刷新Token：用Refresh Token换新Token（旧Refresh Token失效，防盗用）
4. 修改密码：验证旧密码 → 修改
5. 忘记密码：发重置链接到邮箱 → 重置
6. 登出：前端删Token，后端把Refresh Token加入黑名单（Redis）

#### 111.3 JWT双Token机制
- Access Token：短时间（15分钟），放在Authorization头
- Refresh Token：长时间（7天），存在Redis中，仅用于刷新
- 刷新时验证Refresh Token是否在Redis中（可撤销）

#### 111.4 密码重置流程
1. 用户点"忘记密码" → 输入邮箱
2. 后端生成随机Token，存入Redis（15分钟过期）
3. 发邮件到用户邮箱，含重置链接：`/reset-password?token=xxx`
4. 用户点链接 → 输入新密码 → 后端验证Token → 更新密码 → 删除Token

#### 111.5 安全要点
- 密码用bcrypt存储（cost=10）
- 登录失败5次锁定账号30分钟（Redis计数）
- 密码重置链接一次性使用
- 敏感操作记录日志

---

### 第112章 · 项目三：博客系统

#### 112.1 项目目标
- 完整的博客后台：文章管理、分类标签、评论系统
- 技术栈：Go + Gin + GORM + MySQL + Redis + Swagger

#### 112.2 数据库设计
```sql
-- 文章表
articles: id, title, content(MEDIUMTEXT), slug(唯一URL标识), status(草稿/发布), user_id, category_id, view_count, created_at, updated_at

-- 分类表
categories: id, name, parent_id(自关联)

-- 标签表（多对多）
tags: id, name
article_tags: article_id, tag_id

-- 评论表
comments: id, article_id, user_id, content, parent_id(楼中楼)
```

#### 112.3 核心功能
- 文章CRUD + Markdown转HTML
- 分类层级结构（无限级子分类）
- 多标签支持
- 文章slug自动生成（标题拼音）
- 阅读量用Redis INCR，定时回写MySQL
- 评论支持嵌套回复（两级）
- 接口限流（令牌桶，同一IP每分钟最多发3条评论）
- Swagger文档

#### 112.4 Markdown转HTML
```go
import "github.com/yuin/goldmark"
import "github.com/yuin/goldmark-highlighting"

md := goldmark.New(goldmark.WithExtensions(highlighting.Highlighting))
var buf bytes.Buffer
md.Convert([]byte(markdown), &buf)
html := buf.String()
```

---

### 第113章 · 项目四：秒杀系统

#### 113.1 项目目标
- 实现一个高并发秒杀系统（核心：防超卖、高并发）
- 技术栈：Go + Gin + Redis + RabbitMQ + MySQL

#### 113.2 核心挑战
- 库存扣减的并发安全（不能超卖）
- 海量请求的限流和排队
- 用户不能重复下单

#### 113.3 系统架构
```
用户请求 → Nginx限流 → Gin API → Redis预减库存→ RabbitMQ队列 → 
消费者处理 → MySQL持久化订单
```

#### 113.4 核心实现步骤
1. **Redis预减库存**：
   ```go
   // 秒杀开始前把库存加载到Redis
   rdb.Set(ctx, "seckill:stock:100", 100, 0)
   // 用户请求时原子减库存
   if stock, _ := rdb.Decr(ctx, "seckill:stock:100").Result(); stock < 0 {
       return "已抢完"
   }
   ```
2. **发送MQ消息**：预扣库存成功后，发消息到RabbitMQ
3. **消费者处理**：MQ消费者创建订单、扣减MySQL库存
4. **防重复下单**：Redis Set记录已下单用户ID

#### 113.5 关键细节
- 秒杀页面CDN缓存静态资源
- 秒杀按钮防重复点击（前端置灰 + 后端幂等）
- 用Lua脚本保证Redis库存操作原子性
- MQ消息处理失败要有重试和补偿机制
- 订单30分钟未支付自动取消（延时队列）

---

### 第114章 · 项目五：即时通讯IM

#### 114.1 项目目标
- 用Go实现一个支持WebSocket的即时通讯系统
- 技术栈：Go + Gin + WebSocket + Redis + MySQL

#### 114.2 核心功能
1. 用户登录（JWT）
2. 好友列表
3. 一对一聊天（实时消息）
4. 群组聊天
5. 历史消息查询
6. 在线状态

#### 114.3 WebSocket连接管理
```go
var hub = struct {
    clients    map[int64]*websocket.Conn  // userID → conn
    broadcast  chan Message
    register   chan Client
    unregister chan Client
    mu         sync.RWMutex
}{}

func handleWebSocket(c *gin.Context) {
    conn, _ := upgrader.Upgrade(c.Writer, c.Request, nil)
    // 注册到hub
    hub.mu.Lock()
    hub.clients[userID] = conn
    hub.mu.Unlock()

    // 读取消息循环
    for {
        _, msgBytes, err := conn.ReadMessage()
        // 解析消息 → 查找接收者 → 推送
    }
}
```

#### 114.4 消息流转
1. 用户A发送消息到服务器（WebSocket）
2. 服务器保存消息到MySQL（历史记录）
3. 服务器通过WebSocket推送给接收者B（如果在线）
4. 如果B离线，存未读消息（B上线时拉取）

#### 114.5 群聊实现
- 群组表 + 群成员表
- 发消息到群 → 查询群里所有在线成员 → 逐一推送
- 离线成员存储未读

#### 114.6 优化要点
- 使用Goroutine处理每个连接
- 用Redis Pub/Sub实现多节点消息同步
- 心跳检测：客户端定时发ping，超时断开

---

### 第115章 · 项目六：微服务电商系统

#### 115.1 项目目标
- 从单体到微服务的完整拆分实践
- 拆分服务：用户服务、商品服务、订单服务、支付服务

#### 115.2 服务架构
```
                    [Nginx反向代理]
                           │
                    [API网关（Gin）]
                   /    |    |    \
            用户服务  商品服务  订单服务  支付服务
              │       │      │       │
           [MySQL] [MySQL] [MySQL] [MySQL]
              │       │      │       │
           [Redis] [Redis] [Redis] [Redis]
                     \    |    /
                   [消息队列RabbitMQ]
```
- 每个服务独立数据库
- 服务间通过gRPC同步调用 + RabbitMQ异步通信

#### 115.3 服务拆分
| 服务 | 职责 | 核心API |
|------|------|--------|
| 用户服务 | 注册、登录、信息管理 | GetUser, UpdateUser |
| 商品服务 | 商品CRUD，库存管理 | ListProducts, GetProduct |
| 订单服务 | 创建订单、查询订单 | CreateOrder, GetOrder |
| 支付服务 | 支付处理 | ProcessPayment |

#### 115.4 分布式事务（下单流程）
1. 订单服务收到下单请求
2. 调用商品服务预扣库存 → 商品服务预留库存返回结果
3. 订单服务创建订单（状态=待支付）
4. 支付服务处理支付 → 支付成功
5. 订单服务更新订单状态 → 消息队列通知商品服务确认扣减
6. 如果任一步失败，执行补偿操作（释放预留库存等）

#### 115.5 技术要点
- 服务发现用Consul或Etcd
- Proto文件统一管理
- 统一的认证JWT在各服务间传递
- Jaeger全链路追踪
- Prometheus + Grafana统一监控
- 配置统一用Nacos/Apollo
- Docker Compose本地开发，Kubernetes生产部署

#### 115.6 项目感悟
- 微服务不是在代码层面复杂，而是在"运维"和"调试"层面复杂
- 单体跑通了再拆微服务，不要一上来就拆
- 最大的坑：分布式事务、网络延迟、日志追踪

---

## 附录

---

### 附录A · Go标准库速查

#### A.1 常用标准库概览
| 包名 | 用途 | 常用函数/类型 |
|------|------|------------|
| `fmt` | 格式化输入输出 | Printf, Sprintf, Errorf, Scan |
| `io` | I/O基础接口 | Reader, Writer, Copy |
| `os` | 操作系统接口 | Open, Create, Mkdir, Remove, Getenv |
| `net/http` | HTTP客户端/服务端 | Get, Post, ListenAndServe, HandleFunc |
| `encoding/json` | JSON编解码 | Marshal, Unmarshal |
| `strings` | 字符串操作 | Contains, Split, Join, Replace, Trim |
| `strconv` | 字符串与类型转换 | Atoi, Itoa, ParseInt, FormatFloat |
| `time` | 时间处理 | Now, Parse, Format, Duration, Sleep |
| `sync` | 并发同步 | Mutex, WaitGroup, Once, RWMutex |
| `context` | 上下文 | WithCancel, WithTimeout, WithValue |
| `errors` | 错误处理 | New, Is, As, Unwrap, Join |
| `log` | 日志 | Println, Fatalf, SetFlags |
| `path/filepath` | 文件路径操作 | Join, Base, Dir, Ext, Walk |
| `sort` | 排序 | Sort, Slice, Search |
| `math/rand` | 随机数 | Intn, Float64, Shuffle |
| `crypto/*` | 加密相关 | sha256, md5, hmac, rand |

#### A.2 第三方常用库
| 类别 | 推荐库 |
|------|--------|
| Web框架 | gin, echo, fiber |
| ORM | gorm, ent, sqlx |
| Redis | go-redis |
| 配置 | viper |
| 日志 | zap, logrus |
| JWT | golang-jwt |
| 验证 | validator |
| 测试 | testify |
| HTTP客户端 | resty |
| 爬虫 | colly |
| 任务调度 | cron |
| 命令行 | cobra |
| 依赖注入 | wire, dig |

---

### 附录B · MySQL常用命令速查

#### B.1 数据库操作
```sql
CREATE DATABASE dbname CHARSET utf8mb4;
DROP DATABASE dbname;
SHOW DATABASES;
USE dbname;
```

#### B.2 表操作
```sql
CREATE TABLE t (id INT PRIMARY KEY AUTO_INCREMENT, name VARCHAR(50));
ALTER TABLE t ADD COLUMN c VARCHAR(20);
ALTER TABLE t MODIFY COLUMN c INT;
ALTER TABLE t DROP COLUMN c;
DROP TABLE t;
SHOW TABLES;
DESC t;  -- 查看表结构
```

#### B.3 CRUD速查
```sql
INSERT INTO t (name) VALUES ('a'), ('b');
SELECT * FROM t WHERE id=1;
SELECT COUNT(*), AVG(age) FROM t GROUP BY city;
UPDATE t SET name='b' WHERE id=1;
DELETE FROM t WHERE id=1;
```

#### B.4 索引相关
```sql
CREATE INDEX idx_name ON t(name);
CREATE UNIQUE INDEX idx_name ON t(name);
CREATE INDEX idx ON t(a, b);
DROP INDEX idx_name ON t;
SHOW INDEX FROM t;
EXPLAIN SELECT * FROM t WHERE name='a';
```

#### B.5 用户与权限
```sql
CREATE USER 'user'@'%' IDENTIFIED BY 'password';
GRANT ALL ON db.* TO 'user'@'%';
GRANT SELECT ON db.* TO 'user'@'%';
FLUSH PRIVILEGES;
DROP USER 'user'@'%';
```

#### B.6 备份与恢复
```bash
mysqldump -u root -p dbname > backup.sql
mysql -u root -p dbname < backup.sql
```

---

### 附录C · Redis命令速查

#### C.1 Key操作
```bash
KEYS pattern        # 查找key（生产别用）
SCAN 0 MATCH p*     # 游标遍历（生产用）
EXISTS key          # 是否存在
DEL key             # 删除
EXPIRE key 60       # 设置过期
TTL key             # 剩余时间
TYPE key            # 查看类型
RENAME old new      # 重命名
```

#### C.2 String
```bash
GET key / SET key val / SETEX key 60 val / SETNX key val
INCR key / DECR key / INCRBY key 10
MGET k1 k2 / MSET k1 v1 k2 v2
APPEND key val
```

#### C.3 Hash
```bash
HSET key f v / HGET key f / HMSET key f1 v1 f2 v2
HGETALL key / HDEL key f / HINCRBY key f 1
HEXISTS key f / HLEN key / HKEYS key
```

#### C.4 List
```bash
LPUSH key v / RPUSH key v / LPOP key / RPOP key
LRANGE key 0 -1 / LLEN key
LINDEX key 0 / LREM key count value
```

#### C.5 Set
```bash
SADD key v / SREM key v / SMEMBERS key
SISMEMBER key v / SCARD key
SINTER k1 k2 / SUNION k1 k2 / SDIFF k1 k2
```

#### C.6 Sorted Set
```bash
ZADD key score member / ZREM key member
ZRANGE key 0 -1 / ZREVRANGE key 0 -1
ZRANK key member / ZSCORE key member
ZINCRBY key 10 member / ZCARD key
```

---

### 附录D · Docker命令速查

#### D.1 镜像
```bash
docker pull image:tag
docker images
docker rmi image
docker build -t name:tag .
docker tag src dest
docker push image:tag
```

#### D.2 容器
```bash
docker run -d --name c -p 8080:80 image
docker ps / docker ps -a
docker stop c / docker start c / docker restart c
docker rm c / docker rm -f c
docker exec -it c sh
docker logs c / docker logs -f c
docker cp c:/path/file .
docker inspect c
```

#### D.3 Docker Compose
```bash
docker-compose up -d
docker-compose down
docker-compose ps
docker-compose logs -f
docker-compose restart service_name
docker-compose build
```

#### D.4 清理
```bash
docker system prune -a     # 清理所有未使用的（警告：很彻底）
docker container prune
docker image prune
docker volume prune
```

---

### 附录E · Git命令速查

#### E.1 基本流程
```bash
git init                                # 初始化
git clone url                           # 克隆
git add .                               # 暂存所有
git commit -m "msg"                     # 提交
git push origin main                    # 推送
git pull origin main                    # 拉取
```

#### E.2 分支
```bash
git branch                              # 查看分支
git branch name                         # 创建分支
git checkout name                       # 切换分支
git checkout -b name                    # 创建并切换
git merge name                          # 合并
git branch -d name                      # 删除
git push origin --delete name           # 删除远程
```

#### E.3 撤销与回退
```bash
git reset HEAD file                     # 取消add
git checkout -- file                    # 还原工作区
git reset --soft HEAD~1                 # 撤销commit保留修改
git reset --hard HEAD~1                 # 全撤销（危）
git revert commit_hash                  # 安全撤销
git stash / git stash pop               # 暂存/恢复
```

#### E.4 查看
```bash
git status                              # 状态
git log --oneline --graph --all         # 提交历史
git diff                                # 工作区vs暂存区
git diff --staged                       # 暂存区vs仓库
git show commit_hash                    # 查看某次提交
git blame file                          # 每行谁写的
```

---

### 附录F · HTTP状态码大全

| 状态码 | 名称 | 说明 |
|--------|------|------|
| 200 | OK | 成功 |
| 201 | Created | 创建成功 |
| 204 | No Content | 成功但无返回体 |
| 301 | Moved Permanently | 永久重定向 |
| 302 | Found | 临时重定向 |
| 304 | Not Modified | 缓存未修改 |
| 400 | Bad Request | 请求参数有误 |
| 401 | Unauthorized | 未认证 |
| 403 | Forbidden | 无权限 |
| 404 | Not Found | 资源不存在 |
| 405 | Method Not Allowed | 方法不允许 |
| 409 | Conflict | 冲突 |
| 422 | Unprocessable Entity | 无法处理 |
| 429 | Too Many Requests | 请求过多 |
| 500 | Internal Server Error | 服务器内部错误 |
| 502 | Bad Gateway | 网关错误 |
| 503 | Service Unavailable | 服务不可用 |
| 504 | Gateway Timeout | 网关超时 |

---

### 附录G · 常见错误排查指南

#### G.1 数据库连接失败
- 检查：MySQL是否启动 `systemctl status mysql`
- 检查：端口是否正确（默认3306）
- 检查：用户名密码是否正确
- 检查：是否允许远程连接（`bind-address`）
- Go中检查：`db.Ping()` 结果

#### G.2 端口被占用
```bash
# Windows
netstat -ano | findstr :8080
# Linux
lsof -i :8080
# 或
ss -tlnp | grep 8080
```

#### G.3 Go build失败
- 检查Go版本是否满足go.mod要求
- 检查依赖是否下载完整：`go mod tidy`
- CGO问题：`CGO_ENABLED=0 go build`
- 包导入路径是否正确

#### G.4 内存泄露排查
- 用pprof heap分析
- 检查goroutine是否泄露（数量持续增长）
- 检查map是否无限增长
- 检查数据库连接和Redis连接是否正确关闭

#### G.5 接口响应慢
- 看日志中的请求耗时
- 检查慢SQL（`EXPLAIN`）
- 检查Redis是否命中
- 使用Jaeger追踪调用链耗时
- 检查是否少了索引

#### G.6 Docker相关问题
- `docker ps` 看容器状态
- `docker logs` 看容器日志
- 「容器启动就退出」通常是没有前台进程
- 「端口不通」检查 `-p` 映射和防火墙

---

### 附录H · 推荐学习资源

#### H.1 官方文档（必读）
- Go官方文档：https://go.dev/doc/
- Go Tour：https://go.dev/tour/
- Effective Go：https://go.dev/doc/effective_go
- Go Blog：https://go.dev/blog/

#### H.2 在线学习
- Go by Example：https://gobyexample.com/
- Exercism Go Track：https://exercism.org/tracks/go
- LeetCode（Go题解）：https://leetcode.cn/

#### H.3 必读开源项目
- Gin（Web框架）：github.com/gin-gonic/gin
- GORM（ORM）：github.com/go-gorm/gorm
- go-redis：github.com/redis/go-redis
- zap（日志）：github.com/uber-go/zap
- cobra（CLI）：github.com/spf13/cobra

#### H.4 推荐书籍
- 《Go程序设计语言》（Go语言圣经）
- 《Go语言高级编程》
- 《Concurrency in Go》
- 《Designing Data-Intensive Applications》（DDIA，系统设计必读）

#### H.5 社区与资讯
- Go官方周刊：golangweekly.com
- Go Reddit：reddit.com/r/golang
- Go中国社区：gocn.vip
- 掘金Go标签：juejin.cn/tag/Go

#### H.6 学习路线总结
```
第0-2篇（基础准备）→ 第三篇（数据库）→ 第四篇（Web框架）→
第五篇（认证安全）→ 第六篇（消息队列）→ 第七篇（系统设计）→
第八篇（DevOps）→ 第九篇（测试）→ 第十篇（实战项目）
```
- 每完成一篇都应该能做出对应的实战
- 学完了本书，你应该能够独立从零搭建一个生产级的Go Web后端服务

---
*本书完*