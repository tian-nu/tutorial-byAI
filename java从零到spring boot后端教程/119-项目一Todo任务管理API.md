# 119-项目一：Todo任务管理API

> 💡 本章你会做出一个**完整的 Todo 任务管理 API 系统**。完成后的效果：用 Postman 或 curl 发送请求，就能创建、查询、修改、删除待办任务，返回统一的 JSON 响应格式，参数校验不通过时返回清晰的错误信息。这是一个麻雀虽小五脏俱全的 CRUD 项目，你将完整经历 Entity → Repository → Service → Controller → 统一响应 → 异常处理 → 单元测试的全流程。

---

## 本章目标
- 创建完整的 Spring Boot CRUD 项目
- 实现统一响应格式（Result 类）
- 实现全局异常处理（@RestControllerAdvice）
- 使用 Bean Validation 做参数校验
- 编写 JUnit 5 单元测试
- 项目结构清晰、代码可直接运行

---

## 119.1 项目初始化

### 创建项目

用 Spring Initializr（https://start.spring.io）创建：

```
Project：     Maven
Language：    Java
Spring Boot： 3.2.5
Group：       com.example
Artifact：    todo
Dependencies：Spring Web, Spring Data JPA, H2 Database, Lombok, Validation
```

### pom.xml 关键依赖

```xml
<dependencies>
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-web</artifactId>
    </dependency>
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-data-jpa</artifactId>
    </dependency>
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-validation</artifactId>
    </dependency>
    <dependency>
        <groupId>com.h2database</groupId>
        <artifactId>h2</artifactId>
        <scope>runtime</scope>
    </dependency>
    <dependency>
        <groupId>org.projectlombok</groupId>
        <artifactId>lombok</artifactId>
        <optional>true</optional>
    </dependency>
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-test</artifactId>
        <scope>test</scope>
    </dependency>
</dependencies>
```

### application.yml

```yaml
spring:
  datasource:
    url: jdbc:h2:mem:tododb
    driver-class-name: org.h2.Driver
    username: sa
    password:
  h2:
    console:
      enabled: true
      path: /h2-console
  jpa:
    hibernate:
      ddl-auto: create-drop
    show-sql: true
```

---

## 119.2 数据库 DDL（JPA 自动生成）

本章使用 JPA 的 `ddl-auto: create-drop`，实体类即 DDL。对应的 SQL 等价于：

```sql
CREATE TABLE todo (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description VARCHAR(1000),
    completed BOOLEAN DEFAULT FALSE,
    priority VARCHAR(20) DEFAULT 'MEDIUM',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);
```

---

## 119.3 项目结构

```
src/main/java/com/example/todo/
├── TodoApplication.java
├── entity/
│   └── Todo.java
├── repository/
│   └── TodoRepository.java
├── service/
│   ├── TodoService.java
│   └── impl/
│       └── TodoServiceImpl.java
├── controller/
│   └── TodoController.java
├── dto/
│   ├── TodoCreateRequest.java
│   └── TodoUpdateRequest.java
├── common/
│   ├── Result.java
│   └── GlobalExceptionHandler.java
└── exception/
    └── ResourceNotFoundException.java
```

---

## 119.4 统一响应格式

```java
package com.example.todo.common;

import com.fasterxml.jackson.annotation.JsonInclude;
import lombok.AllArgsConstructor;
import lombok.Data;

@Data
@AllArgsConstructor
@JsonInclude(JsonInclude.Include.NON_NULL)
public class Result<T> {

    private int code;
    private String message;
    private T data;

    public static <T> Result<T> success(T data) {
        return new Result<>(200, "success", data);
    }

    public static <T> Result<T> success(String message, T data) {
        return new Result<>(200, message, data);
    }

    public static <T> Result<T> error(int code, String message) {
        return new Result<>(code, message, null);
    }

    public static <T> Result<T> error(String message) {
        return new Result<>(500, message, null);
    }
}
```

返回示例：

