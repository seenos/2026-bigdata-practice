"""Reproduce small-graph evidence without changing the official verifier."""
import json
from pathlib import Path
from task1_pagerank import pagerank, pagerank_no_teleport, SIMPLE, DEAD_END, SPIDER_TRAP


def main():
    rows = []
    for name, graph in [('simple', SIMPLE), ('dead_end', DEAD_END), ('spider_trap', SPIDER_TRAP)]:
        fixed = pagerank(graph)
        row = dict(graph=name, fixed=fixed, total=sum(fixed.values()),
                   iterations=pagerank.iterations, delta=pagerank.delta,
                   converged=pagerank.converged,
                   broken_100=pagerank_no_teleport(graph))
        row['trace'] = []
        for steps in (0, 1, 2, 3, 10, 100):
            broken = pagerank_no_teleport(graph, steps)
            repaired = pagerank(graph, iterations=steps)
            row['trace'].append(dict(max_iterations=steps, broken=broken,
                                     fixed=repaired, actual_iterations=pagerank.iterations))
        assert row['converged'] and row['delta'] < 1e-10
        assert abs(row['total'] - 1) < 1e-12
        rows.append(row)
    assert pagerank({}) == {} and pagerank.iterations == 0
    assert pagerank({'A': []}) == {'A': 1.0}
    assert pagerank(SIMPLE, beta=0) == dict.fromkeys(SIMPLE, 1/3)
    pagerank(SIMPLE, iterations=1)
    assert pagerank.iterations == 1 and not pagerank.converged
    path = Path(__file__).parent / 'out/evidence/task1.json'
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(dict(beta=.85, tol=1e-10, max_iterations=100,
                                   initial='uniform', results=rows), indent=2), encoding='utf-8')
    for r in rows:
        print(r['graph'], r['iterations'], r['delta'], r['fixed'])
    print('Edge cases and convergence status passed.')


if __name__ == '__main__':
    main()
