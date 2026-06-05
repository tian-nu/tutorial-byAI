# 10 - 响应式数据：ref 与 reactive

- **对应文档版本**：requirements.md v1.0
- **适用环境**：Vue3 + Vite 项目（已有 08-09 教程的组件结构）
- **读者角色**：前端初学者
- **预计耗时**：新手 45 分钟 / 熟手 20 分钟
- **前置教程**：09-模板语法：Vue的HTML增强
- **可视化**：无

---

## 一、目标与完成效果

**一句话目标**：理解 Vue 的响应式原理，掌握 `ref`、`reactive`、`computed`、`watch` 四大响应式工具。

**完成后的可观测效果**：
- BlogList 的文章数据用 `ref` 管理，点击文章可以切换「已读/未读」状态
- 能说出 `ref` vs `reactive` 的区别和各自适用场景
- 理解为什么普通变量不能驱动页面更新，而响应式变量可以

---

## 二、前置条件

- 已完成 09 教程，BlogList 用 `v-for` + `ref` 数组渲染
- 开发服务器能正常运行

**环境验证命令**：
```bash
cd blog-frontend && npm run dev
```

---

## 三、比喻：普通变量 vs 响应式变量

这是 Vue 最核心的概念，理解它就理解了 Vue 的一半。

### 3.1 普通 JavaScript 变量 = 便签纸

```javascript
let count = 0
count = 5
// 你改了 count，但页面上的 <span>{{ count }}</span> 不会自动变
```

普通变量就像一张便签纸：你在上面写了 `count = 0`，然后用这张纸显示在页面上。后来你把纸上内容划掉改成 `count = 5`——**但页面不知道你改过了**，它手里拿的还是原来的复印件。

### 3.2 响应式变量 = 电子屏幕

```javascript
const count = ref(0)
count.value = 5
// Vue 检测到 count 变了 → 自动更新页面上所有用到 count 的地方
```

响应式变量像一个**联网的电子屏幕**：你改了数据源（服务器），所有显示这块屏幕的地方（页面上的各个角落）自动刷新。你不用给每个屏幕发通知，Vue 帮你发了。

> 🤔 **想多一点**：Vue 的响应式系统本质是「数据劫持 + 发布订阅」。当你用 `ref()` 包装一个值时，Vue 给这个值套了一层代理。任何代码读取 `count.value`，Vue 都知道「哦，有地方依赖这个值」；任何代码修改 `count.value`，Vue 都会通知所有依赖的地方「嘿，你依赖的值变了，赶紧更新」。这就是「响应式」的本质：数据变化时自动响应。

---

## 四、分步操作

### 步骤 1：`ref()` —— 包装单值

> **我在做什么？** 用 `ref()` 包装一个基础类型的数据，让它变成响应式的。

`ref()` 用于包装**基本类型**：字符串、数字、布尔值。

```vue
<template>
  <div>
    <p>计数：{{ count }}</p>
    <button @click="increment">+1</button>
  </div>
</template>

<script setup>
import { ref } from 'vue'

// 创建响应式变量 count，初始值 0
const count = ref(0)

function increment() {
  // ⚠️ 在 JS 里必须用 .value 读写
  count.value++
  console.log('当前计数:', count.value)
}
</script>
```

**关键规则**：

| 在什么地方 | 怎么写 | 为什么 |
|---|---|---|
| `<script setup>` 里 | `count.value` | JS 里 ref 是个对象，真实值存在 `.value` 属性里 |
| `<template>` 里 | `{{ count }}` | 模板里 Vue **自动解包**，不需要 `.value` |

```javascript
// ❌ 错误：在 JS 里忘了 .value
count++  // 没用，count 是个对象，不是数字

// ✅ 正确
count.value++  // 修改 ref 真正的值
```

> 🤔 **想多一点**：为什么模板里自动解包？因为 Vue 知道在模板里你几乎总是想用 `.value`，所以做了自动处理。这是一个体贴的设计，但也容易让新手困惑——「为什么同一个变量，模板里不用 `.value`，JS 里要用？」记住这个规律就行。

---

### 步骤 2：`reactive()` —— 包装对象

> **我在做什么？** 用 `reactive()` 包装一个对象，让整个对象变成响应式的。

`reactive()` 用于包装**对象类型**（Object、Array）。

