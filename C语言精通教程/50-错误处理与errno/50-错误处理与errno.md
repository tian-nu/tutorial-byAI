# 50 — 错误处理与errno
> - 对应文档版本：C语言精通教程 outline v1
> - 适用环境：C99/C11，gcc编译器
> - 读者角色：已掌握C语言核心的开发者
> - 预计耗时：新手 45 分钟
> - 前置教程：第14章（输入输出）、第36-37章（文件操作）
> - 可视化：无

---

## 我在做什么？

在之前的章节中，我们写的程序都假设一切顺利——文件一定能打开，内存一定能分配成功，数据一定符合预期。但真实世界不是这样的。

想象你是一家餐厅的厨师。你让学徒去仓库拿面粉。他有三种方式向你汇报结果：
1. **沉默**：拿了就回来，如果仓库没面粉，他空手回来，你也不问——结果你和面到一半发现没面粉。
2. **大喊大叫**：面粉没了直接尖叫着跑出厨房，整个餐厅停摆。
3. **主动汇报**：回来时告诉你"面粉拿到了"或者"面粉没了，需要你去买"。

C语言的错误处理就是第三种方式：**函数通过返回值告知调用者"我成功了还是失败了"**，调用者检查返回值并决定如何处理。C语言没有异常机制（不会"大喊大叫"），也没有沉默的默认处理——一切取决于你是否主动检查。

`*此术语见附录F*`：errno、错误码、防御性编程。

---

## 50.1 C语言的错误处理哲学

```
┌──────────────────────────────────────────────────────┐
│              C语言错误处理的三层机制                    │
├──────────────────────────────────────────────────────┤
│                                                      │
│  第一层：函数返回值                                   │
│  ┌──────────────────────────────────────────────┐    │
│  │  fopen() 返回 NULL  →  文件打开失败            │    │
│  │  malloc() 返回 NULL  →  内存分配失败           │    │
│  │  printf() 返回负数   →  输出失败               │    │
│  │  大多数函数返回 -1   →  操作失败               │    │
│  └──────────────────────────────────────────────┘    │
│                         ↓                            │
│  第二层：errno 全局变量                               │
│  ┌──────────────────────────────────────────────┐    │
│  │  失败后，系统设置 errno 为具体错误码            │    │
│  │  errno = ENOENT  →  文件不存在                 │    │
│  │  errno = EACCES  →  权限不足                   │    │
│  │  errno = ENOMEM  →  内存不足                   │    │
│  └──────────────────────────────────────────────┘    │
│                         ↓                            │
│  第三层：错误信息输出                                 │
│  ┌──────────────────────────────────────────────┐    │
│  │  perror("提示")     →  输出可读错误信息         │    │
│  │  strerror(errno)    →  返回错误描述字符串       │    │
│  └──────────────────────────────────────────────┘    │
│                                                      │
└──────────────────────────────────────────────────────┘
```

核心原则：**永远不要假设函数调用一定成功，永远检查返回值。**

---

## 50.2 函数返回值：错误处理的第一道防线

### 常见的返回值约定

```c
/*
 * C语言中常见的错误返回值约定：
 *
 * 返回指针的函数：失败返回 NULL
 * 返回整数的函数：失败返回 -1（或负数）
 * 返回 0 表示成功（Unix 风格）
 * 返回非 0 表示成功（部分库函数风格，需要查文档）
 */
```

### 文件操作示例

```c
#include <stdio.h>

int main(void) {
    /* 打开文件 —— 必须检查返回值 */
    FILE *fp = fopen("nonexistent.txt", "r");
    if (fp == NULL) {
        printf("文件打开失败！\n");
        return 1;
    }

    /* 读取文件... */

    fclose(fp);
    return 0;
}
```

### 内存分配示例

```c
#include <stdio.h>
#include <stdlib.h>

int main(void) {
    int *arr = (int*)malloc(1000000000 * sizeof(int));
    if (arr == NULL) {
        printf("内存分配失败！请求的空间太大了。\n");
        return 1;
    }

    /* 使用 arr... */

    free(arr);
    return 0;
}
```

### 用户输入示例

```c
#include <stdio.h>

int main(void) {
    int age;
    printf("请输入年龄: ");
    int result = scanf("%d", &age);

    if (result != 1) {
        printf("输入无效，请输入一个整数。\n");
        return 1;
    }

    printf("你的年龄是: %d\n", age);
    return 0;
}
```

