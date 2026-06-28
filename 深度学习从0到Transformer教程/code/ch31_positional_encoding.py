"""
Ch31 · Positional Encoding — 给注意力加位置感
==============================================
本文件实现正弦位置编码，并验证手算小例子：

    d_model=4, 前 3 个位置的编码：
    PE(0) = [0,     1,     0,    1   ]
    PE(1) = [0.841, 0.540, 0.01, 1.0 ]
    PE(2) = [0.909,-0.416, 0.02, 1.0 ]

运行：
    cd 深度学习从0到Transformer教程/code
    python ch31_positional_encoding.py
"""

import numpy as np


# ============== 1. 正弦位置编码 ==============
def positional_encoding(T: int, d_model: int) -> np.ndarray:
    """
    生成 (T, d_model) 的正弦位置编码矩阵。
    公式:
        PE(pos, 2i)   = sin(pos / 10000^(2i/d_model))
        PE(pos, 2i+1) = cos(pos / 10000^(2i/d_model))
    """
    pe = np.zeros((T, d_model), dtype=np.float64)
    pos = np.arange(T)[:, None]  # (T, 1)
    # div_term[i] = 1 / 10000^(2i/d_model) = exp(-2i * log(10000) / d_model)
    # 用 exp+log 形式避免直接算 10000**x 时溢出
    div_term = np.exp(np.arange(0, d_model, 2) * (-np.log(10000.0) / d_model))
    pe[:, 0::2] = np.sin(pos * div_term)  # 偶数维 sin
    pe[:, 1::2] = np.cos(pos * div_term)  # 奇数维 cos
    return pe


# ============== 2. 主程序：验证手算 + 演示特性 ==============
def main():
    # === 手算验证小例子 ===
    print("=== Ch31 Positional Encoding 完整流程 ===\n")
    d_model = 4
    T = 3
    pe = positional_encoding(T, d_model)
    print(f"d_model={d_model}, 前 {T} 个位置的编码:")
    for pos in range(T):
        print(f"PE({pos}) = {pe[pos].round(4)}")

    # 与手算结果对比
    expected = np.array([
        [0.0,   1.0,    0.0,  1.0],
        [0.841, 0.540,  0.01, 1.0],
        [0.909,-0.416,  0.02, 1.0],
    ])
    assert np.allclose(pe, expected, atol=1e-3), f"PE 不匹配: {pe}"
    print("✅ 与手算结果一致\n")

    # === 观察低维高频、高维低频 ===
    print("=== 观察：低维变化快（高频），高维变化慢（低频） ===")
    pe_long = positional_encoding(50, d_model)
    for col in range(d_model):
        # 计算这一列前 3 个位置的方差，方差大说明变化快
        var = pe_long[:3, col].var()
        i_idx = col // 2
        freq = 1.0 / (10000 ** (2 * i_idx / d_model))
        print(f"列 {col} (i={i_idx}, 频率={freq:.4f}): 前3位置 {pe_long[:3, col].round(4)}, 方差={var:.4f}")
    print("观察：i=0 的列（前2维）方差大、变化快；i=1 的列（后2维）方差小、变化慢。")
    print("这就像钟表：秒针（低维高频）转得快，时针（高维低频）转得慢，")
    print("不同频率组合能唯一表示任意位置——这就是正弦编码可外推的根本原因。\n")

    # === 验证可外推性 ===
    print("=== 验证可外推性 ===")
    # 假设训练时只见过 pos < 50，推理时遇到 pos = 200
    train_max_pos = 50
    infer_pos = 200
    pe_infer = positional_encoding(infer_pos + 1, d_model)
    print(f"训练时见过的最大 pos = {train_max_pos}")
    print(f"推理时 pos = {infer_pos} 的编码: {pe_infer[infer_pos].round(4)}")
    print(f"  sin/cos 仍在 [-1, 1] 内，不会溢出 ✅")
    print(f"  而且由于周期性，这个编码仍能用已有频率组合表示 ✅\n")

    # === 验证相对位置关系（sin(a+b) 恒等式） ===
    print("=== 验证相对位置关系（sin(pos+k) 可由 sin(pos), cos(pos) 线性表示）===")
    pos_a = 5
    k = 3
    pos_b = pos_a + k
    pe_check = positional_encoding(max(pos_a, pos_b) + 1, d_model)
    sin_a = pe_check[pos_a, 0]   # sin(pos_a / 1)
    cos_a = pe_check[pos_a, 1]   # cos(pos_a / 1)
    sin_b_direct = pe_check[pos_b, 0]  # 直接算 sin(pos_b / 1)
    # 用三角恒等式: sin(pos_a + k) = sin(pos_a)cos(k) + cos(pos_a)sin(k)
    # 这里 pos 单位是 1（i=0, 频率=1），所以 k=3 对应角度 3
    sin_b_via_identity = sin_a * np.cos(k) + cos_a * np.sin(k)
    print(f"sin(pos_a={pos_a}) = {sin_a:.4f}")
    print(f"cos(pos_a={pos_a}) = {cos_a:.4f}")
    print(f"直接算 sin(pos_a+k={pos_b}) = {sin_b_direct:.4f}")
    print(f"用恒等式 sin(a)cos(k)+cos(a)sin(k) = {sin_b_via_identity:.4f}")
    assert np.isclose(sin_b_direct, sin_b_via_identity, atol=1e-6)
    print("✅ 三角恒等式成立，说明 PE(pos+k) 可由 PE(pos) 线性变换得到")
    print("   这就是模型能从绝对位置编码学到相对位置关系的数学基础。\n")

    # === 演示 X + PE 的实际效果 ===
    print("=== 演示 X + PE 的实际效果 ===")
    np.random.seed(42)
    # 假设 3 个词的嵌入，d_model=4
    X = np.random.randn(3, 4) * 0.5  # 量级在 [-1, 1]
    print(f"原始嵌入 X:\n {X.round(3)}")
    print(f"位置编码 PE (前3位置):\n {pe.round(3)}")
    X_plus_PE = X + pe
    print(f"X + PE:\n {X_plus_PE.round(3)}")
    print("观察：X + PE 让不同位置的相同词有不同的最终表示，")
    print("      模型通过这种加法就能感知位置信息。\n")

    # === PyTorch 标准实现（参考） ===
    print("=== PyTorch 等价实现（参考）===")
    try:
        import torch
        import math

        def pe_torch(T, d_model):
            pe = torch.zeros(T, d_model)
            position = torch.arange(0, T).unsqueeze(1).float()
            div_term = torch.exp(
                torch.arange(0, d_model, 2).float() * (-math.log(10000.0) / d_model)
            )
            pe[:, 0::2] = torch.sin(position * div_term)
            pe[:, 1::2] = torch.cos(position * div_term)
            return pe

        pe_t = pe_torch(3, 4).numpy()
        assert np.allclose(pe_t, pe, atol=1e-6)
        print(f"PyTorch 实现与 NumPy 实现一致: ✅")
        print(f"PE(1) = {pe_t[1].round(4)}")
    except ImportError:
        print("(PyTorch 未安装，跳过 PyTorch 演示)")

    print("\n✅ Ch31 Positional Encoding 演示完成")


if __name__ == "__main__":
    main()
