# Java 从零到 Spring Boot 后端 — 大纲

> 主线语言：Java 21 | 框架：Spring Boot 3 | 构建工具：Maven | 详细程度：极致详细（零基础到专业级）

---

## 教什么
从计算机基本原理开始，系统学习 Java 语言、数据结构、数据库、Spring Boot 框架、认证授权、消息队列、微服务架构、DevOps、测试，最终完成 6 个实战项目，覆盖后端工程师所需全部知识体系。

## 不教什么
- 前端开发（HTML/CSS/JavaScript 不在范围内，仅在后端API交互层面涉及）
- Android 移动开发
- 大数据/Hadoop/Spark 等数据工程方向
- 深度学习/AI 方向
- 其他 JVM 语言（Kotlin/Scala/Groovy）

## 学完能做什么
- 独立用 Java + Spring Boot 从零搭建生产级 RESTful API 服务
- 设计并优化数据库（MySQL + Redis），编写高性能 SQL
- 实现完整的用户认证授权体系（Spring Security + JWT + OAuth 2.0）
- 使用消息队列（RabbitMQ/Kafka）处理异步任务
- 将应用容器化部署到云服务器，配置 CI/CD 流水线
- 通过常见后端技术面试

## 读者角色
- 主读者：零基础编程新手，想成为 Java 后端工程师
- 次读者：有其他语言经验的开发者转 Java 生态
- 阅读路径：全文顺序阅读，有基础者可跳过第零篇

## 是否需要可视化
是。以下场景建议生成 HTML 可视化：
- 第 00 章：HTTP 请求完整旅程（浏览器→DNS→服务器→数据库→返回）
- 第 09 章：TCP 三次握手/四次挥手
- 第 42 章：JVM 内存模型与 GC 过程
- 第 72 章：Spring Boot 启动流程
- 第 87 章：Spring Security 过滤器链
- 第 94 章：消息队列解耦/削峰/异步模型
- 第 122 章：电商秒杀系统架构

---

## 第零篇：地基 — 计算机与网络基础（15章，Java 视角）

> 目标：搞清楚"计算机到底是什么"、"互联网到底怎么连上的"。用 Java 工具链举例，让读者从一开始就接触 Java 世界观。

| 章节 | 标题 | 核心内容 |
|------|------|----------|
| 00 | 什么是后端工程师 | 餐厅比喻、HTTP请求全旅程、Java后端生态全景、学习路线图 |
| 01 | 计算机的大脑——CPU | CPU原理、指令集、javac→bytecode→JVM→机器码编译链 |
| 02 | 计算机的记忆——内存（RAM） | 内存原理、栈与堆、JVM堆栈模型预览 |
| 03 | 计算机的仓库——硬盘 | 硬盘原理、文件系统、Java IO基础概念 |
| 04 | 操作系统是什么 | 进程/线程、并发vs并行、JVM进程模型 |
| 05 | 终端与命令行入门 | 基础命令、JAVA_HOME与PATH、Maven命令初体验 |
| 06 | IP地址 | IP原理、公网/内网、Java InetAddress演示 |
| 07 | 域名与DNS | DNS查询过程、hosts文件、Java DNS解析演示 |
| 08 | 端口 | 端口概念、常见端口、Spring Boot默认8080 |
| 09 | TCP协议 | 三次握手/四次挥手、Java Socket编程初体验 |
| 10 | UDP协议 | UDP vs TCP、使用场景、Java DatagramSocket演示 |
| 11 | HTTP协议（一） | 请求/响应、方法、状态码、Java HttpURLConnection演示 |
| 12 | HTTP协议（二） | Cookie/Session、缓存机制、CORS跨域 |
| 13 | HTTPS | 对称/非对称加密、数字证书、TLS握手 |
| 14 | WebSocket | HTTP局限、WebSocket原理、使用场景 |

---

## 第一篇：Java 语言从入门到精通（28章）

