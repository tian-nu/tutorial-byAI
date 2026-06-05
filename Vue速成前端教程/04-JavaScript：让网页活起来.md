# JavaScript：让网页活起来

- 对应文档版本：N/A（入门教程）
- 适用环境：任意现代浏览器，VS Code
- 读者角色：掌握 HTML + CSS 基础的前端新手
- 预计耗时：新手 2 小时 / 熟手 30 分钟
- 前置教程：[01-HTML：网页的骨架](01-HTML：网页的骨架.md)、[02-CSS：让网页变好看](02-CSS：让网页变好看.md)
- 可视化：无

---

## 🎯 学完能做什么

- 用 JavaScript 动态修改页面内容，不需要刷新页面
- 给按钮绑定点击事件，响应用户操作
- 用 `let` / `const` 声明变量，用对象和数组组织数据
- 用 `fetch` 发送网络请求获取数据
- 做一个点击计数的计数器

---

## 🧩 前置条件

| 前置项 | 说明 |
|--------|------|
| HTML | 能写出带 class / id 的标签结构 |
| CSS | 理解 class 选择器、盒模型 |
| 文件 | 准备好 `index.html` 和 `style.css` 的练习环境 |

---

## 📖 分步操作

# 步骤 1：JavaScript = 肌肉——HTML 是骨架，CSS 是衣服，JS 是肌肉

回忆一下前面两节教程的比喻：

| 技术 | 比喻 | 能做什么 |
|------|------|---------|
| HTML | 骨架 | 定义结构："这里有一个按钮" |
| CSS | 衣服 | 定义外观："按钮是蓝色的、圆角的" |
| **JavaScript** | **肌肉** | **定义行为："点击按钮后弹出一个提示"** |

HTML 和 CSS 是**静态的**——页面加载后就不再变化。JavaScript 是**动态的**——它可以在用户点击、输入、滚动时做出响应，可以修改页面内容、发送网络请求、存储数据。

**JavaScript 是一门真正的编程语言**。它有变量、条件判断、循环、函数——所有编程语言该有的东西。

> 🤔 **想多一点**：JavaScript 和 Java 没有任何关系。1995 年 Netscape 公司为了蹭 Java 的热度，把自家开发的 LiveScript 改名为 JavaScript——就像一家小面馆改名叫"意大利面馆"来吸引顾客。这个名字给无数初学者带来了困惑，但历史就是这样。

---

# 步骤 2：`<script>` 标签放哪——body 底部

JavaScript 代码写在 `<script>` 标签里。和 CSS 一样，JS 有三种引入方式：

### 2.1 内部脚本（练习时最常用）

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <title>JS 练习</title>
</head>
<body>
  <h1>Hello</h1>

  <!-- script 放在 body 的底部 -->
  <script>
    console.log('你好，JavaScript！');
  </script>
</body>
</html>
```

### 2.2 外部脚本（生产环境推荐）

```html
<body>
  <h1>Hello</h1>
  <script src="app.js"></script>
</body>
```

### 2.3 为什么放在 body 底部？

浏览器是从上到下读 HTML 的。如果把 `<script>` 放在 `<head>` 里，脚本执行时 `<body>` 里的元素还没加载出来，JS 就无法操作它们。

```html
<!-- ❌ 错误：放在 head 里 -->
<head>
  <script>
    // 此时 h1 还不存在！会报错
    document.querySelector('h1').textContent = 'Hello';
  </script>
</head>
<body>
  <h1>旧标题</h1>
</body>

<!-- ✅ 正确：放在 body 底部 -->
<body>
  <h1>旧标题</h1>
  <script>
    // 此时 h1 已经加载完毕，可以安全操作
    document.querySelector('h1').textContent = '新标题';
  </script>
</body>
```

### 2.4 验证环境

在 `index.html` 的 `<body>` 底部写入：

```html
<script>
  console.log('JS 加载成功！');
  alert('Hello，JavaScript！');
