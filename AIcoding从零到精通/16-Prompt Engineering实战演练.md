# 16-Prompt Engineering实战演练

> **本篇属于**：第一篇·Prompt Engineering篇 | **预计阅读**：25分钟 | **难度**：★★★☆☆
>
> 前置：第09-15章全部。这一章是综合实战，你把前面学到的所有技巧都用上，从头到尾完成一个真实项目。

---

## 任务：做一个天气查询命令行工具

**需求：** 用Python做一个命令行天气查询工具，输入城市名，输出当前温度、天气描述、湿度、风速。

**技术栈：** Python 3.10+，使用免费天气API（wttr.in），纯命令行界面。

**为什么要做这个项目？**
- 涉及API调用（你会遇到网络错误）
- 涉及命令行参数（你会用到argparse）
- 涉及JSON解析（你会遇到数据格式问题）
- 涉及错误处理（你会遇到各种异常）
- 功能简单但完整（能在一个章节内完成）

---

## 完整Prompt链展示

下面展示的是**完整的对话**，包括你的Prompt和AI的输出。**注意：每一步你都要看AI的输出，验证正确后再进行下一步。**

---

### 第一步：需求描述 → AI出技术选型

**你的Prompt：**

```
你是一个10年经验的Python后端工程师。

我想做一个命令行天气查询工具，基本功能：
- 用户在命令行输入城市名，输出当前天气
- 显示：温度、天气描述、湿度、风速
- 支持中文城市名（如"北京"、"上海"）
- 免费，不需要API Key

请帮我做技术选型：
1. 推荐用什么天气API（免费、无需注册）
2. 项目需要哪些Python依赖
3. 建议的项目文件结构
4. 主要功能模块划分

请先分析，再给出建议。
```

**AI输出：**

```
## 技术选型分析

### 1. 天气API推荐：wttr.in

wttr.in 是最适合这个项目的选择：
- 完全免费，无需注册，无需API Key
- 支持中文城市名
- 返回JSON格式数据
- 示例：`curl wttr.in/Beijing?format=j1`

### 2. Python依赖

只需要两个库：
- `requests` — HTTP请求（wttr.in返回JSON）
- 不需要第三方JSON解析库（Python内置json）

### 3. 建议文件结构

```
weather_cli/
├── weather.py          # 主程序入口
├── weather_api.py      # API调用模块
├── weather_display.py  # 输出格式化模块
└── README.md
```

### 4. 功能模块划分

| 模块 | 职责 |
|------|------|
| weather_api.py | 调用wttr.in API，获取原始JSON数据，处理网络错误 |
| weather_display.py | 将JSON数据格式化为人类可读的输出 |
| weather.py | 解析命令行参数，协调API和显示模块 |
```

> ✅ 验证：技术选型合理。wttr.in确实免费、无需注册、支持中文城市名。文件结构清晰。进入下一步。

---

### 第二步：拆分文件 → AI写每个文件

**你的Prompt：**

```
好的，按你建议的文件结构来做。

先写 weather_api.py 模块。要求：
- 函数签名：def get_weather(city: str) -> dict
- 调用 wttr.in API：https://wttr.in/{city}?format=j1
- 返回解析后的JSON字典
- 错误处理：
  - 网络不通 → 抛出自定义异常 WeatherAPIError
  - API返回错误 → 抛出 WeatherAPIError 并附带错误信息
  - 超时设置为10秒
- 使用类型注解和docstring
- 只输出 weather_api.py 的内容
```

**AI输出（weather_api.py）：**

