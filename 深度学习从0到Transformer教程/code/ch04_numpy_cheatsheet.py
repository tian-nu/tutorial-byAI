"""
Ch04 · Python + NumPy 环境搭建 — NumPy 速查表

覆盖：
  - 创建数组
  - 数组属性（shape / dtype / ndim）
  - 索引与切片
  - 形状操作（reshape / transpose / squeeze）
  - 数学运算（逐元素 + 矩阵乘法 + 聚合）
  - 广播规则（broadcasting）
  - 随机数
  - 拼接与拆分

运行方式：
    python ch04_numpy_cheatsheet.py
"""

import numpy as np


def main() -> None:
    # ===============================================================
    # 1. 创建数组
    # ===============================================================
    print("=" * 60)
    print("1. 创建数组")
    print("=" * 60)

    # 从列表创建
    a = np.array([1, 2, 3])
    print(f"np.array([1,2,3])        = {a}, shape={a.shape}")

    # 从嵌套列表创建矩阵
    B = np.array([[1, 2, 3], [4, 5, 6]])
    print(f"np.array([[1,2,3],[4,5,6]]) =\n{B}, shape={B.shape}")

    # 特殊矩阵
    print(f"np.zeros((2,3))          =\n{np.zeros((2, 3))}")
    print(f"np.ones((2,3))           =\n{np.ones((2, 3))}")
    print(f"np.eye(3)                =\n{np.eye(3)}")          # 单位矩阵
    print(f"np.arange(0, 10, 2)      = {np.arange(0, 10, 2)}")  # [0 2 4 6 8]
    print(f"np.linspace(0, 1, 5)     = {np.linspace(0, 1, 5)}") # [0. 0.25 0.5 0.75 1.]

    # ===============================================================
    # 2. 数组属性
    # ===============================================================
    print("\n" + "=" * 60)
    print("2. 数组属性")
    print("=" * 60)

    x = np.array([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]])
    print(f"x =\n{x}")
    print(f"x.shape   = {x.shape}")     # (2, 3)
    print(f"x.ndim    = {x.ndim}")      # 2
    print(f"x.size    = {x.size}")      # 6
    print(f"x.dtype   = {x.dtype}")     # float64
    print(f"x.T       =\n{x.T}")        # 转置 (3, 2)

    # ===============================================================
    # 3. 索引与切片
    # ===============================================================
    print("\n" + "=" * 60)
    print("3. 索引与切片")
    print("=" * 60)

    arr = np.array([[1, 2, 3, 4],
                    [5, 6, 7, 8],
                    [9, 10, 11, 12]])
    print(f"arr =\n{arr}")
    print(f"arr[0, 1]    = {arr[0, 1]}")     # 第0行第1列 → 2
    print(f"arr[1]       = {arr[1]}")        # 第1行 → [5 6 7 8]
    print(f"arr[:, 1]    = {arr[:, 1]}")     # 第1列 → [2 6 10]
    print(f"arr[0:2, 1:3] =\n{arr[0:2, 1:3]}")  # 前2行，第1-2列
    print(f"arr[arr > 5] = {arr[arr > 5]}")  # 布尔索引

    # ===============================================================
    # 4. 形状操作
    # ===============================================================
    print("\n" + "=" * 60)
    print("4. 形状操作")
    print("=" * 60)

    v = np.arange(6)            # [0 1 2 3 4 5]
    print(f"v = {v}, shape={v.shape}")
    print(f"v.reshape(2, 3) =\n{v.reshape(2, 3)}")
    print(f"v.reshape(3, 2) =\n{v.reshape(3, 2)}")
    print(f"v.reshape(-1, 2) =\n{v.reshape(-1, 2)}")  # -1 自动推断

    # squeeze 去掉长度为1的维度
    col_vec = np.array([[1], [2], [3]])   # shape (3, 1)
    print(f"col_vec.shape = {col_vec.shape}")
    print(f"col_vec.squeeze().shape = {col_vec.squeeze().shape}")  # (3,)

    # ===============================================================
    # 5. 数学运算
    # ===============================================================
    print("\n" + "=" * 60)
    print("5. 数学运算")
    print("=" * 60)

    A = np.array([[1, 2], [3, 4]])
    B = np.array([[5, 6], [7, 8]])

    # 逐元素运算
    print(f"A + B =\n{A + B}")
    print(f"A * B =\n{A * B}")            # Hadamard 积（逐元素）
    print(f"A ** 2 =\n{A ** 2}")          # 逐元素平方

    # 矩阵乘法
    print(f"A @ B =\n{A @ B}")            # 矩阵乘法
    print(f"np.dot(A, B) =\n{np.dot(A, B)}")

    # 标量运算
    print(f"A * 2 =\n{A * 2}")
    print(f"A + 10 =\n{A + 10}")

    # 聚合
    print(f"A.sum()       = {A.sum()}")           # 所有元素求和
    print(f"A.mean()      = {A.mean()}")          # 所有元素均值
    print(f"A.max()       = {A.max()}")
    print(f"A.sum(axis=0) = {A.sum(axis=0)}")     # 沿列求和 → [4 6]
    print(f"A.sum(axis=1) = {A.sum(axis=1)}")     # 沿行求和 → [3 7]

    # ===============================================================
    # 6. 广播规则（Broadcasting）
    # ===============================================================
    print("\n" + "=" * 60)
    print("6. 广播规则")
    print("=" * 60)

    M = np.array([[1, 2, 3],
                  [4, 5, 6]])    # shape (2, 3)
    v1 = np.array([10, 20, 30])  # shape (3,)

    # v1 会被"广播"成 (2, 3)，每行都加 v1
    print(f"M =\n{M}, shape={M.shape}")
    print(f"v1 = {v1}, shape={v1.shape}")
    print(f"M + v1 =\n{M + v1}")

    # 列向量广播
    v2 = np.array([[100], [200]])  # shape (2, 1)
    print(f"v2 =\n{v2}, shape={v2.shape}")
    print(f"M + v2 =\n{M + v2}")

    # ===============================================================
    # 7. 随机数
    # ===============================================================
    print("\n" + "=" * 60)
    print("7. 随机数（用 np.random.default_rng）")
    print("=" * 60)

    rng = np.random.default_rng(seed=42)   # 固定种子，结果可复现
    print(f"rng.random()                  = {rng.random():.4f}")          # [0,1) 均匀分布
    print(f"rng.random(3)                 = {rng.random(3)}")
    print(f"rng.standard_normal((2, 3))   =\n{rng.standard_normal((2, 3))}")  # 标准正态
    print(f"rng.integers(0, 10, size=5)   = {rng.integers(0, 10, size=5)}")   # [0,10) 整数

    # ===============================================================
    # 8. 拼接与拆分
    # ===============================================================
    print("\n" + "=" * 60)
    print("8. 拼接与拆分")
    print("=" * 60)

    X = np.array([[1, 2], [3, 4]])
    Y = np.array([[5, 6], [7, 8]])
    print(f"X =\n{X}")
    print(f"Y =\n{Y}")
    print(f"np.vstack([X, Y]) =\n{np.vstack([X, Y])}")   # 垂直拼接（行变多）
    print(f"np.hstack([X, Y]) =\n{np.hstack([X, Y])}")   # 水平拼接（列变多）

    Z = np.arange(6).reshape(2, 3)
    print(f"Z =\n{Z}")
    print(f"np.split(Z, 3, axis=1) = {np.split(Z, 3, axis=1)}")  # 沿列拆成3份

    # ===============================================================
    # 9. 常用技巧
    # ===============================================================
    print("\n" + "=" * 60)
    print("9. 常用技巧")
    print("=" * 60)

    # argmax / argmin：找最大/最小值的索引
    p = np.array([0.1, 0.7, 0.2])
    print(f"p = {p}")
    print(f"np.argmax(p) = {np.argmax(p)}")   # 1，最大值在第1个位置

    # where：条件选择
    arr = np.array([1, -2, 3, -4, 5])
    print(f"arr = {arr}")
    print(f"np.where(arr > 0, arr, 0) = {np.where(arr > 0, arr, 0)}")  # 负数变0

    # clip：截断
    print(f"np.clip(arr, -1, 1) = {np.clip(arr, -1, 1)}")  # 限制在 [-1, 1]


if __name__ == "__main__":
    main()
