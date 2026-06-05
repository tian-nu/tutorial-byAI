# 第29章 · 结构体（Struct）

> "你去医院挂号，护士不会分别问你'姓名'、'年龄'、'性别'、'血型'，再分别记到四张纸上——她把所有信息填在一张挂号单上。结构体就是这张挂号单：把相关的信息打包在一起，变成一个整体。"

---

## 29.1 结构体是什么

之前我们学的变量类型都是"单身"的——一个 `int` 存一个数字，一个 `string` 存一个字符串。但真实世界的数据是"组团"出现的：

- 一个用户：姓名、年龄、邮箱、手机号
- 一本书：书名、作者、ISBN、价格、出版日期
- 一个订单：订单号、商品列表、金额、收货地址

用单独的变量也能存：

```go
var userName string
var userAge int
var userEmail string
var userPhone string
```

但等你要传"一个用户"给函数的时候怎么办？传四个参数？一百个用户字段怎么办？

**结构体就是把相关的字段打包成一个新类型**：

```go
type User struct {
    Name  string
    Age   int
    Email string
    Phone string
}
```

现在 `User` 是一个新的类型，就像 `int` 和 `string` 一样使用：

```go
var u User
u.Name = "张三"
u.Age = 25
u.Email = "zhangsan@example.com"
```

### 比喻：个人信息登记表

`type User struct { ... }` 是设计了一份空白表格——表格上有哪些栏目（姓名、年龄、邮箱），每个栏目什么类型。

`var u User` 是拿出了一份空白表格。

`u.Name = "张三"` 是在姓名栏里填入"张三"。

整个 `u` 就是一张填好的表格——你可以把它作为一个整体传给任何函数。

---

## 29.2 创建和初始化结构体

### 方式一：先声明再逐字段赋值

```go
var u User
u.Name = "张三"
u.Age = 25
u.Email = "zhangsan@example.com"
```

所有字段初始化为零值：字符串是 `""`，int是 `0`。

### 方式二：字面量按字段名初始化

```go
u := User{
    Name:  "张三",
    Age:   25,
    Email: "zhangsan@example.com",
}
```

推荐这种方式——字段名一目了然，顺序不重要，漏掉某个字段就默认为零值。

### 方式三：字面量按顺序初始化

```go
u := User{"张三", 25, "zhangsan@example.com", "13800138000"}
```

**不推荐**。你必须记住字段的顺序，漏一个都不行。而且将来User加了新字段，所有按顺序初始化的代码都得改。容易出错。

### 结构体指针

大部分时候，你创建的不是结构体本身，而是结构体的指针：

```go
u := &User{
    Name: "张三",
    Age:  25,
}
```

`u` 的类型是 `*User`。为什么用指针？因为后面要传给函数修改，或者结构体比较大，避免复制。

---

## 29.3 匿名字段和结构体嵌套

### 匿名字段

有时候你不想给字段起名字：

```go
type Person struct {
    string
    int
}

p := Person{"张三", 25}
fmt.Println(p.string)
fmt.Println(p.int)
```

匿名字段的类型名就是字段名。`Person` 有两个字段：`string` 和 `int`。

匿名字段有什么实际用途？单独用很少，但它是下面"嵌套"的基础。

### 结构体嵌套（组合）

Go **没有继承**（不像Java的 `extends`），但通过结构体嵌套实现了类似效果：

```go
type Address struct {
    Province string
    City     string
    Street   string
}

type User struct {
    Name    string
    Age     int
    Address Address
}

u := User{
    Name: "张三",
    Age:  25,
    Address: Address{
        Province: "广东省",
        City:     "深圳市",
        Street:   "科技园路1号",
    },
}

fmt.Println(u.Address.City)
```

一个结构体包含另一个结构体——这就是**组合**。

### 匿名嵌套（提升字段）

如果把嵌套的结构体写成"匿名字段"，内部字段会被"提升"到外层：

```go
type User struct {
    Name    string
    Age     int
    Address
}

u := User{
    Name: "张三",
    Age:  25,
    Address: Address{
        Province: "广东省",
        City:     "深圳市",
    },
}

fmt.Println(u.City)
fmt.Println(u.Address.City)
```

`u.City` 等价于 `u.Address.City`——就像 `Address` 的字段直接"长在"了 `User` 身上。

如果 `User` 自己也有一个 `City` 字段呢？

```go
type User struct {
    Name    string
    City    string
    Address
}

u := User{
    City: "广州",
    Address: Address{
        City: "深圳",
    },
}

fmt.Println(u.City)
fmt.Println(u.Address.City)
```

