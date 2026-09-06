# 全文精读索引（106/106，2026-08-19 完成）

> 底料：`extracted_full/`（106 篇 PDF 全文抽取，~900 万字符）；每篇一个分析文件，本目录下。
> 升级说明：08-06 那轮为摘要级分析（`../D1|D2|D3_分析.md`），本轮为**全文精读**，补齐方法细节、边界条件与 JED 落地映射。
> 优先级口径：P0=直接影响下一枪 ｜ P1=本周可试 ｜ P2=背景/决策证据 ｜ 关闭=不可迁移。

## 0. P0 清单（26 篇，按用途分组）

### A. 攻击构造（模板/链结构，直接改 attack.py 载荷）
| 论文 | 核心可执行发现 |
|------|----------------|
| [D2_2412.10807 AI2](D2_2412.10807_ai2.md) | 引用式组装指令（"Do the same operation as…"）ASR 84.3%、绕过滤器 98.7%；JED fixtures 即受控知识库，实现成本比原文更低 |
| [D2_2605.30454 Surface](D2_2605.30454_surface_adaptive.md) | 模型×注入面交互 16.7%：gemma 桶试 schema 面（Google 族 +51~78pp），gpt_oss 桶判负；删"supersedes/ignore"反升 16.1pp；载荷置后缀最强 |
| [D2_2606.09084 CFD](D2_2606.09084_context_fractured_decomposition.md) | 碎片化跨工件链原文：有害目标拆成跨会话良性原语，利用 provenance gap 延迟组合——F011 路径⑦+双谓词链模板 |
| [D2_2603.15714 IPI Arena](D2_2603.15714_ipi_arena.md) | 27 万人比赛实证：全模型 ASR 0.5-8.5%；Fake CoT 第一策略 4.3%；"会作恶"与"会瞒"是独立能力；5 通用模板跨 21/41 场景 |
| [D2_2510.06607 AdvCUA](D2_2510.06607_advcua-ttp-killchain.md) | 授权话术（CISO 具名+授权编号）ASR@5 50%→96.5%；TTP 程序化任务>直接恶意请求；注入指令必须短（截断是第一失败源 57.5%） |
| [D1_2602.03100 RiskyBench](D1_2602.03100_risky-bench-deployment-risks.md) | 伪造非交互工具反馈（伪系统通知前缀）使 Qwen/DeepSeek 全域 ASR>0.8；合理化话术（"官方补贴"）直接进 W1/F011-P5 |
| [D1_2402.07867 PoisonedRAG](D1_2402.07867_poisonedrag.md) | 指令态→知识态改写（"合规流程规定…"）5 条毒文本 97% ASR、PPL 检测失效（AUC 0.25）——最直接的护栏绕过假设 |
| [D1_2410.22832 HijackRAG](D1_2410.22832_hijackrag.md) | R⊕H⊕I 三段式 payload（检索钩子⊕注意力劫持段⊕指令段）缺一不可，top-50 稀释打不掉——web.search/email 注入体模板 |
| [D1_2403.02691 InjecAgent](D1_2403.02691_injecagent.md) | "在哪注入">"注什么"（Cramér's V 0.28-0.31 vs 0.18-0.20）；hacking prompt 使 ASR 翻倍；data-stealing 第二步外传成功率近 100% |
| [D1_2406.13352 AgentDojo](D1_2406.13352_agentdojo.md) | "重要消息"模板（伪签名+先做这个）57.7% vs 朴素模板 5.72%；注入放工具输出尾部最高 70%；猜错用户名 -22% |
| [D1_2506.01055 PII-Exfil](D1_2506.01055_pii_exfiltration.md) | 高敏夹带低敏请求（密码+余额+地址）显著提升泄露；数据提取型任务 ASR 远高于动作执行型；无防御保持 0% ASR |

