"""
Ch29 · Self-Attention — 自己看自己
===================================
完整实现 Self-Attention 的前向过程，验证手算小例子：

    X = [[1.0, 0.5], [0.3, 0.7], [0.8, 0.2]]
    W_Q = W_K = W_V = I_2 (单位矩阵)
    期望输出 out[0] = [0.749, 0.458]

运行：
    cd 深度学习从0到Transformer教程/code
    python ch29_self_attention.py
"""

import numpy as np


# ============== 1. 数值稳定的 softmax ==============
def softmax(x: np.ndarray, axis: int = -1) -> np.ndarray:
    """数值稳定的 softmax：先减最大值再 exp。"""
    x = np.asarray(x, dtype=np.float64)
    x_max = np.max(x, axis=axis, keepdims=True)
    e = np.exp(x - x_max)
    return e / np.sum(e, axis=axis, keepdims=True)


# ============== 2. Self-Attention 核心 ==============
def self_attention(X: np.ndarray, WQ: np.ndarray, WK: np.ndarray, WV: np.ndarray):
    """
    Self-Attention 完整实现。
    X:  (T, d_model)
    WQ: (d_model, d_k)
    WK: (d_model, d_k)
    WV: (d_model, d_v)
    返回 out (T, d_v), alpha (T, T)
    """
    Q = X @ WQ   # (T, d_k)
    K = X @ WK   # (T, d_k)
    V = X @ WV   # (T, d_v)

    d_k = K.shape[-1]
    scores = Q @ K.T / np.sqrt(d_k)   # (T, T) 缩放点积
    alpha = softmax(scores, axis=-1)  # 对每行做 softmax
    out = alpha @ V                   # (T, d_v)
    return out, alpha, scores


# ============== 3. 主程序：完整手算验证 ==============
def main():
    # === 教程里的手算小例子 ===
    X = np.array([[1.0, 0.5],
                  [0.3, 0.7],
                  [0.8, 0.2]])
    W = np.eye(2)  # 简化为单位矩阵，让 Q=K=V=X

    print("=== Ch29 Self-Attention 完整流程 ===\n")
    print(f"X:\n {X}\n")

    Q = X @ W
    K = X @ W
    V = X @ W
    print(f"Q (= X):\n {Q}\n")
    print(f"K (= X):\n {K}\n")
    print(f"V (= X):\n {V}\n")

    # 第 1 步：QK^T
    QKT = Q @ K.T
    print(f"QK^T:\n {QKT}\n")
    # 手算预期
    expected_QKT = np.array([[1.25, 0.65, 0.90],
                             [0.65, 0.58, 0.38],
                             [0.90, 0.38, 0.68]])
    assert np.allclose(QKT, expected_QKT, atol=1e-3), f"QK^T 不匹配: {QKT}"
    print(f"✅ QK^T 与手算一致\n")

    # 第 2 步：除以 sqrt(d_k)
    d_k = 2
    sqrt_dk = np.sqrt(d_k)
    scaled = QKT / sqrt_dk
    print(f"QK^T / sqrt(d_k)  (d_k={d_k}, sqrt={sqrt_dk:.4f}):\n {scaled}\n")
    expected_scaled = np.array([[0.884, 0.460, 0.636],
                                [0.460, 0.410, 0.269],
                                [0.636, 0.269, 0.481]])
    assert np.allclose(scaled, expected_scaled, atol=1e-3), f"scaled 不匹配: {scaled}"
    print(f"✅ 缩放后矩阵与手算一致\n")

    # 第 3 步：softmax 每行
    alpha = softmax(scaled, axis=-1)
    print(f"attention 权重 alpha:\n {alpha}\n")
    expected_alpha_row0 = np.array([0.411, 0.269, 0.321])
    assert np.allclose(alpha[0], expected_alpha_row0, atol=1e-3), f"alpha[0] 不匹配: {alpha[0]}"
    print(f"✅ alpha[0] = {alpha[0].round(3)} 与手算 [0.411, 0.269, 0.321] 一致\n")

    # 第 4 步：alpha @ V
    out = alpha @ V
    print(f"输出 out:\n {out}\n")
    # 教程里用 3 位小数 α 手算得 [0.749, 0.458]；
    # 全精度 α 算出来是 [0.748, 0.458]，差异来自分步四舍五入。
    # 容差放宽到 2e-3 以兼容两种算法。
    expected_out_row0 = np.array([0.749, 0.458])
    assert np.allclose(out[0], expected_out_row0, atol=2e-3), f"out[0] 不匹配: {out[0]}"
    print(f"✅ out[0] = {out[0].round(3)} ≈ [0.749, 0.458] (3位 α 手算) / [0.748, 0.458] (全精度)\n")

    # === 验证不缩放会发生什么 ===
    print("=== 验证：不缩放时 softmax 会变 one-hot 吗？===")
    # 假设 d_k 很大，点积方差很大
    rng = np.random.default_rng(0)
    d_k_big = 512
    q_big = rng.standard_normal(d_k_big)
    k_big = rng.standard_normal(d_k_big)
    big_dot = q_big @ k_big  # 不缩放，方差约 d_k_big = 512
    print(f"d_k={d_k_big} 时的点积值（不缩放）: {big_dot:.2f}")
    print(f"  理论标准差: sqrt({d_k_big}) = {np.sqrt(d_k_big):.2f}")
    # 三个 key 的例子
    keys = rng.standard_normal((3, d_k_big))
    scores_unscaled = keys @ q_big
    scores_scaled = scores_unscaled / np.sqrt(d_k_big)
    alpha_unscaled = softmax(scores_unscaled)
    alpha_scaled = softmax(scores_scaled)
    print(f"  不缩放 softmax: {alpha_unscaled.round(3)} (接近 one-hot，梯度会消失)")
    print(f"  缩放后 softmax: {alpha_scaled.round(3)} (有区分度，梯度健康)")

    # === 验证整行 self_attention 函数 ===
    print("\n=== 一次性调用 self_attention 函数 ===")
    out2, alpha2, scores2 = self_attention(X, W, W, W)
    assert np.allclose(out, out2)
    print(f"输出:\n {out2}")
    print("✅ 函数返回结果与分步一致")

    print("\n✅ Ch29 Self-Attention 演示完成")


if __name__ == "__main__":
    main()
