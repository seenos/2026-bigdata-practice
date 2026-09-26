# 4주차 — Mining Data Streams

제한된 메모리에서 스트림을 처리하는 알고리즘을 구현하고 정확도·메모리·시간을 비교했다. Python 3.11.9와 표준 라이브러리만 사용했다.

## 제출 자료

| 과제 | 구현 | 관찰 및 결과 |
|---|---|---|
| Task 1 | [task1_sketches.py](task1_sketches.py) | [상세 관찰](observations/task1.md) |
| Task 2 | [task2_limits.py](task2_limits.py) | [상세 관찰](observations/task2.md) · [측정 표](out/limits.md) · [원시 결과](out/limits.json) |
| Task 3 | [task3_budget.py](task3_budget.py) | [상세 관찰](observations/task3.md) · [실행 출력](out/bench.txt) |

공식 제출용 요약은 [out/observation.md](out/observation.md)에 있다. Task 3는 오탐률 0.856%, 미탐 0개로 strong 조건을 충족했다.

## 검증

저장소 루트에서 실행한다. 아래 검증은 장시간의 Task 2 측정을 다시 실행하지 않는다.

```bash
cd w04-stream
python test_tasks.py
python ../check.py w04
```

전체 자동 테스트는 8개 통과, 실패 0개, 사람의 평가 항목 1개 제외이다. 형식 검사는 파일 존재 여부 등을 확인하며 내용의 타당성을 대신 보장하지 않는다. 제공 bench.py와 test_tasks.py는 수정하지 않았다.

개별 구현과 보충 실험은 다음 명령으로 확인한다.

```bash
python task1_sketches.py --verify
python fm_experiment.py
python bench.py --yours
```

fm_experiment.py는 [FM 결합 방식 비교 결과](out/evidence/fm_comparison.json)를 다시 작성한다.

## Task 2 측정 범위와 재현

두 방법의 비교는 10,000·40,000·160,000·640,000·6,400,000개에서 완료했다. 다섯 크기에 걸친 640배 범위이다. 1,600만 개의 set 측정은 시간 부담을 확인하는 추가 실험으로 남겼다. 같은 크기의 FM은 실행 중단으로 완료 결과가 없어 비교 표에 포함하지 않았다.

아래 명령은 기존 결과를 재현하려는 경우에만 실행한다. 결과는 limits.json에 누적되며 문서 표는 자동 갱신되지 않는다. 640만 개 FM의 기록된 실행 시간은 약 95분으로, 큰 입력의 재실행에는 상당한 시간이 필요하다.

```bash
python task2_limits.py --sizes 10000,40000,160000,640000
python task2_limits.py --sizes 6400000
python task2_limits.py --exact-only --sizes 6400000,16000000
```

## 파일 구조

```text
w04-stream/
├── README.md
├── task1_sketches.py
├── task2_limits.py
├── task3_budget.py
├── fm_experiment.py
├── bench.py
├── test_tasks.py
├── observations/
│   ├── task1.md
│   ├── task2.md
│   └── task3.md
└── out/
    ├── observation.md
    ├── limits.json
    ├── limits.md
    ├── bench.txt
    └── evidence/
        └── fm_comparison.json
```

[수업 원본](https://github.com/codingchild2424/2026-lecture-bigdata-practice/tree/main/w04-stream)
