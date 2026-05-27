# 第13章：MyBatis — SQL掌控者

## 本章目标

学完本章你将能够：

- 理解MyBatis如何解决JDBC的四大痛点，认清从JDBC手工劳动到MyBatis自动化的演进过程
- 独立配置mybatis-spring-boot-starter，完成XML方式和注解方式的完整CRUD
- 深刻理解`#{}`（预编译占位符）与`${}`（字符串拼接）的本质区别，**亲手复现SQL注入攻击并学会防御**
- 掌握resultMap自定义映射，实现一对一（association）和一对多（collection）关联查询
- 熟练运用动态SQL六大标签（`<if>`、`<where>`、`<set>`、`<foreach>`、`<trim>`、`<choose>`）应对复杂业务查询
- 配置PageHelper分页插件实现物理分页
- 为第14章（JPA）建立对比基线：什么场景选MyBatis，什么场景选JPA

---

## 13.1 JDBC痛点回顾：我们为什么要学MyBatis？

在第9章，我们用大约500行Java代码实现了EMS v2的员工CRUD系统。一个"查询所有员工"功能需要几步？打开你的EmployeeDaoImpl.java数一数——**至少10行**（获取连接→预编译SQL→设置参数→执行查询→遍历ResultSet→逐列getXxx→手动塞入Employee对象→关闭ResultSet→关闭PreparedStatement→归还连接）。

而用MyBatis，同样的功能只需要：

```java
// Mapper接口
@Mapper
public interface EmployeeMapper {
    List<Employee> findAll();
}
```

```xml
<!-- Mapper XML -->
<select id="findAll" resultType="com.example.entity.Employee">
    SELECT id, name, age, department, salary, email, hire_date
    FROM employee ORDER BY id
</select>
```

**4行Java + 4行XML = 8行。** 这并非魔法，而是MyBatis帮你自动化了JDBC的每一个繁琐步骤。让我们先把JDBC的痛点拆开来看，再逐一对照MyBatis的解决方案：

### JDBC vs MyBatis 对比表

| 痛点 | JDBC原始写法 | 你的工作量 | MyBatis自动化方案 |
|------|------------|-----------|------------------|
| **硬编码SQL** | SQL字符串写在Java代码里，拼接参数用`+`号 | 改SQL要重新编译Java、SQL分散在各处难以维护 | SQL统一放在XML映射文件中，与Java代码完全分离 |
| **手动设参** | `pstmt.setString(1, name)` 逐参数手动设置，参数多了极易错位 | 每个参数都要写一行，参数顺序必须和SQL中`?`一致 | `#{}`占位符自动绑定，参数名直接对应，MyBatis反射调用getter |
| **手动封装结果** | `rs.getString("name")` 逐列读取然后拼Employee对象 | 每增加一个字段就要修改`buildEmployee()`方法 | `resultType`自动映射同名属性，`resultMap`自定义复杂映射，支持嵌套对象 |
| **资源管理** | try-with-resources管理Connection/PreparedStatement/ResultSet | 每次操作都要写三层嵌套的try | MyBatis的SqlSession内部管理连接，自动关闭资源 |

让我们用一段JDBC代码来直观感受这种对比：

### JDBC版（需要手动完成一切）

```java
public Employee findById(Long id) throws SQLException {
    String sql = "SELECT id, name, age, department, salary, email, hire_date FROM employee WHERE id = ?";
    try (Connection conn = dataSource.getConnection();
         PreparedStatement pstmt = conn.prepareStatement(sql)) {
        pstmt.setLong(1, id);                          // 手动设参
        try (ResultSet rs = pstmt.executeQuery()) {
            if (rs.next()) {
                Employee emp = new Employee();          // 手动创建对象
                emp.setId(rs.getLong("id"));           // 手动逐列读取
                emp.setName(rs.getString("name"));      // 手动逐列赋值
                emp.setAge(rs.getInt("age"));
                emp.setDepartment(rs.getString("department"));
                emp.setSalary(rs.getDouble("salary"));
                emp.setEmail(rs.getString("email"));
                emp.setHireDate(rs.getString("hire_date"));
                return emp;
            }
        }
    }
    return null;
}
```

### MyBatis版（声明式SQL + 自动映射）

```xml
<select id="findById" resultType="com.example.entity.Employee">
    SELECT id, name, age, department, salary, email, hire_date
    FROM employee WHERE id = #{id}
</select>
```

MyBatis的核心哲学可以概括为：**SQL由你掌控，体力活交给我。** 这也是它和JPA最根本的区别——我们将在第14章深入对比。

---

## 13.2 MyBatis快速上手

### 13.2.1 核心架构

在动手编码之前，先快速理解MyBatis的骨架。三个核心组件：

```
┌──────────────────────────────────────────────┐
│           你的Java代码                         │
│   EmployeeMapper mapper = sqlSession          │
│       .getMapper(EmployeeMapper.class);       │
│   List<Employee> list = mapper.findAll();     │
├──────────────────────────────────────────────┤
│  SqlSession（MyBatis顶层API）                  │
│  - 获取Mapper代理对象                          │
│  - 管理数据库操作                              │
│  - 内部封装Connection/PreparedStatement等       │
├──────────────────────────────────────────────┤
│  SqlSessionFactory（工厂，全局唯一）            │
│  - 读取mybatis-config.xml / Spring Boot自动配置 │
│  - 创建SqlSession                             │
│  - 管理所有Mapper接口与XML映射的对应关系         │
└──────────────────────────────────────────────┘
```

在Spring Boot环境下，SqlSessionFactory和SqlSession都由`mybatis-spring-boot-starter`自动配置，你只需要定义Mapper接口和XML映射文件即可。

### 13.2.2 项目初始化

**第一步：添加Maven依赖**

