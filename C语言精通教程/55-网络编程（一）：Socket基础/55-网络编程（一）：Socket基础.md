# 55 — 网络编程（一）：Socket基础
> - 对应文档版本：C语言精通教程 outline v1
> - 适用环境：Linux/macOS（需POSIX Socket支持），gcc编译器
> - 读者角色：已掌握C语言核心的开发者
> - 预计耗时：新手 60 分钟
> - 前置教程：第50章（错误处理）、第53章（进程控制）
> - 可视化：无

---

## 我在做什么？

到目前为止，我们的程序都运行在一台机器上，只能操作本地文件。但真正的 C 程序大多需要网络通信——Web 服务器、数据库客户端、聊天工具，底层都是通过 **Socket** 收发数据。

Socket 这个英文单词原意是"插座"。就像你把电器插头插入墙上的插座就能通电，程序通过 Socket "插入"网络，就能和其他程序通信。你不需要关心电是怎么从发电厂传到插座的——Socket 屏蔽了底层的网络细节。

本章学习 TCP Socket 编程：写一个服务端和一个客户端，让它们通过网络互相发送消息。最终目标是一个**回显服务器（Echo Server）**——客户端发给它什么，它就回什么。

`*此术语见附录F*`：Socket、套接字。

---

## 55.1 Socket 是什么

```
┌──────────────────────────────────────────────────────────────┐
│                     Socket 通信模型                           │
│                                                              │
│  服务端                          客户端                       │
│  ┌──────────┐                   ┌──────────┐                 │
│  │ socket() │  创建 Socket      │ socket() │                 │
│  └────┬─────┘                   └────┬─────┘                 │
│       │                              │                       │
│  ┌────▼─────┐                        │                       │
│  │ bind()   │  绑定地址和端口         │                       │
│  └────┬─────┘                        │                       │
│       │                              │                       │
│  ┌────▼─────┐                        │                       │
│  │ listen() │  开始监听              │                       │
│  └────┬─────┘                        │                       │
│       │                              │                       │
│  ┌────▼─────┐  三次握手         ┌────▼─────┐                 │
│  │ accept() │◄─────────────────│connect() │                 │
│  └────┬─────┘                   └────┬─────┘                 │
│       │                              │                       │
│  ┌────▼─────┐                   ┌────▼─────┐                 │
│  │ recv()   │◄─────────────────│ send()   │                 │
│  │ send()   │─────────────────►│ recv()   │                 │
│  └────┬─────┘                   └────┬─────┘                 │
│       │                              │                       │
│  ┌────▼─────┐                   ┌────▼─────┐                 │
│  │ close()  │                   │ close()  │                 │
│  └──────────┘                   └──────────┘                 │
└──────────────────────────────────────────────────────────────┘
```

一个 Socket 就是一个通信端点，用 **IP 地址 + 端口号** 唯一标识。类比：
- **IP 地址** = 大楼地址（找到哪台机器）
- **端口号** = 房间号（找到机器上的哪个程序）

---

## 55.2 需要的头文件

```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#include <sys/types.h>   /* 基本系统数据类型 */
#include <sys/socket.h>  /* socket(), bind(), listen(), accept(), connect() */
#include <netinet/in.h>  /* struct sockaddr_in, htons(), htonl() */
#include <arpa/inet.h>   /* inet_pton(), inet_ntop() */
```

---

## 55.3 TCP 服务端：逐步构建

### 第一步：socket() — 创建 Socket

```c
/*
 * socket(域, 类型, 协议)
 * - AF_INET: IPv4 协议族
 * - SOCK_STREAM: TCP（面向连接、可靠）
 * - 0: 自动选择协议（TCP）
 */
int server_fd = socket(AF_INET, SOCK_STREAM, 0);
if (server_fd < 0) {
    perror("socket 创建失败");
    exit(1);
}
```

Socket 类型对比：

| 类型 | 协议 | 特点 |
|------|------|------|
| `SOCK_STREAM` | TCP | 面向连接，可靠，有序，有边界 |
| `SOCK_DGRAM` | UDP | 无连接，不可靠，无序，保留边界 |

### 第二步：bind() — 绑定地址和端口

```c
struct sockaddr_in server_addr;
memset(&server_addr, 0, sizeof(server_addr));

server_addr.sin_family      = AF_INET;          /* IPv4 */
server_addr.sin_addr.s_addr = INADDR_ANY;       /* 监听所有网卡（0.0.0.0） */
server_addr.sin_port        = htons(8080);      /* 端口号，htons 转网络字节序 */

if (bind(server_fd, (struct sockaddr*)&server_addr, sizeof(server_addr)) < 0) {
    perror("bind 失败");
    close(server_fd);
    exit(1);
}
```

