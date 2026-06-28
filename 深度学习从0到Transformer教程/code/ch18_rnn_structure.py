"""
Ch18: RNN 的结构与展开
演示：(1) 参数共享 (2) 2维输入2维隐藏的完整数值计算 (3) 参数量与序列长度无关
"""
import numpy as np


def rnn_step(x, h_prev, W_xh, W_hh, b):
    """
    RNN 单步前向传播
    hₜ = tanh(W_xh·xₜ + W_hh·hₜ₋₁ + b)

    参数:
        x: 当前输入 (input_dim,)
        h_prev: 上一步隐藏状态 (hidden_dim,)
        W_xh: 输入权重 (hidden_dim, input_dim)
        W_hh: 隐藏权重 (hidden_dim, hidden_dim)
        b: 偏置 (hidden_dim,)
    返回:
        h: 当前隐藏状态 (hidden_dim,)
        z: 激活前的值 (hidden_dim,)（缓存供反向传播用）
    """
    z = W_xh @ x + W_hh @ h_prev + b
    h = np.tanh(z)
    return h, z


def count_params(W_xh, W_hh, b):
    """统计 RNN 参数量"""
    return W_xh.size + W_hh.size + b.size


def main():
    print("=" * 60)
    print("=== Ch18: RNN 的结构与展开 ===")
    print("=" * 60)

    # === 参数初始化（与教程手算一致）===
    W_xh = np.array([[0.5, -0.5],
                     [0.3, 0.7]])
    W_hh = np.array([[0.1, 0.2],
                     [-0.1, 0.4]])
    b = np.zeros(2)

    # 初始隐藏状态
    h = np.zeros(2)

    # 输入序列（2维输入）
    sequence = [np.array([1.0, 0.5]),
                np.array([0.0, 1.0])]

    # === 参数共享演示 ===
    print("\n--- 参数共享演示 ---")
    n_params = count_params(W_xh, W_hh, b)
    print(f"参数总数: W_xh({W_xh.size}) + W_hh({W_hh.size}) + b({b.size}) = {n_params} 个")

    # === 逐步计算 ===
    print("\n--- 逐步计算 ---")
    cache = {'h': [h.copy()], 'z': [], 'x': []}

    for t, x in enumerate(sequence):
        print(f"\nt={t+1}: 输入 x={x}")

        # 第1步：W_xh · x
        wxh_x = W_xh @ x
        print(f"  W_xh·x{t+1} = {np.round(wxh_x, 3)}")

        # 第2步：W_hh · h_prev
        whh_h = W_hh @ h
        print(f"  W_hh·h{t} = {np.round(whh_h, 3)}")

        # 第3步：加偏置得 z
        z = wxh_x + whh_h + b
        print(f"  z{t+1} = {np.round(z, 3)}")

        # 第4步：tanh 激活
        h = np.tanh(z)
        print(f"  h{t+1} = {np.round(h, 3)}")

        # 缓存
        cache['h'].append(h.copy())
        cache['z'].append(z.copy())
        cache['x'].append(x.copy())

    # === 参数量与序列长度的关系 ===
    print("\n--- 参数量与序列长度的关系 ---")
    print("（正确认知：RNN 参数量与序列长度无关）")
    for seq_len in [2, 10, 100, 1000]:
        print(f"序列长度={seq_len:4d}, RNN 参数量={n_params}")
    print("→ 不管多长，参数量永远是 10（这就是参数共享）")

    # === 验证 h₁ 和 h₂ 与手算结果一致 ===
    print("\n--- 与教程手算结果对照 ---")
    h1_expected = np.array([0.245, 0.572])
    h2_expected = np.array([-0.346, 0.718])
    h1_actual = cache['h'][1]
    h2_actual = cache['h'][2]

    print(f"h₁ 手算: {h1_expected}, 代码: {np.round(h1_actual, 3)}, 一致: {np.allclose(h1_expected, h1_actual, atol=1e-3)}")
    print(f"h₂ 手算: {h2_expected}, 代码: {np.round(h2_actual, 3)}, 一致: {np.allclose(h2_expected, h2_actual, atol=1e-3)}")


if __name__ == "__main__":
    main()
    print("\n" + "=" * 60)
