# 附录N：篇末串讲项目

> **设计理念**：每学完一个大篇章，用一个"最小串讲项目"把该篇知识点串起来，让你获得阶段性成就感。
> 每个项目都是一个**可独立运行的小程序**，3-5 步就能完成，代码量控制在 50-200 行。

---

## 项目1：猜数字游戏

- **对应篇章**：第 0-14 章（地基篇）
- **一句话目标**：体验"写代码 → 运行 → 看到结果"的完整流程
- **建议语言**：Go（用最简单语法，预览 Go 的感觉）

### 用到本篇哪些知识点

- 终端操作（第5章）
- 程序的"输入 → 处理 → 输出"模型
- 条件判断和循环的基本直觉

### 功能描述

程序随机生成一个 1-100 的整数，玩家每次猜一个数，程序告诉你是猜大了还是猜小了，直到猜中为止，最后显示猜了多少次。

### 分步实现

**第1步：初始化**

创建文件 `guess.go`，引入 `fmt` 和 `math/rand` 包，生成一个 1-100 的随机数。

```go
package main

import (
    "fmt"
    "math/rand"
)

func main() {
    target := rand.Intn(100) + 1 // 生成 1-100 的随机数
    fmt.Println("我想了一个 1-100 之间的数，你猜猜看？")
}
```

**第2步：写猜数循环**

用一个无限循环来反复读取玩家输入，直到猜对。

```go
var guess int
for {
    fmt.Print("请输入你猜的数字：")
    fmt.Scan(&guess)
    // 判断大小...
}
```

**第3步：给出提示并计数**

每次猜完比较大小，给出"大了""小了"提示，猜中后退出并显示次数。

```go
attempts := 0
for {
    attempts++
    fmt.Print("请输入你猜的数字：")
    fmt.Scan(&guess)

    if guess > target {
        fmt.Println("大了！再试试。")
    } else if guess < target {
        fmt.Println("小了！再试试。")
    } else {
        fmt.Printf("恭喜你猜对了！你一共猜了 %d 次。\n", attempts)
        break
    }
}
```

### 完整代码

<details>
<summary>点击展开 guess.go</summary>

```go
package main

import (
    "fmt"
    "math/rand"
)

func main() {
    target := rand.Intn(100) + 1
    attempts := 0
    var guess int

    fmt.Println("=== 猜数字游戏 ===")
    fmt.Println("我想了一个 1-100 之间的数，你猜猜看？")

    for {
        attempts++
        fmt.Print("请输入你猜的数字：")
        fmt.Scan(&guess)

        if guess > target {
            fmt.Println("大了！再试试。")
        } else if guess < target {
            fmt.Println("小了！再试试。")
        } else {
            fmt.Printf("恭喜你猜对了！你一共猜了 %d 次。\n", attempts)
            break
        }
    }
}
```

</details>

### 运行效果展示

```
=== 猜数字游戏 ===
我想了一个 1-100 之间的数，你猜猜看？
请输入你猜的数字：50
小了！再试试。
请输入你猜的数字：75
大了！再试试。
请输入你猜的数字：62
小了！再试试。
请输入你猜的数字：68
恭喜你猜对了！你一共猜了 4 次。
```

### 扩展挑战

1. **难度选择**：游戏开始时让玩家选简单（1-50）、中等（1-100）、困难（1-200）。
2. **排行榜**：记录每次游戏的猜数次数，结束后显示历次最佳成绩。

---

## 项目2：个人记账本

- **对应篇章**：第 15-39 章（Go语言篇）
- **一句话目标**：用 Go 核心语法写一个命令行记账工具，把收入支出存到文件里

### 用到本篇哪些知识点

- 变量与常量（第17章）
- 控制流 if/switch/for（第20-21章）
- 切片 Slice（第23章）
- Map（第24章）
- 结构体 Struct + 方法（第29-30章）
- 函数（第26-27章）
- 文件读写（第38章）
- 序列化 JSON（第39章）

### 功能描述

一个命令行程序，支持以下操作：
1. **添加记录**：输入金额、类别（收入/支出）、备注
2. **查看列表**：显示所有记录，带序号
3. **统计总额**：显示总收入、总支出、结余
4. **保存到文件**：将记录保存为 JSON 文件
5. **从文件加载**：启动时自动加载已有记录

### 分步实现

**第1步：定义数据结构**

```go
type Record struct {
    Amount   float64 `json:"amount"`
    Category string  `json:"category"` // "income" 或 "expense"
    Note     string  `json:"note"`
}

type Ledger struct {
    Records []Record `json:"records"`
}
```

**第2步：实现核心方法**

给 `Ledger` 添加添加记录、显示列表、统计总额的方法。

```go
func (l *Ledger) Add(amount float64, category, note string) {
    l.Records = append(l.Records, Record{Amount: amount, Category: category, Note: note})
}

func (l *Ledger) List() {
    for i, r := range l.Records {
        tag := "收入"
        if r.Category == "expense" {
            tag = "支出"
        }
        fmt.Printf("%d. [%s] ¥%.2f - %s\n", i+1, tag, r.Amount, r.Note)
    }
}

func (l *Ledger) Summary() {
    var income, expense float64
    for _, r := range l.Records {
        if r.Category == "income" {
            income += r.Amount
        } else {
            expense += r.Amount
        }
    }
    fmt.Printf("总收入: ¥%.2f  总支出: ¥%.2f  结余: ¥%.2f\n", income, expense, income-expense)
}
```

**第3步：实现文件读写**

用 `encoding/json` + `os.ReadFile` / `os.WriteFile` 实现持久化。

```go
func (l *Ledger) Save(filename string) error {
    data, err := json.MarshalIndent(l, "", "  ")
    if err != nil {
        return err
    }
    return os.WriteFile(filename, data, 0644)
}

func Load(filename string) (*Ledger, error) {
    data, err := os.ReadFile(filename)
    if err != nil {
        if os.IsNotExist(err) {
            return &Ledger{}, nil
        }
        return nil, err
    }
    var ledger Ledger
    if err := json.Unmarshal(data, &ledger); err != nil {
        return nil, err
    }
    return &ledger, nil
}
```

**第4步：写主菜单循环**

用 `switch` 实现命令行菜单。

```go
func main() {
    ledger, _ := Load("ledger.json")
    scanner := bufio.NewScanner(os.Stdin)

    for {
        fmt.Println("\n=== 个人记账本 ===")
        fmt.Println("1. 添加记录  2. 查看列表  3. 统计总额  4. 保存  5. 退出")
        fmt.Print("请选择：")
        scanner.Scan()
        choice := scanner.Text()

        switch choice {
        case "1":
            // 添加记录逻辑
        case "2":
            ledger.List()
        case "3":
            ledger.Summary()
        case "4":
            ledger.Save("ledger.json")
            fmt.Println("已保存！")
        case "5":
            return
        }
    }
}
```

### 完整代码

<details>
<summary>点击展开 main.go</summary>

```go
package main

import (
    "bufio"
    "encoding/json"
    "fmt"
    "os"
    "strconv"
    "strings"
)

type Record struct {
    Amount   float64 `json:"amount"`
    Category string  `json:"category"`
    Note     string  `json:"note"`
}

type Ledger struct {
    Records []Record `json:"records"`
}

func (l *Ledger) Add(amount float64, category, note string) {
    l.Records = append(l.Records, Record{Amount: amount, Category: category, Note: note})
}

func (l *Ledger) List() {
    if len(l.Records) == 0 {
        fmt.Println("暂无记录。")
        return
    }
    for i, r := range l.Records {
        tag := "收入"
        if r.Category == "expense" {
            tag = "支出"
        }
        fmt.Printf("%d. [%s] ¥%.2f - %s\n", i+1, tag, r.Amount, r.Note)
    }
}

func (l *Ledger) Summary() {
    var income, expense float64
    for _, r := range l.Records {
        if r.Category == "income" {
            income += r.Amount
        } else {
            expense += r.Amount
        }
    }
    fmt.Printf("总收入: ¥%.2f  总支出: ¥%.2f  结余: ¥%.2f\n", income, expense, income-expense)
}

func (l *Ledger) Save(filename string) error {
    data, err := json.MarshalIndent(l, "", "  ")
    if err != nil {
        return err
    }
    return os.WriteFile(filename, data, 0644)
}

func Load(filename string) (*Ledger, error) {
    data, err := os.ReadFile(filename)
    if err != nil {
        if os.IsNotExist(err) {
            return &Ledger{}, nil
        }
        return nil, err
    }
    var ledger Ledger
    if err := json.Unmarshal(data, &ledger); err != nil {
        return nil, err
    }
    return &ledger, nil
}

func main() {
    ledger, err := Load("ledger.json")
    if err != nil {
        fmt.Println("加载文件失败:", err)
        return
    }
    scanner := bufio.NewScanner(os.Stdin)

    for {
        fmt.Println("\n=== 个人记账本 ===")
        fmt.Println("1. 添加记录  2. 查看列表  3. 统计总额  4. 保存  5. 退出")
        fmt.Print("请选择：")
        scanner.Scan()
        choice := strings.TrimSpace(scanner.Text())

        switch choice {
        case "1":
            fmt.Print("金额：")
            scanner.Scan()
            amountStr := strings.TrimSpace(scanner.Text())
            amount, err := strconv.ParseFloat(amountStr, 64)
            if err != nil {
                fmt.Println("金额格式错误")
                continue
            }

            fmt.Print("类别（income/expense）：")
            scanner.Scan()
            category := strings.TrimSpace(scanner.Text())
            if category != "income" && category != "expense" {
                fmt.Println("类别必须是 income 或 expense")
                continue
            }

            fmt.Print("备注：")
            scanner.Scan()
            note := strings.TrimSpace(scanner.Text())

            ledger.Add(amount, category, note)
            fmt.Println("已添加！")

        case "2":
            ledger.List()

        case "3":
            ledger.Summary()

        case "4":
            if err := ledger.Save("ledger.json"); err != nil {
                fmt.Println("保存失败:", err)
            } else {
                fmt.Println("已保存到 ledger.json")
            }

        case "5":
            fmt.Println("再见！")
            return

        default:
            fmt.Println("无效选择，请重新输入")
        }
    }
}
```