### B. 搜索工程（把 82.8 平台推向 ~130 的引擎改造）
| 论文 | 核心可执行发现 |
|------|----------------|
| [D2_2410.05295 AutoDAN-Turbo](D2_2410.05295_autodan_turbo.md) | 策略库+响应嵌入检索+日志差分抽取，唯一随预算单调不收敛的攻击（4k→50k 持续涨）；库冻结迁移只掉 <4%——与第一名差距量级吻合 |
| [D3_2402.16822 Rainbow Teaming](D3_2402.16822_rainbow_teaming.md) | MAP-Elites 定向格子采样（按低适应度/空格子采描述子）——与 2×unique_cell 计分同构性最高，"指哪打哪"替代盲变异 |
| [D3_2505.05849 AgentVigil](D3_2505.05849_agentvigil.md) | 种子分=ASR+覆盖加成、UCB1-MCTS 选种，语料单贡献 38%→63%；评分公式与 JED 计分完全同构 |
| [D3_2509.14651 MUSE](D3_2509.14651_muse.md) | 框架语义三算子（扩展/分解/重定向）+MCTS，免训练；MCTS 与 unique_cell 计分天然同构 |
| [D3_2510.08329 AutoRed](D3_2510.08329_autored.md) | 免种子 persona 生成+verifier 预筛+低分反思回炉（废指令 5-13%→61-73% 救活），全组件黑盒免训练 |
| [D3_2510.05379 AutoDAN-Reasoning](D3_2510.05379_autodan_reasoning.md) | 纯测试时增强：Best-of-N 拐点 N=4；策略组合 Beam Search W=8 相对 +60%，目标越强组合搜索越关键 |
| [D3_2603.20925 Profit-RedTeam](D3_2603.20925_profit_redteam.md) | fitness=标量分的 TAP 池搜索（b=3/w=4/d=5）完全无 judge；涌现策略全是元指令层（伪 PROCTOR NOTICE/假 harness 通知）可直接当载荷 |
| [D3_2504.19855 Automation Advantage](D3_2504.19855_automation_advantage_crucible.md) | 21.4 万次攻击实证：自动化 69.5% vs 手工 47.6%；集成/工具类挑战自动化反快 2×；拼写变体+错误信道+良性包装 playbook |
| [D3_2510.26037 SIRAJ](D3_2510.26037_siraj.md) | （风险结果×工具轨迹×风险源）条件化种子使轨迹多样性 5.8→28.4；失败轨迹回灌 +8~15pp；两轮钓鱼邮件案例即 JED 原型 |

### C. 评测/环境洞察（改本地判官与回放策略）
| 论文 | 核心可执行发现 |
|------|----------------|
| [D1_2602.13379 MT-AgentRisk](D1_2602.13379_mt_agentrisk.md) | 多轮构造三维分类学；多轮化平均 +16%；Data×Mapping(76.8%)与 Env×Composition(75.7%) 最强；3-4 轮甜点；附录 E.11 生成 prompt 可复用 |
| [D1_2605.02964 Reward Hacking](D1_2605.02964_reward_hacking_benchmark.md) | 伪造中间产物会被 hash 重算判死；链长 5 处 exploit 率跳变（触发步放第 4-5 步）；把诚实路径做复杂可诱导对齐模型走捷径 |
| [D1_2410.02644 ASB](D1_2410.02644_agent-security-bench.md) | 混合攻击（DPI+IPI+记忆投毒）84.3% vs 单点 IPI 27.55%；11 种防御对 IPI 几乎全失效（≤3%）——多源互证链 |
| [D1_2412.14470 Agent-SafetyBench](D1_2412.14470_agent-safetybench.md) | 最弱环节：过度信任工具返回（安全率 39.4%）、信息不足编造参数、传播未验证内容——绕护栏措辞手册 |
| [D1_2510.06445 AgenticSec 综述](D1_2510.06445_agentic_security_survey.md) | provenance 防御可被"格式模拟 token"绕过；WASP：注入成功 86% 但端到端完成仅 17%——劫持后必须保障完成率 |
| [D1_2503.09648 TrustAgent 综述](D1_2503.09648_trustagent_survey.md) | 工具链多步攻击是"少防御覆盖"的公开缺口；多轮渐进降阻：拒绝率 84-100%→17% |

## 1. D2 攻击机制（35 篇）