```xml
<!-- pom.xml -->
<parent>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-parent</artifactId>
    <version>3.2.0</version>
</parent>

<dependencies>
    <!-- Spring Boot Web -->
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-web</artifactId>
    </dependency>

    <!-- MyBatis Spring Boot Starter -->
    <dependency>
        <groupId>org.mybatis.spring.boot</groupId>
        <artifactId>mybatis-spring-boot-starter</artifactId>
        <version>3.0.3</version>
    </dependency>

    <!-- MySQL驱动 -->
    <dependency>
        <groupId>com.mysql</groupId>
        <artifactId>mysql-connector-j</artifactId>
        <scope>runtime</scope>
    </dependency>

    <!-- Lombok -->
    <dependency>
        <groupId>org.projectlombok</groupId>
        <artifactId>lombok</artifactId>
        <optional>true</optional>
    </dependency>
</dependencies>
```

**第二步：application.yml配置**

```yaml
spring:
  datasource:
    url: jdbc:mysql://localhost:3306/ems?useSSL=false&serverTimezone=Asia/Shanghai&characterEncoding=utf8mb4
    username: root
    password: 你的密码
    driver-class-name: com.mysql.cj.jdbc.Driver

mybatis:
  mapper-locations: classpath:mapper/*.xml        # XML映射文件位置
  type-aliases-package: com.example.entity         # 实体类别名（XML中不用写全限定名）
  configuration:
    map-underscore-to-camel-case: true              # 下划线自动转驼峰
    log-impl: org.apache.ibatis.logging.stdout.StdOutImpl  # SQL日志输出到控制台
```

> 💡 **配置解读**：
> - `mapper-locations`：告诉MyBatis去哪里找XML映射文件。`classpath:mapper/*.xml` 表示扫描`resources/mapper/`目录下的所有`.xml`文件。
> - `type-aliases-package`：设置为实体类所在的包后，XML的`resultType`可以直接写`Employee`而不是`com.example.entity.Employee`。
> - `map-underscore-to-camel-case: true`：**强烈建议开启！** 数据库字段`hire_date`会自动映射到Java属性`hireDate`，省去大量手动映射工作。
> - `log-impl`：开发期开启，可以在控制台看到MyBatis实际执行的SQL和参数值，调试利器。

**第三步：实体类**

```java
package com.example.entity;

import lombok.Data;
import java.time.LocalDate;

@Data
public class Employee {
    private Long id;
    private String name;
    private Integer age;
    private String department;
    private Double salary;
    private String email;
    private LocalDate hireDate;
}
```

> 注意：`hireDate`使用`LocalDate`（Java 8+推荐），MyBatis会自动处理`DATE`类型与`LocalDate`之间的转换，无需额外配置。

**第四步：Mapper接口**

```java
package com.example.mapper;

import com.example.entity.Employee;
import org.apache.ibatis.annotations.Mapper;
import java.util.List;

@Mapper
public interface EmployeeMapper {

    List<Employee> findAll();

    Employee findById(Long id);

    int insert(Employee employee);

    int update(Employee employee);

    int deleteById(Long id);
}
```

> 🚨 **坑点：`@Mapper`注解不能忘！**
> - `@Mapper`告诉Spring这个接口是一个MyBatis的Mapper，Spring会为它创建**动态代理对象**
> - 如果忘记加`@Mapper`，注入时Spring找不到Bean → `NoSuchBeanDefinitionException`
> - 另外，如果你的Mapper数量很多，可以在启动类上统一使用`@MapperScan("com.example.mapper")`替代逐个加`@Mapper`

**第五步：XML映射文件**

在`src/main/resources/mapper/`目录下创建`EmployeeMapper.xml`：

```xml
<?xml version="1.0" encoding="UTF-8" ?>
<!DOCTYPE mapper PUBLIC "-//mybatis.org//DTD Mapper 3.0//EN"
        "http://mybatis.org/dtd/mybatis-3-mapper.dtd">

<!-- namespace必须和Mapper接口的全限定名一致 -->
<mapper namespace="com.example.mapper.EmployeeMapper">

    <!-- 查询所有员工 -->
    <select id="findAll" resultType="com.example.entity.Employee">
        SELECT id, name, age, department, salary, email, hire_date
        FROM employee ORDER BY id
    </select>

    <!-- 按ID查询 -->
    <select id="findById" resultType="com.example.entity.Employee">
        SELECT id, name, age, department, salary, email, hire_date
        FROM employee WHERE id = #{id}
    </select>

    <!-- 新增员工（返回受影响行数） -->
    <insert id="insert" parameterType="com.example.entity.Employee">
        INSERT INTO employee (name, age, department, salary, email, hire_date)
        VALUES (#{name}, #{age}, #{department}, #{salary}, #{email}, #{hireDate})
    </insert>

    <!-- 更新员工 -->
    <update id="update" parameterType="com.example.entity.Employee">
        UPDATE employee
        SET name = #{name},
            age = #{age},
            department = #{department},
            salary = #{salary},
            email = #{email}
        WHERE id = #{id}
    </update>

    <!-- 删除员工 -->
    <delete id="deleteById">
        DELETE FROM employee WHERE id = #{id}
    </delete>

</mapper>
```

> 🚨 **坑点：namespace必须和Mapper接口全限定名一致！**
> - `namespace="com.example.mapper.EmployeeMapper"` 必须和接口的包名+类名完全一致
> - 如果写错（比如写成了`com.example.dao.EmployeeMapper`），启动时不会报错，但调用方法时会抛出 **BindingException：Invalid bound statement (not found)**
> - 排查方法：检查namespace拼写、检查XML文件路径是否在`mapper-locations`范围内

> 🚨 **坑点：mapper.xml在resources下的目录结构必须和java下的Mapper接口目录结构一致！**
> - 如果你的Mapper接口在`src/main/java/com/example/mapper/EmployeeMapper.java`
> - 则XML文件应放在`src/main/resources/mapper/EmployeeMapper.xml`（而不是`src/main/resources/com/example/mapper/EmployeeMapper.xml`）
> - 因为`mapper-locations: classpath:mapper/*.xml` 只扫描`resources/mapper/`目录
> - 如果使用`@MapperScan`且没配置`mapper-locations`，则XML文件名必须和接口名一致且放在同类路径下

**第六步：@MapperScan配置**

当Mapper数量较多时，与其在每个接口上加`@Mapper`，不如在启动类统一扫描：

