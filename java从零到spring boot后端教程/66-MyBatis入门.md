# 第66章 · MyBatis入门

> **📢 第64章学了JDBC走路的每一步，第65章穿了不会磨脚的鞋（连接池）。这章骑上自行车——MyBatis。** 你不再需要手动遍历ResultSet、手动关闭Connection，但你还是要自己写SQL。MyBatis是半自动的ORM框架：SQL你自己写，结果映射帮你做。相比于全自动的JPA（第67章），MyBatis给了你对SQL的完全控制权。

> "回忆一下第64章的JDBC代码——30行代码查一条用户记录，其中20行是样板代码。MyBatis说：'SQL你写，剩下的脏活累活我来。'你只需写一个接口方法+一条SQL，MyBatis替你搞定连接获取、参数设置、结果映射、连接归还。"

---

## 66.1 MyBatis是什么

MyBatis是一个**半自动**的持久层框架。它是对JDBC的封装，但绝不隐藏SQL——你需要手写SQL，MyBatis帮你做的是：

- 自动开/关连接（配合连接池）
- 自动参数设置（把Java对象属性映射到SQL的 `?` 参数）
- 自动结果映射（把ResultSet的列映射到Java对象属性）
- 动态SQL（根据条件拼接WHERE子句，不用写一堆if-else）

```
JPA（全自动）：你定义Java对象 → 框架自动生成SQL
MyBatis（半自动）：你自己写SQL → 框架帮你传参和映射结果
JDBC（全手动）：所有事情你都得自己干
```

> 💡 什么场景选MyBatis而不是JPA？当你的SQL非常复杂（多表关联、复杂报表、需要精细的性能调优）、或者数据库结构已存在且不可控（对接遗留系统）时，MyBatis是更好的选择。

---

## 66.2 项目配置

### 66.2.1 Maven依赖

```xml
<dependencies>
    <!-- Spring Boot MyBatis Starter -->
    <dependency>
        <groupId>org.mybatis.spring.boot</groupId>
        <artifactId>mybatis-spring-boot-starter</artifactId>
        <version>3.0.3</version>
    </dependency>

    <!-- MySQL驱动 -->
    <dependency>
        <groupId>com.mysql</groupId>
        <artifactId>mysql-connector-j</artifactId>
        <version>8.0.33</version>
    </dependency>
</dependencies>
```

### 66.2.2 application.yml

```yaml
spring:
  datasource:
    url: jdbc:mysql://localhost:3306/my_shop?useSSL=false&serverTimezone=Asia/Shanghai
    username: root
    password: your_password_here
    driver-class-name: com.mysql.cj.jdbc.Driver

mybatis:
  mapper-locations: classpath:mapper/*.xml   # XML映射文件的位置
  type-aliases-package: com.example.entity    # 实体类别名包
  configuration:
    map-underscore-to-camel-case: true        # 下划线转驼峰：user_name → userName
    log-impl: org.apache.ibatis.logging.stdout.StdOutImpl  # SQL日志输出
```

---

## 66.3 两种映射方式：XML vs 注解

MyBatis提供两种方式定义SQL映射：XML文件和注解。你看到的教程两者都会讲，实际项目中可以混合使用——简单查询用注解，复杂SQL用XML。

---

## 66.4 注解方式（简单查询首选）

### 66.4.1 实体类

```java
package com.example.entity;

public class User {
    private Long id;
    private String username;
    private String email;
    private Integer age;

    // 必须有无参构造器和getter/setter
    public User() {}

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }

    public String getUsername() { return username; }
    public void setUsername(String username) { this.username = username; }

    public String getEmail() { return email; }
    public void setEmail(String email) { this.email = email; }

    public Integer getAge() { return age; }
    public void setAge(Integer age) { this.age = age; }
}
```

### 66.4.2 Mapper接口

```java
package com.example.mapper;

import com.example.entity.User;
import org.apache.ibatis.annotations.*;

import java.util.List;

@Mapper  // 告诉MyBatis这是一个Mapper接口
public interface UserMapper {

    @Select("SELECT id, username, email, age FROM users WHERE id = #{id}")
    User findById(Long id);

    @Select("SELECT id, username, email, age FROM users")
    List<User> findAll();

    @Select("SELECT id, username, email, age FROM users WHERE age > #{minAge}")
    List<User> findByAgeGreaterThan(@Param("minAge") int minAge);

    @Insert("INSERT INTO users (username, email, age) VALUES (#{username}, #{email}, #{age})")
    @Options(useGeneratedKeys = true, keyProperty = "id")  // 回填自增主键
    int insert(User user);

    @Update("UPDATE users SET username = #{username}, email = #{email}, age = #{age} WHERE id = #{id}")
    int update(User user);

    @Delete("DELETE FROM users WHERE id = #{id}")
    int deleteById(Long id);
}
```

