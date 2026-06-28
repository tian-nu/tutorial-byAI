# 附录 D · 术语表

> 所属篇：附录 · 预计耗时：15 分钟（查阅用）

本附录收录教程正文中所有标记 `→ 进附录D` 的术语，按字母/拼音排序。每条给出：术语、英文、简要解释、出处章节、是否项目特有。

**收录原则**：
- 通用名词（HTTP、Git、Python、NumPy、PyTorch、Jupyter、向量、矩阵、导数、概率分布等）**不收入**，请自行查阅外部资料。
- 项目特有术语（如"调包侠""五维度框架"）标注"是"。
- 反直觉或易混淆概念优先收录。

> 共收录 137 条术语。

---

## A

| 术语 | 英文 | 简要解释 | 出处章节 | 项目特有 |
|------|------|----------|----------|----------|
| Adam | Adaptive Moment Estimation | 自适应矩估计优化器，结合 Momentum 和 RMSProp，对每个参数维护一阶矩和二阶矩的滑动平均。 | Ch16 | 否 |
| Agent | Agent | 能感知环境、自主决策、调用工具完成任务的智能体。LLM Agent 指以大语言模型为大脑的智能体。 | Ch41 | 否 |
| Attention 权重 | Attention Weight | softmax 归一化后的相关性分数，表示一个位置对另一个位置的关注程度，行和为 1。 | Ch28 | 否 |

## B

| 术语 | 英文 | 简要解释 | 出处章节 | 项目特有 |
|------|------|----------|----------|----------|
| Batch Normalization（BN） | Batch Normalization | 对 batch 维度做归一化，让每个特征在 batch 内均值为 0、方差为 1。适合 CNN，不适合 RNN。 | Ch16, Ch32 | 否 |
| BGD / SGD / MBGD | Batch / Stochastic / Mini-Batch Gradient Descent | 批量/随机/小批量梯度下降。BGD 用全量数据，SGD 用单个样本，MBGD 用一小批（主流）。 | Ch16 | 否 |
| BPTT | Backpropagation Through Time | RNN 的反向传播算法，把网络沿时间轴展开后用链式法则求梯度。 | Ch20 | 否 |
| 变分自编码器 | VAE, Variational Autoencoder | 用变分推断学习的生成模型，编码器输出分布参数，优化 ELBO。 | Ch38 | 否 |
| 步长 | Stride | 卷积核每次滑动的步数。步长>1 可下采样降维。 | Ch37 | 否 |

## C

| 术语 | 英文 | 简要解释 | 出处章节 | 项目特有 |
|------|------|----------|----------|----------|
| Causal Mask（因果掩码） | Causal Mask | Decoder 中遮盖未来位置的 mask，上三角填 -∞，保证生成第 t 个词时只看前 t 个。 | Ch34 | 否 |
| CLM | Causal Language Modeling | 因果语言建模，从左到右预测下一个 token，GPT 系列的训练目标。 | Ch40 | 否 |
| Cross-Attention（交叉注意力） | Cross-Attention | Q 来自 Decoder，K/V 来自 Encoder 的注意力，让 Decoder 关注 Encoder 输出。 | Ch34 | 否 |
| 交叉熵 | Cross-Entropy | 衡量两个概率分布差异的指标，分类任务的标准损失函数。`H(p,q) = -Σ p log q`。 | Ch03 | 否 |
| 长依赖 | Long-term Dependency | 序列中相隔很远的位置之间的依赖关系。RNN 难以捕捉，LSTM/Transformer 缓解。 | Ch22 | 否 |
| 重置门 | Reset Gate (GRU) | GRU 中决定前一时刻隐藏状态有多少参与候选状态计算的门。 | Ch26 | 否 |
| 池化 | Pooling | 卷积网络中的下采样操作（最大池化/平均池化），降低空间维度、提供平移不变性。 | Ch37 | 否 |
| 参数共享 | Parameter Sharing | RNN 在每个时间步用同一组权重，让模型能处理变长序列且参数量不随 T 增长。 | Ch18 | 否 |