> 目标：从 Hello World 到能写出生产级 Java 代码。OOP 深入讲解，覆盖 JVM 核心知识。

| 章节 | 标题 | 核心内容 |
|------|------|----------|
| 15 | Java 介绍与环境搭建 | Java历史与版本、JDK 21安装、IDE选择、Hello World |
| 16 | Java 程序的基本结构 | package、import、main方法、javac/javap/jar命令 |
| 17 | 变量与常量 | 基本类型（int/long/float/double/boolean/char）、var、final |
| 18 | 运算符 | 算术、比较、逻辑、位运算、优先级 |
| 19 | 控制流：if 和 switch | if/else、switch表达式（Java 14+）、yield |
| 20 | 控制流：for 和 while | for/while/do-while、增强for、break/continue |
| 21 | 数组 | 声明/初始化/遍历、Arrays工具类、多维数组 |
| 22 | 面向对象（一）：类与对象 | 类/对象/构造器/this、封装、JavaBean |
| 23 | 面向对象（二）：继承 | extends、super、方法重写、Object类 |
| 24 | 面向对象（三）：多态 | 向上转型、动态绑定、instanceof、模式匹配 |
| 25 | 面向对象（四）：抽象类与接口 | abstract、interface、default方法、函数式接口 |
| 26 | 内部类与枚举 | 静态内部类、匿名内部类、enum、record |
| 27 | 字符串深入 | String不可变性、StringBuilder/Buffer、字符串池 |
| 28 | 包装类与自动装箱 | Integer/Long等、自动装箱拆箱、缓存机制 |
| 29 | 异常处理 | try-catch-finally、try-with-resources、自定义异常 |
| 30 | 泛型 | 泛型类/方法、类型擦除、通配符 |
| 31 | 集合框架（一）：List | ArrayList vs LinkedList、Vector、Stack |
| 32 | 集合框架（二）：Set 与 Queue | HashSet/TreeSet/LinkedHashSet、PriorityQueue/ArrayDeque |
| 33 | 集合框架（三）：Map | HashMap原理、TreeMap、LinkedHashMap |
| 34 | 集合框架（四）：深入源码 | HashMap扩容、ConcurrentHashMap、Collections工具类 |
| 35 | Lambda 表达式 | 函数式编程、Lambda语法、方法引用 |
| 36 | Stream API | 创建流、中间操作、终端操作、并行流 |
| 37 | IO 流 | File、字节流/字符流、缓冲流、Files工具类 |
| 38 | 多线程（一）：基础 | Thread/Runnable、线程生命周期、sleep/yield/join |
| 39 | 多线程（二）：同步 | synchronized、volatile、wait/notify |
| 40 | 多线程（三）：高级并发 | 线程池、Callable/Future、CompletableFuture |
| 41 | 虚拟线程（Java 21） | 虚拟线程原理、创建方式、性能对比 |
| 42 | JVM 内存模型与 GC | 堆/栈/方法区、GC算法、常见GC器、调优入门 |
| 43 | 注解与反射 | 内置注解、自定义注解、Class/Field/Method反射、动态代理 |

---

## 第二篇：数据结构与算法（10章，Java 实现）

> 目标：掌握后端开发必备的数据结构与算法，能通过技术面试。

| 章节 | 标题 | 核心内容 |
|------|------|----------|
| 44 | 为什么学数据结构与算法 | 收纳盒比喻、菜谱比喻、后端工程师为什么需要 |
| 45 | 时间复杂度与空间复杂度 | 大O表示法、常见复杂度、代码分析 |
| 46 | 数组与 ArrayList 源码分析 | ArrayList底层数组、扩容机制、性能分析 |
| 47 | 链表 | 单向/双向/循环链表、Java实现、链表vs数组 |
| 48 | 栈与队列 | 栈（一叠盘子）、队列（排队）、Java实现 |
| 49 | 哈希表深入 | 哈希函数、冲突解决、HashMap源码对应 |
| 50 | 树 | 二叉树/BST、四种遍历、Java实现 |
| 51 | 堆与优先队列 | 最大堆/最小堆、PriorityQueue、Top K问题 |
| 52 | 排序算法 | 冒泡/选择/插入/快排/归并、Arrays.sort |
| 53 | 搜索算法与面试题 | 线性/二分/DFS/BFS、经典面试题 |

