"""
Ch02 · 微积分最小必要知识 — 配套代码

覆盖：
  - 数值导数（中心差分）验证解析导数
  - 偏导数的数值验证
  - 链式法则的数值验证
  - 梯度方向可视化（文字版）
  - 梯度下降的小演示

运行方式：
    python ch02_calculus_basics.py
预期输出见每个 print 上方的注释。
"""

import numpy as np


def numerical_deriv(f, x, h=1e-5):
    """数值导数（中心差分）：f'(x) ≈ [f(x+h) - f(x-h)] / (2h)

    中心差分比前向差分精度更高，误差是 O(h²) 而不是 O(h)。
    """
    return (f(x + h) - f(x - h)) / (2 * h)


def numerical_partial(f, x, y, h=1e-5, var="x"):
    """数值偏导数：对 x 或 y 求偏导。"""
    if var == "x":
        return (f(x + h, y) - f(x - h, y)) / (2 * h)
    else:
        return (f(x, y + h) - f(x, y - h)) / (2 * h)


def main() -> None:
    # ---------------------------------------------------------------
    # 1. 导数：f(x) = x²，f'(x) = 2x
    #    在 x=3 处，解析导数 = 6
    # ---------------------------------------------------------------
    print("=== 导数验证：f(x) = x² ===")
    f = lambda x: x ** 2
    x0 = 3.0
    analytic = 2 * x0          # 解析解：6.0
    numeric = numerical_deriv(f, x0)
    print(f"  x = {x0}")
    print(f"  解析导数 f'({x0}) = {analytic}")
    print(f"  数值导数         = {numeric:.6f}")
    print(f"  误差             = {abs(analytic - numeric):.2e}")

    # ---------------------------------------------------------------
    # 2. 链式法则：y = (2x+1)²
    #    令 u = 2x+1，y = u²
    #    dy/dx = dy/du * du/dx = 2u * 2 = 4(2x+1)
    #    在 x=1 处，u=3，dy/dx = 4*3 = 12
    # ---------------------------------------------------------------
    print("\n=== 链式法则验证：y = (2x+1)² ===")
    y = lambda x: (2 * x + 1) ** 2
    x0 = 1.0
    u0 = 2 * x0 + 1            # u = 3
    analytic = 4 * (2 * x0 + 1)  # 12.0
    numeric = numerical_deriv(y, x0)
    print(f"  x = {x0}, u = 2x+1 = {u0}")
    print(f"  解析解 dy/dx = 4*(2x+1) = {analytic}")
    print(f"  数值解       = {numeric:.6f}")
    print(f"  误差         = {abs(analytic - numeric):.2e}")

    # ---------------------------------------------------------------
    # 3. 偏导数：f(x, y) = x² * y
    #    ∂f/∂x = 2xy，∂f/∂y = x²
    #    在 (x=2, y=3) 处：∂f/∂x = 12，∂f/∂y = 4
    # ---------------------------------------------------------------
    print("\n=== 偏导数验证：f(x, y) = x² * y ===")
    g = lambda x, y: (x ** 2) * y
    x0, y0 = 2.0, 3.0
    analytic_dx = 2 * x0 * y0    # 12.0
    analytic_dy = x0 ** 2        # 4.0
    numeric_dx = numerical_partial(g, x0, y0, var="x")
    numeric_dy = numerical_partial(g, x0, y0, var="y")
    print(f"  (x, y) = ({x0}, {y0})")
    print(f"  解析 ∂f/∂x = 2xy = {analytic_dx}, 数值 = {numeric_dx:.6f}")
    print(f"  解析 ∂f/∂y = x²  = {analytic_dy}, 数值 = {numeric_dy:.6f}")

    # ---------------------------------------------------------------
    # 4. 梯度：所有偏导数组成的向量
    #    梯度指向函数上升最快方向，负梯度是下降最快方向
    # ---------------------------------------------------------------
    print("\n=== 梯度方向演示：f(x, y) = x² + y² ===")
    # 这是一个碗，最低点在 (0, 0)
    bowl = lambda x, y: x ** 2 + y ** 2
    x0, y0 = 3.0, 4.0
    grad_x = numerical_partial(bowl, x0, y0, var="x")  # ≈ 6
    grad_y = numerical_partial(bowl, x0, y0, var="y")  # ≈ 8
    print(f"  起点 (x, y) = ({x0}, {y0})")
    print(f"  梯度 ∇f = ({grad_x:.4f}, {grad_y:.4f})")
    print(f"  负梯度 = ({-grad_x:.4f}, {-grad_y:.4f})  ← 这就是下降最快方向")

    # ---------------------------------------------------------------
    # 5. 梯度下降小演示：从 (3, 4) 走到 (0, 0) 附近
    # ---------------------------------------------------------------
    print("\n=== 梯度下降 5 步 ===")
    x, y = 3.0, 4.0
    lr = 0.1   # 学习率
    for step in range(5):
        gx = numerical_partial(bowl, x, y, var="x")
        gy = numerical_partial(bowl, x, y, var="y")
        x = x - lr * gx   # 沿负梯度走
        y = y - lr * gy
        val = bowl(x, y)
        print(f"  step {step+1}: (x, y) = ({x:.4f}, {y:.4f}), f = {val:.4f}")
    print("  → 5 步后已经从 f=25 降到了接近 0 的地方")

    # ---------------------------------------------------------------
    # 6. 验证"负梯度是下降最快方向"
    #    比较：沿负梯度走 0.1 vs 沿其他方向走 0.1
    # ---------------------------------------------------------------
    print("\n=== 验证：负梯度是下降最快方向 ===")
    x0, y0 = 3.0, 4.0
    f0 = bowl(x0, y0)         # 25
    gx = numerical_partial(bowl, x0, y0, var="x")  # 6
    gy = numerical_partial(bowl, x0, y0, var="y")  # 8
    step = 0.1

    # 方向1：负梯度方向 (-6, -8) / |(-6,-8)| = (-0.6, -0.8)
    dx1, dy1 = -gx / 10, -gy / 10
    f1 = bowl(x0 + step * dx1, y0 + step * dy1)

    # 方向2：随便一个方向，比如 (-1, 0) / 1
    dx2, dy2 = -1.0, 0.0
    f2 = bowl(x0 + step * dx2, y0 + step * dy2)

    # 方向3：随便一个方向，比如 (0, -1) / 1
    dx3, dy3 = 0.0, -1.0
    f3 = bowl(x0 + step * dx3, y0 + step * dy3)

    print(f"  起点 f(3, 4) = {f0}")
    print(f"  沿负梯度走 0.1 步: f = {f1:.4f}  (下降 {f0 - f1:.4f})")
    print(f"  沿 (-1, 0) 走 0.1 步: f = {f2:.4f}  (下降 {f0 - f2:.4f})")
    print(f"  沿 (0, -1) 走 0.1 步: f = {f3:.4f}  (下降 {f0 - f3:.4f})")
    print("  → 负梯度方向下降最多，这就是梯度下降的数学基础")


if __name__ == "__main__":
    main()
