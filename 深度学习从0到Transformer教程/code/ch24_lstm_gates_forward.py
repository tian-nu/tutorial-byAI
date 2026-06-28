"""
Ch24 · LSTM 的三个门与细胞状态
================================
完整手算单步 LSTM 的四个门（遗忘门、输入门、候选状态、输出门）、
细胞状态更新和隐藏状态输出。

所有数值与教程手算一致，可逐步验证。

运行：python ch24_lstm_gates_forward.py
"""

import numpy as np


def sigmoid(x):
    """sigmoid 激活函数，输出 [0, 1]"""
    return 1 / (1 + np.exp(-x))


def lstm_single_step(h_prev, x_t, C_prev, W_f, W_i, W_C, W_o, b):
    """LSTM 单步前向传播（完整四门计算）。

    公式:
        f_t = σ(W_f · [h_{t-1}, x_t] + b_f)    # 遗忘门
        i_t = σ(W_i · [h_{t-1}, x_t] + b_i)    # 输入门
        C̃_t = tanh(W_C · [h_{t-1}, x_t] + b_C)  # 候选状态
        o_t = σ(W_o · [h_{t-1}, x_t] + b_o)    # 输出门
        C_t = f_t ⊙ C_{t-1} + i_t ⊙ C̃_t        # 细胞状态更新（加法）
        h_t = o_t ⊙ tanh(C_t)                    # 隐藏状态

    Args:
        h_prev: 上一步隐藏状态 h_{t-1}，shape (h,)
        x_t: 当前输入，shape (d,)
        C_prev: 上一步细胞状态 C_{t-1}，shape (h,)
        W_f, W_i, W_C, W_o: 四组权重矩阵，shape (h, h+d)
        b: 偏置，shape (h,)（本章简化为 0）

    Returns:
        f_t, i_t, C_bar, o_t, C_t, h_t
    """
    # 拼接 [h_{t-1}, x_t]
    concat = np.concatenate([h_prev, x_t])

    # 四门计算（禁用"同理算出"，每门独立计算）
    f_t = sigmoid(W_f @ concat + b)       # 遗忘门
    i_t = sigmoid(W_i @ concat + b)       # 输入门
    C_bar = np.tanh(W_C @ concat + b)     # 候选状态（tanh，不是 sigmoid）
    o_t = sigmoid(W_o @ concat + b)       # 输出门

    # 细胞状态更新（加法更新，核心思想）
    C_t = f_t * C_prev + i_t * C_bar      # ⊙ 逐元素乘

    # 隐藏状态（必须先 tanh 压扁 C_t，再按输出门放行）
    h_t = o_t * np.tanh(C_t)

    return f_t, i_t, C_bar, o_t, C_t, h_t


