"""
Ch40 · 实战二：用 HuggingFace 玩转预训练模型
=============================================
- 三个 pipeline：情感分类、抽取式问答、文本生成
- 微调 BERT 骨架（Trainer API）
- 国内镜像加速：HF_ENDPOINT=https://hf-mirror.com
- 全程 try-except 处理网络/依赖问题，没装 transformers 也能跑（打印提示）

运行：
    cd 深度学习从0到Transformer教程/code
    python ch40_huggingface.py

依赖：
    pip install transformers torch
    （可选）pip install datasets accelerate  # 微调部分需要
"""
import os

# 国内镜像：必须在 import transformers 之前设置环境变量
os.environ.setdefault("HF_ENDPOINT", "https://hf-mirror.com")

# -------------------------------------------------------------------
# 0. 检查 transformers + torch 是否安装（transformers 依赖 torch，同装同缺）
# -------------------------------------------------------------------
try:
    import torch
    from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
    HAS_TRANSFORMERS = True
    print("[环境] transformers 已安装，开始实战。")
    print(f"[环境] HF_ENDPOINT = {os.environ.get('HF_ENDPOINT')}")
except ImportError as e:
    HAS_TRANSFORMERS = False
    torch = None   # 后续逻辑都在 HAS_TRANSFORMERS 守卫下，不会真正用到
    print(f"[环境] 依赖未安装：{e}")
    print("[环境] 请先执行：pip install transformers torch")
    print("[环境] 下面只打印代码骨架，不实际运行。")


# -------------------------------------------------------------------
# 1. 情感分类 pipeline
# -------------------------------------------------------------------
def demo_sentiment():
    print("\n=== 1. 情感分类 pipeline ===")
    if not HAS_TRANSFORMERS:
        print("classifier = pipeline('sentiment-analysis')")
        print("classifier('I love deep learning!')")
        print("# [{'label': 'POSITIVE', 'score': 0.9998}]")
        return
    try:
        # 不指定 model，pipeline 会自动选默认的情感分类模型
        classifier = pipeline("sentiment-analysis")
        texts = [
            "I love deep learning!",
            "This movie is a total waste of time.",
            "The plot was predictable but the acting was brilliant.",
        ]
        for t in texts:
            print(f"  {t!r}  ->  {classifier(t)}")
    except Exception as e:
        print(f"  [跳过] 模型下载失败：{e}")
        print("  提示：确认网络可访问 hf-mirror.com，或手动下载模型后用 pipeline(..., model=本地路径)")


# -------------------------------------------------------------------
# 2. 抽取式问答 pipeline
# -------------------------------------------------------------------
def demo_qa():
    print("\n=== 2. 问答 pipeline ===")
    if not HAS_TRANSFORMERS:
        print("qa = pipeline('question-answering')")
        print("qa(question='...', context='...')")
        return
    try:
        qa = pipeline("question-answering")
        context = (
            "Transformer is a neural network architecture based on self-attention. "
            "It was proposed in 2017 by researchers at Google. "
            "Unlike RNN, Transformer processes all tokens in parallel."
        )
        questions = [
            "What is Transformer?",
            "When was Transformer proposed?",
            "How is Transformer different from RNN?",
        ]
        for q in questions:
            r = qa(question=q, context=context)
            print(f"  Q: {q}")
            print(f"  A: {r['answer']}  (score={r['score']:.3f})")
    except Exception as e:
        print(f"  [跳过] 模型下载失败：{e}")


# -------------------------------------------------------------------
# 3. 文本生成 pipeline
# -------------------------------------------------------------------
def demo_generation():
    print("\n=== 3. 文本生成 pipeline ===")
    if not HAS_TRANSFORMERS:
        print("generator = pipeline('text-generation', model='gpt2')")
        print("generator('Deep learning is', max_length=30)")
        return
    try:
        # gpt2 约 550MB，首次下载需耐心
        generator = pipeline("text-generation", model="gpt2")
        prompts = ["Deep learning is", "The future of AI is"]
        for p in prompts:
            out = generator(p, max_length=30, num_return_sequences=1,
                            pad_token_id=generator.tokenizer.eos_token_id)
            text = out[0]["generated_text"]
            print(f"  提示: {p!r}")
            print(f"  生成: {text}")
    except Exception as e:
        print(f"  [跳过] 模型下载失败：{e}")
        print("  提示：gpt2 较大，可换更小的 distilgpt2 试试。")


