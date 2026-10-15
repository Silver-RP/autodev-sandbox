import json

import pytest

from todo import store


@pytest.mark.parametrize("text", ["2026-10-20", "2024-02-29"])
def test_valid_due_ok(text):
    assert store.valid_due(text) is True


@pytest.mark.parametrize("text", ["2026-02-30", "2026-13-40", "mai", "2026-1-5", "", "20261020"])
def test_valid_due_bad(text):
    assert store.valid_due(text) is False


def test_add_with_due(tmp_path):
    p = tmp_path / "t.json"
    store.add(p, "a", due="2026-10-20")
    assert store.load(p)[0]["due"] == "2026-10-20"


def test_add_without_due(tmp_path):
    p = tmp_path / "t.json"
    store.add(p, "b")
    store.add(p, "c")
    items = store.load(p)
    assert [i["title"] for i in items] == ["b", "c"]
    assert "due" not in items[0]


def test_set_due_on_legacy_file(tmp_path):
    p = tmp_path / "t.json"
    p.write_text(json.dumps([{"id": 1, "title": "cũ", "done": False}]), encoding="utf-8")
    assert store.set_due(p, 1, "2026-10-20") is True
    assert store.load(p)[0]["due"] == "2026-10-20"
    assert store.set_due(p, 1, "2026-11-01") is True
    assert store.load(p)[0]["due"] == "2026-11-01"


def test_set_due_missing_id_keeps_bytes(tmp_path):
    p = tmp_path / "t.json"
    p.write_text('[{"id": 1, "title": "cũ", "done": false}]', encoding="utf-8")
    before = p.read_bytes()
    assert store.set_due(p, 9, "2026-10-20") is False
    assert p.read_bytes() == before


def test_set_due_missing_file_not_created(tmp_path):
    p = tmp_path / "none.json"
    assert store.set_due(p, 1, "2026-10-20") is False
    assert not p.exists()


def _run(tmp_path, monkeypatch, *argv):
    from todo import cli

    monkeypatch.setenv("TODO_FILE", str(tmp_path / "t.json"))
    return cli.main(list(argv))


def test_cli_add_due_not_swallowed(tmp_path, monkeypatch):
    assert _run(tmp_path, monkeypatch, "add", "mua", "sữa", "--due", "2026-10-20") == 0
    item = store.load(tmp_path / "t.json")[0]
    assert item["title"] == "mua sữa" and item["due"] == "2026-10-20"


@pytest.mark.parametrize("bad", ["2026-02-30", "2026-W01-1", "mai", "20261020"])
def test_cli_add_bad_due(tmp_path, monkeypatch, bad):
    assert _run(tmp_path, monkeypatch, "add", "x", "--due", bad) == 2
    assert not (tmp_path / "t.json").exists()


def test_cli_add_due_missing_value(tmp_path, monkeypatch):
    assert _run(tmp_path, monkeypatch, "add", "x", "--due") == 2
    assert not (tmp_path / "t.json").exists()


def test_cli_due_changes(tmp_path, monkeypatch):
    p = tmp_path / "t.json"
    p.write_text('[{"id": 1, "title": "cũ", "done": false}]\n', encoding="utf-8")
    assert _run(tmp_path, monkeypatch, "due", "1", "2026-11-01") == 0
    assert store.load(p)[0]["due"] == "2026-11-01"
    assert _run(tmp_path, monkeypatch, "due", "1", "2026-12-01") == 0
    assert store.load(p)[0]["due"] == "2026-12-01"


@pytest.mark.parametrize(
    ("args", "code"),
    [(["9", "2026-11-01"], 1), (["1", "mai"], 2), (["1", "2026-W01-1"], 2), (["1"], 2)],
)
def test_cli_due_errors_keep_file(tmp_path, monkeypatch, args, code):
    p = tmp_path / "t.json"
    p.write_text('[{"id": 1, "title": "cũ", "done": false}]\n', encoding="utf-8")
    before = p.read_bytes()
    assert _run(tmp_path, monkeypatch, "due", *args) == code
    assert p.read_bytes() == before
