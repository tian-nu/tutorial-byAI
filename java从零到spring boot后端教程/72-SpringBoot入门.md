# 72-SpringBoot入门

> 💡 你买了一台"智能咖啡机"。打开包装，插上电，按一个按钮——咖啡出来了。你不需要知道水泵的转速、加热管的温度曲线、磨豆机的研磨刻度。这就是Spring Boot：一台会自己配置自己的Java应用服务器。本章你要亲手启动它，并看懂它在"按按钮"的那几秒钟里到底干了什么。

---

## 本章目标
- 用 Spring Initializr 创建一个 Spring Boot 项目
- 读懂 `pom.xml` 的 Starter 机制
- 写出第一个 Hello World 控制器
- 理解 `SpringApplication.run()` 内部的启动流程
- 运行并验证第一个接口

---

## 72.1 准备工作

### 你需要安装

| 软件 | 最低版本 | 验证命令 |
|------|----------|----------|
| JDK | 17 | `java -version` |
| Maven | 3.8+ | `mvn -version` |
| IDE | IntelliJ IDEA Community 或 VS Code | — |

> ⚠️ 如果你还没有安装 JDK 17+ 和 Maven，请先完成第 05 章（终端与命令行）和第 15 章（Java 环境搭建）再回来。

---

## 72.2 创建项目——Spring Initializr

