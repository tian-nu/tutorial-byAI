# 第21章：前端基础 — HTML/CSS/JS速览

## 本章目标

学完本章你将能够：

- 理解HTML5文档结构，掌握常用标签和表单元素
- 掌握CSS3盒模型和Flexbox布局，能写出常见的页面布局
- 掌握JavaScript ES6+核心语法：let/const、箭头函数、解构、Promise、async/await
- 使用Fetch API与后端RESTful API交互
- 避开前端开发中最常见的坑点

---

> **本章定位**：本章专门为后端开发者编写。你不需要成为前端专家，但你需要能看懂前端代码、写简单的页面来验证后端接口、理解前后端交互的原理。本章只讲**必要的核心知识**，跳过动画、Canvas、WebGL等与后端无关的内容。第22章将基于本章知识，用Vue 3框架构建完整的前端应用。

---

## 21.1 HTML5核心

### 21.1.1 文档基本结构

每个HTML页面都有固定的骨架结构：

```html
<!DOCTYPE html>                          <!-- 声明文档类型为HTML5 -->
<html lang="zh-CN">                      <!-- 根元素，lang属性指定语言 -->
<head>                                    <!-- 头部：元信息，不显示在页面上 -->
    <meta charset="UTF-8">               <!-- 字符编码，必须设UTF-8 -->
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                                          <!-- 视口设置，移动端适配 -->
    <title>EMS员工管理系统</title>         <!-- 浏览器标签页标题 -->
    <link rel="stylesheet" href="style.css">
                                          <!-- 引入外部CSS样式 -->
</head>
<body>                                    <!-- 身体：页面可见内容 -->
    <h1>员工管理系统</h1>                  <!-- 一级标题 -->
    <p>欢迎使用EMS</p>                    <!-- 段落 -->

    <script src="app.js"></script>        <!-- 引入外部JS脚本，放在body末尾 -->
</body>
</html>
```

关键点：
- `<!DOCTYPE html>`：告诉浏览器用HTML5标准解析，不写的话浏览器会进入"怪异模式"
- `<meta charset="UTF-8">`：必须放在`<head>`的第一个，否则中文可能乱码
- `<script>`放在`</body>`之前：确保DOM元素先加载完，JS才能操作它们

### 21.1.2 常用标签速查

| 标签 | 作用 | 示例 |
|------|------|------|
| `<div>` | 通用容器（块级） | `<div class="container">...</div>` |
| `<span>` | 通用容器（行内） | `<span class="highlight">重点</span>` |
| `<h1>`~`<h6>` | 标题（1最大6最小） | `<h2>部门列表</h2>` |
| `<p>` | 段落 | `<p>这是一段文字</p>` |
| `<a>` | 超链接 | `<a href="/employees">员工列表</a>` |
| `<img>` | 图片 | `<img src="logo.png" alt="Logo">` |
| `<ul>`/`<li>` | 无序列表 | `<ul><li>项目1</li></ul>` |
| `<table>` | 表格 | 见下方示例 |
| `<form>` | 表单 | 见21.1.3节 |

**语义化标签**（HTML5新增，推荐使用）：

```html
<header>   <!-- 页头：logo、导航 -->
<nav>      <!-- 导航区域 -->
<main>     <!-- 主要内容（每页只有一个） -->
<section>  <!-- 内容分区 -->
<article>  <!-- 独立文章 -->
<aside>    <!-- 侧边栏 -->
<footer>   <!-- 页脚：版权信息 -->
```

语义化标签和`<div>`的显示效果完全一样，但语义化标签能让搜索引擎和屏幕阅读器更好地理解页面结构。实际开发中，能用语义化标签的地方就不要用`<div>`。

### 21.1.3 表单标签详解

表单是前后端交互的核心——登录、注册、新增、编辑都离不开表单。

```html
<form id="employeeForm">
    <!-- 文本输入 -->
    <label for="name">姓名：</label>
    <input type="text" id="name" name="name" placeholder="请输入姓名" required>

    <!-- 密码输入（字符显示为●） -->
    <label for="password">密码：</label>
    <input type="password" id="password" name="password">

    <!-- 邮箱输入（自动校验邮箱格式） -->
    <label for="email">邮箱：</label>
    <input type="email" id="email" name="email" placeholder="example@mail.com">

    <!-- 数字输入（只能输入数字，有上下箭头） -->
    <label for="age">年龄：</label>
    <input type="number" id="age" name="age" min="18" max="65" value="25">

    <!-- 日期选择器（浏览器自带日历弹窗） -->
    <label for="hireDate">入职日期：</label>
    <input type="date" id="hireDate" name="hireDate">

    <!-- 单选按钮（name相同为一组，只能选一个） -->
    <label>性别：
        <input type="radio" name="gender" value="male"> 男
        <input type="radio" name="gender" value="female"> 女
    </label>

    <!-- 复选框（可多选） -->
    <label>
        <input type="checkbox" name="skills" value="java"> Java
        <input type="checkbox" name="skills" value="python"> Python
        <input type="checkbox" name="skills" value="go"> Go
    </label>

    <!-- 下拉选择 -->
    <label for="department">部门：</label>
    <select id="department" name="department">
        <option value="">请选择部门</option>
        <option value="技术部">技术部</option>
        <option value="产品部">产品部</option>
        <option value="市场部">市场部</option>
    </select>

    <!-- 多行文本 -->
    <label for="remark">备注：</label>
    <textarea id="remark" name="remark" rows="4" cols="50"></textarea>

    <!-- 提交按钮 -->
    <button type="submit">提交</button>
    <!-- 重置按钮 -->
    <button type="reset">重置</button>
</form>
```

