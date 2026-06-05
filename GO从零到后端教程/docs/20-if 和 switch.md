# 第20章 · if 和 switch

> "程序之所以'聪明'，是因为它能根据不同的情况做出不同的反应。就像下雨带伞、晴天戴帽子——if和switch就是程序做决策的工具。"

---

## 20.1 if：如果...就...

### 基本写法

```go
score := 85

if score >= 60 {
    fmt.Println("及格了")
}
```

如果 `score >= 60` 成立（`true`），就执行花括号里的代码；不成立就跳过。

Go的if有几个特点：
- 条件表达式**不能加括号**（不像C/Java可以写 `if (score >= 60)`）
- 花括号**必须写**，不能省略（不像C里单行可以省略花括号）
- 花括号的 `{` 必须和 `if` 在同一行

### if-else：如果不...就...

```go
score := 55

if score >= 60 {
    fmt.Println("及格了")
} else {
    fmt.Println("没及格")
}
```

### if-else if-else：多重判断

```go
score := 85

if score >= 90 {
    fmt.Println("优秀")
} else if score >= 80 {
    fmt.Println("良好")
} else if score >= 60 {
    fmt.Println("及格")
} else {
    fmt.Println("不及格")
}
```

注意 `else if` 是写在一行的，不是 `else` 加 `if`。而且 `else` 必须和上一个 `}` 在同一行：

```go
if score >= 60 {
    fmt.Println("及格")
}
else {  // ❌ 编译错误！else必须和}在同一行
    fmt.Println("不及格")
}
```

这是Go语法的强制要求。为什么？还是为了统一风格——不允许你在 `}` 和 `else` 之间插空行。

### 带初始化语句的if（Go特色）

Go的if可以在条件判断前面插入一个**简短的初始化语句**：

```go
if err := doSomething(); err != nil {
    fmt.Println("出错了:", err)
    return
}
```

这个初始化语句在if判断之前执行，定义的变量**只在这个if-else块内有效**，外面访问不到。

看一个更实用的例子：

```go
if user, err := getUserByID(123); err != nil {
    fmt.Println("查用户失败:", err)
    return
} else {
    fmt.Println("用户名:", user.Name)
}
```

这里的 `user` 和 `err` 两个变量只在 `if-else` 块中存在，出了块就没了。这样做的好处是**限制变量的作用域**——一个只在查用户的逻辑里用到的变量，不应该污染外面的代码。

```go
if n := rand.Intn(100); n > 50 {
    fmt.Println(n, "大于50")
} else {
    fmt.Println(n, "小于等于50")
}
// fmt.Println(n)  // ❌ 编译错误！n在这里不存在
```

这种"带初始化语句的if"在Go里非常常见，特别是和错误处理结合时。

> 🤔 **想多一点**：其他语言里你可能先声明变量、再判断、然后用——变量一直活到函数结束。Go故意把变量塞到if里面，强迫你缩小其作用域。好处是当你的函数很长时，你不会在函数末尾还看到一个一百行前声明的变量（心里想"这东西是干嘛的来着？"）。限制作用域让代码逻辑更清晰。

---

## 20.2 Go的if特点总结

跟其他语言对比一下：

| 特性 | C/Java/JS | Go |
|------|-----------|-----|
| 条件括号 | `if (x > 0)` 可以有 | `if x > 0` 不能有 |
| 花括号 | 单行时可省略 | 永远不能省略 |
| 左花括号位置 | 可以换行 | 必须和if同一行 |
| 初始化语句 | 无 | `if x := f(); x > 0` |
| 条件类型 | JS可接受任何值 | 必须bool，不能用0/1/nil代替 |

---

## 20.3 switch：多路分支

当if-else太多时，代码会很难看：

```go
if day == 0 {
    fmt.Println("星期日")
} else if day == 1 {
    fmt.Println("星期一")
} else if day == 2 {
    fmt.Println("星期二")
} else if day == 3 {
    fmt.Println("星期三")
// ...
```

这种情况用switch更清爽：

```go
day := 3

switch day {
case 0:
    fmt.Println("星期日")
case 1:
    fmt.Println("星期一")
case 2:
    fmt.Println("星期二")
case 3:
    fmt.Println("星期三")
case 4:
    fmt.Println("星期四")
case 5:
    fmt.Println("星期五")
case 6:
    fmt.Println("星期六")
default:
    fmt.Println("无效的日期")
}
```