打开浏览器，访问 [https://start.spring.io](https://start.spring.io)，按以下配置填写：

```
Project：  Maven
Language： Java
Spring Boot： 3.2.x（选择最新的稳定版，不带 SNAPSHOT）
Group：    com.example
Artifact： demo
Name：     demo
Description： Demo project for Spring Boot
Package name： com.example.demo
Packaging： Jar
Java：     17
```

在右侧 **Dependencies** 区域，点击 **ADD DEPENDENCIES**，搜索并添加：

- **Spring Web**（提供 MVC 和嵌入式 Tomcat）
- **Lombok**（减少样板代码）
- **Spring Boot DevTools**（热重载）

点击 **GENERATE**，下载 `demo.zip`，解压到你想要的工作目录。

用 IDEA 打开：`File → Open → 选择 demo 文件夹（即包含 pom.xml 的那一级）`。

---

## 72.3 项目结构初览

```
demo/
├── pom.xml                     # Maven 项目描述文件
├── src/
│   ├── main/
│   │   ├── java/
│   │   │   └── com/example/demo/
│   │   │       └── DemoApplication.java   # 启动类
│   │   └── resources/
│   │       ├── application.properties     # 配置文件（空的）
│   │       ├── static/                    # 静态资源（HTML/JS/CSS）
│   │       └── templates/                 # 模板文件（Thymeleaf 等）
│   └── test/
│       └── java/
│           └── com/example/demo/
│               └── DemoApplicationTests.java
```

> 🤔 想多一点：你注意到 `application.properties` 是空的。在 Spring Framework 年代，光是启动一个 Web 项目就需要至少 50 行 XML 配置。Spring Boot 的"约定优于配置"意味着：只要你不偏离默认行为，就一行配置都不需要写。

---

## 72.4 解剖 pom.xml

打开 `pom.xml`，先看整体结构：

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0
         https://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <!-- 父 POM：Spring Boot 的版本管理中心 -->
    <parent>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-parent</artifactId>
        <version>3.2.5</version>
        <relativePath/>
    </parent>

    <!-- 项目坐标 -->
    <groupId>com.example</groupId>
    <artifactId>demo</artifactId>
    <version>0.0.1-SNAPSHOT</version>
    <name>demo</name>
    <description>Demo project for Spring Boot</description>

    <properties>
        <java.version>17</java.version>
    </properties>

    <dependencies>
        <!-- Starter：Web 开发全家桶 -->
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
        </dependency>

        <!-- Lombok -->
        <dependency>
            <groupId>org.projectlombok</groupId>
            <artifactId>lombok</artifactId>
            <optional>true</optional>
        </dependency>

        <!-- DevTools：热重载 -->
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-devtools</artifactId>
            <scope>runtime</scope>
            <optional>true</optional>
        </dependency>

        <!-- 测试 Starter -->
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-test</artifactId>
            <scope>test</scope>
        </dependency>
    </dependencies>

    <build>
        <plugins>
            <plugin>
                <groupId>org.springframework.boot</groupId>
                <artifactId>spring-boot-maven-plugin</artifactId>
            </plugin>
        </plugins>
    </build>
</project>
```

### 关键解读

**① parent POM ——版本管理中心**

`spring-boot-starter-parent` 是一个特殊的 POM，它不提供代码，但**统一管理了几百个第三方库的版本号**。因为有了它，你在 `<dependency>` 里不需要写 `<version>`——版本由 parent 决定，避免版本冲突。

**② Starter 机制 ——一站式套餐**

`spring-boot-starter-web` 不是一个 jar，而是一个**依赖集合**。你添加这一个 Starter，Maven 自动拉取：

| Starter 自动引入的常见库 | 作用 |
|--------------------------|------|
| spring-boot-starter | 核心 Starter（自动配置、日志） |
| spring-boot-starter-tomcat | 内嵌 Tomcat |
| spring-web | Spring MVC |
| spring-webmvc | Spring MVC 完整配置 |
| jackson-databind | JSON 序列化 |
| hibernate-validator | 参数校验 |

> 手写版：如果你不用 Starter，需要手工添加 20+ 个 `<dependency>` 且逐个协调版本号。

**③ spring-boot-maven-plugin**

这个插件让你能用 `mvn package` 打出**可执行 fat jar**——一个 jar 包含你的代码 + Tomcat + 所有依赖。`java -jar demo.jar` 一条命令启动整个应用。

---

## 72.5 Hello World——第一个控制器

在 `src/main/java/com/example/demo/` 下创建 `controller/HelloController.java`：

```java
package com.example.demo.controller;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api")
public class HelloController {

    @GetMapping("/hello")
    public String hello() {
        return "Hello, Spring Boot!";
    }

    @GetMapping("/hello/{name}")
    public String helloName(@PathVariable String name) {
        return "Hello, " + name + "!";
    }
}
```

逐行解释：

| 代码 | 含义 |
|------|------|
| `@RestController` | 告诉 Spring：这是一个 REST 控制器，所有方法返回值直接写入 HTTP 响应体 |
| `@RequestMapping("/api")` | 这个控制器下的所有接口路径都以 `/api` 开头 |
| `@GetMapping("/hello")` | 处理 GET 请求，路径为 `/api/hello` |
| `@PathVariable String name` | 从 URL 路径中提取 `{name}` 变量，赋给方法参数 |

---

## 72.6 启动应用

在 IDEA 中，找到 `DemoApplication.java`，点击 `main` 方法左侧的绿色三角 ▶，选择 "Run 'DemoApplication'"。

你会看到控制台输出：

```
  .   ____          _            __ _ _
 /\\ / ___'_ __ _ _(_)_ __  __ _ \ \ \ \
( ( )\___ | '_ | '_| | '_ \/ _` | \ \ \ \
 \\/  ___)| |_)| | | | | || (_| |  ) ) ) )
  '  |____| .__|_| |_|_| |_\__, | / / / /
 =========|_|==============|___/=/_/_/_/

 :: Spring Boot :: (v3.2.5)

2026-05-29T10:00:00.000+08:00  INFO 12345 --- [           main] com.example.demo.DemoApplication         : Starting DemoApplication using Java 17.0.10
2026-05-29T10:00:01.500+08:00  INFO 12345 --- [           main] o.s.b.w.embedded.tomcat.TomcatWebServer  : Tomcat initialized with port 8080 (http)
2026-05-29T10:00:02.000+08:00  INFO 12345 --- [           main] o.s.b.w.embedded.tomcat.TomcatWebServer  : Tomcat started on port 8080 (http)
2026-05-29T10:00:02.200+08:00  INFO 12345 --- [           main] com.example.demo.DemoApplication         : Started DemoApplication in 2.5 seconds
```

看到 `Started DemoApplication in 2.5 seconds`，说明启动成功。

### 验证接口

打开浏览器或终端：

```bash
curl http://localhost:8080/api/hello
# 输出：Hello, Spring Boot!

curl http://localhost:8080/api/hello/World
# 输出：Hello, World!
```

---

## 72.7 启动流程深度解析

`SpringApplication.run(DemoApplication.class, args)` 这一行代码背后发生了什么？本节配合可视化动画讲解。

> 📊 可视化演示见 [java_72_springboot_startup_visual.html](java_72_springboot_startup_visual.html)

启动流程分 **8 个阶段**：

```
阶段 1 ──► 创建 SpringApplication 实例
               ↓
阶段 2 ──► 推断应用类型（SERVLET / REACTIVE / NONE）
               ↓
阶段 3 ──► 加载 ApplicationContextInitializer
               ↓
阶段 4 ──► 加载 ApplicationListener
               ↓
阶段 5 ──► 推断主类（DemoApplication.class）
               ↓
阶段 6 ──► 准备 Environment（读取配置、Profile）
               ↓
阶段 7 ──► 创建并刷新 ApplicationContext
               ├── 扫描 Bean
               ├── 自动配置（AutoConfiguration）
               ├── 启动内嵌 Tomcat
               └── 注册 Controller 映射
               ↓
阶段 8 ──► 调用 ApplicationRunner / CommandLineRunner
               ↓
          应用就绪 ✓
```

### 各阶段详解

**阶段 1-2：创建 SpringApplication**

`new SpringApplication(DemoApplication.class)` 做的事情：
- 根据 classpath 推断应用类型：有 `DispatcherServlet` 就是 SERVLET 类型
- 设置 `ApplicationContextInitializer` 列表
- 设置 `ApplicationListener` 列表

**阶段 3-5：加载初始化器和监听器**

从 `META-INF/spring.factories` 文件中读取所有已注册的初始化器和监听器。这些是 Spring Boot 自动配置机制的核心组件。

**阶段 6：准备 Environment**

创建 `ConfigurableEnvironment`，加载 `application.properties` / `application.yml` 中的配置，确定激活的 Profile。

**阶段 7：刷新 ApplicationContext（最复杂）**

这是 Spring 最核心的启动步骤，内部又分为 12 个子步骤：

| 子步骤 | 说明 |
|--------|------|
| prepareRefresh | 准备上下文，设置启动时间、激活状态 |
| obtainFreshBeanFactory | 创建 BeanFactory |
| prepareBeanFactory | 配置 BeanFactory 的标准上下文 |
| postProcessBeanFactory | BeanFactory 后处理 |
| invokeBeanFactoryPostProcessors | **关键：执行自动配置** |
| registerBeanPostProcessors | 注册 Bean 后处理器（含 AOP 代理创建器） |
| initMessageSource | 国际化 |
| initApplicationEventMulticaster | 事件广播器 |
| onRefresh | **启动内嵌 Tomcat** |
| registerListeners | 注册监听器 |
| finishBeanFactoryInitialization | **实例化所有单例 Bean** |
| finishRefresh | 发布 ContextRefreshedEvent |

**阶段 8：调用 Runner**

如果 Spring 容器中存在 `ApplicationRunner` 或 `CommandLineRunner` Bean，按顺序调用它们的 `run` 方法。应用正式进入可用状态。

> 🤔 想多一点：`@SpringBootApplication` 是一个组合注解，等价于 `@SpringBootConfiguration` + `@EnableAutoConfiguration` + `@ComponentScan`。其中 `@EnableAutoConfiguration` 通过 `@Import(AutoConfigurationImportSelector.class)` 读取 `META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports` 文件，加载所有自动配置类。这就是为什么你什么都没配，Tomcat 自动启动、JSON 自动序列化——Spring Boot 替你做好了这些默认配置。

---

## 72.8 常见启动错误与解决

### 错误 1：端口被占用

```
Port 8080 was already in use.
```

**解决**：
```properties
# application.properties
server.port=8081
```

### 错误 2：找不到主类

```
Could not find or load main class com.example.demo.DemoApplication
```

**解决**：在 IDEA 中 `File → Invalidate Caches → Invalidate and Restart`，重新编译。

### 错误 3：@RestController 不生效

访问接口返回 404。

**排查步骤**：
1. 确认 Controller 在 `DemoApplication` 所在包或其子包下（默认扫描范围）
2. 确认类上有 `@RestController`
3. 确认方法上有 `@GetMapping` 等注解
4. 检查控制台日志，是否有 `Mapped "{[/api/hello]}"` 字样

### 错误 4：依赖下载慢

在 `pom.xml` 同级创建 `settings.xml` 的 mirror 配置，或在 IDEA 中设置 Maven 镜像为阿里云：

```xml
<mirror>
    <id>aliyun</id>
    <mirrorOf>central</mirrorOf>
    <name>Aliyun Maven</name>
    <url>https://maven.aliyun.com/repository/public</url>
</mirror>
```

---

## 72.9 小结

| 知识点 | 核心内容 |
|--------|----------|
| Spring Initializr | 在线生成项目骨架，选依赖自动写入 pom.xml |
| parent POM | 统一版本管理，无需手写 version |
| Starter | 一站式依赖包，一个 starter 引入一整组依赖 |
| @SpringBootApplication | 组合注解 = 配置 + 自动配置 + 组件扫描 |
| @RestController | REST 控制器，返回值直写响应体 |
| SpringApplication.run() | 8 阶段：创建 → 推断 → 初始化器 → 监听器 → 环境 → 刷新上下文 → Tomcat → Runner |
| 自动配置 | 从 `AutoConfiguration.imports` 加载数百个配置类，按条件自动生效 |

---

## 72.10 自测题

**1. 以下关于 `spring-boot-starter-web` 的描述，哪一项是正确的？**

A. 它是一个单独的 jar 包，提供 Web 功能  
B. 它是一个依赖集合，包含 Tomcat、Spring MVC、Jackson 等  
C. 添加它之后还需要单独添加 `spring-boot-starter-tomcat`  
D. 它只能用于 REST API，不能用于传统的 MVC 视图渲染  

**2. 你的 Controller 类放在 `com.example.controller` 包下，而启动类在 `com.example.demo` 包下。请问 Controller 能被 Spring 扫描到吗？如果不能，怎么解决？**

**3. `@SpringBootApplication` 包含哪三个核心注解？各自负责什么？**

---

**答案提示**：1→B。2→不能，因为 `@ComponentScan` 默认只扫描启动类所在包及其子包。解决方法：将 Controller 移到 `com.example.demo.controller`，或在启动类上显式指定 `@ComponentScan("com.example")`。3→`@SpringBootConfiguration`（配置类）+ `@EnableAutoConfiguration`（自动配置）+ `@ComponentScan`（组件扫描）。下一章——深入 IoC 容器，理解 Bean 的生命周期。