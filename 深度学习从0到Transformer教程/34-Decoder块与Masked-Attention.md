# Ch34 · Decoder 块与 Masked Attention

> 所属篇：第五篇 · 预计耗时：30 分钟

Encoder 看整句话，Decoder 要一个词一个词生成。生成第 3 个词时，模型绝对不能偷看第 4 个词——否则训练时抄答案、推理时崩盘。这就是 **Masked Attention** 的活：给未来位置贴上"封条"，只让看过去。本章把 Decoder 块拼出来，讲清楚 mask 怎么造、Cross-Attention 怎么接 Encoder。

---

## 为了什么（Why）

**核心痛点**：训练时 Decoder 一次性接收整个目标序列（并行加速），但推理时只能一个词一个词生成（看不到未来）。如果不遮盖未来位置，训练时模型会"作弊"直接抄答案，loss 看着很低；一上线推理，发现根本看不到未来，性能直接崩。

举个反例：你训练一个中英翻译 Decoder，目标句是 "I love deep learning"。训练时把整句喂进去，没加 mask。模型发现"预测 love 时只要看一眼 deep 就知道答案了"，于是学到一个抄未来词的策略。训练 loss 0.1，看起来很美。上线推理时，"I love" 后面要预测什么？模型还是去"看未来"，可未来根本没生成，直接报错或乱输出。

**这一章的目标**：搞懂 Masked Self-Attention 和 Cross-Attention，能用 PyTorch 组装 Decoder 块。

## 要做到（Goal）

- **输入**：Ch33 的 Encoder 块。
- **输出**：理解 Masked Attention 和 Cross-Attention，能用 PyTorch 组装 Decoder 块。
- **成功标准**：给定 3×3 的 attention 矩阵，能应用下三角 mask 算出结果。

## 做了什么（What）

Decoder 块比 Encoder 块多一个子层，共三个：

```
            ┌──────────────────────────────────────────┐
            │  子层1: Masked Self-Attention             │
            │   x ──> MaskedMHA(x) ──+──> LN ──> z1     │
            │   └───────────────────┘（残差）          │
            ├──────────────────────────────────────────┤
            │  子层2: Cross-Attention（看 Encoder）     │
            │   z1 ─> CrossAttn(Q=z1, K=V=enc) ─+─> LN │
            │                                    │      │
            ├──────────────────────────────────────────┤
            │  子层3: Feed-Forward Network             │
            │   z2 ──> FFN(z2) ──+──> LN ──> out       │
            │   └───────────────┘（残差）              │
            └──────────────────────────────────────────┘
```

### 逐组件拆解

**Masked Self-Attention**：和普通 Self-Attention 一样，只是给 score 矩阵加一个**因果 mask**——上三角（未来位置）填 `-inf`，下三角（过去和现在）填 0。softmax 后未来位置权重严格为 0，模型只能看当前及之前的词。

**Cross-Attention（交叉注意力）**：Q 来自 Decoder，K 和 V 来自 Encoder 输出。Decoder 用自己的"问题"去 Encoder 的"答案库"里检索相关信息。这一步是 Encoder 和 Decoder 之间唯一的桥梁。

**FFN**：和 Encoder 完全一样，逐位置两层 MLP。

**Causal Mask（因果掩码）**：一个下三角矩阵，形如：

```
[[0,    -inf, -inf, -inf],
 [0,    0,    -inf, -inf],
 [0,    0,    0,    -inf],
 [0,    0,    0,    0   ]]
```

含义：第 1 行（生成第 1 个词时）只能看第 1 个词；第 2 行能看 1、2；第 3 行能看 1、2、3；以此类推。

## 怎么算（How）

### 1. 核心公式

```
# 因果 mask
M[i][j] = 0       if j ≤ i   （能看）
       = -inf    if j > i   （不能看）

# Masked Self-Attention
masked_attn(x) = softmax(QK^T/√d_k + M) · V

# Cross-Attention（K、V 来自 Encoder）
cross_attn(z1, enc) = softmax(Q_dec · K_enc^T / √d_k) · V_enc
  其中 Q_dec = z1 · W_Q,  K_enc = enc · W_K,  V_enc = enc · W_V
```

### 2. 数值小例子（3×3 attention 矩阵 + mask）

设原始 attention scores（已除以 √d_k，3 个 query、3 个 key）：

```
scores = [[1.0, 0.5, 0.3],
          [0.4, 0.8, 0.2],
          [0.6, 0.3, 0.9]]
```