---

## 50.3 errno：系统错误码

当系统调用（或某些库函数）失败时，除了返回 -1 或 NULL 之外，还会设置一个全局变量 `errno`（定义在 `<errno.h>` 中），告诉你**具体是什么原因失败**。

```c
#include <stdio.h>
#include <errno.h>   /* errno 和错误码 */
#include <string.h>  /* strerror() */

int main(void) {
    FILE *fp = fopen("nonexistent.txt", "r");
    if (fp == NULL) {
        printf("fopen 返回了 NULL\n");
        printf("errno = %d\n", errno);
        printf("错误描述: %s\n", strerror(errno));
        return 1;
    }
    fclose(fp);
    return 0;
}
```

运行输出（Linux/macOS）：
```
fopen 返回了 NULL
errno = 2
错误描述: No such file or directory
```

### 常见错误码

| 错误码 | 宏常量 | 含义 |
|--------|--------|------|
| 1 | `EPERM` | 操作不允许（权限不足） |
| 2 | `ENOENT` | 文件或目录不存在 |
| 3 | `ESRCH` | 进程不存在 |
| 4 | `EINTR` | 系统调用被信号中断 |
| 5 | `EIO` | I/O 错误 |
| 9 | `EBADF` | 文件描述符无效 |
| 11 | `EAGAIN` | 资源暂时不可用（稍后重试） |
| 12 | `ENOMEM` | 内存不足 |
| 13 | `EACCES` | 权限不足 |
| 17 | `EEXIST` | 文件已存在 |
| 22 | `EINVAL` | 无效参数 |
| 32 | `EPIPE` | 管道破裂 |

**重要**：`errno` 不会自动清零。一次成功的函数调用不会重置 `errno`。所以只应在**函数返回失败后**读取 `errno`。

```c
/* ❌ 错误：在成功调用后读取 errno 没有意义 */
fopen("existing.txt", "r");  /* 假设成功 */
printf("%d\n", errno);       /* errno 可能是上次失败留下的旧值 */

/* ✅ 正确：只在失败时读取 */
FILE *fp = fopen("file.txt", "r");
if (fp == NULL) {
    printf("errno = %d\n", errno);  /* 此时的 errno 才有效 */
}
```

---

## 50.4 perror()：一行输出错误信息

`perror()` 是输出错误信息最便捷的方式。它接受一个字符串前缀，然后自动拼接上 `errno` 对应的错误描述，输出到 `stderr`。

```c
#include <stdio.h>
#include <errno.h>

int main(void) {
    FILE *fp = fopen("nonexistent.txt", "r");
    if (fp == NULL) {
        perror("fopen 失败");  /* 输出到 stderr */
        return 1;
    }
    fclose(fp);
    return 0;
}
```

输出：
```
fopen 失败: No such file or directory
```

`perror()` 的格式是：`<你传的前缀>: <系统错误描述>\n`。它始终输出到 `stderr`（标准错误流），而不是 `stdout`。这是一个好习惯——错误信息应该和正常输出分开。

---

## 50.5 strerror()：获取错误描述字符串

`perror()` 直接打印，`strerror()` 返回字符串指针，让你可以自由处理：

```c
#include <stdio.h>
#include <errno.h>
#include <string.h>

int main(void) {
    for (int i = 1; i <= 5; i++) {
        printf("errno %d: %s\n", i, strerror(i));
    }
    return 0;
}
```

输出：
```
errno 1: Operation not permitted
errno 2: No such file or directory
errno 3: No such process
errno 4: Interrupted system call
errno 5: Input/output error
```

---

## 50.6 防御性编程：检查每一个返回值

**防御性编程**就是把每一个可能出错的调用都包上检查，而不是假设它一定成功。

