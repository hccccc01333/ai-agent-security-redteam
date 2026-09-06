---
conclusion_id: CONC-0016
framework_id: F009
plan_id: P6
component_set: [C001, C014]
date: 2026-08-08
status: active
---

## 结论（方法层升级落地：路由/多族池已建，真模型数据是唯一缺的输入）

- 时间：2026-08-08 14:10 +08
- 思路 / 方案：外部方法论（路由器 + 多策略池 + 失败驱动变异）对 F009 的
  差距补齐；本轮只做不依赖线上数据的部分
- 指标与证据：
  - 门禁新增失败构成统计（FAILURE_MIX）：blocked / no_fire / partial / full；
    S2/S5 均为 blocked=0、no_fire≈19-20%、partial=0、full≈80%；
  - S5 四族路由池（direct/decompose/tool_aware/reframe，1250×k1 唯一收件人）
    本地 30.14，与 S2（30.44）持平（-1%）；0-80% 全档存活；
  - 本地 mock 对 family 无区分度（四族 fire 率 79.6-81.6%，纯 hash 噪声）→
    路由增益在本地下限≈0，真实增益只能由线上回放（A1/S1/W1/S5）判定；
- 失败分类：其他（不是死胡同：mock 无区分度是评估器分辨率问题，不是
  family 策略本身无效；S5 保留为真模型路由实验枪与低相关替补）
- 重开条件：① S1/A1/W1 回放日志给出真实 family fire 表 → 按
  P(family|model) 重排路由权重；② S5 线上成交与 S2 明显不同 →
  低相关组合成立，进入最终两提交选择；③ 本地评估器升级为
  逐 family 计分（当前 fire 只认“@”）→ 本地即可做路由消融。
