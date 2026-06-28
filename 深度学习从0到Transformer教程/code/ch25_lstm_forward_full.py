"""
Ch25 · LSTM 前向传播完整推导
=============================
把 Ch24 的单步 LSTM 沿时间轴展开 4 步，手算每步的 h_t 和 C_t。

简化说明：
  - 4 个门共用同一个对角结构矩阵 W（只为手算可跟随）
  - 实际 LSTM 的 W_f/W_i/W_C/W_o 是 4 个不同的满矩阵
  - 同时提供"标准版"（4 门独立）和 PyTorch 对比

运行：python ch25_lstm_forward_full.py
"""

import numpy as np


def sigmoid(x):
    return 1 / (1 + np.exp(-x))


def lstm_forward_simple(X, W, b=None):
    """简化版 LSTM 前向（4 门共用 W，对角结构，与手算一致）。

    Args:
        X: 输入序列，shape (T, d)
        W: 共用权重矩阵，shape (h, h+d)
        b: 偏置，shape (h,)，默认为 0

    Returns:
        h_final, C_final, history: 最终状态和每步历史
    """
    T = X.shape[0]
    h = W.shape[0]
    if b is None:
        b = np.zeros(h)
    h_t = np.zeros(h)
    C_t = np.zeros(h)
    history = []
    for t in range(T):
        concat = np.concatenate([h_t, X[t]])
        z = W @ concat + b
        f_t = sigmoid(z)         # 简化：4 门共用 W
        i_t = sigmoid(z)
        C_bar = np.tanh(z)
        o_t = sigmoid(z)
        C_t = f_t * C_t + i_t * C_bar
        h_t = o_t * np.tanh(C_t)
        history.append((h_t.copy(), C_t.copy()))
    return h_t, C_t, history


def lstm_forward_standard(X, W_f, W_i, W_C, W_o, b_f, b_i, b_C, b_o):
    """标准版 LSTM 前向（4 门独立 W，与 PyTorch 一致）。

    Args:
        X: 输入序列，shape (T, d)
        W_f, W_i, W_C, W_o: 4 组独立权重，shape (h, h+d)
        b_f, b_i, b_C, b_o: 4 组偏置，shape (h,)

    Returns:
        h_final, C_final, history
    """
    T = X.shape[0]
    h = W_f.shape[0]
    h_t = np.zeros(h)
    C_t = np.zeros(h)
    history = []
    for t in range(T):
        concat = np.concatenate([h_t, X[t]])
        f_t = sigmoid(W_f @ concat + b_f)
        i_t = sigmoid(W_i @ concat + b_i)
        C_bar = np.tanh(W_C @ concat + b_C)
        o_t = sigmoid(W_o @ concat + b_o)
        C_t = f_t * C_t + i_t * C_bar
        h_t = o_t * np.tanh(C_t)
        history.append((h_t.copy(), C_t.copy()))
    return h_t, C_t, history


