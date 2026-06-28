# Ch04 · Python 与 NumPy 环境搭建

> 所属篇：第零篇 · 预计耗时：15 分钟

工欲善其事必先利其器。后面 40 章的代码都要跑在这个环境上。15 分钟搭好，受益 40 小时。这一章不教 Python 语法（假设你会任意一门编程语言），只教你把"Python + NumPy + Matplotlib + PyTorch + Jupyter"这套深度学习标配环境装好，并验证每个都能跑。

---

## 为了什么（Why）

**核心痛点**：没有环境，后面所有代码都跑不了；NumPy 操作不熟，看代码像看天书。

举个反例：Ch38 实战章节会用 PyTorch 训练一个真正的 Transformer。如果你没装 PyTorch，或者装错了 GPU 版却没 CUDA，代码一跑就报错，你连"是代码错了还是环境错了"都分不清，挫败感直接劝退。

**这一章的目标**：把环境装好、装对、验证通过，让后面 40 章的代码都能直接跑。

## 要做到（Goal）

- **输入**：一台装了 Windows / Mac / Linux 的电脑，能上网。
- **输出**：Python 3.10+、NumPy、Matplotlib、PyTorch、Jupyter 全部可用。
- **成功标准**：运行 `python -c "import torch; print(torch.__version__)"` 输出版本号（如 `2.0.1`）。

## 做了什么（What）

> **本节精简**：环境搭建没有技术结构可拆，只列清单。

### 环境清单

| 工具 | 版本要求 | 用途 |
|------|----------|------|
| Python | 3.10+ | 主语言 |
| NumPy | 1.24+ | 矩阵运算（Ch01-Ch36 大量使用） |
| Matplotlib | 3.7+ | 画图（画 loss 曲线、可视化） |
| PyTorch | 2.0+ | 深度学习框架（Ch37+ 实战使用） |
| Jupyter Notebook | 任意 | 交互式编程（探索性分析） |

## 怎么算（How）

> **本节精简**：环境搭建无公式，只讲版本兼容性。

**版本兼容性说明**：
- PyTorch 2.0+ 官方支持 Python 3.8-3.11。建议用 Python 3.10 或 3.11，兼容性最好。
- Python 3.12 较新，部分包可能还没适配，新手不建议用。
- Mac M1/M2 芯片用 `arm64` 版 PyTorch，安装命令与 Intel 版不同。

## 怎么用（Use）

### 第 1 步：安装 Python 3.10+

#### Windows

