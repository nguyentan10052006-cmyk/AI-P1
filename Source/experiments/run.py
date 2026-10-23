"""Script đo thực nghiệm (V23, TV2): chạy solver trên các màn, ghi raw.csv và summary.csv (docs/04).

Cách chạy (trong Source/):
    python -m experiments.run                                     # 5 thuật toán × levels/original, ghi vào experiments/
    python -m experiments.run --levels levels/original/01.json --algorithms bfs,dfs --repeat 5
    python -m experiments.run --algorithms tests.fakes:FakeSolver --levels <thư mục màn thử> --out <thư mục ra>

Cách đo (docs/04 §4):
- Mỗi lần chạy là một tiến trình con riêng (multiprocessing kiểu spawn), có timeout. Hết giờ thì dừng
  tiến trình và ghi status = timeout.
- Đo thời gian `repeat` lần (mặc định 5) bằng perf_counter_ns, gc.collect() trước mỗi lần, KHÔNG bật
  tracemalloc; summary lấy trung vị. Đo bộ nhớ ở một lần chạy riêng: tracemalloc.start() ngay trước
  prepare(), đọc đỉnh ngay sau search(); thời gian của lần đó bị bỏ.
- search_ms chỉ gồm search(); total_ms gồm nạp màn, dựng Problem, prepare() và search().
- Sau khi đo, phát lại path bằng engine và tính lại path_cost bằng Problem.step_cost (ngoài phần đo).
  Không tới đích, hoặc path_cost lệch với solver báo, thì status = invalid.

File ra (trong --out, mặc định experiments/):
- raw.csv: một dòng mỗi lần chạy (kind = time hoặc memory), thêm cột run, kind, path, error.
- summary.csv: một dòng mỗi cặp (màn, thuật toán), đúng cột ở docs/04 §5.
- run_info.json: cấu hình lần chạy và môi trường máy (docs/04 §4: CPU, RAM, hệ điều hành, Python, commit).
Mặc định không ghi đè file đã có; dùng --force nếu chắc chắn.

status: solved | no_solution | timeout | invalid (docs/04 §2), thêm error khi màn không nạp được hoặc
solver ném lỗi / trả sai kiểu; nội dung lỗi nằm ở cột error của raw.csv.
"""
from __future__ import annotations

import argparse
import csv
import gc
import importlib
import json
import multiprocessing as mp
import os
import platform
import statistics
import subprocess
import sys
import time
import tracemalloc
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence

SOURCE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_LEVELS = SOURCE_DIR / "levels" / "original"
DEFAULT_OUT = SOURCE_DIR / "experiments"
DEFAULT_ALGORITHMS = ("bfs", "dfs", "ucs", "astar", "astar_m")

SOLVED, NO_SOLUTION, TIMEOUT, INVALID, ERROR = "solved", "no_solution", "timeout", "invalid", "error"

# docs/04 §5, đúng thứ tự
SUMMARY_COLUMNS = ["level", "passcode", "group", "algorithm", "heuristic", "status", "steps", "path_cost",
                   "expanded", "generated", "max_frontier", "visited", "peak_mem_kb", "search_ms",
                   "total_ms", "commit"]
RAW_COLUMNS = SUMMARY_COLUMNS[:5] + ["run", "kind"] + SUMMARY_COLUMNS[5:] + ["path", "error"]
COUNTERS = ("expanded", "generated", "max_frontier", "visited")
HEURISTIC = {"astar": "h_P", "astar_m": "h_M"}  # bien-ban #15

_CONTEXT = mp.get_context("spawn")


# ---------- trong tiến trình con ----------

def resolve_solver(spec: str):
    """'bfs' → ALGORITHMS['bfs']; 'goi.module:TenLop' → lớp đó (dùng cho solver giả khi kiểm thử)."""
    if ":" in spec:
        module, _, name = spec.partition(":")
        return getattr(importlib.import_module(module), name)
    from solvers import ALGORITHMS
    if spec not in ALGORITHMS:
        raise KeyError(f"thuật toán {spec!r} không có trong ALGORITHMS ({', '.join(ALGORITHMS)})")
    return ALGORITHMS[spec]


