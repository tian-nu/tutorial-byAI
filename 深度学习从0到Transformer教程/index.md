# 从0到Transformer — 深度学习教程总导航

> 从"什么是矩阵"到"手搓Transformer"，一条零基础可跟随的完整路径。

---

## 教程概览

| 项目 | 内容 |
|------|------|
| 章节数 | 41章（Ch00-Ch41）+ 5附录 |
| 可视化 | 20个自包含HTML动画 |
| 代码文件 | 41个可运行Python脚本 |
| 主线语言 | Python（NumPy手写 → PyTorch实战） |
| 读者基础 | 会任意编程语言，数学高中水平即可 |
| 核心框架 | 五维度：为了什么 / 要做到 / 做了什么 / 怎么算 / 怎么用 |

---

## 学习路线图

```
第零篇 地基篇（数学+环境）
  Ch00 开篇 → Ch01 线性代数 → Ch02 微积分 → Ch03 概率论 → Ch04 环境搭建
      │
      ▼
第一篇 机器学习入门
  Ch05 什么是ML → Ch06 线性回归 → Ch07 梯度下降 → Ch08 逻辑回归 → Ch09 过拟合 → Ch10 Titanic项目
      │
      ▼
第二篇 神经网络
  Ch11 感知机 → Ch12 激活函数 → Ch13 MLP → Ch14 前向传播 → Ch15 反向传播 → Ch16 训练技巧
      │
      ▼
第三篇 RNN（序列建模的尝试）
  Ch17 为什么需要RNN → Ch18 结构与展开 → Ch19 前向传播 → Ch20 BPTT → Ch21 梯度消失
      │
      ▼
第四篇 LSTM（长依赖的解药）
  Ch22 为什么记不住 → Ch23 门控思想 → Ch24 三个门 → Ch25 前向完整推导 → Ch26 反向+GRU
      │
      ▼
第五篇 Attention与Transformer（革命）
  Ch27 Seq2Seq → Ch28 Attention → Ch29 Self-Attention → Ch30 Multi-Head → Ch31 位置编码
      → Ch32 LayerNorm+残差 → Ch33 FFN+Encoder → Ch34 Decoder+Mask → Ch35 完整拼装 → Ch36 BERT/GPT
      │
      ▼
第六篇 其他重要架构简介
  Ch37 CNN简介 → Ch38 生成模型简介（VAE/GAN/Diffusion）
      │
      ▼
第七篇 实战与展望
  Ch39 文本分类实战 → Ch40 HuggingFace实战 → Ch41 学习路线图
```

---

## 推荐暂停点

| 标记 | 位置 | 恢复验证 |
|------|------|---------|
| 0/7 | Ch00结束 | 能说出五维度框架 |
| 1/7 | 第一篇结束 | `python -c "import numpy; print(numpy.__version__)"` |
| 2/7 | 第二篇结束 | 能解释反向传播链式法则 |
| 3/7 | 第三篇结束 | 能解释RNN为什么梯度消失 |
| 4/7 | 第四篇结束 | 能手推LSTM前向传播 |
| 5/7 | 第五篇结束 | 能画出Transformer完整结构图 |
| 6/7 | 第六篇结束 | `python -c "import torch; print(torch.nn.Conv2d(3,16,3))"` |
| 7/7 | 全教程结束 | 恭喜你完成了从0到Transformer的旅程 |

---

## 完整章节目录

### 第零篇：地基篇 — 数学与环境（5章）

| 章 | 标题 | 可视化 | 代码 |
|----|------|--------|------|
| 00 | [开篇为什么写这份教程](00-开篇为什么写这份教程.md) | - | - |
| 01 | [线性代数最小必要知识](01-线性代数最小必要知识.md) | - | [ch01](code/ch01_linear_algebra_basics.py) |
| 02 | [微积分最小必要知识](02-微积分最小必要知识.md) | - | [ch02](code/ch02_calculus_basics.py) |
| 03 | [概率论最小必要知识](03-概率论最小必要知识.md) | - | [ch03](code/ch03_probability_basics.py) |
| 04 | [Python与NumPy环境搭建](04-Python与NumPy环境搭建.md) | - | [ch04](code/ch04_numpy_cheatsheet.py) |

### 第一篇：机器学习入门（6章）

| 章 | 标题 | 可视化 | 代码 |
|----|------|--------|------|
| 05 | [什么是机器学习](05-什么是机器学习.md) | - | [ch05](code/ch05_what_is_ml.py) |
| 06 | [线性回归最简单的ML](06-线性回归最简单的ML.md) | - | [ch06](code/ch06_linear_regression.py) |
| 07 | [梯度下降最核心的优化思想](07-梯度下降最核心的优化思想.md) | [梯度下降](07_linear_regression_gd_visual.html) | [ch07](code/ch07_gradient_descent.py) |
| 08 | [逻辑回归分类问题入门](08-逻辑回归分类问题入门.md) | [Softmax交叉熵](08_softmax_cross_entropy_visual.html) | [ch08](code/ch08_logistic_regression.py) |
| 09 | [过拟合与正则化](09-过拟合与正则化.md) | [过拟合](09_overfitting_regularization_visual.html) | [ch09](code/ch09_overfitting_regularization.py) |
| 10 | [第一个完整ML项目](10-第一个完整ML项目.md) | - | [ch10](code/ch10_titanic_project.py) |

