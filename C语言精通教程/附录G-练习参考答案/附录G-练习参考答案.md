# 附录G — 练习参考答案
> - 对应文档版本：C语言精通教程 outline v1
> - 适用环境：所有 C 语言环境
> - 读者角色：C 语言开发者
> - 预计耗时：浏览 30 分钟
> - 前置教程：第1-60章
> - 可视化：无

---

## 我在做什么？

本附录整理了全教程 60 章中每章的练习题参考答案。每道题给出答案和简短解释。建议先独立完成练习，再对照答案检查。

---

## G.1 第1-10章参考答案

### 第1章：C语言概述

**1. C 语言属于编译型语言还是解释型语言？为什么？**

答：C 语言是编译型语言。原因是 C 源代码需要通过编译器（如 gcc）翻译为机器码后才能执行，而不是像 Python 那样由解释器逐行解释执行。编译后的程序可以直接在目标平台上运行，不需要解释器。

**2. 请简单描述从源代码到可执行文件的四个步骤。**

答：预处理 → 编译 → 汇编 → 链接。预处理处理 `#include`、`#define` 等指令；编译将 C 代码翻译为汇编代码；汇编将汇编代码翻译为机器码（.o 目标文件）；链接将多个目标文件和库合并为可执行文件。

**3. 列举三个 C 语言的应用领域。**

答：操作系统（Linux 内核）、嵌入式系统（汽车 ECU）、数据库（MySQL）、网络服务器（Nginx）、游戏引擎、编译器（gcc 本身）。

### 第2章：开发环境搭建

**1. 在你的系统上安装 gcc 并验证版本。**

```bash
gcc --version
# 应显示类似: gcc (Ubuntu 11.4.0) 11.4.0
```

**2. 编写并运行你的第一个 C 程序。**

```c
#include <stdio.h>
int main(void) {
    printf("Hello, World!\n");
    return 0;
}
```

```bash
gcc -o hello hello.c
./hello
```

**3. 了解 gcc 的 `-Wall -Wextra -std=c99` 标志的含义。**

答：`-Wall` 启用常用警告，`-Wextra` 启用额外警告，`-std=c99` 指定使用 C99 标准。

### 第3章：变量与数据类型

**1. 声明一个 `int` 变量并赋值，用 `printf` 打印其值和地址。**

```c
int x = 42;
printf("值: %d, 地址: %p\n", x, (void*)&x);
```

**2. `float` 和 `double` 的区别是什么？各占多少字节？**

答：`float` 是单精度浮点数（4 字节，约 6-7 位有效数字），`double` 是双精度（8 字节，约 15-16 位有效数字）。`double` 精度更高，范围更大。科学计算推荐 `double`。

**3. `char` 类型可以存储整数吗？如果可以，范围是多少？**

答：可以。`char` 本质上是一个 1 字节的整数类型。`signed char` 范围 -128 到 127，`unsigned char` 范围 0 到 255。

### 第4章：运算符与表达式

**1. 表达式 `5 / 2` 的结果是多少？为什么？**

答：结果是 2（整数除法，截断小数部分）。要得到 2.5，需要 `5.0 / 2` 或 `(double)5 / 2`。

**2. 写一个程序，判断输入的年份是否为闰年。**

```c
#include <stdio.h>
int main(void) {
    int year;
    printf("输入年份: ");
    scanf("%d", &year);
    if ((year % 4 == 0 && year % 100 != 0) || year % 400 == 0) {
        printf("%d 是闰年\n", year);
    } else {
        printf("%d 不是闰年\n", year);
    }
    return 0;
}
```

**3. 解释 `a++` 和 `++a` 的区别。**

答：`a++`（后置自增）先使用 `a` 的当前值，再自增；`++a`（前置自增）先自增，再使用新值。例如 `int b = a++` 先赋值再自增，`int b = ++a` 先自增再赋值。

### 第5章：控制流

**1. 用 `for` 循环打印九九乘法表。**

```c
for (int i = 1; i <= 9; i++) {
    for (int j = 1; j <= i; j++) {
        printf("%d×%d=%-2d ", j, i, i * j);
    }
    printf("\n");
}
```

**2. 用 `switch` 实现简单的计算器。**

```c
#include <stdio.h>
int main(void) {
    char op;
    double a, b;
    printf("输入算式 (如 3 + 4): ");
    scanf("%lf %c %lf", &a, &op, &b);
    switch (op) {
        case '+': printf("%.2f\n", a + b); break;
        case '-': printf("%.2f\n", a - b); break;
        case '*': printf("%.2f\n", a * b); break;
        case '/':
            if (b != 0) printf("%.2f\n", a / b);
            else printf("除数不能为0\n");
            break;
        default: printf("不支持的运算符\n");
    }
    return 0;
}
```

**3. `break` 和 `continue` 的区别是什么？**

答：`break` 完全跳出当前循环（或 switch）；`continue` 跳过当前迭代的剩余部分，进入下一次迭代。

### 第6章：数组

**1. 声明一个包含 10 个整数的数组，用循环求最大值和最小值。**

