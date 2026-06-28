# Ch32 · Layer Normalization 与残差连接

> 所属篇：第五篇 · 预计耗时：20 分钟

深层网络有个老大难：层数越多，梯度越不稳，要么爆炸要么消失。Transformer 一上来就堆 6 到 12 层，要是没有保护措施，底层参数根本学不动。这一章请出两位救星——**Layer Norm** 让每层输出的"刻度"稳定，**残差连接** 给梯度修一条"高速公路"直通底层。两个加起来，深层 Transformer 才训得动。

---

## 为了什么（Why）

**核心痛点**：Transformer 堆叠 6 到 12 层，没有残差连接，底层梯度会消失；没有 Layer Norm，各层输出尺度不一，训练会抖到 NaN。

举个反例：你照着原始论文写一个 12 层 Transformer，故意把残差连接和 Layer Norm 都删掉，跑一步反向传播，大概率看到 loss 直接变 `nan`。原因有两个：

- **梯度消失**：每经过一个子层，梯度要乘以该层的雅可比。层数一多，连乘下来梯度指数级缩水，底层参数等于没更新。
- **分布漂移**：每层输出尺度不一样，有的层输出 0.01 量级，有的层输出 100 量级。softmax 一遇到大数就饱和，梯度归零。

**这一章的目标**：搞懂 Layer Norm 的公式和残差连接的作用，能用 PyTorch 把"子层 + 残差 + LN"组装成一块砖，后面 Ch33、Ch34 直接拿这块砖砌墙。

## 要做到（Goal）

- **输入**：Ch29-31 的 Attention 模块（你已经会算多头注意力了）。
- **输出**：理解 LN 公式和残差连接的作用，能用 PyTorch 组装"Attention + 残差 + LN"。
- **成功标准**：给定 `x = [1.0, 2.0, 3.0]`，能手算出 LN 后的值（≈ `[-1.225, 0, 1.225]`）。

## 做了什么（What）

Transformer 每个子层的外壳都是同一种套路：

```
x ──┬──> SubLayer(x) ──> + ──> LayerNorm ──> 输出
    │                       ▲
    └───────────────────────┘
         残差连接（高速公路）
```

两个组件分别解释：

### 逐组件拆解

**Layer Normalization（LN）**：对**单个样本的特征维**做归一化。给它一个学生的"语数英物"四科成绩 `[90, 60, 80, 70]`，它算这四科的均值和方差，然后把每科成绩标准化成"离均值几个标准差"。LN 不关心其他学生，只看这一个样本内部。

**残差连接（Residual Connection）**：把输入 `x` 直接加到子层输出上，`y = SubLayer(x) + x`。意义在于：反向传播时，梯度可以从 `+x` 这条路直接绕过 SubLayer，等于给梯度修了一条"高速公路"，不会因子层的雅可比连乘而消失。

**Post-LN（原始论文）**：先做残差再 LN，`y = LN(SubLayer(x) + x)`。原始 Transformer 用的就是这个。

**Pre-LN（改进版）**：先 LN 再做子层，`y = SubLayer(LN(x)) + x`。训练更稳，不用 warmup 也不会炸，现在大多数实现用这个。

## 怎么算（How）

### 1. Layer Norm 公式

```
LN(x) = γ · (x - μ) / √(σ² + ε) + β
```

其中：
- `μ = mean(x)`：x 的均值（沿特征维算）
- `σ² = var(x)`：x 的方差（沿特征维算）
- `ε`：一个小常数（如 1e-5），防止除以 0
- `γ`、`β`：可学习参数，分别缩放和偏移（默认 γ=1, β=0）

### 2. 数值小例子（逐步展开）

设 `x = [1.0, 2.0, 3.0]`，`ε = 1e-5`，`γ = 1`，`β = 0`。

**第 1 步：算均值 μ**

```
μ = (1.0 + 2.0 + 3.0) / 3 = 6.0 / 3 = 2.0
```

**第 2 步：算方差 σ²**（用总体方差，除以 N 而不是 N-1）

```
σ² = ((1.0-2.0)² + (2.0-2.0)² + (3.0-2.0)²) / 3
   = (1 + 0 + 1) / 3
   = 0.6667
```

**第 3 步：算 √(σ² + ε)**

```
σ² + ε = 0.6667 + 0.00001 ≈ 0.6667
√0.6667 ≈ 0.8165
```

**第 4 步：算 (x - μ) / √(σ² + ε)**

```
(1.0 - 2.0) / 0.8165 = -1.0 / 0.8165 ≈ -1.2247
(2.0 - 2.0) / 0.8165 = 0 / 0.8165    = 0
(3.0 - 2.0) / 0.8165 = 1.0 / 0.8165  ≈ 1.2247
```

得到 `[-1.2247, 0, 1.2247]`。

**第 5 步：乘 γ 加 β**（这里 γ=1, β=0，所以不变）

```
LN(x) = 1 · [-1.2247, 0, 1.2247] + 0 = [-1.2247, 0, 1.2247]
```

四舍五入就是 `[-1.225, 0, 1.225]` ✅ 与目标对上。

**验证**：LN 后的均值确实接近 0，方差接近 1。

### 3. 残差连接公式

```
y = SubLayer(x) + x
```

只有一条硬约束：`SubLayer(x)` 的输出形状必须和 `x` 一样，否则没法逐元素相加。Transformer 里所有子层都满足这点（Attention 输出 `(B, T, d_model)`，FFN 输出也是 `(B, T, d_model)`）。

