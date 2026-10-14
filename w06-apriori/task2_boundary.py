"""Separate larger-input A2 experiment with an external time/memory stop."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
import threading
import time
import tracemalloc

ROOT=Path(__file__).parent


def worker(a):
    import bench
    from task3_pcy import PlainApriori
    bench.BASKETS=a.baskets  # Runtime configuration only; bench.py is unchanged.
    lock=threading.Lock()
    def emit(value):
        with lock:
            print(json.dumps(value),flush=True)
    emit(dict(event='generating',baskets=a.baskets))
    baskets=bench.build()
    emit(dict(event='generated',baskets=len(baskets)))
    for support in [int(s) for s in a.supports.split(',')]:
        algo=PlainApriori(support)
        tracemalloc.start(); start=time.perf_counter()
        done=threading.Event()
        def progress():
            while not done.wait(1):
                _,peak=tracemalloc.get_traced_memory()
                emit(dict(event='progress',support=support,seconds=time.perf_counter()-start,
                          peak_bytes=peak,observed_pair_counters=algo.peak_counters))
        monitor=threading.Thread(target=progress,daemon=True)
        emit(dict(event='started',support=support)); monitor.start()
        pairs=algo.run(baskets)
        seconds=time.perf_counter()-start; _,peak=tracemalloc.get_traced_memory()
        done.set(); monitor.join(); tracemalloc.stop()
        emit(dict(event='completed',support=support,seconds=seconds,peak_bytes=peak,
                  peak_counters=algo.peak_counters,frequent_pairs=len(pairs)))
        del pairs


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--baskets',type=int,default=100000)
    p.add_argument('--supports',default='2000,1000,500,250,125,62,31,15,7,3,1')
    p.add_argument('--seconds',type=float,default=60)
    p.add_argument('--memory-bytes',type=int,default=1000000000)
    p.add_argument('--worker',action='store_true')
    a=p.parse_args()
    if a.baskets<1 or a.seconds<=0 or a.memory_bytes<1 or any(int(s)<1 for s in a.supports.split(',')):
        p.error('positive configuration required')
    if a.worker:
        worker(a); return
    from task2_explosion import machine
    path=ROOT/'out/evidence/a2_boundary.json'; path.parent.mkdir(parents=True,exist_ok=True)
    if path.exists():
        raise SystemExit('Evidence already exists. Review it before starting another measurement.')
    data=dict(machine=machine(),protocol=dict(seed=246,items=2000,baskets=a.baskets,
              supports=[int(s) for s in a.supports.split(',')],
              algorithm_time_stop_seconds=a.seconds,algorithm_memory_stop_bytes=a.memory_bytes,
              generation_timeout_seconds=180,
              silent_worker_watchdog_seconds=a.seconds+10,
              note='Separate larger-input experiment. Same generator and PlainApriori; bench.py unchanged. Algorithm wall time includes tracemalloc and progress monitor overhead; excludes prebuilt input and generation. Peak bytes are additional Python allocation, not total RAM. Stop is an operational waiting/allocation budget, not OOM or a physical maximum.'),
              runs=[],status='running')
    def save():
        tmp=path.with_suffix('.tmp'); tmp.write_text(json.dumps(data,indent=2),encoding='utf-8'); tmp.replace(path)
    save()
    errors=path.with_suffix('.stderr.log')
    with errors.open('w',encoding='utf-8') as err:
        proc=subprocess.Popen([sys.executable,'-u',str(Path(__file__).resolve()),'--worker',
                               '--baskets',str(a.baskets),'--supports',a.supports],
                              stdout=subprocess.PIPE,stderr=err,text=True,encoding='utf-8')
        # Independent watchdog also covers an unexpectedly silent or stalled worker.
        stop=threading.Event(); state={'phase':'generation','start':time.monotonic()}
        def watchdog():
            while not stop.wait(.25):
                budget=180 if state['phase']=='generation' else a.seconds+10
                if time.monotonic()-state['start']>budget:
                    state['watchdog']=True
                    state['watchdog_elapsed']=time.monotonic()-state['start']
                    state['watchdog_budget']=budget
                    proc.terminate(); return
        guard=threading.Thread(target=watchdog,daemon=True); guard.start()
        last=None
        try:
            for line in proc.stdout:
                event=json.loads(line); kind=event['event']
                if kind=='started':
                    state.update(phase='algorithm',start=time.monotonic())
                    last=event; print(f"Starting support={event['support']}",flush=True)
                elif kind=='progress':
                    last=event
                    if event['seconds']>=a.seconds or event['peak_bytes']>=a.memory_bytes:
                        proc.terminate(); proc.wait()
                        data['runs'].append(dict(event,status='stopped',reason=
                            'time_budget' if event['seconds']>=a.seconds else 'allocation_budget',
                            note='Last live sample at termination; partial run, no final answer count.'))
                        data['status']='boundary_observed'; save()
                        print(f"Stopped support={event['support']} at {event['seconds']:.2f}s, {event['peak_bytes']/1e6:.2f} MB.",flush=True)
                        break
                elif kind=='completed':
                    data['runs'].append(dict(event,status='completed')); save()
                    print(f"Completed support={event['support']}: {event['seconds']:.2f}s, {event['peak_bytes']/1e6:.2f} MB",flush=True)
                else:
                    print(kind,flush=True)
            if data['status']=='running':
                rc=proc.wait()
                data['status']='completed_without_boundary' if rc==0 else 'interrupted'
                if rc!=0:
                    data['last_live_sample']=last
                    data['watchdog_triggered']=state.get('watchdog',False)
                    data['watchdog_elapsed_seconds']=state.get('watchdog_elapsed')
                    data['watchdog_budget_seconds']=state.get('watchdog_budget')
                save()
        finally:
            stop.set(); guard.join()
            if proc.poll() is None:
                proc.terminate(); proc.wait()
    print('Saved evidence:',path.name,flush=True)


if __name__=='__main__':
    main()
