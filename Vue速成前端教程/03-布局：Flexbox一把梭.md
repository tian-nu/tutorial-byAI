# 布局：Flexbox 一把梭

- 对应文档版本：N/A（入门教程）
- 适用环境：任意现代浏览器，VS Code
- 读者角色：掌握 HTML + CSS 基础的前端新手
- 预计耗时：新手 1 小时 / 熟手 15 分钟
- 前置教程：[01-HTML：网页的骨架](01-HTML：网页的骨架/)、[02-CSS：让网页变好看](02-CSS：让网页变好看/)
- 可视化：无

---

## 🎯 学完能做什么

- 用 Flexbox 三行代码实现完美的水平/垂直居中
- 用 `justify-content` 和 `align-items` 控制子元素的对齐方式
- 做横向导航栏、卡片列表自动换行、经典 header-main-footer 布局
- 用 `gap` 统一设置子元素间距，告别 margin 计算

---

## 🧩 前置条件

| 前置项 | 说明 |
|--------|------|
| HTML | 能写出带 class 的 div 嵌套结构 |
| CSS | 理解盒模型、margin/padding、class 选择器 |
| 文件 | 准备好 `index.html` 和 `style.css` 的练习环境 |

---

## 📖 分步操作

# 步骤 1：为什么 Flexbox——一个痛点让你理解它

先看一个经典需求：**把一个 div 在页面中水平垂直居中**。

在 Flexbox 诞生之前（2009 年以前），前端开发者是这样做的：

```css
/* ❌ 旧时代：用各种 hack 居中 */
.center-box {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}
```

你不需要理解上面这段代码——它很丑、很绕，而且有各种副作用（脱离文档流、父元素高度塌陷等）。

**用 Flexbox 只需要三行**：

```css
.parent {
  display: flex;
  justify-content: center;  /* 水平居中 */
  align-items: center;      /* 垂直居中 */
}
```

### Flexbox 的直觉类比

把 Flexbox 想象成**机场行李传送带**：

- 传送带有一个方向（主轴）：行李沿着传送带前进。
- 传送带上的行李可以靠左、靠右、居中、分散。
- 行李之间可以自动留出间距。
- 如果行李太多，可以自动换到下一行。

**Flexbox = Flexible Box Layout（弹性盒子布局）**。它的核心思想是：**容器（父元素）决定子元素的排列方式，子元素自动适应。**

---

# 步骤 2：核心概念——主轴、交叉轴、容器、项目

在 Flexbox 世界中，一切围绕两根轴展开：

```
主轴方向：row（默认）→→→→→→→→→→→→→→→→→→→→→→→→→

交叉轴：↓
        ↓
        ↓
        ↓
```

### 2.1 两个角色

| 角色 | 说明 | CSS |
|------|------|-----|
| **Flex 容器** | 设置了 `display: flex;` 的父元素 | `display: flex;` |
| **Flex 项目** | 容器内的直接子元素 | 自动成为 flex 项目 |

```html
<div class="container">     <!-- 这是 Flex 容器 -->
  <div class="item">A</div> <!-- 这是 Flex 项目 -->
  <div class="item">B</div> <!-- 这也是 Flex 项目 -->
  <div class="item">C</div>
</div>
```

> ⚠️ **重要**：只有**直接子元素**会成为 Flex 项目。孙子元素不受影响，除非孙子元素自己的父元素也设置了 `display: flex`。

### 2.2 两根轴

| 轴 | 默认方向 | 比喻 |
|-----|---------|------|
| **主轴（main axis）** | 从左到右 → | 行李传送带的前进方向 |
| **交叉轴（cross axis）** | 从上到下 ↓ | 垂直于传送带的方向 |

所有排列、对齐属性都是围绕这两根轴工作的。

> 🤔 **想多一点**：Flexbox 把 CSS 布局从"二维思维"变成了"一维思维"。传统布局（float、position）需要同时考虑水平和垂直方向，而 Flexbox 让你专注于"主轴"这一维，交叉轴的对齐是顺手的事。这就像从一个需要同时看两张地图的导航，变成了只需要看一张地图——心智负担大幅降低。

---

# 步骤 3：容器属性——控制"传送带"的行为

以下属性全部写在**容器**（父元素）上。