def action_text(action) -> str:
    """Action → 'U', 'D', 'L', 'R'; khi đã tách thêm số khối con: 'U1' … 'R2' (docs/01 §4)."""
    letter = action.dir.name[0]
    return letter if action.cube is None else f"{letter}{action.cube + 1}"


def measure_once(level_path: str, level_id: str, spec: str, measure_memory: bool) -> Dict[str, Any]:
    """Một lần đo theo khung ở docs/04 §4. Chạy trong tiến trình con."""
    from bloxorz.level import load_level
    from bloxorz.problem import Problem
    from solvers.base import NO_SOLUTION as SR_NO_SOLUTION, SOLVED as SR_SOLVED, SearchResult

    solver_cls = resolve_solver(spec)
    gc.collect()
    t0 = time.perf_counter_ns()
    problem = Problem(load_level(Path(level_path), level_id))
    solver = solver_cls()
    if measure_memory:
        tracemalloc.start()
    solver.prepare(problem)
    t1 = time.perf_counter_ns()
    result = solver.search(problem)
    t2 = time.perf_counter_ns()
    peak_kb = None
    if measure_memory:
        peak_kb = tracemalloc.get_traced_memory()[1] / 1024
        tracemalloc.stop()

    if not isinstance(result, SearchResult):
        return {"status": ERROR, "error": f"search() trả về {type(result).__name__}, không phải SearchResult"}
    out: Dict[str, Any] = {name: getattr(result, name) for name in COUNTERS}
    out.update(search_ms=(t2 - t1) / 1e6, total_ms=(t2 - t0) / 1e6, peak_kb=peak_kb,
               path=" ".join(action_text(a) for a in result.path), error="")

    if result.status == SR_NO_SOLUTION and not result.path:
        out.update(status=NO_SOLUTION, steps=None, path_cost=None)
        return out
    if result.status != SR_SOLVED:
        out.update(status=INVALID, steps=None, path_cost=None,
                   error=f"status {result.status!r} với path dài {len(result.path)}")
        return out

    # Phát lại để kiểm tra, ngoài phần đo (docs/04 §4)
    state, cost = problem.initial_state(), 0.0
    for index, action in enumerate(result.path, start=1):
        nxt = problem.result(state, action)
        if nxt is None:
            out.update(status=INVALID, steps=len(result.path), path_cost=None,
                       error=f"bước {index} ({action_text(action)}) làm khối rơi")
            return out
        cost += problem.step_cost(state, action, nxt)
        state = nxt
    if not problem.is_goal(state):
        out.update(status=INVALID, steps=len(result.path), path_cost=cost, error="phát lại không tới đích")
    elif abs(cost - result.path_cost) > 1e-9:
        out.update(status=INVALID, steps=len(result.path), path_cost=cost,
                   error=f"solver báo path_cost {result.path_cost}, phát lại ra {cost}")
    else:
        out.update(status=SOLVED, steps=len(result.path), path_cost=cost)
    return out


def _child(conn, level_path: str, level_id: str, spec: str, measure_memory: bool) -> None:
    try:
        conn.send(measure_once(level_path, level_id, spec, measure_memory))
    except BaseException as exc:  # màn lỗi, solver ném lỗi, chưa cài (NotImplementedError)…
        conn.send({"status": ERROR, "error": f"{type(exc).__name__}: {exc}"})
    finally:
        conn.close()


# ---------- trong tiến trình cha ----------

def run_isolated(level_path: Path, level_id: str, spec: str, measure_memory: bool,
                 timeout_s: float) -> Dict[str, Any]:
    """Chạy measure_once trong tiến trình con riêng; quá timeout_s thì dừng và trả status timeout."""
    parent_conn, child_conn = _CONTEXT.Pipe(duplex=False)
    process = _CONTEXT.Process(target=_child, args=(child_conn, str(level_path), level_id, spec, measure_memory),
                               daemon=True)
    process.start()
    child_conn.close()
    try:
        if parent_conn.poll(timeout_s):
            outcome = parent_conn.recv()
        else:
            outcome = {"status": TIMEOUT, "error": f"quá {timeout_s:g} giây, đã dừng tiến trình"}
    except (EOFError, OSError):
        outcome = {"status": ERROR, "error": "tiến trình con dừng bất thường (có thể hết bộ nhớ)"}
    finally:
        if process.is_alive():
            process.terminate()
        process.join(timeout=5)
        parent_conn.close()
    return outcome