</script>
```

1. 保存文件，刷新浏览器。
2. 应该会弹出一个对话框"Hello，JavaScript！"。
3. 按 `F12` → **Console**（控制台）标签页，应该能看到 `JS 加载成功！`。

---

# 步骤 3：DOM 操作——用 JS 修改页面内容

**DOM**（文档对象模型）是浏览器把 HTML 解析后生成的树状结构。JavaScript 可以通过 DOM API 来查找、修改、添加、删除页面上的任何元素。

### 3.1 查找元素

```javascript
// 通过 CSS 选择器查找（推荐！最灵活）
const title = document.querySelector('h1');           // 找到第一个 h1
const card = document.querySelector('.card');         // 找到第一个 class="card" 的元素
const allCards = document.querySelectorAll('.card');  // 找到所有 class="card" 的元素（返回列表）

// 通过 id 查找（旧方法，但很常用）
const intro = document.getElementById('intro');       // 找到 id="intro" 的元素

// 通过 class 查找（旧方法）
const cards = document.getElementsByClassName('card'); // 找到所有 class="card" 的元素
```

**推荐优先使用 `querySelector` 和 `querySelectorAll`**——它们支持完整的 CSS 选择器语法，和你在 CSS 中使用的选择器一致。

### 3.2 修改内容

```javascript
// 修改文字内容
const title = document.querySelector('h1');
title.textContent = '新的标题文字';          // 纯文本（安全）
title.innerHTML = '<span>带 HTML 的标题</span>';  // 可以包含 HTML 标签

// 修改属性
const link = document.querySelector('a');
link.href = 'https://www.example.com';       // 修改链接地址
link.setAttribute('target', '_blank');        // 在新标签页打开

// 修改样式
const box = document.querySelector('.card');
box.style.backgroundColor = 'yellow';         // 修改背景色
box.style.fontSize = '20px';                  // 修改字号
// 注意：CSS 中的 background-color 在 JS 中写成 backgroundColor（驼峰命名）

// 添加/移除 class
box.classList.add('highlight');               // 添加 class
box.classList.remove('highlight');             // 移除 class
box.classList.toggle('active');                // 切换：有则移除，无则添加
```

> ⚠️ `innerHTML` vs `textContent`：`innerHTML` 可以插入 HTML 标签，但如果内容来自用户输入，可能被注入恶意脚本（XSS 攻击）。处理用户输入时，**始终用 `textContent`**。

### 3.3 创建和删除元素

```javascript
// 创建新元素
const newCard = document.createElement('div');
newCard.className = 'card';
newCard.textContent = '我是新创建的卡片';

// 添加到页面中
const container = document.querySelector('.card-list');
container.appendChild(newCard);

// 删除元素
const oldCard = document.querySelector('.card');
oldCard.remove();  // 删除自己
```

### 3.4 动手练习

在 HTML 中准备：

```html
<h1 id="title">原始标题</h1>
<p class="description">原始描述文字。</p>
<button id="change-btn">点我修改</button>
```

在 JS 中写：

```javascript
const btn = document.querySelector('#change-btn');
btn.addEventListener('click', function() {
  const title = document.querySelector('#title');
  title.textContent = '标题已被修改！';
  title.style.color = 'red';
});
```

### 我做得对不对？

- 点击按钮后，标题文字变了，颜色变成红色。
- F12 的 Console 中没有红色报错信息。

---

# 步骤 4：事件——让页面响应用户操作

**事件** = 用户在页面上做的事情：点击、输入、移动鼠标、按下键盘、滚动……

### 4.1 `addEventListener` — 绑定事件

```javascript
// 语法：元素.addEventListener('事件名', 回调函数);

const btn = document.querySelector('#my-btn');

