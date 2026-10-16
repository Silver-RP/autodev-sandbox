import functools
import http.server
import re
import threading
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

import pytest

SITE = Path(__file__).resolve().parent.parent / "site"
VI = (SITE / "index.html").read_text(encoding="utf-8")
EN = (SITE / "en" / "index.html").read_text(encoding="utf-8")
SECTIONS = ["hero", "dich-vu", "cach-lam", "du-an", "hoi-dap", "lien-he"]
# ký tự tiếng Việt có dấu (ngoài Latin cơ bản): â ă ê ô ơ ư đ và thanh
VI_CHARS = re.compile(
    "[àáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ"
    "ÀÁẠẢÃÂẦẤẬẨẪĂẰẮẶẲẴÈÉẸẺẼÊỀẾỆỂỄÌÍỊỈĨÒÓỌỎÕÔỒỐỘỔỖƠỜỚỢỞỠÙÚỤỦŨƯỪỨỰỬỮỲÝỴỶỸĐ]"
)
BRAND = re.compile(r"LƯỜI CODE STUDIO|Lười Code Studio|Tiếng Việt")


class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = []
        self.sections = []
        self.h1 = 0
        self.lang = None
        self.text = []  # văn bản hiển thị + thuộc tính hiển thị/đọc được
        self._skip = 0
        self._title = False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "html":
            self.lang = a.get("lang")
        if tag == "h1":
            self.h1 += 1
        if tag == "section":
            self.sections.append(a.get("id"))
        if tag in ("script", "style"):
            self._skip += 1
        if tag == "title":
            self._title = True
        if tag == "meta" and (
            a.get("name") in ("description", "twitter:title", "twitter:description")
            or a.get("property") in ("og:title", "og:description")
        ):
            self.text.append(a.get("content") or "")
        for k in ("data-on", "data-off", "aria-label"):
            if a.get(k):
                self.text.append(a[k])

    def handle_endtag(self, tag):
        if tag in ("script", "style"):
            self._skip -= 1
        if tag == "title":
            self._title = False

    def handle_data(self, data):
        if not self._skip:
            self.text.append(data)


def parse(src):
    p = Page()
    p.feed(src)
    p.close()
    return p


def visible_vi_chars(src):
    text = " ".join(parse(src).text)
    text = BRAND.sub("", text)
    return set(VI_CHARS.findall(text))


def test_en_lang_and_single_h1():
    p = parse(EN)
    assert p.lang == "en"
    assert p.h1 == 1
    assert parse(VI).lang == "vi"


def test_en_sections_match_vi():
    assert parse(EN).sections == parse(VI).sections == SECTIONS


def test_en_has_no_vietnamese_visible_text():
    assert visible_vi_chars(EN) == set()
    # kiểm chứng bộ lọc có bắt được bản Việt
    assert visible_vi_chars(VI)


def test_en_main_js_labels_not_vietnamese():
    # nút vui: nhãn do HTML cung cấp, bản Anh không rơi về chữ Việt trong JS
    p = parse(EN)
    assert 'data-on="' in EN and 'data-off="' in EN
    assert not visible_vi_chars(EN)
    assert p.h1 == 1


def test_en_uses_shared_assets_not_copies():
    assert 'href="../style.css"' in EN
    assert 'src="../main.js"' in EN
    assert not (SITE / "en" / "style.css").exists()
    assert not (SITE / "en" / "main.js").exists()


@pytest.fixture
def base_url():
    handler = functools.partial(
        http.server.SimpleHTTPRequestHandler, directory=str(SITE)
    )
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def test_en_page_and_relative_assets_served(base_url):
    from urllib.parse import urljoin

    page_url = base_url + "/en/"
    with urllib.request.urlopen(page_url, timeout=5) as r:
        assert r.status == 200
        html = r.read().decode("utf-8")
    refs = re.findall(r'(?:href|src)="(\.\./[^"]+)"', html)
    assert "../style.css" in refs and "../main.js" in refs
    for ref in refs:
        with urllib.request.urlopen(urljoin(page_url, ref), timeout=5) as r:
            assert r.status == 200, ref
    for path in ("/style.css", "/main.js"):
        with urllib.request.urlopen(base_url + path, timeout=5) as r:
            assert r.status == 200


# ---- dev-02: hreflang, canonical, sitemap, meta ----
def _head(html):
    links, meta = [], {}
    class H(HTMLParser):
        def handle_starttag(self, tag, attrs):
            a = dict(attrs)
            if tag == "link":
                links.append(a)
            elif tag == "meta":
                k = a.get("property") or a.get("name")
                if k:
                    meta.setdefault(k, []).append(a.get("content", ""))
    H().feed(html)
    return links, meta


def _site_url():
    from scripts.site_config import SITE_URL
    return SITE_URL


@pytest.mark.parametrize("html,self_url", [(VI, ""), (EN, "en/")])
def test_hreflang_both_pages_absolute_and_correct(html, self_url):
    base = _site_url()
    links, _ = _head(html)
    alt = {l["hreflang"]: l["href"] for l in links if l.get("rel") == "alternate" and "hreflang" in l}
    assert alt == {"vi": base, "en": base + "en/", "x-default": base}
    canon = [l["href"] for l in links if l.get("rel") == "canonical"]
    assert canon == [base + self_url]


def test_en_meta_locale_and_vi_alternate():
    _, en = _head(EN)
    _, vi = _head(VI)
    assert en["og:locale"] == ["en_US"] and en["og:locale:alternate"] == ["vi_VN"]
    assert en["og:url"] == [_site_url() + "en/"]
    assert vi["og:locale"] == ["vi_VN"] and vi["og:locale:alternate"] == ["en_US"]
    for k in ("og:title", "og:description", "twitter:title", "twitter:description"):
        assert en[k][0].strip() and not VI_CHARS.search(BRAND.sub("", en[k][0])), k
    assert not VI_CHARS.search(BRAND.sub("", re.search(r"<title>(.*?)</title>", EN).group(1)))


def test_sitemap_has_both_urls_once():
    import xml.etree.ElementTree as ET
    root = ET.parse(SITE / "sitemap.xml").getroot()
    locs = [e.text for e in root.iter() if e.tag.endswith("loc")]
    assert sorted(locs) == sorted([_site_url(), _site_url() + "en/"])
