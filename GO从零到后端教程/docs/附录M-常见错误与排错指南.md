# 附录M · 常见编译错误与排错指南

> "每一个 Go 编译器报错，都是一次精准的免费代码审查。学会读懂它，你的调试效率会翻倍。"

---

## 目录

- [一、编译错误篇（20个最常见错误）](#一编译错误篇20个最常见错误)
  - [M1.1 `syntax error: unexpected xxx` — 语法错误](#m11-syntax-error-unexpected-xxx--语法错误)
  - [M1.2 `xxx declared and not used` — 变量声明了但没使用](#m12-xxx-declared-and-not-used--变量声明了但没使用)
  - [M1.3 `xxx imported and not used` — 导入了但没使用](#m13-xxx-imported-and-not-used--导入了但没使用)
  - [M1.4 `cannot use xxx as type yyy` — 类型不匹配](#m14-cannot-use-xxx-as-type-yyy--类型不匹配)
  - [M1.5 `missing return` — 缺少返回值](#m15-missing-return--缺少返回值)
  - [M1.6 `non-name xxx on left side of :=` — := 左边不是变量名](#m16-non-name-xxx-on-left-side-of---左边不是变量名)
  - [M1.7 `no new variables on left side of :=` — := 左边没有新变量](#m17-no-new-variables-on-left-side-of---左边没有新变量)
  - [M1.8 `undefined: xxx` — xxx 未定义](#m18-undefined-xxx--xxx-未定义)
  - [M1.9 `cannot assign to xxx` — 不能给 xxx 赋值](#m19-cannot-assign-to-xxx--不能给-xxx-赋值)
  - [M1.10 `invalid operation: xxx (mismatched types)` — 操作数类型不匹配](#m110-invalid-operation-xxx-mismatched-types--操作数类型不匹配)
  - [M1.11 `use of unexported identifier` — 引用了未导出的标识符](#m111-use-of-unexported-identifier--引用了未导出的标识符)
  - [M1.12 `xxx is not a type` — xxx 不是一个类型](#m112-xxx-is-not-a-type--xxx-不是一个类型)
  - [M1.13 `too many arguments in call to xxx` — 调用 xxx 时传入了太多参数](#m113-too-many-arguments-in-call-to-xxx--调用-xxx-时传入了太多参数)
  - [M1.14 `not enough arguments in call to xxx` — 调用 xxx 时参数不够](#m114-not-enough-arguments-in-call-to-xxx--调用-xxx-时参数不够)
  - [M1.15 `xxx declared and not used`（包级别）— 包级变量声明未使用](#m115-xxx-declared-and-not-used包级别--包级变量声明未使用)
  - [M1.16 `expected 'package', found 'xxx'` — 缺少 package 关键字](#m116-expected-package-found-xxx--缺少-package-关键字)
  - [M1.17 `main redeclared in this block` — main 重复声明](#m117-main-redeclared-in-this-block--main-重复声明)
  - [M1.18 `cannot take the address of xxx` — 不能取 xxx 的地址](#m118-cannot-take-the-address-of-xxx--不能取-xxx-的地址)
  - [M1.19 `constant xxx overflows int` — 常量溢出](#m119-constant-xxx-overflows-int--常量溢出)
  - [M1.20 `type xxx is not an expression` — 把类型名当成了表达式](#m120-type-xxx-is-not-an-expression--把类型名当成了表达式)
- [二、运行时错误篇（10个最常见 Panic）](#二运行时错误篇10个最常见-panic)
- [三、常见逻辑错误篇](#三常见逻辑错误篇)
- [四、排错方法论](#四排错方法论)

---

## 一、编译错误篇（20个最常见错误）

### M1.1 `syntax error: unexpected xxx` — 语法错误

**错误信息（Go 编译器原文）：**

```
./main.go:10:5: syntax error: unexpected newline, expecting comma or }
./main.go:15:1: syntax error: unexpected semicolon or newline before {
```

**中文翻译：**

Go 编译器在第 10 行第 5 列遇到了不该出现的东西（换行/分号/括号等），它本来期望看到一个逗号或右花括号。

**原因分析：**

这是 Go 中最常见的语法错误大类。Go 编译器对代码结构要求严格，不像 Python 那样宽松。常见触发场景：

- 少写了逗号、分号、括号
- 多写了逗号（比如结构体最后一个字段后面多写了一个逗号）
- `if` / `for` / `func` 的左花括号 `{` 没有放在同一行
- 字符串没闭合
- 注释块 `/* */` 没有闭合

**❌ 错误示例：**

```go
// 错误1：左花括号换了行（Go 不允许）
func main()
{
    fmt.Println("hello")
}

// 错误2：结构体字面量最后一个元素后多了逗号（某些旧版本不允许）
// 注：Go 1.x 已逐步放宽此限制，但仍有人中招
user := User{
    Name: "Alice",
    Age:  30,
}

// 错误3：字符串忘了闭合
s := "hello

// 错误4：丢了右括号
fmt.Println("hello"
```

**✅ 正确示例：**

```go
// 正确1：左花括号必须在同一行
func main() {
    fmt.Println("hello")
}

// 正确2：最后一个元素后面的逗号，Go 1.x 允许，但建议加上（方便日后增删字段）
user := User{
    Name: "Alice",
    Age:  30,
}

// 正确3：字符串正确闭合
s := "hello"

// 正确4：括号配对
fmt.Println("hello")
```

**解决方法：**

1. **看行号**：找到报错的行号，先检查那一行本身。
2. **向前看**：很多时候真正的错误在前面一行——比如前一行的字符串没闭合，编译器到下一行才发现语法不对。
3. **检查配对**：数括号 `()`、花括号 `{}`、方括号 `[]` 是否配对。
4. **用 IDE**：VSCode + Go 插件会在保存时自动格式化，很多语法问题在保存时就发现了。

**预防建议：**

- 配置编辑器在保存时自动运行 `gofmt`
- 养成写代码时同时敲开闭括号的习惯
- 使用 `gofmt -e main.go` 命令可得到更友好的错误定位

---

### M1.2 `xxx declared and not used` — 变量声明了但没使用

**错误信息（Go 编译器原文）：**

```
./main.go:8:2: x declared and not used
./main.go:10:2: err declared and not used
```

**中文翻译：**

变量 `x`（在 main.go 第 8 行声明）从来没有被用过。Go 不允许声明了变量却不使用它。

**原因分析：**

这是 Go 语言刻意为之的设计——声明了但不使用的变量意味着要么是废代码，要么是遗漏了逻辑。许多语言对未使用变量只是警告（warning），但 Go 直接报编译错误。这体现了 Go 追求代码整洁的哲学。

**❌ 错误示例：**

```go
func main() {
    x := 10       // 声明了但后面没用
    y := 20
    fmt.Println(y)
}
```

**✅ 正确示例：**

```go
// 方案A：删除没用的变量
func main() {
    y := 20
    fmt.Println(y)
}

// 方案B：如果真的需要 x，就使用它
func main() {
    x := 10
    y := 20
    fmt.Println(x + y)
}

// 方案C：用 _ (下划线) 吃掉不需要的值（常见于 err）
func main() {
    data, _ := someFunc()
    fmt.Println(data)
}
```

**解决方法：**

1. **真的不需要这个变量** → 删掉声明语句。
2. **需要但还没写相关代码** → 把使用它的代码补上。
3. **函数返回多个值但只需要其中一部分** → 用 `_` 占位符：`result, _ := doSomething()`
4. **正在调试中，暂时要保留** → 加一行 `_ = x` 来"假装使用"，但调试完后务必清理。

**预防建议：**

写代码时，声明变量的同时就想好它马上要用来干什么。不要让变量"空站着"。

---

### M1.3 `xxx imported and not used` — 导入了但没使用

**错误信息（Go 编译器原文）：**

```
./main.go:4:2: imported and not used: "fmt"
./main.go:5:2: imported and not used: "net/http"
```

**中文翻译：**

你导入了 `fmt` 包（在 main.go 第 4 行），但整个文件里一次都没有用它。Go 不允许导入用不到的包。

**原因分析：**

和"变量声明了但没用"是同样的设计理念。导入不用的包会增大编译出的二进制体积、拖慢编译速度，Go 编译器直接把它当错误处理。最常见的情况是：写代码时先导入了，后来把用这个包的代码删了，但忘记删除 import。

**❌ 错误示例：**

```go
package main

import (
    "fmt"   // 导入了但没用到
    "net/http"
)

func main() {
    println("hello") // 用了内建 println，没用 fmt
}
```

**✅ 正确示例：**

```go
// 方案A：删掉没用的 import
package main

import ()

func main() {
    println("hello")
}

// 方案B：改为用 fmt 来打印
package main

import "fmt"

func main() {
    fmt.Println("hello")
}

// 方案C：匿名导入（仅为了执行 init() 函数）
import _ "net/http/pprof" // 下划线表示"我知道我不用，但别报错"
```

**解决方法：**

1. **删掉不用的 import 行**。
2. **如果确实要保留导入（比如副作用导入）**，在包名前加 `_`：`import _ "image/png"`
3. **使用 `goimports` 工具**（VSCode 可配置为保存时自动运行），它会自动删除未使用的导入、自动添加缺失的导入。

**预防建议：**

```bash
# 安装 goimports（比 gofmt 更强，自动管理 import）
go install golang.org/x/tools/cmd/goimports@latest

# 在编辑器中配置保存时自动运行 goimports
```

---

### M1.4 `cannot use xxx as type yyy` — 类型不匹配

**错误信息（Go 编译器原文）：**

```
./main.go:8:15: cannot use "hello" (type string) as type int in assignment
./main.go:12:3: cannot use user (type *User) as type User in argument to printUser
```

**中文翻译：**

你不能把 `"hello"`（它的类型是 `string`）当作 `int` 类型来赋值。换句话说：类型对不上。

**原因分析：**

Go 是强静态类型语言。`string` 就是 `string`，不会自动变成 `int`。这和其他语言（如 JavaScript 的隐式类型转换）完全不同。初学者最常见的踩坑：把不同数字类型混用——`int` 和 `int64` 在 Go 里是两种不同的类型，不能直接互用。

**❌ 错误示例：**

```go
// 错误1：字符串塞给 int
var age int = "25"

// 错误2：int 和 int64 不能直接互用
var a int = 10
var b int64 = 20
c := a + b // 编译报错！

// 错误3：指针类型和值类型互用
type User struct { Name string }
u := &User{Name: "Alice"}
printUser(u) // 但 printUser 的参数是 User，不是 *User
```

**✅ 正确示例：**

```go
// 正确1：类型要对上
var age int = 25

// 正确2：显示类型转换
var a int = 10
var b int64 = 20
c := int64(a) + b // a 转成 int64 后相加

// 正确3：指针解引用或传地址
func printUser(u User) { fmt.Println(u.Name) }
u := &User{Name: "Alice"}
printUser(*u) // 解引用，*User → User
```

**解决方法：**

1. **看清楚期望类型和实际类型**：报错信息已经把两边都告诉你了。
2. **做显式类型转换**：`int(x)`、`string(y)`、`float64(z)` 等。
3. **检查函数签名**：确认形参要求的是值类型还是指针类型。
4. **整数字面量**：Go 的整数常量（如 `10`）是无类型常量，会在使用时自动适应——这是特例，不要混淆。

**预防建议：**

在写函数参数和变量声明时，心里默念一遍类型。Go 没有任何隐式类型转换——这是好事，它让 Bug 无处藏身。

---

### M1.5 `missing return` — 缺少返回值

**错误信息（Go 编译器原文）：**

```
./main.go:10:1: missing return
```

**中文翻译：**

函数声明了有返回值（比如返回 `int`），但函数体的某些执行路径上没有写 `return` 语句。

**原因分析：**

Go 要求每个"出口"都必须 return。最典型的问题是：`if-else` 分支里只在 `if` 中写了 `return`，但 `else` 或函数末尾没有写。

**❌ 错误示例：**

```go
// 错误：只在 if 里 return 了，外部没有
func getGrade(score int) string {
    if score >= 90 {
        return "A"
    }
    // 编译器到这里发现：如果 score < 90，你啥也没返回！
}

// 错误：switch 缺少 default 分支的 return
func getLevel(n int) string {
    switch n {
    case 1:
        return "one"
    case 2:
        return "two"
    }
    // n 不是 1 也不是 2 时，没有返回值
}
```

**✅ 正确示例：**

```go
// 正确：所有分支都覆盖
func getGrade(score int) string {
    if score >= 90 {
        return "A"
    }
    return "B" // 兜底
}

// 正确：switch 加 default
func getLevel(n int) string {
    switch n {
    case 1:
        return "one"
    case 2:
        return "two"
    default:
        return "unknown"
    }
}
```

**解决方法：**

1. **找到函数末尾**，确认有没有 `return`。
2. **检查所有分支**（`if`/`else`/`switch`/`for`），确认每个分支都有 `return`。
3. **如果函数可能出错**，通常返回零值 + error：`return "", fmt.Errorf("...")`

**预防建议：**

在写函数签名时，先写完 `return` 语句的骨架，再填充中间逻辑。比如：

```go
func calc(a, b int) int {
    result := a + b
    return result // 先把 return 写下来
}
```

---

### M1.6 `non-name xxx on left side of :=` — `:=` 左边不是变量名

**错误信息（Go 编译器原文）：**

```
./main.go:6:2: non-name x.y on left side of :=
./main.go:8:2: non-name user.Name on left side of :=
```

**中文翻译：**

`:=` 是"声明并赋值"的短语法，左边必须是纯变量名。你写了 `x.y := ...` 这种带点号的表达式，Go 无法理解。

**原因分析：**

`:=` 只能用来**声明新变量**。想给结构体字段赋值？不能用 `:=`，必须用 `=`。想给 map 赋值？也不能用 `:=`。

**❌ 错误示例：**

```go
type User struct {
    Name string
}
u := User{}
u.Name := "Alice"  // 错误：:= 只用于声明变量，不能用于赋值字段

m := make(map[string]int)
m["key"] := 10     // 错误同理
```

**✅ 正确示例：**

```go
u := User{}
u.Name = "Alice"   // 用 = 给字段赋值

m := make(map[string]int)
m["key"] = 10      // 用 = 给 map 赋值
```

**解决方法：**

简单区分：
- **第一次创建变量** → 用 `:=`
- **给已有的变量/字段/元素赋值** → 用 `=`

**预防建议：**

当你要操作一个"已经存在的东西"（结构体字段、map 元素、数组元素），永远用 `=`。

---

### M1.7 `no new variables on left side of :=` — `:=` 左边没有新变量

**错误信息（Go 编译器原文）：**

```
./main.go:8:2: no new variables on left side of :=
```

**中文翻译：**

`:=` 的左边全是已经在当前作用域里声明过的变量，没有一个"新面孔"。Go 要求 `:=` 左边至少有一个是新变量。

**原因分析：**

在**同一个作用域**（同一个函数、同一个 `if` 块等）里，如果变量已经用 `:=` 或 `var` 声明过了，再次对它用 `:=` 会报错——除非这一行的左边至少有一个是从没声明过的新变量。

**❌ 错误示例：**

```go
func main() {
    x := 10
    x := 20 // 错误：x 已经声明过了，左边没有新变量
}
```

**✅ 正确示例：**

```go
// 方案A：用 = 赋值
func main() {
    x := 10
    x = 20
}

// 方案B：左边至少有一个新变量，:= 就合法
func main() {
    x := 10
    x, y := 20, 30 // 合法：y 是新变量
    fmt.Println(x, y)
}
```

**解决方法：**

1. 如果**只是修改值**，用 `=` 而不是 `:=`。
2. 如果**需要同时声明一个新变量**，就用 `:=`，让旧变量陪跑。

**预防建议：**

养成习惯：声明变量后，后面只改值就用 `=`。

---

### M1.8 `undefined: xxx` — xxx 未定义

**错误信息（Go 编译器原文）：**

```
./main.go:10:2: undefined: fmt
./main.go:12:6: undefined: User
./main.go:15:8: undefined: calculateTotal
```

**中文翻译：**

Go 找不到你要用的这个东西——可能是包没导入、类型没定义、函数不存在，或者拼写错误。

**原因分析：**

Go 编译器在编译时把所有符号查一遍，任何找不到的都会报 `undefined`。常见场景：

- 忘记 `import` 对应包
- 函数/变量名拼写错误
- 调用了一个还没定义的函数
- 在不同包之间引用时，忘记写包名前缀（如 `fmt.Println` 写成 `Println`）

**❌ 错误示例：**

```go
package main

func main() {
    Println("hello")       // 错误：应该写 fmt.Println，而且没 import "fmt"
    result := calculate(5) // 错误：calculate 函数不存在
}
```

**✅ 正确示例：**

```go
package main

import "fmt"

func calculate(n int) int {
    return n * 2
}

func main() {
    fmt.Println("hello")
    result := calculate(5)
    fmt.Println(result)
}
```

**解决方法：**

1. **检查拼写**：大小写、下划线。
2. **检查 import**：有没有导入对应的包。
3. **检查作用域**：函数 A 里定义的变量，函数 B 里用不了。
4. **检查跨包引用**：外部包的导出符号首字母必须大写。`mypackage.myFunc` 如果 `myFunc` 首字母小写就无法引用。

**预防建议：**

依靠 IDE 的自动补全和跳转功能，能避免 90% 的拼写和引用错误。

---

### M1.9 `cannot assign to xxx` — 不能给 xxx 赋值

**错误信息（Go 编译器原文）：**

```
./main.go:8:2: cannot assign to someFunc()
./main.go:10:3: cannot assign to "hello"
```

**中文翻译：**

你试图给一个"不可赋值的东西"赋值——比如函数的返回值、字符串字面量、常量等。

**原因分析：**

Go 中只有变量是"可寻址的"（addressable），才能被赋值。函数的返回值、字面量、常量都不是变量，不能放在 `=` 左边。

**❌ 错误示例：**

```go
func getName() string {
    return "Alice"
}

func main() {
    getName() = "Bob" // 错误：函数返回值不能作为赋值目标
    "hello" = "world" // 错误：字面量不能赋值
    const N = 10
    N = 20             // 错误：常量不能重新赋值
}
```

**✅ 正确示例：**

```go
func main() {
    name := getName()
    name = "Bob"    // 正确：变量才能被赋值

    var greeting string = "hello"
    greeting = "world" // 正确
}
```

**解决方法：**

1. 用一个变量把值接住：`x := someFunc()`，然后改 `x`。
2. 如果目的是修改切片/数组元素，检查下标：`arr[i] = val` 要求 `arr` 不是 `nil`。

**预防建议：**

口诀：**只有用 `var` 或 `:=` 创建出来的名字，才能出现在 `=` 左边。**

---

### M1.10 `invalid operation: xxx (mismatched types)` — 操作数类型不匹配

**错误信息（Go 编译器原文）：**

```
./main.go:8:12: invalid operation: "hello" + 1 (mismatched types string and int)
./main.go:10:5: invalid operation: x > y (mismatched types int and string)
```

**中文翻译：**

你对两个类型不兼容的值做了运算——比如把 `string` 和 `int` 相加，或者用 `>` 比较 `int` 和 `string`。

**原因分析：**

Go 不允许跨类型运算。你不能把 `int` 和 `float64` 直接加在一起，也不能比较 `string` 和 `int` 谁大谁小。这些操作在其他语言里可能会自动转换，但 Go 不会。

**❌ 错误示例：**

```go
// 错误1：不同类型相加
result := "age: " + 25

// 错误2：不同类型比较
var a int = 10
var b float64 = 10.5
if a > b { // 报错
    fmt.Println("a > b")
}

// 错误3：对不同类型做运算
sum := 10 + 3.14
```

**✅ 正确示例：**

```go
// 正确1：用 strconv 或 fmt.Sprintf 转换
import "strconv"
result := "age: " + strconv.Itoa(25)

// 正确2：显式类型转换后再比较
var a int = 10
var b float64 = 10.5
if float64(a) > b {
    fmt.Println("a > b")
}

// 正确3：Go 常量中 10 和 3.14 都是无类型常量，所以下面这行其实可以编译
// 但变量运算就会报错
var i int = 10
var f float64 = 3.14
sum := float64(i) + f
```

**解决方法：**

1. 把两边转成同一种类型再运算。
2. 检查你的变量到底是什么类型——用 IDE 的 hover 提示，或在心里自己标注。

**预防建议：**

数字类型统一用 `int` 和 `float64`（除非有特殊理由）。这是 Go 社区的默认选择。

---

### M1.11 `use of unexported identifier` — 引用了未导出的标识符

**错误信息（Go 编译器原文）：**

```
./main.go:10:14: use of unexported identifier 'mypackage.myFunc'
./main.go:12:10: cannot refer to unexported name mypackage.secretVar
```

**中文翻译：**

你试图在包外面使用 `myFunc`，但它在 `mypackage` 包里是小写字母开头的——小写意味着它"不导出"，只有包内部能访问。

**原因分析：**

Go 用首字母大小写来区分公开/私有——大写字母开头 = 导出（exported，包外可见），小写字母开头 = 未导出（unexported，包内私有）。这与 Java 的 `public`/`private` 关键字是同一回事，但 Go 用得更简洁。初学者经常忘记这个规则，写了小写后在外面调不到。

**❌ 错误示例：**

```go
// 文件：mypackage/mypackage.go
package mypackage

func helper() string { // 小写 h，未导出
    return "helper"
}

// 文件：main.go
package main

import "mypackage"

func main() {
    s := mypackage.helper() // 编译错误：helper 未导出
    fmt.Println(s)
}
```

**✅ 正确示例：**

```go
// 文件：mypackage/mypackage.go
package mypackage

func Helper() string { // 大写 H，已导出
    return "helper"
}

// 文件：main.go
package main

import (
    "fmt"
    "mypackage"
)

func main() {
    s := mypackage.Helper() // 正确：Helper 已导出
    fmt.Println(s)
}
```

**解决方法：**

1. 把函数/变量/类型名的首字母改成**大写**。
2. 检查你的调用是否正确——可能你本来就不应该从外部直接调这个函数。

**预防建议：**

写包的函数签名时在心里问一句：「这个函数是给外面用的吗？」→ 是 → 大写；否 → 小写。公开 API 要深思熟虑。

---

### M1.12 `xxx is not a type` — xxx 不是一个类型

**错误信息（Go 编译器原文）：**

```
./main.go:8:5: myFunc is not a type
./main.go:10:8: x is not a type
```

**中文翻译：**

你把一个函数名/变量名/包名放在了"应该写类型"的位置——比如 `var x myFunc`，但 `myFunc` 是一个函数，不是类型。

**原因分析：**

在 Go 里，`type` 关键字定义的东西才能在变量声明中当类型用。如果你把一个函数名或变量名当类型用，编译器就报这个错。

**❌ 错误示例：**

```go
func myFunc() string {
    return "hello"
}

func main() {
    var f myFunc // 错误：myFunc 是函数名，不是类型
    f = myFunc
}
```

**✅ 正确示例：**

```go
func myFunc() string {
    return "hello"
}

func main() {
    var f func() string // 正确：func() string 是函数类型
    f = myFunc

    // 或者更简单：
    f := myFunc
}
```

**解决方法：**

1. 把变量声明改成正确的类型名（如 `func() string`、`int`、`string`）。
2. 如果你想定义一个类型，需要用 `type` 关键字：

```go
type MyFuncType func() string

func myFunc() string { return "hello" }

var f MyFuncType = myFunc // 这样合法
```

**预防建议：**

区分"函数"和"函数类型"——前者是具体实现，后者是签名。`func() string` 是类型，`myFunc` 是值。

---

### M1.13 `too many arguments in call to xxx` — 调用 xxx 时传入了太多参数

**错误信息（Go 编译器原文）：**

```
./main.go:10:10: too many arguments in call to fmt.Println
./main.go:10:10: too many arguments in call to fmt.Println
        have (string, int, string)
        want (...interface{})
    // 上面这种情况其实不会报错（因为 Println 是可变参数），但类似结构会
```

**更典型原文：**

```
./main.go:12:5: too many arguments in call to add
        have (int, int, int)
        want (int, int)
```

**中文翻译：**

调用 `add` 函数时传了 3 个参数，但 `add` 只接受 2 个。

**原因分析：**

调用函数时传的参数个数和函数定义时声明的参数个数不一致。Go 中只有一个特殊函数签名可以接收可变参数，其他函数参数个数都是固定的。

**❌ 错误示例：**

```go
func add(a, b int) int {
    return a + b
}

func main() {
    result := add(1, 2, 3) // 错误：add 只要 2 个参数，传了 3 个
    fmt.Println(result)
}
```

**✅ 正确示例：**

```go
func add(a, b int) int {
    return a + b
}

func main() {
    result := add(1, 2) // 正确：传 2 个参数
    fmt.Println(result)
}
```

**解决方法：**

1. **跳到函数定义**，数清楚参数个数和类型。
2. 如果确实需要传多个值，修改函数签名，使用可变参数 `...int`：

```go
func add(nums ...int) int {
    sum := 0
    for _, n := range nums {
        sum += n
    }
    return sum
}
add(1, 2, 3, 4) // 没问题
```

**预防建议：**

调用函数前先看一下它的定义。IDE 的签名提示功能能帮你避免这种错误。

---

### M1.14 `not enough arguments in call to xxx` — 调用 xxx 时参数不够

**错误信息（Go 编译器原文）：**

```
./main.go:10:10: not enough arguments in call to add
        have (int)
        want (int, int)
```

**中文翻译：**

`add` 函数需要 2 个 `int` 参数，你只传了 1 个。

**原因分析：**

和 M1.13 刚好相反——参数传少了。Go 没有"默认参数值"的概念，每个声明了的参数都必须传入。

**❌ 错误示例：**

```go
func divide(a, b int) int {
    return a / b
}

func main() {
    result := divide(10) // 错误：divide 需要 2 个参数
    fmt.Println(result)
}
```

**✅ 正确示例：**

```go
func main() {
    result := divide(10, 2) // 正确：传 2 个参数
    fmt.Println(result)
}
```

**解决方法：**

检查函数签名，补上缺少的参数，或为函数签名添加你不需要的参数（不建议）。

**预防建议：**

同上，使用 IDE 的签名提示。

---

### M1.15 `xxx declared and not used`（包级别）— 包级变量声明未使用

**错误信息（Go 编译器原文）：**

```
./main.go:5:5: globalVar declared and not used
```

**中文翻译：**

包级别的变量 `globalVar` 声明了但没有被使用。

**原因分析：**

与 M1.2 不同，这里说的是**包级变量**（在 `func` 外面、`package` 下面声明的变量）。注意：包级变量如果只是赋值了但从未被读取，Go 并**不报错**。但如果用 `var` 声明了包级变量后完全没碰过它（也没赋值），Go 编译器**可能**在特定场景下报错，这取决于 Go 版本和代码检查工具（`go vet` 会报告）。

实际上这条规则的准确表述是：**`go vet` 会对包级未使用变量发出警告**，但 `go build` 默认对包级变量不报错。这里列出是为了让你了解在 `go vet` 中常见的提示。

更重要的是，**函数内**的变量（M1.2）和**包级**的变量在 Go 编译器的处理上有差异。包级变量声明后完全不用，某些 lint 工具比如 `staticcheck` 会报。但真正的编译错误只发生在函数内。

---

### M1.16 `expected 'package', found 'xxx'` — 缺少 package 关键字

**错误信息（Go 编译器原文）：**

```
./main.go:1:1: expected 'package', found 'import'
```

**中文翻译：**

Go 源文件的第一行有效代码必须是 `package xxx`。你在 `package` 声明之前写了别的东西（比如 `import` 或者注释之外的代码）。

**原因分析：**

每个 Go 源文件必须以 `package 包名` 开头（包声明之前只能有空行或注释）。如果第一行有效代码不是 `package`，编译器就无法确定这个文件属于哪个包。

**❌ 错误示例：**

```go
import "fmt" // 错误：import 跑到了 package 前面

package main

func main() {
    fmt.Println("hello")
}
```

**✅ 正确示例：**

```go
package main // 正确：package 必须在第一行

import "fmt"

func main() {
    fmt.Println("hello")
}
```

**解决方法：**

确保文件第一行（注释不计）是 `package xxx`。

**预防建议：**

创建新 `.go` 文件后的第一件事：敲下 `package xxx`。

---

### M1.17 `main redeclared in this block` — main 重复声明

**错误信息（Go 编译器原文）：**

```
./main.go:8:6: main redeclared in this block
        previous declaration at ./main.go:5:6
```

**中文翻译：**

在同一个包（同一个代码块）里，`main` 函数被声明了两次。你已经有一个 `func main()` 了，又写了一个。

**原因分析：**

一个包/一个文件夹里，一个函数名只能出现一次（重载在 Go 中不存在）。特别是 `main` 函数——它是程序的入口，只能有一个。

**❌ 错误示例：**

```go
package main

import "fmt"

func main() {
    fmt.Println("first")
}

func main() { // 错误：main 已经在第 5 行声明过了
    fmt.Println("second")
}
```

**✅ 正确示例：**

```go
package main

import "fmt"

func main() {
    fmt.Println("first")
    secondPart()
}

func secondPart() {
    fmt.Println("second")
}
```

**解决方法：**

1. 把第二个 `main` 重命名为其他名字。
2. 如果两个文件都在 `package main` 里，每个文件不能都有自己的 `main` 函数——只能保留一个。

**预防建议：**

每个可执行程序只有一个入口 `func main()`。如果需要多入口，用子命令模式（如 `cobra` 库）。

---

### M1.18 `cannot take the address of xxx` — 不能取 xxx 的地址

**错误信息（Go 编译器原文）：**

```
./main.go:8:5: cannot take the address of "hello"
./main.go:10:3: cannot take the address of someFunc()
./main.go:12:2: cannot take the address of 42
```

**中文翻译：**

你对一个"不可寻址"的值使用了 `&` 取地址操作符——比如字符串字面量、数字字面量、函数返回值。只有变量才有地址。

**原因分析：**

`&` 取的是变量在内存中的位置。一个字面量 `"hello"` 或 `42` 没有固定的内存地址，`someFunc()` 的返回值也是一个临时值，生命周期很短暂，没办法取地址。

**❌ 错误示例：**

```go
func getName() string {
    return "Alice"
}

func main() {
    p1 := &"hello"      // 错误：不能对字面量取地址
    p2 := &getName()    // 错误：不能对函数返回值取地址
    p3 := &42           // 错误：不能对数字字面量取地址
}
```

**✅ 正确示例：**

```go
func main() {
    s := "hello"
    p1 := &s // 正确：对变量取地址

    name := getName()
    p2 := &name // 正确

    n := 42
    p3 := &n // 正确
}
```

**解决方法：**

1. 先把值放进一个变量，再对变量取地址：`x := someFunc(); p := &x`
2. Go 1.18+ 可以用泛型辅助函数，但初学者记住"字面量不能取地址"就够了。

**预防建议：**

口诀：**只有变量才有家（地址），字面量和函数返回值是流浪汉。**

---

### M1.19 `constant xxx overflows int` — 常量溢出

**错误信息（Go 编译器原文）：**

```
./main.go:5:7: constant 999999999999999999999 overflows int
```

**中文翻译：**

你定义了一个常量，它的值太大，超出了 `int` 类型能表示的范围。在 64 位系统上 `int` 最大约 9.22 × 10¹⁸，你写的这个数字超过了它。

**原因分析：**

Go 的常量在编译时就计算。当一个常量被赋值给某个类型的变量时，编译器会检查常量值是否在该类型的合法范围内。如果超出范围，直接报错。

**❌ 错误示例：**

```go
const BigNumber = 999999999999999999999
var n int = BigNumber // 常量值太大，int 装不下
```

**✅ 正确示例：**

```go
// 方案A：用更大的类型
const BigNumber = 999999999999999999999
var n = new(big.Int)
n.SetString("999999999999999999999", 10)

import "math/big" // 需要这个包

// 方案B：如果是合法的 int64 范围，用 int64
var n int64 = 999999999999999
```

**解决方法：**

1. 如果数字在 `int64` 范围内，声明为 `int64`。
2. 如果超出了所有内建类型范围，使用 `math/big` 包。
3. 检查是否手滑多打了数字。

**预防建议：**

处理超大数字（比如加密货币的最小单位、科学计算）时，提前考虑类型范围，优先用 `math/big`。

---

### M1.20 `type xxx is not an expression` — 把类型名当成了表达式

**错误信息（Go 编译器原文）：**

```
./main.go:8:14: type int is not an expression
./main.go:10:10: type string is not an expression
```

**中文翻译：**

你把类型名（`int`、`string`）放在了需要"值/表达式"的位置。比如 `fmt.Println(int)`——`int` 是类型不是值，编译器不知道你想干吗。

**原因分析：**

Go 中类型和值是两回事。你不能把一个类型名当成参数传给一个需要值的函数。

**❌ 错误示例：**

```go
package main

import "fmt"

func main() {
    fmt.Println(int)     // 错误：int 是类型，不能打印
    fmt.Println(string)  // 错误同理
    x := int             // 错误：你可能是想 int(3.14) 做类型转换？
}
```

**✅ 正确示例：**

```go
import (
    "fmt"
    "reflect"
)

func main() {
    // 如果真想打印类型名，用 reflect 包
    var x int
    fmt.Println(reflect.TypeOf(x)) // "int"

    // 如果是想做类型转换
    var f float64 = 3.14
    i := int(f)
    fmt.Println(i) // 3
}
```

**解决方法：**

1. 检查是不是忘了给类型转换加括号和值：`int(x)` 而不是 `int`。
2. 如果只是想看类型信息，用 `reflect.TypeOf()` 或 `fmt.Printf("%T", x)`。

**预防建议：**

`int` 是类型，`int(3.14)` 是转换表达式。这就像 `图纸` vs `按图纸造出来的实物` 的区别。

---

## 二、运行时错误篇（10个最常见 Panic）

> **注意**：以下错误发生在程序运行时（`go run` 后），不是编译期。程序能编译通过，但跑起来就崩溃。

---

### M2.1 `index out of range` — 切片/数组下标越界

**Panic 原文：**

```
panic: runtime error: index out of range [5] with length 3
```

**中文翻译：**

你想访问第 5 号位置的元素，但这个切片只有 3 个元素（长度是 3）。下标跑出了切片边界。

**原因分析：**

Go 的切片和数组都有固定长度。当你用 `s[i]` 访问时，`i` 必须在 `0 ≤ i < len(s)` 范围内。超出这个范围就会 panic。

**❌ 触发代码：**

```go
s := []int{10, 20, 30}
fmt.Println(s[5]) // 长度只有 3，下标 5 越界

// 循环中的经典 Bug
arr := []int{1, 2, 3}
for i := 0; i <= len(arr); i++ { // <= 应该改为 <
    fmt.Println(arr[i]) // i=3 时越界
}
```

**✅ 正确写法：**

```go
s := []int{10, 20, 30}
if len(s) > 5 {
    fmt.Println(s[5])
}

// 用 range 代替手动下标
for _, v := range arr {
    fmt.Println(v)
}
```

**解决方法：**

1. 访问前检查 `len(s)`。
2. 循环遍历尽量用 `range`。
3. 切分切片时确保起止位置不超出长度：`s[a:b]` 要求 `0 ≤ a ≤ b ≤ len(s)`。

---

### M2.2 `nil pointer dereference` — 空指针解引用

**Panic 原文：**

```
panic: runtime error: invalid memory address or nil pointer dereference
```

**中文翻译：**

你试图通过一个 `nil` 指针去访问内存（比如读取字段、调用方法）。指针指向了"空"，里面什么都没有。

**原因分析：**

这是 Go 运行时最常见的 panic，没有之一。任何类型为 `*T` 的变量如果值是 `nil`，在其上做 `.` 操作就会 panic。

**❌ 触发代码：**

```go
var user *User // user 是 nil
fmt.Println(user.Name) // panic

// 函数返回 nil 后没检查
user := findUser(999) // 返回 nil
fmt.Println(user.Name) // panic

// map 是 nil
var m map[string]int
m["key"] = 1 // panic
```

**✅ 正确写法：**

```go
user := findUser(999)
if user != nil {
    fmt.Println(user.Name)
}

// map 要先 make
m := make(map[string]int)
m["key"] = 1
```

**解决方法：**

1. 从函数拿到指针后，立刻检查 `if x != nil`。
2. `map` / `slice` / `channel` 记得用 `make` 初始化。
3. 使用 `go vet` 检查代码，它会标记可能的 nil 解引用。

---

### M2.3 `concurrent map writes` — 并发写 map

**Panic 原文：**

```
fatal error: concurrent map writes
```

**中文翻译：**

同时有多个 goroutine 在往同一个 map 里写数据。Go 的 map 不是并发安全的。

**原因分析：**

Go 的 map 在并发读写/写入时检测到冲突就会直接 fatal——这不是 panic，是更严重的 `fatal error`，程序会立刻终止。即使一个在读一个在写也可能触发。

**❌ 触发代码：**

```go
m := make(map[int]int)

go func() {
    for i := 0; i < 1000; i++ {
        m[i] = i // goroutine 1 在写
    }
}()

go func() {
    for i := 0; i < 1000; i++ {
        m[i] = i * 2 // goroutine 2 也在写
    }
}()

time.Sleep(time.Second)
```

**✅ 正确写法：**

```go
import "sync"

var (
    m   = make(map[int]int)
    mu  sync.RWMutex
)

// 写的时候加锁
go func() {
    for i := 0; i < 1000; i++ {
        mu.Lock()
        m[i] = i
        mu.Unlock()
    }
}()
```

或者直接使用 `sync.Map`（适合特定场景，不总是比 mutex 好）。

**解决方法：**

1. 用 `sync.Mutex` 或 `sync.RWMutex` 保护 map 操作。
2. 考虑用 `sync.Map`（适合读写分离、key 稳定的场景）。
3. 用 channel 串行化对 map 的访问——一个 goroutine 专门管理 map。

---

### M2.4 `send on closed channel` — 向已关闭的 channel 发送

**Panic 原文：**

```
panic: send on closed channel
```

**中文翻译：**

你往一个已经被 `close()` 关闭的 channel 里发数据。Go 不允许这样做。

**原因分析：**

Channel 有开有关。`close(ch)` 之后，再从 `ch` 接收数据是 OK 的（会收到零值，第二个返回值是 `false`），但往里面发送数据就会 panic。常见于多个 goroutine 同时操作同一个 channel 时。

**❌ 触发代码：**

```go
ch := make(chan int, 1)
close(ch)
ch <- 1 // panic：channel 已关闭
```

**✅ 正确写法：**

```go
ch := make(chan int, 1)

go func() {
    defer close(ch) // 发送方负责关闭
    ch <- 1
}()

val, ok := <-ch // 接收方检查 channel 是否关闭
```

**解决方法：**

1. **只在发送方关闭 channel**，接收方永远不要 `close`。
2. 关闭前确保没有 goroutine 在发送。
3. 用 `sync.WaitGroup` 等待所有发送方完成后再 close。

---

### M2.5 `close of closed channel` — 关闭已关闭的 channel

**Panic 原文：**

```
panic: close of closed channel
```

**中文翻译：**

你对同一个 channel 调用了两次 `close()`。

**原因分析：**

和 M2.4 是"关门"系列的两兄弟。`close` 操作只能执行一次。多个 goroutine 都尝试关闭同一个 channel 时会触发。

**❌ 触发代码：**

```go
ch := make(chan int)
close(ch)
close(ch) // panic
```

**✅ 正确写法：**

```go
// 方案A：用 sync.Once 确保只关一次
var once sync.Once
once.Do(func() {
    close(ch)
})

// 方案B：由固定的一个 goroutine 负责关闭
go func() {
    defer close(ch)
    // 发送逻辑...
}()
```

**解决方法：**

1. 用 `sync.Once` 确保 close 只执行一次。
2. 用 `select` + recovery 捕获 panic（不推荐，应用架构设计来避免）。
3. 明确约定：只有一个 goroutine 有权 close。

---

### M2.6 `too many open files` — 打开的文件太多

**Panic 原文：**

```
panic: dial tcp: lookup xxx: too many open files
```
或
```
error: too many open files
```

**中文翻译：**

你的程序打开了太多文件（包括 socket、网络连接也算"文件"），达到了操作系统的上限。

**原因分析：**

Linux/Unix 中一切皆文件——网络连接、管道、普通文件都算。每个进程能同时打开的文件数有上限（`ulimit -n` 可以看到，通常是 1024 或 4096）。如果你的程序打开了大量连接但忘了关，就会撞到这个墙。

**❌ 触发代码：**

```go
for {
    f, _ := os.Open("file.txt")
    // 忘了 defer f.Close() 或 f.Close()
    // 循环很多次后，文件句柄耗尽
}
```

```go
// HTTP 请求后没关闭 Body
for {
    resp, _ := http.Get("http://example.com")
    // 忘了 resp.Body.Close()
}
```

**✅ 正确写法：**

```go
f, err := os.Open("file.txt")
if err != nil {
    log.Fatal(err)
}
defer f.Close() // 打开后立刻 defer Close

resp, err := http.Get("http://example.com")
if err != nil {
    log.Fatal(err)
}
defer resp.Body.Close()
```

**解决方法：**

1. 每次 `Open` / `Get` / `Dial` 后立刻 `defer xxx.Close()`。
2. 用 `lsof -p <PID>`（Linux）排查哪些文件没关。
3. 提高系统上限：`ulimit -n 65535`（治标不治本，先修好代码）。

---

### M2.7 `all goroutines are asleep - deadlock!` — 所有 goroutine 都睡着了（死锁）

**Panic 原文：**

```
fatal error: all goroutines are asleep - deadlock!
```

**中文翻译：**

所有 goroutine 都在等待某个永远不会发生的事件——互相等对方，大家都动不了，程序死锁了。

**原因分析：**

经典死锁模式：Goroutine A 在等 Goroutine B 发数据，Goroutine B 在等 Goroutine A 发数据——谁都不先动。最常见于无缓冲 channel 的使用不当。

**❌ 触发代码：**

```go
ch := make(chan int) // 无缓冲 channel
ch <- 1               // 这里会阻塞，但没有其他 goroutine 来接收
fmt.Println("done")

// 另一个常见死锁：
ch1 := make(chan int)
ch2 := make(chan int)
go func() {
    <-ch1
    ch2 <- 1 // 等 ch1 有数据才能发，但主 goroutine 在等 ch2
}()
<-ch2
ch1 <- 1 // 死锁！
```

**✅ 正确写法：**

```go
// 方案A：用另一个 goroutine 接收
ch := make(chan int)
go func() {
    ch <- 1
}()
fmt.Println(<-ch)

// 方案B：用有缓冲 channel
ch := make(chan int, 1)
ch <- 1
fmt.Println(<-ch)
```

**解决方法：**

1. 无缓冲 channel 的发送和接收必须发生在不同的 goroutine。
2. 用带缓冲的 channel：`make(chan int, N)`。
3. 梳理 goroutine 之间的"等"关系，画出依赖图排查循环等待。

---

### M2.8 `assignment to entry in nil map` — 向 nil map 中写入

**Panic 原文：**

```
panic: assignment to entry in nil map
```

**中文翻译：**

你试图往一个 `nil` map 里写数据。`nil` map 可以读（返回零值）、可以用 `range` 遍历（零次），但**不能写入**。

**原因分析：**

`var m map[string]int` 声明了一个 nil map。读 nil map 返回零值，但写 nil map 会 panic。

**❌ 触发代码：**

```go
var m map[string]int // m 是 nil
m["key"] = 1         // panic

// 全局变量忘了初始化
var cache map[string]string

func initCache() {
    cache["user"] = "Alice" // panic
}
```

**✅ 正确写法：**

```go
m := make(map[string]int) // 初始化
m["key"] = 1

// 或者
var m map[string]int
if m == nil {
    m = make(map[string]int)
}
m["key"] = 1
```

**解决方法：**

1. 声明 map 时直接用 `make`：`m := make(map[K]V)`
2. 写入前检查 nil：`if m == nil { m = make(map[K]V) }`
3. 结构体中的 map 字段在构造函数中初始化。

---

### M2.9 `interface conversion` — 接口类型断言失败

**Panic 原文：**

```
panic: interface conversion: interface {} is int, not string
```

**中文翻译：**

你告诉 Go：「把这个空接口转成 `string`！」结果它实际上是 `int`，Go 就 panic 了。

**原因分析：**

`interface{}`（或 `any`）可以装任何类型。当你用 `x.(string)` 做类型断言时，如果 `x` 实际存的不是 `string`，且你没有用逗号-ok 模式，就会 panic。

**❌ 触发代码：**

```go
var data interface{} = 42
s := data.(string) // panic：data 是 int
fmt.Println(s)
```

**✅ 正确写法：**

```go
var data interface{} = 42

// 安全断言：逗号-ok 模式
if s, ok := data.(string); ok {
    fmt.Println("是 string:", s)
} else {
    fmt.Println("不是 string，实际类型是:", reflect.TypeOf(data))
}
```

**解决方法：**

1. 永远用逗号-ok 模式做类型断言：`v, ok := x.(TargetType)`
2. 使用 `switch v := x.(type)` 处理多种可能的类型。

---

### M2.10 `slice bounds out of range` — 切片操作越界

**Panic 原文：**

```
panic: runtime error: slice bounds out of range [:5] with capacity 3
```

**中文翻译：**

你对一个容量只有 3 的切片做了 `s[:5]` 操作，切片的结束下标不能超过容量。

**原因分析：**

`a[low:high]` 要求 `0 ≤ low ≤ high ≤ cap(a)`，而且 `len(a) ≤ cap(a)`。当 `high` 超过 `cap(a)` 时报错。

**❌ 触发代码：**

```go
s := make([]int, 3, 3) // len=3, cap=3
sub := s[0:5]           // 5 > cap(3)
```

**✅ 正确写法：**

```go
s := make([]int, 3, 5) // len=3, cap=5
sub := s[0:4]           // 合法，4 ≤ cap(5)
```

**解决方法：**

1. 切片前检查 `cap(s)`。
2. 创建切片时指定足够的容量：`make([]int, len, cap)`

---

## 三、常见逻辑错误篇

> 以下错误可以编译通过、能运行，但结果和你预想的完全不同。逻辑错误是最隐蔽的。

---

### M3.1 切片 append 后没有接收返回值

**问题描述：**

`append` 返回一个新的切片，但原切片变量没有被更新，导致你以为追加成功了。

**❌ 错误代码：**

```go
s := []int{1, 2, 3}
append(s, 4)         // 返回值被丢弃了！
fmt.Println(s)        // 还是 [1 2 3]
```

**✅ 正确代码：**

```go
s := []int{1, 2, 3}
s = append(s, 4)     // 用 s 接住返回值
fmt.Println(s)        // [1 2 3 4]
```

**原理：** `append` 可能因为容量不足而分配新的底层数组，返回一个全新的切片。不接收返回值 = 白追加。

---

### M3.2 for range 中取地址的陷阱

**问题描述：**

`for range` 循环中，循环变量 `v` 在每次迭代中**是同一个变量**，只是值被不断覆盖。如果你取了 `v` 的地址存起来，存下的全是最后一个元素的地址。

**❌ 错误代码：**

```go
users := []User{{Name: "Alice"}, {Name: "Bob"}, {Name: "Charlie"}}
var ptrs []*User
for _, u := range users {
    ptrs = append(ptrs, &u) // u 的地址没变过！每次都存了同一个地址
}
for _, p := range ptrs {
    fmt.Println(p.Name) // 三个都是 "Charlie"
}
```

**✅ 正确代码：**

```go
users := []User{{Name: "Alice"}, {Name: "Bob"}, {Name: "Charlie"}}
var ptrs []*User
for i := range users {
    ptrs = append(ptrs, &users[i]) // 取原始切片的元素地址
}
for _, p := range ptrs {
    fmt.Println(p.Name) // Alice, Bob, Charlie
}
```

或者创建副本：

```go
for _, u := range users {
    u := u  // 每次循环创建一个新的局部变量
    ptrs = append(ptrs, &u)
}
```

---

### M3.3 defer 在循环中的问题

**问题描述：**

在循环中写 `defer`，所有 defer 会堆积到函数返回时才执行。如果打开了很多文件/连接，可能导致资源耗尽。

**❌ 错误代码：**

```go
func processFiles(files []string) {
    for _, name := range files {
        f, err := os.Open(name)
        if err != nil {
            log.Println(err)
            continue
        }
        defer f.Close() // 危险：所有文件都要等函数返回才关
        // 处理 f...
    }
}
```

**✅ 正确代码：**

```go
func processFiles(files []string) {
    for _, name := range files {
        func() { // 用一个匿名函数包裹，defer 在每次迭代结束时执行
            f, err := os.Open(name)
            if err != nil {
                log.Println(err)
                return
            }
            defer f.Close()
            // 处理 f...
        }()
    }
}
```

---

### M3.4 字符串 len() 数是字节数，不是字符数

**问题描述：**

Go 的字符串底层是 UTF-8 编码的字节序列。`len("你好")` 返回的是字节数量，不是中文字符数量。

**❌ 错误代码：**

```go
s := "你好"
fmt.Println(len(s)) // 输出 6（每个中文字符占 3 字节），而不是 2
```

**✅ 正确代码：**

```go
import "unicode/utf8"

s := "你好"
fmt.Println(utf8.RuneCountInString(s)) // 输出 2

// 或者转成 []rune
fmt.Println(len([]rune(s))) // 输出 2
```

**注意：** 遍历字符串用 `for _, r := range s` 时，`r` 是正确的 `rune`（Unicode 码点）。

---

### M3.5 map 遍历顺序不确定

**问题描述：**

Go 中 `for k, v := range map` 的遍历顺序是**故意的随机化**——每次运行顺序都可能不同。不要依赖遍历顺序。

**❌ 错误代码：**

```go
m := map[string]int{"a": 1, "b": 2, "c": 3}
for k, v := range m {
    fmt.Println(k, v)
}
// 每次运行输出的顺序可能不同：有时 a→b→c，有时 c→a→b
```

**✅ 正确代码（如果需要有序）：**

```go
m := map[string]int{"a": 1, "b": 2, "c": 3}

// 先取出所有 key，排序
keys := make([]string, 0, len(m))
for k := range m {
    keys = append(keys, k)
}
sort.Strings(keys)

// 按排序后的 key 遍历
for _, k := range keys {
    fmt.Println(k, m[k])
}
```

---

### M3.6 闭包捕获循环变量

**问题描述：**

在循环中创建闭包（函数字面量），闭包捕获了循环变量。当闭包在未来被执行时，循环变量已经变成了循环结束时的值。

**❌ 错误代码：**

```go
var funcs []func()
for i := 0; i < 3; i++ {
    funcs = append(funcs, func() {
        fmt.Println(i) // 闭包捕获了 i
    })
}
for _, f := range funcs {
    f() // 输出：3, 3, 3（而不是 0, 1, 2）
}
```

**✅ 正确代码：**

```go
// 方案A：把 i 作为参数传入
for i := 0; i < 3; i++ {
    func(i int) {
        funcs = append(funcs, func() {
            fmt.Println(i)
        })
    }(i)
}

// 方案B：用局部变量副本（Go 1.22+ 解决了此问题，但旧版需要）
for i := 0; i < 3; i++ {
    i := i // 创建新的局部变量
    funcs = append(funcs, func() {
        fmt.Println(i)
    })
}
```

> **Go 1.22 更新**：从 Go 1.22 开始，`for` 循环中每次迭代都会创建新的循环变量，此问题已在语言层面解决。但若你需要在旧版 Go 上维护代码，仍需注意。

---

## 四、排错方法论

### 4.1 如何阅读 Go 的编译错误信息

Go 编译器的错误信息格式非常规律：

```
文件名:行号:列号: 错误描述
```

**阅读顺序：**

1. **从第一个错误开始修**：后面的错误经常是第一个错误的连锁反应。
2. **行号和列号是金钥匙**：`main.go:15:8` 中的 `15` 是行号，`8` 是该行第 8 个字符的位置。
3. **理解错误关键词**：
   - `declared and not used` → 删掉或使用
   - `undefined` → 拼写错误 / 没导入
   - `cannot use` → 类型不匹配
   - `missing return` → 少写了 `return`
   - `mismatched types` → 运算两边类型不同

**实战案例：**

```
./main.go:18:5: cannot use result (type string) as type int in argument to process
```

译码：在 `main.go` 第 18 行，函数 `process` 需要一个 `int` 参数，但 `result` 是 `string`。回去改 `result` 的类型，或者把 `result` 转成 `int`。

---

### 4.2 二分法定位 Bug

当程序运行结果不对，但你不知道问题出在哪一段时：

1. **在代码中点位置插入 `fmt.Println("--- checkpoint 1 ---")`**
2. 运行，看这个 checkpoint 有没有被打印。
3. 如果有 → Bug 在后面半段；没有 → Bug 在前面半段。
4. 反复二分，直到把范围缩小到几行代码。

这是最原始、最有效的定位方法。配合 `fmt.Printf("变量值 = %+v\n", x)` 查看变量状态。

---

### 4.3 用 `fmt.Println` 调试的技巧

不要只打印 `"here"`，要打印**有意义的信息**：

```go
// ❌ 无效打印
fmt.Println("here")

// ✅ 有效打印
fmt.Printf("[DEBUG] processUser: id=%d, user=%+v\n", id, user)
fmt.Printf("[DEBUG] slice len=%d cap=%d content=%v\n", len(s), cap(s), s)
```

格式化动词速查：

| 动词 | 含义 | 示例 |
|------|------|------|
| `%v` | 默认格式 | `fmt.Printf("%v", user)` |
| `%+v` | 带字段名 | `fmt.Printf("%+v", user)` → `{Name:Alice Age:30}` |
| `%#v` | Go 语法表示 | `fmt.Printf("%#v", user)` |
| `%T` | 打印类型 | `fmt.Printf("%T", x)` → `int` |
| `%d` | 整数 | `fmt.Printf("%d", 42)` |
| `%s` | 字符串 | `fmt.Printf("%s", "hello")` |
| `%p` | 指针地址 | `fmt.Printf("%p", &x)` |

---

### 4.4 如何搜索错误信息

**原则：不要把整个错误信息原封不动贴去搜。**

Go 的编译错误信息中的变量名、类型名、文件名是你项目特有的，别人搜不到。

**正确做法：**

把错误信息拆解为"模板"部分和"具体"部分：

| 原文 | 搜索关键词 |
|------|-----------|
| `cannot use result (type string) as type int` | `golang cannot use (type` |
| `panic: assignment to entry in nil map` | `golang assignment to entry in nil map` |
| `syntax error: unexpected newline` | `golang syntax error unexpected newline` |

**搜索优先级：**
1. **Google**：`golang + 错误信息模板` → 找到 Go 官方文档、Stack Overflow、GitHub Issues。
2. **Go 官方 FAQ**：golang.org/doc/faq ← 非常全面。
3. **Effective Go**：golang.org/doc/effective_go ← 语言最佳实践。
4. **中文社区**：Go 语言中文网、studygolang.com。

---

### 4.5 什么时候该问人 / 问 AI

**先问自己（5 分钟原则）：**

- [ ] 我看明白了错误信息说的是什么吗？
- [ ] 我 Google 了"golang + 错误关键词"吗？
- [ ] 我试着修了一个方向，编译器/运行结果有什么变化？**（带着"我已经试过的方向"去提问）**

**然后问人 / 问 AI：**

贴出以下内容，缺一不可：

1. **你的目标**：我想做什么？
2. **你的代码**：最小可复现示例（见 4.6），**别贴整个项目**。
3. **错误信息**：完整的编译器输出 / panic 栈。
4. **你试过的方法**：试了 A 方案 → 得到 X 错误；试了 B 方案 → 得到 Y 错误。
5. **环境信息**：`go version`、操作系统。

**禁忌：**
- ❌ 只贴代码不解释意图
- ❌ 贴整个项目的几百行代码
- ❌ "报错了怎么办"（不说报的什么错）

---

### 4.6 最小可复现示例的写法

当你要向别人（或向自己）展示一个 Bug，**务必把代码精简到最少**：

**步骤：**

1. 新建一个 `bug_demo.go` 文件。
2. 只保留能触发 Bug 的最少代码——删除与 Bug 无关的业务逻辑。
3. 常量值硬编码，不要依赖外部文件或数据库。
4. 删掉所有第三方库依赖，只用标准库。
5. 在代码注释中写上你期望的结果和实际的结果。

**模板：**

```go
package main

import "fmt"

func main() {
    // ===== 问题描述 =====
    // 期望：输出 6
    // 实际：输出 0

    // ===== 复现代码 =====
    nums := []int{1, 2, 3}
    result := 0
    for _, n := range nums {
        result += n
    }
    fmt.Println(result)
}
```

这样做的好处：
- 80% 的情况在精简过程中你**自己就发现问题了**。
- 剩下的 20%，你也有了让别人快速理解的例程。

---

## 总结

| 错误类别 | 典型特征 | 最快解决路径 |
|----------|----------|-------------|
| 编译错误 | `go build` 报错，程序无法生成 | 读懂错误信息→定位行号→对照本附录 |
| 运行时 Panic | 编译通过，运行中崩溃 | 看 panic 栈第一行→定位行号→检查 nil/边界/channel |
| 逻辑错误 | 编译运行都正常，结果不符合预期 | `fmt.Printf` 打桩→二分法定位→修正逻辑 |

> **记住：Go 编译器的每一次报错，都是它在保护你。真正可怕的不是报错，而是那些悄无声息通过编译、却在生产环境凌晨三点炸掉的逻辑 Bug。**

---

本文件基于 Go 1.21+ 编写。如有新增常见错误，欢迎补充。