```java
package com.example;

import org.mybatis.spring.annotation.MapperScan;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
@MapperScan("com.example.mapper")  // 统一扫描mapper包
public class Application {
    public static void main(String[] args) {
        SpringApplication.run(Application.class, args);
    }
}
```

**第七步：Service层调用**

```java
package com.example.service;

import com.example.entity.Employee;
import com.example.mapper.EmployeeMapper;
import org.springframework.stereotype.Service;
import java.util.List;

@Service
public class EmployeeService {

    private final EmployeeMapper employeeMapper;

    // 构造器注入（推荐）
    public EmployeeService(EmployeeMapper employeeMapper) {
        this.employeeMapper = employeeMapper;
    }

    public List<Employee> listAll() {
        return employeeMapper.findAll();
    }

    public Employee getById(Long id) {
        return employeeMapper.findById(id);
    }

    public void add(Employee employee) {
        employeeMapper.insert(employee);
    }

    public void modify(Employee employee) {
        employeeMapper.update(employee);
    }

    public void remove(Long id) {
        employeeMapper.deleteById(id);
    }
}
```

至此，一个完整的MyBatis CRUD项目就建好了。对比JDBC版本（第9章~500行），MyBatis版本（接口+XML+Service）不到100行Java代码就实现了同样功能。

### 13.2.3 XML映射文件结构详解

每个XML映射文件遵循固定的DTD结构，以下是最常用的四个标签：

| 标签 | 用途 | 注意 |
|------|------|------|
| `<select>` | 查询 | 必须指定`resultType`或`resultMap`（返回类型） |
| `<insert>` | 插入 | 支持`useGeneratedKeys="true"`获取自增主键 |
| `<update>` | 更新 | 返回受影响行数（int） |
| `<delete>` | 删除 | 返回受影响行数（int） |

每个标签的`id`属性对应Mapper接口中的方法名，MyBatis就是通过 **namespace + id** 来定位SQL语句的。

**获取自增主键**：

```xml
<insert id="insert" parameterType="Employee"
        useGeneratedKeys="true" keyProperty="id">
    INSERT INTO employee (name, age, department, salary, email, hire_date)
    VALUES (#{name}, #{age}, #{department}, #{salary}, #{email}, #{hireDate})
</insert>
```

`useGeneratedKeys="true"` 告诉MyBatis使用JDBC的`getGeneratedKeys()`方法获取数据库自动生成的主键值，`keyProperty="id"` 指定将自增值回填到`Employee`对象的`id`属性中。执行完`insert`后，`employee.getId()`就是数据库生成的实际ID。

---

## 13.3 #{} vs ${} — 安全红线

这是本章**最重要的小节**，也是MyBatis学习中安全意识的分水岭。这两个符号在XML中看起来很像，但底层实现天差地别。

### 13.3.1 #{} 原理：预编译占位符

`#{}` 对应JDBC的 `PreparedStatement` 占位符 `?`，执行过程分为两步：

1. **预编译阶段**：MyBatis将`#{}`替换为`?`，将SQL模板发送给数据库编译。数据库解析SQL语法结构，生成执行计划并缓存。
2. **参数注入阶段**：参数值单独发送给数据库，数据库将参数值当作**纯数据**填入已编译好的SQL模板中。

实际执行的SQL（假设参数为`id=5`）：

```sql
-- 发给数据库的模板
SELECT * FROM employee WHERE id = ?
-- 参数值（单独发送）：5
-- 数据库实际执行
SELECT * FROM employee WHERE id = 5
```

关键是：**参数值中的特殊字符会被转义**。即使用户输入了`5 OR 1=1`，数据库也只会去查`id`等于字符串`"5 OR 1=1"`的记录，不会改变SQL语义。

### 13.3.2 ${} 原理：字符串拼接

`${}` 直接做**字符串替换**，相当于JDBC的`Statement`拼接SQL。MyBatis在**构建SQL字符串阶段**就将`${}`的内容原封不动地拼入SQL，然后整个拼好的SQL字符串再发送给数据库。

实际执行的SQL（假设参数为`id=5`）：

```sql
SELECT * FROM employee WHERE id = 5
```

和`#{}`的区别在哪里？**没有预编译过程，参数值在SQL字符串层面就参与进去了。** 如果参数值中包含SQL关键字或特殊字符，就会改变SQL的原有语义。

### 13.3.3 SQL注入攻击在MyBatis中的重现

> ⚠️ **警告：以下代码仅用于教学演示SQL注入原理，绝对不要在生产环境使用！**

假设你写了这样的Mapper：

```xml
<!-- 危险写法！ -->
<select id="login" resultType="Employee">
    SELECT * FROM employee
    WHERE name='${name}' AND password='${password}'
</select>
```

攻击者在登录框输入：
- 用户名：`admin`
- 密码：`' OR '1'='1`

拼接后的SQL变成：

```sql
SELECT * FROM employee WHERE name='admin' AND password='' OR '1'='1'
```

让我们分析这条SQL的逻辑：
- `password=''` → 密码是空串，正常情况下不会匹配
- **但** `OR '1'='1'` → `'1'='1'` 永远为TRUE
- 整个WHERE条件变成了 `(name='admin' AND password='') OR TRUE` = **TRUE**
- 结果：查出了`name='admin'`的用户，**绕过密码验证成功登录**！

这就是经典的"万能密码"注入攻击。如果我们用`#{}`替代`${}`：

```xml
<!-- 安全写法！ -->
<select id="login" resultType="Employee">
    SELECT * FROM employee
    WHERE name=#{name} AND password=#{password}
</select>
```

同样输入密码`' OR '1'='1`，实际执行的SQL等价于：

```sql
SELECT * FROM employee WHERE name='admin' AND password='\' OR \'1\'=\'1'
```

数据库把整个`' OR '1'='1`（包括单引号）当作password字段的**纯字符串值**进行精确匹配。除非数据库里真有一条记录的password列值为`' OR '1'='1`，否则查不到结果。SQL注入被彻底防住了。

### 13.3.4 什么时候必须用${}？

尽管`${}`危险，但它确实有一些`#{}`无法替代的场景：