> 🚨 **坑点：form的默认提交行为会刷新页面！**
>
> 点击`<button type="submit">`时，浏览器会执行默认行为：将表单数据以GET或POST方式提交到`action`属性指定的URL，**页面会整体刷新**。在前后端分离的项目中，我们不希望页面刷新——而是用JavaScript拦截提交，通过Ajax发送数据。
>
> ```javascript
> // 方式1：在事件处理函数中阻止默认行为
> document.getElementById('employeeForm').addEventListener('submit', function(event) {
>     event.preventDefault();  // ← 阻止默认提交行为！
>
>     // 用JavaScript收集表单数据，通过fetch/axios发送
>     const formData = new FormData(this);
>     const data = Object.fromEntries(formData);
>     console.log(data);  // { name: "张三", age: "25", ... }
> });
>
> // 方式2：在HTML中用onsubmit
> // <form onsubmit="return false;">
> ```
>
> 忘记`event.preventDefault()`是最常见的前端Bug之一——点击提交后页面闪了一下，数据没提交成功，控制台也没有错误日志。

---

## 21.2 CSS3关键知识

### 21.2.1 选择器速查

CSS选择器决定"样式应用到哪些元素"：

```css
/* 元素选择器：所有<p>标签 */
p { color: #333; }

/* 类选择器：class="highlight"的元素（最常用） */
.highlight { background-color: yellow; }

/* ID选择器：id="header"的元素（唯一） */
#header { font-size: 24px; }

/* 属性选择器：有type="email"的input */
input[type="email"] { border-color: blue; }

/* 后代选择器：nav下的所有a标签 */
nav a { text-decoration: none; }

/* 子代选择器：nav的直接子元素a（不包括更深层） */
nav > a { color: red; }

/* 伪类选择器：鼠标悬停状态 */
a:hover { color: orange; }

/* 伪类选择器：获取焦点的input */
input:focus { border-color: #409eff; }
```

> 🚨 **坑点：CSS层叠与优先级 → 行内 > ID > 类 > 元素 → !important是核武器慎用**
>
> 当多条规则同时作用于一个元素时，优先级从高到低：
>
> ```
> !important > 行内样式(style属性) > ID选择器 > 类/属性/伪类选择器 > 元素/伪元素选择器
> ```
>
> 计算规则：一个ID选择器的优先级高于任意数量的类选择器。例如：
>
> ```css
> #title { color: red; }        /* 优先级：0-1-0-0 */
> .header .title { color: blue; } /* 优先级：0-0-2-0 */
> /* 结果：红色！一个ID > 两个类 */
> ```
>
> `!important`会覆盖一切优先级规则，但它会让CSS变得极难维护——一旦用了`!important`，后续要覆盖它只能再用`!important`，形成"军备竞赛"。**只在覆盖第三方库样式时使用`!important`，自己的代码永远不要用。**

### 21.2.2 盒模型

CSS中每个元素都是一个"盒子"，由四层组成：

```
┌─────────────────────────────────────────┐
│                 margin                   │  ← 外边距：元素与外部的间距
│  ┌──────────────────────────────────┐   │
│  │              border              │   │  ← 边框
│  │  ┌───────────────────────────┐   │   │
│  │  │         padding           │   │   │  ← 内边距：内容与边框的间距
│  │  │  ┌───────────────────┐    │   │   │
│  │  │  │     content       │    │   │   │  ← 内容：文字、图片等
│  │  │  │                   │    │   │   │
│  │  │  └───────────────────┘    │   │   │
│  │  └───────────────────────────┘   │   │
│  └──────────────────────────────────┘   │
└─────────────────────────────────────────┘
```

