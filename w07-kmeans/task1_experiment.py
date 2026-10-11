"""Record initialisation comparisons and independent edge-case checks."""
import json
from pathlib import Path
import platform
from statistics import mean
from task1_kmeans import BLOBS, assign, update, kmeans


def recovered(labels):
    groups = {frozenset(i for i,l in enumerate(labels) if l == j)
              for j in set(labels)}
    return groups == {frozenset(range(0,3)),frozenset(range(3,6)),frozenset(range(6,9))}


def main():
    assert assign([(0,0)], [(-1,0),(1,0)]) == [0]
    assert update([(0.,),(10.,)], [0,0], 2) == [(5.,),(0.,)]
    labels,cents,sse = kmeans([(1.,1.)]*5,3,init='++')
    assert sse == 0 and len(cents) == 3 and set(labels) == {0}
    kmeans(BLOBS,3,max_iter=1)
    assert kmeans.iterations == 1 and not kmeans.converged
    rows=[]
    for init in ('random','++'):
        for seed in range(40):
            labels,cents,sse = kmeans(BLOBS,3,init=init,seed=seed)
            history=list(kmeans.sse_history)
            assert all(b <= a+1e-9 for a,b in zip(history,history[1:]))
            assert kmeans.converged
            rows.append(dict(init=init,seed=seed,labels=labels,centroids=cents,
                             sse=sse,recovered=recovered(labels),
                             iterations=kmeans.iterations,converged=kmeans.converged,
                             initialization_distances=kmeans.initialization_distances,
                             sse_history=history))
    summary={}
    for init in ('random','++'):
        subset=[r for r in rows if r['init']==init]
        ss=[r['sse'] for r in subset]
        summary[init]=dict(successes=sum(r['recovered'] for r in subset),runs=40,
                           mean_sse=mean(ss),min_sse=min(ss),max_sse=max(ss),
                           mean_iterations=mean(r['iterations'] for r in subset))
    # k comparison is descriptive: these are best runs observed, not proven optima.
    k_rows=[]
    for k in range(1,10):
        values=[kmeans(BLOBS,k,init='++',seed=s)[2] for s in range(40)]
        k_rows.append(dict(k=k,best_observed_sse=min(values)))
    path=Path(__file__).parent/'out/evidence/task1.json'
    path.parent.mkdir(parents=True,exist_ok=True)
    data=dict(machine=dict(platform=platform.platform(),python=platform.python_version()),
              success_definition='Exact recovery of the three known index groups; label names ignored.',
              empty_cluster_policy='Farthest point from the nearest occupied updated center; first input index breaks ties.',
              independent_checks=['assignment tie','empty cluster','duplicate coordinates','iteration cap','nonincreasing SSE'],
              summary=summary,runs=rows,k_comparison=k_rows)
    path.write_text(json.dumps(data,indent=2),encoding='utf-8')
    print(json.dumps(summary,indent=2))
    print('Saved 80 runs, k comparison, and edge-case checks.')


if __name__=='__main__':
    main()
