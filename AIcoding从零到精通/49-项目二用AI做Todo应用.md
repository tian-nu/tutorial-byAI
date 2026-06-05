# 49-项目二：用AI做一个Todo应用

> **本篇属于**：第六篇·实战项目篇 | **预计耗时**：2小时 | **难度**：★★★☆☆
>
> **前置条件**：已完成第48章（个人主页），Python已安装（第06章），了解基本的编程概念（第17-25章）。
>
> **可视化**：无

---

## 为什么第二个项目是"Todo应用"

第一个项目你只碰了一个HTML文件——就像在浅水区踩水。现在我们要往深一点的地方走。

**Todo应用是AI编程的"进阶池"**。它涉及：
- 一个后端（Python Flask）——处理数据
- 一个数据库（SQLite）——存储数据
- 一个前端（HTML/CSS）——展示数据

这三样东西需要协同工作，就像你同时指挥三个厨师各做一道菜，最后还要拼成一桌。但别怕——你是"指挥"不是"做菜"，AI帮你写所有代码。

---

## 49.1 你要做什么

做一个能**添加、删除、标记完成、筛选**待办事项的网页应用。数据存在数据库里，刷新页面不会丢。

**最终效果**：浏览器打开 `http://localhost:5000`，看到一个输入框和一个列表。输入"买牛奶"，点添加，列表里出现"买牛奶"。勾选它，它变灰划掉。点删除，它消失。刷新页面，数据还在。

**技术方案**：Python Flask（后端） + SQLite（数据库） + HTML/CSS（前端）。

---

## 49.2 技术名词速览（先认识，别被吓到）

| 名词 | 白话解释 |
|------|---------|
| **Flask** | 一个Python的"迷你厨房"——帮你处理网页请求，比如"有人访问了首页，给他看什么" |
| **📖 SQLite** | 一个"迷你数据库"——它不需要安装，就是一个文件。你把数据存进去，关了电脑再打开，数据还在。就像一个Excel文件，但更高效 |
| **后端** | 在服务器上跑的程序，你看不到它，但它负责处理数据 |
| **前端** | 你在浏览器里看到的页面，负责展示数据和交互 |
| **路由** | Flask里的一种"指路牌"——`/` 是首页，`/api/add` 是添加数据的接口 |

---

## 49.3 第一步：准备环境

### **1.** 新建项目文件夹 `todo-app`

在电脑上找个地方，新建 `todo-app` 文件夹。

### **2.** 在Cursor或Trae中打开这个文件夹

### **3.** 安装Flask

打开终端（`Ctrl + ``），输入：

```bash
pip install flask
```

验证安装是否成功：

```bash
python -c "import flask; print(flask.__version__)"
```

如果输出类似 `3.0.0` 的版本号，说明安装成功。

---

## 49.4 第二步：需求分析——让AI设计数据库

### **1.** 打开AI对话，输入以下Prompt：

```
我要做一个Todo待办事项应用，技术栈是Python Flask + SQLite + HTML/CSS。

功能需求：
1. 能添加新的待办事项（输入文字，点添加按钮）
2. 能删除待办事项（每条后面有个删除按钮）
3. 能标记完成/未完成（勾选框，完成的事项文字变灰+划线）
4. 能筛选：查看全部 / 只看未完成 / 只看已完成
5. 数据存储在SQLite中，刷新页面不丢失

请你先帮我设计数据库表结构，然后列出需要哪些API接口。
先不要写代码，我先确认你的设计。
```

### **2.** AI会输出类似这样的设计：

**数据库表 `todos`：**
| 列名 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键，自增 |
| content | TEXT | 待办事项内容 |
| completed | INTEGER | 0=未完成，1=已完成 |
| created_at | TIMESTAMP | 创建时间 |

**API接口：**
| 方法 | 路径 | 功能 |
|------|------|------|
| GET | `/` | 显示主页面 |
| POST | `/api/todos` | 添加Todo |
| PUT | `/api/todos/<id>` | 切换完成状态 |
| DELETE | `/api/todos/<id>` | 删除Todo |
| GET | `/api/todos` | 获取Todo列表（支持筛选参数） |

### **3.** 仔细看一下AI的设计，确认没问题后回复：
```
设计没问题，请开始写代码。先写后端Flask应用，再写前端HTML页面。
```

---

## 49.5 第三步：让AI写后端代码

AI会生成一个 `app.py` 文件。代码大概长这样：

```python
# app.py —— Flask后端
from flask import Flask, render_template, request, jsonify
import sqlite3
from datetime import datetime

