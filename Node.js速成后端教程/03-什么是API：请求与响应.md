# 03-什么是 API：请求与响应

> "上一章你让服务器说出了 'Hello World'，但你和服务器之间到底怎么对话的？这一章我们用餐厅服务员的比喻，把 HTTP 请求和响应的每一个细节拆给你看——URL、方法、状态码、请求头、响应体，一个不落。"

---

## 一、目标与完成效果

**一句话目标**：理解"API"到底是什么，看懂一次 HTTP 请求从发出到返回的全过程，学会用浏览器开发者工具和 Thunder Client 观察请求和响应的每一个细节。

**完成后的可观测效果**：
- 你能用餐厅服务员的比喻，跟完全不懂编程的朋友解释清楚什么是 API。
- 你打开浏览器按 F12，点开 Network 标签，亲眼看到访问 `http://localhost:3000` 时浏览器和服务器之间到底传了什么。
- 你能说出 200、404、500 分别代表什么，以及为什么需要这套状态码体系。
- 你用 Thunder Client 发了人生中第一个 POST 请求。
- 你在 `server.js` 里加了一个新路由 `/api/hello`，返回 JSON 格式的数据。

---

## 二、前置条件

| 序号 | 条件 | 验证命令 |
|------|------|----------|
| 1 | 已完成教程 02，`server.js` 能跑起来 | 浏览器访问 `http://localhost:3000` 返回 "Hello World"（或你的修改） |
| 2 | Express 和 nodemon 已安装 | `ls node_modules/express` 存在 |
| 3 | VS Code 已安装，Thunder Client 插件已装 | VS Code 左侧栏有闪电图标 |
| 4 | 浏览器可用（Chrome/Edge/Firefox 任一） | 能打开任意网页 |

**一条命令确认前置满足**：

```bash
npm run dev
```

终端输出 "Server is running on http://localhost:3000"，前置条件满足。

---

## 三、分步操作

### 步骤 1：API 到底是什么？——餐厅服务员的故事

在上一章，你写了一个后端程序，浏览器访问它就能拿到数据。但你有没有想过：**浏览器和你的 Node.js 程序之间，到底是怎么"对话"的？**

它们说的就是 **API** 这门语言。

#### 比喻：餐厅里的服务员

你去一家餐厅吃饭。流程是这样的：

```
你（顾客）          服务员            厨房（厨师）
   │                 │                  │
   │──"来份宫保鸡丁"──→│                  │
   │                 │──"宫保鸡丁一份！"──→│
   │                 │                  │
   │                 │              （炒菜中...）
   │                 │                  │
   │                 │←──🍲 宫保鸡丁 ────│
   │←──🍲 宫保鸡丁 ────│                  │
```

你**不需要**知道厨房里有什么锅、用什么火候、厨师怎么颠勺。你只需要知道：
1. **你要什么**（宫保鸡丁）
2. **怎么点**（跟服务员说）
3. **你会得到什么**（一盘宫保鸡丁）

**API 就是这个服务员。**

- **你（顾客）= 客户端**（浏览器、手机 App、Postman/Thunder Client，任何一个发请求的程序）
- **厨房（厨师）= 服务器**（你的 `server.js`，它负责"做菜"——处理数据、查数据库、算结果）
- **服务员 = API**（Application Programming Interface，应用程序编程接口）

`API` 这个词拆开看：
- **Application（应用程序）**：你的浏览器是一个程序，你的 Node.js 后端是另一个程序。
- **Programming（编程）**：两个程序之间不是"随便聊聊"，而是按**固定规则**对话。
- **Interface（接口）**：一个"接触面"——你不能直接把手伸进厨房，只能通过服务员这个"接触面"来点菜。

> **所以，你上一章写的 `app.get('/', (req, res) => { res.send('Hello World') })` 本质上就是在说："服务员，当有人点'首页'这道菜时，把 'Hello World' 端上去。"**

---

### 步骤 2：用浏览器 F12 观察一次真实的请求

概念讲完了，我们来看真的。让 `npm run dev` 保持运行。

1. 打开浏览器，访问 `http://localhost:3000`
2. 按 **F12**（或 `Ctrl+Shift+I`）打开开发者工具
3. 点击顶部的 **Network**（网络）标签
4. 现在**刷新页面**（按 F5 或 `Ctrl+R`）

你会看到 Network 面板里出现了一条记录：

```
localhost    200    document
```

