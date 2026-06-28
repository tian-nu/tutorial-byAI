# Ch27 · Seq2Seq 与编码器-解码器架构

> 所属篇：第五篇 · 预计耗时：25 分钟

你想把"我爱深度学习"翻译成"I love deep learning"。输入是 5 个中文字，输出是 4 个英文词，长度根本对不上。普通 LSTM 没法处理这种"输入序列和输出序列长度不同"的任务——它只会一格一格往后传，输出维度必须和输入维度对齐。怎么办？2014 年 Sutskever 等人想了个办法：先用一个 LSTM 把整句中文"读"完，压成一个固定向量，再用另一个 LSTM 把这个向量"展开"成英文。这就是 Seq2Seq，它是 Transformer 出现之前所有翻译、摘要、对话系统的基石。本章就把它彻底拆开。

---

## 为了什么（Why）

**核心痛点**：前几章的 RNN/LSTM 只会处理"输入=输出"的任务——给一句话输出一个分类标签（情感、词性），或者给一个词预测下一个词。但真实世界里大量任务是"序列到序列"的：

- 机器翻译：输入 5 字中文，输出 4 词英文
- 文本摘要：输入 1000 字长文，输出 50 字摘要
- 语音识别：输入 10 秒音频帧，输出文字
- 对话生成：输入用户问题，输出回复

这类任务的输入和输出长度都不一样，普通 LSTM 直接卡死。

**举个反例**：你想用普通 LSTM 做翻译，输入 6 字中文、输出 4 词英文。LSTM 的结构是"输入一个时间步、输出一个隐藏状态"——你硬要让它在第 6 步之后突然吐出 4 个英文词，它做不到。要么硬凑长度（把英文补成 6 个词），要么砍掉多余的（丢失信息），两条路都是错的。

**这一章的目标**：理解 Encoder-Decoder 架构，知道"读完整句 → 压成向量 → 展开成译文"这三步是怎么用两个 LSTM 串起来的。

## 要做到（Goal）

- **输入**：Ch25 的 LSTM 前向传播公式、知道 `h_t = LSTM(x_t, h_{t-1}, C_{t-1})` 怎么算。
- **输出**：能用 PyTorch 搭一个最小 Seq2Seq，能画出 Encoder 和 Decoder 的数据流图，能解释为什么训练和推理时 Decoder 的输入不一样。
- **成功标准**：给定 3 词输入、2 词输出的小例子，能手算 Encoder 跑完后上下文向量 `c` 的数值，并解释 Decoder 第一步该用什么作为输入。

## 做了什么（What）

Seq2Seq 的核心思想是一句话：**先把输入序列"读"成一个固定向量，再把这个向量"展开"成输出序列**。

打个比方：Encoder 是你读完整本中文小说，在脑子里压成一页纸的摘要；Decoder 是你看着这页摘要，逐字把它写成英文译文。摘要就是两本书之间的桥梁。

```
输入序列 x_1, x_2, x_3
   │     │     │
   ▼     ▼     ▼
┌──────────────────┐
│  Encoder (LSTM)  │  ← 读完整句
└────────┬─────────┘
         │
         ▼
   上下文向量 c = h_T^enc  ← 整句话压成一个向量
         │
         ▼
┌──────────────────┐
│  Decoder (LSTM)  │  ← 逐字生成译文
└────────┬─────────┘
         │
   y_1, y_2, ..., y_T'
```

### 逐组件拆解

**Encoder（编码器）**：一个标准的 LSTM。把输入序列 `x_1, x_2, ..., x_T` 一个一个喂进去，每一步更新隐藏状态 `h_t^enc` 和细胞状态 `C_t^enc`。读完最后一个词之后，最终隐藏状态 `h_T^enc` 和细胞状态 `C_T^enc` 就是"整句话的信息压缩"。

**上下文向量 c（Context Vector）**：连接 Encoder 和 Decoder 的桥梁。最简单的做法是 `c = h_T^enc`——只用最终隐藏状态。也有实现用 `c = (h_T^enc, C_T^enc)`，把隐藏状态和细胞状态一起传过去。本章采用最简版本 `c = h_T^enc`。

