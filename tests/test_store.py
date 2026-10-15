from todo import store


def test_add_assigns_increasing_ids(tmp_path):
    p = tmp_path / "t.json"
    assert store.add(p, "a")["id"] == 1
    assert store.add(p, "b")["id"] == 2


def test_complete_marks_done_and_reports_missing(tmp_path):
    p = tmp_path / "t.json"
    store.add(p, "a")
    assert store.complete(p, 1) is True
    assert store.load(p)[0]["done"] is True
    assert store.complete(p, 9) is False
