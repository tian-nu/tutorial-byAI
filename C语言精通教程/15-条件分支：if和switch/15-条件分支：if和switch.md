# 15 — 条件分支：if 和 switch

> - 对应文档版本：C语言精通教程 outline v1
> - 适用环境：需gcc编译器
> - 读者角色：C语言零基础的开发者
> - 预计耗时：新手 50 分钟 / 熟手 20 分钟
> - 前置教程：第12章（关系、逻辑、位运算）、第14章（输入输出）
> - 可视化：无

---

## 我在做什么？

到上一章为止，你的程序只能"一条路走到黑"——从第一行执行到最后一行，中间没有任何分叉。

但真正的程序需要"判断"。"如果用户是VIP，给他打八折"。"如果密码错误，拒绝登录"。"如果分数大于60，显示及格，否则显示不及格"。这种"看情况做不同的事"的能力，在编程中叫**条件分支**。

这一章，你会学到C语言中的两类分支结构：
1. **`if` / `else if` / `else`**：最常见的条件判断。
2. **`switch` / `case`**：多分支选择，以及它那个著名的 `break` 陷阱。
3. **三元运算符 `?:`**：一行代码的条件判断。

---

## 15.1 `if` 语句：最基本的判断

### 15.1.1 基本语法

```c
if (条件) {
    /* 条件为真时执行的代码 */
}
```

**比喻**：`if` 就像门卫。"条件"是他手上的名单。你报上名字（条件求值），如果你在名单上（条件为真），他放你进去（执行花括号里的代码）。如果你不在名单上（条件为假），他当你不存在（跳过花括号）。

```c
#include <stdio.h>

int main(void)
{
    int score = 85;

    if (score >= 60) {
        printf("及格！\n");
    }

    return 0;
}
```

### 15.1.2 `if` / `else`：二选一

```c
if (条件) {
    /* 条件为真 */
} else {
    /* 条件为假 */
}
```

```c
int score = 55;

if (score >= 60) {
    printf("及格！\n");
} else {
    printf("不及格，继续努力！\n");
}
```

**比喻**：`if-else` 就像岔路口。路标写着"左转：及格线以上"，"右转：及格线以下"。你走到路口，根据自己的分数，选一条路走。你不可能同时走两条。

### 15.1.3 `if` / `else if` / `else`：多选一

```c
if (条件1) {
    /* 条件1为真 */
} else if (条件2) {
    /* 条件1为假，条件2为真 */
} else if (条件3) {
    /* 条件1和2都为假，条件3为真 */
} else {
    /* 所有条件都为假 */
}
```

```c
#include <stdio.h>

int main(void)
{
    int score = 85;

    if (score >= 90) {
        printf("优秀\n");
    } else if (score >= 80) {
        printf("良好\n");
    } else if (score >= 70) {
        printf("中等\n");
    } else if (score >= 60) {
        printf("及格\n");
    } else {
        printf("不及格\n");
    }

    return 0;
}
```

**执行逻辑**：从上到下依次检查条件。一旦某个条件为真，执行对应的代码，然后**跳过所有后续的 `else if` 和 `else`**。

```
if-else if-else 执行流程：
    条件1 为真？ ──是──→ 执行代码1 ──→ 结束
        │
       否
        ↓
    条件2 为真？ ──是──→ 执行代码2 ──→ 结束
        │
       否
        ↓
    条件3 为真？ ──是──→ 执行代码3 ──→ 结束
        │
       否
        ↓
    执行 else 代码 ──→ 结束
```

---

## 15.2 `else` 的匹配规则

当 `if` 嵌套使用时，`else` 会和**最近的、尚未匹配的 `if`** 配对。

```c
#include <stdio.h>

int main(void)
{
    int x = 10, y = 5;

    if (x > 0)
        if (y > 10)
            printf("A: x>0 且 y>10\n");
    else
        printf("B: 这里匹配的是哪个if？\n");

    return 0;
}
```

输出：`B: 这里匹配的是哪个if？`

**为什么？** `else` 和最近的 `if (y > 10)` 配对，而不是和 `if (x > 0)` 配对。尽管缩进让人以为 `else` 属于外层的 `if`，但编译器只看花括号，不看缩进。

**正确做法**：永远用花括号明确边界。

```c
if (x > 0) {
    if (y > 10) {
        printf("A: x>0 且 y>10\n");
    }
} else {
    printf("B: 现在明确属于外层if\n");
}
```

**金科玉律**：即使 `if` 或 `else` 后面只有一条语句，也给它加上花括号。多打两个字符，能避免无数bug。

---

## 15.3 `switch` / `case`：多分支选择

