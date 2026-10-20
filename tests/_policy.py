"""Luật tài nguyên của site: check(html, css) -> danh sách vi phạm."""
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from scripts.site_config import SITE_URL

INTEGRITY = re.compile(r"sha(?:384|512)-[A-Za-z0-9+/_-]+={0,2}")
JS_ATTRS = ("href", "xlink:href", "src", "action", "formaction", "data")

ALLOWED_HOSTS = {
    "fonts.googleapis.com",
    "fonts.gstatic.com",
    "cdn.jsdelivr.net",
    "cdnjs.cloudflare.com",
}
PIN = re.compile(r"(@\d+\.\d+\.\d+|/\d+\.\d+\.\d+/)")
CSS_URL = re.compile(r"url\(\s*(['\"]?)(.*?)\1\s*\)", re.IGNORECASE | re.DOTALL)
CSS_IMPORT = re.compile(r"@import\s+(?:url\(\s*)?['\"]?([^'\")\s;]+)", re.IGNORECASE)


def _norm(url):
    """Như trình duyệt: bỏ tab/xuống dòng, bỏ khoảng trắng đầu/cuối, `\\` thành `/`, hạ chữ thường."""
    u = re.sub(r"[\t\r\n]", "", url).strip().lower()
    return u.replace("\\", "/")


def _is_external(url):
    return _norm(url).startswith(("http:", "https:", "//"))


def _host(url):
    u = _norm(url)
    if u.startswith("//"):
        u = "x:" + u
    rest = u.split(":", 1)[1].lstrip("/")
    host = re.split(r"[/?#]", rest, 1)[0].rsplit("@", 1)[-1]
    return host.split(":")[0]


def _pinned(src):
    """Đã ghim phiên bản: nếu có đoạn @tag thì mọi tag phải là X.Y.Z; ngược lại cần /X.Y.Z/."""
    path = re.split(r"[?#]", src, 1)[0]
    path = re.sub(r"^(?:https?:)?//[^/]*", "", path, flags=re.IGNORECASE)
    tags = re.findall(r"@([^/]*)", path)
    if tags:
        return all(re.fullmatch(r"\d+\.\d+\.\d+", t) for t in tags)
    return bool(PIN.search(path))


def check_url(url, where):
    """Luật cho URL tài nguyên (không phải <a>)."""
    if not _is_external(url):
        return []
    out = []
    if not _norm(url).startswith("https://"):
        out.append(f"{where}: không phải https: {url}")
    if _host(url) not in ALLOWED_HOSTS:
        out.append(f"{where}: domain không cho phép: {url}")
    return out


class _Html(HTMLParser):
    def __init__(self):
        super().__init__()
        self.v = []
        self._script = None  # (attrs) của <script> inline đang mở
        self._style = False

    def handle_starttag(self, tag, attrs):
        a = {k.lower(): (v or "") for k, v in attrs}
        for k in a:
            if k.startswith("on"):
                self.v.append(f"{tag}: thuộc tính {k} (on*) không được phép")
        for k in JS_ATTRS:
            if k in a and _norm(a[k]).startswith("javascript:"):
                self.v.append(f"{tag} {k}: javascript: không được phép")
        if tag == "base" and "href" in a:
            self.v.append(f"<base href> không được phép: {a['href']}")
        elif tag == "object" and "data" in a:
            self.v += check_url(a["data"], "object data")
        elif tag in ("image", "use"):
            for k in ("href", "xlink:href"):
                if k in a:
                    self.v += check_url(a[k], f"{tag} {k}")
        elif tag == "form" and "action" in a:
            self.v += check_url(a["action"], "form action")
        elif tag in ("button", "input") and "formaction" in a:
            self.v += check_url(a["formaction"], f"{tag} formaction")
        if tag == "a":
            if _norm(a.get("href", "")).startswith("http:"):
                self.v.append(f"a href dùng http: {a['href']}")
        elif tag == "script":
            src = a.get("src")
            if src is None:
                if a.get("type", "").strip().lower() != "application/ld+json":
                    self._script = a
                    self.v.append("script inline không được phép")
            else:
                self.v += check_url(src, "script src")
                if _is_external(src):
                    toks = a.get("integrity", "").split()
                    if not toks or not all(INTEGRITY.fullmatch(t) for t in toks):
                        self.v.append(f"script src thiếu integrity hợp lệ: {src}")
                    if "crossorigin" not in a:
                        self.v.append(f"script src thiếu crossorigin: {src}")
                    if not _pinned(src):
                        self.v.append(f"script src chưa ghim phiên bản: {src}")
        elif tag == "link":
            # canonical là siêu dữ liệu điều hướng, không tải tài nguyên
            # alternate + hreflang cũng chỉ là siêu dữ liệu ngôn ngữ
            # Chỉ miễn trừ khi rel đúng một giá trị và href thuộc SITE_URL (H-06)
            rel = a.get("rel", "").strip().lower()
            nav_meta = (rel == "canonical" or (rel == "alternate" and "hreflang" in a)) and (
                a.get("href", "").strip().startswith(SITE_URL)
            )
            if "href" in a and not nav_meta:
                self.v += check_url(a["href"], "link href")
        elif tag in ("img", "source", "iframe", "audio", "video", "embed"):
            if "src" in a:
                self.v += check_url(a["src"], f"{tag} src")
        elif tag == "style":
            self._style = True
        if "style" in a:
            self.v += check_css(a["style"])

    def handle_endtag(self, tag):
        if tag == "style":
            self._style = False

    def handle_data(self, data):
        if self._style:
            self.v += check_css(data)


def check_css(css):
    out = []
    urls = [m.group(2) for m in CSS_URL.finditer(css)]
    urls += [m.group(1) for m in CSS_IMPORT.finditer(css)]
    seen = set()
    for u in urls:
        if u in seen:
            continue
        seen.add(u)
        out += check_url(u, "css url")
    return out


def check(html="", css=""):
    p = _Html()
    p.feed(html)
    p.close()
    return p.v + check_css(css)