def main():
    print("=" * 60)
    print("Ch25: LSTM 前向传播完整推导")
    print("=" * 60)

    # === 输入序列（T=4，2 维）===
    X = np.array([[1.0, 0.5],
                  [0.3, 0.7],
                  [0.8, 0.2],
                  [0.4, 0.6]])

    # === 第 1 部分：手算简化版（4 门共用 W，对角结构）===
    print()
    print("--- 手算简化版（4 门共用 W，对角结构）---")
    print("W = [[0.5, 0.0, 0.5, 0.0],")
    print("     [0.0, 0.5, 0.0, 0.5]]  ← 每个单元只看对应 h 和 x 分量")
    print("偏置 b = [0, 0]")
    print()

    W = np.array([[0.5, 0.0, 0.5, 0.0],
                  [0.0, 0.5, 0.0, 0.5]])

    h_final, C_final, history = lstm_forward_simple(X, W)

    for t, (h_t, C_t) in enumerate(history, 1):
        print(f"t={t}: h_t={h_t.round(3)}, C_t={C_t.round(3)}")

    print()
    print(f"最终: h_4 = {h_final.round(3)}, C_4 = {C_final.round(3)}")

    # 验证手算值（与教程一致，允许 ±0.002 舍入误差）
    expected_h4 = [0.246, 0.208]
    assert np.allclose(h_final.round(3), expected_h4, atol=0.002), \
        f"h_4 不匹配: {h_final.round(3)}"
    print(f"✅ h_4 = {h_final.round(3)} 与教程一致 (期望 {expected_h4})")

    # === 第 2 部分：标准版（4 门独立 W）===
    print()
    print("--- 标准版（4 门独立 W，与 PyTorch 一致）---")
    print("使用 Ch24 的 4 组权重，展示真实 LSTM 的多步前向")
    print()

    h_prev_dim = 2
    x_dim = 2
    # 4 组独立权重（与 Ch24 相同）
    W_f = np.array([[0.1, 0.2, 0.3, 0.4],
                    [0.5, 0.6, 0.7, 0.8]])
    W_i = np.array([[0.2, 0.1, 0.3, 0.5],
                    [0.4, 0.3, 0.2, 0.1]])
    W_C = np.array([[0.1, 0.3, 0.2, 0.4],
                    [0.5, 0.1, 0.3, 0.2]])
    W_o = np.array([[0.3, 0.2, 0.1, 0.4],
                    [0.2, 0.4, 0.3, 0.1]])
    b = np.zeros(2)

    h_std, C_std, hist_std = lstm_forward_standard(
        X, W_f, W_i, W_C, W_o, b, b, b, b
    )

    for t, (h_t, C_t) in enumerate(hist_std, 1):
        print(f"t={t}: h_t={h_t.round(3)}, C_t={C_t.round(3)}")

    print()
    print(f"最终: h_4 = {h_std.round(3)}, C_4 = {C_std.round(3)}")
    print("（4 门独立 W 的结果与简化版不同，因为权重不同）")

    # === 第 3 部分：PyTorch nn.LSTM 对比 ===
    print()
    print("--- PyTorch nn.LSTM 对比 ---")
    try:
        import torch
        import torch.nn as nn

        # 用随机权重演示 PyTorch LSTM 的接口
        lstm = nn.LSTM(input_size=2, hidden_size=2, batch_first=True,
                       num_layers=1, bias=False)
        # 把 PyTorch 的权重设为我们的简化版（4 门共用 W）
        # PyTorch 的 weight_ih_l0 形状是 (4*h, input_size)
        # weight_hh_l0 形状是 (4*h, hidden_size)
        # 4 门顺序是 [i, f, g(C̃), o]
        with torch.no_grad():
            # 构造 weight_ih_l0：4 门对应的输入权重
            # 简化版中 W = [[0.5, 0.0, 0.5, 0.0],
            #              [0.0, 0.5, 0.0, 0.5]]
            # 拆分为 W_h (h部分) 和 W_x (x部分)
            W_h = W[:, :2]  # 前 2 列对应 h
            W_x = W[:, 2:]  # 后 2 列对应 x
            # PyTorch 4 门顺序是 [i, f, g, o]，我们简化版 4 门相同
            # 所以每门都用相同的 W_h 和 W_x
            lstm.weight_ih_l0.copy_(torch.tensor(
                np.vstack([W_x, W_x, W_x, W_x]), dtype=torch.float32))
            lstm.weight_hh_l0.copy_(torch.tensor(
                np.vstack([W_h, W_h, W_h, W_h]), dtype=torch.float32))

        X_torch = torch.tensor(X, dtype=torch.float32).unsqueeze(0)  # (1, T, d)
        out, (h_n, c_n) = lstm(X_torch)

        print(f"输入 shape: {X_torch.shape} (batch=1, T=4, d=2)")
        print(f"输出 shape: {out.shape} (batch=1, T=4, h=2)")
        print(f"最终 h_n shape: {h_n.shape} (1, 1, 2)")
        print(f"最终 c_n shape: {c_n.shape} (1, 1, 2)")
        print(f"最终 h_n = {h_n.detach().numpy().round(3).flatten()}")
        print(f"最终 c_n = {c_n.detach().numpy().round(3).flatten()}")

        # 验证 PyTorch 与简化版一致（注意 PyTorch 4 门顺序是 [i,f,g,o]）
        # 由于简化版 4 门相同，顺序不影响结果
        print()
        print(f"NumPy 简化版 h_4 = {h_final.round(3)}")
        print(f"PyTorch     h_n = {h_n.detach().numpy().round(3).flatten()}")
        print("（两者应一致，因为简化版 4 门相同）")

    except ImportError:
        print("（未安装 PyTorch，跳过对比。安装后可运行: pip install torch）")

    # === 第 4 部分：关键观察 ===
    print()
    print("--- 关键观察 ---")
    print("C_t 沿时间累积（加法更新），h_t 每步基于 C_t 重新读出。")
    print("这就是 LSTM 的'记忆通道'——C_t 不被重写，只被按比例保留+写入。")
    print()
    print("对比 RNN: h_t = tanh(W·h_{t-1} + ...) 每步重写，旧信息被覆盖。")
    print("LSTM 的 C_t 像传送带，RNN 的 h_t 像黑板。")
    print()
    print("可视化演示见 25_lstm_vs_rnn_memory_visual.html")


if __name__ == "__main__":
    main()
