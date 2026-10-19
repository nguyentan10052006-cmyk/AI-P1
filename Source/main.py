"""Điểm vào: khởi động server và mở giao diện 3D trong trình duyệt."""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import webbrowser
from pathlib import Path

from bloxorz.level import LevelError, load_levels
from server.app import make_server

ROOT = Path(__file__).resolve().parent
LEVELS_DIR = ROOT / "levels"
WEB_DIR = ROOT / "web"


def open_browser(url: str) -> None:
    # Chạy trong WSL: mở trình duyệt của Windows bằng explorer.exe
    if shutil.which("explorer.exe"):
        try:
            subprocess.Popen(["explorer.exe", url])
            return
        except OSError:
            pass
    webbrowser.open(url)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Bloxorz: giao diện 3D và các thuật toán tìm kiếm")
    parser.add_argument("--port", type=int, default=8000, help="cổng HTTP (mặc định 8000)")
    parser.add_argument("--timeout", type=float, default=60.0,
                        help="giới hạn thời gian mỗi lần giải, tính bằng giây (mặc định 60)")
    parser.add_argument("--no-browser", action="store_true", help="không tự mở trình duyệt")
    args = parser.parse_args(argv)

    try:
        levels = load_levels(LEVELS_DIR)
    except LevelError as exc:
        print(f"Lỗi màn chơi: {exc}", file=sys.stderr)
        return 1

    try:
        server = make_server(levels, WEB_DIR, port=args.port, timeout_s=args.timeout)
    except OSError as exc:
        print(f"Không mở được cổng {args.port}: {exc}", file=sys.stderr)
        return 1

    url = f"http://localhost:{args.port}/"
    print(f"Bloxorz đang chạy tại {url}  (nhấn Ctrl+C để dừng)")
    if not args.no_browser:
        open_browser(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
