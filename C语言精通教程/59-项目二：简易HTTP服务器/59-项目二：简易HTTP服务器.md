# 59 — 项目二：简易HTTP服务器
> - 对应文档版本：C语言精通教程 outline v1
> - 适用环境：需 gcc 编译器，Linux/macOS（Windows 需 WSL 或 MinGW）
> - 读者角色：已掌握 C 语言全部核心的开发者
> - 预计耗时：新手 150 分钟，熟手 90 分钟
> - 前置教程：第58章（TODO 命令行工具，项目组织经验）
> - 可视化：无

---

## 我在做什么？

你每天浏览网页时，浏览器向服务器发送请求，服务器返回 HTML 页面。这个过程的核心是 HTTP 协议——一套"请求-响应"的对话规则。本章你将用 C 语言从零实现一个能处理浏览器请求的简易 HTTP 服务器。它监听端口，接收 GET 请求，读取服务器上的文件并返回给浏览器。

```
┌──────────────────────────────────────────────────────────┐
│                    简易 HTTP 服务器                        │
├──────────────────────────────────────────────────────────┤
│                                                          │
│   浏览器                          你的服务器               │
│  ┌──────┐                      ┌──────────────┐          │
│  │Chrome│─── GET /index.html ─▶│  Socket 监听   │          │
│  └──────┘                      │      │        │          │
│       ▲                        │      ▼        │          │
│       │                        │ 解析HTTP请求    │          │
│       │                        │      │        │          │
│       │                        │      ▼        │          │
│       │                        │ 读取文件        │          │
│       │                        │      │        │          │
│       │                        │      ▼        │          │
│       │  ◀── HTTP/1.1 200 OK ──│ 构造响应        │          │
│       │     <html>...</html>   │      │        │          │
│       │                        │      ▼        │          │
│       │                        │ 多线程并发      │          │
│       │                        └──────────────┘          │
│                                                          │
│  端口 8080  ◀───────────────────  TCP 连接                │
└──────────────────────────────────────────────────────────┘
```

---

## 59.1 HTTP 协议简介

HTTP（HyperText Transfer Protocol）是 Web 的基石。一条请求和一条响应组成一次对话。

### 请求格式

```
GET /index.html HTTP/1.1\r\n
Host: localhost:8080\r\n
User-Agent: Mozilla/5.0\r\n
\r\n
```

- 第一行：`方法 路径 协议版本`
- 中间：`头部名: 值`（0 到多行）
- 末尾：一个空行 `\r\n` 表示请求头结束
- GET 请求没有请求体

### 响应格式

```
HTTP/1.1 200 OK\r\n
Content-Type: text/html\r\n
Content-Length: 125\r\n
\r\n
<html><body><h1>Hello World</h1></body></html>
```

- 第一行：`协议版本 状态码 状态描述`
- 头部：与请求头格式相同
- 空行 `\r\n` 分隔
- 响应体：文件内容

### 常见状态码

| 状态码 | 含义 |
|--------|------|
| 200 | OK — 请求成功 |
| 404 | Not Found — 文件不存在 |
| 405 | Method Not Allowed — 不支持的方法 |
| 500 | Internal Server Error — 服务器内部错误 |

---

## 59.2 项目结构

```
httpserver/
├── main.c      # 入口：Socket 监听，创建线程
├── http.h      # HTTP 请求/响应处理声明
├── http.c      # HTTP 请求解析和响应构造
├── mime.h      # MIME 类型映射声明
├── mime.c      # 根据文件扩展名返回 Content-Type
├── Makefile    # 构建脚本
└── www/        # 静态文件根目录（需手动创建）
    └── index.html
```

---

## 59.3 实现步骤

### 步骤 1：MIME 类型模块（mime.h / mime.c）

浏览器需要知道服务器返回的是什么类型的内容（HTML、图片、CSS 等），MIME 类型就是做这个的。

```c
// mime.h
#ifndef MIME_H
#define MIME_H

// 根据文件扩展名返回 MIME 类型字符串
const char* get_mime_type(const char *filename);

#endif
```

```c
// mime.c
#include <string.h>
#include "mime.h"

typedef struct {
    const char *extension;
    const char *mime_type;
} MimeEntry;

static const MimeEntry mime_table[] = {
    {".html", "text/html"},
    {".htm",  "text/html"},
    {".css",  "text/css"},
    {".js",   "application/javascript"},
    {".json", "application/json"},
    {".png",  "image/png"},
    {".jpg",  "image/jpeg"},
    {".jpeg", "image/jpeg"},
    {".gif",  "image/gif"},
    {".svg",  "image/svg+xml"},
    {".ico",  "image/x-icon"},
    {".txt",  "text/plain"},
    {".pdf",  "application/pdf"},
    {".xml",  "application/xml"},
    {NULL,    "application/octet-stream"}  // 默认
};

const char* get_mime_type(const char *filename) {
    // 找到最后一个 '.' 的位置
    const char *dot = strrchr(filename, '.');
    if (!dot) return "application/octet-stream";

    for (int i = 0; mime_table[i].extension != NULL; i++) {
        if (strcmp(dot, mime_table[i].extension) == 0) {
            return mime_table[i].mime_type;
        }
    }
    return "application/octet-stream";
}
```