</details>

### 运行效果展示

```
=== 个人记账本 ===
1. 添加记录  2. 查看列表  3. 统计总额  4. 保存  5. 退出
请选择：1
金额：10000
类别（income/expense）：income
备注：工资
已添加！

请选择：1
金额：35.5
类别（income/expense）：expense
备注：午饭
已添加！

请选择：2
1. [收入] ¥10000.00 - 工资
2. [支出] ¥35.50 - 午饭

请选择：3
总收入: ¥10000.00  总支出: ¥35.50  结余: ¥9964.50

请选择：4
已保存到 ledger.json
```

### 扩展挑战

1. **按类别筛选**：增加菜单项，按收入/支出分别显示记录。
2. **月度统计**：给记录加上日期字段，支持按月份统计收支。

---

## 项目3：链表性能测试器

- **对应篇章**：第 40-49 章（数据结构与算法篇）
- **一句话目标**：用 Go 实测对比切片和链表在不同场景下的性能差异，直观感受时间复杂度

### 用到本篇哪些知识点

- 切片内部原理（第42章）
- 链表实现（第43章）
- 时间复杂度（第41章）
- 排序算法（第48章）

### 功能描述

程序对 Go 内置切片和自己写的单链表，分别测试以下操作的耗时：
- **头部插入** 10000 个元素
- **尾部追加** 10000 个元素
- **按索引查找** 10000 次

最终打印一张耗时对比表。

### 分步实现

**第1步：实现单链表**

```go
type Node struct {
    Value int
    Next  *Node
}

type LinkedList struct {
    Head *Node
}

func (l *LinkedList) InsertHead(v int) {
    l.Head = &Node{Value: v, Next: l.Head}
}

func (l *LinkedList) Append(v int) {
    newNode := &Node{Value: v}
    if l.Head == nil {
        l.Head = newNode
        return
    }
    cur := l.Head
    for cur.Next != nil {
        cur = cur.Next
    }
    cur.Next = newNode
}

func (l *LinkedList) Get(index int) (int, bool) {
    cur := l.Head
    for i := 0; i < index && cur != nil; i++ {
        cur = cur.Next
    }
    if cur == nil {
        return 0, false
    }
    return cur.Value, true
}
```

**第2步：写测试函数**

用 `time.Now()` 和 `time.Since()` 来计时。

```go
func testSliceInsertHead(n int) time.Duration {
    start := time.Now()
    s := make([]int, 0, n)
    for i := 0; i < n; i++ {
        s = append([]int{i}, s...) // 头部插入
    }
    return time.Since(start)
}

func testListInsertHead(n int) time.Duration {
    start := time.Now()
    l := &LinkedList{}
    for i := 0; i < n; i++ {
        l.InsertHead(i)
    }
    return time.Since(start)
}
```

**第3步：打印对比表**

```go
fmt.Println(strings.Repeat("=", 60))
fmt.Printf("%-20s %15s %15s\n", "操作 (N=10000)", "切片耗时", "链表耗时")
fmt.Println(strings.Repeat("-", 60))
fmt.Printf("%-20s %15v %15v\n", "头部插入", sliceInsert, listInsert)
fmt.Printf("%-20s %15v %15v\n", "尾部追加", sliceAppend, listAppend)
fmt.Printf("%-20s %15v %15v\n", "按索引查找", sliceFind, listFind)
```

### 完整代码

<details>
<summary>点击展开 main.go</summary>

```go
package main

import (
    "fmt"
    "strings"
    "time"
)

type Node struct {
    Value int
    Next  *Node
}

type LinkedList struct {
    Head *Node
}

func (l *LinkedList) InsertHead(v int) {
    l.Head = &Node{Value: v, Next: l.Head}
}

func (l *LinkedList) Append(v int) {
    newNode := &Node{Value: v}
    if l.Head == nil {
        l.Head = newNode
        return
    }
    cur := l.Head
    for cur.Next != nil {
        cur = cur.Next
    }
    cur.Next = newNode
}

func (l *LinkedList) Get(index int) (int, bool) {
    cur := l.Head
    for i := 0; i < index && cur != nil; i++ {
        cur = cur.Next
    }
    if cur == nil {
        return 0, false
    }
    return cur.Value, true
}

func testSliceInsertHead(n int) time.Duration {
    start := time.Now()
    s := make([]int, 0, n)
    for i := 0; i < n; i++ {
        s = append([]int{i}, s...)
    }
    return time.Since(start)
}

func testListInsertHead(n int) time.Duration {
    start := time.Now()
    l := &LinkedList{}
    for i := 0; i < n; i++ {
        l.InsertHead(i)
    }
    return time.Since(start)
}

func testSliceAppend(n int) time.Duration {
    start := time.Now()
    s := make([]int, 0, n)
    for i := 0; i < n; i++ {
        s = append(s, i)
    }
    return time.Since(start)
}

func testListAppend(n int) time.Duration {
    start := time.Now()
    l := &LinkedList{}
    for i := 0; i < n; i++ {
        l.Append(i)
    }
    return time.Since(start)
}

func testSliceFind(n int) time.Duration {
    s := make([]int, n)
    for i := 0; i < n; i++ {
        s[i] = i
    }
    start := time.Now()
    for i := 0; i < n; i++ {
        _ = s[i]
    }
    return time.Since(start)
}

func testListFind(n int) time.Duration {
    l := &LinkedList{}
    for i := 0; i < n; i++ {
        l.Append(i)
    }
    start := time.Now()
    for i := 0; i < n; i++ {
        l.Get(i)
    }
    return time.Since(start)
}

func main() {
    n := 10000

    sliceInsert := testSliceInsertHead(n)
    listInsert := testListInsertHead(n)
    sliceAppend := testSliceAppend(n)
    listAppend := testListAppend(n)
    sliceFind := testSliceFind(n)
    listFind := testListFind(n)

    fmt.Println(strings.Repeat("=", 60))
    fmt.Printf("%-20s %15s %15s\n", fmt.Sprintf("操作 (N=%d)", n), "切片耗时", "链表耗时")
    fmt.Println(strings.Repeat("-", 60))
    fmt.Printf("%-20s %15v %15v\n", "头部插入", sliceInsert, listInsert)
    fmt.Printf("%-20s %15v %15v\n", "尾部追加", sliceAppend, listAppend)
    fmt.Printf("%-20s %15v %15v\n", "按索引查找", sliceFind, listFind)
    fmt.Println(strings.Repeat("=", 60))
    fmt.Println("\n结论：")
    fmt.Println("- 头部插入：链表 O(1) 远快于切片 O(n)")
    fmt.Println("- 尾部追加：切片 O(1) 分摊 ≈ 链表 O(n)（无尾指针时）")
    fmt.Println("- 索引查找：切片 O(1) 远快于链表 O(n)")
}
```

</details>

### 运行效果展示

```
============================================================
操作 (N=10000)                   切片耗时          链表耗时
------------------------------------------------------------
头部插入                      1.2345ms           213.4µs
尾部追加                       87.6µs           1.5678ms
按索引查找                      3.4µs           2.3456ms
============================================================

结论：
- 头部插入：链表 O(1) 远快于切片 O(n)
- 尾部追加：切片 O(1) 分摊 ≈ 链表 O(n)（无尾指针时）
- 索引查找：切片 O(1) 远快于链表 O(n)
```

### 扩展挑战

1. **给链表加尾指针**：优化 `Append` 为 O(1)，重新测试尾部追加性能。
2. **加大数据量并画图**：用不同 N 值（1K、10K、100K）各测一轮，观察耗时随 N 增长的趋势。

---

## 项目4：学生成绩管理系统

- **对应篇章**：第 50-64 章（数据库篇）
- **一句话目标**：用 Go + MySQL + GORM 实现学生成绩的增删改查和统计排名

### 用到本篇哪些知识点

- MySQL 基础操作（第50-51章）
- SQL 查询与聚合（第52章）
- JOIN 查询（第53章）
- 表设计（第54章）
- 索引原理（第55章）
- Go 操作 MySQL / GORM（第59章）

### 功能描述

一个命令行管理工具，支持：
1. **添加学生**（姓名、班级）
2. **录入成绩**（学生ID、科目、分数）
3. **查看某学生所有成绩**
4. **按科目排名**（显示该科目所有学生的成绩排序）
5. **计算平均分排名**（所有科目平均分，降序）

### 分步实现

**第1步：定义 Model**

```go
type Student struct {
    ID    uint   `gorm:"primaryKey"`
    Name  string `gorm:"size:50;not null"`
    Class string `gorm:"size:50"`
}

type Score struct {
    ID        uint    `gorm:"primaryKey"`
    StudentID uint    `gorm:"index;not null"`
    Subject   string  `gorm:"size:50;not null"`
    Score     float64 `gorm:"not null"`
    Student   Student `gorm:"foreignKey:StudentID"`
}
```

**第2步：初始化数据库连接和自动迁移**

```go
db, err := gorm.Open(mysql.Open("root:your_password_here@tcp(127.0.0.1:3306)/school?charset=utf8mb4&parseTime=True"), &gorm.Config{})
if err != nil {
    panic("数据库连接失败: " + err.Error())
}
db.AutoMigrate(&Student{}, &Score{})
```

**第3步：实现排名查询**

按科目排名：
```go
var scores []Score
db.Where("subject = ?", "数学").Order("score desc").Find(&scores)
```

平均分排名（原生SQL）：
```go
db.Raw(`
    SELECT s.name, AVG(sc.score) as avg_score
    FROM students s
    JOIN scores sc ON s.id = sc.student_id
    GROUP BY s.id, s.name
    ORDER BY avg_score DESC
`).Scan(&results)
```

### 完整代码

<details>
<summary>点击展开 main.go</summary>

