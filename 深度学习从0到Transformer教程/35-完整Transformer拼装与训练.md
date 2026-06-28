# Ch35 · 完整 Transformer 拼装与训练

> 所属篇：第五篇 · 预计耗时：30 分钟

前面 6 章我们把 Transformer 拆成了零件：Attention、FFN、LN、PE、Mask。本章把它们拧成一台完整的机器，跑通"输入→输出→loss→反向→更新"全流程。这一章跑通，你手里就有了一个能训练的 Transformer。

---

## 为了什么（Why）

**核心痛点**：只懂零件不懂组装，等于纸上谈兵。面试时能背 Attention 公式，但让写一个最小 Transformer 跑通，无从下手。

举个反例：你知道 Multi-Head Attention 怎么算、知道 LayerNorm 怎么归一化，但拼起来时遇到一堆问题——Embedding 维度对不上、PE 加到哪里、训练时 tgt 该怎么喂、loss 怎么算、为什么初始 loss 是 4.6 不是 0.5。这些都是"组装"环节的坑，不亲手拼一遍踩不到。

**这一章的目标**：用 PyTorch 拼出完整 Transformer，跑通一个简单序列任务，看 loss 从 ~4.6 降到 < 3.0。

## 要做到（Goal）

- **输入**：Ch27-34 的所有组件。
- **输出**：能用 PyTorch 拼出完整 Transformer，跑通训练循环。
- **成功标准**：训练 100 步后 loss 明显下降（从 ~4.6 降到 < 3.0）。

## 做了什么（What）

完整 Transformer 的数据流是这样的：

```
src ──> Embedding ──+──> Encoder×N ──┐
                     └──> PE          │
                                      │（Cross-Attn 时 K/V 来源）
tgt[:-1] ─> Embedding ─+──> Decoder×N ──> Linear ──> logits ──> CrossEntropy ──> loss
          └──> PE      │               │
                          └──> tgt_mask │
```

### 逐组件拆解

**输入嵌入（Embedding）**：`nn.Embedding(vocab_size, d_model)`。把 token id（整数）变成 d_model 维向量。比如词表 1000，d_model=64，输入 `[5, 12, 8]` 输出 `(3, 64)`。

**位置编码（Positional Encoding, PE）**：sin/cos 公式生成，加到 Embedding 上。Ch31 里 PE 写成函数，这里**封装成 `nn.Module` 类**方便调用（在 forward 里 `x = x + self.pe(x)`）。封装原因：Transformer 是 `nn.Module`，子组件也应该是 `nn.Module`，才能统一管理参数和设备移动。

**Encoder**：N 个 `EncoderBlock` 堆叠（Ch33）。

**Decoder**：N 个 `DecoderBlock` 堆叠（Ch34）。

**输出层**：`nn.Linear(d_model, vocab)` 把 d_model 维映射回词表大小，得到 logits。softmax 由 CrossEntropyLoss 内部做，不用显式调用。

## 怎么算（How）

### 1. 核心公式

```
# 前向
src_emb = PE(src_emb(src))           # (B, T_src, d_model)
tgt_emb = PE(tgt_emb(tgt))           # (B, T_tgt, d_model)
enc_out = Encoder×N(src_emb)         # (B, T_src, d_model)
dec_out = Decoder×N(tgt_emb, enc_out, tgt_mask)  # (B, T_tgt, d_model)
logits  = Linear(dec_out)            # (B, T_tgt, vocab)

# 损失（teacher forcing：输入 tgt[:-1]，预测 tgt[1:]）
loss = CrossEntropy(logits.reshape(-1, vocab), tgt[:, 1:].reshape(-1))

# 反向 + 更新
loss.backward()
optimizer.step()
```

### 2. 数值小例子（vocab=100, d_model=128, N=3）

设：
- `src = [[5, 12, 8, 1]]`（batch=1, T_src=4）
- `tgt = [[2, 7, 3, 9]]`（batch=1, T_tgt=4）

**前向各步 shape**：

| 阶段 | 操作 | 输出 shape |
|------|------|-----------|
| Embedding | `src_emb(src)` | (1, 4, 64) |
| +PE | `src_emb + pe` | (1, 4, 64) |
| Encoder×2 | 两个 EncoderBlock | (1, 4, 64) |
| Decoder 输入 | `tgt[:, :-1] = [[2, 7, 3]]` | (1, 3) |
| Decoder×2 | 含 Cross-Attn | (1, 3, 64) |
| Linear | 映射回词表 | (1, 3, 100) |
| Loss | 对 `tgt[:, 1:] = [[7, 3, 9]]` | 标量 |

### 3. 为什么初始 loss ≈ ln(100) ≈ 4.6？

这是高频困惑点。解释清楚：

