# 第14章：Spring Data JPA — 自动化的ORM

## 本章目标

学完本章你将能够：

- 理解ORM思想与JPA规范的本质，清晰区分JPA/Hibernate/Spring Data JPA三层关系
- 掌握JPA七大核心注解（`@Entity`/`@Table`/`@Id`/`@GeneratedValue`/`@Column`/`@Enumerated`/`@Transient`）及关联注解
- 熟练使用`JpaRepository`内置方法和自定义方法命名查询（findBy/And/Or/Like/OrderBy等）
- 运用`@Query`注解编写JPQL和原生SQL查询
- 实现分页查询（Pageable/Page），理解页码从0开始的关键细节
- 解决JPA高级陷阱：N+1查询问题、双向关联无限递归、OSIV连接耗尽、ddl-auto生产禁用
- **完成EMS v4：用MyBatis和JPA两种方式实现同一个员工CRUD系统**，亲手体验两种持久化哲学的差异

---

## 14.1 ORM与JPA概述

### 14.1.1 什么是ORM？

在第13章，我们花了大量篇幅学习MyBatis。MyBatis的核心思想是：**你写SQL，我帮你执行和映射**——SQL的控制权始终在你手中。

JPA走的是一条完全不同的路。它的核心思想是：**你把对象交给我，SQL由我自动生成**——你几乎不需要写SQL。

这种思想叫做**ORM（Object-Relational Mapping，对象关系映射）**——

```
┌──────────────────┐        ORM        ┌──────────────────┐
│   Java对象        │ ←──────────────→ │   数据库表         │
│   Employee类      │   自动双向映射     │   employee表       │
├──────────────────┤                  ├──────────────────┤
│   id: Long       │ ←──────────────→ │   id: BIGINT     │
│   name: String   │ ←──────────────→ │   name: VARCHAR  │
│   age: Integer   │ ←──────────────→ │   age: INT       │
│   department     │ ←──────────────→ │   department_id  │
│   : Department   │  (外键 → 对象)   │   : BIGINT(FK)   │
└──────────────────┘                  └──────────────────┘
```

在这个模型中：
- **每一行数据** 自动变成一个Java对象
- **每一列** 自动映射为对象的一个属性
- **外键关系** 自动变成对象之间的引用（`department`属性指向另一个`Department`对象）
- **INSERT/UPDATE/DELETE** 由框架根据对象状态的变化自动生成并执行

### 14.1.2 JPA vs Hibernate vs Spring Data JPA

这三者经常被混为一谈，但它们有清晰的层次关系：

```
┌──────────────────────────────────────────┐
│          Spring Data JPA                 │  ← 再封装：Repository接口、方法命名查询
│  "你只定义接口，我帮你实现"              │
├──────────────────────────────────────────┤
│              Hibernate                   │  ← JPA的具体实现：生成SQL、管理实体状态
│  "我负责把对象变成SQL，管理缓存和事务"    │
├──────────────────────────────────────────┤
│          JPA (Jakarta Persistence)       │  ← 规范：定义注解(@Entity等)和API(EntityManager)
│  "我只定规则，不写代码"                  │
└──────────────────────────────────────────┘
```

| 层次 | 是什么 | 谁开发的 | 你能用它做什么 |
|------|--------|---------|--------------|
| **JPA** | 一套接口规范（jakarta.persistence.*） | Oracle（原Sun）定义的Java EE标准 | 定义实体类、标注映射关系、使用EntityManager操作 |
| **Hibernate** | JPA规范的一个实现 | Red Hat | 实际执行ORM：生成SQL、管理缓存、脏检查、延迟加载 |
| **Spring Data JPA** | 对JPA的进一步封装 | Spring团队 | `JpaRepository`接口：你只需定义接口方法名，它自动生成实现 |

**一个类比**：
- JPA = USB接口规范（定义了形状、协议、电压标准）
- Hibernate = 某厂商生产的USB数据线（实现了规范）
- Spring Data JPA = 你电脑上的"即插即用"驱动（你插上线，它自动识别设备—你几乎不用管底层细节）

> ⚠️ **重要提醒**：Spring Boot 3.x 基于 Jakarta EE 9+，所有JPA注解的包名从`javax.persistence.*`迁移到了 **`jakarta.persistence.*`**！如果你看到老教程用`javax.persistence.*`，在新项目中必须改成`jakarta.persistence.*`，否则编译错误。

### 14.1.3 MyBatis vs JPA 选型指南

这是很多初学者最困惑的问题：我到底该学哪个？该用哪个？

答案是：**都学，根据场景选。** 下表从8个维度进行全方位对比：

| 维度 | MyBatis | Spring Data JPA |
|------|---------|-----------------|
| **SQL控制力** | ⭐⭐⭐⭐⭐ 完全掌控，手写SQL | ⭐⭐ SQL自动生成，复杂查询需JPQL或原生SQL |
| **开发效率** | ⭐⭐⭐ 需编写XML和维护SQL | ⭐⭐⭐⭐⭐ 简单CRUD零SQL，方法命名即可查询 |
| **复杂查询** | ⭐⭐⭐⭐⭐ 动态SQL标签体系强大 | ⭐⭐ JPQL能力有限，复杂查询需回退原生SQL |
| **学习曲线** | ⭐⭐⭐⭐ 低：本质就是写SQL | ⭐⭐ 中高：需理解ORM状态管理、懒加载、缓存 |
| **数据库迁移** | ⭐ 换数据库需改SQL方言 | ⭐⭐⭐⭐⭐ 只需改dialect配置，JPA自动适配 |
| **SQL调优** | ⭐⭐⭐⭐⭐ 直接改SQL，DBA友好 | ⭐⭐ 需分析Hibernate生成的SQL，黑盒感强 |
| **适用场景** | 复杂报表、多表关联、BI系统、遗留数据库 | 标准CRUD管理后台、微服务快速开发、原型验证 |
| **团队适配** | SQL能力强的团队 | 面向对象思维强的团队 |

**一句话总结**：
- 如果你需要**精细控制每一条SQL**（复杂报表、大数据量优化、遗留系统对接）→ **MyBatis**
- 如果你的业务以**标准CRUD为主**，追求**开发速度**（管理后台、微服务、快速原型）→ **JPA**
- 两者可以**共存**：核心业务用MyBatis精细控制SQL，后台管理用JPA快速开发

> **本章和第13章学完后，你将成为"双修"开发者——这才是企业在招聘时真正看重的技能组合。**

---

## 14.2 JPA核心注解

让我们从零开始，用JPA定义我们的Employee实体。每一步都对应一个注解，理解每个注解的含义和陷阱。

### 14.2.1 @Entity + @Table：标记实体与表映射

```java
package com.example.entity;

import jakarta.persistence.*;
import java.time.LocalDate;

@Entity
@Table(name = "employee")
public class Employee {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "name", nullable = false, length = 50)
    private String name;

    private Integer age;

    @Column(name = "department")
    private String department;

    private Double salary;

    @Column(unique = true)
    private String email;

    @Column(name = "hire_date")
    private LocalDate hireDate;

    // 构造方法、getter/setter（用Lombok @Data可省略）
    public Employee() {}

    // getter & setter 省略...
}
```

逐个解析：

- `@Entity`：告诉JPA"这是一个实体类，要映射到数据库表"。**必须有无参构造方法**（JPA通过反射创建对象时需要）。
- `@Table(name = "employee")`：指定映射的表名。不写则默认类名小写（`Employee` → `employee`表）。
- `@Id`：主键。**必须有**，否则JPA不知道如何唯一标识一行。
- `@GeneratedValue`：主键生成策略（下面详解）。
- `@Column`：精细控制列映射。常用属性：`name`（列名）、`nullable`（是否可为空）、`length`（长度，默认255）、`unique`（是否唯一）。

