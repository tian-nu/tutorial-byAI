# 第11章 · HTTP协议（一）

> "TCP解决的是'怎么可靠地传数据'，HTTP解决的是'传什么数据、数据长什么样'。如果说TCP是邮局送信的系统，那HTTP就是信封上写的格式——寄件人、收件人、内容格式。"

## 11.1 HTTP是什么

**HTTP（HyperText Transfer Protocol，超文本传输协议）** 是Web的基石。它跑在TCP之上，定义了客户端（浏览器）和服务端（你写的Spring Boot应用）之间交换数据的格式。

HTTP是**无状态**协议——每个请求都是独立的，服务端不会"记住"上一个请求是谁发的。这就像你在柜台办业务，每次都要重新报名字和身份证号。这个"无状态"问题在第12章通过Cookie和Session解决。

## 11.2 HTTP请求的结构

一个HTTP请求长这样：

```
GET /api/users HTTP/1.1              ← 请求行
Host: example.com                    ← 请求头（Headers）
Accept: application/json
Authorization: Bearer eyJhbGciOi...
User-Agent: Mozilla/5.0

                                     ← 空行分隔
{"page": 1, "size": 10}              ← 请求体（Body，GET请求通常没有）
```

### 请求行三个部分

```
GET         /api/users        HTTP/1.1
│            │                  │
请求方法      请求路径           协议版本
```

| 请求方法 | 含义 | 对应Spring Boot注解 |
|---------|------|-------------------|
| GET | 获取资源 | `@GetMapping` |
| POST | 创建资源 | `@PostMapping` |
| PUT | 更新资源（全量） | `@PutMapping` |
| PATCH | 更新资源（部分） | `@PatchMapping` |
| DELETE | 删除资源 | `@DeleteMapping` |

### 常见请求头

| 请求头 | 含义 | 示例值 |
|--------|------|--------|
| Host | 目标主机 | example.com |
| Content-Type | 请求体的格式 | application/json |
| Accept | 期望的响应格式 | application/json |
| Authorization | 认证信息 | Bearer xxxx |
| User-Agent | 客户端标识 | Mozilla/5.0 |
| Cookie | 携带Cookie数据 | sessionId=abc123 |

## 11.3 HTTP响应的结构

```
HTTP/1.1 200 OK                       ← 状态行
Content-Type: application/json        ← 响应头（Headers）
Content-Length: 72
Set-Cookie: sessionId=abc123

                                      ← 空行分隔
{"id": 1, "name": "张三", "age": 25}   ← 响应体（Body）
```

### 状态行

```
HTTP/1.1        200        OK
│                │          │
协议版本         状态码      状态描述
```

### HTTP状态码分类

| 范围 | 含义 | 你最早遇到的 |
|------|------|------------|
| 1xx | 信息性 | 极少见到 |
| 2xx | 成功 | `200 OK`、`201 Created` |
| 3xx | 重定向 | `301 永久移动`、`302 临时移动` |
| 4xx | 客户端错误 | `400 请求格式错误`、`401 未认证`、`403 禁止`、`404 未找到` |
| 5xx | 服务端错误 | `500 服务器内部错误`、`502 网关错误`、`503 服务不可用` |

每个后端工程师都跟这些状态码是老朋友：

- `200`：一切正常，你好我也好
- `400`：客户端发的东西格式不对
- `401`：没登录就想看需要登录的页面
- `403`：登录了但没权限
- `404`：你访问的接口不存在
- `500`：服务端代码崩了（看日志去！）

## 11.4 Java HttpURLConnection 演示

用Java原生的HTTP客户端发送请求：