当你要根据一个变量的值，在多个选项中选择时，`switch` 比层层叠叠的 `if-else` 更清晰。

### 15.3.1 基本语法

```c
switch (表达式) {
    case 值1:
        /* 代码 */
        break;
    case 值2:
        /* 代码 */
        break;
    case 值3:
        /* 代码 */
        break;
    default:
        /* 所有case都不匹配时执行 */
        break;
}
```

```c
#include <stdio.h>

int main(void)
{
    int day = 3;

    switch (day) {
        case 1:
            printf("星期一\n");
            break;
        case 2:
            printf("星期二\n");
            break;
        case 3:
            printf("星期三\n");
            break;
        case 4:
            printf("星期四\n");
            break;
        case 5:
            printf("星期五\n");
            break;
        case 6:
            printf("星期六\n");
            break;
        case 7:
            printf("星期日\n");
            break;
        default:
            printf("无效的日期\n");
            break;
    }

    return 0;
}
```

**比喻**：`switch` 就像电梯的楼层按钮。你按了3楼（`case 3`），电梯直接把你送到3楼。`break` 是电梯门——到了3楼，门打开，你走出去。如果没有 `break`，电梯门不打开，你被继续带到4楼、5楼……这就是 `switch` 的"穿透"。

### 15.3.2 `break` 与"穿透"（fall-through）

`switch` 最著名的陷阱：**如果忘了写 `break`，程序会继续执行下一个 `case` 的代码**。

```c
/* ❌ 忘记 break 的后果 */
int num = 2;
switch (num) {
    case 1:
        printf("一\n");
    case 2:
        printf("二\n");   /* 这里没有 break！ */
    case 3:
        printf("三\n");
}
/* 输出：
   二
   三
*/
/* 因为 case 2 没有 break，程序"穿透"到了 case 3 */
```

有时候，程序员故意利用穿透来简化代码：

```c
/* 故意利用穿透：工作日共享同一段代码 */
switch (day) {
    case 1:
    case 2:
    case 3:
    case 4:
    case 5:
        printf("工作日\n");
        break;
    case 6:
    case 7:
        printf("周末\n");
        break;
}
```

这种用法需要特别注释说明，否则别人会以为你忘了写 `break`。

### 15.3.3 `switch` 的限制

`switch` 只能用于以下类型的表达式：
- 整数类型（`int`、`char`、`short`、`long`等）
- 枚举类型（后面会学）

**不能**用于：
- 浮点数（`float`、`double`）
- 字符串
- 范围判断（如 `case > 10:` 不合法）

当需要范围判断时，用 `if-else` 而不是 `switch`。

---

## 15.4 三元运算符 `?:`

三元运算符是 `if-else` 的"压缩版"，一行代码完成判断和赋值。

```c
变量 = (条件) ? 值1 : 值2;
/* 条件为真 → 取值1，条件为假 → 取值2 */
```

```c
int score = 75;
char *result = (score >= 60) ? "及格" : "不及格";
printf("%s\n", result);   /* 输出：及格 */
```

等价于：

```c
char *result;
if (score >= 60) {
    result = "及格";
} else {
    result = "不及格";
}
```

**三元运算符可以嵌套，但不推荐**：

```c
/* 不推荐：可读性差 */
int grade = (score >= 90) ? 1 : (score >= 80) ? 2 : (score >= 60) ? 3 : 4;

/* 推荐：用 if-else if-else */
int grade;
if (score >= 90) {
    grade = 1;
} else if (score >= 80) {
    grade = 2;
} else if (score >= 60) {
    grade = 3;
} else {
    grade = 4;
}
```

---

## 15.5 完整示例：成绩等级判断

```c
#include <stdio.h>

int main(void)
{
    int score;

    printf("请输入你的分数（0-100）：");
    scanf("%d", &score);

    /* 输入验证 */
    if (score < 0 || score > 100) {
        printf("分数必须在0到100之间！\n");
        return 1;
    }

    /* 方式一：if-else if-else */
    printf("\n=== 方式一：if-else ===\n");
    if (score >= 90) {
        printf("等级：A（优秀）\n");
    } else if (score >= 80) {
        printf("等级：B（良好）\n");
    } else if (score >= 70) {
        printf("等级：C（中等）\n");
    } else if (score >= 60) {
        printf("等级：D（及格）\n");
    } else {
        printf("等级：F（不及格）\n");
    }

    /* 方式二：switch（按十位数分组） */
    printf("\n=== 方式二：switch ===\n");
    switch (score / 10) {
        case 10:
        case 9:
            printf("等级：A\n");
            break;
        case 8:
            printf("等级：B\n");
            break;
        case 7:
            printf("等级：C\n");
            break;
        case 6:
            printf("等级：D\n");
            break;
        default:
            printf("等级：F\n");
            break;
    }

    /* 方式三：三元运算符（简单判断） */
    printf("\n=== 方式三：三元运算符 ===\n");
    printf("结果：%s\n", (score >= 60) ? "通过" : "未通过");

    return 0;
}
```

