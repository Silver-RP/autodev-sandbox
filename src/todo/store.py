"""Todo items stored as a JSON list in one file."""

import json
from pathlib import Path


def load(path: Path) -> list[dict]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else []


def save(path: Path, items: list[dict]) -> None:
    path.write_text(json.dumps(items, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def add(path: Path, title: str) -> dict:
    items = load(path)
    item = {"id": max((i["id"] for i in items), default=0) + 1, "title": title, "done": False}
    save(path, [*items, item])
    return item


def complete(path: Path, item_id: int) -> bool:
    items = load(path)
    found = False
    for i in items:
        if i["id"] == item_id:
            i["done"], found = True, True
    save(path, items)
    return found
