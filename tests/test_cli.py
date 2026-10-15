from todo import cli


def test_add_then_list(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("TODO_FILE", str(tmp_path / "t.json"))
    assert cli.main(["add", "mua", "sữa"]) == 0
    assert cli.main(["list"]) == 0
    assert "mua sữa" in capsys.readouterr().out


def test_bad_usage_returns_2(tmp_path, monkeypatch):
    monkeypatch.setenv("TODO_FILE", str(tmp_path / "t.json"))
    assert cli.main(["nope"]) == 2