### 66.4.3 #{} vs ${}

这是MyBatis中最容易出错的地方：

| 符号 | 原理 | 防SQL注入 | 用途 |
|------|------|----------|------|
| `#{}` | PreparedStatement的`?`占位符，参数被安全转义 | ✅ 安全 | 普通参数值 |
| `${}` | 字符串直接拼接，不做任何转义 | ❌ 危险 | 动态表名、动态列名、ORDER BY排序字段 |

```java
// ✅ 正确：参数值用 #{} （底层是PreparedStatement）
@Select("SELECT * FROM users WHERE username = #{username}")

// ❌ 危险：${} 直接拼接，可能被SQL注入
@Select("SELECT * FROM users WHERE username = '${username}'")

// ⚠️ 特殊情况：ORDER BY的动态字段只能用 ${}
// 但必须做白名单校验！
@Select("SELECT * FROM users ORDER BY ${sortField} ${sortOrder}")
// 调用前必须校验 sortField 只能是 "id"/"username"/"age" 之一
```

> 🚨 **`${}` 是SQL注入的温床。除非你100%确定参数来自可信源且做了白名单校验，否则永远用 `#{}`。**

---

## 66.5 XML方式（复杂SQL的首选）

### 66.5.1 Mapper接口

```java
package com.example.mapper;

import com.example.entity.User;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

import java.util.List;
import java.util.Map;

@Mapper
public interface UserXmlMapper {

    User findById(Long id);

    List<User> findByCondition(@Param("username") String username,
                               @Param("minAge") Integer minAge,
                               @Param("maxAge") Integer maxAge);

    List<User> findByIds(@Param("ids") List<Long> ids);

    int batchInsert(@Param("users") List<User> users);
}
```

### 66.5.2 XML映射文件

在 `src/main/resources/mapper/UserXmlMapper.xml`：

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE mapper PUBLIC "-//mybatis.org//DTD Mapper 3.0//EN"
        "http://mybatis.org/dtd/mybatis-3-mapper.dtd">

