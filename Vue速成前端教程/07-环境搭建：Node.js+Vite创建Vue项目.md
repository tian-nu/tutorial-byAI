# 07 - 环境搭建：Node.js + Vite 创建 Vue 项目

- **对应文档版本**：requirements.md v1.0
- **适用环境**：Windows / macOS / Linux，Node.js 18 LTS+
- **读者角色**：前端初学者
- **预计耗时**：新手 30 分钟 / 熟手 10 分钟
- **前置教程**：06-Vue是什么（纯概念，可跳过但建议阅读）
- **可视化**：无

---

## 一、目标与完成效果

**一句话目标**：在你的电脑上跑起第一个 Vue3 项目，看到 `localhost:5173` 的欢迎页面。

**完成后的可观测效果**：
- 浏览器打开 `http://localhost:5173`，看到 Vue 官方欢迎页
- 修改 `App.vue` 里的文字，浏览器自动刷新显示新内容
- 能说出项目里每个文件夹是干什么的

---

## 二、前置条件

- 一台能上网的电脑
- 会打开终端（Windows 用 PowerShell 或 CMD，macOS/Linux 用 Terminal）

**环境验证命令**（一条确认前置是否满足）：
```bash
node -v && npm -v
```
如果两条都输出了版本号（没有报错），可以直接跳到步骤三。

---

## 三、分步操作

### 步骤 1：安装 Node.js（LTS 版本）

> **我在做什么？** 安装 JavaScript 的运行环境 Node.js。Vue 的构建工具 Vite 基于 Node.js 运行，所以必须先装它。

打开浏览器，访问 Node.js 官网：

```
https://nodejs.org
```

你会看到两个下载按钮：
- **LTS**（Long Term Support，长期支持版）：稳定可靠，**选这个**
- **Current**（最新版）：功能新但可能有 Bug

点击左边的 **LTS** 按钮下载安装包。

安装过程一路点「Next」即可，所有选项保持默认。**特别注意**：安装界面如果有一个勾选框 "Automatically install the necessary tools"，勾上它（Windows 专属）。

> 🤔 **想多一点**：Node.js 最初是让 JavaScript 能在服务器上运行的，但 Vue 用它不是因为要写后端，而是因为 Vite（构建工具）需要在 Node.js 环境下运行，帮我们编译 `.vue` 文件、启动开发服务器、做热更新。

安装完成后，**关闭当前终端窗口，重新打开一个**（这步很重要，否则环境变量可能没刷新）。

---

### 步骤 2：验证 Node.js 和 npm 版本

> **我在做什么？** 确认安装成功，并记录版本号（后续排错时需要对照）。

在终端里输入：

```bash
node -v
```

预期输出类似：`v18.18.0` 或 `v20.11.0`（只要 ≥ 16 就行）。

再输入：

```bash
npm -v
```

预期输出类似：`9.8.1` 或 `10.2.0`。

> ✅ **做得对不对？** 两条命令都没有报 `command not found` 或 `'node' 不是内部或外部命令`，且版本号 ≥ 16，就成功了。

> ❌ **不对怎么办？**
>
> **错误 1：`'node' 不是内部或外部命令`**
> - 原因：安装后没重启终端
> - 解决：关闭终端 → 重新打开 → 再试一次。还不行就重启电脑。
>
> **错误 2：版本号低于 v16**
> - 原因：电脑里装了旧版 Node.js
> - 解决：去官网重新下载 LTS 版覆盖安装

---

### 步骤 3：用 npm 创建 Vue 项目

> **我在做什么？** 使用 Vue 官方脚手架命令创建一个模板项目。

在终端里，先 `cd` 到你想要存放项目的文件夹（比如桌面或文档目录），然后运行：

```bash
npm create vue@latest blog-frontend
```

这条命令会下载最新版 Vue 脚手架并创建一个叫 `blog-frontend` 的文件夹。

> 🤔 **想多一点**：`npm create vue@latest` 等价于「帮我去 npm 仓库拿最新版的 create-vue 工具来创建一个 Vue 项目」。`blog-frontend` 是项目名，你可以改成任何名字，但建议全小写 + 连字符（这是前端项目命名惯例）。

---

### 步骤 4：选择项目配置

> **我在做什么？** 回答脚手架的一系列问题，选择你要安装的功能。

运行上一步命令后，终端会逐个问你问题。按下面选择：