### 3.1 `display: flex` — 开启 Flexbox

```css
.container {
  display: flex;
}
```

写下这一行，容器内的子元素立刻从"竖着排列"变成"横着排列"。

### 3.2 `flex-direction` — 主轴方向

```css
.container {
  display: flex;
  flex-direction: row;            /* 默认：主轴从左到右 */
  /* flex-direction: row-reverse;  主轴从右到左 */
  /* flex-direction: column;       主轴从上到下 */
  /* flex-direction: column-reverse; 主轴从下到上 */
}
```

| 值 | 主轴方向 | 交叉轴自动变成 |
|-----|---------|-------------|
| `row`（默认） | 左 → 右 | 上 → 下 |
| `row-reverse` | 右 → 左 | 上 → 下 |
| `column` | 上 → 下 | 左 → 右 |
| `column-reverse` | 下 → 上 | 左 → 右 |

### 3.3 `justify-content` — 主轴对齐

控制子元素在**主轴**上的排列方式：

```css
.container {
  display: flex;
  justify-content: flex-start;   /* 默认：靠左 */
  /* justify-content: flex-end;    靠右 */
  /* justify-content: center;      居中 */
  /* justify-content: space-between; 两端对齐，中间均分 */
  /* justify-content: space-around;  每个项目两侧间距相等 */
  /* justify-content: space-evenly;  所有间距完全相等 */
}
```

**图示对比**（以 `flex-direction: row` 为例）：

```
flex-start:    [A][B][C]..............
center:        ......[A][B][C]......
flex-end:      ..............[A][B][C]
space-between: [A]......[B]......[C]
space-around:  ..[A]....[B]....[C]..
space-evenly:  ...[A]...[B]...[C]...
```

### 3.4 `align-items` — 交叉轴对齐

控制子元素在**交叉轴**上的排列方式：

```css
.container {
  display: flex;
  align-items: stretch;    /* 默认：拉伸填满容器高度 */
  /* align-items: flex-start;  顶部对齐 */
  /* align-items: flex-end;    底部对齐 */
  /* align-items: center;      垂直居中 */
  /* align-items: baseline;    文字基线对齐 */
}
```

### 3.5 `flex-wrap` — 是否换行

```css
.container {
  display: flex;
  flex-wrap: nowrap;       /* 默认：不换行，可能溢出 */
  /* flex-wrap: wrap;        自动换行 */
  /* flex-wrap: wrap-reverse; 反向换行 */
}
```

### 3.6 `gap` — 统一间距（推荐！）

```css
.container {
  display: flex;
  gap: 20px;               /* 所有子元素之间统一 20px 间距 */
  /* gap: 20px 10px;        行间距 20px，列间距 10px */
  /* row-gap: 20px;         单独设行间距 */
  /* column-gap: 10px;      单独设列间距 */
}
```

`gap` 是 Flexbox 的"语法糖"——以前你需要用 `margin` 给每个子元素设间距，现在一行搞定。

---

# 步骤 4：实战一——导航栏：横排、两端对齐

需求：做一个横向导航栏，Logo 在左边，菜单项在右边。

### HTML

```html
<nav class="navbar">
  <div class="nav-logo">MySite</div>
  <div class="nav-links">
    <a href="#">首页</a>
    <a href="#">关于</a>
    <a href="#">联系</a>
  </div>
</nav>
```

### CSS

```css
.navbar {
  display: flex;
  justify-content: space-between;  /* Logo 和菜单两端对齐 */
  align-items: center;             /* 垂直居中 */
  padding: 15px 30px;
  background-color: #2c3e50;
  color: white;
}

.nav-logo {
  font-size: 24px;
  font-weight: bold;
}

.nav-links {
  display: flex;       /* 菜单项也变成一个 flex 容器 */
  gap: 20px;           /* 菜单项之间 20px 间距 */
}

.nav-links a {
  color: white;
  text-decoration: none;
}

.nav-links a:hover {
  color: #3498db;
}
```

### 效果

```
┌──────────────────────────────────────────────┐
│ MySite                    首页  关于  联系   │
└──────────────────────────────────────────────┘
```

> 🤔 **想多一点**：注意 `.nav-links` 自己也设了 `display: flex`。这就是 Flexbox 的嵌套能力——容器可以嵌套容器，每一层独立控制自己的子元素排列。就像俄罗斯套娃，每个娃里面还可以再装一个娃。