```go
package main

import (
    "bufio"
    "fmt"
    "os"
    "strconv"
    "strings"

    "gorm.io/driver/mysql"
    "gorm.io/gorm"
)

type Student struct {
    ID    uint   `gorm:"primaryKey"`
    Name  string `gorm:"size:50;not null"`
    Class string `gorm:"size:50"`
}

type Score struct {
    ID        uint    `gorm:"primaryKey"`
    StudentID uint    `gorm:"index;not null"`
    Subject   string  `gorm:"size:50;not null"`
    Score     float64 `gorm:"not null"`
    Student   Student `gorm:"foreignKey:StudentID"`
}

func addStudent(db *gorm.DB, scanner *bufio.Scanner) {
    fmt.Print("姓名：")
    scanner.Scan()
    name := strings.TrimSpace(scanner.Text())
    fmt.Print("班级：")
    scanner.Scan()
    class := strings.TrimSpace(scanner.Text())
    db.Create(&Student{Name: name, Class: class})
    fmt.Println("学生添加成功！")
}

func addScore(db *gorm.DB, scanner *bufio.Scanner) {
    var students []Student
    db.Find(&students)
    fmt.Println("学生列表：")
    for _, s := range students {
        fmt.Printf("  ID:%d  %s (%s)\n", s.ID, s.Name, s.Class)
    }

    fmt.Print("学生ID：")
    scanner.Scan()
    sid, _ := strconv.Atoi(strings.TrimSpace(scanner.Text()))
    fmt.Print("科目：")
    scanner.Scan()
    subject := strings.TrimSpace(scanner.Text())
    fmt.Print("分数：")
    scanner.Scan()
    score, _ := strconv.ParseFloat(strings.TrimSpace(scanner.Text()), 64)

    db.Create(&Score{StudentID: uint(sid), Subject: subject, Score: score})
    fmt.Println("成绩录入成功！")
}

func viewStudentScores(db *gorm.DB, scanner *bufio.Scanner) {
    fmt.Print("学生ID：")
    scanner.Scan()
    sid, _ := strconv.Atoi(strings.TrimSpace(scanner.Text()))

    var scores []Score
    db.Preload("Student").Where("student_id = ?", sid).Find(&scores)

    if len(scores) == 0 {
        fmt.Println("该学生暂无成绩。")
        return
    }
    fmt.Printf("学生：%s\n", scores[0].Student.Name)
    for _, sc := range scores {
        fmt.Printf("  %s: %.1f\n", sc.Subject, sc.Score)
    }
}

func rankBySubject(db *gorm.DB, scanner *bufio.Scanner) {
    fmt.Print("科目：")
    scanner.Scan()
    subject := strings.TrimSpace(scanner.Text())

    var scores []Score
    db.Preload("Student").Where("subject = ?", subject).Order("score desc").Find(&scores)

    fmt.Printf("\n=== %s 成绩排名 ===\n", subject)
    for i, sc := range scores {
        fmt.Printf("%d. %s - %.1f\n", i+1, sc.Student.Name, sc.Score)
    }
}

type AvgRank struct {
    Name     string
    AvgScore float64
}

func rankByAverage(db *gorm.DB) {
    var results []AvgRank
    db.Raw(`
        SELECT s.name, ROUND(AVG(sc.score), 1) as avg_score
        FROM students s
        JOIN scores sc ON s.id = sc.student_id
        GROUP BY s.id, s.name
        ORDER BY avg_score DESC
    `).Scan(&results)

    fmt.Println("\n=== 平均分排名 ===")
    for i, r := range results {
        fmt.Printf("%d. %s - %.1f\n", i+1, r.Name, r.AvgScore)
    }
}

func main() {
    dsn := "root:your_password_here@tcp(127.0.0.1:3306)/school?charset=utf8mb4&parseTime=True&loc=Local"
    db, err := gorm.Open(mysql.Open(dsn), &gorm.Config{})
    if err != nil {
        fmt.Println("数据库连接失败:", err)
        fmt.Println("请确认：1) MySQL已启动  2) 数据库school已创建  3) 密码正确")
        return
    }
    db.AutoMigrate(&Student{}, &Score{})
    scanner := bufio.NewScanner(os.Stdin)

    for {
        fmt.Println("\n=== 学生成绩管理系统 ===")
        fmt.Println("1.添加学生  2.录入成绩  3.查看学生成绩  4.科目排名  5.平均分排名  6.退出")
        fmt.Print("请选择：")
        scanner.Scan()
        choice := strings.TrimSpace(scanner.Text())

        switch choice {
        case "1":
            addStudent(db, scanner)
        case "2":
            addScore(db, scanner)
        case "3":
            viewStudentScores(db, scanner)
        case "4":
            rankBySubject(db, scanner)
        case "5":
            rankByAverage(db)
        case "6":
            fmt.Println("再见！")
            return
        default:
            fmt.Println("无效选择")
        }
    }
}
```

</details>

### 运行效果展示

```
=== 学生成绩管理系统 ===
1.添加学生  2.录入成绩  3.查看学生成绩  4.科目排名  5.平均分排名  6.退出
请选择：1
姓名：张三
班级：一班
学生添加成功！

请选择：1
姓名：李四
班级：一班
学生添加成功！

请选择：2
学生列表：
  ID:1  张三 (一班)
  ID:2  李四 (一班)
学生ID：1
科目：数学
分数：95
成绩录入成功！

请选择：4
科目：数学

=== 数学 成绩排名 ===
1. 张三 - 95.0
2. 李四 - 82.0

请选择：5

=== 平均分排名 ===
1. 张三 - 91.5
2. 李四 - 80.0
```

### 扩展挑战

1. **分页查看**：成绩列表支持分页，每页10条。
2. **删除与修改**：增加"修改分数"和"删除学生"功能注意级联处理。

---

## 项目5：图书管理API

- **对应篇章**：第 65-76 章（Web框架篇）
- **一句话目标**：用 Gin 框架写一个图书管理 RESTful API，包含中间件、参数校验和 Swagger 文档

### 用到本篇哪些知识点

- RESTful API 设计（第65章）
- Gin 路由与路由组（第66-67章）
- 请求处理、参数绑定（第68章）
- 中间件（第69章）
- 统一响应处理（第70、74章）
- 参数校验（第71章）
- 项目结构设计（第72章）
- Swagger 文档（第75章）

### 功能描述

一个图书管理 HTTP API，支持：
- `GET    /api/v1/books`       — 分页查询图书列表（支持关键词搜索）
- `GET    /api/v1/books/:id`   — 获取单本图书详情
- `POST   /api/v1/books`       — 新增图书（校验必填字段）
- `PUT    /api/v1/books/:id`   — 更新图书信息
- `DELETE /api/v1/books/:id`   — 删除图书
- `POST   /api/v1/books/:id/borrow` — 借阅图书
- `POST   /api/v1/books/:id/return` — 归还图书

### 分步实现

**第1步：项目结构和 Model**

```
book-api/
├── main.go
├── model/
│   └── book.go
├── handler/
│   └── book.go
├── middleware/
│   └── logger.go
└── go.mod
```

Model 定义：
```go
type Book struct {
    ID        uint      `gorm:"primaryKey" json:"id"`
    Title     string    `json:"title" binding:"required"`
    Author    string    `json:"author" binding:"required"`
    ISBN      string    `json:"isbn"`
    Status    string    `json:"status"` // available / borrowed
    CreatedAt time.Time `json:"created_at"`
    UpdatedAt time.Time `json:"updated_at"`
}
```

**第2步：统一响应封装**

```go
type Response struct {
    Code    int         `json:"code"`
    Message string      `json:"message"`
    Data    interface{} `json:"data,omitempty"`
}

func Success(c *gin.Context, data interface{}) {
    c.JSON(http.StatusOK, Response{Code: 0, Message: "ok", Data: data})
}

func Error(c *gin.Context, code int, msg string) {
    c.JSON(code, Response{Code: code, Message: msg})
}
```

**第3步：实现 Handler**

```go
func CreateBook(c *gin.Context) {
    var book model.Book
    if err := c.ShouldBindJSON(&book); err != nil {
        Error(c, 400, "参数校验失败: "+err.Error())
        return
    }
    book.Status = "available"
    db.Create(&book)
    Success(c, book)
}
```

**第4步：注册路由 + 中间件**

```go
r := gin.Default()
r.Use(middleware.RequestLogger())

v1 := r.Group("/api/v1")
{
    v1.GET("/books", ListBooks)
    v1.GET("/books/:id", GetBook)
    v1.POST("/books", CreateBook)
    v1.PUT("/books/:id", UpdateBook)
    v1.DELETE("/books/:id", DeleteBook)
    v1.POST("/books/:id/borrow", BorrowBook)
    v1.POST("/books/:id/return", ReturnBook)
}
```

### 完整代码

<details>
<summary>点击展开 main.go</summary>

