"""Chụp trang qua Chrome headless: 360px (qua iframe) và 1280px, sáng và tối."""

from __future__ import annotations

import argparse
import contextlib
import functools
import hashlib
import html
import http.server
import os
import shutil
import struct
import subprocess
import sys
import tempfile
import threading
import urllib.error
import urllib.request
import zlib
from pathlib import Path
from urllib.parse import quote, urlparse

ROOT = Path(__file__).resolve().parent.parent
FRAME_PATH = "/__frame__.html"
MAC_CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
PNG_SIG = b"\x89PNG\r\n\x1a\n"


def chrome_path() -> str:
    env = os.environ.get("CHROME")
    if env:
        return env
    if os.path.exists(MAC_CHROME):
        return MAC_CHROME
    for name in ("google-chrome", "chromium"):
        found = shutil.which(name)
        if found:
            return found
    raise RuntimeError("Không tìm thấy Chrome: đặt biến môi trường CHROME hoặc cài google-chrome/chromium")


def png_size(path) -> tuple[int, int]:
    with open(path, "rb") as f:
        head = f.read(24)
    if len(head) < 24 or head[:8] != PNG_SIG or head[12:16] != b"IHDR":
        raise ValueError(f"không phải PNG: {path}")
    return struct.unpack(">II", head[16:24])


def sha256_file(path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def png_add_text(path, key: str, value: str) -> None:
    """Chèn chunk tEXt (key, value) ngay sau IHDR; thay chunk cùng key nếu đã có."""
    data = Path(path).read_bytes()
    if data[:8] != PNG_SIG:
        raise ValueError(f"không phải PNG: {path}")
    kb = key.encode("latin-1")
    out, pos, inserted = [PNG_SIG], 8, False
    while pos < len(data):
        n = struct.unpack(">I", data[pos : pos + 4])[0]
        kind, end = data[pos + 4 : pos + 8], pos + 12 + n
        if kind == b"tEXt" and data[pos + 8 : end - 4].split(b"\0", 1)[0] == kb:
            pos = end
            continue
        out.append(data[pos:end])
        if kind == b"IHDR" and not inserted:
            body = kb + b"\0" + value.encode("latin-1")
            crc = zlib.crc32(b"tEXt" + body) & 0xFFFFFFFF
            out.append(struct.pack(">I", len(body)) + b"tEXt" + body + struct.pack(">I", crc))
            inserted = True
        pos = end
    Path(path).write_bytes(b"".join(out))


def png_text(path) -> dict[str, str]:
    """Đọc mọi chunk tEXt của PNG."""
    data = Path(path).read_bytes()
    if data[:8] != PNG_SIG:
        raise ValueError(f"không phải PNG: {path}")
    res, pos = {}, 8
    while pos + 8 <= len(data):
        n = struct.unpack(">I", data[pos : pos + 4])[0]
        if data[pos + 4 : pos + 8] == b"tEXt":
            k, _, v = data[pos + 8 : pos + 8 + n].partition(b"\0")
            res[k.decode("latin-1")] = v.decode("latin-1")
        pos += 12 + n
    return res


def og_png_current(png, svg) -> bool:
    """True nếu PNG mang source-sha256 khớp sha256 hiện tại của SVG."""
    return png_text(png).get("source-sha256") == sha256_file(svg)


def frame_html(src: str, width: int, height: int) -> str:
    return (
        "<!doctype html><meta charset=utf-8>"
        "<body style='margin:0'>"
        f'<iframe id="f" src="{html.escape(src, quote=True)}" width="{int(width)}" height="{int(height)}" '
        'style="border:0;display:block"></iframe>'
        "<pre id=\"frame-out\"></pre>"
        "<script>(function(){var f=document.getElementById('f');"
        "function copy(){var d=f.contentDocument,o=d&&d.getElementById('out');"
        "if(o&&o.textContent)document.getElementById('frame-out').textContent=o.textContent;}"
        "f.addEventListener('load',copy);setInterval(copy,100);})();</script>"
    )


@contextlib.contextmanager
def serve(directory):
    """Phục vụ thư mục qua HTTP cổng 0; trả về URL gốc. Có thêm trang khung ảo."""

    class Handler(http.server.SimpleHTTPRequestHandler):
        def do_GET(self):
            if self.path.split("?")[0] == FRAME_PATH:
                from urllib.parse import parse_qs, urlparse

                q = parse_qs(urlparse(self.path).query)
                body = frame_html(
                    q.get("src", ["/"])[0], int(q.get("w", ["360"])[0]), int(q.get("h", ["800"])[0])
                ).encode()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                return
            super().do_GET()

        def log_message(self, *args):
            pass

    handler = functools.partial(Handler, directory=str(directory))
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def is_external(base: str) -> bool:
    """True nếu base không phải server nội bộ ở gốc (host ngoài hoặc có đường con)."""
    u = urlparse(base)
    return u.hostname not in ("127.0.0.1", "localhost") or bool(u.path.strip("/"))


def page_url(base: str, page: str, width: int, height: int, external: bool | None = None) -> str:
    """URL để chụp/đo ở bề rộng width: 1280 trực tiếp, nhỏ hơn qua iframe.

    Server nội bộ: khung ảo __frame__.html. Server ngoài (hoặc có đường con): ghép
    đường dẫn tương đối với base (giữ đường con) và khung là data: URL.
    """
    if external is None:
        external = is_external(base)
    if not external:
        page = page if page.startswith("/") else "/" + page
        if width >= 1000:
            return base + page
        return f"{base}{FRAME_PATH}?src={quote(page)}&w={int(width)}&h={int(height)}"
    root = base if base.endswith("/") else base + "/"
    target = root + page.lstrip("/")
    if width >= 1000:
        return target
    return "data:text/html;charset=utf-8," + quote(frame_html(target, width, height), safe="")


def check_reachable(url: str) -> None:
    """Ném RuntimeError nếu server trả lỗi HTTP hoặc không kết nối được."""
    try:
        with urllib.request.urlopen(url, timeout=15) as r:
            r.read(1)
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"{url}: HTTP {e.code}") from None
    except (urllib.error.URLError, OSError) as e:
        raise RuntimeError(f"{url}: không kết nối được ({e})") from None


