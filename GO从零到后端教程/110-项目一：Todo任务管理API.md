# 第110章 · 项目一：Todo任务管理API

> "所有知识点都学完了——Go语言语法、Gin框架、GORM操作数据库、中间件、测试、部署……现在让我们把它们串起来，从零搭建一个完整的项目。第一个项目选Todo任务管理——它是最经典的练手项目，就像一个厨师学完刀工和火候后做的第一道番茄炒蛋：简单，但涵盖所有基本功。"

---

## 110.1 本篇概述：六个项目，六层台阶

在进入第一个项目之前，先看一眼我们接下来六章的路线图：

| 章节 | 项目 | 难度 | 核心知识点 | 为什么做这个 |
|------|------|------|-----------|-------------|
| 110 | Todo任务管理 | ⭐ | CRUD + Gin + GORM + 单元测试 | 把Go Web开发的基本功跑通 |
| 111 | 用户认证系统 | ⭐⭐ | JWT + bcrypt + 文件上传 | 任何正经项目的标配 |
| 112 | 博客系统 | ⭐⭐⭐ | 多表关联 + RESTful设计 | 经典的"内容型"应用 |
| 113 | 电商秒杀系统 | ⭐⭐⭐⭐ | Redis + 高并发 + 防超卖 | 面试最爱问，真正考验并发功底 |
| 114 | IM即时通讯 | ⭐⭐⭐⭐ | WebSocket长连接 + 消息推送 | 实时系统的典型代表 |
| 115 | 微服务电商 | ⭐⭐⭐⭐⭐ | gRPC + 服务发现 + 分布式事务 | 架构升级，单体→微服务 |

从单体CRUD（Create/Read/Update/Delete，数据库基本增删改查操作，详见附录I）到分布式微服务，每一步都建立在前面打下的基础上。准备好了吗？让我们从最简单的Todo开始。

---

## 110.2 需求分析

### 这个项目要做什么

一个Todo任务管理API——就像你手机里的备忘录应用，但没有界面，只有接口。用户可以通过API：
- 创建一条任务（"明天下午3点开会"）
- 查看所有任务列表（分页）
- 查看单条任务详情
- 按关键词搜索任务
- 标记任务为已完成
- 删除任务

### 功能列表

| 序号 | 功能 | HTTP方法 | 路径 | 说明 |
|------|------|---------|------|------|
| 1 | 创建任务 | POST | /api/todos | 提交JSON创建新任务 |
| 2 | 任务列表 | GET | /api/todos | 分页查询，支持搜索 |
| 3 | 任务详情 | GET | /api/todos/:id | 查看单条任务 |
| 4 | 更新任务 | PUT | /api/todos/:id | 修改标题/内容/状态 |
| 5 | 完成任务 | PATCH | /api/todos/:id/done | 快捷标记完成 |
| 6 | 删除任务 | DELETE | /api/todos/:id | 软删除 |

### 不做什么（明确边界）

- 不做用户系统（那是第111章的事）
- 不做前端界面（纯API）
- 不做分类/标签（第112章博客系统会做）
- 不做定时提醒（超出练手范围）

这个项目就像学开车时先在停车场绕圈——不需要考虑交通规则和导航，只管方向盘、油门和刹车。

---

## 110.3 数据库设计

### 只有一张表：todos

对于Todo应用，一张表就够了。设计数据库就像设计衣柜——先想清楚你要放什么衣服，再设计格子的尺寸。