> 🚨 **坑点：box-sizing默认content-box → 设width:200px+padding:20px → 实际240px**
>
> 默认的`box-sizing: content-box`中，`width`只设置内容区域的宽度。加上padding和border后，元素的实际占用宽度会超出你设的width：
>
> ```
> content-box（默认）：
>   设 width: 200px, padding: 20px, border: 1px
>   实际宽度 = 200 + 20*2 + 1*2 = 242px  ← 不是200！
>
> border-box（推荐）：
>   设 width: 200px, padding: 20px, border: 1px
>   实际宽度 = 200px  ← 就是200！padding和border向内挤压
> ```
>
> **解决方案**：全局设置border-box：
>
> ```css
> * {
>     margin: 0;
>     padding: 0;
>     box-sizing: border-box;  /* 全局设置，让width就是实际宽度 */
> }
> ```
>
> 这是几乎所有现代前端项目的标配重置样式。

### 21.2.3 Flexbox布局（重点）

Flexbox是目前最主流的CSS布局方案，能轻松实现居中、等分、导航栏等常见布局。

**核心概念**：Flex布局有两个角色——**容器**（父元素）和**项目**（子元素）。设置`display: flex`后，容器变成Flex容器，其直接子元素变成Flex项目。

```
┌─────────────── Flex容器 ───────────────┐
│                                         │
│  ┌─────┐  ┌─────┐  ┌─────┐  ┌─────┐   │
│  │ 项目1 │  │ 项目2 │  │ 项目3 │  │ 项目4 │   │
│  └─────┘  └─────┘  └─────┘  └─────┘   │
│                                         │
│  ←──────── 主轴(main axis) ────────→    │
│         ↑                               │
│      交叉轴(cross axis)                  │
│         ↓                               │
└─────────────────────────────────────────┘
```

**容器属性**：

```css
.container {
    display: flex;                    /* 启用Flex布局 */

    /* 主轴方向：项目排列方向 */
    flex-direction: row;              /* 默认：水平从左到右 */
    /* flex-direction: column;        垂直从上到下 */
    /* flex-direction: row-reverse;   水平从右到左 */
    /* flex-direction: column-reverse; 垂直从下到上 */

    /* 主轴对齐：项目在主轴上的分布方式 */
    justify-content: flex-start;      /* 默认：从起点开始 */
    /* justify-content: center;       居中 */
    /* justify-content: flex-end;     从终点开始 */
    /* justify-content: space-between; 两端对齐，项目间等距 */
    /* justify-content: space-around;  每个项目两侧等距 */

    /* 交叉轴对齐：项目在交叉轴上的对齐方式 */
    align-items: stretch;             /* 默认：拉伸填满 */
    /* align-items: center;           居中 */
    /* align-items: flex-start;       从起点开始 */
    /* align-items: flex-end;         从终点开始 */

    /* 是否换行：项目太多时是否换行 */
    flex-wrap: nowrap;                /* 默认：不换行，项目压缩 */
    /* flex-wrap: wrap;               换行 */
}
```

**justify-content效果图解**：

```
flex-start:     [■][■][■]________________________
center:         ______________[■][■][■]____________
flex-end:       ________________________[■][■][■]
space-between:  [■]__________[■]__________[■]
space-around:   ___[■]_______[■]_______[■]___
space-evenly:   ____[■]______[■]______[■]____
```

**项目属性**：

```css
.item {
    /* flex是flex-grow、flex-shrink、flex-basis的简写 */
    flex: 1;          /* 等分剩余空间（最常用） */
    /* flex: 0 0 200px;  固定200px宽度，不伸缩 */
    /* flex: 2;          占2份，其他flex:1的占1份 */

    /* 单独设置交叉轴对齐（覆盖容器的align-items） */
    align-self: center;
}
```

**典型布局1：水平垂直居中**

```css
.center-container {
    display: flex;
    justify-content: center;    /* 水平居中 */
    align-items: center;        /* 垂直居中 */
    height: 100vh;              /* 占满视口高度 */
}
```

```
┌─────────────────────────────────┐
│                                 │
│                                 │
│           ┌──────┐             │
│           │ 居中! │             │
│           └──────┘             │
│                                 │
│                                 │
└─────────────────────────────────┘
```

**典型布局2：导航栏**

```css
.navbar {
    display: flex;
    justify-content: space-between;  /* 左右两端对齐 */
    align-items: center;             /* 垂直居中 */
    padding: 0 20px;
    height: 60px;
    background-color: #409eff;
    color: white;
}

.navbar .logo { font-size: 20px; font-weight: bold; }
.navbar .nav-links { display: flex; gap: 20px; }
```

```html
<nav class="navbar">
    <div class="logo">EMS</div>
    <div class="nav-links">
        <a href="/employees">员工管理</a>
        <a href="/departments">部门管理</a>
        <a href="/profile">个人中心</a>
    </div>
</nav>
```

```
┌──────────────────────────────────────────────┐
│  EMS                    员工管理  部门管理  个人中心  │
└──────────────────────────────────────────────┘
```

