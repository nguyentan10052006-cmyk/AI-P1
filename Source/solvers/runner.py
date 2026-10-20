"""Khung chạy solver cho GUI (V39, TV4): tiến trình riêng, hết giờ, Hủy và So sánh.

Mỗi lần giải chạy trong một tiến trình con. Nếu chạy quá lâu (ví dụ DFS đi sâu vô tận)
hoặc người dùng bấm Hủy, tiến trình bị dừng và GUI vẫn phản hồi bình thường.

Hai cách dùng (docs/07 §6):
- Không chặn, cho GUI Ursina: start_solver() hoặc start_compare() trả về ngay; GUI gọi poll()
  trong update() mỗi khung hình cho tới khi có kết quả. Không có callback từ tiến trình con.
- Chặn, cho server HTTP, test và dòng lệnh: run_solver() chờ tới khi có kết quả.

Kết quả là một dict:
- thành công: {'ok': True, các trường của SearchResult, 'prepare_ms', 'time_ms', 'peak_kb'}
- không thành công: {'ok': False, 'error': ...}, kèm 'timeout': True hoặc 'cancelled': True nếu là hai lý do đó.
Thời gian và bộ nhớ ở đây chỉ để GUI tham khảo; số liệu chính thức do script thực nghiệm đo (docs/04).
"""
from __future__ import annotations

import multiprocessing as mp
import threading
import time
import tracemalloc
from dataclasses import fields
from typing import Any, Dict, Mapping, Optional, Sequence, Type

from bloxorz.problem import Problem

from .base import NO_SOLUTION, SOLVED, SearchResult, Solver

Outcome = Dict[str, Any]

# "spawn" trên mọi hệ điều hành: hành vi giống Windows, và không copy trạng thái của tiến trình cha
_CONTEXT = mp.get_context("spawn")

# Thứ tự cột của nút So sánh: 4 thuật toán, rồi A* với h_M để so với h_P (bien-ban #15)
COMPARE_NAMES = ("bfs", "dfs", "ucs", "astar", "astar_m")


def _cancelled() -> Outcome:
    return {"ok": False, "cancelled": True, "error": "Đã hủy"}


def _timed_out(timeout_s: float) -> Outcome:
    return {"ok": False, "timeout": True, "error": f"Quá {timeout_s:g} giây, đã dừng solver"}


