# 40-Trae实战：从零写一个项目

> **本篇属于**：第四篇·Trae从入门到精通 | **预计阅读**：40分钟 | **难度**：★★★★☆
>
> **前置条件**：已完成第36-39章，熟悉Trae的Builder和Chat模式。
>
> **准备工作**：打开Trae，找一个空文件夹，准备动手。

理论讲完了，这一章我们**动手做一个完整的项目**——一个天气查询工具。从零开始，用Trae Builder一句话生成，然后用Chat修改，最终跑通。

跟着做，一步一步来，你就能真正理解Trae Builder的威力。

---

## 40.1 我们要做什么

我们要做一个**天气查询工具**：

- **后端**：Python **📖 Flask** + 调用免费天气API
- **前端**：HTML页面，美观一点，用户体验好一点
- **功能**：
  1. 用户输入城市名，点击"查询"
  2. 调用天气API，获取当前天气数据
  3. 在页面上展示：温度、湿度、天气状况、风速等
  4. 显示天气图标，让页面更好看

> 📖 术语：Flask——Python的轻量级Web框架，用来快速搭建网页应用。简单理解：它帮你处理"接收用户输入 → 调用API → 返回HTML页面"这些繁琐的事情，你只需要关心业务逻辑。

这是一个典型的"小而完整"的项目——只有几个文件，但完整覆盖了前后端交互，非常适合展示Builder的能力。

---

## 40.2 第一步：Builder生成项目骨架

**1. 打开Trae，点击右侧AI面板的**"Builder"标签

**2. 在Builder输入框里输入这段文字**：

```
帮我做一个天气查询工具。
- 后端：Python Flask
- 前端：HTML + CSS + JavaScript
- 功能：用户输入城市名，查询天气，显示温度、湿度、天气状况、风速
- 调用免费天气API，比如和风天气或者OpenWeatherMap
- 需要申请API key，代码里要留出来让用户填
- 界面要简洁美观，居中布局，响应式（手机也能看）
- 保存最近查询的5个城市，显示在下方

请给我完整的项目结构，每个文件职责清晰。
```

**3. 按回车，发送给Builder**

---

## 40.3 第二步：等待Builder规划

Builder会开始思考，大概几秒钟之后，它会给你一个回复：

- 先复述一遍你的需求，确认理解正确
- 然后列出它规划的项目结构，告诉你每个文件负责什么
- 最后问你："这个结构可以吗？有没有需要调整的？"

### Builder大概会给出这样的结构：

```
weather-app/
├── app.py              # Flask主应用入口，处理请求
├── requirements.txt    # Python依赖列表
├── static/
│   ├── css/
│   │   └── style.css  # 样式文件
│   └── js/
│       └── script.js  # 前端JavaScript
└── templates/
    └── index.html     # HTML模板
```

**每个文件的职责**：
- `app.py`：Flask后端，接收用户请求，调用天气API，返回JSON数据
- `requirements.txt`：列出需要安装的依赖（flask, requests等）
- `style.css`：页面样式
- `script.js`：前端处理用户输入，调用后端接口，显示结果
- `index.html`：HTML页面结构

---

**现在，请你做这件事：仔细检查这个规划。**

- 功能全吗？（保存最近查询、API key占位符，都有了吗？）
- 文件结构合理吗？（每个文件职责清楚吗？）
- 技术栈对吗？（你想要的是Python Flask，没错吧？）

如果都没问题，在Builder里回复：**"好的，结构没问题，开始生成吧。"**

如果有问题，现在就说出来。比如："请加上错误处理，如果城市不存在，要显示错误提示"，Builder会调整规划。

---

## 40.4 第三步：Builder生成所有文件

Builder确认后，会自动：
1. 创建项目文件夹 `weather-app`
2. 创建上面列出的所有文件
3. 写入完整的代码
4. 告诉你如何运行项目

这一步Builder通常只需要几秒钟到一分钟，取决于项目复杂度。我们这个天气工具，大约10秒就能生成完。

---

## 40.5 第四步：看看生成了哪些文件

Builder生成完后，在Trae侧边栏你就能看到所有文件。我们来逐一看看：

### 文件1：`requirements.txt`

列出需要安装的依赖：
```txt
flask
requests
```

### 文件2：`app.py`

Flask后端入口，包含：
- Flask应用初始化
- 路由定义（首页、查询接口）
- 调用天气API的函数
- API key配置项（留空，让你填）