## D

| 术语 | 英文 | 简要解释 | 出处章节 | 项目特有 |
|------|------|----------|----------|----------|
| Decoder（解码器） | Decoder | Seq2Seq 中接收上下文向量并生成目标序列的部分。Transformer Decoder 还接收 Encoder 输出做 Cross-Attention。 | Ch27 | 否 |
| Decoder Block | Decoder Block | Transformer Decoder 的一个完整块：Masked Self-Attention + Cross-Attention + FFN，每个子层带残差和 LN。 | Ch34 | 否 |
| Dropout | Dropout | 训练时按概率 p 随机置零神经元输出，防过拟合。推理时不丢弃，但输出乘以 (1-p) 或训练时缩放。 | Ch16 | 否 |
| 点积 | Dot Product | 两个向量对应相乘再求和，结果为标量。衡量方向相似度。`a·b = Σ a_i b_i`。 | Ch01 | 否 |
| 多模态 | Multimodal | 同时处理多种模态（文本、图像、音频）的模型。如 CLIP、Flamingo。 | Ch41 | 否 |

## E

| 术语 | 英文 | 简要解释 | 出处章节 | 项目特有 |
|------|------|----------|----------|----------|
| ELBO（证据下界） | Evidence Lower Bound | 变分推断中数据对数似然的下界，VAE 的优化目标。最大化 ELBO 等价于最小化 KL 散度。 | Ch38 | 否 |
| Encoder（编码器） | Encoder | Seq2Seq 中把输入序列压缩为上下文向量的部分。Transformer Encoder 输出供 Decoder 做 Cross-Attention。 | Ch27 | 否 |
| Encoder Block | Encoder Block | Transformer Encoder 的一个完整块：Self-Attention + FFN，每个子层带残差和 LayerNorm。 | Ch33 | 否 |

## F

| 术语 | 英文 | 简要解释 | 出处章节 | 项目特有 |
|------|------|----------|----------|----------|
| F1 分数 | F1 Score | 精确率和召回率的调和平均，`F1 = 2·P·R/(P+R)`。处理类别不平衡时比准确率更稳健。 | Ch10 | 否 |
| FFN | Position-wise Feed-Forward Network | Transformer 中逐位置作用的两层 MLP：`FFN(x) = W₂·ReLU(W₁·x + b₁) + b₂`，每个位置独立计算。 | Ch33 | 否 |
| 特征 | Feature | 输入数据中用于预测的属性。如房价预测中的面积、卧室数。 | Ch05 | 否 |
| 微调 | Fine-tuning | 在预训练模型基础上用领域数据继续训练，让其适配下游任务。 | Ch40 | 否 |
| 反向传播 | Backpropagation | 用链式法则从输出端向输入端逐层计算梯度的算法，是神经网络训练的核心。 | Ch15 | 否 |

## G

