# 31 — 动态内存分配（二）：calloc 和 realloc

> - 对应文档版本：C语言精通教程 outline v1
> - 适用环境：C99/C11，gcc编译器
> - 读者角色：C语言零基础的开发者
> - 预计耗时：新手 60 分钟 / 熟手 30 分钟
> - 前置教程：第30章（动态内存分配（一）：malloc 和 free）
> - 可视化：无

---

## 我在做什么？

上一章你学会了 `malloc` 和 `free`——申请和释放堆内存。但 `malloc` 有两个不足：它不初始化内存（内容是垃圾值），而且申请之后大小就固定了。

这一章教你 `calloc`（申请并清零）和 `realloc`（调整已分配内存的大小）。读完这一章，你能实现一个真正的**动态数组**——可以根据需要自动扩容的数组。同时，你会了解 `realloc` 的常见陷阱，以及 Use After Free 和 Double Free 等经典错误。

---

## 一、`calloc`：申请并清零

### 1.1 `calloc` 和 `malloc` 的区别

```c
// malloc：一个参数，总字节数，不初始化
int *p1 = malloc(5 * sizeof(int));

// calloc：两个参数，元素个数和每个元素大小，初始化为 0
int *p2 = calloc(5, sizeof(int));
```

```text
malloc(5 * sizeof(int)) 申请到的内存：
┌──────┬──────┬──────┬──────┬──────┐
│ 垃圾  │ 垃圾  │ 垃圾  │ 垃圾  │ 垃圾  │
└──────┴──────┴──────┴──────┴──────┘

calloc(5, sizeof(int)) 申请到的内存：
┌──────┬──────┬──────┬──────┬──────┐
│  0   │  0   │  0   │  0   │  0   │
└──────┴──────┴──────┴──────┴──────┘
```

### 1.2 `calloc` 的基本用法

```c
#include <stdio.h>
#include <stdlib.h>

int main() {
    int n = 5;
    int *arr = calloc(n, sizeof(int));

    if (arr == NULL) {
        printf("内存分配失败！\n");
        return 1;
    }

    // 验证：所有元素都是 0
    for (int i = 0; i < n; i++) {
        printf("arr[%d] = %d\n", i, arr[i]);  // 每个都输出 0
    }

    free(arr);
    return 0;
}
```

### 1.3 `calloc` 的两个参数

`calloc` 的第一个参数是**元素个数**，第二个参数是**每个元素的大小**。`calloc` 内部会把它们相乘得到总字节数。

```c
// 以下两者等价（但 calloc 额外做了清零）
int *p1 = malloc(10 * sizeof(int));
int *p2 = calloc(10, sizeof(int));
```

### 1.4 什么时候用 `calloc`

- 需要一个全零的数组（比如计数器、标志位数组）。
- 结构体数组，希望所有字段初始化为零。
- 字符串缓冲区，希望初始为空（`\0` 即 ASCII 0）。
- 不确定内存内容会影响后续逻辑时。

```c
// 经典用法：动态分配一个全零的计数器数组
int *counter = calloc(256, sizeof(int));  // 256 个计数器，初始为 0
// 统计字符频率
for (int i = 0; str[i] != '\0'; i++) {
    counter[(unsigned char)str[i]]++;
}
```

---

## 二、`realloc`：调整已分配内存的大小

### 2.1 为什么需要 `realloc`

假设你写了一个动态数组，初始分配了 10 个元素的空间。用户不断添加数据，10 个不够了怎么办？

```c
int *arr = malloc(10 * sizeof(int));
// ... 用户添加了 10 个元素，满了
// 现在需要更多空间！
```

`realloc` 让你**在保留原有数据的前提下**，改变已分配内存块的大小。

### 2.2 `realloc` 的基本用法

```c
void *realloc(void *ptr, size_t new_size);
```

- `ptr`：之前由 `malloc`/`calloc`/`realloc` 返回的指针。
- `new_size`：新的总字节数。
- 返回值：新内存块的地址（可能和原来一样，也可能不一样）。