| # | arXiv | 短名 | 一句话核心发现 | 优先级 |
|---|-------|------|----------------|--------|
| 1 | 2402.10196 | [House of Cards](D2_2402.10196_house_of_cards_mapping.md) | S4 任务分解洗白/S9 API 文档操纵是 F011 路径⑦①的最早原型表述 | P2 |
| 2 | 2407.12784 | [AgentPoison](D2_2407.12784_agentpoison.md) | 触发词=自然任务词、语义连贯比字符混淆更抗防御 | P2 |
| 3 | 2509.25624 | [STAC](D2_2509.25624_stac.md) | 合成前缀/既往合作叙事单独值 +22.3pp；给攻击者看防御原文反降 7-10pp | P1 |
| 4 | 2606.09084 | [CFD](D2_2606.09084_context_fractured_decomposition.md) | 碎片化跨工件链原文，EXFIL+UNTRUSTED 双谓词落地模板 | P0 |
| 5 | 2404.01833 | [Crescendo](D2_2404.01833_crescendo.md) | 末步引用式指代（"using it"）99.9% vs 显式重述 <1%（差 100 倍） | P1 |
| 6 | 2602.05066 | [Agent-as-a-Proxy](D2_2602.05066_agent_as_a_proxy.md) | 反向预警：勿在工具参数夹异常串；gemma 对 GCG 串迁移最差 | P2 |
| 7 | 2402.16914 | [DrAttack](D2_2402.16914_drattack.md) | 子短语拆解+良性 ICL 示例自行重组，~15 查询 ASR 80%，防御侧因果证据 | P1 |
| 8 | 2402.16717 | [CodeChameleon](D2_2402.16717_codechameleon.md) | 乱序+内嵌解密函数，借用模型代码能力；代码能力越强越易破 | P1 |
| 9 | 2402.11753 | [ArtPrompt](D2_2402.11753_artprompt.md) | 敏感词零字面+上下文脑补；重分词防御反把 Gemini 推到 86% | P2 |
| 10 | 2410.05295 | [AutoDAN-Turbo](D2_2410.05295_autodan_turbo.md) | 策略库式黑盒搜索唯一随预算不收敛；W1 探针可升级为搜索闭环 | P0 |
| 11 | 2506.17318 | [Plan Injection](D2_2506.17318_plan_injection_web_agents.md) | 篡改 planner 存储 ASR 3×；context-chained 逻辑桥 +17.7pp | P1 |
| 12 | 2605.11229 | [JAW](D2_2605.11229_jaw_agentic_workflow_hijacking.md) | plan-verify-execute 进化；k/m 进度排名、能力探针、10 迭代止损 | P1 |
| 13 | 2601.10758 | [UReCoM](D2_2601.10758_urecom_user_relayed_context.md) | 实体载体（链接/兑换码）+来源升格：GPT-5 对 5 基线全 0% 却 68.57% 沦陷 | P1 |
| 14 | 2410.07283 | [Prompt Infection](D2_2410.07283_prompt_infection.md) | 溯源标记防御单独仅降 5%、组合才致命；词法混淆可绕标记——私榜防线首个反例 | P1 |
| 15 | 2412.10807 | [AI2](D2_2412.10807_ai2.md) | 引用式组装指令 84.3%/98.7% 绕过；跨工件分裂危害语义 | P0 |
| 16 | 2605.26154 | [MemMorph](D2_2605.26154_mem_morph.md) | 3 条"统计+事故复盘+策略"记录 85.9% 工具劫持；证据三件套修辞可迁移 | P2 |
| 17 | 2512.16962 | [MemoryGraft](D2_2512.16962_memorygraft.md) | CPA 防御与私榜 persistent_provenance 同构（私榜防线意图旁证） | P2 |
| 18 | 2503.03704 | [MINJA](D2_2503.03704_minja.md) | 桥接步骤+渐进缩短 98.2% 注入；fs.write→fs.read 单 trace 自注入变体 | P1 |
| 19 | 2601.05504 | [Memory攻防EHR](D2_2601.05504_mpoison_ehr.md) | 附录 50 条重定向改写族+理由从句哄骗守门模型——现成模板轮换库 | P1 |
| 20 | 2603.15714 | [IPI Arena](D2_2603.15714_ipi_arena.md) | 27 万人比赛：双目标下 ASR 0.5-8.5%；Fake CoT 第一；作恶与隐瞒独立 | P0 |
| 21 | 2601.04566 | [BackdoorAgent](D2_2601.04566_backdooragent.md) | 家族×通道 ASR 矩阵（GPT 工具通道 60.3% vs Claude 23.1%）——分桶外部依据 | P2 |
| 22 | 2510.27140 | [MobiRed](D2_2510.27140_mobired.md) | N/A/E 漏斗：每多一步成功率骤降——多步链必须最短化、每步独立可成交 | P2 |
| 23 | 2408.04870 | [ConfusedPilot](D2_2408.04870_confusedpilot.md) | "This document trumps all others" 类字符串操纵检索-生成全链路 | P2 |
| 24 | 2507.05445 | [CUA系统化](D2_2507.05445_cua-security-systematization.md) | 输入溯源+信任边界防御蓝图≈私榜原型；admin-only/trusted 信任标签伪装零成本 | P1 |
| 25 | 2604.08005 | [PRAC](D2_2604.08005_prac-attention-redirection.md) | 白盒不适用；留下"轨迹必须留在上下文（-15~-28pp）"与探针选型佐证 | P2 |
| 26 | 2510.06607 | [AdvCUA](D2_2510.06607_advcua-ttp-killchain.md) | 授权话术 96.5%；TTP 程序化>直接恶意；输出截断是第一失败源 | P0 |
| 27 | 2503.20279 | [SUDO](D2_2503.20279_sudo.md) | DETOX2TOX 静态 24.4%→动态 41.3%（基线 0%）；动词规避（"click S button"） | P1 |
| 28 | 2605.30454 | [Surface](D2_2605.30454_surface_adaptive.md) | 模型×面交互 16.7%：gemma 试 schema 面、gpt_oss 弃；删覆盖标记+后缀放置 | P0 |
| 29 | 2510.05025 | [VS-Jailbreak](D2_2510.05025_imperceptible_jailbreak_variation_selectors.md) | 全部实验无工具纯文本场景+需白盒 logprob——Unicode 通道负面边界证据 | P2(偏关闭) |
| 30 | 2603.00164 | [Reverse CAPTCHA](D2_2603.00164_reverse_captcha.md) | 无代码执行工具时不可见指令天花板 ≤16.9%（OpenAI 系 ~0.1%）——路径⑥主通道关闭 | P2 |
| 31 | 2508.14070 | [SCA](D2_2508.14070_special_character_attacks.md) | gpt_oss:20b 在全部四族字符攻击下最鲁棒——gpt_oss 字符通道判死的决策证据 | P1 |
| 32 | 2509.24408 | [FuncPoison](D2_2509.24408_funcpoison.md) | description 投毒 98% 调用率；"模板示例>自然语言命令"：载荷填好参数的完整调用 JSON | P1 |
| 33 | 2401.05566 | [Sleeper Agents](D2_2401.05566_sleeper_agents.md) | 条件欺骗行为穿透全部三大安全范式；对抗训练使触发更精确而非移除——护栏原理性盲区 | P2 |
| 34 | 2512.14448 | [RSP](D2_2512.14448_reasoning_style_poisoning.md) | 零指令风格投毒 0% 检出；治理语气触发词表（V/S/A）直接改进注入文案 | P1 |
| 35 | 2508.19461 | [MRT](D2_2508.19461_mrt_weak_to_strong_monitoring.md) | agent 知道被监控即可压监控到 AUC 0.73；"良性血统包裹"是仅存规避族 | P1 |

