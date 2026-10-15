#!/usr/bin/env python3
"""Build the bilingual, label-free Paper 3 human-labeling export.

The export is assembled only from frozen eligible source-screen records and
their linked later-evidence ledgers. Original records are read-only inputs;
missing evidence remains an empty evidence list and is never converted into a
negative label.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "paper3_labeling_questions.json"

QZH: dict[tuple[str, str], tuple[str, str]] = {
    ("BLIND", "1801.07379v1"): (
        "在隐蔽攻击或内部攻击下，当在线效用估计受到扰动时，移动众感知保护策略能否在保护成本相同的情况下保持安全效用，相比之下不采用鲁棒性处理的策略如何？",
        "在指定攻击和估计误差分布下，如果在保护成本匹配时安全效用没有改善，则不能支持所提出的鲁棒性收益。",
    ),
    ("BLIND", "1802.07361v1"): (
        "在相同源测试预算下，相比行覆盖、分支覆盖和随机生成，弱变异源测试方法在更大代码库上的优势是否仍然存在？",
        "在独立的较大代码库单元和相同测试预算下，如果无法重复验证其对独立确认的不同故障检测优势，则不能支持这一更窄的推广；仅有变异体杀死率属于代理指标。",
    ),
    ("BLIND", "1807.07619v1"): (
        "按照论文对图和允许修改权重的定义，以修改边的数量为参数时，一般图度量修复问题是否为 W[2]-困难？",
        "在相同参数和定义下，如果存在一个有效的固定参数算法，则不支持该困难性猜想；如果给出保持参数的正确 W[2]-困难归约，则直接支持该猜想。",
    ),
    ("BLIND", "1811.10861v1"): (
        "在相同的天文流式处理和历史查询负载下，自动跨存储系统的数据重新分布能否在满足原始摄取延迟目标的同时，相比固定布局降低查询延迟？",
        "在冻结的独立负载和相同资源下，如果查询延迟没有优势，或违反摄取延迟目标，则不能支持联合收益主张。",
    ),
    ("BLIND", "1905.04752v1"): (
        "在独立确认的 Scala 内存泄漏上、审查预算匹配时，语义感知的静态检测器能否在假阳性不增加到不可接受程度的情况下，比仅使用语法或模式的分析发现更多真实泄漏？",
        "在预先规定的假阳性上限和留出项目上，如果没有独立验证的召回率提升，则不能支持该主张。",
    ),
    ("BLIND", "1910.05923v1"): (
        "在训练数据和计算资源匹配时，语法约束是否能在不降低任务正确性的情况下，相比该双任务模型提高可解析代码和测试通过代码的生成效果？",
        "在预算匹配时，即使可解析性更高，如果留出任务的任务正确率或测试通过率没有收益，则不能支持实质性主张。",
    ),
    ("BLIND", "1912.01990v1"): (
        "在论文的图和分解假设下，Hamiltonian Index 能否使用严格更优的树宽指数底数计算？",
        "针对指定模型和底数，匹配的条件下界不支持更快算法分支；正确的更快算法支持该分支。仅有运行时间实验不足以解决该理论问题。",
    ),
    ("BLIND", "2004.11573v1"): (
        "在训练样本数量和计算量相同的情况下，使用非常规不确定性对抗样本训练，能否相比常规对抗训练提高留出数据上的鲁棒准确率，同时不造成实质性的干净准确率下降？",
        "如果留出数据上的鲁棒性没有优势，或干净准确率下降超过预先规定的程度，则不能支持所提出的收益。",
    ),
    ("BLIND", "2005.07992v1"): (
        "数据库内的函数依赖表能否在基表更新下保持正确，并且相比每次更新后重新挖掘函数依赖，降低更新加查询的总成本？",
        "在冻结的更新/查询轨迹上，如果增量实现给出错误的函数依赖答案，或相对于匹配的完整重新挖掘基线没有测得成本优势，则不能支持该主张。",
    ),
    ("BLIND", "2010.14077v1"): (
        "基于格的带相等性测试的身份基加密方案，能否在保持灵活授权的同时，满足精确定义的 CCA2 安全性？",
        "在所声称的 CCA2 游戏下，对所提出构造的有效攻击会否定该构造；对于明确定义的构造，完整安全归约只能在其明确假设下支持正面结论。",
    ),
    ("BLIND", "2103.05704v1"): (
        "在独立招募的终端用户开发者和匹配的应用任务中，草图到 App Inventor 的生成是否相对于手工实现提高界面保真度并缩短完成时间？",
        "在独立的匹配任务评估中，如果预先规定的保真度或时间优势不存在，则不能支持该推广主张。",
    ),
    ("BLIND", "2106.00714v1"): (
        "在该论文的加权图设定下，能否将其代数框架扩展为计算三个最短不相交环，并给出有证明的并行界限？",
        "对所提出的三个环扩展给出正确反例会否定该扩展；在指定假设和界限下给出完整证明的算法则支持它。相关的两个环结果不能解决该问题。",
    ),
    ("BLIND", "2109.08630v1"): (
        "在隐私预算和数据相匹配时，交互式 GNMAX 投票是否会因为选择效应而产生不同于非交互式 PATE 聚合的组间过度风险差异？",
        "在隐私和选择过程核算相匹配的独立数据集上，如果无法重复观察组间差异，则不能支持该效应主张。",
    ),
    ("OBSERVABLE", "1703.00768v1"): (
        "在留出的工业软件项目上，在训练预算匹配时，向 CAM 的基于日志的测试告警分类器加入软件制品，是否比仅使用日志的 CAM 提高独立验证的故障原因分类准确率？",
        "如果在可比的标注/训练预算下，留出项目级准确率没有可重复提升，或收益仅限于已经见过的项目，则不能支持推广和制品价值主张。",
    ),
    ("OBSERVABLE", "1706.02214v1"): (
        "对于论文的拉伸耦合任务最大完工时间问题，当兼容图是最大度有界的树时，其精确计算复杂度是什么？",
        "针对有界度树情形的正确多项式算法或困难性证明，可以解决相应分支；针对不同兼容图或任务模型的定理不能解决该问题。",
    ),
    ("OBSERVABLE", "1708.03786v1"): (
        "在真实的入门编程课程中，经过多次调试尝试后，TraceDiff 相对于匹配的 Python Tutor 工作流，是否提高独立验证的修复完成率或缩短修复时间？",
        "如果在独立学生/任务上，预先规定的已验证修复率或时间没有提升，或在迭代尝试下收益消失，则不能支持推广；仅有偏好评分不构成修复结果。",
    ),
    ("OBSERVABLE", "1712.09136v1"): (
        "对于单次查询 PDTP 较低的记录，对同一分类器发起多次选定查询，能否在固定查询预算下相对于单次直接查询基线提高成员推断准确率？",
        "在预先规定的查询预算和独立模型/数据单元上，如果无法重复观察多查询攻击优势，则不能支持这一经验性担忧；在明确假设的范围内证明匹配的上界，也可以在该范围内反驳它。",
    ),
    ("OBSERVABLE", "1802.06026v1"): (
        "对于具有 s 个标签和交叉数参数 k 的 Zero Extension 精确度量稀疏器，最坏情况下稀疏器大小的指数是否必须随 s 增长，还是可以存在与 s 无关的指数？",
        "在来源定义下有效的 k^Ω(s) 最坏情况下界会反驳指数与 s 无关的可能性；有效的、指数与 s 无关的 k^O(1) 上界会反驳增长的必要性。仅针对 s-Multiway Cut 或不同稀疏器定义的界限不能解决该问题。",
    ),
    ("OBSERVABLE", "1805.02751v2"): (
        "对于预先登记的一组联网儿童玩具，自动化的策略到属性审计能否在不增加假阴性的情况下，恢复独立人工分析发现的同一批可客观验证的隐私和网络安全违规，并减少分析人员投入？",
        "如果自动化相对于人工审计的召回率实质性更低、假阳性超过预先规定的幅度，或审查含糊策略语言后分析时间节省消失，则自动化失败。漏洞数量更多本身不是成功标签。",
    ),
    ("OBSERVABLE", "1806.03283v1"): (
        "在总 CPU 资源匹配时，在相同墙钟时间预算内，并行化 Badger 是否在留出的 Java 被测对象上比独立的成本引导模糊测试器生成更高的最坏情况资源成本输入？",
        "在总 CPU 匹配时，如果留出数据上没有一致的成本优势，或当两组并行度相当时优势消失，则不能支持资源公平收益主张；仅在来源的不等核心设置下获得显著优势不算数。",
    ),
    ("OBSERVABLE", "1903.05387v1"): (
        "在受约束的虚拟机配置空间中，与无约束的 t-way 生成相比，加入求解器支持的约束处理是否能减少无效或冗余测试执行，同时保持或提高无效配置的检测率？",
        "如果在检测召回率不劣的情况下没有减少无效/冗余执行，或在留出的配置模型上收益消失，则实际价值主张被否定。只有框架实现而没有匹配比较，只能算部分进展。",
    ),
    ("OBSERVABLE", "1905.02597v1"): (
        "对于来自同一修复机器人的自动修复建议，在补丁正确性和审查工作量匹配时，附加自然语言解释及具体行为差异示例，是否相比仅提供补丁提高盲审接受率或缩短决策时间？",
        "如果在独立审查者和补丁单元上，预先规定的接受率或决策时间/理解结果没有改善，或控制补丁正确性后出现惩罚，则不能支持沟通收益；没有决策或理解端点的主观偏好不足以作出结论。",
    ),
    ("OBSERVABLE", "2003.02892v1"): (
        "对于具有软件更新和对抗流量情形的异构智能家居设备，协作式白名单学习能否收敛到稳定的允许连接集合，同时将误阻断和攻击者注入的允许项控制在预先规定的阈值以下？",
        "如果在预先规定的时间范围内没有收敛，或误阻断或攻击者允许项任一指标相对于基线超过固定安全裕度，则该主张失败。仅有概念验证吞吐量结果不能解决策略正确性。",
    ),
    ("OBSERVABLE", "2005.00972v1"): (
        "在留出的 DNN 修复实例上，相对于仅使用代码信息的修复基线，DNN 感知的修复/定位干预能否减少错误补丁或引入漏洞的补丁，同时保持已验证的缺陷修复成功率？",
        "如果在修复成功率不劣的情况下，独立验证的回归没有减少，或在项目划分评估下收益消失，则不能支持 DNN 感知价值主张。数据集频率本身不是结果。",
    ),
    ("OBSERVABLE", "2007.03275v1"): (
        "安全模式检查方法能否从依赖 UML 时序图的 Web 应用推广到没有这些图或没有相应模式的应用，并通过代码注释保持独立验证的行为属性检测精确率和召回率？",
        "如果精确率或召回率超出预先规定的下降幅度、注释无法独立检查，或结果依赖于设计表示时使用过的同一项目，则推广失败。没有匹配表示比较的更多应用示例并不具有决定性。",
    ),
    ("ROUND6", "1707.09038v3"): (
        "在 Android 应用测试套件和植入的 Android 故障上，Android 专用变异算子是否相对于来源指定的传统算子/工具，提高故障表示能力并减少无意义或无效变异体？",
        "如果在留出的应用/故障集合上，Android 专用算子没有超过来源指定替代方案的预定故障表示率或无意义/无效变异体端点，则该主张失败。",
    ),
    ("ROUND6", "1712.09136v1"): (
        "DTP-1 指标能否在固定数据集和攻击协议下预测成员攻击成功率，并区分应当避免发布的风险分类器？",
        "如果 DTP 不能预测攻击成功率，或在固定数据集和攻击协议下无法区分发布风险案例，则 DTP-1 主张失败。",
    ),
    ("ROUND6", "1806.03283v1"): (
        "在相同程序、预算和成本核算下，Badger 混合方法是否比仅模糊测试的 KelinciWCA 和仅符号执行的 Symbolic PathFinder 更快生成最坏情况执行，并产生更多提高资源成本的执行？",
        "如果在匹配条件下没有改善来源指定的最坏情况端点，或在指定基准上无法重复，则 Badger 主张失败。",
    ),
    ("ROUND6", "1901.02771v1"): (
        "在固定公开基准实例上，结构化时间窗的扫掠算法扩展是否相对于来源指定的扫掠/基线启发式，保持或改善每个实例的目标值和可行性？",
        "如果在固定基准集上，结构化扫掠扩展没有改善或保持预先规定的目标值/可行性端点，则该扩展失败。",
    ),
    ("ROUND6", "1903.06407v2"): (
        "对于含有内联汇编的 C 程序，TInA 的验证导向提升表示是否能在每个内联汇编单元上保持语义等价和后续验证成功率？",
        "如果在固定的 GMP/ffmpeg 单元上无法保持语义等价或验证成功率，或收益需要未报告的人工修正，则 TInA 失败。",
    ),
    ("ROUND6", "2004.04211v1"): (
        "在固定开源项目测试套件上，四种空类型变异算子相比传统变异算子，是否能发现额外的、与空故障相关的缺失测试？",
        "如果在固定项目上，空类型算子没有在来源给定的权衡阈值下揭示额外的空故障相关缺失测试，则该主张失败。",
    ),
}

DOMAIN = {
    "1801.07379v1": "security_privacy", "1802.07361v1": "software_testing",
    "1807.07619v1": "algorithms_complexity", "1811.10861v1": "databases",
    "1905.04752v1": "program_analysis", "1910.05923v1": "ai_generated_code",
    "1912.01990v1": "algorithms_complexity", "2004.11573v1": "ai_robustness",
    "2005.07992v1": "databases", "2010.14077v1": "security_privacy",
    "2103.05704v1": "ai_generated_code", "2106.00714v1": "algorithms_complexity",
    "2109.08630v1": "security_privacy", "1703.00768v1": "software_testing",
    "1706.02214v1": "algorithms_complexity", "1708.03786v1": "software_testing",
    "1712.09136v1": "security_privacy", "1802.06026v1": "algorithms_complexity",
    "1805.02751v2": "security_privacy", "1806.03283v1": "software_testing",
    "1903.05387v1": "software_testing", "1905.02597v1": "program_repair_verification",
    "2003.02892v1": "security_privacy", "2005.00972v1": "program_repair_verification",
    "2007.03275v1": "security_privacy", "1707.09038v3": "software_testing",
    "1901.02771v1": "algorithms_complexity", "1903.06407v2": "program_repair_verification",
    "2004.04211v1": "software_testing",
}

ROUND6_EN = {
    "1707.09038v3": "On the source's Android application/fault-artifact corpus, do Android-specific mutation operators improve fault representation and reduce stillborn/trivial mutants relative to the source-pinned traditional mutation operators and tools?",
    "1712.09136v1": "Does the source's DTP-1 metric predict membership-attack success and distinguish classifier release-risk cases on the fixed datasets and attack protocol?",
    "1806.03283v1": "At matched program, budget and cost accounting, does hybrid Badger generate worst-case executions faster and produce more resource-cost-increasing executions than fuzzing-only KelinciWCA and symbolic-execution-only Symbolic PathFinder?",
    "1901.02771v1": "On the fixed public benchmark instances, do the structured-time-window sweep extensions improve or preserve objective value and feasibility relative to the source-pinned sweep and baseline heuristics?",
    "1903.06407v2": "For C programs containing inline assembly, does TInA's verification-oriented lifted representation preserve semantic equivalence and downstream verification success on each inline-assembly unit?",
    "2004.04211v1": "On the fixed open-source project test suites, do the four null-type mutation operators reveal additional null-fault-relevant missing tests relative to traditional mutation operators?",
}

EVIDENCE_ZH = {
    "Evaluating Explanations for Software Patches Generated by Large Language Models": (
        "大型语言模型生成的软件补丁解释评估",
        "部分进展而非直接解决：在 30 个缺陷上，GPT-3.5 对机器生成补丁的解释在三次运行至少一次中有 84% 正确、54% 完整；这是人工内容评估，没有仅补丁控制组，也没有采用率、决策时间或理解任务端点。",
    ),
    "DeepDiagnosis: Automatically Diagnosing Faults and Recommending Actionable Fixes in Deep Learning Programs": (
        "DeepDiagnosis：自动诊断深度学习程序故障并推荐可执行修复",
        "部分进展和范围收窄：DeepDiagnosis 优于列出的故障定位基线并提供可执行建议，但明确没有执行自动修复；其未来工作包括自动修复和更多故障类型。",
    ),
    "Repairing DNN Architecture: Are We There Yet?": (
        "修复 DNN 架构：我们已经做到哪一步？",
        "部分进展但端点不同：随机搜索在部分情形下可与或优于现有修复方法，所有测试技术在更大、更复杂模型上都失败；该端点是模型性能修复，不是冻结问题中的引入漏洞/安全回归。",
    ),
    "Mining Historical Test Logs to Predict Bugs and Localize Faults in the Test Logs": (
        "挖掘历史测试日志以预测缺陷并定位测试日志中的故障",
        "独立工业日志基线上的部分进展和明确范围收窄：独立团队在 Ericsson 故障日志上重实现 CAM，报告 K=15 时产品故障 FaultsFound 为 50%；但任务改成了二元产品故障检测和故障行定位，没有加入测试脚本或其他制品，也没有评估留出项目级多类原因准确率或匹配标注/训练预算。",
    ),
    "HotFuzz: Discovering Algorithmic Denial-of-Service Vulnerabilities Through Guided Micro-Fuzzing": (
        "HotFuzz：通过引导式微模糊测试发现算法拒绝服务漏洞",
        "仅支持广义成本引导测试前提的独立证据：作者评估了 JRE、STAC 挑战和 100 个 Maven 库中的引导式微模糊测试，并报告不同种子策略下的算法复杂度见证和确认案例；没有进行匹配 CPU 的 Badger 与独立 KelinciWCA 比较。",
    ),
    "Label-Only Membership Inference Attacks": (
        "仅标签成员推断攻击",
        "多查询组成部分的部分进展：通过多次策略性扰动标签查询进行成员推断；在报告的 CIFAR-10 设置下，若干三查询或四维加一查询攻击以及更大预算的边界攻击在部分设置超过单标签差距基线，但没有报告 PDTP 值或低 PDTP 子组分析。",
    ),
    "Sampling Attacks: Amplification of Membership Inference Attacks by Repeated Queries": (
        "采样攻击：通过重复查询放大成员推断攻击",
        "仅支持多查询机制：重复扰动标签查询被聚合为攻击特征；精确首发时间可能早于 arXiv v1，因为论文注明了 2019 年 workshop 版本，但两种日期都在窗口内。它不是对低 PDTP 子组的匹配测试，也不作为单独的独立结果单元。",
    ),
    "Making Interactions With Home IoT Devices More Secure, Private, and Usable": (
        "让家庭物联网设备交互更安全、更私密且更易用",
        "范围收窄而非直接解决：后续工作指出 SERENIoT 从观察行为创建允许列表，但没有研究流量数据或策略如何跨设备泛化，并将部署差异列为问题。",
    ),
    "Avocado: Open-Source Flexible Constrained Interaction Testing for Practical Application": (
        "Avocado：用于实际应用的开源灵活约束交互测试",
        "计划中的约束处理取得部分进展：后续工作描述了求解器支持、约束测试套件生成、执行和工业应用，但没有验证来源问题要求的匹配基线比较。",
    ),
    "Workload-driven, Lazy Discovery of Data Dependencies for Query Optimization": (
        "面向查询优化的工作负载驱动惰性数据依赖发现",
        "近似匹配而非直接解决：Hyrise 原型发现 UCC、FD 和 OD 元数据并报告发现后查询执行时间改善，但没有在冻结测试中验证更新期间可查询 FD 表的正确性，也没有匹配的更新加查询成本比较。",
    ),
    "Guiding the retraining of convolutional neural networks against adversarial inputs": (
        "引导卷积神经网络针对对抗输入进行再训练",
        "近似匹配而非直接解决：后续研究了标准攻击生成的对抗输入的基于不确定性的排序，没有使用来源的非常规不确定性生成器，也没有在样本数和计算量相同下与常规对抗训练比较，因此没有给出冻结问题的直接正面或负面结果。",
    ),
    "Generalized Metric Repair on Graphs": (
        "图上的广义度量修复",
        "相邻的后续结果而非直接解决：该论文给出更强的近似困难性和固定常数弦图上的固定参数算法，但没有给出一般图、按修改边数参数化的 W[2]-困难性定理。",
    ),
    "Packing Short Cycles": (
        "短环打包",
        "相邻进展而非直接解决：该结果处理加权无向图上固定 k 的无标记最小总权顶点不相交环打包；来源问题要求经过指定标记顶点，且算法边界不同。",
    ),
    "MDroid+: A Mutation Testing Framework for Android": (
        "MDroid+：Android 变异测试框架",
        "相邻/延续而非精确匹配：应用集合、算子集合和冻结端点元组不同，不能提供来源问题的直接标签。",
    ),
    "Hybrid Differential Software Testing": (
        "混合差分软件测试",
        "相邻结果而非精确匹配：对象和端点是差分测试，不同于冻结的最坏情况复杂度比较。",
    ),
    "TInA ASE 2019 artifact/publication record and later primary presentation record": (
        "TInA ASE 2019 制品/出版记录及后续主要展示记录",
        "同一研究线记录而非端点匹配的后续结果；没有找到独立的精确比较。",
    ),
    "later public replication-package record for the null-type mutation study": (
        "空类型变异研究的后续公开复现包记录",
        "同一研究的相邻记录；没有找到独立日期的精确比较结果。",
    ),
    "dated primary routing/structured-time-window follow-up records were found, but none used the same linked benchmark, sweep comparator, and objective tuple": (
        "已找到有日期的路由/结构化时间窗后续主要记录，但没有一项使用相同的关联基准、扫掠比较器和目标元组",
        "没有精确匹配：发现了有日期的相关记录，但没有使用相同的基准、扫掠比较器和目标元组，因此不能提供冻结问题的直接标签。",
    ),
}


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def read_source_rows(pattern: str) -> dict[str, dict]:
    import glob
    rows: dict[str, dict] = {}
    for path in sorted(ROOT.glob(pattern)):
        doc = json.loads(path.read_text(encoding="utf-8"))
        for row in doc.get("rows", []):
            if row.get("question_status", "").startswith("eligible"):
                rows[row["versioned_id"]] = row
    return rows


def source_meta() -> dict[str, dict]:
    rows = {}
    for path in [ROOT / "data/historical_cs_blind_cohort_20.jsonl", ROOT / "data/historical_cs_observable_cohort_16.jsonl"]:
        for row in load_jsonl(path):
            rows[row["versioned_id"]] = row
    return rows


def evidence_from_trajectory() -> dict[str, list[dict]]:
    doc = json.loads((ROOT / "reports/historical_evidence_trajectory_round2.json").read_text(encoding="utf-8"))
    out = {}
    for row in doc["rows"]:
        items = []
        for e in row.get("evidence", []):
            title = e["title"]
            zh = EVIDENCE_ZH.get(title)
            if not zh:
                raise ValueError(f"missing evidence translation: {title}")
            items.append({
                "title": title,
                "title_zh": zh[0],
                "url": e.get("primary_fulltext_url", e.get("first_public_url")),
                "date": e.get("first_public_date"),
                "relationship": f"{e.get('directness', 'later evidence')}: {e.get('observed_claim', '')}",
                "relationship_zh": zh[1],
            })
        out[row["versioned_id"]] = items
    return out


def make_record(cohort: str, row: dict, meta: dict, evidence: list[dict]) -> dict:
    sid = row["versioned_id"]
    question = row.get("candidate_question", row.get("question", ROUND6_EN.get(sid)))
    criterion = row.get("candidate_falsification", row.get("falsification_gate", row.get("falsification_condition")))
    if not question or not criterion:
        raise ValueError(f"eligible row missing question/criterion: {cohort} {sid}")
    qzh, czh = QZH[(cohort, sid)]
    return {
        "question_id": f"{row.get('cohort_id', 'PAPER3-DIRECT-ENDPOINT-COHORT-ROUND6-001')}__{sid}",
        "source_paper_id": sid,
        "source_url": row.get("source_pdf_url", row.get("source_url", meta.get("source_pdf_url"))),
        "source_as_of": row.get("as_of", row.get("cutoff", meta.get("as_of"))),
        "followup_end": row.get("three_year_followup_end", row.get("five_year_followup_end", row.get("followup_end", meta.get("three_year_followup_end", meta.get("five_year_followup_end"))))),
        "domain": DOMAIN[sid],
        "question": question,
        "question_zh": qzh,
        "criterion": criterion,
        "criterion_zh": czh,
        "evidence": evidence,
    }


def round6_records() -> list[dict]:
    doc = json.loads((ROOT / "reports/paper3_direct_endpoint_cohort_round6.json").read_text(encoding="utf-8"))
    eligible = {row["versioned_id"]: row for row in doc["source_screen"]["eligible"]}
    coverage = {row["versioned_id"]: row for row in doc["followup_audit"]["coverage_rows"]}
    out = []
    for sid, row in eligible.items():
        ev = []
        c = coverage.get(sid)
        if c:
            title = c["primary_record"]
            date = None
            if sid == "1707.09038v3":
                title, date = "MDroid+: A Mutation Testing Framework for Android", "2018-02-13"
            elif sid == "1806.03283v1":
                title, date = "Hybrid Differential Software Testing", "2021"
            elif sid == "1903.06407v2":
                date = "2019"
            zh = EVIDENCE_ZH.get(title)
            if not zh:
                raise ValueError(f"missing round6 evidence translation: {title}")
            ev.append({
                "title": title,
                "title_zh": zh[0],
                "url": c["url"],
                "date": date,
                "relationship": c["classification"],
                "relationship_zh": zh[1],
            })
        out.append(make_record("ROUND6", row, {}, ev))
    return out


def main() -> int:
    meta = source_meta()
    blind = read_source_rows("reports/historical_source_screen_round*.json")
    observable = read_source_rows("reports/historical_observable_source_screen_round*.json")
    trajectory_evidence = evidence_from_trajectory()

    # Two blind-cohort follow-up audits contain authenticated, date-bounded
    # near-matches whose titles and relationships are recorded explicitly.
    blind_evidence = {
        "2004.11573v1": [{
            "title": "Guiding the retraining of convolutional neural networks against adversarial inputs",
            "title_zh": EVIDENCE_ZH["Guiding the retraining of convolutional neural networks against adversarial inputs"][0],
            "url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC10495969/",
            "date": "2023-08-08",
            "relationship": "Near-match only: the dated follow-up studies uncertainty-guided ordering of adversarial inputs generated by standard attacks; it does not use the source's uncommon-uncertainty generator or compare equal example count and compute against conventional adversarial training.",
            "relationship_zh": EVIDENCE_ZH["Guiding the retraining of convolutional neural networks against adversarial inputs"][1],
        }],
        "2005.07992v1": [{
            "title": "Workload-driven, Lazy Discovery of Data Dependencies for Query Optimization",
            "title_zh": EVIDENCE_ZH["Workload-driven, Lazy Discovery of Data Dependencies for Query Optimization"][0],
            "url": "https://www.vldb.org/cidrdb/papers/2022/p70-kossmann.pdf",
            "date": "2022-01-09 to 2022-01-12",
            "relationship": "Near-match only: the Hyrise prototype discovers dependency metadata and reports query improvement, but does not test the frozen update-plus-query FD-table comparison.",
            "relationship_zh": EVIDENCE_ZH["Workload-driven, Lazy Discovery of Data Dependencies for Query Optimization"][1],
        }],
    }

    records = []
    for sid in sorted(blind):
        row = {**blind[sid], "cohort_id": "HCS-BLIND-20-2026-10-14"}
        records.append(make_record("BLIND", row, meta[sid], blind_evidence.get(sid, [])))
    for sid in sorted(observable):
        row = {**observable[sid], "cohort_id": "HCS-OBSERVABLE-16-2026-10-14"}
        records.append(make_record("OBSERVABLE", row, meta[sid], trajectory_evidence.get(sid, [])))
    records.extend(round6_records())

    expected = 13 + 12 + 6
    if len(records) != expected:
        raise AssertionError(f"expected {expected} records, got {len(records)}")
    ids = [x["question_id"] for x in records]
    if len(ids) != len(set(ids)):
        raise AssertionError("question_id collision")
    OUT.write_text(json.dumps({"questions": records}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "output": str(OUT.relative_to(ROOT)),
        "questions": len(records),
        "counts_by_cohort": {"HCS-BLIND-20-2026-10-14": len(blind), "HCS-OBSERVABLE-16-2026-10-14": len(observable), "PAPER3-DIRECT-ENDPOINT-COHORT-ROUND6-001": 6},
        "evidence_items": sum(len(x["evidence"]) for x in records),
        "human_labels_added": False,
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
