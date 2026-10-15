"""Todo items stored as a JSON list in one file."""

import json
import re
from datetime import date
from pathlib import Path


def load(path: Path) -> list[dict]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else []


def save(path: Path, items: list[dict]) -> None:
    path.write_text(json.dumps(items, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def valid_due(text: str) -> bool:
    if not isinstance(text, str) or not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", text):
        return False
    try:
        date.fromisoformat(text)
    except ValueError:
        return False
    return True


def add(path: Path, title: str, due: str | None = None) -> dict:
    items = load(path)
    item = {"id": max((i["id"] for i in items), default=0) + 1, "title": title, "done": False}
    if due is not None:
        item["due"] = due
    save(path, [*items, item])
    return item


def set_due(path: Path, item_id: int, due: str) -> bool:
    items = load(path)
    for i in items:
        if i["id"] == item_id:
            i["due"] = due
            save(path, items)
            return True
    return False


def complete(path: Path, item_id: int) -> bool:
    items = load(path)
    found = False
    for i in items:
        if i["id"] == item_id:
            i["done"], found = True, True
    save(path, items)
    return found