```c
#include <stdio.h>
#include <stdlib.h>

int main() {
    // 初始分配 5 个 int
    int *arr = malloc(5 * sizeof(int));
    if (arr == NULL) return 1;

    for (int i = 0; i < 5; i++) {
        arr[i] = i * 10;
    }

    // 扩大到 10 个 int
    int *new_arr = realloc(arr, 10 * sizeof(int));
    if (new_arr == NULL) {
        printf("realloc 失败！\n");
        free(arr);   // 原内存仍然有效，记得释放
        return 1;
    }
    arr = new_arr;   // 更新指针

    // 新加入的 5 个元素值未定义（和 malloc 一样）
    for (int i = 5; i < 10; i++) {
        arr[i] = i * 10;
    }

    // 打印
    for (int i = 0; i < 10; i++) {
        printf("arr[%d] = %d\n", i, arr[i]);
    }

    free(arr);
    return 0;
}
```

### 2.3 `realloc` 的工作原理

```text
情况一：原内存块后面有足够的空闲空间
  原来：┌────┬────┬────┬────┬────┬────┬────┬────┬────┐
        │ 已分配（5个） │ 空闲          │ 其他数据    │
        └────┴────┴────┴────┴────┴────┴────┴────┴────┘
  之后：┌────┬────┬────┬────┬────┬────┬────┬────┬────┐
        │ 已分配（10个）                │ 其他数据    │
        └────┴────┴────┴────┴────┴────┴────┴────┴────┘
        ↑ 原地扩容，返回原地址，数据不变

情况二：原内存块后面没有足够的空闲空间
  原来：┌────┬────┬────┬────┬────┬────┬────┬────┬────┐
        │ 已分配（5个） │ 其他数据                   │
        └────┴────┴────┴────┴────┴────┴────┴────┴────┘
  之后：┌────┬────┬────┬────┬────┬────┬────┬────┬────┐
        │ 已释放（5个） │ 其他数据                   │
        └────┴────┴────┴────┴────┴────┴────┴────┴────┘
        
        ┌────┬────┬────┬────┬────┬────┬────┬────┬────┬────┐
        │ 新位置（10个）                                       │
        └────┴────┴────┴────┴────┴────┴────┴────┴────┴────┘
        ↑ 找到更大的空地，复制数据过去，返回新地址
```

**关键**：`realloc` 可能返回新地址（情况二），所以**必须用返回值更新指针**。

### 2.4 `realloc` 的安全用法

```c
// 不安全：如果 realloc 失败，arr 变成 NULL，原内存泄漏
arr = realloc(arr, new_size);

// 安全：先用临时变量接收
int *temp = realloc(arr, new_size);
if (temp == NULL) {
    // realloc 失败，arr 仍然有效，记得处理
    free(arr);
    return 1;
}
arr = temp;
```

### 2.5 `realloc` 也可以缩小

```c
int *arr = malloc(100 * sizeof(int));
// ... 使用 arr ...
int *temp = realloc(arr, 50 * sizeof(int));  // 缩小到 50 个
if (temp != NULL) arr = temp;
// 后 50 个元素的数据丢失了
```

---

## 三、实现动态数组

### 3.1 动态数组的设计

```c
#include <stdio.h>
#include <stdlib.h>

typedef struct {
    int *data;       // 数据存储
    int size;        // 当前元素个数
    int capacity;    // 已分配容量
} DynamicArray;

// 初始化
DynamicArray* da_create() {
    DynamicArray *da = malloc(sizeof(DynamicArray));
    if (da == NULL) return NULL;
    da->capacity = 4;                        // 初始容量 4
    da->size = 0;
    da->data = malloc(da->capacity * sizeof(int));
    if (da->data == NULL) {
        free(da);
        return NULL;
    }
    return da;
}

// 添加元素
void da_append(DynamicArray *da, int value) {
    // 需要扩容？
    if (da->size >= da->capacity) {
        da->capacity *= 2;                   // 容量翻倍
        int *temp = realloc(da->data, da->capacity * sizeof(int));
        if (temp == NULL) {
            printf("扩容失败！\n");
            return;
        }
        da->data = temp;
        printf("  [扩容] 容量变为 %d\n", da->capacity);
    }
    da->data[da->size] = value;
    da->size++;
}

// 获取元素
int da_get(DynamicArray *da, int index) {
    if (index < 0 || index >= da->size) {
        printf("索引越界！\n");
        return -1;
    }
    return da->data[index];
}

// 销毁
void da_destroy(DynamicArray *da) {
    free(da->data);
    free(da);
}

int main() {
    DynamicArray *da = da_create();
    if (da == NULL) return 1;

    printf("添加 10 个元素：\n");
    for (int i = 0; i < 10; i++) {
        da_append(da, i * 10);
    }

    printf("\n所有元素：\n");
    for (int i = 0; i < da->size; i++) {
        printf("  [%d] = %d\n", i, da_get(da, i));
    }
    printf("总容量：%d，已用：%d\n", da->capacity, da->size);

    da_destroy(da);
    return 0;
}
```