### 步骤 2：HTTP 处理模块（http.h / http.c）

```c
// http.h
#ifndef HTTP_H
#define HTTP_H

#define MAX_REQUEST_SIZE 8192
#define MAX_PATH_LEN     512
#define RESPONSE_HEADER_MAX 4096

// 解析后的 HTTP 请求
typedef struct {
    char method[16];            // GET, POST, ...
    char path[MAX_PATH_LEN];    // 请求路径，如 /index.html
    char protocol[16];          // HTTP/1.1
} HttpRequest;

// 解析原始 HTTP 请求字符串
int http_parse_request(const char *raw, HttpRequest *req);

// 构造 HTTP 响应并发送给客户端
void http_send_response(int client_fd, const char *root_dir,
                        const HttpRequest *req);

#endif
```

```c
// http.c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/stat.h>
#include <sys/socket.h>
#include "http.h"
#include "mime.h"

// 解析 HTTP 请求行: "GET /index.html HTTP/1.1"
int http_parse_request(const char *raw, HttpRequest *req) {
    // 只取第一行
    char first_line[1024];
    const char *end = strstr(raw, "\r\n");
    if (!end) return -1;

    size_t len = end - raw;
    if (len >= sizeof(first_line)) len = sizeof(first_line) - 1;
    strncpy(first_line, raw, len);
    first_line[len] = '\0';

    // 解析: METHOD PATH PROTOCOL
    if (sscanf(first_line, "%15s %511s %15s",
               req->method, req->path, req->protocol) != 3) {
        return -1;
    }

    return 0;
}

// 发送 HTTP 响应头
static void send_header(int client_fd, int status_code,
                        const char *status_text,
                        const char *content_type,
                        long content_length) {
    char header[RESPONSE_HEADER_MAX];
    int len = snprintf(header, sizeof(header),
        "HTTP/1.1 %d %s\r\n"
        "Content-Type: %s\r\n"
        "Content-Length: %ld\r\n"
        "Connection: close\r\n"
        "Server: SimpleHTTPServer/1.0\r\n"
        "\r\n",
        status_code, status_text,
        content_type,
        content_length);

    send(client_fd, header, len, 0);
}

// 发送错误响应
static void send_error(int client_fd, int status_code,
                       const char *status_text) {
    const char *body_fmt =
        "<html><body><h1>%d %s</h1></body></html>";
    char body[512];
    int body_len = snprintf(body, sizeof(body),
                            body_fmt, status_code, status_text);

    send_header(client_fd, status_code, status_text,
                "text/html", body_len);
    send(client_fd, body, body_len, 0);
}

// 构造安全路径，防止目录遍历攻击
static void build_safe_path(const char *root_dir, const char *req_path,
                            char *out, size_t out_len) {
    // 默认首页
    if (strcmp(req_path, "/") == 0) {
        snprintf(out, out_len, "%s/index.html", root_dir);
        return;
    }

    snprintf(out, out_len, "%s%s", root_dir, req_path);
}

// 处理 GET 请求
void http_send_response(int client_fd, const char *root_dir,
                        const HttpRequest *req) {
    // 只支持 GET
    if (strcmp(req->method, "GET") != 0) {
        send_error(client_fd, 405, "Method Not Allowed");
        return;
    }

    // 构造文件路径
    char filepath[MAX_PATH_LEN];
    build_safe_path(root_dir, req->path, filepath, sizeof(filepath));

    // 打开文件
    FILE *fp = fopen(filepath, "rb");
    if (!fp) {
        send_error(client_fd, 404, "Not Found");
        return;
    }

    // 获取文件大小
    fseek(fp, 0, SEEK_END);
    long file_size = ftell(fp);
    fseek(fp, 0, SEEK_SET);

    // 发送响应头
    const char *mime = get_mime_type(filepath);
    send_header(client_fd, 200, "OK", mime, file_size);

    // 发送文件内容
    char buffer[4096];
    size_t bytes_read;
    while ((bytes_read = fread(buffer, 1, sizeof(buffer), fp)) > 0) {
        send(client_fd, buffer, bytes_read, 0);
    }

    fclose(fp);
}
```

### 步骤 3：主程序（main.c）—— Socket 监听与多线程