```c
int arr[] = {5, 2, 9, 1, 7, 3, 8, 6, 4, 0};
int max = arr[0], min = arr[0];
for (int i = 1; i < 10; i++) {
    if (arr[i] > max) max = arr[i];
    if (arr[i] < min) min = arr[i];
}
```

**2. 实现冒泡排序。**

```c
void bubble_sort(int arr[], int n) {
    for (int i = 0; i < n - 1; i++) {
        for (int j = 0; j < n - 1 - i; j++) {
            if (arr[j] > arr[j + 1]) {
                int temp = arr[j];
                arr[j] = arr[j + 1];
                arr[j + 1] = temp;
            }
        }
    }
}
```

**3. 数组越界访问会发生什么？**

答：数组越界是未定义行为（UB）。可能读取到垃圾数据、修改其他变量的值、导致段错误，或"看起来正常"。

### 第7章：字符串

**1. 实现一个函数，计算字符串中某字符出现的次数。**

```c
int count_char(const char *str, char ch) {
    int count = 0;
    while (*str) {
        if (*str == ch) count++;
        str++;
    }
    return count;
}
```

**2. 不使用 `strcat` 实现字符串拼接。**

```c
void my_strcat(char *dest, const char *src) {
    while (*dest) dest++;  // 移到 dest 末尾
    while (*src) {
        *dest = *src;
        dest++;
        src++;
    }
    *dest = '\0';
}
```

**3. `strcpy` 和 `strncpy` 有什么区别？哪个更安全？**

答：`strcpy` 不检查目标缓冲区大小，可能溢出；`strncpy` 限制复制长度，但可能不自动添加 `\0`。`strncpy` 更安全，但需要手动添加终止符。最安全的方式是使用 `snprintf`。

### 第8章：函数

**1. 写一个递归函数计算阶乘。**

```c
int factorial(int n) {
    if (n <= 1) return 1;  // 基线条件
    return n * factorial(n - 1);
}
```

**2. 解释"传值调用"的含义。**

答：C 语言默认使用传值调用：调用函数时，实参的值被复制到形参。函数内修改形参不影响实参。要修改实参，需要传递指针（传地址）。

**3. 写一个函数，交换两个整数的值。**

```c
void swap(int *a, int *b) {
    int temp = *a;
    *a = *b;
    *b = temp;
}
// 调用: swap(&x, &y);
```

### 第9章：作用域与生命周期

**1. 以下代码输出什么？**

```c
int x = 10;
void func(void) {
    int x = 20;  // 局部变量，遮蔽全局变量
    printf("%d\n", x);  // 输出 20
}
int main(void) {
    printf("%d\n", x);  // 输出 10（全局变量）
    func();
    return 0;
}
```

**2. `static` 局部变量和普通局部变量有什么区别？**

答：`static` 局部变量只初始化一次，生命周期为整个程序运行期，函数调用结束后值保留；普通局部变量每次函数调用时重新创建，函数返回后销毁。

**3. `extern` 关键字的作用是什么？**

答：`extern` 声明变量或函数在另一个文件中定义，告诉编译器"这个符号存在，但定义在别处"。用于跨文件共享全局变量和函数。

### 第10章：预处理指令

**1. `#define` 和 `const` 有什么区别？**

答：`#define` 是预处理宏，纯文本替换，无类型检查，不占内存；`const` 是真正的常量变量，有类型、有地址，编译器可检查类型。`#define` 可定义宏函数，`const` 不能。

**2. 写一个宏，计算两个数的最大值。**

```c
#define MAX(a, b) ((a) > (b) ? (a) : (b))
// 注意：参数和整个表达式都要加括号，防止优先级问题
```

**3. 头文件保护（include guard）的作用是什么？**

答：防止头文件被多次包含导致重复定义错误。写法：
```c
#ifndef MY_HEADER_H
#define MY_HEADER_H
// 头文件内容...
#endif
```

---

## G.2 第11-20章参考答案

### 第11章：指针基础

**1. 声明一个指针变量，指向一个整数，并通过指针修改该整数的值。**

```c
int x = 10;
int *p = &x;
*p = 20;  // x 现在变为 20
```

**2. `NULL` 是什么？为什么要检查指针是否为 `NULL`？**

答：`NULL` 是空指针常量，值为 `(void*)0`，表示指针不指向任何有效内存。必须检查 `NULL` 以防止解引用空指针导致段错误。

**3. 指针变量本身有地址吗？如何获取？**

答：有。指针变量也是一个变量，存储在内存中。获取指针变量的地址：`&p`（得到的是指针的指针，即二级指针）。

### 第12章：指针与数组

**1. 以下代码中，`arr`、`&arr[0]`、`&arr` 有什么区别？**

```c
int arr[5] = {1, 2, 3, 4, 5};
```

答：`arr` 和 `&arr[0]` 都指向数组第一个元素的地址，类型为 `int*`；`&arr` 是指向整个数组的指针，类型为 `int(*)[5]`。地址值相同，但指针类型不同，+1 时跳过的字节数不同（`arr+1` 跳过 4 字节，`&arr+1` 跳过 20 字节）。

**2. 用指针遍历数组。**

```c
int arr[] = {1, 2, 3, 4, 5};
int *p = arr;
for (int i = 0; i < 5; i++) {
    printf("%d\n", *(p + i));  // 或 p[i]
}
```

