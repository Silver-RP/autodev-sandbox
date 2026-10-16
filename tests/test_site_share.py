import re
import xml.etree.ElementTree as ET
from pathlib import Path

SITE = Path(__file__).parent.parent / "site"
HEXRE = re.compile(r"#[0-9a-f]{6}\b|#[0-9a-f]{3}\b", re.IGNORECASE)
DRAW = {"path", "rect", "circle", "ellipse", "line", "polygon", "polyline"}


def light_tokens():
    css = (SITE / "style.css").read_text(encoding="utf-8")
    root = css[css.index(":root") :].split("}", 1)[0]
    toks = {h.upper() for h in HEXRE.findall(root)}
    assert len(toks) >= 6
    return toks


def hero_h1():
    html = (SITE / "index.html").read_text(encoding="utf-8")
    m = re.search(r'<section id="hero">.*?<h1>(.*?)</h1>', html, re.DOTALL)
    assert m
    return re.sub(r"<[^>]+>", "", m.group(1)).strip()


def tags(path):
    root = ET.parse(path).getroot()
    return root, [e.tag.split("}")[-1] for e in root.iter()]


def test_share_images_use_only_light_tokens():
    toks = light_tokens()
    for name in ("og.svg", "favicon.svg"):
        used = {h.upper() for h in HEXRE.findall((SITE / name).read_text(encoding="utf-8"))}
        assert used, name
        assert used <= toks, (name, used - toks)


def test_og_svg_font_and_greeting_from_hero():
    svg = (SITE / "og.svg").read_text(encoding="utf-8")
    greeting = hero_h1()
    assert greeting
    assert "Baloo 2" in svg
    assert "Be Vietnam Pro" in svg
    assert greeting in svg
    assert "dòng lệnh" not in svg
    assert "Helvetica" not in svg


def test_og_svg_has_chairs_and_cup():
    _, names = tags(SITE / "og.svg")
    assert sum(n in DRAW for n in names) >= 8


def test_favicon_shape_no_text():
    root, names = tags(SITE / "favicon.svg")
    assert root.get("viewBox")
    assert "text" not in names
    assert sum(n in DRAW for n in names) >= 2