def find_levels(paths: Iterable[Path]) -> List[Path]:
    """Mỗi đường dẫn là một file .json hoặc một thư mục (lấy mọi *.json, không đệ quy), giữ thứ tự."""
    found: List[Path] = []
    for path in paths:
        if path.is_dir():
            found.extend(sorted(path.glob("*.json")))
        elif path.suffix == ".json" and path.exists():
            found.append(path)
        else:
            raise FileNotFoundError(f"không có màn chơi tại {path}")
    if not found:
        raise FileNotFoundError("không có file màn nào trong các đường dẫn đã cho")
    return found


def level_info(path: Path) -> Dict[str, Any]:
    """Mã màn, passcode (chuỗi, giữ số 0 ở đầu), nhóm; error nếu bộ nạp màn từ chối file."""
    from bloxorz.level import LevelError, load_level
    info = {"level": path.stem, "passcode": "", "group": "", "error": ""}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        info["passcode"] = str(data.get("passcode", "")) if isinstance(data, dict) else ""
        info["group"] = load_level(path, path.stem).group
    except (OSError, ValueError, LevelError) as exc:
        info["error"] = f"{type(exc).__name__}: {exc}"
    return info


def git_commit(cwd: Path = SOURCE_DIR) -> str:
    """Mã commit ngắn; thêm '-dirty' nếu code chạy khác commit đó: file đã theo dõi bị sửa, hoặc có
    file .py chưa theo dõi trong Source/. File kết quả (CSV, JSON) chưa theo dõi không tính."""
    def git(*args) -> str:
        return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, check=True).stdout.strip()
    try:
        commit = git("rev-parse", "--short", "HEAD")
        dirty = git("status", "--porcelain", "--untracked-files=no") or git(
            "ls-files", "--others", "--exclude-standard", "--", "*.py")
    except (OSError, subprocess.CalledProcessError):
        return ""
    return f"{commit}-dirty" if dirty else commit


def _fmt(value: Any, digits: Optional[int] = None) -> str:
    if value is None or value == "":
        return ""
    if digits is not None:
        return f"{value:.{digits}f}"
    return str(value)


def raw_row(base: Dict[str, Any], run: int, kind: str, outcome: Dict[str, Any]) -> Dict[str, str]:
    timed = kind == "time"
    row = {**base, "run": str(run), "kind": kind, "status": outcome["status"],
           "steps": _fmt(outcome.get("steps")), "path_cost": _fmt(outcome.get("path_cost")),
           "peak_mem_kb": "" if timed else _fmt(outcome.get("peak_kb"), 2),
           "search_ms": _fmt(outcome.get("search_ms"), 4) if timed else "",
           "total_ms": _fmt(outcome.get("total_ms"), 4) if timed else "",
           "path": outcome.get("path", ""), "error": outcome.get("error", "")}
    for name in COUNTERS:
        row[name] = _fmt(outcome.get(name))
    return row