### 14.2.2 @Id + @GeneratedValue：主键生成策略

这是JPA中**最容易踩坑的配置之一**。

```java
@Id
@GeneratedValue(strategy = GenerationType.IDENTITY)
private Long id;
```

`@GeneratedValue`有四种策略：

| 策略 | 说明 | MySQL表现 | 适用场景 |
|------|------|-----------|---------|
| `IDENTITY` | 使用数据库自增列 | `AUTO_INCREMENT` | **MySQL推荐** |
| `SEQUENCE` | 使用数据库序列 | MySQL不支持（需单独建序列表） | Oracle/PostgreSQL |
| `TABLE` | 用一张独立的表模拟序列 | 创建`hibernate_sequence`表 | 老旧数据库（性能差） |
| `AUTO` | JPA自动选择（**默认值**） | **MySQL中默认选TABLE！** | 不推荐使用默认 |

> 🚨 **坑点：`@GeneratedValue`默认策略是AUTO → MySQL中变成TABLE → 额外建hibernate_sequence表！**
> - 当你不写`strategy`或写`strategy = GenerationType.AUTO`时，JPA（Hibernate）会"智能"选择策略
> - 在MySQL中，Hibernate的"智能"选择是**TABLE策略**——因为MySQL原生没有SEQUENCE对象
> - TABLE策略会**自动创建一张`hibernate_sequence`表**来维护全局主键计数器
> - 后果：所有表的ID都从这张表获取，成为性能瓶颈 + 数据库多一张莫名其妙的新表
> - **解决**：**永远明确写 `@GeneratedValue(strategy = GenerationType.IDENTITY)`**

### 14.2.3 @Column：字段映射精细化

```java
@Column(name = "employee_name",      // 数据库列名（和Java属性名不同时指定）
        nullable = false,            // NOT NULL约束
        length = 100,                // 字符串长度
        unique = true,               // UNIQUE约束
        precision = 10, scale = 2)   // 数值精度和小数位（DECIMAL(10,2)）
private String name;
```

常用`@Column`属性速查：

| 属性 | 默认值 | 说明 |
|------|--------|------|
| `name` | 属性名 | 数据库列名 |
| `nullable` | true | 是否允许NULL |
| `length` | 255 | 字符串列长度（仅VARCHAR类型生效） |
| `unique` | false | 是否唯一约束 |
| `precision` | 0 | 数值总位数（配合scale使用） |
| `scale` | 0 | 小数位数 |
| `insertable` | true | 是否参与INSERT |
| `updatable` | true | 是否参与UPDATE |

### 14.2.4 @Enumerated：枚举类型映射

```java
public enum EmployeeStatus {
    ACTIVE,
    INACTIVE,
    RESIGNED
}

@Entity
public class Employee {
    // ...
    @Enumerated(EnumType.STRING)  // 存储为字符串 'ACTIVE'
    private EmployeeStatus status;
}
```

> 🚨 **坑点：`@Enumerated`默认为`EnumType.ORDINAL` → 枚举顺序变了，数据库数据全乱！**
> - `ORDINAL`：按枚举定义的顺序存储序号（`ACTIVE=0, INACTIVE=1, RESIGNED=2`）
> - 假设你后来在`ACTIVE`前面加了一个`PENDING`：
>   ```java
>   public enum EmployeeStatus { PENDING, ACTIVE, INACTIVE, RESIGNED }
>   ```
> - 原来的`ACTIVE(0)`现在变成了`PENDING(0)`，`INACTIVE(1)`变成了`ACTIVE(1)`！
> - 数据库中存的都是数字，根本不知道你的枚举顺序变了。**全部数据映射错乱！**
> - **解决**：永远写 `@Enumerated(EnumType.STRING)`，存储为`'ACTIVE'`，可读且不受顺序影响。

### 14.2.5 @Transient：不映射到数据库

```java
@Transient
private String fullName;  // 这个字段不存数据库，只在Java内存中使用

public String getFullName() {
    return name + " (" + department + ")";
}
```

任何标注了`@Transient`的字段，JPA都会忽略它的持久化（不创建列、不读不写）。常用于计算字段、临时数据。

### 14.2.6 时间自动填充

审计字段（创建时间、修改时间）是每个表的标准配置：

```java
import jakarta.persistence.*;
import org.springframework.data.annotation.CreatedDate;
import org.springframework.data.annotation.LastModifiedDate;
import org.springframework.data.jpa.domain.support.AuditingEntityListener;
import java.time.LocalDateTime;

@Entity
@EntityListeners(AuditingEntityListener.class)  // 启用审计监听器
public class Employee {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String name;

    @CreatedDate
    @Column(updatable = false)  // 创建后不允许修改
    private LocalDateTime createTime;

    @LastModifiedDate
    private LocalDateTime updateTime;

    // ...
}
```

还需要在启动类上启用JPA审计：

```java
@SpringBootApplication
@EnableJpaAuditing  // 启用JPA审计功能
public class Application {
    public static void main(String[] args) {
        SpringApplication.run(Application.class, args);
    }
}
```

效果：每次`save`一个实体时，`createTime`自动设为当前时间（仅首次创建时），`updateTime`自动更新为当前时间——完全无需手动设置。

### 14.2.7 关联关系注解

JPA最强大的特性之一就是用注解表达表之间的关系，让外键变成Java对象的引用。

**（1）@OneToOne：一对一**

```java
@Entity
public class Employee {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @OneToOne
    @JoinColumn(name = "desk_id")  // employee表中的外键列
    private Desk desk;  // 这个员工被分配的工位
}

@Entity
public class Desk {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String locationCode;

    @OneToOne(mappedBy = "desk")  // 双向关联的反方，由Employee.desk维护外键
    private Employee employee;
}
```

**（2）@ManyToOne + @OneToMany：多对一/一对多**

```java
@Entity
public class Employee {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    private String name;

    @ManyToOne
    @JoinColumn(name = "department_id")  // employee表中的外键列
    private Department department;  // 员工属于哪个部门
}

@Entity
public class Department {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    private String name;

    @OneToMany(mappedBy = "department")  // 由Employee.department维护外键
    private List<Employee> employees;  // 部门下有哪些员工
}
```

关键理解：多对一中，**外键存在于"多"的一方**（Employee表），`mappedBy`告诉JPA"这个关系由对方（Employee.department）来维护外键"。

**（3）@ManyToMany：多对多**

```java
@Entity
public class Employee {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    private String name;

    @ManyToMany
    @JoinTable(
        name = "employee_project",  // 中间表名
        joinColumns = @JoinColumn(name = "employee_id"),       // 指向本表的外键
        inverseJoinColumns = @JoinColumn(name = "project_id")  // 指向对方表的外键
    )
    private Set<Project> projects;  // 员工参与了哪些项目
}

@Entity
public class Project {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    private String name;

    @ManyToMany(mappedBy = "projects")  // 由Employee.projects维护
    private Set<Employee> employees;
}
```

### 14.2.8 双向关联无限递归 — 本小节必须解决的问题！

> 🚨 **坑点：双向关联 + JSON序列化 = StackOverflowError（无限递归）！**

问题场景：

```java
Department dept = departmentRepository.findById(1L).get();
// dept.getEmployees() = 该部门的所有员工列表
// 每个员工的 department 属性又指向 dept
// dept 的 employees 属性又包含这些员工...
// → 无限循环！
```

当Spring MVC将`Department`对象序列化为JSON返回给前端时：

```
Department → employees[0] → department → employees[0] → department → ... (无限递归)
```

最终抛出 **`StackOverflowError`**。

**解决方案（三种，按推荐程度排序）**：

**方案一：`@JsonIgnore`（最简单）** —— 在不需要序列化的那一端忽略：