```python
"""
天气API调用模块。
使用 wttr.in 免费天气API，无需注册和API Key。
"""

import requests
from typing import Dict, Any

class WeatherAPIError(Exception):
    """天气API调用异常。"""
    pass

def get_weather(city: str) -> Dict[str, Any]:
    """
    获取指定城市的天气数据。
    
    Args:
        city: 城市名称，支持中文（如"北京"、"上海"）和英文（如"Beijing"）
        
    Returns:
        包含天气数据的字典，格式参见 wttr.in API 文档
        
    Raises:
        WeatherAPIError: API调用失败时抛出
        ValueError: city参数为空时抛出
        
    Examples:
        >>> data = get_weather("Beijing")
        >>> data['current_condition'][0]['temp_C']
        '15'
    """
    if not city or not city.strip():
        raise ValueError("城市名不能为空")
    
    url = f"https://wttr.in/{city.strip()}?format=j1"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.exceptions.Timeout:
        raise WeatherAPIError(f"请求超时：无法连接到天气服务（城市：{city}）")
    except requests.exceptions.ConnectionError:
        raise WeatherAPIError(f"网络连接失败：请检查网络设置（城市：{city}）")
    except requests.exceptions.RequestException as e:
        raise WeatherAPIError(f"请求天气数据失败：{e}")
    
    try:
        data = response.json()
    except ValueError:
        raise WeatherAPIError(f"解析天气数据失败：API返回格式异常")
    
    # wttr.in 即使城市不存在也返回200，所以需要检查数据
    # 如果返回的数据中没有current_condition，说明城市可能不存在
    if 'current_condition' not in data:
        raise WeatherAPIError(f"未找到城市 '{city}' 的天气数据，请检查城市名是否正确")
    
    return data
```

> ✅ 验证：代码结构清晰，错误处理完善，API地址正确。进入下一步。

---

**你的Prompt：**

```
weather_api.py 写好了，现在写 weather_display.py 模块。

要求：
- 函数签名：def format_weather(data: dict) -> str
- 接收 get_weather() 返回的原始JSON数据
- 提取并格式化以下信息：
  - 城市名
  - 当前温度（°C）
  - 体感温度（°C）
  - 天气描述（中文）
  - 湿度（%）
  - 风速（km/h）
- 输出格式美观，用表格或分隔线
- 只输出 weather_display.py 的内容
```

**AI输出（weather_display.py）：**

```python
"""
天气数据格式化显示模块。
将 wttr.in 返回的原始JSON格式化为人类可读的输出。
"""

from typing import Dict, Any

def format_weather(data: Dict[str, Any]) -> str:
    """
    将天气数据格式化为美观的文本输出。
    
    Args:
        data: get_weather() 返回的原始JSON数据
        
    Returns:
        格式化后的天气信息字符串
    """
    # 提取城市信息
    area = data.get('nearest_area', [{}])[0]
    city = area.get('areaName', [{}])[0].get('value', '未知城市')
    country = area.get('country', [{}])[0].get('value', '')
    
    # 提取当前天气
    current = data['current_condition'][0]
    temp_c = current.get('temp_C', 'N/A')
    feels_like = current.get('FeelsLikeC', 'N/A')
    humidity = current.get('humidity', 'N/A')
    wind_speed = current.get('windspeedKmph', 'N/A')
    wind_dir = current.get('winddir16Point', 'N/A')
    
    # 天气描述（wttr.in 返回的是英文，我们直接展示）
    weather_desc = current.get('weatherDesc', [{}])[0].get('value', '未知')
    
    # 能见度和紫外线指数（可选信息）
    visibility = current.get('visibility', 'N/A')
    uv_index = current.get('uvIndex', 'N/A')
    
    # 格式化输出
    location = f"{city}, {country}" if country else city
    
    output = f"""
╔══════════════════════════════════╗
║        🌤️  天气查询结果          ║
╠══════════════════════════════════╣
║  📍 城市: {location:<22} ║
╠══════════════════════════════════╣
║  🌡️  当前温度: {temp_c:>5}°C            ║
║  🥶 体感温度: {feels_like:>5}°C            ║
║  ☁️  天气状况: {weather_desc:<22} ║
║  💧 湿度:     {humidity:>5}%             ║
║  💨 风速:     {wind_speed:>5} km/h ({wind_dir})  ║
╠══════════════════════════════════╣
║  👁️  能见度:  {visibility:>5} km          ║
║  ☀️  紫外线:   {uv_index:>5}              ║
╚══════════════════════════════════╝
"""
    return output.strip()
```

