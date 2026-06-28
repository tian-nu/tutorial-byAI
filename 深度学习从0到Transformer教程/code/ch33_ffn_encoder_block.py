"""
Ch33 · 前馈网络与完整 Encoder 块
================================
- 手算 FFN 数值小例子（d_model=4, d_ff=8，用"前4列类对角"小矩阵，非单位矩阵）
- 实现 FeedForward（两层线性 + ReLU）
- 实现 EncoderBlock（MHA + 残差 + LN）→ FFN + 残差 + LN）
- 端到端验证输出形状保持 (B, T, d_model)

运行：
    cd 深度学习从0到Transformer教程/code
    python ch33_ffn_encoder_block.py
"""
import torch
import torch.nn as nn
import torch.nn.functional as F


# -------------------------------------------------------------------
# 依赖：MultiHeadAttention（来自 Ch30，这里给出最小可用实现）
# 注：本章重点在 FFN 和 EncoderBlock，MHA 只为保证代码可运行
# -------------------------------------------------------------------
class MultiHeadAttention(nn.Module):
    def __init__(self, d_model, n_heads):
        super().__init__()
        assert d_model % n_heads == 0, "d_model 必须能被 n_heads 整除"
        self.d_model = d_model
        self.n_heads = n_heads
        self.d_k = d_model // n_heads
        self.W_q = nn.Linear(d_model, d_model)
        self.W_k = nn.Linear(d_model, d_model)
        self.W_v = nn.Linear(d_model, d_model)
        self.W_o = nn.Linear(d_model, d_model)

    def forward(self, x, mask=None):
        B, T, _ = x.shape
        q = self.W_q(x).view(B, T, self.n_heads, self.d_k).transpose(1, 2)
        k = self.W_k(x).view(B, T, self.n_heads, self.d_k).transpose(1, 2)
        v = self.W_v(x).view(B, T, self.n_heads, self.d_k).transpose(1, 2)
        scores = q @ k.transpose(-2, -1) / (self.d_k ** 0.5)
        if mask is not None:
            scores = scores + mask
        attn = F.softmax(scores, dim=-1)
        out = attn @ v
        out = out.transpose(1, 2).contiguous().view(B, T, self.d_model)
        return self.W_o(out)


# -------------------------------------------------------------------
# FFN：两层线性 + ReLU
# -------------------------------------------------------------------
class FeedForward(nn.Module):
    def __init__(self, d_model, d_ff, dropout=0.1):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(d_model, d_ff),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(d_ff, d_model),
        )

    def forward(self, x):
        return self.net(x)


# -------------------------------------------------------------------
# EncoderBlock：MHA 子层 + FFN 子层（Post-LN 风格）
# -------------------------------------------------------------------
class EncoderBlock(nn.Module):
    def __init__(self, d_model, n_heads, d_ff, dropout=0.1):
        super().__init__()
        self.mha = MultiHeadAttention(d_model, n_heads)
        self.ff = FeedForward(d_model, d_ff)
        self.ln1 = nn.LayerNorm(d_model)
        self.ln2 = nn.LayerNorm(d_model)
        self.dropout = nn.Dropout(dropout)

    def forward(self, x):
        # 子层1: MHA + 残差 + LN
        x = self.ln1(x + self.dropout(self.mha(x)))
        # 子层2: FFN + 残差 + LN
        x = self.ln2(x + self.dropout(self.ff(x)))
        return x


