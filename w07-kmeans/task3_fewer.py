#!/usr/bin/env python3
"""Week 7 · Task 3 — The same clustering, with far fewer distances.

Textbook §7.3, and §7.1.3 for why distance is the expensive part.

`NaiveKMeans` does what the definition says: every iteration, compare every
point with every centroid. That is n x k distance computations per pass, and on
a real dataset the distance computation is almost the entire cost.

Most of that work is wasted. After the first couple of iterations, most points
do not change cluster, and most centroids barely move. The triangle inequality
lets you prove a point cannot have changed cluster **without measuring it**.

    python3 bench.py
    python3 bench.py --yours

Correctness first: your final SSE must match the baseline's. Fewer distances
with a worse clustering is not an improvement, it is a different algorithm.
"""


class NaiveKMeans:
    """Every point against every centroid, every iteration."""

    def __init__(self, k, max_iter=50):
        self.k, self.max_iter = k, max_iter

    def run(self, points, initial_centroids, distance):
        centroids = list(initial_centroids)
        labels = [None] * len(points)
        for self.iterations in range(1, self.max_iter + 1):
            changed = False
            for i, p in enumerate(points):
                best, bi = None, 0
                for j, c in enumerate(centroids):
                    d = distance(p, c)
                    if best is None or d < best - 1e-12:
                        best, bi = d, j
                if labels[i] != bi:
                    labels[i] = bi
                    changed = True
            centroids = _means(points, labels, self.k, centroids)
            if not changed:
                break
        return labels, centroids


def _means(points, labels, k, previous):
    out = []
    for j in range(k):
        group = [p for p, l in zip(points, labels) if l == j]
        if group:
            out.append(tuple(sum(v) / len(group) for v in zip(*group)))
        else:
            out.append(previous[j])
    return out


class YourKMeans:
    """Your k-means.

        __init__(k, max_iter=50)
        run(points, initial_centroids, distance) -> (labels, centroids)

    Same starting centroids, same `distance` function - which is counted. That
    counter is your score.

    The idea, from §7.3 and the triangle inequality:

        if a point is much closer to its current centroid than that centroid
        moved, and than any other centroid could have come, then it cannot have
        changed cluster, and you do not have to measure anything

    Keeping enough bookkeeping to make that test cheap, without keeping so much
    that the bookkeeping costs more than the distances, is the task.

    You may call `distance` on two centroids, and those calls are counted too -
    which is the correct accounting, since that is real work. There are k of
    them and n points, and k is much smaller than n. That asymmetry is the
    whole opening.
    """

    def __init__(self, k, max_iter=50):
        if k < 1 or max_iter < 1:
            raise ValueError("k and max_iter must be positive")
        self.k, self.max_iter = k, max_iter

    def run(self, points, initial_centroids, distance):
        if len(initial_centroids) != self.k or not points:
            raise ValueError("require nonempty points and k initial centroids")
        centroids = list(initial_centroids)
        n = len(points)
        labels = [None]*n
        upper = [float('inf')]*n
        lower = [0.0]*n
        separation = [0.0]*self.k
        self.history = []
        self.distance_counts = dict(point=0, movement=0, separation=0)
        self.pruning = dict(lower=0, separation=0, both=0, after_tightening=0,
                            full_scans=0)

        def measure(a,b,kind):
            self.distance_counts[kind] += 1
            return distance(a,b)

        def safe_bound(i):
            # Strict margin protects baseline's sequential 1e-12 tie rule,
            # including chains of nearly tied centers and float roundoff.
            margin = (self.k+2)*1e-12 + 1e-10*max(1.0,upper[i])
            lo_ok = upper[i]+margin < lower[i]
            sep_ok = upper[i]+margin < separation[labels[i]]
            if lo_ok or sep_ok:
                self.pruning['lower' if lo_ok else 'separation'] += 1
                self.pruning['both'] += int(lo_ok and sep_ok)
                return True
            return False

        for self.iterations in range(1,self.max_iter+1):
            before = sum(self.distance_counts.values())
            changed = False
            skipped = 0
            for i,p in enumerate(points):
                old = labels[i]
                if old is not None and safe_bound(i):
                    skipped += 1
                    continue
                own = None
                if old is not None:
                    own = measure(p,centroids[old],'point')
                    upper[i] = own
                    if safe_bound(i):
                        self.pruning['after_tightening'] += 1
                        skipped += 1
                        continue
                self.pruning['full_scans'] += 1
                ds=[]
                best,bi=None,0
                for j,c in enumerate(centroids):
                    d = own if j == old and own is not None else measure(p,c,'point')
                    ds.append(d)
                    if best is None or d < best-1e-12:
                        best,bi=d,j
                labels[i]=bi
                upper[i]=ds[bi]
                lower[i]=min((d for j,d in enumerate(ds) if j != bi),default=float('inf'))
                changed |= old != bi
            updated = _means(points,labels,self.k,centroids)
            if changed and self.iterations < self.max_iter:
                moves=[measure(a,b,'movement') for a,b in zip(centroids,updated)]
                max_move=max(moves)
                for i,l in enumerate(labels):
                    upper[i] += moves[l]
                    lower[i] = max(0.0,lower[i]-max_move)
                separation=[float('inf')]*self.k
                for a in range(self.k):
                    for b in range(a+1,self.k):
                        half=measure(updated[a],updated[b],'separation')/2
                        separation[a]=min(separation[a],half)
                        separation[b]=min(separation[b],half)
            centroids=updated
            self.history.append(dict(iteration=self.iterations,skipped_points=skipped,
                                     distances=sum(self.distance_counts.values())-before,
                                     changed=changed))
            if not changed:
                break
        return labels,centroids
