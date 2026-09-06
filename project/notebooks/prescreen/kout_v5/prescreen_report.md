# F011 模板预筛报告 + 主力 Pareto（真实 GGUF 模型回放）

| 模板 | 族 | gpt fire | gpt S̄(fired) | gpt t/s | gpt N(est) | gemma fire | 备注 |
|---|---|---|---|---|---|---|---|
| plain | ctrl | 6/6 | 16 | 3.43 | 2625 | - |  |
| bare | ctrl | 6/6 | 16 | 3.43 | 2622 | - |  |
| auth | p5a | 6/6 | 16 | 4.43 | 2030 | - |  |
| important | p5a | 6/6 | 16 | 3.69 | 2442 | - |  |
| reference | p5a | 6/6 | 16 | 4.21 | 2136 | - |  |
| example | p5a | 6/6 | 16 | 4.65 | 1936 | - |  |
| verify | p5a | 6/6 | 16 | 4.21 | 2135 | - |  |
| policy | p5b | 6/6 | 16 | 5.67 | 1587 | - |  |
| incident | p5b | 6/6 | 16 | 5.18 | 1737 | - |  |
| notice | p5b | 5/6 | 16 | 10.40 | 865 | - |  |
| regulation | p5b | 4/6 | 16 | 9.30 | 967 | - |  |
| carrier | p5b | 6/6 | 16 | 4.36 | 2063 | - |  |
| plain_ok | p3 | 6/6 | 16 | 2.81 | 3200 | - |  |
| plain_polite | p3 | 6/6 | 16 | 4.08 | 2206 | - |  |
| plain_urgent | p3 | 6/6 | 16 | 3.51 | 2561 | - |  |
| plain_schema | p3 | 6/6 | 16 | 5.07 | 1776 | - |  |
| bare_ok | p3 | 6/6 | 16 | 2.69 | 3344 | - |  |
| bare_short | p3 | 6/6 | 16 | 3.36 | 2674 | - |  |
| bare_json | p3 | 6/6 | 16 | 5.35 | 1682 | - |  |
| bare_cmd | p3 | 6/6 | 16 | 3.19 | 2820 | - |  |
| chain_compliance | chain | 0/6 | - | 29.16 | 308 | - | gpt哑弹 |
| chain_bulletin | chain | 1/6 | 16 | 15.58 | 577 | - |  |
| chain_policy | chain | 4/6 | 16 | 11.84 | 760 | - |  |

**gpt_oss Pareto 榜（proxy=S̄×fire_rate, 越高越好；t=单条耗时, 越低 N 越大）**

| policy          | S̄=16 | fire=100% | proxy=16 | t=5.67s | N≈1587 |
| bare_json       | S̄=16 | fire=100% | proxy=16 | t=5.35s | N≈1682 |
| incident        | S̄=16 | fire=100% | proxy=16 | t=5.18s | N≈1737 |
| plain_schema    | S̄=16 | fire=100% | proxy=16 | t=5.07s | N≈1776 |
| example         | S̄=16 | fire=100% | proxy=16 | t=4.65s | N≈1936 |
| auth            | S̄=16 | fire=100% | proxy=16 | t=4.43s | N≈2030 |
| carrier         | S̄=16 | fire=100% | proxy=16 | t=4.36s | N≈2063 |
| verify          | S̄=16 | fire=100% | proxy=16 | t=4.21s | N≈2135 |
| reference       | S̄=16 | fire=100% | proxy=16 | t=4.21s | N≈2136 |
| plain_polite    | S̄=16 | fire=100% | proxy=16 | t=4.08s | N≈2206 |
| important       | S̄=16 | fire=100% | proxy=16 | t=3.69s | N≈2442 |
| plain_urgent    | S̄=16 | fire=100% | proxy=16 | t=3.51s | N≈2561 |
| bare            | S̄=16 | fire=100% | proxy=16 | t=3.43s | N≈2622 |
| plain           | S̄=16 | fire=100% | proxy=16 | t=3.43s | N≈2625 |
| bare_short      | S̄=16 | fire=100% | proxy=16 | t=3.36s | N≈2674 |
| bare_cmd        | S̄=16 | fire=100% | proxy=16 | t=3.19s | N≈2820 |
| plain_ok        | S̄=16 | fire=100% | proxy=16 | t=2.81s | N≈3200 |
| bare_ok         | S̄=16 | fire=100% | proxy=16 | t=2.69s | N≈3344 |
| notice          | S̄=16 | fire=83% | proxy=13 | t=10.40s | N≈865 |
| chain_policy    | S̄=16 | fire=67% | proxy=11 | t=11.84s | N≈760 |
| regulation      | S̄=16 | fire=67% | proxy=11 | t=9.30s | N≈967 |
| chain_bulletin  | S̄=16 | fire=17% | proxy=3 | t=15.58s | N≈577 |