# 09 - 模板语法：Vue 的 HTML 增强

- **对应文档版本**：requirements.md v1.0
- **适用环境**：Vue3 + Vite 项目（已有 08 教程的组件结构）
- **读者角色**：前端初学者
- **预计耗时**：新手 45 分钟 / 熟手 20 分钟
- **前置教程**：08-组件：搭积木
- **可视化**：无

---

## 一、目标与完成效果

**一句话目标**：掌握 Vue 模板语法的七大核心指令，能把静态组件改造成数据驱动的动态组件。

**完成后的可观测效果**：
- BlogList 不再写死两篇文章，改为用 `v-for` 循环渲染数据数组
- 页面上的文章数量、内容由 JS 数据决定，改数据页面自动变
- 能说出 `v-if` 和 `v-show` 的区别，知道什么场景分别用谁

---

## 二、前置条件

- 已完成 08 教程，`src/components/BlogList.vue` 存在且能正常显示
- 开发服务器能正常运行

**环境验证命令**：
```bash
cd blog-frontend && npm run dev
```

---

## 三、比喻：模板语法 = HTML + 超能力指令

普通 HTML 是「死的」——你写什么它就显示什么，不会变。Vue 的模板语法给 HTML 注入了「超能力」——它能根据数据动态改变显示内容。

打个比方：

| 普通 HTML | Vue 模板语法 |
|---|---|
| 一张**已经冲洗好的照片**，内容永远不变 | 一个**实时监控屏幕**，画面随摄像头前的场景实时变化 |
| 你在 HTML 里写 `<h1>你好</h1>`，永远显示「你好」 | 你在 Vue 里写 `<h1>{{ greeting }}</h1>`，`greeting` 变量是什么就显示什么 |

这些「超能力」具体表现为一系列 **`v-` 开头的指令**（Directive）。下面我们逐个击破。

> 🤔 **想多一点**：为什么叫「指令」而不是「属性」？因为 `v-if`、`v-for` 这些不是普通的 HTML 属性，它们是 Vue 给 HTML 元素下达的**命令**——「如果条件为真才显示」「循环渲染这个元素 N 次」。它们长得像属性，但功能远超属性。

---

## 四、分步操作

### 步骤 1：`{{ }}` 插值 —— 显示变量

> **我在做什么？** 用双大括号把 JavaScript 变量显示在页面上。

打开 `src/components/BlogHeader.vue`，在 `<script setup>` 里加一个变量，在 `<template>` 里用它：

```vue
<template>
  <header class="blog-header">
    <h1>🖊️ {{ blogTitle }}</h1>    <!-- 原来是写死的文字，现在用变量 -->
    <nav>
      <a href="#">首页</a>
      <a href="#">归档</a>
      <a href="#">关于我</a>
    </nav>
  </header>
</template>

<script setup>
const blogTitle = '我的技术博客'  // 改这里，页面上标题自动变
</script>

<style scoped>
/* ... 样式不变，省略 ... */
</style>
```

保存，浏览器里标题自动变成「我的技术博客」。试试把 `blogTitle` 改成「小明的前端笔记」，保存再看——页面自动更新。

> ✅ **做得对不对？** 改 `blogTitle` 的值，保存后浏览器显示的标题跟着变。

**`{{ }}` 里面可以写任何 JavaScript 表达式**：

```vue
<p>{{ 1 + 1 }}</p>                  <!-- 显示 2 -->
<p>{{ blogTitle.toUpperCase() }}</p> <!-- 显示 我的技术博客（大写） -->
<p>{{ isLogin ? '已登录' : '未登录' }}</p> <!-- 三元表达式 -->
```

但**不能写语句**（`if`、`for`、变量声明），只能用**表达式**（能算出结果的代码）。

---

### 步骤 2：`v-bind`（简写 `:`）—— 动态绑定属性

> **我在做什么？** 让 HTML 属性的值由 JavaScript 变量决定，而不是写死。

普通 HTML 里，属性值是写死的：

```html
<!-- ❌ 属性写死，没法动态改 -->
<a href="https://example.com">链接</a>
<img src="/logo.png">
<div class="static-class">
```

Vue 里用 `v-bind` 把属性值绑定到变量：

```vue
<template>
  <!-- v-bind 完整写法 -->
  <a v-bind:href="blogUrl">链接</a>
  
  <!-- v-bind 简写（最常用）—— 只写一个冒号 -->
  <a :href="blogUrl">链接</a>
  <img :src="logoPath" :alt="logoDesc">
  <div :class="dynamicClass">
</template>

<script setup>
const blogUrl = 'https://example.com'
const logoPath = '/logo.png'
const logoDesc = '网站 Logo'
const dynamicClass = 'highlight'
</script>
```

