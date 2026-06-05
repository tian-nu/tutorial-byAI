# 11 - Props：组件之间传话

- **对应文档版本**：requirements.md v1.0
- **适用环境**：Vue3 + Vite 项目（已有 08-10 教程的组件结构）
- **读者角色**：前端初学者
- **预计耗时**：新手 45 分钟 / 熟手 20 分钟
- **前置教程**：10-响应式数据：ref与reactive
- **可视化**：无

---

## 一、目标与完成效果

**一句话目标**：掌握 Vue 组件通信的两大核心机制——Props（父传子）和 Emit（子传父）。

**完成后的可观测效果**：
- BlogList 拆成 BlogList（父） + BlogPost（子），BlogPost 通过 Props 接收文章数据
- 子组件（BlogPost）点击「标记已读」按钮，通过 Emit 通知父组件更新数据
- 能说出单向数据流的含义，知道为什么子组件不能修改 Props

---

## 二、前置条件

- 已完成 10 教程，BlogList 有 `ref` 数据 + `computed` 未读数 + 点击切换已读
- 开发服务器能正常运行

**环境验证命令**：
```bash
cd blog-frontend && npm run dev
```

---

## 三、比喻：父子组件通信

### 3.1 Props = 父母给孩子零花钱

父组件给子组件传数据，就像**父母给孩子零花钱**：

- 父母（父组件）决定给多少钱、给什么（数据内容）
- 孩子（子组件）可以花（使用、显示），但**不能自己印钞票**（不能修改）

> 💡 **这就是「单向数据流」**：数据只能从父流向子。子组件要用数据？找父组件要。子组件想改数据？得「打电话叫家长」——也就是 Emit。

### 3.2 Emit = 孩子打电话叫家长

子组件想通知父组件做事（比如「文章被点击了」「用户提交了表单」），发一个**事件**出去：

- 孩子（子组件）打电话：「爸，我想买东西！」（emit 一个事件）
- 家长（父组件）听到后决定怎么办：「好，给你钱」或者「不行」（处理事件）

> 🤔 **想多一点**：为什么不让子组件直接修改 Props？因为如果数据可以双向随意改，出了 Bug 你根本不知道是谁改的——父改了子，子改了父，循环下去谁也说不清。单向数据流让数据流向可追踪：永远是从上到下，要找 Bug 就顺着组件树往上找。

---

## 四、分步操作

### 步骤 1：Props —— 父传子

> **我在做什么？** 父组件通过 Props 把数据传给子组件。

**语法三步走**：

① **父组件**：在子组件标签上用 `:属性名="数据"` 绑定传递：

```vue
<template>
  <!-- 父组件里 -->
  <BlogPost :title="post.title" :content="post.content" />
</template>
```

② **子组件**：用 `defineProps()` 声明接收哪些属性：

```vue
<script setup>
// 子组件里
const props = defineProps({
  title: String,   // 期望 title 是字符串
  content: String  // 期望 content 是字符串
})
</script>
```

③ **子组件**：在模板或 JS 里使用接收到的值：

```vue
<template>
  <h2>{{ title }}</h2>
  <p>{{ content }}</p>
</template>
```

**完整示例**——创建一个显示单篇文章的 `BlogPost.vue`：

在 `src/components/BlogPost.vue` 新建：

```vue
<template>
  <article class="post-card">
    <h2>{{ title }}</h2>
    <p class="post-meta">
      发布于 {{ date }} · 标签：{{ tags.join(', ') }}
    </p>
    <p class="post-excerpt">{{ excerpt }}</p>
    <a :href="link" class="read-more">阅读全文 →</a>
  </article>
</template>

<script setup>
// 声明接收的 Props，带类型校验
const props = defineProps({
  title: String,
  date: String,
  tags: Array,
  excerpt: String,
  link: String
})
</script>

<style scoped>
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

> ✅ **做得对不对？** `BlogPost.vue` 创建成功，没有红色波浪线。

---

### 步骤 2：父组件用 Props 传数据

> **我在做什么？** 修改 `BlogList.vue`，让它用 `BlogPost` 子组件代替自己手写 `<article>`。

打开 `src/components/BlogList.vue`，修改为：

```vue
<template>
  <main class="blog-list">
    <p class="unread-info">
      📖 共 {{ posts.length }} 篇文章，
      未读 {{ unreadCount }} 篇
    </p>

    <!-- 用 BlogPost 子组件代替手写 <article> -->
    <BlogPost
      v-for="post in posts"
      :key="post.id"
      :title="post.title"
      :date="post.date"
      :tags="post.tags"
      :excerpt="post.excerpt"
      :link="post.link"
    />
  </main>