```go
package main

import (
    "net/http"
    "strconv"
    "time"

    "github.com/gin-gonic/gin"
    "gorm.io/driver/sqlite"
    "gorm.io/gorm"
)

type Book struct {
    ID        uint      `gorm:"primaryKey" json:"id"`
    Title     string    `gorm:"size:200;not null" json:"title" binding:"required"`
    Author    string    `gorm:"size:100;not null" json:"author" binding:"required"`
    ISBN      string    `gorm:"size:20" json:"isbn"`
    Status    string    `gorm:"size:20;default:available" json:"status"`
    Borrower  string    `gorm:"size:50" json:"borrower,omitempty"`
    CreatedAt time.Time `json:"created_at"`
    UpdatedAt time.Time `json:"updated_at"`
}

type Response struct {
    Code    int         `json:"code"`
    Message string      `json:"message"`
    Data    interface{} `json:"data,omitempty"`
}

type PageResponse struct {
    Code    int         `json:"code"`
    Message string      `json:"message"`
    Data    interface{} `json:"data"`
    Total   int64       `json:"total"`
    Page    int         `json:"page"`
    Size    int         `json:"size"`
}

var db *gorm.DB

func Success(c *gin.Context, data interface{}) {
    c.JSON(http.StatusOK, Response{Code: 0, Message: "ok", Data: data})
}

func Error(c *gin.Context, httpCode int, msg string) {
    c.JSON(httpCode, Response{Code: httpCode, Message: msg})
}

func RequestLogger() gin.HandlerFunc {
    return func(c *gin.Context) {
        start := time.Now()
        c.Next()
        latency := time.Since(start)
        println(c.Request.Method, c.Request.URL.Path, c.Writer.Status(), latency.String())
    }
}

func ListBooks(c *gin.Context) {
    page, _ := strconv.Atoi(c.DefaultQuery("page", "1"))
    size, _ := strconv.Atoi(c.DefaultQuery("size", "10"))
    keyword := c.Query("keyword")

    var books []Book
    var total int64
    query := db.Model(&Book{})
    if keyword != "" {
        query = query.Where("title LIKE ? OR author LIKE ?", "%"+keyword+"%", "%"+keyword+"%")
    }
    query.Count(&total)
    query.Offset((page - 1) * size).Limit(size).Find(&books)

    c.JSON(http.StatusOK, PageResponse{
        Code: 0, Message: "ok", Data: books,
        Total: total, Page: page, Size: size,
    })
}

func GetBook(c *gin.Context) {
    id := c.Param("id")
    var book Book
    if err := db.First(&book, id).Error; err != nil {
        Error(c, 404, "图书不存在")
        return
    }
    Success(c, book)
}

func CreateBook(c *gin.Context) {
    var book Book
    if err := c.ShouldBindJSON(&book); err != nil {
        Error(c, 400, "参数校验失败: "+err.Error())
        return
    }
    book.Status = "available"
    db.Create(&book)
    Success(c, book)
}

func UpdateBook(c *gin.Context) {
    id := c.Param("id")
    var book Book
    if err := db.First(&book, id).Error; err != nil {
        Error(c, 404, "图书不存在")
        return
    }
    var input Book
    if err := c.ShouldBindJSON(&input); err != nil {
        Error(c, 400, "参数校验失败: "+err.Error())
        return
    }
    db.Model(&book).Updates(map[string]interface{}{
        "title":  input.Title,
        "author": input.Author,
        "isbn":   input.ISBN,
    })
    Success(c, book)
}

func DeleteBook(c *gin.Context) {
    id := c.Param("id")
    if err := db.Delete(&Book{}, id).Error; err != nil {
        Error(c, 500, "删除失败")
        return
    }
    Success(c, nil)
}

func BorrowBook(c *gin.Context) {
    id := c.Param("id")
    var book Book
    if err := db.First(&book, id).Error; err != nil {
        Error(c, 404, "图书不存在")
        return
    }
    if book.Status != "available" {
        Error(c, 400, "图书已被借出")
        return
    }
    var input struct {
        Borrower string `json:"borrower" binding:"required"`
    }
    if err := c.ShouldBindJSON(&input); err != nil {
        Error(c, 400, "请输入借阅人姓名")
        return
    }
    db.Model(&book).Updates(map[string]interface{}{
        "status":   "borrowed",
        "borrower": input.Borrower,
    })
    Success(c, book)
}

func ReturnBook(c *gin.Context) {
    id := c.Param("id")
    var book Book
    if err := db.First(&book, id).Error; err != nil {
        Error(c, 404, "图书不存在")
        return
    }
    if book.Status != "borrowed" {
        Error(c, 400, "图书未被借出")
        return
    }
    db.Model(&book).Updates(map[string]interface{}{
        "status":   "available",
        "borrower": "",
    })
    Success(c, book)
}

func main() {
    var err error
    db, err = gorm.Open(sqlite.Open("books.db"), &gorm.Config{})
    if err != nil {
        panic("数据库初始化失败")
    }
    db.AutoMigrate(&Book{})

    r := gin.Default()
    r.Use(RequestLogger())

    v1 := r.Group("/api/v1")
    {
        v1.GET("/books", ListBooks)
        v1.GET("/books/:id", GetBook)
        v1.POST("/books", CreateBook)
        v1.PUT("/books/:id", UpdateBook)
        v1.DELETE("/books/:id", DeleteBook)
        v1.POST("/books/:id/borrow", BorrowBook)
        v1.POST("/books/:id/return", ReturnBook)
    }

    fmt.Println("图书管理API 启动在 http://localhost:8080")
    r.Run(":8080")
}
```

> **注意**：完整代码中顶部还需添加 `import "fmt"`。

</details>

### 运行效果展示

```bash
# 新增图书
curl -X POST http://localhost:8080/api/v1/books \
  -H "Content-Type: application/json" \
  -d '{"title":"Go语言编程","author":"张三","isbn":"978-7-111-12345"}'

# 返回
{"code":0,"message":"ok","data":{"id":1,"title":"Go语言编程","author":"张三","isbn":"978-7-111-12345","status":"available","created_at":"..."}}

# 借阅
curl -X POST http://localhost:8080/api/v1/books/1/borrow \
  -H "Content-Type: application/json" \
  -d '{"borrower":"李四"}'

# 分页搜索
curl "http://localhost:8080/api/v1/books?page=1&size=5&keyword=Go"
```

### 扩展挑战

1. **添加 Swagger 文档**：用 `swaggo/swag` 给所有接口加上注释，生成 Swagger 页面。
2. **按状态筛选**：给列表接口加 `status` 查询参数，只返回"可借"或"已借出"的图书。

---

## 项目6：带权限的笔记API

- **对应篇章**：第 77-84 章（认证安全篇）
- **一句话目标**：实现用户注册登录、JWT 认证、RBAC 权限控制（用户只能看自己的笔记，管理员能看所有人的）

### 用到本篇哪些知识点

- JWT 认证（第79章）
- RBAC 权限控制（第81章）
- bcrypt 密码加密（第83章，加密基础）
- Gin 中间件（第69章）

### 功能描述

一个笔记管理 API：
- `POST   /api/register`          — 注册（用户名+密码）
- `POST   /api/login`             — 登录，返回 JWT
- `GET    /api/notes`             — 获取自己的笔记列表（普通用户）/ 所有人的笔记（管理员）
- `POST   /api/notes`             — 创建笔记
- `GET    /api/notes/:id`         — 获取笔记详情（只能看自己的，管理员除外）
- `PUT    /api/notes/:id`         — 更新笔记
- `DELETE /api/notes/:id`         — 删除笔记

### 分步实现

**第1步：Model + 数据库初始化**

```go
type User struct {
    ID       uint   `gorm:"primaryKey" json:"id"`
    Username string `gorm:"uniqueIndex;size:50" json:"username"`
    Password string `gorm:"size:200" json:"-"`
    Role     string `gorm:"size:20;default:user" json:"role"` // user / admin
}

type Note struct {
    ID       uint   `gorm:"primaryKey" json:"id"`
    UserID   uint   `gorm:"index" json:"user_id"`
    Title    string `gorm:"size:200" json:"title"`
    Content  string `gorm:"type:text" json:"content"`
}
```

**第2步：注册与登录（bcrypt + JWT）**

```go
func Register(c *gin.Context) {
    var input struct {
        Username string `json:"username" binding:"required"`
        Password string `json:"password" binding:"required,min=6"`
    }
    // ... 校验、哈希密码、创建用户
    hashed, _ := bcrypt.GenerateFromPassword([]byte(input.Password), bcrypt.DefaultCost)
    db.Create(&User{Username: input.Username, Password: string(hashed)})
}

func Login(c *gin.Context) {
    // ... 校验用户名密码
    bcrypt.CompareHashAndPassword([]byte(user.Password), []byte(input.Password))
    // 生成 JWT
    token := jwt.NewWithClaims(jwt.SigningMethodHS256, jwt.MapClaims{
        "user_id":  user.ID,
        "username": user.Username,
        "role":     user.Role,
        "exp":      time.Now().Add(24 * time.Hour).Unix(),
    })
    tokenString, _ := token.SignedString(jwtSecret)
}
```

**第3步：认证 + 授权中间件**

```go
func AuthMiddleware() gin.HandlerFunc {
    return func(c *gin.Context) {
        tokenString := c.GetHeader("Authorization")
        tokenString = strings.TrimPrefix(tokenString, "Bearer ")
        // 解析 JWT，把 user_id 和 role 存入 Context
        token, _ := jwt.Parse(tokenString, func(t *jwt.Token) (interface{}, error) {
            return jwtSecret, nil
        })
        claims := token.Claims.(jwt.MapClaims)
        c.Set("user_id", uint(claims["user_id"].(float64)))
        c.Set("role", claims["role"].(string))
        c.Next()
    }
}
```

**第4步：带权限过滤的 Handler**

```go
func ListNotes(c *gin.Context) {
    userID := c.GetUint("user_id")
    role := c.GetString("role")

    var notes []Note
    query := db.Model(&Note{})
    if role != "admin" {
        query = query.Where("user_id = ?", userID) // 普通用户只看自己的
    }
    query.Find(&notes)
    Success(c, notes)
}
```

### 完整代码

<details>
<summary>点击展开 main.go</summary>

