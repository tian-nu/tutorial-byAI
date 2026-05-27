# 第22章：Vue 3 + Element Plus快速入门

## 本章目标

学完本章你将能够：

- 使用Vite创建Vue 3项目，理解SFC单文件组件的结构
- 掌握Vue 3 Composition API核心：`ref()`、`reactive()`、`computed`、`watch`、生命周期钩子
- 使用`<script setup>`语法编写简洁的组件代码
- 实现组件通信：`defineProps`（父→子）、`defineEmits`（子→父）
- 配置Vue Router实现单页应用路由
- 封装Axios实例，实现请求/响应拦截器，统一处理Token和错误
- 使用Element Plus的Table、Form、Dialog、Pagination组件构建CRUD页面
- 配置Vite代理解决开发环境跨域
- 交付EMS v6：Vue 3前端 + Spring Boot后端全栈版

---

> **本章定位**：第21章我们学习了前端基础，但用原生JS写复杂页面效率极低。本章引入Vue 3框架，它通过响应式数据绑定和组件化大幅提升开发效率。我们将用Vue 3 + Element Plus + Axios + Vue Router构建EMS前端，与第20章设计的RESTful API对接，完成前后端全栈联调。**本章所有Vue代码均使用Composition API（`<script setup>`语法），不使用Vue 2的Options API。**

---

## 22.1 Vue 3项目创建

### 22.1.1 使用Vite创建项目

Vue 3官方推荐使用Vite作为构建工具（替代Webpack），启动速度极快：

```bash
# 使用npm创建Vue 3项目
npm create vue@latest ems-frontend
```

创建过程中会提示选择功能，按以下方式选择：

```
✔ Add TypeScript? … No / Yes          ← 本书不用TypeScript，选No
✔ Add JSX Support? … No / Yes          ← 选No
✔ Add Vue Router for Single Page Application? … No / Yes  ← 选Yes
✔ Add Pinia for state management? … No / Yes              ← 选Yes
✔ Add Vitest for Unit testing? … No / Yes                 ← 选No
✔ Add an End-to-End Testing Solution? … No / Yes          ← 选No
✔ Add ESLint for code quality? … No / Yes                 ← 选Yes
✔ Add Prettier for code formatting? … No / Yes            ← 选Yes
```

创建完成后进入项目并安装依赖：

```bash
cd ems-frontend
npm install
```

启动开发服务器：

```bash
npm run dev
```

访问`http://localhost:5173`即可看到Vue的欢迎页面。

### 22.1.2 项目结构说明

```
ems-frontend/
├── index.html                  # 入口HTML（Vite以此作为入口）
├── package.json                # 依赖和脚本配置
├── vite.config.js              # Vite配置文件
├── public/                     # 静态资源（不经过构建处理）
│   └── favicon.ico
└── src/                        # 源代码
    ├── App.vue                 # 根组件
    ├── main.js                 # 应用入口（创建Vue实例、挂载插件）
    ├── router/                 # 路由配置
    │   └── index.js
    ├── stores/                 # Pinia状态管理
    │   └── counter.js
    ├── views/                  # 页面级组件
    │   └── HomeView.vue
    ├── components/             # 可复用组件
    │   └── HelloWorld.vue
    └── assets/                 # 静态资源（经过构建处理）
        └── logo.svg
```

### 22.1.3 SFC单文件组件

Vue的组件以`.vue`文件形式存在，称为SFC（Single File Component），包含三部分：

```vue
<template>
  <!-- HTML模板：定义组件的结构和外观 -->
  <div class="greeting">
    <h1>{{ message }}</h1>
    <button @click="changeMessage">点击修改</button>
  </div>
</template>

<script setup>
// JavaScript逻辑：定义数据和方法
// <script setup>是Vue 3的语法糖，不需要export default
import { ref } from 'vue'

const message = ref('Hello Vue 3!')

function changeMessage() {
  message.value = '你好，Vue 3！'
}
</script>

<style scoped>
/* CSS样式：scoped表示样式只作用于当前组件 */
.greeting {
  text-align: center;
  color: #333;
}
</style>
```

> 🚨 **坑点：Vue 2和Vue 3语法完全不同 → Options API vs Composition API**
>
> Vue 2使用Options API：
> ```vue
> <script>
> export default {
>   data() { return { count: 0 } },
>   methods: { increment() { this.count++ } },
>   computed: { double() { return this.count * 2 } }
> }
> </script>
> ```
>
> Vue 3推荐Composition API（`<script setup>`）：
> ```vue
> <script setup>
> import { ref, computed } from 'vue'
> const count = ref(0)
> const double = computed(() => count.value * 2)
> function increment() { count.value++ }
> </script>
> ```
>
> 网上大量教程还在用Options API，**本书统一使用Composition API**。如果你搜到`data()`、`methods:`、`this.xxx`这种写法，那是Vue 2的，不要照搬。

---

## 22.2 Composition API核心

### 22.2.1 ref() — 包装基本类型的响应式数据

`ref()`用于创建响应式数据，可以包装任何类型的值，但最常用于基本类型（字符串、数字、布尔值）：

```vue
<template>
  <div>
    <p>计数：{{ count }}</p>
    <p>姓名：{{ name }}</p>
    <button @click="increment">+1</button>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const count = ref(0)          // 包装数字
const name = ref('张三')       // 包装字符串

function increment() {
  count.value++               // 在<script>中通过.value访问和修改
}
</script>
```

> 🚨 **坑点：ref在script中需.value，template中自动解包**
>
> ```vue
> <script setup>
> import { ref } from 'vue'
> const count = ref(0)
>
> // 在<script>中：必须用.value
> console.log(count)        // RefImpl { _value: 0, ... }  ← 不是0！
> console.log(count.value)  // 0  ← 正确
> count.value = 10          // 修改值
>
> // 忘写.value是最常见的Vue 3 Bug
> // count = 10  ← 错误！这会丢失响应性
> </script>
>
> <template>
>   <!-- 在<template>中：自动解包，不需要.value -->
>   <p>{{ count }}</p>      <!-- 显示10，不需要count.value -->
> </template>
> ```

### 22.2.2 reactive() — 包装对象的响应式数据

`reactive()`用于创建对象类型的响应式数据：