</template>

<script setup>
import { ref, computed } from 'vue'
import BlogPost from './BlogPost.vue'  // 导入子组件

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
</style>
```

> ✅ **做得对不对？** 浏览器里文章列表正常显示，和之前样子一样，但现在是 BlogList 调用 BlogPost 子组件渲染的。

**发生了什么变化？**

```
以前：BlogList 自己写 <article> 标签 → 模板里一大堆 HTML
现在：BlogList 调用 <BlogPost> 传数据  → 模板很干净，只管循环和传数据
```

---

### 步骤 3：Props 类型校验 —— 让传参更安全

> **我在做什么？** 给 Props 加上类型校验、必填标记、默认值，让组件更健壮。

`defineProps` 有更详细的写法：

```vue
<script setup>
const props = defineProps({
  title: {
    type: String,       // 类型
    required: true      // 必填，不传会报警告
  },
  likes: {
    type: Number,
    default: 0          // 默认值，没传就用这个
  },
  tags: {
    type: Array,
    default: () => []   // ⚠️ 对象/数组的默认值必须用函数返回！
  },
  isPublished: {
    type: Boolean,
    default: false
  },
  author: {
    type: Object,
    default: () => ({ name: '匿名', avatar: '' })
  }
})
</script>
```

**类型支持**：`String`、`Number`、`Boolean`、`Array`、`Object`、`Date`、`Function`、`Symbol`。

> 🔴 **特别注意**：Array 和 Object 的 `default` 必须用**工厂函数**（箭头函数 `() => []` 或 `function() { return {} }`），不能直接写 `default: []`。因为直接写会导致所有组件实例共享同一个数组/对象引用，互相污染数据。

```javascript
// ❌ 错误：所有 BlogPost 实例共享同一个 tags 数组！
tags: { type: Array, default: [] }

// ✅ 正确：每个 BlogPost 实例调用函数拿到自己的 []
tags: { type: Array, default: () => [] }
```

---

### 步骤 4：单向数据流 —— 子组件不能改 Props

> **我在做什么？** 理解并遵守 Vue 的核心规则：子组件不能修改 Props。

```vue
<script setup>
const props = defineProps({ title: String })

// ❌ 严禁：直接修改 props
props.title = '新标题'  // Vue 会报警告：[Vue warn] Attempting to mutate prop "title"

// ✅ 正确：如果需要基于 props 做本地修改，复制一份到本地 ref
import { ref } from 'vue'
const localTitle = ref(props.title)  // 复制一份，你随便改 localTitle
</script>
```

**如果子组件确实需要修改数据怎么办？** → 用 Emit，通知父组件去改。

---

### 步骤 5：Emit —— 子传父

> **我在做什么？** 子组件通过 Emit 发事件，父组件监听事件并处理。

**三步走**：

① **子组件**：用 `defineEmits()` 声明要发的事件，然后调用：

```vue
<!-- BlogPost.vue -->
<template>
  <article class="post-card" :class="{ read: isRead }">
    <h2>{{ title }}</h2>
    <p>{{ excerpt }}</p>
    <button @click="markAsRead">✅ 标记已读</button>
  </article>
</template>

<script setup>
const props = defineProps({
  title: String,
  excerpt: String,
  isRead: Boolean
})

// 步骤①：声明要发的事件
const emit = defineEmits(['mark-read'])

// 步骤②：点击按钮时 emit
function markAsRead() {
  emit('mark-read')  // 发事件给父组件
}
</script>
```

② **父组件**：用 `@事件名="处理函数"` 监听：

```vue
<!-- BlogList.vue -->
<template>
  <BlogPost
    v-for="post in posts"
    :key="post.id"
    :title="post.title"
    :excerpt="post.excerpt"
    :is-read="post.read"
    @mark-read="handleMarkRead(post)"   <!-- 步骤③：监听子组件事件 -->
  />
