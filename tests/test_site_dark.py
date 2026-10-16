import re
import sys
from pathlib import Path

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


def test_svg_has_no_hardcoded_hex_paint():
    svgs = re.findall(r"<svg.*?</svg>", HTML, flags=re.DOTALL)
    assert svgs
    for svg in svgs:
        for attr in re.findall(r'\b(?:fill|stroke)="([^"]*)"', svg):
            assert not HEXRE.search(attr), attr
            assert attr == "none" or attr == "currentColor" or attr.startswith("var("), attr
        assert not HEXRE.search(svg)


@needs_chrome
def test_dark_contrast_script_passes():
    from scripts import contrast

    rc = contrast.main(["--modes", "dark", "--widths", "1280"])
    assert rc == 0
