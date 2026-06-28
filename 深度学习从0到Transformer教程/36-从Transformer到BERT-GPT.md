# Ch36 · 从 Transformer 到 BERT / GPT

> 所属篇：第五篇 · 预计耗时：25 分钟

上一章你拼出了一台完整的 Transformer。但 2018 年之后，业界没人直接用"完整版"Transformer 了——大家拆出 Encoder 或 Decoder 单独用，分别造出了 BERT 和 GPT 两大流派，再加上"全家桶" T5。这一章讲清楚三大流派的区别、预训练任务、以及怎么用 HuggingFace 一行代码调用。

---

## 为了什么（Why）

**核心痛点**：完整 Transformer 需要成对的 (src, tgt) 数据，标注成本高。BERT/GPT/T5 用**自监督预训练**——只靠无标注文本自己跟自己学，再少量标注微调，效果吊打从零训练。

举个反例：你想做一个情感分类器，只有 1 万条标注数据。从零训 Transformer，1 万条根本不够，模型欠拟合。但如果你先拿 BERT（已经在几十 GB 文本上预训练过）做特征提取，再在 1 万条上微调，效果直接接近上限。**预训练 + 微调**是 NLP 的标准范式，本章讲清楚这个范式的源头。

**这一章的目标**：搞懂 BERT、GPT、T5 三大流派的区别和预训练任务，能用 HuggingFace 一行代码跑通。

## 要做到（Goal）

- **输入**：Ch35 的完整 Transformer。
- **输出**：理解 BERT/GPT/T5 三流派的架构和预训练任务，能用 HuggingFace 调用 GPT-2 生成文本。
- **成功标准**：能口述"BERT 用 Encoder、GPT 用 Decoder、T5 用 Encoder-Decoder"以及各自的预训练任务。

## 做了什么（What）

三大流派都是从完整 Transformer 里拆出来的一部分，配上不同的预训练任务：

```
完整 Transformer
       │
       ├──> 只留 Encoder ──> BERT（完形填空专家）
       │
       ├──> 只留 Decoder ──> GPT（接龙游戏冠军）
       │
       └──> 全留 ────────> T5（全能翻译官）
```

### 逐组件拆解

**BERT（Bidirectional Encoder Representations from Transformers）**：
- 架构：只用 Encoder（双向注意力，每个词能看到上下文所有词）
- 预训练任务：**MLM（Masked Language Modeling，完形填空）**——随机 mask 掉 15% 的词，让模型预测被 mask 的词
- 比喻：**完形填空专家**。给它一句 "The cat sat on the [MASK]"，它预测 [MASK] 是 "mat"。
- 适合：理解类任务（分类、NER、问答），不适合生成
- 代表模型：BERT-base、BERT-large、RoBERTa、ALBERT

**GPT（Generative Pre-trained Transformer）**：
- 架构：只用 Decoder（因果注意力，每个词只能看自己和之前，不能看未来）
- 预训练任务：**CLM（Causal Language Modeling，因果语言建模）**——预测下一个词
- 比喻：**接龙游戏冠军**。给它 "The cat sat on the"，它续写 "mat"。
- 适合：生成类任务（写作、对话、代码），也能做理解（用 prompt 引导）
- 代表模型：GPT-2、GPT-3、GPT-4、LLaMA、Qwen

**T5（Text-to-Text Transfer Transformer）**：
- 架构：完整 Encoder-Decoder
- 预训练任务：**Span Corruption**——随机遮盖一段连续 token，让模型生成被遮盖的内容
- 比喻：**全能翻译官**。所有任务都统一成"文本→文本"格式，翻译、摘要、分类都用同一个模型
- 适合：通用任务，工程上灵活
- 代表模型：T5、BART、mT5

### 三流派对比表

| 维度 | BERT | GPT | T5 |
|------|------|-----|-----|
| 架构 | Encoder-only | Decoder-only | Encoder-Decoder |
| 注意力 | 双向 | 单向（因果） | Encoder 双向，Decoder 单向 |
| 预训练任务 | MLM（完形填空） | CLM（接龙） | Span Corruption |
| 输入输出 | 文本→表示 | 文本→续写 | 文本→文本 |
| 擅长 | 理解 | 生成 | 通用 |
| 代表 | BERT、RoBERTa | GPT-2/3/4、LLaMA | T5、BART |

## 怎么算（How）

### 1. BERT 的 MLM 预训练

输入：`"The cat sat on the mat"`
随机 mask 15%：`"The cat [MASK] on the mat"`
目标：预测 `[MASK]` 位置是 `sat`

**15% 的细分**（BERT 原文设定）：
- 80% 真的换成 `[MASK]`
- 10% 换成随机词（防止模型只盯 [MASK] 标记）
- 10% 保持原词（让模型学会"原词也可能是对的"）

### 2. GPT 的 CLM 预训练

输入：`"The cat sat on the mat"`
训练样本拆成：

```
输入: The        → 目标: cat
输入: The cat    → 目标: sat
输入: The cat sat → 目标: on
...
```

由于因果 mask，所有位置可以**并行训练**（一次前向传播算出所有位置的 loss）。

### 3. T5 的 Span Corruption

输入：`"The cat sat on the mat"`
随机遮盖连续片段：`"The cat <X> on the <Y>"`
目标：`"<X> sat <Y> mat"`

T5 把所有任务统一成"输入文本 → 输出文本"，比如分类任务：

```
输入: "classify: This movie is great"
输出: "positive"
```

### 4. 为什么 GPT 能 Scaling Law？

**Scaling Law**（OpenAI 2020 提出）：模型效果随参数量、数据量、计算量**幂律**提升。

```
loss ∝ 1 / N^α   （N 是参数量）
```

