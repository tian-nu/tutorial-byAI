# 附录A：核心公式速查

> 覆盖人教版高中数学必修第一册（A版）全部核心公式。公式使用 LaTeX 块级 `$$...$$` 呈现，便于打印存档与考前速查。

---

## 第一章  集合与逻辑

### 1.1 德摩根律（De Morgan 律）

**并集的补集 = 补集的交集：**

$$
\complement_U (A \cup B) = (\complement_U A) \cap (\complement_U B)
$$

**交集的补集 = 补集的并集：**

$$
\complement_U (A \cap B) = (\complement_U A) \cup (\complement_U B)
$$

> 口诀：并补变交补，交补变并补；长横断开，符号翻转。

---

### 1.2 补集性质

$$
A \cup (\complement_U A) = U, \qquad A \cap (\complement_U A) = \varnothing
$$

$$
\complement_U (\complement_U A) = A
$$

---

### 1.3 子集个数公式

含有 $n$ 个元素的集合，其子集个数为 $2^n$，真子集个数为 $2^n - 1$，非空真子集个数为 $2^n - 2$。

---

## 第二章  不等式

### 2.1 基本不等式（均值不等式）

**二元形式：**

$$
\frac{a + b}{2} \ge \sqrt{ab} \quad (a, b > 0)
$$

取等条件：$a = b$。

**延伸形式：**

$$
ab \le \left(\frac{a + b}{2}\right)^2 \quad (a, b \in \mathbb{R})
$$

---

### 2.2 不等式链（调和 ≤ 几何 ≤ 算术 ≤ 平方）

对正数 $a, b$：

$$
\frac{2}{\frac{1}{a} + \frac{1}{b}}
\;\le\; \sqrt{ab}
\;\le\; \frac{a + b}{2}
\;\le\; \sqrt{\frac{a^2 + b^2}{2}}
$$

> 即：调和均值 ≤ 几何均值 ≤ 算术均值 ≤ 平方均值。全部取等当且仅当 $a = b$。

---

### 2.3 三元基本不等式

对正数 $a, b, c$：

$$
\frac{a + b + c}{3} \ge \sqrt[3]{abc}
$$

取等条件：$a = b = c$。

---

### 2.4 二次不等式解集法则（$a > 0$）

对 $f(x) = ax^2 + bx + c \;(a > 0)$，设 $\Delta = b^2 - 4ac$：

| 判别式 | $f(x) > 0$ 的解集 | $f(x) < 0$ 的解集 |
|:---:|:---|:---|
| $\Delta > 0$，两实根 $x_1 < x_2$ | $\{x \mid x < x_1 \text{ 或 } x > x_2\}$ | $\{x \mid x_1 < x < x_2\}$ |
| $\Delta = 0$，一实根 $x_0$ | $\{x \mid x \ne x_0\}$ | $\varnothing$ |
| $\Delta < 0$，无实根 | $\mathbb{R}$ | $\varnothing$ |

> 口诀（$a>0$ 时）：大于取两边，小于取中间。

---

### 2.5 绝对值不等式

$$
|x| < a \;(a>0) \iff -a < x < a
$$

$$
|x| > a \;(a>0) \iff x < -a \;\text{或}\; x > a
$$

---

## 第三章  函数

### 3.1 函数单调性的定义

**增函数：** 对定义域 $I$ 内某个区间上的任意 $x_1, x_2$：

$$
x_1 < x_2 \;\Longrightarrow\; f(x_1) < f(x_2)
$$

**减函数：**

$$
x_1 < x_2 \;\Longrightarrow\; f(x_1) > f(x_2)
$$

---

### 3.2 函数奇偶性的定义

**偶函数：** 对定义域内任意 $x$：

$$
f(-x) = f(x)
$$

图像关于 $y$ 轴对称。

**奇函数：** 对定义域内任意 $x$：

$$
f(-x) = -f(x)
$$

图像关于原点对称。

**推论：** 若奇函数在 $x = 0$ 处有定义，则 $f(0) = 0$。

---

### 3.3 函数奇偶性的运算性质

偶 ± 偶 = 偶；奇 ± 奇 = 奇；偶 × 偶 = 偶；奇 × 奇 = 偶；奇 × 偶 = 奇。

---

### 3.4 幂函数图像规律

幂函数 $y = x^\alpha$ 的图像特征：

| $\alpha$ 范围 | 过定点 | 单调性（第一象限） | 图像大致形状 |
|:---:|:---|:---|:---|
| $\alpha > 1$ | $(0,0),\,(1,1)$ | ↗ 递增（增速加快） | 下凸上升 |
| $0 < \alpha < 1$ | $(0,0),\,(1,1)$ | ↗ 递增（增速放缓） | 上凸上升 |
| $\alpha < 0$ | $(1,1)$ | ↘ 递减 | 两支双曲线型渐近坐标轴 |