> ✅ 验证：格式美观，提取了所有需要的字段。进入下一步。

---

**你的Prompt：**

```
weather_api.py 和 weather_display.py 都写好了，现在写主程序 weather.py。

要求：
- 使用 argparse 解析命令行参数
- 用法：python weather.py <城市名>
- 也支持 --city 参数：python weather.py --city 北京
- 调用 weather_api.get_weather() 获取数据
- 调用 weather_display.format_weather() 格式化输出
- 如果出错，显示友好的错误信息
- 支持 --help 显示帮助
- 只输出 weather.py 的内容
```

**AI输出（weather.py）：**

```python
"""
天气查询命令行工具 — 主程序入口。

用法:
    python weather.py 北京
    python weather.py --city 上海
    python weather.py --help
"""

import argparse
import sys
from weather_api import get_weather, WeatherAPIError
from weather_display import format_weather

def main():
    parser = argparse.ArgumentParser(
        description='🌤️  命令行天气查询工具 — 使用 wttr.in 免费API',
        epilog='示例: python weather.py 北京'
    )
    
    parser.add_argument(
        'city',
        nargs='?',
        help='要查询的城市名（支持中文和英文）'
    )
    parser.add_argument(
        '--city', '-c',
        dest='city_opt',
        help='要查询的城市名（--city 参数方式）'
    )
    
    args = parser.parse_args()
    
    # 确定城市名：优先使用 --city 参数，否则使用位置参数
    city = args.city_opt or args.city
    
    if not city:
        parser.print_help()
        print("\n❌ 错误: 请指定要查询的城市名")
        sys.exit(1)
    
    try:
        print(f"🔍 正在查询 {city} 的天气...")
        data = get_weather(city)
        output = format_weather(data)
        print(output)
    except WeatherAPIError as e:
        print(f"❌ {e}")
        sys.exit(1)
    except ValueError as e:
        print(f"❌ 参数错误: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n已取消查询")
        sys.exit(0)

if __name__ == "__main__":
    main()
```

> ✅ 验证：argparse使用正确，错误处理完善，支持两种参数方式。进入下一步。

---

### 第三步：运行 → 报错 → 把错误给AI → AI修复

你运行 `python weather.py 北京`，结果：

```
🔍 正在查询 北京 的天气...
❌ 请求天气数据失败：HTTPSConnectionPool(host='wttr.in', port=443): Max retries exceeded
```

**你的Prompt：**

```
运行报错了：

'''
🔍 正在查询 北京 的天气...
❌ 请求天气数据失败：HTTPSConnectionPool(host='wttr.in', port=443): Max retries exceeded
'''

可能的原因：
1. 网络问题（但我其他网站能访问）
2. wttr.in 在中国大陆可能被墙
3. 需要设置代理

请帮我修改 weather_api.py，加上：
1. 代理支持（从环境变量 HTTP_PROXY 和 HTTPS_PROXY 读取）
2. 如果直连和代理都失败，给出更友好的提示
3. 尝试使用 HTTP 而非 HTTPS（wttr.in 支持 HTTP）
```

**AI输出（修改后的 weather_api.py）：**

