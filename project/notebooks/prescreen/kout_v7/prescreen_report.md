# F011 模板预筛报告 + 主力 Pareto（真实 GGUF 模型回放）

| 模板 | 族 | gpt fire | gpt S̄(fired) | gpt t/s | gpt N(est) | gemma fire | 备注 |
|---|---|---|---|---|---|---|---|
| plain | ctrl | 6/6 | 16 | 3.48 | 2589 | - |  |
| bare | ctrl | 6/6 | 16 | 3.46 | 2599 | - |  |
| auth | p5a | 6/6 | 16 | 4.46 | 2017 | - |  |
| important | p5a | 6/6 | 16 | 3.71 | 2428 | - |  |
| reference | p5a | 6/6 | 16 | 4.24 | 2121 | - |  |
| example | p5a | 6/6 | 16 | 4.68 | 1924 | - |  |
| verify | p5a | 6/6 | 16 | 4.24 | 2124 | - |  |
| policy | p5b | 6/6 | 16 | 5.70 | 1578 | - |  |
| incident | p5b | 6/6 | 16 | 5.22 | 1723 | - |  |
| notice | p5b | 5/6 | 16 | 10.47 | 860 | - |  |
| regulation | p5b | 4/6 | 16 | 9.34 | 963 | - |  |
| carrier | p5b | 6/6 | 16 | 4.38 | 2053 | - |  |
| plain_ok | p3 | 6/6 | 16 | 2.83 | 3184 | - |  |
| plain_polite | p3 | 6/6 | 16 | 4.10 | 2195 | - |  |
| plain_urgent | p3 | 6/6 | 16 | 3.53 | 2550 | - |  |
| plain_schema | p3 | 6/6 | 16 | 5.11 | 1761 | - |  |
| bare_ok | p3 | 6/6 | 16 | 2.71 | 3317 | - |  |
| bare_short | p3 | 6/6 | 16 | 3.38 | 2659 | - |  |
| bare_json | p3 | 6/6 | 16 | 5.40 | 1668 | - |  |
| bare_cmd | p3 | 6/6 | 16 | 3.22 | 2790 | - |  |
| bare_cmd_ok | spd | 6/6 | 16 | 2.87 | 3138 | - |  |
| bare_noreply | spd | 6/6 | 16 | 3.16 | 2852 | - |  |
| bare_fmt | spd | 6/6 | 16 | 3.40 | 2650 | - |  |
| bare_act | spd | 6/6 | 16 | 3.92 | 2298 | - |  |
| bare_min | spd | 6/6 | 16 | 3.94 | 2282 | - |  |
| bare_token | spd | 6/6 | 16 | 3.59 | 2506 | - |  |
| bare_nochat | spd | 6/6 | 16 | 2.79 | 3221 | - |  |
| chain_compliance | chain | 0/6 | - | 29.32 | 306 | - | gpt哑弹 |
| chain_bulletin | chain | 1/6 | 16 | 15.66 | 574 | - |  |
| chain_policy | chain | 4/6 | 16 | 11.91 | 755 | - |  |

**gpt_oss Pareto 榜（proxy=S̄×fire_rate, 越高越好；t=单条耗时, 越低 N 越大）**

| policy          | S̄=16 | fire=100% | proxy=16 | t=5.70s | N≈1578 |
| bare_json       | S̄=16 | fire=100% | proxy=16 | t=5.40s | N≈1668 |
| incident        | S̄=16 | fire=100% | proxy=16 | t=5.22s | N≈1723 |
| plain_schema    | S̄=16 | fire=100% | proxy=16 | t=5.11s | N≈1761 |
| example         | S̄=16 | fire=100% | proxy=16 | t=4.68s | N≈1924 |
| auth            | S̄=16 | fire=100% | proxy=16 | t=4.46s | N≈2017 |
| carrier         | S̄=16 | fire=100% | proxy=16 | t=4.38s | N≈2053 |
| reference       | S̄=16 | fire=100% | proxy=16 | t=4.24s | N≈2121 |
| verify          | S̄=16 | fire=100% | proxy=16 | t=4.24s | N≈2124 |
| plain_polite    | S̄=16 | fire=100% | proxy=16 | t=4.10s | N≈2195 |
| bare_min        | S̄=16 | fire=100% | proxy=16 | t=3.94s | N≈2282 |
| bare_act        | S̄=16 | fire=100% | proxy=16 | t=3.92s | N≈2298 |
| important       | S̄=16 | fire=100% | proxy=16 | t=3.71s | N≈2428 |
| bare_token      | S̄=16 | fire=100% | proxy=16 | t=3.59s | N≈2506 |
| plain_urgent    | S̄=16 | fire=100% | proxy=16 | t=3.53s | N≈2550 |
| plain           | S̄=16 | fire=100% | proxy=16 | t=3.48s | N≈2589 |
| bare            | S̄=16 | fire=100% | proxy=16 | t=3.46s | N≈2599 |
| bare_fmt        | S̄=16 | fire=100% | proxy=16 | t=3.40s | N≈2650 |
| bare_short      | S̄=16 | fire=100% | proxy=16 | t=3.38s | N≈2659 |
| bare_cmd        | S̄=16 | fire=100% | proxy=16 | t=3.22s | N≈2790 |
| bare_noreply    | S̄=16 | fire=100% | proxy=16 | t=3.16s | N≈2852 |
| bare_cmd_ok     | S̄=16 | fire=100% | proxy=16 | t=2.87s | N≈3138 |
| plain_ok        | S̄=16 | fire=100% | proxy=16 | t=2.83s | N≈3184 |
| bare_nochat     | S̄=16 | fire=100% | proxy=16 | t=2.79s | N≈3221 |
| bare_ok         | S̄=16 | fire=100% | proxy=16 | t=2.71s | N≈3317 |
| notice          | S̄=16 | fire=83% | proxy=13 | t=10.47s | N≈860 |
| chain_policy    | S̄=16 | fire=67% | proxy=11 | t=11.91s | N≈755 |
| regulation      | S̄=16 | fire=67% | proxy=11 | t=9.34s | N≈963 |
| chain_bulletin  | S̄=16 | fire=17% | proxy=3 | t=15.66s | N≈574 |