from todo import cli


def test_add_then_list(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("TODO_FILE", str(tmp_path / "t.json"))
    assert cli.main(["add", "mua", "sữa"]) == 0
    assert cli.main(["list"]) == 0
    assert "mua sữa" in capsys.readouterr().out


def test_bad_usage_returns_2(tmp_path, monkeypatch):
    monkeypatch.setenv("TODO_FILE", str(tmp_path / "t.json"))
    assert cli.main(["nope"]) == 2


def test_list_shows_due_column(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("TODO_FILE", str(tmp_path / "t.json"))
    cli.main(["add", "mua", "sữa", "--due", "2026-10-20"])
    cli.main(["add", "không hạn"])
    capsys.readouterr()
    assert cli.main(["list"]) == 0
    lines = capsys.readouterr().out.splitlines()
    assert lines[0] == "1\t \t2026-10-20\tmua sữa"
    assert lines[1] == "2\t \t\tkhông hạn"


def test_list_legacy_file_without_due(tmp_path, monkeypatch, capsys):
    p = tmp_path / "t.json"
    p.write_text('[{"id": 1, "title": "việc cũ", "done": true}]', encoding="utf-8")
    monkeypatch.setenv("TODO_FILE", str(p))
    assert cli.main(["list"]) == 0
    assert "1\tx\t\tviệc cũ" in capsys.readouterr().out
