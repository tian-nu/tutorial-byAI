"""
Ch01 · 线性代数最小必要知识 — 配套代码

覆盖：
  - 向量与矩阵的创建
  - 向量点积
  - 矩阵乘法（手写 + NumPy）
  - 维度规则验证
  - 转置与 Hadamard 积对比

运行方式：
    python ch01_linear_algebra_basics.py
预期输出见每个 print 上方的注释。
"""

import numpy as np


def main() -> None:
    # ---------------------------------------------------------------
    # 1. 向量（Vector）：一维数组
    # ---------------------------------------------------------------
    a = np.array([1.0, 2.0, 3.0])
    b = np.array([4.0, 5.0, 6.0])
    print("=== 向量 ===")
    print(f"a = {a}, shape = {a.shape}")   # (3,) 注意不是 (3,1)
    print(f"b = {b}, shape = {b.shape}")

    # ---------------------------------------------------------------
    # 2. 向量点积（Dot Product）：对应元素相乘再求和
    #    a·b = 1*4 + 2*5 + 3*6 = 4 + 10 + 18 = 32
    # ---------------------------------------------------------------
    dot_ab = np.dot(a, b)
    print("\n=== 点积 ===")
    print(f"np.dot(a, b) = {dot_ab}")      # 32.0
    # 也可以用 @ 运算符（Python 3.5+）
    print(f"a @ b = {a @ b}")              # 32.0

    # ---------------------------------------------------------------
    # 3. 矩阵（Matrix）：二维表格
    # ---------------------------------------------------------------
    A = np.array([[1, 2],
                  [3, 4]])
    B = np.array([[5, 6],
                  [7, 8]])
    print("\n=== 矩阵 ===")
    print(f"A =\n{A}\nshape = {A.shape}")  # (2, 2)
    print(f"B =\n{B}\nshape = {B.shape}")

    # ---------------------------------------------------------------
    # 4. 矩阵乘法（Matrix Multiplication）：行 × 列的点积
    #    C[i][j] = sum_k A[i][k] * B[k][j]
    #    C[0][0] = 1*5 + 2*7 = 19
    #    C[0][1] = 1*6 + 2*8 = 22
    #    C[1][0] = 3*5 + 4*7 = 43
    #    C[1][1] = 3*6 + 4*8 = 50
    # ---------------------------------------------------------------
    print("\n=== 矩阵乘法（NumPy @）===")
    C = A @ B
    print(f"A @ B =\n{C}")                 # [[19 22] [43 50]]

    # 手写版本，验证 NumPy 没有骗你
    def matmul_manual(X: np.ndarray, Y: np.ndarray) -> np.ndarray:
        rows, inner = X.shape
        inner2, cols = Y.shape
        assert inner == inner2, f"内维度不匹配: {inner} vs {inner2}"
        out = np.zeros((rows, cols), dtype=Y.dtype)
        for i in range(rows):
            for j in range(cols):
                total = 0
                for k in range(inner):
                    total += X[i][k] * Y[k][j]
                out[i][j] = total
        return out

    print("\n=== 矩阵乘法（手写三重循环）===")
    C_manual = matmul_manual(A, B)
    print(f"手写结果 =\n{C_manual}")
    assert np.array_equal(C, C_manual), "手写结果与 NumPy 不一致！"
    print("✅ 手写结果与 NumPy 一致")

    # ---------------------------------------------------------------
    # 5. 维度规则：(m,n) @ (n,p) = (m,p)
    # ---------------------------------------------------------------
    print("\n=== 维度规则 ===")
    M = np.random.randn(3, 4)   # 3行4列
    N = np.random.randn(4, 2)   # 4行2列
    P = M @ N
    print(f"M.shape = {M.shape}, N.shape = {N.shape}")
    print(f"(M @ N).shape = {P.shape}")    # (3, 2)

    # ---------------------------------------------------------------
    # 6. 转置（Transpose）：行列互换
    # ---------------------------------------------------------------
    print("\n=== 转置 ===")
    print(f"A =\n{A}")
    print(f"A.T =\n{A.T}")
    # 用转置让内维度匹配：A(2,3) @ B.T(3,2) 是合法的
    X = np.array([[1, 2, 3],
                  [4, 5, 6]])   # (2, 3)
    Y = np.array([[7, 8],
                  [9, 10],
                  [11, 12]])     # (3, 2)
    print(f"X.shape = {X.shape}, Y.shape = {Y.shape}")
    print(f"(X @ Y).shape = {(X @ Y).shape}")  # (2, 2)

    # ---------------------------------------------------------------
    # 7. Hadamard 积（对应元素相乘，记作 A * B）
    #    与矩阵乘法 A @ B 完全不同！
    # ---------------------------------------------------------------
    print("\n=== Hadamard 积（对应元素相乘）===")
    H = A * B
    print(f"A * B =\n{H}")                  # [[5 12] [21 32]]
    print("注意：A * B ≠ A @ B")

    # ---------------------------------------------------------------
    # 8. shape 陷阱：(n,) vs (n,1) vs (1,n)
    # ---------------------------------------------------------------
    print("\n=== shape 陷阱 ===")
    v1 = np.array([1, 2, 3])         # shape (3,)   一维
    v2 = np.array([[1], [2], [3]])   # shape (3, 1) 列向量
    v3 = np.array([[1, 2, 3]])       # shape (1, 3) 行向量
    print(f"v1.shape = {v1.shape}  ← 一维，既不是行也不是列")
    print(f"v2.shape = {v2.shape}  ← 列向量")
    print(f"v3.shape = {v3.shape}  ← 行向量")
    # 用 reshape 互转
    print(f"v1.reshape(3,1) =\n{v1.reshape(3, 1)}")
    print(f"v1.reshape(1,3) = {v1.reshape(1, 3)}")


if __name__ == "__main__":
    main()