| 场景 | 为什么不能用#{} | 正确做法 |
|------|----------------|---------|
| **动态表名** | `FROM ?` 是非法SQL（占位符只能替值） | `${}`拼接 + 白名单校验 |
| **动态列名** | `ORDER BY ?` 不会报错但**不会按指定列排序**（会被当做字符串常量） | `${}`拼接 + 白名单校验 |
| **动态排序方向** | `ORDER BY id ?` 参数值`DESC`被当字符串常量 | `${}`拼接 + 白名单校验 |
| **LIKE模糊查询** | `'%${keyword}%'`（可以用`CONCAT('%', #{keyword}, '%')`替代） | 优先用`CONCAT`函数 |

**白名单校验示例**：

```java
// 允许排序的列名白名单
private static final Set<String> ALLOWED_COLUMNS = Set.of("id", "name", "age", "salary", "hire_date");
// 允许的排序方向
private static final Set<String> ALLOWED_DIRECTIONS = Set.of("ASC", "DESC");

public List<Employee> findByOrder(String orderBy, String direction) {
    if (orderBy == null || !ALLOWED_COLUMNS.contains(orderBy)) {
        throw new IllegalArgumentException("不允许的排序列: " + orderBy);
    }
    if (direction == null || !ALLOWED_DIRECTIONS.contains(direction.toUpperCase())) {
        throw new IllegalArgumentException("不允许的排序方向: " + direction);
    }
    return mapper.findByOrder(orderBy, direction.toUpperCase());
}
```

> 🚨 **坑点：`ORDER BY #{column}` 不会报错但不会按你期望的方式排序！**
> - 假设写 `ORDER BY #{column}`，传入参数值`"salary"`
> - 实际SQL变成 `ORDER BY 'salary'`（注意：salary被当作字符串常量了）
> - 数据库会将其理解为"按常量字符串salary排序"——因为每一行的这个"常量"都是相同的，所以**结果不排序**
> - 正确写法：`ORDER BY ${column}`，但必须配合白名单！

### 13.3.5 控制台日志对比

开启`log-impl: org.apache.ibatis.logging.stdout.StdOutImpl`后，可以看到实际执行的SQL。这是两种方式的直观对比：

**#{}方式日志**（参数以`?`预编译，参数值单独显示）：

```
==>  Preparing: SELECT * FROM employee WHERE name=? AND password=?
==> Parameters: admin(String), ' OR '1'='1(String)
```

**${}方式日志**（参数直接拼入SQL）：

```
==>  Preparing: SELECT * FROM employee WHERE name='admin' AND password='' OR '1'='1'
==> Parameters:
```

看到区别了吗？`#{}`方式中，SQL模板和参数是分离的；`${}`方式中，参数已经"融"入了SQL语句本身。这就是安全性鸿沟的根本原因。

---

## 13.4 resultMap与结果映射

### 13.4.1 自动映射原理

MyBatis默认开启了`autoMappingBehavior`，当`resultType`指定了类型后，MyBatis会按以下规则自动映射：

1. SQL查询结果的**列名** → Java对象的**属性名**
2. 不区分大小写（`ID`和`id`都能映射到`id`属性）
3. 开启`map-underscore-to-camel-case: true`后，自动将下划线转为驼峰：`hire_date` → `hireDate`

> 🚨 **坑点：不开启驼峰转换 → 字段映射不到！**
> - 数据库中列名为`department_name`，Java属性名为`departmentName`
> - 如果没有开启`map-underscore-to-camel-case: true`，这两个名字"对不上"
> - 结果：查到了数据，但`departmentName`属性为**null**
> - 检查方法：在日志中查看SQL确实返回了列，但Java对象中对应字段为空 → 八成是映射问题

### 13.4.2 resultMap自定义映射

当自动映射不够用时（关联查询、列名差异大、嵌套对象），就需要`resultMap`：

```xml
<resultMap id="EmployeeMap" type="Employee">
    <!-- id标签：主键列（影响缓存和比较性能） -->
    <id column="id" property="id"/>
    <!-- result标签：普通列 -->
    <result column="name" property="name"/>
    <result column="age" property="age"/>
    <result column="department" property="department"/>
    <result column="salary" property="salary"/>
    <result column="email" property="email"/>
    <result column="hire_date" property="hireDate"/>
</resultMap>

<select id="findById" resultMap="EmployeeMap">
    SELECT id, name, age, department, salary, email, hire_date
    FROM employee WHERE id = #{id}
</select>
```

> 🚨 **坑点：忘记写`<id>`标签 → 分页数据可能重复！**
> - `<id>`标签标记的是主键列，MyBatis用它来判断两行数据是否为"同一个对象"
> - 如果你没用`<id>`而全用了`<result>`，MyBatis认为**所有列共同组成主键**
> - 在分页查询中，如果相邻两页的第一条数据恰好所有列都相同（虽然罕见但理论上可能），MyBatis会错误地将它们视为同一对象，导致分页结果中出现**重复数据**
> - **结论：只要用了resultMap，务必用`<id>`标签标注主键列。**

### 13.4.3 association：一对一关联

场景：每个员工属于一个部门。查询员工时需要同时查出部门信息。

```java
// Department实体
@Data
public class Department {
    private Long id;
    private String name;
    private String location;
}

// Employee实体（增加department属性）
@Data
public class Employee {
    private Long id;
    private String name;
    // ...其他属性
    private Department department;  // 一对一关联
}
```

```xml
<resultMap id="EmployeeWithDeptMap" type="Employee">
    <id column="id" property="id"/>
    <result column="name" property="name"/>
    <result column="age" property="age"/>
    <result column="salary" property="salary"/>
    <!-- association：一对一关联 -->
    <association property="department" javaType="com.example.entity.Department">
        <id column="dept_id" property="id"/>
        <result column="dept_name" property="name"/>
        <result column="dept_location" property="location"/>
    </association>
</resultMap>

<select id="findByIdWithDept" resultMap="EmployeeWithDeptMap">
    SELECT e.id, e.name, e.age, e.salary,
           d.id AS dept_id, d.name AS dept_name, d.location AS dept_location
    FROM employee e
    LEFT JOIN department d ON e.department_id = d.id
    WHERE e.id = #{id}
</select>
```

