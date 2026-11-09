# model-pulse

A daily check on the frontier AI models, built from public leaderboards that often disagree with each other.

Each day a GitHub Action pulls human-preference rankings (LMArena), a benchmark-based capability score (Epoch AI) and live serving data (OpenRouter). It puts them side by side and records what changed: a model sliding in the rankings, a price cut, or a provider quietly switching to lower-precision weights.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="chart-dark.svg">
  <img alt="Line chart of the best LMArena text rating per lab over the last 12 months, for Google, Anthropic, OpenAI and Meta" src="chart-light.svg">
</picture>

## Today

<!-- pulse:start -->
_Snapshot 2026-11-09 · LMArena published 2026-11-08_

| Model | LMArena text | LMArena WebDev | Epoch ECI | Providers | Uptime 24h | Cheapest output $/M | Precision |
|---|---|---|---|---|---|---|---|
| Gemini 4 Argon | #2 (1530) | #11 | 166.45 | 6 | 94.7% | $5.00 | — |
| Claude Opus 5.5 | #4 (1513) | #1 | 168.36 | 11 | 99.9% | $20.00 | — |
| Claude Fable 5.1 | #3 (1513) | #5 | 166.9 | 4 | 100% | $50.00 | — |
| Claude Sonnet 5.5 | #34 (1468) | #2 | 166.24 | 10 | 100% | $10.00 | — |
| GPT-6.1 Sol | #61 (1446) | #6 | 168.94 | 9 | 99.5% | $5.00 | — |
| GPT-6 Astra | #76 (1440) | #4 | 169.07 | 8 | 99.4% | $25.00 | — |
| Muse Wonder | #6 (1504) | #20 | 162.02 | 1 | 100% | $20.00 | — |
| Grok 4.7 | #159 (1398) | #22 | 156.07 | 6 | 98.5% | $6.00 | — |
| Kimi K3 | #27 (1475) | #17 | 158.51 | 30 | 98.8% | $9.50 | fp4/fp8/mxfp4 |
| Gemma 4 31B (open) | #72 (1443) | #114 | — | 19 | 98.8% | $0.10 | bf16/fp4/fp8 |

**Changes since the last snapshot**

- GPT-6.1 Sol: LMArena text rank 60 → 61
- GPT-6 Astra: LMArena text rank 75 → 76
- GPT-6 Astra: WebDev rank 3 → 4
- Grok 4.7: LMArena text rank 158 → 159
- Kimi K3: LMArena text rank 26 → 27
- Kimi K3: WebDev rank 18 → 17
- Gemma 4 31B (open): LMArena text rank 74 → 72
- Gemma 4 31B (open): WebDev rank 115 → 114
<!-- pulse:end -->

## How to read it

- **LMArena text / WebDev:** rank (and rating) from people blind-voting between two models' answers. The best variant counts (e.g. `High`/`Max` reasoning).
- **Epoch ECI:** the Epoch Capabilities Index, one score combining many benchmarks.
- **Providers / uptime / price / precision:** from OpenRouter's public endpoints API. Precision lists the number formats providers publicly declare (`bf16`, `fp8`, `fp4`). Lower precision is cheaper to serve and can cost quality.

When the leaderboards disagree, that's information, not noise. A model can top the benchmarks and still lose the chat vote.

## How it works

`pulse.py` (stdlib + `pyarrow`) runs daily in [`.github/workflows/pulse.yml`](.github/workflows/pulse.yml). It:

1. downloads the sources,
2. matches the models in [`models.json`](models.json) across them (each source names models differently),
3. appends every value to [`data/history.csv`](data/history.csv),
4. redraws the chart and this README.

A source that changes its format makes the run fail loudly instead of publishing wrong numbers. To track other models, edit `models.json`.

```bash
pip install pyarrow && python -m unittest && python pulse.py
```

## Data and credit

- [LMArena leaderboard dataset](https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset), CC BY 4.0
- [Epoch AI, "Capabilities & benchmarking"](https://epoch.ai/benchmarks), CC BY 4.0
- [OpenRouter](https://openrouter.ai) public models API

Code: MIT.
