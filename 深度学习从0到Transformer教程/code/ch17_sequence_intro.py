"""
Ch17: 为什么需要 RNN — 序列数据的挑战
演示：(1) MLP 处理变长序列的困境 (2) MLP 无法区分上下文 (3) 序列数据类型一览
"""
import numpy as np


def mlp_predict(x, W, b):
    """
    最简 MLP：y = W·x + b
    用于演示 MLP 对序列的局限
    """
    return W @ x + b


def demo_variable_length():
    """演示变长序列问题"""
    print("--- 变长问题 ---")
    sentence1 = [1, 2, 3]           # 3 个词
    sentence2 = [1, 2, 3, 4, 5]     # 5 个词

    mlp_input_dim = 3

    if len(sentence1) == mlp_input_dim:
        print(f"句子1 长度 {len(sentence1)}，匹配 MLP 输入维度 {mlp_input_dim}: OK")
    if len(sentence2) > mlp_input_dim:
        print(f"句子2 长度 {len(sentence2)}，超出 MLP 输入维度 {mlp_input_dim}: 需要补零或截断")


def demo_context_blindness():
    """演示 MLP 无法区分上下文不同的同一个词"""
    print("\n--- 上下文问题 ---")

    # "爱" 这个词用 1 维数字 0.5 表示
    W = np.array([[1.0]])  # 1维 -> 1维
    b = np.array([0.0])

    # 两个"爱"的输入完全一样
    ai_in_context1 = np.array([0.5])  # "我 爱 ___" 上下文
    ai_in_context2 = np.array([0.5])  # "也 爱 ___" 上下文

    pred1 = mlp_predict(ai_in_context1, W, b)
    pred2 = mlp_predict(ai_in_context2, W, b)

    print(f"两个'爱'的输入都是: {ai_in_context1}")
    print(f"MLP 对'我 爱 ___'中'爱'的预测: {pred1}")
    print(f"MLP 对'也 爱 ___'中'爱'的预测: {pred2}")
    print(f"两次预测完全一样: {np.array_equal(pred1, pred2)}")
    print("→ MLP 无法区分上下文不同的同一个词")


def demo_sequence_types():
    """展示序列数据的四种典型形态"""
    print("\n--- 序列数据类型一览 ---")
    examples = [
        ("文本", ['我', '爱', '编程'], "有序、变长"),
        ("语音", ['帧1', '帧2', '...', '帧100'], "有序、定长/变长"),
        ("股价", [100.5, 101.2, 99.8, 102.0], "有序、变长"),
        ("视频", ['图1', '图2', '...', '图30'], "有序、定长"),
    ]
    for name, data, feature in examples:
        print(f"{name}: {data}  {feature}")


def demo_window_mlp_limitation():
    """演示滑动窗口 MLP 的局限"""
    print("\n--- 滑动窗口 MLP 的局限 ---")

    # 一个长句子
    sentence = ['我', '出生', '在', '法国', '，', '后来', '搬', '到', '美国',
                '，', '学了', '英语', '和', '德语', '，', '现在', '说', '法语']
    print(f"句子: {' '.join(sentence)}")
    print(f"句子长度: {len(sentence)} 个词")

    # 窗口大小为 3 的 MLP
    window = 3
    print(f"\n滑动窗口 MLP，窗口大小 = {window}")

    # 要预测最后一个词"法语"，但关键信息"法国"在第 3 个位置
    target_pos = len(sentence) - 1  # "法语" 在最后
    key_info_pos = 3                # "法国" 在第3位
    distance = target_pos - key_info_pos

    print(f"关键信息 '{sentence[key_info_pos]}' 在第 {key_info_pos} 位")
    print(f"目标词 '{sentence[target_pos]}' 在第 {target_pos} 位")
    print(f"两者距离: {distance} 个词")

    if distance > window:
        print(f"→ 距离 {distance} > 窗口 {window}，窗口 MLP 看不到'法国'，无法预测'法语'")
        print("→ 这就是 RNN 要解决的问题：用隐藏状态当记忆，理论上能记住任意长的上下文")


def main():
    print("=" * 60)
    print("=== Ch17: 序列数据的挑战 ===")
    print("=" * 60)

    demo_variable_length()
    demo_context_blindness()
    demo_sequence_types()
    demo_window_mlp_limitation()

    print("\n" + "=" * 60)
    print("结论：MLP 处理序列有两大缺陷：")
    print("  1. 固定输入维度，无法处理变长序列")
    print("  2. 无记忆机制，无法利用上下文区分相同输入")
    print("→ 需要 RNN 这种有记忆的模型，见 Ch18")
    print("=" * 60)


if __name__ == "__main__":
    main()
    print("\n" + "=" * 60)
