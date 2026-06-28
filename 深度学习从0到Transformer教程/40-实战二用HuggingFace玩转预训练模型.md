# Ch40 · 实战二：用 HuggingFace 玩转预训练模型

> 所属篇：第七篇 · 预计耗时：30 分钟

Ch39 我们从零训练了两个小模型，BiLSTM 跑到 86% 就沾沾自喜了。但工业界谁还从零训？大家都在用预训练大模型——BERT、GPT、T5。HuggingFace 就是这些模型的"应用商店"，一行代码就能调用一个在海量语料上学过语言的模型。这一章我们用三行代码干掉 Ch39 一整章的工作量，再看看怎么把预训练模型"微调"成自己的任务。

打个比方：Ch39 是从种子开始种小麦、磨面粉、烤面包，全程亲手干，累但懂原理；HuggingFace 是直接买半成品面团，你只要塞进烤箱调个温度就行。微调（fine-tuning）就像大学生转专业——本科四年（预训练）打下的数学英语底子还在，只要补一年专业课（微调）就能上岗，不用重新读一遍大一。

---

## 为了什么（Why）

**核心痛点**：从零训练成本高、效果差。你自己训一个 100M 参数的模型要几天、烧几百块 GPU 费用，效果还比不上人家现成的。而预训练模型已经在几十 GB 文本上学过"语言长什么样"，你只要在它上面"继续学"自己的任务就行。

举个反例。Ch39 我们用 2.5 万条 IMDB 评论从零训 BiLSTM，5 个 epoch 才到 86%。如果你用 BERT 微调同样这份数据，1 个 epoch 就能到 92%+，因为 BERT 在维基百科 + 书堆上预训练过，早就"认识"good/bad/terrible 这些词了，你只是教它"把这些词的情感倾向映射到正负标签"。

**这一章的目标**：学会用 HuggingFace 三件套（Tokenizer / Model / Pipeline）做三件事——情感分类、问答、文本生成；再学会用 Trainer API 微调一个 BERT。看完你就具备了"调包做 NLP 任务"的最低门槛能力。

## 要做到（Goal）

- **输入**：HuggingFace `transformers` 库（`pip install transformers`）。
- **输出**：跑通 3 个 pipeline 任务；写出一段能微调 BERT 的代码骨架。
- **成功标准**：三个 pipeline 都输出合理结果（情感分类给概率、问答抽到片段、生成文本通顺）；微调代码能跑起来不报错（没有 GPU 也能用小模型跑通流程）。

## 做了什么（What）

HuggingFace 的世界可以浓缩成"三件套 + 一个 API"：

```
原始文本
    │
    ▼
Tokenizer（文本 → token id）  ← AutoTokenizer.from_pretrained("模型名")
    │
    ▼
Model（token id → 预测结果）   ← AutoModel.from_pretrained("模型名")
    │
    ▼
Pipeline（封装上面两步，一行调用）  ← pipeline("任务", model="模型名")
    │
    └──> 微调：Trainer API（在预训练模型上继续训练你的数据）
```

### 逐组件拆解

**Tokenizer（分词器）**：把字符串切成 token 并转成 id。和 Ch39 的 `str.split()` 不同，HuggingFace 的 Tokenizer 用的是 **子词分词（subword tokenization）**，比如 BERT 的 WordPiece 会把 `playing` 拆成 `play` + `##ing`。好处是词表小（3 万左右）、能处理未登录词（不会全变 `<unk>`）。一行 `tokenizer("I love it")` 就返回 `{"input_ids": [...], "attention_mask": [...]}`。

**Model（预训练模型）**：装好权重的 Transformer。`from_pretrained("bert-base-chinese")` 会从 HuggingFace Hub 下载权重并加载。BERT 是 Encoder（Ch33）、GPT 是 Decoder（Ch34）、T5 是 Encoder-Decoder（Ch35）——你看，前面学过的零件全在这。

**Pipeline（流水线）**：把 Tokenizer + Model 包成"输入文本 → 输出结果"的高层 API，是你最常调的接口。`pipeline("sentiment-analysis")` 一行就能做情感分类，不用你自己写 forward、softmax、argmax。这就是"应用商店"——选个任务，它自动给你配好模型。

**Trainer API**：微调专用。你只要提供模型、数据集、训练参数（epoch、batch_size、lr），它帮你跑训练循环（Ch39 我们手写的 `zero_grad/backward/step` 全省了）。这就像从"手动挡"换到"自动挡"。

### 预训练目标：BERT 和 GPT 学的是什么

- **BERT**：Masked Language Modeling（MLM）。随机遮盖 15% 的 token，让模型根据上下文猜被遮住的词。像完形填空，所以 BERT **能看双向**上下文，适合理解类任务（分类、问答）。
- **GPT**：Causal Language Modeling（CLM）。预测下一个 token，像文字接龙。只能看左边，所以适合**生成**类任务。

## 怎么算（How）

> 本节精简：BERT 的内部就是 Ch33 的 Transformer Encoder 堆 12 层，GPT 就是 Ch34 的 Decoder 堆 12 层。注意力分数 `softmax(QK^T/√d)` 的公式见 Ch29，这里不重推。
>
> 实战篇聚焦"怎么调"，公式细节回到对应章节查。唯一要记住的数：`bert-base` 约 1.1 亿参数、12 层、隐藏维度 768、12 个头。这就是"base"级的规模——你能跑，消费级显卡 8GB 显存勉强够。

## 怎么用（Use）

代码文件：`深度学习从0到Transformer教程/code/ch40_huggingface.py`

关键片段：