```sql
CREATE DATABASE IF NOT EXISTS todo_db
    DEFAULT CHARACTER SET utf8mb4
    DEFAULT COLLATE utf8mb4_unicode_ci;

USE todo_db;

CREATE TABLE todos (
    id          BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    title       VARCHAR(255)    NOT NULL,
    content     TEXT            DEFAULT NULL,
    status      TINYINT         NOT NULL DEFAULT 0,
    created_at  DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at  DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    deleted_at  DATETIME        DEFAULT NULL,
    PRIMARY KEY (id),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at),
    INDEX idx_deleted_at (deleted_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

### 字段说明

- `id`：自增主键，BIGINT足够你用一百年
- `title`：任务标题，必填（比如"买牛奶"）
- `content`：任务详细描述，可空（比如"去XX超市买XX牌全脂牛奶2升"）
- `status`：0=未完成，1=已完成。用TINYINT而不是字符串，查询更快
- `created_at`：创建时间，默认当前时间
- `updated_at`：更新时间，自动更新
- `deleted_at`：软删除标记。为NULL表示未删除，有值表示已删除。GORM的软删除机制就是靠这个字段

### 为什么索引选这几个

- `idx_status`：你经常要查"所有未完成的任务"——没有索引就是全表扫描
- `idx_created_at`：任务列表按时间排序，索引加速ORDER BY
- `idx_deleted_at`：GORM的软删除查询会自动加 `WHERE deleted_at IS NULL`，索引加速这个过滤

就像给书的目录加标签——知道哪些标签常用，就提前把它们标出来，翻书时就能直接跳过去。

---

## 110.4 项目结构

不像练Go语法时一个main.go搞定一切，正经项目要分目录。下面是Todo项目的目录树：

```
todo-api/
├── main.go                 # 入口：连接数据库、注册路由、启动服务
├── go.mod                  # Go模块定义
├── go.sum                  # 依赖版本锁定
├── config/
│   └── config.go           # 配置：数据库连接字符串、服务端口等
├── model/
│   └── todo.go             # GORM模型定义 + CRUD方法
├── handler/
│   └── todo.go             # HTTP处理函数：参数验证、调用model、返回响应
├── router/
│   └── router.go           # 路由注册
├── middleware/
│   └── recovery.go         # 全局异常恢复中间件（可选）
└── todo_test.go            # 集成测试
```

这个结构的核心思想是**分层**：就像餐厅分后厨（model）、服务员（handler）、接待台（router）——各司其职，出了问题也知道找谁。

- `model/`：只管数据库，外面的人不知道SQL
- `handler/`：只管HTTP，不知道数据库细节
- `router/`：只管路由映射，不碰业务逻辑

---

## 110.5 API设计

### 接口一览

所有接口返回统一的JSON格式：

```json
{
    "code": 200,
    "message": "success",
    "data": { ... }
}
```

如果出错：

```json
{
    "code": 400,
    "message": "title不能为空",
    "data": null
}
```

### 接口详细设计

#### 1. 创建任务 — POST /api/todos

请求体：
```json
{
    "title": "买牛奶",
    "content": "去XX超市买XX牌全脂牛奶2升"
}
```

响应：
```json
{
    "code": 201,
    "message": "创建成功",
    "data": {
        "id": 1,
        "title": "买牛奶",
        "content": "去XX超市买XX牌全脂牛奶2升",
        "status": 0,
        "created_at": "2025-01-01T10:00:00Z",
        "updated_at": "2025-01-01T10:00:00Z"
    }
}
```

#### 2. 任务列表 — GET /api/todos?page=1&page_size=10&keyword=牛奶&status=0

查询参数全部可选：
- `page`：页码，默认1
- `page_size`：每页条数，默认10，最大100
- `keyword`：搜索关键词（匹配title和content）
- `status`：按状态筛选（0/1）

响应：
```json
{
    "code": 200,
    "message": "success",
    "data": {
        "list": [ ... ],
        "total": 50,
        "page": 1,
        "page_size": 10
    }
}
```

#### 3. 任务详情 — GET /api/todos/:id

路由参数：`id`（任务ID）

响应：单个任务对象（同上data格式），404如果不存在。

#### 4. 更新任务 — PUT /api/todos/:id

请求体（全部可选，传什么改什么）：
```json
{
    "title": "买牛奶和面包",
    "content": "更新后的内容",
    "status": 1
}
```

#### 5. 完成任务 — PATCH /api/todos/:id/done

无需请求体。相当于快捷操作——不用传 `{"status":1}`，直接调这个接口。

#### 6. 删除任务 — DELETE /api/todos/:id

软删除，设置 `deleted_at`。

---

## 110.6 核心代码实现

### 第一步：初始化Go模块

```bash
mkdir todo-api && cd todo-api
go mod init todo-api
go get -u github.com/gin-gonic/gin
go get -u gorm.io/gorm
go get -u gorm.io/driver/mysql
```

### config/config.go — 配置管理

```go
package config

