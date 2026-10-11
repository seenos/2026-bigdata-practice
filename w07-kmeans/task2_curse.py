"""Measure sampled pairwise distances; save each completed condition."""
import argparse
from datetime import datetime, timezone
import json
import math
from pathlib import Path
import platform
import random
import time

ROOT = Path(__file__).parent


def machine():
    result = dict(platform=platform.platform(), python=platform.python_version(),
                  processor=platform.processor() or platform.machine(),
                  background='Codex active; other applications not controlled.')
    if platform.system() == 'Windows':
        import ctypes
        import winreg
        class Memory(ctypes.Structure):
            _fields_ = [('length',ctypes.c_ulong),('load',ctypes.c_ulong)] + [
                (name,ctypes.c_ulonglong) for name in
                ('total','available','page_total','page_available','virtual_total',
                 'virtual_available','extended')]
        mem=Memory(); mem.length=ctypes.sizeof(mem)
        if ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(mem)):
            result['ram_bytes']=mem.total
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                            r'HARDWARE\DESCRIPTION\System\CentralProcessor\0') as key:
            result['cpu']=winreg.QueryValueEx(key,'ProcessorNameString')[0].strip()
    return result


def euclid(a,b):
    return math.sqrt(sum((x-y)**2 for x,y in zip(a,b)))


def sample_distances(n,dim,pairs,seed=246):
    # Preserve the instructor's sampling: self-pairs skipped, other pairs may repeat.
    rng=random.Random(seed+dim)
    pts=[tuple(rng.random() for _ in range(dim)) for _ in range(n)]
    ds=[]
    for _ in range(pairs):
        i,j=rng.randrange(n),rng.randrange(n)
        if i != j:
            ds.append(euclid(pts[i],pts[j]))
    return ds


def statistics(ds):
    lo,hi=min(ds),max(ds)
    mean=sum(ds)/len(ds)
    sd=math.sqrt(sum((d-mean)**2 for d in ds)/len(ds))
    return dict(min=lo,max=hi,mean=mean,stdev=sd,
                contrast=(hi-lo)/lo if lo else None,relative_stdev=sd/mean if mean else None)


def all_pairs_prefixes(dim,seed,counts=(100,300,1000)):
    # Nested datasets make exact extrema nondecreasing in contrast as n grows.
    rng=random.Random(seed+dim)
    pts=[tuple(rng.random() for _ in range(dim)) for _ in range(max(counts))]
    lo=float('inf'); hi=0.; rows=[]; start=time.perf_counter()
    for j in range(1,len(pts)):
        for i in range(j):
            d=euclid(pts[i],pts[j]); lo=min(lo,d); hi=max(hi,d)
        n=j+1
        if n in counts:
            rows.append(dict(dim=dim,points=n,seed=seed,pairs=n*(n-1)//2,
                             min=lo,max=hi,contrast=(hi-lo)/lo,
                             cumulative_seconds=time.perf_counter()-start))
    return rows


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--dims',default='2,5,10,20,50,100,200,500,1000')
    p.add_argument('--points',type=int,default=1000)
    p.add_argument('--pairs',type=int,default=20000)
    p.add_argument('--repeats',type=int,default=3)
    p.add_argument('--seed',type=int,default=246)
    p.add_argument('--point-counts',default='100,300,3000')
    p.add_argument('--fixed-dim',type=int,default=50)
    p.add_argument('--all-pairs',action='store_true')
    a=p.parse_args()
    dims=[int(x) for x in a.dims.split(',')]
    ns=[int(x) for x in a.point_counts.split(',') if x]
    if min(dims+[a.fixed_dim]) < 1 or min(ns+[a.points]) < 2 or min(a.pairs,a.repeats)<1:
        p.error('dimensions >= 1, points >= 2, pairs and repeats >= 1 required')
    path=ROOT/'out/curse.json'; path.parent.mkdir(parents=True,exist_ok=True)
    data=json.loads(path.read_text(encoding='utf-8')) if path.exists() else dict(runs=[])
    env=machine(); data['machine']=env
    batch=datetime.now(timezone.utc).isoformat()
    def save():
        temp=path.with_suffix('.tmp'); temp.write_text(json.dumps(data,indent=2),encoding='utf-8'); temp.replace(path)
    configs=[(d,a.points,'dimension') for d in dims]
    configs.extend((a.fixed_dim,n,'point_count') for n in ns if (a.fixed_dim,n) not in [(d,a.points) for d in dims])
    for repeat in range(a.repeats):
        seed=a.seed+repeat
        for dim,n,label in configs:
            start=time.perf_counter(); ds=sample_distances(n,dim,a.pairs,seed)
            elapsed=time.perf_counter()-start
            if not ds:
                raise ValueError('no non-self sampled pairs; increase --pairs')
            row=dict(dim=dim,points=n,pairs=len(ds),pair_attempts=a.pairs,
                     seed=seed,repeat=repeat+1,label=label,batch=batch,
                     seconds=elapsed,environment=env,**statistics(ds))
            data['runs'].append(row); save()
            print(f'd={dim} n={n} seed={seed}: contrast={row["contrast"]:.4f}, rel.sd={row["relative_stdev"]:.4f}, {elapsed:.2f}s',flush=True)
    if a.all_pairs:
        evidence=dict(batch=batch,machine=env,dim=a.fixed_dim,
                      note='All unordered distinct pairs of nested point prefixes; timings cumulative, includes pair calculations but excludes point generation.',runs=[])
        for repeat in range(a.repeats):
            evidence['runs'].extend(all_pairs_prefixes(a.fixed_dim,a.seed+repeat))
            (ROOT/'out/evidence').mkdir(exist_ok=True)
            (ROOT/'out/evidence/all_pairs.json').write_text(json.dumps(evidence,indent=2),encoding='utf-8')
            print(f'Exact all-pairs supplement seed {a.seed+repeat} complete.',flush=True)


if __name__=='__main__':
    main()
