# 09-什么是Prompt

> **本篇属于**：第一篇·Prompt Engineering篇 | **预计阅读**：10分钟 | **难度**：★☆☆☆☆
>
> 不需要任何前置知识。这一章是Prompt Engineering的起点，也是整本书最重要的基础之一。

---

## Prompt是什么：你给AI的"指令说明书"

假设你第一次去一家餐厅，服务员走过来问你："想吃什么？"

你会怎么说？

你不会只说"吃的"——那服务员完全不知道你想干嘛。你也不会只说"面"——什么面？汤面还是拌面？牛肉面还是素面？

你会说：**"来一碗红烧牛肉面，少放辣，多放香菜，面要硬一点。"**

这句话，就是一个**Prompt**（📖 术语：提示词）。

> **Prompt（提示词）** = 你给AI的指令说明书。你用自然语言（中文、英文都可以）告诉AI你要做什么、怎么做、有什么要求。

在AI编程里，Prompt就是你对AI说的话。可以是一句话，也可以是一大段。可以问问题，也可以下命令。

**这是一个Prompt：**

```
帮我写一个Python函数，计算1到100所有数字的总和。
```

**这也是一个Prompt：**

```
我的项目用Python Flask + SQLite，需要实现用户注册功能。
要求：
1. 用户名3-20个字符，不能包含特殊字符
2. 密码至少8位，必须包含数字和字母
3. 邮箱格式验证
4. 密码需要用bcrypt加密存储
5. 注册成功后返回JSON，包含用户ID和创建时间
6. 所有错误信息用中文，格式统一为 {"error": "错误信息"}
请帮我生成完整的代码。
```

这两个Prompt的区别，就是"来的都是客"和"VIP待遇"的区别——你说得越清楚，AI给的结果越好。

---

## 为什么Prompt质量决定输出质量

AI就像一个**超级聪明但完全不会读心术的新同事**。

想象你招了一个新员工，智商200，记忆力超群，但你对他说的第一句话是："把那个事儿办一下。"

他再聪明，也不知道"那个事儿"是什么。

AI也是这样。它的知识储备可能超过99%的人类，但它**完全不知道你心里在想什么**。它只会严格按你给的信息，去猜测你最可能想要的答案。

你给的信息越模糊，AI的猜测空间越大，出错的可能性越高。

你可能觉得"AI很智能啊，应该能理解我的意思吧？"

**不，它不能。** 它只是在统计上计算"最可能的回答是什么"。你给"帮我写一个登录"，它可能给你下面这些东西中的任意一种：

---

## 坏Prompt vs 好Prompt：同一个需求，天壤之别

### 场景：你想做一个用户登录功能

#### ❌ 坏Prompt：

```
帮我写一个登录
```

**AI可能的输出（几种糟糕的情况）：**

```
--- 情况A：AI写了一个HTML登录页面 ---
<!DOCTYPE html>
<html>
<body>
<form>
  <input type="text" placeholder="用户名">
  <input type="password" placeholder="密码">
  <button>登录</button>
</form>
</body>
</html>
```
> 问题：你本来想用Python写后端接口，结果AI给你一个HTML前端页面。它没错——你确实没说清楚。

```
--- 情况B：AI写了一个完全不支持密码加密的登录 ---
def login(username, password):
    user = db.query(f"SELECT * FROM users WHERE username='{username}' AND password='{password}'")
    ...
```
> 问题：密码明文存储 + SQL注入，安全灾难。

```
--- 情况C：AI问了你一大堆问题，你又要回很多轮 ---
AI：请问你用什么语言？（Python / Java / JavaScript？）
AI：请问你用什么框架？
AI：请问用什么数据库？
AI：需要什么验证逻辑？
...
```
> 问题：不是说AI提问不好，而是你把能用一句话说清楚的事，变成了5轮对话。

---

#### ✅ 好Prompt：

```
帮我用Python Flask写一个用户登录接口，要求如下：

技术栈：Flask + SQLite + bcrypt
输入：POST请求，JSON格式，包含 email 和 password
处理逻辑：
  1. 验证邮箱格式
  2. 验证密码非空
  3. 用bcrypt验证密码（数据库中密码已用bcrypt加密存储）
  4. 验证通过返回JWT token，失败返回具体错误信息

返回格式：
  成功：{"success": true, "token": "xxx", "user": {"id": 1, "email": "..."}}
  失败：{"success": false, "error": "具体错误信息"}

请写完整的Flask路由代码，包含错误处理。
```

