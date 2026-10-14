# 6주차 — Frequent Itemsets

Apriori와 연관 규칙을 구현하고 지지도별 후보 증가 및 PCY의 메모리 절감 효과를 측정했다. Python 3.11.9와 표준 라이브러리만 사용했다. 선택 Task 4(SON)는 수행하지 않았다.

## 제출 자료

- [제출용 통합 observation](out/observation.md)
- [Task 1 상세 관찰](observations/task1.md): 방향별 신뢰도, 향상도, 후보와 실제 카운터
- [Task 2 상세 관찰](observations/task2.md) · [측정 표·그래프](out/explosion.md) · [원시 결과](out/explosion.json)
- [Task 3 상세 관찰](observations/task3.md) · [공식 출력](out/bench.txt) · [실제 메모리 비교](out/evidence/pcy_memory.json)

Task 2는 기본 20,000개 입력에서 지지도 400부터 1까지 9개 조건을 완료했다. 추가로 입력을 100,000개와 200,000개로 확장했고, 200,000개·지지도 250에서 약 60.69초·관측 추가 Python 할당 204.88 MB로 시간 기준에 도달해 중단했다. 이는 사전에 정한 대기 예산이며 메모리 고갈이나 물리적 최대 입력 크기는 아니다. [A2 보충 측정](out/a2_boundary.md)에 완료·중단 데이터를 구분했다. Task 3는 같은 빈발 쌍을 찾고 쌍 카운터 97.6% 감소로 strong을 받았다. 카운터 개수와 실제 추가 Python 메모리, 실행 시간은 구분한다.

## 빠른 검증

저장소 루트에서 실행한다. 아래 명령은 장시간 메모리 실험을 다시 수행하지 않는다.

```bash
cd w06-apriori
python test_tasks.py
python ../check.py w06
```

전체 자동 검사는 7 passed, 0 failed, 1 skipped이다. 제외 항목은 PCY 메모리 설명의 사람 평가다. 형식 검사와 자동 테스트가 모든 서술형 요구사항의 충족을 보장하지는 않는다. 제공 bench.py, test_tasks.py와 PlainApriori는 유지했다.

## 실험 재현

```bash
python task1_apriori.py --verify
python task1_experiment.py
python task2_explosion.py --supports 400,200,100,50,25,12,6,3,1
python task2_report.py
python bench.py --yours
python task3_experiment.py
```

Task 2는 결과를 누적하고 완료 조건마다 저장한다. task2_report.py는 같은 지지도의 마지막 완료 행을 골라 표·SVG·Task 2 관찰을 생성한다. Task 1·3 보충 실험은 해당 JSON을 다시 작성한다. 재실행하면 기존 문서의 수치와 달라질 수 있으므로 상세 관찰·요약도 확인해야 한다. 벤치마크는 화면에 출력하며 bench.txt는 저장한 실행 기록이다.

## 파일 구성

- task1_apriori.py, task2_explosion.py, task3_pcy.py: 구현과 측정
- bench.py, test_tasks.py: 제공 평가 코드
- task1_experiment.py, task3_experiment.py: 보충 검증·측정 재현
- task2_report.py: 표와 그래프 생성
- task2_boundary.py, task2_boundary_report.py: 별도 입력 크기의 A2 중단 측정과 보고서 통합
- observations/: Task별 상세 관찰
- out/: 제출용 요약, 측정 JSON·보고서·그래프, 벤치마크 기록
- out/evidence/: Task 1 규칙·후보 수, PCY 메모리 비교, A2 확장·중단 원시 자료

[수업 원본](https://github.com/codingchild2424/2026-lecture-bigdata-practice/tree/main/w06-apriori)