```json
{
    "code": 200,
    "message": "success",
    "data": {
        "id": 1,
        "title": "完成Spring Boot教程",
        "completed": false
    }
}
```

---

## 119.5 Entity

```java
package com.example.todo.entity;

import jakarta.persistence.*;
import lombok.Data;
import java.time.LocalDateTime;

@Data
@Entity
@Table(name = "todo")
public class Todo {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, length = 200)
    private String title;

    @Column(length = 1000)
    private String description;

    @Column(nullable = false)
    private Boolean completed = false;

    @Column(length = 20)
    private String priority = "MEDIUM";

    @Column(name = "created_at", updatable = false)
    private LocalDateTime createdAt;

    @Column(name = "updated_at")
    private LocalDateTime updatedAt;

    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
        updatedAt = LocalDateTime.now();
    }

    @PreUpdate
    protected void onUpdate() {
        updatedAt = LocalDateTime.now();
    }
}
```

---

## 119.6 DTO

```java
package com.example.todo.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;
import lombok.Data;

@Data
public class TodoCreateRequest {

    @NotBlank(message = "标题不能为空")
    @Size(max = 200, message = "标题长度不能超过200")
    private String title;

    @Size(max = 1000, message = "描述长度不能超过1000")
    private String description;

    private String priority = "MEDIUM";
}
```

```java
package com.example.todo.dto;

import lombok.Data;

@Data
public class TodoUpdateRequest {

    @Size(max = 200, message = "标题长度不能超过200")
    private String title;

    @Size(max = 1000, message = "描述长度不能超过1000")
    private String description;

    private Boolean completed;

    private String priority;
}
```

---

## 119.7 Repository

```java
package com.example.todo.repository;

import com.example.todo.entity.Todo;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;

public interface TodoRepository extends JpaRepository<Todo, Long> {

    List<Todo> findByCompleted(Boolean completed);

    List<Todo> findByPriority(String priority);

    List<Todo> findByTitleContaining(String keyword);

    long countByCompleted(Boolean completed);
}
```

---

## 119.8 Service

```java
package com.example.todo.service;

import com.example.todo.dto.TodoCreateRequest;
import com.example.todo.dto.TodoUpdateRequest;
import com.example.todo.entity.Todo;
import java.util.List;

public interface TodoService {

    Todo create(TodoCreateRequest request);

    Todo findById(Long id);

    List<Todo> findAll(Boolean completed, String keyword);

    Todo update(Long id, TodoUpdateRequest request);

    void delete(Long id);

    long countByStatus(Boolean completed);
}
```

```java
package com.example.todo.service.impl;

import com.example.todo.dto.TodoCreateRequest;
import com.example.todo.dto.TodoUpdateRequest;
import com.example.todo.entity.Todo;
import com.example.todo.exception.ResourceNotFoundException;
import com.example.todo.repository.TodoRepository;
import com.example.todo.service.TodoService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
@RequiredArgsConstructor
@Transactional
public class TodoServiceImpl implements TodoService {

    private final TodoRepository todoRepository;

    @Override
    public Todo create(TodoCreateRequest request) {
        Todo todo = new Todo();
        todo.setTitle(request.getTitle());
        todo.setDescription(request.getDescription());
        todo.setPriority(request.getPriority() != null ? request.getPriority() : "MEDIUM");
        return todoRepository.save(todo);
    }

    @Override
    @Transactional(readOnly = true)
    public Todo findById(Long id) {
        return todoRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("Todo not found with id: " + id));
    }

    @Override
    @Transactional(readOnly = true)
    public List<Todo> findAll(Boolean completed, String keyword) {
        if (completed != null && keyword != null) {
            return todoRepository.findByTitleContaining(keyword)
                    .stream()
                    .filter(t -> t.getCompleted().equals(completed))
                    .toList();
        }
        if (completed != null) {
            return todoRepository.findByCompleted(completed);
        }
        if (keyword != null && !keyword.isBlank()) {
            return todoRepository.findByTitleContaining(keyword);
        }
        return todoRepository.findAll();
    }

    @Override
    public Todo update(Long id, TodoUpdateRequest request) {
        Todo todo = findById(id);

        if (request.getTitle() != null) {
            todo.setTitle(request.getTitle());
        }
        if (request.getDescription() != null) {
            todo.setDescription(request.getDescription());
        }
        if (request.getCompleted() != null) {
            todo.setCompleted(request.getCompleted());
        }
        if (request.getPriority() != null) {
            todo.setPriority(request.getPriority());
        }

        return todoRepository.save(todo);
    }

    @Override
    public void delete(Long id) {
        Todo todo = findById(id);
        todoRepository.delete(todo);
    }

    @Override
    @Transactional(readOnly = true)
    public long countByStatus(Boolean completed) {
        return todoRepository.countByCompleted(completed);
    }
}
```

