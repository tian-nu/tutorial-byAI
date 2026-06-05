# 附录D：常见错误与排错指南

> 遇到错误不要慌，Ctrl+C复制错误信息，Ctrl+V粘贴给AI，AI会帮你解决90%的问题。

---

## 一、Python错误

### SyntaxError（语法错误）
```
SyntaxError: invalid syntax
```
**中文解释**：代码语法写错了，通常是拼写错误、括号不匹配、缺少冒号等。
**解决**：检查提示行附近的代码，特别注意冒号、括号、引号。

### IndentationError（缩进错误）
```
IndentationError: expected an indented block
```
**中文解释**：Python用缩进表示代码块，缩进不对就报这个错。
**解决**：检查该缩进的地方是否缩进了，不该缩进的地方是否多了空格。用Tab还是空格要统一（建议用4个空格）。

### NameError（变量名错误）
```
NameError: name 'xxx' is not defined
```
**中文解释**：你用了变量`xxx`，但Python不知道它是什么。
**解决**：检查变量名是否拼写正确，是否在使用前定义了这个变量。

### TypeError（类型错误）
```
TypeError: can only concatenate str (not "int") to str
```
**中文解释**：你把不同类型的数据混在一起用了，比如把字符串和数字直接相加。
**解决**：用`str()`把数字转成字符串，或用`int()`把字符串转成数字。

### ImportError / ModuleNotFoundError
```
ModuleNotFoundError: No module named 'xxx'
```
**中文解释**：你用了`import xxx`，但Python找不到这个库。
**解决**：运行`pip install xxx`安装这个库。

### FileNotFoundError
```
FileNotFoundError: [Errno 2] No such file or directory: 'xxx'
```
**中文解释**：你要打开的文件不存在。
**解决**：检查文件路径是否正确，文件是否在程序所在的目录。

### PermissionError
```
PermissionError: [Errno 13] Permission denied: 'xxx'
```
**中文解释**：没有权限读写这个文件。
**解决**：检查文件是否被其他程序打开，是否只读，是否有管理员权限。

---

## 二、Flask错误

### ImportError: No module named 'flask'
```
ModuleNotFoundError: No module named 'flask'
```
**中文解释**：Flask没安装。
**解决**：运行`pip install flask`。

### Address already in use
```
OSError: [Errno 98] Address already in use
```
**中文解释**：端口5000已经被占用了，可能你之前运行的程序还没关。
**解决**：关闭之前的程序，或换个端口`app.run(port=5001)`。

### Internal Server Error (500)
**中文解释**：服务器内部出错，代码逻辑有问题。
**解决**：看终端里的完整错误信息，复制给AI分析。

### Method Not Allowed (405)
**中文解释**：请求方法不对，比如用GET请求了一个只接受POST的接口。
**解决**：检查你的请求方法是否正确。

---

## 三、HTML/前端错误

### 中文乱码
**现象**：网页上中文显示成乱码。
**原因**：HTML文件缺少字符编码声明。
**解决**：在HTML的`<head>`里加`<meta charset="UTF-8">`。

### 图片不显示
**现象**：网页上图片显示成叉号。
**原因**：图片路径不对。
**解决**：检查图片是否在正确的目录，路径是否正确（相对路径用`./`或直接写文件名）。

### 样式不生效
**现象**：CSS样式没应用到页面上。
**原因**：CSS文件路径不对，或选择器写错了。
**解决**：检查CSS文件路径，用浏览器开发者工具（F12）检查元素。

---

## 四、终端/命令行错误

### 'python' 不是内部或外部命令
**现象**：在终端输入`python`，提示找不到。
**原因**：Python没装，或PATH没配置。
**解决**：重新安装Python，勾选"Add Python to PATH"。

### pip 不是内部或外部命令
**解决**：用`python -m pip`代替`pip`，例如`python -m pip install flask`。

### 终端中文乱码
**解决**：Windows终端输入`chcp 65001`切换到UTF-8编码。

---

## 五、AI工具错误

### Cursor Chat不响应
**原因**：网络问题或上下文太长。
**解决**：检查网络，清空上下文（点击Chat面板的垃圾桶图标），重新问。

### Tab补全不出现
**原因**：可能网络延迟，或当前文件类型不支持。
**解决**：等几秒，或先写注释再试。如果还不行，用Ctrl+K代替。

### Agent模式循环不停
**原因**：Agent陷入死循环，一直改不对。
**解决**：手动停止Agent，分析问题原因，重新描述需求。

### 模型连接失败
**原因**：网络问题，或API额度用完了。
**解决**：检查网络，换一个模型试试。

---

## 六、通用排错流程

当遇到任何错误，按以下步骤操作：

1. **不要慌**：错误是学习的一部分
2. **复制完整错误信息**：Ctrl+C复制终端里的错误信息
3. **粘贴给AI**：Ctrl+V粘贴到Cursor Chat或Trae Chat
4. **告诉AI上下文**：你做了什么操作、想要什么结果
5. **让AI分析**：AI会解释错误原因并给出修复方案
6. **按方案修改**：按AI的建议修改代码
7. **验证**：重新运行，确认问题解决

> **口诀**：不要瞎猜，复制粘贴，问AI，改代码，再验证。