`<association>` 告诉MyBatis：查询结果中有一组列（`dept_id`、`dept_name`、`dept_location`）应该映射到一个**单独的Java对象**（`Department`类型）中。

### 13.4.4 collection：一对多关联

场景：查询一个部门及其所有员工。

```java
// Department实体（增加employees属性）
@Data
public class Department {
    private Long id;
    private String name;
    private String location;
    private List<Employee> employees;  // 一对多关联
}
```

```xml
<resultMap id="DepartmentWithEmployeesMap" type="com.example.entity.Department">
    <id column="dept_id" property="id"/>
    <result column="dept_name" property="name"/>
    <result column="dept_location" property="location"/>
    <!-- collection：一对多关联 -->
    <collection property="employees" ofType="com.example.entity.Employee">
        <id column="emp_id" property="id"/>
        <result column="emp_name" property="name"/>
        <result column="emp_age" property="age"/>
        <result column="emp_salary" property="salary"/>
    </collection>
</resultMap>

<select id="findDeptWithEmployees" resultMap="DepartmentWithEmployeesMap">
    SELECT d.id AS dept_id, d.name AS dept_name, d.location AS dept_location,
           e.id AS emp_id, e.name AS emp_name, e.age AS emp_age, e.salary AS emp_salary
    FROM department d
    LEFT JOIN employee e ON d.id = e.department_id
    WHERE d.id = #{id}
</select>
```

`<collection>` 与 `<association>` 的关键区别：
- `<association>` 用 `javaType` 指定单一对象类型
- `<collection>` 用 `ofType` 指定集合中元素的类型

---

## 13.5 动态SQL — MyBatis的精华

如果说`#{}`的防注入是MyBatis的"盾"，那动态SQL就是MyBatis的"矛"。它让你用XML标签像写程序逻辑一样构建SQL语句——这才是MyBatis真正甩开JDBC的核心竞争力。

### 13.5.1 `<if>`：条件判断

最基础的动态标签，`test`属性使用OGNL表达式：

```xml
<select id="findByCondition" resultType="Employee">
    SELECT * FROM employee WHERE 1=1
    <if test="name != null and name != ''">
        AND name = #{name}
    </if>
    <if test="department != null and department != ''">
        AND department = #{department}
    </if>
</select>
```

> 🚨 **坑点：字符串判断必须用双引号外单引号内的写法！**
> - 正确：`test="name != null and name != ''"`
> - 错误：`test='name != null and name != ""'`（单引号和双引号冲突）
> - OGNL表达式中，字符串用单引号包裹，属性的引用直接用变量名

### 13.5.2 `<where>`：智能WHERE子句

上面用`WHERE 1=1`是"偷懒"写法，更好的做法是`<where>`标签：

```xml
<select id="findByCondition" resultType="Employee">
    SELECT * FROM employee
    <where>
        <if test="name != null and name != ''">
            AND name = #{name}
        </if>
        <if test="department != null and department != ''">
            AND department = #{department}
        </if>
        <if test="minSalary != null">
            AND salary >= #{minSalary}
        </if>
        <if test="maxSalary != null">
            AND salary &lt;= #{maxSalary}
        </if>
    </where>
    ORDER BY id
</select>
```

`<where>` 做了两件聪明事：
1. 如果内部至少有一个条件成立，自动在最前面插入`WHERE`关键字
2. 自动去除第一个条件前的`AND`或`OR`

假设只有`department='技术部'`有值，生成的SQL：

```sql
SELECT * FROM employee WHERE department = ? ORDER BY id
```

假设所有条件都为null/空，生成的SQL：

```sql
SELECT * FROM employee ORDER BY id
```

注意`<where>`自动去掉了`WHERE`——如果没有这个智能判断，SQL就变成了 `WHERE ORDER BY id`，直接语法错误。

### 13.5.3 `<set>`：动态UPDATE

更新操作的最大痛点：用户可能只改了部分字段，你不知道哪些字段需要写进SET子句。`<set>`标签完美解决：

```xml
<update id="updateSelective">
    UPDATE employee
    <set>
        <if test="name != null and name != ''">
            name = #{name},
        </if>
        <if test="age != null">
            age = #{age},
        </if>
        <if test="department != null and department != ''">
            department = #{department},
        </if>
        <if test="salary != null">
            salary = #{salary},
        </if>
        <if test="email != null and email != ''">
            email = #{email},
        </if>
    </set>
    WHERE id = #{id}
</update>
```

`<set>`做了两件事：
1. 自动在前面插入`SET`关键字
2. **自动去掉末尾多余的逗号**

假设只修改了`name`和`salary`，生成的SQL：

```sql
UPDATE employee SET name = ?, salary = ? WHERE id = ?
```

末尾的逗号被`<set>`智能去掉了，否则生成 `SET name = ?, salary = ?,` → SQL语法错误。

### 13.5.4 `<foreach>`：批量操作

批量操作是Web开发中最常遇到的场景之一：批量删除、批量查询、批量插入。`<foreach>`是专门为此设计的。

**场景一：IN查询（批量ID查询）**

```xml
<select id="findByIds" resultType="Employee">
    SELECT * FROM employee
    WHERE id IN
    <foreach collection="ids" item="id" open="(" close=")" separator=",">
        #{id}
    </foreach>
</select>
```

Java调用：
```java
List<Employee> employees = mapper.findByIds(Arrays.asList(1L, 2L, 3L, 5L));
```

生成的SQL：
```sql
SELECT * FROM employee WHERE id IN (?, ?, ?, ?)
```

**参数说明**：
| 属性 | 含义 | 示例值 |
|------|------|--------|
| `collection` | 要遍历的集合（List→list或@Param指定的名称） | `ids` |
| `item` | 每次遍历的当前元素变量名 | `id` |
| `open` | 遍历开始前拼接的字符串 | `(` |
| `close` | 遍历结束后拼接的字符串 | `)` |
| `separator` | 每个元素之间的分隔符 | `,` |

**场景二：批量插入**

```xml
<insert id="batchInsert">
    INSERT INTO employee (name, age, department, salary, email)
    VALUES
    <foreach collection="employees" item="emp" separator=",">
        (#{emp.name}, #{emp.age}, #{emp.department}, #{emp.salary}, #{emp.email})
    </foreach>
</insert>
```