**第 1 步：构造 3×3 因果 mask**

```
M = [[0,    -inf, -inf],
     [0,    0,    -inf],
     [0,    0,    0   ]]
```

**第 2 步：scores + M**

```
masked = [[1.0,  -inf, -inf],
          [0.4,  0.8,  -inf],
          [0.6,  0.3,  0.9]]
```

**第 3 步：逐行 softmax**（`softmax(x)_i = e^x_i / Σ e^x_j`）

**第 1 行** `softmax([1.0, -inf, -inf])`：

- e^1.0 ≈ 2.7183
- e^(-inf) = 0
- e^(-inf) = 0
- 和 = 2.7183
- 结果 = `[2.7183/2.7183, 0, 0] = [1.0, 0, 0]`

含义：生成第 1 个词时，100% 注意力在自己身上（只能看自己）。

**第 2 行** `softmax([0.4, 0.8, -inf])`：

- e^0.4 ≈ 1.4918
- e^0.8 ≈ 2.2255
- e^(-inf) = 0
- 和 = 3.7173
- 结果 = `[1.4918/3.7173, 2.2255/3.7173, 0] = [0.401, 0.599, 0]`

含义：生成第 2 个词时，40.1% 看第 1 个词，59.9% 看第 2 个词，0% 看第 3 个（被封条封住）。

**第 3 行** `softmax([0.6, 0.3, 0.9])`：

- e^0.6 ≈ 1.8221
- e^0.3 ≈ 1.3499
- e^0.9 ≈ 2.4596
- 和 = 5.6316
- 结果 = `[1.8221/5.6316, 1.3499/5.6316, 2.4596/5.6316] = [0.324, 0.240, 0.437]`

含义：生成第 3 个词时，三个词都能看，注意力分配如上。

**完整 masked attention 权重**：

```
[[1.000, 0.000, 0.000],
 [0.401, 0.599, 0.000],
 [0.324, 0.240, 0.437]]
```

注意对角线以上全是 0——未来位置被严格封死。

### 3. Cross-Attention 的 Q/K/V 来源

这是 Decoder 与 Encoder 唯一的"接口"，必须搞清楚：

| 子层 | Q 来源 | K 来源 | V 来源 |
|------|--------|--------|--------|
| Masked Self-Attn | Decoder 输入 | Decoder 输入 | Decoder 输入 |
| Cross-Attn | Decoder 输出（z1） | **Encoder 输出** | **Encoder 输出** |

Cross-Attn 里 Decoder 是"提问者"（Q），Encoder 是"答案库"（K 用于检索、V 用于取内容）。

## 怎么用（Use）

**接口说明（重要）**：Ch30 的 `MultiHeadAttention.forward(x)` 签名需要扩展为 `forward(x, mask=None)`，mask 作为可选参数。本章代码默认 Ch30 已按此签名实现，可直接传 mask。如果你的 Ch30 实现还是老签名，请先在 attention 内部的 score 矩阵上加 mask 再 softmax。

代码文件：`深度学习从0到Transformer教程/code/ch34_decoder_block_mask.py`

关键片段：

```python
import torch
import torch.nn as nn

class DecoderBlock(nn.Module):
    def __init__(self, d_model, n_heads, d_ff, dropout=0.1):
        super().__init__()
        self.self_attn = MultiHeadAttention(d_model, n_heads)   # 来自 Ch30
        self.cross_attn = MultiHeadAttention(d_model, n_heads)  # 来自 Ch30
        self.ff = FeedForward(d_model, d_ff)                    # 来自 Ch33
        self.ln1 = nn.LayerNorm(d_model)
        self.ln2 = nn.LayerNorm(d_model)
        self.ln3 = nn.LayerNorm(d_model)
        self.dropout = nn.Dropout(dropout)

    def forward(self, x, enc_out, tgt_mask=None):
        # 子层1: Masked Self-Attention（mask 传给 self_attn）
        x = self.ln1(x + self.dropout(self.self_attn(x, mask=tgt_mask)))
        # 子层2: Cross-Attention（Q=x, K=V=enc_out，不需要 mask）
        x = self.ln2(x + self.dropout(self.cross_attn(x, enc_out, enc_out)))
        # 子层3: FFN
        x = self.ln3(x + self.dropout(self.ff(x)))
        return x


# 生成下三角因果 mask
T = 5
mask = torch.triu(torch.ones(T, T) * float('-inf'), diagonal=1)
print(mask)
# [[0., -inf, -inf, -inf, -inf],
#  [0., 0., -inf, -inf, -inf],
#  [0., 0., 0., -inf, -inf],
#  [0., 0., 0., 0., -inf],
#  [0., 0., 0., 0., 0.]]
```