**为什么 GPT 系列特别受益**：
- **Decoder-only 架构简单统一**：所有层都是因果 Attention + FFN，没有 Encoder-Decoder 的复杂接口，参数效率高
- **CLM 任务通用**：预测下一个词不需要任何标注，互联网上无穷无尽的文本都能用
- **生成式预训练培养通用能力**：学会预测下一个词，等于学会语言、世界知识、推理的压缩表示
- **涌现能力**：参数到一定规模（百亿级），突然学会指令遵循、上下文学习、推理

**BERT 不能 scaling 的原因**：MLM 任务只在 mask 位置算 loss（15%），训练信号稀疏；且双向注意力不能直接用于生成，扩展到超大模型收益递减。

## 怎么用（Use）

代码文件：`深度学习从0到Transformer教程/code/ch36_bert_gpt_huggingface.py`

关键片段：

```python
# === 一行代码调用 GPT-2 生成文本 ===
from transformers import pipeline

generator = pipeline("text-generation", model="gpt2")
result = generator("The cat sat on the", max_length=20, num_return_sequences=1)
print(result[0]['generated_text'])
# 输出示例: "The cat sat on the mat, watching the rain outside..."

# === 一行代码调用 BERT 做完形填空 ===
unmasker = pipeline("fill-mask", model="bert-base-uncased")
result = unmasker("The cat sat on the [MASK].")
print(result)
# 输出示例: [{'token_str': 'mat', 'score': 0.85}, ...]

# === 一行代码调用 T5 做翻译 ===
translator = pipeline("translation_en_to_fr", model="t5-small")
result = translator("The cat sat on the mat.")
print(result[0]['translation_text'])
# 输出示例: "Le chat s'est assis sur le tapis."
```

运行验证：

```bash
cd 深度学习从0到Transformer教程/code
python ch36_bert_gpt_huggingface.py
```

预期输出（节选，首次运行会下载模型）：
```
=== Ch36: 从 Transformer 到 BERT/GPT ===

--- GPT-2 生成 ---
输入: "The cat sat on the"
输出: "The cat sat on the mat, watching the rain..."

--- BERT 完形填空 ---
输入: "The cat sat on the [MASK]."
top 1: mat (score=0.85)
top 2: floor (score=0.06)
top 3: couch (score=0.03)

--- T5 翻译 ---
输入: "The cat sat on the mat."
输出: "Le chat s'est assis sur le tapis."

✅ 三大流派均调用成功
```

> 📊 完整代码见 [code/ch36_bert_gpt_huggingface.py](code/ch36_bert_gpt_huggingface.py)

**安装依赖**（如未安装）：

```bash
pip install transformers torch
```

## 想多一点

> **为什么 Decoder-only（GPT）最后成了大模型主流，而不是 Encoder-only（BERT）？**
>
> 这是个值得深思的问题，2018 年 BERT 风头正盛，2020 年后 GPT 系列反超。原因有几个：
>
> 1. **任务通用性**：GPT 用"接龙"统一所有任务（prompt 引导），BERT 只擅长理解类任务，生成类任务做不了。
> 2. **训练信号密度**：CLM 每个 token 都算 loss（100% 信号），MLM 只在 mask 位置算（15% 信号），同样算力下 CLM 学得更多。
> 3. **涌现能力**：GPT 到百亿参数以上突然学会指令遵循、上下文学习、思维链推理；BERT 没有这种涌现。
> 4. **工程友好**：Decoder-only 架构简单，KV cache 推理加速容易；Encoder-Decoder 有 Cross-Attention，工程复杂。
> 5. **数据无穷**：CLM 只需要无标注文本，互联网无穷无尽；MLM 也行但信号稀疏。
>
> 但 BERT 系没死——在**纯理解任务**（搜索、推荐、分类）上，小模型 BERT 仍比 GPT 性价比高。**架构选择取决于任务**，不是越新越好。

## 易错点预警

- ❌ 错误：拿 BERT 做文本生成 → ✅ 正确：BERT 是 Encoder-only，双向注意力，没有因果 mask，无法自回归生成。生成任务用 GPT 或 T5。
- ❌ 错误：拿 GPT 做 NER（命名实体识别）还从零训练 → ✅ 正确：GPT 也能做，但 BERT 的双向注意力对理解类任务更友好。理解类任务优先考虑 BERT 系列。
- ❌ 错误：以为 BERT 和 GPT 用的"Transformer"是同一个东西 → ✅ 正确：BERT 用 Encoder（双向），GPT 用 Decoder（单向），架构差别在注意力 mask。虽然都叫 Transformer，但子模块不同。
- ❌ 错误：HuggingFace `pipeline` 第一次运行卡住 → ✅ 正确：首次运行会从 HuggingFace Hub 下载模型（几百 MB 到几 GB），需要网络。国内可设置 `export HF_ENDPOINT=https://hf-mirror.com` 用镜像。

## 章末小结

| 流派 | 架构 | 预训练任务 | 比喻 | 代表模型 |
|------|------|-----------|------|---------|
| BERT | Encoder-only | MLM（完形填空） | 完形填空专家 | BERT、RoBERTa |
| GPT | Decoder-only | CLM（接龙） | 接龙游戏冠军 | GPT-2/3/4、LLaMA |
| T5 | Encoder-Decoder | Span Corruption | 全能翻译官 | T5、BART |
| Scaling Law | - | loss ∝ 1/N^α | 参数越多效果越好 | GPT 系列验证 |

---

> **[可暂停点 7/7]** — 第五篇 + BERT/GPT 全部结束。恭喜你完成了从矩阵乘法到大语言模型的完整旅程！

---

> 下一章：[Ch37 · 生成模型简介 — VAE / GAN / Diffusion](38-生成模型简介VAE-GAN-Diffusion.md)
