"""
Ch23 · LSTM 的核心思想 — 门控
================================
对比 RNN（乘法链）和 LSTM（加法链）的梯度衰减。
演示 sigmoid 作为"水龙头"控制信息流量的直觉。

运行：python ch23_lstm_gate_idea.py
"""

import numpy as np


def sigmoid(x):
    """sigmoid 函数：输出 [0, 1]，像水龙头控制流量"""
    return 1 / (1 + np.exp(-x))


def compare_rnn_lstm_gradient():
    """对比 RNN 和 LSTM 的梯度衰减速度。

    RNN: 每步乘 (W_hh 特征值 × tanh')，约 0.45
    LSTM: 每步乘 (保留比例)，可接近 1.0
    """
    # RNN 每步因子
    rnn_W_eigenvalue = 0.9
    rnn_tanh_deriv = 0.5
    rnn_factor = rnn_W_eigenvalue * rnn_tanh_deriv  # 0.45

    # LSTM 每步因子（保留比例）
    lstm_keep_full = 1.0   # 遗忘水龙头全开
    lstm_keep_09 = 0.9     # 遗忘水龙头开 90%

    print("=== RNN vs LSTM 梯度衰减对比 ===")
    print()
    print(f"RNN 每步因子 = {rnn_factor}（W_hh 特征值 × tanh'）")
    print(f"LSTM 每步因子 = {lstm_keep_full}（保留比例 = 1.0）"
          f" 或 {lstm_keep_09}（保留比例 = 0.9）")
    print()
    print(f"{'T':>5} | {'RNN':>15} | {'LSTM(保留=1.0)':>18} | {'LSTM(保留=0.9)':>18}")
    print("-" * 65)
    for T in [5, 10, 20, 50, 100]:
        rnn_grad = rnn_factor ** T
        lstm_full = lstm_keep_full ** T
        lstm_09 = lstm_keep_09 ** T
        print(f"{T:>5} | {rnn_grad:>15.4e} | {lstm_full:>18.4e} | {lstm_09:>18.4e}")

    print()
    print("关键观察:")
    print(f"  T=50 时: RNN 梯度 = {rnn_factor**50:.2e}（消失）")
    print(f"           LSTM(保留=1.0) = {lstm_keep_full**50:.2e}（不衰减！）")
    print(f"           LSTM(保留=0.9) = {lstm_keep_09**50:.2e}（衰减但远好于 RNN）")


def demonstrate_gate_intuition():
    """演示 sigmoid 作为"水龙头"的直觉"""
    print()
    print("=== 门控直觉：sigmoid 输出 = 水龙头开度 ===")
    for x, label in [(-5, "关紧"),
                     (-1, "微开"),
                     (0, "半开"),
                     (1, "大开"),
                     (5, "全开")]:
        gate = sigmoid(x)
        print(f"  sigmoid({x:>2}) = {gate:.4f}  "
              f"← {label}（信息流量 {gate*100:.1f}%）")

    print()
    print("直觉: 门控 = 按比例放行，不是压扁")
    print("  - sigmoid [0,1] = '保留多少'/'写入多少'（比例）")
    print("  - tanh [-1,1]   = '增加多少'/'减少多少'（增量）")


def demonstrate_additive_update():
    """演示 LSTM 加法更新为什么能避免梯度消失"""
    print()
    print("=== 加法更新 vs 乘法更新：梯度路径对比 ===")
    print()
    print("RNN (乘法链):")
    print("  h_t = tanh(W_xh·x_t + W_hh·h_{t-1})")
    print("  ∂h_t/∂h_{t-1} = W_hh · tanh'(z_t)  ← 每步乘矩阵 W_hh")
    print("  T 步连乘: ∂L/∂h_1 ≈ ∏(W_hh · tanh')  ← 矩阵连乘，衰减严重")
    print()
    print("LSTM (加法链):")
    print("  C_t = (保留比例) ⊙ C_{t-1} + (写入比例) ⊙ (新候选)")
    print("  ∂C_t/∂C_{t-1} = (保留比例)  ← 每步只乘标量，不乘矩阵！")
    print("  T 步连乘: ∂L/∂C_1 ≈ ∏(保留比例)  ← 标量连乘，保留比例≈1 时不衰减")
    print()
    print("核心洞察: LSTM 的加法更新让梯度沿 C 路径顺畅流动，")
    print("          不被 W_hh 矩阵连乘拖累——这就是治 RNN 梯度消失的根本。")


def main():
    print("=" * 60)
    print("Ch23: LSTM 的核心思想 — 门控")
    print("=" * 60)

    compare_rnn_lstm_gradient()
    demonstrate_gate_intuition()
    demonstrate_additive_update()

    print()
    print("=== 总结 ===")
    print("1. 门控: sigmoid 输出 [0,1]，像水龙头按比例控制信息流量")
    print("2. 加法更新: C_t = (保留)⊙C_{t-1} + (写入)⊙(新信息)")
    print("   梯度沿加法路径不衰减（保留比例≈1 时梯度无损传递）")
    print("3. 细胞状态 C_t: LSTM 的记忆通道，用加法更新，不经过 tanh 重写")
    print("4. 思想同源: LSTM 的加法更新 ≈ ResNet 的残差连接 ≈ Transformer 的残差")


if __name__ == "__main__":
    main()
