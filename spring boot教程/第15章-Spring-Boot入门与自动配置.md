# 第15章：Spring Boot入门与自动配置

## 本章目标

学完本章你将能够：

- 深刻理解Spring Boot诞生的背景——为什么Java开发者对它"相见恨晚"
- 用三种方式创建并运行第一个Spring Boot项目，理解项目结构每一部分的职责
- **从源码级别**剖析`@SpringBootApplication`注解和自动配置的运行机制
- 掌握`@Conditional`条件注解家族，理解Spring Boot"按需配置"的核心智慧
- 熟练使用起步依赖（Starter）管理依赖，解决版本冲突
- 理解"约定优于配置"在Spring Boot中的具体体现

---

> **本章定位**：本章是Spring Boot部分的起点。前14章我们从Java SE一路走到Spring MVC，手写了大量配置——XML的、注解的、JDBC的、MyBatis的。从本章开始，你会发现：原来这些配置Spring Boot都可以帮你自动完成。但请记住——**自动配置不是魔法，理解原理才能真正驾驭它**。

---

## 15.1 为什么需要Spring Boot？

### 15.1.1 没有Spring Boot的年代 — 三大痛点

在Spring Boot诞生之前（2014年以前），用Spring Framework开发一个Web项目，程序员要面对什么？

#### 痛点1：配置地狱

给你看一个真实的Spring MVC项目配置文件树（约2013年的典型项目）：

```
src/main/webapp/WEB-INF/
├── web.xml                      # 配置DispatcherServlet、监听器、编码过滤器
├── applicationContext.xml       # Spring主配置（数据源、Service、事务管理器...）
├── spring-mvc.xml               # Spring MVC配置（视图解析器、静态资源映射...）
├── spring-mybatis.xml           # MyBatis整合（SqlSessionFactory、Mapper扫描...）
├── spring-security.xml          # 安全配置
└── spring-scheduler.xml         # 定时任务配置
```

`web.xml` 片段（感受一下密度）：

```xml
<!-- 这是2013年一个Spring MVC项目的web.xml —— 仅此一个文件就超过100行 -->
<web-app xmlns="http://java.sun.com/xml/ns/javaee" version="2.5">

    <!-- 1. 加载Spring容器 -->
    <context-param>
        <param-name>contextConfigLocation</param-name>
        <param-value>classpath:applicationContext.xml</param-value>
    </context-param>
    <listener>
        <listener-class>org.springframework.web.context.ContextLoaderListener</listener-class>
    </listener>

    <!-- 2. 配置字符编码过滤器（解决中文乱码） -->
    <filter>
        <filter-name>encodingFilter</filter-name>
        <filter-class>org.springframework.web.filter.CharacterEncodingFilter</filter-class>
        <init-param>
            <param-name>encoding</param-name>
            <param-value>UTF-8</param-value>
        </init-param>
    </filter>
    <filter-mapping>
        <filter-name>encodingFilter</filter-name>
        <url-pattern>/*</url-pattern>
    </filter-mapping>

    <!-- 3. 配置Spring MVC核心 — DispatcherServlet -->
    <servlet>
        <servlet-name>dispatcher</servlet-name>
        <servlet-class>org.springframework.web.servlet.DispatcherServlet</servlet-class>
        <init-param>
            <param-name>contextConfigLocation</param-name>
            <param-value>classpath:spring-mvc.xml</param-value>
        </init-param>
        <load-on-startup>1</load-on-startup>
    </servlet>
    <servlet-mapping>
        <servlet-name>dispatcher</servlet-name>
        <url-pattern>/</url-pattern>
    </servlet-mapping>

</web-app>
```

`applicationContext.xml` 中的MyBatis配置：

```xml
<!-- 配置数据源 -->
<bean id="dataSource" class="org.apache.commons.dbcp.BasicDataSource"
      destroy-method="close">
    <property name="driverClassName" value="com.mysql.cj.jdbc.Driver"/>
    <property name="url" value="jdbc:mysql://localhost:3306/ems"/>
    <property name="username" value="root"/>
    <property name="password" value="root"/>
    <property name="initialSize" value="5"/>
    <property name="maxActive" value="20"/>
</bean>

<!-- 配置SqlSessionFactory -->
<bean id="sqlSessionFactory" class="org.mybatis.spring.SqlSessionFactoryBean">
    <property name="dataSource" ref="dataSource"/>
    <property name="mapperLocations" value="classpath:mapper/*.xml"/>
    <property name="typeAliasesPackage" value="com.example.entity"/>
</bean>

<!-- 配置Mapper扫描 -->
<bean class="org.mybatis.spring.mapper.MapperScannerConfigurer">
    <property name="basePackage" value="com.example.mapper"/>
    <property name="sqlSessionFactoryBeanName" value="sqlSessionFactory"/>
</bean>

<!-- 配置事务管理器 -->
<bean id="transactionManager"
      class="org.springframework.jdbc.datasource.DataSourceTransactionManager">
    <property name="dataSource" ref="dataSource"/>
</bean>

<!-- 开启事务注解 -->
<tx:annotation-driven transaction-manager="transactionManager"/>
```

数一数：**7-8个XML文件，每个几十上百行，而且经常因为一个classpath路径少写了`*`导致404。** 这就是"配置地狱"——大量的样板配置既繁琐又易错，严重消耗开发者的精力。

#### 痛点2：依赖版本冲突

一个Spring MVC项目需要引入以下依赖：

| 依赖 | 作用 |
|------|------|
| spring-core / spring-beans / spring-context | Spring IoC核心 |
| spring-web / spring-webmvc | Spring MVC |
| spring-jdbc / spring-tx | 事务管理 |
| spring-aop / aspectjweaver | AOP |
| jackson-databind | JSON序列化 |
| mysql-connector-java | MySQL驱动 |
| mybatis / mybatis-spring | MyBatis整合 |
| druid / HikariCP | 连接池 |
| logback-classic / slf4j-api | 日志 |
| servlet-api / jsp-api | Servlet API |
| commons-lang3 / guava | 工具库 |
| ... 更多 | ... |

**每个依赖都有自己的版本号，而且版本之间还存在兼容性约束：**

```
MyBatis 3.5.9  <── 需要 spring-jdbc >= 5.3.0
MyBatis-Spring 2.1.0  <── 需要 MyBatis >= 3.5.0
Jackson 2.13.0  <── 需要 spring-webmvc 5.x
但 spring-webmvc 5.3.20 又需要 spring-core 5.3.20
而另一个库（如shiro-spring）可能还依赖 spring-core 5.2.x
→ 版本冲突！Maven会选一个"最近的"，但不一定是兼容的那个！
```