**典型布局3：等分布局**

```css
.equal-layout {
    display: flex;
    gap: 20px;          /* 项目间距 */
}

.equal-layout .item {
    flex: 1;            /* 每个项目等分 */
    padding: 20px;
    border: 1px solid #ddd;
}
```

```
┌──────────┐  ┌──────────┐  ┌──────────┐
│   1/3    │  │   1/3    │  │   1/3    │
└──────────┘  └──────────┘  └──────────┘
```

---

## 21.3 JavaScript ES6+核心

### 21.3.1 let/const vs var

JavaScript有三个声明变量的关键字，它们的区别至关重要：

```javascript
// var — 函数作用域，有变量提升
console.log(a);  // undefined（不报错！但值是undefined）
var a = 10;

// let — 块级作用域，暂时性死区
// console.log(b);  // ReferenceError: Cannot access 'b' before initialization
let b = 20;

// const — 块级作用域，声明时必须赋值，之后不能重新赋值
const c = 30;
// c = 40;  // TypeError: Assignment to constant variable
```

> 🚨 **坑点：var有变量提升 → 声明前使用不报错但为undefined**
>
> `var`声明的变量会被"提升"到作用域顶部，但赋值不会提升：
>
> ```javascript
> console.log(name);  // undefined（不是ReferenceError！）
> var name = "张三";
> // 等价于：
> // var name;
> // console.log(name);  // undefined
> // name = "张三";
> ```
>
> 这会导致很难发现的Bug——你以为变量还没声明所以会报错，结果它静默地返回undefined。

> 🚨 **坑点：var没有块级作用域 → for循环中用var，闭包取值永远是最后一个**
>
> ```javascript
> // 用var — 经典的闭包陷阱
> for (var i = 0; i < 3; i++) {
>     setTimeout(function() {
>         console.log(i);  // 输出：3, 3, 3（不是0,1,2！）
>     }, 100);
> }
> // 原因：var i是函数作用域，循环结束后i=3，三个回调共享同一个i
>
> // 用let — 正确行为
> for (let i = 0; i < 3; i++) {
>     setTimeout(function() {
>         console.log(i);  // 输出：0, 1, 2
>     }, 100);
> }
> // 原因：let i是块级作用域，每次循环创建一个新的i
> ```

**结论：永远使用`let`和`const`，不要使用`var`。** 不会改变的值用`const`，需要重新赋值的用`let`。

### 21.3.2 箭头函数

箭头函数是ES6引入的更简洁的函数写法：

```javascript
// 普通函数
function add(a, b) {
    return a + b;
}

// 箭头函数
const add = (a, b) => a + b;

// 多行函数体需要大括号和return
const add = (a, b) => {
    const sum = a + b;
    return sum;
};

// 单参数可省略括号
const double = n => n * 2;

// 无参数需要空括号
const sayHi = () => console.log("Hi!");
```

**箭头函数 vs 普通函数对比**：

| 特性 | 普通函数 | 箭头函数 |
|------|---------|---------|
| `this`指向 | 谁调用指向谁 | **继承外层的`this`** |
| `arguments`对象 | 有 | 没有 |
| 作为构造函数 | 可以（`new`） | 不可以 |
| 作为对象方法 | 可以 | **不推荐** |

> 🚨 **坑点：箭头函数没有自己的this → 不适合对象方法/Vue methods**
>
> ```javascript
> const user = {
>     name: "张三",
>     // 普通函数：this指向调用者（user对象）
>     sayHi() {
>         console.log(`Hi, I'm ${this.name}`);  // "Hi, I'm 张三"
>     },
>     // 箭头函数：this继承外层（全局对象/undefined）
>     sayHello: () => {
>         console.log(`Hello, I'm ${this.name}`);  // "Hello, I'm undefined"
>     }
> };
> ```
>
> 箭头函数的`this`在定义时就确定了（词法作用域），无法通过`call`/`apply`/`bind`改变。这在Vue 2的Options API中是坑（methods中用箭头函数`this`不指向Vue实例），但在Vue 3的`<script setup>`中不是问题——因为`<script setup>`中不需要`this`。

### 21.3.3 模板字符串

```javascript
const name = "张三";
const age = 25;

// 传统字符串拼接
const msg1 = "姓名：" + name + "，年龄：" + age;

// 模板字符串（反引号`` + ${}插值）
const msg2 = `姓名：${name}，年龄：${age}`;

// 模板字符串支持多行
const html = `
    <div class="card">
        <h2>${name}</h2>
        <p>年龄：${age}</p>
    </div>
`;

// 模板字符串支持表达式
const msg3 = `${name}今年${age}岁，${age >= 18 ? '已成年' : '未成年'}`;
```

### 21.3.4 解构赋值

```javascript
// 对象解构
const employee = { name: "张三", age: 25, department: "技术部" };
const { name, age, department } = employee;
console.log(name);       // "张三"
console.log(department); // "技术部"