关键代码片段：
```python
# 替换成你自己的API Key
API_KEY = "your_api_key_here"
# 天气API基础URL
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"
```

### 文件3：`templates/index.html`

HTML页面结构，包含：
- 查询输入框和按钮
- 结果展示区域
- 最近查询历史区域
- 引入CSS和JS文件

### 文件4：`static/css/style.css`

CSS样式，让页面好看：
- 居中布局
- 卡片样式
- 响应式设计
- 颜色搭配

### 文件5：`static/js/script.js`

前端JavaScript：
- 处理"查询"按钮点击事件
- 调用后端API
- 渲染结果到页面
- 保存查询历史到本地存储

---

**看到了吗？** 你只说了一句话，Trae Builder帮你生成了**整个项目的所有文件**——前后端都有，能跑。

---

## 40.6 第五步：安装依赖，运行项目

**1. 打开Trae终端，进入项目文件夹**：

```bash
cd weather-app
```

**2. 安装依赖**：

```bash
pip install -r requirements.txt
```

**3. 申请免费天气API key**

我们用 **OpenWeatherMap** 的免费API，申请步骤：

1. 打开浏览器，访问：https://openweathermap.org/
2. 点击"Sign Up"注册一个免费账号
3. 登录后，进入"API Keys"页面
4. 复制你的API key
5. 打开 `app.py`，把 `your_api_key_here` 替换成你的API key：

```python
# 替换成你自己的API Key
API_KEY = "your_actual_api_key_here"  # 改成你复制的API key
```

> ⚠️ **安全提醒**：不要把API key发到公共仓库。你自己用就行。

**4. 启动应用**：

```bash
python app.py
```

你应该看到类似这样的输出：

```
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://127.0.0.1:5000
```

**5. 打开浏览器，访问地址**：

```
http://127.0.0.1:5000
```

---

## 40.7 验证运行效果

打开页面后，你应该看到：

- 一个大标题"天气查询"
- 一个输入框提示"输入城市名"
- 一个蓝色的"查询"按钮

**测试功能**：

1. 在输入框里输入 `Beijing`（英文城市名，OpenWeatherMap要求用英文）
2. 点击"查询"按钮
3. 几秒钟后，页面应该显示：
   - 城市名：Beijing
   - 温度：XX°C
   - 天气状况：Clear Sky / Clouds / Rain 等
   - 湿度：XX%
   - 风速：XX m/s
   - 保存到最近查询历史

✅ 如果能看到这些信息，说明项目**已经跑起来了！**

---

## 40.8 第六步：用Chat修复问题

如果跑不起来怎么办？没关系——这就是Trae的"自愈"能力：Builder生成 → 跑不通 → Chat修复 → 再跑。

我们来看常见问题：

### 🔴 问题1：提示"ModuleNotFoundError: No module named 'flask'"

```
ModuleNotFoundError: No module named 'flask'
```

**原因**：你没有安装Flask依赖。

**解决方案**：在终端里运行：
```bash
pip install flask
```

### 🔴 问题2：提示"401 Unauthorized"，查询不出天气

**原因**：API key不对，或者API key还没激活（OpenWeatherMap的API key注册后需要等几分钟才能激活）。

**解决方案**：
1. 检查 `app.py` 里的API key是否正确复制
2. 如果正确，等10-15分钟再试（新注册的API key需要几分钟激活）
3. 如果还是不行，换一个免费天气API（比如和风天气）

### 🔴 问题3：页面样式不对，按钮位置不对

**原因**：Builder生成的CSS可能有小问题，或者你的浏览器缓存了旧样式。

**解决方案**：
1. 把错误截图描述清楚，或者把CSS代码复制到Trae Chat
2. 在Chat里输入：
   ```
   这个页面的按钮位置不对，样式有点歪，帮我修一下style.css
   ```
3. Chat会给你修复后的CSS，你替换掉原来的，刷新页面再看

### 🔴 问题4：查询中文城市名不工作

你输入"北京"，查询返回404错误。

**原因**：OpenWeatherMap默认需要英文城市名，中文需要额外处理。

**解决方案**：在Trae Chat里输入：

```
现在查询中文城市名不工作，OpenWeatherMap需要英文。帮我修改一下：
1. 用户输入中文城市名，转换成拼音（或者直接把中文传给API试试）
2. 如果API不支持中文，提示用户输入英文
```

Chat会帮你修改代码，加上中文转拼音或者提示。

---

## 40.9 第七步：微调优化（可选）

项目跑起来后，你可以用Trae Chat继续微调：