---

## 第三篇：数据库（17章）

> 目标：从零掌握 MySQL 和 Redis，能用 JDBC/JPA/MyBatis 操作数据库。

| 章节 | 标题 | 核心内容 |
|------|------|----------|
| 54 | 数据库基础与 MySQL 安装 | 关系型数据库概念、MySQL安装、图形化工具 |
| 55 | SQL 基础：DDL 与 DML | CREATE/INSERT/SELECT/UPDATE/DELETE |
| 56 | SQL 进阶：查询与聚合 | WHERE/ORDER BY/LIMIT/GROUP BY/HAVING/聚合函数 |
| 57 | JOIN 多表查询 | INNER/LEFT/RIGHT JOIN、自连接、UNION |
| 58 | 表设计与范式 | 1NF/2NF/3NF、ER图、反范式化 |
| 59 | 索引原理 | B+树、聚簇索引、联合索引、最左前缀 |
| 60 | 索引实战 | EXPLAIN、索引失效场景、覆盖索引 |
| 61 | 事务与隔离级别 | ACID、脏读/幻读/不可重复读、MVCC |
| 62 | 锁机制 | 行锁/表锁、共享锁/排他锁、死锁 |
| 63 | 数据库优化 | 慢查询日志、SQL优化、分库分表简介 |
| 64 | JDBC 入门 | DriverManager、Connection、Statement、PreparedStatement、SQL注入 |
| 65 | 连接池与 DataSource | HikariCP、连接池原理、配置调优 |
| 66 | MyBatis 入门 | 映射文件、动态SQL、与Spring Boot集成 |
| 67 | Spring Data JPA 基础 | Entity/Repository、JPQL、关联映射 |
| 68 | Redis 入门与常用命令 | 五大数据类型、常用命令 |
| 69 | Redis 进阶 | 持久化、过期策略、缓存穿透/击穿/雪崩 |
| 70 | Java 操作 Redis | Spring Data Redis、Jedis、缓存注解 |

---

## 第四篇：Spring Boot 核心（15+1章）

> 目标：从零掌握 Spring Boot 全家桶，能搭建生产级 RESTful API 服务。

| 章节 | 标题 | 核心内容 |
|------|------|----------|
| 70a | RESTful API 设计规范 | REST六大约束、URL设计（名词vs动词）、HTTP方法映射、状态码、统一响应格式 |
| 71 | Spring 框架概述 | IoC/DI/AOP概念、Spring发展史、Spring Boot定位 |
| 72 | Spring Boot 入门 | Spring Initializr、Hello World、启动流程分析 |
| 73 | 依赖注入（IoC 容器） | @Component/@Service/@Repository、@Autowired、Bean生命周期 |
| 74 | 配置管理 | application.yml/properties、@Value/@ConfigurationProperties、多环境 |
| 75 | Spring MVC（一）：控制器 | @RestController/@Controller、@RequestMapping、路径参数 |
| 76 | Spring MVC（二）：请求处理 | @RequestParam/@RequestBody、参数校验 |
| 77 | Spring MVC（三）：响应处理 | 统一响应格式、JSON处理、ResponseEntity |
| 78 | 中间件与拦截器 | Filter、Interceptor、执行顺序、CORS配置 |
| 79 | AOP 切面编程 | @Aspect、切点表达式、日志切面实战 |
| 80 | 异常处理 | @ControllerAdvice/@ExceptionHandler、业务异常体系 |
| 81 | 数据访问：Spring Data JPA 深入 | 查询方法、@Query、分页排序、审计 |
| 82 | 事务管理 | @Transactional、传播行为、隔离级别 |
| 83 | 日志系统 | SLF4J + Logback、日志级别、MDC、Lombok |
| 84 | 文件上传下载 | MultipartFile、静态资源、文件存储方案 |
| 85 | API 文档 | SpringDoc OpenAPI、Swagger UI |

