# -*- coding: utf-8 -*-
"""
Ch38 · 生成模型简介 — VAE / GAN / Diffusion
代码文件：演示 Diffusion 3 步加噪数值小例子 + HuggingFace Diffusion 调用

运行方式：
    cd 深度学习从0到Transformer教程/code
    python ch38_diffusion_demo.py

依赖：numpy（必需）；torch / diffusers（可选，仅 HuggingFace 调用部分需要）
无需 GPU：前半部分纯 NumPy；HuggingFace 部分用 try-except 自动跳过
"""

import numpy as np


# ============================================================
# 第 1 部分：Diffusion 3 步加噪数值小例子（对应正文 How 节）
# ============================================================
# 前向公式：x_t = √(1-β_t)·x_{t-1} + √β_t·ε
#   - β_t：第 t 步的噪声调度（控制加多少噪声）
#   - ε：从标准正态分布 N(0, I) 采样的随机噪声，每步重新采一个
#   - √(1-β_t)·x_{t-1}：把上一图稍微缩小，保证方差不爆炸
# ============================================================

print("=" * 50)
print("=== Diffusion 3 步加噪过程 ===")
print("=" * 50)

x = np.array([1.0, 0.5])
betas = [0.1, 0.2, 0.3]
# 为了和正文手算结果完全对应，这里固定每步采到的 ε（实际训练时是随机的）
epsilons = [
    np.array([0.1, -0.2]),   # 第 1 步采到的噪声 ε_1
    np.array([0.3, 0.1]),    # 第 2 步采到的噪声 ε_2（重新采）
    np.array([-0.2, 0.5]),   # 第 3 步采到的噪声 ε_3（又重新采）
]

print(f"x_0 = {x}")

history = [x.copy()]
for t, (beta, eps) in enumerate(zip(betas, epsilons), 1):
    scale_signal = np.sqrt(1 - beta)   # √(1-β_t)：信号缩放
    scale_noise = np.sqrt(beta)        # √β_t：噪声缩放
    x = scale_signal * x + scale_noise * eps
    history.append(x.copy())
    print(f"x_{t} = √(1-{beta})·x_{t-1} + √{beta}·ε_{t}")
    print(f"     = {scale_signal:.3f}·{history[-2]} + {scale_noise:.3f}·{eps}")
    print(f"     = {x}")
    print()

print(f"最终 x_3 = {x}")
print("✅ 与正文手算一致（x_3 ≈ [0.736, 0.620]）")
print("观察：原始信号被一步步稀释，噪声占比越来越大。")
print("     继续加噪几十步，x_T 就变成纯噪声——Diffusion 前向的终点。")


# ============================================================
# 第 2 部分：随机采样的 Diffusion 加噪（演示真实随机性）
# ============================================================
# 上面用固定 ε 是为了和正文手算对齐。
# 这里用 np.random.randn 真实采样，每次运行结果不同。
# ============================================================

print("\n" + "=" * 50)
print("=== 真实随机采样的 Diffusion 加噪（每次结果不同）===")
print("=" * 50)

np.random.seed(0)  # 仅为本脚本结果可复现；实际训练不设种子
x = np.array([1.0, 0.5])
print(f"x_0 = {x}")
for t, beta in enumerate(betas, 1):
    eps = np.random.randn(*x.shape)   # 从标准正态 N(0, I) 采样
    x = np.sqrt(1 - beta) * x + np.sqrt(beta) * eps
    print(f"  步 {t}: β={beta}, ε={eps.round(3)}, x_{t}={x.round(3)}")
print("（因为是真随机，这里的 x_3 和上面固定 ε 的结果不同，这是正常的）")


# ============================================================
# 第 3 部分：Diffusion 反向去噪的"概念演示"
# ============================================================
# 真实 Diffusion 用一个神经网络预测每步的噪声 ε_θ，然后减掉它。
# 这里用一个简化函数演示"去噪"逻辑（不是真实模型）：
#   x_{t-1} ≈ (x_t - √β_t·ε_θ) / √(1-β_t)
# 其中 ε_θ 假设我们已经"完美预测"了正向加的噪声。
# ============================================================

