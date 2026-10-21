import os

import pytest

from todo import store


def test_failed_save_keeps_old_file_and_leaves_no_temp(tmp_path, monkeypatch):
    path = tmp_path / "todo.json"
    store.add(path, "cu")
    before = path.read_text(encoding="utf-8")

    def boom(*_):
        raise OSError("giả lập chết giữa chừng")

    monkeypatch.setattr(os, "replace", boom)
    with pytest.raises(OSError):
        store.add(path, "moi")

    assert path.read_text(encoding="utf-8") == before
    assert [p.name for p in tmp_path.iterdir()] == ["todo.json"]


def test_save_leaves_only_target_file(tmp_path):
    path = tmp_path / "todo.json"
    store.add(path, "a")
    store.add(path, "b")
    assert [p.name for p in tmp_path.iterdir()] == ["todo.json"]
    assert [i["title"] for i in store.load(path)] == ["a", "b"]


def test_save_keeps_normal_file_mode(tmp_path):
    path = tmp_path / "todo.json"
    umask = os.umask(0o022)
    try:
        store.add(path, "a")
    finally:
        os.umask(umask)
    assert path.stat().st_mode & 0o777 == 0o644


import json  # noqa: E402

from todo import cli  # noqa: E402


def _one_item(path):
    path.write_text(json.dumps([{"id": 1, "title": "a", "done": False}]), encoding="utf-8")


def test_readonly_file_not_overwritten(tmp_path, monkeypatch, capsys):
    path = tmp_path / "todo.json"
    _one_item(path)
    path.chmod(0o444)
    before = (path.read_bytes(), path.stat().st_mode, path.stat().st_ino)
    with pytest.raises(store.StoreError):
        store.save(path, [{"id": 1, "title": "b", "done": False}])
    monkeypatch.setenv("TODO_FILE", str(path))
    assert cli.main(["add", "x"]) == 2
    assert "Traceback" not in capsys.readouterr().err
    st = path.stat()
    assert (path.read_bytes(), st.st_mode, st.st_ino) == before
    assert [p.name for p in tmp_path.iterdir()] == ["todo.json"]


def test_hardlink_preserved(tmp_path, monkeypatch):
    path = tmp_path / "todo.json"
    _one_item(path)
    link = tmp_path / "b"
    os.link(path, link)
    path.chmod(0o640)
    monkeypatch.setenv("TODO_FILE", str(path))
    assert cli.main(["add", "x"]) == 0
    assert os.path.samefile(path, link)
    assert path.stat().st_nlink == 2
    assert [i["title"] for i in store.load(link)] == ["a", "x"]
    assert link.stat().st_mode & 0o777 == 0o640


def test_failed_replace_reports_original_error_when_tmp_gone(tmp_path, monkeypatch, capsys):
    path = tmp_path / "todo.json"
    _one_item(path)
    before = path.read_bytes()
    real_unlink = os.unlink

    def boom(*_):
        raise OSError("gốc")

    def unlink(p, *a, **k):
        real_unlink(p, *a, **k)
        raise FileNotFoundError(p)

    monkeypatch.setattr(os, "replace", boom)
    monkeypatch.setattr(os, "unlink", unlink)
    monkeypatch.setenv("TODO_FILE", str(path))
    assert cli.main(["add", "x"]) == 2
    err = capsys.readouterr().err
    assert "gốc" in err and "Traceback" not in err
    assert path.read_bytes() == before