```vue
<script setup>
import { reactive } from 'vue'

const employee = reactive({
  name: '张三',
  age: 25,
  department: '技术部'
})

// 直接访问属性，不需要.value
console.log(employee.name)  // "张三"
employee.name = '李四'       // 直接修改
</script>
```

> 🚨 **坑点：reactive不能替换整个对象 → 丢失响应性**
>
> ```javascript
> const employee = reactive({ name: '张三', age: 25 })
>
> // 错误！直接赋值新对象会丢失响应性
> employee = { name: '李四', age: 30 }  // ← 报错！const不能重新赋值
>
> // 即使改成let也丢失响应性
> let employee = reactive({ name: '张三', age: 25 })
> employee = reactive({ name: '李四', age: 30 })  // ← 响应性丢失！
>
> // 正确做法1：逐个属性修改
> employee.name = '李四'
> employee.age = 30
>
> // 正确做法2：用Object.assign
> Object.assign(employee, { name: '李四', age: 30 })
>
> // 正确做法3：用ref包装对象（推荐！）
> const employee = ref({ name: '张三', age: 25 })
> employee.value = { name: '李四', age: 30 }  // 替换整个对象，响应性正常
> ```

**ref vs reactive选择指南**：

| 特性 | `ref()` | `reactive()` |
|------|---------|-------------|
| 支持类型 | 任何类型 | 仅对象类型 |
| 访问方式 | `.value` | 直接访问属性 |
| 替换整个值 | 可以（`x.value = newVal`） | **不可以**（丢失响应性） |
| 解构 | 解构后丢失响应性 | 解构后丢失响应性 |
| **推荐度** | ⭐⭐⭐ 优先使用 | 仅在深层对象时使用 |

**经验法则**：优先使用`ref()`，只有当你有一个深层嵌套的对象且需要频繁访问其属性时，才考虑`reactive()`。

### 22.2.3 computed — 计算属性

`computed`创建一个有缓存的计算值——依赖不变就不重新计算：

```vue
<template>
  <p>原价：{{ price }}</p>
  <p>折扣价：{{ discountPrice }}</p>
</template>

<script setup>
import { ref, computed } from 'vue'

const price = ref(100)

const discountPrice = computed(() => {
  console.log('computed执行了')  // 只有price变化时才执行
  return price.value * 0.8
})

// computed是只读的，不能直接赋值
// discountPrice.value = 50  ← 报错！
</script>
```

**computed vs methods的区别**：computed有缓存，methods没有。如果一个计算在模板中被多次使用，computed只计算一次，methods每次渲染都会重新执行。

### 22.2.4 watch vs watchEffect

```vue
<script setup>
import { ref, watch, watchEffect } from 'vue'

const keyword = ref('')
const results = ref([])

// watch：明确监听源，有新旧值
watch(keyword, (newVal, oldVal) => {
  console.log(`搜索词从"${oldVal}"变为"${newVal}"`)
  // 发起搜索请求
  fetchResults(newVal)
})

// 监听多个源
const firstName = ref('张')
const lastName = ref('三')
watch([firstName, lastName], ([newFirst, newLast]) => {
  console.log(`全名变为：${newFirst}${newLast}`)
})

// watchEffect：自动追踪依赖
watchEffect(() => {
  // 自动追踪keyword.value的依赖
  console.log(`搜索词：${keyword.value}`)
  fetchResults(keyword.value)
})
</script>
```

**watch vs watchEffect选择**：

| 特性 | `watch` | `watchEffect` |
|------|---------|--------------|
| 监听源 | 需要明确指定 | 自动追踪 |
| 新旧值 | 可以获取 | 不能获取 |
| 懒执行 | 默认懒执行（值变化才执行） | 立即执行一次 |
| 适用场景 | 需要对比新旧值 | 只关心新值，自动追踪依赖 |

### 22.2.5 生命周期钩子

```vue
<script setup>
import { onMounted, onUnmounted, onUpdated } from 'vue'

onMounted(() => {
  console.log('组件挂载完成 → 可以操作DOM、发起API请求')
  loadEmployees()
})

onUpdated(() => {
  console.log('组件更新完成 → 数据变化导致DOM重新渲染后')
})

onUnmounted(() => {
  console.log('组件卸载 → 清理定时器、取消订阅等')
})
</script>
```

Vue 3生命周期钩子与Vue 2的对应关系：

| Vue 2（Options API） | Vue 3（Composition API） |
|---------------------|-------------------------|
| `created` | `setup()`本身（`<script setup>`中的代码就在created阶段执行） |
| `mounted` | `onMounted()` |
| `updated` | `onUpdated()` |
| `destroyed` | `onUnmounted()` |
| `beforeDestroy` | `onBeforeUnmount()` |

> 🚨 **坑点：不要在setup/script setup之外使用ref/reactive → 响应性丢失**
>
> `ref()`和`reactive()`必须在`setup()`或`<script setup>`中调用。如果你在普通函数中创建ref然后导出，它不会与组件关联，可能导致响应性丢失。正确做法是在`<script setup>`中创建响应式数据，或通过组合函数（Composable）封装。

---

## 22.3 组件化

### 22.3.1 组件定义与使用

每个`.vue`文件就是一个组件。使用时只需导入即可，`<script setup>`中的组件自动注册：

```vue
<!-- Parent.vue -->
<template>
  <div>
    <h1>父组件</h1>
    <ChildComponent title="员工列表" :count="employees.length" />
  </div>
</template>

<script setup>
import ChildComponent from './ChildComponent.vue'
import { ref } from 'vue'

const employees = ref([
  { id: 1, name: '张三' },
  { id: 2, name: '李四' }
])
</script>
```

### 22.3.2 props（父→子）

`defineProps`声明组件接收的属性：

```vue
<!-- ChildComponent.vue -->
<template>
  <div class="child">
    <h2>{{ title }}</h2>
    <p>共 {{ count }} 条数据</p>
  </div>
</template>

<script setup>
// 声明props
const props = defineProps({
  title: {
    type: String,
    required: true
  },
  count: {
    type: Number,
    default: 0
  }
})

// 在script中使用props
console.log(props.title)
</script>
```

> 🚨 **坑点：props只读，不要直接修改**
>
> ```vue
> <script setup>
> const props = defineProps({ count: Number })
>
> // 错误！直接修改props会触发Vue警告
> props.count = 10  // ← Vue警告：Unexpected mutation of prop "count"
>
> // 正确做法：用本地变量接收
> const localCount = ref(props.count)
> localCount.value = 10  // ← 正确
> </script>
> ```

