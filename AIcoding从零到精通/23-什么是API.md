# 23-什么是API：程序的"插座"

> **本篇属于**：第二篇·编程基本概念篇 | **预计阅读**：15分钟 | **难度**：★★☆☆☆
>
> 前置：读完第22章，了解JSON格式。不需要会写代码。

---

## API比喻：餐厅服务员

想象你去餐厅吃饭。

你坐在餐桌前，想点一份番茄炒蛋。你不会自己冲进厨房翻冰箱、开火、炒菜——你只需要：

```
你 → 告诉服务员 → 服务员传话给厨房 → 厨房做菜 → 服务员端菜给你
```

你不需要知道厨房里怎么炒菜，你只需要知道：
1. 服务员是谁（找谁点菜）
2. 菜单上有什么（能点什么）
3. 菜端上来是什么样（你得到什么）

**API（Application Programming Interface，应用程序编程接口）**📖 就是这个"服务员"。

> 📖 **API** = 两个程序之间沟通的"服务员"。你（程序A）告诉API你要什么，API去跟另一个程序（程序B）要东西，然后还给你。

---

## 现实世界中的API：你每天都在用，只是不知道

打开手机上的天气App——它怎么知道今天下不下雨？

你的手机没有装气象卫星。它是这样干的：

```
天气App → 调用天气API → 天气服务器查数据 → 返回天气数据 → App展示
```

打开外卖App看附近有什么餐厅——地图数据和餐厅列表是哪来的？

```
外卖App → 调用地图API + 餐厅API → 服务器返回数据 → App展示
```

**API就是程序之间的"插座"**——插上就能用，不需要知道内部怎么运转。

---

## HTTP请求：GET 和 POST

API最常见的通信方式是**HTTP请求**📖——就是网页浏览器和服务器之间说话的方式。

两个最常用的"动词"：

| 动词 | 代码 | 用途 | 比喻 |
|------|------|------|------|
| **GET** 📖 | `requests.get()` | 获取数据 | "服务员，给我菜单"——只读，不改 |
| **POST** 📖 | `requests.post()` | 提交数据 | "服务员，帮我下单"——发送数据给服务器 |

还有一个直观的对比：

```
GET  ≈ 你在Google搜索框输入关键词，按回车
POST ≈ 你填写注册表单，点击"提交"
```

---

## JSON：API交流的通用语言

API之间交流用的"语言"就是**JSON**📖（第22章已经见过）。

> 📖 **JSON** = JavaScript Object Notation，本质就是一段格式化的文本，长得像Python字典。

服务端返回的JSON可能是这样的：

```json
{
    "city": "北京",
    "temperature": 28,
    "weather": "晴",
    "humidity": 45
}
```

Python拿到JSON后，用 `json.loads()` 或 `response.json()` 就能转成字典，然后像第21章那样 `data["temperature"]` 就能取到温度。

---

## AI生成代码示例：查询免费天气

> 以下代码由AI生成：

```python
import requests                            # 导入requests库，用来发送HTTP请求

# 免费天气API地址（无需注册，直接可用）
url = "https://api.open-meteo.com/v1/forecast"

# 参数：告诉API你要查哪个城市的天气
params = {
    "latitude": 39.9042,                  # 北京的纬度
    "longitude": 116.4074,                # 北京的经度
    "current_weather": True               # 要当前天气数据
}

# 发送GET请求 —— 相当于"服务员，给我北京的天气"
response = requests.get(url, params=params)

# 把返回的JSON转成Python字典
data = response.json()

# 从字典里取出天气信息
weather = data["current_weather"]
temperature = weather["temperature"]       # 温度
windspeed = weather["windspeed"]           # 风速

print(f"北京当前温度：{temperature}°C")
print(f"风速：{windspeed} km/h")
```

**逐行讲解**：
- 第1行：`import requests` 导入requests库。如果没装，先在终端运行 `pip install requests`。
- 第4行：API的网址，相当于"服务员在哪"。
- 第7-10行：`params` 是你要传给API的参数——"我要查北纬39.9、东经116.4那个地方的天气"。
- 第13行：`requests.get()` 发送GET请求，相当于对着服务员说"给我菜单"。
- 第16行：`response.json()` 把API返回的JSON文本转成Python字典。
- 第19-21行：从字典里取数据，和21章一样。
- 第23-24行：打印结果。

**运行结果示例**：
```
北京当前温度：28.5°C
风速：12.3 km/h
```

---

## 你不需要手写API，但需要看懂AI写的

本书的所有项目都会用到API。你不用记住 `requests.get()` 怎么写，但你需要能看懂AI写的API调用代码：

- 看到 `requests.get()` → 知道在"获取数据"
- 看到 `requests.post()` → 知道在"提交数据"
- 看到 `response.json()` → 知道在"把服务器返回的JSON转成字典"
- 看到 `.json()` 后面的 `["xxx"]` → 知道在"从字典里取数据"

---

## 练习

打开Cursor（或Trae），对着AI说：

> "帮我写一个Python程序，调用免费API `https://api.open-meteo.com/v1/forecast`，查询上海的当前天气（上海纬度31.2304，经度121.4737），打印温度、风速、天气状况。如果请求失败，打印'API请求失败，请检查网络连接'。"

AI生成代码后：
1. 逐行读，用 `#` 注释写中文解释
2. 找出 `requests.get()` 和 `response.json()`，回答它们分别做了什么
3. 运行程序，看看输出的JSON里还有哪些天气信息是你没打印的

---

## 小结

| 你学到了什么 | 一句话 |
|-------------|--------|
| API是什么 | 程序之间的"服务员"——你点菜，它传话，厨房做，端给你 |
| HTTP请求 | 浏览器和服务器之间说话的方式 |
| GET | "获取数据"——像搜索 | 
| POST | "提交数据"——像填表单 |
| JSON | API交流的通用语言，长得像Python字典 |
| requests库 | Python发送HTTP请求的工具 |

---

## 自测

1. 用"餐厅服务员"比喻，解释API是什么。
2. `GET` 和 `POST` 的核心区别是什么？各举一个生活中的例子。
3. 下面这行代码在做什么？
   ```python
   data = response.json()
   ```

> **答案**：
> 1. 你（程序A）告诉API（服务员）你要什么，API去跟另一个程序（厨房/程序B）要东西，然后还给你（端菜）。
> 2. GET是获取数据（查天气、搜Google），POST是提交数据（注册账号、下单）。GET只读不改，POST会发送数据给服务器。
> 3. 把API返回的JSON格式文本，转成Python字典，方便后续用 `data["key"]` 的方式取数据。

> 📖 本章术语收录于附录E：API（应用程序编程接口）、HTTP请求、GET、POST、JSON