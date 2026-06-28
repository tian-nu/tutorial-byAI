# 附录 B · NumPy / PyTorch 速查

> 所属篇：附录 · 预计耗时：10 分钟（查阅用）

本附录汇总教程中用到的 NumPy 与 PyTorch 核心 API，按功能分类。每条给出 API 名、用途和最小可运行示例。NumPy 用于 Ch01-Ch16 的手写实现，PyTorch 用于 Ch16 之后和实战章节。

---

## 第一部分 · NumPy 速查

> 引入约定：`import numpy as np`

### 1. 创建数组

| API | 用途 | 示例 |
|-----|------|------|
| `np.array(list)` | 从 Python 列表创建 | `np.array([1.0, 2.0, 3.0])` |
| `np.zeros(shape)` | 全 0 数组 | `np.zeros((2, 3))` |
| `np.ones(shape)` | 全 1 数组 | `np.ones((3, 2))` |
| `np.eye(n)` | 单位矩阵 | `np.eye(3)` |
| `np.arange(start, stop, step)` | 等差数列 | `np.arange(0, 1, 0.1)` |
| `np.linspace(a, b, n)` | 等分区间 | `np.linspace(0, 1, 11)` |
| `np.random.randn(*shape)` | 标准正态随机数 | `np.random.randn(2, 3)` |
| `np.random.rand(*shape)` | [0,1) 均匀随机数 | `np.random.rand(4)` |
| `np.random.randint(a, b, size)` | 整数随机数 | `np.random.randint(0, 10, (3,))` |

```python
import numpy as np
x = np.array([[1, 2], [3, 4]])   # shape (2, 2)
print(x.shape, x.dtype)          # (2, 2) int32
```

### 2. 形状操作

| API | 用途 | 示例 |
|-----|------|------|
| `x.shape` | 查看形状 | `x.shape` → `(2, 3)` |
| `x.reshape(newshape)` | 改形状（必要时复制） | `x.reshape(3, 2)` |
| `x.T` | 转置 | `x.T` |
| `x.transpose(ax)` | 指定轴转置 | `x.transpose(1, 0, 2)` |
| `np.concatenate(list, axis)` | 拼接 | `np.concatenate([a, b], axis=0)` |
| `np.stack(list, axis)` | 新增维度堆叠 | `np.stack([a, b], axis=0)` |
| `np.expand_dims(x, axis)` | 插入新轴 | `np.expand_dims(x, 0)` |
| `np.squeeze(x)` | 去掉长度 1 的轴 | `np.squeeze(x)` |

```python
a = np.zeros((2, 3))
print(a.reshape(3, 2).shape)     # (3, 2)
print(a.T.shape)                 # (3, 2)
```

### 3. 运算

| API | 用途 | 示例 |
|-----|------|------|
| `A @ B` | 矩阵乘法 | `A @ B` |
| `A * B` | 逐元素乘（Hadamard） | `A * B` |
| `np.dot(a, b)` | 点积（向量）/ 矩阵乘（矩阵） | `np.dot(a, b)` |
| `x.sum(axis)` | 沿轴求和 | `x.sum(axis=0)` |
| `x.mean(axis)` | 沿轴求均值 | `x.mean(axis=1)` |
| `x.max(axis)` / `x.argmax(axis)` | 最大值 / 下标 | `x.argmax(axis=-1)` |
| `np.exp(x)` / `np.log(x)` | 指数 / 对数 | `np.exp(x)` |
| `np.sqrt(x)` | 开方 | `np.sqrt(d_k)` |
| `np.maximum(a, b)` | 逐元素取大（ReLU 用） | `np.maximum(0, x)` |
| `np.where(cond, a, b)` | 条件选择 | `np.where(x>0, x, 0.01*x)` |

```python
scores = np.array([1.0, 2.0, 3.0])
scores -= scores.max()                 # 数值稳定
exp = np.exp(scores)
prob = exp / exp.sum()                 # softmax
```

### 4. 索引与切片

| API | 用途 | 示例 |
|-----|------|------|
| `x[i, j]` | 单元素 | `x[0, 1]` |
| `x[i, :]` | 取一行 | `x[0, :]` |
| `x[:, j]` | 取一列 | `x[:, 1]` |
| `x[mask]` | 布尔索引 | `x[x > 0]` |
| `x[fancy]` | 花式索引 | `x[[0, 2, 4]]` |
| `x[i:j:k]` | 切片带步长 | `x[::2]` |