### 22.3.3 emits（子→父）

`defineEmits`声明组件发出的事件：

```vue
<!-- EmployeeDialog.vue -->
<template>
  <div class="dialog">
    <h2>{{ isEdit ? '编辑员工' : '新增员工' }}</h2>
    <input v-model="form.name" placeholder="姓名">
    <button @click="handleSubmit">提交</button>
    <button @click="handleCancel">取消</button>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  isEdit: Boolean,
  employee: Object
})

const emit = defineEmits(['submit', 'cancel'])

const form = ref({ name: props.employee?.name || '' })

function handleSubmit() {
  emit('submit', form.value)  // 发出submit事件，携带数据
}

function handleCancel() {
  emit('cancel')              // 发出cancel事件
}
</script>
```

父组件监听事件：

```vue
<!-- Parent.vue -->
<template>
  <EmployeeDialog
    :is-edit="isEdit"
    :employee="currentEmployee"
    @submit="handleSubmit"
    @cancel="handleCancel"
  />
</template>

<script setup>
import EmployeeDialog from './EmployeeDialog.vue'
import { ref } from 'vue'

const isEdit = ref(false)
const currentEmployee = ref(null)

function handleSubmit(formData) {
  console.log('收到子组件数据：', formData)
}

function handleCancel() {
  console.log('取消操作')
}
</script>
```

### 22.3.4 插槽slot

插槽允许父组件向子组件传递模板内容：

```vue
<!-- Card.vue -->
<template>
  <div class="card">
    <div class="card-header">
      <slot name="header">默认标题</slot>
    </div>
    <div class="card-body">
      <slot>默认内容</slot>
    </div>
    <div class="card-footer">
      <slot name="footer"></slot>
    </div>
  </div>
</template>
```

```vue
<!-- 使用插槽 -->
<template>
  <Card>
    <template #header>
      <h3>员工统计</h3>
    </template>
    <template #default>
      <p>总人数：56</p>
    </template>
    <template #footer>
      <button>查看详情</button>
    </template>
  </Card>
</template>
```

---

## 22.4 Vue Router

### 22.4.1 安装与配置

创建项目时已选择Vue Router，如果没有，手动安装：

```bash
npm install vue-router@4
```

配置路由（`src/router/index.js`）：

```javascript
import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('../views/HomeView.vue')
  },
  {
    path: '/employees',
    name: 'EmployeeList',
    component: () => import('../views/EmployeeList.vue')
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/LoginView.vue')
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('../views/NotFound.vue')
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

export default router
```

> `createWebHistory`使用HTML5 History API（URL无`#`号），需要服务器配置支持。如果服务器不支持，改用`createWebHashHistory()`（URL带`#`号，如`http://localhost:5173/#/employees`）。

### 22.4.2 router-link 与 router-view

```vue
<!-- App.vue -->
<template>
  <div id="app">
    <nav>
      <router-link to="/">首页</router-link>
      <router-link to="/employees">员工管理</router-link>
      <router-link to="/login">登录</router-link>
    </nav>
    <router-view />
  </div>
</template>
```

- `<router-link>`：生成导航链接，点击时不会刷新页面（SPA单页应用的核心）
- `<router-view>`：路由匹配的组件将渲染在这里

### 22.4.3 编程式导航

```javascript
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()

// 导航到指定路径
router.push('/employees')

// 命名路由 + 参数
router.push({ name: 'EmployeeList', query: { department: '技术部' } })

// 获取路由参数
console.log(route.params.id)    // 路径参数 /employees/:id
console.log(route.query.department)  // 查询参数 ?department=技术部

// 返回上一页
router.back()
```

### 22.4.4 路由守卫（登录拦截）

```javascript
// src/router/index.js
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')

  if (to.name !== 'Login' && !token) {
    next({ name: 'Login' })  // 未登录且不是去登录页 → 跳转登录
  } else if (to.name === 'Login' && token) {
    next({ name: 'Home' })   // 已登录还去登录页 → 跳转首页
  } else {
    next()                    // 正常放行
  }
})
```

> 🚨 **坑点：路由name重复 → 路由匹配报错**
>
> 每个路由的`name`必须唯一。如果两个路由的`name`相同，后者会覆盖前者，且可能产生难以排查的导航错误。建议使用有语义的命名，如`EmployeeList`、`EmployeeDetail`、`EmployeeCreate`。

---

## 22.5 Axios封装

### 22.5.1 安装Axios

```bash
npm install axios
```

### 22.5.2 创建Axios实例

创建`src/utils/request.js`：

```javascript
import axios from 'axios'
import { ElMessage } from 'element-plus'
import router from '@/router'

const request = axios.create({
  baseURL: '/api',           // 基础URL，所有请求会自动加上这个前缀
  timeout: 10000,            // 超时时间10秒
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
request.interceptors.request.use(
  (config) => {
    // 每次请求自动添加Token
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
request.interceptors.response.use(
  (response) => {
    const result = response.data

    // 解析后端统一返回格式 Result<T>
    if (result.code === 200) {
      return result.data       // 成功时只返回data，调用方不需要再解包
    } else {
      ElMessage.error(result.message || '操作失败')
      return Promise.reject(new Error(result.message))
    }
  },
  (error) => {
    // HTTP错误处理
    if (error.response) {
      const status = error.response.status
      switch (status) {
        case 401:
          ElMessage.error('登录已过期，请重新登录')
          localStorage.removeItem('token')
          router.push('/login')
          break
        case 403:
          ElMessage.error('没有权限执行此操作')
          break
        case 404:
          ElMessage.error('请求的资源不存在')
          break
        case 500:
          ElMessage.error('服务器内部错误')
          break
        default:
          ElMessage.error(`请求失败：${status}`)
      }
    } else if (error.message.includes('timeout')) {
      ElMessage.error('请求超时，请稍后重试')
    } else {
      ElMessage.error('网络连接异常')
    }
    return Promise.reject(error)
  }
)

export default request
```

