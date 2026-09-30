"""Measure PageRank convergence; graph construction is outside the timer."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import platform
import time

import bench
from task1_pagerank import pagerank


def machine():
    info = dict(platform=platform.platform(), processor=platform.processor(),
                python=platform.python_version(),
                background='Codex active; other user applications not controlled.',
                recorded_at=datetime.now(timezone.utc).isoformat())
    if platform.system() == 'Windows':
        import ctypes
        import winreg
        class Memory(ctypes.Structure):
            _fields_ = [('length', ctypes.c_ulong), ('load', ctypes.c_ulong)] + [
                (name, ctypes.c_ulonglong) for name in
                ('total', 'available', 'page_total', 'page_available',
                 'virtual_total', 'virtual_available', 'extended')]
        mem = Memory()
        mem.length = ctypes.sizeof(mem)
        if ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(mem)):
            info['ram_bytes'] = mem.total
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                            r'HARDWARE\DESCRIPTION\System\CentralProcessor\0') as key:
            info['cpu'] = winreg.QueryValueEx(key, 'ProcessorNameString')[0].strip()
    return info


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--betas', default='0.5,0.7,0.85,0.95,0.99')
    p.add_argument('--nodes', type=int, default=1200)
    p.add_argument('--tol', type=float, default=1e-10)
    p.add_argument('--max-iter', type=int, default=500)
    p.add_argument('--repeats', type=int, default=3)
    p.add_argument('--label', default='measurement')
    a = p.parse_args()
    if a.nodes < 40 or a.repeats < 1 or a.max_iter < 1:
        p.error('nodes >= 40, repeats >= 1 and max-iter >= 1 required')
    bench.NODES = a.nodes
    graph = bench.build()
    path = Path(__file__).parent / 'out/convergence.json'
    path.parent.mkdir(parents=True, exist_ok=True)
    data = json.loads(path.read_text(encoding='utf-8')) if path.exists() else {'runs': []}
    environment = machine()
    data['machine'] = environment
    betas = [float(x) for x in a.betas.split(',')]
    # Reverse parameter order every other repeat to reduce order effects.
    for repeat in range(1, a.repeats + 1):
        for beta in (betas if repeat % 2 else list(reversed(betas))):
            t0 = time.perf_counter()
            ranks = pagerank(graph, beta=beta, iterations=a.max_iter, tol=a.tol)
            elapsed = time.perf_counter() - t0
            top = sorted(ranks.items(), key=lambda kv: (-kv[1], kv[0]))[:10]
            row = dict(beta=beta, nodes=len(graph), edges=sum(map(len, graph.values())),
                       tol=a.tol, iterations=pagerank.iterations, seconds=elapsed,
                       delta=pagerank.delta, converged=pagerank.converged,
                       max_iter=a.max_iter, rank_sum=sum(ranks.values()),
                       top10=[k for k, _ in top], top10_scores=dict(top),
                       repeat=repeat, label=a.label, seed=bench.SEED, environment=environment)
            data['runs'].append(row)
            tmp = path.with_suffix('.tmp')
            tmp.write_text(json.dumps(data, indent=2), encoding='utf-8')
            tmp.replace(path)
            print(f"n={len(graph)} beta={beta} tol={a.tol} repeat={repeat}: "
                  f"{pagerank.iterations} iterations, {elapsed:.4f}s, "
                  f"delta={pagerank.delta:.3g}, converged={pagerank.converged}", flush=True)


if __name__ == '__main__':
    main()