</template>

<script setup>
// 步骤④：处理函数
function handleMarkRead(post) {
  post.read = !post.read  // 父组件拥有数据，父组件负责修改
}
</script>
```

**Emit 也可以传参数**：

```vue
<!-- 子组件 -->
<script setup>
const emit = defineEmits(['submit'])

function onSubmit() {
  emit('submit', { name: '小明', age: 18 })  // 第二个参数就是 payload
}
</script>

<!-- 父组件 -->
<template>
  <ChildForm @submit="handleSubmit" />
</template>

<script setup>
function handleSubmit(payload) {
  console.log(payload)  // { name: '小明', age: 18 }
}
</script>
```

> 🤔 **想多一点**：Emit 和 Props 加起来实现了完整的父子通信闭环。Props 向下传数据，Emit 向上传事件。这就像父母和孩子——父母给钱（Props），孩子有事打电话（Emit），但孩子不能自己翻父母钱包改金额（不能改 Props）。

---

### 步骤 6：练习 —— 把 BlogList 拆成 BlogList + BlogPost

> **我在做什么？** 完整重构：BlogList 只管数据和循环，BlogPost 只管单篇文章的渲染和交互。

#### 6.1 更新 `BlogPost.vue`（加入 Emit + read 状态）

```vue
<template>
  <article
    class="post-card"
    :class="{ read: isRead }"
    @click="$emit('toggle-read')"
  >
    <h2>
      <span v-if="isRead">✅</span>
      {{ title }}
    </h2>
    <p class="post-meta">
      发布于 {{ date }} · 标签：{{ tags.join(', ') }}
    </p>
    <p class="post-excerpt">{{ excerpt }}</p>
    <div class="post-actions">
      <a :href="link" class="read-more" @click.stop>阅读全文 →</a>
      <button class="toggle-btn" @click.stop="$emit('toggle-read')">
        {{ isRead ? '标记未读' : '标记已读' }}
      </button>
    </div>
  </article>
</template>

<script setup>
defineProps({
  title: { type: String, required: true },
  date: { type: String, required: true },
  tags: { type: Array, default: () => [] },
  excerpt: { type: String, default: '' },
  link: { type: String, default: '#' },
  isRead: { type: Boolean, default: false }
})

// 声明事件
defineEmits(['toggle-read'])
</script>

<style scoped>
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
  margin-bottom: 12px;
}
.post-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.read-more {
  color: #42b883;
  text-decoration: none;
  font-weight: bold;
}
.read-more:hover {
  text-decoration: underline;
}
.toggle-btn {
  background: #42b883;
  color: white;
  border: none;
  padding: 6px 14px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9em;
}
.toggle-btn:hover {
  background: #35a372;
}
</style>
```

#### 6.2 更新 `BlogList.vue`（用 BlogPost + 传 Props + 监听 Emit）

```vue
<template>
  <main class="blog-list">
    <p class="unread-info">
      📖 共 {{ posts.length }} 篇文章，
      未读 {{ unreadCount }} 篇
    </p>

    <BlogPost
      v-for="post in posts"
      :key="post.id"
      :title="post.title"
      :date="post.date"
      :tags="post.tags"
      :excerpt="post.excerpt"
      :link="post.link"
      :is-read="post.read"
      @toggle-read="toggleRead(post)"
    />
  </main>
</template>

