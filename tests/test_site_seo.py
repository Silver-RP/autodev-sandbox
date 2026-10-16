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