**示例1：让界面更好看**
```
帮我优化一下界面，加个渐变背景，让卡片更圆润一点，加一点阴影
```

**示例2：增加新功能**
```
帮我加一个显示"体感温度"和"气压"的功能
```

**示例3：改进交互**
```
查询的时候加一个加载动画，让用户知道正在请求
```

每次微调，Chat都会帮你修改对应的文件。修改完刷新页面就能看到效果。

---

## 40.10 最终效果验收

当你完成所有步骤后，你的天气查询工具应该能：

- [ ] 打开页面，看到美观的界面
- [ ] 输入城市名，点击查询
- [ ] 显示温度、湿度、天气状况、风速
- [ ] 保存最近5次查询历史
- [ ] 手机浏览器打开也能正常显示

**如果你全部打勾**——**恭喜！你刚刚用Trae Builder从零生成了一个完整的前后端项目**。全程不超过10分钟。

---

## 完整代码清单（折叠）

<details>
<summary>点击展开查看完整代码</summary>

`app.py`（Flask后端）：

```python
from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

# 替换成你自己的OpenWeatherMap API Key
# 申请地址：https://openweathermap.org/api
API_KEY = "your_api_key_here"
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

# 中文城市名映射（可选，也可以用拼音）
CHINESE_CITIES = {
    "北京": "Beijing",
    "上海": "Shanghai",
    "广州": "Guangzhou",
    "深圳": "Shenzhen",
    "成都": "Chengdu",
    "杭州": "Hangzhou"
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/weather')
def get_weather():
    city = request.args.get('city', '').strip()
    
    if not city:
        return jsonify({'error': '请输入城市名'}), 400
    
    # 中文转英文
    if city in CHINESE_CITIES:
        city = CHINESE_CITIES[city]
    
    params = {
        'q': city,
        'appid': API_KEY,
        'units': 'metric',  # 使用摄氏度
        'lang': 'zh_cn'     # 中文描述
    }
    
    try:
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()
        data = response.json()
        
        if data['cod'] != 200:
            return jsonify({'error': data.get('message', '查询失败')}), 400
        
        result = {
            'city': data['name'],
            'country': data['sys']['country'],
            'temp': round(data['main']['temp'], 1),
            'feels_like': round(data['main']['feels_like'], 1),
            'humidity': data['main']['humidity'],
            'description': data['weather'][0]['description'],
            'icon': data['weather'][0]['icon'],
            'wind_speed': data['wind']['speed']
        }
        
        return jsonify(result)
    
    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'请求失败: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True)
```

`requirements.txt`：
```txt
flask>=2.0
requests>=2.25
```

`templates/index.html`：
```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>天气查询</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
</head>
<body>
    <div class="container">
        <h1>天气查询</h1>
        
        <div class="search-box">
            <input type="text" id="cityInput" placeholder="输入城市名（中文/英文）">
            <button id="searchBtn">查询</button>
        </div>
        
        <div id="loading" class="loading" style="display: none;">
            查询中...
        </div>
        
        <div id="error" class="error" style="display: none;"></div>
        
        <div id="result" class="result" style="display: none;">
            <div class="weather-header">
                <h2 id="cityName"></h2>
                <div class="weather-icon">
                    <img id="weatherIcon" alt="天气图标">
                </div>
            </div>
            
            <div class="weather-info">
                <div class="temp">
                    <span id="temperature"></span>°C
                </div>
                <div class="desc" id="description"></div>
                
                <div class="details">
                    <div class="detail-item">
                        <span class="label">体感温度</span>
                        <span id="feelsLike"></span>°C
                    </div>
                    <div class="detail-item">
                        <span class="label">湿度</span>
                        <span id="humidity"></span>%
                    </div>
                    <div class="detail-item">
                        <span class="label">风速</span>
                        <span id="windSpeed"></span> m/s
                    </div>
                </div>
            </div>
        </div>
        
        <div id="history" class="history">
            <h3>最近查询</h3>
            <div id="historyList"></div>
        </div>
    </div>
    
    <script src="{{ url_for('static', filename='js/script.js') }}"></script>
</body>
</html>
```

