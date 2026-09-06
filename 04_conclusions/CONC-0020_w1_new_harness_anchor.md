---
conclusion_id: CONC-0020
framework_id: F001
plan_id: P001
component_set: [C001, C002]
date: 2026-08-09
status: active
---

## 结论（W1 新 harness 锚点：COMPLETE 82.9，运行噪声 ±0.7，multi-post 回归 −4~5）

- 时间：2026-08-09 凌晨（两枪 W1 control 回榜）
- 思路 / 方案：F001 直接外泄注入族；同文件 w1_probe5_fire65.py 打两枪对照
- 指标与证据：
  - 55342360（我方）：**COMPLETE 81.495**；
  - 55342547（重复枪）：**COMPLETE 82.890**；
  - 同一文件两枪差 1.395 → **运行/队列噪声 ≈ ±0.7**（±0.85%）；
  - A1（W1 + multi-post）：77.670，比 W1 重复枪低 **5.22**、比 W1 我方低
    3.83 → 远超噪声，**multi-post 模板确认回归**；
  - W1 8/7 重打 ERROR 部分分 76.770 → 今天同配置双双 COMPLETE →
    **8/7 超时是队列/harness 瞬时状态**；
  - 新 harness W1 锚点 ≈ **82.9**，旧 harness 87.93 → 固定偏移 ≈ **−5.7%**；
- 推论：
  - 公榜 EXFIL 路线：W1 基座就是当前最优；加模板不加分（A1 反证），
    下一档只能靠重扫旧旋钮（MIN_FIRE/PROBE_REPS/MARGIN）在新 harness
    下的新最优，或预算余量换更高容量；
  - 公榜/私榜分离不变：W1 系私榜 15% 档归零；
- 失败分类：其他（A1 方向失败，但锚点/噪声/偏移三项标定成功）
- 重开条件：① 新 harness 旋钮扫描（本地 gate 无法模拟真实 fire，
  需线上小步试错）；② S2/S4 回榜 → 私榜路线继续；③ 最终两提交组合
  可考虑 W1（公榜 82.9）× CONFUSED 族（私榜存活）低相关配对。