```vue
<template>
  <div>
    <p>姓名：{{ user.name }}</p>
    <p>年龄：{{ user.age }}</p>
    <button @click="haveBirthday">过生日 +1岁</button>
  </div>
</template>

<script setup>
import { reactive } from 'vue'

// reactive 包装对象，不需要 .value
const user = reactive({
  name: '小明',
  age: 18
})

function haveBirthday() {
  user.age++  // ✅ 直接读写，不需要 .value
}
</script>
```

**关键区别**：

```javascript
// ref 包装数字
const count = ref(0)
count.value++  // ⚠️ 需要 .value

// reactive 包装对象
const state = reactive({ count: 0 })
state.count++  // ✅ 不需要 .value，直接访问属性
```

但 `reactive` 有两个限制：
1. **只能包装对象**（Object、Array、Map、Set），不能包装基本类型。`reactive(0)` 报错。
2. **不能整体替换**。`state = reactive({ count: 1 })` 会失去响应式（因为变量指向了新的非响应式对象）。

---

### 步骤 3：对比口诀

> **单值 `ref`，对象 `reactive`，拿不准就 `ref`。**

| | `ref()` | `reactive()` |
|---|---|---|
| **适用类型** | 基本类型（字符串、数字、布尔）**也可以包装对象** | 只能包装对象（Object、Array） |
| **JS 中读写** | 需要 `.value` | 直接读写属性，不需要 `.value` |
| **模板中** | 自动解包，不需要 `.value` | 直接使用 |
| **整体替换** | ✅ 可以 `refObj.value = newObj` | ❌ 不能 `state = newObj`，会失去响应式 |
| **解构** | ❌ 解构会失去响应式 | ❌ 解构会失去响应式 |
| **推荐度** | ⭐⭐⭐⭐⭐ 官方主推 | ⭐⭐⭐ 有局限 |

```javascript
// 拿不准？用 ref 就对了

// ✅ ref 也可以包装对象
const posts = ref([
  { id: 1, title: '文章1' },
  { id: 2, title: '文章2' }
])
// JS 里这样访问：posts.value[0].title
// 模板里这样访问：posts[0].title（自动解包了第一层）
```

> 🤔 **想多一点**：Vue 官方实际上更推荐用 `ref` 而不是 `reactive`。因为 `ref` 更灵活（支持基本类型和对象），而且 `ref` 的整体替换功能在从 API 获取新数据时非常方便——直接 `posts.value = 新数据` 就行。`reactive` 你得一个个属性改，或者用 `Object.assign`。

---

### 步骤 4：`computed` —— 计算属性，自动缓存

> **我在做什么？** 基于已有数据计算出一个新值，而且只在依赖变了时才重新计算。

```vue
<template>
  <div>
    <p>未读文章：{{ unreadCount }} 篇</p>
    <p>文章总数：{{ posts.length }} 篇</p>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const posts = ref([
  { id: 1, title: '文章1', read: true },
  { id: 2, title: '文章2', read: false },
  { id: 3, title: '文章3', read: false }
])

// computed 自动追踪依赖（posts.value），依赖不变就返回缓存
const unreadCount = computed(() => {
  return posts.value.filter(p => !p.read).length
})
</script>
```

`computed` vs 普通函数：

```javascript
// ❌ 用普通函数：每次访问都重新计算
function getUnreadCount() {
  return posts.value.filter(p => !p.read).length
}

// ✅ 用 computed：依赖没变就返回缓存，不重复计算
const unreadCount = computed(() => {
  return posts.value.filter(p => !p.read).length
})
```

**性能差异**：如果 `posts` 有一万篇文章，`computed` 只在数据变化时算一次，普通函数每次访问都算一次。这就是缓存的威力。

**computed 也可以有 setter**（双向计算）：

```javascript
const fullName = computed({
  get: () => firstName.value + ' ' + lastName.value,
  set: (val) => {
    const parts = val.split(' ')
    firstName.value = parts[0]
    lastName.value = parts[1]
  }
})
// fullName.value = '张三丰' → firstName = '张三丰', lastName = ''
```

---

### 步骤 5：`watch` —— 侦听数据变化

> **我在做什么？** 当某个数据变化时，自动执行一段逻辑（比如保存到 localStorage、发请求、打印日志）。