### 4. Post-LN vs Pre-LN

| 变体 | 公式 | 特点 |
|------|------|------|
| Post-LN | `LN(SubLayer(x) + x)` | 原始论文，需要 warmup，否则训练不稳 |
| Pre-LN | `SubLayer(LN(x)) + x` | 训练更稳，主流量化/GPT 风格模型常用 |

直觉：Pre-LN 把 LN 放在子层之前，保证进入子层的输入总是标准化过的，尺度可控；而 Post-LN 把 LN 放在最后，子层内部要自己处理未归一化的输入，容易出大数。

## 怎么用（Use）

代码文件：`深度学习从0到Transformer教程/code/ch32_layer_norm_residual.py`

关键片段：

```python
import torch
import torch.nn as nn

# LayerNorm
ln = nn.LayerNorm(4)
x = torch.tensor([[1.0, 2.0, 3.0, 4.0]])
print(ln(x))  # 约 [-1.34, -0.45, 0.45, 1.34]

# 残差 + LN 子层壳（Pre-LN 风格）
class ResidualSubLayer(nn.Module):
    def __init__(self, d_model, dropout=0.1):
        super().__init__()
        self.ln = nn.LayerNorm(d_model)
        self.dropout = nn.Dropout(dropout)

    def forward(self, x, sublayer):
        # Pre-LN: 先 LN 再子层，再加残差
        return x + self.dropout(sublayer(self.ln(x)))
```

运行验证：

```bash
cd 深度学习从0到Transformer教程/code
python ch32_layer_norm_residual.py
```

预期输出（节选）：
```
=== Ch32: LayerNorm 与残差连接 ===

--- 手算 LN 验证 ---
输入 x = [1. 2. 3.]
μ = 2.0000, σ² = 0.6667, √(σ²+ε) = 0.8165
LN(x) = [-1.2247  0.      1.2247]
nn.LayerNorm 输出 = [-1.2247  0.      1.2247]
✅ 手算与 PyTorch 一致

--- 残差连接验证 ---
SubLayer 输出 shape = (2, 5, 8), 与输入相同 ✅
残差后输出均值 ≈ 0（含 LN 时）
```

> 📊 完整代码见 [code/ch32_layer_norm_residual.py](code/ch32_layer_norm_residual.py)

## 想多一点

> **Layer Norm 和 Batch Norm 有什么区别？**
>
> 这是面试高频题，也是很多人用混的源头。
>
> **Batch Norm（BN）**：对一个 batch 内的**同一特征**做归一化。比喻：一个班 30 个学生，对"数学成绩"这一列算均值方差，把所有学生的数学成绩标准化。BN 依赖 batch size，batch 太小统计量不准；测试时还得保存训练时的 running mean/var，工程复杂。
>
> **Layer Norm（LN）**：对**一个样本的所有特征**做归一化。比喻：看一个学生的"语数英物"四科成绩，算这四科的均值方差，把这个学生的四科成绩标准化。LN 完全在样本内部算，跟 batch size 无关，所以特别适合序列模型（序列长度可变、batch 可能只有 1）。
>
> **为什么 Transformer 用 LN 而不是 BN**：
> - 序列长度可变，BN 没法处理变长 batch
> - 推理时 batch size 经常是 1（生成式），BN 直接失效
> - LN 对每个 token 独立归一化，符合"每个位置独立处理"的设定
>
> 一句话：**BN 看一列（跨样本），LN 看一行（跨特征）**。

## 易错点预警

- ❌ 错误：把 Layer Norm 当 Batch Norm 用，以为 `nn.LayerNorm(d_model)` 是对 batch 归一化 → ✅ 正确：`nn.LayerNorm(d_model)` 归一化的是最后一维 `d_model`，即特征维。对 `(B, T, d_model)` 的输入，它在 `d_model` 这一维上算均值方差，B 和 T 都不参与。
- ❌ 错误：残差连接维度不匹配，`SubLayer(x)` 输出 `(B, T, 256)` 却要加到 `x` 形状 `(B, T, 512)` 上 → ✅ 正确：SubLayer 输出必须和 x 同维。如果非要变维，得加一个投影 `Linear(d_in, d_out)` 把 x 投影到同维再加，但 Transformer 内部不会这么做，所有子层都保持 `d_model` 不变。
- ❌ 错误：把 Pre-LN 写成 `LN(x + SubLayer(x))` 还自称 Pre-LN → ✅ 正确：Pre-LN 是 `x + SubLayer(LN(x))`，LN 在子层**之前**；`LN(x + SubLayer(x))` 是 Post-LN，两者完全相反。

## 章末小结

| 组件 | 公式 | 作用 |
|------|------|------|
| Layer Norm | `γ·(x-μ)/√(σ²+ε)+β` | 稳定每层输出分布（沿特征维） |
| 残差连接 | `y = SubLayer(x) + x` | 梯度高速公路，防消失 |
| Post-LN | `LN(SubLayer(x)+x)` | 原始 Transformer，需 warmup |
| Pre-LN | `SubLayer(LN(x))+x` | 训练更稳，现代常用 |
| Batch Norm（对比） | 跨 batch 归一化同一特征 | 适合 CV，不适合变长序列 |

---

> 下一章：[Ch33 · 前馈网络与完整 Encoder 块](33-前馈网络与完整Encoder块.md)
