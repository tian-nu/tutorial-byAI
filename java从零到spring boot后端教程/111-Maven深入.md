# 111-Maven深入

> 💡 你已经用 Maven 创建过 Spring Boot 项目，`mvn spring-boot:run` 跑得很熟。但如果有人问你：`mvn clean package` 到底干了什么？为什么有时候要 `mvn clean install -DskipTests`？`pom.xml` 里的 `<dependencyManagement>` 和 `<dependencies>` 有什么区别？本章把这些"会用但说不清"的点一一拆开，让你真正理解 Maven 的构建生命周期、依赖管理和多模块项目。

---

## 本章目标
- 理解 Maven 的生命周期与插件机制
- 掌握依赖管理（scope、传递性、冲突解决）
- 创建多模块 Maven 项目
- 使用 Profile 区分环境
- 理解 `mvn install` 和 `mvn package` 的区别

---

## 111.1 Maven 生命周期

Maven 有三个内置生命周期：**default**（构建核心）、**clean**（清理）、**site**（文档站点）。你每天打交道的是 default。

### default 生命周期关键阶段（按顺序）

```
validate   → 验证项目结构
compile    → 编译 Java 源码（src/main/java → target/classes）
test       → 运行单元测试（src/test/java）
package    → 打包（jar / war）
verify     → 集成测试验证
install    → 安装到本地仓库（~/.m2/repository）
deploy     → 部署到远程仓库（如 Maven Central 或公司私服）
```

### 核心规则

**执行后面的阶段，前面的会自动执行。**

```bash
mvn compile    # 只到 compile
mvn package    # validate → compile → test → package
mvn install    # validate → compile → test → package → install
```

### 常用命令

```bash
mvn clean                          # 删除 target/ 目录
mvn clean package                  # 清理 + 打包
mvn clean package -DskipTests      # 跳过测试打包
mvn clean install                  # 安装到本地仓库
mvn test                           # 只运行测试
mvn dependency:tree                # 查看依赖树
```

---

## 111.2 插件——Maven 的灵魂

Maven 的功能都由**插件**提供。`mvn compile` 实际上是在调用 `maven-compiler-plugin`。`mvn package` 是调用打包插件（jar 用 `maven-jar-plugin`，Spring Boot 用 `spring-boot-maven-plugin`）。

### 在 pom.xml 中配置插件

```xml
<build>
    <plugins>
        <plugin>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-maven-plugin</artifactId>
            <version>3.2.5</version>
            <executions>
                <execution>
                    <goals>
                        <goal>repackage</goal>
                    </goals>
                </execution>
            </executions>
        </plugin>
    </plugins>
</build>
```

`spring-boot-maven-plugin` 的 `repackage` goal 把普通 jar 重打包为可执行 fat jar（内嵌 Tomcat + 所有依赖）。

### 验证方法

```bash
mvn clean package
ls -lh target/
# 应看到 your-app-0.0.1-SNAPSHOT.jar（可执行 fat jar）
```

---

## 111.3 依赖管理深入

### scope——控制依赖在什么阶段可用

| scope | 编译时 | 测试时 | 运行时 | 打包到最终 jar | 典型场景 |
|-------|--------|--------|--------|---------------|----------|
| `compile`（默认） | ✅ | ✅ | ✅ | ✅ | Spring Boot Starter |
| `provided` | ✅ | ✅ | ❌ | ❌ | Servlet API、Lombok |
| `runtime` | ❌ | ✅ | ✅ | ✅ | JDBC 驱动 |
| `test` | ❌ | ✅ | ❌ | ❌ | JUnit、Mockito |

```xml
<dependency>
    <groupId>org.projectlombok</groupId>
    <artifactId>lombok</artifactId>
    <scope>provided</scope>
</dependency>
```

> 💡 Lombok 用 `provided`：编译时需要它生成代码，但运行时不需要（字节码已经生成了 getter/setter）。

### 依赖传递性

```
你的项目 → spring-boot-starter-web → spring-boot-starter-tomcat
                                              → jackson-databind
```

你只需要声明 `spring-boot-starter-web`，它的依赖会自动传递进来。

### 排除你不想要的传递依赖

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-web</artifactId>
    <exclusions>
        <exclusion>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-tomcat</artifactId>
        </exclusion>
    </exclusions>
</dependency>
<!-- 然后用 Undertow 代替 Tomcat -->
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-undertow</artifactId>
</dependency>
```

### 依赖冲突与仲裁规则

当两个依赖引入同一个库的不同版本时，Maven 采用**最短路径优先**：

```
A → X:1.0
A → B → X:2.0     （X:1.0 胜出，路径更短）
```

如果路径相同，**先声明的优先**。

### 查看依赖冲突

```bash
mvn dependency:tree -Dincludes=com.fasterxml.jackson.core
```

---

## 111.4 dependencyManagement——统一版本控制

在多模块项目中，`dependencyManagement` 放在父 POM 中，只声明版本号，不实际引入依赖。

```xml
<!-- 父 POM -->
<dependencyManagement>
    <dependencies>
        <dependency>
            <groupId>com.google.guava</groupId>
            <artifactId>guava</artifactId>
            <version>33.0.0-jre</version>
        </dependency>
    </dependencies>
