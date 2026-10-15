"""Chụp trang qua Chrome headless: 360px (qua iframe) và 1280px, sáng và tối."""

from __future__ import annotations

import argparse
import contextlib
import functools
import http.server
import os
import shutil
import struct
import subprocess
import tempfile
import threading
from pathlib import Path

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


def frame_html(src: str, width: int, height: int) -> str:
    return (
        "<!doctype html><meta charset=utf-8>"
        "<body style='margin:0'>"
        f'<iframe id="f" src="{src}" width="{width}" height="{height}" '
        'style="border:0;display:block"></iframe>'
        "<pre id=\"frame-out\"></pre>"
        "<script>document.getElementById('f').addEventListener('load',function(){"
        "var d=this.contentDocument,o=d&&d.getElementById('out');"
        "document.getElementById('frame-out').textContent=o?o.textContent:'';});</script>"
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


def page_url(base: str, page: str, width: int, height: int) -> str:
    """URL để chụp/đo ở bề rộng width: 1280 trực tiếp, nhỏ hơn qua iframe."""
    page = page if page.startswith("/") else "/" + page
    if width >= 1000:
        return base + page
    return f"{base}{FRAME_PATH}?src={page}&w={width}&h={height}"


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


def shoot(url: str, out: Path, width: int, height: int, mode: str) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as profile:
        cmd = chrome_args(width, height, mode) + [
            f"--user-data-dir={profile}",
            "--virtual-time-budget=3000",
            f"--screenshot={out}",
            url,
        ]
        r = subprocess.run(cmd, check=False, capture_output=True, text=True, timeout=60)
    if not out.exists():
        raise RuntimeError(f"Chrome không tạo được ảnh: {r.stderr[-300:]}")


def dump_dom(url: str, width: int, height: int, mode: str) -> str:
    with tempfile.TemporaryDirectory() as profile:
        cmd = chrome_args(width, height, mode) + [
            f"--user-data-dir={profile}",
            "--virtual-time-budget=3000",
            "--dump-dom",
            url,
        ]
        r = subprocess.run(cmd, check=False, capture_output=True, text=True, timeout=60)
    return r.stdout


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--url", help="URL gốc đã chạy sẵn (chụp trang /)")
    g.add_argument("--site", help="thư mục trang (mặc định site/)")
    ap.add_argument("--out", default=str(ROOT / ".autodev" / "shots"))
    ap.add_argument("--widths", default="360,1280")
    ap.add_argument("--modes", default="light,dark")
    ap.add_argument("--height", type=int, default=800)
    a = ap.parse_args(argv)
    widths = [int(w) for w in a.widths.split(",") if w]
    modes = [m for m in a.modes.split(",") if m]
    for m in modes:
        if m not in ("light", "dark"):
            ap.error(f"chế độ không hợp lệ: {m}")
    out = Path(a.out)

    def run(base: str) -> None:
        for w in widths:
            for m in modes:
                path = out / f"{w}-{m}.png"
                shoot(page_url(base, "/index.html", w, a.height), path, w, a.height, m)
                print(path)

    if a.url:
        run(a.url.rstrip("/"))
    else:
        with serve(a.site or ROOT / "site") as base:
            run(base)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