```python
import os
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"   # 国内镜像，加速下载
from transformers import pipeline

# 1. 情感分类 —— 一行干掉 Ch39 一整章
classifier = pipeline("sentiment-analysis")
print(classifier("I love deep learning!"))
# [{'label': 'POSITIVE', 'score': 0.9998}]

# 2. 抽取式问答 —— 给一段上下文，问问题，它从原文抽答案
qa = pipeline("question-answering")
result = qa(
    question="What is Transformer?",
    context="Transformer is a neural network architecture based on self-attention."
)
print(result["answer"])
# 'a neural network architecture based on self-attention'

# 3. 文本生成 —— GPT 接龙
generator = pipeline("text-generation", model="gpt2")
print(generator("Deep learning is", max_length=30, num_return_sequences=1))
```

微调 BERT 的骨架（完整代码见代码文件）：

```python
from transformers import BertForSequenceClassification, Trainer, TrainingArguments

model = BertForSequenceClassification.from_pretrained("bert-base-chinese", num_labels=2)
training_args = TrainingArguments(
    output_dir="./results",
    num_train_epochs=3,
    per_device_train_batch_size=16,
    learning_rate=2e-5,            # 微调 lr 要小，2e-5 是 BERT 经验值
    fp16=True,                      # 显存不够就开混合精度
)
trainer = Trainer(model=model, args=training_args, train_dataset=train_ds)
trainer.train()
```

运行验证：

```bash
cd 深度学习从0到Transformer教程/code
python ch40_huggingface.py
```

预期输出（节选）：

```
=== 1. 情感分类 pipeline ===
[{'label': 'POSITIVE', 'score': 0.9998}]
=== 2. 问答 pipeline ===
答案: a neural network architecture based on self-attention
=== 3. 文本生成 pipeline ===
Deep learning is a method that...
=== 4. 微调 BERT（演示骨架）===
未检测到 GPU，跳过实际微调训练。骨架代码已展示，请见代码文件。
```

> 📊 完整代码见 [code/ch40_huggingface.py](code/ch40_huggingface.py)

### 怎么读 pipeline 的输出

- **情感分类**：返回 `label`（POSITIVE/NEGATIVE）和 `score`（0～1 的置信度）。`score > 0.99` 说明模型很笃定。
- **问答**：返回 `answer`（从 context 抽出来的片段）、`score`（置信度）、`start`/`end`（片段在原文的字符位置）。这是"抽取式"问答——它不会自己编，只会从给定的 context 里找。
- **文本生成**：返回 `generated_text`。`max_length` 控制生成长度，`num_return_sequences` 控制生成几条。GPT 是随机采样，每次跑结果不一样。

## 想多一点

> 预训练模型为什么这么强？
>
> 三个字：**数据、参数、自监督**。BERT 在 16GB 文本（维基百科 + BookCorpus）上训练，GPT-3 在 570GB 文本上训练——一个人一辈子读不完的量。参数从 1 亿到 1750 亿，表达力爆炸。关键是**自监督**：不需要人工标注，"遮住一个词让它猜"或"预测下一个词"就是天然标签，所以能用上几乎无限的数据。
>
> 学到的"通用语言表示"有多通用？研究发现 BERT 的中间层神经元对应语法角色（主语、动词）、共指消解、甚至一些常识——这些都不是人教它的，是从海量文本里"涌现"出来的。下游任务只需微调最后一两层，相当于在"大学基础课"上加一门"专业课"。

## 易错点预警

- ❌ 错误：第一次运行卡在下载模型，等了几分钟以为程序死了直接 Ctrl+C。✅ 正确：BERT-base 约 420MB、GPT2 约 550MB，首次下载慢正常；国内用户先设 `os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"` 走镜像，速度能从几十 KB/s 提到几 MB/s。
- ❌ 错误：`CUDA out of memory` 报错后还硬跑，进程被杀。✅ 正确：按顺序试这三招——① `per_device_train_batch_size` 从 16 降到 8 甚至 4；② 开混合精度 `fp16=True`，显存直接减半；③ 换更小的模型（`bert-base` → `distilbert-base`，参数少 40%）。还不行就 `model.half()` 把权重转成 FP16 再跑。CPU 用户直接 `device="cpu"`，能跑只是慢。
- ❌ 错误：微调时 `learning_rate=1e-3`（照搬 Ch39 的值）→ 模型直接崩，loss 变 NaN。✅ 正确：预训练模型已经训好了，lr 必须小，BERT 微调经验值是 `2e-5` 到 `5e-5`。这是新手最常踩的坑——从零训用大 lr，微调用小 lr。
- ❌ 错误：pipeline 做问答时 `context` 给得特别短或问题与 context 无关，期待它"自己知道"。✅ 正确：抽取式问答**只会从 context 抽**，不会用模型自身的世界知识。context 里没有答案它就乱抽一个。想让它"自己知道"得用生成式模型（如 GPT）。
- ❌ 错误：文本生成不设 `max_length`，一直生成到模型自己停 → 可能跑几百 token 还不停，浪费时间。✅ 正确：显式设 `max_length=30` 或 `max_new_tokens=30`，控制生成长度。

## 章末小结

| 任务 | Pipeline 名 | 典型模型 | 用途 | 微调 lr |
|------|------------|----------|------|---------|
| 情感分类 | `sentiment-analysis` | BERT / DistilBERT | 文本打标签 | 2e-5 |
| 抽取式问答 | `question-answering` | BERT | 从原文抽答案 | 3e-5 |
| 文本生成 | `text-generation` | GPT2 | 续写、补全 | 5e-5 |
| 微调任意任务 | Trainer API | 任意预训练模型 | 下游定制 | 2e-5～5e-5 |
| 显存急救 | — | — | batch 减半 / fp16 / 换小模型 | — |

---

> 下一章：[Ch41 · 下一步去哪 — 学习路线图](41-下一步去哪学习路线图.md)