**3. 指针数组和数组指针有什么区别？**

答：指针数组：`int *arr[10]`，是一个数组，元素是指针（10 个 `int*`）；数组指针：`int (*p)[10]`，是一个指针，指向一个长度为 10 的整型数组。

### 第13章：指针与函数

**1. 实现一个函数，通过指针返回多个值。**

```c
void min_max(int arr[], int n, int *min, int *max) {
    *min = *max = arr[0];
    for (int i = 1; i < n; i++) {
        if (arr[i] < *min) *min = arr[i];
        if (arr[i] > *max) *max = arr[i];
    }
}
```

**2. 函数指针声明：指向返回 `int`、接受两个 `int` 参数的函数。**

```c
int (*func_ptr)(int, int);
```

**3. 用函数指针实现回调：排序时自定义比较规则。**

```c
int ascending(const void *a, const void *b) {
    return (*(int*)a - *(int*)b);
}
int descending(const void *a, const void *b) {
    return (*(int*)b - *(int*)a);
}
// 调用: qsort(arr, n, sizeof(int), ascending);
```

### 第14章：动态内存分配

**1. `malloc` 和 `calloc` 的区别。**

答：`malloc` 只分配内存，不初始化；`calloc` 分配内存并将所有字节初始化为零。`calloc` 参数为 `(数量, 大小)`，`malloc` 参数为 `(总大小)`。

**2. 动态分配一个整型数组并初始化。**

```c
int n = 10;
int *arr = malloc(n * sizeof(int));
if (!arr) { /* 处理失败 */ }
for (int i = 0; i < n; i++) {
    arr[i] = i * 2;
}
// ... 使用 arr ...
free(arr);
arr = NULL;
```

**3. 什么是内存泄漏？如何避免？**

答：内存泄漏是分配了内存但从未释放，导致可用内存逐渐减少。避免方法：每个 `malloc`/`calloc` 都要有对应的 `free`；使用 Valgrind 检测；养成良好的资源管理习惯。

### 第15章：结构体

**1. 定义一个学生结构体，包含姓名、学号、成绩。**

```c
struct Student {
    char name[50];
    int id;
    float score;
};
```

**2. 结构体数组，按成绩排序。**

```c
int compare_student(const void *a, const void *b) {
    const struct Student *s1 = a, *s2 = b;
    if (s1->score < s2->score) return 1;
    if (s1->score > s2->score) return -1;
    return 0;
}
qsort(students, count, sizeof(struct Student), compare_student);
```

**3. 结构体变量和结构体指针访问成员的区别。**

答：结构体变量用 `.` 运算符（如 `s.name`）；结构体指针用 `->` 运算符（如 `p->name`），等价于 `(*p).name`。

### 第16章：共用体与枚举

**1. 共用体和结构体的本质区别是什么？**

答：结构体所有成员各占独立内存，大小等于各成员大小之和（加填充）；共用体所有成员共享同一块内存，大小等于最大成员的大小。同一时间只能存储一个成员。

**2. 用枚举表示一周的天数。**

```c
enum Weekday {
    MON = 1, TUE, WED, THU, FRI, SAT, SUN
};
```

**3. 写一个程序，用 `union` 判断当前系统的字节序。**

```c
int is_little_endian(void) {
    union { int i; char c; } u;
    u.i = 1;
    return u.c == 1;  // 1 表示小端
}
```

### 第17章：文件操作

**1. 写一个程序，读取文本文件并统计行数。**

```c
int count_lines(const char *filename) {
    FILE *fp = fopen(filename, "r");
    if (!fp) return -1;
    int lines = 0;
    char ch;
    while ((ch = fgetc(fp)) != EOF) {
        if (ch == '\n') lines++;
    }
    fclose(fp);
    return lines;
}
```

**2. `fgets` 和 `fscanf` 的区别。**

答：`fgets` 读一整行（含空格），遇到换行或缓冲区满时停止，保留换行符；`fscanf` 按格式解析，读字符串时遇到空白字符就停止。推荐用 `fgets` + `sscanf` 组合。

**3. 二进制文件和文本文件的区别。**

答：文本文件存储可读字符，每行以换行符结束，不同系统换行符不同（`\n` vs `\r\n`）；二进制文件存储原始字节，不做任何转换，适合存储图片、音频、结构体等。

### 第18章：高级指针

**1. 声明一个指向"返回 int 且接受两个 int 参数的函数"的指针数组。**

```c
int (*func_table[10])(int, int);
```

**2. `void*` 指针的用途和限制。**

答：用途：通用指针类型，可以存储任何类型的指针，用于实现通用函数（如 `qsort`、`malloc`）。限制：不能直接解引用（必须先转换为具体类型），不能做指针算术运算。

**3. 使用 `const` 和指针的三种形式。**

```c
const int *p;      // 指向的内容不可修改
int * const p;     // 指针本身不可修改
const int * const p; // 两者都不可修改
```

### 第19章：位运算

**1. 判断一个整数是否为 2 的幂。**

```c
int is_power_of_two(int n) {
    return n > 0 && (n & (n - 1)) == 0;
}
```

