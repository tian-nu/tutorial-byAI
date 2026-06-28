# 附录 C · 常见错误与排错指南

> 所属篇：附录 · 预计耗时：10 分钟（查阅用）

本附录汇总教程各章"易错点预警"中的典型错误，按错误类型分类，供排错时查阅。每条给出错误现象、可能原因、解决方法和相关章节。

> 排错通用三步：① 看 shape ② 看 dtype ③ 看 loss 是否在合理范围。

---

## 一、维度错误（Shape Errors）

| 错误现象 | 可能原因 | 解决方法 | 相关章节 |
|----------|----------|----------|----------|
| `ValueError: shapes (3,4) and (3,2) not aligned` | 矩阵乘法内维度不匹配 | 检查 `A.shape[1] == B.shape[0]`，必要时用 `A @ B.T` 或 `A * B` | Ch01 |
| `np.array([1,2,3])` 的 shape 是 `(3,)` 不是 `(3,1)` | 一维数组既非行向量也非列向量 | 用 `a.reshape(3, 1)` 或 `np.array([[1],[2],[3]])` | Ch01 |
| `A * B` 与 `A @ B` 结果完全不同 | 把 Hadamard 积和矩阵乘法搞混 | `*` 是逐元素乘（要求同形状），`@` 是行乘列（要求内维度匹配） | Ch01 |
| 模型输入报"expected 3D got 2D" | 忘记 batch 维度 | RNN/Transformer 输入应为 `(B, T, D)` 而非 `(T, D)`，加 `x.unsqueeze(0)` | Ch19, Ch29 |
| `view` 报错 `view size is not compatible` | 张量非连续（来自 transpose/permute） | 用 `x.reshape(...)` 替代，或先 `.contiguous()` | Ch04 |
| `RuntimeError: mat1 and mat2 shapes cannot be multiplied` | Linear 层输入未展平 | CNN→FC 前加 `x = x.flatten(1)` 或 `x.view(B, -1)` | Ch37 |
| 梯度形状与参数不匹配（`dW.shape != W.shape`） | `np.outer(delta, a)` 两个向量顺序写反 | 第一个是下游误差，第二个是上游激活值，反了会变转置 | Ch15 |
| `W_Q` 形状写反导致 `X @ W_Q` 报错 | 把 `W_Q` 写成 `(d_k, d_model)` | 正确：`W_Q` 是 `(d_model, d_k)`，`X (T, d_model) @ W_Q (d_model, d_k) = Q (T, d_k)` | Ch29 |
| `QK^T` 写成 `KQ^T`，结果错位 | 顺序写反 | `QK^T` 第 i 行第 j 列是"第 i 个 query 对第 j 个 key 的分数"，shape `(T_q, T_k)` | Ch29 |
| 多头注意力 reshape 报错 | `d_model` 不能被 `n_heads` 整除 | 确保 `d_model % n_heads == 0`，`d_k = d_model // n_heads` | Ch30 |

---

## 二、数值错误（Numerical Errors）

| 错误现象 | 可能原因 | 解决方法 | 相关章节 |
|----------|----------|----------|----------|
| `softmax` 输出 `nan` | 指数溢出（输入值过大） | 减最大值：`z = z - z.max()` | Ch03 |
| `log(0) = -inf` 导致 loss 为 nan | 概率为 0 时取 log | 加小常数：`log(p + 1e-15)`，或用 `BCEWithLogitsLoss` | Ch08 |
| 梯度爆炸（loss 突然变 nan） | 梯度范数过大 | 梯度裁剪：`clip_grad_norm_(model.parameters(), 1.0)` | Ch21, Ch26 |
| 梯度消失（loss 不再下降） | sigmoid/tanh 饱和 | 换 ReLU/GELU；用残差连接；用 LSTM 替代 RNN | Ch12, Ch21 |
| 梯度爆炸（RNN 训练时） | BPTT 链太长 | 梯度裁剪 + 缩短序列 + 用 LSTM/GRU | Ch21 |
| `inf - inf = nan` | mask 用 0 而非 -inf 做 softmax | 必须 `-inf`（或 `-1e9`），softmax 后才严格为 0 | Ch34 |
| 位置编码数值溢出 | 直接算 `10000**(2i/d_model)` | 用等价的 `np.exp(np.arange(0, d, 2) * (-np.log(10000)/d))` | Ch31 |
| 训练几步 loss 就 nan | 学习率过大 | 降低学习率一个数量级（如 1e-3 → 1e-4） | Ch07, Ch35 |
| `tanh` 输出全为 ±1 | 输入过大进入饱和区 | 检查输入是否归一化；用 LayerNorm | Ch12, Ch32 |

