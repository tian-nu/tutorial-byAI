"""
Ch16: 训练技巧 — 让网络真的学得动
包含：(1) Momentum 逐步数值演示 (2) Adam 第1步完整含偏差修正
      (3) SGD vs Momentum vs Adam 对比实验 (4) 完整训练流程
"""
import numpy as np

try:
    import torch
    import torch.nn as nn
    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False
    print("⚠️ PyTorch 未安装，Part 3 (优化器对比) 和 Part 4 (完整训练流程) 将跳过")
    print("   安装命令: pip install torch")


# ========== Part 1: Momentum 逐步演示 ==========

def momentum_demo():
    """Momentum 3步累积的完整数值展示（细纲要求）"""
    print("\n--- Momentum 3步累积演示 ---")
    beta = 0.9
    lr = 0.01
    w = 0.0
    v = 0.0

    print(f"β={beta}, lr={lr}, 恒定梯度 g=1.0")
    print(f"{'步数':>4s} | {'v':>9s} | {'Momentum:w':>12s} | {'纯SGD:w':>10s}")
    print(" " * 4 + " | " + "-"*9 + " | " + "-"*12 + " | " + "-"*10)

    sgd_w = 0.0
    for step in range(1, 4):
        g = 1.0  # 假设每步梯度恒为 1.0
        v = beta * v + (1 - beta) * g
        w = w - lr * v
        sgd_w = sgd_w - lr * g  # 纯SGD对比
        print(f"{step:>4d} | {v:>9.3f} | {w:>12.5f} | {sgd_w:>10.5f}")

    print("\n结论: Momentum前期慢(v在积累)，后期加速超过SGD")


# ========== Part 2: Adam 第1步完整计算 ==========

def adam_demo():
    """Adam 第1步完整计算，含偏差修正解释"""
    print("\n--- Adam 第1步完整计算 ---")

    beta1 = 0.9
    beta2 = 0.999
    lr = 0.001
    eps = 1e-8
    t = 1  # 第1步
    g = 1.0

    m = 0.0
    v = 0.0
    w = 0.0

    # 一阶矩和二阶矩
    m = beta1 * m + (1 - beta1) * g
    v = beta2 * v + (1 - beta2) * (g ** 2)

    print(f"β₁={beta1}, β₂={beta2}, lr={lr}, g={g}")
    print(f"m = {beta1}×0 + {1-beta1}×{g} = {m:.3f}")
    print(f"v = {beta2}×0 + {1-beta2}×{g}² = {v:.6f}")

    # 偏差修正
    m_hat = m / (1 - beta1 ** t)
    v_hat = v / (1 - beta2 ** t)

    print(f"\n偏差修正:")
    print(f"  m̂ = m / (1-β₁ᵗ) = {m:.3f} / {1-beta1**t:.4f} = {m_hat:.6f}")
    print(f"  v̂ = v / (1-β₂ᵗ) = {v:.6f} / {1-beta2**t:.6f} = {v_hat:.6f}")

    # 参数更新
    w_new = w - lr * m_hat / (np.sqrt(v_hat) + eps)
    print(f"\nw更新: {w} - {lr} × {m_hat:.6f} / (√{v_hat:.6f} + {eps}) = {w_new:.6f}")
    print(f"(第1步就走完整学习率!)")


# ========== Part 3: 优化器对比实验 ==========

