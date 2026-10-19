"""Solver giả để kiểm thử khung chạy solver và API. Phải nằm ở mức module để tiến trình con import được."""
import time

from bloxorz.state import Action, Dir
from solvers.base import NO_SOLUTION, SOLVED, SearchResult, Solver


class FakeSolver(Solver):
    """Lời giải đúng cho màn "S##G": lăn phải hai lần."""

    def search(self, problem):
        return SearchResult(SOLVED, [Action(Dir.RIGHT), Action(Dir.RIGHT)], path_cost=2,
                            expanded=3, generated=4, max_frontier=2, visited=4)


class EmptySolver(Solver):
    """Không tìm thấy lời giải."""

    def search(self, problem):
        return SearchResult(NO_SOLUTION, expanded=7, generated=9, max_frontier=3, visited=8)


class IllegalSolver(Solver):
    """Lời giải sai: lăn trái ra khỏi bảng ngay từ đầu."""

    def search(self, problem):
        return SearchResult(SOLVED, [Action(Dir.LEFT)], path_cost=1, expanded=1)


class SleepySolver(Solver):
    """Chạy quá lâu để kiểm tra giới hạn thời gian."""

    def search(self, problem):
        time.sleep(30)
        return SearchResult(NO_SOLUTION)


class CrashingSolver(Solver):
    def search(self, problem):
        raise RuntimeError("boom")


class NotImplementedSolver(Solver):
    def search(self, problem):
        raise NotImplementedError("BFS chưa được cài đặt (test)")


class WrongReturnSolver(Solver):
    """Quên đổi sang SearchResult: trả về list."""

    def search(self, problem):
        return [Action(Dir.RIGHT)]