> 🚨 **坑点：拦截器条件判断缺失 → 死循环**
>
> 最典型的死循环场景：401时跳转登录页，但登录页的请求也被拦截器拦截，又触发401，又跳登录……
>
> ```javascript
> // 危险写法：所有401都跳登录
> if (status === 401) {
>   router.push('/login')  // 如果/login页面本身也会触发API请求呢？
> }
>
> // 安全写法：排除登录相关接口
> if (status === 401 && !error.config.url.includes('/auth/login')) {
>   localStorage.removeItem('token')
>   router.push('/login')
> }
>
> // 更好的做法：用标志位防止重复跳转
> let isRedirecting = false
> if (status === 401 && !isRedirecting) {
>   isRedirecting = true
>   localStorage.removeItem('token')
>   router.push('/login').finally(() => { isRedirecting = false })
> }
> ```

> 🚨 **坑点：Axios拦截器中用useRouter → 在组件外获取router需导入router实例**
>
> 在Vue组件中，我们用`const router = useRouter()`获取路由实例。但在`request.js`这种非组件文件中，`useRouter()`不可用（它必须在`setup`中调用）。
>
> 解决方案：直接导入router实例：
>
> ```javascript
> // request.js
> import router from '@/router'  // 直接导入router实例
>
> // 在拦截器中使用
> router.push('/login')
> ```
>
> 这要求`router/index.js`中导出了router实例。这种方式在模块初始化时就建立了依赖，确保router已创建。

### 22.5.3 封装API调用

创建`src/api/employee.js`：

```javascript
import request from '@/utils/request'

export function getEmployees(params) {
  return request.get('/v1/employees', { params })
}

export function getEmployeeById(id) {
  return request.get(`/v1/employees/${id}`)
}

export function createEmployee(data) {
  return request.post('/v1/employees', data)
}

export function updateEmployee(id, data) {
  return request.put(`/v1/employees/${id}`, data)
}

export function patchEmployee(id, data) {
  return request.patch(`/v1/employees/${id}`, data)
}

export function deleteEmployee(id) {
  return request.delete(`/v1/employees/${id}`)
}
```

使用示例：

```javascript
import { getEmployees, createEmployee } from '@/api/employee'

// 查询员工列表
const pageResult = await getEmployees({ page: 0, size: 10, department: '技术部' })
// pageResult就是后端Result.data中的PageResult对象
console.log(pageResult.content)        // 员工列表
console.log(pageResult.totalElements)  // 总条数

// 创建员工
await createEmployee({
  name: '赵六',
  age: 28,
  department: '产品部',
  salary: 16000,
  email: 'zhaoliu@example.com'
})
```

注意：因为响应拦截器已经解包了`Result.data`，所以`getEmployees`返回的直接就是`PageResult`对象，不需要再`.data.data`。

---

## 22.6 Element Plus

### 22.6.1 安装与引入

```bash
npm install element-plus
```

**完整引入**（简单，但打包体积大）：

```javascript
// src/main.js
import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import zhCn from 'element-plus/es/locale/lang/zh-cn'

const app = createApp(App)
app.use(router)
app.use(ElementPlus, { locale: zhCn })  // 中文语言包
app.mount('#app')
```

**按需引入**（推荐，打包体积小）：

```bash
npm install -D unplugin-vue-components unplugin-auto-import
```

配置`vite.config.js`：

```javascript
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import AutoImport from 'unplugin-auto-import/vite'
import Components from 'unplugin-vue-components/vite'
import { ElementPlusResolver } from 'unplugin-vue-components/resolvers'

export default defineConfig({
  plugins: [
    vue(),
    AutoImport({
      resolvers: [ElementPlusResolver()]
    }),
    Components({
      resolvers: [ElementPlusResolver()]
    })
  ]
})
```

按需引入无需手动import组件，直接在模板中使用即可。

### 22.6.2 el-table — 数据表格

```vue
<template>
  <el-table :data="tableData" stripe border style="width: 100%"
            @selection-change="handleSelectionChange">
    <el-table-column type="selection" width="55" />
    <el-table-column prop="id" label="ID" width="80" sortable />
    <el-table-column prop="name" label="姓名" width="120" />
    <el-table-column prop="age" label="年龄" width="80" sortable />
    <el-table-column prop="department" label="部门" width="120" />
    <el-table-column prop="salary" label="薪资" width="120">
      <template #default="{ row }">
        ¥{{ row.salary?.toLocaleString() }}
      </template>
    </el-table-column>
    <el-table-column prop="email" label="邮箱" min-width="180" />
    <el-table-column label="操作" width="200" fixed="right">
      <template #default="{ row }">
        <el-button type="primary" size="small" @click="handleEdit(row)">
          编辑
        </el-button>
        <el-button type="danger" size="small" @click="handleDelete(row)">
          删除
        </el-button>
      </template>
    </el-table-column>
  </el-table>
</template>

<script setup>
const tableData = ref([])

function handleSelectionChange(selection) {
  console.log('选中行：', selection)
}

function handleEdit(row) {
  console.log('编辑：', row)
}

function handleDelete(row) {
  console.log('删除：', row)
}
</script>
```

> 🚨 **坑点：Element Plus的事件名可能和Element UI不同**
>
> 例如`el-table`的选中事件，Element UI中是`@selection-change`，Element Plus中也是`@selection-change`——但有些事件名有变化。开发时务必参考Element Plus官方文档（`https://element-plus.org`），不要照搬Element UI的用法。

### 22.6.3 el-form — 表单与校验

```vue
<template>
  <el-form ref="formRef" :model="form" :rules="rules" label-width="80px">
    <el-form-item label="姓名" prop="name">
      <el-input v-model="form.name" placeholder="请输入姓名" />
    </el-form-item>

    <el-form-item label="年龄" prop="age">
      <el-input-number v-model="form.age" :min="18" :max="65" />
    </el-form-item>

    <el-form-item label="部门" prop="department">
      <el-select v-model="form.department" placeholder="请选择部门">
        <el-option label="技术部" value="技术部" />
        <el-option label="产品部" value="产品部" />
        <el-option label="市场部" value="市场部" />
      </el-select>
    </el-form-item>

    <el-form-item label="薪资" prop="salary">
      <el-input-number v-model="form.salary" :min="0" :step="1000" />
    </el-form-item>

    <el-form-item label="邮箱" prop="email">
      <el-input v-model="form.email" placeholder="请输入邮箱" />
    </el-form-item>

    <el-form-item>
      <el-button type="primary" @click="submitForm">提交</el-button>
      <el-button @click="resetForm">重置</el-button>
    </el-form-item>
  </el-form>
</template>

<script setup>
import { ref, reactive } from 'vue'

const formRef = ref()

const form = reactive({
  name: '',
  age: 25,
  department: '',
  salary: 15000,
  email: ''
})

const rules = {
  name: [
    { required: true, message: '请输入姓名', trigger: 'blur' },
    { min: 2, max: 20, message: '姓名长度2-20个字符', trigger: 'blur' }
  ],
  age: [
    { required: true, message: '请输入年龄', trigger: 'blur' }
  ],
  department: [
    { required: true, message: '请选择部门', trigger: 'change' }
  ],
  salary: [
    { required: true, message: '请输入薪资', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ]
}

async function submitForm() {
  const valid = await formRef.value.validate()
  if (valid) {
    console.log('表单数据：', { ...form })
    // 调用API提交
  }
}

function resetForm() {
  formRef.value.resetFields()
}
</script>
```