模型刚初始化时，参数随机，输出 logits 接近均匀分布。对一个 100 类的分类问题，如果模型对每个类预测概率都是 1/100，交叉熵损失是：

```
L = -Σ y_i · log(p_i) = -log(1/100) = log(100) ≈ 4.605
```

其中：
- `y_i` 是 one-hot 真实标签（正确类为 1，其余为 0）
- `p_i = 1/100` 是模型对每个类的预测概率（均匀分布）

**推导**：
```
L = -Σ_i y_i · log(p_i)
  = -y_correct · log(1/100) - Σ_{i≠correct} 0 · log(1/100)
  = -1 · log(1/100)
  = -log(1/100)
  = log(100)
  ≈ 4.605
```

**通用规律**：vocab 大小 V，初始 loss ≈ ln(V)。
- V=100 → loss ≈ 4.6
- V=1000 → loss ≈ 6.9
- V=30000（中等词表）→ loss ≈ 10.3

**实战意义**：训练 Transformer 时，第一步 loss 应该在 ln(vocab) 附近。如果第一步 loss 是 0.5 或 20，说明有 bug（标签错了、logits 没归一化、loss 函数选错等）。

### 4. Teacher Forcing 与 mask 配合

训练时用 **teacher forcing**：Decoder 输入是 `tgt[:, :-1]`（去掉最后一个词），目标是 `tgt[:, 1:]`（去掉第一个词）。这样 Decoder 第 i 位输入第 i 个词，预测第 i+1 个词，配合因果 mask 严格保证只看过去。

```
tgt     = [<BOS>, w1, w2, w3, <EOS>]
输入    = [<BOS>, w1, w2, w3]         （tgt[:, :-1]）
目标    = [w1,    w2, w3, <EOS>]      （tgt[:, 1:]）
```

## 怎么用（Use）

代码文件：`深度学习从0到Transformer教程/code/ch35_full_transformer.py`

关键片段：

```python
import torch
import torch.nn as nn
import math

class PositionalEncoding(nn.Module):
    """把 Ch31 的 PE 函数封装成 Module，方便在 Transformer 里调用"""
    def __init__(self, d_model, max_len=5000, dropout=0.1):
        super().__init__()
        self.dropout = nn.Dropout(dropout)
        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len).unsqueeze(1).float()
        div_term = torch.exp(torch.arange(0, d_model, 2).float() *
                             -(math.log(10000.0) / d_model))
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        self.register_buffer('pe', pe.unsqueeze(0))   # (1, max_len, d_model)

    def forward(self, x):
        x = x + self.pe[:, :x.size(1)]
        return self.dropout(x)


class Transformer(nn.Module):
    def __init__(self, src_vocab, tgt_vocab, d_model=512, n_heads=8,
                 N=6, d_ff=2048, dropout=0.1):
        super().__init__()
        self.src_emb = nn.Embedding(src_vocab, d_model)
        self.tgt_emb = nn.Embedding(tgt_vocab, d_model)
        self.pos_enc = PositionalEncoding(d_model, dropout=dropout)
        self.encoder = nn.ModuleList(
            [EncoderBlock(d_model, n_heads, d_ff, dropout) for _ in range(N)])
        self.decoder = nn.ModuleList(
            [DecoderBlock(d_model, n_heads, d_ff, dropout) for _ in range(N)])
        self.fc_out = nn.Linear(d_model, tgt_vocab)

    def forward(self, src, tgt, tgt_mask=None):
        src = self.pos_enc(self.src_emb(src))
        tgt = self.pos_enc(self.tgt_emb(tgt))
        for enc in self.encoder:
            src = enc(src)
        for dec in self.decoder:
            tgt = dec(tgt, src, tgt_mask=tgt_mask)
        return self.fc_out(tgt)


# === 训练循环（迷你任务：复制序列）===
vocab = 100
model = Transformer(vocab, vocab, d_model=64, n_heads=4, N=2, d_ff=128)
opt = torch.optim.Adam(model.parameters(), lr=1e-3)
loss_fn = nn.CrossEntropyLoss()

for step in range(100):
    src = torch.randint(1, vocab, (8, 6))   # batch=8, T=6
    tgt = src.clone()                        # 复制任务：tgt = src
    tgt_mask = torch.triu(torch.ones(6, 6) * float('-inf'), diagonal=1)

    logits = model(src, tgt[:, :-1], tgt_mask=tgt_mask)
    loss = loss_fn(logits.reshape(-1, vocab), tgt[:, 1:].reshape(-1))
    loss.backward()
    opt.step()
    opt.zero_grad()
    if step % 10 == 0:
        print(f"step {step}: loss = {loss.item():.4f}")
```

运行验证：

