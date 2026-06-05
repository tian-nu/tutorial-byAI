# 第59章 · Go操作MySQL

> "前面的八章你一直在MySQL命令行里写SQL。但现在你是Go后端工程师——你的程序要自动连数据库、自动执行SQL、自动把数据库的行转成Go的结构体。从这一章开始，Go和MySQL正式合体。"

---

## 59.1 database/sql：Go的数据库抽象层

Go标准库提供了 `database/sql` 包——它是一套**接口**，不包含任何数据库的**实现**。你需要额外安装对应数据库的**驱动**。

**比喻**：`database/sql` 是遥控器的电池仓——定义了正负极、大小。MySQL驱动（`go-sql-driver/mysql`）是电池——装上才能用。换PostgreSQL只需要换一块"电池"，遥控器还是那个遥控器。

### 安装驱动

```bash
go get github.com/go-sql-driver/mysql
```

### 建立连接

```go
package main

import (
    "database/sql"
    "fmt"
    "log"
    "time"

    _ "github.com/go-sql-driver/mysql"
)

func main() {
    dsn := "root:password@tcp(127.0.0.1:3306)/my_shop?charset=utf8mb4&parseTime=true&loc=Local"

    db, err := sql.Open("mysql", dsn)
    if err != nil {
        log.Fatal("打开数据库失败:", err)
    }
    defer db.Close()

    err = db.Ping()
    if err != nil {
        log.Fatal("连接数据库失败:", err)
    }

    fmt.Println("数据库连接成功!")
}
```

关键点：
- `_ "github.com/go-sql-driver/mysql"`：**匿名导入**。驱动包的 `init()` 函数会把自己注册到 `database/sql` 中，但你的代码不直接调用驱动——全靠这个 `import _` 激活。
- `dsn`（Data Source Name）：连接字符串，包含用户名、密码、地址、端口、数据库名、参数。
- `sql.Open()`：**并不立刻连接数据库**！只是初始化设置。用 `db.Ping()` 验证连接是否真正存活。
- `parseTime=true`：把MySQL的DATETIME/TIMESTAMP字段自动映射为Go的 `time.Time` 类型——**必须加**，否则时间字段返回字符串。
- `loc=Local`：时区用本地时区。

### 查询：单行

```go
type User struct {
    ID        int64
    Username  string
    Email     string
    Age       int
    Balance   float64
    CreatedAt time.Time
}

func GetUserByID(db *sql.DB, id int64) (*User, error) {
    query := "SELECT id, username, email, age, balance, created_at FROM users WHERE id = ?"

    var u User
    err := db.QueryRow(query, id).Scan(
        &u.ID,
        &u.Username,
        &u.Email,
        &u.Age,
        &u.Balance,
        &u.CreatedAt,
    )
    if err != nil {
        if err == sql.ErrNoRows {
            return nil, nil
        }
        return nil, err
    }

    return &u, nil
}
```

- `QueryRow()` 用于单行查询（最多返回一行）。
- `Scan()` 把列值映射到变量——**顺序必须和SELECT字段顺序一致**。
- `sql.ErrNoRows`：查询不到数据不是系统错误，而是"没找到"——用这个错误做区分，而不是当异常处理。

### 查询：多行

```go
func ListActiveUsers(db *sql.DB) ([]User, error) {
    query := "SELECT id, username, email, age, balance, created_at FROM users WHERE is_active = 1"

    rows, err := db.Query(query)
    if err != nil {
        return nil, err
    }
    defer rows.Close()

    var users []User
    for rows.Next() {
        var u User
        err := rows.Scan(&u.ID, &u.Username, &u.Email, &u.Age, &u.Balance, &u.CreatedAt)
        if err != nil {
            return nil, err
        }
        users = append(users, u)
    }

    if err := rows.Err(); err != nil {
        return nil, err
    }

    return users, nil
}
```

关键点：
- `rows.Close()` **必须调用**，否则连接不会释放回连接池——很快连接就会耗尽。
- `rows.Next()` 遍历结果集。注意用完后还要检查 `rows.Err()`——遍历过程中也可能出错。
- 不要忘记defer rows.Close()必须在rows.Next()的循环之后执行——所以要放在err检查之后。

### INSERT / UPDATE / DELETE（Exec）

