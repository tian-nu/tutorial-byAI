# 30 — 动态内存分配（一）：malloc 和 free

> - 对应文档版本：C语言精通教程 outline v1
> - 适用环境：C99/C11，gcc编译器
> - 读者角色：C语言零基础的开发者
> - 预计耗时：新手 70 分钟 / 熟手 35 分钟
> - 前置教程：第29章（指针（五）：函数指针）
> - 可视化：无

---

## 我在做什么？

到目前为止，你创建的所有变量和数组，大小都是在编译时确定的。但现实中，你经常不知道需要多少内存——比如用户输入多少条记录，或者从文件读取多少行数据。

**动态内存分配**让你在程序运行时申请内存，用完了再归还。这块内存来自 *堆（Heap）* *此术语见附录F*，而不是 *栈（Stack）* *此术语见附录F*。读完这一章，你会用 `malloc` 申请内存，用 `free` 释放内存，并且理解 *内存泄漏* *此术语见附录F* 是什么以及如何避免。

---

## 一、为什么需要动态内存

### 1.1 栈的局限

```c
// 栈上的数组：大小必须编译时确定
int arr[100];   // 问题一：如果只需要 10 个，浪费 90 个
                // 问题二：如果需要 1000 个，数组不够大
                // 问题三：函数返回后，数组就消失了
```

```text
栈（Stack）：
┌──────────────────────┐
│ main 的栈帧           │
│  ┌─────────────────┐ │
│  │ int arr[100]    │ │  ← 函数返回时自动销毁
│  └─────────────────┘ │
│  ┌─────────────────┐ │
│  │ 其他局部变量     │ │
│  └─────────────────┘ │
└──────────────────────┘
```

栈的特点：
- 自动管理：进入函数时分配，离开时释放。
- 大小有限：通常只有几 MB，大数组容易栈溢出。
- 编译时确定大小：不能根据运行时数据调整。

### 1.2 堆：自由的内存池

```text
堆（Heap）：
┌──────────────────────────────────────┐
│  ┌──────────┐  ┌──────────┐         │
│  │  malloc  │  │  malloc  │  空闲区  │
│  │  申请 100B│  │  申请 50B │         │
│  └──────────┘  └──────────┘         │
│       ↑              ↑               │
│     需要手动 free   需要手动 free     │
└──────────────────────────────────────┘
```

堆的特点：
- 手动管理：你申请，你释放，编译器不管。
- 大小很大：受系统内存限制，通常几 GB。
- 运行时确定：可以根据用户输入决定分配多少。
- 跨函数生命期：函数返回后内存仍然有效。

---

## 二、`malloc`：申请内存

### 2.1 `malloc` 的基本用法

```c
#include <stdlib.h>

void *malloc(size_t size);
```

`malloc` 接收一个参数：要申请的**字节数**。返回一个 `void*` 指针，指向申请到的内存块。如果申请失败，返回 `NULL`。

```c
#include <stdio.h>
#include <stdlib.h>

int main() {
    // 申请 5 个 int 的空间
    int *arr = (int*)malloc(5 * sizeof(int));

    if (arr == NULL) {
        printf("内存分配失败！\n");
        return 1;
    }

    // 像普通数组一样使用
    for (int i = 0; i < 5; i++) {
        arr[i] = i * 10;
    }

    for (int i = 0; i < 5; i++) {
        printf("arr[%d] = %d\n", i, arr[i]);
    }

    // 用完了，归还内存
    free(arr);

    return 0;
}
```

### 2.2 `malloc` 的工作过程

```text
调用 malloc(20) 时：

1. 操作系统在堆中找到一块 20 字节的连续空闲空间
2. 标记这块空间为"已使用"
3. 返回这块空间的起始地址

堆：
申请前：┌────────────────────────────────────────┐
        │ 空闲  空闲  空闲  空闲  空闲  空闲  ... │
        └────────────────────────────────────────┘

申请后：┌────────────────────────────────────────┐
        │████ 已分配 ████│ 空闲  空闲  空闲  ... │
        └────────────────────────────────────────┘
        ↑
     返回这个地址
```

### 2.3 `malloc` 不初始化内存

`malloc` 申请的内存内容是**未定义的**——可能是之前用过的残留数据，也可能是全零，取决于系统和运气。

```c
int *arr = (int*)malloc(5 * sizeof(int));
// arr[0] 的值是随机的！不要假设它是 0
```

如果希望内存初始化为零，使用 `calloc`（第 31 章讲）。

### 2.4 动态分配字符串

```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main() {
    char *greeting = (char*)malloc(20 * sizeof(char));

    if (greeting == NULL) {
        printf("内存分配失败！\n");
        return 1;
    }

    strcpy(greeting, "Hello, World!");
    printf("%s\n", greeting);

    free(greeting);
    return 0;
}
```

### 2.5 动态分配可变大小

