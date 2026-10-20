"""R15 dev-02 (H-04, H-05): font tải thật qua document.fonts; giảm chuyển động trong CSS."""

import re
import shutil
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from test_site_motion import needs_net
from test_tools import needs_chrome

from scripts import page_metrics as pm

SITE = Path(__file__).parent.parent / "site"
CSS = (SITE / "style.css").read_text(encoding="utf-8")
PAGES = ["/index.html", "/en/index.html"]
IDS = ["vi", "en"]
FAMILIES = ("Baloo 2", "Be Vietnam Pro")
CHECKS = ('700 40px "Baloo 2"', '400 16px "Be Vietnam Pro"')


def font_problems(m):
    """Trả danh sách lỗi font từ số đo của page_metrics (rỗng = đạt)."""
    out = []
    fonts = m.get("fonts") or {"faces": [], "check": {}}
    for fam in FAMILIES:
        if not any(f["family"] == fam and f["status"] == "loaded" for f in fonts["faces"]):
            out.append(f"không có FontFace {fam} trạng thái loaded")
    for q in CHECKS:
        if fonts["check"].get(q) is not True:
            out.append(f"fonts.check({q}) không true")
    h1 = m["h1"]
    if "Baloo 2" not in h1["font_family"]:
        out.append("h1 không dùng Baloo 2")
    if h1["font_family"] == m["body_font"]:
        out.append("h1 cùng font với thân bài")
    return out


def strip_font_links(site, dest):
    shutil.copytree(site, dest)
    for f in dest.rglob("index.html"):
        t = f.read_text(encoding="utf-8")
        t = re.sub(r"<noscript>.*?</noscript>", "", t, flags=re.DOTALL)
        t = re.sub(r"<link[^>]*fonts\.(googleapis|gstatic)\.com[^>]*>", "", t)
        f.write_text(t, encoding="utf-8")
    return dest


# ---- font ----


@needs_chrome
@needs_net
@pytest.mark.parametrize("page", PAGES, ids=IDS)
def test_fonts_loaded_through_document_fonts(page):
    m = pm.collect(SITE, [1280], ["light"], pages=[page])[0]
    assert font_problems(m) == []


@needs_chrome
@pytest.mark.parametrize("page", PAGES, ids=IDS)
def test_negative_no_font_links_is_caught(tmp_path, page):
    bare = strip_font_links(SITE, tmp_path / "site")
    m = pm.collect(bare, [1280], ["light"], pages=[page])[0]
    problems = font_problems(m)
    assert any("FontFace" in p for p in problems), problems


def test_font_problems_flags_empty_and_check_only():
    base = {"h1": {"font_family": '"Baloo 2", cursive'}, "body_font": "sans-serif"}
    assert font_problems(base)  # thiếu khối fonts
    fake = {**base, "fonts": {"faces": [], "check": {q: True for q in CHECKS}}}
    assert any("FontFace" in p for p in font_problems(fake))
    ok = {**base, "fonts": {"faces": [{"family": f, "weight": "400", "status": "loaded"}
                                      for f in FAMILIES],
                            "check": {q: True for q in CHECKS}}}
    assert font_problems(ok) == []
    unloaded = {**ok, "fonts": {**ok["fonts"], "faces": [
        {"family": f, "weight": "400", "status": "unloaded"} for f in FAMILIES]}}
    assert font_problems(unloaded)


# ---- reduced motion ----

REDUCE_MEDIA = "@media (prefers-reduced-motion: reduce)"
NEEDED = ("animation-duration", "animation-iteration-count", "transition-duration",
          "scroll-behavior")


def _blocks(css):
    out, i, n = [], 0, len(css)
    while i < n:
        j = css.find("{", i)
        if j < 0:
            break
        depth, k = 1, j + 1
        while k < n and depth:
            depth += {"{": 1, "}": -1}.get(css[k], 0)
            k += 1
        out.append((css[i:j].strip(), css[j + 1 : k - 1]))
        i = k
    return out


def reduced_motion_missing(css):
    """Danh sách khai báo còn thiếu trong khối reduced-motion cấp trên cùng cho `*`."""
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.DOTALL)
    for sel, body in _blocks(css):
        if re.sub(r"\s+", " ", sel) != REDUCE_MEDIA:
            continue
        for isel, ibody in _blocks(body):
            parts = {p.strip() for p in isel.split(",")}
            if not {"*", "*::before", "*::after"} <= parts:
                continue
            decls = {
                a.strip(): b.strip()
                for a, _, b in (d.partition(":") for d in ibody.split(";"))
                if b
            }
            missing = [d for d in NEEDED if "!important" not in decls.get(d, "")]
            if not missing:
                return []
        return list(NEEDED)
    return list(NEEDED)


GOOD = (
    "@media (prefers-reduced-motion: reduce) { *, *::before, *::after {"
    " animation-duration: 0.01ms !important; animation-iteration-count: 1 !important;"
    " transition-duration: 0.01ms !important; scroll-behavior: auto !important; } }"
)


def test_reduced_motion_block_in_real_css():
    assert reduced_motion_missing(CSS) == []


def test_reduced_motion_detector_accepts_good():
    assert reduced_motion_missing("a { color: red }\n" + GOOD) == []


def test_negative_reduced_motion_only_in_comment():
    assert reduced_motion_missing("/* " + GOOD + " */ a { color: red }")


def test_negative_reduced_motion_nested_in_min_width():
    assert reduced_motion_missing("@media (min-width: 64rem) { " + GOOD + " }")


def test_negative_reduced_motion_missing_transition_duration():
    assert reduced_motion_missing(GOOD.replace("transition-duration: 0.01ms !important;", ""))


def test_negative_reduced_motion_without_important_or_wrong_selector():
    assert reduced_motion_missing(GOOD.replace(" !important", ""))
    assert reduced_motion_missing(GOOD.replace("*, *::before, *::after", "body"))
    assert reduced_motion_missing("")