> 口诀：奇次幂奇函数，偶次幂偶函数；指数决定开口，正上凸下凸看是否大于1。

---

## 第四章  指数函数与对数函数

### 4.1 指数运算法则

设 $a > 0,\,b > 0$，$m, n \in \mathbb{R}$。

**同底相乘：**
$$
a^m \cdot a^n = a^{m+n}
$$

**同底相除：**
$$
\frac{a^m}{a^n} = a^{m-n}
$$

**幂的幂：**
$$
(a^m)^n = a^{mn}
$$

**积的幂：**
$$
(ab)^n = a^n \cdot b^n
$$

**商的幂：**
$$
\left(\frac{a}{b}\right)^n = \frac{a^n}{b^n}
$$

---

### 4.2 指数函数图像与性质

$$
y = a^x \quad (a > 0,\; a \ne 1)
$$

| 项目 | $a > 1$ | $0 < a < 1$ |
|:---|:---|:---|
| 定义域 | $\mathbb{R}$ | $\mathbb{R}$ |
| 值域 | $(0, +\infty)$ | $(0, +\infty)$ |
| 过定点 | $(0, 1)$ | $(0, 1)$ |
| 单调性 | 增函数 | 减函数 |

---

### 4.3 对数定义

若 $a^x = N \;(a > 0,\, a \ne 1)$，则：

$$
x = \log_a N
$$

其中 $a$ 为底数，$N$ 为真数（$N > 0$）。

---

### 4.4 对数运算法则

设 $a > 0,\, a \ne 1$，$M > 0,\, N > 0$。

**积的对数：**
$$
\log_a (MN) = \log_a M + \log_a N
$$

**商的对数：**
$$
\log_a \frac{M}{N} = \log_a M - \log_a N
$$

**幂的对数：**
$$
\log_a M^n = n \log_a M
$$

---

### 4.5 换底公式

$$
\log_a b = \frac{\log_c b}{\log_c a} \quad (c > 0,\, c \ne 1)
$$

**常用推论：**

$$
\log_a b \cdot \log_b a = 1
$$

$$
\log_{a^n} b^m = \frac{m}{n} \log_a b
$$

---

### 4.6 对数恒等式

**基本恒等式：**
$$
a^{\log_a N} = N \quad (N > 0)
$$

**特殊值：**
$$
\log_a 1 = 0, \qquad \log_a a = 1
$$

---

### 4.7 对数函数图像与性质

$$
y = \log_a x \quad (a > 0,\, a \ne 1)
$$

| 项目 | $a > 1$ | $0 < a < 1$ |
|:---|:---|:---|
| 定义域 | $(0, +\infty)$ | $(0, +\infty)$ |
| 值域 | $\mathbb{R}$ | $\mathbb{R}$ |
| 过定点 | $(1, 0)$ | $(1, 0)$ |
| 单调性 | 增函数 | 减函数 |

---

### 4.8 指数函数与对数函数互为反函数

$$
y = a^x \;\longleftrightarrow\; y = \log_a x
$$

二者图像关于直线 $y = x$ 对称。

---

## 第五章  三角函数

### 5.1 特殊角的三角函数值

| 角 $\alpha$ | $0$ | $\dfrac{\pi}{6}$ | $\dfrac{\pi}{4}$ | $\dfrac{\pi}{3}$ | $\dfrac{\pi}{2}$ | $\pi$ | $\dfrac{3\pi}{2}$ |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| $\sin\alpha$ | $0$ | $\dfrac{1}{2}$ | $\dfrac{\sqrt{2}}{2}$ | $\dfrac{\sqrt{3}}{2}$ | $1$ | $0$ | $-1$ |
| $\cos\alpha$ | $1$ | $\dfrac{\sqrt{3}}{2}$ | $\dfrac{\sqrt{2}}{2}$ | $\dfrac{1}{2}$ | $0$ | $-1$ | $0$ |
| $\tan\alpha$ | $0$ | $\dfrac{\sqrt{3}}{3}$ | $1$ | $\sqrt{3}$ | 无意义 | $0$ | 无意义 |

---

### 5.2 同角三角函数的基本关系

**平方关系：**
$$
\sin^2\alpha + \cos^2\alpha = 1
$$

**商数关系：**
$$
\tan\alpha = \frac{\sin\alpha}{\cos\alpha} \quad \left(\alpha \ne k\pi + \frac{\pi}{2}\right)
$$

