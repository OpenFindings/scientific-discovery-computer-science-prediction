# 全文审查批次 7：2020–2024 随机样本与结果条件核查

审查日期：2026-10-11。以下三篇均来自固定抽样框 `data/fulltext_stratified_sample.jsonl` 的 2020–2024 uniform-random arm，分属软件供应链、机器人安全和持续学习三个子领域。

## 1. Towards Measuring Supply Chain Attacks on Package Managers for Interpreted Languages（arXiv:2002.01139v2；随机样本；NDSS 2021）

- §§III–IV：MALOSS 把元数据、静态和动态分析组合成筛选管线，作者迭代人工核验可疑包；对 PyPI、npm、RubyGems 报告 339 个新恶意包，注册表维护者确认并移除 278 个（82%），其中 3 个包超过 10 万下载并获 CVE。这个数是经人工核验并获维护方处置的一批发现，不是对三大生态恶意包总量的无偏估计。
- §V-B：作者明确说目标是严重性/流行度测量，不是高覆盖、高鲁棒程序分析；管线的静态分析不准确、动态分析覆盖有限且容易规避。范围只包括对应语言源文件，排除 native extensions、嵌入二进制和其他语言；动态分析只在 Ubuntu 16.04，忽略开发依赖。反射、动态代码生成和基于已知攻击规则的人工核验都会造成漏报。
- 解释边界：82% 是维护者对已报告候选的确认/移除比例，不是精确率的随机估计；未被发现的恶意包、环境不匹配与攻击者规避均不在该比例分母里。

## 2. Simulation-based Testing for Early Safety-Validation of Robot Systems（arXiv:2011.10294v1；随机样本）

- §§III–IV：系统用 Monte Carlo Tree Search 控制简化的人体模型，在 CoppeliaSim 中搜寻违反“机器人运动时人机不得接触”的状态。人体动作仅 30 种走路/上身组合，不含手臂动作；臂部可达性用静态 octree 近似。示例人为设置了 3 个安全缺陷场景，每个算法/场景 10 个随机种子、最多 200 个 episode。
- Table III：Random 搜索在三个场景分别找到 hazard 3/10、3/10、8/10；两个 MCTS 变体为 10/10、8/10、10/10 和 10/10、9/10、10/10。发现所需 episode 也更少。不过样本仅 3 个刻意构造场景；两种 MCTS 之间没有清晰优劣，作者认为测试场景数太少。
- §§V–VII：只做 falsification，找到反例不能证明系统安全；一次只能找一个 hazard，需修复后重跑。简化人体模型、静态手臂工作空间、未建模碰撞力及单一模拟器都是边界。

## 3. Coresets via Bilevel Optimization for Continual Learning and Streaming（arXiv:2006.03875v2；随机样本）

- §6、Table 1：在任务式 continual-learning 评估里，coreset 对 SplitMNIST 的平均任务准确率为 95.87±0.20，uniform 为 92.80±0.79；SplitCIFAR-10 为 37.60±2.41 对 36.20±3.19。表中结果各为 5 次运行。
- §6.3：收益依赖数据流。作者明确报告，buffer=200 的 CIFAR-10 streaming 上 coreset 没有胜过 reservoir sampling；但在他们构造的任务严重不均衡流上，SplitMNIST 为 92.30±0.23，对比 reservoir 80.60±4.36、class-balancing reservoir 89.71±1.31；SplitCIFAR-10 为 33.98±1.69，对比 27.22±1.24 和 32.25±1.69。
- 附录 E：每种 continual/streaming 方法按“测试集上最佳”的 buffer regularization strength β 报告结果。这带来测试集参与调参的潜在乐观偏差；不能据此判定结论失效，但独立评估应冻结验证集选择、只用最终测试集一次。
- 其他边界：实验主要是 PermMNIST、SplitMNIST、SplitCIFAR-10 与特定网络/记忆预算；NTK proxy 在 CIFAR-10 较复杂数据上比 RBF 更合适，RBF 在简单 MNIST 派生任务有效但在更难 CIFAR-10 失败。coreset 大小增加时生成成本非线性上升；论文测得从 1,000 点选 400 个 coreset 的生成耗时约 187–189 秒（其特定 GTX 1080 Ti + 单 CPU 设置）。

## 跨条件可证伪问题：记忆选择收益是否取决于数据流状态，而且常被调参协议放大？

在相同模型、缓冲区大小和在线训练预算下，预注册任务平衡/不平衡、stationary/shifted、MNIST/CIFAR 类难度；比较 bilevel coreset、reservoir 与 class-balanced reservoir。只在独立验证流上选择 β/proxy，测试流完全不参与调参；至少报告最终精度、逐任务最差精度、遗忘、记忆构建时间和方差。主要检验：不均衡流下 coreset 的优势是否仍在；平衡 CIFAR 类流下是否仍不优于 reservoir；采用无泄漏调参后效应量收缩多少。该问题与更广泛的“记忆策略跨任务/数据条件的迁移”相关，但当前这里只审计了一项基准论文，尚非系统综述或已证实的新颖性。
