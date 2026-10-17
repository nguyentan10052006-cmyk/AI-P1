"""Các thuật toán tìm kiếm. Mỗi file là một solver, cùng giao diện SolveFn."""
from .astar import astar
from .bfs import bfs
from .dfs import dfs
from .ucs import ucs

ALGORITHMS = {
    "bfs": bfs,
    "dfs": dfs,
    "ucs": ucs,
    "astar": astar,
}
