# 16 - 调用后端 API

- 对应文档版本：N/A（教程系列第16篇）
- 适用环境：Vue 3 + Vite / Node.js 18+
- 读者角色：前端开发者
- 预计耗时：新手 40分钟 / 熟手 15分钟
- 前置教程：[15 - 文章详情页](./15-文章详情页.md)
- 可视化：有，[vue_16_api_visual.html](vue_16_api_visual.html)

---

## 一、目标与完成效果

**一句话目标**：把 mock 假数据替换为从后端 API 获取的真实数据，学会 `fetch` + `async/await` 的标准写法。

**完成后的可观测效果**：
- 首页文章列表从后端 API 获取（而非 `mock/posts.js`）
- 文章详情页从后端 API 获取
- 代码中有一个集中的 `api/index.js` 文件，统一管理所有请求
- 即使后端还没写好，用在线 mock 服务也能验证前端逻辑

---

## 二、前置条件

| 前置项 | 版本/要求 | 验证命令 |
|--------|-----------|----------|
| 首页与详情页已实现 | 13~14教程完成 | 浏览器访问 `/` 和 `/post/1` 正常 |
| 后端 API 可用（或使用在线 mock） | 见练习步骤 | `curl http://localhost:8000/api/posts` 有返回 |

**一键验证**（如果后端已启动）：
```bash
curl http://localhost:8000/api/posts
```

如果后端未启动，本教程提供在线 mock 替代方案，不影响学习。

---

## 三、分步操作

> 📊 可视化演示见 [vue_16_api_visual.html](vue_16_api_visual.html)

### 步骤1：理解为什么需要后端 API

#### 我在做什么？

先弄明白「为什么不能一直用 mock 数据」。

**比喻：餐厅的前台和后厨**

```
你（浏览器）           前台（前端）           后厨（后端API）
    │                     │                      │
    │  "我要一份牛排"      │                      │
    │─────────────────────→│                      │
    │                     │  "5号桌要牛排"         │
    │                     │─────────────────────→│
    │                     │                      │ 煎牛排...
    │                     │     "牛排好了"         │
    │                     │←─────────────────────│
    │  "您的牛排"          │                      │
    │←─────────────────────│                      │
```

| 角色 | 谁 | 干什么 |
|------|-----|--------|
| 食客 | 浏览器 | 发起请求，展示结果 |
| 前台 | 前端（Vue） | 发送请求，把数据渲染成界面 |
| 后厨 | 后端 API | 接收请求，查数据库，返回数据 |

mock 数据相当于「前台自己在柜台下藏了几份预制菜」——开发阶段可以糊弄，但真正的数据必须从后厨（后端）拿。

#### 前端 vs 后端职责边界

| 前端负责 | 后端负责 |
|----------|----------|
| 发送请求（fetch） | 接收请求 |
| 渲染数据到界面 | 查询数据库 |
| 处理加载/错误状态 | 校验权限 |
| 页面跳转 | 返回 JSON 数据 |

> 📌 **术语标记**：「API」「fetch」「async/await」「BASE_URL」将收录于术语附录。

---

### 步骤2：封装 API 请求模块

#### 我在做什么？

把所有「跟后端通信」的代码集中到一个文件里，而不是散落在各个组件中。这样以后换后端地址、加 token、改请求方式，只改一个文件就够了。

**创建 `src/api/index.js`**：

```js
// api/index.js — 后端 API 请求封装（所有请求的统一出口）

// 后端服务器地址（开发环境）
const BASE_URL = 'http://localhost:8000'

/**
 * 封装 fetch 请求
 * @param {string} path - API 路径，如 '/api/posts'
 * @param {object} options - fetch 配置项（method, headers, body 等）
 * @returns {Promise<object>} 解析后的 JSON 数据
 */
async function request(path, options = {}) {
  // 拼接完整 URL
  const url = `${BASE_URL}${path}`

  // 默认配置 + 用户传入的配置（后者覆盖前者）
  const config = {
    headers: {
      'Content-Type': 'application/json',
    },
    ...options,
  }

  // 发送请求
  const response = await fetch(url, config)

  // 如果响应状态码不是 2xx，抛出错误
  if (!response.ok) {
    throw new Error(`请求失败: ${response.status} ${response.statusText}`)
  }

  // 解析 JSON 并返回
  return response.json()
}

// ====== 具体 API 方法 ======

/** 获取文章列表 */
export function getPosts() {
  return request('/api/posts')
}

/** 获取单篇文章 */
export function getPost(id) {
  return request(`/api/posts/${id}`)
}

/** 用户注册 */
export function registerUser(data) {
  return request('/api/users/register', {
    method: 'POST',
    body: JSON.stringify(data),
  })
}

/** 用户登录 */
export function loginUser(data) {
  return request('/api/users/login', {
    method: 'POST',
    body: JSON.stringify(data),
  })
}

/** 创建文章（需要认证） */
export function createPost(data, token) {
  return request('/api/posts', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
    },
    body: JSON.stringify(data),
  })
}

/** 更新文章（需要认证） */
export function updatePost(id, data, token) {
  return request(`/api/posts/${id}`, {
    method: 'PUT',
    headers: {
      'Authorization': `Bearer ${token}`,
    },
    body: JSON.stringify(data),
  })
}

/** 删除文章（需要认证） */
export function deletePost(id, token) {
  return request(`/api/posts/${id}`, {
    method: 'DELETE',
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  })
}
```

