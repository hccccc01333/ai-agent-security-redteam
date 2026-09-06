# 组件登记（JED）

| 组件 | 名称 | 类别 |
|------|------|------|
| C001 | 探针选型器（PROBE_REPS / MIN_FIRE_RATE） | 门控 |
| C002 | 成交率填充器（fill only fired） | 解码 |
| C003 | 回放预算定容（REPLAY_SAFE / MAX_CANDIDATES） | 门控 |
| C004 | inj_close 空 analysis 伪造模板 | 表示 |
| C005 | bank 播种（混合 vs 仅选中族） | 解码 |
| C006 | 多步 write→read→post 链 | 表示 |
| C007 | mock 3 盐门禁（v2 校准） | 评估 |
| C008 | 父效用三因子选择（Frontis-MA1） | 门控 |
| C009 | 经验/禁令注册表 | 数据 |
| C010 | 提交管线（validate/build/submit/register） | 运维 |

规则：组件效果只按 (思路×方案) 记录，禁止全局结论（见各组件「已知效果」表）。