btn.addEventListener('click', function() {
  console.log('按钮被点击了！');
});
```

### 4.2 常用事件一览

| 事件名 | 触发时机 | 适用于 |
|--------|---------|--------|
| `click` | 鼠标点击 | 按钮、链接、任何元素 |
| `input` | 输入框内容变化 | `<input>`、`<textarea>` |
| `submit` | 表单提交 | `<form>` |
| `keydown` | 键盘按下 | 全局快捷键 |
| `mouseenter` | 鼠标进入元素 | 悬停效果（用 CSS `:hover` 更简单） |
| `mouseleave` | 鼠标离开元素 | 悬停效果 |
| `DOMContentLoaded` | HTML 加载完毕 | 初始化脚本 |

### 4.3 事件对象 `event`

事件回调函数会收到一个 `event` 参数，包含事件的详细信息：

```javascript
btn.addEventListener('click', function(event) {
  console.log('点击的坐标：', event.clientX, event.clientY);
  console.log('被点击的元素：', event.target);
});
```

### 4.4 练习：输入框实时显示

```html
<input type="text" id="name-input" placeholder="输入你的名字">
<p>你好，<span id="display-name">______</span>！</p>
```

```javascript
const input = document.querySelector('#name-input');
const display = document.querySelector('#display-name');

input.addEventListener('input', function() {
  display.textContent = input.value || '______';  // 如果为空则显示占位符
});
```

> 🤔 **想多一点**：`addEventListener` 可以给同一个元素绑定多个事件处理函数，所有函数都会执行——不会互相覆盖。这是它比旧方法 `onclick` 更优越的地方。`onclick` 只能绑定一个函数，后来的会覆盖先前的。

---

# 步骤 5：变量、对象、数组——JS 的数据容器

### 5.1 `let` 和 `const`

```javascript
// let：可以重新赋值（可变变量）
let count = 0;
count = 1;       // ✅ 可以
count = count + 1; // ✅ 可以

// const：不能重新赋值（常量）
const name = '小明';
name = '小红';     // ❌ 报错！Assignment to constant variable

// 但 const 对象的属性可以修改
const user = { name: '小明', age: 20 };
user.age = 21;     // ✅ 可以！修改属性不是重新赋值
user = { name: '小红' };  // ❌ 报错！这才是重新赋值
```

**规则**：能用 `const` 就用 `const`，只有确定需要重新赋值时才用 `let`。**永远不要用 `var`**（它是旧时代的遗产，有各种奇怪的坑）。

### 5.2 基本类型

```javascript
const name = '小明';          // 字符串
const age = 25;              // 数字
const isStudent = true;      // 布尔值
const nothing = null;        // 空值（有意为之）
const notDefined = undefined; // 未定义（通常浏览器自己返回的）
```

### 5.3 对象（Object）

对象 = 一组相关数据的集合，用 `{}` 包裹：

```javascript
const article = {
  title: 'Flexbox 入门',
  author: '小张',
  likes: 128,
  tags: ['CSS', '布局'],
  published: true
};

// 访问属性
console.log(article.title);       // 'Flexbox 入门'（点号访问）
console.log(article['author']);   // '小张'（方括号访问，用于动态属性名）

// 修改属性
article.likes = 129;

// 添加新属性
article.createdAt = '2026-01-01';
```

### 5.4 数组（Array）

数组 = 一组有序数据的集合，用 `[]` 包裹：

```javascript
const fruits = ['苹果', '香蕉', '橘子'];

// 访问
console.log(fruits[0]);        // '苹果'（索引从 0 开始）
console.log(fruits.length);    // 3

// 添加
fruits.push('葡萄');            // 末尾添加 → ['苹果', '香蕉', '橘子', '葡萄']

// 删除
fruits.pop();                   // 末尾删除 → 返回 '葡萄'

// 遍历
fruits.forEach(function(fruit) {
  console.log(fruit);
});
// 输出：苹果、香蕉、橘子