### 22.6.4 el-dialog — 弹窗

```vue
<template>
  <el-dialog
    v-model="dialogVisible"
    :title="isEdit ? '编辑员工' : '新增员工'"
    width="500px"
    @close="handleClose"
  >
    <el-form ref="formRef" :model="form" :rules="rules" label-width="80px">
      <!-- 表单内容同上 -->
    </el-form>

    <template #footer>
      <el-button @click="dialogVisible = false">取消</el-button>
      <el-button type="primary" @click="submitForm">确定</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, nextTick } from 'vue'

const dialogVisible = ref(false)
const isEdit = ref(false)
const formRef = ref()

const form = reactive({
  id: null,
  name: '',
  age: 25,
  department: '',
  salary: 15000,
  email: ''
})

function openDialog(employee = null) {
  isEdit.value = !!employee
  if (employee) {
    Object.assign(form, employee)  // 编辑：回显数据
  } else {
    resetFormFields()              // 新增：清空表单
  }
  dialogVisible.value = true
}

function handleClose() {
  formRef.value?.resetFields()
}

function resetFormFields() {
  form.id = null
  form.name = ''
  form.age = 25
  form.department = ''
  form.salary = 15000
  form.email = ''
}

defineExpose({ openDialog })
</script>
```

父组件调用：

```vue
<template>
  <EmployeeDialog ref="dialogRef" @submit="handleSubmit" />
  <el-button @click="dialogRef.openDialog()">新增员工</el-button>
  <el-button @click="dialogRef.openDialog(currentRow)">编辑员工</el-button>
</template>
```

### 22.6.5 el-pagination — 分页

```vue
<template>
  <el-pagination
    v-model:current-page="currentPage"
    v-model:page-size="pageSize"
    :page-sizes="[10, 20, 50, 100]"
    :total="total"
    layout="total, sizes, prev, pager, next, jumper"
    @size-change="handleSizeChange"
    @current-change="handlePageChange"
  />
</template>

<script setup>
import { ref } from 'vue'

const currentPage = ref(1)    // 当前页码（从1开始）
const pageSize = ref(20)      // 每页条数
const total = ref(0)          // 总条数

function handleSizeChange(size) {
  pageSize.value = size
  currentPage.value = 1       // 切换每页条数时回到第1页
  loadData()
}

function handlePageChange(page) {
  currentPage.value = page
  loadData()
}

async function loadData() {
  // 后端Pageable页码从0开始，前端从1开始，需要-1
  const params = {
    page: currentPage.value - 1,
    size: pageSize.value
  }
  const result = await getEmployees(params)
  total.value = result.totalElements
  // ...
}
</script>
```

---

## 22.7 前后端联调实战

### 22.7.1 Vite配置代理（解决跨域）

前后端分离开发时，前端运行在`localhost:5173`，后端运行在`localhost:8080`，浏览器会阻止跨域请求。Vite提供了开发代理来解决：

```javascript
// vite.config.js
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src')  // @指向src目录
    }
  },
  server: {
    port: 5173,
    proxy: {
      '/api': {                           // 匹配以/api开头的请求
        target: 'http://localhost:8080',  // 代理到后端地址
        changeOrigin: true                // 修改请求头中的Origin
        // 不需要rewrite，因为后端的Controller路径就是/api/v1/...
      }
    }
  }
})
```

工作原理：

```
浏览器 → http://localhost:5173/api/v1/employees
         ↓ (Vite代理)
后端   → http://localhost:8080/api/v1/employees
```

浏览器以为请求是同源的（都是5173），Vite在中间转发到8080，绕过了浏览器的同源策略限制。

> 🚨 **坑点：Vite代理只在开发环境生效 → 生产环境用Nginx**
>
> `vite.config.js`中的proxy配置只在`npm run dev`时生效。生产环境（`npm run build`后部署的静态文件）没有Vite代理，跨域问题需要用Nginx反向代理解决：
>
> ```nginx
> server {
>     listen 80;
>     server_name example.com;
>
>     # 前端静态文件
>     location / {
>         root /opt/ems-frontend/dist;
>         try_files $uri $uri/ /index.html;  # SPA路由回退
>     }
>
>     # API代理到后端
>     location /api/ {
>         proxy_pass http://localhost:8080;
>         proxy_set_header Host $host;
>         proxy_set_header X-Real-IP $remote_addr;
>     }
> }
> ```

### 22.7.2 完整登录流程

**LoginView.vue**：

```vue
<template>
  <div class="login-container">
    <el-card class="login-card">
      <h2>EMS员工管理系统</h2>
      <el-form ref="loginFormRef" :model="loginForm" :rules="loginRules">
        <el-form-item prop="username">
          <el-input v-model="loginForm.username" placeholder="用户名"
                    prefix-icon="User" />
        </el-form-item>
        <el-form-item prop="password">
          <el-input v-model="loginForm.password" type="password"
                    placeholder="密码" prefix-icon="Lock"
                    show-password @keyup.enter="handleLogin" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="loading" style="width: 100%"
                     @click="handleLogin">
            登录
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'

const router = useRouter()
const loginFormRef = ref()
const loading = ref(false)

const loginForm = reactive({
  username: '',
  password: ''
})

const loginRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

async function handleLogin() {
  const valid = await loginFormRef.value.validate()
  if (!valid) return

  loading.value = true
  try {
    const data = await request.post('/v1/auth/login', {
      username: loginForm.username,
      password: loginForm.password
    })

    localStorage.setItem('token', data.token)
    localStorage.setItem('username', data.username)
    ElMessage.success('登录成功')
    router.push('/')
  } catch (error) {
    // 错误已在拦截器中处理
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background-color: #f0f2f5;
}
.login-card {
  width: 400px;
}
.login-card h2 {
  text-align: center;
  margin-bottom: 20px;
  color: #409eff;
}
</style>
```

