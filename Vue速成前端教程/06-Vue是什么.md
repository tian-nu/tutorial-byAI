# 06 - Vue 是什么？

- **对应文档版本**：requirements.md v1.0
- **适用环境**：任意浏览器、Node.js 18+（本教程不涉及编码，纯概念讲解）
- **读者角色**：前端初学者
- **预计耗时**：新手 25 分钟 / 熟手 10 分钟
- **前置教程**：05-从零搭建静态博客页面（HTML + CSS）
- **可视化**：无

---

## 一、目标与完成效果

**一句话目标**：理解 Vue 解决了什么问题，以及它的核心思想是什么。

**完成后的可观测效果**：
- 能用一句大白话向同事解释「Vue 到底干了啥」
- 能画出 MVVM 模式的三层关系图
- 能说出 Vue3 相比 jQuery 的本质区别
- 知道 Vue 生态里每个工具分别干什么用

---

## 二、前置条件

- 已经手写过至少一个 HTML + CSS 页面（对应 05 教程），体会过手动改 DOM 的痛苦
- 不需要安装任何东西，本教程纯文字 + 插图描述

---

## 三、回顾 05 痛点：你手动改 DOM，Vue 帮你自动改

先回忆一下 05 教程里你做博客页面的经历。

假设页面上有一个文章标题 `<h1 id="title">旧标题</h1>`，你想把它改成「新标题」。用原生 JS 你得这么写：

```javascript
// ❌ 原生 JS：手动找到 DOM，手动改内容
document.getElementById('title').innerText = '新标题';
```

这只是一个标题。如果你的博客有 20 篇文章，每篇文章有标题、摘要、日期、标签，你要分别去找到每一个 DOM 节点，一个一个改。

> 🎯 **痛点总结**：你花大量时间写「怎么找到元素」「怎么改元素」这种重复代码，而不是写「数据应该是什么」。

Vue 的思路正好反过来：**你把数据准备好，Vue 自动帮你把数据渲染到页面上。数据变了，页面自动跟着变。** 你不用再写 `document.getElementById` 了。

---

## 四、Vue 核心理念：你只管数据，Vue 管页面

用一句人话概括 Vue 的核心哲学：

> **你告诉 Vue「我的数据长这样」，Vue 负责把数据变成屏幕上能看的页面。数据变了，页面自动刷新，不用你操心。**

打个比方：

| 传统方式（jQuery/原生JS） | Vue 方式 |
|---|---|
| 你是一个**装修工人**，亲自搬砖、刷墙、换灯泡，什么都要自己动手 | 你是一个**设计师**，只需要在图纸上标注「这里放沙发，那里放电视」，施工队（Vue）自动帮你布置好 |
| 数据变了 → 你手动找到那个 DOM 节点 → 手动改内容 | 数据变了 → Vue 自动找到对应 DOM → 自动更新 |

**这就是「声明式渲染」**：你声明数据长什么样，Vue 负责渲染。你不需要告诉 Vue「怎么」渲染，只需要告诉它「渲染什么」。

> 🤔 **想多一点**：声明式 vs 命令式。命令式 = 你做菜时一步步写「切菜→热油→下锅→翻炒」，声明式 = 你告诉厨师「我要一盘宫保鸡丁」，厨师自己搞定。Vue 就是那个厨师。

---

## 五、MVVM 模式：Model → ViewModel → View

Vue 的架构基于 **MVVM** 模式，这是理解 Vue 的关键。

```
┌─────────┐      ┌──────────────┐      ┌─────────┐
│  Model  │ ───→ │  ViewModel   │ ───→ │  View   │
│  (数据)  │ ←─── │ (Vue 实例)    │ ←─── │  (页面)  │
└─────────┘      └──────────────┘      └─────────┘
```

三个角色分别是什么？

| 层 | 全称 | 你的代码里是什么 | 比喻 |
|---|---|---|---|
| **M**odel | 数据层 | JavaScript 变量/对象（比如 `{ title: '你好' }`） | 菜谱上的食材清单 |
| **V**iewModel | 视图模型层 | Vue 实例（你写的 `<script setup>` 里的逻辑） | 厨师，把食材加工成菜 |
| **V**iew | 视图层 | `<template>` 里的 HTML | 端上桌的菜 |

**数据流向**：
- Model 变了 → ViewModel 自动检测 → View 自动更新（**数据驱动视图**）
- 用户在 View 上操作（点按钮、输入文字）→ ViewModel 捕获 → Model 更新（**事件驱动数据**）

这就是 **双向绑定** 的底层原理。Vue 的 ViewModel 层像一个「传话筒」，Model 和 View 互相不直接通信，都通过 ViewModel 中转。

> 🤔 **想多一点**：MVVM 名字听起来唬人，其实就是「数据」和「页面」之间加了一个中间人。这个中间人负责两件事：① 数据变了通知页面更新；② 页面操作了通知数据更新。没有这个中间人，你就得自己当传话筒，累死。

---

## 六、Vue3 特点：Composition API 与 `<script setup>`

Vue3 引入了两大革新：

### 6.1 Composition API（组合式 API）

Vue2 用的是 Options API（选项式 API），所有逻辑按 `data`、`methods`、`computed` 分类。一个功能的代码散落在不同选项里：

```javascript
// ❌ Vue2 Options API：一个功能的代码散落各处
export default {
  data() {
    return { count: 0, name: '' }
  },
  methods: {
    increment() { this.count++ },
    setName(n) { this.name = n }
  }
}
```

