"""
Ch19: RNN 前向传播
完整实现：(1) 3维输入→2维隐藏→1维输出的 RNN 前向传播 (2) 3个时间步逐步计算 (3) 与手算结果对照
注意：本章参数与 Ch18 不同（3维输入 vs 2维输入），不要混用
"""
import numpy as np


def rnn_forward(X, W_xh, W_hh, W_hy, b_h, b_y, h0):
    """
    RNN 完整前向传播

    参数:
        X: 输入序列，列表 of (input_dim,)
        W_xh: 输入权重 (hidden_dim, input_dim)
        W_hh: 隐藏权重 (hidden_dim, hidden_dim)
        W_hy: 输出权重 (output_dim, hidden_dim)
        b_h: 隐藏偏置 (hidden_dim,)
        b_y: 输出偏置 (output_dim,)
        h0: 初始隐藏状态 (hidden_dim,)
    返回:
        outputs: 每步输出列表
        h_final: 最终隐藏状态
        cache: 缓存中间值供反向传播用
    """
    h = h0.copy()
    outputs = []
    cache = {'h': [h0.copy()], 'z': [], 'x': []}

    for x in X:
        # 隐藏状态更新：z = W_xh·x + W_hh·h_prev + b_h
        z = W_xh @ x + W_hh @ h + b_h
        h = np.tanh(z)
        # 输出：y = W_hy·h + b_y
        y = W_hy @ h + b_y
        outputs.append(y)
        # 缓存（供 Ch20 反向传播使用）
        cache['h'].append(h.copy())
        cache['z'].append(z.copy())
        cache['x'].append(x.copy())

    return outputs, h, cache


def main():
    print("=" * 60)
    print("=== Ch19: RNN 前向传播 ===")
    print("=" * 60)

    # === 参数初始化（与教程手算一致）===
    # 注意：本章用 3 维输入（区别于 Ch18 的 2 维）
    W_xh = np.array([[0.1, 0.2, 0.3],
                     [0.4, 0.5, 0.6]])      # (2, 3): 3维输入 → 2维隐藏
    W_hh = np.array([[0.1, 0.0],
                     [0.0, 0.1]])            # (2, 2): 2维隐藏 → 2维隐藏
    W_hy = np.array([[1.0, -1.0]])           # (1, 2): 2维隐藏 → 1维输出
    b_h = np.zeros(2)
    b_y = np.zeros(1)
    h0 = np.zeros(2)

    # 输入序列（3个时间步，每个 3 维）
    X = [np.array([1.0, 0.0, 0.0]),
         np.array([0.0, 1.0, 0.0]),
         np.array([0.0, 0.0, 1.0])]

    # === 维度说明 ===
    print("\n--- 参数维度说明（与 Ch18 的差异）---")
    print(f"W_xh shape: {W_xh.shape}   ← 3维输入（Ch18 是 2维）")
    print(f"W_hh shape: {W_hh.shape}   ← 2维隐藏（与 Ch18 一致）")
    print(f"W_hy shape: {W_hy.shape}   ← 新增：2维隐藏→1维输出")

    # === 逐步计算 ===
    print("\n--- 逐步计算 ---")
    outputs, h_final, cache = rnn_forward(X, W_xh, W_hh, W_hy, b_h, b_y, h0)

    for t in range(len(X)):
        print(f"\nt={t+1}: x={X[t]}")
        wxh_x = W_xh @ X[t]
        h_prev = cache['h'][t]
        whh_h = W_hh @ h_prev
        z = cache['z'][t]
        h = cache['h'][t+1]
        y = outputs[t]
        print(f"  W_xh·x{t+1} = {np.round(wxh_x, 4)}")
        print(f"  W_hh·h{t} = {np.round(whh_h, 4)}")
        print(f"  z{t+1} = {np.round(z, 4)}")
        print(f"  h{t+1} = {np.round(h, 4)}")
        print(f"  y{t+1} = {np.round(y, 4)}")

    # === 与手算结果对照 ===
    print("\n--- 与手算结果对照 ---")
    expected_y = [-0.2803, -0.2846, -0.2610]
    expected_h = [np.array([0.0997, 0.3799]),
                  np.array([0.2069, 0.4915]),
                  np.array([0.3101, 0.5711])]

    all_pass = True
    for t in range(3):
        y_match = abs(outputs[t][0] - expected_y[t]) < 1e-3
        h_match = np.allclose(cache['h'][t+1], expected_h[t], atol=1e-3)
        status_y = "✅" if y_match else "❌"
        status_h = "✅" if h_match else "❌"
        print(f"y{t+1}: 手算={expected_y[t]}, 代码={outputs[t][0]:.4f}, 一致 {status_y}")
        print(f"h{t+1}: 手算={expected_h[t]}, 代码={np.round(cache['h'][t+1], 4)}, 一致 {status_h}")
        if not (y_match and h_match):
            all_pass = False

    if all_pass:
        print("\n✅ 所有手算结果与代码一致！")
    else:
        print("\n❌ 存在不一致，请检查实现")

    # === 最终隐藏状态 ===
    print(f"\n--- 最终隐藏状态 ---")
    print(f"h₃ = {np.round(h_final, 4)}（这是整个序列的'压缩记忆'）")


if __name__ == "__main__":
    main()
    print("\n" + "=" * 60)