```c
/*
 * 防御性编程示例：打开文件、读取内容、写入另一个文件
 * 每一步都检查返回值
 */
#include <stdio.h>
#include <stdlib.h>
#include <errno.h>
#include <string.h>

int copy_file(const char *src_path, const char *dst_path) {
    /* 1. 打开源文件 */
    FILE *src = fopen(src_path, "r");
    if (src == NULL) {
        fprintf(stderr, "无法打开源文件 %s: %s\n",
                src_path, strerror(errno));
        return -1;
    }

    /* 2. 打开目标文件 */
    FILE *dst = fopen(dst_path, "w");
    if (dst == NULL) {
        fprintf(stderr, "无法创建目标文件 %s: %s\n",
                dst_path, strerror(errno));
        fclose(src);  /* 不要忘记关闭已打开的文件 */
        return -1;
    }

    /* 3. 逐字符复制 */
    int ch;
    while ((ch = fgetc(src)) != EOF) {
        if (fputc(ch, dst) == EOF) {
            fprintf(stderr, "写入目标文件失败: %s\n",
                    strerror(errno));
            fclose(src);
            fclose(dst);
            return -1;
        }
    }

    /* 4. 检查读取是否因为错误而终止（而非正常读到文件尾） */
    if (ferror(src)) {
        fprintf(stderr, "读取源文件时出错: %s\n",
                strerror(errno));
        fclose(src);
        fclose(dst);
        return -1;
    }

    /* 5. 关闭文件 */
    fclose(src);
    if (fclose(dst) == EOF) {
        fprintf(stderr, "关闭目标文件时出错: %s\n",
                strerror(errno));
        return -1;
    }

    printf("文件复制成功: %s -> %s\n", src_path, dst_path);
    return 0;
}

int main(void) {
    /* 创建一个测试文件 */
    FILE *test = fopen("test_src.txt", "w");
    if (test == NULL) {
        perror("创建测试文件失败");
        return 1;
    }
    fprintf(test, "Hello, this is a test file.\n");
    fclose(test);

    /* 复制文件 */
    if (copy_file("test_src.txt", "test_dst.txt") != 0) {
        fprintf(stderr, "复制文件失败\n");
        return 1;
    }

    /* 尝试复制一个不存在的文件 */
    printf("\n--- 尝试复制不存在的文件 ---\n");
    if (copy_file("no_such_file.txt", "output.txt") != 0) {
        printf("（预期失败，这是正常行为）\n");
    }

    return 0;
}
```

---

## 50.7 封装：让错误处理更优雅

当代码中充满 `if (xxx == NULL) { ... return -1; }` 时，可读性会下降。一种常见的策略是使用 `goto` 进行统一清理：

```c
#include <stdio.h>
#include <stdlib.h>
#include <errno.h>
#include <string.h>

int process_files(const char *path1, const char *path2, const char *path3) {
    FILE *f1 = NULL;
    FILE *f2 = NULL;
    FILE *f3 = NULL;
    int ret = -1;

    f1 = fopen(path1, "r");
    if (f1 == NULL) {
        fprintf(stderr, "打开 %s 失败: %s\n", path1, strerror(errno));
        goto cleanup;
    }

    f2 = fopen(path2, "r");
    if (f2 == NULL) {
        fprintf(stderr, "打开 %s 失败: %s\n", path2, strerror(errno));
        goto cleanup;
    }

    f3 = fopen(path3, "w");
    if (f3 == NULL) {
        fprintf(stderr, "打开 %s 失败: %s\n", path3, strerror(errno));
        goto cleanup;
    }

    /* 处理文件... */
    printf("三个文件全部打开成功！\n");
    ret = 0;

cleanup:
    if (f1) fclose(f1);
    if (f2) fclose(f2);
    if (f3) fclose(f3);
    return ret;
}

int main(void) {
    /* 创建两个测试文件 */
    FILE *f = fopen("a.txt", "w");
    if (f) { fprintf(f, "A\n"); fclose(f); }
    f = fopen("b.txt", "w");
    if (f) { fprintf(f, "B\n"); fclose(f); }

    /* 成功情况 */
    printf("=== 成功情况 ===\n");
    process_files("a.txt", "b.txt", "c.txt");

    /* 失败情况 */
    printf("\n=== 失败情况 ===\n");
    process_files("a.txt", "x.txt", "c.txt");

    return 0;
}
```

`goto cleanup` 模式在 Linux 内核代码中大量使用，是 C 语言中实现"资源统一释放"的标准做法。注意：`goto` 只能跳转到同一函数内的标签，不能跨函数跳转。

---

## 50.8 完整代码清单

