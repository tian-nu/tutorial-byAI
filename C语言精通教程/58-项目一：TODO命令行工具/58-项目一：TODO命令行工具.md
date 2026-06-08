# 58 — 项目一：TODO命令行工具
> - 对应文档版本：C语言精通教程 outline v1
> - 适用环境：需 gcc 编译器，Linux/macOS/Windows(WSL/MinGW)
> - 读者角色：已掌握 C 语言全部核心的开发者
> - 预计耗时：新手 120 分钟，熟手 60 分钟
> - 前置教程：第1-57章（链表、文件读写、命令行参数、Makefile）
> - 可视化：无

---

## 我在做什么？

想象你手里拿着一张白纸和一支笔，你需要写一个程序来管理你的待办事项。这个程序运行在终端里，你可以输入命令来添加任务、查看任务列表、标记任务完成、删除任务。任务数据保存在文件中，程序关闭后下次打开还在。

这就是一个**TODO命令行工具**——也是你学完 C 语言后第一个有实际意义的完整项目。它把之前各章的知识点（结构体、*链表\*此术语见附录F\*、文件读写、命令行参数、Makefile）串联成一个可用的工具。

```
┌──────────────────────────────────────────────────┐
│                   TODO 命令行工具                  │
├──────────────────────────────────────────────────┤
│  用户输入命令                                      │
│    │                                              │
│    ▼                                              │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    │
│  │  解析命令  │───▶│  执行操作  │───▶│ 输出结果   │    │
│  └──────────┘    └──────────┘    └──────────┘    │
│                        │                          │
│                        ▼                          │
│              ┌──────────────────┐                 │
│              │   链表（内存中）   │                 │
│              └──────┬───────────┘                 │
│                     │ 持久化                      │
│                     ▼                             │
│              ┌──────────────────┐                 │
│              │  tasks.txt (磁盘) │                 │
│              └──────────────────┘                 │
└──────────────────────────────────────────────────┘
```

---

## 58.1 需求分析

### 支持的命令

| 命令 | 功能 | 示例 |
|------|------|------|
| `add <描述>` | 添加新任务 | `add 买菜` |
| `list` | 列出所有任务 | `list` |
| `done <ID>` | 标记任务为完成 | `done 3` |
| `delete <ID>` | 删除任务 | `delete 2` |
| `help` | 显示帮助 | `help` |
| `quit` | 退出程序 | `quit` |

### 数据存储格式

任务保存在 `tasks.txt` 文件中，每行一个任务：

```
id|description|status
1|买菜|0
2|写报告|1
3|跑步|0
```

- `status`：`0` 表示未完成，`1` 表示已完成
- `id`：自动递增的整数

---

## 58.2 项目结构

```
todo/
├── main.c      # 入口：命令行交互循环
├── todo.h      # 头文件：结构体定义和函数声明
├── todo.c      # 实现：链表操作和文件读写
└── Makefile    # 构建脚本
```

---

## 58.3 数据结构设计

### 任务结构体

```c
// todo.h - 任务结构体定义
#ifndef TODO_H
#define TODO_H

#define MAX_DESC_LEN 256
#define FILENAME "tasks.txt"

// 单个任务 *此术语见附录F*
typedef struct Task {
    int id;                 // 任务ID（自增）
    char description[MAX_DESC_LEN]; // 任务描述
    int status;             // 0=未完成, 1=已完成
    struct Task *next;      // 指向下一个任务的指针
} Task;

// 任务链表 *此术语见附录F*
typedef struct {
    Task *head;   // 头节点 *此术语见附录F*
    int next_id;  // 下一个可用的任务ID
} TodoList;

#endif
```

### 设计要点

1. 使用单向链表管理任务，动态增长，不限制任务数量。
2. `TodoList` 结构体封装了链表头和下一个 ID，方便全局访问。
3. `next_id` 从文件中读取最大 ID 后 +1，保证 ID 连续不重复。

---

## 58.4 实现步骤