// 映射（生成新数组）
const upperFruits = fruits.map(function(fruit) {
  return fruit.toUpperCase();
});
// upperFruits = ['苹果', '香蕉', '橘子']（中文不变，仅示例）
```

### 5.5 对象数组——最常用的数据结构

```javascript
const articles = [
  { title: 'Flexbox 入门', author: '小张', likes: 128 },
  { title: 'CSS 盒模型', author: '小李', likes: 56 },
  { title: 'JS 事件循环', author: '小王', likes: 203 }
];

// 遍历
articles.forEach(function(article) {
  console.log(article.title + ' - ' + article.author);
});
```

---

# 步骤 6：函数——把代码打包成工具箱

函数 = 把一段代码封装起来，取个名字，需要时调用。

### 6.1 普通函数

```javascript
// 定义函数
function greet(name) {
  return '你好，' + name + '！';
}

// 调用函数
const message = greet('小明');
console.log(message);  // '你好，小明！'
```

### 6.2 箭头函数（推荐）

```javascript
// 普通函数写法
const add = function(a, b) {
  return a + b;
};

// 箭头函数写法（更简洁）
const add = (a, b) => {
  return a + b;
};

// 如果只有一行 return，可以更简洁
const add = (a, b) => a + b;

// 如果只有一个参数，括号也可以省略
const double = x => x * 2;
```

**箭头函数是日常开发的首选写法**——它更简洁，而且 `this` 的行为更符合直觉（在 Vue 项目中尤其重要）。

### 6.3 函数作为参数

JavaScript 可以把函数作为参数传给另一个函数——这是 JS 最强大的特性之一：

```javascript
const numbers = [1, 2, 3, 4, 5];

// filter：过滤出满足条件的元素
const evens = numbers.filter(n => n % 2 === 0);
console.log(evens);  // [2, 4]

// map：把每个元素映射成新值
const doubled = numbers.map(n => n * 2);
console.log(doubled);  // [2, 4, 6, 8, 10]

// forEach：遍历每个元素
numbers.forEach(n => console.log(n));
```

> 🤔 **想多一点**：函数作为参数传递的模式，在 JavaScript 中叫"回调函数"（Callback）。它就像你在餐厅点菜后给服务员一个号码牌——"做好了叫我"。浏览器在事件发生时（例如点击按钮），就会"叫"你事先写好的回调函数。

---

# 步骤 7：`fetch` — 发网络请求获取数据

`fetch` 是浏览器内置的 API，用于发送 HTTP 请求获取数据。

### 7.1 基本用法

```javascript
fetch('https://jsonplaceholder.typicode.com/posts/1')
  .then(response => response.json())  // 把响应转成 JSON 对象
  .then(data => {
    console.log('获取到的数据：', data);
    console.log('标题：', data.title);
  })
  .catch(error => {
    console.error('请求失败：', error);
  });
```

### 7.2 使用 async/await（更现代的写法）

```javascript
async function fetchPost() {
  try {
    const response = await fetch('https://jsonplaceholder.typicode.com/posts/1');
    const data = await response.json();
    console.log('标题：', data.title);
  } catch (error) {
    console.error('请求失败：', error);
  }
}

fetchPost();
```

### 7.3 把数据渲染到页面上

```javascript
async function loadPosts() {
  const container = document.querySelector('#post-list');

  try {
    const response = await fetch('https://jsonplaceholder.typicode.com/posts');
    const posts = await response.json();

    // 只取前 5 条
    const top5 = posts.slice(0, 5);

    top5.forEach(post => {
      const div = document.createElement('div');
      div.className = 'card';
      div.innerHTML = `
        <h3>${post.title}</h3>
        <p>${post.body.slice(0, 100)}...</p>
      `;
      container.appendChild(div);
    });
  } catch (error) {
    container.innerHTML = '<p>加载失败，请检查网络连接。</p>';
  }
}

