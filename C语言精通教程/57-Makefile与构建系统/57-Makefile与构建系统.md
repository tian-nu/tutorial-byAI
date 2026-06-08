# 57 — Makefile与构建系统
> - 对应文档版本：C语言精通教程 outline v1
> - 适用环境：Linux/macOS（需make工具），gcc编译器
> - 读者角色：已掌握C语言核心的开发者
> - 预计耗时：新手 45 分钟
> - 前置教程：第40章（多文件项目与头文件）、第41章（编译的四个阶段）
> - 可视化：无

---

## 我在做什么？

到目前为止，我们都是手动输入 `gcc` 命令编译程序。对于一个文件的小项目，这没问题。但真实项目可能有几十上百个源文件，每个文件有不同的编译选项，还有依赖关系——A 文件改了只重新编译 A，B 没改就不用重编。

**Makefile** 就是管理这些编译规则的"施工图纸"。你告诉 `make` 工具：目标文件是什么、依赖哪些源文件、用什么命令生成。`make` 自动判断哪些文件需要重新编译，只编译有变动的部分。

想象你是一个建筑工头。你不用每次都从头建整栋楼，而是看图纸（Makefile），只修补有变化的部分——墙没变就不用重砌，只换掉坏了的窗户。

---

## 57.1 为什么需要 Makefile

### 手动编译的痛点

```bash
# 一个简单的多文件项目
gcc -c main.c -o main.o
gcc -c utils.c -o utils.o
gcc -c network.c -o network.o
gcc -c database.c -o database.o
gcc main.o utils.o network.o database.o -o myapp -lm -lpthread

# 问题：
# 1. 每次修改任何一个文件，都要手动输入以上所有命令
# 2. 改了 utils.c 只需要重编 utils.o 和重新链接，但手动操作容易漏
# 3. 团队成员可能不知道编译选项，导致编译结果不一致
# 4. 清理编译产物（.o 文件）需要手动 rm
```

### Makefile 的解决方案

```makefile
# 只需要一条命令
$ make          # 编译
$ make clean    # 清理
```

---

## 57.2 Makefile 基本语法

### 规则（Rule）

Makefile 的核心是**规则**，每条规则由三部分组成：

```makefile
目标: 依赖
	命令
```

```
┌─────────────────────────────────────────────────┐
│  目标（target）: 依赖（prerequisites）             │
│  <TAB>命令（recipe）                              │
│                                                   │
│  含义：如果目标不存在，或者依赖比目标更新，         │
│        则执行命令来生成目标                        │
└─────────────────────────────────────────────────┘
```

**关键规则**：命令前面必须是 **TAB 字符**，不能用空格！这是 Makefile 最常见的坑。

### 第一个 Makefile

```makefile
# 文件: Makefile
# 这是注释

hello: hello.c
	gcc -std=c99 -Wall -o hello hello.c

# 运行: make
# make 会检查 hello 是否存在，以及 hello.c 是否比 hello 更新
# 如果是，则执行 gcc 命令
```

运行：
```bash
$ make
gcc -std=c99 -Wall -o hello hello.c

$ make       # 再次运行
make: 'hello' is up to date.   # 没有变化，不重新编译

$ touch hello.c   # 模拟修改了源文件
$ make
gcc -std=c99 -Wall -o hello hello.c   # 重新编译了
```

### 多目标 Makefile

```makefile
# 多文件项目
# 项目结构: main.c, utils.c, utils.h

myapp: main.o utils.o
	gcc -std=c99 -Wall -o myapp main.o utils.o

main.o: main.c utils.h
	gcc -std=c99 -Wall -c main.c

utils.o: utils.c utils.h
	gcc -std=c99 -Wall -c utils.c
```

```
myapp 的依赖链:

  main.c ──> main.o ──┐
                       ├──> myapp
  utils.c ──> utils.o ─┘
  utils.h ──> 两者都依赖它
```

当修改 `utils.h` 时，`main.o` 和 `utils.o` 都会重新编译，因为两者都依赖 `utils.h`。

### 默认目标

`make` 不带参数时，执行 Makefile 中的**第一个目标**。通常第一个目标是 `all`：

```makefile
all: myapp

myapp: main.o utils.o
	gcc -std=c99 -Wall -o myapp main.o utils.o

# ...
```

---

## 57.3 变量与自动变量

### 定义和使用变量

```makefile
# 变量定义
CC      = gcc
CFLAGS  = -std=c99 -Wall -g
LDFLAGS = -lm -lpthread
TARGET  = myapp
OBJECTS = main.o utils.o network.o

# 使用变量: $(变量名)
$(TARGET): $(OBJECTS)
	$(CC) $(CFLAGS) -o $(TARGET) $(OBJECTS) $(LDFLAGS)

main.o: main.c utils.h
	$(CC) $(CFLAGS) -c main.c

utils.o: utils.c utils.h
	$(CC) $(CFLAGS) -c utils.c

network.o: network.c network.h
	$(CC) $(CFLAGS) -c network.c
```

