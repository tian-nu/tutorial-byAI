"""
Ch35 · 完整 Transformer 拼装与训练
===================================
- 把前面所有零件拼成完整 Transformer
- PositionalEncoding 封装成 nn.Module（Ch31 函数版 → 这里类版）
- 跑通"复制序列"任务：loss 从 ~ln(vocab) 降到接近 0
- 解释初始 loss ≈ ln(vocab) 的原因
- 演示 teacher forcing：输入 tgt[:, :-1]，预测 tgt[:, 1:]

运行：
    cd 深度学习从0到Transformer教程/code
    python ch35_full_transformer.py
"""
import math
import torch
import torch.nn as nn
import torch.nn.functional as F

# 复用前面章节的组件
from ch33_ffn_encoder_block import EncoderBlock
from ch34_decoder_block_mask import DecoderBlock, make_causal_mask


# -------------------------------------------------------------------
# PositionalEncoding（Ch31 的 sin/cos 函数版封装成 Module）
# -------------------------------------------------------------------
class PositionalEncoding(nn.Module):
    """把 Ch31 的 PE 函数封装成 Module，方便在 Transformer 里调用。

    封装原因：
    - Transformer 是 nn.Module，子组件也应为 Module，便于 .to(device) 和 .eval()
    - 用 register_buffer 注册 pe，让它随模型一起移动到 GPU
    """
    def __init__(self, d_model, max_len=5000, dropout=0.1):
        super().__init__()
        self.dropout = nn.Dropout(dropout)
        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len).unsqueeze(1).float()
        div_term = torch.exp(
            torch.arange(0, d_model, 2).float() * -(math.log(10000.0) / d_model)
        )
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        self.register_buffer('pe', pe.unsqueeze(0))   # (1, max_len, d_model)

    def forward(self, x):
        # x shape: (B, T, d_model)
        x = x + self.pe[:, :x.size(1)]
        return self.dropout(x)


# -------------------------------------------------------------------
# 完整 Transformer
# -------------------------------------------------------------------
class Transformer(nn.Module):
    def __init__(self, src_vocab, tgt_vocab, d_model=512, n_heads=8,
                 N=6, d_ff=2048, dropout=0.1):
        super().__init__()
        self.src_emb = nn.Embedding(src_vocab, d_model)
        self.tgt_emb = nn.Embedding(tgt_vocab, d_model)
        self.pos_enc = PositionalEncoding(d_model, dropout=dropout)
        self.encoder = nn.ModuleList(
            [EncoderBlock(d_model, n_heads, d_ff, dropout) for _ in range(N)]
        )
        self.decoder = nn.ModuleList(
            [DecoderBlock(d_model, n_heads, d_ff, dropout) for _ in range(N)]
        )
        self.fc_out = nn.Linear(d_model, tgt_vocab)

    def forward(self, src, tgt, tgt_mask=None):
        # Encoder 路径
        src = self.pos_enc(self.src_emb(src))
        for enc in self.encoder:
            src = enc(src)
        # Decoder 路径
        tgt = self.pos_enc(self.tgt_emb(tgt))
        for dec in self.decoder:
            tgt = dec(tgt, src, tgt_mask=tgt_mask)
        # 输出层
        return self.fc_out(tgt)