```python
x = np.arange(10)
print(x[2:5])        # [2 3 4]
print(x[x % 2 == 0]) # [0 2 4 6 8]
```

### 5. 线性代数（`np.linalg`）

| API | 用途 | 示例 |
|-----|------|------|
| `np.linalg.inv(A)` | 矩阵逆 | `A_inv = np.linalg.inv(A)` |
| `np.linalg.solve(A, b)` | 解线性方程 Ax=b | `x = np.linalg.solve(A, b)` |
| `np.linalg.norm(x)` | 范数 | `np.linalg.norm(grad)` |
| `np.linalg.eig(A)` | 特征值分解 | `w, V = np.linalg.eig(A)` |

---

## 第二部分 · PyTorch 速查

> 引入约定：`import torch; import torch.nn as nn; import torch.nn.functional as F`

### 1. 张量创建与基础

| API | 用途 | 示例 |
|-----|------|------|
| `torch.tensor(data)` | 从数据创建 | `torch.tensor([1.0, 2.0])` |
| `torch.zeros(shape)` / `torch.ones(shape)` | 全 0 / 全 1 | `torch.zeros(3, 4)` |
| `torch.randn(shape)` | 标准正态 | `torch.randn(2, 3)` |
| `torch.arange(a, b, step)` | 等差数列 | `torch.arange(0, 10)` |
| `torch.eye(n)` | 单位矩阵 | `torch.eye(3)` |
| `x.to(device)` | 移到 GPU/CPU | `x.to('cuda')` |
| `x.dtype` / `x.device` | 数据类型 / 设备 | `x.dtype` |

```python
import torch
x = torch.randn(2, 3)
print(x.shape, x.dtype)         # torch.Size([2, 3]) torch.float32
```

### 2. 形状与运算

| API | 用途 | 示例 |
|-----|------|------|
| `x.shape` / `x.size()` | 查看形状 | `x.size()` |
| `x.view(shape)` | 改形状（要求连续） | `x.view(3, 2)` |
| `x.reshape(shape)` | 改形状（自动处理非连续） | `x.reshape(3, 2)` |
| `x.transpose(dim0, dim1)` | 交换两轴 | `x.transpose(0, 1)` |
| `x.permute(*dims)` | 重排所有轴 | `x.permute(2, 0, 1)` |
| `x.unsqueeze(dim)` | 插入长度 1 轴 | `x.unsqueeze(0)` |
| `x.squeeze(dim)` | 去掉长度 1 轴 | `x.squeeze(0)` |
| `torch.cat(list, dim)` | 拼接 | `torch.cat([a, b], dim=0)` |
| `torch.stack(list, dim)` | 新轴堆叠 | `torch.stack([a, b], dim=0)` |
| `x @ y` | 矩阵乘法 | `Q @ K.transpose(-2, -1)` |
| `x * y` | 逐元素乘 | `gate * candidate` |
| `x.sum(dim)` / `x.mean(dim)` | 沿轴求和/均值 | `x.sum(dim=-1)` |
| `x.softmax(dim)` | softmax | `scores.softmax(dim=-1)` |
| `torch.exp(x)` / `torch.log(x)` | 指数/对数 | `torch.exp(x)` |
| `torch.matmul(a, b)` | 批量矩阵乘 | `torch.matmul(Q, K.transpose(-2,-1))` |
| `x.norm(dim)` | 范数 | `grad.norm()` |

```python
import torch
x = torch.randn(4, 8)
y = x.view(2, 16)               # 改形状
z = x.unsqueeze(0)              # (1, 4, 8)
```

### 3. 神经网络模块（`torch.nn`）

