import copy
import re
import shutil
import subprocess
from pathlib import Path

import pytest
import yaml

from scripts.site_config import SITE_URL

ROOT = Path(__file__).parent.parent
WF_PATH = ROOT / ".github" / "workflows" / "pages.yml"
PAGES = [ROOT / "site" / "index.html", ROOT / "site" / "en" / "index.html"]
PLACEHOLDER = '<meta name="version" content="dev">'
FAKE_SHA = "0123456789abcdef0123456789abcdef01234567"
STEP_NAME = "Ghi phiên bản"


def load():
    return yaml.safe_load(WF_PATH.read_text(encoding="utf-8"))


WF = load()


def triggers(wf):
    # PyYAML (YAML 1.1) đọc khoá `on` thành True
    return wf["on"] if "on" in wf else wf[True]


def as_list(v):
    return [v] if isinstance(v, str) else list(v or [])


def _perm_keys(node):
    perms = node.get("permissions")
    return perms if isinstance(perms, dict) else {}


def workflow_problems(wf):
    """Danh sách lỗi cấu trúc về job test/build/deploy; rỗng là đạt."""
    out = []
    jobs = wf.get("jobs", {})
    test = jobs.get("test", {})
    steps = test.get("steps", [])
    runs = [str(s.get("run", "")).strip() for s in steps]
    for cmd in ("uv run ruff check .", "uv run pytest -q"):
        if cmd not in runs:
            out.append(f"jobs.test thiếu bước chạy đúng `{cmd}`")
    for key in ("continue-on-error", "if"):
        if key in test:
            out.append(f"jobs.test không được có `{key}`")
        for s in steps:
            if key in s:
                out.append(f"bước của jobs.test không được có `{key}`: {s.get('run') or s.get('uses')}")
    for name in ("build", "deploy"):
        if "if" in jobs.get(name, {}):
            out.append(f"jobs.{name} không được có `if`")
    if "test" not in as_list(jobs.get("build", {}).get("needs")):
        out.append("jobs.build.needs thiếu test")
    if "build" not in as_list(jobs.get("deploy", {}).get("needs")):
        out.append("jobs.deploy.needs thiếu build")
    top = _perm_keys(wf)
    for k in ("pages", "id-token"):
        if k in top:
            out.append(f"permissions cấp workflow không được có `{k}`")
        if k in _perm_keys(test):
            out.append(f"jobs.test.permissions không được có `{k}`")
    bperm = _perm_keys(jobs.get("build", {}))
    if "id-token" in bperm:
        out.append("jobs.build.permissions không được có `id-token`")
    if bperm.get("pages", "read") != "read":
        out.append("jobs.build.permissions.pages chỉ được là `read`")
    for name, job in jobs.items():
        t = job.get("timeout-minutes")
        if isinstance(t, bool) or not isinstance(t, (int, float)) or t <= 0:
            out.append(f"jobs.{name} thiếu timeout-minutes dương")
    return out


def all_uses(wf):
    return [s["uses"] for j in wf["jobs"].values() for s in j.get("steps", []) if "uses" in s]


def test_workflow_test_job_and_needs_chain():
    assert workflow_problems(WF) == []
    steps = WF["jobs"]["test"]["steps"]
    uses = [s.get("uses") for s in steps]
    assert "actions/checkout@v4" in uses
    assert "astral-sh/setup-uv@v3" in uses
    assert any("uv sync" in s.get("run", "") for s in steps)


def test_workflow_negative_build_without_needs_test_fails():
    bad = copy.deepcopy(WF)
    del bad["jobs"]["build"]["needs"]
    assert any("build.needs" in p for p in workflow_problems(bad))
    bad = copy.deepcopy(WF)
    bad["jobs"]["deploy"]["needs"] = []
    assert any("deploy.needs" in p for p in workflow_problems(bad))
    bad = copy.deepcopy(WF)
    bad["jobs"]["test"]["steps"] = [s for s in bad["jobs"]["test"]["steps"] if "pytest" not in s.get("run", "")]
    assert any("pytest" in p for p in workflow_problems(bad))
    # gọi lặp lại trên bản gốc không bị rò trạng thái
    assert workflow_problems(WF) == []