### 第二篇：神经网络（6章）

| 章 | 标题 | 可视化 | 代码 |
|----|------|--------|------|
| 11 | [感知机最简单的神经元](11-感知机最简单的神经元.md) | [感知机](11_perceptron_visual.html) | [ch11](code/ch11_perceptron.py) |
| 12 | [激活函数家族](12-激活函数家族.md) | [激活函数](12_activation_functions_visual.html) | [ch12](code/ch12_activation_functions.py) |
| 13 | [多层感知机MLP](13-多层感知机MLP.md) | - | [ch13](code/ch13_mlp_xor.py) |
| 14 | [前向传播信号从前往后走](14-前向传播信号从前往后走.md) | [前向传播](14_forward_propagation_visual.html) | [ch14](code/ch14_forward_propagation.py) |
| 15 | [反向传播误差从后往前传](15-反向传播误差从后往前传.md) | [反向传播](15_backpropagation_visual.html) · [计算图](15_computational_graph_autodiff_visual.html) | [ch15](code/ch15_backpropagation.py) |
| 16 | [训练技巧让网络真的学得动](16-训练技巧让网络真的学得动.md) | [优化器对比](16_optimizers_comparison_visual.html) | [ch16](code/ch16_training_tricks.py) |

### 第三篇：RNN — 处理序列的尝试（5章）

| 章 | 标题 | 可视化 | 代码 |
|----|------|--------|------|
| 17 | [为什么需要RNN序列数据的挑战](17-为什么需要RNN序列数据的挑战.md) | - | [ch17](code/ch17_sequence_intro.py) |
| 18 | [RNN的结构与展开](18-RNN的结构与展开.md) | [RNN展开](18_rnn_unfold_visual.html) | [ch18](code/ch18_rnn_structure.py) |
| 19 | [RNN前向传播](19-RNN前向传播.md) | - | [ch19](code/ch19_rnn_forward.py) |
| 20 | [RNN反向传播BPTT](20-RNN反向传播BPTT.md) | - | [ch20](code/ch20_rnn_bptt.py) |
| 21 | [RNN的致命问题梯度消失与爆炸](21-RNN的致命问题梯度消失与爆炸.md) | [梯度消失爆炸](21_rnn_bptt_gradient_visual.html) | [ch21](code/ch21_gradient_clipping.py) |

### 第四篇：LSTM — 长依赖的解药（5章）

| 章 | 标题 | 可视化 | 代码 |
|----|------|--------|------|
| 22 | [为什么RNN记不住长序列](22-为什么RNN记不住长序列.md) | - | [ch22](code/ch22_rnn_long_dependency.py) |
| 23 | [LSTM的核心思想门控](23-LSTM的核心思想门控.md) | - | [ch23](code/ch23_lstm_gate_idea.py) |
| 24 | [LSTM的三个门与细胞状态](24-LSTM的三个门与细胞状态.md) | [LSTM三门](24_lstm_gates_visual.html) | [ch24](code/ch24_lstm_gates_forward.py) |
| 25 | [LSTM前向传播完整推导](25-LSTM前向传播完整推导.md) | [LSTM vs RNN记忆](25_lstm_vs_rnn_memory_visual.html) | [ch25](code/ch25_lstm_forward_full.py) |
| 26 | [LSTM反向传播与GRU变体](26-LSTM反向传播与GRU变体.md) | - | [ch26](code/ch26_lstm_backward_gru.py) |

### 第五篇：Attention与Transformer — 革命（10章）

| 章 | 标题 | 可视化 | 代码 |
|----|------|--------|------|
| 27 | [Seq2Seq与编码器解码器架构](27-Seq2Seq与编码器解码器架构.md) | - | [ch27](code/ch27_seq2seq.py) |
| 28 | [Attention机制让模型学会看哪里](28-Attention机制让模型学会看哪里.md) | [Attention热力图](28_attention_weights_visual.html) | [ch28](code/ch28_attention.py) |
| 29 | [Self-Attention自己关注自己](29-Self-Attention自己关注自己.md) | [Self-Attention计算](29_self_attention_visual.html) | [ch29](code/ch29_self_attention.py) |
| 30 | [Multi-Head-Attention多角度关注](30-Multi-Head-Attention多角度关注.md) | [多头并行](30_multi_head_attention_visual.html) | [ch30](code/ch30_multi_head_attention.py) |
| 31 | [Positional-Encoding给序列加位置感](31-Positional-Encoding给序列加位置感.md) | [位置编码](31_positional_encoding_visual.html) | [ch31](code/ch31_positional_encoding.py) |
| 32 | [LayerNorm与残差连接](32-LayerNorm与残差连接.md) | - | [ch32](code/ch32_layer_norm_residual.py) |
| 33 | [前馈网络与完整Encoder块](33-前馈网络与完整Encoder块.md) | - | [ch33](code/ch33_ffn_encoder_block.py) |
| 34 | [Decoder块与Masked-Attention](34-Decoder块与Masked-Attention.md) | - | [ch34](code/ch34_decoder_block_mask.py) |
| 35 | [完整Transformer拼装与训练](35-完整Transformer拼装与训练.md) | [Transformer架构](35_transformer_architecture_visual.html) | [ch35](code/ch35_full_transformer.py) |
| 36 | [从Transformer到BERT-GPT](36-从Transformer到BERT-GPT.md) | - | [ch36](code/ch36_bert_gpt_huggingface.py) |