**AI输出（大幅改善）：**

```python
import bcrypt
import jwt
from flask import Flask, request, jsonify
from datetime import datetime, timedelta

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'

@app.route('/api/login', methods=['POST'])
def login():
    # 获取请求数据
    data = request.get_json()
    
    # 参数校验
    if not data or 'email' not in data or 'password' not in data:
        return jsonify({"success": False, "error": "缺少email或password参数"}), 400
    
    email = data['email']
    password = data['password']
    
    # 邮箱格式验证
    if '@' not in email or '.' not in email:
        return jsonify({"success": False, "error": "邮箱格式不正确"}), 400
    
    # 密码非空验证
    if not password:
        return jsonify({"success": False, "error": "密码不能为空"}), 400
    
    # 查询用户（这里假设有数据库连接对象db）
    user = db.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    if not user:
        return jsonify({"success": False, "error": "邮箱或密码错误"}), 401
    
    # bcrypt验证密码
    if not bcrypt.checkpw(password.encode('utf-8'), user['password']):
        return jsonify({"success": False, "error": "邮箱或密码错误"}), 401
    
    # 生成JWT Token
    token = jwt.encode(
        {"user_id": user['id'], "exp": datetime.utcnow() + timedelta(hours=24)},
        app.config['SECRET_KEY'],
        algorithm="HS256"
    )
    
    return jsonify({
        "success": True,
        "token": token,
        "user": {"id": user['id'], "email": user['email']}
    })

if __name__ == '__main__':
    app.run(debug=True)
```

---

### 对比总结

| 维度 | 坏Prompt | 好Prompt |
|------|---------|---------|
| **代码可用性** | 前端HTML或完全不安全的后端 | 可直接使用的生产级接口 |
| **安全** | 明文密码 + SQL注入 | bcrypt加密 + 参数化查询 |
| **错误处理** | 没有或极其简陋 | 每种情况都有具体错误信息 |
| **返回格式** | 不确定 | 明确的JSON格式 |
| **需要额外对话** | 至少还要3-5轮 | 基本零修改直接用 |
| **你的精力消耗** | 高（来回改） | 低（一次到位） |

你会发现一个规律：**你在Prompt里省的字，AI会在输出里十倍的浪费你的时间。**

---

## Prompt Engineering（提示词工程）：一门新技能

现在你知道了什么是Prompt，那你可能会想："这谁不会啊，不就是说话吗？"

说话人人都会。但让AI**精确、稳定、高质量**地输出你想要的结果——这是一种技能。

**📖 术语：Prompt Engineering（提示词工程）** = 设计和优化给AI的指令，使其产生最准确、最有用输出的方法和技巧。

就像厨师做菜，把食材扔进锅里谁都会，但掌握火候、调味、摆盘就是厨艺。Prompt Engineering就是你和AI对话的"厨艺"。

**学完这篇（第09-16章），你将掌握的核心技能：**

1. 让AI一次就写出你想要的代码（而不是改五遍）
2. 用最少的字数表达最精确的需求
3. 当AI写错时，知道怎么让它快速修正
4. 把一个大需求拆成AI能吃下的若干小步骤

---

## 小结

| 你学到了什么 | 一句话 |
|-------------|--------|
| Prompt是什么 | 你给AI的"指令说明书" |
| Prompt为什么重要 | AI不会读心术，你越模糊它越乱写 |
| 好Prompt的效果 | 一次到位，省下反复修改的时间 |
| Prompt Engineering | 设计和优化Prompt的"厨艺" |

---

## 自测

1. 用一句话向你的朋友解释什么是Prompt。
2. 下面这个Prompt有什么问题？你会怎么改进？`"帮我写一个搜索功能"`
3. Prompt Engineering是什么意思？和"会打字"有什么区别？

> **答案**：
> 1. Prompt就是你告诉AI要干什么的指令，就像你跟厨师点菜一样。
> 2. 问题：太模糊——没说什么语言、什么框架、搜索什么数据、怎么展示结果。改进：至少加上技术栈、输入输出格式、具体需求描述。
> 3. Prompt Engineering是"设计和优化Prompt的方法和技巧"。会打字只是"能发出指令"，Prompt Engineering是"能发出精确指令，让AI稳定产出高质量结果"。

> 📖 本章术语：**Prompt（提示词）**、**Prompt Engineering（提示词工程）** — 已收录于附录E「技术术语速查」。