> 🚨 **坑点：批量插入SQL过长 → 超过数据库最大包限制！**
> - MySQL默认 `max_allowed_packet = 4MB`（部分版本更低）
> - 如果一次插入10000条记录，生成的INSERT语句可能超过这个限制
> - 解决方案：分批插入，每次处理500-1000条
> ```java
> int batchSize = 500;
> for (int i = 0; i < employees.size(); i += batchSize) {
>     int end = Math.min(i + batchSize, employees.size());
>     mapper.batchInsert(employees.subList(i, end));
> }
> ```

**场景三：批量删除**

```xml
<delete id="batchDelete">
    DELETE FROM employee WHERE id IN
    <foreach collection="ids" item="id" open="(" close=")" separator=",">
        #{id}
    </foreach>
</delete>
```

### 13.5.5 `<trim>`：更灵活的前缀/后缀处理

`<where>`和`<set>`本质上都是`<trim>`的特例。`<trim>`给了你更精细的控制：

```xml
<!-- <where> 的 <trim> 等价写法 -->
<trim prefix="WHERE" prefixOverrides="AND |OR ">
    <if test="name != null">AND name = #{name}</if>
    <if test="department != null">AND department = #{department}</if>
</trim>

<!-- <set> 的 <trim> 等价写法 -->
<trim prefix="SET" suffixOverrides=",">
    <if test="name != null">name = #{name},</if>
    <if test="salary != null">salary = #{salary},</if>
</trim>
```

`<trim>`的四个属性：
| 属性 | 含义 | 示例 |
|------|------|------|
| `prefix` | 在内容前添加前缀 | `WHERE` / `SET` |
| `suffix` | 在内容后添加后缀 | `)` |
| `prefixOverrides` | 去掉内容开头的指定字符串 | `AND |OR ` |
| `suffixOverrides` | 去掉内容末尾的指定字符串 | `,` |

### 13.5.6 `<choose>` / `<when>` / `<otherwise>`：多分支选择

相当于Java的`switch-case-default`语句，用于"多个条件只选一个"的场景：

```xml
<select id="findByPriority" resultType="Employee">
    SELECT * FROM employee
    <where>
        <choose>
            <when test="id != null">
                AND id = #{id}
            </when>
            <when test="name != null and name != ''">
                AND name = #{name}
            </when>
            <when test="department != null and department != ''">
                AND department = #{department}
            </when>
            <otherwise>
                AND status = 'ACTIVE'
            </otherwise>
        </choose>
    </where>
</select>
```

逻辑：优先按ID查 → 没有ID则按姓名查 → 没有姓名则按部门查 → 都没有则查所有在职员工。

### 13.5.7 综合实战：多条件动态查询员工

结合以上所有标签，写一个完整的动态查询：

```xml
<select id="searchEmployees" resultType="Employee">
    SELECT id, name, age, department, salary, email, hire_date
    FROM employee
    <where>
        <if test="keyword != null and keyword != ''">
            AND (name LIKE CONCAT('%', #{keyword}, '%')
                 OR department LIKE CONCAT('%', #{keyword}, '%'))
        </if>
        <if test="department != null and department != ''">
            AND department = #{department}
        </if>
        <if test="minSalary != null">
            AND salary >= #{minSalary}
        </if>
        <if test="maxSalary != null">
            AND salary &lt;= #{maxSalary}
        </if>
        <if test="minAge != null">
            AND age >= #{minAge}
        </if>
        <if test="maxAge != null">
            AND age &lt;= #{maxAge}
        </if>
        <if test="hireDateStart != null">
            AND hire_date >= #{hireDateStart}
        </if>
        <if test="hireDateEnd != null">
            AND hire_date &lt;= #{hireDateEnd}
        </if>
        <if test="ids != null and ids.size() > 0">
            AND id IN
            <foreach collection="ids" item="id" open="(" close=")" separator=",">
                #{id}
            </foreach>
        </if>
    </where>
    ORDER BY
    <choose>
        <when test="orderBy == 'salary'">salary ${orderDirection}</when>
        <when test="orderBy == 'age'">age ${orderDirection}</when>
        <when test="orderBy == 'hire_date'">hire_date ${orderDirection}</when>
        <otherwise>id ASC</otherwise>
    </choose>
</select>
```

对应的Mapper接口方法：

```java
List<Employee> searchEmployees(
    @Param("keyword") String keyword,
    @Param("department") String department,
    @Param("minSalary") Double minSalary,
    @Param("maxSalary") Double maxSalary,
    @Param("minAge") Integer minAge,
    @Param("maxAge") Integer maxAge,
    @Param("hireDateStart") LocalDate hireDateStart,
    @Param("hireDateEnd") LocalDate hireDateEnd,
    @Param("ids") List<Long> ids,
    @Param("orderBy") String orderBy,
    @Param("orderDirection") String orderDirection
);
```

这个查询可以应对几乎所有的组合条件——每次前端传什么条件，SQL就动态添加什么WHERE子句。这就是MyBatis动态SQL的真正威力。

---

## 13.6 注解方式

MyBatis也支持纯注解开发，省去XML文件。对于简单CRUD场景，注解非常方便。

### 13.6.1 基本CRUD注解

```java
package com.example.mapper;

import com.example.entity.Employee;
import org.apache.ibatis.annotations.*;
import java.util.List;

@Mapper
public interface EmployeeAnnotationMapper {

    @Select("SELECT id, name, age, department, salary, email, hire_date " +
            "FROM employee ORDER BY id")
    List<Employee> findAll();

    @Select("SELECT id, name, age, department, salary, email, hire_date " +
            "FROM employee WHERE id = #{id}")
    Employee findById(Long id);

    @Insert("INSERT INTO employee (name, age, department, salary, email, hire_date) " +
            "VALUES (#{name}, #{age}, #{department}, #{salary}, #{email}, #{hireDate})")
    @Options(useGeneratedKeys = true, keyProperty = "id")
    int insert(Employee employee);

    @Update("UPDATE employee SET name=#{name}, age=#{age}, department=#{department}, " +
            "salary=#{salary}, email=#{email} WHERE id=#{id}")
    int update(Employee employee);

    @Delete("DELETE FROM employee WHERE id = #{id}")
    int deleteById(Long id);
}
```