```go
func CreateUser(db *sql.DB, username, email string, age int) (int64, error) {
    query := "INSERT INTO users (username, email, age) VALUES (?, ?, ?)"

    result, err := db.Exec(query, username, email, age)
    if err != nil {
        return 0, err
    }

    id, err := result.LastInsertId()
    if err != nil {
        return 0, err
    }

    return id, nil
}
```

```go
func UpdateUserAge(db *sql.DB, userID int64, newAge int) (int64, error) {
    query := "UPDATE users SET age = ? WHERE id = ?"

    result, err := db.Exec(query, newAge, userID)
    if err != nil {
        return 0, err
    }

    affected, err := result.RowsAffected()
    if err != nil {
        return 0, err
    }

    return affected, nil
}
```

- `Exec()` 用于不返回结果集的SQL（INSERT/UPDATE/DELETE）。
- `result.LastInsertId()` 返回AUTO_INCREMENT生成的主键值。
- `result.RowsAffected()` 返回影响了几行——用来判断操作是否真的生效。

### 预处理语句（Prepared Statement）

```go
func BatchInsertUsers(db *sql.DB, users []User) error {
    stmt, err := db.Prepare("INSERT INTO users (username, email, age) VALUES (?, ?, ?)")
    if err != nil {
        return err
    }
    defer stmt.Close()

    for _, u := range users {
        _, err := stmt.Exec(u.Username, u.Email, u.Age)
        if err != nil {
            return err
        }
    }

    return nil
}
```

Prepare将SQL模板发给MySQL预编译一次，之后每次只传参数——省去重复解析的开销。适合批量操作。

### 事务

```go
func TransferMoney(db *sql.DB, fromID, toID int64, amount float64) error {
    tx, err := db.Begin()
    if err != nil {
        return err
    }

    _, err = tx.Exec("UPDATE accounts SET balance = balance - ? WHERE id = ?", amount, fromID)
    if err != nil {
        tx.Rollback()
        return err
    }

    _, err = tx.Exec("UPDATE accounts SET balance = balance + ? WHERE id = ?", amount, toID)
    if err != nil {
        tx.Rollback()
        return err
    }

    return tx.Commit()
}
```

- `db.Begin()` 开启事务，返回 `*sql.Tx`。
- 所有操作通过 `tx.Exec()` / `tx.Query()` 执行。
- 出错时调用 `tx.Rollback()` 撤销——用defer不太方便（因为要区分错误类型），所以直接在err处手动回滚。

---

## 59.2 连接池配置

`sql.Open()` 返回的 `*sql.DB` 内部维护了一个**连接池**——你不应该频繁创建和销毁 `*sql.DB`。把 `*sql.DB` 做成全局单例，整个进程共用一个：

```go
db, err := sql.Open("mysql", dsn)
if err != nil {
    log.Fatal(err)
}

db.SetMaxOpenConns(25)
db.SetMaxIdleConns(10)
db.SetConnMaxLifetime(5 * time.Minute)
db.SetConnMaxIdleTime(2 * time.Minute)
```

| 参数 | 含义 | 建议值 |
|------|------|--------|
| MaxOpenConns | 最大打开连接数 | 根据MySQL `max_connections` 设定，单应用25~100合理 |
| MaxIdleConns | 最大空闲连接数 | 设为 MaxOpenConns 的 40%~60% |
| ConnMaxLifetime | 连接最大存活时间 | 5分钟（小于MySQL wait_timeout） |
| ConnMaxIdleTime | 连接最大空闲时间 | 2分钟 |

**为什么设MaxOpenConns？** MySQL默认 `max_connections` 是151。如果10台应用服务器每台开50个连接，总共500个——超过151，MySQL直接拒绝新的连接，应用全挂。

---

## 59.3 SQL注入防护

SQL注入是Web安全的第一杀手——通过拼接SQL字符串，攻击者能让你的数据库执行任意命令。

### 注入演示

```go
userInput := "1' OR '1'='1"
query := "SELECT * FROM users WHERE id = " + userInput
```

执行的SQL变成：

```sql
SELECT * FROM users WHERE id = 1 OR '1'='1'
```

`'1'='1'` 永远为真——返回全部用户数据。攻击者拿到了所有用户的密码哈希。

更恐怖的：

