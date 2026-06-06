# CSS：让网页变好看

- 对应文档版本：N/A（入门教程）
- 适用环境：任意浏览器，VS Code，已掌握 HTML 基础
- 读者角色：有 HTML 基础的前端新手
- 预计耗时：新手 1.5 小时 / 熟手 20 分钟
- 前置教程：[01-HTML：网页的骨架](01-HTML：网页的骨架/)
- 可视化：无

---

## 🎯 学完能做什么

- 用三种方式给 HTML 页面添加样式
- 用 class 选择器、id 选择器、后代选择器精准选中目标元素
- 用颜色、字体、宽高、边距等属性美化页面
- 打开 F12 的 Styles 面板实时调试 CSS
- 理解盒模型，知道为什么有时候宽高不生效

---

## 🧩 前置条件

| 前置项 | 说明 |
|--------|------|
| HTML 基础 | 能写出带 class / id 的标签，理解嵌套关系 |
| VS Code | 已安装 |
| 浏览器 | Chrome / Edge / Firefox |

### 环境验证

在 `index.html`（上一节教程创建的）的 `<body>` 中确认有以下内容：

```html
<h1 class="main-title">Hello，世界！</h1>
<p id="intro">这是我的第一个 HTML 页面。</p>
```

能双击在浏览器中打开即可。

---

## 📖 分步操作

# 步骤 1：CSS 是什么——给 HTML 穿衣服

还记得上一节我们把 HTML 比喻成骨架吗？那 **CSS** 就是给它穿的衣服。

- HTML 说：**"这里有一个标题。"**
- CSS 说：**"这个标题用红色、36px 大小、加粗显示。"**

**CSS** = Cascading Style Sheets，层叠样式表。三个关键词：

| 关键词 | 含义 | 比喻 |
|--------|------|------|
| **Cascading（层叠）** | 多条规则可以叠加，后写的覆盖先写的 | 冬天穿衣服：先穿秋衣（底层），再穿毛衣，最后穿外套（最外层） |
| **Style（样式）** | 颜色、大小、位置、边框……一切视觉相关 | 衣服的颜色、款式、尺码 |
| **Sheets（表）** | 样式写在一个独立的文件或区块里 | 一本穿搭手册，记录每件衣服怎么搭配 |

一个最简单的 CSS 规则长这样：

```css
h1 {
  color: red;
  font-size: 36px;
}
```

- `h1` — **选择器**：我要给谁穿这件衣服？
- `{ }` — **声明块**：这件衣服长什么样？
- `color: red;` — **声明**：属性是颜色，值是红色。
- `font-size: 36px;` — **声明**：属性是字号，值是 36 像素。

> 🤔 **想多一点**：CSS 为什么叫"层叠"？因为同一个元素可以被多条规则命中。比如 `<h1 class="main-title">` 可以被 `h1 { }` 选中，也可以被 `.main-title { }` 选中。两条规则会"层叠"在一起，冲突时按优先级决定最终效果。这个"层叠"机制是 CSS 最核心也最容易让人困惑的地方——后面会详细讲。

---

# 步骤 2：三种引入 CSS 的方式

### 方式一：行内样式（inline style）

直接写在标签的 `style` 属性里：

```html
<h1 style="color: red; font-size: 36px;">红色标题</h1>
```

**优点**：立即见效，不用额外文件。
**缺点**：每个标签都要单独写，改一个颜色得翻遍所有标签。**几乎不推荐。**

### 方式二：内部样式表（`<style>` 标签）

写在 HTML 的 `<head>` 里：

```html
<head>
  <style>
    h1 {
      color: red;
      font-size: 36px;
    }
  </style>
</head>
```

**优点**：所有样式集中管理，不需要额外文件。
**缺点**：只对当前页面生效，多个页面之间无法共享。

### 方式三：外部样式表（推荐！）

把 CSS 写在一个独立的 `.css` 文件里，然后在 HTML 中用 `<link>` 引入：

**index.html**：
```html
<head>
  <link rel="stylesheet" href="style.css">
</head>
```

