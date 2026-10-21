"""Đo Lighthouse (mobile) trên site/ thật qua HTTP.

Mã thoát: 0 = đạt ngưỡng E2; 1 = dưới ngưỡng E2; 2 = lỗi công cụ (thiếu npx/Chrome,
Lighthouse lỗi hoặc quá --timeout, kết quả thiếu khoá/null/NaN/inf, trang không có
trong site, không có trang nào để đo).
"""

from __future__ import annotations

import argparse
import functools
import http.server
import json
import math
import os
import shutil
import statistics
import subprocess
import sys
import tempfile
import threading
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

ROOT = Path(__file__).resolve().parent.parent
CATEGORIES = ("performance", "accessibility", "best-practices", "seo")
THRESHOLDS = {"performance": 90, "accessibility": 95, "best-practices": 95, "seo": 95}
MAX_BYTES = 300 * 1024
RUNS_ROOT = 3
RUNS_EN = 1
DEFAULT_TIMEOUT = 180


def build_command(url: str, out_path: str, npx: str = "npx") -> list[str]:
    return [
        npx, "-y", "lighthouse@12", url, "--quiet",
        "--chrome-flags=--headless=new",
        "--form-factor=mobile",
        "--output=json", f"--output-path={out_path}",
    ]


def read_result(path) -> dict:
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        res = {}
        for c in CATEGORIES:
            res[c] = _finite(data["categories"][c]["score"], c) * 100
            res[c] = round(res[c])
        res["total-byte-weight"] = _finite(
            data["audits"]["total-byte-weight"]["numericValue"], "total-byte-weight")
    except (KeyError, TypeError, ValueError) as e:
        raise RuntimeError(f"kết quả Lighthouse không hợp lệ: {e!r}") from e
    return res


def _finite(v, name):
    if isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v):
        raise ValueError(f"{name} = {v!r}")
    return v


def median(values):
    return statistics.median(values)


def aggregate(runs: list[dict]) -> dict:
    keys = list(CATEGORIES) + ["total-byte-weight"]
    return {k: median([r[k] for r in runs]) for k in keys}


def failures(agg: dict) -> list[str]:
    bad = []
    for c, need in THRESHOLDS.items():
        if agg[c] < need:
            bad.append(f"{c} {agg[c]} < {need}")
    if agg["total-byte-weight"] > MAX_BYTES:
        bad.append(f"total-byte-weight {agg['total-byte-weight']:.0f} > {MAX_BYTES}")
    return bad


class MissingTool(RuntimeError):
    pass


def run_lighthouse(url: str, npx: str, env: dict, timeout: float = DEFAULT_TIMEOUT) -> dict:
    with tempfile.TemporaryDirectory() as td:
        out = os.path.join(td, "lh.json")
        try:
            proc = subprocess.run(build_command(url, out, npx), env=env, check=False,
                                  capture_output=True, text=True, timeout=timeout)
        except subprocess.TimeoutExpired as e:
            raise RuntimeError(f"lighthouse quá {timeout}s: {url}") from e
        if proc.returncode != 0 or not os.path.exists(out):
            raise RuntimeError(f"lighthouse lỗi ({proc.returncode}): {proc.stderr[-500:]}")
        return read_result(out)


def _serve(site: Path):
    class Quiet(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *args, **kwargs):
            pass

    handler = functools.partial(Quiet, directory=str(site))
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv


def _table(rows: dict[str, list[dict]]) -> None:
    print("page  run  perf  a11y  bp  seo  bytes")
    for page, runs in rows.items():
        for i, r in enumerate(runs, 1):
            print(f"{page}  {i}  {r['performance']}  {r['accessibility']}  "
                  f"{r['best-practices']}  {r['seo']}  {r['total-byte-weight']:.0f}")
        a = aggregate(runs)
        print(f"{page}  median  {a['performance']}  {a['accessibility']}  "
              f"{a['best-practices']}  {a['seo']}  {a['total-byte-weight']:.0f}")


def _pages(site: Path, spec: str | None) -> list[str]:
    if spec is None:
        return ["/"] + (["/en/"] if (site / "en" / "index.html").is_file() else [])
    out = []
    for p in (x.strip() for x in spec.split(",")):
        if not p:
            continue
        p = p if p.startswith("/") else "/" + p
        f = site / (p.lstrip("/") + ("index.html" if p.endswith("/") else ""))
        if not f.is_file():
            raise RuntimeError(f"trang không có trong {site}: {p}")
        out.append(p)
    return out


def main(argv=None, runner=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--site", default=str(ROOT / "site"))
    ap.add_argument("--runs", type=int, default=RUNS_ROOT)
    ap.add_argument("--en-runs", type=int, default=RUNS_EN)
    ap.add_argument("--pages", help="danh sách trang, vd /,/en/ (mặc định: / và /en/ nếu có)")
    ap.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT,
                    help="giây cho mỗi lần chạy Lighthouse")
    a = ap.parse_args(argv)
    runner = runner or run_lighthouse

    site_dir = Path(a.site)
    if not site_dir.is_dir():
        print(f"Lỗi: --site không phải thư mục: {site_dir}", file=sys.stderr)
        return 2
    if not (site_dir / "index.html").is_file():
        print(f"Lỗi: không có index.html trong {site_dir}", file=sys.stderr)
        return 2

    npx = shutil.which("npx")
    env = dict(os.environ)
    if runner is run_lighthouse:
        if not npx:
            print("Lỗi: không có npx (cài Node.js)", file=sys.stderr)
            return 2
        try:
            from scripts import screenshot as sh
            env["CHROME_PATH"] = sh.chrome_path()
        except RuntimeError as e:
            print(f"Lỗi: {e}", file=sys.stderr)
            return 2

    site = Path(a.site)
    srv = _serve(site)
    base = f"http://127.0.0.1:{srv.server_address[1]}"
    try:
        pages = _pages(site, a.pages)
    except RuntimeError as e:
        srv.shutdown()
        srv.server_close()
        print(f"Lỗi: {e}", file=sys.stderr)
        return 2
    plan = [(p, a.runs if p == "/" else a.en_runs) for p in pages]
    plan = [(p, n) for p, n in plan if n > 0]
    rows: dict[str, list[dict]] = {}
    try:
        if not plan:
            raise RuntimeError("không có trang nào để đo (kiểm --pages, --runs)")
        for path, n in plan:
            if runner is run_lighthouse:
                rows[path] = [runner(base + path, npx or "npx", env, timeout=a.timeout)
                              for _ in range(n)]
            else:
                rows[path] = [runner(base + path, npx or "npx", env) for _ in range(n)]
    except (RuntimeError, subprocess.TimeoutExpired) as e:
        print(f"Lỗi: {e}", file=sys.stderr)
        return 2
    finally:
        srv.shutdown()
        srv.server_close()

    _table(rows)
    bad = []
    for page, runs in rows.items():
        bad += [f"{page}: {m}" for m in failures(aggregate(runs))]
    if bad:
        print("TRƯỢT:\n" + "\n".join(bad))
        return 1
    print("OK: đạt ngưỡng E2")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
