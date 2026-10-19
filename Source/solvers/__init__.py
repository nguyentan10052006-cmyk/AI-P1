"""Các thuật toán tìm kiếm. Mỗi file là một lớp con của Solver (solvers/base.py)."""
from .astar import AStar
from .bfs import BFS
from .dfs import DFS
from .ucs import UCS

ALGORITHMS = {
    "bfs": BFS,
    "dfs": DFS,
    "ucs": UCS,
    "astar": AStar,
}
