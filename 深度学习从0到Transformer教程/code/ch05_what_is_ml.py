"""
Ch05 · 什么是机器学习 —— 最简示例
用 sklearn 的 LinearRegression 展示 ML 的核心流程：
数据 → fit(学习) → predict(预测)
"""

from sklearn.linear_model import LinearRegression
import numpy as np


def main():
    print("=" * 50)
    print("=== 什么是机器学习 ===")
    print("=" * 50)

    # ========== 1. 准备数据 ==========
    # 特征 X：房子的面积（单位：㎡）
    # 形状 (n_samples, n_features)，这里 n_features=1（只有面积一个特征）
    X = np.array([[50], [80], [120]])
    # 标签 y：对应的房价（单位：万）
    y = np.array([60, 100, 150])

    print("\n【数据】")
    print(f"X (面积/㎡):\n{X}")
    print(f"y (房价/万): {y}")

    # ========== 2. 创建并训练模型 ==========
    # LinearRegression 会自动寻找最优的 w 和 b
    # 使得 ŷ = w * X + b 尽可能接近真实的 y
    model = LinearRegression()
    model.fit(X, y)  # fit = "从数据中学习"

    # ========== 3. 查看学到的参数 ==========
    w = model.coef_[0]      # 权重（斜率）：每平米的单价
    b = model.intercept_    # 偏置（截距）：基础价格

    print("\n【训练结果】")
    print(f"学到的系数 w: {w:.4f}  (每平米价值)")
    print(f"学到的截距 b: {b:.4f}  (基础价格)")

    # ========== 4. 用模型做预测 ==========
    new_x = np.array([[90]])  # 90㎡ 的新房子
    prediction = model.predict(new_x)

    print(f"\n【预测】")
    print(f"90㎡ 预测房价: {prediction[0][0]:.1f} 万")

    # ========== 5. 手动验证 ==========
    manual_pred = w * 90 + b
    print(f"手动计算(w×90+b): {manual_pred:.1f} 万")

    # ========== 6. 解读 ==========
    print("\n【解读】")
    print(f"模型学到的公式: 房价 ≈ {w:.3f} × 面积 + {b:.2f}")
    print(f"即每平米约值 {w:.3f} 万")
    print(f"\n这就是机器学习：我们没有写 'w=1.125' 这个规则，")
    print(f"模型自己从 [(50,60), (80,100), (120,150)] 这三组数据中发现了规律！")


if __name__ == "__main__":
    main()