```java
import java.io.*;
import java.net.*;

public class HttpDemo {
    public static void main(String[] args) throws Exception {
        // 发送GET请求
        getRequest();

        // 发送POST请求
        postRequest();
    }

    static void getRequest() throws Exception {
        URL url = new URL("https://jsonplaceholder.typicode.com/posts/1");
        HttpURLConnection conn = (HttpURLConnection) url.openConnection();
        conn.setRequestMethod("GET");
        conn.setRequestProperty("Accept", "application/json");

        int status = conn.getResponseCode();
        System.out.println("GET 状态码: " + status);  // 200

        BufferedReader in = new BufferedReader(
            new InputStreamReader(conn.getInputStream()));
        String line;
        StringBuilder response = new StringBuilder();
        while ((line = in.readLine()) != null) {
            response.append(line);
        }
        in.close();

        System.out.println("GET 响应体: " + response.toString());
    }

    static void postRequest() throws Exception {
        URL url = new URL("https://jsonplaceholder.typicode.com/posts");
        HttpURLConnection conn = (HttpURLConnection) url.openConnection();
        conn.setRequestMethod("POST");
        conn.setRequestProperty("Content-Type", "application/json; charset=UTF-8");
        conn.setDoOutput(true);  // 允许写请求体

        // 写请求体
        String jsonBody = "{\"title\":\"foo\",\"body\":\"bar\",\"userId\":1}";
        OutputStream os = conn.getOutputStream();
        os.write(jsonBody.getBytes("UTF-8"));
        os.close();

        int status = conn.getResponseCode();
        System.out.println("POST 状态码: " + status);  // 201 Created

        BufferedReader in = new BufferedReader(
            new InputStreamReader(conn.getInputStream()));
        String line;
        StringBuilder response = new StringBuilder();
        while ((line = in.readLine()) != null) {
            response.append(line);
        }
        in.close();

        System.out.println("POST 响应体: " + response.toString());
    }
}
```

> 💡 `jsonplaceholder.typicode.com` 是一个免费的假数据API，专门用来测试HTTP请求。学第72章Spring Boot入门时会再次遇到它——那时你将不用笨重的HttpURLConnection，而是用更优雅的方式发送请求。

## 11.5 HTTP与Spring Boot的对应关系

你在Spring Boot中写的每一个Controller方法，本质上都是在处理HTTP请求和生成HTTP响应：

```java
@RestController
@RequestMapping("/api/users")
public class UserController {

    @GetMapping("/{id}")                          // 对应 GET /api/users/1
    public User getUser(@PathVariable Long id) {
        return userService.findById(id);
        // Spring Boot自动把返回的User对象序列化为JSON
        // 自动设置 Content-Type: application/json
        // 自动设置状态码 200
    }

    @PostMapping                                // 对应 POST /api/users
    @ResponseStatus(HttpStatus.CREATED)          // 手动指定状态码 201
    public User createUser(@RequestBody User user) {
        // @RequestBody 把请求体中的JSON自动反序列化为User对象
        return userService.create(user);
    }

    @DeleteMapping("/{id}")                     // 对应 DELETE /api/users/1
    @ResponseStatus(HttpStatus.NO_CONTENT)       // 状态码 204
    public void deleteUser(@PathVariable Long id) {
        userService.delete(id);
    }
}
```

> 🤔 想多一点：很多人初学Spring Boot时感觉"太魔法了"——写个 `@GetMapping` 就能处理HTTP请求。但如果你理解了本章讲的HTTP请求/响应结构，就会发现Spring Boot只不过是把这些底层概念做了优雅的封装：`@GetMapping` = HTTP GET方法，`@RequestBody` = 解析请求体JSON，返回对象 = 自动写响应体JSON。**魔法背后是HTTP协议，理解协议才能驾驭魔法。**

---

## 本章小结

| 学了什么 | 一句话说明 |
|----------|-----------|
| HTTP角色 | 跑在TCP之上的应用层协议，定义数据交换格式 |
| 请求结构 | 请求行（方法+路径+版本）+ 请求头 + 请求体 |
| 请求方法 | GET/POST/PUT/PATCH/DELETE，对应Spring Boot注解 |
| 响应结构 | 状态行（版本+状态码+描述）+ 响应头 + 响应体 |
| 状态码 | 2xx成功/3xx重定向/4xx客户端错误/5xx服务端错误 |
| Java HttpClient | HttpURLConnection发送GET/POST请求 |

## 自测题

1. 一个HTTP请求包含哪三个主要部分？请画出GET /api/users的完整请求示例。

2. 下面这些状态码分别意味着什么？哪种情况下你应该去看服务端日志？
   - 200, 201, 400, 401, 403, 404, 500

3. 你在Spring Boot的Controller里写 `@PostMapping("/users")`，客户端发了一个 `GET /users` 请求，会返回什么状态码？为什么？