### 第六篇：其他重要架构简介（2章）

| 章 | 标题 | 可视化 | 代码 |
|----|------|--------|------|
| 37 | [CNN简介处理图像的另一条路](37-CNN简介处理图像的另一条路.md) | [CNN卷积池化](37_cnn_conv_pool_visual.html) | [ch37](code/ch37_cnn_basics.py) |
| 38 | [生成模型简介VAE-GAN-Diffusion](38-生成模型简介VAE-GAN-Diffusion.md) | [Diffusion去噪](38_diffusion_process_visual.html) | [ch38](code/ch38_diffusion_demo.py) |

### 第七篇：实战与展望（3章）

| 章 | 标题 | 可视化 | 代码 |
|----|------|--------|------|
| 39 | [实战一用PyTorch训练文本分类模型](39-实战一用PyTorch训练文本分类模型.md) | - | [ch39](code/ch39_text_classification.py) |
| 40 | [实战二用HuggingFace玩转预训练模型](40-实战二用HuggingFace玩转预训练模型.md) | - | [ch40](code/ch40_huggingface.py) |
| 41 | [下一步去哪学习路线图](41-下一步去哪学习路线图.md) | - | - |

### 附录

| 附录 | 标题 |
|------|------|
| A | [数学符号速查](附录A-数学符号速查.md) |
| B | [NumPy/PyTorch速查](附录B-NumPy_PyTorch速查.md) |
| C | [常见错误与排错指南](附录C-常见错误与排错指南.md) |
| D | [术语表](附录D-术语表.md) |
| E | [论文阅读指南](附录E-论文阅读指南.md) |

---

## 可视化动画总览（20个）

| # | 文件 | 对应章节 | 类型 |
|---|------|---------|------|
| 1 | [梯度下降](07_linear_regression_gd_visual.html) | Ch07 | 优化过程 |
| 2 | [Softmax交叉熵](08_softmax_cross_entropy_visual.html) | Ch08 | 概率变换 |
| 3 | [过拟合与正则化](09_overfitting_regularization_visual.html) | Ch09 | 模型对比 |
| 4 | [感知机](11_perceptron_visual.html) | Ch11 | 决策边界 |
| 5 | [激活函数](12_activation_functions_visual.html) | Ch12 | 函数曲线 |
| 6 | [前向传播](14_forward_propagation_visual.html) | Ch14 | 信号流动 |
| 7 | [反向传播](15_backpropagation_visual.html) | Ch15 | 梯度流动 |
| 8 | [计算图自动微分](15_computational_graph_autodiff_visual.html) | Ch15 | 链式法则 |
| 9 | [优化器对比](16_optimizers_comparison_visual.html) | Ch16 | 优化轨迹 |
| 10 | [RNN展开](18_rnn_unfold_visual.html) | Ch18 | 时间展开 |
| 11 | [梯度消失爆炸](21_rnn_bptt_gradient_visual.html) | Ch21 | 梯度分析 |
| 12 | [LSTM三门](24_lstm_gates_visual.html) | Ch24 | 门控机制 |
| 13 | [LSTM vs RNN记忆](25_lstm_vs_rnn_memory_visual.html) | Ch25 | 记忆对比 |
| 14 | [Attention热力图](28_attention_weights_visual.html) | Ch28 | 权重可视化 |
| 15 | [Self-Attention计算](29_self_attention_visual.html) | Ch29 | 矩阵运算 |
| 16 | [多头并行](30_multi_head_attention_visual.html) | Ch30 | 多头视角 |
| 17 | [位置编码](31_positional_encoding_visual.html) | Ch31 | 编码矩阵 |
| 18 | [Transformer架构](35_transformer_architecture_visual.html) | Ch35 | 数据流 |
| 19 | [CNN卷积池化](37_cnn_conv_pool_visual.html) | Ch37 | 卷积滑动 |
| 20 | [Diffusion去噪](38_diffusion_process_visual.html) | Ch38 | 加噪去噪 |

---

## 环境准备

```bash
# Python 3.9+
python -m venv .venv

# Windows
.venv\Scripts\activate
# Mac/Linux
source .venv/bin/activate

# 安装依赖
pip install numpy matplotlib scikit-learn pandas
pip install torch --index-url https://download.pytorch.org/whl/cpu
pip install transformers datasets
```

---

> 开始学习：[Ch00 · 开篇为什么写这份教程](00-开篇为什么写这份教程.md)
