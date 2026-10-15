import pytest

from todo import cli, store


@pytest.mark.parametrize(
    "text", ["2026-W01-1", "20261020  ", " 2026-10-20", "2026-10-20\n", "２０２６-10-20"]
)
def test_valid_due_strict_bad(text):
    assert store.valid_due(text) is False


@pytest.mark.parametrize("text", ["2026-10-20", "2024-02-29"])
def test_valid_due_strict_ok(text):
    assert store.valid_due(text) is True


def test_valid_due_non_str():
    assert store.valid_due(None) is False


def test_cli_due_week_format_rejected_file_unchanged(tmp_path, monkeypatch):
    p = tmp_path / "t.json"
    monkeypatch.setenv("TODO_FILE", str(p))
    store.add(p, "a")
    before = p.read_bytes()
    assert cli.main(["due", "1", "2026-W01-1"]) == 2
    assert p.read_bytes() == before
    assert cli.main(["due", "1", "2026-W01-1"]) == 2  # repeat call
    assert p.read_bytes() == before


def test_cli_has_no_private_date_check():
    assert not hasattr(cli, "_ok_date")