**2. 不使用临时变量交换两个整数。**

```c
void swap_xor(int *a, int *b) {
    *a = *a ^ *b;
    *b = *a ^ *b;
    *a = *a ^ *b;
}
```

**3. 位运算的常见应用场景。**

答：权限标志位（位掩码）、快速乘除（`<<` 和 `>>`）、状态存储、加密算法、图形处理、嵌入式编程中的寄存器操作。

### 第20章：多文件编程

**1. 创建一个包含数学函数的多文件项目。**

```
math/
├── math_utils.h   # 函数声明
├── math_utils.c   # 函数实现
├── main.c         # 使用
└── Makefile
```

**2. `static` 函数的作用。**

答：`static` 函数限制作用域为当前文件，其他文件无法访问（即使有 `extern` 声明）。用于实现模块内部的"私有"函数。

**3. 头文件中应该放什么？不应该放什么？**

答：应该放：函数声明、类型定义（`typedef`、`struct`）、宏定义、`extern` 变量声明、注释。不应该放：函数实现（除非 `static inline`）、全局变量定义（会导致重复定义）。

---

## G.3 第21-30章参考答案

### 第21章：链表

**1. 实现单向链表的插入操作。**

参见第58章 `todolist_add` 实现。

**2. 反转单向链表。**

```c
Node* reverse(Node *head) {
    Node *prev = NULL, *cur = head, *next;
    while (cur) {
        next = cur->next;
        cur->next = prev;
        prev = cur;
        cur = next;
    }
    return prev;  // 新的头节点
}
```

**3. 检测链表是否有环。**

```c
int has_cycle(Node *head) {
    Node *slow = head, *fast = head;
    while (fast && fast->next) {
        slow = slow->next;
        fast = fast->next->next;
        if (slow == fast) return 1;
    }
    return 0;
}
```

### 第22章：栈

**1. 用数组实现栈。**

```c
#define MAX 100
typedef struct {
    int data[MAX];
    int top;
} Stack;

void push(Stack *s, int val) {
    if (s->top < MAX - 1) s->data[++(s->top)] = val;
}
int pop(Stack *s) {
    if (s->top >= 0) return s->data[(s->top)--];
    return -1;  // 空栈
}
```

**2. 用栈实现括号匹配。**

```c
int is_balanced(const char *expr) {
    Stack s = {.top = -1};
    for (int i = 0; expr[i]; i++) {
        if (expr[i] == '(') push(&s, '(');
        else if (expr[i] == ')') {
            if (s.top == -1) return 0;
            pop(&s);
        }
    }
    return s.top == -1;
}
```

**3. 栈的应用场景。**

答：函数调用栈、表达式求值（中缀转后缀）、括号匹配、撤销操作（Undo）、浏览器的前进后退、深度优先搜索。

### 第23章：队列

**1. 用链表实现队列。**

```c
typedef struct QNode {
    int data;
    struct QNode *next;
} QNode;

typedef struct {
    QNode *front, *rear;
} Queue;

void enqueue(Queue *q, int val) {
    QNode *node = malloc(sizeof(QNode));
    node->data = val; node->next = NULL;
    if (!q->rear) q->front = q->rear = node;
    else { q->rear->next = node; q->rear = node; }
}
int dequeue(Queue *q) {
    if (!q->front) return -1;
    QNode *temp = q->front;
    int val = temp->data;
    q->front = q->front->next;
    if (!q->front) q->rear = NULL;
    free(temp);
    return val;
}
```

**2. 循环队列的优势。**

答：避免普通数组队列在出队后产生"假溢出"（front 前移，前面的空间无法利用）。循环队列通过取模运算重用空间，固定大小的数组能持续使用。

**3. 队列的应用场景。**

答：任务调度（打印队列）、消息队列、广度优先搜索、缓冲区管理（生产者-消费者模型）、网络数据包排队。

### 第24章：二叉树

**1. 实现二叉树的中序遍历。**

```c
void inorder(TreeNode *root) {
    if (!root) return;
    inorder(root->left);
    printf("%d ", root->val);
    inorder(root->right);
}
```

**2. 计算二叉树的深度。**

```c
int max_depth(TreeNode *root) {
    if (!root) return 0;
    int left = max_depth(root->left);
    int right = max_depth(root->right);
    return (left > right ? left : right) + 1;
}
```

**3. 满二叉树和完全二叉树的区别。**

答：满二叉树：每个节点要么是叶子节点，要么有两个子节点，且所有叶子在同一层。完全二叉树：除最后一层外全满，且最后一层节点靠左对齐。

### 第25章：堆

**1. 用数组实现一个小顶堆。**

```c
void heapify_down(int arr[], int n, int i) {
    int smallest = i;
    int left = 2 * i + 1, right = 2 * i + 2;
    if (left < n && arr[left] < arr[smallest]) smallest = left;
    if (right < n && arr[right] < arr[smallest]) smallest = right;
    if (smallest != i) {
        int temp = arr[i]; arr[i] = arr[smallest]; arr[smallest] = temp;
        heapify_down(arr, n, smallest);
    }
}
```

**2. 堆排序的思路。**