def chrome_args(width: int, height: int, mode: str) -> list[str]:
    args = [
        chrome_path(),
        "--headless=new",
        "--disable-gpu",
        "--hide-scrollbars",
        "--no-first-run",
        "--no-default-browser-check",
        f"--window-size={width},{height}",
    ]
    if mode == "dark":
        args.append("--blink-settings=preferredColorScheme=0")
    return args


def _run_chrome(cmd: list[str]) -> subprocess.CompletedProcess:
    try:
        return subprocess.run(cmd, check=False, capture_output=True, text=True, timeout=60)
    except subprocess.TimeoutExpired:
        raise RuntimeError("Chrome quá thời gian (60 giây)") from None


def shoot(url: str, out: Path, width: int, height: int, mode: str) -> None:
    """Chụp url ra out. Xoá out cũ trước; lỗi Chrome thì RuntimeError và out không còn."""
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.unlink(missing_ok=True)
    with tempfile.TemporaryDirectory() as profile:
        cmd = chrome_args(width, height, mode) + [
            f"--user-data-dir={profile}",
            "--virtual-time-budget=3000",
            f"--screenshot={out}",
            url,
        ]
        r = _run_chrome(cmd)
    if r.returncode != 0 or not out.exists():
        out.unlink(missing_ok=True)
        raise RuntimeError(f"Chrome không tạo được ảnh (mã {r.returncode}): {r.stderr[-300:]}")


def dump_dom(url: str, width: int, height: int, mode: str) -> str:
    with tempfile.TemporaryDirectory() as profile:
        cmd = chrome_args(width, height, mode) + [
            f"--user-data-dir={profile}",
            "--virtual-time-budget=3000",
            "--dump-dom",
            url,
        ]
        r = _run_chrome(cmd)
    if r.returncode != 0 or not r.stdout.strip():
        raise RuntimeError(f"Chrome không dump được DOM (mã {r.returncode}): {r.stderr[-300:]}")
    return r.stdout


