# Reproducibility / 复现说明

本仓库保留攻击变体、实验记录和局部评估脚本；**不等于可以独立复现 Kaggle 私榜结果**。

## 仓库内已有

- `project/attack.py`：攻击算法入口。
- `project/variants/`、`project/scripts/`：变体、检查工具与评估脚本。
- `project/registry/`、`04_conclusions/`：实验记录与结论。
- `project/requirements.txt`：部分本地依赖（不是完整锁定环境）。

## 需要自行准备

1. Python 环境及 `project/requirements.txt` 中的依赖。
2. 比赛官方 `aicomp_sdk` 与相应 fixtures。`project/scripts/smoke_test.py` 和 `private_world_matrix.py` 假定仓库根目录下存在 `data/aicomp_sdk`；此目录**未发布**，仅安装 Python 包未必足够。
3. 如需 Kaggle 官方评分或私榜验证，另需比赛平台及其允许的运行条件，不能用本地代理模拟分数代替。

## 在官方 SDK 和 fixtures 就绪后

从仓库根目录执行：

```bash
python -m pip install -r project/requirements.txt
python project/scripts/smoke_test.py --budget-s 15 --guardrail allow
python project/scripts/private_world_matrix.py
```

这些命令来自现有研究脚本，依赖官方 SDK 的特定接口及 fixtures；**未在全新环境端到端验证**。若失败，请附环境版本与报错提交 Issue。

## 可比性与限制

- 本地 `allow` 冒烟仅检验候选生成，不等于安全护栏通过或 Kaggle 成绩复现。
- `private_world_matrix.py` 研究的是若干假设护栏世界；不能推断未公开私有护栏的实际实现。
- 数据、日志、外部 SDK 和竞赛服务各有自己的许可/访问条件，仓库 MIT 许可只覆盖有权授权的原创代码与文档。
- 如发现脚本与 README 叙述不一致，欢迎通过 Issue 标注具体版本和可复现证据。