---

# 步骤 5：实战二——卡片列表：自动换行 + 等间距

需求：做一个 3 列卡片布局，屏幕变窄时自动变成 2 列或 1 列。

### HTML

```html
<div class="card-list">
  <div class="card">
    <h3>卡片 1</h3>
    <p>这是第一张卡片的内容。</p>
  </div>
  <div class="card">
    <h3>卡片 2</h3>
    <p>这是第二张卡片的内容。</p>
  </div>
  <div class="card">
    <h3>卡片 3</h3>
    <p>这是第三张卡片的内容。</p>
  </div>
  <div class="card">
    <h3>卡片 4</h3>
    <p>这是第四张卡片的内容。</p>
  </div>
  <div class="card">
    <h3>卡片 5</h3>
    <p>这是第五张卡片的内容。</p>
  </div>
  <div class="card">
    <h3>卡片 6</h3>
    <p>这是第六张卡片的内容。</p>
  </div>
</div>
```

### CSS

```css
.card-list {
  display: flex;
  flex-wrap: wrap;        /* 空间不够时自动换行 */
  gap: 20px;              /* 卡片之间统一 20px 间距 */
  padding: 20px;
}

.card {
  /* calc 计算：每行 3 个，减去 gap 占用的空间 */
  flex: 0 0 calc(33.333% - 14px);  /* 后文会解释 flex 属性 */
  /* 不设 flex 的简化写法：width: calc(33.333% - 14px); */
  padding: 20px;
  border: 1px solid #ddd;
  border-radius: 8px;
  background-color: white;
}
```

### `flex` 属性详解

`flex: 0 0 calc(33.333% - 14px);` 是三个属性的缩写：

| 缩写 | 全称 | 含义 | 比喻 |
|------|------|------|------|
| `0` | `flex-grow` | 不放大（有多余空间也不撑大） | 行李不会自动膨胀 |
| `0` | `flex-shrink` | 不缩小（空间不够也不缩小） | 行李不会自动压缩 |
| `calc(33.333% - 14px)` | `flex-basis` | 基础宽度 | 行李的标准尺寸 |

`calc(33.333% - 14px)` 的意思是：每行 3 个卡片（100% ÷ 3 = 33.333%），减去 gap 的空间。由于 `gap: 20px` 在 3 个卡片之间有 2 个缝隙（共 40px），每个卡片需要减掉约 40px ÷ 3 ≈ 13.33px，取 14px 近似。

### 效果

```
宽屏（3 列）：
┌──────────┐ ┌──────────┐ ┌──────────┐
│  卡片 1   │ │  卡片 2   │ │  卡片 3   │
└──────────┘ └──────────┘ └──────────┘
┌──────────┐ ┌──────────┐ ┌──────────┐
│  卡片 4   │ │  卡片 5   │ │  卡片 6   │
└──────────┘ └──────────┘ └──────────┘

窄屏（2 列）：
┌──────────────┐ ┌──────────────┐
│    卡片 1     │ │    卡片 2     │
└──────────────┘ └──────────────┘
```

---

# 步骤 6：实战三——经典页面布局：header / main+sidebar / footer

这是 90% 网站的基本布局骨架。

### HTML

```html
<div class="page">
  <header class="page-header">
    <h1>我的网站</h1>
  </header>
  <div class="page-body">
    <main class="page-main">
      <h2>主要内容</h2>
      <p>这里是文章内容区域。</p>
    </main>
    <aside class="page-sidebar">
      <h3>侧边栏</h3>
      <ul>
        <li>推荐文章</li>
        <li>标签云</li>
        <li>关于我</li>
      </ul>
    </aside>
  </div>
  <footer class="page-footer">
    <p>&copy; 2026 我的网站</p>
  </footer>
</div>
```

### CSS