---

## 三、训练错误

| 错误现象 | 可能原因 | 解决方法 | 相关章节 |
|----------|----------|----------|----------|
| loss 不下降 | 学习率过大/过小；梯度为 None；标签错位 | 打印 `grad.norm()`；检查学习率（试 1e-3、1e-4、1e-5）；检查 `y` 与 `ŷ` 是否对齐 | Ch07, Ch16 |
| loss 为 nan | 除零、log(0)、inf 混入 | 加 `torch.autograd.set_detect_anomaly(True)` 定位 | Ch08, Ch35 |
| loss 降了但精度不升 | 标签泄漏 / 验证集预处理与训练不一致 | 检查数据管道；验证集用训练集的统计量归一化 | Ch09, Ch10 |
| 训练 loss 低、验证 loss 高（过拟合） | 模型容量过大 / 数据少 | 加 Dropout、L2 正则、早停、数据增强 | Ch09, Ch16 |
| 训练 loss 也降不下去（欠拟合） | 模型容量不足 / 训练不够 | 加宽加深；训练更多 epoch；检查数据是否混入噪声标签 | Ch09 |
| 训练初期 loss 不是 `ln(vocab)` 附近 | logits 或 loss 函数选错 | 分类用 `CrossEntropyLoss`（不要先 softmax）；初始 loss 应在 `ln(vocab)` 附近（如 vocab=10000 时约 9.2） | Ch35 |
| `CrossEntropyLoss` 报 "0D or 1D target" | 标签维度不对 | 标签应为整数类索引 `(B,)`，而非 one-hot `(B, C)`；logits 应为 `(B, C)` | Ch08, Ch35 |
| 反向传播漏乘激活函数导数 | 公式 `δ⁽ˡ⁾ = (Wᵀ·δ⁽ˡ⁺¹⁾) ⊙ σ'(z⁽ˡ⁾)` 漏了 `⊙ σ'` | 每层 δ 都必须乘该层激活函数的导数 | Ch15 |
| 数值梯度验证失败 | 扰动后未恢复参数值 | 每次扰动后立即 `w = original` | Ch15 |
| 梯度裁剪后 loss 仍爆炸 | 裁剪只解决爆炸不解决消失 | 消失需 LSTM/残差/换激活函数；裁剪只缩大不放大 | Ch21 |
| 用 ReLU 替换 tanh 想解决 RNN 梯度消失 | ReLU 无上界会让 RNN 隐藏状态爆炸 | RNN 用 tanh 不用 ReLU；LSTM 用 sigmoid 门控 + tanh 候选 | Ch21 |
| `tanh'` 用错最大值 | 误以为最大值是 0.5 | `tanh'(z) = 1 - tanh²(z)`，z=0 时为 1；0.5 只是训练示意值 | Ch21 |
| RNN 训练几个 step 后 hidden 全是 0 | 输入未归一化导致 tanh 饱和 | 检查输入均值方差；用 LayerNorm | Ch19 |
| Dropout 训练时精度低 | 评估时未关 Dropout | 评估前 `model.eval()`；训练前 `model.train()` | Ch16 |

---

## 四、Transformer 特有错误

