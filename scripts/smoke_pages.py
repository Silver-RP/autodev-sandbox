"""Smoke test trang đã deploy lên GitHub Pages.

Dùng: python scripts/smoke_pages.py [--url URL] [--sha SHA]
Exit 0 khi đạt, 1 khi sau mọi lần thử vẫn lỗi.
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


def git_sha():
    out = subprocess.run(
        ["git", "rev-parse", "origin/main"],
        capture_output=True,
        text=True,
        check=True,
    )
    return out.stdout.strip()


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--url", default=SITE_URL)
    p.add_argument("--sha", default=None)
    p.add_argument("--retries", type=int, default=10)
    p.add_argument("--interval", type=float, default=30)
    args = p.parse_args(argv)
    sha = args.sha or git_sha()
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
