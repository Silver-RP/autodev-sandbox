import pytest

from todo.cli import main


@pytest.fixture
def env(tmp_path, monkeypatch):
    monkeypatch.setenv("TODO_FILE", str(tmp_path / "t.json"))
    monkeypatch.setenv("TODO_TODAY", "2026-10-15")
    return tmp_path


def seed():
    # thứ tự hạn ngược
    assert main(["add", "tuong-lai", "--due", "2026-10-16"]) == 0
    assert main(["add", "hom-nay", "--due", "2026-10-15"]) == 0
    assert main(["add", "qua-han", "--due", "2026-10-14"]) == 0
    assert main(["add", "xong-roi", "--due", "2026-10-01"]) == 0
    assert main(["done", "4"]) == 0
    assert main(["add", "khong-han"]) == 0


def test_overdue_one_line(env, capsys):
    seed()
    capsys.readouterr()
    assert main(["overdue"]) == 0
    lines = capsys.readouterr().out.splitlines()
    assert len(lines) == 1 and "qua-han" in lines[0]
    assert lines[0] == "3\t \t2026-10-14\tqua-han"


def test_overdue_empty_or_missing(env, capsys):
    assert main(["overdue"]) == 0
    assert capsys.readouterr().out == ""
    (env / "t.json").write_text("[]")
    assert main(["overdue"]) == 0
    assert capsys.readouterr().out == ""


def test_bad_today(env, monkeypatch, capsys):
    monkeypatch.setenv("TODO_TODAY", "mai")
    assert main(["overdue"]) == 2
    assert capsys.readouterr().err.strip()


def test_extra_args(env, capsys):
    assert main(["overdue", "x"]) == 2
    assert "todo overdue" in capsys.readouterr().err


def test_boundary_moves_with_date(env, monkeypatch, capsys):
    seed()
    capsys.readouterr()
    monkeypatch.setenv("TODO_TODAY", "2026-10-17")
    assert main(["overdue"]) == 0
    out = capsys.readouterr().out.splitlines()
    assert [ln.split("\t")[3] for ln in out] == ["qua-han", "hom-nay", "tuong-lai"]
    assert main(["overdue"]) == 0  # gọi lặp lại
    assert len(capsys.readouterr().out.splitlines()) == 3