def parse_size(text: str) -> tuple[int, int]:
    try:
        w, h = (int(x) for x in text.lower().split("x"))
    except ValueError:
        raise ValueError(f"cỡ không hợp lệ: {text!r} (dạng WxH)") from None
    if w <= 0 or h <= 0:
        raise ValueError(f"cỡ không hợp lệ: {text!r}")
    return w, h


def shot_prefix(page: str) -> str:
    """/index.html -> '' ; /en/index.html -> 'en-' (tiền tố tên tệp ảnh)."""
    parts = [x for x in page.split("/") if x and x != "index.html"]
    return "".join(f"{x}-" for x in parts)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--url", help="URL gốc đã chạy sẵn (chụp trang /)")
    g.add_argument("--site", help="thư mục trang (mặc định site/)")
    ap.add_argument("--out", default=str(ROOT / ".autodev" / "shots"))
    ap.add_argument("--widths", default="360,1280")
    ap.add_argument("--modes", default="light,dark")
    ap.add_argument("--height", type=int, default=800)
    ap.add_argument("--pages", default="/index.html",
                    help="các trang chụp; trang con ra <tên>-<w>-<mode>.png (vd en-360-light.png)")
    ap.add_argument("--page", help="chụp đúng một trang/tệp (vd /og.svg) ra --file, cỡ --size")
    ap.add_argument("--size", default="1200x630", help="WxH cho --page")
    ap.add_argument("--file", help="tệp PNG đầu ra cho --page")
    a = ap.parse_args(argv)
    try:
        widths = [int(w) for w in a.widths.split(",") if w]
    except ValueError:
        ap.error(f"--widths không hợp lệ: {a.widths!r} (dạng 360,1280)")
    if not widths or any(w <= 0 for w in widths):
        ap.error(f"--widths phải là số nguyên dương: {a.widths!r}")
    if a.height <= 0:
        ap.error(f"--height phải > 0: {a.height}")
    modes = [m for m in a.modes.split(",") if m]
    for m in modes:
        if m not in ("light", "dark"):
            ap.error(f"chế độ không hợp lệ: {m}")
    out = Path(a.out)
    if out.exists() and not out.is_dir():
        ap.error(f"--out là tệp, không phải thư mục: {out}")
    pages = [p if p.startswith("/") else "/" + p for p in a.pages.split(",") if p]
    for p in pages + ([a.page] if a.page else []):
        if ".." in p.replace("\\", "/").split("/"):
            ap.error(f"đường dẫn thoát khỏi site/: {p!r}")

    try:
        return _main(a, ap, widths, modes, out, pages)
    except RuntimeError as e:
        print(f"Lỗi: {e}", file=sys.stderr)
        return 2


def _main(a, ap, widths, modes, out, pages) -> int:
    if a.page:
        if not a.file:
            ap.error("--page cần --file")
        try:
            w, h = parse_size(a.size)
        except ValueError as e:
            ap.error(str(e))
        page = a.page if a.page.startswith("/") else "/" + a.page

        def one(base: str) -> None:
            try:
                check_reachable(base + page)
            except RuntimeError:
                Path(a.file).unlink(missing_ok=True)
                raise
            shoot(base + page, Path(a.file), w, h, "light")
            src = Path(a.site or ROOT / "site") / page.lstrip("/")
            if not a.url and src.is_file():
                png_add_text(a.file, "source-sha256", sha256_file(src))
            print(a.file)

        if a.url:
            one(a.url.rstrip("/"))
        else:
            with serve(a.site or ROOT / "site") as base:
                one(base)
        return 0

    def run(base: str, external: bool = False) -> None:
        for pg in pages:
            real = page_url(base, pg, 1280, a.height, external=external)
            prefix = shot_prefix(pg)
            for w in widths:
                for m in modes:
                    path = out / f"{prefix}{w}-{m}.png"
                    try:
                        check_reachable(real)
                    except RuntimeError:
                        path.unlink(missing_ok=True)
                        raise
                    shoot(page_url(base, pg, w, a.height, external=external), path, w, a.height, m)
                    print(path)

    if a.url:
        run(a.url.rstrip("/"), external=True)
    else:
        with serve(a.site or ROOT / "site") as base:
            run(base)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
