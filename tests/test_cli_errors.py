import pytest

from todo import cli, store


@pytest.fixture
def tf(tmp_path, monkeypatch):
    p = tmp_path / "t.json"
    monkeypatch.setenv("TODO_FILE", str(p))
    return p


def _snap(p):
    return p.read_bytes(), p.stat().st_mtime_ns


@pytest.mark.parametrize("bad", ["²", "١", "１", "-1", "1.0"])
def test_done_rejects_non_ascii_id(tf, capsys, bad):
    store.add(tf, "a")
    before = _snap(tf)
    assert cli.main(["done", bad]) == 2
    cap = capsys.readouterr()
    assert cap.err and cap.out == ""
    assert "Traceback" not in cap.err
    assert _snap(tf) == before
    assert store.load(tf)[0]["done"] is False


@pytest.mark.parametrize("bad", ["²", "١"])
def test_due_rejects_non_ascii_id(tf, capsys, bad):
    store.add(tf, "a")
    before = _snap(tf)
    assert cli.main(["due", bad, "2026-10-20"]) == 2
    cap = capsys.readouterr()
    assert "Traceback" not in cap.err and cap.out == ""
    assert _snap(tf) == before


@pytest.mark.parametrize("args", [[""], ["   "], ["\t\n"], ["", "--due", "2026-10-20"]])
def test_add_rejects_blank_title(tf, capsys, args):
    assert cli.main(["add", *args]) == 2
    cap = capsys.readouterr()
    assert cap.err and cap.out == ""
    assert not tf.exists()
    store.add(tf, "keep")
    before = _snap(tf)
    assert cli.main(["add", *args]) == 2
    capsys.readouterr()
    assert _snap(tf) == before


def test_add_title_single_line_four_columns(tf, capsys):
    assert cli.main(["add", "a\tb\nc\r\nd e"]) == 0
    capsys.readouterr()
    assert cli.main(["list"]) == 0
    out = capsys.readouterr().out
    lines = out.splitlines()
    assert len(lines) == 1 and out.count("\n") == 1
    parts = lines[0].split("\t")
    assert len(parts) == 4
    assert not set(parts[3]) & set("\t\n\r\x0b\x0c\x85  \x1c\x1d\x1e")
    assert parts[3] == "a b c d e"


def test_store_add_cleans_title(tmp_path):
    p = tmp_path / "t.json"
    assert store.add(p, "x\ty")["title"] == "x y"
    assert store.load(p)[0]["title"] == "x y"


def test_done_missing_id_does_not_write(tf, capsys):
    store.add(tf, "a")
    before = _snap(tf)
    assert cli.main(["done", "9"]) == 1
    cap = capsys.readouterr()
    assert "không có việc id 9" in cap.err and cap.out == ""
    assert _snap(tf) == before


def test_done_missing_id_no_file(tf, capsys):
    assert cli.main(["done", "9"]) == 1
    assert "không có việc id 9" in capsys.readouterr().err
    assert not tf.exists()


def test_store_complete_missing_returns_false_no_write(tmp_path):
    p = tmp_path / "t.json"
    assert store.complete(p, 9) is False
    assert not p.exists()
    store.add(p, "a")
    before = _snap(p)
    assert store.complete(p, 9) is False
    assert _snap(p) == before
