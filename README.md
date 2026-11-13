# model-pulse

A daily check on the frontier AI models, built from public leaderboards that often disagree with each other.

Each day a GitHub Action pulls human-preference rankings (LMArena), a benchmark-based capability score (Epoch AI) and live serving data (OpenRouter). It puts them side by side and records what changed: a model sliding in the rankings, a price cut, or a provider quietly switching to lower-precision weights.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="chart-dark.svg">
  <img alt="Line chart of the best LMArena text rating per lab over the last 12 months, for Google, Anthropic, OpenAI and Meta" src="chart-light.svg">
</picture>

## Today

<!-- pulse:start -->
_Snapshot 2026-11-13 · LMArena published 2026-11-11_

| Model | LMArena text | LMArena WebDev | Epoch ECI | Providers | Uptime 24h | Cheapest output $/M | Precision |
|---|---|---|---|---|---|---|---|
| Gemini 4 Argon | #2 (1529) | #13 | 166.48 | 6 | 91.7% | $5.00 | — |
| Claude Opus 5.5 | #3 (1514) | #2 | 168.54 | 11 | 99.2% | $20.00 | — |
| Claude Fable 5.1 | #4 (1512) | #7 | 166.99 | 5 | 98.7% | $50.00 | — |
| Claude Sonnet 5.5 | #34 (1469) | #3 | 166.56 | 10 | 99.2% | $10.00 | — |
| GPT-6.1 Sol | #66 (1445) | #6 | 168.48 | 9 | 98.9% | $5.00 | — |
| GPT-6 Astra | #78 (1440) | #5 | 169 | 8 | 99.9% | $25.00 | — |
| Muse Wonder | #6 (1503) | #22 | 161.68 | 2 | 99.3% | $20.00 | — |
| Grok 4.7 | #158 (1400) | #24 | 156.18 | 6 | 99.5% | $6.00 | — |
| Kimi K3 | #28 (1475) | #19 | 158.58 | 28 | 97.7% | $9.50 | fp4/fp8/mxfp4 |
| Gemma 4 31B (open) | #73 (1443) | #117 | — | 18 | 97.6% | $0.10 | bf16/fp4/fp8 |

**Changes since the last snapshot**

- Gemini 4 Argon: WebDev rank 12 → 13
- GPT-6.1 Sol: LMArena text rank 62 → 66
- GPT-6 Astra: LMArena text rank 77 → 78
- Muse Wonder: WebDev rank 21 → 22
- Grok 4.7: LMArena text rank 160 → 158
- Grok 4.7: WebDev rank 23 → 24
- Kimi K3: LMArena text rank 27 → 28
- Kimi K3: WebDev rank 18 → 19
- Kimi K3: providers 26 → 28
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