### 22.7.3 完整CRUD流程

**EmployeeList.vue** — 员工管理页面（EMS v6核心页面）：

```vue
<template>
  <div class="employee-list">
    <!-- 搜索栏 -->
    <el-card class="search-card">
      <el-form :inline="true" :model="searchForm">
        <el-form-item label="姓名">
          <el-input v-model="searchForm.name" placeholder="请输入姓名" clearable />
        </el-form-item>
        <el-form-item label="部门">
          <el-select v-model="searchForm.department" placeholder="请选择部门" clearable>
            <el-option label="技术部" value="技术部" />
            <el-option label="产品部" value="产品部" />
            <el-option label="市场部" value="市场部" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 工具栏 -->
    <el-card class="table-card">
      <div class="toolbar">
        <el-button type="primary" @click="handleAdd">新增员工</el-button>
        <el-button type="danger" :disabled="!selectedRows.length"
                   @click="handleBatchDelete">
          批量删除
        </el-button>
      </div>

      <!-- 数据表格 -->
      <el-table :data="tableData" stripe border v-loading="loading"
                @selection-change="handleSelectionChange">
        <el-table-column type="selection" width="55" />
        <el-table-column prop="id" label="ID" width="80" sortable />
        <el-table-column prop="name" label="姓名" width="120" />
        <el-table-column prop="age" label="年龄" width="80" />
        <el-table-column prop="department" label="部门" width="120" />
        <el-table-column prop="salary" label="薪资" width="120">
          <template #default="{ row }">
            ¥{{ row.salary?.toLocaleString() }}
          </template>
        </el-table-column>
        <el-table-column prop="email" label="邮箱" min-width="180" />
        <el-table-column prop="hireDate" label="入职日期" width="120" />
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="handleEdit(row)">
              编辑
            </el-button>
            <el-button type="danger" size="small" @click="handleDelete(row)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.size"
          :page-sizes="[10, 20, 50]"
          :total="pagination.total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="loadData"
          @current-change="loadData"
        />
      </div>
    </el-card>

    <!-- 新增/编辑弹窗 -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="500px"
               @close="resetForm">
      <el-form ref="formRef" :model="form" :rules="formRules" label-width="80px">
        <el-form-item label="姓名" prop="name">
          <el-input v-model="form.name" placeholder="请输入姓名" />
        </el-form-item>
        <el-form-item label="年龄" prop="age">
          <el-input-number v-model="form.age" :min="18" :max="65" />
        </el-form-item>
        <el-form-item label="部门" prop="department">
          <el-select v-model="form.department" placeholder="请选择部门">
            <el-option label="技术部" value="技术部" />
            <el-option label="产品部" value="产品部" />
            <el-option label="市场部" value="市场部" />
          </el-select>
        </el-form-item>
        <el-form-item label="薪资" prop="salary">
          <el-input-number v-model="form.salary" :min="0" :step="1000" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="form.email" placeholder="请输入邮箱" />
        </el-form-item>
        <el-form-item label="入职日期" prop="hireDate">
          <el-date-picker v-model="form.hireDate" type="date"
                          value-format="YYYY-MM-DD" placeholder="选择日期" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitLoading" @click="submitForm">
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  getEmployees,
  createEmployee,
  updateEmployee,
  deleteEmployee
} from '@/api/employee'

const loading = ref(false)
const submitLoading = ref(false)
const tableData = ref([])
const selectedRows = ref([])
const dialogVisible = ref(false)
const isEdit = ref(false)
const formRef = ref()

const searchForm = reactive({ name: '', department: '' })

const pagination = reactive({ page: 1, size: 20, total: 0 })

const form = reactive({
  id: null,
  name: '',
  age: 25,
  department: '',
  salary: 15000,
  email: '',
  hireDate: ''
})

const formRules = {
  name: [
    { required: true, message: '请输入姓名', trigger: 'blur' },
    { min: 2, max: 20, message: '姓名长度2-20个字符', trigger: 'blur' }
  ],
  age: [{ required: true, message: '请输入年龄', trigger: 'blur' }],
  department: [{ required: true, message: '请选择部门', trigger: 'change' }],
  salary: [{ required: true, message: '请输入薪资', trigger: 'blur' }],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ]
}

const dialogTitle = computed(() => isEdit.value ? '编辑员工' : '新增员工')

onMounted(() => {
  loadData()
})

async function loadData() {
  loading.value = true
  try {
    const params = {
      page: pagination.page - 1,
      size: pagination.size
    }
    if (searchForm.name) params.nameLike = searchForm.name
    if (searchForm.department) params.department = searchForm.department

    const result = await getEmployees(params)
    tableData.value = result.content
    pagination.total = result.totalElements
  } catch (error) {
    // 错误已在拦截器中处理
  } finally {
    loading.value = false
  }
}

function handleSearch() {
  pagination.page = 1
  loadData()
}

function handleReset() {
  searchForm.name = ''
  searchForm.department = ''
  pagination.page = 1
  loadData()
}

function handleSelectionChange(selection) {
  selectedRows.value = selection
}

function handleAdd() {
  isEdit.value = false
  resetFormFields()
  dialogVisible.value = true
}

function handleEdit(row) {
  isEdit.value = true
  Object.assign(form, { ...row })
  dialogVisible.value = true
}

async function handleDelete(row) {
  try {
    await ElMessageBox.confirm(
      `确定要删除员工"${row.name}"吗？`, '删除确认',
      { type: 'warning', confirmButtonText: '确定', cancelButtonText: '取消' }
    )
    await deleteEmployee(row.id)
    ElMessage.success('删除成功')
    loadData()
  } catch (error) {
    if (error !== 'cancel') {
      // 用户取消不处理，其他错误已在拦截器中处理
    }
  }
}

async function handleBatchDelete() {
  const ids = selectedRows.value.map(row => row.id)
  try {
    await ElMessageBox.confirm(
      `确定要删除选中的${ids.length}名员工吗？`, '批量删除确认',
      { type: 'warning' }
    )
    // 逐个删除（后端没有批量删除接口时）
    for (const id of ids) {
      await deleteEmployee(id)
    }
    ElMessage.success('批量删除成功')
    loadData()
  } catch (error) {
    if (error !== 'cancel') {
      // 错误已在拦截器中处理
    }
  }
}

async function submitForm() {
  const valid = await formRef.value.validate()
  if (!valid) return

  submitLoading.value = true
  try {
    if (isEdit.value) {
      await updateEmployee(form.id, { ...form })
      ElMessage.success('更新成功')
    } else {
      await createEmployee({ ...form })
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    loadData()
  } catch (error) {
    // 错误已在拦截器中处理
  } finally {
    submitLoading.value = false
  }
}

function resetForm() {
  formRef.value?.resetFields()
}

function resetFormFields() {
  form.id = null
  form.name = ''
  form.age = 25
  form.department = ''
  form.salary = 15000
  form.email = ''
  form.hireDate = ''
}
</script>

<style scoped>
.employee-list {
  padding: 20px;
}
.search-card {
  margin-bottom: 20px;
}
.toolbar {
  margin-bottom: 15px;
}
.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>
```

