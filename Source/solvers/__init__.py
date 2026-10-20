"""Các thuật toán tìm kiếm. Mỗi file là một lớp con của Solver (solvers/base.py)."""
from .astar import AStar, AStarM
from .bfs import BFS
from .dfs import DFS
from .ucs import UCS

ALGORITHMS = {
    "bfs": BFS,
    "dfs": DFS,
    "ucs": UCS,
    "astar": AStar,     # h_P, heuristic chính
    "astar_m": AStarM,  # h_M, để so sánh với h_P
}
