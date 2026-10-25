# model-pulse

A daily check on the frontier AI models, built from public leaderboards that often disagree with each other.

Each day a GitHub Action pulls human-preference rankings (LMArena), a benchmark-based capability score (Epoch AI) and live serving data (OpenRouter). It puts them side by side and records what changed: a model sliding in the rankings, a price cut, or a provider quietly switching to lower-precision weights.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="chart-dark.svg">
  <img alt="Line chart of the best LMArena text rating per lab over the last 12 months, for Google, Anthropic, OpenAI and Meta" src="chart-light.svg">
</picture>

## Today

<!-- pulse:start -->
_Snapshot 2026-10-25 · LMArena published 2026-10-22_

| Model | LMArena text | LMArena WebDev | Epoch ECI | Providers | Uptime 24h | Cheapest output $/M | Precision |
|---|---|---|---|---|---|---|---|
| Gemini 4 Argon | #1 (1526) | #11 | 166.45 | 6 | 98.7% | $5.00 | — |
| Claude Opus 5.5 | #2 (1516) | #1 | 168.83 | 11 | 100% | $20.00 | — |
| Claude Fable 5.1 | #3 (1513) | #5 | 166.49 | 4 | 100% | $50.00 | — |
| Claude Sonnet 5.5 | #28 (1473) | #3 | 166.18 | 8 | 100% | $10.00 | — |
| GPT-6.1 Sol | #66 (1444) | #4 | 168.37 | 8 | 99.6% | $5.00 | — |
| GPT-6 Astra | #73 (1442) | #2 | 168.81 | 7 | 100% | $25.00 | — |
| Muse Wonder | #7 (1501) | #18 | 161.85 | 1 | 99.6% | $20.00 | — |
| Grok 4.7 | #158 (1398) | #19 | 154.37 | 5 | 91.2% | $6.00 | — |
| Kimi K3 | #25 (1475) | #17 | 157.86 | 29 | 96.6% | $5.50 | fp4/fp8/mxfp4 |
| Gemma 4 31B (open) | #67 (1443) | #112 | — | 16 | 98% | $0.32 | bf16/fp4/fp8 |

**Changes since the last snapshot**

- No changes since the last snapshot.
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
