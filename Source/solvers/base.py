"""Hợp đồng chung của các solver: kết quả trả về và lớp cơ sở (docs/01 mục 4)."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from bloxorz.problem import Problem
from bloxorz.state import Action

SOLVED = "solved"
NO_SOLUTION = "no_solution"
TIMEOUT = "timeout"  # do khung chạy solver gán khi quá giờ, solver không tự trả về


@dataclass
class SearchResult:
    """Kết quả một lần tìm kiếm. Cách đếm các chỉ số theo docs/04 mục 3.

    path      : dãy hành động từ trạng thái đầu tới đích; rỗng khi không có lời giải
    path_cost : tổng step_cost dọc path
    expanded  : số nút lấy ra khỏi frontier để sinh con
    generated : số trạng thái con hợp lệ (result() khác None), đếm trước khi xét tập đã thăm
    max_frontier : kích thước frontier lớn nhất
    visited   : số trạng thái khác nhau đã gặp
    """

    status: str
    path: List[Action] = field(default_factory=list)
    path_cost: float = 0.0
    expanded: int = 0
    generated: int = 0
    max_frontier: int = 0
    visited: int = 0


class Solver:
    """Lớp cơ sở. Mỗi thuật toán là một lớp con, đăng ký trong solvers/__init__.py."""

    name = "BASE"

    def prepare(self, problem: Problem) -> None:
        """Tiền xử lý trước khi tìm (ví dụ bảng heuristic của A*). Mặc định không làm gì."""

    def search(self, problem: Problem) -> SearchResult:
        raise NotImplementedError(f"{self.name} chưa cài đặt")