```sql
userInput := "1; DROP TABLE users; --"
```

执行的SQL：

```sql
SELECT * FROM users WHERE id = 1; DROP TABLE users; --'
```

你的users表消失了。

### 防护：占位符

**永远使用 `?` 占位符，永远不要拼接SQL字符串**：

```go
db.QueryRow("SELECT * FROM users WHERE id = ?", userInput)
```

Go的 `database/sql` 会把参数和SQL模板分开发送给MySQL——参数再恶毒也只是数据，不会被当成SQL执行。

### ORM的防注入

GORM和sqlx都自动使用参数化查询——只要你用Query/Exec/Where等方法传参，而不是手动拼接SQL字符串。

🤔 **想多一点**：所有SQL注入本质上都是**把数据和指令混在一起**。就像你去餐厅点"一份牛排"，传菜员听成"一份牛排和一张100元钞票"。解决方法是分开传递：一张纸上写"订单：牛排"，另一张纸条上写"订单内容：XXX"。占位符就是这个"分开传递"的机制。

---

## 59.4 GORM入门

GORM是Go生态中最流行的ORM（Object-Relational Mapping，把数据库表映射为程序结构体，详见附录I）库。它把数据库表映射为Go结构体，把SQL操作映射为方法调用。

### 安装

```bash
go get gorm.io/gorm
go get gorm.io/driver/mysql
```

### 模型定义

```go
type User struct {
    ID        uint           `gorm:"primaryKey"`
    Username  string         `gorm:"size:50;uniqueIndex;not null"`
    Email     string         `gorm:"size:100;uniqueIndex;not null"`
    Age       int            `gorm:"default:0"`
    Balance   float64        `gorm:"default:0"` // 注意：生产环境金额字段应使用 decimal 类型，见第51章
    CreatedAt time.Time
    UpdatedAt time.Time
    DeletedAt gorm.DeletedAt `gorm:"index"`
}
```

GORM通过struct tag约定行为：
- `primaryKey`：主键。
- `size:50`：字段长度。
- `uniqueIndex`：唯一索引。
- `not null`：非空。
- `default:0`：默认值。
- `gorm.DeletedAt`：**软删除**支持——GORM自动管理。

### 连接与自动迁移

```go
import (
    "gorm.io/driver/mysql"
    "gorm.io/gorm"
)

func main() {
    dsn := "root:password@tcp(127.0.0.1:3306)/my_shop?charset=utf8mb4&parseTime=true&loc=Local"
    db, err := gorm.Open(mysql.Open(dsn), &gorm.Config{})
    if err != nil {
        log.Fatal(err)
    }

    db.AutoMigrate(&User{})
}
```

`AutoMigrate` 自动创建或更新表结构——开发阶段很方便，但**生产环境禁止使用**（会导致锁表和不预期的修改）。

### CRUD

**创建**：

```go
user := User{Username: "zhangsan", Email: "zs@test.com", Age: 25}
result := db.Create(&user)
fmt.Println(user.ID, result.RowsAffected)
```

**查询单条**：

```go
var user User
db.First(&user, 1)
db.First(&user, "username = ?", "zhangsan")
db.Where("age > ?", 18).First(&user)
```

**查询多条**：

```go
var users []User
db.Where("age BETWEEN ? AND ?", 20, 30).Find(&users)
```

**更新**：

```go
db.Model(&User{}).Where("id = ?", 1).Update("age", 26)
db.Model(&User{}).Where("id = ?", 1).Updates(User{Age: 26, Balance: 100})
```

Updates传结构体时，**零值字段不会被更新**——这是一个大坑。如果想更新零值，传map：

```go
db.Model(&User{}).Where("id = ?", 1).Updates(map[string]interface{}{"age": 0})
```

**删除**：

```go
db.Delete(&User{}, 1)
```

如果模型有 `DeletedAt` 字段，GORM默认执行软删除——只是把 `deleted_at` 设为当前时间。真要物理删除，加 `Unscoped()`：

```go
db.Unscoped().Delete(&User{}, 1)
```

### 关联

```go
type User struct {
    gorm.Model
    Orders []Order `gorm:"foreignKey:UserID"`
}

type Order struct {
    gorm.Model
    UserID  uint
    Amount  float64
}
```

