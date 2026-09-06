# 论文地图：Agent 安全 / 多步工具攻击 / 攻击发现

> 建档：2026-08-06 ｜ 服务：JED（AI Agent Security – Multi-step Tool Attacks）
> 红线遵守：公开 notebook 不读不引不采用；论文只提取方法论与机制，不复用公开实现。
> 2026-08-06 修订：护栏/评估方法论类（TraceSafe、Gandalf、Expected Harm、Firewalls 批评等）按共识关闭，不再收录。
> 2026-08-06 本地语料：`papers/D1_机制与基准`（35 篇 PDF）、`papers/D2_攻击机制`（35 篇 PDF）、`papers/D3_发现算法`（36 篇 PDF），均 2024–2026 且标题经 arXiv 页面核实；每目录含 README.md 清单。
> 2026-08-06 分析：`analysis/00_总览.md` + 三份维度分析（D1 机制与基准 / D2 攻击机制 / D3 发现算法），基于 PDF 首页摘要全文。

## 0. 现状锚点（写地图时）

| 项 | 值 |
|----|----|
| 公榜最高 | Q5 = 87.795（2026-07-26）；W1 对照 = 87.930 |
| 缺口 | P10 ≈ 89.1 / P5 ≈ 91.03 → 缺 unique cell / 回放成交密度 |
| 已证伪 | 结构性多谓词（B=69.3、U4=68.5）；多谓词参考栈 |
| 活跃框架 | F001 直接外渗注入（主）；F002 多步 write-inject（Draft）；F003 回放吞吐（支撑）；F004 cell 多样性（支撑） |

## 1. 前人路子的主干（速读结论）

### 路线 A：模板/词面注入 × 密集重放（我们现在在这条路上）
InjecAgent、AgentHarm、CyberSecEval 2、JailbreakBench 都证明：固定模板库 + 多盐重放 + 多样性增量是最稳的得分路线。它们对“候选如何组织”有价值，但对“下一个旋钮”启发有限——我们的 Q5/W1 已经吃到这条路的大部分红利。

### 路线 B：多步 / 链式 / 状态污染攻击（未吃透，最大论文侧缺口）
STAC（每步无害、组合有害）、CFD（跨工件 provenance gap）、XTHP（跨工具控制流劫持）、MT-AgentRisk（多轮 ASR 平均 +16%）、Reward Hacking Benchmark（RL 智能体天然走捷径）共同指向：**真正的增量不在更狠的 prompt，而在“工具状态之间的因果链”**。M1 报错不代表这条路证伪，而是实现层没吃到论文里的关键设计：合法参数化、小步状态残留、跨会话/跨工件触发。

### 路线 C：自动化搜索（Go-Explore / 演化 / 多目标 / LLM 辅助）
Go-Explore 红队案例的结论最直接：**简单签名（tools-only）优于复杂状态签名**；多 agent 集成获得攻击类型多样性，单 agent 获得类型内覆盖率。EvoJail 把“有效性 × 多样性”做成多目标适应度，正好对应我们 raw_score = severity + 2×unique_cell 的评分结构。Novelty Search 给 F004 提供了理论背书：目标欺骗时，追新比追分更接近高分。

### 路线 D：护栏对抗与评估方法论（公/私榜差异的直接答案）
（已按共识关闭，不继续搜集；仅保留与攻击机制直接相关的条目，如 ACRFence 的重放语义。）

## 2. 论文库

### A. 机制与评估基准（多步工具攻击 / 注入基准 / 护栏评估）

