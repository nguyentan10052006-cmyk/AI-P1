"""Khung chạy solver cho GUI: tiến trình riêng, giới hạn thời gian và cho phép hủy giữa chừng.

Mỗi lần giải chạy trong một tiến trình con. Nếu chạy quá lâu (ví dụ DFS đi sâu vô tận)
hoặc người dùng bấm Hủy, tiến trình bị dừng và server vẫn phản hồi bình thường.
Số liệu chính thức của thực nghiệm do script riêng đo (docs/04), không lấy từ đây.
"""
from __future__ import annotations

import multiprocessing as mp
import threading
import time
import tracemalloc
from dataclasses import fields
from typing import Any, Dict, Optional, Type

from bloxorz.problem import Problem

from .base import NO_SOLUTION, SOLVED, SearchResult, Solver

# "spawn" để không copy trạng thái của server (có nhiều luồng) sang tiến trình con.
_CONTEXT = mp.get_context("spawn")


class SolveJob:
    """Một lần giải đang chạy. cancel() dừng tiến trình solver ngay lập tức."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._process = None
        self.cancelled = False

    def attach(self, process) -> None:
        with self._lock:
            self._process = process
            if self.cancelled:
                process.terminate()

    def cancel(self) -> None:
        with self._lock:
            self.cancelled = True
            if self._process is not None and self._process.is_alive():
                self._process.terminate()


def _worker(conn, solver_cls: Type[Solver], problem: Problem) -> None:
    try:
        solver = solver_cls()
        tracemalloc.start()
        try:
            started = time.perf_counter()
            solver.prepare(problem)
            prepared = time.perf_counter()
            result = solver.search(problem)
            finished = time.perf_counter()
            _, peak = tracemalloc.get_traced_memory()
        finally:
            tracemalloc.stop()
        if not isinstance(result, SearchResult):
            raise TypeError(f"search() phải trả về SearchResult, nhận {type(result).__name__}")
        if result.status not in (SOLVED, NO_SOLUTION):
            raise ValueError(f"status phải là {SOLVED!r} hoặc {NO_SOLUTION!r}, nhận {result.status!r}")
        conn.send({
            "ok": True,
            # không dùng asdict(): nó đổi luôn các Action trong path thành dict
            **{f.name: getattr(result, f.name) for f in fields(result)},
            "prepare_ms": (prepared - started) * 1000,
            "time_ms": (finished - prepared) * 1000,
            "peak_kb": peak / 1024,
        })
    except NotImplementedError as exc:  # solver chưa cài đặt: thông báo đã nói rõ file cần viết
        conn.send({"ok": False, "error": str(exc)})
    except Exception as exc:  # solver bị lỗi: giữ tên lỗi để dễ tìm nguyên nhân
        message = str(exc) or type(exc).__name__
        conn.send({"ok": False, "error": f"{type(exc).__name__}: {message}"})
    finally:
        conn.close()


def run_solver(solver_cls: Type[Solver], problem: Problem, timeout_s: float = 60.0,
               job: Optional[SolveJob] = None) -> Dict[str, Any]:
    """Chạy prepare() rồi search() trong tiến trình con, trả về dict kết quả, lỗi, hết giờ hoặc đã hủy."""
    parent_conn, child_conn = _CONTEXT.Pipe(duplex=False)
    process = _CONTEXT.Process(target=_worker, args=(child_conn, solver_cls, problem), daemon=True)
    process.start()
    if job is not None:
        job.attach(process)
    child_conn.close()
    try:
        if not parent_conn.poll(timeout_s):
            return {"ok": False, "timeout": True, "error": f"Quá {timeout_s:g} giây, đã dừng solver"}
        return parent_conn.recv()
    except EOFError:
        if job is not None and job.cancelled:
            return {"ok": False, "cancelled": True, "error": "Đã hủy"}
        return {"ok": False, "error": "Solver bị dừng bất thường (có thể hết bộ nhớ)"}
    finally:
        if process.is_alive():
            process.terminate()
        process.join(timeout=5)
        parent_conn.close()