答：1) 将数组构建为最大堆（自底向上 heapify）；2) 依次取出堆顶（最大值）放到数组末尾，缩小堆范围，重新 heapify；3) 重复直到堆为空，数组变为升序。

**3. 堆（heap）和栈（stack）在数据结构上的区别。**

答：堆（数据结构）是一种满足堆性质的完全二叉树，用于快速获取最大/最小值；栈（数据结构）是一种 LIFO 线性结构，只能在一端操作。不要与内存中的堆和栈混淆。

### 第26章：哈希表

**1. 实现一个简单的哈希表。**

参见第60章完整实现。

**2. 哈希冲突的解决方法有哪些？**

答：链地址法（冲突的键值对挂在同一链表中）、开放地址法（线性探测、平方探测、双重哈希）。链地址法实现简单，删除方便。

**3. 哈希表的应用场景。**

答：数据库索引、缓存（如 Redis）、字典/集合实现、去重、计数统计、符号表（编译器）。

### 第27章：错误处理

**1. `errno` 的作用和使用方法。**

答：`errno` 是全局错误码变量，系统调用或库函数失败时设置它。使用前需要 `#include <errno.h>`，用 `perror` 或 `strerror(errno)` 获取可读错误信息。注意：成功时 `errno` 不会被重置。

**2. 防御性编程的原则。**

答：1) 检查所有函数返回值；2) 参数合法性检查；3) 空指针检查；4) 边界条件检查；5) 假设一切可能出错。

**3. 写一个安全的文件读取函数。**

```c
char* safe_read_file(const char *filename) {
    if (!filename) return NULL;
    FILE *fp = fopen(filename, "r");
    if (!fp) return NULL;
    fseek(fp, 0, SEEK_END);
    long size = ftell(fp);
    fseek(fp, 0, SEEK_SET);
    if (size < 0) { fclose(fp); return NULL; }
    char *buf = malloc(size + 1);
    if (!buf) { fclose(fp); return NULL; }
    fread(buf, 1, size, fp);
    buf[size] = '\0';
    fclose(fp);
    return buf;
}
```

### 第28章：时间处理

**1. 计算两个日期之间相差的天数。**

```c
#include <time.h>
int days_between(struct tm date1, struct tm date2) {
    time_t t1 = mktime(&date1);
    time_t t2 = mktime(&date2);
    return (int)(difftime(t2, t1) / 86400);
}
```

**2. 格式化输出当前时间。**

```c
time_t now = time(NULL);
struct tm *t = localtime(&now);
char buf[64];
strftime(buf, sizeof(buf), "%Y年%m月%d日 %H:%M:%S", t);
printf("%s\n", buf);
```

**3. 测量一段代码的执行时间。**

```c
clock_t start = clock();
// ... 被测量的代码 ...
clock_t end = clock();
double elapsed = (double)(end - start) / CLOCKS_PER_SEC;
printf("执行时间: %.3f 秒\n", elapsed);
```

### 第29章：进程

**1. `fork()` 的返回值含义。**

答：在父进程中返回子进程的 PID（>0）；在子进程中返回 0；出错时返回 -1。

**2. 僵尸进程和孤儿进程的区别。**

答：僵尸进程：子进程已退出但父进程未调用 `wait()` 回收；孤儿进程：父进程先退出，子进程被 init 收养。

**3. 用 `fork` 和 `exec` 实现一个简单的 shell。**

```c
#include <unistd.h>
#include <sys/wait.h>
pid_t pid = fork();
if (pid == 0) {
    execlp("ls", "ls", "-l", NULL);
    perror("execlp");
    _exit(1);
} else if (pid > 0) {
    wait(NULL);
}
```

### 第30章：线程

**1. 创建两个线程，一个打印奇数，一个打印偶数。**

```c
void* print_odd(void *arg) {
    for (int i = 1; i <= 19; i += 2) printf("奇数: %d\n", i);
    return NULL;
}
void* print_even(void *arg) {
    for (int i = 2; i <= 20; i += 2) printf("偶数: %d\n", i);
    return NULL;
}
// main: pthread_create + pthread_join
```

**2. 互斥锁的作用。**

答：保证同一时间只有一个线程访问临界区，防止竞态条件。用法：`pthread_mutex_lock` 锁定，`pthread_mutex_unlock` 解锁。

**3. 死锁的四个必要条件。**

答：1) 互斥条件（资源不能共享）；2) 持有并等待（持有资源的同时等待其他资源）；3) 不可剥夺；4) 循环等待。破坏任一条件即可防止死锁。

---

## G.4 第31-40章参考答案

### 第31章：网络编程

**1. TCP 和 UDP 的区别。**

答：TCP 是面向连接的可靠协议（三次握手、确认重传、有序）；UDP 是无连接的不可靠协议（无连接、不保证送达、无序但更快）。TCP 适合文件传输、HTTP；UDP 适合视频流、DNS。

**2. 实现一个简单的 TCP 客户端。**

参见第59章 `main.c` 中的 Socket 创建流程。客户端需要 `socket()` → `connect()` → `send()`/`recv()`。

**3. 什么是 I/O 多路复用？**