def main():
    print("=== Ch35: 完整 Transformer 拼装与训练 ===\n")

    torch.manual_seed(42)

    # ---------------------------------------------------------------
    # 1. 模型配置
    # 用较小的 vocab 和 T 让复制任务在 100 步内可见 loss 下降
    # 注：vocab=100 时初始 loss ≈ ln(100)≈4.6（见下方验证）
    # ---------------------------------------------------------------
    vocab = 100                            # 用于演示 ln(vocab) 初始 loss
    d_model = 128
    n_heads = 4
    N = 3
    d_ff = 512
    T = 6
    B = 16                                 # 较大 batch 加速收敛

    model = Transformer(
        src_vocab=vocab, tgt_vocab=vocab,
        d_model=d_model, n_heads=n_heads, N=N, d_ff=d_ff, dropout=0.0   # 小模型关 dropout
    )
    print(f"模型配置: vocab={vocab}, d_model={d_model}, n_heads={n_heads}, N={N}, d_ff={d_ff}")
    print(f"参数总量: {sum(p.numel() for p in model.parameters()):,}\n")

    # ---------------------------------------------------------------
    # 2. 验证初始 loss ≈ ln(vocab)
    # ---------------------------------------------------------------
    print("--- 初始 loss 验证 ---")
    print(f"vocab = {vocab}, ln(vocab) = {math.log(vocab):.4f}")

    src = torch.randint(1, vocab, (B, T))
    tgt = src.clone()                     # 复制任务：tgt = src
    # 注意：模型输入是 tgt[:, :-1]（长度 T-1），mask 尺寸要与之匹配
    tgt_mask = make_causal_mask(T - 1)

    model.eval()
    with torch.no_grad():
        logits = model(src, tgt[:, :-1], tgt_mask=tgt_mask)
        loss_init = F.cross_entropy(
            logits.reshape(-1, vocab), tgt[:, 1:].reshape(-1)
        )
    print(f"初始 loss = {loss_init.item():.4f}")
    assert abs(loss_init.item() - math.log(vocab)) < 1.0, "初始 loss 应接近 ln(vocab)"
    print("✅ 初始 loss 接近 ln(vocab)，符合均匀分布的交叉熵\n")

    # ---------------------------------------------------------------
    # 3. 训练循环（复制序列任务）
    # 用固定训练集（200 条序列）让模型能学会复制算法
    # warmup + Adam 让 Post-LN 架构训练更稳
    # ---------------------------------------------------------------
    print("--- 训练循环（复制序列任务）---")
    model.train()
    opt = torch.optim.Adam(model.parameters(), lr=1e-3)
    loss_fn = nn.CrossEntropyLoss()

    # warmup: 前 20 步线性升温到 1e-3，之后保持
    warmup_steps = 20
    def lr_lambda(step):
        return min(1.0, (step + 1) / warmup_steps)
    scheduler = torch.optim.lr_scheduler.LambdaLR(opt, lr_lambda)

    # 固定训练集：200 条随机序列，模型学复制算法
    n_train = 200
    train_src = torch.randint(1, vocab, (n_train, T))

    n_steps = 200
    for step in range(n_steps):
        # 每步随机抽 B 条
        idx = torch.randint(0, n_train, (B,))
        src = train_src[idx]
        tgt = src.clone()                   # 复制任务：tgt = src
        tgt_mask = make_causal_mask(T - 1)

        logits = model(src, tgt[:, :-1], tgt_mask=tgt_mask)
        loss = loss_fn(logits.reshape(-1, vocab), tgt[:, 1:].reshape(-1))

        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        opt.step()
        opt.zero_grad()
        scheduler.step()

        if step % 20 == 0 or step == n_steps - 1:
            print(f"  step {step:3d}: loss = {loss.item():.4f}")

    print()

    # ---------------------------------------------------------------
    # 4. 验证模型真的学会了
    # ---------------------------------------------------------------
    print("--- 验证模型是否学会复制 ---")
    model.eval()
    with torch.no_grad():
        test_src = torch.randint(1, vocab, (1, T))
        test_tgt = test_src.clone()
        test_mask = make_causal_mask(T - 1)   # 与 test_tgt[:, :-1] 长度一致

        logits = model(test_src, test_tgt[:, :-1], tgt_mask=test_mask)
        preds = logits.argmax(dim=-1)

        print(f"输入 src  = {test_src[0].tolist()}")
        print(f"目标 tgt  = {test_tgt[0, 1:].tolist()}")
        print(f"预测 pred = {preds[0].tolist()}")
        acc = (preds[0] == test_tgt[0, 1:]).float().mean().item()
        print(f"准确率 = {acc:.2%}")
        if acc > 0.8:
            print("✅ 模型学会了复制任务\n")
        else:
            print("⚠️  准确率偏低，可能需要更多训练步数\n")

    # ---------------------------------------------------------------
    # 5. 演示 teacher forcing 的对齐
    # ---------------------------------------------------------------
    print("--- Teacher Forcing 对齐演示 ---")
    print("tgt     = [<BOS>, w1, w2, w3, <EOS>]")
    print("输入    = [<BOS>, w1, w2, w3]          (tgt[:, :-1])")
    print("目标    = [w1,    w2, w3, <EOS>]       (tgt[:, 1:])")
    print("Decoder 第 i 位输入第 i 个词，预测第 i+1 个词，配合因果 mask 保证只看过去\n")

    # ---------------------------------------------------------------
    # 6. 演示 ignore_index（padding 不计入 loss）
    # ---------------------------------------------------------------
    print("--- ignore_index 演示 ---")
    pad_id = 0
    tgt_padded = torch.tensor([[1, 5, 8, pad_id, pad_id]])     # 后两位 padding
    loss_fn_pad = nn.CrossEntropyLoss(ignore_index=pad_id)

    src_padded = torch.randint(1, vocab, (1, 5))
    tgt_mask_pad = make_causal_mask(4)   # tgt_padded[:, :-1] 长度为 4
    with torch.no_grad():
        logits = model(src_padded, tgt_padded[:, :-1], tgt_mask=tgt_mask_pad)
        loss_padded = loss_fn_pad(
            logits.reshape(-1, vocab), tgt_padded[:, 1:].reshape(-1)
        )
    print(f"含 padding 的 tgt = {tgt_padded[0].tolist()}")
    print(f"ignore_index={pad_id} 的 loss = {loss_padded.item():.4f}")
    print("要点：padding 位置不计入 loss，避免模型浪费容量学预测 padding\n")

    print("=== Ch35 完成 ===")
    print()
    print("📊 可视化演示见 35_transformer_architecture_visual.html")


if __name__ == "__main__":
    main()
