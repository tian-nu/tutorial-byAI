"""
Ch20: RNN 反向传播 — BPTT
完整实现：(1) 2个时间步前向传播 (2) BPTT 手动反向传播 (3) 数值梯度验证
关键：W_hh 用对角矩阵简化手算；损失函数用 MSE 演示 BPTT 机制
"""
import numpy as np


def rnn_forward(X, params, h0):
    """
    RNN 前向传播，缓存所有中间值供 BPTT 用

    参数:
        X: 输入序列（列表 of 数组）
        params: dict 包含 W_xh, W_hh, W_hy
        h0: 初始隐藏状态
    返回:
        cache: dict 包含 h, z, y 列表
    """
    W_xh, W_hh, W_hy = params['W_xh'], params['W_hh'], params['W_hy']
    b_h = params.get('b_h', np.zeros(W_hh.shape[0]))
    b_y = params.get('b_y', np.zeros(W_hy.shape[0]))

    h = h0.copy()
    cache = {'h': [h0.copy()], 'z': [], 'y': [], 'x': []}

    for x in X:
        z = W_xh @ x + W_hh @ h + b_h
        h = np.tanh(z)
        y = W_hy @ h + b_y
        cache['h'].append(h.copy())
        cache['z'].append(z.copy())
        cache['y'].append(y.copy())
        cache['x'].append(x.copy())

    return cache


def compute_loss(X, target, params, h0):
    """
    MSE 损失（只在最后一步有损失，匹配教程手算）
    L = (1/2) * (y_T - target)²

    参数:
        target: 最后一个时间步的真实值（标量）
    """
    cache = rnn_forward(X, params, h0)
    y_last = cache['y'][-1][0]
    loss = 0.5 * (y_last - target) ** 2
    return loss


def rnn_bptt(X, target, params, cache):
    """
    RNN 反向传播（BPTT）
    沿时间倒序累加梯度
    损失只在最后一个时间步计算（与教程手算一致）

    参数:
        X: 输入序列
        target: 最后一个时间步的真实值（标量）
        params: dict 包含 W_xh, W_hh, W_hy
        cache: 前向传播的缓存
    返回:
        dW_xh, dW_hh, dW_hy: 各参数的梯度
    """
    W_xh, W_hh, W_hy = params['W_xh'], params['W_hh'], params['W_hy']
    h_list = cache['h']   # [h0, h1, h2]
    y_list = cache['y']   # [y1, y2]

    dW_xh = np.zeros_like(W_xh)
    dW_hh = np.zeros_like(W_hh)
    dW_hy = np.zeros_like(W_hy)

    hidden_dim = W_hh.shape[0]
    dh_next = np.zeros(hidden_dim)  # 从 t+1 传回来的梯度
    T = len(X)

    # 从最后一个时间步倒着遍历
    for t in reversed(range(T)):
        # 输出层梯度（MSE: ∂L/∂y = y - target）
        # 只有最后一步 t=T-1 有损失，其他步 dy = 0
        if t == T - 1:
            dy = np.array([y_list[t][0] - target])  # shape (1,)
        else:
            dy = np.zeros(1)
        dW_hy += np.outer(dy, h_list[t + 1])       # (1, hidden)

        # 隐藏层梯度 = 来自输出 + 来自下一步
        dh = dy @ W_hy + dh_next                    # (hidden,)
        # tanh 导数: 1 - h²
        dh_raw = dh * (1 - h_list[t + 1] ** 2)      # (hidden,)

        # 累加 W_hh 和 W_xh 的梯度（沿时间累加！）
        dW_hh += np.outer(dh_raw, h_list[t])        # (hidden, hidden)
        dW_xh += np.outer(dh_raw, X[t])             # (hidden, input)

        # 传给下一步（t-1）
        dh_next = dh_raw @ W_hh

    return dW_xh, dW_hh, dW_hy


def numerical_gradient(f, params, key, indices, eps=1e-5):
    """
    数值梯度（中心差分法）
    """
    arr = params[key]
    original = arr[indices].copy()

    arr[indices] = original + eps
    loss_plus = f(params)

    arr[indices] = original - eps
    loss_minus = f(params)

    arr[indices] = original  # 恢复！
    return (loss_plus - loss_minus) / (2 * eps)