// 重命名解构
const { name: empName, age: empAge } = employee;
console.log(empName);    // "张三"

// 默认值
const { salary = 15000 } = employee;
console.log(salary);     // 15000（对象中没有salary属性，使用默认值）

// 数组解构
const colors = ["red", "green", "blue"];
const [first, second, third] = colors;
console.log(first);  // "red"

// 跳过元素
const [, , third] = colors;
console.log(third);  // "blue"

// 函数参数解构（非常实用！）
function printEmployee({ name, age, department }) {
    console.log(`${name}, ${age}岁, ${department}`);
}
printEmployee(employee);  // "张三, 25岁, 技术部"
```

### 21.3.5 展开运算符

```javascript
// 数组展开
const arr1 = [1, 2, 3];
const arr2 = [4, 5, 6];
const merged = [...arr1, ...arr2];  // [1, 2, 3, 4, 5, 6]

// 对象展开（后者的属性覆盖前者）
const defaults = { theme: "light", fontSize: 14, language: "zh" };
const userConfig = { fontSize: 16, language: "en" };
const finalConfig = { ...defaults, ...userConfig };
// { theme: "light", fontSize: 16, language: "en" }

// 数组复制（浅拷贝）
const original = [1, 2, 3];
const copy = [...original];  // [1, 2, 3]
copy.push(4);
console.log(original);  // [1, 2, 3]（不影响原数组）

// 函数参数展开
const nums = [3, 1, 4, 1, 5];
Math.max(...nums);  // 5（等价于Math.max(3,1,4,1,5)）
```

### 21.3.6 Promise（重点）

JavaScript是单线程语言，网络请求、文件读取等耗时操作不能阻塞主线程。Promise就是处理异步操作的标准方式。

**三种状态**：

```
                    resolve(value)
  pending ──────────────────────→ fulfilled（已成功）
     │
     │    reject(reason)
     └──────────────────────────→ rejected（已失败）
```

Promise的状态一旦改变就不可逆：pending→fulfilled或pending→rejected，之后不会再变。

```javascript
// 创建Promise
const fetchData = new Promise((resolve, reject) => {
    // 模拟异步操作
    setTimeout(() => {
        const success = true;
        if (success) {
            resolve({ id: 1, name: "张三" });  // 成功
        } else {
            reject(new Error("网络请求失败"));    // 失败
        }
    }, 1000);
});

// 消费Promise — .then().catch().finally() 链式调用
fetchData
    .then(data => {
        console.log("成功：", data);       // { id: 1, name: "张三" }
        return data.name;                   // 返回值传递给下一个.then
    })
    .then(name => {
        console.log("姓名：", name);        // "张三"
    })
    .catch(error => {
        console.error("失败：", error);     // 捕获任何环节的错误
    })
    .finally(() => {
        console.log("无论成功失败都执行");   // 清理工作
    });
```

> 🚨 **坑点：.then中没有return → 后续.then取到undefined**
>
> ```javascript
> fetchData
>     .then(data => {
>         console.log(data);  // 打印了data
>         // 忘记return！
>     })
>     .then(result => {
>         console.log(result);  // undefined！不是data
>     });
> ```
>
> `.then`的回调函数如果返回一个值，这个值会传递给下一个`.then`。如果没有`return`，下一个`.then`收到的是`undefined`。这是Promise链式调用中最常见的Bug。

**Promise.all / Promise.race**：

```javascript
// Promise.all：所有都成功才成功，一个失败就失败
const p1 = fetch('/api/employees');
const p2 = fetch('/api/departments');
const p3 = fetch('/api/stats');

Promise.all([p1, p2, p3])
    .then(([employees, departments, stats]) => {
        // 三个请求都完成了
        console.log(employees, departments, stats);
    })
    .catch(error => {
        // 只要有一个失败就进入这里
        console.error("某个请求失败：", error);
    });

// Promise.race：谁先完成就用谁的结果
Promise.race([
    fetch('/api/data'),
    new Promise((_, reject) =>
        setTimeout(() => reject(new Error('超时')), 5000)
    )
]).then(data => {
    console.log("5秒内完成：", data);
}).catch(error => {
    console.error("超时或失败：", error);
});
```

### 21.3.7 async/await

`async/await`是Promise的语法糖，让异步代码看起来像同步代码：

```javascript
// Promise写法
function getEmployee(id) {
    return fetch(`/api/employees/${id}`)
        .then(res => res.json())
        .then(data => {
            console.log(data);
            return data;
        })
        .catch(error => console.error(error));
}