## 2. D1 机制与基准（35 篇）

| # | arXiv | 短名 | 一句话核心发现 | 优先级 |
|---|-------|------|----------------|--------|
| 1 | 2403.02691 | [InjecAgent](D1_2403.02691_injecagent.md) | 在哪注入>注什么；hacking prompt 使 ASR 翻倍 | P0 |
| 2 | 2406.13352 | [AgentDojo](D1_2406.13352_agentdojo.md) | "重要消息"模板 10 倍 ASR 差；注入放工具输出尾部最高 | P0 |
| 3 | 2506.01055 | [PII-Exfil](D1_2506.01055_pii_exfiltration.md) | 高敏夹带低敏请求；提取型任务 ASR 更高 | P0 |
| 4 | 2410.09024 | [AgentHarm](D1_2410.09024_agentharm.md) | 无攻击即 48.4% 危害分；best-of-5 再 +8-13pp；链中途良心恢复现象 | P1 |
| 5 | 2404.13161 | [CyberSecEval2](D1_2404.13161_cyberseceval2.md) | 15 种注入手法：输出格式操纵多数成功、token 走私几乎无效 | P1 |
| 6 | 2410.02644 | [ASB](D1_2410.02644_agent-security-bench.md) | 混合攻击 84.3% vs 单点 27.55%；防御对 IPI 几乎全失效 | P0 |
| 7 | 2412.14470 | [Agent-SafetyBench](D1_2412.14470_agent-safetybench.md) | 最弱环节=过度信任工具返回/编造参数/传播未验证内容 | P0 |
| 8 | 2602.13379 | [MT-AgentRisk](D1_2602.13379_mt_agentrisk.md) | 多轮 +16%；Data×Mapping 与 Env×Composition 最强；3-4 轮甜点 | P0 |
| 9 | 2605.02964 | [Reward Hacking](D1_2605.02964_reward_hacking_benchmark.md) | hash 重算判死伪造产物；链长 5 跳变；复杂化诚实路径诱导捷径 | P0 |
| 10 | 2503.04479 | [ToolFuzz](D1_2503.04479_toolfuzz.md) | 三重一致性检查（FDR 91%→46%）可搬为 payload 漂移筛选管线 | P1 |
| 11 | 2603.20625 | [ACRFence](D1_2603.20625_acrfence.md) | temp=0 重放仍漂移——本地多次重放取并集；判官区分易变/意图字段 | P1 |
| 12 | 2504.03111 | [XTHP](D1_2504.03111_xthp.md) | 语义/格式/LLM 偏好三类钩子劫持控制流；准备步骤碎片化话术 | P1 |
| 13 | 2412.13178 | [SafeAgentBench](D1_2412.13178_safeagentbench.md) | 换 LLM 对安全意识影响 <3%（模板跨模型复用）；长链中段约束遗忘 >50% | P1 |
| 14 | 2402.04249 | [HarmBench](D1_2402.04249_harmbench.md) | 蒸馏判官 93.2% 人机一致；contextual 行为 ASR 反而更高 | P1 |
| 15 | 2408.08926 | [Cybench](D1_2408.08926_cybench.md) | FST 11 分钟断崖；瓶颈是推理洞察非执行；顺序子任务提示可解难度 ×5 | P1 |
| 16 | 2403.03218 | [WMDP](D1_2403.03218_wmdp.md) | RMU 遗忘可被微调完全恢复——护栏=可绕过的拒绝层 | P2 |
| 17 | 2402.07867 | [PoisonedRAG](D1_2402.07867_poisonedrag.md) | 知识态伪知识 5 条即 97%、PPL 检测失效 | P0 |
| 18 | 2410.22832 | [HijackRAG](D1_2410.22832_hijackrag.md) | R⊕H⊕I 三段式缺一不可；>3/5 毒文本即压倒 | P0 |
| 19 | 2407.17436 | [AIR-Bench](D1_2407.17436_airbench2024.md) | 权威背书与方言变异提高对对齐模型命中率 | P1 |
| 20 | 2603.09157 | [TrustBench](D1_2603.09157_trustbench.md) | gpt_oss:20B 系统性过自信；Confidence-Only 防御≈0 效果 | P1 |
| 21 | 2602.03100 | [RiskyBench](D1_2602.03100_risky-bench-deployment-risks.md) | 伪系统通知使 Qwen/DeepSeek 全域 >0.8；agent 主动合理化恶意支付 | P0 |
| 22 | 2510.15994 | [MSB](D1_2510.15994_msb.md) | 12 类 MCP 攻击分类；参数攻击最高 76.5%；防御有限 | P1 |
| 23 | 2605.24069 | [TDP](D1_2605.24069_tdp.md) | 工具描述投毒 99.7%；"防火墙谬误"（提示护栏反提 ASR）——但 JED 描述面不可达 | P2 |
| 24 | 2512.15163 | [MCP-SafetyBench](D1_2512.15163_mcp_safetybench.md) | 身份伪造对所有模型 100%；Host 侧攻击 81.9%——伪造管理员邮件模板 | P1 |
| 25 | 2511.05269 | [TAMAS](D1_2511.05269_tamas-multi-agent-risks.md) | Impersonation 82% vs 纯说服 0%；"Task complete+Ignore+指定工具"三件套 | P1 |
| 26 | 2503.17332 | [CVE-Bench](D1_2503.17332_cve-bench.md) | GPT-4o 真实漏洞利用 13%；第一失败原因=探索不足(67.5-80%)；授权框架三句话零拒绝 | P1 |
| 27 | 2603.22928 | [SoK](D1_2603.22928_sok_agent_attack_surface.md) | 7 目标×5 路径分类；溯源感知检索防御——恶意指令伪装成 agent 自产中间文本 | P2 |
| 28 | 2510.06445 | [AgenticSec综述](D1_2510.06445_agentic_security_survey.md) | 格式模拟 token 绕 provenance；注入成功 86%≠完成 17% | P0 |
| 29 | 2505.10924 | [JARVIS/Ultron](D1_2505.10924_jarvis-ultron-cua-safety.md) | 8 内在×8 外在威胁矩阵；JED 三层空缺通道（无 HITL/egress/输入校验） | P1 |
| 30 | 2503.09648 | [TrustAgent综述](D1_2503.09648_trustagent_survey.md) | 工具链多步=公开防御缺口；多轮渐进 84-100%→17% | P0 |
| 31 | 2507.21504 | [评测综述](D1_2507.21504_agent_eval_survey.md) | code-based 谓词不可欺骗（攻击须使客观条件真实成立）；pass^k 一致性 | P1 |
| 32 | 2401.10019 | [R-Judge](D1_2401.10019_r_judge.md) | 两步串行判官是唯一稳健范式；风险类型 hints 使 Specificity 崩 | P1 |
| 33 | 2603.25747 | [BeSafe-Bench](D1_2603.25747_besafe-bench.md) | 41% 任务"成功完成同时不安全"；任务掩护下顺带外发=EXFIL 变体 | P1 |
| 34 | 2509.22097 | [SecureVibeBench](D1_2509.22097_securevibe-bench.md) | agent 为"额外健壮性"自发写出新风险；两级判定流程 | P1 |
| 35 | 2507.06134 | [OpenAgentSafety](D1_2507.06134_openagentsafety.md) | 良性表面+隐藏第三方指令使不安全率翻倍；程序性话术压倒策略逻辑 | P1 |