> **如果找不到 Network 标签怎么办？**
> - Chrome/Edge：F12 打开后，顶部有一排标签（Elements、Console、Sources、**Network**、...），Network 可能在右侧，点 `>>` 展开就能看到。
> - Firefox：F12 打开后，顶部标签栏直接有 Network。
> - 如果 Network 里是空的：刷新页面之前没打开 F12。打开 F12 后**再刷新一次**，它只会记录打开之后发生的请求。

点击那条记录，右侧会展开详细信息。我们来认一认这些信息——它们就是一次 HTTP 请求-响应的"解剖图"。

---

### 步骤 3：拆解 HTTP 请求——浏览器说了什么？

一次 HTTP 请求就像你给服务员下的一张"点菜单"。它有四个部分：

#### 3.1 URL（统一资源定位符）——你点的是哪道菜

```
http://localhost:3000/
```

拆开看：

| 部分 | 值 | 含义 |
|------|-----|------|
| 协议（scheme） | `http` | 用 HTTP 协议通信（就像餐厅用"普通话"点菜） |
| 主机（host） | `localhost` | 厨房在哪台电脑上（`localhost` = 你自己的电脑） |
| 端口（port） | `3000` | 厨房的哪个窗口（一台电脑可以同时跑很多程序，用端口号区分） |
| 路径（path） | `/` | 点哪道菜（`/` = 首页，`/users` = 用户列表，`/articles/5` = 第 5 号文章） |

**比喻总结**：`http://localhost:3000/` = "用普通话（HTTP），在我自己电脑的 3000 号窗口，点一道叫'首页'的菜。"

#### 3.2 请求方法（Request Method）——你怎么点

在 Network 面板里，你会看到 `GET` 字样。这就是**请求方法**。

常见的请求方法对应餐厅里的动作：

| 方法 | 餐厅比喻 | 含义 |
|------|----------|------|
| **GET** | "给我看看菜单上的这道菜" | 获取数据，不修改任何东西 |
| **POST** | "我要点一道新菜（菜单上没有的）" | 创建新数据 |
| **PUT** | "这道菜换一种做法" | 完整替换已有数据 |
| **DELETE** | "这道菜不要了，退掉" | 删除数据 |

> 你在浏览器地址栏输入网址回车，浏览器发的就是 **GET** 请求。这也是为什么你只能"看"网页，不能用地址栏"删"网页——地址栏只会发 GET。

#### 3.3 请求头（Request Headers）——额外的备注信息

在 Network 面板里往下翻，找到 **Request Headers** 区域。你会看到类似这些：

```
GET / HTTP/1.1
Host: localhost:3000
Connection: keep-alive
Accept: text/html,application/xhtml+xml,...
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) ...
Accept-Encoding: gzip, deflate
Accept-Language: zh-CN,zh;q=0.9
```

**请求头就是点菜时附带的备注**：
- `Host`：告诉服务员"我找的是这个厨房"（一台服务器可能托管多个网站）。
- `Accept`：告诉厨房"我能接受的菜式"（浏览器说：我能吃 HTML 和 JSON）。
- `User-Agent`：告诉厨房"我是谁"（我是 Chrome 浏览器，Windows 系统）。
- `Accept-Language`：告诉厨房"我偏好什么语言"（中文优先）。

#### 3.4 请求体（Request Body）——附带的数据

**GET 请求通常没有请求体。** 就像你问服务员"今天有什么推荐菜？"——你不需要额外递一张纸过去。

POST 和 PUT 请求才会有请求体，里面装着你要提交的数据。

> 🔥 **魔鬼细节**：GET 请求的参数在 URL 里（`?key=value`），POST 请求的参数在 Body 里。这是两者最核心的区别之一。URL 有长度限制（通常 2048 字符左右），Body 没有——所以传大量数据必须用 POST。

---

### 步骤 4：拆解 HTTP 响应——服务器回了什么？

浏览器发完请求后，服务器（你的 `server.js`）处理完，回了一个**响应**。响应有三个部分：

#### 4.1 状态码（Status Code）——"您的菜做好了"还是"厨房没这道菜"

在 Network 面板里，最显眼的就是那个 **200**。这就是状态码——服务器用三个数字告诉你"结果如何"。

| 状态码 | 含义 | 餐厅比喻 |
|--------|------|----------|
| **200** | OK，成功 | "您的菜好了，请慢用！" |
| **201** | Created，创建成功 | "您点的定制菜已经做好了！" |
| **301** | 永久重定向 | "这道菜永久搬到另一桌了" |
| **400** | Bad Request，请求有误 | "您点的'红烧橡皮擦'我们做不了" |
| **401** | Unauthorized，未认证 | "请先出示会员卡" |
| **403** | Forbidden，禁止访问 | "会员卡有效，但你没权限进这个包间" |
| **404** | Not Found，找不到 | "抱歉，菜单上没有这道菜" |
| **500** | Internal Server Error | "厨房着火了！" |