// async/await写法（推荐）
async function getEmployee(id) {
    try {
        const res = await fetch(`/api/employees/${id}`);
        const data = await res.json();
        console.log(data);
        return data;
    } catch (error) {
        console.error(error);
    }
}
```

`async`函数总是返回一个Promise。`await`只能在`async`函数内部使用，它会"暂停"函数执行，直到Promise解决。

> 🚨 **坑点：async函数忘记await → 拿到Promise对象而非值**
>
> ```javascript
> async function main() {
>     // 忘记await！
>     const data = getEmployee(1);  // data是Promise对象，不是实际数据
>     console.log(data);  // Promise { <pending> }  ← 不是你期望的数据！
>
>     // 正确写法
>     const data = await getEmployee(1);  // await等待Promise完成
>     console.log(data);  // { id: 1, name: "张三" }
> }
> ```

> 🚨 **坑点：await必须try-catch包裹或有.catch兜底**
>
> ```javascript
> async function main() {
>     // 危险！如果fetch失败，抛出的异常会变成未捕获的Promise rejection
>     const res = await fetch('/api/employees/999');
>     const data = await res.json();
>     console.log(data);
>
>     // 正确写法1：try-catch
>     try {
>         const res = await fetch('/api/employees/999');
>         const data = await res.json();
>         console.log(data);
>     } catch (error) {
>         console.error("请求失败：", error);
>     }
>
>     // 正确写法2：给Promise加.catch（不推荐，不如try-catch清晰）
>     const res = await fetch('/api/employees/999').catch(err => {
>         console.error("请求失败：", err);
>         return null;
>     });
>     if (res) {
>         const data = await res.json();
>     }
> }
> ```

> 🚨 **坑点：forEach中不能用await → 用for...of**
>
> ```javascript
> // 错误：forEach不会等待await完成
> async function processAll() {
>     const ids = [1, 2, 3];
>     ids.forEach(async (id) => {
>         const data = await fetch(`/api/employees/${id}`);
>         console.log(data);  // 顺序不确定！可能3先打印
>     });
>     console.log("完成");  // 这行会先于上面的await执行！
> }
>
> // 正确：for...of会依次等待每个await
> async function processAll() {
>     const ids = [1, 2, 3];
>     for (const id of ids) {
>         const data = await fetch(`/api/employees/${id}`);
>         console.log(data);  // 保证1→2→3的顺序
>     }
>     console.log("完成");  // 所有await完成后才执行
> }
>
> // 如果不需要顺序，用Promise.all并行（更快）
> async function processAll() {
>     const ids = [1, 2, 3];
>     const promises = ids.map(id => fetch(`/api/employees/${id}`));
>     const results = await Promise.all(promises);
>     console.log("完成");
> }
> ```

### 21.3.8 模块化

ES6模块化让JavaScript代码可以拆分为多个文件，每个文件是一个模块：

```javascript
// math.js — 导出
export const PI = 3.14159;

export function add(a, b) {
    return a + b;
}

// 默认导出（一个模块只能有一个）
export default class Calculator {
    multiply(a, b) { return a * b; }
}
```

```javascript
// app.js — 导入
import Calculator, { PI, add } from './math.js';
//    ↑ 默认导出      ↑ 命名导出

console.log(PI);           // 3.14159
console.log(add(1, 2));    // 3
const calc = new Calculator();
console.log(calc.multiply(3, 4));  // 12
```

**命名导出 vs 默认导出**：

| 特性 | 命名导出 | 默认导出 |
|------|---------|---------|
| 一个模块中数量 | 可以有多个 | 只能有一个 |
| 导入时名称 | 必须与导出名一致 | 可以任意命名 |
| 使用场景 | 工具函数、常量 | 组件、类、主功能 |

---

## 21.4 Fetch API

### 21.4.1 fetch()基本用法

`fetch`是浏览器内置的HTTP请求API，替代了老旧的XMLHttpRequest：

```javascript
// GET请求
fetch('http://localhost:8080/api/v1/employees?page=0&size=10')
    .then(response => response.json())  // 解析JSON响应
    .then(result => {
        console.log(result);  // { code: 200, message: "操作成功", data: {...} }
    })
    .catch(error => {
        console.error('请求失败：', error);
    });

// POST请求
fetch('http://localhost:8080/api/v1/employees', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        name: '赵六',
        age: 28,
        department: '产品部',
        salary: 16000,
        email: 'zhaoliu@example.com'
    })
})
    .then(response => response.json())
    .then(result => {
        if (result.code === 200) {
            console.log('创建成功：', result.data);
        } else {
            console.log('创建失败：', result.message);
        }
    });

