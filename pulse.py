#!/usr/bin/env python3
"""Daily snapshot of frontier AI models across public leaderboards.

Sources (all free, no API key): LMArena (text + WebDev), Epoch AI Capabilities Index,
OpenRouter's public endpoints API. Writes the README table, chart-{light,dark}.svg
and appends to data/history.csv.
"""
import csv
import io
import json
import re
import sys
import urllib.request
import zipfile
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
from html import escape

ARENA = "https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset/resolve/main/{}-00000-of-00001.parquet"
EPOCH = "https://epoch.ai/data/benchmark_data.zip"
OPENROUTER = "https://openrouter.ai/api/v1/models/{}/endpoints"
HISTORY = "data/history.csv"

# Fixed lab -> color slot; a lab keeps its color forever (validated palette, light/dark steps)
LABS = ["google", "anthropic", "openai", "meta"]
LAB_NAMES = {"google": "Google", "anthropic": "Anthropic", "openai": "OpenAI", "meta": "Meta"}
THEMES = {
    "light": {"series": ["#2a78d6", "#eb6834", "#1baf7a", "#eda100"], "surface": "#ffffff",
              "ink": "#0b0b0b", "ink2": "#52514e", "muted": "#898781", "grid": "#e1e0d9", "axis": "#c3c2b7"},
    "dark": {"series": ["#3987e5", "#d95926", "#199e70", "#c98500"], "surface": "#0d1117",
             "ink": "#f0efec", "ink2": "#c3c2b7", "muted": "#898781", "grid": "#2c2c2a", "axis": "#383835"},
}


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "model-pulse (github.com/vmitchell/model-pulse)"})
    with urllib.request.urlopen(req, timeout=180) as r:
        return r.read()


# ---------- fetch ----------

def arena_rows(path):
    import pyarrow.compute as pc
    import pyarrow.parquet as pq
    cols = ["model_name", "organization", "rating", "rank", "category", "leaderboard_publish_date"]
    t = pq.read_table(io.BytesIO(get(ARENA.format(path))), columns=cols)
    rows = t.filter(pc.equal(t["category"], "overall")).to_pylist()
    if not rows:
        sys.exit(f"LMArena {path}: no 'overall' rows, did the format change?")
    return rows


def epoch_eci():
    z = zipfile.ZipFile(io.BytesIO(get(EPOCH)))
    name = next((n for n in z.namelist() if n.endswith("epoch_capabilities_index/eci_scores.csv")), None)
    if not name:
        sys.exit("Epoch zip: eci_scores.csv missing, did the format change?")
    rows = csv.DictReader(io.TextIOWrapper(z.open(name), encoding="utf-8"))
    return {r["Display name"]: float(r["eci"]) for r in rows}


def openrouter(model_id):
    try:
        eps = json.loads(get(OPENROUTER.format(model_id)))["data"]["endpoints"]
    except Exception as e:  # one model failing shouldn't sink the whole snapshot
        print(f"warning: OpenRouter {model_id}: {e}", file=sys.stderr)
        return None
    return summarize_endpoints(eps)


# ---------- pure logic (tested) ----------

def summarize_endpoints(eps):
    up = [e["uptime_last_1d"] for e in eps if e.get("uptime_last_1d") is not None]
    prices = [float(e["pricing"]["completion"]) * 1e6 for e in eps if e.get("pricing", {}).get("completion")]
    quants = sorted({e["quantization"] for e in eps if e.get("quantization") not in (None, "", "unknown")})
    return {
        "or_providers": len(eps),
        "or_uptime": round(sum(up) / len(up), 1) if up else None,
        "or_price_out": round(min(prices), 2) if prices else None,
        "or_quant": "/".join(quants) or None,
    }


def best_variant(rows, base):
    """Best-rated arena entry for a model: exact name or a '(High)'-style variant, never 'Base Full (Max)'."""
    hits = [r for r in rows if r["model_name"] == base or r["model_name"].startswith(base + " (")]
    return max(hits, key=lambda r: r["rating"]) if hits else None


def latest(rows):
    d = max(r["leaderboard_publish_date"] for r in rows)
    return [r for r in rows if r["leaderboard_publish_date"] == d], d


def snapshot(models, text, web, eci, orinfo):
    out = []
    for m in models:
        t, w = best_variant(text, m["arena"]), best_variant(web, m["arena"])
        row = {
            "model": m["name"],
            "arena_text_rank": int(t["rank"]) if t else None,
            "arena_text_rating": round(t["rating"]) if t else None,
            "arena_webdev_rank": int(w["rank"]) if w else None,
            "epoch_eci": eci.get(m["epoch"]) if m["epoch"] else None,
        }
        row.update(orinfo.get(m["name"]) or {})
        out.append(row)
    return out


