"""
Ch14: 前向传播 — 信号从前往后走
完整实现：(1) 细纲要求的 3→4→2 手动计算 (2) 批量前向传播 (3) 维度追踪
"""
import numpy as np


def relu(z):
    """ReLU 激活函数"""
    return np.maximum(0, z)


def softmax(z):
    """
    Softmax 函数
    关键技巧：减去最大值防止 exp() 溢出
    数学上等价：softmax(z) = softmax(z - c)，对任意常数 c
    """
    e = np.exp(z - np.max(z))
    return e / e.sum()


def forward_step_by_step():
    """逐步展示 3维输入 → 4维隐藏 → 2维输出的完整前向传播"""
    print("\n--- 手动计算验证 ---")

    # === 输入 ===
    x = np.array([1.0, 0.5, -1.0])
    print(f"输入 x = {x}")

    # === 第 1 层参数（隐藏层：4个神经元）===
    W1 = np.array([
        [1, 0, -1],   # 隐藏神经元 1
        [0, 1, 1],    # 隐藏神经元 2
        [-1, 1, 0],   # 隐藏神经元 3
        [1, 1, 1]     # 隐藏神经元 4
    ], dtype=float)
    b1 = np.zeros(4)
    print(f"W₁ shape = {W1.shape} (4个隐藏神经元 × 3个输入)")

    # --- z⁽¹⁾ 计算（逐元素展开）---
    print(f"\n第 1 层（隐藏层）:")
    z1 = W1 @ x + b1
    print(f"  z⁽¹⁾ = W₁ @ x + b₁ = {z1}")

    # 展示每个 z 值的来源
    for i in range(4):
        dot_val = np.dot(W1[i], x)
        print(f"    z{i+1} = {W1[i]}·{x} + {b1[i]} = {dot_val:.1f} + {b1[i]} = {z1[i]:.1f}")

    # --- a⁽¹⁾ = ReLU ---
    a1 = relu(z1)
    print(f"  a⁽¹⁾ = ReLU(z⁽¹⁾) = {a1}")

    # === 第 2 层参数（输出层：2个神经元）===
    W2 = np.array([
        [1, 0, 0, 1],  # 输出神经元 1
        [0, 1, 1, 0]   # 输出神经元 2
    ], dtype=float)
    b2 = np.zeros(2)
    print(f"\n第 2 层（输出层）:")
    print(f"W₂ shape = {W2.shape} (2个输出 × 4个隐藏)")

    # --- z⁽²⁾ 计算 ---
    z2 = W2 @ a1 + b2
    print(f"  z⁽²⁾ = W₂ @ a⁽¹⁾ + b₂ = {z2}")

    for i in range(2):
        dot_val = np.dot(W2[i], a1)
        print(f"    z'{i+1} = {W2[i]}·{a1} + {b2[i]} = {dot_val:.1f} + {b2[i]} = {z2[i]:.1f}")

    # --- softmax 输出 ---
    y_hat = softmax(z2)
    print(f"  ŷ = softmax(z⁽²⁾) = {y_hat}")

    # --- 验证 ---
    expected = np.array([0.9241, 0.0759])
    if np.allclose(y_hat, expected, atol=0.01):
        print(f"\n✅ 与手算一致！")
    else:
        print(f"\n❌ 与手算不一致！期望约 {expected}")

    return x, W1, b1, a1, z1, W2, b2, y_hat


def batch_forward():
    """批量前向传播：同时处理多个样本"""
    print("\n--- 批量前向传播演示 ---")

    # 4 个样本，每个 3 维
    X_batch = np.array([
        [1.0, 0.5, -1.0],
        [0.0, 1.0, 0.5],
        [-1.0, -0.5, 0.0],
        [0.0, 0.0, 1.0],
    ])
    print(f"批量输入 shape: {X_batch.shape}")  # (4, 3)

    W1 = np.array([[1,0,-1],[0,1,1],[-1,1,0],[1,1,1]], dtype=float)
    b1 = np.zeros(4)
    W2 = np.array([[1,0,0,1],[0,1,1,0]], dtype=float)
    b2 = np.zeros(2)

    # 批量计算（矩阵乘法自动处理所有样本）
    Z1 = X_batch @ W1.T + b1   # (4,3) @ (3,4) + (4,) = (4,4)
    A1 = relu(Z1)               # (4,4)
    Z2 = A1 @ W2.T + b2         # (4,4) @ (4,2) + (2,) = (4,2)
    Y_hat = np.apply_along_axis(softmax, 1, Z2)  # 对每行做 softmax

    print(f"输出 shape: {Y_hat.shape}")  # (4, 2)

    predictions = np.argmax(Y_hat, axis=1)
    for i in range(len(X_batch)):
        print(f"  第{i+1}个样本: {Y_hat[i].round(4)} -> 预测类别 {predictions[i]}")


if __name__ == "__main__":
    print("=" * 55)
    print("=== Ch14: 前向传播 — 信号从前往后走 ===")
    print("=" * 55)

    forward_step_by_step()
    batch_forward()

    print("\n" + "=" * 55)
