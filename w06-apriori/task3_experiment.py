"""Measure full allocation peaks, including PCY buckets and returned results."""
import json
from pathlib import Path
import random
import time
import tracemalloc
import bench
from task3_pcy import PlainApriori, YourAlgorithm


def measure(algo, baskets):
    tracemalloc.start()
    start = time.perf_counter()
    result = algo.run(baskets)
    seconds = time.perf_counter()-start
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return result, dict(seconds=seconds, peak_bytes=peak,
                        peak_counters=algo.peak_counters, answers=len(result),
                        **{k:getattr(algo,k) for k in ('buckets','counted_pairs','bucket_array_bytes','bitmap_bytes','frequent_buckets') if hasattr(algo,k)})


def main():
    rng=random.Random(246)
    for _ in range(30):
        baskets=[set(rng.sample(range(15),rng.randrange(1,9))) for _ in range(30)]
        support=rng.randrange(1,15)
        expected=PlainApriori(support).run(baskets)
        for buckets in (1,16,128):
            assert YourAlgorithm(support,buckets).run(baskets)==expected
    print('90 independent dictionary comparisons passed.',flush=True)
    baskets=bench.build()
    path=Path(__file__).parent/'out/evidence/pcy_memory.json'
    path.parent.mkdir(parents=True,exist_ok=True)
    data=dict(seed=bench.SEED,support=50,rows=[],
              note='Single run per configuration. tracemalloc includes solver allocations and output; excludes prebuilt input and preexisting reference result. Same fixed-seed input prefix. No concurrent benchmark.')
    for n in (200,1000,5000,20000):
        docs=baskets[:n]
        reference,base=measure(PlainApriori(50),docs)
        for bucket_count in ((1<<20,1<<14) if n==20000 else (1<<20,)):
            print(f'Start PCY n={n}, buckets={bucket_count}',flush=True)
            result,mine=measure(YourAlgorithm(50,bucket_count),docs)
            assert result==reference, 'Pair counts differ'
            data['rows'].append(dict(baskets=n,baseline=base,pcy=mine,exact_match=True))
            path.write_text(json.dumps(data,indent=2),encoding='utf-8')
            print(f'n={n} buckets={bucket_count}: base={base["peak_bytes"]} bytes; PCY={mine["peak_bytes"]} bytes; pairs={len(result)}; counters={mine["peak_counters"]}',flush=True)
            del result
        del reference


if __name__=='__main__':
    main()
