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
