"""Solver giả riêng cho test của script thực nghiệm (V23). Số liệu ở đây là dữ liệu giả, chỉ để kiểm tra pipeline.

Phải nằm ở mức module để tiến trình con (spawn) import được. Các solver giả dùng chung nằm ở tests/fakes.py.
"""
import os
import time
import tracemalloc

from bloxorz.state import Action, Dir
from solvers.base import NO_SOLUTION, SOLVED, SearchResult, Solver


class TracingProbeSolver(Solver):
    """Giải đúng màn "S##G" và báo qua `expanded` là tracemalloc có đang bật lúc search() không (1 = có)."""

    def search(self, problem):
        return SearchResult(SOLVED, [Action(Dir.RIGHT), Action(Dir.RIGHT)], path_cost=2,
                            expanded=int(tracemalloc.is_tracing()), generated=2, max_frontier=1, visited=3)


def _right_right(**counts):
    defaults = dict(expanded=1, generated=2, max_frontier=1, visited=3)
    defaults.update(counts)
    return SearchResult(SOLVED, [Action(Dir.RIGHT), Action(Dir.RIGHT)], path_cost=2, **defaults)


class SlowWhenTracingSolver(Solver):
    """Nhanh khi đo thời gian, chậm 2 giây khi tracemalloc bật: giả lập lần đo bộ nhớ hết giờ (F1)."""

    def search(self, problem):
        if tracemalloc.is_tracing():
            time.sleep(2)
        return _right_right()


class NoSolutionWhenTracingSolver(Solver):
    """Lần đo bộ nhớ ra kết quả khác lần đo thời gian (F1)."""

    def search(self, problem):
        if tracemalloc.is_tracing():
            return SearchResult(NO_SOLUTION, expanded=1, generated=2, max_frontier=1, visited=3)
        return _right_right()


class CountsDifferWhenTracingSolver(Solver):
    """Cùng lời giải nhưng số nút khác ở lần đo bộ nhớ (F4)."""

    def search(self, problem):
        return _right_right(expanded=9 if tracemalloc.is_tracing() else 1)


class HardExitSolver(Solver):
    """Tiến trình con chết đột ngột, không kịp gửi kết quả (F5)."""

    def search(self, problem):
        os._exit(3)


class RoundingCostSolver(Solver):
    """Đường đi đúng, path_cost lệch 1.5e-9 như sai số khi cộng chi phí lẻ theo thứ tự khác: vẫn là solved."""

    def search(self, problem):
        return SearchResult(SOLVED, [Action(Dir.RIGHT), Action(Dir.RIGHT)], path_cost=2 + 1.5e-9,
                            expanded=1, generated=2, max_frontier=1, visited=3)


class WrongCostSolver(Solver):
    """Đường đi đúng nhưng báo sai path_cost: script phải ghi invalid."""

    def search(self, problem):
        return SearchResult(SOLVED, [Action(Dir.RIGHT), Action(Dir.RIGHT)], path_cost=5,
                            expanded=1, generated=2, max_frontier=1, visited=3)