> **记忆口诀**：`2xx` = 成功（你开心），`3xx` = 重定向（你换个地方），`4xx` = 你的错（请求有问题），`5xx` = 我的错（服务器崩了）。

#### 4.2 响应头（Response Headers）——附带的说明

在 Network 面板里找到 **Response Headers**：

```
HTTP/1.1 200 OK
X-Powered-By: Express
Content-Type: text/html; charset=utf-8
Content-Length: 11
ETag: W/"b-Ck1VqNd45QIvq3AZd8XYQLvEhtA"
```

- `X-Powered-By: Express`：告诉浏览器"我是用 Express 框架处理的"。
- `Content-Type: text/html; charset=utf-8`：告诉浏览器"我返回的是 HTML 文本，用 UTF-8 编码"。
- `Content-Length: 11`：返回的数据有 11 个字节（`Hello World` 的长度）。

#### 4.3 响应体（Response Body）——菜本身

在 Network 面板里点击 **Response** 或 **Preview** 标签，你会看到：

```
Hello World
```

这就是响应体——服务器真正返回给你的**数据本身**。前面的状态码、响应头都是"包装"，响应体才是你点的那盘菜。

---

### 🤔 想多一点：为什么需要状态码这套设计？

**如果没有状态码会怎样？**

想象你去餐厅，服务员什么也不说，直接端上来一盘菜。或者更糟——服务员什么也不说，什么也不端，就站在那看着你。你完全不知道：
- 菜做好了没？
- 是不是没这道菜？
- 还是厨房着火了，厨师跑了？

**状态码体系的核心价值**：让程序（而不只是人）能自动判断下一步该做什么。浏览器看到 301 会自动跳转，看到 404 会显示"找不到页面"，看到 500 会显示"服务器错误"。如果所有错误都返回 200 但内容是"呃，出错了"，那程序就没办法自动处理了——它得先读懂人类语言才知道发生了什么。

**这就是 API 设计的核心原则之一：让机器能读懂机器。**

---

### 步骤 5：用 Thunder Client 发请求

浏览器只能发 GET 请求。要发 POST、PUT、DELETE 请求，我们需要一个专门的工具。

#### 5.1 打开 Thunder Client

在 VS Code 中，点击左侧活动栏的**闪电图标**（Thunder Client）。如果没有这个图标，说明插件没装——回到 [01-环境搭建](01-环境搭建.md) 步骤 5。

点击后，你会看到 Thunder Client 的界面。顶部有一个输入框（URL 栏）和下拉菜单（选择请求方法）。

#### 5.2 发一个 GET 请求

1. 方法选择 **GET**
2. URL 输入：`http://localhost:3000`
3. 点击 **Send** 按钮

你会看到：
- **Status: 200 OK**（绿色）
- **Response** 标签下显示：`Hello World`
- **Headers** 标签下能看到和 F12 类似的请求头和响应头

> Thunder Client 本质上就是一个"不带界面的浏览器"——它不会渲染 HTML，只展示服务器返回的原始数据。对于测试 API 来说，这正是我们想要的。

---

### 步骤 6：在 server.js 中添加新路由——返回 JSON

到目前为止，你的接口返回的都是纯文本（`res.send('Hello World')`）。但真正的 API 返回的是 **JSON 格式的数据**。

#### 6.1 什么是 JSON？

JSON（JavaScript Object Notation）是一种用纯文本表示数据结构的格式。它和 JavaScript 的对象语法几乎一模一样：

```json
{
  "message": "Hello API",
  "status": "ok",
  "timestamp": "2026-06-12"
}
```

> JSON 的名字里有 "JavaScript"，但所有编程语言都能读写 JSON——Python、Java、Go、C# 都内置了 JSON 解析器。JSON 是前后端通信的"通用语言"。

#### 6.2 用 res.json() 返回 JSON

打开 `server.js`，在现有代码后面添加一个新路由：

```javascript
// 新增：一个返回 JSON 的 API 接口
app.get('/api/hello', (req, res) => {
    res.json({ message: 'Hello API' });
});
```

修改后的完整 `server.js`：