def summarize(base: Dict[str, Any], timed: Sequence[Dict[str, Any]], memory: Optional[Dict[str, Any]],
              warnings: List[str]) -> Dict[str, str]:
    """Gộp các lần đo của một cặp (màn, thuật toán) thành một dòng summary.

    status: có lần error → error; có lần invalid → invalid; có lần timeout → timeout; mọi lần solved
    → solved; mọi lần no_solution → no_solution; lẫn lộn solved/no_solution → error (kèm cảnh báo).
    Chỉ số đếm lấy từ lần đầu (solver tất định); lệch giữa các lần thì cảnh báo.
    Thời gian là trung vị các lần chạy xong (solved, no_solution), 2 chữ số thập phân (docs/04 §4).
    """
    row = {name: "" for name in SUMMARY_COLUMNS}
    row.update({k: base[k] for k in ("level", "passcode", "group", "algorithm", "heuristic", "commit")})
    statuses = {o["status"] for o in timed}
    label = f"{base['level']}/{base['algorithm']}"
    for status in (ERROR, INVALID, TIMEOUT):
        if status in statuses:
            row["status"] = status
            break
    else:
        if statuses in ({SOLVED}, {NO_SOLUTION}):
            row["status"] = statuses.pop()
        else:
            row["status"] = ERROR
            warnings.append(f"{label}: kết quả không nhất quán giữa các lần chạy: {sorted(statuses)}")

    finished = [o for o in timed if o["status"] in (SOLVED, NO_SOLUTION, INVALID)]
    if finished:
        first = finished[0]
        for name in COUNTERS + ("steps", "path_cost"):
            row[name] = _fmt(first.get(name))
            if any(o.get(name) != first.get(name) for o in finished[1:]):
                warnings.append(f"{label}: {name} khác nhau giữa các lần chạy")
    done = [o for o in timed if o["status"] in (SOLVED, NO_SOLUTION)]
    if done and row["status"] in (SOLVED, NO_SOLUTION):
        row["search_ms"] = _fmt(statistics.median(o["search_ms"] for o in done), 2)
        row["total_ms"] = _fmt(statistics.median(o["total_ms"] for o in done), 2)
    if memory is not None and memory.get("peak_kb") is not None and row["status"] in (SOLVED, NO_SOLUTION):
        row["peak_mem_kb"] = _fmt(memory["peak_kb"], 2)
    return row


def machine_info() -> Dict[str, Any]:
    info = {"python": sys.version.split()[0], "implementation": platform.python_implementation(),
            "platform": platform.platform(), "machine": platform.machine(),
            "processor": platform.processor(), "cpu_count": os.cpu_count(), "ram_gb": None}
    try:
        if sys.platform == "win32":
            import ctypes

            class MemoryStatus(ctypes.Structure):
                _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                            ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                            ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                            ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                            ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]
            status = MemoryStatus()
            status.dwLength = ctypes.sizeof(MemoryStatus)
            if ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
                info["ram_gb"] = round(status.ullTotalPhys / 2**30, 1)
        elif hasattr(os, "sysconf"):
            info["ram_gb"] = round(os.sysconf("SC_PAGE_SIZE") * os.sysconf("SC_PHYS_PAGES") / 2**30, 1)
    except (OSError, ValueError, AttributeError):
        pass
    return info


