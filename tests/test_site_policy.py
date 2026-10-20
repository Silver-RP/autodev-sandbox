import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent))
from _policy import check

sys.path.insert(0, str(Path(__file__).parent.parent))
from scripts.site_config import SITE_URL

SITE = Path(__file__).parent.parent / "site"
GSAP = (
    '<script src="https://cdn.jsdelivr.net/npm/gsap@3.12.5/dist/gsap.min.js" '
    'integrity="sha384-abc" crossorigin="anonymous" defer></script>'
)


def test_current_site_has_no_violations():
    files = [p for p in SITE.rglob("*") if p.suffix in (".html", ".css", ".svg")]
    assert files
    bad = []
    for p in files:
        text = p.read_text(encoding="utf-8")
        v = check(html=text) if p.suffix != ".css" else check(css=text)
        bad += [f"{p}: {x}" for x in v]
    assert bad == []


@pytest.mark.parametrize(
    "kw",
    [
        {"html": '<link rel="stylesheet" href="https://evil.example/x.css">'},
        {"css": "@import url(https://evil.example/x.css);"},
        {"html": GSAP.replace("gsap@3.12.5", "gsap@latest")},
        {"html": GSAP.replace("gsap@3.12.5", "gsap@latest/3.12.5")},  # H-02
        {"html": GSAP.replace(' integrity="sha384-abc"', "")},
        {"html": "<script>alert(1)</script>"},
        {"html": '<link href="HTTP://fonts.googleapis.com/css2?family=X">'},
    ],
)
def test_negative_cases_one_violation_each(kw):
    assert len(check(**kw)) == 1, check(**kw)


@pytest.mark.parametrize(
    "html",
    [
        '<link href="https://fonts.googleapis.com/css2?family=X&display=swap">',
        GSAP,
        '<script type="application/ld+json">{}</script>',
        '<a href="https://example.org/x">x</a>',
        '<a href="/trang">x</a>',
    ],
)
def test_positive_cases(html):
    assert check(html=html) == []


def test_missing_crossorigin_and_bad_integrity():
    assert check(html=GSAP.replace(' crossorigin="anonymous"', ""))
    assert check(html=GSAP.replace("sha384-abc", "md5-abc"))


def test_a_http_forbidden_case_insensitive():
    assert check(html='<a href="HTTP://example.org">x</a>')


def test_css_variants_and_repeat_calls():
    assert check(css="a{background:url('http://fonts.gstatic.com/x')}")
    assert check(css='@import "https://evil.example/a.css";')
    assert check(css="a{background:url(https://fonts.gstatic.com/x.woff2)}") == []
    assert check() == []
    assert check() == []


def test_inline_script_with_other_type_and_uppercase_ldjson():
    assert check(html='<script type="module">x()</script>')
    assert check(html='<script type="APPLICATION/LD+JSON">{}</script>') == []


# --- dev-03: vá lỗ H-09, H-06 ---
SCRIPT_EXT = (
    '<script src="https://cdn.jsdelivr.net/npm/gsap@3.12.5/dist/gsap.min.js" '
    'integrity="{i}" crossorigin="anonymous" defer></script>'
)


@pytest.mark.parametrize(
    "html",
    [
        '<base href="https://evil.com/">',
        '<BASE HREF="/x/">',
        '<img src="/\\evil.com/x.png">',
        '<img src="\\\\evil.com/x.png">',
        '<img src="\\/evil.com/x.png">',
        '<img src="  /\\evil.com/x.png">',
        '<img src="x" ONLOAD="x()">',
        '<body onclick="x()">',
        '<link rel="preload" as="style" href="x.css" onload="this.rel=1">',
        '<a href=" JavaScript:alert(1)">x</a>',
        '<form action="javascript:x()"></form>',
        '<button formaction="javascript:x()">x</button>',
        '<object data="https://evil.com/x"></object>',
        '<object data="javascript:x()"></object>',
        '<svg><image href="https://evil.com/x.png"/></svg>',
        '<svg><image xlink:href="https://evil.com/x.png"/></svg>',
        '<svg><use href="https://evil.com/x.svg#a"/></svg>',
        '<form action="https://evil.com/post"></form>',
        SCRIPT_EXT.format(i=""),
        SCRIPT_EXT.format(i="sha384-"),
        SCRIPT_EXT.format(i="sha512-"),
        '<link rel="alternate" hreflang="en" href="https://evil.com/x.css">',
        '<link rel="canonical" href="https://evil.com/">',
        '<link rel="stylesheet canonical" href="https://evil.com/x.css">',
        '<link rel="canonical alternate" href="https://evil.com/x.css">',
    ],
)
def test_h09_h06_negative_variants(html):
    assert check(html=html), html
    assert check(html=html), html  # gọi lặp lại


def test_no_state_leak_between_calls():
    assert check(html="<p>ok</p>") == []
    assert check(html='<body onclick="x()">')
    assert check(html="<p>ok</p>") == []


@pytest.mark.parametrize(
    "html",
    [
        f'<link rel="alternate" hreflang="en" href="{SITE_URL}en/">',
        f'<link rel="canonical" href="{SITE_URL}">',
        '<svg><use href="#a"/></svg>',
        '<a href="/x" class="y" data-onload="1">x</a>',
        '<form action="/x"></form>',
    ],
)
def test_h06_positive(html):
    assert check(html=html) == []


def test_svg_files_are_scanned_and_sample_caught():
    svgs = list(SITE.rglob("*.svg"))
    assert svgs, "site/ phải có .svg để quét"
    for p in svgs:
        assert check(html=p.read_text(encoding="utf-8")) == [], p
    bad = '<svg xmlns="http://www.w3.org/2000/svg"><image href="https://evil.com/x"/></svg>'
    assert check(html=bad)


def test_site_scan_includes_svg():
    body = Path(__file__).read_text(encoding="utf-8").split("def test_current_site_has_no_violations")[1]
    assert '".svg"' in body.split("\ndef ")[0]


@pytest.mark.parametrize("page", ["index.html", "en/index.html"])
def test_real_pages_have_no_on_attributes(page):
    import re

    s = (SITE / page).read_text(encoding="utf-8")
    assert not re.search(r"\son[a-z]+\s*=", s, re.IGNORECASE)
    assert check(html=s) == []
