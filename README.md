# model-pulse

A daily check on the frontier AI models, built from public leaderboards that often disagree with each other.

Each day a GitHub Action pulls human-preference rankings (LMArena), a benchmark-based capability score (Epoch AI) and live serving data (OpenRouter). It puts them side by side and records what changed: a model sliding in the rankings, a price cut, or a provider quietly switching to lower-precision weights.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="chart-dark.svg">
  <img alt="Line chart of the best LMArena text rating per lab over the last 12 months, for Google, Anthropic, OpenAI and Meta" src="chart-light.svg">
</picture>

## Today

<!-- pulse:start -->
_Snapshot 2026-11-19 · LMArena published 2026-11-18_

| Model | LMArena text | LMArena WebDev | Epoch ECI | Providers | Uptime 24h | Cheapest output $/M | Precision |
|---|---|---|---|---|---|---|---|
| Gemini 4 Argon | #3 (1529) | #18 | 166.57 | 5 | 97.5% | $5.00 | — |
| Claude Opus 5.5 | #4 (1514) | #2 | 168.7 | 6 | 99.9% | $20.00 | — |
| Claude Fable 5.1 | #5 (1512) | #11 | 167.09 | 3 | 99.8% | $50.00 | — |
| Claude Sonnet 5.5 | #34 (1470) | #4 | 166.59 | 5 | 100% | $10.00 | — |
| GPT-6.1 Sol | #62 (1447) | #10 | 168.63 | 6 | 99.8% | $5.00 | — |
| GPT-6 Astra | #78 (1441) | #7 | 169.2 | 6 | 99.9% | $25.00 | — |
| Muse Wonder | #7 (1503) | #26 | 161.74 | 2 | 99.7% | $20.00 | — |
| Grok 4.7 | #160 (1400) | #28 | 156.43 | 5 | 97.5% | $6.00 | — |
| Kimi K3 | #30 (1474) | #23 | 158.6 | 29 | 99.6% | $9.50 | fp4/fp8/mxfp4 |
| Gemma 4 31B (open) | #73 (1443) | #121 | — | 18 | 99.3% | $0.10 | bf16/fp4/fp8 |

**Changes since the last snapshot**

- Gemini 4 Argon: LMArena text rank 2 → 3
- Gemini 4 Argon: WebDev rank 15 → 18
- Claude Opus 5.5: LMArena text rank 3 → 4
- Claude Fable 5.1: LMArena text rank 4 → 5
- Claude Fable 5.1: WebDev rank 7 → 11
- Claude Sonnet 5.5: WebDev rank 3 → 4
- GPT-6.1 Sol: LMArena text rank 66 → 62
- GPT-6.1 Sol: WebDev rank 8 → 10
- GPT-6 Astra: WebDev rank 5 → 7
- Muse Wonder: LMArena text rank 6 → 7
- Muse Wonder: WebDev rank 23 → 26
- Grok 4.7: LMArena text rank 158 → 160
- Grok 4.7: WebDev rank 25 → 28
- Kimi K3: LMArena text rank 28 → 30
- Kimi K3: WebDev rank 20 → 23
- Kimi K3: providers 28 → 29
- Gemma 4 31B (open): WebDev rank 118 → 121
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