> **为什么用最后一个隐藏状态作为上下文？** 因为 LSTM 的隐藏状态 `h_t` 本来就是"到第 t 步为止所有信息的总结"——每一步 `h_t` 都是基于 `h_{t-1}` 和 `x_t` 更新出来的，所以 `h_T` 隐式地包含了 `x_1, ..., x_T` 的全部信息。LSTM 的门控机制保证了远距离信息不会被立刻冲掉。这也是为什么 LSTM 比 Vanilla RNN 更适合做 Encoder——它的"记忆"更稳。

**Decoder（解码器）**：另一个 LSTM。它的初始隐藏状态 `h_0^dec = c`（拿 Encoder 的总结当起点）。每一步输入上一步的输出 `y_{t-1}`（或特殊标记 `<START>`），更新自己的隐藏状态，再通过一个线性层 + softmax 输出当前词的概率分布。

**Teacher Forcing（教师强制）**：训练和推理时 Decoder 的输入方式完全不同：
- **训练时**：用真实答案 `y_{t-1}`（ground truth）作为下一步的输入。哪怕第 1 步预测错了，第 2 步还是喂真实的第 1 个词。这叫 Teacher Forcing——"老师"强制把正确答案塞给学生，让学生每一步都在正确路径上学习，收敛快得多。
- **推理时**：没有真实答案可用了，只能用第 t-1 步的预测值作为第 t 步的输入。一旦某步预测错，后面会越错越离谱，这叫"误差累积"（exposure bias）。

> **为什么叫 Teacher Forcing？** 想象老师在教学生写翻译。学生写到第 3 个词时卡住了，老师不会让他乱猜一个继续写下去，而是直接告诉他正确答案，让他从正确答案继续往下学。这样学生每一步都在"正确语境"里学，不会被自己前面的错误带偏。"Forcing"就是"强制喂正确答案"的意思。

## 怎么算（How）

### 核心公式

**Encoder**（沿用 Ch24/Ch25 的 LSTM 公式）：

```
h_t^enc, C_t^enc = LSTM(x_t, h_{t-1}^enc, C_{t-1}^enc)
```

读完整个序列后：

```
c = h_T^enc          # 上下文向量
```

**Decoder**：

```
h_t^dec, C_t^dec = LSTM(y_{t-1}, h_{t-1}^dec, C_{t-1}^dec)
y_t = softmax(W_o · h_t^dec)
```

初始条件：`h_0^dec = c`，`y_0 = <START>`（一个特殊的起始标记）。

### 数值小例子（2 维隐藏，输入 3 词，输出 2 词）

设输入序列 `x = [[1.0, 0.5], [0.3, 0.7], [0.8, 0.2]]`（3 个词，每个词 2 维嵌入）。

**第 1 步：Encoder 跑 3 步**

沿用 Ch25 的 LSTM 前向结果（具体门控计算见 Ch25，这里直接用结果）：

- 读 `x_1 = [1.0, 0.5]`，得 `h_1^enc ≈ [0.5, 0.5]`
- 读 `x_2 = [0.3, 0.7]`，得 `h_2^enc ≈ [0.8, 0.2]`（数字为示意，实际取决于权重）
- 读 `x_3 = [0.8, 0.2]`，得 `h_3^enc ≈ [0.85, 0.85]`

所以上下文向量：

```
c = h_3^enc ≈ [0.85, 0.85]
```

**第 2 步：Decoder 初始化**

```
h_0^dec = c = [0.85, 0.85]
y_0 = <START> = [1.0, 0.0]   # 假设 <START> 的嵌入就是 [1, 0]
```

**第 3 步：Decoder 第 1 步**

把 `y_0 = [1.0, 0.0]` 和 `h_0^dec = [0.85, 0.85]` 喂给 Decoder LSTM（同样套用 Ch25 的 LSTM 公式），假设算出：

```
h_1^dec ≈ [0.78, 0.78]
```

再过线性层 + softmax 输出词的概率。假设输出层权重 `W_o = [[1, 0], [0, 1]]`（单位矩阵，简化）：

```
logits = W_o · h_1^dec = [0.78, 0.78]
softmax([0.78, 0.78]) = [0.5, 0.5]
```

意思是"两个候选词的概率各一半"——因为 logits 两个值相等，softmax 必然均分。

**第 4 步：Decoder 第 2 步**

- 训练时（Teacher Forcing）：把真实答案的第 1 个词（不是预测值）作为输入
- 推理时：把第 1 步预测出来的词作为输入

继续跑 LSTM，输出第 2 个词的概率分布，循环往复直到输出 `<END>` 标记为止。