### 步骤 1：链表基本操作（todo.c 前半部分）

**创建和初始化链表**：

```c
// todo.c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "todo.h"

// 初始化空链表
void todolist_init(TodoList *list) {
    list->head = NULL;
    list->next_id = 1;
}
```

**添加任务**——在链表尾部插入新节点：

```c
// 添加任务，返回新任务的ID
int todolist_add(TodoList *list, const char *desc) {
    Task *new_task = malloc(sizeof(Task));
    if (!new_task) {
        fprintf(stderr, "内存分配失败\n");
        return -1;
    }

    new_task->id = list->next_id++;
    strncpy(new_task->description, desc, MAX_DESC_LEN - 1);
    new_task->description[MAX_DESC_LEN - 1] = '\0';
    new_task->status = 0;
    new_task->next = NULL;

    // 插入到链表尾部
    if (list->head == NULL) {
        list->head = new_task;
    } else {
        Task *cur = list->head;
        while (cur->next != NULL) {
            cur = cur->next;
        }
        cur->next = new_task;
    }

    return new_task->id;
}
```

### 步骤 2：查找和删除任务

```c
// 根据ID查找任务（线性查找）
static Task* find_task(TodoList *list, int id) {
    Task *cur = list->head;
    while (cur != NULL) {
        if (cur->id == id) return cur;
        cur = cur->next;
    }
    return NULL;
}

// 标记任务为完成
int todolist_done(TodoList *list, int id) {
    Task *task = find_task(list, id);
    if (!task) return 0;  // 未找到
    task->status = 1;
    return 1;
}

// 删除任务
int todolist_delete(TodoList *list, int id) {
    Task *cur = list->head;
    Task *prev = NULL;

    while (cur != NULL) {
        if (cur->id == id) {
            // 处理链表头节点的情况
            if (prev == NULL) {
                list->head = cur->next;
            } else {
                prev->next = cur->next;
            }
            free(cur);
            return 1;
        }
        prev = cur;
        cur = cur->next;
    }
    return 0;  // 未找到
}

// 列出所有任务
void todolist_print(TodoList *list) {
    if (list->head == NULL) {
        printf("（暂无任务）\n");
        return;
    }

    printf("%-4s %-4s %s\n", "ID", "状态", "描述");
    printf("--------------------------------\n");

    Task *cur = list->head;
    while (cur != NULL) {
        const char *status_str = (cur->status == 1) ? "[✓]" : "[ ]";
        printf("%-4d %-4s %s\n", cur->id, status_str, cur->description);
        cur = cur->next;
    }
}
```

### 步骤 3：文件持久化

```c
// 从文件加载任务
int todolist_load(TodoList *list) {
    FILE *fp = fopen(FILENAME, "r");
    if (!fp) return 0;  // 文件不存在，从空开始

    char line[512];
    int max_id = 0;

    while (fgets(line, sizeof(line), fp)) {
        int id;
        char desc[MAX_DESC_LEN];
        int status;

        // 解析格式：id|description|status
        if (sscanf(line, "%d|%[^|]|%d", &id, desc, &status) == 3) {
            Task *new_task = malloc(sizeof(Task));
            if (!new_task) {
                fclose(fp);
                return -1;
            }
            new_task->id = id;
            strncpy(new_task->description, desc, MAX_DESC_LEN - 1);
            new_task->description[MAX_DESC_LEN - 1] = '\0';
            new_task->status = status;
            new_task->next = NULL;

            // 插入到链表尾部
            if (list->head == NULL) {
                list->head = new_task;
            } else {
                Task *cur = list->head;
                while (cur->next) cur = cur->next;
                cur->next = new_task;
            }

            if (id > max_id) max_id = id;
        }
    }

    fclose(fp);
    list->next_id = max_id + 1;
    return 1;
}

// 保存任务到文件
int todolist_save(TodoList *list) {
    FILE *fp = fopen(FILENAME, "w");
    if (!fp) {
        fprintf(stderr, "无法打开文件 %s 进行写入\n", FILENAME);
        return -1;
    }

    Task *cur = list->head;
    while (cur != NULL) {
        fprintf(fp, "%d|%s|%d\n", cur->id, cur->description, cur->status);
        cur = cur->next;
    }

    fclose(fp);
    return 0;
}
```