#### 代码分层解释

```
api/index.js 的分层结构：
┌─────────────────────────────────┐
│  request() — 基础请求函数        │  ← 统一处理 URL 拼接、JSON 解析、错误处理
├─────────────────────────────────┤
│  getPosts()                     │
│  getPost(id)                    │  ← 具体 API 方法（每个函数只做一件事）
│  registerUser(data)             │
│  loginUser(data)                │
│  createPost(data, token)        │
│  updatePost(id, data, token)    │
│  deletePost(id, token)          │
└─────────────────────────────────┘
```

#### 核心概念解释

| 代码 | 含义 |
|------|------|
| `BASE_URL` | 后端服务器地址。开发时是 `localhost:8000`，上线后改成真实域名 |
| `fetch(url, config)` | 浏览器原生 API，发起 HTTP 请求 |
| `await` | 等待异步操作完成，拿到结果后再继续执行 |
| `response.json()` | 把服务器返回的 JSON 字符串解析为 JavaScript 对象 |
| `!response.ok` | HTTP 状态码不是 2xx 时（如 404、500），`ok` 为 `false` |
| `JSON.stringify(data)` | 把 JS 对象转为 JSON 字符串（POST/PUT 请求体需要） |
| `Authorization: Bearer ${token}` | HTTP 认证头，告诉后端「我是谁」 |

🤔 **想多一点**：为什么需要 `await` 两次？`await fetch(url, config)` 等待服务器「响应」（拿到响应头），`await response.json()` 等待响应体「全部下载并解析」。这是两个阶段：先确认对方收到了，再等对方说完。

---

### 步骤3：用 async/await 改造 Home.vue

#### 我在做什么？

把首页的「从 mock 导入数据」改为「从后端 API 获取数据」。

**比喻**：之前你从口袋里掏出一张写好的菜单（mock），现在你要走到后厨窗口去问「今天有什么菜？」（fetch API）。

**修改 `src/views/Home.vue`**：

```vue
<template>
  <div class="home">
    <h1>📚 最新文章</h1>

    <!-- 加载中 -->
    <div v-if="loading">⏳ 加载中...</div>

    <!-- 加载失败 -->
    <div v-else-if="error" class="error">
      <p>😵 加载失败：{{ error }}</p>
      <button @click="fetchPosts">🔄 重试</button>
    </div>

    <!-- 文章列表 -->
    <template v-else>
      <BlogCard
        v-for="post in posts"
        :key="post.id"
        :post="post"
      />
      <p v-if="posts.length === 0">还没有文章，快来写第一篇吧！</p>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getPosts } from '../api/index.js'   // ← 改为从 API 导入
import BlogCard from '../components/BlogCard.vue'

const posts = ref([])         // 文章列表
const loading = ref(true)     // 加载状态
const error = ref(null)       // 错误信息

async function fetchPosts() {
  loading.value = true
  error.value = null
  try {
    const data = await getPosts()   // 调用 API
    posts.value = data
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchPosts()
})
</script>

<style scoped>
.home {
  max-width: 720px;
  margin: 0 auto;
  padding: 20px;
}
h1 {
  margin-bottom: 20px;
}
.error {
  text-align: center;
  padding: 40px;
  color: #e74c3c;
}
.error button {
  margin-top: 12px;
  padding: 8px 20px;
  cursor: pointer;
}
</style>
```

#### 代码逐行解释

