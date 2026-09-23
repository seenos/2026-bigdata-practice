# 2026 빅데이터 실습 및 과제

## 과제 목록

| 주차 | 과제 | 결과 |
|---|---|---|
| 03 | [Finding Similar Items — Task 1·2·3](w03-lsh/) | 구현, 성능 측정, LSH 검색 실험 완료 |

## 3주차 제출 자료

- [통합 관찰](w03-lsh/out/observation.md)
- [Task 2 측정 보고서](w03-lsh/out/curve.md)
- [Task 3 수식과 밴드 실험](w03-lsh/out/task3-analysis.md)
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
    ├── task1-observation-detail.md
    └── out/
        ├── crossover.json
        ├── curve.md
        ├── bench.txt
        ├── observation.md
        ├── task3-analysis.md
        ├── band_experiment.json
        └── machine.json
```

3주차 전체 제출본은 `w03-lsh/`이며, 측정 결과와 통합 관찰은 `w03-lsh/out/`에 있습니다. 상세 설명과 실험 원시 자료도 함께 보관합니다.

[수업 원본](https://github.com/codingchild2424/2026-lecture-bigdata-practice/tree/main/w03-lsh)
