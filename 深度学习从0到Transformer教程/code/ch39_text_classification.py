"""
Ch39 · 实战一：用 PyTorch 训练文本分类模型
============================================
- IMDB 电影评论情感分类（二分类）
- 两个模型对比：BiLSTM vs Transformer Encoder
- 数据加载用 HuggingFace datasets（不用 torchtext，它在 PyTorch 2.6+ 已弃用）
- Tokenizer 用最简单的 str.lower().split()（不引入 spaCy，减少依赖）
- 训练 5 个 epoch，目标准确率 > 80%
- 计算并打印两个模型的参数量，解释 BiLSTM 的 4×(输入+隐藏+1)×隐藏×2 公式

运行：
    cd 深度学习从0到Transformer教程/code
    python ch39_text_classification.py

说明：
- 如果网络无法下载 IMDB，会自动切到模拟数据（mock），保证流程能跑通。
- 模拟数据带清晰的情感词模式，两个模型都能学到 > 80% 准确率。
- CPU 也能跑，只是慢；GPU 更快。显存不足见易错点预警（markdown 文档）。
"""
import math
import random
from collections import Counter

import torch
import torch.nn as nn
from torch.utils.data import DataLoader, Dataset

# -------------------------------------------------------------------
# 全局配置
# -------------------------------------------------------------------
SEED = 42
EMB_DIM = 100
HID_DIM = 256          # BiLSTM 隐藏维度
N_HEADS = 2            # Transformer 多头数
N_LAYERS = 2           # Transformer 层数
FF_DIM = 256           # Transformer FFN 中间维度
N_CLASSES = 2
MAX_LEN = 256          # 评论截断/补齐长度
BATCH_SIZE = 64
EPOCHS = 5
LR = 1e-3
MIN_FREQ = 10          # 词表最小词频
PAD_IDX = 1
UNK_IDX = 0

random.seed(SEED)
torch.manual_seed(SEED)

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"[设备] 使用 {DEVICE}")


# -------------------------------------------------------------------
# 1. 数据加载：优先 HuggingFace datasets，失败则用模拟数据
# -------------------------------------------------------------------
def load_imdb():
    """尝试用 datasets.load_dataset("imdb") 下载真实 IMDB。

    失败原因可能是：没装 datasets、网络不通、被墙。
    失败时返回 None，由 load_mock_data() 兜底。
    """
    try:
        from datasets import load_dataset
        print("[数据] 正在通过 HuggingFace datasets 下载 IMDB（首次约 80MB）...")
        ds = load_dataset("imdb")
        train_texts = [item["text"] for item in ds["train"]]
        train_labels = [item["label"] for item in ds["train"]]
        test_texts = [item["text"] for item in ds["test"]]
        test_labels = [item["label"] for item in ds["test"]]
        print(f"[数据] 真实 IMDB 加载成功：训练 {len(train_texts)} 条，测试 {len(test_texts)} 条")
        return (train_texts, train_labels, test_texts, test_labels, True)
    except Exception as e:
        print(f"[数据] 真实 IMDB 加载失败：{e}")
        print("[数据] 自动切换到模拟数据（mock），保证流程可跑通。")
        return None


