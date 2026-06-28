"""
Ch15: 反向传播 — 误差从后往前传
完整实现：(1) 手动反向传播计算 (2) compute_loss 完整定义 (3) 数值梯度验证
这是本教程中最重要的一章代码！
"""
import numpy as np


# ========== 核心函数 ==========

def relu(z):
    """ReLU 激活"""
    return np.maximum(0, z)


def softmax(z):
    """Softmax（防溢出版本）"""
    e = np.exp(z - np.max(z))
    return e / e.sum()


def compute_loss(x, y, W1, b1, W2, b2):
    """
    完整的前向传播 + 交叉熵损失计算
    
    这个函数用于数值梯度验证——每次扰动一个参数后，
    重新跑一遍完整的前向传播得到新的损失值。
    
    参数:
        x: 输入向量 (n,)
        y: 真实标签 one-hot (m,)
        W1, b1: 第1层参数
        W2, b2: 第2层参数
    返回:
        loss: 标量损失值
    """
    # --- 前向传播（与 Ch14 完全一致）---
    z1 = W1 @ x + b1                    # 第1层线性变换
    a1 = np.maximum(0, z1)               # ReLU 激活
    z2 = W2 @ a1 + b2                    # 第2层线性变换
    # Softmax 输出
    exp_z2 = np.exp(z2 - np.max(z2))
    y_hat = exp_z2 / np.sum(exp_z2)
    # 交叉熵损失（加 1e-8 防 log(0)）
    loss = -np.sum(y * np.log(y_hat + 1e-8))
    return loss


def forward(x, W1, b1, W2, b2):
    """
    前向传播，返回所有中间值（反向传播需要缓存这些值）
    返回: z1, a1, z2, y_hat
    """
    z1 = W1 @ x + b1
    a1 = relu(z1)
    z2 = W2 @ a1 + b2
    y_hat = softmax(z2)
    return z1, a1, z2, y_hat


def backward(x, y, z1, a1, z2, y_hat, W2):
    """
    反向传播：计算所有参数的梯度
    
    参数:
        中间值来自 forward() 的返回值
    返回:
        dW1, db1, dW2, db2: 各参数的梯度
    """
    # --- 输出层误差: δ³ = ŷ - y（softmax+交叉熵的简化形式）---
    delta3 = y_hat - y                     # shape (m,)

    # --- 输出层参数梯度 ---
    dW2 = np.outer(delta3, a1)             # shape (m, h) = (2, 4)
    db2 = delta3.copy()                    # shape (m,) = (2,)

    # --- 误差反传到隐藏层: δ¹ = (W₂ᵀ · δ³) ⊙ ReLU'(z¹) ---
    da1 = W2.T @ delta3                    # shape (h,) = (4,)
    dz1 = da1 * (z1 > 0).astype(float)     # ReLU'：正数为1，非正为0；shape (h,) = (4,)

    # --- 隐藏层参数梯度 ---
    dW1 = np.outer(dz1, x)                 # shape (h, n) = (4, 3)
    db1 = dz1.copy()                       # shape (h,) = (4,)

    return dW1, db1, dW2, db2


def numerical_gradient(f, params_dict, key, indices, eps=1e-5):
    """
    数值梯度（中心差分法）
    
    参数:
        f: 接受 params_dict 并返回标量的函数
        params_dict: 包含所有参数的字典
        key: 要扰动的参数名（如 'W1'）
        indices: 扰动的索引（如 (0, 0) 表示 W1[0,0]）
        eps: 扰动大小
    返回:
        num_grad: 数值梯度
    """
    arr = params_dict[key]
    original = arr[indices].copy()

    arr[indices] = original + eps
    loss_plus = f(params_dict)

    arr[indices] = original - eps
    loss_minus = f(params_dict)

    arr[indices] = original  # 恢复原值！
    return (loss_plus - loss_minus) / (2 * eps)


# ========== 主流程 ==========

def main():
    print("=" * 60)
    print("=== Ch15: 反向传播 — 误差从后往前传 ===")
    print("=" * 60)

    # === 参数初始化（与 Ch14 完全一致）===
    x = np.array([1.0, 0.5, -1.0])
    y = np.array([1, 0])  # one-hot: 第1类

    W1 = np.array([[1, 0, -1],
                   [0, 1, 1],
                   [-1, 1, 0],
                   [1, 1, 1]], dtype=float)
    b1 = np.zeros(4)

    W2 = np.array([[1, 0, 0, 1],
                   [0, 1, 1, 0]], dtype=float)
    b2 = np.zeros(2)

    # === 前向传播 ===
    print("\n--- 前向传播结果 ---")
    z1, a1, z2, y_hat = forward(x, W1, b1, W2, b2)

    print(f"z⁽¹⁾ = {z1}")
    print(f"a⁽¹⁾ = {a1}  (ReLU)")
    print(f"ŷ = {y_hat.round(4)}")
    print(f"真实标签 y = {y}")

    loss_val = compute_loss(x, y, W1, b1, W2, b2)
    print(f"交叉熵损失 L = {loss_val:.4f}")

    # === 反向传播 ===
    print("\n--- 反向传播 ---")
    dW1, db1, dW2, db2 = backward(x, y, z1, a1, z2, y_hat, W2)

    print(f"δ³ = ŷ - y = {np.round(y_hat - y, 4)}")
    print(f"δ¹ = {np.round(db1, 4)}")

    print("\n梯度:")
    print(f"  dW2 shape={dW2.shape}:")
    for row in dW2:
        print(f"    {np.round(row, 4)}")
    print(f"  db2 shape={db2.shape}: {np.round(db2, 4)}")
    print(f"  dW1 shape={dW1.shape}:")
    for row in dW1:
        print(f"    {np.round(row, 4)}")
    print(f"  db1 shape={db1.shape}: {np.round(db1, 4)}")

    # === 数值梯度验证 ===
    print("\n--- 数值梯度验证 ---")
    print(f"{'参数':<12s} {'解析梯度':>10s} {'数值梯度':>10s} {'差异':>10s} {'状态':>4s}")
    print("-" * 52)

    # 构建参数字典供 numerical_gradient 使用
    params = {'W1': W1, 'b1': b1, 'W2': W2, 'b2': b2}

    def loss_fn(p):
        return compute_loss(x, y, p['W1'], p['b1'], p['W2'], p['b2'])

    all_pass = True
    test_cases = [
        ('W1', (0, 0), dW1[0, 0]),
        ('W1', (0, 1), dW1[0, 1]),
        ('W1', (0, 2), dW1[0, 2]),
        ('W2', (0, 0), dW2[0, 0]),
        ('W2', (0, 3), dW2[0, 3]),
        ('b2', (0,), db2[0]),
    ]

    for key, idx, analytic in test_cases:
        num = numerical_gradient(loss_fn, params, key, idx)
        diff = abs(analytic - num)
        status = "✅" if diff < 1e-7 else "❌"
        if diff >= 1e-7:
            all_pass = False
        print(f"{key}{str(idx):<8s} {analytic:>10.6f} {num:>10.6f} {diff:>10.8f} {status:>4s}")

    if all_pass:
        print("\n✅ 所有梯度验证通过！差异均 < 1e-7")
    else:
        print("\n❌ 存在梯度不一致，请检查反向传播实现")


if __name__ == "__main__":
    main()
    print("\n" + "=" * 60)
