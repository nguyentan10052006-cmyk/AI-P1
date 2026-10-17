"""Khung chạy solver: đo thời gian, bộ nhớ và giới hạn thời gian mỗi lần giải.

Mỗi solver chạy trong một tiến trình riêng. Nếu chạy quá lâu (ví dụ DFS đi sâu vô tận)
thì tiến trình bị dừng, server vẫn phản hồi bình thường.
"""
from __future__ import annotations

import multiprocessing as mp
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


def run_solver(solve_fn: SolveFn, problem: Problem, timeout_s: float = 60.0) -> Dict[str, Any]:
    """Chạy solve_fn(problem) trong tiến trình con, trả về dict kết quả hoặc lỗi."""
    parent_conn, child_conn = _CONTEXT.Pipe(duplex=False)
    process = _CONTEXT.Process(target=_worker, args=(child_conn, solve_fn, problem), daemon=True)
    process.start()
    child_conn.close()
    try:
        if not parent_conn.poll(timeout_s):
            return {"ok": False, "error": f"Quá {timeout_s:g} giây, đã dừng solver"}
        return parent_conn.recv()
    except EOFError:
        return {"ok": False, "error": "Solver bị dừng bất thường (có thể hết bộ nhớ)"}
    finally:
        if process.is_alive():
            process.terminate()
        process.join(timeout=5)
        parent_conn.close()