Vue3 的 Composition API 让你**按功能组织代码**，一个功能的逻辑写在一起：

```javascript
// ✅ Vue3 Composition API：按功能归类
const count = ref(0)          // 计数器功能
const increment = () => count.value++

const name = ref('')          // 名字功能
const setName = (n) => name.value = n
```

### 6.2 `<script setup>` 语法糖

`<script setup>` 是 Composition API 的「懒人版」，省去大量样板代码：

| | 不用 `<script setup>` | 用 `<script setup>` |
|---|---|---|
| 导入组件 | 还要手动 `components: { }` 注册 | `import` 即自动注册 |
| 定义 Props | `props: { }` 选项 + `setup(props)` | `defineProps()` 一行搞定 |
| 导出变量 | 需要 `return { }` 暴露给模板 | 所有顶层变量自动暴露 |
| 代码量 | 啰嗦 | 简洁 |

**本系列教程全部使用 `<script setup>` + Composition API**，这是 Vue3 官方推荐的写法。

---

## 七、与 jQuery 对比：手动 DOM vs 声明式渲染

这是一个经典对比，帮助理解 Vue 的革命性：

**场景**：页面上有一个计数器和一个按钮，点按钮数字 +1。

### jQuery 写法（命令式）

```javascript
// ❌ jQuery：手动操作 DOM
let count = 0;
$('#btn').on('click', function() {
  count++;
  $('#display').text(count);  // 手动更新显示
});
```

### Vue 写法（声明式）

```vue
<template>
  <div>
    <span>{{ count }}</span>           <!-- 声明：这里显示 count -->
    <button @click="count++">+1</button> <!-- 声明：点击时 count+1 -->
  </div>
</template>

<script setup>
import { ref } from 'vue'
const count = ref(0)  // 声明：数据初始为 0
</script>
```

**关键区别**：

| 维度 | jQuery（命令式） | Vue（声明式） |
|---|---|---|
| **DOM 操作** | 你手动 `$('#xxx').text()` | 你不知道 DOM 节点在哪，Vue 自己找 |
| **数据同步** | 数据变了 → 你记得更新 DOM，忘了就出 Bug | 数据变了 → 页面自动更新 |
| **代码可读性** | 操作步骤多，逻辑散落 | 模板直接描述结果，一目了然 |
| **维护成本** | 改一个 UI 可能要改多处 JS | 改数据即可，模板自动反映 |

> 💡 **一句话总结**：jQuery 让你告诉浏览器「**怎么**做」，Vue 让你告诉浏览器「**要什么**」。前者累人，后者省心。

---

## 八、Vue 生态：全家桶一览

Vue 本身只负责**视图层**（把数据渲染成页面）。但一个完整的 Web 应用还需要：

| 需求 | Vue 官方方案 | 什么用 | 会不会在本教程出现 |
|---|---|---|---|
| **页面路由**（多个页面跳转） | **Vue Router** | `/home`、`/about` 等 URL 对应不同页面组件 | ✅ 会 |
| **状态管理**（多个组件共享数据） | **Pinia** | 用户登录状态、购物车数据，全局共享 | ✅ 会 |
| **构建工具**（打包、开发服务器） | **Vite** | 启动开发服务器、热更新、打包上线 | ✅ 已经在用 |
| **全栈框架**（SSR、文件路由） | **Nuxt** | 服务端渲染、SEO 友好、约定式路由 | ❌ 本系列不涉及 |

> 🤔 **想多一点**：Nuxt 之于 Vue，就像 Next.js 之于 React。它是一套「 batteries-included 」的全栈框架，适合做官网、博客等需要 SEO 的项目。入门阶段不用碰它，先把 Vue 核心搞懂。

---

## 九、小结

| 你学了什么 | 一句话 |
|---|---|
| 为什么需要 Vue | 手动改 DOM 痛苦且易出错，Vue 自动帮你同步数据与页面 |
| Vue 的哲学 | 声明式渲染：你声明数据长什么样，Vue 负责渲染 |
| MVVM 模式 | Model（数据）↔ ViewModel（Vue）↔ View（页面），双向自动同步 |
| Vue3 特色 | Composition API 按功能组织代码 + `<script setup>` 省去样板代码 |
| vs jQuery | jQuery 命令式手动改 DOM，Vue 声明式自动同步 |
| Vue 生态 | Router（路由）、Pinia（状态管理）、Vite（构建）、Nuxt（全栈框架） |

---

## 十、术语附录

| 术语 | 解释 |
|---|---|
| **MVVM** | Model-View-ViewModel，一种架构模式。Model 是数据，View 是页面，ViewModel（Vue 实例）是中间人，让数据与页面自动同步 |
| **声明式渲染** | 你声明「数据长什么样」，框架负责把数据渲染成页面。与之相对的是「命令式」——你一步步告诉浏览器怎么改 DOM |
| **Composition API** | Vue3 引入的 API 风格，允许按功能（而非选项类型）组织代码。`ref()`、`reactive()`、`computed()` 都是它的成员 |
| **`<script setup>`** | Vue3 的语法糖，写在 `.vue` 文件 `<script>` 标签里的 `setup` 属性。让你少写大量样板代码，`import` 的组件自动可用，顶层变量自动暴露给模板 |

---

## 十一、下一步建议

现在你已经知道 Vue 是干什么的了，下一步我们动手：安装 Node.js，用 Vite 创建你的第一个 Vue 项目！

👉 继续阅读：**07-环境搭建：Node.js + Vite 创建 Vue 项目**