| API | 用途 | 示例 |
|-----|------|------|
| `nn.Linear(in, out)` | 全连接层 | `nn.Linear(768, 10)` |
| `nn.Embedding(num, dim)` | 嵌入层 | `nn.Embedding(vocab_size, 512)` |
| `nn.Dropout(p)` | 随机丢弃 | `nn.Dropout(0.1)` |
| `nn.LayerNorm(d)` | 层归一化 | `nn.LayerNorm(512)` |
| `nn.BatchNorm1d(d)` | 批归一化 | `nn.BatchNorm1d(128)` |
| `nn.ReLU()` / `nn.GELU()` / `nn.Tanh()` | 激活函数 | `nn.GELU()` |
| `nn.Sigmoid()` | sigmoid | `nn.Sigmoid()` |
| `nn.Softmax(dim)` | softmax 模块 | `nn.Softmax(dim=-1)` |
| `nn.Conv2d(in, out, k)` | 2D 卷积 | `nn.Conv2d(3, 16, 3, padding=1)` |
| `nn.MaxPool2d(k)` | 2D 最大池化 | `nn.MaxPool2d(2)` |
| `nn.RNN(in, hidden)` | RNN 层 | `nn.RNN(64, 128, batch_first=True)` |
| `nn.LSTM(in, hidden)` | LSTM 层 | `nn.LSTM(64, 128, batch_first=True)` |
| `nn.GRU(in, hidden)` | GRU 层 | `nn.GRU(64, 128)` |
| `nn.MultiheadAttention(d, h)` | 多头注意力 | `nn.MultiheadAttention(512, 8)` |
| `nn.TransformerEncoderLayer(d, h, ff)` | Encoder 块 | `nn.TransformerEncoderLayer(512, 8, 2048)` |
| `nn.TransformerDecoderLayer(d, h, ff)` | Decoder 块 | `nn.TransformerDecoderLayer(512, 8, 2048)` |
| `nn.ModuleList([...])` | 模块列表（用于循环） | `nn.ModuleList([block(...) for _ in range(6)])` |
| `nn.Sequential(...)` | 顺序容器 | `nn.Sequential(nn.Linear(10,5), nn.ReLU())` |

```python
import torch.nn as nn
class MLP(nn.Module):
    def __init__(self):
        super().__init__()
        self.fc1 = nn.Linear(784, 128)
        self.fc2 = nn.Linear(128, 10)
        self.act = nn.ReLU()
    def forward(self, x):
        return self.fc2(self.act(self.fc1(x)))
```

### 4. 损失函数（`torch.nn`）

| API | 用途 | 示例 |
|-----|------|------|
| `nn.MSELoss()` | 均方误差（回归） | `loss = nn.MSELoss()(y_pred, y)` |
| `nn.CrossEntropyLoss()` | 交叉熵（多分类，自带 softmax） | `loss = nn.CrossEntropyLoss()(logits, y)` |
| `nn.BCELoss()` | 二元交叉熵（输入概率） | `loss = nn.BCELoss()(prob, y)` |
| `nn.BCEWithLogitsLoss()` | 二元交叉熵（输入 logits，更稳） | `loss = nn.BCEWithLogitsLoss()(logit, y)` |
| `nn.NLLLoss()` | 负对数似然（配合 log_softmax） | `loss = nn.NLLLoss()(logp, y)` |

> ⚠️ `CrossEntropyLoss` 期望输入是 **logits**（未过 softmax），且标签是**整数类索引**而非 one-hot。详见 Ch35 易错点。

### 5. 优化器与调度器（`torch.optim`）

| API | 用途 | 示例 |
|-----|------|------|
| `optim.SGD(params, lr, momentum)` | 随机梯度下降 | `optim.SGD(model.parameters(), lr=0.01, momentum=0.9)` |
| `optim.Adam(params, lr)` | Adam | `optim.Adam(model.parameters(), lr=1e-4)` |
| `optim.AdamW(params, lr, weight_decay)` | 带 decoupled 权重衰减的 Adam | `optim.AdamW(model.parameters(), lr=5e-5, weight_decay=0.01)` |
| `optim.lr_scheduler.StepLR(opt, step, gamma)` | 阶梯衰减 | `StepLR(opt, step_size=10, gamma=0.1)` |
| `optim.lr_scheduler.CosineAnnealingLR(opt, T_max)` | 余弦衰减 | `CosineAnnealingLR(opt, T_max=50)` |
| `optim.lr_scheduler.LambdaLR(opt, fn)` | 自定义（Warmup 用） | `LambdaLR(opt, lambda step: warmup_fn(step))` |
| `torch.nn.utils.clip_grad_norm_(model, max_norm)` | 梯度裁剪 | `clip_grad_norm_(model.parameters(), 1.0)` |

```python
from torch import optim
opt = optim.AdamW(model.parameters(), lr=5e-5, weight_decay=0.01)
sched = optim.lr_scheduler.CosineAnnealingLR(opt, T_max=10)
```

### 6. 训练工具

