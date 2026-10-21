"""Smoke test trang đã deploy lên GitHub Pages.

Dùng: python scripts/smoke_pages.py [--url URL] [--sha SHA]
Hợp đồng SHA: không có --sha thì MỖI LẦN THỬ fetch lại và lấy SHA `main` của remote
(`git fetch origin +refs/heads/main:refs/remotes/origin/main` rồi
`git rev-parse origin/main`; refspec tường minh nên đúng cả ở clone
--single-branch khác nhánh). Đạt khi `/` và `/en/` đều mang đúng SHA mới nhất đó;
trang mang SHA cũ hơn `main` hiện tại luôn trượt. Có --sha thì cố định, không gọi git.
Tài nguyên phải 200: en/, style.css, og.png, main.js, robots.txt, sitemap.xml.
Mã thoát: 0 = đạt; 1 = sau mọi lần thử vẫn lỗi; 2 = lỗi công cụ (git: không phải
repo, không có remote, fetch lỗi, không có git, git quá GIT_TIMEOUT giây) hoặc
tham số sai (--url không phải http/https có host, --interval < 0, --retries <= 0).
Mỗi lệnh git có timeout GIT_TIMEOUT (60s) và GIT_TERMINAL_PROMPT=0 (không chờ
mật khẩu). Lỗi mạng giữa chừng (IncompleteRead...) tính là lần thử lỗi.
"""

import argparse
import http.client
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

try:
    from scripts.site_config import SITE_URL
except ModuleNotFoundError:  # chạy trực tiếp: python scripts/smoke_pages.py
    from site_config import SITE_URL

GIT_TIMEOUT = 60
MARKER = "Lười Code Studio"
EXTRA_PATHS = ("style.css", "og.png", "main.js", "robots.txt", "sitemap.xml")
VERSION_RE = re.compile(
    r'<meta\s+name="version"\s+content="([^"]*)"', re.IGNORECASE
)


def fetch(url, timeout=15):
    """Trả (status, body bytes); lỗi HTTP trả mã lỗi, lỗi mạng trả (0, b'')."""
    try:
        req = urllib.request.Request(url, headers={"Cache-Control": "no-cache"})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e:
        return e.code, b""
    except (urllib.error.URLError, OSError, http.client.HTTPException,
            ValueError):
        return 0, b""


def check_content(url, sha):
    """Kiểm một lần; trả danh sách lỗi (rỗng là đạt)."""
    base = url if url.endswith("/") else url + "/"
    errors = []
    for page, need_marker in ((base, True), (base + "en/", False)):
        status, body = fetch(page)
        if status != 200:
            errors.append(f"{page}: HTTP {status}")
            continue
        html = body.decode("utf-8", errors="replace")
        if need_marker and MARKER not in html:
            errors.append(f"{page}: thiếu '{MARKER}'")
        m = VERSION_RE.search(html)
        if not m:
            errors.append(f"{page}: thiếu meta version")
        elif m.group(1) != sha:
            errors.append(f"{page}: version {m.group(1)!r} != {sha!r}")
    for path in EXTRA_PATHS:
        status, _ = fetch(base + path)
        if status != 200:
            errors.append(f"{base + path}: HTTP {status}")
    return errors


class GitError(RuntimeError):
    pass


def _git(*args):
    try:
        out = subprocess.run(
            ["git", *args], capture_output=True, text=True, check=False,
            timeout=GIT_TIMEOUT,
            env={**os.environ, "GIT_TERMINAL_PROMPT": "0"},
        )
    except subprocess.TimeoutExpired as e:
        raise GitError(f"git {' '.join(args)} quá timeout {GIT_TIMEOUT}s") from e
    except OSError as e:
        raise GitError(f"không chạy được git: {e}") from e
    if out.returncode != 0:
        raise GitError(f"git {' '.join(args)} lỗi ({out.returncode}): "
                       f"{out.stderr.strip()[-300:]}")
    return out.stdout.strip()


def git_sha():
    """SHA `main` của remote sau khi fetch (rev-parse origin/main); lỗi ném GitError."""
    _git("fetch", "origin", "+refs/heads/main:refs/remotes/origin/main")
    return _git("rev-parse", "origin/main")


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--url", default=SITE_URL)
    p.add_argument("--sha", default=None)
    p.add_argument("--retries", type=int, default=10)
    p.add_argument("--interval", type=float, default=30)
    args = p.parse_args(argv)
    try:
        parts = urllib.parse.urlsplit(args.url)
        host = parts.hostname
        scheme = parts.scheme
    except ValueError:
        host, scheme = None, ""
    problem = None
    if scheme not in ("http", "https") or not host:
        problem = f"--url phải là http/https có host: {args.url!r}"
    elif not (args.interval >= 0):
        problem = f"--interval phải >= 0: {args.interval}"
    elif args.retries <= 0:
        problem = f"--retries phải > 0: {args.retries}"
    if problem:
        print(f"Lỗi: {problem}", file=sys.stderr)
        return 2
    sha = args.sha
    for attempt in range(1, args.retries + 1):
        if not args.sha:
            try:
                sha = git_sha()
            except GitError as e:
                print(f"Lỗi: {e}", file=sys.stderr)
                return 2
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