```python
"""
天气API调用模块。
使用 wttr.in 免费天气API，无需注册和API Key。
"""

import os
import requests
from typing import Dict, Any, Optional

class WeatherAPIError(Exception):
    """天气API调用异常。"""
    pass

def _get_proxies() -> Optional[Dict[str, str]]:
    """从环境变量读取代理配置。"""
    proxies = {}
    http_proxy = os.environ.get('HTTP_PROXY') or os.environ.get('http_proxy')
    https_proxy = os.environ.get('HTTPS_PROXY') or os.environ.get('https_proxy')
    
    if http_proxy:
        proxies['http'] = http_proxy
    if https_proxy:
        proxies['https'] = https_proxy
    
    return proxies if proxies else None

def get_weather(city: str) -> Dict[str, Any]:
    """
    获取指定城市的天气数据。
    
    Args:
        city: 城市名称，支持中文和英文
        
    Returns:
        包含天气数据的字典
        
    Raises:
        WeatherAPIError: API调用失败时抛出
        ValueError: city参数为空时抛出
    """
    if not city or not city.strip():
        raise ValueError("城市名不能为空")
    
    city = city.strip()
    proxies = _get_proxies()
    
    # 尝试多个URL（HTTPS优先，HTTP备用）
    urls = [
        f"https://wttr.in/{city}?format=j1",
        f"http://wttr.in/{city}?format=j1",
    ]
    
    last_error = None
    
    for url in urls:
        try:
            response = requests.get(url, timeout=10, proxies=proxies)
            response.raise_for_status()
            break  # 成功则跳出循环
        except requests.exceptions.Timeout:
            last_error = f"请求超时"
            continue
        except requests.exceptions.ConnectionError:
            last_error = f"无法连接到天气服务"
            continue
        except requests.exceptions.RequestException as e:
            last_error = str(e)
            continue
    else:
        # 所有URL都失败了
        proxy_msg = ""
        if proxies:
            proxy_msg = f"\n  当前使用代理: {proxies}"
        else:
            proxy_msg = "\n  未配置代理（可设置 HTTP_PROXY/HTTPS_PROXY 环境变量）"
        
        raise WeatherAPIError(
            f"无法获取天气数据，所有连接方式均失败。{proxy_msg}\n"
            f"  请检查：\n"
            f"  1. 网络连接是否正常\n"
            f"  2. 是否需要配置代理\n"
            f"  3. 城市名 '{city}' 是否正确"
        )
    
    try:
        data = response.json()
    except ValueError:
        raise WeatherAPIError("解析天气数据失败：API返回格式异常")
    
    if 'current_condition' not in data:
        raise WeatherAPIError(f"未找到城市 '{city}' 的天气数据，请检查城市名是否正确")
    
    return data
```

> ✅ 验证：添加了代理支持、HTTP/HTTPS双URL回退、详细错误提示。重新运行，成功！

**运行结果：**

```
🔍 正在查询 北京 的天气...
╔══════════════════════════════════╗
║        🌤️  天气查询结果          ║
╠══════════════════════════════════╣
║  📍 城市: Beijing, China        ║
╠══════════════════════════════════╣
║  🌡️  当前温度:    22°C            ║
║  🥶 体感温度:    20°C            ║
║  ☁️  天气状况: Sunny              ║
║  💧 湿度:        45%             ║
║  💨 风速:        15 km/h (NW)    ║
╠══════════════════════════════════╣
║  👁️  能见度:     10 km          ║
║  ☀️  紫外线:       5              ║
╚══════════════════════════════════╝
```

> ✅ 成功运行！

---

### 第四步：优化 → 加错误处理 → 加README

**你的Prompt：**

```
工具已经能跑了，现在做最后的优化：

1. 添加 README.md 文件，包含：
   - 项目简介
   - 安装方法
   - 使用示例
   - 常见问题（网络问题、代理配置）

2. 给 weather.py 添加 --version 参数，显示版本号

3. 优化 weather_display.py 的输出：如果天气是"Sunny"显示☀️，如果是"Rain"显示🌧️

请分别输出修改后的文件。
```

**AI输出（README.md）：**

```markdown
# 🌤️ Weather CLI

一个简单的命令行天气查询工具，使用 wttr.in 免费API。

## 功能

- 查询全球任意城市的实时天气
- 显示温度、体感温度、天气描述、湿度、风速
- 支持中文城市名（北京、上海、东京等）
- 完全免费，无需注册，无需API Key

## 安装

```bash
# 安装依赖
pip install requests
```

## 使用

```bash
# 基本用法
python weather.py 北京

# 使用 --city 参数
python weather.py --city 上海

# 查看帮助
python weather.py --help

