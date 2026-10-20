"""screenshot.py báo lỗi Chrome đúng, không để PNG cũ mang hash mới (H-07)."""

import subprocess
from pathlib import Path

import pytest

from scripts import screenshot as sh

OLD_PNG = (
    sh.PNG_SIG
    + b"\x00\x00\x00\x0dIHDR" + (b"\x00\x00\x00\x01" * 2) + b"\x08\x02\x00\x00\x00" + b"\x00" * 4
    + b"\x00\x00\x00\x00IEND\xaeB`\x82"
)


def _fake(monkeypatch, returncode=1, creates=False, stdout="", exc=None):
    monkeypatch.setattr(sh, "chrome_path", lambda: "chrome-gia")

    def run(cmd, **kw):
        if exc:
            raise exc
        if creates:
            for c in cmd:
                if c.startswith("--screenshot="):
                    Path(c.split("=", 1)[1]).write_bytes(OLD_PNG)
        return subprocess.CompletedProcess(cmd, returncode, stdout, "loi gia stderr")

    monkeypatch.setattr(sh.subprocess, "run", run)


def test_shoot_loi_xoa_png_cu(tmp_path, monkeypatch):
    out = tmp_path / "a.png"
    out.write_bytes(OLD_PNG)
    _fake(monkeypatch, returncode=1)
    with pytest.raises(RuntimeError, match="loi gia stderr"):
        sh.shoot("http://x/", out, 100, 100, "light")
    assert not out.exists()


def test_shoot_rc0_khong_tao_tep(tmp_path, monkeypatch):
    out = tmp_path / "a.png"
    out.write_bytes(OLD_PNG)
    _fake(monkeypatch, returncode=0)
    with pytest.raises(RuntimeError):
        sh.shoot("http://x/", out, 100, 100, "light")
    assert not out.exists()


def test_shoot_thanh_cong(tmp_path, monkeypatch):
    out = tmp_path / "a.png"
    _fake(monkeypatch, returncode=0, creates=True)
    sh.shoot("http://x/", out, 100, 100, "light")
    assert out.exists()


def test_shoot_timeout_la_runtimeerror(tmp_path, monkeypatch):
    _fake(monkeypatch, exc=subprocess.TimeoutExpired("chrome", 60))
    with pytest.raises(RuntimeError):
        sh.shoot("http://x/", tmp_path / "a.png", 100, 100, "light")


def test_main_timeout_exit_2_khong_traceback(tmp_path, monkeypatch, capsys):
    _fake(monkeypatch, exc=subprocess.TimeoutExpired("chrome", 60))
    rc = sh.main(["--site", str(tmp_path), "--widths", "1280", "--modes", "light",
                  "--out", str(tmp_path / "o")])
    assert rc == 2
    assert "Lỗi:" in capsys.readouterr().err


def test_page_loi_khong_de_png_cu_mang_hash_moi(tmp_path, monkeypatch, capsys):
    site = tmp_path / "site"
    site.mkdir()
    (site / "og.svg").write_text("<svg xmlns='http://www.w3.org/2000/svg'/>")
    f = tmp_path / "og.png"
    f.write_bytes(OLD_PNG)
    sh.png_add_text(f, "source-sha256", "hash-cu")
    _fake(monkeypatch, returncode=1)
    rc = sh.main(["--site", str(site), "--page", "/og.svg", "--file", str(f)])
    assert rc == 2
    assert "Lỗi:" in capsys.readouterr().err
    assert not f.exists() or sh.png_text(f).get("source-sha256") != sh.sha256_file(site / "og.svg")


def test_dump_dom_returncode_loi(monkeypatch):
    _fake(monkeypatch, returncode=1, stdout="<html>")
    with pytest.raises(RuntimeError):
        sh.dump_dom("http://x/", 100, 100, "light")


def test_dump_dom_stdout_rong(monkeypatch):
    _fake(monkeypatch, returncode=0, stdout="  \n")
    with pytest.raises(RuntimeError):
        sh.dump_dom("http://x/", 100, 100, "light")


def test_dump_dom_ok_va_timeout(monkeypatch):
    _fake(monkeypatch, returncode=0, stdout="<html></html>")
    assert sh.dump_dom("http://x/", 100, 100, "light") == "<html></html>"
    _fake(monkeypatch, exc=subprocess.TimeoutExpired("chrome", 60))
    with pytest.raises(RuntimeError):
        sh.dump_dom("http://x/", 100, 100, "light")