---

## 119.9 异常类与全局异常处理

```java
package com.example.todo.exception;

public class ResourceNotFoundException extends RuntimeException {
    public ResourceNotFoundException(String message) {
        super(message);
    }
}
```

```java
package com.example.todo.common;

import com.example.todo.exception.ResourceNotFoundException;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.ResponseStatus;
import org.springframework.web.bind.annotation.RestControllerAdvice;

import java.util.HashMap;
import java.util.Map;

@RestControllerAdvice
public class GlobalExceptionHandler {

    @ExceptionHandler(ResourceNotFoundException.class)
    @ResponseStatus(HttpStatus.NOT_FOUND)
    public Result<Void> handleNotFound(ResourceNotFoundException ex) {
        return Result.error(404, ex.getMessage());
    }

    @ExceptionHandler(MethodArgumentNotValidException.class)
    @ResponseStatus(HttpStatus.BAD_REQUEST)
    public Result<Map<String, String>> handleValidation(MethodArgumentNotValidException ex) {
        Map<String, String> errors = new HashMap<>();
        ex.getBindingResult().getFieldErrors().forEach(error ->
                errors.put(error.getField(), error.getDefaultMessage())
        );
        return new Result<>(400, "参数校验失败", errors);
    }

    @ExceptionHandler(Exception.class)
    @ResponseStatus(HttpStatus.INTERNAL_SERVER_ERROR)
    public Result<Void> handleGeneral(Exception ex) {
        return Result.error(500, "服务器内部错误: " + ex.getMessage());
    }
}
```

---

## 119.10 Controller

```java
package com.example.todo.controller;

import com.example.todo.common.Result;
import com.example.todo.dto.TodoCreateRequest;
import com.example.todo.dto.TodoUpdateRequest;
import com.example.todo.entity.Todo;
import com.example.todo.service.TodoService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/todos")
@RequiredArgsConstructor
public class TodoController {

    private final TodoService todoService;

    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    public Result<Todo> create(@Valid @RequestBody TodoCreateRequest request) {
        Todo todo = todoService.create(request);
        return Result.success("创建成功", todo);
    }

    @GetMapping
    public Result<List<Todo>> list(
            @RequestParam(required = false) Boolean completed,
            @RequestParam(required = false) String keyword) {
        List<Todo> todos = todoService.findAll(completed, keyword);
        return Result.success(todos);
    }

    @GetMapping("/{id}")
    public Result<Todo> getById(@PathVariable Long id) {
        Todo todo = todoService.findById(id);
        return Result.success(todo);
    }

    @PutMapping("/{id}")
    public Result<Todo> update(@PathVariable Long id,
                                @Valid @RequestBody TodoUpdateRequest request) {
        Todo todo = todoService.update(id, request);
        return Result.success("更新成功", todo);
    }

    @DeleteMapping("/{id}")
    @ResponseStatus(HttpStatus.NO_CONTENT)
    public Result<Void> delete(@PathVariable Long id) {
        todoService.delete(id);
        return Result.success("删除成功", null);
    }

    @GetMapping("/stats")
    public Result<java.util.Map<String, Long>> stats() {
        long total = todoService.countByStatus(null);
        long completed = todoService.countByStatus(true);
        long pending = todoService.countByStatus(false);
        return Result.success(java.util.Map.of(
                "total", total,
                "completed", completed,
                "pending", pending
        ));
    }
}
```

