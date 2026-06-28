"""
Ch27 · Seq2Seq 与编码器-解码器架构
===================================
最小可运行的 Encoder-Decoder 演示：
- Encoder 用 LSTM 把输入序列压成上下文向量 (h, c)
- Decoder 用 LSTM 以 (h, c) 为初始状态，逐步生成输出
- 同时演示训练模式 (Teacher Forcing) 与推理模式 (自回归)

运行：
    cd 深度学习从0到Transformer教程/code
    python ch27_seq2seq.py

依赖：torch (pip install torch)
"""

import sys

try:
    import torch
    import torch.nn as nn
    import torch.nn.functional as F
except ImportError:
    print("[Ch27] 本模块需要 PyTorch 才能运行。")
    print("       请先安装：pip install torch")
    print("       安装后重新运行：python ch27_seq2seq.py")
    sys.exit(0)


# ============== 1. Encoder ==============
class Encoder(nn.Module):
    """读入整数索引序列，输出最终隐藏状态 (h, c) 作为上下文向量。"""

    def __init__(self, vocab_size: int, emb_dim: int, hid_dim: int):
        super().__init__()
        self.emb = nn.Embedding(vocab_size, emb_dim, padding_idx=0)
        self.lstm = nn.LSTM(emb_dim, hid_dim, batch_first=True)

    def forward(self, x: torch.Tensor):
        # x: (batch, T) LongTensor
        emb = self.emb(x)               # (batch, T, emb_dim)
        outputs, (h, c) = self.lstm(emb)  # h, c: (1, batch, hid_dim)
        return outputs, (h, c)


# ============== 2. Decoder ==============
class Decoder(nn.Module):
    """以 (h, c) 为初始状态，每步输入一个 token，输出 logits。"""

    def __init__(self, vocab_size: int, emb_dim: int, hid_dim: int):
        super().__init__()
        self.emb = nn.Embedding(vocab_size, emb_dim, padding_idx=0)
        self.lstm = nn.LSTM(emb_dim, hid_dim, batch_first=True)
        self.fc = nn.Linear(hid_dim, vocab_size)

    def forward(self, y: torch.Tensor, h: torch.Tensor, c: torch.Tensor):
        # y: (batch, 1) 当前步输入 token 的索引
        emb = self.emb(y)                       # (batch, 1, emb_dim)
        out, (h, c) = self.lstm(emb, (h, c))    # out: (batch, 1, hid_dim)
        logits = self.fc(out.squeeze(1))        # (batch, vocab_size)
        return logits, h, c


# ============== 3. Seq2Seq 训练 (Teacher Forcing) ==============
def train_forward(encoder: Encoder, decoder: Decoder,
                  src: torch.Tensor, trg: torch.Tensor,
                  start_token: int = 1):
    """
    训练模式：使用 Teacher Forcing。
    src: (batch, T_src) 输入序列
    trg: (batch, T_trg) 目标序列 (含 <START>)
    返回 logits: (batch, T_trg, vocab_size)
    """
    batch_size, T_trg = trg.shape
    vocab_size = decoder.fc.out_features

    # Encoder 跑一遍
    _, (h, c) = encoder(src)

    # Decoder 第一步输入 <START>
    y = trg[:, 0:1]  # (batch, 1) 取目标序列第一个 token 作为 <START>
    logits_list = []

    for t in range(1, T_trg):
        # Teacher Forcing: 用真实标签 trg[:, t-1:t] 作为输入
        y = trg[:, t - 1:t]
        logits, h, c = decoder(y, h, c)
        logits_list.append(logits)

    # (batch, T_trg-1, vocab_size)
    return torch.stack(logits_list, dim=1)


# ============== 4. Seq2Seq 推理 (自回归) ==============
def infer_forward(encoder: Encoder, decoder: Decoder,
                  src: torch.Tensor, start_token: int = 1,
                  end_token: int = 2, max_len: int = 20):
    """
    推理模式：自回归生成，遇到 <END> 或达到 max_len 停止。
    返回生成的 token 索引列表。
    """
    batch_size = src.shape[0]
    _, (h, c) = encoder(src)

    y = torch.full((batch_size, 1), start_token, dtype=torch.long, device=src.device)
    generated = []

    for _ in range(max_len):
        logits, h, c = decoder(y, h, c)
        next_token = logits.argmax(dim=-1, keepdim=True)  # (batch, 1)
        generated.append(next_token)
        y = next_token
        if (next_token == end_token).all():
            break

    return torch.cat(generated, dim=1)  # (batch, T_gen)


# ============== 5. 主程序：跑一个小例子 ==============
def main():
    torch.manual_seed(42)

    # 假设词表大小 20，嵌入 8 维，隐藏 8 维
    vocab_size = 20
    emb_dim = 8
    hid_dim = 8

    encoder = Encoder(vocab_size, emb_dim, hid_dim)
    decoder = Decoder(vocab_size, emb_dim, hid_dim)

    # 构造假数据：batch=2，输入 3 词，输出 4 词 (含 <START> 和 <END>)
    # 1=<START>, 2=<END>, 0=<PAD>
    src = torch.tensor([[3, 4, 5], [6, 7, 8]])   # (2, 3)
    trg = torch.tensor([[1, 9, 10, 2], [1, 11, 12, 2]])  # (2, 4)

    print("=== Seq2Seq 前向 ===")
    _, (h, c) = encoder(src)
    print(f"Encoder (h, c) 形状: {h.shape}, {c.shape}")  # (1, 2, 8)

    # 训练模式
    train_logits = train_forward(encoder, decoder, src, trg)
    print(f"训练模式 logits 形状: {train_logits.shape}")  # (2, 3, 20)
    print("训练模式: 用真实标签作为下一步输入 (Teacher Forcing)")

    # 推理模式
    generated = infer_forward(encoder, decoder, src, max_len=5)
    print(f"推理模式生成 token: {generated.tolist()}")
    print("推理模式: 用预测值作为下一步输入")

    # 验证：训练模式下，相同输入但不同 trg，输出不同（因为 Teacher Forcing 不同）
    print("\n=== 验证 Teacher Forcing 的效果 ===")
    trg_a = torch.tensor([[1, 9, 10, 2], [1, 11, 12, 2]])
    trg_b = torch.tensor([[1, 13, 14, 2], [1, 15, 16, 2]])
    out_a = train_forward(encoder, decoder, src, trg_a)
    out_b = train_forward(encoder, decoder, src, trg_b)
    diff = (out_a - out_b).abs().mean().item()
    print(f"两条不同 trg 下的 logits 平均差异: {diff:.4f} (应 > 0，说明 Teacher Forcing 让输出依赖真实标签)")

    print("\n✅ Ch27 Seq2Seq 演示完成")


if __name__ == "__main__":
    main()