---

## 第五篇：认证授权与安全（8章）

> 目标：掌握用户身份认证和权限控制的所有主流方案，防御常见Web攻击。

| 章节 | 标题 | 核心内容 |
|------|------|----------|
| 86 | 认证基础 | 认证vs授权、密码哈希、bcrypt、Spring Security概述 |
| 87 | Spring Security 入门 | 过滤器链、SecurityContext、表单登录、自定义配置 |
| 88 | JWT 认证实战 | JWT结构、生成/验证、Access Token + Refresh Token |
| 89 | OAuth 2.0 与第三方登录 | 四种授权模式、GitHub/Google登录集成 |
| 90 | RBAC 权限控制 | 用户/角色/权限模型、方法级权限注解 |
| 91 | 常见 Web 攻击防御 | SQL注入、XSS、CSRF原理与Spring Security防护 |
| 92 | 加密基础 | 哈希算法、AES对称加密、RSA非对称加密、数字签名 |
| 93 | HTTPS 与证书管理 | TLS握手、证书链、自签名证书、Let's Encrypt |

---

## 第六篇：消息队列（6章）

> 目标：理解异步处理，掌握 RabbitMQ 和 Kafka，能用 Spring 集成。

| 章节 | 标题 | 核心内容 |
|------|------|----------|
| 94 | 消息队列基础 | 同步vs异步、解耦/削峰/异步、几种模型 |
| 95 | RabbitMQ 入门 | 安装、基本概念、工作队列、发布订阅、路由 |
| 96 | RabbitMQ 进阶 | 消息确认、持久化、死信队列、延迟队列 |
| 97 | Kafka 入门 | 核心概念：Topic/Partition/Consumer Group、顺序读写 |
| 98 | Kafka 进阶 | 可靠性保证、幂等性、Offset管理 |
| 99 | Spring 集成消息队列 | Spring AMQP（RabbitMQ）、Spring Kafka |

---

## 第七篇：系统设计与架构（8章）

> 目标：具备架构思维，能设计中等规模系统，应对系统设计面试。

| 章节 | 标题 | 核心内容 |
|------|------|----------|
| 100 | 设计模式（Java 实现） | 单例/工厂/策略/观察者/依赖注入 |
| 101 | SOLID 原则 | 单一职责/开闭/里氏替换/接口隔离/依赖反转 |
| 102 | 微服务基础 | 单体vs微服务、拆分原则、Spring Cloud概述 |
| 103 | 微服务通信 | REST/gRPC/消息队列、同步vs异步选择 |
| 104 | 分布式基础理论 | CAP定理、BASE理论、Paxos/Raft简介 |
| 105 | 负载均衡与反向代理 | Nginx入门、负载均衡算法、健康检查 |
| 106 | 高并发系统设计 | 缓存策略、限流（令牌桶/漏桶）、熔断降级 |
| 107 | 系统设计面试经典题 | 短链接/秒杀/推送/Feed流系统设计 |

---

## 第八篇：DevOps 与部署（7章）

> 目标：能把代码部署到服务器上，让别人访问到。

| 章节 | 标题 | 核心内容 |
|------|------|----------|
| 108 | Linux 必备知识 | 目录结构、文件权限、用户管理、进程管理、systemd |
| 109 | Shell 脚本基础 | 变量、条件判断、循环、函数、运维脚本 |
| 110 | Git 版本控制 | 基本操作、分支管理、合并冲突、Git工作流 |
| 111 | Maven 深入 | 生命周期、多模块项目、插件、依赖管理 |
| 112 | Docker 容器化 | 镜像/容器、Dockerfile、docker-compose、多阶段构建 |
| 113 | CI/CD（GitHub Actions） | 自动化测试、自动构建、自动部署Java项目 |
| 114 | 云服务部署实战 | 云服务器购买、域名备案、Nginx反向代理、SSL证书、Spring Boot部署 |

