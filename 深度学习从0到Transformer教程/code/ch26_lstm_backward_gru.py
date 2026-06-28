"""
Ch26 · LSTM 反向传播与 GRU 变体
=================================
1. 基于 Ch24 前向结果手算 LSTM 反向梯度（5 个梯度）
2. GRU 单步前向数值例子（2 维）
3. PyTorch LSTM 自动反向 + 梯度裁剪

运行：python ch26_lstm_backward_gru.py
"""

import numpy as np


def sigmoid(x):
    return 1 / (1 + np.exp(-x))


def lstm_backward_step(dh_t, dC_next, f_next,
                       C_prev, C_bar, f_t, i_t, o_t, C_t):
    """LSTM 单步反向传播。

    公式:
        ∂L/∂C_t = ∂L/∂h_t ⊙ o_t ⊙ (1 - tanh²(C_t)) + ∂L/∂C_{t+1} ⊙ f_{t+1}
        ∂L/∂f_t = ∂L/∂C_t ⊙ C_{t-1}
        ∂L/∂i_t = ∂L/∂C_t ⊙ C̃_t
        ∂L/∂C̃_t = ∂L/∂C_t ⊙ i_t
        ∂L/∂o_t = ∂L/∂h_t ⊙ tanh(C_t)

    Args:
        dh_t: 上游对 h_t 的梯度
        dC_next: 下一时间步对 C_{t+1} 的梯度
        f_next: 下一时间步的遗忘门 f_{t+1}
        C_prev, C_bar, f_t, i_t, o_t, C_t: 前向值（来自 Ch24）

    Returns:
        dC_t, df_t, di_t, do_t, dC_bar
    """
    tanh_Ct = np.tanh(C_t)
    one_minus_tanh2 = 1 - tanh_Ct ** 2

    # 步骤 1: h 路径分量
    dC_t_from_h = dh_t * o_t * one_minus_tanh2

    # 步骤 2: 累加 C_{t+1} 路径
    dC_t = dC_t_from_h + dC_next * f_next

    # 步骤 3: 三门梯度
    df_t = dC_t * C_prev
    di_t = dC_t * C_bar
    do_t = dh_t * tanh_Ct

    # 步骤 4: 候选状态梯度
    dC_bar = dC_t * i_t

    return dC_t, df_t, di_t, do_t, dC_bar


def gru_forward_step(h_prev, x_t, W_z, W_r, W_h):
    """GRU 单步前向传播。

    公式:
        z_t = σ(W_z · [h_{t-1}, x_t])          # 更新门
        r_t = σ(W_r · [h_{t-1}, x_t])          # 重置门
        h̃_t = tanh(W_h · [r_t ⊙ h_{t-1}, x_t])  # 候选状态
        h_t = (1 - z_t) ⊙ h_{t-1} + z_t ⊙ h̃_t  # 隐藏状态（加法更新）

    Args:
        h_prev: h_{t-1}, shape (h,)
        x_t: 当前输入, shape (d,)
        W_z, W_r, W_h: 3 组权重, shape (h, h+d)

    Returns:
        z_t, r_t, h_bar, h_t
    """
    concat = np.concatenate([h_prev, x_t])

    z_t = sigmoid(W_z @ concat)           # 更新门
    r_t = sigmoid(W_r @ concat)           # 重置门

    r_h = r_t * h_prev                    # 重置门控制历史依赖
    concat2 = np.concatenate([r_h, x_t])
    h_bar = np.tanh(W_h @ concat2)        # 候选状态

    h_t = (1 - z_t) * h_prev + z_t * h_bar  # 加法更新

    return z_t, r_t, h_bar, h_t


