"""
Ch10 · 第一个完整 ML 项目 —— Titanic 生还预测
特点：
1. 内置模拟数据生成（无需下载外部 CSV 文件）
2. 完整流程：数据清洗 → 特征工程 → 训练 → 评估
3. 包含混淆矩阵、F1 分数、分类报告
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.metrics import (
    confusion_matrix, classification_report,
    f1_score, accuracy_score
)


def make_titanic_data(n_samples=891, seed=42):
    """
    生成模拟的 Titanic 风格数据集。
    无需下载外部文件，基于统计规律模拟真实分布。
    """
    rng = np.random.RandomState(seed)

    # 舱位等级: 1/2/3 等比例约 16%/24%/60%
    Pclass = rng.choice([1, 2, 3], size=n_samples, p=[0.16, 0.24, 0.60])

    # 性别: 约 65% male, 35% female
    Sex = rng.choice(["male", "female"], size=n_samples, p=[0.65, 0.35])

    # 年龄: 正态分布，均值30，标准差14，范围0.5~80
    Age = np.clip(rng.normal(30, 14, size=n_samples), 0.5, 80).astype(float)

    # 兄弟配偶数 SibSp: 大部分是0或1
    SibSp = rng.choice([0, 0, 0, 1, 1, 2, 3, 4, 5], size=n_samples)

    # 父母子女数 Parch: 大部分是0
    Parch = rng.choice([0, 0, 0, 0, 1, 1, 2, 3], size=n_samples)

    # 票价 Fare: 与舱位相关
    base_fare = {1: 80, 2: 25, 3: 8}
    Fare = np.array([base_fare[p] for p in Pclass]) + rng.exponential(10, n_samples)
    Fare = np.clip(Fare, 3, 512)

    # ===== 根据规则生成标签（Survived）=====
    # 规则基于真实 Titanic 统计规律
    logit = (
        -1.5                                      # 基础偏置（整体死亡率高）
        + (1 == Pclass) * 1.8                     # 一等舱优势大
        + (2 == Pclass) * 0.9                     # 二等舱中等
        + (Sex == "female") * 2.5                 # 女性生存率高很多
        + (Age < 12) * 1.0                        # 儿童优先
        + (Age < 5) * 0.5                         # 幼童额外加成
        - (Age > 60) * 1.2                        # 老人劣势
        - (SibSp >= 4) * 1.0                      # 大家庭劣势
        + rng.normal(0, 1.2, n_samples)           # 随机噪声
    )
    prob = 1 / (1 + np.exp(-logit))               # sigmoid
    Survived = (rng.random(n_samples) < prob).astype(int)

    # 引入一些缺失值（模拟真实数据）
    mask_age = rng.random(n_samples) < 0.20       # ~20% 年龄缺失
    Age[mask_age] = np.nan

    df = pd.DataFrame({
        "PassengerId": range(1, n_samples + 1),
        "Pclass": Pclass,
        "Sex": Sex,
        "Age": Age,
        "SibSp": SibSp,
        "Parch": Parch,
        "Fare": Fare.round(2),
        "Survived": Survived,
    })

    return df


def main():
    print("=" * 70)
    print("=== 第一个完整 ML 项目 —— Titanic 生还预测 ===")
    print("=" * 70)

    # ========== 1. 加载数据 ==========
    df = make_titanic_data()

    print(f"\n【1. 数据概览】")
    print(f"总样本数: {len(df)}")
    print(f"特征: {list(df.columns[:-1])}")
    print(f"标签: Survived (生还率: {df['Survived'].mean()*100:.1f}%)")
    print(f"\n缺失值统计:")
    print(df.isnull().sum()[df.isnull().sum() > 0])

    # 显示前几行
    print(f"\n原始数据预览:")
    print(df.head(3).to_string())

    # ========== 2. 数据清洗 ==========
    print(f"\n{'='*70}")
    print("【2. 数据清洗】")

    age_median = df["Age"].median()
    n_missing_age = df["Age"].isnull().sum()
    df["Age"] = df["Age"].fillna(age_median)

    print(f"  Age 缺失: {n_missing_age} 个 → 用中位数 {age_median:.1f} 填充")

    # 性别编码
    df["Sex"] = df["Sex"].map({"male": 0, "female": 1})
    print(f"  性别编码: male→0, female→1")

    # ========== 3. 特征工程 ==========
    print(f"\n{'='*70}")
    print("【3. 特征工程】")

    features = ["Pclass", "Sex", "Age", "Fare"]
    X = df[features].fillna(0)
    y = df["Survived"]

    print(f"  使用特征: {features}")
    print(f"  特征矩阵 shape: {X.shape}")

    # ========== 4. 划分数据集 ==========
    print(f"\n{'='*70}")
    print("【4. 划分数据集】")

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    print(f"  训练集: {len(X_train)} 样本 ({len(X_train)/len(X)*100:.0f}%)")
    print(f"  测试集: {len(X_test)} 样本 ({len(X_test)/len(X)*100:.0f}%)")

    # ========== 5. 模型训练 ==========
    print(f"\n{'='*70}")
    print("【5. 模型训练】")

    # 用随机森林（效果通常比逻辑回归好）
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=5,
        min_samples_split=10,
        random_state=42
    )

    model.fit(X_train, y_train)
    print(f"  模型: RandomForestClassifier(n_estimators=100, max_depth=5)")

    # 特征重要性
    print(f"\n  特征重要性:")
    for name, imp in zip(features, model.feature_importances_):
        print(f"    {name:>8s}: {imp:.4f}")

    # ========== 6. 交叉验证 ==========
    print(f"\n{'='*70}")
    print("【6. 交叉验证】(5折)")

    cv_scores = cross_val_score(model, X, y, cv=5)
    print(f"  各折准确率: {[f'{s:.4f}' for s in cv_scores]}")
    print(f"  CV accuracy: {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")

    # ========== 7. 测试集评估 ==========
    print(f"\n{'='*70}")
    print("【7. 测试集详细评估】")

    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)

    print(f"\n  Accuracy: {acc:.4f}")
    print(f"  F1 Score: {f1:.4f}")

    # 混淆矩阵
    cm = confusion_matrix(y_test, y_pred)
    print(f"\n  混淆矩阵:")
    print(f"               预测: 死亡(0)  生还(1)")
    print(f"  实际: 死亡(0)   {cm[0][0]:>6d}     {cm[0][1]:>6d}")
    print(f"        生还(1)   {cm[1][0]:>6d}     {cm[1][1]:>6d}")

    tn, fp, fn, tp = cm.ravel()
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    print(f"\n  TP={tp}, FP={fp}, FN={fn}, TN={tn}")
    print(f"  Precision(精确率): {precision:.4f}  (预测为生还的人中，真正生的比例)")
    print(f"  Recall(召回率):    {recall:.4f}  (真正生还的人中，被找出的比例)")

    # 分类报告
    print(f"\n  分类报告:")
    print(classification_report(y_test, y_pred, target_names=["死亡(0)", "生还(1)"]))

    # ========== 8. 与逻辑回归对比 ==========
    print(f"\n{'='*70}")
    print("【8. 对比: 逻辑回归 vs 随机森林】")

    lr_model = LogisticRegression(max_iter=1000, random_state=42)
    lr_model.fit(X_train, y_train)
    lr_cv = cross_val_score(lr_model, X, y, cv=5)

    print(f"  逻辑回归 CV accuracy: {lr_cv.mean():.4f} ± {lr_cv.std():.4f}")
    print(f"  随机森林 CV accuracy: {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")

    # ========== 9. 预测示例 ==========
    print(f"\n{'='*70}")
    print("【9. 预测示例】")

    examples = pd.DataFrame({
        "Pclass": [3, 1, 2],
        "Sex": [0, 1, 0],
        "Age": [25.0, 35.0, 50.0],
        "Fare": [7.25, 100.0, 25.0],
    })

    pred_probs = model.predict_proba(examples)
    preds = model.predict(examples)

    sex_map = {0: "男", 1: "女"}
    class_map = {0: "死亡", 1: "生还"}

    print(f"  {'Pclass':>6s} | {'性别':>4s} | {'年龄':>5s} | {'票价':>6s} | "
          f"{'概率':>6s} | {'预测':>6s}")
    print("  " + "-" * 55)
    for i in range(len(examples)):
        pcls = int(examples.iloc[i]["Pclass"])
        sex = sex_map[int(examples.iloc[i]["Sex"])]
        age = examples.iloc[i]["Age"]
        fare = examples.iloc[i]["Fare"]
        prob = pred_probs[i][1]
        pred = class_map[preds[i]]
        print(f"  {pcls:>6d} | {sex:>4s} | {age:>5.1f} | {fare:>6.2f} | "
              f"{prob:>5.1%} | {pred:>6s}")


if __name__ == "__main__":
    main()