### 自动变量

Make 提供了一些自动变量，让你不用重复写目标名和依赖名：

| 自动变量 | 含义 |
|----------|------|
| `$@` | 当前规则的目标文件名 |
| `$<` | 第一个依赖文件名 |
| `$^` | 所有依赖文件名（去重） |
| `$?` | 所有比目标新的依赖文件名 |
| `$*` | 模式规则中匹配的部分（不含后缀） |

```makefile
# 使用自动变量改写
CC      = gcc
CFLAGS  = -std=c99 -Wall -g
TARGET  = myapp
OBJECTS = main.o utils.o

$(TARGET): $(OBJECTS)
	$(CC) $(CFLAGS) -o $@ $^
# $@ = myapp, $^ = main.o utils.o

main.o: main.c utils.h
	$(CC) $(CFLAGS) -c $<
# $< = main.c

utils.o: utils.c utils.h
	$(CC) $(CFLAGS) -c $<
# $< = utils.c
```

---

## 57.4 模式规则与通配符

对于大量类似的编译规则，可以用**模式规则**（Pattern Rule）避免重复：

```makefile
# 模式规则: %.o: %.c
# 含义：任何 .o 文件都依赖于同名的 .c 文件

%.o: %.c
	$(CC) $(CFLAGS) -c $< -o $@

# 这样，main.o 自动依赖 main.c，utils.o 自动依赖 utils.c
# 不需要为每个 .o 单独写规则了
```

### 完整示例

```makefile
CC      = gcc
CFLAGS  = -std=c99 -Wall -g
TARGET  = myapp
SOURCES = $(wildcard *.c)       # 获取所有 .c 文件
OBJECTS = $(SOURCES:.c=.o)      # 把 .c 替换为 .o
DEPS    = $(SOURCES:.c=.d)      # 依赖文件

# 默认目标
all: $(TARGET)

# 链接
$(TARGET): $(OBJECTS)
	$(CC) $(CFLAGS) -o $@ $^

# 模式规则：编译 .c -> .o
%.o: %.c
	$(CC) $(CFLAGS) -c $< -o $@

# 自动生成依赖（GCC 的 -MMD 选项）
%.d: %.c
	$(CC) -MM $< > $@

# 清理
clean:
	rm -f $(TARGET) $(OBJECTS) $(DEPS)

# 声明伪目标
.PHONY: all clean

# 包含依赖文件（如果存在）
-include $(DEPS)
```

### 关键函数

| 函数 | 说明 | 示例 |
|------|------|------|
| `$(wildcard *.c)` | 获取匹配通配符的文件列表 | `main.c utils.c` |
| `$(SOURCES:.c=.o)` | 字符串替换 | `main.o utils.o` |
| `$(shell command)` | 执行 shell 命令 | `$(shell date)` |

---

## 57.5 伪目标（PHONY）

```makefile
# 伪目标：不是真正的文件名，只是一个动作标签
.PHONY: all clean test install

clean:
	rm -f *.o $(TARGET)

test:
	./$(TARGET) --test

install:
	cp $(TARGET) /usr/local/bin/
```

为什么需要 `.PHONY`？如果目录下恰好有一个名叫 `clean` 的文件，`make clean` 就不会执行（因为 `clean` 文件已经"存在"且"最新"）。声明 `.PHONY` 后，`make` 始终执行这个目标。

---

## 57.6 高级特性

### 条件判断

```makefile
# 根据环境选择编译选项
ifeq ($(DEBUG), 1)
    CFLAGS += -g -O0 -DDEBUG
else
    CFLAGS += -O2
endif
```

使用：
```bash
make DEBUG=1          # 调试模式
make                  # 发布模式
```

### 递归 make

```makefile
# 在子目录中调用 make
SUBDIRS = src lib tests

all:
	for dir in $(SUBDIRS); do \
		$(MAKE) -C $$dir; \
	done

clean:
	for dir in $(SUBDIRS); do \
		$(MAKE) -C $$dir clean; \
	done
```

### 静默输出

```makefile
# 在命令前加 @ 可以隐藏命令本身的输出
# 常用于输出更友好的提示信息

$(TARGET): $(OBJECTS)
	@echo "链接 $@..."
	@$(CC) $(CFLAGS) -o $@ $^
	@echo "构建完成: $@"
```

---

## 57.7 通用 Makefile 模板

下面是一个可以直接用于大多数 C 项目的 Makefile 模板：

