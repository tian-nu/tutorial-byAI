# 第17章：Spring Boot集成数据访问层

## 本章目标

学完本章你将能够：

- 在Spring Boot中整合MyBatis，完成从Controller到XML的完整CRUD链路
- 使用MyBatis Plus的BaseMapper和LambdaQueryWrapper快速开发
- 在Spring Boot中整合JPA，掌握ddl-auto配置策略
- **深入掌握@Transactional事务管理，亲手复现7种事务失效场景并理解其根因**
- 配置多数据源实现读写分离
- 使用Flyway进行数据库版本管理
- **完成EMS v5：Spring Boot版员工管理系统**——一个完整的三层架构RESTful API后端

---

> **本章定位**：第13章和第14章我们深入学习了MyBatis和JPA本身。本章将它们整合到Spring Boot中——利用Spring Boot的自动配置，大幅简化数据访问层的搭建。同时，事务管理是本章的硬核核心，7种事务失效场景的复现和修复，将让你在面试和实战中从容应对。

---

## 17.1 整合MyBatis

### 17.1.1 添加依赖

在`pom.xml`中添加：

```xml
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
```

### 17.1.2 配置文件详解

在`application.yml`中：

```yaml
spring:
  datasource:
    url: jdbc:mysql://localhost:3306/ems?useSSL=false&serverTimezone=Asia/Shanghai&characterEncoding=utf8mb4
    username: root
    password: root
    driver-class-name: com.mysql.cj.jdbc.Driver    # MySQL 8驱动类
    hikari:                                         # HikariCP连接池配置
      maximum-pool-size: 20
      minimum-idle: 5
      connection-timeout: 3000
      idle-timeout: 600000
      max-lifetime: 1800000

mybatis:
  mapper-locations: classpath:mapper/**/*.xml       # Mapper XML文件位置
  type-aliases-package: com.example.springbootdemo.entity  # 实体类别名
  configuration:
    map-underscore-to-camel-case: true              # 下划线转驼峰
    log-impl: org.apache.ibatis.logging.stdout.StdOutImpl  # 打印SQL（开发用）
```

**每行配置解读**：

- `mapper-locations`：指定Mapper XML的位置。`classpath:mapper/**/*.xml`表示扫描`resources/mapper/`目录及其子目录下所有`.xml`文件。
- `type-aliases-package`：指定实体类所在的包。之后在XML中写`resultType="Employee"`而不需要写全限定名。
- `map-underscore-to-camel-case`：**必须开启！** 数据库字段`hire_date`自动映射到Java属性`hireDate`。不开的话所有带下划线的字段映射为null。
- `log-impl`：将SQL语句输出到控制台，开发调试用。**生产环境必须关闭或改为DEBUG级别！**

> 🚨 **致命坑点：mapper-locations路径写错 → 找不到mapped statement**
> 
> ```yaml
> # ❌ 常见错误写法：
> mybatis:
>   mapper-locations: mapper/*.xml          # 相对路径，非classpath！
>   mapper-locations: classpath:mapper/*.xml # 只匹配mapper目录下的.xml，不包含子目录！
> ```
> 
> 正确的写法是：`classpath:mapper/**/*.xml`（`**`表示任意层级子目录）。
> 
> 启动时报错：
> ```
> org.apache.ibatis.binding.BindingException: Invalid bound statement (not found):
>   com.example.springbootdemo.mapper.EmployeeMapper.selectById
> ```
> 这就是典型的XML文件没被扫描到——检查`mapper-locations`路径是否正确。

### 17.1.3 @Mapper vs @MapperScan

**方式1：@Mapper（每个Mapper接口上加）**

```java
@Mapper
public interface EmployeeMapper {
    Employee selectById(Long id);
    // ...
}
```

每个Mapper接口都要加，10个Mapper就要加10次——繁琐。

**方式2：@MapperScan（启动类上加，推荐）**

```java
@SpringBootApplication
@MapperScan("com.example.springbootdemo.mapper")
public class SpringbootDemoApplication {
    public static void main(String[] args) {
        SpringApplication.run(SpringbootDemoApplication.class, args);
    }
}
```

一次配置，`mapper`包下所有接口自动注册。

> 🚨 **坑点：@MapperScan的basePackages路径写错 → Mapper Bean未创建**
> 
> ```java
> @MapperScan("com.example.mapper")           // ❌ 路径不对
> @MapperScan("com.example.springbootdemo.*") // ❌ 通配符不支持
> @MapperScan(basePackages = {                 // ✅ 正确
>     "com.example.springbootdemo.mapper",
>     "com.example.springbootdemo.other.mapper"
> })
> ```

### 17.1.4 完整CRUD演示

以下是从数据库到Controller的完整四层链路。

**步骤1：实体类**

```java
package com.example.springbootdemo.entity;

import lombok.Data;
import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;

@Data
public class Employee {
    private Long id;
    private String name;
    private Integer age;
    private String department;
    private BigDecimal salary;
    private String email;
    private LocalDate hireDate;
    private LocalDateTime createTime;
    private LocalDateTime updateTime;
}
```

**步骤2：Mapper接口**

```java
package com.example.springbootdemo.mapper;

import com.example.springbootdemo.entity.Employee;
import org.apache.ibatis.annotations.Param;
import java.util.List;

public interface EmployeeMapper {

    Employee selectById(@Param("id") Long id);

    List<Employee> selectAll();

    List<Employee> selectByDepartment(@Param("department") String department);

    List<Employee> selectByCondition(@Param("name") String name,
                                     @Param("department") String department,
                                     @Param("minSalary") BigDecimal minSalary);

    int insert(Employee employee);

    int update(Employee employee);

    int deleteById(@Param("id") Long id);

    int batchInsert(@Param("list") List<Employee> list);
}
```

**步骤3：Mapper XML**

`src/main/resources/mapper/EmployeeMapper.xml`：

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE mapper PUBLIC "-//mybatis.org//DTD Mapper 3.0//EN"
        "http://mybatis.org/dtd/mybatis-3-mapper.dtd">
