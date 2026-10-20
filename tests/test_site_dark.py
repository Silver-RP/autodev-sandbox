import re
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from test_design_doc import palette
from test_site_visual import CSS, HEXRE, HTML, blocks, strip_comments
from test_tools import needs_chrome

DARK = "@media (prefers-color-scheme: dark)"


def _tokens(body):
    return dict(re.findall(r"(--color-[\w-]+)\s*:\s*([^;]+);", body))


def _dark_root():
    css = strip_comments(CSS)
    media = [b for s, b in blocks(css) if s == DARK]
    assert len(media) == 1, "cần đúng một khối prefers-color-scheme: dark"
    inner = [b for s, b in blocks(media[0]) if s == ":root"]
    assert inner, "khối tối phải gán lại token ở :root"
    return _tokens(inner[0])


def _light_root():
    css = strip_comments(CSS)
    return _tokens("".join(b for s, b in blocks(css) if s == ":root"))


def test_dark_block_reassigns_bg_and_text_differently():
    dark, light = _dark_root(), _light_root()
    for name in ("--color-tuong-voi", "--color-muc-bang"):
        assert name in dark
        assert dark[name].strip().upper() != light[name].strip().upper()
    assert len([n for n in dark if dark[n].strip() != light.get(n, "").strip()]) >= 2


def test_dark_hex_equals_doc_dark_palette():
    dark = _dark_root()
    found = {h.upper() for v in dark.values() for h in HEXRE.findall(v)}
    assert found == {h.upper() for h in palette("Tối")}


def test_dark_block_has_only_root():
    css = strip_comments(CSS)
    media = [b for s, b in blocks(css) if s == DARK]
    media = media[0]
    assert [s for s, _ in blocks(media)] == [":root"]


EN_HTML = (Path(__file__).resolve().parent.parent / "site" / "en" / "index.html").read_text(
    encoding="utf-8"
)
PAGES = {"vi": HTML, "en": EN_HTML}


def _hex_paint_violations(html):
    out = []
    for svg in re.findall(r"<svg.*?</svg>", html, flags=re.DOTALL):
        for attr in re.findall(r'\b(?:fill|stroke)="([^"]*)"', svg):
            if HEXRE.search(attr) or not (
                attr == "none" or attr == "currentColor" or attr.startswith("var(")
            ):
                out.append(attr)
        if HEXRE.search(svg):
            out.append("hex")
    return out


@pytest.mark.parametrize("lang", list(PAGES))
def test_svg_has_no_hardcoded_hex_paint(lang):
    svgs = re.findall(r"<svg.*?</svg>", PAGES[lang], flags=re.DOTALL)
    assert svgs
    for svg in svgs:
        for attr in re.findall(r'\b(?:fill|stroke)="([^"]*)"', svg):
            assert not HEXRE.search(attr), attr
            assert attr == "none" or attr == "currentColor" or attr.startswith("var("), attr
        assert not HEXRE.search(svg)


def test_en_svg_hex_fill_is_caught():
    assert _hex_paint_violations(EN_HTML) == []
    bad = EN_HTML.replace('<path d="M20 262H380"/>', '<path d="M20 262H380" stroke="#ff0000"/>', 1)
    assert _hex_paint_violations(bad)


def test_en_svg_named_color_is_caught():
    bad = EN_HTML.replace('stroke="currentColor"', 'stroke="red"', 1)
    assert _hex_paint_violations(bad)


def test_en_svg_gradient_hex_in_style_is_caught():
    bad = EN_HTML.replace("<svg ", '<svg data-x="#abc123" ', 1)
    assert _hex_paint_violations(bad)


@needs_chrome
def test_dark_contrast_script_passes():
    from scripts import contrast

    rc = contrast.main(["--modes", "dark", "--widths", "1280"])
    assert rc == 0
