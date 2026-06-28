# 附录 E · 论文阅读指南

> 所属篇：附录 · 预计耗时：20 分钟（通读一次，之后按需查阅）

本附录给出去读深度学习经典论文的方法、顺序和清单。教程正文讲的是"原理怎么算"，论文读完后能补上"作者为什么这么想"和"这个领域怎么演进"。

---

## 一、为什么要读论文

教程是**消化后的二次产出**，论文是**一手来源**。读论文能获得教程难以传递的三样东西：

1. **动机**：作者为什么觉得这个问题值得做？当时别人怎么做的、有什么痛点？
2. **取舍**：为什么是这个公式而不是另一个？哪些是工程妥协？
3. **演进脉络**：每篇论文都站在前人肩上，读几篇就能看到一条"RNN → LSTM → Seq2Seq → Attention → Transformer → BERT/GPT"的主线。

> 一句话：教程教你"会用"，论文教你"会判断"。

---

## 二、论文阅读三遍法（推荐）

来自 S. Keshav《How to Read a Paper》，是公认最高效的方法。

### 第一遍：鸟瞰（5~10 分钟）

**目的**：判断这篇论文值不值得读、属于哪一类。

- 读 **标题、摘要、引言**。
- 读 **章节标题**、**图表**、**结论**。
- 不读公式、不读相关工作。

**第一遍后能回答**：
1. 这篇论文解决什么问题？
2. 用了什么方法？
3. 跟我相关吗？要不要继续读？

### 第二遍：抓核心（30~60 分钟）

**目的**：掌握论文的核心贡献和方法。

- 读 **方法部分**的每一张图（架构图最关键）。
- 读 **实验设置**：用了什么数据集、对比哪些 baseline、用什么指标。
- 跳过陌生但非核心的公式推导。
- 标记**不懂的术语和引用**，第二遍结束集中查。

**第二遍后能回答**：
1. 方法的关键创新点是什么？（一两句话）
2. 实验是否支持结论？
3. 哪些细节我需要去复现？

### 第三遍：深度复现（数小时～数天）

**目的**：能从头复现这篇论文。

- 推导每个公式，自己用 NumPy/PyTorch 写一遍核心模块。
- 对照作者给的实验设置跑一遍。
- 思考：如果换我来做，会怎么改进？

> 第三遍不是每篇都要做。只对你**真正要用**的论文做第三遍。

---

## 三、带着问题读

读论文前先写下 3 个问题，读完后逐条回答。问题模板：

1. **痛点**：作者说之前的方法有什么问题？
2. **招式**：作者用了什么新方法解决？关键公式是哪个？
3. **证据**：哪个实验最能说明这个方法有效？

> 如果读完答不出这三问，说明你没读懂或这篇论文没干货。

---

## 四、推荐论文阅读顺序

按难度从易到难、按时间从早到晚排列。建议**跟着教程进度读**：学完对应章节再读相关论文。

