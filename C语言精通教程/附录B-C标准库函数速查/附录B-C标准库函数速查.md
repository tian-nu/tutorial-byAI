# 附录B — C标准库函数速查
> - 对应文档版本：C语言精通教程 outline v1
> - 适用环境：所有 C 语言环境
> - 读者角色：C 语言开发者
> - 预计耗时：20 分钟浏览
> - 前置教程：无
> - 可视化：无

---

## 我在做什么？

C 标准库是你写 C 程序时最常用的工具箱。本附录按头文件分类，列出最常用的函数，每个附上函数签名、一句话说明和短示例，方便你随时查阅。

---

## B.1 `<stdio.h>` — 标准输入输出

### `printf` — 格式化输出到标准输出

```c
int printf(const char *format, ...);
```

```c
printf("Hello %s, you are %d years old.\n", "Alice", 25);
// 输出: Hello Alice, you are 25 years old.
```

### `scanf` — 格式化输入从标准输入

```c
int scanf(const char *format, ...);
```

```c
int age;
printf("输入年龄: ");
scanf("%d", &age);
```

> **注意**：`scanf` 读取数字后会在缓冲区留下换行符，可能影响后续 `fgets` 调用。

### `fopen` — 打开文件

```c
FILE *fopen(const char *filename, const char *mode);
```

```c
FILE *fp = fopen("data.txt", "r");   // 只读
FILE *fp = fopen("data.txt", "w");   // 只写（覆盖）
FILE *fp = fopen("data.txt", "a");   // 追加
FILE *fp = fopen("data.txt", "rb");  // 二进制读
if (!fp) { perror("打开失败"); }
```

### `fclose` — 关闭文件

```c
int fclose(FILE *stream);
```

```c
fclose(fp);  // 关闭文件，刷新缓冲区
```

### `fread` — 从文件读取二进制数据

```c
size_t fread(void *ptr, size_t size, size_t nmemb, FILE *stream);
```

```c
int buffer[100];
size_t n = fread(buffer, sizeof(int), 100, fp);
printf("读取了 %zu 个整数\n", n);
```

### `fwrite` — 向文件写入二进制数据

```c
size_t fwrite(const void *ptr, size_t size, size_t nmemb, FILE *stream);
```

```c
int data[] = {1, 2, 3, 4, 5};
fwrite(data, sizeof(int), 5, fp);
```

### `fprintf` — 格式化输出到文件

```c
int fprintf(FILE *stream, const char *format, ...);
```

```c
fprintf(fp, "Name: %s, Score: %d\n", "Bob", 95);
```

### `fscanf` — 格式化输入从文件

```c
int fscanf(FILE *stream, const char *format, ...);
```

```c
char name[50]; int score;
fscanf(fp, "%s %d", name, &score);
```

### `fgets` — 从文件读取一行

```c
char *fgets(char *s, int size, FILE *stream);
```

```c
char line[256];
while (fgets(line, sizeof(line), fp)) {
    printf("%s", line);
}
```

### `fputs` — 向文件写入字符串

```c
int fputs(const char *s, FILE *stream);
```

```c
fputs("Hello, World!\n", fp);
```

### `fseek` — 移动文件位置指针

```c
int fseek(FILE *stream, long offset, int whence);
```

```c
fseek(fp, 0, SEEK_SET);  // 移到开头
fseek(fp, 0, SEEK_END);  // 移到末尾
fseek(fp, 10, SEEK_CUR); // 从当前位置向后移 10 字节
```

### `ftell` — 获取当前文件位置

```c
long ftell(FILE *stream);
```

```c
fseek(fp, 0, SEEK_END);
long size = ftell(fp);  // 获取文件大小
printf("文件大小: %ld 字节\n", size);
```

### `perror` — 打印最近一次系统错误描述

```c
void perror(const char *s);
```

```c
FILE *fp = fopen("nonexistent.txt", "r");
if (!fp) {
    perror("错误");  // 输出: 错误: No such file or directory
}
```

### `feof` — 检查是否到达文件末尾

```c
int feof(FILE *stream);
```

```c
while (!feof(fp)) {
    // 读取数据
}
// 注意：feof 在读取失败后才返回 true，应配合 fgets 返回值使用
```

---

## B.2 `<stdlib.h>` — 通用工具

### `malloc` — 分配指定字节的内存（不初始化）

```c
void *malloc(size_t size);
```

```c
int *arr = malloc(100 * sizeof(int));
if (!arr) { /* 处理失败 */ }
// 注意：malloc 分配的内存内容未初始化
```