```vue
<template>
  <div>
    <input v-model="keyword" placeholder="搜索文章" />
    <p>搜索关键词：{{ keyword }}</p>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'

const keyword = ref('')

// watch：侦听 keyword 的变化
watch(keyword, (newVal, oldVal) => {
  console.log(`关键词从 "${oldVal}" 变为 "${newVal}"`)
  // 这里可以调用搜索 API，或过滤列表
})
</script>
```

**侦听多个数据**：

```javascript
const firstName = ref('')
const lastName = ref('')

// 用一个数组同时监听多个
watch([firstName, lastName], ([newFirst, newLast], [oldFirst, oldLast]) => {
  console.log(`姓名从 ${oldFirst} ${oldLast} 变为 ${newFirst} ${newLast}`)
})
```

**侦听 reactive 对象的属性**：

```javascript
const user = reactive({ name: '小明', age: 18 })

// ⚠️ reactive 对象的属性必须用 getter 函数包裹
watch(() => user.age, (newAge, oldAge) => {
  console.log(`年龄从 ${oldAge} 变为 ${newAge}`)
})
```

**立即执行 + 深度监听**：

```javascript
watch(keyword, (newVal) => {
  console.log('关键词变化:', newVal)
}, {
  immediate: true,  // 组件创建时立即执行一次
  deep: true        // 深度监听对象内部变化（仅对 reactive 或 ref 包裹的对象）
})
```

> 🤔 **想多一点**：什么时候用 `computed`，什么时候用 `watch`？**computed 用于「计算一个新值去显示」**，比如根据文章列表算出未读数；**watch 用于「数据变了要执行一个动作」**，比如搜索词变了去调 API、用户登出了清空缓存。`computed` 有返回值（给模板用），`watch` 没有返回值（执行副作用）。

---

### 步骤 6：练习 —— 文章列表用 ref，点击切换已读状态

> **我在做什么？** 给 BlogList 加上「已读/未读」状态切换功能。

打开 `src/components/BlogList.vue`，在 `posts` 数据里每个文章加上 `read` 字段，并添加点击切换功能：

```vue
<template>
  <main class="blog-list">
    <!-- 未读数在列表顶部显示 -->
    <p class="unread-info">
      📖 共 {{ posts.length }} 篇文章，
      未读 {{ unreadCount }} 篇
    </p>

    <article
      v-for="post in posts"
      :key="post.id"
      class="post-card"
      :class="{ read: post.read }"
      @click="toggleRead(post)"
    >
      <h2>
        <!-- 已读的文章标题前加 ✅ -->
        <span v-if="post.read">✅</span>
        {{ post.title }}
      </h2>
      <p class="post-meta">
        发布于 {{ post.date }} · 标签：{{ post.tags.join(', ') }}
      </p>
      <p class="post-excerpt">{{ post.excerpt }}</p>
      <a :href="post.link" class="read-more" @click.stop>阅读全文 →</a>
    </article>
  </main>
</template>

<script setup>
import { ref, computed } from 'vue'

const posts = ref([
  {
    id: 1,
    title: 'Vue3 入门指南',
    date: '2026-06-01',
    tags: ['Vue', '前端'],
    excerpt: 'Vue3 是 Vue.js 的最新主版本...',
    link: '#',
    read: false    // 新增：已读状态
  },
  {
    id: 2,
    title: 'JavaScript 异步编程',
    date: '2026-05-28',
    tags: ['JavaScript'],
    excerpt: '从回调函数到 Promise...',
    link: '#',
    read: false
  },
  {
    id: 3,
    title: 'CSS Grid 布局实战',
    date: '2026-05-20',
    tags: ['CSS', '布局'],
    excerpt: '告别浮动和定位的痛苦...',
    link: '#',
    read: true    // 这篇默认已读
  }
])

// computed：自动计算未读文章数
const unreadCount = computed(() => {
  return posts.value.filter(p => !p.read).length
})

// 点击文章切换已读/未读
function toggleRead(post) {
  post.read = !post.read
}
</script>

<style scoped>
.blog-list {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}
.unread-info {
  color: #999;
  font-size: 0.95em;
  margin-bottom: 16px;
}
.post-card {
  background: white;
  border-radius: 8px;
  padding: 24px;
  margin-bottom: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  cursor: pointer;
  transition: all 0.2s;
}
.post-card:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
}
/* 已读文章样式：半透明 + 左边框变色 */
.post-card.read {
  opacity: 0.6;
  border-left: 4px solid #42b883;
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

> ✅ **做得对不对？** 
> - 点击文章卡片，该文章的透明度变化（已读变半透明），标题前出现 ✅
> - 顶部「未读 N 篇」的数字自动更新
> - 点击「阅读全文」不会触发已读切换（因为加了 `@click.stop`）

---

## 四、完整代码清单

### `src/components/BlogList.vue`（最终状态）

```vue
<template>
  <main class="blog-list">
    <p class="unread-info">
      📖 共 {{ posts.length }} 篇文章，
      未读 {{ unreadCount }} 篇
    </p>

    <article
      v-for="post in posts"
      :key="post.id"
      class="post-card"
      :class="{ read: post.read }"
      @click="toggleRead(post)"
    >
      <h2>
        <span v-if="post.read">✅</span>
        {{ post.title }}
      </h2>
      <p class="post-meta">
        发布于 {{ post.date }} · 标签：{{ post.tags.join(', ') }}
      </p>
      <p class="post-excerpt">{{ post.excerpt }}</p>
      <a :href="post.link" class="read-more" @click.stop>阅读全文 →</a>
    </article>
  </main>
