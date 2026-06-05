# 10-好Prompt的黄金法则

> **本篇属于**：第一篇·Prompt Engineering篇 | **预计阅读**：18分钟 | **难度**：★★☆☆☆
>
> 前置：第09章「什么是Prompt」。如果你还不清楚Prompt是什么，先回去读第09章。

---

这一章，我们不讲理论，直接给你**四条铁律**。每条铁律记住一句话——然后配合对比案例理解——就够了。

---

## 好Prompt黄金法则总览

把四条法则浓缩成一句话：

> **具体、有上下文、有约束、给例子。**

就像你让朋友帮你带外卖：

| 法则 | 点外卖的对比例子 |
|------|----------------|
| ❌ 不具体 | "带点吃的" |
| ✅ 具体 | "带一份黄焖鸡米饭，中辣" |
| ❌ 没上下文 | "帮我带一下"（带什么？去哪带？） |
| ✅ 有上下文 | "公司楼下那家黄焖鸡，帮我带一份" |
| ❌ 没约束 | "带份饭"（什么饭？几个人吃？） |
| ✅ 有约束 | "一份黄焖鸡米饭，中辣，不要香菜，打包" |
| ❌ 没例子 | "你知道我爱吃什么的" |
| ✅ 有例子 | "就上次那种，鸡块多一点的那个" |

---

## 法则一：具体（Be Specific）

**一句话：不要模糊，说清楚你想要什么。**

AI不是你的老朋友，不知道你喜欢什么。你越具体，它的输出越接近你想要的。

### ❌ 坏示例

```
帮我写一个爬虫
```

**AI输出（四种可能，你拿到的可能是任意一种）：**

```python
# 可能一：爬取整个网页HTML
import requests
url = "https://example.com"
response = requests.get(url)
print(response.text)
```

```python
# 可能二：爬取特定数据但不告诉你干了什么
from bs4 import BeautifulSoup
# AI 可能用你完全没见过的库，或者爬了一个你不需要的网站
```

```python
# 可能三：完全没有错误处理
import requests
r = requests.get("https://xxx.com")
data = r.json()  # 如果网站挂了，直接崩溃
```

```python
# 可能四：AI开始反问，浪费一轮对话
AI：请问你要爬什么网站？需要什么数据？用什么语言？有什么特殊要求？
```

### ✅ 好示例

```
帮我用Python写一个爬虫，具体要求：

- 目标网站：https://news.ycombinator.com
- 爬取内容：首页所有新闻标题和链接
- 输出格式：JSON，每条包含 title 和 url 两个字段
- 技术栈：requests + BeautifulSoup
- 错误处理：请求失败重试3次，每次间隔2秒
- 输出：调用完直接print结果
```

**AI输出：**

```python
import requests
from bs4 import BeautifulSoup
import json
import time

def fetch_hn_news():
    url = "https://news.ycombinator.com"
    
    # 带重试的请求
    for attempt in range(3):
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            break
        except requests.RequestException as e:
            if attempt == 2:
                print(f"请求失败: {e}")
                return []
            print(f"第{attempt+1}次重试...")
            time.sleep(2)
    
    soup = BeautifulSoup(response.text, 'html.parser')
    results = []
    
    for item in soup.select('.titleline'):
        title = item.get_text()
        link = item.find('a')['href']
        results.append({"title": title, "url": link})
    
    return results

if __name__ == "__main__":
    news = fetch_hn_news()
    print(json.dumps(news, ensure_ascii=False, indent=2))
    print(f"共抓取 {len(news)} 条新闻")
```

**看到区别了吗？** 好Prompt写出来的是"拿来就能用的工具"，坏Prompt写出来的是"你自己再改改"的半成品。

---

## 法则二：有上下文（Provide Context）

**一句话：告诉AI你已经有什么、你在做什么项目、技术栈是什么。**

想象你中途加入一个项目会议，同事上来就说"把这个改成那个"——你一脸懵，因为你不知道"这个"是什么、"那个"是什么、为什么要改。