</dependencyManagement>
```

子模块引用时不需要写版本：

```xml
<!-- 子模块 POM -->
<dependencies>
    <dependency>
        <groupId>com.google.guava</groupId>
        <artifactId>guava</artifactId>
        <!-- 版本由父 POM 统一管理，这里不用写 -->
    </dependency>
</dependencies>
```

### 与 `<dependencies>` 的区别

| 标签 | 作用 |
|------|------|
| `<dependencies>` | 实际引入依赖 |
| `<dependencyManagement>` | 只声明版本，不引入 |

父 POM 的 `<dependencies>` 中的依赖会**自动传递**给所有子模块。父 POM 的 `<dependencyManagement>` 则不会自动引入，需要子模块显式声明才生效。

---

## 111.5 多模块项目

### 项目结构

```
my-platform/                     # 父模块（pom）
├── pom.xml                      # <packaging>pom</packaging>
├── common/                      # 公共模块（jar）
│   └── pom.xml
├── user-service/                # 用户服务（jar）
│   └── pom.xml
└── order-service/               # 订单服务（jar）
    └── pom.xml
```

### 父 POM（my-platform/pom.xml）

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0
         http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <parent>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-parent</artifactId>
        <version>3.2.5</version>
    </parent>

    <groupId>com.example</groupId>
    <artifactId>my-platform</artifactId>
    <version>1.0.0</version>
    <packaging>pom</packaging>

    <modules>
        <module>common</module>
        <module>user-service</module>
        <module>order-service</module>
    </modules>

    <properties>
        <java.version>17</java.version>
    </properties>
</project>
```

### 子模块 POM（user-service/pom.xml）

```xml
<project>
    <parent>
        <groupId>com.example</groupId>
        <artifactId>my-platform</artifactId>
        <version>1.0.0</version>
    </parent>

    <artifactId>user-service</artifactId>

    <dependencies>
        <dependency>
            <groupId>com.example</groupId>
            <artifactId>common</artifactId>
            <version>${project.version}</version>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
        </dependency>
    </dependencies>
</project>
```

### 构建

```bash
cd my-platform
mvn clean install     # 从父模块构建，所有子模块按依赖顺序编译
```

### 验证方法

```bash
mvn clean install
echo $?               # 应输出 0
ls user-service/target/
# 应看到 user-service-1.0.0.jar
```

---

## 111.6 Profile——环境切换

```xml
<profiles>
    <profile>
        <id>dev</id>
        <properties>
            <env>dev</env>
        </properties>
        <activation>
            <activeByDefault>true</activeByDefault>
        </activation>
    </profile>
    <profile>
        <id>prod</id>
        <properties>
            <env>prod</env>
        </properties>
    </profile>
</profiles>
```

使用：

```bash
mvn clean package -Pprod     # 使用 prod profile
mvn clean package             # 使用默认 dev profile
```

---

## 111.7 完成效果

学完本章，你应该能：
1. 解释 `mvn clean package` 到底执行了哪些阶段
2. 正确使用 dependency scope 和排除传递依赖
3. 搭建多模块 Maven 项目
4. 用 Profile 切换开发/生产环境

---

## 小结

| 知识点 | 核心内容 |
|--------|----------|
| 生命周期阶段 | validate → compile → test → package → install → deploy |
| 常用命令 | `mvn clean package`, `mvn clean install -DskipTests` |
| 依赖 scope | compile / provided / runtime / test |
| 依赖排除 | `<exclusions><exclusion>...` |
| 版本统一 | 父 POM 的 `<dependencyManagement>` |
| 多模块 | 父 POM `<packaging>pom</packaging>` + `<modules>` |
| 环境切换 | `<profiles>` + `mvn ... -Pxxx` |

---

## 自测题

1. `mvn package` 和 `mvn install` 有什么区别？
2. 你在 `pom.xml` 中引入了 `guava:33.0.0`，但它传递引入了 `guava:30.0`（来自另一个依赖），最终项目用的是哪个版本？为什么？
3. 你想在多模块项目中，让所有子模块统一使用 `jackson 2.17.0`。应该把版本声明放在哪个标签里？

<details>
<summary>点击查看答案</summary>

1. `mvn package` 只打包到 target/ 目录；`mvn install` 在 package 之后还会把 jar 安装到本地 Maven 仓库（~/.m2/repository），让其他本地项目可以引用它。
2. 33.0.0。因为你直接声明的依赖路径更短（1层），传递依赖（2层）在仲裁中优先级更低。
3. 放在父 POM 的 `<dependencyManagement>` 中。这样所有子模块声明 jackson 依赖时都不用写版本号，统一由父 POM 控制。
</details>