答：用一个线程同时监控多个文件描述符，哪个就绪就处理哪个。`select` 是最基础的实现，`poll` 是改进版，`epoll`（Linux）是高性能实现。

### 第32-40章：（略）

第32-40章涉及高级主题，练习题答案根据各章具体内容而定。思路与上述章节一致：先分析问题，再设计数据结构，最后实现并测试。

---

## G.5 第41-57章参考答案

第41-57章为进阶主题（如排序算法、查找算法、编码规范、调试技巧、性能优化等），练习题答案需要结合具体代码实现。

### 排序算法练习

**快速排序实现：**

```c
void quicksort(int arr[], int low, int high) {
    if (low >= high) return;
    int pivot = arr[high];
    int i = low - 1;
    for (int j = low; j < high; j++) {
        if (arr[j] < pivot) {
            i++;
            int temp = arr[i]; arr[i] = arr[j]; arr[j] = temp;
        }
    }
    int temp = arr[i + 1]; arr[i + 1] = arr[high]; arr[high] = temp;
    quicksort(arr, low, i);
    quicksort(arr, i + 2, high);
}
```

---

## G.6 第58章：TODO命令行工具

**1. 增加 `clear` 命令。**

```c
// 在 main.c 中添加
else if (strcmp(cmd, "clear") == 0) {
    todolist_free(&list);
    todolist_init(&list);
    remove(FILENAME);  // 删除数据文件
    printf("所有任务已清空\n");
}
```

**2. `list done` 和 `list todo` 参数支持。**

```c
// 修改 todolist_print 或新增函数
void todolist_print_filtered(TodoList *list, int show_done) {
    Task *cur = list->head;
    int found = 0;
    while (cur) {
        if ((show_done && cur->status == 1) || (!show_done && cur->status == 0)) {
            printf("%-4d [%s] %s\n", cur->id,
                   cur->status == 1 ? "✓" : " ", cur->description);
            found = 1;
        }
        cur = cur->next;
    }
    if (!found) printf("（无匹配任务）\n");
}
```

**3. 增加任务优先级。**

```c
// 在 Task 结构体中添加
int priority;  // 0=低, 1=中, 2=高

// 文件格式改为: id|description|status|priority
// 加载时解析: sscanf(line, "%d|%[^|]|%d|%d", &id, desc, &status, &priority)
```

**4. 检测重复任务。**

```c
// 在 todolist_add 中，创建新节点前检查
Task *cur = list->head;
while (cur) {
    if (strcmp(cur->description, desc) == 0) {
        printf("任务已存在: #%d %s\n", cur->id, desc);
        return -1;  // 或返回 0
    }
    cur = cur->next;
}
```

**5. 双向链表 + swap 命令。**

```c
// Task 结构体增加 prev 指针
typedef struct Task {
    // ... 原有字段 ...
    struct Task *prev;
} Task;

// swap 交换两个节点的数据（不改变指针结构，更简单）
void todolist_swap(TodoList *list, int id1, int id2) {
    Task *t1 = find_task(list, id1);
    Task *t2 = find_task(list, id2);
    if (!t1 || !t2) return;
    // 交换 description 和 status（不交换 id）
    char temp_desc[MAX_DESC_LEN];
    int temp_status;
    strcpy(temp_desc, t1->description);
    temp_status = t1->status;
    strcpy(t1->description, t2->description);
    t1->status = t2->status;
    strcpy(t2->description, temp_desc);
    t2->status = temp_status;
}
```

---

## G.7 第59章：简易HTTP服务器

**1. POST 方法支持。**

```c
// 在 http_send_response 中增加 POST 分支
else if (strcmp(req->method, "POST") == 0) {
    // 解析 Content-Length
    const char *cl = strstr(raw_request, "Content-Length: ");
    int content_length = 0;
    if (cl) sscanf(cl, "Content-Length: %d", &content_length);

    // 找到请求体
    const char *body = strstr(raw_request, "\r\n\r\n");
    if (body) {
        body += 4;
        printf("[POST 数据] %.*s\n", content_length, body);
    }

    const char *ok = "HTTP/1.1 200 OK\r\nContent-Length: 2\r\n\r\nOK";
    send(client_fd, ok, strlen(ok), 0);
}
```

**2. 目录列表功能。**

```c
// 使用 opendir/readdir 遍历目录
#include <dirent.h>
void list_directory(int client_fd, const char *dirpath) {
    DIR *dir = opendir(dirpath);
    if (!dir) { send_error(client_fd, 404, "Not Found"); return; }

    // 生成 HTML 目录列表
    char html[8192] = "<html><body><h1>Directory Listing</h1><ul>";
    struct dirent *entry;
    while ((entry = readdir(dir)) != NULL) {
        char line[256];
        snprintf(line, sizeof(line),
                 "<li><a href=\"%s\">%s</a></li>",
                 entry->d_name, entry->d_name);
        strcat(html, line);
    }
    strcat(html, "</ul></body></html>");
    closedir(dir);

    send_header(client_fd, 200, "OK", "text/html", strlen(html));
    send(client_fd, html, strlen(html), 0);
}
```

**3. 访问日志。**