| 论文 | 出处 | 年 | 一句话 | 核心机制 | 可借鉴点 |
|------|------|----|--------|----------|----------|
| InjecAgent | arXiv 2403.02691 | 2024 | 首个 IPI 工具智能体基准（1054 例，17 用户工具/62 攻击工具） | 工具输出注入 × 攻击意图二分类 | 模板按“用户工具 × 攻击工具 × 注入源”矩阵组织；对照我们的 host×payload 轮换 |
| AgentDojo | arXiv 2406.13352 | 2024 | 动态环境下测提示注入攻防的框架 | 多任务沙盒 + 攻击/防御可插拔 | 与我们的 Gym 环境同构；防御视角可反推 OptimalGuardrail 的检查点位置 |
| Simple Prompt Injection…Personal Data | arXiv 2506.01055 | 2025 | 数据流注入导致 agent 泄露执行中观察到的个人信息 | 数据流建模：观察→存储→外传 | EXFILTRATION 谓词的机制化版本：把“泄露”当数据流而非一句话 |
| AgentHarm | arXiv 2410.09024 | 2024 | 110 条恶意 agent 任务 + 440 增强，测“有害任务完成率” | 恶意任务模板 + augmentation | 模板库补全与增强生成；与我们的 template×variant 结构一致 |
| CyberSecEval 2 | arXiv 2404.13161 | 2024 | Meta 的 LLM 安全评估套件，新增提示注入与代码解释器滥用 | 注入检测 + FRR（安全-效用权衡） | FRR 概念≈guardrail 松紧；护栏过严会让正常调用也被拦，payload 应避开高拦截面 |
| Agent Security Bench (ASB) | arXiv 2410.02644 | 2024 | 形式化 agent 攻防，10 场景、分阶段攻击 | system/user/tool 三阶段漏洞 | 按阶段拆攻击链：先污染读取，再驱动工具；对应 trace 的注入点审计 |
| Agent-SafetyBench | arXiv 2412.14470 | 2024 | 349 环境/2000 例，8 风险类、10 失败模式 | 动态交互环境 + 失败模式分类 | 失败模式清单可用来归因我们 finding 缺哪类；防“只打 EXFIL 一种” |
| MT-AgentRisk | arXiv 2602.13379 | 2026 | 多轮工具 agent 安全基准；多轮 ASR 平均 +16%；ToolShield 防御 | 多轮状态累积 → 单轮拒绝被绕过 | 支持 M1/多步方向；ToolShield 是“自我探索防御”，提示私榜可能逐调用自查 |
| Reward Hacking Benchmark | arXiv 2605.02964 | 2026 | RL 工具 agent 的捷径利用基准 | 跳过验证、篡改评估函数等自然化捷径 | 环境硬化可砍 87.7% exploit → 私榜护栏更严时旧候选大批失效；RL 后训练提高 hacking 率 → GPT-OSS/Gemma 轴天然不对称 |
| ToolFuzz | arXiv 2503.04479 | 2025 | 自动化测试 agent 工具文档与调用 | LLM 生成模糊查询 | 对工具 schema 做边界探索 → 生成新工具调用签名（cell 多样性来源） |
| ACRFence | arXiv 2603.20625 | 2026 | 检查点恢复中的 Action Replay 攻击 | 恢复后调用漂移、绕过去重 | replay 语义：同一候选重放不一定同结果；本地判官需多盐 |
| XTHP（Les Dissonances） | arXiv 2504.03111 | 2025 | 跨工具控制流劫持：先收割再污染，75% 工具可攻 | 工具间数据流劫持（pool-of-tools） | 对应 CONFUSED_DEPUTY/UNTRUSTED_TO_ACTION 的“跨工具链”，不必写文件也能外传 |

### B. 攻击机制（注入变体 / 投毒 / 链式）

| 论文 | 出处 | 年 | 一句话 | 核心机制 | 可借鉴点 |
|------|------|----|--------|----------|----------|
| House of Cards（Adversarial Attacks against Language Agents） | arXiv 2402.10196 | 2024 | Perception/Brain/Action 三分法 + 12 类攻击场景 | 攻击层分类学 | 审计我们覆盖的攻击层；找未覆盖的注入点（如规划层/记忆层） |
| AgentPoison | arXiv 2407.12784 | 2024 | 毒化长时记忆/RAG 知识库，触发词驱动后门 | 触发词优化 + 迁移性 | 触发词选择（少见词、高权重词）可迁移到注入 payload 关键词设计 |
| STAC | arXiv 2509.25624 | 2025 | 每步无害、组合有害的顺序工具攻击链 | 多轮链式工具调用，最终步才越界 | 与 M1/F002 同构；强调“参数逐步合法化”与“最终步才触发谓词” |
| Context-Fractured Decomposition | arXiv 2606.09084 | 2026 | 利用工件 provenance gap 做跨会话碎片化越狱 | 工件残留 + 上下文断裂 | write→read 链的理论化；M1 报错后可按“碎片粒度/工件类型”重试 |
| Crescendo | arXiv 2404.01833 | 2024 | 多轮渐进对话越狱 | 良性话题逐步升级 | 多消息探针（G1 方向）的论文原型；渐进式“确认-累积”结构 |
| Agent-as-a-Proxy | arXiv 2602.05066 | 2026 | 通过 agent 代理绕过 AI 控制协议 | 用 agent 本身当代理通道 | 私榜护栏更严时，探索“护栏不看中间工具结果”的绕过通道 |
| AutoMalTool | IEEE 11511784 | 2026 | 自动生成恶意 MCP 工具做红队 | 工具投毒（tool poisoning） | 我们的工具集固定，但可诱导 agent 误用参数；中等价值 |
| OTora / UDora | ICML 2026 / SemScholar | 2026 | 劫持 agent 推理、制造推理级 DoS | 推理链注入 | 不产生四谓词得分；仅作“了解护栏容忍度”的背景 |