---

## 119.11 主启动类

```java
package com.example.todo;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class TodoApplication {
    public static void main(String[] args) {
        SpringApplication.run(TodoApplication.class, args);
    }
}
```

---

## 119.12 运行与验证

### 启动

```bash
mvn spring-boot:run
```

### 用 curl 测试

```bash
# 创建任务
curl -X POST http://localhost:8080/api/todos \
  -H "Content-Type: application/json" \
  -d '{"title":"学习Spring Boot","priority":"HIGH"}'

# 查询所有
curl http://localhost:8080/api/todos

# 查询单个
curl http://localhost:8080/api/todos/1

# 搜索
curl "http://localhost:8080/api/todos?keyword=Spring"

# 标记完成
curl -X PUT http://localhost:8080/api/todos/1 \
  -H "Content-Type: application/json" \
  -d '{"completed":true}'

# 统计
curl http://localhost:8080/api/todos/stats

# 删除
curl -X DELETE http://localhost:8080/api/todos/1

# 测试校验（标题为空）
curl -X POST http://localhost:8080/api/todos \
  -H "Content-Type: application/json" \
  -d '{"title":""}'
```

---

## 119.13 单元测试

```java
package com.example.todo.service.impl;

import com.example.todo.dto.TodoCreateRequest;
import com.example.todo.dto.TodoUpdateRequest;
import com.example.todo.entity.Todo;
import com.example.todo.exception.ResourceNotFoundException;
import com.example.todo.repository.TodoRepository;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.util.Optional;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class TodoServiceImplTest {

    @Mock
    private TodoRepository todoRepository;

    @InjectMocks
    private TodoServiceImpl todoService;

    private TodoCreateRequest createRequest;
    private Todo todo;

    @BeforeEach
    void setUp() {
        createRequest = new TodoCreateRequest();
        createRequest.setTitle("测试任务");
        createRequest.setPriority("HIGH");

        todo = new Todo();
        todo.setId(1L);
        todo.setTitle("测试任务");
        todo.setPriority("HIGH");
        todo.setCompleted(false);
    }

    @Test
    @DisplayName("创建Todo——正常输入应返回保存后的Todo")
    void create_WithValidRequest_ShouldReturnSavedTodo() {
        when(todoRepository.save(any(Todo.class))).thenReturn(todo);

        Todo result = todoService.create(createRequest);

        assertNotNull(result);
        assertEquals("测试任务", result.getTitle());
        assertEquals("HIGH", result.getPriority());
        verify(todoRepository, times(1)).save(any(Todo.class));
    }

    @Test
    @DisplayName("根据ID查询——存在时应返回Todo")
    void findById_WhenExists_ShouldReturnTodo() {
        when(todoRepository.findById(1L)).thenReturn(Optional.of(todo));

        Todo result = todoService.findById(1L);

        assertEquals(1L, result.getId());
        assertEquals("测试任务", result.getTitle());
    }

    @Test
    @DisplayName("根据ID查询——不存在时应抛异常")
    void findById_WhenNotExists_ShouldThrowException() {
        when(todoRepository.findById(99L)).thenReturn(Optional.empty());

        assertThrows(ResourceNotFoundException.class,
                () -> todoService.findById(99L));
    }

    @Test
    @DisplayName("更新Todo——修改标题和完成状态")
    void update_ShouldUpdateFields() {
        when(todoRepository.findById(1L)).thenReturn(Optional.of(todo));
        when(todoRepository.save(any(Todo.class))).thenReturn(todo);

        TodoUpdateRequest updateRequest = new TodoUpdateRequest();
        updateRequest.setTitle("更新后的标题");
        updateRequest.setCompleted(true);

        Todo result = todoService.update(1L, updateRequest);

        assertEquals("更新后的标题", result.getTitle());
        assertTrue(result.getCompleted());
    }

    @Test
    @DisplayName("删除Todo——存在时应调用delete")
    void delete_WhenExists_ShouldCallDelete() {
        when(todoRepository.findById(1L)).thenReturn(Optional.of(todo));
        doNothing().when(todoRepository).delete(todo);

        todoService.delete(1L);

        verify(todoRepository, times(1)).delete(todo);
    }
}
```