```makefile
# ============================================================
# 通用 Makefile 模板
# 用法:
#   make          编译项目
#   make clean    清理编译产物
#   make debug    调试模式编译（DEBUG=1）
#   make release  发布模式编译
# ============================================================

# 编译器和选项
CC       = gcc
CFLAGS   = -std=c99 -Wall -Wextra
LDFLAGS  =

# 调试/发布模式
DEBUG    ?= 0
ifeq ($(DEBUG), 1)
    CFLAGS += -g -O0 -DDEBUG
    BUILD_DIR = build/debug
else
    CFLAGS += -O2 -DNDEBUG
    BUILD_DIR = build/release
endif

# 项目信息
TARGET   = $(BUILD_DIR)/myapp
SRC_DIR  = src
INC_DIR  = include

# 自动收集源文件
SOURCES  = $(wildcard $(SRC_DIR)/*.c)
OBJECTS  = $(patsubst $(SRC_DIR)/%.c, $(BUILD_DIR)/%.o, $(SOURCES))
DEPS     = $(OBJECTS:.o=.d)

# 头文件搜索路径
CFLAGS  += -I$(INC_DIR)

# ==================== 目标 ====================

.PHONY: all clean debug release

all: $(TARGET)

debug:
	@$(MAKE) DEBUG=1

release:
	@$(MAKE) DEBUG=0

# 链接
$(TARGET): $(OBJECTS)
	@echo "[LD] $@"
	@mkdir -p $(dir $@)
	@$(CC) $(CFLAGS) -o $@ $^ $(LDFLAGS)

# 编译
$(BUILD_DIR)/%.o: $(SRC_DIR)/%.c
	@echo "[CC] $<"
	@mkdir -p $(dir $@)
	@$(CC) $(CFLAGS) -MMD -c $< -o $@

# 清理
clean:
	@echo "清理编译产物..."
	@rm -rf build

# 运行
run: all
	@./$(TARGET)

# 包含自动生成的依赖文件
-include $(DEPS)
```

### 目录结构示例

```
项目根目录/
├── Makefile
├── src/
│   ├── main.c
│   ├── utils.c
│   └── network.c
├── include/
│   ├── utils.h
│   └── network.h
└── build/
    ├── debug/
    │   ├── main.o
    │   ├── utils.o
    │   └── myapp
    └── release/
        ├── main.o
        ├── utils.o
        └── myapp
```

---

## 57.8 完整示例

创建一个多文件项目，用 Makefile 管理编译：

```bash
# 创建项目结构
mkdir -p make_demo/src make_demo/include
```

**src/main.c**：
```c
#include <stdio.h>
#include "utils.h"
#include "math_utils.h"

int main(void) {
    printf("Hello from Makefile demo!\n");
    printf("add(3, 4) = %d\n", add(3, 4));
    printf("multiply(3, 4) = %d\n", multiply(3, 4));
    return 0;
}
```

**src/utils.c**：
```c
#include "utils.h"

void print_message(const char *msg) {
    printf("%s\n", msg);
}
```

**include/utils.h**：
```c
#ifndef UTILS_H
#define UTILS_H

#include <stdio.h>

void print_message(const char *msg);

#endif
```

**src/math_utils.c**：
```c
#include "math_utils.h"

int add(int a, int b) {
    return a + b;
}

int multiply(int a, int b) {
    return a * b;
}
```

**include/math_utils.h**：
```c
#ifndef MATH_UTILS_H
#define MATH_UTILS_H

int add(int a, int b);
int multiply(int a, int b);

#endif
```

**Makefile**：
```makefile
CC       = gcc
CFLAGS   = -std=c99 -Wall -Wextra -Iinclude
TARGET   = demo
SRC_DIR  = src
OBJ_DIR  = build

SOURCES  = $(wildcard $(SRC_DIR)/*.c)
OBJECTS  = $(patsubst $(SRC_DIR)/%.c, $(OBJ_DIR)/%.o, $(SOURCES))
DEPS     = $(OBJECTS:.o=.d)

.PHONY: all clean

all: $(TARGET)

$(TARGET): $(OBJECTS)
	@echo "[LD] 链接 $@"
	$(CC) $(CFLAGS) -o $@ $^

$(OBJ_DIR)/%.o: $(SRC_DIR)/%.c
	@echo "[CC] 编译 $<"
	@mkdir -p $(OBJ_DIR)
	$(CC) $(CFLAGS) -MMD -c $< -o $@

clean:
	@echo "[CLEAN] 清理"
	rm -rf $(OBJ_DIR) $(TARGET)

-include $(DEPS)
```