**倒数关系（拓展）：**
$$
\tan\alpha \cdot \cot\alpha = 1
$$

---

### 5.3 诱导公式（六组）

> 口诀：「奇变偶不变，符号看象限」——将 $\alpha$ 视为锐角，原函数名在对应象限的符号即为结果符号。

**公式一（终边相同的角）：**
$$
\sin(2k\pi + \alpha) = \sin\alpha,\quad
\cos(2k\pi + \alpha) = \cos\alpha,\quad
\tan(2k\pi + \alpha) = \tan\alpha
$$

**公式二（$\pi + \alpha$）：**
$$
\sin(\pi + \alpha) = -\sin\alpha,\quad
\cos(\pi + \alpha) = -\cos\alpha,\quad
\tan(\pi + \alpha) = \tan\alpha
$$

**公式三（$-\alpha$）：**
$$
\sin(-\alpha) = -\sin\alpha,\quad
\cos(-\alpha) = \cos\alpha,\quad
\tan(-\alpha) = -\tan\alpha
$$

**公式四（$\pi - \alpha$）：**
$$
\sin(\pi - \alpha) = \sin\alpha,\quad
\cos(\pi - \alpha) = -\cos\alpha,\quad
\tan(\pi - \alpha) = -\tan\alpha
$$

**公式五（$\frac{\pi}{2} - \alpha$）：**
$$
\sin\!\left(\frac{\pi}{2} - \alpha\right) = \cos\alpha,\quad
\cos\!\left(\frac{\pi}{2} - \alpha\right) = \sin\alpha
$$

**公式六（$\frac{\pi}{2} + \alpha$）：**
$$
\sin\!\left(\frac{\pi}{2} + \alpha\right) = \cos\alpha,\quad
\cos\!\left(\frac{\pi}{2} + \alpha\right) = -\sin\alpha
$$

---

### 5.4 两角和与差公式

**正弦：**
$$
\sin(\alpha + \beta) = \sin\alpha\cos\beta + \cos\alpha\sin\beta
$$
$$
\sin(\alpha - \beta) = \sin\alpha\cos\beta - \cos\alpha\sin\beta
$$

**余弦：**
$$
\cos(\alpha + \beta) = \cos\alpha\cos\beta - \sin\alpha\sin\beta
$$
$$
\cos(\alpha - \beta) = \cos\alpha\cos\beta + \sin\alpha\sin\beta
$$

**正切：**
$$
\tan(\alpha + \beta) = \frac{\tan\alpha + \tan\beta}{1 - \tan\alpha\tan\beta}
$$
$$
\tan(\alpha - \beta) = \frac{\tan\alpha - \tan\beta}{1 + \tan\alpha\tan\beta}
$$

> 口诀：余余正正符号反（余弦），正余余正符号同（正弦）。

---

### 5.5 二倍角公式

**正弦：**
$$
\sin 2\alpha = 2\sin\alpha\cos\alpha
$$

**余弦（三种等价形式）：**
$$
\cos 2\alpha = \cos^2\alpha - \sin^2\alpha = 2\cos^2\alpha - 1 = 1 - 2\sin^2\alpha
$$

**正切：**
$$
\tan 2\alpha = \frac{2\tan\alpha}{1 - \tan^2\alpha}
$$

---

### 5.6 降幂公式

由二倍角余弦公式变形得：

$$
\sin^2\alpha = \frac{1 - \cos 2\alpha}{2}
$$

$$
\cos^2\alpha = \frac{1 + \cos 2\alpha}{2}
$$

---

### 5.7 半角公式

$$
\sin\frac{\alpha}{2} = \pm\sqrt{\frac{1 - \cos\alpha}{2}}
$$

$$
\cos\frac{\alpha}{2} = \pm\sqrt{\frac{1 + \cos\alpha}{2}}
$$

$$
\tan\frac{\alpha}{2} = \pm\sqrt{\frac{1 - \cos\alpha}{1 + \cos\alpha}}
$$

$\pm$ 号由 $\frac{\alpha}{2}$ 所在象限决定。

**半角正切的有理形式（不含根号）：**

$$
\tan\frac{\alpha}{2} = \frac{\sin\alpha}{1 + \cos\alpha} = \frac{1 - \cos\alpha}{\sin\alpha}
$$

---

### 5.8 万能公式

令 $t = \tan\dfrac{\alpha}{2}$，则：

$$
\sin\alpha = \frac{2t}{1 + t^2}
$$

$$
\cos\alpha = \frac{1 - t^2}{1 + t^2}
$$