### 13.6.2 结果映射注解

```java
@Select("SELECT id, name, age, department, salary, email, hire_date " +
        "FROM employee WHERE id = #{id}")
@Results({
    @Result(column = "id", property = "id", id = true),
    @Result(column = "name", property = "name"),
    @Result(column = "hire_date", property = "hireDate")
})
Employee findByIdWithMapping(Long id);
```

### 13.6.3 @Param：多参数绑定

Mapper接口中如果有多个参数，MyBatis默认用`arg0`、`arg1`或`param1`、`param2`来引用，这既不直观也容易出错。`@Param`可以为参数命名：

```java
@Select("SELECT * FROM employee WHERE department = #{dept} AND salary >= #{minSal}")
List<Employee> findByDeptAndMinSalary(
    @Param("dept") String department,
    @Param("minSal") Double minSalary
);
```

> 🚨 **坑点：复杂SQL不要用注解！**
> - 当SQL超过3-4行，或者涉及动态SQL（`<if>`、`<foreach>`）时，不要硬塞在注解里
> - 注解中的SQL是字符串拼接，没有语法高亮、没有IDE提示、多行时极其难维护
> - **原则：简单CRUD用注解，复杂查询用XML。** 一个项目中两种方式可以共存，各取所长。

### 13.6.4 XML vs 注解 对比总结

| 维度 | XML方式 | 注解方式 |
|------|---------|---------|
| **简单CRUD** | 需要单独文件，略繁琐 | 简洁，一目了然 |
| **复杂动态SQL** | 标签体系完备，可读性好 | 字符串拼接，可读性灾难 |
| **SQL与Java分离** | ✅ SQL独立管理 | ❌ SQL嵌入Java代码 |
| **DBA参与度** | DBA可以直接修改XML | DBA需要懂Java代码 |
| **IDE支持** | MyBatisX插件提供跳转、补全 | 普通字符串，无特殊支持 |
| **推荐场景** | 复杂查询、多条件动态SQL | 简单单表CRUD |
| **项目中如何选** | 主力方式 | 辅助方式 |

---

## 13.7 分页

在Web应用中，列表页面不可能一次加载几万条数据，分页是刚需。MyBatis本身不提供分页功能，但有两个成熟的方案。

### 13.7.1 PageHelper分页插件

PageHelper是国内使用最广泛的MyBatis分页插件，通过"拦截器"机制在SQL执行前自动追加LIMIT子句。

**引入依赖**：

```xml
<dependency>
    <groupId>com.github.pagehelper</groupId>
    <artifactId>pagehelper-spring-boot-starter</artifactId>
    <version>2.1.0</version>
</dependency>
```

**使用方式**：

```java
// 第1页，每页10条
PageHelper.startPage(1, 10);
List<Employee> employees = employeeMapper.findAll();  // 紧跟的查询自动分页
PageInfo<Employee> pageInfo = new PageInfo<>(employees);

System.out.println("总记录数: " + pageInfo.getTotal());
System.out.println("总页数: " + pageInfo.getPages());
System.out.println("当前页: " + pageInfo.getPageNum());
System.out.println("每页大小: " + pageInfo.getPageSize());
```

> 🚨 **坑点：`startPage`后必须紧跟查询，否则分页参数泄露到下一个查询！**
> - `PageHelper.startPage()` 使用 **ThreadLocal** 存储分页参数
> - 下一个执行的`select`查询会自动消费这个ThreadLocal中的分页参数
> - 如果你在`startPage`后先做了其他查询（比如检查权限、查询配置），那个查询就会被错误地加上LIMIT
> - **正确做法**：
> ```java
> PageHelper.startPage(pageNum, pageSize);   // 设置分页
> List<Employee> list = mapper.findAll();     // 紧跟分页查询
> PageInfo<Employee> page = new PageInfo<>(list);
> // 之后可以安全地做其他查询了
> ```

**PageInfo常用属性**：

| 属性 | 说明 |
|------|------|
| `getTotal()` | 总记录数 |
| `getPages()` | 总页数 |
| `getPageNum()` | 当前页码 |
| `getPageSize()` | 每页大小 |
| `getList()` | 当前页数据列表 |
| `isHasNextPage()` | 是否有下一页 |
| `isHasPreviousPage()` | 是否有上一页 |
| `getNavigatepageNums()` | 页码导航数组（如[1,2,3,4,5]） |

### 13.7.2 MyBatis Plus分页

MyBatis Plus是MyBatis的增强工具，提供了更简洁的分页方式：

```java
// 配置分页插件
@Configuration
public class MybatisPlusConfig {
    @Bean
    public MybatisPlusInterceptor mybatisPlusInterceptor() {
        MybatisPlusInterceptor interceptor = new MybatisPlusInterceptor();
        interceptor.addInnerInterceptor(new PaginationInnerInterceptor(DbType.MYSQL));
        return interceptor;
    }
}

// 使用
Page<Employee> page = new Page<>(1, 10);  // 第1页，每页10条
Page<Employee> result = employeeMapper.selectPage(page, null);
```

> **提示**：MyBatis Plus将在第17章详细讲解。本章先掌握PageHelper即可满足基本分页需求。

---

## 13.8 本章小结

恭喜你完成了MyBatis的学习！这是Java持久化层中最重要的技能之一。回顾本章的收获：

1. **JDBC痛点 → MyBatis解决方案**：硬编码SQL、手动设参、手动封装结果、资源管理 —— MyBatis用XML分离SQL、`#{}`自动绑定、resultType自动映射、SqlSession自动管理资源，将CRUD代码量从JDBC的~500行压缩到~100行。

2. **#{} vs ${}安全性**：
   - `#{}` = PreparedStatement占位符 → 预编译 + 参数值转义 → **安全**
   - `${}` = 字符串直接拼接 → 改变SQL语义 → **有注入风险**
   - 只有在动态表名/列名/排序字段等`#{}`无法替代的场景才用`${}`，且必须**白名单校验**
   - 亲自演示了SQL注入攻击的完整过程 —— 知道危险在哪里，才能避开它