### `calloc` — 分配内存并初始化为零

```c
void *calloc(size_t nmemb, size_t size);
```

```c
int *arr = calloc(100, sizeof(int));  // 所有元素初始化为 0
if (!arr) { /* 处理失败 */ }
```

### `realloc` — 调整已分配内存的大小

```c
void *realloc(void *ptr, size_t size);
```

```c
int *arr = malloc(10 * sizeof(int));
// ... 需要更多空间
int *new_arr = realloc(arr, 20 * sizeof(int));
if (!new_arr) { free(arr); /* 处理失败 */ }
arr = new_arr;
```

### `free` — 释放已分配的内存

```c
void free(void *ptr);
```

```c
free(arr);
arr = NULL;  // 防止野指针
```

### `atoi` — 字符串转整数

```c
int atoi(const char *nptr);
```

```c
int n = atoi("12345");  // n = 12345
int m = atoi("abc");    // m = 0（转换失败返回 0）
```

### `atof` — 字符串转浮点数

```c
double atof(const char *nptr);
```

```c
double d = atof("3.14");  // d = 3.14
```

### `atol` — 字符串转长整数

```c
long atol(const char *nptr);
```

```c
long l = atol("1000000");
```

### `rand` — 生成伪随机数

```c
int rand(void);
```

```c
int r = rand();  // 0 到 RAND_MAX（至少 32767）
int dice = rand() % 6 + 1;  // 1 到 6
```

### `srand` — 设置随机数种子

```c
void srand(unsigned int seed);
```

```c
#include <time.h>
srand(time(NULL));  // 用当前时间播种
int r = rand();
```

### `qsort` — 快速排序

```c
void qsort(void *base, size_t nmemb, size_t size,
           int (*compar)(const void *, const void *));
```

```c
int compare(const void *a, const void *b) {
    return (*(int*)a - *(int*)b);
}

int arr[] = {5, 2, 9, 1, 7};
qsort(arr, 5, sizeof(int), compare);
// arr = {1, 2, 5, 7, 9}
```

### `exit` — 终止程序

```c
void exit(int status);
```

```c
if (error) {
    fprintf(stderr, "致命错误\n");
    exit(EXIT_FAILURE);  // EXIT_FAILURE = 1
}
// 正常退出用 exit(EXIT_SUCCESS) 或 exit(0)
```

### `system` — 执行系统命令

```c
int system(const char *command);
```

```c
system("ls -la");    // Linux
system("dir");       // Windows
```

### `abs` / `labs` — 取绝对值

```c
int abs(int j);
long labs(long j);
```

```c
int a = abs(-5);    // 5
long l = labs(-100000L);
```

---

## B.3 `<string.h>` — 字符串操作

### `strlen` — 计算字符串长度（不含 `\0`）

```c
size_t strlen(const char *s);
```

```c
size_t len = strlen("Hello");  // len = 5
```

### `strcpy` — 复制字符串（不检查长度）

```c
char *strcpy(char *dest, const char *src);
```

```c
char dest[50];
strcpy(dest, "Hello World");
// 危险：如果 src 比 dest 长，会缓冲区溢出
```

### `strncpy` — 复制指定长度的字符串（较安全）

```c
char *strncpy(char *dest, const char *src, size_t n);
```

```c
char dest[10];
strncpy(dest, "Hello World", sizeof(dest) - 1);
dest[sizeof(dest) - 1] = '\0';  // 手动添加终止符
```

### `strcat` — 拼接字符串（不检查长度）

```c
char *strcat(char *dest, const char *src);
```

```c
char buf[50] = "Hello ";
strcat(buf, "World");
// buf = "Hello World"
// 危险：不检查 dest 是否有足够空间
```

### `strncat` — 拼接指定长度的字符串（较安全）

```c
char *strncat(char *dest, const char *src, size_t n);
```

```c
char buf[20] = "Hello ";
strncat(buf, "Beautiful World", 9);  // 只拼接 "Beautiful"
// buf = "Hello Beautiful"
```

### `strcmp` — 比较两个字符串

```c
int strcmp(const char *s1, const char *s2);
```

```c
if (strcmp("abc", "abc") == 0) printf("相等\n");   // 0
if (strcmp("abc", "abd") < 0)  printf("abc < abd\n"); // 负数
if (strcmp("z", "a") > 0)      printf("z > a\n");     // 正数
```

### `strncmp` — 比较指定长度的字符串

```c
int strncmp(const char *s1, const char *s2, size_t n);
```