<mapper namespace="com.example.mapper.UserXmlMapper">

    <!-- 结果映射：把数据库列名和Java属性对应起来 -->
    <resultMap id="userMap" type="com.example.entity.User">
        <id column="id" property="id"/>
        <result column="username" property="username"/>
        <result column="email" property="email"/>
        <result column="age" property="age"/>
    </resultMap>

    <!-- 基础查询 -->
    <select id="findById" resultMap="userMap">
        SELECT id, username, email, age
        FROM users
        WHERE id = #{id}
    </select>

    <!-- 动态SQL：根据传入参数动态拼接WHERE条件 -->
    <select id="findByCondition" resultMap="userMap">
        SELECT id, username, email, age
        FROM users
        <where>
            <if test="username != null and username != ''">
                AND username LIKE CONCAT('%', #{username}, '%')
            </if>
            <if test="minAge != null">
                AND age &gt;= #{minAge}
            </if>
            <if test="maxAge != null">
                AND age &lt;= #{maxAge}
            </if>
        </where>
        ORDER BY id DESC
    </select>

    <!-- foreach：批量ID查询 -->
    <select id="findByIds" resultMap="userMap">
        SELECT id, username, email, age
        FROM users
        WHERE id IN
        <foreach collection="ids" item="id" open="(" separator="," close=")">
            #{id}
        </foreach>
    </select>

    <!-- 批量插入 -->
    <insert id="batchInsert" useGeneratedKeys="true" keyProperty="id">
        INSERT INTO users (username, email, age) VALUES
        <foreach collection="users" item="user" separator=",">
            (#{user.username}, #{user.email}, #{user.age})
        </foreach>
    </insert>

</mapper>
```

### 66.5.3 动态SQL标签速查

| 标签 | 作用 | 示例 |
|------|------|------|
| `<if>` | 条件判断 | `<if test="name != null"> AND name = #{name} </if>` |
| `<where>` | 自动处理AND前缀，全部条件为空时不生成WHERE | 见上例 |
| `<set>` | UPDATE时自动处理逗号 | `<set> <if test="name!=null">name=#{name},</if> </set>` |
| `<foreach>` | 遍历集合 | 见上例的IN查询和批量插入 |
| `<choose>/<when>/<otherwise>` | 等同于switch-case-default | 多选一的条件 |
| `<trim>` | 自定义前缀/后缀处理 | 比where/set更灵活 |
| `<sql>` + `<include>` | SQL片段复用 | 避免重复写相同的列名列表 |

---

## 66.6 在Service层使用Mapper

```java
package com.example.service;

import com.example.entity.User;
import com.example.mapper.UserMapper;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
public class UserService {

    @Autowired
    private UserMapper userMapper;

    public User getUserById(Long id) {
        return userMapper.findById(id);
    }

    public List<User> getAllUsers() {
        return userMapper.findAll();
    }

    @Transactional
    public User createUser(User user) {
        userMapper.insert(user);
        // insert后user.getId()会自动回填数据库生成的自增ID
        return user;
    }

    @Transactional
    public void updateUser(User user) {
        int rows = userMapper.update(user);
        if (rows == 0) {
            throw new RuntimeException("用户不存在");
        }
    }

    @Transactional
    public void deleteUser(Long id) {
        userMapper.deleteById(id);
    }
}
```

---

## 66.7 MyBatis vs JDBC 代码量对比

| 操作 | JDBC（行） | MyBatis注解（行） |
|------|-----------|------------------|
| 查询单条 | 25 | 2（SQL注解+接口方法签名） |
| 查询列表 | 25 | 2 |
| 插入 | 20 | 4（含@Options） |
| 更新 | 20 | 2 |
| 删除 | 18 | 2 |
| 条件查询 | 30+ | 5（动态SQL） |

---

## 本章小结

| 概念 | 要点 |
|------|------|
| MyBatis | 半自动ORM框架，手写SQL+自动结果映射 |
| @Mapper | 标识MyBatis的Mapper接口 |
| #{} | 预编译占位符，安全，**永远用它存参数值** |
| ${} | 字符串直接拼接，危险，仅用于动态表名/列名且必须做白名单 |
| 动态SQL | if/where/set/foreach，解决复杂条件拼接 |
| XML映射 | 复杂SQL首选，支持resultMap和动态SQL |
| 注解映射 | 简单CRUD首选，代码和SQL放在一起更直观 |
| 定位 | 对SQL有完全控制权，适合复杂查询和遗留数据库 |

---

## 自测题

1. **`#{}` 和 `${}` 的区别是什么？什么场景下可以安全使用 `${}`？**

2. **MyBatis是"半自动"ORM框架，这个"半自动"体现在哪里？和JDBC、JPA比较。**

3. **写出MyBatis动态SQL：根据可选的 `status` 和 `minAmount` 参数查询订单，如果都不传则查全部。**

<details>
<summary>参考答案（做完再看）</summary>

1. `#{}` 底层使用PreparedStatement的`?`占位符，参数被安全转义，防SQL注入。`${}` 是字符串直接拼接，不转义，有SQL注入风险。`${}` 只能在以下场景使用，且必须做白名单校验：动态表名、动态列名、ORDER BY/GROUP BY后的排序字段名。例如 `ORDER BY ${validatedField}`，validatedField必须来自一个允许值的白名单（如只允许"id"/"username"/"createTime"）。

2. "半自动"体现在：MyBatis帮你做连接管理、参数映射、结果映射（自动化的部分），但SQL是你自己写的（手动部分）。对比：JDBC是全手动（什么都自己干），JPA是全自动（定义Java对象后框架自动生成SQL）。MyBatis在中间——你控制SQL但不用写样板代码。

3. ```xml
<select id="findOrders" resultMap="orderMap">
    SELECT * FROM orders
    <where>
        <if test="status != null and status != ''">
            AND status = #{status}
        </if>
        <if test="minAmount != null">
            AND amount >= #{minAmount}
        </if>
    </where>
</select>
```
`<where>` 标签自动处理：如果两个条件都不传，不生成WHERE子句；如果只传一个，自动去除多余的AND。
</details>