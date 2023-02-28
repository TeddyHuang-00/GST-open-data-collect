以下会用到的符号的含义如下

$$
\begin{cases}
    E &= &Enzyme\\
    S &= &Substrate\\
    P &= &Product\\
\end{cases}
$$

下标带 $_0$ 字样的表示总量或起始值

被方括号 $[\ ]$ 所包围的表示瞬时浓度

---

我们假设 GST 所催化的 GSH 取代反应仅一步中间态，即反应中化学平衡应遵守:

$$
E+S \underset{k_{-1}}{\overset{k_1}{\rightleftharpoons}} ES \underset{k_{-2}}{\overset{k_2}{\rightleftharpoons}} E+P
$$

为简化条件，不妨假设从中间态到产物的过程几乎不可逆，即有 :red[$k_{-2}\to0$]，那么就可以简化为:

$$
E+S \underset{k_{-1}}{\overset{k_1}{\rightleftharpoons}} ES \overset{k_2}{\rightharpoonup} E+P
$$

由于时间尺度较大，反应体系应当已经达到平衡，我们又不妨假设 :red[$[ES]$ 的大小恒定]，即消耗与生成速率相当，则有:

$$
(k_{-1}+k_2)[ES] = k_1[E][S]
$$

与常规米氏方程推导不同的是，由于 GST 的催化速率较高，我们不妨假设动态平衡时:red[仅有少量[ES]的存在]，因此我们可取近似:

$$
[E] = E_0-[ES]\approx E_0
$$

其中 $E_0$ 指酶的总浓度，应为一常数。结合上述条件，我们不难得到:

$$
\begin{aligned}
    & (k_{-1}+k_2)[ES] = k_1E_0[S]\\
    \Rightarrow& [ES] = \frac{k_1E_0[S]}{k_{-1}+k_2}\\
    \Rightarrow& \frac{d[P]}{dt} = k_2[ES] = \frac{k_1k_2E_0[S]}{k_{-1}+k_2}\\
\end{aligned}
$$

由于我们测得的 $Abs_{340}$ 值可视为只与产物 $[P]$ 有关，即:

$$
Abs_{340}=[P]\cdot\varepsilon\cdot L\propto[P]
$$

其中 $\varepsilon$ 为消光系数，$L$ 为比色杯光程，因此我们可以通过求得 $[P]$ 随时间的表达式来对 $Abs_{340}$ 进行建模。为此，我们假定加入的底物总浓度为:

$$
S_0=[S]+[P]
$$

则有:

$$
\begin{aligned}
    & \frac{d[P]}{dt} = \frac{k_1k_2E_0(S_0-[P]))}{k_{-1}+k_2}\\
    \Rightarrow& \frac{k_{-1}+k_2}{k_1k_2E_0}\cdot\frac{d[P]}{S_0-[P]} = dt\\
    \xRightarrow{两边积分}& \frac{k_{-1}+k_2}{k_1k_2E_0}\ln{\frac{1}{1-\frac{[P]}{S_0}}} = t\\
    \Rightarrow& \frac{1}{1-\frac{[P]}{S_0}} = \exp\left\{\frac{k_1k_2E_0}{k_{-1}+k_2}\cdot t\right\}\\
    \Rightarrow& 1-\frac{[P]}{S_0} = \exp\left\{-\frac{k_1k_2E_0}{k_{-1}+k_2}\cdot t\right\}\\
    \Rightarrow& [P] = \left(1-\exp\left\{-\frac{k_1k_2E_0}{k_{-1}+k_2}\cdot t\right\}\right)S_0\\
\end{aligned}
$$

我们将 $\frac{k_1 k_2}{k_{-1}+k_2} E_0$ 设为 $K_{tot}$，代表该溶液中酶的总活力，简化后的表达式应为:

$$
[P] = \left(1-e^{-K_{tot}\cdot t}\right)S_0\\
$$

代入 $Abs_{340}=[P]\cdot\varepsilon\cdot L$ 则有:

$$
Abs_{340}=\left(1-e^{-K_{tot}\cdot t}\right)S_0\cdot\varepsilon\cdot L
$$

其中 $\varepsilon=9.6 L\cdot mmol^{-1}\cdot cm^{-1}$，$L=1 cm$，$S_0$ 可根据加入 GSH 的量推算（由于体系中其他因素的影响，这一项也可作为待定项），因此待定系数仅有 $K_{tot}$ 一项，我们可以据此对数据进行模型拟合来求得所有待定项