**重要**：`htons()` 和 `htonl()` 将主机字节序转换为网络字节序（大端）。不同 CPU 的字节序可能不同，但网络传输统一用大端。

```
htons = Host TO Network Short (16位)
htonl = Host TO Network Long  (32位)
ntohs = Network TO Host Short
ntohl = Network TO Host Long
```

### 第三步：listen() — 开始监听

```c
/*
 * listen(fd, backlog)
 * backlog: 等待连接队列的最大长度
 */
if (listen(server_fd, 5) < 0) {
    perror("listen 失败");
    close(server_fd);
    exit(1);
}
printf("服务器正在监听端口 8080...\n");
```

### 第四步：accept() — 接受连接

```c
struct sockaddr_in client_addr;
socklen_t client_len = sizeof(client_addr);

/*
 * accept() 会阻塞，直到有客户端连接
 * 返回一个新的 socket fd，用于和这个客户端通信
 */
int client_fd = accept(server_fd, (struct sockaddr*)&client_addr, &client_len);
if (client_fd < 0) {
    perror("accept 失败");
    close(server_fd);
    exit(1);
}

/* 获取客户端 IP 地址 */
char client_ip[INET_ADDRSTRLEN];
inet_ntop(AF_INET, &client_addr.sin_addr, client_ip, sizeof(client_ip));
printf("客户端已连接: %s:%d\n", client_ip, ntohs(client_addr.sin_port));
```

**关键理解**：`server_fd` 是"门铃"——用来接受新连接。`client_fd` 是"对讲机"——用来和特定客户端通信。`server_fd` 只有一个，`client_fd` 每个客户端一个。

### 第五步：send() 和 recv() — 收发数据

```c
char buffer[1024];

/* 接收数据 */
ssize_t bytes_received = recv(client_fd, buffer, sizeof(buffer) - 1, 0);
if (bytes_received < 0) {
    perror("recv 失败");
} else if (bytes_received == 0) {
    printf("客户端断开连接\n");
} else {
    buffer[bytes_received] = '\0';  /* 添加字符串结束符 */
    printf("收到: %s\n", buffer);

    /* 发送数据 */
    send(client_fd, buffer, bytes_received, 0);
}
```

### 第六步：close() — 关闭连接

```c
close(client_fd);  /* 关闭客户端连接 */
close(server_fd);  /* 关闭服务器 socket */
```

---

## 55.4 完整的回显服务器

```c
/*
 * echo_server.c —— TCP 回显服务器
 * 编译: gcc -std=c99 -Wall -o echo_server echo_server.c
 * 运行: ./echo_server
 * 然后在另一个终端: telnet localhost 8080
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>

#define PORT 8080
#define BUFFER_SIZE 1024

int main(void) {
    int server_fd, client_fd;
    struct sockaddr_in server_addr, client_addr;
    socklen_t client_len = sizeof(client_addr);
    char buffer[BUFFER_SIZE];

    /* 1. 创建 socket */
    server_fd = socket(AF_INET, SOCK_STREAM, 0);
    if (server_fd < 0) {
        perror("socket 创建失败");
        exit(1);
    }

    /* 允许端口重用（避免 "Address already in use" 错误） */
    int opt = 1;
    setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));

    /* 2. 绑定地址 */
    memset(&server_addr, 0, sizeof(server_addr));
    server_addr.sin_family = AF_INET;
    server_addr.sin_addr.s_addr = INADDR_ANY;
    server_addr.sin_port = htons(PORT);

    if (bind(server_fd, (struct sockaddr*)&server_addr,
             sizeof(server_addr)) < 0) {
        perror("bind 失败");
        close(server_fd);
        exit(1);
    }

    /* 3. 开始监听 */
    if (listen(server_fd, 5) < 0) {
        perror("listen 失败");
        close(server_fd);
        exit(1);
    }

    printf("回显服务器启动，监听端口 %d\n", PORT);
    printf("在另一个终端运行: telnet localhost %d\n", PORT);

    /* 4. 接受连接 */
    client_fd = accept(server_fd, (struct sockaddr*)&client_addr,
                       &client_len);
    if (client_fd < 0) {
        perror("accept 失败");
        close(server_fd);
        exit(1);
    }

    char client_ip[INET_ADDRSTRLEN];
    inet_ntop(AF_INET, &client_addr.sin_addr, client_ip, sizeof(client_ip));
    printf("客户端已连接: %s:%d\n", client_ip, ntohs(client_addr.sin_port));

    /* 5. 回显循环 */
    while (1) {
        memset(buffer, 0, BUFFER_SIZE);
        ssize_t bytes = recv(client_fd, buffer, BUFFER_SIZE - 1, 0);

        if (bytes < 0) {
            perror("recv 失败");
            break;
        } else if (bytes == 0) {
            printf("客户端断开连接\n");
            break;
        }

        buffer[bytes] = '\0';
        printf("收到 %zd 字节: %s", bytes, buffer);

        /* 回显给客户端 */
        if (send(client_fd, buffer, bytes, 0) < 0) {
            perror("send 失败");
            break;
        }
    }

    /* 6. 关闭连接 */
    close(client_fd);
    close(server_fd);
    printf("服务器关闭\n");
    return 0;
}
```

