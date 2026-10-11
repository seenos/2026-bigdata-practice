"""Build Task 2 tables from the latest completed experiment batch."""
import json
import math
from pathlib import Path
from statistics import median

ROOT=Path(__file__).parent


def main():
    data=json.loads((ROOT/'out/curse.json').read_text(encoding='utf-8'))
    batch=data['runs'][-1]['batch']; rows=[r for r in data['runs'] if r['batch']==batch]
    dims=sorted({r['dim'] for r in rows if r['label']=='dimension'})
    assert len(dims)>=6 and max(dims)>=200
    assert all(len([r for r in rows if r['dim']==d and r['label']=='dimension'])==3 for d in dims)
    assert all(r['pairs']<=r['pair_attempts'] and r['min']>0 and r['min']<=r['mean']<=r['max'] for r in rows)
    assert all(math.isclose(r['contrast'],(r['max']-r['min'])/r['min']) and
               math.isclose(r['relative_stdev'],r['stdev']/r['mean']) for r in rows)
    exact=json.loads((ROOT/'out/evidence/all_pairs.json').read_text(encoding='utf-8'))
    assert exact['batch']==batch
    def med(rs,key): return median(r[key] for r in rs)
    lines=[]
    for d in dims:
        rs=[r for r in rows if r['dim']==d and r['label']=='dimension']
        lines.append(f"| {d} | {med(rs,'min'):.4f} | {med(rs,'max'):.4f} | {med(rs,'mean'):.4f} | {med(rs,'contrast'):.4f} ({min(r['contrast'] for r in rs):.4f}–{max(r['contrast'] for r in rs):.4f}) | {med(rs,'relative_stdev'):.4f} | {med(rs,'mean')/math.sqrt(d):.4f} | {med(rs,'seconds'):.3f} |")
    nlines=[]
    for n in sorted({r['points'] for r in rows if r['dim']==50}):
        rs=[r for r in rows if r['dim']==50 and r['points']==n]
        nlines.append(f"| {n} | {med(rs,'contrast'):.4f} | {min(r['contrast'] for r in rs):.4f}–{max(r['contrast'] for r in rs):.4f} | {med(rs,'relative_stdev'):.4f} |")
    elines=[]
    for n in sorted({r['points'] for r in exact['runs']}):
        rs=[r for r in exact['runs'] if r['points']==n]
        elines.append(f"| {n} | {rs[0]['pairs']:,} | {med(rs,'contrast'):.4f} | {min(r['contrast'] for r in rs):.4f}–{max(r['contrast'] for r in rs):.4f} |")
    for seed in {r['seed'] for r in exact['runs']}:
        vals=[r['contrast'] for r in sorted([r for r in exact['runs'] if r['seed']==seed],key=lambda r:r['points'])]
        assert vals==sorted(vals)
    # Brackets refer only to the tested dimension grid, not precise crossing values.
    thresholds=[]
    for limit in (1,.5):
        for seed in sorted({r['seed'] for r in rows}):
            rs=sorted([r for r in rows if r['label']=='dimension' and r['seed']==seed],key=lambda r:r['dim'])
            pos=next((i for i,r in enumerate(rs) if r['contrast']<limit),None)
            thresholds.append(f"- seed {seed}, contrast < {limit}: "+(f"{rs[pos-1]['dim']}–{rs[pos]['dim']}차원 사이의 측정 구간 (처음 관측 {rs[pos]['dim']}차원)." if pos and pos>0 else '확인 필요.'))
    env=data['machine']; largest=max(rows,key=lambda r:r['dim']); slowest=max(rows,key=lambda r:r['seconds'])
    text=f'''# Task 2 — 차원이 커질수록 거리의 대비가 줄어드는가?

## 환경과 측정 방법 (A1, A7)

- CPU: {env.get('cpu',env['processor'])}, RAM {env.get('ram_bytes',0):,} bytes.
- {env['platform']}, Python {env['python']}. Codex 실행 중이며 다른 앱 부하는 통제하지 않았다.
- 본 실험은 1,000개 점, 차원 2·5·10·20·50·100·200·500·1,000, 조건당 seed 246·247·248의 3회 독립 생성이다. 동일 데이터의 시간만 반복 측정한 것이 아니다.
- 점은 단위 정육면체 [0,1]^d의 균등 난수다. 제공 코드와 동일하게 시드에 차원을 더하고 점 생성 이후 20,000회 점 쌍을 뽑는다. 자기 자신과의 쌍은 제외하며 중복 쌍은 허용하므로 실제 거리 개수는 20,000보다 조금 작다.
- 시간은 점 생성과 거리 표본 생성을 포함하며 JSON 저장 및 통계 계산은 제외한다. CPU 사용량·전체 RAM을 측정한 실험은 아니다.
- 표는 열별 중앙값이다. min·max·mean의 중앙값에서 contrast를 다시 계산한 값이 아니라 실행별 contrast의 중앙값을 보고한다.

## 차원별 표 (A2, A4, A5)

| 차원 d | 최소 거리 | 최대 거리 | 평균 거리 | contrast 중앙값 (범위) | 상대 표준편차 | 평균/√d | 시간 중앙값(s) |
|---:|---:|---:|---:|---:|---:|---:|---:|
{chr(10).join(lines)}

contrast=(max−min)/min, 상대 표준편차=표준편차/평균이다. 분산은 표본 거리 목록 자체의 기술 통계로 분모를 거리 개수로 사용했다.

## 기준을 통과한 차원 (A3)

{chr(10).join(thresholds)}

이는 선택한 차원 격자와 난수 표본에서 처음 관측한 구간이다. 정확한 경계 차원이나 다른 데이터의 보장이 아니며 반복 간 범위도 함께 확인해야 한다. contrast의 극값은 표본 수와 우연히 선택한 쌍에 민감하다.

## 평균 거리는 왜 √d 수준인가? (A4, A5)

독립 균등 난수 X,Y에 대해 E[(X−Y)²]=1/6이므로 d차원의 제곱거리 기댓값은 d/6이다. 제곱거리의 제곱근 평균과 평균의 제곱근은 일반적으로 같지 않지만, 높은 차원에서 거리가 집중되면 평균 거리가 √(d/6)에 가까워진다. 따라서 평균/√d가 약 1/√6=0.4082로 접근하는지 표에서 확인한다. 거리가 차원에 선형 비례한다는 해석은 맞지 않는다.

평균 거리는 커지면서 상대 표준편차는 작아졌다. 상대 표준편차는 전체 표본 거리의 상대적인 산포를, contrast는 가장 극단적인 두 거리의 간격을 반영한다. 표본의 거리 집중을 요약할 때는 극값 하나에 덜 좌우되는 상대 표준편차를 우선 사용하겠다. 그러나 어떤 점의 최근접 이웃이 의미 있는지를 이 두 전역 통계만으로 판정할 수는 없다. 1이나 0.5도 의미 상실의 보편적인 임계값은 아니다.

## 점 개수의 영향 (A6)

50차원에서 점 개수만 바꾸고 거리 선택 시도는 20,000회로 고정했다. 각 조건은 3개 시드다. 점 생성 뒤 같은 난수 생성기로 쌍을 뽑으므로 점 개수를 바꾸면 선택한 쌍도 달라진다.

| 점 개수 | 표본 contrast 중앙값 | 3회 범위 | 상대 표준편차 중앙값 |
|---:|---:|---:|---:|
{chr(10).join(nlines)}

고정 개수의 무작위 쌍을 보는 방식에서는 n이 커져도 모든 극값을 관측하지 못하며, contrast가 반드시 단조 증가할 이유는 없다. 점 개수와 쌍 표본 수의 효과를 구분하기 위해 같은 1,000개 점의 앞 100·300·1,000개를 대상으로 모든 서로 다른 쌍을 계산했다. 이 보충 실험은 주 실험과 방법이 달라 별도 원자료에 저장했다.

| 점 개수 | 모든 쌍 개수 | 전체 쌍 contrast 중앙값 | 3회 범위 |
|---:|---:|---:|---:|
{chr(10).join(elines)}

각 시드에서 점 집합을 확장할수록 전체 쌍 contrast가 줄지 않는 것을 확인했다. 기존 쌍이 포함되어 최솟값은 커질 수 없고 최댓값은 작아질 수 없기 때문이다. 이 결과는 전역 모든 쌍의 극값에 관한 것이며 특정 기준점의 최근접·최원거리나 모든 분포의 증가 폭에 대한 보장은 아니다.

## 3주차 LSH와의 연결 (A8)

이번 실험은 균등한 실수 벡터의 유클리드 거리다. 3주차는 문서 shingle 집합의 Jaccard 유사도와 MinHash·LSH이므로 이 측정만으로 LSH가 무효라고 결론 낼 수 없다. 단어 집합의 구조와 유사도 분포가 다르다. 실제 데이터에서 유사 문서와 무관한 문서의 Jaccard 값 차이가 작아지면 후보 구분이 어려워질 수 있지만, 문서 길이나 표현 차원이 크다는 사실만으로 판단할 수 없다. 3주차처럼 임계값별 재현율·후보 수를 실제 자료로 측정해야 한다.

## 실행 시간과 재현

가장 높은 차원은 {largest['dim']}이며 해당 3회 시간은 {', '.join(f"{r['seconds']:.3f}" for r in rows if r['label']=='dimension' and r['dim']==largest['dim'])}초다. 주 실험 전체 중 가장 긴 단일 실행은 {slowest['seconds']:.3f}초(d={slowest['dim']}, n={slowest['points']}, seed={slowest['seed']})다. 실행 시간은 이번 환경의 관찰값이다. 전체 쌍 보충 실험의 시간은 점 생성 제외 누적 시간으로 기록했으므로 직접 비교하지 않는다.

```bash
python task2_curse.py --all-pairs
python task2_report.py
python test_tasks.py --task 2
```

[주 실험 원자료](curse.json) · [전체 쌍 보충 실험](evidence/all_pairs.json). 재실행은 JSON에 누적되며 보고서 생성기는 마지막 batch만 사용한다. 3회 반복을 모두 완료해야 보고서를 생성할 수 있다.
'''
    (ROOT/'out/curse.md').write_text(text,encoding='utf-8')
    print('Validated',len(rows),'sampled runs and',len(exact['runs']),'all-pairs rows.')
    print('Report saved to out/curse.md')


if __name__=='__main__':
    main()