def run_experiment(level_paths: Sequence[Path], algorithms: Sequence[str], out_dir: Path, repeat: int = 5,
                   timeout_s: float = 60.0, force: bool = False, log=print) -> Dict[str, Any]:
    """Chạy toàn bộ và ghi raw.csv, summary.csv, run_info.json vào out_dir. Trả về run_info."""
    if repeat < 1:
        raise ValueError("repeat phải >= 1")
    if timeout_s <= 0:
        raise ValueError("timeout phải > 0")
    out_dir.mkdir(parents=True, exist_ok=True)
    targets = {name: out_dir / name for name in ("raw.csv", "summary.csv", "run_info.json")}
    existing = [str(p) for p in targets.values() if p.exists()]
    if existing and not force:
        raise FileExistsError("không ghi đè file kết quả đã có (dùng --force nếu chắc chắn): " + ", ".join(existing))

    levels = find_levels(level_paths)
    commit = git_commit()
    started = datetime.now(timezone.utc)
    warnings: List[str] = []
    summary_rows: List[Dict[str, str]] = []
    partial = out_dir / "raw.csv.partial"   # ghi dần; xong mới đổi tên, để lần chạy hỏng không đè kết quả cũ

    with partial.open("w", newline="", encoding="utf-8") as raw_file:
        raw_writer = csv.DictWriter(raw_file, fieldnames=RAW_COLUMNS)
        raw_writer.writeheader()
        for path in levels:
            info = level_info(path)
            for spec in algorithms:
                base = {"level": info["level"], "passcode": info["passcode"], "group": info["group"],
                        "algorithm": spec, "heuristic": HEURISTIC.get(spec, ""), "commit": commit}
                if info["error"]:   # màn không nạp được: không chạy, ghi một dòng error
                    failed = {"status": ERROR, "error": info["error"]}
                    raw_writer.writerow(raw_row(base, 1, "time", failed))
                    summary_rows.append(summarize(base, [failed], None, warnings))
                    log(f"{info['level']:>8} {spec:<12} error   {info['error']}")
                    continue
                timed = []
                for run in range(1, repeat + 1):
                    outcome = run_isolated(path, info["level"], spec, False, timeout_s)
                    timed.append(outcome)
                    raw_writer.writerow(raw_row(base, run, "time", outcome))
                    if outcome["status"] in (TIMEOUT, ERROR):
                        break   # các lần sau cũng sẽ như vậy; không tốn thêm timeout_s mỗi lần
                memory = None
                if timed[-1]["status"] in (SOLVED, NO_SOLUTION):
                    memory = run_isolated(path, info["level"], spec, True, timeout_s)
                    raw_writer.writerow(raw_row(base, repeat + 1, "memory", memory))
                raw_file.flush()
                row = summarize(base, timed, memory, warnings)
                summary_rows.append(row)
                log(f"{row['level']:>8} {spec:<12} {row['status']:<11} steps={row['steps'] or '-':>4} "
                    f"expanded={row['expanded'] or '-':>6} search_ms={row['search_ms'] or '-'}")

    with (out_dir / "summary.csv.partial").open("w", newline="", encoding="utf-8") as summary_file:
        writer = csv.DictWriter(summary_file, fieldnames=SUMMARY_COLUMNS)
        writer.writeheader()
        writer.writerows(summary_rows)
    run_info = {
        "started_utc": started.isoformat(timespec="seconds"),
        "finished_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "commit": commit, "repeat": repeat, "timeout_s": timeout_s,
        "levels": [str(p) for p in levels], "algorithms": list(algorithms),
        "machine": machine_info(), "warnings": warnings,
        "method": "docs/04 §4: tiến trình spawn riêng mỗi lần chạy; thời gian = trung vị perf_counter_ns, "
                  "không bật tracemalloc; bộ nhớ = đỉnh tracemalloc ở một lần chạy riêng",
    }
    (out_dir / "run_info.json.partial").write_text(json.dumps(run_info, ensure_ascii=False, indent=2) + "\n",
                                                  encoding="utf-8")
    for name, target in targets.items():
        os.replace(out_dir / f"{name}.partial", target)
    for message in warnings:
        log(f"CẢNH BÁO: {message}")
    return run_info


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--levels", type=Path, nargs="+", default=[DEFAULT_LEVELS],
                        help="file .json hoặc thư mục màn (mặc định levels/original)")
    parser.add_argument("--algorithms", default=",".join(DEFAULT_ALGORITHMS),
                        help="tên trong ALGORITHMS hoặc goi.module:TenLop, cách nhau bởi dấu phẩy")
    parser.add_argument("--repeat", type=int, default=5, help="số lần đo thời gian (mặc định 5)")
    parser.add_argument("--timeout", type=float, default=60.0, help="giây mỗi lần chạy (mặc định 60)")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT, help="thư mục ghi kết quả (mặc định experiments/)")
    parser.add_argument("--force", action="store_true", help="ghi đè raw.csv, summary.csv, run_info.json đã có")
    args = parser.parse_args(argv)
    for stream in (sys.stdout, sys.stderr):  # console Windows mặc định cp1252, không in được tiếng Việt
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")

    algorithms = [a.strip() for a in args.algorithms.split(",") if a.strip()]
    try:
        info = run_experiment(args.levels, algorithms, args.out, args.repeat, args.timeout, args.force)
    except (FileExistsError, FileNotFoundError, ValueError) as exc:
        print(f"LỖI: {exc}", file=sys.stderr)
        return 1
    print(f"Đã ghi {args.out / 'raw.csv'}, {args.out / 'summary.csv'}, {args.out / 'run_info.json'}"
          f" (commit {info['commit'] or 'không rõ'})")
    return 0


if __name__ == "__main__":   # bắt buộc trên Windows khi dùng multiprocessing
    sys.exit(main())