```javascript
const express = require('express');
const app = express();

app.get('/', (req, res) => {
    res.send('你好，世界！');
});

// 新增：返回 JSON 的 API 接口
app.get('/api/hello', (req, res) => {
    res.json({ message: 'Hello API' });
});

app.listen(3000, () => {
    console.log('Server is running on http://localhost:3000');
});
```

保存文件。nodemon 会自动重启服务器。

#### 6.3 验证

用 Thunder Client：
- 方法：**GET**
- URL：`http://localhost:3000/api/hello`
- 点击 **Send**

你应该看到：

```json
{
  "message": "Hello API"
}
```

同时查看 **Headers** 标签，其中的 **Response Headers** 里会有一行：

```
Content-Type: application/json; charset=utf-8
```

> 🔥 **魔鬼细节**：`res.json()` 自动做了两件事——① 把 JavaScript 对象转成 JSON 字符串 ② 设置响应头 `Content-Type: application/json`。你什么都不用管，Express 帮你全搞定。

#### 6.4 res.send() vs res.json() 的区别

| 方法 | 用途 | Content-Type | 何时用 |
|------|------|-------------|--------|
| `res.send('Hello World')` | 发送任意内容 | 自动判断（通常是 `text/html`） | 返回纯文本或 HTML |
| `res.json({...})` | 发送 JSON 数据 | `application/json` | **返回 API 数据（绝大多数情况用这个）** |

> 实际上，如果你 `res.send({ message: 'Hello' })`（传一个对象），Express 也会自动把它转成 JSON 并设置正确的 Content-Type。但明确用 `res.json()` 更清晰——它明确告诉读代码的人："这个接口返回的是 JSON 数据"。

---

### 步骤 7：状态码速查——一张表搞定

| 状态码 | 英文名 | 含义 | 餐厅比喻 | 你会遇到的场景 |
|--------|--------|------|----------|----------------|
| **200** | OK | 请求成功 | "您的菜好了！" | 正常访问任何页面 |
| **201** | Created | 创建成功 | "您定制的新菜已加入菜单！" | 用 POST 创建了一篇文章 |
| **301** | Moved Permanently | 永久重定向 | "这道菜永久搬到隔壁桌了" | 网站换域名 |
| **400** | Bad Request | 请求有误 | "您点的'红烧橡皮擦'我们做不了" | 你传了错误格式的数据 |
| **401** | Unauthorized | 未认证 | "请先出示会员卡" | 没登录就去访问需要登录的接口 |
| **404** | Not Found | 资源不存在 | "抱歉，菜单上没有这道菜" | 访问了一个不存在的路径 |
| **500** | Internal Server Error | 服务器内部错误 | "厨房着火了！" | 你的代码里有 bug，崩溃了 |

---

## 四、完整代码清单

### `blog-backend/server.js`（本章最终状态）

```javascript
const express = require('express');
const app = express();

app.get('/', (req, res) => {
    res.send('你好，世界！');
});

app.get('/api/hello', (req, res) => {
    res.json({ message: 'Hello API' });
});

app.listen(3000, () => {
    console.log('Server is running on http://localhost:3000');
});
```

---

## 五、验证方法

| 序号 | 操作 | 预期结果 |
|------|------|----------|
| 1 | 浏览器访问 `http://localhost:3000` | 显示 "你好，世界！" |
| 2 | Thunder Client 发 GET `http://localhost:3000/api/hello` | Status 200，Response 显示 `{"message":"Hello API"}` |
| 3 | F12 → Network → 刷新 `http://localhost:3000` | 能看到一条记录，Status 200，Type document |
| 4 | 点击该记录查看 Headers | 能看到 Request Headers 和 Response Headers |
| 5 | 浏览器访问 `http://localhost:3000/nonexistent` | 浏览器可能显示空白或 "Cannot GET /nonexistent"（这是 Express 默认的 404 处理） |

全部通过？你已经理解了 HTTP 请求和响应的基本原理。

---

## 六、小结表格

| 学到的东西 | 一句话解释 |
|-----------|-----------|
| API 是什么 | 客户端（浏览器）和服务器（你的 Node.js 程序）之间的"服务员"——传话、端菜、反馈结果 |
| HTTP 请求的四个部分 | URL（点哪道菜）+ 方法（怎么点）+ 头部（备注）+ 体（附带数据） |
| HTTP 响应的三个部分 | 状态码（做没做成）+ 响应头（额外说明）+ 响应体（菜本身） |
| HTTP 方法 | GET 获取 / POST 创建 / PUT 替换 / DELETE 删除 |
| 常见状态码 | 200 成功 / 400 你错了 / 404 找不到 / 500 服务器崩了 |
| 浏览器 F12 Network | 能看到每一次请求的完整"解剖图"——请求头、响应头、状态码、响应体 |
| Thunder Client | VS Code 内置的 API 测试工具，能发任意类型的 HTTP 请求 |
| `res.json()` | 返回 JSON 数据，自动设置 `Content-Type: application/json` |
| JSON | 前后端通信的"通用语言"——用花括号和方括号表示数据结构 |