import "os"

type Config struct {
    DBHost     string
    DBPort     string
    DBUser     string
    DBPassword string
    DBName     string
    ServerPort string
}

func Load() *Config {
    return &Config{
        DBHost:     getEnv("DB_HOST", "127.0.0.1"),
        DBPort:     getEnv("DB_PORT", "3306"),
        DBUser:     getEnv("DB_USER", "root"),
        DBPassword: getEnv("DB_PASSWORD", ""),
        DBName:     getEnv("DB_NAME", "todo_db"),
        ServerPort: getEnv("SERVER_PORT", "8080"),
    }
}

func (c *Config) DSN() string {
    return c.DBUser + ":" + c.DBPassword +
        "@tcp(" + c.DBHost + ":" + c.DBPort + ")/" +
        c.DBName + "?charset=utf8mb4&parseTime=True&loc=Local"
}

func getEnv(key, defaultVal string) string {
    if val := os.Getenv(key); val != "" {
        return val
    }
    return defaultVal
}
```

用环境变量管理配置是正经项目的标配。这样同一份代码在开发环境和生产环境可以用不同的数据库，改配置不需要改代码。

### model/todo.go — 数据模型

```go
package model

import (
    "time"
    "gorm.io/gorm"
)

type Todo struct {
    ID        uint64         `gorm:"primaryKey" json:"id"`
    Title     string         `gorm:"size:255;not null" json:"title"`
    Content   string         `gorm:"type:text" json:"content"`
    Status    int8           `gorm:"default:0" json:"status"`
    CreatedAt time.Time      `json:"created_at"`
    UpdatedAt time.Time      `json:"updated_at"`
    DeletedAt gorm.DeletedAt `gorm:"index" json:"-"`
}

func (Todo) TableName() string {
    return "todos"
}

type CreateReq struct {
    Title   string `json:"title" binding:"required"`
    Content string `json:"content"`
}

type UpdateReq struct {
    Title   string `json:"title"`
    Content string `json:"content"`
    Status  *int8  `json:"status"`
}

type ListResp struct {
    List     []Todo `json:"list"`
    Total    int64  `json:"total"`
    Page     int    `json:"page"`
    PageSize int    `json:"page_size"`
}
```

注意 `Status` 字段用 `*int8`（指针）：因为Go的零值是0，如果不用指针，你无法区分"用户想设status=0"和"用户没传status字段"。就像你去奶茶店，"不加糖"（0）和"我没说"（nil）是两回事。

### model/todo.go — CRUD方法（继续）

```go
func CreateTodo(db *gorm.DB, req *CreateReq) (*Todo, error) {
    todo := &Todo{
        Title:   req.Title,
        Content: req.Content,
        Status:  0,
    }
    if err := db.Create(todo).Error; err != nil {
        return nil, err
    }
    return todo, nil
}

func GetTodoByID(db *gorm.DB, id uint64) (*Todo, error) {
    var todo Todo
    err := db.Where("id = ?", id).First(&todo).Error
    if err != nil {
        return nil, err
    }
    return &todo, nil
}

func ListTodos(db *gorm.DB, page, pageSize int, keyword string, status *int8) (*ListResp, error) {
    var todos []Todo
    var total int64

    query := db.Model(&Todo{})

    if keyword != "" {
        like := "%" + keyword + "%"
        query = query.Where("title LIKE ? OR content LIKE ?", like, like)
    }
    if status != nil {
        query = query.Where("status = ?", *status)
    }

    query.Count(&total)

    offset := (page - 1) * pageSize
    err := query.Order("created_at DESC").
        Offset(offset).
        Limit(pageSize).
        Find(&todos).Error
    if err != nil {
        return nil, err
    }

    return &ListResp{
        List:     todos,
        Total:    total,
        Page:     page,
        PageSize: pageSize,
    }, nil
}