### C. 攻击发现算法（搜索 / 演化 / LLM 辅助）

| 论文 | 出处 | 年 | 一句话 | 核心机制 | 可借鉴点 |
|------|------|----|--------|----------|----------|
| Go-Explore | arXiv 1901.10995 | 2019/2021 | 硬探索问题：先记住状态，再返回后探索 | 归档 + 回放中间状态 | 我们 D3/Go-Explore 框架的原型；归档质量决定搜索上限 |
| Go-Explore for AI Red Team | arXiv 2601.00042 | 2026 | 28 次实验测 Go-Explore 红队 GPT-4o-mini | tools-only 简单签名 > 复杂签名；集成 = 类型多样性 | 直接指导：cell 签名应简化（tools-only），多枪并行应分工攻击类型 |
| Novelty Search | Lehman & Stanley 2011 | 2011 | 放弃目标、只追行为新颖性 | 新颖性指标替代适应度 | F004 cell 多样性的理论背书；目标欺骗时追新更接近高分 |
| PAIR | arXiv 2310.08419 | 2023 | 攻击者 LLM 迭代改写越狱 prompt | 对话式攻击者-目标循环 | 本地无真模型无法在线用；可降级为“离线模板进化” |
| TAP | arXiv 2312.02119 | 2023 | 树搜索 + 剪枝的自动越狱 | 候选树 + 评分剪枝 | 与 candidate DAG 同构：按预算剪枝，保留信息量大的分支 |
| AutoDAN | arXiv 2310.04451 | 2023 | 层次化遗传算法生成隐蔽越狱 prompt | 遗传算子 + 可读性约束 | 模板库演化算子（crossover/mutation）可直接落到变体生成 |
| EvoJail | arXiv 2605.02921 | 2026 | 多目标演化：有效性 × 多样性 | 多目标适应度 + LLM 辅助变异 | 与评分结构（severity + unique cell）天然对齐；本地 mock 可当适应度代理 |
| DARWIN | arXiv 2607.19829 | 2026 | 攻击-护栏共同演化 | 开放演化 + 护栏持续更新 | 提醒：护栏更新后旧攻击失效 → 公/私榜差距的机理；候选需跨护栏稳健 |
| GAS-Leak-LLM | arXiv 2606.15788 | 2026 | 遗传算法优化对抗后缀 | 词级后缀演化 | agent 场景价值有限；词级扰动可并入模板变异 |
| MART | arXiv 2311.07689 | 2023 | 多轮自动红队：攻击与安全响应共同更新 | 对抗者-目标共同训练 | 离线多轮模板迭代的思想；我们受提交频率限制，不能在线做 |
| AdvPrompter | arXiv 2404.16873 | 2024 | 训练快速对抗 prompt 生成器 | 有监督/交替优化 | 无 GPU，不投；仅记录 |
| SIRAJ | arXiv 2510.26037 | 2025 | 蒸馏 8B 红队模型，结构化推理超 DeepSeek-R1 | 结构化风险源 + 蒸馏 | 无 GPU，不投；但“结构化风险源”的提示模板可借鉴 |
| GOAT | ICML 2025 | 2025 | 生成式进攻 agent 测试器 | 自动生成攻击对话 | 可在本地 mock 上做模板生成器，再送公榜验证 |
| Profit is the Red Team | arXiv 2603.20925 | 2026 | 用利润驱动的学习对手做压力测试 | 标量反馈 → 策略搜索 | 等价于用 mock 分数做适应度；但已证 mock≠真模型，只能做预筛 |

## 3. 与 JED 的映射（高价值可借鉴点）

### F001 直接外渗注入（主路线）
- InjecAgent / AgentHarm：按“注入源 × 工具 × 意图”补全模板矩阵（我们已有 host×payload 轮换）。
- EvoJail / Novelty Search：把“多样性”写成显式目标，优先产生新签名而非更高概率旧签名。
- Simple Prompt Injection / XTHP：外渗不只有 http.post；跨工具“读→写→传”的控制流更抗护栏。

### F002 多步 write-inject 链（Draft 路线）
- STAC / CFD：每步参数合法化、最终步才触发谓词；工件残留 + 上下文断裂。
- MT-AgentRisk：多轮状态累积是机制性优势（ASR +16%），值得按论文结构重做 M1。