---

## EMS v6：Vue前端 + Spring Boot后端全栈版

### 项目架构

```
┌─────────────────────────────────────────────────────────┐
│                    浏览器                                │
│  ┌─────────────────────────────────────────────────┐   │
│  │           Vue 3 + Element Plus                    │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────────┐    │   │
│  │  │  Router   │ │  Views   │ │  Components   │    │   │
│  │  └──────────┘ └──────────┘ └──────────────┘    │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────────┐    │   │
│  │  │  Axios    │ │  Pinia   │ │ Element Plus │    │   │
│  │  │(拦截器)   │ │ (状态)   │ │  (UI组件)    │    │   │
│  │  └──────────┘ └──────────┘ └──────────────┘    │   │
│  └────────────────────┬────────────────────────────┘   │
│                       │ HTTP (JSON)                     │
│                       ▼                                 │
│  ┌────────────────────────────────────────────────┐    │
│  │         Spring Boot RESTful API                 │    │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────────┐   │    │
│  │  │Controller│ │  Service  │ │  Repository   │   │    │
│  │  └──────────┘ └──────────┘ └──────────────┘   │    │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────────┐   │    │
│  │  │  Result   │ │ 全局异常  │ │  参数校验     │   │    │
│  │  │ (统一格式)│ │  处理     │ │  (JSR-380)   │   │    │
│  │  └──────────┘ └──────────┘ └──────────────┘   │    │
│  └────────────────────┬───────────────────────────┘    │
│                       │ JDBC / JPA                      │
│                       ▼                                 │
│  ┌────────────────────────────────────────────────┐    │
│  │              MySQL 数据库                        │    │
│  └────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
```

### 前端目录结构

```
ems-frontend/
├── index.html
├── package.json
├── vite.config.js
└── src/
    ├── App.vue
    ├── main.js
    ├── router/
    │   └── index.js
    ├── stores/
    │   └── user.js
    ├── api/
    │   ├── employee.js
    │   └── auth.js
    ├── utils/
    │   └── request.js
    ├── views/
    │   ├── LoginView.vue
    │   ├── HomeView.vue
    │   ├── EmployeeList.vue
    │   └── NotFound.vue
    └── components/
        └── AppHeader.vue
```

### 关键文件清单

| 文件 | 作用 | 本章对应章节 |
|------|------|-------------|
| `vite.config.js` | Vite配置（代理、别名） | 22.7.1 |
| `src/utils/request.js` | Axios封装（拦截器） | 22.5.2 |
| `src/api/employee.js` | 员工API接口封装 | 22.5.3 |
| `src/router/index.js` | 路由配置+守卫 | 22.4 |
| `src/views/LoginView.vue` | 登录页面 | 22.7.2 |
| `src/views/EmployeeList.vue` | 员工CRUD页面 | 22.7.3 |

### 后端需要的接口清单

EMS v6前端需要后端提供以下RESTful API：

| 方法 | URL | 说明 | 请求体 | 响应 |
|------|-----|------|--------|------|
| POST | `/api/v1/auth/login` | 登录 | `{username, password}` | `{token, username}` |
| GET | `/api/v1/employees` | 分页查询 | 查询参数 | `PageResult<EmployeeVO>` |
| GET | `/api/v1/employees/{id}` | 查询详情 | - | `EmployeeVO` |
| POST | `/api/v1/employees` | 创建员工 | `EmployeeCreateDTO` | `EmployeeVO` |
| PUT | `/api/v1/employees/{id}` | 全量更新 | `EmployeeUpdateDTO` | `EmployeeVO` |
| DELETE | `/api/v1/employees/{id}` | 删除员工 | - | 204 |

这些接口在第15-20章已经实现（EMS v5），前端直接对接即可。

### 启动与验证

1. **启动后端**：运行Spring Boot应用（端口8080）
2. **启动前端**：`npm run dev`（端口5173）
3. 访问`http://localhost:5173`，登录后进入员工管理页面
4. 测试完整CRUD流程：搜索→新增→编辑→删除→分页

### EMS版本演进回顾

| 版本 | 章节 | 交付物 | 技术栈 |
|------|------|--------|--------|
| EMS v1 | 第1-7章 | 命令行员工CRUD | Java SE |
| EMS v2 | 第8-9章 | JDBC+MySQL版 | JDBC/Druid |
| EMS v3 | 第10-12章 | Spring版重构 | Spring IoC/AOP/MVC |
| EMS v4 | 第13-14章 | MyBatis/JPA版 | MyBatis/JPA |
| EMS v5 | 第15-19章 | Spring Boot后端API | Spring Boot/RESTful |
| **EMS v6** | **第20-22章** | **Vue前端全栈** | **Vue 3/Element Plus/Axios** |

---

## 22.8 本章小结

本章从零开始构建了EMS前端应用，核心收获：