def optimizer_comparison():
    """SGD vs Momentum vs Adam 在简单二分类任务上的对比"""
    if not HAS_TORCH:
        print("\n--- 优化器对比实验 (跳过: 需要 PyTorch) ---")
        return
    print("\n--- 优化器对比实验 ---")

    # 生成简单的可分数据
    np.random.seed(42)
    X = np.random.randn(200, 2)
    y = (X[:, 0] + X[:, 1] > 0).astype(float)

    X_t = torch.tensor(X, dtype=torch.float32)
    y_t = torch.tensor(y, dtype=torch.float32).unsqueeze(1)

    def make_model():
        return nn.Sequential(
            nn.Linear(2, 16),
            nn.ReLU(),
            nn.Linear(16, 1),
            nn.Sigmoid()
        )

    optimizers = {
        "SGD": lambda p: torch.optim.SGD(p, lr=0.01),
        "Mom": lambda p: torch.optim.SGD(p, lr=0.01, momentum=0.9),
        "Adam": lambda p: torch.optim.Adam(p, lr=0.01),
    }

    print(f"{'Epoch':>5s}", end="")
    for name in optimizers:
        print(f" {name+' Loss':>10s}", end="")
    print()

    results = {name: [] for name in optimizers}

    for epoch in range(101):
        for name, opt_fn in optimizers.items():
            model = make_model()
            optimizer = opt_fn(model.parameters())
            criterion = nn.BCELoss()

            for _ in range(10):  # 每个 epoch 内迭代10次
                pred = model(X_t)
                loss = criterion(pred, y_t)
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()

            if epoch % 20 == 0 or epoch == 100:
                with torch.no_grad():
                    final_loss = criterion(model(X_t), y_t).item()
                results[name].append(final_loss)

        if epoch % 20 == 0 or epoch == 100:
            print(f"{epoch:>5d}", end="")
            for name in optimizers:
                idx = len(results[name]) - 1
                print(f" {results[name][idx]:>10.3f}", end="")
            print()


# ========== Part 4: 完整训练流程 ==========

def full_training_demo():
    """展示包含 BatchNorm/Dropout/Adam/Scheduler 的完整训练流程"""
    if not HAS_TORCH:
        print("\n--- 完整训练流程演示 (跳过: 需要 PyTorch) ---")
        return
    print("\n--- 完整训练流程演示 ---")

    # 构建模型
    model = nn.Sequential(
        nn.Linear(10, 64),    # 全连接层: 输入10维 -> 隐藏64维
        nn.ReLU(),            # ReLU 激活函数
        nn.Dropout(0.5),      # Dropout: 训练时随机丢弃50%神经元防过拟合
        nn.Linear(64, 32),    # 全连接层: 64维 -> 32维
        nn.ReLU(),            # ReLU 激活
        nn.BatchNorm1d(32),   # BatchNorm: 对32维特征做批归一化，稳定训练
        nn.Linear(32, 2),     # 输出层: 32维 -> 2类分类
    )
    print("模型结构:")
    print(model)

    # 创建假数据（实际使用时替换为真实数据）
    np.random.seed(42)
    from torch.utils.data import TensorDataset, DataLoader

    X_train = torch.randn(500, 10)   # 500个样本，每个10维特征
    y_train = torch.randint(0, 2, (500,))  # 二分类标签
    train_dataset = TensorDataset(X_train, y_train)
    dataloader = DataLoader(train_dataset, batch_size=32, shuffle=True)

    # 优化器 + 学习率调度
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=100)
    criterion = nn.CrossEntropyLoss()

    # 训练
    model.train()  # 设为训练模式（Dropout开启，BatchNorm用batch统计量）
    for epoch in range(100):
        total_loss = 0
        for X_batch, y_batch in dataloader:
            pred = model(X_batch)                 # 前向传播
            loss = criterion(pred, y_batch)        # 计算损失
            optimizer.zero_grad()                  # 清空梯度
            loss.backward()                        # 反向传播
            optimizer.step()                       # 更新参数
            total_loss += loss.item()
        scheduler.step()                           # 更新学习率

        if (epoch + 1) % 25 == 0:
            avg_loss = total_loss / len(dataloader)
            current_lr = scheduler.get_last_lr()[0]
            print(f"  Epoch {epoch+1:3d}: loss={avg_loss:.4f}, lr={current_lr:.6f}")

    # 推理（关键：切换到 eval 模式！）
    model.eval()  # 设为评估模式（Dropout关闭，BatchNorm用全局统计量）
    X_test = torch.randn(100, 10)
    y_test = torch.randint(0, 2, (100,))
    with torch.no_grad():  # 关闭梯度计算节省内存
        test_pred = model(X_test)
        test_acc = (test_pred.argmax(dim=1) == y_test).float().mean()
    print(f"\n最终测试准确率: {test_acc.item()*100:.1f}%")
    model.train()  # 切回训练模式


if __name__ == "__main__":
    print("=" * 60)
    print("=== Ch16: 训练技巧 — 让网络真的学得动 ===")
    print("=" * 60)

    momentum_demo()
    adam_demo()
    optimizer_comparison()
    full_training_demo()

    print("\n" + "=" * 60)