</template>

<script setup>
import { ref, computed } from 'vue'

const posts = ref([
  {
    id: 1,
    title: 'Vue3 入门指南',
    date: '2026-06-01',
    tags: ['Vue', '前端'],
    excerpt: 'Vue3 是 Vue.js 的最新主版本...',
    link: '#',
    read: false
  },
  {
    id: 2,
    title: 'JavaScript 异步编程',
    date: '2026-05-28',
    tags: ['JavaScript'],
    excerpt: '从回调函数到 Promise...',
    link: '#',
    read: false
  },
  {
    id: 3,
    title: 'CSS Grid 布局实战',
    date: '2026-05-20',
    tags: ['CSS', '布局'],
    excerpt: '告别浮动和定位的痛苦...',
    link: '#',
    read: true
  }
])

const unreadCount = computed(() => {
  return posts.value.filter(p => !p.read).length
})

function toggleRead(post) {
  post.read = !post.read
}
</script>

<style scoped>
.blog-list {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}
.unread-info {
  color: #999;
  font-size: 0.95em;
  margin-bottom: 16px;
}
.post-card {
  background: white;
  border-radius: 8px;
  padding: 24px;
  margin-bottom: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  cursor: pointer;
  transition: all 0.2s;
}
.post-card:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
}
.post-card.read {
  opacity: 0.6;
  border-left: 4px solid #42b883;
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

---

## 五、小结

| 工具 | 用途 | 口诀 |
|---|---|---|
| `ref()` | 包装任意类型为响应式 | **JS 里用 `.value`，模板里自动解包** |
| `reactive()` | 包装对象为响应式 | **直接读写属性，但不能整体替换** |
| `computed()` | 基于已有数据计算新值 | **有缓存，依赖不变不重复算** |
| `watch()` | 侦听数据变化，执行副作用 | **watch 做事，computed 算值** |
| 选择策略 | — | **单值 ref，对象也 ref，拿不准就 ref** |

---

## 六、术语附录

| 术语 | 解释 |
|---|---|
| **ref** | Vue3 的响应式 API，用于创建一个响应式引用。`ref(0)` 返回 `{ value: 0 }` 的代理对象。JS 里用 `.value` 读写，模板里自动解包 |
| **reactive** | Vue3 的响应式 API，用于创建一个响应式对象。直接读写属性不需要 `.value`，但只能用于对象类型，且不能整体替换 |
| **computed** | 计算属性。基于已有响应式数据产生派生值，自动追踪依赖并缓存结果。依赖不变时不会重新计算 |
| **watch** | 侦听器。监视一个或多个响应式数据的变化，变化时执行回调函数。适合执行副作用（调 API、存 localStorage 等） |
| **响应式（Reactivity）** | Vue 的核心机制。数据变化时，所有依赖该数据的地方自动更新。类比：联网电子屏幕，数据源变了画面自动刷新 |

---

## 七、下一步建议

现在数据都在各自组件里管着，但 BlogList 和 BlogHeader 之间还没有交流。下一篇我们学 **Props**——让组件之间可以传数据，实现父子组件通信。

👉 继续阅读：**11-Props：组件之间传话**