```go
package main

import (
    "net/http"
    "strings"
    "time"

    "github.com/gin-gonic/gin"
    "github.com/golang-jwt/jwt/v5"
    "golang.org/x/crypto/bcrypt"
    "gorm.io/driver/sqlite"
    "gorm.io/gorm"
)

type User struct {
    ID       uint   `gorm:"primaryKey" json:"id"`
    Username string `gorm:"uniqueIndex;size:50;not null" json:"username"`
    Password string `gorm:"size:200;not null" json:"-"`
    Role     string `gorm:"size:20;default:user" json:"role"`
}

type Note struct {
    ID      uint   `gorm:"primaryKey" json:"id"`
    UserID  uint   `gorm:"index;not null" json:"user_id"`
    Title   string `gorm:"size:200;not null" json:"title" binding:"required"`
    Content string `gorm:"type:text" json:"content"`
}

var db *gorm.DB
var jwtSecret = []byte("your-secret-key-change-in-production")

type Response struct {
    Code    int         `json:"code"`
    Message string      `json:"message"`
    Data    interface{} `json:"data,omitempty"`
}

func Success(c *gin.Context, data interface{}) {
    c.JSON(http.StatusOK, Response{Code: 0, Message: "ok", Data: data})
}

func Error(c *gin.Context, httpCode int, msg string) {
    c.JSON(httpCode, Response{Code: httpCode, Message: msg})
}

func AuthMiddleware() gin.HandlerFunc {
    return func(c *gin.Context) {
        authHeader := c.GetHeader("Authorization")
        if authHeader == "" {
            Error(c, 401, "未提供认证令牌")
            c.Abort()
            return
        }
        tokenString := strings.TrimPrefix(authHeader, "Bearer ")
        token, err := jwt.Parse(tokenString, func(t *jwt.Token) (interface{}, error) {
            return jwtSecret, nil
        })
        if err != nil || !token.Valid {
            Error(c, 401, "令牌无效或已过期")
            c.Abort()
            return
        }
        claims, ok := token.Claims.(jwt.MapClaims)
        if !ok {
            Error(c, 401, "令牌解析失败")
            c.Abort()
            return
        }
        c.Set("user_id", uint(claims["user_id"].(float64)))
        c.Set("role", claims["role"].(string))
        c.Next()
    }
}

func Register(c *gin.Context) {
    var input struct {
        Username string `json:"username" binding:"required,min=3"`
        Password string `json:"password" binding:"required,min=6"`
    }
    if err := c.ShouldBindJSON(&input); err != nil {
        Error(c, 400, "参数错误: "+err.Error())
        return
    }
    var exist User
    if db.Where("username = ?", input.Username).First(&exist).Error == nil {
        Error(c, 400, "用户名已存在")
        return
    }
    hashed, _ := bcrypt.GenerateFromPassword([]byte(input.Password), bcrypt.DefaultCost)
    db.Create(&User{Username: input.Username, Password: string(hashed)})
    Success(c, gin.H{"username": input.Username})
}

func Login(c *gin.Context) {
    var input struct {
        Username string `json:"username" binding:"required"`
        Password string `json:"password" binding:"required"`
    }
    if err := c.ShouldBindJSON(&input); err != nil {
        Error(c, 400, "参数错误")
        return
    }
    var user User
    if db.Where("username = ?", input.Username).First(&user).Error != nil {
        Error(c, 401, "用户名或密码错误")
        return
    }
    if bcrypt.CompareHashAndPassword([]byte(user.Password), []byte(input.Password)) != nil {
        Error(c, 401, "用户名或密码错误")
        return
    }
    token := jwt.NewWithClaims(jwt.SigningMethodHS256, jwt.MapClaims{
        "user_id":  user.ID,
        "username": user.Username,
        "role":     user.Role,
        "exp":      time.Now().Add(24 * time.Hour).Unix(),
    })
    tokenString, _ := token.SignedString(jwtSecret)
    Success(c, gin.H{"token": tokenString})
}

func ListNotes(c *gin.Context) {
    userID := c.GetUint("user_id")
    role := c.GetString("role")

    var notes []Note
    query := db.Model(&Note{})
    if role != "admin" {
        query = query.Where("user_id = ?", userID)
    }
    query.Find(&notes)
    Success(c, notes)
}

func CreateNote(c *gin.Context) {
    userID := c.GetUint("user_id")
    var note Note
    if err := c.ShouldBindJSON(&note); err != nil {
        Error(c, 400, "参数错误: "+err.Error())
        return
    }
    note.UserID = userID
    db.Create(&note)
    Success(c, note)
}

func GetNote(c *gin.Context) {
    userID := c.GetUint("user_id")
    role := c.GetString("role")

    var note Note
    if db.First(&note, c.Param("id")).Error != nil {
        Error(c, 404, "笔记不存在")
        return
    }
    if role != "admin" && note.UserID != userID {
        Error(c, 403, "无权访问此笔记")
        return
    }
    Success(c, note)
}

func UpdateNote(c *gin.Context) {
    userID := c.GetUint("user_id")
    role := c.GetString("role")

    var note Note
    if db.First(&note, c.Param("id")).Error != nil {
        Error(c, 404, "笔记不存在")
        return
    }
    if role != "admin" && note.UserID != userID {
        Error(c, 403, "无权修改此笔记")
        return
    }
    var input Note
    if err := c.ShouldBindJSON(&input); err != nil {
        Error(c, 400, "参数错误")
        return
    }
    db.Model(&note).Updates(map[string]interface{}{
        "title": input.Title, "content": input.Content,
    })
    Success(c, note)
}

func DeleteNote(c *gin.Context) {
    userID := c.GetUint("user_id")
    role := c.GetString("role")

    var note Note
    if db.First(&note, c.Param("id")).Error != nil {
        Error(c, 404, "笔记不存在")
        return
    }
    if role != "admin" && note.UserID != userID {
        Error(c, 403, "无权删除此笔记")
        return
    }
    db.Delete(&note)
    Success(c, nil)
}

func main() {
    var err error
    db, err = gorm.Open(sqlite.Open("notes.db"), &gorm.Config{})
    if err != nil {
        panic("数据库初始化失败")
    }
    db.AutoMigrate(&User{}, &Note{})

    r := gin.Default()

    r.POST("/api/register", Register)
    r.POST("/api/login", Login)

    auth := r.Group("/api")
    auth.Use(AuthMiddleware())
    {
        auth.GET("/notes", ListNotes)
        auth.POST("/notes", CreateNote)
        auth.GET("/notes/:id", GetNote)
        auth.PUT("/notes/:id", UpdateNote)
        auth.DELETE("/notes/:id", DeleteNote)
    }

    println("笔记API 启动在 http://localhost:8080")
    r.Run(":8080")
}
```

</details>

### 运行效果展示

```bash
# 注册
curl -X POST http://localhost:8080/api/register \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","password":"123456"}'
# => {"code":0,"message":"ok","data":{"username":"alice"}}

# 登录
curl -X POST http://localhost:8080/api/login \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","password":"123456"}'
# => {"code":0,"message":"ok","data":{"token":"eyJhbGciOiJIUzI1NiIs..."}}

# 创建笔记（带上JWT）
curl -X POST http://localhost:8080/api/notes \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{"title":"学习笔记","content":"今天学了JWT认证"}'

# alice 看不到 bob 的笔记
# admin 可以看到所有人的笔记
```

### 扩展挑战

1. **Token 刷新**：实现 `/api/refresh` 接口，用 refresh token 换取新 access token。
2. **软删除**：笔记删除时只标记 `deleted_at`，不真正从数据库删除——考察你的 GORM 软删除知识。

---

## 项目7：异步邮件发送器

- **对应篇章**：第 85-90 章（消息队列篇）
- **一句话目标**：HTTP 接收发邮件请求 → 入队 RabbitMQ → 消费者异步发送 → 记录日志

### 用到本篇哪些知识点

- RabbitMQ 基础（第86-87章）
- Goroutine（第34章）
- Channel（第35章）
- Go 操作消息队列（第90章）

### 功能描述

一个邮件发送服务，拆分为生产者和消费者：
- **HTTP API**（生产者）：
  - `POST /api/send` — 接收 `{to, subject, body}`，将邮件任务入队 RabbitMQ
- **消费者**（独立 Goroutine）：
  - 从 RabbitMQ 队列取任务，模拟发送邮件（打印日志），记录结果到文件

> **环境说明**：本项目需要本地运行 RabbitMQ。如果暂时没装 RabbitMQ，代码中提供了**纯 Channel 模式**作为降级方案，不依赖外部中间件即可运行。

### 分步实现

**第1步：定义消息结构体**

```go
type EmailTask struct {
    To      string `json:"to"`
    Subject string `json:"subject"`
    Body    string `json:"body"`
}
```

**第2步：HTTP 生产者（入队）**

```go
func SendEmailHandler(ch chan<- EmailTask) gin.HandlerFunc {
    return func(c *gin.Context) {
        var task EmailTask
        if err := c.ShouldBindJSON(&task); err != nil {
            c.JSON(400, gin.H{"error": err.Error()})
            return
        }
        ch <- task // 放入 Channel（模拟入队）
        c.JSON(200, gin.H{"message": "邮件已加入发送队列"})
    }
}
```

**第3步：消费者 Goroutine**

```go
func emailWorker(ch <-chan EmailTask, logFile *os.File) {
    for task := range ch {
        // 模拟发送
        time.Sleep(1 * time.Second)
        result := fmt.Sprintf("[%s] 邮件已发送 -> %s | 主题: %s\n",
            time.Now().Format("2006-01-02 15:04:05"),
            task.To, task.Subject)
        fmt.Print(result)
        logFile.WriteString(result)
    }
}
```

**第4步：主函数组装**

```go
func main() {
    ch := make(chan EmailTask, 100) // 带缓冲 Channel 模拟消息队列
    logFile, _ := os.OpenFile("email.log", os.O_CREATE|os.O_APPEND|os.O_WRONLY, 0644)
    defer logFile.Close()

    // 启动消费者
    go emailWorker(ch, logFile)

    // 启动 HTTP 服务器（生产者）
    r := gin.Default()
    r.POST("/api/send", SendEmailHandler(ch))
    r.Run(":8080")
}
```

### 完整代码

<details>
<summary>点击展开 main.go（纯 Channel 版，无需 RabbitMQ）</summary>

```go
package main

import (
    "fmt"
    "net/http"
    "os"
    "time"

    "github.com/gin-gonic/gin"
)

type EmailTask struct {
    To      string `json:"to" binding:"required"`
    Subject string `json:"subject" binding:"required"`
    Body    string `json:"body" binding:"required"`
}

func emailWorker(ch <-chan EmailTask, logFile *os.File) {
    for task := range ch {
        time.Sleep(800 * time.Millisecond)
        entry := fmt.Sprintf("[%s] 发送成功 | 收件人:%s | 主题:%s\n",
            time.Now().Format("2006-01-02 15:04:05"),
            task.To, task.Subject)
        fmt.Print(entry)
        logFile.WriteString(entry)
    }
}

func SendEmailHandler(ch chan<- EmailTask) gin.HandlerFunc {
    return func(c *gin.Context) {
        var task EmailTask
        if err := c.ShouldBindJSON(&task); err != nil {
            c.JSON(http.StatusBadRequest, gin.H{
                "code": 400, "message": "参数错误: " + err.Error(),
            })
            return
        }
        select {
        case ch <- task:
            c.JSON(http.StatusOK, gin.H{
                "code": 0, "message": "邮件已加入发送队列",
                "data":   task,
            })
        default:
            c.JSON(http.StatusTooManyRequests, gin.H{
                "code": 429, "message": "队列已满，请稍后再试",
            })
        }
    }
}

func main() {
    taskQueue := make(chan EmailTask, 100)

    logFile, err := os.OpenFile("email.log", os.O_CREATE|os.O_APPEND|os.O_WRONLY, 0644)
    if err != nil {
        panic("无法创建日志文件: " + err.Error())
    }
    defer logFile.Close()

    go emailWorker(taskQueue, logFile)

    r := gin.Default()
    r.POST("/api/send", SendEmailHandler(taskQueue))

    fmt.Println("异步邮件发送器 启动在 http://localhost:8080")
    fmt.Println("队列容量: 100, 模式: Channel (无需 RabbitMQ)")
    r.Run(":8080")
}
```