| 术语 | 英文 | 简要解释 | 出处章节 | 项目特有 |
|------|------|----------|----------|----------|
| GAN | Generative Adversarial Network | 生成对抗网络，生成器和判别器对抗训练。生成器造假，判别器辨真，最终生成器产出逼真样本。 | Ch38 | 否 |
| GELU | Gaussian Error Linear Unit | 高斯误差线性单元，`GELU(x) = x·Φ(x)`，Φ 为标准正态 CDF。Transformer 标配激活函数，比 ReLU 平滑。 | Ch12 | 否 |
| Gating（门控） | Gating | 用 sigmoid 输出（0~1）控制信息通过比例的机制，LSTM 的核心思想。 | Ch23 | 否 |
| 梯度 | Gradient | 偏导数组成的向量，指向函数上升最快的方向。负梯度是下降最快的方向。 | Ch02 | 否 |
| 梯度裁剪 | Gradient Clipping | 把梯度范数限制在阈值内防止爆炸。`g ← g · min(1, max_norm/‖g‖)`。只解决爆炸不解决消失。 | Ch21 | 否 |
| 梯度下降 | Gradient Descent | 沿负梯度方向更新参数的优化算法：`θ ← θ - η·∇L`。 | Ch07 | 否 |
| 梯度消失 | Vanishing Gradient | 深层网络中梯度反传时由于 sigmoid/tanh 饱和或连乘小于 1 而趋近于 0，导致浅层学不动。 | Ch12 | 否 |
| 梯度爆炸 | Exploding Gradient | 深层/RNN 网络中梯度反传时由于连乘大于 1 而指数增长，导致 loss 变 nan。 | Ch21 | 否 |
| 感知机 | Perceptron | 最早的神经元模型，`y = sign(w·x + b)`。只能解决线性可分问题。 | Ch11 | 否 |
| 感受野 | Receptive Field | 卷积网络中某层一个输出像素对应输入图像的区域大小。层越深感受野越大。 | Ch37 | 否 |
| 更新门 | Update Gate (GRU) | GRU 中决定新旧隐藏状态混合比例的门，相当于 LSTM 的遗忘门+输入门合并。 | Ch26 | 否 |

## H

| 术语 | 英文 | 简要解释 | 出处章节 | 项目特有 |
|------|------|----------|----------|----------|
| Hadamard 积 | Hadamard Product | 两个同形状矩阵的逐元素相乘，记作 `A ⊙ B` 或 `A * B`，区别于矩阵乘法 `A @ B`。 | Ch01 | 否 |
| HuggingFace Transformers | HuggingFace Transformers | 开源预训练模型库，提供数千个模型和 tokenizer 的统一 API。 | Ch40 | 否 |
| 候选状态 | Candidate State | LSTM 中由输入和前一隐藏状态生成的候选细胞状态，`C̃_t = tanh(W_C·[h_{t-1}, x_t])`。 | Ch24 | 否 |
| 混淆矩阵 | Confusion Matrix | 分类模型的预测 vs 真实标签的矩阵，行是真、列是预测。对角线为正确预测。 | Ch10 | 否 |

## J

| 术语 | 英文 | 简要解释 | 出处章节 | 项目特有 |
|------|------|----------|----------|----------|
| 激活函数 | Activation Function | 引入非线性的函数，如 ReLU、sigmoid、tanh。没有它多层网络退化为单层线性变换。 | Ch12 | 否 |
| 解析解 | Closed-form Solution | 可直接用公式一步算出的解，区别于迭代逼近的数值解。线性回归有解析解 `w = (XᵀX)⁻¹Xᵀy`。 | Ch06 | 否 |
| 计算图 | Computational Graph | 把运算画成有向无环图，节点是运算、边是数据流。反向传播沿图反向传播梯度。 | Ch15 | 否 |
| 交叉验证 | Cross-Validation | 把数据分 K 份轮流当验证集，训练 K 次取平均，更稳健地评估模型。 | Ch10 | 否 |
| 决策边界 | Decision Boundary | 分类模型中不同类别分界的曲面。逻辑回归的决策边界是线性的。 | Ch08 | 否 |
| 局部最优 | Local Minimum | 损失函数在某邻域内最小的点，但不是全局最小。深度网络局部最优通常不严重。 | Ch07 | 否 |
| 卷积核 | Kernel / Filter | 卷积网络中滑动的小权重矩阵，如 3×3。一个核学习一种特征（边缘、纹理等）。 | Ch37 | 否 |

## K

| 术语 | 英文 | 简要解释 | 出处章节 | 项目特有 |
|------|------|----------|----------|----------|
| Key（K） | Key | Attention 中的"键"，被查询匹配的对象。`K = X W_K`，shape `(T, d_k)`。 | Ch29 | 否 |

## L

