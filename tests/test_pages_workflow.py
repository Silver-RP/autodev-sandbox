import re
from pathlib import Path

from scripts.site_config import SITE_URL

ROOT = Path(__file__).parent.parent
WF = (ROOT / ".github" / "workflows" / "pages.yml").read_text()
PAGES = [ROOT / "site" / "index.html", ROOT / "site" / "en" / "index.html"]


def test_workflow_pins_four_actions():
    for a in (
        "actions/checkout@v4",
        "actions/configure-pages@v5",
        "actions/upload-pages-artifact@v3",
        "actions/deploy-pages@v4",
    ):
        assert re.search(rf"uses:\s*{re.escape(a)}\s*$", WF, re.MULTILINE), a


def test_workflow_permissions_triggers_concurrency():
    perms = re.search(r"^permissions:\n((?:  .*\n)+)", WF, re.MULTILINE).group(1)
    got = dict(re.findall(r"^\s+([\w-]+):\s*(\w+)\s*$", perms, re.MULTILINE))
    assert got == {"pages": "write", "id-token": "write", "contents": "read"}
    assert re.search(r"branches:\s*\[main\]", WF)
    assert "workflow_dispatch:" in WF
    assert re.search(r"group:\s*pages", WF)
    assert re.search(r"cancel-in-progress:\s*false", WF)


def test_workflow_uploads_site_dir_and_injects_sha():
    assert re.search(r"^\s+path:\s*site\s*$", WF, re.MULTILINE)
    assert "${{ github.sha }}" in WF
    assert 'content="dev"' in WF


def test_no_placeholder_domain_and_urls_use_site_url():
    assert "example.github.io" not in SITE_URL
    for p in (ROOT / "site").rglob("*"):
        if p.suffix in {".html", ".txt", ".xml", ".svg", ".css", ".js"}:
            assert "example.github.io" not in p.read_text(), p
    for p in PAGES:
        for u in re.findall(r'(?:href|content)="(https?://[^"]+)"', p.read_text()):
            if "autodev-sandbox" in u:
                assert u.startswith(SITE_URL), (p, u)


def test_pages_have_version_placeholder_once():
    for p in PAGES:
        assert p.read_text().count('<meta name="version" content="dev">') == 1, p
