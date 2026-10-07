"""Build the report and SVG from completed measurements (standard library)."""
import json
import math
from pathlib import Path


def main():
    root = Path(__file__).parent
    d = json.loads((root/'out/explosion.json').read_text(encoding='utf-8'))
    latest = {r['support']:r for r in d['runs'] if r.get('status')=='completed'}
    rows = [latest[s] for s in sorted(latest, reverse=True)]
    assert len(rows)>=5
    table=[]
    for i,r in enumerate(rows):
        prev=rows[i-1] if i else None
        cg=f"{r['peak_counters']/prev['peak_counters']:.3f}" if prev else '—'
        ag=f"{r['frequent_pairs']/prev['frequent_pairs']:.3f}" if prev else '—'
        table.append(f"| {r['support']} | {r['frequent_items']:,} | {r['peak_counters']:,} | {r['frequent_pairs']:,} | {cg} | {ag} | {r['seconds']:.2f} | {r['peak_bytes']/1e6:.2f} |")
    # Log y axis allows counts spanning several orders of magnitude to coexist.
    svg=['<svg xmlns="http://www.w3.org/2000/svg" width="900" height="480" viewBox="0 0 900 480">',
         '<rect width="900" height="480" fill="white"/>',
         '<g font-family="Arial,sans-serif" fill="#172b4d">',
         '<text x="60" y="30" font-size="20">Apriori: counters versus frequent pairs</text>',
         '<text x="60" y="53" font-size="13">20,000 baskets; fixed data; logarithmic count axis</text>']
    lo,hi=2,7
    def x(i): return 90+i*740/(len(rows)-1)
    def y(v): return 395-(math.log10(max(v,1))-lo)*300/(hi-lo)
    for power in range(lo,hi+1):
        yy=y(10**power)
        svg.append(f'<path d="M90 {yy} H830" stroke="#dde3ea"/><text x="25" y="{yy+4}" font-size="12">10^{power}</text>')
    for i,r in enumerate(rows):
        svg.append(f'<text x="{x(i)}" y="420" text-anchor="middle" font-size="12">{r["support"]}</text>')
    for key,color,label,legend in [('peak_counters','#2255aa','Pair counters',90),('frequent_pairs','#bd4b12','Frequent pairs',290)]:
        points=' '.join(f'{x(i)},{y(r[key])}' for i,r in enumerate(rows))
        svg.append(f'<polyline points="{points}" fill="none" stroke="{color}" stroke-width="3"/>')
        for i,r in enumerate(rows):
            svg.append(f'<circle cx="{x(i)}" cy="{y(r[key])}" r="4" fill="{color}"><title>Support {r["support"]}: {r[key]:,}</title></circle>')
        svg.append(f'<text x="{legend}" y="78" fill="{color}" font-size="14">{label}</text>')
    svg.append('<text x="460" y="452" text-anchor="middle" font-size="14">Support threshold (tested settings, decreasing)</text></g></svg>')
    (root/'out/explosion.svg').write_text('\n'.join(svg),encoding='utf-8')
    saturated = next((r for r in rows if r['frequent_items']==d['protocol']['items']),None)
    last=rows[-1]
    reached=any(r['seconds']>=60 or r['peak_bytes']>=1e9 for r in rows)
    stop = ('설정한 시간·메모리 기준에 도달했다.' if reached else
            '최소 양의 지지도 1까지 완료했고, 설정한 시간·메모리 기준에는 도달하지 않았다.')
    plateau = f"지지도 {saturated['support']}부터 모든 {saturated['frequent_items']:,}개 항목이 첫 통과를 통과했다." if saturated else '모든 항목이 살아남는 조건은 관찰하지 못했다.'
    explanation=f'''## 증가 양상과 정답 수의 차이 (A4, A5)

지지도 400→200→100→50에서 카운터는 약 5.54·4.67·3.00배 늘었다. 지지도를 절반으로 낮추면 두 배 정도만 늘 것이라는 단순한 예상보다 빠르다. 반면 50→25에서는 증가폭이 작아졌다. {plateau} 이후 같은 입력의 실제 공출현 쌍을 모두 세기 때문에 지지도를 더 낮춰도 새 후보 카운터가 계속 늘지는 않는다. 전체 가능한 쌍 1,999,000개를 모두 미리 할당한 것도 아니다.

빈발 쌍은 이미 세고 있던 후보 중 최종 기준을 통과한 것이다. 낮은 지지도 구간에서는 후보 카운터가 포화되어도 정답 수는 계속 증가한다. 따라서 카운터가 항상 정답보다 더 빠르게 증가한다거나 정답 수가 늘 느리게 증가한다고 일반화할 수 없다. 지지도 50에서는 820,259개 카운터로 6,397개 정답을 찾아 약 128배의 차이가 있었지만, 지지도 1에서는 관찰된 모든 쌍이 답이 되어 두 수가 같아진다.

카운터가 일정해도 반환 결과 사전이 커지면 Python 메모리는 늘 수 있다. 따라서 쌍 카운터 수와 전체 추가 할당의 최고값도 서로 다른 지표다.
'''
    text=f'''# Task 2 — 지지도와 후보 계수 비용

## 예상과 조건

지지도를 낮추면 첫 통과에서 더 많은 항목이 살아남아 후보가 빠르게 늘 것으로 예상했다. 다만 고정된 유한 데이터에서는 후보 수에 상한이 있으며, 실제 정답 수와 후보 수가 같은 속도로 증가할 필요는 없다.

CPU {d['machine']['cpu']}, RAM {d['machine']['ram_bytes']/2**30:.2f} GiB, {d['machine']['platform']}, Python {d['machine']['python']}에서 실행했다. Codex가 실행 중이고 다른 사용자 앱은 통제하지 않았다. 고정 시드 246의 동일한 20,000개 장바구니·2,000개 상품 데이터를 사용했다. 제공 PlainApriori와 bench.py는 변경하지 않았다.

지지도당 한 번씩 측정했다. 알고리즘 호출에 tracemalloc 계측 비용이 포함된다. 입력 생성·사전 환경 조사·파일 저장은 시간에서 제외되며, 메모리는 이미 생성한 입력을 제외한 Python 추가 할당 최고값으로 전체 프로세스 RAM이 아니다. 결과 사전 생성 비용은 포함된다. 이전 결과는 다음 조건 전에 해제했다. 400은 첫 실행, 나머지는 후속 실행 묶음이다. 각 행에 환경 기록을 보존했다.

## 측정 표 (A1, A3)

| 지지도 | 빈발 항목 | 최대 쌍 카운터 | 빈발 쌍 | 직전 대비 카운터 배율 | 직전 대비 정답 배율 | 시간(s) | 메모리(MB) |
|---:|---:|---:|---:|---:|---:|---:|---:|
{chr(10).join(table)}

MB는 1,000,000 bytes이다. {len(rows)}개 지지도, 최대·최소 {rows[0]['support']/last['support']:.0f}배 범위이다. 25→12, 3→1은 정확히 절반은 아니며 배율은 실제 이웃 측정값으로 계산했다. 시간은 단회 관찰이므로 작은 차이의 의미를 과장하지 않는다.

![카운터와 빈발 쌍 수](explosion.svg)

세로축은 로그 눈금이며 가로축은 측정 조건 순서다. 두 곡선의 원자료는 위 표와 같다.

{explanation}

## 종료 지점과 한계 (A2)

{stop} 가장 긴 실행은 {max(r['seconds'] for r in rows):.2f}초, 가장 큰 추가 할당은 {max(r['peak_bytes'] for r in rows)/1e6:.2f} MB였다. 시간 60초 또는 추가 할당 1 GB를 완료 조건별 확장 중지 기준으로 설정했으며 메모리 부족·실행 실패는 관찰되지 않았다. 이 기준은 강제 timeout이나 메모리 제한은 아니다.

이번 고정 데이터에서 컴퓨터가 감당하지 못하는 지지도를 발견했다고 주장하지 않는다. 과제 A2가 기대하는 실제 부담 지점은 관찰하지 못했으며, 지원 범위의 최솟값에 도달한 결과로 기록한다. 입력 크기를 바꾸면 다른 결과가 나올 수 있지만 이번 실험에서 측정한 것은 아니다.

## 재현

```bash
python task2_explosion.py --supports 400,200,100,50,25,12,6,3,1
python task2_report.py
python test_tasks.py --task 2
```

측정값은 [explosion.json](explosion.json)에 조건 완료마다 저장·누적된다. 보고서 생성기는 같은 지지도의 마지막 완료 행을 선택한다.
'''
    (root/'out/explosion.md').write_text(text,encoding='utf-8')
    obs=f'''# Task 2 — Observation

고정된 20,000개 장바구니에서 지지도 400부터 1까지 {len(rows)}개 조건을 측정했다. 낮은 지지도는 후보를 크게 늘릴 것으로 예상했으나, 후보 증가율은 구간마다 달랐다.

{explanation}

## 실제 종료 사유

{stop} 최고 시간은 {max(r['seconds'] for r in rows):.2f}초, 최고 추가 Python 할당은 {max(r['peak_bytes'] for r in rows)/1e6:.2f} MB였으며 시간·메모리 고갈은 관찰되지 않았다. 따라서 “지지도 몇에서 컴퓨터 한계에 도달했다”는 결론은 내릴 수 없다. 최소 기준까지 실행한 사실과 과제 A2의 부담 지점을 찾지 못한 한계를 함께 기록한다.

Core i5-11400H, RAM 약 15.74 GiB, Python 3.11.9에서 Codex가 실행 중이었으며 다른 앱은 통제하지 않았다. 계측 오버헤드를 포함한 단회 결과로, 일반적인 실행 시간이나 실제 프로세스 RAM과 구분한다.

[전체 표와 그래프](../out/explosion.md) · [원시 측정값](../out/explosion.json)
'''
    (root/'observations/task2.md').write_text(obs,encoding='utf-8')
    p=root/'out/observation.md'; s=p.read_text(encoding='utf-8')
    task3 = s[s.index('## Task 3'):] if '## Task 3' in s else None
    s=s[:s.index('## Task 2')] + f'''## Task 2

지지도 400→200→100→50에서 카운터는 약 5.54·4.67·3.00배 증가했지만, 모든 항목이 살아남은 뒤에는 후보 수가 포화됐다. 반면 낮은 지지도에서 정답 수는 계속 늘었고 지지도 1에서는 모든 계수 대상이 정답이 됐다.
{stop} 따라서 A2의 실제 부담 지점은 발견하지 못했으며, 시간·메모리 고갈을 주장하지 않는다.
카운터 수·최종 정답 수·반환 결과를 포함한 Python 메모리는 서로 다른 지표다. [상세 관찰](../observations/task2.md) · [측정 표·그래프](explosion.md)

## Task 3

아직 구현·측정하지 않았다. 이 문서는 최종 제출본이 아니다.
'''
    if task3 is not None:
        s = s[:s.index('## Task 3')] + task3
    p.write_text(s,encoding='utf-8')
    print('Reports and SVG written from',len(rows),'completed conditions.')


if __name__=='__main__':
    main()
