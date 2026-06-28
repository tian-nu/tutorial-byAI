"""
Ch07 · 梯度下降 —— 核心优化算法演示
1. 用 L(w)=w² 展示完整的梯度下降过程
2. 对比三种学习率（太小/合适/太大）
3. 可视化收敛曲线（文字版）
"""

import numpy as np


def loss_fn(w):
    """损失函数 L(w) = w^2"""
    return w ** 2


def gradient(w):
    """梯度 dL/dw = 2w"""
    return 2 * w


def gradient_descent(w_init, lr, steps, label=""):
    """执行梯度下降，返回历史记录"""
    w = w_init
    history = []
    for step in range(steps):
        history.append((step, w, loss_fn(w)))
        grad = gradient(w)
        w = w - lr * grad
    # 最后一步
    history.append((steps, w, loss_fn(w)))
    return history


def print_history(history, label, print_every=10):
    """打印训练历史"""
    print(f"\n--- {label} ---")
    for step, w_val, loss_val in history:
        if step % print_every == 0 or step == len(history) - 1:
            print(f"step {step:3d}: w={w_val:>10.6f}, L={loss_val:>14.8f}")


def main():
    print("=" * 60)
    print("=== 梯度下降 — 核心演示 ===")
    print("=" * 60)

    print("\n【损失函数】L(w) = w²")
    print("  梯度: dL/dw = 2w")
    print("  最优解: w* = 0, 最小损失 = 0")

    w_init = 5.0   # 起始点
    steps = 100    # 总步数

    # ========== 三种学习率对比 ==========
    learning_rates = [
        (0.01, "η=0.01 (太小，收敛极慢)", 10),
        (0.1,  "η=0.1  (合适)", 10),
        (1.1,  "η=1.1  (太大，发散!)", 1),
    ]

    results = {}
    for lr, label, interval in learning_rates:
        hist = gradient_descent(w_init, lr, steps, label)
        results[lr] = hist
        print_history(hist, label, print_every=interval)

        # 判断是否收敛或发散
        final_w = hist[-1][1]
        final_loss = hist[-1][2]
        if abs(final_w) > abs(w_init) * 1.5 or final_loss > loss_fn(w_init):
            print(f"  ❌ 发散! |w| 从 {w_init} 变成了 {abs(final_w):.2f}")
        elif final_loss < 1e-6:
            print(f"  ✅ 收敛良好! w≈{final_w:.6f}, L≈{final_loss:.2e}")
        else:
            print(f"  ⚠️ 未完全收敛, w={final_w:.4f}, L={final_loss:.4f}")

    # ========== 详细展示 η=0.1 的前10步 ==========
    print(f"\n{'='*60}")
    print("【η=0.1 前10步详细展开】")
    print(f"{'='*60}")
    print(f"{'步骤':>4s} | {'当前 w':>10s} | {'梯度 2w':>10s} | "
          f"{'更新量':>10s} | {'新 w':>10s} | {'损失':>10s}")
    print("-" * 65)

    w = w_init
    for step in range(min(10, steps)):
        grad = gradient(w)
        update = 0.1 * grad
        new_w = w - update
        loss_val = loss_fn(w)
        print(f"{step:4d} | {w:10.6f} | {grad:10.6f} | "
              f"{update:10.6f} | {new_w:10.6f} | {loss_val:10.6f}")
        w = new_w
    loss_val = loss_fn(w)
    print(f"{10:4d} | {w:10.6f} | {'...':>10s} | "
          f"{'...':>10s} | {'...':>10s} | {loss_val:10.6f}")

    # ========== 总结 ==========
    print(f"\n{'='*60}")
    print("【总结】")
    print(f"{'='*60}")
    print(f"  η 太小 (0.01): 像蜗牛爬，安全但慢")
    print(f"  η 合适 (0.1):  稳步下降，高效收敛")
    print(f"  η 太大 (1.1):  跨过谷底，越来越远（发散）")
    print(f"\n  经验法则：从 0.01 开始试，观察 loss 曲线调整")


if __name__ == "__main__":
    main()