你可以用 `mvn dependency:tree` 查看依赖树——通常在整合第三方库时，输出了几百行，其中几个依赖版本标着红色冲突警告。手动排冲突（exclusions）耗时且容易引入新问题。

#### 痛点3：启动繁琐

传统的Spring Web项目需要部署到外部Tomcat：

```
1. 写完代码
2. mvn package  →  生成 .war 包
3. 把 .war 拷贝到 Tomcat 的 webapps/ 目录
4. 启动/重启 Tomcat（shutdown.sh → startup.sh）
5. 通过 http://localhost:8080/项目名/ 访问
```

每次改一行代码都要经历这几步。而且你得先在服务器上**安装好Tomcat并配置好端口、JVM参数**。

更让人抓狂的是：不同操作系统、不同Tomcat版本、不同JDK版本之间经常出现莫名其妙的兼容性问题。比如"这个项目在IDEA里跑得好好的，部署到服务器Tomcat就404"——这种问题排查起来少则半小时，多则一整天。

### 15.1.2 Spring Boot的三大解决之道

Spring Boot不是新的框架——它是Spring Framework的**脚手架**，基于Spring Framework 5.x/6.x（Boot 2.x→5.x, Boot 3.x→6.x）。它用三种核心能力解决了上述三大痛点：

```
Spring Framework（地基）
        │
        ▼
Spring Boot（脚手架/快速启动器）
   │         │           │
   ▼         ▼           ▼
自动配置    起步依赖    内嵌服务器
（零XML）  （版本统一）  （java -jar）
```

#### 解决1：自动配置 → 零XML

你只需要加一个依赖：

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-web</artifactId>
</dependency>
```

Spring Boot会自动：
- 启动内嵌Tomcat
- 配置DispatcherServlet
- 配置字符编码过滤器（UTF-8）
- 配置Jackson JSON序列化
- 配置静态资源默认路径
- 注册默认的`/error`错误页面

**不需要一行XML，不需要一个`web.xml`。** 如果加了`mybatis-spring-boot-starter`，它还会自动创建`SqlSessionFactory`、扫描Mapper。

这就是**自动配置**——Spring Boot根据你引入的依赖（classpath中有哪些jar包），自动推断你需要什么配置并创建对应的Bean。本章15.3和15.4节将从源码级别深入剖析这个过程。

#### 解决2：起步依赖（Starter）→ 版本统一

```xml
<!-- 传统方式：手动管理几十个依赖的版本 -->
<dependency><groupId>org.springframework</groupId><artifactId>spring-webmvc</artifactId><version>6.1.0</version></dependency>
<dependency><groupId>com.fasterxml.jackson.core</groupId><artifactId>jackson-databind</artifactId><version>2.15.0</version></dependency>
<!-- ...还要十几个... -->

<!-- Spring Boot方式：一个Starter搞定 -->
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-web</artifactId>
    <!-- 无需写版本号！版本由spring-boot-starter-parent统一管理 -->
</dependency>
```

所有Spring Boot官方Starter的版本号都继承自`spring-boot-starter-parent`（它又继承自`spring-boot-dependencies`这个BOM）。你不需要指定版本号，也不需要担心版本冲突——Spring Boot团队已经替你测试过所有组合。

**BOM（Bill of Materials，物料清单）** 是Maven提供的一种版本管理机制：在一个pom.xml中集中定义一大批依赖的版本号，其他项目通过`<dependencyManagement>`引入该BOM后，即可不写版本号自动使用BOM中定义的版本。

#### 解决3：内嵌服务器 → 一键启动

Spring Boot将Tomcat、Jetty或Undertow直接打包进你的应用jar中：

```
your-app.jar
├── BOOT-INF/
│   ├── classes/           ← 你的代码
│   ├── lib/               ← 所有依赖jar（包含tomcat-embed-core-10.1.x.jar！）
│   └── classpath.idx
├── META-INF/
└── org/springframework/boot/loader/   ← Spring Boot的类加载器
```

启动方式变成了一行命令：

```bash
java -jar your-app.jar
```

不需要安装Tomcat，不需要部署war，不需要配置服务器。你的jar包里自带了Web服务器——**一个jar包就是一个完整的可运行的应用**。

### 15.1.3 "约定优于配置"深度解读

Spring Boot的设计哲学是"**约定优于配置**（Convention over Configuration）"。这不是一句空洞的口号，它在Spring Boot中有非常具体的体现：

**例1：配置文件位置约定**

不用在`web.xml`中指定Spring配置文件的位置，Spring Boot自动在以下位置查找`application.yml`：

```
优先级从高到低：
1. 当前目录的 /config 子目录：./config/application.yml
2. 当前目录：./application.yml
3. classpath中的 /config 包：classpath:/config/application.yml
4. classpath根目录：classpath:/application.yml
```

你把`application.yml`放到`src/main/resources/`下，它就自动被加载——这就是约定。

**例2：组件扫描路径约定**

```java
@SpringBootApplication  // 默认扫描该类所在包及所有子包
public class Application {
    public static void main(String[] args) {
        SpringApplication.run(Application.class, args);
    }
}
```

你不需要写`@ComponentScan("com.example")`——只要你的所有业务类（Controller、Service、Mapper等）都放在`Application`类所在的包或子包下，它们就会被自动扫描到。**前提：启动类必须放在根包位置（如`com.example`），而不能放在子包（如`com.example.config`）中。**

**例3：静态资源路径约定**

不用配置`<mvc:resources>`，以下路径下的文件自动作为静态资源：

- `classpath:/static/`
- `classpath:/public/`
- `classpath:/resources/`
- `classpath:/META-INF/resources/`

你把`logo.png`放到`src/main/resources/static/`，然后用`http://localhost:8080/logo.png`即可访问——这就是约定。

> **约定的本质**：Spring Boot预设了最常用、最合理的默认配置。你按约定来，零配置即可运行。当你需要定制时，可以在`application.yml`中覆盖默认值，或用`@Bean`替换默认Bean。约定让80%的场景变得简单，剩下20%的定制场景依然灵活。

---

## 15.2 第一个Spring Boot项目

理解了"为什么要用"之后，让我们动手创建第一个Spring Boot 3.x项目。

### 15.2.1 创建项目的方式

#### 方式一：Spring Initializr（在线生成，推荐）