## 怎么用（Use）

代码文件：`深度学习从0到Transformer教程/code/ch27_seq2seq.py`

关键片段：

```python
import torch
import torch.nn as nn

class Encoder(nn.Module):
    def __init__(self, vocab_size, emb_dim, hid_dim):
        super().__init__()
        self.emb = nn.Embedding(vocab_size, emb_dim)
        self.lstm = nn.LSTM(emb_dim, hid_dim, batch_first=True)

    def forward(self, x):
        # x: (batch, T) 整数索引
        _, (h, c) = self.lstm(self.emb(x))
        # h, c: (1, batch, hid_dim)
        return h, c

class Decoder(nn.Module):
    def __init__(self, vocab_size, emb_dim, hid_dim):
        super().__init__()
        self.emb = nn.Embedding(vocab_size, emb_dim)
        self.lstm = nn.LSTM(emb_dim, hid_dim, batch_first=True)
        self.fc = nn.Linear(hid_dim, vocab_size)

    def forward(self, y, h, c):
        # y: (batch, 1) 当前步输入词的索引
        out, (h, c) = self.lstm(self.emb(y), (h, c))
        logits = self.fc(out.squeeze(1))   # (batch, vocab_size)
        return logits, h, c
```

运行验证：

```bash
cd 深度学习从0到Transformer教程/code
python ch27_seq2seq.py
```

预期输出（节选）：

```
=== Seq2Seq 前向 ===
Encoder (h, c) 形状: torch.Size([1, 2, 8])
Decoder 第 1 步 logits 形状: torch.Size([2, 20])
Decoder 第 2 步 logits 形状: torch.Size([2, 20])
训练模式: 用真实标签作为下一步输入 (Teacher Forcing)
推理模式: 用预测值作为下一步输入
```

> 📊 完整代码见 [code/ch27_seq2seq.py](code/ch27_seq2seq.py)

## 想多一点

> 上下文向量 `c` 是一个固定长度的向量，真的能装下整句话的信息吗？
>
> 答案是：**短句子可以，长句子必然丢失**。这就是 Seq2Seq 的核心瓶颈。假设 `c` 是 512 维，翻译 10 字短句够用，但翻译 100 字长段时，Encoder 必须把这 100 字的全部细节压进同样的 512 维——信息被严重压缩，后段翻译质量会断崖式下跌。
>
> Bahdanau 等人在 2014 年提出 Attention 机制，正是为了解决这个瓶颈：Decoder 每一步都不再只看一个固定 `c`，而是动态地"回看" Encoder 的所有隐藏状态，挑当前最相关的部分加权求和。下一章我们就拆 Attention。

## 易错点预警

- ❌ Decoder 第一步输入用零向量 → ✅ 正确：必须用一个特殊的 `<START>` token 作为起始信号。零向量没有任何"开始生成"的语义提示，Decoder 不知道该从哪开始。
- ❌ 训练时用模型自己的预测值作为下一步输入 → ✅ 正确：训练时用 Teacher Forcing（喂真实标签），让每一步都在正确路径上学，收敛更快；推理时才用预测值。两者不能搞反。
- ❌ 上下文向量 `c` 同时塞给 Decoder 的 `h_0` 和 `C_0` 但没意识到自己这么做了 → ✅ 正确：明确写 `h_0^dec = c`，`C_0^dec` 可以用零张量或同样设为 `c`，但要清楚自己选了哪种。最简版本只用 `h_0 = c`，`C_0` 用零。

## 章末小结

| 组件 | 作用 | 输入 | 输出 |
|------|------|------|------|
| Encoder | 读入序列，压缩成上下文 | `x_1, ..., x_T` | `c = h_T^enc` |
| 上下文 c | 桥接编码和解码 | `h_T^enc` | `h_0^dec` |
| Decoder | 逐步生成输出 | `y_{t-1}, h_{t-1}^dec` | `y_t` |
| Teacher Forcing | 训练时用真实标签加速收敛 | `y_true_{t-1}` | 稳定梯度 |
| `<START>` token | 告诉 Decoder "开始生成" | 无 | 第一个时间步的输入 |
| `<END>` token | 告诉 Decoder "可以停了" | 无 | 生成终止信号 |

---

> 下一章：[Ch28 · Attention 机制让模型学会看哪里](28-Attention机制让模型学会看哪里.md)