// async/await写法（推荐）
async function createEmployee(employeeData) {
    try {
        const response = await fetch('http://localhost:8080/api/v1/employees', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(employeeData)
        });

        const result = await response.json();

        if (result.code === 200) {
            return result.data;
        } else {
            throw new Error(result.message);
        }
    } catch (error) {
        console.error('创建员工失败：', error);
        throw error;
    }
}
```

### 21.4.2 fetch请求配置

```javascript
const response = await fetch(url, {
    method: 'GET',                    // 请求方法：GET/POST/PUT/PATCH/DELETE
    headers: {                        // 请求头
        'Content-Type': 'application/json',
        'Authorization': 'Bearer eyJhbGciOiJIUzI1NiJ9...'  // Token认证
    },
    body: JSON.stringify(data),       // 请求体（GET/HEAD不能有body）
    credentials: 'include',           // 跨域请求携带cookie
    // credentials: 'same-origin'     // 同源请求携带cookie（默认）
    // credentials: 'omit'            // 不携带cookie
});
```

> 🚨 **坑点：fetch不自动处理非2xx状态 → response.ok需手动判断**
>
> `fetch`只在**网络故障**或**请求被阻止**时才reject。HTTP 404、500等错误状态码**不会**触发`.catch`——`fetch`认为这些是"成功的HTTP请求"（只是服务器返回了错误）。
>
> ```javascript
> // 错误写法：以为404会进入catch
> fetch('/api/employees/999')
>     .then(res => res.json())
>     .then(data => console.log(data))    // 404也会走到这里！
>     .catch(err => console.log(err));    // 404不会走到这里！
>
> // 正确写法：手动检查response.ok
> fetch('/api/employees/999')
>     .then(res => {
>         if (!res.ok) {                  // res.ok在2xx时为true
>             throw new Error(`HTTP ${res.status}: ${res.statusText}`);
>         }
>         return res.json();
>     })
>     .then(data => console.log(data))
>     .catch(err => console.error(err));  // "HTTP 404: Not Found"
> ```
>
> 这和Axios（第22章将学习）不同——Axios会自动对非2xx状态码reject。

> 🚨 **坑点：fetch默认不携带cookie → credentials:'include'**
>
> 前后端分离项目中，后端可能用Cookie/Session维持登录状态。但`fetch`默认**不会**在跨域请求中携带Cookie。你需要显式设置：
>
> ```javascript
> fetch('http://localhost:8080/api/v1/profile', {
>     credentials: 'include'  // 跨域请求也携带Cookie
> });
> ```
>
> 同时后端也需要配置CORS允许携带凭证（第16章已讲）：
>
> ```java
> @Bean
> public CorsFilter corsFilter() {
>     CorsConfiguration config = new CorsConfiguration();
>     config.setAllowCredentials(true);  // 允许携带Cookie
>     config.addAllowedOriginPattern("*");  // 不能用addAllowedOrigin("*")
>     // ...
> }
> ```

### 21.4.3 与后端Result格式配合

第16章设计的`Result<T>`统一返回格式，前端需要这样解析：

```javascript
async function apiRequest(url, options = {}) {
    const response = await fetch(url, {
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        ...options
    });

    if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
    }

    const result = await response.json();

    // 解析后端统一返回格式 Result<T>
    if (result.code === 200) {
        return result.data;     // 成功时返回data
    } else {
        throw new Error(result.message);  // 业务错误
    }
}

