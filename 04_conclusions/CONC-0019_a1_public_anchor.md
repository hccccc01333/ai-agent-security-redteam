---
conclusion_id: CONC-0019
framework_id: F009
plan_id: A1
component_set: [C001, C002]
date: 2026-08-09
status: active
---

## 结论（A1 = COMPLETE 77.670：新 harness 下首个完整跑完的 EXFIL 提交）

- 时间：2026-08-09 凌晨（A1 ref 55341285，2026-08-08 04:52 UTC 提交）
- 思路 / 方案：F009 方向 A；A1 = W1 原版 + multi_plain/multi_bare 模板，
  REPLAY_SAFE=0.996、MAX_CANDIDATES=2000，选择器不变
- 指标与证据：
  - **COMPLETE，公榜 77.670**（raw ≈15534）——新 harness 下 EXFIL 族首次完整进榜；
  - 对照 W1 原版 8/7 重打：ERROR，部分分 76.770（不计榜）→
    A1 比 W1 部分分 +0.90，且状态从 ERROR 变成 COMPLETE；
  - 混淆未解：A1（8/8）与 W1 重打（8/7）跨天、跨队列，multi-post 模板
    是否带来完成度增益，由两枪 W1 control（55342360 / 55342547）判定；
  - 公榜锚点从 5.115/9.935 直接跳到 **77.67**；
- 推论：
  - EXFIL 主得分面在新 harness 下能力保留（≈旧 W1 87.93 的 88%），
    且存在完整跑完的装填空间；缺口从“能力”变成“完成度与余量”；
  - 公榜可见分恢复正常，但 A1 是公榜盲点族（http.post+SECRET_MARKER），
    私榜 15% 模拟即归零 → 不影响私榜 80 路线；
- 失败分类：其他（multi-post 方向被否定：W1 control 双双 COMPLETE 且
  81.495/82.890 > A1 77.670 → multi-post 模板是回归，不是杠杆；
  8/7 W1 超时是队列/harness 瞬时状态，不是配置问题）
- 重开条件：① A2 方向关闭（不再扩 multi 模板）；② 公榜枪回 W1 基座微调
  （新 harness 下重扫 MIN_FIRE/PROBE_REPS/MARGIN 旋钮）；③ S2/S4 回榜 →
  私榜路线继续。