class SolveJob:
    """Một lần giải. Tạo bằng start_solver(), hoặc tạo rỗng rồi truyền vào run_solver(job=...)
    để một luồng khác có thể cancel() trong lúc run_solver() đang chờ (server HTTP làm vậy)."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._process = None
        self._conn = None
        self._started: Optional[float] = None
        self._finished: Optional[float] = None
        self._result: Optional[Outcome] = None
        self.timeout_s = 60.0
        self.cancelled = False

    def start(self, solver_cls: Type[Solver], problem: Problem, timeout_s: float = 60.0) -> "SolveJob":
        """Mở tiến trình con rồi trả về ngay."""
        parent_conn, child_conn = _CONTEXT.Pipe(duplex=False)
        process = _CONTEXT.Process(target=_worker, args=(child_conn, solver_cls, problem), daemon=True)
        with self._lock:
            if self._process is not None:
                raise RuntimeError("SolveJob đã được chạy")
            self.timeout_s = timeout_s
            self._conn = parent_conn
            self._process = process
            self._started = time.perf_counter()
            process.start()
            if self.cancelled:  # đã bấm Hủy trước khi kịp mở tiến trình
                process.terminate()
        child_conn.close()
        return self

    @property
    def elapsed(self) -> float:
        """Số giây đã chạy (dừng đếm khi đã có kết quả), để GUI hiện "Đang tìm… 12 s"."""
        if self._started is None:
            return 0.0
        end = self._finished if self._finished is not None else time.perf_counter()
        return end - self._started

    @property
    def done(self) -> bool:
        return self._result is not None

    def poll(self) -> Optional[Outcome]:
        """None khi chưa xong; không chặn. Quá timeout_s thì dừng tiến trình và trả kết quả hết giờ."""
        return self._collect(0.0)

    def wait(self) -> Outcome:
        """Chờ tới khi có kết quả (hết giờ, hủy hoặc solver xong)."""
        while True:
            result = self._collect(max(0.0, self.timeout_s - self.elapsed))
            if result is not None:
                return result

    def cancel(self) -> None:
        """Dừng tiến trình con ngay; lần poll() sau trả kết quả đã hủy."""
        with self._lock:
            self.cancelled = True
            if self._process is not None and self._process.is_alive():
                self._process.terminate()

    def _collect(self, wait_s: float) -> Optional[Outcome]:
        if self._result is not None:
            return self._result
        if self._conn is None:
            raise RuntimeError("SolveJob chưa được chạy (gọi start() hoặc start_solver() trước)")
        if self.cancelled:
            return self._finish(_cancelled())
        try:
            # poll() cũng trả True khi tiến trình con đã tắt (EOF), nên không bị treo khi solver chết
            if self._conn.poll(wait_s):
                return self._finish(self._conn.recv())
        except (EOFError, OSError):
            if self.cancelled:
                return self._finish(_cancelled())
            return self._finish({"ok": False, "error": "Solver bị dừng bất thường (có thể hết bộ nhớ)"})
        if self.cancelled:
            return self._finish(_cancelled())
        if self.elapsed >= self.timeout_s:
            return self._finish(_timed_out(self.timeout_s))
        return None

    def _finish(self, result: Outcome) -> Outcome:
        with self._lock:
            if self._result is None:
                self._result = result
                self._finished = time.perf_counter()
                if self._process.is_alive():
                    self._process.terminate()
                self._process.join(timeout=5)
                self._conn.close()
            return self._result


class CompareJob:
    """Chạy lần lượt nhiều solver trên cùng một bài toán, mỗi solver một tiến trình.
    Chạy lần lượt, không song song, để thời gian và bộ nhớ không ảnh hưởng lẫn nhau."""

    def __init__(self, problem: Problem, names: Sequence[str], algorithms: Mapping[str, Type[Solver]],
                 timeout_s: float = 60.0) -> None:
        unknown = [name for name in names if name not in algorithms]
        if unknown:
            raise KeyError(f"thuật toán không có trong ALGORITHMS: {unknown}")
        self.problem = problem
        self.names = tuple(names)
        self.timeout_s = timeout_s
        self._algorithms = algorithms
        self._results: Dict[str, Outcome] = {}
        self._job: Optional[SolveJob] = None
        self._next = 0
        self.cancelled = False
        self._start_next()

    @property
    def done(self) -> bool:
        return len(self._results) == len(self.names)

    @property
    def running(self) -> Optional[str]:
        """Tên thuật toán đang chạy, hoặc None khi đã xong."""
        return None if self.done else self.names[self._next - 1]

    @property
    def elapsed(self) -> float:
        """Số giây thuật toán đang chạy đã dùng."""
        return 0.0 if self._job is None or self.done else self._job.elapsed

    def poll(self) -> Dict[str, Outcome]:
        """Kết quả của các thuật toán đã xong tới lúc gọi, theo thứ tự names. Không chặn."""
        if not self.done and self._job is not None:
            result = self._job.poll()
            if result is not None:
                self._results[self.running] = result
                self._start_next()
        return {name: self._results[name] for name in self.names if name in self._results}

    def cancel(self) -> None:
        """Dừng thuật toán đang chạy; các thuật toán chưa chạy cũng được ghi là đã hủy."""
        self.cancelled = True
        if self._job is not None:
            self._job.cancel()
        for name in self.names:
            self._results.setdefault(name, _cancelled())

    def _start_next(self) -> None:
        if self.cancelled or self._next >= len(self.names):
            return
        name = self.names[self._next]
        self._next += 1
        self._job = start_solver(self._algorithms[name], self.problem, self.timeout_s)


def start_solver(solver_cls: Type[Solver], problem: Problem, timeout_s: float = 60.0) -> SolveJob:
    """Mở tiến trình con chạy prepare() rồi search(), trả về SolveJob ngay. GUI gọi job.poll() mỗi khung hình."""
    return SolveJob().start(solver_cls, problem, timeout_s)


def start_compare(problem: Problem, names: Sequence[str] = COMPARE_NAMES, timeout_s: float = 60.0,
                  algorithms: Optional[Mapping[str, Type[Solver]]] = None) -> CompareJob:
    """Bắt đầu So sánh, trả về CompareJob ngay. algorithms mặc định là solvers.ALGORITHMS."""
    if algorithms is None:
        from . import ALGORITHMS  # import muộn: solvers/__init__.py không phụ thuộc runner
        algorithms = ALGORITHMS
    return CompareJob(problem, names, algorithms, timeout_s)


def run_solver(solver_cls: Type[Solver], problem: Problem, timeout_s: float = 60.0,
               job: Optional[SolveJob] = None) -> Outcome:
    """Chạy và chờ tới khi có kết quả. Truyền job để luồng khác có thể cancel() giữa chừng."""
    job = job if job is not None else SolveJob()
    return job.start(solver_cls, problem, timeout_s).wait()


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
