# 附录A — C语言关键字速查
> - 对应文档版本：C语言精通教程 outline v1
> - 适用环境：所有 C 语言环境
> - 读者角色：C 语言开发者
> - 预计耗时：15 分钟浏览
> - 前置教程：无
> - 可视化：无

---

## 我在做什么？

C 语言的关键字是编译器保留的"特殊词汇"，你不能用它们做变量名或函数名。本附录列出 C89/C99/C11 全部 44 个关键字，按分类排列，每个附一句话说明和短代码示例，方便你随时查阅。

---

## A.1 类型关键字（14 个）

这些关键字用于定义变量的数据类型。

### `void`
表示"无类型"。用于函数无返回值或无参数。

```c
void say_hello(void) {
    printf("Hello\n");
}
```

### `char`
字符类型，占 1 字节。可存储 ASCII 字符或小整数。

```c
char c = 'A';       // 字符
char score = 65;    // 等价于 'A'
```

### `short`
短整型，通常 2 字节。范围约 -32768 到 32767。

```c
short s = -1000;
```

### `int`
整型，通常 4 字节（32 位系统）。最常用的整数类型。

```c
int count = 42;
```

### `long`
长整型，通常 4 或 8 字节（取决于平台）。

```c
long big = 100000L;
long long huge = 9000000000000LL;  // C99
```

### `float`
单精度浮点数，4 字节，约 6-7 位有效数字。

```c
float pi = 3.14159f;
```

### `double`
双精度浮点数，8 字节，约 15 位有效数字。

```c
double e = 2.718281828459045;
```

### `signed`
有符号类型修饰符（默认修饰 int 和 char）。

```c
signed int x = -5;   // 等价于 int x = -5;
signed char c = -128; // 范围 -128 到 127
```

### `unsigned`
无符号类型修饰符，值域为 0 到正最大值。

```c
unsigned int age = 25;
unsigned char byte = 200;  // 范围 0 到 255
```

### `_Bool`
C99 引入的布尔类型，值为 0 或 1。包含 `<stdbool.h>` 后可用 `bool`。

```c
#include <stdbool.h>
_Bool flag = 1;     // C99 原生
bool ready = true;   // 使用 stdbool.h
```

### `_Complex`
C99 引入的复数类型。

```c
#include <complex.h>
double complex z = 1.0 + 2.0 * I;
```

### `_Imaginary`
C99 引入的虚数类型（较少使用）。

```c
#include <complex.h>
double imaginary zi = 3.0 * I;
```

### `struct`
定义结构体类型——将多个变量打包成一个。

```c
struct Point {
    int x;
    int y;
};
struct Point p = {10, 20};
```

### `union`
定义共用体——所有成员共享同一块内存。

```c
union Data {
    int i;
    float f;
    char str[20];
};
union Data d;
d.i = 10;  // 写入 int，覆盖之前的内容
```

### `enum`
定义枚举类型——一组命名的整数常量。

```c
enum Color { RED, GREEN, BLUE };  // RED=0, GREEN=1, BLUE=2
enum Color c = RED;
```

### `typedef`
为已有类型创建别名。

```c
typedef unsigned long size_t;
typedef struct Point Point;
```

---

## A.2 控制流关键字（12 个）

### `if` / `else`
条件判断。

```c
if (score >= 60) {
    printf("及格\n");
} else {
    printf("不及格\n");
}
```

### `switch` / `case` / `default`
多分支选择。

```c
switch (day) {
    case 1: printf("周一\n"); break;
    case 7: printf("周日\n"); break;
    default: printf("无效\n");
}
```

### `for`
计数循环。

```c
for (int i = 0; i < 10; i++) {
    printf("%d\n", i);
}
```

### `while`
条件循环（先判断后执行）。

```c
while (n > 0) {
    printf("%d\n", n--);
}
```

### `do`
条件循环（先执行后判断，至少执行一次）。

