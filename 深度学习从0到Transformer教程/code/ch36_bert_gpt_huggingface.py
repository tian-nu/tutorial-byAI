"""
Ch36 · 从 Transformer 到 BERT / GPT
=====================================
- 用最小代码演示 BERT（MLM 完形填空）、GPT（CLM 接龙）、T5（text-to-text）三流派
- 用 HuggingFace transformers 一行调用真实模型
- 演示 scaling law 的直观对比（小模型 vs 大模型生成质量）

注意：
- 首次运行会从 HuggingFace Hub 下载模型（gpt2 ~500MB, bert-base-uncased ~440MB, t5-small ~240MB）
- 国内网络可设置环境变量用镜像：
    export HF_ENDPOINT=https://hf-mirror.com   (Linux/Mac)
    set HF_ENDPOINT=https://hf-mirror.com      (Windows PowerShell)
- 若未安装 transformers，先执行：pip install transformers torch

运行：
    cd 深度学习从0到Transformer教程/code
    python ch36_bert_gpt_huggingface.py
"""
import os
import sys


def check_transformers():
    """检查 transformers 是否安装，未安装则提示"""
    try:
        import transformers
        return True
    except ImportError:
        print("⚠️  未安装 transformers，请先执行：pip install transformers torch")
        print("   安装后重新运行本脚本")
        return False


def demo_minimal_transformer_variants():
    """用纯 PyTorch 演示三种架构的最小差异（不依赖 transformers）"""
    print("--- 三流派架构最小对比（纯 PyTorch）---")
    print()
    print("BERT (Encoder-only)：")
    print("  - 双向注意力，每个词看上下文所有词")
    print("  - 预训练任务：MLM（mask 15% 词，预测被 mask 的）")
    print("  - 比喻：完形填空专家")
    print()
    print("GPT (Decoder-only)：")
    print("  - 因果注意力，每个词只看自己和之前（上三角 -inf mask）")
    print("  - 预训练任务：CLM（预测下一个词）")
    print("  - 比喻：接龙游戏冠军")
    print()
    print("T5 (Encoder-Decoder)：")
    print("  - Encoder 双向，Decoder 因果，Cross-Attn 桥接")
    print("  - 预训练任务：Span Corruption（遮盖连续片段，生成被遮盖内容）")
    print("  - 比喻：全能翻译官")
    print()


def demo_gpt_generation():
    """GPT-2 文本生成（CLM）"""
    from transformers import pipeline

    print("--- GPT-2 生成（CLM 接龙）---")
    generator = pipeline("text-generation", model="gpt2")

    prompt = "The cat sat on the"
    print(f"输入: \"{prompt}\"")
    result = generator(prompt, max_length=25, num_return_sequences=1,
                       pad_token_id=50256)   # 消除 warning
    print(f"输出: \"{result[0]['generated_text']}\"")
    print()


def demo_bert_mlm():
    """BERT 完形填空（MLM）"""
    from transformers import pipeline

    print("--- BERT 完形填空（MLM）---")
    unmasker = pipeline("fill-mask", model="bert-base-uncased")

    text = "The cat sat on the [MASK]."
    print(f"输入: \"{text}\"")
    results = unmasker(text)
    for i, r in enumerate(results[:5]):
        print(f"  top {i+1}: {r['token_str']:10s} (score={r['score']:.4f})")
    print()


def demo_t5_translation():
    """T5 翻译（text-to-text）"""
    from transformers import pipeline

    print("--- T5 翻译（text-to-text）---")
    translator = pipeline("translation_en_to_fr", model="t5-small")

    text = "The cat sat on the mat."
    print(f"输入: \"{text}\"")
    result = translator(text)
    print(f"输出: \"{result[0]['translation_text']}\"")
    print()


def demo_scaling_intuition():
    """scaling law 直观说明"""
    print("--- Scaling Law 直观说明 ---")
    print("OpenAI 2020 提出的 scaling law: loss ∝ 1 / N^α")
    print("  N = 参数量, α ≈ 0.076")
    print()
    print("GPT 系列验证：")
    print("  GPT-2 Small :  117M 参数")
    print("  GPT-2 XL    : 1.5B 参数")
    print("  GPT-3       : 175B 参数")
    print("  GPT-4       : 参数量未公开（估计 > 1T）")
    print()
    print("关键观察：参数到百亿级，涌现出指令遵循、上下文学习、思维链推理")
    print("BERT 不能 scaling 的原因：MLM 信号稀疏（只 15% 位置算 loss），且双向注意力不擅生成\n")


def main():
    print("=== Ch36: 从 Transformer 到 BERT/GPT ===\n")

    # 第一部分：纯文字对比（不依赖 transformers，保证可运行）
    demo_minimal_transformer_variants()

    # 第二部分：HuggingFace 实操（需要 transformers）
    if check_transformers():
        try:
            demo_gpt_generation()
        except Exception as e:
            print(f"⚠️  GPT-2 演示失败: {e}")
            print("   可能原因：网络问题或模型下载失败\n")

        try:
            demo_bert_mlm()
        except Exception as e:
            print(f"⚠️  BERT 演示失败: {e}")
            print("   可能原因：网络问题或模型下载失败\n")

        try:
            demo_t5_translation()
        except Exception as e:
            print(f"⚠️  T5 演示失败: {e}")
            print("   可能原因：网络问题或模型下载失败\n")
    else:
        print("跳过 HuggingFace 实操（未安装 transformers）\n")

    # 第三部分：scaling law 说明
    demo_scaling_intuition()

    # 第四部分：三流派对比表
    print("--- 三流派对比表 ---")
    print(f"{'维度':<10} {'BERT':<20} {'GPT':<20} {'T5':<20}")
    print(f"{'-'*70}")
    print(f"{'架构':<10} {'Encoder-only':<20} {'Decoder-only':<20} {'Encoder-Decoder':<20}")
    print(f"{'注意力':<10} {'双向':<20} {'单向(因果)':<20} {'Enc双向,Dec单向':<20}")
    print(f"{'预训练':<10} {'MLM(完形填空)':<20} {'CLM(接龙)':<20} {'Span Corruption':<20}")
    print(f"{'擅长':<10} {'理解':<20} {'生成':<20} {'通用':<20}")
    print(f"{'代表':<10} {'BERT/RoBERTa':<20} {'GPT-2/3/4/LLaMA':<20} {'T5/BART':<20}")
    print()

    print("=== Ch36 完成 ===")


if __name__ == "__main__":
    main()
