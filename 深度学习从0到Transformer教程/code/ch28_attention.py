"""
Ch28 · Attention 机制 — 让模型学会看哪里
=========================================
本文件实现 Attention 的三步走：打分 → 归一化 → 加权求和。
并对比三种打分函数：dot、general、concat。

手算验证小例子：
    h_enc = [[0.5,0.5],[0.8,0.2],[0.3,0.7]]
    h_dec = [0.6, 0.4]
    期望 alpha = [0.331, 0.351, 0.318]
    期望 c     = [0.542, 0.459]

运行：
    cd 深度学习从0到Transformer教程/code
    python ch28_attention.py
"""

import numpy as np


# ============== 1. 数值稳定的 softmax ==============
def softmax_stable(x: np.ndarray, axis: int = -1) -> np.ndarray:
    """
    数值稳定的 softmax：先减最大值再 exp。
    与 Ch03 教的一致。
    """
    x = np.asarray(x, dtype=np.float64)
    x_max = np.max(x, axis=axis, keepdims=True)
    e = np.exp(x - x_max)
    return e / np.sum(e, axis=axis, keepdims=True)


# ============== 2. 三种打分函数 ==============
def score_dot(h_dec: np.ndarray, h_enc_list: np.ndarray) -> np.ndarray:
    """Dot 打分：e_i = h_dec · h_enc_i"""
    return h_enc_list @ h_dec  # (T,)


def score_general(h_dec: np.ndarray, h_enc_list: np.ndarray, W: np.ndarray) -> np.ndarray:
    """General 打分：e_i = h_dec^T · W · h_enc_i"""
    # h_dec: (d,), h_enc_list: (T, d), W: (d, d)
    return h_enc_list @ (W @ h_dec)  # (T,)


def score_concat(h_dec: np.ndarray, h_enc_list: np.ndarray,
                 W: np.ndarray, v: np.ndarray) -> np.ndarray:
    """Concat 打分：e_i = v^T · tanh(W · [h_dec ; h_enc_i])"""
    T = h_enc_list.shape[0]
    # 拼接: [h_dec; h_enc_i] 长度 2d
    concat = np.concatenate([
        np.tile(h_dec, (T, 1)),  # (T, d)
        h_enc_list               # (T, d)
    ], axis=1)                   # (T, 2d)
    hidden = np.tanh(concat @ W)  # (T, d)
    return hidden @ v            # (T,)


# ============== 3. Attention 主体 ==============
def attention(h_dec: np.ndarray, h_enc_list: np.ndarray,
              score_fn=score_dot, **kwargs) -> tuple:
    """
    通用 Attention：打分 → softmax → 加权求和。
    返回 (c, alpha)。
    """
    scores = score_fn(h_dec, h_enc_list, **kwargs)
    alpha = softmax_stable(scores)
    c = np.sum(alpha[:, None] * h_enc_list, axis=0)
    return c, alpha


# ============== 4. 主程序：验证手算小例子 ==============
def main():
    # 教程里的手算小例子
    h_enc = np.array([[0.5, 0.5],
                      [0.8, 0.2],
                      [0.3, 0.7]])
    h_dec = np.array([0.6, 0.4])

    print("=== Ch28 Attention 三步走 (dot 打分) ===")
    scores = score_dot(h_dec, h_enc)
    print(f"打分 (dot): {scores}")
    alpha = softmax_stable(scores)
    print(f"softmax (数值稳定): {alpha}")
    c = np.sum(alpha[:, None] * h_enc, axis=0)
    print(f"上下文 c: {c}")

    # 与手算结果对比
    expected_alpha = np.array([0.331, 0.351, 0.318])
    expected_c = np.array([0.542, 0.459])
    assert np.allclose(alpha, expected_alpha, atol=1e-3), f"alpha 不匹配: {alpha}"
    assert np.allclose(c, expected_c, atol=1e-3), f"c 不匹配: {c}"
    print("✅ 与手算结果一致")

    # === 三种打分函数对比 ===
    print("\n=== 三种打分函数对比 ===")
    d = 2

    # dot
    c_dot, alpha_dot = attention(h_dec, h_enc, score_fn=score_dot)
    print(f"dot:    alpha={alpha_dot.round(3)}, c={c_dot.round(3)}")

    # general (随机初始化 W，固定 seed 保证可复现)
    rng = np.random.default_rng(42)
    W_general = rng.standard_normal((d, d)) * 0.5
    c_gen, alpha_gen = attention(h_dec, h_enc, score_fn=score_general, W=W_general)
    print(f"general: alpha={alpha_gen.round(3)}, c={c_gen.round(3)}")

    # concat
    W_concat = rng.standard_normal((2 * d, d)) * 0.5
    v_concat = rng.standard_normal(d) * 0.5
    c_cat, alpha_cat = attention(h_dec, h_enc, score_fn=score_concat,
                                  W=W_concat, v=v_concat)
    print(f"concat:  alpha={alpha_cat.round(3)}, c={c_cat.round(3)}")

    # 验证 softmax 数值稳定
    print("\n=== 验证 softmax 数值稳定性 ===")
    big_scores = np.array([1000., 1001., 1002.])
    naive = np.exp(big_scores) / np.exp(big_scores).sum()
    stable = softmax_stable(big_scores)
    print(f"大分数 naive softmax (会溢出): {naive}")
    print(f"大分数 stable softmax: {stable}")
    print("✅ stable softmax 不会溢出")

    # === 多步 Decoder Attention 演示 ===
    print("\n=== 多步 Decoder Attention 演示 ===")
    print("假设 Decoder 有 2 步，每步 attention 权重不同：")
    h_dec_steps = [np.array([0.6, 0.4]), np.array([0.3, 0.7])]
    for t, hd in enumerate(h_dec_steps):
        c_t, alpha_t = attention(hd, h_enc, score_fn=score_dot)
        print(f"  Decoder 步 {t+1}: h_dec={hd}, alpha={alpha_t.round(3)}, c_t={c_t.round(3)}")
    print("观察：不同 Decoder 状态会得到不同的 attention 分布——这就是动态看哪里。")

    print("\n✅ Ch28 Attention 演示完成")


if __name__ == "__main__":
    main()