> ✅ **做得对不对？** 属性值跟着变量走，改 JS 变量页面属性自动变。

**动态 class 特别有用**：

```vue
<template>
  <!-- 单个 class -->
  <div :class="activeClass">...</div>

  <!-- 对象语法：true 就加这个 class，false 就不加 -->
  <div :class="{ active: isActive, disabled: !isActive }">...</div>

  <!-- 数组语法：多个 class -->
  <div :class="['base-class', extraClass]">...</div>
</template>

<script setup>
const activeClass = 'highlight'
const isActive = true
const extraClass = 'shadow'
</script>
```

> 🤔 **想多一点**：记住一个规律——**凡是 HTML 属性值你想要动态改变的，就在属性名前加 `:`**。`href` → `:href`，`src` → `:src`，`class` → `:class`。这是 Vue 里用得最频繁的语法之一。

---

### 步骤 3：`v-if` / `v-else` / `v-show` —— 条件渲染

> **我在做什么？** 根据条件决定一个元素显示还是不显示。

**口诀：频繁切换用 `v-show`，不常变用 `v-if`。**

#### 3.1 `v-if` / `v-else`

```vue
<template>
  <!-- 如果 isLogin 为 true，显示「欢迎回来」；否则显示「请登录」 -->
  <p v-if="isLogin">👋 欢迎回来，{{ username }}！</p>
  <p v-else>🔒 请先登录</p>
</template>

<script setup>
const isLogin = false
const username = '小明'
</script>
```

`v-if` 是「**真**的渲染」：条件为 false 时，这个元素**完全不存在于 DOM 中**（你用浏览器「检查元素」找不到它）。适合用在条件不太频繁变化的场景，比如用户是否登录、是否有权限。

#### 3.2 `v-show`

```vue
<template>
  <!-- v-show 只用在一个元素上，不能和 v-else 搭配 -->
  <p v-show="isVisible">👀 你能看到我</p>
</template>

<script setup>
const isVisible = true
</script>
```

`v-show` 是「**假**的隐藏」：条件为 false 时，元素还在 DOM 里，只是被加了 `display: none`。适合用在频繁切换的场景，比如选项卡、折叠面板、弹窗显隐。

#### 3.3 对比

| | `v-if` | `v-show` |
|---|---|---|
| **false 时的行为** | 元素从 DOM 中**移除** | 元素还在，加 `display: none` |
| **切换开销** | 高（每次要创建/销毁元素） | 低（只改 CSS） |
| **初始渲染开销** | 低（false 时不渲染） | 高（不管 true/false 都会渲染） |
| **适用场景** | 条件不常变（登录状态、权限） | 频繁切换（选项卡、弹窗） |
| **能否和 `v-else` 搭配** | ✅ 可以 | ❌ 不可以 |

> ✅ **做得对不对？** 修改 JS 里的布尔变量，页面上对应元素出现/消失。

---

### 步骤 4：`v-for` —— 列表渲染

> **我在做什么？** 根据数组数据，循环生成多个相同结构的元素。

这是改造 BlogList 的关键一步。不再写死两篇 `<article>`，而是用数据数组 + `v-for` 自动渲染。

**语法**：`v-for="item in items"` 或 `v-for="(item, index) in items"`

```vue
<template>
  <ul>
    <!-- 循环渲染每个水果名 -->
    <li v-for="fruit in fruits" :key="fruit">{{ fruit }}</li>
  </ul>
</template>

<script setup>
const fruits = ['🍎 苹果', '🍌 香蕉', '🍊 橘子']
</script>
```

**`:key` 必须加！** `:key` 给每个循环项一个唯一标识，帮助 Vue 追踪哪个元素变了。不加 `:key` Vue 会报警告，而且在列表顺序变化时可能出现渲染错误。

```vue
<!-- ❌ 没有 :key，Vue 会报警告 -->
<li v-for="fruit in fruits">{{ fruit }}</li>

<!-- ✅ 加了 :key -->
<li v-for="fruit in fruits" :key="fruit">{{ fruit }}</li>

<!-- ✅ 用索引当 key（实在没有唯一值时） -->
<li v-for="(fruit, index) in fruits" :key="index">{{ fruit }}</li>
```

> 🤔 **想多一点**：为什么 `:key` 这么重要？Vue 为了高效更新 DOM，会尽量复用已有的元素。如果你没有 `:key`，Vue 分不清「第一个 `<li>` 和第二个 `<li>` 谁是谁」。如果你删了数组第一项，Vue 可能只改内容而不移动 DOM 节点，导致状态错乱。`key` 就像每个元素的身份证号。