</details>

<details>
<summary>点击展开 main.go（RabbitMQ 版）</summary>

```go
package main

import (
    "encoding/json"
    "fmt"
    "log"
    "net/http"
    "os"
    "time"

    "github.com/gin-gonic/gin"
    amqp "github.com/rabbitmq/amqp091-go"
)

type EmailTask struct {
    To      string `json:"to" binding:"required"`
    Subject string `json:"subject" binding:"required"`
    Body    string `json:"body" binding:"required"`
}

var ch *amqp.Channel

func initQueue() {
    conn, err := amqp.Dial("amqp://guest:guest@localhost:5672/")
    if err != nil {
        log.Fatalf("RabbitMQ 连接失败: %v", err)
    }
    ch, err = conn.Channel()
    if err != nil {
        log.Fatalf("Channel 创建失败: %v", err)
    }
    _, err = ch.QueueDeclare("email_queue", true, false, false, false, nil)
    if err != nil {
        log.Fatalf("队列声明失败: %v", err)
    }
    fmt.Println("RabbitMQ 连接成功，队列: email_queue")
}

func emailConsumer(logFile *os.File) {
    msgs, err := ch.Consume("email_queue", "", false, false, false, false, nil)
    if err != nil {
        log.Fatalf("消费者注册失败: %v", err)
    }
    for msg := range msgs {
        var task EmailTask
        json.Unmarshal(msg.Body, &task)
        time.Sleep(800 * time.Millisecond) // 模拟发送
        entry := fmt.Sprintf("[%s] 发送成功 | 收件人:%s | 主题:%s\n",
            time.Now().Format("2006-01-02 15:04:05"), task.To, task.Subject)
        fmt.Print(entry)
        logFile.WriteString(entry)
        msg.Ack(false) // 手动确认
    }
}

func SendEmailHandler(c *gin.Context) {
    var task EmailTask
    if err := c.ShouldBindJSON(&task); err != nil {
        c.JSON(http.StatusBadRequest, gin.H{"code": 400, "message": "参数错误"})
        return
    }
    body, _ := json.Marshal(task)
    err := ch.Publish("", "email_queue", false, false, amqp.Publishing{
        ContentType: "application/json", Body: body,
    })
    if err != nil {
        c.JSON(500, gin.H{"code": 500, "message": "入队失败"})
        return
    }
    c.JSON(200, gin.H{"code": 0, "message": "邮件已加入队列"})
}

func main() {
    initQueue()
    logFile, _ := os.OpenFile("email.log", os.O_CREATE|os.O_APPEND|os.O_WRONLY, 0644)
    defer logFile.Close()
    go emailConsumer(logFile)

    r := gin.Default()
    r.POST("/api/send", SendEmailHandler)
    fmt.Println("异步邮件发送器 (RabbitMQ) 启动在 http://localhost:8080")
    r.Run(":8080")
}
```

</details>

### 运行效果展示

```bash
# 终端1：启动服务
$ go run main.go
异步邮件发送器 启动在 http://localhost:8080
队列容量: 100, 模式: Channel (无需 RabbitMQ)

# 终端2：发送请求
curl -X POST http://localhost:8080/api/send \
  -H "Content-Type: application/json" \
  -d '{"to":"user@example.com","subject":"欢迎","body":"欢迎注册！"}'

# 终端1 输出：
[2026-05-28 14:30:01] 发送成功 | 收件人:user@example.com | 主题:欢迎

# email.log 文件内容同上
```

### 扩展挑战

1. **多消费者并发**：启动 3 个消费者 Goroutine 同时消费队列，观察并发效果。
2. **失败重试**：发送失败时将任务放入"死信队列"，支持最多重试 3 次。

---

## 项目8：URL 短链接服务

- **对应篇章**：第 91-98 章（系统设计篇）
- **一句话目标**：实现长链转短链、短链重定向、访问计数，理解高并发短链服务的核心设计

### 用到本篇哪些知识点

- 设计模式 — 策略模式 / 单例模式（第91章）
- 微服务思想 — 单一职责（第93章）
- 高并发设计 — 缓存 / 唯一ID生成（第97章）
- 哈希表（映射关系本质）

### 功能描述

- `POST /api/shorten` — 提交长URL，返回短码（如 `abc123`）
- `GET /:code` — 访问短码，302 重定向到原始URL，访问计数 +1
- `GET /api/stats/:code` — 查看某短码的访问次数

短码生成策略：用 Base62（0-9, a-z, A-Z）编码一个自增 ID。

### 分步实现

**第1步：短码生成器**

```go
const base62Chars = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"

func toBase62(n int64) string {
    if n == 0 {
        return "0"
    }
    result := ""
    for n > 0 {
        result = string(base62Chars[n%62]) + result
        n /= 62
    }
    return result
}
```

**第2步：存储层**

用内存 Map + sync.RWMutex（项目规模小，无需引入 Redis）：

```go
type Store struct {
    mu      sync.RWMutex
    urls    map[string]string // code -> longURL
    counter map[string]int64  // code -> visit count
    nextID  int64
}
```

**第3步：核心逻辑**

```go
func (s *Store) Shorten(longURL string) string {
    s.mu.Lock()
    defer s.mu.Unlock()
    s.nextID++
    code := toBase62(s.nextID)
    s.urls[code] = longURL
    s.counter[code] = 0
    return code
}

func (s *Store) Expand(code string) (string, bool) {
    s.mu.RLock()
    defer s.mu.RUnlock()
    url, ok := s.urls[code]
    return url, ok
}

func (s *Store) IncrementVisit(code string) {
    s.mu.Lock()
    defer s.mu.Unlock()
    s.counter[code]++
}
```

### 完整代码

<details>
<summary>点击展开 main.go</summary>

```go
package main

import (
    "fmt"
    "net/http"
    "sync"

    "github.com/gin-gonic/gin"
)

const base62Chars = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"

func toBase62(n int64) string {
    if n == 0 {
        return "0"
    }
    result := ""
    for n > 0 {
        result = string(base62Chars[n%62]) + result
        n /= 62
    }
    return result
}

type Store struct {
    mu      sync.RWMutex
    urls    map[string]string
    counter map[string]int64
    nextID  int64
}

func NewStore() *Store {
    return &Store{
        urls:    make(map[string]string),
        counter: make(map[string]int64),
        nextID:  0,
    }
}

func (s *Store) Shorten(longURL string) string {
    s.mu.Lock()
    defer s.mu.Unlock()
    s.nextID++
    code := toBase62(s.nextID)
    s.urls[code] = longURL
    s.counter[code] = 0
    return code
}

func (s *Store) Expand(code string) (string, bool) {
    s.mu.RLock()
    defer s.mu.RUnlock()
    url, ok := s.urls[code]
    return url, ok
}

func (s *Store) IncrementVisit(code string) {
    s.mu.Lock()
    defer s.mu.Unlock()
    s.counter[code]++
}

func (s *Store) GetStats(code string) (string, int64, bool) {
    s.mu.RLock()
    defer s.mu.RUnlock()
    url, ok := s.urls[code]
    if !ok {
        return "", 0, false
    }
    return url, s.counter[code], true
}

func main() {
    store := NewStore()
    r := gin.Default()

    r.POST("/api/shorten", func(c *gin.Context) {
        var input struct {
            URL string `json:"url" binding:"required"`
        }
        if err := c.ShouldBindJSON(&input); err != nil {
            c.JSON(400, gin.H{"code": 400, "message": "请提供有效URL"})
            return
        }
        code := store.Shorten(input.URL)
        c.JSON(200, gin.H{
            "code":       0,
            "short_url":  fmt.Sprintf("http://localhost:8080/%s", code),
            "short_code": code,
        })
    })

    r.GET("/:code", func(c *gin.Context) {
        code := c.Param("code")
        // 过滤 API 路由
        if code == "api" {
            c.Next()
            return
        }
        url, ok := store.Expand(code)
        if !ok {
            c.JSON(404, gin.H{"code": 404, "message": "短链接不存在"})
            return
        }
        store.IncrementVisit(code)
        c.Redirect(http.StatusFound, url)
    })

    r.GET("/api/stats/:code", func(c *gin.Context) {
        code := c.Param("code")
        url, visits, ok := store.GetStats(code)
        if !ok {
            c.JSON(404, gin.H{"code": 404, "message": "短链接不存在"})
            return
        }
        c.JSON(200, gin.H{
            "code":       0,
            "short_code": code,
            "long_url":   url,
            "visits":     visits,
        })
    })

    fmt.Println("URL 短链接服务 启动在 http://localhost:8080")
    r.Run(":8080")
}
```

</details>

### 运行效果展示

```bash
# 缩短
curl -X POST http://localhost:8080/api/shorten \
  -H "Content-Type: application/json" \
  -d '{"url":"https://example.com/very/long/url/that/needs/shortening"}'
# => {"code":0,"short_url":"http://localhost:8080/1","short_code":"1"}

# 访问短链（浏览器打开或 curl -L）
curl -L http://localhost:8080/1
# => 302 重定向到 https://example.com/very/long/url/...

# 查看统计
curl http://localhost:8080/api/stats/1
# => {"code":0,"short_code":"1","long_url":"https://example.com/...","visits":5}
```

### 扩展挑战

1. **自定义短码**：允许用户在缩短时指定自定义短码（如 `my-blog`），需要校验重复。
2. **过期机制**：给短链接加 `expire_at` 字段，过期后返回 410 Gone。

---