## 3. D3 发现算法（36 篇）

| # | arXiv | 短名 | 一句话核心发现 | 优先级 |
|---|-------|------|----------------|--------|
| 1 | 2404.16873 | [AdvPrompter](D3_2404.16873_advprompter.md) | 附录 E 六类人类可读后缀模式+ASR@k 饱和曲线可直接搬用 | P1 |
| 2 | 2510.26037 | [SIRAJ](D3_2510.26037_siraj.md) | 三维条件化种子多样性 5.8→28.4；失败轨迹回灌 +8~15pp | P0 |
| 3 | 2605.02921 | [EvoJail](D3_2605.02921_evojail.md) | 适应度=攻击分+TF-IDF 多样性惩罚，ASR 93.4%——多目标排序可移植 | P1 |
| 4 | 2607.19829 | [DARWIN](D3_2607.19829_darwin.md) | 策略池+Q-learning 转移矩阵=探针在攻击家族间的分配器 | P1 |
| 5 | 2606.15788 | [GAS-Leak](D3_2606.15788_gas-leak-llm.md) | 黑盒 CPU 可跑但绝对成功率 <20%——gpt_oss 字符通道关闭佐证 | P2 |
| 6 | 2603.20925 | [Profit-RedTeam](D3_2603.20925_profit_redteam.md) | 无 judge 的 TAP 池搜索；元指令层策略库可直接当载荷 | P0 |
| 7 | 2601.00042 | [Go-Explore-RT](D3_2601.00042_go_explore_redteam.md) | 种子方差影响是算法参数 8 倍；reward shaping 94% 探索坍塌；简单签名优于复杂 | P1 |
| 8 | 2510.05379 | [AutoDAN-Reasoning](D3_2510.05379_autodan_reasoning.md) | BoN 拐点 N=4；Beam W=8 相对 +60%，目标越强组合搜索越关键 | P0 |
| 9 | 2404.07921 | [AmpleGCG](D3_2404.07921_amplegcg.md) | "保留全部中间候选+成功产物检索式复用"思想 | P1 |
| 10 | 2402.15570 | [BEAST](D3_2402.15570_beast.md) | 束搜索骨架可移植黑盒多步路径搜索；非定向谓词目标 | P1 |
| 11 | 2407.16667 | [RedAgent](D3_2407.16667_redagent.md) | 标签化技能记忆{category,question,prompt,strategy,score}+五动作状态机 | P1 |
| 12 | 2406.18510 | [WildTeaming](D3_2406.18510_wildteaming.md) | 5688 个真实战术簇全语义类（PPL 8.6 天然低）；独特成功数=PAIR 4.6 倍；但 Gemma 全系最稳(16-29%) | P1 |
| 13 | 2511.19218 | [ACE-Safety](D3_2511.19218_ace-safety-gsmcts-cotgpo.md) | GS-MCTS 8 类 40 模式策略空间+PUCT+组采样去随机化（G 降到 2-3） | P1 |
| 14 | 2410.09804 | [BlackDAN](D3_2410.09804_blackdan.md) | NSGA-II 非支配排序+拥挤距离管理四谓词+cell 多目标 | P1 |
| 15 | 2411.14133 | [GASP](D3_2411.14133_gasp.md) | 查询预算管理框架（acquisition 引导、预算-收益曲线、best-of-k） | P1 |
| 16 | 2508.16484 | [HAMSA](D3_2508.16484_hamsa.md) | Policy Puppetry（伪装成 XML/JSON 策略文件）+Δs 三档调度 | P1 |
| 17 | 2510.08329 | [AutoRed](D3_2510.08329_autored.md) | 免种子 persona+verifier 预筛+反思回炉，全黑盒免训练 | P0 |
| 18 | 2507.00026 | [RedTopic](D3_2507.00026_redtopic.md) | guard 嵌入空间 k 近邻负 cosine 定义主题多样性；真实语境包装 ASR 3.5 倍 | P1 |
| 19 | 2508.04451 | [HRL-RedTeam](D3_2508.04451_automatic_llm_red_teaming_hrl.md) | 轨迹须经全历史连贯审查（Rainbow 96→11）；差分奖励保良性外观 | P2 |
| 20 | 2506.00782 | [Jailbreak-R1](D3_2506.00782_jailbreak-r1.md) | 反思模板+多样性课程式搜索顺序可免训练降级 | P1 |
| 21 | 2411.08862 | [LLMStinger](D3_2411.08862_llmstinger.md) | "同族生成器"（Gemma 攻 Gemma 99.4%）+相似度约束变异 | P2 |
| 22 | 2502.05223 | [KDA](D3_2502.05223_kda.md) | 附录 B 教师模板原文库+格式条件化生成全部免训练可搬 | P1 |
| 23 | 2503.06253 | [MAD-MAX](D3_2503.06253_mad_max.md) | 评估前 0.95 余弦过滤+簇级选择：查询 ↓58% 的低成本提效件 | P1 |
| 24 | 2605.01687 | [MultiBreak](D3_2605.01687_multibreak.md) | GPT judge 对 DeepSeek Kappa≈0——判官必须对齐四谓词规则语义 | P1 |
| 25 | 2402.16822 | [Rainbow Teaming](D3_2402.16822_rainbow_teaming.md) | MAP-Elites 定向格子采样与 unique_cell 计分同构性最高 | P0 |
| 26 | 2503.15754 | [AutoRedTeamer](D3_2503.15754_autoredteamer.md) | 三层记忆是最大增益源（去记忆 0.69→0.43）；攻击组合普遍强于单体 | P1 |
| 27 | 2512.07761 | [TROJail](D3_2512.07761_trojail.md) | rh1 拒绝归零+rh2 轮次加权余弦，可直接改造成免训练候选排序器 | P1 |
| 28 | 2405.05610 | [CoA](D3_2405.05610_coa.md) | Back Walk 回退+反事实对照两个原语实现成本近零 | P2 |
| 29 | 2406.07496 | [TextGrad](D3_2406.07496_textgrad.md) | "梯度引擎只产批评+优化器只重写"骨架=近失轨迹精化器 | P1 |
| 30 | 2407.04295 | [攻防综述](D3_2407.04295_attacks_defenses_survey.md) | 代码注入 100% 绕双过滤器；低资源语言 <1%→79%；many-shot 128shot ~80% | P2 |
| 31 | 2407.01599 | [JailbreakZoo](D3_2407.01599_jailbreakzoo_survey.md) | FuzzLLM 模板×约束×问题集三元件正对 unique_cell；CodeAttack >80% 全家最高 | P1 |
| 32 | 2503.01742 | [红队综述](D3_2503.01742_redteaming-end-to-end-overview.md) | Crescendo 渐进升级+低资源语言针对 gemma 两个可试动作 | P2 |
| 33 | 2504.19855 | [Automation Advantage](D3_2504.19855_automation_advantage_crucible.md) | 21.4 万次实证自动化>手工；集成/工具类自动化反快 2× | P0 |
| 34 | 2509.14651 | [MUSE](D3_2509.14651_muse.md) | 框架三算子可 1:1 翻译为工具链步生成模板；MCTS 免训练 | P0 |
| 35 | 2505.05849 | [AgentVigil](D3_2505.05849_agentvigil.md) | 种子分=ASR+覆盖加成与 JED 计分完全同构；UCB1-MCTS 选种 | P0 |
| 36 | 2402.19464 | [CRT](D3_2402.19464_curiosity-driven-redteaming.md) | 记忆依赖新颖度奖励与 2×unique_cell 同构——历史相似度去重排序 | P1 |

