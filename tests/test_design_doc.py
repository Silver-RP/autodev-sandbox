import re
from pathlib import Path

DOC = Path(__file__).parent.parent / "docs" / "design" / "lazy-landing.md"
HEX = re.compile(r"`(#[0-9A-Fa-f]{6})`")


def text():
    return DOC.read_text(encoding="utf-8")


def section(title, level="##"):
    """Nội dung từ tiêu đề `title` tới tiêu đề cùng hoặc cao hơn kế tiếp."""
    t = text()
    m = re.search(rf"^{level} {re.escape(title)}.*$", t, re.MULTILINE)
    assert m, f"thiếu mục {title}"
    rest = t[m.end():]
    n = re.search(rf"^#{{1,{len(level)}}} ", rest, re.MULTILINE)
    return rest[: n.start()] if n else rest


def palette(title):
    """Hex ở cột 2 của các hàng bảng trong mục `title` (### con)."""
    body = section("Bảng màu")
    m = re.search(rf"^### {re.escape(title)}.*$", body, re.MULTILINE)
    assert m, f"thiếu bảng {title}"
    rest = body[m.end():]
    n = re.search(r"^###? ", rest, re.MULTILINE)
    rest = rest[: n.start()] if n else rest
    out = []
    for line in rest.splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) >= 2 and line.startswith("|"):
            h = HEX.fullmatch(cells[1])
            if h:
                out.append(h.group(1).upper())
    return out


def test_chosen_direction_not_empty():
    m = re.search(r"^Hướng đã chọn:(.*)$", text(), re.MULTILINE)
    assert m and m.group(1).strip()


def test_light_palette_has_six():
    assert len(palette("Sáng")) == 6


def test_dark_palette_has_six():
    assert len(palette("Tối")) == 6


def test_two_fonts_named():
    t = text()
    assert "Baloo 2" in t and "Be Vietnam Pro" in t


def test_wireframes_360_and_1280():
    body = section("Bố cục")
    assert re.search(r"^### 1280\s*$", body, re.MULTILINE)
    assert re.search(r"^### 360\s*$", body, re.MULTILINE)
    assert body.count("```") >= 4


def test_ai_signs_avoided_has_five_lines():
    body = section("Dấu hiệu AI đã tránh")
    items = [ln for ln in body.splitlines() if re.match(r"^\d+\. ", ln)]
    assert len(items) == 5


def test_banned_colors_only_as_negations():
    t = text()
    # chỉ được nhắc trong mục "Dấu hiệu AI đã tránh" / lời cấm, không nằm trong bảng màu
    for bad in ("#F4F1EA", "#D97757"):
        assert bad not in section("Bảng màu").upper()
        assert bad not in palette("Sáng") + palette("Tối")
    assert "#F4F1EA" not in t.upper()