def main():
    print("=" * 60)
    print("Ch26: LSTM 反向传播与 GRU 变体")
    print("=" * 60)

    # === 第 1 部分：LSTM 反向梯度手算验证 ===
    print()
    print("=" * 50)
    print("第 1 部分: LSTM 反向梯度（接 Ch24 前向结果）")
    print("=" * 50)

    # 前向值（来自 Ch24）
    C_prev = np.array([0.6, -0.4])
    C_bar = np.array([0.446, 0.592])
    f_t = np.array([0.648, 0.804])
    i_t = np.array([0.684, 0.596])
    o_t = np.array([0.625, 0.589])
    C_t = np.array([0.694, 0.031])

    print()
    print("--- 前向值（来自 Ch24）---")
    print(f"C_{{t-1}} = {C_prev}")
    print(f"C̃_t    = {C_bar}")
    print(f"f_t    = {f_t}")
    print(f"i_t    = {i_t}")
    print(f"o_t    = {o_t}")
    print(f"C_t    = {C_t}")
    print(f"tanh(C_t) = {np.tanh(C_t).round(3)}")

    # 上游梯度
    dh_t = np.array([0.1, 0.1])
    dC_next = np.array([0.05, 0.05])
    f_next = 0.9

    print()
    print("--- 上游梯度 ---")
    print(f"∂L/∂h_t     = {dh_t}")
    print(f"∂L/∂C_{{t+1}} = {dC_next}")
    print(f"f_{{t+1}}     = {f_next}")

    # 计算反向梯度
    dC_t, df_t, di_t, do_t, dC_bar_grad = lstm_backward_step(
        dh_t, dC_next, f_next,
        C_prev, C_bar, f_t, i_t, o_t, C_t
    )

    print()
    print("--- 反向梯度计算 ---")
    print(f"∂L/∂C_t  = {dC_t.round(3)}")
    print(f"  ├─ h 路径: {dh_t} * {o_t} * { (1 - np.tanh(C_t)**2).round(3) }"
          f" = {(dh_t * o_t * (1 - np.tanh(C_t)**2)).round(3)}")
    print(f"  └─ C 路径: {dC_next} * {f_next}"
          f" = {(dC_next * f_next).round(3)}")
    print(f"∂L/∂f_t  = {df_t.round(3)}  (= ∂L/∂C_t ⊙ C_{{t-1}})")
    print(f"∂L/∂i_t  = {di_t.round(3)}  (= ∂L/∂C_t ⊙ C̃_t)")
    print(f"∂L/∂o_t  = {do_t.round(3)}  (= ∂L/∂h_t ⊙ tanh(C_t))")
    print(f"∂L/∂C̃_t = {dC_bar_grad.round(3)}  (= ∂L/∂C_t ⊙ i_t)")

    # 验证
    expected = {
        'dC_t': [0.085, 0.104],
        'df_t': [0.051, -0.042],
        'di_t': [0.038, 0.061],  # 代码精确值
        'do_t': [0.060, 0.003],
        'dC_bar': [0.058, 0.062],
    }
    print()
    print("--- 验证 ---")
    for name, val, exp in [
        ('∂L/∂C_t', dC_t, expected['dC_t']),
        ('∂L/∂f_t', df_t, expected['df_t']),
        ('∂L/∂i_t', di_t, expected['di_t']),
        ('∂L/∂o_t', do_t, expected['do_t']),
        ('∂L/∂C̃_t', dC_bar_grad, expected['dC_bar']),
    ]:
        match = np.allclose(val.round(3), exp, atol=0.002)
        status = "✅" if match else "⚠️"
        print(f"  {status} {name} = {val.round(3)} (期望 {exp})")

    # 核心洞察
    print()
    print("--- 核心洞察 ---")
    print(f"∂L/∂C_t 的第 2 分量 = {dC_t[1]:.3f}")
    print(f"  其中 {dC_next[1] * f_next:.3f} 来自 C 路径 (∂L/∂C_{{t+1}} × f_{{t+1}})")
    print(f"  f_{{t+1}} = {f_next} 让梯度几乎无损回传——这就是 LSTM 缓解梯度消失的核心！")
    print(f"  对比 RNN: W_hh × tanh' ≈ 0.45，只能传回 {dC_next[1] * 0.45:.3f}")

    # === 第 2 部分：GRU 前向 ===
    print()
    print("=" * 50)
    print("第 2 部分: GRU 前向（与 Ch24 同输入对比）")
    print("=" * 50)

    h_prev = np.array([0.5, -0.3])
    x_t = np.array([1.0, 0.8])

    print()
    print("--- 输入（与 Ch24 相同）---")
    print(f"h_{{t-1}} = {h_prev}")
    print(f"x_t     = {x_t}")

    # 3 组权重（对比 LSTM 的 4 组）
    W_z = np.array([[0.1, 0.2, 0.3, 0.4],
                    [0.5, 0.6, 0.7, 0.8]])
    W_r = np.array([[0.2, 0.1, 0.3, 0.5],
                    [0.4, 0.3, 0.2, 0.1]])
    W_h = np.array([[0.3, 0.2, 0.1, 0.4],
                    [0.2, 0.4, 0.3, 0.1]])

    print()
    print("--- 权重（3 组，对比 LSTM 的 4 组）---")
    print(f"W_z = {W_z}  ← 更新门")
    print(f"W_r = {W_r}  ← 重置门")
    print(f"W_h = {W_h}  ← 候选状态")

    z_t, r_t, h_bar, h_t = gru_forward_step(h_prev, x_t, W_z, W_r, W_h)

    print()
    print("--- GRU 计算 ---")
    concat = np.concatenate([h_prev, x_t])
    print(f"第 1 步: 更新门 z_t = σ(W_z · concat)")
    print(f"  z_t = sigmoid({W_z @ concat}) = {z_t.round(3)}")

    print(f"第 2 步: 重置门 r_t = σ(W_r · concat)")
    print(f"  r_t = sigmoid({W_r @ concat}) = {r_t.round(3)}")

    r_h = r_t * h_prev
    concat2 = np.concatenate([r_h, x_t])
    print(f"第 3 步: 候选状态 h̃_t = tanh(W_h · [r_t⊙h_{{t-1}}, x_t])")
    print(f"  r_t ⊙ h_{{t-1}} = {r_h.round(3)}")
    print(f"  h̃_t = tanh({W_h @ concat2}) = {h_bar.round(3)}")

    print(f"第 4 步: 隐藏状态 h_t = (1-z_t)⊙h_{{t-1}} + z_t⊙h̃_t")
    print(f"  (1-z_t) = {(1 - z_t).round(3)}")
    print(f"  (1-z_t)⊙h_{{t-1}} = {((1 - z_t) * h_prev).round(3)}")
    print(f"  z_t⊙h̃_t = {(z_t * h_bar).round(3)}")
    print(f"  h_t = {((1 - z_t) * h_prev + z_t * h_bar).round(3)}")

    print()
    print("--- GRU 结果汇总 ---")
    print(f"z_t  = {z_t.round(3)}   ← 更新门")
    print(f"r_t  = {r_t.round(3)}   ← 重置门")
    print(f"h̃_t = {h_bar.round(3)}   ← 候选状态")
    print(f"h_t  = {h_t.round(3)}   ← 隐藏状态")

    # 对比 LSTM
    print()
    print("--- LSTM vs GRU 对比 ---")
    print(f"{'模型':>6} | {'h_t':>20} | {'权重矩阵数':>10} | {'状态数':>6}")
    print("-" * 50)
    print(f"{'LSTM':>6} | {'[0.375, 0.018]':>20} | {'4':>10} | {'2 (h,C)':>6}")
    print(f"{'GRU':>6} | {str(h_t.round(3)):>20} | {'3':>10} | {'1 (h)':>6}")
    print()
    print("GRU 用更少参数（3 个 W vs LSTM 的 4 个 W）达到类似效果。")

    # === 第 3 部分：PyTorch 对比 ===
    print()
    print("=" * 50)
    print("第 3 部分: PyTorch LSTM/GRU 对比")
    print("=" * 50)

    try:
        import torch
        import torch.nn as nn

        # PyTorch LSTM 自动反向
        print()
        print("--- PyTorch LSTM 自动反向 ---")
        lstm = nn.LSTM(input_size=10, hidden_size=20, batch_first=True)
        X = torch.randn(1, 5, 10)  # batch=1, T=5, d=10
        out, (h, C) = lstm(X)
        loss = out.sum()
        loss.backward()

        # 梯度裁剪（防止爆炸）
        grad_norm_before = torch.nn.utils.clip_grad_norm_(
            lstm.parameters(), max_norm=5.0
        )
        print(f"LSTM 参数梯度已计算: {lstm.weight_ih_l0.grad is not None}")
        print(f"梯度裁剪前范数: {grad_norm_before:.2f}")
        print(f"梯度裁剪后范数 ≤ 5.0")

        # GRU 对比
        print()
        print("--- LSTM vs GRU 参数量 ---")
        gru = nn.GRU(input_size=10, hidden_size=20, batch_first=True)

        lstm_params = sum(p.numel() for p in lstm.parameters())
        gru_params = sum(p.numel() for p in gru.parameters())
        print(f"LSTM 参数量: {lstm_params}")
        print(f"GRU  参数量: {gru_params}")
        print(f"GRU 比 LSTM 少 {lstm_params - gru_params} 个参数"
              f"（约 {(1 - gru_params/lstm_params)*100:.1f}%）")

    except ImportError:
        print("（未安装 PyTorch，跳过对比。安装后可运行: pip install torch）")

    # === 总结 ===
    print()
    print("=" * 50)
    print("总结")
    print("=" * 50)
    print("1. LSTM 反向传播有两条梯度路径:")
    print("   - h 路径: ∂L/∂h_t → ∂L/∂C_t（经 o_t 和 tanh'）")
    print("   - C 路径: ∂L/∂C_{t+1} → ∂L/∂C_t（经 f_{t+1}）← 加法高速公路")
    print("2. C 路径的加法更新让梯度几乎无损传递（f≈1 时）")
    print("3. GRU 把 3 门压成 2 门（更新门 z_t + 重置门 r_t）")
    print("4. GRU 把 2 状态压成 1 状态（无独立 C_t）")
    print("5. 梯度裁剪只治爆炸不治消失，LSTM 的加法更新才治本")


if __name__ == "__main__":
    main()