```c
#include <stdio.h>
#include <stdlib.h>

int main() {
    int n;
    printf("请输入数组大小：");
    scanf("%d", &n);

    // 运行时确定大小
    int *arr = (int*)malloc(n * sizeof(int));

    if (arr == NULL) {
        printf("内存分配失败！数组太大？\n");
        return 1;
    }

    for (int i = 0; i < n; i++) {
        arr[i] = i * 2;
        printf("%d ", arr[i]);
    }
    printf("\n");

    free(arr);
    return 0;
}
```

---

## 三、`free`：释放内存

### 3.1 为什么必须 `free`

堆内存不会自动回收。如果你只申请不释放，程序占用的内存会越来越多，最终可能耗尽系统内存。这就是 *内存泄漏* *此术语见附录F*。

```c
// 内存泄漏示例
void leak() {
    int *p = malloc(100 * sizeof(int));
    // 没有 free(p)！
    // 函数返回后，p 被销毁，但 100 个 int 的内存还占着
    // 而且没有任何指针指向它，永远无法释放
}
```

### 3.2 `free` 的正确用法

```c
int *p = malloc(100);
// ... 使用 p ...
free(p);     // 释放内存
p = NULL;    // 好习惯：避免悬空指针
```

```text
free(p) 之后：
┌────────────────────────────────────────┐
│████ 已分配 ████│░░░░ 已释放 ░░░░│ 空闲  │
│                └── 这块内存归还给堆    │
└────────────────────────────────────────┘
```

### 3.3 `free` 的规则

1. **只能 free 由 malloc/calloc/realloc 返回的指针**。
2. **不能 free 同一个指针两次**（Double Free，会导致崩溃）。
3. **free 之后，指针变成悬空指针**，建议立即置为 `NULL`。
4. **free(NULL) 是安全的**（什么也不做）。

```c
int arr[10];
free(arr);    // 错误！arr 不是 malloc 分配的

int *p = malloc(10);
free(p);
free(p);      // 错误！Double Free
```

---

## 四、内存泄漏

### 4.1 什么是内存泄漏

*内存泄漏* *此术语见附录F* 是指：程序申请了堆内存，但丢失了指向它的指针，无法释放。

```c
void cause_leak() {
    int *p = malloc(1024 * 1024);  // 申请 1MB
    p = malloc(2048 * 2048);       // 又申请 2MB，原来的 1MB 丢了！
    free(p);                       // 只释放了 2MB，1MB 泄漏了
}
```

```text
第一次 malloc：
p → ┌──────────┐
    │ 1MB 内存  │
    └──────────┘

第二次 malloc：
p → ┌──────────┐    ┌──────────┐
    │ 2MB 内存  │    │ 1MB 内存  │ ← 泄漏！没有任何指针指向它
    └──────────┘    └──────────┘
```

### 4.2 内存泄漏的危害

- **短时间运行的程序**：泄漏影响不大，程序退出后操作系统回收所有内存。
- **长时间运行的程序**（服务器、数据库）：泄漏会逐渐耗尽内存，最终系统崩溃。
- **嵌入式系统**：内存极其有限，泄漏几 KB 都可能导致问题。

### 4.3 如何检测内存泄漏

**Valgrind** *此术语见附录F* 是 Linux 下最常用的内存检测工具：

```bash
$ gcc -g -o program program.c
$ valgrind --leak-check=full ./program
```

输出示例：
```text
==12345== LEAK SUMMARY:
==12345==    definitely lost: 100 bytes in 1 blocks
==12345==    indirectly lost: 0 bytes in 0 blocks
==12345==      possibly lost: 0 bytes in 0 blocks
==12345==    still reachable: 0 bytes in 0 blocks
==12345==         suppressed: 0 bytes in 0 blocks
```

---

## 五、栈 vs 堆 对比

| | 栈（Stack） | 堆（Heap） |
|---|---|---|
| 管理方式 | 自动（编译器） | 手动（程序员） |
| 分配速度 | 极快（移动栈指针） | 较慢（需要查找空闲块） |
| 大小限制 | 几 MB | 几 GB |
| 生命期 | 离开作用域自动销毁 | 手动 free 才销毁 |
| 碎片化 | 无 | 可能产生碎片 |
| 典型用途 | 局部变量、小数组 | 大数组、不确定大小的数据 |

```text
内存布局全景：

高地址  ┌──────────────┐
        │   命令行参数   │
        │   环境变量     │
        ├──────────────┤
        │     栈       │
        │     ↓       │  ← 向下增长
        │              │
        │              │
        │     ↑       │  ← 向上增长
        │     堆       │
        ├──────────────┤
        │   BSS 段     │  ← 未初始化全局变量
        ├──────────────┤
        │  数据段       │  ← 已初始化全局变量
        ├──────────────┤
低地址  │  代码段       │  ← 程序指令
        └──────────────┘
```

---

## 六、常见错误与排错

### 6.1 忘记 `free`

❌ 错误示例：
```c
void process() {
    int *data = malloc(1000 * sizeof(int));
    // ... 使用 data ...
    // 忘记 free(data)！
}
```

✅ 正确示例：
```c
void process() {
    int *data = malloc(1000 * sizeof(int));
    // ... 使用 data ...
    free(data);
}
```

### 6.2 `free` 后继续使用

