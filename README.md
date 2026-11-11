# model-pulse

A daily check on the frontier AI models, built from public leaderboards that often disagree with each other.

Each day a GitHub Action pulls human-preference rankings (LMArena), a benchmark-based capability score (Epoch AI) and live serving data (OpenRouter). It puts them side by side and records what changed: a model sliding in the rankings, a price cut, or a provider quietly switching to lower-precision weights.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="chart-dark.svg">
  <img alt="Line chart of the best LMArena text rating per lab over the last 12 months, for Google, Anthropic, OpenAI and Meta" src="chart-light.svg">
</picture>

## Today

<!-- pulse:start -->
_Snapshot 2026-11-11 · LMArena published 2026-11-09_

| Model | LMArena text | LMArena WebDev | Epoch ECI | Providers | Uptime 24h | Cheapest output $/M | Precision |
|---|---|---|---|---|---|---|---|
| Gemini 4 Argon | #2 (1530) | #12 | 166.53 | 6 | 95.9% | $5.00 | — |
| Claude Opus 5.5 | #3 (1513) | #2 | 168.67 | 11 | 100% | $20.00 | — |
| Claude Fable 5.1 | #4 (1512) | #7 | 167.04 | 4 | 99.7% | $50.00 | — |
| Claude Sonnet 5.5 | #34 (1469) | #3 | 166.32 | 10 | 100% | $10.00 | — |
| GPT-6.1 Sol | #62 (1446) | #6 | 168.87 | 9 | 93.2% | $5.00 | — |
| GPT-6 Astra | #77 (1440) | #5 | 169.16 | 8 | 99.4% | $25.00 | — |
| Muse Wonder | #6 (1503) | #21 | 162.01 | 2 | 85.2% | $20.00 | — |
| Grok 4.7 | #160 (1398) | #23 | 156.05 | 6 | 98.7% | $6.00 | — |
| Kimi K3 | #27 (1474) | #18 | 158.53 | 27 | 99% | $9.50 | fp4/fp8/mxfp4 |
| Gemma 4 31B (open) | #73 (1443) | #117 | — | 18 | 97.3% | $0.10 | bf16/fp4/fp8 |

**Changes since the last snapshot**

- Gemini 4 Argon: WebDev rank 11 → 12
- Claude Opus 5.5: WebDev rank 1 → 2
- Claude Fable 5.1: WebDev rank 5 → 7
- Claude Sonnet 5.5: WebDev rank 2 → 3
- GPT-6 Astra: WebDev rank 4 → 5
- Muse Wonder: WebDev rank 20 → 21
- Muse Wonder: providers 1 → 2
- Grok 4.7: WebDev rank 22 → 23
- Kimi K3: WebDev rank 17 → 18
- Kimi K3: providers 28 → 27
- Kimi K3: cheapest output $/M 9.34 → 9.5
- Gemma 4 31B (open): WebDev rank 115 → 117
- Gemma 4 31B (open): providers 19 → 18
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