运行验证：

```bash
cd 深度学习从0到Transformer教程/code
python ch34_decoder_block_mask.py
```

预期输出（节选）：
```
=== Ch34: Decoder 块与 Masked Attention ===

--- 因果 mask ---
mask = 
[[0., -inf, -inf, -inf, -inf],
 [0., 0., -inf, -inf, -inf],
 [0., 0., 0., -inf, -inf],
 [0., 0., 0., 0., -inf],
 [0., 0., 0., 0., 0.]]

--- 3×3 数值小例子 ---
masked scores = [[1.0, -inf, -inf], [0.4, 0.8, -inf], [0.6, 0.3, 0.9]]
attn weights  = [[1.000, 0.000, 0.000],
                 [0.401, 0.599, 0.000],
                 [0.324, 0.240, 0.437]]
✅ 上三角严格为 0

--- 完整 Decoder 块 ---
输入 x shape = (2, 8, 64)
enc_out shape = (2, 10, 64)
输出 shape = (2, 8, 64) ✅
```

> 📊 完整代码见 [code/ch34_decoder_block_mask.py](code/ch34_decoder_block_mask.py)
> 📊 可视化演示见 [35_transformer_architecture_visual.html](35_transformer_architecture_visual.html)（Decoder 块在完整架构中的位置）

## 想多一点

> **为什么用 `-inf` 而不是 `0` 做 mask？**
>
> 这是高频踩坑点。用 `0` 的话，softmax(0) = e^0 / Σ = 非零值，未来位置仍然有非零权重，等于"封条没贴紧"，信息泄漏。
>
> 用 `-inf` 的话，e^(-inf) = 0，softmax 后未来位置权重**严格为 0**，物理上完全切断。
>
> 工程上 `-inf` 用 `float('-inf')` 表示，PyTorch 的 softmax 会正确处理（不会出 NaN）。如果担心数值问题，可以用 `-1e9` 代替——softmax 后约等于 0，足够安全。
>
> **一句话：mask 的目标是"严格禁止"，不是"减弱"。要禁止就用 `-inf`，要减弱才用小负数。**

## 易错点预警

- ❌ 错误：用 `0` 而非 `-inf` 做 mask → ✅ 正确：必须用 `-inf`（或 `-1e9`），softmax 后才严格为 0。用 0 会让未来位置有非零权重，训练时模型偷看未来。
- ❌ 错误：Cross-Attention 的 K/V 用 Decoder 自己的输出 → ✅ 正确：Cross-Attention 的 K 和 V **必须来自 Encoder 输出**，只有 Q 来自 Decoder。如果 K/V 也用 Decoder，就退化成 Self-Attention，Encoder 的信息根本没传过来。
- ❌ 错误：调用 `self.self_attn(x)` 时没传 mask，或者 mask 形状不对 → ✅ 正确：`self.self_attn(x, mask=tgt_mask)`，mask 形状要能广播到 attention score 矩阵 `(B, n_heads, T, T)`。一般是 `(T, T)` 或 `(B, 1, T, T)`。
- ❌ 错误：推理时也加训练用的 mask，导致生成第 1 个词时只能看自己 → ✅ 正确：推理时本来就一个词一个词生成，mask 自然满足（每次只看到已生成的）。训练时为了并行才需要 mask，推理时 mask 退化成"天然存在"。

## 章末小结

| 子层 | Q 来源 | K/V 来源 | 作用 |
|------|--------|----------|------|
| Masked Self-Attn | Decoder | Decoder | 已生成部分内部交互（贴封条） |
| Cross-Attn | Decoder | **Encoder** | 看源序列（Encoder-Decoder 桥梁） |
| FFN | - | - | 逐位置非线性变换 |
| Causal Mask | - | - | 上三角 -inf，封住未来 |

---

> **[可暂停点 5/7]** — 第五篇核心理论结束，可安全暂停。恢复时验证：`python -c "import torch; print(torch.nn.TransformerEncoderLayer(512, 8, 2048))"`

---

> 下一章：[Ch35 · 完整 Transformer 拼装与训练](35-完整Transformer拼装与训练.md)