❌ 错误示例：
```c
int *p = malloc(sizeof(int));
*p = 42;
free(p);
printf("%d\n", *p);  // Use After Free！危险！
```

✅ 正确示例：
```c
int *p = malloc(sizeof(int));
*p = 42;
printf("%d\n", *p);  // 先用
free(p);             // 再释放
p = NULL;            // 标记为无效
```

### 6.3 `malloc` 后不检查 `NULL`

❌ 错误示例：
```c
int *p = malloc(1000000000000);  // 可能失败
*p = 42;                          // 如果 p 是 NULL，段错误！
```

✅ 正确示例：
```c
int *p = malloc(1000000000000);
if (p == NULL) {
    printf("内存分配失败\n");
    return 1;
}
*p = 42;
```

### 6.4 `sizeof` 用错类型

❌ 错误示例：
```c
int *p = malloc(100);  // 100 字节，只能存 25 个 int（假设 int 是 4 字节）
// 以为存了 100 个 int，实际只存了 25 个
```

✅ 正确示例：
```c
int *p = malloc(100 * sizeof(int));  // 100 个 int
```

---

## 我做得对不对？

用以下程序验证：

```c
#include <stdio.h>
#include <stdlib.h>

// 动态分配数组并求和
int sum_dynamic(int n) {
    int *arr = malloc(n * sizeof(int));
    if (arr == NULL) {
        return -1;
    }
    for (int i = 0; i < n; i++) {
        arr[i] = i + 1;
    }
    int total = 0;
    for (int i = 0; i < n; i++) {
        total += arr[i];
    }
    free(arr);
    return total;
}

int main() {
    // 测试1：基本 malloc/free
    int *p = malloc(sizeof(int));
    if (p != NULL) {
        *p = 42;
        printf("测试1：*p = %d (应为 42)\n", *p);
        free(p);
    }

    // 测试2：动态数组
    int n = 5;
    int *arr = malloc(n * sizeof(int));
    if (arr != NULL) {
        for (int i = 0; i < n; i++) arr[i] = i * 10;
        printf("测试2：arr[2] = %d (应为 20)\n", arr[2]);
        free(arr);
    }

    // 测试3：跨函数动态分配
    printf("测试3：sum_dynamic(100) = %d (应为 5050)\n", sum_dynamic(100));

    // 测试4：malloc 失败处理
    int *huge = malloc((size_t)-1);  // 几乎一定会失败
    printf("测试4：malloc 超大值返回 NULL？%s\n",
           huge == NULL ? "是 (正确)" : "否");

    return 0;
}
```

编译运行：
```bash
$ gcc -Wall -o test test.c
$ ./test
测试1：*p = 42 (应为 42)
测试2：arr[2] = 20 (应为 20)
测试3：sum_dynamic(100) = 5050 (应为 5050)
测试4：malloc 超大值返回 NULL？是 (正确)
```

---

## 不对怎么办？

| 现象 | 可能原因 | 解决 |
|------|----------|------|
| 段错误 | `malloc` 返回 NULL 但没检查 | 每次 `malloc` 后检查返回值 |
| 程序运行越久内存占用越大 | 内存泄漏 | 检查每个 `malloc` 是否有对应的 `free` |
| `free` 后程序崩溃 | Double Free | 确保每个 `malloc` 只 `free` 一次 |
| `free` 后程序崩溃 | `free` 了栈上的地址 | 只能 `free` 由 `malloc` 返回的指针 |
| 动态数组越界没报错 | 和普通数组一样，C 不检查 | 自己记录数组大小，遍历时检查边界 |

---

## 本章小结

| 知识点 | 一句话总结 |
|--------|-----------|
| 动态内存 | 运行时从堆上申请的内存，大小可以运行时确定 |
| `malloc` | 申请内存，返回 `void*`，失败返回 `NULL` |
| `free` | 释放 `malloc` 申请的内存 |
| 堆 vs 栈 | 堆手动管理、大而慢；栈自动管理、小而快 |
| 内存泄漏 | 申请了内存但没有释放，导致内存被白白占用 |
| 悬空指针 | `free` 后指针仍然指向已释放的内存 |
| Valgrind | Linux 下检测内存泄漏的工具 |

---

## 练习题

1. 写一个程序，让用户输入一个数字 `n`，然后动态分配一个长度为 `n` 的 `int` 数组，填充 1 到 `n`，打印所有元素，最后释放内存。

2. 写一个函数 `int* range(int start, int end, int *size)`，返回一个包含 `start` 到 `end`（含）所有整数的动态数组，`*size` 存储数组长度。在 `main` 中调用并打印结果，别忘了 `free`。

3. 写一个程序，模拟一个"动态待办事项列表"。用户可以输入 `add 任务名` 添加任务，输入 `list` 列出所有任务，输入 `quit` 退出。用动态内存存储任务列表。（提示：每次添加任务时用 `realloc` 扩充数组，或者先用固定大小，下一章再优化。）

4. （选做）用 Valgrind 检测你写的程序是否有内存泄漏。如果有，修复它。