| 序号 | 论文 | 年份 | 核心贡献 | 难度 | 前置知识 | 对应教程章节 |
|------|------|------|----------|------|----------|--------------|
| 1 | Learning long-term dependencies with gradient descent is difficult — Bengio et al. | 1994 | 首次系统论证 RNN 训练中梯度消失/爆炸是本质问题，长依赖难学的根因 | ⭐⭐ | 反向传播、链式法则 | Ch21, Ch22 |
| 2 | Long Short-Term Memory — Hochreiter & Schmidhuber | 1997 | 提出 LSTM，用门控和细胞状态让梯度在长序列上稳定流动 | ⭐⭐⭐ | RNN、BPTT、梯度消失 | Ch23-Ch26 |
| 3 | Sequence to Sequence Learning with Neural Networks — Sutskever et al. | 2014 | Encoder-Decoder 范式：一个 RNN 编码、一个 RNN 解码，端到端翻译 | ⭐⭐⭐ | LSTM | Ch27 |
| 4 | Neural Machine Translation by Jointly Learning to Align and Translate — Bahdanau et al. | 2014 | 提出 Attention，Decoder 每步动态关注 Encoder 不同位置，打破信息瓶颈 | ⭐⭐⭐⭐ | Seq2Seq、LSTM | Ch28 |
| 5 | Attention Is All You Need — Vaswani et al. | 2017 | Transformer：纯 Self-Attention 替代循环，可并行训练，开启大模型时代 | ⭐⭐⭐⭐ | Attention、LayerNorm、残差连接 | Ch29-Ch35 |
| 6 | BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding — Devlin et al. | 2018 | 双向 MLM 预训练 + 微调范式，刷爆 11 项 NLP 任务 | ⭐⭐⭐ | Transformer | Ch36, Ch40 |
| 7 | Improving Language Understanding by Generative Pre-Training (GPT) — Radford et al. | 2018 | 单向 CLM 预训练 + 微调，证明生成式预训练也有效 | ⭐⭐⭐ | Transformer | Ch36, Ch40 |
| 8 | Language Models are Unsupervised Multitask Learners (GPT-2) — Radford et al. | 2019 | 扩大模型+数据，零样本学习涌现，预示 scaling law | ⭐⭐⭐ | GPT-1 | Ch36, Ch41 |
| 9 | Language Models are Few-Shot Learners (GPT-3) — Brown et al. | 2020 | 1750 亿参数，in-context learning 涌现，确立 scaling law | ⭐⭐⭐⭐ | GPT-2 | Ch41 |
| 10 | Deep Residual Learning for Image Recognition (ResNet) — He et al. | 2016 | 残差连接 `y=F(x)+x`，让上百层网络可训练 | ⭐⭐ | 反向传播、梯度消失 | Ch32 |
| 11 | Batch Normalization — Ioffe & Szegedy | 2015 | 批归一化，让深层网络训练更稳定，加速收敛 | ⭐⭐ | 前向传播 | Ch16, Ch32 |
| 12 | Layer Normalization — Ba et al. | 2016 | 层归一化，对 RNN/Transformer 友好的归一化方式 | ⭐⭐ | BatchNorm | Ch32 |
| 13 | Generative Adversarial Networks — Goodfellow et al. | 2014 | GAN：生成器与判别器对抗训练 | ⭐⭐⭐⭐ | 概率论、神经网络 | Ch38 |
| 14 | Auto-Encoding Variational Bayes (VAE) — Kingma & Welling | 2013 | 变分自编码器，重参数化技巧，ELBO 优化 | ⭐⭐⭐⭐⭐ | 概率论、贝叶斯 | Ch38 |
| 15 | Denoising Diffusion Probabilistic Models (DDPM) — Ho et al. | 2020 | 扩散模型：加噪去噪生成图像，Stable Diffusion 的基础 | ⭐⭐⭐⭐⭐ | VAE、马尔可夫链 | Ch38 |
| 16 | High-Resolution Image Synthesis with Latent Diffusion Models (Stable Diffusion) — Rombach et al. | 2022 | 潜在空间扩散，把扩散搬到低维 latent space，大幅降算力 | ⭐⭐⭐⭐ | DDPM、VAE | Ch38 |

---

## 五、按主题分类的论文清单

### 5.1 RNN 与序列建模主线

| 论文 | 年份 | 一句话总结 |
|------|------|-----------|
| Bengio 1994 | 1994 | 证明梯度消失是 RNN 长依赖的本质障碍 |
| Hochreiter & Schmidhuber (LSTM) | 1997 | 用门控解决梯度消失 |
| Cho et al. (GRU) | 2014 | 简化 LSTM，合并门为更新门和重置门 |
| Sutskever et al. (Seq2Seq) | 2014 | Encoder-Decoder 范式 |
| Bahdanau et al. (Attention) | 2014 | 让 Decoder 动态关注 Encoder |

### 5.2 Transformer 主线

| 论文 | 年份 | 一句话总结 |
|------|------|-----------|
| Vaswani et al. (Transformer) | 2017 | Attention is all you need |
| Devlin et al. (BERT) | 2018 | 双向预训练 + 微调 |
| Radford et al. (GPT) | 2018 | 单向预训练 + 微调 |
| Radford et al. (GPT-2) | 2019 | 零样本涌现 |
| Brown et al. (GPT-3) | 2020 | 少样本涌现 + scaling law |
| Hoffmann et al. (Chinchilla) | 2022 | 修正 scaling law：数据与模型应等比放大 |

### 5.3 训练与归一化

| 论文 | 年份 | 一句话总结 |
|------|------|-----------|
| He et al. (ResNet) | 2016 | 残差连接让深层网络可训练 |
| Ioffe & Szegedy (BatchNorm) | 2015 | 批归一化 |
| Ba et al. (LayerNorm) | 2016 | 层归一化 |
| Srivastava et al. (Dropout) | 2014 | 随机丢弃防过拟合 |
| Kingma & Ba (Adam) | 2014 | 自适应矩估计优化器 |