func UpdateTodo(db *gorm.DB, id uint64, req *UpdateReq) (*Todo, error) {
    var todo Todo
    if err := db.First(&todo, id).Error; err != nil {
        return nil, err
    }

    updates := map[string]interface{}{}
    if req.Title != "" {
        updates["title"] = req.Title
    }
    if req.Content != "" {
        updates["content"] = req.Content
    }
    if req.Status != nil {
        updates["status"] = *req.Status
    }

    if len(updates) > 0 {
        if err := db.Model(&todo).Updates(updates).Error; err != nil {
            return nil, err
        }
    }

    db.First(&todo, id)
    return &todo, nil
}

func MarkDone(db *gorm.DB, id uint64) error {
    return db.Model(&Todo{}).Where("id = ?", id).
        Update("status", 1).Error
}

func DeleteTodo(db *gorm.DB, id uint64) error {
    return db.Delete(&Todo{}, id).Error
}
```

### handler/todo.go — HTTP处理函数

```go
package handler

import (
    "net/http"
    "strconv"
    "todo-api/model"

    "github.com/gin-gonic/gin"
    "gorm.io/gorm"
)

type TodoHandler struct {
    DB *gorm.DB
}

func NewTodoHandler(db *gorm.DB) *TodoHandler {
    return &TodoHandler{DB: db}
}

func (h *TodoHandler) Create(c *gin.Context) {
    var req model.CreateReq
    if err := c.ShouldBindJSON(&req); err != nil {
        c.JSON(http.StatusBadRequest, gin.H{
            "code":    400,
            "message": "参数错误: " + err.Error(),
            "data":    nil,
        })
        return
    }

    todo, err := model.CreateTodo(h.DB, &req)
    if err != nil {
        c.JSON(http.StatusInternalServerError, gin.H{
            "code":    500,
            "message": "创建失败",
            "data":    nil,
        })
        return
    }

    c.JSON(http.StatusCreated, gin.H{
        "code":    201,
        "message": "创建成功",
        "data":    todo,
    })
}

func (h *TodoHandler) List(c *gin.Context) {
    page, _ := strconv.Atoi(c.DefaultQuery("page", "1"))
    pageSize, _ := strconv.Atoi(c.DefaultQuery("page_size", "10"))
    if pageSize > 100 {
        pageSize = 100
    }
    if page < 1 {
        page = 1
    }

    keyword := c.Query("keyword")
    var status *int8
    if s := c.Query("status"); s != "" {
        v, err := strconv.Atoi(s)
        if err == nil && (v == 0 || v == 1) {
            sv := int8(v)
            status = &sv
        }
    }

    resp, err := model.ListTodos(h.DB, page, pageSize, keyword, status)
    if err != nil {
        c.JSON(http.StatusInternalServerError, gin.H{
            "code":    500,
            "message": "查询失败",
            "data":    nil,
        })
        return
    }

    c.JSON(http.StatusOK, gin.H{
        "code":    200,
        "message": "success",
        "data":    resp,
    })
}

func (h *TodoHandler) GetByID(c *gin.Context) {
    id, err := strconv.ParseUint(c.Param("id"), 10, 64)
    if err != nil {
        c.JSON(http.StatusBadRequest, gin.H{
            "code":    400,
            "message": "无效的ID",
            "data":    nil,
        })
        return
    }

    todo, err := model.GetTodoByID(h.DB, id)
    if err != nil {
        c.JSON(http.StatusNotFound, gin.H{
            "code":    404,
            "message": "任务不存在",
            "data":    nil,
        })
        return
    }

    c.JSON(http.StatusOK, gin.H{
        "code":    200,
        "message": "success",
        "data":    todo,
    })
}