---

## 15.6 常见错误

### 错误1：`if` 条件中 `=` 写成 `==`

```c
/* ❌ 错误示例 */
int x = 5;
if (x = 10) {   /* 赋值，不是比较！条件永远为真 */
    printf("x等于10\n");
}

/* ✅ 正确示例 */
int x = 5;
if (x == 10) {   /* 比较 */
    printf("x等于10\n");
}
```

### 错误2：`switch` 忘记 `break`

```c
/* ❌ 错误示例 */
switch (choice) {
    case 1:
        printf("选项1\n");
    case 2:       /* 没有 break，会穿透下来 */
        printf("选项2\n");
    default:
        printf("默认\n");
}

/* ✅ 正确示例 */
switch (choice) {
    case 1:
        printf("选项1\n");
        break;
    case 2:
        printf("选项2\n");
        break;
    default:
        printf("默认\n");
        break;
}
```

### 错误3：`else` 匹配错误

```c
/* ❌ 错误示例 */
if (a > 0)
    if (b > 0)
        printf("a和b都大于0\n");
else          /* 这个 else 属于 if (b > 0)，不是 if (a > 0)！ */
    printf("a不大于0？错！\n");

/* ✅ 正确示例：加花括号 */
if (a > 0) {
    if (b > 0) {
        printf("a和b都大于0\n");
    }
} else {
    printf("a不大于0\n");
}
```

### 错误4：`switch` 用于浮点数

```c
/* ❌ 错误示例 */
double price = 9.99;
switch (price) {   /* 编译报错！switch 不能用于浮点数 */
    case 9.99: ...
}

/* ✅ 正确示例：用 if-else */
if (price == 9.99) { ... }
```

---

## 15.7 我在做什么？做得对不对？不对怎么办？

### 我在做什么？

我在学习C语言的条件分支：用 `if`/`else if`/`else` 做多路判断，用 `switch`/`case` 做多分支选择（理解 `break` 的穿透机制），用三元运算符 `?:` 做简洁的条件赋值。

### 我做得对不对？

- 你能写出一个完整的 `if-else if-else` 链 → if语句过关。
- 你能解释 `switch` 中 `break` 的作用和忘记 `break` 的后果 → switch过关。
- 你知道 `else` 会匹配最近的 `if` → 匹配规则过关。
- 你能用三元运算符替代简单的 `if-else` → 三元运算符过关。

### 不对怎么办？

| 症状 | 第一步检查 |
|------|-----------|
| `if` 条件总成立 | 是否把 `==` 写成了 `=`？ |
| `switch` 执行了多余的 case | 是否忘了 `break`？ |
| `else` 执行了不该执行的代码 | 是否 `else` 的匹配对象不是你期望的？加花括号 |
| `switch` 编译报错 | 表达式是否为浮点数或字符串？改用 `if-else` |
| 条件判断结果与预期相反 | 是否逻辑反了？是否 `!` 用错了位置？ |

---

## 本章小结

| 知识点 | 说明 |
|--------|------|
| `if` | 最基本的条件判断：条件为真则执行 |
| `if-else` | 二选一分支 |
| `if-else if-else` | 多选一分支，从上到下依次检查 |
| `else` 匹配规则 | 与最近的未匹配 `if` 配对 |
| `switch-case` | 多分支选择，基于整数值 |
| `break` | 在 `switch` 中阻止穿透 |
| 穿透（fall-through） | 忘记 `break` 时，执行会继续到下一个 case |
| `default` | `switch` 中所有 case 都不匹配时执行 |
| 三元运算符 `?:` | `条件 ? 值1 : 值2`，一行完成条件赋值 |

---

## 练习题

1. **成绩等级**：输入一个0-100的分数，用 `if-else if-else` 输出对应的等级（A/B/C/D/F）。

2. **月份天数**：输入月份（1-12），用 `switch` 输出该月有多少天（不考虑闰年，2月按28天算）。

3. **简易计算器**：输入两个数字和一个运算符（+ - * /），用 `switch` 根据运算符计算并输出结果。考虑除数为0的情况。

4. **闰年判断**：输入一个年份，判断是否为闰年。闰年规则：能被4整除但不能被100整除，或者能被400整除。用 `if-else` 实现。

5. **三元运算符练习**：输入三个整数，用三元运算符找出最大值。提示：`max = (a > b) ? ((a > c) ? a : c) : ((b > c) ? b : c);`