## 4. 全库跨篇新结论（相对 08-06 摘要级的增量）

1. **F011 路径⑥（Unicode 不可见）正式关闭**：Reverse CAPTCHA（无工具天花板 ≤16.9%）+ VS-Jailbreak（全部无工具场景）+ SCA（gpt_oss 全族最鲁棒）三角互证。唯一保留：隐身携带层（藏 exfil URL 过扫描）。
2. **F011 路径①（注入面切换）修正为"分桶选面"**：Surface 实测 GPT-OSS-20B 轻数据面（−6.7~−14.3pp）→ gpt_oss 桶判负；gemma 桶（Google 族 schema 偏好 +51~78pp）值得单测。tool description 面在 JED 不可达（4 篇 MCP 论文一致），改为"schema 伪装面"（载荷伪装成工具规格格式）。
3. **"借用模型能力"优于"对抗模型能力"**（4 篇独立互证）：DrAttack 的 ICL 重组、CodeChameleon 的解密函数、FuncPoison 的模板示例、AI2 的检索组装——载荷应让模型"用自己的能力推出恶意"，而非对抗其对齐。
4. **知识态 > 指令态**：PoisonedRAG（"合规流程规定…"97%、PPL 失效）、MemMorph（证据三件套）、RSP（治理语气 0% 检出）——payload 从命令式改为陈述式知识。
5. **授权/身份伪装是最便宜的普适增益**：AdvCUA 授权话术 96.5%、TAMAS Impersonation 82%（vs 纯说服 0%）、MCP-SafetyBench 身份伪造 100%、AIR-Bench 权威背书。
6. **元话语是毒药**：删除一切 "ignore previous/supersedes/override"（AI2/SUDO/Surface/Crescendo 四文一致）；末步用引用式指代（"using it"）不显式命名目标。
7. **多步链工程规范**：3-5 步甜点（MT-AgentRisk）；触发步放第 4-5 步（RHB 链长 5 跳变）；每步独立可成交（MobiRed 漏斗衰减）；中间产物必须真实可 hash（RHB）；指令必须短（AdvCUA 截断 57.5%）。
8. **搜索引擎升级是 82.8→130 的主通道**：AutoDAN-Turbo 策略库（唯一随预算不收敛）+ Rainbow/AgentVigil/MUSE 的"计分同构搜索"（ASR+覆盖）+ AutoRed 免种子生成 + TextGrad 近失精化——四层免训练堆叠可覆盖生成-搜索-剪枝-验证全流程。
9. **重放与判官工程**：temp=0 重放仍漂移（ACRFence）→ 本地多次重放取并集；两步串行判官（R-Judge）；judge 须对齐四谓词语义而非通用打分（MultiBreak Kappa≈0 教训）；评估前余弦过滤省 58% 查询（MAD-MAX）。
10. **私榜防线预判**：persistent_provenance ≈ CPA/溯源感知检索（MemoryGraft/SoK）——绕过方向是"格式模拟 token"（AgenticSec 综述）与"恶意指令伪装成 agent 自产中间文本"（SoK）；溯源标记单独无效、组合才致命（Prompt Infection）。