```java
@Entity
public class Department {
    // ...

    @OneToMany(mappedBy = "department")
    @JsonIgnore  // 查询部门时，不序列化员工列表
    private List<Employee> employees;
}
```

如果需要某个接口返回带员工列表的部门，又不想在另一个接口中出现递归，可以用DTO（数据传输对象）区分。

**方案二：`@JsonManagedReference` + `@JsonBackReference`（更精细）**：

```java
@Entity
public class Department {
    @OneToMany(mappedBy = "department")
    @JsonManagedReference   // "被管理"的引用 → 正常序列化
    private List<Employee> employees;
}

@Entity
public class Employee {
    @ManyToOne
    @JoinColumn(name = "department_id")
    @JsonBackReference      // "回指"引用 → 序列化时忽略
    private Department department;
}
```

**方案三：使用DTO（最推荐，生产环境标准做法）**：

```java
// 不直接返回Entity，而是返回DTO
public class DepartmentDTO {
    private Long id;
    private String name;
    private List<EmployeeSummaryDTO> employees; // 只包含摘要信息，不含department回指

    public static DepartmentDTO from(Department dept) {
        DepartmentDTO dto = new DepartmentDTO();
        dto.setId(dept.getId());
        dto.setName(dept.getName());
        dto.setEmployees(dept.getEmployees().stream()
            .map(EmployeeSummaryDTO::from)
            .toList());
        return dto;
    }
}
```

> ⚠️ **最佳实践**：生产环境中，永远不要直接向Controller返回JPA Entity对象。始终使用DTO做一层转换——这不仅解决了递归问题，还实现了API与数据库模型的解耦。

### 14.2.9 CascadeType：级联操作的陷阱

```java
@OneToMany(mappedBy = "department", cascade = CascadeType.ALL)
private List<Employee> employees;
```

级联类型说明：

| CascadeType | 效果 | 危险程度 |
|-------------|------|---------|
| `PERSIST` | 保存部门时，自动保存新增的员工 | ⭐ 安全 |
| `MERGE` | 更新部门时，自动更新关联的员工 | ⭐ 安全 |
| `REMOVE` | 删除部门时，**自动删除该部门的所有员工** | ⚠️⚠️⚠️ 危险！ |
| `ALL` | 以上全部（等效于PERSIST+MERGE+REMOVE） | ⚠️⚠️⚠️ 非常危险！ |
| `DETACH` | 脱管时，自动脱管关联实体 | ⭐ 安全 |
| `REFRESH` | 刷新时，自动刷新关联实体 | ⭐ 安全 |

> 🚨 **坑点：`cascade = CascadeType.ALL`或`CascadeType.REMOVE`→ 误删关联数据！**
> - 如果你在一个不重要的刷新操作中间接调用了`delete(dept)`，结果把整个部门的员工全删了
> - **建议**：除非业务明确要求"删除部门时级联删除员工"，否则不要使用`REMOVE`和`ALL`
> - 安全做法：显式写 `cascade = {CascadeType.PERSIST, CascadeType.MERGE}`

---

## 14.3 Repository接口

### 14.3.1 继承体系

Spring Data为Repository设计了一套清晰的继承树：

```
Repository (标记接口，最顶层)
  └── CrudRepository (基本CRUD)
        └── PagingAndSortingRepository (分页+排序)
              └── JpaRepository (JPA专用：批量操作/flush/删批)
```

日常开发中，几乎总是直接继承`JpaRepository`，因为它包含了你需要的所有方法：

```java
import com.example.entity.Employee;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface EmployeeRepository extends JpaRepository<Employee, Long> {
    // <Employee, Long> = <实体类型, 主键类型>

    // 你不需要写任何代码！以下方法全部自动提供：
    // save(Employee)       → INSERT 或 UPDATE
    // findById(Long)       → SELECT ... WHERE id=?
    // findAll()            → SELECT * FROM ...
    // count()              → SELECT COUNT(*)
    // deleteById(Long)     → DELETE ... WHERE id=?
    // existsById(Long)     → SELECT COUNT(*) > 0
    // ... 还有十几个内置方法
}
```

### 14.3.2 JpaRepository内置方法速查

| 方法 | 作用 | SQL等价 |
|------|------|---------|
| `save(S entity)` | 新增或更新（有ID则更新，无ID则新增） | INSERT/UPDATE |
| `saveAll(Iterable<S>)` | 批量保存 | 批量INSERT/UPDATE |
| `findById(ID id)` | 按主键查（返回`Optional<T>`） | `SELECT ... WHERE id=?` |
| `findAll()` | 查全部 | `SELECT *` |
| `findAllById(Iterable<ID>)` | 按主键集合批量查 | `SELECT ... WHERE id IN (?)` |
| `count()` | 总记录数 | `SELECT COUNT(*)` |
| `existsById(ID id)` | 是否存在 | `SELECT COUNT(*) > 0` |
| `deleteById(ID id)` | 按主键删除 | `DELETE ... WHERE id=?` |
| `delete(T entity)` | 删除指定实体 | `DELETE ... WHERE id=?` |
| `deleteAll()` | 删除全部（逐条删！慎用） | `DELETE FROM ...` |
| `deleteAllInBatch()` | 批量删除全部（一条SQL） | `DELETE FROM ...` |
| `flush()` | 将持久化上下文的变更立即同步到数据库 | — |
| `getReferenceById(ID id)` | 获取引用（延迟加载，不立即查库） | 使用时才SELECT |

```java
@Service
public class EmployeeService {

    private final EmployeeRepository employeeRepository;

    public EmployeeService(EmployeeRepository employeeRepository) {
        this.employeeRepository = employeeRepository;
    }

    // 查询：利用Optional的安全机制
    public Employee getById(Long id) {
        return employeeRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("员工不存在: " + id));
    }

    // 保存（新增or更新）
    public Employee save(Employee employee) {
        return employeeRepository.save(employee);
    }

    // 删除
    public void delete(Long id) {
        employeeRepository.deleteById(id);
    }
}
```

> 🚨 **坑点：不要直接在Controller用Repository！**
> - 虽然技术上可行（注入Repository到Controller），但这打破了分层架构
> - Controller应该只管HTTP请求/响应，Service层管理业务逻辑和事务
> - 通过Service封装的好处：可以在Service中统一管理事务（`@Transactional`）、添加业务规则校验、组合多个Repository操作

---

## 14.4 方法命名查询

Spring Data JPA最令人惊叹的特性：你只需要按规则命名方法，JPA就能自动生成对应的SQL。

### 14.4.1 规则大全

```java
@Repository
public interface EmployeeRepository extends JpaRepository<Employee, Long> {

    // ===== 精确匹配 =====
    Employee findByName(String name);                          // WHERE name = ?

    // ===== 多条件组合 =====
    List<Employee> findByNameAndAge(String name, Integer age); // WHERE name=? AND age=?
    List<Employee> findByNameOrDepartment(String name, String dept); // WHERE name=? OR dept=?

    // ===== 比较运算 =====
    List<Employee> findByAgeGreaterThan(Integer age);          // WHERE age > ?
    List<Employee> findBySalaryLessThan(Double salary);        // WHERE salary < ?
    List<Employee> findByAgeBetween(Integer min, Integer max); // WHERE age BETWEEN ? AND ?
    List<Employee> findByHireDateAfter(LocalDate date);        // WHERE hire_date > ?
    List<Employee> findByHireDateBefore(LocalDate date);       // WHERE hire_date < ?

    // ===== 模糊查询 =====
    List<Employee> findByNameLike(String pattern);             // WHERE name LIKE ?
    List<Employee> findByNameStartingWith(String prefix);      // WHERE name LIKE 'prefix%'
    List<Employee> findByNameEndingWith(String suffix);        // WHERE name LIKE '%suffix'
    List<Employee> findByNameContaining(String keyword);       // WHERE name LIKE '%keyword%'

    // ===== 集合查询 =====
    List<Employee> findByDepartmentIn(List<String> departments); // WHERE department IN (?)
    List<Employee> findByIdNotIn(List<Long> ids);               // WHERE id NOT IN (?)

    // ===== NULL检查 =====
    List<Employee> findByEmailIsNull();                        // WHERE email IS NULL
    List<Employee> findByEmailIsNotNull();                     // WHERE email IS NOT NULL

    // ===== 排序 =====
    List<Employee> findByDepartmentOrderBySalaryDesc(String dept); // ...ORDER BY salary DESC
    List<Employee> findByDepartmentOrderByAgeAscNameDesc(String dept); // ...ORDER BY age ASC, name DESC

    // ===== 限制数量 =====
    List<Employee> findTop3ByOrderBySalaryDesc();              // LIMIT 3
    Employee findFirstByDepartmentOrderByHireDateAsc(String dept); // LIMIT 1
}
```

