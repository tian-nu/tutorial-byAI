"""
Ch13: 多层感知机 (MLP)
包含：(1) 手动 2-3-1 MLP 计算 XOR (2) PyTorch 实现 MLP 训练 XOR
首次引入 PyTorch，关键 API 均有中文注释
"""
import numpy as np

try:
    import torch
    import torch.nn as nn
    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False


# ========== Part 1: 手动计算 2-3-1 MLP 解 XOR ==========
def manual_mlp_xor():
    """手动实现 2-3-1 MLP 的完整前向传播（对应细纲数值小例子）"""
    print("\n--- 手动计算 2-3-1 MLP 解 XOR ---")

    # 输入 x = [1, 0]，XOR 应该输出 1
    x = np.array([1.0, 0.0])

    # 第 1 层（隐藏层）参数
    W1 = np.array([[1, 1],
                   [1, 1],
                   [0, 1]], dtype=float)  # shape (3, 2)
    b1 = np.array([0, -1, 0], dtype=float)  # shape (3,)

    # 第 2 层（输出层）参数
    W2 = np.array([1, -1, 1], dtype=float)  # shape (1, 3)
    b2 = np.array([0.0])  # shape (1,)

    # --- 隐藏层前向 ---
    print(f"输入 x = {x}")
    z1 = W1 @ x + b1  # 加权求和 + 偏置
    print(f"隐藏层 z = {z1}")

    def relu(z):
        return np.maximum(0, z)

    h1 = relu(z1)  # ReLU 激活
    print(f"隐藏层 h = {h1}  (ReLU)")

    # --- 输出层前向 ---
    z2 = (W2 @ h1 + b2).item()  # 转为 Python 标量
    print(f"输出层 z = {z2:.1f}")

    def sigmoid(z):
        return 1.0 / (1.0 + np.exp(-np.clip(z, -500, 500)))

    y_hat = sigmoid(float(z2))
    print(f"ŷ = sigmoid({z2:.1f}) = {y_hat:.4f}")

    prediction = 1 if y_hat > 0.5 else 0
    print(f"{y_hat:.4f} > 0.5 → 预测 {prediction} {'✅' if prediction == 1 else '❌'}")

    # --- 参数量统计 ---
    print("\n--- 参数量统计 ---")
    params_w1 = W1.size  # 3*2 = 6
    params_b1 = b1.size  # 3
    params_w2 = W2.size  # 1*3 = 3
    params_b2 = b2.size  # 1
    total = params_w1 + params_b1 + params_w2 + params_b2
    print(f"W₁ ({W1.shape[0]}×{W1.shape[1]}): {params_w1} 个参数")
    print(f"b₁ ({b1.shape[0]},):  {params_b1} 个参数")
    if W2.ndim == 1:
        print(f"W₂ ({W2.shape[0]},):     {params_w2} 个参数")
    else:
        print(f"W₂ ({W2.shape[0]}×{W2.shape[1]}): {params_w2} 个参数")
    if b2.ndim == 0:
        print(f"b₂ (标量):      {params_b2} 个参数")
    else:
        print(f"b₂ ({b2.shape[0]},):  {params_b2} 个参数")
    print(f"总参数量: {total} 个")

    return y_hat


# ========== Part 2: PyTorch 训练 MLP 解 XOR ==========
def pytorch_mlp_xor():
    """用 PyTorch nn.Sequential 构建 MLP 并训练解决 XOR"""
    if not HAS_TORCH:
        print("\n--- PyTorch 训练 MLP 解 XOR (跳过: 需要 PyTorch) ---")
        print("   安装命令: pip install torch")
        return
    print("\n--- PyTorch 训练 MLP 解 XOR ---")

    # --- 定义模型 ---
    model = nn.Sequential(
        nn.Linear(2, 4),   # 全连接层：2维输入 → 4维隐藏（仿射变换 y=Wx+b）
        nn.ReLU(),         # ReLU 激活：max(0,z)，注入非线性
        nn.Linear(4, 1),   # 全连接层：4维隐藏 → 1维输出
        nn.Sigmoid()       # Sigmoid 激活：压缩到(0,1)，输出概率
    )

    # --- 数据准备 ---
    X = torch.tensor([[0., 0.], [0., 1.], [1., 0.], [1., 1.]])
    y = torch.tensor([[0.], [1.], [1.], [0.]])

    # --- 损失函数与优化器 ---
    loss_fn = nn.BCELoss()  # Binary Cross Entropy Loss，二分类交叉熵损失
    optimizer = torch.optim.Adam(model.parameters(), lr=0.01)  # Adam 自适应优化器

    # --- 训练循环 ---
    for epoch in range(1000):
        # 前向传播：数据流经整个网络得到预测值
        pred = model(X)
        # 计算损失：预测值与真实标签的差异
        loss = loss_fn(pred, y)
        # 清空梯度：PyTorch 默认累积梯度，必须先清零
        optimizer.zero_grad()
        # 反向传播：自动计算每个参数的梯度
        loss.backward()
        # 参数更新：沿梯度反方向走一步
        optimizer.step()

        # 每 200 轮打印一次
        if (epoch + 1) % 200 == 0:
            print(f"  Epoch {epoch+1:4d}: loss = {loss.item():.4f}")

    # --- 验证 ---
    print(f"\n训练完成！最终 loss = {loss.item():.4f}")
    print("预测结果:")
    with torch.no_grad():  # 关闭梯度计算，节省内存
        predictions = model(X)
        for i in range(len(X)):
            pred_val = predictions[i].item()
            pred_label = 1 if pred_val > 0.5 else 0
            true_label = int(y[i].item())
            status = "✅" if pred_label == true_label else "❌"
            print(f"  输入{X[i].tolist()} -> 预测{pred_val:.3f} -> {pred_label} (期望{true_label}) {status}")

    # 统计准确率
    correct = sum((predictions > 0.5).int().flatten() == y.int().flatten())
    acc = correct.item() / len(y)
    print(f"\n✅ XOR 准确率 {acc*100:.0f}%（阈值 0.5）")


if __name__ == "__main__":
    print("=" * 55)
    print("=== Ch13: 多层感知机 (MLP) ===")
    print("=" * 55)

    manual_mlp_xor()
    pytorch_mlp_xor()

    print("\n" + "=" * 55)