---

## 第九篇：测试（4章）

> 目标：写出可靠的代码，掌握测试方法论。

| 章节 | 标题 | 核心内容 |
|------|------|----------|
| 115 | JUnit 5 单元测试 | 断言、生命周期、参数化测试、覆盖率 |
| 116 | Mockito 与测试替身 | Mock/Stub/Spy、行为验证、Spring Boot测试切片 |
| 117 | Spring Boot 集成测试 | @SpringBootTest、Testcontainers、数据库测试 |
| 118 | 性能测试 | JMH基准测试、JMeter压测、JProfiler分析 |

---

## 第十篇：实战项目（6章）

> 目标：把前面学的所有东西串起来，做出能上线的项目。

| 章节 | 标题 | 核心内容 |
|------|------|----------|
| 119 | 项目一：Todo 任务管理 API | CRUD完整实现、统一响应、异常处理、JUnit测试 |
| 120 | 项目二：用户认证系统 | 注册/登录/登出、JWT、RBAC、密码重置 |
| 121 | 项目三：博客系统 | 文章管理、分类标签、评论、Markdown、文件上传 |
| 122 | 项目四：电商秒杀系统 | 商品管理、订单、库存扣减（并发安全）、Redis分布式锁、消息队列异步 |
| 123 | 项目五：IM 即时通讯 | WebSocket、消息存储、在线状态、群聊 |
| 124 | 项目六：微服务电商系统 | 服务拆分、注册中心、gRPC通信、分布式事务 |

---

## 技术栈总览

| 层级 | 技术选型 |
|------|----------|
| 语言 | Java 21（LTS） |
| 框架 | Spring Boot 3.x |
| 构建 | Maven |
| ORM | Spring Data JPA + MyBatis（简介） |
| 数据库 | MySQL 8.0 |
| 缓存 | Redis 7.x |
| 消息队列 | RabbitMQ + Kafka |
| 安全 | Spring Security + JWT + OAuth 2.0 |
| 测试 | JUnit 5 + Mockito + Testcontainers |
| 容器 | Docker + Docker Compose |
| CI/CD | GitHub Actions |
| 文档 | SpringDoc OpenAPI (Swagger) |
| IDE | IntelliJ IDEA（社区版） |

---

## 风格约定

- 参考 `GO从零到后端教程/101-Git版本控制.md` 风格：口语化、比喻丰富、有"想多一点"深度思考、完整代码块、错误vs正确示例、每章末尾小结
- 语言：中文为主，术语保留英文，代码注释可用英文
- 每章末尾含：小结表格（本章学了什么）、自测题（2-3道）
- 产出目录：`java从零到spring boot后端教程/`
- 文件命名：`<序号>-<标题>.md`（如 `00-什么是后端工程师.md`）

---

## 附录（6个）

| 附录 | 标题 | 内容 |
|------|------|------|
| A | Java 标准库速查 | java.lang/java.util/java.io/java.time/java.util.stream/java.util.concurrent 常用类和方法 |
| B | MySQL 命令速查 | DDL/DML/查询/索引/事务/用户管理常用命令 |
| C | Redis 命令速查 | String/Hash/List/Set/Sorted Set + 通用命令 + Spring Data Redis 集成 |
| D | Docker 命令速查 | 镜像/容器/docker-compose/网络/卷常用命令 + Java 多阶段构建示例 |
| E | Git 命令速查 | clone/commit/push/pull/分支/撤销/远程操作 + Java .gitignore 模板 |
| F | 技术术语速查 | 148 个术语，分8类：计算机底层/Java核心/Spring生态/数据库/网络/架构/测试/编程通识 |

---

> **总计：10篇 124章 + 1插章（70a） + 6附录 + 7可视化HTML，覆盖从零基础到高级 Java 后端工程师的全部知识体系。**