---

## 119.14 完整代码清单

| 文件 | 路径 |
|------|------|
| 启动类 | `src/main/java/com/example/todo/TodoApplication.java` |
| Entity | `src/main/java/com/example/todo/entity/Todo.java` |
| Repository | `src/main/java/com/example/todo/repository/TodoRepository.java` |
| Service 接口 | `src/main/java/com/example/todo/service/TodoService.java` |
| Service 实现 | `src/main/java/com/example/todo/service/impl/TodoServiceImpl.java` |
| Controller | `src/main/java/com/example/todo/controller/TodoController.java` |
| DTO-创建请求 | `src/main/java/com/example/todo/dto/TodoCreateRequest.java` |
| DTO-更新请求 | `src/main/java/com/example/todo/dto/TodoUpdateRequest.java` |
| 统一响应 | `src/main/java/com/example/todo/common/Result.java` |
| 异常处理 | `src/main/java/com/example/todo/common/GlobalExceptionHandler.java` |
| 自定义异常 | `src/main/java/com/example/todo/exception/ResourceNotFoundException.java` |
| 测试 | `src/test/java/com/example/todo/service/impl/TodoServiceImplTest.java` |
| 配置 | `src/main/resources/application.yml` |

---

## 119.15 完成效果

成功启动后：
1. **创建任务**：POST `/api/todos` → 返回 `{"code":200,"message":"创建成功","data":{...}}`
2. **查询列表**：GET `/api/todos` → 返回所有任务
3. **搜索筛选**：GET `/api/todos?completed=false&keyword=Spring` → 筛选未完成含关键词的任务
4. **参数校验**：提交空标题 → 返回 `{"code":400,"message":"参数校验失败","data":{"title":"标题不能为空"}}`
5. **ID 不存在**：GET `/api/todos/999` → 返回 404 错误

---

## 小结

| 知识点 | 在本项目中的体现 |
|--------|-----------------|
| JPA Entity | `@Entity`, `@Id`, `@GeneratedValue`, `@PrePersist`, `@PreUpdate` |
| Repository | `JpaRepository` + 自定义查询方法 |
| Service 分层 | 接口 + 实现类，`@Transactional` |
| DTO | 分离请求体与实体，`@Valid` 校验 |
| 统一响应 | `Result<T>` 封装 code/message/data |
| 全局异常 | `@RestControllerAdvice` + `@ExceptionHandler` |
| 单元测试 | JUnit 5 + Mockito，Mock Repository |

---

## 自测题

1. 为什么要把请求体（DTO）和实体（Entity）分开，而不直接用 Entity 接收请求？
2. `@RestControllerAdvice` 的工作原理是什么？
3. 如果要把 H2 数据库换成 MySQL，需要改哪些地方？

<details>
<summary>点击查看答案</summary>

1. ①安全性：避免客户端直接修改不该改的字段（如 id、createdAt）；②灵活：DTO 可以组合多个实体的字段，校验规则也不一样；③演进：Entity 改变不影响 API 契约。
2. `@RestControllerAdvice` 是 Spring AOP 的应用——它拦截所有 Controller 抛出的异常，按 `@ExceptionHandler` 匹配异常类型，将异常转换为统一格式的 JSON 响应，而不是让 Tomcat 返回默认的 500 错误页。
3. ①`application.yml` 中改 `spring.datasource.url/username/password/driver-class-name`；②`pom.xml` 中把 H2 依赖换成 MySQL Connector；③移除 `spring.h2.console` 配置；④把 `spring.jpa.hibernate.ddl-auto` 改为 `validate` 或 `update`（生产慎用 auto DDL）。
</details>