---

## 七、术语附录

| 术语 | 英文 | 通俗解释 | 本章出现位置 | 字面陷阱 |
|------|------|----------|-------------|----------|
| HTTP 方法 | HTTP Method | 告诉服务器"你要做什么"的动词：GET（看）、POST（创建）、PUT（改）、DELETE（删）。也叫"HTTP 动词"。 | 步骤 3.2 | "方法"不是编程语言里的 function/method，而是"动作类型"。 |
| 请求（Request） | Request | 客户端发给服务器的完整消息，包含方法、URL、头部和可选的 Body。 | 步骤 3 | 口语中"发请求"= 浏览器/App 找服务器要数据。 |
| 响应（Response） | Response | 服务器返回给客户端的完整消息，包含状态码、头部和 Body。 | 步骤 4 | 口语中"返回响应"= 服务器给浏览器/App 回数据。 |
| 状态码 | Status Code | 一个三位数字，告诉客户端"结果如何"。2xx 成功、3xx 重定向、4xx 客户端错误、5xx 服务器错误。 | 步骤 4.1 | "200"不是"两百块钱"，是"一切 OK"的意思。 |
| 请求头（Headers） | Request Headers | 请求附带的元信息（metadata）——"我是谁、我能接受什么格式、我想要什么语言"。 | 步骤 3.3 | "头"不是"开头"，是"附加说明信息"的集合。 |
| 请求体（Body） | Request Body | 请求中附带的实际数据。GET 请求通常没有 Body，POST/PUT 才有。 | 步骤 3.4 | "身体"不是"网页主体"，是请求中携带的核心数据部分。 |
| JSON | JavaScript Object Notation | 一种用纯文本表示数据结构的格式。所有编程语言都能读写，是前后端通信的"通用语言"。 | 步骤 6.1 | 名字里有 "JavaScript"，但跟 JS 语言本身没有绑定关系——任何语言都能用 JSON。 |
| Content-Type | — | 响应头中的一个字段，告诉客户端"我返回的数据是什么格式"（`text/html`、`application/json`等）。 | 步骤 6.3 | 不是"内容类型"的字面翻译——它其实是"MIME 类型"（Multipurpose Internet Mail Extensions），一个历史遗留名词。 |

---

## 八、已知坑点与禁止事项

1. **F12 Network 空白**：打开 Network 标签后什么都看不到，是因为在打开 F12 **之前**发起的请求不会被记录。**打开 F12 后再刷新页面**。

2. **GET 请求的参数在 URL 里，POST 在 Body 里**：这是初学者最容易搞混的点。在地址栏里输入网址就是 GET 请求，参数通过 `?key=value` 附加在 URL 后面。POST 的数据藏在请求体里，地址栏看不到。

3. **`res.json()` 自动设置 Content-Type**：不需要（也不应该）手动设置 `Content-Type: application/json`。Express 的 `res.json()` 已经帮你做了。手动设置可能导致重复设置。

4. **Thunder Client 第一次用找不到**：确认插件已安装。如果左侧栏没有闪电图标，右键左侧栏空白处，勾选 Thunder Client。

5. **不要用 `res.send()` 返回对象**：虽然 Express 会"智能"处理，但 `res.json()` 语义更明确。养成习惯：返回 JSON 数据用 `res.json()`。

---

## 九、下一步建议

你已经理解了 HTTP 的基本原理，也能用 Thunder Client 测试接口了。但现在的代码全挤在一个 `server.js` 里。接下来：

- **下一章**：[04-模块系统：require与文件拆分](04-模块系统：require与文件拆分.md)——学会用 `require` 和 `module.exports` 把代码拆到多个文件，让项目结构清晰起来。
- **延伸阅读**：好奇 GET 和 POST 之外还有什么 HTTP 方法？PATCH、HEAD、OPTIONS 是什么？第 05 章会讲。

---

> 📊 本教程无可视化
>
> 本教程编辑记录：2026-06-12 初始版本。