`static/css/style.css`：
```css
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    min-height: 100vh;
    padding: 20px;
    display: flex;
    justify-content: center;
    align-items: center;
}

.container {
    background: white;
    border-radius: 20px;
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
    padding: 40px;
    width: 100%;
    max-width: 500px;
}

h1 {
    text-align: center;
    color: #333;
    margin-bottom: 30px;
    font-size: 2em;
}

.search-box {
    display: flex;
    gap: 10px;
    margin-bottom: 20px;
}

#cityInput {
    flex: 1;
    padding: 12px 16px;
    border: 2px solid #e0e0e0;
    border-radius: 10px;
    font-size: 16px;
    transition: border-color 0.3s;
}

#cityInput:focus {
    outline: none;
    border-color: #667eea;
}

#searchBtn {
    padding: 12px 24px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border: none;
    border-radius: 10px;
    font-size: 16px;
    cursor: pointer;
    transition: transform 0.2s;
}

#searchBtn:hover {
    transform: translateY(-2px);
}

.loading {
    text-align: center;
    color: #666;
    padding: 10px;
}

.error {
    background: #ffebee;
    color: #c62828;
    padding: 12px;
    border-radius: 10px;
    margin-bottom: 20px;
}

.result {
    margin-top: 20px;
    animation: fadeIn 0.5s ease-in;
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}

.weather-header {
    text-align: center;
    margin-bottom: 20px;
}

.weather-header h2 {
    color: #333;
    margin-bottom: 10px;
}

.weather-icon img {
    width: 80px;
    height: 80px;
}

.weather-info {
    text-align: center;
}

.temp {
    font-size: 3em;
    font-weight: bold;
    color: #667eea;
    margin-bottom: 10px;
}

.desc {
    color: #666;
    font-size: 1.2em;
    margin-bottom: 20px;
    text-transform: capitalize;
}

.details {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 15px;
    margin-top: 20px;
}

.detail-item {
    background: #f5f5f5;
    padding: 15px;
    border-radius: 10px;
    text-align: center;
}

.detail-item .label {
    display: block;
    color: #666;
    font-size: 0.9em;
    margin-bottom: 5px;
}

.detail-item span:last-child {
    color: #333;
    font-weight: bold;
    font-size: 1.1em;
}

.history {
    margin-top: 30px;
    padding-top: 20px;
    border-top: 1px solid #eee;
}

.history h3 {
    color: #333;
    margin-bottom: 10px;
    font-size: 1.1em;
}

.history-item {
    display: inline-block;
    background: #f0f0f0;
    padding: 6px 12px;
    border-radius: 20px;
    margin: 4px;
    cursor: pointer;
    font-size: 0.9em;
    transition: background 0.2s;
}

.history-item:hover {
    background: #667eea;
    color: white;
}

@media (max-width: 600px) {
    .container {
        padding: 20px;
    }
    
    .details {
        grid-template-columns: 1fr;
    }
    
    .search-box {
        flex-direction: column;
    }
}
```

`static/js/script.js`：
```javascript
const cityInput = document.getElementById('cityInput');
const searchBtn = document.getElementById('searchBtn');
const resultDiv = document.getElementById('result');
const errorDiv = document.getElementById('error');
const loadingDiv = document.getElementById('loading');
const historyDiv = document.getElementById('historyList');

// 最近查询历史，最多保存5个
let searchHistory = JSON.parse(localStorage.getItem('searchHistory') || '[]');

// 渲染历史记录
function renderHistory() {
    if (searchHistory.length === 0) {
        document.getElementById('history').style.display = 'none';
        return;
    }
    document.getElementById('history').style.display = 'block';
    historyDiv.innerHTML = searchHistory.map(city => 
        `<span class="history-item" onclick="searchHistoryClick('${city}')">${city}</span>`
    ).join('');
}

// 点击历史记录重新查询
function searchHistoryClick(city) {
    cityInput.value = city;
    searchWeather(city);
}

// 添加到历史记录
function addToHistory(city) {
    // 去重
    searchHistory = searchHistory.filter(item => item !== city);
    // 添加到开头
    searchHistory.unshift(city);
    // 只保留最近5个
    if (searchHistory.length > 5) {
        searchHistory = searchHistory.slice(0, 5);
    }
    // 保存到本地存储
    localStorage.setItem('searchHistory', JSON.stringify(searchHistory));
    renderHistory();
}

async function searchWeather(city) {
    // 显示加载
    loadingDiv.style.display = 'block';
    resultDiv.style.display = 'none';
    errorDiv.style.display = 'none';
    
    try {
        const response = await fetch(`/api/weather?city=${encodeURIComponent(city)}`);
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || '查询失败');
        }
        
        // 显示结果
        document.getElementById('cityName').textContent = `${data.city}, ${data.country}`;
        document.getElementById('temperature').textContent = data.temp;
        document.getElementById('feelsLike').textContent = data.feels_like;
        document.getElementById('humidity').textContent = data.humidity;
        document.getElementById('windSpeed').textContent = data.wind_speed;
        document.getElementById('description').textContent = data.description;
        document.getElementById('weatherIcon').src = 
            `https://openweathermap.org/img/wn/${data.icon}@2x.png`;
        
        resultDiv.style.display = 'block';
        addToHistory(city);
        
    } catch (error) {
        errorDiv.textContent = error.message;
        errorDiv.style.display = 'block';
    } finally {
        loadingDiv.style.display = 'none';
    }
}