// 使用
async function loadEmployees() {
    try {
        const pageResult = await apiRequest('/api/v1/employees?page=0&size=10');
        console.log('员工列表：', pageResult.content);
        console.log('总条数：', pageResult.totalElements);
    } catch (error) {
        console.error('加载失败：', error.message);
    }
}
```

这个`apiRequest`函数就是Axios拦截器的雏形——第22章会用Axios拦截器实现更完善的版本。

---

## 21.5 本章小结

本章从后端开发者的视角，快速速览了前端三大核心技术：

1. **HTML5**：文档结构、常用标签、表单元素。记住`event.preventDefault()`阻止表单默认提交行为
2. **CSS3**：选择器优先级（行内>ID>类>元素）、盒模型（全局设置`box-sizing: border-box`）、Flexbox布局（容器属性+项目属性，轻松实现居中/导航栏/等分布局）
3. **JavaScript ES6+**：
   - `let`/`const`替代`var`（块级作用域，无变量提升）
   - 箭头函数（没有自己的`this`，不适合对象方法）
   - 模板字符串、解构赋值、展开运算符
   - Promise（三种状态、链式调用、`Promise.all`）
   - `async`/`await`（同步写法写异步，必须`try-catch`，`forEach`中不能用`await`）
4. **Fetch API**：`fetch()`基本用法，注意两个坑——不自动处理非2xx状态码（检查`response.ok`）、默认不携带Cookie（设置`credentials: 'include'`）

这些知识足以让你看懂第22章的Vue 3代码。Vue框架本质上就是用JavaScript操作HTML和CSS，只是提供了更高效的方式。

---

## 思考题

1. 以下CSS代码中，`<p>`标签的文字最终显示什么颜色？为什么？
   ```html
   <style>
       p { color: black; }
       .text { color: blue; }
       #intro { color: red; }
   </style>
   <p id="intro" class="text">Hello</p>
   ```

2. 以下JavaScript代码的输出是什么？请解释原因。
   ```javascript
   for (var i = 0; i < 3; i++) {
       setTimeout(() => console.log(i), 0);
   }
   console.log("end");
   ```

3. 以下`async`函数有什么问题？如何修复？
   ```javascript
   async function loadAllEmployees() {
       const ids = [1, 2, 3, 4, 5];
       ids.forEach(async (id) => {
           const res = await fetch(`/api/employees/${id}`);
           const data = await res.json();
           console.log(data.name);
       });
       console.log("全部加载完成");
   }
   ```

4. 使用Fetch API发送POST请求创建员工，但后端返回401 Unauthorized。你的请求代码如下，可能是什么原因？如何修复？
   ```javascript
   fetch('http://localhost:8080/api/v1/employees', {
       method: 'POST',
       headers: { 'Content-Type': 'application/json' },
       body: JSON.stringify({ name: '张三', age: 25 })
   });
   ```

5. 请用Flexbox实现以下布局：左侧固定宽度200px的侧边栏，右侧自适应宽度的主内容区。

---

<details>
<summary>思考题参考答案（点击展开）</summary>

**第1题**：

红色。优先级：`#intro`（ID选择器，0-1-0-0）> `.text`（类选择器，0-0-1-0）> `p`（元素选择器，0-0-0-1）。ID选择器优先级最高，所以显示红色。

**第2题**：

输出顺序：`end`，然后`3, 3, 3`。

原因：
1. `var i`是函数作用域，循环结束后`i=3`
2. `setTimeout`是异步的，回调会被放入任务队列，等主线程执行完再执行
3. 主线程先执行`console.log("end")`，然后执行三个`setTimeout`回调
4. 三个回调共享同一个`i`，此时`i=3`，所以都输出3

如果改成`let i`，输出是`end`，然后`0, 1, 2`。

**第3题**：

问题1：`forEach`不会等待`async`回调完成，所以"全部加载完成"会先于所有数据加载打印。

问题2：如果某个请求失败，异常不会被外层捕获，会变成未处理的Promise rejection。

修复方案：

```javascript
async function loadAllEmployees() {
    const ids = [1, 2, 3, 4, 5];

    // 方案1：串行加载（按顺序）
    for (const id of ids) {
        try {
            const res = await fetch(`/api/employees/${id}`);
            const data = await res.json();
            console.log(data.name);
        } catch (error) {
            console.error(`加载员工${id}失败：`, error);
        }
    }
    console.log("全部加载完成");

    // 方案2：并行加载（更快，推荐）
    try {
        const promises = ids.map(id =>
            fetch(`/api/employees/${id}`).then(res => res.json())
        );
        const results = await Promise.all(promises);
        results.forEach(data => console.log(data.name));
        console.log("全部加载完成");
    } catch (error) {
        console.error("加载失败：", error);
    }
}
```

**第4题**：

401 Unauthorized表示未认证。可能的原因：

1. **没有携带认证Token**：如果后端需要JWT Token，请求头中需要添加`Authorization`：
   ```javascript
   fetch('http://localhost:8080/api/v1/employees', {
       method: 'POST',
       headers: {
           'Content-Type': 'application/json',
           'Authorization': 'Bearer ' + localStorage.getItem('token')  // 添加Token
       },
       body: JSON.stringify({ name: '张三', age: 25 })
   });
   ```

2. **Token已过期**：需要重新登录获取新Token

3. **Cookie未携带**：如果后端使用Session认证，需要添加`credentials: 'include'`

**第5题**：

```html
<div class="layout">
    <aside class="sidebar">侧边栏</aside>
    <main class="content">主内容区</main>
</div>
```

```css
.layout {
    display: flex;
    height: 100vh;
}

.sidebar {
    width: 200px;         /* 固定宽度 */
    flex-shrink: 0;       /* 不允许收缩 */
    background-color: #f5f5f5;
}

.content {
    flex: 1;              /* 占据剩余空间 */
    padding: 20px;
}
```

</details>

---

> **下一篇预告**：本章我们掌握了前端三大基础技术。但用原生HTML/CSS/JS写复杂页面效率极低——你需要手动操作DOM、手动管理状态、手动处理更新。第22章将引入Vue 3框架，用Composition API和`<script setup>`语法，配合Element Plus组件库和Axios HTTP客户端，构建完整的EMS前端应用。最终交付EMS v6——Vue前端 + Spring Boot后端的全栈版！
