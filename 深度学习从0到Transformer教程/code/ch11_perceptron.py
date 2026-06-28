"""
Ch11: 感知机 — 最简单的神经元
完整实现：AND/OR 门训练与验证，以及 XOR 问题的演示
"""
import numpy as np


def step_function(z):
    """阶跃函数：z > 0 返回 1，否则返回 0"""
    return np.where(z > 0, 1, 0)


def train_perceptron(X, y, lr=0.1, epochs=100):
    """
    感知机训练（感知机学习规则）
    参数:
        X: 输入特征 (n_samples, n_features)
        y: 标签 (n_samples,)
        lr: 学习率
        epochs: 训练轮数
    返回:
        w: 权重向量
        b: 偏置
    """
    n_features = X.shape[1]
    w = np.zeros(n_features)  # 权重初始化为 0
    b = 0.0                   # 偏置初始化为 0

    for epoch in range(epochs):
        for i in range(len(X)):
            # 前向传播：加权求和 + 偏置
            z = np.dot(w, X[i]) + b
            # 阶跃函数
            pred = 1 if z > 0 else 0
            # 感知机学习规则
            error = y[i] - pred
            w += lr * error * X[i]
            b += lr * error

    return w, b


def predict_perceptron(X, w, b):
    """用训练好的感知机做预测"""
    predictions = []
    for i in range(len(X)):
        z = np.dot(w, X[i]) + b
        pred = 1 if z > 0 else 0
        predictions.append(pred)
    return np.array(predictions)


def verify_gate(name, X, y_true):
    """训练并验证一个逻辑门"""
    print(f"\n--- {name} ---")
    w, b = train_perceptron(X, y_true)
    print(f"{name}: w={w}, b={b:.3f}")

    y_pred = predict_perceptron(X, w, b)
    all_correct = True
    for i in range(len(X)):
        status = "✅" if y_pred[i] == y_true[i] else "❌"
        print(f"  输入{X[i]} -> 预测{int(y_pred[i])}, 期望{int(y_true[i])} {status}")
        if y_pred[i] != y_true[i]:
            all_correct = False

    if all_correct:
        print(f"  {name} 门完全正确！")
    else:
        print(f"  ⚠️ {name} 门有错误（可能需要更多 epoch 或该问题不可分）")

    return w, b, all_correct


if __name__ == "__main__":
    print("=" * 50)
    print("=== Ch11: 感知机 — 最简单的神经元 ===")
    print("=" * 50)

    # === 数据准备 ===
    X = np.array([[0, 0], [0, 1], [1, 0], [1, 1]])
    y_and = np.array([0, 0, 0, 1])   # AND 门
    y_or = np.array([0, 1, 1, 1])    # OR 门
    y_xor = np.array([0, 1, 1, 0])   # XOR 门（线性不可分！）

    # === 手动验证 AND 门（细纲要求的固定参数）===
    print("\n【手动验证】AND 门 w=[1,1], b=-1.5:")
    w_manual = np.array([1.0, 1.0])
    b_manual = -1.5
    for i in range(len(X)):
        z = np.dot(w_manual, X[i]) + b_manual
        pred = 1 if z > 0 else 0
        print(f"  输入{X[i]}: z={z:.1f} -> {'输出1' if pred==1 else '输出0'} (期望{y_and[i]})")

    # === 训练 AND 门 ===
    verify_gate("AND 门", X, y_and)

    # === 训练 OR 门 ===
    verify_gate("OR 门", X, y_or)

    # === 尝试 XOR 门（应该失败）===
    print("\n--- XOR 门（线性不可分，预期失败）---")
    w_xor, b_xor, xor_ok = verify_gate("XOR", X, y_xor)
    if not xor_ok:
        print("  💡 正如预期：单层感知机无法解决 XOR 问题！")
        print("  解决方案：使用多层感知机（MLP）+ 非线性激活函数（见 Ch13）")

    print("\n" + "=" * 50)