```c
do {
    printf("至少执行一次\n");
} while (0);
```

### `break`
跳出当前循环或 switch。

```c
for (int i = 0; i < 100; i++) {
    if (i == 5) break;  // 提前退出
}
```

### `continue`
跳过本次循环剩余部分，进入下一次迭代。

```c
for (int i = 0; i < 10; i++) {
    if (i % 2 == 0) continue;  // 跳过偶数
    printf("%d\n", i);
}
```

### `goto`
无条件跳转到标签。谨慎使用，容易导致代码混乱。

```c
if (error) goto cleanup;
// ... 正常代码 ...
cleanup:
    free(buffer);
```

### `return`
从函数返回，可带返回值。

```c
int add(int a, int b) {
    return a + b;
}
```

---

## A.3 存储类关键字（6 个）

### `auto`
默认存储类，局部变量自动分配和释放。几乎从不显式使用。

```c
auto int x = 5;  // 等价于 int x = 5;
```

### `register`
建议编译器将变量放在寄存器中（编译器可能忽略）。不能取地址。

```c
register int counter = 0;  // 提示编译器优化
```

### `static`
静态变量：函数内保持值不变，文件内限制作用域。

```c
void count_calls(void) {
    static int calls = 0;  // 只初始化一次
    calls++;
    printf("调用次数: %d\n", calls);
}
```

### `extern`
声明变量或函数在另一个文件中定义。

```c
extern int global_counter;  // 定义在别的 .c 文件中
extern void log_message(const char *msg);
```

### `const`
声明常量，值不可修改。

```c
const int MAX = 100;
const char *msg = "Hello";  // 指向的内容不可修改
```

### `volatile`
告诉编译器变量可能被外部因素改变，禁止优化。

```c
volatile int flag;  // 可能被硬件或信号处理函数修改
```

---

## A.4 其他关键字（2 个）

### `sizeof`
计算类型或变量占用的字节数。编译时求值（VLA 除外）。

```c
int n = sizeof(int);           // 通常是 4
size_t s = sizeof(struct Point); // 结构体大小
```

### `_Alignas` / `_Alignof`
C11 引入的对齐关键字。

```c
_Alignas(16) int aligned_var;  // C11: 16 字节对齐
size_t a = _Alignof(int);     // C11: 返回对齐要求
```

---

## A.5 类型限定符（C11 新增）

### `_Atomic`
C11 引入的原子类型，用于多线程安全操作。

```c
#include <stdatomic.h>
_Atomic int counter = 0;
atomic_fetch_add(&counter, 1);
```

### `_Noreturn`
C11 引入，标记函数不会返回（如 `exit()`）。

```c
_Noreturn void fatal_error(void) {
    exit(1);
}
```

### `_Generic`
C11 引入，编译时根据类型选择表达式。

```c
#define print(x) _Generic((x), \
    int: printf("%d\n", x),    \
    double: printf("%f\n", x), \
    default: printf("?\n"))

print(42);     // 输出 42
print(3.14);   // 输出 3.140000
```

### `_Static_assert`
C11 引入，编译时断言。

```c
_Static_assert(sizeof(int) >= 4, "int 必须至少 4 字节");
```

### `_Thread_local`
C11 引入，每个线程独立的变量副本。

```c
_Thread_local int thread_id;
```

---

## A.6 关键字速查表（按字母排序）