输出：
```text
添加 10 个元素：
  [扩容] 容量变为 8
  [扩容] 容量变为 16

所有元素：
  [0] = 0
  [1] = 10
  [2] = 20
  ...
  [9] = 90
总容量：16，已用：10
```

```text
扩容过程：
初始: capacity=4, size=0
加4个: capacity=4, size=4  (满了)
加第5个: capacity=8, size=5  (扩容)
加第8个: capacity=8, size=8  (满了)
加第9个: capacity=16, size=9 (扩容)
```

---

## 四、常见内存错误

### 4.1 Use After Free

```c
int *p = malloc(sizeof(int));
*p = 42;
free(p);
*p = 100;    // 错误！p 指向的内存已经释放了
```

`free` 之后，那块内存可能被分配给其他用途。继续使用它会导致数据损坏或崩溃。

### 4.2 Double Free

```c
int *p = malloc(sizeof(int));
free(p);
free(p);     // 错误！重复释放
```

Double Free 会破坏堆的内部数据结构，通常导致程序崩溃。

### 4.3 内存泄漏

```c
void func() {
    int *p = malloc(100);
    if (some_condition) {
        return;    // 提前返回，忘记 free(p)！
    }
    free(p);
}
```

每个 `return` 路径都要确保释放了所有已分配的内存。

### 4.4 `realloc` 返回值直接赋给原指针

```c
// 危险
arr = realloc(arr, new_size);
// 如果 realloc 失败返回 NULL，arr 变成 NULL，原内存泄漏

// 安全
int *temp = realloc(arr, new_size);
if (temp == NULL) {
    free(arr);   // 释放原内存
    return 1;
}
arr = temp;
```

---

## 五、`malloc` vs `calloc` vs `realloc` 总结

| 函数 | 参数 | 初始化 | 用途 |
|------|------|--------|------|
| `malloc` | 总字节数 | 不初始化 | 通用分配 |
| `calloc` | 元素个数, 每个元素大小 | 初始化为 0 | 需要清零的数组 |
| `realloc` | 原指针, 新总字节数 | 新增部分不初始化 | 调整已分配内存大小 |

---

## 六、常见错误与排错

### 6.1 `realloc` 后继续使用原指针

❌ 错误示例：
```c
int *arr = malloc(5 * sizeof(int));
int *temp = realloc(arr, 10 * sizeof(int));
if (temp != NULL) {
    arr = temp;
}
// 如果 temp != NULL，后面应该用 arr（已更新）
// 如果 temp == NULL，arr 仍然有效但没扩容成功
```

✅ 正确示例：
```c
int *arr = malloc(5 * sizeof(int));
int *temp = realloc(arr, 10 * sizeof(int));
if (temp == NULL) {
    free(arr);
    return 1;
}
arr = temp;  // 更新指针
```

### 6.2 `calloc` 参数顺序搞反

❌ 错误示例：
```c
int *p = calloc(sizeof(int), 10);  // 虽然结果一样，但语义不对
```

✅ 正确示例：
```c
int *p = calloc(10, sizeof(int));  // 10 个元素，每个 sizeof(int) 字节
```

### 6.3 `free` 后忘记置 NULL

❌ 错误示例：
```c
free(p);
// ... 很多代码 ...
if (p != NULL) {   // p 不是 NULL，但指向的内存已经释放
    *p = 10;       // 危险！
}
```

✅ 正确示例：
```c
free(p);
p = NULL;   // 明确标记为无效
```

---

## 我做得对不对？

用以下程序验证：