```css
.page {
  display: flex;
  flex-direction: column;    /* 整体从上到下排列 */
  min-height: 100vh;         /* 至少占满整个屏幕高度 */
}

.page-header {
  background-color: #2c3e50;
  color: white;
  padding: 20px 30px;
}

.page-body {
  display: flex;             /* 主体区域横向排列 */
  flex: 1;                   /* 撑满剩余空间，把 footer 推到底部 */
  gap: 20px;
  padding: 20px;
}

.page-main {
  flex: 3;                   /* 占 3 份宽度 */
  background-color: white;
  padding: 20px;
  border-radius: 8px;
}

.page-sidebar {
  flex: 1;                   /* 占 1 份宽度 */
  background-color: #f5f5f5;
  padding: 20px;
  border-radius: 8px;
}

.page-footer {
  background-color: #2c3e50;
  color: #999;
  text-align: center;
  padding: 15px;
}
```

### 关键点解释

- `flex: 3` 和 `flex: 1`：相当于 `flex-grow` 的值。`page-main` 占 3 份，`page-sidebar` 占 1 份，总共 4 份。所以 main 占 75% 宽度，sidebar 占 25%。
- `min-height: 100vh`：`vh` 是 viewport height（视口高度）的单位。`100vh` = 整个浏览器窗口高度。这确保 footer 被推到页面底部。
- `flex: 1`（在 `.page-body` 上）：让 body 区域自动撑满 header 和 footer 之间的剩余空间。

---

# 步骤 7：常见错误排查

### ❌ 错误 1：搞反主轴和交叉轴

```css
/* 期望：子元素垂直居中 */
.container {
  display: flex;
  justify-content: center;   /* ❌ 这是主轴居中（水平），不是垂直！ */
}

/* ✅ 正确 */
.container {
  display: flex;
  align-items: center;       /* 这才是交叉轴（垂直）居中 */
}
```

**记住口诀**：
- `justify-content` → **jus**tify → 主轴（记忆：justify 的 j 像一条水平线）
- `align-items` → **align** → 交叉轴（记忆：align 的 a 像一座山，垂直方向）

### ❌ 错误 2：忘了设 `flex-wrap`

```css
.container {
  display: flex;
  /* 没有 flex-wrap: wrap; */
}
```

默认 `flex-wrap: nowrap`，子元素再多也不会换行，会挤在一起甚至溢出。

```css
.container {
  display: flex;
  flex-wrap: wrap;           /* ✅ 加上换行 */
}
```

### ❌ 错误 3：`gap` 在旧版浏览器不支持

`gap` 在 Flexbox 中的支持是从 2021 年左右才开始普及的（Safari 14.1+、Chrome 84+）。如果你的项目需要兼容老旧浏览器，可以用 `margin` 替代：

```css
/* 替代方案 */
.card-list .card {
  margin: 10px;
}
.card-list {
  margin: -10px;  /* 抵消边缘多余间距 */
}
```

### ❌ 错误 4：`align-items` 和 `align-content` 分不清

| 属性 | 作用 | 使用场景 |
|------|------|---------|
| `align-items` | 单行内所有项目的交叉轴对齐 | 只有一行（或 `nowrap`） |
| `align-content` | 多行之间的交叉轴对齐 | `flex-wrap: wrap` 且有多行 |

**简单判断**：只有一行 → 用 `align-items`；有多行 → 用 `align-content` 控制行与行之间的分布。

---

## 📋 完整代码清单