def test_workflow_pins_four_actions():
    uses = all_uses(WF)
    for a in (
        "actions/checkout@v4",
        "actions/configure-pages@v5",
        "actions/upload-pages-artifact@v3",
        "actions/deploy-pages@v4",
    ):
        assert a in uses, a


def test_workflow_permissions_triggers_concurrency():
    assert WF["permissions"] == {"contents": "read"}
    assert WF["jobs"]["deploy"]["permissions"] == {"pages": "write", "id-token": "write"}
    bperm = WF["jobs"]["build"]["permissions"]
    assert "id-token" not in bperm and bperm.get("pages") != "write"
    on = triggers(WF)
    assert on["push"]["branches"] == ["main"]
    assert "workflow_dispatch" in on
    assert WF["concurrency"]["group"] == "pages"
    assert WF["concurrency"]["cancel-in-progress"] is False


def test_workflow_uploads_site_dir_and_injects_sha():
    upload = [s for s in WF["jobs"]["build"]["steps"] if s.get("uses") == "actions/upload-pages-artifact@v3"]
    assert upload and upload[0]["with"]["path"] == "site"
    run = version_step_run()
    assert "${{ github.sha }}" in run
    assert 'content="dev"' in run


def version_step_run():
    steps = [s for s in WF["jobs"]["build"]["steps"] if STEP_NAME in s.get("name", "")]
    assert len(steps) == 1
    return steps[0]["run"]


def sed_shim(tmp_path):
    """Thư mục PATH có `sed` hiểu `-i` kiểu GNU; BSD sed (macOS) cần `-i ''`."""
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    gsed = shutil.which("gsed")
    if gsed:
        target = f'exec "{gsed}" "$@"'
    else:
        gnu = subprocess.run(["sed", "--version"], capture_output=True, check=False).returncode == 0
        if gnu:
            return None
        target = 'if [ "$1" = "-i" ]; then shift; exec /usr/bin/sed -i "" "$@"; fi; exec /usr/bin/sed "$@"'
    shim = bin_dir / "sed"
    shim.write_text(f"#!/bin/sh\n{target}\n")
    shim.chmod(0o755)
    return bin_dir


def run_version_step(tmp_path):
    site = tmp_path / "work" / "site"
    shutil.copytree(ROOT / "site", site)
    cmd = version_step_run().replace("${{ github.sha }}", FAKE_SHA)
    env = {"PATH": "/usr/bin:/bin", "HOME": str(tmp_path)}
    shim = sed_shim(tmp_path)
    if shim:
        env["PATH"] = f"{shim}:{env['PATH']}"
    r = subprocess.run(
        ["bash", "-e", "-c", cmd], cwd=site.parent, env=env, capture_output=True, text=True, check=False
    )
    return site, r


def test_version_step_writes_sha_once_per_page(tmp_path):
    site, r = run_version_step(tmp_path)
    assert r.returncode == 0, r.stderr
    meta = f'<meta name="version" content="{FAKE_SHA}">'
    for rel in ("index.html", "en/index.html"):
        t = (site / rel).read_text(encoding="utf-8")
        assert t.count(meta) == 1, rel
        assert PLACEHOLDER not in t, rel
    # bản gốc trong repo không bị đụng
    for p in PAGES:
        assert p.read_text(encoding="utf-8").count(PLACEHOLDER) == 1