`switch` 后面跟一个表达式，然后和每个 `case` 的值比较，匹配上了就执行对应的代码。

---

## 20.4 Go的switch四大特色

Go的switch和其他语言（特别是C/Java）的switch有很大不同。

### 特色一：不需要break

C/Java程序员最头疼的就是"忘了写break，导致case穿透"。

```java
// Java —— 如果忘了break，会一直往下执行
switch (day) {
    case 1:
        System.out.println("星期一");
        break;  // 忘了写这个，就会继续打印"星期二"
    case 2:
        System.out.println("星期二");
        break;
}
```

Go的设计者认为这个设计太蠢了——**程序员写case几乎从来不是为了"穿透"，break才是99%的情况。** 所以Go的switch**默认不穿透**，匹配到某个case，执行完自动跳出，不需要写break。

```go
switch day {
case 1:
    fmt.Println("星期一")     // 执行完自动跳出，不会去执行case 2
case 2:
    fmt.Println("星期二")
}
```

### 特色二：fallthrough（显式穿透）

那少量的"需要穿透"的场景呢？Go提供了 `fallthrough` 关键字，显式声明"我要继续执行下一个case"：

```go
switch num {
case 1:
    fmt.Println("一")
    fallthrough
case 2:
    fmt.Println("二")  // case 1执行完后，因为fallthrough，会继续执行这一段
default:
    fmt.Println("其他")
}

// 输入num=1时输出：
// 一
// 二
```

`fallthrough` 只能用在case的最后一行，而且只能穿透到下一个case（不能跨多个）。

### 特色三：多值case

一个case可以匹配多个值：

```go
switch day {
case 0, 6:
    fmt.Println("周末")
case 1, 2, 3, 4, 5:
    fmt.Println("工作日")
}
```

### 特色四：无表达式的switch（最酷的特性）

如果你不在 `switch` 后面写表达式，它就变成了一个**更优雅的if-else链**：

```go
score := 85

switch {
case score >= 90:
    fmt.Println("优秀")
case score >= 80:
    fmt.Println("良好")
case score >= 60:
    fmt.Println("及格")
default:
    fmt.Println("不及格")
}
```

每个case后面可以写任意布尔表达式，从上到下依次匹配，第一个为true的case被执行。

这种写法比 `if-else if-else` 更整洁，因为对齐整齐，一眼能看清所有分支。

### 更实用的例子

```go
hour := time.Now().Hour()  // 需 import "time"（标准库详见第33章）

switch {
case hour < 6:
    fmt.Println("凌晨，该睡觉了")
case hour < 9:
    fmt.Println("早上好")
case hour < 12:
    fmt.Println("上午好")
case hour < 14:
    fmt.Println("中午好")
case hour < 18:
    fmt.Println("下午好")
default:
    fmt.Println("晚上好")
}
```

### 带初始化语句的switch

和if一样，switch也支持初始化语句：

```go
switch lang := getUserLanguage(userID); lang {
case "zh":
    fmt.Println("你好")
case "en":
    fmt.Println("Hello")
case "ja":
    fmt.Println("こんにちは")
default:
    fmt.Println("Unknown language:", lang)
}
```

`lang` 变量也只在switch块内有效。

> 🤔 **想多一点**：Go的switch设计可以说是"吸取了所有语言的教训"。C/Java的默认穿透产生了无数Bug，JavaScript的switch用严格比较（===）还好但风格老旧。Go的无表达式switch尤其好用——它本质上就是if-else的"表格化"，让多分支判断一目了然。这也是为什么Go代码里switch出现频率比很多语言高得多。

---

## 本章小结

| 知识点 | 核心要点 |
|--------|----------|
| if基本 | 条件不加括号，花括号不可省略 |
| if-else | else必须和 `}` 同一行 |
| 带初始化语句的if | `if x := f(); x > 0` — 变量作用域限定在if块内 |
| switch基本 | 匹配case后自动跳出，不需要break |
| fallthrough | 显式声明"我要穿透到下一个case" |
| 多值case | `case 0, 6:` 一次匹配多个值 |
| 无表达式switch | `switch { case x>90: ... }` 替代if-else链 |
| 带初始化语句的switch | `switch x := f(); x { ... }` |

---

> 🚀 **下一章**：会判断了，还得会"重复"——循环是做批量处理的基础。Go只有一种循环：for。但它能变出三种花样。第21章见。

---
[← 上一章：19-运算符](19-运算符.md) | [下一章：21-for循环 →](21-for循环.md)