1. 打开浏览器访问 [https://start.spring.io](https://start.spring.io)
2. 配置项目基本信息：

```
Project:   Maven（选Maven项目结构）
Language:  Java
Spring Boot:  3.3.x（选最新的稳定版3.x，如3.3.0）
Group:     com.example
Artifact:  springboot-demo
Name:      springboot-demo
Package name:  com.example.springbootdemo
Packaging: Jar
Java:      17
```

3. 添加依赖（点击右侧"ADD DEPENDENCIES"按钮）：
   - **Spring Web**（spring-boot-starter-web）
   - **Lombok**（简化JavaBean代码）
   - **MySQL Driver**（mysql-connector-j）
   - **MyBatis Framework**（mybatis-spring-boot-starter）

4. 点击"GENERATE"下载压缩包，解压后用IDEA打开。

#### 方式二：IDEA直接创建

1. IDEA → File → New → Project
2. 左侧选择"Spring Initializr"
3. 配置与方式一相同
4. 点击Next，选择依赖后Finish

### 15.2.2 项目结构详解

Spring Boot 3.x项目生成后的完整目录结构：

```
springboot-demo/
├── pom.xml                              # Maven构建配置（依赖管理核心）
├── src/
│   ├── main/
│   │   ├── java/
│   │   │   └── com/example/springbootdemo/
│   │   │       └── SpringbootDemoApplication.java    # 启动类 ★
│   │   └── resources/
│   │       ├── static/                  # 静态资源（js/css/图片）
│   │       ├── templates/              # 模板文件（Thymeleaf/FreeMarker）
│   │       └── application.yml         # 主配置文件 ★
│   └── test/
│       └── java/
│           └── com/example/springbootdemo/
│               └── SpringbootDemoApplicationTests.java  # 空测试类
└── HELP.md                             # Spring Boot快速参考（可删除）
```

让我们逐一理解每个部分。

#### pom.xml — 项目的心脏

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0
         https://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <!-- 1. 继承spring-boot-starter-parent：统一管理所有版本 -->
    <parent>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-parent</artifactId>
        <version>3.3.0</version>
        <relativePath/>  <!-- 从Maven仓库查找parent，不从本地相对路径 -->
    </parent>

    <groupId>com.example</groupId>
    <artifactId>springboot-demo</artifactId>
    <version>0.0.1-SNAPSHOT</version>
    <name>springboot-demo</name>

    <properties>
        <java.version>17</java.version>   <!-- JDK版本 -->
    </properties>

    <!-- 2. 起步依赖：直接引入Starter -->
    <dependencies>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
        </dependency>

        <dependency>
            <groupId>com.mysql</groupId>
            <artifactId>mysql-connector-j</artifactId>
            <scope>runtime</scope>  <!-- 运行时才需要，编译期不需要 -->
        </dependency>

        <dependency>
            <groupId>org.mybatis.spring.boot</groupId>
            <artifactId>mybatis-spring-boot-starter</artifactId>
            <version>3.0.3</version>
        </dependency>

        <dependency>
            <groupId>org.projectlombok</groupId>
            <artifactId>lombok</artifactId>
            <optional>true</optional>  <!-- 不传递给依赖此项目的子模块 -->
        </dependency>

        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-test</artifactId>
            <scope>test</scope>
        </dependency>
    </dependencies>

    <!-- 3. 构建插件：Spring Boot Maven Plugin -->
    <build>
        <plugins>
            <plugin>
                <groupId>org.springframework.boot</groupId>
                <artifactId>spring-boot-maven-plugin</artifactId>
                <configuration>
                    <excludes>
                        <exclude>
                            <groupId>org.projectlombok</groupId>
                            <artifactId>lombok</artifactId>
                        </exclude>
                    </excludes>
                </configuration>
            </plugin>
        </plugins>
    </build>
</project>
```

重点解释几个关键配置：

**`spring-boot-starter-parent`**：这是所有Spring Boot项目的父POM。它里面通过`<dependencyManagement>`引入了`spring-boot-dependencies`（真正的版本管理BOM）。你可以点进这个parent看到：

```xml
<!-- spring-boot-starter-parent 内部（简化版） -->
<parent>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-dependencies</artifactId>
    <version>3.3.0</version>
</parent>

<properties>
    <java.version>17</java.version>
    <maven.compiler.source>${java.version}</maven.compiler.source>
    <maven.compiler.target>${java.version}</maven.compiler.target>
</properties>
```

`spring-boot-dependencies`中定义了**几百个**三方库的版本：

```xml
<!-- spring-boot-dependencies内部（仅展示部分） -->
<properties>
    <spring-framework.version>6.1.8</spring-framework.version>
    <tomcat.version>10.1.20</tomcat.version>
    <jackson.version>2.17.0</jackson.version>
    <mysql.version>8.3.0</mysql.version>
    <hikaricp.version>5.1.0</hikaricp.version>
    <mybatis-spring-boot.version>3.0.3</mybatis-spring-boot.version>
    <lombok.version>1.18.32</lombok.version>
    <!-- ... 共几百个 -->
</properties>
```

所以当你在自己的pom.xml中写`spring-boot-starter-web`且不指定版本时，Maven会向上追溯到`spring-boot-dependencies`中定义的版本——**版本统一管理就此实现**。

**`spring-boot-maven-plugin`**：这个插件做三件事：
1. 将项目打包为**可执行的Fat Jar**（包含所有依赖），而非普通的jar
2. 提供 `mvn spring-boot:run` 命令直接启动应用
3. 可以将Fat Jar按层级解压（layertools），优化Docker镜像构建

#### 启动类详解

```java
package com.example.springbootdemo;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication                       // ← 这个注解是灵魂
public class SpringbootDemoApplication {
    public static void main(String[] args) {
        SpringApplication.run(SpringbootDemoApplication.class, args);
    }
}
```

关键点：

- **`@SpringBootApplication`**：这是一个组合注解，本章15.3节将源码级深入解剖
- **`SpringApplication.run()`**：启动Spring Boot应用，执行以下流程：
  1. 创建`ApplicationContext`（Spring容器）
  2. 解析`application.yml`配置
  3. 执行自动配置
  4. 启动内嵌Tomcat
  5. 部署应用到Tomcat
- **`main`方法**：这是应用的入口，你可以在IDEA里像普通Java程序一样右键运行

#### 启动类位置要求 — 最容易犯的错

> 🚨 **致命坑点：启动类必须放在所有业务包的父包下！**

这是Spring Boot新人最容易犯的错误——把启动类随便放，结果404一整天。

**正确的包结构**：

```
com.example.springbootdemo              ← 启动类在这里（根包）
├── SpringbootDemoApplication.java       ← @SpringBootApplication
├── controller/
│   └── HelloController.java            ← 能被扫描到 ✅
├── service/
│   └── HelloService.java               ← 能被扫描到 ✅
├── mapper/
│   └── UserMapper.java                 ← 能被扫描到 ✅
└── config/
    └── MyConfig.java                   ← 能被扫描到 ✅
```

**错误的包结构**：

```
com.example.springbootdemo
├── config/
│   └── SpringbootDemoApplication.java  ← ❌ 启动类放在config子包下！
├── controller/
│   └── HelloController.java           ← ❌ 和启动类平级，扫不到！
└── service/
    └── HelloService.java               ← ❌ 扫不到！
```

**为什么**？因为`@SpringBootApplication`中的`@ComponentScan`默认扫描**启动类所在包及其所有子包**。当启动类在`com.example.springbootdemo.config`下时，它只扫描`config`包及其子包——`controller`和`service`平级，不在扫描范围内。

**修复方式有两种**：

```java
// 方式1：把启动类移回根包（推荐）
package com.example.springbootdemo;
@SpringBootApplication
public class SpringbootDemoApplication { ... }

// 方式2：手动指定扫描路径
@SpringBootApplication(scanBasePackages = "com.example.springbootdemo")
public class SpringbootDemoApplication { ... }
```

### 15.2.3 编写第一个Controller验证项目

创建`src/main/java/com/example/springbootdemo/controller/HelloController.java`：

```java
package com.example.springbootdemo.controller;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class HelloController {

    @GetMapping("/hello")
    public String hello() {
        return "Hello, Spring Boot 3!";
    }
}
```

### 15.2.4 运行项目的三种方式

#### 方式1：IDEA中直接运行

在`SpringbootDemoApplication`类的`main`方法左侧点击绿色三角形，选择"Run"。

#### 方式2：Maven命令运行

```bash
# 在项目根目录（pom.xml所在目录）执行
mvn spring-boot:run
```

#### 方式3：打包后运行

```bash
# 第1步：跳过测试打包
mvn clean package -DskipTests

# 第2步：运行jar包
java -jar target/springboot-demo-0.0.1-SNAPSHOT.jar
```

运行成功后，控制台会输出类似：

```
  .   ____          _            __ _ _
 /\\ / ___'_ __ _ _(_)_ __  __ _ \ \ \ \
( ( )\___ | '_ | '_| | '_ \/ _` | \ \ \ \
 \\/  ___)| |_)| | | | | || (_| |  ) ) ) )
  '  |____| .__|_| |_|_| |_\__, | / / / /
 =========|_|==============|___/=/_/_/_/
 :: Spring Boot ::                (v3.3.0)

2026-05-22T14:30:00.123+08:00  INFO 12345 --- [main]
  com.example.springbootdemo.SpringbootDemoApplication : Starting
  SpringbootDemoApplication using Java 17.0.8 ...
2026-05-22T14:30:01.456+08:00  INFO 12345 --- [main]
  o.s.b.w.embedded.tomcat.TomcatWebServer : Tomcat started on port 8080 (http) ...
2026-05-22T14:30:01.567+08:00  INFO 12345 --- [main]
  com.example.springbootdemo.SpringbootDemoApplication : Started
  SpringbootDemoApplication in 1.876 seconds (process running for 2.345)
```

看到 `Tomcat started on port 8080` 就表示成功了！打开浏览器访问 `http://localhost:8080/hello`，你会看到：

```
Hello, Spring Boot 3!
```

#### 端口冲突解决

> 🚨 **坑点：端口8080被占用**

最常见的启动失败就是这个：

```
***************************
APPLICATION FAILED TO START
***************************

Description:
Web server failed to start. Port 8080 was already in use.

Action:
Identify and stop the process that's listening on port 8080 or configure
this application to listen on another port.
```

**解决方案1：换端口**（在`application.yml`中配置）：

```yaml
server:
  port: 8081
```

**解决方案2：终止占用端口的进程**：

Windows PowerShell：

```powershell
# 查找占用8080端口的进程ID
netstat -ano | findstr :8080
# 输出: TCP  0.0.0.0:8080  0.0.0.0:0  LISTENING  12345
# 杀掉该进程（12345是PID）
taskkill /PID 12345 /F
```

macOS/Linux：

```bash
lsof -i :8080
# 输出: java  12345 user ... TCP *:8080 (LISTEN)
kill -9 12345
```

#### application.yml — 全局配置文件

Spring Boot会自动加载`src/main/resources/application.yml`作为全局配置。YAML语法要点：

```yaml
# 层级结构（缩进必须是空格，不能用Tab！）
server:
  port: 8081                                    # 端口

spring:
  application:
    name: springboot-demo                        # 应用名
  datasource:
    url: jdbc:mysql://localhost:3306/ems         # 数据源
    username: root
    password: root
    driver-class-name: com.mysql.cj.jdbc.Driver

# 列表语法
my-list:
  - item1
  - item2
  - item3
```

> 🚨 **坑点：YAML缩进不能用Tab！必须用空格（通常2个或4个空格）！** 这是YAML语法规范，如果混用Tab和空格，Spring Boot会报`mapping values are not allowed here`之类的解析错误。

---

## 15.3 @SpringBootApplication 解密

`@SpringBootApplication`是Spring Boot最核心的注解。它看似简单，实为一个**三合一的组合注解**。让我们从源码级别逐步拆解。

### 15.3.1 点击源码：三层结构

在IDEA中按住Ctrl点击`@SpringBootApplication`进入源码（Spring Boot 3.x）：

```java
// Spring Boot 3.x 中 @SpringBootApplication 的源码
@Target(ElementType.TYPE)
@Retention(RetentionPolicy.RUNTIME)
@Documented
@Inherited
@SpringBootConfiguration          // 第一层：标记为配置类
@EnableAutoConfiguration          // 第二层：开启自动配置（核心！）
@ComponentScan(                    // 第三层：组件扫描
    excludeFilters = {
        @Filter(type = FilterType.CUSTOM, classes = TypeExcludeFilter.class),
        @Filter(type = FilterType.CUSTOM,
                classes = AutoConfigurationExcludeFilter.class)
    }
)
public @interface SpringBootApplication {

    // 覆盖 @ComponentScan 的 basePackages
    @AliasFor(annotation = ComponentScan.class, attribute = "basePackages")
    String[] scanBasePackages() default {};

    // 覆盖 @EnableAutoConfiguration 的 exclude
    @AliasFor(annotation = EnableAutoConfiguration.class, attribute = "exclude")
    Class<?>[] exclude() default {};

    // 覆盖 @EnableAutoConfiguration 的 excludeName
    @AliasFor(annotation = EnableAutoConfiguration.class, attribute = "excludeName")
    String[] excludeName() default {};

    // ... 其他属性
}
```

可以看到三个关键子注解。`@AliasFor`是Spring提供的注解属性别名机制——比如`@SpringBootApplication(scanBasePackages = "com.example")`等价于`@ComponentScan(basePackages = "com.example")`。

### 15.3.2 第一层：@SpringBootConfiguration

```java
@Target(ElementType.TYPE)
@Retention(RetentionPolicy.RUNTIME)
@Documented
@Configuration              // ← 核心就是这个 @Configuration
@Indexed
public @interface SpringBootConfiguration {

    @AliasFor(annotation = Configuration.class)
    boolean proxyBeanMethods() default true;
}
```

`@SpringBootConfiguration`本身只是给`@Configuration`换了个名字。它的作用是把启动类标注为Spring的配置类——这样你就可以在启动类中定义`@Bean`方法了。

### 15.3.3 第三层：@ComponentScan

```java
@ComponentScan(
    excludeFilters = {
        @Filter(type = FilterType.CUSTOM, classes = TypeExcludeFilter.class),
        @Filter(type = FilterType.CUSTOM, classes = AutoConfigurationExcludeFilter.class)
    }
)
```

`@ComponentScan`告诉Spring扫描哪些包中的`@Component`、`@Service`、`@Controller`、`@Repository`等注解类，创建对应的Bean。

由于没有指定`basePackages`，默认扫描**声明此注解的类所在的包及所有子包**。这就是为什么启动类必须放在根包——它决定了扫描范围。

两个`excludeFilters`用于排除不需要扫描的类：
- `TypeExcludeFilter`：用于Spring Boot测试时的排除逻辑
- `AutoConfigurationExcludeFilter`：排除自动配置类本身（它们通过`@EnableAutoConfiguration`的机制加载，不需要`@ComponentScan`扫描）

> 🚨 **坑点：自己写`@ComponentScan`会覆盖默认扫描路径**

```java
// ❌ 危险：显式写@ComponentScan会覆盖@SpringBootApplication中默认的扫描！
@SpringBootApplication
@ComponentScan("com.example.controller")  // 只扫描controller包！
public class Application { ... }
// 结果：service包、mapper包中的@Component全部扫不到！

// ✅ 正确1：使用scanBasePackages属性追加扫描路径
@SpringBootApplication(scanBasePackages = {"com.example", "com.thirdparty"})

// ✅ 正确2：如果一定要自定义@ComponentScan，确保包含根包
@SpringBootApplication
@ComponentScan(basePackages = {
    "com.example.springbootdemo",
    "com.thirdparty.lib"
})
```

### 15.3.4 第二层：@EnableAutoConfiguration — 自动配置的引擎

这是三合一中最核心的注解，也是Spring Boot自动配置的入口。

```java
@Target(ElementType.TYPE)
@Retention(RetentionPolicy.RUNTIME)
@Documented
@Inherited
@AutoConfigurationPackage                // 记录自动配置包名
@Import(AutoConfigurationImportSelector.class)  // ★ 核心：导入自动配置选择器
public @interface EnableAutoConfiguration {
    String ENABLED_OVERRIDE_PROPERTY = "spring.boot.enableautoconfiguration";
    Class<?>[] exclude() default {};
    String[] excludeName() default {};
}
```

关键在`@Import(AutoConfigurationImportSelector.class)`。`@Import`是Spring的原生注解，用于导入一个类到容器中。这里导入的`AutoConfigurationImportSelector`是一个实现了`ImportSelector`接口的类——Spring会在处理`@Import`时调用它的`selectImports()`方法，返回一组需要被加载的配置类的全限定名。

> 这就是Spring Boot自动配置的秘密入口：**一个`ImportSelector`能够通过编程方式决定哪些配置类需要被加载**。

---

## 15.4 自动配置原理 — 源码级深入

这是本章最硬核的部分，也是面试最喜欢问的内容。我将带你从`AutoConfigurationImportSelector`开始，逐层深入到Spring Boot如何加载`spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports`、如何通过`@Conditional`条件判断来控制Bean的创建。

### 15.4.1 自动配置触发链路

整个自动配置的触发链路如下：

```
SpringApplication.run()
    │
    ▼
refresh() → invokeBeanFactoryPostProcessors()
    │
    ▼
ConfigurationClassPostProcessor（处理@Configuration类）
    │
    ▼
发现启动类上的 @SpringBootApplication
    │
    ▼
处理其中的 @EnableAutoConfiguration
    │
    ▼
处理其中的 @Import(AutoConfigurationImportSelector.class)
    │
    ▼
调用 AutoConfigurationImportSelector.selectImports()
    │
    ├──① 读取 spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports
    │     （Spring Boot 2.x放在 spring.factories 的
    │      org.springframework.boot.autoconfigure.EnableAutoConfiguration 键下）
    │
    ├──② 应用 exclude 过滤（用户手动排除的自动配置类）
    │
    ├──③ 应用 @Conditional 条件过滤（每个自动配置类上的条件注解）
    │
    └──④ 将符合条件的配置类的全限定名返回给Spring
          → Spring将其作为@Configuration类处理
          → 执行其中的@Bean方法
          → 创建对应的Bean放入容器
```

### 15.4.2 存储自动配置类的文件 — Spring Boot 3.x的变化

**重要变化**：Spring Boot 2.x使用`META-INF/spring.factories`文件，Spring Boot 3.x改为使用`META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports`文件。

**为什么改**？`spring.factories`是一个通用文件，里面可以配置很多种类型的扩展（自动配置、监听器、初始化器等），所有内容混在一个文件里。Spring Boot 3.x将自动配置类的列表独立到专属文件中，更清晰、加载更快。

你可以在IDE中找到`spring-boot-autoconfigure-3.3.0.jar`，打开`META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports`：

```
# 该文件列出了所有自动配置类（Spring Boot 3.3.0 约150+行）
org.springframework.boot.autoconfigure.admin.SpringApplicationAdminJmxAutoConfiguration
org.springframework.boot.autoconfigure.aop.AopAutoConfiguration
org.springframework.boot.autoconfigure.cache.CacheAutoConfiguration
org.springframework.boot.autoconfigure.context.ConfigurationPropertiesAutoConfiguration
org.springframework.boot.autoconfigure.dao.PersistenceExceptionTranslationAutoConfiguration
org.springframework.boot.autoconfigure.data.jpa.JpaRepositoriesAutoConfiguration
org.springframework.boot.autoconfigure.data.redis.RedisAutoConfiguration
org.springframework.boot.autoconfigure.data.web.SpringDataWebAutoConfiguration
org.springframework.boot.autoconfigure.flyway.FlywayAutoConfiguration
org.springframework.boot.autoconfigure.freemarker.FreeMarkerAutoConfiguration
org.springframework.boot.autoconfigure.gson.GsonAutoConfiguration
org.springframework.boot.autoconfigure.http.HttpMessageConvertersAutoConfiguration
org.springframework.boot.autoconfigure.integration.IntegrationAutoConfiguration
org.springframework.boot.autoconfigure.jackson.JacksonAutoConfiguration
org.springframework.boot.autoconfigure.jdbc.DataSourceAutoConfiguration
org.springframework.boot.autoconfigure.jdbc.JdbcTemplateAutoConfiguration
org.springframework.boot.autoconfigure.jms.JmsAutoConfiguration
org.springframework.boot.autoconfigure.jmx.JmxAutoConfiguration
org.springframework.boot.autoconfigure.mail.MailSenderAutoConfiguration
org.springframework.boot.autoconfigure.orm.jpa.HibernateJpaAutoConfiguration
org.springframework.boot.autoconfigure.security.servlet.SecurityAutoConfiguration
org.springframework.boot.autoconfigure.task.TaskExecutionAutoConfiguration
org.springframework.boot.autoconfigure.task.TaskSchedulingAutoConfiguration
org.springframework.boot.autoconfigure.thymeleaf.ThymeleafAutoConfiguration
org.springframework.boot.autoconfigure.transaction.TransactionAutoConfiguration
org.springframework.boot.autoconfigure.validation.ValidationAutoConfiguration
org.springframework.boot.autoconfigure.web.client.RestTemplateAutoConfiguration
org.springframework.boot.autoconfigure.web.embedded.EmbeddedWebServerFactoryCustomizerAutoConfiguration
org.springframework.boot.autoconfigure.web.servlet.DispatcherServletAutoConfiguration
org.springframework.boot.autoconfigure.web.servlet.ServletWebServerFactoryAutoConfiguration
org.springframework.boot.autoconfigure.web.servlet.WebMvcAutoConfiguration
org.springframework.boot.autoconfigure.web.servlet.error.ErrorMvcAutoConfiguration
org.springframework.boot.autoconfigure.websocket.servlet.WebSocketServletAutoConfiguration
# ... 共约150个自动配置类
```

**每个自动配置类在被加载前都要经过条件判断**。这个条件判断就是通过`@Conditional`系列注解实现的。

### 15.4.3 @Conditional 条件注解家族

Spring Boot定义了一系列`@Conditional`派生注解，每一个都代表一种条件判断逻辑：

| 注解 | 条件逻辑 | 常见使用场景 |
|------|----------|-------------|
| `@ConditionalOnClass` | 当classpath中存在指定类时生效 | 检测驱动类、第三方库是否存在 |
| `@ConditionalOnMissingClass` | 当classpath中不存在指定类时生效 | 在没有某库时使用降级方案 |
| `@ConditionalOnBean` | 当容器中存在指定Bean时生效 | 依赖其他自动配置的结果 |
| `@ConditionalOnMissingBean` | 当容器中不存在指定Bean时生效 | 用户自己定义Bean后自动配置不生效 |
| `@ConditionalOnProperty` | 当配置文件中某属性为指定值时生效 | 通过配置开关功能 |
| `@ConditionalOnResource` | 当classpath中存在指定资源文件时生效 | 检测配置文件是否存在 |
| `@ConditionalOnWebApplication` | 当应用是Web应用时生效 | Web相关配置 |
| `@ConditionalOnNotWebApplication` | 当应用不是Web应用时生效 | 非Web环境配置 |
| `@ConditionalOnExpression` | 当SpEL表达式为true时生效 | 复杂条件判断 |
| `@ConditionalOnJava` | 当JDK版本满足条件时生效 | 不同JDK版本使用不同实现 |
| `@ConditionalOnSingleCandidate` | 当指定类型的Bean只有一个或有主Bean时生效 | 自动注入时确保唯一性 |
| `@ConditionalOnCloudPlatform` | 当运行在指定云平台时生效 | 云环境特定配置 |

#### 每个条件的代码示例

**@ConditionalOnClass — 类存在时才加载**：

```java
@Configuration(proxyBeanMethods = false)
@ConditionalOnClass({ DataSource.class, EmbeddedDatabaseType.class })
// ↑ classpath中有DataSource.class和EmbeddedDatabaseType.class时，此配置类才生效
public class DataSourceAutoConfiguration {
    // ...
}
```

**@ConditionalOnMissingBean — 用户没定义时才用默认的**：

```java
@Bean
@ConditionalOnMissingBean
// ↑ 如果容器中还没有DataSource Bean（用户没自己定义），就创建一个默认的
public DataSource dataSource() {
    return ...;
}
```

这是Spring Boot"约定优于配置"的核心体现：**你可以通过自己定义`@Bean`来覆盖任何Spring Boot的默认配置**。

**@ConditionalOnProperty — 配置驱动**：

```java
@Bean
@ConditionalOnProperty(name = "app.cache.enabled", havingValue = "true", matchIfMissing = false)
// ↑ 只有当你在application.yml中配置了 app.cache.enabled=true 时，这个Bean才创建
public CacheManager cacheManager() {
    return new ConcurrentMapCacheManager();
}
```

**@ConditionalOnWebApplication — Web环境判断**：

```java
@Configuration(proxyBeanMethods = false)
@ConditionalOnWebApplication(type = ConditionalOnWebApplication.Type.SERVLET)
// ↑ 仅当是Servlet Web应用时生效（非Reactive Web）
public class WebMvcAutoConfiguration {
    // ...
}
```

### 15.4.4 实战：以 DataSourceAutoConfiguration 为例走一遍自动配置流程

假设你的项目引入了`spring-boot-starter-jdbc`（或通过`spring-boot-starter-web`间接引入），classpath中就有了`DataSource`类和HikariCP连接池。Spring Boot的自动配置会经历以下步骤：

**第1步：读取配置类列表**

`AutoConfigurationImportSelector`从`spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports`中读到`DataSourceAutoConfiguration`的全限定名。

**第2步：执行条件判断**

打开`DataSourceAutoConfiguration`源码：

```java
@AutoConfiguration(after = SqlInitializationAutoConfiguration.class)
// ↑ Spring Boot 3.x新增的@AutoConfiguration注解，可控制加载顺序（after/before）
@ConditionalOnClass({ DataSource.class, EmbeddedDatabaseType.class })
// ↑ 条件1：classpath中有DataSource.class和EmbeddedDatabaseType.class
@EnableConfigurationProperties(DataSourceProperties.class)
// ↑ 将application.yml中以spring.datasource为前缀的属性绑定到DataSourceProperties对象
@Import({ DataSourcePoolMetadataProvidersConfiguration.class,
          DataSourceCheckpointRestoreConfiguration.class })
public class DataSourceAutoConfiguration {

    @Configuration(proxyBeanMethods = false)
    @Conditional(PooledDataSourceCondition.class)
    @ConditionalOnMissingBean({ DataSource.class, XADataSource.class })
    // ↑ 条件2：容器中没有用户自定义的DataSource Bean
    @Import({ DataSourceConfiguration.Hikari.class,    // HikariCP
              DataSourceConfiguration.Tomcat.class,    // Tomcat连接池
              DataSourceConfiguration.Dbcp2.class,     // DBCP2
              DataSourceConfiguration.OracleUcp.class, // Oracle UCP
              DataSourceConfiguration.Generic.class,   // 通用
              DataSourceJmxConfiguration.class })
    static class PooledDataSourceConfiguration {
        // 这个内部配置类根据classpath中存在的连接池，选择对应的DataSource创建
    }
}
```

**第3步：DataSourceConfiguration.Hikari 再次条件判断**

```java
// DataSourceConfiguration 内部类
@Configuration(proxyBeanMethods = false)
@ConditionalOnClass(HikariDataSource.class)       // 条件3：有HikariCP的类
@ConditionalOnMissingBean(DataSource.class)        // 条件4：用户没定义DataSource
@ConditionalOnProperty(name = "spring.datasource.type",
                       havingValue = "com.zaxxer.hikari.HikariDataSource",
                       matchIfMissing = true)      // 条件5：没显式指定其他连接池类型
static class Hikari {
    @Bean
    @ConfigurationProperties(prefix = "spring.datasource.hikari")
    HikariDataSource dataSource(DataSourceProperties properties) {
        HikariDataSource dataSource = properties
                .initializeDataSourceBuilder()
                .type(HikariDataSource.class)
                .build();
        return dataSource;
    }
}
```

**第4步：创建HikariDataSource Bean**

如果所有条件都满足，Spring Boot就会创建一个`HikariDataSource`的Bean放入容器。这个Bean的配置参数来自`application.yml`中`spring.datasource.*`下的配置项。

**整个过程用流程图总结**：

```
classpath有DataSource.class? ──YES──→ 加载DataSourceAutoConfiguration
                                        │
              容器中有用户定义的DataSource Bean? ──NO──→ 继续
                                        │
              classpath有HikariDataSource.class? ──YES──→ 创建HikariCP连接池
                                        │
              配置文件中指定了其他连接池类型? ──NO──→ HikariCP作为默认
                                        │
                        创建 HikariDataSource Bean ──→ 完成！
```

> 这就是"自动"的真正含义：**Spring Boot根据你引入了什么jar包、定义了哪些配置、创建了哪些Bean，自动决定要不要创建某个Bean以及如何创建**。

### 15.4.5 排除不需要的自动配置

有时你不需要某个自动配置——比如你的项目不需要数据库，但某个Starter间接引入了JDBC依赖，导致`DataSourceAutoConfiguration`尝试创建DataSource但因缺少数据库配置而启动失败。

**解决方案1：注解排除**

```java
@SpringBootApplication(exclude = {DataSourceAutoConfiguration.class})
public class Application {
    public static void main(String[] args) {
        SpringApplication.run(Application.class, args);
    }
}
```

**解决方案2：配置文件排除**

```yaml
spring:
  autoconfigure:
    exclude:
      - org.springframework.boot.autoconfigure.jdbc.DataSourceAutoConfiguration
      - org.springframework.boot.autoconfigure.orm.jpa.HibernateJpaAutoConfiguration
```

`spring.autoconfigure.exclude`是一个列表，可以排除任意多个自动配置类。

> 🚨 **坑点：项目中引用了JDBC依赖但没配置数据库连接信息 → 启动报错**
> 
> 这是因为`DataSourceAutoConfiguration`检测到classpath中有`DataSource.class`，尝试创建数据源时发现没有`spring.datasource.url`配置。此时要么配上数据库，要么排除`DataSourceAutoConfiguration`。

---

## 15.5 起步依赖（Starter）深度解析

### 15.5.1 一个Starter到底包含了什么？

以最常用的`spring-boot-starter-web`为例，在IDEA中展开它的依赖树：

```
spring-boot-starter-web (3.3.0)
├── spring-boot-starter (3.3.0)          ← 核心Starter
│   ├── spring-boot (3.3.0)             ← Spring Boot核心
│   ├── spring-boot-autoconfigure (3.3.0) ← 自动配置
│   ├── spring-boot-starter-logging     ← 日志（Logback）
│   │   ├── logback-classic
│   │   ├── log4j-to-slf4j              ← 桥接Log4j到SLF4J
│   │   └── jul-to-slf4j                ← 桥接JUL到SLF4J
│   ├── jakarta.annotation-api          ← Jakarta注解（@Resource等）
│   ├── spring-core / spring-context ...
│   └── snakeyaml                       ← YAML解析器
│
├── spring-boot-starter-json            ← JSON处理
│   ├── jackson-databind
│   ├── jackson-datatype-jdk8
│   ├── jackson-datatype-jsr310         ← Java 8时间API支持
│   └── jackson-module-parameter-names
│
├── spring-boot-starter-tomcat          ← 内嵌Tomcat
│   ├── tomcat-embed-core (10.1.20)     ← Tomcat 10（Jakarta EE 9+）
│   ├── tomcat-embed-el
│   └── tomcat-embed-websocket
│
└── spring-webmvc (6.1.8)              ← Spring MVC
    ├── spring-web
    ├── spring-webmvc
    └── spring-aop / spring-beans ...
```

**一个`spring-boot-starter-web`引入了约40个jar包**，但你只需要一行配置。所有jar包的版本都已由`spring-boot-dependencies`统一管理，保证了兼容性。

### 15.5.2 版本管理原理图解

```
你的项目 pom.xml
  └── parent: spring-boot-starter-parent (3.3.0)
        └── parent: spring-boot-dependencies (3.3.0)  ← 这是BOM
              └── <dependencyManagement>
                    spring-core: 6.1.8
                    spring-webmvc: 6.1.8
                    tomcat: 10.1.20
                    jackson: 2.17.0
                    hikaricp: 5.1.0
                    mysql-connector-j: 8.3.0
                    mybatis-spring-boot: 3.0.3
                    logback: 1.5.6
                    snakeyaml: 2.2
                    ...共几百个版本号
              </dependencyManagement>
```

`<dependencyManagement>`中的版本号不会直接引入依赖——它只是定义"如果谁引用了这个库，就用这个版本"。所以当你写`spring-boot-starter-web`（不写version）时，Maven会向上追溯：
1. 看自己的`<dependencyManagement>`中有无定义（一般没有）
2. 看父POM（`spring-boot-starter-parent`）的`<dependencyManagement>`（也没有）
3. 看祖父POM（`spring-boot-dependencies`）的`<dependencyManagement>`中：找到了！版本为3.3.0

> 🚨 **坑点：引入非Spring Boot管理的第三方库时版本冲突**

```xml
<!-- 假设你引入了ES客户端，它依赖的jackson版本与Spring Boot管理的不同 -->
<dependency>
    <groupId>co.elastic.clients</groupId>
    <artifactId>elasticsearch-java</artifactId>
    <version>8.12.0</version>  <!-- 它内部依赖jackson 2.16.0 -->
</dependency>
```

此时由于BOM中定义了jackson 2.17.0，Maven会优先使用BOM的版本。但如果ES客户端真的不兼容jackson 2.17.0怎么办？

**排查方法**：

```bash
# 查看完整依赖树
mvn dependency:tree

# 只看冲突的依赖（过滤出omitted for conflict）
mvn dependency:tree -Dverbose | grep "omitted for conflict"
```

**解决方法**：

```xml
<dependency>
    <groupId>co.elastic.clients</groupId>
    <artifactId>elasticsearch-java</artifactId>
    <version>8.12.0</version>
    <exclusions>
        <exclusion>
            <groupId>com.fasterxml.jackson.core</groupId>
            <artifactId>jackson-databind</artifactId>
        </exclusion>
    </exclusions>
</dependency>
<!-- 然后显式声明兼容版本 -->
<dependency>
    <groupId>com.fasterxml.jackson.core</groupId>
    <artifactId>jackson-databind</artifactId>
    <version>2.17.0</version>
</dependency>
```

### 15.5.3 常用Spring Boot官方Starter速查

| Starter | 功能 |
|---------|------|
| `spring-boot-starter-web` | Web开发（MVC + 内嵌Tomcat + Jackson） |
| `spring-boot-starter-webflux` | 响应式Web（WebFlux + Netty） |
| `spring-boot-starter-test` | 测试（JUnit 5 + Mockito + AssertJ） |
| `spring-boot-starter-data-jpa` | JPA + Hibernate |
| `spring-boot-starter-jdbc` | JDBC + HikariCP |
| `spring-boot-starter-data-redis` | Redis（Lettuce客户端） |
| `spring-boot-starter-security` | Spring Security |
| `spring-boot-starter-validation` | Bean Validation（Hibernate Validator） |
| `spring-boot-starter-actuator` | 应用监控（/actuator端点） |
| `spring-boot-starter-mail` | 邮件发送 |
| `spring-boot-starter-aop` | AOP（AspectJ） |
| `spring-boot-starter-cache` | 缓存抽象 |
| `spring-boot-starter-quartz` | 定时任务（Quartz调度器） |
| `spring-boot-starter-thymeleaf` | Thymeleaf模板引擎 |
| `spring-boot-starter-amqp` | RabbitMQ消息队列 |

---

## 15.6 自定义启动Banner（趣味实战）

在`src/main/resources/`下创建`banner.txt`：

```
${AnsiColor.RED}
  _____             _             ____              _
 / ____|           (_)           |  _ \            | |
| (___  _ __  _ __  _ _ __   __ _| |_) | ___   ___ | |_
 \___ \| '_ \| '_ \| | '_ \ / _` |  _ < / _ \ / _ \| __|
 ____) | |_) | |_) | | | | | (_| | |_) | (_) | (_) | |_
