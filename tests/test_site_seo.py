from html.parser import HTMLParser
from pathlib import Path

from scripts.site_config import SITE_URL

HTML = (Path(__file__).parent.parent / "site" / "index.html").read_text(encoding="utf-8")


class Head(HTMLParser):
    def __init__(self):
        super().__init__()
        self.meta = {}
        self.links = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "meta":
            key = a.get("property") or a.get("name")
            if key and "content" in a:
                self.meta[key] = a["content"]
        elif tag == "link":
            self.links.append(a)


def parse():
    p = Head()
    p.feed(HTML)
    return p


REQUIRED = [
    "og:title", "og:description", "og:type", "og:url", "og:image",
    "og:image:width", "og:image:height", "og:locale",
    "twitter:card", "twitter:title", "twitter:description", "twitter:image",
]


def test_site_url_default():
    assert SITE_URL == "https://example.github.io/autodev-sandbox/"
    assert SITE_URL.endswith("/")


def test_meta_og_twitter_full_and_nonempty():
    meta = parse().meta
    for k in REQUIRED:
        assert meta.get(k, "").strip(), k
    assert meta["og:type"] == "website"
    assert meta["og:image:width"] == "1200"
    assert meta["og:image:height"] == "630"
    assert meta["og:locale"] == "vi_VN"
    assert meta["twitter:card"] == "summary_large_image"


def test_canonical_present_once():
    c = [l for l in parse().links if l.get("rel") == "canonical"]
    assert len(c) == 1 and c[0].get("href", "").strip()


def test_absolute_urls_start_with_site_url():
    p = parse()
    canon = next(l["href"] for l in p.links if l.get("rel") == "canonical")
    urls = [canon, p.meta["og:url"], p.meta["og:image"], p.meta["twitter:image"]]
    for u in urls:
        assert u.startswith(SITE_URL), u
    assert p.meta["og:image"].endswith("og.png")


SITE = Path(__file__).parent.parent / "site"


def test_og_svg_has_viewbox_and_brand():
    svg = (SITE / "og.svg").read_text(encoding="utf-8")
    assert 'viewBox="0 0 1200 630"' in svg
    assert "Lười Code Studio" in svg


def test_og_png_size_and_fresh():
    from scripts.screenshot import png_size

    png = SITE / "og.png"
    assert png_size(png) == (1200, 630)
    assert png.stat().st_size > 5 * 1024
    assert png.stat().st_mtime >= (SITE / "og.svg").stat().st_mtime


def test_favicon_valid_svg_and_linked():
    import xml.etree.ElementTree as ET

    root = ET.parse(SITE / "favicon.svg").getroot()
    assert root.tag.endswith("svg")
    icons = [l for l in parse().links if l.get("rel") == "icon"]
    assert len(icons) == 1
    assert icons[0]["type"] == "image/svg+xml"
    assert (SITE / icons[0]["href"]).exists()


def test_robots_and_sitemap_use_site_url():
    import xml.etree.ElementTree as ET

    robots = (SITE / "robots.txt").read_text(encoding="utf-8").splitlines()
    assert "Allow: /" in robots
    assert f"Sitemap: {SITE_URL}sitemap.xml" in robots
    root = ET.parse(SITE / "sitemap.xml").getroot()
    locs = [e.text for e in root.iter() if e.tag.endswith("loc")]
    assert SITE_URL in locs


def test_parse_size():
    import pytest

    from scripts.screenshot import parse_size

    assert parse_size("1200x630") == (1200, 630)
    for bad in ("", "abc", "0x5", "10", "-1x5"):
        with pytest.raises(ValueError):
            parse_size(bad)