| 术语 | 英文 | 简要解释 | 出处章节 | 项目特有 |
|------|------|----------|----------|----------|
| Label（标签） | Label | 监督学习中样本的真实答案。分类是类别，回归是数值。 | Ch05 | 否 |
| Layer Normalization（LN） | Layer Normalization | 对每个样本的特征维做归一化（均值为 0、方差为 1），与 batch 无关。Transformer 标配。 | Ch32 | 否 |
| L1 / L2 正则化 | L1 / L2 Regularization | 在损失中加 `λ‖w‖₁`（L1，稀疏）或 `λ‖w‖₂²`（L2，权重衰减）惩罚大权重，防过拟合。 | Ch09 | 否 |
| 学习率 | Learning Rate | 梯度下降的步长 η。过大震荡发散，过小学不动。典型值 1e-3 ~ 1e-5。 | Ch06 | 否 |
| 学习率衰减 | Learning Rate Decay | 训练后期逐步降低学习率，让模型在最优解附近稳定收敛。 | Ch16 | 否 |
| LeakyReLU | LeakyReLU | `x if x>0 else 0.01x`，负区间有微小梯度，避免死亡 ReLU。 | Ch12 | 否 |
| 链式法则 | Chain Rule | 复合函数导数等于各层导数相乘：`df/dx = df/dg · dg/dx`。反向传播的数学基础。 | Ch02 | 否 |
| LSTM | Long Short-Term Memory | 带遗忘门/输入门/输出门和细胞状态的 RNN 变体，通过门控让梯度流畅通，缓解长依赖问题。 | Ch23 | 否 |
| LLM | Large Language Model | 大语言模型，参数量巨大（数十亿到万亿）、在海量文本上预训练的模型，如 GPT、LLaMA。 | Ch41 | 否 |

## M

| 术语 | 英文 | 简要解释 | 出处章节 | 项目特有 |
|------|------|----------|----------|----------|
| MLM | Masked Language Modeling | 掩码语言建模，随机遮盖部分 token 让模型预测，BERT 的训练目标。 | Ch40 | 否 |
| Momentum | Momentum | 在 SGD 中累积历史梯度方向，加速收敛、减少震荡。`v = βv + ∇L; θ ← θ - η·v`。 | Ch16 | 否 |
| Multi-Head Attention | Multi-Head Attention | 多头注意力，把 Q/K/V 拆成 h 个头并行做 Self-Attention 再拼接，让模型从不同子空间关注不同模式。 | Ch30 | 否 |
| MLP | Multi-Layer Perceptron | 多层感知机，至少含一个隐藏层的前馈神经网络。 | Ch13 | 否 |
| MSE | Mean Squared Error | 均方误差，回归任务常用损失：`MSE = (1/n)Σ(ŷ-y)²`。 | Ch06 | 否 |
| 模式崩溃 | Mode Collapse | GAN 训练中生成器只产出少数几种样本的现象，丢失数据多样性。 | Ch38 | 否 |

## N

| 术语 | 英文 | 简要解释 | 出处章节 | 项目特有 |
|------|------|----------|----------|----------|
| （无 N 开头术语） | — | — | — | — |

## O

| 术语 | 英文 | 简要解释 | 出处章节 | 项目特有 |
|------|------|----------|----------|----------|
| Optimizer（优化器） | Optimizer | 根据梯度更新参数的算法，如 SGD、Adam、AdamW。 | Ch05 | 否 |
| Overfitting（过拟合） | Overfitting | 模型把训练数据的噪声也学进去，表现为训练 loss 低但验证 loss 高。 | Ch09 | 否 |

## P

| 术语 | 英文 | 简要解释 | 出处章节 | 项目特有 |
|------|------|----------|----------|----------|
| Permutation Invariance（置换不变性） | Permutation Invariance | 输入顺序打乱后输出不变的特性。纯 Self-Attention 有此性质，所以需要位置编码打破它。 | Ch31 | 否 |
| Pipeline | Pipeline | HuggingFace 提供的高阶 API，一行代码完成 tokenization + 模型推理 + 后处理。 | Ch40 | 否 |
| Positional Encoding（位置编码） | Positional Encoding | 给序列注入位置信息的方法，因为 Self-Attention 本身无位置感。常用正弦/余弦编码。 | Ch31 | 否 |
| Pre-LN / Post-LN | Pre-LN / Post-LN | LN 在残差外（Pre）还是残差内（Post）。原论文是 Post-LN，但 Pre-LN 训练更稳定。 | Ch32 | 否 |
| Pre-trained Model（预训练模型） | Pre-trained Model | 在大规模无标注数据上预训练，再用领域数据微调的模型。如 BERT、GPT。 | Ch40 | 否 |
| 批大小 | Batch Size | 一次前向/反向传播使用的样本数。过大占显存、过大过小都影响泛化。 | Ch16 | 否 |