AI也一样。没上下文时，AI会瞎猜；有上下文时，AI的输出会和你的项目无缝衔接。

### ❌ 坏示例

```
帮我给这个函数加错误处理
```
（你没贴函数代码，AI不知道是什么函数）

### ✅ 好示例

```
我在写一个Flask博客系统，下面是用户注册的现有代码。
帮我给这个函数加上错误处理：

1. 邮箱格式验证（必须包含@）
2. 用户名长度3-20字符
3. 数据库插入失败时返回500错误而不是崩溃
4. 所有错误返回格式统一为 {"success": false, "error": "具体描述"}

现有代码：
```python
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data['username']
    email = data['email']
    password = data['password']
    
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    db.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
               (username, email, hashed))
    return jsonify({"success": True, "message": "注册成功"})
```
```

**AI输出：**

```python
@app.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        
        # 参数存在性检查
        required_fields = ['username', 'email', 'password']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({"success": False, "error": f"缺少必要参数: {field}"}), 400
        
        username = data['username']
        email = data['email']
        password = data['password']
        
        # 用户名长度验证
        if not (3 <= len(username) <= 20):
            return jsonify({"success": False, "error": "用户名长度必须在3-20个字符之间"}), 400
        
        # 邮箱格式验证
        if '@' not in email:
            return jsonify({"success": False, "error": "邮箱格式不正确"}), 400
        
        # 密码强度验证（顺手加了，AI的"附加价值"）
        if len(password) < 8:
            return jsonify({"success": False, "error": "密码长度至少8位"}), 400
        
        hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        
        try:
            db.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
                       (username, email, hashed))
        except Exception as e:
            return jsonify({"success": False, "error": f"注册失败，请稍后重试"}), 500
        
        return jsonify({"success": True, "message": "注册成功"}), 201
        
    except Exception as e:
        return jsonify({"success": False, "error": "服务器内部错误"}), 500
```

**关键点：** 你给了上下文（"Flask博客系统"、"现有代码"、"统一错误格式"），AI的输出就直接和你的项目风格一致，不是另起炉灶。

---

## 法则三：有约束（Set Constraints）

**一句话：指定语言、框架、代码风格、输出格式。**

不给约束，AI会选它"最擅长的"——但不一定是你需要的。你可能用Python写后端，AI却给你JavaScript代码；你可能要面向对象的风格，AI却给你函数式。

### ❌ 坏示例

```
写一个排序函数
```

**AI可能输出10种不同的东西：**

```python
# Python版
def sort_list(lst):
    return sorted(lst)
```

```javascript
// JavaScript版
function sortList(arr) {
    return arr.sort((a, b) => a - b);
}
```

```java
// Java版
public static List<Integer> sortList(List<Integer> list) {
    Collections.sort(list);
    return list;
}
```

你拿到Java代码，而你的项目是Python——这就白写了。

### ✅ 好示例

```
帮我写一个排序函数。

约束：
- 语言：Python 3.10+
- 不使用内置sorted()或.sort()，自己实现
- 算法：快速排序（Quick Sort）
- 类型注解：必须使用typing
- 要有docstring
- 代码风格：PEP8
- 返回类型：List[int]（返回新列表，不修改原列表）
```

**AI输出：**

```python
from typing import List

def quick_sort(arr: List[int]) -> List[int]:
    """
    使用快速排序算法对整数列表进行排序。
    
    不修改原列表，返回一个新的排序后的列表。
    
    Args:
        arr: 待排序的整数列表
        
    Returns:
        排序后的新列表
        
    Examples:
        >>> quick_sort([3, 1, 4, 1, 5, 9])
        [1, 1, 3, 4, 5, 9]
    """
    if len(arr) <= 1:
        return arr.copy()
    
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    
    return quick_sort(left) + middle + quick_sort(right)
```

**你看，加了约束之后，AI的输出精确到你心里的预期。** 语言对、算法对、风格对、还有文档注释。

---

## 法则四：有示例（Few-shot）

**一句话：给AI看一个你想要的输出样例。**

