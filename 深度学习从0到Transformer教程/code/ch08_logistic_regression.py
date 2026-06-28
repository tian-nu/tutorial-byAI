"""
Ch08 · 逻辑回归 —— 手写实现
关键点：
1. sigmoid 函数的实现
2. 交叉熵损失的计算（带数值稳定性保护）
3. 维度处理：X(n,1), w(1,), 正确使用 @ 运算符
"""

import numpy as np


def sigmoid(z):
    """Sigmoid 函数: σ(z) = 1 / (1 + e^(-z))"""
    return 1 / (1 + np.exp(-z))


def cross_entropy_loss(y_true, y_pred):
    """
    二分类交叉熵损失: L = -mean(y*log(p) + (1-y)*log(1-p))
    加 1e-15 防止 log(0)
    """
    eps = 1e-15
    y_pred = np.clip(y_pred, eps, 1 - eps)  # 把 p 限制在 [eps, 1-eps]
    return -np.mean(y_true * np.log(y_pred) + (1 - y_true) * np.log(1 - y_pred))


def main():
    print("=" * 60)
    print("=== 逻辑回归 — 手写实现 ===")
    print("=" * 60)

    # ========== 1. 准备数据 ==========
    # 4 个样本，每个样本 1 个特征
    X = np.array([[2.0], [3.0], [1.0], [0.5]], dtype=float)
    y = np.array([1, 1, 0, 0], dtype=float)

    print("\n【数据】")
    print(f"X shape: {X.shape}  (4个样本, 1个特征)")
    print(f"X:\n{X}")
    print(f"y: {y}")

    # ========== 2. 初始化参数（注意维度！）==========
    # w 必须是 shape (1,) 的数组，不是标量！
    w = np.array([0.0])  # shape (1,)
    b = 0.0              # 标量
    lr = 0.1             # 学习率
    epochs = 200         # 训练轮数

    print(f"\n【初始参数】w={w}, b={b}")

    # ========== 3. 训练循环 ==========
    print("\n【训练中...】")
    for epoch in range(epochs):
        # --- 前向传播 ---
        z = X @ w + b           # (4,1) @ (1,) = (4,)  ← 关键维度操作
        p = sigmoid(z)          # (4,)

        # --- 计算损失 ---
        loss = cross_entropy_loss(y, p)

        # --- 计算梯度 ---
        # ∂L/∂w = mean((p - y) * x)，注意 X 要 flatten 到一维
        dw = np.mean((p - y) * X.flatten())  # 标量
        db = np.mean(p - y)                    # 标量

        # --- 更新参数 ---
        w -= lr * dw  # 更新 w 数组中的元素
        b -= lr * db

        if epoch in (0, 50, 100, 150, 199):
            print(f"epoch {epoch:3d}: w={w[0]:.4f}, b={b:.4f}, loss={loss:.4f}")

    # ========== 4. 最终结果 ==========
    print(f"\n{'='*60}")
    print(f"【最终结果】")
    print(f"w = {w[0]:.4f}")
    print(f"b = {b:.4f}")
    print(f"最终损失 = {cross_entropy_loss(y, sigmoid(X @ w + b)):.6f}")

    # 决策边界: wx + b = 0  =>  x = -b/w
    boundary = -b / w[0]
    print(f"\n决策边界: x = {-b/w[0]:.2f}")
    print(f"  x > {boundary:.2f} → 预测为类别 1")
    print(f"  x ≤ {boundary:.2f} → 预测为类别 0")

    # ========== 5. 预测验证 ==========
    print(f"\n【预测验证】")
    z_test = X @ w + b
    p_test = sigmoid(z_test)
    predictions = (p_test > 0.5).astype(int)

    correct = 0
    for i in range(len(X)):
        status = "✅" if predictions[i] == int(y[i]) else "❌"
        if predictions[i] == int(y[i]):
            correct += 1
        print(f"  x={X[i][0]:.1f} → p={p_test[i]:.2f} → "
              f"预测={predictions[i]} (真实={int(y[i])}) {status}")

    accuracy = correct / len(y) * 100
    print(f"\n准确率: {accuracy:.0f}% ({correct}/{len(y)})")

    # ========== 6. Sigmoid 演示 ==========
    print(f"\n【Sigmoid 函数演示】")
    test_z = np.array([-3, -1, 0, 1, 3])
    print(f"{'z':>5s} | {'σ(z)':>10s}")
    print("-" * 20)
    for zi in test_z:
        print(f"{zi:5.1f} | {sigmoid(zi):10.6f}")


if __name__ == "__main__":
    main()