| 错误现象 | 可能原因 | 解决方法 | 相关章节 |
|----------|----------|----------|----------|
| Self-Attention softmax 后全是均匀分布 | 忘记除以 `√d_k` | `softmax(QK^T / sqrt(d_k))`，否则点积过大让 softmax 饱和 | Ch29 |
| softmax 维度错（每列和为 1 而非每行） | `dim` 参数错 | 对**每行**做 softmax：`F.softmax(scores, dim=-1)` | Ch29 |
| 忘记位置编码 | Transformer 是置换不变的 | `X' = X + PE`，否则打乱输入序列结果不变 | Ch31 |
| 位置编码与输入**相乘**而非相加 | 误用 `*` | 必须 `+`，相乘会破坏嵌入语义 | Ch31 |
| 位置编码奇偶维搞反 | `2i` 和 `2i+1` 弄混 | 偶数维（0,2,4,...）用 sin，奇数维（1,3,5,...）用 cos | Ch31 |
| 把正弦 PE 当可学习参数训练 | 误把 PE 设为 `nn.Parameter` | 正弦 PE 是**固定**的，用 `register_buffer` 注册 | Ch31, Ch35 |
| Mask 用 0 而非 -inf | 0 softmax 后非零 | 未来位置填 `-inf`（或 `-1e9`） | Ch34 |
| Cross-Attention 的 K/V 用 Decoder 自己的输出 | 退化成 Self-Attention | K/V **必须来自 Encoder 输出**，只有 Q 来自 Decoder | Ch34 |
| Mask 形状不匹配 | mask 不能广播到 `(B, n_heads, T, T)` | mask 一般为 `(T, T)` 或 `(B, 1, T, T)` | Ch34 |
| 训练时 tgt 用完整序列而非 `tgt[:, :-1]` | 模型"看到答案再预测答案" | 输入 `tgt[:, :-1]`，目标 `tgt[:, 1:]`；第 i 位预测第 i+1 位 | Ch34, Ch35 |
| 忘记 `ignore_index=0` | padding 位置计入 loss | loss 函数加 `ignore_index=0`（假设 0 是 padding id） | Ch35 |
| PE 没跟着 `.to(device)` | 用函数而非 Module | PE 封装为 `nn.Module`，用 `register_buffer('pe', ...)` | Ch35 |
| Warmup 阶段 loss 不降反升 | 学习率调度写反 | Warmup 是线性升到峰值再衰减，不是直接用大 lr | Ch35 |
| Label Smoothing 后 loss 不为 0 | 这是正常的 | Label Smoothing 把 one-hot 变成 `[ε/(K-1), ..., 1-ε, ..., ε/(K-1)]`，最优 loss 永远不为 0 | Ch35 |
| 推理时也加训练用的 mask | 多余但不错 | 推理时一个词一个词生成，mask 退化成"天然存在" | Ch34 |
| 多头拼接后维度对不上 | 忘记 `W_O` 投影 | `concat` shape `(B, T, n_heads·d_k)`，用 `W_O (n_heads·d_k, d_model)` 投回 `d_model` | Ch30 |

---

## 五、环境与数据错误