## 项目9：一键部署脚本

- **对应篇章**：第 99-105 章（DevOps篇）
- **一句话目标**：给项目5（图书管理API）编写 Dockerfile + docker-compose + 部署脚本，实现一键启动

### 用到本篇哪些知识点

- Docker 容器化（第102章）
- Docker Compose 多服务编排（第102章）
- Shell 脚本基础（第100章）
- Nginx 反向代理（第96、76章）
- CI/CD 思想（第103章）

### 功能描述

为图书管理 API（项目5）制作全套部署方案：
1. **Dockerfile**：将 Go 代码编译为二进制，构建精简镜像
2. **docker-compose.yml**：编排 API 服务 + Nginx 反向代理
3. **nginx.conf**：配置反向代理规则
4. **deploy.sh**：一键部署脚本（构建 + 启动 + 健康检查）

### 分步实现

**第1步：编写 Dockerfile（多阶段构建）**

```dockerfile
# 阶段1：编译
FROM golang:1.22-alpine AS builder
WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -o /book-api .

# 阶段2：运行
FROM alpine:3.19
RUN apk add --no-cache ca-certificates tzdata
COPY --from=builder /book-api /book-api
EXPOSE 8080
CMD ["/book-api"]
```

**第2步：编写 docker-compose.yml**

```yaml
version: '3.8'
services:
  api:
    build: .
    container_name: book-api
    restart: always
    volumes:
      - ./books.db:/books.db
    networks:
      - app-net

  nginx:
    image: nginx:alpine
    container_name: book-nginx
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/conf.d/default.conf
    depends_on:
      - api
    networks:
      - app-net

networks:
  app-net:
    driver: bridge
```

**第3步：编写 nginx.conf**

```nginx
server {
    listen 80;
    server_name localhost;

    location / {
        proxy_pass http://api:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

**第4步：编写 deploy.sh**

```bash
#!/bin/bash
set -e

echo "=== 图书管理API 一键部署 ==="
echo "1. 停止旧容器..."
docker-compose down 2>/dev/null || true

echo "2. 构建镜像..."
docker-compose build

echo "3. 启动服务..."
docker-compose up -d

echo "4. 等待服务就绪..."
sleep 3

echo "5. 健康检查..."
if curl -f http://localhost/api/v1/books > /dev/null 2>&1; then
    echo "✓ 部署成功！API 可通过 http://localhost/api/v1/books 访问"
else
    echo "✗ 健康检查失败，请检查日志: docker-compose logs"
    exit 1
fi
```

### 完整代码（所有文件）

<details>
<summary>点击展开 Dockerfile</summary>

```dockerfile
FROM golang:1.22-alpine AS builder
WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -o /book-api .

FROM alpine:3.19
RUN apk add --no-cache ca-certificates tzdata
COPY --from=builder /book-api /book-api
EXPOSE 8080
CMD ["/book-api"]
```

</details>

<details>
<summary>点击展开 docker-compose.yml</summary>

```yaml
version: '3.8'
services:
  api:
    build: .
    container_name: book-api
    restart: always
    volumes:
      - ./books.db:/books.db
    networks:
      - app-net

  nginx:
    image: nginx:alpine
    container_name: book-nginx
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/conf.d/default.conf
    depends_on:
      - api
    networks:
      - app-net

networks:
  app-net:
    driver: bridge
