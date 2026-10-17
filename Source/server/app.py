"""Server HTTP: phục vụ giao diện trong web/ và API JSON dưới /api/."""
from __future__ import annotations

import json
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Mapping, Tuple

from solvers import ALGORITHMS

from . import api

API_PREFIX = "/api/levels/"


class BloxorzServer(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, address, levels, web_dir: Path, timeout_s: float, algorithms) -> None:
        self.levels = levels
        self.timeout_s = timeout_s
        self.algorithms = algorithms
        super().__init__(address, partial(Handler, directory=str(web_dir)))


class Handler(SimpleHTTPRequestHandler):
    server: BloxorzServer

    def do_GET(self) -> None:
        path = self._path()
        if path == "/api/levels":
            self._send(api.list_levels(self.server.levels))
        elif path.startswith(API_PREFIX):
            self._send(api.get_level(self.server.levels, path[len(API_PREFIX):]))
        elif path.startswith("/api/"):
            self._send((404, {"error": "không có API này"}))
        else:
            super().do_GET()

    def do_POST(self) -> None:
        path = self._path()
        if path not in ("/api/step", "/api/solve"):
            self._send((404, {"error": "không có API này"}))
            return
        try:
            body = self._read_body()
        except ValueError as exc:
            self._send((400, {"error": f"JSON không hợp lệ: {exc}"}))
            return
        try:
            if path == "/api/step":
                response = api.step_level(self.server.levels, body)
            else:
                response = api.solve_level(
                    self.server.levels, body, self.server.algorithms, self.server.timeout_s
                )
        except Exception as exc:  # lỗi bất ngờ: báo cho GUI thay vì đóng kết nối
            response = (500, {"error": f"{type(exc).__name__}: {exc}"})
        self._send(response)

    def end_headers(self) -> None:
        # Không cache: sửa JS/CSS rồi tải lại trang là thấy ngay
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def _path(self) -> str:
        return self.path.split("?", 1)[0]

    def _read_body(self) -> Any:
        length = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(length) if length else b""
        return json.loads(raw.decode("utf-8") or "null")

    def _send(self, response: Tuple[int, Mapping[str, Any]]) -> None:
        code, data = response
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def make_server(levels, web_dir: Path, port: int = 8000, timeout_s: float = 60.0,
                algorithms=ALGORITHMS) -> BloxorzServer:
    return BloxorzServer(("127.0.0.1", port), levels, web_dir, timeout_s, algorithms)