运行：
```bash
$ make
[CC] 编译 src/math_utils.c
[CC] 编译 src/utils.c
[CC] 编译 src/main.c
[LD] 链接 demo

$ ./demo
Hello from Makefile demo!
add(3, 4) = 7
multiply(3, 4) = 12

$ make clean
[CLEAN] 清理

$ make
[CC] 编译 src/math_utils.c    # 重新编译
[CC] 编译 src/utils.c
[CC] 编译 src/main.c
[LD] 链接 demo
```

---

## 我做得对不对？

1. **首次 `make`**：所有 `.c` 文件被编译，最后链接生成可执行文件。
2. **再次 `make`**：输出 "nothing to be done" 或类似提示，没有重新编译。
3. **修改一个文件后 `make`**：只有被修改的文件和最终链接重新执行。
4. **`make clean`**：删除所有 `.o` 文件和可执行文件。
5. **`make clean && make`**：重新完整编译。

---

## 不对怎么办？

### 常见Bug 1：命令前用了空格而不是 TAB

```makefile
# ❌ 命令前用了 4 个空格
main.o: main.c
    gcc -c main.c      # 报错: *** missing separator.  Stop.
```

✅ 命令前必须用 **TAB 字符**，不能是空格。大多数编辑器可以显示空白字符（在 VSCode 中按 `Ctrl+Shift+P` → "Toggle Render Whitespace"）。

### 常见Bug 2：变量引用用了圆括号

```makefile
# ❌ make 中变量引用是 $(VAR) 或 ${VAR}，$VAR 只取第一个字符
OBJECTS = main.o utils.o
gcc -o app $OBJECTS    # 展开为 gcc -o app main.o (只取 $O)
```

✅ 使用 `$(OBJECTS)` 或 `${OBJECTS}`。

### 常见Bug 3：make 找不到 Makefile

```bash
$ make
make: *** No targets specified and no makefile found.  Stop.
```

✅ 确保文件名为 `Makefile` 或 `makefile` 或 `GNUmakefile`（区分大小写），且在当前目录。或用 `make -f <文件名>` 指定。

### 常见Bug 4：依赖关系写错导致不重新编译

```makefile
# ❌ main.o 没有声明对 utils.h 的依赖
main.o: main.c         # 缺少 utils.h
	gcc -c main.c

# 改了 utils.h 后 make，main.o 不会被重新编译！
```

✅ 把用到的所有头文件都写入依赖，或用 GCC 的 `-MMD` 选项自动生成。

### 常见Bug 5：clean 目标前面有同名文件

```bash
# 如果目录下有一个叫 clean 的文件
$ make clean
make: 'clean' is up to date.   # 不会执行 clean！
```

✅ 声明 `.PHONY: clean` 解决。

---

## 本章小结

| 要点 | 说明 |
|------|------|
| Makefile | 构建规则文件，描述编译依赖和命令 |
| 规则 | 目标: 依赖 → 命令（TAB 开头） |
| 变量 | `CC`、`CFLAGS`、`LDFLAGS` 等，用 `$(VAR)` 引用 |
| 自动变量 | `$@`(目标)、`$<`(首个依赖)、`$^`(全部依赖) |
| 模式规则 | `%.o: %.c` 匹配所有同名文件 |
| `wildcard` | 获取匹配的文件列表 |
| `patsubst` | 模式替换 |
| `.PHONY` | 声明伪目标，始终执行 |
| `-MMD` | GCC 自动生成头文件依赖 |
| `-include` | 包含文件，不存在时不报错 |
| 条件判断 | `ifeq/ifneq` 根据变量选择编译选项 |

---

## 练习题

**题1（编程）**：为第55章的回显服务器写一个 Makefile。要求：
- 支持 `make`（编译）、`make clean`（清理）、`make run`（编译并运行）
- 使用变量管理编译选项
- 服务端和客户端分别编译为 `echo_server` 和 `echo_client`

**题2（编程）**：创建一个包含 `src/`、`include/`、`lib/`、`tests/` 四个子目录的项目结构。写一个 Makefile，支持：
- 编译 `src/` 下的代码为 `.o` 文件放入 `build/`
- 编译 `tests/` 下的测试代码
- `make test` 运行所有测试
- `make debug` 和 `make release` 两种模式

**题3（编程）**：研究自动依赖生成。用 GCC 的 `-MMD` 和 `-MP` 选项生成 `.d` 依赖文件，并用 `-include` 包含它们。验证：修改头文件后，依赖它的所有 `.c` 文件都会重新编译。

**题4（选做）**：了解 CMake（现代 C/C++ 构建系统）。用 CMake 重写上述项目的构建配置（`CMakeLists.txt`）。比较 Makefile 和 CMake 的语法差异，以及 CMake 的跨平台优势。

---

> **下一篇预告**：第58章将进入实战篇——用 C 语言写一个完整的 TODO 命令行工具，综合运用文件操作、数据结构、命令行参数等知识。