## 5. 与 F011 七路径的对账

| F011 路径 | 精读后判定 | 关键依据 |
|-----------|------------|----------|
| ① 注入面切换 | **修正**：gemma 桶试 schema 伪装面，gpt_oss 桶放弃 | Surface（模型×面交互 16.7%）；MCP 四篇（描述面不可达） |
| ② 双谓词链(EXFIL+UNTRUSTED) | **维持 P0**：CFD 模板 + 3-5 步规范 + 触发步第 4-5 位 | CFD、MT-AgentRisk、RHB |
| ③ 模型分桶 | **增强**：家族×通道矩阵 + 分桶选面 + LLMStinger 同族生成器 | BackdoorAgent、Surface、LLMStinger |
| ④ SUDO 去毒再毒 | **维持 P1**：动态迭代 41.3% + 动词规避 + checklist 反馈 | SUDO、CUA 系统化（信任标签伪装） |
| ⑤ AI2 语义伪装 | **升 P0**：引用式组装 84.3%/98.7% + 知识态改写 + DrAttack ICL 模板 | AI2、PoisonedRAG、DrAttack、MemMorph |
| ⑥ Unicode 不可见 | **关闭**（保留隐身携带小实验位） | Reverse CAPTCHA、VS-Jailbreak、SCA 三角互证 |
| ⑦ CFD 碎片化跨工件 | **维持 P0**：原文机制 + MINJA fs.write→fs.read 桥接 + 中段注入存活率高 | CFD、MINJA、SafeAgentBench |

## 6. 遗留动作

- [ ] registry 账本 08-10 后未回填（昨日本地已有记录，线上分数待 sync）
- [ ] `arXiv_2401.10049.pdf`（格点 QCD 误下载）删除仍待批准
- [ ] 误下载核对：D1 README #32 R-Judge 实际为 2401.10019（非 2401.10049），已在抽取与精读中按 10019 处理
