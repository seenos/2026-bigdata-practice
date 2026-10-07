#!/usr/bin/env python3
"""Week 6 · Task 2 — Lower the threshold until your machine says no.

Textbook §6.1, §6.2.

Support is a knob, and turning it down is how you find the interesting rules.
It is also how you run out of memory, and where that happens is a fact about
your laptop rather than about the algorithm.

    python3 task2_explosion.py --supports 400,200,100,50,25
    python3 task2_explosion.py --supports 12,6            # careful

Lower the threshold until something gives. Write down where and what.
"""
import argparse, json, os, platform, time, tracemalloc
from datetime import datetime, timezone
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")


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
    p.add_argument("--supports", default="400,200,100,50,25")
    a = p.parse_args()
    os.makedirs(OUT, exist_ok=True)

    import bench
    from task3_pcy import PlainApriori
    baskets = bench.build()
    singleton_counts = Counter(i for basket in baskets for i in basket)
    path = os.path.join(OUT, "explosion.json")
    prior = json.load(open(path, encoding="utf-8")) if os.path.exists(path) else {"runs": []}
    environment = machine()
    prior["machine"] = environment
    prior["protocol"] = {"seed": bench.SEED, "baskets": len(baskets),
                         "items": bench.ITEMS, "time_stop_seconds": 60,
                         "memory_stop_bytes": 1000000000,
                         "note": "Stop expansion after a completed condition reaches either criterion. tracemalloc includes algorithm allocations, excludes prebuilt baskets. Single run per support."}

    rows = []
    for support in [int(x) for x in a.supports.split(",")]:
        if support < 1:
            raise ValueError("support must be positive")
        print(f"Starting support={support}", flush=True)
        algo = PlainApriori(support)
        tracemalloc.start()
        t0 = time.perf_counter()
        pairs = algo.run(baskets)
        elapsed = time.perf_counter() - t0
        _, peak_bytes = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        row = {"support": support, "frequent_pairs": len(pairs),
               "peak_counters": algo.peak_counters, "seconds": elapsed,
               "peak_bytes": peak_bytes,
               "frequent_items": sum(c >= support for c in singleton_counts.values()),
               "environment": environment, "status": "completed"}
        rows.append(row)
        prior["runs"].append(row)
        tmp = path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(prior, f, indent=2)
        os.replace(tmp, path)
        print(f"  support {support:>5}   pairs {len(pairs):>7,}   "
              f"counters {algo.peak_counters:>10,}   "
              f"{elapsed:>7.2f}s   {peak_bytes / 1e6:>8.1f} MB")
        del pairs
        if elapsed >= 60 or peak_bytes >= 1000000000:
            print("Stopping expansion: recorded time/memory criterion reached.", flush=True)
            break

    path = os.path.join(OUT, "explosion.json")
    print(f"\n  -> out/explosion.json  ({len(prior['runs'])} run(s))")
    print("  Keep halving the support until it is unbearable. Record where.")


if __name__ == "__main__":
    main()