loadPosts();
```

> 📌 `jsonplaceholder.typicode.com` 是一个免费的假数据 API，专为前端练习设计。你可以用它来模拟后端返回的数据，不需要真的部署一个服务器。

---

# 步骤 8：练习——计数器

把前面学到的知识整合起来，做一个完整的计数器。

### HTML

```html
<div class="counter-container">
  <h2>计数器</h2>
  <p class="counter-display" id="count">0</p>
  <div class="counter-buttons">
    <button id="btn-decrease">-1</button>
    <button id="btn-reset">重置</button>
    <button id="btn-increase">+1</button>
  </div>
</div>
```

### CSS

```css
.counter-container {
  text-align: center;
  padding: 40px;
  max-width: 300px;
  margin: 50px auto;
  background-color: white;
  border-radius: 12px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.counter-display {
  font-size: 64px;
  font-weight: bold;
  color: #2c3e50;
  margin: 20px 0;
}

.counter-buttons {
  display: flex;
  gap: 10px;
  justify-content: center;
}

.counter-buttons button {
  padding: 10px 20px;
  font-size: 18px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  color: white;
  transition: opacity 0.2s;
}

.counter-buttons button:hover {
  opacity: 0.8;
}

#btn-decrease { background-color: #e74c3c; }
#btn-reset    { background-color: #95a5a6; }
#btn-increase { background-color: #27ae60; }
```

### JavaScript

```javascript
// 获取 DOM 元素
const countDisplay = document.querySelector('#count');
const btnDecrease = document.querySelector('#btn-decrease');
const btnReset = document.querySelector('#btn-reset');
const btnIncrease = document.querySelector('#btn-increase');

// 状态变量
let count = 0;

// 更新显示
function updateDisplay() {
  countDisplay.textContent = count;

  // 根据正负改变颜色
  if (count > 0) {
    countDisplay.style.color = '#27ae60';  // 绿色
  } else if (count < 0) {
    countDisplay.style.color = '#e74c3c';  // 红色
  } else {
    countDisplay.style.color = '#2c3e50';  // 默认
  }
}

// 绑定事件
btnIncrease.addEventListener('click', () => {
  count = count + 1;
  updateDisplay();
});

btnDecrease.addEventListener('click', () => {
  count = count - 1;
  updateDisplay();
});

btnReset.addEventListener('click', () => {
  count = 0;
  updateDisplay();
});

// 初始显示
updateDisplay();
```

### 效果

一个完整的计数器：点击 +1 数字增加变绿，点击 -1 数字减少变红，点击重置回到 0。

---

## 📋 完整代码清单

将以上所有练习整合到一个文件中：

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>JavaScript 练习</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: Arial, "Microsoft YaHei", sans-serif; background-color: #fafafa; padding: 20px; }

    .counter-container {
      text-align: center;
      padding: 40px;
      max-width: 300px;
      margin: 50px auto;
      background-color: white;
      border-radius: 12px;
      box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    .counter-display { font-size: 64px; font-weight: bold; color: #2c3e50; margin: 20px 0; }
    .counter-buttons { display: flex; gap: 10px; justify-content: center; }
    .counter-buttons button {
      padding: 10px 20px; font-size: 18px; border: none;
      border-radius: 6px; cursor: pointer; color: white; transition: opacity 0.2s;
    }
    .counter-buttons button:hover { opacity: 0.8; }
    #btn-decrease { background-color: #e74c3c; }
    #btn-reset    { background-color: #95a5a6; }
    #btn-increase { background-color: #27ae60; }

    #name-input { padding: 8px 12px; border: 1px solid #ddd; border-radius: 4px; font-size: 16px; }
  </style>
</head>
<body>

  <h1>JavaScript 练习</h1>

  <!-- 输入框实时显示 -->
  <section style="padding: 20px;">
    <input type="text" id="name-input" placeholder="输入你的名字">
    <p>你好，<span id="display-name">______</span>！</p>
  </section>

  <!-- 计数器 -->
  <div class="counter-container">
    <h2>计数器</h2>
    <p class="counter-display" id="count">0</p>
    <div class="counter-buttons">
      <button id="btn-decrease">-1</button>
      <button id="btn-reset">重置</button>
      <button id="btn-increase">+1</button>
    </div>
  </div>

  <script>
    // ========== 输入框实时显示 ==========
    const nameInput = document.querySelector('#name-input');
    const displayName = document.querySelector('#display-name');

    nameInput.addEventListener('input', () => {
      displayName.textContent = nameInput.value || '______';
    });

    // ========== 计数器 ==========
    const countDisplay = document.querySelector('#count');
    const btnDecrease = document.querySelector('#btn-decrease');
    const btnReset = document.querySelector('#btn-reset');
    const btnIncrease = document.querySelector('#btn-increase');

    let count = 0;

    function updateDisplay() {
      countDisplay.textContent = count;
      if (count > 0) {
        countDisplay.style.color = '#27ae60';
      } else if (count < 0) {
        countDisplay.style.color = '#e74c3c';
      } else {
        countDisplay.style.color = '#2c3e50';
      }
    }

    btnIncrease.addEventListener('click', () => {
      count = count + 1;
      updateDisplay();
    });

    btnDecrease.addEventListener('click', () => {
      count = count - 1;
      updateDisplay();
    });

    btnReset.addEventListener('click', () => {
      count = 0;
      updateDisplay();
    });
  </script>

</body>
</html>
```

---

## ✅ 最终验证

在浏览器中打开页面，确认：
- 在输入框中输入文字，下面的"你好，______！"实时更新
- 点击 +1，数字增加，变成绿色
- 点击 -1，数字减少，变成红色
- 点击重置，数字回到 0，颜色恢复默认
- 按 F12 → Console，没有红色报错信息

---

## 🧠 术语附录

| 术语 | 解释 |
|------|------|
| **DOM** | 文档对象模型，浏览器把 HTML 解析后生成的树状结构，JavaScript 通过它操作页面。 |
| **事件（Event）** | 用户在页面上发起的操作（点击、输入、滚动等），JS 可以监听并响应。 |
| **addEventListener** | 给元素绑定事件监听器的标准方法。 |
| **fetch** | 浏览器内置的 HTTP 请求 API，用于从服务器获取数据。 |
| **箭头函数（Arrow Function）** | ES6 引入的简洁函数写法：`(参数) => { 函数体 }`。 |
| **回调函数（Callback）** | 作为参数传给另一个函数的函数，在特定时机被调用。 |
| **async/await** | 处理异步操作的语法糖，让异步代码看起来像同步代码。 |
| **JSON** | JavaScript Object Notation，一种轻量数据交换格式，JS 对象和数组的字符串表示。 |
| **XSS** | 跨站脚本攻击，通过注入恶意 HTML/JS 代码攻击用户。使用 `textContent` 而非 `innerHTML` 可以防范。 |

---

## 🚧 已知坑点与禁止事项

- **`<script>` 放在 `<body>` 底部**：放在 `<head>` 会导致 DOM 还没加载完脚本就执行，操作元素会失败。
- **不要用 `var`**：用 `let` 和 `const`。`var` 有变量提升和作用域问题，是现代代码的禁区。
- **处理用户输入时用 `textContent`，不要用 `innerHTML`**：`innerHTML` 有 XSS 安全风险。
- **`querySelector` 只返回第一个匹配元素**：要获取所有匹配元素，用 `querySelectorAll`。
- **`fetch` 不会自动报错**：HTTP 状态码 404 或 500 时，`fetch` 不会进 `catch`，需要手动检查 `response.ok`。
- **`const` 对象属性可以修改**：`const` 只阻止重新赋值，不阻止修改对象内部的属性。

---

## 📖 下一步建议

完成这篇后，继续学习 **[05-第一个前端项目：静态博客页](05-第一个前端项目：静态博客页.md)**，把 HTML、CSS、JavaScript 组合起来，做一个完整的静态博客首页。