<mapper namespace="com.example.springbootdemo.mapper.EmployeeMapper">

    <!-- 公共列（避免重复书写） -->
    <sql id="baseColumns">
        id, name, age, department, salary, email, hire_date, create_time, update_time
    </sql>

    <!-- 按ID查询 -->
    <select id="selectById" resultType="Employee">
        SELECT <include refid="baseColumns"/>
        FROM employee
        WHERE id = #{id}
    </select>

    <!-- 查询所有 -->
    <select id="selectAll" resultType="Employee">
        SELECT <include refid="baseColumns"/>
        FROM employee
        ORDER BY id DESC
    </select>

    <!-- 按部门查询 -->
    <select id="selectByDepartment" resultType="Employee">
        SELECT <include refid="baseColumns"/>
        FROM employee
        WHERE department = #{department}
    </select>

    <!-- 动态多条件查询（本章核心演示：<where> + <if>） -->
    <select id="selectByCondition" resultType="Employee">
        SELECT <include refid="baseColumns"/>
        FROM employee
        <where>
            <if test="name != null and name != ''">
                AND name LIKE CONCAT('%', #{name}, '%')
            </if>
            <if test="department != null and department != ''">
                AND department = #{department}
            </if>
            <if test="minSalary != null">
                AND salary >= #{minSalary}
            </if>
        </where>
        ORDER BY id DESC
    </select>

    <!-- 插入 -->
    <insert id="insert" useGeneratedKeys="true" keyProperty="id">
        INSERT INTO employee (name, age, department, salary, email, hire_date)
        VALUES (#{name}, #{age}, #{department}, #{salary}, #{email}, #{hireDate})
    </insert>

    <!-- 更新 -->
    <update id="update">
        UPDATE employee
        <set>
            <if test="name != null and name != ''">name = #{name},</if>
            <if test="age != null">age = #{age},</if>
            <if test="department != null">department = #{department},</if>
            <if test="salary != null">salary = #{salary},</if>
            <if test="email != null">email = #{email},</if>
            <if test="hireDate != null">hire_date = #{hireDate},</if>
            update_time = NOW()
        </set>
        WHERE id = #{id}
    </update>

    <!-- 删除 -->
    <delete id="deleteById">
        DELETE FROM employee WHERE id = #{id}
    </delete>

    <!-- 批量插入 -->
    <insert id="batchInsert" useGeneratedKeys="true" keyProperty="id">
        INSERT INTO employee (name, age, department, salary, email, hire_date)
        VALUES
        <foreach collection="list" item="emp" separator=",">
            (#{emp.name}, #{emp.age}, #{emp.department},
             #{emp.salary}, #{emp.email}, #{emp.hireDate})
        </foreach>
    </insert>

</mapper>
```

**步骤4：Service层**

```java
package com.example.springbootdemo.service;

import com.example.springbootdemo.common.ResultCode;
import com.example.springbootdemo.common.exception.BusinessException;
import com.example.springbootdemo.entity.Employee;
import com.example.springbootdemo.mapper.EmployeeMapper;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
@RequiredArgsConstructor
public class EmployeeService {

    private final EmployeeMapper employeeMapper;

    public Employee findById(Long id) {
        Employee employee = employeeMapper.selectById(id);
        if (employee == null) {
            throw new BusinessException(ResultCode.USER_NOT_FOUND, "员工不存在，ID: " + id);
        }
        return employee;
    }

    public List<Employee> findAll() {
        return employeeMapper.selectAll();
    }

    public List<Employee> findByDepartment(String department) {
        return employeeMapper.selectByDepartment(department);
    }

    public List<Employee> findByCondition(String name, String department, BigDecimal minSalary) {
        return employeeMapper.selectByCondition(name, department, minSalary);
    }

    @Transactional
    public Employee save(Employee employee) {
        employeeMapper.insert(employee);
        return employee;  // 返回带自增ID的对象
    }

    @Transactional
    public Employee update(Employee employee) {
        Employee exist = findById(employee.getId());  // 先查是否存在
        employeeMapper.update(employee);
        return findById(employee.getId());
    }

    @Transactional
    public void deleteById(Long id) {
        Employee exist = findById(employee.getId());  // 先查是否存在
        employeeMapper.deleteById(id);
    }

    @Transactional
    public void batchSave(List<Employee> employees) {
        employeeMapper.batchInsert(employees);
    }
}
```

**步骤5：Controller层**（复用第16章的Result类和全局异常处理）

```java
package com.example.springbootdemo.controller;

import com.example.springbootdemo.common.Result;
import com.example.springbootdemo.common.ResultCode;
import com.example.springbootdemo.entity.Employee;
import com.example.springbootdemo.service.EmployeeService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.math.BigDecimal;
import java.util.List;

@RestController
@RequestMapping("/api/employees")
@RequiredArgsConstructor
public class EmployeeController {

    private final EmployeeService employeeService;

    @GetMapping("/{id}")
    public Result<Employee> getById(@PathVariable Long id) {
        return Result.success(employeeService.findById(id));
    }

    @GetMapping
    public Result<List<Employee>> list(
            @RequestParam(required = false) String name,
            @RequestParam(required = false) String department,
            @RequestParam(required = false) BigDecimal minSalary) {
        if (name != null || department != null || minSalary != null) {
            return Result.success(employeeService.findByCondition(name, department, minSalary));
        }
        return Result.success(employeeService.findAll());
    }

    @PostMapping
    public Result<Employee> create(@RequestBody @Valid Employee employee) {
        return Result.success(employeeService.save(employee));
    }

    @PutMapping("/{id}")
    public Result<Employee> update(@PathVariable Long id, @RequestBody Employee employee) {
        employee.setId(id);
        return Result.success(employeeService.update(employee));
    }

    @DeleteMapping("/{id}")
    public Result<Void> delete(@PathVariable Long id) {
        employeeService.deleteById(id);
        return Result.success();
    }
}
```

**步骤6：application.yml 数据源配置确认**

```yaml
spring:
  datasource:
    url: jdbc:mysql://localhost:3306/ems?useSSL=false&serverTimezone=Asia/Shanghai&characterEncoding=utf8mb4
    username: root
    password: root
    driver-class-name: com.mysql.cj.jdbc.Driver

mybatis:
  mapper-locations: classpath:mapper/**/*.xml
  type-aliases-package: com.example.springbootdemo.entity
  configuration:
    map-underscore-to-camel-case: true
    log-impl: org.apache.ibatis.logging.stdout.StdOutImpl
```

---

## 17.2 整合MyBatis Plus

MyBatis Plus（简称MP）是MyBatis的增强工具，在MyBatis的基础上只做增强不做改变。如果你的项目使用了MyBatis Plus，开发效率会进一步提升。

### 17.2.1 依赖切换

只需把MyBatis Starter换成MyBatis Plus Starter：

```xml
<!-- 替换原来的 mybatis-spring-boot-starter -->
<dependency>
    <groupId>com.baomidou</groupId>
    <artifactId>mybatis-plus-spring-boot3-starter</artifactId>
    <version>3.5.5</version>
</dependency>
```

注意：**Spring Boot 3.x必须使用`mybatis-plus-spring-boot3-starter`**，不能用`mybatis-plus-boot-starter`（那是给Spring Boot 2.x用的）。

### 17.2.2 配置文件调整

```yaml
mybatis-plus:                               # 注意：前缀改为 mybatis-plus
  mapper-locations: classpath:mapper/**/*.xml
  type-aliases-package: com.example.springbootdemo.entity
  configuration:
    map-underscore-to-camel-case: true
    log-impl: org.apache.ibatis.logging.stdout.StdOutImpl
  global-config:
    db-config:
      id-type: auto                         # 主键自增
      logic-delete-field: deleted           # 逻辑删除字段
      logic-delete-value: 1                 # 已删除的值
      logic-not-delete-value: 0             # 未删除的值
```

`@MapperScan`依然有效，但路径要改成MyBatis Plus的：

```java
import com.baomidou.mybatisplus.annotation.MapperScan;

@SpringBootApplication
@MapperScan("com.example.springbootdemo.mapper")
public class SpringbootDemoApplication { ... }
```

### 17.2.3 BaseMapper — 零SQL的CRUD

继承`BaseMapper<T>`后，你不需要写任何SQL就能获得完整的CRUD能力：

```java
package com.example.springbootdemo.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.example.springbootdemo.entity.Employee;

public interface EmployeeMapper extends BaseMapper<Employee> {
    // BaseMapper已内置以下方法（无需定义！）：
    // int insert(T entity)
    // int deleteById(Serializable id)
    // int updateById(T entity)
    // T selectById(Serializable id)
    // List<T> selectBatchIds(Collection<Serializable> idList)
    // List<T> selectByMap(Map<String, Object> columnMap)
    // Long selectCount(Wrapper<T> queryWrapper)
    // List<T> selectList(Wrapper<T> queryWrapper)
    // ...

    // 你只需要写复杂查询的自定义方法（XML依然可用）
}
```

### 17.2.4 LambdaQueryWrapper — 链式查询防字段名写错

传统方式写字段名时容易拼错（如`"departmnet"`），用了Lambda就绝不会错：

```java
@Service
@RequiredArgsConstructor
public class EmployeeService {

    private final EmployeeMapper employeeMapper;

    public List<Employee> search(String name, String department, BigDecimal minSalary) {
        LambdaQueryWrapper<Employee> wrapper = new LambdaQueryWrapper<>();

        wrapper.like(StringUtils.hasText(name), Employee::getName, name)
               .eq(StringUtils.hasText(department), Employee::getDepartment, department)
               .ge(minSalary != null, Employee::getSalary, minSalary)
               .orderByDesc(Employee::getId);

        return employeeMapper.selectList(wrapper);
    }
}
```

`LambdaQueryWrapper`通过方法引用（如`Employee::getName`）指定字段，IDE会有代码提示，编译期就能发现字段名错误——这比字符串方式安全太多。

### 17.2.5 MyBatis Plus分页

**配置分页插件**：

```java
package com.example.springbootdemo.config;

import com.baomidou.mybatisplus.annotation.DbType;
import com.baomidou.mybatisplus.extension.plugins.MybatisPlusInterceptor;
import com.baomidou.mybatisplus.extension.plugins.inner.PaginationInnerInterceptor;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class MybatisPlusConfig {

    @Bean
    public MybatisPlusInterceptor mybatisPlusInterceptor() {
        MybatisPlusInterceptor interceptor = new MybatisPlusInterceptor();
        interceptor.addInnerInterceptor(
                new PaginationInnerInterceptor(DbType.MYSQL));
        return interceptor;
    }
}
```

**Service中使用**：

```java
public IPage<Employee> findByPage(int page, int size) {
    Page<Employee> pageParam = new Page<>(page, size);
    LambdaQueryWrapper<Employee> wrapper = new LambdaQueryWrapper<>();
    wrapper.orderByDesc(Employee::getId);
    return employeeMapper.selectPage(pageParam, wrapper);
    // IPage中包含：records（当前页数据）、total（总记录数）、pages（总页数）、current（当前页码）
}
```

**Controller中使用**：

```java
@GetMapping("/page")
public Result<IPage<Employee>> page(
        @RequestParam(defaultValue = "1") int page,
        @RequestParam(defaultValue = "10") int size) {
    return Result.success(employeeService.findByPage(page, size));
}
```

---

## 17.3 整合JPA

如果你是JPA阵营的，Spring Boot对JPA的支持同样出色。

### 17.3.1 依赖

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-data-jpa</artifactId>
</dependency>
<!-- MySQL驱动与之前相同，无需重复添加 -->
```

### 17.3.2 配置

```yaml
spring:
  datasource:
    url: jdbc:mysql://localhost:3306/ems?useSSL=false&serverTimezone=Asia/Shanghai&characterEncoding=utf8mb4
    username: root
    password: root
    driver-class-name: com.mysql.cj.jdbc.Driver
  jpa:
    hibernate:
      ddl-auto: validate      # ★ 生产环境必须validate或none！
    show-sql: false            # 生产环境必须false
    properties:
      hibernate:
        format_sql: true       # 格式化SQL输出（开发时开）
```

> 🚨 **致命坑点：ddl-auto取值生产环境必须极其谨慎！**
> 
> | 值 | 行为 | 风险 |
> |----|------|------|
> | `none` | 什么都不做 | 最安全 |
> | `validate` | 只校验实体与表结构是否匹配 | 安全，推荐 |
> | `update` | 自动修改表结构以匹配实体 | **生产禁用！** 可能删字段、改类型 |
> | `create` | 每次启动删除旧表建新表 | **生产禁用！** 数据全丢 |
> | `create-drop` | 启动创建，关闭删除 | **生产禁用！** |
> 
> 生产环境用`none`或`validate`。`update`在开发阶段很方便，但如果删了实体类中的某个字段，Hibernate会直接把那列DROP掉——数据全丢了！

### 17.3.3 实体类

```java
package com.example.springbootdemo.entity;

import jakarta.persistence.*;
import lombok.Data;
import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;

@Data
@Entity
@Table(name = "employee")
public class Employee {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)  // MySQL自增主键
    private Long id;

    @Column(nullable = false, length = 20)
    private String name;

    @Column(nullable = false)
    private Integer age;

    @Column(nullable = false, length = 50)
    private String department;

    @Column(nullable = false, precision = 10, scale = 2)
    private BigDecimal salary;

    @Column(length = 100)
    private String email;

    @Column(name = "hire_date")
    private LocalDate hireDate;

    @Column(name = "create_time", updatable = false)
    private LocalDateTime createTime;

    @Column(name = "update_time")
    private LocalDateTime updateTime;

    @PrePersist
    protected void onCreate() {
        createTime = LocalDateTime.now();
        updateTime = LocalDateTime.now();
    }

    @PreUpdate
    protected void onUpdate() {
        updateTime = LocalDateTime.now();
    }
}
```

### 17.3.4 Repository

```java
package com.example.springbootdemo.repository;

import com.example.springbootdemo.entity.Employee;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.math.BigDecimal;
import java.util.List;

@Repository
public interface EmployeeRepository extends JpaRepository<Employee, Long> {

    // 方法命名查询
    List<Employee> findByDepartment(String department);

    List<Employee> findBySalaryGreaterThanEqual(BigDecimal minSalary);

    List<Employee> findByNameContaining(String keyword);

    List<Employee> findByDepartmentAndSalaryGreaterThanEqual(String department, BigDecimal salary);
}
```

JpaRepository的CRUD使用与Service层的整合与MyBatis完全相同——因为你已经在17.1.4节定义了Service接口规范，无论底层是MyBatis还是JPA，Controller和Service的代码几乎不用变（只需在Service实现中把`EmployeeMapper`换成`EmployeeRepository`）。

---

## 17.4 事务管理 — 7种失效场景深度剖析

这是本章最重要的一节。`@Transactional`看似简单，实则隐藏了大量容易踩的坑。面试中关于"事务失效场景"的考察频率极高，因为**真正理解事务失效的原因，意味着你理解了Spring AOP的代理机制、异常传播规则、数据库底层特性**。

### 17.4.1 @Transactional 的核心属性

```java
@Transactional(
    propagation = Propagation.REQUIRED,       // 传播行为
    isolation = Isolation.DEFAULT,            // 隔离级别
    rollbackFor = {RuntimeException.class, Error.class}, // 回滚的异常类型（默认！）
    noRollbackFor = {},                       // 不回滚的异常类型
    timeout = -1,                             // 超时时间（秒），-1表示无限制
    readOnly = false,                         // 是否只读
    transactionManager = "transactionManager" // 指定事务管理器
)
```

#### propagation（传播行为）— 7种值

| 传播行为 | 含义 | 使用场景 |
|----------|------|---------|
| `REQUIRED`（默认） | 有事务则加入，无则新建 | 最常见，增删改操作 |
| `REQUIRES_NEW` | 永远新建事务，挂起当前事务 | 日志记录（日志不应因主业务回滚而回滚） |
| `SUPPORTS` | 有事务则加入，无则非事务运行 | 查询操作（可有可无） |
| `NOT_SUPPORTED` | 非事务运行，挂起当前事务 | 不需要事务的操作 |
| `MANDATORY` | 必须在事务中运行，否则抛异常 | 要求调用方必须开事务 |
| `NEVER` | 必须非事务运行，否则抛异常 | 明确禁止事务的场景 |
| `NESTED` | 嵌套事务（保存点机制） | 部分回滚场景 |

#### isolation（隔离级别）— 4种值 + DEFAULT

| 隔离级别 | 脏读 | 不可重复读 | 幻读 | 性能 |
|----------|------|-----------|------|------|
| `READ_UNCOMMITTED` | ✅可能 | ✅可能 | ✅可能 | 最高 |
| `READ_COMMITTED` | ❌ | ✅可能 | ✅可能 | 高 |
| `REPEATABLE_READ`（MySQL默认） | ❌ | ❌ | ✅可能 | 中 |
| `SERIALIZABLE` | ❌ | ❌ | ❌ | 低 |
| `DEFAULT` | 使用数据库默认级别 | — | — | — |

> 绝大多数业务场景使用`DEFAULT`即可，Spring会将这个值委托给数据库默认隔离级别（MySQL为REPEATABLE_READ）。

### 17.4.2 事务失效7种场景（每种附可复现代码）

下面7种场景是导致`@Transactional`失效的最常见原因。每一种都附带了**可复制运行**的代码——你可以在自己的项目中直接用，看效果，加深理解。

---

#### 场景1：非public方法 → 事务失效

**原理**：Spring AOP基于动态代理，默认只能代理public方法。如果方法不是public的，代理对象无法拦截它，事务切面就不会织入。

**可复现代码**：

```java
@Service
public class EmployeeService {

    @Autowired
    private EmployeeMapper employeeMapper;

    // ❌ 事务失效！方法非public
    @Transactional
    void saveInternal(Employee employee) {
        employeeMapper.insert(employee);
        int i = 1 / 0;  // 故意抛异常
        employeeMapper.insert(employee);
    }

    // ✅ 正确写法
    @Transactional
    public void save(Employee employee) {
        employeeMapper.insert(employee);
        int i = 1 / 0;
        employeeMapper.insert(employee);
    }
}
```

**验证方法**：分别调用`saveInternal`（通过外部类调用或改为public测试）和`save`，观察数据库中是否插入了数据。`saveInternal`的方法不是public，异常发生后数据仍然被插入了（事务未生效）。

---

#### 场景2：同类内部调用 → 事务失效

**原理**：这也是第11章AOP中讲过的。Spring的事务是通过**代理对象**实现的。当你在同一个类中，方法A调用方法B时，调用的是`this.methodB()`，而不是`proxy.methodB()`——this是原始对象，不是代理对象，所以事务切面不生效。

**可复现代码**：

```java
@Service
public class EmployeeService {

    @Autowired
    private EmployeeMapper employeeMapper;

    // 外部调用此方法（非事务）
    public void doBatchSave(List<Employee> employees) {
        for (Employee emp : employees) {
            this.saveOne(emp);  // ← this调用！不是代理调用！
        }
    }

    @Transactional  // ← 这个事务注解失效了！
    public void saveOne(Employee employee) {
        employeeMapper.insert(employee);
        if (employee.getName().equals("error")) {
            throw new RuntimeException("测试回滚");
        }
    }
}
```

**验证**：传入一个包含`name="error"`的列表。你会发现"error"之前的员工已经插入了，没有回滚——因为`saveOne`上的`@Transactional`根本没生效。

**解决方案（4种）**：

```java
// 方案1：把saveOne移到另一个Service中（推荐，最简单）
@Service
public class EmployeeSaveService {
    @Transactional
    public void saveOne(Employee employee) { ... }
}

// 方案2：自己注入自己（利用代理）
@Service
public class EmployeeService {
    @Autowired
    private EmployeeService self;  // 注入自己的代理对象

    public void doBatchSave(List<Employee> employees) {
        for (Employee emp : employees) {
            self.saveOne(emp);  // 通过代理调用
        }
    }

    @Transactional
    public void saveOne(Employee employee) { ... }
}

// 方案3：AopContext.currentProxy()
// 需要在启动类上加 @EnableAspectJAutoProxy(exposeProxy = true)
public void doBatchSave(List<Employee> employees) {
    EmployeeService proxy = (EmployeeService) AopContext.currentProxy();
    for (Employee emp : employees) {
        proxy.saveOne(emp);
    }
}

// 方案4：直接在调用方加@Transactional
@Transactional
public void doBatchSave(List<Employee> employees) {
    for (Employee emp : employees) {
        saveOne(emp);  // 此时整个doBatchSave在事务中，saveOne的不生效也无妨
    }
}
```

---

#### 场景3：异常被catch吃掉 → 事务不回滚

**原理**：Spring只在事务方法**向外抛出**异常时才触发回滚。如果你在方法内部try-catch了异常且没有再抛出，Spring根本感知不到异常的发生，自然不会回滚。

**可复现代码**：

```java
@Service
public class EmployeeService {

    @Autowired
    private EmployeeMapper employeeMapper;

    @Transactional
    public void saveWithCatch(Employee employee) {
        try {
            employeeMapper.insert(employee);
            int i = 1 / 0;           // ArithmeticException
            employeeMapper.insert(employee);
        } catch (Exception e) {
            log.error("出错了: {}", e.getMessage());
            // ❌ 没有重新抛出！Spring感知不到异常
            // 结果：第一条insert已经提交了！
        }
    }

    @Transactional
    public void saveWithRethrow(Employee employee) {
        try {
            employeeMapper.insert(employee);
            int i = 1 / 0;
            employeeMapper.insert(employee);
        } catch (Exception e) {
            log.error("出错了: {}", e.getMessage());
            throw new BusinessException(ResultCode.BUSINESS_ERROR, "保存失败");  // ✅ 重新抛出
        }
    }
}
```

**验证**：调用`saveWithCatch`后检查数据库——employee被插入了（没有回滚）。调用`saveWithRethrow`后检查——employee没有插入（回滚成功）。

> **重要**：有时候你需要catch异常做一些补偿操作（如发送告警），然后仍然需要回滚——此时catch后一定要重新抛出异常或手动回滚。

**手动回滚方式**：

```java
@Transactional
public void saveWithManualRollback(Employee employee) {
    try {
        employeeMapper.insert(employee);
        int i = 1 / 0;
    } catch (Exception e) {
        log.error("出错了: {}", e.getMessage());
        TransactionAspectSupport.currentTransactionStatus().setRollbackOnly();
        // 手动设置事务为"仅回滚"状态，事务结束时会自动回滚
    }
}
```

---

#### 场景4：rollbackFor设置不当 → 受检异常不回滚

**这是最容易被忽视的坑！**

**原理**：`@Transactional`默认只回滚`RuntimeException`和`Error`，**不回滚受检异常（checked exception）**！

```java
// @Transactional 源码中的默认值
@Transactional(rollbackFor = {RuntimeException.class, Error.class})
```

如果你抛出了一个`IOException`（或其子类），事务**不会回滚**。

**可复现代码**：

```java
// 自定义一个受检异常
public class EmployeeSaveException extends Exception {
    public EmployeeSaveException(String message) {
        super(message);
    }
}

@Service
public class EmployeeService {

    @Autowired
    private EmployeeMapper employeeMapper;

    @Transactional  // ← 默认只回滚RuntimeException和Error
    public void saveWithCheckedException(Employee employee) throws EmployeeSaveException {
        employeeMapper.insert(employee);
        throw new EmployeeSaveException("保存失败");  // ← 受检异常！事务不回滚！
    }

    @Transactional(rollbackFor = Exception.class)  // ← 指定所有Exception都回滚
    public void saveWithCheckedExceptionFixed(Employee employee) throws EmployeeSaveException {
        employeeMapper.insert(employee);
        throw new EmployeeSaveException("保存失败");  // ← 现在会回滚了！
    }
}
```

**验证**：调用`saveWithCheckedException`，检查数据库——数据插入了（没有回滚）！调用`saveWithCheckedExceptionFixed`，检查数据库——数据没有插入（回滚成功）。

**建议**：

```java
// 最佳实践：明确指定rollbackFor = Exception.class
@Transactional(rollbackFor = Exception.class)
public void save(Employee employee) {
    // ...
}
```

这样不管是`RuntimeException`还是受检异常，都会回滚。**除非你明确需要某些受检异常不回滚，否则一律用`rollbackFor = Exception.class`。**

---

#### 场景5：数据库引擎不支持事务 → 事务"假生效"

**原理**：MySQL的MyISAM引擎不支持事务。如果表是MyISAM引擎，即使加了`@Transactional`，也不会生效——每条SQL独立执行且不可回滚。

**可复现代码**：

```sql
-- 创建一个MyISAM表
CREATE TABLE myisam_test (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(20)
) ENGINE=MyISAM;  -- ← 注意这里！
```

```java
@Transactional
public void testMyISAM() {
    jdbcTemplate.update("INSERT INTO myisam_test (name) VALUES (?)", "test1");
    int i = 1 / 0;  // 抛异常
    jdbcTemplate.update("INSERT INTO myisam_test (name) VALUES (?)", "test2");
}
// 结果：test1插入了，即使抛异常也没有回滚——因为MyISAM不支持事务！
```

**验证方法**：

```sql
-- 查询表的引擎
SHOW TABLE STATUS LIKE 'employee';

-- 正确的引擎应该是 InnoDB
-- Engine: InnoDB
```

**复盘**：这个场景不常见（现代项目基本都用InnoDB），但在接手遗留系统时可能遇到。如果你的`@Transactional`怎么都不生效，别忘了检查表的存储引擎。

---

#### 场景6：多线程 → 每个线程有自己独立的事务

**原理**：Spring的事务是通过`ThreadLocal`绑定的，每个线程有自己独立的事务上下文。如果在一个事务方法中启动了新线程，新线程中的操作不在当前事务中。

**可复现代码**：

```java
@Service
public class EmployeeService {

    @Autowired
    private EmployeeMapper employeeMapper;

    @Transactional
    public void saveWithNewThread(Employee e1, Employee e2) {
        employeeMapper.insert(e1);  // 在事务A中

        // 新线程有自己独立的事务（或者根本没有事务）
        new Thread(() -> {
            employeeMapper.insert(e2);  // 不在事务A中！
            // 即使这里抛异常，e1也不会回滚
        }).start();

        int i = 1 / 0;  // 抛异常
        // 结果：e1回滚了（事务A回滚），但e2没有被回滚（它在另一个线程里）
    }
}
```

**验证**：调用此方法后检查数据库——e2被插入了（新线程的事务与主线程独立），e1被回滚了。

**如果需要多线程的事务一致性，解决方案**：
- 使用分布式事务框架（如Seata）
- 使用消息队列的最终一致性方案
- 将多线程操作改为同步操作放在同一个事务中

---

#### 场景7：propagation设置错误 → 事务以非事务方式运行

**原理**：有些传播行为会让方法不在事务中运行，导致没有回滚保护。

**可复现代码**：

```java
@Service
public class EmployeeService {

    @Autowired
    private EmployeeMapper employeeMapper;

    @Transactional
    public void saveParent(Employee e1, Employee e2) {
        employeeMapper.insert(e1);  // 在事务中
        try {
            saveChild(e2);  // 调用NOT_SUPPORTED的方法
        } catch (Exception e) {
            log.error("子方法失败: {}", e.getMessage());
        }
    }

    @Transactional(propagation = Propagation.NOT_SUPPORTED)
    // ↑ NOT_SUPPORTED：以非事务方式运行，挂起当前事务
    public void saveChild(Employee employee) {
        employeeMapper.insert(employee);  // 不在事务中！
        int i = 1 / 0;  // 抛异常
    }
}

// 结果：
// 1. e2被插入（在非事务中执行，异常不会导致回滚）
// 2. e1也被插入（因为catch了异常，父事务正常提交）
```

**其他危险的传播行为配置**：

```java
@Transactional(propagation = Propagation.NEVER)
// ↑ 如果当前有事务就抛异常，完全不用事务

@Transactional(propagation = Propagation.SUPPORTS)
// ↑ 如果当前没有事务（比如直接调用此方法），就以非事务方式运行
//   此时数据库操作没有回滚保护
```

### 17.4.3 事务失效场景速查总结

| # | 场景 | 根因 | 关键词 |
|---|------|------|--------|
| 1 | 非public方法 | Spring AOP只代理public方法 | `protected`/`private`/默认 |
| 2 | 同类内部调用 | `this.xxx()`不走代理 | AOP代理机制 |
| 3 | 异常被catch吃掉 | Spring感知不到异常 | try-catch不抛出 |
| 4 | rollbackFor不对 | 默认只回滚运行时异常 | 受检异常 |
| 5 | 数据库引擎不支持 | MyISAM无事务 | 存储引擎 |
| 6 | 多线程 | ThreadLocal隔离 | 线程独立事务 |
| 7 | propagation不对 | NOT_SUPPORTED/NEVER等 | 传播行为 |

### 17.4.4 编程式事务 — TransactionTemplate

当你需要更精细的事务控制时（如在循环中每次迭代独立事务），可以使用编程式事务：

```java
@Service
public class EmployeeService {

    @Autowired
    private TransactionTemplate transactionTemplate;
    @Autowired
    private EmployeeMapper employeeMapper;

    public void batchSave(List<Employee> employees) {
        for (Employee emp : employees) {
            transactionTemplate.execute(status -> {
                try {
                    employeeMapper.insert(emp);
                    return null;  // 成功
                } catch (Exception e) {
                    status.setRollbackOnly();  // 标记回滚
                    log.error("保存员工失败: {} -> {}", emp.getName(), e.getMessage());
                    return null;  // 不影响其他员工的保存
                }
            });
        }
    }
}
```

**编程式事务 vs 声明式事务**：
- 声明式（`@Transactional`）：代码简洁，适合大多数场景
- 编程式（`TransactionTemplate`）：精细控制，适合复杂场景（如循环中每项独立事务、动态决定是否回滚）

### 17.4.5 事务 + 异常的正确写法模板

```java
// ✅ 最佳实践模板
@Service
@Slf4j
public class OrderService {

    @Autowired
    private OrderMapper orderMapper;
    @Autowired
    private InventoryMapper inventoryMapper;

    @Transactional(rollbackFor = Exception.class)  // 1. 指定rollbackFor
    public void createOrder(OrderDTO dto) {
        // 2. 业务校验在最前面（不通过直接抛异常）
        if (dto.getItems() == null || dto.getItems().isEmpty()) {
            throw new BusinessException(ResultCode.PARAM_ERROR, "订单明细不能为空");
        }

        // 3. 数据库操作
        orderMapper.insert(dto.toOrder());           // 插入订单主表

        for (OrderItemDTO item : dto.getItems()) {
            int rows = inventoryMapper.deductStock(
                    item.getProductId(), item.getQuantity());
            if (rows == 0) {
                // 4. 业务逻辑不满足 → 抛异常触发回滚
                throw new BusinessException(ResultCode.BUSINESS_ERROR,
                        "商品[" + item.getProductName() + "]库存不足");
            }
            orderMapper.insertItem(item.toOrderItem());
        }

        // 5. 如果所有操作都成功 → 事务自动提交
        //    如果任何一步失败 → 事务自动回滚
    }
}
```

---

## 17.5 多数据源

### 17.5.1 场景：读写分离

大型系统中常见的架构：主库（Master）处理写操作，从库（Slave）处理读操作。

```
写请求 ──→ 主库（master）
读请求 ──→ 从库（slave）

主库的数据通过MySQL主从复制同步到从库
```

### 17.5.2 双数据源配置

**application.yml**：

```yaml
spring:
  datasource:
    master:
      url: jdbc:mysql://192.168.1.100:3306/ems?useSSL=false&serverTimezone=Asia/Shanghai
      username: root
      password: root
      driver-class-name: com.mysql.cj.jdbc.Driver
    slave:
      url: jdbc:mysql://192.168.1.101:3306/ems?useSSL=false&serverTimezone=Asia/Shanghai
      username: read_only
      password: read_only
      driver-class-name: com.mysql.cj.jdbc.Driver
```

**主数据源配置类**：

```java
package com.example.springbootdemo.config;

import com.zaxxer.hikari.HikariDataSource;
import org.apache.ibatis.session.SqlSessionFactory;
import org.mybatis.spring.SqlSessionFactoryBean;
import org.mybatis.spring.annotation.MapperScan;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.boot.jdbc.DataSourceBuilder;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Primary;
import org.springframework.core.io.support.PathMatchingResourcePatternResolver;
import org.springframework.jdbc.datasource.DataSourceTransactionManager;

import javax.sql.DataSource;

@Configuration
@MapperScan(
    basePackages = "com.example.springbootdemo.mapper.master",
    sqlSessionFactoryRef = "masterSqlSessionFactory"
)
public class MasterDataSourceConfig {

    @Bean("masterDataSource")
    @Primary  // ← 标记为主数据源（默认使用）
    @ConfigurationProperties(prefix = "spring.datasource.master")
    public DataSource masterDataSource() {
        return DataSourceBuilder.create().type(HikariDataSource.class).build();
    }

    @Bean("masterSqlSessionFactory")
    @Primary
    public SqlSessionFactory masterSqlSessionFactory(
            @Qualifier("masterDataSource") DataSource dataSource) throws Exception {
        SqlSessionFactoryBean bean = new SqlSessionFactoryBean();
        bean.setDataSource(dataSource);
        bean.setMapperLocations(new PathMatchingResourcePatternResolver()
                .getResources("classpath:mapper/master/**/*.xml"));
        return bean.getObject();
    }

    @Bean("masterTransactionManager")
    @Primary
    public DataSourceTransactionManager masterTransactionManager(
            @Qualifier("masterDataSource") DataSource dataSource) {
        return new DataSourceTransactionManager(dataSource);
    }
}
```

**从数据源配置类**（结构相同，只是包路径和前缀不同）：

```java
@Configuration
@MapperScan(
    basePackages = "com.example.springbootdemo.mapper.slave",
    sqlSessionFactoryRef = "slaveSqlSessionFactory"
)
public class SlaveDataSourceConfig {

    @Bean("slaveDataSource")
    @ConfigurationProperties(prefix = "spring.datasource.slave")
    public DataSource slaveDataSource() {
        return DataSourceBuilder.create().type(HikariDataSource.class).build();
    }

    @Bean("slaveSqlSessionFactory")
    public SqlSessionFactory slaveSqlSessionFactory(
            @Qualifier("slaveDataSource") DataSource dataSource) throws Exception {
        SqlSessionFactoryBean bean = new SqlSessionFactoryBean();
        bean.setDataSource(dataSource);
        bean.setMapperLocations(new PathMatchingResourcePatternResolver()
                .getResources("classpath:mapper/slave/**/*.xml"));
        return bean.getObject();
    }

    @Bean("slaveTransactionManager")
    public DataSourceTransactionManager slaveTransactionManager(
            @Qualifier("slaveDataSource") DataSource dataSource) {
        return new DataSourceTransactionManager(dataSource);
    }
}
```

**项目包结构调整**：

```
mapper/
├── master/
│   └── EmployeeMapper.java    ← 操作主库（写）
└── slave/
    └── EmployeeReadMapper.java ← 操作从库（读）
```

> 🚨 **坑点：@Transactional只能管一个数据源的事务**
> 
> ```java
> @Transactional("masterTransactionManager")  // 这个事务只管理主库
> public void doSomething() {
>     masterMapper.insert(...);   // 在事务中
>     slaveMapper.select(...);    // 不在同一个事务中！
> }
> ```
> 
> 如果你需要跨多个数据源的事务一致性，就需要**分布式事务**方案（Seata、RocketMQ事务消息等）。这在中小型项目中通常不推荐直接上分布式事务——复杂度远高于引入它的收益。

### 17.5.3 AbstractRoutingDataSource 动态路由

上面的静态双数据源方案需要手动选择用哪个Mapper。更高级的做法是使用`AbstractRoutingDataSource`，在运行时根据上下文（如读写类型）动态切换数据源。

```java
public class DynamicDataSource extends AbstractRoutingDataSource {
    @Override
    protected Object determineCurrentLookupKey() {
        return DataSourceContextHolder.getDataSourceType();
        // 返回 "master" 或 "slave"
    }
}
```

配合AOP切面，在Service方法上标注`@ReadOnly`注解时自动切到从库——这在Spring Boot中是比较成熟的方案，但已超出本章范围。感兴趣的读者可以搜索"Spring Boot 动态数据源"了解完整实现。

---

## 17.6 Flyway数据库版本管理

### 17.6.1 为什么需要数据库版本管理？

在团队协作中，数据库变更是个痛点：

```
开发者A: 在我的库里加了一个字段 age
开发者B: 在我的库里加了一个字段 salary
测试环境: 两个人脚本都没执行...
生产环境: 执行了谁的脚本？忘记了...
```

**Flyway解决的就是这个问题**：把数据库的变更用SQL脚本管理起来，像Git管理代码一样管理数据库结构的变化。

### 17.6.2 引入Flyway

```xml
<dependency>
    <groupId>org.flywaydb</groupId>
    <artifactId>flyway-core</artifactId>
</dependency>
<!-- MySQL需要额外引入（Spring Boot 3.x） -->
<dependency>
    <groupId>org.flywaydb</groupId>
    <artifactId>flyway-mysql</artifactId>
</dependency>
```

### 17.6.3 配置

```yaml
spring:
  flyway:
    enabled: true
    locations: classpath:db/migration       # SQL脚本存放位置
    baseline-on-migrate: true               # 已有表的数据库首次使用Flyway时设为true
    baseline-version: 1                     # 基线版本
```

### 17.6.4 SQL脚本命名规范

Flyway的SQL脚本有严格的命名规范：

```
V<版本号>__<描述>.sql

示例：
V1__init_schema.sql
V2__add_age_column.sql
V3__create_department_table.sql
V4__update_salary_default.sql
```

注意：版本号后的分隔符是**两个下划线**（`__`），不是一个！

在`src/main/resources/db/migration/`下创建：

**V1__init_schema.sql**：

```sql
CREATE TABLE employee (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(20) NOT NULL,
    department VARCHAR(50) NOT NULL,
    salary DECIMAL(10,2) NOT NULL,
    email VARCHAR(100),
    hire_date DATE,
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

**V2__add_age_column.sql**：

```sql
ALTER TABLE employee ADD COLUMN age INT AFTER name;
```

**V3__add_index.sql**：

```sql
CREATE INDEX idx_department ON employee(department);
CREATE INDEX idx_email ON employee(email);
```

### 17.6.5 执行机制

Flyway在应用启动时自动执行：

1. 检查`flyway_schema_history`表（Flyway的元数据表）
2. 对比该表中已执行的脚本和`db/migration/`目录下的脚本
3. 执行未执行过的脚本（按版本号升序）
4. 每执行一个脚本，在`flyway_schema_history`中记录一条

```
应用启动 →
  V1 已执行 ✓（跳过）
  V2 已执行 ✓（跳过）
  V3 未执行 → 执行 V3__add_index.sql → 记录到 flyway_schema_history
  V4 未执行 → 执行 V4__xxx.sql → 记录到 flyway_schema_history
  → 启动完成
```

> 🚨 **致命坑点：已执行的Flyway脚本绝对不能修改！**
> 
> Flyway通过脚本文件的**checksum（校验和）**来判断脚本是否被修改过。如果修改了已执行的脚本，Flyway会检测到checksum不匹配，**启动直接失败**：
> 
> ```
> Migration checksum mismatch for migration version 2
> → Expected: 123456789 but was: 987654321
> ```
> 
> **正确做法**：永远创建新的版本脚本来修改数据库结构。数据库演进应该是"追加"而非"修改"历史。

> 🚨 **坑点：生产环境Flyway migrate失败会阻止启动**
> 
> 这是一个保护机制：如果数据库脚本执行失败（比如SQL语法错误），Flyway会阻止应用启动，避免代码与数据库结构不一致导致的运行时错误。**这是好事**——但意味着你的Flyway脚本必须经过充分测试。

---

## EMS v5：Spring Boot版员工管理系统

现在，让我们将本章和前两章学到的所有知识整合起来，完成**EMS v5：一个完整的三层架构Spring Boot后端API**。

### v5 项目结构

```
src/main/java/com/example/ems/
├── EmsApplication.java                  # 启动类
├── common/
│   ├── Result.java                      # 统一返回格式（第16章）
│   ├── ResultCode.java                  # 状态码枚举（第16章）
│   └── exception/
│       ├── BusinessException.java       # 业务异常（第16章）
│       └── GlobalExceptionHandler.java  # 全局异常处理（第16章）
├── config/
│   └── WebMvcConfig.java               # CORS + 拦截器配置（第16章）
├── entity/
│   └── Employee.java                   # 实体类
├── dto/
│   ├── EmployeeSaveDTO.java            # 新增员工DTO
│   ├── EmployeeUpdateDTO.java          # 更新员工DTO
│   └── EmployeeQueryDTO.java           # 查询条件DTO
├── mapper/
│   └── EmployeeMapper.java             # MyBatis Mapper接口
├── service/
│   ├── EmployeeService.java            # Service接口
│   └── impl/
│       └── EmployeeServiceImpl.java    # Service实现
└── controller/
    └── EmployeeController.java         # RESTful Controller

src/main/resources/
├── application.yml
├── db/migration/
│   └── V1__init_employee.sql           # Flyway初始化脚本
└── mapper/
    └── EmployeeMapper.xml
```

### 基础组件（复用第16章的通用代码）

`Result.java`、`ResultCode.java`、`BusinessException.java`、`GlobalExceptionHandler.java`、`WebMvcConfig.java` 均沿用第16章的设计，放在`common/`包下。此处不再重复列出。

### application.yml

```yaml
server:
  port: 8080

spring:
  application:
    name: ems-v5
  datasource:
    url: jdbc:mysql://localhost:3306/ems?useSSL=false&serverTimezone=Asia/Shanghai&characterEncoding=utf8mb4
    username: root
    password: root
    driver-class-name: com.mysql.cj.jdbc.Driver
    hikari:
      maximum-pool-size: 20
      minimum-idle: 5
      connection-timeout: 3000
  flyway:
    enabled: true
    locations: classpath:db/migration
    baseline-on-migrate: true

mybatis:
  mapper-locations: classpath:mapper/**/*.xml
  type-aliases-package: com.example.ems.entity
  configuration:
    map-underscore-to-camel-case: true
    log-impl: org.apache.ibatis.logging.stdout.StdOutImpl
```

### Flyway初始化脚本

`src/main/resources/db/migration/V1__init_employee.sql`：

```sql
CREATE TABLE IF NOT EXISTS employee (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(20) NOT NULL,
    age INT NOT NULL,
    department VARCHAR(50) NOT NULL,
    salary DECIMAL(10,2) NOT NULL,
    email VARCHAR(100),
    hire_date DATE,
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_department (department),
    INDEX idx_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO employee (name, age, department, salary, email, hire_date) VALUES
('张三', 28, '技术部', 18000.00, 'zhangsan@ems.com', '2023-03-15'),
('李四', 32, '技术部', 20000.00, 'lisi@ems.com', '2022-07-01'),
('王五', 25, '市场部', 12000.00, 'wangwu@ems.com', '2024-01-10'),
('赵六', 35, '人事部', 18000.00, 'zhaoliu@ems.com', '2021-05-20'),
('钱七', 29, '技术部', 16000.00, 'qianqi@ems.com', '2023-09-01');
```

### Entity

```java
package com.example.ems.entity;

import lombok.Data;
import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;

@Data
public class Employee {
    private Long id;
    private String name;
    private Integer age;
    private String department;
    private BigDecimal salary;
    private String email;
    private LocalDate hireDate;
    private LocalDateTime createTime;
    private LocalDateTime updateTime;
}
```

### DTO

```java
package com.example.ems.dto;

import jakarta.validation.constraints.*;
import lombok.Data;
import java.math.BigDecimal;
import java.time.LocalDate;

@Data
public class EmployeeSaveDTO {
    @NotBlank(message = "姓名不能为空")
    @Size(min = 2, max = 20, message = "姓名长度2-20")
    private String name;

    @NotNull(message = "年龄不能为空")
    @Min(value = 18, message = "年龄不能小于18岁")
    @Max(value = 65, message = "年龄不能大于65岁")
    private Integer age;

    @NotBlank(message = "部门不能为空")
    private String department;

    @NotNull(message = "薪资不能为空")
    @Positive(message = "薪资必须大于0")
    private BigDecimal salary;

    @Email(message = "邮箱格式不正确")
    private String email;

    @Past(message = "入职日期必须是过去日期")
    private LocalDate hireDate;
}
```

```java
package com.example.ems.dto;

import lombok.Data;
import java.math.BigDecimal;

@Data
public class EmployeeQueryDTO {
    private String name;
    private String department;
    private BigDecimal minSalary;
    private BigDecimal maxSalary;
}
```

### Mapper

```java
package com.example.ems.mapper;

import com.example.ems.entity.Employee;
import org.apache.ibatis.annotations.Param;
import java.util.List;

public interface EmployeeMapper {
    Employee selectById(@Param("id") Long id);
    List<Employee> selectAll();
    List<Employee> selectByCondition(@Param("name") String name,
                                     @Param("department") String department,
                                     @Param("minSalary") BigDecimal minSalary,
                                     @Param("maxSalary") BigDecimal maxSalary);
    int insert(Employee employee);
    int update(Employee employee);
    int deleteById(@Param("id") Long id);
}
```

### Mapper XML

`src/main/resources/mapper/EmployeeMapper.xml`：

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE mapper PUBLIC "-//mybatis.org//DTD Mapper 3.0//EN"
        "http://mybatis.org/dtd/mybatis-3-mapper.dtd">
<mapper namespace="com.example.ems.mapper.EmployeeMapper">

    <sql id="baseColumns">
        id, name, age, department, salary, email, hire_date, create_time, update_time
    </sql>

    <select id="selectById" resultType="Employee">
        SELECT <include refid="baseColumns"/>
        FROM employee WHERE id = #{id}
    </select>

    <select id="selectAll" resultType="Employee">
        SELECT <include refid="baseColumns"/>
        FROM employee ORDER BY id DESC
    </select>

    <select id="selectByCondition" resultType="Employee">
        SELECT <include refid="baseColumns"/>
        FROM employee
        <where>
            <if test="name != null and name != ''">
                AND name LIKE CONCAT('%', #{name}, '%')
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
        ORDER BY id DESC
    </select>

    <insert id="insert" useGeneratedKeys="true" keyProperty="id">
        INSERT INTO employee (name, age, department, salary, email, hire_date)
        VALUES (#{name}, #{age}, #{department}, #{salary}, #{email}, #{hireDate})
    </insert>

    <update id="update">
        UPDATE employee
        <set>
            <if test="name != null and name != ''">name = #{name},</if>
            <if test="age != null">age = #{age},</if>
            <if test="department != null">department = #{department},</if>
            <if test="salary != null">salary = #{salary},</if>
            <if test="email != null">email = #{email},</if>
            <if test="hireDate != null">hire_date = #{hireDate},</if>
            update_time = NOW()
        </set>
        WHERE id = #{id}
    </update>

    <delete id="deleteById">
        DELETE FROM employee WHERE id = #{id}
    </delete>

</mapper>
```

### Service

```java
package com.example.ems.service;

import com.example.ems.dto.EmployeeQueryDTO;
import com.example.ems.dto.EmployeeSaveDTO;
import com.example.ems.entity.Employee;
import java.util.List;

public interface EmployeeService {
    Employee findById(Long id);
    List<Employee> findAll();
    List<Employee> findByCondition(EmployeeQueryDTO query);
    Employee save(EmployeeSaveDTO dto);
    Employee update(Long id, EmployeeSaveDTO dto);
    void deleteById(Long id);
}
```

```java
package com.example.ems.service.impl;

import com.example.ems.common.ResultCode;
import com.example.ems.common.exception.BusinessException;
import com.example.ems.dto.EmployeeQueryDTO;
import com.example.ems.dto.EmployeeSaveDTO;
import com.example.ems.entity.Employee;
import com.example.ems.mapper.EmployeeMapper;
import com.example.ems.service.EmployeeService;
import lombok.RequiredArgsConstructor;
import org.springframework.beans.BeanUtils;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
@RequiredArgsConstructor
public class EmployeeServiceImpl implements EmployeeService {

    private final EmployeeMapper employeeMapper;

    @Override
    public Employee findById(Long id) {
        Employee employee = employeeMapper.selectById(id);
        if (employee == null) {
            throw new BusinessException(ResultCode.USER_NOT_FOUND, "员工不存在，ID: " + id);
        }
        return employee;
    }

    @Override
    public List<Employee> findAll() {
        return employeeMapper.selectAll();
    }

    @Override
    public List<Employee> findByCondition(EmployeeQueryDTO query) {
        return employeeMapper.selectByCondition(
                query.getName(), query.getDepartment(),
                query.getMinSalary(), query.getMaxSalary());
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public Employee save(EmployeeSaveDTO dto) {
        Employee employee = new Employee();
        BeanUtils.copyProperties(dto, employee);
        employeeMapper.insert(employee);
        return findById(employee.getId());
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public Employee update(Long id, EmployeeSaveDTO dto) {
        findById(id);
        Employee employee = new Employee();
        BeanUtils.copyProperties(dto, employee);
        employee.setId(id);
        employeeMapper.update(employee);
        return findById(id);
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public void deleteById(Long id) {
        findById(id);
        employeeMapper.deleteById(id);
    }
}
```

### Controller

```java
package com.example.ems.controller;

import com.example.ems.common.Result;
import com.example.ems.dto.EmployeeQueryDTO;
import com.example.ems.dto.EmployeeSaveDTO;
import com.example.ems.entity.Employee;
import com.example.ems.service.EmployeeService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/employees")
@RequiredArgsConstructor
public class EmployeeController {

    private final EmployeeService employeeService;

    @GetMapping("/{id}")
    public Result<Employee> getById(@PathVariable Long id) {
        return Result.success(employeeService.findById(id));
    }

    @GetMapping
    public Result<List<Employee>> list(EmployeeQueryDTO query) {
        if (query.getName() != null || query.getDepartment() != null
                || query.getMinSalary() != null || query.getMaxSalary() != null) {
            return Result.success(employeeService.findByCondition(query));
        }
        return Result.success(employeeService.findAll());
    }

    @PostMapping
    public Result<Employee> create(@RequestBody @Valid EmployeeSaveDTO dto) {
        return Result.success(employeeService.save(dto));
    }

    @PutMapping("/{id}")
    public Result<Employee> update(@PathVariable Long id, @RequestBody @Valid EmployeeSaveDTO dto) {
        return Result.success(employeeService.update(id, dto));
    }

    @DeleteMapping("/{id}")
    public Result<Void> delete(@PathVariable Long id) {
        employeeService.deleteById(id);
        return Result.success();
    }
}
```

### 启动类

```java
package com.example.ems;

import org.mybatis.spring.annotation.MapperScan;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
@MapperScan("com.example.ems.mapper")
public class EmsApplication {
    public static void main(String[] args) {
        SpringApplication.run(EmsApplication.class, args);
    }
}
```

### API接口清单

| 方法 | URL | 说明 |
|------|-----|------|
| `GET` | `/api/employees/{id}` | 查询单个员工 |
| `GET` | `/api/employees` | 查询全部 / 条件查询（?name=&department=&minSalary=&maxSalary=） |
| `POST` | `/api/employees` | 新增员工（Body: JSON，自动校验） |
| `PUT` | `/api/employees/{id}` | 更新员工（Body: JSON，自动校验） |
| `DELETE` | `/api/employees/{id}` | 删除员工 |
| `GET` | `/api/employees/1` | 示例：查询ID为1的员工 |

### EMS版本演进回顾

| 版本 | 章节 | 技术栈 | 核心能力 |
|------|------|--------|---------|
| EMS v1 | 第7章 | Java SE + List内存存储 | 命令行CRUD |
| EMS v2 | 第9章 | JDBC + Druid + MySQL | 数据持久化到数据库 |
| EMS v3 | 第12章 | Spring IoC/AOP/MVC | 分层架构、IoC管理依赖 |
| EMS v4 | 第13-14章 | MyBatis/JPA | ORM框架、SQL/JPA双方案 |
| **EMS v5** | **第15-17章** | **Spring Boot + MyBatis + RESTful** | **自动配置、统一返回格式、全局异常处理、参数校验、事务管理** |
| EMS v6 | 第20-22章 | Vue 3 + Element Plus | 前后端分离、前端管理界面 |
| EMS v7 | 第23-24章 | Spring Security + JWT | 认证授权、Token管理 |
| EMS v8 | 第25章 | Redis | 缓存优化 |
| EMS v9 | 第26-27章 | Docker + Nginx + Nacos | 容器化部署、微服务 |

---

## 本章小结

1. **MyBatis整合**：`mybatis-spring-boot-starter` + `application.yml`配置 + `@MapperScan`一站式扫描。`mapper-locations`路径用`classpath:mapper/**/*.xml`。

2. **MyBatis Plus整合**：只需切换Starter依赖，继承`BaseMapper<T>`即可获得零SQL的CRUD能力。`LambdaQueryWrapper`利用方法引用防字段名写错。

3. **JPA整合**：`spring-boot-starter-data-jpa` + `ddl-auto`配置。**生产环境绝对不能用`update`或`create`**，用`validate`或`none`。

4. **事务管理7种失效场景**：
   - 场景1：非public方法（AOP只代理public）
   - 场景2：同类内部调用（`this.xxx()`不走代理）
   - 场景3：异常被catch吃掉（Spring感知不到异常）
   - 场景4：rollbackFor设置不对（默认只回滚RuntimeException，受检异常不回滚！）
   - 场景5：数据库引擎不支持（MyISAM无事务）
   - 场景6：多线程（ThreadLocal隔离，各线程独立事务）
   - 场景7：propagation设置不当（NOT_SUPPORTED等非事务传播）

5. **多数据源**：读写分离场景下需配置多个DataSource + SqlSessionFactory + MapperScan。`@Transactional`只能管一个数据源的事务，跨数据源需分布式事务。

6. **Flyway**：SQL版本管理工具，脚本命名规范`V<版本号>__<描述>.sql`。已执行的脚本绝对不能修改！

7. **EMS v5**：整合了第15-17章所有知识——Spring Boot自动配置 + MyBatis数据层 + 统一返回格式Result + 全局异常处理 + 参数校验 + 事务管理，构成一个完整、健壮的三层架构后端API。

> **下一章预告**：第18章将学习配置管理与多环境——`application-{profile}.yml`多环境切换、`@ConfigurationProperties`类型安全配置绑定、配置优先级、Jasypt敏感信息加密。告别"改配置要重新打包"的烦恼。

---

## 思考题

1. 以下代码中的`@Transactional`是否会生效？如果不会，为什么？如何修复？
   ```java
   @Service
   public class EmployeeService {
       @Autowired
       private EmployeeMapper mapper;
       
       protected void internalSave(Employee e) {
           mapper.insert(e);
       }
       
       @Transactional(rollbackFor = Exception.class)
       protected void transactionalSave(Employee e) {
           mapper.insert(e);
           int i = 1 / 0;
       }
   }
   ```

2. 以下代码执行后，数据库里会有几条员工记录（假设所有员工都是new Employee()）？为什么？
   ```java
   @Transactional
   public void batchProcess() {
       try {
           mapper.insert(new Employee("A"));
           throw new RuntimeException("error");
       } catch (RuntimeException e) {
           log.error("捕获异常: {}", e.getMessage());
       }
       mapper.insert(new Employee("B"));
   }
   ```

3. `@Transactional`的`rollbackFor`默认是什么？如果你的方法抛出`SQLException`（一个受检异常），事务会回滚吗？请写出正确的配置。

4. 设计一个场景：两个Service方法都需要事务，其中一个是主业务（需要回滚），另一个是日志记录（无论主业务成功与否都要记录，且日志记录不能被主业务回滚影响）。请用`@Transactional`的`propagation`属性实现这个场景。

5. 在EMS v5的基础上增加一个功能：批量导入员工（Excel数据通过API传入JSON数组）。要求：
   - 参数校验仍然生效
   - 每个员工的导入失败不影响其他员工
   - 返回每个员工的导入结果（成功/失败+原因）
   请给出Service方法的核心设计（使用编程式事务`TransactionTemplate`）。

6. 你的项目需要在测试环境和生产环境使用不同的Flyway行为：测试环境自动执行所有脚本（包括可能破坏数据的），生产环境只验证脚本是否都已执行且不执行新的破坏性脚本。如何通过Spring Boot的多环境配置实现这个需求？