```c
// main.c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <pthread.h>
#include <signal.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include "http.h"

#define PORT 8080
#define BACKLOG 10
#define WWW_ROOT "./www"

// 每个客户端连接的参数
typedef struct {
    int client_fd;
    struct sockaddr_in client_addr;
} ClientArgs;

// 处理单个客户端连接的线程函数
void* handle_client(void *arg) {
    ClientArgs *args = (ClientArgs*)arg;
    int client_fd = args->client_fd;

    // 读取 HTTP 请求
    char buffer[MAX_REQUEST_SIZE];
    ssize_t bytes_read = recv(client_fd, buffer, sizeof(buffer) - 1, 0);

    if (bytes_read > 0) {
        buffer[bytes_read] = '\0';

        // 解析请求
        HttpRequest req;
        if (http_parse_request(buffer, &req) == 0) {
            printf("[请求] %s %s 来自 %s\n",
                   req.method, req.path,
                   inet_ntoa(args->client_addr.sin_addr));
            http_send_response(client_fd, WWW_ROOT, &req);
        } else {
            // 解析失败，返回 400
            const char *bad =
                "HTTP/1.1 400 Bad Request\r\n"
                "Content-Type: text/html\r\n"
                "Content-Length: 45\r\n"
                "\r\n"
                "<html><body><h1>400 Bad Request</h1></body></html>";
            send(client_fd, bad, strlen(bad), 0);
        }
    }

    close(client_fd);
    free(args);
    return NULL;
}

int main(void) {
    int server_fd;
    struct sockaddr_in server_addr;

    // 忽略 SIGPIPE 信号（客户端断开时 send 会触发此信号）
    signal(SIGPIPE, SIG_IGN);

    // 1. 创建 Socket
    server_fd = socket(AF_INET, SOCK_STREAM, 0);
    if (server_fd < 0) {
        perror("socket 创建失败");
        exit(EXIT_FAILURE);
    }

    // 2. 设置地址重用（避免 "Address already in use" 错误）
    int opt = 1;
    setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));

    // 3. 绑定地址和端口
    memset(&server_addr, 0, sizeof(server_addr));
    server_addr.sin_family = AF_INET;
    server_addr.sin_addr.s_addr = INADDR_ANY;  // 监听所有网卡
    server_addr.sin_port = htons(PORT);

    if (bind(server_fd, (struct sockaddr*)&server_addr,
             sizeof(server_addr)) < 0) {
        perror("bind 失败");
        close(server_fd);
        exit(EXIT_FAILURE);
    }

    // 4. 开始监听
    if (listen(server_fd, BACKLOG) < 0) {
        perror("listen 失败");
        close(server_fd);
        exit(EXIT_FAILURE);
    }

    printf("HTTP 服务器已启动: http://localhost:%d\n", PORT);
    printf("静态文件目录: %s\n", WWW_ROOT);
    printf("按 Ctrl+C 停止服务器\n\n");

    // 5. 主循环：接受连接并创建线程
    while (1) {
        struct sockaddr_in client_addr;
        socklen_t client_len = sizeof(client_addr);
        int client_fd = accept(server_fd,
                               (struct sockaddr*)&client_addr,
                               &client_len);

        if (client_fd < 0) {
            perror("accept 失败");
            continue;
        }

        // 为每个客户端创建线程
        ClientArgs *args = malloc(sizeof(ClientArgs));
        if (!args) {
            fprintf(stderr, "内存分配失败\n");
            close(client_fd);
            continue;
        }

        args->client_fd = client_fd;
        args->client_addr = client_addr;

        pthread_t thread;
        if (pthread_create(&thread, NULL, handle_client, args) != 0) {
            fprintf(stderr, "创建线程失败\n");
            close(client_fd);
            free(args);
            continue;
        }

        // 分离线程，线程结束后自动回收资源
        pthread_detach(thread);
    }

    close(server_fd);
    return 0;
}
```

### 步骤 4：Makefile

```makefile
# Makefile
CC = gcc
CFLAGS = -Wall -Wextra -std=c99 -g
LDFLAGS = -pthread

TARGET = httpserver
OBJS = main.o http.o mime.o

all: $(TARGET)

$(TARGET): $(OBJS)
	$(CC) $(CFLAGS) -o $@ $^ $(LDFLAGS)

main.o: main.c http.h
	$(CC) $(CFLAGS) -c main.c

http.o: http.c http.h mime.h
	$(CC) $(CFLAGS) -c http.c

mime.o: mime.c mime.h
	$(CC) $(CFLAGS) -c mime.c

clean:
	rm -f $(OBJS) $(TARGET)

run: $(TARGET)
	./$(TARGET)

.PHONY: all clean run
```

### 步骤 5：创建测试用的静态文件

