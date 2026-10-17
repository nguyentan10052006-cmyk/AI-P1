"""Tiện ích dựng màn chơi nhỏ cho các bài test."""
from bloxorz.level import Level, parse_level


def make_level(grid, switches=(), level_id="test") -> Level:
    return parse_level({"grid": list(grid), "switches": list(switches)}, level_id)


def open_board(rows: int, cols: int, start) -> Level:
    """Bảng toàn nền '#', S tại start, G ở góc dưới phải."""
    grid = [["#"] * cols for _ in range(rows)]
    grid[start[0]][start[1]] = "S"
    grid[rows - 1][cols - 1] = "G"
    return make_level(["".join(row) for row in grid])