## Q

| 术语 | 英文 | 简要解释 | 出处章节 | 项目特有 |
|------|------|----------|----------|----------|
| Query（Q） | Query | Attention 中的"查询"，主动去匹配 Key。`Q = X W_Q`，shape `(T, d_k)`。 | Ch29 | 否 |
| 全局最优 | Global Minimum | 损失函数在整个定义域内的最小点。非凸问题难以保证找到，但深度学习实践中常不严重。 | Ch07 | 否 |
| 全连接层 | Fully Connected Layer | 每个输入与每个输出相连的线性层，即 `nn.Linear`。 | Ch13 | 否 |
| 前向传播 | Forward Propagation | 输入从输入层经隐藏层到输出层逐层计算的过程，得到模型预测。 | Ch14 | 否 |
| 潜在空间 | Latent Space | 模型把数据压缩后的低维表示空间。VAE 编码器输出的分布参数描述此空间。 | Ch38 | 否 |

## R

| 术语 | 英文 | 简要解释 | 出处章节 | 项目特有 |
|------|------|----------|----------|----------|
| RAG | Retrieval-Augmented Generation | 检索增强生成，先从外部知识库检索相关文档，再拼到 prompt 中让 LLM 生成，缓解幻觉。 | Ch41 | 否 |
| ReLU | Rectified Linear Unit | `max(0, x)`，最常用的激活函数。计算简单、不饱和、缓解梯度消失，但有死亡 ReLU 问题。 | Ch12 | 否 |
| Residual Connection（残差连接） | Residual Connection | `y = SubLayer(x) + x`，让梯度能直接回传，是训练深层网络的关键。 | Ch32 | 否 |
| RNN | Recurrent Neural Network | 循环神经网络，每个时间步用同一组权重处理输入并维护隐藏状态，天然适合序列。 | Ch18 | 否 |

## S