# -------------------------------------------------------------------
# 4. 微调 BERT 骨架（Trainer API）
# -------------------------------------------------------------------
def demo_finetune_bert():
    print("\n=== 4. 微调 BERT（演示骨架）===")
    if not HAS_TRANSFORMERS:
        print("from transformers import BertForSequenceClassification, Trainer, TrainingArguments")
        print("model = BertForSequenceClassification.from_pretrained('bert-base-chinese', num_labels=2)")
        print("trainer = Trainer(model=model, args=training_args, train_dataset=ds)")
        print("trainer.train()")
        return

    has_gpu = torch.cuda.is_available()
    print(f"  GPU 可用: {has_gpu}")

    try:
        from transformers import (
            BertForSequenceClassification,
            Trainer,
            TrainingArguments,
        )
    except ImportError:
        print("  [跳过] 微调需要 transformers 完整版，请 pip install transformers")
        return

    # --- 构建模型 ---
    try:
        model = BertForSequenceClassification.from_pretrained(
            "bert-base-chinese", num_labels=2
        )
        print("  BERT 模型加载成功")
    except Exception as e:
        print(f"  [跳过] BERT 下载失败：{e}")
        print("  下面是骨架代码，照着写即可：")
        print("""
        model = BertForSequenceClassification.from_pretrained("bert-base-chinese", num_labels=2)
        training_args = TrainingArguments(
            output_dir="./results",
            num_train_epochs=3,
            per_device_train_batch_size=16,
            learning_rate=2e-5,      # 微调必须小 lr！
            fp16=True,                # 显存不够就开
        )
        trainer = Trainer(model=model, args=training_args, train_dataset=train_ds)
        trainer.train()
        """)
        return

    # --- 训练参数 ---
    # 关键：微调 lr 必须小（2e-5），不能照搬从零训练的 1e-3
    training_args = TrainingArguments(
        output_dir="./results",
        num_train_epochs=1,                 # 演示只跑 1 个 epoch
        per_device_train_batch_size=8 if has_gpu else 4,
        learning_rate=2e-5,                 # BERT 微调经验值
        fp16=has_gpu,                       # GPU 才开混合精度
        save_strategy="no",                 # 演示不存 checkpoint
        logging_steps=5,
    )

    # --- 准备一个迷你数据集（演示用，真实任务用 datasets.load_dataset）---
    fake_dataset = _make_fake_dataset(model.config.name_or_path)

    if fake_dataset is None:
        print("  [跳过] Tokenizer 加载失败，无法构造数据集。骨架代码已展示。")
        return

    trainer = Trainer(model=model, args=training_args, train_dataset=fake_dataset)

    if not has_gpu:
        print("  未检测到 GPU，CPU 微调 BERT 非常慢（每 step 几秒）。")
        print("  这里只演示 2 个 step 验证流程能通，不完整训练。")
        print("  完整微调请用 GPU，或换更小的 distilbert-base-uncased。")
        # 跑 2 个 step 验证流程
        try:
            trainer.train()
        except Exception as e:
            print(f"  [跳过] 训练失败：{e}")
            print("  骨架代码正确，可能是显存/算力不足。在 GPU 机器上可正常跑。")
    else:
        print("  检测到 GPU，开始微调（1 epoch，演示用）...")
        trainer.train()
        print("  微调完成！模型保存在 ./results")


def _make_fake_dataset(model_name):
    """构造一个迷你数据集供微调流程验证。

    真实任务用 datasets.load_dataset("imdb") 替换。这里用几条样例
    验证 Trainer 流程能跑通即可。
    """
    try:
        from transformers import AutoTokenizer
        tokenizer = AutoTokenizer.from_pretrained(model_name)
    except Exception:
        return None

    texts = ["这部电影很好看", "太糟糕了浪费时间", "非常喜欢", "烂片别看",
             "剧情精彩", "无聊透顶", "演员演技棒", "垃圾电影"]
    labels = [1, 0, 1, 0, 1, 0, 1, 0]

    enc = tokenizer(texts, truncation=True, padding=True, max_length=32,
                    return_tensors="pt")

    class _DS(torch.utils.data.Dataset):
        def __init__(self, enc, labels):
            self.enc = enc
            self.labels = labels

        def __len__(self):
            return len(self.labels)

        def __getitem__(self, idx):
            return {
                "input_ids": self.enc["input_ids"][idx],
                "attention_mask": self.enc["attention_mask"][idx],
                "labels": torch.tensor(self.labels[idx], dtype=torch.long),
            }

    return _DS(enc, labels)


# -------------------------------------------------------------------
# 主流程
# -------------------------------------------------------------------
def main():
    print("=" * 60)
    print("Ch40 · 用 HuggingFace 玩转预训练模型")
    print("=" * 60)

    demo_sentiment()
    demo_qa()
    demo_generation()
    demo_finetune_bert()

    print("\n" + "=" * 60)
    print("[完成] 三个 pipeline + 微调骨架演示完毕。")
    print("关键记忆点：")
    print("  1. pipeline('任务名') 一行调用，封装 Tokenizer + Model")
    print("  2. 微调 lr 用 2e-5，不是从零训练的 1e-3")
    print("  3. 显存不足：batch 减半 → fp16 → 换小模型")
    print("  4. 国内加速：HF_ENDPOINT=https://hf-mirror.com")
    print("=" * 60)


if __name__ == "__main__":
    main()
