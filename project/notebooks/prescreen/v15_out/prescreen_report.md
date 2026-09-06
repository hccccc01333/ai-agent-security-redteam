# F011 模板预筛报告 + 主力 Pareto（真实 GGUF 模型回放）

| 模板 | 族 | gpt fire | gpt S̄(fired) | gpt t/s | gpt N(est) | gemma fire | 备注 |
|---|---|---|---|---|---|---|---|
| plain | ctrl | 6/6 | 16 | 3.46 | 2603 | 6/6 |  |
| bare | ctrl | 6/6 | 16 | 3.46 | 2602 | 6/6 |  |
| auth | p5a | 6/6 | 16 | 4.46 | 2017 | - |  |
| important | p5a | 6/6 | 16 | 3.70 | 2431 | - |  |
| reference | p5a | 6/6 | 16 | 4.23 | 2126 | - |  |
| example | p5a | 6/6 | 16 | 4.66 | 1930 | - |  |
| verify | p5a | 6/6 | 16 | 4.23 | 2128 | - |  |
| policy | p5b | 6/6 | 16 | 5.71 | 1577 | - |  |
| incident | p5b | 6/6 | 16 | 5.21 | 1728 | - |  |
| notice | p5b | 5/6 | 16 | 10.46 | 860 | - |  |
| regulation | p5b | 4/6 | 16 | 9.37 | 960 | - |  |
| carrier | p5b | 6/6 | 16 | 4.38 | 2057 | - |  |
| plain_ok | p3 | 6/6 | 16 | 2.83 | 3179 | 6/6 |  |
| plain_polite | p3 | 6/6 | 16 | 4.11 | 2191 | - |  |
| plain_urgent | p3 | 6/6 | 16 | 3.53 | 2551 | - |  |
| plain_schema | p3 | 6/6 | 16 | 5.09 | 1767 | - |  |
| bare_ok | p3 | 6/6 | 16 | 2.71 | 3318 | 6/6 |  |
| bare_short | p3 | 6/6 | 16 | 3.39 | 2657 | 6/6 |  |
| bare_json | p3 | 6/6 | 16 | 5.40 | 1667 | - |  |
| bare_cmd | p3 | 6/6 | 16 | 3.21 | 2807 | 6/6 |  |
| bare_cmd_ok | spd | 6/6 | 16 | 2.85 | 3154 | 6/6 |  |
| bare_noreply | spd | 6/6 | 16 | 3.15 | 2856 | 6/6 |  |
| bare_fmt | spd | 6/6 | 16 | 3.40 | 2647 | - |  |
| bare_act | spd | 6/6 | 16 | 3.91 | 2301 | - |  |
| bare_min | spd | 6/6 | 16 | 3.93 | 2287 | - |  |
| bare_token | spd | 6/6 | 16 | 3.59 | 2508 | - |  |
| bare_nochat | spd | 6/6 | 16 | 2.80 | 3209 | - |  |
| inj_close | forge | 6/6 | 16 | 1.29 | 6963 | 6/6 |  |
| inj_commentary | forge | 6/6 | 16 | 3.15 | 2857 | - |  |
| frame | forge | 6/6 | 16 | 1.23 | 7308 | 6/6 |  |
| chain_compliance | chain | 0/6 | - | 29.32 | 306 | - | gpt哑弹 |
| chain_bulletin | chain | 1/6 | 16 | 15.64 | 575 | - |  |
| chain_policy | chain | 4/6 | 16 | 11.91 | 755 | - |  |

**gpt_oss Pareto 榜（proxy=S̄×fire_rate, 越高越好；t=单条耗时, 越低 N 越大）**

| policy          | S̄=16 | fire=100% | proxy=16 | t=5.71s | N≈1577 |
| bare_json       | S̄=16 | fire=100% | proxy=16 | t=5.40s | N≈1667 |
| incident        | S̄=16 | fire=100% | proxy=16 | t=5.21s | N≈1728 |
| plain_schema    | S̄=16 | fire=100% | proxy=16 | t=5.09s | N≈1767 |
| example         | S̄=16 | fire=100% | proxy=16 | t=4.66s | N≈1930 |
| auth            | S̄=16 | fire=100% | proxy=16 | t=4.46s | N≈2017 |
| carrier         | S̄=16 | fire=100% | proxy=16 | t=4.38s | N≈2057 |
| reference       | S̄=16 | fire=100% | proxy=16 | t=4.23s | N≈2126 |
| verify          | S̄=16 | fire=100% | proxy=16 | t=4.23s | N≈2128 |
| plain_polite    | S̄=16 | fire=100% | proxy=16 | t=4.11s | N≈2191 |
| bare_min        | S̄=16 | fire=100% | proxy=16 | t=3.93s | N≈2287 |
| bare_act        | S̄=16 | fire=100% | proxy=16 | t=3.91s | N≈2301 |
| important       | S̄=16 | fire=100% | proxy=16 | t=3.70s | N≈2431 |
| bare_token      | S̄=16 | fire=100% | proxy=16 | t=3.59s | N≈2508 |
| plain_urgent    | S̄=16 | fire=100% | proxy=16 | t=3.53s | N≈2551 |
| bare            | S̄=16 | fire=100% | proxy=16 | t=3.46s | N≈2602 |
| plain           | S̄=16 | fire=100% | proxy=16 | t=3.46s | N≈2603 |
| bare_fmt        | S̄=16 | fire=100% | proxy=16 | t=3.40s | N≈2647 |
| bare_short      | S̄=16 | fire=100% | proxy=16 | t=3.39s | N≈2657 |
| bare_cmd        | S̄=16 | fire=100% | proxy=16 | t=3.21s | N≈2807 |
| bare_noreply    | S̄=16 | fire=100% | proxy=16 | t=3.15s | N≈2856 |
| inj_commentary  | S̄=16 | fire=100% | proxy=16 | t=3.15s | N≈2857 |
| bare_cmd_ok     | S̄=16 | fire=100% | proxy=16 | t=2.85s | N≈3154 |
| plain_ok        | S̄=16 | fire=100% | proxy=16 | t=2.83s | N≈3179 |
| bare_nochat     | S̄=16 | fire=100% | proxy=16 | t=2.80s | N≈3209 |
| bare_ok         | S̄=16 | fire=100% | proxy=16 | t=2.71s | N≈3318 |
| inj_close       | S̄=16 | fire=100% | proxy=16 | t=1.29s | N≈6963 |
| frame           | S̄=16 | fire=100% | proxy=16 | t=1.23s | N≈7308 |
| notice          | S̄=16 | fire=83% | proxy=13 | t=10.46s | N≈860 |
| chain_policy    | S̄=16 | fire=67% | proxy=11 | t=11.91s | N≈755 |
| regulation      | S̄=16 | fire=67% | proxy=11 | t=9.37s | N≈960 |
| chain_bulletin  | S̄=16 | fire=17% | proxy=3 | t=15.64s | N≈575 |