> ✅ **做得对不对？** 修改数组内容（push、pop、修改某项），页面列表自动更新。

---

### 步骤 5：`v-model` —— 双向绑定

> **我在做什么？** 让表单输入框和 JavaScript 变量「双向同步」：输入框改了变量自动变，变量改了输入框也自动变。

```vue
<template>
  <div>
    <!-- v-model 让 input 和变量双向绑定 -->
    <input v-model="username" placeholder="输入你的名字" />
    <p>你好，{{ username }}！</p>
  </div>
</template>

<script setup>
import { ref } from 'vue'
const username = ref('')
</script>
```

**效果**：你在输入框里打字，下面 `<p>` 里的名字实时跟着变。不用写 `addEventListener('input', ...)`，不用手动更新 DOM，`v-model` 全包了。

> 🤔 **想多一点**：`v-model` 本质上是 `v-bind:value` + `v-on:input` 的语法糖。也就是说 Vue 偷偷帮你写了一行绑定 `value` 属性 + 一行监听 `input` 事件。这就是框架的价值——把重复的脏活累活封装成简单的指令。

`v-model` 适用于各种表单元素：

```vue
<input v-model="text" />                    <!-- 文本框 -->
<textarea v-model="text"></textarea>         <!-- 文本域 -->
<input type="checkbox" v-model="checked" /> <!-- 复选框 -->
<input type="radio" v-model="picked" />     <!-- 单选按钮 -->
<select v-model="selected">                 <!-- 下拉框 -->
  <option value="a">A</option>
  <option value="b">B</option>
</select>
```

---

### 步骤 6：`v-on`（简写 `@`）—— 事件处理

> **我在做什么？** 监听用户的点击、输入、滚动等操作，执行 JavaScript 代码。

**语法**：`v-on:事件名="处理函数"` 或简写 `@事件名="处理函数"`

```vue
<template>
  <div>
    <p>点击次数：{{ count }}</p>
    <!-- v-on 完整写法 -->
    <button v-on:click="count++">+1（完整写法）</button>
    <!-- @ 简写，最常用 -->
    <button @click="count++">+1（简写）</button>
    <!-- 调用函数 -->
    <button @click="resetCount">归零</button>
  </div>
</template>

<script setup>
import { ref } from 'vue'
const count = ref(0)

function resetCount() {
  count.value = 0
}
</script>
```

**常用事件**：`@click`、`@input`、`@submit`、`@keydown`、`@mouseenter`、`@mouseleave`。

**传参**：

```vue
<button @click="sayHello('小明')">打招呼</button>

<script setup>
function sayHello(name) {
  alert('你好，' + name)
}
</script>
```

**获取原生事件对象**：

```vue
<!-- 不传参时，函数自动接收 event -->
<button @click="handleClick">点我</button>

<!-- 传参时，用 $event 显式传入 -->
<button @click="handleClick($event, '额外参数')">点我</button>

<script setup>
function handleClick(event, extra) {
  console.log(event.target)  // 被点击的按钮元素
  console.log(extra)
}
</script>
```

---

### 步骤 7：练习 —— 用模板语法改造 BlogList

> **我在做什么？** 把 BlogList 从写死两篇 `<article>` 改造为数据驱动渲染。

打开 `src/components/BlogList.vue`，把整个文件替换为：

```vue
<template>
  <main class="blog-list">
    <!-- 用 v-for 循环渲染文章列表 -->
    <article v-for="post in posts" :key="post.id" class="post-card">
      <h2>{{ post.title }}</h2>
      <p class="post-meta">
        发布于 {{ post.date }} · 标签：{{ post.tags.join(', ') }}
      </p>
      <p class="post-excerpt">{{ post.excerpt }}</p>
      <a :href="post.link" class="read-more">阅读全文 →</a>
    </article>
  </main>
</template>

<script setup>
import { ref } from 'vue'

// 文章数据放在数组里，想加文章？往数组里 push 就行！
const posts = ref([
  {
    id: 1,
    title: 'Vue3 入门指南',
    date: '2026-06-01',
    tags: ['Vue', '前端'],
    excerpt: 'Vue3 是 Vue.js 的最新主版本，带来了 Composition API、更快的渲染速度和更好的 TypeScript 支持...',
    link: '#'
  },
  {
    id: 2,
    title: 'JavaScript 异步编程',
    date: '2026-05-28',
    tags: ['JavaScript'],
    excerpt: '从回调函数到 Promise，再到 async/await，一文搞懂 JavaScript 的异步编程演进史...',
    link: '#'
  },
  {
    id: 3,
    title: 'CSS Grid 布局实战',
    date: '2026-05-20',
    tags: ['CSS', '布局'],
    excerpt: '告别浮动和定位的痛苦，CSS Grid 让你用最简单的代码实现最复杂的网页布局...',
    link: '#'
  }
])
</script>

<style scoped>
.blog-list {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}
.post-card {
  background: white;
  border-radius: 8px;
  padding: 24px;
  margin-bottom: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}
.post-card h2 {
  margin: 0 0 8px;
  color: #35495e;
}
.post-meta {
  color: #999;
  font-size: 0.9em;
  margin-bottom: 12px;
}
.post-excerpt {
  color: #555;
  line-height: 1.6;
}
.read-more {
  color: #42b883;
  text-decoration: none;
  font-weight: bold;
}
.read-more:hover {
  text-decoration: underline;
}
</style>
```

