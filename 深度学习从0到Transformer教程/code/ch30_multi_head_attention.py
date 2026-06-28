"""
Ch30 · Multi-Head Attention — 多头注意力
==========================================
本文件包含两部分：
1. NumPy 手算验证版：用 2 头、d_model=4 的小例子，逐步算出 out_1, out_2, concat, 最终输出
2. PyTorch 标准实现版：可处理任意 batch_size, T, d_model, n_heads

手算验证小例子：
    X = [[1.0, 0.5, 0.3, 0.7],
         [0.2, 0.8, 0.4, 0.6],
         [0.9, 0.1, 0.5, 0.5]]
    h=2, d_model=4, d_k=2
    每头 W_Q = W_K = W_V = I_2, W_O = I_4
    期望:
      out_1 ≈ [[0.760, 0.445], [0.673, 0.502], [0.770, 0.428]]
      out_2 ≈ [[0.398, 0.602], [0.399, 0.602], [0.400, 0.600]]
      concat ≈ [[0.760, 0.445, 0.398, 0.602], ...]
      最终输出 ≈ concat (W_O=I_4)

运行：
    cd 深度学习从0到Transformer教程/code
    python ch30_multi_head_attention.py
"""

import numpy as np


# ============== 1. 数值稳定的 softmax ==============
def softmax(x: np.ndarray, axis: int = -1) -> np.ndarray:
    x = np.asarray(x, dtype=np.float64)
    x_max = np.max(x, axis=axis, keepdims=True)
    e = np.exp(x - x_max)
    return e / np.sum(e, axis=axis, keepdims=True)


# ============== 2. 单头 Self-Attention（用于复用） ==============
def single_head_attention(X, WQ, WK, WV):
    """对单头做 Self-Attention。"""
    Q = X @ WQ
    K = X @ WK
    V = X @ WV
    d_k = K.shape[-1]
    scores = Q @ K.T / np.sqrt(d_k)
    alpha = softmax(scores, axis=-1)
    out = alpha @ V
    return out, alpha


# ============== 3. Multi-Head Attention (NumPy 版，可手算验证) ==============
def multi_head_attention_numpy(X, WQ_list, WK_list, WV_list, W_O):
    """
    X: (T, d_model)
    WQ_list, WK_list: list of (d_model, d_k)，每头一个
    WV_list: list of (d_model, d_v)，每头一个
    W_O: (h*d_v, d_model)
    返回 out (T, d_model), heads_out (list of (T, d_v))
    """
    heads_out = []
    for WQ, WK, WV in zip(WQ_list, WK_list, WV_list):
        out_i, _ = single_head_attention(X, WQ, WK, WV)
        heads_out.append(out_i)

    # 沿特征维拼接
    concat = np.concatenate(heads_out, axis=-1)  # (T, h*d_v)
    final = concat @ W_O                          # (T, d_model)
    return final, heads_out, concat


# ============== 4. PyTorch 标准实现 ==============
def demo_pytorch_mha():
    """演示 PyTorch 标准的 Multi-Head Attention 实现。"""
    try:
        import torch
        import torch.nn as nn
        import torch.nn.functional as F
    except ImportError:
        print("[PyTorch 演示] 未安装 torch，跳过此部分。")
        print("               如需运行：pip install torch")
        return None

    class MultiHeadAttention(nn.Module):
        def __init__(self, d_model, n_heads):
            super().__init__()
            assert d_model % n_heads == 0, "d_model 必须能被 n_heads 整除"
            self.d_model = d_model
            self.n_heads = n_heads
            self.d_k = d_model // n_heads
            self.W_q = nn.Linear(d_model, d_model)
            self.W_k = nn.Linear(d_model, d_model)
            self.W_v = nn.Linear(d_model, d_model)
            self.W_o = nn.Linear(d_model, d_model)

        def forward(self, x):
            B, T, _ = x.shape
            Q = self.W_q(x).view(B, T, self.n_heads, self.d_k).transpose(1, 2)
            K = self.W_k(x).view(B, T, self.n_heads, self.d_k).transpose(1, 2)
            V = self.W_v(x).view(B, T, self.n_heads, self.d_k).transpose(1, 2)
            scores = Q @ K.transpose(-2, -1) / (self.d_k ** 0.5)
            attn = F.softmax(scores, dim=-1)
            out = attn @ V
            out = out.transpose(1, 2).contiguous().view(B, T, self.d_model)
            return self.W_o(out)

    mha = MultiHeadAttention(d_model=512, n_heads=8)
    x = torch.randn(2, 10, 512)
    out = mha(x)
    print(f"PyTorch MHA 输出形状: {out.shape}")  # (2, 10, 512)
    return out.shape