输出：
```
广州
深圳
```

外层字段优先级更高——`u.City` 是 `User` 自己的 `City`，要访问 `Address` 的 `City` 必须通过 `u.Address.City`。

---

## 29.4 结构体标签（Tag）

在结构体字段后面，你可以用反引号写一些"标签"：

```go
type User struct {
    Name string `json:"name"`
    Age  int    `json:"age"`
}
```

这看起来像注释，但实际上**可以被程序读取**！标签是结构体字段的元数据——关于数据的数据。

### 最常见的标签：json

```go
type User struct {
    Name string `json:"name"`
    Age  int    `json:"age"`
}

u := User{Name: "张三", Age: 25}
data, _ := json.Marshal(u)  // json序列化详见第39章
fmt.Println(string(data))
```

输出：
```json
{"name":"张三","age":25}
```

`json:"name"` 告诉 `json.Marshal`："序列化这个字段时，用 `name` 作为JSON的键名，不要用 `Name`"。

没有标签的话，JSON键名会是 `Name` 和 `Age`（大写开头），这在Go内部没问题，但对外API通常用小写。

### 其他常用标签

```go
type User struct {
    ID    int    `json:"id" gorm:"primaryKey"`
    Name  string `json:"name" validate:"required,min=2,max=50"`
    Email string `json:"email" validate:"email"`
    Age   int    `json:"age,omitempty"`
}
```

| 标签 | 用途 | 例子 |
|------|------|------|
| `json` | JSON序列化控制 | `json:"name,omitempty"` |
| `gorm` | GORM数据库映射 | `gorm:"primaryKey"` |
| `validate` | 参数校验 | `validate:"required,email"` |
| `form` | Gin表单绑定 | `form:"username"` |
| `xml` | XML序列化控制 | `xml:"name,attr"` |

`omitempty` 的意思是：如果字段是零值（0、""、nil等），序列化时跳过它。

### Tag的格式

Tag的格式是 `key:"value"`，多个标签用空格分隔：

```go
`json:"name" xml:"name"`
```

用 `reflect` 包可以读取标签，但你通常不需要手动读——各种库（json、gorm、gin）会自动读取。

---

## 29.5 空结构体：0字节的神奇类型

```go
var s struct{}
fmt.Println(unsafe.Sizeof(s))  // unsafe 包属于高级话题，此处了解即可
```

输出：`0`

空结构体不占用任何内存。它有什么用？

### 用途一：实现Set

Go没有内置Set类型。但可以用 `map[KeyType]struct{}` 来模拟：

```go
visited := make(map[string]struct{})

visited["北京"] = struct{}{}
visited["上海"] = struct{}{}

if _, ok := visited["北京"]; ok {
    fmt.Println("北京已经去过了")
}
```

为什么不用 `map[string]bool`？因为 `struct{}` 不占内存，比 `bool`（占1字节）更省。当你有百万个key时，差别就明显了。

### 用途二：信号通知

```go
done := make(chan struct{})

go func() {
    time.Sleep(2 * time.Second)
    done <- struct{}{}
}()

<-done
fmt.Println("任务完成")
```

用 `chan struct{}` 表示"我只发信号，不传输任何数据"。收到信号就知道完成了，但信号本身不携带信息。

### 用途三：方法集合

有时候你只需要一个类型来挂载方法，不需要存任何数据：

```go
type Logger struct{}

func (l Logger) Info(msg string) {
    fmt.Println("[INFO]", msg)
}
```

---

## 本章小结

| 知识点 | 要点 |
|--------|------|
| 结构体定义 | `type Name struct { ... }`，把相关字段打包成新类型 |
| 创建方式 | 逐字段赋值、按字段名字面量、按顺序字面量 |
| 嵌套 | 结构体包含结构体，组合而非继承 |
| 匿名嵌套 | 内层字段提升到外层，可直接访问 |
| Tag | 字段元数据，`json`/`gorm`/`validate` 等库自动读取 |
| 空结构体 | 0字节，用于Set模拟、信号通知、纯方法集合 |

> 🚀 下一章：第30章 · 方法——函数是"孤狼"，方法是"有主的狼"。方法绑定在类型上，可以操作类型内部的数据。值接收者还是指针接收者？这是一个每天都会遇到的抉择。

---
[← 上一章：28-指针](28-指针.md) | [下一章：30-方法 →](30-方法.md)