📖 **术语：Few-shot（少样本学习）** = 在Prompt中提供1-3个示例，让AI模仿你的格式和风格。

这是最被低估的技巧。很多人只知道说"我要什么样的"，但不知道"给AI看一个例子"效率高得多。AI模仿能力极强，你给它一个示例，它就能照葫芦画瓢。

### ❌ 坏示例（没有示例）

```
帮我给这个项目写README文档
```

**AI输出（天知道写成什么样）：**

```
# Project Name

This is a project.

## Installation

pip install ...

## Usage

python main.py
```

### ✅ 好示例（有示例）

```
帮我给我的Python项目写README.md，参考以下格式（这是我另一个项目product-api的README，请模仿这个风格）：

参考格式示例：
'''
# Product API

一个简单的产品管理REST API，支持CRUD操作。

## 快速开始

\`\`\`bash
pip install -r requirements.txt
python app.py
\`\`\`

## API文档

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /products | 获取所有产品 |
| GET | /products/:id | 获取单个产品 |
| POST | /products | 创建产品 |
| PUT | /products/:id | 更新产品 |
| DELETE | /products/:id | 删除产品 |

## 技术栈

- Flask 3.0
- SQLite
- bcrypt
'''

现在给我的用户认证项目（auth-service）写README，功能包括：注册、登录、JWT验证、密码重置。
请严格模仿上面的格式和风格。
```

**AI输出（风格一致，格式一致，直接就能用）：**

```
# Auth Service

一个用户认证微服务，支持注册、登录、JWT验证、密码重置功能。

## 快速开始

\`\`\`bash
pip install -r requirements.txt
python app.py
\`\`\`

## API文档

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /register | 用户注册 |
| POST | /login | 用户登录（返回JWT Token） |
| GET | /verify | JWT Token验证 |
| POST | /reset-password | 密码重置请求 |
| PUT | /reset-password | 执行密码重置 |

## 技术栈

- Flask 3.0
- SQLite
- bcrypt
- PyJWT 2.8
```

**用Few-shot的威力在于：你不需要用文字描述"表格格式、章节顺序、语气"——一个例子胜过千言万语。**

---

## 总结：四条法则一句话

> **具体、有上下文、有约束、给例子。**

每次给AI发Prompt之前，心里过一遍这四句话：

1. 我说清楚**到底要什么**了吗？（具体）
2. 我告诉AI我的**项目和现状**了吗？（上下文）
3. 我限制了**语言、框架、风格**了吗？（约束）
4. 我给了**一个参考示例**吗？（例子）

**如果四条都做到了，你的Prompt就是黄金级的。**

---

## 小结

| 法则 | 核心 | 反问自己 |
|------|------|---------|
| 具体 | 不要模糊 | "我说清楚到底要什么了吗？" |
| 有上下文 | 别让AI瞎猜 | "AI知道我在做什么项目吗？" |
| 有约束 | 指定边界 | "我限制语言和风格了吗？" |
| 有示例 | 给AI看样例 | "我给了参考格式吗？" |

---

## 自测

1. 好Prompt的四条黄金法则分别是什么？用一句话概括每条。
2. 下面这个Prompt违反了哪几条法则？`"帮我写一个API"`
3. Few-shot是什么意思？为什么比直接描述"请用表格格式"更有效？

> **答案**：
> 1. 具体（说清楚到底要什么）、有上下文（告诉AI项目背景）、有约束（指定语言框架风格）、有示例（给AI看你想模仿的样例）。
> 2. 违反了全部四条——不具体（什么API？）、没上下文（什么项目？）、没约束（什么语言？什么框架？）、没示例（API文档长什么样？）。
> 3. Few-shot是在Prompt中提供1-3个示例，让AI模仿格式和风格。比文字描述更有效是因为AI擅长模式匹配——你给它看一个例子，它直接模仿；你描述格式，它会理解偏差。

> 📖 本章术语：**Few-shot（少样本学习）** — 已收录于附录E「技术术语速查」。