app = Flask(__name__)

# 初始化数据库
def init_db():
    conn = sqlite3.connect('todos.db')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS todos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL,
            completed INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.close()

# 首页
@app.route('/')
def index():
    return render_template('index.html')

# 获取所有Todo
@app.route('/api/todos', methods=['GET'])
def get_todos():
    filter_type = request.args.get('filter', 'all')
    conn = sqlite3.connect('todos.db')
    conn.row_factory = sqlite3.Row
    
    if filter_type == 'completed':
        rows = conn.execute('SELECT * FROM todos WHERE completed = 1 ORDER BY id DESC').fetchall()
    elif filter_type == 'active':
        rows = conn.execute('SELECT * FROM todos WHERE completed = 0 ORDER BY id DESC').fetchall()
    else:
        rows = conn.execute('SELECT * FROM todos ORDER BY id DESC').fetchall()
    
    conn.close()
    return jsonify([dict(row) for row in rows])

# 添加Todo
@app.route('/api/todos', methods=['POST'])
def add_todo():
    data = request.get_json()
    content = data.get('content', '').strip()
    if not content:
        return jsonify({'error': '内容不能为空'}), 400
    
    conn = sqlite3.connect('todos.db')
    conn.execute('INSERT INTO todos (content) VALUES (?)', (content,))
    conn.commit()
    conn.close()
    return jsonify({'success': True}), 201

# ... 完整代码由AI生成，这里只展示关键部分
```

> ⚠️ **注意**：上面只是示意代码。**不要自己手打**，让AI生成完整代码。AI生成的代码会和这个差不多，但可能更完整。

---

## 49.6 第四步：让AI写前端页面

AI会接着生成前端页面。你需要告诉AI把HTML文件放到 `templates` 文件夹里：

```
请把前端HTML文件放在 templates/index.html 路径下。
```

Flask默认会从 `templates/` 文件夹加载HTML模板，所以路径必须对。

### 前端页面大概包含：

- 一个输入框 + 添加按钮
- 筛选按钮组：全部 / 未完成 / 已完成
- Todo列表，每条有：勾选框 + 文字 + 删除按钮
- 用JavaScript调用后端API（不刷新页面就能添加/删除/切换状态）

---

## 49.7 第五步：运行并测试

### **1.** 确认项目结构如下：

```
todo-app/
├── app.py              # 后端代码
├── todos.db            # SQLite数据库文件（运行后自动生成）
└── templates/
    └── index.html      # 前端页面
```

### **2.** 在终端运行：

```bash
python app.py
```

### **3.** 看到以下输出说明启动成功：

```
 * Running on http://127.0.0.1:5000
```

### **4.** 打开浏览器，访问 `http://localhost:5000`

### **5.** 试试功能：

- 输入"买牛奶"，点添加 → 列表出现"买牛奶"
- 勾选"买牛奶" → 文字变灰+划线
- 点删除 → 消失
- 点筛选"已完成" → 只显示已完成
- **关闭浏览器，重新打开 `http://localhost:5000`** → 数据还在！

---

## 49.8 第六步：出Bug了？正常！让AI修

### 一个真实的调试过程可能是这样的：

**第一次运行**：`python app.py` 报错 `ModuleNotFoundError: No module named 'flask'`
→ 执行 `pip install flask`，再运行

**第二次运行**：页面能打开，但添加Todo没反应
→ 按F12打开浏览器开发者工具 → Console面板有红色报错"404 Not Found"
→ 把报错信息发给AI："添加Todo时返回404，请检查API路由"
→ AI修复

**第三次运行**：页面能添加了，但刷新后数据没了
→ 告诉AI："刷新页面后数据丢失了，检查数据库是否正确保存"
→ AI发现是数据库连接没commit，修复

**第四次运行**：✅ 全部功能正常！

---

## 49.9 验收标准

