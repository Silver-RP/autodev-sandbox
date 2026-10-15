import re
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from test_design_doc import palette

SITE = Path(__file__).parent.parent / "site"
HTML = (SITE / "index.html").read_text(encoding="utf-8")
CSS = (SITE / "style.css").read_text(encoding="utf-8")
HEXRE = re.compile(r"#[0-9A-Fa-f]{6}\b|#[0-9A-Fa-f]{3}\b")


def blocks(css):
    """Tách css thành (selector, body) cấp trên cùng; @media giữ nguyên làm một khối."""
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


def strip_comments(css):
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.DOTALL)
    return re.sub(r"@import\s+url\([^)]*\)\s*;", "", css)


def test_root_hex_equal_light_palette_from_doc():
    light = {h.upper() for h in palette("Sáng")}
    root = [b for s, b in blocks(strip_comments(CSS)) if s == ":root"]
    assert root, "thiếu :root"
    found = {h.upper() for b in root for h in HEXRE.findall(b)}
    assert found == light, (found ^ light)


def test_no_loose_hex_outside_root():
    rest = [
        f"{s}{{{b}}}"
        for s, b in blocks(strip_comments(CSS))
        if s != ":root"
    ]
    assert not HEXRE.findall("\n".join(rest))


def test_root_tokens_named_with_prefixes():
    root = "".join(b for s, b in blocks(strip_comments(CSS)) if s == ":root")
    names = set(re.findall(r"(--[\w-]+)\s*:", root))
    assert any(n.startswith("--color-") for n in names)
    assert any(n.startswith("--font-") for n in names)
    assert any(n.startswith("--space-") for n in names)


def test_google_fonts_preconnect_and_swap():
    for host in ("https://fonts.googleapis.com", "https://fonts.gstatic.com"):
        assert re.search(
            rf'<link[^>]*rel="preconnect"[^>]*href="{re.escape(host)}"', HTML
        ), host
    assert re.search(
        r'<link[^>]*rel="preconnect"[^>]*href="https://fonts.gstatic.com"[^>]*crossorigin', HTML
    )
    # test_site.py cấm >1 <link rel=stylesheet>, nên URL font nằm trong @import của style.css
    urls = re.findall(r'https://fonts.googleapis.com/css2\?[^"\')\s]+', HTML + CSS)
    assert urls
    u = urls[0].replace("&amp;", "&")
    assert "display=swap" in u
    assert "Baloo+2" in u and "Be+Vietnam+Pro" in u
    assert "subset=vietnamese" in u or "text=" in u


def test_font_families_have_fallbacks():
    assert re.search(r'"Baloo 2",\s*"Arial Rounded MT Bold",\s*system-ui,\s*sans-serif', CSS)
    assert re.search(r'"Be Vietnam Pro",\s*system-ui,\s*sans-serif', CSS)


def test_headings_use_clamp_scale():
    assert re.search(r"h1\s*\{[^}]*clamp\(\s*40px[^}]*64px", CSS)
    assert re.search(r"h2\s*\{[^}]*clamp\(\s*28px[^}]*40px", CSS)


def test_layout_frame():
    assert "72rem" in CSS
    for tag in ("<header", "<footer", "<main"):
        assert tag in HTML
    assert HTML.count("<section") == 4


def _can_measure():
    import socket

    from scripts import screenshot as sh

    try:
        sh.chrome_path()
        socket.create_connection(("fonts.googleapis.com", 443), timeout=3).close()
    except (RuntimeError, OSError):
        return False
    return True


@pytest.mark.skipif(not _can_measure(), reason="không có Chrome hoặc không có mạng")
def test_h1_font_loaded_and_differs_from_body():
    from scripts import page_metrics as pm

    metrics = pm.collect(SITE, [1280], ["light"])[0]
    h1 = metrics["h1"]
    assert h1["font_size"] >= 40
    assert h1["font_family"] != metrics["body_font"]
    assert "Baloo 2" in h1["font_family"]
