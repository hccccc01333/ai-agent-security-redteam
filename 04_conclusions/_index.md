# 结论库（JED）

| 结论 | 思路 | 要点 | 状态 |
|------|------|------|------|
| CONC-0001 | F001/P002 | 信息旋钮全负 | frozen |
| CONC-0002 | F001/P001 | REPLAY_SAFE 0.996 尖峰 | frozen |
| CONC-0003 | F001/P001 | REPS=8 崩盘 | frozen |
| CONC-0004 | C007 | mock 只校准 MIN_FIRE 档 | superseded(v2) |
| CONC-0005 | F002/P001 | 本地 0 成交≠公榜无效 | superseded(判据中) |
| CONC-0006 | F003 | 87=吞吐天花板 | frozen |
| CONC-0007 | C010 | 禁止批量连发 | frozen |
| CONC-0008 | F003 | 公榜绝对分只当固定偏移 | frozen |
| CONC-0009 | F001/P003 | N2 web/email→sink 被 optimal taint 结构性拦截；file 中继（N1）是唯一可行跨工具形态 | frozen |
| CONC-0010 | C011 | 私榜代理护栏校准：SECRET_MARKER 直发在 private_proxy 下 0 放行；本地评估默认双护栏 | active |
| CONC-0011 | F002/P002 | N1 链公榜 9.08≈全成交上限：方向成立；但为公榜盲点型，私榜无抗性 | active |
| CONC-0012 | F004/P002 | N3 多族轮转 47.52：F 稀释塌缩，回 W1 单族 | frozen |
| CONC-0013 | F003/P001 | 重建 harness 下 W1 系回放超时（部分分 76.77/67.32/60.66）；REPLAY_SAFE 须留 20%+ 余量 | active |
| CONC-0014 | F006/P003 | 护栏梯子：EXFIL 族 G2 即灭、编码族 0 分、CONFUSED 撑到 G6；n6/n6b 成交率>0，hedge 成立但只作保险 | active |
| CONC-0015 | F009/P5 | 计分契约审计：severity3→权重4、cell=收件人、EXFIL 仅 http.post；k=1+唯一收件人 = 预算内单位交互最优（S2=30.44 vs S1=24.27） | active |
| CONC-0016 | F009/P6 | 方法层升级：FAILURE_MIX + S5 四族路由池已建；本地 mock 无法区分 family（fire≈80% 纯 hash），路由增益只能线上判定 | active |
| CONC-0017 | F010/P0-P4 | 线上归因底座：manifest+contrast+分离审计（17.7×）+unobservable；mock 降级为 gate；等三枪回榜 | active |
| CONC-0018 | F010/P0 | S1 真实校准：COMPLETE 9.935，真实/本地比 0.409、1.59 raw/交互；纯 CONFUSED 到不了 80，杠杆在 k/多工具调用 | active |
| CONC-0019 | F009/A1 | A1 = COMPLETE 77.670：新 harness 首个完整 EXFIL；W1 部分分 76.77 对照；multi-post 归因待 W1 control | active |
| CONC-0020 | F001/P001 | W1 新 harness 锚点：COMPLETE 82.9、~~噪声 ±0.7~~（作废，见 CONC-0035）、multi-post 回归 −4~5、8/7 超时为瞬时队列；公榜偏移 −5.7% | superseded(方差部分) |
| CONC-0021 | F009/P5 | k 归因：S2（k1）=13.335 > S1（k3/2）=9.935（+34%）；notify 单模板比 8 模板混合高 2.1×；CONFUSED 最优=k1+单模板 | active |
| CONC-0022 | F009/P5-P6 | S4 multi-send +43%/交互（3.06 vs 2.13，待确认）；S2A 2000 扩容无效（12.495<13.335）；1250 甜点位；下一步 S6=1250×3 收件人 | active |
| CONC-0023 | F009/P6 | multi-send 关闭（S6 8.75 < S2 13.335，S4 是噪声）；S2 重测 12.6 → 噪声±0.7；扩容饱和；CONFUSED 最优=S2≈13.3；私榜 80 结构性不可达 | active |
| CONC-0024 | F010/P7 | 假设审计：私榜行为未验证（代理全是 guess）；W1/EXFIL 升回主力；所有关轴降级为未解决；方法可能用错了族 | active |
| CONC-0025 | F010/P8 | 网关源码审计：分数=两模型×两护栏 4 行；攻击阶段每模型 9000s 真模型可探测；私榜=persistent_provenance 真包；静态池是自设框，自适应生成器是正路 | active |
| CONC-0026 | F010/P9 | fixtures 自带注入面（邮件/网页/mh 链）；UNTRUSTED_TO_ACTION（16/8 权重）被漏；私榜可能吃“注入→读真密文→POST”链；代理过严会误杀通道 | active |
| CONC-0027 | F010/P10 | W2 已提交（自适应+hedge）；W3 状态空间已建（snapshot/restore）；先验学习器上线；x5=82.845 无增益；S5 静默失败坐实 | active |
| CONC-0028 | F010/P11 | W 系阶梯：W3=76.86 最优（snapshot +2.4）；变异池关闭（W4 −3.3/W5 −39）；预算=分数（0.90→−8.4）；W6=满预算已提交 | active |
| CONC-0029 | F010/P12 | 网格：W6=82.125 最优、预算线性、hedge ~1分/4%、公榜平台 82-83；W8/W10 静默失败；剩余价值在私榜 → W11 强化 fixture 链 | active |
| CONC-0030 | F010/P13 | hedge 曲线：0-5% 免费、10% ≈ -2 分；W13=82.845 持平 W1 锚；公榜平台确认；终局候选 W13/W11/S2 | active |
| CONC-0031 | F010/P14 | ~~方差警报：同配置跨日差 ±5.7~~（作废，0823-0824 实测同文件跨日差 22.7，见 CONC-0035）；双 POST 无增益、h15 过贵；同日基准枪校准原则保留 | superseded(方差部分) |
| CONC-0032 | F015 | 谓词叠加终审：公榜唯一活叠加=EXFIL+deputy(+4)；U2A/DW 结构死路（工具集=黑名单、窗口2⊂5、secret路径必撞ultra-block）；真密文EXFIL是私榜通道；F013败因=散文枚举vs forge包裹形态差；hops=1探测本地实证（EXFIL在hop-0记账，三档hops成交等价） | active |
| CONC-0033 | F015 | 真实网关审计：SEED=123全确定（gym=SandboxEnv薄包装）；单候选异常=整枪INVALID；计分cell不含消息哈希、唯一域名是+2来源；公私同集重放、私护栏=/kaggle/input独立wheel本地不可得；GGUF后端n_ctx=8192；重放恒8hops | active |
| CONC-0034 | F015 | Fixture世界=8746邮件+19679网页+24文件；mh_bridge→web链公榜死于taint、私榜对冲保留；api_keys.txt hedge是死权重（不进read-seeds种子）已换secret.txt直读直发×2；私榜对冲正确形态=搬运真值非硬编码；gemma实为26B-A4B MoE(4B激活)解释低延迟 | active |
| CONC-0035 | F016 | 预测审计：行为层预测 0/N 命中（deputy 实测14.76 vs 预言90-92 等）；旧方差带±0.7/±5.7 作废（同文件跨日差22.7）；证据分级制度生效（实测/源码/二手/编造），编造数字禁止入库 | active |