| 关键字 | 分类 | 标准 | 一句话 |
|--------|------|------|--------|
| `_Alignas` | 其他 | C11 | 指定对齐方式 |
| `_Alignof` | 其他 | C11 | 查询对齐要求 |
| `_Atomic` | 限定符 | C11 | 原子类型 |
| `_Bool` | 类型 | C99 | 布尔类型 |
| `_Complex` | 类型 | C99 | 复数类型 |
| `_Generic` | 其他 | C11 | 编译时类型选择 |
| `_Imaginary` | 类型 | C99 | 虚数类型 |
| `_Noreturn` | 限定符 | C11 | 标记不返回的函数 |
| `_Static_assert` | 其他 | C11 | 编译时断言 |
| `_Thread_local` | 限定符 | C11 | 线程局部存储 |
| `auto` | 存储类 | C89 | 自动存储（默认） |
| `break` | 控制流 | C89 | 跳出循环/switch |
| `case` | 控制流 | C89 | switch 分支标签 |
| `char` | 类型 | C89 | 字符类型 |
| `const` | 存储类 | C89 | 常量限定 |
| `continue` | 控制流 | C89 | 跳过本次循环剩余 |
| `default` | 控制流 | C89 | switch 默认分支 |
| `do` | 控制流 | C89 | do-while 循环 |
| `double` | 类型 | C89 | 双精度浮点 |
| `else` | 控制流 | C89 | if 的否则分支 |
| `enum` | 类型 | C89 | 枚举类型 |
| `extern` | 存储类 | C89 | 外部声明 |
| `float` | 类型 | C89 | 单精度浮点 |
| `for` | 控制流 | C89 | for 循环 |
| `goto` | 控制流 | C89 | 无条件跳转 |
| `if` | 控制流 | C89 | 条件判断 |
| `inline` | 限定符 | C99 | 内联函数建议 |
| `int` | 类型 | C89 | 整型 |
| `long` | 类型 | C89 | 长整型 |
| `register` | 存储类 | C89 | 寄存器变量建议 |
| `restrict` | 限定符 | C99 | 指针独占访问 |
| `return` | 控制流 | C89 | 函数返回 |
| `short` | 类型 | C89 | 短整型 |
| `signed` | 类型 | C89 | 有符号修饰 |
| `sizeof` | 其他 | C89 | 求字节大小 |
| `static` | 存储类 | C89 | 静态变量/函数 |
| `struct` | 类型 | C89 | 结构体 |
| `switch` | 控制流 | C89 | 多分支选择 |
| `typedef` | 类型 | C89 | 类型别名 |
| `union` | 类型 | C89 | 共用体 |
| `unsigned` | 类型 | C89 | 无符号修饰 |
| `void` | 类型 | C89 | 无类型 |
| `volatile` | 存储类 | C89 | 易变变量 |
| `while` | 控制流 | C89 | while 循环 |

---

## A.7 三问

1. **`_Bool` 和 `bool` 有什么区别？** `_Bool` 是 C99 关键字，`bool` 是 `<stdbool.h>` 中通过 `#define` 定义的宏，等价于 `_Bool`。建议使用 `bool`（更可读）。

2. **`static` 在函数内和函数外有什么区别？** 函数内 `static` 变量保持值不丢失（生命周期为整个程序运行期）；函数外 `static` 变量/函数限制作用域为当前文件。

3. **`const` 和 `#define` 有什么区别？** `const` 是真正的变量，有类型、有地址，编译器可检查类型；`#define` 是预处理宏，纯文本替换，无类型检查。

---

## A.8 本章小结

| 内容 | 说明 |
|------|------|
| 关键字总数 | 44 个（C89: 32, C99: +5, C11: +7） |
| 类型关键字 | void, char, short, int, long, float, double, signed, unsigned, _Bool, _Complex, _Imaginary, struct, union, enum, typedef |
| 控制流关键字 | if, else, switch, case, default, for, while, do, break, continue, goto, return |
| 存储类关键字 | auto, register, static, extern, const, volatile |
| C11 新增 | _Alignas, _Alignof, _Atomic, _Generic, _Noreturn, _Static_assert, _Thread_local |

---

## A.9 练习题

1. 列出 `static` 关键字的三种不同用法，并各写一个示例。
2. `typedef` 和 `#define` 都可以创建别名，举例说明它们的关键区别。
3. 分析以下代码中哪些标识符不能用作变量名：`int float = 3; int _count = 0; int main = 5;`