def load_mock_data():
    """生成模拟情感分类数据。

    模式清晰：正向样本含 good/great/wonderful/excellent/love 等词，
    负向样本含 bad/terrible/awful/horrible/hate 等词，再混入随机常见词。
    两个模型都能轻松学到 > 80%。
    """
    POS_WORDS = ["good", "great", "wonderful", "excellent", "love", "amazing",
                 "fantastic", "perfect", "best", "enjoyable", "brilliant", "nice"]
    NEG_WORDS = ["bad", "terrible", "awful", "horrible", "hate", "worst",
                 "boring", "waste", "stupid", "disappointing", "poor", "dull"]
    NEUTRAL = ["movie", "film", "story", "actor", "scene", "music", "time",
               "watch", "end", "plot", "character", "director", "screen"]

    def make_sentence(positive):
        core = POS_WORDS if positive else NEG_WORDS
        n_core = random.randint(2, 4)
        n_neutral = random.randint(3, 8)
        words = [random.choice(core) for _ in range(n_core)] + \
                [random.choice(NEUTRAL) for _ in range(n_neutral)]
        random.shuffle(words)
        return " ".join(words)

    n_train, n_test = 8000, 2000
    train_texts, train_labels = [], []
    test_texts, test_labels = [], []
    for _ in range(n_train):
        label = random.randint(0, 1)
        train_texts.append(make_sentence(label == 1))
        train_labels.append(label)
    for _ in range(n_test):
        label = random.randint(0, 1)
        test_texts.append(make_sentence(label == 1))
        test_labels.append(label)
    print(f"[数据] 模拟数据生成：训练 {n_train} 条，测试 {n_test} 条")
    return train_texts, train_labels, test_texts, test_labels


# -------------------------------------------------------------------
# 2. Tokenizer + 词表
# -------------------------------------------------------------------
def tokenize(text):
    """最简单的分词：小写化 + 按空格切。

    不用 spaCy，减少依赖。对英文情感分类够用。
    """
    return text.lower().split()


def build_vocab(train_texts, min_freq=MIN_FREQ):
    """统计训练集词频，保留出现 >= min_freq 的词，加 <unk>/<pad>。"""
    counter = Counter()
    for text in train_texts:
        counter.update(tokenize(text))
    vocab = {"<unk>": UNK_IDX, "<pad>": PAD_IDX}
    for tok, cnt in counter.most_common():
        if cnt >= min_freq:
            vocab[tok] = len(vocab)
    return vocab


def text_to_ids(text, vocab, max_len=MAX_LEN):
    """单条文本 → id 列表（截断到 max_len，不足不补，collate_fn 统一补）。"""
    ids = [vocab.get(tok, UNK_IDX) for tok in tokenize(text)]
    return ids[:max_len]


# -------------------------------------------------------------------
# 3. Dataset + collate_fn（变长 → 定长 padded tensor）
# -------------------------------------------------------------------
class TextDataset(Dataset):
    def __init__(self, texts, labels, vocab):
        self.items = [(text_to_ids(t, vocab), int(l)) for t, l in zip(texts, labels)]

    def __len__(self):
        return len(self.items)

    def __getitem__(self, idx):
        return self.items[idx]


def collate_fn(batch):
    """把一个 batch 的变长 id 列表 pad 到该 batch 最大长度。

    返回 (text, label)，text 形状 (B, L)，label 形状 (B,)。
    padding 用 PAD_IDX=1。
    """
    texts, labels = zip(*batch)
    max_len = max(len(t) for t in texts)
    padded = torch.full((len(texts), max_len), PAD_IDX, dtype=torch.long)
    for i, t in enumerate(texts):
        padded[i, :len(t)] = torch.tensor(t, dtype=torch.long)
    labels = torch.tensor(labels, dtype=torch.long)
    return padded, labels


# -------------------------------------------------------------------
# 4. PositionalEncoding（Ch31 的 sin/cos，封装成 Module）
# -------------------------------------------------------------------
class PositionalEncoding(nn.Module):
    """sin/cos 位置编码。注册成 buffer，随模型一起 .to(device)。"""

    def __init__(self, d_model, max_len=512, dropout=0.1):
        super().__init__()
        self.dropout = nn.Dropout(dropout)
        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len).unsqueeze(1).float()
        div_term = torch.exp(
            torch.arange(0, d_model, 2).float() * -(math.log(10000.0) / d_model)
        )
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        self.register_buffer("pe", pe.unsqueeze(0))   # (1, max_len, d_model)

    def forward(self, x):
        # x: (B, L, d_model)
        x = x + self.pe[:, :x.size(1)]
        return self.dropout(x)


