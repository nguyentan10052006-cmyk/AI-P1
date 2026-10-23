"""Solver giả riêng cho test của script thực nghiệm (V23). Số liệu ở đây là dữ liệu giả, chỉ để kiểm tra pipeline.

Phải nằm ở mức module để tiến trình con (spawn) import được. Các solver giả dùng chung nằm ở tests/fakes.py.
"""
import tracemalloc

from bloxorz.state import Action, Dir
from solvers.base import SOLVED, SearchResult, Solver


class TracingProbeSolver(Solver):
    """Giải đúng màn "S##G" và báo qua `expanded` là tracemalloc có đang bật lúc search() không (1 = có)."""

    def search(self, problem):
        return SearchResult(SOLVED, [Action(Dir.RIGHT), Action(Dir.RIGHT)], path_cost=2,
                            expanded=int(tracemalloc.is_tracing()), generated=2, max_frontier=1, visited=3)


class WrongCostSolver(Solver):
    """Đường đi đúng nhưng báo sai path_cost: script phải ghi invalid."""

    def search(self, problem):
        return SearchResult(SOLVED, [Action(Dir.RIGHT), Action(Dir.RIGHT)], path_cost=5,
                            expanded=1, generated=2, max_frontier=1, visited=3)
