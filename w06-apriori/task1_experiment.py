"""Reproducible Task 1 observations and independent small-data checks."""
import json
from pathlib import Path
from collections import Counter
from itertools import combinations
import random
import bench
from task1_apriori import frequent_singletons, frequent_pairs, association_rules, BASKETS


def main():
    rng = random.Random(246)
    for _ in range(40):
        baskets = [[rng.randrange(8) for _ in range(rng.randrange(10))] for _ in range(20)]
        support = rng.randrange(1, 10)
        truth = Counter(frozenset(p) for b in baskets for p in combinations(set(b), 2))
        assert frequent_pairs(baskets, support) == {p:c for p,c in truth.items() if c>=support}
    assert frequent_pairs([], 1) == {}
    assert association_rules([], 1, 0) == []
    asym = [{'X','Y'}, {'X','Y'}, {'X'}, {'X'}]
    rules = association_rules(asym, 2, 0)
    assert {(a,b):c for a,b,c,l in rules} == {('X','Y'):.5, ('Y','X'):1.0}
    baskets = bench.build()
    singles = frequent_singletons(baskets, bench.SUPPORT)
    pairs = frequent_pairs(baskets, bench.SUPPORT)
    counters = frequent_pairs.peak_counters
    large_rules = association_rules(baskets, bench.SUPPORT, 0)
    data = dict(seed=bench.SEED, support=bench.SUPPORT, baskets=len(baskets),
                items=bench.ITEMS, all_possible_pairs=bench.ITEMS*(bench.ITEMS-1)//2,
                frequent_items=len(singles), possible_survivor_pairs=len(singles)*(len(singles)-1)//2,
                actual_pair_counters=counters, frequent_pairs=len(pairs),
                small_rules=association_rules(BASKETS,3,.75), asymmetric_rules=rules,
                highest_confidence_rules=large_rules[:10],
                top_rule_counts={str(x):singles[x] for x in large_rules[0][:2]},
                top_pair_count=pairs[frozenset(large_rules[0][:2])])
    out=Path(__file__).parent/'out/evidence/task1.json'
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(data,indent=2),encoding='utf-8')
    print(json.dumps(data,indent=2))
    print('40 independent pair-count checks and edge cases passed.')


if __name__ == '__main__':
    main()