### 5.4 生成模型

| 论文 | 年份 | 一句话总结 |
|------|------|-----------|
| Goodfellow et al. (GAN) | 2014 | 对抗训练生成 |
| Kingma & Welling (VAE) | 2013 | 变分推断生成 |
| Ho et al. (DDPM) | 2020 | 扩散模型 |
| Rombach et al. (Latent Diffusion / Stable Diffusion) | 2022 | 潜在空间扩散 |

### 5.5 大模型与下游应用

| 论文 | 年份 | 一句话总结 |
|------|------|-----------|
| Raffel et al. (T5) | 2019 | text-to-text 统一框架 |
| Lewis et al. (BART) | 2019 | 去噪自编码器预训练 |
| Lewis et al. (RAG) | 2020 | 检索增强生成 |
| Ouyang et al. (InstructGPT) | 2022 | RLHF 对齐语言模型 |
| Touvron et al. (LLaMA) | 2023 | 开源高效小参数大模型 |

---

## 六、阅读论文的工具与资源

### 6.1 找论文

| 平台 | 用途 |
|------|------|
| [arXiv](https://arxiv.org/) | 预印本，AI 论文几乎都先发这里 |
| [Papers With Code](https://paperswithcode.com/) | 论文 + 代码 + 排行榜，强烈推荐 |
| [Semantic Scholar](https://www.semanticscholar.org/) | 学术搜索，可看引用关系 |
| [Connected Papers](https://www.connectedpapers.com/) | 可视化论文引用关系图 |
| [Google Scholar](https://scholar.google.com/) | 通用学术搜索 |

### 6.2 读论文

| 工具 | 用途 |
|------|------|
| [arxiv-vanity](https://www.arxiv-vanity.com/) | 把 arXiv 论文渲染成网页，公式图表更清晰 |
| [ar5iv](https://ar5iv.labs.arxiv.org/) | 同上，HTML 版 arXiv |
| Notion / Obsidian | 整理笔记、双链引用 |
| Zotero | 论文管理与引用 |

### 6.3 看论文讲解

| 资源 | 说明 |
|------|------|
| 李沐《论文精读》系列（B 站） | 中文最好，每篇 30~60 分钟逐段讲 |
| Yannic Kilcher（YouTube） | 英文，新论文速读 |
| AI-Scholar / 机器之心 | 中文综述博客 |

---

## 七、复现论文的推荐项目

读第三遍时跟着开源实现对照最有效。

| 论文 | 推荐复现项目 | 难度 |
|------|--------------|------|
| Transformer | [The Annotated Transformer](http://nlp.seas.harvard.edu/annotated-transformer/)（Harvard NLP） | ⭐⭐ |
| GPT-2 | [nanoGPT](https://github.com/karpathy/nanoGPT)（Karpathy） | ⭐⭐ |
| BERT | [annotated BERT](https://nlp.seas.harvard.edu/2018/12/28/) | ⭐⭐⭐ |
| LSTM | 自己用 NumPy 写（教程 Ch23-Ch26 已覆盖） | ⭐⭐ |
| Diffusion | [annotated diffusion](https://huggingface.co/blog/annotated-diffusion)（HuggingFace） | ⭐⭐⭐ |

---

## 八、阅读路径建议

根据你的目标选不同路径：

### 路径 A：理解 Transformer（对应教程主线）

```
Bengio 1994 → LSTM 1997 → Seq2Seq 2014 → Bahdanau Attention 2014
                                                              ↓
                                                  Transformer 2017
                                                              ↓
                                              BERT 2018 / GPT 2018
                                                              ↓
                                                       GPT-2 / GPT-3
```

### 路径 B：理解生成模型（对应 Ch38）

```
GAN 2014 → VAE 2013 → DDPM 2020 → Latent Diffusion 2022
```

### 路径 C：理解训练技巧（对应 Ch16, Ch32）

```
Dropout 2014 → BatchNorm 2015 → ResNet 2016 → LayerNorm 2016 → Adam 2014
```

### 路径 D：跟进大模型前沿（对应 Ch41）

```
GPT-3 2020 → InstructGPT 2022 (RLHF) → Chinchilla 2022 (scaling law) → LLaMA 2023
```

---

## 九、避坑提示

| 坑 | 提醒 |
|----|------|
| 一上来就读第三遍 | 99% 的论文第二遍就够了，别浪费时间 |
| 字字死磕相关工作 | "相关工作"部分通常写给审稿人看的，跳过不影响理解 |
| 不看图只看公式 | 架构图往往比公式更传递核心思想，先看图再看公式 |
| 跳过实验直接看方法 | 实验告诉你"这方法在什么场景有效"，是判断能否用在自己任务上的关键 |
| 信论文的 SOTA | 论文常挑对自己有利的 baseline 和指标，看相对提升而非绝对数 |
| 不复现就声称看懂了 | 第三遍复现才能发现"我以为懂了但其实没懂"的盲点 |
| 追新不追经典 | 经典论文经过时间检验，新论文很多会被遗忘。先读经典再追新 |
| 只读不写笔记 | 一周后忘光。每篇论文至少记下"痛点—招式—证据"三句话 |

---

## 十、配套教程章节对照表

| 教程章节 | 推荐配套论文 |
|----------|--------------|
| Ch21 RNN 梯度问题 | Bengio 1994 |
| Ch23-Ch26 LSTM/GRU | LSTM 1997, GRU 2014 |
| Ch27 Seq2Seq | Sutskever 2014 |
| Ch28 Attention | Bahdanau 2014 |
| Ch29-Ch35 Transformer | Vaswani 2017 |
| Ch32 残差与 LN | ResNet 2016, LayerNorm 2016 |
| Ch36, Ch40 BERT/GPT | BERT 2018, GPT-1 2018, GPT-2 2019 |
| Ch38 生成模型 | GAN 2014, VAE 2013, DDPM 2020, LDM 2022 |
| Ch41 大模型前沿 | GPT-3 2020, InstructGPT 2022, Chinchilla 2022 |

---

## 十一、延伸资源

### 11.1 综述论文

- **A Survey of Transformers**（Lin et al., 2021）：Transformer 变体全景
- **Challenges and Applications of Large Language Models**（2023）
- **The Illustrated Transformer**（Jay Alammar，博客）：图解 Transformer，入门首选

### 11.2 经典教材

- **《深度学习》**（花书，Goodfellow）：理论基础
- **《动手学深度学习》**（李沐）：实战入门，配套代码
- **《神经网络与深度学习》**（邱锡鹏）：中文教材
- **《Natural Language Processing with Transformers》**（HuggingFace 团队）：预训练模型实战

### 11.3 公开课

- **Stanford CS224N**（NLP with Deep Learning）
- **Stanford CS231N**（CV with Deep Learning）
- **李沐《论文精读》系列**（B 站，免费）
- **HuggingFace NLP Course**（免费）
- **fast.ai Practical Deep Learning**

### 11.4 社区

- **HuggingFace**：模型与数据集
- **Papers With Code**：论文 + 代码 + 排行榜
- **GitHub**：开源项目
- **知乎 / 掘金**：中文社区
- **arXiv**：最新论文

---

## 十二、一个完整的"读论文"工作流示例

以 **Attention Is All You Need** 为例：

**第一遍（10 分钟）**：
- 标题/摘要：提出 Transformer，纯 attention，不用 RNN/CNN，可并行，WMT 翻译 SOTA。
- 看图 1（架构图）、图 2（注意力可视化）。
- 结论：值得读第二遍。

**第二遍（45 分钟）**：
- 读第 3 节（Model Architecture），理解 Encoder/Decoder 堆叠、Multi-Head、PE。
- 读第 5 节（实验），看 WMT EnDe/EnFr 的 BLEU。
- 标记不懂：为什么要除 √d_k？为什么 PE 用 sin/cos？留到第三遍或查博客。

**第三遍（按需，数小时）**：
- 跟着 The Annotated Transformer 用 PyTorch 复现一遍。
- 自己跑一个小翻译任务。
- 思考：为什么作者选了 Post-LN 而不是 Pre-LN？

**记笔记（3 句话）**：
- 痛点：RNN 难以并行训练，长序列梯度问题严重。
- 招式：用 Self-Attention 替代循环，每层所有位置直接相连；多头并行捕获不同模式。
- 证据：WMT EnDe BLEU 28.4，比当时最好的 RNN 系统高 2 分，且训练时间大幅缩短。

---

> 上一附录：[附录 D · 术语表](附录D-术语表.md)  ｜  返回：[00 · 开篇为什么写这份教程](00-开篇为什么写这份教程.md)

> 本附录基于 `ml_rnn_lstm_transformer_detailed_outline.md` 附录 E 部分扩展整理。论文年份与作者以原论文为准。