def main():
    print("=== Ch33: FFN 与完整 Encoder 块 ===\n")

    # ---------------------------------------------------------------
    # 1. FFN 数值小例子（d_model=4, d_ff=8）
    # 用"前4列类对角"小矩阵，不是单位矩阵（4×8 不是方阵）
    # ---------------------------------------------------------------
    print("--- FFN 数值小例子 ---")
    x = torch.tensor([[1.0, 0.5, -0.3, 0.8]])
    print(f"x = {x[0].numpy()}")

    d_model, d_ff = 4, 8
    ff = FeedForward(d_model, d_ff, dropout=0.0)

    # 手动设置 W_1、b_1、W_2、b_2 为教程里的"类对角"结构
    with torch.no_grad():
        # W_1 (4×8): 前 4 列为对角，后 4 列全 0
        W1 = torch.zeros(d_ff, d_model)   # nn.Linear 权重形状 (out, in)
        for i in range(d_model):
            W1[i, i] = 1.0
        ff.net[0].weight.copy_(W1)
        ff.net[0].bias.zero_()

        # W_2 (4×8) 形状在 nn.Linear 里是 (d_model, d_ff)
        W2 = torch.zeros(d_model, d_ff)
        for i in range(d_model):
            W2[i, i] = 1.0
        ff.net[3].weight.copy_(W2)
        ff.net[3].bias.zero_()

    # 分步打印
    with torch.no_grad():
        h_pre = ff.net[0](x)             # Linear(d_model, d_ff)
        h = ff.net[1](h_pre)             # ReLU
        out = ff.net[3](h)               # Linear(d_ff, d_model)（中间 dropout=0）

    print(f"W_1·x + b_1 = {h_pre[0].numpy()}")
    print(f"ReLU 后 h   = {h[0].numpy()}")
    print(f"FFN(x)      = {out[0].numpy()}")
    expected = torch.tensor([[1.0, 0.5, 0.0, 0.8]])
    assert torch.allclose(out, expected, atol=1e-6), "FFN 手算结果不一致"
    print("✅ 手算与 PyTorch 一致\n")

    # ---------------------------------------------------------------
    # 2. 残差 + LN 演示
    # ---------------------------------------------------------------
    print("--- FFN + 残差 + LN ---")
    ln = nn.LayerNorm(d_model)
    with torch.no_grad():
        residual = out + x
        final = ln(residual)
    print(f"FFN(x) + x = {(out + x)[0].numpy()}")
    print(f"LN(FFN(x)+x) = {final[0].numpy()}")
    print(f"LN 后均值 ≈ {final.mean().item():.4f}, 方差 ≈ {final.var(unbiased=False).item():.4f}\n")

    # ---------------------------------------------------------------
    # 3. 完整 Encoder 块端到端
    # ---------------------------------------------------------------
    print("--- 完整 Encoder 块 ---")
    enc_block = EncoderBlock(d_model=512, n_heads=8, d_ff=2048)
    x_in = torch.randn(2, 10, 512)
    x_out = enc_block(x_in)
    print(f"输入 shape = {tuple(x_in.shape)}")
    print(f"输出 shape = {tuple(x_out.shape)}")
    assert x_out.shape == x_in.shape, "Encoder 块应保持形状不变"
    print("✅ 输出形状与输入相同\n")

    # ---------------------------------------------------------------
    # 4. 多层 Encoder 堆叠
    # ---------------------------------------------------------------
    print("--- 6 层 Encoder 堆叠 ---")
    layers = nn.ModuleList([
        EncoderBlock(d_model=512, n_heads=8, d_ff=2048) for _ in range(6)
    ])
    h = x_in
    for i, layer in enumerate(layers):
        h = layer(h)
        print(f"  经第 {i+1} 层后 shape = {tuple(h.shape)}, 均值 = {h.mean().item():.4f}")
    print("✅ 6 层堆叠成功，形状保持 (2, 10, 512)\n")

    # ---------------------------------------------------------------
    # 5. FFN 是 position-wise 的验证
    # ---------------------------------------------------------------
    print("--- FFN 是 position-wise 验证 ---")
    ff_small = FeedForward(4, 8, dropout=0.0)
    x_a = torch.tensor([[[1.0, 0.5, -0.3, 0.8]]])           # (1, 1, 4)
    x_b = torch.tensor([[[1.0, 0.5, -0.3, 0.8],
                         [1.0, 0.5, -0.3, 0.8]]])           # (1, 2, 4) 同样的两行
    with torch.no_grad():
        out_a = ff_small(x_a)
        out_b = ff_small(x_b)
    diff = (out_b[0, 0] - out_b[0, 1]).abs().max().item()
    print(f"两个相同位置分别单独算和合并算，差异 = {diff:.2e}")
    assert diff < 1e-6, "FFN 应该是 position-wise，位置间互不影响"
    print("✅ FFN 对每个位置独立计算，位置间互不影响\n")

    print("=== Ch33 完成 ===")


if __name__ == "__main__":
    main()
