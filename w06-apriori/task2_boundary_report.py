"""Integrate the separate A2 experiment without mixing datasets in the main curve."""
import json
from pathlib import Path


def extend_reports(root):
    path=root/'out/evidence/a2_boundary.json'
    if not path.exists():
        return
    data=json.loads(path.read_text(encoding='utf-8'))
    if data['status']!='boundary_observed':
        print('A2 evidence has not reached a recorded boundary; base report preserved.')
        return
    protocol=data['protocol']; stopped=data['runs'][-1]
    assert stopped['status']=='stopped'
    preceding=root/'out/evidence/a2_boundary_200000_interrupted.json'
    previous_rows=[]
    if preceding.exists():
        earlier=json.loads(preceding.read_text(encoding='utf-8'))
        assert earlier['protocol']['baskets']==protocol['baskets']
        previous_rows=[r for r in earlier['runs'] if r['status']=='completed']
    combined=previous_rows+data['runs']
    completed=[r for r in combined if r['status']=='completed']
    table=[]
    for r in combined:
        done=r['status']=='completed'
        counters=r['peak_counters'] if done else r['observed_pair_counters']
        answers=f"{r['frequent_pairs']:,}" if done else '미완료'
        table.append(f"| {r['support']} | {'완료' if done else '기준 도달로 중단'} | {r['seconds']:.2f} | {r['peak_bytes']/1e6:.2f} | {counters:,} | {answers} |")
    reason='시간' if stopped['reason']=='time_budget' else '추가 할당'
    summary=f"장바구니 {protocol['baskets']:,}개 보충 실험에서 지지도 {stopped['support']} 실행을 {stopped['seconds']:.2f}초·관측 최고 추가 할당 {stopped['peak_bytes']/1e6:.2f} MB에서 {reason} 기준으로 중단했다."
    archive=root/'out/evidence/a2_boundary_100000.json'
    previous=''
    if archive.exists():
        pilot=json.loads(archive.read_text(encoding='utf-8'))
        assert pilot['status']=='completed_without_boundary'
        previous=f"앞서 100,000개 입력에서는 지지도 2,000부터 1까지 완료했고 최대 {max(r['seconds'] for r in pilot['runs']):.2f}초·{max(r['peak_bytes'] for r in pilot['runs'])/1e6:.2f} MB로 기준에 미달했다. [이 확장 단계의 원자료](evidence/a2_boundary_100000.json)도 보존한다.\n\n"
    section=f'''## A2 보충 실험 — 입력을 늘린 뒤 지지도 낮추기

기본 20,000개 입력은 지지도 1에서도 부담 기준에 도달하지 않았다. 양의 등장 횟수 기준을 더 낮출 수 없어 같은 생성기의 장바구니 수를 {protocol['baskets']:,}개로 늘렸다. 상품 2,000개, 평균 길이 20, seed=246과 PlainApriori 알고리즘은 유지했다. bench.py 파일은 바꾸지 않고 별도 프로세스에서 BASKETS 값만 설정했다.

기본 실험의 곡선과 다른 데이터이므로 결과를 explosion.json의 같은 표에 섞지 않았다. 큰 입력 하나를 고정하고 지지도를 순서대로 낮췄다. 앞선 20만 개 실행의 지지도 4,000·2,000·1,000·500은 완료했으나 250 실행이 감시 타임아웃으로 중단되어 마지막 알고리즘 표본은 약 52초였다. 이 값만으로 60초에 도달했다고 주장하지 않고, 250부터 별도로 이어서 확인했다. [앞선 실행 원자료](evidence/a2_boundary_200000_interrupted.json)는 보존한다.

{previous}

사전에 정한 종료 기준은 알고리즘 대기 {protocol['algorithm_time_stop_seconds']:.0f}초 또는 추가 Python 할당 {protocol['algorithm_memory_stop_bytes']/1e9:.1f} GB다. 별도 감시 프로세스가 약 1초 간격의 측정값을 받아 해당 실행을 중단했다. 시간은 tracemalloc과 진행 감시의 오버헤드를 포함하고 입력 생성은 제외한다. 메모리는 미리 생성한 입력을 제외한 추가 Python 할당으로 전체 프로세스 RAM이 아니다.

| 지지도 | 상태 | 알고리즘 시간(s) | 관측 최고 추가 할당(MB) | 쌍 카운터(중단 행은 부분값) | 최종 빈발 쌍 |
|---:|---|---:|---:|---:|---:|
{chr(10).join(table)}

{summary} 중단된 행은 마지막 실시간 표본이므로 최종 실행 시간·최종 카운터 최고값·정답 수가 아니다. 정답 수나 중단 이후 결과를 추정해 채우지 않았다.

중단 행의 카운터가 직전 완료 행보다 작은 것은 아직 입력 전체를 처리하지 않았기 때문이다. 이 두 수로 지지도 하락에 따른 최종 카운터 증가율을 계산하지 않는다. 표의 완료 행과 중단 행은 서로 다른 실행 묶음이며 시간 차이를 지지도만의 효과로 단정하지 않는다.

직전 완료 지지도는 {completed[-1]['support'] if completed else '없음'}이다. 이는 측정한 단계에서 처음 종료 예산을 넘긴 지점이며 그 사이의 정확한 교차점, 사용자의 주관적인 불편함, 메모리 부족, 기계의 물리적 최대 크기를 의미하지 않는다. 이번에 먼저 도달한 것은 {reason} 예산이며 A2에 이 실측 중단 근거를 제시한다. 입력을 늘린 보충 조건이라는 점은 명확히 구분하며 원래 20,000개 데이터에서도 같은 문제가 발생했다고 주장하지 않는다.

환경은 원자료의 machine에 기록했다. 순차 측정했으며 다른 사용자 앱은 통제하지 않았다. 과제에서 데이터 크기 변경을 명시적으로 금지하지는 않지만, 기본 입력 고정을 요구하는 채점 해석이라면 보충 실험의 인정 여부는 교수님의 판단이다.

[보충 실험 원자료](evidence/a2_boundary.json)

```bash
python task2_boundary.py --baskets {protocol['baskets']} --supports {','.join(str(s) for s in protocol['supports'])}
python task2_report.py
```

앞선 완료 행은 20만 개 입력에서 `--supports 4000,2000,1000,500,250`로 시작한 별도 실행 기록이다. 위 명령은 중단 후 250부터 확인한 실행의 재현 설정이며 표의 모든 행을 한 번에 새로 측정하는 명령은 아니다.

보충 측정기는 기존 원자료가 있으면 재실행을 거부하므로 먼저 기록을 검토해야 한다. 보고서 갱신은 측정을 다시 실행하지 않는다.
'''
    (root/'out/a2_boundary.md').write_text('# Task 2 — A2 추가 한계 탐색\n\n'+section,encoding='utf-8')
    for file,link in [(root/'out/explosion.md','a2_boundary.md'),(root/'observations/task2.md','../out/a2_boundary.md')]:
        text=file.read_text(encoding='utf-8')
        marker='\n## A2 보충 실험 결과\n'
        text=text.split(marker)[0]
        text=text.replace('입력 크기를 바꾸면 다른 결과가 나올 수 있지만 이 기본 실험에서 측정한 것은 아니다.',
                          '위 내용은 기본 입력의 결과이며, 입력을 늘린 보충 실험은 아래에 따로 기록한다.')
        text+=marker+'\n'+summary+' 기본 입력에서는 지지도 1까지 한계를 발견하지 못한 결과도 보존한다.\n\n'+f'[조건·중단 근거·측정 표]({link})\n'
        file.write_text(text,encoding='utf-8')
    p=root/'out/observation.md'; text=p.read_text(encoding='utf-8')
    start=text.index('## Task 2'); end=text.index('## Task 3',start)
    part=text[start:end]
    old='최소 양의 지지도 1까지 완료했고, 설정한 시간·메모리 기준에는 도달하지 않았다. 따라서 A2의 실제 부담 지점은 발견하지 못했으며, 시간·메모리 고갈을 주장하지 않는다.'
    part=part.replace(old,f"기본 20,000개 입력은 지지도 1에서도 기준에 미달했다. {summary} 이는 시간·메모리 고갈이 아닌 사전에 정한 대기·할당 예산의 중단이며 원래 데이터와 구분한다.")
    if 'a2_boundary.md' not in part:
        part=part.rstrip()+' · [A2 보충 근거](a2_boundary.md)\n\n'
    p.write_text(text[:start]+part+text[end:],encoding='utf-8')
    print('A2 evidence integrated; separate input sizes preserved.')


if __name__=='__main__':
    extend_reports(Path(__file__).parent)