### 14.4.2 方法命名规则组合

一个复杂的方法名：

```java
List<Employee> findTop10ByNameContainingAndAgeBetweenAndDepartmentInOrderBySalaryDesc(
    String keyword, Integer minAge, Integer maxAge, List<String> depts
);
```

SQL等价：

```sql
SELECT * FROM employee
WHERE name LIKE '%keyword%'
  AND age BETWEEN ? AND ?
  AND department IN (?, ?, ?)
ORDER BY salary DESC
LIMIT 10
```

> 🚨 **坑点：方法名太长 → 可读性极差！**
> - 当方法名超过30个字符（如上面的例子），读一个方法名要逐词解析
> - **原则**：方法名超过3-4个条件时，改用`@Query`写JPQL——清晰100倍
> - ```java
>   // 对比：用@Query清晰得多
>   @Query("SELECT e FROM Employee e WHERE e.name LIKE %:keyword% " +
>          "AND e.age BETWEEN :minAge AND :maxAge " +
>          "AND e.department IN :depts ORDER BY e.salary DESC")
>   List<Employee> search(@Param("keyword") String keyword,
>                          @Param("minAge") Integer minAge,
>                          @Param("maxAge") Integer maxAge,
>                          @Param("depts") List<String> depts);
>   ```

### 14.4.3 常用关键词速查

| 关键词 | SQL等价 | 示例 |
|--------|---------|------|
| `And` | `AND` | `findByNameAndAge` |
| `Or` | `OR` | `findByNameOrDepartment` |
| `Is` / `Equals` | `=` | `findByNameIs` 或 `findByNameEquals` |
| `Between` | `BETWEEN` | `findByAgeBetween` |
| `LessThan` | `<` | `findBySalaryLessThan` |
| `GreaterThan` | `>` | `findByAgeGreaterThan` |
| `After` | `>`（日期） | `findByHireDateAfter` |
| `Before` | `<`（日期） | `findByHireDateBefore` |
| `Like` | `LIKE` | `findByNameLike` |
| `StartingWith` | `LIKE 'xx%'` | `findByNameStartingWith` |
| `EndingWith` | `LIKE '%xx'` | `findByNameEndingWith` |
| `Containing` | `LIKE '%xx%'` | `findByNameContaining` |
| `In` | `IN` | `findByDepartmentIn` |
| `NotIn` | `NOT IN` | `findByIdNotIn` |
| `IsNull` | `IS NULL` | `findByEmailIsNull` |
| `IsNotNull` | `IS NOT NULL` | `findByEmailIsNotNull` |
| `OrderBy` | `ORDER BY` | `findByDepartmentOrderBySalaryDesc` |
| `First` / `Top` | `LIMIT` | `findFirst3By...` |
| `True` / `False` | `= TRUE / FALSE` | `findByActiveTrue` |
| `IgnoreCase` | `UPPER(column) = UPPER(?)` | `findByNameIgnoreCase` |

---

## 14.5 @Query查询

当命名查询不够用，或者方法名太长时，`@Query`是你的救星。

### 14.5.1 JPQL vs 原生SQL

JPQL（Java Persistence Query Language）是JPA定义的面向对象查询语言——**查询的是实体和属性，而不是表和列**。

```java
// ===== JPQL：面向实体和属性 =====
@Query("SELECT e FROM Employee e WHERE e.department.name = :deptName")
List<Employee> findByDeptName(@Param("deptName") String deptName);

// ===== 原生SQL：面向表和列 =====
@Query(value = "SELECT * FROM employee WHERE department_id = ?1",
       nativeQuery = true)
List<Employee> findByDeptIdNative(Long deptId);
```

关键区别：

| 维度 | JPQL | 原生SQL（nativeQuery=true） |
|------|------|--------------------------|
| **查询对象** | 实体类名和属性名（`Employee`/`e.name`） | 表名和列名（`employee`/`name`） |
| **FROM子句** | `FROM Employee`（类名） | `FROM employee`（表名） |
| **关联查询** | `e.department.name`（点号穿透对象图） | `JOIN department d ON e.department_id = d.id` |
| **数据库方言** | JPA自动适配 | 手写SQL，绑定特定数据库 |
| **可移植性** | ✅ 换数据库只需改方言 | ❌ 换数据库需改写SQL |
| **推荐度** | ⭐⭐⭐ 优先使用 | ⭐ 仅复杂查询和数据库特有函数时使用 |

### 14.5.2 参数绑定

两种方式可以混用（但不推荐混用）：

```java
// 位置绑定（?编号）：容易出现参数顺序错误
@Query("SELECT e FROM Employee e WHERE e.department = ?1 AND e.salary >= ?2")
List<Employee> findByDeptAndMinSalary(String dept, Double minSalary);

// 命名绑定（:参数名）：清晰，推荐
@Query("SELECT e FROM Employee e WHERE e.department = :dept AND e.salary >= :minSal")
List<Employee> findByDeptAndMinSalaryNamed(
    @Param("dept") String dept,
    @Param("minSal") Double minSalary
);
```

**推荐始终使用命名绑定**——参数多了位置绑定极易错位。

### 14.5.3 @Modifying：UPDATE/DELETE操作

对于`SELECT`之外的写操作，必须同时使用两个注解：

```java
@Modifying
@Transactional
@Query("UPDATE Employee e SET e.salary = e.salary * :rate WHERE e.department = :dept")
int raiseSalaryByDept(@Param("dept") String dept, @Param("rate") double rate);

@Modifying
@Transactional
@Query("DELETE FROM Employee e WHERE e.department = :dept")
int deleteByDepartment(@Param("dept") String dept);
```

> 🚨 **坑点：`@Modifying`忘记加`@Transactional` → 执行报错！**
> - `@Modifying`标注的方法必须是事务性的
> - 如果没有`@Transactional`，会抛出 `TransactionRequiredException`
> - 从Spring Data JPA 2.x起，`@Modifying`的`clearAutomatically`默认false → 更新后的实体可能还在持久化上下文中（脏数据），建议设置`clearAutomatically = true`

> 🚨 **坑点：`nativeQuery=true`忘记设置 → SQL被当作JPQL执行！**
> - 当你写了一条原生SQL但忘记加`nativeQuery = true`
> - JPA会把它当作JPQL解析 → `SELECT * FROM employee` 在JPQL中是无效语法（JPQL应该是`SELECT e FROM Employee e`）
> - 报错：`unexpected token: *`
> - **排查方法**：看到"unexpected token"且SQL中有`*`号 → 99%是忘记设置`nativeQuery=true`

### 14.5.4 JPQL关联查询

JPQL最大的优势在于跨实体关联查询，利用对象图导航：

