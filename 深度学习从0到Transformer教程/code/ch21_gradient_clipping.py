"""
Ch21: RNN 的致命问题 — 梯度消失与爆炸
演示：(1) tanh' 的实际取值范围 (2) 梯度消失连乘 (3) 梯度爆炸连乘 (4) 梯度裁剪
"""
import numpy as np


def clip_gradient(grad, max_norm=5.0):
    """
    梯度裁剪
    当梯度范数超过 max_norm 时，按比例缩放到 max_norm
    方向不变，只缩短长度

    参数:
        grad: 梯度向量
        max_norm: 最大范数
    返回:
        裁剪后的梯度
    """
    norm = np.linalg.norm(grad)
    if norm > max_norm:
        grad = grad * max_norm / norm
    return grad


def demo_tanh_prime():
    """展示 tanh' 的实际取值范围，说明 0.5 的来源"""
    print("--- 关于 tanh' ≈ 0.5 的说明 ---")
    print("tanh'(z) = 1 - tanh²(z)")

    test_z = [0.0, 0.5, 1.0, 1.5]
    for z in test_z:
        tanh_val = np.tanh(z)
        tanh_prime = 1 - tanh_val ** 2
        print(f"  z={z:.1f} 时: tanh'={tanh_prime:.3f}")

    print("→ tanh' 的最大值是 1（z=0 时），但训练中 z 通常不为 0")
    print("→ 平均下来约 0.5，这里用 0.5 作为示意值")


def demo_vanishing(T=20, W_hh=0.5, tanh_prime=0.5):
    """
    演示梯度消失
    每步乘 W_hh × tanh'，连乘 T 步
    """
    print("\n--- 梯度消失演示 ---")
    factor = W_hh * tanh_prime
    print(f"参数: W_hh={W_hh}, tanh'={tanh_prime}, 每步乘 {factor}")

    grad = 1.0
    checkpoints = {1, 5, 10, 20}
    for t in range(1, T + 1):
        grad *= factor
        if t in checkpoints:
            print(f"  T={t:2d}: 梯度 = {grad:.2e}")

    print("→ 梯度趋近 0，模型学不到早期信息")
    return grad


def demo_exploding(T=20, W_hh=2.0, tanh_prime=0.8):
    """
    演示梯度爆炸
    每步乘 W_hh × tanh'，连乘 T 步
    """
    print("\n--- 梯度爆炸演示 ---")
    factor = W_hh * tanh_prime
    print(f"参数: W_hh={W_hh}, tanh'={tanh_prime}, 每步乘 {factor}")

    grad = 1.0
    checkpoints = {1, 5, 10, 20}
    for t in range(1, T + 1):
        grad *= factor
        if t in checkpoints:
            print(f"  T={t:2d}: 梯度 = {grad:.2e}")

    print("→ 梯度趋近 ∞，训练崩溃（NaN）")
    return grad


def demo_clipping():
    """演示梯度裁剪"""
    print("\n--- 梯度裁剪演示 ---")

    # 一个过大的梯度
    big_grad = np.array([10.0, 20.0, 30.0])
    norm_before = np.linalg.norm(big_grad)
    print(f"裁剪前梯度: {big_grad}, 范数 = {norm_before:.2f}")

    # 裁剪
    clipped = clip_gradient(big_grad, max_norm=5.0)
    norm_after = np.linalg.norm(clipped)
    print(f"裁剪后梯度: {np.round(clipped, 2)}, 范数 = {norm_after:.2f}")
    print("→ 范数被限制在 5.0 以内")

    # 验证方向不变（只缩短长度）
    direction_before = big_grad / norm_before
    direction_after = clipped / norm_after
    print(f"方向一致: {np.allclose(direction_before, direction_after)}")

    # 小梯度不受影响
    small_grad = np.array([0.001, 0.002, 0.003])
    clipped_small = clip_gradient(small_grad, max_norm=5.0)
    print(f"\n小梯度 {small_grad} 裁剪后: {clipped_small}（不受影响）")
    print("→ 裁剪只治爆炸，不治消失")


def verify_key_numbers():
    """验证教程中的关键数字"""
    print("\n--- 验证关键数字 ---")

    # 梯度消失
    vanishing_10 = 0.25 ** 10
    vanishing_20 = 0.25 ** 20
    print(f"0.25^10 = {vanishing_10:.2e} (预期 9.5e-7) {'✅' if abs(vanishing_10 - 9.5e-7) < 1e-6 else '❌'}")
    print(f"0.25^20 = {vanishing_20:.2e} (预期 9.1e-13) {'✅' if abs(vanishing_20 - 9.1e-13) < 1e-12 else '❌'}")

    # 梯度爆炸
    exploding_10 = 1.6 ** 10
    exploding_20 = 1.6 ** 20
    print(f"1.6^10 = {exploding_10:.2e} (预期 109.9) {'✅' if abs(exploding_10 - 109.9) < 1 else '❌'}")
    print(f"1.6^20 = {exploding_20:.2e} (预期 12089) {'✅' if abs(exploding_20 - 12089) < 1 else '❌'}")


def main():
    print("=" * 60)
    print("=== Ch21: RNN 的致命问题 — 梯度消失与爆炸 ===")
    print("=" * 60)

    demo_tanh_prime()
    demo_vanishing()
    demo_exploding()
    demo_clipping()
    verify_key_numbers()

    print("\n" + "=" * 60)
    print("结论：")
    print("  - 梯度消失：|W_hh × tanh'| < 1，连乘趋近 0，模型学不到长依赖")
    print("  - 梯度爆炸：|W_hh × tanh'| > 1，连乘趋近 ∞，训练崩溃")
    print("  - 梯度裁剪：缓解爆炸，但无法解决消失")
    print("  - 消失需要架构层面解决 → LSTM（见 Ch22）")
    print("=" * 60)


if __name__ == "__main__":
    main()
    print("\n" + "=" * 60)