```c
void log_access(const char *ip, const char *method,
                const char *path, int status) {
    time_t now = time(NULL);
    char time_str[32];
    strftime(time_str, sizeof(time_str), "%Y-%m-%d %H:%M:%S",
             localtime(&now));
    FILE *log = fopen("access.log", "a");
    if (log) {
        fprintf(log, "%s %s %s %s %d\n", time_str, ip, method, path, status);
        fclose(log);
    }
}
```

**4. 线程池（思路）。**

```c
// 预创建 N 个线程，共享一个任务队列
// 主线程 accept 后，将 client_fd 放入队列
// 工作线程从队列取出 client_fd 并处理
// 需要互斥锁保护队列，条件变量通知工作线程
```

**5. Keep-Alive 支持。**

```c
// 响应头中设置 Connection: keep-alive
// 在 handle_client 中循环读取请求，直到客户端关闭或超时
// 需要设置超时（使用 setsockopt 设置 SO_RCVTIMEO）
```

---

## G.8 第60章：简易数据库（KV存储）

**1. EXISTS 命令。**

```c
else if (strcmp(cmd, "EXISTS") == 0) {
    if (n < 2) { printf("用法: EXISTS <key>\n"); continue; }
    const char *val = ht_get(&ht, key);
    printf("%d\n", val ? 1 : 0);
}
```

**2. RENAME 命令。**

```c
else if (strcmp(cmd, "RENAME") == 0) {
    if (n < 3) { printf("用法: RENAME <old> <new>\n"); continue; }
    if (ht_get(&ht, value)) {
        printf("错误: 目标键 '%s' 已存在\n", value);
        continue;
    }
    const char *val = ht_get(&ht, key);
    if (!val) {
        printf("错误: 源键 '%s' 不存在\n", key);
        continue;
    }
    ht_set(&ht, value, val);
    ht_del(&ht, key);
    printf("OK\n");
}
```

**3. 哈希表自动扩容。**

```c
void ht_resize(HashTable *ht, int new_size) {
    // 保存旧数据
    Entry **old_buckets = ht->buckets;
    int old_size = TABLE_SIZE;  // 需要改为动态大小

    // 重新分配桶数组
    memset(ht->buckets, 0, sizeof(ht->buckets));
    ht->count = 0;

    // 重新哈希所有键值对
    for (int i = 0; i < old_size; i++) {
        Entry *cur = old_buckets[i];
        while (cur) {
            ht_set(ht, cur->key, cur->value);
            Entry *next = cur->next;
            free(cur);
            cur = next;
        }
    }
}
```

**4. DUMP 命令（JSON 格式）。**

```c
else if (strcmp(cmd, "DUMP") == 0) {
    printf("{\n");
    int first = 1;
    for (int i = 0; i < TABLE_SIZE; i++) {
        Entry *cur = ht.buckets[i];
        while (cur) {
            if (!first) printf(",\n");
            printf("  \"%s\": \"%s\"", cur->key, cur->value);
            first = 0;
            cur = cur->next;
        }
    }
    printf("\n}\n");
}
```

**5. 事务支持（思路）。**

```c
// BEGIN: 深拷贝当前哈希表（快照）
// SET/GET/DEL: 操作在快照上
// COMMIT: 用快照替换原哈希表，释放原表
// ROLLBACK: 释放快照，保留原表
```

---

## G.9 附录A：C语言关键字速查

**1. `static` 关键字的三种用法。**

- 函数内静态局部变量：`void f() { static int x = 0; x++; }`（保持值）
- 文件内静态全局变量：`static int counter;`（限制作用域）
- 静态函数：`static void helper() {}`（文件内私有）

**2. `typedef` 和 `#define` 的区别。**

```c
typedef int* IntPtr;    // 创建类型别名，IntPtr a, b → 两个都是指针
#define IntPtr int*     // 文本替换，IntPtr a, b → a 是指针，b 是 int
```

**3. 不能用作变量名的标识符。**

答：`float` 是关键字，不能用作变量名。`_count` 可以（下划线开头合法）。`main` 可以但不推荐（与 `main` 函数同名会造成混淆）。

---

## G.10 附录B：C标准库函数速查

**1. 用 `fgets` 和 `sscanf` 安全读取整数。**

```c
int safe_read_int(void) {
    char line[32];
    int value;
    if (!fgets(line, sizeof(line), stdin)) return 0;
    if (sscanf(line, "%d", &value) == 1) return value;
    return 0;  // 解析失败
}
```

**2. 用 `qsort` 排序字符串数组。**

```c
int cmp_string(const void *a, const void *b) {
    return strcmp(*(const char**)a, *(const char**)b);
}
// char *words[] = {"banana", "apple", "cherry"};
// qsort(words, 3, sizeof(char*), cmp_string);
```

**3. 用 `ftell` 和 `fseek` 计算文件行数。**

```c
int count_lines(const char *filename) {
    FILE *fp = fopen(filename, "r");
    if (!fp) return -1;
    int lines = 0;
    char ch;
    while ((ch = fgetc(fp)) != EOF) {
        if (ch == '\n') lines++;
    }
    fclose(fp);
    return lines;
}
```

---

## G.11 附录C：编译错误与排错指南

**1. 故意制造段错误，用 gdb 定位。**