```java
// 查所有在"技术部"的员工 —— 不用写JOIN！
@Query("SELECT e FROM Employee e WHERE e.department.name = :deptName")
List<Employee> findByDepartmentName(@Param("deptName") String deptName);

// 查所有月薪大于部门平均薪资的员工（关联查询 + 子查询）
@Query("SELECT e FROM Employee e WHERE e.salary > " +
       "(SELECT AVG(e2.salary) FROM Employee e2 WHERE e2.department = e.department)")
List<Employee> findAboveDeptAverage();

// JOIN FETCH：一次性加载关联数据（解决N+1问题，见14.7.2节）
@Query("SELECT d FROM Department d JOIN FETCH d.employees WHERE d.id = :id")
Optional<Department> findByIdWithEmployees(@Param("id") Long id);
```

---

## 14.6 分页与排序

### 14.6.1 Pageable接口

JPA的分页极其简洁——在Repository方法上加一个`Pageable`参数即可：

```java
@Repository
public interface EmployeeRepository extends JpaRepository<Employee, Long> {

    // 自动分页查询
    Page<Employee> findByDepartment(String department, Pageable pageable);

    // 带排序的分页查询
    @Query("SELECT e FROM Employee e WHERE e.salary >= :minSal")
    Page<Employee> findByMinSalary(@Param("minSal") Double minSal, Pageable pageable);
}
```

Service层调用：

```java
// 第1页，每页10条，按薪资降序
Pageable pageable = PageRequest.of(0, 10, Sort.by("salary").descending());
Page<Employee> page = employeeRepository.findByDepartment("技术部", pageable);

System.out.println("当前页数据: " + page.getContent());
System.out.println("当前页码: " + page.getNumber());
System.out.println("每页大小: " + page.getSize());
System.out.println("总记录数: " + page.getTotalElements());
System.out.println("总页数: " + page.getTotalPages());
System.out.println("是否有下一页: " + page.hasNext());
```

> 🚨 **坑点：Pageable的页码从0开始！**
> - `PageRequest.of(0, 10)` = 第1页，`PageRequest.of(1, 10)` = 第2页
> - 前端通常传第1页时传`page=1`，你需要在Service层做转换：`PageRequest.of(page - 1, size)`
> - 忘记这个规则 → 前端请求第1页，你给了第2页的数据

**Page<T> 返回结果的结构**：

```json
{
    "content": [ { "id": 1, "name": "张三" }, ... ],
    "pageable": { "pageNumber": 0, "pageSize": 10 },
    "totalElements": 85,
    "totalPages": 9,
    "last": false,
    "first": true,
    "numberOfElements": 10,
    "empty": false
}
```

### 14.6.2 多级排序

```java
// 先按部门升序，部门相同按薪资降序
Sort sort = Sort.by(Sort.Order.asc("department"), Sort.Order.desc("salary"));
Pageable pageable = PageRequest.of(0, 10, sort);
```

### 14.6.3 Slice：轻量分页（不需要总记录数）

如果不需要知道"总共有多少页"（如无限滚动加载），用`Slice`代替`Page`：

```java
Slice<Employee> findByDepartment(String department, Pageable pageable);

// Slice只查 pageSize+1 条数据来判断"是否有下一页"
// 不会执行 COUNT(*) 查询，性能更好
```

---

## 14.7 JPA高级话题

### 14.7.1 一级缓存与脏检查

JPA（Hibernate）维护了一个**一级缓存（Persistence Context / EntityManager缓存）**——同一事务内的实体状态管理。

**现象一：同一事务内，同一个ID只查一次数据库**：

```java
@Transactional
public void cacheDemo() {
    Employee e1 = repository.findById(1L).orElseThrow();  // 发出一条SELECT
    Employee e2 = repository.findById(1L).orElseThrow();  // 不发出SQL！从一级缓存拿
    System.out.println(e1 == e2);                         // true（同一个对象引用）
}
```

**现象二：脏检查（Dirty Checking）——自动更新**：

```java
@Transactional
public void dirtyCheckDemo() {
    Employee emp = repository.findById(1L).orElseThrow();
    emp.setName("新名字");  // 只改了Java对象的属性，没有调save()！
    // 事务提交时，JPA对比emp的当前状态和加载时的原始状态
    // 发现name变了 → 自动发出 UPDATE employee SET name='新名字' WHERE id=1
}
```

> 🚨 **坑点：同一事务内修改实体 → 自动发送UPDATE！**
> - 这是JPA的核心机制（脏检查），也是很多人觉得"JPA莫名其妙改了数据库"的原因
> - 事务提交时，JPA会自动flush所有变更到数据库——**不管你有没有显式调用save()**
> - 如果你只是临时修改了实体做计算而并不想更新数据库 → 在一个只读事务中操作，或使用`@Transactional(readOnly = true)`

### 14.7.2 延迟加载与N+1问题

JPA的关联关系默认加载策略：

| 关联类型 | 默认FetchType | 说明 |
|----------|-------------|------|
| `@OneToOne` | **EAGER**（立即加载） | 查主实体时同时查关联实体 |
| `@ManyToOne` | **EAGER**（立即加载） | 查主实体时同时查关联实体 |
| `@OneToMany` | **LAZY**（延迟加载） | 查主实体时不查关联集合，用到时才查 |
| `@ManyToMany` | **LAZY**（延迟加载） | 同上 |

**N+1问题演示**：

```java
// 查询所有部门：1条SQL
List<Department> depts = departmentRepository.findAll();  // SELECT * FROM department

// 遍历每个部门获取员工：N条SQL
for (Department dept : depts) {
    System.out.println(dept.getEmployees().size()); // 每个部门触发一次 SELECT * FROM employee WHERE department_id=?
}
// 总共：1 + N 条SQL → N+1问题！
```

**解决方案一：`@EntityGraph`**（推荐，最简单）：

```java
// Repository中添加
@EntityGraph(attributePaths = {"employees"})  // 指定要一起加载的关联属性
@Query("SELECT d FROM Department d")
List<Department> findAllWithEmployees();  // 一条SQL + JOIN搞定
```

**解决方案二：`JOIN FETCH`**：

```java
@Query("SELECT DISTINCT d FROM Department d LEFT JOIN FETCH d.employees")
List<Department> findAllWithEmployees();
```

> ⚠️ **注意**：`JOIN FETCH`和`@EntityGraph`的本质是一样的——用一条带JOIN的SQL一次性把所有数据取出来。区别在于`@EntityGraph`是声明式的（推荐），`JOIN FETCH`需要手写JPQL。

### 14.7.3 OSIV（Open Session In View）

> 🚨 **坑点：OSIV默认开启 → 数据库连接保持到视图渲染完 → 高并发连接耗尽！**

OSIV是Spring Boot + JPA中最容易被忽视的性能杀手。

**OSIV开启时的流程**（默认行为）：

```
请求进入 → 开启Session(占用一个数据库连接) → Controller处理 → Service处理
→ Repository查询 → 返回数据 → 视图渲染(可能触发懒加载) → Session关闭(归还连接)
                                                                    ↑
                                    连接被占用了整个请求周期！
```

**问题**：如果视图渲染需要200ms（Thymeleaf模板渲染、大数据量JSON序列化），连接就被无意义地占用了200ms。高并发场景下，连接池很快耗尽。

**OSIV关闭后的流程**（推荐）：

```
请求进入 → Controller处理 → Service处理(@Transactional范围内)
→ Repository查询 → Session关闭(归还连接) → 视图渲染(不需要连接)
```

**关闭方式**：

```yaml
spring:
  jpa:
    open-in-view: false    # 关闭OSIV（前后端分离项目强烈建议关闭！）
```

关闭后的注意事项：
- 懒加载的关联数据在Service层事务外无法访问 → 会在访问时报`LazyInitializationException`
- 解决方案：在Service层中用`JOIN FETCH`或`@EntityGraph`提前把需要的数据加载好

### 14.7.4 ddl-auto配置 — 生产环境的定时炸弹

