"""Check exact assignments and record distance accounting independently."""
import json
from pathlib import Path
import random
import time
import bench
from task2_curse import machine
from task3_fewer import NaiveKMeans, YourKMeans


def compare(points,initial,max_iter=50):
    k=len(initial)
    d1,d2=bench.Distance(),bench.Distance()
    base,mine=NaiveKMeans(k,max_iter),YourKMeans(k,max_iter)
    t=time.perf_counter(); a,c1=base.run(points,initial,d1); t1=time.perf_counter()-t
    t=time.perf_counter(); b,c2=mine.run(points,initial,d2); t2=time.perf_counter()-t
    assert a==b, 'Assignments differ'
    assert c1==c2, 'Centroids differ'
    assert base.iterations==mine.iterations
    assert sum(mine.distance_counts.values())==d2.calls
    s1,s2=bench.sse(points,a,c1),bench.sse(points,b,c2)
    assert s1==s2
    return dict(points=len(points),dim=len(points[0]),k=k,max_iter=max_iter,
                exact_labels=True,exact_centroids=True,iterations=mine.iterations,
                baseline=dict(calls=d1.calls,sse=s1,seconds=t1),
                yours=dict(calls=d2.calls,sse=s2,seconds=t2),
                cut=1-d2.calls/d1.calls,distance_counts=mine.distance_counts,
                pruning=mine.pruning,history=mine.history,
                first_iteration_fraction=mine.history[0]['distances']/d2.calls)


def main():
    rng=random.Random(246); checked=0
    for dim in (1,2,5):
        for k in (1,2,5):
            for cap in (1,2,50):
                for _ in range(4):
                    points=[tuple(rng.randrange(-5,6) for _ in range(dim)) for _ in range(40)]
                    compare(points,rng.sample(points,k),cap); checked += 1
    # Duplicate centers, empty clusters, exact ties and tolerance chains.
    special=[([(0.,),(0.,),(10.,)],[(0.,),(0.,),(0.,)]),
             ([(0.,),(-1.,),(1.,)],[(-1.,),(1.,)]),
             ([(0.,)]*10,[(0.,)]*3),
             ([(0.,),(1.,),(2.,)],[ (1.+1.5e-12,), (1.+.75e-12,), (1.,)]),
             ([(1e10,),(1e10+1.,),(1e10+2.,)],[(1e10,),(1e10+2.,)])]
    for points,initial in special:
        compare(points,initial); checked += 1
    print(f'{checked} independent small comparisons passed.',flush=True)
    points,initial=bench.build()
    result=compare(points,initial)
    result.update(seed=bench.SEED,machine=machine(),small_cases=checked,
                  note='One timing per solver, input generated before timer. An official benchmark ran concurrently during part of this measurement; timings are not used for speedup claims. Distance calls include point-center, center movements, and center-center separation. First-iteration fraction includes bound setup. Exact equality checked for labels and centroids, beyond official SSE tolerance.')
    path=Path(__file__).parent/'out/evidence/task3.json'
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k not in ('history','machine','note')},indent=2),flush=True)


if __name__=='__main__':
    main()
