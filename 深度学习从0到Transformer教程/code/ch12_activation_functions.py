"""
Ch12: 激活函数家族
完整实现 5 种激活函数及其导数，含数值验证
"""
import numpy as np


# ========== 激活函数定义 ==========

def sigmoid(z):
    """Sigmoid: 压缩到 (0, 1), clip 防止溢出"""
    return 1.0 / (1.0 + np.exp(-np.clip(z, -500, 500)))


def sigmoid_derivative(z):
    """Sigmoid 导数: σ'(z) = σ(z)(1-σ(z))"""
    s = sigmoid(z)
    return s * (1 - s)


def tanh_activate(z):
    """Tanh: 压缩到 (-1, 1), 零中心"""
    return np.tanh(z)


def tanh_derivative(z):
    """Tanh 导数: tanh'(z) = 1 - tanh²(z)"""
    t = np.tanh(z)
    return 1 - t ** 2


def relu(z):
    """ReLU: max(0, z)"""
    return np.maximum(0, z)


def relu_derivative(z):
    """ReLU 导数: z>0 为 1, 否则为 0"""
    return np.where(z > 0, 1.0, 0.0)


def leaky_relu(z, alpha=0.01):
    """LeakyReLU: max(αz, z), 默认 α=0.01"""
    return np.where(z > 0, z, alpha * z)


def leaky_relu_derivative(z, alpha=0.01):
    """LeakyReLU 导数"""
    return np.where(z > 0, 1.0, alpha)


def gelu(z):
    """
    GELU (Gaussian Error Linear Unit) — 近似形式
    精确形式: z * Φ(z), Φ 是标准正态 CDF
    近似误差 < 0.0001
    """
    return 0.5 * z * (1.0 + np.tanh(np.sqrt(2.0 / np.pi) * (z + 0.044715 * z ** 3)))


# ========== 数值验证工具 ==========

def numerical_derivative(f, z, eps=1e-5):
    """用中心差分法求数值导数"""
    return (f(z + eps) - f(z - eps)) / (2 * eps)


if __name__ == "__main__":
    print("=" * 55)
    print("=== Ch12: 激活函数家族 ===")
    print("=" * 55)

    # --- 细纲要求的两个关键点 ---
    print("\n--- 数值验证 (z=2.0 和 z=-1.0) ---")
    test_points = [2.0, -1.0]
    for z_val in test_points:
        s = sigmoid(z_val)
        t = tanh_activate(z_val)
        r = relu(z_val)
        lr = leaky_relu(z_val)
        g = gelu(z_val)
        print(f"z = {z_val:+.1f}: sigmoid={s:.4f}, tanh={t:.4f}, "
              f"ReLU={r:.4f}, L-ReLU={lr:.4f}, GELU={g:.4f}")

    # --- 批量测试 ---
    print("\n--- 批量测试 ---")
    z_batch = np.array([-2.0, -1.0, 0.0, 1.0, 2.0])
    print(f"z        = {z_batch}")
    print(f"sigmoid  = {np.round(sigmoid(z_batch), 3)}")
    print(f"tanh     = {np.round(tanh_activate(z_batch), 3)}")
    print(f"ReLU     = {relu(z_batch).astype(int)}")  # ReLU 整数显示更清晰
    print(f"L-ReLU   = {np.round(leaky_relu(z_batch), 3)}")
    print(f"GELU    = {np.round(gelu(z_batch), 4)}")

    # --- sigmoid 导数验证（细纲重点要求）---
    print("\n--- sigmoid 导数验证 ---")
    z_test = 2.0
    s_val = sigmoid(z_test)
    analytic_deriv = s_val * (1 - s_val)  # σ'(z) = σ(z)(1-σ(z))
    numeric_deriv = numerical_derivative(sigmoid, z_test)
    print(f"σ({z_test}) = {s_val:.4f}")
    print(f"σ'({z_test}) 通过自身值计算 = {analytic_deriv:.4f}")
    print(f"σ'({z_test}) 数值差分验证    = {numeric_deriv:.4f}", end="")
    if abs(analytic_deriv - numeric_deriv) < 1e-6:
        print(" ✅ 吻合！")
    else:
        print(" ❌ 不一致！")

    # --- 所有函数导数验证 ---
    print("\n--- 所有激活函数导数验证 (z=1.0) ---")
    funcs = [
        ("sigmoid", sigmoid, sigmoid_derivative),
        ("tanh", tanh_activate, tanh_derivative),
        ("relu", relu, relu_derivative),
        ("leaky_relu", leaky_relu, leaky_relu_derivative),
    ]
    for name, f, df in funcs:
        analytic = df(1.0)
        numeric = numerical_derivative(f, 1.0)
        match = "✅" if abs(analytic - numeric) < 1e-6 else "❌"
        print(f"  {name:10s}: 解析={analytic:.4f}, 数值={numeric:.4f} {match}")

    # --- GELU vs ReLU 对比 ---
    print("\n--- GELU vs ReLU 对比 (负区行为) ---")
    neg_z = np.array([-3, -2, -1, -0.5, 0])
    print(f"{'z':>6s} | {'ReLU':>8s} | {'GELU':>8s} | 差异说明")
    print("-" * 45)
    for zv in neg_z:
        r = float(relu(zv))
        g = float(gelu(zv))
        note = "GELU 保留了部分负值" if g != r else "相同"
        print(f"{zv:>6.1f} | {r:>8.4f} | {g:>8.4f} | {note}")

    print("\n" + "=" * 55)
