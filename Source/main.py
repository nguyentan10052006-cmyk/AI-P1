"""Điểm vào: mở GUI Ursina. Chạy trong Source/: python main.py [mã màn, ví dụ 05]"""
from __future__ import annotations

import sys


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    # Import ở đây, không đặt ở đầu file: tiến trình con của solver (spawn) nạp lại file này,
    # import ursina ở cấp ngoài cùng sẽ làm mỗi lần Solve chậm thêm (docs/07 §2).
    from gui.app import run
    return run(argv[0] if argv else "01")


if __name__ == "__main__":   # bắt buộc trên Windows khi dùng multiprocessing
    raise SystemExit(main())