```c
// 故意段错误代码
int *p = NULL;
*p = 42;  // Segfault

// gdb 操作:
// gdb ./program
// (gdb) run
// (gdb) print p   → 显示 NULL
// (gdb) backtrace → 显示崩溃位置
```

**2. 内存泄漏检测代码。**

```c
// 内存泄漏代码
void leak(void) {
    int *p = malloc(100 * sizeof(int));  // 未 free
}
// Valgrind: valgrind --leak-check=full ./program
// 输出: 400 bytes in 1 blocks are definitely lost
```

**3. 代码问题分析。**

```c
#include <stdio.h>
int main(void) {
    int x;              // 未初始化
    printf("%d\n", x);  // 使用未初始化的值（UB）
    if (x = 5) {        // 赋值而非比较，警告: suggest parentheses
        printf("x is 5\n");
    }
    return;             // main 应返回 int
}
```

修复：初始化 `x`，`if (x == 5)`，`return 0;`。

---

## G.12 附录D：运算符优先级全表

**1. 表达式求值（设 a=2, b=4, c=6）。**

- `a + b * c` = `2 + 24` = 26（乘除优先级高于加减）
- `a << 2 + 1` = `a << (2 + 1)` = `2 << 3` = 16（加法优先级高于移位）
- `a & b | c` = `(2 & 4) | 6` = `0 | 6` = 6（从左到右结合）
- `a && b || c` = `(2 && 4) || 6` = `1 || 6` = 1（逻辑与优先级高于逻辑或）

**2. 未定义行为分析。**

```c
int a = 5;
int b = a++ + ++a;  // 未定义行为！
```

C 标准没有规定 `a++` 和 `++a` 的执行顺序，也没有规定 `a` 在什么时候被修改。不同编译器结果不同（可能是 10、11 或 12）。这是典型的未定义行为：同一表达式内多次修改同一变量且无序列点分隔。

**3. 加括号使意图明确。**

```c
result = (x + (y * z)) << 2;  // 或 x + ((y * z) << 2)，取决于意图
flag = (a && b) || (c && d);  // 即使 && 优先级高于 ||，加括号更清晰
ptr = (*(p++)) + 1;           // 先取 *p，p 自增，再加 1
```

---

## G.13 附录E：ASCII码表

**1. 打印可打印字符的 ASCII 码表。**

```c
for (int i = 32; i <= 126; i++) {
    printf("ASCII %3d = '%c'\n", i, (char)i);
}
```

**2. 不用 `<ctype.h>` 实现 `is_digit` 和 `is_alpha`。**

```c
int is_digit(char c) {
    return c >= '0' && c <= '9';
}
int is_alpha(char c) {
    return (c >= 'A' && c <= 'Z') || (c >= 'a' && c <= 'z');
}
```

**3. 从字符 `'7'` 得到整数 7。**

```c
// 方法一：利用 ASCII 连续性
int n1 = '7' - '0';  // 55 - 48 = 7

// 方法二：使用 sscanf
int n2;
sscanf("7", "%d", &n2);
```

---

## G.14 附录F：术语速查

**1. 同一英文词的两个含义。**

- **heap**：内存堆（`malloc` 分配的区域）vs 数据结构堆（完全二叉树）
- **stack**：内存栈（函数调用栈）vs 数据结构栈（LIFO 线性结构）
- **static**：存储类关键字（静态变量）vs 普通英语含义

**2. "传值调用"和"值传递"的区别。**

答：这两个术语在 C 语言中含义相同，都指函数调用时将实参的值复制给形参。C 语言只有传值调用，没有"传引用调用"（那是 C++ 的概念）。C 语言通过传指针的地址值来模拟传引用效果。

**3. 向初学者解释"栈溢出"。**

答：想象一摞盘子，每次函数调用就放一个盘子，函数返回就取走一个。如果盘子太高（递归太深或局部变量太大），摞不下了，就是栈溢出。避免方法：确保递归有基线条件，不在函数中分配超大数组。

---

## G.15 三问

1. **练习题答案中，为什么有些未给出完整代码？** 复杂题目的答案只是思路或关键代码片段，完整实现需要读者结合上下文自己完成。这是有意为之——编程能力在"写"中提升，而不是在"看"中。

2. **答案和我的实现不同，哪个是对的？** 编程没有唯一正确答案。只要你的代码能正确运行、符合题目要求，就是对的。答案只是参考实现之一。

3. **遇到答案看不懂的题目怎么办？** 回到对应章节重新阅读关键概念，尝试理解答案的每一步。如果仍然不懂，可以搜索相关主题的更多资料，或在社区提问。

---

## G.16 本章小结

| 范围 | 题目数量 | 说明 |
|------|----------|------|
| 第1-10章 | 约 30 题 | 基础语法 |
| 第11-20章 | 约 30 题 | 指针与结构体 |
| 第21-30章 | 约 30 题 | 数据结构与系统编程 |
| 第31-57章 | 略 | 网络编程与进阶主题 |
| 第58-60章 | 15 题 | 实战项目扩展 |
| 附录A-F | 约 15 题 | 速查表练习 |

---

*本附录持续更新。如果你发现答案有误或有更好的解法，欢迎指出。*