| API | 用途 | 示例 |
|-----|------|------|
| `DataLoader(dataset, batch_size, shuffle)` | 批迭代器 | `DataLoader(ds, batch_size=32, shuffle=True)` |
| `Dataset`（自定义） | 数据集抽象 | 继承实现 `__len__` 和 `__getitem__` |
| `model.train()` / `model.eval()` | 切训练/评估模式（影响 Dropout/BN） | `model.eval()` |
| `with torch.no_grad():` | 关闭梯度（推理/评估用） | `with torch.no_grad(): out = model(x)` |
| `loss.backward()` | 反向传播 | `loss.backward()` |
| `opt.step()` | 更新参数 | `opt.step()` |
| `opt.zero_grad()` | 清零梯度 | `opt.zero_grad()` |
| `x.requires_grad_(True)` | 标记需要梯度 | `x.requires_grad_(True)` |
| `x.detach()` | 脱离计算图 | `value = loss.detach().item()` |
| `x.item()` | 取标量值 | `loss.item()` |

### 7. 标准训练循环模板

```python
import torch
from torch import optim
from torch.utils.data import DataLoader

model = MyModel().to(device)
opt = optim.AdamW(model.parameters(), lr=1e-4)
loss_fn = torch.nn.CrossEntropyLoss(ignore_index=0)

for epoch in range(num_epochs):
    model.train()
    for x, y in DataLoader(train_ds, batch_size=32, shuffle=True):
        x, y = x.to(device), y.to(device)
        logits = model(x)
        loss = loss_fn(logits, y)
        opt.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        opt.step()
    # 评估
    model.eval()
    with torch.no_grad():
        # 验证逻辑
        pass
```

### 8. 模型保存与加载

| API | 用途 | 示例 |
|-----|------|------|
| `torch.save(obj, path)` | 保存（模型/dict/任意） | `torch.save(model.state_dict(), 'm.pt')` |
| `torch.load(path)` | 加载 | `state = torch.load('m.pt')` |
| `model.state_dict()` | 取参数字典 | `sd = model.state_dict()` |
| `model.load_state_dict(sd)` | 加载参数字典 | `model.load_state_dict(sd)` |

```python
torch.save(model.state_dict(), 'model.pt')
model.load_state_dict(torch.load('model.pt'))
```

### 9. 常用工具函数

| API | 用途 | 示例 |
|-----|------|------|
| `torch.cuda.is_available()` | 检测 GPU | `device = 'cuda' if torch.cuda.is_available() else 'cpu'` |
| `torch.tril(torch.ones(n,n))` | 下三角矩阵（Causal Mask 用） | `mask = torch.tril(torch.ones(T,T))` |
| `torch masked_fill(mask, val)` | 按掩码填充 | `scores.masked_fill(mask==0, float('-inf'))` |
| `F.softmax(x, dim)` | 函数式 softmax | `F.softmax(scores, dim=-1)` |
| `F.cross_entropy(logits, y)` | 函数式交叉熵 | `F.cross_entropy(logits, y)` |
| `F.relu(x)` / `F.gelu(x)` | 函数式激活 | `F.gelu(x)` |
| `torch.bmm(Q, K.transpose(1,2))` | 批量矩阵乘（仅 3D） | `torch.bmm(Q, K.transpose(1, 2))` |

---

## 三、NumPy ↔ PyTorch 互转

| 操作 | 代码 |
|------|------|
| NumPy → Torch | `t = torch.from_numpy(np_array)` |
| Torch → NumPy | `arr = t.detach().cpu().numpy()` |
| 共享内存（同 CPU） | 默认共享，改一个另一个也变 |
| 跨设备转换 | `t = torch.from_numpy(arr).to('cuda')` |

```python
import numpy as np, torch
arr = np.array([1.0, 2.0, 3.0])
t = torch.from_numpy(arr)        # 共享内存
arr[0] = 99
print(t)                         # tensor([99., 2., 3.])
```

---

## 四、易混 API 对照

| NumPy | PyTorch | 区别 |
|-------|---------|------|
| `x.reshape(...)` | `x.view(...)` / `x.reshape(...)` | `view` 要求连续，`reshape` 自动处理 |
| `np.dot(a, b)` | `torch.matmul(a, b)` / `a @ b` | PyTorch 用 `@` 更直观 |
| `x.sum(axis=0)` | `x.sum(dim=0)` | 关键字不同：`axis` vs `dim` |
| `np.maximum(0, x)` | `torch.clamp(x, min=0)` 或 `F.relu(x)` | PyTorch 用 `clamp` |
| `np.expand_dims(x, 0)` | `x.unsqueeze(0)` | 名称不同 |
| `np.concatenate` | `torch.cat` | 名称不同 |
| `np.linalg.norm` | `x.norm()` | 方法不同 |

---

> 上一附录：[附录 A · 数学符号速查](附录A-数学符号速查.md)  ｜  下一附录：[附录 C · 常见错误与排错指南](附录C-常见错误与排错指南.md)