| 问题 | 你的选择 | 为什么 |
|---|---|---|
| Add TypeScript? | **No** | 本系列用 JavaScript，减少学习负担 |
| Add JSX Support? | **No** | JSX 是 React 风格语法，Vue 用模板更地道 |
| Add Vue Router? | **Yes** | 后面做多页面博客需要路由 |
| Add Pinia? | **Yes** | 后面做登录、全局状态需要状态管理 |
| Add Vitest? | **No** | 单元测试工具，本系列不涉及 |
| Add End-to-End Testing? | **No** | E2E 测试，本系列不涉及 |
| Add ESLint? | **No** | 代码检查工具，初学阶段先不引入 |
| Add Prettier? | **No** | 代码格式化工具，同上 |

**用键盘 ↑↓ 箭头切换选项，回车确认。**

选完之后脚手架会自动下载依赖，生成项目文件。

> ✅ **做得对不对？** 看到 `Scaffolding project in blog-frontend... Done.` 类似的提示，没有报红字错误。

---

### 步骤 5：进入项目并安装依赖

> **我在做什么？** 脚手架只是创建了项目结构和 `package.json`，还需要实际下载依赖包。

```bash
cd blog-frontend
npm install
```

这条命令会根据 `package.json` 里的列表，把 Vue、Vue Router、Pinia、Vite 等库下载到 `node_modules` 文件夹。

> ✅ **做得对不对？** 看到进度条跑完，末尾没有 `ERR!` 或红色报错。文件夹里多了一个 `node_modules`。

> ❌ **不对怎么办？**
>
> **错误：`npm install` 卡住或报 timeout**
> - 原因：国内网络访问 npm 官方源慢
> - 解决：换成淘宝镜像源，运行：
>   ```bash
>   npm config set registry https://registry.npmmirror.com
>   npm install
>   ```
>   装完后如果想恢复官方源：
>   ```bash
>   npm config set registry https://registry.npmjs.org
>   ```

---

### 步骤 6：启动开发服务器

> **我在做什么？** 启动 Vite 开发服务器，在浏览器里看到你的 Vue 项目。

```bash
npm run dev
```

终端会输出类似：

```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
```

用浏览器打开 `http://localhost:5173/`。

你应该看到一个 Vue 欢迎页面，中间有个大 Logo，旁边写着 "You did it!" 之类的文字。

> ✅ **做得对不对？** 浏览器里看到页面了，地址栏是 `localhost:5173`，不是 404 或报错。

> ❌ **不对怎么办？**
>
> **错误：端口 5173 被占用**
> - 现象：终端报 `Port 5173 is already in use`
> - 解决：Vite 会自动尝试下一个端口（5174、5175…），看终端实际显示的端口号
>
> **错误：浏览器显示「无法访问此网站」**
> - 原因：开发服务器没启动，或终端报错了
> - 解决：回到终端看报错信息，最常见是依赖没装完，重新 `npm install`

---

### 步骤 7：认识项目结构

> **我在做什么？** 快速了解项目里每个文件夹是干嘛的，后面会频繁用到。

停止开发服务器（在终端按 `Ctrl + C`），用 VS Code（或任意编辑器）打开 `blog-frontend` 文件夹。你会看到这样的结构：

```
blog-frontend/
├── index.html              # 入口 HTML，Vite 从这里启动
├── package.json            # 项目配置，记录依赖和脚本
├── vite.config.js          # Vite 配置文件
├── node_modules/           # 下载的第三方库（不用管，别手动改）
├── public/                 # 静态资源（不会被编译，直接复制到最终输出）
└── src/                    # ⭐ 你写代码的地方
    ├── App.vue             # 根组件
    ├── main.js             # 应用入口，初始化 Vue
    ├── components/         # 存放可复用的组件
    ├── views/              # 存放页面级组件
    ├── router/             # Vue Router 路由配置
    ├── stores/             # Pinia 状态管理
    └── assets/             # 图片、CSS 等资源（会被编译处理）
```

| 文件/文件夹 | 一句话作用 | 你之后会改吗 |
|---|---|---|
| `index.html` | 项目的 HTML 入口，Vite 会自动注入 `<script>` | 偶尔改标题 |
| `src/main.js` | 创建 Vue 应用，挂载 Router、Pinia | 加新插件时改 |
| `src/App.vue` | 所有页面的「外壳」组件 | **经常改** |
| `src/components/` | 放可复用的组件（按钮、卡片、导航栏） | **经常放文件** |
| `src/views/` | 放页面级组件（首页、关于页、文章页） | **经常放文件** |
| `src/router/` | 配置 URL 和页面的对应关系 | 加新页面时改 |
| `src/stores/` | 全局共享数据（登录状态等） | 需要共享数据时改 |
| `src/assets/` | 图片、字体、全局 CSS | 加资源时放文件 |

---

### 步骤 8：打开 App.vue，认识 SFC（单文件组件）

> **我在做什么？** 打开 `src/App.vue`，看看一个 Vue 组件文件长什么样。