func (h *TodoHandler) Update(c *gin.Context) {
    id, err := strconv.ParseUint(c.Param("id"), 10, 64)
    if err != nil {
        c.JSON(http.StatusBadRequest, gin.H{
            "code":    400,
            "message": "无效的ID",
            "data":    nil,
        })
        return
    }

    var req model.UpdateReq
    if err := c.ShouldBindJSON(&req); err != nil {
        c.JSON(http.StatusBadRequest, gin.H{
            "code":    400,
            "message": "参数错误",
            "data":    nil,
        })
        return
    }

    todo, err := model.UpdateTodo(h.DB, id, &req)
    if err != nil {
        c.JSON(http.StatusInternalServerError, gin.H{
            "code":    500,
            "message": "更新失败",
            "data":    nil,
        })
        return
    }

    c.JSON(http.StatusOK, gin.H{
        "code":    200,
        "message": "更新成功",
        "data":    todo,
    })
}

func (h *TodoHandler) MarkDone(c *gin.Context) {
    id, err := strconv.ParseUint(c.Param("id"), 10, 64)
    if err != nil {
        c.JSON(http.StatusBadRequest, gin.H{
            "code":    400,
            "message": "无效的ID",
            "data":    nil,
        })
        return
    }

    if err := model.MarkDone(h.DB, id); err != nil {
        c.JSON(http.StatusInternalServerError, gin.H{
            "code":    500,
            "message": "操作失败",
            "data":    nil,
        })
        return
    }

    c.JSON(http.StatusOK, gin.H{
        "code":    200,
        "message": "已标记为完成",
        "data":    nil,
    })
}

func (h *TodoHandler) Delete(c *gin.Context) {
    id, err := strconv.ParseUint(c.Param("id"), 10, 64)
    if err != nil {
        c.JSON(http.StatusBadRequest, gin.H{
            "code":    400,
            "message": "无效的ID",
            "data":    nil,
        })
        return
    }

    if err := model.DeleteTodo(h.DB, id); err != nil {
        c.JSON(http.StatusInternalServerError, gin.H{
            "code":    500,
            "message": "删除失败",
            "data":    nil,
        })
        return
    }

    c.JSON(http.StatusOK, gin.H{
        "code":    200,
        "message": "删除成功",
        "data":    nil,
    })
}
```

### router/router.go — 路由注册

```go
package router

import (
    "todo-api/handler"

    "github.com/gin-gonic/gin"
    "gorm.io/gorm"
)

func Setup(db *gorm.DB) *gin.Engine {
    r := gin.Default()

    h := handler.NewTodoHandler(db)

    api := r.Group("/api")
    {
        todos := api.Group("/todos")
        {
            todos.POST("", h.Create)
            todos.GET("", h.List)
            todos.GET("/:id", h.GetByID)
            todos.PUT("/:id", h.Update)
            todos.PATCH("/:id/done", h.MarkDone)
            todos.DELETE("/:id", h.Delete)
        }
    }

    return r
}
```

### main.go — 入口

```go
package main

import (
    "fmt"
    "log"
    "todo-api/config"
    "todo-api/model"
    "todo-api/router"

    "gorm.io/driver/mysql"
    "gorm.io/gorm"
)

func main() {
    cfg := config.Load()

    db, err := gorm.Open(mysql.Open(cfg.DSN()), &gorm.Config{})
    if err != nil {
        log.Fatalf("数据库连接失败: %v", err)
    }

    db.AutoMigrate(&model.Todo{})

    r := router.Setup(db)

    addr := fmt.Sprintf(":%s", cfg.ServerPort)
    log.Printf("服务启动在 http://localhost%s", addr)
    if err := r.Run(addr); err != nil {
        log.Fatalf("服务启动失败: %v", err)
    }
}
```

`AutoMigrate` 会自动根据模型结构创建/更新表结构——开发阶段非常方便。但生产环境建议手动管理数据库迁移（用专门的migration工具），因为AutoMigrate不会删除列、不会改列类型，容易留下历史包袱。

---

## 110.7 单元测试

测试不是"写完代码顺手写点测试"，而是"先想清楚这个函数该干什么，再验证它确实干了"。下面是对核心CRUD方法的测试：

```go
package main