### 步骤 4：释放链表内存

```c
// 释放整个链表
void todolist_free(TodoList *list) {
    Task *cur = list->head;
    while (cur != NULL) {
        Task *next = cur->next;
        free(cur);
        cur = next;
    }
    list->head = NULL;
}
```

### 步骤 5：命令行交互（main.c）

```c
// main.c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "todo.h"

// 去掉末尾换行符
static void trim_newline(char *str) {
    size_t len = strlen(str);
    if (len > 0 && str[len - 1] == '\n') {
        str[len - 1] = '\0';
    }
}

// 打印帮助信息
static void print_help(void) {
    printf("TODO 命令行工具 - 命令列表:\n");
    printf("  add <描述>     添加新任务\n");
    printf("  list           列出所有任务\n");
    printf("  done <ID>      标记任务为完成\n");
    printf("  delete <ID>    删除任务\n");
    printf("  help           显示本帮助\n");
    printf("  quit           退出并保存\n");
}

int main(void) {
    TodoList list;
    todolist_init(&list);
    todolist_load(&list);

    char input[512];
    printf("TODO 命令行工具 v1.0（输入 help 查看帮助）\n");

    while (1) {
        printf("\n> ");
        if (!fgets(input, sizeof(input), stdin)) break;
        trim_newline(input);

        // 解析命令
        char cmd[32] = {0};
        char arg[MAX_DESC_LEN] = {0};
        sscanf(input, "%31s %[^\n]", cmd, arg);

        if (strcmp(cmd, "quit") == 0) {
            printf("正在保存...\n");
            todolist_save(&list);
            todolist_free(&list);
            printf("再见！\n");
            break;
        } else if (strcmp(cmd, "help") == 0) {
            print_help();
        } else if (strcmp(cmd, "list") == 0) {
            todolist_print(&list);
        } else if (strcmp(cmd, "add") == 0) {
            if (strlen(arg) == 0) {
                printf("用法: add <描述>\n");
                continue;
            }
            int id = todolist_add(&list, arg);
            if (id > 0) {
                printf("已添加任务 #%d: %s\n", id, arg);
            }
        } else if (strcmp(cmd, "done") == 0) {
            int id = atoi(arg);
            if (id <= 0) {
                printf("用法: done <ID>\n");
                continue;
            }
            if (todolist_done(&list, id)) {
                printf("任务 #%d 已标记为完成\n", id);
            } else {
                printf("未找到任务 #%d\n", id);
            }
        } else if (strcmp(cmd, "delete") == 0) {
            int id = atoi(arg);
            if (id <= 0) {
                printf("用法: delete <ID>\n");
                continue;
            }
            if (todolist_delete(&list, id)) {
                printf("任务 #%d 已删除\n", id);
            } else {
                printf("未找到任务 #%d\n", id);
            }
        } else if (strlen(cmd) > 0) {
            printf("未知命令: %s（输入 help 查看帮助）\n", cmd);
        }
    }

    return 0;
}
```

### 步骤 6：Makefile

```makefile
# Makefile
CC = gcc
CFLAGS = -Wall -Wextra -std=c99 -g

TARGET = todo
OBJS = main.o todo.o

all: $(TARGET)

$(TARGET): $(OBJS)
	$(CC) $(CFLAGS) -o $@ $^

main.o: main.c todo.h
	$(CC) $(CFLAGS) -c main.c

todo.o: todo.c todo.h
	$(CC) $(CFLAGS) -c todo.c

clean:
	rm -f $(OBJS) $(TARGET)

run: $(TARGET)
	./$(TARGET)

.PHONY: all clean run
```

> **Windows 用户注意**：`rm -f` 在 PowerShell 中应替换为 `del /f`，或使用 MinGW/MSYS2 环境。

