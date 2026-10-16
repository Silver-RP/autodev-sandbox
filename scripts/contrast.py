"""Kiểm tương phản WCAG AA cho từng khối chữ trên trang thật (qua page_metrics)."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts import page_metrics as pm


def _lin(c: float) -> float:
    c /= 255
    return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4


def parse_color(s: str) -> tuple[int, int, int]:
    s = s.strip()
    m = re.fullmatch(r"#([0-9a-fA-F]{3}|[0-9a-fA-F]{6})", s)
    if m:
        h = m.group(1)
        if len(h) == 3:
            h = "".join(ch * 2 for ch in h)
        return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    m = re.match(r"rgba?\(\s*([\d.]+)[,\s]+([\d.]+)[,\s]+([\d.]+)", s)
    if m:
        r, g, b = (round(float(x)) for x in m.groups())
        return r, g, b
    raise ValueError(f"không đọc được màu: {s!r}")


def luminance(rgb) -> float:
    r, g, b = (_lin(v) for v in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def ratio(fg: str, bg: str) -> float:
    a, b = luminance(parse_color(fg)), luminance(parse_color(bg))
    hi, lo = max(a, b), min(a, b)
    return (hi + 0.05) / (lo + 0.05)


def is_large(size: float, weight: int) -> bool:
    return size >= 24 or (size >= 18.66 and weight >= 700)


def threshold(size: float, weight: int) -> float:
    return 3.0 if is_large(size, weight) else 4.5


def failures(results: list[dict]) -> list[dict]:
    bad = []
    for r in results:
        for c in r.get("colors", []):
            need = threshold(c.get("font_size", 16), c.get("font_weight", 400))
            got = ratio(c["color"], c["background"])
            if got < need:
                bad.append({
                    "width": r["width"], "mode": r["mode"],
                    "selector": c.get("selector", "?"),
                    "color": c["color"], "background": c["background"],
                    "ratio": got, "need": need,
                })
    return bad


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--site", default=str(pm.ROOT / "site"))
    ap.add_argument("--widths", default="1280")
    ap.add_argument("--modes", default="light,dark")
    a = ap.parse_args(argv)
    widths = [int(w) for w in a.widths.split(",") if w]
    modes = [m for m in a.modes.split(",") if m]
    for m in modes:
        if m not in ("light", "dark"):
            ap.error(f"chế độ không hợp lệ: {m}")
    bad = failures(pm.collect(a.site, widths, modes))
    if bad:
        print("mode  width  selector  color  background  ratio  need")
        for b in bad:
            print(f"{b['mode']}  {b['width']}  {b['selector']}  {b['color']}  "
                  f"{b['background']}  {b['ratio']:.2f}  {b['need']}")
        return 1
    print("OK: mọi cặp màu đạt WCAG AA")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