# -------------------------------------------------------------------
# 5. 两个模型
# -------------------------------------------------------------------
class BiLSTMClassifier(nn.Module):
    """双向 LSTM：取前向+后向末时刻隐藏态拼接，过 Linear 输出 logits。"""

    def __init__(self, vocab_size, emb_dim=EMB_DIM, hid_dim=HID_DIM,
                 n_classes=N_CLASSES, pad_idx=PAD_IDX):
        super().__init__()
        self.emb = nn.Embedding(vocab_size, emb_dim, padding_idx=pad_idx)
        self.lstm = nn.LSTM(emb_dim, hid_dim, batch_first=True, bidirectional=True)
        self.fc = nn.Linear(hid_dim * 2, n_classes)

    def forward(self, x):
        emb = self.emb(x)                       # (B, L, emb_dim)
        _, (h, _) = self.lstm(emb)              # h: (2, B, hid_dim)
        h = torch.cat([h[-2], h[-1]], dim=1)    # 拼接前向末态、后向末态
        return self.fc(h)                       # (B, n_classes)


class TransformerClassifier(nn.Module):
    """Transformer Encoder + mean pooling。

    必须加位置编码，否则 Self-Attention 对顺序无感知。
    """

    def __init__(self, vocab_size, emb_dim=EMB_DIM, n_heads=N_HEADS,
                 n_layers=N_LAYERS, ff_dim=FF_DIM, n_classes=N_CLASSES,
                 pad_idx=PAD_IDX, max_len=MAX_LEN):
        super().__init__()
        self.emb = nn.Embedding(vocab_size, emb_dim, padding_idx=pad_idx)
        self.pos = PositionalEncoding(emb_dim, max_len)
        layer = nn.TransformerEncoderLayer(
            d_model=emb_dim, nhead=n_heads, dim_feedforward=ff_dim,
            batch_first=True, dropout=0.1
        )
        self.encoder = nn.TransformerEncoder(layer, n_layers)
        self.fc = nn.Linear(emb_dim, n_classes)

    def forward(self, x):
        x = self.pos(self.emb(x))               # (B, L, emb_dim)
        x = self.encoder(x)                     # (B, L, emb_dim)
        return self.fc(x.mean(dim=1))           # mean pooling → (B, n_classes)


# -------------------------------------------------------------------
# 6. 训练 / 评估
# -------------------------------------------------------------------
def count_parameters(model):
    """统计可训练参数总量。"""
    return sum(p.numel() for p in model.parameters() if p.requires_grad)


def train_one_epoch(model, loader, opt, loss_fn, device):
    model.train()
    total_loss, total = 0.0, 0
    for text, label in loader:
        text, label = text.to(device), label.to(device)
        opt.zero_grad()
        logits = model(text)
        loss = loss_fn(logits, label)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)   # 梯度裁剪
        opt.step()
        total_loss += loss.item() * label.size(0)
        total += label.size(0)
    return total_loss / total


@torch.no_grad()
def evaluate(model, loader, device):
    model.eval()
    correct, total = 0, 0
    for text, label in loader:
        text, label = text.to(device), label.to(device)
        preds = model(text).argmax(dim=1)
        correct += (preds == label).sum().item()
        total += label.size(0)
    return correct / total


def run_training(name, model, train_loader, test_loader, device, epochs=EPOCHS):
    print(f"\n=== 训练 {name} ===")
    opt = torch.optim.Adam(model.parameters(), lr=LR)
    loss_fn = nn.CrossEntropyLoss()
    losses, accs = [], []   # 记录曲线，用于画图
    for epoch in range(1, epochs + 1):
        loss = train_one_epoch(model, train_loader, opt, loss_fn, device)
        acc = evaluate(model, test_loader, device)
        losses.append(loss)
        accs.append(acc)
        print(f"Epoch {epoch}/{epochs}  loss={loss:.3f}  test_acc={acc:.3f}")
    final_acc = evaluate(model, test_loader, device)
    print(f"{name} 最终测试准确率: {final_acc*100:.1f}%")
    _save_curve(name, losses, accs)
    return final_acc


