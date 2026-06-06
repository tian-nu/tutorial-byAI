# 第16章 · Java程序的基本结构

> "上一章我们写了5行代码打印出Hello World。但一个真正的Java项目绝对不止5行代码——它有成百上千个文件，分布在不同的文件夹里。这些文件是怎么组织的？class、package、import分别是什么？这一章帮你把Java程序的骨骼结构看清楚。"

---

## 16.1 package：把类分门别类装进"文件夹"

### 为什么需要package？

想象你有一个项目，里面写了100个类。如果全部堆在同一个文件夹里，找类和避免重名都会变成噩梦。

Java用**package**（包）来组织类，相当于操作系统的文件夹。比如：

```java
// 这个类在 com.example.model 包里
package com.example.model;

public class User {
    private String name;
    private int age;
}
```

类 `User` 的全名不是 `User`，而是 `com.example.model.User`。就像你家的地址不是"302室"，而是"中国XX省XX市XX小区302室"——package就是地址。

### package命名规范

业界通用约定：
- 全部小写字母
- 用公司域名的倒序开头：`com.google.search`、`org.apache.commons`
- 多层用 `.` 分隔：`com.example.controller.user`
- 不要用Java内置的包名：不要叫 `java.xxx`、`javax.xxx`

**本书练习项目的package**：
```
com.example.demo          → 根包
com.example.demo.model    → 放数据模型类（User、Product等）
com.example.demo.service  → 放业务逻辑类
com.example.demo.controller → 放控制器类
```

### 默认包（不推荐）

如果你不写 `package xxx;` 语句，类就属于"默认包"。这在练习代码时没问题，但在真正项目里**强烈不建议**——默认包里的类不能被其他包里的类导入。

---

## 16.2 import：借用别的包里的类

如果你要用另一个包里的类，必须先"导入"它：

```java
package com.example.demo.controller;

import com.example.demo.model.User;  // 导入User类
import java.util.List;               // 导入Java标准库的List接口
import java.util.*;                  // 导入java.util包里的所有类

public class UserController {
    public List<User> getAllUsers() {
        // ...
    }
}
```

### 三种导入方式

| 方式 | 写法 | 优缺点 |
|------|------|--------|
| 单个导入 | `import java.util.List;` | ✅ 清晰明确，知道用了哪些类。推荐 |
| 通配符导入 | `import java.util.*;` | ⚠️ 省事但不够清晰，可能引入不需要的类 |
| 静态导入 | `import static java.lang.Math.PI;` | 导入类的静态成员，之后直接写 `PI` 而不是 `Math.PI` |

### 不需要import的包

`java.lang` 包里的所有类**自动导入**，不需要写import。你常用的 `String`、`System`、`Math`、基本类型（`int`、`double` 等）都在 `java.lang` 里。

### 同名类冲突

如果两个包里有同名的类，你只能显式导入其中一个，另一个使用时必须写全名：

```java
import java.util.Date;  // 导入java.util的Date

public class Example {
    Date utilDate = new Date();              // 用java.util.Date
    java.sql.Date sqlDate = new java.sql.Date(1234L);  // 用全名区分
}
```

---

## 16.3 class：Java里的一切都是类

Java是**纯粹的面向对象语言**——你写的每一行代码都在某个类里面。不存在像Python那样可以随便写在文件顶部全局执行"的代码。

```java
package com.example.demo;

public class Person {
    // 1. 字段（Field）——也叫成员变量、属性
    private String name;
    private int age;

    // 2. 构造器（Constructor）——创建对象时调用
    public Person(String name, int age) {
        this.name = name;
        this.age = age;
    }

    // 3. 方法（Method）——类能做什么
    public void sayHello() {
        System.out.println("你好，我是" + name);
    }
}
```

### 一个.java文件能放几个类？

一个 `.java` 文件里可以有多个类，但**最多只能有一个 `public` 类**，并且这个public类的名字必须和文件名一致：

```java
// 文件：Example.java
public class Example {        // ✅ public类，名字=文件名
}

class Helper {                // ✅ 非public类，可以有
}

class AnotherHelper {         // ✅ 可以有多个非public类
}

// public class Something {}  // ❌ 编译错误！只能有一个public类
```

实际开发中，**一个文件一个类**是最好的习惯。

---

## 16.4 main方法：程序的唯一入口

上一章我们已经见过 `main` 方法，这里补充一些你可能不知道的细节。

### main方法的标准签名

```java
public static void main(String[] args)
```

任何Java程序都必须有一个这样的main方法，JVM才能启动。你可以改动 `args` 这个参数名（叫 `arguments` 也行），但其他部分**一个字都不能改**。

### 接收命令行参数

```java
public class ArgsDemo {
    public static void main(String[] args) {
        System.out.println("你传了 " + args.length + " 个参数：");
        for (int i = 0; i < args.length; i++) {
            System.out.println("args[" + i + "] = " + args[i]);
        }
    }
}
```

编译后运行：

```powershell
javac ArgsDemo.java
java ArgsDemo 张三 25 hello
```

输出：

```
你传了 3 个参数：
args[0] = 张三
args[1] = 25
args[2] = hello
```

**注意**：在命令行里用空格分隔参数。如果你想传一个含空格的参数（比如 `"张三 你好"`），用双引号包住。

### 可以有多个main方法吗？