// 点击搜索按钮
searchBtn.addEventListener('click', () => {
    const city = cityInput.value.trim();
    if (city) {
        searchWeather(city);
    }
});

// 回车触发搜索
cityInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        searchBtn.click();
    }
});

// 初始渲染历史
renderHistory();
```

</details>

---

## 40.11 ⚠️ 如果出错了怎么办

### 🔴 问题1：API key 无效，返回401错误

**原因**：API key不对，或者还没激活。

**解决方案**：
1. 回到OpenWeatherMap官网，重新复制API key
2. 确认 `app.py` 里 `API_KEY` 已经替换，**不要留引号**
3. 新注册的API key需要等5-15分钟才能激活，耐心等一下再试
4. 如果还是不行，检查你的账户额度，免费版每天有调用次数限制

### 🔴 问题2：页面能打开，但查询后一直转圈

**原因**：跨域问题？后端API路由不对？

**检查一下**：
1. 打开浏览器开发者工具（F12）→ 控制台，看看有没有报错
2. 看看后端终端有没有报错
3. 确认后端路由是 `/api/weather`，前端调用的地址对不对
4. 把错误信息复制给Trae Chat，让它帮你修

### 🔴 问题3：查询中文城市找不到

**原因**：OpenWeatherMap的API对中文城市支持不好，API找不到城市。

**解决方案**：
- 先用英文城市名试试，比如输入 `Beijing` 而不是 "北京"
- 如果要支持中文，在Trae Chat里输入："帮我修改代码，支持中文城市名查询"，AI会帮你加上中文转拼音或映射

### 🔴 问题4：Flask启动失败，端口被占用

**症状**：`OSError: [Errno 98] Address already in use`

**原因**：5000端口已经被别的程序占用了。

**解决方案**：修改 `app.py` 最后一行，指定另一个端口：

```python
if __name__ == '__main__':
    app.run(debug=True, port=5001)  # 改成5001
```

然后重新启动，访问 `http://127.0.0.1:5001`。

---

## 小结

| 你学到了什么 | 一句话 |
|-------------|--------|
| Builder实战流程 | 一句话描述需求 → Builder规划 → 审查确认 → 生成项目 → 运行验证 → Chat修复 → 微调 |
| Builder能做什么 | 一句话生成完整的前后端项目骨架，包含所有文件 |
| 自愈循环 | Builder生成 → 跑不通 → Chat修复 → 再跑，直到成功 |
| API key占位 | 代码里用 `your_api_key_here`，用户替换，安全不泄露 |
| 最终效果 | 从零开始，10分钟得到一个能跑的天气查询工具 |

**关键感悟**：Trae Builder不是"帮你写几行代码"，它是**帮你搭整个房子**。你只需要说清楚要什么样的房子，它帮你打地基、砌墙、装修。你做了规划和验收，剩下的交给Builder。

---

## 自测

1. 在我们这个实战中，Builder总共做了哪些事情？请按顺序列出。
2. 如果Builder生成的项目跑不起来，你接下来应该怎么做？
3. 为什么API key在代码里要留占位符 `your_api_key_here`，而不是直接写在代码里？

> **答案**：
> 1. ①理解需求 → ②复述需求确认理解 → ③规划项目结构 → ④询问确认 → ⑤生成所有文件 → ⑥告诉如何运行。
> 2. ①把错误信息完整复制下来；②切到Trae Chat；③粘贴错误信息，告诉AI"这个项目运行报错了，帮我修一下"；④按Chat说的修改代码；⑤重新运行；⑥如果还报错，重复①-⑤。这就是Trae的自愈循环。
> 3. 因为如果直接把API key写在代码里，推到公共GitHub仓库，别人就能看到你的API key，可能会被盗用，扣你的额度甚至花钱。用占位符提醒用户替换自己的API key，这是安全好习惯。

---

> 📖 本章术语已收录：Flask、API Key