$$
\tan\alpha = \frac{2t}{1 - t^2}
$$

> 用途：将三角有理式统一为 $t$ 的有理函数，便于求积分或解方程。

---

### 5.9 辅助角公式（合一变形）

对 $a\sin x + b\cos x$（$a, b$ 不同时为零）：

$$
a\sin x + b\cos x = \sqrt{a^2 + b^2}\,\sin(x + \varphi)
$$

其中 $\varphi$（辅助角）满足：

$$
\cos\varphi = \frac{a}{\sqrt{a^2 + b^2}}, \qquad
\sin\varphi = \frac{b}{\sqrt{a^2 + b^2}}, \qquad
\tan\varphi = \frac{b}{a}
$$

> 也可写成余弦形式：$a\sin x + b\cos x = \sqrt{a^2 + b^2}\,\cos(x - \theta)$，其中 $\tan\theta = \dfrac{a}{b}$。

---

### 5.10 函数 $y = A\sin(\omega x + \varphi)$ 的图像变换

**基本参数含义：**

| 参数 | 名称 | 含义 |
|:---:|:---|:---|
| $A$ | 振幅 | 最大值 $|A|$，最小值 $-|A|$ |
| $\omega$ | 角频率 | 周期 $T = \dfrac{2\pi}{|\omega|}$ |
| $\varphi$ | 初相 | 图像在 $x$ 轴方向的平移量 |

**变换公式（由 $y = \sin x$ 出发）：**

1. **左右平移**：$y = \sin(x + \varphi)$，左 $+$ 右 $-$（平移 $|\varphi|$ 个单位）。

2. **横向伸缩**：$y = \sin(\omega x)$，
   - $|\omega| > 1$：横坐标缩短为原来的 $\dfrac{1}{|\omega|}$；
   - $0 < |\omega| < 1$：横坐标伸长为原来的 $\dfrac{1}{|\omega|}$。

3. **纵向伸缩**：$y = A\sin x$，
   - $|A| > 1$：纵坐标伸长为原来的 $|A|$ 倍；
   - $0 < |A| < 1$：纵坐标缩短为原来的 $|A|$ 倍。

**标准变换顺序（先平移，后伸缩）：**

$$
y = \sin x
\;\xrightarrow{\text{左/右平移 }|\varphi|}\;
y = \sin(x + \varphi)
\;\xrightarrow{\text{横坐标变为 }\frac{1}{\omega}}\;
y = \sin(\omega x + \varphi)
\;\xrightarrow{\text{纵坐标变为 }A\text{ 倍}}\;
y = A\sin(\omega x + \varphi)
$$

> 若先伸缩后平移，则平移量为 $\left|\dfrac{\varphi}{\omega}\right|$。

---

### 5.11 三角函数的周期性

- $y = A\sin(\omega x + \varphi)$ 和 $y = A\cos(\omega x + \varphi)$ 的周期：$T = \dfrac{2\pi}{|\omega|}$。
- $y = A\tan(\omega x + \varphi)$ 的周期：$T = \dfrac{\pi}{|\omega|}$。

---

### 5.12 积化和差公式（拓展）

$$
\sin\alpha\cos\beta = \frac{1}{2}\bigl[\sin(\alpha + \beta) + \sin(\alpha - \beta)\bigr]
$$

$$
\cos\alpha\sin\beta = \frac{1}{2}\bigl[\sin(\alpha + \beta) - \sin(\alpha - \beta)\bigr]
$$

$$
\cos\alpha\cos\beta = \frac{1}{2}\bigl[\cos(\alpha + \beta) + \cos(\alpha - \beta)\bigr]
$$

$$
\sin\alpha\sin\beta = -\frac{1}{2}\bigl[\cos(\alpha + \beta) - \cos(\alpha - \beta)\bigr]
$$

---

### 5.13 和差化积公式（拓展）

$$
\sin\theta + \sin\varphi = 2\sin\frac{\theta + \varphi}{2}\cos\frac{\theta - \varphi}{2}
$$

$$
\sin\theta - \sin\varphi = 2\cos\frac{\theta + \varphi}{2}\sin\frac{\theta - \varphi}{2}
$$

$$
\cos\theta + \cos\varphi = 2\cos\frac{\theta + \varphi}{2}\cos\frac{\theta - \varphi}{2}
$$

$$
\cos\theta - \cos\varphi = -2\sin\frac{\theta + \varphi}{2}\sin\frac{\theta - \varphi}{2}
$$

---

> **附录完** — 以上覆盖人教版必修第一册全部核心公式。建议打印或保存为 PDF，日常练习和考前速查均可使用。