def main():
    print("=" * 60)
    print("=== Ch20: RNN 反向传播 BPTT ===")
    print("=" * 60)

    # === 损失函数说明 ===
    print("\n--- 损失函数说明 ---")
    print("本章用 MSE 损失演示 BPTT 机制（梯度公式更简洁）")
    print("实际 NLP 任务多用交叉熵损失，见 Ch21")

    # === 简化说明 ===
    print("\n--- 简化说明 ---")
    print("W_hh 用对角矩阵简化手算；实际中 W_hh 是满矩阵")

    # === 参数初始化（与教程手算一致）===
    W_xh = np.array([[1.0, 0.0],
                     [0.0, 1.0]])           # 2×2 单位矩阵
    W_hh = np.array([[0.5, 0.0],
                     [0.0, 0.5]])           # 2×2 对角矩阵（关键简化）
    W_hy = np.array([[1.0, 1.0]])           # 1×2
    params = {'W_xh': W_xh, 'W_hh': W_hh, 'W_hy': W_hy}
    h0 = np.zeros(2)

    # 输入序列（2个时间步）
    X = [np.array([1.0, 0.5]),
         np.array([0.0, 1.0])]

    # === 前向传播 ===
    print("\n--- 前向传播结果 ---")
    cache = rnn_forward(X, params, h0)
    h1 = cache['h'][1]
    h2 = cache['h'][2]
    y2 = cache['y'][1][0]
    target = 1.0
    L = 0.5 * (y2 - target) ** 2

    print(f"h₁ = {np.round(h1, 3)}")
    print(f"h₂ = {np.round(h2, 3)}")
    print(f"y₂ = {y2:.3f}")
    print(f"target = {target}")
    print(f"L = {L:.4f}")

    # === BPTT 反向传播 ===
    print("\n--- BPTT 反向传播 ---")
    dW_xh, dW_hh, dW_hy = rnn_bptt(X, target, params, cache)

    # 手动复算 δh₂, ∂L/∂h₁, δh₁ 供对照
    dy = y2 - target
    dh2 = dy * W_hy[0]                          # [0.204, 0.204]
    tanh_prime_z2 = 1 - h2 ** 2
    delta_h2 = dh2 * tanh_prime_z2              # δh₂
    dh1 = W_hh.T @ delta_h2                     # ∂L/∂h₁
    tanh_prime_z1 = 1 - h1 ** 2
    delta_h1 = dh1 * tanh_prime_z1              # δh₁

    print(f"δh₂ = {np.round(delta_h2, 3)}")
    print(f"∂L/∂h₁ = {np.round(dh1, 3)}")
    print(f"δh₁ = {np.round(delta_h1, 3)}")

    print(f"\n∂L/∂W_hh =")
    for row in dW_hh:
        print(f"  {np.round(row, 3)}")

    # === 数值梯度验证 ===
    print("\n--- 数值梯度验证 ---")

    def loss_fn(p):
        return compute_loss(X, target, p, h0)

    print(f"{'参数':<12s} {'解析梯度':>10s} {'数值梯度':>10s} {'差异':>12s} {'状态':>4s}")
    print("-" * 55)

    test_cases = [
        ('W_hh', (0, 0), dW_hh[0, 0]),
        ('W_hh', (0, 1), dW_hh[0, 1]),
        ('W_hh', (1, 0), dW_hh[1, 0]),
        ('W_hh', (1, 1), dW_hh[1, 1]),
        ('W_xh', (0, 0), dW_xh[0, 0]),
        ('W_xh', (1, 1), dW_xh[1, 1]),
        ('W_hy', (0, 0), dW_hy[0, 0]),
        ('W_hy', (0, 1), dW_hy[0, 1]),
    ]

    all_pass = True
    for key, idx, analytic in test_cases:
        num = numerical_gradient(loss_fn, params, key, idx)
        diff = abs(analytic - num)
        status = "✅" if diff < 1e-7 else "❌"
        if diff >= 1e-7:
            all_pass = False
        print(f"{key}{str(idx):<8s} {analytic:>10.6f} {num:>10.6f} {diff:>12.8f} {status:>4s}")

    if all_pass:
        print("\n✅ 所有梯度验证通过！差异均 < 1e-7")
    else:
        print("\n❌ 存在梯度不一致，请检查 BPTT 实现")

    # === 与教程手算结果对照 ===
    print("\n--- 与教程手算结果对照 ---")
    # 教程手算用 3 位小数（tanh(1.0)≈0.762 等），实际值更精确
    # 这里用较宽松的容差对照（数值梯度验证已精确通过）
    expected_dW_hh = np.array([[0.135, 0.082],
                               [0.045, 0.027]])
    match = np.allclose(dW_hh, expected_dW_hh, atol=2e-3)
    print(f"∂L/∂W_hh 手算: {expected_dW_hh.tolist()}")
    print(f"∂L/∂W_hh 代码: {np.round(dW_hh, 3).tolist()}")
    print(f"一致（容差 2e-3，因教程手算 tanh 值取 3 位小数）: {'✅' if match else '❌'}")


if __name__ == "__main__":
    main()
    print("\n" + "=" * 60)