def test_version_step_fails_on_two_placeholders(tmp_path):
    site = tmp_path / "work" / "site"
    shutil.copytree(ROOT / "site", site)
    page = site / "index.html"
    page.write_text(page.read_text(encoding="utf-8") + "\n" + PLACEHOLDER + "\n", encoding="utf-8")
    cmd = version_step_run().replace("${{ github.sha }}", FAKE_SHA)
    env = {"PATH": "/usr/bin:/bin", "HOME": str(tmp_path)}
    shim = sed_shim(tmp_path)
    if shim:
        env["PATH"] = f"{shim}:{env['PATH']}"
    r = subprocess.run(
        ["bash", "-e", "-c", cmd], cwd=site.parent, env=env, capture_output=True, text=True, check=False
    )
    assert r.returncode != 0
    assert FAKE_SHA not in page.read_text(encoding="utf-8")


def test_version_step_missing_placeholder_fails(tmp_path):
    site = tmp_path / "work" / "site"
    shutil.copytree(ROOT / "site", site)
    page = site / "en" / "index.html"
    page.write_text(page.read_text(encoding="utf-8").replace(PLACEHOLDER, ""), encoding="utf-8")
    cmd = version_step_run().replace("${{ github.sha }}", FAKE_SHA)
    r = subprocess.run(["bash", "-e", "-c", cmd], cwd=site.parent, capture_output=True, text=True, check=False)
    assert r.returncode != 0


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
        assert p.read_text().count(PLACEHOLDER) == 1, p


@pytest.mark.parametrize("name", ["test", "build", "deploy"])
def test_jobs_exist(name):
    assert name in WF["jobs"]


def _mutate(fn):
    bad = copy.deepcopy(WF)
    fn(bad)
    return workflow_problems(bad)


def _pytest_step(wf):
    return next(s for s in wf["jobs"]["test"]["steps"] if s.get("run", "").strip() == "uv run pytest -q")


def test_workflow_real_has_no_problems():
    assert workflow_problems(WF) == []


@pytest.mark.parametrize(
    "name,fn",
    [
        ("or-true", lambda w: _pytest_step(w).update(run="uv run pytest -q || true")),
        ("echo", lambda w: _pytest_step(w).update(run='echo "uv run pytest -q"')),
        ("semicolon", lambda w: _pytest_step(w).update(run="uv run pytest -q; true")),
        ("step-coe", lambda w: _pytest_step(w).update({"continue-on-error": True})),
        ("job-coe", lambda w: w["jobs"]["test"].update({"continue-on-error": True})),
        ("step-if", lambda w: _pytest_step(w).update({"if": "false"})),
        ("job-if", lambda w: w["jobs"]["test"].update({"if": "false"})),
        ("build-always", lambda w: w["jobs"]["build"].update({"if": "always()"})),
        ("deploy-always", lambda w: w["jobs"]["deploy"].update({"if": "always()"})),
        ("no-timeout-test", lambda w: w["jobs"]["test"].pop("timeout-minutes", None)),
        ("no-timeout-deploy", lambda w: w["jobs"]["deploy"].pop("timeout-minutes", None)),
        ("zero-timeout", lambda w: w["jobs"]["build"].update({"timeout-minutes": 0})),
        ("test-pages", lambda w: w["jobs"]["test"].update({"permissions": {"pages": "write"}})),
        ("wf-pages", lambda w: w["permissions"].update({"pages": "write"})),
        ("wf-idtoken", lambda w: w["permissions"].update({"id-token": "write"})),
        ("build-idtoken", lambda w: w["jobs"]["build"].setdefault("permissions", {}).update({"id-token": "write"})),
        ("build-pages-write", lambda w: w["jobs"]["build"].setdefault("permissions", {}).update({"pages": "write"})),
    ],
)
def test_workflow_negative_cases(name, fn):
    assert _mutate(fn), name
    assert workflow_problems(WF) == []


def test_workflow_timeouts_and_job_permissions():
    jobs = WF["jobs"]
    assert 0 < jobs["test"]["timeout-minutes"] <= 30
    assert 0 < jobs["build"]["timeout-minutes"] <= 10
    assert 0 < jobs["deploy"]["timeout-minutes"] <= 10
    assert jobs["build"]["permissions"] == {"contents": "read", "pages": "read"}