def lab_race(rows, days=365):
    """{lab: [(date, best rating, model)]} for each leaderboard update in the window."""
    end = max(r["leaderboard_publish_date"] for r in rows)
    start = (date.fromisoformat(end) - timedelta(days=days)).isoformat()
    best = defaultdict(dict)
    for r in rows:
        d, lab = r["leaderboard_publish_date"], r["organization"]
        if d < start or lab not in LABS:
            continue
        if lab not in best[d] or r["rating"] > best[d][lab][0]:
            best[d][lab] = (r["rating"], r["model_name"])
    return {lab: [(d, best[d][lab][0], best[d][lab][1]) for d in sorted(best) if lab in best[d]] for lab in LABS}


TRACKED = {"arena_text_rank": "LMArena text rank", "arena_webdev_rank": "WebDev rank", "epoch_eci": "Epoch ECI",
           "or_providers": "providers", "or_quant": "precision", "or_price_out": "cheapest output $/M"}


def changes(prev, snap):
    """Human-readable diffs vs the previous snapshot: the drift signal."""
    out = []
    for row in snap:
        for k, label in TRACKED.items():
            old, new = prev.get((row["model"], k)), row.get(k)
            if old is not None and new is not None and str(old) != str(new):
                out.append(f"{row['model']}: {label} {old} → {new}")
    return out


def fmt(v, kind=""):
    if v is None:
        return "—"
    if kind == "rank":
        return f"#{v}"
    if kind == "pct":
        return f"{v:g}%"
    if kind == "usd":
        return f"${v:.2f}"
    return f"{v:g}" if isinstance(v, float) else str(v)


def render_table(snap):
    lines = ["| Model | LMArena text | LMArena WebDev | Epoch ECI | Providers | Uptime 24h | Cheapest output $/M | Precision |",
             "|---|---|---|---|---|---|---|---|"]
    for r in snap:
        text = f"{fmt(r['arena_text_rank'], 'rank')} ({fmt(r['arena_text_rating'])})" if r["arena_text_rank"] else "—"
        lines.append(f"| {r['model']} | {text} | {fmt(r['arena_webdev_rank'], 'rank')} | {fmt(r['epoch_eci'])} | "
                     f"{fmt(r.get('or_providers'))} | {fmt(r.get('or_uptime'), 'pct')} | "
                     f"{fmt(r.get('or_price_out'), 'usd')} | {fmt(r.get('or_quant'))} |")
    return "\n".join(lines)


def update_readme(readme, block):
    new, n = re.subn(r"(<!-- pulse:start -->).*?(<!-- pulse:end -->)", lambda m: f"{m[1]}\n{block}\n{m[2]}", readme, flags=re.S)
    if n != 1:
        sys.exit("README.md: pulse markers missing")
    return new