| 代码 | 含义 |
|------|------|
| `async function fetchPosts()` | `async` 标记这是一个异步函数，内部可以用 `await` |
| `await getPosts()` | 等待 API 返回数据，拿到结果后赋值给 `data` |
| `try { ... } catch (err) { ... }` | 捕获网络错误或 API 返回的错误 |
| `finally { ... }` | 无论成功还是失败，最终都会执行（关闭 loading） |
| `error.value = err.message` | 把错误信息存起来，显示给用户 |
| `v-if="loading"` | 正在加载时显示加载动画 |
| `v-else-if="error"` | 加载失败时显示错误 + 重试按钮 |

❌ **错误写法**：不用 `try/catch`
```js
const data = await getPosts()  // 如果网络断了，整个应用崩溃
posts.value = data
```

✅ **正确写法**：用 `try/catch` 包裹
```js
try {
  const data = await getPosts()
  posts.value = data
} catch (err) {
  error.value = err.message   // 错误被捕获，显示友好提示
}
```

---

### 步骤4：用 async/await 改造 PostDetail.vue

#### 我在做什么？

同样改造详情页，从 API 获取单篇文章。

**修改 `src/views/PostDetail.vue` 的 `<script setup>` 部分**：

```vue
<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { getPost } from '../api/index.js'   // ← 改为从 API 导入

const route = useRoute()
const id = Number(route.params.id)
const post = ref(null)
const loading = ref(true)
const error = ref(null)

async function fetchPost() {
  loading.value = true
  error.value = null
  try {
    const data = await getPost(id)   // 调用 API
    post.value = data
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchPost()
})
</script>
```

**模板部分增加错误状态**（在上方 `<template>` 中添加）：

```vue
<template>
  <div class="post-detail">
    <div v-if="loading">⏳ 加载中...</div>

    <!-- 新增：加载失败 -->
    <div v-else-if="error" class="error">
      <p>😵 加载失败：{{ error }}</p>
      <button @click="fetchPost">🔄 重试</button>
    </div>

    <div v-else-if="!post" class="not-found">
      <!-- ... 不变 ... -->
    </div>

    <article v-else>
      <!-- ... 不变 ... -->
    </article>

    <router-link to="/" class="back-link">← 返回首页</router-link>
  </div>
</template>
```

#### 现在变成四种状态了

| 状态 | 条件 | 显示 |
|------|------|------|
| 加载中 | `loading === true` | ⏳ 加载中... |
| 加载失败 | `error !== null` | 😵 加载失败 + 重试按钮 |
| 文章不存在 | `!loading && !error && !post` | 😕 文章不存在 |
| 正常 | `!loading && !error && post` | 文章内容 |

---

### 步骤5：async/await vs Promise.then() 对比

#### 我在做什么？

用一张表说清楚两种异步写法的区别，帮你理解为什么教程选 `async/await`。

**比喻**：`Promise.then()` 是发短信——发完一条等回复，收到回复再发下一条。`async/await` 是打电话——打通后直接说，不用来回发短信。

| | `Promise.then()` | `async/await` |
|------|------|------|
| 写法 | `fetch(url).then(res => res.json()).then(data => ...)` | `const res = await fetch(url); const data = await res.json()` |
| 可读性 | 链式调用，嵌套多了像「回调地狱」 | 看起来像同步代码，从上到下逐行执行 |
| 错误处理 | `.catch(err => ...)` | `try/catch` |
| 调试 | 断点难打（链式调用） | 逐行打断点，和普通代码一样 |

❌ **Promise.then() 写法**（不推荐）：
```js
fetch('/api/posts')
  .then(res => res.json())
  .then(data => {
    posts.value = data
  })
  .catch(err => {
    error.value = err.message
  })
```

✅ **async/await 写法**（推荐）：
```js
try {
  const res = await fetch('/api/posts')
  const data = await res.json()
  posts.value = data
} catch (err) {
  error.value = err.message
}
```

🤔 **想多一点**：`async/await` 是 `Promise.then()` 的语法糖——本质上做的事一模一样，但写法更符合人类阅读习惯。就像「把大象放进冰箱」：打开门→放进去→关门，而不是「打开门，然后(放进去，然后(关门))」。

---

### 步骤6：练习——启动后端或使用在线 Mock

#### 方案A：你有后端 API

如果你的后端博客 API 已启动在 `http://localhost:8000`：

```bash
# 验证后端可用
curl http://localhost:8000/api/posts
```

