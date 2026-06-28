"""
Ch06 · 线性回归 —— 手写梯度下降
完整展示：数据准备 → 前向传播 → 计算损失 → 计算梯度 → 更新参数
"""

import numpy as np


def main():
    print("=" * 55)
    print("=== 线性回归 — 手写梯度下降 ===")
    print("=" * 55)

    # ========== 1. 准备数据 ==========
    # X=[1,2,3,4], Y=[2,4,6,8]  完美线性关系 y = 2x
    X = np.array([[1], [2], [3], [4]], dtype=float)
    y = np.array([[2], [4], [6], [8]], dtype=float)

    n_samples = X.shape[0]

    print("\n【数据】")
    print(f"X (shape {X.shape}):\n{X.flatten()}")
    print(f"y (shape {y.shape}):\n{y.flatten()}")
    print("真实关系: y = 2x")

    # ========== 2. 初始化参数 ==========
    w = 0.0  # 权重（斜率）
    b = 0.0  # 偏置（截距）
    lr = 0.01  # 学习率
    epochs = 500  # 迭代次数

    # 初始预测和损失
    y_pred_init = X * w + b
    loss_init = np.mean((y_pred_init - y) ** 2)

    print(f"\n【初始状态】w={w:.4f}, b={b:.4f}, loss={loss_init:.6f}")

    # ========== 3. 梯度下降训练循环 ==========
    print("\n【训练中...】")
    for epoch in range(epochs):
        # --- 前向传播 ---
        y_pred = X * w + b  # ŷ = wx + b

        # --- 计算 MSE 损失 ---
        loss = np.mean((y_pred - y) ** 2)

        # --- 计算梯度 ---
        # ∂L/∂w = (2/n) * Σ(ŷ_i - y_i) * x_i
        dw = np.mean(2 * (y_pred - y) * X)
        # ∂L/∂b = (2/n) * Σ(ŷ_i - y_i)
        db = np.mean(2 * (y_pred - y))

        # --- 更新参数 ---
        w -= lr * dw
        b -= lr * db

        # 定期打印进度
        if epoch in (0, 50, 100, 200, 300, 400):
            print(f"epoch {epoch:4d}: w={w:.4f}, b={b:.4f}, loss={loss:.6f}")

    # 最终结果
    y_pred_final = X * w + b
    loss_final = np.mean((y_pred_final - y) ** 2)
    print(f"epoch {epochs-1:4d}: w={w:.4f}, b={b:.4f}, loss={loss_final:.6f}")

    # ========== 4. 结果分析 ==========
    print(f"\n{'='*55}")
    print(f"【最终结果】w≈{w:.4f}, b≈{b:.4f}, loss≈{loss_final:.6f}")
    print(f"学到的函数: ŷ = {w:.4f} × x + ({b:.4f})")

    if abs(w - 2.0) < 0.01 and abs(b) < 0.01:
        print("✅ 成功收敛到 w≈2, b≈0（理论最优解 y=2x）")
    else:
        print("⚠️ 未完全收敛，可能需要更多 epochs 或调整学习率")

    # ========== 5. 预测新数据 ==========
    new_x = np.array([[5]])
    pred = new_x * w + b
    print(f"\n【预测】x=5 时, ŷ = {pred[0][0]:.4f} (理论值应为 10)")

    # ========== 6. 解析解对比 ==========
    print("\n【解析解对比】")
    # W = (X^T X)^{-1} X^T y  （加上偏置列）
    X_with_bias = np.hstack([np.ones((n_samples, 1)), X])  # 加一列1作为偏置
    w_analytical = np.linalg.inv(X_with_bias.T @ X_with_bias) @ X_with_bias.T @ y
    b_analytic = float(w_analytical.flatten()[0])
    w_analytic_val = float(w_analytical.flatten()[1])
    print(f"解析解: w={w_analytic_val:.6f}, b={b_analytic:.6f}")
    print(f"梯度下降: w={w:.6f}, b={b:.6f}")


if __name__ == "__main__":
    main()