print("\n" + "=" * 50)
print("=== Diffusion 反向去噪概念演示（假设完美预测噪声）===")
print("=" * 50)

# 从第 1 部分得到的 x_3 开始，用"完美预测的 ε"反向去噪
x_noisy = history[-1].copy()  # x_3
print(f"起点 x_3 = {x_noisy}")

x_recovered = x_noisy.copy()
for t in range(len(betas), 0, -1):           # 从 t=3 倒着去到 t=1
    beta = betas[t - 1]
    eps = epsilons[t - 1]                    # 假设网络完美预测了正向加的 ε
    x_recovered = (x_recovered - np.sqrt(beta) * eps) / np.sqrt(1 - beta)
    print(f"  去噪步 {t}→{t-1}: x_{t-1} = {x_recovered.round(3)}")

print(f"\n还原结果 x_0 = {x_recovered.round(3)}")
print(f"原始     x_0 = {history[0]}")
print("✅ 完美去噪（因为我们用了真实 ε）；真实网络只能近似预测 ε，所以还原会有误差。")


# ============================================================
# 第 4 部分：HuggingFace 调用 Diffusion 模型生成图片
# ============================================================
# 这一步需要：① 安装 diffusers + transformers
#             ② 有 GPU（cuda）会更快，CPU 也能跑但慢
#             ③ 联网下载模型（首次约 4GB）
# 用 try-except 包裹：缺依赖/无网络/无 GPU 时自动跳过，不报错
# ============================================================

print("\n" + "=" * 50)
print("=== HuggingFace Diffusion 调用 ===")
print("=" * 50)

try:
    from diffusers import StableDiffusionPipeline
    import torch

    # 检查是否有 GPU
    has_cuda = torch.cuda.is_available()
    dtype = torch.float16 if has_cuda else torch.float32
    device = "cuda" if has_cuda else "cpu"

    print(f"设备: {device}, dtype: {dtype}")
    print("正在加载 Stable Diffusion 模型（首次需联网下载约 4GB）...")

    pipe = StableDiffusionPipeline.from_pretrained(
        "runwayml/stable-diffusion-v1-5",
        torch_dtype=dtype,
    )
    pipe = pipe.to(device)

    prompt = "a cat wearing a hat"
    print(f'提示词: "{prompt}"')
    image = pipe(prompt).images[0]
    image.save("cat_hat.png")
    print("✅ 生成完成，已保存到 cat_hat.png")

except ImportError:
    print("⚠️ 跳过：未安装 diffusers / transformers")
    print("   如需运行，请执行：pip install diffusers transformers")
except Exception as e:
    print(f"⚠️ 跳过：调用失败（{type(e).__name__}: {e}）")
    print("   常见原因：无网络、无 GPU、模型下载失败、内存不足")
    print("   这不影响前面 3 部分的演示——它们纯 NumPy，无需任何外部依赖。")


# ============================================================
# 第 5 部分：三大生成模型核心思想对比
# ============================================================

print("\n" + "=" * 50)
print("=== 三大生成模型核心思想对比 ===")
print("=" * 50)

models = [
    ("VAE",        "压缩再还原",          "编码器→潜在 z→解码器，加 KL 正则", "训练稳定",       "生成模糊"),
    ("GAN",        "造假者 vs 警察",       "生成器造图，判别器辨真伪，对抗",     "生成清晰",       "训练难、模式崩溃"),
    ("Diffusion",  "慢慢擦掉再慢慢画回来", "前向加噪→反向去噪",                "质量高、可控",   "生成慢（迭代多步）"),
]
print(f"{'模型':<12}{'核心比喻':<22}{'机制':<28}{'优势':<14}{'劣势'}")
print("-" * 90)
for name, metaphor, mechanism, pros, cons in models:
    print(f"{name:<12}{metaphor:<22}{mechanism:<28}{pros:<14}{cons}")

print("\n✅ 全部演示完成。")