将以上三个实战合并到一个练习文件中：

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Flexbox 练习</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: Arial, "Microsoft YaHei", sans-serif; background-color: #fafafa; }

    /* ========== 导航栏 ========== */
    .navbar {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 15px 30px;
      background-color: #2c3e50;
      color: white;
    }
    .nav-logo { font-size: 24px; font-weight: bold; }
    .nav-links { display: flex; gap: 20px; }
    .nav-links a { color: white; text-decoration: none; }
    .nav-links a:hover { color: #3498db; }

    /* ========== 卡片列表 ========== */
    .card-list {
      display: flex;
      flex-wrap: wrap;
      gap: 20px;
      padding: 20px;
      max-width: 960px;
      margin: 0 auto;
    }
    .card {
      flex: 0 0 calc(33.333% - 14px);
      padding: 20px;
      border: 1px solid #ddd;
      border-radius: 8px;
      background-color: white;
    }
    .card h3 { margin-bottom: 10px; color: #2c3e50; }

    /* ========== 页面布局 ========== */
    .page {
      display: flex;
      flex-direction: column;
      min-height: 100vh;
    }
    .page-header {
      background-color: #2c3e50;
      color: white;
      padding: 20px 30px;
    }
    .page-body {
      display: flex;
      flex: 1;
      gap: 20px;
      padding: 20px;
      max-width: 960px;
      margin: 0 auto;
      width: 100%;
    }
    .page-main {
      flex: 3;
      background-color: white;
      padding: 20px;
      border-radius: 8px;
    }
    .page-sidebar {
      flex: 1;
      background-color: #f5f5f5;
      padding: 20px;
      border-radius: 8px;
    }
    .page-footer {
      background-color: #2c3e50;
      color: #999;
      text-align: center;
      padding: 15px;
    }
  </style>
</head>
<body>
  <!-- 导航栏 -->
  <nav class="navbar">
    <div class="nav-logo">MySite</div>
    <div class="nav-links">
      <a href="#">首页</a>
      <a href="#">关于</a>
      <a href="#">联系</a>
    </div>
  </nav>

  <!-- 页面主体 -->
  <div class="page-body">
    <main class="page-main">
      <h2>主要内容</h2>
      <p>使用 Flexbox 实现的经典页面布局。</p>

      <!-- 卡片列表 -->
      <div class="card-list" style="padding: 20px 0;">
        <div class="card"><h3>卡片 1</h3><p>Flexbox 三行居中。</p></div>
        <div class="card"><h3>卡片 2</h3><p>gap 统一间距。</p></div>
        <div class="card"><h3>卡片 3</h3><p>flex-wrap 自动换行。</p></div>
      </div>
    </main>
    <aside class="page-sidebar">
      <h3>侧边栏</h3>
      <ul>
        <li>推荐文章</li>
        <li>标签云</li>
        <li>关于我</li>
      </ul>
    </aside>
  </div>

  <!-- 页脚 -->
  <footer class="page-footer">
    <p>&copy; 2026 MySite</p>
  </footer>
</body>
</html>
```

---

## ✅ 最终验证

在浏览器中打开页面，确认：
- 导航栏：Logo 在左，菜单在右，垂直居中
- 卡片列表：3 列排列，间距均匀。缩小浏览器窗口，卡片自动变成 2 列或 1 列
- 页面布局：header 在顶部，中间是 main + sidebar（75% + 25%），footer 在底部
- 按 F12，在 Elements 面板中选中容器元素，Styles 面板旁边会有 Flexbox 图标（`display: flex` 旁边），点击可以在页面上可视化显示 Flex 布局的辅助线

---

## 🧠 术语附录

| 术语 | 解释 |
|------|------|
| **Flexbox** | 弹性盒子布局，CSS 的一维布局系统，2009 年提出，2017 年后广泛支持。 |
| **flex-direction** | 主轴方向，决定子元素排列方向（row / column）。 |
| **justify-content** | 主轴对齐方式，控制子元素在主轴上的分布（居中、两端对齐等）。 |
| **align-items** | 交叉轴对齐方式，控制子元素在交叉轴上的位置。 |
| **gap** | 子元素之间的统一间距，替代逐个设置 margin。 |
| **flex-wrap** | 是否允许子元素换行。默认 `nowrap`（不换行）。 |
| **flex** | `flex-grow`、`flex-shrink`、`flex-basis` 三个属性的缩写。 |
| **主轴** | Flexbox 中元素排列的主要方向，由 `flex-direction` 决定。 |
| **交叉轴** | 垂直于主轴的方向。 |
| **vh** | viewport height，视口高度单位，`100vh` = 整个浏览器窗口高度。 |

---

## 🚧 已知坑点与禁止事项

- **`justify-content` 和 `align-items` 不要搞反**：前者管主轴，后者管交叉轴。
- **默认不换行**：`flex-wrap` 默认是 `nowrap`，需要换行时必须显式写 `flex-wrap: wrap`。
- **只有直接子元素受 Flex 影响**：孙子元素不会自动成为 Flex 项目。
- **`gap` 在非常旧的浏览器中不支持**：如需兼容 IE11 等，用 `margin` 替代。
- **不要用 Float 布局了**：2026 年了，Flexbox 和 Grid 是现代布局的标准答案。

---

## 📖 下一步建议

完成这篇后，继续学习 **[04-JavaScript：让网页活起来](04-JavaScript：让网页活起来/)**，用 JavaScript 给网页添加交互能力。