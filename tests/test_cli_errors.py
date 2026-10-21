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


_CMDS = [
    ["add", "x"],
    ["list"],
    ["overdue"],
    ["done", "1"],
    ["due", "1", "2026-10-20"],
]


@pytest.mark.parametrize("argv", _CMDS)
def test_corrupt_json_all_commands(tf, capsys, argv):
    tf.write_bytes("{hỏng".encode())
    assert cli.main(argv) == 2
    cap = capsys.readouterr()
    assert str(tf) in cap.err and "Traceback" not in cap.err
    assert cap.out == ""


def test_add_on_corrupt_file_keeps_bytes(tf, capsys):
    tf.write_bytes(b"{hong")
    before = _snap(tf)
    assert cli.main(["add", "x"]) == 2
    assert _snap(tf) == before


@pytest.mark.parametrize(
    "content",
    [
        b"{}",
        b"[1]",
        b'[{"title": "x", "done": false}]',
        b'[{"id": "1", "title": "x", "done": false}]',
        b'[{"id": true, "title": "x", "done": false}]',
        b"\xff\xfe",
    ],
)
def test_list_bad_structure(tf, capsys, content):
    tf.write_bytes(content)
    assert cli.main(["list"]) == 2
    cap = capsys.readouterr()
    assert cap.err.strip() and "Traceback" not in cap.err and cap.out == ""
    assert str(tf) in cap.err


def test_bad_element_reason_mentions_id(tf, capsys):
    tf.write_bytes(b'[{"title": "x"}]')
    cli.main(["list"])
    assert "id" in capsys.readouterr().err


def test_legacy_file_still_lists(tf, capsys):
    tf.write_text('[{"id": 1, "title": "việc cũ", "done": true}]', encoding="utf-8")
    assert cli.main(["list"]) == 0
    assert "việc cũ" in capsys.readouterr().out


def test_empty_file_is_error(tf, capsys):
    tf.write_bytes(b"")
    assert cli.main(["list"]) == 2
    cap = capsys.readouterr()
    assert cap.err.strip() and "Traceback" not in cap.err


def test_missing_file_is_empty_list(tf):
    assert store.load(tf) == []


# ---- R18 dev-01: đầu vào lạ -> exit 2 ----
import json
import os
import subprocess
import sys

_ONE = '[{"id": 1, "title": "a", "done": false}]'


@pytest.mark.parametrize("argv", [["done", "9" * 5000], ["due", "9" * 5000, "2026-10-20"]])
def test_done_huge_id_exit_2(tf, capsys, argv):
    tf.write_text(_ONE, encoding="utf-8")
    before = _snap(tf)
    assert cli.main(argv) == 2
    cap = capsys.readouterr()
    assert cap.out == ""
    assert "Traceback" not in cap.err
    assert len(cap.err.strip().splitlines()) == 1
    assert _snap(tf) == before


@pytest.mark.parametrize("argv", [["list"], ["overdue"], ["add", "x"], ["done", "1"]])
def test_deeply_nested_json_exit_2(tf, capsys, argv):
    tf.write_bytes(b"[" * 100000)
    before = _snap(tf)
    assert cli.main(argv) == 2
    cap = capsys.readouterr()
    assert str(tf) in cap.err and "Traceback" not in cap.err
    assert _snap(tf) == before


def test_huge_int_in_file_exit_2(tf, capsys):
    tf.write_text('[{"id": 1' + "0" * 5000 + ', "title": "a", "done": false}]', encoding="utf-8")
    assert cli.main(["list"]) == 2
    cap = capsys.readouterr()
    assert str(tf) in cap.err and "Traceback" not in cap.err


def test_add_with_id_too_big_to_write_exit_2(tf, capsys):
    tf.write_text('[{"id": ' + "9" * 4300 + ', "title": "a", "done": false}]', encoding="utf-8")
    before = _snap(tf)
    assert cli.main(["add", "x"]) == 2
    cap = capsys.readouterr()
    assert "Traceback" not in cap.err and cap.err.strip()
    assert _snap(tf) == before
    assert [p.name for p in tf.parent.iterdir()] == [tf.name]


@pytest.mark.parametrize("argv", [[b"add", b"a\xff"], [b"due", b"1", b"\xff"]])
def test_non_utf8_argv_subprocess_exit_2(tf, argv):
    tf.write_text(_ONE, encoding="utf-8")
    before = _snap(tf)
    code = "import sys; from todo import cli; sys.exit(cli.main())"
    r = subprocess.run(
        [os.fsencode(sys.executable), b"-c", code.encode(), *argv],
        env={**os.environ, "TODO_FILE": str(tf)},
        capture_output=True,
        check=False,
    )
    assert r.returncode == 2, r.stderr
    assert b"Traceback" not in r.stderr and r.stderr.strip()
    assert _snap(tf) == before


@pytest.mark.parametrize("argv", [["add", "a\udcff"], ["due", "1", "\udcff"]])
def test_surrogate_argv_in_process_exit_2(tf, capsys, argv):
    tf.write_text(_ONE, encoding="utf-8")
    before = _snap(tf)
    assert cli.main(argv) == 2
    cap = capsys.readouterr()
    assert cap.err.strip() and "Traceback" not in cap.err
    assert _snap(tf) == before
    json.loads(tf.read_text(encoding="utf-8"))