<script setup>
import { ref, computed } from 'vue'
import BlogPost from './BlogPost.vue'

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
</style>
```

> ✅ **做得对不对？**
> - 页面显示三篇文章，样式正常
> - 点击文章卡片或「标记已读」按钮，状态切换正常
> - 点击「阅读全文」不会触发状态切换
> - 未读数自动更新

---

## 五、数据流全景图

```
┌─────────────────────────────────────────────┐
│  App.vue                                    │
│  （根组件，只管拼装）                          │
│                                             │
│  ┌─────────────┐  ┌───────────────────────┐ │
│  │ BlogHeader  │  │ BlogList               │ │
│  │  （独立）    │  │ （拥有 posts 数据）       │ │
│  └─────────────┘  │                        │ │
│                   │  Props ↓     Emit ↑    │ │
│                   │  ┌───────────────────┐ │ │
│                   │  │ BlogPost（子组件）  │ │ │
│                   │  │ 接收：title, date, │ │ │
│                   │  │ tags, excerpt,     │ │ │
│                   │  │ link, isRead       │ │ │
│                   │  │                    │ │ │
│                   │  │ 发出：toggle-read   │ │ │
│                   │  └───────────────────┘ │ │
│                   └───────────────────────┘ │
│  ┌─────────────┐                            │
│  │ BlogFooter  │                            │
│  │  （独立）    │                            │
│  └─────────────┘                            │
└─────────────────────────────────────────────┘

数据流向：
  Props（父→子）：数据向下流 → BlogList 把 post 数据传给 BlogPost
  Emit（子→父） ：事件向上冒 → BlogPost 发出 toggle-read，BlogList 处理
```

---

## 六、小结

| 你学了什么 | 核心要点 |
|---|---|
| **Props 概念** | 父组件给子组件传数据，类似父母给孩子零花钱 |
| **Props 语法** | 父：`:属性="值"`，子：`defineProps({ 属性: 类型 })` |
| **类型校验** | `type`、`required`、`default`，Array/Object 的 default 必须用工厂函数 `() => []` |
| **单向数据流** | 子组件**不能修改** Props，数据只能从父流向子 |
| **Emit 概念** | 子组件发事件通知父组件，类似孩子打电话叫家长 |
| **Emit 语法** | 子：`defineEmits(['事件名'])` + `emit('事件名', 参数)`，父：`@事件名="处理函数"` |
| **完整通信** | Props ↓（父→子）+ Emit ↑（子→父）= 父子通信闭环 |

---

## 七、术语附录

| 术语 | 解释 |
|---|---|
| **Props** | 父组件传递给子组件的数据。子组件通过 `defineProps()` 声明接收，父组件通过 `:属性="值"` 传递。类比：父母给孩子的零花钱 |
| **`defineProps()`** | Vue3 的编译宏，在 `<script setup>` 中声明组件接收的 Props。接受一个对象，定义每个属性的类型、必填、默认值 |
| **`defineEmits()`** | Vue3 的编译宏，在 `<script setup>` 中声明组件可以发出的事件。返回的 `emit` 函数用于触发事件 |
| **单向数据流** | Vue 的核心设计原则：数据只能从父组件流向子组件。子组件不能直接修改 Props，需要修改时必须通过 Emit 通知父组件 |
| **Emit** | 子组件向父组件通信的机制。子组件发出一个命名事件（如 `@toggle-read`），父组件监听并处理 |

---

## 八、已知坑点与禁止事项

| 坑点 | 现象 | 解决 |
|---|---|---|
| 子组件修改 Props | Vue 警告 `Attempting to mutate prop` | 子组件不能直接改 Props，改用 Emit 通知父组件改 |
| Array/Object default 不写函数 | 多个组件实例共享同一份数据，改一个全变 | `default: () => []`，必须用工厂函数 |
| Emit 事件名大小写 | HTML 模板中事件名会自动转小写 | 始终用 kebab-case 命名事件：`toggle-read` 而不是 `toggleRead` |
| 忘记 `defineEmits` | 调用 `emit()` 但未声明 | 必须在 `<script setup>` 里先 `defineEmits(['事件名'])` |
| Props 类型传错 | Vue 报警告 `Invalid prop type` | 检查传递的值类型是否和定义的一致（比如 `:count="1"` 传的是数字，`:count="'1'"` 传的是字符串） |

---

## 九、下一步建议

现在你已经掌握了 Vue 的核心三件套：**模板语法**（09）→ **响应式数据**（10）→ **组件通信**（11）。从下一篇开始，我们将给博客加上多页面路由、全局状态管理、后端 API 交互，逐步搭建成一个完整的动态博客应用！

👉 继续阅读：**12-Vue Router：给博客加上多页面**