**style.css**：
```css
h1 {
  color: red;
  font-size: 36px;
}
```

**优点**：一个 CSS 文件可以被多个页面共享，修改一处全局生效。浏览器会缓存 CSS 文件，第二次访问更快。**这是生产环境的标准做法。**

### 三种方式对比

| 方式 | 位置 | 复用性 | 推荐度 |
|------|------|--------|--------|
| 行内样式 | 标签的 `style` 属性 | 无 | ⭐ |
| 内部样式表 | `<head>` 中的 `<style>` | 当前页面 | ⭐⭐ |
| 外部样式表 | 独立 `.css` 文件 + `<link>` | 全站 | ⭐⭐⭐ |

### 动手做

1. 在 `index.html` 同级目录下新建 `style.css`。
2. 在 `index.html` 的 `<head>` 中添加 `<link rel="stylesheet" href="style.css">`。
3. 在 `style.css` 中写：

```css
h1 {
  color: darkblue;
}
```

4. 保存所有文件，刷新浏览器，标题应该变成深蓝色。

### 我做得对不对？

- 刷新后标题颜色变了。
- 在 F12 → Elements 面板中选中 `<h1>`，右侧 Styles 面板会显示 `h1 { color: darkblue; }` 来自 `style.css`。

---

# 步骤 3：选择器——精准定位你要打扮的元素

选择器 = CSS 的"瞄准镜"。你必须告诉浏览器"我要给谁穿这件衣服"。

### 3.1 标签选择器

选中页面上所有同类型的标签：

```css
p {
  color: gray;
}
```

页面上**所有** `<p>` 标签都会变成灰色。

### 3.2 class 选择器（`.`）

选中所有 `class="xxx"` 的元素：

```css
.card {
  border: 1px solid #ccc;
  padding: 20px;
}
```

```html
<div class="card">卡片1</div>
<div class="card">卡片2</div>
<!-- 两个都会被选中 -->
```

**class 选择器是日常开发中最常用的选择器。** 一个元素可以有多个 class：

```html
<div class="card highlight">重点卡片</div>
```

```css
.card { border: 1px solid #ccc; }
.highlight { background-color: yellow; }
/* 两条规则都会生效，层叠在一起 */
```

### 3.3 id 选择器（`#`）

选中具有特定 id 的唯一元素：

```css
#hero-banner {
  width: 100%;
  height: 300px;
}
```

```html
<div id="hero-banner">主横幅</div>
```

### 3.4 后代选择器

选中某个元素内部的所有指定后代：

```css
/* 选中 .article 内部的所有 p 标签 */
.article p {
  line-height: 1.8;
}
```

```html
<div class="article">
  <p>这段文字的行高是 1.8。</p>
  <div>
    <p>嵌套在里面的 p 也会被选中！</p>
  </div>
</div>
```

> ⚠️ 后代选择器用空格分隔。`.article p` 的意思是"class 为 article 的元素内部的所有 p 标签"，不管嵌套多深。

### 3.5 选择器速查表

| 选择器 | 写法 | 选中 | 比喻 |
|--------|------|------|------|
| 标签 | `p` | 所有 `<p>` | "所有穿红衣服的人" |
| class | `.card` | 所有 `class="card"` | "所有戴工牌的人" |
| id | `#logo` | `id="logo"` 的那个元素 | "工号 007 的那个人" |
| 后代 | `.nav a` | `.nav` 内部所有 `<a>` | "办公室里的所有人" |
| 多选 | `h1, h2, h3` | 所有 h1、h2、h3 | "张三、李四、王五" |

> 🤔 **想多一点**：为什么 class 和 id 选择器用不同的符号？因为它们在 HTML 中被设计为不同的概念。class 是"分类"——你可以给很多元素分到同一个类；id 是"身份"——每个元素只有一个唯一身份。CSS 用 `.` 和 `#` 来区分这两个概念，让你一眼就能看出选择器是瞄准"一类人"还是"一个人"。

---

# 步骤 4：常用 CSS 属性——调色盘