def _save_curve(name, losses, accs):
    """把训练曲线保存成 PNG。matplotlib 没装就跳过，不影响主流程。"""
    try:
        import matplotlib
        matplotlib.use("Agg")   # 无界面后端
        import matplotlib.pyplot as plt
        import os
        os.makedirs("results", exist_ok=True)
        epochs = range(1, len(losses) + 1)
        fig, ax = plt.subplots(1, 2, figsize=(10, 4))
        ax[0].plot(epochs, losses, "o-")
        ax[0].set_title(f"{name} loss")
        ax[0].set_xlabel("epoch")
        ax[1].plot(epochs, accs, "s-")
        ax[1].set_title(f"{name} test accuracy")
        ax[1].set_xlabel("epoch")
        path = f"results/{name.lower()}_curve.png"
        plt.tight_layout()
        plt.savefig(path)
        print(f"  曲线已保存: {path}")
    except ImportError:
        print("  [提示] 未安装 matplotlib，跳过曲线保存。pip install matplotlib 后可生成 PNG。")
    except Exception as e:
        print(f"  [提示] 曲线保存失败：{e}")


# -------------------------------------------------------------------
# 7. 主流程
# -------------------------------------------------------------------
def main():
    # ---- 数据 ----
    print("=== 数据加载 ===")
    real = load_imdb()
    if real is None:
        train_texts, train_labels, test_texts, test_labels = load_mock_data()
    else:
        train_texts, train_labels, test_texts, test_labels, _ = real

    # ---- 词表 ----
    vocab = build_vocab(train_texts)
    print(f"词表大小: {len(vocab)}")

    # ---- DataLoader ----
    train_ds = TextDataset(train_texts, train_labels, vocab)
    test_ds = TextDataset(test_texts, test_labels, vocab)
    train_loader = DataLoader(train_ds, batch_size=BATCH_SIZE, shuffle=True,
                              collate_fn=collate_fn)
    test_loader = DataLoader(test_ds, batch_size=BATCH_SIZE, shuffle=False,
                             collate_fn=collate_fn)

    # ---- 参数量对比 ----
    print("\n=== 参数量对比 ===")
    bilstm = BiLSTMClassifier(len(vocab)).to(DEVICE)
    transformer = TransformerClassifier(len(vocab)).to(DEVICE)
    print(f"BiLSTM        参数量: {count_parameters(bilstm):,}")
    print(f"Transformer   参数量: {count_parameters(transformer):,}")
    print(
        "  解读：BiLSTM = 4个门 × (输入100+隐藏256+1偏置) × 隐藏256 × 双向2 ≈ 73万；\n"
        "        Transformer 主干 = 2层(MHA 4×100×100 + FFN 100×256+256×100 + LN) ≈ 18万。\n"
        "        4=门数，2=双向，+1=偏置合并进矩阵的写法。"
    )

    # ---- 训练两个模型 ----
    bilstm_acc = run_training("BiLSTM", bilstm, train_loader, test_loader, DEVICE)
    tf_acc = run_training("Transformer", transformer, train_loader, test_loader, DEVICE)

    # ---- 汇总 ----
    print("\n=== 最终结果 ===")
    print(f"BiLSTM       测试准确率: {bilstm_acc*100:.1f}%")
    print(f"Transformer  测试准确率: {tf_acc*100:.1f}%")
    if bilstm_acc > 0.8 and tf_acc > 0.8:
        print("✅ 两个模型都达到 > 80% 的目标")
    else:
        print("⚠️  未达 80%，可增加 epoch 或检查数据。模拟数据下应能轻松超过。")

    print("\n[完成] BiLSTM 在小数据上归纳偏置更强，常优于 Transformer；")
    print("       Transformer 需要大数据预训练才能碾压，这正是下一章 HuggingFace 的主题。")


if __name__ == "__main__":
    main()
