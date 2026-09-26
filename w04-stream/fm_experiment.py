"""Compare FM combining rules on identical hash maxima; save raw evidence."""
import json
from pathlib import Path
import random
import statistics

from task1_sketches import _fm_maxima, _fm_combine, reservoir_sample, flajolet_martin


def main():
    rows = []
    for n in (100, 2000, 20000):
        for seed in (246, 247, 248, 249, 250):
            maxima = _fm_maxima((f"k{i}" for i in range(n)), 64, seed)
            estimates = [2 ** r for r in maxima]
            rules = {"mean": statistics.mean(estimates),
                     "median": statistics.median(estimates),
                     "mean_of_group_medians": _fm_combine(maxima)}
            rows.append({"true_distinct": n, "seed": seed, "estimates": rules,
                         "ratios": {k: v / n for k, v in rules.items()},
                         "maxima": maxima})
    rng = random.Random(246)
    fixture = [f"k{rng.randrange(20000)}" for _ in range(120000)]
    maxima = _fm_maxima(iter(fixture), 64, 246)
    values = [2 ** r for r in maxima]
    official = {"true_distinct": len(set(fixture)),
                "mean": statistics.mean(values),
                "median": statistics.median(values),
                "mean_of_group_medians": _fm_combine(maxima)}
    assert flajolet_martin(iter(())) == 0
    assert flajolet_martin(iter(["same"] * 100)) == flajolet_martin(iter(["same"]))
    assert reservoir_sample(iter(range(3)), 5) == [0, 1, 2]
    assert reservoir_sample(iter(range(3)), 0) == []
    assert len(set(reservoir_sample(iter(range(100)), 10))) == 10
    out = Path(__file__).parent / "out" / "evidence"
    out.mkdir(parents=True, exist_ok=True)
    data = {"n_hashes": 64, "group_size": 8, "rows": rows,
            "official_fixture": official,
            "note": "Finite seed/size checks, not a universal factor-of-two guarantee."}
    (out / "fm_comparison.json").write_text(json.dumps(data, indent=2), encoding="utf-8")
    print("Official fixture:", official)
    for rule in rows[0]["ratios"]:
        ratios = [r["ratios"][rule] for r in rows]
        print(rule, "ratio range", min(ratios), max(ratios),
              "within factor two", sum(0.5 <= x <= 2 for x in ratios), "/", len(ratios))
    print("Empty, duplicate, and reservoir edge checks passed.")


if __name__ == "__main__":
    main()
