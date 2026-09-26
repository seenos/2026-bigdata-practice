# 2026 빅데이터 실습 및 과제

## 과제 목록

| 주차 | 과제 | 결과 |
|---|---|---|
| 03 | [Finding Similar Items — Task 1·2·3](w03-lsh/) | 구현, 성능 측정, LSH 검색 실험 완료 |
| 04 | [Mining Data Streams — Task 1·2·3](w04-stream/) | 스트림 알고리즘 구현, 메모리 비교, 필터 개선 완료 |

## 3주차 제출 자료

- [통합 관찰](w03-lsh/out/observation.md)
- [Task 1 observation](w03-lsh/observations/task1.md)
- [Task 2 observation](w03-lsh/observations/task2.md)
- [Task 3 observation](w03-lsh/observations/task3.md)
- [Task 2 측정 보고서](w03-lsh/out/curve.md)
- [공식 벤치마크 결과](w03-lsh/out/bench.txt): 재현율 98.35%, 비교 132회, strong

Python 3에서 실행합니다. 별도 패키지는 필요하지 않습니다.

```bash
cd w03-lsh
python task1_minhash.py --verify
python bench.py --yours
python test_tasks.py
python ../check.py w03
```

성능 측정 재실행: `python task2_crossover.py --sizes 250,500,750,1000,2000,4000` (결과 누적).

## 파일 구조

4주차 파일 구조와 실행 방법은 [4주차 안내](w04-stream/README.md)에 있습니다. 아래는 기존 3주차 구조입니다.

```text
2026-bigdata-practice/
├── README.md
├── check.py
└── w03-lsh/
    ├── task1_minhash.py
    ├── task2_crossover.py
    ├── task3_scale.py
    ├── bench.py
    ├── test_tasks.py
    ├── observations/
    │   ├── task1.md
    │   ├── task2.md
    │   └── task3.md
    └── out/
        ├── observation.md
        ├── crossover.json
        ├── curve.md
        ├── bench.txt
        └── evidence/
            ├── band_experiment.json
            └── machine.json
```

3주차 전체 제출본은 `w03-lsh/`이며, 측정 결과와 통합 관찰은 `w03-lsh/out/`에 있습니다. 과제별 상세 설명은 `observations/`, 보충 실험 자료는 `out/evidence/`에 보관합니다.

[수업 원본](https://github.com/codingchild2424/2026-lecture-bigdata-practice/tree/main/w03-lsh)

## 4주차 제출 자료

- [제출용 통합 관찰](w04-stream/out/observation.md)
- [Task 1 observation](w04-stream/observations/task1.md)
- [Task 2 observation](w04-stream/observations/task2.md)
- [Task 3 observation](w04-stream/observations/task3.md)
- [메모리 측정 보고서](w04-stream/out/limits.md) · [원시 측정값](w04-stream/out/limits.json)
- [공식 벤치마크 결과](w04-stream/out/bench.txt): 오탐률 0.856%, 미탐 0개, strong

Python 3.11.9에서 검증했으며 별도 패키지는 필요하지 않습니다. 저장소 루트에서 다음과 같이 실행합니다.

```bash
cd w04-stream
python test_tasks.py
python ../check.py w04
```

Task 2는 640만 개까지 두 방법을 비교했고, 1,600만 개는 set의 추가 실험으로 구분했습니다. 1,600만 개의 FM은 중단되어 완료 결과가 없습니다. 대규모 측정을 다시 실행하지 않아도 저장된 결과와 문서를 확인할 수 있습니다.