### 常见错误对照

| 错误写法 | 问题 | 正确写法 |
|----------|------|----------|
| `strcpy(desc, arg)` | 无长度检查，可能缓冲区溢出 | `strncpy(desc, arg, MAX_DESC_LEN - 1); desc[MAX_DESC_LEN - 1] = '\0';` |
| `while (cur);` | 漏写条件更新，死循环 | `while (cur) { cur = cur->next; }` |
| `fgets(line, 512, fp)` | 未检查返回值 | `if (!fgets(...)) break;` |
| 删除节点后未 `free` | 内存泄漏 | ❌ 仅 `prev->next = cur->next;` → ✅ 先更新指针再 `free(cur);` |

---

## 58.5 编译与运行

```bash
# 编译
cd todo/
make

# 运行
./todo

# 运行示例
> add 买菜
已添加任务 #1: 买菜

> add 写报告
已添加任务 #2: 写报告

> list
ID   状态  描述
--------------------------------
1    [ ]  买菜
2    [ ]  写报告

> done 1
任务 #1 已标记为完成

> list
ID   状态  描述
--------------------------------
1    [✓]  买菜
2    [ ]  写报告

> delete 2
任务 #2 已删除

> quit
正在保存...
再见！
```

---

## 58.6 完整代码清单

### todo.h（完整版）

```c
#ifndef TODO_H
#define TODO_H

#define MAX_DESC_LEN 256
#define FILENAME "tasks.txt"

typedef struct Task {
    int id;
    char description[MAX_DESC_LEN];
    int status;          /* 0=未完成, 1=已完成 */
    struct Task *next;
} Task;

typedef struct {
    Task *head;
    int next_id;
} TodoList;

void todolist_init(TodoList *list);
int  todolist_add(TodoList *list, const char *desc);
int  todolist_done(TodoList *list, int id);
int  todolist_delete(TodoList *list, int id);
void todolist_print(TodoList *list);
int  todolist_load(TodoList *list);
int  todolist_save(TodoList *list);
void todolist_free(TodoList *list);

#endif
```

### todo.c（完整版）

```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "todo.h"

void todolist_init(TodoList *list) {
    list->head = NULL;
    list->next_id = 1;
}

static Task* find_task(TodoList *list, int id) {
    Task *cur = list->head;
    while (cur) {
        if (cur->id == id) return cur;
        cur = cur->next;
    }
    return NULL;
}

int todolist_add(TodoList *list, const char *desc) {
    Task *new_task = malloc(sizeof(Task));
    if (!new_task) {
        fprintf(stderr, "内存分配失败\n");
        return -1;
    }

    new_task->id = list->next_id++;
    strncpy(new_task->description, desc, MAX_DESC_LEN - 1);
    new_task->description[MAX_DESC_LEN - 1] = '\0';
    new_task->status = 0;
    new_task->next = NULL;

    if (list->head == NULL) {
        list->head = new_task;
    } else {
        Task *cur = list->head;
        while (cur->next) cur = cur->next;
        cur->next = new_task;
    }

    return new_task->id;
}

int todolist_done(TodoList *list, int id) {
    Task *task = find_task(list, id);
    if (!task) return 0;
    task->status = 1;
    return 1;
}

int todolist_delete(TodoList *list, int id) {
    Task *cur = list->head;
    Task *prev = NULL;

    while (cur) {
        if (cur->id == id) {
            if (prev == NULL)
                list->head = cur->next;
            else
                prev->next = cur->next;
            free(cur);
            return 1;
        }
        prev = cur;
        cur = cur->next;
    }
    return 0;
}

void todolist_print(TodoList *list) {
    if (!list->head) {
        printf("（暂无任务）\n");
        return;
    }

    printf("%-4s %-4s %s\n", "ID", "状态", "描述");
    printf("--------------------------------\n");

    Task *cur = list->head;
    while (cur) {
        printf("%-4d %-4s %s\n",
               cur->id,
               (cur->status == 1) ? "[✓]" : "[ ]",
               cur->description);
        cur = cur->next;
    }
}

int todolist_load(TodoList *list) {
    FILE *fp = fopen(FILENAME, "r");
    if (!fp) return 0;

    char line[512];
    int max_id = 0;

    while (fgets(line, sizeof(line), fp)) {
        int id, status;
        char desc[MAX_DESC_LEN];
        if (sscanf(line, "%d|%[^|]|%d", &id, desc, &status) == 3) {
            Task *new_task = malloc(sizeof(Task));
            if (!new_task) { fclose(fp); return -1; }

            new_task->id = id;
            strncpy(new_task->description, desc, MAX_DESC_LEN - 1);
            new_task->description[MAX_DESC_LEN - 1] = '\0';
            new_task->status = status;
            new_task->next = NULL;

            if (!list->head) {
                list->head = new_task;
            } else {
                Task *cur = list->head;
                while (cur->next) cur = cur->next;
                cur->next = new_task;
            }

            if (id > max_id) max_id = id;
        }
    }

    fclose(fp);
    list->next_id = max_id + 1;
    return 1;
}

int todolist_save(TodoList *list) {
    FILE *fp = fopen(FILENAME, "w");
    if (!fp) {
        fprintf(stderr, "无法打开文件 %s 进行写入\n", FILENAME);
        return -1;
    }

    Task *cur = list->head;
    while (cur) {
        fprintf(fp, "%d|%s|%d\n", cur->id, cur->description, cur->status);
        cur = cur->next;
    }

    fclose(fp);
    return 0;
}

void todolist_free(TodoList *list) {
    Task *cur = list->head;
    while (cur) {
        Task *next = cur->next;
        free(cur);
        cur = next;
    }
    list->head = NULL;
}
```

