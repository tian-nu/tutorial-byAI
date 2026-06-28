"""
Ch34 · Decoder 块与 Masked Attention
=====================================
- 构造下三角因果 mask（上三角 -inf）
- 手算 3×3 数值小例子，验证 mask 后上三角严格为 0
- 实现 DecoderBlock（三个子层：Masked Self-Attn / Cross-Attn / FFN）
- 端到端验证输出形状保持 (B, T_tgt, d_model)

接口说明：
- Ch30 的 MultiHeadAttention.forward(x) 需扩展为 forward(q, k=None, v=None, mask=None)
  · k/v 为 None 时，默认 Q=K=V=q（自注意力）
  · 传 k、v 时为交叉注意力（Q=q, K=k, V=v）
  · mask 可选，加到 score 矩阵上再 softmax

运行：
    cd 深度学习从0到Transformer教程/code
    python ch34_decoder_block_mask.py
"""
import torch
import torch.nn as nn
import torch.nn.functional as F


# -------------------------------------------------------------------
# 依赖：MultiHeadAttention（扩展签名以支持 mask 和 cross-attention）
# -------------------------------------------------------------------
class MultiHeadAttention(nn.Module):
    """支持 mask 和 cross-attention 的多头注意力。

    forward(q, k=None, v=None, mask=None):
      - k/v 为 None → 自注意力（Q=K=V=q）
      - 传 k、v → 交叉注意力（Q=q, K=k, V=v）
      - mask 加到 scores 上再 softmax
    """
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

    def forward(self, q, k=None, v=None, mask=None):
        if k is None:
            k = q
        if v is None:
            v = q
        B, Tq, _ = q.shape
        Tk = k.size(1)

        q = self.W_q(q).view(B, Tq, self.n_heads, self.d_k).transpose(1, 2)
        k = self.W_k(k).view(B, Tk, self.n_heads, self.d_k).transpose(1, 2)
        v = self.W_v(v).view(B, Tk, self.n_heads, self.d_k).transpose(1, 2)

        scores = q @ k.transpose(-2, -1) / (self.d_k ** 0.5)   # (B, H, Tq, Tk)
        if mask is not None:
            # mask 形状 (Tq, Tk) 或 (B, 1, Tq, Tk)，可广播
            scores = scores + mask
        attn = F.softmax(scores, dim=-1)
        out = attn @ v                                         # (B, H, Tq, d_k)
        out = out.transpose(1, 2).contiguous().view(B, Tq, self.d_model)
        return self.W_o(out)


# -------------------------------------------------------------------
# 依赖：FeedForward（来自 Ch33）
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
# DecoderBlock：三个子层
# -------------------------------------------------------------------
class DecoderBlock(nn.Module):
    def __init__(self, d_model, n_heads, d_ff, dropout=0.1):
        super().__init__()
        self.self_attn = MultiHeadAttention(d_model, n_heads)
        self.cross_attn = MultiHeadAttention(d_model, n_heads)
        self.ff = FeedForward(d_model, d_ff)
        self.ln1 = nn.LayerNorm(d_model)
        self.ln2 = nn.LayerNorm(d_model)
        self.ln3 = nn.LayerNorm(d_model)
        self.dropout = nn.Dropout(dropout)

    def forward(self, x, enc_out, tgt_mask=None):
        # 子层1: Masked Self-Attention（Q=K=V=x，传 tgt_mask）
        x = self.ln1(x + self.dropout(self.self_attn(x, mask=tgt_mask)))
        # 子层2: Cross-Attention（Q=x, K=V=enc_out，不需要 mask）
        x = self.ln2(x + self.dropout(self.cross_attn(x, k=enc_out, v=enc_out)))
        # 子层3: FFN
        x = self.ln3(x + self.dropout(self.ff(x)))
        return x


def make_causal_mask(T):
    """生成 T×T 因果 mask：上三角为 -inf，下三角为 0。"""
    return torch.triu(torch.ones(T, T) * float('-inf'), diagonal=1)