3. **resultMap映射体系**：
   - 自动映射（驼峰转换）+ 手动resultMap（id/result标签）
   - association（一对一）和collection（一对多）处理关联查询
   - `<id>`标签的正确使用对性能和数据准确性至关重要

4. **动态SQL六种标签**：`<if>`（条件）、`<where>`（智能WHERE）、`<set>`（智能UPDATE）、`<foreach>`（批量）、`<trim>`（万能前缀后缀）、`<choose>`（多分支）—— 这是MyBatis区别于JDBC最闪亮的地方

5. **注解 vs XML**：简单CRUD用注解，复杂动态查询用XML，两者可以和谐共存

6. **分页**：PageHelper一行`startPage()`实现物理分页，但要注意"紧跟查询"的规则

---

## 思考题

1. 以下Mapper方法存在严重安全漏洞，请指出并给出修正方案：

   ```java
   @Select("SELECT * FROM employee ORDER BY ${column} ${direction}")
   List<Employee> findByOrder(@Param("column") String column, @Param("direction") String direction);
   ```

2. `#{}`和`${}`在生成的SQL日志中有什么不同？从日志中如何判断一个项目是否存在SQL注入风险？

3. 以下动态SQL有什么潜在问题？

   ```xml
   <select id="findByCondition" resultType="Employee">
       SELECT * FROM employee WHERE
       <if test="name != null">
           name = #{name}
       </if>
       <if test="department != null">
           AND department = #{department}
       </if>
   </select>
   ```

4. 在`<collection>`标签中，为什么是用`ofType`而不是`javaType`？

5. PageHelper的`startPage`使用了ThreadLocal机制。如果在一个方法中先后调用了`startPage`和两次Mapper查询，分别获取第1页和第2页数据，会出现什么问题？如何修正？

---

<details>
<summary>思考题参考答案（点击展开）</summary>

**第1题**：

此为SQL注入漏洞，`${column}`和`${direction}`直接拼接用户输入。

修正方案：

```java
// Java端白名单校验
private static final Set<String> ALLOWED_COLUMNS = Set.of("id", "name", "age", "salary", "hire_date");
private static final Set<String> ALLOWED_DIRECTIONS = Set.of("ASC", "DESC");

public List<Employee> findByOrder(String column, String direction) {
    if (column == null || !ALLOWED_COLUMNS.contains(column)) {
        throw new IllegalArgumentException("不支持的排序列: " + column);
    }
    if (direction == null || !ALLOWED_DIRECTIONS.contains(direction.toUpperCase())) {
        throw new IllegalArgumentException("不支持的排序方向: " + direction);
    }
    return mapper.findByOrderSafe(column, direction.toUpperCase());
}
```

```java
@Select("SELECT * FROM employee ORDER BY ${column} ${direction}")
List<Employee> findByOrderSafe(@Param("column") String column, @Param("direction") String direction);
```

关键：白名单校验在Java层完成，确保传到Mapper的`column`和`direction`只能是预定义的合法值。

**第2题**：

- `#{}`日志：`Preparing: SELECT * FROM employee WHERE name=? AND password=?` `Parameters: admin(String), 123456(String)` ——SQL模板和参数分离显示
- `${}`日志：`Preparing: SELECT * FROM employee WHERE name='admin' AND password='123456'` ——参数直接嵌入SQL，无Parameters行

**判断方法**：如果日志中频繁出现没有`?`占位符的SQL语句，且WHERE条件值直接拼在SQL中，就存在注入风险。

**第3题**：

问题：如果`name`为null但`department`有值，生成的SQL是：

```sql
SELECT * FROM employee WHERE AND department = ?
```

开头多了一个`AND`，语法错误。

修正：用`<where>`标签包裹，它会自动去掉多余的`AND`：

```xml
<select id="findByCondition" resultType="Employee">
    SELECT * FROM employee
    <where>
        <if test="name != null">AND name = #{name}</if>
        <if test="department != null">AND department = #{department}</if>
    </where>
</select>
```

**第4题**：

- `javaType`用于指定**单个对象**的类型（如`Department`）→ 用于`<association>`
- `ofType`用于指定**集合中元素**的类型（如`Employee`）→ 用于`<collection>`
- `<collection property="employees" ofType="Employee">` 表示`employees`是一个List，其中每个元素是`Employee`类型。MyBatis需要知道元素类型才能正确映射每一行数据的子对象。

**第5题**：

第一次调用`startPage` → 执行查询A → 获得第1页数据。此时ThreadLocal中的分页参数**已被消费**。第二次执行查询B时，ThreadLocal中已经没有分页参数，查询B会返回全部数据而不是第2页。

修正：每次分页查询前都要重新调用`startPage`：

```java
PageHelper.startPage(1, 10);
List<Employee> page1 = mapper.findAll();

PageHelper.startPage(2, 10);  // 重新设置
List<Employee> page2 = mapper.findAll();
```

这正是"startPage后必须紧跟查询"规则的另一面：一个startPage只管它后面**第一个查询**。

</details>

---

> **下一篇预告**：第14章将学习Spring Data JPA —— 一种与MyBatis完全不同的持久化哲学。JPA不是给你SQL的控制权，而是把SQL从你手中"夺走"，让你用面向对象的方式操作数据库。你将理解ORM的本质、掌握JPA核心注解、学会Repository方法命名查询，最重要的是：学会**MyBatis和JPA各自适用什么场景**。在章末，我们还会交付EMS v4 —— 用MyBatis和JPA两种方式实现同一个员工CRUD系统，让你亲身体验两者的差异。
>
> **学习路线回顾**：
> - 第8章：SQL → 你学会了怎么直接操作数据库
> - 第9章：JDBC → 你学会了Java怎么连接数据库
> - 第13章：MyBatis → 你学会了半自动化的SQL映射
> - 第14章：JPA → 你将学会全自动化的ORM
>
> 这是一个从底层到高层的完整进化过程，理解每一步的演进逻辑，你才能真正驾驭Java持久化体系。