查询用户及其订单（预加载）：

```go
var user User
db.Preload("Orders").First(&user, 1)
```

### 事务

```go
db.Transaction(func(tx *gorm.DB) error {
    if err := tx.Model(&User{}).Where("id = ?", 1).Update("balance", gorm.Expr("balance - ?", 100)).Error; err != nil {
        return err
    }
    if err := tx.Model(&User{}).Where("id = ?", 2).Update("balance", gorm.Expr("balance + ?", 100)).Error; err != nil {
        return err
    }
    return nil
})
```

GORM的事务用闭包——返回error就自动回滚，返回nil就自动提交。比原生database/sql的事务操作简洁很多。

---

## 59.5 sqlx简介

sqlx是 `database/sql` 的增强版——保留了原生的灵活性，添加了结构体映射和命名参数等便利功能。

### 安装

```bash
go get github.com/jmoiron/sqlx
```

### 结构体映射

```go
type User struct {
    ID        int64     `db:"id"`
    Username  string    `db:"username"`
    Email     string    `db:"email"`
    Age       int       `db:"age"`
    CreatedAt time.Time `db:"created_at"`
}
```

```go
var users []User
err := db.Select(&users, "SELECT id, username, email, age, created_at FROM users WHERE age > ?", 18)
```

sqlx自动把列映射到结构体的 `db` tag。不需要手动Scan每一列——代码量减少60%。

### 命名参数

```go
query := `SELECT * FROM users WHERE age > :min_age AND balance > :min_balance`
arg := map[string]interface{}{
    "min_age":     20,
    "min_balance": 100,
}
rows, err := db.NamedQuery(query, arg)
```

### 三者对比

| 特性 | database/sql | sqlx | GORM |
|------|:---:|:---:|:---:|
| 学习成本 | 低 | 低 | 中 |
| 灵活性 | 最高 | 高 | 中 |
| 自动化程度 | 最低 | 中 | 最高 |
| 结构体映射 | 手动Scan | 自动 | 自动 |
| SQL控制力 | 完全控制 | 完全控制 | 封装（但也能写原生SQL） |
| 迁移 | 自行管理 | 自行管理 | 自动迁移 |
| 性能 | 最佳 | 很好 | 有微小开销 |

**选型建议**：
- 简单项目或注重性能：用 `sqlx`——比原生方便又不失控制力。
- 标准Web后端项目：用 `GORM`——开发效率高，团队协作方便。
- 复杂SQL场景（报表、数据分析）：用 `sqlx` 或原生 `database/sql`——GORM的Query Builder复杂SQL不灵活。

---

## 本章小结

| 知识点 | 要点 |
|--------|------|
| database/sql | Go标准库的数据库抽象，需搭配驱动，`_ "..."` 匿名导入激活 |
| DSN | `user:pass@tcp(host:port)/db?parseTime=true&loc=Local` |
| QueryRow | 单行查询+Scan，`sql.ErrNoRows` 表示无结果 |
| Query | 多行查询，`rows.Next()` 遍历，`defer rows.Close()` 必须，查完检查 `rows.Err()` |
| Exec | INSERT/UPDATE/DELETE，返回 `LastInsertId` 和 `RowsAffected` |
| Prepare | 预编译SQL模板，批量操作省解析开销 |
| 事务 | `db.Begin()` → `tx.Exec/Query` → `tx.Commit/Rollback` |
| 连接池 | MaxOpenConns(25~100)、MaxIdleConns、ConnMaxLifetime(5min) 关键参数 |
| SQL注入 | 绝不用字符串拼接，用 `?` 占位符，ORM自动防注入 |
| GORM | ORM库，模型定义+CRUD+关联+事务，AutoMigrate仅开发用 |
| sqlx | 原生SQL增强版，结构体自动映射，灵活性优于GORM |

> 🚀 下一章：第60章 · Redis入门。MySQL搞定了，但你的网站首页每次都要查数据库——100万用户每秒都来查，数据库扛不住。这时候你需要一个超快的缓存。Redis，内存中的闪电，它的读写速度比MySQL快100倍以上。而它的数据类型只有5种，一天就能上手。

---
[← 上一章：58-数据库优化](58-数据库优化.md) | [下一章：60-Redis入门 →](60-Redis入门.md)