```c
/*
 * error_handling_demo.c —— C语言错误处理完整演示
 * 编译: gcc -std=c99 -Wall -o err_demo error_handling_demo.c
 */

#include <stdio.h>
#include <stdlib.h>
#include <errno.h>
#include <string.h>

/* 打印所有常见 errno 值 */
void print_errno_list(void) {
    printf("常见 errno 错误码:\n");
    printf("  %-3d  %-12s  %s\n", 1,  "EPERM",   strerror(1));
    printf("  %-3d  %-12s  %s\n", 2,  "ENOENT",  strerror(2));
    printf("  %-3d  %-12s  %s\n", 4,  "EINTR",   strerror(4));
    printf("  %-3d  %-12s  %s\n", 9,  "EBADF",   strerror(9));
    printf("  %-3d  %-12s  %s\n", 12, "ENOMEM",  strerror(12));
    printf("  %-3d  %-12s  %s\n", 13, "EACCES",  strerror(13));
    printf("  %-3d  %-12s  %s\n", 22, "EINVAL",  strerror(22));
}

/* 带完整错误处理的安全文件复制 */
int safe_copy(const char *src_path, const char *dst_path) {
    FILE *src = NULL;
    FILE *dst = NULL;
    int ret = -1;

    src = fopen(src_path, "r");
    if (src == NULL) {
        fprintf(stderr, "[错误] 打开源文件 '%s': %s\n",
                src_path, strerror(errno));
        goto cleanup;
    }

    dst = fopen(dst_path, "w");
    if (dst == NULL) {
        fprintf(stderr, "[错误] 创建目标文件 '%s': %s\n",
                dst_path, strerror(errno));
        goto cleanup;
    }

    int ch;
    while ((ch = fgetc(src)) != EOF) {
        if (fputc(ch, dst) == EOF) {
            fprintf(stderr, "[错误] 写入失败: %s\n", strerror(errno));
            goto cleanup;
        }
    }

    if (ferror(src)) {
        fprintf(stderr, "[错误] 读取失败: %s\n", strerror(errno));
        goto cleanup;
    }

    printf("[成功] 复制完成: %s -> %s\n", src_path, dst_path);
    ret = 0;

cleanup:
    if (src) fclose(src);
    if (dst) {
        if (fclose(dst) == EOF) {
            fprintf(stderr, "[警告] 关闭目标文件失败: %s\n",
                    strerror(errno));
            ret = -1;
        }
    }
    return ret;
}

/* 演示 perror() 的用法 */
void demo_perror(void) {
    printf("\n=== perror() 演示 ===\n");
    FILE *fp = fopen("/nonexistent/file.txt", "r");
    if (fp == NULL) {
        perror("尝试打开文件");  /* 自动附加 errno 描述 */
    }
}

/* 演示 scanf 返回值检查 */
void demo_scanf_check(void) {
    printf("\n=== scanf 返回值检查 ===\n");
    int number;
    printf("(模拟输入 'abc' 而不是数字)\n");
    printf("请确保输入一个整数: ");

    int result = scanf("%d", &number);
    if (result == 1) {
        printf("成功读取: %d\n", number);
    } else if (result == 0) {
        printf("输入格式错误，不是整数\n");
        /* 清空输入缓冲区 */
        int c;
        while ((c = getchar()) != '\n' && c != EOF);
    } else {  /* result == EOF */
        printf("输入流已结束\n");
    }
}

int main(void) {
    /* 1. 打印 errno 列表 */
    print_errno_list();

    /* 2. perror 演示 */
    demo_perror();

    /* 3. 创建测试文件并复制 */
    printf("\n=== 文件复制演示 ===\n");
    FILE *f = fopen("test_original.txt", "w");
    if (f == NULL) {
        perror("创建测试文件");
        return 1;
    }
    fprintf(f, "Hello, Error Handling!\n");
    fprintf(f, "Line 2: This is a test.\n");
    fprintf(f, "Line 3: End of file.\n");
    fclose(f);

    safe_copy("test_original.txt", "test_copy.txt");

    /* 4. 尝试复制不存在的文件 */
    printf("\n=== 复制不存在的文件 ===\n");
    safe_copy("no_such_file.txt", "output.txt");

    /* 5. 演示 scanf 检查 */
    demo_scanf_check();

    return 0;
}
```

---

## 我做得对不对？