```

</details>

<details>
<summary>点击展开 nginx.conf</summary>

```nginx
server {
    listen 80;
    server_name localhost;

    location / {
        proxy_pass http://api:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

</details>

<details>
<summary>点击展开 deploy.sh</summary>

```bash
#!/bin/bash
set -e

echo "=== 图书管理API 一键部署 ==="

echo "1. 停止旧容器..."
docker-compose down 2>/dev/null || true

echo "2. 构建镜像..."
docker-compose build

echo "3. 启动服务..."
docker-compose up -d

echo "4. 等待服务就绪..."
sleep 3

echo "5. 健康检查..."
if curl -f http://localhost/api/v1/books > /dev/null 2>&1; then
    echo "✓ 部署成功！API 可通过 http://localhost/api/v1/books 访问"
else
    echo "✗ 健康检查失败，请检查日志: docker-compose logs"
    exit 1
fi
```

</details>

### 运行效果展示

```bash
# 将四个文件放到项目5的目录下，然后：
$ chmod +x deploy.sh
$ ./deploy.sh

=== 图书管理API 一键部署 ===
1. 停止旧容器...
2. 构建镜像...
[+] Building 12.3s
3. 启动服务...
[+] Running 2/2
 ✔ Container book-api    Started
 ✔ Container book-nginx  Started
4. 等待服务就绪...
5. 健康检查...
✓ 部署成功！API 可通过 http://localhost/api/v1/books 访问
```

### 扩展挑战

1. **环境变量管理**：用 `.env` 文件管理数据库路径、端口等配置，修改 docker-compose 读取环境变量。
2. **日志收集**：在 docker-compose 中添加 `logging` 配置，将日志输出到文件或 ELK。

---

## 项目10：为记账本 API 写全套测试

- **对应篇章**：第 106-109 章（测试篇）
- **一句话目标**：给项目2（个人记账本）的 HTTP 版本写单元测试、表格驱动测试、Mock 测试和性能基准测试

### 用到本篇哪些知识点

- 单元测试 `go test`（第106章）
- 表格驱动测试（第106章）
- Mock 与测试替身（第107章）
- Benchmark 性能测试（第109章）

### 功能描述

将项目2的命令行记账本改为 HTTP API 版本，然后为其编写：
1. **表格驱动测试**：测试 `Add`、`Summary` 等核心逻辑
2. **HTTP Handler 测试**：用 `httptest` 测试 API 接口
3. **Benchmark**：测试 `Add` 和 `Summary` 在大数据量下的性能

### 分步实现

**第1步：HTTP 版记账本（待测代码）**

```go
// ledger.go
package ledger

type Record struct {
    Amount   float64 `json:"amount"`
    Category string  `json:"category"`
    Note     string  `json:"note"`
}

type Ledger struct {
    Records []Record `json:"records"`
}

func (l *Ledger) Add(amount float64, category, note string) {
    l.Records = append(l.Records, Record{Amount: amount, Category: category, Note: note})
}

func (l *Ledger) Summary() (income, expense float64) {
    for _, r := range l.Records {
        if r.Category == "income" {
            income += r.Amount
        } else {
            expense += r.Amount
        }
    }
    return
}
```

**第2步：表格驱动测试**

```go
// ledger_test.go
func TestAdd(t *testing.T) {
    tests := []struct {
        name     string
        amount   float64
        category string
        note     string
        wantLen  int
    }{
        {"添加收入", 1000, "income", "工资", 1},
        {"添加支出", 50, "expense", "午餐", 2},
        {"添加大额", 99999, "income", "奖金", 3},
    }
    l := &Ledger{}
    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            l.Add(tt.amount, tt.category, tt.note)
            if len(l.Records) != tt.wantLen {
                t.Errorf("期望 %d 条记录, 实际 %d 条", tt.wantLen, len(l.Records))
            }
        })
    }
}

func TestSummary(t *testing.T) {
    tests := []struct {
        name         string
        records      []Record
        wantIncome   float64
        wantExpense  float64
    }{
        {"空账本", nil, 0, 0},
        {"仅收入", []Record{{100, "income", ""}}, 100, 0},
        {"仅支出", []Record{{50, "expense", ""}}, 0, 50},
        {"混合", []Record{{100, "income", ""}, {30, "expense", ""}, {20, "expense", ""}}, 100, 50},
    }
    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            l := &Ledger{Records: tt.records}
            income, expense := l.Summary()
            if income != tt.wantIncome || expense != tt.wantExpense {
                t.Errorf("Summary() = (%.2f, %.2f), want (%.2f, %.2f)",
                    income, expense, tt.wantIncome, tt.wantExpense)
            }
        })
    }
}
```

**第3步：HTTP Handler 测试（用 httptest）**

```go
func TestAddHandler(t *testing.T) {
    l := &Ledger{}
    router := setupRouter(l) // gin 路由

    body := `{"amount":100,"category":"income","note":"工资"}`
    req := httptest.NewRequest("POST", "/api/records", strings.NewReader(body))
    req.Header.Set("Content-Type", "application/json")
    w := httptest.NewRecorder()

    router.ServeHTTP(w, req)

    assert.Equal(t, 200, w.Code)
    assert.Equal(t, 1, len(l.Records))
    assert.Equal(t, 100.0, l.Records[0].Amount)
}
```

**第4步：Benchmark**

```go
func BenchmarkAdd(b *testing.B) {
    l := &Ledger{}
    b.ResetTimer()
    for i := 0; i < b.N; i++ {
        l.Add(float64(i), "income", "test")
    }
}

func BenchmarkSummary(b *testing.B) {
    l := &Ledger{}
    for i := 0; i < 10000; i++ {
        l.Add(float64(i), "income", "test")
    }
    b.ResetTimer()
    for i := 0; i < b.N; i++ {
        l.Summary()
    }
}
```

### 完整代码

<details>
<summary>点击展开 ledger.go（待测代码）</summary>

```go
package ledger

import (
    "net/http"
    "strconv"

    "github.com/gin-gonic/gin"
)

type Record struct {
    Amount   float64 `json:"amount"`
    Category string  `json:"category"`
    Note     string  `json:"note"`
}

type Ledger struct {
    Records []Record `json:"records"`
}

func (l *Ledger) Add(amount float64, category, note string) {
    l.Records = append(l.Records, Record{Amount: amount, Category: category, Note: note})
}

func (l *Ledger) Summary() (income, expense float64) {
    for _, r := range l.Records {
        if r.Category == "income" {
            income += r.Amount
        } else {
            expense += r.Amount
        }
    }
    return
}

func (l *Ledger) List() []Record {
    return l.Records
}

func (l *Ledger) Count() int {
    return len(l.Records)
}

func SetupRouter(l *Ledger) *gin.Engine {
    r := gin.Default()

    r.POST("/api/records", func(c *gin.Context) {
        var input struct {
            Amount   float64 `json:"amount" binding:"required"`
            Category string  `json:"category" binding:"required,oneof=income expense"`
            Note     string  `json:"note"`
        }
        if err := c.ShouldBindJSON(&input); err != nil {
            c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
            return
        }
        l.Add(input.Amount, input.Category, input.Note)
        c.JSON(http.StatusOK, gin.H{"count": l.Count()})
    })

    r.GET("/api/records", func(c *gin.Context) {
        c.JSON(http.StatusOK, gin.H{"records": l.List(), "total": l.Count()})
    })

    r.GET("/api/summary", func(c *gin.Context) {
        income, expense := l.Summary()
        c.JSON(http.StatusOK, gin.H{
            "income":  strconv.FormatFloat(income, 'f', 2, 64),
            "expense": strconv.FormatFloat(expense, 'f', 2, 64),
            "balance": strconv.FormatFloat(income-expense, 'f', 2, 64),
        })
    })

    return r
}
```

</details>

<details>
<summary>点击展开 ledger_test.go（完整测试）</summary>

```go
package ledger

import (
    "net/http"
    "net/http/httptest"
    "strings"
    "testing"
)

// ==================== 表格驱动测试 ====================

func TestAdd(t *testing.T) {
    tests := []struct {
        name     string
        amount   float64
        category string
        note     string
        wantLen  int
    }{
        {"添加收入", 1000, "income", "工资", 1},
        {"添加支出", 50, "expense", "午餐", 2},
        {"添加大额", 99999, "income", "奖金", 3},
    }
    l := &Ledger{}
    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            l.Add(tt.amount, tt.category, tt.note)
            if len(l.Records) != tt.wantLen {
                t.Errorf("期望 %d 条记录, 实际 %d 条", tt.wantLen, len(l.Records))
            }
        })
    }
}

func TestSummary(t *testing.T) {
    tests := []struct {
        name        string
        records     []Record
        wantIncome  float64
        wantExpense float64
    }{
        {"空账本", nil, 0, 0},
        {"仅收入", []Record{{100, "income", ""}}, 100, 0},
        {"仅支出", []Record{{50, "expense", ""}}, 0, 50},
        {"混合", []Record{
            {100, "income", ""},
            {30, "expense", ""},
            {20, "expense", ""},
        }, 100, 50},
        {"多笔收入", []Record{
            {200, "income", ""},
            {300, "income", ""},
        }, 500, 0},
    }
    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            l := &Ledger{Records: tt.records}
            income, expense := l.Summary()
            if income != tt.wantIncome || expense != tt.wantExpense {
                t.Errorf("Summary() = (%.2f, %.2f), want (%.2f, %.2f)",
                    income, expense, tt.wantIncome, tt.wantExpense)
            }
        })
    }
}

func TestCount(t *testing.T) {
    l := &Ledger{}
    if l.Count() != 0 {
        t.Errorf("空账本计数应为 0，实际为 %d", l.Count())
    }
    l.Add(100, "income", "")
    if l.Count() != 1 {
        t.Errorf("添加1条后计数应为 1，实际为 %d", l.Count())
    }
}

// ==================== HTTP Handler 测试 ====================

func TestAddHandler(t *testing.T) {
    l := &Ledger{}
    router := SetupRouter(l)

    body := `{"amount":100.5,"category":"income","note":"工资"}`
    req := httptest.NewRequest("POST", "/api/records", strings.NewReader(body))
    req.Header.Set("Content-Type", "application/json")
    w := httptest.NewRecorder()

    router.ServeHTTP(w, req)

    if w.Code != http.StatusOK {
        t.Errorf("期望状态码 200，实际 %d", w.Code)
    }
    if l.Count() != 1 {
        t.Errorf("期望记录数 1，实际 %d", l.Count())
    }
    if l.Records[0].Amount != 100.5 {
        t.Errorf("期望金额 100.5，实际 %.2f", l.Records[0].Amount)
    }
}

func TestAddHandlerInvalidCategory(t *testing.T) {
    l := &Ledger{}
    router := SetupRouter(l)

    body := `{"amount":100,"category":"invalid","note":""}`
    req := httptest.NewRequest("POST", "/api/records", strings.NewReader(body))
    req.Header.Set("Content-Type", "application/json")
    w := httptest.NewRecorder()

    router.ServeHTTP(w, req)

    if w.Code != http.StatusBadRequest {
        t.Errorf("无效类别应返回 400，实际 %d", w.Code)
    }
}

func TestSummaryHandler(t *testing.T) {
    l := &Ledger{}
    l.Add(200, "income", "工资")
    l.Add(50, "expense", "午餐")
    router := SetupRouter(l)

    req := httptest.NewRequest("GET", "/api/summary", nil)
    w := httptest.NewRecorder()
    router.ServeHTTP(w, req)

    if w.Code != http.StatusOK {
        t.Errorf("期望状态码 200，实际 %d", w.Code)
    }
    if !strings.Contains(w.Body.String(), "150.00") {
        t.Errorf("期望结余 150.00，实际响应: %s", w.Body.String())
    }
}

func TestListHandler(t *testing.T) {
    l := &Ledger{}
    l.Add(100, "income", "test")
    router := SetupRouter(l)

    req := httptest.NewRequest("GET", "/api/records", nil)
    w := httptest.NewRecorder()
    router.ServeHTTP(w, req)

    if w.Code != http.StatusOK {
        t.Errorf("期望状态码 200，实际 %d", w.Code)
    }
    if !strings.Contains(w.Body.String(), `"total":1`) {
        t.Errorf("期望 total=1，实际响应: %s", w.Body.String())
    }
}

// ==================== Benchmark ====================

func BenchmarkAdd(b *testing.B) {
    l := &Ledger{}
    b.ResetTimer()
    for i := 0; i < b.N; i++ {
        l.Add(float64(i), "income", "benchmark")
    }
}

func BenchmarkSummary(b *testing.B) {
    l := &Ledger{}
    for i := 0; i < 10000; i++ {
        l.Add(float64(i), "income", "")
    }
    b.ResetTimer()
    for i := 0; i < b.N; i++ {
        l.Summary()
    }
}

func BenchmarkAddHandler(b *testing.B) {
    l := &Ledger{}
    router := SetupRouter(l)
    body := `{"amount":100,"category":"income","note":"test"}`

    b.ResetTimer()
    for i := 0; i < b.N; i++ {
        req := httptest.NewRequest("POST", "/api/records", strings.NewReader(body))
        req.Header.Set("Content-Type", "application/json")
        w := httptest.NewRecorder()
        router.ServeHTTP(w, req)
    }
}
```

</details>

### 运行效果展示

```bash
# 运行所有测试
$ go test -v ./...
=== RUN   TestAdd
=== RUN   TestAdd/添加收入
=== RUN   TestAdd/添加支出
=== RUN   TestAdd/添加大额
--- PASS: TestAdd (0.00s)
=== RUN   TestSummary
=== RUN   TestSummary/空账本
=== RUN   TestSummary/仅收入
=== RUN   TestSummary/仅支出
=== RUN   TestSummary/混合
=== RUN   TestSummary/多笔收入
--- PASS: TestSummary (0.00s)
=== RUN   TestAddHandler
--- PASS: TestAddHandler (0.00s)
=== RUN   TestAddHandlerInvalidCategory
--- PASS: TestAddHandlerInvalidCategory (0.00s)
PASS
ok      ledger  0.123s

# 运行 Benchmark
$ go test -bench=. -benchmem
BenchmarkAdd-8              100000000    10.5 ns/op    0 B/op    0 allocs/op
BenchmarkSummary-8           1000000     1234 ns/op    0 B/op    0 allocs/op
BenchmarkAddHandler-8         500000     3456 ns/op  1024 B/op   12 allocs/op
```

### 扩展挑战

1. **Mock 数据库测试**：假如记账本改用数据库存储，用 `go-sqlmock` 或接口 mock 写不依赖真实数据库的测试。
2. **集成测试**：用 `httptest.Server` 启动完整 HTTP 服务，用真实 HTTP 客户端发送请求完成端到端测试。

---

## 十个项目总结

| 项目 | 对应篇章 | 语言/技术 | 代码行数 | 核心收获 |
|------|----------|-----------|----------|----------|
| 1. 猜数字 | 地基篇 (0-14) | Go 基础 | ~20 | 体验编程完整流程 |
| 2. 记账本 | Go语言篇 (15-39) | Go 核心语法 | ~100 | 掌握变量/切片/Map/结构体/文件 |
| 3. 链表测试器 | 数据结构篇 (40-49) | 算法 + 性能 | ~120 | 直观感受时间复杂度差异 |
| 4. 成绩管理 | 数据库篇 (50-64) | MySQL + GORM | ~150 | 掌握 CRUD + SQL 聚合排名 |
| 5. 图书API | Web框架篇 (65-76) | Gin + SQLite | ~150 | 掌握 RESTful API 全流程 |
| 6. 笔记API | 认证安全篇 (77-84) | JWT + bcrypt | ~200 | 认证授权完整闭环 |
| 7. 邮件发送器 | 消息队列篇 (85-90) | Channel / RabbitMQ | ~80 | 理解生产者-消费者模式 |
| 8. 短链接 | 系统设计篇 (91-98) | Gin + 并发Map | ~100 | 理解短链系统核心设计 |
| 9. 部署脚本 | DevOps篇 (99-105) | Docker + Nginx | ~40 (配置) | 掌握容器化部署流程 |
| 10. 全套测试 | 测试篇 (106-109) | go test + httptest | ~180 | 掌握测试金字塔各层 |

### 使用建议

1. **按顺序做**：每个项目都依赖前面篇章的知识，跳着做可能卡住。
2. **先自己写**：看完"功能描述"后，先不看完整代码，自己尝试实现一遍，再对照。
3. **完成扩展挑战**：基本功能做完后，至少做一个扩展题，加深理解。
4. **提交到 GitHub**：每个项目建一个独立 repo，积累你的 GitHub 绿点。
5. **写在简历上**：做完项目 5-8 任意两个，就可以在简历上写"独立开发 RESTful API，熟悉 Gin + JWT + MySQL"。

---

> **变更记录**
> - 2026-05-28：初版，包含全部 10 个篇末串讲项目