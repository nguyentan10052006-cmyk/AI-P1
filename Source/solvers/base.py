"""Khung chạy solver: đo thời gian, bộ nhớ, giới hạn thời gian và cho phép hủy giữa chừng.

Mỗi solver chạy trong một tiến trình riêng. Nếu chạy quá lâu (ví dụ DFS đi sâu vô tận)
hoặc người dùng bấm Hủy, tiến trình bị dừng và server vẫn phản hồi bình thường.
"""
from __future__ import annotations

import multiprocessing as mp
import threading
import time
import tracemalloc
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional

from bloxorz.problem import Problem
from bloxorz.state import Action


@dataclass
class SearchResult:
    """Kết quả solver trả về. actions = None nghĩa là không có lời giải."""

    actions: Optional[List[Action]]
    expanded: int = 0


SolveFn = Callable[[Problem], SearchResult]

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


def _worker(conn, solve_fn: SolveFn, problem: Problem) -> None:
    try:
        tracemalloc.start()
        try:
            started = time.perf_counter()
            result = solve_fn(problem)
            elapsed = time.perf_counter() - started
            _, peak = tracemalloc.get_traced_memory()
        finally:
            tracemalloc.stop()
        conn.send({
            "ok": True,
            "actions": result.actions,
            "expanded": result.expanded,
            "time_ms": elapsed * 1000,
            "peak_kb": peak / 1024,
        })
    except Exception as exc:  # solver chưa cài đặt hoặc bị lỗi
        message = str(exc) or type(exc).__name__
        conn.send({"ok": False, "error": f"{type(exc).__name__}: {message}"})
    finally:
        conn.close()


def run_solver(solve_fn: SolveFn, problem: Problem, timeout_s: float = 60.0,
               job: Optional[SolveJob] = None) -> Dict[str, Any]:
    """Chạy solve_fn(problem) trong tiến trình con, trả về dict kết quả, lỗi hoặc đã hủy."""
    parent_conn, child_conn = _CONTEXT.Pipe(duplex=False)
    process = _CONTEXT.Process(target=_worker, args=(child_conn, solve_fn, problem), daemon=True)
    process.start()
    if job is not None:
        job.attach(process)
    child_conn.close()
    try:
        if not parent_conn.poll(timeout_s):
            return {"ok": False, "error": f"Quá {timeout_s:g} giây, đã dừng solver"}
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