```bash
cd 深度学习从0到Transformer教程/code
python ch35_full_transformer.py
```

预期输出（节选）：
```
=== Ch35: 完整 Transformer 拼装与训练 ===

模型配置: vocab=100, d_model=128, n_heads=4, N=3, d_ff=512
参数总量: 1,427,044

--- 初始 loss 验证 ---
vocab = 100, ln(vocab) = 4.6052
初始 loss = 4.7690
✅ 初始 loss 接近 ln(vocab)，符合均匀分布的交叉熵

--- 训练循环（复制序列任务）---
  step   0: loss = 4.7266
  step  20: loss = 4.1713
  step  40: loss = 2.7703
  step  60: loss = 1.9411
  step  80: loss = 0.9940
  step 100: loss = 0.5720
  step 120: loss = 0.2963
  step 140: loss = 0.0874
  step 160: loss = 0.2274
  step 180: loss = 0.2071
  step 199: loss = 0.0650
✅ loss 从 4.73 降到 0.07，训练成功
```

> 📊 完整代码见 [code/ch35_full_transformer.py](code/ch35_full_transformer.py)
> 📊 可视化演示见 [35_transformer_architecture_visual.html](35_transformer_architecture_visual.html)

## 想多一点

> **为什么 Transformer 训练用 Adam 而非 SGD？**
>
> Transformer 的梯度 landscape 很复杂：Attention 的 softmax 梯度、FFN 的 ReLU 梯度、LayerNorm 的归一化梯度，尺度差异大。SGD 用统一学习率，要么Attention 那边梯度太小没动静，要么 FFN 那边梯度太大炸了。
>
> **Adam 的优势**：
> - **自适应学习率**：每个参数有自己的有效学习率，自动适配梯度尺度。
> - **动量**：累积历史梯度方向，平滑噪声。
> - **对初始学习率不敏感**：比 SGD 容忍度高。
>
> **为什么还需要 warmup**：原始论文用 `Adam + warmup`——前 4000 步学习率从 0 线性升到最大，再按 inverse_sqrt 衰减。原因是 Adam 最初几步的二阶矩估计不准（统计量还没攒够），大学习率会让训练抖动。warmup 给统计量攒够的时间，再放大学习率。
>
> **现代趋势**：用 AdamW（Adam + weight decay 解耦），warmup 可选。很多大模型（GPT、LLaMA）都是 AdamW 训练的。

## 易错点预警

- ❌ 错误：训练时 tgt 用完整序列而非 `tgt[:, :-1]` → ✅ 正确：输入是 `tgt[:, :-1]`（去掉最后一位），目标是 `tgt[:, 1:]`（去掉第一位）。这样第 i 位预测第 i+1 位，符合自回归生成逻辑。如果输入完整 tgt，模型会"看到答案再预测答案"，训练推理不一致。
- ❌ 错误：忘记 `ignore_index=0`（padding 位置计入 loss） → ✅ 正确：如果用 0 做 padding id，loss 函数加 `ignore_index=0`，让 padding 位置不计入 loss。否则模型会花大量精力学习预测 padding，浪费容量。
- ❌ 错误：初始 loss 不是 ln(vocab) 附近，比如 0.5 或 20 → ✅ 正确：第一步 loss 应该在 ln(vocab) 附近。偏离太多说明有 bug——检查 logits 是否正确、标签是否对齐、loss 函数是否选对（分类用 CrossEntropyLoss 不是 MSELoss）。
- ❌ 错误：PositionalEncoding 用函数而非 Module，导致 .to(device) 时 pe 没跟着移动 → ✅ 正确：PE 封装成 `nn.Module`，用 `register_buffer('pe', ...)` 注册，这样 `.to(device)` 和 `.eval()` 会自动处理。

## 章末小结

| 阶段 | 操作 | 输出 shape |
|------|------|-----------|
| 嵌入 | Embedding + PE | (B, T, d_model) |
| 编码 | Encoder×N | (B, T_src, d_model) |
| 解码 | Decoder×N（含 Cross-Attn） | (B, T_tgt, d_model) |
| 输出 | Linear(d_model, vocab) | (B, T_tgt, vocab) |
| 训练 | CE Loss + Adam + warmup | loss（初始 ≈ ln(vocab)，训练后 ≈ 0.07） |
| 推理 | 自回归 + beam search | 生成的 token 序列 |

---

> **[可暂停点 6/7]** — 第五篇全部结束，可安全暂停。恢复时验证：`python -c "import torch; m=torch.nn.Transformer(d_model=64, nhead=4, num_encoder_layers=2); print(m)"`

---

> 下一章：[Ch36 · 从 Transformer 到 BERT / GPT](36-从Transformer到BERT-GPT.md)
