# 全文核查第四批：差分隐私图切误差界的十余年演化

更新：2026-10-11。本批从固定分层样本中取 2011 年理论论文，再按其开放问题和后续引用追到 2025 年论文。重点是比较问题定义/保证，不把渐近界直接当作同条件的性能差。

## 1. Iterative Constructions and Private Data Release (2011)

- **版本/发表：** arXiv:1107.3731v2；发表于 TCC 2012，属于理论计算机科学/隐私保护。
- **问题：** 如何对图的指数多个 cut queries 提供边级差分隐私下的交互回答，或释放可供离线查询的合成图。
- **方法与结论：** 提出 iterative database construction (IDC) 统一框架，涵盖并改进 median/multiplicative-weights 分析；构造基于 Frieze–Kannan 分解的交互机制，在图较稠密、数据库规模接近 universe 时改进此前误差界。合成图方案用 edge-wise Laplace 随机响应再配 cut-norm 近似，将所有 cut 的加性误差做到 O(|V|^1.5/ε)。原文 §§1、3–6。
- **开放问题：** 若能高效私有计算足够准确的 rank-1 matrix approximation，就可进一步改进合成图 cut-query 误差；论文将如何构造该算法列为主要开放问题。原文 §7。
- **边界：** 主要是理论证明/误差界，不是实际数据集上的效用基准；交互 query release 与非交互 synthetic graph 是不同产品目标，误差度量也不能混为一谈。
- **来源：** [原文 §§1–7](https://arxiv.org/html/1107.3731)；[TCC 2012 发表版本](https://www.iacr.org/archive/tcc2012/71940208/71940208.pdf)。

## 2. Breaking the (n^{1.5}) Additive Error Barrier (2025)

- **版本/发表：** arXiv:2507.01873v1（2025-07-02）；理论图算法与差分隐私。
- **问题及贡献：** 对非负加权图发布私有 synthetic sparsifier，使所有 cuts 同时得到近似。作者将 2012 年 GRU 的 O(n^1.5) 误差列为此前高效私有算法界限，给出多项式时间算法，输出约 O(n/γ²) 条边的非负加权图，并对任意 cut 提供 1+γ 乘法误差加 n^(1.25+o(1))·polylog(1/δ)/(ε√γ) 级加性误差。核心是 private expander decomposition。原文 §1、Theorem 1.1、§3。
- **机制：** 把图切成内部扩展性强的 dense pieces 与总权重受控的 inter-component sparse edges：前者用乘法近似吸收局部噪声，后者用约 O(√(nm)) 型 DP cut approximation 处理。原文 §§1.2、3–4。
- **后续仍未解决：** 作者还问能否把加性误差从 n^1.25 降低、以及哪些 m≫n 区间存在可证明的更好界。原文 §6。
- **可比性限制：** 2011/2012 方案为 pure DP、针对所有 cuts 的加性误差界，且图可非稀疏；2025 主定理为 approximate (ε,δ)-DP，输出 sparse non-negative synthetic graph，保证同时含乘法 1+γ 与加性误差。新论文宣称突破的是允许乘法误差的 sparse cut-sparsifier 问题；不能说它在同一纯加性/同一隐私定义下把 2011 结论直接降了指数。
- **来源：** [2025 原文 §§1、3–6](https://arxiv.org/html/2507.01873)。

## 时间线判断

这里的发现不是“老论文落后”，而是对照了公开开放问题与后来理论进展：相近的 cut-query 目标在 2012–2025 年间从纯加性界转向乘法+加性稀疏合成图，并利用私有扩展分解跨过 n^1.5 障碍。可继续研究的部分已转为 n^1.25 后续改善、参数区域、纯 DP / approximate DP 的差距，以及相同图类/隐私参数下的统一定理比较。理论界不是实证收益；本审计也未独立证明其定理。