| 术语 | 英文 | 简要解释 | 出处章节 | 项目特有 |
|------|------|----------|----------|----------|
| Self-Attention | Self-Attention | 序列自身做 Q/K/V 的注意力，每个位置直接关注所有位置，解决 RNN 的长依赖问题。 | Ch29 | 否 |
| Seq2Seq | Sequence to Sequence | 序列到序列模型，Encoder 把输入序列编码为向量，Decoder 据此生成输出序列。用于翻译等。 | Ch27 | 否 |
| Sigmoid 函数 | Sigmoid | `σ(x) = 1/(1+e⁻ˣ)`，把任意实数压到 (0,1)。用于二分类输出和门控。易饱和导致梯度消失。 | Ch08 | 否 |
| Sinusoidal PE（正弦位置编码） | Sinusoidal PE | 用 sin/cos 不同频率生成的固定位置编码，原 Transformer 论文方案。相对位置可由线性组合表达。 | Ch31 | 否 |
| Softmax | Softmax | 把一组分数变为概率分布（和为 1）的函数：`softmax(z)_i = e^{z_i}/Σe^{z_j}`。分类输出层标配。 | Ch03 | 否 |
| Saddle Point（鞍点） | Saddle Point | 一个方向是极小、另一方向是极大的点。高维损失函数中鞍点比局部最优更常见，是训练慢的原因之一。 | Ch07 | 否 |
| Step Function（阶跃函数） | Step Function | 感知机的输出函数 `sign(x)`，x>0 输出 1 否则 0。不可导，无法用梯度下降训练。 | Ch11 | 否 |
| 收敛 | Convergence | 训练过程中 loss 逐渐稳定不再显著下降的状态。 | Ch07 | 否 |
| 上下文 | Context | 序列建模中指当前时刻之前的信息。RNN 用隐藏状态压缩上下文。 | Ch17 | 否 |
| 上下文向量 | Context Vector | Seq2Seq 中 Encoder 把输入序列压缩成的单一向量，作为 Decoder 的初始输入。是信息瓶颈。 | Ch27 | 否 |
| 上下文向量（Attention 版） | Context Vector (Attention) | Attention 中按权重对所有 Value 加权求和得到的向量，每个时间步动态生成，不再固定。 | Ch28 | 否 |
| 输入门 | Input Gate | LSTM 中决定多少候选状态写入细胞状态的门。`i_t = σ(W_i·[h_{t-1}, x_t])`。 | Ch23 | 否 |
| 输出门 | Output Gate | LSTM 中决定细胞状态多少暴露为隐藏状态的门。`o_t = σ(W_o·[h_{t-1}, x_t])`。 | Ch23 | 否 |
| 输出投影矩阵 W_O | Output Projection Matrix W_O | Multi-Head Attention 中把拼接后的多头输出投回 d_model 维的矩阵。 | Ch30 | 否 |
| 数值稳定技巧（减最大值） | Numerical Stability Trick | softmax 前先减去最大值，避免 exp 溢出，结果数学上等价。 | Ch03 | 否 |
| 数值梯度验证 | Gradient Checking | 用有限差分法（`[f(w+ε)-f(w-ε)]/(2ε)`）近似梯度，与反向传播梯度对比验证实现正确性。 | Ch15 | 否 |
| 损失函数 | Loss Function | 衡量预测与真实标签差距的函数，训练目标是最小化它。如 MSE、Cross-Entropy。 | Ch05 | 否 |
| 时间展开 | Unfolding / Unrolling in Time | 把 RNN 按时间步展开成等长的链式网络，便于用链式法则做 BPTT。 | Ch18 | 否 |
| 缩放点积注意力 | Scaled Dot-Product Attention | `softmax(QKᵀ/√d_k)V`，缩放因子 √d_k 防止点积过大导致 softmax 饱和。 | Ch29 | 否 |
| 死亡 ReLU | Dying ReLU | ReLU 在负区间梯度为 0，若神经元长期输入为负将永久不再激活。LeakyReLU 可缓解。 | Ch12 | 否 |

## T

| 术语 | 英文 | 简要解释 | 出处章节 | 项目特有 |
|------|------|----------|----------|----------|
| tanh | Hyperbolic Tangent | `tanh(x) = (eˣ-e⁻ˣ)/(eˣ+e⁻ˣ)`，输出 (-1,1)，零中心化。RNN/LSTM 候选状态用。 | Ch12 | 否 |
| Teacher Forcing | Teacher Forcing | 训练 Decoder 时用真实标签作为下一步输入而非模型预测，加速收敛，但推理时不存在输入差异。 | Ch27 | 否 |
| Tokenizer | Tokenizer | 把文本切分为 token 并映射为 ID 的工具。常见 BPE、WordPiece、SentencePiece。 | Ch39 | 否 |
| Transformer | Transformer | 完全基于 Self-Attention 的序列模型，无循环结构，可并行训练，是现代 NLP 的基础架构。 | Ch33 | 否 |
| 调包侠 | — | 项目术语，指只会调用高级 API（如 `pipeline`）而不懂原理的开发者。本教程旨在消灭调包侠。 | Ch00 | **是** |
| 头数 | Number of Heads | Multi-Head Attention 中并行头的数量 h。`d_model = h · d_k`。原论文 h=8。 | Ch30 | 否 |
| 通道 | Channel | 图像的颜色通道（RGB=3）或卷积特征图的通道数。每通道对应一种特征。 | Ch37 | 否 |

