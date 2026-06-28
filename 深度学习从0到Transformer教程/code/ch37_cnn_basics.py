# -*- coding: utf-8 -*-
"""
Ch37 · CNN 简介 — 处理图像的另一条路
代码文件：演示 3×3 卷积数值小例子 + 一层 Conv2d + 一层 MaxPool2d

运行方式：
    cd 深度学习从0到Transformer教程/code
    python ch37_cnn_basics.py

依赖：numpy, torch（无需 GPU）
"""

import numpy as np
import torch
import torch.nn as nn


# ============================================================
# 第 1 部分：手写 3×3 卷积数值小例子（对应正文 How 节）
# ============================================================
# 输入：4×4 灰度图，左半=1 右半=2，中间是一条垂直边缘
# 卷积核：3×3 垂直边缘检测器（左列 +1，中间 0，右列 -1）
# 无 padding，stride=1，输出尺寸 (4-3)/1+1 = 2 → 2×2
# ============================================================

print("=" * 50)
print("=== 手写 3×3 卷积数值小例子 ===")
print("=" * 50)

x_np = np.array(
    [[1, 1, 2, 2],
     [1, 1, 2, 2],
     [1, 1, 2, 2],
     [1, 1, 2, 2]],
    dtype=float,
)
k_np = np.array(
    [[1, 0, -1],
     [1, 0, -1],
     [1, 0, -1]],
    dtype=float,
)

print("输入 X (4×4):")
print(x_np)
print("\n卷积核 K (3×3, 垂直边缘检测器):")
print(k_np)

# 手写滑动卷积：两个位置 (i=0,1) × (j=0,1) 共 4 个输出
out_h = (x_np.shape[0] - k_np.shape[0]) // 1 + 1  # (4-3)/1+1 = 2
out_w = (x_np.shape[1] - k_np.shape[1]) // 1 + 1  # (4-3)/1+1 = 2
out_np = np.zeros((out_h, out_w))

print(f"\n输出尺寸: ({x_np.shape[0]}-{k_np.shape[0]})/1+1 = {out_h} → {out_h}×{out_w}")

for i in range(out_h):
    for j in range(out_w):
        window = x_np[i:i + 3, j:j + 3]          # 取出 3×3 窗口
        out_np[i, j] = np.sum(window * k_np)     # 对应相乘再求和
        print(f"\n位置 ({i},{j}) 窗口:")
        print(window)
        print(f"  对应相乘再求和 = {out_np[i, j]:.0f}")

print("\n最终输出:")
print(out_np)
print("✅ 与正文手算一致（四个位置都是 -3，因为每个 3×3 窗口都是『左 1 右 2』结构）")


# ============================================================
# 第 2 部分：用 PyTorch 一层 Conv2d
# ============================================================
# nn.Conv2d(in_channels=3, out_channels=16, kernel_size=3, padding=1)
# 参数量 = (3×3×3 + 1) × 16 = 448
#   - 3×3×3 = 27  → 单个卷积核（深度=输入通道数 3）
#   - ×16         → 16 个卷积核
#   - +1×16 = 16  → 每个输出通道一个偏置
# ============================================================

print("\n" + "=" * 50)
print("=== 一层 Conv2d ===")
print("=" * 50)

conv = nn.Conv2d(in_channels=3, out_channels=16, kernel_size=3, padding=1)
x_t = torch.randn(1, 3, 32, 32)  # batch=1, C=3, H=32, W=32

out_t = conv(x_t)
print(f"conv(x).shape       = {tuple(out_t.shape)}   # padding=1 保持尺寸")
print(f"conv.weight.shape   = {tuple(conv.weight.shape)}  # 16 个核 × 3 通道 × 3×3")

n_params = sum(p.numel() for p in conv.parameters())
print(f"参数量              = {n_params}")
print(f"  计算过程: (3×3×3 + 1) × 16 = {(3*3*3 + 1) * 16}")
print(f"  其中 weight = {conv.weight.numel()}, bias = {conv.bias.numel()}")

assert n_params == 448, f"参数量应为 448，实际 {n_params}"
print("✅ 参数量 = 448，与正文一致")


# ============================================================
# 第 3 部分：一层 MaxPool2d（降维）
# ============================================================
# MaxPool2d(kernel_size=2, stride=2)：每个 2×2 块取最大值，尺寸减半
# 无可学习参数
# ============================================================

print("\n" + "=" * 50)
print("=== 一层 MaxPool2d ===")
print("=" * 50)

pool = nn.MaxPool2d(kernel_size=2, stride=2)
pooled = pool(out_t)
print(f"pool(out).shape     = {tuple(pooled.shape)}  # 尺寸减半 32→16")
print(f"pool 参数量          = {sum(p.numel() for p in pool.parameters()) if list(pool.parameters()) else 0}  # MaxPool 无可学习参数")


# ============================================================
# 第 4 部分：感受野演示
# ============================================================
# 第 1 层 3×3 卷积：感受野 = 3
# 第 2 层 3×3 卷积：感受野 = 3 + (3-1) = 5
# 第 3 层 3×3 卷积：感受野 = 5 + (3-1) = 7
# 公式：r_l = r_{l-1} + (k_l - 1)，r_1 = k_1
# ============================================================

print("\n" + "=" * 50)
print("=== 感受野演示（3 层 3×3 卷积堆叠）===")
print("=" * 50)

receptive_field = 0
for layer in range(1, 4):
    k = 3
    if layer == 1:
        receptive_field = k
    else:
        receptive_field = receptive_field + (k - 1)
    print(f"第 {layer} 层 3×3 卷积 → 感受野 = {receptive_field}")

print("\n层数越深，感受野越大，深层神经元能看到的『全局结构』越多。")


# ============================================================
# 第 5 部分：对比全连接的参数量
# ============================================================
# 同样输入 3×32×32 = 3072 维，输出 16 维
# 全连接: 3072×16 + 16 = 49168
# CNN:    448
# ============================================================

print("\n" + "=" * 50)
print("=== 参数量对比：CNN vs 全连接 ===")
print("=" * 50)

fc_params = 3 * 32 * 32 * 16 + 16
cnn_params = 448
print(f"全连接 Linear(3072, 16): {fc_params} 个参数")
print(f"CNN Conv2d(3, 16, 3):    {cnn_params} 个参数")
print(f"CNN 是全连接的 {cnn_params / fc_params * 100:.1f}% → 参数共享的威力")

print("\n✅ 全部演示完成。")
