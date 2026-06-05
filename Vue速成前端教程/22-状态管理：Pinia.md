# 22 — 状态管理：Pinia，全局数据的"公告栏"

- 对应文档版本：N/A（独立教程）
- 适用环境：Vue 3.x + Pinia 2.x + `pinia-plugin-persistedstate`
- 读者角色：前端开发者
- 预计耗时：新手 60 分钟 / 熟手 25 分钟
- 前置教程：教程 21（表单处理进阶）
- 可视化：无

---

## 一、目标与完成效果

**一句话目标**：用 Pinia 替换散落在各组件里的 `localStorage` 读写，实现统一的全局状态管理，并让登录状态在刷新后不丢失。

**完成后你将看到**：
- 登录成功后，导航栏自动显示用户名和头像，不再需要手动刷新页面。
- 刷新浏览器后，登录状态仍然保持（不会一刷新就变"未登录"）。
- 任何组件都能通过一行 `useUserStore()` 读写用户信息，不用再到处 `localStorage.getItem`。

---

## 二、前置条件

- Vue 3 项目已创建，已有 `Login.vue`、导航栏组件（如 `BlogHeader.vue`）
- 项目中已有的登录逻辑是将 token 存入 `localStorage`
- 理解 Vue 3 Composition API 基础（`ref`、`reactive`、`computed`）

**环境验证命令**：
```bash
npm list pinia
```
如果提示找不到 Pinia，先安装：
```bash
npm install pinia
```

---

## 三、分步操作

### 步骤 1：痛点诊断 — 为什么需要 Pinia？

**先看看现状**。

你的项目中，登录成功后大概率这样写：

```js
// Login.vue
async function handleSubmit() {
  const res = await fetch('/api/login', { /* ... */ })
  const data = await res.json()
  localStorage.setItem('token', data.token)
  localStorage.setItem('userInfo', JSON.stringify(data.user))
  // 可是导航栏还不知道你登录了！
}
```

然后导航栏里这样读：

```js
// BlogHeader.vue
const isLoggedIn = ref(false)
const username = ref('')
onMounted(() => {
  const token = localStorage.getItem('token')
  if (token) {
    isLoggedIn.value = true
    username.value = JSON.parse(localStorage.getItem('userInfo')).username
  }
})
```

**问题清单**（你能感觉到痛）：
1. 每个需要用户信息的组件都要写一遍 `localStorage.getItem`。
2. 登录成功后，导航栏不会自动更新——因为 `localStorage` 不是响应式的。
3. 取数据时忘了 `JSON.parse`，调半天发现是 `[object Object]`。
4. 你不知道到底有哪些地方在用 token，想改存储方式时不敢动。

类比：这就好比你有一份重要的公司公告，但不是贴在公告栏，而是复印了几十份塞在每个员工的抽屉里。每次内容更新，你得逐个抽屉去换。**Pinia 就是那个公告栏**——信息贴在一个地方，所有人抬头就能看到最新版本。

---

### 步骤 2：理解 Pinia 三要素

Pinia 的核心概念只有三个，用"冰箱"类比：

| 概念 | 冰箱类比 | 代码里的样子 |
|------|----------|-------------|
| **State（状态）** | 冰箱里存的食物 | `const token = ref('')` |
| **Getters（计算属性）** | "冰箱满了吗？"（看一眼就知道，不做改动） | `const isLoggedIn = computed(() => !!token)` |
| **Actions（动作）** | 往冰箱放东西 / 拿东西 | `function login(token) { this.token = token }` |

🤔 **想多一点**：Pinia 的 Actions 里既有同步操作也有异步操作——不像 Vuex 那样强行分 `mutations` 和 `actions`。Pinia 认为"放冰箱"这件事本身就是操作，你管我是一秒钟放进去（同步）还是跑去超市买回来再放（异步）呢？

---

### 步骤 3：创建第一个 Store — `stores/user.js`

**我在做什么？**
创建一个"用户公告栏"——所有和用户身份有关的信息都写在这里。

**创建文件** `src/stores/user.js`：

```js
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useUserStore = defineStore('user', () => {
  // ---- State（状态）----
  const token = ref('')
  const userInfo = ref(null)

  // ---- Getters（计算属性）----
  const isLoggedIn = computed(() => !!token.value)

  const username = computed(() => {
    return userInfo.value?.username || '未登录'
  })

  // ---- Actions（动作）----
  function login(newToken, newUserInfo) {
    token.value = newToken
    userInfo.value = newUserInfo
  }

  function logout() {
    token.value = ''
    userInfo.value = null
  }

  // 导出给外部使用
  return { token, userInfo, isLoggedIn, username, login, logout }
})
```

**注册 Pinia**，修改 `src/main.js`：

```js
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.mount('#app')
```

步骤小结：
1. `defineStore('user', () => { ... })` 定义了一个叫 `user` 的 store
2. Setup Store 风格（用 Composition API 写 store）是 Pinia 推荐的写法
3. 在 `main.js` 里 `app.use(createPinia())` 注册后，所有组件都能用了