用编辑器打开 `src/App.vue`，你会看到三个区块：

```vue
<!-- 第一部分：模板（Template）——写 HTML 结构 -->
<template>
  <div>
    <h1>Hello Vue!</h1>
  </div>
</template>

<!-- 第二部分：脚本（Script）——写 JS 逻辑 -->
<script setup>
// 这里写数据、方法、逻辑
</script>

<!-- 第三部分：样式（Style）——写 CSS -->
<style scoped>
/* scoped 表示这个样式只对当前组件生效 */
h1 {
  color: blue;
}
</style>
```

这就是 **SFC（Single File Component，单文件组件）**——一个 `.vue` 文件就是一个完整的组件，自带 HTML、JS、CSS，各回各家互不干扰。

> 🤔 **想多一点**：`scoped` 是 Vue 的魔法属性。加上它，你在 `App.vue` 里写的 `h1 { color: blue }` 就只影响 `App.vue` 里的 `<h1>`，不会把别的组件里的 `<h1>` 也染蓝。它背后的原理是 Vue 自动给每个元素加了独一无二的 `data-v-xxxxx` 属性来区分范围。

---

### 步骤 9：修改文字，体验「热更新」

> **我在做什么？** 改一行代码，验证浏览器是否自动刷新——这就是热更新。

**先确认开发服务器在运行**（否则运行 `npm run dev`）。

在 `App.vue` 的 `<template>` 里，找到任意一段文字，改成：

```vue
<template>
  <div>
    <h1>🎉 我的第一个 Vue 项目跑起来了！</h1>
    <p>修改这段文字，保存后浏览器会自动刷新</p>
  </div>
</template>
```

按 `Ctrl + S` 保存。

**切换到浏览器**，不要手动刷新——你会发现页面已经自动变成新内容了。

> ✅ **做得对不对？** 保存后浏览器自动更新，显示你刚改的文字。

> ❌ **不对怎么办？**
> - 如果浏览器没变化：检查终端是否在运行 `npm run dev`，是否报错
> - 如果终端报错：通常是 `<template>` 里写错了 HTML（比如标签没闭合），检查修改的位置

这就是 **热更新（Hot Module Replacement, HMR）**：Vite 检测到你保存文件，只替换改动的部分，不用整个页面刷新，保留你在页面上的操作状态。

---

## 四、完整代码清单

### `src/App.vue`（验证用，最终状态）

```vue
<template>
  <div>
    <h1>🎉 我的第一个 Vue 项目跑起来了！</h1>
    <p>修改这段文字，保存后浏览器会自动刷新</p>
  </div>
</template>

<script setup>
// 暂时什么都不写，后面会加逻辑
</script>

<style scoped>
h1 {
  color: #42b883; /* Vue 官方绿色 */
}
</style>
```

---

## 五、验证方法

运行以下命令，确认一切正常：

```bash
# 进入项目目录
cd blog-frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

浏览器访问 `http://localhost:5173/`，看到你的文字即表示成功。

---

## 六、已知坑点与禁止事项

| 坑点 | 现象 | 解决 |
|---|---|---|
| Node 版本太低 | Vite 报错 `requires Node.js version >=18` | 去官网装最新 LTS |
| npm install 超时 | 卡住不动或报 `ETIMEDOUT` | 换成淘宝镜像 `registry.npmmirror.com` |
| 忘记 `cd blog-frontend` | 终端报 `no such file` | 先 `cd` 进项目目录再 `npm install` |
| 没有重启终端 | `node -v` 报找不到命令 | 关了重开终端，再不行重启电脑 |

---

## 七、术语附录

| 术语 | 解释 |
|---|---|
| **Node.js** | 让 JavaScript 脱离浏览器运行的环境。Vue 的构建工具（Vite）依赖它来编译代码、启动服务器 |
| **npm** | Node Package Manager，Node.js 自带的包管理器。`npm install` 下载依赖，`npm run dev` 执行脚本 |
| **Vite** | Vue 官方推荐的构建工具。提供极快的开发服务器、热更新、打包上线功能。法语意为「快」 |
| **SFC** | Single File Component，单文件组件。一个 `.vue` 文件包含 `<template>`（HTML）、`<script>`（JS）、`<style>`（CSS）三部分 |
| **scoped** | `<style>` 标签的一个属性。加了 `scoped`，这个组件写的样式只影响自己，不会污染别的组件 |
| **热更新（HMR）** | Hot Module Replacement。保存代码后浏览器自动更新，不用手动刷新，且保留页面当前状态 |

---

## 八、下一步建议

项目跑起来了！下一步我们学习 Vue 的核心概念——**组件**，理解怎么像搭乐高一样搭页面。

👉 继续阅读：**08-组件：搭积木**