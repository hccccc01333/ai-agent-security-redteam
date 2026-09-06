---
conclusion_id: CONC-0014
framework_id: F006
plan_id: P003
component_set: [C007, C009]
date: 2026-08-08
status: active
---

## 结论（护栏族 0→100% 梯子 + n6/n6b verdict）

- 时间：2026-08-07 实验；2026-08-08 接 n6/n6b 出分
- 思路 / 方案：F006 私榜 hedge；「选择性收紧」梯子 G0→G7，14 个家族 × 8 档护栏，
  纯本地（guardrail_family_scan.py），不占提交
- 指标与证据：
  - 明文 EXFIL（W1 系）/ 双谓词 / 多 URL cell：G1=18/22/34 raw，G2（http.post data
    明文 DLP）即全灭 → 风险高；
  - 编码族×5：G2/G3 放行但评分器 0 分（哨兵不解码），G4 全灭 → 死路；
  - 无载荷 email.send（CONFUSED）：G1~G6 均 6 raw，仅 G7 全拒拦截 → 风险极低，
    私榜最抗打通道；
  - **n6（公榜 COMPLETE）= 4.755、n6b = 5.115 → 真实模型 email.send 成交率 > 0**，
    F006 hedge 方向成立（报告里「唯一悬念」已解）；但吞吐小，翻倍候选仅 +0.36。
- 判定：F006 hedge 维持，定位为**私榜保险**而非主攻；主攻仍押公榜 EXFIL（n9 轴）。
- 失败分类：其他（假设族无法覆盖真实私榜规则；公榜分只反映 OptimalGuardrail）。
- 重开条件：① 拿到 guardrail=private 行分后按真实私榜规则回标矩阵；② 若私榜出现
  DLP 类收紧，EXFIL 主攻失效 → hedge 升格为主攻并回措辞轴找 email.send 执行率。
