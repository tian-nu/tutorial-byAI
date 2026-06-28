"""
Ch03 · 概率论最小必要知识 — 配套代码

覆盖：
  - 期望与方差的数值验证
  - softmax 的朴素实现 + 数值稳定实现对比
  - 交叉熵的计算
  - one-hot 编码
  - 概率分布的可视化（文字版）

运行方式：
    python ch03_probability_basics.py
预期输出见每个 print 上方的注释。
"""

import numpy as np


def softmax_naive(z):
    """朴素 softmax：直接按公式算，数值大时会溢出。"""
    e = np.exp(z)
    return e / e.sum()


def softmax_stable(z):
    """数值稳定 softmax：先减最大值，防止 exp 溢出。

    数学上等价于朴素版本：
        exp(z_i - m) / sum(exp(z_j - m))
      = exp(z_i) * exp(-m) / [sum(exp(z_j)) * exp(-m)]
      = exp(z_i) / sum(exp(z_j))
    减最大值不改变结果，但让 exp 的输入都 ≤ 0，避免溢出。
    """
    z = np.asarray(z, dtype=np.float64)
    z_max = np.max(z)
    e = np.exp(z - z_max)
    return e / e.sum()


def cross_entropy(y_true, y_pred, eps=1e-15):
    """交叉熵：H(y_true, y_pred) = -sum(y_true_i * log(y_pred_i))

    eps 是为了防止 log(0)，给预测概率加一个小下界。
    """
    y_pred = np.clip(y_pred, eps, 1.0)   # 防 log(0)
    return -np.sum(y_true * np.log(y_pred))


def main() -> None:
    # ---------------------------------------------------------------
    # 1. 期望与方差：用骰子验证
    #    E[X] = (1+2+3+4+5+6)/6 = 3.5
    #    Var(X) = E[(X - 3.5)²] = 35/12 ≈ 2.9167
    # ---------------------------------------------------------------
    print("=== 期望与方差：骰子 ===")
    dice = np.array([1, 2, 3, 4, 5, 6])
    probs = np.array([1/6] * 6)
    expected = np.sum(probs * dice)
    variance = np.sum(probs * (dice - expected) ** 2)
    print(f"  E[X] = {expected}")          # 3.5
    print(f"  Var(X) = {variance:.4f}")    # 2.9167

    # ---------------------------------------------------------------
    # 2. softmax：z = [2.0, 1.0, 0.1]
    #    exp(2.0)=7.389, exp(1.0)=2.718, exp(0.1)=1.105
    #    总和 = 11.212
    #    p = [0.659, 0.242, 0.099]
    # ---------------------------------------------------------------
    print("\n=== softmax: z = [2.0, 1.0, 0.1] ===")
    z = np.array([2.0, 1.0, 0.1])
    p_naive = softmax_naive(z)
    p_stable = softmax_stable(z)
    print(f"  z = {z}")
    print(f"  exp(z) = {np.exp(z)}")
    print(f"  sum(exp(z)) = {np.exp(z).sum():.4f}")
    print(f"  朴素 softmax   = {p_naive}")     # [0.659 0.242 0.099]
    print(f"  稳定 softmax   = {p_stable}")
    print(f"  两者差异       = {np.max(np.abs(p_naive - p_stable)):.2e}")
    print(f"  概率之和       = {p_stable.sum():.6f}")  # 1.0

    # ---------------------------------------------------------------
    # 3. 数值稳定性的必要性：大数对比
    # ---------------------------------------------------------------
    print("\n=== 数值稳定性：z = [1000, 1001, 1002] ===")
    z_big = np.array([1000.0, 1001.0, 1002.0])
    print(f"  z = {z_big}")
    print(f"  朴素 softmax 会溢出：")
    try:
        p_big_naive = softmax_naive(z_big)
        print(f"    结果 = {p_big_naive}")    # 会得到 [nan nan nan]
    except Exception as e:
        print(f"    报错: {e}")
    print(f"  稳定 softmax 正常工作：")
    p_big_stable = softmax_stable(z_big)
    print(f"    结果 = {p_big_stable}")       # 正常概率

    # ---------------------------------------------------------------
    # 4. one-hot 编码
    #    分类问题中，真实标签通常用 one-hot 表示
    #    比如 3 类分类，真实类别是第 0 类 → [1, 0, 0]
    # ---------------------------------------------------------------
    print("\n=== one-hot 编码 ===")
    num_classes = 3
    true_label = 0
    one_hot = np.zeros(num_classes)
    one_hot[true_label] = 1.0
    print(f"  类别数 = {num_classes}, 真实标签 = {true_label}")
    print(f"  one-hot = {one_hot}")           # [1. 0. 0.]
    print(f"  解释：只有真实类别位置是 1，其他都是 0")

    # ---------------------------------------------------------------
    # 5. 交叉熵：H(y_true, y_pred) = -sum(y_true * log(y_pred))
    #    y_true = [1, 0, 0], y_pred = [0.659, 0.242, 0.099]
    #    H = -log(0.659) = 0.417
    # ---------------------------------------------------------------
    print("\n=== 交叉熵 ===")
    y_true = np.array([1.0, 0.0, 0.0])           # one-hot
    y_pred = np.array([0.659, 0.242, 0.099])     # softmax 输出
    ce = cross_entropy(y_true, y_pred)
    print(f"  y_true (one-hot) = {y_true}")
    print(f"  y_pred (softmax) = {y_pred}")
    print(f"  交叉熵 H = {ce:.4f}")              # 0.417

    # 对比：预测越准，交叉熵越小
    print("\n=== 交叉熵 vs 预测准确度 ===")
    y_pred_perfect = np.array([0.99, 0.005, 0.005])  # 几乎全押对
    y_pred_wrong = np.array([0.1, 0.1, 0.8])         # 押错
    print(f"  预测很准 {y_pred_perfect} → H = {cross_entropy(y_true, y_pred_perfect):.4f}")
    print(f"  预测中等 {y_pred} → H = {cross_entropy(y_true, y_pred):.4f}")
    print(f"  预测错误 {y_pred_wrong} → H = {cross_entropy(y_true, y_pred_wrong):.4f}")
    print("  → 预测越接近真实，交叉熵越小；预测越偏离，交叉熵越大")

    # ---------------------------------------------------------------
    # 6. 为什么交叉熵用 log？数值演示
    #    log 在 [0,1] 上是负的，且当 p→0 时 log(p)→-∞
    #    这意味着：真实类别预测概率越接近 0，惩罚越大（趋向无穷）
    # ---------------------------------------------------------------
    print("\n=== 为什么交叉熵用 log？===")
    print("  真实类别 y_true=1，预测概率 p 不同时的 -log(p)：")
    for p in [0.99, 0.7, 0.5, 0.1, 0.01, 0.001]:
        print(f"    p = {p:.3f} → -log(p) = {-np.log(p):.4f}")
    print("  → p 越接近 0，-log(p) 越大（趋向无穷）")
    print("  → 这就是 log 的作用：对'把真类预测成低概率'的严重惩罚")


if __name__ == "__main__":
    main()