### 4.1 颜色相关

```css
/* 文字颜色 */
color: #333333;           /* 十六进制：最常用 */
color: rgb(51, 51, 51);   /* RGB */
color: red;               /* 颜色名：仅限基础颜色 */

/* 背景颜色 */
background-color: #f5f5f5;
background-color: lightblue;

/* 背景图片 */
background-image: url('bg.jpg');
```

### 4.2 字体相关

```css
font-size: 16px;          /* 字号 */
font-weight: bold;        /* 粗细：normal, bold, 100-900 */
font-family: Arial, sans-serif;  /* 字体族：从左到右依次尝试 */
text-align: center;       /* 对齐：left, center, right */
line-height: 1.6;         /* 行高：无单位数字表示字号的倍数 */
text-decoration: none;    /* 去掉下划线（常用于 a 标签） */
```

### 4.3 尺寸相关

```css
width: 300px;             /* 宽度 */
height: 200px;            /* 高度 */
max-width: 600px;         /* 最大宽度：屏幕变小时自动缩小 */
min-height: 100px;        /* 最小高度 */
```

### 4.4 边距相关（重点！）

```css
/* 外边距：元素与元素之间的距离 */
margin: 20px;                   /* 四边都是 20px */
margin: 10px 20px;              /* 上下 10px，左右 20px */
margin: 10px 20px 30px 40px;    /* 上 右 下 左（顺时针） */
margin-top: 10px;               /* 单独设置某一边 */

/* 内边距：元素内容与边框之间的距离 */
padding: 20px;
padding: 10px 20px;
padding-left: 15px;

/* 边框 */
border: 1px solid #ccc;         /* 宽度 样式 颜色 */
border-radius: 8px;             /* 圆角 */
```

### 4.5 动手练习

在 `style.css` 中写：

```css
body {
  font-family: Arial, sans-serif;
  background-color: #fafafa;
  margin: 0;
  padding: 0;
}

.main-title {
  color: #2c3e50;
  text-align: center;
  font-size: 32px;
  margin-top: 40px;
}

.card {
  width: 300px;
  margin: 20px auto;       /* 上下 20px，左右自动（居中） */
  padding: 20px;
  border: 1px solid #ddd;
  border-radius: 8px;
  background-color: white;
}

.card a {
  color: #3498db;
  text-decoration: none;
}
```

然后在 HTML 中给对应元素加上 class，刷新查看效果。

---

# 步骤 5：盒模型——CSS 世界的基本法则

CSS 把每个元素看作一个**矩形盒子**。这个盒子由四层组成，从内到外：

```
┌─────────────────────────────────┐
│          margin（外边距）         │
│  ┌───────────────────────────┐  │
│  │     border（边框）         │  │
│  │  ┌─────────────────────┐  │  │
│  │  │  padding（内边距）   │  │  │
│  │  │  ┌───────────────┐  │  │  │
│  │  │  │ content（内容）│  │  │  │
│  │  │  │  文字/图片     │  │  │  │
│  │  │  └───────────────┘  │  │  │
│  │  └─────────────────────┘  │  │
│  └───────────────────────────┘  │
└─────────────────────────────────┘
```

### 5.1 四层比喻

| 层 | CSS 属性 | 比喻 |
|-----|---------|------|
| **content** | `width`, `height` | 照片本身 |
| **padding** | `padding` | 照片周围的留白卡纸 |
| **border** | `border` | 相框 |
| **margin** | `margin` | 相框和隔壁相框之间的墙间距 |

### 5.2 标准盒模型 vs 怪异盒模型

默认情况下（标准盒模型），你设置的 `width` 只代表 content 的宽度：

```css
.box {
  width: 200px;
  padding: 20px;
  border: 5px solid black;
}
/* 实际占用宽度 = 200 + 20×2 + 5×2 = 250px */
```

这常常让人困惑——"我明明设了 width: 200px，为什么实际占 250px？"

**解决方案**：使用 `box-sizing: border-box;`：

