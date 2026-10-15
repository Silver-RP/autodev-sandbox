import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent))
from _policy import check

SITE = Path(__file__).parent.parent / "site"
GSAP = (
    '<script src="https://cdn.jsdelivr.net/npm/gsap@3.12.5/dist/gsap.min.js" '
    'integrity="sha384-abc" crossorigin="anonymous" defer></script>'
)


def test_current_site_has_no_violations():
    files = [p for p in SITE.rglob("*") if p.suffix in (".html", ".css")]
    assert files
    bad = []
    for p in files:
        text = p.read_text(encoding="utf-8")
        v = check(html=text) if p.suffix == ".html" else check(css=text)
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