**我做得对不对？**
在浏览器控制台输入 `app.config.globalProperties` 不会有 Pinia，但在任何 `.vue` 文件的 `<script setup>` 中可以直接 `import { useUserStore } from '@/stores/user'` 并使用。

---

### 步骤 4：组件中使用 Store

**改造 Login.vue**——登录成功后将数据写入 store 而非 `localStorage`：

```js
// Login.vue <script setup>
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()

async function handleSubmit() {
  // ... 校验逻辑 ...
  submitting.value = true
  try {
    const res = await fetch('/api/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(form)
    })
    if (!res.ok) throw new Error('登录失败')
    const data = await res.json()

    // 🎯 关键改变：写入 store 而非 localStorage
    userStore.login(data.token, data.user)

    toast.show = true
    toast.message = '登录成功！'
    toast.type = 'success'
  } catch (e) {
    toast.show = true
    toast.message = e.message
    toast.type = 'error'
  } finally {
    submitting.value = false
  }
}
```

❌ **旧写法**：`localStorage.setItem('token', data.token)`
✅ **新写法**：`userStore.login(data.token, data.user)`

**改造 BlogHeader.vue**——从 store 读而非 `localStorage`：

```html
<template>
  <header class="blog-header">
    <h1>我的博客</h1>
    <nav>
      <router-link to="/">首页</router-link>
      <router-link to="/create">写文章</router-link>
      <template v-if="userStore.isLoggedIn">
        <span>👋 {{ userStore.username }}</span>
        <button @click="handleLogout">退出</button>
      </template>
      <template v-else>
        <router-link to="/login">登录</router-link>
      </template>
    </nav>
  </header>
</template>

<script setup>
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()

function handleLogout() {
  userStore.logout()
}
</script>
```

🤔 **想多一点**：你会发现导航栏不再需要 `onMounted` 了。因为 store 是响应式的——`userStore.isLoggedIn` 是一个 `computed`，它背后依赖的 `token` 是 `ref`。当 Login 组件调用 `userStore.login()` 改变 `token` 时，所有用到 `isLoggedIn` 的地方都会自动刷新。这就是"公告栏"的力量：贴一张公告，所有人抬头都看到了。

**我做得对不对？**
1. 登录成功后，导航栏应立即显示用户名（不需要刷新页面）。
2. 点击"退出"按钮，导航栏应立刻变回"登录"链接。
3. 在浏览器 DevTools 的 Vue 插件中可以看到 Pinia store 的状态变化。

**不对怎么办？**
- 导航栏不更新 → 检查 `BlogHeader.vue` 是否在 `<script setup>` 中调用了 `useUserStore()`（不是在 `onMounted` 里调用）。
- 报错 "getActivePinia was called with no active Pinia" → 检查 `main.js` 是否执行了 `app.use(createPinia())`。
- 登录后刷新又变回未登录 → 正常！因为我们还没做持久化，看下一步。

---

### 步骤 5：持久化 — 刷新不丢失

**我在做什么？**
现在的 store 存在内存里，一刷新浏览器就没了——就像公告栏上的便利贴被风吹走了。我们需要把公告"刻在石板上"。

**安装插件**：
```bash
npm install pinia-plugin-persistedstate
```

**注册插件**，修改 `src/main.js`：

```js
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import piniaPluginPersistedstate from 'pinia-plugin-persistedstate'
import App from './App.vue'

const app = createApp(App)
const pinia = createPinia()
pinia.use(piniaPluginPersistedstate)

app.use(pinia)
app.mount('#app')
```

**在 Store 中开启持久化**，修改 `src/stores/user.js`：

```js
export const useUserStore = defineStore('user', () => {
  // ... 内部代码不变 ...
  return { token, userInfo, isLoggedIn, username, login, logout }
}, {
  persist: true  // 🎯 就这一行，全部自动存到 localStorage
})
```

**工作原理**：
- 每次 state 变化，插件自动写入 `localStorage`
- 每次页面加载（刷新），插件自动从 `localStorage` 恢复到 state
- 你完全不需要手动写 `getItem` / `setItem`

**如果只想持久化部分字段**（比如 token 要存，但某些临时状态不用存）：

```js
persist: {
  pick: ['token', 'userInfo']  // 只存这两个字段
}
```

🤔 **想多一点**：为什么不直接继续用 `localStorage.setItem`？因为 Pinia 持久化插件解决了两个问题：(1) 自动同步，不需要在每个 action 里手动 `setItem`；(2) 统一管理，将来你想换成 `sessionStorage` 或 IndexedDB，只需改插件配置，不用翻遍所有组件。

**我做得对不对？**
1. 登录成功后，关闭浏览器标签页再打开（或直接按 F5 刷新），导航栏仍显示已登录。
2. 打开浏览器 DevTools → Application → Local Storage，能看到 key 为 `user` 的条目，内容是 Pinia store 的 JSON。

---

### 步骤 6：改造完整流程

**最终调整清单**：