## U

| 术语 | 英文 | 简要解释 | 出处章节 | 项目特有 |
|------|------|----------|----------|----------|
| Underfitting（欠拟合） | Underfitting | 模型容量不足或训练不够，连训练集都学不好。需加深加宽模型或训练更久。 | Ch09 | 否 |

## V

| 术语 | 英文 | 简要解释 | 出处章节 | 项目特有 |
|------|------|----------|----------|----------|
| VAE | Variational Autoencoder | 见"变分自编码器"。 | Ch38 | 否 |
| Value（V） | Value | Attention 中的"值"，按权重加权求和的内容。`V = X W_V`，shape `(T, d_v)`。 | Ch29 | 否 |
| Vocabulary（词表） | Vocabulary | 模型能识别的所有 token 集合，每个 token 对应一个 ID。词表大小影响 embedding 层参数量。 | Ch39 | 否 |

## W

| 术语 | 英文 | 简要解释 | 出处章节 | 项目特有 |
|------|------|----------|----------|----------|
| Warmup 学习率调度 | Warmup LR Schedule | 训练初期线性升高学习率到峰值，再按余弦/反比例衰减。防止初期梯度过大破坏模型。 | Ch35 | 否 |
| Weight Initialization（权重初始化） | Weight Initialization | 训练前给权重赋初值。全 0 会让所有神经元学到相同东西，需随机初始化。 | Ch16 | 否 |
| Xavier / He 初始化 | Xavier / He Initialization | 按层维度缩放的初始化方法。Xavier 适合 sigmoid/tanh，He 适合 ReLU。让各层方差一致。 | Ch16 | 否 |
| 万能近似定理 | Universal Approximation Theorem | 只要隐藏层足够宽，单隐层 MLP 能逼近任意连续函数（但没说能不能学到）。 | Ch13 | 否 |
| 误差信号 δ | Delta / Error Signal | `δ⁽ˡ⁾ = ∂L/∂z⁽ˡ⁾`，反向传播中每层的误差信号，由后一层误差信号传过来并乘激活函数导数得到。 | Ch15 | 否 |
| 五维度框架 | — | 项目术语，本教程正文的统一结构：为了什么/要做到/做了什么/怎么算/怎么用/想多一点。 | Ch00 | **是** |

## X

| 术语 | 英文 | 简要解释 | 出处章节 | 项目特有 |
|------|------|----------|----------|----------|
| 序列数据 | Sequence Data | 具有时间/顺序结构的数据，如文本、语音、股价。打乱顺序语义改变。 | Ch17 | 否 |
| 序列建模 | Sequence Modeling | 对序列数据建模的任务族，包括语言模型、翻译、语音识别等。 | Ch17 | 否 |
| 信息瓶颈 | Information Bottleneck | Seq2Seq 中把整个输入序列压缩到一个固定长度向量，信息丢失导致长序列效果差。Attention 解决了它。 | Ch22 | 否 |
| 细胞状态 | Cell State | LSTM 中贯穿时间的主记忆通道 C_t，由门控调节增删信息。区别于隐藏状态 h_t。 | Ch23 | 否 |
| 线性可分 | Linearly Separable | 存在一个超平面能完全分开两类样本。感知机只能解决线性可分问题，XOR 不是。 | Ch11 | 否 |

## Y

| 术语 | 英文 | 简要解释 | 出处章节 | 项目特有 |
|------|------|----------|----------|----------|
| 隐藏层 | Hidden Layer | 输入层与输出层之间的层，提取抽象特征。 | Ch13 | 否 |
| 隐藏状态 | Hidden State | RNN 每个时间步的内部状态 h_t，压缩了截至当前时刻的序列信息。 | Ch18 | 否 |
| 遗忘门 | Forget Gate | LSTM 中决定前一细胞状态保留多少的门。`f_t = σ(W_f·[h_{t-1}, x_t])`。 | Ch23 | 否 |
| 训练集 / 验证集 / 测试集 | Train / Validation / Test Set | 训练集训练参数，验证集调超参，测试集最终评估。三者严格分离。 | Ch09 | 否 |