import (
    "encoding/json"
    "net/http"
    "net/http/httptest"
    "strings"
    "testing"

    "github.com/gin-gonic/gin"
    "github.com/stretchr/testify/assert"
    "gorm.io/driver/sqlite"
    "gorm.io/gorm"
    "todo-api/handler"
    "todo-api/model"
    "todo-api/router"
)

func setupTestDB(t *testing.T) *gorm.DB {
    db, err := gorm.Open(sqlite.Open(":memory:"), &gorm.Config{})
    if err != nil {
        t.Fatalf("测试数据库初始化失败: %v", err)
    }
    db.AutoMigrate(&model.Todo{})
    return db
}

func TestCreateTodo(t *testing.T) {
    db := setupTestDB(t)
    r := setupTestRouter(db)

    body := `{"title":"测试任务","content":"这是一个测试"}`
    req := httptest.NewRequest("POST", "/api/todos", strings.NewReader(body))
    req.Header.Set("Content-Type", "application/json")
    w := httptest.NewRecorder()

    r.ServeHTTP(w, req)

    assert.Equal(t, http.StatusCreated, w.Code)

    var resp map[string]interface{}
    json.Unmarshal(w.Body.Bytes(), &resp)
    assert.Equal(t, float64(201), resp["code"])
}

func TestListTodos(t *testing.T) {
    db := setupTestDB(t)
    r := setupTestRouter(db)

    model.CreateTodo(db, &model.CreateReq{Title: "任务1", Content: "内容1"})
    model.CreateTodo(db, &model.CreateReq{Title: "任务2", Content: "内容2"})

    req := httptest.NewRequest("GET", "/api/todos?page=1&page_size=10", nil)
    w := httptest.NewRecorder()

    r.ServeHTTP(w, req)

    assert.Equal(t, http.StatusOK, w.Code)

    var resp map[string]interface{}
    json.Unmarshal(w.Body.Bytes(), &resp)
    data := resp["data"].(map[string]interface{})
    assert.Equal(t, float64(2), data["total"])
}

func TestGetTodoByID(t *testing.T) {
    db := setupTestDB(t)
    r := setupTestRouter(db)

    todo, _ := model.CreateTodo(db, &model.CreateReq{Title: "测试"})

    req := httptest.NewRequest("GET", "/api/todos/1", nil)
    w := httptest.NewRecorder()

    r.ServeHTTP(w, req)

    assert.Equal(t, http.StatusOK, w.Code)
    var resp map[string]interface{}
    json.Unmarshal(w.Body.Bytes(), &resp)
    data := resp["data"].(map[string]interface{})
    assert.Equal(t, todo.Title, data["title"])
}

func TestUpdateTodo(t *testing.T) {
    db := setupTestDB(t)
    r := setupTestRouter(db)

    model.CreateTodo(db, &model.CreateReq{Title: "原始标题"})

    body := `{"title":"新标题","status":1}`
    req := httptest.NewRequest("PUT", "/api/todos/1", strings.NewReader(body))
    req.Header.Set("Content-Type", "application/json")
    w := httptest.NewRecorder()

    r.ServeHTTP(w, req)

    assert.Equal(t, http.StatusOK, w.Code)
    var resp map[string]interface{}
    json.Unmarshal(w.Body.Bytes(), &resp)
    data := resp["data"].(map[string]interface{})
    assert.Equal(t, "新标题", data["title"])
}

func TestMarkDone(t *testing.T) {
    db := setupTestDB(t)
    r := setupTestRouter(db)

    model.CreateTodo(db, &model.CreateReq{Title: "待完成"})

    req := httptest.NewRequest("PATCH", "/api/todos/1/done", nil)
    w := httptest.NewRecorder()

    r.ServeHTTP(w, req)

    assert.Equal(t, http.StatusOK, w.Code)

    todo, _ := model.GetTodoByID(db, 1)
    assert.Equal(t, int8(1), todo.Status)
}