```c
if (strncmp("hello123", "hello456", 5) == 0) {
    printf("前 5 个字符相同\n");
}
```

### `strchr` — 查找字符在字符串中首次出现的位置

```c
char *strchr(const char *s, int c);
```

```c
char *pos = strchr("hello world", 'w');
if (pos) printf("'w' 在位置 %ld\n", pos - "hello world");
// 输出: 'w' 在位置 6
```

### `strstr` — 查找子串首次出现的位置

```c
char *strstr(const char *haystack, const char *needle);
```

```c
char *pos = strstr("hello world", "world");
if (pos) printf("找到: %s\n", pos);
// 输出: 找到: world
```

### `strrchr` — 查找字符在字符串中最后出现的位置

```c
char *strrchr(const char *s, int c);
```

```c
char *last = strrchr("/home/user/file.txt", '/');
if (last) printf("文件名: %s\n", last + 1);
// 输出: 文件名: file.txt
```

### `memcpy` — 复制内存块

```c
void *memcpy(void *dest, const void *src, size_t n);
```

```c
int src[] = {1, 2, 3, 4, 5};
int dest[5];
memcpy(dest, src, sizeof(src));
// 注意：memcpy 不处理内存重叠，重叠时用 memmove
```

### `memmove` — 安全复制内存块（支持重叠）

```c
void *memmove(void *dest, const void *src, size_t n);
```

```c
char buf[] = "abcdef";
memmove(buf + 2, buf, 3);  // buf = "ababcf"
// memmove 正确处理了重叠区域
```

### `memset` — 用指定值填充内存

```c
void *memset(void *s, int c, size_t n);
```

```c
int arr[100];
memset(arr, 0, sizeof(arr));  // 全部填充为 0

char buf[50];
memset(buf, 'A', 10);  // 前 10 字节填充为 'A'
buf[10] = '\0';
```

### `memcmp` — 比较内存块

```c
int memcmp(const void *s1, const void *s2, size_t n);
```

```c
int a[] = {1, 2, 3};
int b[] = {1, 2, 4};
if (memcmp(a, b, sizeof(a)) < 0) printf("a < b\n");
```

---

## B.4 `<math.h>` — 数学函数

编译时需加 `-lm` 链接数学库。

### `sqrt` — 平方根

```c
double sqrt(double x);
```

```c
double r = sqrt(16.0);  // r = 4.0
```

### `pow` — 幂运算

```c
double pow(double x, double y);
```

```c
double r = pow(2.0, 10.0);  // r = 1024.0
```

### `sin` / `cos` / `tan` — 三角函数（参数为弧度）

```c
double sin(double x);
double cos(double x);
double tan(double x);
```

```c
double angle = 3.14159 / 2;  // 90 度
double s = sin(angle);  // s ≈ 1.0
```

### `log` / `log10` — 对数

```c
double log(double x);    // 自然对数（以 e 为底）
double log10(double x);  // 以 10 为底
```

```c
double ln = log(2.71828);  // ln ≈ 1.0
double lg = log10(1000);   // lg = 3.0
```

### `ceil` / `floor` — 向上/向下取整

```c
double ceil(double x);
double floor(double x);
```

```c
double c = ceil(3.14);   // c = 4.0
double f = floor(3.99);  // f = 3.0
```

### `fabs` — 浮点数绝对值

```c
double fabs(double x);
```

```c
double a = fabs(-3.14);  // a = 3.14
```

### `round` — 四舍五入（C99）

```c
double round(double x);
```

```c
double r = round(3.49);  // r = 3.0
double s = round(3.50);  // s = 4.0
```

---

## B.5 `<time.h>` — 时间处理

### `time` — 获取当前时间戳（Unix 时间）

```c
time_t time(time_t *tloc);
```

```c
time_t now = time(NULL);
printf("Unix 时间戳: %ld\n", (long)now);
// 输出: Unix 时间戳: 1700000000
```

### `localtime` — 将时间戳转换为本地时间结构体

```c
struct tm *localtime(const time_t *timep);
```

```c
time_t now = time(NULL);
struct tm *t = localtime(&now);
printf("当前时间: %d-%02d-%02d %02d:%02d:%02d\n",
       t->tm_year + 1900, t->tm_mon + 1, t->tm_mday,
       t->tm_hour, t->tm_min, t->tm_sec);
```

### `strftime` — 格式化时间为字符串

```c
size_t strftime(char *s, size_t max, const char *format,
                const struct tm *tm);
```