去 [python.org](https://www.python.org/downloads/) 下载 3.10 或 3.11 安装包。**安装时务必勾选 "Add Python to PATH"**，否则命令行找不到 `python`。

验证（打开 PowerShell）：
```powershell
python --version
# 输出 Python 3.10.x 或 3.11.x 即成功
```

#### Mac

Mac 自带 Python 2，但版本太旧。推荐用 [Homebrew](https://brew.sh/) 装：
```bash
# 先装 Homebrew（如果没装）
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 装 Python 3.10
brew install python@3.10

# 验证
python3.10 --version
```

#### Linux（Ubuntu/Debian）

```bash
sudo apt update
sudo apt install python3.10 python3.10-venv python3-pip

# 验证
python3.10 --version
```

### 第 2 步：创建虚拟环境（强烈推荐）

虚拟环境隔离不同项目的依赖，避免"装了 A 包把 B 包搞坏"的灾难。

#### 三平台通用

```bash
# 在项目根目录执行
python -m venv .venv            # Windows 用 python，Mac/Linux 用 python3

# 激活虚拟环境
# Windows (PowerShell):
.venv\Scripts\Activate.ps1
# Mac/Linux:
source .venv/bin/activate

# 激活成功后，命令行前面会出现 (.venv) 字样
# 验证
python --version
which python    # Mac/Linux，应指向 .venv/bin/python
```

> **易错点**：Windows PowerShell 执行脚本可能被策略阻止，报 "无法加载文件...因为在此系统上禁止运行脚本"。解决：以管理员身份运行 PowerShell，执行 `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser`，选 Y。

### 第 3 步：安装 NumPy / Matplotlib / Jupyter

三平台通用（确保已激活虚拟环境）：

```bash
# 升级 pip（避免老版本 pip 装新包报错）
python -m pip install --upgrade pip

# 装 NumPy、Matplotlib、Jupyter
pip install numpy matplotlib jupyter
```

**验证 NumPy 安装成功**（这一步必须做，模拟读者反馈的轻微缺口）：

```bash
python -c "import numpy as np; print('numpy', np.__version__); print(np.array([1,2,3]).sum())"
```

预期输出：
```
numpy 1.26.x
6
```

如果报 `ModuleNotFoundError: No module named 'numpy'`，说明你没激活虚拟环境，或者装到了别的 Python 里。回到第 2 步重新激活。

### 第 4 步：安装 PyTorch

PyTorch 分 CPU 版和 GPU 版。**新手强烈建议先装 CPU 版**，简单可靠，跑通教程所有代码足够了。等熟练后再折腾 GPU 版。

#### CPU 版（三平台通用）

```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
```

#### GPU 版（仅 Windows/Linux + NVIDIA 显卡）

先确认你有 NVIDIA 显卡且装了 CUDA：
```bash
nvidia-smi    # 能输出显卡信息说明有 CUDA
```

然后装 GPU 版（以 CUDA 11.8 为例）：
```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

#### Mac M1/M2 版

M 系列芯片用 MPS 加速，安装命令：
```bash
pip install torch torchvision
```

### 第 5 步：一键验证所有环境

把下面这条命令复制到命令行运行：

```bash
python -c "import numpy, matplotlib, torch; print('numpy', numpy.__version__); print('matplotlib', matplotlib.__version__); print('torch', torch.__version__); print('env ok')"
```

预期输出（版本号可能不同）：
```
numpy 1.26.4
matplotlib 3.8.0
torch 2.1.0
env ok
```

看到 `env ok` 就说明环境全部装好了。

### 第 6 步：NumPy 速查表

代码文件：`深度学习从0到Transformer教程/code/ch04_numpy_cheatsheet.py`

这份速查表覆盖了后面所有章节会用到的 NumPy 操作：创建数组、索引切片、形状操作、矩阵乘法、广播、随机数、拼接拆分。**强烈建议跑一遍**，对照输出理解每个操作。

关键片段：

```python
import numpy as np

# 创建数组
a = np.zeros((2, 3))         # 全 0 矩阵
b = np.random.randn(2, 3)    # 标准正态分布
c = np.arange(0, 10, 2)      # [0 2 4 6 8]

# 矩阵乘法
A = np.array([[1, 2], [3, 4]])
B = np.array([[5, 6], [7, 8]])
print(A @ B)                 # [[19 22] [43 50]]

# 广播：列向量加到矩阵每列
M = np.array([[1, 2, 3], [4, 5, 6]])
v = np.array([[100], [200]]) # shape (2, 1)
print(M + v)                 # 每行加对应值
```

运行验证：

```bash
cd 深度学习从0到Transformer教程/code
python ch04_numpy_cheatsheet.py
```

> 📊 完整代码见 [code/ch04_numpy_cheatsheet.py](code/ch04_numpy_cheatsheet.py)

## 想多一点

> 为什么深度学习用 Python 而不是 C++？C++ 明明快得多。
>
> 提示：Python 是"胶水语言"——控制流程、写模型结构、调参，这些用 Python 写又快又清晰。真正耗时的矩阵运算底层调的是 CUDA/C++ 写的库（cuDNN、MKL）。PyTorch 的 `A @ B` 表面是 Python，底层是高度优化的 C++/CUDA 代码。所以"Python 慢"在深度学习里是个伪命题——慢的部分根本不是 Python 在算。

## 易错点预警

- ❌ Windows 下直接 `pip install torch` 装了 GPU 版但没 CUDA，运行报错 → ✅ 正确：用 `--index-url https://download.pytorch.org/whl/cpu` 显式装 CPU 版。新手先用 CPU 版，跑通教程完全够用。
- ❌ NumPy 数组 shape 不匹配直接相加报错 → ✅ 正确：理解广播规则——从右往左对齐维度，每个维度要么相同、要么其中一个为 1、要么缺失。拿不准就用 `reshape` 显式对齐维度。
- ❌ 忘记激活虚拟环境，`pip install` 装到了全局 Python → ✅ 正确：每次开新终端先激活虚拟环境，看到命令行前面的 `(.venv)` 再装包。可以用 `which python`（Mac/Linux）或 `where python`（Windows）确认当前用的是哪个 Python。

## 章末小结

| 工具 | 用途 | 易错点 |
|------|------|--------|
| Python 3.10+ | 主语言 | Windows 安装时勾选 "Add to PATH" |
| 虚拟环境 venv | 隔离项目依赖 | 每次开新终端要重新激活 |
| NumPy | 矩阵运算 | shape 不匹配是最常见报错，理解广播规则 |
| Matplotlib | 画图 | 中文显示需设置字体（后面用到再说） |
| PyTorch | 深度学习框架 | CPU 版和 GPU 版安装命令不同，新手用 CPU 版 |
| Jupyter | 交互式编程 | 记得重启内核清状态，避免变量残留 |

---

> **[可暂停点 0/7]** — 第零篇结束，可安全暂停。恢复时验证：`python -c "import numpy, torch, matplotlib; print('env ok')"`
>
> 下一章：[Ch05 · 什么是机器学习](05-什么是机器学习.md)（待写）
