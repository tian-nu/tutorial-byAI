"""
Ch22 · 为什么 RNN 记不住长序列
=================================
模拟 RNN 梯度随时间步衰减，验证"梯度消失"现象。
对比 W_hh 特征值 < 1（消失）和 > 1（爆炸）两种情况。

运行：python ch22_rnn_long_dependency.py
"""

import numpy as np


def simulate_rnn_gradient_decay(w_eigenvalue, tanh_deriv, T_list):
    """模拟 RNN 梯度随时间步 T 衰减。

    每步梯度乘上 (W_hh 特征值 × tanh')，T 步连乘后梯度为：
        grad = (w_eigenvalue * tanh_deriv) ** T

    Args:
        w_eigenvalue: W_hh 的最大特征值（衡量矩阵对向量的整体缩放）
        tanh_deriv: tanh 导数的平均值（约 0.5）
        T_list: 要模拟的时间步列表
    """
    factor = w_eigenvalue * tanh_deriv
    print(f"每步缩放因子 = W_hh 特征值 × tanh' = {w_eigenvalue} × {tanh_deriv} = {factor}")
    print()
    for T in T_list:
        grad = factor ** T
        print(f"T={T:3d} 步: 梯度 = {grad:.4e}")


def main():
    print("=" * 60)
    print("Ch22: 为什么 RNN 记不住长序列")
    print("=" * 60)

    # === 第 1 部分：RNN 梯度随时间步衰减（特征值 < 1）===
    print()
    print("=== RNN 梯度随时间步衰减（W_hh 特征值 = 0.9）===")
    # W_hh 的最大特征值 = 0.9（每经过一次 W_hh，向量长度最多乘 0.9）
    # tanh 的导数平均取 0.5（tanh 在 0 附近导数为 1，饱和区趋近 0）
    simulate_rnn_gradient_decay(
        w_eigenvalue=0.9,
        tanh_deriv=0.5,
        T_list=[5, 10, 20, 50, 100],
    )

    # === 第 2 部分：如果 W_hh 特征值 > 1（梯度爆炸）===
    print()
    print("=== 如果 W_hh 特征值 = 1.1（梯度爆炸风险）===")
    print("(注意：1.1 × 0.5 = 0.55 仍在衰减，但特征值更大时就会爆炸)")
    simulate_rnn_gradient_decay(
        w_eigenvalue=1.1,
        tanh_deriv=0.5,
        T_list=[5, 10, 20, 50, 100],
    )

    # === 第 3 部分：更直观的对比 ===
    print()
    print("=== 不同特征值下 T=50 步的梯度 ===")
    print(f"{'特征值':>8} | {'每步因子':>10} | {'T=50 梯度':>15} | {'现象':>10}")
    print("-" * 55)
    for eigenval, label in [(0.5, "严重消失"),
                            (0.9, "消失"),
                            (1.0, "临界"),
                            (1.1, "衰减中"),
                            (2.5, "爆炸")]:
        factor = eigenval * 0.5
        grad = factor ** 50
        print(f"{eigenval:>8.1f} | {factor:>10.2f} | {grad:>15.4e} | {label:>10}")

    # === 第 4 部分：三大缺陷总结 ===
    print()
    print("=== RNN 三大结构性缺陷 ===")
    print("1. 记忆覆盖: h_t = tanh(W_xh·x_t + W_hh·h_{t-1})，每步重写")
    print("2. 梯度连乘: ∂L/∂h_1 ≈ ∏(W_hh·tanh')，T 大时趋近 0 或 ∞")
    print("3. 信息瓶颈: 所有历史压在固定大小 h_t 中，序列越长丢得越多")
    print()
    print("结论: 这是 RNN 的基因缺陷，调参治不了。")
    print("      要根治，必须改记忆更新方式 → LSTM 的加法更新（Ch23）。")


if __name__ == "__main__":
    main()
