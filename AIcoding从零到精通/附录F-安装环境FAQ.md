# 附录F：安装环境FAQ

> 安装Python、Cursor、Trae时最常见的20个问题及解决方案。

---

## 一、Python安装问题

### Q1：安装Python时忘记勾选"Add Python to PATH"怎么办？
**A**：两种方法：
1. 重新运行安装程序，勾选"Add Python to PATH"
2. 手动添加：Windows搜索"环境变量" → 编辑系统环境变量 → Path → 添加Python安装目录（如`C:\Python312\`和`C:\Python312\Scripts\`）

### Q2：终端输入`python`提示"'python'不是内部或外部命令"
**A**：参考Q1，PATH没配置好。

### Q3：终端输入`python`显示的是Python 2.x
**A**：Mac用户可能同时装了Python 2和Python 3，用`python3`命令代替`python`。

### Q4：`pip install`提示权限不足
**A**：
- Windows：用管理员身份运行终端
- Mac/Linux：`pip install --user <包名>` 或 `sudo pip install <包名>`

### Q5：Python官网下载太慢
**A**：使用国内镜像源：
- 清华镜像：https://mirrors.tuna.tsinghua.edu.cn/python/
- 或者安装Python后用镜像源装包：`pip install -i https://pypi.tuna.tsinghua.edu.cn/simple <包名>`

---

## 二、Cursor安装问题

### Q6：Cursor官网打不开或下载慢
**A**：Cursor官网是 https://cursor.com ，如果访问慢，可以尝试：
- 换个网络环境
- 用镜像站下载

### Q7：Cursor登录需要翻墙吗？
**A**：Cursor国内可以直接访问，但速度可能较慢。登录支持邮箱、GitHub、Google账号。

### Q8：Cursor打开后一片空白
**A**：
1. 检查显卡驱动是否最新
2. 尝试以管理员身份运行
3. 删除`%USERPROFILE%\.cursor`配置文件夹，重新打开

### Q9：Cursor提示"模型加载失败"
**A**：
1. 检查网络连接
2. 尝试切换模型（从GPT-4o切换到Claude 3.5）
3. 检查是否登录成功

### Q10：Cursor免费额度用完了怎么办？
**A**：
- 免费版每月有2000次AI补全额度
- 用完后可以升级Pro版（$20/月），无限使用
- 或者切换到免费模型（如DeepSeek V3）

---

## 三、Trae安装问题

### Q11：Trae官网打不开
**A**：Trae官网是 https://trae.ai ，国内访问顺畅，不需要翻墙。

### Q12：Trae登录需要什么账号？
**A**：国内手机号直接登录，不需要邮箱或Google账号。

### Q13：Trae启动黑屏
**A**：
1. 检查显卡驱动
2. 以管理员身份运行
3. 删除Trae配置文件夹，重新打开

### Q14：Trae模型加载失败
**A**：
1. 检查网络
2. 重新登录
3. 切换模型

### Q15：Trae Builder生成的项目跑不起来
**A**：
1. 看终端错误信息，复制给Trae Chat修复
2. 检查依赖是否安装（`pip install -r requirements.txt`）
3. 检查Python版本是否3.10+

---

## 四、通用问题

### Q16：Windows和Mac操作有什么不同？
**A**：
- 终端：Windows用`cmd`或`PowerShell`，Mac用`Terminal`
- 命令：大部分命令相同，但`python`在Mac上可能需要用`python3`
- 路径：Windows用`\`，Mac用`/`
- 安装：Windows用`.exe`安装包，Mac用`.dmg`或`homebrew`

### Q17：电脑配置不够怎么办？
**A**：AI编程工具对配置要求不高：
- 最低8GB内存，推荐16GB
- 不需要独立显卡
- 不需要强大的CPU
- 因为AI计算在云端，不在你电脑上

### Q18：可以两个工具都装吗？
**A**：完全可以。Cursor和Trae不冲突，可以同时安装。推荐工作流：Trae Builder建项目骨架 → Cursor精调细节。

### Q19：安装失败多次，想放弃怎么办？
**A**：安装确实是编程中最容易卡住的环节。如果反复失败：
1. 截图错误信息，用手机发到Cursor Chat或ChatGPT
2. 搜索"xxx安装失败"（百度/Google）
3. 找懂电脑的朋友帮忙
4. 不要放弃！安装成功之后，后面的路就好走了

### Q20：所有工具都装好了，下一步做什么？
**A**：打开第00章，从"这本书在讲什么"开始读。如果已经读过第00章，直接跳到第09章（Prompt Engineering），开始你的AI编程之旅！

---

> **最后提醒**：如果以上方案都无法解决你的问题，把错误信息复制给AI（ChatGPT/Claude/Cursor Chat），AI会帮你分析并提供解决方案。这就是AI编程的精髓——遇到问题，不要自己瞎猜，让AI帮你！