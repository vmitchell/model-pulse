import unittest
import xml.etree.ElementTree as ET

import pulse


def row(name, rating, rank=1, org="google", d="2026-10-22"):
    return {"model_name": name, "rating": rating, "rank": rank, "organization": org, "leaderboard_publish_date": d}


class Pulse(unittest.TestCase):
    def test_best_variant_picks_top_rated_variant_but_not_other_models(self):
        rows = [row("Claude Opus 5.5", 1500), row("Claude Opus 5.5 (High)", 1516),
                row("Claude Opus 5.5 Full (Max)", 1600), row("Claude Opus 5", 1490)]
        self.assertEqual(pulse.best_variant(rows, "Claude Opus 5.5")["model_name"], "Claude Opus 5.5 (High)")
        self.assertIsNone(pulse.best_variant(rows, "Claude Opus 6"))

    def test_latest_keeps_only_newest_publish_date(self):
        rows = [row("A", 1, d="2026-10-20"), row("B", 2, d="2026-10-22")]
        self.assertEqual(pulse.latest(rows), ([rows[1]], "2026-10-22"))

    def test_lab_race_takes_best_per_lab_per_date_inside_window(self):
        rows = [row("G1", 1400, org="google", d="2026-10-01"), row("G2", 1450, org="google", d="2026-10-01"),
                row("A1", 1420, org="anthropic", d="2026-10-01"), row("X", 9999, org="xai", d="2026-10-01"),
                row("old", 1300, org="google", d="2025-01-01"), row("G2", 1460, org="google", d="2026-10-22")]
        race = pulse.lab_race(rows)
        self.assertEqual(race["google"], [("2026-10-01", 1450, "G2"), ("2026-10-22", 1460, "G2")])
        self.assertEqual(race["anthropic"], [("2026-10-01", 1420, "A1")])
        self.assertEqual(race["openai"], [])
        self.assertNotIn("xai", race)

    def test_summarize_endpoints(self):
        eps = [{"uptime_last_1d": 100, "pricing": {"completion": "0.00002"}, "quantization": "unknown"},
               {"uptime_last_1d": 90, "pricing": {"completion": "0.000015"}, "quantization": "fp8"},
               {"uptime_last_1d": None, "pricing": {}, "quantization": "fp4"}]
        self.assertEqual(pulse.summarize_endpoints(eps),
                         {"or_providers": 3, "or_uptime": 95.0, "or_price_out": 15.0, "or_quant": "fp4/fp8"})

    def test_changes_reports_moves_and_ignores_new_or_missing_values(self):
        prev = {("M", "arena_text_rank"): "3", ("M", "or_quant"): "fp8", ("M", "epoch_eci"): "160.0"}
        snap = [{"model": "M", "arena_text_rank": 2, "or_quant": "fp8", "epoch_eci": None, "or_providers": 5}]
        self.assertEqual(pulse.changes(prev, snap), ["M: LMArena text rank 3 → 2"])

    def test_update_readme_replaces_only_between_markers(self):
        out = pulse.update_readme("top\n<!-- pulse:start -->\nold\n<!-- pulse:end -->\nbottom", "NEW")
        self.assertEqual(out, "top\n<!-- pulse:start -->\nNEW\n<!-- pulse:end -->\nbottom")
        with self.assertRaises(SystemExit):
            pulse.update_readme("no markers", "NEW")

    def test_nice_ticks_cover_the_range(self):
        ticks, step = pulse.nice_ticks(1433, 1526)
        self.assertLessEqual(ticks[0], 1433)
        self.assertGreaterEqual(ticks[-1], 1526)
        self.assertTrue(all(t % step == 0 for t in ticks))

    def test_chart_is_valid_svg_with_one_line_per_lab_and_separated_labels(self):
        race = {lab: [("2025-11-01", 1400 + i, "a"), ("2026-10-22", 1500 + i, "b")] for i, lab in enumerate(pulse.LABS)}
        for theme in pulse.THEMES:
            svg = pulse.render_chart(race, theme)
            root = ET.fromstring(svg)
            ns = "{http://www.w3.org/2000/svg}"
            lines = [p for p in root.iter(ns + "polyline") if p.get("stroke-width") == "2"]
            self.assertEqual(len(lines), 4)
            label_ys = sorted(float(t.get("y")) for t in root.iter(ns + "text") if float(t.get("x")) > 880 - 168)
            self.assertTrue(all(b - a >= 15 for a, b in zip(label_ys, label_ys[1:])), label_ys)


if __name__ == "__main__":
    unittest.main()