**可以**。JVM启动时只调用你指定的那个类的main方法：

```java
public class A {
    public static void main(String[] args) {
        System.out.println("这是A的main");
    }
}

class B {
    public static void main(String[] args) {
        System.out.println("这是B的main");
    }
}
```

```powershell
java A   # 输出：这是A的main
java B   # 输出：这是B的main
```

---

## 16.5 javac、javap、jar：三个你迟早要用到的命令

### javac：编译器

你已经用过它了。补充几个常用选项：

```powershell
# 基本用法
javac HelloWorld.java

# 指定编译输出目录
javac -d ./bin HelloWorld.java

# 编译多个文件
javac *.java

# 指定编码（Windows下可能遇到中文乱码问题）
javac -encoding UTF-8 HelloWorld.java
```

> ❌ **常见错误**：带BOM（字节顺序标记）的UTF-8文件在Windows下用记事本保存时，可能会自动加上BOM头，导致javac报错"非法字符: '\ufeff'"。解决方法：用Notepad++或VS Code保存为"UTF-8 without BOM"，或者用IntelliJ IDEA（自动处理编码）。

### javap：反编译工具

`javap` 能让你窥探 `.class` 文件的内容。它不会给你看得懂的源代码，但能告诉你类里有哪些方法、哪些字段：

```powershell
# 查看类的基本信息
javap HelloWorld

# 查看详细信息（包括字节码指令）
javap -c HelloWorld

# 查看所有成员（包括私有的）
javap -p HelloWorld
```

示例输出（`javap HelloWorld`）：

```
Compiled from "HelloWorld.java"
public class HelloWorld {
  public HelloWorld();
  public static void main(java.lang.String[]);
}
```

你会看到多了一个 `HelloWorld()` 构造器——这是Java编译器自动加上的默认构造器（即使你没写）。这个我们第22章详细讲。

### jar：打包工具

当你的项目变成几十上百个 `.class` 文件时，把它们打包成一个文件更方便分发。这个包就是 **JAR文件**（Java ARchive），本质上就是个ZIP压缩包。

```powershell
# 创建jar包
jar cvf myapp.jar *.class

# 列出jar包内容
jar tf myapp.jar

# 解压jar包
jar xvf myapp.jar

# 运行jar包（需要指定main类）
java -cp myapp.jar HelloWorld
```

参数记忆：`c` = create（创建），`v` = verbose（显示详细信息），`f` = file（指定文件名），`t` = table（列出内容），`x` = extract（解压）。

---

## 16.6 一个标准Java项目的目录结构

看到这里，你对一个Java文件的"骨架"已经有了概念。现在看一下一个标准项目的完整目录结构：

```
my-project/
├── src/
│   ├── main/
│   │   ├── java/                          ← Java源码
│   │   │   └── com/
│   │   │       └── example/
│   │   │           └── demo/
│   │   │               ├── model/
│   │   │               │   └── User.java
│   │   │               ├── service/
│   │   │               │   └── UserService.java
│   │   │               └── DemoApplication.java   ← main方法在这里
│   │   └── resources/                     ← 配置文件
│   │       └── application.properties
│   └── test/
│       └── java/                          ← 测试代码
│           └── com/
│               └── example/
│                   └── demo/
│                       └── UserServiceTest.java
├── target/                                ← 编译产物（maven生成）
└── pom.xml                                ← Maven配置（第111章深入讲解）
```

**现阶段你不需要记住全部**，只需要记住两件事：
1. Java源码放在 `src/main/java/` 下
2. 包名 `com.example.demo` 对应的文件夹路径就是 `com/example/demo/`

---

## 本章小结

| 知识点 | 核心要点 |
|--------|----------|
| package | 组织类的命名空间。`package com.example.demo;` 放在文件第一行 |
| import | 导入其他包里的类。`java.lang.*` 自动导入。同名类冲突时用全名 |
| class | Java里一切代码都在类里。一个文件最多一个public类，类名=文件名 |
| main方法 | 程序入口：`public static void main(String[] args)`，签名一个字不能改 |
| javac | 编译器，`-d`指定输出目录，`-encoding UTF-8`指定编码 |
| javap | 反编译查看 `.class` 内容 |
| jar | 打包多个 `.class` 为一个文件 |

---

## 自测题

**1.** 以下哪个import语句是不必要的（因为相关类属于 `java.lang` 包，自动导入）？
- A. `import java.util.List;`
- B. `import java.lang.String;`
- C. `import java.io.File;`
- D. `import java.math.BigDecimal;`

**2.** 一个 `.java` 文件里，以下哪种情况会导致编译错误？
- A. 有一个public类 + 两个非public类
- B. 有两个public类
- C. 没有任何public类，只有一个非public类
- D. 一个public类，名称与文件名不同

**3.** main方法的参数 `String[] args` 中，`args[0]` 是什么？
- A. 编译时指定的参数
- B. 运行时命令行的第一个参数（程序名本身不算）
- C. 类名
- D. 文件路径

---

> 🚀 **下一章**：第17章 · 变量与常量——Java有8种基本数据类型，每个都有固定的范围和默认值。为什么3/2等于1而不是1.5？`var`关键字和`final`常量又是怎么回事？

---

[← 上一章：15-Java介绍与环境搭建](15-Java介绍与环境搭建/) | [下一章：17-变量与常量 →](17-变量与常量/)