# 5주차 — Link Analysis

PageRank의 dead end·spider trap 문제를 확인하고, 수렴 조건과 희소 구현의 성능을 비교했다. 필수 Task 1·2·3을 수행했으며 선택 Task 4(Spark)는 제외했다. Python 3.11.9에서 검증했고 별도 패키지는 필요하지 않다.

## 제출 자료

먼저 [제출용 통합 observation](out/observation.md)을 읽고, 근거와 해석은 Task별 상세 문서에서 확인할 수 있다.

| 과제 | 코드 | 상세 관찰과 결과 |
|---|---|---|
| Task 1 | [task1_pagerank.py](task1_pagerank.py) | [관찰](observations/task1.md) · [원시 결과](out/evidence/task1.json) |
| Task 2 | [task2_convergence.py](task2_convergence.py) | [관찰](observations/task2.md) · [측정 보고서](out/convergence.md) · [원시 결과](out/convergence.json) |
| Task 3 | [task3_sparse.py](task3_sparse.py) | [관찰](observations/task3.md) · [공식 실행 출력](out/bench.txt) |

Task 1은 공식 7개 검증을 통과했다. Task 2는 5개 beta, 2개 그래프 크기, 5개 허용 오차의 비교 조건을 각각 3회 실행했으며 본 실험 45건 모두 수렴했다. 조건을 전부 교차한 실험은 아니며 각 효과를 분리해 비교했다. 별도의 시험 실행 1건은 통계에서 제외했다.

Task 3의 저장된 벤치마크는 최대 점수 차이 5.55e-17, 약 48.4배 속도 향상, 실수 저장 개수 약 596배 감소로 strong을 받았다. 속도는 해당 실행의 관찰값이며 메모리 지표는 전체 RAM이 아닌 실수 저장 개수의 비교다.

## 검증

저장소 루트에서 다음과 같이 실행한다.

```bash
cd w05-pagerank
python test_tasks.py
python ../check.py w05
```

자동 테스트 결과는 8 passed, 0 failed, 1 skipped이다. 제외된 항목은 순간 이동 처리에 대한 사람의 평가 항목이다. 형식 검사 통과가 observation의 타당성까지 자동 보장하는 것은 아니다. 제공 bench.py와 test_tasks.py는 수정하지 않았다.

## 실험 재현

```bash
python task1_pagerank.py --verify
python task1_experiment.py
python task2_convergence.py --label beta
python task2_convergence.py --nodes 6000 --label size
python task2_convergence.py --betas 0.85 --tol 1e-3 --label tolerance
python task2_convergence.py --betas 0.85 --tol 1e-4 --label tolerance
python task2_convergence.py --betas 0.85 --tol 1e-5 --label tolerance
python task2_convergence.py --betas 0.85 --tol 1e-6 --label tolerance
python task2_convergence.py --betas 0.85 --tol 1e-7 --label tolerance
python bench.py --yours
```

Task 2는 기본적으로 조건당 3회 측정하고 JSON에 누적한다. 문서 표는 자동 갱신되지 않으므로 재실행 후 대상 실행을 선택해 다시 집계해야 한다. Task 1의 보충 실험은 evidence/task1.json을 갱신한다. 벤치마크는 화면에 출력하며 저장된 bench.txt는 기존 실행 기록이다.

## 파일 구조

```text
w05-pagerank/
├── README.md
├── task1_pagerank.py
├── task1_experiment.py
├── task2_convergence.py
├── task3_sparse.py
├── bench.py
├── test_tasks.py
├── observations/
│   ├── task1.md
│   ├── task2.md
│   └── task3.md
└── out/
    ├── observation.md
    ├── convergence.json
    ├── convergence.md
    ├── bench.txt
    └── evidence/
        └── task1.json
```

[수업 원본](https://github.com/codingchild2424/2026-lecture-bigdata-practice/tree/main/w05-pagerank)