```c
#include <stdio.h>
#include <stdlib.h>

int main() {
    // 测试1：calloc 清零
    int *arr1 = calloc(5, sizeof(int));
    if (arr1 == NULL) return 1;
    int all_zero = 1;
    for (int i = 0; i < 5; i++) {
        if (arr1[i] != 0) all_zero = 0;
    }
    printf("测试1：calloc 清零？%s (应为 是)\n", all_zero ? "是" : "否");
    free(arr1);

    // 测试2：realloc 扩容
    int *arr2 = malloc(3 * sizeof(int));
    if (arr2 == NULL) return 1;
    arr2[0] = 10; arr2[1] = 20; arr2[2] = 30;
    int *temp = realloc(arr2, 5 * sizeof(int));
    if (temp == NULL) { free(arr2); return 1; }
    arr2 = temp;
    printf("测试2：扩容后 arr2[0] = %d (应为 10)\n", arr2[0]);
    printf("测试2：扩容后 arr2[2] = %d (应为 30)\n", arr2[2]);
    arr2[3] = 40; arr2[4] = 50;
    printf("测试2：arr2[4] = %d (应为 50)\n", arr2[4]);
    free(arr2);

    // 测试3：realloc 缩小
    int *arr3 = malloc(5 * sizeof(int));
    if (arr3 == NULL) return 1;
    for (int i = 0; i < 5; i++) arr3[i] = i + 1;
    temp = realloc(arr3, 3 * sizeof(int));
    if (temp == NULL) { free(arr3); return 1; }
    arr3 = temp;
    printf("测试3：缩小后 arr3[0] = %d (应为 1)\n", arr3[0]);
    printf("测试3：缩小后 arr3[2] = %d (应为 3)\n", arr3[2]);
    free(arr3);

    return 0;
}
```

编译运行：
```bash
$ gcc -Wall -o test test.c
$ ./test
测试1：calloc 清零？是 (应为 是)
测试2：扩容后 arr2[0] = 10 (应为 10)
测试2：扩容后 arr2[2] = 30 (应为 30)
测试2：arr2[4] = 50 (应为 50)
测试3：缩小后 arr3[0] = 1 (应为 1)
测试3：缩小后 arr3[2] = 3 (应为 3)
```

---

## 不对怎么办？

| 现象 | 可能原因 | 解决 |
|------|----------|------|
| `realloc` 后数据丢失 | `realloc` 返回新地址但没更新指针 | 用 `temp` 接收，成功后再赋给原指针 |
| `realloc` 后程序崩溃 | `realloc` 失败返回 NULL，但直接赋给了原指针 | 先检查返回值再赋值 |
| `calloc` 申请的内存不是全零 | 极罕见，通常是后续代码覆盖了 | 检查 `calloc` 后是否有写操作 |
| `free` 后程序崩溃 | Double Free 或 Use After Free | 检查 `free` 调用次数，`free` 后置 NULL |
| 动态数组扩容后元素丢失 | 扩容时忘了更新 `capacity` 变量 | 确保 `capacity` 和实际分配大小一致 |

---

## 本章小结

| 知识点 | 一句话总结 |
|--------|-----------|
| `calloc` | 申请内存并初始化为 0，参数是（元素个数，元素大小） |
| `realloc` | 调整已分配内存的大小，可能返回新地址 |
| `realloc` 安全用法 | 用临时变量接收返回值，检查后再更新原指针 |
| 动态数组 | 用 `realloc` 实现自动扩容的数组 |
| Use After Free | `free` 后继续使用已释放的内存 |
| Double Free | 对同一块内存调用两次 `free` |
| `free` 后置 NULL | 避免悬空指针导致意外使用 |

---

## 练习题

1. 写一个程序，用 `calloc` 分配一个长度为 10 的 `int` 数组，验证所有元素都是 0，然后释放。

2. 写一个程序，用 `malloc` 分配一个初始容量为 3 的 `int` 数组，用 `realloc` 逐步扩容到 10，每次扩容时打印旧容量和新容量。验证原有数据在扩容后没有丢失。

3. 完善第 30 章练习题中的"动态待办事项列表"，使用 `realloc` 实现自动扩容。每次添加任务时，如果容量不够就自动扩大为原来的 2 倍。

4. （选做）实现一个 `char* read_line(FILE *fp)` 函数，从文件中逐字符读取一行，用 `realloc` 动态扩展缓冲区，直到遇到换行符或 EOF。返回动态分配的字符串，调用者负责 `free`。