然后启动前端：
```bash
npm run dev
```

首页应该能正常加载文章列表。

#### 方案B：使用 JSON Server 快速搭建 Mock API

如果后端还没写好，用 `json-server` 在本地快速搭一个 RESTful API：

```bash
# 1. 安装 json-server
npm install -g json-server

# 2. 创建 db.json（在项目根目录）
```

**创建 `db.json`**（放在项目根目录）：

```json
{
  "posts": [
    { "id": 1, "title": "Vue 3 入门指南", "summary": "从零搭建你的第一个项目", "author": "小明", "createdAt": "2026-05-01", "content": "正文..." },
    { "id": 2, "title": "深入理解响应式原理", "summary": "ref 与 reactive 的区别", "author": "小红", "createdAt": "2026-05-05", "content": "正文..." },
    { "id": 3, "title": "Vue Router 完全指南", "summary": "从入门到动态路由", "author": "小明", "createdAt": "2026-05-10", "content": "正文..." }
  ]
}
```

```bash
# 3. 启动 json-server（监听 8000 端口）
json-server --watch db.json --port 8000
```

现在访问 `http://localhost:8000/posts` 会返回 JSON 数据。

**注意**：json-server 的路径是 `/posts`，不是 `/api/posts`。如果使用 json-server，需要临时修改 `api/index.js` 中的路径：
```js
// 用 json-server 时去掉 /api 前缀
export function getPosts() {
  return request('/posts')        // 不是 '/api/posts'
}
export function getPost(id) {
  return request(`/posts/${id}`)  // 不是 '/api/posts/${id}'
}
```

---

## 四、完整代码清单

<details>
<summary>src/api/index.js</summary>

（见步骤2的完整代码）
</details>

<details>
<summary>src/views/Home.vue（改造后）</summary>

（见步骤3的完整代码）
</details>

<details>
<summary>src/views/PostDetail.vue（改造后的 script 部分）</summary>

（见步骤4的完整代码）
</details>

---

## 五、术语附录

| 术语 | 解释 | 是否项目特有 |
|------|------|:---:|
| **API** | Application Programming Interface，这里指后端提供的 HTTP 接口。前端通过 URL 请求它，后端返回 JSON 数据。 | 否 |
| **fetch** | 浏览器原生 API，用于发起 HTTP 请求。相当于快递员，帮你把请求送到服务器，把响应带回来。 | 否 |
| **async/await** | JavaScript 的异步语法糖。`async` 标记函数为异步，`await` 等待异步操作完成。让异步代码看起来像同步代码。 | 否 |
| **BASE_URL** | 后端服务器的基础地址，如 `http://localhost:8000`。所有 API 路径都拼接在这个地址后面。 | 否 |
| **JSON** | JavaScript Object Notation，前后端数据交换的格式。看起来像 JS 对象，但本质是字符串。 | 否 |

---

## 六、小结

| 我学了什么 | 关键点 |
|------------|--------|
| 为什么需要 API | 前端是前台，后端是后厨，数据从后厨来 |
| 封装请求模块 | `api/index.js` 统一管理所有请求 |
| fetch 基础用法 | `fetch(url, config)` + `response.json()` |
| async/await | `async function` + `await` + `try/catch` |
| 错误处理 | `try/catch` 捕获异常，`error` 状态显示友好提示 |
| 三态变四态 | 增加「加载失败」状态，用户体验更完整 |
| JSON Server | 后端没写好时用 `json-server` 快速搭建 Mock API |

---

## 七、下一步建议

下一篇：[17 - 用户注册登录](./17-用户注册登录.md)，实现注册和登录表单，接收后端返回的 token，存到 localStorage，导航栏根据登录状态显示不同内容。

---

## 八、已知坑点与禁止事项

- ⚠️ **CORS 跨域问题**：如果后端没有配置 CORS，浏览器会阻止请求。表现为控制台报 `Access-Control-Allow-Origin` 错误。解决方案见下一篇教程。
- ⚠️ **`fetch` 不自动抛异常**：`fetch` 只在网络故障时 reject，HTTP 404/500 不会 reject。需要手动检查 `response.ok`。
- ⚠️ **`await` 只能在 `async` 函数里用**：如果在普通函数里写 `await`，会报语法错误。
- ⚠️ **`JSON.stringify` 别忘了**：POST/PUT 请求的 `body` 必须是 JSON 字符串，不是 JS 对象。