def main():
    print("=" * 60)
    print("Ch24: LSTM 三个门与细胞状态")
    print("=" * 60)

    # === 输入 ===
    h_prev = np.array([0.5, -0.3])
    x_t = np.array([1.0, 0.8])
    C_prev = np.array([0.6, -0.4])

    print()
    print("--- 输入 ---")
    print(f"h_{{t-1}} = {h_prev}")
    print(f"x_t     = {x_t}")
    print(f"C_{{t-1}} = {C_prev}")
    print(f"拼接 [h_{{t-1}}, x_t] = {np.concatenate([h_prev, x_t])}")

    # === 四组权重（2×4 矩阵，偏置为 0）===
    W_f = np.array([[0.1, 0.2, 0.3, 0.4],
                    [0.5, 0.6, 0.7, 0.8]])
    W_i = np.array([[0.2, 0.1, 0.3, 0.5],
                    [0.4, 0.3, 0.2, 0.1]])
    W_C = np.array([[0.1, 0.3, 0.2, 0.4],
                    [0.5, 0.1, 0.3, 0.2]])
    W_o = np.array([[0.3, 0.2, 0.1, 0.4],
                    [0.2, 0.4, 0.3, 0.1]])
    b = np.zeros(2)

    print()
    print("--- 四组权重 ---")
    print(f"W_f =\n{W_f}")
    print(f"W_i =\n{W_i}")
    print(f"W_C =\n{W_C}")
    print(f"W_o =\n{W_o}")
    print(f"b   = {b}")

    # === 单步前向传播 ===
    f_t, i_t, C_bar, o_t, C_t, h_t = lstm_single_step(
        h_prev, x_t, C_prev, W_f, W_i, W_C, W_o, b
    )

    # === 逐步打印（与教程手算对照）===
    print()
    print("--- 四门计算（逐步展开）---")

    concat = np.concatenate([h_prev, x_t])

    # 遗忘门
    print()
    print("第 1 步: 遗忘门 f_t = σ(W_f · concat + b)")
    print(f"  W_f · concat = {W_f @ concat}")
    print(f"  f_t = sigmoid({W_f @ concat}) = {f_t.round(3)}")

    # 输入门
    print()
    print("第 2 步: 输入门 i_t = σ(W_i · concat + b)")
    print(f"  W_i · concat = {W_i @ concat}")
    print(f"  i_t = sigmoid({W_i @ concat}) = {i_t.round(3)}")

    # 候选状态
    print()
    print("第 3 步: 候选状态 C̃_t = tanh(W_C · concat + b)")
    print(f"  W_C · concat = {W_C @ concat}")
    print(f"  C̃_t = tanh({W_C @ concat}) = {C_bar.round(3)}")

    # 输出门
    print()
    print("第 4 步: 输出门 o_t = σ(W_o · concat + b)")
    print(f"  W_o · concat = {W_o @ concat}")
    print(f"  o_t = sigmoid({W_o @ concat}) = {o_t.round(3)}")

    # 细胞状态更新
    print()
    print("第 5 步: 细胞状态更新 C_t = f_t ⊙ C_{t-1} + i_t ⊙ C̃_t")
    print(f"  f_t ⊙ C_{{t-1}} = {f_t} * {C_prev} = {(f_t * C_prev).round(3)}")
    print(f"  i_t ⊙ C̃_t    = {i_t} * {C_bar} = {(i_t * C_bar).round(3)}")
    print(f"  C_t = {(f_t * C_prev).round(3)} + {(i_t * C_bar).round(3)} = {C_t.round(3)}")

    # 隐藏状态
    print()
    print("第 6 步: 隐藏状态 h_t = o_t ⊙ tanh(C_t)")
    print(f"  tanh(C_t) = tanh({C_t.round(3)}) = {np.tanh(C_t).round(3)}")
    print(f"  h_t = {o_t.round(3)} * {np.tanh(C_t).round(3)} = {h_t.round(3)}")

    # === 结果汇总 ===
    print()
    print("=" * 60)
    print("--- 结果汇总 ---")
    print(f"{'量':>10} | {'数值':>20} | {'含义':>30}")
    print("-" * 65)
    print(f"{'f_t':>10} | {str(f_t.round(3)):>20} | {'遗忘门：保留 64.8%/80.4% 旧记忆':>30}")
    print(f"{'i_t':>10} | {str(i_t.round(3)):>20} | {'输入门：写入 68.4%/59.6% 新信息':>30}")
    print(f"{'C̃_t':>10} | {str(C_bar.round(3)):>20} | {'候选：新信息 +0.446/+0.592':>30}")
    print(f"{'o_t':>10} | {str(o_t.round(3)):>20} | {'输出门：暴露 62.5%/58.9% 细胞状态':>30}")
    print(f"{'C_t':>10} | {str(C_t.round(3)):>20} | {'新细胞状态（加法更新）':>30}")
    print(f"{'h_t':>10} | {str(h_t.round(3)):>20} | {'新隐藏状态（对外输出）':>30}")

    # === 验证 ===
    print()
    print("--- 验证 ---")
    expected_C = [0.694, 0.031]
    expected_h = [0.375, 0.018]
    assert np.allclose(C_t.round(3), expected_C, atol=0.001), f"C_t 不匹配: {C_t}"
    assert np.allclose(h_t.round(3), expected_h, atol=0.001), f"h_t 不匹配: {h_t}"
    print(f"✅ C_t = {C_t.round(3)} 与教程一致 (期望 [0.694, 0.031])")
    print(f"✅ h_t = {h_t.round(3)} 与教程一致 (期望 [0.375, 0.018])")

    print()
    print("可视化演示见 24_lstm_gates_visual.html")


if __name__ == "__main__":
    main()