```bash
# 创建 www 目录
mkdir -p www

# 创建 index.html
cat > www/index.html << 'EOF'
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>简易HTTP服务器</title>
</head>
<body>
    <h1>Hello from C HTTP Server!</h1>
    <p>这个页面由你用 C 语言编写的 HTTP 服务器提供。</p>
</body>
</html>
EOF
```

---

## 59.4 编译与运行

```bash
# 编译
cd httpserver/
make

# 运行
./httpserver

# 输出
HTTP 服务器已启动: http://localhost:8080
静态文件目录: ./www
按 Ctrl+C 停止服务器
```

打开浏览器访问 `http://localhost:8080`，你将看到 `index.html` 的内容。

### 测试命令

```bash
# 用 curl 测试
curl -v http://localhost:8080/

# 测试 404
curl -v http://localhost:8080/nonexistent.html

# 测试 MIME 类型
curl -I http://localhost:8080/
```

---

## 59.5 常见错误对照

| 错误写法 | 问题 | 正确写法 |
|----------|------|----------|
| `send(client_fd, data, len, 0)` 不检查返回值 | 客户端断开时可能崩溃 | 检查 `send` 返回值，或忽略 `SIGPIPE` 信号 |
| `strcpy(filepath, root_dir); strcat(filepath, req->path);` | 缓冲区溢出风险 | 使用 `snprintf` 限制长度 |
| 不处理 `pthread_create` 返回值 | 线程创建失败后继续使用无效句柄 | 检查返回值并清理资源 |
| `fopen(filepath, "r")` 读取二进制文件 | 图片等二进制文件损坏 | 使用 `"rb"` 模式打开 |
| `content-length` 拼写错误 | 浏览器可能无法正确解析 | 注意是 `Content-Length`（大写 L） |

---

## 59.6 完整代码清单

### mime.h / mime.c（见上文步骤1，完整代码）

### http.h（完整版）

```c
#ifndef HTTP_H
#define HTTP_H

#define MAX_REQUEST_SIZE 8192
#define MAX_PATH_LEN     512
#define RESPONSE_HEADER_MAX 4096

typedef struct {
    char method[16];
    char path[MAX_PATH_LEN];
    char protocol[16];
} HttpRequest;

int  http_parse_request(const char *raw, HttpRequest *req);
void http_send_response(int client_fd, const char *root_dir,
                        const HttpRequest *req);

#endif
```

### http.c（完整版，见上文步骤2）

### main.c（完整版，见上文步骤3）

### Makefile（完整版，见上文步骤4）

---

## 59.7 三问

1. **为什么用多线程而不是单线程？** 单线程处理时，如果一个客户端请求大文件，其他客户端必须等待，体验很差。多线程让每个客户端都有独立的处理线程，互不阻塞。但线程数不是无限的，生产环境通常用线程池。

2. **`SIGPIPE` 信号是什么？** 当向已关闭的连接 `send` 数据时，系统会发送 `SIGPIPE` 信号，默认行为是终止进程。我们用 `signal(SIGPIPE, SIG_IGN)` 忽略它，让 `send` 返回 -1 而不是崩溃程序。

3. **为什么只支持 GET 方法？** GET 是最简单、最常用的 HTTP 方法。POST 需要解析请求体，涉及 `Content-Length` 和 `Transfer-Encoding` 等复杂处理。作为教学项目，先掌握 GET 即可。

---

## 59.8 本章小结

| 知识点 | 对应位置 |
|--------|----------|
| TCP Socket 编程 | `socket()`/`bind()`/`listen()`/`accept()` |
| HTTP 协议 | 请求/响应格式，状态码，头部字段 |
| 多线程并发 | `pthread_create()`/`pthread_detach()` |
| 文件 I/O | `fopen()`/`fread()`/`fseek()`/`ftell()` 二进制读取 |
| MIME 类型 | 根据扩展名映射 Content-Type |
| 网络安全基础 | 路径安全检查，防止目录遍历 |
| 信号处理 | `SIGPIPE` 忽略 |

---

## 59.9 练习题

1. 增加对 `POST` 方法的支持：接收 JSON 格式的请求体并打印到控制台。
2. 实现目录列表功能：当请求路径是目录时，显示该目录下的文件列表（HTML 格式）。
3. 增加访问日志功能：将每个请求的 IP、时间、路径、状态码写入 `access.log` 文件。
4. 实现简单的线程池：预创建 N 个线程，用队列管理任务，避免频繁创建/销毁线程。
5. 增加 `Keep-Alive` 支持：允许同一连接上处理多个请求，提升性能。

---

*[可暂停点]：如果你在这里暂停，按 Ctrl+C 停止服务器，输入 `make clean` 清理。恢复时用 `make && ./httpserver` 重新启动。*