```css
.box {
  box-sizing: border-box;
  width: 200px;
  padding: 20px;
  border: 5px solid black;
}
/* 实际占用宽度 = 200px（padding 和 border 被包含在 200px 内） */
```

**推荐在所有项目开头加上**：

```css
* {
  box-sizing: border-box;
}
```

这会让所有元素都使用 border-box 模式，避免无休止的"为什么宽高不对"的困惑。

> 🤔 **想多一点**：为什么浏览器不把 `border-box` 设为默认值？历史原因。CSS 诞生于 1996 年，那时的网页设计很简单，content-box 的逻辑更直观。但随着网页复杂度爆炸式增长，`border-box` 明显更符合直觉。好消息是：几乎所有现代 CSS 框架（Tailwind、Bootstrap 等）都会默认设置 `border-box`。

---

# 步骤 6：F12 → Styles 面板实时调试 CSS

这是你学习的**最强武器**——浏览器开发者工具可以让你实时修改 CSS，即时看到效果，而不用反复改文件、保存、刷新。

### 6.1 操作步骤

1. 在浏览器中打开 `index.html`，按 `F12`。
2. 点击 **Elements** 标签页。
3. 在 DOM 树中点击任意元素（比如 `<h1>`）。
4. 右侧会出现 **Styles** 面板，显示所有当前生效的 CSS 规则。

### 6.2 试试看

- **修改属性值**：点击 `color: darkblue;` 中的 `darkblue`，改成 `tomato`，回车——页面上的标题立刻变成番茄色。
- **添加新属性**：在任意规则末尾的 `}` 前面点击，输入 `font-size: 48px;`——标题立刻变大。
- **勾选/取消勾选**：每条属性前面有个复选框，取消勾选可以临时禁用该属性，观察效果。
- **查看盒模型**：在 Styles 面板下方（或 Computed 标签页），可以看到一个图形化的盒模型示意图，鼠标悬停时浏览器页面会高亮对应区域。

### 6.3 被划掉的样式

在 Styles 面板中，你可能会看到某些样式被划了一条横线：

```css
h1 {
  color: red;
  color: blue;   /* 这条生效，上面的被划掉 */
}
```

被划掉表示这条声明被其他更高优先级的规则**覆盖**了。这是 CSS 层叠机制的正常表现。

> ⚠️ 注意：在 Styles 面板中的修改是临时的，刷新页面就会消失。要永久保存，必须把修改同步回源文件。

---

# 步骤 7：常见错误排查

### ❌ 错误 1：class 选择器忘了加 `.`

```css
/* ❌ 错误：card 会被当成标签选择器，选中所有 <card> 标签（不存在） */
card {
  border: 1px solid #ccc;
}

/* ✅ 正确 */
.card {
  border: 1px solid #ccc;
}
```

**这是 CSS 新手最容易犯的错误。** 记住：class 前面必须加 `.`，id 前面必须加 `#`。

### ❌ 错误 2：margin 合并（塌陷）

```html
<div class="box1">上</div>
<div class="box2">下</div>
```

```css
.box1 { margin-bottom: 30px; }
.box2 { margin-top: 20px; }
/* 两个盒子之间的间距不是 50px，而是 30px！ */
```

**现象**：两个相邻元素的上下 margin 会"合并"成较大的那个，而不是相加。

**解决**：使用 `padding` 替代 margin，或者给父元素加 `overflow: hidden;`、`display: flex;` 等触发 BFC（Block Formatting Context）。

### ❌ 错误 3：宽高不生效

```css
span {
  width: 200px;   /* ❌ 行内元素默认忽略 width/height */
  height: 100px;
}
```

**原因**：`<span>`、`<a>` 等行内元素默认不能设置宽高。

**解决**：

```css
span {
  display: inline-block;  /* 行内块：同行显示，但可以设宽高 */
  width: 200px;
  height: 100px;
}
```

或者：

```css
span {
  display: block;  /* 转成块级元素 */
}
```

### ❌ 错误 4：CSS 文件路径写错

