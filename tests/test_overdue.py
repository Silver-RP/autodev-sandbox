from datetime import date

import pytest

from todo import store

T = date(2026, 10, 15)


def item(i, title, due=None, done=False):
    d = {"id": i, "title": title, "done": done}
    if due is not None:
        d["due"] = due
    return d


def test_five_kinds_only_overdue():
    items = [
        item(1, "khong-han"),
        item(2, "tuong-lai", "2026-10-20"),
        item(3, "hom-nay", "2026-10-15"),
        item(4, "xong-roi", "2026-10-01", done=True),
        item(5, "qua-han", "2026-10-14"),
    ]
    assert [i["title"] for i in store.overdue(items, T)] == ["qua-han"]


def test_due_equal_today_not_overdue():
    assert store.overdue([item(1, "a", "2026-10-15")], T) == []


def test_sorted_by_due_ascending_then_id():
    items = [
        item(1, "a", "2026-10-12"),
        item(2, "b", "2026-10-10"),
        item(3, "c", "2026-10-11"),
        item(0, "d", "2026-10-10"),
    ]
    assert [i["id"] for i in store.overdue(items, T)] == [0, 2, 3, 1]


def test_invalid_due_ignored_and_empty():
    items = [item(1, "a", "abc"), item(2, "b", "2026-10-01")]
    assert [i["id"] for i in store.overdue(items, T)] == [2]
    assert store.overdue([], T) == []


def test_today_env(monkeypatch):
    monkeypatch.setenv("TODO_TODAY", "2026-10-15")
    assert store.today() == date(2026, 10, 15)
    assert store.today() == date(2026, 10, 15)


def test_today_invalid_env(monkeypatch):
    monkeypatch.setenv("TODO_TODAY", "mai")
    with pytest.raises(ValueError):
        store.today()


def test_today_default(monkeypatch):
    monkeypatch.delenv("TODO_TODAY", raising=False)
    assert store.today() == date.today()