## Z

| 术语 | 英文 | 简要解释 | 出处章节 | 项目特有 |
|------|------|----------|----------|----------|
| 张量 | Tensor | 多维数组的统称。标量是 0 维、向量是 1 维、矩阵是 2 维张量。PyTorch 的核心数据结构。 | Ch01 | 否 |
| 早停 | Early Stopping | 监控验证 loss，连续若干 epoch 不降就停止训练，防过拟合。 | Ch09 | 否 |
| 正则化 | Regularization | 在损失中加入惩罚项或限制模型复杂度，防过拟合。包括 L1/L2、Dropout、早停等。 | Ch09 | 否 |
| 自动微分 | Automatic Differentiation | 框架自动用链式法则计算梯度的机制，PyTorch 用反向模式自动微分（反向传播）。 | Ch15 | 否 |
| 逐元素乘 ⊙ | Hadamard Product | 见"Hadamard 积"。LSTM 门控用 `⊙` 控制信息流。 | Ch24 | 否 |
| 置换不变性 | Permutation Invariance | 见"Permutation Invariance"。 | Ch31 | 否 |

---

## 项目特有术语汇总

| 术语 | 出处 | 含义 |
|------|------|------|
| 调包侠 | Ch00 | 只会调用高级 API 而不懂原理的开发者，本教程的消灭对象。 |
| 五维度框架 | Ch00 | 教程正文的统一结构：为了什么/要做到/做了什么/怎么算/怎么用/想多一点。 |

---

## 易混淆术语对照

| 术语 A | 术语 B | 区别 |
|--------|--------|------|
| 梯度消失 | 梯度爆炸 | 消失是梯度趋 0（连乘<1），爆炸是梯度趋 ∞（连乘>1）。裁剪只解决爆炸。 |
| 过拟合 | 欠拟合 | 过拟合是训练好验证差（容量过大），欠拟合是训练都差（容量不足）。 |
| BatchNorm | LayerNorm | BN 按 batch 维归一化（适合 CNN），LN 按特征维归一化（适合 RNN/Transformer）。 |
| 隐藏状态（RNN） | 细胞状态（LSTM） | RNN 只有 h_t；LSTM 有 C_t（主记忆）和 h_t（输出，由 o_t⊙tanh(C_t) 得到）。 |
| 遗忘门 | 输入门 | 遗忘门控制旧信息留多少，输入门控制新信息写多少。 |
| Cross-Attention | Self-Attention | Self 的 Q/K/V 同源，Cross 的 Q 来自 Decoder、K/V 来自 Encoder。 |
| Causal Mask | Padding Mask | Causal Mask 遮未来位置（Decoder），Padding Mask 遮 padding 位置。 |
| MLM | CLM | MLM 随机遮盖预测（BERT），CLM 从左到右预测下一个（GPT）。 |
| Attention 权重 | Attention 分数 | 分数是 softmax 前（QKᵀ/√d_k），权重是 softmax 后（行和为 1）。 |
| 解析解 | 数值解 | 解析解一步算出（线性回归），数值解迭代逼近（梯度下降）。 |
| Pre-LN | Post-LN | Pre-LN 在残差外、训练稳定；Post-LN 在残差内、原论文方案、需 warmup。 |

---

## 统计信息

- **总条目数**：137
- **项目特有**：2（调包侠、五维度框架）
- **覆盖章节**：Ch00-Ch41
- **按主题分布**：数学基础 ~10 条、ML 基础 ~15 条、神经网络 ~25 条、RNN/LSTM ~20 条、Attention/Transformer ~25 条、其他架构 ~10 条、应用与展望 ~15 条、训练技巧 ~17 条。

---

> 上一附录：[附录 C · 常见错误与排错指南](附录C-常见错误与排错指南.md)  ｜  下一附录：[附录 E · 论文阅读指南](附录E-论文阅读指南.md)