1. **Vue 3项目创建**：使用Vite + `npm create vue@latest`创建项目，理解SFC单文件组件（template + script setup + style scoped）
2. **Composition API核心**：`ref()`（基本类型响应式，script中`.value`访问）、`reactive()`（对象响应式，不能替换整个对象）、`computed`（缓存计算）、`watch`/`watchEffect`（侦听器）、`onMounted`等生命周期钩子
3. **组件化**：`defineProps`（父→子，只读不可修改）、`defineEmits`（子→父）、插槽slot
4. **Vue Router**：路由配置、`router-link`/`router-view`、编程式导航、路由守卫（登录拦截）
5. **Axios封装**：创建实例（baseURL/timeout）、请求拦截器（自动添加Token）、响应拦截器（解包Result格式、统一错误处理、401跳登录）、避免死循环
6. **Element Plus**：el-table（数据表格+自定义列+操作按钮）、el-form（表单+校验规则）、el-dialog（弹窗编辑）、el-pagination（分页）
7. **前后端联调**：Vite代理解决开发环境跨域（生产环境用Nginx）、完整登录流程、完整CRUD流程
8. **EMS v6交付**：Vue 3前端 + Spring Boot后端全栈版，前后端通过RESTful API + JSON交互

---

## 思考题

1. 以下Vue 3代码有什么问题？请修正：
   ```vue
   <script setup>
   import { reactive } from 'vue'
   const employee = reactive({ name: '张三', age: 25 })
   
   function reset() {
     employee = { name: '', age: 0 }
   }
   </script>
   ```

2. 你的Axios响应拦截器中，401状态码会跳转登录页。但用户反馈：登录页面本身也会弹出"登录已过期"的错误提示。请分析原因并修复。

3. 以下代码中，`<template>`里能正确显示count的值吗？为什么？
   ```vue
   <script setup>
   import { ref } from 'vue'
   let count = ref(0)
   count = count.value + 1
   </script>
   <template>
     <p>{{ count }}</p>
   </template>
   ```

4. 你的Vue前端项目打包部署到Nginx后，刷新页面出现404。但开发环境（`npm run dev`）中刷新是正常的。请分析原因并给出Nginx配置修复方案。

5. 请设计一个Pinia store来管理用户登录状态（token、username、登录/登出方法），并在路由守卫和Axios拦截器中使用它。

---

<details>
<summary>思考题参考答案（点击展开）</summary>

**第1题**：

问题：`reactive`对象不能直接赋值替换，`employee = { name: '', age: 0 }`会丢失响应性（且`const`声明不能重新赋值，会直接报错）。

修正方案：

```javascript
// 方案1：逐个属性重置
function reset() {
  employee.name = ''
  employee.age = 0
}

// 方案2：Object.assign
function reset() {
  Object.assign(employee, { name: '', age: 0 })
}

// 方案3（推荐）：改用ref
const employee = ref({ name: '张三', age: 25 })
function reset() {
  employee.value = { name: '', age: 0 }  // ref可以替换整个值
}
```

**第2题**：

原因：登录页面的API请求（如获取验证码、提交登录）也经过了响应拦截器。如果这些请求返回401（比如Token无效但登录页仍然携带了旧Token），拦截器会弹出"登录已过期"的提示。

修复方案：在拦截器中排除登录相关接口：

```javascript
if (status === 401) {
  const url = error.config.url
  // 排除登录相关接口
  if (url && !url.includes('/auth/login') && !url.includes('/auth/captcha')) {
    ElMessage.error('登录已过期，请重新登录')
    localStorage.removeItem('token')
    router.push('/login')
  }
}
```

更好的做法：登录接口不携带Token。在请求拦截器中，如果URL是登录相关接口，就不添加Authorization头。

**第3题**：

不能。`let count = ref(0)`创建了一个ref，但紧接着`count = count.value + 1`把`count`重新赋值为数字`1`（不再是ref）。模板中`{{ count }}`显示的是`1`，但它不再是响应式的——后续修改`count`不会触发视图更新。

正确写法：

```javascript
const count = ref(0)
count.value = count.value + 1  // 通过.value修改，保持响应性
```

**第4题**：

原因：Vue是SPA（单页应用），所有路由都由前端处理。开发环境Vite会自动将未匹配的请求回退到`index.html`。但Nginx默认会尝试匹配文件路径，找不到就返回404。

例如：访问`/employees`，Nginx去找`/opt/ems-frontend/dist/employees`这个文件，找不到就返回404。但实际应该返回`index.html`，让Vue Router处理路由。

修复方案：在Nginx配置中添加`try_files`：

```nginx
location / {
    root /opt/ems-frontend/dist;
    try_files $uri $uri/ /index.html;  # 找不到文件时回退到index.html
}
```

**第5题**：

```javascript
// src/stores/user.js
import { defineStore } from 'pinia'
import { ref } from 'vue'
import request from '@/utils/request'
import router from '@/router'

export const useUserStore = defineStore('user', () => {
  const token = ref(localStorage.getItem('token') || '')
  const username = ref(localStorage.getItem('username') || '')

  async function login(loginForm) {
    const data = await request.post('/v1/auth/login', loginForm)
    token.value = data.token
    username.value = data.username
    localStorage.setItem('token', data.token)
    localStorage.setItem('username', data.username)
  }

  function logout() {
    token.value = ''
    username.value = ''
    localStorage.removeItem('token')
    localStorage.removeItem('username')
    router.push('/login')
  }

  return { token, username, login, logout }
})
```

路由守卫中使用：

```javascript
import { useUserStore } from '@/stores/user'

router.beforeEach((to, from, next) => {
  const userStore = useUserStore()
  if (to.name !== 'Login' && !userStore.token) {
    next({ name: 'Login' })
  } else {
    next()
  }
})
```

Axios拦截器中使用：

```javascript
import { useUserStore } from '@/stores/user'

request.interceptors.request.use((config) => {
  const userStore = useUserStore()
  if (userStore.token) {
    config.headers.Authorization = `Bearer ${userStore.token}`
  }
  return config
})
```

</details>

---

> **下一篇预告**：EMS v6已经实现了前后端全栈联调，但有一个严重的安全隐患——目前的登录只是简单的用户名密码验证，Token也没有加密，任何人都能伪造。第23章将全面学习Spring Security认证与授权体系，实现数据库用户认证、RBAC权限模型、方法级权限控制。第24章将引入JWT令牌，实现无状态认证和Token刷新机制，交付EMS v7——权限安全版。