def main():
    print("=== Ch34: Decoder 块与 Masked Attention ===\n")

    # ---------------------------------------------------------------
    # 1. 因果 mask 构造
    # ---------------------------------------------------------------
    print("--- 因果 mask ---")
    T = 5
    mask = make_causal_mask(T)
    print(f"mask ({T}×{T}) =")
    print(mask.numpy())
    print("要点：上三角（未来位置）= -inf，下三角（过去和现在）= 0\n")

    # ---------------------------------------------------------------
    # 2. 3×3 数值小例子手算验证
    # ---------------------------------------------------------------
    print("--- 3×3 数值小例子 ---")
    scores = torch.tensor([[1.0, 0.5, 0.3],
                           [0.4, 0.8, 0.2],
                           [0.6, 0.3, 0.9]])
    mask3 = make_causal_mask(3)
    masked = scores + mask3
    print(f"原始 scores =\n{scores.numpy()}")
    print(f"mask =\n{mask3.numpy()}")
    print(f"masked scores =\n{masked.numpy()}")

    # 逐行 softmax（手工算）
    weights = torch.zeros_like(scores)
    # 第 1 行: softmax([1.0, -inf, -inf]) = [1.0, 0, 0]
    weights[0] = torch.tensor([1.0, 0.0, 0.0])
    # 第 2 行: softmax([0.4, 0.8, -inf])
    e = torch.tensor([torch.exp(torch.tensor(0.4)).item(),
                      torch.exp(torch.tensor(0.8)).item(), 0.0])
    weights[1] = e / e.sum()
    # 第 3 行: softmax([0.6, 0.3, 0.9])
    e = torch.tensor([torch.exp(torch.tensor(0.6)).item(),
                      torch.exp(torch.tensor(0.3)).item(),
                      torch.exp(torch.tensor(0.9)).item()])
    weights[2] = e / e.sum()

    # 用 PyTorch softmax 验证
    torch_weights = F.softmax(masked, dim=-1)
    print(f"手算 attn weights =\n{weights.numpy()}")
    print(f"PyTorch softmax =\n{torch_weights.numpy()}")
    assert torch.allclose(weights, torch_weights, atol=1e-4), "手算与 PyTorch 不一致"
    print("✅ 手算与 PyTorch 一致")

    # 验证上三角严格为 0
    upper = torch_weights.triu(diagonal=1)
    assert (upper == 0).all(), "上三角应严格为 0"
    print("✅ 上三角严格为 0（未来被封住）\n")

    # ---------------------------------------------------------------
    # 3. mask 用 0 而非 -inf 的错误演示
    # ---------------------------------------------------------------
    print("--- 错误演示：用 0 而非 -inf 做 mask ---")
    wrong_mask = torch.triu(torch.ones(3, 3) * 0.0, diagonal=1)  # 上三角填 0
    wrong_masked = scores + wrong_mask
    wrong_weights = F.softmax(wrong_masked, dim=-1)
    print(f"用 0 做 mask 的 weights =\n{wrong_weights.numpy()}")
    print(f"第 1 行未来位置权重 = {wrong_weights[0, 1:].tolist()}")
    print("⚠️  未来位置权重非零，信息泄漏！正确做法是 -inf\n")

    # ---------------------------------------------------------------
    # 4. 完整 Decoder 块端到端
    # ---------------------------------------------------------------
    print("--- 完整 Decoder 块 ---")
    d_model = 64
    dec_block = DecoderBlock(d_model=d_model, n_heads=4, d_ff=128)

    B, T_tgt, T_src = 2, 8, 10
    x = torch.randn(B, T_tgt, d_model)
    enc_out = torch.randn(B, T_src, d_model)
    tgt_mask = make_causal_mask(T_tgt)

    out = dec_block(x, enc_out, tgt_mask=tgt_mask)
    print(f"输入 x shape = {tuple(x.shape)}")
    print(f"enc_out shape = {tuple(enc_out.shape)}")
    print(f"输出 shape = {tuple(out.shape)}")
    assert out.shape == x.shape, "Decoder 块应保持 tgt 形状不变"
    print("✅ 输出形状与 tgt 输入相同\n")

    # ---------------------------------------------------------------
    # 5. 多层 Decoder 堆叠
    # ---------------------------------------------------------------
    print("--- 6 层 Decoder 堆叠 ---")
    layers = nn.ModuleList([
        DecoderBlock(d_model=d_model, n_heads=4, d_ff=128) for _ in range(6)
    ])
    h = x
    for i, layer in enumerate(layers):
        h = layer(h, enc_out, tgt_mask=tgt_mask)
        print(f"  经第 {i+1} 层后 shape = {tuple(h.shape)}, 均值 = {h.mean().item():.4f}")
    print("✅ 6 层堆叠成功\n")

    # ---------------------------------------------------------------
    # 6. Cross-Attention 的 Q/K/V 来源验证
    # ---------------------------------------------------------------
    print("--- Cross-Attention Q/K/V 来源验证 ---")
    # 取一层 cross_attn，检查 K/V 来自 enc_out 而非 x
    probe = layers[0]
    # 手动调用 cross_attn，对比 K=enc_out vs K=x 的输出
    with torch.no_grad():
        out_correct = probe.cross_attn(h, k=enc_out, v=enc_out)
        out_wrong = probe.cross_attn(h, k=h, v=h)  # 错误：K/V 用 Decoder 自己
    diff = (out_correct - out_wrong).abs().mean().item()
    print(f"Cross-Attn 用 enc_out 作 K/V vs 用 x 作 K/V 的输出差异 = {diff:.4f}")
    print("要点：Cross-Attn 的 K/V 必须来自 Encoder 输出，否则 Encoder 信息丢失\n")

    print("=== Ch34 完成 ===")


if __name__ == "__main__":
    main()