| 错误现象 | 可能原因 | 解决方法 | 相关章节 |
|----------|----------|----------|----------|
| `ModuleNotFoundError: No module named 'torch'` | 未装 PyTorch 或虚拟环境未激活 | `pip install torch`；激活 `.venv` 后再运行 | Ch04 |
| CUDA 报错 `CUDA out of memory` | batch 过大或模型过大 | 减小 `batch_size`；用 `gradient accumulation`；用 `mixed precision` | Ch39 |
| GPU 可用但跑在 CPU 上 | 没显式 `.to(device)` | `device = 'cuda' if torch.cuda.is_available() else 'cpu'`，model 和数据都 `.to(device)` | Ch39 |
| `TypeError: expected Tensor as element 0` | DataLoader 返回 Python list 而非 Tensor | Dataset 的 `__getitem__` 返回 torch.Tensor | Ch39 |
| Tokenizer 报 "out of vocabulary" | 词表未覆盖测试词 | 用 `tokenizer.encode(text, add_special_tokens=True)`；HuggingFace 模型用配套 tokenizer | Ch40 |
| HuggingFace 模型下载慢/失败 | 网络问题 | 设置 `HF_ENDPOINT=https://hf-mirror.com` 镜像；或离线加载 | Ch40 |
| `transformers` 版本不兼容 | API 变化 | 锁定版本：`pip install transformers==4.30.0` | Ch40 |
| 训练时 `DataLoader` 卡住 | `num_workers` 在 Windows 上出问题 | Windows 下设 `num_workers=0` | Ch39 |
| Jupyter 显示图表异常 | matplotlib 后端 | `import matplotlib; matplotlib.use('Agg')` 或 `%matplotlib inline` | Ch04 |
| `git` 中文文件名乱码 | 编码问题 | `git config --global core.quotepath false` | Ch00 |

---

## 六、排错通用流程

遇到错误时按以下顺序排查：

```
1. 看 Traceback 第一行：哪个文件、哪一行报错？
   ↓
2. 看 Traceback 最后一行：什么类型的错误？
   ↓
3. 打印关键变量的 shape 和 dtype：
   print(x.shape, x.dtype, y.shape, y.dtype)
   ↓
4. 数值错误时打印 min/max/nan：
   print(x.min(), x.max(), torch.isnan(x).any())
   ↓
5. 训练问题先看梯度：
   for n, p in model.named_parameters():
       if p.grad is not None:
           print(n, p.grad.norm())
   ↓
6. 还不行：用最小复现（batch_size=1, 单层网络）逐步定位
```

---

## 七、调试常用代码片段

### 7.1 打印模型结构

```python
print(model)
# 或更详细
for name, param in model.named_parameters():
    print(name, param.shape, param.requires_grad)
```

### 7.2 检查梯度

```python
for name, p in model.named_parameters():
    if p.grad is None:
        print(f"{name}: NO GRAD")           # 没接入计算图
    else:
        print(f"{name}: grad_norm={p.grad.norm().item():.4f}")
```

### 7.3 检查 NaN 来源

```python
torch.autograd.set_detect_anomaly(True)     # 慢但能定位
loss.backward()                              # 会报错的 op
```

### 7.4 形状速查

```python
def shapes(**kwargs):
    for k, v in kwargs.items():
        if hasattr(v, 'shape'):
            print(f"{k}: {tuple(v.shape)}")
        else:
            print(f"{k}: {v}")
```

---

## 八、AI 必看（项目特有坑点）

> 以下坑点来自本教程写作过程中的踩坑记录，写作子 Agent 不得在数值示例中重蹈覆辙。

| 坑点 | 出处 | 提醒 |
|------|------|------|
| LSTM 的 W 是 `(2,4)` 矩阵不是方阵，不能用单位矩阵简化 | Ch25 | 用对角矩阵 `[[0.5,0,0.5,0],[0,0.5,0,0.5]]` |
| RNN 的 `W_hh` 用标量会与矩阵形式矛盾 | Ch20 | 用对角矩阵 `[[0.5,0],[0,0.5]]`，隐藏状态 2 维 |
| `np.array([1,2,3])` 是 `(3,)` 不是 `(3,1)` | Ch01 | 一维是"裸向量"，既非行也非列 |
| Multi-Head 数值不能用"得 out_1"跳过 | Ch30 | 必须展开两个头的完整计算 |
| Ch08 的 `w` 是 Python 标量时 `X @ w` 报错 | Ch08 | `w = np.array([0.0])` 形状 `(1,)` |

---

> 上一附录：[附录 B · NumPy/PyTorch 速查](附录B-NumPy_PyTorch速查.md)  ｜  下一附录：[附录 D · 术语表](附录D-术语表.md)
