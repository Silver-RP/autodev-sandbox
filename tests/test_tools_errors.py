import json
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from test_tools import needs_chrome

from scripts import contrast as ct
from scripts import lh_check as lh
from scripts import page_metrics as pm

SAMPLE = {
    "categories": {
        "performance": {"score": 0.95},
        "accessibility": {"score": 0.97},
        "best-practices": {"score": 1},
        "seo": {"score": 0.96},
    },
    "audits": {"total-byte-weight": {"numericValue": 1000}},
}


def _write(tmp_path, mutate=None, name="lh.json"):
    d = json.loads(json.dumps(SAMPLE))
    if mutate:
        mutate(d)
    p = tmp_path / name
    p.write_text(json.dumps(d))  # NaN được ghi thành NaN, json.loads đọc lại được
    return p


@pytest.fixture
def site(tmp_path):
    s = tmp_path / "s"
    (s / "en").mkdir(parents=True)
    (s / "index.html").write_text("<body>x</body>")
    (s / "en" / "index.html").write_text("<body>y</body>")
    return s


def _ok_runner(tmp_path, seen=None):
    p = _write(tmp_path)

    def run(url, npx, env):
        if seen is not None:
            seen.append(url)
        return lh.read_result(p)
    return run


def test_lh_both_pages_ok_and_perf_80_fails(tmp_path, site):
    assert lh.main(["--site", str(site)], runner=_ok_runner(tmp_path)) == 0
    bad = _write(tmp_path, lambda d: d["categories"]["performance"].update(score=0.8), "b.json")
    assert lh.main(["--site", str(site)], runner=lambda u, n, e: lh.read_result(bad)) == 1


def test_lh_timeout_exit_2_and_default_timeout(tmp_path, site, monkeypatch, capsys):
    def boom(url, npx, env):
        raise subprocess.TimeoutExpired("lighthouse", 1)
    assert lh.main(["--site", str(site)], runner=boom) == 2

    calls = []

    def fake_run(cmd, **kw):
        calls.append(kw)
        raise subprocess.TimeoutExpired(cmd, kw.get("timeout"))
    monkeypatch.setattr(lh.subprocess, "run", fake_run)
    monkeypatch.setattr(lh.shutil, "which", lambda n: "/bin/npx")
    from scripts import screenshot as sh
    monkeypatch.setattr(sh, "chrome_path", lambda: "/bin/chrome")
    assert lh.main(["--site", str(site), "--runs", "1"]) == 2
    assert calls and calls[0]["timeout"] >= 120
    assert lh.main(["--site", str(site), "--runs", "1", "--timeout", "7"]) == 2
    assert calls[-1]["timeout"] == 7


def test_lh_null_score_exit_2(tmp_path, site):
    p = _write(tmp_path, lambda d: d["categories"]["seo"].update(score=None))
    assert lh.main(["--site", str(site)], runner=lambda u, n, e: lh.read_result(p)) == 2


def test_lh_missing_key_exit_2(tmp_path, site):
    p = _write(tmp_path, lambda d: d["audits"].pop("total-byte-weight"))
    assert lh.main(["--site", str(site)], runner=lambda u, n, e: lh.read_result(p)) == 2


@pytest.mark.parametrize("val", [float("nan"), float("inf")])
def test_lh_non_finite_weight_exit_2(tmp_path, site, val):
    p = _write(tmp_path, lambda d: d["audits"]["total-byte-weight"].update(numericValue=val))
    assert lh.main(["--site", str(site)], runner=lambda u, n, e: lh.read_result(p)) == 2


def test_lh_empty_plan_exit_2_no_ok(tmp_path, site, capsys):
    r = lh.main(["--site", str(site), "--runs", "0", "--en-runs", "0"],
                runner=_ok_runner(tmp_path))
    out = capsys.readouterr().out
    assert r == 2
    assert "OK" not in out


def test_lh_pages_only_en_and_unknown(tmp_path, site, capsys):
    seen = []
    assert lh.main(["--site", str(site), "--pages", "/en/"],
                   runner=_ok_runner(tmp_path, seen)) == 0
    assert len(seen) == 1 and seen[0].endswith("/en/")
    seen.clear()
    assert lh.main(["--site", str(site), "--pages", "/khong-co/"],
                   runner=_ok_runner(tmp_path, seen)) == 2
    assert seen == []
    assert lh.main(["--site", str(site), "--pages", ""], runner=_ok_runner(tmp_path)) == 2


def test_lh_repeatable(tmp_path, site):
    r = _ok_runner(tmp_path)
    assert [lh.main(["--site", str(site)], runner=r) for _ in range(2)] == [0, 0]


@needs_chrome
@pytest.mark.parametrize("mod", [pm, ct])
def test_real_en_page_and_missing_page(mod):
    args = ["--widths", "360", "--modes", "light"]
    assert mod.main(["--pages", "/en/", *args]) == 0
    assert mod.main(["--pages", "/khong-co/", *args]) == 2


@pytest.mark.parametrize("mod", [pm, ct])
def test_missing_and_empty_pages_exit_2_without_chrome(mod, site):
    assert mod.main(["--site", str(site), "--pages", "/khong-co/"]) == 2
    assert mod.main(["--site", str(site), "--pages", ""]) == 2


def test_normalize_pages(site):
    assert pm.normalize_pages(site, ["/en/", "/", "index.html"]) == [
        "/en/index.html", "/index.html", "/index.html"]


@pytest.mark.parametrize("mod", [pm, ct])
def test_measure_runtime_error_exit_2(mod, site, monkeypatch):
    def bad(*a, **k):
        raise RuntimeError("DOM rỗng")
    monkeypatch.setattr(pm, "measure", bad)
    assert mod.main(["--site", str(site), "--widths", "360", "--modes", "light"]) == 2
    assert pm.main(["--site", str(site), "--widths", "360", "--modes", "light",
                    "--check-overflow"]) == 2
    with pytest.raises(RuntimeError):
        pm.collect(site, [360], ["light"], pages=["/"])