def nice_ticks(lo, hi):
    step = next(s for s in (10, 25, 50, 100, 200) if (hi - lo) / s <= 6)
    first = int(lo // step) * step
    return [first + i * step for i in range(int((hi - first) // step) + 2) if first + i * step <= hi + step], step


def render_chart(race, theme):
    c = THEMES[theme]
    W, H, L, R, T, B = 880, 400, 52, 168, 52, 66
    pts = [p for s in race.values() for p in s]
    ticks, step = nice_ticks(min(p[1] for p in pts), max(p[1] for p in pts))
    y0, y1 = ticks[0], ticks[-1]
    d0, d1 = date.fromisoformat(min(p[0] for p in pts)), date.fromisoformat(max(p[0] for p in pts))
    span = max((d1 - d0).days, 1)
    X = lambda d: L + (date.fromisoformat(d) - d0).days / span * (W - L - R)
    Y = lambda v: T + (y1 - v) / (y1 - y0) * (H - T - B)
    font = 'font-family="system-ui,-apple-system,Segoe UI,sans-serif"'
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" {font} role="img" aria-labelledby="t d">',
         f'<title id="t">Best LMArena text rating by lab, {d0:%b %Y} to {d1:%b %Y}</title>',
         '<desc id="d">' + escape("; ".join(f"{LAB_NAMES[l]} {round(v[-1][1])} ({v[-1][2]})" for l, v in race.items() if v)) + '</desc>',
         f'<text x="{L}" y="26" font-size="17" font-weight="600" fill="{c["ink"]}">Who leads the frontier?</text>']
    x, ly = L, H - 14  # legend row along the bottom
    for i, lab in enumerate(LABS):
        s.append(f'<line x1="{x}" y1="{ly - 4}" x2="{x + 16}" y2="{ly - 4}" stroke="{c["series"][i]}" stroke-width="2" stroke-linecap="round"/>'
                 f'<text x="{x + 22}" y="{ly}" font-size="12" fill="{c["ink2"]}">{LAB_NAMES[lab]}</text>')
        x += 36 + 6.4 * len(LAB_NAMES[lab])
    # CC BY 4.0 requires crediting LMArena wherever the chart is shown
    s.append(f'<text x="{W - R}" y="{ly}" font-size="11" fill="{c["muted"]}" text-anchor="end">LMArena text rating · data CC BY 4.0</text>')
    for v in ticks:
        s.append(f'<line x1="{L}" x2="{W - R}" y1="{Y(v):.1f}" y2="{Y(v):.1f}" stroke="{c["grid"] if v != y0 else c["axis"]}" stroke-width="1"/>'
                 f'<text x="{L - 8}" y="{Y(v) + 4:.1f}" font-size="11" fill="{c["muted"]}" text-anchor="end" style="font-variant-numeric:tabular-nums">{v}</text>')
    m = date(d0.year, d0.month, 1)
    while m <= d1:
        if m >= d0 and m.month % 2 == 1:
            label = m.strftime("%b") if m.month != 1 else m.strftime("%b %Y")
            s.append(f'<text x="{X(m.isoformat()):.1f}" y="{H - B + 18}" font-size="11" fill="{c["muted"]}" text-anchor="middle">{label}</text>')
        m = date(m.year + (m.month == 12), m.month % 12 + 1, 1)
    ends = []
    for i, lab in enumerate(LABS):
        series = race.get(lab) or []
        if not series:
            continue
        col = c["series"][i]
        path = " ".join(f"{X(d):.1f},{Y(v):.1f}" for d, v, _ in series)
        s.append(f'<polyline points="{path}" fill="none" stroke="{col}" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"/>')
        for d, v, name in series:  # hover targets when the SVG is opened directly
            s.append(f'<circle cx="{X(d):.1f}" cy="{Y(v):.1f}" r="6" fill="transparent"><title>{escape(f"{LAB_NAMES[lab]} · {d} · {round(v)} · {name}")}</title></circle>')
        d, v, name = series[-1]
        s.append(f'<circle cx="{X(d):.1f}" cy="{Y(v):.1f}" r="4" fill="{col}" stroke="{c["surface"]}" stroke-width="2"/>')
        ends.append([Y(v), Y(v), lab, round(v)])
    ends.sort()
    for a, b in zip(ends, ends[1:]):  # keep end labels 15px apart; leader lines tie them back
        b[1] = max(b[1], a[1] + 15)
    for y, ly, lab, v in ends:
        lx = W - R + 14
        if abs(ly - y) > 0.5:
            s.append(f'<polyline points="{W - R + 5},{y:.1f} {lx - 4},{ly:.1f}" fill="none" stroke="{c["axis"]}" stroke-width="1"/>')
        s.append(f'<text x="{lx}" y="{ly + 4:.1f}" font-size="12" fill="{c["ink"]}">{LAB_NAMES[lab]} <tspan fill="{c["ink2"]}" style="font-variant-numeric:tabular-nums">{v}</tspan></text>')
    s.append("</svg>")
    return "\n".join(s)


# ---------- history ----------

def read_history():
    try:
        with open(HISTORY, newline="") as f:
            return list(csv.DictReader(f))
    except FileNotFoundError:
        return []


def write_history(rows):
    with open(HISTORY, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["date", "model", "metric", "value"])
        w.writeheader()
        w.writerows(rows)


def main():
    today = datetime.now(timezone.utc).date().isoformat()
    models = json.load(open("models.json"))
    full = arena_rows("text/full")
    text, arena_date = latest(full)
    web, _ = latest(arena_rows("webdev/latest"))
    eci = epoch_eci()
    orinfo = {m["name"]: openrouter(m["openrouter"]) for m in models}
    if not any(orinfo.values()):
        sys.exit("OpenRouter: every request failed")
    snap = snapshot(models, text, web, eci, orinfo)
    for m in models:
        if not best_variant(text, m["arena"]):
            print(f"warning: {m['name']} not found on LMArena text as '{m['arena']}'", file=sys.stderr)
        if m["epoch"] and m["epoch"] not in eci:
            print(f"warning: {m['name']} not found in Epoch as '{m['epoch']}'", file=sys.stderr)

    hist = [r for r in read_history() if r["date"] != today]  # reruns on the same day replace that day
    prev = {(r["model"], r["metric"]): r["value"] for r in hist}  # rows are in date order, so the last value wins
    diff = changes(prev, snap)
    hist += [{"date": today, "model": r["model"], "metric": k, "value": v}
             for r in snap for k, v in r.items() if k != "model" and v is not None]
    write_history(hist)

    for theme in THEMES:
        with open(f"chart-{theme}.svg", "w") as f:
            f.write(render_chart(lab_race(full), theme))
    changelog = "\n".join(f"- {c}" for c in diff) or "- No changes since the last snapshot."
    block = (f"_Snapshot {today} · LMArena published {arena_date}_\n\n{render_table(snap)}\n\n"
             f"**Changes since the last snapshot**\n\n{changelog}")
    with open("README.md") as f:
        readme = update_readme(f.read(), block)
    with open("README.md", "w") as f:
        f.write(readme)
    print(f"ok: {len(snap)} models, {len(diff)} changes")


if __name__ == "__main__":
    main()
