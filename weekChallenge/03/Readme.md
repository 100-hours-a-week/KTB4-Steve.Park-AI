# Week Challenge 03 - NumPy & Pandas 미니퀘스트

Python 데이터 분석의 핵심 라이브러리인 **NumPy**와 **Pandas**의 주요 개념을 실습하는 미니퀘스트 모음입니다.

---

## 프로젝트 구조

```
03/
├── numpy_quest.py    # NumPy 퀘스트 (6개 통합)
├── pandas_quest.py   # Pandas 기본 + 데이터 변환 퀘스트 (9개 통합)
├── utils/
│   └── utils.py      # 공통 출력 유틸리티
└── data/
    └── unique_data.csv  # 중복 제거 퀘스트에서 생성되는 CSV
```

---

## numpy_quest.py

| Quest | 주제 | 핵심 개념 |
|-------|------|-----------|
| Quest 1 | **Dimension (차원)** | `ndim`, `reshape`, `np.newaxis`로 배열 차원 다루기 |
| Quest 2 | **Shape (형태)** | `shape`, `reshape`으로 배열 형태 변환 |
| Quest 3 | **Data Type (데이터 타입)** | `dtype`, `float64`, `uint8`, `itemsize`로 자료형 다루기 |
| Quest 4 | **Indexing (인덱싱)** | 기본 인덱싱, 2D 배열 슬라이싱, 조건 기반 인덱싱 |
| Quest 5 | **Operations (연산)** | 배열 덧셈, 브로드캐스팅, 최대값 위치 탐색 |
| Quest 6 | **Universal Functions (유니버설 함수)** | `np.multiply`, `np.add`, `np.log10` 등 ufunc 활용 |

---

## pandas_quest.py

| Quest | 주제 | 핵심 개념 |
|-------|------|-----------|
| Pandas Quest 1 | **Series** | Series 생성(리스트/딕셔너리), 인덱스 접근, `fillna`로 NaN 처리 |
| Pandas Quest 2 | **DataFrame** | 컬럼 접근, `sort_values` 정렬, 조건 필터링, 파생 컬럼 추가 |
| Data Mutation Quest 1 | **Filtering (필터링)** | 단일 조건, 복합 조건(`\|`), `query()`를 이용한 데이터 필터링 |
| Data Mutation Quest 2 | **Grouping (그룹화)** | `groupby` + `sum`, `agg(['sum','mean'])`, `filter`로 그룹 집계 |
| Data Mutation Quest 3 | **Merge (병합)** | `inner join`, `left join`, 다중 키 merge 및 `suffixes` 처리 |
| Data Mutation Quest 4 | **Missing Data (결측값 처리)** | `isnull().sum()`, `dropna()`, `fillna(mean())`으로 결측값 처리 |
| Data Mutation Quest 5 | **Pivot (피벗)** | `pivot`, `pivot_table`, 다중 값 컬럼 피벗 테이블 생성 |
| Data Mutation Quest 6 | **Duplicates Removal (중복 제거)** | `drop_duplicates`, `duplicated`, CSV 저장 및 불러오기 |
| Data Mutation Quest 7 | **String Operations (문자열 처리)** | `str.lower`, `str.strip`, `str.contains`, `str.split`으로 문자열 조작 |

---

## 유틸리티

### `utils/utils.py`
모든 퀘스트에서 공통으로 사용하는 출력 함수입니다.

```python
def printanswer(num: int, answer: list | str):
    # 퀘스트 번호와 결과를 포맷에 맞게 출력
```

---

## 실행 방법

```bash
# 루트 디렉토리(03/)에서 실행
python numpy_quest.py
python pandas_quest.py
```

> **주의**: `utils` 모듈 경로 참조를 위해 반드시 `03/` 디렉토리에서 실행해야 합니다.

---

## 사용 라이브러리

- `numpy` — 다차원 배열 연산
- `pandas` — 데이터프레임 기반 데이터 분석


## 회고
이전 위클리 챌린지에서 db사용인가 json데이터 다루는데에 pandas를 사용했었는데 이렇게 깊게 사용한 적은 처음이다. 확실히 코테에서는
이렇게 깊기 다루지도 않고 굳이 pandas를 안써도 대부분 풀 수 있는 문제이기 때문에 깊게 보지 않았던 점이 있었다. 그리고 numpy같은 경우
아직 numpy가 얼마나 더 필요한 지는 감이 안온다. 하도 코테에서 list, dict, 등 다양한걸 어떻게 풀어내는지만 연구하다가
이걸로 리스트와 dict에 유용한 함수들을 사용해보려 하니 헷갈리는 부분도 있지만 차원에 대해서 더 확인해볼 필요가 있다.
또한 go처럼 int64, int32, 데이터 유형을 더 잘게 쪼개서 데이터 타입을 정하는 것도 신선한 충격이였다. 왜냐하면 나에게 파이썬은 그냥
동적 할당과 아무렇게나 해도 기본 데이터 유형으로 저장해주는 쉬운 언어라 생각했기 때문이다. 다시 공부하려니 머리아프다.