```html
<!-- ❌ 错误：路径不对，CSS 不生效 -->
<link rel="stylesheet" href="styles/style.css">

<!-- ✅ 正确：确认文件确实在 index.html 同级目录 -->
<link rel="stylesheet" href="style.css">
```

**排查方法**：F12 → Network 标签页 → 刷新页面 → 看 `style.css` 是否返回 200（成功）还是 404（找不到）。

---

## 📋 完整代码清单

**style.css**（最终版本）：

```css
/* 全局重置 */
* {
  box-sizing: border-box;
}

body {
  font-family: Arial, "Microsoft YaHei", sans-serif;
  background-color: #fafafa;
  margin: 0;
  padding: 0;
  color: #333;
}

/* 标题 */
.main-title {
  color: #2c3e50;
  text-align: center;
  font-size: 32px;
  margin-top: 40px;
}

/* 段落 */
#intro {
  text-align: center;
  color: #666;
  font-size: 16px;
}

/* 卡片 */
.card {
  width: 300px;
  margin: 20px auto;
  padding: 20px;
  border: 1px solid #ddd;
  border-radius: 8px;
  background-color: white;
}

.card h3 {
  margin-top: 0;
  color: #2c3e50;
}

.card p {
  line-height: 1.6;
}

.card a {
  color: #3498db;
  text-decoration: none;
}

.card a:hover {
  text-decoration: underline;
}

/* 导航 */
nav {
  background-color: #2c3e50;
  padding: 15px 30px;
  text-align: center;
}

nav a {
  color: white;
  text-decoration: none;
  margin: 0 15px;
  font-size: 16px;
}

nav a:hover {
  color: #3498db;
}

/* 页脚 */
footer {
  text-align: center;
  padding: 20px;
  color: #999;
  font-size: 14px;
  border-top: 1px solid #eee;
  margin-top: 40px;
}
```

---

## ✅ 最终验证

在浏览器中打开 `index.html`，确认：
- 页面背景变成了浅灰（`#fafafa`）
- 标题居中、深色
- 导航栏有深色背景，链接是白色
- 卡片有白色背景、圆角、阴影效果
- 按 F12 在 Styles 面板中能看到所有 CSS 规则，且都来自 `style.css`

---

## 🧠 术语附录

| 术语 | 解释 |
|------|------|
| **CSS** | 层叠样式表，控制 HTML 元素外观的语言。 |
| **选择器（Selector）** | CSS 规则中用来指定"给谁应用样式"的部分，如 `.card`、`#logo`、`p`。 |
| **盒模型（Box Model）** | CSS 布局的基石：每个元素由 content、padding、border、margin 四层组成。 |
| **margin** | 外边距，元素与相邻元素之间的距离。 |
| **padding** | 内边距，元素内容与边框之间的距离。 |
| **层叠（Cascading）** | 多条 CSS 规则叠加到同一元素时的优先级机制。 |
| **border-box** | 一种盒模型模式，`width` 包含 content + padding + border，更符合直觉。 |
| **行内元素** | 不换行、不能设宽高的元素，如 `<span>`、`<a>`。 |
| **块级元素** | 独占一行、可以设宽高的元素，如 `<div>`、`<p>`。 |

---

## 🚧 已知坑点与禁止事项

- **class 选择器必须加 `.`**：忘记加点是 CSS 新手最常见错误，没有之一。
- **margin 合并**：两个相邻元素的上下 margin 会合并，取较大值而不是相加。
- **行内元素不能设宽高**：想设宽高就加 `display: inline-block` 或 `display: block`。
- **CSS 文件路径**：确保 `<link href="...">` 的路径相对于 HTML 文件正确。
- **不要滥用 `!important`**：`!important` 会强制提升优先级，但它会让后续调试变得极其痛苦。优先通过提高选择器精度来解决问题。

---

## 📖 下一步建议

完成这篇后，继续学习 **[03-布局：Flexbox一把梭](03-布局：Flexbox一把梭/)**，用 Flexbox 三行代码搞定居中、对齐、换行等布局难题。