"""Smoke test trang đã deploy lên GitHub Pages.

Dùng: python scripts/smoke_pages.py [--url URL] [--sha SHA]
Không có --sha: chạy `git fetch origin main` rồi `git rev-parse origin/main`.
Mã thoát: 0 = đạt; 1 = sau mọi lần thử vẫn lỗi; 2 = lỗi công cụ (git: không phải
repo, không có remote, fetch lỗi, không có git).
"""

import argparse
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request

try:
    from scripts.site_config import SITE_URL
except ModuleNotFoundError:  # chạy trực tiếp: python scripts/smoke_pages.py
    from site_config import SITE_URL

MARKER = "Lười Code Studio"
EXTRA_PATHS = ("en/", "style.css", "og.png")
VERSION_RE = re.compile(
    r'<meta\s+name="version"\s+content="([^"]*)"', re.IGNORECASE
)


def fetch(url, timeout=15):
    """Trả (status, body bytes); lỗi HTTP trả mã lỗi, lỗi mạng trả (0, b'')."""
    req = urllib.request.Request(url, headers={"Cache-Control": "no-cache"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e:
        return e.code, b""
    except (urllib.error.URLError, OSError):
        return 0, b""


def check_content(url, sha):
    """Kiểm một lần; trả danh sách lỗi (rỗng là đạt)."""
    base = url if url.endswith("/") else url + "/"
    errors = []
    status, body = fetch(base)
    if status != 200:
        errors.append(f"{base}: HTTP {status}")
    else:
        html = body.decode("utf-8", errors="replace")
        if MARKER not in html:
            errors.append(f"{base}: thiếu '{MARKER}'")
        m = VERSION_RE.search(html)
        if not m:
            errors.append(f"{base}: thiếu meta version")
        elif m.group(1) != sha:
            errors.append(f"{base}: version {m.group(1)!r} != {sha!r}")
    for path in EXTRA_PATHS:
        status, _ = fetch(base + path)
        if status != 200:
            errors.append(f"{base + path}: HTTP {status}")
    return errors


class GitError(RuntimeError):
    pass


def _git(*args):
    try:
        out = subprocess.run(["git", *args], capture_output=True, text=True,
                             check=False)
    except OSError as e:
        raise GitError(f"không chạy được git: {e}") from e
    if out.returncode != 0:
        raise GitError(f"git {' '.join(args)} lỗi ({out.returncode}): "
                       f"{out.stderr.strip()[-300:]}")
    return out.stdout.strip()


def git_sha():
    """SHA của origin/main sau khi fetch; lỗi git ném GitError."""
    _git("fetch", "origin", "main")
    return _git("rev-parse", "origin/main")


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--url", default=SITE_URL)
    p.add_argument("--sha", default=None)
    p.add_argument("--retries", type=int, default=10)
    p.add_argument("--interval", type=float, default=30)
    args = p.parse_args(argv)
    try:
        sha = args.sha or git_sha()
    except GitError as e:
        print(f"Lỗi: {e}", file=sys.stderr)
        return 2
    errors = []
    for attempt in range(1, max(args.retries, 1) + 1):
        errors = check_content(args.url, sha)
        if not errors:
            print(f"OK (lần {attempt}): {args.url} @ {sha}")
            return 0
        print(f"lần {attempt}: " + "; ".join(errors), file=sys.stderr)
        if attempt < args.retries:
            time.sleep(args.interval)
    return 1


if __name__ == "__main__":
    sys.exit(main())