> 🛑 **警告：这是本章最重要的配置！配置错误可能导致生产数据库被清空！**

```yaml
spring:
  jpa:
    hibernate:
      ddl-auto: validate   # ← 生产环境的唯一安全选择！
    show-sql: false        # 生产环境关闭SQL日志（性能优化）
```

`ddl-auto`的五个取值：

| 值 | 行为 | 启动时做什么 | 开发 | 测试 | 生产 |
|----|------|------------|------|------|------|
| `none` | 什么都不做 | 无 | ❌ | ⚠️ | ✅ |
| `validate` | 校验实体与表结构是否一致 | 不一致则**启动失败**（不修改表） | ⚠️ | ✅ | **✅ 推荐** |
| `update` | 自动修改表结构 | 新增的列会添加；**但已删除的列不会删除！** | ✅ | ⚠️ | 🛑 **禁用！** |
| `create` | 每次启动删表重建 | **启动时DROP所有表再CREATE** | ⚠️ | ⚠️ | 🛑 **绝对禁用！** |
| `create-drop` | 启动建表，关闭删表 | 同create + SessionFactory关闭时DROP | ⚠️ | ⚠️ | 🛑 **绝对禁用！** |

> 🛑 **生产环境底线**：
> - **`create`**：每次重启删掉整个数据库重建 → **所有数据永久丢失！**
> - **`create-drop`**：同上，但应用关闭时还要再删一次 → **双重毁灭！**
> - **`update`**：
>   - 你以为它"智能更新表结构"，实际上：
>     - 新增列 → 它会添加（看似方便）
>     - 删除列 → **它不会删除！** 导致数据库有废弃列
>     - 修改列类型 → **可能执行失败！** (如VARCHAR(50)改VARCHAR(100)，DDL不保证成功)
>     - 外键重命名 → **它不认识，可能删了旧的再建新的，导致数据丢失！**
> - **生产环境唯一安全选择：`validate`**
>   - 启动时只检查实体定义和表结构是否一致
>   - 不一致则**启动失败**，但**绝不修改数据库**
>   - 所有DDL变更统一通过Flyway/Liquibase等版本管理工具手工管理

> 🛑 **真实案例**：2020年某国外电商平台运维人员在重启生产服务器时，Spring Boot配置中`ddl-auto`被错误设为`create`，导致启动后所有订单数据被清空。恢复用了整整72小时，直接经济损失超过200万美元。**这个配置值可能就是200万美金。**

---

## EMS v4：MyBatis版 + JPA版员工CRUD

恭喜你学完了MyBatis（第13章）和JPA（第14章）！现在是实战时刻——用两种方式实现同一个员工管理系统，亲身体验两者的差异。

### v4 vs v3 对比

| 对比维度 | EMS v3（第12章） | EMS v4（本章） |
|----------|---------------|---------------|
| 数据存储 | 内存List（无持久化） | MySQL数据库 |
| 持久化方式 | 无 | **MyBatis版** / **JPA版**（双版本） |
| 技术栈 | Spring IoC/AOP/MVC | Spring + MyBatis / Spring + JPA |
| DAO层 | 无（Service直接操作List） | Mapper接口 / Repository接口 |

### 项目结构

```
ems-v4/
├── pom.xml
├── src/main/resources/
│   ├── application.yml                           ← 数据源配置
│   └── mapper/                                    ← MyBatis版XML
│       └── EmployeeMapper.xml
└── src/main/java/com/ems/
    ├── Application.java                           ← 启动类
    ├── entity/
    │   └── Employee.java                          ← 公共实体（Lombok @Data）
    ├── mybatis/                                   ← MyBatis版
    │   ├── mapper/
    │   │   └── EmployeeMapper.java                ← Mapper接口
    │   ├── service/
    │   │   └── EmployeeServiceMyBatis.java         ← Service（MyBatis实现）
    │   └── controller/
    │       └── EmployeeControllerMyBatis.java      ← Controller（MyBatis实现）
    └── jpa/                                       ← JPA版
        ├── repository/
        │   └── EmployeeRepository.java            ← Repository接口
        ├── service/
        │   └── EmployeeServiceJpa.java             ← Service（JPA实现）
        └── controller/
            └── EmployeeControllerJpa.java          ← Controller（JPA实现）
```

### 公共部分

**pom.xml**（两个版本的所有依赖）：

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
        <version>3.2.0</version>
    </parent>

    <groupId>com.ems</groupId>
    <artifactId>ems-v4</artifactId>
    <version>4.0</version>

    <properties>
        <java.version>17</java.version>
    </properties>

    <dependencies>
        <!-- Spring Boot Web -->
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
        </dependency>

        <!-- MyBatis -->
        <dependency>
            <groupId>org.mybatis.spring.boot</groupId>
            <artifactId>mybatis-spring-boot-starter</artifactId>
            <version>3.0.3</version>
        </dependency>

        <!-- Spring Data JPA -->
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-data-jpa</artifactId>
        </dependency>

        <!-- MySQL -->
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
</project>
```

**application.yml**：

```yaml
spring:
  datasource:
    url: jdbc:mysql://localhost:3306/ems?useSSL=false&serverTimezone=Asia/Shanghai&characterEncoding=utf8mb4
    username: root
    password: 你的密码
    driver-class-name: com.mysql.cj.jdbc.Driver

  jpa:
    hibernate:
      ddl-auto: validate
    show-sql: true
    open-in-view: false