```c
time_t now = time(NULL);
struct tm *t = localtime(&now);
char buf[64];
strftime(buf, sizeof(buf), "%Y-%m-%d %H:%M:%S", t);
printf("%s\n", buf);  // 输出: 2024-01-15 14:30:00
```

### `difftime` — 计算两个时间戳的差值（秒）

```c
double difftime(time_t time1, time_t time0);
```

```c
time_t start = time(NULL);
// ... 执行一些操作 ...
time_t end = time(NULL);
printf("耗时: %.1f 秒\n", difftime(end, start));
```

### `clock` — 获取 CPU 时间

```c
clock_t clock(void);
```

```c
clock_t start = clock();
// ... 执行操作 ...
clock_t end = clock();
double elapsed = (double)(end - start) / CLOCKS_PER_SEC;
printf("CPU 时间: %.3f 秒\n", elapsed);
```

---

## B.6 `<ctype.h>` — 字符分类和转换

### `isalpha` — 判断是否为字母

```c
int isalpha(int c);
```

```c
if (isalpha('A')) printf("是字母\n");   // 是
if (isalpha('1')) printf("是字母\n");   // 否
```

### `isdigit` — 判断是否为数字

```c
int isdigit(int c);
```

```c
if (isdigit('5')) printf("是数字\n");   // 是
```

### `isalnum` — 判断是否为字母或数字

```c
int isalnum(int c);
```

```c
if (isalnum('A')) printf("字母或数字\n");  // 是
if (isalnum('1')) printf("字母或数字\n");  // 是
if (isalnum('!')) printf("字母或数字\n");  // 否
```

### `isspace` — 判断是否为空白字符

```c
int isspace(int c);
```

```c
if (isspace(' '))  printf("空格\n");    // 是
if (isspace('\t')) printf("制表符\n");  // 是
if (isspace('\n')) printf("换行符\n");  // 是
```

### `islower` / `isupper` — 判断大小写

```c
int islower(int c);
int isupper(int c);
```

```c
if (islower('a')) printf("小写\n");  // 是
if (isupper('Z')) printf("大写\n");  // 是
```

### `tolower` / `toupper` — 大小写转换

```c
int tolower(int c);
int toupper(int c);
```

```c
char lower = tolower('A');  // lower = 'a'
char upper = toupper('z');  // upper = 'Z'
```

### `isxdigit` — 判断是否为十六进制数字

```c
int isxdigit(int c);
```

```c
if (isxdigit('F')) printf("是十六进制数字\n");  // 是
if (isxdigit('G')) printf("是十六进制数字\n");  // 否
```

---

## B.7 三问

1. **`malloc` 和 `calloc` 有什么区别？** `malloc` 不初始化内存（内容随机），更快；`calloc` 将内存初始化为零，更安全但稍慢。`calloc` 的参数是 `(数量, 每个大小)`，`malloc` 是 `(总大小)`。

2. **`strcpy` 和 `strncpy` 应该选哪个？** 永远选 `strncpy`！`strcpy` 不检查目标缓冲区大小，是缓冲区溢出的经典来源。但 `strncpy` 也可能不自动添加 `\0`，需要手动处理。

3. **`fgets` 和 `scanf` 读字符串有什么区别？** `fgets` 读整行（含空格），遇到换行符停止，保留换行符；`scanf("%s", ...)` 读到空白字符就停止，不读空格。推荐用 `fgets` 配合 `sscanf` 解析。

---

## B.8 本章小结

| 头文件 | 核心函数 | 数量 |
|--------|----------|------|
| `<stdio.h>` | printf, scanf, fopen, fclose, fread, fwrite, fgets, fputs, fprintf, fscanf, fseek, ftell, perror | 14 |
| `<stdlib.h>` | malloc, free, calloc, realloc, atoi, atof, rand, srand, qsort, exit, abs, system | 13 |
| `<string.h>` | strlen, strcpy, strncpy, strcat, strncat, strcmp, strncmp, strchr, strstr, memcpy, memset | 11 |
| `<math.h>` | sqrt, pow, sin, cos, log, ceil, floor, fabs, round | 9 |
| `<time.h>` | time, localtime, strftime, difftime, clock | 5 |
| `<ctype.h>` | isalpha, isdigit, isspace, islower, isupper, tolower, toupper | 7 |

---

## B.9 练习题

1. 写一个函数，使用 `fgets` 和 `sscanf` 安全地从文件读取一个整数。
2. 用 `qsort` 对一个字符串数组按字典序排序（提示：`strcmp` 配合 `qsort`）。
3. 用 `ftell` 和 `fseek` 实现一个函数，返回文件的总行数。*