| 文件 | 改动内容 |
|------|----------|
| `src/main.js` | 注册 Pinia + 持久化插件 |
| `src/stores/user.js` | 新建，定义 state/getters/actions，开启 persist |
| `src/views/Login.vue` | 用 `userStore.login()` 替换 `localStorage.setItem` |
| `src/views/Register.vue` | 注册成功后同样写入 store |
| `src/components/BlogHeader.vue` | 从 store 读取 `isLoggedIn` 和 `username` |
| 其他需要 token 的组件 | 从 store 读取 `token` 发请求 |

**改造示例 — 发送 API 请求时从 store 取 token**：

```js
// 任何需要认证的请求
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()

async function fetchPosts() {
  const res = await fetch('/api/posts', {
    headers: {
      'Authorization': `Bearer ${userStore.token}`  // 🎯 从 store 取
    }
  })
  // ...
}
```

---

## 四、完整代码清单

<details>
<summary>src/main.js</summary>

```js
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import piniaPluginPersistedstate from 'pinia-plugin-persistedstate'
import App from './App.vue'
import router from './router'

const app = createApp(App)
const pinia = createPinia()
pinia.use(piniaPluginPersistedstate)

app.use(pinia)
app.use(router)
app.mount('#app')
```
</details>

<details>
<summary>src/stores/user.js</summary>

```js
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useUserStore = defineStore('user', () => {
  const token = ref('')
  const userInfo = ref(null)

  const isLoggedIn = computed(() => !!token.value)

  const username = computed(() => {
    return userInfo.value?.username || '未登录'
  })

  function login(newToken, newUserInfo) {
    token.value = newToken
    userInfo.value = newUserInfo
  }

  function logout() {
    token.value = ''
    userInfo.value = null
  }

  return { token, userInfo, isLoggedIn, username, login, logout }
}, {
  persist: true
})
```
</details>

---

## 五、验证方法

按顺序检查：

1. 未登录时 → 导航栏显示"登录"链接
2. 登录成功 → 导航栏立刻显示用户名（不刷新页面）
3. F5 刷新 → 导航栏仍显示已登录
4. 点击"退出"→ 导航栏立刻变回"登录"链接
5. 打开 DevTools → Application → Local Storage → 确认有 `user` 这个 key

---

## 六、小结

| 痛点 | 旧方案 | Pinia 方案 |
|------|--------|-----------|
| 数据分散 | 每个组件各自 `localStorage.getItem` | 统一在 store 中读写 |
| 不响应式 | `localStorage` 变了组件不知道 | `ref` + `computed`，自动更新 |
| 类型不安全 | `JSON.parse` 可能报错或返回 `null` | store 的 `ref` 有明确初始类型 |
| 重复代码 | N 个组件写 N 遍读取逻辑 | 一行 `useUserStore()` |

| 概念 | 比喻 | 代码 |
|------|------|------|
| **Store** | 公告栏 | `defineStore('user', () => { ... })` |
| **State** | 冰箱里的食物 | `const token = ref('')` |
| **Getters** | "冰箱满了吗？" | `computed(() => !!token.value)` |
| **Actions** | 放东西 / 拿东西 | `function login(token) { ... }` |
| **持久化** | 把便利贴刻在石板上 | `persist: true` |

---

## 七、术语附录

| 术语 | 解释 |
|------|------|
| **Pinia** | Vue 3 官方推荐的状态管理库，Vuex 的继任者。比 Vuex 更轻量、TypeScript 友好、不需要 `mutations`。 |
| **Store** | Pinia 中的"仓库"，存放某个领域的所有状态和操作。一个应用可以有多个 store（如 userStore、postStore）。 |
| **State** | Store 中存的"数据本身"，如 token、userInfo。底层是 Vue 的 `ref` 或 `reactive`。 |
| **Getters** | 基于 state 计算出的值，类似 `computed`。当依赖的 state 变化时自动重新计算。 |
| **Actions** | 修改 state 的函数（同步或异步都行）。和 Vuex 最大的不同：不需要区分 `mutations` 和 `actions`。 |
| **持久化 (Persistence)** | 将内存中的数据保存到持久存储（如 localStorage），使得页面刷新后数据不丢失。Pinia 通过插件实现。 |

---

## 八、已知坑点与禁止事项

- **禁止在组件外（如普通 `.js` 文件）直接调用 `useUserStore()`**：必须在 `setup` 函数或 `<script setup>` 生命周期内调用。如果在 router 守卫里用，需要特殊处理（教程 25 会讲）。
- **禁止在 store 的 action 里用 `this.$router`**：store 不应该依赖路由实例。需要跳转的话，在组件里调用 action 后再跳转。
- **persist 插件默认用 `localStorage`**：注意存储空间限制（通常 5-10MB），不要把所有数据都塞进一个 store。
- **敏感信息警告**：token 存在 `localStorage` 里是明文，有 XSS 风险。生产环境建议用 httpOnly cookie，但这是后端的话题。

---

## 九、下一步建议

- 教程 23：错误处理与加载状态，给项目加上统一的 loading 和空状态展示。
- 进阶：创建第二个 Store（如 `stores/post.js`）管理文章列表，练习多 Store 协作。