func TestDeleteTodo(t *testing.T) {
    db := setupTestDB(t)
    r := setupTestRouter(db)

    model.CreateTodo(db, &model.CreateReq{Title: "待删除"})

    req := httptest.NewRequest("DELETE", "/api/todos/1", nil)
    w := httptest.NewRecorder()

    r.ServeHTTP(w, req)

    assert.Equal(t, http.StatusOK, w.Code)

    _, err := model.GetTodoByID(db, 1)
    assert.NotNil(t, err)
}

func TestSearchTodo(t *testing.T) {
    db := setupTestDB(t)
    r := setupTestRouter(db)

    model.CreateTodo(db, &model.CreateReq{Title: "买牛奶", Content: "去超市"})
    model.CreateTodo(db, &model.CreateReq{Title: "写代码", Content: "完成项目"})

    req := httptest.NewRequest("GET", "/api/todos?keyword=牛奶", nil)
    w := httptest.NewRecorder()

    r.ServeHTTP(w, req)

    assert.Equal(t, http.StatusOK, w.Code)
    var resp map[string]interface{}
    json.Unmarshal(w.Body.Bytes(), &resp)
    data := resp["data"].(map[string]interface{})
    assert.Equal(t, float64(1), data["total"])
}

func setupTestRouter(db *gorm.DB) *gin.Engine {
    gin.SetMode(gin.TestMode)
    return router.Setup(db)
}
```

测试用了SQLite内存数据库（`:memory:`），跑测试不需要安装MySQL。`httptest.NewRecorder` 不需要真实启动HTTP服务，全部在内存中完成——速度飞快。

---

## 110.8 运行方式

### 环境准备

```bash
go mod tidy

export DB_HOST=127.0.0.1
export DB_PORT=3306
export DB_USER=root
export DB_PASSWORD=your_password
export DB_NAME=todo_db
export SERVER_PORT=8080
```

### 创建数据库

```sql
CREATE DATABASE IF NOT EXISTS todo_db
    DEFAULT CHARACTER SET utf8mb4
    DEFAULT COLLATE utf8mb4_unicode_ci;
```

### 启动服务

```bash
go run main.go
```

### 测试接口

```bash
curl -X POST http://localhost:8080/api/todos \
  -H "Content-Type: application/json" \
  -d '{"title":"买牛奶","content":"去超市买全脂牛奶"}'

curl http://localhost:8080/api/todos?page=1\&page_size=10

curl http://localhost:8080/api/todos/1

curl -X PUT http://localhost:8080/api/todos/1 \
  -H "Content-Type: application/json" \
  -d '{"title":"买牛奶和面包"}'

curl -X PATCH http://localhost:8080/api/todos/1/done

curl -X DELETE http://localhost:8080/api/todos/1
```

### 运行测试

```bash
go test -v ./...
```

---

## 本章小结

恭喜！你完成了第一个完整的Go Web项目。虽然它只是一个Todo应用，但你实际上已经走过了一个后端项目的完整生命周期：

1. **需求分析**：搞清楚要做什么、不做什么
2. **数据库设计**：建表、选字段类型、加索引
3. **项目分层**：model → handler → router → main
4. **API设计**：RESTful风格，统一响应格式
5. **核心实现**：Gin+GORM，参数验证，错误处理
6. **单元测试**：每一条业务逻辑都有对应的测试用例
7. **运行部署**：环境变量配置，启动和测试

> 🚀 这个项目就像一个乐高基础套装——后面的项目都是在这个基础结构上增加更多模块和复杂度。下一章我们要在这个骨架上加入用户认证——这是每个正经项目的必备组件。

---
[← 上一章：109-性能测试.md](109-性能测试/) | [下一章：111-项目二：用户认证系统.md →](111-项目二：用户认证系统/)