### main.c（完整版，见上文步骤5）

### Makefile（完整版，见上文步骤6）

---

## 58.7 三问

1. **为什么用链表而不是数组？** 任务数量不固定，链表可以动态扩展。数组需要预设大小，太小放不下，太大浪费内存。如果你已知任务上限（如 1000 个），用数组更简单。

2. **为什么选择 `quit` 时才保存，而不是每次操作都保存？** 减少磁盘写入次数，提高性能。代价是程序崩溃时可能丢失未保存的数据。折中方案：增加 `save` 命令手动保存，或设置定时自动保存。

3. **`fgets` 和 `scanf` 有什么区别？** `fgets` 读一行（含空格），安全可控，需要手动解析；`scanf` 按格式解析，但处理含空格的字符串容易出错。本工具先用 `fgets` 读取整行，再用 `sscanf` 解析——这是推荐组合。

---

## 58.8 本章小结

| 知识点 | 对应位置 |
|--------|----------|
| 结构体定义 | `Task` 结构体，封装任务属性 |
| 链表操作 | 增/删/查/遍历，含头节点特殊处理 |
| 文件读写 | `fopen`/`fgets`/`fprintf`/`fclose`，数据持久化 |
| 命令行解析 | `fgets` + `sscanf`，字符串比较 `strcmp` |
| Makefile | 多文件编译，目标依赖，clean 规则 |
| 内存管理 | `malloc`/`free`，防止内存泄漏 |

---

## 58.9 练习题

1. 增加一个 `clear` 命令，一键清空所有任务（全部删除，并清空文件）。
2. 给 `list` 命令增加参数支持：`list done` 只显示已完成任务，`list todo` 只显示未完成任务。
3. 增加任务优先级字段（高/中/低），修改文件存储格式和 list 显示。
4. 当 `add` 命令检测到与已有任务描述完全相同时，提示"任务已存在"并拒绝添加。
5. 将链表改为双向链表，支持 `swap <ID1> <ID2>` 命令交换两个任务的位置。

---

*[可暂停点]：如果你在这里暂停，输入 `make clean` 清理编译产物。恢复时用 `make && ./todo` 验证项目仍可编译运行。*