---

## 55.5 TCP 客户端

```c
/*
 * echo_client.c —— TCP 回显客户端
 * 编译: gcc -std=c99 -Wall -o echo_client echo_client.c
 * 运行: ./echo_client
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>

#define PORT 8080
#define BUFFER_SIZE 1024

int main(void) {
    int sock_fd;
    struct sockaddr_in server_addr;
    char buffer[BUFFER_SIZE];

    /* 1. 创建 socket */
    sock_fd = socket(AF_INET, SOCK_STREAM, 0);
    if (sock_fd < 0) {
        perror("socket 创建失败");
        exit(1);
    }

    /* 2. 连接到服务器 */
    memset(&server_addr, 0, sizeof(server_addr));
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(PORT);

    /* 将 IP 地址字符串转换为网络字节序 */
    if (inet_pton(AF_INET, "127.0.0.1", &server_addr.sin_addr) <= 0) {
        perror("无效的地址");
        close(sock_fd);
        exit(1);
    }

    printf("正在连接到服务器...\n");
    if (connect(sock_fd, (struct sockaddr*)&server_addr,
                sizeof(server_addr)) < 0) {
        perror("连接失败");
        close(sock_fd);
        exit(1);
    }
    printf("已连接到服务器！输入消息（输入 quit 退出）:\n");

    /* 3. 通信循环 */
    while (1) {
        printf("> ");
        fflush(stdout);

        if (fgets(buffer, BUFFER_SIZE, stdin) == NULL) {
            break;
        }

        /* 移除末尾换行符以便比较 */
        size_t len = strlen(buffer);
        if (len > 0 && buffer[len - 1] == '\n') {
            buffer[len - 1] = '\0';
            len--;
        }

        if (strcmp(buffer, "quit") == 0) {
            break;
        }

        /* 发送消息（包含换行符） */
        buffer[len] = '\n';
        buffer[len + 1] = '\0';
        if (send(sock_fd, buffer, len + 1, 0) < 0) {
            perror("发送失败");
            break;
        }

        /* 接收回显 */
        memset(buffer, 0, BUFFER_SIZE);
        ssize_t bytes = recv(sock_fd, buffer, BUFFER_SIZE - 1, 0);
        if (bytes <= 0) {
            printf("服务器断开连接\n");
            break;
        }

        buffer[bytes] = '\0';
        printf("回显: %s", buffer);
    }

    close(sock_fd);
    printf("客户端关闭\n");
    return 0;
}
```

---

## 55.6 网络字节序与字节序转换

不同 CPU 架构的字节序不同：

```
数字 0x12345678 在内存中的存储:

大端（Big Endian）—— 网络字节序:
  低地址  →  高地址
  ┌────┬────┬────┬────┐
  │ 12 │ 34 │ 56 │ 78 │  高位字节在低地址
  └────┴────┴────┴────┘

小端（Little Endian）—— x86/ARM:
  低地址  →  高地址
  ┌────┬────┬────┬────┐
  │ 78 │ 56 │ 34 │ 12 │  低位字节在低地址
  └────┴────┴────┴────┘
```

网络传输统一使用大端字节序。转换函数：

```c
#include <arpa/inet.h>

uint16_t htons(uint16_t hostshort);   /* 16位: 主机序 → 网络序 */
uint32_t htonl(uint32_t hostlong);    /* 32位: 主机序 → 网络序 */
uint16_t ntohs(uint16_t netshort);    /* 16位: 网络序 → 主机序 */
uint32_t ntohl(uint32_t netlong);     /* 32位: 网络序 → 主机序 */
```

```c
#include <stdio.h>
#include <arpa/inet.h>

int main(void) {
    uint16_t port = 0x1234;
    uint16_t net_port = htons(port);

    printf("主机字节序端口: 0x%04x\n", port);
    printf("网络字节序端口: 0x%04x\n", net_port);

    /* 验证：转换回主机序 */
    printf("转换回来:        0x%04x\n", ntohs(net_port));

    return 0;
}
```

---

## 55.7 完整代码清单

由于服务端和客户端代码较长，已在 55.4 和 55.5 节完整给出。下面是两者的整合编译说明：

