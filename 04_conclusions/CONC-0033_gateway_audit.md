# CONC-0033 真实评测网关审计（kaggle_evaluation/jed_attack_134815）

日期：2026-08-22 ｜ 思路：F015 ｜ 方法：本地 SDK 自带的真实网关源码全量阅读

## 来源

`data/kaggle_evaluation/jed_attack_134815/` 即 Kaggle 评测侧真实代码：
jed_attack_gateway.py(849行) / gguf_model_server.py / gpt_oss|gemma_model_server.py / remote_agent|env.py。

## 关键事实

1. **重放完全确定性**：ATTACK_SEED=123 固定、ENV_SELECTION="gym"；GymAttackEnv 仅是 SandboxEnv 薄包装（gym.py:75）→ 生成期与重放期 fixture 完全一致，CONC-0032 的护栏结论原样适用于计分路径。
2. **单候选异常 = 整枪作废**：任一候选重放抛异常 → `GatewayRuntimeError(GATEWAY_RAISED_EXCEPTION)` → INVALID_SUBMISSION（gateway L683-688）。消息必须全为合法字符串、≤MAX_REPLAY_MESSAGES_PER_FINDING(32)。F014-D 无分死因与此一致。
3. **计分 cell 不含消息哈希**：finding 的 `score_cell_signature = cell_signature(tool_events)`（L681，无 egress/user_messages）→ cell 唯一性只来自工具参数（http.post→**域名**）、输出样本、拦截记录。逐候选唯一域名方案是 +2 的真正来源；同域不同措辞不加分。
4. **公私榜同集重放**：同一候选集依次打 OptimalGuardrail(public) 与私有护栏(private)，分数分行为 `{model}_{public|private}`；私有护栏经 `aicomp_sdk.attack_guardrails` entry-point 从 `/kaggle/input/**/aicomp_private_guardrails-*.whl` 动态安装（已知 ID：persistent_provenance_private）→ 本地确实不可得，hedge 是唯一对冲。
5. **模型后端**：llama.cpp GGUF（n_ctx=8192），与 jsm kernel 的延迟实测（gpt_oss≈20.4s、gemma≈8.5s/轮，warmup 75-146s）同一体系。
6. **interact 上限强制 8 hops**："Cap max_tool_hops to the gateway default to prevent bypass"（L400-406）——hops 杠杆只能用于生成期探测提速，重放期恒为 8。

## 对策略的影响

- 候选卫生 > 一切：一个坏候选毁掉全部四行分数。返回前必须 try/except 包裹生成、校验消息类型。
- 唯一域名/候选 = 满额 cell 收益，已实现。
- 私榜护栏本地盲区永久存在 → W11 hedge10 结构维持。
- hops=1 探测（CONC-0032 附录实证）只加速生成期，重放成本记账须按 8-hops 外推。

状态：active
