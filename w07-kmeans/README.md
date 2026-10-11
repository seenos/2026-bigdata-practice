# 7주차 — Clustering

Task 1 k-means 초기화 비교, Task 2 차원별 거리 측정, Task 3 거리 경계를 이용한 계산 생략을 수행했다. Python 표준 라이브러리만 사용한다.

- [Task 1 코드](task1_kmeans.py)
- [Task 1 상세 관찰](observations/task1.md)
- [시드별 실험 결과](out/evidence/task1.json)
- [Task 2 코드](task2_curse.py) · [보고서 생성기](task2_report.py)
- [Task 2 상세 관찰](observations/task2.md)
- [차원별 측정 표](out/curse.md) · [측정 JSON](out/curse.json)
- [모든 점 쌍 보충 실험](out/evidence/all_pairs.json)
- [Task 3 코드](task3_fewer.py) · [검증·계측](task3_experiment.py)
- [Task 3 상세 관찰](observations/task3.md) · [거리 호출 원자료](out/evidence/task3.json)
- [공식 벤치마크 결과](out/bench.txt)
- [제출용 통합 관찰](out/observation.md)

Python 표준 라이브러리만 사용한다. 제공 bench.py와 test_tasks.py는 수정하지 않았다.

```bash
python test_tasks.py --task 1
python task1_experiment.py
python test_tasks.py --task 2
python test_tasks.py
python ../check.py w07
```

공식 Task 1의 7개 검증을 통과했고, 40개 시드씩 두 초기화를 비교했다. random은 27회, k-means++는 40회 원래 세 군집을 복원했다.

Task 2는 9개 차원과 50차원의 4개 점 개수를 조건별 3회 비교해 총 36회 실행했다. 보충 실험은 3개 시드의 중첩 점 집합에 대한 모든 쌍을 계산해 9개 행을 기록했다. 공식 Task 2 검사 5개를 통과했다.

Task 3는 거리 호출 10,320,000회에서 1,150,986회로 88.85% 줄여 strong 조건을 충족했다. 최종 SSE 차이는 0이고 배정·중심·43회 반복도 기준과 같았다. 추가로 작은 사례 113개에서 정확한 일치를 확인했다. 두 계측 실행이 일부 겹쳐 저장된 시간은 속도 향상 근거로 사용하지 않는다.

점별 상한·하한은 추가 수 2n개를 요구하며, 경계 유지를 위한 중심 이동·중심 간 거리도 공식 호출 수에 포함했다. 제공 bench.py와 test_tasks.py는 원본 그대로다.

전체 공식 테스트는 8 passed, 0 failed, 1 skipped이며 제출 파일 검사도 통과했다. 건너뛴 항목은 경계 원리를 observation에서 설명했는지 사람이 평가하는 항목이다. 자동 검사 통과가 관찰 내용의 채점을 보장하는 것은 아니다.

측정을 재실행하려면 아래를 사용한다. JSON은 누적되며 보고서는 마지막 완료 묶음에서 생성한다. 조건별 3회 반복과 전체 쌍 보충 실험이 필요하다.

```bash
python task2_curse.py --all-pairs
python task2_report.py
```

Task 3 재현 및 문서 갱신은 다음 순서다. 측정은 순차 실행하고 공식 출력은 필요한 경우 out/bench.txt에 저장한다.

```bash
python bench.py --yours
python task3_experiment.py
python task3_report.py
```

[수업 원본](https://github.com/codingchild2424/2026-lecture-bigdata-practice/tree/main/w07-kmeans)
