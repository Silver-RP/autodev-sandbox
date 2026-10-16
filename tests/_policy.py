"""Luật tài nguyên của site: check(html, css) -> danh sách vi phạm."""
import re
from html.parser import HTMLParser

ALLOWED_HOSTS = {
    "fonts.googleapis.com",
    "fonts.gstatic.com",
    "cdn.jsdelivr.net",
    "cdnjs.cloudflare.com",
}
PIN = re.compile(r"(@\d+\.\d+\.\d+|/\d+\.\d+\.\d+/)")
CSS_URL = re.compile(r"url\(\s*(['\"]?)(.*?)\1\s*\)", re.IGNORECASE | re.DOTALL)
CSS_IMPORT = re.compile(r"@import\s+(?:url\(\s*)?['\"]?([^'\")\s;]+)", re.IGNORECASE)


def _is_external(url):
    u = url.strip().lower()
    return u.startswith(("http:", "https:", "//"))


def _host(url):
    u = url.strip().lower()
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
    if not url.strip().lower().startswith("https://"):
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
        if tag == "a":
            if a.get("href", "").strip().lower().startswith("http:"):
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
                    integ = a.get("integrity", "").strip().lower()
                    if not integ.startswith(("sha384-", "sha512-")):
                        self.v.append(f"script src thiếu integrity hợp lệ: {src}")
                    if "crossorigin" not in a:
                        self.v.append(f"script src thiếu crossorigin: {src}")
                    if not _pinned(src):
                        self.v.append(f"script src chưa ghim phiên bản: {src}")
        elif tag == "link":
            if "href" in a:
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