# ============== 5. 主程序：手算验证 + PyTorch 演示 ==============
def main():
    # === 教程里的手算小例子 ===
    X = np.array([[1.0, 0.5, 0.3, 0.7],
                  [0.2, 0.8, 0.4, 0.6],
                  [0.9, 0.1, 0.5, 0.5]])
    print("=== Ch30 Multi-Head Attention 完整流程 ===\n")
    print(f"X (3, 4):\n {X}\n")

    # 拆头：头 1 用前 2 维，头 2 用后 2 维
    X_1 = X[:, :2]   # (3, 2)
    X_2 = X[:, 2:]   # (3, 2)

    # 简化假设：每头 W_Q = W_K = W_V = I_2
    I2 = np.eye(2)
    WQ1 = WK1 = WV1 = I2
    WQ2 = WK2 = WV2 = I2

    # 头 1
    out_1, alpha_1 = single_head_attention(X_1, WQ1, WK1, WV1)
    print("=== 头 1 ===")
    print(f"X_1 (前 2 维):\n {X_1}")
    print(f"QK^T_1 = X_1 · X_1^T:\n {X_1 @ X_1.T}")
    print(f"alpha_1:\n {alpha_1.round(3)}")
    print(f"out_1:\n {out_1.round(3)}\n")

    # 教程里用 3 位小数 α 手算的近似值；代码全精度计算有 0.001~0.002 的四舍五入差异。
    expected_out_1 = np.array([[0.760, 0.445],
                               [0.673, 0.502],
                               [0.770, 0.428]])
    assert np.allclose(out_1, expected_out_1, atol=2e-3), f"out_1 不匹配: {out_1}"
    print(f"✅ out_1 与手算一致 (容差 2e-3，兼容 3 位 α 与全精度)\n")

    # 头 2
    out_2, alpha_2 = single_head_attention(X_2, WQ2, WK2, WV2)
    print("=== 头 2 ===")
    print(f"X_2 (后 2 维):\n {X_2}")
    print(f"QK^T_2 = X_2 · X_2^T:\n {X_2 @ X_2.T}")
    print(f"alpha_2:\n {alpha_2.round(3)}")
    print(f"out_2:\n {out_2.round(3)}\n")

    # 教程里用 3 位小数 α 手算的近似值；代码全精度计算有 0.001~0.002 的四舍五入差异。
    expected_out_2 = np.array([[0.398, 0.602],
                               [0.399, 0.602],
                               [0.400, 0.600]])
    assert np.allclose(out_2, expected_out_2, atol=2e-3), f"out_2 不匹配: {out_2}"
    print(f"✅ out_2 与手算一致 (容差 2e-3，兼容 3 位 α 与全精度)\n")

    # 拼接
    concat = np.concatenate([out_1, out_2], axis=-1)  # (3, 4)
    print(f"=== 拼接 ===")
    print(f"concat (3, 4):\n {concat.round(3)}\n")

    expected_concat = np.array([[0.760, 0.445, 0.398, 0.602],
                                [0.673, 0.502, 0.399, 0.602],
                                [0.770, 0.428, 0.400, 0.600]])
    assert np.allclose(concat, expected_concat, atol=2e-3), f"concat 不匹配: {concat}"
    print(f"✅ concat 与手算一致 (容差 2e-3)\n")

    # W_O = I_4
    W_O = np.eye(4)
    final = concat @ W_O
    print(f"=== 输出投影 (W_O = I_4) ===")
    print(f"最终输出 (3, 4):\n {final.round(3)}\n")
    assert np.allclose(final, concat), "W_O=I 时最终输出应等于 concat"
    print(f"✅ 最终输出与手算一致\n")

    # === 用 multi_head_attention_numpy 函数验证 ===
    print("=== 用 multi_head_attention_numpy 函数验证 ===")
    # 注意：这里用切片投影矩阵（前2维或后2维）来模拟"拆头"行为
    # 实际 PyTorch 实现里 W_Q 是 (d_model, d_model)，再用 view+transpose 拆
    # 我们这里用 (d_model, d_k) 的稀疏矩阵来等价表示
    WQ1_full = np.zeros((4, 2)); WQ1_full[:2, :] = I2  # 取前2维
    WQ2_full = np.zeros((4, 2)); WQ2_full[2:, :] = I2  # 取后2维
    final2, heads_out2, concat2 = multi_head_attention_numpy(
        X, [WQ1_full, WQ2_full], [WQ1_full, WQ2_full], [WQ1_full, WQ2_full], W_O
    )
    assert np.allclose(final2, final, atol=1e-6), f"函数版与分步版不一致: {final2}"
    print(f"函数版最终输出:\n {final2.round(3)}")
    print("✅ 与分步结果一致\n")

    # === 观察两个头的差异 ===
    print("=== 两个头输出对比 ===")
    print(f"头 1 out_1 (波动大):")
    print(f"  行间标准差: {out_1.std(axis=0).round(4)}")
    print(f"头 2 out_2 (波动小):")
    print(f"  行间标准差: {out_2.std(axis=0).round(4)}")
    print("观察：头 1 的输出在不同位置间差异明显（X_1 各行差异大），")
    print("      头 2 的输出几乎一致（X_2 各行相似，attention 退化成平均）。")
    print("      这就是不同头关注不同子空间信息的体现。")

    # === PyTorch 标准实现 ===
    print("\n=== PyTorch 标准实现 ===")
    shape = demo_pytorch_mha()
    if shape is not None:
        print(f"✅ PyTorch MHA 可正常运行，输出形状 {shape}")
    else:
        print("(跳过 PyTorch 演示，不影响手算验证结果)")

    print("\n✅ Ch30 Multi-Head Attention 演示完成")


if __name__ == "__main__":
    main()