# 查看版本
python weather.py --version
```

## 常见问题

### 网络连接失败

如果在中国大陆使用，wttr.in 可能被墙。解决方法：

1. **配置代理**：
   ```bash
   # Windows (PowerShell)
   $env:HTTP_PROXY="http://127.0.0.1:7890"
   $env:HTTPS_PROXY="http://127.0.0.1:7890"
   
   # Linux/Mac
   export HTTP_PROXY="http://127.0.0.1:7890"
   export HTTPS_PROXY="http://127.0.0.1:7890"
   ```

2. **检查和更新代理配置**：工具会自动读取环境变量

### 城市名查不到

wttr.in 使用英文城市名作为查询基础。如果中文名查不到，试试英文名：
```bash
python weather.py Tokyo
python weather.py "New York"
```

## 技术栈

- Python 3.10+
- requests
- wttr.in API
```

**AI输出（修改后的 weather_display.py 关键部分）：**

```python
# ... 前面的代码不变 ...

# 天气图标映射
WEATHER_ICONS = {
    'Sunny': '☀️',
    'Clear': '🌙',
    'Partly cloudy': '⛅',
    'Cloudy': '☁️',
    'Overcast': '☁️',
    'Mist': '🌫️',
    'Fog': '🌫️',
    'Rain': '🌧️',
    'Light rain': '🌦️',
    'Heavy rain': '⛈️',
    'Snow': '❄️',
    'Thunder': '⚡',
}

def _get_weather_icon(desc: str) -> str:
    """根据天气描述返回对应图标。"""
    for key, icon in WEATHER_ICONS.items():
        if key.lower() in desc.lower():
            return icon
    return '🌡️'

# ... 在 format_weather 中使用 _get_weather_icon(weather_desc) ...
```

> ✅ 优化完成。项目从3个文件扩展为4个文件，功能完整，文档齐全。

---

## 最终项目文件清单

```
weather_cli/
├── weather.py          # 主程序（含argparse、--version、--help）
├── weather_api.py      # API调用（含代理支持、HTTP/HTTPS双回退）
├── weather_display.py  # 格式化输出（含天气图标映射）
└── README.md           # 项目文档
```

---

## 本次实战用到的所有技巧回顾

| 步骤 | 用到的技巧 | 对应章节 |
|------|-----------|---------|
| 第一步 | 角色设定（"10年经验工程师"）+ CoT思维链（"先分析再给建议"） | 第15章、第12章 |
| 第二步 | 具体（说清楚API地址、返回格式）+ 约束（类型注解、docstring）+ 分步（一次只写一个文件） | 第10章、第12章 |
| 第三步 | 错误修正三步法（贴完整错误信息 + 说期望 + 给AI分析空间） | 第13章 |
| 第四步 | 迭代优化（第一版能跑 → 加功能 → 加文档） | 第14章 |

---

## 小结

| 你学到了什么 | 一句话 |
|-------------|--------|
| 完整Prompt链 | 从需求 → 设计 → 编码 → 排错 → 优化，一条龙 |
| 每一步都验证 | 不看AI输出就进入下一步 = 给自己埋雷 |
| 技巧综合运用 | 角色设定 + 思维链 + 具体约束 + 分步 + 错误修正 + 迭代优化 |
| 从0到1的完整项目 | 4个文件，100行代码，30分钟完成 |

---

## 自测

1. 这次实战用到了哪些Prompt技巧？请至少说出5个。
2. 为什么AI写代码时，你要"一次只让AI写一个文件"？（提示：回顾第12章）
3. 如果天气查询工具运行失败，你应该怎么向AI描述错误？（提示：回顾第13章的三步修正法）

> **答案**：
> 1. 角色设定（"10年经验工程师"）、思维链（"先分析再给建议"）、具体（明确API地址和返回格式）、约束（类型注解+docstring）、分步引导（一次一个文件）、错误修正三步法（贴错误+说期望+给分析）、迭代优化（能跑→加代理→加图标→加README）、Few-shot（README格式参考）。
> 2. 因为AI的上下文窗口有限，一次写多个文件会"忘事"，导致前后代码不一致。分步写，每步都基于前面已验证的代码，质量更高。
> 3. 三步修正法：①把完整错误信息复制粘贴给AI ②说清楚期望改成什么样（比如"加上代理支持"）③让AI解释修改思路。不要说"不对，重新写"。