"""
Ch09 · 过拟合与正则化 —— 演示
1. 展示三种状态：欠拟合/刚好/过拟合（通过多项式次数控制）
2. L1/L2 正则化的数值对比
3. Ridge 和 Lasso 在 sklearn 中的使用
"""

import numpy as np
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.preprocessing import PolynomialFeatures
from sklearn.model_selection import train_test_split


def main():
    print("=" * 65)
    print("=== 过拟合与正则化 ===")
    print("=" * 65)

    # ========== 1. 生成数据 ==========
    np.random.seed(42)
    n_samples = 50
    X = np.random.randn(n_samples, 1) * 2
    # 真实关系: y = 3x + noise
    true_w = 3.0
    noise_std = 1.5
    y = true_w * X.flatten() + np.random.randn(n_samples) * noise_std

    # 划分训练集和测试集
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=42
    )

    print(f"\n【数据】{n_samples} 个样本, 1 个特征")
    print(f"真实关系: y = {true_w}x + N(0, {noise_std}²)")
    print(f"训练集: {len(X_train)} 样本, 测试集: {len(X_test)} 样本")

    # ========== 2. 无正则化 baseline ==========
    print(f"\n{'='*65}")
    print("【Baseline: 无正则化的线性回归】")
    model_base = LinearRegression().fit(X_train, y_train)
    r2_train = model_base.score(X_train, y_train)
    r2_test = model_base.score(X_test, y_test)
    print(f"训练集 R²: {r2_train:.4f}")
    print(f"测试集 R²: {r2_test:.4f}")
    print(f"学到的权重: w={model_base.coef_[0]:.4f}, b={model_base.intercept_:.4f}")

    # ========== 3. L2 正则化 (Ridge) ==========
    print(f"\n{'='*65}")
    print("【L2 正则化 (Ridge) — 不同 alpha 对比】")
    alphas = [0.001, 0.01, 0.1, 1.0, 10.0]
    print(f"{'alpha':>8s} | {'train R²':>9s} | {'test R²':>8s} | {'weight':>10s}")
    print("-" * 48)
    for alpha in alphas:
        model = Ridge(alpha=alpha).fit(X_train, y_train)
        r2_tr = model.score(X_train, y_train)
        r2_te = model.score(X_test, y_test)
        print(f"{alpha:8.3f} | {r2_tr:9.4f} | {r2_te:8.4f} | {model.coef_[0]:10.4f}")

    # ========== 4. L1 正则化 (Lasso) ==========
    print(f"\n{'='*65}")
    print("【L1 正则化 (Lasso) — 不同 alpha 对比】")
    print(f"{'alpha':>8s} | {'train R²':>9s} | {'test R²':>8s} | {'weight':>10s} | {'非零权重数'}")
    print("-" * 62)
    for alpha in alphas:
        model = Lasso(alpha=alpha, max_iter=10000).fit(X_train, y_train)
        r2_tr = model.score(X_train, y_train)
        r2_te = model.score(X_test, y_test)
        n_nonzero = np.sum(model.coef_ != 0)
        print(f"{alpha:8.3f} | {r2_tr:9.4f} | {r2_te:8.4f} | "
              f"{model.coef_[0]:10.4f} | {n_nonzero}")

    # ========== 5. 过拟合演示: 多项式拟合 ==========
    print(f"\n{'='*65}")
    print("【过拟合演示: 不同多项式次数】")
    print(f"{'degree':>6s} | {'train R²':>9s} | {'test R²':>8s} | {'状态'}")
    print("-" * 52)

    degrees = [1, 2, 4, 8, 12]
    for deg in degrees:
        poly = PolynomialFeatures(degree=deg, include_bias=False)
        X_train_poly = poly.fit_transform(X_train)
        X_test_poly = poly.transform(X_test)

        model = LinearRegression().fit(X_train_poly, y_train)
        r2_tr = model.score(X_train_poly, y_train)
        r2_te = model.score(X_test_poly, y_test)

        gap = r2_tr - r2_te
        if gap > 0.15:
            status = "❌ 过拟合"
        elif r2_tr < 0.7:
            status = "⚠️ 欠拟合"
        else:
            status = "✅ 刚好"

        print(f"{deg:6d} | {r2_tr:9.4f} | {r2_te:8.4f} | {status}")

    # ========== 6. L2 正则化数值手算展示 ==========
    print(f"\n{'='*65}")
    print("【L2 正则化数值手算展示】")
    w_example = np.array([3.0, -2.0, 1.0])
    l_data = 10.0
    lam = 0.1

    l2_term = lam * np.sum(w_example ** 2)
    l1_term = lam * np.sum(np.abs(w_example))

    print(f"原始损失 L_data = {l_data}")
    print(f"权重 w = {w_example}")
    print(f"λ = {lam}")
    print()
    print(f"L2 正则项 = λ × Σw² = {lam} × ({w_example[0]}²+{w_example[1]}²+{w_example[2]}²)")
    print(f"          = {lam} × ({w_example[0]**2:.1f}+{w_example[1]**2:.1f}+{w_example[2]**2:.1f})")
    print(f"          = {lam} × {np.sum(w_example**2):.1f} = {l2_term:.4f}")
    print(f"L2 总损失 = {l_data} + {l2_term:.4f} = {l_data + l2_term:.4f}")
    print()
    print(f"L1 正则项 = λ × Σ|w| = {lam} × ({abs(w_example[0])}+{abs(w_example[1])}+{abs(w_example[2])})")
    print(f"          = {lam} × {np.sum(np.abs(w_example)):.1f} = {l1_term:.4f}")
    print(f"L1 总损失 = {l_data} + {l1_term:.4f} = {l_data + l1_term:.4f}")


if __name__ == "__main__":
    main()
