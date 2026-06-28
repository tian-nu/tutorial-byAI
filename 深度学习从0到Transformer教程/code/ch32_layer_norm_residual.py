"""
Ch32 · LayerNorm 与残差连接
============================
- 手算 LN([1,2,3]) 并与 nn.LayerNorm 对比
- 演示 LayerNorm vs BatchNorm 的作用维度差异
- 实现一个 Pre-LN 风格的"残差 + LN"子层壳
- 演示残差连接对梯度流的保护作用

运行：
    cd 深度学习从0到Transformer教程/code
    python ch32_layer_norm_residual.py
"""
import torch
import torch.nn as nn
import torch.nn.functional as F


def main():
    print("=== Ch32: LayerNorm 与残差连接 ===\n")

    # ---------------------------------------------------------------
    # 1. 手算 LN([1, 2, 3]) 与 PyTorch 对比
    # ---------------------------------------------------------------
    print("--- 手算 LN 验证 ---")
    x = torch.tensor([1.0, 2.0, 3.0])
    eps = 1e-5

    mu = x.mean()
    var = x.var(unbiased=False)            # 总体方差（除以 N），与 nn.LayerNorm 一致
    std = torch.sqrt(var + eps)

    hand_ln = (x - mu) / std               # γ=1, β=0
    print(f"输入 x = {x.numpy()}")
    print(f"μ = {mu:.4f}, σ² = {var:.4f}, √(σ²+ε) = {std:.4f}")
    print(f"手算 LN(x) = {hand_ln.numpy()}")

    ln = nn.LayerNorm(3)                   # 默认 γ=1, β=0
    # 固定参数确保对比公平
    with torch.no_grad():
        ln.weight.fill_(1.0)
        ln.bias.fill_(0.0)
    torch_ln = ln(x)
    print(f"nn.LayerNorm 输出 = {torch_ln.detach().numpy()}")
    assert torch.allclose(hand_ln, torch_ln, atol=1e-5), "手算与 PyTorch 不一致！"
    print("✅ 手算与 PyTorch 一致\n")

    # ---------------------------------------------------------------
    # 2. LayerNorm vs BatchNorm 作用维度对比
    # ---------------------------------------------------------------
    print("--- LayerNorm vs BatchNorm 作用维度 ---")
    # 构造 (B=4, T=3, d_model=5) 的输入
    x_seq = torch.randn(4, 3, 5)

    ln_seq = nn.LayerNorm(5)
    bn_seq = nn.BatchNorm1d(5)             # BN 默认对 (B, C) 或 (B, C, L) 操作

    out_ln = ln_seq(x_seq)
    # BN 需要 (B, C) 形状，把 T 维拼到 B 上
    x_flat = x_seq.reshape(4 * 3, 5)
    out_bn = bn_seq(x_flat).reshape(4, 3, 5)

    print(f"输入 shape = {tuple(x_seq.shape)}  (B, T, d_model)")
    print(f"LN 后 d_model 维均值≈0: {out_ln.mean(dim=-1).mean().item():.4f}")
    print(f"BN 后 d_model 维均值（per-channel）: {out_bn.mean(dim=(0,1)).abs().mean().item():.4f}")
    print("要点：LN 沿最后一维（特征维）归一化；BN 沿 batch 维归一化（每个通道独立）\n")

    # ---------------------------------------------------------------
    # 3. Pre-LN 风格的"残差 + LN"子层壳
    # ---------------------------------------------------------------
    print("--- 残差 + LN 子层壳（Pre-LN）---")

    class ResidualSubLayer(nn.Module):
        """Pre-LN: x + dropout(sublayer(LN(x)))"""
        def __init__(self, d_model, dropout=0.1):
            super().__init__()
            self.ln = nn.LayerNorm(d_model)
            self.dropout = nn.Dropout(dropout)

        def forward(self, x, sublayer):
            return x + self.dropout(sublayer(self.ln(x)))

    class DummySubLayer(nn.Module):
        """一个简单的子层：线性变换 + ReLU，输出维度不变"""
        def __init__(self, d_model):
            super().__init__()
            self.fc = nn.Linear(d_model, d_model)

        def forward(self, x):
            return F.relu(self.fc(x))

    d_model = 8
    shell = ResidualSubLayer(d_model)
    sub = DummySubLayer(d_model)

    x_in = torch.randn(2, 5, d_model)
    out = shell(x_in, sub)
    print(f"输入 shape = {tuple(x_in.shape)}")
    print(f"SubLayer 输出 shape = {tuple(out.shape)}")
    assert out.shape == x_in.shape, "残差要求输出与输入同形"
    print("✅ 残差连接输出与输入同形\n")

    # ---------------------------------------------------------------
    # 4. 残差连接对梯度流的保护
    # ---------------------------------------------------------------
    print("--- 残差连接保护梯度流 ---")
    torch.manual_seed(0)

    # 4 个子层堆叠，无残差
    class StackNoResidual(nn.Module):
        def __init__(self, d_model, n_layers=4):
            super().__init__()
            self.layers = nn.ModuleList([DummySubLayer(d_model) for _ in range(n_layers)])

        def forward(self, x):
            for layer in self.layers:
                x = layer(x)
            return x

    # 4 个子层堆叠，带残差
    class StackWithResidual(nn.Module):
        def __init__(self, d_model, n_layers=4):
            super().__init__()
            self.shells = nn.ModuleList([ResidualSubLayer(d_model) for _ in range(n_layers)])
            self.subs = nn.ModuleList([DummySubLayer(d_model) for _ in range(n_layers)])

        def forward(self, x):
            for shell, sub in zip(self.shells, self.subs):
                x = shell(x, sub)
            return x

    d_model = 16
    x_test = torch.randn(1, 4, d_model, requires_grad=True)

    no_res = StackNoResidual(d_model)
    with_res = StackWithResidual(d_model)

    out_no = no_res(x_test)
    out_with = with_res(x_test)

    # 反向传播看输入梯度
    out_no.sum().backward(retain_graph=True)
    grad_no = x_test.grad.abs().mean().item()
    x_test.grad = None

    out_with.sum().backward()
    grad_with = x_test.grad.abs().mean().item()

    print(f"4 层堆叠，反向后输入端梯度的绝对值均值：")
    print(f"  无残差: {grad_no:.6f}")
    print(f"  有残差: {grad_with:.6f}")
    print("要点：残差连接给梯度一条'高速公路'，底层梯度不会被层层雅可比连乘缩成 0\n")

    # ---------------------------------------------------------------
    # 5. Post-LN vs Pre-LN 对比
    # ---------------------------------------------------------------
    print("--- Post-LN vs Pre-LN ---")
    print("Post-LN: LN(x + SubLayer(x))    # 原始 Transformer，需 warmup")
    print("Pre-LN:  x + SubLayer(LN(x))    # 现代 GPT 风格，训练更稳")
    print("本章代码默认用 Pre-LN，主流程对深层网络更稳\n")

    print("=== Ch32 完成 ===")


if __name__ == "__main__":
    main()
