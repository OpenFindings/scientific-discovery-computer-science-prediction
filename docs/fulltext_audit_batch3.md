# 全文核查第三批：跨年代、跨子领域的机制与测量

更新：2026-10-11。此批从可复现抽样框及其跨研究引用追踪中取材。这里记录的“读过”指核对了原文方法/结果/讨论中列出的具体段落，不代表复现代码或穷尽该主题文献。

## 逐篇核查

### 1. FairFuzz：稀有分支命中改善，不保证更早找到崩溃

- **版本/出版：** arXiv:1709.07101v1，2017；软件测试/fuzzing。
- **研究问题与机制：** AFL 会破坏维持深层分支所需的输入字节。FairFuzz优先变异命中稀有分支的种子，并用 branch mask 尽量保留让目标分支继续命中的字节位置。
- **实验：** 与 AFL、FidgetyAFL、AFLFast.new 对比；9 个程序；无字典；每工具每程序单核运行 24 小时、重复 20 次。主指标为 AFL branch/basic-block-transition coverage，附 95% CI。原文 §§4.1–4.2。
- **主要结果：** FairFuzz 多数程序前期覆盖更快；24 小时后它在 `tcpdump`、`xmllint` 有领先，`c++filt` 则 AFLFast.new 占优。`xmllint` 有明显运行间差异：FairFuzz 有一轮因 rare-queue 逻辑卡住，另外两轮产生极高覆盖。branch mask 的定向阶段目标分支命中率很高，havoc 阶段约提高 3–10 倍。原文 §§4.1–4.2、Table 2。
- **重要反例/边界：** 9 个程序中只有 `c++filt` 和 `readelf` 找到崩溃。`c++filt` 上 FairFuzz 仅 25% runs 找到 crash，AFL 85%，FidgetyAFL/AFLFast.new 各 100%；FairFuzz 找到 crash 的少数运行要约 10 小时，对照 FidgetyAFL 少于 2 小时。作者推测超长输入和路径/分支建模是原因。原文 §4.3。FairFuzz 也无法优先引导从未被任何 AFL 种子命中的分支；单个多字节比较没有逐字节 coverage 时尤其难。原文 §5。
- **可复核来源：** [原文 §§3–5](https://arxiv.org/html/1709.07101)。
- **判断：** 这篇提供了“优化中间机制指标、但下游目标指标退步”的机制级实例。不能从中概括 FairFuzz 总体无效；后续 FuzzBench 对比又显示排名随 crash/bug 指标而变。

### 2. Deep Bayesian Active Learning for NLP：系统性正结果，但外部验证规模有限

- **版本/出版：** arXiv:1808.05697v3，2018；NLP/active learning。
- **研究问题与机制：** 新任务中不能先耗尽标注预算比较多个 acquisition function。研究 MC Dropout 与 Bayes-by-Backprop 的 disagreement acquisition（DO-BALD、BB-BALD），对照经典不确定性采样和 i.i.d. 随机抽样。
- **实验：** 三类任务——句子分类、命名实体识别、语义角色标注；每类两个数据集。初始随机 warm start 为 2%，之后每轮新增 2%，最高标注到 50%；每个配置用 3 个 warm-start seed。作者总结为 40 多个实验、约 25 轮/实验、约 3,000 次完整训练。原文 §§3–4。
- **主要结果：** 所测 AL 方法在所有设置中超过随机 i.i.d.；DO-BALD/BB-BALD 通常超过经典 uncertainty sampling，但个别差距很小。NER 上约使用 20% 样本达到全量数据性能的 98–99%；随机 i.i.d. 约需 50% 数据达到相近 F-score。原文 §3.6、§4。
- **边界：** acquisition functions 只研究 uncertainty-based 家族；实验依赖旧一代 NLP 架构/数据集，每配置仅 3 个随机起点。论文将不调参、避免全标签泄漏列为目标，但不能自动外推到当前大模型、长尾数据或实际标注者成本；词数预算与句子预算也因任务而异。
- **可复核来源：** [原文 §§3–4](https://arxiv.org/html/1808.05697)。
- **判断：** 对“主动学习是否普遍优于随机抽样”，这是一项跨任务支持较广的历史基线，不是无条件证明 Bayesian disagreement 始终最好。下一步应查新模型下的外部复现及 acquisition/标注成本的同预算比较。

### 3. iFogSim 与 YAFS：同一策略的仿真数字会随建模约定改变

- **版本/出版：** iFogSim arXiv:1606.02007（2016）；YAFS arXiv:1902.01091v1（2019）；分布式/边缘系统。
- **iFogSim 研究内容：** 提供 IoT–fog–cloud 离散事件模拟框架，以 EEG 游戏和分布式摄像头为案例比较 cloud-only 与 edge-ward placement。论文报告 edge-ward 能降低控制环延迟、网络用量和云数据中心能耗，同时略增边缘设备能耗；还在 4–64 个传感器手机、1–16 个网关范围内测模拟器 footprint。原文 §§5–6。
- **独立交叉核对：** YAFS 用 iFogSim 的 EEG 游戏模型实现同样两种 placement，改变 fog 节点规模，并分析 execution time/response time。作者指出两模拟器结果并不相等，尽量匹配仍有 MIPS vs IPT、链路带宽/传播时延表示及消息/事件定义差异；在 edge policy 下报告两个模拟器的 latency 估计较稳定，但 cloud policy 下网络饱和会使模拟结果和模拟器运行时间发生变化。原文 §4、Tables 2–3。
- **实验限制：** YAFS 三个动态扩展场景（动态分配、设备故障、用户移动）没有真实 trace；作者明确说使用任意分布/参数来表现预期行为，且无法与真实案例比较。原文 §5。两篇均是仿真验证，不是生产系统的能耗测量。
- **可复核来源：** [iFogSim §§5–6](https://arxiv.org/html/1606.02007)；[YAFS 原文 §§4–5](https://arxiv.org/pdf/1902.01091)。
- **判断：** 这里不仅有“模拟结果可能和现实不同”的一般提醒，更有一次跨模拟器的同策略对照：策略趋势可相近而数值不一致，且作者具体指出参数语义映射问题。适合形成配对验证问题，但尚不足以说 placement 排名必然反转。

### 4. AI Safety Gridworlds 与现代 safe-RL 评测：安全评分依赖保留哪些 run、测哪个策略

- **版本/出版：** AI Safety Gridworlds arXiv:1711.09883v2（2017）；Evaluation Metrics for Safe Reinforcement Learning arXiv:2609.15315v1（2026）；安全强化学习。
- **早期基准的设计/结果：** Gridworlds 构造 specification 与 robustness 两类玩具环境，用 agent 可见 reward 和隐藏 safety-performance function 的差距来显露 reward gaming、side effects、supervisor absence 等问题。A2C/Rainbow 在若干任务能学到高可见 reward，却没有获得相应高 safety performance。训练 20 seeds 后，作者剔除表现最差的 25% 以减小方差，因此主图展示剩余 15 个 seeds 的平均结果。原文 §§1、3.1–3.2。
- **现代评测的补充：** 2026 年 SafeRLEval 论文在 4 个 safety-navigation tasks × 3 个 bounds × 4 个算法上跑 30 seeds；同时报告平均成本、违规频率、违规幅度和成本分布，并分别评估训练中的带噪策略与最终 greedy policy。论文展示最终 greedy 策略与带探索噪声的安全分布可显著不同。一个具体指标例子：训练中 FOCOPS 违规率 IQM 优于 PPO-Lag，但因 normalized mean-cost deviation 略高于 0 被分到 Tier 0，而 PPO-Lag 到 Tier 2；单一“最安全算法”排序因此随指标定义改变。原文 §§3–4、Appendix A.1。
- **证据边界：** 两论文环境、算法、目标和年代完全不同，不是直接 benchmark replication。Gridworlds 的剔除是为降低 A2C 不稳定性方差，并非作者声称估算部署尾部风险；SafeRLEval 只研究四个 task、三个安全 bound，且局限于训练期允许违规、渐近/近似满足约束的算法。2026 结果不证明 2017 结论错误。
- **可复核来源：** [AI Safety Gridworlds §§1、3](https://arxiv.org/html/1711.09883)；[Safe-RL evaluation §§3–5、Appendix A.1](https://arxiv.org/html/2609.15315)。
- **判断：** 一个未被充分拆开的评价选择是：报告平均学习表现时是否应删掉差 run，能否同时回答“典型算法表现”与“安全失败风险”。可直接做全 seeds vs trimmed seeds 的敏感性分析，报告违规概率和尾部严重度，而非只比均值。

## 抽样框审计中的时间边界

抽样框的时期按 arXiv 首次提交日期分层，不是会议/期刊首次发表日期。比如候选 `1106.0235` 的 arXiv 上传为 2011 年，但元数据所列 JAIR 发表年为 2000 年。它本身在本批只用于核验年份错位，不计作已完成全文审阅。后续“十几年进展”需再按 venue 年份重排，并用引用链纳入 arXiv 之外的早期基础论文。

## 本批结论和下一批规则

这一批给出四个具体证据模式：fuzzing 的内部覆盖代理可能与崩溃目标分离；active learning 的积极趋势仍受模型/数据/seed 范围限制；fog placement 的效果数值受模拟器参数语义与校准数据影响；安全 RL 的算法排序依赖 seed 保留规则、评测阶段和安全聚合指标。它们是不同学科的研究线索，不应拼成一个宏大统一结论。下一批继续按子领域与发表年份分层，同时追支持、反例和“不支持”的结果；随机组用于筛选精度核验，词法优先组用于找高信息量案例，两者分开计数。