保存，浏览器里应该看到**三篇**文章（而不是之前的两篇）。

> ✅ **做得对不对？** 页面显示三篇文章。试试在 `posts` 数组里添加第四篇文章，保存后页面立刻出现第四篇。

**效果对比**：

| | 改造前（08 教程） | 改造后（09 教程） |
|---|---|---|
| 文章数量 | 写死 2 篇 | 由 `posts` 数组长度决定 |
| 添加文章 | 复制粘贴大段 HTML | `posts` 数组里加一个对象 |
| 修改内容 | 在 HTML 里找对应的 `<h2>` 改文字 | 改数组里的 `title` 字段 |
| 标签显示 | 写死 | `.join(', ')` 自动拼接 |

---

## 五、七大指令速查表

| 指令 | 简写 | 作用 | 示例 |
|---|---|---|---|
| `{{ }}` | — | 插值，显示变量值 | `{{ username }}` |
| `v-bind` | `:` | 动态绑定 HTML 属性 | `:href="url"`、`:class="{ active: isActive }"` |
| `v-if` | — | 条件为真时才渲染（移除 DOM） | `v-if="isLogin"` |
| `v-else` | — | `v-if` 的 else 分支 | `v-else` |
| `v-show` | — | 条件为假时隐藏（`display: none`） | `v-show="isVisible"` |
| `v-for` | — | 循环渲染列表 | `v-for="item in items" :key="item.id"` |
| `v-model` | — | 表单双向绑定 | `v-model="username"` |
| `v-on` | `@` | 监听事件 | `@click="handleClick"`、`@input="onInput"` |

---

## 六、小结

| 你学了什么 | 核心技巧 |
|---|---|
| `{{ }}` 插值 | 双大括号显示变量，里面可以写 JS 表达式但不能写语句 |
| `v-bind` / `:` | 属性值动态化，`:class` 对象语法最常用 |
| `v-if` / `v-show` | **频繁切换用 `v-show`，不常变用 `v-if`** |
| `v-for` | 循环渲染数组，**`:key` 必加**，用唯一 ID 不要用 index |
| `v-model` | 表单数据自动同步，本质是 `:value` + `@input` 的语法糖 |
| `v-on` / `@` | `@click`、`@input`、`@submit`，函数可传参，用 `$event` 获取原生事件 |
| 实战 | 把 BlogList 从写死 HTML 改造成数据驱动渲染 |

---

## 七、术语附录

| 术语 | 解释 |
|---|---|
| **插值（Interpolation）** | `{{ }}` 语法，把 JS 变量的值「插入」到 HTML 里显示 |
| **`v-bind`** | 动态绑定 HTML 属性。简写 `:`。比如 `:href="url"` 等价于 `v-bind:href="url"` |
| **`v-if`** | 条件渲染指令，false 时元素从 DOM 中彻底移除 |
| **`v-show`** | 条件显示指令，false 时元素保留在 DOM 中，只是加了 `display: none` |
| **`v-for`** | 列表渲染指令，循环数组生成 HTML 元素。必须配 `:key` 使用 |
| **`v-model`** | 表单双向绑定指令。输入框的值和 JS 变量自动同步，一方变另一方跟着变 |
| **`v-on`** | 事件监听指令。简写 `@`。比如 `@click="fn"` 等价于 `v-on:click="fn"` |
| **双向绑定** | 数据 → 视图 和 视图 → 数据 两个方向都自动同步。`v-model` 是双向绑定的典型实现 |

---

## 八、下一步建议

模板语法学完了，但你可能注意到我们用了 `ref()` 来包装数据。为什么 `const count = 0` 不行，必须 `const count = ref(0)`？下一篇揭开谜底！

👉 继续阅读：**10-响应式数据：ref与reactive**