mybatis:
  mapper-locations: classpath:mapper/*.xml
  type-aliases-package: com.ems.entity
  configuration:
    map-underscore-to-camel-case: true
    log-impl: org.apache.ibatis.logging.stdout.StdOutImpl
```

**Employee.java（公共实体）**：

```java
package com.ems.entity;

import jakarta.persistence.*;
import lombok.Data;
import java.time.LocalDate;

@Data
@Entity
@Table(name = "employee")
public class Employee {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, length = 50)
    private String name;

    private Integer age;

    private String department;

    private Double salary;

    @Column(unique = true)
    private String email;

    @Column(name = "hire_date")
    private LocalDate hireDate;
}
```

> **注意**：同一个`Employee`类被MyBatis和JPA共用。JPA注解（`@Entity`、`@Id`等）不影响MyBatis的映射，两者可以和平共存。

**Application.java（启动类）**：

```java
package com.ems;

import org.mybatis.spring.annotation.MapperScan;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
@MapperScan("com.ems.mybatis.mapper")
public class Application {
    public static void main(String[] args) {
        SpringApplication.run(Application.class, args);
    }
}
```

### 方案A：MyBatis版

**EmployeeMapper.java**：

```java
package com.ems.mybatis.mapper;

import com.ems.entity.Employee;
import org.apache.ibatis.annotations.Mapper;
import java.util.List;

@Mapper
public interface EmployeeMapper {

    List<Employee> findAll();

    Employee findById(Long id);

    List<Employee> findByDepartment(String department);

    List<Employee> findBySalaryRange(@org.apache.ibatis.annotations.Param("min") Double min,
                                      @org.apache.ibatis.annotations.Param("max") Double max);

    List<Employee> search(@org.apache.ibatis.annotations.Param("keyword") String keyword,
                          @org.apache.ibatis.annotations.Param("department") String department,
                          @org.apache.ibatis.annotations.Param("minSalary") Double minSalary);

    int insert(Employee employee);

    int update(Employee employee);

    int deleteById(Long id);
}
```

**EmployeeMapper.xml**（放在`src/main/resources/mapper/`）：

```xml
<?xml version="1.0" encoding="UTF-8" ?>
<!DOCTYPE mapper PUBLIC "-//mybatis.org//DTD Mapper 3.0//EN"
        "http://mybatis.org/dtd/mybatis-3-mapper.dtd">

<mapper namespace="com.ems.mybatis.mapper.EmployeeMapper">

    <select id="findAll" resultType="com.ems.entity.Employee">
        SELECT id, name, age, department, salary, email, hire_date
        FROM employee ORDER BY id
    </select>

    <select id="findById" resultType="com.ems.entity.Employee">
        SELECT id, name, age, department, salary, email, hire_date
        FROM employee WHERE id = #{id}
    </select>

    <select id="findByDepartment" resultType="com.ems.entity.Employee">
        SELECT id, name, age, department, salary, email, hire_date
        FROM employee WHERE department = #{department} ORDER BY id
    </select>

    <select id="findBySalaryRange" resultType="com.ems.entity.Employee">
        SELECT id, name, age, department, salary, email, hire_date
        FROM employee WHERE salary BETWEEN #{min} AND #{max} ORDER BY salary DESC
    </select>

    <select id="search" resultType="com.ems.entity.Employee">
        SELECT id, name, age, department, salary, email, hire_date FROM employee
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
        </where>
        ORDER BY id
    </select>

    <insert id="insert" useGeneratedKeys="true" keyProperty="id">
        INSERT INTO employee (name, age, department, salary, email, hire_date)
        VALUES (#{name}, #{age}, #{department}, #{salary}, #{email}, #{hireDate})
    </insert>

    <update id="update">
        UPDATE employee
        SET name=#{name}, age=#{age}, department=#{department},
            salary=#{salary}, email=#{email}
        WHERE id=#{id}
    </update>

    <delete id="deleteById">
        DELETE FROM employee WHERE id=#{id}
    </delete>

</mapper>
```

**EmployeeServiceMyBatis.java**：

```java
package com.ems.mybatis.service;

import com.ems.entity.Employee;
import com.ems.mybatis.mapper.EmployeeMapper;
import org.springframework.stereotype.Service;
import java.util.List;

@Service
public class EmployeeServiceMyBatis {

    private final EmployeeMapper mapper;

    public EmployeeServiceMyBatis(EmployeeMapper mapper) {
        this.mapper = mapper;
    }

    public List<Employee> listAll() { return mapper.findAll(); }

    public Employee getById(Long id) { return mapper.findById(id); }

    public List<Employee> search(String keyword, String dept, Double minSalary) {
        return mapper.search(keyword, dept, minSalary);
    }

    public Employee add(Employee emp) {
        mapper.insert(emp);
        return emp;  // emp.getId() 已由useGeneratedKeys回填
    }

    public Employee modify(Employee emp) {
        mapper.update(emp);
        return emp;
    }

    public void remove(Long id) { mapper.deleteById(id); }
}
```

**EmployeeControllerMyBatis.java**：

```java
package com.ems.mybatis.controller;

import com.ems.entity.Employee;
import com.ems.mybatis.service.EmployeeServiceMyBatis;
import org.springframework.web.bind.annotation.*;
import java.util.List;

@RestController
@RequestMapping("/api/mybatis/employees")
public class EmployeeControllerMyBatis {

    private final EmployeeServiceMyBatis service;

    public EmployeeControllerMyBatis(EmployeeServiceMyBatis service) {
        this.service = service;
    }

    @GetMapping
    public List<Employee> list() { return service.listAll(); }

    @GetMapping("/{id}")
    public Employee get(@PathVariable Long id) { return service.getById(id); }

    @GetMapping("/search")
    public List<Employee> search(
            @RequestParam(required = false) String keyword,
            @RequestParam(required = false) String department,
            @RequestParam(required = false) Double minSalary) {
        return service.search(keyword, department, minSalary);
    }

    @PostMapping
    public Employee add(@RequestBody Employee emp) { return service.add(emp); }

    @PutMapping("/{id}")
    public Employee modify(@PathVariable Long id, @RequestBody Employee emp) {
        emp.setId(id);
        return service.modify(emp);
    }

    @DeleteMapping("/{id}")
    public String remove(@PathVariable Long id) {
        service.remove(id);
        return "删除成功";
    }
}
```

### 方案B：JPA版

**EmployeeRepository.java**：

```java
package com.ems.jpa.repository;

import com.ems.entity.Employee;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;
import java.util.List;

@Repository
public interface EmployeeRepository extends JpaRepository<Employee, Long> {

    List<Employee> findByDepartment(String department);

    List<Employee> findBySalaryBetween(Double min, Double max);

    @Query("SELECT e FROM Employee e WHERE " +
           "(:keyword IS NULL OR e.name LIKE %:keyword% OR e.department LIKE %:keyword%) " +
           "AND (:department IS NULL OR e.department = :department) " +
           "AND (:minSalary IS NULL OR e.salary >= :minSalary)")
    List<Employee> search(@Param("keyword") String keyword,
                          @Param("department") String department,
                          @Param("minSalary") Double minSalary);
}
```

**EmployeeServiceJpa.java**：

```java
package com.ems.jpa.service;

import com.ems.entity.Employee;
import com.ems.jpa.repository.EmployeeRepository;
import org.springframework.stereotype.Service;
import java.util.List;

@Service
public class EmployeeServiceJpa {

    private final EmployeeRepository repo;

    public EmployeeServiceJpa(EmployeeRepository repo) {
        this.repo = repo;
    }

    public List<Employee> listAll() { return repo.findAll(); }

    public Employee getById(Long id) {
        return repo.findById(id)
                .orElseThrow(() -> new RuntimeException("员工不存在: " + id));
    }

    public List<Employee> search(String keyword, String dept, Double minSalary) {
        return repo.search(keyword, dept, minSalary);
    }

    public Employee add(Employee emp) {
        emp.setId(null);  // 确保是新增而非更新（JPA by ID判断）
        return repo.save(emp);
    }

    public Employee modify(Employee emp) {
        return repo.save(emp);  // JPA自动判断：有ID → UPDATE
    }

    public void remove(Long id) { repo.deleteById(id); }
}
```

**EmployeeControllerJpa.java**：

```java
package com.ems.jpa.controller;

import com.ems.entity.Employee;
import com.ems.jpa.service.EmployeeServiceJpa;
import org.springframework.web.bind.annotation.*;
import java.util.List;

@RestController
@RequestMapping("/api/jpa/employees")
public class EmployeeControllerJpa {

    private final EmployeeServiceJpa service;

    public EmployeeControllerJpa(EmployeeServiceJpa service) {
        this.service = service;
    }

    @GetMapping
    public List<Employee> list() { return service.listAll(); }

    @GetMapping("/{id}")
    public Employee get(@PathVariable Long id) { return service.getById(id); }

    @GetMapping("/search")
    public List<Employee> search(
            @RequestParam(required = false) String keyword,
            @RequestParam(required = false) String department,
            @RequestParam(required = false) Double minSalary) {
        return service.search(keyword, department, minSalary);
    }

    @PostMapping
    public Employee add(@RequestBody Employee emp) { return service.add(emp); }

    @PutMapping("/{id}")
    public Employee modify(@PathVariable Long id, @RequestBody Employee emp) {
        emp.setId(id);
        return service.modify(emp);
    }

    @DeleteMapping("/{id}")
    public String remove(@PathVariable Long id) {
        service.remove(id);
        return "删除成功";
    }
}
```

### 双版本对比总结

| 对比维度 | MyBatis版 | JPA版 |
|----------|----------|------|
| Java代码量 | ~130行 | ~80行 |
| 配置文件 | application.yml + EmployeeMapper.xml | application.yml |
| CRUD实现方式 | XML中手写SQL | JpaRepository自动提供 |
| 复杂查询 | `<where>`+`<if>` 动态SQL | JPQL `@Query` 参数判断 |
| 获取自增主键 | `useGeneratedKeys="true"` | JPA自动回填 |
| UPDATE方式 | 手写UPDATE XML | `repo.save()` 自动判断新增/更新 |
| 事务管理 | 手动控制 | JPA自动管理 |
| 灵活性 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| 开发速度 | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

### 测试接口

两个版本同时启动后（端口8080），可以用curl或Postman测试：

```bash
# MyBatis版
curl http://localhost:8080/api/mybatis/employees
curl -X POST http://localhost:8080/api/mybatis/employees \
  -H "Content-Type: application/json" \
  -d '{"name":"新员工","age":25,"department":"技术部","salary":15000,"email":"new@ems.com"}'

# JPA版
curl http://localhost:8080/api/jpa/employees
curl -X POST http://localhost:8080/api/jpa/employees \
  -H "Content-Type: application/json" \
  -d '{"name":"新员工","age":25,"department":"技术部","salary":15000,"email":"new2@ems.com"}'
```

---

## 14.8 本章小结

恭喜你完成了JPA的学习！回顾本章的收获：

1. **ORM思想**：对象↔关系映射，JPA是规范、Hibernate是实现、Spring Data JPA是封装——三层递进关系。

2. **MyBatis vs JPA选型**（8维度对比）：SQL控制力、开发效率、复杂查询、学习曲线、数据库迁移、SQL调优、适用场景、团队适配——没有谁更好，只有谁更适合当前场景。

3. **JPA核心注解**：
   - `@Entity` + `@Table`：实体与表映射
   - `@Id` + `@GeneratedValue(strategy = GenerationType.IDENTITY)`：**MySQL必须写IDENTITY，避免默认AUTO变TABLE**
   - `@Enumerated(EnumType.STRING)`：**永远用STRING，ORDINAL会因枚举顺序变化导致数据错乱**
   - `@OneToMany` / `@ManyToOne` + `@JoinColumn`：关联关系映射
   - 双向关联的JSON序列化无限递归解决方案：`@JsonIgnore` / `@JsonManagedReference+@JsonBackReference` / DTO

4. **Repository继承体系**：`JpaRepository<T, ID>` 提供20+内置方法，你只需定义接口无需实现

5. **方法命名查询**：`findByNameAndAgeGreaterThanOrderBySalaryDesc` → JPA自动生成SQL。记住：方法名太长就用`@Query`

6. **@Query查询**：JPQL（面向实体）vs 原生SQL（面向表），`@Modifying + @Transactional`用于写操作

7. **分页**：`PageRequest.of(0, 10)` → `Page<T>`，注意页码从0开始！

8. **JPA高级陷阱**：
   - 🛑 ddl-auto生产环境绝对只能用`validate`（`create`/`update`/`create-drop`可能导致数据全部丢失）
   - 脏检查：同一事务内修改实体自动UPDATE
   - N+1查询：`@EntityGraph`或`JOIN FETCH`解决
   - OSIV：前后端分离项目建议关闭（`open-in-view: false`）

9. **EMS v4双版本实战**：用MyBatis和JPA分别实现了同一个RESTful API，真实感受两者的差异

---

## 思考题

1. `@GeneratedValue`的默认策略是`AUTO`。在MySQL中，如果使用默认策略，会发生什么？为什么？

2. 以下代码存在什么问题？

   ```java
   @Entity
   public class Employee {
       @Enumerated
       private EmployeeStatus status;  // EmployeeStatus: ACTIVE, INACTIVE, RESIGNED
   }
   ```

3. 假设`Department`和`Employee`是双向关联（`@OneToMany` + `@ManyToOne`），以下接口为什么会导致StackOverflowError？给出至少两种解决方案。

   ```java
   @GetMapping("/{id}")
   public Department getDept(@PathVariable Long id) {
       return departmentRepository.findById(id).orElseThrow();
   }
   ```

4. 解释JPA的N+1查询问题：什么场景下会发生？如何用`@EntityGraph`解决？

5. 某项目`application.yml`中配置了`spring.jpa.hibernate.ddl-auto: create`。项目在生产环境运行一个月后需要重启服务器。重启后会发生什么？这个配置在生产环境应该改成什么？

---

<details>
<summary>思考题参考答案（点击展开）</summary>

**第1题**：

`AUTO`策略在MySQL中会被Hibernate选为`TABLE`策略，因为MySQL没有原生的SEQUENCE对象。

后果：
1. Hibernate会自动创建一张`hibernate_sequence`表来模拟序列
2. 所有使用`AUTO`策略的实体都从这张表获取ID，成为全局瓶颈
3. 数据库中出现一张用户没有显式创建的"幽灵表"，增加维护困惑

解决方案：明确写 `@GeneratedValue(strategy = GenerationType.IDENTITY)`。

**第2题**：

`@Enumerated` 默认使用 `EnumType.ORDINAL`，按枚举定义顺序存储数字（ACTIVE=0, INACTIVE=1, RESIGNED=2）。

问题：如果在ACTIVE前面插入一个新枚举值（如PENDING），枚举顺序变为（PENDING=0, ACTIVE=1, INACTIVE=2, RESIGNED=3），原来数据库中存的0（曾是ACTIVE）现在映射为PENDING，全部数据映射错乱。

修正：`@Enumerated(EnumType.STRING)`。

**第3题**：

`Department`对象包含`List<Employee>`，每个`Employee`又引用回`Department`。Jackson在序列化`Department`为JSON时：
Department → employees[0] → department → employees[0] → ...（无限递归）→ StackOverflowError

解决方案（三选一）：
- `@JsonIgnore`：在不需要序列化的那端（通常是`Department.employees`）加`@JsonIgnore`
- `@JsonManagedReference` + `@JsonBackReference`：正向用Managed、回引用用Back
- **DTO**（生产推荐）：不直接返回Entity，而是转换为不包含回引用的DTO对象

**第4题**：

N+1问题场景：查询N个部门（1条SQL），然后遍历每个部门获取其员工列表时，每次访问`dept.getEmployees()`都触发一条新SQL（N条SQL），总共1+N条。

`@EntityGraph`解决方案：

```java
@EntityGraph(attributePaths = {"employees"})
@Query("SELECT d FROM Department d")
List<Department> findAllWithEmployees();
```

这会生成一条带LEFT JOIN FETCH的SQL，一次性查出所有部门和员工。

**第5题**：

重启后，Hibernate会在启动时执行：
1. `DROP TABLE employee`（以及其他所有被JPA管理的表）
2. `CREATE TABLE employee`（重新建表）
3. 结果：**一个月积累的所有数据全部丢失！**

生产环境应该改为：`spring.jpa.hibernate.ddl-auto: validate`（或`none`）。同时所有DDL变更统一通过Flyway或Liquibase进行版本管理。

</details>

---

> **下一篇预告**：第15章将正式进入Spring Boot的世界！我们将学习Spring Boot的设计哲学——"约定优于配置"，理解`@SpringBootApplication`自动配置背后的原理，创建第一个Spring Boot项目，彻底告别繁重的XML配置。
>
> **学习路线回顾**：
> - 第8章：SQL → 你学会了怎么操作数据库
> - 第9章：JDBC → 你学会了Java怎么连接数据库（手动）
> - 第13章：MyBatis → 你学会了半自动化的SQL映射
> - 第14章：JPA → 你学会了全自动化的ORM
>
> **你现在拥有了双持久化技能**：面对复杂报表你可以用MyBatis手写优化SQL，面对标准CRUD你可以用JPA享受零SQL开发的快感。接下来，Spring Boot会将这一切整合到一起——自动配置、起步依赖、内嵌服务器，让开发体验进入一个全新境界。
>
> **关于EMS项目**：本章的EMS v4同时实现了MyBatis版和JPA版。你可以根据实际需求选择其中一个方案继续开发（第15-19章的Spring Boot版本），也可以保留两个方案作为参考。在后续章节中，我们会逐步为EMS添加权限管理、缓存优化、前端界面等功能，最终打造一个生产级的全栈项目。