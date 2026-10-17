"""Solver giả để kiểm thử khung chạy solver và API. Phải nằm ở mức module để tiến trình con import được."""
import time

from bloxorz.state import Action, Dir
from solvers.base import SearchResult


def fake_solver(problem):
    """Lời giải đúng cho màn "S##G": lăn phải hai lần."""
    return SearchResult([Action(Dir.RIGHT), Action(Dir.RIGHT)], expanded=3)


def empty_solver(problem):
    """Không tìm thấy lời giải."""
    return SearchResult(None, expanded=7)


def illegal_solver(problem):
    """Lời giải sai: lăn trái ra khỏi bảng ngay từ đầu."""
    return SearchResult([Action(Dir.LEFT)], expanded=1)


def sleepy_solver(problem):
    """Chạy quá lâu để kiểm tra giới hạn thời gian."""
    time.sleep(30)
    return SearchResult(None)


def crashing_solver(problem):
    raise RuntimeError("boom")


def not_implemented_solver(problem):
    raise NotImplementedError("BFS chưa được cài đặt (test)")