|_____/| .__/| .__/|_|_| |_|\__, |____/ \___/ \___/ \__|
       | |   | |             __/ |
       |_|   |_|            |___/
${AnsiColor.DEFAULT}
:: Spring Boot ${spring-boot.version} :: JDK ${java.version}
```

你也可以在`application.yml`中配置关闭Banner或使用图片Banner：

```yaml
spring:
  main:
    banner-mode: off     # off | console | log
```

---

## 本章小结

1. **Spring Boot的诞生原因**：传统Spring Framework有三大痛点——配置地狱（7-8个XML）、依赖版本冲突（手动管理几十个版本号）、启动繁琐（需要外部Tomcat部署）。Spring Boot用自动配置、起步依赖、内嵌服务器三大手段彻底解决了这些问题。

2. **"约定优于配置"**：Spring Boot预设了大量合理默认值（配置文件位置、扫描路径、静态资源路径等），开发者按约定行事即可零配置运行，需要定制时也能灵活覆盖。

3. **Spring Boot 3.x项目结构**：启动类必须放在根包下（否则`@ComponentScan`扫不到子包中的组件）；`pom.xml`通过`spring-boot-starter-parent`继承版本统一管理；`application.yml`是全局配置文件。

4. **@SpringBootApplication三合一**：`@SpringBootConfiguration`（≈@Configuration）+ `@EnableAutoConfiguration`（自动配置入口）+ `@ComponentScan`（组件扫描）。

5. **自动配置原理（源码级）**：`@EnableAutoConfiguration`中的`@Import(AutoConfigurationImportSelector.class)`读取`spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports`文件，获取所有自动配置类（约150个），然后通过`@Conditional`条件注解逐一判断是否生效。

6. **@Conditional条件注解家族**：`@ConditionalOnClass`（类存在）、`@ConditionalOnMissingBean`（Bean不存在）、`@ConditionalOnProperty`（配置项触发）等12种条件注解，实现了"按需配置"。

7. **起步依赖（Starter）**：一个Starter聚合了多个相关依赖，版本由`spring-boot-dependencies` BOM统一管理。排查冲突用`mvn dependency:tree`，排除冲突用`<exclusions>`。

> **下一章预告**：第16章将进入Spring Boot Web开发实战——统一返回格式Result类、@RestControllerAdvice全局异常处理、参数校验、CORS跨域、文件上传下载、拦截器。我们将把这些最佳实践整合成可复用的基础架构代码。

---

## 思考题

1. Spring Boot 3.x将自动配置类列表从`spring.factories`迁移到了`AutoConfiguration.imports`文件。请分析这个变化的好处是什么？有没有什么可能的弊端？

2. 如果你的Spring Boot项目启动时提示"Failed to configure a DataSource: 'url' attribute is not specified"，但你的项目根本不需要数据库，你应该怎么做？请给出两种解决方案。

3. 阅读以下启动类代码，指出问题并给出修复方案：
   ```java
   package com.example.config;
   
   @SpringBootApplication
   @ComponentScan("com.example.controller")
   public class App {
       public static void main(String[] args) {
           SpringApplication.run(App.class, args);
       }
   }
   ```

4. 在Spring Boot中，如果你想用自己的`DataSource`替换Spring Boot自动配置的HikariCP，你应该怎么做？（不需要多数据源，就是单纯替换实现）

5. `@ConditionalOnMissingBean`的"缺失"判断是发生在Bean定义的哪个阶段？如果两个`@Configuration`类中都有`@ConditionalOnMissingBean`标注的同类型Bean，谁先生效？（提示：思考`@Configuration`类的加载顺序和`@AutoConfiguration`的`before`/`after`属性）

6. 你现在打开了一个Spring Boot 3.x项目，`pom.xml`中有`spring-boot-starter-web`但没有写版本号。请追踪这个Starter的版本号到底是从哪里来的——从`pom.xml`开始，经过哪些中间步骤，最终在哪里被定义的？