| 序号 | 检查项 | 怎么做 |
|------|--------|--------|
| 1 | `python app.py` 能正常启动 | 终端看到 `Running on http://127.0.0.1:5000` |
| 2 | 浏览器能打开 `http://localhost:5000` | 看到输入框和空列表 |
| 3 | 能添加Todo项 | 输入文字点添加，列表出现新项 |
| 4 | 能标记完成 | 勾选后文字变灰+划线 |
| 5 | 能删除Todo项 | 点删除，该项消失 |
| 6 | 能筛选 | 点"未完成"/"已完成"后列表正确过滤 |
| 7 | 刷新页面数据不丢 | 关掉浏览器重新打开，数据还在 |
| 8 | 关闭终端后再运行 `python app.py`，数据还在 | 数据存在 `todos.db` 文件里 |

---

## 49.10 排错指南

### 🔴 问题1：`ModuleNotFoundError: No module named 'flask'`

**原因**：没装Flask。

**解决**：
```bash
pip install flask
```

### 🔴 问题2：`python app.py` 报错 `Address already in use`

**原因**：上一次运行的Flask还没关，端口（5000）被占用了。

**解决**：关掉之前运行的终端，或者按 `Ctrl + C` 停止上次的Flask进程。

### 🔴 问题3：页面打开后空白，F12 Console报错 `404 Not Found`

**原因**：API路径不对，或者前端JavaScript请求的URL和后端路由不匹配。

**解决**：把浏览器Console的完整报错发给AI，说"前端请求这个API返回404，请检查后端路由"。

### 🔴 问题4：添加Todo后刷新页面数据丢失

**原因**：数据库操作没有commit（提交），或者数据库文件路径不对。

**解决**：告诉AI"刷新页面后数据丢失了，请检查数据库连接是否正确commit"。同时检查 `todo-app` 文件夹里是否生成了 `todos.db` 文件。

### 🔴 问题5：中文输入后变成乱码

**原因**：可能是数据库连接或HTTP响应头没有设置UTF-8编码。

**解决**：告诉AI"中文输入后显示乱码，请确保数据库和HTTP响应都使用UTF-8编码"。

### 🔴 问题6：前端页面找不到CSS/JS文件

**原因**：Flask默认只从 `templates/` 加载HTML，CSS和JS需要放在 `static/` 文件夹。

**解决**：告诉AI"CSS和JS文件请放在static文件夹里，HTML中用/static/xxx.css引用"。

---

## 49.11 小结

| 你学到了什么 | 一句话 |
|-------------|--------|
| 前后端分离的概念 | 后端管数据（Python Flask），前端管展示（HTML/JS），它们通过API通信 |
| 📖 SQLite是什么 | 一个"迷你数据库"，就是一个文件，不需要安装 |
| Flask项目结构 | `app.py` + `templates/`（HTML）+ `static/`（CSS/JS） |
| API调试方法 | 按F12看Console报错，把报错给AI |
| 先设计再编码 | 让AI先设计数据库和API，你确认后再写代码，避免返工 |

---

## 49.12 自测

1. 你的Todo应用里，数据存在哪里？为什么关掉电脑再打开，数据还在？
2. 如果你想让Todo应用支持"编辑已添加的Todo文字"，你需要改哪些地方？（不需要写代码，只说思路）
3. 运行 `python app.py` 时报错 `Address already in use`，这是什么意思？怎么解决？

> **答案**：
> 1. 数据存在 `todos.db` 这个SQLite数据库文件里。SQLite把数据写到硬盘上，不像内存那样关机就没了，所以关掉电脑再打开，数据还在。
> 2. 需要改三处：①数据库操作层加一个更新SQL（`UPDATE todos SET content = ? WHERE id = ?`）；②后端加一个PUT路由处理编辑请求；③前端每条Todo加一个编辑按钮，点击后变成可编辑的输入框，确认后调用更新API。
> 3. 意思是5000端口被占用了，通常是上一次的Flask进程还没关。按 `Ctrl + C` 停止上次的进程，或者关掉之前的终端窗口再重新运行。

---

> 📖 本章术语：**SQLite**（数据库）——一个不需要安装的迷你数据库，本质就是一个文件，用来持久化存储数据。已收录于附录E「技术术语速查」。