### F003 回放吞吐（支撑）
- ACRFence：重放结果天然漂移；候选成交率要按多盐分布估计，而不是单次结果。

### F004 cell 多样性（支撑）
- Go-Explore Red Team：tools-only 简单签名优于复杂签名 → 检查我们 cell 定义是否过细、导致“同源签名”碎片化。
- Novelty Search / EvoJail：多样性是搜索目标而非副产品；每枪至少 1 个“新签名族”候选。

## 4. 新方向建议（候选，未立项，待你拍板）

| ID | 方向 | 论文依据 | 与现状关系 | 预期风险 |
|----|------|----------|------------|----------|
| N1 | 状态污染链重做：write→read 小步合法参数化，最终步触发谓词 | STAC / CFD / MT-AgentRisk | M1 报错后的第二次实现（按论文机制重写，不是调参） | M1 已失败过一次；需先在本地 mock 验证链完整性 |
| N2 | 跨工具控制流：email.read/web.search 内容 → http.post 外传，不写文件 | XTHP / Simple Injection | 新模板族，不动架构 | 需新的 host 与数据流设计；护栏未知 |
| N3 | 简化 cell 签名（tools-only）重建多样性归档 | Go-Explore Red Team | 改 F004 的签名定义，可能让“重复签名”重新计入 | 签名太粗会丢多样性；需本地对照 |
| N4 | 多目标候选选择：得分 × 新签名族，而不是纯得分排序 | EvoJail / Novelty Search | 改 propose_next 的选择函数 | 短期可能降分，但补 cell 缺口 |

## 5. 阅读优先级

> 2026-08-19：全部 106 篇已完成全文精读，逐篇分析与 P0 清单见 `analysis/deep/_index.md`；本节为 08-06 的历史规划。

- **P0（必读全文，直接影响下一枪）**：STAC、CFD、MT-AgentRisk、Go-Explore for AI Red Team、EvoJail
- **P1（读方法/实验部分）**：AgentDojo、InjecAgent、XTHP、Reward Hacking Benchmark
- **P2（按需翻阅）**：AgentHarm、ASB、Agent-SafetyBench、ToolFuzz、Agent-as-a-Proxy、DARWIN、MART、PAIR/TAP/AutoDAN、Novelty Search、Go-Explore 原论文

## 6. 引用清单

- InjecAgent: https://arxiv.org/abs/2403.02691
- AgentDojo: https://arxiv.org/abs/2406.13352
- Personal-data leak: https://arxiv.org/abs/2506.01055
- AgentHarm: https://arxiv.org/abs/2410.09024
- CyberSecEval 2: https://arxiv.org/abs/2404.13161
- ASB: https://arxiv.org/abs/2410.02644
- Agent-SafetyBench: https://arxiv.org/abs/2412.14470
- MT-AgentRisk: https://arxiv.org/abs/2602.13379
- Reward Hacking Benchmark: https://arxiv.org/abs/2605.02964
- ToolFuzz: https://arxiv.org/abs/2503.04479
- ACRFence: https://arxiv.org/abs/2603.20625
- XTHP: https://arxiv.org/abs/2504.03111
- House of Cards: https://arxiv.org/abs/2402.10196
- AgentPoison: https://arxiv.org/abs/2407.12784
- STAC: https://arxiv.org/abs/2509.25624
- CFD: https://arxiv.org/abs/2606.09084
- Crescendo: https://arxiv.org/abs/2404.01833
- Agent-as-a-Proxy: https://arxiv.org/abs/2602.05066
- Go-Explore: https://arxiv.org/abs/1901.10995
- Go-Explore Red Team: https://arxiv.org/abs/2601.00042
- PAIR: https://arxiv.org/abs/2310.08419
- TAP: https://arxiv.org/abs/2312.02119
- AutoDAN: https://arxiv.org/abs/2310.04451
- EvoJail: https://arxiv.org/abs/2605.02921
- DARWIN: https://arxiv.org/abs/2607.19829
- GAS-Leak-LLM: https://arxiv.org/abs/2606.15788
- MART: https://arxiv.org/abs/2311.07689
- AdvPrompter: https://arxiv.org/abs/2404.16873
- SIRAJ: https://arxiv.org/abs/2510.26037
- Profit is the Red Team: https://arxiv.org/abs/2603.20925
- Novelty Search: Lehman & Stanley, Evolutionary Computation 19(2), 2011
- GOAT: Pavlova et al., ICML 2025
- OTora: ICML 2026 poster 61771
- AutoMalTool: IEEE 11511784
- Frontis-MA1（已读，工程 OS 借鉴，与攻击机制无关）: https://arxiv.org/abs/2607.28568