1. `print_errno_list()` 输出 1, 2, 4, 9, 12, 13, 22 号错误码及其描述。
2. 运行 `perror()` 演示，看到 "尝试打开文件: No such file or directory"。
3. `safe_copy()` 成功复制 `test_original.txt` 到 `test_copy.txt`，文件内容一致。
4. `safe_copy()` 复制不存在的文件时，输出清晰的错误信息而不会崩溃。
5. 输入非整数时，`scanf` 检查能捕获并提示错误。

---

## 不对怎么办？

### 常见Bug 1：忘记检查 fopen 返回值

```c
/* ❌ 不检查返回值，fp 可能是 NULL，后续操作导致段错误 */
FILE *fp = fopen("file.txt", "r");
fprintf(fp, "hello");  /* 如果 fp == NULL，程序崩溃 */
```

✅ 每次打开文件后立即检查 `fp == NULL`。

### 常见Bug 2：在成功操作后读取 errno

```c
/* ❌ fopen 成功后读取 errno 没有意义 */
FILE *fp = fopen("exists.txt", "r");
printf("errno = %d\n", errno);  /* 可能是上次失败残留的值 */
```

✅ 只在函数返回失败后读取 `errno`。

### 常见Bug 3：错误处理中忘记关闭已打开的资源

```c
/* ❌ 第二个 fopen 失败时，第一个文件没有关闭 */
FILE *f1 = fopen("a.txt", "r");
if (f1 == NULL) return -1;
FILE *f2 = fopen("b.txt", "w");
if (f2 == NULL) return -1;  /* f1 泄漏！ */
```

✅ 使用 `goto cleanup` 模式，或立即关闭已打开的文件。

### 常见Bug 4：忘记包含 <errno.h>

```c
/* ❌ 没有 #include <errno.h>，errno 可能被当作未声明标识符 */
if (fp == NULL) {
    printf("errno = %d\n", errno);  /* 编译警告或错误 */
}
```

✅ 在文件开头 `#include <errno.h>`。

### 常见Bug 5：perror 和 printf 混用导致的输出顺序问题

```c
/* ❌ stdout 和 stderr 可能因为缓冲导致输出顺序混乱 */
printf("开始处理...\n");     /* stdout（行缓冲） */
perror("处理失败");           /* stderr（无缓冲） */
```

✅ 错误信息统一用 `fprintf(stderr, ...)` 或 `perror()`，不要和 `printf()` 混用。

---

## 本章小结

| 要点 | 说明 |
|------|------|
| C语言错误处理哲学 | 函数通过返回值报告成功/失败，没有异常机制 |
| 返回值约定 | 指针返回 NULL，整数返回 -1/负数 表示失败 |
| errno | 全局变量，系统调用失败时设置为具体错误码 |
| 常见错误码 | ENOENT(2)、EACCES(13)、ENOMEM(12) 等 |
| perror() | 直接输出"前缀: 错误描述"到 stderr |
| strerror() | 返回错误码对应的字符串描述 |
| 防御性编程 | 检查每一个可能失败的函数调用 |
| goto cleanup | 统一资源释放的 C 语言惯用模式 |
| stderr vs stdout | 错误信息应输出到 stderr，与正常输出分离 |

---

## 练习题

**题1（编程）**：写一个函数 `read_file_safe(const char *path)`，打开文件，读取全部内容到一个动态分配的字符串中，返回该字符串。如果任何一步失败，返回 NULL 并输出清晰的错误信息。注意：调用者负责 `free()` 返回的字符串。

**题2（编程）**：写一个函数 `safe_divide(int a, int b, double *result)`，如果 `b == 0` 返回 -1 并设置 `errno = EINVAL`，否则计算 `a / b` 并通过 `result` 指针返回结果，函数返回 0。

**题3（编程）**：写一个程序，遍历 errno 从 1 到 133（Linux 下最大常见错误码），对每个 errno 输出 `strerror()` 的结果，找出哪些错误码在你的系统上有效。

**题4（选做）**：将 `safe_copy()` 函数改造成一个独立的命令行工具 `mycp`（类似 `cp` 命令），用法为 `./mycp 源文件 目标文件`。要求：检查命令行参数数量，检查源文件是否存在，检查目标文件是否已存在（如果存在则询问是否覆盖）。

---

> **下一篇预告**：第51章将学习命令行参数——`argc` 和 `argv`，以及如何使用 `getopt` 解析带选项的命令行参数。