```bash
# 编译服务端
gcc -std=c99 -Wall -o echo_server echo_server.c

# 编译客户端
gcc -std=c99 -Wall -o echo_client echo_client.c

# 终端1：启动服务端
./echo_server

# 终端2：启动客户端
./echo_client

# 或者用 telnet 测试服务端
telnet localhost 8080
```

---

## 我做得对不对？

1. **服务端启动**：看到 "回显服务器启动，监听端口 8080"。
2. **客户端连接**：客户端显示 "已连接到服务器"，服务端显示 "客户端已连接"。
3. **回显功能**：客户端输入 "hello"，服务端收到后回传，客户端显示 "回显: hello"。
4. **多行消息**：多次发送消息，每次都能正确回显。
5. **断开连接**：客户端输入 "quit" 或按 Ctrl+C，服务端显示 "客户端断开连接"。

---

## 不对怎么办？

### 常见Bug 1：Address already in use

```bash
$ ./echo_server
bind 失败: Address already in use
```

原因：上次运行的服务端没有正常关闭，端口仍然被占用。

✅ 解决：
- 使用 `setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR, ...)` 允许端口重用
- 等待约 60 秒让操作系统释放端口（TIME_WAIT 状态）
- 或用 `netstat -tulnp | grep 8080` 找到占用进程并 kill

### 常见Bug 2：忘记 htons() 导致连接失败

```c
/* ❌ 直接用主机字节序设置端口 */
server_addr.sin_port = 8080;  /* 8080 在内存中是 0x1F90 */

/* 如果主机是小端，网络端会收到 0x901F = 36895，不是 8080！ */
```

✅ 始终使用 `htons(PORT)` 设置端口号。

### 常见Bug 3：recv 返回值处理不当

```c
/* ❌ 假设 recv 一次能收到完整消息 */
char buf[1024];
recv(fd, buf, sizeof(buf), 0);
printf("%s\n", buf);  /* buf 可能没有 '\0' 结尾！ */
```

✅ 检查返回值，手动添加 `'\0'`，并处理 `bytes == 0`（连接关闭）和 `bytes < 0`（错误）。

### 常见Bug 4：send 不检查返回值

```c
/* ❌ send 可能只发送了部分数据 */
send(fd, data, large_size, 0);  /* 返回值被忽略 */
```

✅ 检查 `send()` 返回值，必要时循环发送直到全部数据发送完毕。

### 常见Bug 5：客户端和服务端端口不一致

```c
/* ❌ 服务端监听 8080，客户端连接 9090 */
/* 服务端 */
server_addr.sin_port = htons(8080);
/* 客户端 */
server_addr.sin_port = htons(9090);  /* 连不上！ */
```

✅ 确保服务端和客户端使用相同的端口号。

---

## 本章小结

| 要点 | 说明 |
|------|------|
| Socket | 网络通信端点，IP + 端口唯一标识 |
| socket() | 创建 Socket，指定协议族和类型 |
| sockaddr_in | IPv4 地址结构体，包含 IP 和端口 |
| bind() | 将 Socket 绑定到指定地址和端口 |
| listen() | 开始监听连接请求 |
| accept() | 接受客户端连接，返回新的 Socket fd |
| connect() | 客户端连接到服务端 |
| send() / recv() | 发送和接收数据 |
| htons() / htonl() | 主机字节序转网络字节序（大端） |
| ntohs() / ntohl() | 网络字节序转主机字节序 |
| inet_pton() | IP 字符串转二进制 |
| inet_ntop() | 二进制转 IP 字符串 |
| SO_REUSEADDR | 允许端口重用，避免 "Address already in use" |

---

## 练习题

**题1（编程）**：修改回显服务器，使其在回显消息前加上前缀 `[ECHO] `。例如收到 "hello"，返回 `[ECHO] hello`。

**题2（编程）**：写一个简单的 HTTP 客户端：连接到 `example.com` 的 80 端口，发送 `GET / HTTP/1.1\r\nHost: example.com\r\n\r\n`，接收并打印响应头。提示：用 `getaddrinfo()` 解析域名。

**题3（编程）**：写一个文件传输程序：客户端发送文件名，服务端读取该文件内容并发送给客户端。客户端将内容保存为 `<原文件名>.copy`。注意处理大文件分段传输。

**题4（选做）**：实现一个简单的 UDP 回显服务器。注意 UDP 使用 `SOCK_DGRAM`，服务端不需要 `listen()` 和 `accept()`，使用 `recvfrom()` 和 `sendto()` 代替 `recv()` 和 `send()`。

---

> **下一篇预告**：第56章将继续网络编程，学习并发服务器——多进程、多线程、IO多路复用（select/poll/epoll），以及一个简单的聊天服务器。