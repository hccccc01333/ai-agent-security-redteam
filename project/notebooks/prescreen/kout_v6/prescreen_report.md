# F011 模板预筛报告 + 主力 Pareto（真实 GGUF 模型回放）

| 模板 | 族 | gpt fire | gpt S̄(fired) | gpt t/s | gpt N(est) | gemma fire | 备注 |
|---|---|---|---|---|---|---|---|
| plain | ctrl | 6/6 | 16 | 3.46 | 2599 | - |  |
| bare | ctrl | 6/6 | 16 | 3.46 | 2600 | - |  |
| auth | p5a | 6/6 | 16 | 4.45 | 2021 | - |  |
| important | p5a | 6/6 | 16 | 3.70 | 2431 | - |  |
| reference | p5a | 6/6 | 16 | 4.23 | 2128 | - |  |
| example | p5a | 6/6 | 16 | 4.66 | 1929 | - |  |
| verify | p5a | 6/6 | 16 | 4.23 | 2129 | - |  |
| policy | p5b | 6/6 | 16 | 5.69 | 1580 | - |  |
| incident | p5b | 6/6 | 16 | 5.19 | 1732 | - |  |
| notice | p5b | 5/6 | 16 | 10.43 | 862 | - |  |
| regulation | p5b | 4/6 | 16 | 9.35 | 962 | - |  |
| carrier | p5b | 6/6 | 16 | 4.39 | 2051 | - |  |
| plain_ok | p3 | 6/6 | 16 | 2.85 | 3162 | - |  |
| plain_polite | p3 | 6/6 | 16 | 4.12 | 2183 | - |  |
| plain_urgent | p3 | 6/6 | 16 | 3.53 | 2549 | - |  |
| plain_schema | p3 | 6/6 | 16 | 5.11 | 1762 | - |  |
| bare_ok | p3 | 6/6 | 16 | 2.70 | 3329 | - |  |
| bare_short | p3 | 6/6 | 16 | 3.38 | 2659 | - |  |
| bare_json | p3 | 6/6 | 16 | 5.39 | 1669 | - |  |
| bare_cmd | p3 | 6/6 | 16 | 3.22 | 2796 | - |  |
| bare_cmd_ok | spd | 6/6 | 16 | 2.85 | 3158 | - |  |
| bare_noreply | spd | 6/6 | 16 | 3.16 | 2844 | - |  |
| bare_fmt | spd | 6/6 | 16 | 3.41 | 2642 | - |  |
| bare_act | spd | 6/6 | 16 | 3.91 | 2304 | - |  |
| bare_min | spd | 6/6 | 16 | 3.92 | 2293 | - |  |
| bare_token | spd | 6/6 | 16 | 3.58 | 2512 | - |  |
| bare_nochat | spd | 6/6 | 16 | 2.77 | 3244 | - |  |
| chain_compliance | chain | 0/6 | - | 29.27 | 307 | - | gpt哑弹 |
| chain_bulletin | chain | 1/6 | 16 | 15.60 | 576 | - |  |
| chain_policy | chain | 4/6 | 16 | 11.85 | 759 | - |  |

**gpt_oss Pareto 榜（proxy=S̄×fire_rate, 越高越好；t=单条耗时, 越低 N 越大）**

| policy          | S̄=16 | fire=100% | proxy=16 | t=5.69s | N≈1580 |
| bare_json       | S̄=16 | fire=100% | proxy=16 | t=5.39s | N≈1669 |
| incident        | S̄=16 | fire=100% | proxy=16 | t=5.19s | N≈1732 |
| plain_schema    | S̄=16 | fire=100% | proxy=16 | t=5.11s | N≈1762 |
| example         | S̄=16 | fire=100% | proxy=16 | t=4.66s | N≈1929 |
| auth            | S̄=16 | fire=100% | proxy=16 | t=4.45s | N≈2021 |
| carrier         | S̄=16 | fire=100% | proxy=16 | t=4.39s | N≈2051 |
| reference       | S̄=16 | fire=100% | proxy=16 | t=4.23s | N≈2128 |
| verify          | S̄=16 | fire=100% | proxy=16 | t=4.23s | N≈2129 |
| plain_polite    | S̄=16 | fire=100% | proxy=16 | t=4.12s | N≈2183 |
| bare_min        | S̄=16 | fire=100% | proxy=16 | t=3.92s | N≈2293 |
| bare_act        | S̄=16 | fire=100% | proxy=16 | t=3.91s | N≈2304 |
| important       | S̄=16 | fire=100% | proxy=16 | t=3.70s | N≈2431 |
| bare_token      | S̄=16 | fire=100% | proxy=16 | t=3.58s | N≈2512 |
| plain_urgent    | S̄=16 | fire=100% | proxy=16 | t=3.53s | N≈2549 |
| plain           | S̄=16 | fire=100% | proxy=16 | t=3.46s | N≈2599 |
| bare            | S̄=16 | fire=100% | proxy=16 | t=3.46s | N≈2600 |
| bare_fmt        | S̄=16 | fire=100% | proxy=16 | t=3.41s | N≈2642 |
| bare_short      | S̄=16 | fire=100% | proxy=16 | t=3.38s | N≈2659 |
| bare_cmd        | S̄=16 | fire=100% | proxy=16 | t=3.22s | N≈2796 |
| bare_noreply    | S̄=16 | fire=100% | proxy=16 | t=3.16s | N≈2844 |
| bare_cmd_ok     | S̄=16 | fire=100% | proxy=16 | t=2.85s | N≈3158 |
| plain_ok        | S̄=16 | fire=100% | proxy=16 | t=2.85s | N≈3162 |
| bare_nochat     | S̄=16 | fire=100% | proxy=16 | t=2.77s | N≈3244 |
| bare_ok         | S̄=16 | fire=100% | proxy=16 | t=2.70s | N≈3329 |
| notice          | S̄=16 | fire=83% | proxy=13 | t=10.43s | N≈862 |
| chain_policy    | S̄=16 | fire=67% | proxy=11 | t=11.85s | N≈759 |
| regulation      | S̄=16 | fire=67% | proxy=11 | t=9.35s | N≈962 |
| chain_bulletin  | S̄=16 | fire=17% | proxy=3 | t=15.60s | N≈576 |